"""Typed iOS plan adapter; original 1.7.0 programs remain the only state writers."""
from __future__ import annotations

import importlib.util
import os
import re
import subprocess
import sys
import tempfile
import shutil
import platform
import uuid
import time
from contextlib import contextmanager
from pathlib import Path

from .core import MigrationError, atomic_write, digest, io_path, json_bytes, read_json, safe_child, snapshot, write_json
from .ios_facts import validate_graph
from .ios_harness import ac_inventory, check
from .harness_schema import validate
from .macos_permissions import PermissionRepairError
from .init_environment import check_runtime_ready
from .portable_helper import quarantine_free_launcher

ROOT = Path(__file__).resolve().parents[2]
UPSTREAM = ROOT / 'vendor/hmigbot-1.7.0/skills/a2h-execute/scripts'


def baseline_inputs(project, wave):
    project = Path(project).resolve()
    mutable = {'spec/baseline/' + name for name in ('ui-manifest.md', 'feature-index.md', 'verification.json', 'impl-claims.json', 'ios-source-check.json')}
    from .plan_contract import profile, structural_digest
    projected = {'spec/baseline/ui-manifest.md', 'spec/baseline/feature-index.md'} if profile(project) >= 2 else set()
    mutable -= projected
    inputs = {f['path']: f['sha256'] for f in snapshot(project)['files']
            if (f['path'].startswith('spec/baseline/') and f['path'] not in mutable
                or f['path'].startswith(('spec/ref/ios-expertise-', 'spec/ref/ios-mcp-', 'spec/ref/mcp-runs/', 'spec/ref/ios-analysis-provenance.json', 'spec/ref/ios-manifest-evidence/')))
            and (wave != 'understand' or Path(f['path']).name in {'ios-facts.json', 'ios-obligations.json', 'ios-source-index.json'})}
    graph_path = project / 'spec/baseline/ios-facts.json'
    if graph_path.is_file():
        from .conditional_evidence import frozen_inputs
        inputs.update(frozen_inputs(project, read_json(graph_path)))
    from .source_analysis import frozen_inputs as analysis_inputs
    inputs.update(analysis_inputs(project))
    if wave == 'domains':
        from .ios_harness import responsibility
        projection = responsibility(project)
        if projection is not None:
            inputs.update(projection.frozen_inputs())
        from .spec_contract import dependency_inputs
        inputs.update({path: value for path, value in dependency_inputs(project).items()
                       if path not in mutable})
        inputs.pop('spec/baseline/plans/resource-mapping.md', None)
        if profile(project) >= 2:
            from .plan_contract import indexed_contract_inputs
            inputs.update(indexed_contract_inputs(project))
    for path in projected:
        target = safe_child(project, path)
        if path in inputs and target.is_file():
            inputs[path] = structural_digest(target.read_text(encoding='utf-8-sig'), artifact=path)
    return inputs


def _execution_evidence(path):
    """Named generator outputs are not task-owned product files.

    Keep this adapter-local: source fingerprints must still include source
    files with these names. Never ignore an entire work/spec/config tree, and
    never permit product .ets, resource directories or arbitrary JSON here.
    Support programs have a separate, explicitly named workspace.
    """
    exact = {
        # Observed DevEco-generated editor/cache metadata, not product inputs.
        # Keep raw/source snapshots intact and all neighboring paths audited.
        '.idea/.deveco/cxx/.clang-format', '.idea/.deveco/module/entry.cache.json',
        '.idea/.deveco/project.cache.json', '.idea/.gitignore',
        'build_out.log', 'build_temp.bat', 'spec/migration-report.md',
        'spec/reports/init-environment.json',
        'spec/ui-coverage-report.md', 'spec/verify-report.md',
        'spec/placeholder-registry.md', 'spec/execution/base-contracts.md',
        'spec/execution/capability-manifest.json',
        'spec/a2h/_work/join-ledger.jsonl',
        'spec/reports/product-literals.json', 'spec/reports/visual-verify-report.md',
        'spec/.a2h/open-findings.json', 'spec/.a2h/impl-claims.json',
        'spec/baseline/verification.json', 'spec/baseline/impl-claims.json',
        'spec/baseline/ios-source-check.json',
    }
    if path in exact:
        return True
    patterns = (
        r'spec/state/(?:state|dispatch|journal)\.json',
        r'spec/waves/plan-(?:understand|domains)\.json',
        r'spec/waves/wave-(?:understand|domains)\.result\.json',
        r'spec/waves/prompts/(?:understand|domains)/[a-z0-9_-]+\.txt(?:\.repair\.txt)?',
        r'spec/waves/results/(?:understand|domains)/[a-z0-9_-]+\.json',
        r'spec/reports/(?:ios-|spec-|migration-)[a-z0-9_-]+\.(?:json|md)',
        r'spec/reports/scheduler/[a-z_]+\.(?:(?:stdout|stderr)\.log|failure\.json)',
        r'spec/reports/scheduler/[a-z_]+\.permissions\.json',
        r'spec/reports/scheduler/[a-z_]+\.cleanup-[0-9a-f]{32}\.json',
        r'spec/reports/static-runtime/land-[a-z0-9_-]+\.json',
        r'spec/reports/ios-blocked-recovery/[0-9a-f]{64}/[a-z-]+\.json',
        r'spec/reports/ios-blocked-receipts/(?:understand|domains)/[a-z0-9_-]+/[0-9a-f]{64}\.json',
        r'spec/reports/derived/(?:[A-Za-z0-9_.-]+/)*(?:spec-summary|product-literals|source-analysis|spec-scaffold|spec-authoring|spec-upgrade|usage-budget)\.json',
        r'spec/reports/derived/(?:[A-Za-z0-9_.-]+/)*(?:ui-plan|feature-plan|migration-report)\.md',
        r'spec/reports/derived/a2h-join/[A-Za-z0-9_.-]+/[0-9a-f]{64}\.json',
        r'spec/reports/derived/(?:[A-Za-z0-9_.-]+/)*usage-budget\.json\.lock',
        r'spec/reports/behavior/[A-Za-z0-9_-]+/(?:stdout|stderr)\.log',
        r'spec/reports/host-oracle/(?:support/)?[A-Za-z0-9_.-]+\.(?:py|cjs|mjs|js|json|log|md)',
        r'spec/pipeline-run-\d{8}\.md',
        r'spec/a2h/_work/expected_[A-Za-z0-9_-]+\.json',
        r'spec/fix/round-[1-9]\d*/patrol/arkts-(?:ui-build|ui-adapt|data-network|system-component|thirdparty-component)-(?:batch|group)-\d+\.md',
        r'spec/execution/briefs/[A-Za-z0-9_-]+\.md',
        r'spec/execution/writeback/writeback-(?:(?:batch|group)-\d+|base-\d+(?:[._]\d+)?|final)\.json',
        r'spec/execution/source-understanding/[A-Za-z0-9_-]+-source-notes\.md',
        r'spec/execution/theme-receipts/page_\d{4}\.json',
        # Structural CLI state/output names are caller-selected JSON data in
        # this flat round namespace; this grants no script or product ownership.
        r'spec/execution/autofix-log/round-[1-9]\d*/[A-Za-z0-9_][A-Za-z0-9_.-]*\.json',
        r'spec/execution/autofix-log/round-[1-9]\d*/(?:loop-state|loop-result-latest|loops|audit|wiring|orphans|immersive|icon|ledger|assembly|binding|capability|theme|literal|deadshell|carrier|hittest|resname|native-images|memory)[A-Za-z0-9_.-]*\.(?:json|log|md)',
        r'spec/execution/autofix-log/round-[1-9]\d*/native-pipeline-dispositions-iter\d+\.json',
        r'spec/execution/autofix-log/round-[1-9]\d*/native-pipeline-raw/loop-state-pipeline-final-iter\d+-[0-9a-f]{32}/(?:assembly|audit|binding|carrier|deadshell|hittest|icon|immersive|ledger|literal|orphans|resname|theme)-pipeline-iter\d+\.json',
        r'spec/execution/autofix-log/round-[1-9]\d*/native-pipeline-raw/loop-state-pipeline-final-iter\d+-[0-9a-f]{32}/(?:state|result)\.json',
        r'work/pipeline-\d{8}/run\.py',
        r'work/pipeline-\d{8}/support/[A-Za-z0-9_.-]+\.(?:py|mjs|js|ps1|sh|md|txt|log)',
        r'work/pipeline-\d{8}/support/states/[A-Za-z0-9_.-]+\.json',
        r'work/pipeline-\d{8}/calls/\d{8}T\d{12}-[0-9a-f]{6}(?:\.json|\.(?:stdout|stderr)\.log)',
    )
    return any(re.fullmatch(pattern, path) for pattern in patterns)


def execution_files(project):
    from .plan_contract import profile, structural_digest
    project = Path(project)
    projected = {'spec/baseline/ui-manifest.md', 'spec/baseline/feature-index.md'} if profile(project) >= 2 else set()
    files = {}
    for entry in snapshot(project)['files']:
        path = entry['path']
        if _execution_evidence(path):
            continue
        files[path] = (structural_digest(safe_child(project, path).read_text(encoding='utf-8-sig'), artifact=path)
                       if path in projected else entry['sha256'])
    return files


def _fence_files(project):
    prefix = 'spec/state/fence-snapshot/'
    return {entry['path']: entry['sha256'] for entry in snapshot(project)['files']
            if entry['path'].startswith(prefix)}


def _original_ownership(paths):
    """Mirror the original fence's leading './' character stripping.

    The native ownership contract and receipt checks retain exact paths. Only
    the original kernel's plan gets these literal compatibility aliases; this
    must never authorize a real shadow file such as gitignore for .gitignore.
    """
    return list(dict.fromkeys([*paths, *(path.lstrip('./') for path in paths)]))


def _land_native_receipts(project, wave, plan_path, blocked):
    """Bridge a native blocked outcome through the original failure writer.

    The legacy kernel treats any schema-valid final_state as task completion,
    including BLOCKED. It has a supported missing-as-failed channel instead.
    Preserve the exact native receipt as content-addressed evidence, remove it
    only from the legacy consumer while that writer records the failed attempt,
    then restore it. A crash leaves recoverable evidence, never a fake success
    receipt or a hand-authored state/dispatch/journal entry.
    """
    if not blocked:
        return invoke(project, 'land_results', ['--plan', str(plan_path), '--state', 'spec/state/state.json', '--json'])
    dispatch = read_json(project / 'spec/state/dispatch.json').get('waves', {}).get(wave, {}).get('dispatched', {})
    journal_path = project / 'spec/state/journal.json'
    landed, _ = kernel().journal_indexes(read_json(journal_path) if journal_path.exists() else {}, wave)
    pending, evidence, removed = [], [], []
    try:
        for ident, path in blocked:
            raw = path.read_bytes()
            archive = f'spec/reports/ios-blocked-receipts/{wave}/{ident}/{digest(raw)}.json'
            archived = safe_child(project, archive)
            if archived.exists():
                if archived.read_bytes() != raw:
                    raise MigrationError('Blocked receipt archive conflicts with its content hash')
            else:
                atomic_write(archived, raw)
            evidence.append({'id': ident, 'archive': archive, 'sha256': digest(raw),
                             'native_status': 'blocked', 'original_disposition': 'missing-as-failed'})
            if dispatch.get(ident, {}).get('attempts', 0) > landed.get(ident, 0):
                path.unlink()
                removed.append((path, raw))
                pending.append(ident)
        args = ['--plan', str(plan_path), '--state', 'spec/state/state.json', '--json']
        if pending:
            args += ['--missing-as-failed', ','.join(pending)]
        action = invoke(project, 'land_results', args)
    finally:
        restore_errors = []
        for path, raw in removed:
            try:
                if path.exists() and path.read_bytes() != raw:
                    raise MigrationError('Native result changed during legacy failure landing: ' + str(path))
                if not path.exists():
                    atomic_write(path, raw)
            except (OSError, MigrationError) as exc:
                restore_errors.append(exc)
        if restore_errors:
            raise MigrationError('Could not restore all native receipts; originals retained in blocked archive: '
                                 + '; '.join(str(exc) for exc in restore_errors)) from restore_errors[0]
    action['ios_blocked_receipts'] = evidence
    action['ok'] = False
    return action


def kernel():
    spec = importlib.util.spec_from_file_location('ios_upstream_wavelib', UPSTREAM / '_wavelib.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _cleanup_windows_runtime(project, program, directory, parent):
    """A staged executable lock is cleanup debt, not a command failure."""
    error = None
    for attempt in range(1, 5):
        try:
            # Delete only the unique directory created under this explicit
            # temporary parent; refuse links or a changed resolved target.
            if (directory.resolve() != parent / directory.name or not directory.name.startswith('ios-scheduler-python-')
                    or directory.is_symlink() or getattr(directory, 'is_junction', lambda: False)()):
                raise MigrationError('Refusing cleanup outside the staged runtime directory')
            shutil.rmtree(directory)
            error = None
            break
        except (OSError, MigrationError) as exc:
            if isinstance(exc, FileNotFoundError) and not directory.exists():
                error = None
                break
            error = exc
            if isinstance(exc, OSError) and getattr(exc, 'winerror', None) in {5, 32, 33} and attempt < 4:
                time.sleep(0.05 * 2 ** (attempt - 1))
                continue
            break
    if error is None and attempt == 1:
        return None
    report = {'schema_version': 1, 'kind': 'scheduler_runtime_cleanup', 'program': program,
              'status': 'retained' if error else 'removed_after_retry', 'runtime_path': str(directory),
              'attempts': attempt, 'error': str(error) if error else None,
              'winerror': getattr(error, 'winerror', None)}
    path = project / 'spec/reports/scheduler' / (program + '.cleanup-' + uuid.uuid4().hex + '.json')
    report['audit_path'] = str(path)
    try:
        write_json(path, report)
    except OSError as exc:
        report['audit_error'] = str(exc)
        try:
            sys.stderr.write(f'Scheduler runtime cleanup {report["status"]}: {directory}; '
                             f'attempts={attempt}; cleanup_error={error}; audit_error={exc}\n')
        except OSError as stderr_error:
            report['stderr_error'] = str(stderr_error)
    return report


@contextmanager
def _runtime_directory(project, program, *, windows, cleanup_reports=None):
    if not windows:
        with tempfile.TemporaryDirectory(prefix='ios-scheduler-python-', dir='/private/tmp' if platform.system() == 'Darwin' else None) as temp:
            yield temp
        return
    parent = Path(tempfile.gettempdir()).resolve()
    directory = Path(tempfile.mkdtemp(prefix='ios-scheduler-python-', dir=parent))
    try:
        yield str(directory)
    finally:
        report = _cleanup_windows_runtime(project, program, directory, parent)
        if report and cleanup_reports is not None:
            cleanup_reports.append(report)


def invoke(project, program, args):
    from .runtime_timeouts import timeout_for
    from .scheduler_windows_runtime import run as run_owned_process
    env = {**os.environ, 'PYTHONUTF8': '1', 'ARKTS_SKILL_DIR': str(UPSTREAM.parent)}
    windows, cleanup_reports, permission_receipts = os.name == 'nt', [], []
    if windows:
        project = io_path(project)
        args = list(args)
        # The frozen kernel derives its project root from these input paths.
        # Supply the filesystem spelling explicitly: Path(custom_path) inside
        # the original code would otherwise discard the I/O-aware subclass.
        for index, flag in enumerate(args[:-1]):
            if flag in {'--plan', '--state'}:
                path = Path(args[index + 1])
                args[index + 1] = os.fspath(io_path(path if path.is_absolute() else project / path))
    try:
        timeout_for('scheduler', env=env)
        # Frozen upstream sys.executable points at a non-shipped python.exe beside
        # its binary on Windows. Stage unchanged payload plus the host interpreter;
        # never repair vendor bytes in place or replace original state algorithms.
        with _runtime_directory(project, program, windows=windows, cleanup_reports=cleanup_reports) as temp:
            command = [sys.executable, str(UPSTREAM / (program + '.py')), *args]
            if platform.system() == 'Darwin':
                import shlex
                architecture = 'arm64' if platform.machine().lower() in {'arm64', 'aarch64'} else 'x64'
                payload = UPSTREAM / 'bin' / ('macos-' + architecture) / '_entry.dist'
                permission_receipts.append(check_runtime_ready(project, payload))
                scripts = Path(temp) / 'a2h-execute/scripts'
                scripts.mkdir(parents=True)
                for source in UPSTREAM.glob('*.py'):
                    shutil.copy2(source, scripts / source.name)
                    text = source.read_text(encoding='utf-8')
                    safe = quarantine_free_launcher(text)
                    if safe != text:
                        (scripts / source.name).write_text(safe, encoding='utf-8')
                directory = scripts / 'bin' / ('macos-' + architecture) / '_entry.dist'
                shutil.copytree(payload, directory, ignore=shutil.ignore_patterns('Python'))
                # macOS commonly has case-insensitive paths: Python is a dylib,
                # while frozen sys.executable is python. Keep the original dylib
                # outside the staged directory and resolve it through dyld.
                interpreter = directory / 'python'
                bootstrap = ("import os,runpy,sys; os.environ['DYLD_LIBRARY_PATH']=" + repr(str(payload)) +
                             "; sys.argv=sys.argv[1:]; runpy.run_path(sys.argv[0],run_name='__main__')")
                interpreter.write_text('#!/bin/sh\nunset DYLD_LIBRARY_PATH\nexec ' +
                                       shlex.quote(sys.executable) + ' -c ' + shlex.quote(bootstrap) +
                                       ' "$@"\n', encoding='utf-8')
                interpreter.chmod(0o755)
                executable = directory / '_entry.bin'
                executable.chmod(executable.stat().st_mode | 0o111)
                env['DYLD_LIBRARY_PATH'] = str(payload)
                env['ARKTS_SKILL_DIR'] = str(scripts.parent)
                command = [str(executable), program, *args]
            if windows:
                if platform.machine().lower() not in {'amd64', 'x86_64', 'x64'}:
                    raise MigrationError('Bundled Windows kernel requires x64')
                directory = Path(temp) / '_entry.dist'
                shutil.copytree(UPSTREAM / 'bin/windows-x64/_entry.dist', directory)
                from .windows_python_runtime import stage_base_python
                stage_base_python(directory, env)
                command = [str(directory / '_entry.exe'), program, *args]
            limit = timeout_for('scheduler', env=env)
            if windows:
                proc = run_owned_process(command, cwd=project, env=env, timeout=limit)
            else:
                proc = subprocess.run(command,
                                      cwd=project, env=env, capture_output=True, timeout=limit, shell=False)
    except (subprocess.TimeoutExpired, OSError, PermissionRepairError) as exc:
        directory = project / 'spec/reports/scheduler'
        atomic_write(directory / (program + '.stdout.log'), getattr(exc, 'output', None) or b'')
        atomic_write(directory / (program + '.stderr.log'), getattr(exc, 'stderr', None) or b'')
        log = project / 'spec/reports/scheduler' / (program + '.failure.json')
        report = {'program': program, 'error': str(exc), 'status': 'FAIL',
                  'process_tree': getattr(exc, 'ios_process_tree', None),
                  'timeout_policy': getattr(exc, 'ios_timeout_policy', None)}
        if isinstance(exc, PermissionRepairError):
            report['tool_runtime_permissions'] = exc.receipt
        if cleanup_reports:
            report['runtime_cleanup'] = cleanup_reports
        write_json(log, report)
        raise MigrationError('Original scheduler failed; evidence: ' + str(log)) from exc
    directory = project / 'spec/reports/scheduler'
    atomic_write(directory / (program + '.stdout.log'), proc.stdout)
    atomic_write(directory / (program + '.stderr.log'), proc.stderr)
    if proc.returncode:
        raise MigrationError('Original scheduler rejected input: ' + proc.stderr.decode('utf-8', errors='replace')[-1800:])
    import json
    try:
        result = json.loads(proc.stdout)
        if permission_receipts:
            write_json(directory / (program + '.permissions.json'),
                       {'schema_version': 1, 'kind': 'tool_runtime_permissions',
                        'program': program, 'receipts': permission_receipts, 'product_verified': False})
        if isinstance(result, dict) and any('stderr_error' in report for report in cleanup_reports):
            result['ios_runtime_cleanup'] = cleanup_reports
        return result
    except (ValueError, UnicodeError) as exc:
        raise MigrationError('Original scheduler did not return a JSON action') from exc


def generate(project, input_path, *, validate_only=False):
    from .native_pipeline import context
    source, project = context(project)
    request = validate(read_json(input_path), 'planRequest')
    from .plan_contract import profile, contract_revision, validate_plan
    contract_profile = profile(project)
    existing_contract = project / 'spec/blueprint/contracts.json'
    if existing_contract.is_file() and read_json(existing_contract).get('spec_contract_version', 1) > contract_profile:
        raise MigrationError('Cannot downgrade a frozen spec contract profile to bypass planning gates')
    if request.get('schema_version') != 2 or request.get('wave') not in {'understand', 'domains'}:
        raise MigrationError('Expected typed v2 plan for understand or domains wave')
    wave = request['wave']
    plan_contract = validate_plan(project, request)
    graph, obligations = validate_graph(source, project)
    projection = None
    if wave == 'domains':
        from .ios_harness import responsibility
        projection = responsibility(project, source=source, graph=graph, obligations=obligations)
        if projection is not None and projection.candidate:
            raise MigrationError('Candidate responsibility cannot authorize planning or dispatch')
    if wave == 'domains':
        report, code = check(project, report_only=validate_only)
        if code:
            raise MigrationError('Source harness gate failed; resolve findings before planning implementation')
    graph_hash = digest(json_bytes(graph))
    if request.get('graph_sha256') != graph_hash:
        raise MigrationError('Plan input must pin the current fact graph')
    tasks = request.get('tasks')
    if not isinstance(tasks, list) or not tasks:
        raise MigrationError('Plan must have nonempty typed tasks')
    ids, owned, original_owned, covered, planned = set(), set(), {}, set(), []
    all_acs = ac_inventory(project) if wave == 'domains' else {}
    all_facts = {f['id'] for f in graph['facts']}
    for task in tasks:
        ident = task.get('id')
        if not isinstance(ident, str) or not re.fullmatch(r'[a-z][a-z0-9_-]*', ident) or ident in ids:
            raise MigrationError('Task IDs must be unique portable names')
        ids.add(ident)
        role = task.get('role')
        if not isinstance(role, str) or not (ROOT / 'agents-codex' / (role + '.toml')).is_file():
            raise MigrationError('Role is not bundled: ' + str(role))
        own = task.get('ownership')
        readonly_verification = contract_profile >= 2 and task.get('verification') in {'compile', 'behavior', 'visual'} and not own
        if not isinstance(own, list) or not own and not readonly_verification:
            raise MigrationError('Tasks need explicit file ownership; wildcards are not allowed')
        for path in own:
            safe_child(project, path)
            portable = path.casefold()
            if any(ch in path for ch in '*?[') or portable in owned or portable.startswith(('spec/state/', 'spec/blueprint/', 'spec/waves/', 'spec/.a2h/', '.migbot/', '.hmigbot-ios/', '.agents/', '.codex/', '.git/')):
                raise MigrationError('Overlapping or control-plane ownership: ' + path)
            if wave == 'understand' and not path.startswith('spec/'):
                raise MigrationError('Understanding tasks may only write specs')
            owned.add(portable)
        for path in _original_ownership(own):
            portable = path.casefold()
            if portable in original_owned and original_owned[portable] != ident:
                raise MigrationError('Ambiguous original ownership projection: ' + path)
            original_owned[portable] = ident
        ac_ids = task.get('ac_ids', [])
        fact_ids = task.get('fact_ids')
        if not isinstance(ac_ids, list) or any(a not in all_acs for a in ac_ids) or wave == 'domains' and not ac_ids and contract_profile < 2:
            raise MigrationError('Implementation task must bind real acceptance criteria')
        if not isinstance(fact_ids, list) or not fact_ids or not set(fact_ids) <= all_facts:
            raise MigrationError('Task must bind current machine facts')
        covered.update(ac_ids)
        if not isinstance(task.get('goal'), str) or not task['goal'].strip():
            raise MigrationError('Task goal is required')
        planned.append(task)
    if set(all_acs) - covered:
        raise MigrationError('Plan omitted acceptance criteria: ' + ','.join(sorted(set(all_acs) - covered)))
    if wave == 'domains':
        mapping = read_json(project / 'spec/baseline/ios-coverage.json')['mappings']
        obs = read_json(project / 'spec/baseline/ios-obligations.json')['obligations']
        by_obligation = {o['id']: o for o in obs}
        owned_obligations = set()
        for row in mapping:
            if projection is not None and row['obligation_id'] in projection.historical_obligation_ids:
                continue
            if row['obligation_id'] in report.get('excluded_obligation_ids', []):
                continue  # Only source-harness-validated Preview reviews are non-product obligations.
            fact_id = by_obligation[row['obligation_id']]['fact_id']
            if not any(fact_id in t['fact_ids'] and set(t['ac_ids']) & set(row['ac_ids']) for t in tasks):
                raise MigrationError('Obligation has no implementation owner: ' + row['obligation_id'])
            owned_obligations.add(row['obligation_id'])
        if projection is not None:
            projection.validate_target_ownership(covered, owned_obligations)
    completed = set()
    while len(completed) < len(tasks):
        ready = [t['id'] for t in tasks if t['id'] not in completed and isinstance(t.get('parents', []), list) and set(t.get('parents', [])) <= completed]
        if not ready:
            raise MigrationError('Unknown parent or dependency cycle')
        completed.update(ready)
    parallel = request.get('max_parallel', 1)
    if type(parallel) is not int or not 1 <= parallel <= 8:
        raise MigrationError('max_parallel must be 1..8; serial is the default')
    from .prompt_inputs import project_inputs
    prompt_inputs = project_inputs(graph['facts'], planned, request.get('decisions', []))
    if validate_only:
        return {'status': 'request_validated', 'source_sha256': graph['source_sha256'], 'plan_contract': plan_contract}
    plan_path = project / f'spec/waves/plan-{wave}.json'
    if plan_path.exists():
        raise MigrationError('Existing plan is immutable; use a new project or explicit reviewed replan')
    blueprint = project / 'spec/blueprint'
    if wave == 'domains' and (blueprint / 'workflow-params.json').exists():
        if read_json(blueprint / 'workflow-params.json').get('ios_adapter_version') != 2:
            raise MigrationError('Original blueprint needs explicit compatibility adaptation')
    # Pin complete model-authored request in the canonical six-item contract.
    input_hashes = baseline_inputs(project, wave)
    for name, value in {
        'domain-map.json': {'version': 1, 'domains': [{'key': t['id'], 'title': t['goal'], 'pages': []} for t in planned]},
        'ownership.json': {'version': 1, 'owners': {t['id']: t['ownership'] for t in planned}, 'mainloop_owned': []},
        'contracts.json': {'version': 1, 'ios_adapter_version': 2, 'source_sha256': graph['source_sha256'],
                           'graph_sha256': graph_hash, 'input_hashes': input_hashes, 'ios_tasks': tasks, 'modules': [], 'wires': [],
                           **({'responsibility_enabled': True} if projection is not None else {}),
                           'spec_contract_version': contract_profile, 'contract_revision': contract_revision(project),
                           'task_inputs': plan_contract['task_inputs']},
        'decisions.json': {'version': 1, 'decisions': request.get('decisions', [])},
        'workflow-params.json': {'ios_adapter_version': 2, 'project': {'root': str(project), 'ios_src': str(source)}, 'gates': {'unattended': False}}
    }.items():
        write_json(blueprint / name, value)
    if not (blueprint / 'decision-ledger.md').exists():
        atomic_write(blueprint / 'decision-ledger.md', b'# iOS decisions\n\nNo implicit platform decisions.\n')
    decision_ledger_sha256 = digest((blueprint / 'decisions.json').read_bytes())
    warnings = []
    nodes = []
    for t in planned:
        prompt = f'spec/waves/prompts/{wave}/{t["id"]}.txt'
        receipt = f'spec/waves/results/{wave}/{t["id"]}.json'
        inputs = prompt_inputs[t['id']]
        facts = inputs['facts']
        consumer_inputs = plan_contract['task_inputs'].get(t['id'], [])
        body = ('Use the assigned bundled role and iOS skill protocol. You share the codebase; preserve others\' edits.\n'
                'Read spec/ref/ios-expertise-plan.json and ios-expertise-reviews.json when present.\n'
                'Use frozen source semantics, ACs and linked tool_evidence_ids; do not replace source behavior with upstream best practices.\n'
                'Only write the explicitly owned files. Shared wiring requires its designated owner.\n'
                'Return generated/blocked; generation is not compilation or behavior verification.\n'
                f'Goal: {t["goal"]}\nRole: {t["role"]}\nOwnership: {t["ownership"]}\nACs: {t.get("ac_ids", [])}\n'
                f'Spec contract profile: {contract_profile}; revision: {contract_revision(project)}\n'
                f'Markdown plan items: {t.get("plan_item_refs", [])}\nVerification obligation: {t.get("verification", "generated")} (not an achieved result)\n'
                'Read each mapped item and preserve all its verification duties; the highest enum does not replace independent behavior/visual evidence.\n'
                'Required inputs: read every exact heading below at the pinned file hash. If missing/conflicting, return blocked and identify the conflicting references.\n'
                + json_bytes(consumer_inputs).decode() + '\n'
                +
                f'Receipt path: {receipt}\nUse ios-receipt v2 with source_sha256, plan_sha256, task_id, files hashes, ac_ids and findings.\n'
                'Facts:\n' + json_bytes(facts).decode() + '\nDecisions:\n' + json_bytes(inputs['decisions']).decode()
                + '\nDecision projection: ' + json_bytes({
                    'full_ledger': 'spec/blueprint/decisions.json',
                    'sha256': decision_ledger_sha256,
                    'omitted_explicitly_scoped_decisions': inputs['omitted_decisions'],
                    'scope_semantics': 'explicit task/ac/fact consumer union; unscoped decisions always included',
                }).decode())
        atomic_write(safe_child(project, prompt), body.encode())
        nodes.append({'id': t['id'], 'kind': 'agent', 'agent': t['role'] + '@0.6.0',
                      'model': t.get('model', 'inherit'), 'schema': 'fixResult',
                      'prompt_file': prompt, 'parents': t.get('parents', []), 'map_group': 'ios-' + wave,
                      'ownership': _original_ownership(t['ownership']), 'result_path': receipt, 'resume_key': wave + ':' + t['id']})
    plan = {'plan_version': 'a2h-2.1.0', 'wave': wave,
            'max_parallel': parallel, 'max_attempts': 2, 'tasks': nodes, 'products': {}, 'ios_adapter_version': 2}
    contract = read_json(blueprint / 'contracts.json')
    contract['plan_identity_sha256'] = digest(json_bytes(plan))
    contract['prompt_hashes'] = {n['prompt_file']: digest(safe_child(project, n['prompt_file']).read_bytes()) for n in nodes}
    write_json(blueprint / 'contracts.json', contract)
    contract_hash = kernel().compute_contract_hash(blueprint, warnings)
    plan['contract_hash'] = contract_hash
    write_json(plan_path, plan)
    invoke(project, 'state_update', ['--state', 'spec/state/state.json', '--op', 'init', '--json'])
    return {'status': 'plan_generated', 'plan': str(plan_path), 'contract_hash': contract_hash, 'warnings': warnings,
            'state_writer': 'original state_update.py', 'behavior_verified': False}


def _validate_task_inputs(project, task_inputs):
    """Hash each immutable contract file once at this step's input boundary.

    Resolve every reference, including repeats, before deduplicating so an
    unsafe alias or conflicting expected hash cannot hide behind a prior ref.
    This cache lasts only for this call; it does not inherit PASS across steps,
    rely on stat metadata, or replace graph/baseline/final evidence validation.
    As with the other snapshot gates, callers must not mutate frozen inputs
    concurrently; one boundary check is not continuous filesystem monitoring.
    """
    files = {}
    for refs in task_inputs.values():
        for ref in refs:
            path = safe_child(project, ref['path'])
            if path in files and files[path]['sha256'] != ref['sha256']:
                raise MigrationError('Conflicting pinned task contract input hashes: ' + ref['path'])
            files.setdefault(path, ref)
    for path, ref in files.items():
        if digest(path.read_bytes()) != ref['sha256']:
            raise MigrationError('Pinned task contract input changed: ' + ref['path'] + '#' + ref['heading'])


def step(project, wave, *, landing=False, usage_ledger=None, usage_run_id=None):
    from .native_pipeline import context
    source, project = context(project)
    if (usage_ledger is None) != (usage_run_id is None):
        raise MigrationError('Select both usage_ledger and usage_run_id')
    if landing and usage_ledger is not None:
        raise MigrationError('Usage dispatch checks belong to next-batch; landing remains available')
    if wave not in {'understand', 'domains'}:
        raise MigrationError('Unsupported adapter wave')
    plan_path = project / f'spec/waves/plan-{wave}.json'
    plan = read_json(plan_path)
    if plan.get('ios_adapter_version') != 2:
        raise MigrationError('Do not mix original and iOS state consumers')
    contract = read_json(project / 'spec/blueprint/contracts.json')
    from .plan_contract import assert_pinned
    assert_pinned(project, contract)
    _validate_task_inputs(project, contract.get('task_inputs', {}))
    if digest(json_bytes({k: v for k, v in plan.items() if k != 'contract_hash'})) != contract.get('plan_identity_sha256'):
        raise MigrationError('Plan IR changed after generation; do not dispatch edited tasks')
    for path, expected in contract.get('prompt_hashes', {}).items():
        if digest(safe_child(project, path).read_bytes()) != expected:
            raise MigrationError('Task prompt changed after generation: ' + path)
    graph, _ = validate_graph(source, project)
    if graph['source_sha256'] != contract['source_sha256']:
        raise MigrationError('Plan source snapshot changed')
    if baseline_inputs(project, wave) != contract['input_hashes']:
        raise MigrationError('Plan baseline changed; review and explicitly replan')
    if wave == 'domains' and check(project)[1]:
        raise MigrationError('Source harness gate failed')
    if landing:
        evidence_path = project / f'spec/reports/ios-dispatch-{wave}.json'
        dispatch_evidence = read_json(evidence_path)
        if dispatch_evidence.get('plan_sha256') != digest(plan_path.read_bytes()):
            raise MigrationError('Dispatch evidence does not match frozen plan')
        actual = execution_files(project)
        before = dispatch_evidence['before_files']
        changed = {p for p in before.keys() | actual.keys() if before.get(p) != actual.get(p)}
        active_ids = set(dispatch_evidence['task_ids'])
        allowed = {p for task in contract['ios_tasks'] if task['id'] in active_ids for p in task['ownership']}
        if changed - allowed:
            raise MigrationError('Dispatch changed files outside ownership: ' + ','.join(sorted(changed - allowed)))
        owned_tasks = {t['id']: t for t in contract['ios_tasks']}
        blocked = []
        for task in plan['tasks']:
            path = safe_child(project, task['result_path'])
            if not path.exists():
                continue  # Original in-flight timeout and retry rules remain authoritative.
            receipt = validate(read_json(path), 'receipt')
            task_def = owned_tasks[task['id']]
            # Adapter receipt and original schema share a single result file, never a second state file.
            if receipt.get('ios_receipt_version') != 2 or receipt.get('source_sha256') != graph['source_sha256'] or receipt.get('plan_sha256') != digest(plan_path.read_bytes()) or receipt.get('task_id') != task['id']:
                raise MigrationError('Stale/invalid receipt: ' + task['id'])
            if receipt.get('status') not in {'generated', 'blocked'} or receipt.get('behavior_verified') is not False:
                raise MigrationError('Receipt cannot claim compilation or behavior acceptance')
            if receipt.get('final_state') != ('PASS' if receipt['status'] == 'generated' else 'BLOCKED'):
                raise MigrationError('Receipt generation status and original final_state disagree')
            files = receipt.get('file_hashes')
            readonly_verification = contract.get('spec_contract_version', 1) >= 2 and not task_def['ownership'] and task_def.get('verification') in {'compile', 'behavior', 'visual'}
            if not isinstance(files, dict) or receipt.get('status') == 'generated' and not files and not readonly_verification:
                raise MigrationError('Receipt must pin actual generated files')
            for name, expected in files.items():
                if name not in task_def['ownership'] or digest(safe_child(project, name).read_bytes()) != expected:
                    raise MigrationError('Receipt ownership/hash mismatch: ' + name)
            if receipt.get('status') == 'generated' and set(files) != set(task_def['ownership']):
                raise MigrationError('Generated receipt omitted planned outputs')
            if set(receipt.get('files_touched', [])) != set(files):
                raise MigrationError('Original touched-files field differs from pinned outputs')
            if set(receipt.get('ac_ids', [])) != set(task_def.get('ac_ids', [])):
                raise MigrationError('Receipt omitted task acceptance criteria')
            if receipt.get('status') == 'generated' and receipt.get('findings'):
                raise MigrationError('Open semantic findings cannot be landed as generated success')
            if receipt['status'] == 'blocked':
                blocked.append((task['id'], path))
        action = _land_native_receipts(project, wave, plan_path, blocked)
    else:
        state_path = project / 'spec/state/state.json'
        if state_path.exists():
            rows = read_json(state_path).get('waves', {}).get(wave, {}).get('tasks', [])
            rows = rows.values() if isinstance(rows, dict) else rows
            if any((row.get('status') == 'failed' and not str(row.get('reason', '')).startswith('RETRY_NEEDED'))
                   or row.get('status') == 'folded' or row.get('final_state') == 'BLOCKED' for row in rows):
                raise MigrationError('Native failed/blocked tasks cannot advance; repair and explicitly review replan')
        usage_observation = None
        if usage_ledger is not None:
            from .usage_budget import check_for_dispatch
            ledger = Path(usage_ledger)
            if not ledger.is_absolute():
                ledger = safe_child(project, ledger.as_posix())
            usage_observation = check_for_dispatch(ledger, run_id=usage_run_id, project_root=project)
            if not usage_observation['can_continue']:
                reasons = usage_observation['reasons'] or ['no_remaining_dispatch_budget']
                raise MigrationError('Usage budget refused dispatch: ' + ', '.join(reasons))
        before = execution_files(project)
        evidence_path = project / f'spec/reports/ios-dispatch-{wave}.json'
        prior = read_json(evidence_path) if evidence_path.exists() else None
        if prior and prior.get('plan_sha256') != digest(plan_path.read_bytes()):
            prior = None
        prefix = 'spec/state/fence-snapshot/'
        previous_fence = _fence_files(project)
        if prior:
            pinned_fence = {p: value for p, value in prior['before_files'].items() if p.startswith(prefix)}
            if pinned_fence != previous_fence:
                raise MigrationError('Dispatch changed files outside ownership: original fence snapshot changed')
        # The original next_batch creates these backup copies before workers
        # start. Pin only actual copies matching its original scope and the
        # source bytes at this trusted call boundary, not arbitrary future
        # files under a directory that happens to be named fence-snapshot.
        expected_fence = {prefix + path: digest(safe_child(project, path).read_bytes())
                          for path in kernel()._scope_files(os.fspath(io_path(project)))}
        action = invoke(project, 'next_batch', ['--plan', str(plan_path), '--state', 'spec/state/state.json', '--json'])
        if usage_observation is not None:
            action['usage_budget'] = dict(usage_observation, ledger=str(ledger), scope='supplied evidence before dispatch; no reservation')
        if action.get('action') == 'dispatch':
            generated_fence = _fence_files(project)
            if any(path != prefix + '.manifest.json'
                   and value not in (expected_fence.get(path), previous_fence.get(path))
                   for path, value in generated_fence.items()):
                raise MigrationError('Original dispatch fence copy does not match its source snapshot')
            # Preserve earlier batch baseline so in-flight writes stay attributable.
            if prior:
                before = prior['before_files']
                task_ids = list(dict.fromkeys(prior['task_ids'] + [b['id'] for b in action['batch']]))
            else:
                task_ids = [b['id'] for b in action['batch']]
            before = {p: value for p, value in before.items() if not p.startswith(prefix)}
            before.update(generated_fence)
            write_json(evidence_path, {'plan_sha256': digest(plan_path.read_bytes()), 'before_files': before, 'task_ids': task_ids})
    action['ios_scope'] = 'task generation only; compile and behavior gates remain separate'
    action['behavior_verified'] = False
    failed = (bool(action.get('ios_blocked_receipts')) or action.get('action') == 'escalate'
              or any(x.get('status') in {'RETRY_NEEDED', 'RETRY_EXHAUSTED', 'FAIL', 'INFRA_FAIL'} for x in action.get('landed', [])))
    return action, 2 if failed else 0


def replan(project, input_path):
    """Explicit new run: preserve every old control artifact; never import old success."""
    from .native_pipeline import context
    source, project = context(project)
    request = validate(read_json(input_path), 'planRequest')
    review = request.get('replan_review', {})
    if not all(isinstance(review.get(k), str) and review[k].strip() for k in ('reviewer', 'reason')):
        raise MigrationError('Replan requires a concrete reviewer and change reason')
    graph, _ = validate_graph(source, project)
    if request['graph_sha256'] != digest(json_bytes(graph)) or request['wave'] == 'domains' and check(project)[1]:
        raise MigrationError('Resolve changed source contracts before replanning')
    generate(project, input_path, validate_only=True)
    state_dir = project / 'spec/state'
    if (state_dir / 'dispatch.json').exists():
        dispatch = read_json(state_dir / 'dispatch.json')
        journal = read_json(state_dir / 'journal.json') if (state_dir / 'journal.json').exists() else {}
        for wave, record in dispatch.get('waves', {}).items():
            landed, _ = kernel().journal_indexes(journal, wave)
            if any(row.get('attempts', 0) > landed.get(ident, 0) for ident, row in record.get('dispatched', {}).items()):
                raise MigrationError('In-flight tasks must land or be explicitly terminated before replan')
    archive = safe_child(project, 'spec/.a2h/history/replan-' + uuid.uuid4().hex)
    archive.mkdir(parents=True)
    moved = []
    try:
        for relative in ('spec/state', 'spec/blueprint', 'spec/waves',
                         'spec/reports/ios-dispatch-understand.json', 'spec/reports/ios-dispatch-domains.json'):
            origin = safe_child(project, relative)
            if origin.exists():
                destination = safe_child(archive, relative)
                destination.parent.mkdir(parents=True, exist_ok=True)
                origin.rename(destination)
                moved.append((origin, destination))
        result = generate(project, input_path)
    except Exception:
        # No recursive deletes. A partial new run is retained for diagnosis; old
        # data stays recoverable and never gets silently overwritten.
        write_json(archive / 'replan-failure.json', {'review': review, 'moved': [str(d) for _, d in moved], 'status': 'failed'})
        raise
    result.update(archive=str(archive), replan_review=review, prior_success_inherited=False)
    write_json(archive / 'replan-review.json', result)
    return result
