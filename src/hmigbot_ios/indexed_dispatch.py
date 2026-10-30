"""Dispatch cooperation for the existing indexed execute workflow.

The host performs spawn/list/wait. This controller consumes its original trace,
checks frozen dependencies and outputs, and never writes the original ledgers.
"""
from __future__ import annotations
import argparse
from contextlib import contextmanager
import fcntl
import json
import os
from pathlib import Path
import re
import sys
import uuid

from .core import MigrationError, digest, json_bytes, source_snapshot
from .resource_merge import _project, _path, _raw, _atomic, _context

ROOT = 'spec/execution/indexed-dispatch'


def require(value, message):
    if not value:
        raise MigrationError(message)


def measured_start(project, key, metadata):
    try:
        from .execution_measurements import observe_start
        return observe_start(project,'execute',key,category='task',metadata=metadata)
    except Exception as exc:
        print('Dispatch measurement unavailable: '+str(exc),file=sys.stderr)
        return None


def measured_end(project, token, status):
    try:
        from .execution_measurements import observe_end
        observe_end(project,token,status,exit_code=0 if status=='returned' else None)
    except Exception as exc:
        print('Dispatch measurement unavailable: '+str(exc),file=sys.stderr)


@contextmanager
def locked(project):
    folder = _path(project, ROOT)
    folder.mkdir(parents=True, exist_ok=True)
    path = _path(project, ROOT + '/.lock')
    fd = os.open(path, os.O_RDWR | os.O_CREAT | getattr(os, 'O_NOFOLLOW', 0), 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        os.close(fd)


def host_trace():
    from .host_join import current_rollout, read_trace, native_bytes
    path = current_rollout()
    require(path is not None, 'Current native CODEX_THREAD_ID history is required; no self-reported host state')
    trace = read_trace(path, raw=native_bytes(path))
    require(not trace.invalid_lists or trace.last_full_list_call > trace.last_invalid_list_output,
            'Refresh a valid complete host agent list after its last error')
    return trace


def owner(ident):
    if ident.startswith('SLICE:'):
        return ':'.join(ident.split(':')[:2])
    return ident


def policy_from_plans(project, contract):
    policy = {'compile_policy': 'per-group', 'items': {}}
    seen = set()
    for relative in contract['plan_inputs']:
        if not relative.endswith('.md'):
            continue
        text = _raw(project, relative).decode('utf-8-sig')
        for block in re.findall(r'```json\s*\n(.*?)\n```', text, re.S):
            if '"dispatch_policy_version"' not in block:
                continue
            value = json.loads(block)
            if not isinstance(value, dict) or 'dispatch_policy_version' not in value:
                continue
            require(value['dispatch_policy_version'] == 1 and type(value['dispatch_policy_version']) is int,
                    'Unsupported frozen dispatch policy')
            require(not set(value) - {'dispatch_policy_version', 'compile_policy', 'items'}, 'Unknown dispatch policy fields')
            if 'compile_policy' in value:
                require(value['compile_policy'] in {'per-group', 'stage3-pilot'}, 'Invalid compile policy')
                require('compile' not in seen, 'Compile policy must have one frozen authority')
                seen.add('compile');policy['compile_policy'] = value['compile_policy']
            for item in value.get('items', []):
                ident = item['item_id']
                require(ident in contract['plan_items'] and ident not in policy['items'], 'Unknown/duplicate dispatch policy item')
                require(not set(item) - {'item_id', 'checkpoint', 'reads'}, 'Unknown item dispatch fields')
                require(contract['plan_items'][ident]['path'] == relative, 'Dispatch policy must be in its own reviewed plan')
                cp = item.get('checkpoint', '')
                require(not cp or isinstance(cp, str) and re.fullmatch(r'[A-Za-z0-9_-]+', cp), 'Invalid checkpoint')
                for read in item.get('reads', []):
                    require(isinstance(read, dict) and set(read) == {'path', 'producer'}, 'Invalid required target input')
                    _path(project, read['path'])
                    producer = contract['plan_items'].get(read['producer'])
                    require(producer and read['path'] in producer['ownership'], 'Read input must have a frozen producer')
                    require(read['producer'] in contract['plan_items'][ident]['parents'], 'Read input cannot erase an undeclared dependency')
                policy['items'][ident] = item
    return policy


def catalog(project, contract):
    policy = policy_from_plans(project, contract)
    jobs = {}
    for ident, item in contract['plan_items'].items():
        if item['scope'] != 'product' or ident.startswith('FV:'):
            continue
        key = owner(ident)
        phase = {'UI': 'ui', 'BASE': 'base', 'SLICE': 'slice'}[ident.split(':')[0]]
        job = jobs.setdefault(key, {'phase': phase, 'items': [], 'ownership': [], 'parents': [], 'reads': [],
                                    'checkpoint': key.replace(':', '-'), 'closer_writes': []})
        job['items'].append(ident);job['ownership'] += item['ownership']
        job['parents'] += item['parents']
        if ident.endswith(':3d'):
            job['closer_writes'] += item['ownership']
        specific = policy['items'].get(ident, {})
        if specific.get('checkpoint'):
            prior = job.get('specified_checkpoint')
            require(prior in (None, specific['checkpoint']), 'Slice parts disagree about their closer checkpoint')
            job['checkpoint'] = job['specified_checkpoint'] = specific['checkpoint']
        job['reads'] += specific.get('reads', [])
    for key, job in jobs.items():
        job['items'] = sorted(job['items'])
        job['ownership'] = sorted(set(job['ownership']))
        job['parents'] = sorted(set(job['parents']) - set(job['items']))
        job['closer_writes'] = sorted(set(job['closer_writes']))
        job['reads'] = sorted(job['reads'], key=lambda r:(r['producer'],r['path']))
        # A batch name is read from the existing reviewed UI table/heading.
        if job['phase'] == 'ui' and not job.get('specified_checkpoint'):
            item = contract['plan_items'][job['items'][0]]
            text = _raw(project, item['path']).decode('utf-8-sig')
            current, batches = None, []
            short = job['items'][0].split(':', 1)[1]
            for line in text.splitlines():
                match = re.match(r'^##\s+Batch\s+([A-Za-z0-9_-]+)\b', line)
                if match:current = 'batch-' + match[1]
                elif line.startswith('## '):current = None
                if current and line.lstrip().startswith('|') and short in [s.strip(' `') for s in line.split('|')]:
                    batches.append(current)
            require(len(batches) == 1, 'UI item must belong to one reviewed Batch: ' + key)
            job['checkpoint'] = batches[0]
    return jobs, policy['compile_policy']


def load(project):
    raw = _raw(project, ROOT + '/state.json')
    state = json.loads(raw)
    binding, contract = _context(project)
    require(state['binding'] == binding, 'Dispatch inputs changed; keep evidence and reviewed replan')
    return state, contract


def initialize(project, *, usage_ledger=None, usage_run_id=None, trace=None):
    project = _project(project);trace = trace or host_trace()
    require((usage_ledger is None) == (usage_run_id is None), 'Both usage ledger and run id are required')
    with locked(project):
        binding, contract = _context(project)
        jobs, compile_policy = catalog(project, contract)
        if _raw(project, ROOT+'/state.json', missing=True) is not None:
            state, _ = load(project)
            require(state['dispatcher'] == trace.meta['id'], 'Continue in the original dispatcher; do not borrow old handles')
            return {'status':'existing','jobs':len(state['jobs']),'compile_policy':state['compile_policy']}
        nonce = uuid.uuid4().hex[:10]
        for key, job in jobs.items():
            job.update(status='pending', task_name='indexed_'+nonce+'_'+digest(key.encode())[:10], outputs={})
            if job['ownership']:
                expected = {'join_point':'indexed-dispatch', 'task_names':[job['task_name']],
                    'artifacts':[{'path':p,'min_count':1,'min_bytes':1,'json':p.endswith('.json')} for p in job['ownership']]}
                job['expected_set'] = 'spec/a2h/_work/expected_'+job['task_name']+'.json'
                _atomic(project, job['expected_set'], json_bytes(expected))
        state = {'schema_version':1,'binding':binding,'dispatcher':trace.meta['id'],'agent_path':trace.scope,
                 'compile_policy':compile_policy,'jobs':jobs,'builds':{},'checkpoints':{},'empty_returns':0,
                 'usage_ledger':str(usage_ledger) if usage_ledger else None,'usage_run_id':usage_run_id}
        _atomic(project, ROOT+'/state.json', json_bytes(state))
        return {'status':'initialized','jobs':len(jobs),'compile_policy':compile_policy}


def assert_dispatcher(state, trace):
    require(state['dispatcher'] == trace.meta['id'] and state['agent_path'] == trace.scope,
            'Native host history belongs to another dispatcher')


def current_outputs(project, job):
    result = {}
    for path in job['ownership']:
        raw = _raw(project,path)
        require(raw, 'Missing/empty planned output: '+path)
        if path.endswith('.json'):json.loads(raw)
        result[path] = digest(raw)
    return result


def base7_ready(state):
    job=state['jobs'].get('BASE:Base-7')
    return bool(job and 'base7' in state['builds'] and job['status']=='closed' and
                job['checkpoint'] in state['checkpoints'])


def stable_parent(project, state, contract, parent, consumer):
    key = owner(parent)
    upstream = state['jobs'].get(key)
    if not upstream:return False
    if upstream['status'] == 'closed':
        return current_outputs(project, upstream) == upstream['outputs']
    # Only target reads explicitly frozen in the plan can bypass a whole closer.
    reads = [r for r in consumer['reads'] if r['producer'] == parent]
    needed = set(contract['plan_items'][parent]['ownership'])
    if (upstream['status'] != 'returned' or not reads or not needed
            or {r['path'] for r in reads} != needed):return False
    if upstream['checkpoint']!=consumer['checkpoint']:
        # A later nonempty resource scope would capture preimages before this
        # group's closer appends to the same JSON. Do not create stale work.
        from .resource_merge import _state, ROOT as RESOURCE_ROOT
        empty_scope=False
        directory=_path(project,RESOURCE_ROOT)
        if directory.is_dir():
            for path in directory.glob('*/scope.json'):
                value=json.loads(_raw(project,path.relative_to(project).as_posix()));manifest=value.get('manifest',{})
                if manifest.get('resources')==[] and any(t.get('task_id')==consumer['task_name'] and
                    set(t.get('plan_item_ids',[]))>=set(consumer['items']) for t in manifest.get('tasks',[])):
                    _state(project,path.parent.name)
                    empty_scope=True
        if not empty_scope:return False
    if needed & set(upstream['closer_writes']):return False
    if any(needed & set(job['ownership']) for other,job in state['jobs'].items()
           if other != key and job['status'] in {'pending','active','returned'}):return False
    return all(digest(_raw(project,p)) == upstream['outputs'].get(p) for p in needed)


def next_jobs(project, phase, *, capacity, checkpoint=None, trace=None):
    project=_project(project);state,contract=load(project);trace=trace or host_trace();assert_dispatcher(state,trace)
    require(type(capacity) is int and capacity>0, 'Use the actual positive host capacity')
    require(trace.last_full_list_call >= trace.last_spawn_output and trace.last_full_list_call >= 0,
            'Refresh the complete native host list before choosing free slots')
    relevant_failures=[f for f in trace.failed_spawns if f['requested_task'] in {
        trace.scope+'/'+j['task_name'] for j in state['jobs'].values() if j['status']=='pending'}]
    for failure in relevant_failures:
        offset=0;failure_offset=trace.source_bytes
        for line in trace.source_data.splitlines(keepends=True):
            offset+=len(line);row=json.loads(line)
            payload=row.get('payload',{})
            if payload.get('type')=='function_call_output' and payload.get('call_id')==failure['call_id']:
                failure_offset=offset
        if ('limit' not in failure['error'].lower() or trace.last_full_list_call<=failure_offset or
                not any(e['observed_bytes']>failure_offset for e in trace.completion_evidence.values())):
            return {'status':'host_dispatch_blocked','dispatch':[],'original_error':failure['error'],
                    'recovery':'Wait for a real host capacity change or repair the original dispatch error; do not busy retry'}
    if state['usage_ledger']:
        from .usage_budget import check_for_dispatch
        budget=check_for_dispatch(state['usage_ledger'],run_id=state['usage_run_id'],project_root=project)
        if not budget['can_continue']:
            return {'status':'budget_exhausted','dispatch':[],'reasons':budget['reasons'],'reclaim_allowed':True}
    active = {full for full,value in trace.status.items() if full != trace.scope
              and value in ('running','pending','control_pending')}
    active |= {full for full in trace.handles if full not in trace.completed
               and trace.status.get(full) not in ('idle','errored','interrupted','killed')}
    # Degrade after empty returns without guessing that a running task is dead.
    effective=max(1,capacity-state['empty_returns'])
    available=max(0,effective-len(active))
    selected=[];blocked={};writes=set();reads=set()
    if phase=='ui':
        pending_cps=[j['checkpoint'] for j in state['jobs'].values() if j['phase']=='ui' and j['status']!='closed']
        if pending_cps:
            first=sorted(set(pending_cps),key=lambda s:[int(p) if p.isdigit() else p for p in re.split(r'(\d+)',s)])[0]
            require(checkpoint in (None,first),'Do not open a later UI batch before the current batch writeback')
            checkpoint=first
    for job in state['jobs'].values():
        if job['status'] in {'active','stopped'}:writes.update(job['ownership']);reads.update(r['path'] for r in job['reads'])
    for key,job in sorted(state['jobs'].items()):
        if job['phase']!=phase or job['status']!='pending' or checkpoint and job['checkpoint']!=checkpoint:continue
        reasons=[]
        if phase=='base' and any(j['phase']=='ui' and j['status']!='closed' for j in state['jobs'].values()):
            reasons.append('UI batches have not finished their original closer/writeback')
        if key=='BASE:Base-7':reasons.append('Base-7 uses the real build-report gate, not a worker')
        if phase=='slice' and not base7_ready(state):reasons.append('Base-7 real build and original closer/writeback are not both complete')
        for parent in job['parents']:
            if parent=='BASE:Base-7' and base7_ready(state):continue
            if not stable_parent(project,state,contract,parent,job):reasons.append('unstable dependency '+parent)
        owned=set(job['ownership']);needed={r['path'] for r in job['reads']}
        if owned & (writes|reads) or needed & writes:reasons.append('active file ownership/read conflict')
        if not job['ownership']:reasons.append('No generated outputs; run the declared original gate')
        if reasons:blocked[key]=reasons;continue
        if len(selected)<available:
            selected.append({'job':key,**job});writes.update(owned);reads.update(needed)
    return {'status':'ready' if selected else 'waiting','dispatch':selected,'blocked':blocked,
            'capacity':capacity,'effective_capacity':effective,'in_flight':len(active),'available':available,
            'compile_policy':state['compile_policy']}


def bind(project, key, *, trace=None):
    project=_project(project);trace=trace or host_trace()
    with locked(project):
        state,contract=load(project);assert_dispatcher(state,trace);job=state['jobs'][key]
        full=trace.scope+'/'+job['task_name']
        require(full in trace.handles,'Task has no actual native spawn result')
        if job['status']=='active':return {'status':'active','job':key,'task':full}
        require(job['status']=='pending','Task is not a fresh pending attempt')
        require(job['ownership'] and key!='BASE:Base-7','Run the original compile gate instead of a generated worker')
        if job['phase']=='base':
            require(not any(j['phase']=='ui' and j['status']!='closed' for j in state['jobs'].values()),'UI closer boundary is unfinished')
        if job['phase']=='slice':require(base7_ready(state),'Base-7 real build and original writeback are not both verified')
        # Recheck frozen dependencies even if the dispatcher's earlier suggestion was stale.
        for parent in job['parents']:
            require(parent=='BASE:Base-7' and base7_ready(state) or
                    stable_parent(project,state,contract,parent,job),'Dependency changed before actual spawn binding: '+parent)
        for other,part in state['jobs'].items():
            if other!=key and part['status'] in {'active','stopped'}:
                require(not set(part['ownership']) & (set(job['ownership'])|{r['path'] for r in job['reads']}),
                        'Actual spawn conflicts with another active writer')
                require(not set(job['ownership']) & {r['path'] for r in part['reads']},'Actual spawn would mutate a reader input')
        job.update(status='active',task=full,measurement=measured_start(project,key,
            {'phase':job['phase'],'checkpoint':job['checkpoint'],'task':full}))
        job['read_hashes']={r['path']:digest(_raw(project,r['path'])) for r in job['reads']}
        _atomic(project,ROOT+'/state.json',json_bytes(state))
        return {'status':'active','job':key,'task':full,'host_bytes':trace.source_bytes}


def observe(project, *, trace=None):
    project=_project(project);trace=trace or host_trace()
    with locked(project):
        state,_=load(project);assert_dispatcher(state,trace);results={}
        from .host_join import contracts, artifact_gaps
        expected,errors=contracts(project,'indexed-dispatch');require(not errors,'Expected artifact contracts are invalid')
        for key,job in state['jobs'].items():
            if job['status']!='active':continue
            full=job['task']
            if full in trace.completed:
                gaps=artifact_gaps(project,job['task_name'],expected,require_declaration=True)
                if gaps:
                    job['status']='stopped';state['empty_returns']+=1
                    measured_end(project,job.get('measurement'),'incomplete')
                    results[key]={'status':'incomplete','gaps':gaps};continue
                require(all(digest(_raw(project,p))==sha for p,sha in job.get('read_hashes',{}).items()),
                        'Worker read an input that changed during execution; keep failure and revalidate: '+key)
                job.update(outputs=current_outputs(project,job),status='returned',
                           completion=trace.completion_evidence[full],host_sha256=trace.source_sha256)
                measured_end(project,job.get('measurement'),'returned')
                results[key]={'status':'returned','outputs':job['outputs']}
            elif trace.status.get(full) in ('idle','errored','interrupted','killed') or full in trace.terminal_observations:
                # Do not free ownership or respawn until cessation is positively known.
                job['status']='stopped';state['empty_returns']+=1
                measured_end(project,job.get('measurement'),'stopped')
                results[key]={'status':'stopped','recovery':'Verify no child process writes; use a new reviewed attempt, never revive this task name'}
            else:results[key]={'status':'running_or_unobserved'}
        _atomic(project,ROOT+'/state.json',json_bytes(state))
        return {'status':'observed','jobs':results}


def checkpoint(project, name, receipt):
    project=_project(project)
    with locked(project):
        state,contract=load(project)
        relative=Path(receipt).as_posix()
        require(relative.startswith('spec/execution/receipts/') and relative.endswith('.json'),'Use the original indexed receipt path')
        raw=_raw(project,relative);proof=json.loads(raw)
        require(proof.get('contract_sha256')==state['binding']['execution_contract_sha256'] and
                proof.get('source_sha256')==contract['source_sha256'] and type(proof.get('original_exit_code')) is int and proof['original_exit_code']==0,
                'Writeback receipt is stale or failed')
        for field in ('manifest','brief'):
            require(digest(_raw(project,proof[field]))==proof[field+'_sha256'],'Original writeback evidence changed')
        selected={key:job for key,job in state['jobs'].items() if job['checkpoint']==name}
        require(selected and all(j['status'] in {'returned','closed'} for j in selected.values()),'Checkpoint still has unfinished tasks')
        from .indexed_evidence import _selected
        request=json.loads(_raw(project,proof['manifest']))
        requested=(pending_selection(project,name,request) if state['compile_policy']=='stage3-pilot' and
                   all(j['phase']=='slice' for j in selected.values()) else
                   {ident for ident,item in contract['plan_items'].items() if item['scope']=='product' and _selected(ident,item,request)})
        require(requested ==
                {ident for j in selected.values() for ident in j['items']},'Writeback selected a different checkpoint')
        if state['compile_policy']=='stage3-pilot' and all(j['phase']=='slice' for j in selected.values()):
            require(proof.get('generated_checkpoint')=={'name':name,'plan_item_ids':sorted(requested)},
                    'Original adapter receipt lacks this exact generated-only checkpoint binding')
        if any(j['phase']=='slice' for j in selected.values()) and state['compile_policy']=='per-group':
            require('group:'+name in state['builds'],'Per-group compilation is required by this frozen plan')
        elif any(j['phase']=='slice' for j in selected.values()):
            brief=_raw(project,proof['brief']).decode('utf-8-sig')
            require(re.search(r'(?m)^-?\s*final_state:\s*GENERATED_PENDING_COMPILE\s*$',brief) and
                    re.search(r'(?m)^-?\s*build_status:\s*deferred-to-stage3-gate\s*$',brief),
                    'Deferred group brief must say generated/pending compilation, never PASS')
            compile_section=re.search(r'(?m)^  compile:\s*\n((?:    [^\n]*\n?)+)',brief)
            require(compile_section and re.search(r'(?m)^    converged:\s*false\s*$',compile_section[1]) and
                    re.search(r'(?m)^    iterations:\s*0\s*$',compile_section[1]),
                    'Unrun compilation must keep converged=false and iterations=0')
        ids={i for j in selected.values() for i in j['items'] if contract['plan_items'][i]['ownership']}
        require(set(proof['items'])==ids,'Original receipt does not close this exact checkpoint')
        for key,job in selected.items():
            for ident in job['items']:
                if not contract['plan_items'][ident]['ownership']:continue
                require(proof['items'][ident]['outputs']=={p:digest(_raw(project,p)) for p in contract['plan_items'][ident]['ownership']},
                        'Original receipt outputs changed')
            job.update(status='closed',outputs=current_outputs(project,job))
        state['checkpoints'][name]={'path':relative,'sha256':digest(raw)}
        _atomic(project,ROOT+'/state.json',json_bytes(state))
        return {'status':'closed','checkpoint':name,'jobs':sorted(selected)}


def pending_selection(project, name, request):
    """Adapter-only item selection; it never manufactures progress mutations."""
    project=_project(project);state,_=load(project)
    require(state['compile_policy']=='stage3-pilot' and request.get('mode')=='group',
            'Generated-only checkpoint requires the frozen Stage 3 pilot')
    require(not request.get('ui_manifest') and not request.get('feature_index'),
            'Uncompiled generation cannot flip verified/implemented progress')
    jobs=[j for j in state['jobs'].values() if j['checkpoint']==name]
    require(jobs and all(j['phase']=='slice' and j['status'] in {'returned','closed'} for j in jobs),
            'Generated checkpoint still has unfinished slice workers')
    for job in jobs:
        current=current_outputs(project,job)
        require(all(current[p]==sha for p,sha in job['outputs'].items() if p not in job['closer_writes']),
                'Closer changed an already published worker interface')
    return {ident for j in jobs for ident in j['items']}


def record_build(project, gate, evidence):
    project=_project(project)
    with locked(project):
        state,contract=load(project)
        require(not any(j['status'] in {'active','stopped'} for j in state['jobs'].values()),'Build must not read active or unconfirmed stopped writer files')
        require(gate in {'base7','stage3'} or gate.startswith('group:'),'Final FV gates remain the original pipeline, not this dispatcher')
        if gate.startswith('group:'):
            relevant=[j for j in state['jobs'].values() if j['phase']=='slice' and j['checkpoint']==gate.split(':',1)[1]]
            allowed={'returned','closed'}
        else:
            relevant=([j for key,j in state['jobs'].items() if j['phase']=='base' and key!='BASE:Base-7']
                      if gate=='base7' else [j for j in state['jobs'].values() if j['phase']=='slice'])
            allowed={'closed'}
        require(relevant and all(j['status'] in allowed for j in relevant),'Finish relevant outputs before the build gate')
        require(all(current_outputs(project,j)==j['outputs'] for j in relevant),'Outputs changed since their observed completion')
        path=Path(evidence).resolve(strict=True)
        require(path.is_relative_to(project.parent/'.a2h-build-evidence') and path.name=='build.json', 'Use the actual build provider evidence')
        report=json.loads(path.read_bytes())
        require(report.get('status')=='build_passed' and type(report.get('exit_code')) is int and report.get('exit_code')==0 and
                report.get('target_project')==str(project) and report.get('source_sha256')==contract['source_sha256'] and
                report.get('source_changed') is False,'Build failed or has another project/source')
        from .quality_views import target_inputs
        require(report.get('target_input_hashes')==target_inputs(project),'Build inputs no longer match current target')
        diagnostics=json.loads((path.parent/report['diagnostics']['path']).read_bytes())
        require(digest((path.parent/report['diagnostics']['path']).read_bytes())==report['diagnostics']['sha256'] and
                diagnostics.get('build_command_passed') is True,'Compiler diagnostics are not a current success')
        logs=(path.parent/'stdout.log').read_bytes()+(path.parent/'stderr.log').read_bytes()
        require(report.get('hvigor_success_marker') is True and b'BUILD SUCCESSFUL' in logs,'Actual build success marker missing')
        require(report.get('artifacts'),'Build produced no HAP artifacts')
        for artifact in report['artifacts']:
            raw=_raw(project,artifact['path'])
            require(raw and digest(raw)==artifact['sha256'],'Build artifact changed or is empty')
        state['builds'][gate]={'evidence':str(path),'sha256':digest(path.read_bytes()),'target_inputs':report['target_input_hashes']}
        if gate=='base7' and 'BASE:Base-7' in state['jobs']:state['jobs']['BASE:Base-7']['status']='returned'
        _atomic(project,ROOT+'/state.json',json_bytes(state))
        return {'status':'build_verified','gate':gate,'final_fv_still_required':True}


def error_owners(project, diagnostics):
    project=_project(project);state,_=load(project);result=[]
    if isinstance(diagnostics,dict):diagnostics=diagnostics['findings']
    for finding in diagnostics:
        path=finding.get('path') or finding.get('file')
        if isinstance(path,str) and Path(path).is_absolute():
            try:path=Path(path).relative_to(project).as_posix()
            except ValueError:path=None
        owners=[key for key,j in state['jobs'].items() if path in j['ownership']]
        result.append({'finding':finding,'owners':owners,'resolution':'owned_task' if len(owners)==1 else 'shared_or_unknown_review',
                       'automatic_repair_allowed':len(owners)==1})
    return {'status':'classified','findings':result}


def status(project):
    project=_project(project);state,_=load(project)
    slices=[j for j in state['jobs'].values() if j['phase']=='slice']
    generated=bool(slices) and all(j['status']=='closed' for j in slices)
    compiled=(generated and ('stage3' in state['builds'] if state['compile_policy']=='stage3-pilot' else
                            all('group:'+j['checkpoint'] in state['builds'] for j in slices)))
    if compiled and state['compile_policy']=='stage3-pilot':
        from .indexed_compile_gate import current_stage3
        current_stage3(project)
    return {'status':'handoff_to_fv' if compiled else 'compile_pending' if generated else 'working',
            'jobs':state['jobs'],'builds':state['builds'],'checkpoints':state['checkpoints'],
            'final_structural_and_build_required':True,'behavior_verified':False}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='action',required=True)
    for name in ('init','next','bind','observe','checkpoint','build-report','errors','status'):
        p=sub.add_parser(name);p.add_argument('--project',type=Path,required=True)
        if name=='init':p.add_argument('--usage-ledger',type=Path);p.add_argument('--usage-run-id')
        elif name=='next':
            p.add_argument('--phase',choices=['ui','base','slice'],required=True);p.add_argument('--capacity',type=int,required=True);p.add_argument('--checkpoint')
        elif name=='bind':p.add_argument('--job',required=True)
        elif name=='checkpoint':p.add_argument('--name',required=True);p.add_argument('--receipt',required=True)
        elif name=='build-report':p.add_argument('--gate',required=True);p.add_argument('--evidence',type=Path,required=True)
        elif name=='errors':p.add_argument('--input',type=Path,required=True)
    args=parser.parse_args(argv)
    try:
        if args.action=='init':result=initialize(args.project,usage_ledger=args.usage_ledger,usage_run_id=args.usage_run_id)
        elif args.action=='next':result=next_jobs(args.project,args.phase,capacity=args.capacity,checkpoint=args.checkpoint)
        elif args.action=='bind':result=bind(args.project,args.job)
        elif args.action=='observe':result=observe(args.project)
        elif args.action=='checkpoint':result=checkpoint(args.project,args.name,args.receipt)
        elif args.action=='build-report':result=record_build(args.project,args.gate,args.evidence)
        elif args.action=='errors':result=error_owners(args.project,json.loads(args.input.read_bytes()))
        else:result=status(args.project)
        print(json.dumps(result,ensure_ascii=False,indent=2));return 0
    except (MigrationError,OSError,ValueError,KeyError,TypeError,AttributeError) as exc:
        print(json.dumps({'status':'blocked','error':str(exc),'recovery':'Keep original evidence; repair the current dependency or use a reviewed new attempt.'},ensure_ascii=False));return 2

if __name__=='__main__':raise SystemExit(main())
