"""Synthetic compiler capture integration; real graph/parser/projection consumers."""
import copy
from pathlib import Path
import pytest
from hmigbot_ios.core import MigrationError, digest, json_bytes, read_json, write_json
from hmigbot_ios.ios_facts import RULES
from hmigbot_ios.native_semantics import required_facts, validate_native_payload
from hmigbot_ios.ios_harness import ac_inventory, validate_native_claims, check
from hmigbot_ios.source_responsibility import load_and_validate
from test_source_responsibility import case, replacement


def persist(c):
    from hmigbot_ios.native_pipeline import configure, index_source
    from hmigbot_ios.ios_harness import initialize
    configure(c['source'], c['project']); initialize(c['project']); index_source(c['project'])
    cfg=read_json(c['project']/'.migbot/config.json'); cfg['ios_harness']['spec_contract_version']=1
    write_json(c['project']/'.migbot/config.json',cfg)
    path=c['project']/'spec/baseline/features/F001-private.md'
    path.write_text(path.read_text().replace('---\nsource_anchors:', '---\nsource_platform: ios\nsource_anchors:').replace('判:device | 实际窗口','判:unit | 公共窗口请求及应用赋值保留'))
    sem, claim = replacement(c)
    doc=sem['documents'][0]; doc.update(languages=['objc'], frameworks=['nonvisual'])
    for dim in required_facts('feature', {'objc'}, {'nonvisual'}):
        if dim=='state_transitions': continue
        relevant=[f for f in c['graph']['facts'] if dim in RULES[f['kind']]['dimensions']]
        doc['facts'][dim] = ({'status':'known','value':{'reviewed':'actual source token'},
            'fact_ids':[f['id'] for f in relevant], 'evidence':[{'path':f['anchor']['path'],'line':f['anchor']['line']} for f in relevant]}
            if relevant else {'status':'not_applicable','reason':'Complete fixture source has no operation'})
    write_json(c['project']/'spec/baseline/ios-semantics.json',sem)
    write_json(c['project']/'spec/baseline/ios-responsibility.json', c['payload'])
    projection=load_and_validate(c['project'],c['source'],c['graph'],c['obs'])
    rows=[]
    for o in c['obs']['obligations']:
        row={'obligation_id':o['id'], 'ac_ids':['F001-AC02'],
             'source_review':{'status':'reviewed','input':'open','processing':'request','observable':'window','reviewer':'fixture-reader'}}
        if o['id'] in projection.historical_obligation_ids:
            row.update(ac_ids=[], responsibility_ref='B-private')
        rows.append(row)
    write_json(c['project']/'spec/baseline/ios-coverage.json',{'schema_version':2,'graph_sha256':digest(json_bytes(c['graph'])),'mappings':rows})
    return sem,projection


def test_real_projection_consumed_by_acceptance_and_plan_inventory(case):
    sem,p=persist(case)
    assert set(ac_inventory(case['project']))=={'F001-AC02'}
    from hmigbot_ios.plan_contract import _inventory
    assert set(_inventory(case['project'])[0])=={'F001-AC02'}
    (case['project']/'spec/baseline/ios-responsibility.json').unlink()
    assert set(ac_inventory(case['project']))=={'F001-AC01','F001-AC02'}
    assert set(_inventory(case['project'])[0])=={'F001-AC01','F001-AC02'}


def test_private_unknown_retained_app_parts_validate_with_ordinary_rules(case):
    sem,p=persist(case); before=copy.deepcopy(sem); issues=[]
    validate_native_payload(case['source'],case['project'],{'F001':('feature',['App.m','Private.m'])},
                            {'App.m','Private.m'},lambda *i:issues.append(i),sem,projection=p)
    validate_native_claims(case['project'],case['graph'],sem,lambda *i:issues.append(i),projection=p)
    assert issues==[]
    assert sem==before and sem['documents'][0]['facts']['state_transitions']['status']=='unknown'
    issues=[]
    validate_native_payload(case['source'],case['project'],{'F001':('feature',['App.m','Private.m'])},
                            {'App.m','Private.m'},lambda *i:issues.append(i),sem)
    assert any(i[0]=='IOS.NATIVE_FACT_UNKNOWN' for i in issues)


def test_harness_counts_all_product_and_history_without_losing_mappings(case):
    sem,p=persist(case)
    report,code=check(case['project'],report_only=True)
    assert report['checks']['responsibility']['status']=='PASS', report
    assert report['checks']['coverage']['status']=='PASS',report['findings']
    assert report['checks']['native_claims']['status']=='PASS',report
    assert report['responsibility_counts']==p.counts
    assert report['acceptance_counts']=={'all':2,'active_target':1,'source_history':1}
    assert report['historical_obligation_ids']==list(p.historical_obligation_ids)
    coverage=case['project']/'spec/baseline/ios-coverage.json'; data=read_json(coverage)
    data['mappings']=[r for r in data['mappings'] if r['obligation_id'] not in p.historical_obligation_ids]
    write_json(coverage,data)
    assert any(f['rule']=='IOS.OBLIGATION_UNCOVERED' for f in check(case['project'],report_only=True)[0]['findings'])


@pytest.mark.parametrize('mutation',['history_ref','history_with_ac','product_history_ref','product_old_ac'])
def test_harness_projection_cannot_hide_or_relabel_product(case,mutation):
    _,p=persist(case); path=case['project']/'spec/baseline/ios-coverage.json'; data=read_json(path)
    hist=next(r for r in data['mappings'] if r['obligation_id'] in p.historical_obligation_ids)
    app=next(r for r in data['mappings'] if r['obligation_id'] in p.product_obligation_ids)
    if mutation=='history_ref': hist['responsibility_ref']='B-fake'
    elif mutation=='history_with_ac': hist['ac_ids']=['F001-AC02']
    elif mutation=='product_history_ref': app.update(ac_ids=[],responsibility_ref='B-private')
    else: app['ac_ids']=['F001-AC01']
    write_json(path,data)
    assert check(case['project'],report_only=True)[0]['checks']['coverage']['status']=='FAIL'


@pytest.mark.parametrize('mutation',['review','decision','payload','semantics','build','ac'])
def test_freeze_consumes_complete_responsibility_proof(case,mutation):
    _,p=persist(case)
    from hmigbot_ios.ios_scheduler import baseline_inputs
    before=baseline_inputs(case['project'],'domains')
    assert p.frozen_inputs().items() <= before.items()
    rel={'review':'spec/ref/responsibility-review.json','decision':'spec/decision-ledger.md',
         'payload':'spec/baseline/ios-responsibility.json','semantics':'spec/baseline/ios-semantics.json',
         'build':'spec/ref/build/manifest.json','ac':'spec/baseline/features/F001-private.md'}[mutation]
    path=case['project']/rel; path.write_bytes(path.read_bytes()+b'\n ')
    with pytest.raises(MigrationError): p.validate_frozen_inputs(case['project'])
    # New baseline generation either rejects changed proof or produces a different
    # frozen map; both are refused by existing dispatch AND receipt before writers.
    try: after=baseline_inputs(case['project'],'domains')
    except MigrationError: return
    assert after!=before


def test_shared_projection_pins_actual_page_anchor_input(case):
    sem,p=persist(case)
    page=case['project']/'spec/baseline/ui/page_0001_Reader.md'; page.parent.mkdir(parents=True)
    page.write_text('---\nsource_platform: ios\nsource_anchors:\n  - path: App.m\n  - path: Private.m\n---\n# Reader\n')
    claim=copy.deepcopy(sem['documents'][0]['facts']['state_transitions'])
    sem['documents'].append({'id':'page_0001','kind':'page','facts':{'state_transitions':claim}})
    part=copy.deepcopy(case['payload']['replacements'][0]['semantic_parts'][0]); part['document_id']='page_0001'
    case['payload']['replacements'][0]['semantic_parts'].append(part)
    write_json(case['project']/'spec/baseline/ios-semantics.json',sem)
    write_json(case['project']/'spec/baseline/ios-responsibility.json',case['payload'])
    p=load_and_validate(case['project'],case['source'],case['graph'],case['obs'])
    assert 'spec/baseline/ui/page_0001_Reader.md' in p.frozen_inputs()
    page.write_text(page.read_text().replace('  - path: Private.m\n',''))
    with pytest.raises(MigrationError): p.validate_frozen_inputs(case['project'])


def complete_synthetic_contract(c):
    """Source-reviewed minimal app contract; no runtime or real compiler claim."""
    from hmigbot_ios.ios_literals import run
    from hmigbot_ios.expertise import prepare as expertise_prepare, record
    base=c['project']/'spec/baseline'
    for name in ('feature-base.md','feature-index.md','ui-manifest.md','source-coverage-report.md'):
        (base/name).write_text('# Fixture source contract\nApp.open writes one and requests Private.open; system window replaces private implementation.\n')
    feature=base/'features/F001-private.md'
    feature.write_text(feature.read_text()+'''\ncomplexity: simple
tier: standard
depth: full
## 范围
App.open assignment and public private-request interface only; no page inventory in this synthetic source.
## 服务层
| 目标接口 | 输入输出 |
|---|---|
| Preview.open | window request or error; application assignment remains |
## 状态管理
App.count assigned one on open; private source count assigned two retained as historical implementation.
## 对接点
App.open invokes system Preview.open through its public contract.
''')
    # No app-binding original AC row is changed; the same approved replacement
    # still pins current Markdown, including the newly authored target contract.
    run(c['project'])
    expertise_prepare(c['project'])
    plan=read_json(c['project']/'spec/ref/ios-expertise-plan.json')
    request=c['project'].parent/'expertise-fixture.json'
    write_json(request,{'plan_sha256':digest(json_bytes(plan)),'reviews':[
        {'id':r['id'],'resources':r['resources'],'status':'reviewed','reviewer':'fixture-source-reader',
         'observations':[{'source':{'path':p,'line':1},'interpretation':'Synthetic source app writes one and calls public private interface; no private queue knowledge inferred.','unknowns':[]} for p in r['source_paths']]}
        for r in plan['reviews']]})
    record(c['project'],request)
    report,code=check(c['project'],report_only=True)
    assert code==0, report['findings']


def test_authoring_preserves_unknown_and_emits_only_candidate(case):
    sem,p=persist(case)
    from hmigbot_ios.native_authoring import prepare,render
    request=prepare(case['project'])['input_template']
    request.update(documents=sem['documents'],dispositions=[],truth_anchors=[{'ac_id':'F001-AC01','path':'Private.m','line':2}])
    result=render(case['project'],request)
    assert result['status']=='candidate' and result['spec_complete'] is False
    assert result['files']['spec/baseline/ios-semantics.json']==sem
    # A candidate payload is an output for independent review, never a dispatch
    # input or a forged source gate result.
    (case['project']/'spec/baseline/ios-responsibility.json').unlink()
    request=prepare(case['project'])['input_template']
    request.update(documents=sem['documents'],dispositions=[],responsibility=case['payload'],
                   truth_anchors=[{'ac_id':'F001-AC01','path':'Private.m','line':2}])
    result=render(case['project'],request)
    assert result['files']['spec/baseline/ios-responsibility.json']==case['payload']
    assert not (case['project']/'spec/baseline/ios-responsibility.json').exists()


@pytest.mark.parametrize('missing',['evidence','fact_ids','value'])
def test_surviving_application_claim_missing_blocks_every_consumer(case,missing):
    sem,p=persist(case)
    claim=sem['documents'][0]['facts']['state_transitions']; claim['parts'][1].pop(missing)
    case['payload']['replacements'][0]['semantic_parts'][0]['claim_sha256']=digest(json_bytes(claim))
    write_json(case['project']/'spec/baseline/ios-responsibility.json',case['payload'])
    write_json(case['project']/'spec/baseline/ios-semantics.json',sem)
    with pytest.raises(MigrationError): ac_inventory(case['project'])
    from hmigbot_ios.plan_contract import _inventory
    with pytest.raises(MigrationError): _inventory(case['project'])
    report,_=check(case['project'],report_only=True)
    assert report['checks']['responsibility']['status']=='FAIL'
    assert report['checks']['coverage']['status']=='not_run'
    assert report['checks']['native_claims']['status']=='not_run'


@pytest.mark.parametrize('landing',[False,True])
@pytest.mark.parametrize('drift',['review','decision','build','ui_anchors','payload'])
def test_actual_scheduler_refuses_drift_before_original_writers(case,landing,drift):
    sem,p=persist(case); complete_synthetic_contract(case)
    from hmigbot_ios.ios_scheduler import generate,step
    request=case['project'].parent/'plan.json'
    task={'id':'app','role':'a2h-ios-converter','goal':'Preserve app count and open replacement public window',
          'ownership':['entry/App.ets'],'ac_ids':['F001-AC02'],
          'fact_ids':[f['id'] for f in case['graph']['facts'] if f['anchor']['path']=='App.m'],'parents':[]}
    write_json(request,{'schema_version':2,'wave':'domains','graph_sha256':digest(json_bytes(case['graph'])),'tasks':[task]})
    generate(case['project'],request)
    if landing:
        action,code=step(case['project'],'domains'); assert action['action']=='dispatch'
        output=case['project']/'entry/App.ets'; output.parent.mkdir(parents=True,exist_ok=True); output.write_text('class App {}\n')
        row=action['batch'][0]
        write_json(case['project']/row['result_path'],{'ios_receipt_version':2,'source_sha256':case['graph']['source_sha256'],
            'plan_sha256':digest((case['project']/'spec/waves/plan-domains.json').read_bytes()),'task_id':'app','task':'app','domain':'app',
            'status':'generated','final_state':'PASS','behavior_verified':False,'file_hashes':{'entry/App.ets':digest(output.read_bytes())},
            'ac_ids':['F001-AC02'],'files_touched':['entry/App.ets'],'files':['entry/App.ets'],'fixed':[],'skipped':[],'findings':[]})
    rel={'review':'spec/ref/responsibility-review.json','decision':'spec/decision-ledger.md','build':'spec/ref/build/manifest.json',
         'payload':'spec/baseline/ios-responsibility.json','ui_anchors':'spec/baseline/ui/page_0001_Reader.md'}[drift]
    target=case['project']/rel; target.parent.mkdir(parents=True,exist_ok=True)
    target.write_bytes((target.read_bytes() if target.exists() else b'---\nsource_anchors:\n  - path: App.m\n---\n')+b'\n ')
    before={str(p.relative_to(case['project'])):p.read_bytes() for p in (case['project']/'spec/state').rglob('*') if p.is_file()}
    with pytest.raises(MigrationError): step(case['project'],'domains',landing=landing)
    after={str(p.relative_to(case['project'])):p.read_bytes() for p in (case['project']/'spec/state').rglob('*') if p.is_file()}
    assert before==after


def test_v2_indexed_plan_uses_same_active_projection(case):
    _,p=persist(case)
    from test_plan_contract import PlanContractTests
    from hmigbot_ios.plan_contract import validate_plan
    template=PlanContractTests(methodName='test_valid_explicit_merge_and_transitive_consumer')
    template.setUp()
    try:
        for old in (template.project/'spec/baseline/plans').rglob('*.md'):
            target=case['project']/old.relative_to(template.project); target.parent.mkdir(parents=True,exist_ok=True)
            target.write_text(old.read_text().replace('F001-AC01','F001-AC02'))
        for relative in ('feature-index.md','ui-manifest.md','ui/page_0001_Counter.md'):
            old=template.project/'spec/baseline'/relative; target=case['project']/'spec/baseline'/relative
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_text(old.read_text().replace('features/F001-counter.md','features/F001-private.md').replace('F001-AC01','F001-AC02'))
        cfg=read_json(case['project']/'.migbot/config.json'); cfg['ios_harness']['spec_contract_version']=2
        write_json(case['project']/'.migbot/config.json',cfg)
        request=copy.deepcopy(template.request)
        for task in request['tasks']:
            task['ac_ids']=[a.replace('F001-AC01','F001-AC02') for a in task['ac_ids']]
            task['fact_ids']=[f['id'] for f in case['graph']['facts'] if f['anchor']['path']=='App.m']
        assert validate_plan(case['project'],request)['status']=='PASS'
        request['tasks'][1]['ac_ids']=['F001-AC01']
        with pytest.raises(MigrationError): validate_plan(case['project'],request)
    finally: template.tearDown()


def test_product_literal_view_retains_separate_source_history(case):
    _,p=persist(case)
    from hmigbot_ios.ios_literals import run
    from hmigbot_ios.quality_views import product_literals
    run(case['project'])
    before=(case['project']/'spec/baseline/literal-ledger.json').read_bytes()
    view=product_literals(case['project'])
    assert view['inputs']['responsibility']==digest(json_bytes(p.frozen_inputs()))
    # Value occurrences stay in the raw ledger even when implementation scope is
    # replaced. Classification is source consumption evidence, never execution.
    assert all(e['classification']=='source_history' for e in view['entries'] if any(s.startswith('Private.m:2') for s in e['sources']))
    assert before==(case['project']/'spec/baseline/literal-ledger.json').read_bytes()


@pytest.mark.parametrize('legacy',['dependency','test','not_applicable'])
def test_validated_literal_responsibility_dominates_old_file_disposition(case,legacy):
    _,p=persist(case)
    from hmigbot_ios.ios_literals import run
    from hmigbot_ios.quality_views import product_literals
    run(case['project'])
    write_json(case['project']/'spec/baseline/ios-source-disposition.json',{
        'source_sha256':case['graph']['source_sha256'],'files':[
            {'path':name,'line':1,'end_line':3,'source_sha256':digest((case['source']/name).read_bytes()),
             'disposition':legacy,'reason':'Legacy source ownership note, not an obligation exclusion'} for name in ('App.m','Private.m')]})
    raw=(case['project']/'spec/baseline/literal-ledger.json').read_bytes()
    entries=product_literals(case['project'])['entries']
    private=[e for e in entries if any(a.startswith('Private.m:2') for a in e['sources'])]
    app=[e for e in entries if any(a.startswith('App.m:2') for a in e['sources'])]
    assert private and app, 'Fixture must exercise actual numeric literal occurrences'
    assert {e['classification'] for e in private}=={'source_history'}
    assert {e['classification'] for e in app}=={'product'}
    assert raw==(case['project']/'spec/baseline/literal-ledger.json').read_bytes()


def test_optional_projection_pins_tool_revision_even_for_legacy_markdown_profile(case):
    persist(case)
    from hmigbot_ios.plan_contract import assert_pinned,contract_revision
    contract={'spec_contract_version':1,'contract_revision':contract_revision(case['project']), 'responsibility_enabled':True}
    assert_pinned(case['project'],contract)
    contract['contract_revision']='0'*64
    with pytest.raises(MigrationError): assert_pinned(case['project'],contract)
    (case['project']/'spec/baseline/ios-responsibility.json').unlink()
    with pytest.raises(MigrationError): assert_pinned(case['project'],contract)


def test_literal_shared_by_historical_and_active_facts_stays_product(case):
    from hmigbot_ios.ios_facts import extract,obligations
    from hmigbot_ios.native_pipeline import configure,index_source
    from hmigbot_ios.ios_harness import initialize
    from hmigbot_ios.ios_literals import run
    from hmigbot_ios.quality_views import product_literals
    from test_source_responsibility import reseal_review
    (case['source']/'Private.m').write_text('@implementation Private\n- (void)open { self.count = 2; self.result = 3; }\n@end\n')
    graph=extract(case['source']); obs=obligations(graph)
    configure(case['source'],case['project']); initialize(case['project']); index_source(case['project'])
    private=[f for f in graph['facts'] if f['anchor']['path']=='Private.m']
    assert len(private)==2 and private[0]['anchor']['line']==private[1]['anchor']['line']==2
    history=private[0]['id']
    case['review']['source_sha256']=graph['source_sha256']; case['review']['graph_sha256']=digest(json_bytes(graph))
    for row in case['review']['file_roles']: row['source_sha256']=digest((case['source']/row['path']).read_bytes())
    case['review']['routes']=[{'fact_id':f['id'],'resolution':'dependency_boundary' if f['id']==history else 'product_entry',
        'boundary_ids':['B-private'] if f['id']==history else [],'evidence':[f['anchor']]} for f in graph['facts']]
    reseal_review(case)
    payload=case['payload']; payload.update(source_sha256=graph['source_sha256'],graph_sha256=digest(json_bytes(graph)))
    boundary=payload['boundaries'][0]; boundary['sources'][0]['source_sha256']=digest((case['source']/'Private.m').read_bytes())
    boundary['obligation_ids']=['IO-'+history[3:]]
    boundary['public_contracts'][0]['caller_fact_ids']=[f['id'] for f in graph['facts'] if f['anchor']['path']=='App.m']
    write_json(case['project']/'spec/baseline/ios-facts.json',graph)
    write_json(case['project']/'spec/baseline/ios-obligations.json',obs)
    write_json(case['project']/'spec/baseline/ios-responsibility.json',payload)
    write_json(case['project']/'spec/baseline/ios-coverage.json',{'schema_version':2,'graph_sha256':digest(json_bytes(graph)),
        'mappings':[{'obligation_id':o['id'],'ac_ids':[] if o['fact_id']==history else ['F001-AC02'],
        'source_review':{'status':'reviewed','input':'public request','processing':'retain active public result','observable':'app consumes public result','reviewer':'fixture-source-reader'}} for o in obs['obligations']]})
    run(case['project'])
    entries=[e for e in product_literals(case['project'])['entries'] if 'Private.m:2' in e['sources']]
    assert entries
    assert {e['classification'] for e in entries}=={'product'}


def test_summary_separates_history_counts_without_converting_evidence(case):
    _, projection = persist(case)
    from hmigbot_ios.quality_views import summary
    before = {p.relative_to(case['project']): p.read_bytes() for p in case['project'].rglob('*') if p.is_file()}
    result = summary(case['project'])
    assert result['counts']['acceptance'] == 1
    assert result['counts']['acceptance_all'] == 2
    assert result['counts']['acceptance_source_history'] == 1
    assert result['source_responsibility']['counts'] == projection.counts
    assert result['source_responsibility']['behavior_verified'] is False
    assert result['behavior_verified'] is False
    assert result['axes']['behavior']['status'] != 'passed'
    assert before == {p.relative_to(case['project']): p.read_bytes() for p in case['project'].rglob('*') if p.is_file()}


def test_scheduler_still_requires_ordinary_ac_from_a_mixed_target_action(case):
    persist(case)
    feature = case['project']/'spec/baseline/features/F001-private.md'
    text = feature.read_text().replace('## 动作', '- [ ] F001-AC03 应用HUD保留。 `源:App.open → 标:Preview.open` `判:unit | HUD调用保留` `真:src:App.m:2`\n## 动作')
    text = text.replace('"ac_ids": ["F001-AC02"]', '"ac_ids": ["F001-AC02", "F001-AC03"]')
    feature.write_text(text)
    complete_synthetic_contract(case)
    from hmigbot_ios.ios_scheduler import generate
    request = case['project'].parent/'missing-app-ac.json'
    write_json(request, {'schema_version':2, 'wave':'domains', 'graph_sha256':digest(json_bytes(case['graph'])),
        'tasks':[{'id':'app','role':'a2h-ios-converter','goal':'Preserve preview plus HUD', 'ownership':['entry/App.ets'],
            'ac_ids':['F001-AC02'], 'fact_ids':[f['id'] for f in case['graph']['facts'] if f['anchor']['path']=='App.m'], 'parents':[]}]})
    with pytest.raises(MigrationError, match='omitted acceptance criteria.*F001-AC03'):
        generate(case['project'], request, validate_only=True)
