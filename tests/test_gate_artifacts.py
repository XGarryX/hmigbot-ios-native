"""Regression boundaries for generated iOS gate artifacts."""
import contextlib
import io
import json
import os
from pathlib import Path
import sys
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(os.environ.get('HMIGBOT_TEST_RUNTIME', Path(__file__).resolve().parents[1])).resolve()
sys.path.insert(0, str(ROOT / 'src'))

from hmigbot_ios.core import MigrationError, digest, snapshot, write_json
from hmigbot_ios.gate_artifacts import (
    MARKER, generate_spec_gates, generate_plan_gates, generate_verify_report,
    generate_execution_gates,
)
from hmigbot_ios.ios_facts import refresh
from hmigbot_ios.native_pipeline import configure, index_source, main


class GateArtifactTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='ios-gates-')
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        self.source, self.project = root / 'ios', root / 'harmony'
        self.source.mkdir()
        self.project.mkdir()
        (self.source / 'Screen.swift').write_text(
            'import SwiftUI\nstruct Screen: View { var body: some View { Text("Hello") } }\n')
        configure(self.source, self.project)
        index_source(self.project)
        refresh(self.project, self.source)

    def cli(self, *args):
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            code = main([*args, '--project', str(self.project)])
        return code, json.loads(stream.getvalue())

    def files(self, relative='spec'):
        return {p.relative_to(self.project).as_posix(): p.read_bytes()
                for p in (self.project / relative).rglob('*') if p.is_file()}

    def test_all_stages_generate_reports_but_pending_contracts_never_pass(self):
        code, receipt = self.cli('gate-artifacts', '--stage', 'all')
        self.assertEqual(code, 0, receipt)
        for relative in (
            'spec/baseline/ui-manifest.md', 'spec/baseline/feature-index.md',
            'spec/baseline/plans/ui-plan.md', 'spec/baseline/plans/feature-plan.md',
            'spec/ui-coverage-report.md', 'spec/reports/derived/ui-plan.md',
            'spec/reports/derived/feature-plan.md', 'spec/migration-report.md',
            'spec/verify-report.md',
        ):
            self.assertTrue((self.project / relative).is_file(), relative)
        self.assertIn('gate_status: BLOCKED', (self.project / 'spec/ui-coverage-report.md').read_text())
        self.assertIn('gate_status: FAIL', (self.project / 'spec/verify-report.md').read_text())
        self.assertEqual(self.cli('migration-report', '--check', str(self.project / 'spec/migration-report.md'))[0], 0)
        self.assertEqual(self.cli('verify-report', '--check', str(self.project / 'spec/verify-report.md'))[0], 0)
        before = self.files('spec/baseline')
        self.cli('gate-artifacts', '--stage', 'all')
        self.assertEqual(before, self.files('spec/baseline'))

    def test_marked_documents_and_reviewed_json_are_preserved(self):
        generate_spec_gates(self.project)
        page = self.project / 'spec/baseline/ui/page_0001.md'
        page.write_text(page.read_text() + '\nUser authored behavior and evidence.\n')
        coverage = self.project / 'spec/baseline/ios-coverage.json'
        value = json.loads(coverage.read_text())
        value['mappings'][0]['ac_ids'] = ['F001-AC01']
        write_json(coverage, value)
        before = self.files('spec/baseline')
        generate_spec_gates(self.project)
        self.assertEqual(before, self.files('spec/baseline'))

    def test_existing_feature_id_is_not_duplicated_by_facts_hook(self):
        folder = self.project / 'spec/baseline/features'
        folder.mkdir(parents=True)
        (folder / 'F001-real.md').write_text('# Real feature\nUser contract\n')
        code, receipt = self.cli('facts', '--brief')
        self.assertEqual(code, 0, receipt)
        self.assertEqual([p.name for p in folder.glob('F*.md')], ['F001-real.md'])
        semantics = json.loads((self.project / 'spec/baseline/ios-semantics.json').read_text())
        for document in semantics['documents']:
            self.assertTrue(document['languages'])
            self.assertTrue(document['frameworks'])
            self.assertTrue(document['facts'])
            self.assertTrue(all(fact['status'] == 'unknown' for fact in document['facts'].values()))

    def test_shell_wrapper_forwards_stage_and_brief_arguments(self):
        proc = subprocess.run(['/bin/sh', str(ROOT / 'bin/a2h-tool'), 'facts', '--brief'],
                              cwd=self.project, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
        self.assertIsInstance(json.loads(proc.stdout)['facts'], int)
        proc = subprocess.run(['/bin/sh', str(ROOT / 'bin/a2h-tool'), 'gate-artifacts', '--stage', 'plan'],
                              cwd=self.project, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
        self.assertEqual(len(json.loads(proc.stdout)['stages']), 1)

    def test_ids_survive_new_declarations_and_no_old_page_is_deleted(self):
        generate_spec_gates(self.project)
        old = (self.project / 'spec/baseline/ui/page_0001.md').read_bytes()
        (self.source / 'AAA.swift').write_text('import SwiftUI\nstruct Added: View { var body: some View { Text("A") } }')
        (self.project / 'spec/baseline/ios-source-index.json').unlink()  # fixture-only refresh
        index_source(self.project)
        refresh(self.project, self.source)
        generate_spec_gates(self.project)
        self.assertEqual(old, (self.project / 'spec/baseline/ui/page_0001.md').read_bytes())
        self.assertIn('Added', (self.project / 'spec/baseline/ui/page_0002.md').read_text())

    def test_read_only_gate_and_frozen_plans_are_not_mutated(self):
        generate_spec_gates(self.project)
        plans = self.project / 'spec/baseline/plans'
        plans.mkdir()
        (plans / 'ui-plan.md').write_text('# Reviewed UI plan\nFrozen user input\n')
        (plans / 'feature-plan.md').write_text('# Reviewed indexed feature plan\nFrozen user input\n')
        write_json(self.project / 'spec/blueprint/contracts.json', {'test': 'frozen'})
        before = self.files('spec/baseline')
        generate_plan_gates(self.project)
        generate_spec_gates(self.project)
        self.assertEqual(before, self.files('spec/baseline'))
        everything = self.files()
        self.cli('source-check', '--harness', '--report-only')
        self.assertEqual(everything, self.files())

    def test_stale_source_refuses_scaffolding(self):
        before = self.files()
        (self.source / 'Screen.swift').write_text('// changed source\n')
        with self.assertRaisesRegex(MigrationError, 'stale'):
            generate_spec_gates(self.project)
        self.assertEqual(before, self.files())

    def test_filename_and_old_status_cannot_claim_compilation_or_behavior_pass(self):
        generate_spec_gates(self.project)
        write_json(self.project / 'spec/ref/random-build.json', {'status': 'PASS'})
        write_json(self.project / 'spec/reports/ios-behavior-check.json', {'status': 'PASS'})
        generate_verify_report(self.project)
        text = (self.project / 'spec/verify-report.md').read_text()
        self.assertIn('| compilation | not_run |', text)
        self.assertNotIn('| behavior | passed |', text)
        self.assertIn('| CHECK-3 | 视觉对齐 | DEFERRED |', text)

    def test_verification_check_rejects_edited_report(self):
        generate_spec_gates(self.project)
        generate_verify_report(self.project)
        path = self.project / 'spec/verify-report.md'
        path.write_text(path.read_text() + '\nmanual PASS\n')
        code, _ = self.cli('verify-report', '--check', str(path))
        self.assertEqual(code, 2)

    def test_verifier_selection_requires_current_hashes_and_preserves_unrun_scope(self):
        from hmigbot_ios.quality_views import spec_inputs, target_inputs
        generate_spec_gates(self.project)
        evidence = self.project / 'spec/ref/static-result.json'
        write_json(evidence, {'static_errors': 0})
        entry = {'id': 'CHECK-1', 'selected': True, 'status': 'PASS', 'exit_code': 0,
                 'detail': 'static result', 'evidence': [{'path': 'spec/ref/static-result.json',
                                                         'sha256': digest(evidence.read_bytes())}]}
        write_json(self.project / 'spec/verification/verify-results.json', {
            'schema_version': 1, 'source_sha256': snapshot(self.source)['sha256'],
            'spec_input_hashes': spec_inputs(self.project), 'target_input_hashes': target_inputs(self.project),
            'checks': [entry, {'id': 'CHECK-3', 'selected': False, 'status': 'SKIP',
                               'detail': 'User explicitly did not select visual verification', 'evidence': []}]})
        generate_verify_report(self.project)
        text = (self.project / 'spec/verify-report.md').read_text()
        self.assertIn('| CHECK-1 | 静态分析 | PASS |', text)
        self.assertIn('| CHECK-3 | 视觉对齐 | SKIP |', text)
        self.assertIn('| CHECK-4 | 单元测试 | DEFERRED |', text)
        evidence.write_text('{"static_errors": 1}')
        generate_verify_report(self.project)
        text = (self.project / 'spec/verify-report.md').read_text()
        self.assertIn('| CHECK-1 | 静态分析 | DEFERRED |', text)

    def test_summary_failure_still_produces_honest_blocked_report(self):
        with patch('hmigbot_ios.quality_views.summary', side_effect=MigrationError('Evidence is stale')):
            receipt = generate_execution_gates(self.project)
        self.assertEqual(receipt['summary_status'], 'blocked')
        text = (self.project / 'spec/migration-report.md').read_text()
        self.assertIn('gate_status: BLOCKED', text)
        self.assertIn('Evidence is stale', text)


if __name__ == '__main__':
    unittest.main()
