"""Canonical numeric input types for the original literal detector.

Native source extraction records JSON numbers and unresolved source units;
the bundled detector accepts numeric strings. Only a disposable ledger changes
that representation. Original source anchors, items, text/color decisions and
the original detector report remain available, without claiming unit coverage.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

from .core import io_path, snapshot, write_json
from .native_structural_evidence import product_source_roots, SKIP, TEST_PARTS
from .swiftui import tokenize
from .scheduler_windows_runtime import run as run_owned_process
from .runtime_timeouts import timeout_for, timeout_evidence

ROOT = Path(__file__).resolve().parents[2]
LEDGER = 'spec/baseline/literal-ledger.json'


def canonical_ledger(raw):
    """Return an item-preserving copy, changing only finite numeric values."""
    if not isinstance(raw, dict):
        raise ValueError('Literal ledger must be an object')
    result, changes = copy.deepcopy(raw), []
    for collection in ('dims', 'durations_ms'):
        values = result.get(collection, [])
        if not isinstance(values, list):
            raise ValueError('Literal numeric collection must be a list: ' + collection)
        for index, item in enumerate(values):
            if not isinstance(item, dict) or 'value' not in item:
                raise ValueError('Literal numeric item requires a value')
            value = item['value']
            if isinstance(value, str):
                continue
            if type(value) not in {int, float} or (type(value) is float and not math.isfinite(value)):
                raise ValueError('Literal numeric value must be a finite number or legacy string')
            item['value'] = json.dumps(value, allow_nan=False)
            changes.append({'collection': collection, 'index': index,
                            'original_value': value, 'canonical_value': item['value'],
                            'unit': item.get('unit'), 'sources': item.get('sources', [])})
    return result, changes


def _files(directory):
    if not directory.is_dir():
        return
    for parent, directories, names in os.walk(io_path(directory)):
        directories[:] = sorted(name for name in directories
            if name not in SKIP | TEST_PARTS and not name.startswith('.'))
        for name in sorted(names):
            path = io_path(Path(parent) / name).resolve()
            if not path.is_relative_to(directory):
                raise ValueError('Literal input escapes configured source directory')
            if path.is_file():
                yield path


def _inputs(project):
    roots = product_source_roots(project)
    paths = {}
    for root in roots:
        for path in _files(root):
            if path.suffix == '.ets':
                paths[path.relative_to(project).as_posix()] = path
        for path in _files(root.parent / 'resources'):
            paths[path.relative_to(project).as_posix()] = path
    for path in _files(project / 'AppScope/resources'):
        paths[path.relative_to(project).as_posix()] = path
    return paths


def _hash(raw):
    return hashlib.sha256(raw).hexdigest()


def _pairs(tokens):
    result, stack = {}, []
    closing = {')': '(', ']': '[', '}': '{'}
    for index, token in enumerate(tokens):
        if token.kind == 'string':
            continue
        if token.value in closing.values():
            stack.append((index, token.value))
        elif token.value in closing:
            if not stack or stack[-1][1] != closing[token.value]:
                raise ValueError('Unbalanced Swift literal source')
            begin, _ = stack.pop()
            result[begin] = index
    if stack:
        raise ValueError('Unbalanced Swift literal source')
    return result


def _call(tokens, pairs, position):
    openings = [index for index, end in pairs.items()
                if tokens[index].value == '(' and index < position < end and index]
    if not openings:
        return None
    opening = max(openings)
    start, cursor = opening + 1, opening + 1
    while cursor < position:
        if cursor in pairs and pairs[cursor] < position:
            cursor = pairs[cursor] + 1
            continue
        if tokens[cursor].value == ',':
            start = cursor + 1
        cursor += 1
    label = tokens[start].value if start + 1 < position and tokens[start + 1].value == ':' else None
    end, cursor = pairs[opening], position + 1
    while cursor < end:
        if cursor in pairs:
            cursor = pairs[cursor] + 1
            continue
        if tokens[cursor].value == ',':
            end = cursor
            break
        cursor += 1
    return {'callee': tokens[opening - 1].value, 'label': label,
            'argument': 0 if start == opening + 1 else 1,
            'argument_start': start + (2 if label else 0), 'argument_end': end,
            'prefix': [token.value for token in tokens[max(0, opening - 8):opening]],
            'pure_literal_argument': position == start + (2 if label else 0)}


def _literal_role(tokens, pairs, position, declared_names=(), source_name_counts=None):
    call = _call(tokens, pairs, position)
    if call and call['callee'] in {'Image', 'Label'} and call['label'] in {'systemName', 'systemImage'} and call['callee'] not in declared_names:
        start, end = call['argument_start'], call['argument_end']
        values = [token.value for token in tokens]
        questions = [i for i in range(start, end) if values[i] == '?']
        colons = [i for i in range(start, end) if values[i] == ':']
        if (len(questions) == len(colons) == 1 and questions[0] > start
                and colons[0] == questions[0] + 2 and end == colons[0] + 2
                and tokens[questions[0] + 1].kind == tokens[colons[0] + 1].kind == 'string'
                and position in {questions[0] + 1, colons[0] + 1}):
            return 'system_symbol_identifier', {**call, 'syntax': 'same named argument, two literal ternary branches'}
    if call and call['pure_literal_argument']:
        callee, label = call['callee'], call['label']
        if callee in declared_names:
            return 'ui_or_usage_unresolved', {'shadowed_callee': callee}
        if callee in {'Image', 'Label'} and label in {'systemName', 'systemImage'}:
            return 'system_symbol_identifier', call
        if callee == 'Color' and call['argument'] == 0 and label is None:
            return 'asset_color_identifier', call
        if callee == 'Image' and call['argument'] == 0 and label is None:
            return 'asset_image_identifier', call
        if callee == 'accessibilityIdentifier':
            return 'automation_identifier', call
        if (callee == 'object' and label == 'forInfoDictionaryKey'
                and call['prefix'][-5:] == ['Bundle', '.', 'main', '.', 'object']
                and 'Bundle' not in declared_names):
            return ('automation_identifier' if callee == 'accessibilityIdentifier' else 'bundle_metadata_key'), call
        if callee == 'url' and label in {'forResource', 'withExtension'} and call['prefix'][-5:] == ['Bundle', '.', 'main', '.', 'url']:
            return 'bundle_resource_identifier', call
        if callee == 'Name' and call['prefix'][-3:] == ['Notification', '.', 'Name']:
            return 'notification_identifier', call
        if callee == 'reloadTimelines' and label == 'ofKind' and call['prefix'][-5:] == ['WidgetCenter', '.', 'shared', '.', 'reloadTimelines'] and 'WidgetCenter' not in declared_names:
            return 'widget_configuration_identifier', call
        if callee == 'contains' and call['prefix'][-7:] == ['ProcessInfo', '.', 'processInfo', '.', 'arguments', '.', 'contains']:
            return 'process_argument_configuration', call
        if callee == 'fatalError':
            return 'diagnostic_trap_message', call
        if callee == 'String' and label == 'format':
            return 'runtime_format_template', call
    # A language list is platform configuration only when its receiver has a
    # unique real VNRecognizeTextRequest construction, rather than by value/name.
    values = [token.value for token in tokens]
    if (call and call['callee'] == 'value' and call['pure_literal_argument']
            and call['argument'] == 0 and call['prefix'][-4:] == ['x', ':', '.', 'value']
            and not {'Chart', 'LineMark', 'PointMark', 'value'} & set(declared_names)):
        for chart in range(len(values) - 2):
            if values[chart:chart + 2] != ['Chart', '('] or chart + 1 not in pairs:
                continue
            body = pairs[chart + 1] + 1
            if body not in pairs or values[body] != '{' or not body < position < pairs[body]:
                continue
            parent_calls = [opening for opening, end in pairs.items()
                if values[opening] == '(' and opening < position < end and opening
                and values[opening - 1] in {'LineMark', 'PointMark'}]
            if not parent_calls:
                continue
            cursor, hidden, aggregate, axis_count, label_count = pairs[body] + 1, None, None, 0, 0
            while cursor + 2 < len(values) and values[cursor] == '.' and values[cursor + 2] == '(' and cursor + 2 in pairs:
                end = pairs[cursor + 2]
                if values[cursor + 1] == 'chartXAxis':
                    axis_count += 1
                    hidden = tokens[cursor].line if values[cursor + 3:end] == ['.', 'hidden'] else None
                if values[cursor + 1] == 'accessibilityLabel':
                    label_count += 1
                    aggregate = ({'line': tokens[cursor].line, 'source_expression': tokens[cursor + 3].value}
                        if end == cursor + 4 and tokens[cursor + 3].kind == 'string' else None)
                cursor = end + 1
            if (hidden and aggregate and axis_count == label_count == 1
                    and not {'chartXAxis', 'accessibilityLabel'} & set(declared_names)):
                return 'hidden_chart_dimension_label', {'chart_line': tokens[chart].line,
                    'hidden_x_axis_line': hidden, 'aggregate_accessibility_label': aggregate,
                    'a11y_runtime_verified': False,
                    'scope': 'Hidden X dimension semantic name, not ordinary static Text; screen-reader equivalence remains unverified'}
    # A computed App Group identifier fallback is platform metadata only when
    # the unique binding has no other source use besides the actual FileManager
    # container lookup; a later Text(binding) would make this proof fail.
    for opening, closing in pairs.items():
        if not (tokens[opening].value == '{' and opening < position < closing and opening >= 4):
            continue
        if values[opening - 4:opening - 3] != ['var'] or values[opening - 2:opening] != [':', 'String']:
            continue
        name = values[opening - 3]
        body = values[opening + 1:closing]
        lookups = [i for i in range(len(values) - 9)
            if values[i:i + 10] == ['FileManager', '.', 'default', '.', 'containerURL', '(',
                                    'forSecurityApplicationGroupIdentifier', ':', name, ')']]
        if (len(lookups) == 1 and source_name_counts and source_name_counts.get(name) == 1
                and not {'Bundle', 'FileManager'} & set(declared_names)
                and body[:8] == ['Bundle', '.', 'main', '.', 'object', '(', 'forInfoDictionaryKey', ':']
                and position == closing - 1 and values[position - 2:position] == ['?', '?']):
            return 'app_group_configuration_fallback', {'binding': name,
                'container_lookup_line': tokens[lookups[0]].line,
                'source_binding_reads': source_name_counts[name]}
    line_start = position
    while line_start and tokens[line_start - 1].line == tokens[position].line:
        line_start -= 1
    prefix = values[line_start:position]
    for index in range(len(prefix) - 4):
        if prefix[index + 1:index + 5] == ['.', 'recognitionLanguages', '=', '[']:
            receiver = prefix[index]
            declarations = [i for i in range(len(values) - 5)
                if values[i:i + 6] == ['let', receiver, '=', 'VNRecognizeTextRequest', '(', ')']]
            bindings = [i for i in range(len(values) - 1)
                        if values[i] in {'let', 'var'} and values[i + 1] == receiver]
            opening = line_start + index + 4
            if (len(declarations) == len(bindings) == 1 and declarations[0] < position
                    and 'VNRecognizeTextRequest' not in declared_names
                    and opening in pairs and opening < position < pairs[opening]
                    and all(token.kind == 'string' or token.value == ','
                            for token in tokens[opening + 1:pairs[opening]])):
                return 'recognition_language_configuration', {'receiver': receiver,
                    'construction_line': tokens[declarations[0]].line}
    # Constant widget kind is proven by a real StaticConfiguration(kind: value)
    # use of the same unique lexical binding, never by its string spelling.
    declarations = []
    for begin in range(max(0, position - 5), position):
        segment = values[begin:position]
        if len(segment) >= 3 and segment[0] in {'let', 'var'} and segment[-1] == '=':
            declarations.append((begin, segment[1]))
    if len(declarations) == 1:
        begin, name = declarations[0]
        uses = [i for i in range(len(values) - 5)
                if values[i:i + 5] == ['StaticConfiguration', '(', 'kind', ':', name]]
        bindings = [i for i in range(len(values) - 1)
                    if values[i] in {'let', 'var'} and values[i + 1] == name]
        if (len(uses) == len(bindings) == 1 and bindings[0] == begin
                and source_name_counts and source_name_counts.get(name) == 1
                and 'StaticConfiguration' not in declared_names):
            return 'widget_configuration_identifier', {'binding': name, 'consumer_line': tokens[uses[0]].line}
    return 'ui_or_usage_unresolved', call


def classify_texts(project, raw):
    """Classify only exact, current source anchors; unknown usage stays required."""
    config_path = project / '.migbot/config.json'
    if not config_path.is_file():
        return []
    config = json.loads(config_path.read_text(encoding='utf-8-sig'))
    source_root = config.get('ios')
    if config.get('source_platform') != 'ios' or not isinstance(source_root, str):
        return []
    source = io_path(source_root).resolve()
    if not source.is_dir() or raw.get('source_sha256') != snapshot(source)['sha256']:
        return []
    scope_path = project / 'spec/baseline/ios-source-disposition.json'
    scope = json.loads(scope_path.read_text(encoding='utf-8-sig')) if scope_path.is_file() else {}
    approved = scope.get('files', []) if scope.get('source_sha256') == raw.get('source_sha256') else []
    cache, result, declared_names, source_name_counts = {}, [], set(), {}
    target_aggregate_anchors = None
    for path in _files(source):
        if path.suffix != '.swift':
            continue
        tokens = tokenize(path.read_text(encoding='utf-8-sig'))
        for index, token in enumerate(tokens):
            if (token.kind != 'string' and not (index and tokens[index - 1].value in {'let', 'var'})
                    and not (index + 1 < len(tokens) and tokens[index + 1].value == ':')):
                source_name_counts[token.value] = source_name_counts.get(token.value, 0) + 1
        declared_names.update(tokens[index + 1].value for index in range(len(tokens) - 1)
            if tokens[index].value in {'struct', 'class', 'enum', 'func', 'typealias'}
            or (tokens[index].value in {'let', 'var'} and tokens[index + 1].value[:1].isupper()))
    stage0_path = project / 'spec/reports/derived/stage0-resources.json'
    stage0 = json.loads(stage0_path.read_text(encoding='utf-8-sig')) if stage0_path.is_file() else {}
    for index, item in enumerate(raw.get('texts', [])):
        anchors, roles = [], []
        for anchor in item.get('sources', []):
            relative, separator, line = anchor.rpartition(':')
            if not separator or not line.isdigit() or Path(relative).is_absolute() or '..' in Path(relative).parts:
                continue
            path = io_path(source / relative).resolve()
            if not path.is_relative_to(source) or not path.is_file():
                continue
            if relative not in cache:
                body = path.read_bytes()
                tokens = tokenize(body.decode('utf-8-sig'))
                cache[relative] = (body, tokens, _pairs(tokens))
            body, tokens, pairs = cache[relative]
            digest = _hash(body)
            if item.get('file_sha256') != digest:
                continue
            positions = []
            for position, token in enumerate(tokens):
                if token.kind == 'string' and token.line == int(line):
                    try:
                        value = json.loads(token.value)
                    except ValueError:
                        continue
                    if value == item.get('value'):
                        positions.append(position)
            if not positions:
                continue
            scoped = [entry for entry in approved if entry.get('path') == relative
                and entry.get('source_sha256') == digest and type(entry.get('line')) is int
                and type(entry.get('end_line')) is int and entry['line'] <= int(line) <= entry['end_line']
                and entry.get('disposition') in {'test', 'dependency', 'not_applicable'}
                and isinstance(entry.get('reason'), str) and entry['reason'].strip()]
            if len(scoped) == 1:
                role, evidence = 'reviewed_' + scoped[0]['disposition'], {'approved_disposition': scoped[0]}
                local_roles = [(role, evidence)]
            else:
                local_roles = [_literal_role(tokens, pairs, position, declared_names, source_name_counts) for position in positions]
            for role, evidence in local_roles:
                roles.append(role)
                anchors.append({'source': anchor, 'source_sha256': digest, 'role': role,
                                'syntax_evidence': evidence})
        # No unsupported role, stale source, or ambiguous mixed usage disappears.
        complete = len({entry['source'] for entry in anchors}) == len(item.get('sources', [])) and bool(anchors)
        non_page = complete and all(role != 'ui_or_usage_unresolved' for role in roles)
        mapping = None
        if 'system_symbol_identifier' in roles:
            mapping = {'kind': 'existing-stage0-symbol-replacement',
                       'target': stage0.get('symbol_replacements', {}).get(item.get('value')),
                       'report_present': bool(stage0)}
        elif 'asset_color_identifier' in roles:
            mapping = {'kind': 'existing-stage0-source-color',
                       'source_asset': str(item.get('value')) + '.colorset',
                       'registered': str(item.get('value')) + '.colorset' in stage0.get('source_colors', {})}
        aggregate_targets = None
        if 'hidden_chart_dimension_label' in roles:
            if target_aggregate_anchors is None:
                target_aggregate_anchors = []
                for root in product_source_roots(project):
                    for target in _files(root):
                        if target.suffix != '.ets':
                            continue
                        data = target.read_bytes()
                        lines = data.decode('utf-8-sig').splitlines()
                        for line_no, text in enumerate(lines, 1):
                            match = re.search(r'\.accessibilityGroup\(true\)\.accessibilityText\(this\.([\w$]+)\(\)\)', text)
                            if not match:
                                continue
                            methods = [{'line': number, 'text': line} for number, line in enumerate(lines, 1)
                                       if re.search(r'\b' + re.escape(match[1]) + r'\([^)]*\)\s*:\s*string\s*\{', line)]
                            target_aggregate_anchors.append({'file': target.relative_to(project).as_posix(),
                                'sha256': _hash(data), 'line': line_no, 'text': text,
                                'aggregate_method': methods, 'a11y_runtime_verified': False})
            aggregate_targets = target_aggregate_anchors
        result.append({'collection': 'texts', 'index': index, 'value': item.get('value'),
            'raw_item': copy.deepcopy(item), 'classification': 'non_page_literal' if non_page else 'ui_or_usage_unresolved',
            'page_literal_required': not non_page, 'evidence': anchors, 'existing_resource_mapping': mapping,
            'target_aggregate_accessibility_anchors': aggregate_targets,
            'semantic_validation': 'not a claim that resource, protocol, formatted runtime output or behavior is equivalent'})
    return result


def _original(project, output):
    command = [sys.executable, str(ROOT / 'vendor/hmigbot/skills/a2h-execute/scripts/literal_gate.py'),
               '--project', str(project), '--json', '--output-json', str(output)]
    env = {**os.environ, 'PYTHONUTF8': '1', 'PYTHONIOENCODING': 'utf-8'}
    # Select the detector's own original script root, rather than inheriting
    # the structural pipeline's different sibling-library root.
    env['ARKTS_SKILL_DIR'] = str(ROOT / 'vendor/hmigbot/skills/a2h-execute/scripts')
    if os.name == 'nt':
        return run_owned_process(command, cwd=project, env=env, timeout=timeout_for('literal', env=env))
    from .portable_helper import run
    return run(command[1], command[2:], cwd=project, env=env, capture_output=True, timeout=timeout_for('literal', env=env))


def _detector(project, output):
    process = _original(project, output)
    if process.returncode not in {0, 1} or not output.is_file():
        raise ValueError('Original literal detector did not produce a complete report: '
                         + process.stderr.decode('utf-8', errors='replace')[-1800:])
    result = json.loads(output.read_text(encoding='utf-8-sig'))
    if (not isinstance(result, dict) or type(result.get('passed')) is not bool
            or result.get('skipped') is not False or not isinstance(result.get('stats'), dict)
            or not isinstance(result.get('findings'), list) or not isinstance(result.get('warnings'), list)
            or process.returncode != (0 if result['passed'] else 1)):
        raise ValueError('Original literal detector report is incomplete or inconsistent')
    return result


def audit(project):
    project = io_path(project).resolve()
    ledger_path = project / LEDGER
    original_bytes = ledger_path.read_bytes()
    raw = json.loads(original_bytes)
    canonical, changes = canonical_ledger(raw)
    dispositions = classify_texts(project, raw)
    non_page = {item['index'] for item in dispositions if not item['page_literal_required']}
    page_projection = copy.deepcopy(canonical)
    page_projection['texts'] = [item for index, item in enumerate(canonical.get('texts', [])) if index not in non_page]
    paths = _inputs(project)
    contents = {name: path.read_bytes() for name, path in sorted(paths.items())}
    before = {name: _hash(value) for name, value in contents.items()}
    with tempfile.TemporaryDirectory(prefix='native-literal-') as temporary:
        directory = Path(temporary)
        for name, value in contents.items():
            path = directory / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(value)
        ledger = directory / LEDGER
        ledger.parent.mkdir(parents=True, exist_ok=True)
        ledger.write_text(json.dumps(canonical, ensure_ascii=False, allow_nan=False) + '\n', encoding='utf-8')
        original_report = _detector(directory, directory / 'literal-raw.json')
        effective = original_report
        if non_page:
            ledger.write_text(json.dumps(page_projection, ensure_ascii=False, allow_nan=False) + '\n', encoding='utf-8')
            effective = _detector(directory, directory / 'literal-page-projection.json')
    after = {name: _hash(path.read_bytes()) for name, path in paths.items()}
    if before != after or ledger_path.read_bytes() != original_bytes:
        raise ValueError('Literal source input changed during the read-only audit')
    for item in dispositions:
        for evidence in item['evidence']:
            relative = evidence['source'].rpartition(':')[0]
            config = json.loads((project / '.migbot/config.json').read_text(encoding='utf-8-sig'))
            if _hash((io_path(config['ios']) / relative).read_bytes()) != evidence['source_sha256']:
                raise ValueError('Swift literal role source changed during the read-only audit')
    result = copy.deepcopy(effective)
    unresolved = [{'index': index, 'value': item['value'], 'unit': item.get('unit'),
                   'sources': item.get('sources', [])}
                  for index, item in enumerate(raw.get('dims', []))
                  if item.get('unit') == 'source_point_or_context_unresolved']
    if unresolved:
        result['stats']['dims'] = {'ok': 0, 'missing': effective['stats']['dims']['missing'],
            'unresolved': len(unresolved), 'source_units_verified': False,
            'raw_numeric_occurrence_only': copy.deepcopy(effective['stats']['dims'])}
        result['warnings'].append({'severity': 'WARN', 'kind': 'native-dimension-unit-unresolved',
            'reason': 'Numeric presence does not establish source-point to target-vp mapping or layout coverage',
            'count': len(unresolved)})
    result['original_report'] = original_report
    result['native_literal_inputs'] = {'raw_ledger_sha256': _hash(original_bytes),
        'canonical_ledger_sha256': _hash((json.dumps(canonical, ensure_ascii=False, allow_nan=False) + '\n').encode('utf-8')),
        'canonical_numeric_values': changes, 'raw_items_removed': 0,
        'page_text_projection_count': len(page_projection['texts']),
        'classified_non_page_text_count': len(non_page), 'text_classifications': dispositions,
        'source_file_hashes': before, 'mutated': False,
        'unresolved_dimensions': unresolved, 'source_units_verified': False,
        'text_and_color_decisions': 'original detector executes raw and page-role input projections; raw items/report retained, unknown page usage still checked',
        'scope': 'Literal occurrences only; not behavior verification, unit conversion or pixel equivalence'}
    return result


def main(arguments=None):
    parser = argparse.ArgumentParser(description='Original literal gate with native numeric input representation')
    parser.add_argument('--project', type=Path, required=True)
    parser.add_argument('--json', action='store_true')
    parser.add_argument('--output-json', type=Path)
    args = parser.parse_args(arguments)
    try:
        result = audit(args.project)
    except (ValueError, OSError, KeyError, subprocess.TimeoutExpired) as exc:
        result = {'detector': 'literal', 'passed': False, 'skipped': False, 'error': str(exc),
            'findings': [{'severity': 'FAIL', 'code': 'native-literal-input-error', 'message': str(exc)}],
            'warnings': []}
        if isinstance(exc, subprocess.TimeoutExpired):
            result['process_output'] = timeout_evidence(exc)
    if args.output_json:
        write_json(args.output_json, result)
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
