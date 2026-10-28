import json
from pathlib import Path
import plistlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from hmigbot_ios152.native_context import describe
from hmigbot_ios152.source import Source


class NativeContextTests(unittest.TestCase):
    def inspect(self, text, extra=None):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'Neutral.swift').write_text(text)
            for name, data in (extra or {}).items():
                p = root / name
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(data)
            return describe(Source(root))

    def test_launcher_is_main_app_not_alphabetical_view(self):
        value = self.inspect('''import SwiftUI
import UIKit
struct AAFirstView: View { var body: some View { Text("First") } }
@main struct ZNeutralApp: App { var body: some Scene { WindowGroup { AAFirstView() } } }
let accent = UIColor.red
''')
        self.assertEqual('ZNeutralApp', value['launcher_short'])
        self.assertEqual('pure_compose', value['arch'])
        self.assertEqual(['AAFirstView'], [r['symbol'] for r in value['render_roots']])

    def test_widget_entry_is_separate(self):
        value = self.inspect('''import SwiftUI
import WidgetKit
@main struct MainApp: App { var body: some Scene { WindowGroup { Text("App") } } }
@main struct NeutralWidgets: WidgetBundle { var body: some Widget { StatusWidget() } }
''')
        self.assertEqual('MainApp', value['launcher_short'])
        self.assertEqual('NeutralWidgets', value['extension_roots'][0]['symbol'])

    def test_ambiguous_app_entries_are_not_arbitrarily_selected(self):
        value = self.inspect('''import SwiftUI
@main struct A: App { var body: some Scene { WindowGroup { Text("A") } } }
@main struct B: App { var body: some Scene { WindowGroup { Text("B") } } }
''')
        self.assertIsNone(value['launcher_short'])
        self.assertIn('ambiguous_application_entry', [x['kind'] for x in value['unknowns']])

    def test_uikit_scene_and_initial_controller_use_declared_plist(self):
        info = {'UIApplicationSceneManifest': {'UISceneConfigurations': {
            'UIWindowSceneSessionRoleApplication': [{'UISceneDelegateClassName': '$(PRODUCT_MODULE_NAME).SceneDelegate',
                                                     'UISceneStoryboardFile': 'Main'}]}}}
        storyboard = b'<document initialViewController="root"><scenes><viewController id="root" customClass="HomeController"/></scenes></document>'
        value = self.inspect('''import UIKit
@main class AppDelegate: UIResponder, UIApplicationDelegate {}
class SceneDelegate: UIResponder, UIWindowSceneDelegate {}
class HomeController: UIViewController {}
''', {'Info.plist': plistlib.dumps(info), 'Main.storyboard': storyboard})
        self.assertEqual('AppDelegate', value['launcher_short'])
        self.assertEqual('pure_traditional', value['arch'])
        self.assertIn('HomeController', [r['symbol'] for r in value['render_roots']])

    def test_absent_entry_is_explicit(self):
        value = self.inspect('import SwiftUI\nstruct Screen: View { var body: some View { Text("Only") } }')
        self.assertIsNone(value['launcher_short'])
        self.assertIn('application_entry_not_declared', [x['kind'] for x in value['unknowns']])

    def test_additive_provider_owner_labels_and_utf8_spans(self):
        text = '''import SwiftUI
struct Outer { struct Inner { func go(to target: String) { print("豆") }
func go(_ number: Int) { print(number) } } }
extension Outer.Inner { func back(animated: Bool = true) {} }
'''
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'Facts.swift'; p.write_text(text)
            facts = Source(tmp).syntax('Facts.swift')['nodes']
            methods = [n['value'] for n in facts if n['kind'] == 'function']
            self.assertEqual(['Outer', 'Inner'], methods[0]['owners'])
            self.assertEqual(['Outer.Inner'], methods[2]['owners'])
            self.assertEqual('to', methods[0]['parameters'][0]['first_name'])
            self.assertEqual('_', methods[1]['parameters'][0]['first_name'])
            for method in methods:
                span = method['body']
                self.assertEqual(span['text'], text.encode()[span['start_utf8']:span['end_utf8']].decode())


if __name__ == '__main__':
    unittest.main()
