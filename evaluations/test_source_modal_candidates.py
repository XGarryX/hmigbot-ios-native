"""Regressions from neutral SwiftSyntax input, independent of migration specs."""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from hmigbot_ios152.source import Source
from hmigbot_ios152.native_routes import analyze, expected_nav, worklist, apply_verdicts
from hmigbot_ios.core import MigrationError


class ModalCandidates(unittest.TestCase):
    def facts(self, text):
        with tempfile.TemporaryDirectory(prefix='native-modal-candidates-') as folder:
            root = Path(folder)
            (root / 'Input.swift').write_text(text)
            return analyze(Source(root))

    def test_alert_and_confirmation_preserve_real_binding_and_trigger(self):
        for api in ('alert', 'confirmationDialog'):
            with self.subTest(api=api):
                f = self.facts('import SwiftUI\nstruct Root:View { @State var showing=false; '
                    'var body:some View{ VStack{Button("Ask"){showing=true}}.' + api +
                    '("Question",isPresented:$showing){Button("Confirm"){showing=false}} }}')
                route, = f['routes']
                self.assertEqual(route['state_binding'], '$showing')
                self.assertEqual(route['guard'], 'state:$showing')
                self.assertEqual(route['trigger_text'], 'Ask')
                self.assertIsNotNone(route['control_id'])
                self.assertIn('<closure>', route['method_key'])
                self.assertEqual(f['modals'][route['target']]['native_arguments'][1]['expression'], '$showing')

    def test_dynamic_binding_is_retained_without_inventing_a_trigger(self):
        for api in ('alert', 'confirmationDialog'):
            with self.subTest(api=api):
                f = self.facts('import SwiftUI\nstruct Root:View { var body:some View{Text("Body").' +
                    api + '("Question",isPresented:Binding(get:{false},set:{_ in})) {Button("OK") {}}}}')
                route, = f['routes']
                self.assertEqual(route['state_binding'], 'Binding(get:{false},set:{_ in})')
                self.assertEqual(route['guard'], 'state:' + route['state_binding'])
                self.assertIsNone(route['control_id'])
                self.assertIsNone(route['trigger_text'])

    def test_bindingless_legacy_alert_stays_unbound(self):
        f = self.facts('import SwiftUI\nstruct Root:View { var body:some View{Text("Body").alert("Question"){Button("OK") {}}}}')
        route, = f['routes']
        self.assertIsNone(route['state_binding'])
        self.assertEqual(route['guard'], 'none')

    def test_representable_prevents_false_unique_destination_without_page_inflation(self):
        for protocol in ('UIViewControllerRepresentable', 'UIViewRepresentable'):
            with self.subTest(protocol=protocol):
                implementation = ('func makeUIViewController(context:Context)->NativeHost{NativeHost()};'
                    'func updateUIViewController(_ controller:NativeHost,context:Context){}'
                    if protocol == 'UIViewControllerRepresentable' else
                    'func makeUIView(context:Context)->UIView{UIView()};'
                    'func updateUIView(_ view:UIView,context:Context){}')
                f = self.facts('''import SwiftUI
import UIKit
struct Root:View{@State var show=false;var body:some View{Button("Open"){show=true}.fullScreenCover(isPresented:$show){VStack{Bridge();ActionControl(action:{show=false})}}}}
struct ActionControl:View{var action:()->Void;var body:some View{Button("Done"){action()}}}
struct Bridge:''' + protocol + ' {' + implementation + '''}
final class NativeHost:UIViewController{}
''')
                self.assertEqual({r['target'] for r in f['routes']}, {'Bridge', 'ActionControl'})
                self.assertTrue(all(r['declaration_only'] for r in f['routes']))
                self.assertNotIn('Bridge', {p['name'] for p in f['pages']})
                expected = expected_nav(f)
                pending = worklist(f, expected)
                self.assertGreater(pending['unique_methods'], 0)
                with self.assertRaises(MigrationError):
                    apply_verdicts(f, expected, pending, {})

    def test_real_single_view_presentation_is_unchanged(self):
        f = self.facts('import SwiftUI\nstruct Root:View{@State var show=false;var body:some View{Button("Open"){show=true}.sheet(isPresented:$show){Detail()}}}\nstruct Detail:View{var body:some View{Text("Detail")}}')
        route, = f['routes']
        self.assertEqual(route['target'], 'Detail')
        self.assertFalse(route['declaration_only'])


if __name__ == '__main__':
    unittest.main()
