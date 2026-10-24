"""Pragma headings are metadata; executable source and its anchors stay intact."""
import os
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(os.environ.get('HMIGBOT_TEST_RUNTIME', Path(__file__).resolve().parents[1])).resolve()
sys.path.insert(0, str(ROOT / 'src'))
from hmigbot_ios.core import digest
from hmigbot_ios.ios_facts import extract
from hmigbot_ios.swiftui import tokenize


class PragmaMarkTests(unittest.TestCase):
    def graph(self, text, suffix='.m'):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / ('Sample' + suffix)
            path.write_text(text, encoding='utf-8')
            return extract(Path(directory))

    def test_headings_do_not_create_identifiers_or_behavior_facts(self):
        for suffix in ('.m', '.mm', '.h', '.c', '.cpp'):
            for heading in ('中文分组', 'English', '- if delegate Task { count = 2'):
                with self.subTest(suffix=suffix, heading=heading):
                    graph = self.graph('#pragma mark ' + heading + '\nvoid f(void) {}\n', suffix)
                    self.assertEqual(graph['issues'], [])
                    self.assertEqual(graph['facts'], [])

    def test_real_unicode_identifier_still_blocks(self):
        graph = self.graph('#pragma mark 中文分组\nvoid f(void) { int 数量 = 1; }\n')
        self.assertIn('IOS.TOKEN_IDENTIFIER_UNRESOLVED', [i['rule'] for i in graph['issues']])

    def test_following_behavior_keeps_original_anchor_and_hash(self):
        text = '#pragma mark 中文分组\nvoid f(void) {\n  count += 1;\n}\n'
        graph = self.graph(text)
        fact = next(f for f in graph['facts'] if f['kind'] == 'write')
        self.assertEqual(fact['symbol'], 'count')
        self.assertEqual(fact['anchor']['line'], 3)
        self.assertEqual(fact['anchor']['snippet'], '  count += 1;')
        self.assertEqual(fact['anchor']['file_sha256'], digest(text.encode()))
        self.assertEqual(fact['anchor']['snippet_sha256'], digest(b'  count += 1;'))

    def test_conditionals_are_not_suppressed(self):
        for directive in ('#if DEBUG', '#ifdef DEBUG', '#ifndef HEADER_H'):
            with self.subTest(directive=directive):
                graph = self.graph('#pragma mark 中文\n' + directive + '\nint count = 1;\n#endif\n')
                self.assertIn('IOS.CONDITIONAL_BUILD', [i['rule'] for i in graph['issues']])
                self.assertTrue(any(f['kind'] == 'write' for f in graph['facts']))

    def test_strings_and_comments_are_not_directives(self):
        text = '// #pragma mark 中文\n/* #pragma mark 中文 */\nNSString *label = @"#pragma mark 中文";\n'
        graph = self.graph(text)
        self.assertEqual(graph['issues'], [])
        fact = next(f for f in graph['facts'] if f['kind'] == 'write')
        self.assertIn('@"#pragma mark 中文"', fact['anchor']['snippet'])
        self.assertIn('"#pragma mark 中文"', fact['value']['tokens'])

    def test_multiline_string_is_preserved(self):
        text = '"""start\n#pragma mark 中文\nend"""\n'
        self.assertEqual(tokenize(text, skip_pragma_marks=True), tokenize(text))

    def test_opt_in_does_not_change_swift_analysis(self):
        graph = self.graph('#pragma mark 中文\nvar count = 1\n', '.swift')
        self.assertIn('IOS.TOKEN_IDENTIFIER_UNRESOLVED', [i['rule'] for i in graph['issues']])
        self.assertIn('pragma', [t.value for t in tokenize('#pragma mark 中文\n')])

    def test_only_exact_directive_at_line_start_is_filtered(self):
        for text in ('int x; #pragma mark 中文\n', '#pragma marker 中文\n', '#define 标识 1\n'):
            with self.subTest(text=text):
                graph = self.graph(text)
                self.assertIn('IOS.TOKEN_IDENTIFIER_UNRESOLVED', [i['rule'] for i in graph['issues']])
        self.assertEqual(self.graph(' \t# \tpragma\tmark - 中文')['issues'], [])

    def test_continued_heading_preserves_following_line(self):
        for ending in ('\n', '\r\n'):
            text = '#pragma mark 标题 \\' + ending + '续行 if { count = 2' + ending + 'int actual = 1;' + ending
            graph = self.graph(text)
            self.assertEqual(graph['issues'], [])
            self.assertEqual([(f['kind'], f['symbol'], f['anchor']['line']) for f in graph['facts']],
                             [('write', 'actual', 3)])


if __name__ == '__main__':
    unittest.main()
