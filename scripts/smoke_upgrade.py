"""Real old-to-new workspace upgrade, including refusal of edited managed files."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


def hashes(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--old', required=True, type=Path)
    parser.add_argument('--new', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    report = {'status': 'failed', 'scope': 'Tool installation only; synthetic project preservation', 'checks': []}
    env = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1', 'PYTHON': sys.executable}
    def run(name, plugin, workspace, expected=0):
        process = subprocess.run([sys.executable, str(plugin.resolve() / 'scripts/manage_install.py'),
                                  'install', '--workspace', str(workspace)],
                                 capture_output=True, env=env, timeout=300, shell=False)
        (output / (name + '.stdout.log')).write_bytes(process.stdout)
        (output / (name + '.stderr.log')).write_bytes(process.stderr)
        report['checks'].append({'name': name, 'exit_code': process.returncode,
                                 'expected_exit': expected, 'passed': process.returncode == expected})
        if process.returncode != expected:
            raise RuntimeError(name + ': ' + process.stderr.decode('utf-8', errors='replace'))
        return process
    try:
        with tempfile.TemporaryDirectory(prefix='hmigbot upgrade 中文 ') as temporary:
            workspace = Path(temporary).resolve()
            preserved = {'AGENTS.md': b'# User instructions\r\n',
                         '.migbot/config.json': b'{"user":"configuration"}\n',
                         'spec/state/state.json': b'{"user":"existing synthetic ledger"}\n',
                         'entry/Main.ets': b'// synthetic user application\n'}
            for relative, content in preserved.items():
                path = workspace / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(content)
            run('old-install', args.old, workspace)
            manifest_path = workspace / '.hmigbot-ios/install.json'
            report['old_version'] = json.loads(manifest_path.read_text())['version']
            managed = workspace / '.hmigbot-ios/plugin/src/hmigbot_ios/__init__.py'
            original = managed.read_bytes()
            managed.write_bytes(original + b'\n# User local edit\n')
            before = hashes(workspace)
            refused = run('edited-upgrade-refused', args.new, workspace, expected=2)
            if b'user-edited managed file' not in refused.stderr or hashes(workspace) != before:
                raise RuntimeError('Edited upgrade must refuse before changing any workspace bytes')
            managed.write_bytes(original)
            run('old-to-new-upgrade', args.new, workspace)
            manifest = json.loads(manifest_path.read_text())
            report['new_version'] = manifest['version']
            expected_version = json.loads((args.new / '.codex-plugin/plugin.json').read_text())['version']
            if report['new_version'] != expected_version:
                raise RuntimeError('Upgrade did not install the new version')
            actual = hashes(workspace)
            if any(actual.get(p) != value for p, value in manifest['files'].items()):
                raise RuntimeError('Installed upgrade differs from its manifest')
            for relative, content in preserved.items():
                actual_bytes = (workspace / relative).read_bytes()
                if relative == 'AGENTS.md':
                    if not actual_bytes.startswith(content):
                        raise RuntimeError('User AGENTS prefix changed')
                elif actual_bytes != content:
                    raise RuntimeError('User file changed: ' + relative)
            report['checks'].append({'name': 'all-upgraded-files-hashed-and-user-files-preserved',
                                     'files': len(manifest['files']), 'passed': True})
            report['status'] = 'passed'
    except (OSError, ValueError, KeyError, RuntimeError, subprocess.TimeoutExpired) as exc:
        report['error'] = str(exc)
    (output / 'upgrade-checks.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report['status'] == 'passed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
