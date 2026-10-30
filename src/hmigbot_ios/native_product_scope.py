"""Adapt actual Xcode build graphs/products into a bounded native product scope.

Xcode owns the graph and settings; this adapter selects the requested root and
its physically embedded app extensions. Compiler inputs still come exclusively
from source_build_membership. No caller-authored source allowlist is accepted.
"""
from pathlib import Path
import json
import plistlib
import re

from .core import source_snapshot
from .core import MigrationError, digest, json_bytes, read_json, safe_child, snapshot, write_json

ARTIFACT = 'target-scope.json'


def require(ok, message):
    if not ok:
        raise MigrationError('Native product scope: ' + message)


def build_graph(text):
    lines = text.splitlines()
    starts = [(i, re.search(r'Target dependency graph \((\d+) targets?\)', line))
              for i, line in enumerate(lines) if 'Target dependency graph (' in line]
    if not starts:
        return None
    require(len(starts) == 1 and starts[0][1] is not None, 'ambiguous build dependency graph')
    index, match = starts[0]
    graph, current = {}, None
    for line in lines[index + 1:]:
        if not line.strip():
            break
        target = re.fullmatch(r"\s+Target '([^']+)' in project '([^']+)'(?: \(no dependencies\))?", line)
        dependency = re.fullmatch(r"\s+➜ (?:Explicit|Implicit) dependency on target '([^']+)' in project '([^']+)'(?: via .+)?", line)
        if target:
            current = (target[2], target[1])
            require(current not in graph, 'duplicate target graph node')
            graph[current] = set()
        elif dependency and current is not None:
            graph[current].add((dependency[2], dependency[1]))
        else:
            raise MigrationError('Native product scope: unsupported dependency graph line: ' + line)
    require(len(graph) == int(match[1]), 'incomplete dependency graph')
    require(all(dep in graph for deps in graph.values() for dep in deps), 'dependency graph omits a target')
    return graph


def closure(graph, root):
    require(root in graph, 'root target absent from build dependency graph')
    done, active = set(), set()
    def visit(key):
        require(key not in active, 'cyclic dependency graph')
        if key in done:
            return
        active.add(key)
        for child in graph[key]:
            visit(child)
        active.remove(key); done.add(key)
    visit(root)
    require(len({name for _, name in done}) == len(done), 'same target name in different projects is ambiguous')
    return done


def target_row(rows, name):
    require(isinstance(rows, list) and bool(rows), 'empty build settings')
    for row in rows:
        require(isinstance(row, dict) and not row.get('error') and isinstance(row.get('buildSettings'), dict),
                'build settings contain an error or invalid row')
    found = [r for r in rows if r.get('target', r['buildSettings'].get('TARGET_NAME')) == name]
    require(len(found) == 1 and found[0]['buildSettings'].get('TARGET_NAME') == name,
            'expected exactly one settings row for ' + name)
    return found[0]


def context_matches(row, root, configuration, sdk, architectures):
    b = row['buildSettings']
    require(b.get('CONFIGURATION') == configuration and isinstance(b.get('SDK_NAME'), str)
            and b['SDK_NAME'].startswith(sdk) and isinstance(b.get('ARCHS'), str)
            and set(architectures) <= set(b['ARCHS'].split()),
            'configuration, SDK or architecture differs: ' + row['target'])
    require(isinstance(b.get('PROJECT_FILE_PATH'), str) and bool(b['PROJECT_FILE_PATH'])
            and isinstance(root.get('PROJECT_FILE_PATH'), str) and bool(root['PROJECT_FILE_PATH'])
            and isinstance(root.get('PROJECT_NAME'), str) and bool(root['PROJECT_NAME']), 'invalid project settings')
    require(b.get('PROJECT_NAME') == root.get('PROJECT_NAME')
            and Path(b.get('PROJECT_FILE_PATH', '')).resolve() == Path(root.get('PROJECT_FILE_PATH', '')).resolve(),
            'target belongs to a different project: ' + row['target'])


def regular_child(root, path):
    root, path = Path(root).resolve(), Path(path)
    require(path.resolve().is_relative_to(root) and path.resolve() != root, 'product escapes captured DerivedData')
    # Normalize only trusted system aliases; do not resolve a product symlink
    # before examining every component below DerivedData.
    from .core import trusted_system_alias
    path = path.absolute()
    for alias in ('/tmp', '/var'):
        if (path == Path(alias) or str(path).startswith(alias + '/')) and trusted_system_alias(Path(alias)):
            path = Path('/private' + str(path))
    try:
        parts = path.relative_to(root).parts
    except ValueError as exc:
        raise MigrationError('Native product scope: noncanonical product path') from exc
    cursor = root
    for part in parts:
        cursor = cursor / part
        require(not cursor.is_symlink() and not (hasattr(cursor, 'is_junction') and cursor.is_junction()),
                'linked product or metadata path')
    return path.resolve()


def capture_scope(source, derived, capture, rows, *, root_target, scheme, configuration,
                  sdk, architectures, source_sha256, command, allow_non_application=False):
    """Capture one root plus real embedded extensions; command returns raw stdout."""
    source, derived, capture = Path(source).resolve(), Path(derived).resolve(), Path(capture).resolve()
    require(not (capture / ARTIFACT).exists(), 'scope artifact already exists')
    require(source_snapshot(source)['sha256'] == source_sha256, 'source changed before target scope capture')
    root_row = target_row(rows, root_target); root = root_row['buildSettings']
    context_matches(root_row, root, configuration, sdk, architectures)
    if (allow_non_application and root.get('PRODUCT_TYPE') in {
            'com.apple.product-type.framework', 'com.apple.product-type.library.static',
            'com.apple.product-type.library.dynamic'}):
        # Preserve the existing explicit framework/library target API. It makes
        # no complete-application claim and requires no App/appex product proof.
        return {'targets': [root_target], 'settings': rows, 'proof': None}
    require(root.get('WRAPPER_EXTENSION') in {'app', 'appex'}, 'root is not an app or app extension')
    project = Path(root.get('PROJECT_FILE_PATH', '')).resolve()
    require(project.is_relative_to(source) and project.suffix == '.xcodeproj' and project.is_dir(), 'root project is outside source or missing')
    name = root.get('FULL_PRODUCT_NAME')
    require(isinstance(name, str) and Path(name).name == name, 'invalid root product name')
    product = regular_child(derived, Path(root.get('TARGET_BUILD_DIR', '')) / name)
    require(product.is_dir(), 'built root product is missing')
    components = [product, *sorted(product.rglob('*.appex'))]
    log = capture / 'device-build.stdout.log'
    text = log.read_text(encoding='utf-8')
    graph = build_graph(text)
    require(graph is not None or len(components) == 1, 'embedded extensions require a captured dependency graph')
    root_key = (root.get('PROJECT_NAME'), root_target)
    reachable = closure(graph, root_key) if graph is not None else {root_key}
    candidates = {root_target: root_row}
    queried = []
    # No embedded extension means no extra settings query is needed at all.
    for number, (project_name, target) in enumerate(sorted(reachable - {root_key}) if len(components) > 1 else []):
        if project_name != root_key[0]:
            continue  # External dependency projects do not expand the selected product.
        found = [r for r in rows if r.get('target') == target]
        if found:
            row = target_row(rows, target)
        else:
            stem = f'target-settings-{number:04}'
            args = ['xcodebuild', '-project', str(project), '-target', target,
                    '-configuration', configuration, '-sdk', sdk,
                    'ARCHS=' + ' '.join(architectures), 'CODE_SIGNING_ALLOWED=NO', 'CODE_SIGNING_REQUIRED=NO',
                    'SYMROOT=' + str(capture / 'target-settings/Products'),
                    'OBJROOT=' + str(capture / 'target-settings/Intermediates'), '-showBuildSettings', '-json']
            raw = command(stem, args)
            row = target_row(json.loads(raw), target)
            queried.append({'target': target, 'stdout_artifact': stem + '.stdout.log'})
        context_matches(row, root, configuration, sdk, architectures)
        candidates[target] = row
    products, selected = [], {root_target}
    for number, component in enumerate(components):
        component = regular_child(derived, component)
        info_path = regular_child(derived, component / 'Info.plist')
        raw = info_path.read_bytes(); info = plistlib.loads(raw)
        require(isinstance(info, dict) and isinstance(info.get('CFBundleIdentifier'), str), 'invalid built product Info.plist')
        if number == 0:
            matched = [root_row]
        else:
            matched = [row for row in candidates.values() if row['target'] != root_target
                       and row['buildSettings'].get('WRAPPER_EXTENSION') == 'appex'
                       and row['buildSettings'].get('FULL_PRODUCT_NAME') == component.name
                       and row['buildSettings'].get('PRODUCT_BUNDLE_IDENTIFIER') == info['CFBundleIdentifier']]
        require(len(matched) == 1, 'embedded product does not identify exactly one reachable target: ' + component.name)
        row = matched[0]
        require(row['buildSettings'].get('FULL_PRODUCT_NAME') == component.name
                and row['buildSettings'].get('PRODUCT_BUNDLE_IDENTIFIER') == info['CFBundleIdentifier'],
                'built product disagrees with target settings')
        target = row['target']
        require(target not in selected or number == 0, 'duplicate embedded target product')
        selected.add(target)
        artifact = f'product-scope/{number:04}.Info.plist'
        destination = capture / artifact; destination.parent.mkdir(parents=True, exist_ok=True); destination.write_bytes(raw)
        products.append({'target': target, 'relative_product': component.relative_to(product.parent).as_posix(),
                         'info_artifact': artifact, 'info_sha256': digest(raw)})
    original = list(rows)
    rows = original + [candidates[t] for t in sorted(selected) if not any(r.get('target') == t for r in original)]
    require(source_snapshot(source)['sha256'] == source_sha256, 'source changed during target settings capture')
    write_json(capture / 'build-settings-root.json', original)
    write_json(capture / 'build-settings.json', rows)
    root_stdout = 'build-settings.stdout.log' if (capture / 'build-settings.stdout.log').is_file() else 'settings.stdout.log'
    require(read_json(capture / root_stdout) == original, 'root settings differ from original CLI stdout')
    proof = {'schema_version': 1, 'kind': 'xcode_built_product_scope', 'policy': 'root_and_embedded_app_extensions',
             'source_sha256': source_sha256, 'root_target': root_target, 'root_project': root_key[0],
             'scheme': scheme, 'configuration': configuration, 'sdk': sdk, 'architectures': sorted(architectures),
             'targets': sorted(selected), 'products': products, 'queried_settings': queried,
             'root_settings_stdout': root_stdout, 'root_settings_sha256': digest((capture / root_stdout).read_bytes()),
             'build_log_sha256': digest(log.read_bytes()), 'settings_sha256': digest(json_bytes(rows)),
             'excluded_targets': sorted(name for _, name in reachable if name not in selected),
             'capture_authenticity': 'not_verified'}
    write_json(capture / ARTIFACT, proof)
    return {'targets': proof['targets'], 'settings': rows, 'proof': proof}


def validate_scope(source, capture, membership):
    """Replay new scope evidence; refuse known partial legacy App captures."""
    capture = Path(capture)
    rows = read_json(capture / 'build-settings.json')
    path = capture / ARTIFACT
    if not path.exists():
        # Legacy evidence remains readable. A declared embedded extension cannot
        # disappear merely because old selected membership called itself complete.
        roots = [r for r in rows if r.get('target') in membership['selection']['targets']
                 and r.get('buildSettings', {}).get('WRAPPER_EXTENSION') == 'app']
        if len(roots) == 1:
            from .project_scope import resolve
            b = roots[0]['buildSettings']
            from pathlib import PurePosixPath
            def canonical(value):
                value = str(value).replace('\\', '/')
                for alias in membership.get('path_aliases', []):
                    if value == alias['from'] or value.startswith(alias['from'] + '/'):
                        value = alias['to'] + value[len(alias['from']):]
                return PurePosixPath(value)
            captured_root = canonical(membership.get('capture_roots', {}).get('source', source))
            project_path = canonical(b['PROJECT_FILE_PATH']).relative_to(captured_root).as_posix()
            variant, model = resolve(Path(source), {'scope': 'project-targets',
                'project_path': project_path + '/project.pbxproj', 'targets': [roots[0]['target']],
                'configuration': membership['selection']['configuration']}, _context=True)
            expected = {n for n in variant['target_closure']
                        if model.targets[model.names[n]].get('productType') in {
                            'com.apple.product-type.application', 'com.apple.product-type.app-extension'}}
            require(expected <= set(membership['selection']['targets']),
                    'legacy compiler selection omits embedded product targets: ' + ', '.join(sorted(expected - set(membership['selection']['targets']))))
        return {'status': 'legacy_scope_checked'}
    proof = read_json(path)
    require(proof.get('schema_version') == 1 and proof.get('kind') == 'xcode_built_product_scope'
            and proof.get('policy') == 'root_and_embedded_app_extensions', 'unsupported scope evidence')
    selection = membership['selection']
    require(proof.get('source_sha256') == membership['source_sha256'], 'scope source differs from membership')
    for key in ('targets', 'scheme', 'configuration', 'sdk', 'architectures'):
        require(proof.get(key) == selection[key], 'scope and membership differ: ' + key)
    require(proof.get('settings_sha256') == digest((capture / 'build-settings.json').read_bytes()), 'scope settings changed')
    root_stdout = proof.get('root_settings_stdout')
    require(root_stdout in {'build-settings.stdout.log', 'settings.stdout.log'}, 'invalid root settings stdout')
    raw_root = safe_child(capture, root_stdout).read_bytes()
    require(digest(raw_root) == proof.get('root_settings_sha256'), 'root settings stdout changed')
    originals = json.loads(raw_root)
    target_row(originals, proof.get('root_target'))
    require(read_json(capture / 'build-settings-root.json') == originals, 'root settings projection changed')
    captured_rows = {r['target']: r for r in originals}
    for query in proof.get('queried_settings', []):
        artifact = query.get('stdout_artifact')
        require(isinstance(artifact, str) and re.fullmatch(r'target-settings-\d{4,}\.stdout\.log', artifact), 'invalid target settings stdout')
        row = target_row(read_json(safe_child(capture, artifact)), query.get('target'))
        require(query['target'] not in captured_rows, 'duplicate target settings source')
        captured_rows[query['target']] = row
    for target in proof.get('targets', []):
        require(captured_rows.get(target) == target_row(rows, target), 'settings row differs from original CLI output')
    log = capture / 'device-build.stdout.log'
    require(proof.get('build_log_sha256') == digest(log.read_bytes()), 'scope build log changed')
    graph = build_graph(log.read_text(encoding='utf-8'))
    root_key = (proof.get('root_project'), proof.get('root_target'))
    reachable = closure(graph, root_key) if graph is not None else {root_key}
    products = proof.get('products')
    require(isinstance(products, list) and bool(products), 'scope products are missing')
    require(graph is not None or len(products) == 1, 'embedded scope has no dependency graph')
    root_row = target_row(rows, root_key[1]); root_name = root_row['buildSettings'].get('FULL_PRODUCT_NAME')
    selected, paths = set(), set()
    for index, item in enumerate(products):
        target = item.get('target'); relative = item.get('relative_product')
        require((root_key[0], target) in reachable and target not in selected, 'scope product target is ambiguous or outside graph')
        require(isinstance(relative, str) and relative not in paths, 'invalid or duplicate scope product path')
        safe_child(capture, relative)
        require(relative == root_name if index == 0 else relative.startswith(root_name + '/') and relative.endswith('.appex'),
                'extension is outside the root product')
        artifact = item.get('info_artifact')
        require(isinstance(artifact, str) and artifact == f'product-scope/{index:04}.Info.plist', 'invalid scope Info artifact')
        raw = safe_child(capture, artifact).read_bytes()
        require(digest(raw) == item.get('info_sha256'), 'scope Info.plist changed')
        info = plistlib.loads(raw); row = target_row(rows, target)['buildSettings']
        require(isinstance(info, dict), 'invalid scope Info dictionary')
        require(row.get('FULL_PRODUCT_NAME') == Path(relative).name
                and row.get('PRODUCT_BUNDLE_IDENTIFIER') == info.get('CFBundleIdentifier'), 'scope product identity differs')
        require(index == 0 and target == root_key[1] and row.get('WRAPPER_EXTENSION') in {'app', 'appex'}
                or index > 0 and row.get('WRAPPER_EXTENSION') == 'appex', 'invalid scope product role')
        selected.add(target); paths.add(relative)
    require(sorted(selected) == proof['targets'], 'scope target set is not the actual product set')
    require(proof.get('excluded_targets') == sorted(name for _, name in reachable if name not in selected), 'scope exclusions changed')
    return {'status': 'scope_replayed', 'targets': proof['targets']}
