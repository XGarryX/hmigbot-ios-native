"""Capture real Xcode context once and feed the existing authoritative consumers."""
from pathlib import Path
import json
import platform
import shlex
import shutil

from .core import MigrationError, digest, read_json, snapshot, write_json
from .apple_capabilities import command

ROOT = Path(__file__).resolve().parents[2]


def selection(source, supplied, output):
    selected = dict(supplied)
    if bool(selected.get('workspace')) == bool(selected.get('project')):
        raise MigrationError('Native analysis needs exactly one selected project or workspace')
    kind = 'workspace' if selected.get('workspace') else 'project'
    argv = ['xcodebuild', '-' + kind, str(source / selected[kind])]
    raw = command(output, 'xcode-list', argv + ['-list', '-json'], cwd=source)
    listing = json.loads(raw).get(kind, {})
    schemes = listing.get('schemes', [])
    if selected.get('scheme'):
        if selected['scheme'] not in schemes:
            raise MigrationError('Selected scheme absent from actual Xcode scheme discovery')
    elif len(schemes) == 1:
        selected['scheme'] = schemes[0]
    elif selected.get('target') in schemes:
        selected['scheme'] = selected['target']
    else:
        raise MigrationError('Analysis needs selection.scheme; actual candidates: ' + ', '.join(schemes))
    configurations = listing.get('configurations', [])
    defaults = []
    if not selected.get('configuration'):
        if 'Debug' in configurations:
            selected['configuration'] = 'Debug'
        elif len(configurations) == 1:
            selected['configuration'] = configurations[0]
        else:
            raise MigrationError('Analysis needs selection.configuration; actual candidates: ' + ', '.join(configurations))
        defaults.append('configuration')
    elif selected['configuration'] not in configurations:
        raise MigrationError('Selected configuration absent from actual Xcode discovery')
    default_arch = 'x86_64' if selected.get('sdk', '').startswith('iphonesimulator') and platform.machine().lower() not in {'arm64', 'aarch64'} else 'arm64'
    for key, default in [('sdk', 'iphoneos'), ('arch', default_arch)]:
        if key not in selected:
            selected[key] = default
            defaults.append(key)
    if 'destination' not in selected:
        selected['destination'] = 'generic/platform=iOS Simulator' if selected['sdk'].startswith('iphonesimulator') else 'generic/platform=iOS'
        defaults.append('destination')
    selected['defaults_applied'] = defaults
    write_json(output / 'selection.json', selected)
    return selected


def swift_provider(source, output):
    compiler = Path(command(output, 'swiftc-location', ['xcrun', '--find', 'swiftc'], cwd=source, timeout=30).decode().strip())
    host = compiler.parent.parent / 'lib/swift/host'
    if not (host / 'SwiftSyntax.swiftmodule').exists() or not (host / 'SwiftParser.swiftmodule').exists():
        raise MigrationError('Installed Swift toolchain has no compatible SwiftSyntax/SwiftParser host modules')
    executable = output / 'swift-syntax-provider'
    main = ROOT / 'providers/swift-syntax/main.swift'
    sdk = command(output, 'macos-sdk', ['xcrun', '--sdk', 'macosx', '--show-sdk-path'], cwd=source, timeout=30).decode().strip()
    argv = [str(compiler), str(main), '-sdk', sdk, '-I', str(host), '-L', str(host),
            '-lSwiftSyntax', '-lSwiftParser', '-lSwiftParserDiagnostics',
            '-Xlinker', '-rpath', '-Xlinker', str(host), '-o', str(executable)]
    command(output, 'swift-syntax-build', argv, cwd=source, timeout=120)
    config = output / 'swift-syntax.json'
    write_json(config, {'command': [str(executable)], 'version_command': ['xcrun', 'swiftc', '--version'],
                        'timeout_seconds': 120, 'provider_source_sha256': digest(main.read_bytes()),
                        'provider_binary_sha256': digest(executable.read_bytes())})
    return config


def capture(source, project, supplied, output, *, need_conditionals=False, timeout=600):
    from .source_build_membership import collect
    from .evidence import pack
    from .conditional_evidence import _dependency_paths, preprocess_argv, FLAGS
    before = snapshot(source)['sha256']
    selected = supplied
    capture_dir = output / 'capture'
    capture_dir.mkdir(parents=True)
    derived = output / 'DerivedData'
    kind = 'workspace' if selected.get('workspace') else 'project'
    base = ['xcodebuild', '-' + kind, str(source / selected[kind]), '-scheme', selected['scheme'],
            '-configuration', selected['configuration'], '-sdk', selected['sdk'],
            '-destination', selected['destination'], '-derivedDataPath', str(derived),
            'ARCHS=' + selected['arch'], 'CODE_SIGNING_ALLOWED=NO', 'CODE_SIGNING_REQUIRED=NO']
    version = command(capture_dir, 'xcode-version', ['xcodebuild', '-version'], cwd=source, timeout=30).decode().strip()
    settings_raw = command(capture_dir, 'build-settings', base + ['-showBuildSettings', '-json'], cwd=source)
    settings = json.loads(settings_raw)
    candidates = [e for e in settings if e.get('target') == selected.get('target')] if selected.get('target') else [
        e for e in settings if e.get('buildSettings', {}).get('WRAPPER_EXTENSION') == 'app']
    if len(candidates) != 1:
        raise MigrationError('Analysis needs one exact main target from captured Xcode settings')
    target = candidates[0]['buildSettings']
    selected = {**selected, 'target': candidates[0]['target']}
    write_json(capture_dir / 'build-settings.json', settings)
    known_tools = {}
    for program in ('clang', 'clang++'):
        compiler = Path(command(capture_dir, program.replace('+', 'p') + '-location',
                                ['xcrun', '--find', program], cwd=source, timeout=30).decode().strip()).resolve()
        known_tools[str(compiler)] = digest(compiler.read_bytes())
    sdk_settings = (Path(target['SDKROOT']) / 'SDKSettings.json').resolve()
    known_tools[str(sdk_settings)] = digest(sdk_settings.read_bytes())
    # The same raw build feeds membership, Clang AST and conditional capture.
    build = base + ['-verbose', 'build']
    command(capture_dir, 'device-build', build, cwd=source, timeout=timeout)
    if snapshot(source)['sha256'] != before:
        raise MigrationError('Source changed during automatic native capture')
    records = [{'name': 'device-build', 'argv': build, 'cwd': str(source), 'exit_code': 0}]
    write_json(capture_dir / 'commands.json', records)
    write_json(capture_dir / 'capture-report.json', {'commands': records, 'build_succeeded': True,
               'source_unchanged': True, 'source_sha256': before})
    membership = collect(source, derived, capture_dir,
                         {'scheme': selected['scheme'], 'configuration': selected['configuration'],
                          'sdk': selected['sdk'], 'xcode_version': version, 'targets': [selected['target']],
                          'architectures': [selected['arch']]},
                         build_log=capture_dir / 'device-build.stdout.log')
    if membership['membership_status'] != 'complete':
        raise MigrationError('Automatic build membership incomplete; preserve capture and resolve its findings')
    commands, members, ast_units = [], set(), []
    inputs = capture_dir / 'build-inputs'
    inputs.mkdir()
    log = (capture_dir / 'device-build.stdout.log').read_text().splitlines()
    for n, line in enumerate(log, 1):
        try:
            argv = shlex.split(line.strip())
        except ValueError:
            continue
        if not argv or Path(argv[0]).name not in {'clang', 'clang++'} or argv.count('-c') != 1:
            continue
        expanded = []
        for arg in argv:
            if arg.startswith('@'):
                response = Path(arg[1:])
                response = response if response.is_absolute() else source / response
                content = response.read_bytes()
                destination = inputs / response.name
                if destination.exists() and destination.read_bytes() != content:
                    raise MigrationError('Response files with duplicate basenames differ')
                destination.write_bytes(content)
                values = shlex.split(content.decode())
                if any(v.startswith('@') for v in values):
                    raise MigrationError('Nested compiler response files unsupported')
                expanded.extend(values)
            else:
                expanded.append(arg)
        unit = Path(expanded[expanded.index('-c') + 1]).resolve()
        if not unit.is_relative_to(source):
            raise MigrationError('Native compilation unit escapes source')
        name = unit.relative_to(source).as_posix()
        semantic = preprocess_argv(expanded)[:-len(FLAGS)]
        ast_units.append({'file': name, 'arguments': semantic + ['-fsyntax-only', '-Xclang', '-ast-dump=json']})
        commands.append({'build_log_line': n, 'original_argv': argv, 'expanded_argv': expanded})
        members.add(name)
        if '-MF' in expanded:
            dependency = Path(expanded[expanded.index('-MF') + 1])
            dependency = dependency if dependency.is_absolute() else source / dependency
            content = dependency.read_bytes()
            destination = inputs / dependency.name
            if destination.exists() and destination.read_bytes() != content:
                raise MigrationError('Dependency outputs with duplicate basenames differ')
            destination.write_bytes(content)
            members.update(Path(p).relative_to(source).as_posix()
                           for p in _dependency_paths(content.decode(), source)
                           if Path(p).is_relative_to(source))
    used_tools = {str(Path(c['expanded_argv'][0]).resolve()) for c in commands} | {str(sdk_settings)}
    if any(p not in known_tools or digest(Path(p).read_bytes()) != known_tools[p] for p in used_tools):
        raise MigrationError('Compiler or SDK changed or was not observed before build')
    tool_hashes = {p: known_tools[p] for p in used_tools}
    write_json(capture_dir / 'toolchain-inputs.json', {'before': tool_hashes, 'after': tool_hashes})
    write_json(capture_dir / 'compile-commands.json', commands)
    clang = None
    if ast_units:
        clang = capture_dir / 'clang-provider.json'
        write_json(clang, {'version_command': ['xcrun', 'clang', '--version'],
                          'translation_units': ast_units, 'timeout_seconds': min(timeout, 600)})
    compiled = output / 'compilation-evidence'
    pack(source, capture_dir, compiled, 'source_build', version)
    variant = {'scope': 'selected-build', 'source_files': membership['source_files'], 'evidence_path': str(compiled)}
    condition_path, unsupported = None, None
    if need_conditionals:
        if kind != 'project':
            unsupported = 'Conditional compiler evidence currently requires a single Xcode project'
        elif not commands:
            unsupported = 'No C-family compilation command available for conditional evidence'
        else:
            # Keep compiler units and preprocessing dependencies in separate bundles.
            conditional_dir = output / 'conditional-build-capture'
            shutil.copytree(capture_dir, conditional_dir)
            write_json(conditional_dir / 'source-files.json', {'source_files': sorted(members)})
            bundle = output / 'conditional-build-evidence'
            pack(source, conditional_dir, bundle, 'source_build', version)
            expected = {'project': selected['project'], 'scheme': selected['scheme'],
                        'target': selected['target'], 'configuration': selected['configuration'],
                        'sdk': selected['sdk'], 'architecture': selected['arch']}
            config = output / 'conditional-config.json'
            write_json(config, {'schema_version': 1, 'build_evidence': str(bundle),
                                'expected_build': expected, 'timeout_seconds': min(timeout, 600)})
            condition_path = project / 'spec/ref/ios-conditional-evidence' / (output.parent.name + '-' + output.name)
            from .conditional_evidence import capture as capture_condition
            capture_condition(project, config, condition_path)
            variant = {'scope': 'selected-build', 'source_files': sorted(members),
                       'evidence_path': str(bundle), 'conditional_evidence': str(condition_path),
                       'expected_build': expected, 'compilation_evidence_path': str(compiled)}
    return {'variant': variant, 'compilation': str(compiled), 'clang_config': str(clang) if clang else None,
            'conditional': str(condition_path) if condition_path else None, 'conditional_unresolved': unsupported,
            'selection': selected, 'source_sha256': before, 'status': 'captured'}
