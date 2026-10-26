"""Validate native indexes around the unchanged original writeback program.

This adapter never writes an index, brief, claims ledger or control ledger. The
bundled helper remains the sole writer. A zero exit containing warnings is a
failure, as is a readback that changes anything beyond the requested cells.
"""
from __future__ import annotations

import argparse
import copy
from contextlib import contextmanager
import platform
import types
from pathlib import Path
import re
import subprocess
import sys

from .artifact_contract import markdown_sections, markdown_tables
from .core import MigrationError, digest, io_path, read_json, safe_child
from .plan_contract import _core_index_tables, structural_digest

UI = 'spec/baseline/ui-manifest.md'
FEATURE = 'spec/baseline/feature-index.md'
REGISTRY = 'spec/placeholder-registry.md'
CLAIMS = 'spec/.a2h/impl-claims.json'

# Garry ios.32 open helpers; changed bytes require explicit reviewed adaptation.
HELPER_SHA256 = {'registry_table_format': '237a922df1d7434ed1478f23801cc8319bc88d2e5acf675bdfa47adb2dd344b5', 'feature_status_writeback': '09bb545ebae45e81901b0466edc03167055f534e87076cd913f2e0aabe3538fc'}


def _object(value, allowed, label):
    if not isinstance(value, dict) or set(value) - set(allowed):
        raise MigrationError(label + ': expected object with supported fields ' + ', '.join(allowed))
    return value


def _strings(value, label, pattern=None):
    if (not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value)
            or len(set(value)) != len(value)):
        raise MigrationError(label + ': expected unique nonempty string values')
    if pattern and any(not re.fullmatch(pattern, item) for item in value):
        raise MigrationError(label + ': invalid stable ID')
    return value


def _read(project, relative):
    path = safe_child(project, relative)
    return path.read_bytes() if path.is_file() else None


def _index(project, relative):
    raw = _read(project, relative)
    if raw is None:
        raise MigrationError('Required native index missing: ' + relative)
    text = raw.decode('utf-8-sig')
    tables = _core_index_tables(text, relative)
    if len(tables) != 1:
        raise MigrationError('Missing or ambiguous complete native core index: ' + relative)
    section, table = tables[0]
    key = section['progress']['id_column']
    column = table['headers'].index(key)
    rows = {}
    for row in table['rows']:
        if len(row) != len(table['headers']) or any(not cell for cell in row):
            raise MigrationError('Incomplete native core row: ' + relative)
        identity = row[column]
        if not re.fullmatch(section['progress']['id_pattern'], identity) or identity in rows:
            raise MigrationError('Invalid or duplicate native core ID: ' + relative)
        rows[identity] = dict(zip(table['headers'], row))
    if not rows:
        raise MigrationError('Empty native core index: ' + relative)
    if relative == UI and table['authored_headers'][table['headers'].index('状态')] != '状态':
        raise MigrationError('UI writeback requires authored status header 状态; review the header migration before the original writer')
    if relative == UI and table['authored_headers'][0] != '序号':
        raise MigrationError('UI writeback requires authored header 序号 with stable page_#### values; '
                             'review the upstream header migration and replan before execution. '
                             'The adapter never rewrites an active frozen header.')
    return text, rows


def _registry(project, *, raw=None, allow_groups=False):
    raw = _read(project, REGISTRY) if raw is None else raw
    if raw is None:
        raise MigrationError('Registry missing: ' + REGISTRY)
    text = raw.decode('utf-8-sig')
    headings = markdown_sections(text)
    tables = []
    for table in markdown_tables(text):
        prior = [item for item in headings if item['line'] < table['line']]
        if (allow_groups or prior and prior[-1]['title'] == '注册表') and table['headers'] == [
                'P-ID', 'location', 'trigger_condition', 'status', 'kind', 'resolve_by']:
            tables.append(table)
    if not tables or not allow_groups and len(tables) != 1:
        raise MigrationError('Registry requires one complete native 注册表 table (explicit header repair permits row groups)')
    table, rows = tables[0], {}
    for cells in [row for group in tables for row in group['rows']]:
        if (len(cells) != len(table['headers']) or any(not cell for cell in cells)
                or not re.fullmatch(r'P-[A-Za-z0-9_-]+', cells[0]) or cells[0] in rows):
            raise MigrationError('Invalid, incomplete or duplicate registry ID')
        rows[cells[0]] = dict(zip(table['headers'], cells))
    # Removing just data rows pins the complete surrounding text and headers.
    lines = text.splitlines()
    row_lines = {line for group in tables for line in group['row_lines']}
    structure = '\n'.join(line for number, line in enumerate(lines, 1) if number not in row_lines)
    return structure, rows


def _claim_identity(claim):
    if not isinstance(claim, dict):
        raise MigrationError('impl_claims.claims entries must be objects')
    for key in ('requirement_id', 'packet_id', 'requirement_digest'):
        if not isinstance(claim.get(key), str) or not claim[key]:
            raise MigrationError('impl_claims.claims missing ' + key)
    if type(claim.get('attempt')) is not int or claim['attempt'] < 1:
        raise MigrationError('impl_claims.claims attempt must be a positive integer')
    _strings(claim.get('files'), 'impl_claims.claims.files')
    if 'symbols' in claim:
        _strings(claim['symbols'], 'impl_claims.claims.symbols')
    return claim['requirement_id'], claim['packet_id'], claim['attempt']


def preflight(project, manifest):
    """Read-only validation and expected readbacks; reject before any helper IO."""
    _object(manifest, ('mode', 'id', 'ui_manifest', 'feature_index', 'registry', 'impl_claims', 'brief'), 'manifest')
    if 'mode' in manifest and manifest['mode'] not in ('batch', 'base', 'group', 'final'):
        raise MigrationError('Invalid writeback mode')
    if 'id' in manifest and (type(manifest['id']) not in (str, int) or not str(manifest['id'])):
        raise MigrationError('Invalid writeback id')
    checks, touched = [], set()
    for key, relative, desired_states, valid_states in (
            ('ui_manifest', UI, ('converted', 'verified'), {'pending', 'converted', 'verified'}),
            ('feature_index', FEATURE, ('implemented', 'verified'), {'pending', 'implemented', 'verified'})):
        if key not in manifest:
            continue
        operations = _object(manifest[key], desired_states, key)
        if key == 'feature_index' and 'verified' in operations:
            if manifest.get('mode') != 'final':
                raise MigrationError('feature_index.verified is a final-mode field')
            _plain_path(project, FEATURE)
            ident = manifest.get('id')
            if not isinstance(ident, str) or not ident.strip() or any(c in ident for c in '\r\n\0'):
                raise MigrationError('Final verified writeback requires a valid string id')
        for state, identities in operations.items():
            _strings(identities, key + '.' + state, r'page_[0-9]{4}' if relative == UI else r'F[0-9]+')
        if not any(operations.values()):
            continue
        text, rows = _index(project, relative)
        expected, seen = copy.deepcopy(rows), set()
        for state, identities in operations.items():
            for identity in _strings(identities, key + '.' + state,
                                     r'page_[0-9]{4}' if relative == UI else r'F[0-9]+'):
                if identity in seen or identity not in rows:
                    raise MigrationError(key + ': duplicate or unknown ID ' + identity)
                seen.add(identity)
                if rows[identity]['状态'] not in valid_states:
                    raise MigrationError(key + ': invalid source progress state for ' + identity)
                if key == 'feature_index' and state == 'verified' and rows[identity]['状态'] not in {'implemented','verified'}:
                    raise MigrationError('Feature must be implemented before final verification: ' + identity)
                if rows[identity]['状态'] == 'verified' and state != 'verified':
                    raise MigrationError(key + ': refusing progress downgrade for ' + identity)
                expected[identity]['状态'] = state
        checks.append(('index', relative, structural_digest(text, artifact=relative), expected))
        touched.add(relative)
    if 'registry' in manifest:
        operations = _object(manifest['registry'], ('resolve', 'retag', 'ensure_table_headers'), 'registry')
        if 'ensure_table_headers' in operations and type(operations['ensure_table_headers']) is not bool:
            raise MigrationError('registry.ensure_table_headers must be a boolean')
        formatting = operations.get('ensure_table_headers', False)
        if formatting:
            _plain_path(project, REGISTRY)
            with _helpers() as (formatter, _):
                formatted, _ = formatter.format_registry(_read(project, REGISTRY))
            structure, rows = _registry(project, raw=formatted, allow_groups=True)
        else:
            structure, rows = _registry(project)
        expected = copy.deepcopy(rows)
        for identity in _strings(operations.get('resolve', []), 'registry.resolve', r'P-[A-Za-z0-9_-]+'):
            if identity not in rows:
                # The original protocol defines this as a replay no-op after a
                # forward-ref row was deleted. Do not claim a new resolution,
                # invent tombstones or change that upstream behavior.
                continue
            if rows[identity]['kind'] == 'forward-ref':
                del expected[identity]
            else:
                expected[identity]['status'] = 'resolved'
        retags, seen = operations.get('retag', []), set()
        if not isinstance(retags, list):
            raise MigrationError('registry.retag must be an array')
        for item in retags:
            _object(item, ('pid', 'column', 'value'), 'registry.retag')
            identity, column, value = item.get('pid'), item.get('column'), item.get('value')
            if (not isinstance(identity, str) or identity not in expected or column not in rows[identity]
                    or column == 'P-ID' or not isinstance(value, str) or not value
                    or '\n' in value or '\r' in value or '|' in value or (identity, column) in seen):
                raise MigrationError('Invalid, duplicate or unknown registry retag')
            seen.add((identity, column))
            expected[identity][column] = value
        checks.append(('registry_formatted' if formatting else 'registry', REGISTRY, structure, expected))
        touched.add(REGISTRY)
    if 'impl_claims' in manifest:
        operations = _object(manifest['impl_claims'], ('claims', 'executed_packets'), 'impl_claims')
        path = safe_child(project, CLAIMS)
        ledger = read_json(path) if path.exists() else {'claims': [], 'executed_packets': []}
        if not isinstance(ledger, dict) or not isinstance(ledger.get('claims'), list):
            raise MigrationError('Malformed existing impl_claims ledger')
        packets = _strings(ledger.get('executed_packets'), 'existing executed_packets')
        indexed = {}
        for claim in ledger['claims']:
            identity = _claim_identity(claim)
            if identity in indexed:
                raise MigrationError('Duplicate existing claim identity')
            indexed[identity] = claim
        new_claims = operations.get('claims', [])
        if not isinstance(new_claims, list):
            raise MigrationError('impl_claims.claims must be an array')
        seen = set()
        for claim in new_claims:
            identity = _claim_identity(claim)
            if identity in seen:
                raise MigrationError('Duplicate requested claim identity')
            seen.add(identity)
            for relative in claim['files']:
                safe_child(project, relative)
            indexed[identity] = claim
        expected_packets = list(packets)
        for packet in _strings(operations.get('executed_packets', []), 'executed_packets'):
            if packet not in expected_packets:
                expected_packets.append(packet)
        checks.append(('claims', CLAIMS, list(indexed.values()), expected_packets))
        touched.add(CLAIMS)
    if 'brief' in manifest:
        brief = _object(manifest['brief'], ('path', 'content'), 'brief')
        relative, content = brief.get('path'), brief.get('content')
        if (not isinstance(relative, str) or not re.fullmatch(r'spec/execution/briefs/[A-Za-z0-9_-]+\.md', relative)
                or not isinstance(content, str)):
            raise MigrationError('brief requires a canonical execution brief path and string content')
        safe_child(project, relative)
        checks.append(('brief', relative, content, None))
        touched.add(relative)
    # Also bind canonical files not requested by this manifest: a helper bug
    # must not silently modify another index/ledger alongside a valid brief.
    before = {relative: _read(project, relative) for relative in touched | {UI, FEATURE, REGISTRY, CLAIMS}}
    return checks, before, touched


def postflight(project, checks, before, touched, *, dry=False):
    for relative, raw in before.items():
        if (dry or relative not in touched) and _read(project, relative) != raw:
            raise MigrationError('Unexpected writeback mutation: ' + relative)
    if dry:
        return
    for kind, relative, structure, expected in checks:
        if kind == 'index':
            text, rows = _index(project, relative)
            valid = structural_digest(text, artifact=relative) == structure and rows == expected
        elif kind in {'registry', 'registry_formatted'}:
            actual_structure, rows = _registry(project, allow_groups=kind == 'registry_formatted')
            valid = actual_structure == structure and rows == expected
        elif kind == 'claims':
            actual = read_json(safe_child(project, relative))
            valid = actual.get('claims') == structure and actual.get('executed_packets') == expected
        else:
            valid = safe_child(project, relative).read_text(encoding='utf-8-sig') == structure
        if not valid:
            raise MigrationError('Original writeback readback differs from requested changes: ' + relative)


def _emit(stream, content):
    if content:
        if hasattr(stream, 'buffer'):
            stream.buffer.write(content)
            stream.buffer.flush()
        else:
            stream.write(content.decode('utf-8', errors='replace'))


def _plain_path(project, relative):
    path = Path(project) / relative
    for part in (path, *path.parents):
        if part.is_symlink() or getattr(part, 'is_junction', lambda: False)():
            raise MigrationError('Writeback path cannot traverse links: ' + relative)
    return path


@contextmanager
def _helpers():
    """Load only the selected, bundled .32 helpers; never import project code."""
    folder = Path(__file__).resolve().parents[2] / 'vendor/hmigbot/skills/a2h-execute/scripts'
    saved = {name: sys.modules.get(name) for name in ('registry_table_format','feature_status_writeback')}
    loaded = []
    try:
        for name in saved:
            path = folder / (name + '.py')
            module = types.ModuleType(name);module.__file__ = str(path)
            sys.modules[name] = module
            raw = path.read_bytes()
            if digest(raw) != HELPER_SHA256[name]:
                raise MigrationError('Selected writeback helper changed: ' + name)
            exec(compile(raw, str(path), 'exec'), module.__dict__)
            loaded.append(module)
        yield tuple(loaded)
    finally:
        for name, module in saved.items():
            if module is None:sys.modules.pop(name,None)
            else:sys.modules[name] = module


def _extended(manifest):
    return ('verified' in manifest.get('feature_index', {})
            or manifest.get('registry', {}).get('ensure_table_headers') is True)


def validate_summary(stdout, manifest, *, dry=False):
    matches = re.findall(rb'(?m)^(DRY-RUN )?apply_writeback:\s*(\d+) applied / (\d+) no-op / (\d+) warn\s*$', stdout)
    expected = [True] if dry else [True, False] if 'verified' in manifest.get('feature_index', {}) else [False]
    if ([bool(row[0]) for row in matches] != expected or any(int(row[3]) for row in matches)):
        raise MigrationError('Original writeback emitted warnings or no unambiguous expected result sequence')


def run_helper(helper, argv, manifest, **kwargs):
    """Extended fields enter the same vendor chain; legacy uses original engine."""
    if _extended(manifest):
        return subprocess.run([sys.executable, '-B', str(helper), *map(str, argv)], **kwargs)
    from .portable_helper import run
    return run(helper, argv, **kwargs)


def chain_main(helper, argv):
    """Selected vendor launcher: .32 explicit adapters around one original engine."""
    if platform.system() != 'Darwin' or platform.machine().lower() not in {'arm64','aarch64'}:
        print('writeback platform deferred: selected payload is macos-arm64',file=sys.stderr)
        return 2
    parser=argparse.ArgumentParser(add_help=False)
    parser.add_argument('manifest',nargs='?');parser.add_argument('--project-root',default='.')
    args,_=parser.parse_known_args(argv)
    if args.manifest:
        request=read_json(Path(args.manifest))
        project=Path(args.project_root).resolve(strict=True)
        preflight(project,request) # Direct vendor calls keep the same local preflight.
        if 'verified' in request.get('feature_index',{}):_plain_path(project,FEATURE)
    from .portable_helper import run
    def original(arguments):
        result=run(helper,arguments,capture_output=True)
        _emit(sys.stdout,result.stdout);_emit(sys.stderr,result.stderr)
        if result.returncode:return result.returncode
        if '-h' in arguments or '--help' in arguments:return 0
        # Adapters never promote state after a warning-only native exit 0.
        validate_summary(result.stdout, {}, dry='--dry-run' in arguments)
        return 0
    try:
        with _helpers() as (formatter, features):
            def registry_chain(arguments):
                result=formatter.apply_if_requested(arguments,original)
                return original(arguments) if result is None else result
            result=features.apply_if_requested(argv,registry_chain)
            return registry_chain(argv) if result is None else result
    except (MigrationError,OSError,UnicodeError,ValueError,TypeError) as exc:
        print('Explicit writeback chain rejected: '+str(exc),file=sys.stderr)
        return 2


def main(argv=None, *, helper):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest')
    parser.add_argument('--project-root', default='.')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args(argv)
    try:
        project = io_path(Path(args.project_root)).resolve()
        manifest = read_json(Path(args.manifest))
        checks, before, touched = preflight(project, manifest)
        result = run_helper(helper, [str(Path(args.manifest).resolve()),
                     '--project-root', str(project), *(['--dry-run'] if args.dry_run else [])], manifest, capture_output=True)
        _emit(sys.stdout, result.stdout)
        _emit(sys.stderr, result.stderr)
        if result.returncode:
            return result.returncode
        validate_summary(result.stdout, manifest, dry=args.dry_run)
        postflight(project, checks, before, touched, dry=args.dry_run)
        return 0
    except (MigrationError, OSError, UnicodeError, ValueError, TypeError) as exc:
        print('Native writeback rejected: ' + str(exc), file=sys.stderr)
        return 2
