"""One conditional-source service composes official Swift and Clang observations.

The current source_build bundle remains the authority for selected membership.
Compiler observations preserve per-unit contexts and original source coordinates.
"""
from pathlib import Path
import json
import tempfile

from .core import MigrationError, digest, json_bytes, read_json, safe_child, source_snapshot, write_json
from . import swift_conditions as swift

KIND = 'compiler_source_views'
VERSION = 2


def _build(source, bundle, expected):
    from .evidence import validate
    from .source_build_membership import validate as membership_validate
    source, bundle = Path(source).resolve(), Path(bundle).resolve()
    checked = validate(source, bundle)
    swift.require(checked['kind'] == 'source_build', 'source_build bundle required')
    manifest = read_json(bundle / 'manifest.json')
    artifacts = bundle / 'artifacts'
    required = {'source-files.json', 'commands.json', 'capture-report.json', 'device-build.stdout.log',
                'build-settings.json', 'build-settings.stdout.log'}
    swift.require({'artifacts/' + name for name in required} <= manifest['artifacts'].keys(), 'build context artifacts missing')
    document = read_json(artifacts / 'source-files.json')
    membership = membership_validate(source, document, capture=artifacts)
    swift.require(membership['membership_status'] == 'complete', 'compiler membership is incomplete')
    if any(name.endswith('.swift') for name in membership['source_files']):
        swift.require('artifacts/swift-toolchain-inputs.json' in manifest['artifacts'],
                      'original Swift toolchain receipt is missing')
        tools = read_json(artifacts / 'swift-toolchain-inputs.json')
        swift.require(isinstance(tools.get('before'), dict) and tools['before'] == tools.get('after')
                      and bool(tools['before']), 'Swift compiler/SDK capture changed during build')
        for name, sha in tools['before'].items():
            swift.require(digest(Path(name).read_bytes()) == sha, 'Swift compiler/SDK changed: ' + name)
    commands = read_json(artifacts / 'commands.json')
    capture = read_json(artifacts / 'capture-report.json')
    builds = [c for c in commands if c.get('name') == 'device-build']
    swift.require(len(builds) == 1 and builds[0].get('exit_code') == 0 and capture.get('commands') == commands and
                  capture.get('source_unchanged') is True and capture.get('build_succeeded') is True and
                  capture.get('source_sha256') == checked['source_sha256'], 'build capture/source identity differs')
    argv = builds[0]['argv']
    selector = '-workspace' if expected['project'].endswith('.xcworkspace') else '-project'
    swift.require(Path(argv[0]).name == 'xcodebuild' and argv[-1] == 'build' and
                  Path(builds[0]['cwd']).resolve() == source and
                  Path(swift.option(argv, selector)).resolve() == safe_child(source, expected['project']) and
                  all(swift.option(argv, '-' + key) == expected[key] for key in ('scheme', 'configuration', 'sdk')),
                  'actual Xcode action differs from requested build context')
    swift.require('** BUILD SUCCEEDED **' in (artifacts / 'device-build.stdout.log').read_text(), 'native build success marker absent')
    swift.require(read_json(artifacts / 'build-settings.json') == json.loads((artifacts / 'build-settings.stdout.log').read_text()),
                  'build settings differ from original Xcode output')
    return {'membership': {**membership, 'selection': document['selection'], 'evidence': document['evidence']},
            'source_sha256': checked['source_sha256'],
            'build_manifest_sha256': digest((bundle / 'manifest.json').read_bytes()), 'artifacts': artifacts}


def _files(folder):
    return {path.relative_to(folder).as_posix(): digest(path.read_bytes()) for path in sorted(folder.rglob('*'))
            if path.is_file() and not {'ModuleCache', 'ProbeCache', 'Clang'}.intersection(path.relative_to(folder).parts)
            and path.name not in {'manifest.json', 'failure.json'}}


def _native_files(data):
    return [{key: item.get(key) for key in ('path', 'sha256', 'status', 'filtered_source', 'regions', 'source_map')}
            for item in data.get('files', [])]


def _semantic_context(context):
    result = dict(context)
    arguments, index = [], 0
    while index < len(context['arguments']):
        value = context['arguments'][index]
        if value == '-module-cache-path':
            arguments.extend([value, '<task-cache>']); index += 2
        else:
            arguments.append('-fmodules-cache-path=<task-cache>' if value.startswith('-fmodules-cache-path=') else value)
            index += 1
    result['arguments'] = arguments
    return result


def _clang(source, path, expected, project):
    if path is None:
        return None
    from .conditional_evidence import validate
    checked = validate(source, Path(path), project=project)
    swift.require(checked['expected_build'] == expected, 'Clang and Swift selected build contexts differ')
    return checked


def capture(source, project, build, output, expected, *, clang=None):
    source, project, output, build = Path(source).resolve(), Path(project).resolve(), Path(output).resolve(), Path(build).resolve()
    swift.require(output.is_relative_to((project / 'spec/ref/ios-conditional-evidence').resolve()) and not output.exists(),
                  'choose a fresh project-local conditional evidence directory')
    swift.require(build.is_relative_to((project / 'spec/ref').resolve()), 'build context must be project-local')
    original = _build(source, build, expected)
    output.mkdir(parents=True)
    try:
        selected = swift.contexts(source, original['artifacts'], original['membership'], expected, output / 'driver-contexts')
        engine = swift.provider(output / 'provider') if selected else None
        results = []
        for index, context in enumerate(selected):
            request, response = swift.run(source, context, engine['binary'], output / ('swift-' + str(index)))
            if response.get('status') == 'unknown':
                results.append({'context': context, 'status': 'unknown', 'error': response.get('error')})
            else:
                swift.observations(request, response, context['id'])
                results.append({'context': context, 'status': 'observed'})
        _clang(source, clang, expected, project)
        swift.require(source_snapshot(source)['sha256'] == original['source_sha256'], 'source changed during conditional capture')
        write_json(output / 'contexts.json', results)
        write_json(output / 'provider.json', engine)
        artifacts = _files(output)
        manifest = {'schema_version': VERSION, 'kind': KIND, 'source_sha256': original['source_sha256'],
                    'build_evidence': str(build), 'build_manifest_sha256': original['build_manifest_sha256'],
                    'expected_build': expected, 'clang_evidence': str(Path(clang).resolve()) if clang else None,
                    'artifacts': artifacts, 'capture_authenticity': 'not_verified', 'behavior_equivalence': 'not_verified'}
        write_json(output / 'manifest.json', manifest)
        checked = validate(source, output, project=project)
        return {'status': 'partial' if checked['unknowns'] else 'captured', 'path': str(output),
                'swift_contexts': len(selected), 'unknowns': checked['unknowns'], 'behavior_verified': False}
    except (MigrationError, OSError, ValueError, KeyError, TypeError) as exc:
        write_json(output / 'failure.json', {'status': 'capture_failed', 'error': str(exc)})
        raise


def validate(source, output, *, project=None):
    source, output = Path(source).resolve(), Path(output).resolve()
    swift.require(not (output / 'failure.json').exists(), 'failed compiler view cannot be consumed')
    if project is not None:
        project = Path(project).resolve()
        swift.require(output.is_relative_to((project / 'spec/ref/ios-conditional-evidence').resolve()), 'view outside project')
    manifest = read_json(output / 'manifest.json')
    swift.require(manifest.get('kind') == KIND and manifest.get('schema_version') == VERSION and
                  manifest.get('capture_authenticity') == 'not_verified' and manifest.get('behavior_equivalence') == 'not_verified',
                  'unsupported compiler view contract')
    for name, expected_sha in manifest['artifacts'].items():
        swift.require(digest(safe_child(output, name).read_bytes()) == expected_sha, 'compiler view artifact changed: ' + name)
    build = Path(manifest['build_evidence']).resolve()
    if project is not None:
        swift.require(build.is_relative_to((project / 'spec/ref').resolve()), 'build outside project')
    original = _build(source, build, manifest['expected_build'])
    swift.require(original['source_sha256'] == manifest['source_sha256'] and
                  original['build_manifest_sha256'] == manifest['build_manifest_sha256'], 'source/build context changed')
    clang = _clang(source, manifest.get('clang_evidence'), manifest['expected_build'], project)
    observed = {name: list(views) for name, views in clang['observed'].items()} if clang else {}
    unknown = []
    contexts = read_json(output / 'contexts.json')
    engine = read_json(output / 'provider.json')
    # Replay the native branch result against live module/bridging context. A
    # mere request/hash acknowledgement cannot establish active source regions.
    with tempfile.TemporaryDirectory(prefix='hmigbot-swift-context-replay-') as temporary:
        scratch = Path(temporary)
        current = swift.contexts(source, original['artifacts'], original['membership'], manifest['expected_build'], scratch / 'contexts')
        swift.require(len(contexts) == len(current), 'captured Swift context set changed')
        if contexts:
            swift.require(isinstance(engine, dict) and Path(engine['binary']).resolve().is_relative_to(output) and
                          digest(Path(engine['binary']).read_bytes()) == engine['binary_sha256'] and
                          digest((ROOT_PROVIDER()).read_bytes()) == engine['source_sha256'], 'Swift conditional provider changed')
            for path, expected in engine['toolchain_libraries'].items():
                swift.require(digest(Path(path).read_bytes()) == expected, 'official Swift host library changed')
        for index, (record, context) in enumerate(zip(contexts, current)):
            recorded = record['context']
            for key in ('id', 'target', 'architecture', 'original_argv', 'files', 'compiler_sha256'):
                swift.require(recorded[key] == context[key], 'Swift driver context changed: ' + key)
            swift.require(_semantic_context(recorded['context']) == _semantic_context(context['context']),
                          'Swift semantic compiler arguments differ from original build')
            request = read_json(output / ('swift-' + str(index)) / 'request.json')
            response = read_json(output / ('swift-' + str(index)) / 'response.json')
            swift.require(request['context'] == recorded['context'], 'Swift context differs from original request')
            swift.require([file['path'] for file in request['files']] == recorded['files'], 'Swift request source set differs from captured driver')
            for file in request['files']:
                raw = safe_child(source, file['path']).read_bytes()
                swift.require(raw == file['source'].encode('utf-8') and digest(raw) == file['sha256'], 'Swift source input changed')
            live_request, live_response = swift.run(source, context, engine['binary'], scratch / ('swift-' + str(index)))
            swift.require(_native_files(response) == _native_files(live_response), 'live Apple compiler/SwiftIfConfig source view changed')
            if record['status'] == 'unknown':
                unknown.extend({'path': name, 'context': recorded['id'], 'diagnostics': [record.get('error')]} for name in recorded['files'])
                continue
            views, unresolved = swift.observations(request, response, recorded['id'])
            for name, values in views.items():
                observed.setdefault(name, []).extend(values)
            unknown.extend(unresolved)
    return {'reference': {'path': str(output), 'manifest_sha256': digest((output / 'manifest.json').read_bytes()),
                          'build_manifest_sha256': original['build_manifest_sha256']},
            'members': original['membership']['source_files'], 'observed': observed,
            'analysis_files': sorted(set(original['membership']['source_files']) | set(observed)),
            'expected_build': manifest['expected_build'], 'unknowns': unknown}


def ROOT_PROVIDER():
    return Path(__file__).resolve().parents[2] / 'providers/swift-conditions/main.swift'


def frozen_inputs(project, output):
    project, output = Path(project).resolve(), Path(output).resolve()
    manifest = read_json(output / 'manifest.json')
    paths = [output / 'manifest.json'] + [safe_child(output, path) for path in manifest['artifacts']]
    build = Path(manifest['build_evidence'])
    paths += [build / 'manifest.json'] + [safe_child(build, path) for path in read_json(build / 'manifest.json')['artifacts']]
    result = {path.relative_to(project).as_posix(): digest(path.read_bytes()) for path in paths}
    if manifest.get('clang_evidence'):
        from .conditional_evidence import frozen_inputs as clang_inputs
        # The shared dispatch validates the nested Clang view with its own
        # dependency/compiler receipts; no unrelated source service is added.
        checked = _clang(Path(read_json(project / '.migbot/config.json')['ios']), manifest['clang_evidence'], manifest['expected_build'], project)
        result.update(clang_inputs(project, {'conditional_evidence': checked['reference']}))
    return result
