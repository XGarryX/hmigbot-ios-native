"""Xcode/OpenStep structure, without pretending to evaluate an Xcode build."""
from pathlib import Path, PurePosixPath
import re

from .core import MigrationError, read_json


def synchronized_membership(root, project_path, objects, targets):
    """Conservative, filesystem-backed *declarations*, never compiler evidence.

    Apple's public folder guide used here does not specify this serialization
    schema. The field subset follows Xcodeproj's primary implementation:
    https://github.com/CocoaPods/Xcodeproj/blob/master/lib/xcodeproj/project/object/file_system_synchronized_root_group.rb
    https://github.com/CocoaPods/Xcodeproj/blob/master/lib/xcodeproj/project/object/file_system_synchronized_exception_set.rb
    Treat it as an input-format assumption, not complete Xcode compatibility.
    """
    root = Path(root).resolve()
    parents = {}
    main_groups = {obj.get('mainGroup') for obj in objects.values() if obj.get('isa') == 'PBXProject'}
    for key, obj in objects.items():
        for child in obj.get('children', []):
            parents.setdefault(child, []).append(key)

    def strings(value, label):
        if (not isinstance(value, list) or any(not isinstance(v, str) for v in value)
                or len(value) != len(set(value))):
            raise MigrationError(f'Invalid synchronized {label} list')
        return value

    def relative(value, label):
        if (not isinstance(value, str) or not value or '$' in value or '\\' in value or ':' in value
                or PurePosixPath(value).is_absolute() or '..' in PurePosixPath(value).parts
                or value != PurePosixPath(value).as_posix()):
            raise MigrationError(f'Unresolved synchronized {label} path: {value}')
        return value

    def location(key, visiting=()):
        if key in visiting or key not in objects:
            raise MigrationError(f'Unknown or cyclic synchronized group reference: {key}')
        obj = objects[key]
        if obj.get('isa') not in {'PBXGroup', 'PBXFileSystemSynchronizedRootGroup'}:
            raise MigrationError(f'Unsupported synchronized directory ancestor kind: {key}')
        local = obj.get('path', '')
        if local:
            relative(local, key)
        elif obj.get('isa') == 'PBXFileSystemSynchronizedRootGroup':
            raise MigrationError(f'Synchronized root requires a concrete directory path: {key}')
        tree = obj.get('sourceTree', '<group>')
        if tree == 'SOURCE_ROOT':
            base = project_path.parent.parent
        elif tree == '<group>':
            owners = parents.get(key, [])
            if len(owners) > 1:
                raise MigrationError(f'Ambiguous synchronized group parents: {key}')
            if not owners and key not in main_groups:
                raise MigrationError(f'Synchronized group has no anchored parent: {key}')
            base = location(owners[0], visiting + (key,)) if owners else project_path.parent.parent
        else:
            raise MigrationError(f'Unresolved synchronized sourceTree {tree}: {key}')
        candidate = base / local
        # Check before resolve so an in-repository link is also rejected.
        for part in (candidate, *candidate.parents):
            if part.is_symlink() or (hasattr(part, 'is_junction') and part.is_junction()):
                raise MigrationError(f'Synchronized source links require materialization: {candidate}')
            if part == root:
                break
        actual = candidate.resolve()
        if not actual.is_relative_to(root):
            raise MigrationError(f'Synchronized directory escapes source root: {key}')
        return actual

    associations = {}
    for tid, target in targets.items():
        for gid in strings(target.get('fileSystemSynchronizedGroups', []), f'{tid} groups'):
            if objects.get(gid, {}).get('isa') != 'PBXFileSystemSynchronizedRootGroup':
                raise MigrationError(f'Unknown synchronized root group: {gid}')
            if target.get('isa') != 'PBXNativeTarget':
                raise MigrationError(f'Synchronized membership requires a native target: {tid}')
            phases = [objects.get(pid, {}).get('isa') for pid in target.get('buildPhases', [])]
            if phases.count('PBXSourcesBuildPhase') != 1:
                raise MigrationError(f'Synchronized target requires one declared sources phase: {tid}')
            associations.setdefault(gid, set()).add(tid)
    memberships, exclusions, declarations, locations = {}, {}, [], []
    compile_types = {'.swift': 'sourcecode.swift', '.m': 'sourcecode.c.objc', '.mm': 'sourcecode.cpp.objcpp',
                     '.c': 'sourcecode.c.c', '.cpp': 'sourcecode.cpp.cpp', '.cc': 'sourcecode.cpp.cpp',
                     '.cxx': 'sourcecode.cpp.cpp', '.metal': 'sourcecode.metal', '.s': 'sourcecode.asm'}
    for gid, group in objects.items():
        if group.get('isa') != 'PBXFileSystemSynchronizedRootGroup':
            continue
        unknown = set(group) - {'isa', 'path', 'sourceTree', 'exceptions', 'explicitFileTypes', 'explicitFolders'}
        if unknown:
            raise MigrationError(f'Unsupported synchronized root fields {gid}: {sorted(unknown)}')
        if strings(group.get('explicitFolders', []), f'{gid} explicitFolders'):
            raise MigrationError(f'Unsupported synchronized explicitFolders semantics: {gid}')
        actual = location(gid)
        if not actual.is_dir():
            raise MigrationError(f'Synchronized directory does not exist: {gid}')
        if any(actual.is_relative_to(other) or other.is_relative_to(actual) for other in locations):
            raise MigrationError(f'Overlapping synchronized directories require explicit handling: {gid}')
        locations.append(actual)
        owners = associations.get(gid, set())
        if not owners:
            # Unattached groups are not target declarations. Strict scope resolution
            # still rejects any compile file left without an owner after this scan.
            continue
        excluded = {tid: set() for tid in owners}
        exception_evidence = []
        for eid in strings(group.get('exceptions', []), f'{gid} exceptions'):
            exception = objects.get(eid, {})
            if exception.get('isa') != 'PBXFileSystemSynchronizedBuildFileExceptionSet':
                raise MigrationError(f'Unsupported synchronized exception kind: {eid}')
            unknown = set(exception) - {'isa', 'target', 'membershipExceptions'}
            if unknown:
                raise MigrationError(f'Unsupported synchronized exception fields {eid}: {sorted(unknown)}')
            tid = exception.get('target')
            if tid not in owners:
                raise MigrationError(f'Synchronized exception target is not associated with root {gid}: {tid}')
            paths = strings(exception.get('membershipExceptions', []), f'{eid} membershipExceptions')
            for name in paths:
                relative(name, eid)
                child = actual / name
                # Folder exclusion/recursive toggling is outside this subset.
                if not child.is_file() or child.is_symlink() or not child.resolve().is_relative_to(actual):
                    raise MigrationError(f'Synchronized exception must name an existing regular file: {eid}: {name}')
                if name in excluded[tid]:
                    raise MigrationError(f'Duplicate synchronized exception for {tid}: {name}')
                excluded[tid].add(name)
            exception_evidence.append({'id': eid, 'target': tid, 'paths': paths})
        explicit_types = group.get('explicitFileTypes', {})
        if not isinstance(explicit_types, dict):
            raise MigrationError(f'Invalid synchronized explicitFileTypes: {gid}')
        for name, file_type in explicit_types.items():
            relative(name, gid)
            if (compile_types.get(Path(name).suffix) != file_type or not (actual / name).is_file()):
                raise MigrationError(f'Unsupported synchronized explicit file type {gid}: {name}: {file_type}')
        files = []
        for child in sorted(actual.rglob('*')):
            if child.is_symlink() or (hasattr(child, 'is_junction') and child.is_junction()):
                raise MigrationError(f'Synchronized source links require materialization: {child}')
            if not child.is_file() or child.suffix.lower() not in compile_types:
                continue
            local = child.relative_to(actual).as_posix()
            if (any(part.startswith('.') for part in child.relative_to(actual).parts)
                    and any(local not in excluded[tid] for tid in owners)):
                raise MigrationError(f'Synchronized hidden compile source requires explicit resolution: {local}')
            if child.name == 'Package.swift' or child.suffix not in compile_types:
                raise MigrationError(f'Unsupported synchronized compile file: {local}')
            if any('.' in part for part in child.relative_to(actual).parts[:-1]):
                raise MigrationError(f'Synchronized compile file inside an opaque or special folder: {local}')
            rel = child.relative_to(root).as_posix()
            files.append(rel)
            for tid in owners:
                destination = exclusions if local in excluded[tid] else memberships
                destination.setdefault(rel, set()).add(tid)
        declarations.append({'id': gid, 'path': actual.relative_to(root).as_posix(), 'targets': sorted(owners),
                             'source_files': files, 'membership_exceptions': exception_evidence,
                             'evidence': 'project_declared_synchronized_membership',
                             'format_status': 'conservative_subset_not_apple_schema_verified'})
    return memberships, exclusions, declarations


class OpenStep:
    """Compatibility interface backed exclusively by Apple's property-list parser."""
    def __init__(self, text):
        self.text = text

    def parse(self):
        import plistlib
        from .apple_tools import run
        result = run(['/usr/bin/plutil', '-convert', 'xml1', '-o', '-', '-'],
                     data=self.text.encode('utf-8'), timeout=30)
        try:
            return plistlib.loads(result.stdout)
        except (ValueError, plistlib.InvalidFileException) as exc:
            raise MigrationError('Apple plutil returned invalid property-list data') from exc


def project_inventory(root, files):
    projects, issues = [], []
    for item in files:
        if not item['path'].endswith('.pbxproj'):
            continue
        path = root / item['path']
        try:
            document = OpenStep(path.read_text(encoding='utf-8-sig')).parse()
            objects = document.get('objects', {})
            if not isinstance(objects, dict):
                raise MigrationError('Xcode objects must be a dictionary')
            parents = {}
            for key, obj in objects.items():
                if not isinstance(obj, dict):
                    raise MigrationError('Invalid Xcode object')
                for child in obj.get('children', []):
                    parents.setdefault(child, []).append(key)
            project_base = path.parent.parent

            def file_path(key, visited=()):
                if key in visited:
                    raise MigrationError('Cyclic Xcode groups')
                obj = objects.get(key, {})
                tree, local = obj.get('sourceTree', '<group>'), obj.get('path', '')
                if tree == 'SOURCE_ROOT':
                    result = project_base / local
                elif tree == '<group>':
                    parent = parents.get(key, [])
                    if len(parent) > 1:
                        return None
                    base = file_path(parent[0], visited + (key,)) if parent else project_base
                    if base is None:
                        return None
                    result = base / local
                else:
                    return None  # SDKROOT, BUILT_PRODUCTS_DIR and external references remain logical.
                return result.resolve()

            def reference(key):
                obj = objects.get(key, {})
                actual = file_path(key)
                relative = actual.relative_to(root).as_posix() if actual is not None and actual.is_relative_to(root) else None
                return {'id': key, 'name': obj.get('name', obj.get('path')), 'source_tree': obj.get('sourceTree'),
                        'path': relative, 'exists': bool(actual and actual.is_file()),
                        'resolution': 'repository_path' if relative is not None else 'unresolved'}

            declared_targets = {key: obj for key, obj in objects.items()
                                if obj.get('isa') in {'PBXNativeTarget', 'PBXAggregateTarget', 'PBXLegacyTarget'}}
            sync_groups = []
            try:
                _, _, sync_groups = synchronized_membership(root, path, objects, declared_targets)
            except MigrationError as exc:
                issues.append({'code': 'synchronized_groups_unresolved', 'path': item['path'], 'message': str(exc)})
            targets = []
            for key, obj in objects.items():
                if obj.get('isa') not in {'PBXNativeTarget', 'PBXAggregateTarget', 'PBXLegacyTarget'}:
                    continue
                phases = []
                for phase_id in obj.get('buildPhases', []):
                    phase = objects.get(phase_id, {})
                    entries = []
                    for build_file in phase.get('files', []):
                        file = objects.get(build_file, {})
                        entry = reference(file.get('fileRef', file.get('productRef', '')))
                        entry['build_file_id'] = build_file
                        entry['settings'] = file.get('settings', {})
                        entries.append(entry)
                    phases.append({'id': phase_id, 'kind': phase.get('isa'), 'files': entries})
                    if phase.get('isa') == 'PBXShellScriptBuildPhase':
                        issues.append({'code': 'build_script_not_executed', 'path': item['path'], 'target': obj.get('name')})
                configurations = []
                configuration_list = objects.get(obj.get('buildConfigurationList'), {})
                for config_id in configuration_list.get('buildConfigurations', []):
                    config = objects.get(config_id, {})
                    configurations.append({'name': config.get('name'), 'inline_settings': config.get('buildSettings', {}),
                        'base_config': reference(config['baseConfigurationReference']) if config.get('baseConfigurationReference') else None})
                targets.append({'id': key, 'name': obj.get('name'), 'product_type': obj.get('productType'),
                                'phases': phases, 'configurations': configurations,
                                'effective_settings': 'unresolved'})
                groups = [group for group in sync_groups if key in group['targets']]
                if groups:
                    targets[-1]['synchronized_groups'] = groups
            projects.append({'path': item['path'], 'sha256': item['sha256'], 'targets': targets,
                             'object_version': document.get('objectVersion')})
        except (MigrationError, UnicodeError, AttributeError, TypeError) as exc:
            issues.append({'code': 'project_parse_failed', 'path': item['path'], 'message': str(exc)})
    return {'projects': projects, 'effective_build': 'unresolved'}, issues


def dependency_inventory(root, files, *, manifest_evaluations=None):
    dependencies, issues = [], []
    evaluated = {item['path']: item for item in manifest_evaluations or []}
    consumed = []
    for item in files:
        path = root / item['path']
        try:
            if path.name == 'Package.resolved':
                value = read_json(path)
                for pin in value.get('pins', value.get('object', {}).get('pins', [])):
                    dependencies.append({'manager': 'SwiftPM', 'identity': pin.get('identity', pin.get('package')),
                        'location': pin.get('location', pin.get('repositoryURL')), 'state': pin.get('state', {}),
                        'source_path': item['path'], 'evidence': 'lockfile'})
            elif path.name == 'Podfile.lock':
                in_pods = False
                for number, line in enumerate(path.read_text(encoding='utf-8-sig').splitlines(), 1):
                    if line == 'PODS:':
                        in_pods = True
                    elif line and not line.startswith(' '):
                        in_pods = False
                    if in_pods:
                        match = re.fullmatch(r'  - ([^ (]+) \(([^)]+)\):?', line)
                        if match:
                            dependencies.append({'manager': 'CocoaPods', 'identity': match[1], 'state': {'version': match[2]},
                                'source_path': item['path'], 'line': number, 'evidence': 'lockfile'})
                issues.append({'code': 'pod_dependency_edges_unresolved', 'path': item['path']})
            elif path.name == 'Cartfile.resolved':
                for number, line in enumerate(path.read_text(encoding='utf-8-sig').splitlines(), 1):
                    match = re.fullmatch(r'(github|git|binary) "([^"]+)" "([^"]+)"', line.strip())
                    if match:
                        dependencies.append({'manager': 'Carthage', 'kind': match[1], 'location': match[2],
                                             'state': {'resolved': match[3]}, 'source_path': item['path'], 'line': number, 'evidence': 'lockfile'})
                    elif line.strip() and not line.strip().startswith('#'):
                        issues.append({'code': 'carthage_line_unresolved', 'path': item['path'], 'line': number})
            elif path.name in {'Package.swift', 'Podfile', 'Cartfile'}:
                evaluation = evaluated.get(item['path']) if path.name == 'Package.swift' else None
                if (evaluation is not None and evaluation.get('status') == 'manifest_evaluated'
                        and evaluation.get('manifest_sha256') == item['sha256']):
                    consumed.append(evaluation)
                else:
                    issues.append({'code': 'executable_manifest_not_evaluated', 'path': item['path']})
        except (MigrationError, UnicodeError, AttributeError, TypeError) as exc:
            issues.append({'code': 'dependency_parse_failed', 'path': item['path'], 'message': str(exc)})
    result = {'dependencies': dependencies, 'complete_graph': False}
    if consumed:
        result['manifest_evaluations'] = consumed
    return result, issues
