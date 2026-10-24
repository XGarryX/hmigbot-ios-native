import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(os.environ.get('HMIGBOT_TEST_RUNTIME', Path(__file__).resolve().parents[1])).resolve()
sys.path.insert(0, str(ROOT / 'src'))
from hmigbot_ios.core import MigrationError, read_json, snapshot, write_json
from hmigbot_ios.native_pipeline import configure, index_source
from hmigbot_ios.source_analysis import run
from hmigbot_ios.native_authoring import prepare


class SourceAnalysisTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source, self.project = self.root / 'ios', self.root / 'harmony'
        self.source.mkdir()
        self.project.mkdir()
        self.file = self.source / 'Counter.swift'
        self.file.write_text('''import SwiftUI
struct Counter: View {
    @State var count = 0
    var body: some View {
        VStack { Text("Count"); Button("Add") { count += 1 } }
    }
}
''', encoding='utf-8')
        configure(self.source, self.project)
        # Unit tests use the explicit static scope; native orchestration is tested separately.
        write_json(self.project / 'spec/ref/ios-analysis-config.json', {'schema_version': 1, 'mode': 'static'})

    def test_fresh_entry_produces_candidates_without_approving_them(self):
        result = run(self.project, apply_scaffold=True)
        self.assertEqual(result['status'], 'needs_review')
        self.assertFalse(result['spec_complete'])
        self.assertFalse(result['behavior_verified'])
        self.assertEqual(result['build'], 'not_run')
        inventory = prepare(self.project)
        self.assertTrue(inventory['documents'])
        self.assertEqual(inventory['acceptance'], [])  # no fabricated ACs
        graph = read_json(self.project / 'spec/baseline/ios-facts.json')
        obs_path = self.project / 'spec/baseline/ios-obligations.json'
        obs = obs_path.read_bytes()
        self.assertEqual(result['counts']['facts'], len(graph['facts']))
        self.assertGreater(result['counts']['obligations'], 0)
        from hmigbot_ios.ios_harness import check
        self.assertEqual(check(self.project, report_only=True)[1], 2)
        self.assertEqual(obs_path.read_bytes(), obs)

    def test_default_does_not_apply_candidate_and_returns_small_receipt(self):
        result = run(self.project)
        self.assertTrue((self.project / 'spec/reports/derived/spec-scaffold.json').is_file())
        self.assertFalse((self.project / 'spec/baseline/features').exists())
        self.assertNotIn('file_contents', result)
        self.assertNotIn('facts', result)
        for path, entry in result['artifacts'].items():
            self.assertEqual(entry['bytes'], (self.project / path).stat().st_size)

    def test_stale_source_with_same_mtime_and_size_preserves_baseline(self):
        run(self.project)
        before = (self.project / 'spec/baseline/ios-source-index.json').read_bytes()
        stat = self.file.stat()
        original_size = stat.st_size
        self.file.write_bytes(self.file.read_bytes().replace(b'Add', b'Del'))
        os.utime(self.file, ns=(stat.st_atime_ns, stat.st_mtime_ns))
        self.assertEqual(self.file.stat().st_size, original_size)
        with self.assertRaisesRegex(MigrationError, 'stale'):
            run(self.project)
        self.assertEqual((self.project / 'spec/baseline/ios-source-index.json').read_bytes(), before)

    def test_planned_project_is_rejected_before_any_mutation(self):
        write_json(self.project / 'spec/waves/plan-domains.json', {'pending': True})
        before = snapshot(self.project)
        with self.assertRaisesRegex(MigrationError, 'planned project'):
            run(self.project)
        self.assertEqual(snapshot(self.project), before)

    def test_provider_failure_retains_failed_preparation_receipt(self):
        with patch('hmigbot_ios.ios_facts.refresh', side_effect=MigrationError('provider unavailable')):
            with self.assertRaisesRegex(MigrationError, 'retained analysis receipt'):
                run(self.project)
        report = read_json(self.project / 'spec/reports/derived/source-analysis.json')
        self.assertEqual(report['status'], 'failed')
        self.assertFalse(report['spec_complete'])
        self.assertFalse((self.project / 'spec/baseline/ios-facts.json').exists())

    def test_current_host_and_explicit_static_execution_are_separate(self):
        from hmigbot_ios.host import detect_host_profile
        run(self.project)  # existing harness initialization may add expertise config
        config_before = (self.project / '.migbot/config.json').read_bytes()
        for host in ['Windows', 'Darwin']:
            profile = detect_host_profile(host_os=host, lookup=lambda name: '/tools/' + name,
                                          machine='fixture', environ={})
            with patch('hmigbot_ios.host.detect_host_profile', return_value=profile):
                result = run(self.project)
            self.assertEqual(result['host_profile'], profile)
            selection = result['source_provider_selection']
            self.assertFalse(selection['discovery_only'])
            self.assertEqual(selection['provider'], profile['source']['provider'])
            self.assertEqual(selection['execution'], 'automatic_context_plan')
            self.assertEqual(selection['selected_backend'], 'static')
            self.assertEqual(selection['compiler_binding'], 'unresolved')
            self.assertEqual(result['build'], 'not_run')
            self.assertFalse(result['behavior_verified'])
            self.assertEqual(read_json(self.project / 'spec/reports/derived/source-analysis.json')['host_profile'], profile)
        self.assertEqual((self.project / '.migbot/config.json').read_bytes(), config_before)

    def test_invalid_provider_plan_retains_receipt_without_preparing_baseline(self):
        plan = self.root / 'providers.json'
        write_json(plan, {'schema_version': 2, 'providers': [
            {'operation': 'interface-builder'}, {'operation': 'swift-syntax'}]})
        from hmigbot_ios.atoms import run_atom
        with patch('hmigbot_ios.atoms.run_atom', wraps=run_atom) as atom:
            with self.assertRaisesRegex(MigrationError, 'Provider plan'):
                run(self.project, providers=plan)
            atom.assert_not_called()
        self.assertFalse((self.project / 'spec/baseline/ios-source-index.json').exists())
        self.assertFalse((self.project / 'spec/baseline/ios-facts.json').exists())
        receipt = read_json(self.project / 'spec/reports/derived/source-analysis.json')
        self.assertEqual(receipt['status'], 'failed')
        self.assertEqual(receipt['stages'][-1]['name'], 'provider-plan-preflight')

    def test_source_change_during_index_never_publishes_mixed_index(self):
        from hmigbot_ios.analyze import analyze
        def mutate(source):
            result = analyze(source)
            self.file.write_bytes(self.file.read_bytes().replace(b'Add', b'Del'))
            return result
        with patch('hmigbot_ios.native_pipeline.analyze', side_effect=mutate):
            with self.assertRaisesRegex(MigrationError, 'changed while indexing'):
                index_source(self.project)
        self.assertFalse((self.project / 'spec/baseline/ios-source-index.json').exists())

    def test_cli_under_gbk_prepares_fresh_source(self):
        result = subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/a2h_ios.py'),
                                 'source-analysis', '--project', str(self.project), '--apply-scaffold'],
                                capture_output=True, env={**os.environ, 'PYTHONIOENCODING': 'gbk'}, timeout=30)
        self.assertEqual(result.returncode, 0, (result.stdout, result.stderr))
        payload = json.loads(result.stdout.decode('utf-8'))
        self.assertEqual(payload['status'], 'needs_review')
        self.assertFalse(payload['spec_complete'])


if __name__ == '__main__':
    unittest.main()
