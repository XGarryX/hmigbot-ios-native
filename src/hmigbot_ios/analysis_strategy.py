"""Deterministic project-context decisions, separate from execution receipts."""
from pathlib import Path, PurePosixPath
import re

from .core import MigrationError, digest, json_bytes, read_json, safe_child, snapshot
from .xcode import project_inventory

CONFIG = 'spec/ref/ios-analysis-config.json'
MODES = {'auto', 'native', 'replay', 'static'}
C_SOURCE = {'.c', '.m', '.mm', '.cpp', '.cc', '.cxx'}


def configuration(project, path=None):
    path = Path(path) if path else project / CONFIG
    if not path.exists():
        if path != project / CONFIG:
            raise MigrationError('Analysis configuration is missing')
        return {'schema_version': 1, 'mode': 'auto'}, None
    value = read_json(path)
    allowed = {'schema_version', 'mode', 'selection', 'evidence', 'mcp_server',
               'require_official', 'official_skills', 'timeout_seconds'}
    if (not isinstance(value, dict) or value.get('schema_version') != 1
            or set(value) - allowed or value.get('mode', 'auto') not in MODES):
        raise MigrationError('Unsupported analysis configuration')
    for key in ('selection', 'evidence'):
        if key in value and not isinstance(value[key], dict):
            raise MigrationError('Analysis ' + key + ' must be an object')
    if set(value.get('selection', {})) - {'project', 'workspace', 'scheme', 'target', 'configuration', 'sdk', 'arch', 'destination'}:
        raise MigrationError('Unknown analysis selection field')
    if any(not isinstance(v, str) or not v.strip() for v in value.get('selection', {}).values()):
        raise MigrationError('Analysis selection values must be nonempty strings')
    if set(value.get('evidence', {})) - {'build', 'compilation', 'conditional', 'manifest'}:
        raise MigrationError('Unknown analysis evidence field')
    if any(not isinstance(v, str) or not v.strip() for v in value.get('evidence', {}).values()):
        raise MigrationError('Analysis evidence paths must be nonempty strings')
    for key in ('require_official', 'official_skills'):
        if key in value and type(value[key]) is not bool:
            raise MigrationError('Analysis ' + key + ' must be boolean')
    if 'mcp_server' in value and (not isinstance(value['mcp_server'], str) or not value['mcp_server'].strip()):
        raise MigrationError('Analysis mcp_server must be a nonempty configuration path')
    timeout = value.get('timeout_seconds', 600)
    if type(timeout) is not int or not 1 <= timeout <= 3600:
        raise MigrationError('Analysis timeout must be 1..3600 seconds')
    return value, {'path': str(path.resolve()), 'sha256': digest(path.read_bytes())}


def resolve_path(project, value):
    path = Path(value)
    path = path.resolve() if path.is_absolute() else safe_child(project, value)
    if not path.is_relative_to((project / 'spec/ref').resolve()):
        raise MigrationError('Analysis evidence must be under project/spec/ref')
    return path


def inspect_source(source):
    snap = snapshot(source)
    inventory, issues = project_inventory(source, snap['files'])
    tokens, c_conditionals = set(), []
    languages = {}
    from .swiftui import tokenize
    for entry in snap['files']:
        suffix = Path(entry['path']).suffix.lower()
        languages.setdefault(suffix, []).append(entry['path'])
        if suffix in C_SOURCE | {'.swift', '.h'}:
            text = (source / entry['path']).read_text(encoding='utf-8-sig')
            lexed = tokenize(text, skip_pragma_marks=suffix != '.swift')
            tokens.update(t.value for t in lexed if t.kind != 'string')
            if suffix in C_SOURCE | {'.h'} and any(t.value == '#' for t in lexed):
                if re.search(r'^\s*#\s*(if|ifdef|ifndef|elif)\b', text, re.M):
                    c_conditionals.append(entry['path'])
    return {'snapshot': snap, 'projects': inventory['projects'], 'issues': issues,
            'languages': languages, 'tokens': sorted(tokens), 'c_conditionals': c_conditionals}


def _selection(source, inventory, supplied):
    selected = dict(supplied)
    projects = inventory['projects']
    missing = []
    if selected.get('project'):
        path = safe_child(source, selected['project'])
        if not path.is_dir() or path.suffix != '.xcodeproj':
            raise MigrationError('Selected analysis project does not exist')
        projects = [p for p in projects if p['path'] == selected['project'] + '/project.pbxproj']
    elif not selected.get('workspace'):
        if len(projects) == 1:
            selected['project'] = str(Path(projects[0]['path']).parent)
        elif len(projects) > 1:
            missing.append({'field': 'selection.project', 'reason': 'Multiple Xcode projects',
                            'candidates': [str(Path(p['path']).parent) for p in projects]})
    if selected.get('workspace') and not safe_child(source, selected['workspace']).is_dir():
        raise MigrationError('Selected workspace does not exist')
    if len(projects) == 1:
        targets = [t for t in projects[0]['targets'] if t['product_type'] == 'com.apple.product-type.application']
        if selected.get('target'):
            targets = [t for t in projects[0]['targets'] if t['name'] == selected['target']]
            if len(targets) != 1:
                raise MigrationError('Selected analysis target is unknown or ambiguous')
        if len(targets) == 1:
            selected.setdefault('target', targets[0]['name'])
        elif targets:
            missing.append({'field': 'selection.target', 'reason': 'Multiple product targets',
                            'candidates': [t['name'] for t in targets]})
    return selected, missing


def _evidence(source, project, cfg):
    from .evidence import validate
    from .source_build_membership import validate as membership
    explicit = cfg.get('evidence', {}).get('compilation') or cfg.get('evidence', {}).get('build')
    candidates = [resolve_path(project, explicit)] if explicit else []
    if not explicit:
        for directory in ('ios-build-evidence', 'analysis-runs'):
            parent = project / 'spec/ref' / directory
            if parent.exists():
                candidates.extend(p.parent for p in sorted(parent.rglob('manifest.json'))
                                  if p.parent.name in {'evidence', 'compilation-evidence'})
    good, rejected = [], []
    selection = cfg.get('selection', {})
    for bundle in dict.fromkeys(candidates):
        try:
            valid = validate(source, bundle)
            if valid['kind'] != 'source_build':
                raise MigrationError('Not source_build evidence')
            settings = bundle / 'artifacts/build-settings.json'
            document = bundle / 'artifacts/source-files.json'
            if not settings.is_file() or not document.is_file():
                raise MigrationError('Build evidence lacks settings or membership')
            doc = read_json(document)
            if doc.get('kind') != 'source_build_membership':
                if explicit:
                    raise MigrationError('Automatic replay requires versioned compiler membership')
                continue
            checked = membership(source, doc, capture=bundle / 'artifacts')
            if checked['membership_status'] != 'complete':
                raise MigrationError('Incomplete compiler membership')
            actual = doc['selection']
            settings_rows = read_json(settings)
            if not isinstance(settings_rows, list):
                raise MigrationError('Build settings must contain captured target rows')
            project_paths = set()
            def canonical(path):
                path = str(path).replace('\\', '/')
                for alias in doc.get('path_aliases', []):
                    if path == alias['from'] or path.startswith(alias['from'] + '/'):
                        path = alias['to'] + path[len(alias['from']):]
                return PurePosixPath(path)
            for target_name in actual['targets']:
                rows = [r for r in settings_rows if r.get('target') == target_name]
                if len(rows) != 1:
                    raise MigrationError('Build settings do not identify one selected target')
                build = rows[0].get('buildSettings', {})
                if (build.get('CONFIGURATION') != actual['configuration']
                        or not build.get('SDK_NAME', '').startswith(actual['sdk'])
                        or not set(actual['architectures']) <= set(build.get('ARCHS', '').split())):
                    raise MigrationError('Build settings disagree with compiler membership context')
                root = canonical(doc['capture_roots']['source'])
                try:
                    project_paths.add(canonical(build['PROJECT_FILE_PATH']).relative_to(root).as_posix())
                except (KeyError, ValueError) as exc:
                    raise MigrationError('Build settings do not bind a project under captured source') from exc
            if selection.get('project') and project_paths != {selection['project']}:
                raise MigrationError('Evidence differs from selected project')
            if selection.get('workspace'):
                command = bundle / 'artifacts/device-build.command.json'
                captured = read_json(command).get('argv', []) if command.is_file() else []
                if '-workspace' not in captured or captured.index('-workspace') + 1 >= len(captured):
                    raise MigrationError('Evidence does not bind the selected workspace')
                workspace = canonical(captured[captured.index('-workspace') + 1])
                if workspace.relative_to(root).as_posix() != selection['workspace']:
                    raise MigrationError('Evidence differs from selected workspace')
            for key in ('scheme', 'configuration', 'sdk'):
                if key in selection and selection[key] != actual.get(key):
                    raise MigrationError('Evidence differs from selected ' + key)
            if selection.get('target') and selection['target'] not in actual['targets']:
                raise MigrationError('Evidence differs from selected target')
            if selection.get('arch') and selection['arch'] not in actual['architectures']:
                raise MigrationError('Evidence differs from selected architecture')
            good.append({'path': str(bundle), 'selection': actual, 'projects': sorted(project_paths), 'source_files': doc['source_files'],
                         'manifest_sha256': digest((bundle / 'manifest.json').read_bytes())})
        except (MigrationError, OSError, ValueError, KeyError) as exc:
            if explicit:
                raise MigrationError('Requested replay evidence rejected: ' + str(exc)) from exc
            rejected.append({'path': str(bundle), 'reason': str(exc)})
    identities = {digest(json_bytes({'selection': e['selection'], 'projects': e['projects']})) for e in good}
    if len(identities) > 1:
        return None, rejected, [{'field': 'selection', 'reason': 'Valid evidence covers different build contexts',
                                 'candidates': [e['selection'] for e in good]}]
    return (good[0] if good else None), rejected, []


def plan(source, project, cfg, host, *, explicit_providers=None, variant=None):
    inventory = inspect_source(source)
    mode = cfg.get('mode', 'auto')
    selection, missing = _selection(source, inventory, cfg.get('selection', {}))
    if variant and variant.get('scope') == 'project-targets':
        selection.setdefault('project', str(Path(variant['project_path']).parent))
        if len(variant.get('targets', [])) == 1:
            selection.setdefault('target', variant['targets'][0])
        selection.setdefault('configuration', variant['configuration'])
        missing = [m for m in missing if m['field'] not in {'selection.project', 'selection.target'}]
    evidence, rejected, evidence_missing = _evidence(source, project, {**cfg, 'selection': selection}) if mode != 'static' else (None, [], [])
    missing.extend(evidence_missing)
    native = host['source']['provider'] == 'macos_xcode'
    has_xcode = bool(inventory['projects'] or selection.get('workspace'))
    conditional_missing = False
    if evidence and inventory['c_conditionals']:
        from .source_analysis import _replay_variant
        context = {'evidence': evidence}
        paired, rejected_conditions = _replay_variant(project, source, context, cfg)
        rejected.extend(rejected_conditions)
        conditional_missing = not paired.get('conditional_evidence')
    decisions = []
    def choose(capability, backend, reason):
        decisions.append({'capability': capability, 'backend': backend, 'reason': reason})
    if explicit_providers is not None:
        backend = 'explicit'
        choose('providers', backend, 'Caller supplied provider plan takes precedence')
    elif variant is not None:
        backend = 'explicit_variant'
        missing = []
        choose('source_context', backend, 'Preserve caller-selected source scope; validate it when facts consume it')
    elif mode == 'static':
        backend = 'static'
        missing = []
        choose('source_context', backend, 'Explicit static-only scope')
    elif evidence and mode != 'native' and not (mode == 'auto' and native and has_xcode and conditional_missing):
        backend = 'replay'
        choose('source_context', backend, 'Current source-bound complete evidence matches selected context')
    elif native and has_xcode and mode != 'replay':
        backend = 'native'
        choose('source_context', backend, 'Xcode available and a source project exists')
        if conditional_missing:
            choose('conditional_context', 'native_recapture',
                   'Complete membership exists but current matching C-family conditional evidence is missing')
    elif mode in {'native', 'replay'}:
        backend = 'blocked'
        missing.append({'field': 'native_tools' if mode == 'native' else 'evidence.build',
                        'reason': 'Requested native capture or valid replay evidence is unavailable'})
    else:
        backend = 'static'
        choose('source_context', backend, 'No applicable native Xcode project or current complete evidence; retain unresolved context')
        if not has_xcode:
            missing = [m for m in missing if not m['field'].startswith('selection.')]
    if backend == 'replay':
        selection = {**evidence['selection'], **selection}
    steps = ['official-skills', 'official-mcp-discovery']
    if backend == 'native':
        steps += ['native-selection', 'native-source-capture']
    elif backend == 'replay':
        steps += ['replay-evidence']
    if explicit_providers is None and '.swift' in inventory['languages'] and host['host']['os'] == 'macos' and host['tools']['swift']['status'] == 'available' and mode != 'static':
        steps.append('swift-syntax-provider')
        choose('swift_syntax', 'swift_official_libraries', 'Swift source and Swift toolchain present')
    if any(Path(f['path']).name == 'Package.swift' for f in inventory['snapshot']['files']) and host['tools']['swift']['status'] == 'available' and mode != 'static':
        steps.append('manifest-evaluation')
    steps += ['facts', 'literals', 'official-mcp-evidence', 'expertise-plan', 'spec-scaffold']
    return {'schema_version': 1, 'kind': 'source-analysis-execution-plan',
            'source_sha256': inventory['snapshot']['sha256'], 'mode': mode, 'backend': backend,
            'selection': selection, 'evidence': evidence, 'rejected_evidence': rejected,
            'needs_input': missing, 'status': 'needs_input' if missing else 'ready',
            'decisions': decisions, 'steps': steps, 'inventory': inventory,
            'official_policy': 'Apple skills/MCP first; official CLI and compiler evidence cooperate; declared fallback only'}
