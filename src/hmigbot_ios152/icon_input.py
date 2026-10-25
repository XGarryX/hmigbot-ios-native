"""Prevent the original pipeline detector from applying an assumed source density.

No target code or state ledger is written here. The original audit and autofix
dry-run determine the original detector's own would-change set. Apply a source-
evidenced explicit plan before calling the loop, never as an implicit exception.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from uuid import uuid4

from .graph_wire import _emit


def snapshot(project):
    return {p.relative_to(project).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in project.rglob('*.ets') if p.is_file()}


def changed(before, after):
    return sorted(p for p in before.keys() | after.keys() if before.get(p) != after.get(p))


def maybe_run(engine, argv, scripts_dir, *, pipeline_runner=None):
    if not argv or argv[0] != 'iterate' or '--help' in argv or '-h' in argv:
        return None
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--mode'); parser.add_argument('--project-root')
    args, _ = parser.parse_known_args(argv[1:])
    if args.mode != 'pipeline' or not args.project_root:
        return None
    project = Path(args.project_root).resolve()
    if not project.is_dir():
        return None  # original CLI owns normal argument validation
    evidence = project / 'spec/execution/autofix-log/native-icon-input' / (
        datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '-' + uuid4().hex[:8])
    evidence.mkdir(parents=True, exist_ok=False)
    record = {'adapter': 'hmigbot_ios152.icon_input.v1', 'project': str(project),
              'arguments': list(argv), 'original_called': False, 'writes_target_or_ledgers': False}
    before = snapshot(project)
    record['code_before'] = before
    env = dict(os.environ, PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1')
    icon_scripts = Path(scripts_dir).resolve().parents[1] / 'arkts-icon-sizing/scripts'
    result_code = 3
    raw_out = raw_err = b''
    try:
        for name, tail in [('icon_audit', ['--json', str(evidence / 'audit.json')]),
                           ('icon_autofix', ['--project-root', str(project), '--output-json', str(evidence / 'dry-run.json')])]:
            command = [sys.executable, str(icon_scripts / f'{name}.py'), *tail]
            result = subprocess.run(command, cwd=project, capture_output=True, env=env)
            (evidence / f'{name}-stdout.log').write_bytes(result.stdout)
            (evidence / f'{name}-stderr.log').write_bytes(result.stderr)
            if result.returncode:
                raise ValueError(f'Original read-only {name} failed with exit {result.returncode}')
        check = json.loads((evidence / 'dry-run.json').read_text(encoding='utf-8-sig'))
        record['would_fix_count'] = check['fixed_count']
        record['would_fix'] = check.get('fixed', [])
        record['dynamic_unresolved'] = check.get('dynamic_unresolved', [])
        record['no_raster_unresolved'] = check.get('no_raster_unresolved', [])
        record['preflight_changed_code'] = changed(before, snapshot(project))
        if record['preflight_changed_code']:
            raise ValueError('Original dry-run unexpectedly changed target code; stop as a tool defect')
        if check['fixed_count'] != 0:
            raise ValueError('Native image dimensions need source evidence before the original pipeline loop: '
                             + '; '.join(check.get('fixed', []))
                             + '. Inspect the actual modifier chain first; retain correct dimensions. '
                             'Apply an explicit source-backed size/ratio, then rerun. No assumed density is allowed.')
        if pipeline_runner is None:
            result = subprocess.run([str(engine), 'structural_loop', *argv], capture_output=True,
                                    env=dict(env, ARKTS_SKILL_DIR=str(scripts_dir)))
            record['original_called'] = True
            record['original_exit_code'] = result.returncode
            raw_out, raw_err = result.stdout, result.stderr
            (evidence / 'original-stdout.log').write_bytes(raw_out)
            (evidence / 'original-stderr.log').write_bytes(raw_err)
            result_code = result.returncode
        else:
            record['pipeline_adapter_called'] = True
            outcome = None
            try:
                outcome = pipeline_runner(project=project, argv=list(argv), engine=engine,
                                          scripts_dir=Path(scripts_dir), env=dict(env),
                                          code_before=dict(before), icon_evidence=evidence)
                record['original_called'] = outcome.backend_called
                if outcome.backend_called:
                    record['original_exit_code'] = outcome.backend_exit_code
                    (evidence / 'original-stdout.log').write_bytes(outcome.backend_stdout)
                    (evidence / 'original-stderr.log').write_bytes(outcome.backend_stderr)
                record['canonical_exit_code'] = outcome.canonical_exit_code
                record['canonical_committed'] = outcome.canonical_committed
                record['canonical_files'] = outcome.canonical_files
                record['failure_stage'] = outcome.failure_stage
                record['backend_workdir'] = str(outcome.backend_workdir) if outcome.backend_workdir else None
                adapter_record = {
                    'backend_called': outcome.backend_called,
                    'backend_exit_code': outcome.backend_exit_code,
                    'backend_workdir': record['backend_workdir'],
                    'backend_verdict_discarded': outcome.backend_called,
                    'binding_rows': outcome.binding_rows,
                    'orphan_provenance': getattr(outcome, 'orphan_provenance', {}),
                    'failure_stage': outcome.failure_stage,
                    'canonical_committed': outcome.canonical_committed,
                    'canonical_files': outcome.canonical_files,
                    'canonical_exit_code': outcome.canonical_exit_code,
                }
                if outcome.canonical_exit_code == 0 and not (
                        outcome.backend_called and outcome.canonical_committed and
                        outcome.failure_stage is None):
                    raise ValueError('Pipeline runner returned success without a complete committed measurement')
                adapter_path = evidence / 'pipeline-adapter.json'
                adapter_path.write_text(json.dumps(adapter_record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
                record['pipeline_adapter_record'] = str(adapter_path)
                raw_out, raw_err = outcome.stdout, outcome.stderr
                result_code = outcome.canonical_exit_code
            except Exception as error:
                if outcome is None:
                    # A failed callback has not supplied an observation of its
                    # backend/commit actions. Preserve that uncertainty.
                    record['original_called'] = None
                    record['canonical_committed'] = None
                raise ValueError(f'Pipeline runner failed: {type(error).__name__}: {error}') from error
        after = snapshot(project)
        record['code_after'] = after
        record['unexpected_code_changes'] = changed(before, after)
        if record['unexpected_code_changes']:
            result_code = 3
            raw_err += ('Native icon input guard: original pipeline unexpectedly changed target code: '
                        + ', '.join(record['unexpected_code_changes']) + '\n').encode('utf-8')
    except (OSError, ValueError, KeyError, TypeError) as error:
        if record.get('pipeline_adapter_called'):
            result_code = 3
        record['error'] = str(error)
        raw_err += ('Native icon input guard: ' + str(error) + '\n').encode('utf-8')
    if record.get('pipeline_adapter_called'):
        try:
            (evidence / 'canonical-stdout.log').write_bytes(raw_out)
            (evidence / 'canonical-stderr.log').write_bytes(raw_err)
        except OSError as error:
            result_code = 3
            record['error'] = f'Cannot save pipeline output evidence: {error}'
            raw_err += (record['error'] + '\n').encode('utf-8')
    record['exit_code'] = result_code
    if record.get('pipeline_adapter_called'):
        try:
            (evidence / 'guard.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        except OSError as error:
            raw_err += (f'Cannot save pipeline guard evidence: {error}\n').encode('utf-8')
            _emit(sys.stdout, raw_out); _emit(sys.stderr, raw_err)
            return 3
    else:
        (evidence / 'guard.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    _emit(sys.stdout, raw_out); _emit(sys.stderr, raw_err)
    return result_code
