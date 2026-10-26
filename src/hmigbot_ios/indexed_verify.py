"""Bind applicable checks to current evidence; advanced observations are optional."""
from pathlib import Path

from .core import source_snapshot
from .core import MigrationError, digest, json_bytes, read_json, safe_child, snapshot

LABELS={'CHECK-1':'终态全量编译','CHECK-2':'静态分析','CHECK-3':'占位符扫描','CHECK-4':'App 身份校验',
        'CHECK-5':'页面状态审计','CHECK-6':'路由跳转验证','CHECK-7':'视觉与功能子项'}


CHECK_KEYS={'CHECK-1':'compilation','CHECK-2':'static_analysis','CHECK-3':'placeholders',
            'CHECK-4':'app_identity','CHECK-5':'page_state','CHECK-6':'routing','CHECK-7':'visual_runtime'}
DEFAULT_CHECKS=['CHECK-1','CHECK-2','CHECK-3','CHECK-4']


def scope(request, *, applicable_checks=()):
    if not isinstance(request,dict):raise MigrationError('Verification scope must be an object')
    chosen=request.get('checks',DEFAULT_CHECKS+list(applicable_checks))
    if (not isinstance(chosen,list) or any(not isinstance(i,str) or i not in LABELS for i in chosen)
            or len(chosen)!=len(set(chosen))):
        raise MigrationError('Verification checks must be unique known identifiers')
    behavior=request.get('behavior','pending')
    if behavior not in {'selected','not_selected','pending'}:
        raise MigrationError('Behavior scope must be selected, not_selected or pending')
    run=request.get('run_behavior',False)
    if type(run) is not bool or run and (behavior!='selected' or request.get('authorized_cases') is not True):
        raise MigrationError('Real behavior execution needs selected scope and authorized cases with independent oracles')
    chosen=[i for i in LABELS if i in chosen]
    return {'schema_version':2,'execution_model':'indexed-stages-v1','checks':chosen,
            'check_keys':{i:CHECK_KEYS[i] for i in LABELS},'execution_order':chosen,
            'unavailable':'DEFERRED','behavior':behavior,'run_behavior':run,
            'overall_checks':chosen,'behavior_affects_overall':False,
            'scope_note':'Selected checks only; not_selected and unavailable observations do not establish complete acceptance'}


def _applicable_checks(project):
    """Use actual authored inputs, never assume device/UI availability."""
    checks=[]
    contract=project/'spec/execution/execution-contract.json'
    try:
        if contract.is_file() and read_json(contract).get('source_ui'):
            checks.append('CHECK-5')
        graph=project/'spec/baseline/ios-facts.json'
        if graph.is_file() and any(row.get('kind')=='navigation' for row in read_json(graph).get('facts',[]) if isinstance(row,dict)):
            checks.append('CHECK-6')
    except (OSError,MigrationError,ValueError,TypeError,AttributeError):
        # Broken formal inputs are diagnosed by their producer, not invented here.
        pass
    return checks


def report(project, *, write=True, build_evidence=None, scope_request=None):
    from .gate_artifacts import _write_report,_cell,MARKER
    from .native_pipeline import context
    from .quality_views import _summary_inputs,target_inputs,_compilation
    project=Path(project).resolve();source,_=context(project)
    selected=scope(scope_request if scope_request is not None else {},
                   applicable_checks=_applicable_checks(project))
    path=project/'spec/verification/verify-results.json'
    errors=[]
    try:
        results=read_json(path) if path.is_file() else {}
        if not isinstance(results,dict) or not isinstance(results.get('checks',[]),list):
            raise MigrationError('Verification results must contain a check list')
    except (OSError,MigrationError,ValueError,TypeError) as exc:
        errors.append(str(exc));results={}
    source_sha=source_snapshot(source)['sha256'];spec,baseline=_summary_inputs(project);target=target_inputs(project)
    contract=project/'spec/execution/execution-contract.json'
    bound=(contract.is_file() and baseline['status']!='not_established' and not baseline.get('input_error')
           and results.get('schema_version')==2 and results.get('execution_model')=='indexed-stages-v1'
           and results.get('source_sha256')==source_sha and results.get('spec_input_hashes')==spec
           and results.get('target_input_hashes')==target
           and results.get('execution_contract_sha256')==digest(contract.read_bytes()))
    checks={}
    for entry in results.get('checks',[]):
        if not isinstance(entry,dict):
            errors.append('Malformed verification check entry');continue
        ident=entry.get('id')
        if ident not in LABELS or ident in checks:
            errors.append('Unknown/duplicate indexed verification check: '+str(ident))
            if ident in LABELS:checks[ident]={'status':'DEFERRED','detail':'冲突的重复检查记录，保留原始结果供恢复'}
            continue
        state=entry.get('status');evidence=entry.get('evidence',[]);reason=entry.get('detail','')
        valid=(bound and state in {'PASS','FAIL','DEFERRED','NOT_APPLICABLE'} and isinstance(evidence,list)
               and entry.get('key',CHECK_KEYS[ident])==CHECK_KEYS[ident])
        if state in {'PASS','FAIL','NOT_APPLICABLE'}:
            valid=valid and bool(evidence) and type(entry.get('exit_code')) is int and (state=='FAIL' or entry['exit_code']==0)
            if state=='NOT_APPLICABLE':valid=valid and ident in {'CHECK-3','CHECK-5','CHECK-6','CHECK-7'} and bool(reason)
        else:valid=valid and bool(reason)
        for item in evidence if isinstance(evidence,list) else []:
            try:
                p=safe_child(project,item['path'])
                valid=valid and item['path'].startswith('spec/') and p not in {path,project/'spec/verify-report.md'} and digest(p.read_bytes())==item['sha256']
            except (OSError,ValueError,KeyError,TypeError):valid=False
        checks[ident]={'status':state if valid else 'DEFERRED','detail':reason if valid else '缺少当前绑定或证据已失效'}
    for ident in LABELS:checks.setdefault(ident,{'status':'DEFERRED','detail':'not_run：尚无当前实际检查证据'})
    compilation=_compilation(project,source_sha,build_evidence)
    if compilation.get('status')=='passed':
        checks['CHECK-1']={'status':'PASS','detail':'真实构建命令及当前输入、配置、产物绑定有效（允许合法缓存命中）'}
    elif compilation.get('status')=='failed':
        checks['CHECK-1']={'status':'FAIL','detail':'当前绑定的真实构建失败；详见构建证据'}
    elif checks['CHECK-1']['status']=='PASS':
        checks['CHECK-1']={'status':'DEFERRED','detail':'缺少绑定当前目标字节的终态真实构建证据'}
    for ident,item in checks.items():
        item.update(key=CHECK_KEYS[ident],selected=ident in selected['checks'],
                    selection_state='selected' if ident in selected['checks'] else 'not_selected')
    states=[v['status'] for v in checks.values()]
    selected_states=[checks[i]['status'] for i in selected['checks']]
    # A selected scope cannot erase a current, evidenced product defect.
    gate=('FAIL' if 'FAIL' in states else 'PARTIAL' if not selected_states or any(
          state not in {'PASS','NOT_APPLICABLE'} for state in selected_states)
          else 'PASS' if len(selected['checks'])==len(LABELS) and 'NOT_APPLICABLE' not in selected_states
          else 'PASS_SELECTED_SCOPE')
    lines=['# 迁移验证报告',MARKER,'execution_model: indexed-stages-v1',f'source_sha256: {source_sha}',
           f'gate_status: {gate}','selected_checks: '+', '.join(selected['checks']),
           'complete_migration_acceptance: not_established','','| 编号 | 检查项 | 本次范围 | 状态 | 证据结论 |','|---|---|---|---|---|']
    lines += ['| '+' | '.join(_cell(v) for v in (i,label,checks[i]['selection_state'],checks[i]['status'],checks[i]['detail']))+' |' for i,label in LABELS.items()]
    lines += ['','当前编号固定：1编译、2静态、3占位、4身份、5页面、6路由、7视觉/运行。跨版本以 check key 对应，禁止直接套用旧五项编号。',
              '只验收本次已选且适用的检查；NOT_APPLICABLE 须有当前检查证据和理由，不代表产品行为已验证。',
              '高级UI、设备和视觉观察仅按明确选择与授权执行；未选、不具备能力或未执行均不计通过。',
              '完整迁移验收与实际运行等价保持独立；真实已归因失败不会因缩小范围而消失。',
              f"deferred_count: {states.count('DEFERRED')}"]
    if baseline['missing_inputs']:lines += ['','待建立的规格输入：'+', '.join(baseline['missing_inputs'])]
    if errors:lines += ['','输入诊断：'+'; '.join(errors)]
    runtime=Path(__file__).resolve().parents[2]
    report_cli=runtime/'scripts/a2h_ios.py'
    alternatives=[]
    if report_cli.is_file():
        import sys
        alternatives.append({'id':'file_progress_report','available':True,
            'command':[sys.executable,str(report_cli),'migration-report','--project',str(project)],
            'capability':'Read existing files and produce partial progress',
            'evidence_scope':'Current files and previously bound evidence only; no device, UI or runtime observation'})
    if compilation.get('status')=='passed':
        alternatives.append({'id':'retain_current_build_axis','available':True,
            'capability':'Reuse current, bound SDK build evidence',
            'evidence_scope':'Compilation/artifact integrity only; other missing checks remain DEFERRED',
            'evidence':str(build_evidence)})
    if alternatives:
        lines += ['','可用恢复路径：']+['- '+item['id']+'：'+item['capability']+'；'+item['evidence_scope'] for item in alternatives]
    markdown='\n'.join(lines)+'\n'
    if write:_write_report(project/'spec/verify-report.md',markdown)
    return {'status':'generated','gate_status':gate,'checks':checks,'report':'spec/verify-report.md',
            'baseline':baseline,'binding_errors':errors,'compilation':compilation,'scope':selected,
            'complete_migration_acceptance':'not_established',
            'alternatives':alternatives,
            **({'markdown':markdown} if not write else {})}
