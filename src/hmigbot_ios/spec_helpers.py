"""Auditable object contract around the bundled HMigBot spec helpers.

The divergence and traceability helpers are shipped as compiled Nuitka
binaries; their internal filename filters and rule implementations are not in
this repository.  This module does not re-implement or replace them.  It keeps
the original helper as the only implementation of its own protocol (R1/R2/R3/
R5 divergence checks, decision-ledger resolution and requirements-index
derivation) and adds the source-visible object contract that the helpers lack:

1. ``spec_discovery`` decides the expected document and AC identity set;
2. a temporary, read-only shadow of the features directory gives a document
   the helper's historical ASCII filename only when that helper's filter would
   otherwise miss it; real project files are never renamed or edited, and the
   alias is deterministic (derived from the real file name);
3. the original helper runs with the caller's arguments - ledger path and
   ``--gate`` semantics are unchanged - against that shadow;
4. the helper's reported mains/AC counts, or its emitted index contents, are
   compared with the expected set and count; duplicate IDs, unknown mappings,
   a non-empty expectation with zero actual objects and schema drift all fail
   closed;
5. aliases are mapped back to the real relative paths before an index is
   published.

Diagnostics are plain text, never JSON disguised as a log.  The only JSON this
module writes is the published requirements index after it passed the object
contract.  When the contract cannot be guaranteed the caller exits nonzero and
no PASS is printed.
"""
from __future__ import annotations

from collections import Counter
from contextlib import contextmanager
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from typing import Iterator

from . import spec_discovery

DIVERGENCE = 'lint_divergence'
TRACEABILITY = 'build_traceability_index'

# Observed CLI-side filename filters of the compiled helpers.  They are used
# only to decide whether a real name needs an ASCII alias; the expected/actual
# count comparison independently verifies that the set the helper read is the
# set this package expects, so a filter change fails closed instead of passing.
_DIVERGENCE_MAIN = re.compile(r'F\d+-[a-z0-9-]+\.md')
_TRACEABILITY_MAIN = re.compile(r'[A-Z][A-Za-z0-9]*\d+-[a-z0-9-]+\.md')

_AC_ID = re.compile(r'^F\d+-AC\d+$')
_DIGEST = re.compile(r'^sha256:[0-9a-f]{8,128}$')
_REQUIRED_FIELDS = ('requirement_id', 'kind', 'feature_id', 'spec_uri',
                    'assertion', 'assertion_digest', 'status')


class HelperError(RuntimeError):
    """The bundled helper or its launcher is not usable."""

    def __init__(self, code: str, message: str):
        super().__init__('%s: %s' % (code, message))
        self.code = code
        self.detail = message


class ObjectContractError(RuntimeError):
    """Expected and actual objects disagree; never convert this to a PASS."""

    def __init__(self, code: str, message: str):
        super().__init__('%s: %s' % (code, message))
        self.code = code
        self.detail = message


@dataclass(frozen=True)
class HelperResult:
    returncode: int
    stdout: bytes
    stderr: bytes


@dataclass(frozen=True)
class Shadow:
    root: Path
    features_dir: Path
    aliases: dict[str, str]  # helper-facing file name -> real file name


@dataclass(frozen=True)
class DivergenceArguments:
    spec_dir: str | None
    ledger: str | None
    allow_empty: bool
    forward: tuple[str, ...]


@dataclass(frozen=True)
class TraceabilityArguments:
    project_root: str | None
    out: str | None
    allow_empty: bool
    forward: tuple[str, ...]


@dataclass(frozen=True)
class TraceabilityStats:
    requirements: int
    documents: int
    aliased: int
    rewritten_uris: int


def helper_script(root: Path, name: str) -> Path:
    if name not in (DIVERGENCE, TRACEABILITY):
        raise HelperError('HELPER_UNKNOWN', name)
    script = Path(root) / 'vendor/hmigbot/skills/a2h-spec/scripts' / (name + '.py')
    if not script.is_file():
        raise HelperError('HELPER_MISSING',
                          '%s is missing; reinstall the complete plugin' % script)
    return script


def run_helper(script: Path, args) -> HelperResult:
    """Run the bundled helper unchanged, capturing raw stdout/stderr bytes."""
    command = [sys.executable, '-X', 'utf8', str(script), *map(str, args)]
    environment = dict(os.environ)
    environment['PYTHONUTF8'] = '1'
    environment['PYTHONIOENCODING'] = 'utf-8'
    environment.setdefault('A2H_TELEMETRY_OFF', '1')
    from .portable_helper import run
    completed = run(script, args, env=environment, capture_output=True)
    return HelperResult(completed.returncode, completed.stdout, completed.stderr)


def forward(result: HelperResult, *, aliases: dict[str, str] | None = None,
            replacements: tuple[tuple[str, str], ...] = ()) -> None:
    """Write helper output unchanged except for agreed alias/path remapping."""
    stdout, stderr = result.stdout, result.stderr
    if aliases or replacements:
        stdout = _remap_bytes(stdout, aliases or {}, replacements)
        stderr = _remap_bytes(stderr, aliases or {}, replacements)
    _write(sys.stdout, stdout)
    _write(sys.stderr, stderr)


def _remap_bytes(data: bytes, aliases: dict[str, str],
                 replacements: tuple[tuple[str, str], ...]) -> bytes:
    text = data.decode('utf-8', 'replace')
    ordered = sorted(replacements, key=lambda item: len(item[0]), reverse=True)
    ordered += sorted(((alias, real) for alias, real in aliases.items()),
                      key=lambda item: len(item[0]), reverse=True)
    for old, new in ordered:
        text = text.replace(old, new)
    return text.encode('utf-8')


def rendered(result: HelperResult, *, aliases: dict[str, str] | None = None,
             replacements: tuple[tuple[str, str], ...] = ()) -> tuple[str, str]:
    """Helper output as text with the agreed path/alias remapping applied."""
    return (_remap_bytes(result.stdout, aliases or {}, replacements).decode('utf-8', 'replace'),
            _remap_bytes(result.stderr, aliases or {}, replacements).decode('utf-8', 'replace'))


def path_replacements(shadow_root: Path, real_root: Path) -> tuple[tuple[str, str], ...]:
    """Path forms the helper may print, with both separator styles."""
    pairs: list[tuple[str, str]] = []
    for shadow, real in ((str(shadow_root), str(real_root)),
                         (str(shadow_root).replace('\\', '/'),
                          str(real_root).replace('\\', '/'))):
        pairs.append((shadow, real))
    return tuple(pairs)


def _write(stream, data: bytes) -> None:
    buffer = getattr(stream, 'buffer', None)
    if buffer is not None:
        buffer.write(data)
        buffer.flush()
    else:
        stream.write(data.decode('utf-8', 'replace'))
        stream.flush()


def temp_base() -> str:
    """Temporary work stays on the D drive on this Windows runtime."""
    if os.name == 'nt':
        candidate = Path('D:/Temp')
        if candidate.is_dir():
            return str(candidate)
    return tempfile.gettempdir()


def helper_discovers(name: str, helper_name: str) -> bool:
    if helper_name == DIVERGENCE:
        return _DIVERGENCE_MAIN.fullmatch(name) is not None
    if helper_name == TRACEABILITY:
        return _TRACEABILITY_MAIN.fullmatch(name) is not None
    raise HelperError('HELPER_UNKNOWN', helper_name)


def alias_name(document: spec_discovery.FeatureDocument) -> str:
    """Deterministic ASCII alias that keeps the stable F-ID."""
    digest = hashlib.sha256(document.name.encode('utf-8')).hexdigest()[:12]
    return '%s-doc-%s.md' % (document.feature_id, digest)


@contextmanager
def shadow_features(features_dir: Path, discovery: spec_discovery.Discovery,
                    helper_name: str) -> Iterator[Shadow]:
    """Copy the features directory, aliasing only documents the helper misses."""
    spec_discovery.reject_links(features_dir)
    for entry in Path(features_dir).iterdir():
        spec_discovery.reject_links(entry)
    root = Path(tempfile.mkdtemp(prefix='hmigbot-object-gate-', dir=temp_base()))
    try:
        shadow = root / 'spec/baseline/features'
        shadow.mkdir(parents=True)
        by_name = {document.name: document for document in discovery.documents}
        aliases: dict[str, str] = {}
        for entry in sorted(Path(features_dir).iterdir(), key=lambda item: item.name):
            spec_discovery.reject_links(entry)
            if not entry.is_file():
                continue
            document = by_name.get(entry.name)
            if (document is not None and document.is_main
                    and not helper_discovers(document.name, helper_name)):
                alias = alias_name(document)
                counter = 1
                while alias in aliases or (shadow / alias).exists():
                    counter += 1
                    alias = '%s-%d.md' % (alias_name(document)[:-3], counter)
                shutil.copyfile(entry, shadow / alias)
                aliases[alias] = entry.name
            else:
                shutil.copyfile(entry, shadow / entry.name)
        yield Shadow(root=root, features_dir=shadow, aliases=aliases)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def validate_output_path(path: Path, project_root: Path,
                         discovery: spec_discovery.Discovery) -> None:
    """Refuse source clobbering before invoking a helper or publishing JSON.

    Existing JSON indexes outside source directories remain replaceable. Link
    checks precede resolve, while samefile detects hard-link aliases of inputs.
    """
    path = Path(path)
    spec_discovery.reject_links(path)
    if path.suffix.lower() != '.json' or path.is_dir():
        raise ObjectContractError('OUTPUT_CONFLICT', 'index output must be a JSON file: %s' % path)
    actual = path.resolve()
    baseline = Path(project_root) / 'spec/baseline'
    for directory in (baseline, discovery.spec_dir):
        spec_discovery.reject_links(directory)
        if actual.is_relative_to(directory.resolve()):
            raise ObjectContractError('OUTPUT_CONFLICT', 'output is inside source directory: %s' % path)
    inputs = [document.path for document in discovery.documents]
    # Protect every baseline input, including non-feature Markdown and ledgers,
    # from hard-link aliases named *.json outside the baseline directory.
    spec_root = Path(project_root) / 'spec'
    if spec_root.is_dir():
        for entry in spec_root.rglob('*'):
            spec_discovery.reject_links(entry)
            if entry.is_file() and (entry.is_relative_to(baseline) or entry.suffix.lower() == '.md'):
                inputs.append(entry)
    for entry in discovery.spec_dir.iterdir():
        spec_discovery.reject_links(entry)
        if entry.is_file():
            inputs.append(entry)
    for source in inputs:
        if actual == source.resolve() or (path.exists() and source.exists() and path.samefile(source)):
            raise ObjectContractError('OUTPUT_CONFLICT', 'output aliases source input: %s' % source)


def parse_divergence_arguments(args) -> DivergenceArguments:
    spec_dir = ledger = None
    allow_empty = False
    forward: list[str] = []
    index = 0
    values = list(args)
    while index < len(values):
        token = values[index]
        if token == '--allow-empty':
            allow_empty = True
            index += 1
            continue
        if token == '--gate':
            forward.append(token)
            index += 1
            continue
        if token == '--spec-dir' or token == '--ledger':
            forward.append(token)
            if index + 1 < len(values):
                if token == '--spec-dir':
                    spec_dir = values[index + 1]
                else:
                    ledger = values[index + 1]
                forward.append(values[index + 1])
                index += 2
            else:
                index += 1
            continue
        if token.startswith('--spec-dir='):
            spec_dir = token.split('=', 1)[1]
            forward.append(token)
            index += 1
            continue
        if token.startswith('--ledger='):
            ledger = token.split('=', 1)[1]
            forward.append(token)
            index += 1
            continue
        forward.append(token)
        index += 1
    return DivergenceArguments(spec_dir=spec_dir, ledger=ledger,
                               allow_empty=allow_empty, forward=tuple(forward))


def parse_traceability_arguments(args) -> TraceabilityArguments:
    project_root = out = None
    allow_empty = False
    forward: list[str] = []
    index = 0
    values = list(args)
    while index < len(values):
        token = values[index]
        if token == '--allow-empty':
            allow_empty = True
            index += 1
            continue
        if token == '--project-root' or token == '--out':
            forward.append(token)
            if index + 1 < len(values):
                if token == '--project-root':
                    project_root = values[index + 1]
                else:
                    out = values[index + 1]
                forward.append(values[index + 1])
                index += 2
            else:
                index += 1
            continue
        if token.startswith('--project-root='):
            project_root = token.split('=', 1)[1]
            forward.append(token)
            index += 1
            continue
        if token.startswith('--out='):
            out = token.split('=', 1)[1]
            forward.append(token)
            index += 1
            continue
        forward.append(token)
        index += 1
    return TraceabilityArguments(project_root=project_root, out=out,
                                 allow_empty=allow_empty, forward=tuple(forward))


def rewrite_option(args, option: str, value: str, *, append_if_missing: bool = True) -> list[str]:
    """Replace one option value while preserving every other caller argument."""
    result: list[str] = []
    found = False
    index = 0
    values = list(args)
    while index < len(values):
        token = values[index]
        if token == option:
            found = True
            result.append(option)
            result.append(value)
            index += 2 if index + 1 < len(values) else 1
            continue
        if token.startswith(option + '='):
            found = True
            result.append(option + '=' + value)
            index += 1
            continue
        result.append(token)
        index += 1
    if not found and append_if_missing:
        result.extend([option, value])
    return result


def default_ledger(spec_dir_argument: str) -> str:
    """The helper's default ledger, expressed against the real features dir."""
    return os.path.normpath(os.path.join(spec_dir_argument, '..', '..', 'decision-ledger.md'))


def parse_divergence_counts(text: str) -> dict[str, int]:
    match = re.search(r'mains=(\d+)\s+parity ACs=(\d+)\s+divergence ACs=(\d+)', text)
    if match is None:
        raise ObjectContractError(
            'HELPER_OUTPUT_UNPARSED',
            'divergence summary line not found; helper output protocol changed')
    return {'mains': int(match.group(1)), 'parity': int(match.group(2)),
            'divergence': int(match.group(3))}


def verify_divergence_objects(discovery: spec_discovery.Discovery,
                              reported: dict[str, int], *,
                              allow_empty: bool = False) -> None:
    """Compare the helper's summary with the expected document/AC counts.

    The divergence helper reports only aggregate counts, so this guard verifies
    the document count and the parity/divergence totals.  Identity-level
    comparison of every AC is performed by the traceability wrapper, whose
    helper emits the full requirement list.
    """
    expected = spec_discovery.divergence_counts(discovery)
    if expected['mains'] == 0:
        if not allow_empty:
            raise ObjectContractError(
                'ZERO_OBJECTS',
                'no main feature document under %s and --allow-empty was not given'
                % discovery.spec_dir)
        if reported != expected:
            raise ObjectContractError(
                'EXPECTED_COUNT_MISMATCH',
                'empty scope accepted, but helper reported mains=%d parity ACs=%d '
                'divergence ACs=%d instead of 0/0/0'
                % (reported['mains'], reported['parity'], reported['divergence']))
        return
    if reported['mains'] == 0:
        raise ObjectContractError(
            'ZERO_OBJECTS',
            'expected %d main document(s) and %d parity AC(s), helper read 0 objects '
            '(expected/actual set mismatch)' % (expected['mains'], expected['parity']))
    if reported != expected:
        raise ObjectContractError(
            'EXPECTED_COUNT_MISMATCH',
            'expected mains=%(mains)d parity ACs=%(parity)d divergence ACs=%(divergence)d; '
            'helper reported mains=%(actual_mains)d parity ACs=%(actual_parity)d '
            'divergence ACs=%(actual_divergence)d' % {
                **expected,
                'actual_mains': reported['mains'],
                'actual_parity': reported['parity'],
                'actual_divergence': reported['divergence'],
            })


def load_json(path: Path):
    try:
        return json.loads(Path(path).read_text(encoding='utf-8'))
    except (OSError, ValueError) as exc:
        raise ObjectContractError('INDEX_UNREADABLE', '%s: %s' % (path, exc)) from exc


def validate_traceability_index(payload, discovery: spec_discovery.Discovery,
                                aliases: dict[str, str]) -> tuple[dict, TraceabilityStats]:
    """Validate every indexed requirement against the real document set.

    Returns a normalized payload whose ``spec_uri`` values are real POSIX
    relative paths (``spec/baseline/features/<real name>``).  Raises
    ``ObjectContractError`` before anything is published when identities,
    counts, mappings or meta counters disagree.
    """
    expected_items = spec_discovery.expected_requirements(discovery)
    expected_ids = [item.requirement_id for item in expected_items]
    if not isinstance(payload, dict):
        raise ObjectContractError('INDEX_SCHEMA', 'top level must be a JSON object')
    requirements = payload.get('requirements')
    if not isinstance(requirements, list):
        raise ObjectContractError('INDEX_SCHEMA', 'requirements must be a list')
    meta = payload.get('_meta')
    if not isinstance(meta, dict):
        raise ObjectContractError('INDEX_SCHEMA', '_meta must be an object')

    by_name = {document.name: document for document in discovery.documents}
    expected_by_id: dict[str, list[spec_discovery.RequirementExpectation]] = {}
    for item in expected_items:
        expected_by_id.setdefault(item.requirement_id, []).append(item)

    normalized = json.loads(json.dumps(payload))  # detached deep copy
    actual_ids: list[str] = []
    rewritten = 0
    for position, requirement in enumerate(requirements):
        if not isinstance(requirement, dict):
            raise ObjectContractError('INDEX_SCHEMA', 'requirement %d is not an object' % position)
        missing = [field for field in _REQUIRED_FIELDS if field not in requirement]
        if missing:
            raise ObjectContractError(
                'INDEX_SCHEMA', 'requirement %d lacks %s' % (position, ', '.join(missing)))
        requirement_id = requirement['requirement_id']
        if not isinstance(requirement_id, str) or _AC_ID.fullmatch(requirement_id) is None:
            raise ObjectContractError(
                'INDEX_SCHEMA', 'requirement %d has an invalid ID' % position)
        feature_id = requirement_id.split('-AC', 1)[0]
        if requirement.get('feature_id') != feature_id:
            raise ObjectContractError(
                'OBJECT_MAPPING', '%s declares feature_id %r instead of %s'
                % (requirement_id, requirement.get('feature_id'), feature_id))
        if requirement.get('kind') != 'acceptance_criterion':
            raise ObjectContractError(
                'INDEX_SCHEMA', '%s has kind %r' % (requirement_id, requirement.get('kind')))
        digest = requirement.get('assertion_digest')
        if not isinstance(requirement.get('assertion'), str) or not requirement['assertion']:
            raise ObjectContractError('INDEX_SCHEMA', '%s has no assertion text' % requirement_id)
        if not isinstance(digest, str) or _DIGEST.match(digest) is None:
            raise ObjectContractError('INDEX_SCHEMA', '%s has an invalid assertion_digest' % requirement_id)
        if not isinstance(requirement.get('status'), str):
            raise ObjectContractError('INDEX_SCHEMA', '%s has no status' % requirement_id)

        uri = requirement.get('spec_uri')
        if not isinstance(uri, str) or not uri:
            raise ObjectContractError('INDEX_SCHEMA', '%s has no spec_uri' % requirement_id)
        parts = re.split(r'[\\/]', uri)
        if parts[:-1] != ['spec', 'baseline', 'features'] or not parts[-1]:
            raise ObjectContractError(
                'OBJECT_MAPPING',
                '%s has spec_uri %r outside spec/baseline/features' % (requirement_id, uri))
        name = parts[-1]
        real_name = aliases.get(name, name)
        document = by_name.get(real_name)
        if document is None:
            raise ObjectContractError(
                'UNKNOWN_OBJECT',
                '%s points to %r, which is not a discovered feature document' % (requirement_id, uri))
        candidates = expected_by_id.get(requirement_id, [])
        if not candidates:
            raise ObjectContractError(
                'UNEXPECTED_OBJECT',
                '%s is not an authored AC of the expected documents' % requirement_id)
        if all(item.document.name != document.name for item in candidates):
            raise ObjectContractError(
                'OBJECT_MAPPING',
                '%s maps to %s, but its expected document is %s'
                % (requirement_id, document.name,
                   ', '.join(sorted({item.document.name for item in candidates}))))
        actual_ids.append(requirement_id)
        normalized_uri = 'spec/baseline/features/' + document.name
        if normalized['requirements'][position]['spec_uri'] != normalized_uri:
            normalized['requirements'][position]['spec_uri'] = normalized_uri
            rewritten += 1

    duplicates = sorted(requirement_id for requirement_id, count in Counter(actual_ids).items()
                        if count > 1)
    meta_duplicates = meta.get('duplicate_ids') or []
    if duplicates or meta_duplicates:
        raise ObjectContractError(
            'DUPLICATE_AC_ID',
            'duplicate requirement identities: %s'
            % ', '.join(sorted(set(duplicates) | set(map(str, meta_duplicates)))))

    if sorted(expected_ids) != sorted(actual_ids):
        missing = sorted(Counter(expected_ids) - Counter(actual_ids))
        extra = sorted(Counter(actual_ids) - Counter(expected_ids))
        if expected_ids and not actual_ids:
            raise ObjectContractError(
                'ZERO_OBJECTS',
                'expected %d AC(s) from %d main document(s); index contains 0 requirements'
                % (len(expected_ids), len(discovery.mains)))
        raise ObjectContractError(
            'EXPECTED_COUNT_MISMATCH',
            'expected %d requirement(s) from %d main document(s), index has %d; '
            'missing=%s unexpected=%s'
            % (len(expected_ids), len(discovery.mains), len(actual_ids),
               missing or '-', extra or '-'))

    if meta.get('total') != len(requirements):
        raise ObjectContractError(
            'INDEX_META', '_meta.total=%r but requirements has %d entries'
            % (meta.get('total'), len(requirements)))
    active = sum(1 for item in requirements if item.get('status') == 'active')
    if meta.get('active') != active:
        raise ObjectContractError(
            'INDEX_META', '_meta.active=%r but %d entries are active' % (meta.get('active'), active))
    with_oracle = sum(1 for item in requirements if item.get('status') == 'active' and item.get('oracle') is not None)
    if meta.get('with_oracle') != with_oracle:
        raise ObjectContractError(
            'INDEX_META', '_meta.with_oracle=%r but %d entries have an oracle'
            % (meta.get('with_oracle'), with_oracle))
    with_truth = sum(1 for item in requirements if item.get('status') == 'active' and item.get('truth_source') is not None)
    if meta.get('with_truth_source') != with_truth:
        raise ObjectContractError(
            'INDEX_META', '_meta.with_truth_source=%r but %d entries have a truth source'
            % (meta.get('with_truth_source'), with_truth))

    return normalized, TraceabilityStats(
        requirements=len(requirements), documents=len(discovery.mains),
        aliased=len(aliases), rewritten_uris=rewritten)


def write_index(path: Path, payload) -> None:
    """Atomically publish the validated index using UTF-8 and platform newlines."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + '.', suffix='.tmp',
                                             dir=str(path.parent))
    try:
        with os.fdopen(descriptor, 'w', encoding='utf-8') as handle:
            handle.write(json.dumps(payload, ensure_ascii=False, indent=2) + '\n')
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise
