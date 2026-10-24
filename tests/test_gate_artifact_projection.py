"""UI projections bind exact source identities and preserve source-gate failures."""
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(os.environ.get('HMIGBOT_TEST_RUNTIME', Path(__file__).resolve().parents[1])).resolve()
sys.path.insert(0, str(ROOT / 'src'))

from hmigbot_ios.core import snapshot, write_json
from hmigbot_ios.gate_artifacts import (
    _coverage_report, _manifest_pages, _page_candidates,
    generate_plan_gates, generate_spec_gates,
)
from hmigbot_ios.ios_facts import refresh
from hmigbot_ios.native_pipeline import configure, index_source


class UIProjectionTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='ios-ui-projection-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.source, self.project = self.root / 'ios', self.root / 'harmony'
        self.source.mkdir()
        self.project.mkdir()
        configure(self.source, self.project)

    def source_file(self, relative, content):
        path = self.source / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')
        return path

    def page(self, ident, anchors, *, display='abbreviated.m:99', kind='page', pending=False):
        path = self.project / f'spec/baseline/ui/{ident}.md'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('# Reviewed UI contract\n'
                        + ('status: pending_authoring\n' if pending else 'status: reviewed\n')
                        + '```yaml\nsource_anchors:\n' + ''.join(
                            f'  - role: view\n    path: "{relative}"\n    symbol: "{symbol}"\n    line: {line}\n'
                            for relative, symbol, line in anchors) + '```\n', encoding='utf-8')
        return {'page_id': ident, 'spec': path.relative_to(self.project).as_posix(),
                'source': display, 'kind': kind, 'target': 'entry/src/main/ets/pages/Screen.ets',
                'feature': 'F001', 'priority': 'P0', 'status': 'pending'}

    def inventory(self):
        index = snapshot(self.source)
        return {'source_sha256': index['sha256'], 'files': index['files']}, _page_candidates(self.project, index['files'])

    def report(self, pages, *, gate=None):
        index, candidates = self.inventory()
        return _coverage_report(self.project, index, pages, candidates=candidates,
                                gate=gate or {'status': 'PASS', 'findings': []})

    def test_header_declaration_matches_exact_spec_anchor_not_display_string(self):
        self.source_file('App/Screen.h', '@interface Screen : UIViewController\n@end\n')
        self.source_file('App/Screen.m', '#import "Screen.h"\n@implementation Screen\n@end\n')
        page = self.page('page_0001', [('App/Screen.h', 'Screen', 1)], display='Screen.m:2 / UIKit')
        report = self.report([page])
        self.assertIn('gate_status: PASS', report)
        self.assertNotIn('未进入索引的源候选', report)
        self.assertIn('App/Screen.h:1', report)

    def test_same_name_different_modules_and_build_slices_are_not_collapsed(self):
        for relative in ('AppA/Screen.h', 'AppB/Screen.h', 'SDK/ios-arm64/Screen.h', 'SDK/ios-arm64-simulator/Screen.h'):
            self.source_file(relative, '@interface Screen : UIViewController\n@end\n')
        index, candidates = self.inventory()
        self.assertEqual(len(candidates), 4)
        page = self.page('page_0001', [('AppA/Screen.h', 'Screen', 1),
                                      ('SDK/ios-arm64/Screen.h', 'Screen', 1),
                                      ('SDK/ios-arm64-simulator/Screen.h', 'Screen', 1)])
        report = _coverage_report(self.project, index, [page], candidates=candidates,
                                  gate={'status': 'PASS', 'findings': []})
        self.assertIn('gate_status: BLOCKED', report)
        unmapped = [line for line in report.splitlines() if '未进入索引的源候选' in line]
        self.assertEqual(len(unmapped), 1)
        self.assertIn('AppB/Screen.h', unmapped[0])

    def test_same_file_wrong_symbol_wrong_line_or_display_only_cannot_cover(self):
        self.source_file('App/Widgets.h', '@interface First : UIView\n@end\n@interface Second : UIView\n@end\n')
        for anchors in ([('App/Widgets.h', 'Other', 1)], [('App/Widgets.h', 'First', 3)], []):
            with self.subTest(anchors=anchors):
                page = self.page('page_0001', anchors, display='App/Widgets.h / First Second')
                report = self.report([page])
                self.assertIn('gate_status: BLOCKED', report)
                self.assertEqual(report.count('未进入索引的源候选'), 2)

    def test_classification_inventory_includes_every_compound_and_unknown_kind(self):
        kinds = ['page', 'nested', 'overlay_source / inline_target',
                 'nested_source / superseded_target', 'page_source / system_owned_target',
                 'nested_source / service_seam_target', 'unused_dependency_branch',
                 'unused_sdk_declaration', 'non_product_candidate', 'unknown']
        pages = []
        for number, kind in enumerate(kinds, 1):
            symbol = f'Screen{number}'
            relative = f'App/{symbol}.h'
            self.source_file(relative, f'@interface {symbol} : UIView\n@end\n')
            pages.append(self.page(f'page_{number:04d}', [(relative, symbol, 1)], kind=kind))
        report = self.report(pages)
        for kind in kinds:
            self.assertIn(f'| {kind} | 1 | 1 |', report)
        self.assertIn('类型原值', report)
        self.assertIn('未审', report)
        self.assertIn('不构成范围排除', report)

    def test_missing_pending_or_unregistered_pages_and_failed_source_gate_stay_blocked(self):
        self.source_file('App/Screen.h', '@interface Screen : UIViewController\n@end\n')
        page = self.page('page_0001', [('App/Screen.h', 'Screen', 1)])
        failed = self.report([page], gate={'status': 'FAIL', 'findings': [{'rule': 'IOS.REAL_PRODUCT_GAP'}]})
        self.assertIn('gate_status: BLOCKED', failed)
        self.assertIn('源规格门禁：FAIL；发现 1 项', failed)
        self.assertNotIn('gate_status: PASS', failed)
        self.assertIn('gate_status: BLOCKED', self.report([]))
        self.page('page_0001', [('App/Screen.h', 'Screen', 1)], pending=True)
        self.assertIn('gate_status: BLOCKED', self.report([page]))
        (self.project / page['spec']).unlink()
        self.assertIn('gate_status: BLOCKED', self.report([page]))

    def test_new_same_name_candidates_get_distinct_ids_and_old_specs_stay_byte_identical(self):
        self.source_file('ModuleA/Screen.h', '@interface Screen : UIViewController\n@end\n')
        index_source(self.project)
        refresh(self.project, self.source)
        with patch('hmigbot_ios.ios_harness.check', return_value=({'status': 'FAIL', 'findings': []}, 2)):
            generate_spec_gates(self.project)
        old = self.project / 'spec/baseline/ui/page_0001.md'
        before = old.read_bytes()
        self.source_file('ModuleB/Screen.h', '@interface Screen : UIViewController\n@end\n')
        (self.project / 'spec/baseline/ios-source-index.json').unlink()  # fixture-only refresh
        index_source(self.project)
        refresh(self.project, self.source)
        with patch('hmigbot_ios.ios_harness.check', return_value=({'status': 'FAIL', 'findings': []}, 2)):
            generate_spec_gates(self.project)
        self.assertEqual(old.read_bytes(), before)
        new = self.project / 'spec/baseline/ui/page_0002.md'
        self.assertTrue(new.is_file())
        self.assertIn('ModuleB/Screen.h', new.read_text())
        # The authored manifest is preserved, so the unregistered new module
        # is still a real projection gap rather than silently marked covered.
        report = (self.project / 'spec/ui-coverage-report.md').read_text()
        self.assertIn('ModuleB/Screen.h', report)
        self.assertIn('gate_status: BLOCKED', report)

    def test_line_shift_keeps_stable_id_without_rewriting_stale_reviewed_anchor(self):
        self.source_file('ModuleA/Screen.h', '@interface Screen : UIViewController\n@end\n')
        index_source(self.project)
        refresh(self.project, self.source)
        with patch('hmigbot_ios.ios_harness.check', return_value=({'status': 'FAIL', 'findings': []}, 2)):
            generate_spec_gates(self.project)
        old = self.project / 'spec/baseline/ui/page_0001.md'
        before = old.read_bytes()
        self.source_file('ModuleA/Screen.h', '// new comment\n@interface Screen : UIViewController\n@end\n')
        (self.project / 'spec/baseline/ios-source-index.json').unlink()  # fixture-only refresh
        index_source(self.project)
        refresh(self.project, self.source)
        with patch('hmigbot_ios.ios_harness.check', return_value=({'status': 'FAIL', 'findings': []}, 2)):
            generate_spec_gates(self.project)
        self.assertEqual(old.read_bytes(), before)
        self.assertFalse((self.project / 'spec/baseline/ui/page_0002.md').exists())
        report = (self.project / 'spec/ui-coverage-report.md').read_text()
        self.assertIn('ModuleA/Screen.h:2', report)
        self.assertIn('gate_status: BLOCKED', report)

    def test_stale_candidate_hash_and_duplicate_anchor_fields_fail_closed(self):
        path = self.source_file('App/Screen.h', '@interface Screen : UIViewController\n@end\n')
        page = self.page('page_0001', [('App/Screen.h', 'Screen', 1)])
        index, candidates = self.inventory()
        path.write_text(path.read_text() + '// changed bytes\n')
        report = _coverage_report(self.project, index, [page], candidates=candidates,
                                  gate={'status': 'PASS', 'findings': []})
        self.assertIn('未进入索引的源候选', report)
        path.write_text('@interface Screen : UIViewController\n@end\n')
        spec = self.project / page['spec']
        spec.write_text(spec.read_text().replace('    line: 1', '    symbol: "Screen"\n    line: 1'))
        self.assertIn('未进入索引的源候选', self.report([page]))

    def test_existing_canonical_plans_are_preserved_and_reported_as_preserved(self):
        self.source_file('Screen.swift', 'import SwiftUI\nstruct Screen: View { var body: some View { Text("x") } }\n')
        index_source(self.project)
        refresh(self.project, self.source)
        folder = self.project / 'spec/baseline/plans'
        folder.mkdir(parents=True)
        original = {}
        for name in ('ui-plan.md', 'feature-plan.md'):
            path = folder / name
            path.write_text(f'# Existing canonical {name}\nF001 pending old authored draft\n')
            original[path] = path.read_bytes()
        with patch('hmigbot_ios.ios_harness.check', return_value=({'status': 'FAIL', 'findings': []}, 2)):
            result = generate_plan_gates(self.project)
        self.assertEqual(result['gate_status'], 'BLOCKED_BY_SPEC')
        for path, before in original.items():
            self.assertEqual(path.read_bytes(), before)
        report = (self.project / 'spec/reports/derived/feature-plan.md').read_text()
        self.assertIn('已保留', report)
        self.assertIn('重新生成', report)
        self.assertIn('BLOCKED_BY_SPEC', report)


if __name__ == '__main__':
    unittest.main()
