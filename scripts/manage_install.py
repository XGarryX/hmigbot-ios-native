"""Workspace-only install/upgrade/uninstall with ownership and edit preservation."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import sys
import tempfile
from functools import lru_cache

def filesystem_path(path):
    """Use extended Win32 paths without changing machine-wide long-path policy."""
    path = Path(path).resolve()
    value = str(path)
    if os.name == 'nt' and not value.startswith('\\\\?\\'):
        value = '\\\\?\\UNC\\' + value[2:] if value.startswith('\\\\') else '\\\\?\\' + value
        return Path(value)
    return path


ROOT = filesystem_path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(ROOT / 'src'))
from hmigbot_ios.payload_layout import (DEFERRED_SKILLS, ROOT_DIRECTORIES, ROOT_FILES, exclusion,
                                       release_profile)
BEGIN = '<!-- hmigbot-ios:begin -->'
END = '<!-- hmigbot-ios:end -->'
BLOCK = f'''{BEGIN}
## Native iOS to HarmonyOS migration

Use the bundled $a2h-run: a2h-spec -> a2h-plan -> a2h-execute -> a2h-verify
-> a2h-retrospect. For iOS, read source_platform and ios in .migbot/config.json
and read the native source skills. Keep the shared spec/baseline contracts,
indexed plans, execution briefs, AC traceability and spec/.a2h/open-findings.json.
Use source_anchors and ios-semantics.json to retain SwiftUI/UIKit and language facts.
Load ios-source-analysis/references/harness-v2.md for the control contract.
Read rules/tool-project-status-separation.md in the bundled runtime. Record tool
fix/release/install evidence separately from project gates and conversion progress.
Load references/external-expertise.md in that skill for pinned iOS expertise.
Run expertise-plan/review before the source gate; MCP responses stay tool evidence.
Generate machine facts/obligations and run source-check --harness before plan-ir.
Read a2h-run/references/execution-boundary.md. Run execution-contract --apply,
then the indexed resources/UI/Base/Slices/FV stages and closer/writeback protocol.
Legacy v2 attempts keep their original receipt/recovery API; never run both schedulers.
Only original tools write state ledgers. No screen capture/read/recording or device
remote control is authorized by this installation.
All skills, references, templates, binaries and agent roles are local. No external
HMigBot path or binding packet is needed. Helper runtime: .hmigbot-ios/plugin.
Use the original ArkTS implementation and validation steps. Respect current user
scope and prior authorization; don't repeat already authorized stage approvals.
Dispatch only supported roles, otherwise follow their protocols sequentially.
Distinguish generated, compiled and behavior-verified results. Never fabricate
done markers. Telemetry hooks are not installed and upload is not a prerequisite.
{END}'''


def checksum(data):
    if isinstance(data, Path):
        with filesystem_path(data).open('rb') as stream:
            return hashlib.file_digest(stream, 'sha256').hexdigest()
    return hashlib.sha256(data).hexdigest()


def put(path, data):
    path = filesystem_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(data, Path):
        shutil.copy2(filesystem_path(data), path)
    else:
        path.write_bytes(data)
    if os.name != 'nt' and (path.suffix in {'.sh', '.bin'} or path.name in {'a2h', 'a2h-tool', 'a2h-bootstrap', 'a2h-agreement'}):
        path.chmod(path.stat().st_mode | 0o111)


@lru_cache(maxsize=8)
def skill_names(root):
    names = {s.name for s in (root / 'skills').iterdir() if s.is_dir()}
    # Old owned installations must remain removable after optional source
    # directories have been moved out of this release tree.
    names.update(DEFERRED_SKILLS)
    names.update('a2h-ios-' + s for s in ('run', 'analyze', 'map', 'implement', 'verify', 'evidence'))
    retired = root / 'docs/upstream/retired-skills.json'
    if retired.is_file():
        names.update(json.loads(retired.read_text(encoding='utf-8')))
    return names


def child(workspace, relative):
    p = Path(relative)
    if p.is_absolute() or '..' in p.parts or ':' in relative or '\\' in relative:
        raise ValueError('Invalid managed path: ' + relative)
    path = (workspace / p).resolve()
    if path == workspace or not path.is_relative_to(workspace):
        raise ValueError('Managed path escapes workspace')
    if not relative.startswith(('.hmigbot-ios/', '.agents/skills/', '.codex/agents/', '.migbot/bin/', '.migbot/policies/')) and relative != '.codex/config.toml':
        raise ValueError('Path is outside managed install directories')
    if relative.startswith('.agents/skills/'):
        known = skill_names(ROOT)
        if len(p.parts) < 4 or p.parts[2] not in known:
            raise ValueError('Manifest cannot own another plugin skill')
    # Never traverse existing links/junctions, even if they point back into the workspace.
    cursor = workspace / p
    while cursor != workspace:
        if cursor.is_symlink() or (hasattr(cursor, 'is_junction') and cursor.is_junction()):
            raise ValueError('Managed path contains a link: ' + relative)
        cursor = cursor.parent
    return path


def require_release_host():
    profile = release_profile()
    if (platform.system() != profile['host']['system'] or
            platform.machine().lower() not in profile['host']['architectures']):
        raise ValueError('This release profile supports macOS Apple Silicon only: ' + profile['id'])


def payload(*, check_host=True):
    if check_host:
        require_release_host()
    files = {}
    for folder in sorted(ROOT_DIRECTORIES):
        for path in (ROOT / folder).rglob('*'):
            if exclusion(path.relative_to(ROOT).as_posix(), directory=path.is_dir()):
                continue
            if path.is_file() and not {'__pycache__', '.build', '.swiftpm'}.intersection(path.parts) and path.suffix != '.pyc':
                if path.is_symlink():
                    raise ValueError('Install source contains links')
                files['.hmigbot-ios/plugin/' + path.relative_to(ROOT).as_posix()] = path
    for name in sorted(ROOT_FILES):
        if (ROOT / name).is_file() and not exclusion(name):
            files['.hmigbot-ios/plugin/' + name] = ROOT / name
    for skill in (ROOT / 'skills').iterdir():
        if (not skill.is_dir() or not (skill / 'SKILL.md').is_file() or
                exclusion(skill.relative_to(ROOT).as_posix(), directory=True)):
            continue
        for file in skill.rglob('*'):
            if file.is_file() and not exclusion(file.relative_to(ROOT).as_posix()):
                files['.agents/skills/' + skill.name + '/' + file.relative_to(skill).as_posix()] = file
        files[f'.agents/skills/{skill.name}/runtime.json'] = b'{"runtime_relative":"../../../.hmigbot-ios/plugin"}\n'
    for role in (ROOT / 'agents-codex').glob('*.toml'):
        if not exclusion(role.relative_to(ROOT).as_posix()):
            files['.codex/agents/' + role.name] = role
    for path in (ROOT / 'bin').iterdir():
        if path.is_file() and not exclusion(path.relative_to(ROOT).as_posix()):
            files['.migbot/bin/' + path.name] = path
    asset = ROOT / 'bin/a2h-darwin-arm64'
    if not asset.is_file(): raise ValueError('Bundled runtime unavailable: ' + asset.name)
    files['.migbot/bin/a2h'] = asset
    for path in (ROOT / 'policies').glob('*'):
        if path.is_file() and not exclusion(path.relative_to(ROOT).as_posix()):
            files['.migbot/policies/' + path.name] = path
    return files


def manage(workspace, mode, hmigbot_root=None):
    if hmigbot_root is not None:
        raise ValueError('External binding retired; this release bundles HMigBot resources')
    if sys.version_info < (3, 11):
        raise ValueError('HMigBot iOS requires Python 3.11 or newer')
    workspace = filesystem_path(workspace)
    if not workspace.is_dir():
        raise ValueError('Workspace must already exist')
    metadata = child(workspace, '.hmigbot-ios/install.json')
    old = json.loads(metadata.read_text(encoding='utf-8')) if metadata.exists() else None
    if old and (old.get('owner') != 'hmigbot-ios' or old.get('schema_version') != 1):
        raise ValueError('Unknown existing install manifest')
    owned = old.get('files', {}) if old else {}
    for name in owned:
        child(workspace, name)
    agent_path = workspace / 'AGENTS.md'
    if agent_path.is_symlink():
        raise ValueError('AGENTS.md is a symlink')
    agent_bytes = agent_path.read_bytes() if agent_path.exists() else None
    agent_text = agent_bytes.decode('utf-8-sig') if agent_bytes is not None else ''
    if mode == 'uninstall':
        if not old:
            return {'status': 'not_installed'}
        kept, removed = [], []
        for name, expected in owned.items():
            path = child(workspace, name)
            if not path.exists():
                continue
            if checksum(path) != expected:
                kept.append(name)
            else:
                path.unlink()
                removed.append(name)
        block = old.get('agent_block')
        if agent_bytes is not None and checksum(agent_bytes) == old.get('agent_installed_sha256'):
            original = old.get('agent_original_base64')
            if original is None:
                agent_path.unlink()
            else:
                agent_path.write_bytes(base64.b64decode(original))
        elif block and block in agent_text:
            replacement = agent_text.replace(block, '', 1)
            if replacement.strip():
                agent_path.write_bytes(replacement.encode('utf-8'))
            else:
                agent_path.unlink()
        elif BEGIN in agent_text:
            kept.append('AGENTS.md: edited marker block')
        if kept:
            old['files'] = {name: owned[name] for name in kept if name in owned}
            metadata.write_text(json.dumps(old, indent=2), encoding='utf-8')
        else:
            metadata.unlink()
        # Remove only empty, managed directories. Never recursively remove the workspace.
        parents = {child(workspace, n).parent for n in removed}
        for start in sorted(parents, key=lambda p: len(p.parts), reverse=True):
            p = start
            while p != workspace and p.is_relative_to(workspace) and p.is_dir():
                try:
                    p.rmdir()
                except OSError:
                    break
                p = p.parent
        return {'status': 'uninstalled_with_preserved_edits' if kept else 'uninstalled', 'preserved': kept}
    new = payload()
    codex_config = '.codex/config.toml'
    if not (workspace / codex_config).exists():
        new[codex_config] = b'[features]\nmulti_agent = true\n\n[agents]\nmax_threads = 4\nmax_depth = 2\n'
    elif codex_config in owned:
        new[codex_config] = workspace / codex_config
    if old:
        for name, expected in owned.items():
            path = child(workspace, name)
            if path.exists() and checksum(path) != expected:
                raise ValueError('Upgrade refused: user-edited managed file ' + name)
    for name in new:
        path = child(workspace, name)
        if path.exists() and name not in owned:
            raise ValueError('Install would overwrite an unowned file: ' + name)
    if BEGIN in agent_text:
        if not old or old.get('agent_block') not in agent_text:
            raise ValueError('Existing AGENTS marker is not owned or was edited')
        updated_agents = agent_text.replace(old['agent_block'], BLOCK, 1)
    else:
        updated_agents = agent_text + ('\n\n' if agent_text else '') + BLOCK + '\n'
    hashes = {name: checksum(data) for name, data in new.items()}
    changes = {name for name in new if not child(workspace, name).is_file() or checksum(child(workspace, name)) != hashes[name]}
    rollback = tempfile.TemporaryDirectory(prefix='hmigbot-rollback-')
    backup = {}
    for name in changes | (set(owned) - set(new)):
        path = child(workspace, name)
        saved = filesystem_path(Path(rollback.name) / name)
        if path.exists():
            saved.parent.mkdir(parents=True, exist_ok=True)
            put(saved, path)
            backup[name] = saved
        else:
            backup[name] = None
    prior_metadata = metadata.read_bytes() if metadata.exists() else None
    new_version = json.loads((ROOT / '.codex-plugin/plugin.json').read_text(encoding='utf-8'))['version']
    from hmigbot_ios.upgrade_cleanup import prepare_upgrade_cleanup
    cleanup = prepare_upgrade_cleanup(workspace, old.get('version') if old else None, new_version,
                                      tool_changed=bool(old and (changes or set(owned) - set(new) or old.get('version') != new_version)))
    permission_receipts = []
    try:
        cleanup.apply()
        for name in changes:
            put(child(workspace, name), new[name])
        for name in set(owned) - set(new):
            child(workspace, name).unlink(missing_ok=True)
        agent_path.write_bytes(updated_agents.encode('utf-8'))
        from hmigbot_ios.macos_permissions import ensure_runtime_permissions
        for relative in ['.hmigbot-ios/plugin', *sorted(n for n in new if n.startswith('.migbot/bin/'))]:
            target = child(workspace, relative)
            if target.exists():
                permission_receipts.append(ensure_runtime_permissions(workspace, target))
        manifest = {'schema_version': 1, 'owner': 'hmigbot-ios', 'version': new_version,
                    'release_profile': release_profile(),
                    'files': hashes, 'agent_block': BLOCK,
                    'agent_original_base64': old.get('agent_original_base64') if old else (base64.b64encode(agent_bytes).decode() if agent_bytes is not None else None),
                    'agent_installed_sha256': checksum(agent_path.read_bytes())}
        cleanup.commit()
        manifest['last_upgrade_cleanup'] = cleanup.receipt
        manifest['permission_repairs'] = permission_receipts
        metadata.parent.mkdir(parents=True, exist_ok=True)
        metadata.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    except Exception:
        try:
            cleanup.rollback()
        finally:
            for name, original in backup.items():
                path = child(workspace, name)
                if original is None:
                    path.unlink(missing_ok=True)
                else:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    put(path, original)
            if agent_bytes is None:
                agent_path.unlink(missing_ok=True)
            else:
                agent_path.write_bytes(agent_bytes)
            if prior_metadata is None:
                metadata.unlink(missing_ok=True)
            else:
                metadata.write_bytes(prior_metadata)
        raise
    finally:
        # Files inside rollback can exceed MAX_PATH even when the workspace
        # itself is short. This root was created exclusively by this invocation.
        backup_root = filesystem_path(rollback.name)
        if backup_root.is_dir():
            shutil.rmtree(backup_root)
        rollback.cleanup()
    # Retired generated skills must not remain as empty skill directories.
    for name in sorted(set(owned) - set(new), key=lambda n: n.count('/'), reverse=True):
        directory = child(workspace, name).parent
        while directory != workspace and directory.is_relative_to(workspace) and directory.is_dir():
            try:
                directory.rmdir()  # Empty-only; preserves all unowned/user-created files.
            except OSError:
                break
            directory = directory.parent
    display_workspace = str(workspace)
    if display_workspace.startswith('\\\\?\\UNC\\'):
        display_workspace = '\\\\' + display_workspace[8:]
    elif display_workspace.startswith('\\\\?\\'):
        display_workspace = display_workspace[4:]
    return {'status': 'upgraded' if old else 'installed', 'workspace': display_workspace,
            'skills': sum(1 for key in new if key.startswith('.agents/skills/') and key.endswith('/SKILL.md')),
            'hmigbot': 'bundled', 'agents': sum(key.startswith('.codex/agents/') for key in new),
            'version': manifest['version'], 'upgrade_cleanup': cleanup.receipt,
            'release_profile': manifest['release_profile'],
            'permission_repairs': permission_receipts}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['install', 'uninstall'])
    parser.add_argument('--workspace', type=Path, required=True)
    args = parser.parse_args()
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')
    try:
        print(json.dumps(manage(args.workspace, args.mode), ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError) as exc:
        error = {'status': 'error', 'error': str(exc)}
        if isinstance(getattr(exc, 'receipt', None), dict):
            error['permission_repair'] = exc.receipt
        print(json.dumps(error, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
