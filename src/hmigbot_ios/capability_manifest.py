"""One authoritative static capability model for public and staged helpers."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

from .core import MigrationError, digest, json_bytes, safe_child, write_json
from .plan_contract import plan_units, profile, contract_revision
from .capability_contract import load_contract
from .capability_runtime import ClosureError, RuntimeEvidence, require
from .native_structural_evidence import EvidenceIndex


def derive(project):
    project=Path(project).resolve()
    plans,units=plan_units(project)
    contract=load_contract(project,plans,units,required=True)
    require(contract.get('capability_schema')==2,'capability-v2-required','v1 is reference-only',True)
    entries=contract['declarations']
    obligations={(item['path'],ident,path) for ident,item in units.items() if item['scope']=='product'
                 and re.fullmatch(r'(?:BASE:Base-[1-6]|SLICE:F\d+:3c)',ident)
                 for path in item['ownership'] if path.endswith('.ets')}
    require(obligations,'capability-obligations-empty')
    covered=set()
    for entry in entries:
        source,ident=entry['provider'].split('#')
        item=units[ident]
        identity=(item['path'],ident,entry['path'])
        require(identity in obligations,'capability-provider-not-obligation',entry['key'])
        covered.add(identity)
    require(covered==obligations,'capability-coverage-missing',','.join(sorted(p for _,_,p in obligations-covered)))
    pending=[e['key'] for e in entries if e['materialization']=='pending' or not safe_child(project,e['path']).is_file()]
    materialized=[e for e in entries if e['key'] not in pending]
    assembly_paths=[path for ident,item in units.items() if ident=='BASE:Base-6.5' and item['scope']=='product'
                    for path in item['ownership'] if path.endswith('.ets')]
    require(assembly_paths,'capability-assembly-obligation-missing')
    assembly_missing=[path for path in assembly_paths if not safe_child(project,path).is_file()]
    deferred=bool(assembly_missing or any(e['kind']=='runtime-slot' and e['key'] in pending for e in entries))
    if deferred:
        pending += ['assembly:'+path for path in assembly_missing]
        index=EvidenceIndex(project); runtime_slots=sum(e['kind']=='runtime-slot' for e in entries); registrations={}
    else:
        evidence=RuntimeEvidence(project,materialized,assembly_paths,contract['initialization'])
        index=evidence.index; runtime_slots=len(evidence.slots); registrations=evidence.registrations
    plan_hashes={path.relative_to(project).as_posix():digest(path.read_bytes()) for path in plans}
    source_hashes={source.relative:digest(source.path.read_bytes()) for source in index.sources}
    source_hashes.update(registrations)
    for path in [project/'build-profile.json5',*[root.parent/'module.json5' for root in index.source_roots]]:
        source_hashes[path.relative_to(project).as_posix()]=digest(path.read_bytes())
    return {'capability_schema':2,'input_digest':digest(json_bytes({'contract':contract,'plans':plan_hashes,'tool_contract_revision':contract_revision(project)})),
            'source_digest':digest(json_bytes(source_hashes)),'plans':plan_hashes,'source_evidence':source_hashes,
            'declarations':entries,'initialization':contract['initialization'],'pending':pending,
            'counts':{'obligation_paths':len(obligations),'declarations':len(entries),'runtime_slots':runtime_slots,
                      'pending':len(pending)},'runtime_verified':False,'verification':'pending canonical source evidence' if deferred else 'reviewed static obligations only'}


def report(manifest, findings):
    return {'passed':not findings,'summary':{'FAIL':len(findings),'WARN':0},'findings':findings,
            'input_digest':manifest.get('input_digest'),'source_digest':manifest.get('source_digest'),
            'counts':manifest.get('counts',{}),'runtime_verified':False}


def main(kind='gate', legacy=None, argv=None):
    arguments=list(sys.argv[1:] if argv is None else argv)
    probe=argparse.ArgumentParser(add_help=False)
    probe.add_argument('--project-root',type=Path,default=Path.cwd())
    known,_=probe.parse_known_args(arguments)
    # Legacy is intentionally the unchanged process protocol, including help.
    if '-h' in arguments or '--help' in arguments or profile(known.project_root)<2:
        if legacy is None: return 2
        from .portable_helper import run
        return run(legacy, arguments).returncode
    parser=argparse.ArgumentParser()
    parser.add_argument('--project-root',type=Path,default=Path.cwd())
    parser.add_argument('--output-json',type=Path)
    if kind=='gen': parser.add_argument('--emit-interface',type=Path)
    args=parser.parse_args(arguments)
    project=args.project_root.resolve(); manifest={}
    try:
        if kind=='gen' and args.emit_interface:
            raise ClosureError('capability-emit-interface-unsupported','product writes require a reviewed owner',True)
        manifest=derive(project)
        findings=[]
        if kind=='gate':
            if manifest['pending']:
                findings.append({'kind':'capability-not-materialized','severity':'FAIL','keys':manifest['pending']})
            original=project/'spec/execution/capability-manifest.json'
            if original.is_file():
                old=json.loads(original.read_text(encoding='utf-8-sig'))
                if not isinstance(old,dict) or old.get('input_digest')!=manifest['input_digest'] or old.get('source_digest')!=manifest['source_digest']:
                    findings.append({'kind':'capability-digest-mismatch','severity':'FAIL'})
            result=report(manifest,findings)
        else: result=manifest
        if args.output_json:
            write_json(args.output_json,result)
        elif kind=='gen':
            write_json(project/'spec/execution/capability-manifest.json',result)
        print(json.dumps(result,ensure_ascii=False))
        return 1 if kind=='gate' and findings else 0
    except (MigrationError,ValueError,OSError) as exc:
        finding={'kind':getattr(exc,'code',str(exc).split(':')[0]),'severity':'FAIL','detail':str(exc)}
        result=report(manifest,[finding]); result['unsupported']=getattr(exc,'unsupported',False)
        if args.output_json: write_json(args.output_json,result)
        print(json.dumps(result,ensure_ascii=False))
        if getattr(exc,'unsupported',False) or 'invalid' in str(exc) or 'unsupported' in str(exc): return 2
        return 1
