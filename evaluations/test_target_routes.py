"""Official ETS target facts checked against original compiled inline oracles."""
from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from hmigbot_ios152.target_routes import (TargetRouteError, supplement_target,
    validate_receipt, validate_target_snapshot)
from hmigbot_ios152.native_routes_entry import compiled

SCRIPTS = ROOT / 'skills/arkts-router-verify/scripts'
PARSER = Path('/Applications/DevEco-Studio.app/Contents/sdk/default/openharmony/ets/build-tools/ets-loader/node_modules/typescript')
NODE = Path('/Applications/DevEco-Studio.app/Contents/tools/node/bin/node')


def wire(value):
    if isinstance(value, dict):
        return {key: wire(item) for key, item in value.items()
                if key not in {'native_provenance', 'supplement', 'original_engine_row', 'original_engine_control', 'hmos_root'}}
    if isinstance(value, list):
        return [wire(item) for item in value]
    return value


@unittest.skipUnless(PARSER.is_dir() and NODE.is_file(), 'requires selected official DevEco ETS SDK')
class TargetRoutes(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='target-route-sdk-')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.env = patch.dict(os.environ, {'HMIGBOT_ETS_PARSER': str(PARSER), 'HMIGBOT_NODE': str(NODE), 'PYTHONDONTWRITEBYTECODE': '1'})
        self.env.start()
        self.addCleanup(self.env.stop)
        self.index = 0

    def fixture(self, members='', build="Text('Empty')", extra=None):
        self.index += 1
        root = self.base / ('case' + str(self.index))
        (root / '.agents').mkdir(parents=True)
        pages = root / 'entry/src/main/ets/pages'
        pages.mkdir(parents=True)
        names = ['FirstPage', 'SecondPage', 'ThirdPage', 'DetailPage', 'SheetPage']
        imports = []
        for name in names:
            (pages / (name + '.ets')).write_text('@Component export struct ' + name + "{build(){Text('Actual body')}}")
            imports.append("import {" + name + "} from './" + name + "'")
        (pages / 'Root.ets').write_text('\n'.join(imports) + '\n@Entry @Component struct Root {' + members + ' build(){' + build + '} }\n')
        for relative, content in (extra or {}).items():
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
        return root

    def extract(self, root):
        out = root / 'spec/verify/route'
        result = compiled(SCRIPTS, 'hmos_extract', ['--hmos-root', str(root), '--out-dir', str(out)],
                          {'ROUTE_VERIFY_ROOT': str(root), 'ROUTE_VERIFY_OUT': str(out)})
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return json.loads((out / 'actual_nav.json').read_text())

    def compare(self, builder_root, inline_root):
        original = self.extract(builder_root)
        frozen = copy.deepcopy(original)
        actual, receipt = supplement_target(builder_root, original)
        expected = self.extract(inline_root)
        self.assertEqual(original, frozen, 'supplement mutated the original graph')
        self.assertEqual(wire(actual), wire(expected))
        self.assertTrue(validate_target_snapshot(builder_root, receipt, actual))
        return original, actual, receipt

    def tabs(self, first='FirstPage()', second='SecondPage()'):
        return "Tabs(){TabContent(){" + first + "}.tabBar('First');TabContent(){" + second + "}.tabBar('Second')}"

    def test_direct_tabs_keep_original_bytes_and_no_duplicate(self):
        root = self.fixture(build=self.tabs())
        original = self.extract(root)
        actual, receipt = supplement_target(root, original)
        self.assertEqual(actual, original)
        self.assertEqual(receipt['added_edges'], [])
        self.assertEqual(len(receipt['facts']['tabGroups']), 1)

    def test_zero_argument_builders_equal_original_inline(self):
        builder = self.fixture('@Builder first(){FirstPage()} @Builder second(){SecondPage()}', self.tabs('this.first()', 'this.second()'))
        inline = self.fixture(build=self.tabs())
        original, actual, receipt = self.compare(builder, inline)
        self.assertEqual(original['tab_groups'], [])
        self.assertEqual(len(receipt['added_edges']), 2)
        for edge in receipt['added_edges']:
            self.assertEqual(edge['supplement'], 'ets_ast')
            self.assertTrue(any(link['kind'] == 'builder-call' for link in edge['native_provenance']['chain']))

    def test_same_target_two_tabs_keeps_original_distinct_call_sites(self):
        builder = self.fixture('@Builder first(){FirstPage()}', self.tabs('this.first()', 'this.first()'))
        inline = self.fixture(build=self.tabs('FirstPage()', 'FirstPage()'))
        _, actual, receipt = self.compare(builder, inline)
        self.assertEqual(len(actual['edges']), 2)
        spans = [edge['native_provenance']['tab_content']['start_utf16'] for edge in receipt['added_tab_edges']]
        self.assertEqual(len(set(spans)), 2)

    def test_two_separate_identical_tab_groups_keep_original_multiplicity(self):
        builder = self.fixture('@Builder first(){FirstPage()}', 'Column(){' + self.tabs('this.first()') + ';' + self.tabs('this.first()') + '}')
        inline = self.fixture(build='Column(){' + self.tabs() + ';' + self.tabs() + '}')
        _, actual, _ = self.compare(builder, inline)
        self.assertEqual(len(actual['tab_groups']), 2)
        self.assertEqual(len(actual['edges']), 4)

    def test_navigation_and_multilayer_tabs_builder_equal_inline(self):
        body = self.tabs('Navigation(){this.first()}', 'Navigation(){this.second()}')
        root = self.fixture('@Builder first(){this.inner()} @Builder inner(){FirstPage()} @Builder second(){SecondPage()} @Builder allTabs(){' + body + '}', 'this.allTabs()')
        inline = self.fixture(build=self.tabs('Navigation(){FirstPage()}', 'Navigation(){SecondPage()}'))
        _, actual, receipt = self.compare(root, inline)
        self.assertEqual(len(actual['edges']), 2)
        self.assertTrue(any(link.get('builder') == 'allTabs' for link in receipt['added_edges'][0]['native_provenance']['chain']))

    def test_condition_matches_original_first_syntactic_branch(self):
        root = self.fixture('@State flag:boolean=true;@Builder first(){if(this.flag){FirstPage()}else{ThirdPage()}}', self.tabs('this.first()'))
        inline = self.fixture('@State flag:boolean=true;', self.tabs('if(this.flag){FirstPage()}else{ThirdPage()}'))
        _, actual, receipt = self.compare(root, inline)
        self.assertEqual(actual['tab_groups'][0]['tabs'], ['FirstPage', 'SecondPage'])
        self.assertTrue(any('not runtime branch selection' in row['reason'] for row in receipt['unknowns']))

    def test_unreferenced_builder_only_diagnostic_no_added_edge(self):
        root = self.fixture('@Builder unused(){' + self.tabs() + '}')
        original = self.extract(root)
        actual, receipt = supplement_target(root, original)
        self.assertEqual(actual, original)
        self.assertEqual(receipt['added_edges'], [])
        self.assertTrue(any(row['builder'] == 'unused' for row in receipt['dead_builders']))

    def assert_unknown_no_added(self, members, first, reason):
        root = self.fixture(members, self.tabs(first))
        original = self.extract(root)
        _, receipt = supplement_target(root, original)
        self.assertEqual(receipt['added_edges'], [])
        self.assertTrue(any(reason in row['reason'] for row in receipt['unknowns']), receipt['unknowns'])

    def test_parameterized_builder_unknown(self):
        self.assert_unknown_no_added('@Builder first(value:number){FirstPage()}', 'this.first(1)', 'parameterized Builder')

    def test_recursive_builder_unknown_even_before_recursive_call(self):
        self.assert_unknown_no_added('@Builder first(){FirstPage();this.first()}', 'this.first()', 'recursive Builder')

    def test_foreach_builder_unknown(self):
        self.assert_unknown_no_added('@Builder first(){ForEach([1,2],()=>{FirstPage()})}', 'this.first()', 'dynamic ForEach')

    def test_builderparam_unknown(self):
        self.assert_unknown_no_added('@BuilderParam first:()=>void;', 'this.first()', 'BuilderParam')

    def test_missing_component_unknown(self):
        self.assert_unknown_no_added('@Builder first(){MissingPage()}', 'this.first()', 'no supported unique')

    def test_ambiguous_import_is_not_guessed(self):
        root = self.fixture('@Builder first(){FirstPage()}', self.tabs('this.first()'))
        pages = root / 'entry/src/main/ets/pages'
        (pages / 'Duplicate.ets').write_text("@Component export struct FirstPage{build(){Text('Different')}}")
        path = pages / 'Root.ets'
        path.write_text("import {FirstPage} from './Duplicate'\n" + path.read_text())
        _, receipt = supplement_target(root, self.extract(root))
        self.assertEqual(receipt['added_edges'], [])
        self.assertTrue(any('ambiguous' in row['reason'] for row in receipt['unknowns']))

    def test_official_syntax_error_is_explicit_failure(self):
        root = self.fixture(build=self.tabs())
        path = root / 'entry/src/main/ets/pages/Root.ets'
        path.write_text(path.read_text() + '\nstruct Broken { build( }')
        with self.assertRaisesRegex(TargetRouteError, 'parse diagnostics'):
            supplement_target(root, {'tab_groups': [], 'edges': [], 'stats': {}, 'pages': {}})

    def test_overlay_builder_equals_original_literal_closure(self):
        members = '@State shown:boolean=false;'
        builder = self.fixture(members + '@Builder sheet(){SheetPage()}', "Column(){Button('Open').onClick(()=>{this.shown=true})}.bindSheet(this.shown,this.sheet)")
        inline = self.fixture(members, "Column(){Button('Open').onClick(()=>{this.shown=true})}.bindSheet(this.shown,()=>{SheetPage()})")
        original, _, receipt = self.compare(builder, inline)
        self.assertIsNone(original['edges'][0]['target'])
        row = receipt['resolved_overlay_rows'][0]
        self.assertEqual(row['original_engine_row'], original['edges'][0])
        self.assertEqual(row['target'], 'SheetPage')

    def test_content_cover_builder_equals_original_literal_closure(self):
        members = '@State shown:boolean=false;'
        builder = self.fixture(members + '@Builder cover(){SheetPage()}', "Column(){Text('Body')}.bindContentCover(this.shown,this.cover)")
        inline = self.fixture(members, "Column(){Text('Body')}.bindContentCover(this.shown,()=>{SheetPage()})")
        self.compare(builder, inline)

    def test_conditional_overlay_stays_unknown(self):
        root = self.fixture('@State shown:boolean=false;@Builder sheet(){if(this.shown){SheetPage()}else{FirstPage()}}', "Column(){Text('Body')}.bindSheet(this.shown,this.sheet)")
        original = self.extract(root)
        actual, receipt = supplement_target(root, original)
        self.assertEqual(actual, original)
        self.assertTrue(any('conditional overlay' in row['reason'] for row in receipt['unknowns']))

    def push_fixture(self, optional=True, target="'DetailPage'", registrations=1, fake_stack=False):
        members = ('stack:NavPathStack|undefined=new NavPathStack();' if not fake_stack else "stack:FakeStack|undefined=new FakeStack();")
        members += "@Builder pageMap(name:string){if(name==='DetailPage'){DetailPage()}}"
        if registrations == 2:
            members += "@Builder otherMap(name:string){if(name==='DetailPage'){DetailPage()}}"
        dot = '?.' if optional else '.'
        body = "Navigation(this.stack){Button('Open').onClick(()=>{this.stack" + dot + 'pushPathByName(' + target + ',{})})}'
        if registrations:
            body += '.navDestination(this.pageMap)'
        if registrations == 2:
            body += '.navDestination(this.otherMap)'
        root = self.fixture(members, body)
        if fake_stack:
            path = root / 'entry/src/main/ets/pages/Root.ets'
            path.write_text('class FakeStack{pushPathByName(name:string,param:object):void{}}\n' + path.read_text())
        return root

    def test_optional_push_equals_original_nonoptional(self):
        original, actual, receipt = self.compare(self.push_fixture(), self.push_fixture(optional=False))
        self.assertEqual(original['edges'], [])
        self.assertFalse(actual['edges'][0]['registered'], 'preserve the original surface wire semantics')
        self.assertEqual(receipt['added_optional_pushes'][0]['native_provenance']['registration']['target'], 'DetailPage')

    def test_optional_dynamic_or_missing_or_ambiguous_registration_unknown(self):
        for root in [self.push_fixture(target='this.routeName'), self.push_fixture(registrations=0), self.push_fixture(registrations=2), self.push_fixture(fake_stack=True)]:
            with self.subTest(root=root.name):
                actual, receipt = supplement_target(root, self.extract(root))
                self.assertEqual(receipt['added_optional_pushes'], [])
                self.assertTrue(receipt['unknowns'])

    def test_snapshot_rejects_edited_added_deleted_input_and_output(self):
        root = self.fixture('@Builder first(){FirstPage()}', self.tabs('this.first()'))
        actual, receipt = supplement_target(root, self.extract(root))
        self.assertTrue(validate_receipt(root, receipt))
        changed = copy.deepcopy(actual)
        changed['edges'][0]['target'] = 'WrongPage'
        with self.assertRaisesRegex(TargetRouteError, 'artifact changed'):
            validate_target_snapshot(root, receipt, changed)
        path = root / 'entry/src/main/ets/pages/Root.ets'
        saved = path.read_bytes()
        path.write_bytes(saved + b'\n// changed')
        with self.assertRaisesRegex(TargetRouteError, 'stale'):
            validate_receipt(root, receipt)
        path.write_bytes(saved)
        new = path.with_name('NewPage.ets')
        new.write_text("@Component struct NewPage{build(){Text('New')}}")
        with self.assertRaisesRegex(TargetRouteError, 'stale'):
            validate_receipt(root, receipt)
        new.unlink()
        path.unlink()
        with self.assertRaisesRegex(TargetRouteError, 'stale'):
            validate_receipt(root, receipt)

    def test_snapshot_rejects_changed_receipt_tool_identity(self):
        root = self.fixture(build=self.tabs())
        _, receipt = supplement_target(root, self.extract(root))
        receipt['snapshot']['tool_files'][str(ROOT / 'src/hmigbot_ios152/target_routes_sdk.cjs')] = '0' * 64
        with self.assertRaisesRegex(TargetRouteError, 'stale'):
            validate_receipt(root, receipt)

    def test_receipt_revalidation_is_repeatably_read_only(self):
        root = self.fixture('@Builder first(){FirstPage()}', self.tabs('this.first()'))
        actual, receipt = supplement_target(root, self.extract(root))
        def clocks():
            return {str(path.relative_to(root)): (path.stat().st_mtime_ns,
                hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None)
                for path in [root, *root.rglob('*')]}
        before = clocks()
        self.assertTrue(validate_receipt(root, receipt))
        self.assertTrue(validate_target_snapshot(root, receipt, actual))
        self.assertEqual(clocks(), before)

    def test_missing_sdk_never_becomes_empty_success(self):
        root = self.fixture(build=self.tabs())
        with patch.dict(os.environ, {'HMIGBOT_ETS_PARSER': '/missing/ets-loader/node_modules/typescript'}):
            with self.assertRaisesRegex(TargetRouteError, 'missing or ambiguous'):
                supplement_target(root, self.extract(root))

    def test_chain_source_span_and_hash_are_real(self):
        root = self.fixture('@Builder first(){FirstPage()}', self.tabs('this.first()'))
        _, receipt = supplement_target(root, self.extract(root))
        for edge in receipt['added_tab_edges']:
            for link in edge['native_provenance']['chain']:
                raw = (root / link['file']).read_bytes()
                self.assertEqual(hashlib.sha256(raw).hexdigest(), link['file_sha256'])
                text = raw.decode('utf-8').encode('utf-16-le')
                fragment = text[link['start_utf16'] * 2:link['end_utf16'] * 2].decode('utf-16-le')
                self.assertTrue(fragment)


if __name__ == '__main__':
    unittest.main()
