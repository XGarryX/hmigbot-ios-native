"""Actual CHECK-6 execution using the shipped router verifier's target engine.

iOS expectations are reviewed source facts, never the old Android extractor.
This adapter writes derived reports only and never repairs application code.
"""
import argparse
import json
import os
import re
from pathlib import Path
import subprocess
import sys
import uuid

from .core import MigrationError, digest, json_bytes, read_json, source_snapshot, write_json
from .receipt_outputs import regular_path

RUNTIME = Path(__file__).resolve().parents[2]
OUT = 'spec/verify/route'
EXPECTATIONS = 'spec/verification/ios-routing.json'
RESULT = OUT + '/ios-route-check.json'


def _bindings(project):
    from .native_pipeline import context
    from .quality_views import _summary_inputs, target_inputs
    source, _ = context(project)
    spec, baseline = _summary_inputs(project)
    contract = regular_path(project, 'spec/execution/execution-contract.json')
    expected = regular_path(project, EXPECTATIONS)
    producer = [Path(__file__), RUNTIME/'skills/arkts-router-verify/scripts/hmos_extract.py',
        RUNTIME/'skills/arkts-router-verify/scripts/hmos_reachability.py',
        RUNTIME/'vendor/hmigbot/skills/arkts-router-verify/scripts/bin/macos-arm64/_entry.dist/_entry.bin']
    graph = regular_path(project, 'spec/baseline/ios-facts.json')
    return source, {'source_sha256': source_snapshot(source)['sha256'],
        'config_sha256': digest(regular_path(project,'.migbot/config.json').read_bytes()),
        'graph_sha256': digest(graph.read_bytes()) if graph.is_file() else None,
        'spec_inputs': spec, 'target_inputs': target_inputs(project),
        'contract_sha256': digest(contract.read_bytes()) if contract.is_file() else None,
        'expectations_sha256': digest(expected.read_bytes()) if expected.is_file() else None,
        'producer': {str(p.relative_to(RUNTIME)): digest(p.read_bytes()) for p in producer if p.is_file()}}, baseline


def current(project):
    project = Path(project).resolve()
    try:
        _, binding, _ = _bindings(project)
        result = read_json(regular_path(project, RESULT))
        if result.get('binding') != binding:
            raise MigrationError('Routing inputs or checker changed')
        for item in result.get('evidence', []):
            if digest(regular_path(project, item['path']).read_bytes()) != item['sha256']:
                raise MigrationError('Routing evidence changed')
        return dict(result, actual_call_now=False, reused_current_evidence=True)
    except (MigrationError, OSError, ValueError, TypeError, KeyError) as exc:
        return {'status': 'DEFERRED', 'detail': 'not_run/current evidence unavailable: '+str(exc),
                'actual_call_now': False, 'runtime_verified': False}


def run(project):
    project = Path(project).resolve()
    source, binding, baseline = _bindings(project)
    run_dir = regular_path(project, OUT+'/runs/'+uuid.uuid4().hex)
    run_dir.mkdir(parents=True)
    helper = RUNTIME/'skills/arkts-router-verify/scripts/hmos_extract.py'
    command = [sys.executable, '-B', str(helper), '--hmos-root', str(project), '--out-dir', str(run_dir)]
    findings, gaps, evidence, calls = [], [], [], []
    code = None
    called = False
    def save(name, raw):
        path = run_dir/name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        evidence.append({'path': path.relative_to(project).as_posix(), 'sha256': digest(raw)})
    try:
        process = subprocess.run(command, cwd=project, capture_output=True, timeout=120, shell=False)
        called = True
        code = process.returncode
        calls.append({'command':command,'exit_code':code,'role':'target-edge-extraction'})
        save('stdout.log', process.stdout); save('stderr.log', process.stderr)
        if code != 0:
            raise MigrationError('Actual arkts-router-verify extractor failed with exit '+str(code))
        actual_path = regular_path(project, run_dir.relative_to(project).as_posix()+'/actual_nav.json')
        actual = read_json(actual_path)
        evidence.append({'path': actual_path.relative_to(project).as_posix(), 'sha256': digest(actual_path.read_bytes())})
        if not isinstance(actual.get('edges'), list):
            raise MigrationError('Router extractor returned no complete edge list')
        # The edge extractor's `registered` flag only models classic router
        # pages. Run the shipped registration engine for Navigation pageMap.
        # These empty source arrays deliberately request target registration only;
        # they are never used as source coverage or a full reachability verdict.
        save('page_mapping.json', json_bytes({'page_mapping': [], 'scope':'target-registration-only'}))
        save('nav_edges.json', json_bytes({'edges': [], 'scope':'target-registration-only'}))
        # main_pages registers classic router URLs, not NavPathStack names.
        # Scan exact pinned ETS copies without classic profiles so equal names
        # in main_pages cannot make an unregistered Navigation route pass.
        registration_root = run_dir/'navigation-registration-input'
        registration_root.mkdir()
        for relative, sha in binding['target_inputs'].items():
            if relative.endswith('.ets'):
                raw = regular_path(project,relative).read_bytes()
                if digest(raw) != sha: raise MigrationError('Target changed before registration scan: '+relative)
                save('navigation-registration-input/'+relative,raw)
        registration_command = [sys.executable, '-B', str(RUNTIME/'skills/arkts-router-verify/scripts/hmos_reachability.py')]
        registration_process = subprocess.run(registration_command, cwd=project, capture_output=True, timeout=120,
            shell=False, env=dict(os.environ, ROUTE_VERIFY_ROOT=str(registration_root), ROUTE_VERIFY_OUT=str(run_dir)))
        calls.append({'command':registration_command, 'exit_code':registration_process.returncode,
                      'role':'navigation-registration-only','root':str(registration_root),'out_dir':str(run_dir),
                      'projection':'exact current ETS files; classic main_pages excluded'})
        save('registration-stdout.log', registration_process.stdout)
        save('registration-stderr.log', registration_process.stderr)
        if registration_process.returncode:
            raise MigrationError('Actual arkts-router-verify registration scan failed with exit '+str(registration_process.returncode))
        registration_path = regular_path(project, run_dir.relative_to(project).as_posix()+'/reachability_robust.json')
        registration = read_json(registration_path)
        evidence.append({'path':registration_path.relative_to(project).as_posix(),'sha256':digest(registration_path.read_bytes())})
        registered_names = registration.get('registered_names')
        if not isinstance(registered_names,list) or any(not isinstance(name,str) for name in registered_names):
            raise MigrationError('Registration scan returned no complete registration-name list')
        from .ios_facts import validate_graph
        graph, _ = validate_graph(source, project)
        facts = {f['id']: f for f in graph['facts'] if f.get('kind') == 'navigation'}
        save('source-worklist.json', json_bytes({'source_sha256':binding['source_sha256'],
              'graph_sha256':binding['graph_sha256'],'navigation_facts':list(facts.values()),
              'required':'Review all source navigation facts against current page Spec; do not infer expected routes from target code'}))
        expected_path = regular_path(project, EXPECTATIONS)
        if not expected_path.is_file():
            expected = {'routes': []}
            if facts:gaps.append('Author current source-derived ios-routing.json before full route acceptance')
        else:
            expected = read_json(expected_path)
            if (expected.get('source_sha256') != binding['source_sha256']
                    or expected.get('graph_sha256') != binding['graph_sha256']
                    or not isinstance(expected.get('reviewer'), str) or not expected['reviewer']):
                raise MigrationError('Source routing expectations are stale or unreviewed')
            inputs = expected.get('spec_inputs')
            if not isinstance(inputs, dict) or not inputs:
                raise MigrationError('Routing expectations need current authored Spec anchors')
            for path, sha in inputs.items():
                if not path.startswith('spec/baseline/') or digest(regular_path(project,path).read_bytes()) != sha:
                    raise MigrationError('Routing Spec input changed: '+path)
        routes = expected.get('routes')
        if not facts and actual['edges']:
            gaps.append('Target navigation exists but source navigation inventory is not established')
        if not isinstance(routes, list):raise MigrationError('Expected routes must be a list')
        covered = set()
        for number, edge in enumerate(routes):
            if not isinstance(edge, dict) or edge.get('fact_id') not in facts:
                raise MigrationError('Expected route is not bound to a current navigation fact')
            covered.add(edge['fact_id'])
            if any(not isinstance(edge.get(k), str) or not edge[k] for k in ('source','target','control_text','target_type')):
                gaps.append('Unresolved source navigation: '+edge['fact_id']);continue
            if any(edge.get(k) for k in ('parameters','return_state','modal_state')):
                gaps.append('Parameter/return/modal semantics require independent current evidence: '+edge['fact_id'])
            matches = [e for e in actual['edges'] if all(e.get(k)==edge[k]
                       for k in ('source','target','control_text','target_type'))
                       and e.get('bound') is True and not e.get('dead_builder')]
            if edge.get('via'):matches=[e for e in matches if e.get('via')==edge['via']]
            if edge.get('guard') is not None:matches=[e for e in matches if e.get('guard')==edge['guard']]
            if not matches:
                findings.append({'id':'route-'+str(number),'rule':'ROUTE.MISSING_BINDING',
                    'source_fact':edge['fact_id'],'expected':edge,'status':'open'})
        if covered != set(facts):gaps.append('Navigation fact coverage is incomplete: '+', '.join(sorted(set(facts)-covered)))
        if actual.get('stats',{}).get('nav_target_unresolved',0):
            gaps.append('Some target navigation destinations remain unresolved by the extractor')
        resolved = set(actual.get('stats',{}).get('distinct_target_pages',[]))
        system_route_map = any(re.search(r'[\"\']?routerMap[\"\']?\s*:', regular_path(project,path).read_text(encoding='utf-8-sig'))
                               for path in binding['target_inputs'] if path.endswith('/module.json5'))
        for edge in actual['edges']:
            if edge.get('target_type') != 'page' or edge.get('target') not in resolved:
                continue
            if edge.get('via') == 'navigation':
                if edge['target'] in registered_names:
                    continue
                if system_route_map:
                    gaps.append('System routerMap registration needs independent current evidence: '+edge['target'])
                    continue
                missing = True
            else:
                missing = edge.get('registered') is False
            if missing:
                findings.append({'id':'route-registration-'+str(len(findings)), 'rule':'ROUTE.UNREGISTERED',
                                 'actual':edge,'status':'open'})
        if baseline.get('status')=='not_established' or baseline.get('input_error'):
            gaps.append('Formal source/Spec binding is not established')
        if not binding['contract_sha256']:gaps.append('Current execution contract is absent')
    except (MigrationError, OSError, ValueError, TypeError, KeyError, subprocess.SubprocessError) as exc:
        if isinstance(exc, subprocess.TimeoutExpired):called = True
        gaps.append(str(exc))
    # Recompute to detect concurrent source/target mutation; no stale PASS.
    try:
        if _bindings(project)[1] != binding:gaps.append('Inputs changed during actual route verification')
    except (MigrationError,OSError,ValueError) as exc:gaps.append(str(exc))
    status = 'FAIL' if findings else 'DEFERRED' if gaps else 'PASS' if binding['graph_sha256'] else 'DEFERRED'
    result = {'schema_version':1, 'status':status,'skill':'arkts-router-verify',
        'actual_call_now':called,'attempted':True,'command':command,'exit_code':code,'actual_calls':calls,'binding':binding,
        'findings':findings,'gaps':gaps,'evidence':evidence,
        'detail': ('Current static route defects found' if findings else '; '.join(gaps) if gaps else 'Current reviewed static edges and registrations checked'),
        'runtime_verified':False,'complete_navigation_acceptance':False,
        'recovery':'Read current source worklist; repair only under original ownership, rerun this same checker and affected build. Static results do not prove runtime reachability.'}
    write_json(regular_path(project,RESULT),result)
    summary = regular_path(project, OUT+'/ROUTE_VERIFY_SUMMARY.md')
    left, right = '<!-- hmigbot-ios-route:start -->', '<!-- hmigbot-ios-route:end -->'
    section = left+'\n# iOS 路由静态检查\n\n状态：'+status+'\n\n'+result['detail']+'\n\n真实运行跳转：未验证。参数/返回/模态语义缺证据不记通过。\n'+right+'\n'
    old = summary.read_text(encoding='utf-8') if summary.is_file() else ''
    if left in old and right in old:
        prefix, rest = old.split(left,1); _, suffix = rest.split(right,1); section=prefix+section.rstrip('\n')+suffix
    elif old:section=old+'\n\n'+section
    summary.write_text(section,encoding='utf-8')
    return result


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project',type=Path,required=True);parser.add_argument('--check',action='store_true')
    args=parser.parse_args(argv)
    try:
        result=current(args.project) if args.check else run(args.project)
        print(json.dumps(result,ensure_ascii=False,indent=2))
        return 0 if result['status'] in {'PASS','NOT_APPLICABLE'} else 1 if result['status']=='FAIL' else 3
    except (MigrationError,OSError,ValueError,TypeError,KeyError) as exc:
        print(json.dumps({'status':'DEFERRED','error':str(exc)},ensure_ascii=False));return 3
