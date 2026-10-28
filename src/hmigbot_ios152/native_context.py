"""Native entry declarations from the current selected source view.

An alphabetical list of View types is not a launcher. Imports of UIKit (for a
colour or image) likewise do not prove a UIKit navigation architecture. Results
are declaration evidence; runtime arrival belongs to the XCTest observer.
"""
from pathlib import Path
import plistlib
import re
import xml.etree.ElementTree as ET

from hmigbot_ios.core import MigrationError, safe_child


SWIFT_UI = {'App', 'View', 'UIHostingController', 'UIViewRepresentable',
            'UIViewControllerRepresentable'}
UIKIT_UI = {'UIViewController', 'UINavigationController', 'UITabBarController',
            'UIPageViewController', 'UITableViewController', 'UICollectionViewController',
            'UIHostingController', 'UIViewRepresentable', 'UIViewControllerRepresentable'}
EXTENSION_UI = {'Widget', 'WidgetBundle', 'ControlWidget'}


def _names(values):
    # Only normalize identifiers already obtained from official syntax nodes.
    return {w for v in values for w in re.findall(r'\b[A-Za-z_]\w*\b', v)}


def _type_name(value):
    return str(value).rsplit('.', 1)[-1].strip('`')


def _selected_plists(source):
    """Use selected target declarations; never select an arbitrary Info.plist."""
    plists, issues = [], []
    if source.selection:
        from hmigbot_ios.project_scope import resolve
        _, graph = resolve(source.root, source.config['ios']['variant'], _context=True)
        selected = set(source.selection['targets'])
        for config in graph.selected_configs:
            if config['owner'] not in selected:
                continue
            path = config['settings'].get('INFOPLIST_FILE')
            if not path:
                continue  # generated Info.plist; @main declarations remain evidence
            if not isinstance(path, str):
                issues.append({'kind': 'unresolved_info_plist', 'target': config['owner']})
                continue
            path = path.replace('$(SRCROOT)/', '').replace('${SRCROOT}/', '')
            if '$' in path:
                issues.append({'kind': 'unresolved_info_plist', 'target': config['owner'], 'value': path})
                continue
            # INFOPLIST_FILE is relative to the Xcode project's source root.
            base = Path(source.selection['project_path']).parent.parent
            plists.append((base / path).as_posix())
    else:
        candidates = [p for p in source.records if Path(p).name == 'Info.plist']
        if len(candidates) == 1:
            plists = candidates
        elif candidates:
            issues.append({'kind': 'ambiguous_info_plist', 'candidates': sorted(candidates)})
    return sorted(set(plists)), issues


def describe(source):
    types, by_file, unknowns = [], {}, []
    for name in sorted(source.files):
        if not name.endswith('.swift'):
            if Path(name).suffix in {'.m', '.mm'}:
                unknowns.append({'kind': 'objc_entry_requires_review', 'file': name,
                                 'reason': 'No compiler-resolved Objective-C entry facts in SwiftSyntax'})
            continue
        source.text(name)  # validates selected Release source before consuming nodes
        nodes = source.syntax(name)['nodes']
        by_file[name] = nodes
        for n in nodes:
            if n['kind'] != 'type':
                continue
            v = n['value']
            parents = [x for x in nodes if x['kind'] == 'type' and x['start'] < n['start'] and x['end'] > n['end']]
            owners = [x['value']['name'] for x in sorted(parents, key=lambda x: x['start'])]
            types.append({'symbol': '.'.join(owners + [v['name']]), 'short': v['name'],
                          'file': name, 'line': n['line'], 'start': n['start'], 'end': n['end'],
                          'kind': v['kind'], 'bases': sorted(_names(v.get('inherits', []))),
                          'attributes': v.get('attributes', '')})
    named = {t['symbol']: t for t in types}
    # Resolve local superclass chains for architectural declarations only.
    def bases(t, seen=()):
        result = set(t['bases'])
        for name in t['bases']:
            if name in seen:
                continue
            matches = [v for v in types if v['symbol'] == name or v['short'] == name]
            if len(matches) == 1:
                result.update(bases(matches[0], seen + (name,)))
        return result
    roots, extension_roots, render_roots = [], [], []
    swift_files, uikit_files, main_markers = set(), set(), []
    for t in types:
        inherited = bases(t)
        if inherited & SWIFT_UI:
            swift_files.add(t['file'])
        if inherited & UIKIT_UI:
            uikit_files.add(t['file'])
        # AttributeSyntax has exact declaration attachment; text here is the
        # attributes field of that parsed type, never a source regex search.
        attrs = _names([t['attributes']])
        is_main = bool(attrs & {'main', 'UIApplicationMain'})
        if is_main:
            main_markers.append(t)
            row = {k: t[k] for k in ('symbol', 'short', 'file', 'line')}
            row['evidence'] = 'SwiftSyntax:attached-main-attribute'
            if inherited & EXTENSION_UI:
                row['kind'] = 'widget-extension'
                extension_roots.append(row)
            elif 'App' in inherited:
                row['kind'] = 'SwiftUI.App'
                roots.append(row)
            elif 'UIApplicationDelegate' in inherited:
                row['kind'] = 'UIApplicationDelegate'
                roots.append(row)
            else:
                unknowns.append({'kind': 'unresolved_main_type', **row, 'bases': sorted(inherited)})
    plist_paths, plist_issues = _selected_plists(source)
    unknowns.extend(plist_issues)
    storyboard_names = set()
    declared_delegates = []
    for name in plist_paths:
        path = safe_child(source.root, name)
        try:
            data = plistlib.loads(path.read_bytes())
        except (OSError, ValueError, plistlib.InvalidFileException) as exc:
            raise MigrationError('Cannot read declared Info.plist ' + name + ': ' + str(exc)) from exc
        if data.get('UIMainStoryboardFile'):
            storyboard_names.add(str(data['UIMainStoryboardFile']))
        scenes = data.get('UIApplicationSceneManifest', {}).get('UISceneConfigurations', {})
        if not isinstance(scenes, dict):
            raise MigrationError('Invalid UISceneConfigurations in ' + name)
        for configurations in scenes.values():
            if not isinstance(configurations, list):
                raise MigrationError('Invalid scene configuration list in ' + name)
            for scene in configurations:
                if scene.get('UISceneStoryboardFile'):
                    storyboard_names.add(str(scene['UISceneStoryboardFile']))
                if scene.get('UISceneDelegateClassName'):
                    declared_delegates.append({'symbol': _type_name(scene['UISceneDelegateClassName']),
                                               'plist': name, 'evidence': 'Info.plist:UISceneDelegateClassName'})
    for delegate in declared_delegates:
        matches = [t for t in types if t['short'] == delegate['symbol']]
        if len(matches) == 1:
            t = matches[0]
            render_roots.append({**delegate, 'file': t['file'], 'line': t['line'], 'kind': 'scene-delegate'})
        else:
            unknowns.append({'kind': 'unresolved_scene_delegate', **delegate})
    from .native_resources import selected
    resources = selected(source)
    unknowns.extend(resources['issues'])
    for name in (p for p in resources['files'] if p.endswith('.storyboard')):
        if Path(name).stem not in storyboard_names:
            continue
        raw = safe_child(source.root, name).read_bytes()
        if b'<!DOCTYPE' in raw.upper() or b'<!ENTITY' in raw.upper():
            raise MigrationError('Unsupported XML entities in ' + name)
        try:
            doc = ET.fromstring(raw)
        except ET.ParseError as exc:
            raise MigrationError('Cannot parse storyboard ' + name) from exc
        initial = doc.get('initialViewController')
        matches = [n for n in doc.iter() if n.get('id') == initial] if initial else []
        if len(matches) == 1:
            n = matches[0]
            render_roots.append({'kind': 'storyboard-initial', 'symbol': n.get('customClass'),
                                 'storyboard_id': initial, 'file': name,
                                 'evidence': 'Info.plist+IB:initialViewController'})
            uikit_files.add(name)
        else:
            unknowns.append({'kind': 'unresolved_storyboard_initial', 'file': name})
    # Explicit WindowGroup child call facts, including generic container roots.
    for root in roots:
        if root['kind'] != 'SwiftUI.App':
            continue
        t = named[root['symbol']]
        nodes = by_file[t['file']]
        for window in [n for n in nodes if n['kind'] == 'call' and t['start'] <= n['start'] < t['end']
                       and n['value'].get('callee_name', n['value'].get('callee')) == 'WindowGroup']:
            closures = window['value'].get('trailing_closures', [])
            for closure in closures:
                span = closure['body']
                children = [n for n in nodes if n['kind'] == 'call' and
                            span['start_utf8'] <= n['start_utf8'] < span['end_utf8']]
                # A chained modifier encloses its base constructor in syntax.
                # Exclude calls inside *nested* closures, not the base of a
                # modifier chain. This preserves conditional root branches.
                nested_closures = [c['body'] for x in children for c in x['value'].get('trailing_closures', [])]
                outer = [n for n in children if not n['value'].get('callee_base') and
                         n['value'].get('callee_name', '')[:1].isupper() and
                         not any(c['start_utf8'] <= n['start_utf8'] < c['end_utf8'] for c in nested_closures)]
                for n in outer:
                    name = n['value'].get('callee_name', '')
                    if name:
                        render_roots.append({'kind': 'WindowGroup-content', 'symbol': name,
                                             'file': t['file'], 'line': n['line'],
                                             'evidence': 'SwiftSyntax:WindowGroup-trailing-closure'})
    unique = {(r['symbol'], r['file']): r for r in roots}
    roots = list(unique.values())
    launcher = roots[0]['short'] if len(roots) == 1 else None
    if len(roots) > 1:
        unknowns.append({'kind': 'ambiguous_application_entry', 'candidates': [r['symbol'] for r in roots]})
    if not roots:
        unknowns.append({'kind': 'application_entry_not_declared',
                         'reason': 'Select the application target or review native entry declarations'})
    swift_count = len(swift_files)
    ui_count = len(uikit_files)
    arch = 'hybrid' if swift_count and ui_count else 'pure_compose' if swift_count else 'pure_traditional'
    return {'source_platform': 'ios', 'source_root': str(source.root), 'source_sha256': source.fingerprint,
            'evidence_kind': 'current-selected-source-declarations', 'arch': arch, 'architecture': arch,
            'frameworks': {'SwiftUI': sorted(swift_files), 'UIKit': sorted(uikit_files)},
            'application_roots': roots, 'extension_roots': extension_roots, 'render_roots': render_roots,
            'launcher_short': launcher,
            'launcher_arch': ('compose' if roots and roots[0]['kind'] == 'SwiftUI.App' else 'xml') if launcher else None,
            'compose_screen_ratio': swift_count / len(swift_files | uikit_files) if swift_files | uikit_files else 0,
            'unknowns': unknowns,
            'wire_labels': {'pure_compose': 'SwiftUI', 'pure_traditional': 'UIKit/IB', 'hybrid': 'mixed native UI'}}
