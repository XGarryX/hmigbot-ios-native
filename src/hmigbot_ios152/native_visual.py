"""iOS source observations for the existing visual verification workflow.

XCTest supplies real UI facts/actions; this module supplies native identity,
point/pixel conversion and the existing capture/ledger wire contract. It does
not judge image similarity, waive functional checks or complete a round.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import time
import xml.etree.ElementTree as ET

from hmigbot_ios.core import MigrationError, read_json, write_json, atomic_write

TYPE_NAMES = {1:'Other', 2:'Application', 3:'Group', 4:'Window', 5:'Sheet',
              7:'Alert', 8:'Dialog', 9:'Button', 14:'PopUpButton', 18:'Popover',
              19:'Keyboard', 20:'Key', 21:'NavigationBar', 22:'TabBar', 24:'Toolbar',
              25:'StatusBar', 26:'Table', 32:'CollectionView', 33:'Slider',
              34:'PageIndicator', 35:'ProgressIndicator', 37:'SegmentedControl',
              38:'Picker', 39:'PickerWheel', 40:'Switch', 41:'Toggle', 42:'Link',
              43:'Image', 44:'Icon', 45:'SearchField', 46:'ScrollView', 48:'StaticText',
              49:'TextField', 50:'SecureTextField', 51:'DatePicker', 52:'TextView',
              53:'Menu', 54:'MenuItem', 58:'WebView', 75:'Cell', 79:'Stepper', 80:'Tab'}
INTERACTIVE = {9,10,12,13,14,15,16,17,20,33,37,38,39,40,41,42,44,45,49,50,51,52,54,75,79,80}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def collection_inputs(tree, project, previous=None):
    from .native_canonical import _source_current
    current = _source_current(tree,project,allow_manifest_collection=True) or {}
    if previous and previous.get('native_blackbox_source_inputs_sha256') != current.get('native_blackbox_source_inputs_sha256'):
        raise MigrationError('Native source classification inputs changed during collection; recapture affected observations')
    return current


def observer_build(tree, session):
    value=getattr(session,'state',{}).get('source_app_build')
    expected=tree.get('native_context',{}).get('source_sha256')
    if value and expected and value.get('build_record_binding') and value.get('source_sha256')!=expected:
        raise MigrationError('Owned source observer was built from an earlier source snapshot; rebuild before capture')
    return value


def nodes(tree):
    yield tree
    for child in tree.get('children', []):
        yield from nodes(child)


def selector_matches(node, selector):
    for key, value in selector.items():
        if key in {'type','element_type'}:
            actual = TYPE_NAMES.get(node.get('element_type'), str(node.get('element_type')))
            if isinstance(value, int):
                if node.get('element_type') != value: return False
            elif actual != str(value).removeprefix('XCUIElementType'): return False
        elif key in {'identifier', 'label', 'value', 'title'}:
            if node.get(key) != value: return False
        else:
            raise MigrationError('Unsupported native identity selector: ' + key)
    return bool(selector) and node.get('exists') is True


def observed_signatures(observation):
    return [{'type': TYPE_NAMES.get(n.get('element_type'), str(n.get('element_type'))),
             'identifier': n.get('identifier', ''), 'label': n.get('label', ''),
             'value': n.get('value'), 'frame': n.get('frame')}
            for n in nodes(observation['tree']) if n.get('exists') is True]


def signature_strings(observation):
    result = set()
    for n in nodes(observation['tree']):
        if n.get('exists') is not True: continue
        for field, prefix in [('identifier','identifier:'),('label','text:'),('value','value:')]:
            if n.get(field) is not None and str(n[field]): result.add(prefix+str(n[field]))
    return sorted(result)


def capture_ref(raw):
    result = {'png':raw['png'],'native_json':raw['native_json'],'sha256':raw['sha256'],
            'request_id':raw['observation']['request_id'],'session':raw['observation']['session']}
    # The native JSON records every actual scope. Keep legacy app references
    # byte-identical, and make system captures explicit for downstream judges.
    if raw['observation'].get('scope','app') != 'app':
        result['scope'] = raw['observation']['scope']
    return result


def arrival(observation, page, identities, live_queries=None):
    """Exact native signatures, checked for competing page matches.

    Identities are source/grounding annotations, not Android Activity names.
    An absent/ambiguous identity remains not_arrived and cannot name a baseline.
    """
    checks = []
    matched = []
    scope = observation.get('scope','app')
    for candidate, contract in identities.items():
        if contract.get('scope','app') != scope:
            continue
        required = contract.get('required', [])
        excluded = contract.get('excluded', [])
        if not required:
            checks.append({'page':candidate, 'status':'identity_unavailable'})
            continue
        present = [sum(selector_matches(n, s) for n in nodes(observation['tree'])) for s in required]
        forbidden = [sum(selector_matches(n, s) for n in nodes(observation['tree'])) for s in excluded]
        live = (live_queries or {}).get(candidate)
        if live is not None:
            present = [1 if x['visible_unique'] else 0 for x in live['required']]
            # A failed/ambiguous query is not proof that an excluded element is
            # absent. Only the public query's explicit not_found proves absence.
            forbidden = [0 if x.get('absence_proven') else max(1,forbidden[i])
                         for i,x in enumerate(live['excluded'])]
        # A selector that matches several elements is not a unique grounding.
        okay = all(count == 1 for count in present) and not any(forbidden)
        checks.append({'page':candidate, 'required_match_counts':present,
                       'excluded_match_counts':forbidden, 'matched':okay, 'live_queries':live})
        if okay: matched.append(candidate)
    blockers = []
    if scope == 'springboard' and observation.get('bundle_id') != 'com.apple.springboard':
        blockers.append('system_scope_identity_mismatch')
    if observation.get('app_state_before') != 4 or observation.get('app_state_after') != 4:
        blockers.append('source_not_foreground')
    if observation.get('system_overlay', {}).get('alert_count', 0):
        blockers.append('system_alert_present')
    if observation.get('system_tree_status') != 'observed':
        blockers.append('system_overlay_unknown')
    all_matched=list(matched)
    hosts=[name for name in matched if identities[name].get('_native_identity_host_members')]
    leaves=[name for name in matched if name not in hosts]
    expected=identities.get(page,{})
    expected_host=bool(expected.get('_native_identity_host_members'))
    if (hosts or expected_host) and not expected.get('_native_identity_ancestry_valid',True):
        blockers.append('identity_relationship_unavailable')
    matched=hosts if expected_host else leaves
    relation_ok=True
    if hosts:
        if len(hosts)>1:relation_ok=False
        elif expected_host:
            relation_ok=(len(leaves)<=1 and all(page in identities[name].get('_native_identity_ancestors',[]) for name in leaves))
        else:
            relation_ok=all(host in expected.get('_native_identity_ancestors',[]) for host in hosts)
        if not relation_ok:blockers.append('unrelated_or_ambiguous_native_host')
    if matched != [page]:
        blockers.append('identity_unavailable' if not matched else 'wrong_or_ambiguous_page')
    return {'arrived':not blockers, 'expected_page':page, 'matched_pages':matched,
            'all_matched_pages':all_matched,'matched_host_pages':hosts,
            'identity_level':'host' if expected_host else 'leaf',
            'blockers':blockers, 'checks':checks, 'method':'unique-native-signature',
            'evidence_kind':'live-query-backed' if live_queries is not None else 'snapshot-diagnostic',
            'verified':live_queries is not None and not blockers,
            'request_id':observation['request_id']}


def live_page_queries(session, observation, identities):
    """Use real unique XCUI queries to reject offscreen/background signatures.

    Snapshot layers can contain the same native Icon twice, whereas XCUI's
    public query returns one unique element. Retain both facts in evidence.
    """
    result = {}; scope=observation.get('scope','app')
    for page,contract in identities.items():
        if contract.get('scope','app') != scope or not contract.get('required'): continue
        if not all(any(selector_matches(n,s) for n in nodes(observation['tree'])) for s in contract['required']): continue
        record={'required':[],'excluded':[]}
        for group in ('required','excluded'):
            for selector in contract.get(group,[]):
                query={k:v for k,v in selector.items() if k in {'identifier','label','element_type'}}
                typ=selector.get('type')
                if typ is not None:
                    if isinstance(typ,int):query['element_type']=typ
                    else:
                        names={v:k for k,v in TYPE_NAMES.items()}
                        resolved=names.get(str(typ).removeprefix('XCUIElementType'))
                        if resolved is not None:query['element_type']=resolved
                if not query:
                    record[group].append({'selector':selector,'visible_unique':False,'absence_proven':False,
                                          'reason':'native-query-selector-unavailable'});continue
                response=session.command('find',{'scope':scope,'selector':query})
                if response.get('session_invalidated'):
                    from .xcode_ui import XcodeUIError
                    raise XcodeUIError('Native identity query invalidated observer session; original error: '+json.dumps(response.get('error')))
                observed=response.get('result',{})
                visible=bool(response.get('ok') and observed.get('hittable') is True and selector_matches(observed,selector))
                absent=not response.get('ok') and response.get('error',{}).get('code') == 'not_found'
                record[group].append({'selector':selector,'visible_unique':visible,'absence_proven':absent,'response':response})
        result[page]=record
    return result


def observation_xml(observation, hittability=None, *, native_sha256=None, png_sha256=None):
    """Native XML accepted by legacy text/structure consumers, with true geometry.

    class is XCUIElementType*, resource-id is intentionally empty; actual native
    identifiers stay in identifier. clickable preserves visible enabled native
    interaction candidates; native_hittable records the separate live query.
    bounds are screenshot pixels, frame_*
    are original screen points. No Android types, activities or IDs are made up.
    """
    if observation.get('platform') != 'ios': raise MigrationError('Expected an iOS observation')
    geometry = observation['screenshot']
    sx, sy = geometry['pixel_per_point_x'], geometry['pixel_per_point_y']
    if not all(isinstance(x,(int,float)) and math.isfinite(x) and x > 0 for x in (sx,sy)):
        raise MigrationError('Observed screenshot point/pixel mapping is unavailable')
    origin = geometry['origin_screen_points']
    pixels = geometry['pixel_size']
    width, height = pixels['width'], pixels['height']
    if not all(isinstance(v,(int,float)) and math.isfinite(v) for v in (origin['x'],origin['y'],width,height)) or width <= 0 or height <= 0:
        raise MigrationError('Observed screenshot viewport is unavailable')
    points = geometry.get('point_size')
    if points and (round(points['width']*sx) != width or round(points['height']*sy) != height):
        raise MigrationError('Screenshot point and pixel dimensions disagree')
    if not math.isclose(sx,sy,rel_tol=1e-6):
        raise MigrationError('Screenshot orientation or point/pixel aspect ratio disagrees')
    viewport = (0,0,int(width),int(height))
    bounds = lambda box: '[%d,%d][%d,%d]' % box
    root = ET.Element('hierarchy', {'platform':'ios', 'schema':'hmigbot.xcui.v1',
        'bundle_id':observation['bundle_id'], 'collection_method':observation['collection_method'],
        'request_id':observation['request_id'], 'native_coordinate_space':'screen_points',
        'bounds_coordinate_space':'screenshot_pixels', 'pixel_per_point_x':str(sx), 'pixel_per_point_y':str(sy),
        'comparison_projection':'screenshot-viewport-v1', 'bounds':bounds(viewport),
        'width':str(width),'height':str(height)})
    if native_sha256: root.set('native_snapshot_sha256',native_sha256)
    if png_sha256: root.set('screenshot_sha256',png_sha256)
    root.set('capture_started_at',str(observation['started_at']))
    root.set('capture_finished_at',str(observation['finished_at']))
    def add(parent, node, path):
        frame = node.get('frame')
        if not isinstance(frame, dict) or not all(isinstance(frame.get(k),(int,float)) and math.isfinite(frame[k])
                                                for k in ('x','y','width','height')):
            raise MigrationError('Invalid native frame in captured hierarchy')
        x,y,w,h = (frame[k] for k in ('x','y','width','height'))
        box = (round((x-origin['x'])*sx), round((y-origin['y'])*sy),
               round((x+w-origin['x'])*sx), round((y+h-origin['y'])*sy))
        clipped = (max(0,box[0]),max(0,box[1]),min(int(width),box[2]),min(int(height),box[3]))
        visible = node.get('exists') is True and clipped[2] > clipped[0] and clipped[3] > clipped[1]
        native = node.get('element_type')
        name = TYPE_NAMES.get(native, str(native))
        live_hittable = (hittability or {}).get(path, node.get('hittable'))
        text = node.get('value') if native in {45,49,50,52} and node.get('value') is not None else node.get('label', '')
        label = node.get('label') or ''
        # AX snapshots retain offscreen descendants. Legacy consumers ignore
        # exists/visible and derive screen size from bounds, so project all of
        # their text, geometry and action fields together. Preserve raw facts.
        comparison_box = clipped if visible else (0,0,0,0)
        if path == '0' and native in {2,4}: comparison_box = viewport
        if not visible or native in {2,4}: text,label = '',''
        attrs = {'index':path.rsplit('/',1)[-1], 'class':'XCUIElementType'+name,
                 'native_type':str(native), 'identifier':node.get('identifier') or '',
                 'native_label':node.get('label') or '', 'native_value':str(node.get('value') or ''),
                 'text':str(text or ''), 'content-desc':str(label),
                 'resource-id':'', 'package':observation['bundle_id'],
                 'bounds':bounds(comparison_box), 'native_original_bounds':bounds(box),
                 'frame_points':json.dumps(frame, sort_keys=True),
                 'comparison_visible':str(visible).lower(),
                 'comparison_omitted_reason':('not_exists' if node.get('exists') is not True else 'outside_screenshot') if not visible else '',
                 'exists':str(node.get('exists') is True).lower(),
                 'enabled':str(node.get('enabled') is True).lower(),
                 'selected':str(node.get('selected') is True).lower(),
                 'clickable':str(visible and native in INTERACTIVE and node.get('enabled') is True).lower(),
                 'native_hittable':str(live_hittable).lower() if live_hittable is not None else 'unknown',
                 'scrollable':str(visible and native in {26,32,46}).lower(), 'native_path':path}
        element = ET.SubElement(parent, 'node', attrs)
        for i, child in enumerate(node.get('children', [])): add(element, child, path+'/'+str(i))
    add(root, observation['tree'], '0')
    return ET.tostring(root, encoding='unicode')+'\n'


def live_hittability(session, observation):
    result = {}
    def visit(node, path):
        if node.get('element_type') in INTERACTIVE and node.get('exists'):
            selector = {'element_type':node['element_type']}
            if node.get('identifier'): selector['identifier'] = node['identifier']
            elif node.get('label'): selector['label'] = node['label']
            else: selector = None
            if selector:
                response = session.command('find', {'selector':selector,'scope':observation.get('scope','app')})
                if response.get('session_invalidated'):
                    from .xcode_ui import XcodeUIError
                    raise XcodeUIError('Native control query invalidated observer session')
                value = response.get('result', {})
                if response.get('ok') and value.get('count', 1) == 1:
                    result[path] = value.get('hittable')
        for i, child in enumerate(node.get('children', [])): visit(child, path+'/'+str(i))
    visit(observation['tree'], '0')
    return result


def capture(session, page, identities, output, *, overwrite=False, scope='app', trip=None):
    output = Path(output); output.mkdir(parents=True, exist_ok=True)
    if any(c in page for c in ('/','\\')) or page in {'','.', '..'}:
        raise MigrationError('Invalid page filename')
    png, xml, meta = output/(page+'.png'), output/(page+'.ios.xml'), output/(page+'.capture.json')
    if not overwrite and any(p.exists() for p in (png,xml,meta)):
        raise MigrationError('Capture already exists; explicit overwrite is required')
    if overwrite and any(p.exists() for p in (png,xml,meta)):
        previous = read_json(meta) if meta.is_file() else None
        # Preserve old evidence, but never let a failed re-capture leave its
        # previous success metadata eligible for new baseline placement.
        write_json(meta,{'status':'capture_pending','page_id':page,'trip':trip,
                         'invalidated_at':datetime.now(timezone.utc).isoformat(),
                         'reason':'Explicit working-capture overwrite requested',
                         'previous_capture':previous})
    started = time.monotonic()
    from .xcode_ui import XcodeUIError
    try:
        raw = session.capture(output/'native-observations',scope=scope)
    except XcodeUIError as exc:
        return 13, {'status':'dump_unavailable','page_id':page,'error':str(exc)}
    observation = raw['observation']
    identity = arrival(observation, page, identities,live_page_queries(session,observation,identities))
    write_json(output/(raw['response']['id']+'.arrival.json'), identity)
    if not identity['arrived']:
        return 15, {'status':'wrong_page', 'page_id':page, 'arrival':identity,
                    'raw_capture':capture_ref(raw), 'notes':['No canonical page filename was assigned']}
    hittability = live_hittability(session, observation)
    # Check the same identity after potentially slow live element queries.
    after = session.command('snapshot',{'scope':scope})
    if not after.get('ok'): raise MigrationError('Post-capture snapshot unavailable')
    # A fresh paired capture ensures that image and final tree use one request.
    try:
        fresh = session.capture(output/'native-observations',scope=scope)
    except XcodeUIError as exc:
        return 13, {'status':'dump_unavailable','page_id':page,'error':str(exc)}
    identity_after = arrival(fresh['observation'], page, identities,
                             live_page_queries(session,fresh['observation'],identities))
    write_json(output/(fresh['response']['id']+'.arrival.json'),identity_after)
    if not identity_after['arrived']:
        return 15, {'status':'wrong_page','page_id':page,'arrival':identity_after,'raw_capture':capture_ref(fresh)}
    from .apple_image import inspect
    try:
        image = inspect(fresh['png'])
    except MigrationError as exc:
        return 14, {'status':'screenshot_failed','page_id':page,'error':str(exc),'raw_capture':capture_ref(fresh)}
    dimensions = fresh['observation']['screenshot']['pixel_size']
    if (image['width'],image['height']) != (dimensions['width'],dimensions['height']):
        return 14, {'status':'screenshot_failed','page_id':page,'reason':'PNG and observed geometry differ','raw_capture':capture_ref(fresh)}
    if image['black_sample']:
        return 12, {'status':'empty_state','page_id':page,'reason':'ImageIO black screenshot sample','raw_capture':capture_ref(fresh),'image_inspection':image}
    # Hittability paths are valid only if the native node sequence stayed equal.
    if observed_signatures(observation) != observed_signatures(fresh['observation']):
        hittability = {}
    shutil.copy2(fresh['png'], png)
    atomic_write(xml, observation_xml(fresh['observation'], hittability,
                                    native_sha256=digest(fresh['native_json']),png_sha256=digest(fresh['png'])).encode())
    raw_xml = Path(fresh['native_json']).with_suffix('.ios.xml')
    shutil.copy2(xml,raw_xml)
    result = {'status':'ok', 'page_id':page, 'trip':trip,'shot_path':str(png.resolve()), 'dump_path':str(xml.resolve()),
              'raw_png':fresh['png'],'raw_xml':str(raw_xml),
              'raw_sha256':{'png':digest(fresh['png']),'xml':digest(raw_xml),'native_json':digest(fresh['native_json'])},
              'native_json':fresh['native_json'], 'source_platform':'ios',
              'native_scope':scope,'native_bundle_id':fresh['observation']['bundle_id'],
              'captured_at':datetime.now(timezone.utc).isoformat(), 'nav_by':'xctest-public-actions',
              'verify_by':'unique-native-signature+foreground+system-overlay+post-query-check',
              'arrival':identity_after, 'hop_n':0, 'reach_path':[],
              'observed_signature':signature_strings(fresh['observation']),
              'native_observed_signature':observed_signatures(fresh['observation']), 'image_inspection':image,
              'elapsed':{'total':time.monotonic()-started}, 'notes':[],
              'sha256':{'png':digest(png),'xml':digest(xml),'native_json':digest(fresh['native_json'])}}
    source_build=getattr(session,'state',{}).get('source_app_build')
    if source_build:result['source_app_build']=source_build
    write_json(meta, result)
    return 0, result


def identities_from_tree(tree):
    result = {};records=[]
    for collection in ('pages','fragments','dialogs'):
        values = tree.get(collection, [])
        if isinstance(values, dict): values = values.values()
        for page in values:
            records.append(page)
            if page.get('native_identity'):
                result[page['id']]={k:v for k,v in page['native_identity'].items() if not k.startswith('_native_identity_')}
    by_id={p['id']:p for p in records}
    def resolve(name,file=None):
        if not isinstance(name,str) or not name:return None
        exact=[p['id'] for p in records if p['id']==name and (file is None or p.get('ios_file')==file)]
        if len(exact)==1:return exact[0]
        matches=[p['id'] for p in records if name in {p['id'],p.get('fq_class')}
                 and (file is None or p.get('ios_file')==file)]
        return matches[0] if len(matches)==1 else None
    for page in records:
        name=page['id']
        if name not in result:continue
        chain=[];current=page;valid=True;seen={name}
        while current.get('parent_in_nav'):
            parent=resolve(current['parent_in_nav'])
            if parent is None or parent in seen:valid=False;break
            chain.append(parent);seen.add(parent);current=by_id[parent]
        result[name]['_native_identity_ancestors']=chain if valid else []
        result[name]['_native_identity_ancestry_valid']=valid
        if page.get('is_container') is not True or page.get('navigation_contract',{}).get('relationship_kind')!='activity_root':continue
        groups=[g for g in tree.get('native_tab_groups',[]) if resolve(g.get('host'),g.get('file'))==name]
        if len(groups)!=1:continue
        targets=[resolve(item.get('target')) for item in groups[0].get('items',[])]
        children={p['id'] for p in records if resolve(p.get('parent_in_nav'))==name
                  and p.get('navigation_contract',{}).get('relationship_kind')=='tab'}
        contains={resolve(child) for child in page.get('contains',[]) if isinstance(child,str)}
        if targets and None not in targets and len(set(targets))==len(targets) and set(targets)==children==contains:
            result[name]['_native_identity_host_members']=targets
    return result


def fact_scaffold(source, bundle):
    """Fresh syntax scaffold for the existing source analyst/enrichment step.

    This deliberately does not import old SPEC navigation or invent functional
    outcomes. The normal analyst must classify auxiliary views, enrich behavior
    and ground page identities before the original visual gates can pass.
    """
    from .native_routes import analyze
    facts = analyze(source)
    pages = []
    roots = {r['symbol'] for r in facts['context']['application_roots']}
    extensions = {r['symbol'] for r in facts['context']['extension_roots']}
    by_name = Counter(p['name'] for p in facts['pages'])
    ids = {}
    for item in facts['pages']:
        name = item['name']
        if name in roots or name in extensions: continue
        identity = name if by_name[name] == 1 else name+'_'+hashlib.sha256(item['file'].encode()).hexdigest()[:8]
        ids[(name,item['file'])] = identity
        controls = [c for c in facts['controls'] if c['owner'] == name and c['file'] == item['file']]
        components = []
        for c in controls:
            component = {'id':c['id'], 'type':c['type'], 'parent_id':None,
                         'uncertain':c.get('text') is None, 'text':c.get('text'),
                         'hint':None, 'image_resource':None, 'content_desc':None,
                         'is_interactive':c['interactive'], 'visibility':c.get('visibility'),
                         'source_anchor':{'file':c['file'],'line':c['line']},
                         'native_source_span':{'start':c['start'],'end':c['end']},
                         'triggers':[], 'behaviors':[], 'notes':['Syntax fact; runtime visibility remains to be grounded']}
            if c.get('accessibility_identifier') is not None:
                component['native_identifier'] = c['accessibility_identifier']
            if c.get('accessibility_label') is not None:
                component['native_accessibility_label'] = c['accessibility_label']
            components.append(component)
        bases = ' '.join(item.get('inherits',[]))
        surface = 'widget' if any(x in bases for x in ('Widget','ControlWidget')) else 'application'
        pages.append({'id':identity, 'type':'Activity', 'native_type':bases,
                      'native_surface':surface, 'fq_class':name, 'package':bundle,
                      'label':name, 'purpose':None, 'uncertain':True, 'ios_file':item['file'],
                      'layout_file':None, 'harmony_target':None, 'contains':[], 'shows_dialogs':[],
                      'components':components, 'navigation':{'inbound':[],'outbound':[]},
                      'reach_paths':[], 'functional_checks':[],
                      'notes':['Native source candidate: analyst must classify page/fragment and enrich behavior before verification']})
    lookup = {}
    for page in pages:
        lookup.setdefault(page['fq_class'],[]).append(page['id'])
    edges = []
    for route in facts['routes']:
        owner = route.get('source') or route.get('owner')
        target = route.get('target')
        left,right = lookup.get(owner,[]),lookup.get(target,[])
        if len(left) == len(right) == 1:
            edges.append({'from':left[0], 'to':right[0], 'via_component':route.get('control_id'),
                          'trigger':route.get('trigger') or route.get('via'),
                          'is_dynamic':route.get('resolution') != 'direct',
                          'declaration_only':bool(route.get('declaration_only')),
                          'native_evidence':route})
    app_roots = facts['context']['application_roots']
    tree = {'$schema_version':1, 'schema_version':1,
            'source':{'platform':'ios','ios_root':str(source.root),'source_sha256':facts['source_sha'],
                      'generated_at':datetime.now(timezone.utc).isoformat(),
                      'generator':{'skill':'ios-fact-tree','script':'ios_visual.py facts'},'toolkit_refs':{}},
            'source_platform':'ios',
            'native_source_sha256':facts['source_sha'], 'native_source_root':str(source.root),
            'native_context':facts['context'], 'native_unknowns':facts['unknowns'],
            'native_tab_groups':facts.get('native_tab_groups',[]),
            'app':{'package':bundle, 'label':None, 'launcher_activity':None,
                   'launcher_short':None,'native_bootstrap_type':facts['context']['launcher_short'],
                   'native_render_roots':facts['context']['render_roots'],'native_application_roots':app_roots,
                   'min_sdk':None,'target_sdk':None,'version_name':None},
            'features':[], 'pages':pages,'fragments':[],'dialogs':[],
            'flow_graph':{'nodes':[{'id':p['id'],'type':p['type'],'label':p['label']} for p in pages],
                          'edges':edges}, 'dependency_graph':{},
            'stats':{'pages':len(pages),'components':sum(len(p['components']) for p in pages),'edges':len(edges)},
            'notes':['Fresh current-selected-source scaffold, not runtime observation or completed enrichment',
                     'Native tab groups are source declarations for analyst enrichment, not generated navigation edges or runtime observations',
                     'Activity/launcher_activity are historical wire names; values describe native iOS source declarations']}
    return tree, facts


def capture_cli(argv):
    from .xcode_ui import XcodeUISession, XcodeUIError
    p = argparse.ArgumentParser(description='Native iOS capture using an owned XCUITest observer')
    p.add_argument('tree'); p.add_argument('--page',required=True); p.add_argument('--trip',required=True)
    p.add_argument('--serial'); p.add_argument('--pkg'); p.add_argument('--launcher')
    p.add_argument('--project-root',default='.'); p.add_argument('--shots-dir')
    p.add_argument('--native-session',default=os.environ.get('HMIGBOT_IOS_SESSION'))
    p.add_argument('--capture-only',action='store_true'); p.add_argument('--overwrite',action='store_true')
    p.add_argument('--no-reset',action='store_true'); p.add_argument('--no-replay',action='store_true')
    p.add_argument('--nav-only',action='store_true'); p.add_argument('--plan-dir'); p.add_argument('--pending-dir'); p.add_argument('--boot-wait',type=float)
    a = p.parse_args(argv)
    if not a.native_session: raise MigrationError('Native iOS source capture needs --native-session or HMIGBOT_IOS_SESSION')
    if not a.capture_only:
        raise MigrationError('iOS source navigation uses explicit XCUITest edge actions, then --capture-only; no Activity/reset replay is substituted')
    tree = read_json(Path(a.tree))
    source_inputs = collection_inputs(tree,Path(a.project_root))
    session = XcodeUISession.open(a.native_session)
    if a.pkg and a.pkg != session.state['bundle_id']: raise MigrationError('Capture bundle does not match owned source observer')
    if a.serial and a.serial != session.state['udid']: raise MigrationError('Capture UDID does not match owned source observer')
    if tree.get('app',{}).get('package') != session.state['bundle_id']:
        raise MigrationError('Source tree bundle does not match the owned iOS observer')
    observer_build(tree,session)
    output = a.shots_dir or Path(a.project_root)/'spec/visual-verify/edgewalk/shots'
    identities = identities_from_tree(tree)
    scope = identities.get(a.page,{}).get('scope','app')
    code,result = capture(session,a.page,identities,output,overwrite=a.overwrite,scope=scope,trip=a.trip)
    result.update(source_inputs)
    if code == 0:
        try:
            result.update(collection_inputs(tree,Path(a.project_root),source_inputs))
        except MigrationError as exc:
            write_json(Path(output)/(a.page+'.capture.json'),{'status':'error','page_id':a.page,
                       'error':str(exc),'previous_capture':result})
            raise
        write_json(Path(output)/(a.page+'.capture.json'),result)
    print(json.dumps(result,ensure_ascii=False)); return code


def functional_snapshot(page):
    values=[{'idx':i,'feature_path':c.get('feature_path'),'name':c.get('name',c.get('check_name')),
             'check_kind':c.get('check_kind') or 'functional'} for i,c in enumerate(page.get('functional_checks',[]))]
    return hashlib.sha256(json.dumps({'node':page['id'],'checks':values},sort_keys=True,ensure_ascii=False,
                                    separators=(',',':')).encode()).hexdigest()


def sweep_plans(page, action_plan):
    checks=page.get('functional_checks',[]);names=[c.get('name',c.get('check_name')) for c in checks]
    if any(not n for n in names):raise MigrationError('Functional checks need their original names')
    fingerprint=functional_snapshot(page);given=action_plan.get('functional_checks_sha256')
    if given is not None and given!=fingerprint:raise MigrationError('Sweep plan functional snapshot is stale')
    actions=action_plan.get('checks',{})
    if isinstance(actions,list):
        if given!=fingerprint:raise MigrationError('Indexed sweep plan needs the current functional_checks_sha256')
        plans={}
        for item in actions:
            if not isinstance(item,dict):raise MigrationError('Indexed sweep plan requires object entries')
            idx=item.get('check_idx')
            if type(idx) is not int or not 0<=idx<len(checks) or idx in plans:
                raise MigrationError('Invalid or duplicate page-local zero-based check_idx')
            check=checks[idx]
            if not item.get('feature_path') or item['feature_path']!=check.get('feature_path'):
                raise MigrationError('Sweep check_idx does not match its original feature_path')
            if item.get('check_name',names[idx])!=names[idx]:raise MigrationError('Sweep check name differs from its indexed check')
            plans[idx]=item
        return plans,fingerprint
    if not isinstance(actions,dict):raise MigrationError('Sweep checks must be an indexed list or legacy name dictionary')
    if set(actions)-set(names):raise MigrationError('Sweep action plan references checks outside the current source node')
    if any(not isinstance(item,dict) for item in actions.values()):raise MigrationError('Legacy sweep plans require object entries')
    for name in actions:
        if names.count(name)!=1:raise MigrationError('Ambiguous legacy sweep name; use check_idx and feature_path: '+name)
    return {i:actions[name] for i,name in enumerate(names) if name in actions},fingerprint


def sweep(session, tree, page_id, action_plan, output, *, project=None):
    """Batch already-selected public UI actions and retain every check's outcome.

    The existing LLM edge-walk chooses actions and recovery. This batch collector
    supplies raw evidence to its grounding/blackbox judgement; it never labels a
    feature PASS, auto-confirms destructive actions or erases unperformed checks.
    """
    source_inputs = collection_inputs(tree,project or Path.cwd())
    build_identity=observer_build(tree,session)
    if build_identity:source_inputs['source_app_build']=build_identity
    output = Path(output); output.mkdir(parents=True,exist_ok=True)
    collection = [p for key in ('pages','fragments','dialogs') for p in
                  (tree.get(key,{}).values() if isinstance(tree.get(key,[]),dict) else tree.get(key,[]))]
    pages = [p for p in collection if p['id'] == page_id]
    if len(pages) != 1: raise MigrationError('Sweep requires one real source page')
    page = pages[0]; identities = identities_from_tree(tree)
    if identities.get(page_id,{}).get('_native_identity_host_members'):
        raise MigrationError('Source activity_root tab host is capture-only; ground its tab controls through planned edges')
    actions,fingerprint=sweep_plans(page,action_plan)
    scope = identities.get(page_id,{}).get('scope','app')
    if scope not in {'app','springboard'}:
        raise MigrationError('Sweep scope must be app or springboard')
    for plan in actions.values():
        if 'after_scope' in plan and plan['after_scope'] not in {'app','springboard'}:
            raise MigrationError('Sweep after_scope must be app or springboard')
        for action in plan.get('actions',[]):
            arguments = action.get('arguments',{})
            if 'scope' in arguments and arguments['scope'] not in {'app','springboard'}:
                raise MigrationError('Sweep action scope must be app or springboard')
    def collect(directory, capture_scope=scope):
        # Preserve the public call contract for unchanged app-only consumers.
        return (session.capture(directory) if capture_scope == 'app'
                else session.capture(directory,scope=capture_scope))
    if tree.get('app',{}).get('package') != session.state['bundle_id']:
        raise MigrationError('Sweep source tree bundle does not match owned observer')
    before = collect(output/'before')
    initial = arrival(before['observation'],page_id,identities,
                      live_page_queries(session,before['observation'],identities))
    if not initial['arrived']: raise MigrationError('Sweep source identity is not arrived: '+json.dumps(initial))
    checks = page.get('functional_checks',[])
    inventory = []
    for index,n in enumerate(nodes(before['observation']['tree'])):
        if n.get('element_type') not in INTERACTIVE or not n.get('exists'): continue
        selector = {'element_type':n['element_type']}
        if n.get('identifier'): selector['identifier'] = n['identifier']
        elif n.get('label'): selector['label'] = n['label']
        inventory.append({'index':index,'selector':selector,'node':{k:v for k,v in n.items() if k!='children'},
                          'disposition':'unjudged','source':'actual-XCTest-inventory'})
    records = []; escaped = False
    for idx,check in enumerate(checks):
        name = check.get('name',check.get('check_name')); plan = actions.get(idx)
        record = {'idx':idx,'name':name,'check_idx':idx,'check_name':name,'node':page_id,
                  'feature_path':check.get('feature_path'),'functional_checks_sha256':fingerprint,
                  'expected_ios':check.get('expected_ios'),
                  'status':'not_found','before_capture':capture_ref(before),'actions':[],'judged':False}
        if escaped:
            record.update(status='deferred_outcome',reason='Prior action escaped source node; LLM recovery required')
        elif not plan:
            record['reason'] = 'No grounded locator/action was provided; retained in denominator'
        elif plan.get('disposition') in {'deferred_to_walk','settled_by_walk','deferred_outcome','input_field_no_tap','deferred_same_destination'}:
            record.update(status=plan['disposition'],reason=plan.get('reason'),walk_evidence=plan.get('walk_evidence'))
            if plan['disposition']=='deferred_same_destination':
                inherit=plan.get('inherit_from_edge')
                if (not isinstance(inherit,dict) or inherit.get('from')!=page_id
                        or not isinstance(inherit.get('to'),str) or not inherit['to']
                        or inherit.get('trigger') is not None and not isinstance(inherit['trigger'],str)):
                    raise MigrationError('Same-destination sweep needs its explicit original inherit_from_edge binding')
                record['inherit_from_edge']=dict(inherit)
        else:
            current=collect(output/('check-before-'+str(idx)))
            record['before_capture']=capture_ref(current)
            current_identity=arrival(current['observation'],page_id,identities,
                                     live_page_queries(session,current['observation'],identities))
            if not current_identity['arrived']:
                escaped=True;record.update(status='deferred_outcome',reason='Source position changed before this check',
                                          before_identity=current_identity)
            else:
                for action in plan.get('actions',[]):
                    source_inputs.update(collection_inputs(tree,project or Path.cwd(),source_inputs))
                    operation = action.get('operation')
                    if operation not in {'tap','type_text','swipe','long_press','openurl'}:
                        raise MigrationError('Sweep only batches explicit public UI actions')
                    if action.get('safety') != 'normal':
                        record.update(status='deferred_outcome',reason='Action was not classified normal by existing walk safety triage')
                        break
                    arguments = dict(action.get('arguments',{}))
                    if scope != 'app': arguments.setdefault('scope',scope)
                    response = session.command(operation,arguments)
                    record['actions'].append({'operation':operation,'arguments':arguments,'response':response})
                    if not response.get('ok'):
                        record.update(status='not_found',reason=response.get('error'));break
                else:
                    if record['actions']:
                        after = collect(output/('check-'+str(len(records))),plan.get('after_scope',scope))
                        record.update(status='ok',after_capture=capture_ref(after),
                                      after_identity=arrival(after['observation'],page_id,identities,
                                          live_page_queries(session,after['observation'],identities)))
                        escaped = not record['after_identity']['arrived']
        records.append(record)
        source_inputs.update(collection_inputs(tree,project or Path.cwd(),source_inputs))
        write_json(output/'run_meta.json',{**source_inputs,'source_platform':'ios','node':page_id,'source_sha256':tree.get('native_source_sha256'),
                  'checks':records,'functional_checks_sha256':fingerprint,'inventory':inventory,'raw_observations_only':True,
                  'needs_llm_judgement':True,'escaped':escaped})
    if not checks:
        source_inputs.update(collection_inputs(tree,project or Path.cwd(),source_inputs))
        write_json(output/'run_meta.json',{**source_inputs,'source_platform':'ios','node':page_id,'checks':[],
                   'functional_checks_sha256':fingerprint,
                   'inventory':inventory,'raw_observations_only':True,'needs_llm_judgement':True})
    return {**source_inputs,'run_meta':str(output/'run_meta.json'),'checks':len(checks),'records':len(records),
            'inventory':len(inventory),'judged':False,'escaped':escaped}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command',required=True)
    q = sub.add_parser('xml'); q.add_argument('--observation',required=True); q.add_argument('--out',required=True)
    q = sub.add_parser('arrival'); q.add_argument('--observation',required=True); q.add_argument('--identities',required=True); q.add_argument('--page',required=True); q.add_argument('--out',required=True)
    q.add_argument('--workspace',help='Owned live observer; without it output is diagnostic and cannot pass arrival')
    q = sub.add_parser('capture'); q.add_argument('args',nargs=argparse.REMAINDER)
    q = sub.add_parser('facts'); q.add_argument('--src',required=True); q.add_argument('--project-root')
    q.add_argument('--bundle',required=True); q.add_argument('--out',required=True); q.add_argument('--facts-out',required=True)
    q = sub.add_parser('build-source');q.add_argument('--src',required=True);q.add_argument('--project-root')
    q.add_argument('--xcode-project');q.add_argument('--scheme');q.add_argument('--out',required=True)
    q = sub.add_parser('sweep'); q.add_argument('--workspace',required=True);q.add_argument('--tree',required=True)
    q.add_argument('--page',required=True);q.add_argument('--actions',required=True);q.add_argument('--out',required=True)
    q.add_argument('--project-root',help='Source selection context; defaults to the fact-tree project')
    a = p.parse_args(argv)
    try:
        if a.command == 'capture': return capture_cli(a.args)
        if a.command == 'facts':
            from .source import Source
            tree, facts = fact_scaffold(Source(a.src,a.project_root),a.bundle)
            write_json(Path(a.out),tree); write_json(Path(a.facts_out),facts)
            print(json.dumps({'tree':a.out,'facts':a.facts_out,'enriched':False,'source_sha256':facts['source_sha']})); return 0
        if a.command == 'build-source':
            from .source import Source
            from .native_source_build import build
            value=build(Source(a.src,a.project_root),a.out,project_path=a.xcode_project,scheme=a.scheme)
            print(json.dumps({key:value[key] for key in ('app','bundle_id','exit_code','signing_mode','source_sha256','source_behavior_verified')}
                             | {'build_record':str(Path(a.out).resolve()/'build.json'),
                                'entitlement_validation':value['simulator_entitlements']['validation']},ensure_ascii=False));return 0
        if a.command == 'sweep':
            from .xcode_ui import XcodeUISession
            result=sweep(XcodeUISession.open(a.workspace),read_json(Path(a.tree)),a.page,read_json(Path(a.actions)),a.out,
                         project=a.project_root or Path(a.tree).resolve().parent.parent)
            print(json.dumps(result,ensure_ascii=False));return 0
        observation = read_json(Path(a.observation))
        if a.command == 'xml': atomic_write(Path(a.out),observation_xml(observation).encode()); return 0
        # Standalone annotation files carry signatures only. Host roles require
        # the fact tree's independently checked containment/tab declarations.
        identities={name:{k:v for k,v in contract.items() if not k.startswith('_native_identity_')}
                    for name,contract in read_json(Path(a.identities)).items()};live=None
        if a.workspace:
            from .xcode_ui import XcodeUISession
            session=XcodeUISession.open(a.workspace)
            if observation['session'] != session.state['session']:
                raise MigrationError('Observation does not belong to the live owned observer')
            live=live_page_queries(session,observation,identities)
        result = arrival(observation,a.page,identities,live)
        if not a.workspace:
            result.update(snapshot_match=result['arrived'],arrived=False,needs_live=True)
        write_json(Path(a.out),result);print(json.dumps(result,ensure_ascii=False));return 0 if result['verified'] else 15
    except (MigrationError,OSError,ValueError,RuntimeError) as exc:
        print(json.dumps({'status':'error','source_platform':'ios','error':str(exc)},ensure_ascii=False));return 2


if __name__ == '__main__': raise SystemExit(main())
