"""Shared responsibility contract: synthetic evidence unit tests, no runtime proof."""
import copy
import importlib.util
import json
import re
from pathlib import Path
import tempfile
from unittest.mock import patch

import pytest
from hmigbot_ios.core import MigrationError, digest, json_bytes, snapshot, write_json
from hmigbot_ios.ios_facts import extract, obligations

ROOT = Path(__file__).resolve().parents[1]


def api():
    assert importlib.util.find_spec('hmigbot_ios.source_responsibility') is not None, 'Shared responsibility validator is not implemented'
    from hmigbot_ios import source_responsibility
    return source_responsibility


@pytest.fixture
def case(tmp_path):
    source, project = tmp_path / 'source', tmp_path / 'project'
    source.mkdir(); project.mkdir()
    (source / 'App.m').write_text('@implementation App\n- (void)open { self.count = 1; [Private open]; }\n@end\n')
    (source / 'Private.m').write_text('@implementation Private\n- (void)open { self.count = 2; }\n@end\n')
    graph = extract(source); obs = obligations(graph)
    feature = (ROOT / 'tests/fixtures' / '_unused')
    text = '''---
source_anchors:
  - path: App.m
  - path: Private.m
---
# F001
## 数据流
替代路径（PD-X）：私有SDK→系统窗口；supersedes [F001-AC01]，emits [F001-AC02]。
## 实现映射
| 源机制 | 目标实现 | 数据/生命周期契约及依据 | 迁移分类 | 决策 |
|---|---|---|---|---|
| private | Preview.open | 系统窗口替代 | HARD-DIV | PD-X; supersedes: [F001-AC01]; emits: [F001-AC02] |
## 验收标准
- [ ] F001-AC01 原私有实现。 `源:Private.open → 标:Reader.open` `判:contract | 源调用` `真:src:Private.m:2` 〔superseded by PD-X〕
- [ ] F001-AC02 由系统窗口打开，失败可重试。 `决:PD-X → 标:Preview.open` `判:device | 实际窗口` `真:decision:PD-X`
## 动作
'''
    for ident, target, ac in [('F001-A01', 'Reader.open', 'F001-AC01'), ('F001-A02', 'Preview.open', 'F001-AC02')]:
        action = {'action_id': ident, 'owner':'F001', 'target':target,
                  'source_anchors':[{'role':'handler','path':'Private.m','line':2,'symbol':'open'}],
                  'immediate_effect':'request','completion_event':'return','final_effect':'visible',
                  'failure_cancel':'error','scope':'active','ac_ids':[ac]}
        text += '\n```action-contract\n' + json.dumps(action) + '\n```\n'
    path = project / 'spec/baseline/features/F001-private.md'
    path.parent.mkdir(parents=True); path.write_text(text)
    ledger = project / 'spec/decision-ledger.md'
    ledger.write_text('# Decisions\n## PD-X Local preview\n- status：approved。\n- 授权：用户明确授权本地系统窗口替代私有SDK。\n- 作用域：仅私有SDK；应用文件流程保持。\n')
    (project / 'spec/baseline/skip-list.md').write_text('# Scope\n## Private boundary\nPrivate.m open retains original source obligations and history.\n')
    write_json(project / 'spec/baseline/ios-facts.json', graph)
    write_json(project / 'spec/baseline/ios-obligations.json', obs)
    private = [o['id'] for o in obs['obligations'] if next(f for f in graph['facts'] if f['id']==o['fact_id'])['anchor']['path']=='Private.m']
    facts = {f['id']: f for f in graph['facts']}
    review = {'schema_version':1,'mode':'independent_source_review','source_sha256':graph['source_sha256'],
              'graph_sha256':digest(json_bytes(graph)), 'reviewer':'source-reader','independent_reviewer':'independent-reader',
              'input':'App open is the user boundary', 'processing':'Private implementation is called only via documented interface',
              'observable':'System window replaces private rendering',
              'file_roles':[{'path':p,'source_sha256':digest((source/p).read_bytes()),'role':role,'package':pkg}
                            for p,role,pkg in [('App.m','application','Demo'),('Private.m','dependency','PrivateSDK')]],
              'routes':[{'fact_id':f['id'],'resolution':'product_entry' if f['anchor']['path']=='App.m' else 'dependency_boundary',
                         'boundary_ids':[] if f['anchor']['path']=='App.m' else ['B-private'],
                         'evidence':[f['anchor']]} for f in graph['facts']], 'unresolved':[]}
    reviewpath = project / 'spec/ref/responsibility-review.json'; write_json(reviewpath, review)
    members = ['App.m','Private.m']
    expected = {'project':'Demo.xcodeproj','scheme':'Demo','target':'Demo','configuration':'Debug','sdk':'iphoneos','architecture':'arm64'}
    context = {'expected_build':expected,'build_evidence':'spec/ref/build','conditional_evidence':'spec/ref/ios-conditional-evidence/capture'}
    write_json(project / 'spec/ref/build/manifest.json', {'fixture':'synthetic'})
    write_json(project / 'spec/ref/ios-conditional-evidence/capture/manifest.json', {'fixture':'synthetic'})
    payload = {'schema_version':1,'source_platform':'ios','source_sha256':graph['source_sha256'],'graph_sha256':digest(json_bytes(graph)),
               'product_context':context,'review':{'path':'spec/ref/responsibility-review.json','sha256':digest(reviewpath.read_bytes())},
               'boundaries':[{'id':'B-private','kind':'dependency_internal',
                   'sources':[{'path':'Private.m','line':1,'end_line':3,'symbol':'Private','source_sha256':digest((source/'Private.m').read_bytes())}],
                   'obligation_ids':private, 'public_contracts':[{'caller_fact_ids':[f['id'] for f in graph['facts'] if f['anchor']['path']=='App.m'],
                   'ac_ids':['F001-AC02'],'callee_symbol':'Private.open'}], 'skip_ref':'spec/baseline/skip-list.md#Private boundary'}],
               'replacements':[]}
    # Shared unit fixture stubs only the upstream compiler replay. Dedicated upstream
    # conditional/build suites exercise those validators with real/synthetic captures.
    patches = [patch('hmigbot_ios.conditional_evidence._build', return_value={'members':members,'expected_build':copy.deepcopy(expected)}),
               patch('hmigbot_ios.conditional_evidence.validate', return_value={'members':members,'expected_build':copy.deepcopy(expected)}),
               patch('hmigbot_ios.conditional_evidence.frozen_inputs', return_value={'spec/ref/build/manifest.json':digest((project/'spec/ref/build/manifest.json').read_bytes())})]
    for p in patches: p.start()
    yield {'source':source,'project':project,'graph':graph,'obs':obs,'payload':payload,'review':review,'private':private,'patches':patches}
    for p in reversed(patches): p.stop()


def load(c, **kwargs):
    return api().load_and_validate(c['project'], c['source'], c['graph'], c['obs'], candidate=c['payload'], **kwargs)


def reseal_review(c):
    path = c['project'] / c['payload']['review']['path']
    write_json(path, c['review']); c['payload']['review']['sha256'] = digest(path.read_bytes())


def replacement(c):
    c['payload']['boundaries'][0]['kind'] = 'replaced_source_history'
    # Use the ownership dimension so both application and private facts must be
    # accounted for; private unknown stays unknown, application typed facts survive.
    privatefacts = [f for f in c['graph']['facts'] if f['anchor']['path']=='Private.m' and f['kind']=='write']
    appfacts = [f for f in c['graph']['facts'] if f['anchor']['path']=='App.m' and f['kind']=='write']
    claim = {'status':'unknown','reason':'Private SDK implementation unavailable',
             'parts':[{'id':'private','status':'unknown','reason':'Private SDK implementation unavailable',
                       'fact_ids':[f['id'] for f in privatefacts]},
                      {'id':'app','status':'known','value':{'assignments':'App sets count to one'},
                       'fact_ids':[f['id'] for f in appfacts],
                       'evidence':[{'path':f['anchor']['path'],'line':f['anchor']['line']} for f in appfacts]}]}
    semantics = {'schema_version':2,'source_platform':'ios','documents':[{'id':'F001','kind':'feature','facts':{'state_transitions':claim}}]}
    c['payload']['replacements'] = [{'id':'R-private','decision_id':'PD-X','decision_ref':'spec/decision-ledger.md#PD-X Local preview',
                 'decision_sha256':digest((c['project']/'spec/decision-ledger.md').read_bytes()),
                 'boundary_ids':['B-private'],'superseded_ac_ids':['F001-AC01'],'replacement_ac_ids':['F001-AC02'],
                 'historical_action_ids':['F001-A01'],'target_action_ids':['F001-A02'],
                 'semantic_parts':[{'document_id':'F001','dimension':'state_transitions','claim_sha256':digest(json_bytes(claim)),
                                    'private_part_ids':['private'],'retained_part_ids':['app'],'retained_app_ac_ids':['F001-AC02']}]}]
    return semantics, claim


def test_p01_exact_projection_keeps_all_denominators(case):
    result = load(case)
    assert set(result.all_obligation_ids) == {o['id'] for o in case['obs']['obligations']}
    assert set(result.historical_obligation_ids) == set(case['private'])
    assert len(result.product_obligation_ids)+len(result.historical_obligation_ids)==len(result.all_obligation_ids)
    assert result.counts['dependency_internal']==len(case['private'])
    assert result.behavior_verified is False


def test_p02_private_unknown_remains_unknown_and_app_contract_survives(case):
    semantics, claim = replacement(case); before=copy.deepcopy(semantics)
    projection = load(case, semantics=semantics)
    treatment = projection.semantic_requirement('F001','state_transitions',claim)
    assert treatment['target_required'] is False
    assert treatment['source_status']=='unknown'
    assert treatment['retained_parts'][0]['id']=='app'
    assert treatment['requires_ordinary_validation'] is True
    assert semantics==before
    assert set(projection.acceptance['active_target'])=={'F001-AC02'}
    assert set(projection.acceptance['source_history'])=={'F001-AC01'}


@pytest.mark.parametrize('mutation', ['source','graph','build','path_glob','path_directory','path_escape','span','file_hash','unknown_id','duplicate_id','overlap','app_dependency','unresolved','pending_review','same_reviewer'])
def test_n01_to_n07_invalid_boundary_fails_closed(case, mutation):
    b=case['payload']['boundaries'][0]
    if mutation=='source': (case['source']/'App.m').write_text('// changed\n')
    elif mutation=='graph': case['payload']['graph_sha256']='0'*64
    elif mutation=='build': case['payload']['product_context']['expected_build']['sdk']='iphonesimulator'
    elif mutation=='path_glob': b['sources'][0]['path']='*.m'
    elif mutation=='path_directory': b['sources'][0]['path']='.'
    elif mutation=='path_escape': b['sources'][0]['path']='../Private.m'
    elif mutation=='span': b['sources'][0]['line']=3
    elif mutation=='file_hash': b['sources'][0]['source_sha256']=case['graph']['source_sha256']
    elif mutation=='unknown_id': b['obligation_ids'].append('IO-fake')
    elif mutation=='duplicate_id': b['obligation_ids']*=2
    elif mutation=='overlap': case['payload']['boundaries'].append({**copy.deepcopy(b),'id':'B-other'})
    elif mutation=='app_dependency': b['sources'].append({'path':'App.m','line':1,'end_line':3,'symbol':'App','source_sha256':digest((case['source']/'App.m').read_bytes())})
    elif mutation=='unresolved': case['review']['unresolved']=['performSelector: unresolved']; reseal_review(case)
    elif mutation=='pending_review': case['review']['mode']='generated_pending'; reseal_review(case)
    elif mutation=='same_reviewer': case['review']['independent_reviewer']=case['review']['reviewer']; reseal_review(case)
    with pytest.raises(MigrationError): load(case)


def test_n03_symlink_is_not_regular_source(case):
    original=case['source']/'Private.m'; original.unlink(); original.symlink_to(case['source']/'App.m')
    with pytest.raises(MigrationError): load(case)


def test_n05_old_file_disposition_never_excludes(case):
    write_json(case['project']/'spec/baseline/ios-source-disposition.json', {'files':[{'path':'Private.m','disposition':'dependency'}]})
    result=api().load_and_validate(case['project'],case['source'],case['graph'],case['obs'])
    assert result.all_obligation_ids==result.product_obligation_ids
    assert result.historical_obligation_ids==()


def test_n06_internal_cannot_be_bound_to_unrelated_or_inactive_ac(case):
    case['payload']['boundaries'][0]['public_contracts'][0]['ac_ids']=['F001-AC01']
    with pytest.raises(MigrationError): load(case)


def test_n07_unused_symbol_with_product_route_rejected(case):
    case['payload']['boundaries'][0]['kind']='unused_symbol'
    with pytest.raises(MigrationError): load(case)


@pytest.mark.parametrize('mutation',['unapproved','decision_id','decision_hash','inactive_target','dangling_source','cross_decision','missing_emits','app_private','mixed_unknown','source_known','claim_drift','wrong_action'])
def test_n08_to_n13_invalid_replacement_rejected(case, mutation):
    sem, claim=replacement(case); r=case['payload']['replacements'][0]
    if mutation=='unapproved':
        p=case['project']/'spec/decision-ledger.md'; p.write_text(p.read_text().replace('approved','proposed')); r['decision_sha256']=digest(p.read_bytes())
    elif mutation=='decision_id': r['decision_id']='PD-Y'
    elif mutation=='decision_hash': r['decision_sha256']='0'*64
    elif mutation=='inactive_target': r['replacement_ac_ids']=['F001-AC01']
    elif mutation=='dangling_source': r['superseded_ac_ids']=['F001-AC99']
    elif mutation=='cross_decision':
        p=case['project']/'spec/baseline/features/F001-private.md'; p.write_text(p.read_text().replace('`决:PD-X','`决:PD-Y'))
    elif mutation=='missing_emits': r['replacement_ac_ids']=[]
    elif mutation=='app_private':
        claim['parts'][0]['fact_ids']+=claim['parts'][1]['fact_ids']; claim['parts'][1]['fact_ids']=[]; r['semantic_parts'][0]['claim_sha256']=digest(json_bytes(claim))
    elif mutation=='mixed_unknown':
        claim['parts'][1]['status']='unknown'; claim['parts'][1]['reason']='observer unresolved'; r['semantic_parts'][0]['claim_sha256']=digest(json_bytes(claim))
    elif mutation=='source_known': claim['status']='known'; r['semantic_parts'][0]['claim_sha256']=digest(json_bytes(claim))
    elif mutation=='claim_drift': claim['reason']='changed private description'
    elif mutation=='wrong_action': r['target_action_ids']=['F001-A01']
    with pytest.raises(MigrationError): load(case,semantics=sem)


def test_n09_edited_requirements_index_is_ignored(case):
    write_json(case['project']/'spec/.a2h/requirements-index.json', {'requirements':[{'requirement_id':'F001-AC01','status':'active'}]})
    result=load(case)
    assert set(result.acceptance['active_target'])=={'F001-AC02'}


def test_n14_frozen_inputs_detect_review_and_decision_drift(case):
    result=load(case)
    assert 'spec/ref/responsibility-review.json' in result.frozen_inputs()
    (case['project']/'spec/decision-ledger.md').write_text('# changed\n')
    with pytest.raises(MigrationError): result.validate_frozen_inputs(case['project'])


def test_n15_missing_active_ac_and_product_obligation_cannot_be_owned_by_history(case):
    result=load(case)
    with pytest.raises(MigrationError): result.validate_target_ownership([],case['private'])
    result.validate_target_ownership(['F001-AC02'],list(result.product_obligation_ids))


def test_n16_candidate_and_persisted_have_identical_treatment(case):
    candidate=load(case)
    write_json(case['project']/'spec/baseline/ios-responsibility.json',case['payload'])
    persisted=api().load_and_validate(case['project'],case['source'],case['graph'],case['obs'])
    assert candidate.counts==persisted.counts
    assert candidate.product_obligation_ids==persisted.product_obligation_ids


def test_n17_no_payload_preserves_all_strict_unknowns(case):
    result=api().load_and_validate(case['project'],case['source'],case['graph'],case['obs'])
    assert result.all_obligation_ids==result.product_obligation_ids
    claim={'status':'unknown','reason':'not reviewed'}
    assert result.semantic_requirement('F001','lifetime',claim)['target_required'] is True


def test_n18_variant_counts_are_exact_no_runtime_claim(case):
    result=load(case)
    assert result.variant==case['graph']['variant']
    assert result.counts['all']==len(case['obs']['obligations'])
    assert result.counts['product']+result.counts['historical']==result.counts['all']
    assert result.behavior_verified is False


def test_public_boundary_rejects_selector_with_no_actual_caller_tokens(case):
    case['payload']['boundaries'][0]['public_contracts'][0]['callee_symbol']='Private.notCalled'
    with pytest.raises(MigrationError): load(case)


def test_unused_cannot_use_review_text_as_complete_program_proof(case):
    case['payload']['boundaries'][0]['kind']='unused_symbol'
    case['payload']['boundaries'][0]['public_contracts']=[]
    for route in case['review']['routes']:
        if route['boundary_ids']: route['resolution']='no_entry'
    reseal_review(case)
    with pytest.raises(MigrationError): load(case)


def test_private_header_declaration_can_ground_unknown_dimension_without_invented_signal(case):
    sem, claim=replacement(case)
    # Header/type ownership can ground a private composition unknown even when
    # lexical extraction has no composition fact; this is never a known claim.
    claim['parts']=claim['parts'][:1]
    sem['documents'][0]['facts']={'layout':claim}
    treatment=case['payload']['replacements'][0]['semantic_parts'][0]
    treatment.update(dimension='layout',retained_part_ids=[],claim_sha256=digest(json_bytes(claim)))
    result=load(case,semantics=sem)
    assert result.semantic_requirement('F001','layout',claim)['source_status']=='unknown'


def test_known_source_claim_is_still_target_required_without_projection(case):
    result=api().load_and_validate(case['project'],case['source'],case['graph'],case['obs'])
    assert result.semantic_requirement('F001','events',{'status':'known','value':{'handler':'open'}})['target_required'] is True


def test_public_boundary_needs_call_not_same_named_method_declaration(case):
    path=case['source']/'App.m'; path.write_text(path.read_text().replace(' [Private open];',''))
    graph=extract(case['source']); obs=obligations(graph)
    case['graph'],case['obs']=graph,obs
    for item in (case['payload'],case['review']):
        item['source_sha256']=graph['source_sha256']; item['graph_sha256']=digest(json_bytes(graph))
    for row in case['review']['file_roles']:
        row['source_sha256']=digest((case['source']/row['path']).read_bytes())
    case['review']['routes']=[{'fact_id':f['id'],'resolution':'product_entry' if f['anchor']['path']=='App.m' else 'dependency_boundary',
                               'boundary_ids':[] if f['anchor']['path']=='App.m' else ['B-private'],'evidence':[f['anchor']]} for f in graph['facts']]
    case['payload']['boundaries'][0]['public_contracts'][0]['caller_fact_ids']=[f['id'] for f in graph['facts'] if f['anchor']['path']=='App.m']
    write_json(case['project']/'spec/baseline/ios-facts.json',graph); write_json(case['project']/'spec/baseline/ios-obligations.json',obs)
    reseal_review(case)
    with pytest.raises(MigrationError): load(case)


# Public Demo excerpts retain OFDDemo's multiline SDK call/callback and rotation
# structure. No confidential SDK implementation or compiler/runtime result is used.
OFD_DEMO_APP = '''@interface SWTestDetailsController ()
@property (nonatomic, strong) SWOFDView *ofdView;
@end
@implementation SWTestDetailsController
- (void)viewDidLoad {
    [self createTestView];
    [self.ofdView swOpenDoc:self.filePath
                  DocTyep:_fileType
               LayoutMode:OFD_LAYOUT_MODE_SERIES
              DefaultPage:1 EnabledScale:YES completion:^(SWErrCode code) {
        if (code == SWErrSuccess) {
            [SWHUDUtil hideHudAtWindow];
        } else {
            [SWHUDUtil ViewWithTitle:@"文档被删除或文档损坏"];
        }
    }];
}
-(void)viewWillTransitionToSize:(CGSize)size withTransitionCoordinator:(id)coordinator
{
    [self.ofdView swOfdViewTransition];
    [coordinator animateAlongsideTransition:^(id context) {
        [self.ofdView swOfdViewWillTransitionToSize:self.ofdView.frame.size];
    } completion:^(id context) { }];
}
-(void)unrelatedPersistence {
    self.savedPath = @"unchanged app responsibility";
}
@end
'''


def ofd_case(c):
    (c['source']/'App.m').write_text(OFD_DEMO_APP)
    (c['source']/'Private.m').write_text('@interface SWOFDView : NSObject\n@property(nonatomic,strong) id delegate;\n- (void)open;\n@end\n')
    feature=c['project']/'spec/baseline/features/F001-private.md'
    text=feature.read_text().replace('源:Private.open','源:SWOFDView.open').replace('真:src:Private.m:2','真:src:Private.m:3')
    first=text.index('```action-contract'); end=text.index('```',first+3)
    action=json.loads(text[first+len('```action-contract'):end]); action['source_anchors'][0]['line']=3
    feature.write_text(text[:first]+'```action-contract\n'+json.dumps(action)+'\n'+text[end:])
    graph=extract(c['source']); obs=obligations(graph)
    c['graph'],c['obs']=graph,obs
    for item in (c['payload'],c['review']):
        item['source_sha256']=graph['source_sha256']; item['graph_sha256']=digest(json_bytes(graph))
    for row in c['review']['file_roles']:
        row['source_sha256']=digest((c['source']/row['path']).read_bytes())
    c['review']['routes']=[{'fact_id':f['id'],'resolution':'product_entry' if f['anchor']['path']=='App.m' else 'dependency_boundary',
                            'boundary_ids':[] if f['anchor']['path']=='App.m' else ['B-private'],'evidence':[f['anchor']]} for f in graph['facts']]
    privatefacts=[f for f in graph['facts'] if f['anchor']['path']=='Private.m']
    privateids=[o['id'] for o in obs['obligations'] if o['fact_id'] in {f['id'] for f in privatefacts}]
    span={'path':'Private.m','line':1,'end_line':4,'symbol':'SWOFDView','source_sha256':digest((c['source']/'Private.m').read_bytes())}
    boundary=c['payload']['boundaries'][0]; boundary['sources']=[span]; boundary['obligation_ids']=privateids
    branch=next(f for f in graph['facts'] if f['kind']=='branch' and f['anchor']['path']=='App.m')
    boundary['public_contracts']=[{'caller_fact_ids':[branch['id']],'ac_ids':['F001-AC02'],
                                 'callee_symbol':'SWOFDView.swOpenDoc:DocTyep:LayoutMode:DefaultPage:EnabledScale:completion:',
                                 'caller_sources':[{'path':'App.m','line':7,'end_line':16,'symbol':'swOpenDoc','source_sha256':digest((c['source']/'App.m').read_bytes())}]}]
    c['private']=privateids
    skip=c['project']/'spec/baseline/skip-list.md'; skip.write_text(skip.read_text().replace('Private.m open','Private.m SWOFDView'))
    write_json(c['project']/'spec/baseline/ios-facts.json',graph); write_json(c['project']/'spec/baseline/ios-obligations.json',obs)
    reseal_review(c)
    return c


def app_replacement(c):
    ofd_case(c)
    path=c['project']/'spec/baseline/features/F001-private.md'
    text=path.read_text().replace('源:SWOFDView.open','源:SWTestDetailsController.viewWillTransitionToSize:withTransitionCoordinator:').replace('真:src:Private.m:3','真:src:App.m:18')
    first=text.index('```action-contract'); end=text.index('```',first+3)
    action=json.loads(text[first+len('```action-contract'):end])
    action['source_anchors']=[{'role':'handler','path':'App.m','line':18,'symbol':'viewWillTransitionToSize:withTransitionCoordinator:'}]
    text=text[:first]+'```action-contract\n'+json.dumps(action)+'\n'+text[end:]
    path.write_text(text)
    span={'path':'App.m','line':18,'end_line':24,'symbol':'viewWillTransitionToSize','source_sha256':digest((c['source']/'App.m').read_bytes())}
    facts={f['id']:f for f in c['graph']['facts']}
    appids=[o['id'] for o in c['obs']['obligations'] if facts[o['fact_id']]['anchor']['path']=='App.m' and
            span['line']<=facts[o['fact_id']]['anchor']['line']<=facts[o['fact_id']]['anchor']['end_line']<=span['end_line']]
    assert appids
    binding={'source_ac_id':'F001-AC01','source_ac_sha256':digest(json_bytes(api().acceptance_inventory(c['project'],'source_history')['F001-AC01'])),'source_span':copy.deepcopy(span),'obligation_ids':appids,
             'source_reviews':[{'obligation_id':o,'fact_sha256':digest(json_bytes(facts[next(x['fact_id'] for x in c['obs']['obligations'] if x['id']==o)])),
                                'status':'reviewed','input':'iOS rotation callback','processing':'Submit SDK transition/size at coordinator callback',
                                'observable':'Old reader relayout is system-window responsibility under approved replacement',
                                'reviewer':'source-reader','replacement_ac_ids':['F001-AC02']} for o in appids]}
    b={'id':'B-rotation','kind':'replaced_source_history','sources':[span],'obligation_ids':appids,'public_contracts':[],
       'skip_ref':'spec/baseline/skip-list.md#Rotation history','source_ac_bindings':[binding]}
    c['payload']['boundaries'].append(b)
    p=c['project']/'spec/baseline/skip-list.md'; p.write_text(p.read_text()+'\n## Rotation history\nApp.m viewWillTransitionToSize explicit old reader rotation history.\n')
    for route in c['review']['routes']:
        if route['fact_id'] in {x['fact_id'] for x in c['obs']['obligations'] if x['id'] in appids}:
            route['boundary_ids']=['B-rotation']
    reseal_review(c)
    c['payload']['replacements']=[{'id':'R-rotation','decision_id':'PD-X','decision_ref':'spec/decision-ledger.md#PD-X Local preview',
                 'decision_sha256':digest((c['project']/'spec/decision-ledger.md').read_bytes()),'boundary_ids':['B-rotation'],
                 'superseded_ac_ids':['F001-AC01'],'replacement_ac_ids':['F001-AC02'],
                 'historical_action_ids':['F001-A01'],'target_action_ids':['F001-A02'],'semantic_parts':[]}]
    return b


def test_ofd_multiline_sdk_call_can_use_exact_source_span_without_fake_call_fact(case):
    ofd_case(case)
    projection=load(case)
    assert set(case['private']) <= set(projection.historical_obligation_ids)
    # App callback branch remains a product responsibility.
    branch=case['payload']['boundaries'][0]['public_contracts'][0]['caller_fact_ids'][0]
    assert next(o['id'] for o in case['obs']['obligations'] if o['fact_id']==branch) in projection.product_obligation_ids


def test_ofd_multiline_without_explicit_span_keeps_old_strict_fact_anchor(case):
    ofd_case(case)
    del case['payload']['boundaries'][0]['public_contracts'][0]['caller_sources']
    with pytest.raises(MigrationError): load(case)


@pytest.mark.parametrize('mutation',['hash','wrong_path','fact_outside','selector','non_app','unreviewed_fact'])
def test_ofd_caller_source_span_is_exact_and_reviewed(case,mutation):
    ofd_case(case); contract=case['payload']['boundaries'][0]['public_contracts'][0]
    span=contract['caller_sources'][0]
    if mutation=='hash': span['source_sha256']='0'*64
    elif mutation=='wrong_path': span['path']='Private.m'
    elif mutation=='fact_outside': span['end_line']=10
    elif mutation=='selector': contract['callee_symbol']='SWOFDView.notARealCall:'
    elif mutation=='non_app':
        case['review']['file_roles'][0]['role']='dependency'; reseal_review(case)
    elif mutation=='unreviewed_fact':
        for route in case['review']['routes']:
            if route['fact_id'] in contract['caller_fact_ids']: route['resolution']='no_entry'
        reseal_review(case)
    with pytest.raises(MigrationError): load(case)


def test_ofd_superseded_app_rotation_span_keeps_role_and_unrelated_behavior(case):
    b=app_replacement(case); result=load(case)
    assert set(b['obligation_ids'])<=set(result.historical_obligation_ids)
    unrelated=[o['id'] for o in case['obs']['obligations'] if next(f for f in case['graph']['facts'] if f['id']==o['fact_id'])['anchor']['line']>=25]
    assert unrelated and set(unrelated)<=set(result.product_obligation_ids)
    assert case['review']['file_roles'][0]['role']=='application'


@pytest.mark.parametrize('mutation',['no_bindings','old_ac_wrong','active_ac','truth_outside','wrong_owner','whole_file','missing_review','fact_hash','missing_replacement_ac','other_decision','source_ac_hash','unknown_reviewer','app_as_private_unknown'])
def test_ofd_app_replacement_requires_exact_original_source_ac_and_per_obligation_review(case,mutation):
    b=app_replacement(case); binding=b['source_ac_bindings'][0]
    if mutation=='no_bindings': del b['source_ac_bindings']
    elif mutation=='old_ac_wrong': binding['source_ac_id']='F001-AC99'
    elif mutation=='active_ac': binding['source_ac_id']='F001-AC02'
    elif mutation=='truth_outside': binding['source_span']['line']=20
    elif mutation=='wrong_owner':
        p=case['project']/'spec/baseline/features/F001-private.md'; p.write_text(p.read_text().replace('源:SWTestDetailsController.','源:OtherController.'))
    elif mutation=='whole_file':
        b['sources'][0]['line']=1; b['sources'][0]['end_line']=28; binding['source_span']=copy.deepcopy(b['sources'][0])
        b['obligation_ids']=[o['id'] for o in case['obs']['obligations'] if next(f for f in case['graph']['facts'] if f['id']==o['fact_id'])['anchor']['path']=='App.m']
    elif mutation=='missing_review': binding['source_reviews']=binding['source_reviews'][:-1]
    elif mutation=='fact_hash': binding['source_reviews'][0]['fact_sha256']='0'*64
    elif mutation=='missing_replacement_ac': binding['source_reviews'][0]['replacement_ac_ids']=[]
    elif mutation=='other_decision': case['payload']['replacements'][0]['decision_id']='PD-Y'
    elif mutation=='source_ac_hash': binding['source_ac_sha256']='0'*64
    elif mutation=='unknown_reviewer': binding['source_reviews'][0]['reviewer']='generated-unreviewed-agent'
    elif mutation=='app_as_private_unknown':
        fact=next(f for f in case['graph']['facts'] if f['anchor']['path']=='App.m' and 18<=f['anchor']['line']<=24)
        claim={'status':'unknown','reason':'unreviewed app behavior','parts':[{'id':'private','status':'unknown','reason':'do not waive app','fact_ids':[fact['id']]}]}
        sem={'documents':[{'id':'F001','kind':'feature','facts':{'lifetime':claim}}]}
        case['payload']['replacements'][0]['semantic_parts']=[{'document_id':'F001','dimension':'lifetime','claim_sha256':digest(json_bytes(claim)),
                    'private_part_ids':['private'],'retained_part_ids':[],'retained_app_ac_ids':['F001-AC02']}]
        with pytest.raises(MigrationError): load(case,semantics=sem)
        return
    with pytest.raises(MigrationError): load(case)


def test_ofd_concurrency_retained_app_callback_uses_real_branch_fact_without_fake_task(case):
    ofd_case(case)
    private=case['payload']['boundaries'][0]; private['kind']='replaced_source_history'
    branch=next(f for f in case['graph']['facts'] if f['anchor']['path']=='App.m' and f['kind']=='branch')
    sdk=next(f for f in case['graph']['facts'] if f['anchor']['path']=='Private.m')
    assert not [f for f in case['graph']['facts'] if f['kind']=='task']
    claim={'status':'unknown','reason':'Private SDK callback queue remains unknown',
           'parts':[{'id':'private','status':'unknown','reason':'SDK owns callback delivery queue','fact_ids':[sdk['id']]},
                    {'id':'app','status':'known','fact_ids':[branch['id']],
                     'value':{'callback':'App branches on code and directly invokes HUD callbacks without dispatch'},
                     'evidence':[{'path':'App.m','line':branch['anchor']['line']}]}]}
    case['payload']['replacements']=[{'id':'R-callback','decision_id':'PD-X','decision_ref':'spec/decision-ledger.md#PD-X Local preview',
        'decision_sha256':digest((case['project']/'spec/decision-ledger.md').read_bytes()),'boundary_ids':['B-private'],
        'superseded_ac_ids':['F001-AC01'],'replacement_ac_ids':['F001-AC02'],
        'historical_action_ids':['F001-A01'],'target_action_ids':['F001-A02'],
        'semantic_parts':[{'document_id':'F001','dimension':'concurrency','claim_sha256':digest(json_bytes(claim)),
                           'private_part_ids':['private'],'retained_part_ids':['app'],'retained_app_ac_ids':['F001-AC02']}]}]
    sem={'documents':[{'id':'F001','kind':'feature','facts':{'concurrency':claim}}]}
    before=copy.deepcopy(case['graph'])
    result=load(case,semantics=sem)
    projected=result.semantic_requirement('F001','concurrency',claim)
    assert projected['retained_parts'][0]['fact_ids']==[branch['id']]
    assert projected['requires_ordinary_validation'] is True
    assert case['graph']==before


def test_target_action_retains_ordinary_active_app_acceptance(case):
    semantics, _ = replacement(case)
    feature = case['project']/'spec/baseline/features/F001-private.md'
    text = feature.read_text().replace('## 动作', '- [ ] F001-AC03 显示应用HUD。 `源:App.open → 标:Preview.open` `判:unit | HUD调用保留` `真:src:App.m:2`\n## 动作')
    text = text.replace('"ac_ids": ["F001-AC02"]', '"ac_ids": ["F001-AC02", "F001-AC03"]')
    feature.write_text(text)
    projection = load(case, semantics=semantics)
    assert set(projection.target_acceptance_ids) == {'F001-AC02', 'F001-AC03'}
    with pytest.raises(MigrationError, match='active target acceptance ownership missing'):
        projection.validate_target_ownership(['F001-AC02'], projection.product_obligation_ids)


@pytest.mark.parametrize('field,value', [('path', 'App.m'), ('line', 99), ('symbol', 'deleteAll')])
def test_historical_action_cannot_hide_unrelated_application_source(case, field, value):
    semantics, _ = replacement(case)
    feature = case['project']/'spec/baseline/features/F001-private.md'
    text = feature.read_text()
    start = text.index('```action-contract')
    end = text.index('```', start+3)
    block = text[start+len('```action-contract'):end]
    row = json.loads(block)
    row['source_anchors'][0][field] = value
    feature.write_text(text[:start]+'```action-contract\n'+json.dumps(row)+'\n'+text[end:])
    with pytest.raises(MigrationError, match='historical action'):
        load(case, semantics=semantics)


@pytest.mark.parametrize('selector,call,expected', [
    ('open', '[Private open]', True), ('open:', '[Private open:1]', True),
    ('open', '[Private open:1]', False), ('open:', '[Private open]', False),
    ('open:mode:', '[Private open:1 mode:2]', True),
    ('open:mode:', '[Private open:1 mode:2 extra:3]', False)])
def test_public_dependency_selector_keeps_colon_arity(selector, call, expected):
    from hmigbot_ios.swiftui import tokenize
    selectors = re.findall(r'[A-Za-z_]\w*', selector)
    assert api()._has_selector_call(tokenize(call), selectors, arity=selector.count(':')) is expected


def test_original_parser_payload_is_part_of_frozen_tool_revision(case):
    from hmigbot_ios.plan_contract import contract_revision, assert_pinned
    from hmigbot_ios.native_pipeline import configure
    configure(case['source'], case['project'])
    with patch('hmigbot_ios.source_responsibility.parser_fingerprints', return_value={'original-parser': 'a'*64}):
        contract = {'spec_contract_version': 1, 'responsibility_enabled': True, 'contract_revision': contract_revision(case['project'])}
    with patch('hmigbot_ios.source_responsibility.parser_fingerprints', return_value={'original-parser': 'b'*64}):
        with pytest.raises(MigrationError, match='tool contract revision'):
            assert_pinned(case['project'], contract)
