"""Install an extracted ZIP and run original consumers using only installed resources."""
import argparse
import hashlib
import json
import os
import platform
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile
from manage_install import filesystem_path
from package_tree import verify_package


def sha(path):
    with filesystem_path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit('Use a new validation report path')
    package = args.package.resolve()
    package_report = verify_package(package)
    if package_report['status'] != 'passed':
        raise SystemExit('Package source manifest verification failed')
    checksum = sha(package)
    if checksum != package.with_suffix(package.suffix + '.sha256').read_text().split()[0]:
        raise SystemExit('Package checksum mismatch')
    report = {'package': package.name, 'sha256': checksum, 'status': 'failed', 'checks': [{'name': 'archive-source-manifest', 'passed': True,
                  'files': package_report['files'], 'directories': package_report['directories']}],
              'platform': platform.platform(), 'architecture': platform.machine(),
              'scope': 'Standalone installation, original consumers and installed iOS harness adversarial/four-beat contracts on this host; no device behavior acceptance'}
    evidence = args.output.resolve().parent / (args.output.stem + '-evidence')
    if evidence.exists(): raise SystemExit('Evidence directory already exists')
    evidence.mkdir(parents=True)
    try:
        with tempfile.TemporaryDirectory(prefix='hmigbot standalone 发行包 ') as tmp:
            root = Path(tmp).resolve()
            with zipfile.ZipFile(package) as archive:
                for info in archive.infolist():
                    path = (root / info.filename).resolve()
                    if not path.is_relative_to(root) or '\\' in info.filename or ':' in info.filename or (info.external_attr >> 16) & 0o170000 == 0o120000:
                        raise RuntimeError('Unsafe ZIP path or link')
                if archive.testzip(): raise RuntimeError('Package CRC failure')
                archive.extractall(root)
            plugin = root / package_report['source_root_name']
            workspace = root / '安装 workspace'
            workspace.mkdir()
            original = b'# User rules\r\nPreserve these exact bytes.\r\n'
            (workspace / 'AGENTS.md').write_bytes(original)
            env = {**os.environ, 'PYTHONUTF8': '1', 'PYTHON': sys.executable, 'A2H_TELEMETRY_OFF': '1'}

            def execute(name, command, cwd=root, timeout=300):
                try:
                    result = subprocess.run(command, cwd=cwd, env=env, capture_output=True, timeout=timeout, shell=False)
                except subprocess.TimeoutExpired as exc:
                    (evidence / (name + '.stdout.log')).write_bytes(exc.stdout or b'')
                    (evidence / (name + '.stderr.log')).write_bytes(exc.stderr or b'')
                    report['checks'].append({'name': name, 'passed': False, 'timed_out': True, 'timeout_seconds': timeout})
                    raise RuntimeError(name + ': timed out; partial diagnostics retained') from exc
                (evidence / (name + '.stdout.log')).write_bytes(result.stdout)
                (evidence / (name + '.stderr.log')).write_bytes(result.stderr)
                report['checks'].append({'name': name, 'exit_code': result.returncode, 'passed': result.returncode == 0})
                if result.returncode:
                    raise RuntimeError(name + ': ' + result.stderr.decode('utf-8', errors='replace'))
                return result

            def wrapper(mode, base):
                if os.name == 'nt':
                    return ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', str(base / (mode + '.ps1')),
                            '-Workspace', str(workspace), '-Python', sys.executable]
                return ['/bin/sh', str(base / (mode + '.sh')), str(workspace)]

            installed = json.loads(execute('platform-install', wrapper('install', plugin)).stdout)
            if installed.get('skills') != 96 or installed.get('agents') != 29 or installed.get('hmigbot') != 'bundled':
                raise RuntimeError('Incomplete installed skill/role resources')
            runtime = workspace / '.hmigbot-ios/plugin'
            manifest = json.loads((workspace / '.hmigbot-ios/install.json').read_text(encoding='utf-8'))
            for relative, expected in manifest['files'].items():
                if sha(workspace / relative) != expected:
                    raise RuntimeError('Installed file differs from manifest: ' + relative)
            if (workspace / '.hmigbot-ios/hmigbot-binding.json').exists():
                raise RuntimeError('External HMigBot binding unexpectedly required')
            report['checks'].append({'name': 'all-installed-resources-hashed', 'passed': True, 'files': len(manifest['files'])})
            # Source assets are fixture data only. Every consumer below comes from the installed runtime.
            fixtures = plugin / 'tests/fixtures'
            execute('installed-native-pipeline', [sys.executable, '-X', 'utf8', str(runtime / 'scripts/validate_native_pipeline.py'),
                    '--fixtures', str(fixtures), '--output', str(evidence / 'native-pipeline')])
            execute('installed-upstream-audit', [sys.executable, '-X', 'utf8', str(runtime / 'scripts/audit_upstream.py')])
            execute('installed-scheduler-audit', [sys.executable, '-X', 'utf8', str(runtime / 'scripts/audit_scheduler.py')])
            execute('installed-expertise-audit', [sys.executable, '-X', 'utf8', str(runtime / 'scripts/a2h_ios.py'), 'expertise-audit'])
            execute('installed-native-surface', [sys.executable, '-X', 'utf8', str(runtime / 'scripts/audit_native_surface.py')])
            env['HMIGBOT_TEST_RUNTIME'] = str(runtime)
            env['PYTHONPATH'] = str(runtime / 'src') + os.pathsep + str(plugin / 'tests')
            execute('installed-ios-harness', [sys.executable, '-X', 'utf8', '-m', 'unittest', 'discover',
                    '-s', str(plugin / 'tests'), '-p', 'test_ios_harness.py', '-v'])
            execute('installed-spec-contract', [sys.executable, '-X', 'utf8', '-m', 'unittest', 'discover',
                    '-s', str(plugin / 'tests'), '-p', 'test_spec_contract.py', '-v'])
            for pattern in ('test_artifact_contract.py', 'test_plan_contract.py', 'test_quality_views.py',
                            'test_markdown_gates.py', 'test_freeze_contract.py', 'test_raw_strings.py',
                            'test_spec_upgrade.py', 'test_spec_upgrade_cli.py', 'test_page_evidence.py',
                            'test_evidence_review.py', 'test_xcode_snapshot.py', 'test_native_authoring.py',
                            'test_gate_artifacts.py', 'test_conditional_evidence.py',
                            'test_ios_harness_diagnostics.py', 'test_xcode_direct_provider.py',
                            'test_scheduler_failure_receipts.py', 'test_native_pipeline_runtime.py', 'test_portable_helper.py', 'test_resource_preview_routing.py', 'test_package_tree.py'):
                execute('installed-' + pattern.removesuffix('.py'), [sys.executable, '-X', 'utf8', '-m', 'unittest', 'discover',
                        '-s', str(plugin / 'tests'), '-p', pattern, '-v'])
            execute('installed-expertise-mcp', [sys.executable, '-X', 'utf8', '-m', 'unittest', 'discover',
                    '-s', str(plugin / 'tests'), '-p', 'test_expertise_mcp.py', '-v'])
            for name in (
                         'test_source_responsibility.py', 'test_responsibility_consumers.py',
                         'test_source_responsibility_consumers.py', 'test_source_resource_coordinates.py',
                         'test_gate_artifact_projection.py', 'test_contract_root_aliases.py',
                         'test_macos_permissions.py', 'test_upgrade_cleanup.py',
                         'test_upgrade_install_integration.py', 'test_permissions_cli.py', 'test_objc_state_facts.py', 'test_objc_state_contract.py',
                         'test_source_analysis.py', 'test_auto_orchestration.py'):
                execute('installed-' + name.removesuffix('.py'),
                        [sys.executable, '-X', 'utf8', '-m', 'pytest', '-q', '-p', 'no:cacheprovider', str(plugin / 'tests' / name)],
                        timeout=900)
            del env['HMIGBOT_TEST_RUNTIME']
            del env['PYTHONPATH']
            fixture_project = evidence / 'native-pipeline/harmony'
            native = workspace / '.migbot/bin' / ('a2h.exe' if os.name == 'nt' else 'a2h')
            execute('offline-runtime-init', [str(native), 'init-run', '--consent', 'denied'], cwd=fixture_project)
            execute('offline-stage-marker', [str(native), 'mark-stage', 'a2h-retrospect'], cwd=fixture_project)
            if not list((fixture_project / '.migbot/metrics').glob('*/retrospect.done')):
                raise RuntimeError('Original runtime did not produce the stage sentinel')
            # Hide the extracted original before upgrading from the installed copy.
            plugin.rename(root / 'extracted-source-hidden')
            execute('self-contained-upgrade', wrapper('install', runtime))
            execute('self-contained-uninstall', wrapper('uninstall', runtime))
            if (workspace / 'AGENTS.md').read_bytes() != original or (workspace / '.agents/skills/a2h-run/SKILL.md').exists():
                raise RuntimeError('Uninstall did not preserve ownership boundaries')
            report['checks'].append({'name': 'restored-original-agents', 'passed': True})
            report['status'] = 'passed'
    except (OSError, ValueError, KeyError, RuntimeError, subprocess.TimeoutExpired, zipfile.BadZipFile) as exc:
        report['error'] = str(exc)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report['status'] == 'passed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
