"""Explicit failure-only recovery of a reviewed-spec-change deadlock.

The original kernel remains the only state/dispatch/journal writer. This is
deliberately separate from normal frozen-plan dispatch and landing.
"""
from pathlib import Path
import base64
import re

from .core import MigrationError, atomic_write, digest, json_bytes, read_json, safe_child, write_json


def _require(condition, message):
    if not condition:
        raise MigrationError('Blocked recovery: ' + message)


def _sha(value):
    return isinstance(value, str) and re.fullmatch(r'[0-9a-f]{64}', value) is not None


def _review(path):
    value = read_json(path)
    fields = {'version', 'wave', 'task_id', 'attempt', 'reviewer', 'reason', 'workers_stopped',
              'old', 'new', 'changes', 'replan_request'}
    _require(isinstance(value, dict) and fields <= set(value) <= fields | {'authoring_rebind', 'managed_upgrade'}, 'review schema fields differ')
    _require(type(value['version']) is int and value['version'] == 1 and value['wave'] in {'domains', 'understand'}, 'review version/wave')
    _require(isinstance(value['task_id'], str) and re.fullmatch(r'[a-z][a-z0-9_-]*', value['task_id']), 'task id')
    _require(type(value['attempt']) is int and value['attempt'] > 0, 'attempt')
    _require(value['workers_stopped'] is True, 'workers must be stopped before recovery')
    _require(all(isinstance(value[k], str) and value[k].strip() for k in ('reviewer', 'reason')), 'review identity/reason')
    old_fields = {'plan_sha256', 'contract_sha256', 'dispatch_sha256', 'dispatch_evidence_sha256',
                  'receipt_sha256', 'source_sha256', 'graph_sha256', 'baseline_inputs_sha256', 'contract_revision'}
    _require(isinstance(value['old'], dict) and set(value['old']) == old_fields
             and all(_sha(v) for v in value['old'].values()), 'old digest bindings')
    _require(isinstance(value['new'], dict) and set(value['new']) == {'contract_revision', 'baseline_inputs_sha256'}
             and all(_sha(v) for v in value['new'].values()), 'new digest bindings')
    _require(isinstance(value['changes'], list) and value['changes'], 'explicit reviewed Spec changes required')
    return value


MANAGED = {
    '.agents/skills/ios-source-analysis/SKILL.md': 'skills/ios-source-analysis/SKILL.md',
    '.agents/skills/ios-source-analysis/references/harness-v2.md': 'skills/ios-source-analysis/references/harness-v2.md',
}


def _managed_binding(review, manifest, record):
    """Validate archived or fresh bytes independently of mutable current state."""
    proof = review['managed_upgrade']
    _require(isinstance(proof, dict) and set(proof) == {'install_manifest_sha256', 'old_runtime_revision', 'current_runtime_revision', 'files'}
             and _sha(proof['install_manifest_sha256']) and proof['old_runtime_revision'] == review['old']['contract_revision']
             and proof['current_runtime_revision'] == review['new']['contract_revision'], 'managed upgrade revision/schema')
    _require(isinstance(manifest, dict) and manifest.get('owner') == 'hmigbot-ios'
             and type(manifest.get('schema_version')) is int and manifest['schema_version'] == 1
             and isinstance(manifest.get('files'), dict), 'managed install manifest schema')
    _require(isinstance(proof['files'], list) and 1 <= len(proof['files']) <= 2
             and isinstance(record, dict) and set(record) == {'proof', 'files'} and record['proof'] == proof
             and isinstance(record['files'], list) and len(record['files']) == len(proof['files']), 'managed proof files')
    seen = set()
    for item, saved in zip(proof['files'], record['files']):
        _require(isinstance(item, dict) and set(item) == {'path', 'old_sha256', 'new_sha256', 'old_copy'}
                 and item['path'] in MANAGED and item['path'] not in seen and _sha(item['old_sha256'])
                 and _sha(item['new_sha256']) and item['old_sha256'] != item['new_sha256'], 'unsupported managed path/binding')
        path = item['path']; seen.add(path)
        _require(isinstance(saved, dict) and set(saved) == {'path', 'old_base64', 'public_base64', 'package_base64'}
                 and saved['path'] == path, 'managed archived byte schema')
        old, public, package = [base64.b64decode(saved[k], validate=True) for k in ('old_base64', 'public_base64', 'package_base64')]
        _require(digest(old) == item['old_sha256'] and public == package and digest(public) == item['new_sha256']
                 and manifest['files'].get(path) == item['new_sha256']
                 and manifest['files'].get('.hmigbot-ios/plugin/' + MANAGED[path]) == item['new_sha256'], 'managed manifest/public/package byte mismatch')
    return seen


def _managed_upgrade(project, review, before):
    from .ios_scheduler import ROOT
    _require(Path(ROOT).resolve() == safe_child(project, '.hmigbot-ios/plugin'), 'managed proof requires the installed public runtime')
    manifest_path = safe_child(project, '.hmigbot-ios/install.json')
    proof = review['managed_upgrade']
    _require(isinstance(proof, dict) and digest(manifest_path.read_bytes()) == proof.get('install_manifest_sha256'), 'managed install manifest digest')
    _require(isinstance(proof.get('files'), list), 'managed files schema')
    record = {'proof': proof, 'files': []}
    for item in proof['files']:
        _require(isinstance(item, dict) and item.get('path') in MANAGED, 'unsupported managed path')
        path = item['path']
        _require(before.get(path) == item.get('old_sha256'), 'managed original dispatch binding')
        record['files'].append({'path': path, 'old_base64': base64.b64encode(Path(item['old_copy']).read_bytes()).decode('ascii'),
                                'public_base64': base64.b64encode(safe_child(project, path).read_bytes()).decode('ascii'),
                                'package_base64': base64.b64encode(safe_child(project, '.hmigbot-ios/plugin/' + MANAGED[path]).read_bytes()).decode('ascii')})
    paths = _managed_binding(review, read_json(manifest_path), record)
    return paths, manifest_path.read_bytes(), record


def _cache_names(review, presence):
    _require(isinstance(presence, dict) and set(presence) == {'journal_before_present'}
             and type(presence['journal_before_present']) is bool, 'cache control presence schema')
    names = {'review.json', 'result.json', 'plan.json', 'contract.json', 'dispatch.json',
             'dispatch-evidence.json', 'receipt.json', 'replan-request.json', 'state-before.json',
             'control-presence.json', 'inputs.json', 'state-after.json', 'dispatch-after.json', 'journal-after.json'}
    if presence['journal_before_present']:
        names.add('journal-before.json')
    if 'authoring_rebind' in review:
        names.update({'authoring-old.json', 'authoring-new.json'})
    if 'managed_upgrade' in review:
        names.update({'managed-install.json', 'managed-upgrade.json'})
    return names


def _seal_archive(archive, review):
    """Write last, once: a missing seal is incomplete evidence, never resumable."""
    _require(not (archive / 'seal.json').exists(), 'first cache seal already exists')
    names = _cache_names(review, read_json(archive / 'control-presence.json'))
    _require({p.name for p in archive.iterdir()} == names, 'first cache evidence files differ')
    write_json(archive / 'seal.json', {'version': 1, 'review_sha256': digest(json_bytes(review)),
                                     'files': {name: digest((archive / name).read_bytes()) for name in sorted(names)}})


def _cached_result(project, archive, review, key):
    _require((archive / 'review.json').read_bytes() == json_bytes(review), 'prior evidence conflict')
    seal = read_json(archive / 'seal.json')
    names = _cache_names(review, read_json(archive / 'control-presence.json'))
    _require(isinstance(seal, dict) and set(seal) == {'version', 'review_sha256', 'files'}
             and type(seal['version']) is int and seal['version'] == 1 and seal['review_sha256'] == key
             and isinstance(seal['files'], dict) and set(seal['files']) == names, 'cache seal identity/files')
    _require({p.name for p in archive.iterdir()} == names | {'seal.json'}, 'cache evidence files differ')
    for name in names:
        _require(_sha(seal['files'][name]) and digest((archive / name).read_bytes()) == seal['files'][name],
                 'cache evidence digest: ' + name)
    old, ident, attempt, wave = review['old'], review['task_id'], review['attempt'], review['wave']
    for name, field in [('plan.json', 'plan_sha256'), ('contract.json', 'contract_sha256'),
                        ('dispatch.json', 'dispatch_sha256'), ('dispatch-evidence.json', 'dispatch_evidence_sha256'),
                        ('receipt.json', 'receipt_sha256')]:
        _require(seal['files'][name] == old[field], 'cache original binding: ' + name)
    _require(seal['files']['replan-request.json'] == review['replan_request']['sha256'], 'cache replan binding')
    if 'authoring_rebind' in review:
        binding = review['authoring_rebind']
        _require(seal['files']['authoring-old.json'] == binding['old_sha256']
                 and seal['files']['authoring-new.json'] == binding['new_sha256'], 'cache authoring binding')
    if 'managed_upgrade' in review:
        _require(seal['files']['managed-install.json'] == review['managed_upgrade']['install_manifest_sha256'], 'cache managed manifest binding')
        record = read_json(archive / 'managed-upgrade.json')
        _managed_binding(review, read_json(archive / 'managed-install.json'), record)
        before = read_json(archive / 'dispatch-evidence.json')['before_files']
        _require(all(before.get(item['path']) == item['old_sha256'] for item in review['managed_upgrade']['files']), 'cache managed original dispatch binding')
    result = read_json(archive / 'result.json')
    fields = {'status', 'task_id', 'attempt', 'archive', 'review_sha256', 'state_writer', 'action',
              'prior_success_inherited', 'behavior_verified'}
    _require(isinstance(result, dict) and set(result) == fields
             and result['status'] == 'blocked_attempt_terminated' and result['task_id'] == ident
             and type(result['attempt']) is int and result['attempt'] == attempt
             and result['archive'] == archive.relative_to(project).as_posix() and result['review_sha256'] == key
             and result['state_writer'] == 'original land_results --missing-as-failed'
             and result['prior_success_inherited'] is False and result['behavior_verified'] is False,
             'cache failure-only result identity/flags')
    receipt = read_json(archive / 'receipt.json')
    _require(receipt.get('task_id') == ident and receipt.get('plan_sha256') == old['plan_sha256']
             and receipt.get('source_sha256') == old['source_sha256'] and receipt.get('status') == 'blocked'
             and receipt.get('final_state') == 'BLOCKED' and receipt.get('behavior_verified') is False,
             'cache original blocked receipt identity')
    action = result['action']
    action_fields = {'ok', 'wave', 'workflow_status', 'landed', 'pending', 'reduces', 'skipped', 'escalations',
                     'approval', 'errors', 'journal', 'next', 'ios_blocked_receipts', 'ios_runtime_cleanup'}
    _require(isinstance(action, dict) and set(action) <= action_fields and action.get('ok') is False and action.get('wave') == wave
             and isinstance(action.get('landed'), list) and len(action['landed']) == 1, 'cache original failed action')
    _require('workflow_status' not in action or action['workflow_status'] in {'RUNNING', 'FAILED', 'BLOCKED'},
             'cache workflow cannot claim success')
    row = action['landed'][0]
    failures = {'RETRY_NEEDED', 'RETRY_EXHAUSTED', 'FAIL', 'INFRA_FAIL'}
    _require(isinstance(row, dict) and row.get('id') == ident and type(row.get('attempt')) is int
             and row['attempt'] == attempt and row.get('status') in failures, 'cache landed failure identity')
    blocked = action.get('ios_blocked_receipts')
    _require(blocked == [{'id': ident, 'archive': f'spec/reports/ios-blocked-receipts/{wave}/{ident}/{old["receipt_sha256"]}.json',
                         'sha256': old['receipt_sha256'], 'native_status': 'blocked', 'original_disposition': 'missing-as-failed'}],
             'cache blocked writer evidence')
    journal = read_json(archive / 'journal-after.json')
    rows = [r for r in journal.get('operation_outputs', []) if r.get('workflow_id') == wave
            and r.get('task_id') == ident and r.get('attempt') == attempt]
    _require(rows and all(type(r.get('attempt')) is int and r.get('status') == row['status'] for r in rows),
             'cache original journal failure mismatch')
    state = read_json(archive / 'state-after.json')['waves'][wave]['tasks']
    state = list(state.values()) if isinstance(state, dict) else state
    _require(any(r.get('id') == ident and r.get('status') == 'failed' for r in state)
             and not any(r.get('id') == ident and r.get('status') == 'done' for r in state), 'cache original failed state')
    inputs = read_json(archive / 'inputs.json')
    _require(digest(json_bytes(inputs['old'])) == old['baseline_inputs_sha256']
             and digest(json_bytes(inputs['new'])) == review['new']['baseline_inputs_sha256'], 'cache input collection binding')
    return result


def recover_blocked(project, review_path):
    from . import ios_scheduler as scheduler
    from .native_pipeline import context
    from .ios_facts import validate_graph
    from .ios_harness import ac_inventory
    from .harness_schema import validate
    from .plan_contract import profile, contract_revision

    review = _review(review_path)
    source, project = context(project)
    wave, ident, attempt = review['wave'], review['task_id'], review['attempt']
    key = digest(json_bytes(review))
    archive = safe_child(project, 'spec/reports/ios-blocked-recovery/' + key)
    result_path = archive / 'result.json'
    if result_path.is_file():
        # A completed exact request is immutable and repeatable even after replan.
        return _cached_result(project, archive, review, key)
    request_ref = review['replan_request']
    _require(isinstance(request_ref, dict) and set(request_ref) == {'path', 'sha256'}
             and isinstance(request_ref['path'], str) and request_ref['path'].startswith('spec/ref/')
             and request_ref['path'].endswith('.json') and _sha(request_ref['sha256']), 'replan request schema/path')
    request_path = safe_child(project, request_ref['path'])
    _require(digest(request_path.read_bytes()) == request_ref['sha256'], 'replan request digest')
    scheduler.generate(project, request_path, validate_only=True)
    old = review['old']
    plan_path = project / f'spec/waves/plan-{wave}.json'
    contract_path = project / 'spec/blueprint/contracts.json'
    dispatch_path = project / 'spec/state/dispatch.json'
    evidence_path = project / f'spec/reports/ios-dispatch-{wave}.json'
    for name, path in [('plan', plan_path), ('contract', contract_path), ('dispatch', dispatch_path),
                       ('dispatch_evidence', evidence_path)]:
        _require(digest(path.read_bytes()) == old[name + '_sha256'], name + ' binding changed')
    plan, contract, dispatch, evidence = map(read_json, (plan_path, contract_path, dispatch_path, evidence_path))
    _require(plan.get('ios_adapter_version') == 2 and contract.get('ios_adapter_version') == 2, 'native v2 required')
    _require(profile(project) == contract.get('spec_contract_version'), 'profile changed')
    _require(contract.get('contract_revision') == old['contract_revision']
             and contract_revision(project) == review['new']['contract_revision'], 'tool revision binding changed')
    _require(digest(json_bytes({k: v for k, v in plan.items() if k != 'contract_hash'}))
             == contract.get('plan_identity_sha256'), 'plan IR changed')
    _require(scheduler.kernel().compute_contract_hash(project / 'spec/blueprint', []) == plan['contract_hash'],
             'original six-item contract changed')
    for path, expected in contract.get('prompt_hashes', {}).items():
        _require(digest(safe_child(project, path).read_bytes()) == expected, 'prompt changed: ' + path)
    graph, _ = validate_graph(source, project)
    _require(graph['source_sha256'] == old['source_sha256'] == contract['source_sha256']
             and digest(json_bytes(graph)) == old['graph_sha256'] == contract['graph_sha256'], 'source/graph changed')
    _require(evidence.get('plan_sha256') == old['plan_sha256'] and ident in evidence.get('task_ids', []), 'dispatch evidence identity')
    prefix = 'spec/state/fence-snapshot/'
    before = evidence['before_files']
    pinned_fence = {p: v for p, v in before.items() if p.startswith(prefix)}
    _require(pinned_fence and pinned_fence == scheduler._fence_files(project), 'sealed original fence changed/missing')
    _require(pinned_fence.get(prefix + 'spec/blueprint/contracts.json') == old['contract_sha256'], 'fence contract binding')
    tasks = {t['id']: t for t in plan['tasks']}
    definitions = {t['id']: t for t in contract['ios_tasks']}
    _require(ident in tasks and ident in definitions, 'unknown task')
    row = dispatch.get('waves', {}).get(wave, {})
    _require(row.get('contract_hash') == plan['contract_hash'], 'dispatch contract identity')
    journal_path = project / 'spec/state/journal.json'
    journal = read_json(journal_path) if journal_path.exists() else {}
    landed, _ = scheduler.kernel().journal_indexes(journal, wave)
    pending = {i: r for i, r in row.get('dispatched', {}).items() if r.get('attempts', 0) > landed.get(i, 0)}
    _require(set(pending) == {ident} and pending[ident].get('attempts') == attempt
             and landed.get(ident, 0) == attempt - 1, 'only the explicit original pending attempt may recover')
    for field in ('prompt_file', 'result_path', 'resume_key'):
        _require(pending[ident].get(field) == tasks[ident].get(field), 'dispatch task identity: ' + field)
    receipt_path = safe_child(project, tasks[ident]['result_path'])
    raw = receipt_path.read_bytes()
    _require(digest(raw) == old['receipt_sha256'], 'receipt binding changed')
    receipt = validate(read_json(receipt_path), 'receipt')
    _require(receipt.get('ios_receipt_version') == 2 and receipt.get('task_id') == ident
             and receipt.get('source_sha256') == old['source_sha256']
             and receipt.get('plan_sha256') == old['plan_sha256'], 'stale/other task receipt')
    _require(receipt.get('status') == 'blocked' and receipt.get('final_state') == 'BLOCKED'
             and receipt.get('behavior_verified') is False and receipt.get('findings'), 'honest blocked receipt required')
    # Receipts have no attempt field: only attempt one can be authenticated
    # from this protocol. Later attempts require an explicit future protocol.
    _require(attempt == 1, 'receipt protocol cannot authenticate later attempts')
    definition = definitions[ident]
    from .receipt_outputs import validate_outputs
    validate_outputs(project, receipt, definition, before=before)
    _require(set(receipt.get('ac_ids', [])) == set(definition.get('ac_ids', [])), 'receipt AC mismatch')
    if wave == 'domains':
        _require(set(ac_inventory(project)) == {a for t in definitions.values() for a in t.get('ac_ids', [])}, 'AC inventory changed')
    current = scheduler.baseline_inputs(project, wave)
    previous = contract['input_hashes']
    _require(digest(json_bytes(previous)) == old['baseline_inputs_sha256']
             and digest(json_bytes(current)) == review['new']['baseline_inputs_sha256'], 'baseline digest bindings')
    reviewed = {}
    for change in review['changes']:
        _require(isinstance(change, dict) and set(change) == {'path', 'old_sha256', 'new_sha256'}, 'change schema')
        path = change['path']
        safe_child(project, path)
        # Only already-frozen prose Spec inputs; no source/graph, arbitrary
        # config, new control file, plan/prompt or App escape via a review.
        _require(path in previous and path.startswith('spec/baseline/') and path.endswith('.md')
                 and path not in reviewed and _sha(change['old_sha256']) and _sha(change['new_sha256']), 'unsupported reviewed path: ' + str(path))
        _require(previous[path] == change['old_sha256'] and current.get(path) == change['new_sha256']
                 and change['old_sha256'] != change['new_sha256'], 'reviewed change binding: ' + path)
        reviewed[path] = change
    differences = {p for p in previous.keys() | current.keys() if previous.get(p) != current.get(p)}
    _require(differences == set(reviewed), 'unreviewed baseline changes')
    for refs in contract.get('task_inputs', {}).values():
        for ref in refs:
            expected = reviewed.get(ref['path'], {}).get('new_sha256', ref['sha256'])
            _require(digest(safe_child(project, ref['path']).read_bytes()) == expected, 'unreviewed task input change')
    derived = set()
    managed = None
    rebind = review.get('authoring_rebind')
    if rebind is not None:
        _require(isinstance(rebind, dict) and set(rebind) == {'path', 'previous_copy', 'old_sha256', 'new_sha256'}, 'authoring rebind schema')
        path = rebind['path']
        _require(path == 'spec/ref/native-authoring-reviewed-input.json'
                 and _sha(rebind['old_sha256']) and _sha(rebind['new_sha256'])
                 and before.get(path) == rebind['old_sha256'], 'authoring original dispatch binding')
        previous_copy = Path(rebind['previous_copy'])
        _require(digest(previous_copy.read_bytes()) == rebind['old_sha256'], 'authoring old copy digest')
        current_copy = safe_child(project, path)
        _require(digest(current_copy.read_bytes()) == rebind['new_sha256'], 'authoring new digest')
        old_authoring, new_authoring = read_json(previous_copy), read_json(current_copy)
        _require(isinstance(old_authoring, dict) and isinstance(new_authoring, dict)
                 and 'inventory_sha256' in old_authoring and 'inventory_sha256' in new_authoring
                 and {k: v for k, v in old_authoring.items() if k != 'inventory_sha256'}
                 == {k: v for k, v in new_authoring.items() if k != 'inventory_sha256'}, 'authoring changed beyond inventory binding')
        from .native_authoring import _inventory
        inventory = _inventory(project)[3]
        _require(new_authoring['inventory_sha256'] == digest(json_bytes(inventory))
                 and new_authoring.get('source_sha256') == old['source_sha256'], 'authoring current inventory/source binding')
        derived.add(path)
    if 'managed_upgrade' in review:
        managed_paths, managed_manifest, managed_record = _managed_upgrade(project, review, before)
        derived.update(managed_paths)
        managed = (managed_manifest, managed_record)
    actual = scheduler.execution_files(project)
    changed = {p for p in before.keys() | actual.keys() if before.get(p) != actual.get(p)}
    _require(not (changed - set(definition['ownership']) - set(reviewed) - {request_ref['path']} - derived), 'changed files outside ownership/review: '
             + ','.join(sorted(changed - set(definition['ownership']) - set(reviewed) - {request_ref['path']} - derived)))
    # All validation precedes the first write. Never overwrite first evidence;
    # an interrupted attempt is stopped for manual audit rather than replayed.
    _require(not archive.exists(), 'incomplete prior recovery requires manual audit')
    archive.mkdir(parents=True)
    write_json(archive / 'review.json', review)
    for name, path in [('plan.json', plan_path), ('contract.json', contract_path), ('dispatch.json', dispatch_path),
                       ('dispatch-evidence.json', evidence_path), ('receipt.json', receipt_path), ('replan-request.json', request_path),
                       ('state-before.json', project / 'spec/state/state.json')]:
        atomic_write(archive / name, path.read_bytes())
    if journal_path.exists():
        atomic_write(archive / 'journal-before.json', journal_path.read_bytes())
    write_json(archive / 'control-presence.json', {'journal_before_present': journal_path.exists()})
    write_json(archive / 'inputs.json', {'old': previous, 'new': current, 'changed': sorted(changed), 'reviewed': reviewed})
    if rebind is not None:
        atomic_write(archive / 'authoring-old.json', previous_copy.read_bytes())
        atomic_write(archive / 'authoring-new.json', current_copy.read_bytes())
    if managed is not None:
        atomic_write(archive / 'managed-install.json', managed[0])
        write_json(archive / 'managed-upgrade.json', managed[1])
    action = scheduler._land_native_receipts(project, wave, plan_path, [(ident, receipt_path)])
    after = read_json(journal_path)
    rows = [r for r in after.get('operation_outputs', []) if r.get('workflow_id') == wave
            and r.get('task_id') == ident and r.get('attempt') == attempt]
    _require(rows and all(r.get('status') in {'RETRY_NEEDED', 'RETRY_EXHAUSTED', 'FAIL', 'INFRA_FAIL'} for r in rows), 'original writer did not record failure')
    state = read_json(project / 'spec/state/state.json')['waves'][wave]['tasks']
    state = list(state.values()) if isinstance(state, dict) else state
    _require(not any(r.get('id') == ident and r.get('status') == 'done' for r in state), 'unexpected successful state')
    _require(receipt_path.read_bytes() == raw, 'native receipt restoration failed')
    _require(scheduler.baseline_inputs(project, wave) == current, 'original writer changed reviewed Spec')
    for name in ('state', 'dispatch', 'journal'):
        path = project / f'spec/state/{name}.json'
        atomic_write(archive / (name + '-after.json'), path.read_bytes())
    result = {'status': 'blocked_attempt_terminated', 'task_id': ident, 'attempt': attempt,
              'archive': archive.relative_to(project).as_posix(), 'review_sha256': key,
              'state_writer': 'original land_results --missing-as-failed', 'action': action,
              'prior_success_inherited': False, 'behavior_verified': False}
    write_json(result_path, result)
    _seal_archive(archive, review)
    return result
