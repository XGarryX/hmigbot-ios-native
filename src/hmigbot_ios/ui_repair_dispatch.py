"""Execute evidenced repair groups and current, affected rechecks.

Explicit project-owned commands provide repairs/build/checks. This adapter is
not a device backend, a second findings writer, or an application PASS oracle.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from contextlib import contextmanager
import fcntl
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import time

from .core import MigrationError, digest, json_bytes, read_json, source_snapshot, write_json
from .quality_views import target_inputs
from .repair_triage import require, project_path, triage, harvested
from .ui_validation_evidence import impact_plan, pair_evidence, build_identity

ROOT = 'spec/reports/repair-recheck'
PASSED = {'PASS', 'passed', 'success', 'built'}


def _project(value):
    project = Path(value).expanduser().resolve(strict=True)
    require(project.is_dir(), 'Expected target project directory')
    require(project != Path(__file__).resolve().parents[2], 'Repair execution cannot target its tool runtime')
    return project


def _binding(project):
    cfg_path = project_path(project, '.migbot/config.json')
    cfg = read_json(cfg_path)
    require(cfg.get('source_platform') == 'ios' and isinstance(cfg.get('ios'), str), 'Expected configured iOS project')
    source = Path(cfg['ios']);source = source if source.is_absolute() else project/source
    source = source.resolve(strict=True)
    require(source != project and not source.is_relative_to(project) and not project.is_relative_to(source),
            'Source and target must be separate')
    protected = {'.migbot/config.json': digest(cfg_path.read_bytes())}
    for root in ('spec/baseline', 'spec/blueprint', 'spec/verification'):
        folder = project_path(project, root)
        if folder.exists():
            for path in folder.rglob('*'):
                require(not path.is_symlink(), 'Protected plan/source evidence contains a symlink')
                if path.is_file():protected[path.relative_to(project).as_posix()] = digest(path.read_bytes())
    source_sha = source_snapshot(source)['sha256']
    contract = project_path(project, 'spec/execution/execution-contract.json')
    if contract.exists():
        from .plan_contract import contract_revision, structural_digest
        frozen = read_json(contract)
        require(frozen.get('source_sha256') == source_sha and
                frozen.get('contract_revision') == contract_revision(project),
                'Execution source/tool rules changed; reviewed replan is required')
        require(isinstance(frozen.get('plan_inputs'), dict) and frozen['plan_inputs'],
                'Repair requires frozen plan inputs')
        for relative, sha in frozen['plan_inputs'].items():
            path = project_path(project, relative)
            actual = structural_digest(path.read_text(encoding='utf-8-sig'), artifact=relative) if relative.endswith('.md') else digest(path.read_bytes())
            require(actual == sha, 'Frozen plan input changed: ' + relative)
        protected[contract.relative_to(project).as_posix()] = digest(contract.read_bytes())
    rules = {name: digest(Path(__file__).with_name(name).read_bytes()) for name in
             ('ui_repair_dispatch.py', 'repair_triage.py', 'ui_validation_evidence.py', 'ui_cross_platform.py', 'gate_policy.py')}
    return {'source_sha256': source_sha, 'protected_inputs': protected,
            'rules': rules}


def _changed(before, after):
    return sorted(p for p in set(before) | set(after) if before.get(p) != after.get(p))


def _command(project, value):
    require(isinstance(value, dict), 'Expected an explicit command object')
    argv = value.get('argv')
    require(isinstance(argv, list) and argv and all(isinstance(a, str) and a and '\0' not in a for a in argv),
            'Command argv must be a nonempty string list; shell commands are unsupported')
    forbidden = {'sh', 'bash', 'zsh', 'fish', 'osascript', 'open', 'sudo', 'ssh', 'cua'}
    require(Path(argv[0]).name not in forbidden, 'Desktop, shell, remote or privilege command is outside repair protocol')
    executable = shutil.which(argv[0])
    require(executable is not None, 'Command executable unavailable: ' + argv[0])
    executable = str(Path(executable).resolve(strict=True))
    timeout = value.get('timeout_seconds', 300)
    require(type(timeout) in (int, float) and math.isfinite(timeout) and 0 < timeout <= 7200, 'Invalid command timeout')
    pinned = {executable: digest(Path(executable).read_bytes())}
    for token in argv[1:]:
        if token.endswith(('.py', '.sh', '.js', '.cjs', '.mjs')):
            path = Path(token)
            path = project_path(project, token) if not path.is_absolute() else path
            require(path.is_file() and not path.is_symlink(), 'Command script is unavailable or a symlink: ' + token)
            pinned[str(path.resolve())] = digest(path.read_bytes())
    return {'argv': [executable, *argv[1:]], 'timeout_seconds': timeout, 'pinned': pinned}


def _validate(project, request, diagnosis):
    require(isinstance(request, dict) and request.get('schema_version') == 1
            and type(request['schema_version']) is int, 'Unsupported repair input schema')
    ident = request.get('run_id')
    require(isinstance(ident, str) and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,100}', ident), 'Expected unique portable run_id')
    checkpoints = request.get('checkpoint_ids')
    # The existing algorithm remains the authority for full/affected selection.
    impact_plan(checkpoints, [], request.get('ownership'), phase=request.get('phase', 'intermediate'))
    workers = request.get('available_slots', 1)
    require(type(workers) is int and workers > 0, 'Actual available_slots must be a positive integer')
    require(('usage_ledger' in request) == ('usage_run_id' in request), 'Selected usage ledger and run id must be supplied together')
    if 'usage_ledger' in request:
        project_path(project, request['usage_ledger'])
        require(isinstance(request['usage_run_id'], str) and request['usage_run_id'], 'Usage run id is missing')
    findings = {f['id']: f for f in diagnosis['findings']}
    repairs = request.get('repairs', [])
    require(isinstance(repairs, list), 'Expected repair list')
    ids, assigned = set(), set()
    contract_path = project_path(project, 'spec/execution/execution-contract.json')
    contract = read_json(contract_path) if contract_path.exists() else {}
    units = contract.get('plan_items', {})
    commands = {}
    for repair in repairs:
        require(isinstance(repair, dict) and isinstance(repair.get('id'), str) and repair['id']
                and repair['id'] not in ids, 'Duplicate/missing repair id')
        ids.add(repair['id'])
        refs = repair.get('finding_ids')
        require(isinstance(refs, list) and refs and len(refs) == len(set(refs))
                and set(refs) <= findings.keys() and not assigned & set(refs), 'Repair finding selection is invalid')
        assigned.update(refs)
        require({findings[f]['owner_stage'] for f in refs} == {'execute'},
                'Source/spec/plan/tool owners must recover in their original author stage')
        cause_by_id = {f: cause for cause in diagnosis['cause_groups'] for f in cause['finding_ids']}
        require(all(cause_by_id[f]['kind'] in {'code', 'unknown'} for f in refs),
                'Environment/tool/source/plan diagnosis must use its original recovery path')
        task = repair.get('task_id')
        require(task in units and units[task].get('scope') == 'product', 'Repair must belong to a real current product plan item')
        writes = repair.get('write_files')
        require(isinstance(writes, list) and writes and len(writes) == len(set(writes))
                and set(writes) <= set(units[task].get('ownership', [])), 'Repair writes exceed its frozen plan ownership')
        for name in writes:
            project_path(project, name)
            require(not name.startswith(('spec/', '.migbot/', '.hmigbot-ios/', '.agents/', '.codex/')),
                    'Target repair may not rewrite source/plan/control/tool files')
            require('/resources/' not in name or not name.endswith('.json'),
                    'Shared resource JSON uses resource-delta; repair must not bypass its unique writer')
        cps = repair.get('checkpoint_ids')
        require(isinstance(cps, list) and cps and len(cps) == len(set(cps)) and set(cps) <= set(checkpoints),
                'Repair needs actual checkpoint responsibilities')
        commands['repair:' + repair['id']] = _command(project, repair.get('command'))
    build = request.get('build')
    require(isinstance(build, dict) and isinstance(build.get('report'), str) and isinstance(build.get('artifact'), str),
            'Repair round requires an explicit build command/report/artifact')
    commands['build'] = _command(project, build)
    project_path(project, build['artifact'])
    checks = request.get('checks')
    require(isinstance(checks, list) and checks, 'Actual recheck commands must be declared')
    check_ids = set()
    for check in checks:
        require(isinstance(check, dict) and isinstance(check.get('id'), str) and check['id']
                and check['id'] not in check_ids, 'Duplicate/missing recheck id')
        check_ids.add(check['id'])
        cps = check.get('checkpoint_ids')
        require(isinstance(cps, list) and cps and len(cps) == len(set(cps)) and set(cps) <= set(checkpoints),
                'Recheck must name its checkpoint scope')
        refs = check.get('finding_ids', [])
        require(isinstance(refs, list) and len(refs) == len(set(refs)) and set(refs) <= findings.keys(),
                'Recheck finding selection is invalid')
        require(isinstance(check.get('requires_build', True), bool), 'requires_build must be boolean')
        path = check.get('report')
        require(isinstance(path, str), 'Recheck needs original producer report path')
        require(all(findings[f]['report'] == path for f in refs), 'Recheck must rerun the original finding producer report')
        if 'pair' in check:
            require(isinstance(check['pair'], dict) and set(check['pair']) == {'source', 'target', 'current', 'rules'},
                    'UI recheck needs source/target/current/rules input paths')
            for name in check['pair'].values():project_path(project, name)
        if 'case_map' in check:
            mapping = check['case_map']
            require(isinstance(mapping, dict) and set(mapping) == set(cps),
                    'Behavior case_map must map every declared checkpoint')
            verification = read_json(project_path(project, 'spec/verification/ios-behavior.json'))
            known_cases = {c['id'] for c in verification.get('cases', [])}
            require(all(isinstance(ids, list) and ids and all(isinstance(i, str) for i in ids)
                        and len(ids) == len(set(ids)) and set(ids) <= known_cases for ids in mapping.values()),
                    'Behavior case_map must reference actual frozen original cases')
        commands['check:' + check['id']] = _command(project, check)
    for command in [build, *checks]:
        name = command['report'];project_path(project, name)
        require(name.startswith(('spec/reports/', 'spec/fix/')) and name.endswith('.json'),
                'Build/recheck reports must use existing project evidence roots')
    return commands


def _groups(repairs, impact):
    groups = []
    for repair in repairs:
        keys = {i for i, g in enumerate(impact['disjoint_fix_groups']) if
                set(g['checkpoints']) & set(repair['checkpoint_ids'])}
        item = {'repairs': [repair], 'files': set(repair['write_files']), 'impact_groups': keys}
        matches = [g for g in groups if g['files'] & item['files'] or g['impact_groups'] & keys
                   or repair['task_id'] in {r['task_id'] for r in g['repairs']}]
        for prior in matches:
            item['repairs'] += prior['repairs'];item['files'] |= prior['files'];item['impact_groups'] |= prior['impact_groups']
            groups.remove(prior)
        groups.append(item)
    return groups


def _dispatch(groups, commands, project, folder, slots, diagnosis, units, request):
    priority = {f: c['priority_consumers'] for c in diagnosis['cause_groups'] for f in c['finding_ids']}
    tasks = {r['task_id']: i for i, g in enumerate(groups) for r in g['repairs']}
    parents = {i: {tasks[p] for r in g['repairs'] for p in units[r['task_id']].get('parents', [])
                   if p in tasks and tasks[p] != i} for i, g in enumerate(groups)}
    # Unknown-file groups run after located groups and cannot overlap each other.
    located = {i for i, g in enumerate(groups) if g['impact_groups']}
    unlocated = [i for i in range(len(groups)) if i not in located]
    if any(parents[i] & set(unlocated) for i in located):
        # Missing UI ownership cannot reverse a real prerequisite. Collapse
        # to one serial topological group instead of guessing safe parallelism.
        combined = {'repairs':[r for g in groups for r in g['repairs']],
                    'files':set().union(*(g['files'] for g in groups)), 'impact_groups':set()}
        return _dispatch([combined], commands, project, folder, 1, diagnosis, units, request)
    for index, ident in enumerate(unlocated):parents[ident] |= located | set(unlocated[:index])
    verified = set()
    while len(verified) < len(groups):
        ready = {i for i in range(len(groups)) if i not in verified and parents[i] <= verified}
        require(ready, 'Cyclic repair prerequisites; no repair was started')
        verified |= ready
    pending = set(range(len(groups)));done = {};calls = []
    def work(ident):
        group = groups[ident];remaining = list(group['repairs']);completed = set();receipts = []
        while remaining:
            internal = {r['task_id'] for r in remaining}
            ready = [r for r in remaining if not set(units[r['task_id']].get('parents', [])) & internal]
            require(ready, 'Cyclic repair dependencies inside a conflict group')
            ready.sort(key=lambda r: (-max((priority[f] for f in r['finding_ids']), default=0), r['id']))
            repair = ready[0]
            if 'usage_ledger' in request:
                from .usage_budget import check_for_dispatch
                try:
                    budget = check_for_dispatch(project_path(project, request['usage_ledger']),
                        run_id=request['usage_run_id'], project_root=project)
                except (MigrationError, OSError, ValueError, KeyError, TypeError) as exc:
                    budget = {'can_continue':False, 'reasons':['Unverified selected usage budget: '+str(exc)]}
                if not budget['can_continue']:
                    receipts.append({'operation': 'repair:' + repair['id'], 'actual_call_now':False,
                        'status':'blocked_budget', 'exit_code':None, 'reasons':budget.get('reasons', [])})
                    write_json(folder/('call-' + digest(('repair:' + repair['id']).encode())[:20] + '.json'), receipts[-1])
                    break
            receipt = _call(project, folder, 'repair:' + repair['id'], commands['repair:' + repair['id']], 'rework')
            receipts.append(receipt)
            if receipt['exit_code'] != 0:break
            completed.add(repair['task_id']);remaining.remove(repair)
        return receipts
    with ThreadPoolExecutor(max_workers=slots) as executor:
        running = {}
        while pending or running:
            blocked = {i for i in pending if any(p in done and not done[p] for p in parents[i])}
            for ident in blocked:done[ident] = False
            pending -= blocked
            ready = sorted((i for i in pending if parents[i] <= done.keys() and all(done[p] for p in parents[i])),
                key=lambda i: (-max((priority[f] for r in groups[i]['repairs'] for f in r['finding_ids']), default=0), i))
            for ident in ready[:max(0, slots-len(running))]:
                pending.remove(ident);running[executor.submit(work, ident)] = ident
            if not running:
                require(not pending, 'Cyclic repair group prerequisites; retain original findings')
                break
            finished, _ = wait(running, return_when=FIRST_COMPLETED)
            for future in finished:
                ident = running.pop(future);receipts = future.result();calls.extend(receipts)
                done[ident] = len(receipts) == len(groups[ident]['repairs']) and all(c['exit_code'] == 0 for c in receipts)
    return calls


def _observe(project, operation, category):
    try:
        from .execution_measurements import observe_start
        return observe_start(project, 'verify', operation, category=category)
    except (ImportError, MigrationError, OSError, ValueError):
        return None


def _observed(project, token, status, code):
    try:
        from .execution_measurements import observe_end
        observe_end(project, token, status, exit_code=code)
    except (ImportError, MigrationError, OSError, ValueError):
        pass


def _call(project, folder, name, command, category):
    for path, expected in command['pinned'].items():
        require(digest(Path(path).read_bytes()) == expected, 'Command implementation changed before execution')
    token = _observe(project, name, category)
    started = time.monotonic();status = 'failed';code = None
    try:
        result = subprocess.run(command['argv'], cwd=project, shell=False, capture_output=True,
                                timeout=command['timeout_seconds'])
        code = result.returncode;stdout, stderr = result.stdout, result.stderr
        status = 'returned' if code == 0 else 'failed'
    except subprocess.TimeoutExpired as exc:
        stdout, stderr = exc.stdout or b'', exc.stderr or b'';status = 'timed_out'
    except OSError as exc:
        stdout, stderr = b'', str(exc).encode();status = 'unavailable'
    finally:
        _observed(project, token, status, code)
    receipt = {'operation': name, 'argv': command['argv'], 'actual_call_now': True,
        'status': status, 'exit_code': code, 'elapsed_seconds': time.monotonic()-started,
        'pinned_commands': command['pinned']}
    for channel, raw in [('stdout', stdout), ('stderr', stderr)]:
        path = folder/(digest(name.encode())[:20] + '.' + channel + '.txt')
        path.write_bytes(raw);receipt[channel] = {'path': path.relative_to(project).as_posix(), 'sha256': digest(raw)}
    write_json(folder/('call-' + digest(name.encode())[:20] + '.json'), receipt)
    return receipt


def _report(project, path):
    target = project_path(project, path)
    require(target.is_file(), 'Current command did not produce its report: ' + path)
    value = read_json(target)
    require(isinstance(value, dict), 'Current check report is not an object')
    return value, digest(target.read_bytes())


def _coverage(value, check, binding, target):
    """Scope comes from actual producer results, never manifest labels alone."""
    requested = set(check['checkpoint_ids'])
    if 'pair' in check:
        return {p['id'] for p in value.get('pairs', []) if p.get('status') == 'compared'
                and p.get('assessment', {}).get('evidence_complete') is True}
    if 'observations' in value:
        if (value.get('source_sha256') != binding['source_sha256'] or
                value.get('target_input_hashes') != target):
            return set()
        observations = value['observations']
        if not isinstance(observations, list):return set()
        performed = {o['id'] for o in observations if isinstance(o, dict) and isinstance(o.get('id'), str)
                     and o.get('status') in {'observed_pass', 'observed_fail'}
                     and type(o.get('exit_code')) is int}
        mapping = check.get('case_map', {key:[key] for key in requested})
        return {key for key, ids in mapping.items() if set(ids) <= performed}
    declared = value.get('checkpoint_ids')
    if (not isinstance(declared, list) or not all(isinstance(c, str) for c in declared)
            or len(declared) != len(set(declared))):return set()
    return set(declared)


@contextmanager
def _lock(project):
    folder = project_path(project, ROOT);folder.mkdir(parents=True, exist_ok=True)
    path = project_path(project, ROOT + '/.lock')
    fd = os.open(path, os.O_CREAT | os.O_RDWR | getattr(os, 'O_NOFOLLOW', 0), 0o600)
    try:
        try:fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:raise MigrationError('Another repair round is running; retain its evidence and wait') from exc
        yield
    finally:os.close(fd)


def run(project, request):
    project = _project(project)
    diagnosis = triage(project, request)
    commands = _validate(project, request, diagnosis)  # Validate everything before running any command.
    with _lock(project):
        require(not project_path(project, 'spec/execution/resource-deltas/pending.json').exists(),
                'Resource transaction pending; recover its original scope first')
        folder = project_path(project, ROOT + '/' + request['run_id'])
        require(not folder.exists(), 'Repair run already exists; preserve evidence and use a new run_id')
        folder.mkdir()
        write_json(folder/'input.json', request)
        binding = _binding(project);before = target_inputs(project)
        planned_writes = sorted({p for repair in request.get('repairs', []) for p in repair['write_files']})
        planned = impact_plan(request['checkpoint_ids'], planned_writes, request.get('ownership'),
                              phase=request.get('phase', 'intermediate'))
        groups = _groups(request.get('repairs', []), planned)
        result = {'schema_version': 1, 'run_id': request['run_id'], 'status': 'running',
            'input_sha256': digest(json_bytes(request)), 'binding': binding, 'triage': diagnosis,
            'planned_impact': planned, 'calls': [], 'check_results': [], 'finding_results': [],
            'original_queues_modified': False, 'application_acceptance': 'not_established'}
        write_json(folder/'result.json', result)
        try:
            frozen = read_json(project_path(project, 'spec/execution/execution-contract.json'))
            result['calls'].extend(_dispatch(groups, commands, project, folder,
                min(request.get('available_slots', 1), max(1, len(groups))), diagnosis, frozen['plan_items'], request))
            require(not any(c['status'] == 'timed_out' for c in result['calls']),
                    'Repair timed out; verify old child processes stopped before new repair/build/recheck')
            executed = {c['operation'][7:] for c in result['calls'] if c['operation'].startswith('repair:')}
            result['unattempted_repair_ids'] = sorted({r['id'] for r in request.get('repairs', [])}-executed)
            require(_binding(project) == binding, 'Repair changed protected source/plan/config inputs')
            after = target_inputs(project);changed = _changed(before, after)
            require(set(changed) <= set(planned_writes), 'Repair changed files outside frozen ownership: ' +
                    ', '.join(sorted(set(changed)-set(planned_writes))))
            result['changed_files'] = changed
            actual = impact_plan(request['checkpoint_ids'], changed, request.get('ownership'),
                                 phase=request.get('phase', 'intermediate'))
            # Original failed requirements always get a recheck, even with no code delta.
            failed_cps = {f['checkpoint_id'] for f in diagnosis['findings'] if f['checkpoint_id']}
            selected = set(actual['selected_checkpoint_ids']) | failed_cps
            actual['selected_checkpoint_ids'] = sorted(selected)
            actual['not_selected_checkpoint_ids'] = sorted(set(request['checkpoint_ids'])-selected)
            result['actual_impact'] = actual
            result['fix_groups'] = [{'repair_ids':[r['id'] for r in g['repairs']],
                                    'write_files':sorted(g['files'])} for g in groups]
            build = _call(project, folder, 'build', commands['build'], 'build');result['calls'].append(build)
            build_ok = False
            if build['exit_code'] == 0:
                report, sha = _report(project, request['build']['report'])
                build_ok = report.get('status') in PASSED and not report.get('failures')
                build.update(report=request['build']['report'], report_sha256=sha)
                if build_ok:build['artifact_sha256'] = build_identity(project_path(project, request['build']['artifact']))
            require(_binding(project) == binding and target_inputs(project) == after,
                    'Build changed protected or product inputs; rerun the affected repair round')
            result['build_verified'] = build_ok
            by_id = {f['id']: f for f in diagnosis['findings']}
            decisions = {f: [] for f in by_id}
            covered = set()
            for check in request['checks']:
                requested = set(check['checkpoint_ids'])
                if not requested & selected and not check.get('finding_ids'):
                    continue
                if check.get('requires_build', True) and not build_ok:
                    result['check_results'].append({'id': check['id'], 'status': 'blocked', 'reason': 'current_build_not_passed'})
                    continue
                call = _call(project, folder, 'check:' + check['id'], commands['check:' + check['id']], 'work')
                result['calls'].append(call)
                require(_binding(project) == binding and target_inputs(project) == after,
                        'Read-only recheck changed product or protected inputs')
                value, sha = _report(project, check['report'])
                pair_ref = {}
                if 'pair' in check and call['exit_code'] == 0:
                    config = check['pair']
                    value = pair_evidence(project_path(project, config['source']), project_path(project, config['target']),
                        current=read_json(project_path(project, config['current'])),
                        phase=request.get('phase', 'intermediate'), checkpoints=sorted(requested & selected),
                        rules=read_json(project_path(project, config['rules'])))
                    derived = folder/('paired-' + digest(check['id'].encode())[:16]+'.json');write_json(derived, value)
                    pair_ref = {'paired_report': derived.relative_to(project).as_posix(),
                                'paired_report_sha256': digest(derived.read_bytes())}
                failed_keys = {key for key, _ in harvested(value)}
                actual_scope = _coverage(value, check, binding, after)
                ui_complete = ('pair' in check and value.get('current_binding_verified') is True and
                    bool(value.get('pairs')) and all(p.get('assessment', {}).get('evidence_complete') is True
                    for p in value['pairs']))
                scope_complete = requested <= actual_scope
                fresh = call['exit_code'] == 0 and scope_complete and (value.get('status') in PASSED and not failed_keys or ui_complete)
                outcome = {'id': check['id'], 'status': 'rechecked' if fresh else 'failed',
                    'checkpoint_ids': sorted(requested), 'report': check['report'], 'report_sha256': sha,
                    'actual_call_now': True, 'remaining_finding_keys': sorted(failed_keys),
                    'actual_checkpoint_ids':sorted(actual_scope), 'missing_checkpoint_ids':sorted(requested-actual_scope), **pair_ref}
                result['check_results'].append(outcome)
                if fresh:covered.update(requested)
                for ident in check.get('finding_ids', []):
                    finding = by_id[ident]
                    clear = fresh and finding['local_key'] not in failed_keys
                    original = finding['original']
                    case_id = original.get('case_id') or (original.get('subject') if
                        original.get('rule') == 'IOS.BEHAVIOR_OBSERVATION' else None)
                    if 'observations' in value and isinstance(case_id, str):
                        clear = clear and any(o.get('id') == case_id and o.get('status') == 'observed_pass'
                            and o.get('exit_code') == 0 for o in value['observations'] if isinstance(o, dict))
                    if 'pair' in check:
                        pairs = [p for p in value.get('pairs', []) if p['id'] == finding.get('checkpoint_id')]
                        clear = clear and len(pairs) == 1 and pairs[0].get('assessment', {}).get('evidence_complete') is True
                    decisions[ident].append('resolved_by_original_recheck' if clear else 'open')
            for ident, finding in by_id.items():
                results = decisions[ident]
                result['finding_results'].append({'id': ident, 'report': finding['report'],
                    'local_key': finding['local_key'], 'original': finding['original'],
                    'state': 'resolved_by_original_recheck' if results and all(r == 'resolved_by_original_recheck' for r in results) else 'open'})
            unresolved = [f['id'] for f in result['finding_results'] if f['state'] == 'open']
            result['unchecked_checkpoint_ids'] = sorted(selected-covered)
            result['status'] = 'rechecked' if not unresolved and not result['unchecked_checkpoint_ids'] and not result['unattempted_repair_ids'] and build_ok and not any(
                c.get('remaining_finding_keys') for c in result['check_results']) and all(
                c['exit_code'] == 0 for c in result['calls']) else 'partial'
            result['target_inputs_after'] = after
        except (MigrationError, OSError, ValueError, KeyError, TypeError) as exc:
            saved = [read_json(p) for p in sorted(folder.glob('call-*.json'))]
            result['calls'] = saved
            result.update(status='blocked', error=str(exc), recovery='Preserve this run and original findings; repair the stated input and use a new run_id. Never reuse old PASS.')
        result['receipt_sha256'] = digest(json_bytes(result))
        write_json(folder/'result.json', result)
        return result


def check(project, run_id):
    project = _project(project)
    require(isinstance(run_id, str) and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,100}', run_id), 'Invalid repair run id')
    folder = project_path(project, ROOT + '/' + run_id)
    request = read_json(project_path(project, ROOT + '/' + run_id + '/input.json'))
    result = read_json(project_path(project, ROOT + '/' + run_id + '/result.json'))
    expected = result.get('receipt_sha256')
    require(digest(json_bytes({k:v for k,v in result.items() if k != 'receipt_sha256'})) == expected,
            'Repair receipt changed or was interrupted')
    require(result['input_sha256'] == digest(json_bytes(request)) and _binding(project) == result['binding'], 'Repair source/plan/config/rules changed')
    require(result.get('status') == 'rechecked' and target_inputs(project) == result.get('target_inputs_after'),
            'Repair round incomplete or current target changed')
    for call in result['calls']:
        require(call['actual_call_now'] is True and call['exit_code'] == 0, 'Repair call did not actually pass')
        for channel in ('stdout', 'stderr'):
            ref = call[channel]
            require(digest(project_path(project, ref['path']).read_bytes()) == ref['sha256'], 'Repair process evidence changed')
        for path, sha in call['pinned_commands'].items():
            require(digest(Path(path).read_bytes()) == sha, 'Repair/check implementation changed')
        if 'report' in call:
            require(digest(project_path(project, call['report']).read_bytes()) == call['report_sha256'],
                    'Current build report changed')
    build = next(c for c in result['calls'] if c['operation'] == 'build')
    require(build_identity(project_path(project, request['build']['artifact'])) == build.get('artifact_sha256'),
            'Build artifact changed since affected recheck')
    for outcome in result['check_results']:
        require(outcome.get('status') == 'rechecked' and outcome.get('actual_call_now') is True,
                'Recheck was not actually completed')
        require(digest(project_path(project, outcome['report']).read_bytes()) == outcome['report_sha256'],
                'Original recheck report changed')
        if 'paired_report' in outcome:
            require(digest(project_path(project, outcome['paired_report']).read_bytes()) == outcome['paired_report_sha256'],
                    'Paired recheck evidence changed')
    return {'status': 'current_rechecked', 'run_id': run_id, 'receipt_sha256': expected,
            'application_acceptance': 'not_established'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='action', required=True)
    for name in ('triage', 'run', 'check'):
        command = commands.add_parser(name);command.add_argument('--project', type=Path, required=True)
        if name == 'check':command.add_argument('--run-id', required=True)
        else:command.add_argument('--input', type=Path, required=True)
    args = parser.parse_args(argv)
    progress = None
    try:
        project = _project(args.project)
        if args.action == 'run':
            project_path(project, '.migbot/config.json')
            from .project_progress import ProjectProgress
            args.command = 'ui-repair-run'
            progress = ProjectProgress(args);progress.record('running')
        if args.action == 'triage':result = triage(project, read_json(args.input))
        elif args.action == 'run':result = run(project, read_json(args.input))
        else:result = check(project, args.run_id)
        from .cli_output import emit_json
        if progress is not None:
            progress.record(result['status'], result, exit_code=0 if result['status'] == 'rechecked' else 2)
        emit_json(result)
        return 0 if result['status'] in {'triaged', 'rechecked', 'current_rechecked'} else 2
    except (MigrationError, OSError, ValueError, KeyError, TypeError) as exc:
        from .cli_output import emit_json
        result = {'status':'blocked','error':str(exc),'recovery':'Preserve original evidence; repair this input and explicitly rerun the original producer.'}
        if progress is not None:progress.record('blocked', result, exit_code=2)
        emit_json(result)
        return 2
