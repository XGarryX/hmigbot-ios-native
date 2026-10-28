"""Public native route chain and refusal of stale/failed target evidence."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from hmigbot_ios152.native_routes_entry import compiled
SCRIPTS = ROOT / 'skills/arkts-router-verify/scripts'


class TargetRouteEntry(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='native-target-entry-')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.project = self.base / 'project'
        (self.project / '.agents').mkdir(parents=True)
        self.source = self.base / 'source'
        self.source.mkdir()
        (self.source / 'Main.swift').write_text('''import SwiftUI
@main struct AppRoot:App{var body:some Scene{WindowGroup{RootView()}}}
struct RootView:View{var body:some View{TabView{FirstView().tabItem{Text("First")};SecondView().tabItem{Text("Second")}}}}
struct FirstView:View{var body:some View{Text("First")}}
struct SecondView:View{var body:some View{Text("Second")}}
''')
        self.pages = self.project / 'entry/src/main/ets/pages'
        self.pages.mkdir(parents=True)
        self.host = self.pages / 'NeutralRoot.ets'
        self.host.write_text('''import { FirstPage } from './FirstPage'
import { SecondPage } from './SecondPage'
@Entry @Component struct NeutralRoot {
 @Builder firstContent(){FirstPage()}
 @Builder secondContent(){SecondPage()}
 build(){Tabs(){TabContent(){Navigation(){this.firstContent()}}.tabBar('First');TabContent(){Navigation(){this.secondContent()}}.tabBar('Second')}}
}
''')
        for name in ('FirstPage', 'SecondPage'):
            (self.pages / (name + '.ets')).write_text('@Component export struct ' + name + "{build(){Text('Real content')}}")
        manifest = self.project / 'spec/baseline/ui-manifest.md'
        manifest.parent.mkdir(parents=True)
        manifest.write_text('| 序号 | iOS | ArkTS 产出 | 优先级 | confidence | 状态 |\n'
            '|---|---|---|---|---|---|\n'
            '| 0000 | RootView | NeutralRoot.ets | P0 | high | converted |\n'
            '| 0001 | FirstView | FirstPage.ets | P0 | high | converted |\n'
            '| 0002 | SecondView | SecondPage.ets | P0 | high | converted |\n')
        profile = self.project / 'entry/src/main/resources/base/profile/main_pages.json'
        profile.parent.mkdir(parents=True)
        profile.write_text(json.dumps({'src': ['pages/NeutralRoot']}))
        self.out = self.project / 'spec/verify/route'
        for stage in ('extract_nav_graph', 'llm_worklist', 'apply_llm'):
            result = self.runstage(stage, *(['--platform', 'ios', '--ios-root', str(self.source)] if stage == 'extract_nav_graph' else []))
            self.assertEqual(result.returncode, 0, stage + result.stdout + result.stderr)

    def runstage(self, stage, *args):
        return subprocess.run([sys.executable, '-B', str(SCRIPTS / (stage + '.py')), *args],
            cwd=self.project, env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1',
                'ROUTE_VERIFY_ROOT': str(self.project), 'ROUTE_VERIFY_OUT': str(self.out)},
            text=True, capture_output=True, timeout=120)

    def read(self, name):
        return json.loads((self.out / name).read_text())

    def extract_target(self):
        result = self.runstage('hmos_extract')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_public_chain_preserves_independent_robust_classifications(self):
        self.extract_target()
        self.assertEqual(self.read('actual_nav.original.json')['tab_groups'], [])
        self.assertEqual(self.read('actual_nav.json')['tab_groups'][0]['tabs'], ['FirstPage', 'SecondPage'])
        for stage in ('build_page_mapping', 'build_report', 'diff_routes', 'hmos_reachability', 'thin_shell_probe', 'ios_dialog_probe', 'build_fix_plan'):
            result = self.runstage(stage)
            self.assertEqual(result.returncode, 0, stage + result.stdout + result.stderr)
        reference = self.base / 'reference'
        shutil.copytree(self.out, reference)
        original = compiled(SCRIPTS, 'hmos_reachability', env={'ROUTE_VERIFY_ROOT': str(self.project), 'ROUTE_VERIFY_OUT': str(reference)})
        self.assertEqual(original.returncode, 0, original.stderr)
        actual = self.read('reachability_robust.json')
        self.assertTrue(any(page.get('ets_ast_supplement') for page in actual['pages']))
        for page in actual['pages']:
            page.pop('ets_ast_supplement', None)
        self.assertEqual(actual, json.loads((reference / 'reachability_robust.json').read_text()))

    def test_changed_target_cannot_reuse_extraction(self):
        self.extract_target()
        self.host.write_text(self.host.read_text() + '\n// changed measured input\n')
        result = self.runstage('build_page_mapping')
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertEqual(self.read('build_page_mapping.native-input.json')['status'], 'incomplete')

    def test_changed_actual_output_cannot_reuse_receipt(self):
        self.extract_target()
        path = self.out / 'actual_nav.json'
        path.write_text(path.read_text() + '\n')
        result = self.runstage('build_report')
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn('target output changed', result.stderr)

    def test_failed_parse_invalidates_prior_success(self):
        self.extract_target()
        self.host.write_text(self.host.read_text() + '\n@Component struct Broken {\n')
        result = self.runstage('hmos_extract')
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertEqual(self.read('hmos_extract.native-input.json')['status'], 'incomplete')
        result = self.runstage('build_report')
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
