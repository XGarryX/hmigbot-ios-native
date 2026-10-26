# OPTIMIZED_FOR_MACOS_XCODE_NATIVE: retains Python orchestration only; compiler/build facts come from Xcode CLI.
"""Run the unchanged compiled structural pipeline in its expected skill layout.

Nuitka resolves ``__file__`` beside its executable.  The shipping launcher puts
that executable three directories below scripts, so sibling helper discovery
cannot find the complete bundle.  A disposable layout places the entry binary
beside the original scripts and retains each helper's own unchanged payload.
Native input bridges retain the original detectors and their failure decisions.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import os
from pathlib import Path
import platform
import shutil
import subprocess
import tempfile

from .core import io_path
from .init_environment import check_runtime_ready
from .portable_helper import quarantine_free_launcher
from .process_runtime import run as run_owned_process
from .runtime_timeouts import timeout_for

ROOT = Path(__file__).resolve().parents[2]
VENDOR = ROOT / 'vendor/hmigbot/skills'
HELPERS = {
    'arkts-structural-closure': ('assembly_gate.py', 'binding_gate.py'),
    'a2h-execute': ('dead_shell_gate.py', 'carrier_gate.py',
                    'hit_test_gate.py', 'resource_name_gate.py'),
}


def _platform():
    from .host import require_supported_host
    require_supported_host()
    return 'macos', 'arm64'


def _copy_scripts(source, destination, system, architecture, *, project_root=None, permission_receipts=None):
    payload = source / 'bin' / (system + '-' + architecture) / '_entry.dist'
    if not payload.is_dir():
        raise ValueError('Complete original structural payload is missing: ' + str(payload))
    if system == 'macos':
        receipt = check_runtime_ready(project_root, payload)
        if permission_receipts is not None:
            permission_receipts.append(receipt)
    destination.mkdir(parents=True)
    for path in source.iterdir():
        if path.name in {'bin', 'tests', '__pycache__'}:
            continue
        if path.is_dir():
            shutil.copytree(path, destination / path.name, ignore=shutil.ignore_patterns('__pycache__'))
        else:
            shutil.copy2(path, destination / path.name)
            if system == 'macos' and path.suffix == '.py':
                text = path.read_text(encoding='utf-8')
                safe = quarantine_free_launcher(text)
                if safe != text:
                    (destination / path.name).write_text(safe, encoding='utf-8')
    copied = destination / 'bin' / (system + '-' + architecture) / '_entry.dist'
    shutil.copytree(payload, copied)
    # macOS preserves vendor mode bits; Nuitka entrypoints must be executable.
    if system == 'macos':
        for entry in (copied / '_entry.bin',):
            if entry.exists():
                entry.chmod(entry.stat().st_mode | 0o111)
    return payload


@contextmanager
def runtime_layout(*, project_root=None, permission_receipts=None):
    """Yield an isolated original engine; never mutate the installed bundle."""
    system, architecture = _platform()
    with tempfile.TemporaryDirectory(prefix='native-pipeline-', dir='/private/tmp' if system == 'macos' else None) as temporary:
        skills = Path(temporary) / 'skills'
        closure = skills / 'arkts-structural-closure/scripts'
        payload = _copy_scripts(VENDOR / 'arkts-structural-closure/scripts', closure, system, architecture,
                                project_root=project_root, permission_receipts=permission_receipts)
        _copy_scripts(VENDOR / 'a2h-execute/scripts', skills / 'a2h-execute/scripts', system, architecture,
                      project_root=project_root, permission_receipts=permission_receipts)
        for skill, names in HELPERS.items():
            for name in names:
                if not (skills / skill / 'scripts' / name).is_file():
                    raise ValueError('Complete original structural helper is missing: ' + name)
        # The entrypoint is flat only to restore __file__-based sibling paths.
        # Nested helper launchers keep their original payload and command line.
        for path in payload.iterdir():
            if path.is_dir():
                shutil.copytree(path, closure / path.name)
            else:
                shutil.copy2(path, closure / path.name)
        icon = skills / 'arkts-icon-sizing/scripts/icon_autofix.py'
        icon.parent.mkdir(parents=True)
        icon.write_text('import sys\n'
            f'sys.path.insert(0, {str(ROOT / "src")!r})\n'
            'from hmigbot_ios.native_icon_scope import autofix_main\n'
            'raise SystemExit(autofix_main())\n', encoding='utf-8')
        literal = skills / 'a2h-execute/scripts/literal_gate.py'
        literal.write_text('import sys\n'
            f'sys.path.insert(0, {str(ROOT / "src")!r})\n'
            'from hmigbot_ios.native_literal_scope import main\n'
            'raise SystemExit(main())\n', encoding='utf-8')
        from .native_pipeline_semantics import stage_runtime
        stage_runtime(skills, root=ROOT)
        env = {**os.environ, 'PYTHONUTF8': '1', 'PYTHONIOENCODING': 'utf-8',
               'ARKTS_SKILL_DIR': str(closure)}
        if system == 'windows':
            # Deferred source path; _platform refuses this host before any copy.
            from .windows_python_runtime import stage_base_python
            stage_base_python(closure, env)
        suffix = '.exe' if system == 'windows' else '.bin'
        yield closure / ('_entry' + suffix), env


def _invoke_raw(arguments, original=None):
    """Return the original pipeline's exact stdout/stderr/exit disposition."""
    arguments = list(map(str, arguments))
    # All platforms need the same sibling-helper layout.
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--project-root', type=Path)
    probe, _ = parser.parse_known_args(arguments)
    project = io_path(probe.project_root or Path.cwd()).resolve()
    permission_receipts = []
    with runtime_layout(project_root=project, permission_receipts=permission_receipts) as (executable, env):
        command = [str(executable), 'structural_loop', *arguments]
        try:
            limit = timeout_for('structural', env=env)
            result = run_owned_process(command, cwd=project, env=env, timeout=limit)
        except subprocess.TimeoutExpired as exc:
            # Preserve the Mac subprocess timeout's actual partial output.
            # Descendant-tree cleanup is not claimed by this adapter.
            result = subprocess.CompletedProcess(command, 124, exc.output or b'',
                (exc.stderr or b'') + b'\nOriginal structural pipeline timed out.\n')
    process = subprocess.CompletedProcess(result.args, result.returncode,
        result.stdout.decode('utf-8', errors='replace'),
        result.stderr.decode('utf-8', errors='replace'))
    process.macos_permission_receipts = permission_receipts
    return process


def invoke(arguments, original=None):
    """Preserve raw engine evidence, then use the original native loop protocol."""
    arguments = list(map(str, arguments))
    if arguments and arguments[0] == 'iterate':
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument('--mode')
        args, _ = parser.parse_known_args(arguments)
        if args.mode == 'pipeline':
            from .native_pipeline_semantics import pipeline_iterate
            return pipeline_iterate(arguments, lambda raw: _invoke_raw(raw, original=original))
    return _invoke_raw(arguments, original=original)
