"""Provider processes exchange data on stdin/stdout; app text is never executed."""
import json
from pathlib import Path
import subprocess

from .core import MigrationError, json_bytes, read_json


def invoke_json_provider(config_path, request):
    """Shared process boundary for syntax and conditional-source providers."""
    config = read_json(config_path)
    for field in ('command', 'version_command'):
        if not isinstance(config.get(field), list) or not config[field] or not all(isinstance(v, str) and v for v in config[field]):
            raise MigrationError(f'Provider {field} must be a nonempty argument array')
    timeout = config.get('timeout_seconds', 120)
    if type(timeout) is not int or not 1 <= timeout <= 3600:
        raise MigrationError('Provider timeout must be 1..3600 seconds')
    try:
        from .init_environment import _environment
        environment = _environment()
        version = subprocess.run(config['version_command'], capture_output=True, timeout=30, shell=False, env=environment)
        if version.returncode or not version.stdout.strip():
            raise MigrationError('Cannot verify Swift provider version')
        result = subprocess.run(config['command'], input=json_bytes(request), capture_output=True,
                                timeout=timeout, shell=False, env=environment)
    except (subprocess.TimeoutExpired, OSError) as exc:
        raise MigrationError('Swift provider unavailable or timed out') from exc
    if result.returncode:
        raise MigrationError('Swift provider failed: ' + result.stderr.decode('utf-8', errors='replace')[-2000:])
    try:
        value = json.loads(result.stdout)
    except (ValueError, UnicodeError) as exc:
        raise MigrationError('Provider did not return UTF-8 JSON') from exc
    return value, {'command': config['command'], 'version_command': config['version_command'],
                   'exit_code': result.returncode, 'version_stdout': version.stdout.decode('utf-8', errors='replace'),
                   'version_stderr': version.stderr.decode('utf-8', errors='replace')}, result.stdout, result.stderr


def swift_syntax(root, files, config_path, *, source_view=None):
    inputs = []
    for item in files:
        if item['path'].endswith('.swift'):
            if source_view and not source_view.includes(item['path']):
                continue
            inputs.append({**item, 'source': source_view.text(item['path']) if source_view else (root / item['path']).read_bytes().decode('utf-8')})
    if not inputs:
        raise MigrationError('No Swift input files')
    value, run, _, _ = invoke_json_provider(config_path, {'files': inputs})
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
    value['tool_version_output'] = run['version_stdout'].strip()
    value['compiler_binding'] = 'unresolved'
    if source_view:
        value['source_view'] = source_view.reference
    return value, issues


def normalize_build_settings(raw):
    if not isinstance(raw, list) or not raw:
        raise MigrationError('Expected nonempty xcodebuild -showBuildSettings -json array')
    targets = []
    seen = {}
    duplicate_targets = []
    retained = {'PRODUCT_NAME', 'PRODUCT_BUNDLE_IDENTIFIER', 'PRODUCT_TYPE', 'SWIFT_VERSION', 'SDKROOT',
                'SDK_NAME', 'IPHONEOS_DEPLOYMENT_TARGET', 'SUPPORTED_PLATFORMS', 'ARCHS', 'CONFIGURATION',
                'SWIFT_ACTIVE_COMPILATION_CONDITIONS', 'GCC_PREPROCESSOR_DEFINITIONS', 'OTHER_SWIFT_FLAGS',
                'OTHER_CFLAGS', 'HEADER_SEARCH_PATHS', 'FRAMEWORK_SEARCH_PATHS', 'INFOPLIST_FILE',
                'CODE_SIGN_ENTITLEMENTS', 'SWIFT_OBJC_BRIDGING_HEADER', 'SRCROOT', 'PROJECT_FILE_PATH',
                'PLATFORM_NAME', 'EFFECTIVE_PLATFORM_NAME', 'SDK_VERSION', 'TOOLCHAIN_DIR', 'SWIFT_EXEC',
                'SWIFT_INCLUDE_PATHS', 'PRODUCT_MODULE_NAME'}
    for entry in raw:
        if not isinstance(entry, dict) or not isinstance(entry.get('buildSettings'), dict):
            raise MigrationError('Invalid Xcode build settings entry')
        name = entry.get('target')
        if name in seen:
            if seen[name] != entry:
                raise MigrationError('Conflicting Xcode settings for target: ' + str(name))
            duplicate_targets.append(name)
            continue  # Xcode -alltargets can repeat its primary target verbatim.
        seen[name] = entry
        settings = entry['buildSettings']
        targets.append({'target': entry.get('target'), 'settings': {key: settings[key] for key in sorted(retained & settings.keys())},
                        'source_file_membership': 'not_provided_by_showBuildSettings'})
    return {'targets': targets, 'evidence': 'imported_xcode_settings', 'capture_authenticity': 'not_verified',
            'identical_duplicate_entries':duplicate_targets}


def clang_ast(root, files, config_path):
    """Retain genuine compiler AST per explicit translation unit; no guessed SDK flags."""
    from .core import safe_child, digest
    config = read_json(config_path)
    units = config.get('translation_units')
    version_command = config.get('version_command')
    if not isinstance(units, list) or not units or not isinstance(version_command, list) or not version_command or not all(isinstance(a, str) for a in version_command):
        raise MigrationError('Clang needs version_command and translation_units arrays')
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
