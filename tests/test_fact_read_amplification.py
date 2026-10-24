"""Facts must read each source file once, not once per fact, and stay byte-faithful."""
import os
import plistlib
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(os.environ.get('HMIGBOT_TEST_RUNTIME', Path(__file__).resolve().parents[1])).resolve()
sys.path.insert(0, str(ROOT / 'src'))
from hmigbot_ios.core import digest
from hmigbot_ios.ios_facts import extract

BOM = '﻿'


def declarations(count):
    """A dense file: every declaration emits a state fact, every assignment a write fact."""
    body = ''.join(f'    @State private var value{index} = {index}\n' for index in range(count))
    writes = ''.join(f'        value{index} = {index + 1}\n' for index in range(count))
    return ('import SwiftUI\nstruct Dense {\n' + body
            + '    var body: some View {\n        VStack {\n' + writes + '        }\n    }\n}\n')


def _plain(path):
    """Strip the long-path prefix io_path may add, so one file counts as one key."""
    text = str(path)
    return text[4:] if text.startswith('\\\\?\\') else text


class ReadCounting:
    """Count filesystem text reads per file so amplification is measured, not asserted away."""

    def __init__(self):
        self.counts = {}
        self._patchers = []

    def __enter__(self):
        for name in ('read_bytes', 'read_text'):
            def counted(self_path, _original=getattr(Path, name), **kwargs):
                key = _plain(self_path)
                self.counts[key] = self.counts.get(key, 0) + 1
                return _original(self_path, **kwargs)

            self._patchers.append(mock.patch.object(Path, name, counted))
        for patcher in self._patchers:
            patcher.start()
        return self

    def __exit__(self, *exc_info):
        for patcher in self._patchers:
            patcher.stop()
        return False

    def for_source(self, source):
        prefix = _plain(source)
        return {Path(key).name: count for key, count in self.counts.items() if _plain(Path(key).parent) == prefix}


class FactReadAmplificationTests(unittest.TestCase):
    def setUp(self):
        self._directory = tempfile.TemporaryDirectory()
        self.addCleanup(self._directory.cleanup)
        self.root = Path(self._directory.name)
        self._index = 0

    def source_with(self, files):
        self._index += 1
        source = self.root / f'source-{self._index}'
        source.mkdir()
        for name, text in files.items():
            (source / name).write_bytes(text.encode('utf-8') if isinstance(text, str) else text)
        return source

    def extract_counted(self, files):
        source = self.source_with(files)
        with ReadCounting() as counter:
            graph = extract(source)
        return source, graph, counter.for_source(source)

    def test_reads_do_not_grow_with_fact_density(self):
        """The decisive probe: ten times the facts on one file must not add a single extra read."""
        low_source, low, low_reads = self.extract_counted({'Dense.swift': declarations(100)})
        high_source, high, high_reads = self.extract_counted({'Dense.swift': declarations(1000)})
        self.assertGreaterEqual(len(high['facts']), 2000, 'expected >=2000 facts from 1000 declarations')
        self.assertGreater(len(high['facts']), 5 * len(low['facts']), 'probe is not fact-dense enough')
        # One read for the whole-tree snapshot, one cached read for every fact anchor.
        self.assertEqual(low_reads, {'Dense.swift': 2}, f'100-declaration file: {low_reads}')
        self.assertEqual(high_reads, {'Dense.swift': 2}, f'1000-declaration file: {high_reads}')
        self.assertEqual(sum(low_reads.values()), sum(high_reads.values()))

    def test_binary_resource_and_text_resources_use_one_view(self):
        source, graph, reads = self.extract_counted({
            'Info.plist': plistlib.dumps({'name': 'binary'}, fmt=plistlib.FMT_BINARY),
            'Notes.stringsdict': plistlib.dumps({'name': 'xml'}, fmt=plistlib.FMT_XML),
            'App.swift': 'import SwiftUI\nstruct App: View { var body: some View { Text("hi") } }\n',
        })
        self.assertEqual(reads, {'Info.plist': 2, 'Notes.stringsdict': 2, 'App.swift': 2},
                         'resource facts must not re-read per fact: ' + str(reads))
        plist = next(f for f in graph['facts'] if f['anchor']['path'] == 'Info.plist')
        self.assertEqual(plist['kind'], 'resource')
        self.assertEqual(plist['anchor']['snippet'], 'binary resource sha256:' + plist['anchor']['file_sha256'])
        self.assertEqual(plist['value']['encoding'], 'binary')
        self.assertEqual(plist['value']['content_validation'], 'parsed')
        strings = next(f for f in graph['facts'] if f['anchor']['path'] == 'Notes.stringsdict')
        self.assertEqual(strings['anchor']['snippet'], '<?xml version="1.0" encoding="UTF-8"?>')

    def test_non_text_source_still_needs_an_explicit_parser(self):
        source = self.source_with({'Broken.swift': b'struct A { var x = "\xff\xfe" }\n'})
        with self.assertRaises(UnicodeDecodeError):
            extract(source)

    def test_crlf_unicode_and_bom_snippets_are_byte_faithful(self):
        crlf_source, crlf, crlf_reads = self.extract_counted(
            {'Crlf.swift': 'import SwiftUI\r\nstruct C {\r\n    @State var count = 0\r\n}\r\n'})
        lf_source, lf, lf_reads = self.extract_counted({'Lf.swift': 'import SwiftUI\nstruct C {\n    @State var count = 0\n}\n'})
        bom_source, bom, bom_reads = self.extract_counted({'Bom.swift': BOM + 'import SwiftUI\nstruct C {\n    @State var greeting = "你好"\n}\n'})
        self.assertEqual([crlf_reads, lf_reads, bom_reads], [{'Crlf.swift': 2}, {'Lf.swift': 2}, {'Bom.swift': 2}])
        state = lambda graph: next(f for f in graph['facts'] if f['kind'] == 'state')
        crlf_state, lf_state, bom_state = state(crlf), state(lf), state(bom)
        self.assertEqual(crlf_state['anchor']['snippet'], lf_state['anchor']['snippet'], 'CRLF leaked a \\r into the snippet')
        self.assertEqual(crlf_state['anchor']['snippet_sha256'], lf_state['anchor']['snippet_sha256'])
        self.assertEqual(crlf_state['anchor']['line'], lf_state['anchor']['line'], 'CRLF shifted the line window')
        self.assertEqual(bom_state['anchor']['snippet'], '    @State var greeting = "你好"', 'BOM moved the window')
        self.assertEqual(bom_state['symbol'], 'greeting')
        self.assertEqual(digest(bom_state['anchor']['snippet'].encode('utf-8')), bom_state['anchor']['snippet_sha256'])
        unicode_source, unicode_graph, unicode_reads = self.extract_counted(
            {'CJK.swift': 'struct C { @State var 数量 = 0 }\n'})
        self.assertEqual(unicode_reads, {'CJK.swift': 2})
        self.assertIn('IOS.TOKEN_IDENTIFIER_UNRESOLVED', [i['rule'] for i in unicode_graph['issues']])
        self.assertEqual(state(unicode_graph)['anchor']['snippet'], 'struct C { @State var 数量 = 0 }')

    def test_cache_switches_between_files_without_reusing_lines(self):
        long_line = 'import SwiftUI\nstruct Long {\n    @State var big = "' + 'x' * 400 + '"\n}\n'
        source, graph, reads = self.extract_counted(
            {'Long.swift': long_line, 'Short.swift': 'struct Short { @State var n = 1 }\n'})
        self.assertEqual(reads, {'Long.swift': 2, 'Short.swift': 2})
        snippets = {f['anchor']['path']: f['anchor']['snippet'] for f in graph['facts'] if f['kind'] == 'state'}
        self.assertEqual(set(snippets), {'Long.swift', 'Short.swift'})
        self.assertEqual(len(snippets['Long.swift']), 400 + len('    @State var big = "') + 1)
        self.assertIn('n = 1', snippets['Short.swift'])
        self.assertNotIn('x' * 400, snippets['Short.swift'])

    def test_equal_size_content_change_is_detected_by_hash_not_size(self):
        source = self.source_with({'Same.swift': 'struct S { @State var a = "AAAAAAAA" }\n'})
        before = extract(source)
        path = source / 'Same.swift'
        stamp = os.stat(path)
        path.write_bytes(b'struct S { @State var a = "BBBBBBB2" }\n')
        os.utime(path, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
        self.assertEqual(os.stat(path).st_size, stamp.st_size, 'fixture must keep size and mtime identical')
        self.assertEqual(os.stat(path).st_mtime_ns, stamp.st_mtime_ns, 'fixture must keep mtime identical')
        after = extract(source)
        state = lambda graph: next(f for f in graph['facts'] if f['kind'] == 'state')
        self.assertNotEqual(before['source_sha256'], after['source_sha256'])
        self.assertNotEqual(state(after)['anchor']['snippet'], state(before)['anchor']['snippet'])
        self.assertEqual(digest(path.read_bytes()), state(after)['anchor']['file_sha256'])


if __name__ == '__main__':
    unittest.main()
