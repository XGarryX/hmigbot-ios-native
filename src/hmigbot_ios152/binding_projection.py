"""Optional whole-row presence projections. All proof/evidence stays external.

The compiled binding detector remains the measurement oracle. This module only
replaces a freshly measured runtime row after both official syntax chains prove
the declared projection. It does not prove delivery, timing or visual semantics.
"""
from dataclasses import dataclass, field
from pathlib import Path
import copy
import hashlib
import json
import os
import subprocess
import uuid


class ProjectionInputError(ValueError):
    pass


class ProjectionEvidenceError(OSError):
    pass


class ProjectionInputChanged(RuntimeError):
    pass


class ProjectionMeasurementError(RuntimeError):
    """A native measurement is incomplete or cannot establish equivalence."""


@dataclass(frozen=True)
class Declaration:
    path: Path
    sha256: str
    data: dict


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ProjectionInputError('Duplicate JSON key: ' + key)
        value[key] = item
    return value


def _keys(value, expected, location):
    if not isinstance(value, dict) or set(value) != set(expected.split()):
        raise ProjectionInputError('Invalid keys/object at ' + location)


def _strings(value, keys, location):
    _keys(value, keys, location)
    for key in keys.split():
        if not isinstance(value[key], str) or not value[key].strip():
            raise ProjectionInputError('Expected nonempty string: ' + location + '.' + key)


def _digest(value, location):
    if not isinstance(value, str) or len(value) != 64 or any(c not in '0123456789abcdef' for c in value):
        raise ProjectionInputError('Expected lowercase SHA256: ' + location)


def load_declarations(project: Path) -> Declaration | None:
    """Pure formal-input read; absent only means the formal path is missing."""
    path = Path(project) / 'spec/baseline/ui/target-binding-projections.json'
    try:
        raw = path.read_bytes()
    except FileNotFoundError as error:
        # A dangling link or a missing parent under an existing formal entry is
        # an input error, not an opt-out.
        if not os.path.lexists(path):
            return None
        raise ProjectionInputError('Unreadable declaration: ' + str(path)) from error
    except OSError as error:
        raise ProjectionInputError('Unreadable declaration: ' + str(path)) from error
    try:
        data = json.loads(raw.decode('utf-8-sig'), object_pairs_hook=_object,
                          parse_constant=lambda x: (_ for _ in ()).throw(ProjectionInputError('Invalid JSON constant: ' + x)))
    except (ValueError, UnicodeError) as error:
        raise ProjectionInputError('Invalid projection JSON: ' + str(error)) from error
    _keys(data, 'schema projections', 'declaration')
    if data['schema'] != 'native-binding-projections.v1' or not isinstance(data['projections'], list):
        raise ProjectionInputError('Invalid projection schema/list')
    ids, rows = set(), set()
    for item in data['projections']:
        _keys(item, 'id source_row_index source_row_sha256 mapping_ref proof', 'projection')
        if not isinstance(item['id'], str) or not item['id'].strip():
            raise ProjectionInputError('Invalid projection id')
        index = item['source_row_index']
        if type(index) is not int or index < 0:
            raise ProjectionInputError('Invalid source_row_index')
        if item['id'] in ids or index in rows:
            raise ProjectionInputError('Duplicate projection id or source row')
        ids.add(item['id']); rows.add(index)
        _digest(item['source_row_sha256'], 'source_row_sha256')
        ref = item['mapping_ref']
        _strings(ref, 'file anchor section_sha256', 'mapping_ref')
        _digest(ref['section_sha256'], 'section_sha256')
        proof = item['proof']
        _keys(proof, 'kind producer extension receiver render', 'proof')
        if not isinstance(proof['kind'], str) or not proof['kind'].strip():
            raise ProjectionInputError('Invalid proof kind')
        _strings(proof['producer'], 'file data_function input_parameter boolean_field binding_function', 'producer')
        _strings(proof['extension'], 'file class form_profile form_name', 'extension')
        _strings(proof['receiver'], 'file component storage_member', 'receiver')
        if not isinstance(proof['render'], list) or not proof['render']:
            raise ProjectionInputError('render must be a nonempty list')
        selectors = set()
        for render in proof['render']:
            _strings(render, 'file component param', 'render')
            selector = tuple(render[k] for k in ('file', 'component', 'param'))
            if selector in selectors:
                raise ProjectionInputError('Duplicate render selector')
            selectors.add(selector)
    return Declaration(path, _sha(raw), data)


@dataclass
class RawRow:
    index: int
    raw: bytes
    value: object


class ManifestRows:
    """Keep the actual JSON token bytes, including each row's original spacing."""
    def __init__(self, raw):
        text = raw.decode('utf-8-sig')
        document = json.loads(text)
        if not isinstance(document, dict):
            raise ValueError('Manifest is not an object')
        decoder = json.JSONDecoder()
        def skip(i):
            while i < len(text) and text[i] in ' \t\r\n': i += 1
            return i
        i = skip(0) + 1
        span = None
        while text[skip(i)] != '}':
            key, end = decoder.raw_decode(text, skip(i)); i = skip(end)
            if text[i] != ':': raise ValueError('Invalid manifest separator')
            start = skip(i + 1); value, end = decoder.raw_decode(text, start)
            if key == 'rows':
                # Match native JSON's last-key semantics, preserving any
                # earlier same-named field bytes in the surrounding document.
                span = start, end; selected_rows = value
            i = skip(end)
            if text[i] == ',': i += 1
            else: break
        self.rows = []; self.prefix = self.suffix = b''
        if span is not None:
            if not isinstance(selected_rows, list): raise ValueError('Invalid manifest rows')
            start, end = span
            bom = b'\xef\xbb\xbf' if raw.startswith(b'\xef\xbb\xbf') else b''
            self.prefix = bom + text[:start + 1].encode(); self.suffix = text[end - 1:].encode()
            i = skip(start + 1)
            while text[i] != ']':
                value, stop = decoder.raw_decode(text, i)
                self.rows.append(RawRow(len(self.rows), text[i:stop].encode(), value))
                i = skip(stop)
                if text[i] == ',': i = skip(i + 1)
                else: break

    def single(self, row):
        return self.prefix + row.raw + self.suffix


def _write(path, raw):
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    except OSError as error:
        raise ProjectionEvidenceError(str(error)) from error


def _json(path, value):
    _write(path, (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode())


def _file(path):
    try:
        import fcntl
        fd = os.open(path, os.O_RDONLY)
        try:
            st = os.fstat(fd)
            physical = fcntl.fcntl(fd, fcntl.F_GETPATH, b'\0' * 1024).split(b'\0', 1)[0].decode()
            with os.fdopen(os.dup(fd), 'rb') as stream:
                digest = _sha(stream.read())
            return {'physical_path': physical, 'device': st.st_dev, 'inode': st.st_ino, 'sha256': digest}
        finally:
            os.close(fd)
    except (OSError, RuntimeError) as error:
        return {'error': type(error).__name__, 'errno': getattr(error, 'errno', None), 'path': str(path.absolute())}


class _Guard:
    def __init__(self):
        self.paths = {}; self.trees = {}

    def add(self, path):
        path = Path(path).absolute(); name = str(path)
        now = _file(path)
        if name in self.paths and self.paths[name] != now:
            raise ProjectionInputChanged('Input changed during preparation: ' + name)
        self.paths[name] = now

    def tree(self, path, excluded=()):
        path = Path(path).absolute()
        names = self._names(path, excluded)
        key = str(path)
        if key in self.trees and self.trees[key]['names'] != names:
            raise ProjectionInputChanged('Input inventory changed: ' + key)
        self.trees[key] = {'excluded': list(excluded), 'names': names}
        for name in names: self.add(path / name)

    @staticmethod
    def _names(path, excluded):
        found = []
        for directory, dirs, names in os.walk(path):
            dirs[:] = sorted(d for d in dirs if d not in excluded)
            found.extend(str((Path(directory) / n).relative_to(path)) for n in sorted(names))
        return sorted(found)

    def snapshot(self):
        return {'files': copy.deepcopy(self.paths), 'inventories': copy.deepcopy(self.trees)}

    def verify(self):
        for name, value in self.paths.items():
            if _file(Path(name)) != value: raise ProjectionInputChanged('Projection input changed: ' + name)
        for name, value in self.trees.items():
            if self._names(Path(name), value['excluded']) != value['names']:
                raise ProjectionInputChanged('Projection input inventory changed: ' + name)


def _child(project, name):
    path = (project / name).resolve()
    if not path.is_relative_to(project.resolve()): raise ValueError('Declared path escapes project: ' + name)
    return path


def _process(argv, evidence, label, *, env, cwd, data=None):
    run_id = uuid.uuid4().hex
    record = {'runId': run_id, 'argv': list(map(str, argv)), 'cwd': str(cwd)}
    try:
        p = subprocess.run(record['argv'], cwd=cwd, env=env, input=data, capture_output=True, timeout=180)
        record['exit_code'] = p.returncode
        stdout, stderr = p.stdout, p.stderr
    except (OSError, subprocess.TimeoutExpired) as error:
        record.update(exit_code=None, error=str(error)); stdout = getattr(error, 'stdout', None) or b''; stderr = getattr(error, 'stderr', None) or b''
    _write(evidence / (label + '.stdout.log'), stdout); _write(evidence / (label + '.stderr.log'), stderr)
    record.update(stdout_sha256=_sha(stdout), stderr_sha256=_sha(stderr))
    _json(evidence / (label + '.process.json'), record)
    return record, stdout, stderr


def _section(raw, anchor):
    """Title anchor, bytes from the heading through the next same/higher heading."""
    lines = raw.splitlines(keepends=True); headings = []
    def slug(title):
        return '-'.join(''.join(c.lower() for c in title if c.isalnum() or c in ' _-').split())
    for i, line in enumerate(lines):
        text = line.decode('utf-8').strip()
        count = len(text) - len(text.lstrip('#'))
        if 1 <= count <= 6 and text[count:count + 1] == ' ':
            title = text[count:].strip().rstrip('#').rstrip()
            headings.append((i, count, title, slug(title)))
    wanted = anchor.lstrip('#')
    matches = [h for h in headings if wanted in (h[2], h[3])]
    if len(matches) != 1: raise ValueError('Missing/ambiguous mapping title anchor')
    line, depth, _, _ = matches[0]
    end = next((h[0] for h in headings if h[0] > line and h[1] <= depth), len(lines))
    return b''.join(lines[line:end])


def _swift_source(project, guard, evidence, env):
    from .source import Source, config
    from hmigbot_ios.apple_tools import provider
    cfg = config(project); ios = cfg.get('ios', {})
    root = ios.get('source_root') if isinstance(ios, dict) else ios
    root = root or cfg.get('android')
    if not isinstance(root, str) or not root: raise ValueError('Native source root is not configured')
    root = (project / root).resolve()
    guard.add(project / '.migbot/config.json'); guard.tree(root, ('.git', 'DerivedData', '.build'))
    guard.add(project / 'spec/ref/ios-source-view.json')
    views = project / 'spec/ref/source-views'
    if views.is_dir(): guard.tree(views)
    source = Source(root, project)
    inputs = []
    for name in sorted(p for p in source.files if p.endswith('.swift')):
        text = source.view.text(name) if source.view else (root / name).read_text(encoding='utf-8-sig')
        inputs.append({'path': name, 'source': text, 'sha256': _sha(text.encode())})
    binary, info, apple_env = provider()
    guard.add(binary); guard.add(binary.parent / 'build.json'); guard.add(info['swiftc'])
    for name in ('libSwiftSyntax.dylib', 'libSwiftParser.dylib', 'libSwiftDiagnostics.dylib', 'libSwiftIfConfig.dylib'):
        guard.add(Path(info['host_libraries']) / name)
    provider_root = Path(__file__).resolve().parents[2] / 'providers/swift-syntax'
    guard.tree(provider_root)
    request = (json.dumps({'files': inputs}, ensure_ascii=False) + '\n').encode()
    _write(evidence / 'swift.request.json', request)
    process, stdout, _ = _process([binary], evidence, 'swift', env=apple_env, cwd=project, data=request)
    if process['exit_code'] != 0: raise ValueError('Official SwiftSyntax process failed')
    value = json.loads(stdout)
    if value.get('provider') != 'SwiftSyntax' or value.get('schema_version') != 2 or value.get('semantic_resolution') is not False:
        raise ValueError('Unexpected existing SwiftSyntax protocol')
    expected = {x['path']: x for x in inputs}; facts = {}
    for item in value.get('files', []):
        name = item.get('path')
        if name not in expected or name in facts or item.get('sha256') != expected[name]['sha256'] or item.get('parse_has_error') is not False:
            raise ValueError('Stale/invalid official Swift input')
        if not source.view and any(n['kind'] == 'conditional_compilation' for n in item['nodes']):
            raise ValueError('Configured Release source view required')
        facts[name] = item
    if set(expected) != set(facts): raise ValueError('SwiftSyntax omitted selected source')
    return source, facts


def _source_proof(row, facts):
    location = row.get('src', '').rsplit(':', 1)
    if len(location) != 2 or not location[1].isdigit() or location[0] not in facts:
        raise ValueError('Original source row has no selected Swift source')
    fact = facts[location[0]]
    nodes = [n for n in fact['nodes'] if n['kind'] == 'visibility' and n['line'] == int(location[1])
             and n['value'].get('expression') == row.get('expression') and n['value'].get('drivers') == row.get('drivers')
             and n['value'].get('owner') == row.get('screen') and n['value'].get('form') == 'if']
    if len(nodes) != 1: raise ValueError('Original row does not identify one official visibility range')
    node = nodes[0]; start, end = node['start_utf8'], node['end_utf8']
    tokens = [t for t in fact['tokens'] if t['start_utf8'] >= start and t['end_utf8'] <= end]
    if not tokens or tokens[0]['start_utf8'] != start or tokens[-1]['end_utf8'] != end:
        raise ValueError('Official source tokens do not cover visibility range')
    words = [t['value'] for t in tokens]
    if len(words) < 7 or words[:2] != ['if', 'let'] or tokens[2]['kind'] != 'identifier' or words[3] != '=':
        raise ValueError('Source is not one explicit if let')
    opening = words.index('{')
    predicate = tokens[4:opening]
    if not predicate or any(t['kind'] != 'identifier' if i % 2 == 0 else t['value'] != '.' for i, t in enumerate(predicate)) or len(predicate) % 2 == 0:
        raise ValueError('Source optional initializer is not one member path')
    if [t['value'].strip('`') for t in predicate[::2]] != row['drivers']:
        raise ValueError('Source member path does not cover the complete original predicate')
    def close(index):
        depth = 0
        for i in range(index, len(words)):
            if words[i] == '{': depth += 1
            elif words[i] == '}':
                depth -= 1
                if depth == 0: return i
        raise ValueError('Unclosed official source branch')
    stop = close(opening); branches = [(opening, stop)]; has_else = stop + 1 < len(words)
    if has_else:
        if words[stop + 1:stop + 3] != ['else', '{']: raise ValueError('Source else-if/unsupported tail')
        last = close(stop + 2)
        if last != len(words) - 1: raise ValueError('Unsupported source tail')
        branches.append((stop + 2, last))
    # The existing provider emits actual call nodes; these are the same SDK UI
    # constructors consumed by its native UI outline, never comment matches.
    ui = {'Text', 'Label', 'Image', 'Button', 'Toggle', 'TextField', 'SecureField', 'List', 'ScrollView',
          'VStack', 'HStack', 'ZStack', 'NavigationStack', 'NavigationLink', 'TabView', 'Picker', 'ForEach'}
    for left, right in branches:
        if not any(n['kind'] == 'call' and n['value'].get('callee') in ui and
                   n['start_utf8'] > tokens[left]['start_utf8'] and n['end_utf8'] <= tokens[right]['end_utf8'] for n in fact['nodes']):
            raise ValueError('Source branch has no provider UI call')
    return {'file': location[0], 'visibility': node, 'has_else': has_else, 'whole_predicate': row['drivers']}


@dataclass
class BindingMeasurement:
    result: dict
    rows: list
    signature: dict
    _guard: object = field(repr=False)

    def verify(self) -> None:
        self._guard.verify()


def measure_binding_projection(*, project: Path, engine: Path, scripts_dir: Path, evidence: Path,
                               env: dict, declaration: Declaration, original_binding: dict) -> BindingMeasurement:
    project, engine, scripts_dir, evidence = map(Path, (project, engine, scripts_dir, evidence))
    if evidence.resolve().is_relative_to(project.resolve()):
        raise ProjectionEvidenceError('Projection measurement evidence must be outside project')
    run_id = uuid.uuid4().hex
    guard = _Guard(); guard.add(declaration.path)
    if _file(declaration.path).get('sha256') != declaration.sha256:
        raise ProjectionInputChanged('Declaration changed after loading')
    loaded = load_declarations(project)
    if loaded is None or loaded.data != declaration.data:
        raise ProjectionInputChanged('Declaration object differs from formal input')
    guard.add(project / 'spec/baseline/ui/visibility-bindings.json')
    guard.add(project / '.migbot/config.json'); guard.add(project / 'build-profile.json5'); guard.add(project / 'local.properties')
    guard.add(engine); guard.add(Path(__file__)); guard.add(Path(__file__).with_name('binding_projection_sdk.cjs'))
    guard.add(Path(__file__).with_name('ets_components.cjs'))
    manifest_path = project / 'spec/baseline/ui/visibility-bindings.json'
    native_safe_failure = bool(original_binding.get('error')) and any(
        x.get('kind') == 'binding-gate-not-run' and x.get('severity') == 'FAIL' for x in original_binding.get('findings', []))
    native_manifest_failure = original_binding.get('passed') is False and any(
        x.get('kind') == 'binding-manifest-broken' for x in original_binding.get('findings', []))
    native_skip_reason = ('跳过投影，原因是manifest损坏' if native_manifest_failure else
                          'Native safe-detector binding failure; entire class retained without projection' if native_safe_failure else None)
    try:
        manifest = ManifestRows(manifest_path.read_bytes()) if manifest_path.is_file() and not native_skip_reason else None
    except (OSError, ValueError, UnicodeError, IndexError) as error:
        if any(x.get('kind') == 'binding-manifest-broken' for x in original_binding.get('findings', [])) and not any(
                x.get('kind') == 'binding-dropped' for x in original_binding.get('findings', [])):
            manifest = None  # The native non-runtime FAIL is retained verbatim.
        else:
            raise ProjectionMeasurementError('Cannot reconstruct native manifest runtime rows') from error
    declarations = {x['source_row_index']: x for x in copy.deepcopy(declaration.data)['projections']}
    # Freeze every formally referenced input before any native measurement.
    reference_errors = {}
    for index, item in declarations.items():
        try:
            guard.add(_child(project, item['mapping_ref']['file']))
            proof = item['proof']
            for selector in [proof['producer'], proof['extension'], proof['receiver'], *proof['render']]:
                guard.add(_child(project, selector['file']))
            guard.add(_child(project, proof['extension']['form_profile']))
        except ValueError as error:
            reference_errors[index] = str(error)
    from importlib.util import spec_from_file_location, module_from_spec
    helper_path = scripts_dir / 'wiring_source.py'
    spec = spec_from_file_location('_binding_projection_wiring_helpers', helper_path)
    helper = module_from_spec(spec); spec.loader.exec_module(helper)
    target_files = helper.source_files(project)
    for path in target_files: guard.add(path)
    ets_roots = set()
    for path in target_files:
        parts = path.relative_to(project).parts
        index = next(i for i in range(len(parts) - 2) if parts[i:i + 3] == ('src', 'main', 'ets'))
        ets_roots.add(project.joinpath(*parts[:index + 3]))
    for root in ets_roots: guard.tree(root)
    target_inventory = tuple(map(str, target_files))
    # Native source/config and selected SDK must be frozen before measuring.
    swift = sdk = None; preparation_errors = []
    if declarations and not native_skip_reason:
        try: swift = _swift_source(project, guard, evidence, env)
        except (ProjectionInputChanged, ProjectionEvidenceError): raise
        except Exception as error: preparation_errors.append('source: ' + str(error))
        try:
            node, parser, selection = helper.sdk_runtime(project)
            loader = next(p for p in (parser, *parser.parents) if p.name == 'ets-loader')
            sdk_root = loader.parent.parent
            for path in [node, Path(selection['package']), loader / 'tsconfig.json']: guard.add(path)
            guard.tree(parser if parser.is_dir() else parser.parent)
            # Imported SDK declaration closure and its additions are guarded.
            for name in ('api', 'kits', 'component'):
                if (sdk_root / name).is_dir(): guard.tree(sdk_root / name)
            guard.tree(loader / 'declarations')
            guard.tree(loader / 'node_modules/json5')
            companion = sdk_root.parent.parent / 'hms/ets'
            if companion.is_dir():
                for name in ('api', 'kits', 'component'):
                    if (companion / name).is_dir(): guard.tree(companion / name)
            for module in project.glob('*/src/main/module.json5'): guard.add(module)
            for profile in project.glob('*/src/main/resources/base/profile/*.json*'): guard.add(profile)
            sdk = (node, parser, selection, sdk_root)
        except (ProjectionInputChanged, ProjectionEvidenceError): raise
        except Exception as error: preparation_errors.append('SDK: ' + str(error))
    _json(evidence / 'signature-before.json', guard.snapshot())
    if native_skip_reason:
        rows = [{'index': index, 'proof': 'skipped', 'proof_error': native_skip_reason, 'final_status': 'unchanged'}
                for index in declarations]
        guard.verify(); signature = guard.snapshot(); result = copy.deepcopy(original_binding)
        _json(evidence / 'measurement.json', {'runId': run_id, 'native_binding_projection_skipped': native_skip_reason,
              'rows': rows, 'result': result, 'signature': signature, 'limitations': ['未经设备验证']})
        return BindingMeasurement(result, rows, signature, guard)
    fresh = []; rows = []
    runtime = lambda result: [x for x in result.get('findings', []) if x.get('kind') == 'binding-dropped']
    for row in manifest.rows if manifest else []:
        if not isinstance(row.value, dict) or row.value.get('kind') != 'runtime-toggle': continue
        selected = evidence / ('row-' + str(row.index) + '.manifest.json')
        _write(selected, manifest.single(row))
        output = evidence / ('row-' + str(row.index) + '.json')
        argv = [str(engine), 'binding_gate', '--project-root', str(project), '--manifest', str(selected), '--output-json', str(output)]
        process, _, _ = _process(argv, evidence, 'row-' + str(row.index), env=env, cwd=project)
        if process['exit_code'] not in (0, 1) or not output.is_file():
            # No safe way to establish aggregate equivalence from a crashed
            # measurement: fail closed before canonical, never erase failures.
            raise ProjectionMeasurementError('Native per-row binding measurement failed: ' + str(row.index))
        try: result = json.loads(output.read_bytes())
        except (OSError, ValueError) as error: raise ProjectionMeasurementError('Incomplete row measurement') from error
        findings = runtime(result)
        if len(findings) > 1 or any(x.get('severity') != 'FAIL' for x in findings):
            raise ProjectionMeasurementError('Unexpected native runtime row shape')
        fresh.extend(findings)
        record = {'index': row.index, 'raw_row_sha256': _sha(row.raw), 'original_status': 'FAIL' if findings else 'PASS',
                  'remeasured': True, 'binding_exit_code': process['exit_code'], 'original_process': process,
                  'findings': findings, 'proof': 'not-declared', 'final_status': 'FAIL' if findings else 'PASS', 'proof_error': None}
        rows.append(record)
    if fresh != runtime(original_binding):
        raise ProjectionMeasurementError('Fresh runtime row aggregate differs from current native backend')
    _json(evidence / 'runtime-equivalence.json', {'runId': run_id, 'equal': True, 'fresh_runtime_findings': fresh})
    final_runtime = []; proved = 0
    for record in rows:
        item = declarations.get(record['index']); row = manifest.rows[record['index']]
        if item:
            try:
                if record['index'] in reference_errors: raise ValueError(reference_errors[record['index']])
                if row.value.get('kind') != 'runtime-toggle': raise ValueError('Declared row is not runtime-toggle')
                if item['source_row_sha256'] != record['raw_row_sha256']: raise ValueError('Stale source row SHA256')
                ref = item['mapping_ref']; section = _section(_child(project, ref['file']).read_bytes(), ref['anchor'])
                if _sha(section) != ref['section_sha256']: raise ValueError('Stale mapping section SHA256')
                if ('projection-id:' + item['id']).encode() not in section: raise ValueError('Missing mapping reverse projection-id')
                if item['proof']['kind'] != 'harmony-form-optional-presence.v1': raise ValueError('Unsupported proof kind')
                if preparation_errors: raise ValueError('; '.join(preparation_errors))
                source_fact = _source_proof(row.value, swift[1])
                node, parser, selection, sdk_root = sdk
                request = {'runId': run_id + '-' + str(row.index), 'project': str(project.resolve()), 'files': list(map(str, target_files)),
                           'parserModule': str(parser), 'sdkSelection': selection, 'proof': item['proof'], 'sourceHasElse': source_fact['has_else']}
                _json(evidence / ('proof-' + str(row.index) + '.request.json'), request)
                process, stdout, _ = _process([node, Path(__file__).with_name('binding_projection_sdk.cjs')], evidence, 'proof-' + str(row.index),
                                              env=env, cwd=project, data=json.dumps(request).encode())
                if process['exit_code'] != 0: raise ValueError('Official SDK proof process failed')
                proof = json.loads(stdout)
                context = proof.get('componentContext')
                if context is not None:
                    helper_file = Path(__file__).with_name('ets_components.cjs')
                    helper_record = context.get('helper', {})
                    if (helper_record.get('file') != str(helper_file) or
                            helper_record.get('sha256') != _file(helper_file).get('sha256')):
                        raise ProjectionInputChanged('ETS component context helper identity changed')
                    for dependency in context.get('files', []):
                        path = Path(dependency['file'])
                        if _file(path).get('sha256') != dependency.get('sha256'):
                            raise ProjectionInputChanged('ETS component dependency changed: ' + str(path))
                        guard.add(path)
                if proof.get('runId') != request['runId'] or proof.get('proved') is not True:
                    raise ValueError('SDK proof: ' + str(proof.get('error', 'unproved')))
                record.update(proof='proved', source_proof=source_fact, sdk_proof=proof)
                if record['original_status'] == 'FAIL':
                    record['final_status'] = 'PASS'; proved += 1
            except (ProjectionInputChanged, ProjectionEvidenceError): raise
            except Exception as error:
                record.update(proof='unproved', proof_error=str(error))
        if record['final_status'] == 'FAIL': final_runtime.extend(record['findings'])
    for index, item in declarations.items():
        if not manifest or index >= len(manifest.rows) or not isinstance(manifest.rows[index].value, dict) or manifest.rows[index].value.get('kind') != 'runtime-toggle':
            rows.append({'index': index, 'proof': 'unproved', 'proof_error': 'Declared row absent or not runtime-toggle', 'final_status': 'unchanged'})
    # Rebuild the runtime category from independent measurements. Preserve the
    # current non-runtime records and their positions in the original schema.
    merged = []; measured_slots = iter([r for r in rows if 'findings' in r for _ in r['findings']])
    for finding in original_binding.get('findings', []):
        if finding.get('kind') == 'binding-dropped':
            measured_row = next(measured_slots)
            if measured_row['final_status'] == 'FAIL': merged.extend(copy.deepcopy(measured_row['findings']))
        else: merged.append(copy.deepcopy(finding))
    result = copy.deepcopy(original_binding); result['findings'] = merged
    summary = result.get('summary')
    if isinstance(summary, dict):
        for level in ('FAIL', 'WARN', 'INFO'):
            if level in summary: summary[level] = sum(x.get('severity') == level for x in merged)
        if 'total' in summary: summary['total'] = len(merged)
    if 'pass' in result: result['pass'] = not any(x.get('severity') == 'FAIL' for x in merged)
    if 'passed' in result: result['passed'] = not any(x.get('severity') == 'FAIL' for x in merged)
    assert len(final_runtime) == len(fresh) - proved
    if tuple(map(str, helper.source_files(project))) != target_inventory:
        raise ProjectionInputChanged('Target module source inventory changed')
    guard.verify()
    signature = guard.snapshot()
    _json(evidence / 'measurement.json', {'runId': run_id, 'rows': rows, 'result': result, 'signature': signature,
          'limitations': ['未经设备验证', 'Static syntax/symbol/dataflow proof only; not a target build, delivery, timing, visual or text-equivalence proof',
                          'Source payload to target parameter semantics relies on approved mapping_ref']})
    return BindingMeasurement(result, rows, signature, guard)
