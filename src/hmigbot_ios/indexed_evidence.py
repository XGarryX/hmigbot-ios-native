"""Observe successful Garry writeback without becoming another state writer."""
from pathlib import Path
import argparse
import json
import re
import sys

from .core import MigrationError, digest, json_bytes, read_json, safe_child, write_json
from .portable_helper import run


def _emit(stream, data):
    if hasattr(stream,'buffer'):stream.buffer.write(data);stream.buffer.flush()
    else:stream.write(data.decode('utf-8',errors='replace'))


def _deletion_intents(project, contract):
    """Consume the preimage checked by the frozen plan-ir producer.

    prepare() retains the source/plan/runtime guards. The blueprint is pinned by
    that indexed contract. Its original creation also checked and captured the
    pre-dispatch file bytes. Current absence or intent alone is not a preimage.
    """
    from .receipt_outputs import deletion_intent, regular_path
    path = regular_path(project, 'spec/blueprint/contracts.json')
    pinned = read_json(path)
    tasks = [task for task in pinned.get('ios_tasks', []) if task.get('deletions')]
    if not tasks:
        return {}
    blueprint_sha = digest(path.read_bytes())
    if (contract.get('plan_inputs', {}).get('spec/blueprint/contracts.json') != blueprint_sha
            or pinned.get('source_sha256') != contract.get('source_sha256')
            or not contract.get('contract_revision')
            or pinned.get('contract_revision') != contract['contract_revision']
            or pinned.get('spec_contract_version', 1) < 2
            or pinned.get('ios_adapter_version') != 2):
        raise MigrationError('Indexed deletion lacks the frozen plan preimage binding')
    proof = contract.get('deletion_preimages', {})
    if not isinstance(proof, dict) or set(proof) != {task['id'] for task in tasks}:
        raise MigrationError('Indexed deletion lacks its original pre-dispatch preimage evidence')
    result = {}
    for task in tasks:
        planned = deletion_intent(project, task)
        if contract.get('deletion_preimages', {}).get(task['id']) != planned:
            raise MigrationError('Indexed deletion lacks its original pre-dispatch preimage evidence')
        assigned = set()
        for ident in task.get('plan_item_refs', []):
            item = contract['plan_items'].get(ident)
            if item is None:
                raise MigrationError('Indexed deletion owner references an unknown plan item')
            deleted = {p: sha for p, sha in planned.items() if p in item['ownership']}
            if not deleted:
                continue
            if ident in result:
                raise MigrationError('Indexed deletion has ambiguous task ownership')
            assigned.update(deleted)
            result[ident] = {'files': deleted, 'source': {
                'owner_task': task['id'], 'blueprint_sha256': blueprint_sha,
                'contract_revision': contract['contract_revision']}}
        if assigned != set(planned):
            raise MigrationError('Frozen deletion has no indexed plan ownership')
    return result


def _absent(project, relative):
    import os
    from .receipt_outputs import regular_path
    # regular_path rejects links in every path component, including dangling
    # links; lexists also refuses files/directories appearing after deletion.
    if os.path.lexists(regular_path(project, relative)):
        raise MigrationError('Declared deleted output reappeared: ' + relative)


def _selected(ident, item, request):
    pages = {p for key, values in request.get('ui_manifest', {}).items()
             if key in {'converted', 'verified'} for p in values}
    features = {f for key, values in request.get('feature_index', {}).items()
                if key in {'implemented', 'verified'} for f in values}
    base = str(request.get('id', '')).lstrip('0') or '0'
    return (ident.startswith('UI:') and bool(set(item['page_ids']) & pages)
            or ident.startswith('SLICE:') and ident.split(':')[1] in features
            or request.get('mode') == 'base' and ident == f'BASE:Base-{base}')


def _resource_writeback(project, contract, request, scope, closer, selected_items=None):
    required = (contract.get('resource_protocol') == 'task-deltas-v1'
                and request.get('mode') in {'batch', 'group'})
    if not scope and not closer and not required:
        return None
    if not scope or not closer:
        raise MigrationError('Batch/group writeback requires --resource-scope and --resource-closer; merge all declared task deltas first')
    from .resource_merge import verify_merged
    merged = verify_merged(project, scope, closer)
    relative = 'spec/execution/resource-deltas/' + scope + '/scope.json'
    raw = safe_child(project, relative).read_bytes()
    if digest(raw) != merged['scope_sha256']:
        raise MigrationError('Resource scope changed during writeback preflight')
    manifest = json.loads(raw)['manifest']
    declared = {ident for task in manifest['tasks'] for ident in task['plan_item_ids']}
    selected = (set(selected_items) if selected_items is not None else
                {ident for ident, item in contract['plan_items'].items()
                 if item['scope'] == 'product' and _selected(ident, item, request)})
    if not selected or declared != selected:
        raise MigrationError('Resource scope plan items do not match this writeback selection')
    receipt_relative = 'spec/execution/resource-deltas/' + scope + '/merge-receipt.json'
    receipt_raw = safe_child(project, receipt_relative).read_bytes()
    if json.loads(receipt_raw) != merged:
        raise MigrationError('Resource merge receipt changed during writeback preflight')
    return {'scope': scope, 'closer_id': closer, 'scope_sha256': merged['scope_sha256'],
            'receipt': receipt_relative, 'receipt_sha256': digest(receipt_raw)}


def _writeback(helper, argv):
    resource_parser = argparse.ArgumentParser(add_help=False)
    resource_parser.add_argument('--resource-scope')
    resource_parser.add_argument('--resource-closer')
    resource_parser.add_argument('--generated-checkpoint')
    resource_args, argv = resource_parser.parse_known_args(argv)
    parser=argparse.ArgumentParser(add_help=False)
    parser.add_argument('manifest',nargs='?');parser.add_argument('--project-root',type=Path)
    args,_=parser.parse_known_args(argv)
    contract=None
    if args.project_root and args.manifest:
        project=args.project_root.resolve()
        path=project/'spec/execution/execution-contract.json'
        if path.exists():
            from .execution_bridge import prepare
            contract_raw = path.read_bytes()
            prepared = prepare(project)
            checked_raw = path.read_bytes()
            contract_sha = digest(contract_raw)
            if checked_raw != contract_raw or prepared.get('contract_sha256') != contract_sha:
                raise MigrationError('Indexed execution contract changed before/during preparation')
            contract=json.loads(checked_raw)
            manifest=Path(args.manifest)
            manifest=manifest if manifest.is_absolute() else Path.cwd()/manifest
            manifest=safe_child(project,manifest.resolve().relative_to(project).as_posix())
            if not manifest.is_relative_to(project/'spec/execution/writeback'):
                raise MigrationError('Indexed writeback must use the canonical execution writeback directory')
            raw=manifest.read_bytes();request=json.loads(raw)
    if contract is None:
        if resource_args.resource_scope or resource_args.resource_closer or resource_args.generated_checkpoint:
            raise MigrationError('Resource writeback requires the current indexed execution contract')
        from .native_writeback import main
        return main(argv,helper=helper)
    from .native_writeback import preflight,postflight,run_helper,validate_summary
    checks,before,touched=preflight(project,request)
    if resource_args.generated_checkpoint:
        from .indexed_dispatch import pending_selection
        selected = set(pending_selection(project, resource_args.generated_checkpoint, request))
    else:
        selected = {ident for ident, item in contract['plan_items'].items()
                    if item['scope'] == 'product' and _selected(ident, item, request)}
    resource_proof = _resource_writeback(project, contract, request,
                                        resource_args.resource_scope, resource_args.resource_closer, selected)
    from .ios_ui_delivery import verify_delivery
    for phase in ('generated', 'assembled'):
        delivered = verify_delivery(project, contract['plan_items'], selected, phase=phase)
        if delivered['status'] not in {'PASS', 'not_applicable'}:
            raise MigrationError('UI delivery is incomplete before original writeback: ' + json.dumps(delivered, ensure_ascii=False))
    intents = _deletion_intents(project, contract)
    for ident, item in contract['plan_items'].items():
        if ident in selected:
            for relative in intents.get(ident, {}).get('files', {}):
                _absent(project, relative)
    result=run_helper(helper,argv,request,capture_output=True)
    _emit(sys.stdout,result.stdout);_emit(sys.stderr,result.stderr)
    if result.returncode or contract is None:
        return result.returncode
    dry='--dry-run' in argv
    validate_summary(result.stdout,request,dry=dry)
    postflight(project,checks,before,touched,dry=dry)
    if dry:return 0
    if resource_proof != _resource_writeback(project, contract, request,
                                             resource_args.resource_scope, resource_args.resource_closer, selected):
        raise MigrationError('Resource merge proof changed during original writeback')
    if manifest.read_bytes()!=raw:
        raise MigrationError('Writeback manifest changed during original apply')
    brief=request.get('brief',{})
    brief_path=safe_child(project,brief.get('path',''))
    if not brief_path.is_relative_to(project/'spec/execution/briefs') or brief_path.read_text(encoding='utf-8')!=brief.get('content'):
        raise MigrationError('Original writeback did not publish its exact declared brief')
    records={}
    if resource_args.generated_checkpoint:
        if selected != set(pending_selection(project, resource_args.generated_checkpoint, request)):
            raise MigrationError('Generated checkpoint selection changed during original writeback')
    # The receipt binds the exact snapshot prepare validated, never a later hash.
    checked_raw = path.read_bytes()
    if checked_raw != contract_raw:
        raise MigrationError('Indexed execution contract changed during original apply')
    checked_contract = json.loads(checked_raw)
    if _deletion_intents(project, checked_contract) != intents:
        raise MigrationError('Indexed deletion binding changed during original apply')
    contract = checked_contract
    for ident,item in contract['plan_items'].items():
        if ident not in selected or item['scope']!='product' or not item['ownership']:continue
        deleted = intents.get(ident, {}).get('files', {})
        outputs={}
        for relative in item['ownership']:
            if relative in deleted:
                _absent(project, relative)
                continue
            target=safe_child(project,relative)
            if not target.is_file():raise MigrationError('Writeback claimed an absent plan-owned output: '+relative)
            outputs[relative]=digest(target.read_bytes())
        records[ident]={'outputs':outputs,'ac_ids':item['ac_ids']}
        if deleted:
            records[ident].update(deleted_files=deleted, deletion_source=intents[ident]['source'])
    record={'schema_version':1,'contract_sha256':contract_sha,
        'source_sha256':contract['source_sha256'],'manifest':manifest.relative_to(project).as_posix(),
        'manifest_sha256':digest(raw),'brief':brief_path.relative_to(project).as_posix(),
        'brief_sha256':digest(brief_path.read_bytes()),'original_exit_code':result.returncode,
        'original_helper_sha256':digest(Path(helper).read_bytes()),'items':records,'behavior_verified':False}
    if resource_proof is not None:
        record['resource_merge'] = resource_proof
    if resource_args.generated_checkpoint:
        record['generated_checkpoint'] = {'name': resource_args.generated_checkpoint,
                                          'plan_item_ids': sorted(selected)}
    receipt=project/'spec/execution/receipts'/(digest(raw)+'.json')
    if receipt.exists() and read_json(receipt)!=record:
        raise MigrationError('Existing writeback receipt changed; retain original evidence and review the new target bytes')
    if path.read_bytes() != contract_raw:
        raise MigrationError('Indexed execution contract changed before receipt publication')
    write_json(receipt,record)
    return 0


def writeback(helper, argv):
    """Time the real writer chain without changing its result or exception."""
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--project-root', type=Path)
    args, _ = parser.parse_known_args(argv)
    token = None
    if args.project_root:
        try:
            from .execution_measurements import observe_start
            token = observe_start(args.project_root, 'execute', 'apply-writeback', 'writeback')
        except (MigrationError, OSError, ValueError, TypeError, KeyError) as exc:
            print('Writeback measurement unavailable: ' + str(exc), file=sys.stderr)
    def measured_end(status, code):
        if token is not None:
            try:
                from .execution_measurements import observe_end
                observe_end(args.project_root, token, status, exit_code=code)
            except (MigrationError, OSError, ValueError, TypeError, KeyError) as exc:
                print('Writeback measurement unavailable: ' + str(exc), file=sys.stderr)
    try:
        code = _writeback(helper, argv)
    except BaseException:
        measured_end('failed', None)
        raise
    measured_end('completed' if code == 0 else 'failed', code)
    return code


def generation(project, source_sha):
    from .execution_bridge import prepare
    try:
        prepare(project)
        path=project/'spec/execution/execution-contract.json';contract=read_json(path)
        if contract['source_sha256']!=source_sha:raise MigrationError('Indexed source changed')
        tasks=[{'id':ident,'ownership':item['ownership'],'plan_item_refs':[ident],
                'ac_ids':item['ac_ids']} for ident,item in contract['plan_items'].items() if item['scope']=='product']
        records={t['id']:{'status':'not_run','outputs':{}} for t in tasks}
        intents = _deletion_intents(project, contract)
        for receipt in sorted((project/'spec/execution/receipts').glob('*.json'),key=lambda p:p.stat().st_mtime_ns):
            r=read_json(receipt)
            if r.get('contract_sha256')!=digest(path.read_bytes()) or r.get('original_exit_code')!=0:
                raise MigrationError('Indexed receipt has a different contract or failed original apply')
            for key in ('manifest','brief'):
                if digest(safe_child(project,r[key]).read_bytes())!=r[key+'_sha256']:
                    raise MigrationError('Indexed writeback evidence changed: '+key)
            for ident,value in r['items'].items():
                deleted = value.get('deleted_files', {})
                if (ident not in records or not isinstance(deleted, dict)
                        or set(value['outputs']) & set(deleted)
                        or set(value['outputs']) | set(deleted) != set(contract['plan_items'][ident]['ownership'])
                        or deleted != intents.get(ident, {}).get('files', {})):
                    raise MigrationError('Indexed receipt output/deletion ownership differs from frozen plan')
                if deleted and value.get('deletion_source') != intents[ident]['source']:
                    raise MigrationError('Indexed receipt deletion preimage binding changed')
                for relative in deleted:
                    _absent(project, relative)
                valid=all(digest(safe_child(project,p).read_bytes())==sha for p,sha in value['outputs'].items())
                records[ident]={'status':'generated' if valid else 'stale','outputs':value['outputs'],
                               'receipt':receipt.relative_to(project).as_posix()}
                if deleted:
                    records[ident]['deleted_files'] = deleted
        states=[records[t['id']]['status'] for t in tasks if t['ownership']]
        from .page_evidence import combine
        return {'status':combine(states),'scope':'Successful original indexed writeback and current plan-owned bytes; compile/behavior separate'},tasks,records
    except (MigrationError,OSError,ValueError,KeyError,TypeError) as exc:
        return {'status':'stale','reason':str(exc)},[],{}
