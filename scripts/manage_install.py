"""Workspace-only install/upgrade/uninstall with ownership and edit preservation."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import stat
import subprocess
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
BEGIN = '<!-- hmigbot-ios:begin -->'
END = '<!-- hmigbot-ios:end -->'
BLOCK = f'''{BEGIN}
## Native iOS port of HMigBot 1.5.2

Use the bundled a2h-spec -> a2h-plan -> a2h-execute -> a2h-verify -> a2h-retrospect.
Read .migbot/config.json source_platform=ios and ios.source_root. Read
.agents/skills/a2h-spec/references/native-input.md for native source adapters.
Keep the original 1.5.2 baseline templates, file-level source_anchors,
stable F/AC IDs, group/skip accounting, stage gates and findings queue.
Do not require the previous iOS harness, obligation review or typed-v2 mode.
INIT confirms environment/paths/Release context; SPEC confirms product/capability scope.
Preserve existing user scope and authorization. Default to local operation;
telemetry hooks are not installed and uploading is not a prerequisite.
Distinguish generated, compiled and behavior-verified results. Do not fabricate markers.
{END}'''


def checksum(data):
    if isinstance(data, Path):
        with filesystem_path(data).open('rb') as stream:
            return hashlib.file_digest(stream, 'sha256').hexdigest()
    return hashlib.sha256(data).hexdigest()


def put(path, data, mode=None):
    path = filesystem_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(data, Path):
        shutil.copy2(filesystem_path(data), path)
    else:
        path.write_bytes(data)
    if mode is not None:
        path.chmod(mode)


@lru_cache(maxsize=1)
def runtime_modes():
    return json.loads((ROOT / 'docs/macos-runtime-modes.json').read_text(encoding='utf-8'))['files']


def payload_mode(data, name):
    mode = stat.S_IMODE(data.stat().st_mode) if isinstance(data, Path) else 0o644
    if isinstance(data, Path) and data.is_relative_to(ROOT):
        relative = data.relative_to(ROOT).as_posix()
        record = runtime_modes().get(relative)
        if record is not None:
            if checksum(data) != record['sha256']:
                raise ValueError('Bundled runtime hash differs from permission manifest: ' + relative)
            return 0o755 if record['executable'] else 0o644
    path = Path(name)
    if path.suffix in {'.sh', '.bin'} or path.name in {'a2h', 'a2h-tool', 'a2h-bootstrap', 'a2h-agreement'}:
        mode |= 0o111
    return mode


@lru_cache(maxsize=8)
def skill_names(root):
    names = {s.name for s in (root / 'skills').iterdir() if s.is_dir()}
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
    if not relative.startswith(('.hmigbot-ios/', '.agents/hmigbot-runtime/', '.agents/skills/', '.codex/agents/', '.migbot/bin/', '.migbot/policies/')) and relative != '.codex/config.toml':
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


def native_runtime_member(relative, data):
    """Select only current-architecture Mach-O code in this package's payload."""
    if platform.system() != 'Darwin': return False
    architecture=platform.machine().lower()
    if architecture not in {'arm64','aarch64'}:
        raise ValueError('This Mac distribution requires its bundled arm64 stage engines')
    allowed=('/bin/macos-arm64/' in '/'+relative or
             relative in {'.migbot/bin/a2h','.migbot/bin/a2h-darwin-arm64',
                          '.agents/hmigbot-runtime/bin/a2h-darwin-arm64'})
    if not allowed:return False
    if not isinstance(data,Path):return False
    with data.open('rb') as stream: magic=stream.read(4)
    return magic in {b'\xcf\xfa\xed\xfe',b'\xfe\xed\xfa\xcf',b'\xca\xfe\xba\xbe',b'\xbe\xba\xfe\xca'}


def quarantine_present(path):
    result=subprocess.run(['/usr/bin/xattr',str(path)],capture_output=True,timeout=30)
    if result.returncode:raise ValueError('Cannot inspect installed runtime metadata: '+str(path))
    return 'com.apple.quarantine' in result.stdout.decode('utf-8').splitlines()


def prepare_native_execution(workspace, relative, expected):
    path=child(workspace,relative)
    if not native_runtime_member(relative,path):raise ValueError('Outside native runtime allowlist: '+relative)
    if checksum(path)!=expected:raise ValueError('Native runtime hash differs before metadata preparation: '+relative)
    action='not_present'
    if quarantine_present(path):
        # Recheck immediately before the narrowly scoped Apple xattr operation.
        path=child(workspace,relative)
        if checksum(path)!=expected:raise ValueError('Native runtime changed before metadata preparation: '+relative)
        result=subprocess.run(['/usr/bin/xattr','-d','com.apple.quarantine',str(path)],capture_output=True,timeout=30)
        if result.returncode:raise ValueError('Native runtime metadata preparation failed: '+relative)
        action='removed_download_quarantine'
    after=checksum(path)
    if after!=expected:raise ValueError('Native runtime bytes changed during metadata preparation: '+relative)
    return {'path':relative,'action':action,'before_sha256':expected,'after_sha256':after}


def generated_runtime_stage(path):
    """Original SPEC wrappers stage this data beside the binary at run time.

    scripts/coverage-rules.json remains the authoritative distributed asset.
    Do not turn a prior wrapper run into ownership of its private working copy.
    """
    parts = path.relative_to(ROOT).parts
    return (len(parts) == 7 and parts[:4] == ('skills', 'a2h-spec', 'scripts', 'bin')
            and parts[5:] == ('_entry.dist', 'coverage-rules.json'))


def payload():
    files = {}
    for folder in ('.codex-plugin', 'skills', 'scripts', 'src', 'rules', 'schemas', 'providers', 'docs', 'evaluations', 'agents-codex', 'bin', 'policies', 'vendor'):
        for path in (ROOT / folder).rglob('*'):
            if path.is_file() and path.name != '.DS_Store' and not {'__pycache__', '.build', '.swiftpm'}.intersection(path.parts) and path.suffix != '.pyc':
                if path.is_symlink():
                    raise ValueError('Install source contains links')
                if generated_runtime_stage(path):
                    continue
                files['.agents/hmigbot-runtime/' + path.relative_to(ROOT).as_posix()] = path
    for name in ('.gitattributes', '.gitignore', 'README.md', 'CHANGELOG.md', 'pyproject.toml', 'install.ps1', 'install.sh', 'uninstall.ps1', 'uninstall.sh', 'validate.sh'):
        files['.agents/hmigbot-runtime/' + name] = ROOT / name
    for skill in (ROOT / 'skills').iterdir():
        if not skill.is_dir() or not (skill / 'SKILL.md').is_file():
            continue
        for file in skill.rglob('*'):
            if file.is_file() and file.name != '.DS_Store' and '__pycache__' not in file.parts and not generated_runtime_stage(file):
                files['.agents/skills/' + skill.name + '/' + file.relative_to(skill).as_posix()] = file
        files[f'.agents/skills/{skill.name}/runtime.json'] = b'{"runtime_relative":"../../hmigbot-runtime"}\n'
    for role in (ROOT / 'agents-codex').glob('*.toml'):
        files['.codex/agents/' + role.name] = role
    for path in (ROOT / 'bin').iterdir():
        if path.is_file() and path.name != '.DS_Store': files['.migbot/bin/' + path.name] = path
    os_name = {'Windows': 'windows', 'Darwin': 'darwin', 'Linux': 'linux'}.get(platform.system())
    arch = 'arm64' if platform.machine().lower() in {'arm64', 'aarch64'} else 'amd64'
    suffix = '.exe' if os_name == 'windows' else ''
    asset = ROOT / 'bin' / f'a2h-{os_name}-{arch}{suffix}'
    if not asset.is_file(): raise ValueError('Bundled runtime unavailable: ' + asset.name)
    files['.migbot/bin/a2h' + suffix] = asset
    for path in (ROOT / 'policies').glob('*'):
        if path.is_file() and path.name != '.DS_Store': files['.migbot/policies/' + path.name] = path
    return files


def manage(workspace, mode, hmigbot_root=None):
    if mode != "uninstall" and platform.system() != "Darwin":
        raise ValueError("This distribution targets macOS with full Xcode")
    if hmigbot_root is not None:
        raise ValueError('External binding retired; this release bundles HMigBot resources')
    if sys.version_info < (3, 11):
        raise ValueError('HMigBot iOS requires Python 3.11 or newer')
    workspace = filesystem_path(workspace)
    if not workspace.is_dir():
        raise ValueError('Workspace must already exist')
    config_path = workspace / '.migbot/config.json'
    if mode != 'uninstall' and config_path.is_file():
        cfg = json.loads(config_path.read_text(encoding='utf-8-sig'))
        if (cfg.get('source_platform') not in (None, 'ios') or cfg.get('tool_package') not in (None, 'hmigbot-ios152')
            or (not cfg.get('source_platform') and not cfg.get('ios'))):
            raise ValueError('Project belongs to another migration package; install in a separate workspace')
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
    modes = {name: payload_mode(data, name) for name, data in new.items()}
    runtime_names = {name for name, data in new.items()
                     if isinstance(data, Path) and data.is_relative_to(ROOT)
                     and data.relative_to(ROOT).as_posix() in runtime_modes()}
    changes = {name for name in new if not child(workspace, name).is_file() or checksum(child(workspace, name)) != hashes[name]
               or (name in runtime_names and bool(child(workspace, name).stat().st_mode & 0o111) != bool(modes[name] & 0o111))}
    native={name:hashes[name] for name,data in new.items() if native_runtime_member(name,data)}
    if '.migbot/bin/a2h' not in native or '.agents/skills/a2h-spec/scripts/bin/macos-arm64/_entry.dist/_entry.bin' not in native:
        raise ValueError('Current-architecture native runtime is missing from package manifest')
    for name in native:
        path=child(workspace,name)
        if path.is_file() and name not in changes and quarantine_present(path):
            changes.add(name)  # Back up and restage this owned, verified file transactionally.
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
    try:
        for name in changes:
            put(child(workspace, name), new[name], modes[name])
            if checksum(child(workspace,name))!=hashes[name]:
                raise ValueError('Installed payload hash mismatch: '+name)
            if stat.S_IMODE(child(workspace,name).stat().st_mode)!=modes[name]:
                raise ValueError('Installed payload mode mismatch: '+name)
        native_preparation=[prepare_native_execution(workspace,name,expected) for name,expected in sorted(native.items())]
        for name in set(owned) - set(new):
            child(workspace, name).unlink(missing_ok=True)
        agent_path.write_bytes(updated_agents.encode('utf-8'))
        manifest = {'schema_version': 1, 'owner': 'hmigbot-ios', 'version': json.loads((ROOT / '.codex-plugin/plugin.json').read_text(encoding='utf-8'))['version'],
                    'files': hashes, 'agent_block': BLOCK,
                    'agent_original_base64': old.get('agent_original_base64') if old else (base64.b64encode(agent_bytes).decode() if agent_bytes is not None else None),
                    'agent_installed_sha256': checksum(agent_path.read_bytes())}
        manifest['native_runtime_allowlist_sha256']=checksum(json.dumps(native,sort_keys=True).encode('utf-8'))
        manifest['file_modes'] = {name: modes[name] for name in runtime_names}
        manifest['native_runtime_architecture']=platform.machine()
        manifest['native_execution_preparation']=native_preparation
        metadata.parent.mkdir(parents=True, exist_ok=True)
        metadata.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    except Exception:
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
            'version': manifest['version']}


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
        print(json.dumps({'status': 'error', 'error': str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
