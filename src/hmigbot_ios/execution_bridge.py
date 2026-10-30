"""Freeze the Git plan/source contract for the single indexed execution flow.

Only derived execution inputs are created. Reviewed spec, plan, source and the
three legacy control ledgers remain owned by their original writers.
"""
from pathlib import Path
import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET

from .core import source_snapshot
from .core import MigrationError, digest, json_bytes, read_json, safe_child, snapshot, write_json

CONTRACT = 'spec/execution/execution-contract.json'


def source_ui(project, source, page_ids, *, items=None):
    """Project approved page anchors to Garry meta/outline; no runtime geometry."""
    from .native_pipeline import source_paths
    from .source_ui_capture import authoring_observations
    documents=[]
    for page in sorted((project/'spec/baseline/ui').glob('page_*.md')):
        match=re.fullmatch(r'(page_\d{4})_(.+)\.md',page.name)
        if match and match[1] in page_ids:
            documents.append({'id':match[1],'kind':'page','source_anchors':[
                {'path':p} for p in source_paths(page.read_text(encoding='utf-8-sig'))]})
    observed,_,gaps=authoring_observations(project,source.root,documents)
    rows, files = [], {}
    delivery = {}
    if items is not None:
        from .ios_ui_delivery import projection
        delivery, delivery_files = projection(project, source.root, items, observed)
        files.update(delivery_files)
    for page in sorted((project / 'spec/baseline/ui').glob('page_*.md')):
        match = re.fullmatch(r'(page_\d{4})_(.+)\.md', page.name)
        if match is None:
            raise MigrationError('Ambiguous page identity: ' + page.name)
        if match[1] not in page_ids:
            continue
        text = page.read_text(encoding='utf-8-sig')
        layouts = source_paths(text)
        if not layouts or any(p not in source.records for p in layouts):
            raise MigrationError('Page requires current source anchors: ' + page.name)
        for name in layouts:
            if digest(safe_child(source.root, name).read_bytes()) != source.records[name]['sha256']:
                raise MigrationError('Page source changed: ' + name)
        page_id, symbol = match.groups()
        folder = 'spec/execution/source-ui/' + page.stem
        meta = {'page_id':page_id, 'activity':symbol, 'package':'',
                'layout_sources':layouts, 'style_sources':layouts,
                'menu_sources':[], 'fragment_tags':[], 'recycler_item_layouts':[],
                'navigation_targets':[], 'navigation_mode':'UNKNOWN',
                'dynamic_menus':{}, 'clickable_elements':[], 'page_type':'unknown',
                'needs_immersive_safearea':None, 'view_xml_synthesized':True,
                'source_platform':'ios', 'source_sha256':source.fingerprint,
                'source_evidence':'reviewed Git anchors; static outline, runtime geometry unavailable',
                'page_spec':page.relative_to(project).as_posix(),
                'page_spec_sha256':digest(page.read_bytes()),
                'analysis_notes':['Phase A must retain unknown layout/state/navigation until source-backed review']}
        upstream=[]
        for candidate in (project/'spec/baseline/ui-snapshots').glob('*/meta.json'):
            value=read_json(candidate)
            if value.get('page_id')==page_id:
                upstream.append((candidate,value))
        if len(upstream)>1:
            raise MigrationError('Multiple upstream metadata records for '+page_id)
        if upstream:
            candidate,value=upstream[0]
            meta.update(upstream_metadata=value,upstream_metadata_ref=candidate.relative_to(project).as_posix(),
                        upstream_metadata_sha256=digest(candidate.read_bytes()))
        captures=observed.get(page_id,[])
        meta.update(runtime_observations=captures, runtime='captured' if captures else 'not_run',
                    runtime_observed_checkpoints=[c['checkpoint_id'] for c in captures],
                    runtime_observation_scope='This page/checkpoint only; synthetic outline remains static',
                    screenshot=captures[0]['screenshot']['path'] if captures else None)
        if captures:
            meta['source_evidence']='reviewed Git anchors with separately bound native UI observations; view.xml remains a static outline'
            meta['analysis_notes'].append('UI author must read runtime_observations original screenshots/hierarchies; do not infer other states or source defaults')
        meta.update(delivery.get(page_id, {}))
        hierarchy = ET.Element('hierarchy', {'synthesized':'true','source-platform':'ios',
                                            'bounds-evidence':'unavailable'})
        for name in layouts:
            parent = ET.SubElement(hierarchy, 'node', {'class':Path(name).stem,'source-file':name,
                                'bounds':'','resource-id':'','source-evidence':'approved-source-anchor'})
            if name not in source.files:
                continue  # IB/resource documents retain their explicit anchor without code claims.
            for token in source.tokens(name):
                if token.kind != 'string' and token.value in {'Text','Button','Toggle','TextField','Image',
                        'List','ScrollView','VStack','HStack','ZStack','NavigationStack','NavigationLink','TabView','Picker'}:
                    ET.SubElement(parent,'node',{'class':'SwiftUI.'+token.value,'source-file':name,
                         'source-line':str(token.line),'bounds':'','resource-id':'','clickable':'unknown',
                         'visibility':'unknown','enabled':'unknown'})
        files[folder+'/meta.json'] = json_bytes(meta)
        files[folder+'/view.xml'] = (ET.tostring(hierarchy,encoding='unicode')+'\n').encode('utf-8')
        rows.append({'page_id':page_id,'activity':symbol,'snapshot_dir':folder,
                     'page_spec':meta['page_spec'],'source_anchors':layouts,
                     'runtime_observations':captures,'runtime_observed_checkpoints':meta['runtime_observed_checkpoints'],
                     **delivery.get(page_id, {})})
    if len({r['page_id'] for r in rows}) != len(rows):
        raise MigrationError('Duplicate approved page IDs')
    files['spec/execution/source-ui/manifest.json'] = json_bytes({'source_platform':'ios',
        'source_sha256':source.fingerprint,'pages':rows,'runtime_observed':False,
        'runtime_observed_page_ids':sorted(observed),
        'runtime_observation_scope':'per page/checkpoint only; not all-page acceptance',
        'runtime_evidence_gaps':gaps})
    return rows, files


def _deletion_preimages(project, tasks, *, capture=False):
    """Capture exact original target bytes only before indexed dispatch.

    Never backfill an old contract from current absence or an expected hash.
    Frozen plan intent is necessary; capture=True additionally reads the real
    ordinary-file preimage through the existing original deletion guard.
    """
    from .receipt_outputs import deletion_intent
    return {task['id']: deletion_intent(project, task, check_current=capture)
            for task in tasks if task.get('deletions')}


def prepare(project, *, apply=False, usage_ledger=None, usage_run_id=None):
    from .native_pipeline import context
    from .execution_source import Source
    from .ios_harness import check, reuse_acceptance
    from .plan_contract import plan_units, structural_digest, assert_pinned, contract_revision
    from .ios_scheduler import baseline_inputs
    project = Path(project).resolve()
    if (usage_ledger is None)!=(usage_run_id is None):
        raise MigrationError('Select both usage_ledger and usage_run_id')
    usage=None
    if usage_ledger is not None:
        from .usage_budget import check_for_dispatch
        ledger=Path(usage_ledger)
        ledger=ledger if ledger.is_absolute() else project/ledger
        usage=check_for_dispatch(ledger,run_id=usage_run_id,project_root=project)
        if not usage['can_continue']:
            raise MigrationError('Usage budget refused indexed dispatch: '+', '.join(usage['reasons']))
    source_root, _ = context(project)
    source = Source(source_root, project)
    projections, units = plan_units(project)
    if any(item['scope']=='product' and item['page_ids'] for item in units.values()):
        from .native_writeback import _index,UI
        _index(project,UI)  # Enforce the existing, authored Git writer schema before execution.
    plan = safe_child(project,'spec/blueprint/contracts.json')
    if not plan.is_file():
        raise MigrationError('Git plan-ir freeze is required before indexed execution')
    pinned = read_json(plan)
    assert_pinned(project, pinned)
    if pinned.get('source_sha256') != source.fingerprint or baseline_inputs(project, 'domains') != pinned.get('input_hashes'):
        raise MigrationError('Git frozen plan inputs changed; reviewed replan is required')
    for path, expected in pinned.get('prompt_hashes',{}).items():
        if digest(safe_child(project,path).read_bytes()) != expected:
            raise MigrationError('Frozen prompt changed: '+path)
    for refs in pinned.get('task_inputs',{}).values():
        for ref in refs:
            if digest(safe_child(project,ref['path']).read_bytes()) != ref['sha256']:
                raise MigrationError('Frozen task input changed: '+ref['path'])
    reused = reuse_acceptance(project, source_root, source.graph, pinned)
    if reused is None:
        report, code = check(project, report_only=True)
        gate_use = {'mode': 'actual', 'not_actual_call_now': False}
    else:
        (report, gate_use), code = reused, 0
    from .gate_policy import blocking_findings, scope_to_tasks
    blockers = blocking_findings(report.get('findings', []))
    if code and blockers:
        scoped = scope_to_tasks(blockers, pinned.get('ios_tasks', []), graph=source.graph,
                                task_inputs=pinned.get('task_inputs', {}))
        raise MigrationError('Source-bound execution has unresolved product/consumer inputs; independent diagnostics remain available: ' + json.dumps(scoped,ensure_ascii=False))
    dispatch = project / 'spec/state/dispatch.json'
    if dispatch.is_file():
        waves = read_json(dispatch).get('waves',{})
        if waves.get('domains',{}).get('dispatched'):
            raise MigrationError('Existing v2 domains attempts must finish/recover before indexed handoff; no dual scheduler')
    rows, outputs = source_ui(project, source, {page for unit in units.values()
                          if unit['scope'] == 'product' for page in unit['page_ids']}, items=units)
    frozen = {p.relative_to(project).as_posix(): structural_digest(p.read_text(encoding='utf-8-sig'),
                    artifact=p.relative_to(project).as_posix()) for p in projections}
    frozen['spec/blueprint/contracts.json'] = digest(plan.read_bytes())
    from .ios_ui_delivery import INVENTORY
    inventory = safe_child(project, INVENTORY)
    if inventory.is_file():
        frozen[INVENTORY] = digest(inventory.read_bytes())
    contract = {'schema_version':1,'execution_model':'indexed-stages-v1','source_sha256':source.fingerprint,
        'resource_protocol':'task-deltas-v1',
        'source_authority':'git','execution_authority':'garry','plan_inputs':frozen,
        'contract_revision':contract_revision(project),'plan_items':units,
        'source_ui':rows,'output_hashes':{p:digest(raw) for p,raw in outputs.items()},
        'runtime_observed':False,'behavior_verified':False,
        'scope':'source/plan handoff only; does not mark execution, compilation or verification completed'}
    planned_deletions = _deletion_preimages(project, pinned.get('ios_tasks', []))
    destination = safe_child(project, CONTRACT)
    if destination.exists():
        prior_raw = destination.read_bytes()
        prior = json.loads(prior_raw)
        # Execution workers may enrich a derived meta with source-backed observations.
        # Never overwrite that result, or silently move a frozen handoff boundary.
        for key in ('execution_model','resource_protocol','source_sha256','plan_inputs','contract_revision','plan_items'):
            if prior.get(key) != contract[key]:
                raise MigrationError('Existing indexed execution contract changed: '+key+'; archive/review before replan')
        if prior.get('deletion_preimages', {}) != planned_deletions:
            raise MigrationError('Existing indexed deletion preimage evidence missing/changed; review recovery without backfilling history')
        if destination.read_bytes() != prior_raw:
            raise MigrationError('Indexed execution contract changed during preparation')
        return {'status':'ready','contract':CONTRACT,'pages':len(rows),'applied':False,'existing':True,
                'contract_sha256':digest(prior_raw), 'harness_check':gate_use,
                **({'usage_budget':usage} if usage is not None else {})}
    if apply:
        captured = _deletion_preimages(project, pinned.get('ios_tasks', []), capture=True)
        if captured:
            contract['deletion_preimages'] = captured
        # All checks complete before the first write. Reject existing unowned inputs.
        for relative in outputs:
            if safe_child(project,relative).exists():
                raise MigrationError('Derived execution input already exists without its contract: '+relative)
        if source_snapshot(source_root)['sha256'] != source.fingerprint:
            raise MigrationError('Source changed during indexed execution preparation')
        from .core import atomic_write
        written = []
        try:
            for relative, raw in outputs.items():
                target=safe_child(project,relative)
                atomic_write(target,raw);written.append((target,digest(raw)))
            write_json(destination,contract)
        except BaseException:
            for target, expected in reversed(written):
                if target.is_file() and digest(target.read_bytes()) == expected:
                    target.unlink()
            raise
    return {'status':'ready' if apply else 'preview','contract':CONTRACT,'pages':len(rows),'applied':apply,
            'harness_check':gate_use,
            'execution_model':'indexed-stages-v1','behavior_verified':False,
            **({'usage_budget':usage} if usage is not None else {})}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project',type=Path,required=True)
    parser.add_argument('--apply',action='store_true')
    parser.add_argument('--usage-ledger',type=Path)
    parser.add_argument('--usage-run-id')
    args=parser.parse_args(argv)
    try:
        print(json.dumps(prepare(args.project,apply=args.apply,usage_ledger=args.usage_ledger,
                                 usage_run_id=args.usage_run_id),ensure_ascii=False,indent=2))
        return 0
    except (MigrationError,ValueError,OSError,KeyError,TypeError) as exc:
        print(json.dumps({'status':'blocked','error':str(exc),'recovery':'repair/review Git source and indexed plan; rerun execution-contract'},ensure_ascii=False))
        return 2
