"""Capture real Xcode context once and feed the existing authoritative consumers."""
from pathlib import Path
import json
import platform
import shlex
import shutil

from .core import source_snapshot
from .core import MigrationError, digest, json_bytes, read_json, snapshot, write_json
from .apple_capabilities import command

ROOT = Path(__file__).resolve().parents[2]

# Owned adapter fingerprints verified against the corresponding local 0.13.x
# source packages. Unknown/third-party implementations are never substituted.
SWIFT_PREDECESSORS = {
    '20e6ecd716cde8c994ffa2d72e2f75d7983e3e37d289c50017a3f29fec63877b': '0.13.0',
    '4963baf6ac13af05a02b288d6a9ed602646b06807f6f39a5003e139978687ff9': '0.13.1',
}


def swift_provider_identity():
    """Bind every compiled Swift adapter source, not just its main entry file."""
    sources = [ROOT / 'providers/swift-syntax' / name for name in ('main.swift', 'VisibilityFacts.swift')]
    hashes = {path.relative_to(ROOT).as_posix(): digest(path.read_bytes()) for path in sources}
    return sources, hashes, digest(json_bytes(hashes))


def current_swift_adapter(config_path, config):
    """Upgrade only known, unextended HMigBot adapter requests.

    The caller first checks the requested executable hash. Original configs and
    artifacts remain untouched; fresh CLI diagnostics are retained outside the
    package. This prevents old project configuration from retaining Python Swift
    analysis after the local tool has been upgraded.
    """
    previous = config.get('provider_source_sha256')
    _, _, current = swift_provider_identity()
    declared = config.get('provider_sources_sha256')
    if declared is not None:
        if (not isinstance(declared, dict) or not declared
                or any(not isinstance(path, str) or not isinstance(value, str) or len(value) != 64
                       or any(char not in '0123456789abcdef' for char in value) for path, value in declared.items())
                or digest(json_bytes(declared)) != previous):
            raise MigrationError('Swift adapter source bundle identity is inconsistent')
    if previous not in SWIFT_PREDECESSORS or previous == current:
        return config, None
    fields = {'command', 'version_command', 'timeout_seconds', 'provider_source_sha256', 'provider_binary_sha256'}
    if (set(config) != fields or len(config['command']) != 1 or not Path(config['command'][0]).is_absolute()
            or config['version_command'] != ['xcrun', 'swiftc', '--version']):
        raise MigrationError('Known legacy Swift adapter has custom configuration; explicit migration is required')
    import tempfile
    from . import __version__
    folder = Path(tempfile.mkdtemp(prefix='hmigbot-swift-upgrade-'))
    path = swift_provider(folder, folder / 'provider')
    effective = read_json(path)
    record = {'status': 'upgraded', 'from_tool': SWIFT_PREDECESSORS[previous], 'tool_version': __version__,
              'requested_config_sha256': digest(Path(config_path).read_bytes()),
              'requested_source_sha256': previous, 'effective_source_sha256': current,
              'effective_config_sha256': digest(path.read_bytes()),
              'effective_binary_sha256': effective['provider_binary_sha256'], 'evidence_directory': str(folder)}
    write_json(folder / 'upgrade.json', record)
    return effective, record


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
    sources, source_hashes, source_identity = swift_provider_identity()
    sdk = command(output, 'macos-sdk', ['xcrun', '--sdk', 'macosx', '--show-sdk-path'], cwd=source, timeout=30).decode().strip()
    argv = [str(compiler), *map(str, sources), '-O', '-sdk', sdk, '-module-cache-path', str(output / 'ModuleCache'),
            '-I', str(host), '-L', str(host),
            '-lSwiftSyntax', '-lSwiftParser', '-lSwiftParserDiagnostics',
            '-Xlinker', '-rpath', '-Xlinker', str(host), '-o', str(executable)]
    command(output, 'swift-syntax-build', argv, cwd=source, timeout=120)
    config = output / 'swift-syntax.json'
    write_json(config, {'command': [str(executable)], 'version_command': ['xcrun', 'swiftc', '--version'],
                        'timeout_seconds': 120, 'provider_source_sha256': source_identity,
                        'provider_sources_sha256': source_hashes,
                        'provider_binary_sha256': digest(executable.read_bytes())})
    return config


def capture(source, project, supplied, output, *, need_conditionals=False, timeout=600):
    from .source_build_membership import collect
    from .evidence import pack
    from .conditional_evidence import _dependency_paths, preprocess_argv, FLAGS
    before = source_snapshot(source)['sha256']
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
    for program in ('clang', 'clang++', 'swiftc'):
        compiler = Path(command(capture_dir, program.replace('+', 'p') + '-location',
                                ['xcrun', '--find', program], cwd=source, timeout=30).decode().strip()).resolve()
        known_tools[str(compiler)] = digest(compiler.read_bytes())
    sdk_settings = (Path(target['SDKROOT']) / 'SDKSettings.json').resolve()
    known_tools[str(sdk_settings)] = digest(sdk_settings.read_bytes())
    # The same raw build feeds membership, Clang AST and conditional capture.
    build = base + ['-verbose', 'build']
    command(capture_dir, 'device-build', build, cwd=source, timeout=timeout)
    if source_snapshot(source)['sha256'] != before:
        raise MigrationError('Source changed during automatic native capture')
    records = [{'name': 'device-build', 'argv': build, 'cwd': str(source), 'exit_code': 0}]
    write_json(capture_dir / 'commands.json', records)
    write_json(capture_dir / 'capture-report.json', {'commands': records, 'build_succeeded': True,
               'source_unchanged': True, 'source_sha256': before})
    from .native_product_scope import capture_scope
    product_scope = capture_scope(source, derived, capture_dir, settings,
        root_target=selected['target'], scheme=selected['scheme'], configuration=selected['configuration'],
        sdk=selected['sdk'], architectures=[selected['arch']], source_sha256=before,
        command=lambda name, argv: command(capture_dir, name, argv, cwd=source, timeout=min(timeout, 120)),
        allow_non_application=True)
    selected = {**selected, 'targets': product_scope['targets']}
    membership = collect(source, derived, capture_dir,
                         {'scheme': selected['scheme'], 'configuration': selected['configuration'],
                          'sdk': selected['sdk'], 'xcode_version': version, 'targets': product_scope['targets'],
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
    swift_tools = set()
    for line in log:
        if line.lstrip().startswith('builtin-SwiftDriver -- '):
            arguments = shlex.split(line.strip())[2:]
            if arguments:
                swift_tools.add(str(Path(arguments[0]).resolve()))
    if swift_tools:
        swift_tools.add(str(sdk_settings))
        if any(path not in known_tools or digest(Path(path).read_bytes()) != known_tools[path] for path in swift_tools):
            raise MigrationError('Swift compiler/SDK changed since the observed native build')
        hashes = {path: known_tools[path] for path in sorted(swift_tools)}
        write_json(capture_dir / 'swift-toolchain-inputs.json', {'before': hashes, 'after': hashes})
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
        has_swift = any(name.endswith('.swift') for name in membership['source_files'])
        if len(product_scope['targets']) != 1:
            unsupported = 'Conditional compiler evidence currently requires a single selected target'
        elif kind != 'project':
            unsupported = 'Conditional compiler evidence currently requires a single Xcode project'
        elif not commands and not has_swift:
            unsupported = 'No C-family compilation command available for conditional evidence'
        elif commands:
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
        if has_swift and unsupported is None:
            # Compose real Swift and Clang observations under the one selected
            # compiler membership. Swift flags and Clang -D/-Xcc contexts stay
            # separate; a failed component never invents active source lines.
            expected = {'project': selected[kind], 'scheme': selected['scheme'],
                        'target': selected['target'], 'configuration': selected['configuration'],
                        'sdk': selected['sdk'], 'architecture': selected['arch']}
            from .conditional_views import capture as capture_views
            swift_path = project / 'spec/ref/ios-conditional-evidence' / (output.parent.name + '-' + output.name + '-configured')
            result = capture_views(source, project, compiled, swift_path, expected, clang=condition_path)
            condition_path = swift_path
            variant = {'scope': 'selected-build', 'source_files': membership['source_files'],
                       'evidence_path': str(compiled), 'conditional_evidence': str(condition_path),
                       'expected_build': expected}
            unsupported = result['unknowns'] or None
    return {'variant': variant, 'compilation': str(compiled), 'clang_config': str(clang) if clang else None,
            'conditional': str(condition_path) if condition_path else None, 'conditional_unresolved': unsupported,
            'selection': selected, 'source_sha256': before, 'status': 'captured'}
