"""Explicit initialization of a project's controlled tool runtime.

Inspection is read-only. Preparation changes only listed tool entry metadata and
observed runtime quarantine, with separate receipts. No application is executed.
"""
from __future__ import annotations

import os
from pathlib import Path
import platform
import stat

from .core import MigrationError, digest, json_bytes, read_json, write_json
from .macos_permissions import _root, _target, _tree, _quarantined, ensure_runtime_permissions

REPORT = 'spec/reports/init-environment.json'
MANIFEST = 'runtime-entrypoints.json'


def inspect(project, runtime):
    from .native_pipeline import context
    from .host import detect_host_profile
    source, project = context(Path(project))
    runtime = Path(runtime).resolve(strict=True)
    entries = read_json(runtime / MANIFEST)
    if entries.get('schema_version') != 1 or not isinstance(entries.get('entries'), list):
        raise MigrationError('Invalid controlled runtime entrypoint manifest')
    missing, executable, roots = [], [], set()
    controlled = runtime.is_relative_to(project.resolve())
    for relative in entries['entries']:
        path = _target(runtime, relative)
        # Known entries never authorize a link or hard-link outside the runtime.
        _tree(runtime, path)
        if not stat.S_ISREG(path.stat().st_mode):
            raise MigrationError('Controlled entrypoint must be a regular file: ' + relative)
        if not os.access(path, os.X_OK):
            missing.append(relative)
        executable.append({'path': relative, 'sha256': digest(path.read_bytes()),
                           'mode': stat.S_IMODE(path.stat().st_mode)})
        roots.add(path.parent if path.name in {'_entry.bin', 'Python', '_entry.exe'} else path)
    quarantine = []
    if platform.system() == 'Darwin':
        for path in sorted(roots):
            quarantine.extend(_quarantined(_tree(runtime, path)))
    host = detect_host_profile()
    return {'schema_version': 1, 'kind': 'init_environment', 'project': str(project),
            'runtime': str(runtime), 'controlled_runtime': controlled,
            'entrypoints': executable, 'missing_execute': missing,
            'quarantined_paths': sorted(set(quarantine)),
            'capabilities': {'static_source_read': os.access(source, os.R_OK),
                             'native_source_capture': host['source'],
                             'target_build': 'requires_validate', 'device_verification': 'not_run'},
            'status': 'preparation_required' if missing or quarantine else 'ready',
            'actions': [], 'product_verified': False}


def run(project, runtime, *, prepare=False):
    receipt = inspect(project, runtime)
    root, runtime = Path(receipt['project']), Path(receipt['runtime'])
    if not prepare:
        return receipt
    if not receipt['controlled_runtime'] and (receipt['missing_execute'] or receipt['quarantined_paths']):
        raise MigrationError('External runtime needs installation into this project; init cannot repair an external checkout')
    for relative in receipt['missing_execute']:
        path = _target(root, runtime / relative)
        _tree(root, path)
        before = stat.S_IMODE(path.stat().st_mode)
        path.chmod(before | 0o111)
        receipt['actions'].append({'operation': 'chmod', 'path': str(path), 'before': before,
                                   'after': stat.S_IMODE(path.stat().st_mode)})
    # Only observed attributes on the controlled runtime roots are eligible.
    targets = set()
    for value in receipt['quarantined_paths']:
        path = _target(root, value)
        targets.add(path)
    for target in sorted(targets):
        if not target.is_relative_to(runtime):
            raise MigrationError('Quarantine target escaped controlled runtime')
        receipt['actions'].append(ensure_runtime_permissions(root, target))
    checked = inspect(root, runtime)
    receipt.update(status=checked['status'], missing_execute=checked['missing_execute'],
                   quarantined_paths=checked['quarantined_paths'])
    write_json(root / REPORT, receipt)
    return receipt


def check_runtime_ready(project_root, target, *, source_path=None):
    """Read-only per-call admission; invalid preparation returns its recovery path."""
    path = Path(target).resolve(strict=True)
    if platform.system() != 'Darwin':
        return {'status': 'not_applicable', 'mutated': False, 'product_verified': False}
    root = _root(project_root) if project_root is not None else None
    if root is not None and source_path is not None:
        lexical = Path(os.path.abspath(source_path))
        if lexical.is_relative_to(root):
            _target(root, lexical)
    # External tools can run but cannot become mutation roots.
    boundary = root if root is not None and path.is_relative_to(root) else path
    entries = _tree(boundary, path)
    quarantined = _quarantined(entries)
    executable = path / '_entry.bin' if path.is_dir() else path
    if quarantined or executable.is_file() and not os.access(executable, os.X_OK):
        raise MigrationError('Runtime preparation invalid: ' + str(path) +
                             '; run init-environment --prepare for the configured project (external runtime requires installation)')
    return {'status': 'ready', 'target': str(path), 'mutated': False, 'product_verified': False}
