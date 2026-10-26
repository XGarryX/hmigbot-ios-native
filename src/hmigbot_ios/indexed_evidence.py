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


def writeback(helper, argv):
    parser=argparse.ArgumentParser(add_help=False)
    parser.add_argument('manifest',nargs='?');parser.add_argument('--project-root',type=Path)
    args,_=parser.parse_known_args(argv)
    contract=None
    if args.project_root and args.manifest:
        project=args.project_root.resolve()
        path=project/'spec/execution/execution-contract.json'
        if path.exists():
            from .execution_bridge import prepare
            prepare(project)
            contract=read_json(path)
            manifest=Path(args.manifest)
            manifest=manifest if manifest.is_absolute() else Path.cwd()/manifest
            manifest=safe_child(project,manifest.resolve().relative_to(project).as_posix())
            if not manifest.is_relative_to(project/'spec/execution/writeback'):
                raise MigrationError('Indexed writeback must use the canonical execution writeback directory')
            raw=manifest.read_bytes();request=json.loads(raw)
    if contract is None:
        from .native_writeback import main
        return main(argv,helper=helper)
    from .native_writeback import preflight,postflight,run_helper,validate_summary
    checks,before,touched=preflight(project,request)
    result=run_helper(helper,argv,request,capture_output=True)
    _emit(sys.stdout,result.stdout);_emit(sys.stderr,result.stderr)
    if result.returncode or contract is None:
        return result.returncode
    dry='--dry-run' in argv
    validate_summary(result.stdout,request,dry=dry)
    postflight(project,checks,before,touched,dry=dry)
    if dry:return 0
    if manifest.read_bytes()!=raw:
        raise MigrationError('Writeback manifest changed during original apply')
    brief=request.get('brief',{})
    brief_path=safe_child(project,brief.get('path',''))
    if not brief_path.is_relative_to(project/'spec/execution/briefs') or brief_path.read_text(encoding='utf-8')!=brief.get('content'):
        raise MigrationError('Original writeback did not publish its exact declared brief')
    pages={n for key,values in request.get('ui_manifest',{}).items()
           if key in {'converted','verified'} for n in values}
    features={name for key,values in request.get('feature_index',{}).items() if key in {'implemented','verified'} for name in values}
    mode=request.get('mode');base=str(request.get('id','')).lstrip('0') or '0'
    records={}
    for ident,item in contract['plan_items'].items():
        selected=(ident.startswith('UI:') and set(item['page_ids'])&pages
                  or ident.startswith('SLICE:') and ident.split(':')[1] in features
                  or mode=='base' and ident==f'BASE:Base-{base}')
        if not selected or item['scope']!='product' or not item['ownership']:continue
        outputs={}
        for relative in item['ownership']:
            target=safe_child(project,relative)
            if not target.is_file():raise MigrationError('Writeback claimed an absent plan-owned output: '+relative)
            outputs[relative]=digest(target.read_bytes())
        records[ident]={'outputs':outputs,'ac_ids':item['ac_ids']}
    record={'schema_version':1,'contract_sha256':digest(path.read_bytes()),
        'source_sha256':contract['source_sha256'],'manifest':manifest.relative_to(project).as_posix(),
        'manifest_sha256':digest(raw),'brief':brief_path.relative_to(project).as_posix(),
        'brief_sha256':digest(brief_path.read_bytes()),'original_exit_code':result.returncode,
        'original_helper_sha256':digest(Path(helper).read_bytes()),'items':records,'behavior_verified':False}
    receipt=project/'spec/execution/receipts'/(digest(raw)+'.json')
    if receipt.exists() and read_json(receipt)!=record:
        raise MigrationError('Existing writeback receipt changed; retain original evidence and review the new target bytes')
    write_json(receipt,record)
    return 0


def generation(project, source_sha):
    from .execution_bridge import prepare
    try:
        prepare(project)
        path=project/'spec/execution/execution-contract.json';contract=read_json(path)
        if contract['source_sha256']!=source_sha:raise MigrationError('Indexed source changed')
        tasks=[{'id':ident,'ownership':item['ownership'],'plan_item_refs':[ident],
                'ac_ids':item['ac_ids']} for ident,item in contract['plan_items'].items() if item['scope']=='product']
        records={t['id']:{'status':'not_run','outputs':{}} for t in tasks}
        for receipt in sorted((project/'spec/execution/receipts').glob('*.json'),key=lambda p:p.stat().st_mtime_ns):
            r=read_json(receipt)
            if r.get('contract_sha256')!=digest(path.read_bytes()) or r.get('original_exit_code')!=0:
                raise MigrationError('Indexed receipt has a different contract or failed original apply')
            for key in ('manifest','brief'):
                if digest(safe_child(project,r[key]).read_bytes())!=r[key+'_sha256']:
                    raise MigrationError('Indexed writeback evidence changed: '+key)
            for ident,value in r['items'].items():
                if ident not in records or set(value['outputs'])!=set(contract['plan_items'][ident]['ownership']):
                    raise MigrationError('Indexed receipt output ownership differs from frozen plan')
                valid=all(digest(safe_child(project,p).read_bytes())==sha for p,sha in value['outputs'].items())
                records[ident]={'status':'generated' if valid else 'stale','outputs':value['outputs'],
                               'receipt':receipt.relative_to(project).as_posix()}
        states=[records[t['id']]['status'] for t in tasks if t['ownership']]
        from .page_evidence import combine
        return {'status':combine(states),'scope':'Successful original indexed writeback and current plan-owned bytes; compile/behavior separate'},tasks,records
    except (MigrationError,OSError,ValueError,KeyError,TypeError) as exc:
        return {'status':'stale','reason':str(exc)},[],{}
