"""Slice/group dispatch using original audit, C1/C4, and finalize.

This module never runs an old loop and changes its verdict. Each measurement is
made from the current source. source_verdict preserves original convergence rules
and the high-level custom cap, checked against the unchanged compiled oracle.
Other modes and finalize remain with the original structural_loop entry point.
"""
from pathlib import Path
import argparse, datetime, hashlib, json, subprocess, sys, uuid
import wiring_source
from source_verdict import evaluate


def encoded(value):
    return json.dumps(value, ensure_ascii=False, indent=2)


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(encoded(value), encoding='utf-8')


def merge_wiring(results, slices):
    categories = {}
    repairs = []
    modified = []
    for result in results:
        for name, category in result.get('categories', {}).items():
            combined = categories.setdefault(name, {'pass': 0, 'fail': 0, 'details': []})
            combined['pass'] += category.get('pass', 0)
            combined['fail'] += category.get('fail', 0)
            combined['details'].extend(category.get('details', []))
        repairs.extend(result.get('repair_actions', []))
        for name in result.get('scope', {}).get('modifies_files', []):
            if name not in modified:
                modified.append(name)
    return {'categories': categories, 'repair_actions': repairs,
            'scope': {'modifies_files': modified, 'cross_slice_edits_files': []},
            'group_slices': [str(n) for n in slices]}


def dispatch(mode, target, iteration, audit, wiring, history):
    findings = [item for item in audit.get('findings', []) if item.get('severity_at_scope') == 'FAIL']
    repairs = wiring.get('repair_actions', [])
    text = f'=== STRUCTURAL LOOP — {mode}={target} iteration {iteration} repair brief ===\n'
    text += f'上一轮检测脚本扫到本 {mode} 仍有以下 FAIL 项。请仅按各条 `suggested_action` 字段逐条修复，不做其他无关变更；修复完后返回，脚本会重新检测验证。\n\n'
    text += f'## Skeleton findings (audit_skeletons.py, {len(findings)} FAIL items)\n```json\n{encoded(findings)}\n```\n\n'
    text += f'## Wiring repair_actions (verify_slice_wiring.py, {len(repairs)} items)\n```json\n{encoded(repairs)}\n```\n\n'
    text += f'## History so far (iterations 0..{iteration-1})\n'
    for item in history:
        text += f"  iter {item['iter']}: audit_fail={item.get('audit_fail',0)} wiring_repair={item.get('wiring_repair_actions',0)}\n"
    text += '\n## 约束\n- 只编辑 findings/orphans/repair_actions 中列出的文件\n- 不要做无关重构 / 不要改文件结构 / 不要重命名\n- 完成后返回；勿在本次响应中重复运行检测脚本（loop 自驱）\n'
    return text


def safe_wiring(project, number, scripts, output, registry, guard=None):
    try:
        return wiring_source.run(project, number, scripts, output, registry_path=registry,measurement_guard=guard)
    except (wiring_source.EvidenceIOError,wiring_source.SourceInputChangedError):
        raise
    except (Exception, SystemExit) as error:
        message = 'detector crashed — see error'
        detail = f'{type(error).__name__}: {error}'
        evidence = output.parent / 'wiring-evidence' / output.stem / 'sdk-evidence.json'
        # SDK-specific failures are an explicit platform-input difference. Keep
        # their original crash accounting, with useful facts in the repair text.
        if 'SDK' in detail or 'Node runtime' in detail:
            facts = {}
            available = False
            try:
                candidate = json.loads(evidence.read_text(encoding='utf-8'))
                run = json.loads((evidence.parent/'run.json').read_text(encoding='utf-8'))
                available = bool(run.get('run_id')) and candidate.get('runId') == run['run_id']
                if available:facts = candidate
            except (OSError, ValueError, TypeError):
                pass
            sdk = {'version': facts.get('sdkSelection', {}).get('metadata', {}).get('version'),
                   'config_sha256': facts.get('configSha256'), 'evidence': str(evidence) if available else None,
                   'evidence_available': available,
                   'diagnostics': {name: value['diagnostics'] for name, value in facts.get('files', {}).items() if value.get('diagnostics')},
                   'error': detail}
            message += ' — ' + json.dumps(sdk, ensure_ascii=False)
        elif 'F_GETPATH' in detail:
            message += ' — ' + detail
        result = {'categories': {}, 'repair_actions': [message], 'passed': False,
                  'detector': 'wiring', 'error': detail}
        write(output, result)
        return result


def safe_audit(command, project, output, evidence):
    wiring_source.preserve_previous(output)
    process = subprocess.run(command, cwd=project, capture_output=True, text=True, encoding='utf-8')
    (evidence / 'audit.stdout.log').write_text(process.stdout,encoding='utf-8')
    (evidence / 'audit.stderr.log').write_text(process.stderr,encoding='utf-8')
    write(evidence / 'audit-process.json', {'argv':command,'returncode':process.returncode})
    sys.stderr.write(process.stderr)
    try:
        return json.loads(output.read_text(encoding='utf-8'))
    except (OSError, ValueError) as error:
        # Original _safe_detector counts a failed detector once and preserves
        # the real JSON-read exception, rather than declaring convergence.
        detail = f'{type(error).__name__}: {error}'
        sys.stderr.write(f"[structural_loop] detector 'audit' FAILED (pipeline continues): {error}\n")
        result = {'summary': {'FAIL': 1, 'WARN': 0, 'L1': 0, 'L2': 0,
                              'L3': 0, 'L4': 0, 'handoff_escape_hatches': 0},
                  'findings': [], 'handoff_escape_hatches': [], 'scope_files': [],
                  'passed': False, 'detector': 'audit', 'error': detail}
        write(output, result)
        return result


def prepare_inputs(args, project, scripts, state_path):
    """Only input-format routing. Never inspect source to choose an engine."""
    sys.path.insert(0, str(scripts))
    from plan_lib.feature_plan_parser import FeaturePlan
    reason = None
    try:
        plan_path=project / 'spec/baseline/plans/feature-plan.md'
        plan_input=wiring_source.plan_signature(plan_path)
        plan = FeaturePlan.parse_file(project / 'spec/baseline/plans/feature-plan.md')
        if wiring_source.plan_signature(plan_path)!=plan_input:
            raise wiring_source.SourceInputChangedError('Plan changed while parsing inputs')
        if args.mode == 'group':
            if not args.slices:
                raise ValueError('group mode requires --slices')
            numbers = [int(value.strip()) for value in args.slices.split(',') if value.strip()]
        else:
            numbers = [int(args.target)]
        specifications = [plan.slices[number] for number in numbers]
        state = json.loads(state_path.read_text(encoding='utf-8')) if state_path.is_file() else {'history': [], 'max_iter': 8}
        if not isinstance(state, dict):
            raise ValueError('state is not a JSON object')
        history = state.setdefault('history', [])
        if not isinstance(history, list) or any(not isinstance(row, dict) for row in history):
            raise ValueError('history is not a list of JSON objects')
        scope=list(dict.fromkeys(name for spec in specifications for name in [*spec.modifies_files,*(row.file for row in spec.cross_slice_edits)]))
        guard=wiring_source.MeasurementGuard(project,plan_path,scope,
              [row.file for spec in specifications for row in spec.cross_slice_edits],
              args.handoffs or [],project/'spec/placeholder-registry.md',plan_input)
        prepared = (numbers, specifications, state, history, guard)
    except (OSError, ValueError, KeyError, TypeError, AttributeError, SystemExit) as error:
        reason = f'{type(error).__name__}: {error}'
        prepared = None
    if project.is_dir():
        evidence = project / 'spec/execution/autofix-log/native-wiring-routing' / (uuid.uuid4().hex + '.json')
        write(evidence, {'selected_engine': 'original' if reason else 'source',
                         'reason': reason or 'valid plan and history containers',
                         'state_file': str(state_path), 'mode': args.mode,
                         'target': args.target, 'source_inspected_for_routing': False})
    return prepared


def maybe_run(engine, argv, scripts):
    if not argv or argv[0] != 'iterate' or '--help' in argv or '-h' in argv:
        return None
    probe = argparse.ArgumentParser(add_help=False)
    probe.add_argument('--mode')
    selected, _ = probe.parse_known_args(argv[1:])
    if selected.mode not in ('slice', 'group'):
        return None
    parser = argparse.ArgumentParser(prog='structural_loop.py iterate')
    parser.add_argument('--project-root', required=True, type=Path)
    parser.add_argument('--android-res', nargs='*')
    parser.add_argument('--density', type=float)
    parser.add_argument('--mode', required=True, choices=['stage', 'slice', 'group', 'pipeline'])
    parser.add_argument('--target', required=True)
    parser.add_argument('--slices')
    parser.add_argument('--state-file', required=True, type=Path)
    parser.add_argument('--max-iter', type=int, default=8)
    parser.add_argument('--diff-base')
    parser.add_argument('--handoffs', nargs='*')
    parser.add_argument('--output-json', type=Path)
    args = parser.parse_args(argv[1:])
    project = args.project_root.resolve()
    scripts = Path(scripts).resolve()
    state_path = args.state_file.resolve()
    output = args.output_json.resolve() if args.output_json else None
    try:
        for path in [state_path, output]:
            if path and any(path.parts[i:i+2] == ('docs','autofix-log') for i in range(len(path.parts)-1)):
                sys.stderr.write(f'error: 输出路径 {path} 位于已废弃的 docs/autofix-log——closure 产物一律落 spec/execution/autofix-log/round-<R>/\n')
                return 1
        prepared = prepare_inputs(args, project, scripts, state_path)
        if prepared is None:
            return None  # The unchanged compiled entry owns its input errors.
        numbers, specifications, state, history, guard = prepared
        scope = []
        for spec in specifications:
            for name in [*spec.modifies_files, *(row.file for row in spec.cross_slice_edits)]:
                if name not in scope:
                    scope.append(name)
        iteration = len(history)
        log = state_path.parent
        log.mkdir(parents=True, exist_ok=True)
        evidence = log / 'native-wiring-loop' / (datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '-' + uuid.uuid4().hex[:8])
        evidence.mkdir(parents=True)
        write(evidence/'shared-input-signature.json',guard.before)
        audit_path = log / f'audit-{args.target}-iter{iteration}.json'
        registry = project / 'spec/placeholder-registry.md'
        registry_input = wiring_source.registry_snapshot(registry)
        audit_command = [sys.executable, str(scripts / 'audit_skeletons.py'), '--project-root', str(project), '--scope', 'slice', '--scope-files', *scope, '--registry', str(registry), '--output-json', str(audit_path)]
        if args.handoffs:
            audit_command.extend(['--handoffs', *args.handoffs])
        guard.verify()
        if scope:
            audit = safe_audit(audit_command, project, audit_path, evidence)
        else:
            # The original compiled loop emits this four-key receipt for a
            # successfully parsed empty scope; its scanner CLI rejects no files.
            audit = {'summary': {'FAIL': 0, 'WARN': 0, 'L1': 0, 'L2': 0,
                                 'L3': 0, 'L4': 0, 'handoff_escape_hatches': 0},
                     'findings': [], 'handoff_escape_hatches': [], 'scope_files': []}
            write(audit_path, audit)
            write(evidence / 'audit-empty-scope.json',
                  {'scope_files': [], 'scanner_called': False,
                   'semantics': 'original compiled loop empty-scope receipt'})
        guard.verify()
        wiring_path = log / f'wiring-{args.target}-iter{iteration}.json'
        if args.mode == 'slice':
            wiring = safe_wiring(project, numbers[0], scripts, wiring_path, registry, guard)
            guard.verify()
        else:
            results=[]
            for number in numbers:
                results.append(safe_wiring(project, number, scripts, log / f'wiring-{args.target}-s{number}-iter{iteration}.json', registry, guard))
                guard.verify()
            wiring = merge_wiring(results, numbers)
            write(wiring_path, wiring)
        guard.verify()
        if wiring_source.registry_snapshot(registry) != registry_input:
            raise RuntimeError('Registry input changed between audit and wiring')
        repairs = wiring.get('repair_actions', [])
        fingerprint = [[row.get('file', ''), row.get('p_id') or row.get('line', 0), row.get('subtype', '')] for row in audit.get('findings', []) if row.get('severity_at_scope') == 'FAIL']
        for row in repairs:
            if isinstance(row, dict):
                fingerprint.append([row.get('file', ''), 0, 'wiring:' + row.get('category', '') + ':' + (row.get('failed_check') or row.get('current_state', '')[:30])])
        current = {'iter': iteration, 'audit_fail': audit.get('summary', {}).get('FAIL', 0),
                   'audit_warn': audit.get('summary', {}).get('WARN', 0),
                   'wiring_blocked_categories': sum(bool(category.get('fail')) for category in wiring.get('categories', {}).values()),
                   'wiring_repair_actions': len(repairs),
                   'handoff_escape_hatches': len(audit.get('handoff_escape_hatches', [])),
                   'fingerprint': fingerprint, 'detectors_run': ['audit', 'wiring'],
                   'detectors_skipped': [], 'detectors_effective': ['audit', 'wiring']}
        core_input = evidence / 'convergence-input.json'
        core_output = evidence / 'convergence-verdict.json'
        write(core_input, {'history': history, 'current': current, 'max_iter': args.max_iter})
        verdict, exit_code = evaluate(history, current, args.max_iter)
        write(core_output, verdict)
        history.append(current)
        # Preserve existing metadata and insertion order. The original writes
        # state before constructing dispatch; an invalid old row may fail there.
        state['last_verdict'] = verdict
        state['mode'] = args.mode
        state['target'] = args.target
        state['max_iter'] = args.max_iter
        write(state_path, state)
        total = current['audit_fail'] + len(repairs) + current['handoff_escape_hatches']
        def relative(path):
            try:return str(path.relative_to(project))
            except ValueError:return str(path)
        result = {'mode': args.mode, 'target': args.target, 'iteration': iteration,
                  'verdict': verdict['verdict'], 'escalation': verdict['escalation'], 'reason': verdict['reason'],
                  'current_state': {'audit_fail': current['audit_fail'], 'wiring_repair_actions': len(repairs),
                                    'handoff_escape_hatches': current['handoff_escape_hatches'], 'total_fail': total},
                  'dispatch_prompt': dispatch(args.mode, args.target, iteration, audit, wiring, history) if verdict['verdict'] == 'CONTINUE' else '',
                  'detector_json_paths': {'audit': relative(audit_path), 'wiring': relative(wiring_path)},
                  'state_file': relative(state_path)}
        if output:
            write(output, result)
        else:
            print(encoded(result))
        implementation = Path(__file__).with_name('source_verdict.py')
        write(evidence / 'dispatch-evidence.json', {'original_audit_argv': audit_command,
                                                   'registry_input': registry_input,
                                                   'source_verdict_implementation': str(implementation),
                                                   'source_verdict_sha256': hashlib.sha256(implementation.read_bytes()).hexdigest(),
                                                   'current': current, 'verdict': verdict, 'source_wiring': [str(number) for number in numbers]})
        return exit_code
    except (OSError, RuntimeError) as error:
        sys.stderr.write(f'structural_loop error: {error}\n')
        return 3
