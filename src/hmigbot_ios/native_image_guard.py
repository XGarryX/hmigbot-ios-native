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

def _emit(stream, data):
    if hasattr(stream, 'buffer'):
        stream.buffer.write(data); stream.buffer.flush()
    else:
        stream.write(data.decode('utf-8', errors='replace'))



def snapshot(project):
    return {p.relative_to(project).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in project.rglob('*.ets') if p.is_file()}


def changed(before, after):
    return sorted(p for p in before.keys() | after.keys() if before.get(p) != after.get(p))


def maybe_run(engine, argv, scripts_dir, *, invoke=True):
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
        if not invoke:
            record.update(exit_code=0, original_called=False, scope='read-only image preflight; shared native layout invokes the unchanged engine')
            (evidence / 'guard.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
            return 0
        result = subprocess.run([str(engine), 'structural_loop', *argv], capture_output=True,
                                env=dict(env, ARKTS_SKILL_DIR=str(scripts_dir)))
        record['original_called'] = True
        record['original_exit_code'] = result.returncode
        raw_out, raw_err = result.stdout, result.stderr
        (evidence / 'original-stdout.log').write_bytes(raw_out)
        (evidence / 'original-stderr.log').write_bytes(raw_err)
        result_code = result.returncode
        after = snapshot(project)
        record['code_after'] = after
        record['unexpected_code_changes'] = changed(before, after)
        if record['unexpected_code_changes']:
            result_code = 3
            raw_err += ('Native icon input guard: original pipeline unexpectedly changed target code: '
                        + ', '.join(record['unexpected_code_changes']) + '\n').encode('utf-8')
    except (OSError, ValueError, KeyError, TypeError) as error:
        record['error'] = str(error)
        raw_err += ('Native icon input guard: ' + str(error) + '\n').encode('utf-8')
    record['exit_code'] = result_code
    (evidence / 'guard.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    _emit(sys.stdout, raw_out); _emit(sys.stderr, raw_err)
    return result_code
