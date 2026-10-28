"""Bind native indexed observations to the retained walk-inheritance contract.

The original core owns inheritance and retap decisions. These functions only
prepare its disposable input and restore collector identity on its output.
"""
from __future__ import annotations

from collections import Counter
import copy
from pathlib import Path

from hmigbot_ios.core import MigrationError, read_json, write_json


def prepare_inputs(edgewalk, destination, guard, argv):
    from . import native_canonical as C
    from .native_visual import functional_snapshot

    edgewalk, destination = Path(edgewalk), Path(destination)
    metadata, legacy_nodes = [], []
    for path in sorted((edgewalk / 'grounding').glob('*/run_meta.json')):
        value = read_json(path)
        if value.get('functional_checks_sha256'):
            metadata.append((path, value))
        else:
            legacy_nodes.append(value.get('node', path.parent.name))
    if not metadata:
        return {}, None  # Keep the original unindexed/legacy path unchanged.

    plan_path = edgewalk / 'walk_plan.json'
    guard.add(plan_path)
    plan = read_json(plan_path)
    tree_path = Path(plan.get('tree') or C._project_for(argv) / 'spec/toolkit-fact-tree.json')
    if not tree_path.is_absolute():
        tree_path = C._project_for(argv) / tree_path
    guard.add(tree_path)
    tree = read_json(tree_path)
    plan_identity = {'path': str(plan_path), 'sha256': C.sha(plan_path),
                     'tree_path': str(tree_path), 'tree_sha256': C.sha(tree_path),
                     'declared_fingerprints': {key: plan[key] for key in
                         ('tree_sha256', 'native_source_sha256', 'source_sha256') if key in plan},
                     'freshness': 'Current collector/check binding and call input guard only; '
                                  'optional plan fingerprint semantics are not established or checked'}
    source = tree.get('source', {})
    if not isinstance(source, dict):
        raise MigrationError('Indexed inheritance fact-tree source requires an object')
    source_fingerprint = tree.get('native_source_sha256') or source.get('source_sha256')
    records = list(C.page_records(tree))
    pages = {p['id']: p for p in records}
    if len(pages) != len(records):
        raise MigrationError('Indexed inheritance needs unique source node identities')
    bindings, mapped, unresolved = {}, [], []

    for path, meta in metadata:
        node = meta.get('node', path.parent.name)
        if node != path.parent.name:
            raise MigrationError('Indexed inheritance node does not match its collector directory')
        if meta.get('source_sha256') is not None and meta['source_sha256'] != source_fingerprint:
            raise MigrationError('Indexed inheritance observation source fingerprint is stale')
        page = pages.get(node)
        fingerprint = meta['functional_checks_sha256']
        if page is None or fingerprint != functional_snapshot(page):
            raise MigrationError('Indexed inheritance collector snapshot is stale: ' + str(node))
        checks = page.get('functional_checks', [])
        names = [c.get('name', c.get('check_name')) for c in checks]
        counts = Counter(names)
        seen = set()
        staged_path = destination / path.relative_to(edgewalk)
        staged = read_json(staged_path)
        if not isinstance(meta.get('checks'), list):
            raise MigrationError('Indexed inheritance collector checks require the original row list')
        for row in meta.get('checks', []):
            idx = row.get('idx')
            if type(idx) is not int or not 0 <= idx < len(checks) or idx in seen:
                raise MigrationError('Invalid indexed inheritance collector index: ' + str(node))
            seen.add(idx)
            check = checks[idx]
            name = check.get('name', check.get('check_name'))
            feature = check.get('feature_path')
            if (not feature or row.get('name') != name or row.get('check_idx') != idx
                    or row.get('check_name') != name or row.get('feature_path') != feature
                    or row.get('functional_checks_sha256') != fingerprint):
                raise MigrationError('Indexed inheritance collector identity mismatch: ' + str(node))
            key = (node, idx, name)
            if key in bindings:
                raise MigrationError('Duplicate indexed inheritance collector identity')
            bindings[key] = {'feature_path': feature, 'functional_checks_sha256': fingerprint}
            status = row.get('status')
            if status not in {'deferred_to_walk', 'deferred_same_destination'}:
                continue
            evidence = row.get('walk_evidence') or {}
            if not isinstance(evidence, dict):
                raise MigrationError('Indexed inheritance walk evidence requires an object')
            explicit = row.get('inherit_from_edge')
            if (isinstance(explicit, dict) and explicit.get('trigger') is not None
                    and not isinstance(explicit['trigger'], str)):
                raise MigrationError('Invalid original inheritance trigger value')
            valid_explicit = (isinstance(explicit, dict) and explicit.get('from') == node
                              and isinstance(explicit.get('to'), str) and bool(explicit['to']))
            matches = [r for r in staged.get('checks', []) if r.get('idx') == idx]
            if len(matches) != 1:
                raise MigrationError('Disposable inheritance collector row is ambiguous')
            candidates = []
            for walk in plan.get('walks', []):
                if evidence.get('walk_id') and walk.get('walk_id') != evidence['walk_id']:
                    continue
                for step in walk.get('steps', []):
                    if evidence.get('step') is not None and step.get('step') != evidence['step']:
                        continue
                    if (step.get('action') != 'tap' or step.get('from') != node
                            or name not in step.get('settles_grounding', [])):
                        continue
                    if explicit is not None and (not valid_explicit
                            or explicit.get('from') != node or explicit.get('to') != step.get('to')):
                        continue
                    candidates.append(step)
            # A navigation disposition alone does not establish same destination.
            hinted = (isinstance(evidence, dict) and isinstance(evidence.get('walk_id'), str)
                      and type(evidence.get('step')) is int)
            if (counts[name] != 1 or len(candidates) != 1
                    or status != 'deferred_same_destination' and not hinted
                    or status == 'deferred_same_destination' and not valid_explicit):
                unresolved.append({'node': node, 'check_idx': idx, 'check_name': name,
                                   'reason': 'No unique current-plan binding; original grounding debt retained'})
                # An unbound explicit declaration must not reach the original
                # core as if its source/check association had been verified.
                if status == 'deferred_same_destination':
                    matches[0]['status'] = 'deferred_to_walk'
                    matches[0].pop('inherit_from_edge', None)
                continue
            step = candidates[0]
            inherit = copy.deepcopy(explicit) if explicit is not None else {
                'from': node, 'to': step['to'], 'trigger': step.get('trigger')}
            if inherit.get('trigger') is not None and not isinstance(inherit['trigger'], str):
                raise MigrationError('Invalid original inheritance trigger value')
            matches[0].update(status='deferred_same_destination', inherit_from_edge=inherit)
            mapped.append({'node': node, 'check_idx': idx, 'check_name': name,
                           'inherit_from_edge': inherit, 'walk_evidence': evidence})
        write_json(staged_path, staged)

    trip = C._option(argv, '--device-state')
    excluded = []
    edges_path = destination / 'edge_results.json'
    if edges_path.is_file():
        edges = read_json(edges_path)
        if not isinstance(edges, list):
            raise MigrationError('Indexed inheritance edges require the original row list')
        if any(not isinstance(edge, dict) for edge in edges):
            raise MigrationError('Indexed inheritance edge rows require objects')
        if any(edge.get('device_state') is not None and not isinstance(edge['device_state'], str) for edge in edges):
            raise MigrationError('Inheritance edge device_state must be a string or absent')
        states = {edge.get('device_state') for edge in edges}
        if not trip and (len(states) > 1 or None in states):
            raise MigrationError('Indexed mixed/unknown-trip inheritance needs explicit --device-state')
        selected = []
        for idx, edge in enumerate(edges):
            if not isinstance(edge, dict):
                raise MigrationError('Indexed inheritance edge rows require objects')
            if not trip or edge.get('device_state') == trip:
                selected.append(edge)
            else:
                excluded.append({'index': idx, 'device_state': edge.get('device_state'),
                                 'from': edge.get('from'), 'to': edge.get('to')})
        write_json(edges_path, selected)
    return bindings, {'source_platform': 'ios', 'producer': 'native-indexed-inheritance/1',
                      'trip': trip, 'mapped': mapped, 'unresolved': unresolved,
                      'indexed_nodes': [m.get('node', p.parent.name) for p, m in metadata],
                      'legacy_nodes': legacy_nodes, 'trip_scope': 'whole directory, including legacy nodes',
                      'plan_identity': plan_identity,
                      'excluded_edges': excluded,
                      'inputs': {str(p): h for p, h in guard.files.items()},
                      'note': 'Original core decides inheritance/retap. Indexed trip input is scoped; '
                              'this deliberately tightens the original unfiltered mixed-trip behavior. '
                              'Canonical edges and raw observations are retained unchanged.'}


def bind_results(rows, bindings, receipt, prior_rows):
    mapped = {(r['node'], r['check_idx'], r['check_name']) for r in receipt['mapped']}
    remaining = list(prior_rows)
    for row in rows:
        if row.get('evidence_source') != 'inherited_from_edge':
            continue
        node = row.get('node')
        if node not in receipt['indexed_nodes']:
            continue
        idx = row.get('check_idx', row.get('idx'))
        key = (node, idx, row.get('check_name')) if type(idx) is int else None
        # The core retains existing rows on repeat calls. Preserve those rows
        # without upgrading their identity or trusting stale/legacy evidence.
        if row in remaining:
            remaining.remove(row)
            current = bindings.get(key)
            state = ('prior_unbound' if not current or not all(k in row for k in
                     ('feature_path', 'functional_checks_sha256')) else
                     'prior_valid' if all(row[k] == v for k, v in current.items()) else 'prior_stale')
            receipt.setdefault('prior_retained', []).append({
                'node': node, 'check_idx': idx, 'check_name': row.get('check_name'),
                'state': state, 'prior_retained_without_current_mapping': key not in mapped,
                'note': 'Unchanged prior row; no rebinding. Native writeback still checks current collector identity.'})
            continue
        if key not in bindings or key not in mapped:
            raise MigrationError('Inherited output does not match its indexed collector identity')
        for name, value in bindings[key].items():
            if name in row and row[name] != value:
                raise MigrationError('Inherited output collector binding conflicts with current input')
            row[name] = value
    return rows


def bind_retap(rows, bindings, receipt):
    mapped = {(r['node'], r['check_idx'], r['check_name']) for r in receipt['mapped']}
    for row in rows:
        if row.get('node') not in receipt['indexed_nodes']:
            continue
        def matching(keys):
            return [key for key in keys if key[0] == row.get('node')
                    and key[2] == row.get('check_name')
                    and ('check_idx' not in row or type(row['check_idx']) is int and row['check_idx'] == key[1])]
        candidates = matching(mapped)
        if not candidates:
            candidates = matching(bindings)
        if len(candidates) != 1:
            receipt.setdefault('unbound_retap', []).append({
                'row': copy.deepcopy(row), 'reason': 'No unique current collector identity; debt retained unchanged'})
            continue
        key = candidates[0]
        identity = {'check_idx': key[1], **bindings[key]}
        if any(name in row and row[name] != value for name, value in identity.items()):
            receipt.setdefault('unbound_retap', []).append({
                'row': copy.deepcopy(row), 'reason': 'Conflicting collector identity; debt retained unchanged'})
            continue
        row.update(identity)
    return rows
