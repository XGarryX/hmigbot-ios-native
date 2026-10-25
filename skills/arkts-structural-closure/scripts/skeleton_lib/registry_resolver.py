"""RegistryResolver: parse placeholder-registry.md + resource-mapping.md and
decide whether a skeleton finding is "legitimate" (L1) — i.e. covered by a
registered placeholder, FWD-REF marker, or intentional-default rule.

Inputs:
- spec/placeholder-registry.md         — 6-col markdown table.
  Parsing is HEADER-AWARE: columns are mapped by name from each table's header
  row, so both the canonical template order (P-ID|location|trigger_condition|
  status|kind|resolve_by) and drifted orders produced by execute-phase agents
  (e.g. status last) load identically. Cell values tolerate markdown noise:
  backticks/strikethrough around location, `**resolved**（批注）`-style status.
  A headerless table falls back to the legacy positional regex.
- spec/baseline/plans/resource-mapping.md — kind=intentional-default section

Outputs (queried by classifier):
- is_fwd_ref_resolved(p_id) -> bool
- is_fwd_ref_known(p_id) -> bool
- is_sdk_placeholder(p_id) -> Optional[dict]
- is_intentional_default(file, resource_id) -> bool
- rows_loaded -> int  (registry liveness — audit_skeletons guards on 0)
"""
from __future__ import annotations
import re
from pathlib import Path
from typing import Optional

# Legacy positional fallback (canonical template order), used only when a table
# carries no recognizable header row.
_TABLE_ROW = re.compile(
    r"^\|\s*(?P<p_id>P-[A-Za-z0-9_-]+)\s*"
    r"\|\s*(?P<location>[^|]+?)\s*"
    r"\|\s*(?P<trigger>[^|]+?)\s*"
    r"\|\s*(?P<status>[A-Za-z_]+)\s*"
    r"\|\s*(?P<kind>[A-Za-z-]+)\s*"
    r"\|\s*(?P<resolve_by>[^|]*?)\s*\|"
)

# Header cell text → canonical field name. Unknown headers map to None (cell ignored).
_HEADER_ALIASES = {
    "p-id": "p_id",
    "p_id": "p_id",
    "location": "location",
    "trigger_condition": "trigger_condition",
    "trigger": "trigger_condition",
    "status": "status",
    "kind": "kind",
    "resolve_by": "resolve_by",
}

_P_ID_ANY = re.compile(r"P-[A-Za-z0-9_-]+")
# First enum-like token in a cell: `**resolved**（2026-07-22 …）` → resolved,
# `emitted 🔴` → emitted, `forward-ref` → forward-ref.
_ENUM_TOKEN = re.compile(r"[A-Za-z][A-Za-z_-]*")


def _split_cells(line: str) -> list[str]:
    core = line.strip()
    if core.startswith("|"):
        core = core[1:]
    if core.endswith("|"):
        core = core[:-1]
    return [c.strip() for c in core.split("|")]


def _norm_enum(cell: str) -> str:
    s = cell.replace("*", "").replace("~", "").strip()
    m = _ENUM_TOKEN.search(s)
    return m.group(0) if m else s


def _norm_location(cell: str) -> str:
    return cell.strip().strip("`~*").strip()

# A simple section detector for resource-mapping.md to find the
# kind=intentional-default block — convention: a H2 / H3 heading mentions
# "intentional-default" or "兜底图" or "默认资源".
_INTENT_DEFAULT_SECTION_HEAD = re.compile(
    r"^#{2,3}\s+.*(intentional[- ]?default|兜底图|默认资源)",
    re.IGNORECASE,
)
_NEXT_SECTION = re.compile(r"^#{2,3}\s+")
_RESOURCE_ID_IN_TABLE = re.compile(
    r"\$r\(\s*['\"](?P<rid>app\.[a-z]+\.[a-zA-Z0-9_]+)['\"]\s*\)"
)


class RegistryResolver:
    def __init__(
        self,
        registry_path: Optional[Path] = None,
        resource_mapping_path: Optional[Path] = None,
    ):
        # P-ID → dict(location, trigger, status, kind, resolve_by)
        self._registry: dict[str, dict] = {}
        # set of resource IDs (e.g. "app.media.ic_default_avatar") declared intentional
        self._intentional_defaults: set[str] = set()

        if registry_path and registry_path.exists():
            self._load_registry(registry_path)
        if resource_mapping_path and resource_mapping_path.exists():
            self._load_resource_mapping(resource_mapping_path)

    # ── Loading ─────────────────────────────────────────────────────────────
    @property
    def rows_loaded(self) -> int:
        return len(self._registry)

    def _store(self, p_id: str, location: str, trigger: str,
               status: str, kind: str, resolve_by: str) -> None:
        self._registry[p_id] = {
            "p_id": p_id,
            "location": _norm_location(location),
            "trigger_condition": trigger.strip(),
            "status": _norm_enum(status),
            "kind": _norm_enum(kind),
            "resolve_by": resolve_by.strip(),
        }

    def _load_registry(self, path: Path) -> None:
        text = path.read_text(encoding="utf-8", errors="replace")
        # Column map of the table currently being read (from its header row).
        # None → not inside a recognized registry table; reset at each non-|
        # line so an unrelated later table (延期记录 / 校验失败) can't inherit it.
        col_order: Optional[list] = None
        for line in text.splitlines():
            if not line.lstrip().startswith("|"):
                col_order = None
                continue
            cells = _split_cells(line)
            if set("".join(cells)) <= set("-: "):
                continue  # separator row
            lowered = [c.strip("` *").lower() for c in cells]
            if any(c in ("p-id", "p_id") for c in lowered):
                mapped = [_HEADER_ALIASES.get(c) for c in lowered]
                # Registry tables must at least name location + kind; other
                # P-ID tables (defer log, failure lists) are skipped entirely.
                col_order = mapped if ("location" in mapped and "kind" in mapped) else None
                continue
            if col_order is None:
                m = _TABLE_ROW.match(line)
                if m:
                    self._store(m.group("p_id"), m.group("location"), m.group("trigger"),
                                m.group("status"), m.group("kind"), m.group("resolve_by"))
                continue
            entry: dict[str, str] = {}
            for idx, name in enumerate(col_order):
                if name and idx < len(cells):
                    entry[name] = cells[idx]
            pid_m = _P_ID_ANY.search(entry.get("p_id", ""))
            if not pid_m:
                continue
            self._store(pid_m.group(0), entry.get("location", ""),
                        entry.get("trigger_condition", ""), entry.get("status", ""),
                        entry.get("kind", ""), entry.get("resolve_by", ""))

    def _load_resource_mapping(self, path: Path) -> None:
        text = path.read_text(encoding="utf-8", errors="replace")
        lines = text.splitlines()
        in_section = False
        for i, line in enumerate(lines):
            if _INTENT_DEFAULT_SECTION_HEAD.match(line):
                in_section = True
                continue
            if in_section and _NEXT_SECTION.match(line):
                in_section = False
                continue
            if in_section:
                for m in _RESOURCE_ID_IN_TABLE.finditer(line):
                    self._intentional_defaults.add(m.group("rid"))

    # ── Queries used by classifier ──────────────────────────────────────────
    def is_fwd_ref_known(self, p_id: str) -> bool:
        entry = self._registry.get(p_id)
        return bool(entry and entry["kind"] == "forward-ref")

    def is_fwd_ref_resolved(self, p_id: str) -> bool:
        entry = self._registry.get(p_id)
        return bool(entry and entry["kind"] == "forward-ref" and entry["status"] == "resolved")

    def is_sdk_placeholder_registered(self, p_id: str) -> bool:
        entry = self._registry.get(p_id)
        return bool(entry and entry["kind"] == "thirdparty-sdk")

    def get_entry(self, p_id: str) -> Optional[dict]:
        return self._registry.get(p_id)

    def get_entry_by_location(self, location: str) -> Optional[dict]:
        """Reverse lookup: find registry entry whose `location` field matches.

        Used by `scan_resource_jsons` to check whether a `[TODO: translate]` in
        resources/<locale>/element/string.json:home_feed has a corresponding
        resource-pending-translation registry entry.

        Match is exact-string by default; if not found, also tries prefix match
        (`location.startswith(self_location)`) to handle minor path quoting diffs.
        """
        for entry in self._registry.values():
            entry_loc = entry.get("location", "")
            if entry_loc == location:
                return entry
        # Fallback: prefix / endswith for paths with subtle diff
        for entry in self._registry.values():
            entry_loc = entry.get("location", "")
            if entry_loc and (entry_loc.endswith(location) or location.endswith(entry_loc)):
                return entry
        return None

    def all_unresolved_fwd_refs(self) -> dict[str, dict]:
        return {
            p_id: e
            for p_id, e in self._registry.items()
            if e["kind"] == "forward-ref" and e["status"] != "resolved"
        }

    def is_intentional_default_resource(self, resource_id: str) -> bool:
        return resource_id in self._intentional_defaults

    # ── Convenience constructors ────────────────────────────────────────────
    @classmethod
    def from_project(cls, project_root: Path) -> "RegistryResolver":
        return cls(
            registry_path=project_root / "spec" / "placeholder-registry.md",
            resource_mapping_path=project_root / "spec" / "baseline" / "plans" / "resource-mapping.md",
        )
