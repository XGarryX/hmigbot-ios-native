"""Original 1.5.2 wire is the oracle, including multiline control bindings."""
import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from . import test_target_routes as fixtures
from hmigbot_ios152.target_routes import supplement_target, target_inputs
from hmigbot_ios152.target_route_oracle import _apply_tokens
from hmigbot_ios152 import target_route_oracle as oracle


class OriginalRouteOracle(unittest.TestCase):
    setUp = fixtures.TargetRoutes.setUp
    fixture = fixtures.TargetRoutes.fixture
    extract = fixtures.TargetRoutes.extract

    def navigation(self, optional=True, crlf=False, alias=False):
        route = 'DetailAlias' if alias else 'DetailPage'
        members = ("@State stack:NavPathStack=new NavPathStack();\n"
            " @Builder map(name:string){if(name==='" + route + "'){DetailPage()}}\n"
            " open():void{\n"
            "  // 中文😀\n"
            "  this.stack" + ('?.' if optional else '.') + "pushPathByName('" + route + "',null);\n }\n")
        body = "\nNavigation(this.stack){\n Button('Open')\n .onClick(()=>{\n this.open();\n })\n}.navDestination(this.map)\n"
        root = self.fixture(members, body)
        if crlf:
            for path in root.rglob('*.ets'):
                path.write_bytes(b'\xef\xbb\xbf' + path.read_bytes().replace(b'\n', b'\r\n'))
        return root

    def measured(self, **kwargs):
        root = self.navigation(**kwargs)
        original = self.extract(root)
        raw = (root / 'spec/verify/route/actual_nav.json').read_bytes()
        frozen = {name: (root / name).read_bytes() for name in target_inputs(root)}
        actual, receipt = supplement_target(root, original, original_bytes=raw)
        expected_root = self.navigation(optional=False, **{k: v for k, v in kwargs.items() if k != 'optional'})
        expected = self.extract(expected_root)
        self.assertEqual(fixtures.wire(actual), fixtures.wire(expected), receipt['merge_unknowns'])
        self.assertEqual(receipt['optional_measurement']['status'], 'complete', receipt['merge_unknowns'])
        self.assertEqual(receipt['optional_measurement']['real_raw_sha256'], receipt['optional_measurement']['baseline_normalised_sha256'])
        self.assertEqual({name: (root / name).read_bytes() for name in frozen}, frozen)
        return actual, receipt

    def test_multiline_indirect_uses_original_onclick_line_and_stats(self):
        actual, receipt = self.measured()
        edge = receipt['added_optional_pushes'][0]
        self.assertEqual(edge['control_type'], 'Button')
        self.assertEqual(edge['chain'], '→open')
        self.assertEqual(edge['line'], edge['native_provenance']['onclick_binding']['line'])
        self.assertEqual(actual['stats']['bound_to_nav'], 1)
        self.assertTrue(receipt['optional_measurement']['control_changes'])

    def test_utf16_emoji_bom_crlf_preserves_real_bytes_and_lines(self):
        self.measured(crlf=True)

    def test_alias_literal_keeps_original_wire_and_resolved_component_evidence(self):
        _, receipt = self.measured(alias=True)
        edge = receipt['added_optional_pushes'][0]
        self.assertEqual(edge['target'], 'DetailAlias')
        self.assertEqual(edge['native_provenance']['target_match'], 'push_literal')
        self.assertEqual(edge['native_provenance']['registration']['target'], 'DetailPage')

    def test_unreproduced_raw_graph_stays_unknown_no_partial_merge(self):
        root = self.navigation()
        original = self.extract(root)
        raw = (root / 'spec/verify/route/actual_nav.json').read_bytes() + b'\n'
        actual, receipt = supplement_target(root, original, original_bytes=raw)
        self.assertEqual(actual, original)
        self.assertEqual(receipt['optional_measurement']['status'], 'merge_unknown')
        self.assertFalse(receipt['added_optional_pushes'])

    def test_changed_token_fails_before_any_private_source_edit(self):
        root = self.navigation()
        _, receipt = supplement_target(root, self.extract(root))
        tokens = copy.deepcopy(receipt['optional_measurement']['tokens'])
        tokens[0]['start_utf16'] += 1
        with self.assertRaisesRegex(ValueError, 'span'):
            _apply_tokens(root, root, tokens, target_inputs(root))

    def test_optional_call_form_remains_explicit_unknown(self):
        root = self.navigation()
        path = root / 'entry/src/main/ets/pages/Root.ets'
        path.write_text(path.read_text().replace('stack?.pushPathByName(', 'stack?.pushPathByName?.('))
        original = self.extract(root)
        actual, receipt = supplement_target(root, original)
        self.assertEqual(actual, original)
        self.assertTrue(any('optional_call' in row['reason'] for row in receipt['merge_unknowns']))

    def test_unexplained_bound_change_rejects_entire_batch(self):
        root = self.navigation()
        path = root / 'entry/src/main/ets/pages/Root.ets'
        path.write_text(path.read_text().replace("Button('Open')", "Button('Idle').onClick(()=>{})\n Button('Open')"))
        original = self.extract(root)
        measure = oracle._measure
        def inconsistent(scripts, mirror, out, argv=()):
            raw = measure(scripts, mirror, out, argv)
            if Path(out).name == 'modified':
                data = json.loads(raw)
                idle = next(control for control in data['pages']['Root']['controls'] if control['text'] == 'Idle')
                self.assertFalse(idle['bound'])
                idle['bound'] = True
                return json.dumps(data, ensure_ascii=False, indent=2).encode()
            return raw
        with patch.object(oracle, '_measure', inconsistent):
            actual, receipt = supplement_target(root, original)
        self.assertEqual(actual, original)
        self.assertEqual(receipt['optional_measurement']['status'], 'merge_unknown')
        self.assertIn('no new navigation evidence', receipt['merge_unknowns'][0]['reason'])


if __name__ == '__main__':
    unittest.main()
