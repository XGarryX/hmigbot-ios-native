"""Independent gate diagnostics must expose gaps without weakening acceptance."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from test_ios_harness import fixture
from hmigbot_ios.core import read_json, write_json
from hmigbot_ios.ios_harness import check


class HarnessDiagnosticsTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='ios-harness-diagnostics-')
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve()
        self.source, self.project, self.graph = fixture(self.root)
        self.base = self.project / 'spec/baseline'

    def test_missing_inputs_are_reported_together(self):
        for path in ('spec/ref/ios-expertise-reviews.json',
                     'spec/baseline/literal-ledger.json',
                     'spec/baseline/ios-semantics.json',
                     'spec/baseline/ios-coverage.json',
                     'spec/baseline/feature-base.md'):
            (self.project / path).unlink()
        report, code = check(self.project, report_only=True)
        self.assertEqual(code, 2)
        for stage in ('expertise', 'literals', 'semantics_input', 'coverage_input', 'spec_contract'):
            self.assertEqual(report['checks'][stage]['status'], 'FAIL', (stage, report))
        self.assertEqual(report['checks']['native_claims'],
                         {'status': 'not_run', 'blocked_dependencies': ['source_contract', 'semantics_input']})
        self.assertEqual(report['checks']['coverage'],
                         {'status': 'not_run', 'blocked_dependencies': ['coverage_input']})
        self.assertTrue(any(f['subject'].endswith('feature-base.md') for f in report['findings']))
        for name in ('ios-expertise-reviews.json', 'literal-ledger.json', 'ios-semantics.json', 'ios-coverage.json'):
            self.assertIn(name, str(report['findings']))

    def test_invalid_graph_blocks_consumers_but_spec_still_runs(self):
        graph = read_json(self.base / 'ios-facts.json')
        graph['facts'][0]['owner'] = 'TamperedOwner'
        write_json(self.base / 'ios-facts.json', graph)
        (self.base / 'feature-base.md').unlink()
        with patch('hmigbot_ios.ios_harness.validate_native_claims') as claims:
            report, code = check(self.project, report_only=True)
        self.assertEqual(code, 2)
        claims.assert_not_called()
        for name in ('extraction', 'expertise', 'native_claims', 'coverage'):
            self.assertEqual(report['checks'][name]['status'], 'not_run')
            self.assertIn('graph', report['checks'][name]['blocked_dependencies'])
        self.assertEqual(report['checks']['spec_contract']['status'], 'FAIL')
        self.assertTrue(any(f['subject'].endswith('feature-base.md') for f in report['findings']))
        self.assertFalse(any(f['rule'] == 'IOS.OBLIGATION_UNCOVERED' for f in report['findings']))
        self.assertEqual(report['excluded_obligation_ids'], [])

    def test_malformed_json_graph_is_failure_not_crash_or_coverage_pass(self):
        (self.base / 'ios-facts.json').write_text('{invalid json', encoding='utf-8')
        report, code = check(self.project, report_only=True)
        self.assertEqual(code, 2)
        self.assertEqual(report['checks']['graph']['status'], 'FAIL')
        self.assertEqual(report['checks']['coverage']['status'], 'not_run')
        # The spec validator is independently attempted; its malformed input is
        # surfaced as its own failure instead of silently dropping that stage.
        self.assertEqual(report['checks']['spec_contract']['status'], 'FAIL')

    def test_malformed_semantics_cannot_reach_native_claims(self):
        write_json(self.base / 'ios-semantics.json',
                   {'schema_version': 2, 'source_platform': 'ios', 'documents': [None]})
        with patch('hmigbot_ios.ios_harness.validate_native_claims') as claims:
            report, code = check(self.project, report_only=True)
        self.assertEqual(code, 2)
        claims.assert_not_called()
        self.assertEqual(report['checks']['semantics_input']['status'], 'FAIL')
        self.assertEqual(report['checks']['native_claims']['status'], 'not_run')
        self.assertEqual(report['checks']['coverage']['status'], 'PASS')

    def test_malformed_coverage_cannot_be_counted(self):
        for malformed in (None, [], {'schema_version': 2, 'graph_sha256': 'a', 'mappings': [None]},
                          {'schema_version': 2, 'graph_sha256': 'a', 'mappings': [
                              {'obligation_id': [], 'ac_ids': []}]}):
            with self.subTest(value=malformed):
                write_json(self.base / 'ios-coverage.json', malformed)
                report, code = check(self.project, report_only=True)
                self.assertEqual(code, 2)
                self.assertEqual(report['checks']['coverage_input']['status'], 'FAIL')
                self.assertEqual(report['checks']['coverage']['status'], 'not_run')
                self.assertFalse(any(f['rule'].startswith('IOS.OBLIGATION_') for f in report['findings']))

    def test_report_only_failure_preserves_entire_project(self):
        from hmigbot_ios.native_pipeline import findings_module
        queue = findings_module()
        queue.replace_section(str(self.project), 'spec.ios-harness', [
            queue.make('IOS.SENTINEL', 'spec', 'preserve', 'Earlier unresolved finding')])
        (self.base / 'ios-coverage.json').unlink()
        before = {p.relative_to(self.project): p.read_bytes()
                  for p in self.project.rglob('*') if p.is_file()}
        report, code = check(self.project, report_only=True)
        after = {p.relative_to(self.project): p.read_bytes()
                 for p in self.project.rglob('*') if p.is_file()}
        self.assertEqual(code, 2, report)
        self.assertEqual(before, after)

    def test_valid_contract_retains_acceptance_and_behavior_boundary(self):
        report, code = check(self.project, report_only=True)
        self.assertEqual(code, 0, report)
        self.assertEqual(report['status'], 'PASS')
        self.assertEqual(report['findings'], [])
        self.assertFalse(report['behavior_verified'])
        self.assertEqual(report['excluded_obligation_ids'], [])
        self.assertEqual(report['extraction_issue_dispositions'], [])
        self.assertTrue(report['checks'])
        self.assertTrue(all(item['status'] == 'PASS' for item in report['checks'].values()))

    def test_normal_mode_uses_original_writer_and_saves_full_report(self):
        (self.base / 'ios-coverage.json').unlink()
        report, code = check(self.project)
        self.assertEqual(code, 2)
        self.assertEqual(read_json(self.project / 'spec/reports/ios-harness-check.json'), report)
        self.assertTrue((self.project / 'spec/.a2h/open-findings.json').exists())


if __name__ == '__main__':
    unittest.main()
