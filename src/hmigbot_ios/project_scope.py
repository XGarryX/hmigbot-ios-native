"""Derive conservative product source membership from an actual Xcode project.

This is declaration evidence, never an Xcode/compiler build result. Conditional
build settings do not remove sources, and unresolved membership fails closed.
"""
from pathlib import Path, PurePosixPath

from .core import MigrationError, digest, safe_child, snapshot
from .xcode import OpenStep, synchronized_membership


COMPILE_SUFFIXES = {'.swift', '.m', '.mm', '.c', '.cpp', '.cc', '.cxx', '.metal', '.s'}
ANALYZED_COMPILE_SUFFIXES = {'.swift', '.m', '.mm', '.c', '.cpp'}
ROOT_PRODUCTS = {'com.apple.product-type.application', 'com.apple.product-type.app-extension'}
TEST_PRODUCTS = {'com.apple.product-type.bundle.unit-test', 'com.apple.product-type.bundle.ui-testing'}
INPUT_FIELDS = {'scope', 'project_path', 'targets', 'configuration'}
DERIVED_FIELDS = {'source_files', 'source_membership', 'excluded_sources', 'source_hash',
                  'project_sha256', 'target_closure', 'evidence', 'effective_build', 'limitations'}


def resolve(source: Path, variant: dict, *, _context=False) -> dict:
    """Return derived membership, rejecting partial, stale or edited derivatives.

    Callers initially provide only scope/project_path/targets/configuration. A
    previously returned value is accepted only when every field still matches a
    fresh derivation. Caller-authored source allowlists cannot define the scope.
    """
    if not isinstance(variant, dict) or variant.get('scope') != 'project-targets':
        raise MigrationError('Project membership requires scope=project-targets')
    unknown = set(variant) - INPUT_FIELDS - DERIVED_FIELDS
    if unknown:
        raise MigrationError(f'Unsupported project membership fields: {sorted(unknown)}')
    supplied_derived = set(variant) & DERIVED_FIELDS
    if supplied_derived and supplied_derived != DERIVED_FIELDS:
        raise MigrationError('Partial derived membership fields are not accepted')
    if not INPUT_FIELDS <= set(variant):
        raise MigrationError('Project membership requires project_path, targets and configuration')
    requested = variant['targets']
    if not isinstance(requested, list) or not requested or any(not isinstance(n, str) or not n for n in requested):
        raise MigrationError('Project membership targets must be nonempty exact target names')
    if len(set(requested)) != len(requested):
        raise MigrationError('Duplicate requested target names')
    configuration = variant['configuration']
    if not isinstance(configuration, str) or not configuration:
        raise MigrationError('Project membership configuration must be a nonempty name')
    project_path = variant['project_path']
    if not isinstance(project_path, str):
        raise MigrationError('Project membership project_path must be a relative project.pbxproj path')
    source = Path(source).resolve()
    path = safe_child(source, project_path)
    if path.name != 'project.pbxproj' or path.parent.suffix != '.xcodeproj':
        raise MigrationError('project_path must name an actual .xcodeproj/project.pbxproj')
    snap = snapshot(source)
    if not path.is_file():
        raise MigrationError(f'Project does not exist: {project_path}')
    try:
        document = OpenStep(path.read_text(encoding='utf-8-sig')).parse()
        graph = _Project(source, path, document)
        result = graph.derive(requested, configuration, snap)
    except (OSError, UnicodeError, TypeError, AttributeError, KeyError) as exc:
        raise MigrationError(f'Cannot resolve project membership: {exc}') from exc
    if supplied_derived and variant != result:
        changed = sorted(k for k in result if variant.get(k) != result[k])
        raise MigrationError(f'Stale or modified derived project membership: {changed}')
    return (result, graph) if _context else result


class _Project:
    def __init__(self, source, path, document):
        self.source, self.path = source, path
        self.selected_configs = []
        self.selected_closure = set()
        if not isinstance(document, dict) or not isinstance(document.get('objects'), dict):
            raise MigrationError('Project objects must be a dictionary')
        self.objects = document['objects']
        if any(not isinstance(obj, dict) for obj in self.objects.values()):
            raise MigrationError('Invalid project object')
        self.root_id = document.get('rootObject')
        self.project = self.object(self.root_id, 'PBXProject')
        if self.project.get('projectDirPath', ''):
            raise MigrationError('Nonempty projectDirPath requires Xcode resolution')
        self.parents = {}
        for key, obj in self.objects.items():
            children = obj.get('children', [])
            self.list_value(children, f'children of {key}')
            for child in children:
                self.parents.setdefault(child, []).append(key)
        self.targets, self.names, self.products = {}, {}, {}
        target_ids = self.list_value(self.project.get('targets'), 'project targets')
        for key in target_ids:
            obj = self.object(key)
            if obj.get('isa') not in {'PBXNativeTarget', 'PBXAggregateTarget', 'PBXLegacyTarget'}:
                raise MigrationError(f'Unknown project target type: {key}')
            name = obj.get('name')
            if not isinstance(name, str) or not name:
                raise MigrationError(f'Unknown target name: {key}')
            if name in self.names:
                raise MigrationError(f'Duplicate project target name: {name}')
            self.targets[key], self.names[name] = obj, key
            product = obj.get('productReference')
            if product:
                self.object(product, 'PBXFileReference')
                if product in self.products:
                    raise MigrationError(f'Duplicate target product reference: {product}')
                self.products[product] = key

    @staticmethod
    def list_value(value, description):
        if not isinstance(value, list) or any(not isinstance(v, str) for v in value):
            raise MigrationError(f'Invalid {description} list')
        if len(value) != len(set(value)):
            raise MigrationError(f'Duplicate {description} entry')
        return value

    def object(self, key, kind=None):
        obj = self.objects.get(key)
        if not isinstance(obj, dict) or (kind and obj.get('isa') != kind):
            raise MigrationError(f'Unknown or invalid project reference {key}: expected {kind or "object"}')
        return obj

    def file_path(self, key, visiting=()):
        if key in visiting:
            raise MigrationError(f'Cyclic project groups: {key}')
        obj = self.object(key)
        local, tree = obj.get('path', ''), obj.get('sourceTree', '<group>')
        if not isinstance(local, str) or '$' in local or not isinstance(tree, str) or '$' in tree:
            raise MigrationError(f'Unresolved path variable in project reference: {key}')
        if '\\' in local or ':' in local or PurePosixPath(local).is_absolute() or '..' in PurePosixPath(local).parts:
            raise MigrationError(f'Project reference path must not escape source root: {local}')
        if tree == 'SOURCE_ROOT':
            base = self.path.parent.parent
        elif tree == '<group>':
            parents = self.parents.get(key, [])
            if len(parents) > 1:
                raise MigrationError(f'Ambiguous project reference has multiple parents: {key}')
            base = self.file_path(parents[0], visiting + (key,)) if parents else self.path.parent.parent
        else:
            raise MigrationError(f'Unresolved project sourceTree {tree}: {key}')
        result = (base / local).resolve()
        if not result.is_relative_to(self.source):
            raise MigrationError(f'Project source reference is outside source root: {local}')
        return result

    def configuration(self, obj, name, owner):
        configs = self.object(obj.get('buildConfigurationList'), 'XCConfigurationList')
        candidates = []
        for key in self.list_value(configs.get('buildConfigurations'), f'{owner} configurations'):
            config = self.object(key, 'XCBuildConfiguration')
            if config.get('name') == name:
                candidates.append(config)
        if len(candidates) != 1:
            raise MigrationError(f'Missing or ambiguous configuration {name} for {owner}')
        config = candidates[0]
        if not isinstance(config.get('buildSettings', {}), dict):
            raise MigrationError(f'Invalid configuration settings for {owner}')
        actual = None
        if config.get('baseConfigurationReference'):
            actual = self.file_path(config['baseConfigurationReference'])
            if not actual.is_file():
                raise MigrationError(f'Base configuration does not exist: {actual}')
        self.selected_configs.append({'owner': owner, 'name': name, 'settings': config.get('buildSettings', {}),
                                      'base_path': actual.relative_to(self.source).as_posix() if actual else None})

    def phases(self, target):
        for key in self.list_value(target.get('buildPhases', []), f'{target["name"]} build phases'):
            yield key, self.object(key)

    def build_files(self, phase, phase_id):
        for key in self.list_value(phase.get('files', []), f'{phase_id} build files'):
            item = self.object(key, 'PBXBuildFile')
            if item.get('platformFilter') or item.get('platformFilters'):
                raise MigrationError(f'Unresolved platform-filtered project membership: {key}')
            yield key, item

    def dependency(self, key):
        dependency = self.object(key, 'PBXTargetDependency')
        direct = dependency.get('target')
        proxy_id = dependency.get('targetProxy')
        proxy_target = None
        if proxy_id:
            proxy = self.object(proxy_id, 'PBXContainerItemProxy')
            if proxy.get('containerPortal') != self.root_id:
                raise MigrationError(f'Cross-project dependency portal requires Xcode resolution: {key}')
            if proxy.get('proxyType') != '1':
                raise MigrationError(f'Unresolved target proxy type: {key}')
            proxy_target = proxy.get('remoteGlobalIDString')
        if direct and proxy_target and direct != proxy_target:
            raise MigrationError(f'Ambiguous dependency target and proxy: {key}')
        result = direct or proxy_target
        if result not in self.targets:
            raise MigrationError(f'Unknown or external target dependency: {key}')
        return result

    def closure(self, roots, configuration):
        closure, visiting = set(), set()

        def visit(key):
            if key in visiting:
                raise MigrationError('Cyclic target dependencies require Xcode resolution')
            if key in closure:
                return
            visiting.add(key)
            target = self.targets[key]
            if target.get('isa') != 'PBXNativeTarget':
                raise MigrationError(f'Unresolved non-native product target: {target["name"]}')
            if target.get('packageProductDependencies'):
                raise MigrationError(f'Unresolved external package product dependencies: {target["name"]}')
            if target.get('buildRules'):
                raise MigrationError(f'Custom build rules may generate or transform sources: {target["name"]}')
            self.configuration(target, configuration, target['name'])
            for dep in self.list_value(target.get('dependencies', []), f'{target["name"]} dependencies'):
                visit(self.dependency(dep))
            for phase_id, phase in self.phases(target):
                kind = phase.get('isa')
                if kind == 'PBXShellScriptBuildPhase':
                    raise MigrationError(f'Unexecuted build script may affect source membership: {target["name"]}')
                if kind not in {'PBXSourcesBuildPhase', 'PBXResourcesBuildPhase', 'PBXFrameworksBuildPhase',
                                'PBXCopyFilesBuildPhase', 'PBXHeadersBuildPhase'}:
                    raise MigrationError(f'Unsupported project build phase: {kind}')
                if phase.get('platformFilter') or phase.get('platformFilters'):
                    raise MigrationError(f'Unresolved platform-filtered project phase: {phase_id}')
                for bid, build_file in self.build_files(phase, phase_id):
                    ref = build_file.get('fileRef')
                    if build_file.get('productRef'):
                        raise MigrationError(f'Unresolved external package product reference: {bid}')
                    self.object(ref)
                    if ref in self.products:
                        visit(self.products[ref])
                    elif kind in {'PBXFrameworksBuildPhase', 'PBXCopyFilesBuildPhase'}:
                        obj = self.object(ref)
                        if obj.get('isa') == 'PBXReferenceProxy' or obj.get('sourceTree') == 'BUILT_PRODUCTS_DIR':
                            raise MigrationError(f'Unresolved external or implicit product reference: {ref}')
            visiting.remove(key)
            closure.add(key)

        for key in roots:
            visit(key)
        return closure

    def memberships(self):
        memberships, self.synchronized_exclusions, self.synchronized_declarations = synchronized_membership(
            self.source, self.path, self.objects, self.targets)
        for key, target in self.targets.items():
            seen = {relative for relative, owners in memberships.items() if key in owners}
            for phase_id, phase in self.phases(target):
                if phase.get('isa') != 'PBXSourcesBuildPhase':
                    continue
                for bid, build_file in self.build_files(phase, phase_id):
                    ref = build_file.get('fileRef')
                    self.object(ref, 'PBXFileReference')
                    actual = self.file_path(ref)
                    if not actual.is_file():
                        raise MigrationError(f'Declared source does not exist: {actual}')
                    relative = actual.relative_to(self.source).as_posix()
                    if key in self.synchronized_exclusions.get(relative, set()):
                        raise MigrationError(f'Conflicting explicit/synchronized membership in target {target["name"]}: {relative}')
                    if relative in seen:
                        raise MigrationError(f'Duplicate source membership in target {target["name"]}: {relative}')
                    if actual.suffix.lower() not in COMPILE_SUFFIXES:
                        raise MigrationError(f'Unsupported source phase file requires explicit handling: {relative}')
                    if actual.name == 'Package.swift':
                        raise MigrationError('Package.swift cannot be assumed to be a product compile unit')
                    seen.add(relative)
                    memberships.setdefault(relative, set()).add(key)
        return memberships

    def derive(self, requested, configuration, snap):
        roots = []
        for name in sorted(requested):
            if name not in self.names:
                raise MigrationError(f'Unknown requested target: {name}')
            key = self.names[name]
            if self.targets[key].get('productType') not in ROOT_PRODUCTS:
                raise MigrationError('Requested root targets must be application or app-extension products')
            roots.append(key)
        self.configuration(self.project, configuration, 'project')
        closure = self.closure(roots, configuration)
        self.selected_closure = closure
        memberships = self.memberships()
        disk = {item['path']: item for item in snap['files']
                if Path(item['path']).suffix.lower() in COMPILE_SUFFIXES and Path(item['path']).name != 'Package.swift'}
        unowned = set(disk) - set(memberships) - set(self.synchronized_exclusions)
        if unowned:
            raise MigrationError(f'Unknown source membership for unowned compile units: {sorted(unowned)}')
        unavailable = (set(memberships) | set(self.synchronized_exclusions)) - set(disk)
        if unavailable:
            raise MigrationError(f'Declared sources are outside the indexed source snapshot: {sorted(unavailable)}')
        included, excluded = [], []
        for relative in sorted(set(memberships) | set(self.synchronized_exclusions)):
            owners = memberships.get(relative, set())
            entry = {'path': relative, 'targets': sorted(self.targets[key]['name'] for key in owners),
                     'sha256': disk[relative]['sha256']}
            declarations = [group for group in self.synchronized_declarations if relative in group['source_files']]
            if declarations:
                entry['synchronized_group_ids'] = sorted(group['id'] for group in declarations)
            exceptions = self.synchronized_exclusions.get(relative, set())
            if exceptions:
                entry['excluded_from_targets'] = sorted(self.targets[key]['name'] for key in exceptions)
            if owners & closure:
                if Path(relative).suffix not in ANALYZED_COMPILE_SUFFIXES:
                    raise MigrationError(f'Unsupported product compile language has no source facts analyzer: {relative}')
                included.append(entry)
            else:
                entry['reason'] = ('synchronized_membership_exception' if not owners else
                                  'test_only_oracle' if all(self.targets[key].get('productType') in TEST_PRODUCTS for key in owners)
                                   else 'outside_product_target_closure')
                excluded.append(entry)
        return {'scope': 'project-targets', 'project_path': self.path.relative_to(self.source).as_posix(),
                'targets': sorted(requested), 'configuration': configuration,
                'target_closure': sorted(self.targets[key]['name'] for key in closure),
                'source_files': [item['path'] for item in included], 'source_membership': included,
                'excluded_sources': excluded, 'source_hash': snap['sha256'],
                'project_sha256': digest(self.path.read_bytes()), 'evidence': 'project_declared_membership',
                'effective_build': 'unresolved',
                'limitations': ['headers_implicit_includes_unresolved', 'conditional_build_settings_not_evaluated']
                + (['synchronized_format_subset_not_apple_schema_verified',
                    'synchronized_membership_windows_fixture_only_not_xcode_build_verified']
                   if self.synchronized_declarations else [])}
