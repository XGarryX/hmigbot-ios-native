"""Public visual entry dispatch: native source facts/actions, retained target gates.

Every shipped visual launcher calls this module, including compiled reentry.
An unimplemented iOS source action is explicit and never falls back to ADB.
"""
from __future__ import annotations
import argparse
from collections import Counter
from contextlib import redirect_stdout
import copy
import io
import json
import os
from pathlib import Path
import shutil
import sys
import time
import uuid

from hmigbot_ios.core import MigrationError, read_json, write_json
from . import native_canonical as canonical

SOURCE_DEVICE = {
    'ad_dismiss','adhoc_capture','auto_install_artifacts','blackbox_explore',
    'capture_page_e2e','capture_or_reuse','chain_ledger_settle','click_and_verify_edge',
    'dismiss_popups','gate_experiment','ground_page_checks','hit_chain_probe',
    'meltdown_probe','node_sweep','run_phase2_android_survey','run_phase2_ios_survey',
    'run_scenario_with_verify','stitch_long_screenshot','verify_outcome',
    'walk_back_to','walk_clickables','walk_exec','walk_to','walk_whereami',
    'extract_dialog_ids','extract_clickables_717','lib_tools',
}
DATA = {
    'assert_evidence_channel','assert_gap_ticket_coverage','assert_replay_artifacts',
    'assert_round_complete','assert_run_success','build_baseline_aliases','build_batches',
    'build_judge_input','build_orphan_dialogs_doc','build_page_queue','build_spec_oracle',
    'carry_forward_findings','check_android_screenshot','check_blackbox_evidence',
    'check_dimension_prereqs','check_fix_schema','check_functional_dimension',
    'check_prereq_freshness','check_reviewer_report','collect_changed_files',
    'compare_webview_urls','compile_replay_plan','compose_side_by_side','detect_stubborn',
    'enrich_factree_anchors','extract_clickables_cli',
    'fill_chunk_prompt','incremental_verify','inject_factree_refs','inject_spec_oracle',
    'lib_image','lib_resolve_round','mark_batch_done',
    'materialize_blackbox_to_factree','merge_capture_dirs','next_batch','next_resume',
    'phase2_needs','phase2_scope','plan_edge_walk','reformat_markdown_to_schema',
    'render_finding_skeleton','render_report','replay_place_artifacts','resize_screenshot',
    'resolve_hmos_impl','reverify_transaction','round_budget','run_fix_self_check',
    'slice_batches','structural_diff','trip_assign','trip_end_slice',
    'validate_batch_output','walk_finalize','walk_inherit','walk_ledger',
    'walk_place_baselines','writeback_walk',
}
TARGET_DEVICE = {'hmos_capture_page_e2e','replay_exec','check_replay'}
SOURCE_DATA_BRIDGE = {'build_batches','build_judge_input','check_android_screenshot',
    'check_blackbox_evidence','check_functional_dimension','phase2_needs','replay_place_artifacts'}


def _kind(value):
    if not isinstance(value,dict):return None
    source=value.get('source_platform') or value.get('platform')
    if isinstance(source,str) and source in {'ios','android'}:return source
    provenance=value.get('native_input_provenance',{})
    if isinstance(provenance,dict) and provenance.get('source_platform')=='ios':return 'ios'
    if isinstance(value.get('source'),str) and value.get('source') in {'ios','android'}:return value['source']
    if isinstance(value.get('source'),dict):return value['source'].get('platform')
    if value.get('app',{}).get('source_platform') in {'ios','android'}:return value['app']['source_platform']
    return None


def source_kind(argv):
    # An explicit target operation remains target-only in an iOS migration.
    for key in ('--platform','--device','--target'):
        value=canonical._option(argv,key)
        if value in {'android','ios'}:return value
    if argv and argv[0] in {'android','ios'}:return argv[0]
    candidates=[]
    for key in ('--tree','--fact-tree','--factree'):
        value=canonical._option(argv,key)
        if value:candidates.append(Path(value))
    project=canonical._project_for(argv)
    candidates += [project/'spec/toolkit-fact-tree.json',project/'.migbot/config.json']
    candidates += [p/'.migbot/config.json' for p in (Path.cwd(),*Path.cwd().parents)]
    candidates += [Path(x) for x in argv if not x.startswith('-') and x.endswith('.json')]
    for path in candidates:
        if path.is_file():
            value=read_json(path)
            result=_kind(value)
            if result:return result
    if os.environ.get('HMIGBOT_IOS_SESSION'):return 'ios'
    return None


def _session(argv):
    from .xcode_ui import XcodeUISession
    value=canonical._option(argv,'--native-session',os.environ.get('HMIGBOT_IOS_SESSION'))
    if not value:raise MigrationError('iOS source action needs --native-session or HMIGBOT_IOS_SESSION')
    return XcodeUISession.open(value)


def _collection_recheck(tree,project,before):
    current=canonical._source_current(tree,project,allow_manifest_collection=True)
    key='native_blackbox_source_inputs_sha256'
    if (current or {}).get(key)!=(before or {}).get(key):
        raise canonical.BindingError('Native classification inputs changed while collecting the observation',22)
    return current


def native_whereami(argv):
    from .native_visual import arrival,identities_from_tree,live_page_queries
    parser=argparse.ArgumentParser(description='Native iOS page identity using public XCTest observations')
    parser.add_argument('--expect',required=True);parser.add_argument('--wait',type=float,default=0)
    parser.add_argument('--dir',default='spec/visual-verify/edgewalk');parser.add_argument('--tree',default='spec/toolkit-fact-tree.json')
    parser.add_argument('--native-session',default=os.environ.get('HMIGBOT_IOS_SESSION'))
    args=parser.parse_args(argv)
    if args.wait<0 or args.wait>300:raise MigrationError('Native arrival wait must be between 0 and 300 seconds')
    tree=read_json(Path(args.tree));project=canonical._project_for(['--tree',args.tree])
    collection=canonical._source_current(tree,project,allow_manifest_collection=True)
    observer=_session(argv)
    if tree.get('app',{}).get('package')!=observer.state['bundle_id']:
        raise MigrationError('Native source tree bundle does not match the owned observer')
    started=time.monotonic();deadline=started+args.wait
    identities=identities_from_tree(tree);scope=identities.get(args.expect,{}).get('scope','app')
    while True:
        collection=_collection_recheck(tree,project,collection)
        raw=observer.capture(Path(args.dir)/'identity_observations',scope=scope)
        result=arrival(raw['observation'],args.expect,identities,live_page_queries(observer,raw['observation'],identities))
        if result['arrived'] or time.monotonic()>=deadline:break
        time.sleep(min(.2,max(0,deadline-time.monotonic())))
    collection=_collection_recheck(tree,project,collection)
    print(json.dumps({'match':result['arrived'],'hits':result['matched_pages'],
        'why':result['blockers'],'weak':False,'waited_s':time.monotonic()-started,
        'source_platform':'ios','identity':result,'native_json':raw['native_json'],'png':raw['png'],
        **(collection or {})},ensure_ascii=False))
    return 0 if result['arrived'] else 15


def native_clickables(argv):
    from .native_visual import nodes,TYPE_NAMES,INTERACTIVE
    parser=argparse.ArgumentParser(description='Native iOS interactive candidates; actual XCUI identifiers and screen points')
    parser.add_argument('--grep');parser.add_argument('--rid',help='Historical locator spelling; value is a real native identifier')
    parser.add_argument('--all',action='store_true');parser.add_argument('--dir',default='spec/visual-verify/edgewalk')
    parser.add_argument('--tree',default='spec/toolkit-fact-tree.json')
    parser.add_argument('--scope',choices=['app','springboard'],default='app')
    parser.add_argument('--native-session',default=os.environ.get('HMIGBOT_IOS_SESSION'))
    args=parser.parse_args(argv);observer=_session(argv)
    collection=None
    if Path(args.tree).is_file():
        tree=read_json(Path(args.tree));project=canonical._project_for(['--tree',args.tree])
        collection=canonical._source_current(tree,project,allow_manifest_collection=True)
        if tree.get('app',{}).get('package')!=observer.state['bundle_id']:
            raise MigrationError('Native source tree bundle does not match the owned observer')
    raw=observer.capture(Path(args.dir)/'clickable_observations',scope=args.scope)
    if Path(args.tree).is_file():collection=_collection_recheck(tree,project,collection)
    result=[]
    for index,node in enumerate(nodes(raw['observation']['tree'])):
        if not node.get('exists') or node.get('element_type') not in INTERACTIVE:continue
        if args.rid and node.get('identifier')!=args.rid:continue
        if args.grep and args.grep not in str(node.get('label','')):continue
        result.append({'native_index':index,'native_type':node['element_type'],
                       'type':TYPE_NAMES.get(node['element_type'],str(node['element_type'])),
                       'identifier':node.get('identifier',''),'label':node.get('label',''),
                       'frame_points':node.get('frame'),'coordinate_space':'screen_points',
                       'enabled':node.get('enabled'),'hittable':node.get('hittable'),
                       'note':'Candidate only; use public find to establish unique existence/hittability before tap'})
    # No resource-id based deduplication: anonymous native controls remain distinct.
    print(json.dumps({'source_platform':'ios','count':len(result),'elements':result,
                      'native_json':raw['native_json'],'png':raw['png'],**(collection or {})},ensure_ascii=False));return 0


def native_settle(argv,scripts):
    from .native_visual import capture_cli
    parser=argparse.ArgumentParser(description='Native source walk settle; capture failure codes are preserved')
    parser.add_argument('--dir',default=os.environ.get('VV_EDGEWALK_DIR','spec/visual-verify/edgewalk'))
    parser.add_argument('command',choices=['settle']);parser.add_argument('--node',required=True)
    parser.add_argument('--via',default='');parser.add_argument('--mode',default='walk')
    parser.add_argument('--tree',required=True);parser.add_argument('--trip',required=True)
    parser.add_argument('--pkg',required=True);parser.add_argument('--launcher',required=True)
    parser.add_argument('--project-root',default='.');parser.add_argument('--native-session',default=os.environ.get('HMIGBOT_IOS_SESSION'))
    args=parser.parse_args(argv);ew=Path(args.dir).resolve();ew.mkdir(parents=True,exist_ok=True)
    canonical._safe_name(args.node);canonical._safe_name(args.trip,'trip')
    tree=read_json(Path(args.tree));collection=canonical._source_current(tree,Path(args.project_root),allow_manifest_collection=True)
    plan=read_json(ew/'walk_plan.json')
    if args.node not in plan.get('targets',[]):raise MigrationError('Native settle node is absent from the current walk targets')
    path=ew/'ledger.json';before=canonical.sha(path) if path.is_file() else None
    ledger=read_json(path) if path.is_file() else {'t0':time.time(),'coldstarts':[],
        'settled':{},'targets':plan.get('targets',[])}
    staged=ew/'pending_shots'/('native-settle-'+uuid.uuid4().hex)
    command=[args.tree,'--page',args.node,'--trip',args.trip,'--pkg',args.pkg,'--launcher',args.launcher,
             '--project-root',args.project_root,'--shots-dir',str(staged),'--capture-only']
    if args.native_session:command+=['--native-session',args.native_session]
    start=time.monotonic();stdout=io.StringIO()
    with redirect_stdout(stdout):code=capture_cli(command)
    if code:
        print(stdout.getvalue(),end='');return code
    try:meta=json.loads(stdout.getvalue())
    except ValueError as exc:raise MigrationError('Native capture did not return its actual JSON metadata') from exc
    canonical.capture_pair(meta)
    collection=_collection_recheck(tree,Path(args.project_root),collection)
    if meta.get('page_id')!=args.node:raise MigrationError('Native capture returned the wrong page metadata')
    page=next((p for p in canonical.page_records(tree) if p.get('id')==args.node),{})
    collection_pending=(collection or {}).get('native_classification_status')=='pending_rematerialization'
    if collection_pending and page.get('type')=='PageVariant' and page.get('source')=='blackbox_discovery':
        print(json.dumps({'status':'stale_classification','reason':'native_manifest_growth','exit_code':22,
            'coverage_credited':False,'capture_meta':meta,'source_platform':'ios'},ensure_ascii=False));return 22
    if (canonical.sha(path) if path.is_file() else None)!=before:
        raise MigrationError('Native walk ledger changed while capturing')
    shots=ew/'shots';shots.mkdir(exist_ok=True)
    prior=ledger.get('settled',{}).get(args.node)
    prior_trip=(prior or {}).get('trip') or (prior or {}).get('capture_meta',{}).get('trip') or (prior or {}).get('capture_meta',{}).get('trip_id')
    archived=None
    if prior and prior_trip and prior_trip!=args.trip:
        canonical._safe_name(prior_trip,'trip');archive=shots/'_bytrip'/prior_trip;archive.mkdir(parents=True,exist_ok=True)
        old=copy.deepcopy(prior);old_meta=old.get('capture_meta',{})
        for key in ('shot_path','dump_path'):
            if not old_meta.get(key):raise MigrationError('Previous trip capture lacks its paired artifact')
            source=Path(old_meta[key]);target=archive/source.name
            if target.exists() and canonical.sha(target)!=canonical.sha(source):
                raise MigrationError('Archived native trip evidence would be overwritten')
            if not target.exists():shutil.copy2(source,target)
            old_meta[key]=str(target)
        old_meta['shots_archived']={'dir':str(archive)}
        ledger.setdefault('settled_by_trip',{}).setdefault(prior_trip,{})[args.node]=old
        archived={'trip':prior_trip,'dir':str(archive)}
    for key,suffix in (('shot_path','.png'),('dump_path','.ios.xml')):
        target=shots/(args.node+suffix);shutil.copy2(meta[key],target);meta[key]=str(target)
    meta['trip']=args.trip;meta['trip_id']=args.trip
    meta['reach_path']=meta.get('reach_path') or ([args.via] if args.via else [])
    if not meta['reach_path']:raise MigrationError('Native settle requires its actual nonempty --via or capture reach path')
    write_json(shots/(args.node+'.capture.json'),meta)
    row={'via':args.via,'mode':args.mode,'capture':'verified','capture_meta':meta,
         'activity':None,'source_platform':'ios','native_identity':meta['arrival'],
         'native_classification_status':(collection or {}).get('native_classification_status'),'coverage_credited':False,
         'trip':args.trip,'at':round(time.time()-ledger['t0'],1),
         'cost_s':round(time.monotonic()-start,1),'coldstart_idx':len(ledger.get('coldstarts',[]))}
    if archived:row['archived_prior']=archived
    ledger.setdefault('settled',{})[args.node]=row;write_json(path,ledger)
    print(json.dumps({'settled':args.node,'trip':args.trip,'source_platform':'ios','coverage_credited':False,
                      **(collection or {}),
                      'capture_meta':meta,'left':[x for x in ledger['targets'] if x not in ledger['settled']]},ensure_ascii=False));return 0


def _target_explicit(argv):
    if argv and argv[0] in {'harmony','harmonyos','hmos'}:return True
    return any(canonical._option(argv,key) in {'harmony','harmonyos','hmos'} for key in ('--platform','--device','--target'))


def run(command,argv,scripts):
    from .compiled_runtime import run as original
    try:
        kind=source_kind(argv)
        if command in {'extract_dialog_ids','enrich_factree_anchors'} and kind=='ios':
            from .native_visual_prepare import catalog_cli,enrich_cli
            return catalog_cli(argv) if command=='extract_dialog_ids' else enrich_cli(argv,scripts)
        if command in {'check_prereq_freshness','check_functional_dimension'} and kind=='ios':
            from .visual_prerequisites import run as prerequisites
            return prerequisites(command,argv,scripts)
        if command=='check_dimension_prereqs' and kind=='ios':
            from .visual_prerequisites import dimensions
            return dimensions(argv,scripts)
        if command=='check_ios_screenshot':
            if kind!='ios':raise MigrationError('check_ios_screenshot requires an iOS canonical tree/project')
            return canonical.data_cli('check_android_screenshot',argv,scripts)
        if command=='run_phase2_ios_survey':
            guidance=('Native Phase 2 survey is orchestrated by the LLM with the owned Xcode observer: '
                'use python -m hmigbot_ios152.xcode_ui command/capture, then capture_page_e2e.py, '
                'walk_ledger.py settle and walk_finalize.py. Follow references/native-xcode-source.md. '
                'The opaque Android survey is not run for this native entry.')
            if '--help' in argv or '-h' in argv:print(guidance);return 0
            raise MigrationError(guidance)
        if command in TARGET_DEVICE:
            if command=='replay_exec' and kind=='ios':return canonical.replay_exec_cli(argv,scripts)
            return original(command,argv,scripts)
        if command in SOURCE_DEVICE:
            if _target_explicit(argv):return original(command,argv,scripts)
            if kind=='android':return original(command,argv,scripts)
            if command=='capture_page_e2e':
                from .native_visual import capture_cli
                return capture_cli(argv)
            if command=='walk_whereami':return native_whereami(argv)
            if command=='walk_clickables':return native_clickables(argv)
            raise MigrationError('Native source step '+command+' requires LLM orchestration with the public Xcode observer; '
                'use python -m hmigbot_ios152.xcode_ui command/capture, then native capture/ledger. This opaque Android action is not executed.')
        if command not in DATA:raise MigrationError('Unclassified opaque visual entry is not safe to dispatch: '+command)
        if command=='walk_ledger' and kind is None and 'settle' in argv:
            raise MigrationError('Source platform is unknown; refusing an opaque device settle')
        if kind!='ios':return original(command,argv,scripts)
        if command in {'build_page_queue','build_batches'} and canonical._active_mirror() is None:
            from .native_file_mapping import queue_cli,batches_cli
            return queue_cli(argv,scripts) if command=='build_page_queue' else batches_cli(argv,scripts)
        if command=='walk_ledger':
            action=next((x for x in argv if x in {'settle','coldstart','status','report','bind-from-evidence'}),None)
            if action=='settle':return native_settle(argv,scripts)
            if action=='bind-from-evidence':raise MigrationError('Native binding needs real snapshot identity reclassification; Android Activity binding is unsupported')
            return original(command,argv,scripts)
        if command=='compile_replay_plan':return canonical.compile_replay_cli(argv,scripts)
        if command=='walk_place_baselines':return canonical.place_baselines_cli(argv,scripts)
        if command=='walk_finalize':return canonical.finalize_cli(argv,scripts)
        if command in {'writeback_walk','materialize_blackbox_to_factree'}:return canonical.tree_write_cli(command,argv,scripts)
        if command=='walk_inherit':return canonical.inherit_cli(argv,scripts)
        if command=='assert_round_complete':return canonical.round_aggregate_cli(argv,scripts)
        if command in {'assert_replay_artifacts','assert_gap_ticket_coverage','assert_evidence_channel'}:
            return canonical.target_gate_cli(command,argv,scripts)
        if command in SOURCE_DATA_BRIDGE:return canonical.data_cli(command,argv,scripts)
        return original(command,argv,scripts)
    except (MigrationError,OSError,ValueError,RuntimeError) as exc:
        print(json.dumps({'status':'error','source_platform':'ios','entry':command,'error':str(exc),
                          'note':'No verification success or round completion is implied'},ensure_ascii=False),file=sys.stderr)
        return getattr(exc,'code',2)
