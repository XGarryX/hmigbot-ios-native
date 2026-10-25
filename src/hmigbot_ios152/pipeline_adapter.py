"""Fresh compiled pipeline measurements and guarded canonical publication.

The backend runs only in an external temporary work directory. Its diagnostic
verdict is archived and discarded. Canonical convergence uses current measured
facts, the actual canonical history, and the unchanged source_verdict rules.
"""
from __future__ import annotations
from dataclasses import dataclass, field
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

from . import pipeline_transactions

DETECTORS = tuple(sorted(('assembly', 'audit', 'binding', 'carrier', 'deadshell',
                         'hittest', 'icon', 'immersive', 'ledger', 'literal',
                         'orphans', 'resname', 'theme')))
_GENERATED = re.compile(r'^(?:' + '|'.join(DETECTORS) + r')-pipeline-iter\d+\.json$')


@dataclass
class RunnerOutcome:
    backend_called: bool = False
    backend_exit_code: int | None = None
    backend_stdout: bytes = b''
    backend_stderr: bytes = b''
    backend_workdir: Path | None = None
    canonical_exit_code: int = 3
    canonical_committed: bool = False
    canonical_files: dict = field(default_factory=dict)
    failure_stage: str | None = None
    binding_rows: list = field(default_factory=list)
    orphan_provenance: dict = field(default_factory=dict)
    stdout: bytes = b''
    stderr: bytes = b''


def _encoded(value):
    return json.dumps(value, ensure_ascii=False, indent=2).encode('utf-8')


def _read_object(path):
    value = json.loads(path.read_bytes())
    if not isinstance(value, dict):
        raise ValueError(f'JSON object required: {path}')
    return value


def _options(argv):
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--project-root', required=True, type=Path)
    parser.add_argument('--mode', required=True, choices=['pipeline'])
    parser.add_argument('--target', required=True)
    parser.add_argument('--state-file', required=True, type=Path)
    parser.add_argument('--max-iter', type=int, default=8)
    parser.add_argument('--output-json', type=Path)
    args, _ = parser.parse_known_args(argv[1:])
    return args


def _replace_option(argv, option, value):
    output = []
    index = 0
    while index < len(argv):
        if argv[index] == option:
            index += 2
        elif argv[index].startswith(option + '='):
            index += 1
        else:
            output.append(argv[index])
            index += 1
    return [*output, option, str(value)]


def _file_signature(path):
    try:
        stat = path.stat()
        return {'device': stat.st_dev, 'inode': stat.st_ino, 'resolved': str(path.resolve()),
                'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
    except FileNotFoundError:
        return {'absent': True}


def _input_signature(project, state_path, output_path, engine, scripts):
    """Hash native inputs and their file identities, excluding generated logs."""
    excluded = {'.git', 'oh_modules', 'node_modules', 'build', '.cxx', '.preview',
                '.claude', '.agents', '.codex', '.hvigor', '__pycache__'}
    explicit_outputs = {state_path, output_path}
    inputs = []
    for directory, dirs, names in os.walk(project):
        base = Path(directory)
        dirs[:] = [name for name in dirs if name not in excluded and not
                   (base == project / 'spec' and name == 'execution')]
        for name in names:
            path = base / name
            if path.resolve() in explicit_outputs or _GENERATED.match(name):
                continue
            if path.suffix.lower() in ('.ets', '.swift', '.json', '.json5', '.md', '.plist', '.properties', '.ts'):
                inputs.append(path)
    inputs.extend((Path(engine), scripts / 'source_verdict.py', Path(__file__), Path(pipeline_transactions.__file__)))
    inputs.extend(Path(__file__).with_name(name) for name in
                  ('orphan_measurement.py', 'orphan_measurement_sdk.cjs', 'ets_components.cjs'))
    inputs.extend(scripts / name for name in
                  ('fswalk.py', 'ref_graph_lib/graph.py', 'ref_graph_lib/ets_parser.py',
                   'ref_graph_lib/import_resolver.py'))
    inputs.append(Path(sys.executable))
    signature = {str(path): _file_signature(path) for path in sorted(set(inputs))}
    signature['<pipeline-process-context>'] = {'child_python_hash_seed': '0',
        'fresh_python_executable': sys.executable, 'fresh_python_version': sys.version}
    return signature


def _evaluate(scripts, history, current, max_iter):
    path = scripts / 'source_verdict.py'
    spec = importlib.util.spec_from_file_location('_hmigbot_pipeline_source_verdict', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.evaluate(history, current, max_iter)


def _measurements(workdir, process):
    if process.returncode not in (0, 1, 2):
        raise RuntimeError(f'compiled pipeline process exited {process.returncode}')
    state = _read_object(workdir / 'backend-state.json')
    result = _read_object(workdir / 'backend-result.json')
    history = state.get('history')
    if not isinstance(history, list) or len(history) != 1 or not isinstance(history[0], dict) or history[0].get('iter') != 0:
        raise ValueError('backend is not a fresh iteration-zero measurement')
    current = history[0]
    expected_exit = {'CONVERGED': 0, 'CONTINUE': 1, 'STALLED': 2, 'REGRESSED': 2, 'EXHAUSTED': 2}
    if result.get('verdict') not in expected_exit:
        raise DispatchTemplateUnsupported('unknown native verdict shape')
    if process.returncode != expected_exit[result['verdict']] or state.get('last_verdict', {}).get('verdict') != result['verdict']:
        raise ValueError('native exit/state/result verdict observations disagree')
    if current.get('detectors_run') != list(DETECTORS) or current.get('detectors_effective') != list(DETECTORS) or current.get('detectors_skipped') != []:
        raise ValueError('backend did not complete all thirteen effective detectors')
    data, raw, paths = {}, {}, {}
    for name in DETECTORS:
        found = list(workdir.glob(name + '-pipeline-iter0.json'))
        if len(found) != 1:
            raise ValueError(f'missing or ambiguous fresh detector JSON: {name}')
        path = found[0]
        raw[name] = path.read_bytes()
        data[name] = _read_object(path)
        paths[name] = path
    if result.get('iteration') != 0 or result.get('mode') != 'pipeline' or state.get('mode') != 'pipeline':
        raise ValueError('backend result metadata does not describe pipeline iteration zero')
    return state, result, data, raw, paths


def _number(value, label):
    if type(value) is not int or value < 0:
        raise ValueError('invalid native count: ' + label)
    return value


def _fresh_counts(measured, binding, orphans=None):
    audit = measured['audit']
    summary = audit.get('summary', {})
    wiring = _number((measured['orphans'] if orphans is None else orphans).get('orphan_count', 0), 'orphans')
    wiring += int(not measured['immersive'].get('passed', True))
    wiring += int(not measured['icon'].get('passed', True))
    wiring += _number(measured['ledger'].get('summary', {}).get('FAIL', 0), 'ledger')
    wiring += len(measured['assembly'].get('findings', []))
    wiring += len(binding.get('findings', []))
    for name in ('theme', 'literal', 'deadshell', 'carrier', 'hittest', 'resname'):
        wiring += sum(item.get('severity') == 'FAIL' for item in measured[name].get('findings', []))
    return {'audit_fail': _number(summary.get('FAIL', 0), 'audit.FAIL'),
            'audit_warn': _number(summary.get('WARN', 0), 'audit.WARN'),
            'wiring_blocked_categories': 0, 'wiring_repair_actions': wiring,
            'handoff_escape_hatches': len(audit.get('handoff_escape_hatches', []))}


def _binding_fingerprint(binding):
    return [[item.get('file', ''), 0, 'binding:' + item.get('kind', '') + ':' + item.get('class', '')]
            for item in binding.get('findings', [])]


def _orphan_fingerprint(orphans):
    return [[item['file'], 0, 'pipeline-orphan:' + item['class_name'] + ':' + item['reason']]
            for item in orphans['orphans']]


def _validate_orphans(measurement, native, raw):
    if measurement.baseline_bytes != raw or measurement.baseline != native:
        raise ValueError('fresh source orphan baseline differs from same-seed native measurement')
    fresh = measurement.result
    if json.loads(measurement.result_bytes) != fresh:
        raise ValueError('fresh orphan bytes and facts disagree')
    proofs = measurement.provenance.get('rescued', [])
    records = [proof['record'] for proof in proofs]
    if any(not proof.get('chain') for proof in proofs):
        raise ValueError('orphan correction lacks a component composition proof chain')
    if any(record not in native['orphans'] or record['reason'] != 'NO_IMPORTER' for record in records):
        raise ValueError('orphan composition proof does not identify a native NO_IMPORTER record')
    encoded = [json.dumps(record, sort_keys=True) for record in records]
    if len(encoded) != len(set(encoded)):
        raise ValueError('duplicate orphan composition proof')
    # This assertion validates independently generated full facts; it never
    # produces the fresh result from native findings or subtracts native totals.
    expected = dict(native)
    expected['orphans'] = [item for item in native['orphans'] if item not in records]
    expected['orphan_count'] = len(expected['orphans'])
    expected['component_orphan_count'] = fresh['component_orphan_count']
    if (fresh != expected or fresh['component_orphan_count'] < 0 or
            fresh['component_orphan_count'] + len(records) != native['component_orphan_count']):
        raise ValueError('fresh orphan measurement changed facts outside proven local composition')
    if not proofs and measurement.result_bytes != raw:
        raise ValueError('unchanged orphan facts did not preserve native bytes')


def _current_record(measured, native_current, binding, iteration, orphans=None):
    # All numbers come from fresh thirteen detector facts. The native current
    # record supplies only the unchanged twelve categories' interpretation.
    baseline_counts = _fresh_counts(measured, measured['binding'])
    if any(native_current.get(key) != value for key, value in baseline_counts.items()):
        raise ValueError('fresh detector counts differ from native aggregation')
    native_fingerprint = native_current.get('fingerprint')
    if not isinstance(native_fingerprint, list) or any(not isinstance(item, list) or len(item) != 3 for item in native_fingerprint):
        raise ValueError('invalid native fingerprint record')
    is_binding = lambda item: isinstance(item[2], str) and item[2].startswith('binding:')
    native_binding = [item for item in native_fingerprint if is_binding(item)]
    original_generated = _binding_fingerprint(measured['binding'])
    if original_generated != native_binding:
        raise ValueError('fresh binding fingerprint differs from native aggregation')
    is_orphan = lambda item: isinstance(item[2], str) and item[2].startswith('pipeline-orphan:')
    if [item for item in native_fingerprint if is_orphan(item)] != _orphan_fingerprint(measured['orphans']):
        raise ValueError('fresh orphan fingerprint differs from native aggregation')
    fresh_binding = _binding_fingerprint(binding)
    fresh_orphans = _orphan_fingerprint(measured['orphans'] if orphans is None else orphans)
    rebuilt = []
    inserted = False
    orphan_inserted = False
    for item in native_fingerprint:
        if is_binding(item):
            if not inserted:
                rebuilt.extend(fresh_binding)
                inserted = True
        elif is_orphan(item):
            if not orphan_inserted:
                rebuilt.extend(fresh_orphans)
                orphan_inserted = True
        else:
            rebuilt.append(item)
    if fresh_binding and not inserted:
        raise ValueError('binding measurement introduced a failure absent from native category')
    if fresh_orphans and not orphan_inserted:
        raise ValueError('orphan measurement introduced a failure absent from native category')
    current = dict(native_current)
    current['iter'] = iteration
    current.update(_fresh_counts(measured, binding, orphans))
    current['fingerprint'] = rebuilt
    current['detectors_run'] = list(DETECTORS)
    current['detectors_skipped'] = []
    current['detectors_effective'] = list(DETECTORS)
    return current


def _path_for_project(path, project):
    try:
        return str(path.relative_to(project))
    except ValueError:
        return str(path)


class DiagnosticPathUnmapped(RuntimeError):
    pass


def _json_string_spans(raw):
    text = raw.decode('utf-8')
    decoder = json.JSONDecoder()
    spans = {}
    def skip(index):
        while index < len(text) and text[index].isspace(): index += 1
        return index
    def value(index, pointer):
        index = skip(index)
        start = index
        if text[index] == '{':
            index = skip(index + 1)
            while text[index] != '}':
                key, stop = decoder.raw_decode(text, index)
                index = skip(stop)
                if text[index] != ':': raise ValueError('invalid JSON object separator')
                escaped = key.replace('~', '~0').replace('/', '~1')
                index = skip(value(index + 1, pointer + '/' + escaped))
                if text[index] == ',': index = skip(index + 1)
                else: break
            return index + 1
        if text[index] == '[':
            index = skip(index + 1); number = 0
            while text[index] != ']':
                index = skip(value(index, pointer + '/' + str(number))); number += 1
                if text[index] == ',': index = skip(index + 1)
                else: break
            return index + 1
        item, stop = decoder.raw_decode(text, index)
        if isinstance(item, str):
            spans[pointer] = (len(text[:start].encode('utf-8')), len(text[:stop].encode('utf-8')), item)
        return stop
    value(0, '')
    return spans


def _tokens(value, path):
    offset = 0
    while True:
        start = value.find(path, offset)
        if start < 0: return
        end = start + len(path)
        # These are the exact token delimiters observed in native safe-error
        # diagnostics. A path fragment, suffix, or prefix is never rewritten.
        if (start == 0 and end == len(value)) or (start > 0 and end < len(value) and
                value[start - 1] == value[end] and value[end] in ("'", '"')):
            yield start, end
        offset = end


def _diagnostic_json(raw, *, location, mapping, changes):
    original = json.loads(raw)
    if not isinstance(original, dict): raise ValueError('detector JSON is not an object')
    spans = _json_string_spans(raw)
    allowed = set()
    if original.get('passed') is False: allowed.add('/error')
    for index, finding in enumerate(original.get('findings', [])):
        if original.get('detector') == 'binding' and original.get('passed') is False and isinstance(finding, dict) and finding.get('kind') == 'binding-gate-not-run':
            allowed.add('/findings/' + str(index) + '/reason')
    patches = []
    expected = json.loads(raw)
    for pointer in allowed:
        if pointer not in spans: continue
        start, end, value = spans[pointer]
        value_patches = []
        token_raw = raw[start:end]
        replacements = []
        for old, new in mapping.items():
            occurrences = list(_tokens(value, old))
            if not occurrences: continue
            old_encoded = json.dumps(old, ensure_ascii=False)[1:-1].encode('utf-8')
            new_encoded = json.dumps(new, ensure_ascii=False)[1:-1].encode('utf-8')
            if token_raw.count(old_encoded) != len(occurrences):
                raise DiagnosticPathUnmapped('unsupported diagnostic JSON escape form')
            # Each accepted occurrence is a full native-delimited path token.
            # Byte patch locations stay relative to the original source file.
            offset = 0
            for _ in occurrences:
                at = token_raw.index(old_encoded, offset)
                replacements.append((start + at, start + at + len(old_encoded), new_encoded))
                offset = at + len(old_encoded)
                changes.append({'kind': 'diagnostic-json-path', 'location': str(location),
                    'pointer': pointer, 'source_sha256': hashlib.sha256(raw).hexdigest(),
                    'start_byte': start + at, 'end_byte': start + at + len(old_encoded),
                    'old_path': old, 'new_path': new, 'old_hex': old_encoded.hex(), 'new_hex': new_encoded.hex()})
            value_patches.extend((left, right, new) for left, right in occurrences)
        if replacements:
            new_value = value
            for left, right, replacement in sorted(value_patches, reverse=True):
                new_value = new_value[:left] + replacement + new_value[right:]
            patches.extend(replacements)
            parts = pointer.split('/')[1:]
            parent = expected
            for key in parts[:-1]: parent = parent[int(key)] if isinstance(parent, list) else parent[key.replace('~1', '/').replace('~0', '~')]
            last = parts[-1]
            parent[int(last) if isinstance(parent, list) else last] = new_value
    mapped = raw
    for start, end, replacement in sorted(patches, reverse=True):
        mapped = mapped[:start] + replacement + mapped[end:]
    if json.loads(mapped) != expected:
        raise DiagnosticPathUnmapped('diagnostic byte patch changed unapproved JSON content')
    return mapped


def _diagnostic_leaks(outputs, workdir, mapping):
    needles = [str(workdir), *mapping]
    for location, raw in outputs.items():
        representations = [raw]
        try:
            representations.append(json.dumps(json.loads(raw), ensure_ascii=False).encode('utf-8'))
        except (ValueError, UnicodeError):
            pass
        if any(needle.encode('utf-8') in representation for needle in needles for representation in representations):
            raise DiagnosticPathUnmapped('unmapped measurement output path in ' + str(location))


class DispatchTemplateUnsupported(RuntimeError):
    pass


def _fragment(record, kind, source, start, end, replacement):
    record.append({'kind': kind, 'source_sha256': hashlib.sha256(source).hexdigest(),
                   'start_byte': start, 'end_byte': end, 'old_hex': source[start:end].hex(),
                   'new_hex': replacement.hex()})


def _dispatch(raw_prompt, iteration, target, history, changes):
    raw = raw_prompt.encode('utf-8')
    header = f'=== STRUCTURAL LOOP — pipeline={target} iteration 0 repair brief ===\n'.encode('utf-8')
    if not raw.startswith(header):
        raise DispatchTemplateUnsupported('unrecognized native dispatch header')
    marker = b'## History so far (iterations 0..-1)\n'
    if raw.count(marker) != 1:
        raise DispatchTemplateUnsupported('unrecognized native dispatch history section')
    start = raw.index(marker)
    end = raw.find('\n## 约束\n'.encode('utf-8'), start)
    if end < 0:
        raise DispatchTemplateUnsupported('unrecognized native dispatch constraint tail')
    native_history = raw[start + len(marker):end]
    # The original fresh iteration-zero dispatch includes its current record.
    # Oracle checks confirm this complete line grammar, including the newline.
    if not re.fullmatch(rb'  iter 0: audit_fail=\d+ wiring_repair=\d+\n', native_history):
        raise DispatchTemplateUnsupported('unrecognized native history line grammar')
    lines = f'## History so far (iterations 0..{iteration-1})\n'
    for item in history:
        lines += f"  iter {item['iter']}: audit_fail={item.get('audit_fail',0)} wiring_repair={item.get('wiring_repair_actions',0)}\n"
    new_header = f'=== STRUCTURAL LOOP — pipeline={target} iteration {iteration} repair brief ===\n'.encode('utf-8')
    new_history = lines.encode('utf-8')
    _fragment(changes, 'dispatch-iteration-header', raw, 0, len(header), new_header)
    _fragment(changes, 'dispatch-history', raw, start, end, new_history)
    return (new_header + raw[len(header):start] + new_history + raw[end:]).decode('utf-8')


def _orphan_dispatch(prompt, original, fresh, changes):
    if original == fresh:
        return prompt
    raw = prompt.encode('utf-8')
    headers = list(re.finditer(rb'## Cross-Slice orphans \(ref_graph_lib, (\d+) items\)\n', raw))
    if len(headers) != 1 or int(headers[0].group(1)) != len(original['orphans']):
        raise DispatchTemplateUnsupported('unrecognized native orphan dispatch header')
    header = headers[0]
    start = raw.find(b'\n```json\n', header.end())
    end = raw.find(b'\n```\n', start + 9) if start >= 0 else -1
    if start < 0 or end < 0:
        raise DispatchTemplateUnsupported('missing native orphan dispatch JSON')
    start += len(b'\n```json\n')
    if json.loads(raw[start:end]) != original['orphans']:
        raise DispatchTemplateUnsupported('native orphan dispatch disagrees with fresh native facts')
    replacement = json.dumps(fresh['orphans'], ensure_ascii=False, indent=2).encode('utf-8')
    new_header = f"## Cross-Slice orphans (ref_graph_lib, {len(fresh['orphans'])} items)\n".encode('utf-8')
    _fragment(changes, 'orphan-dispatch-header', raw, header.start(), header.end(), new_header)
    _fragment(changes, 'orphan-dispatch-facts', raw, start, end, replacement)
    return (raw[:header.start()] + new_header + raw[header.end():start] + replacement + raw[end:]).decode('utf-8')


def _verdict_shape(backend, canonical):
    # All supported shapes are exercised against real native history/cap
    # controls. Fresh iteration zero cannot produce STALLED or REGRESSED.
    supported = {('CONVERGED', 'CONVERGED'), ('CONTINUE', 'CONTINUE'),
                 ('CONTINUE', 'CONVERGED'), ('CONTINUE', 'STALLED'),
                 ('CONTINUE', 'REGRESSED'), ('CONTINUE', 'EXHAUSTED'),
                 ('EXHAUSTED', 'EXHAUSTED'), ('EXHAUSTED', 'CONVERGED')}
    if (backend, canonical) not in supported:
        raise DispatchTemplateUnsupported('uncovered native/canonical verdict combination')


def _binding_report(binding, *, fail_prefix, warning_prefix):
    report = b''
    for name, prefix, rows in [('FAIL', fail_prefix, binding.get('findings', [])),
                               ('WARN', warning_prefix, binding.get('warnings', []))]:
        for item in rows:
            report += prefix + f"{name} [{item.get('kind', '')}] {item.get('class', '')} ({item.get('file', '')})\n".encode('utf-8')
    report += f"binding_gate: {len(binding.get('findings', []))} FAIL / {len(binding.get('warnings', []))} WARN / manifest={binding.get('manifest', 'absent')}\n".encode('utf-8')
    return report


def _canonical_stdout(raw, original_binding, binding, changes):
    if binding == original_binding:
        return raw
    prefixes = {}
    lines = raw.splitlines(keepends=True)
    for name, key in [('FAIL', 'findings'), ('WARN', 'warnings')]:
        found = set()
        for item in original_binding.get(key, []):
            suffix = f"{name} [{item.get('kind', '')}] {item.get('class', '')} ({item.get('file', '')})\n".encode('utf-8')
            matched = [line[:-len(suffix)] for line in lines if line.endswith(suffix)]
            if not matched:
                raise DispatchTemplateUnsupported('native binding report line not found')
            found.update(matched)
        if len(found) > 1:
            raise DispatchTemplateUnsupported('ambiguous native binding report prefix')
        prefixes[name] = next(iter(found), b'')
    original = _binding_report(original_binding, fail_prefix=prefixes['FAIL'], warning_prefix=prefixes['WARN'])
    if raw.count(original) != 1:
        raise DispatchTemplateUnsupported('native binding report boundary is not unique')
    replacement = _binding_report(binding, fail_prefix=prefixes['FAIL'], warning_prefix=prefixes['WARN'])
    start = raw.index(original)
    _fragment(changes, 'binding-stdout-report', raw, start, start + len(original), replacement)
    return raw[:start] + replacement + raw[start + len(original):]


def _error(outcome, stage, error):
    outcome.failure_stage = stage
    outcome.canonical_exit_code = 3
    outcome.stdout = outcome.backend_stdout
    outcome.stderr = outcome.backend_stderr + (f'Pipeline adapter: {stage}: {type(error).__name__}: {error}\n').encode('utf-8')
    return outcome


def make_runner(declaration=None):
    """Return the keyword callback consumed by icon_input.maybe_run."""
    def run(*, project, argv, engine, scripts_dir, env, code_before, icon_evidence):
        from .icon_input import snapshot
        outcome = RunnerOutcome()
        stage = 'signature'
        project, scripts = Path(project).resolve(), Path(scripts_dir).resolve()
        try:
            if pipeline_transactions.unfinished_transactions(project):
                raise RuntimeError('unfinished pipeline transaction requires explicit recovery')
            args = _options(argv)
            state_path = args.state_file.resolve()
            output_path = args.output_json.resolve() if args.output_json else None
            for path in (state_path, output_path):
                if path and any(path.parts[index:index+2] == ('docs', 'autofix-log') for index in range(len(path.parts)-1)):
                    raise ValueError('closure output uses deprecated docs/autofix-log')
            old_state_signature = _file_signature(state_path)
            state = _read_object(state_path) if state_path.exists() else {'history': [], 'max_iter': args.max_iter}
            history = state.setdefault('history', [])
            if not isinstance(history, list) or any(not isinstance(item, dict) for item in history):
                raise ValueError('canonical history is not a list of JSON objects')
            iteration = len(history)
            inputs = _input_signature(project, state_path, output_path, engine, scripts)
            workdir = Path(tempfile.mkdtemp(prefix='hmigbot-pipeline-')).resolve()
            outcome.backend_workdir = workdir
            if workdir.is_relative_to(project):
                raise OSError('backend temporary directory must be outside project')
            (workdir / 'backend-input-signature.json').write_bytes(_encoded(inputs))
            backend_argv = _replace_option(argv, '--state-file', workdir / 'backend-state.json')
            backend_argv = _replace_option(backend_argv, '--output-json', workdir / 'backend-result.json')
            command = [str(engine), 'structural_loop', *backend_argv]
            stage = 'backend'
            measurement_env = dict(env, ARKTS_SKILL_DIR=str(scripts), PYTHONHASHSEED='0')
            process = subprocess.run(command, capture_output=True, env=measurement_env)
            outcome.backend_called = True
            outcome.backend_exit_code = process.returncode
            outcome.backend_stdout, outcome.backend_stderr = process.stdout, process.stderr
            (workdir / 'backend-stdout.log').write_bytes(process.stdout)
            (workdir / 'backend-stderr.log').write_bytes(process.stderr)
            (workdir / 'backend-process.json').write_bytes(_encoded({'argv': command, 'exit_code': process.returncode,
                    'verdict_discarded': True, 'canonical_history_used_for_measurement': False,
                    'environment_overrides': {'PYTHONHASHSEED': '0'}}))
            stage = 'measurement_json'
            backend_state, backend_result, measured, raw, paths = _measurements(workdir, process)
            destinations = {name: state_path.parent / paths[name].name.replace('-iter0.json', f'-iter{iteration}.json') for name in DETECTORS}
            diagnostic_mapping = {str(paths[name]): str(destinations[name]) for name in DETECTORS}
            diagnostic_mapping[str(workdir / 'backend-state.json')] = str(state_path)
            if output_path is not None:
                diagnostic_mapping[str(workdir / 'backend-result.json')] = str(output_path)
            stage = 'orphan_measurement'
            from .orphan_measurement import measure_orphans
            orphan_measurement = measure_orphans(project=project, scripts_dir=scripts,
                evidence=workdir / 'orphan-measurement', env=measurement_env)
            _validate_orphans(orphan_measurement, measured['orphans'], raw['orphans'])
            outcome.orphan_provenance = orphan_measurement.provenance
            binding, measurement = measured['binding'], None
            if declaration is not None:
                stage = 'binding_io'
                from .binding_projection import measure_binding_projection
                measurement = measure_binding_projection(project=project, engine=Path(engine), scripts_dir=scripts,
                    evidence=workdir / 'binding-projection', env=measurement_env, declaration=declaration,
                    original_binding=measured['binding'])
                outcome.binding_rows = measurement.rows
                binding = measurement.result
            stage = 'measurement_json'
            current = _current_record(measured, backend_state['history'][0], binding, iteration, orphan_measurement.result)
            verdict, exit_code = _evaluate(scripts, history, current, args.max_iter)
            history.append(current)
            state['max_iter'] = args.max_iter
            state['last_verdict'] = verdict
            state['mode'], state['target'] = args.mode, args.target
            result = dict(backend_result)
            result.update(iteration=iteration, verdict=verdict['verdict'], escalation=verdict['escalation'], reason=verdict['reason'])
            result['current_state'] = {'audit_fail': current['audit_fail'],
                'wiring_repair_actions': current['wiring_repair_actions'], 'handoff_escape_hatches': current['handoff_escape_hatches'],
                'total_fail': current['audit_fail'] + current['wiring_repair_actions'] + current['handoff_escape_hatches']}
            changes = []
            _verdict_shape(backend_result['verdict'], verdict['verdict'])
            if verdict['verdict'] == 'CONTINUE':
                prompt = _orphan_dispatch(backend_result['dispatch_prompt'], measured['orphans'], orphan_measurement.result, changes)
                result['dispatch_prompt'] = _dispatch(prompt, iteration, args.target, history, changes)
            else:
                result['dispatch_prompt'] = ''
                raw_prompt = backend_result['dispatch_prompt'].encode('utf-8')
                if raw_prompt:
                    _fragment(changes, 'verdict-suppressed-dispatch', raw_prompt, 0, len(raw_prompt), b'')
            result['detector_json_paths'] = {name: _path_for_project(destinations[name], project) for name in backend_result['detector_json_paths']}
            result['state_file'] = _path_for_project(state_path, project)
            targets = {destinations[name]: raw[name] for name in DETECTORS}
            # Unchanged binding facts retain their original native byte format.
            if binding != measured['binding']:
                targets[destinations['binding']] = json.dumps(binding, ensure_ascii=False, indent=1).encode('utf-8')
            targets[destinations['orphans']] = orphan_measurement.result_bytes
            targets = {path: _diagnostic_json(data, location=path, mapping=diagnostic_mapping, changes=changes) for path, data in targets.items()}
            if output_path is not None:
                if output_path in targets or output_path == state_path:
                    raise ValueError('canonical output destinations overlap')
                targets[output_path] = _encoded(result)
            targets[state_path] = _encoded(state)
            canonical_stdout = _canonical_stdout(process.stdout, measured['binding'], binding, changes)
            if output_path is None:
                canonical_stdout += _encoded(result) + b'\n'
            (workdir / 'diagnostic-path-mappings.json').write_bytes(_encoded({'mapping': diagnostic_mapping, 'changes': changes}))
            _diagnostic_leaks({**targets, 'stdout': canonical_stdout, 'stderr': process.stderr,
                'dispatch': result['dispatch_prompt'].encode('utf-8')}, workdir, diagnostic_mapping)
            (workdir / 'canonical-derivation.json').write_bytes(_encoded({
                'native_binary_sha256': hashlib.sha256(Path(engine).read_bytes()).hexdigest(),
                'native_result_sha256': hashlib.sha256((workdir / 'backend-result.json').read_bytes()).hexdigest(),
                'native_prompt_sha256': hashlib.sha256(backend_result['dispatch_prompt'].encode('utf-8')).hexdigest(),
                'orphan_provenance': orphan_measurement.provenance,
                'transformations': changes, 'current': current, 'verdict': verdict,
                'canonical_result': result, 'canonical_state': state}))
            stage = 'signature'
            orphan_measurement.verify()
            if measurement is not None:
                measurement.verify()
            stage = 'precommit_code_changed'
            if snapshot(project) != code_before:
                raise RuntimeError('target code changed before canonical commit')
            stage = 'signature'
            after_inputs = _input_signature(project, state_path, output_path, engine, scripts)
            (workdir / 'backend-input-signature-after.json').write_bytes(_encoded(after_inputs))
            if after_inputs != inputs or _file_signature(state_path) != old_state_signature:
                raise RuntimeError('pipeline measurement inputs or canonical history changed before commit')
            # The final signature check is immediately before entering staging.
            stage = 'signature'
            orphan_measurement.verify()
            if measurement is not None:
                measurement.verify()
            stage = 'commit'
            transaction = pipeline_transactions.commit_files(targets, state_path=state_path, icon_evidence=icon_evidence)
            outcome.canonical_committed = True
            outcome.canonical_files = transaction.files
            outcome.canonical_exit_code = exit_code
            outcome.stdout, outcome.stderr = canonical_stdout, process.stderr
            outcome.failure_stage = None
            return outcome
        except (Exception, SystemExit) as error:
            if type(error).__name__ in ('ProjectionInputChanged', 'OrphanInputChanged'):
                stage = 'signature'
            elif type(error).__name__ == 'ProjectionMeasurementError':
                stage = 'measurement'
            return _error(outcome, stage, error)
    return run
