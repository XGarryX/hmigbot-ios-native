"""Stage the base Windows interpreter beside disposable compiled payloads.

On Windows, venv's python.exe may be a redirector requiring pyvenv.cfg, not a
relocatable interpreter. CPython itself uses sys._base_executable to identify
the base executable when creating venvs:
https://github.com/python/cpython/blob/3.13/Lib/venv/__init__.py
"""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import sys

from .core import MigrationError


def base_python_executable() -> Path:
    """Select only an existing interpreter from this runtime's base install.

    Never search PATH, copy a venv launcher, or switch Python installations to
    conceal a broken installation. The conventional base path is a fallback
    for runtimes without CPython's private _base_executable attribute.
    """
    base = Path(sys.base_prefix).resolve()
    candidates = []
    executable = getattr(sys, '_base_executable', None)
    if executable:
        candidates.append(Path(executable))
    candidates.append(base / 'python.exe')
    in_venv = sys.prefix != sys.base_prefix
    venv = Path(sys.prefix).resolve()
    for candidate in candidates:
        if not candidate.is_absolute() or not candidate.is_file():
            continue
        candidate = candidate.resolve()
        if not candidate.is_relative_to(base):
            continue
        if in_venv and candidate.is_relative_to(venv):
            continue
        if any((parent / 'pyvenv.cfg').is_file() for parent in (candidate.parent, candidate.parent.parent)):
            continue
        return candidate
    raise MigrationError('Cannot stage a real base Windows Python interpreter from ' + str(base)
                         + '; refusing to copy the virtual-environment launcher')


def stage_base_python(directory: Path, env: dict) -> Path:
    """Copy aliases and base DLLs, retaining the existing vendor staging API."""
    executable = base_python_executable()
    directory = Path(directory)
    for name in ('python.exe', 'python3.exe'):
        shutil.copy2(executable, directory / name)
    for dll in Path(sys.base_prefix).glob('*.dll'):
        shutil.copy2(dll, directory / dll.name)
    env['PATH'] = str(directory) + os.pathsep + env.get('PATH', '')
    env['PYTHONHOME'] = sys.base_prefix
    return executable
