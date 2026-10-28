"""Neutral compiler/ownership contracts. Fixtures are not device evidence."""
from __future__ import annotations

import copy
import hashlib
import json
import io
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from contextlib import redirect_stdout, redirect_stderr
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'evaluations'))
from hmigbot_ios.apple_tools import environment
from hmigbot_ios.core import write_json, read_json
from hmigbot_ios152 import native_canonical as C
from hmigbot_ios152.native_semantics import constructor_declarations, verify_binding
from hmigbot_ios152.source import Source
from test_native_canonical import Fixture


class SystemOwnershipTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='native-system43-fixture-')
        self.root = Path(self.temp.name)
        self.info, self.env = environment()

    def tearDown(self):
        self.temp.cleanup()

    def fixture(self, code=None, *, extra_args=()):
        root = self.root / 'Source'; root.mkdir(exist_ok=True)
        path = root / 'Neutral.swift'
        path.write_text(code or '''import SwiftUI
import Charts
struct HomeView: View {
 var body: some View { ShareLink("Observed share", item: "Neutral value") }
}
''')
        source = Source(root)
        capture = self.root / 'captured'; capture.mkdir(exist_ok=True)
        file_list = capture / 'Neutral.SwiftFileList'; file_list.write_text(str(path) + '\n')
        context = {'toolchain': self.info, 'swiftc': self.info['swiftc'],
                   'arguments': ['-target', 'arm64-apple-ios17.0', '-sdk', self.info['sdk'],
                                 '-swift-version', '5', *extra_args]}
        write_json(capture / 'provider/0/request.json', {'files': [{'path': path.name}], 'compiler_context': context})
        tree = {'source_platform': 'ios', 'source': {'platform': 'ios', 'ios_root': str(root)},
                'pages': [{'id': 'HomeView', 'fq_class': 'HomeView', 'ios_file': 'Neutral.swift'}],
                'fragments': [], 'dialogs': []}
        with patch.object(C, '_blackbox_source', return_value=source):
            index = C.NativeTriggerIndex(tree, self.root, C.InputGuard())
        source.selection = {'source_membership': [{'path': path.name, 'targets': ['Neutral']} ]}
        source.view = SimpleNamespace(root=capture, artifact={
            'inputs': {'provider/0/request.json': C.sha(capture / 'provider/0/request.json')},
            'settings_targets': {'Neutral': {'PRODUCT_MODULE_NAME': 'Neutral'}},
            'compiler_argument_checks': [{'module': 'Neutral', 'compiler_arguments': [[self.info['swiftc'], '@' + str(file_list)]]}]},
            text=lambda name: (root / name).read_text(), includes=lambda name: name in source.files)
        meta = self.root / 'parent-run.json'
        write_json(meta, {'node': 'HomeView', 'source_sha256': index.facts['source_sha']})
        manifest = {'native_run_meta': str(meta), 'native_run_meta_sha256': C.sha(meta)}
        discovery = {'key': 'synthetic-share', 'external_system_ui': True,
                     'trigger_text': 'Observed share', 'trigger_resource_id': '',
                     'landing_ability': 'ObservedSystemSurface',
                     'source_anchor': {'file': 'Neutral.swift', 'line': 4}}
        return source, tree, index, manifest, discovery

    def classify(self, code=None, *, extra_args=(), edit=None):
        source, tree, index, manifest, discovery = self.fixture(code, extra_args=extra_args)
        if edit:
            edit(source, tree, manifest, discovery)
        return index.classify(discovery, tree['pages'][0], manifest)

    def test_real_sdk_imports_and_current_callee_are_proven(self):
        result = self.classify()
        self.assertEqual(result['destination_ownership'], 'system')
        self.assertFalse(result['runtime_verified'])
        self.assertNotIn('replay_annotation', result)
        proof = result['evidence'][-1]
        self.assertEqual((proof['typecheck_exit'], proof['ast_exit']), (0, 0))
        self.assertTrue(proof['declaration'].startswith('SwiftUI.(file).ShareLink'))
        self.assertTrue(proof['loaded_module_sha256'])

    def test_qualified_callee_and_legacy_relocated_anchor(self):
        code = '''import SwiftUI
struct HomeView: View {
 var body: some View { SwiftUI.ShareLink("Observed share", item: "Neutral value") }
}
'''
        result = self.classify(code, edit=lambda s,t,m,d: d.update(source_anchor='Neutral.swift:900 old API hint'))
        self.assertEqual(result['destination_ownership'], 'system')
        self.assertTrue(result['evidence'][0]['anchor_relocated'])

    def test_real_local_constructor_shadow_is_not_system_owned(self):
        result = self.classify('''import SwiftUI
struct ShareLink: View {
 init(_ name: String, item: String) {}
 var body: some View { Text("An app component") }
}
struct HomeView: View {
 var body: some View { ShareLink("Observed share", item: "Neutral value") }
}
''')
        self.assertEqual(result['classification'], 'unknown')
        self.assertNotIn('destination_ownership', result)

    def test_real_other_module_declaration_cannot_be_mistaken_for_sdk(self):
        other = self.root / 'Other.swift'
        other.write_text('''import SwiftUI
public struct ShareLink: View {
 public init(_ title: String, item: String) {}
 public var body: some View { Text("Other module") }
}
''')
        args = [self.info['swiftc'], '-emit-module', '-parse-as-library', '-module-name', 'Other',
                '-sdk', self.info['sdk'], '-target', 'arm64-apple-ios17.0', str(other),
                '-o', str(self.root / 'Other.swiftmodule')]
        p = subprocess.run(args, env=self.env, capture_output=True, text=True, timeout=60)
        self.assertEqual(p.returncode, 0, p.stderr)
        result = self.classify('''import SwiftUI
import Other
struct HomeView: View {
 var body: some View { ShareLink("Observed share", item: "Neutral value") }
}
''', extra_args=['-I', str(self.root)])
        # Unsupported/custom APIs take the original app path, never suppression.
        self.assertNotIn('destination_ownership', result)

    def test_false_system_flag_on_app_button_keeps_original_static_classification(self):
        result = self.classify('''import SwiftUI
struct HomeView: View {
 var body: some View { Button("Observed share") {} }
}
''')
        self.assertEqual(result['classification'], 'static')
        self.assertNotIn('destination_ownership', result)

    def test_stale_source_and_wrong_parent_context_leave_binding_debt(self):
        for change in [lambda s,t,m,d: d['source_anchor'].update(sha256='bad'),
                       lambda s,t,m,d: m.update(native_run_meta_sha256='bad'),
                       lambda s,t,m,d: t['pages'][0].update(ios_file='Other.swift')]:
            with self.subTest(change=change):
                result = self.classify(edit=change)
                self.assertEqual(result['classification'], 'unknown')

    def test_duplicate_calls_and_nested_control_are_not_suppressed(self):
        for body in [
            'VStack { ShareLink("Observed share", item: "A"); ShareLink("Observed share", item: "B") }',
            'ShareLink(item: "A") { Button("Observed share") {} }']:
            result = self.classify('import SwiftUI\nstruct HomeView: View { var body: some View { ' + body + ' } }\n')
            self.assertEqual(result['classification'], 'unknown')

    def test_missing_real_module_and_changed_file_list_are_unknown(self):
        result = self.classify('''import SwiftUI
import MissingSyntheticModule
struct HomeView: View { var body: some View { ShareLink("Observed share", item: "A") } }
''')
        self.assertEqual(result['classification'], 'unknown')
        result = self.classify(edit=lambda s,t,m,d: (self.root / 'captured/Neutral.SwiftFileList').write_text(''))
        self.assertEqual(result['classification'], 'unknown')

    def test_builder_expansion_is_deduplicated_but_conflicting_constructors_reject(self):
        row = '''(call_expr location=/P.swift:3:5
  (constructor_ref_call_expr
    (declref_expr implicit location=/P.swift:3:5 range=[] decl="SwiftUI.(file).ShareLink.init(item:)")))
(declref_expr location=/P.swift:3:5 range=[] decl="App.(file).builderValue")
'''
        self.assertEqual(constructor_declarations(row + row, '/P.swift', 3, 5),
                         {'SwiftUI.(file).ShareLink.init(item:)'})
        self.assertEqual(len(constructor_declarations(row + row.replace('SwiftUI.(file)', 'Other.(file)'), '/P.swift', 3, 5)), 2)

    def test_published_binding_invalidates_changed_generated_or_imported_inputs(self):
        result = self.classify()
        proof = result['evidence'][-1]
        verify_binding(proof)
        Path(proof['swift_file_list']).write_text('changed synthetic build membership')
        with self.assertRaisesRegex(Exception, 'dependency changed'):
            verify_binding(proof)

    @unittest.skipUnless(os.environ.get('HMIGBOT_TEST_ORIGINAL_VISUAL_ENGINE'), 'isolated original core required')
    def test_original_materializer_preserves_behavior_and_only_prunes_unfrozen_system_variant(self):
        source, tree, index, header, discovery = self.fixture()
        fixture = Fixture(self.root / 'project', names=('HomeView',))
        original = read_json(fixture.tree)
        original['source'] = tree['source']
        original['native_source_sha256'] = index.facts['source_sha']
        original['native_source_root'] = str(source.root)
        parent = original['pages'][0]
        parent.update(tree['pages'][0])
        parent['functional_checks'] = [{'name': 'Existing check', 'ios_trusted': False}]
        variant, edge, extra = C._native_variant(parent, discovery)
        parent['navigation'] = {'outbound': [edge]}
        parent['extras_variants'] = [extra]
        original['pages'].append(variant)
        write_json(fixture.tree, original)
        directory = fixture.root / 'spec/visual-verify/blackbox_discoveries'
        manifest = directory / 'HomeView__manifest.json'
        entries = [{'trigger_text': 'Observed share', 'outcome': 'overlay',
                    'before': {'png': 'synthetic-before'}, 'after': {'png': 'synthetic-after'},
                    'recovery': 'synthetic close action'}]
        write_json(manifest, {**header, 'parent_page_id': 'HomeView', 'trip_id': fixture.trip,
                              'discoveries': [discovery], 'behavior_ledger': entries})
        identity = hashlib.sha256(json.dumps({'manifest': str(manifest.resolve()), 'key': discovery['key'],
                                  'parent': 'HomeView', 'trip': fixture.trip}, sort_keys=True).encode()).hexdigest()
        unrelated = {'id': 'unrelated-debt', 'type': 'native_blackbox_capture', 'applied': False}
        write_json(fixture.ew / 'pending_bindings.json', [unrelated,
            {'id': identity, 'type': 'native_blackbox_capture', 'applied': False}])
        engine = Path(os.environ['HMIGBOT_TEST_ORIGINAL_VISUAL_ENGINE']).resolve()
        def execute(command, args, scripts, **kwargs):
            return subprocess.run([str(engine), command, *map(str, args)], capture_output=True,
                                  text=True, timeout=60, env={**os.environ, 'ARKTS_SKILL_DIR': str(engine.parents[3])})
        args = ['--factree', str(fixture.tree), '--discoveries-dir', str(directory)]
        with patch.object(C, 'NativeTriggerIndex', return_value=index), patch.object(C, '_core', side_effect=execute):
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                self.assertEqual(C.materialize_native_cli(args, ROOT / 'skills/arkts-visual-verify/scripts'), 20)
        after = read_json(fixture.tree)
        self.assertEqual([p['id'] for p in after['pages']], ['HomeView'])
        self.assertEqual(after['pages'][0]['functional_checks'], parent['functional_checks'])
        self.assertEqual(after['pages'][0]['blackbox_behavior'][fixture.trip], entries)
        self.assertEqual(read_json(fixture.ew / 'pending_bindings.json'), [unrelated])
        self.assertFalse(fixture.baseline.exists())
        # The real published receipt must carry the proof consumed by the
        # same public readiness entry used in finalization, not only a helper.
        receipt = C._verify_blackbox_receipt(after, fixture.root)
        row = receipt['outputs']['classifications'][0]
        self.assertEqual(row['destination_ownership'], 'system')
        self.assertEqual(row['evidence'][-1]['kind'], 'Apple real Source typecheck and AST binding')
        file_list = Path(row['evidence'][-1]['swift_file_list'])
        original_list = file_list.read_bytes()
        file_list.write_text('changed synthetic build membership')
        with self.assertRaises(C.BindingError) as stale:
            C.data_cli('check_blackbox_evidence', [], ROOT / 'skills/arkts-visual-verify/scripts',
                       project_override=fixture.root)
        self.assertEqual(stale.exception.code, 22)
        self.assertIn('dependency changed', str(stale.exception))
        file_list.write_bytes(original_list)
        # Accepted/frozen evidence cannot be silently removed.
        original['pages'][-1]['screenshots'] = {fixture.trip: {'synthetic': True}}
        write_json(fixture.tree, original)
        before = fixture.tree.read_bytes()
        with patch.object(C, 'NativeTriggerIndex', return_value=index):
            with self.assertRaises(C.BindingError) as error:
                C.materialize_native_cli(args, ROOT / 'skills/arkts-visual-verify/scripts')
        self.assertEqual(error.exception.code, 22)
        self.assertEqual(fixture.tree.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
