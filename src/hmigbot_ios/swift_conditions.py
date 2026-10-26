"""Captured Swift compiler argv -> official SwiftIfConfig source views.

Python owns evidence/argument adaptation only. SwiftIfConfig selects clauses;
Apple Swift answers conditions with actual SDK/arch/defines/import context.
"""
from pathlib import Path
import json
import re
import shlex
import tempfile

from .core import MigrationError, digest, json_bytes, read_json, safe_child, source_snapshot, write_json
from .apple_capabilities import command

ROOT = Path(__file__).resolve().parents[2]
OUTPUT_PAIRS = {'-o', '-output-file-map', '-emit-module-path', '-emit-objc-header-path',
                '-emit-dependencies-path', '-emit-reference-dependencies-path', '-serialize-diagnostics-path',
                '-dependency-scan-serialize-diagnostics-path', '-index-store-path', '-index-unit-output-path',
                '-num-threads', '-j', '-module-cache-path', '-const-gather-protocols-file',
                '-const-gather-protocols-list', '-emit-module-interface-path', '-emit-private-module-interface-path',
                '-emit-package-module-interface-path', '-emit-module-source-info-path', '-emit-abi-descriptor-path'}
OUTPUT_PAIRS |= {'-emit-localized-strings-path'}
OUTPUT_FLAGS = {'-c', '-emit-module', '-emit-objc-header', '-emit-dependencies', '-serialize-diagnostics',
                '-incremental', '-enable-batch-mode', '-whole-module-optimization', '-parseable-output',
                '-use-frontend-parseable-output', '-emit-const-values', '-save-temps', '-v'}
# The AST query uses the same target, SDK, defines, imports and search paths.
# Xcode's explicit-module build driver mode rejects -dump-ast-format json;
# module search remains bound to the captured paths and unresolved imports
# remain unknown rather than being guessed active/inactive.
OUTPUT_FLAGS |= {'-emit-localized-strings', '-experimental-emit-module-separately', '-explicit-module-build'}


def require(ok, message):
    if not ok:
        raise MigrationError('Swift conditional context: ' + message)


def option(argv, name):
    require(argv.count(name) == 1 and argv.index(name) + 1 < len(argv), 'missing/duplicate ' + name)
    return argv[argv.index(name) + 1]


def provider(output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    compiler = Path(command(output, 'swiftc-location', ['xcrun', '--find', 'swiftc'], cwd=output, timeout=30).decode().strip())
    sdk = command(output, 'macos-sdk', ['xcrun', '--sdk', 'macosx', '--show-sdk-path'], cwd=output, timeout=30).decode().strip()
    host = compiler.parent.parent / 'lib/swift/host'
    require((host / 'SwiftIfConfig.swiftmodule').is_dir(), 'Xcode toolchain has no SwiftIfConfig host module')
    main = ROOT / 'providers/swift-conditions/main.swift'
    executable = output / 'swift-condition-provider'
    argv = [str(compiler), str(main), '-O', '-sdk', sdk, '-module-cache-path', str(output / 'ModuleCache'),
            '-I', str(host), '-L', str(host), '-lSwiftSyntax', '-lSwiftParser', '-lSwiftParserDiagnostics',
            '-lSwiftIfConfig', '-Xlinker', '-rpath', '-Xlinker', str(host), '-o', str(executable)]
    command(output, 'provider-build', argv, cwd=output, timeout=120)
    return {'binary': str(executable), 'binary_sha256': digest(executable.read_bytes()),
            'source_sha256': digest(main.read_bytes()), 'toolchain_libraries': {
                str(path): digest(path.read_bytes()) for name in ('SwiftIfConfig', 'SwiftSyntax', 'SwiftParser', 'SwiftParserDiagnostics')
                if (path := host / ('lib' + name + '.dylib')).is_file()}}


def probe_arguments(argv, cache):
    """Retain every semantic compiler argument; remove only known output actions.

    An unknown argument is passed to the real driver, never silently interpreted
    or dropped. Unsupported contexts remain unknown with the native diagnostic.
    """
    require(isinstance(argv, list) and argv and Path(argv[0]).is_absolute() and
            Path(argv[0]).name in {'swiftc', 'swiftc-frontend', 'swift-frontend'}, 'absolute Swift compiler required')
    require(Path(argv[0]).name == 'swiftc', 'capture a SwiftDriver argv; frontend-only context requires explicit adaptation')
    result, index = [], 1
    while index < len(argv):
        arg = argv[index]
        if arg.startswith('@'):
            require(arg.endswith('.SwiftFileList'), 'opaque Swift response file is not a source file list')
            index += 1
        elif arg in OUTPUT_PAIRS:
            require(index + 1 < len(argv), 'missing output option value: ' + arg)
            index += 2
        elif arg in OUTPUT_FLAGS or re.fullmatch(r'-j\d+', arg):
            index += 1
        elif Path(arg).suffix == '.swift' and not arg.startswith('-'):
            index += 1
        elif arg == '-Xcc' and index + 1 < len(argv) and argv[index + 1].startswith('-fmodules-cache-path='):
            result.extend(['-Xcc', '-fmodules-cache-path=' + str(cache / 'Clang')]); index += 2
        else:
            result.append(arg); index += 1
    option(result, '-target'); option(result, '-sdk')
    require(result.count('-swift-version') <= 1, 'duplicate Swift language mode')
    return result + ['-module-cache-path', str(cache)]


def contexts(source, artifacts, membership, expected, output):
    """Bind driver commands to their original captured file lists and targets."""
    from .source_build_membership import parse_file_list, _location
    source, artifacts, output = Path(source).resolve(), Path(artifacts), Path(output)
    selected = membership['selection']
    require(selected['scheme'] == expected['scheme'] and selected['configuration'] == expected['configuration']
            and selected['sdk'] == expected['sdk'] and expected['target'] in selected['targets']
            and expected['architecture'] in selected['architectures'], 'selected build differs from expected context')
    lists = membership['evidence']['sources']
    members = set(membership['source_files'])
    result, seen = [], set()
    for line_number, line in enumerate((artifacts / 'device-build.stdout.log').read_text().splitlines(), 1):
        if not line.lstrip().startswith('builtin-SwiftDriver -- '):
            continue
        argv = shlex.split(line.strip())[2:]
        require(argv and Path(argv[0]).is_absolute() and Path(argv[0]).name == 'swiftc', 'invalid SwiftDriver executable')
        file_lists = [arg[1:] for arg in argv if arg.startswith('@') and arg.endswith('.SwiftFileList')]
        if not file_lists:
            continue
        files, target, architecture = set(), None, None
        for spelling in file_lists:
            t, a = _location(Path(spelling))
            if t not in selected['targets']:
                continue  # Other products/dependencies do not create selected-product duties.
            require(target is None or (t, a) == (target, architecture), 'one driver mixes target file-list contexts')
            target, architecture = t, a
            module = Path(spelling).name.rsplit('.', 1)[0]
            captured = [entry for entry in lists if entry['kind'] == 'swift_file_list' and
                        entry['target'] == t and entry['architecture'] == a and entry['module'] == module]
            require(len(captured) == 1, 'ambiguous/missing original Swift file list: ' + spelling)
            raw = safe_child(artifacts, captured[0]['artifact']).read_bytes()
            require(digest(raw) == captured[0]['sha256'], 'captured Swift file list changed')
            for path in parse_file_list(raw):
                actual = Path(path).resolve()
                if actual.is_relative_to(source):
                    relative = actual.relative_to(source).as_posix()
                    require(relative in members, 'driver file list has a source outside compiled membership')
                    files.add(relative)
        if not files:
            continue
        require(architecture == expected['architecture'] and option(argv, '-target').split('-')[0] == architecture,
                'Swift target triple/architecture mismatch')
        settings = read_json(artifacts / 'build-settings.json')
        targets = [row['buildSettings'] for row in settings if row.get('target') == target]
        require(len(targets) == 1 and Path(option(argv, '-sdk')).resolve() == Path(targets[0]['SDKROOT']).resolve(),
                'Swift compiler SDK differs from captured target settings')
        key = digest(json_bytes([argv, sorted(files), target, architecture]))
        if key in seen:
            continue
        seen.add(key)
        version = command(output, 'compiler-version-' + key[:12], [argv[0], '--version'], cwd=source, timeout=30).decode()
        match = re.search(r'Swift version\s+(\d+)\.(\d+)(?:\.(\d+))?', version)
        require(match is not None, 'unrecognized actual Swift compiler version')
        result.append({'id': key, 'target': target, 'architecture': architecture, 'build_log_line': line_number,
                       'compiler_sha256': digest(Path(argv[0]).read_bytes()),
                       'original_argv': argv, 'files': sorted(files),
                       'context': {'swiftc': argv[0], 'arguments': probe_arguments(argv, output / 'ModuleCache'),
                                   'compiler_version': [int(v) for v in match.groups() if v is not None],
                                   'declared_modules': sorted({item.get('module') for item in lists if item.get('module')})}})
    swift_members = {p for p in members if p.endswith('.swift')}
    require(set().union(*(set(c['files']) for c in result)) == swift_members,
            'selected Swift members are not all backed by original driver commands')
    return result


def run(source, context, executable, output):
    source, output = Path(source), Path(output)
    output.mkdir(parents=True, exist_ok=True)
    files = [{'path': name, 'source': safe_child(source, name).read_bytes().decode('utf-8'),
              'sha256': digest(safe_child(source, name).read_bytes())} for name in context['files']]
    request = {'context': context['context'], 'files': files}
    write_json(output / 'request.json', request)
    raw = command(output, 'conditional-query', [str(executable)], cwd=source,
                  input_data=json_bytes(request), timeout=600)
    response = json.loads(raw)
    write_json(output / 'response.json', response)
    return request, response


def observations(request, response, unit):
    """Check native masks against original UTF-8, preserving original coordinates."""
    files = response.get('files', [])
    require(response.get('provider') == 'SwiftIfConfig+AppleSwiftCompiler' and
            isinstance(files, list) and {f.get('path') for f in files} == {f['path'] for f in request['files']}
            and len(files) == len(request['files']), 'official provider did not return every requested source')
    inputs = {f['path']: f for f in request['files']}
    queries = response.get('compiler_queries')
    require(isinstance(queries, list) and queries, 'native compiler query records missing')
    for record in queries:
        expression = record.get('expression')
        require(isinstance(expression, str) and record.get('input_source') ==
                '#if ' + expression + '\nenum HMIGBOT_CONDITION_TRUE {}\n#else\nenum HMIGBOT_CONDITION_FALSE {}\n#endif\n',
                'compiler query source record differs')
        argv = record.get('argv', [])
        require(record.get('ast_format') == 'text' and
                argv[:-1] == [request['context']['swiftc'], '-dump-ast'] + request['context']['arguments'],
                'compiler query argv differs from captured context')
    observed, unknown = {}, []
    for item in files:
        original = inputs[item['path']]
        require(item.get('sha256') == original['sha256'], 'native view source hash mismatch')
        if item.get('status') != 'resolved':
            unknown.append({'path': item['path'], 'context': unit, 'diagnostics': item.get('diagnostics', [])})
            continue
        raw, masked = original['source'].encode('utf-8'), item.get('filtered_source', '').encode('utf-8')
        require(len(raw) == len(masked) and item.get('source_map') == 'utf8-offset-and-newline-preserving-mask',
                'native source mask changed UTF-8 coordinates')
        require(all(a == b or b == 32 and a not in (10, 13) for a, b in zip(raw, masked)),
                'native source mask invented bytes or changed newlines')
        active = [number for number, line in enumerate(masked.decode('utf-8').splitlines(), 1) if line.strip()]
        observed[item['path']] = [{'unit': unit, 'instance': 'swift', 'active_lines': active}]
    return observed, unknown
