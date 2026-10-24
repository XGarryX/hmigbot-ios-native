"""Validate native indexes around the unchanged original writeback program.

This adapter never writes an index, brief, claims ledger or control ledger. The
bundled helper remains the sole writer. A zero exit containing warnings is a
failure, as is a readback that changes anything beyond the requested cells.
"""
from __future__ import annotations

import argparse
import copy
from pathlib import Path
import re
import subprocess
import sys

from .artifact_contract import markdown_sections, markdown_tables
from .core import MigrationError, io_path, read_json, safe_child
from .plan_contract import _core_index_tables, structural_digest

UI = 'spec/baseline/ui-manifest.md'
FEATURE = 'spec/baseline/feature-index.md'
REGISTRY = 'spec/placeholder-registry.md'
CLAIMS = 'spec/.a2h/impl-claims.json'


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
    if relative == UI and table['authored_headers'][0] != '序号':
        raise MigrationError('UI writeback requires authored header 序号 with stable page_#### values; '
                             'review the upstream header migration and replan before execution. '
                             'The adapter never rewrites an active frozen header.')
    return text, rows


def _registry(project):
    raw = _read(project, REGISTRY)
    if raw is None:
        raise MigrationError('Registry missing: ' + REGISTRY)
    text = raw.decode('utf-8-sig')
    headings = markdown_sections(text)
    tables = []
    for table in markdown_tables(text):
        prior = [item for item in headings if item['line'] < table['line']]
        if prior and prior[-1]['title'] == '注册表' and table['headers'] == [
                'P-ID', 'location', 'trigger_condition', 'status', 'kind', 'resolve_by']:
            tables.append(table)
    if len(tables) != 1:
        raise MigrationError('Registry requires one complete native 注册表 table')
    table, rows = tables[0], {}
    for cells in table['rows']:
        if (len(cells) != len(table['headers']) or any(not cell for cell in cells)
                or not re.fullmatch(r'P-[A-Za-z0-9_-]+', cells[0]) or cells[0] in rows):
            raise MigrationError('Invalid, incomplete or duplicate registry ID')
        rows[cells[0]] = dict(zip(table['headers'], cells))
    # Removing just data rows pins the complete surrounding text and headers.
    lines = text.splitlines()
    row_lines = set(table['row_lines'])
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
            ('feature_index', FEATURE, ('implemented',), {'pending', 'implemented', 'verified'})):
        if key not in manifest:
            continue
        operations = _object(manifest[key], desired_states, key)
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
                if rows[identity]['状态'] == 'verified' and state != 'verified':
                    raise MigrationError(key + ': refusing progress downgrade for ' + identity)
                expected[identity]['状态'] = state
        checks.append(('index', relative, structural_digest(text, artifact=relative), expected))
        touched.add(relative)
    if 'registry' in manifest:
        operations = _object(manifest['registry'], ('resolve', 'retag'), 'registry')
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
        checks.append(('registry', REGISTRY, structure, expected))
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
        elif kind == 'registry':
            actual_structure, rows = _registry(project)
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
        from .portable_helper import run
        result = run(helper, [str(Path(args.manifest).resolve()),
                     '--project-root', str(project), *(['--dry-run'] if args.dry_run else [])], capture_output=True)
        _emit(sys.stdout, result.stdout)
        _emit(sys.stderr, result.stderr)
        if result.returncode:
            return result.returncode
        summaries = re.findall(rb'(?m)^(?:DRY-RUN )?apply_writeback:\s*(\d+) applied / (\d+) no-op / (\d+) warn\s*$',
                               result.stdout)
        if len(summaries) != 1 or int(summaries[0][2]):
            raise MigrationError('Original writeback emitted warnings or no unambiguous result; '
                                 'inspect preserved helper output, do not count this as complete')
        postflight(project, checks, before, touched, dry=args.dry_run)
        return 0
    except (MigrationError, OSError, UnicodeError, ValueError, TypeError) as exc:
        print('Native writeback rejected: ' + str(exc), file=sys.stderr)
        return 2
