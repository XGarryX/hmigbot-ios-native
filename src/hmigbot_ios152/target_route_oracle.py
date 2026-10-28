"""Measure proved receiver-optional routes with the bundled original engine.

Only private copies lose the proved ``?`` bytes. No original graph field is
guessed from SDK syntax, and any unexplained batch difference stays unknown.
"""
from __future__ import annotations

from collections import Counter
import copy
import hashlib
import json
from pathlib import Path
import platform
import re
import tempfile

from hmigbot_ios.core import MigrationError
from .route_engine import compiled


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode('utf-8')


def engine_scripts(root):
    package = Path(__file__).resolve().parents[2] / 'skills/arkts-router-verify/scripts'
    return package if package.is_dir() else Path(root) / '.agents/skills/arkts-router-verify/scripts'


def engine_files(scripts):
    system = {'Darwin': 'macos', 'Linux': 'linux', 'Windows': 'windows'}[platform.system()]
    arch = 'arm64' if platform.machine().lower() in {'arm64', 'aarch64'} else 'x64'
    dist = Path(scripts) / 'bin' / (system + '-' + arch) / '_entry.dist'
    if not dist.is_dir():
        raise MigrationError('Missing original route engine: ' + str(dist))
    return {str(p.resolve()): sha(p.read_bytes()) for p in sorted(dist.rglob('*')) if p.is_file()}


def _root_wire(raw):
    matches = list(re.finditer(rb'^  "hmos_root"\s*:\s*("(?:[^"\\]|\\.)*")', raw, flags=re.M))
    if len(matches) != 1:
        raise ValueError('Original hmos_root wire cannot be located uniquely')
    return matches[0][1]


def _normalise(raw, root_wire):
    """Replace only the known top-level hmos_root JSON value, preserving wire."""
    data = json.loads(raw)
    old = data.get('hmos_root')
    if not isinstance(old, str):
        raise ValueError('Original graph has no hmos_root')
    pattern = rb'(^  "hmos_root"\s*:\s*)"(?:[^"\\]|\\.)*"'
    result, count = re.subn(pattern, lambda m: m[1] + root_wire, raw, flags=re.M)
    if count != 1:
        raise ValueError('Original hmos_root wire cannot be normalised uniquely')
    return result


def _measure(scripts, root, out, argv=()):
    passthrough, skip = [], False
    for value in argv:
        if skip:
            skip = False
        elif value in {'--hmos-root', '--out-dir'}:
            skip = True
        elif not value.startswith(('--hmos-root=', '--out-dir=')):
            passthrough.append(value)
    result = compiled(scripts, 'hmos_extract', [*passthrough, '--hmos-root', str(root), '--out-dir', str(out)],
                      {'ROUTE_VERIFY_ROOT': str(root), 'ROUTE_VERIFY_OUT': str(out)})
    path = out / 'actual_nav.json'
    if result.returncode or not path.is_file():
        raise MigrationError('Original optional-route measurement failed: ' + result.stdout[-1500:] + result.stderr[-1500:])
    return path.read_bytes()


def _tokens(records):
    selected, rejected, tokens = [], [], {}
    for record in records:
        values = record.get('optional_tokens') or [record.get('optional_token')]
        if not values or any(not token or token.get('placement') != 'receiver' for token in values):
            rejected.append({'reason': 'optional_call_or_missing_receiver_token_not_supplemented', 'candidate': record})
            continue
        selected.append(record)
        for token in values:
            key = token['file'], token['start_utf16'], token['end_utf16']
            if key in tokens and tokens[key] != token:
                raise ValueError('Conflicting optional token proof')
            tokens[key] = token
    return selected, rejected, list(tokens.values())


def _apply_tokens(root, mirror, tokens, inputs):
    by_file = {}
    for token in tokens:
        name = token['file']
        if name not in inputs or inputs[name] != token['file_sha256']:
            raise ValueError('Optional token is outside fresh target inputs')
        by_file.setdefault(name, []).append(token)
    for name, values in by_file.items():
        raw = (root / name).read_bytes()
        if sha(raw) != inputs[name]:
            raise ValueError('Optional token source changed')
        text = raw.decode('utf-8').encode('utf-16-le')
        for token in sorted(values, key=lambda t: t['start_utf16'], reverse=True):
            start, end = token['start_utf16'] * 2, token['end_utf16'] * 2
            if token.get('token_text') != '?.' or text[start:end] != '?.'.encode('utf-16-le'):
                raise ValueError('Optional token span does not contain receiver ?.')
            text = text[:start] + text[start + 2:]
        changed = text.decode('utf-16-le').encode('utf-8')
        if changed.count(b'\n') != raw.count(b'\n') or changed.count(b'\r') != raw.count(b'\r'):
            raise ValueError('Optional token change altered source lines')
        (mirror / name).write_bytes(changed)


def _anchors(record):
    sites = [record.get(key, {}) for key in ('control_site', 'onclick_binding', 'call_site', 'push_call_site')]
    sites += [site for site in record.get('chain', []) if site.get('kind') in
              {'onclick-binding', 'event-method-call', 'event-parameter-invoke', 'navpath-push', 'optional-navpath-push'}]
    result = {(site.get('file'), site.get('line')) for site in sites}
    for witness in record.get('instance_witnesses', []):
        result.update(_anchors(witness))
    return result


def _stats_delta(before, after):
    delta = {}
    for key in before.keys() | after.keys():
        left, right = before.get(key, 0), after.get(key, 0)
        if isinstance(right, dict) and key not in before:
            left = {}
        if left == right:
            continue
        if key == 'distinct_target_pages' and isinstance(left, list) and isinstance(right, list):
            if not set(left).issubset(right):
                raise ValueError('Original stats lost a target')
            delta[key] = sorted(set(right) - set(left))
        elif isinstance(left, dict) and isinstance(right, dict):
            delta[key] = _stats_delta(left, right)
        elif type(left) in (int, float) and type(right) in (int, float):
            delta[key] = right - left
        else:
            raise ValueError('Unexplained original stats change: ' + key)
    return delta


def _add_stats(target, delta):
    for key, value in delta.items():
        if isinstance(value, dict):
            _add_stats(target.setdefault(key, {}), value)
        elif key == 'distinct_target_pages':
            target[key] = sorted(set(target.get(key, [])) | set(value))
        else:
            target[key] = target.get(key, 0) + value


def optional_delta(root, original, actual, records, inputs, scripts=None, original_bytes=None, engine_argv=()):
    """Return measured graph/added edges/evidence/conflicts, all-or-none."""
    evidence = {'method': 'original engine counterfactual measurement plus official ETS proof',
                'normalisation': 'only top-level hmos_root; no other graph fields normalised',
                'status': 'not_needed'}
    try:
        selected, rejected, tokens = _tokens(records)
        evidence['tokens'] = tokens
        if not tokens:
            return actual, [], evidence, rejected
        scripts = Path(scripts or engine_scripts(root))
        evidence['status'] = 'incomplete'
        with tempfile.TemporaryDirectory(prefix='hmigbot-target-original-oracle-') as temporary:
            base = Path(temporary)
            mirror = base / 'project'
            (mirror / '.agents').mkdir(parents=True)
            for name, expected in inputs.items():
                raw = (root / name).read_bytes()
                if sha(raw) != expected:
                    raise ValueError('Target changed before mirror copy: ' + name)
                destination = mirror / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(raw)
            baseline_raw = _measure(scripts, mirror, base / 'baseline', engine_argv)
            root_wire = _root_wire(original_bytes) if original_bytes is not None else json.dumps(original['hmos_root']).encode('utf-8')
            baseline_normalised = _normalise(baseline_raw, root_wire)
            evidence.update({'baseline_raw_sha256': sha(baseline_raw),
                             'mirror_root': str(mirror), 'normalised_field': 'hmos_root',
                             'original_engine_arguments': list(engine_argv),
                             'baseline_normalised_sha256': sha(baseline_normalised),
                             'real_raw_sha256': sha(original_bytes) if original_bytes else None,
                             'baseline_basis': 'exact normalised bytes' if original_bytes else 'complete parsed graph'})
            if json.loads(baseline_normalised) != original or (original_bytes is not None and baseline_normalised != original_bytes):
                raise ValueError('Unmodified private mirror does not reproduce original graph')
            _apply_tokens(root, mirror, tokens, inputs)
            changed_raw = _measure(scripts, mirror, base / 'modified', engine_argv)
            evidence['modified_raw_sha256'] = sha(changed_raw)
            changed = json.loads(_normalise(changed_raw, root_wire))
        baseline = original
        if {k: v for k, v in baseline.items() if k not in {'edges', 'pages', 'stats'}} != {
                k: v for k, v in changed.items() if k not in {'edges', 'pages', 'stats'}}:
            raise ValueError('Original counterfactual changed unrelated graph sections')
        old_edges = Counter(canonical(edge) for edge in baseline.get('edges', []))
        new_edges = Counter(canonical(edge) for edge in changed.get('edges', []))
        if old_edges - new_edges:
            raise ValueError('Original counterfactual removed or changed existing edges')
        remaining = new_edges - old_edges
        added = []
        used = set()
        for edge in changed.get('edges', []):
            key = canonical(edge)
            if not remaining[key]:
                continue
            remaining[key] -= 1
            witnesses = [(i, record) for i, record in enumerate(selected) if
                edge.get('source') == record['source'] and edge.get('source_file') == record['source_file']
                and edge.get('target') is not None and edge.get('target') in {record['target'], record.get('registration', {}).get('target')} and edge.get('via') == 'navigation'
                and edge.get('target_type') == 'page' and (edge.get('source_file'), edge.get('line')) in _anchors(record)]
            if not witnesses:
                raise ValueError('Original counterfactual edge has no proved event/push anchor')
            pushes = {(r['source_file'], (r.get('push_call_site') or r.get('call_site', {})).get('start_utf16')) for _, r in witnesses}
            if len(pushes) != 1:
                raise ValueError('Original counterfactual edge ambiguously matches different pushes')
            used.update(i for i, _ in witnesses)
            added.append({**edge, 'supplement': 'ets_ast', 'native_provenance': {
                **copy.deepcopy(witnesses[0][1]), 'measurement_method': evidence['method'],
                'target_match': 'push_literal' if edge.get('target') == witnesses[0][1]['target'] else 'registered_component',
                'all_proof_witnesses': [record for _, record in witnesses]}})
        if used != set(range(len(selected))) or not added:
            raise ValueError('Proved optional chain did not yield an attributable original edge')
        result = copy.deepcopy(actual)
        old_pages, new_pages = baseline.get('pages', {}), changed.get('pages', {})
        if old_pages.keys() != new_pages.keys():
            raise ValueError('Original counterfactual changed page inventory')
        control_changes = []
        for name, old_page in old_pages.items():
            new_page = new_pages[name]
            if {k: v for k, v in old_page.items() if k != 'controls'} != {k: v for k, v in new_page.items() if k != 'controls'}:
                raise ValueError('Original counterfactual changed page metadata')
            controls, new_controls = old_page.get('controls', []), new_page.get('controls', [])
            if len(controls) != len(new_controls):
                raise ValueError('Original counterfactual changed control inventory')
            for index, (old, new) in enumerate(zip(controls, new_controls)):
                if old == new:
                    continue
                if {k: v for k, v in old.items() if k not in {'bound', 'navs'}} != {k: v for k, v in new.items() if k not in {'bound', 'navs'}}:
                    raise ValueError('Original counterfactual changed control identity')
                old_navs = Counter(canonical(nav) for nav in old.get('navs', []))
                new_navs = Counter(canonical(nav) for nav in new.get('navs', []))
                if old_navs - new_navs or new.get('bound') is not True:
                    raise ValueError('Original counterfactual removed a control binding')
                if not new_navs - old_navs:
                    raise ValueError('Original control change has no new navigation evidence')
                for raw in (new_navs - old_navs):
                    nav = json.loads(raw)
                    if not any(edge.get('source') == name and edge.get('line') == new.get('line') and
                               all(edge.get(k) == value for k, value in nav.items()) for edge in added):
                        raise ValueError('Original control change has no measured edge')
                if result['pages'][name]['controls'][index] != old:
                    raise ValueError('Another supplement already changed this original control')
                result['pages'][name]['controls'][index] = {**copy.deepcopy(new),
                    'supplement': 'ets_ast', 'original_engine_control': copy.deepcopy(old)}
                control_changes.append({'page': name, 'index': index, 'before': old, 'after': new})
        delta = _stats_delta(baseline.get('stats', {}), changed.get('stats', {}))
        _add_stats(result.setdefault('stats', {}), delta)
        result.setdefault('edges', []).extend(added)
        evidence.update({'status': 'complete', 'measured_added_edges': [edge for edge in changed.get('edges', [])
                         if canonical(edge) in (new_edges - old_edges)], 'control_changes': control_changes, 'stats_delta': delta})
        return result, added, evidence, rejected
    except ValueError as exc:
        evidence.update({'status': 'merge_unknown', 'reason': str(exc)})
        return actual, [], evidence, [{'reason': str(exc), 'method': evidence['method']}]
