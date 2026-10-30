"""App-scoped cross-platform observations, not an SDK or a pixel-equivalence oracle.

Runtime ids never establish identity. Source anchors bind a reviewed migration
map to bytes; labels/geometry provide candidates, not invented source semantics.
"""
import math
from pathlib import Path, PurePosixPath
import re
import unicodedata

from .core import MigrationError, digest, json_bytes

MAP_SCHEMA = 'hmigbot-ui-controls-map/1'
# Values checked against Apple's XCUIElementTypes.h; names remain platform types.
APPLE_TYPES = {5:'sheet', 7:'alert', 8:'dialog', 9:'button', 19:'keyboard',
               21:'navigationbar', 22:'tabbar', 25:'statusbar', 33:'slider',
               40:'switch', 41:'switch', 42:'link', 43:'image', 45:'textfield',
               48:'text', 49:'textfield', 50:'securetextfield', 52:'textview'}
ALIASES = {'statictext':'text', 'label':'text', 'textinput':'textfield',
           'toggle':'switch', 'alertdialog':'dialog', 'navigation':'navigationbar',
           'tabs':'tabbar', 'tabcontent':'container', 'row':'container',
           'column':'container', 'stack':'container', 'rect':'container'}
SYSTEM_ROLES = {'statusbar', 'keyboard'}
CONTAINERS = {'container', 'window', 'application', 'other', 'scrollview', 'swiper',
              'navigationbar', 'tabbar', 'toolbar', 'group'}


def require(value, message):
    if not value:
        raise MigrationError(message)


def text(value):
    # Preserve punctuation, decimals, signs, case and language. Never translate
    # button labels or collapse "1.0" into "10" to manufacture a match.
    return ' '.join(unicodedata.normalize('NFC', str(value or '')).split())


def role(value):
    raw = str(value or '')
    match = re.fullmatch(r'XCUIElementType\(rawValue: (\d+)\)', raw)
    if match:
        return APPLE_TYPES.get(int(match[1]), 'other')
    raw = raw.removeprefix('XCUIElementType').replace('_', '').casefold()
    return ALIASES.get(raw, raw or 'unknown')


def frame(value):
    if not isinstance(value, dict):
        return None
    values = [value.get('x', value.get('left')), value.get('y', value.get('top')),
              value.get('width'), value.get('height')]
    if not all(type(v) in (int, float) and math.isfinite(v) for v in values):
        return None
    if values[2] <= 0 or values[3] <= 0:
        return None
    return dict(zip(('x', 'y', 'width', 'height'), values))


def nodes(document):
    result = []
    def visit(item, parent=None):
        if isinstance(item, list):
            for child in item:
                visit(child, parent)
        elif isinstance(item, dict):
            index = parent
            if 'type' in item:
                index = len(result)
                ident = item.get('identifier', item.get('accessibilityIdentifier', ''))
                result.append({**item, 'index': index, 'parent': item.get('parent_index', parent),
                               'identifier': ident if isinstance(ident, str) else '',
                               'role': role(item['type']), 'label': text(item.get('label')),
                               'frame': frame(item.get('frame', item.get('bounds')))})
            for key in ('nodes', 'elements', 'children'):
                if key in item:
                    visit(item[key], index)
    visit(document)
    for item in result:
        item['descendant_labels'] = []
    for item in result:
        parent, seen = item['parent'], set()
        while type(parent) is int and 0 <= parent < len(result) and parent not in seen:
            seen.add(parent)
            if item['label'] and item['label'] not in result[parent]['descendant_labels']:
                result[parent]['descendant_labels'].append(item['label'])
            parent = result[parent]['parent']
    for item in result:
        # Official native layouts sometimes expose only the generic Button tag
        # as its label; retain raw label and derive candidate text from actual
        # descendants. This is not a new accessibility identifier.
        generic = item['label'].casefold() == str(item.get('type','')).casefold()
        labels = item['descendant_labels']
        item['matching_text'] = labels[0] if generic and len(labels) == 1 else item['label']
        item['matching_text_origin'] = 'single_observed_descendant_label' if generic and len(labels)==1 else 'native_label'
    return result


def _path(root, value):
    require(isinstance(value, str), 'Mapping anchor needs a relative path')
    relative = PurePosixPath(value)
    require(value and value == relative.as_posix() and not relative.is_absolute()
            and '..' not in relative.parts and '\\' not in value and ':' not in value,
            'Unsafe UI mapping anchor path')
    current = Path(root).resolve()
    for part in relative.parts:
        current /= part
        require(not current.is_symlink(), 'UI mapping anchor cannot follow a symlink')
    require(current.is_file(), 'UI mapping anchor file missing: ' + value)
    return current


def _anchor(root, value, verify=False):
    require(isinstance(value, dict), 'UI mapping endpoint must be an object')
    path = _path(root, value.get('path'))
    line = value.get('line')
    lines = path.read_text(encoding='utf-8').splitlines()
    require(type(line) is int and 1 <= line <= len(lines), 'UI mapping line outside current source')
    selector = value.get('selector')
    require(isinstance(selector, dict) and not set(selector)-{'identifier','role','label','descendant_label'},
            'Mapping selector accepts identifier, role, exact label and descendant_label only')
    require((isinstance(selector.get('identifier'), str) and selector['identifier'])
            or (isinstance(selector.get('role'), str) and selector['role']
                and any(isinstance(selector.get(k),str) and text(selector[k]) for k in ('label','descendant_label'))),
            'Mapping endpoint needs an observed identifier or role+label selector')
    actual = {**value, 'sha256': digest(path.read_bytes()), 'quote': lines[line-1]}
    if verify:
        require(value.get('sha256') == actual['sha256'] and value.get('quote') == actual['quote'],
                'UI mapping source bytes/line changed: ' + value['path'])
    return actual


def bind_mapping(proposal, source_root, target_root):
    """Bind explicit per-control correspondence to current source/target bytes.

    This records the caller's mapping; it does not invent a correspondence from
    equal line numbers, mutate source code or certify a human review.
    """
    from .ui_validation_evidence import source_identity
    require(isinstance(proposal, dict) and isinstance(proposal.get('controls'), list)
            and proposal['controls'], 'Mapping proposal needs nonempty controls')
    controls, seen = [], set()
    for item in proposal['controls']:
        require(isinstance(item, dict) and isinstance(item.get('control_id'), str)
                and item['control_id'] and item['control_id'] not in seen,
                'Mapping control ids must be nonempty and unique')
        require(isinstance(item.get('checkpoint_id'), str) and item['checkpoint_id'],
                'Mapping must bind one explicit checkpoint')
        seen.add(item['control_id'])
        controls.append({**item, 'ios': _anchor(source_root, item.get('ios')),
                         'harmonyos': _anchor(target_root, item.get('harmonyos'))})
    result = {'schema_version': MAP_SCHEMA, 'authority': 'caller_supplied_migration_correspondence',
              'source_sha256': source_identity('ios', source_root),
              'target_sha256': source_identity('harmonyos', target_root), 'controls': controls}
    result['mapping_sha256'] = digest(json_bytes(result))
    return result


def validate_mapping(mapping, current):
    require(isinstance(mapping, dict) and mapping.get('schema_version') == MAP_SCHEMA,
            'Unsupported UI control mapping')
    require(mapping.get('mapping_sha256') == digest(json_bytes({k:v for k,v in mapping.items()
                                                               if k != 'mapping_sha256'})),
            'UI control mapping changed')
    # A change in an unrelated page need not invalidate every control mapping.
    # Actual capture/build freshness is checked by pair_evidence; the mapping's
    # own dependency is the exact source/target anchor files verified below.
    require(isinstance(mapping.get('controls'), list) and mapping['controls'], 'Empty UI control mapping')
    ids = []
    for item in mapping['controls']:
        require(isinstance(item, dict) and isinstance(item.get('control_id'), str)
                and item['control_id'] and isinstance(item.get('checkpoint_id'), str)
                and item['checkpoint_id'], 'Malformed UI control mapping record')
        ids.append(item['control_id'])
        for platform in ('ios', 'harmonyos'):
            _anchor(current[platform]['verification']['source_root'], item[platform], verify=True)
    require(len(ids) == len(set(ids)), 'Duplicate UI control mapping ids')
    return mapping


def _select(items, selector):
    return [n for n in items if all((n['identifier'] == value if key == 'identifier'
            else n['role'] == role(value) if key == 'role'
            else text(value) in n['descendant_labels'] if key == 'descendant_label'
            else n['label'] == text(value))
            for key,value in selector.items())]


def _normalized(n, viewport):
    f = n['frame']
    if not f or not viewport:
        return None
    return ((f['x']-viewport['x']+f['width']/2)/viewport['width'],
            (f['y']-viewport['y']+f['height']/2)/viewport['height'])


def match_controls(source, target, mapping=None, checkpoint_id=None, *, control_map=None):
    left, right = nodes(source), nodes(target)
    # A native system status bar/keyboard is explicitly distinguished from app
    # navigation/tab bars. App-owned chrome is never excluded by its name.
    def usable(n):
        return n['role'] not in SYSTEM_ROLES and (n['role'] not in CONTAINERS or n['identifier'])
    a, b = [n for n in left if usable(n)], [n for n in right if usable(n)]
    matches, unresolved, candidates, used_a, used_b = [], [], [], set(), set()
    if not a or not b:
        unresolved.append({'reason':'no_comparable_controls_on_one_or_both_sides'})
    if any(n.get('children_truncated') is True for n in left+right):
        unresolved.append({'reason':'accessible_hierarchy_truncated'})
    def commit(x, y, method, trusted):
        matches.append({'source':x['index'], 'target':y['index'], 'method':method,
                        'identity_established':trusted})
        used_a.add(x['index']); used_b.add(y['index'])
    for item in (mapping or {}).get('controls', []):
        if item['checkpoint_id'] != checkpoint_id:
            continue
        aa, bb = _select(a,item['ios']['selector']), _select(b,item['harmonyos']['selector'])
        if (len(aa) == len(bb) == 1 and aa[0]['index'] not in used_a and bb[0]['index'] not in used_b):
            commit(aa[0], bb[0], 'source_anchored_mapping', True)
            matches[-1]['control_id'] = item['control_id']
        else:
            unresolved.append({'control_id':item['control_id'], 'reason':'mapping_selector_missing_ambiguous_or_reused',
                               'source_candidates':[n['index'] for n in aa], 'target_candidates':[n['index'] for n in bb]})
    # Exact semantic ids must be unique on both sides, including already consumed nodes.
    for x in a:
        if x['index'] in used_a or not x['identifier']:
            continue
        wanted = (control_map or {}).get(x['identifier'], x['identifier'])
        aa = [n for n in a if n['identifier'] == x['identifier']]
        bb = [n for n in b if n['identifier'] == wanted]
        if len(aa) == len(bb) == 1 and bb[0]['index'] not in used_b:
            commit(x, bb[0], 'semantic_identifier', True)
    # Text/type is useful for correspondence, but remains inferred identity.
    for x in a:
        if x['index'] in used_a or not x['matching_text'] or x['role'] in {'other','unknown'}:
            continue
        aa = [n for n in a if (n['role'], n['matching_text']) == (x['role'], x['matching_text'])]
        bb = [n for n in b if (n['role'], n['matching_text']) == (x['role'], x['matching_text'])]
        if len(aa) == len(bb) == 1 and bb[0]['index'] not in used_b:
            commit(x, bb[0], 'unique_text_and_type', False)
        elif bb:
            candidates.append({'source':x['index'], 'targets':[n['index'] for n in bb],
                               'method':'text_and_type', 'reason':'ambiguous_or_already_consumed'})
    av = next((n['frame'] for n in left if n['frame']), None)
    bv = next((n['frame'] for n in right if n['frame']), None)
    # Positions are normalized independently (iOS points vs target pixels).
    # Nearby geometry is a hint only, even when there is exactly one candidate.
    for x in a:
        if x['index'] in used_a:
            continue
        point = _normalized(x,av)
        nearby = []
        if point and x['role'] not in {'other','unknown'}:
            for y in b:
                other = _normalized(y,bv)
                if y['index'] not in used_b and y['role'] == x['role'] and other:
                    distance = math.dist(point,other)
                    if distance <= 0.04:
                        nearby.append({'target':y['index'], 'distance':distance})
        if nearby:
            candidates.append({'source':x['index'], 'method':'normalized_position_and_type',
                               'targets':sorted(nearby,key=lambda n:n['distance']), 'identity_established':False})
        unresolved.append({'source':x['index'], 'reason':'no_unambiguous_correspondence',
                           'identifier':x['identifier'], 'role':x['role'], 'label':x['label']})
    return {'matches':matches, 'candidates':candidates, 'unresolved':unresolved,
            'unmatched_target':[n['index'] for n in b if n['index'] not in used_b],
            'source_nodes':left, 'target_nodes':right,
            'viewports':{'ios':av,'harmonyos':bv},
            'counts':{'source_controls':len(a),'target_controls':len(b), 'matched':len(matches),
                      'identity_established':sum(m['identity_established'] for m in matches)},
            'system_nodes_excluded':{'ios':[n['index'] for n in left if n['role'] in SYSTEM_ROLES],
                                     'harmonyos':[n['index'] for n in right if n['role'] in SYSTEM_ROLES]},
            'limitations':['Exposed accessible controls only; unmatched is not proof of a missing implementation',
                           'Text/type and position do not establish source identity or business equivalence']}


def assess_controls(matching, configuration, fields=None, exceptions=None):
    """Classify actual observed fields; never give 100% to missing evidence."""
    fields = ['label','value','enabled'] if fields is None else fields
    require(isinstance(fields,list) and fields and len(fields)==len(set(fields))
            and set(fields)<={'label','value','enabled','selected'}, 'Invalid cross-platform compare fields')
    differences, unknown = [], list(matching['unresolved'])
    left, right = matching['source_nodes'], matching['target_nodes']
    for match in matching['matches']:
        x, y = left[match['source']], right[match['target']]
        if not match['identity_established']:
            unknown.append({'source':x['index'],'target':y['index'],'reason':'inferred_correspondence_needs_confirmation'})
        for field in fields:
            av,bv = x.get(field), y.get(field)
            if av is None or bv is None:
                unknown.append({'source':x['index'],'target':y['index'],'field':field,'reason':'field_not_exposed'})
            elif av != bv:
                differences.append({'source':x['index'],'target':y['index'],'field':field,
                    'category':'content_mismatch' if field in {'label','value'} else 'state_mismatch',
                    'severity':'high', 'disposition':'needs_fix' if match['identity_established'] else 'needs_confirmation',
                    'expected':av,'actual':bv, 'match_method':match['method']})
        if x['role'] != y['role']:
            differences.append({'source':x['index'],'target':y['index'],'category':'control_type_mismatch',
                                'severity':'high','disposition':'needs_fix','expected':x['role'],'actual':y['role']})
        if match['identity_established']:
            ap = _normalized(x,matching['viewports']['ios'])
            bp = _normalized(y,matching['viewports']['harmonyos'])
            if ap is not None and bp is not None and math.dist(ap,bp) > 0.04:
                offset = math.dist(ap,bp)
                differences.append({'source':x['index'],'target':y['index'],'category':'layout_mismatch',
                    'severity':'high' if offset > 0.12 else 'medium',
                    'disposition':'needs_fix' if configuration.get('application_configuration_comparable') else 'needs_confirmation',
                    'normalized_center_distance':offset,'scope':'relative viewport positions; not raw pixel tolerance'})
    dialogs_a = [n for n in left if n['role'] in {'alert','dialog','sheet'}]
    dialogs_b = [n for n in right if n['role'] in {'alert','dialog','sheet'}]
    if bool(dialogs_a) != bool(dialogs_b):
        differences.append({'category':'application_state_difference','severity':'high','disposition':'needs_fix',
                            'reason':'dialog_or_sheet_present_on_only_one_side',
                            'source_nodes':[n['index'] for n in dialogs_a], 'target_nodes':[n['index'] for n in dialogs_b],
                            'cause':'not_diagnosed; no automatic dismissal or system exemption'})
    if matching['unmatched_target']:
        unknown.append({'reason':'additional_unmapped_target_controls','target_nodes':matching['unmatched_target']})
    for gap in configuration.get('gaps',[]):
        unknown.append({'reason':'configuration_context_gap','detail':gap})
    # Actual known differences are reported; config mismatch never authorizes a
    # blanket exemption for content, missing buttons or app error dialogs.
    for difference in configuration.get('differences',[]):
        differences.append({'category':'config_difference','severity':'low', 'disposition':'needs_confirmation',
                            **difference})
    for index,difference in enumerate(differences):
        difference['id'] = 'UI-D'+str(index+1).zfill(4)
        difference['observation_sha256'] = digest(json_bytes(difference))
    # Exceptions are reviewed per-observation decisions, never a label inferred
    # from appearance. An app alert or missing control cannot be waived here.
    for exception in exceptions or []:
        require(isinstance(exception,dict) and set(exception) == {'difference_id','observation_sha256','category','reason','evidence'},
                'Exception needs difference_id, category, reason and bound evidence')
        require(exception['category'] in {'dynamic_content','design_difference','config_difference'},
                'Unsupported UI difference exception category')
        require(isinstance(exception['reason'],str) and exception['reason'].strip(), 'Exception reason missing')
        found = [d for d in differences if d['id'] == exception['difference_id']]
        require(len(found) == 1,'Exception must reference a difference in this comparison')
        difference = found[0]
        require(exception['observation_sha256'] == difference['observation_sha256'],
                'UI exception belongs to a different observed difference')
        require(difference['category'] in {'content_mismatch','layout_mismatch','config_difference'},
                'Application state/control/state errors cannot be excluded by this rule')
        if exception['category'] == 'config_difference':
            require(bool(configuration.get('differences')), 'Configuration exemption requires an actually observed difference')
        evidence = exception['evidence']
        require(isinstance(evidence,dict) and evidence.get('validated_for_current_comparison') is True,
                'UI exception evidence has not been bound to current artifacts/source')
        difference.update(category=exception['category'],disposition='excluded',
                          exclusion_reason=exception['reason'],exclusion_evidence=evidence)
    score = max(0.0,round(1-sum({'high':0.05,'medium':0.02,'low':0.01}[d['severity']]
                               for d in differences if d['disposition'] != 'excluded'),6))
    complete = not unknown and configuration.get('application_configuration_comparable') is True
    blockers = [d for d in differences if d['disposition'] != 'excluded']
    return {'status':'differences_observed' if differences else 'incomplete' if not complete else 'equal_control_observations',
            'differences':differences,'unknown':unknown,'evidence_complete':complete,
            'rubric_score':score if complete else None, 'provisional_rubric_score':score,
            'score_policy':'HMigBot local difference rubric: high -0.05, medium -0.02, low -0.01; not image similarity',
            'aligned_observations':complete and not blockers,
            'automatic_page_closure':False, 'application_acceptance':'not_established',
            'closure_blockers':(['incomplete_control_or_configuration_evidence'] if not complete else [])
                               +(['unresolved_differences'] if blockers else [])
                               +['full_visual_and_business_acceptance_not_proven_by_control_observations']}


def include_visual_observations(assessment, observations):
    """Consume a separately attributed, capture-bound visual review.

    The offline matcher does not pretend to detect pixels, dialogs or colours
    that the native hierarchy did not expose. Review never grants acceptance.
    """
    for item in observations:
        require(item.get('category') in {'application_error_dialog','layout_mismatch','content_mismatch',
                                        'control_missing','color_mismatch'}, 'Unsupported visual observation category')
        require(item.get('severity') in {'high','medium','low'} and isinstance(item.get('reason'),str)
                and item['reason'].strip(), 'Visual observation needs severity and a concrete reason')
        difference={**item,'disposition':'needs_fix','origin':'capture_bound_visual_review'}
        difference['id']='UI-V'+str(len([d for d in assessment['differences'] if d.get('origin')=='capture_bound_visual_review'])+1).zfill(4)
        difference['observation_sha256']=digest(json_bytes(difference))
        assessment['differences'].append(difference)
    if observations:
        score=max(0.0,round(1-sum({'high':.05,'medium':.02,'low':.01}[d['severity']]
                    for d in assessment['differences'] if d['disposition']!='excluded'),6))
        assessment.update(status='differences_observed',aligned_observations=False,
                          provisional_rubric_score=score,
                          rubric_score=score if assessment['evidence_complete'] else None)
        if 'unresolved_differences' not in assessment['closure_blockers']:
            assessment['closure_blockers'].append('unresolved_differences')
    return assessment
