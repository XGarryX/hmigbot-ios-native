"""Public source evidence must be consumed and replayed by the real facts CLI."""
import contextlib
import inspect
import io
import json
import os
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(os.environ.get('HMIGBOT_TEST_RUNTIME', Path(__file__).resolve().parents[1])).resolve()
sys.path.insert(0, str(ROOT / 'src'))

from hmigbot_ios.core import MigrationError, digest, json_bytes, read_json, write_json
from hmigbot_ios.ios_facts import extract, refresh, validate_graph
from hmigbot_ios.native_pipeline import configure, main


class SourceInputIntegrationTests(unittest.TestCase):
    def test_raw_manifest_capture_is_pinned_for_domain_consumers(self):
        from hmigbot_ios.ios_scheduler import baseline_inputs
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            write_json(project / '.migbot/config.json', {'ios_harness': {'spec_contract_version': 2}})
            (project / 'spec/baseline').mkdir(parents=True)
            # This probe has no product rows, but it still declares a valid
            # profile-2 catalog table so dependency pinning need not accept a
            # malformed index merely to exercise raw source evidence.
            (project / 'spec/baseline/feature-index.md').write_text(
                '# No product features in this evidence pinning fixture\n## 功能清单\n'
                '| ID | 功能 | 优先级 | 排序依赖 | 契约依赖 | 关联页面 | 创建页面 | complexity | tier | depth | 状态 | spec |\n'
                '|---|---|---|---|---|---|---|---|---|---|---|---|\n', encoding='utf-8')
            bundle = project / 'spec/ref/ios-manifest-evidence/capture-001'
            (bundle / 'artifacts').mkdir(parents=True)
            (bundle / 'manifest.json').write_text('{}', encoding='utf-8')
            (bundle / 'artifacts/evaluation.stdout.log').write_text('{"name":"Offline"}', encoding='utf-8')
            inputs = baseline_inputs(project, 'domains')
            self.assertIn('spec/ref/ios-manifest-evidence/capture-001/manifest.json', inputs)
            self.assertIn('spec/ref/ios-manifest-evidence/capture-001/artifacts/evaluation.stdout.log', inputs)

    def test_refresh_and_replay_reject_changed_raw_manifest_output(self):
        from hmigbot_ios.manifest_evidence import capture
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, project = root / 'source', root / 'project'
            source.mkdir(); project.mkdir()
            (source / 'Package.swift').write_text('// swift-tools-version: 5.9\nimport PackageDescription\nlet package = Package(name: "Offline")\n', encoding='utf-8')
            configure(source, project)
            config = root / 'capture.json'
            write_json(config, {'schema_version': 1, 'manifests': [{'path': 'Package.swift',
                'command': ['swift', 'package', '--package-path', str(source), 'dump-package'],
                'version_command': ['swift', '--version']}]})
            bundle = project / 'spec/ref/ios-manifest-evidence/capture-001'
            results = [SimpleNamespace(returncode=0, stdout=b'Swift version 6.0.3\n', stderr=b''),
                       SimpleNamespace(returncode=0, stdout=json_bytes({'name': 'Offline', 'targets': [], 'dependencies': []}), stderr=b'')]
            import platform
            platform.uname()  # Avoid mocking a first-use host probe on Python 3.14.
            with patch('hmigbot_ios.manifest_evidence.subprocess.run', side_effect=results):
                captured = capture(source, config, bundle)
            self.assertEqual(captured['status'], 'captured')
            graph = refresh(project, source, manifest_evidence=bundle)
            self.assertEqual(validate_graph(source, project)[0], graph)
            artifact = bundle / captured['manifests'][0]['evaluation_artifact']
            artifact.write_text('{"name":"A different package","targets":[],"dependencies":[]}', encoding='utf-8')
            with self.assertRaises(MigrationError):
                validate_graph(source, project)

    def test_cli_exposes_real_manifest_capture(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output), self.assertRaises(SystemExit) as exit_:
            main(['--help'])
        self.assertEqual(exit_.exception.code, 0)
        self.assertIn('manifest-evaluate', output.getvalue(), 'The CLI cannot obtain manifest evaluation evidence')

    def test_facts_accepts_bound_manifest_evidence(self):
        self.assertIn('manifest_evidence', inspect.signature(extract).parameters,
                      'Facts have no input for actual manifest evaluation, so a valid Package.swift remains unresolved')
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'source'
            source.mkdir()
            (source / 'Package.swift').write_text('// swift-tools-version: 5.9\nimport PackageDescription\nlet package = Package(name: "Offline")\n', encoding='utf-8')
            plain = extract(source)
            self.assertTrue(any(i.get('code') == 'executable_manifest_not_evaluated' for i in plain['issues']))
            manifest = source / 'Package.swift'
            evidence = Path(directory) / 'capture'
            evidence.mkdir()
            (evidence / 'manifest.json').write_text('{}', encoding='utf-8')
            result = {'schema_version': 1, 'integrity_passed': True, 'source_sha256': plain['source_sha256'],
                      'manifests': [{'path': 'Package.swift', 'name': 'Offline', 'targets': [], 'dependencies': [],
                                     'manifest_sha256': digest(manifest.read_bytes()), 'status': 'manifest_evaluated'}],
                      'dependency_resolution': 'not_verified', 'capture_authenticity': 'not_verified'}
            with patch('hmigbot_ios.manifest_evidence.validate', return_value=result):
                graph = extract(source, manifest_evidence=evidence)
            self.assertFalse(any(i.get('path') == 'Package.swift' and i.get('code') == 'executable_manifest_not_evaluated'
                                 for i in graph['issues']))
            self.assertIs(graph['dependencies']['complete_graph'], False)
            self.assertEqual(graph['manifest_evidence']['report_sha256'], digest((evidence / 'manifest.json').read_bytes()))

    def test_manifest_evidence_does_not_clear_other_managers(self):
        self.assertIn('manifest_evidence', inspect.signature(extract).parameters)
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'source'
            source.mkdir()
            (source / 'Package.swift').write_text('import PackageDescription\n', encoding='utf-8')
            (source / 'Podfile').write_text('platform :ios, "17.0"\n', encoding='utf-8')
            evidence = Path(directory) / 'capture'
            evidence.mkdir()
            (evidence / 'manifest.json').write_text('{}', encoding='utf-8')
            plain = extract(source)
            result = {'source_sha256': plain['source_sha256'], 'integrity_passed': True,
                      'manifests': [{'path': 'Package.swift', 'name': 'Offline', 'targets': [], 'dependencies': [],
                                    'manifest_sha256': digest((source / 'Package.swift').read_bytes()), 'status': 'manifest_evaluated'}]}
            with patch('hmigbot_ios.manifest_evidence.validate', return_value=result):
                graph = extract(source, manifest_evidence=evidence)
            self.assertTrue(any(i.get('path') == 'Podfile' and i.get('code') == 'executable_manifest_not_evaluated'
                                for i in graph['issues']))

    def test_scope_filters_only_verified_declared_compilation_members(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)
            (source / 'Product.swift').write_text('struct Product { var value = 0 }\n', encoding='utf-8')
            (source / 'Oracle.swift').write_text('#if canImport(Product)\nimport Product\n#endif\n', encoding='utf-8')
            (source / 'Bridge.h').write_text('#if FEATURE\nint run(void);\n#endif\n', encoding='utf-8')
            normalized = {'scope': 'project-targets', 'source_files': ['Product.swift'], 'effective_build': 'unresolved'}
            try:
                with patch('hmigbot_ios.project_scope.resolve', return_value=(normalized, None)):
                    graph = extract(source, {'scope': 'project-targets', 'project_path': 'Product.xcodeproj/project.pbxproj',
                                             'targets': ['Product'], 'configuration': 'Release'})
            except (ImportError, AttributeError, MigrationError) as exc:
                self.fail('Facts cannot use project-declared product membership: ' + str(exc))
            self.assertFalse(any(i.get('path') == 'Oracle.swift' for i in graph['issues']))
            self.assertTrue(any(i.get('path') == 'Bridge.h' and i.get('rule') == 'IOS.CONDITIONAL_BUILD'
                                for i in graph['issues']), 'Implicitly included headers must remain conservatively reviewed')
            self.assertEqual(graph['variant']['effective_build'], 'unresolved')


if __name__ == '__main__':
    unittest.main()
