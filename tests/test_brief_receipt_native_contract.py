"""--brief writes the same full file and prints only a small receipt."""
import io
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

ROOT = Path(os.environ.get('HMIGBOT_TEST_RUNTIME', Path(__file__).resolve().parents[1])).resolve()
sys.path.insert(0, str(ROOT / 'src'))

from hmigbot_ios.core import MigrationError, digest, write_json
from hmigbot_ios.native_pipeline import main
from test_ios_harness import fixture


def _run(argv):
    stream = io.StringIO()
    with redirect_stdout(stream):
        code = main(argv)
    return code, stream.getvalue()


class BriefReceiptTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='brief-receipt-')
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.source, self.project, self.graph = fixture(self.root)

    def test_migration_report_brief_matches_full_bytes_and_sha(self):
        report = self.project / 'spec/migration-report.md'
        full_code, full_out = _run(['migration-report', '--project', str(self.project),
                                    '--output', str(report)])
        self.assertEqual(full_code, 0, full_out)
        full_bytes = report.read_bytes()
        self.assertIn('迁移证据报告', full_out)
        self.assertIn('markdown', full_out)

        brief_code, brief_out = _run(['migration-report', '--project', str(self.project),
                                      '--output', str(report), '--brief'])
        self.assertEqual(brief_code, 0, brief_out)
        self.assertEqual(report.read_bytes(), full_bytes)
        self.assertLess(len(brief_out.encode('utf-8')), 2048)
        self.assertNotIn('迁移证据报告', brief_out)
        self.assertNotIn('| page_0001', brief_out)
        payload = json.loads(brief_out)
        self.assertEqual(payload['status'], 'generated')
        self.assertEqual(payload['mode'], 'brief')
        self.assertEqual(payload['sha256'], digest(full_bytes))
        self.assertEqual(payload['bytes'], len(full_bytes))
        self.assertEqual(Path(payload['output']).resolve(), report.resolve())

    def test_spec_summary_brief_matches_full_bytes_and_sha(self):
        summary_path = self.project / 'spec/reports/spec-summary.json'
        full_code, full_out = _run(['spec-summary', '--project', str(self.project),
                                    '--output', str(summary_path)])
        self.assertEqual(full_code, 0, full_out)
        full_bytes = summary_path.read_bytes()
        self.assertIn('"pages"', full_out)

        brief_code, brief_out = _run(['spec-summary', '--project', str(self.project),
                                      '--output', str(summary_path), '--brief'])
        self.assertEqual(brief_code, 0, brief_out)
        self.assertEqual(summary_path.read_bytes(), full_bytes)
        self.assertLess(len(brief_out.encode('utf-8')), 2048)
        payload = json.loads(brief_out)
        self.assertEqual(payload['mode'], 'brief')
        self.assertEqual(payload['sha256'], digest(full_bytes))
        self.assertEqual(payload['bytes'], len(full_bytes))

    def test_brief_requires_output_and_rejects_check_or_unsupported_mode(self):
        code, out = _run(['migration-report', '--project', str(self.project), '--brief'])
        self.assertEqual(code, 2)
        self.assertIn('--brief requires --output', out)
        code, out = _run(['spec-summary', '--project', str(self.project), '--brief'])
        self.assertEqual(code, 2)
        self.assertIn('--brief requires --output', out)

        report = self.project / 'spec/migration-report.md'
        _run(['migration-report', '--project', str(self.project), '--output', str(report)])
        code, out = _run(['migration-report', '--project', str(self.project),
                          '--check', str(report), '--brief'])
        self.assertEqual(code, 2)
        self.assertIn('--brief is not supported with --check', out)

        # Unsupported mode: argparse rejects --brief for product-literals.
        with self.assertRaises(SystemExit):
            _run(['product-literals', '--project', str(self.project),
                  '--output', str(self.project / 'spec/reports/product-literals.json'), '--brief'])

    def test_check_semantics_still_reject_tampered_report(self):
        report = self.project / 'spec/migration-report.md'
        code, _ = _run(['migration-report', '--project', str(self.project), '--output', str(report)])
        self.assertEqual(code, 0)
        original = report.read_bytes()
        report.write_bytes(original.replace(b'hmigbot-derived-report:2', b'hmigbot-derived-report:3', 1))
        code, out = _run(['migration-report', '--project', str(self.project), '--check', str(report)])
        self.assertEqual(code, 2, out)
        report.write_bytes(original)
        code, out = _run(['migration-report', '--project', str(self.project), '--check', str(report)])
        self.assertEqual(code, 0, out)


if __name__ == '__main__':
    unittest.main()
