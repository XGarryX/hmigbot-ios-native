"""Real binary resources must not interrupt or bypass obligation coverage."""
import os
from pathlib import Path
import plistlib
import sys
import tempfile
import unittest

ROOT = Path(os.environ.get('HMIGBOT_TEST_RUNTIME', Path(__file__).resolve().parents[1])).resolve()
sys.path.insert(0, str(ROOT / 'src'))
from hmigbot_ios.analyze import analyze
from hmigbot_ios.core import digest, read_json, write_json
from hmigbot_ios.ios_harness import check
from hmigbot_ios import source_scope
from test_ios_harness import fixture


class ResourcePreviewTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='resource-preview-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()

    def project(self, name='fixture', fmt=plistlib.FMT_BINARY, suffix='.plist'):
        root = self.root / name
        root.mkdir()
        self.metadata = {'CFBundleName': '合法资源 #Preview { Text("资源") }', 'CFBundleVersion': '1'}
        data = plistlib.dumps(self.metadata, fmt=fmt)
        return fixture(root, resources={'AInfo' + suffix: data,
                                       'ZTail.plist': plistlib.dumps({'CFBundleName': 'Later resource'})})

    def test_binary_and_xml_plist_metadata_are_read_by_the_existing_format_parser(self):
        for number, fmt in enumerate((plistlib.FMT_BINARY, plistlib.FMT_XML)):
            with self.subTest(format=fmt):
                source, _, _ = self.project('metadata-' + str(number), fmt)
                report = analyze(source)
                metadata = [f for f in report['facts'] if f['kind'] == 'declaration_config'
                            and f['value'].get('key') == 'CFBundleName']
                self.assertTrue(any(f['value']['value'] == self.metadata['CFBundleName'] for f in metadata))
                self.assertEqual(plistlib.loads((source / 'AInfo.plist').read_bytes()), self.metadata)

    def test_plist_formats_and_binary_property_resources_keep_their_coverage_obligations(self):
        cases = [(plistlib.FMT_BINARY, '.plist'), (plistlib.FMT_XML, '.plist'),
                 (plistlib.FMT_BINARY, '.entitlements'), (plistlib.FMT_BINARY, '.xcprivacy'),
                 (plistlib.FMT_BINARY, '.stringsdict')]
        for number, (fmt, suffix) in enumerate(cases):
            with self.subTest(format=fmt, suffix=suffix):
                source, project, graph = self.project('coverage-' + str(number), fmt, suffix)
                before = {p.relative_to(project): p.read_bytes() for p in project.rglob('*') if p.is_file()}
                resources = {f['id'] for f in graph['facts'] if f['kind'] == 'resource'}
                obligations = read_json(project / 'spec/baseline/ios-obligations.json')['obligations']
                required = {o['id'] for o in obligations if o['fact_id'] in resources}
                report, code = check(project, report_only=True)
                self.assertEqual(code, 2)  # The fixture's UI-only AC cannot satisfy resource/static obligations.
                weak = {f['subject'] for f in report['findings'] if f['rule'] == 'IOS.ORACLE_TOO_WEAK'}
                self.assertEqual(weak, required)
                self.assertFalse(any(f['rule'] == 'IOS.HARNESS_CONTRACT' for f in report['findings']), report)
                self.assertEqual(report['excluded_obligation_ids'], [])
                self.assertFalse(report['behavior_verified'])
                self.assertEqual(before, {p.relative_to(project): p.read_bytes() for p in project.rglob('*') if p.is_file()})
                self.assertEqual(plistlib.loads((source / ('AInfo' + suffix)).read_bytes()), self.metadata)

    def test_all_obligations_after_a_binary_resource_still_report_missing_acceptance(self):
        _, project, graph = self.project()
        base = project / 'spec/baseline'
        coverage = read_json(base / 'ios-coverage.json')
        for mapping in coverage['mappings']:
            mapping['ac_ids'] = []
        write_json(base / 'ios-coverage.json', coverage)
        expected = {m['obligation_id'] for m in coverage['mappings']}
        report, code = check(project, report_only=True)
        self.assertEqual(code, 2)
        observed = {f['subject'] for f in report['findings'] if f['rule'] == 'IOS.OBLIGATION_AC_MISSING'}
        self.assertEqual(observed, expected)
        self.assertEqual(report['checks']['coverage']['finding_count'], len(expected))
        self.assertTrue(any(f['anchor']['path'] == 'ZTail.plist' for f in graph['facts']))

    def test_resource_cannot_be_excluded_by_a_forged_preview_review(self):
        _, project, graph = self.project()
        base = project / 'spec/baseline'
        resource = next(f for f in graph['facts'] if f['anchor']['path'] == 'AInfo.plist')
        obligations = read_json(base / 'ios-obligations.json')['obligations']
        ident = next(o['id'] for o in obligations if o['fact_id'] == resource['id'])
        coverage = read_json(base / 'ios-coverage.json')
        mapping = next(m for m in coverage['mappings'] if m['obligation_id'] == ident)
        mapping.update(ac_ids=[], disposition='preview-only',
                       source_sha256=resource['anchor']['file_sha256'],
                       skip_ref='spec/baseline/skip-list.md#Preview')
        write_json(base / 'ios-coverage.json', coverage)
        (base / 'skip-list.md').write_text('# Scope\n\n## Preview\nAInfo.plist reviewed.\n')
        report, code = check(project, report_only=True)
        self.assertEqual(code, 2)
        self.assertIn(ident, {f['subject'] for f in report['findings'] if f['rule'] == 'IOS.PREVIEW_REVIEW_REQUIRED'})
        self.assertNotIn(ident, report['excluded_obligation_ids'])

    def test_binary_resource_change_still_invalidates_the_graph(self):
        source, project, graph = self.project()
        path = source / 'AInfo.plist'
        before = digest(path.read_bytes())
        path.write_bytes(plistlib.dumps({'CFBundleName': 'Changed'}, fmt=plistlib.FMT_BINARY))
        self.assertNotEqual(digest(path.read_bytes()), before)
        report, code = check(project, report_only=True)
        self.assertEqual(code, 2)
        self.assertEqual(report['checks']['graph']['status'], 'FAIL')
        self.assertEqual(report['checks']['coverage']['status'], 'not_run')

    def test_objective_c_sources_and_headers_keep_facts_and_obligations_beside_binary_plist(self):
        code = ('#import <Foundation/Foundation.h>\n'
                'static NSInteger counter = 0;\n'
                'static inline void IncrementCounter(void) {\n'
                '  counter += 1;\n}\n')
        for suffix, language in (('.m', 'Objective-C'), ('.mm', 'Objective-C++'),
                                 ('.h', 'C-family-header')):
            with self.subTest(suffix=suffix):
                root = self.root / ('objc-' + suffix[1:])
                root.mkdir()
                name = 'ZCounter' + suffix
                metadata = {'CFBundleName': 'OC and binary resource'}
                source, project, graph = fixture(root, resources={
                    'AInfo.plist': plistlib.dumps(metadata, fmt=plistlib.FMT_BINARY),
                    name: code.encode('utf-8')})
                inventory = analyze(source)
                self.assertEqual(inventory['inventory']['languages'][language], 1)
                self.assertTrue(any(f['kind'] == 'header_import'
                                    and f['source_anchors_ref'][0]['path'] == name
                                    for f in inventory['facts']))
                self.assertTrue(any(f['kind'] == 'declaration_config'
                                    and f['value'] == {'key': 'CFBundleName', 'value': metadata['CFBundleName']}
                                    for f in inventory['facts']))
                objc_facts = {f['id'] for f in graph['facts'] if f['anchor']['path'] == name}
                self.assertTrue(any(f['id'] in objc_facts and f['kind'] == 'write'
                                    and f['symbol'] == 'counter' and f['anchor']['line'] == 4
                                    for f in graph['facts']))
                base = project / 'spec/baseline'
                obligations = read_json(base / 'ios-obligations.json')['obligations']
                objc_obligations = {o['id'] for o in obligations if o['fact_id'] in objc_facts}
                self.assertTrue(objc_obligations)
                coverage = read_json(base / 'ios-coverage.json')
                for mapping in coverage['mappings']:
                    mapping['ac_ids'] = []
                write_json(base / 'ios-coverage.json', coverage)
                report, status = check(project, report_only=True)
                observed = {f['subject'] for f in report['findings'] if f['rule'] == 'IOS.OBLIGATION_AC_MISSING'}
                self.assertEqual(status, 2)
                self.assertEqual(report['checks']['graph']['status'], 'PASS')
                self.assertEqual(observed, {o['id'] for o in obligations})
                self.assertTrue(objc_obligations <= observed)
                self.assertEqual(report['excluded_obligation_ids'], [])
                self.assertFalse(any(f['rule'] == 'IOS.HARNESS_CONTRACT' for f in report['findings']))

    def test_preview_file_routing_keeps_swift_lines_and_rejects_corrupt_swift(self):
        path = self.root / 'Screen.swift'
        path.write_text('// 标题\n#Preview {\n Text("示例")\n}\n', encoding='utf-8-sig')
        self.assertEqual(source_scope.preview_source_lines(path), {2, 3, 4})
        path.write_bytes(plistlib.dumps({'Name': '不是Swift'}, fmt=plistlib.FMT_BINARY))
        with self.assertRaises(UnicodeDecodeError):
            source_scope.preview_source_lines(path)

    def test_preview_looking_resource_text_is_never_swift_source(self):
        for suffix in ('.plist', '.json', '.png', '.storyboard', '.m'):
            with self.subTest(suffix=suffix):
                path = self.root / ('Resource' + suffix)
                path.write_bytes(b'#Preview {\n Text("resource")\n}\n')
                self.assertEqual(source_scope.preview_source_lines(path), set())
