"""Source-backed UI obligations and current task reference packets.

This adapter consumes reviewed iOS specifications and existing official capture
evidence. It does not infer Swift semantics, capture screens or prove behavior.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import re
import sys

from .core import MigrationError, digest, json_bytes, read_json, source_snapshot, write_json
from .receipt_outputs import regular_path

INVENTORY = 'spec/baseline/plans/ui-delivery.json'
PACKETS = 'spec/execution/ui-delivery/packets'
RECEIPTS = 'spec/execution/ui-delivery/receipts'
CONSUMED = 'spec/execution/ui-delivery/consumed'
TABLES = {'组件层级': 'component', '状态接口': 'state', '交互与导航': 'interaction'}


def require(ok, message):
    if not ok:
        raise MigrationError('UI delivery: ' + message)


def _context(project):
    project = Path(project).resolve()
    cfg_path = regular_path(project, '.migbot/config.json')
    cfg = read_json(cfg_path)
    require(cfg.get('source_platform') == 'ios' and isinstance(cfg.get('ios'), str), 'configured iOS source required')
    source = Path(cfg['ios'])
    source = (source if source.is_absolute() else project / source).resolve()
    return project, source, {'source_sha256': source_snapshot(source)['sha256'], 'config_sha256': digest(cfg_path.read_bytes())}


def _unit_id(page, kind, identity):
    return page + '.' + kind + '.' + digest(identity.encode())[:16]


def _spec_inventory(project, source, items):
    """Recompute the denominator from the actual reviewed Markdown core tables."""
    from .artifact_contract import markdown_sections, markdown_tables
    from .native_pipeline import source_paths
    pages = sorted({page for item in items.values() if item['scope'] == 'product' for page in item['page_ids']})
    units, inputs = [], {}
    for page_id in pages:
        matches = sorted((project / 'spec/baseline/ui').glob(page_id + '_*.md'))
        require(len(matches) == 1, 'expected one source specification for ' + page_id)
        path = regular_path(project, matches[0].relative_to(project).as_posix())
        raw = path.read_bytes(); text = raw.decode('utf-8-sig')
        relative = path.relative_to(project).as_posix(); inputs[relative] = digest(raw)
        anchors = source_paths(text)
        require(anchors, 'page has no source anchors: ' + page_id)
        for anchor in anchors:
            f = regular_path(source, anchor)
            require(f.is_file(), 'source anchor is missing: ' + anchor)
            inputs['source:' + anchor] = digest(f.read_bytes())
        owners = [ident for ident, item in items.items() if ident.startswith('UI:')
                  and item['scope'] == 'product' and page_id in item['page_ids']]
        require(len(owners) == 1, 'page must have one UI generating plan item: ' + page_id)
        owner = owners[0]
        require(items[owner]['ownership'], 'UI owner has no target output ownership: ' + owner)
        base = {'page_id': page_id, 'source_spec': relative, 'source_anchors': anchors,
                'generator': owner, 'assembler': owner, 'verifier': owner,
                'output_paths': sorted(items[owner]['ownership'])}
        units.append({**base, 'unit_id': _unit_id(page_id, 'page', page_id), 'kind': 'page',
                      'label': page_id, 'section': '页面与范围', 'requirements': {'page': page_id}})
        headings = markdown_sections(text)
        seen_nodes, seen_states = set(), set()
        counted = {title: 0 for title in TABLES}
        for table in markdown_tables(text):
            prior = [s for s in headings if s['line'] < table['line']]
            title = prior[-1]['title'] if prior else ''
            if title not in TABLES:
                continue
            for number, cells in enumerate(table['rows'], 1):
                counted[title] += 1
                require(len(cells) == len(table['headers']) and all(c.strip() for c in cells),
                        'incomplete ' + title + ' row in ' + relative)
                record = dict(zip(table['headers'], cells))
                kind = TABLES[title]
                identity = cells[0] if kind != 'interaction' else json.dumps(cells, ensure_ascii=False)
                if kind == 'component':
                    require(identity not in seen_nodes, 'duplicate component identity: ' + identity)
                    seen_nodes.add(identity)
                elif kind == 'state':
                    require(identity not in seen_states, 'duplicate state identity: ' + identity)
                    seen_states.add(identity)
                units.append({**base, 'unit_id': _unit_id(page_id, kind, identity), 'kind': kind,
                              'label': cells[0] if kind != 'interaction' else ' / '.join(cells[:2]),
                              'section': title, 'requirements': record})
        lines = text.splitlines()
        for title, count in counted.items():
            if count:
                continue
            section = next((h for h in headings if h['title'] == title), None)
            if section:
                later = [h['line'] for h in headings if h['line'] > section['line']]
                body = '\n'.join(lines[section['line']:min(later)-1 if later else len(lines)])
            else:
                body = ''
            require(re.search(r'\bnot_applicable\b\s*[:：]\s*\S+', body),
                    'source UI inventory is incomplete: ' + relative + ' / ' + title
                    + '; fill its real source-backed rows or an explicit not_applicable: reason')
        for unit in [u for u in units if u['page_id'] == page_id and u['kind'] == 'component']:
            parent = unit['requirements'].get('父节点')
            require(parent in (None, '-', '—') or parent in seen_nodes, 'component parent not in same page: ' + str(parent))
    require(len({u['unit_id'] for u in units}) == len(units), 'duplicate UI obligation identity')
    return units, inputs


def draft(project, *, apply=False, items=None):
    project, source, binding = _context(project)
    if items is None:
        from .plan_contract import plan_units
        _, items = plan_units(project, check_ui_delivery=False)
    units, inputs = _spec_inventory(project, source, items)
    value = {'schema_version': 1, **binding, 'spec_inputs': inputs, 'units': units,
             'reference_bindings': [], 'target_bindings': [], 'behavior_verified': False,
             'scope': 'reviewed source/spec obligations; source tables are not runtime observations'}
    path = regular_path(project, INVENTORY)
    if path.exists():
        old = read_json(path)
        require(all(old.get(k) == value[k] for k in ('schema_version', 'source_sha256', 'config_sha256', 'spec_inputs', 'units')),
                'existing inventory changed; retain prior evidence and review source/plan before a new draft')
        value = old
    elif apply and units:
        write_json(path, value)
    return {'status': 'not_applicable' if not units else 'ready' if apply else 'preview',
            'path': INVENTORY, 'inventory': value, 'applied': bool(apply and units)}


def validate_inventory(project, items, *, required=True):
    project, source, binding = _context(project)
    units, inputs = _spec_inventory(project, source, items)
    path = regular_path(project, INVENTORY)
    if not path.exists():
        require(not required or not units,
                'UI obligations need a source-derived inventory; run ui-delivery draft --project <target> --apply before plan-ir')
        return None
    value = read_json(path)
    require(type(value.get('schema_version')) is int and value['schema_version'] == 1, 'unsupported inventory schema')
    require(all(value.get(k) == expected for k, expected in {**binding, 'spec_inputs': inputs, 'units': units}.items()),
            'inventory omits/changes a current source obligation, source/config identity or task owner')
    refs = value.get('reference_bindings')
    require(isinstance(refs, list), 'reference_bindings must be a list')
    known = {u['unit_id']: u for u in units}; seen = set()
    targets = value.get('target_bindings')
    require(isinstance(targets, list), 'target_bindings must declare concrete target symbols during Plan')
    target_ids = set()
    for target in targets:
        require(isinstance(target, dict) and {'unit_id', 'path', 'symbol'} <= set(target)
                and not set(target) - {'unit_id', 'path', 'symbol', 'render_symbol'}
                and target['unit_id'] in known and target['unit_id'] not in target_ids
                and target['path'] in known[target['unit_id']]['output_paths']
                and Path(target['path']).suffix in {'.ets', '.ts'}
                and isinstance(target['symbol'], str) and target['symbol'].strip(), 'invalid, duplicate or unowned target binding')
        require('render_symbol' not in target or isinstance(target['render_symbol'], str)
                and re.fullmatch(r'[A-Za-z_$][A-Za-z0-9_$]*', target['render_symbol']), 'invalid explicit state render symbol')
        target_ids.add(target['unit_id'])
        unit = known[target['unit_id']]
        if unit['kind'] == 'state':
            spelling = unit['requirements'].get('目标 Owner.state 与类型', '').split(':', 1)[0]
            names = re.findall(r'[A-Za-z_$][A-Za-z0-9_$]*', spelling)
            claimed = re.findall(r'[A-Za-z_$][A-Za-z0-9_$]*', target['symbol'])
            require(names and claimed and names[-1] == claimed[-1], 'state target binding differs from its reviewed target state interface')
    require({u['unit_id'] for u in units if u['kind'] != 'page'} <= target_ids,
            'Plan must bind every component/state/interaction to its concrete owned target symbol; fill target_bindings before plan-ir')
    for ref in refs:
        require(isinstance(ref, dict) and set(ref) <= {'unit_id', 'checkpoint_id', 'region', 'required'}
                and ref.get('unit_id') in known and isinstance(ref.get('checkpoint_id'), str)
                and ref['checkpoint_id'] and type(ref.get('required', False)) is bool, 'invalid reference binding')
        key = (ref['unit_id'], ref['checkpoint_id'])
        require(key not in seen, 'duplicate unit/checkpoint reference')
        seen.add(key)
        region = ref.get('region')
        require(region is None or isinstance(region, list) and len(region) == 4
                and all(type(n) in (int, float) and math.isfinite(n) and n >= 0 for n in region)
                and region[2] > 0 and region[3] > 0, 'region must be [x,y,width,height] in source screenshot coordinates')
    return value


def _packet(project, source, value, page_id, observations):
    units = [u for u in value['units'] if u['page_id'] == page_id]
    require(units, 'unknown delivery page ' + page_id)
    inputs = {p: h for p, h in value['spec_inputs'].items() if p == units[0]['source_spec'] or p.startswith('source:')
              and p[7:] in units[0]['source_anchors']}
    captures = {o['checkpoint_id']: o for o in observations}
    materials, gaps = [], []
    for unit in units:
        refs = [r for r in value['reference_bindings'] if r['unit_id'] == unit['unit_id']]
        if not refs:
            gaps.append({'unit_id': unit['unit_id'], 'reason': 'no_state_region_reference', 'required': False})
        for ref in refs:
            observed = captures.get(ref['checkpoint_id'])
            if observed is None:
                gaps.append({'unit_id': unit['unit_id'], 'checkpoint_id': ref['checkpoint_id'],
                             'reason': 'selected_checkpoint_not_captured', 'required': ref.get('required', False)})
                continue
            if ref.get('region') is not None:
                from .ui_validation_evidence import _png_dimensions
                width, height = _png_dimensions(regular_path(project, observed['screenshot']['path']))
                x, y, w, h = ref['region']
                require(x + w <= width and y + h <= height, 'declared source region exceeds captured screenshot')
            material = {'unit_id': unit['unit_id'], 'checkpoint_id': ref['checkpoint_id'], 'region': ref.get('region'),
                        'captured_identity': observed['captured_identity'], 'screenshot': observed['screenshot'],
                        'hierarchy': observed['hierarchy'], 'configuration_gaps': observed.get('configuration_gaps', []),
                        'evidence_kind': 'native_observation'}
            materials.append(material)
            for kind in ('screenshot', 'hierarchy'):
                p, h = observed[kind]['path'], observed[kind]['sha256']
                require(digest(regular_path(project, p).read_bytes()) == h, 'captured input changed: ' + p)
                inputs[p] = h
    return {'schema_version': 1, 'page_id': page_id, 'source_sha256': value['source_sha256'],
            'config_sha256': value['config_sha256'], 'inventory_sha256': digest(json_bytes(value)),
            'generator': units[0]['generator'], 'units': units, 'inputs': inputs,
            'materials': materials, 'gaps': gaps, 'runtime_observed': bool(materials),
            'behavior_verified': False, 'image_review': 'author must inspect original pixels; reading bytes is not visual acceptance'}


def projection(project, source, items, observations):
    """Called by source_ui after its existing official-capture verification."""
    value = validate_inventory(project, items)
    if value is None:
        return {}, {}
    rows, files = {}, {}
    for page in sorted({u['page_id'] for u in value['units']}):
        packet = _packet(Path(project), Path(source), value, page, observations.get(page, []))
        path = PACKETS + '/' + page + '.json'
        raw = json_bytes(packet); files[path] = raw
        rows[page] = {'ui_delivery_packet': path, 'ui_delivery_packet_sha256': digest(raw),
                      'ui_delivery_unit_ids': [u['unit_id'] for u in packet['units']],
                      'ui_delivery_reference_gaps': packet['gaps']}
    return rows, files


def _consume(project, page_id, *, apply=True):
    """Read and validate full inputs before returning structured task material."""
    project, source, binding = _context(project)
    require(re.fullmatch(r'page_\d{4}', page_id), 'invalid page identity')
    path = regular_path(project, PACKETS + '/' + page_id + '.json')
    raw = path.read_bytes(); packet = read_json(path)
    require(all(packet.get(k) == v for k, v in binding.items()), 'packet source/config is stale')
    from .plan_contract import contract_revision
    contract = read_json(regular_path(project, 'spec/execution/execution-contract.json'))
    require(contract.get('source_sha256') == binding['source_sha256']
            and contract.get('contract_revision') == contract_revision(project)
            and contract.get('output_hashes', {}).get(path.relative_to(project).as_posix()) == digest(raw),
            'packet is not the current frozen execution output')
    inventory = read_json(regular_path(project, INVENTORY))
    require(contract.get('plan_inputs', {}).get(INVENTORY) == digest(regular_path(project, INVENTORY).read_bytes()),
            'UI inventory is not the frozen execution input')
    validate_inventory(project, contract['plan_items'])
    require(packet.get('inventory_sha256') == digest(json_bytes(inventory)), 'packet inventory changed')
    expected_units = [u for u in inventory['units'] if u['page_id'] == page_id]
    require(packet.get('units') == expected_units and expected_units, 'packet obligation set changed')
    require(not any(g.get('required') for g in packet['gaps']), 'required state reference is missing; resolve capture gap before generation')
    payloads, total = [], 0
    for relative, expected in sorted(packet['inputs'].items()):
        actual = regular_path(source, relative[7:]) if relative.startswith('source:') else regular_path(project, relative)
        data = actual.read_bytes(); total += len(data)
        require(digest(data) == expected, 'required input changed: ' + relative)
        if actual.suffix.lower() in {'.json', '.xml'}:
            if actual.suffix.lower() == '.json':
                value = read_json(actual)  # Parse the full hierarchy, never truncate JSON.
            else:
                from xml.etree import ElementTree
                root = ElementTree.fromstring(data)
                value = {'xml': data.decode('utf-8'), 'nodes': sum(1 for _ in root.iter())}
            payloads.append({'path': relative, 'content': value})
        elif actual.suffix.lower() not in {'.png', '.jpg', '.jpeg', '.webp'}:
            payloads.append({'path': relative, 'content': data.decode('utf-8-sig')})
    receipt = {'schema_version': 1, 'page_id': page_id, **binding, 'packet_sha256': digest(raw),
               'input_hashes': packet['inputs'], 'input_files': len(packet['inputs']), 'input_bytes': total,
               'unit_ids': [u['unit_id'] for u in expected_units], 'images_reviewed': False,
               'scope': 'actual file reads and full structural parsing; author pixel review and implementation remain separate'}
    if apply:
        write_json(regular_path(project, CONSUMED + '/' + page_id + '.json'), receipt)
    return {'status': 'consumed', 'receipt': receipt, 'packet': packet, 'structured_inputs': payloads,
            'image_inputs': [{'path': str(regular_path(project, m['screenshot']['path'])),
                              'sha256': m['screenshot']['sha256'], 'unit_id': m['unit_id'],
                              'checkpoint_id': m['checkpoint_id'], 'region': m['region']}
                             for m in packet['materials']]}


def consume(project, page_id, *, apply=True):
    """Record only actual material consumption; accounting cannot replace IO results."""
    from .execution_measurements import observe_start, observe_end
    token = None
    try:
        if apply:
            token = observe_start(project, 'execute', 'ui-reference-consume', category='input', metadata={'page_id': page_id})
    except (MigrationError, OSError, ValueError, KeyError, TypeError) as exc:
        print('UI reference measurement unavailable: ' + str(exc), file=sys.stderr)
    result = None
    try:
        result = _consume(project, page_id, apply=apply)
        return result
    finally:
        try:
            observe_end(project, token, 'passed' if result else 'failed', exit_code=0 if result else 2,
                        metadata=({'input_bytes': result['receipt']['input_bytes'],
                                   'input_files': result['receipt']['input_files']} if result else {}))
        except (MigrationError, OSError, ValueError, KeyError, TypeError) as exc:
            print('UI reference measurement completion unavailable: ' + str(exc), file=sys.stderr)


def verify_delivery(project, items, selected, *, phase='generated'):
    """Static delivery gate: all required units have current owned symbol outputs."""
    require(phase in {'generated', 'assembled'}, 'invalid static delivery phase')
    value = validate_inventory(project, items)
    if value is None:
        return {'status': 'not_applicable', 'units': 0, 'behavior_verified': False}
    selected = set(selected)
    wanted = [u for u in value['units'] if u['generator' if phase == 'generated' else 'assembler'] in selected]
    failures = []
    used_locations = {}
    bindings = {b['unit_id']: b for b in value['target_bindings']}
    for page in sorted({u['page_id'] for u in wanted}):
        actual_consumed = read_json(regular_path(project, CONSUMED + '/' + page + '.json'))
        consumed = consume(project, page, apply=False)['receipt']
        require(actual_consumed == consumed, 'missing/current task input consumption receipt: ' + page)
    for owner in sorted({u['generator' if phase == 'generated' else 'assembler'] for u in wanted}):
        path = regular_path(project, RECEIPTS + '/' + digest(owner.encode()) + '-' + phase + '.json')
        if not path.is_file():
            failures.append({'rule': 'IOS.UI_DELIVERY_RECEIPT', 'owner': owner, 'detail': 'missing ' + phase + ' receipt'}); continue
        receipt = read_json(path)
        require(receipt.get('inventory_sha256') == digest(json_bytes(value)) and receipt.get('owner') == owner
                and receipt.get('phase') == phase, 'stale or mismatched delivery receipt')
        entries = receipt.get('units')
        require(isinstance(entries, list) and all(isinstance(e, dict) and isinstance(e.get('unit_id'), str) for e in entries), 'invalid delivered units')
        require(len({e['unit_id'] for e in entries}) == len(entries), 'duplicate unit receipt')
        expected = {u['unit_id']: u for u in wanted if u['generator' if phase == 'generated' else 'assembler'] == owner}
        require(set(e['unit_id'] for e in entries) <= expected.keys(), 'receipt adds unowned UI obligations')
        for ident in sorted(expected):
            row = next((r for r in entries if r['unit_id'] == ident), None)
            if row is None:
                failures.append({'rule': 'IOS.UI_DELIVERY_MISSING', 'unit_id': ident, 'page_id': expected[ident]['page_id'],
                                 'owner': owner, 'detail': expected[ident]['label']}); continue
            outputs = row.get('outputs')
            require(isinstance(outputs, list) and outputs, 'unit needs actual output symbols')
            if expected[ident]['kind'] == 'state':
                require({o.get('role') for o in outputs} == {'state_definition', 'state_render'},
                        'state requires separate declaration and actual UI render-read anchors')
            for output in outputs:
                require(output.get('path') in expected[ident]['output_paths'], 'UI output outside frozen task ownership')
                if ident in bindings:
                    binding = bindings[ident]
                    require(output.get('path') == binding['path'] and output.get('symbol') == binding['symbol'],
                            'unit output differs from its Plan-frozen target symbol: ' + ident)
                require(Path(output['path']).suffix in {'.ets', '.ts'}, 'UI delivery needs actual target code, not prose or a done marker')
                data = regular_path(project, output['path']).read_bytes()
                line = output.get('line'); symbol = output.get('symbol')
                require(output.get('sha256') == digest(data) and type(line) is int and line > 0
                        and line <= len(data.decode('utf-8-sig').splitlines()) and isinstance(symbol, str) and symbol
                        and symbol in data.decode('utf-8-sig').splitlines()[line - 1], 'missing/stale output symbol for ' + ident)
                from .behavior import _target_tokens, _empty_target_handler, _target_pairs, _selected_handler_bodies
                tokens = _target_tokens(data.decode('utf-8-sig')); name = _target_tokens(symbol)
                require(name and not any(t.literal for t in name) and any(
                    [t.value for t in tokens[n:n + len(name)]] == [t.value for t in name]
                    and all(not t.literal and t.line == line for t in tokens[n:n + len(name)])
                    for n in range(len(tokens))), 'output symbol appears only in comments/literals or another line')
                require(not _empty_target_handler(data.decode('utf-8-sig'), symbol, line), 'empty output handler does not deliver a UI obligation')
                if expected[ident]['kind'] == 'state':
                    pairs = _target_pairs(tokens)
                    render_symbol = bindings[ident].get('render_symbol', 'build')
                    build_bodies = [b for n, t in enumerate(tokens) if t.value == render_symbol and not t.literal
                                    for b in _selected_handler_bodies(tokens, n, pairs)]
                    indices = [n for n, t in enumerate(tokens) if t.value == name[-1].value and not t.literal and t.line == line]
                    if output['role'] == 'state_definition':
                        require(any(n + 1 < len(tokens) and tokens[n+1].value == ':'
                                    and not any(b < n < pairs.get(b, b) for b in build_bodies) for n in indices),
                                'state declaration anchor is not a concrete target property')
                    else:
                        reads = [n for n in indices if any(b < n < pairs.get(b, b) for b in build_bodies)
                                 and n + 1 < len(tokens) and tokens[n+1].value not in {'=', '++', '--'}]
                        require(reads, 'state_render must reference the state from the actual build body')
                        empty_if = any(tokens[o-1].value == 'if' and o < n < c
                                       and c+1 < len(tokens) and tokens[c+1].value == '{' and pairs.get(c+1) == c+2
                                       for n in reads for o,c in pairs.items() if o > 0 and tokens[o].value == '(')
                        require(not empty_if, 'empty conditional body cannot deliver the required state UI')
                location = (output['path'], line, symbol)
                require(location not in used_locations or used_locations[location] == ident,
                        'different UI obligations cannot reuse one undifferentiated shell location: ' + ident)
                used_locations[location] = ident
    return {'status': 'FAIL' if failures else 'PASS', 'units': len(wanted), 'failures': failures,
            'inventory_sha256': digest(json_bytes(value)), 'behavior_verified': False,
            'scope': 'static unit/output completeness only; runtime/state behavior remains independent'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_subparsers(dest='action', required=True)
    for name in ('draft', 'check', 'consume', 'verify'):
        p = actions.add_parser(name); p.add_argument('--project', type=Path, required=True)
        if name == 'draft': p.add_argument('--apply', action='store_true')
        if name == 'consume': p.add_argument('--page', required=True)
        if name == 'verify':
            p.add_argument('--item', action='append', required=True)
            p.add_argument('--phase', choices=['generated', 'assembled'], default='generated')
    args = parser.parse_args(argv)
    args.command = 'ui-delivery-' + args.action
    progress_note = None
    if args.action == 'consume' or args.action == 'draft' and args.apply:
        from .project_progress import ProjectProgress
        progress_note = ProjectProgress(args)
        progress_note.record('running')
    try:
        if args.action == 'draft': result = draft(args.project, apply=args.apply)
        elif args.action == 'consume': result = consume(args.project, args.page)
        else:
            from .plan_contract import plan_units
            _, items = plan_units(args.project, check_ui_delivery=False)
            if args.action == 'check':
                value = validate_inventory(args.project, items)
                result = {'status': 'ready' if value else 'not_applicable', 'units': len(value['units']) if value else 0}
            else: result = verify_delivery(args.project, items, args.item, phase=args.phase)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if progress_note is not None:
            progress_note.record(result.get('status', 'returned'), result, exit_code=2 if result.get('status') == 'FAIL' else 0)
        return 2 if result.get('status') == 'FAIL' else 0
    except (MigrationError, OSError, ValueError, KeyError, TypeError) as exc:
        result = {'status': 'blocked', 'error': str(exc), 'recovery': 'retain current evidence; regenerate reviewed source/plan UI inventory or repair the exact missing unit/input'}
        if progress_note is not None:
            progress_note.record('blocked', result, exit_code=2)
        print(json.dumps(result, ensure_ascii=False))
        return 2
