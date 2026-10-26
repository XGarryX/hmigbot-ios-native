"""Explicit initialization of a project's controlled tool runtime.

Inspection is read-only. Preparation changes only listed tool entry metadata and
observed runtime quarantine, with separate receipts. No application is executed.
"""
from __future__ import annotations

import os
from pathlib import Path
import platform
import stat

from .core import MigrationError, digest, json_bytes, read_json, safe_child, write_json
from .macos_permissions import _root, _target, _tree, _quarantined, ensure_runtime_permissions

REPORT = 'spec/reports/init-environment.json'
MANIFEST = 'runtime-entrypoints.json'


def permission_options(source, project, host, mcp):
    """Explain capabilities before they run, without inventing OS authorization."""
    def entry(name, purpose, reads, writes, available, alternatives, authorization):
        return {'capability': name, 'purpose': purpose, 'reads': reads, 'writes': writes,
                'capability_available': available, 'authorized': None,
                'actually_invoked': False, 'result': 'not_run',
                'authorization_steps': authorization, 'options': alternatives,
                'authorization_note': 'Reuse existing explicit task and host authorization; do not repeat already authorized steps'}
    return [entry('source_analysis', 'Read the chosen iOS source to establish migration facts',
                  [str(source)], [], os.access(source, os.R_OK),
                  [{'id': 'read_source', 'difference': 'Enables source-backed analysis within this directory'},
                   {'id': 'environment_only', 'difference': 'Environment diagnosis/reporting continues; source conclusions remain not_run'}],
                  'Grant the host/agent read access only to the selected source directory when not already authorized'),
            entry('project_outputs', 'Write this migration project configuration, evidence and generated outputs',
                  [str(project)], [str(project)], os.access(project, os.W_OK),
                  [{'id': 'project_write', 'difference': 'Allows the requested outputs inside this project'},
                   {'id': 'choose_writable_output', 'difference': 'Use an explicitly writable project/cache path; changing cwd does not change sandbox access'}],
                  'Authorize the selected target directory through the host, or choose an already writable target; no source-write scope is implied'),
            entry('native_source_capture', 'Capture the selected iOS compiler/build context with Xcode CLI',
                  [str(source), 'Installed Xcode toolchain/SDK'], ['Selected task build/cache/evidence directories'],
                  host.get('capabilities', {}).get('ios.build') == 'available',
                  [{'id': 'native_cli', 'difference': 'Produces actual Xcode/compiler evidence; may execute the selected project build steps'},
                   {'id': 'static_or_replay', 'difference': 'Static or current bound evidence can be inspected; missing native proof remains unresolved'}],
                  'Use the existing build authorization and writable task cache; resolve any license/SDK prompt manually through official Xcode/CLI steps'),
            entry('xcode_mcp', 'Read applicable Xcode project or official documentation context',
                  ['Only the authorized project and actual advertised read tools'], [],
                  mcp.get('tool_access', {}).get('capability_available'),
                  [{'id': 'enable', 'difference': 'Adds MCP context; needs service plus agent/project authorization'},
                   {'id': 'skip', 'difference': 'Continues current xcodebuild/xcrun/Swift/Clang CLI evidence without MCP'}],
                  'Choose --mcp enable --prepare or --mcp skip; if needed enable manually in Xcode settings and approve only the intended agent/project'),
            entry('target_build', 'Compile the chosen HarmonyOS product using its actual target SDK',
                  [str(project), 'Selected target SDK'], ['Target build artifacts and task cache'],
                  host.get('capabilities', {}).get('harmony.build') == 'available',
                  [{'id': 'target_sdk', 'difference': 'Allows actual target compilation when its SDK is available'},
                   {'id': 'source_only', 'difference': 'Source analysis and reporting continue; target compilation remains not_run'}],
                  'Install/configure the selected official target SDK and authorize its project output/cache paths before that build'),
            entry('device_verification', 'Perform separately requested verification on a specified device',
                  ['Only separately authorized device evidence'], ['Only separately authorized device changes'], None,
                  [{'id': 'existing_evidence', 'difference': 'Review current bound CLI/log evidence without controlling a device'},
                   {'id': 'not_selected', 'difference': 'Keep device verification not_run; no screen or remote-device capability is enabled by init'}],
                  'No device or screen capability is authorized by initialization; keep it outside default calls')]


def inspect(project, runtime, *, entrypoints=(), mcp='ask'):
    from .native_pipeline import context
    from .host import detect_host_profile
    source, project = context(Path(project))
    runtime = Path(runtime).resolve(strict=True)
    if not isinstance(entrypoints, (list, tuple)) or any(not isinstance(v, str) or not v for v in entrypoints):
        raise MigrationError('Selected runtime entrypoints must be explicit relative paths')
    selected = list(dict.fromkeys(entrypoints))
    manifest_error = None
    try:
        entries = read_json(runtime / MANIFEST)
        if (entries.get('schema_version') != 1 or not isinstance(entries.get('entries'), list)
                or any(not isinstance(v, str) for v in entries['entries'])):
            raise MigrationError('Invalid controlled runtime entrypoint manifest')
    except (MigrationError, OSError, ValueError, TypeError) as exc:
        if selected:
            raise MigrationError('Cannot admit selected runtime entrypoints: ' + str(exc)) from exc
        entries, manifest_error = {'entries': []}, str(exc)
    if not set(selected) <= set(entries['entries']):
        raise MigrationError('Selected entrypoint is outside the controlled runtime manifest')
    missing, executable, roots, advisories = [], [], set(), []
    controlled = runtime.is_relative_to(project.resolve())
    for relative in entries['entries']:
        required = relative in selected
        try:
            path = safe_child(runtime, relative)
            if not path.is_file():
                raise MigrationError('Runtime entrypoint is missing or not a regular file: ' + relative)
            if not required:
                # Full payload integrity belongs to install/release auditing.
                # Per-call admission below remains strict for the actual tool.
                executable.append({'path': relative, 'selected': False, 'status': 'present'})
                continue
            path = _target(runtime, relative)
            _tree(runtime, path)
            if not stat.S_ISREG(path.stat().st_mode):
                raise MigrationError('Controlled entrypoint must be a regular file: ' + relative)
        except (MigrationError, OSError) as exc:
            if required:
                raise MigrationError('Selected runtime entrypoint unavailable: ' + relative + '; ' + str(exc) +
                                     '; restore/install this selected payload before its call, or continue independent static/CLI work without it') from exc
            advisories.append({'path': relative, 'status': 'unavailable', 'blocking': False, 'reason': str(exc),
                               'options': [{'id': 'continue_selected_work', 'difference': 'This backend is not selected; current independent CLI/static work continues'},
                                           {'id': 'restore_when_needed', 'difference': 'Install or restore only this payload before selecting its capability'}]})
            continue
        if not os.access(path, os.X_OK):
            missing.append(relative)
        executable.append({'path': relative, 'selected': True, 'sha256': digest(path.read_bytes()),
                           'mode': stat.S_IMODE(path.stat().st_mode)})
        roots.add(path.parent if path.name in {'_entry.bin', 'Python', '_entry.exe'} else path)
    quarantine = []
    if platform.system() == 'Darwin':
        for path in sorted(roots):
            quarantine.extend(_quarantined(_tree(runtime, path)))
    host = detect_host_profile()
    from .xcode_mcp import prepare as prepare_mcp
    mcp_status = prepare_mcp(choice=mcp, apply=False)
    return {'schema_version': 1, 'kind': 'init_environment', 'project': str(project),
            'runtime': str(runtime), 'controlled_runtime': controlled,
            'entrypoints': executable, 'selected_entrypoints': selected,
            'advisories': advisories, 'manifest_error': manifest_error, 'missing_execute': missing,
            'quarantined_paths': sorted(set(quarantine)),
            'capabilities': {'static_source_read': os.access(source, os.R_OK),
                             'native_source_capture': host['source'],
                             'target_build': 'requires_validate', 'device_verification': 'not_run',
                             'xcode_mcp': mcp_status},
            'permission_preflight': permission_options(source, project, host, mcp_status),
            'permission_preflight_scope': 'Subsequent conversion capabilities; permission probes and preparation metadata are separate actual actions',
            'status': 'preparation_required' if missing or quarantine else 'ready',
            'actions': [], 'product_verified': False}


def run(project, runtime, *, prepare=False, entrypoints=(), mcp='ask'):
    receipt = inspect(project, runtime, entrypoints=entrypoints, mcp=mcp)
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
    checked = inspect(root, runtime, entrypoints=entrypoints, mcp=mcp)
    receipt.update(status=checked['status'], missing_execute=checked['missing_execute'],
                   quarantined_paths=checked['quarantined_paths'])
    from .xcode_mcp import prepare as prepare_mcp
    receipt['capabilities']['xcode_mcp'] = prepare_mcp(choice=mcp, apply=True)
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
