"""Auditable, local usage ledger; no provider calls or token estimation.

All attempts (including failed calls and child agents) must be recorded separately.
The caller is responsible for complete coverage and disjoint call scopes: do not
record both a provider call and an aggregate which already includes that call.
PASS certifies only the supplied ledger, not migration quality or source size.

Normalization contracts (all output totals already include reasoning/image tokens):
* openai_responses: input_tokens includes input_tokens_details.cached_tokens.
* anthropic_messages: input_tokens excludes cache_read_input_tokens and
  cache_creation_input_tokens (optional cache counters mean zero).
* canonical_cache_subset / canonical_cache_separate: input_tokens includes /
  excludes cache_read_tokens + cache_write_tokens (both counters required).
* multica_input_includes_cache / multica_input_excludes_cache: explicit caller
  contract for total_input_tokens relative to total_cache_read_tokens and
  total_cache_write_tokens. unreported_task_count is required; nonzero is unknown.
  These are terminal aggregates, usable only for a disjoint aggregate scope.

Missing input/output is unknown; known components still count. Optional subset
detail counters never increase totals. Unknown formats must use unreported.
Wall time starts at start(), includes waits/builds/verification, and stops only
at finish(). Clock reversals/disagreement permanently prevent PASS.
"""
from __future__ import annotations

from contextlib import contextmanager
import json
import math
import os
from pathlib import Path
import platform
import tempfile
import time
from typing import Any
from uuid import UUID


TARGET_TOKENS = 20_000_000
DEFAULT_TOKEN_LIMIT = 19_900_000
MAX_WALLTIME_SECONDS = 120 * 60
MODES = frozenset({"openai_responses", "anthropic_messages", "canonical_cache_subset",
                   "canonical_cache_separate", "multica_input_includes_cache",
                   "multica_input_excludes_cache", "unreported"})


class BudgetError(ValueError):
    """Invalid evidence or conflicting ledger operation."""


def _name(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise BudgetError(f"{field} must be a nonempty string")
    return value


def _integer(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise BudgetError(f"{field} must be a nonnegative integer")
    return value


def _raw(value: Any) -> Any:
    """Validate and copy JSON without discarding the original provider evidence."""
    def validate(item: Any) -> None:
        if isinstance(item, bool):
            raise BudgetError("boolean usage is invalid")
        if isinstance(item, (int, float)):
            if item < 0 or (isinstance(item, float) and not math.isfinite(item)):
                raise BudgetError("usage numbers must be finite and nonnegative")
        elif isinstance(item, dict):
            for key, child in item.items():
                if not isinstance(key, str):
                    raise BudgetError("usage keys must be strings")
                validate(child)
        elif isinstance(item, list):
            for child in item:
                validate(child)
        elif item is not None and not isinstance(item, str):
            raise BudgetError("usage must contain JSON values")
    if value is not None and not isinstance(value, dict):
        raise BudgetError("raw_usage must be an object or None")
    validate(value)
    return json.loads(json.dumps(value, allow_nan=False))


def _normalize(raw: Any, mode: str) -> dict:
    if not isinstance(mode, str) or mode not in MODES:
        raise BudgetError(f"unsupported normalization_mode: {mode}")
    reasons: list[str] = []
    raw = _raw(raw)
    if raw is None or mode == "unreported":
        return {"non_cached_input_tokens": None, "cached_input_tokens": None,
                "output_tokens": None, "total_tokens": 0, "verified": False,
                "reasons": ["usage_unreported"]}

    def counter(mapping: dict, key: str, *, optional: bool = False) -> int | None:
        if key not in mapping:
            if optional:
                return 0
            reasons.append(f"missing:{key}")
            return None
        if mapping[key] is None:
            reasons.append(f"null:{key}")
            return None
        return _integer(mapping[key], key)

    def details(key: str) -> dict:
        item = raw.get(key, {})
        if not isinstance(item, dict):
            raise BudgetError(f"{key} must be an object")
        return item

    separate = mode in {"anthropic_messages", "canonical_cache_separate",
                        "multica_input_excludes_cache"}
    if mode.startswith("multica_"):
        inp = counter(raw, "total_input_tokens")
        out = counter(raw, "total_output_tokens")
        read = counter(raw, "total_cache_read_tokens")
        write = counter(raw, "total_cache_write_tokens")
        unreported = counter(raw, "unreported_task_count")
        if unreported:
            reasons.append("unreported_tasks")
    else:
        inp, out = counter(raw, "input_tokens"), counter(raw, "output_tokens")
        if mode == "openai_responses":
            read = counter(details("input_tokens_details"), "cached_tokens", optional=True)
            write = 0
            reasoning = counter(details("output_tokens_details"), "reasoning_tokens", optional=True)
            if out is not None and reasoning is not None and reasoning > out:
                raise BudgetError("reasoning_tokens exceeds inclusive output_tokens")
        elif mode == "anthropic_messages":
            read = counter(raw, "cache_read_input_tokens", optional=True)
            write = counter(raw, "cache_creation_input_tokens", optional=True)
        else:
            read = counter(raw, "cache_read_tokens")
            write = counter(raw, "cache_write_tokens")
    cache = None if read is None or write is None else read + write
    if not separate and inp is not None and cache is not None and cache > inp:
        raise BudgetError("cache subset exceeds inclusive input_tokens")
    noncache = inp if separate else (inp - cache if inp is not None and cache is not None else None)
    # Inclusive input remains fully countable even if cache breakdown is missing.
    known_cache = (read or 0) + (write or 0)
    total_input = (inp or 0) + known_cache if separate else (inp if inp is not None else known_cache)
    total = total_input + (out or 0)
    if mode == "openai_responses" and "total_tokens" in raw:
        reported_total = _integer(raw["total_tokens"], "total_tokens")
        if inp is not None and out is not None and reported_total != total:
            raise BudgetError("total_tokens disagrees with input/output counters")
    return {"non_cached_input_tokens": noncache, "cached_input_tokens": cache,
            "output_tokens": out, "total_tokens": total,
            "verified": not reasons, "reasons": reasons}


def _path(ledger: str | Path) -> Path:
    path = Path(ledger)
    if not path.is_absolute():
        raise BudgetError("ledger must be an explicit absolute path")
    path = path.resolve()
    return path


@contextmanager
def _lock(path: Path):
    """OS-held lock: released on crash; never remove the shared lock inode."""
    lockpath = path.with_name(path.name + ".lock")
    descriptor = os.open(lockpath, os.O_RDWR | os.O_CREAT, 0o600)
    locked = False
    try:
        if os.fstat(descriptor).st_size == 0:
            os.write(descriptor, b"0")
        deadline = time.monotonic() + 10
        while True:
            try:
                if os.name == "nt":
                    import msvcrt
                    os.lseek(descriptor, 0, os.SEEK_SET)
                    msvcrt.locking(descriptor, msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
                locked = True
                break
            except OSError:
                if time.monotonic() >= deadline:
                    raise BudgetError("ledger is busy; retry without dropping the call")
                time.sleep(0.02)
        yield
    finally:
        if locked:
            if os.name == "nt":
                import msvcrt
                os.lseek(descriptor, 0, os.SEEK_SET)
                msvcrt.locking(descriptor, msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(descriptor, fcntl.LOCK_UN)
        os.close(descriptor)


def _save(path: Path, data: dict) -> None:
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix=path.name + ".", suffix=".tmp", delete=False) as stream:
            temporary = stream.name
            json.dump(data, stream, ensure_ascii=False, allow_nan=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        if os.name != "nt":
            descriptor = os.open(path.parent, os.O_RDONLY)
            try:
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
    finally:
        if temporary and os.path.exists(temporary):
            os.unlink(temporary)


def _clock() -> tuple[float, float]:
    return time.time(), time.monotonic()


def _clock_source() -> str:
    # This host label only supplements _boot_id; it is not a boot identity.
    return platform.system() + ":" + platform.node()


def _boot_id() -> str | None:
    """Read an OS boot identity, never derive it from adjustable wall time.

    Windows BootId increments on each successful boot (Microsoft documentation):
    https://learn.microsoft.com/en-us/windows-hardware/design/device-experiences/oem-hvci-enablement
    Linux boot_id is a UUID stable within a boot (kernel documentation):
    https://docs.kernel.org/admin-guide/sysctl/kernel.html#random
    Unsupported platforms, absent counters, and denied reads fail closed.
    """
    try:
        system = platform.system()
        if system == "Windows":
            import winreg
            key_path = (r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management"
                        r"\PrefetchParameters")
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0,
                                winreg.KEY_READ | winreg.KEY_WOW64_64KEY) as key:
                value, kind = winreg.QueryValueEx(key, "BootId")
            if kind == winreg.REG_DWORD and type(value) is int and value >= 0:
                return "windows_registry_boot_id:" + str(value)
        elif system == "Darwin":
            import ctypes
            libc = ctypes.CDLL(None, use_errno=True)
            probe = libc.sysctlbyname
            probe.argtypes = [ctypes.c_char_p, ctypes.c_void_p, ctypes.POINTER(ctypes.c_size_t), ctypes.c_void_p, ctypes.c_size_t]
            probe.restype = ctypes.c_int
            size = ctypes.c_size_t(256)
            buffer = ctypes.create_string_buffer(size.value)
            if probe(b"kern.bootsessionuuid", buffer, ctypes.byref(size), None, 0) == 0:
                value = UUID(buffer.value.decode("ascii"))
                if value.int:
                    return "darwin_boot_uuid:" + str(value)
        elif system == "Linux":
            value = UUID(Path("/proc/sys/kernel/random/boot_id").read_text(encoding="ascii").strip())
            if value.int:
                return "linux_boot_uuid:" + str(value)
    except (OSError, ValueError, ImportError, UnicodeError):
        pass
    return None


def _observe(data: dict) -> None:
    anomalies = data["clock_anomalies"]
    boot_id = _boot_id()
    boot_reason = ("boot_identity_unverified" if boot_id is None or data.get("clock_boot_id") is None
                   else "boot_identity_changed" if data["clock_boot_id"] != boot_id else None)
    if boot_reason and boot_reason not in anomalies:
        anomalies.append(boot_reason)
    if data['clock_source'] != _clock_source() and 'clock_source_changed' not in anomalies:
        anomalies.append('clock_source_changed')
    if data["finished"]:
        return
    wall, mono = _clock()
    if not all(math.isfinite(value) for value in (wall, mono)):
        raise BudgetError("nonfinite clock observation")
    previous = data["clock"]
    wall_step, mono_step = wall - previous["last_wall"], mono - previous["last_mono"]
    for condition, reason in ((wall_step < 0, "wall_clock_reversed"),
                              (mono_step < 0, "monotonic_clock_reversed"),
                              (abs(wall_step - mono_step) > 5
                               or abs((wall - previous["start_wall"]) - (mono - previous["start_mono"])) > 5,
                               "clock_disagreement")):
        if condition and reason not in anomalies:
            anomalies.append(reason)
    data["elapsed_seconds"] = max(data["elapsed_seconds"], wall - previous["start_wall"],
                                   mono - previous["start_mono"], 0)
    previous.update(last_wall=wall, last_mono=mono)


def _load(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if type(data["schema_version"]) is not int or data["schema_version"] not in {1, 2}:
            raise BudgetError("unsupported ledger schema")
        root = _path(data["project_root"])
        if not path.is_relative_to(root):
            raise BudgetError("ledger is outside its declared project_root")
        _name(data["run_id"], "run_id")
        _name(data["clock_source"], "clock_source")
        if data.get("clock_boot_id") is not None:
            _name(data["clock_boot_id"], "clock_boot_id")
        _limits(data["token_limit"], data["walltime_limit_seconds"])
        if type(data["finished"]) is not bool or not isinstance(data["calls"], list):
            raise BudgetError("invalid ledger state")
        for key in ("start_wall", "start_mono", "last_wall", "last_mono"):
            value = data["clock"][key]
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                raise BudgetError("invalid persisted clock")
        elapsed = data["elapsed_seconds"]
        if isinstance(elapsed, bool) or not isinstance(elapsed, (int, float)) or not math.isfinite(elapsed) or elapsed < 0:
            raise BudgetError("invalid elapsed_seconds")
        if not isinstance(data["clock_anomalies"], list):
            raise BudgetError("invalid clock evidence")
        anomalies = data["clock_anomalies"]
        for reason in anomalies:
            _name(reason, "clock_anomalies entry")
        if len(set(anomalies)) != len(anomalies):
            raise BudgetError("duplicate clock anomaly")
        # Endpoints are retained independently of elapsed_seconds. Check them
        # even after finish(), when observing current time must not extend a run.
        clock = data["clock"]
        wall_delta = clock["last_wall"] - clock["start_wall"]
        mono_delta = clock["last_mono"] - clock["start_mono"]
        lower_bound = max(wall_delta, mono_delta, 0)
        if elapsed < lower_bound:
            raise BudgetError("elapsed_seconds is below retained clock evidence")
        required = ((wall_delta < 0, "wall_clock_reversed"),
                    (mono_delta < 0, "monotonic_clock_reversed"),
                    (abs(wall_delta - mono_delta) > 5, "clock_disagreement"))
        if any(condition and reason not in anomalies for condition, reason in required):
            raise BudgetError("clock anomalies disagree with retained clock evidence")
        if elapsed > lower_bound and not {"wall_clock_reversed", "monotonic_clock_reversed"}.intersection(anomalies):
            raise BudgetError("elapsed history requires missing clock reversal evidence")
        seen = set()
        for call in data["calls"]:
            for field in ("call_id", "stage", "agent", "provider", "run_id"):
                _name(call[field], field)
            if call["run_id"] != data["run_id"] or call["call_id"] in seen:
                raise BudgetError("duplicate call or mismatched run identity")
            seen.add(call["call_id"])
            if _integer(call["attempt"], "attempt") < 1:
                raise BudgetError("attempt starts at 1")
            if call["normalized"] != _normalize(call["raw_usage"], call["normalization_mode"]):
                raise BudgetError("stored normalization disagrees with raw usage")
        reservations = data.get("reservations", [])
        if not isinstance(reservations, list):
            raise BudgetError("invalid reservations")
        if (data['schema_version'] == 1 and reservations) or (data['schema_version'] == 2 and 'reservations' not in data):
            raise BudgetError('reservation evidence requires ledger schema 2')
        reserved_ids = set()
        calls = {call["call_id"]: call for call in data["calls"]}
        for item in reservations:
            for field in ("call_id", "run_id", "stage", "agent", "provider"):
                _name(item[field], field)
            if item['call_id'] in reserved_ids or item['run_id'] != data['run_id']:
                raise BudgetError("duplicate reservation or mismatched run identity")
            reserved_ids.add(item['call_id'])
            if _integer(item['attempt'], 'attempt') < 1 or _integer(item['token_upper_bound'], 'token_upper_bound') < 1:
                raise BudgetError("reservation attempt and bound must be positive")
            state = item['state']
            if state not in {'active', 'usage_unknown', 'settled', 'released'}:
                raise BudgetError("invalid reservation state")
            if 'release_reason' in item:
                _name(item['release_reason'], 'release_reason')
            call = calls.get(item['call_id'])
            if call is None:
                if state not in {'active', 'released'} or (state == 'released') != ('release_reason' in item):
                    raise BudgetError("reservation state has no matching call/release evidence")
            else:
                if any(item[k] != call[k] for k in ('run_id', 'stage', 'agent', 'provider', 'attempt')):
                    raise BudgetError("reservation and call identity disagree")
                expected = 'settled' if call['normalized']['verified'] else 'usage_unknown'
                if state != expected:
                    raise BudgetError("reservation state disagrees with raw call evidence")
        return data
    except (KeyError, TypeError, json.JSONDecodeError) as error:
        raise BudgetError("invalid ledger evidence") from error


def _limits(token_limit: int, walltime_limit_seconds: int) -> None:
    if not 0 < _integer(token_limit, "token_limit") < TARGET_TOKENS:
        raise BudgetError("token_limit must be positive and strictly below 20M")
    if not 0 < _integer(walltime_limit_seconds, "walltime_limit_seconds") <= MAX_WALLTIME_SECONDS:
        raise BudgetError("walltime limit must be positive and at most 7200 seconds")


def _summary(data: dict) -> dict:
    calls = data["calls"]
    total = sum(call["normalized"]["total_tokens"] for call in calls)
    unknown = sum(not call["normalized"]["verified"] for call in calls)
    calls_by_id = {call['call_id']: call for call in calls}
    reservations = data.get('reservations', [])
    active = [item for item in reservations if item['state'] in {'active', 'usage_unknown'}]
    # Known partial usage is already in total; hold the rest of the supplied
    # bound until usage is complete. Unknown usage independently stops dispatch.
    reserved = sum(max(0, item['token_upper_bound'] -
                       calls_by_id.get(item['call_id'], {}).get('normalized', {}).get('total_tokens', 0))
                   for item in active)
    overruns = sum(calls_by_id.get(item['call_id'], {}).get('normalized', {}).get('total_tokens', 0)
                   > item['token_upper_bound'] for item in reservations)
    failed = []
    if total >= TARGET_TOKENS:
        failed.append("strict_20M_target_exceeded")
    if total > data["token_limit"]:
        failed.append("run_token_limit_exceeded")
    if data["elapsed_seconds"] > data["walltime_limit_seconds"]:
        failed.append("walltime_limit_exceeded")
    if any('release_reason' in item and item['call_id'] in calls_by_id for item in reservations):
        failed.append('released_reservation_was_used')
    uncertain = []
    if unknown:
        uncertain.append("unverified_usage")
    if data["clock_anomalies"]:
        uncertain.append("unverified_clock")
    if active:
        uncertain.append('unsettled_reservations')
    if not data["finished"]:
        uncertain.append("run_not_finished")
    status = "FAIL" if failed else ("UNKNOWN" if uncertain else "PASS")
    return {"run_id": data["run_id"], "status": status, "finished": data["finished"],
            "call_count": len(calls), "unverified_call_count": unknown,
            "known_non_cached_input_tokens": sum(call["normalized"]["non_cached_input_tokens"] or 0 for call in calls),
            "known_cached_input_tokens": sum(call["normalized"]["cached_input_tokens"] or 0 for call in calls),
            "known_output_tokens": sum(call["normalized"]["output_tokens"] or 0 for call in calls),
            "total_tokens": total, "token_limit": data["token_limit"],
            "reserved_tokens": reserved, "active_reservation_count": len(active),
            "reservation_overrun_count": overruns,
            "available_tokens": max(0, data['token_limit'] - total - reserved),
            "target_tokens_exclusive": TARGET_TOKENS,
            "elapsed_seconds": data["elapsed_seconds"],
            "walltime_limit_seconds": data["walltime_limit_seconds"],
            "clock_anomalies": list(data["clock_anomalies"]),
            "reasons": failed + uncertain,
            "can_continue": not data["finished"] and not unknown and not data["clock_anomalies"] and not failed
                and total + reserved < data["token_limit"] and data["elapsed_seconds"] < data["walltime_limit_seconds"]}


def start(ledger: str | Path, run_id: str, *, project_root: str | Path,
          token_limit: int = DEFAULT_TOKEN_LIMIT,
          walltime_limit_seconds: int = MAX_WALLTIME_SECONDS) -> dict:
    """Start immediately before end-to-end work. Refuses to overwrite a run.

    Ledger must be within project_root. The caller selects its local data path.
    Bounds only govern checks: record always preserves real over-limit evidence.
    """
    path, root = _path(ledger), _path(project_root)
    _name(run_id, "run_id")
    _limits(token_limit, walltime_limit_seconds)
    if not root.is_dir() or path == root or not path.is_relative_to(root):
        raise BudgetError("ledger must be within an existing project_root")
    path.parent.mkdir(parents=True, exist_ok=True)
    with _lock(path):
        if path.exists():
            raise BudgetError("ledger already exists; use a new ledger for a new run")
        wall, mono = _clock()
        if not all(math.isfinite(value) for value in (wall, mono)):
            raise BudgetError("nonfinite clock observation")
        boot_id = _boot_id()
        data = {"schema_version": 1, "run_id": run_id, "project_root": str(root),
                "token_limit": token_limit, "walltime_limit_seconds": walltime_limit_seconds,
                "finished": False, "elapsed_seconds": 0,
                "clock_anomalies": [] if boot_id is not None else ["boot_identity_unverified"],
                "clock_source": _clock_source(),
                "clock_boot_id": boot_id,
                "clock": {"start_wall": wall, "start_mono": mono, "last_wall": wall, "last_mono": mono},
                "calls": [], "reservations": []}
        _save(path, data)
        return _summary(data)


def record(ledger: str | Path, call_id: str, raw_usage: dict | None, *, run_id: str,
           normalization_mode: str, stage: str, agent: str, provider: str,
           attempt: int = 1) -> dict:
    """Record every provider attempt under a unique call_id, even failed attempts.

    Reusing an ID is idempotent only when raw evidence AND all identity fields
    are unchanged. Child-agent input/output belongs here too. Finished runs are
    immutable. A matching reservation settles only with complete usage. This
    never dispatches provider work; unreserved evidence is still always counted.
    """
    path = _path(ledger)
    call = {"call_id": _name(call_id, "call_id"), "run_id": _name(run_id, "run_id"),
            "stage": _name(stage, "stage"), "agent": _name(agent, "agent"),
            "provider": _name(provider, "provider"), "attempt": _integer(attempt, "attempt"),
            "normalization_mode": normalization_mode, "raw_usage": _raw(raw_usage)}
    if attempt < 1:
        raise BudgetError("attempt starts at 1")
    call["normalized"] = _normalize(call["raw_usage"], normalization_mode)
    with _lock(path):
        data = _load(path)
        if data["finished"] or data["run_id"] != run_id:
            raise BudgetError("run is finished or run_id does not match")
        previous = next((item for item in data["calls"] if item["call_id"] == call_id), None)
        if previous is not None and previous != call:
            raise BudgetError("call_id conflicts with existing evidence")
        reservation = next((item for item in data.get('reservations', []) if item['call_id'] == call_id), None)
        if reservation is not None:
            if any(reservation[k] != call[k] for k in ('run_id', 'stage', 'agent', 'provider', 'attempt')):
                raise BudgetError('call identity conflicts with reservation')
            reservation['state'] = 'settled' if call['normalized']['verified'] else 'usage_unknown'
        if previous is None:
            data["calls"].append(call)
        _observe(data)
        _save(path, data)
        return _summary(data)


def reserve(ledger: str | Path, call_id: str, token_upper_bound: int, *, run_id: str,
            project_root: str | Path, stage: str, agent: str, provider: str,
            attempt: int = 1) -> dict:
    """Atomically hold a caller-supplied inclusive input+output upper bound.

    This is a permit for this identity, not automatic host/model integration.
    available_tokens/can_continue describe capacity for *additional* work. A
    retry needs a new call_id and reservation; evidence is never a prediction.
    Replaying an active reservation is idempotent bookkeeping, not permission
    to invoke a provider twice; the caller must enforce unique execution IDs.
    """
    path, root = _path(ledger), _path(project_root)
    item = {'call_id': _name(call_id, 'call_id'), 'run_id': _name(run_id, 'run_id'),
            'token_upper_bound': _integer(token_upper_bound, 'token_upper_bound'),
            'stage': _name(stage, 'stage'), 'agent': _name(agent, 'agent'),
            'provider': _name(provider, 'provider'), 'attempt': _integer(attempt, 'attempt'),
            'state': 'active'}
    if token_upper_bound < 1 or attempt < 1:
        raise BudgetError('reservation attempt and bound must be positive')
    if not path.is_relative_to(root) or path == root:
        raise BudgetError('reservation ledger must be within project_root')
    with _lock(path):
        data = _load(path)
        if data['finished'] or data['run_id'] != run_id or _path(data['project_root']) != root:
            raise BudgetError('run is finished or reservation project/run identity does not match')
        previous = next((entry for entry in data.get('reservations', []) if entry['call_id'] == call_id), None)
        if previous is not None:
            if any(previous[k] != item[k] for k in item if k != 'state'):
                raise BudgetError('call_id conflicts with existing reservation')
            if previous['state'] != 'active':
                raise BudgetError('reservation is no longer active; a new attempt needs a new call_id')
            _observe(data)
            _save(path, data)
            current = _summary(data)
            if (current['status'] == 'FAIL' or current['unverified_call_count'] or data['clock_anomalies']
                    or data['elapsed_seconds'] >= data['walltime_limit_seconds']):
                raise BudgetError('run cannot replay an active reservation')
            return {**current, 'reservation_created': False, 'reservation_status': 'active',
                    'reservation_call_id': call_id}
        if any(call['call_id'] == call_id for call in data['calls']):
            raise BudgetError('call_id already has recorded usage; do not reserve retrospectively')
        _observe(data)
        current = _summary(data)
        if not current['can_continue'] or token_upper_bound > current['available_tokens']:
            # Retain detected clock anomalies even when capacity refuses work.
            # Calls/reservations stay unchanged; a later clock recovery cannot
            # erase evidence of reversal and turn the run back into PASS.
            _save(path, data)
            raise BudgetError('reservation exceeds available budget or run cannot dispatch')
        data.setdefault('reservations', []).append(item)
        # Older readers reject schema 2 instead of silently ignoring holds.
        # Legacy schema 1 ledgers remain readable until their first reservation.
        data['schema_version'] = 2
        _save(path, data)
        return {**_summary(data), 'reservation_created': True, 'reservation_status': 'active',
                'reservation_call_id': call_id}


def release(ledger: str | Path, call_id: str, *, run_id: str, reason: str) -> dict:
    """Audit the caller's assertion that a reserved provider call was not made.

    Never releases recorded usage. A contradictory late record is retained and
    reported as failure, rather than discarded to preserve a previous PASS.
    """
    path = _path(ledger)
    _name(call_id, 'call_id')
    _name(run_id, 'run_id')
    _name(reason, 'reason')
    with _lock(path):
        data = _load(path)
        if data['finished'] or data['run_id'] != run_id:
            raise BudgetError('run is finished or run_id does not match')
        item = next((entry for entry in data.get('reservations', []) if entry['call_id'] == call_id), None)
        if item is None or any(call['call_id'] == call_id for call in data['calls']):
            raise BudgetError('only an uncalled reservation can be released')
        if item['state'] == 'released' and item['release_reason'] != reason:
            raise BudgetError('release reason conflicts with existing audit evidence')
        item.update(state='released', release_reason=reason)
        _observe(data)
        _save(path, data)
        return _summary(data)


def summary(ledger: str | Path) -> dict:
    """Replay raw evidence and observe elapsed wall time under the writer lock.

    total_tokens and known_* are lower bounds whenever usage is unverified.
    Finished usage/time stay frozen; newly detected boot anomalies stay sticky.
    """
    path = _path(ledger)
    with _lock(path):
        data = _load(path)
        previous_anomalies = list(data["clock_anomalies"])
        _observe(data)
        if not data["finished"] or previous_anomalies != data["clock_anomalies"]:
            _save(path, data)
        return _summary(data)


def check(ledger: str | Path) -> dict:
    """Return PASS/FAIL/UNKNOWN plus can_continue; never calls a model."""
    return summary(ledger)


def check_for_dispatch(ledger: str | Path, *, run_id: str,
                       project_root: str | Path) -> dict:
    """Check an explicitly selected run at the scheduler dispatch boundary.

    This observes supplied evidence (including outstanding reservations); it neither reserves future tokens nor
    verifies that the host has reported every call. Landing work remains allowed
    after this check refuses further dispatch.
    """
    path, root = _path(ledger), _path(project_root)
    _name(run_id, "run_id")
    if not path.is_relative_to(root) or path == root:
        raise BudgetError("dispatch ledger must be within project_root")
    with _lock(path):
        data = _load(path)
        if data["run_id"] != run_id or _path(data["project_root"]) != root:
            raise BudgetError("dispatch ledger project or run identity does not match")
        _observe(data)
        _save(path, data)
        return _summary(data)


def finish(ledger: str | Path, *, run_id: str) -> dict:
    """Freeze end-to-end elapsed time after all waits/builds/validation complete."""
    path = _path(ledger)
    with _lock(path):
        data = _load(path)
        if data["run_id"] != run_id:
            raise BudgetError("run_id does not match")
        if any(item['state'] in {'active', 'usage_unknown'} for item in data.get('reservations', [])):
            raise BudgetError('settle usage or audit uncalled reservation releases before finishing')
        _observe(data)
        data["finished"] = True
        _save(path, data)
        return _summary(data)
