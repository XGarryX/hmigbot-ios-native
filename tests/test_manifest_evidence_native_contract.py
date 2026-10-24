"""SwiftPM evaluation evidence is replayed, source-bound and fail closed."""
import copy
import importlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from hmigbot_ios.core import MigrationError, digest, json_bytes, read_json, snapshot, write_json


class ManifestEvidenceTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='swiftpm-evidence-')
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.source = self.root / 'ios'
        self.source.mkdir()
        (self.source / 'Package.swift').write_text('// swift-tools-version: 6.0\nimport PackageDescription\n')
        (self.source / 'App.swift').write_text('struct App {}\n')
        self.config = self.root / 'config.json'
        self.output = self.root / 'evidence'
        self.raw = {'name': 'Example', 'targets': [{'name': 'Example', 'type': 'regular',
                    'dependencies': [], 'path': 'Sources/Example'}], 'dependencies': []}
        self.settings = {'schema_version': 1, 'manifests': [{'path': 'Package.swift',
            'command': ['swift', 'package', '--package-path', '{package_dir}', 'dump-package'],
            'version_command': ['swift', '--version'], 'timeout_seconds': 30}]}
        write_json(self.config, self.settings)

    def module(self):
        self.assertIsNotNone(importlib.util.find_spec('hmigbot_ios.manifest_evidence'),
            'Missing SwiftPM manifest evaluation evidence capability')
        return importlib.import_module('hmigbot_ios.manifest_evidence')

    def good_run(self, command, **kwargs):
        value = b'Swift version 6.0.3 (swift-6.0.3-RELEASE)\nTarget: x86_64-unknown-linux-gnu\n' if '--version' in command else json_bytes(self.raw)
        return subprocess.CompletedProcess(command, 0, value, b'')

    def capture(self, runner=None):
        module = self.module()
        # Python's Windows host probe may itself use subprocess on first access.
        # Complete that real probe before mocking only the SwiftPM invocations.
        module.platform.uname()
        with patch.object(module.subprocess, 'run', side_effect=runner or self.good_run) as run:
            result = module.capture(self.source, self.config, self.output)
        return result, run

    def test_capture_real_process_results_and_validate_current_source(self):
        module = self.module()
        report, run = self.capture()
        self.assertEqual(report['status'], 'captured')
        self.assertEqual(run.call_count, 2)
        for call in run.call_args_list:
            self.assertFalse(call.kwargs['shell'])
            self.assertEqual(call.kwargs['cwd'], self.source.resolve())
        checked = module.validate(self.source, self.output)
        self.assertTrue(checked['integrity_passed'])
        item = checked['manifests'][0]
        self.assertEqual(item['path'], 'Package.swift')
        self.assertEqual(item['name'], self.raw['name'])
        self.assertEqual(item['targets'], self.raw['targets'])
        self.assertEqual(item['dependencies'], [])
        self.assertEqual(item['manifest_sha256'], digest((self.source / 'Package.swift').read_bytes()))
        self.assertEqual(item['source_sha256'], snapshot(self.source)['sha256'])
        self.assertEqual(item['status'], 'manifest_evaluated')
        self.assertEqual(item['scope'], 'current_host_manifest_evaluation')
        self.assertIn('Swift version 6.0.3', item['version_output'])
        self.assertTrue(item['host']['system'])
        self.assertEqual(checked['dependency_resolution'], 'not_verified')
        self.assertEqual(checked['behavior_equivalence'], 'not_verified')
        self.assertEqual(checked['capture_authenticity'], 'not_verified')
        self.assertEqual(json.loads((self.output / item['evaluation_artifact']).read_text()), self.raw)
        self.assertEqual(module.validate(self.source, self.output / 'manifest.json'), checked)

    def test_empty_targets_is_valid_manifest_not_resolved_dependency_graph(self):
        self.raw = {'name': 'Empty', 'targets': [], 'dependencies': [{'fileSystem': [{'path': '../Other', 'identity': 'other'}]}]}
        self.capture()
        item = self.module().validate(self.source, self.output)['manifests'][0]
        self.assertEqual(item['targets'], [])
        self.assertEqual(item['dependencies'], self.raw['dependencies'])

    def test_nested_manifest_only_covers_explicit_path_and_expands_argv(self):
        nested = self.source / 'Packages/Library'
        nested.mkdir(parents=True)
        (nested / 'Package.swift').write_text('// swift-tools-version: 6.0\n')
        self.settings['manifests'][0].update(path='Packages/Library/Package.swift',
            command=['swift', 'package', '--package-path', '{package_dir}', 'dump-package'],
            version_command=['swift', '--version'], conditions='Explicit local package')
        write_json(self.config, self.settings)
        self.capture()
        item = self.module().validate(self.source, self.output)['manifests'][0]
        self.assertEqual(item['path'], 'Packages/Library/Package.swift')
        self.assertIn(str(nested.resolve()), item['command'])
        self.assertEqual(item['conditions'], 'Explicit local package')

    def test_invalid_json_or_missing_swiftpm_fields_is_preserved_and_rejected(self):
        for value in (b'not JSON', b'[]', b'{"name":"A","targets":[]}',
                      b'{"name":"A","targets":null,"dependencies":[]}',
                      b'{"name":"A","targets":[{}],"dependencies":[]}',
                      b'{"name":"A","targets":[],"dependencies":["guess"]}',
                      b'{"name":"A","name":"B","targets":[],"dependencies":[]}'):
            with self.subTest(value=value):
                self.output = self.root / ('bad-' + digest(value)[:12])
                def runner(command, **kwargs):
                    return self.good_run(command, **kwargs) if '--version' in command else subprocess.CompletedProcess(command, 0, value, b'diagnostics')
                report, _ = self.capture(runner)
                self.assertEqual(report['status'], 'capture_failed')
                self.assertTrue((self.output / 'manifest.json').is_file())
                self.assertIn(value, [p.read_bytes() for p in (self.output / 'artifacts').rglob('*') if p.is_file()])
                with self.assertRaises(MigrationError):
                    self.module().validate(self.source, self.output)

    def test_failed_or_empty_version_does_not_execute_evaluation(self):
        for code, stdout in ((4, b'Swift'), (0, b'  ')):
            with self.subTest(code=code, stdout=stdout):
                self.output = self.root / ('version-' + str(code))
                report, run = self.capture(lambda cmd, **kw: subprocess.CompletedProcess(cmd, code, stdout, b'version error'))
                self.assertEqual(report['status'], 'capture_failed')
                self.assertEqual(run.call_count, 1)
                with self.assertRaises(MigrationError):
                    self.module().validate(self.source, self.output)

    def test_command_failure_timeout_and_missing_executable_are_retained(self):
        for mode in ('failure', 'timeout', 'missing'):
            with self.subTest(mode=mode):
                self.output = self.root / mode
                def runner(command, **kwargs):
                    if '--version' in command:
                        return self.good_run(command, **kwargs)
                    if mode == 'timeout':
                        raise subprocess.TimeoutExpired(command, 30, output=b'partial stdout', stderr=b'partial stderr')
                    if mode == 'missing':
                        raise FileNotFoundError('swift unavailable')
                    return subprocess.CompletedProcess(command, 8, b'failed stdout', b'bad manifest')
                report, _ = self.capture(runner)
                self.assertEqual(report['status'], 'capture_failed')
                self.assertTrue(report['failures'])
                self.assertTrue((self.output / 'manifest.json').exists())
                with self.assertRaises(MigrationError):
                    self.module().validate(self.source, self.output)

    def test_source_mutation_during_capture_is_failed_with_before_after_hashes(self):
        def runner(command, **kwargs):
            if '--version' not in command:
                (self.source / 'App.swift').write_text('struct Changed {}\n')
            return self.good_run(command, **kwargs)
        report, _ = self.capture(runner)
        self.assertEqual(report['status'], 'capture_failed')
        self.assertTrue(report['source_changed'])
        self.assertNotEqual(report['source_sha256'], report['source_after_sha256'])
        with self.assertRaises(MigrationError):
            self.module().validate(self.source, self.output)

    def test_source_or_manifest_staleness_is_rejected(self):
        self.capture()
        for path in ('App.swift', 'Package.swift'):
            file = self.source / path
            original = file.read_bytes()
            file.write_bytes(original + b'// changed\n')
            with self.assertRaises(MigrationError):
                self.module().validate(self.source, self.output)
            file.write_bytes(original)

    def test_derived_names_targets_dependencies_and_status_cannot_override_raw_stdout(self):
        self.capture()
        file = self.output / 'manifest.json'
        original = read_json(file)
        for field, value in (('name', 'Forged'), ('targets', []),
                             ('dependencies', [{'forged': True}]), ('status', 'resolved')):
            with self.subTest(field=field):
                changed = copy.deepcopy(original)
                changed['manifests'][0][field] = value
                write_json(file, changed)
                with self.assertRaises(MigrationError):
                    self.module().validate(self.source, self.output)
        write_json(file, original)

    def test_changed_missing_or_escaping_artifacts_are_rejected(self):
        report, _ = self.capture()
        file = self.output / 'manifest.json'
        item = report['manifests'][0]
        artifact = self.output / item['evaluation_artifact']
        raw = artifact.read_bytes()
        artifact.write_bytes(b'changed')
        with self.assertRaises(MigrationError):
            self.module().validate(self.source, self.output)
        artifact.unlink()
        with self.assertRaises(MigrationError):
            self.module().validate(self.source, self.output)
        artifact.write_bytes(raw)
        changed = copy.deepcopy(report)
        changed['artifacts']['../escape'] = digest(b'x')
        write_json(file, changed)
        with self.assertRaises(MigrationError):
            self.module().validate(self.source, self.output)

    def test_refingerprinted_invalid_raw_output_does_not_pass_replay(self):
        report, _ = self.capture()
        relative = report['manifests'][0]['evaluation_artifact']
        raw = b'{"name":"Example","targets":[]}'
        (self.output / relative).write_bytes(raw)
        report['artifacts'][relative] = digest(raw)
        write_json(self.output / 'manifest.json', report)
        with self.assertRaises(MigrationError):
            self.module().validate(self.source, self.output)

    def test_command_records_cannot_be_overridden_by_summary_metadata(self):
        report, _ = self.capture()
        report['manifests'][0]['command'] = ['swift', 'package', 'dump-package', '--fake']
        write_json(self.output / 'manifest.json', report)
        with self.assertRaises(MigrationError):
            self.module().validate(self.source, self.output)

    def test_invalid_manifest_config_is_failed_with_no_process_execution(self):
        cases = [
            {'schema_version': 9, 'manifests': self.settings['manifests']},
            {'schema_version': 1, 'manifests': []},
            {'schema_version': 1, 'manifests': self.settings['manifests'] * 2},
        ]
        for changes in ({'path': '../Package.swift'}, {'path': 'Podfile'}, {'path': 'Missing/Package.swift'},
                        {'command': 'swift package dump-package'}, {'command': ['echo', 'hello']},
                        {'version_command': []}, {'timeout_seconds': 0}, {'timeout_seconds': True}):
            item = {**self.settings['manifests'][0], **changes}
            cases.append({'schema_version': 1, 'manifests': [item]})
        for i, config in enumerate(cases):
            with self.subTest(config=config):
                self.output = self.root / ('config-' + str(i))
                write_json(self.config, config)
                report, run = self.capture()
                self.assertEqual(report['status'], 'capture_failed')
                self.assertEqual(run.call_count, 0)
                self.assertTrue((self.output / 'manifest.json').exists())

    def test_capture_rejects_source_overlap_and_existing_nonempty_output(self):
        module = self.module()
        for output in (self.source, self.source / 'evidence', self.root):
            with self.assertRaises(MigrationError):
                module.capture(self.source, self.config, output)
        self.output.mkdir()
        marker = self.output / 'keep.txt'
        marker.write_text('keep')
        with self.assertRaises(MigrationError):
            module.capture(self.source, self.config, self.output)
        self.assertEqual(marker.read_text(), 'keep')

    def test_duplicate_manifest_in_evidence_is_rejected(self):
        report, _ = self.capture()
        report['manifests'].append(copy.deepcopy(report['manifests'][0]))
        write_json(self.output / 'manifest.json', report)
        with self.assertRaises(MigrationError):
            self.module().validate(self.source, self.output)

    def test_version_timeout_preserves_partial_logs_and_skips_evaluation(self):
        def runner(command, **kwargs):
            raise subprocess.TimeoutExpired(command, 30, output=b'partial version', stderr=b'startup stalled')
        report, run = self.capture(runner)
        self.assertEqual(report['status'], 'capture_failed')
        self.assertEqual(run.call_count, 1)
        self.assertEqual((self.output / 'artifacts/manifest-0000/version.stdout.log').read_bytes(), b'partial version')
        record = read_json(self.output / report['manifests'][0]['version_record'])
        self.assertTrue(record['timed_out'])
        self.assertIsNone(record['exit_code'])

    def test_multiple_manifests_keep_individual_command_evidence_on_failure(self):
        nested = self.source / 'Nested'
        nested.mkdir()
        (nested / 'Package.swift').write_text('// swift-tools-version: 6.0\n')
        self.settings['manifests'].append({**self.settings['manifests'][0], 'path': 'Nested/Package.swift'})
        write_json(self.config, self.settings)
        def runner(command, **kwargs):
            if str(nested.resolve()) in command:
                return subprocess.CompletedProcess(command, 7, b'', b'nested manifest invalid')
            return self.good_run(command, **kwargs)
        report, run = self.capture(runner)
        self.assertEqual(run.call_count, 4)
        self.assertEqual(report['status'], 'capture_failed')
        self.assertEqual([item['status'] for item in report['manifests']], ['manifest_evaluated', 'capture_failed'])
        self.assertEqual(read_json(self.output / report['manifests'][1]['evaluation_record'])['exit_code'], 7)
        with self.assertRaises(MigrationError):
            self.module().validate(self.source, self.output)

    def test_failure_status_cannot_be_promoted_when_raw_exit_code_is_nonzero(self):
        def runner(command, **kwargs):
            if '--version' in command:
                return self.good_run(command, **kwargs)
            return subprocess.CompletedProcess(command, 9, json_bytes(self.raw), b'compiler rejected manifest')
        report, _ = self.capture(runner)
        report.update(status='captured', failures=[])
        report['manifests'][0].update(status='manifest_evaluated', **self.raw)
        write_json(self.output / 'manifest.json', report)
        with self.assertRaises(MigrationError):
            self.module().validate(self.source, self.output)

    def test_configuration_rejects_unknown_fields_instead_of_ignoring_typo(self):
        self.settings['manifests'][0]['target_configuration'] = 'Release'
        write_json(self.config, self.settings)
        report, run = self.capture()
        self.assertEqual(report['status'], 'capture_failed')
        self.assertEqual(run.call_count, 0)

    def test_same_named_manifests_cannot_cross_bind_package_path(self):
        for name in ('A', 'B'):
            package = self.source / name
            package.mkdir()
            (package / 'Package.swift').write_text('// swift-tools-version: 6.0\n// ' + name)
        # Both commands can return the same package name/targets. The input path,
        # not the package name, determines which source obligation is discharged.
        self.settings['manifests'][0].update(path='A/Package.swift',
            command=['swift', 'package', '--package-path', str(self.source / 'B'), 'dump-package'])
        write_json(self.config, self.settings)
        report, run = self.capture()
        self.assertEqual(report['status'], 'capture_failed')
        self.assertEqual(run.call_count, 0)

    def test_package_path_must_be_explicit_unique_and_local(self):
        for index, command in enumerate((
                ['swift', 'package', 'dump-package'],
                ['swift', 'package', '--package-path', '{package_dir}', '--package-path', '{package_dir}', 'dump-package'],
                ['swift', 'package', '--package-path', '{package_dir}', '--package-path=/other', 'dump-package'],
                ['swift', 'package', '--package-path', 'dump-package'],
                ['wsl', '--', 'swift', 'package', '--package-path', '/home/remote-copy', 'dump-package'])):
            with self.subTest(command=command):
                self.output = self.root / ('binding-' + str(index))
                self.settings['manifests'][0]['command'] = command
                write_json(self.config, self.settings)
                report, run = self.capture()
                self.assertEqual(report['status'], 'capture_failed')
                self.assertEqual(run.call_count, 0)

    def test_swiftpm_reported_root_must_match_the_configured_manifest(self):
        self.raw['packageKind'] = {'root': [str(self.source / 'Other')]}
        report, _ = self.capture()
        self.assertEqual(report['status'], 'capture_failed')
        self.assertTrue(report['failures'])

    @unittest.skipUnless(sys.platform == 'win32', 'WSL drive mapping applies to a Windows source root')
    def test_wsl_drive_path_binds_to_the_same_windows_source(self):
        wsl_source = '/mnt/' + self.source.drive[0].lower() + self.source.as_posix()[2:]
        self.settings['manifests'][0].update(
            command=['wsl', '--', 'env', 'SWIFTPM_CUSTOM_LIBS_DIR=/opt/swift/lib', 'swift', 'package',
                     '--package-path', wsl_source, 'dump-package'],
            version_command=['wsl', '--', 'swift', '--version'])
        self.raw['packageKind'] = {'root': [wsl_source]}
        write_json(self.config, self.settings)
        self.capture()
        self.assertEqual(self.module().validate(self.source, self.output)['manifests'][0]['path'], 'Package.swift')

    def test_equal_style_package_path_is_unambiguous_and_bound(self):
        self.settings['manifests'][0]['command'] = ['swift', 'package', '--package-path={package_dir}', 'dump-package']
        write_json(self.config, self.settings)
        self.capture()
        self.assertEqual(self.module().validate(self.source, self.output)['manifests'][0]['name'], 'Example')

    def test_arbitrary_nonempty_tool_version_is_rejected(self):
        def runner(command, **kwargs):
            if '--version' in command:
                return subprocess.CompletedProcess(command, 0, b'Python 3.13.1\n', b'')
            return self.good_run(command, **kwargs)
        report, run = self.capture(runner)
        self.assertEqual(report['status'], 'capture_failed')
        self.assertEqual(run.call_count, 1)

    def test_refingerprinted_non_swift_version_is_rejected_during_replay(self):
        report, _ = self.capture()
        record = read_json(self.output / report['manifests'][0]['version_record'])
        raw = b'Python 3.13.1\n'
        (self.output / record['stdout']).write_bytes(raw)
        report['artifacts'][record['stdout']] = digest(raw)
        report['manifests'][0]['version_output'] = raw.decode().strip()
        write_json(self.output / 'manifest.json', report)
        with self.assertRaises(MigrationError):
            self.module().validate(self.source, self.output)


if __name__ == '__main__':
    unittest.main()
