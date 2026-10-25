"""Pinned, shared configured-source views; never rewrite the iOS input tree.

Xcode provides merged settings. SwiftIfConfig provides syntax and selection.
Existing evidence, atomic-provider and project-membership modules retain ownership
of their contracts. This adapter supports custom Boolean Swift conditions only.
"""
from pathlib import Path
import re
import shlex

from .core import MigrationError, digest, json_bytes, read_json, safe_child, snapshot, write_json
from .providers import invoke_json_provider

POINTER = 'spec/ref/ios-source-view.json'
CODE = {'.swift', '.m', '.mm', '.c', '.cpp'}


def require(value, message):
    if not value:
        raise MigrationError(message)


def conditions(settings):
    """Normalize resolved flags only; this is deliberately not an xcconfig merger."""
    def tokens(key):
        value = settings.get(key, '')
        require(isinstance(value, (str, list)), 'Invalid ' + key)
        if isinstance(value, list):
            require(all(isinstance(x, str) for x in value), 'Invalid flag array')
            value = ' '.join(value)
        require('$' not in value and '@' not in value, 'Unexpanded or response-file Swift flags require captured compiler context')
        try:
            return shlex.split(value)
        except ValueError as exc:
            raise MigrationError('Malformed Swift flag quoting') from exc
    active = tokens('SWIFT_ACTIVE_COMPILATION_CONDITIONS')
    flags = tokens('OTHER_SWIFT_FLAGS')
    for i, flag in enumerate(flags):
        if flag == '-D':
            require(i + 1 < len(flags), 'Missing -D condition')
            active.append(flags[i + 1])
        elif flag.startswith('-D'):
            active.append(flag[2:])
        elif flag in {'-Xfrontend', '-Xswiftc', '-target', '-sdk', '-swift-version'}:
            raise MigrationError('Context-changing Swift flags require a supported compiler capture')
    require(all(re.fullmatch(r'[A-Za-z_][A-Za-z_0-9]*', x) for x in active), 'Invalid custom Swift condition')
    return sorted(set(active))


def validate_capture(source, bundle, variant):
    """Validate imported query integrity and matching source/configuration bytes."""
    supplied = {}
    for line in (bundle / 'bundle-files.sha256').read_text(encoding='utf-8-sig').splitlines():
        parts = line.split('  ', 1)
        require(len(parts) == 2 and re.fullmatch('[0-9a-f]{64}', parts[0]), 'Invalid capture file map')
        sha, name = parts
        require(name not in supplied, 'Duplicate captured artifact')
        require(digest(safe_child(bundle, name).read_bytes()) == sha, 'Modified Mac artifact: ' + name)
        supplied[name] = sha
    required = {'release-build-settings.json', 'source-files.json', 'command-execution-records.json'}
    require(required <= supplied.keys(), 'Mac capture omitted required hashed inputs')
    files = read_json(bundle / 'source-files.json')['files']
    captured = {}
    for file in files:
        name = file['path']
        require(name not in captured and file.get('kind') == 'file', 'Invalid source identity entry')
        path = safe_child(source, name)
        require(path.is_file() and digest(path.read_bytes()) == file['sha256'], 'Mac/local source differs: ' + name)
        require(path.stat().st_size == file['size_bytes'], 'Mac/local source size differs: ' + name)
        captured[name] = file['sha256']
    require(set(variant['source_files']) <= captured.keys(), 'Capture omitted selected source members')
    # Bind every source configuration, not only files appearing in the selected
    # target. An added xcconfig/scheme/lockfile may change the effective query.
    for file in snapshot(source)['files']:
        name = file['path']
        if (Path(name).suffix in CODE | {'.h'}
                or name.endswith(('.pbxproj', '.xcconfig', '.xcscheme', '.xcworkspacedata', '.xcsettings'))
                or Path(name).name in {'Package.swift', 'Package.resolved', 'Podfile', 'Podfile.lock', 'Cartfile', 'Cartfile.resolved'}):
            require(captured.get(name) == file['sha256'], 'Capture omitted current build input: ' + name)
    records = read_json(bundle / 'command-execution-records.json')
    commands = [c for c in records['commands'] if c.get('id') == 'release-build-settings']
    require(len(commands) == 1, 'Expected one recorded Xcode settings query')
    command = commands[0]
    require(command.get('exit_code') == 0 and command.get('timed_out') is False, 'Xcode query failed')
    args = command.get('argv', [])
    require('-showBuildSettings' in args and '-json' in args, 'Not an Xcode JSON settings query')
    for flag, value in (('-configuration', variant['configuration']), ('-sdk', 'iphoneos')):
        require(args.count(flag) == 1 and args[args.index(flag) + 1] == value, 'Wrong Xcode query ' + flag)
    require('-project' in args and Path(args[args.index('-project') + 1]).name == Path(variant['project_path']).parent.name,
            'Xcode query does not identify selected project')
    require(command.get('stdout') == 'release-build-settings.json', 'Unexpected Xcode stdout artifact')
    for stream in ('stdout', 'stderr'):
        name = command[stream]
        require(name in supplied and digest(safe_child(bundle, name).read_bytes()) == command[stream + '_sha256'],
                'Changed Xcode query stream')
    return command, captured


def prepare(project, source, bundle, provider_config, variant, output, *, migration_scope=False):
    from .project_scope import resolve
    from .evidence import pack
    from .atoms import run_atom
    project, source, bundle, output = map(lambda p: Path(p).resolve(), (project, source, bundle, output))
    require(output.is_relative_to(project / 'spec/ref/source-views') and output != project / 'spec/ref/source-views',
            'Capture source views under project/spec/ref/source-views/<run>')
    require(not output.exists(), 'Source-view capture is immutable; choose a new run directory')
    require(variant.get('scope') == 'project-targets' and variant.get('configuration') == 'Release',
            'Configured source requires explicit project-targets Release selection')
    resolved, context = resolve(source, variant, _context=True)
    analysis_members = set(resolved['source_files'])
    if migration_scope:
        from hmigbot_ios152.source import migration_members
        analysis_members = migration_members(source, resolved)
    try:
        command, source_hashes = validate_capture(source, bundle, resolved)
    except (KeyError, IndexError, TypeError, OSError) as exc:
        raise MigrationError('Malformed Mac configuration capture: ' + str(exc)) from exc
    before = snapshot(source)
    output.mkdir(parents=True)
    try:
        pack(source, bundle, output / 'evidence', 'source_build_settings', 'imported-xcode-settings-query')
        normalized = run_atom('build-settings', source, output / 'build-settings', input_path=output / 'evidence')
        targets, target_conditions, target_compilers = {}, {}, {}
        from .mac_capture import compiler_context
        raw_settings=read_json(bundle/'release-build-settings.json')
        flag_checks=[]
        declared_modules=[t['settings'].get('PRODUCT_MODULE_NAME') or t['target'] for t in normalized['data']['targets']]
        selected_targets=set(resolved['target_closure'])
        if provider_config is None:
            from .apple_tools import provider
            binary, toolchain, _ = provider()
            provider_config=output / 'provider/config.json'
            write_json(provider_config, {'command':[str(binary),'--conditional-source'],
                'version_command':[toolchain['swiftc'],'--version'],'timeout_seconds':120})
        for target in normalized['data']['targets']:
            name, settings = target['target'], target['settings']
            if name not in selected_targets:
                continue
            require(isinstance(name, str) and name not in targets, 'Duplicate or invalid Xcode target')
            require(settings.get('CONFIGURATION') == 'Release' and settings.get('PLATFORM_NAME') == 'iphoneos',
                    'Expected iOS Release settings')
            require(settings.get('SWIFT_VERSION') in {'4','4.0','5','5.0','6','6.0'}, 'Unsupported Swift language mode')
            applicable = [c for c in context.selected_configs if c['owner'] in {'project', name}]
            missing_base_flags=False
            for key in ('SWIFT_ACTIVE_COMPILATION_CONDITIONS', 'OTHER_SWIFT_FLAGS'):
                require(not any(t.get('target')==name and key in t['buildSettings'] for t in raw_settings) or key in settings,
                        'Normalized Xcode settings omitted an original Swift flag: '+key)
                if key not in settings:
                    if any(c['base_path'] is not None for c in applicable):
                        missing_base_flags=True
                    else:
                        require(all(c['settings'].get(key) in (None, '', []) for c in applicable),
                                'Xcode export omitted a configured Swift flag: '+key)
            targets[name], target_conditions[name] = settings, conditions(settings)
            actual_arguments=None
            if missing_base_flags or (bundle/'compiler-arguments.json').is_file():
                from .mac_capture import verify_unset_flags
                checked=verify_unset_flags(bundle,settings,target_conditions[name])
                flag_checks.append(checked)
                actual_arguments=checked['compiler_arguments']
            target_compilers[name] = compiler_context(settings,target_conditions[name],declared_modules,actual_arguments)
        batches = {}
        for member in resolved['source_membership']:
            if member['path'] not in analysis_members:
                continue
            if not member['path'].endswith('.swift'):
                continue
            require(set(member['targets']) <= targets.keys(), 'Xcode query omitted a selected target')
            sets = {(tuple(target_conditions[t]),json_bytes(target_compilers[t]).decode()) for t in member['targets']}
            require(len(sets) == 1, 'Shared source has differing target compiler contexts; separate target analyses are required')
            batches.setdefault(next(iter(sets)), []).append(member['path'])
        require(batches, 'No selected Swift sources')
        files, inputs = [], {}
        for index, ((custom, compiler_json), paths) in enumerate(sorted(batches.items())):
            import json
            request = {'schema_version': 2, 'custom_conditions': list(custom), 'conditions_complete': True,
                       'compiler_context':json.loads(compiler_json),
                       'files': [{'path': p, 'source': safe_child(source, p).read_bytes().decode('utf-8-sig')} for p in sorted(paths)]}
            response, run, stdout, stderr = invoke_json_provider(provider_config, request)
            require(isinstance(response, dict) and response.get('stage') == 'official-swift-if-config'
                    and response.get('evidence') == 'compiler-backed-conditions'
                    and response.get('schema_version') == 2
                    and response.get('provider_build') == 'xcode-toolchain', 'Unexpected conditional-provider protocol')
            result = response.get('files')
            require(isinstance(result, list) and len(result) == len(paths), 'Conditional provider omitted source files')
            seen = set()
            for file in result:
                name = file.get('path')
                require(name in paths and name not in seen, 'Unknown/duplicate conditional source')
                seen.add(name)
                require(file.get('status') == 'resolved' and not file.get('diagnostics'),
                        'Conditional source remains unresolved: ' + str(name) + ': ' + str(file.get('diagnostics')))
                original = safe_child(source, name).read_bytes().decode('utf-8-sig').encode()
                text = file.get('filtered_source')
                require(isinstance(text, str), 'Missing conditional source text')
                body = text.encode()
                require(len(body) == len(original) and all(a == b or b == 32 and a not in (10, 13)
                        for a, b in zip(original, body)), 'Provider changed original source offsets or active bytes')
                view = 'views/' + name
                path = safe_child(output, view)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(body)
                files.append({'path': name, 'sha256': source_hashes[name], 'view': view,
                    'view_sha256': digest(body), 'regions': file.get('regions', []), 'custom_conditions': list(custom)})
            for suffix, body in (('request.json', json_bytes(request)), ('response.json', stdout),
                                 ('stderr.log', stderr), ('run.json', json_bytes(run))):
                name = f'provider/{index}/{suffix}'
                path = safe_child(output, name)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(body)
                inputs[name] = digest(body)
        require(snapshot(source)['sha256'] == before['sha256'], 'Source changed during conditional capture')
        for name in ('evidence/manifest.json', 'build-settings/artifact.json'):
            inputs[name] = digest(safe_child(output, name).read_bytes())
        artifact = {'schema_version': 1, 'source_sha256': before['sha256'], 'variant': resolved,
            'evidence': 'configured_parser_syntax', 'effective_build': 'unresolved', 'behavior_verified': False,
            'query_scope': 'Recorded Xcode settings query; not an actual compiler/archive invocation',
            'settings_targets': targets, 'files': sorted(files, key=lambda f: f['path']), 'inputs': inputs,
            'compiler_argument_checks':flag_checks,
            'query_command': command['argv']}
        if migration_scope:
            artifact['analysis_source_files'] = sorted(analysis_members)
        write_json(output / 'artifact.json', artifact)
        reference = {'path': (output / 'artifact.json').relative_to(project).as_posix(),
                     'sha256': digest((output / 'artifact.json').read_bytes())}
        SourceView(source, project, reference)  # Validate everything before publishing the active pointer.
        write_json(project / POINTER, reference)
        return {'status': 'prepared', 'source_sha256': before['sha256'], 'source_view': reference,
                'files': len(files), 'conditional_files': sum(bool(f['regions']) for f in files),
                'effective_build': 'unresolved', 'behavior_verified': False}
    except (MigrationError, OSError, ValueError, KeyError, TypeError) as exc:
        write_json(output / 'failure.json', {'status': 'failed', 'error': str(exc), 'active_pointer_updated': False})
        if isinstance(exc, MigrationError): raise
        raise MigrationError('Conditional capture failed: ' + str(exc)) from exc


class SourceView:
    def __init__(self, source, project, reference):
        from .evidence import validate
        self.source = Path(source).resolve()
        self.reference = reference
        require(isinstance(reference, dict) and set(reference) == {'path', 'sha256'}, 'Invalid source-view reference')
        artifact_path = safe_child(project, reference['path'])
        require(artifact_path.is_relative_to(Path(project).resolve() / 'spec/ref/source-views'), 'Source-view reference escapes pinned captures')
        require(digest(artifact_path.read_bytes()) == reference['sha256'], 'Source-view capture changed')
        self.root = artifact_path.parent
        self.artifact = read_json(artifact_path)
        require(self.artifact.get('schema_version') == 1 and self.artifact.get('source_sha256') == snapshot(source)['sha256'],
                'Source-view capture is stale')
        for name, sha in self.artifact['inputs'].items():
            require(digest(safe_child(self.root, name).read_bytes()) == sha, 'Source-view evidence changed: ' + name)
        validate(source, self.root / 'evidence')
        self.files = {}
        for file in self.artifact['files']:
            name = file['path']
            require(name not in self.files and digest(safe_child(source, name).read_bytes()) == file['sha256'], 'Stale/duplicate source-view file')
            path = safe_child(self.root, file['view'])
            require(digest(path.read_bytes()) == file['view_sha256'], 'Filtered source view changed: ' + name)
            self.files[name] = path.read_bytes().decode('utf-8')
        self.members = set(self.artifact.get('analysis_source_files', self.artifact['variant']['source_files']))
        if 'analysis_source_files' in self.artifact:
            from hmigbot_ios152.source import migration_members
            require(self.artifact['analysis_source_files'] == sorted(migration_members(self.source, self.artifact['variant'])),
                    'Migration source projection differs from the selected product declarations')

    def includes(self, path):
        return Path(path).suffix not in CODE or path in self.members

    def text(self, path):
        require(self.includes(path), 'Source is outside selected product: ' + path)
        if path.endswith('.swift'):
            require(path in self.files, 'Missing configured Swift source: ' + path)
            return self.files[path]
        return safe_child(self.source, path).read_bytes().decode('utf-8-sig')


def for_project(project, source):
    path = Path(project) / POINTER
    try:
        if path.exists():
            return SourceView(source, project, read_json(path))
        for name in ('ios-facts.json', 'ios-source-index.json', 'literal-ledger.json'):
            prior = Path(project) / 'spec/baseline' / name
            if prior.exists() and read_json(prior).get('source_view'):
                raise MigrationError('Configured-source pointer is missing; restore or explicitly review the configuration change')
        return None
    except (OSError, KeyError, TypeError, ValueError) as exc:
        raise MigrationError('Invalid configured-source capture: ' + str(exc)) from exc
