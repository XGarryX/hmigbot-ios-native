# OPTIMIZED_FOR_MACOS_XCODE_NATIVE: retains Python orchestration only; compiler/build facts come from Xcode CLI.
"""Provider processes exchange data on stdin/stdout; app text is never executed."""
import json
from pathlib import Path
import subprocess

from .core import MigrationError, digest, json_bytes, read_json


def swift_syntax(root, files, config_path):
    config = read_json(config_path)
    for field in ('command', 'version_command'):
        if not isinstance(config.get(field), list) or not config[field] or not all(isinstance(v, str) and v for v in config[field]):
            raise MigrationError(f'Provider {field} must be a nonempty argument array')
    inputs = []
    for item in files:
        if item['path'].endswith('.swift'):
            inputs.append({**item, 'source': (root / item['path']).read_bytes().decode('utf-8')})
    if not inputs:
        raise MigrationError('No Swift input files')
    timeout = config.get('timeout_seconds', 120)
    if type(timeout) is not int or not 1 <= timeout <= 3600:
        raise MigrationError('Provider timeout must be 1..3600 seconds')
    binary_sha = config.get('provider_binary_sha256')
    if binary_sha and digest(Path(config['command'][0]).read_bytes()) != binary_sha:
        raise MigrationError('Generated SwiftSyntax provider binary changed')
    from .native_source_capture import current_swift_adapter
    config, adapter_upgrade = current_swift_adapter(config_path, config)
    binary_sha = config.get('provider_binary_sha256')
    try:
        version = subprocess.run(config['version_command'], capture_output=True, timeout=30, shell=False)
        if version.returncode or not version.stdout.strip():
            raise MigrationError('Cannot verify Swift provider version')
        result = subprocess.run(config['command'], input=json_bytes({'files': inputs}), capture_output=True,
                                timeout=timeout, shell=False)
    except subprocess.TimeoutExpired as exc:
        raise MigrationError('SwiftSyntax provider timed out; no successful artifact was produced') from exc
    if result.returncode:
        raise MigrationError('SwiftSyntax provider failed: ' + result.stderr.decode('utf-8', errors='replace')[-2000:])
    if binary_sha and digest(Path(config['command'][0]).read_bytes()) != binary_sha:
        raise MigrationError('Generated SwiftSyntax provider binary changed during execution')
    try:
        value = json.loads(result.stdout)
    except (ValueError, UnicodeError) as exc:
        raise MigrationError('Provider did not return UTF-8 JSON') from exc
    if not isinstance(value, dict) or value.get('protocol_version') != 1 or value.get('provider') != 'SwiftSyntax' or value.get('semantic_resolution') is not False:
        raise MigrationError('Unexpected SwiftSyntax protocol/evidence class')
    if not isinstance(value.get('files'), list):
        raise MigrationError('Provider files must be an array')
    expected = {item['path']: item for item in inputs}
    received, issues = set(), []
    for file in value.get('files', []):
        if not isinstance(file, dict) or file.get('path') not in expected or file['path'] in received:
            raise MigrationError('Unknown/duplicate provider source file')
        received.add(file['path'])
        source = expected[file['path']]
        if file.get('sha256') != source['sha256']:
            raise MigrationError('Provider returned stale source hash')
        if not isinstance(file.get('nodes'), list) or type(file.get('parse_has_error')) is not bool:
            raise MigrationError('Provider omitted nodes or parse diagnostics')
        if value.get('lexical_protocol_version') == 1 and not file['parse_has_error']:
            from .swift_native import tokens_for
            tokens_for(file, source['source'])
        for node in file['nodes']:
            if not isinstance(node, dict):
                raise MigrationError('Provider nodes must be objects')
            start, end = node.get('start_utf8'), node.get('end_utf8')
            if type(start) is not int or type(end) is not int or not 0 <= start <= end <= len(source['source'].encode('utf-8')):
                raise MigrationError('Provider returned invalid source span')
            if type(node.get('line')) is not int or node['line'] < 1:
                raise MigrationError('Provider returned invalid source line')
            node['evidence'] = 'parser_syntax'
        if file['parse_has_error']:
            issues.append({'code': 'swift_parse_error', 'path': file['path'], 'diagnostics': file.get('diagnostics', [])})
    if received != set(expected):
        raise MigrationError('SwiftSyntax provider omitted source files')
    value['tool_version_output'] = version.stdout.decode('utf-8', errors='replace').strip()
    value['compiler_binding'] = 'unresolved'
    if adapter_upgrade:
        if value.get('lexical_protocol_version') != 1:
            raise MigrationError('Upgraded local Swift adapter omitted its native lexical protocol')
        value['adapter_upgrade'] = adapter_upgrade
    return value, issues


def normalize_build_settings(raw):
    if not isinstance(raw, list) or not raw:
        raise MigrationError('Expected nonempty xcodebuild -showBuildSettings -json array')
    targets = []
    retained = {'PRODUCT_NAME', 'PRODUCT_BUNDLE_IDENTIFIER', 'PRODUCT_TYPE', 'SWIFT_VERSION', 'SDKROOT',
                'SDK_NAME', 'IPHONEOS_DEPLOYMENT_TARGET', 'SUPPORTED_PLATFORMS', 'ARCHS', 'CONFIGURATION',
                'SWIFT_ACTIVE_COMPILATION_CONDITIONS', 'GCC_PREPROCESSOR_DEFINITIONS', 'OTHER_SWIFT_FLAGS',
                'OTHER_CFLAGS', 'HEADER_SEARCH_PATHS', 'FRAMEWORK_SEARCH_PATHS', 'INFOPLIST_FILE',
                'CODE_SIGN_ENTITLEMENTS', 'SWIFT_OBJC_BRIDGING_HEADER', 'SRCROOT', 'PROJECT_FILE_PATH'}
    for entry in raw:
        if not isinstance(entry, dict) or not isinstance(entry.get('buildSettings'), dict):
            raise MigrationError('Invalid Xcode build settings entry')
        settings = entry['buildSettings']
        targets.append({'target': entry.get('target'), 'settings': {key: settings[key] for key in sorted(retained & settings.keys())},
                        'source_file_membership': 'not_provided_by_showBuildSettings'})
    return {'targets': targets, 'evidence': 'imported_xcode_settings', 'capture_authenticity': 'not_verified'}


def xcodebuild_settings(root, config):
    """Capture build settings directly from Xcode; no generated Python helper is involved."""
    if not isinstance(config, dict):
        raise MigrationError('Xcode build settings config must be an object')
    workspace = config.get('workspace')
    project = config.get('project')
    if not workspace and not project:
        workspaces = sorted(root.glob('*.xcworkspace'))
        projects = sorted(root.glob('*.xcodeproj'))
        if len(workspaces) == 1:
            workspace = workspaces[0].name
        elif len(projects) == 1:
            project = projects[0].name
        else:
            raise MigrationError('Xcode build settings requires an unambiguous workspace/project or explicit config')
    scheme = config.get('scheme')
    command = ['xcodebuild', '-showBuildSettings', '-json']
    if workspace:
        command += ['-workspace', str(root / workspace)]
    else:
        command += ['-project', str(root / project)]
    if scheme:
        command += ['-scheme', scheme]
    # Explicit values are preferred; defaults are recorded so broad projects do not
    # silently inherit a developer's last Xcode selection.
    configuration = config.get('configuration', 'Debug')
    sdk = config.get('sdk')
    destination = config.get('destination')
    arch = config.get('arch')
    if not isinstance(configuration, str) or not configuration:
        raise MigrationError('Xcode configuration must be a nonempty string')
    command += ['-configuration', configuration]
    if sdk:
        command += ['-sdk', str(sdk)]
    if destination:
        command += ['-destination', str(destination)]
    if arch:
        command += ['ARCHS=' + str(arch)]
    extra = config.get('arguments', [])
    if not isinstance(extra, list) or not all(isinstance(v, str) and v for v in extra):
        raise MigrationError('Xcode build settings arguments must be a string array')
    command += extra
    if not all(isinstance(v, str) and v for v in command):
        raise MigrationError('Xcode build settings arguments must be strings')
    try:
        result = subprocess.run(command, cwd=root, capture_output=True, timeout=int(config.get('timeout_seconds', 120)), shell=False)
    except subprocess.TimeoutExpired as exc:
        raise MigrationError('xcodebuild -showBuildSettings timed out') from exc
    if result.returncode:
        raise MigrationError('xcodebuild -showBuildSettings failed: ' + result.stderr.decode('utf-8', errors='replace')[-2000:])
    try:
        raw = json.loads(result.stdout)
    except (ValueError, UnicodeError) as exc:
        raise MigrationError('xcodebuild returned invalid JSON') from exc
    value = normalize_build_settings(raw)
    value['evidence'] = 'direct_xcodebuild_showBuildSettings'
    value['command'] = command
    value['xcodebuild_stderr'] = result.stderr.decode('utf-8', errors='replace')
    value['selection'] = {'workspace': workspace, 'project': project, 'scheme': scheme,
                          'configuration': configuration, 'sdk': sdk,
                          'destination': destination, 'arch': arch,
                          'defaults_applied': [k for k, v in {'configuration': config.get('configuration'),
                                                               'sdk': sdk, 'destination': destination, 'arch': arch}.items()
                                               if v is None and k == 'configuration']}
    return value



def xcodebuild_compile_commands(root, config, *, derived_data):
    """Run a no-sign Xcode build in disposable DerivedData and extract real compiler argv."""
    import shlex
    if not isinstance(config, dict):
        raise MigrationError('Xcode compile config must be an object')
    settings = dict(config)
    settings.setdefault('configuration', 'Debug')
    project = settings.get('project')
    workspace = settings.get('workspace')
    command = ['xcodebuild']
    if workspace:
        command += ['-workspace', str(root / workspace)]
    elif project:
        command += ['-project', str(root / project)]
    else:
        projects = sorted(root.glob('*.xcodeproj'))
        workspaces = sorted(root.glob('*.xcworkspace'))
        if len(workspaces) == 1:
            command += ['-workspace', str(workspaces[0])]
        elif len(projects) == 1:
            command += ['-project', str(projects[0])]
        else:
            raise MigrationError('Xcode compile requires an unambiguous project/workspace')
    if settings.get('scheme'): command += ['-scheme', str(settings['scheme'])]
    command += ['-configuration', str(settings['configuration'])]
    if settings.get('sdk'): command += ['-sdk', str(settings['sdk'])]
    if settings.get('destination'): command += ['-destination', str(settings['destination'])]
    if settings.get('arch'): command += ['ARCHS=' + str(settings['arch'])]
    command += ['CODE_SIGNING_ALLOWED=NO', 'CODE_SIGNING_REQUIRED=NO', '-verbose', 'build']
    timeout = int(settings.get('timeout_seconds', 900))
    command[1:1] = ['-derivedDataPath', str(derived_data)]
    try:
        result = subprocess.run(command, cwd=root, capture_output=True, timeout=timeout, shell=False)
    except subprocess.TimeoutExpired as exc:
        error = MigrationError('xcodebuild compile command capture timed out')
        error.provider_diagnostics = {'xcodebuild.stdout.log': exc.stdout or b'', 'xcodebuild.stderr.log': exc.stderr or b''}
        raise error from exc
    if result.returncode:
        error = MigrationError('xcodebuild failed; compiler commands are not accepted: ' +
                             result.stderr.decode('utf-8', errors='replace')[-2000:])
        error.provider_diagnostics = {'xcodebuild.stdout.log': result.stdout, 'xcodebuild.stderr.log': result.stderr}
        raise error
    text = (result.stdout + result.stderr).decode('utf-8', errors='replace')
    commands = []
    for line in text.splitlines():
        if not any(token in line for token in ('/clang ', '/clang++ ')):
            continue
        try:
            argv = shlex.split(line.strip())
        except ValueError:
            continue
        if (argv and Path(argv[0]).is_absolute() and Path(argv[0]).name in {'clang', 'clang++'}
                and argv.count('-c') == 1):
            expanded = []
            for arg in argv:
                if arg.startswith('@'):
                    response = Path(arg[1:])
                    if not response.is_absolute():
                        response = root / response
                    extra = shlex.split(response.read_text(encoding='utf-8'))
                    if any(a.startswith('@') for a in extra):
                        raise MigrationError('Nested Xcode response files are unsupported')
                    expanded.extend(extra)
                else:
                    expanded.append(arg)
            if expanded.count('-c') == 1 and expanded.index('-c') + 1 < len(expanded):
                commands.append(expanded)
    if not commands:
        detail = text[-2000:]
        raise MigrationError('xcodebuild produced no compiler commands; exit=%s: %s' % (result.returncode, detail))
    return {'command': command, 'exit_code': result.returncode, 'compiler_commands': commands,
            'stdout': result.stdout.decode('utf-8', errors='replace'),
            'stderr': result.stderr.decode('utf-8', errors='replace')}

def clang_ast(root, files, config_path):
    """Retain genuine compiler AST per explicit translation unit; no guessed SDK flags."""
    from .core import safe_child, digest
    config = read_json(config_path)
    units = config.get('translation_units')
    if not units and isinstance(config.get('xcodebuild'), dict):
        import tempfile
        from .conditional_evidence import preprocess_argv, FLAGS
        # Build response files, header maps and module paths must survive until
        # the actual AST commands finish. They are not portable evidence.
        with tempfile.TemporaryDirectory(prefix='xcode-derived-data-') as derived:
            captured = xcodebuild_compile_commands(root, config['xcodebuild'], derived_data=Path(derived))
            units = []
            for argv in captured['compiler_commands']:
                source = Path(argv[argv.index('-c') + 1])
                if not source.is_absolute():
                    source = root / source
                name = source.resolve().relative_to(root.resolve()).as_posix()
                if source.suffix not in {'.m', '.mm', '.c', '.cc', '.cpp'}:
                    raise MigrationError('Xcode AST supports only C/Objective-C translation units')
                semantic = preprocess_argv(argv)[:-len(FLAGS)]
                units.append({'file': name, 'arguments': semantic +
                              ['-fsyntax-only', '-Xclang', '-ast-dump=json']})
            nested = {**config, 'translation_units': units}
            nested.pop('xcodebuild', None)
            nested_path = Path(derived) / 'ast-provider.json'
            nested_path.write_bytes(json_bytes(nested))
            value, issues, payload = clang_ast(root, files, nested_path)
            payload['xcodebuild.stdout.log'] = captured.pop('stdout').encode('utf-8')
            payload['xcodebuild.stderr.log'] = captured.pop('stderr').encode('utf-8')
            value['xcodebuild_capture'] = captured
            return value, issues, payload
    version_command = config.get('version_command', ['xcrun', 'clang', '--version'])
    if not isinstance(units, list) or not units or not isinstance(version_command, list) or not version_command or not all(isinstance(a, str) for a in version_command):
        raise MigrationError('Clang needs version_command and translation_units, or xcodebuild config')
    try:
        version = subprocess.run(version_command, capture_output=True, timeout=30, shell=False)
    except subprocess.TimeoutExpired as exc:
        raise MigrationError('Clang version probe timed out') from exc
    if version.returncode or not version.stdout.strip():
        raise MigrationError('Cannot verify Clang version')
    timeout = config.get('timeout_seconds', 120)
    if type(timeout) is not int or not 1 <= timeout <= 3600:
        raise MigrationError('Clang timeout must be 1..3600 seconds')
    known = {file['path']: file for file in files}
    payload, summaries, issues, seen = {}, [], [], set()
    for unit in units:
        if not isinstance(unit, dict):
            raise MigrationError('Clang translation unit must be an object')
        name = unit.get('file')
        args = unit.get('arguments')
        if name not in known or name in seen or Path(name).suffix not in {'.m', '.mm', '.c', '.cc', '.cpp', '.h', '.hpp'}:
            raise MigrationError('Invalid or duplicate Clang translation unit')
        if not isinstance(args, list) or not args or not all(isinstance(a, str) and a for a in args):
            raise MigrationError('Clang arguments must be an explicit executable argument array')
        if '-fsyntax-only' not in args or '-ast-dump=json' not in args:
            raise MigrationError('Clang invocation must use -fsyntax-only and -Xclang -ast-dump=json')
        seen.add(name)
        file = safe_child(root, name)
        command = [arg.replace('{source}', str(root)).replace('{file}', str(file)) for arg in args]
        prefix = 'clang/' + digest(name.encode())[:16]
        try:
            result = subprocess.run(command, cwd=root, capture_output=True, timeout=timeout, shell=False)
            code, stdout, stderr = result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired as exc:
            code, stdout, stderr = None, exc.stdout or b'', exc.stderr or b''
        payload[prefix + '.stdout.json'] = stdout
        payload[prefix + '.stderr.log'] = stderr
        valid = False
        if code == 0:
            try:
                ast = json.loads(stdout)
                valid = isinstance(ast, dict) and ast.get('kind') == 'TranslationUnitDecl'
            except (ValueError, UnicodeError):
                pass
        if not valid:
            issues.append({'code': 'clang_ast_unavailable', 'path': name, 'exit_code': code, 'diagnostics': prefix + '.stderr.log'})
        summaries.append({'path': name, 'sha256': known[name]['sha256'], 'arguments': command, 'exit_code': code,
            'ast': prefix + '.stdout.json', 'diagnostics': prefix + '.stderr.log',
            'status': 'compiler_ast_available' if valid else 'failed',
            'scope': 'Configured translation unit only; active iOS SDK and complete project membership must be established separately'})
    return {'translation_units': summaries, 'tool_version_output': version.stdout.decode('utf-8', errors='replace').strip()}, issues, payload
