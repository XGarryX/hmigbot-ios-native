"""Whole-wire oracles plus unsupported closure and original scan-scope facts."""
import copy
import os
import unittest

from evaluations import test_target_routes as fixtures
from hmigbot_ios152.target_routes import supplement_target


@unittest.skipUnless(fixtures.PARSER.is_dir() and fixtures.NODE.is_file(), 'requires selected official ETS SDK')
class ScopeCounterfacts(unittest.TestCase):
    setUp = fixtures.TargetRoutes.setUp
    fixture = fixtures.TargetRoutes.fixture
    extract = fixtures.TargetRoutes.extract
    tabs = fixtures.TargetRoutes.tabs

    def test_overlay_builder_referenced_only_inside_lambda_stays_unknown(self):
        root = self.fixture('@State shown:boolean=false; @Builder sheetContent(){SheetPage()}',
            "Column(){Button('Open').onClick(()=>{this.shown=true})}.bindSheet(this.shown,()=>{this.sheetContent()})")
        original = self.extract(root)
        original_overlay = [edge for edge in original['edges'] if edge['via'] == 'bindSheet']
        self.assertEqual(len(original_overlay), 1)
        self.assertIsNone(original_overlay[0]['target'])
        actual, receipt = supplement_target(root, original)
        self.assertEqual(actual, original)
        self.assertEqual(receipt['added_edges'], [])
        self.assertTrue(any(row['reason'] == 'Builder referenced outside supported render chain' for row in receipt['unknowns']))

    def test_tab_builder_referenced_only_inside_lambda_stays_unknown(self):
        root = self.fixture('@Builder firstContent(){FirstPage()}',
            self.tabs('(() => {this.firstContent()})()'))
        original = self.extract(root)
        actual, receipt = supplement_target(root, original)
        self.assertEqual(actual, original)
        self.assertEqual(receipt['added_edges'], [])
        self.assertTrue(any(row['reason'] == 'Builder referenced outside supported render chain' for row in receipt['unknowns']))

    def test_original_and_supplement_share_test_directory_scan_scope(self):
        root = self.fixture()
        for folder, owner in [('ohosTest', 'OfficialTestScope'), ('test', 'LocalTestScope')]:
            path = root / ('entry/src/' + folder + '/ets/test/Scope.ets')
            path.parent.mkdir(parents=True)
            path.write_text("import {FirstPage} from '../../../main/ets/pages/FirstPage'\n"
                "import {SecondPage} from '../../../main/ets/pages/SecondPage'\n"
                '@Component struct ' + owner + '{build(){' + self.tabs() + '}}\n')
        original = self.extract(root)
        self.assertEqual(original['tab_groups'], [])
        frozen = copy.deepcopy(original)
        actual, receipt = supplement_target(root, original)
        self.assertEqual(original, frozen)
        self.assertEqual(actual, original)
        self.assertEqual(receipt['facts']['tabGroups'], [])
        self.assertTrue(all(path.startswith('entry/src/main/ets/') for path in receipt['selected_files']))

    def test_main_nested_test_directories_keep_original_scope(self):
        root = self.fixture()
        folders = [('test', 'MainTestScope'), ('tests', 'MainTestsScope'),
                   ('docs', 'MainDocsScope'), ('design', 'MainDesignScope'),
                   ('plans', 'MainPlansScope'), ('spec', 'MainSpecScope')]
        for folder, owner in folders:
            path = root / ('entry/src/main/ets/' + folder + '/' + owner + '.ets')
            path.parent.mkdir(parents=True)
            path.write_text("import {FirstPage} from '../pages/FirstPage'\nimport {SecondPage} from '../pages/SecondPage'\n"
                '@Component struct ' + owner + '{build(){' + self.tabs() + '}}')
        original = self.extract(root)
        actual, receipt = supplement_target(root, original)
        self.assertEqual(actual, original)
        self.assertEqual({group['host'] for group in original['tab_groups']}, {owner for _, owner in folders})
        self.assertEqual(len(receipt['facts']['tabGroups']), len(folders))

    def test_other_layouts_do_not_become_supplement_hosts(self):
        root = self.fixture()
        for i, relative in enumerate(['library/src/main/ets/pages', 'feature/src/main/ets/pages',
                'src/main/ets/pages', 'entry/ets/pages', 'pages']):
            directory = root / relative
            directory.mkdir(parents=True)
            for child in ('ChildA', 'ChildB'):
                (directory / (child + '.ets')).write_text('@Component struct ' + child + "{build(){Text('Body')}}")
            (directory / ('OutsideHost' + str(i) + '.ets')).write_text("import {ChildA}from './ChildA'\nimport {ChildB}from './ChildB'\n"
                '@Component struct OutsideHost' + str(i) + "{build(){Tabs(){TabContent(){ChildA()}.tabBar('A');TabContent(){ChildB()}.tabBar('B')}}}")
        original = self.extract(root)
        actual, receipt = supplement_target(root, original)
        self.assertEqual(actual, original)
        self.assertEqual(actual['tab_groups'], [])
        self.assertEqual(receipt['facts']['tabGroups'], [])

    def test_missing_default_scope_matches_original_empty_result(self):
        root = self.fixture()
        (root / 'entry').rename(root / 'other-module')
        original = self.extract(root)
        actual, receipt = supplement_target(root, original)
        self.assertEqual(actual, original)
        self.assertEqual(actual['tab_groups'], [])
        self.assertEqual(receipt['scope_status'], 'default_scope_absent')
        self.assertEqual(receipt['selected_files'], {})

    def external_fixture(self, mode, wrapped):
        root = self.fixture()
        pages = root / 'entry/src/main/ets/pages'
        library = root / 'library/src/main/ets/pages'
        library.mkdir(parents=True)
        (library / 'OutsidePage.ets').write_text('@Component export struct OutsidePage {'
            '@BuilderParam content:()=>void=()=>{}; build(){Column(){Text("Library");this.content()}}}')
        relative = os.path.relpath(library / 'OutsidePage', pages).replace(os.sep, '/')
        imported = "import * as Library from '" + relative + "'" if mode == 'namespace' else \
            "import {OutsidePage" + (' as OutsideAlias' if mode == 'alias' else '') + "} from '" + relative + "'"
        first = 'Library.OutsidePage()' if mode == 'namespace' else 'OutsideAlias()' if mode == 'alias' else \
            'OutsidePage(){Text("Child")}' if mode == 'trailing' else 'OutsidePage()'
        prefix = '@Builder firstContent(){' + first + '}' if wrapped else ''
        (pages / 'Root.ets').write_text(imported + "\nimport {SecondPage}from './SecondPage'\n"
            '@Entry @Component struct Root{' + prefix + 'build(){' +
            self.tabs('this.firstContent()' if wrapped else first) + '}}')
        return root

    def test_external_named_alias_namespace_and_trailing_import_oracles(self):
        for mode in ('named', 'alias', 'namespace', 'trailing'):
            with self.subTest(mode=mode):
                builder, inline = self.external_fixture(mode, True), self.external_fixture(mode, False)
                original, expected = self.extract(builder), self.extract(inline)
                actual, receipt = supplement_target(builder, original)
                self.assertEqual(fixtures.wire(actual), fixtures.wire(expected))
                self.assertTrue(any('/library/' in path for path in receipt['snapshot']['context_files']))
                self.assertFalse(any(path.startswith('library/') for path in receipt['selected_files']))
                if mode == 'namespace':
                    self.assertEqual(actual['tab_groups'], [])
                    self.assertTrue(any('direct-identifier' in row['reason'] for row in receipt['unknowns']))
                elif mode == 'alias':
                    self.assertEqual(actual['tab_groups'][0]['tabs'][0], 'OutsideAlias')
                    self.assertEqual(receipt['added_tab_edges'][0]['native_provenance']['target_declaration']['declaration_name'], 'OutsidePage')

    def test_symlink_host_retains_original_without_supplement_or_stage_failure(self):
        root = self.fixture()
        library = root / 'library'
        library.mkdir()
        source = library / 'LinkedHost.ets'
        source.write_text("import {FirstPage}from '../entry/src/main/ets/pages/FirstPage'\n"
            "import {SecondPage}from '../entry/src/main/ets/pages/SecondPage'\n"
            '@Component struct LinkedHost{build(){' + self.tabs() + '}}')
        link = root / 'entry/src/main/ets/pages/LinkedHost.ets'
        link.symlink_to(source)
        original = self.extract(root)
        actual, receipt = supplement_target(root, original)
        self.assertEqual(actual, original)
        self.assertEqual(receipt['added_edges'], [])
        self.assertEqual(receipt['status'], 'complete')
        self.assertTrue(any(row['file'].endswith('LinkedHost.ets') for row in receipt['scope_exclusions']))


if __name__ == '__main__':
    unittest.main()
