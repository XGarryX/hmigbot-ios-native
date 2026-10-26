"""Read-only joins of page contracts, original landing rows and current file hashes."""
from pathlib import Path
import re

from .core import MigrationError, digest, io_path, json_bytes, read_json, safe_child


def generation(project, source_sha):
    if (Path(project) / 'spec/execution/execution-contract.json').is_file():
        from .indexed_evidence import generation as indexed_generation
        return indexed_generation(Path(project), source_sha)
    from .ios_scheduler import baseline_inputs, kernel
    from .plan_contract import assert_pinned
    plan_path = project / 'spec/waves/plan-domains.json'
    if not plan_path.exists():
        return {'status': 'not_run'}, [], {}
    try:
        plan = read_json(plan_path)
        contract = read_json(project / 'spec/blueprint/contracts.json')
        assert_pinned(project, contract)
        if (plan.get('ios_adapter_version') != 2 or contract.get('source_sha256') != source_sha
                or baseline_inputs(project, 'domains') != contract.get('input_hashes')
                or digest(json_bytes({k: v for k, v in plan.items() if k != 'contract_hash'}))
                != contract.get('plan_identity_sha256')
                or kernel().compute_contract_hash(project / 'spec/blueprint', []) != plan.get('contract_hash')):
            raise MigrationError('Plan or its pinned source/contracts changed')
        refs = [(r['path'], r['sha256']) for rs in contract.get('task_inputs', {}).values() for r in rs]
        refs += list(contract.get('prompt_hashes', {}).items())
        if any(digest(safe_child(project, path).read_bytes()) != expected for path, expected in refs):
            raise MigrationError('Pinned task input changed')
        tasks = contract['ios_tasks']
        if {t['id'] for t in tasks} != {t['id'] for t in plan['tasks']}:
            raise MigrationError('Original plan task set differs from contract')
    except (OSError, KeyError, TypeError, ValueError, MigrationError) as exc:
        return {'status': 'stale', 'reason': str(exc)}, [], {}
    journal_path = project / 'spec/state/journal.json'
    journal = read_json(journal_path) if journal_path.exists() else {}
    dispatch_path = project / 'spec/state/dispatch.json'
    dispatch = read_json(dispatch_path).get('waves', {}).get('domains', {}) if dispatch_path.exists() else {}
    workflows = [w for w in journal.get('workflow_status', []) if w.get('workflow_id') == 'domains']
    def current_run(row):
        try:
            return (row.get('contract_hash') == plan['contract_hash']
                    and io_path(Path(row.get('plan_path', ''))).resolve() == io_path(plan_path).resolve())
        except (ValueError, TypeError): return False
    run_current = len(workflows) == 1 and current_run(workflows[0]) and current_run(dispatch)
    records, by_id = {}, {t['id']: t for t in plan['tasks']}
    dispatch_evidence_path = project / 'spec/reports/ios-dispatch-domains.json'
    dispatch_evidence = read_json(dispatch_evidence_path) if dispatch_evidence_path.is_file() else {}
    before = dispatch_evidence.get('before_files') if dispatch_evidence.get('plan_sha256') == digest(plan_path.read_bytes()) else None
    for task in tasks:
        ident = task['id']; result_path = by_id[ident]['result_path']
        path = safe_child(project, result_path)
        state = {'status': 'not_run', 'outputs': {}, 'receipt': result_path}
        records[ident] = state
        if not path.exists():
            continue
        try:
            receipt = read_json(path)
            from .receipt_outputs import validate_outputs
            files, deleted = validate_outputs(project, receipt, task, before=before,
                readonly=not task['ownership'] and task.get('verification') in {'compile', 'behavior', 'visual'})
            if (receipt.get('source_sha256') != source_sha
                    or receipt.get('ios_receipt_version') != 2
                    or receipt.get('plan_sha256') != digest(plan_path.read_bytes())
                    or receipt.get('task_id') != ident or receipt.get('behavior_verified') is not False
                    or set(receipt.get('ac_ids', [])) != set(task.get('ac_ids', []))
                    ):
                raise MigrationError('Receipt binding or current output hashes differ')
            rows = [r for r in journal.get('operation_outputs', []) if r.get('workflow_id') == 'domains'
                    and r.get('task_id') == ident and r.get('kind') == 'agent']
            landed = rows[-1] if rows else {}
            dispatched = dispatch.get('dispatched', {}).get(ident, {})
            if receipt.get('status') == 'blocked':
                state['status'] = 'blocked'
            elif (receipt.get('status') != 'generated' or receipt.get('final_state') != 'PASS'
                    or receipt.get('findings')):
                state['status'] = 'unverified'
            elif (not run_current or landed.get('status') != 'OK' or landed.get('result_path') != result_path
                    or type(landed.get('attempt')) is not int or landed['attempt'] < 1
                    or dispatched.get('attempts') != landed['attempt']
                    or landed.get('resume_key') != by_id[ident].get('resume_key')
                    or dispatched.get('resume_key') != landed.get('resume_key')
                    or any(dispatched.get(k) != by_id[ident].get(k) for k in ('agent', 'prompt_file', 'result_path'))):
                state['status'] = 'unlanded'
            else:
                state.update(status='generated', outputs=files, landing={
                    'journal': 'spec/state/journal.json', 'attempt': landed['attempt']})
                if deleted:
                    state['deleted_outputs'] = deleted
        except (OSError, KeyError, TypeError, ValueError, MigrationError) as exc:
            state.update(status='stale', reason=str(exc))
    relevant = [records[t['id']]['status'] for t in tasks if t['ownership']]
    overall = combine(relevant)
    return {'status': overall, 'task_counts': {s: relevant.count(s) for s in sorted(set(relevant))},
            'scope': 'Original landed generation with current hashes; no compilation or behavior claim'}, tasks, records


def combine(statuses):
    if not statuses: return 'not_run'
    if len(set(statuses)) == 1: return statuses[0]
    for state in ('stale', 'blocked', 'unlanded', 'unverified'):
        if state in statuses: return state
    return 'partial'


def pages(project, acs, global_axes, tasks, records):
    from .artifact_contract import markdown_tables
    from .plan_contract import _manifest_target, _projection, _table_rows, profile
    from .artifact_contract import catalog
    manifest = project / 'spec/baseline/ui-manifest.md'
    catalog_profile = profile(project) >= 2
    rows = []
    if manifest.exists():
        if catalog_profile:
            rows = _table_rows(manifest, artifact='spec/baseline/ui-manifest.md')
        else:
            for table in markdown_tables(manifest.read_text(encoding='utf-8-sig')):
                rows.extend(dict(zip(table['headers'], row)) for row in table['rows'])
    units = []
    try:
        for artifact in catalog()['plan']['artifacts']:
            if artifact.get('check') != 'correspondence': continue
            paths = [project / artifact['path']] if 'path' in artifact else sorted(project.glob(artifact['glob']))
            for path in paths:
                if path.exists(): units.extend(_projection(project, path))
    except (OSError, KeyError, TypeError, ValueError, MigrationError):
        units = []  # Stale/malformed contracts must never create a page success.
    result = []
    for doc in sorted((project / 'spec/baseline/ui').glob('page_*.md')):
        match = re.match(r'(page_\d{4})(?:_|\.)', doc.name)
        if not match: continue
        ident = match[1]
        entries = [r for r in rows if r.get('page_id', '').strip('` ') == ident]
        targets = (sorted({_manifest_target(project, row, ident) for row in entries}) if catalog_profile else
                   sorted({v.strip('` ') for row in entries for k, v in row.items()
                           if ('ArkTS' in k and '目标' in k) or k in {'target_path', '目标文件'}}))
        item_ids = {u['item_id'] for u in units if ident in u.get('page_ids', []) and u.get('scope') == 'product'}
        linked = [t for t in tasks if (item_ids & set(t.get('plan_item_refs', []))
                  or not t.get('plan_item_refs') and set(targets) & set(t['ownership']))]
        ids = set(re.findall(r'\bF\d+-AC\d+\b', doc.read_text(encoding='utf-8-sig'))) & set(acs)
        ids.update(a for u in units if u['item_id'] in item_ids and u['item_id'].startswith('UI:')
                   for a in u.get('ac_ids', []) if a in acs)
        gen = ({'status': global_axes['generation']['status']} if not linked
               else {'status': combine([records[t['id']]['status'] for t in linked]),
                     'tasks': {t['id']: records[t['id']] for t in linked}})
        if not linked and gen['status'] == 'generated': gen['status'] = 'unmapped'
        compile_axis = dict(global_axes['compilation'])
        if compile_axis['status'] == 'passed':
            build = read_json(Path(compile_axis['evidence']))
            if (not targets or len(entries) != 1
                    or any(t not in build['target_input_hashes'] for t in targets)):
                compile_axis['status'] = 'unmapped'
            compile_axis['scope'] = 'Current whole-project build binds declared page files; runtime reachability is separate'
        behavior = global_axes['behavior']
        ac_states = {a: behavior.get('ac_statuses', {}).get(a, 'unverified') for a in sorted(ids)}
        status = behavior['status'] if behavior['status'] in {'not_run', 'stale', 'legacy_unclassified'} else (
            'passed' if ac_states and set(ac_states.values()) == {'passed'} else
            'failed' if 'failed' in ac_states.values() else 'unverified')
        result.append({'page_id': ident, 'spec': doc.relative_to(project).as_posix(),
            'plan_item_refs': sorted(item_ids), 'task_ids': sorted(t['id'] for t in linked),
            'target_paths': targets, 'ac_ids': sorted(ids), 'axes': {
                'generation': gen, 'compilation': compile_axis,
                'behavior': {'status': status, 'ac_statuses': ac_states,
                             'scope': behavior.get('scope', 'Current page AC observations only')},
                'visual': {'status': 'not_run'}}})
    return result
