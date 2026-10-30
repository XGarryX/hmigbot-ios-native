"""Clang directives-only observations for a captured, selected Xcode build.

This is a bounded adapter, not a C preprocessor implemented in Python. Clang
selects branches; we preserve original token locations. PCM/PCH-only headers
without textual observations remain unresolved. Integrity is not authenticity.
"""
from __future__ import annotations

import datetime
import re
import shlex
import subprocess
from pathlib import Path

from .core import source_snapshot
from .core import MigrationError, digest, json_bytes, read_json, safe_child, snapshot, write_json
from .swiftui import tokenize
from .harness_schema import validate as validate_schema

VERSION = 1
C_SOURCE = {'.c', '.m', '.mm', '.cpp'}
C_INPUT = C_SOURCE | {'.h', '.pch', '.inc'}
PAIR_OUTPUT = {'-o', '-MT', '-MF', '--serialize-diagnostics', '-index-store-path', '-index-unit-output-path'}
SINGLE_OUTPUT = {'-c', '-MMD', '-MD', '-MP'}
FLAGS = ['-E', '-fdirectives-only', '-dD', '-CC', '-Rmodule-import']
SUPPORTED_DIRECTIVES = {'if', 'ifdef', 'ifndef', 'elif', 'else', 'endif',
                        'define', 'undef', 'include', 'include_next', 'import',
                        'pragma', 'error', 'warning', 'line', 'ident'}
MARKER = re.compile(r'^# (\d+) ("(?:[^"\\]|\\.)*")(?: ([1234 ]+))?\s*$')


def require(ok, message):
    if not ok:
        raise MigrationError('Conditional evidence: ' + message)


def _option(argv, name):
    require(argv.count(name) == 1 and argv.index(name) + 1 < len(argv), 'missing/duplicate ' + name)
    return argv[argv.index(name) + 1]


def preprocess_argv(argv):
    """Remove only known build output actions; keep all semantic arguments."""
    require(isinstance(argv, list) and argv and all(isinstance(a, str) for a in argv), 'invalid compiler argv')
    require(Path(argv[0]).is_absolute() and Path(argv[0]).name in {'clang', 'clang++'}, 'absolute Clang compiler required')
    require(not any(a.startswith(('-fplugin', '-ivfsoverlay', '-fpass-plugin')) or
                    a in {'-load', '-plugin', '-add-plugin', '-cc1', '-E', '-P', '-dM', '-dD',
                          '-fdirectives-only', '-frewrite-includes', '-fno-directives-only'}
                    for a in argv), 'unsupported compiler action/plugin/overlay')
    _option(argv, '-c')
    result, i = [], 0
    while i < len(argv):
        arg = argv[i]
        if arg in PAIR_OUTPUT:
            require(i + 1 < len(argv), 'missing output argument')
            i += 2
        elif arg in SINGLE_OUTPUT:
            i += 1
        else:
            result.append(arg)
            i += 1
    return result + FLAGS


def _build(source, bundle, expected):
    """Re-derive compiler membership from hashed original logs, not a caller list."""
    from .evidence import validate as check_bundle
    from .project_scope import resolve
    source, bundle = source.resolve(), bundle.resolve()
    validate_schema(expected, 'conditionalBuildIdentity')
    checked = check_bundle(source, bundle)
    require(checked['kind'] == 'source_build', 'source_build bundle required')
    manifest = read_json(bundle / 'manifest.json')

    def artifact(name):
        require('artifacts/' + name in manifest['artifacts'], 'missing hashed build input: ' + name)
        return safe_child(bundle / 'artifacts', name)

    require(isinstance(expected, dict) and set(expected) ==
            {'project', 'scheme', 'target', 'configuration', 'sdk', 'architecture'}, 'invalid expected_build fields')
    require(all(isinstance(v, str) and v for v in expected.values()), 'empty build identity')
    project = safe_child(source, expected['project'])
    require(project.suffix == '.xcodeproj', 'one Xcode project is required')
    commands = read_json(artifact('commands.json'))
    report = read_json(artifact('capture-report.json'))
    require(report.get('commands') == commands and report.get('build_succeeded') is True and
            report.get('source_unchanged') is True and report.get('source_sha256') == checked['source_sha256'],
            'build report/commands/source disagree')
    builds = [c for c in commands if c.get('name') == 'device-build']
    require(len(builds) == 1 and type(builds[0].get('exit_code')) is int and builds[0]['exit_code'] == 0,
            'one successful device-build command required')
    command = builds[0]
    argv = command['argv']
    require(Path(argv[0]).name == 'xcodebuild' and argv[-1] == 'build' and
            Path(command['cwd']).resolve() == source, 'invalid build action/cwd')
    require(Path(_option(argv, '-project')).resolve() == project and
            _option(argv, '-scheme') == expected['scheme'] and
            _option(argv, '-configuration') == expected['configuration'] and
            _option(argv, '-sdk') == expected['sdk'], 'selected build identity mismatch')
    settings = read_json(artifact('build-settings.json'))
    selected = [r['buildSettings'] for r in settings if r.get('target') == expected['target']]
    require(len(selected) == 1, 'ambiguous build settings target')
    settings = selected[0]
    require(settings.get('TARGET_NAME') == expected['target'] and
            settings.get('CONFIGURATION') == expected['configuration'] and
            Path(settings.get('PROJECT_FILE_PATH', '')).resolve() == project and
            settings.get('ARCHS', '').split() == [expected['architecture']] and
            settings.get('SDK_NAME', '').startswith(expected['sdk']), 'build settings mismatch')
    raw_settings = artifact('build-settings.stdout.log').read_text()
    require(read_json(artifact('build-settings.json')) == __import__('json').loads(raw_settings),
            'build settings are not the captured stdout')
    log = artifact('device-build.stdout.log').read_text().splitlines()
    require(any(line.strip() == '** BUILD SUCCEEDED **' for line in log), 'build success marker absent')
    rows = []
    for n, line in enumerate(log, 1):
        if not re.match(r'^\s*/.*?/clang(?:\+\+)? ', line):
            continue
        original = shlex.split(line)
        if '-c' not in original:
            continue
        path = Path(_option(original, '-c')).resolve()
        require(path.is_relative_to(source) and path.suffix in C_SOURCE, 'unsupported/external compilation unit')
        expanded = []
        for arg in original:
            if arg.startswith('@'):
                response = artifact('build-inputs/' + Path(arg[1:]).name).read_text()
                more = shlex.split(response)
                require(not any(a.startswith('@') for a in more), 'nested response files unsupported')
                expanded.extend(more)
            else:
                expanded.append(arg)
        require(_option(expanded, '-target').split('-')[0] == expected['architecture'] and
                Path(_option(expanded, '-isysroot')).resolve() == Path(settings['SDKROOT']).resolve(),
                'compiler target/SDK mismatch')
        rows.append({'source': path.relative_to(source).as_posix(), 'build_log_line': n,
                     'original_argv': original, 'expanded_argv': expanded,
                     'argv': preprocess_argv(expanded)})
    declared = resolve(source, {'scope': 'project-targets',
                                'project_path': expected['project'] + '/project.pbxproj',
                                'targets': [expected['target']], 'configuration': expected['configuration']})
    require(declared['target_closure'] == [expected['target']], 'multi-target conditional capture is not supported yet')
    declared_c = {p for p in declared['source_files'] if Path(p).suffix in C_SOURCE}
    require(rows and len({r['source'] for r in rows}) == len(rows) and
            {r['source'] for r in rows} == declared_c, 'incomplete/duplicate C-family compilation units')
    supplied = read_json(artifact('compile-commands.json'))
    require([(r['build_log_line'], r['original_argv'], r['expanded_argv']) for r in rows] ==
            [(r['build_log_line'], r['original_argv'], r['expanded_argv']) for r in supplied],
            'compile command summary differs from original log/response files')
    toolchain = read_json(artifact('toolchain-inputs.json'))
    expected_tools = {str(Path(r['expanded_argv'][0]).resolve()) for r in rows}
    expected_tools.add(str((Path(settings['SDKROOT']) / 'SDKSettings.json').resolve()))
    require(isinstance(toolchain, dict) and set(toolchain) == {'before', 'after'} and
            isinstance(toolchain['before'], dict) and set(toolchain['before']) == expected_tools and
            toolchain['before'] == toolchain['after'], 'build toolchain inputs absent/changed')
    require(toolchain['before'] == {p: digest(Path(p).read_bytes()) for p in expected_tools},
            'compiler/SDK changed since captured build')
    members = read_json(artifact('source-files.json')).get('source_files')
    require(isinstance(members, list) and len(set(members)) == len(members) and
            set(members) <= {f['path'] for f in source_snapshot(source)['files']} and
            {r['source'] for r in rows} <= set(members), 'invalid source members')
    derived_members = {r['source'] for r in rows}
    for row in rows:
        dep = artifact('build-inputs/' + Path(_option(row['expanded_argv'], '-MF')).name)
        dependencies = _dependency_paths(dep.read_text(), source)
        require(str(source / row['source']) in dependencies, 'build dependency output omits its compilation unit')
        derived_members.update(Path(p).relative_to(source).as_posix()
                               for p in dependencies if Path(p).is_relative_to(source))
    if 'artifacts/framework-header-provenance.json' in manifest['artifacts']:
        for row in read_json(artifact('framework-header-provenance.json')):
            original_header = safe_child(source, row['source'])
            staged = Path(row['staged'])
            framework = next((p.stem for p in staged.parents if p.suffix == '.framework'), None)
            require(framework is not None, 'non-framework module mapping unsupported')
            module_info = artifact('preprocessing/' + framework + '-module-info.txt').read_text()
            require(staged.is_absolute() and
                    ('Input file: ' + str(staged)) in module_info and
                    digest(staged.read_bytes()) == digest(original_header.read_bytes()) == row['sha256'],
                    'module dependency provenance mismatch')
            if original_header.suffix in C_SOURCE | {'.h'}:
                derived_members.add(row['source'])
    require(sorted(derived_members) == members, 'member list differs from original dependency/module inputs')
    return {'source_sha256': checked['source_sha256'], 'build_manifest_sha256': digest((bundle / 'manifest.json').read_bytes()),
            'expected_build': expected, 'rows': rows, 'members': members}


def directives(text):
    """Find actual logical directives using the existing comment/string lexer."""
    lines = text.splitlines()
    by_line = {}
    for t in tokenize(text, skip_pragma_marks=True):
        by_line.setdefault(t.line, []).append(t)
    result, continuation = {}, set()
    for n in range(1, len(lines) + 1):
        if n in continuation:
            continue
        end = n
        while end <= len(lines) and lines[end - 1].endswith('\\'):
            end += 1
        continuation.update(range(n + 1, end + 1))
        ts = by_line.get(n, [])
        if ts and ts[0].value == '#' and len(ts) > 1:
            result[n] = {'name': ts[1].value, 'end_line': min(end, len(lines))}
    return result


def marker_path(quoted):
    """Clang line markers use C byte escapes, including octal UTF-8 paths."""
    result = bytearray()
    i = 1
    escapes = {'\\': 92, '"': 34, "'": 39, '?': 63, 'a': 7, 'b': 8,
               'f': 12, 'n': 10, 'r': 13, 't': 9, 'v': 11}
    while i < len(quoted) - 1:
        char = quoted[i]
        i += 1
        if char != '\\':
            result.extend(char.encode('utf-8'))
            continue
        require(i < len(quoted) - 1, 'truncated line marker escape')
        char = quoted[i]
        if char in '01234567':
            match = re.match(r'[0-7]{1,3}', quoted[i:])
            value = int(match[0], 8)
            i += len(match[0])
        elif char == 'x':
            match = re.match(r'[0-9a-fA-F]+', quoted[i + 1:])
            require(match is not None, 'invalid line marker hex escape')
            value = int(match[0], 16)
            i += len(match[0]) + 1
        else:
            require(char in escapes, 'unsupported line marker escape')
            value = escapes[char]
            i += 1
        require(value <= 255, 'line marker escape exceeds a byte')
        result.append(value)
    try:
        path = result.decode('utf-8')
    except UnicodeDecodeError as exc:
        raise MigrationError('Conditional evidence: line marker is not UTF-8') from exc
    require(not any(ord(c) < 32 for c in path), 'line marker contains a control character')
    return path


def project_output(source, output, members):
    """Map directives-only output to separate include occurrences and source lines.

    An absent file is NOT an empty/disabled file. Never merge different occurrences
    into a synthetic translation unit. #line overrides are conservatively refused.
    """
    source = source.resolve()
    texts = {p: safe_child(source, p).read_text(encoding='utf-8-sig')
             for p in members if Path(p).suffix in C_INPUT}
    ds = {p: directives(t) for p, t in texts.items()}
    for p, items in ds.items():
        require(not any(d['name'] == 'line' or d['name'].isdigit() for d in items.values()),
                'source #line remapping unsupported: ' + p)
    # A marker-shaped line inside a retained comment/string is not a directive.
    marker_lines = {t.line for t in tokenize(output, language="c") if t.value == '#'}
    views, stack = [], []
    current, line_no = None, 1
    for output_line, raw in enumerate(output.splitlines(), 1):
        marker = MARKER.fullmatch(raw) if output_line in marker_lines else None
        if marker:
            absolute = marker_path(marker[2])
            flags = (marker[3] or '').split()
            rel = None
            if not absolute.startswith('<'):
                file = Path(absolute)
                if not file.is_absolute():
                    file = source / file
                file = file.resolve()
                if file.is_relative_to(source):
                    rel = file.relative_to(source).as_posix()
                    require(rel in texts, 'unaccounted textual source input: ' + rel)
            if '1' in flags:
                stack.append(current)
                current = None
            elif '2' in flags:
                current = stack.pop() if stack else None
            if rel is None:
                current = None
            elif current is None or current['path'] != rel:
                current = {'path': rel, 'instance': len(views), 'active_lines': set()}
                views.append(current)
            line_no = int(marker[1])
            continue
        if current and raw.strip():
            p = current['path']
            source_lines = texts[p].splitlines()
            require(1 <= line_no <= len(source_lines), 'output location outside source: ' + p)
            directive = ds[p].get(line_no)
            # Clang module imports are emitted pragmas, not original source code.
            if output_line in marker_lines and raw.lstrip().startswith('#pragma'):
                pass
            elif directive:
                require(directive['name'] not in {'if', 'ifdef', 'ifndef', 'elif', 'else', 'endif'},
                        'unevaluated conditional in directives-only output')
                current['active_lines'].update(range(line_no, directive['end_line'] + 1))
            else:
                # FD-only leaves code unexpanded. Preserve all spliced physical lines.
                end = line_no
                while end <= len(source_lines) and source_lines[end - 1].endswith('\\'):
                    end += 1
                current['active_lines'].update(range(line_no, min(end, len(source_lines)) + 1))
        line_no += 1
    return [{**v, 'active_lines': sorted(v['active_lines'])} for v in views]


def _dependency_paths(text, cwd):
    flattened = text.replace('\\\n', '')
    require(': ' in flattened, 'invalid Clang dependency output')
    return {str((Path(cwd) / p).resolve()) for p in shlex.split(flattened.split(': ', 1)[1])}


def compare_branches(source, direct_views, expanded_views):
    """Reject FD-only differences caused by stateful non-directive macros.

    For example __COUNTER__ or _Pragma can change a subsequent #if in a normal
    compilation. A second, fully expanding Clang pass is the independent branch
    observation. Empty expansions or ambiguous locations fail conservatively.
    """
    by_path = []
    for views in (direct_views, expanded_views):
        groups = {}
        for view in views:
            groups.setdefault(view['path'], []).append(set(view['active_lines']))
        by_path.append(groups)
    require(set(by_path[0]) == set(by_path[1]), 'directives-only/full preprocessing include sets differ')
    for path, direct in by_path[0].items():
        expanded = by_path[1][path]
        require(len(direct) == len(expanded), 'preprocessing include occurrences differ: ' + path)
        text = safe_child(source, path).read_text(encoding='utf-8-sig')
        require('%:' not in text and '??=' not in text, 'alternative directives require a dedicated provider')
        ds, stack, regions, control = directives(text), [], [], set()
        require(all(d['name'] in SUPPORTED_DIRECTIVES for d in ds.values()),
                'unsupported or spliced directive name: ' + path)
        for line, directive in sorted(ds.items()):
            kind, end = directive['name'], directive['end_line']
            if kind in {'if', 'ifdef', 'ifndef'}:
                stack.append(end + 1)
            elif kind in {'elif', 'else'}:
                require(bool(stack), 'unbalanced conditional directive')
                regions.append((stack.pop(), line - 1))
                stack.append(end + 1)
            elif kind == 'endif':
                require(bool(stack), 'unbalanced conditional directive')
                regions.append((stack.pop(), line - 1))
            if kind in {'if', 'ifdef', 'ifndef', 'elif', 'else', 'endif'}:
                control.update(range(line, end + 1))
        require(not stack, 'unterminated conditional directive')
        code = {t.line for t in tokenize(text, skip_pragma_marks=True)} - control
        for a, b in zip(direct, expanded):
            for start, end in regions:
                relevant = {n for n in code if start <= n <= end}
                require(bool(relevant & a) == bool(relevant & b),
                        'directives-only/full preprocessing branch disagreement: ' + path + ':' + str(start))


def _file_inputs(argv):
    result = set()
    for arg in argv:
        # Includes prefix/PCH, header maps, explicit PCM, SDK stat cache, compiler.
        value = arg.rsplit('=', 1)[-1] if '=' in arg else arg
        p = Path(value)
        if p.is_absolute() and p.is_file():
            result.add(str(p.resolve()))
        if p.is_absolute() and p.is_dir() and (p / 'SDKSettings.json').is_file():
            result.add(str((p / 'SDKSettings.json').resolve()))
    return result


def _module_paths(stderr, stdout=''):
    matches = re.findall(r"remark: importing module '[^']+'(?: into '[^']+')? from '([^']+)' \[-Rmodule-import\]", stderr)
    tokens = tokenize(stdout, language="c")
    values = [t.value for t in tokens]
    has_import = any(values[i:i+5] == ['#', 'pragma', 'clang', 'module', 'import']
                     and tokens[i].line == tokens[i+4].line for i in range(max(0, len(values)-4)))
    require(not (has_import and not matches),
            'module imports lack actual PCM loading evidence')
    require(all(Path(p).is_absolute() and Path(p).suffix == '.pcm' for p in matches),
            'invalid imported PCM path')
    return {str(Path(p).resolve()) for p in matches}


def simple_guard(text):
    """Only a whole-header, empty-definition, non-redefined include guard.

    An imported enum definition can witness entry into this sole conditional.
    Other module conditionals deliberately have no exemption.
    """
    # Alternative directive spellings and spliced directive names need a full
    # preprocessing record; never classify them as an unconditional guard body.
    if '%:' in text or '??=' in text:
        return None
    tokens = tokenize(text, skip_pragma_marks=True)
    values = [t.value for t in tokens]
    ds = directives(text)
    if any(d['name'] not in SUPPORTED_DIRECTIVES for d in ds.values()):
        return None
    if any(n != d['end_line'] for n, d in ds.items()):
        return None
    conditionals = [(n, d) for n, d in ds.items()
                    if d['name'] in {'if', 'ifdef', 'ifndef', 'elif', 'else', 'endif'}]
    if (len(conditionals) != 2 or conditionals[0][1]['name'] != 'ifndef' or
            conditionals[-1][1]['name'] != 'endif' or len(values) < 8 or
            values[:2] != ['#', 'ifndef'] or values[-2:] != ['#', 'endif']):
        return None
    guard = values[2]
    if values[3:6] != ['#', 'define', guard] or values.count(guard) != 2:
        return None
    first, last = conditionals[0][0], conditionals[-1][0]
    definition = tokens[3].line
    if [t.value for t in tokens if t.line == definition] != ['#', 'define', guard]:
        return None
    # Require an actual named enum declaration, not an arbitrary symbol guess.
    for i in range(6, len(values) - 7):
        if (values[i:i+3] == ['typedef', 'NS_ENUM', '('] and values[i+4] == ',' and
                values[i+6:i+8] == [')', '{']):
            return {'guard': guard, 'symbol': values[i+5], 'line': tokens[i+5].line,
                    'body_start': definition + 1, 'body_end': last - 1}
        if values[i] == 'enum' and values[i+2] == '{' and re.fullmatch(r'[A-Za-z_]\w*', values[i+1]):
            return {'guard': guard, 'symbol': values[i+1], 'line': tokens[i+1].line,
                    'body_start': definition + 1, 'body_end': last - 1}
    return None


def _module_candidates(source, build, original, observed):
    manifest = read_json(build / 'manifest.json')
    name = 'artifacts/framework-header-provenance.json'
    if name not in manifest['artifacts']:
        return []
    provenance = read_json(build / name)
    require(isinstance(provenance, list), 'invalid module header provenance')
    candidates = []
    for row in provenance:
        path = row.get('source')
        if path not in original['members'] or path in observed or Path(path).suffix != '.h':
            continue
        file = safe_child(source, path)
        guard = simple_guard(file.read_text(encoding='utf-8-sig'))
        if guard is None:
            continue
        staged = Path(row['staged'])
        require(staged.is_absolute() and staged.is_file() and
                digest(staged.read_bytes()) == digest(file.read_bytes()) == row['sha256'],
                'module header source/copy mismatch')
        candidates.append({'path': path, 'staged': str(staged), 'guard': guard})
    require(len({c['path'] for c in candidates}) == len(candidates), 'duplicate module header mapping')
    return candidates


def _guard_witness(source, candidate, raw):
    import json
    decoder, remaining, nodes = json.JSONDecoder(), raw.lstrip(), []
    while remaining:
        node, end = decoder.raw_decode(remaining)
        nodes.append(node)
        remaining = remaining[end:].lstrip()
    guard = candidate['guard']
    data = safe_child(source, candidate['path']).read_bytes()
    for node in nodes:
        if not isinstance(node, dict):
            continue
        loc = node.get('loc', {})
        loc = loc.get('spellingLoc', loc)
        offset = loc.get('offset')
        end = node.get('range', {}).get('end', {})
        end_offset = end.get('offset')
        # Imported PCM enum constants may remain lazy even with ast-dump-all.
        # A direct source closing brace distinguishes the actual definition from
        # NS_ENUM's synthetic forward declaration; macro-generated ends don't.
        definition_end = (type(end_offset) is int and type(offset) is int and
                          0 <= offset < end_offset < len(data) and
                          end.get('file', candidate['staged']) == candidate['staged'] and
                          end.get('tokLen') == 1 and data[end_offset:end_offset+1] == b'}' and
                          end.get('line') == data[:end_offset].count(b'\n') + 1 and
                          'spellingLoc' not in end and 'expansionLoc' not in end)
        if (node.get('kind') == 'EnumDecl' and node.get('name') == guard['symbol'] and
                loc.get('file') == candidate['staged'] and loc.get('line') == guard['line'] and
                type(offset) is int and offset >= 0 and
                data[offset:offset + len(guard['symbol'])] == guard['symbol'].encode() and
                (definition_end or any(n.get('kind') == 'EnumConstantDecl' for n in node.get('inner', [])))):
            return True
    return False


def capture(project, config_path, output):
    from .native_pipeline import context
    source, project = context(project)
    cfg = read_json(config_path)
    validate_schema(cfg, 'conditionalConfig')
    require(isinstance(cfg, dict) and set(cfg) <=
            {'schema_version', 'build_evidence', 'expected_build', 'timeout_seconds'} and cfg.get('schema_version') == VERSION,
            'unsupported capture config')
    timeout = cfg.get('timeout_seconds', 300)
    require(type(timeout) is int and 1 <= timeout <= 3600, 'invalid timeout')
    output = output.resolve()
    require(output.is_relative_to((project / 'spec/ref/ios-conditional-evidence').resolve()) and
            not output.exists(), 'choose a fresh project/spec/ref/ios-conditional-evidence directory')
    build = Path(cfg['build_evidence']).resolve()
    require(build.is_relative_to((project / 'spec/ref').resolve()), 'build evidence must be project-local')
    original = _build(source, build, cfg['expected_build'])
    output.mkdir(parents=True)
    write_json(output / 'config.json', cfg)
    records, inputs = [], {}
    try:
        for index, row in enumerate(original['rows']):
            name = f'tu-{index:04d}'
            argv = row['argv'] + ['-MD', '-MF', str(output / (name + '.d'))]
            paths = _file_inputs(row['expanded_argv'])
            before = {p: digest(Path(p).read_bytes()) for p in paths}
            started = datetime.datetime.now().astimezone().isoformat()
            with (output / (name + '.i')).open('wb') as out, (output / (name + '.stderr.log')).open('wb') as err:
                process = subprocess.run(argv, cwd=source, stdout=out, stderr=err, timeout=timeout)
            record = {'source': row['source'], 'argv': argv, 'cwd': str(source),
                      'started_at': started, 'exit_code': process.returncode,
                      'stdout': name + '.i', 'stderr': name + '.stderr.log', 'dependencies': name + '.d'}
            records.append(record)
            write_json(output / 'commands.json', records)
            require(process.returncode == 0, 'preprocessor failed: ' + row['source'])
            require(before == {p: digest(Path(p).read_bytes()) for p in before}, 'compiler inputs changed during capture')
            paths |= _dependency_paths((output / (name + '.d')).read_text(), source)
            paths |= _module_paths((output / record['stderr']).read_text(), (output / record['stdout']).read_text())
            for p in paths:
                value = digest(Path(p).read_bytes())
                require(p not in inputs or inputs[p] == value, 'input changed between compilation units')
                inputs[p] = value
            record['views'] = project_output(source, (output / record['stdout']).read_text(), original['members'])
            require(any(v['path'] == row['source'] for v in record['views']), 'main file observation missing')
            full_argv = [a for a in argv if a != '-fdirectives-only']
            full_argv[-1] = str(output / (name + '.full.d'))
            with (output / (name + '.full.i')).open('wb') as out, (output / (name + '.full.stderr.log')).open('wb') as err:
                full = subprocess.run(full_argv, cwd=source, stdout=out, stderr=err, timeout=timeout)
            record['full'] = {'argv': full_argv, 'exit_code': full.returncode,
                              'stdout': name + '.full.i', 'stderr': name + '.full.stderr.log',
                              'dependencies': name + '.full.d'}
            require(full.returncode == 0, 'full preprocessor failed: ' + row['source'])
            full_views = project_output(source, (output / record['full']['stdout']).read_text(), original['members'])
            compare_branches(source, record['views'], full_views)
            paths = _dependency_paths((output / record['full']['dependencies']).read_text(), source)
            paths |= _module_paths((output / record['full']['stderr']).read_text(), (output / record['full']['stdout']).read_text())
            for p in paths:
                value = digest(Path(p).read_bytes())
                require(p not in inputs or inputs[p] == value, 'input changed during full preprocessing')
                inputs[p] = value
        observed = {v['path'] for r in records for v in r['views']}
        guards = []
        for index, candidate in enumerate(_module_candidates(source, build, original, observed)):
            row = original['rows'][0]
            name = f'guard-{index:04d}'
            argv = row['argv'][:-len(FLAGS)] + ['-fsyntax-only', '-Rmodule-import',
                    '-Xclang', '-ast-dump-all=json', '-Xclang', '-ast-dump-filter=' + candidate['guard']['symbol']]
            with (output / (name + '.json')).open('wb') as out, (output / (name + '.stderr.log')).open('wb') as err:
                process = subprocess.run(argv, cwd=source, stdout=out, stderr=err, timeout=timeout)
            require(process.returncode == 0, 'module guard AST observation failed')
            witnessed = _guard_witness(source, candidate, (output / (name + '.json')).read_text())
            guards.append({'candidate': candidate, 'unit': row['source'], 'argv': argv,
                           'cwd': str(source), 'exit_code': process.returncode, 'witnessed': witnessed,
                           'stdout': name + '.json', 'stderr': name + '.stderr.log'})
            paths = {str(Path(candidate['staged']).resolve())} | _module_paths((output / (name + '.stderr.log')).read_text())
            for p in paths:
                value = digest(Path(p).read_bytes())
                require(p not in inputs or inputs[p] == value, 'module changed during AST observation')
                inputs[p] = value
        require(source_snapshot(source)['sha256'] == original['source_sha256'], 'source changed during capture')
        require(inputs == {p: digest(Path(p).read_bytes()) for p in inputs}, 'capture input changed before sealing')
        write_json(output / 'guards.json', guards)
        write_json(output / 'commands.json', records)
        write_json(output / 'inputs.json', inputs)
        files = {p.name: digest(p.read_bytes()) for p in output.iterdir() if p.is_file()}
        report = {'schema_version': VERSION, 'kind': 'clang_directives_only',
                  'source_sha256': original['source_sha256'], 'build_evidence': str(build),
                  'build_manifest_sha256': original['build_manifest_sha256'],
                  'expected_build': cfg['expected_build'], 'artifacts': files,
                  'scope': 'textually_observed_compilation_units_and_include_occurrences',
                  'capture_authenticity': 'not_verified', 'behavior_equivalence': 'not_verified'}
        write_json(output / 'manifest.json', report)
        validate(source, output, project=project)
        return {'status': 'captured', 'path': str(output), 'translation_units': len(records),
                'behavior_verified': False}
    except (MigrationError, OSError, ValueError, subprocess.SubprocessError) as exc:
        write_json(output / 'failure.json', {'status': 'capture_failed', 'error': str(exc)})
        raise


def validate(source, output, *, project=None):
    output = Path(output).resolve()
    if project is not None:
        require(output.is_relative_to((project / 'spec/ref/ios-conditional-evidence').resolve()), 'capture outside pinned directory')
    require(not (output / 'failure.json').exists(), 'failed capture cannot be consumed')
    report = read_json(output / 'manifest.json')
    if report.get('kind') == 'compiler_source_views':
        from .conditional_views import validate as validate_views
        return validate_views(source, output, project=project)
    validate_schema(report, 'conditionalManifest')
    require(isinstance(report, dict) and set(report) ==
            {'schema_version', 'kind', 'source_sha256', 'build_evidence', 'build_manifest_sha256',
             'expected_build', 'artifacts', 'scope', 'capture_authenticity', 'behavior_equivalence'} and
            report['schema_version'] == VERSION and report['kind'] == 'clang_directives_only' and
            report['capture_authenticity'] == 'not_verified' and report['behavior_equivalence'] == 'not_verified' and
            report['scope'] == 'textually_observed_compilation_units_and_include_occurrences',
            'unsupported conditional evidence manifest')
    artifacts = report['artifacts']
    require(isinstance(artifacts, dict) and {'commands.json', 'inputs.json', 'config.json', 'guards.json'} <= artifacts.keys(),
            'capture artifacts missing')
    for name, expected in artifacts.items():
        require(Path(name).name == name and name not in {'manifest.json', 'failure.json'} and
                digest(safe_child(output, name).read_bytes()) == expected, 'missing/modified artifact: ' + name)
    build = Path(report['build_evidence']).resolve()
    if project is not None:
        require(build.is_relative_to((project / 'spec/ref').resolve()), 'build bundle outside project')
    original = _build(source, build, report['expected_build'])
    require(original['source_sha256'] == report['source_sha256'] and
            original['build_manifest_sha256'] == report['build_manifest_sha256'], 'source/build evidence changed')
    cfg = read_json(output / 'config.json')
    validate_schema(cfg, 'conditionalConfig')
    require(cfg.get('expected_build') == report['expected_build'] and
            Path(cfg.get('build_evidence', '')).resolve() == build, 'capture config mismatch')
    inputs = read_json(output / 'inputs.json')
    require(isinstance(inputs, dict) and inputs, 'input fingerprints absent')
    for path, expected in inputs.items():
        require(Path(path).is_absolute() and Path(path).is_file() and digest(Path(path).read_bytes()) == expected,
                'live compiler/dependency input missing or changed: ' + path)
    records = read_json(output / 'commands.json')
    require(isinstance(records, list) and len(records) == len(original['rows']), 'incomplete captured compilation units')
    observed, required_inputs = {}, set()
    for index, (record, row) in enumerate(zip(records, original['rows'])):
        name = f'tu-{index:04d}'
        stdout, stderr, deps = name + '.i', name + '.stderr.log', name + '.d'
        require({stdout, stderr, deps} <= artifacts.keys(), 'missing per-unit artifacts')
        require(record.get('source') == row['source'] and record.get('argv') ==
                row['argv'] + ['-MD', '-MF', str(output / deps)] and
                record.get('cwd') == str(source.resolve()) and type(record.get('exit_code')) is int and
                record['exit_code'] == 0 and record.get('stdout') == stdout and record.get('stderr') == stderr and
                record.get('dependencies') == deps, 'command/action/exit status mismatch')
        required_inputs |= _file_inputs(row['expanded_argv'])
        required_inputs |= _dependency_paths((output / deps).read_text(), source)
        required_inputs |= _module_paths((output / stderr).read_text(), (output / stdout).read_text())
        views = project_output(source, (output / stdout).read_text(), original['members'])
        require(views == record.get('views') and any(v['path'] == row['source'] for v in views),
                'derived source views differ from raw output')
        full = record.get('full', {})
        full_stdout, full_stderr, full_deps = name + '.full.i', name + '.full.stderr.log', name + '.full.d'
        full_argv = [a for a in record['argv'] if a != '-fdirectives-only']
        full_argv[-1] = str(output / full_deps)
        require({full_stdout, full_stderr, full_deps} <= artifacts.keys() and
                full.get('argv') == full_argv and type(full.get('exit_code')) is int and full['exit_code'] == 0 and
                full.get('stdout') == full_stdout and full.get('stderr') == full_stderr and
                full.get('dependencies') == full_deps, 'missing/modified full preprocessing observation')
        full_views = project_output(source, (output / full_stdout).read_text(), original['members'])
        compare_branches(source, views, full_views)
        required_inputs |= _dependency_paths((output / full_deps).read_text(), source)
        required_inputs |= _module_paths((output / full_stderr).read_text(), (output / full_stdout).read_text())
        for view in views:
            observed.setdefault(view['path'], []).append(
                {'unit': row['source'], 'instance': view['instance'], 'active_lines': view['active_lines']})
    candidates = _module_candidates(source, build, original, observed)
    guards = read_json(output / 'guards.json')
    require(isinstance(guards, list) and len(guards) == len(candidates), 'module guard attempts incomplete')
    for index, (record, candidate) in enumerate(zip(guards, candidates)):
        row, name = original['rows'][0], f'guard-{index:04d}'
        stdout, stderr = name + '.json', name + '.stderr.log'
        expected_argv = row['argv'][:-len(FLAGS)] + ['-fsyntax-only', '-Rmodule-import',
                         '-Xclang', '-ast-dump-all=json', '-Xclang', '-ast-dump-filter=' + candidate['guard']['symbol']]
        require({stdout, stderr} <= artifacts.keys() and record.get('candidate') == candidate and
                record.get('unit') == row['source'] and record.get('argv') == expected_argv and
                record.get('cwd') == str(source.resolve()) and type(record.get('exit_code')) is int and
                record['exit_code'] == 0 and record.get('stdout') == stdout and record.get('stderr') == stderr,
                'invalid module guard command or provenance')
        witnessed = _guard_witness(source, candidate, (output / stdout).read_text())
        require(type(record.get('witnessed')) is bool and record['witnessed'] == witnessed,
                'module guard witness differs from original AST')
        required_inputs.add(str(Path(candidate['staged']).resolve()))
        required_inputs |= _module_paths((output / stderr).read_text())
        if witnessed:
            guard = candidate['guard']
            observed[candidate['path']] = [{'unit': row['source'], 'instance': 'module-guard-' + str(index),
                'active_lines': list(range(guard['body_start'], guard['body_end'] + 1))}]
    require(set(inputs) == required_inputs, 'dependency input fingerprint set mismatch')
    return {'reference': {'path': str(output), 'manifest_sha256': digest((output / 'manifest.json').read_bytes()),
                          'build_manifest_sha256': original['build_manifest_sha256']},
            'members': original['members'], 'observed': observed,
            'expected_build': original['expected_build']}


def frozen_inputs(project, graph):
    ref = graph.get('conditional_evidence')
    if ref is None:
        return {}
    source = Path(read_json(project / '.migbot/config.json')['ios']).resolve()
    checked = validate(source, Path(ref['path']), project=project)
    require(checked['reference'] == ref, 'conditional evidence reference changed')
    output = Path(ref['path'])
    report = read_json(output / 'manifest.json')
    if report.get('kind') == 'compiler_source_views':
        from .conditional_views import frozen_inputs as view_inputs
        return view_inputs(project, output)
    build = Path(report['build_evidence'])
    paths = [output / 'manifest.json', build / 'manifest.json']
    paths += [safe_child(output, p) for p in report['artifacts']]
    paths += [safe_child(build, p) for p in read_json(build / 'manifest.json')['artifacts']]
    return {p.relative_to(project).as_posix(): digest(p.read_bytes()) for p in paths}
