"""Resolve a real selected Swift call with the pinned Apple compiler context.

This is semantic source evidence, never a build or runtime verdict. Unsupported
contexts and compiler/debug-format changes leave the existing binding debt.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import shlex
import subprocess
import tempfile

from hmigbot_ios.apple_tools import environment
from hmigbot_ios.core import MigrationError, read_json


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def constructor_declarations(output, path, line, column):
    """Read constructor callees, excluding generated builder value references."""
    where = re.escape(str(path)) + ':' + str(line) + ':' + str(column)
    stack, declarations = [], set()
    for row in output.splitlines():
        node = re.match(r'^(\s*)\((\w+)\b', row)
        if not node:
            continue
        indent = len(node[1])
        while stack and stack[-1][0] >= indent:
            stack.pop()
        if (node[2] == 'declref_expr' and stack and stack[-1][1] == 'constructor_ref_call_expr'
                and re.search(r' location=' + where + r'\s', row)):
            found = re.search(r' decl="([^"]+)"', row)
            if found:
                declarations.add(found[1])
        stack.append((indent, node[2]))
    return declarations


def context(source, name, guard):
    if not source.view or not source.selection:
        raise MigrationError('Semantic binding needs the pinned Release compiler context')
    artifact = source.view.artifact
    owners = [r['targets'] for r in source.selection['source_membership'] if r['path'] == name]
    if len(owners) != 1 or len(owners[0]) != 1:
        raise MigrationError('Semantic binding needs one selected target for its Source file')
    target = owners[0][0]
    settings = artifact['settings_targets'][target]
    module = settings['PRODUCT_MODULE_NAME']
    requests = []
    for rel in artifact['inputs']:
        if not re.fullmatch(r'provider/[^/]+/request\.json', rel):
            continue
        path = source.view.root / rel
        value = read_json(path)
        if any(f['path'] == name for f in value.get('files', [])):
            guard.add(path)
            requests.append(value['compiler_context'])
    contexts = {json.dumps(c, sort_keys=True): c for c in requests}
    if len(contexts) != 1:
        raise MigrationError('No unique pinned compiler context for this Source file')
    ctx = next(iter(contexts.values()))
    info, env = environment()
    if ctx['toolchain'] != info or ctx['swiftc'] != info['swiftc']:
        raise MigrationError('Pinned compiler/toolchain differs from the selected Xcode')
    checks = [c for c in artifact.get('compiler_argument_checks', []) if c.get('module') == module]
    commands = [a for c in checks for a in c.get('compiler_arguments', [])]
    lists = {Path(a[1:]).resolve() for c in commands for a in c if a.startswith('@')}
    if len(lists) != 1:
        raise MigrationError('Semantic binding needs the captured target SwiftFileList')
    file_list = next(iter(lists))
    guard.add(file_list)
    paths = [Path(n).resolve() for n in shlex.split(file_list.read_text())]
    members = {r['path'] for r in source.selection['source_membership']
               if target in r['targets'] and r['path'].endswith('.swift')}
    selected = {p.relative_to(source.root).as_posix() for p in paths if p.is_relative_to(source.root)}
    if selected != members or not members <= source.files or len(paths) != len(set(paths)):
        raise MigrationError('Captured target file list differs from selected Source membership')
    inputs = []
    for path in paths:
        guard.add(path)
        if path.is_relative_to(source.root):
            rel = path.relative_to(source.root).as_posix()
            text = source.text(rel)
        else:
            # Retain generated inputs from the captured build, rather than
            # pretending declared repository members are the whole module.
            rel = None
            text = path.read_text(encoding='utf-8-sig')
        inputs.append({'path': path, 'source_file': rel, 'text': text,
                       'raw_sha256': _sha(path.read_bytes()), 'view_sha256': _sha(text.encode())})
    return ctx, info, env, module, inputs, file_list


def resolved_call(index, file, call):
    """Return one deduplicated declaration at the exact real call location."""
    source = index.source
    name = file.name
    guard = index.guard
    ctx, info, env, module, inputs, file_list = context(source, name, guard)
    callee = file.span(call['value']['callee_name_span'])
    if not call['start'] <= callee['start'] < callee['end'] <= call['end']:
        raise MigrationError('Swift callee name is outside its parsed call')
    prefix = file.text[:callee['start']]
    line = prefix.count('\n') + 1
    column = len(prefix.rsplit('\n', 1)[-1].encode('utf-8')) + 1
    with tempfile.TemporaryDirectory(prefix='hmigbot-swift-binding-') as directory:
        root = Path(directory)
        mapped = {}
        for offset, item in enumerate(inputs):
            dest = root / str(offset) / item['path'].name
            dest.parent.mkdir()
            dest.write_text(item['text'], encoding='utf-8')
            mapped[item['path']] = dest
        primary = mapped[source.root / name]
        driver = [ctx['swiftc'], '-typecheck', '-dump-ast', '-parse-as-library',
                  *ctx['arguments'], '-module-name', module, *map(str, mapped.values())]
        jobs = subprocess.run(driver + ['-driver-print-jobs'], env=env, capture_output=True,
                              text=True, timeout=60)
        if jobs.returncode:
            raise MigrationError('Apple semantic driver failed: ' + jobs.stderr[-1500:])
        candidates = [shlex.split(row) for row in jobs.stdout.splitlines() if row.strip()]
        candidates = [a for a in candidates if '-primary-file' in a
                      and a[a.index('-primary-file') + 1] == str(primary)]
        if len(candidates) != 1:
            raise MigrationError('Apple driver did not yield one real primary-file semantic job')
        job = candidates[0]
        trace = root / 'modules.json'
        check_job = ['-typecheck' if a == '-dump-ast' else a for a in job]
        check_job += ['-emit-loaded-module-trace-path', str(trace)]
        guard.verify()
        checked = subprocess.run(check_job, env=env, capture_output=True, text=True, timeout=180)
        if checked.returncode or not trace.is_file():
            raise MigrationError('Apple typecheck/module trace failed: ' + checked.stderr[-1500:])
        modules = read_json(trace)
        paths = modules.get('swiftmodules')
        if not isinstance(paths, list) or not paths:
            raise MigrationError('Apple module trace did not identify loaded Swift modules')
        loaded = {str(Path(p).resolve()): guard.add(Path(p)) for p in paths}
        macros = {str(Path(p['path']).resolve()): guard.add(Path(p['path']))
                  for p in modules.get('swiftmacros', [])}
        # Compiler-generated macro expansions are resolved by the same job;
        # retain the official trace and plugin arguments as evidence.
        guard.verify()
        ast = subprocess.run(job, env=env, capture_output=True, text=True, timeout=180)
        if ast.returncode:
            raise MigrationError('Apple real Source AST failed: ' + ast.stderr[-1500:])
        declarations = constructor_declarations(ast.stdout + '\n' + ast.stderr, primary, line, column)
        # Result-builder expansion can print the same reference repeatedly.
        # Conflicting declarations at one location remain ambiguous.
        if len(declarations) != 1:
            raise MigrationError('No unique resolved declaration at the real Swift call')
        declaration = next(iter(declarations))
        guard.verify()
        return {'kind': 'Apple real Source typecheck and AST binding', 'declaration': declaration,
                'file': name, 'line': line, 'utf8_column': column, 'start': call['start'], 'end': call['end'],
                'target_module': module, 'source_sha256': source.fingerprint,
                'compiler_context': ctx, 'swift_file_list': str(file_list),
                'swift_file_list_sha256': _sha(file_list.read_bytes()),
                'inputs': [{k: str(v) if isinstance(v, Path) else v for k, v in p.items() if k != 'text'} for p in inputs],
                'path_mapping': {str(p): str(q) for p, q in mapped.items()},
                'driver_argv': driver, 'typecheck_argv': check_job, 'ast_argv': job,
                'typecheck_exit': checked.returncode, 'ast_exit': ast.returncode,
                'ast_sha256': _sha(ast.stdout.encode()), 'ast_stderr_sha256': _sha(ast.stderr.encode()),
                'module_trace': modules, 'loaded_module_sha256': loaded,
                'loaded_macro_sha256': macros,
                'job_difference': {'replace': ['-dump-ast', '-typecheck'],
                                   'append': ['-emit-loaded-module-trace-path', str(trace)]},
                'typecheck_warnings': checked.stderr, 'ast_diagnostics': ast.stderr,
                'mode': 'isolated configured Source; non-WMO primary-file semantic analysis, not the original build job or runtime verification'}


def verify_binding(proof):
    """Imported/generated input changes invalidate a previously published proof."""
    inputs = dict(proof['loaded_module_sha256'])
    inputs.update(proof['loaded_macro_sha256'])
    inputs[proof['swift_file_list']] = proof['swift_file_list_sha256']
    inputs.update({p['path']: p['raw_sha256'] for p in proof['inputs']})
    for name, digest in inputs.items():
        path = Path(name)
        if not path.is_file() or _sha(path.read_bytes()) != digest:
            raise MigrationError('Native semantic binding dependency changed: ' + name)
