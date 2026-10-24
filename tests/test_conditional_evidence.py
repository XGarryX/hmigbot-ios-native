"""Clang-backed conditional observations and fail-closed evidence contracts.

The build fixture is synthetic and tests validation only. Parser/occurrence,
module import and AST witness tests invoke the real locally installed Clang.
"""
import copy
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from hmigbot_ios import conditional_evidence as ce
from hmigbot_ios.core import MigrationError, digest, json_bytes, read_json, snapshot, write_json


CLANG = shutil.which('clang')


class TemporarySource(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix='conditional-evidence-')
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name).resolve()
        self.source = self.root / 'source'
        self.source.mkdir()

    def file(self, name, text):
        p = self.source / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding='utf-8')
        return p

    def clang(self, *args):
        if not CLANG:
            self.skipTest('Real Clang is required for the compiler observation tests')
        result = subprocess.run([CLANG, *map(str, args)], cwd=self.source,
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result

    def observe(self, name, members=None, flags=()):
        result = self.clang(*flags, *ce.FLAGS, self.source / name)
        if members is None:
            members = [p.relative_to(self.source).as_posix()
                       for p in self.source.rglob('*') if p.is_file()]
        return ce.project_output(self.source, result.stdout, members)

    def token_lines(self, name, views):
        active = set().union(*(set(v['active_lines']) for v in views if v['path'] == name))
        return {t.value for t in ce.tokenize((self.source / name).read_text()) if t.line in active}


class ClangConditionalTests(TemporarySource):
    def test_real_clang_octal_utf8_line_markers_keep_unicode_paths(self):
        self.file('中文源.c', '#if 1\nint selected;\n#else\nint rejected;\n#endif\n')
        views = self.observe('中文源.c')
        self.assertIn('selected', self.token_lines('中文源.c', views))
        self.assertNotIn('rejected', self.token_lines('中文源.c', views))

    def test_if_ifdef_ifndef_elif_else_undef_and_parent_inactive(self):
        self.file('main.c', '''#define ENABLED 1
#if ENABLED
int selected_if;
#else
int rejected_else;
#endif
#ifdef ENABLED
int selected_ifdef;
#endif
#undef ENABLED
#ifdef ENABLED
int rejected_after_undef;
#elif defined(MISSING)
int rejected_elif;
#else
int selected_else;
#endif
#ifndef ENABLED
int selected_ifndef;
#endif
#if 0
#if 1
int rejected_nested_parent;
#endif
#endif
#if 0
int rejected_first;
#elif 2
int selected_elif;
#else
int rejected_last;
#endif
''')
        tokens = self.token_lines('main.c', self.observe('main.c'))
        for ident in ('selected_if', 'selected_ifdef', 'selected_else', 'selected_ifndef', 'selected_elif'):
            self.assertIn(ident, tokens)
        self.assertFalse({v for v in tokens if v.startswith('rejected_')})

    def test_same_header_different_translation_units_remains_distinct(self):
        self.file('choice.h', '#if PICK\nint left;\n#else\nint right;\n#endif\n')
        self.file('left.c', '#define PICK 1\n#include "choice.h"\n')
        self.file('right.c', '#define PICK 0\n#include "choice.h"\n')
        left, right = self.observe('left.c'), self.observe('right.c')
        self.assertIn('left', self.token_lines('choice.h', left))
        self.assertNotIn('right', self.token_lines('choice.h', left))
        self.assertIn('right', self.token_lines('choice.h', right))
        self.assertNotIn('left', self.token_lines('choice.h', right))

    def test_repeated_include_keeps_each_occurrence_not_union(self):
        self.file('repeat.h', '#if PICK\nint first;\n#else\nint second;\n#endif\n')
        self.file('main.c', '#define PICK 1\n#include "repeat.h"\n#undef PICK\n#define PICK 0\n#include "repeat.h"\n')
        views = [v for v in self.observe('main.c') if v['path'] == 'repeat.h']
        self.assertEqual(len(views), 2)
        self.assertNotEqual(views[0]['instance'], views[1]['instance'])
        self.assertEqual(views[0]['active_lines'], [2])
        self.assertEqual(views[1]['active_lines'], [4])

    def test_absent_include_is_not_an_observed_empty_file(self):
        self.file('unused.h', '#if 1\nint unused;\n#endif\n')
        self.file('main.c', '#if 0\n#include "unused.h"\n#endif\nint kept;\n')
        views = self.observe('main.c')
        self.assertFalse(any(v['path'] == 'unused.h' for v in views))
        self.assertIn('kept', self.token_lines('main.c', views))

    def test_cross_line_comment_keeps_post_comment_effective_tokens(self):
        self.file('main.c', 'int a /* split\n comment */ = 1;\n#if 0\nint gone;\n#endif\nint b = 2;\n')
        views = self.observe('main.c')
        lines = next(v['active_lines'] for v in views if v['path'] == 'main.c')
        self.assertIn(2, lines)
        self.assertIn('1', self.token_lines('main.c', views))
        self.assertNotIn('gone', self.token_lines('main.c', views))

    def test_fake_pragma_and_marker_inside_comment_are_not_control(self):
        self.file('main.c', '/*\n#pragma fake */ int x=1;\n/*\n# 500 "imaginary.h" 1\n*/ int y=2;\n')
        views = self.observe('main.c')
        self.assertEqual({v['path'] for v in views}, {'main.c'})
        tokens = self.token_lines('main.c', views)
        self.assertTrue({'x', 'y', '1', '2'} <= tokens)

    def test_multiline_define_and_code_splice_keep_all_physical_lines(self):
        self.file('main.c', '#define ENABLED \\\n  1\n#if ENABLED\nint answer = \\\n  42;\n#else\nint gone;\n#endif\n')
        views = self.observe('main.c')
        lines = next(v['active_lines'] for v in views if v['path'] == 'main.c')
        self.assertTrue({1, 2, 4, 5} <= set(lines))
        tokens = self.token_lines('main.c', views)
        self.assertIn('42', tokens)
        self.assertNotIn('gone', tokens)

    def branch_pair(self, name):
        members = [p.relative_to(self.source).as_posix()
                   for p in self.source.rglob('*') if p.is_file()]
        direct = self.clang(*ce.FLAGS, self.source / name)
        full = self.clang(*(a for a in ce.FLAGS if a != '-fdirectives-only'), self.source / name)
        return (ce.project_output(self.source, direct.stdout, members),
                ce.project_output(self.source, full.stdout, members))

    def test_counter_side_effect_branch_difference_is_rejected(self):
        self.file('main.c', 'int consumed = __COUNTER__;\n#if __COUNTER__ == 0\nint only_direct;\n#else\nint only_full;\n#endif\n')
        direct, full = self.branch_pair('main.c')
        self.assertIn('only_direct', self.token_lines('main.c', direct))
        self.assertNotIn('only_full', self.token_lines('main.c', direct))
        self.assertIn('only_full', self.token_lines('main.c', full))
        with self.assertRaisesRegex(MigrationError, 'branch disagreement'):
            ce.compare_branches(self.source, direct, full)

    def test_spliced_directive_name_cannot_bypass_counter_branch_check(self):
        self.file('main.c', 'int consumed = __COUNTER__;\n#i\\\nf __COUNTER__ == 0\nint only_direct;\n#en\\\ndif\n')
        direct, full = self.branch_pair('main.c')
        self.assertIn('only_direct', self.token_lines('main.c', direct))
        self.assertNotIn('only_direct', self.token_lines('main.c', full))
        with self.assertRaises(MigrationError):
            ce.compare_branches(self.source, direct, full)

    def test_unsupported_elif_variants_cannot_hide_branch_disagreement(self):
        for directive in ('elifdef FLAG', 'elifndef MISSING'):
            with self.subTest(directive=directive):
                self.file('main.c', '#define FLAG 1\nint consumed = __COUNTER__;\n#if __COUNTER__ == 0\nint only_direct;\n#' + directive + '\nint only_full;\n#endif\n')
                direct, full = self.branch_pair('main.c')
                self.assertIn('only_direct', self.token_lines('main.c', direct))
                self.assertIn('only_full', self.token_lines('main.c', full))
                with self.assertRaises(MigrationError):
                    ce.compare_branches(self.source, direct, full)

    def test_ordinary_branches_agree_per_repeated_include_occurrence(self):
        self.file('repeat.h', '#if PICK\nint first;\n#else\nint second;\n#endif\n')
        self.file('main.c', '#define PICK 1\n#include "repeat.h"\n#undef PICK\n#define PICK 0\n#include "repeat.h"\n')
        direct, full = self.branch_pair('main.c')
        self.assertEqual(len([v for v in direct if v['path'] == 'repeat.h']), 2)
        self.assertEqual(len([v for v in full if v['path'] == 'repeat.h']), 2)
        ce.compare_branches(self.source, direct, full)
        missing_occurrence = [v for v in full if not (v['path'] == 'repeat.h' and 4 in v['active_lines'])]
        with self.assertRaisesRegex(MigrationError, 'include occurrences differ'):
            ce.compare_branches(self.source, direct, missing_occurrence)

    def test_source_line_override_is_explicitly_rejected(self):
        p = self.file('main.c', '#line 400 "elsewhere.c"\nint kept;\n')
        result = self.clang(*ce.FLAGS, p)
        with self.assertRaisesRegex(MigrationError, '#line remapping unsupported'):
            ce.project_output(self.source, result.stdout, ['main.c'])

    def test_implicit_module_import_reports_actual_pcm(self):
        self.file('mod/Feature.h', '#define FEATURE 1\nstruct FeatureType { int value; };\n')
        self.file('mod/module.modulemap', 'module Feature { header "Feature.h" export * }\n')
        main = self.file('main.m', '#include "Feature.h"\n#if FEATURE\nint selected;\n#else\nint rejected;\n#endif\n')
        cache = self.root / 'module-cache'
        result = self.clang('-fmodules', '-fimplicit-module-maps', '-fmodules-cache-path=' + str(cache),
                            '-I', self.source / 'mod', *ce.FLAGS, main)
        paths = ce._module_paths(result.stderr, result.stdout)
        self.assertTrue(paths, result.stderr)
        self.assertTrue(all(Path(p).is_file() and Path(p).suffix == '.pcm' for p in paths))
        self.assertTrue(all(Path(p).is_relative_to(cache) for p in paths))


class ModuleGuardTests(TemporarySource):
    HEADER = '#ifndef TYPES_H\n#define TYPES_H\nenum Entry { First = 1, Second = 2 };\n#endif\n'

    def test_simple_guard_accepts_only_whole_unmodified_guard(self):
        result = ce.simple_guard(self.HEADER)
        self.assertEqual(result, {'guard': 'TYPES_H', 'symbol': 'Entry', 'line': 3,
                                  'body_start': 3, 'body_end': 3})
        for text in (self.HEADER.replace('#ifndef', '#ifdef'),
                     self.HEADER.replace('#define TYPES_H', '#define TYPES_H 1'),
                     self.HEADER.replace('enum Entry', '#if ENABLED\nenum Entry').replace('#endif', '#endif\n#endif'),
                     self.HEADER.replace('#endif', '#undef TYPES_H\n#endif'),
                     self.HEADER.replace('#endif', '#elifdef FLAG\nint disabled;\n#endif'),
                     self.HEADER.replace('#endif', '#elifndef MISSING\nint disabled;\n#endif'),
                     self.HEADER.replace('#endif', '%:if 0\nint disabled;\n%:endif\n#endif'),
                     self.HEADER.replace('#endif', '??=if 0\nint disabled;\n??=endif\n#endif'),
                     self.HEADER + 'int outside;\n',
                     self.HEADER.replace('enum Entry { First = 1, Second = 2 };', 'enum Entry;')):
            with self.subTest(text=text):
                self.assertIsNone(ce.simple_guard(text))

    def test_ns_enum_guard_is_supported_without_general_condition_waiver(self):
        text = self.HEADER.replace('enum Entry { First = 1, Second = 2 };',
                                   'typedef NS_ENUM(NSInteger, Entry) { First = 1, Second = 2 };')
        self.assertEqual(ce.simple_guard(text)['symbol'], 'Entry')
        self.assertIsNone(ce.simple_guard(text.replace('#endif', '#else\n#endif')))

    def candidate(self):
        header = self.file('Types.h', self.HEADER)
        return {'path': 'Types.h', 'staged': str(header), 'guard': ce.simple_guard(self.HEADER)}

    def test_real_enum_ast_body_witness_and_wrong_path_rejection(self):
        candidate = self.candidate()
        main = self.file('main.c', '#include "Types.h"\n')
        raw = self.clang('-fsyntax-only', '-Xclang', '-ast-dump-all=json',
                         '-Xclang', '-ast-dump-filter=Entry', main).stdout
        self.assertTrue(ce._guard_witness(self.source, candidate, raw), raw)
        wrong = {**candidate, 'staged': str(self.root / 'Wrong.h')}
        self.assertFalse(ce._guard_witness(self.source, wrong, raw))
        modified = copy.deepcopy(candidate)
        modified['guard']['line'] += 1
        self.assertFalse(ce._guard_witness(self.source, modified, raw))

    def test_lazy_pcm_enum_definition_requires_exact_direct_closing_brace(self):
        text = '#ifndef TYPES_H\n#define TYPES_H\nenum Entry {\n First = 1,\n Second = 2\n};\n#endif\n'
        header = self.file('Types.h', text)
        self.file('module.modulemap', 'module Example { header "Types.h" export * }\n')
        main = self.file('main.m', '#include "Types.h"\n')
        candidate = {'path': 'Types.h', 'staged': str(header), 'guard': ce.simple_guard(text)}
        result = self.clang('-fmodules', '-fimplicit-module-maps',
                            '-fmodules-cache-path=' + str(self.root / 'cache'), '-I', self.source,
                            '-fsyntax-only', '-Xclang', '-ast-dump-all=json',
                            '-Xclang', '-ast-dump-filter=Entry', main)
        node = json.loads(result.stdout)
        self.assertEqual(node['kind'], 'EnumDecl')
        self.assertFalse(node.get('inner'), 'The real PCM fixture must exercise lazy children')
        self.assertTrue(ce._guard_witness(self.source, candidate, result.stdout))
        mutations = []
        for field, value in (('offset', text.index('First')), ('file', str(self.root / 'Wrong.h')),
                             ('line', 99), ('tokLen', 2)):
            changed = copy.deepcopy(node)
            changed['range']['end'][field] = value
            mutations.append(changed)
        forward = copy.deepcopy(node)
        forward['range']['end'] = dict(forward['loc'])
        mutations.append(forward)
        macro = copy.deepcopy(node)
        macro['range']['end'] = {'spellingLoc': dict(node['range']['end']),
                                 'expansionLoc': dict(node['loc'])}
        mutations.append(macro)
        wrong_symbol_offset = copy.deepcopy(node)
        wrong_symbol_offset['loc']['offset'] += 1
        mutations.append(wrong_symbol_offset)
        for changed in mutations:
            with self.subTest(end=changed['range']['end'], loc=changed['loc']):
                self.assertFalse(ce._guard_witness(self.source, candidate, json.dumps(changed)))

    def test_forward_enum_and_empty_ast_are_not_positive_witnesses(self):
        candidate = self.candidate()
        main = self.file('forward.c', 'enum Entry;\n')
        raw = self.clang('-fsyntax-only', '-Xclang', '-ast-dump-all=json',
                         '-Xclang', '-ast-dump-filter=Entry', main).stdout
        # Even with matching location metadata a forward decl lacks enum values.
        node = json.loads(raw)
        node['loc'] = {'file': candidate['staged'], 'line': 3,
                       'offset': self.HEADER.index('Entry')}
        self.assertFalse(ce._guard_witness(self.source, candidate, json.dumps(node)))
        self.assertFalse(ce._guard_witness(self.source, candidate, ''))

    def test_module_paths_require_import_evidence_and_absolute_pcm(self):
        p = self.root / 'Feature.pcm'
        direct = f"remark: importing module 'Feature' from '{p}' [-Rmodule-import]\n"
        nested = f"remark: importing module 'Feature' into 'Parent' from '{p}' [-Rmodule-import]\n"
        self.assertEqual(ce._module_paths(direct + nested), {str(p)})
        with self.assertRaisesRegex(MigrationError, 'lack actual PCM'):
            ce._module_paths('', '#pragma clang module import Feature\n')
        for bad in ('relative.pcm', str(self.root / 'not-pcm.txt')):
            with self.subTest(path=bad), self.assertRaisesRegex(MigrationError, 'invalid imported PCM'):
                ce._module_paths(f"remark: importing module 'Feature' from '{bad}' [-Rmodule-import]")

    def test_comment_mention_of_module_import_is_not_missing_pcm_evidence(self):
        main = self.file('comment.c', '/* #pragma clang module import Example */\nint visible;\n')
        result = self.clang(*ce.FLAGS, main)
        self.assertEqual(ce._module_paths(result.stderr, result.stdout), set())

    def test_module_candidate_requires_exact_source_copy_and_simple_guard(self):
        header = self.file('Types.h', self.HEADER)
        staged = self.root / 'copied/Types.h'
        staged.parent.mkdir(); staged.write_bytes(header.read_bytes())
        build = self.root / 'build'
        write_json(build / 'manifest.json', {'artifacts': {'artifacts/framework-header-provenance.json': 'fixture'}})
        provenance = [{'source': 'Types.h', 'staged': str(staged), 'sha256': digest(header.read_bytes())}]
        write_json(build / 'artifacts/framework-header-provenance.json', provenance)
        original = {'members': ['Types.h']}
        candidates = ce._module_candidates(self.source, build, original, {})
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0]['guard']['symbol'], 'Entry')
        self.assertEqual(ce._module_candidates(self.source, build, original, {'Types.h': [{}]}), [])
        staged.write_text(self.HEADER + '// different copy\n')
        with self.assertRaisesRegex(MigrationError, 'source/copy mismatch'):
            ce._module_candidates(self.source, build, original, {})
        complex_header = self.HEADER.replace('enum Entry', '#if ENABLED\nenum Entry').replace('#endif', '#endif\n#endif')
        header.write_text(complex_header); staged.write_text(complex_header)
        provenance[0]['sha256'] = digest(header.read_bytes())
        write_json(build / 'artifacts/framework-header-provenance.json', provenance)
        self.assertEqual(ce._module_candidates(self.source, build, original, {}), [])

    def test_file_inputs_include_explicit_named_pcm_and_sdk_identity(self):
        pcm, hdr = self.root / 'Feature.pcm', self.root / 'prefix.pch'
        pcm.write_bytes(b'pcm'); hdr.write_bytes(b'prefix')
        sdk = self.root / 'sdk'; sdk.mkdir()
        (sdk / 'SDKSettings.json').write_text('{}')
        result = ce._file_inputs(['-fmodule-file=Feature=' + str(pcm), '-include-pch', str(hdr),
                                  '-isysroot', str(sdk)])
        self.assertEqual(result, {str(pcm), str(hdr), str(sdk / 'SDKSettings.json')})


class EvidenceContractTests(TemporarySource):
    def setUp(self):
        super().setUp()
        self.project = self.root / 'project'
        self.project.mkdir()
        write_json(self.project / '.migbot/config.json', {'source_platform': 'ios', 'ios': str(self.source)})
        self.main = self.file('main.c', '#if 1\nint included;\n#else\nint excluded;\n#endif\n')
        self.build = self.project / 'spec/ref/build'
        self.build.mkdir(parents=True)
        write_json(self.build / 'manifest.json', {'artifacts': {}})
        self.expected = {'project': 'Demo.xcodeproj', 'scheme': 'Demo', 'target': 'Demo',
                         'configuration': 'Debug', 'sdk': 'iphoneos', 'architecture': 'arm64'}
        self.output = self.project / 'spec/ref/ios-conditional-evidence/capture'

    def captured(self):
        if not CLANG:
            self.skipTest('Real Clang is required for capture tests')
        expanded = [CLANG, '-c', str(self.main)]
        original = {'source_sha256': snapshot(self.source)['sha256'],
                    'build_manifest_sha256': digest((self.build / 'manifest.json').read_bytes()),
                    'expected_build': self.expected, 'members': ['main.c'],
                    'rows': [{'source': 'main.c', 'expanded_argv': expanded,
                              'argv': ce.preprocess_argv(expanded)}]}
        self.build_patch = patch.object(ce, '_build', return_value=original)
        self.build_patch.start(); self.addCleanup(self.build_patch.stop)
        self.config = self.project / 'capture-config.json'
        write_json(self.config, {'schema_version': ce.VERSION, 'build_evidence': str(self.build),
                                'expected_build': self.expected})
        ce.capture(self.project, self.config, self.output)
        return original

    def reseal(self, name):
        manifest = read_json(self.output / 'manifest.json')
        manifest['artifacts'][name] = digest((self.output / name).read_bytes())
        write_json(self.output / 'manifest.json', manifest)

    def test_real_capture_replays_and_freezes_raw_evidence(self):
        self.captured()
        checked = ce.validate(self.source, self.output, project=self.project)
        tokens = {t.value for t in ce.tokenize(self.main.read_text())
                  if t.line in checked['observed']['main.c'][0]['active_lines']}
        self.assertIn('included', tokens)
        self.assertNotIn('excluded', tokens)
        frozen = ce.frozen_inputs(self.project, {'conditional_evidence': checked['reference']})
        self.assertIn('spec/ref/build/manifest.json', frozen)
        for name in ('manifest.json', 'tu-0000.i', 'tu-0000.stderr.log', 'tu-0000.d',
                     'tu-0000.full.i', 'tu-0000.full.stderr.log', 'tu-0000.full.d', 'commands.json', 'inputs.json', 'guards.json', 'config.json'):
            self.assertIn('spec/ref/ios-conditional-evidence/capture/' + name, frozen)

    def test_modified_artifact_and_failed_capture_are_rejected(self):
        self.captured()
        path = self.output / 'tu-0000.i'
        original = path.read_bytes()
        path.write_bytes(original + b'\nint injected;\n')
        with self.assertRaisesRegex(MigrationError, 'missing/modified artifact'):
            ce.validate(self.source, self.output, project=self.project)
        path.write_bytes(original)
        write_json(self.output / 'failure.json', {'status': 'capture_failed'})
        with self.assertRaisesRegex(MigrationError, 'failed capture'):
            ce.validate(self.source, self.output, project=self.project)

    def test_missing_full_preprocessing_artifact_is_rejected(self):
        self.captured()
        manifest = read_json(self.output / 'manifest.json')
        del manifest['artifacts']['tu-0000.full.i']
        write_json(self.output / 'manifest.json', manifest)
        with self.assertRaisesRegex(MigrationError, 'missing/modified full preprocessing observation'):
            ce.validate(self.source, self.output, project=self.project)

    def test_capture_with_counter_disagreement_is_sealed_as_failure(self):
        self.main.write_text('int consumed = __COUNTER__;\n#if __COUNTER__ == 0\nint direct_only;\n#else\nint full_only;\n#endif\n')
        with self.assertRaisesRegex(MigrationError, 'branch disagreement'):
            self.captured()
        self.assertTrue((self.output / 'failure.json').is_file())
        with self.assertRaisesRegex(MigrationError, 'failed capture'):
            ce.validate(self.source, self.output, project=self.project)

    def test_resealed_config_mismatch_is_not_accepted(self):
        self.captured()
        cfg = read_json(self.output / 'config.json')
        cfg['expected_build']['configuration'] = 'Release'
        write_json(self.output / 'config.json', cfg); self.reseal('config.json')
        with self.assertRaisesRegex(MigrationError, 'capture config mismatch'):
            ce.validate(self.source, self.output, project=self.project)

    def test_resealed_manual_active_lines_cannot_replace_clang_observation(self):
        self.captured()
        records = read_json(self.output / 'commands.json')
        records[0]['views'][0]['active_lines'].append(4)
        write_json(self.output / 'commands.json', records); self.reseal('commands.json')
        with self.assertRaisesRegex(MigrationError, 'derived source views differ'):
            ce.validate(self.source, self.output, project=self.project)

    def test_replayed_config_requires_the_same_supported_schema_as_capture(self):
        self.captured()
        original = read_json(self.output / 'config.json')
        for mutation in ({'schema_version': 999}, {'bypass': True}):
            with self.subTest(mutation=mutation):
                write_json(self.output / 'config.json', {**original, **mutation})
                self.reseal('config.json')
                with self.assertRaisesRegex(MigrationError, 'conditionalConfig'):
                    ce.validate(self.source, self.output, project=self.project)

    def test_incomplete_commands_and_missing_live_inputs_are_rejected(self):
        self.captured()
        records = read_json(self.output / 'commands.json')
        write_json(self.output / 'commands.json', []); self.reseal('commands.json')
        with self.assertRaisesRegex(MigrationError, 'incomplete captured compilation units'):
            ce.validate(self.source, self.output, project=self.project)
        write_json(self.output / 'commands.json', records); self.reseal('commands.json')
        inputs = read_json(self.output / 'inputs.json')
        del inputs[str(Path(CLANG).resolve())]
        write_json(self.output / 'inputs.json', inputs); self.reseal('inputs.json')
        with self.assertRaisesRegex(MigrationError, 'fingerprint set mismatch'):
            ce.validate(self.source, self.output, project=self.project)

    def test_live_source_change_and_changed_build_binding_fail_closed(self):
        original = self.captured()
        self.main.write_text(self.main.read_text() + 'int changed;\n')
        with self.assertRaisesRegex(MigrationError, 'live compiler/dependency input'):
            ce.validate(self.source, self.output, project=self.project)
        original['build_manifest_sha256'] = '0' * 64
        with self.assertRaisesRegex(MigrationError, 'source/build evidence changed'):
            ce.validate(self.source, self.output, project=self.project)

    def test_frozen_reference_cannot_be_swapped(self):
        self.captured()
        reference = ce.validate(self.source, self.output, project=self.project)['reference']
        reference['manifest_sha256'] = '0' * 64
        with self.assertRaisesRegex(MigrationError, 'reference changed'):
            ce.frozen_inputs(self.project, {'conditional_evidence': reference})

    def test_capture_rejects_unknown_config_and_outside_output(self):
        config = self.project / 'bad-config.json'
        write_json(config, {'schema_version': ce.VERSION, 'build_evidence': str(self.build),
                            'expected_build': self.expected, 'bypass': True})
        with self.assertRaisesRegex(MigrationError, 'conditionalConfig: unknown field'):
            ce.capture(self.project, config, self.output)
        data = read_json(config); del data['bypass']; write_json(config, data)
        with self.assertRaisesRegex(MigrationError, 'fresh project/spec/ref'):
            ce.capture(self.project, config, self.root / 'outside')


class BuildBindingTests(TemporarySource):
    def setUp(self):
        super().setUp()
        self.main = self.file('main.c', 'int main(void) { return 0; }\n')
        self.header = self.file('dependency.h', 'enum Dependency { Required = 1 };\n')
        self.unused = self.file('unused.h', 'int not_a_dependency;\n')
        (self.source / 'Demo.xcodeproj').mkdir()
        self.bundle = self.root / 'build'
        self.artifacts = self.bundle / 'artifacts'
        self.artifacts.mkdir(parents=True)
        self.compiler = self.root / 'tools/clang'
        self.compiler.parent.mkdir(); self.compiler.write_bytes(b'compiler identity fixture')
        self.sdk = self.root / 'sdk'; self.sdk.mkdir()
        (self.sdk / 'SDKSettings.json').write_text('{"SDK":"fixture"}')
        self.expected = {'project': 'Demo.xcodeproj', 'scheme': 'Demo', 'target': 'Demo',
                         'configuration': 'Debug', 'sdk': 'iphoneos', 'architecture': 'arm64'}
        argv = ['/usr/bin/xcodebuild', '-project', str(self.source / 'Demo.xcodeproj'),
                '-scheme', 'Demo', '-configuration', 'Debug', '-sdk', 'iphoneos', 'build']
        commands = [{'name': 'device-build', 'argv': argv, 'cwd': str(self.source), 'exit_code': 0}]
        sha = snapshot(self.source)['sha256']
        settings = [{'target': 'Demo', 'buildSettings': {'TARGET_NAME': 'Demo', 'CONFIGURATION': 'Debug',
                    'PROJECT_FILE_PATH': str(self.source / 'Demo.xcodeproj'), 'ARCHS': 'arm64',
                    'SDK_NAME': 'iphoneos27.1', 'SDKROOT': str(self.sdk)}}]
        expanded = [str(self.compiler), '-target', 'arm64-apple-ios17.6', '-isysroot', str(self.sdk),
                    '-c', str(self.main), '-MF', str(self.root / 'DerivedData/main.d')]
        values = {'commands.json': commands,
                  'capture-report.json': {'commands': commands, 'build_succeeded': True,
                                         'source_unchanged': True, 'source_sha256': sha},
                  'build-settings.json': settings,
                  'compile-commands.json': [{'build_log_line': 1, 'original_argv': expanded,
                                            'expanded_argv': expanded}],
                  'source-files.json': {'source_files': ['dependency.h', 'main.c']}}
        tools = {str(self.compiler): digest(self.compiler.read_bytes()),
                 str(self.sdk / 'SDKSettings.json'): digest((self.sdk / 'SDKSettings.json').read_bytes())}
        values['toolchain-inputs.json'] = {'before': tools, 'after': tools}
        for name, data in values.items():
            write_json(self.artifacts / name, data)
        (self.artifacts / 'build-settings.stdout.log').write_bytes(json_bytes(settings))
        (self.artifacts / 'device-build.stdout.log').write_text(shlex.join(expanded) + '\n** BUILD SUCCEEDED **\n')
        (self.artifacts / 'build-inputs').mkdir()
        self.dependency = self.artifacts / 'build-inputs/main.d'
        self.dependency.write_text('main.o: ' + str(self.main) + ' ' + str(self.header) + '\n')
        write_json(self.bundle / 'manifest.json', {'artifacts': {
            'artifacts/' + p.relative_to(self.artifacts).as_posix(): digest(p.read_bytes())
            for p in self.artifacts.rglob('*') if p.is_file()}})
        bundle_patch = patch('hmigbot_ios.evidence.validate', return_value={'kind': 'source_build', 'source_sha256': sha})
        scope_patch = patch('hmigbot_ios.project_scope.resolve',
                            return_value={'target_closure': ['Demo'], 'source_files': ['main.c']})
        bundle_patch.start(); scope_patch.start()
        self.addCleanup(bundle_patch.stop); self.addCleanup(scope_patch.stop)

    def test_build_membership_and_toolchain_identity_match(self):
        result = ce._build(self.source, self.bundle, self.expected)
        self.assertEqual(result['members'], ['dependency.h', 'main.c'])
        self.assertEqual(len(result['rows']), 1)
        self.assertEqual(result['rows'][0]['argv'][-len(ce.FLAGS):], ce.FLAGS)

    def test_member_list_cannot_omit_a_real_dependency(self):
        write_json(self.artifacts / 'source-files.json', {'source_files': ['main.c']})
        with self.assertRaisesRegex(MigrationError, 'member list differs from original dependency/module inputs'):
            ce._build(self.source, self.bundle, self.expected)

    def test_member_list_cannot_add_an_unreferenced_source(self):
        write_json(self.artifacts / 'source-files.json',
                   {'source_files': ['dependency.h', 'main.c', 'unused.h']})
        with self.assertRaisesRegex(MigrationError, 'member list differs from original dependency/module inputs'):
            ce._build(self.source, self.bundle, self.expected)

    def test_dependency_file_must_belong_to_its_compilation_unit(self):
        self.dependency.write_text('wrong.o: ' + str(self.header) + ' ' + str(self.unused) + '\n')
        with self.assertRaisesRegex(MigrationError, 'dependency output omits its compilation unit'):
            ce._build(self.source, self.bundle, self.expected)

    def test_wrong_configuration_or_architecture_is_rejected(self):
        for field, wrong in (('configuration', 'Release'), ('architecture', 'x86_64'), ('scheme', 'Other')):
            with self.subTest(field=field), self.assertRaises(MigrationError):
                ce._build(self.source, self.bundle, {**self.expected, field: wrong})

    def test_missing_original_toolchain_evidence_is_rejected(self):
        manifest = read_json(self.bundle / 'manifest.json')
        del manifest['artifacts']['artifacts/toolchain-inputs.json']
        write_json(self.bundle / 'manifest.json', manifest)
        with self.assertRaisesRegex(MigrationError, 'missing hashed build input: toolchain-inputs.json'):
            ce._build(self.source, self.bundle, self.expected)

    def test_toolchain_changed_during_or_after_build_is_rejected(self):
        path = self.artifacts / 'toolchain-inputs.json'
        value = read_json(path)
        value['after'][str(self.compiler)] = '0' * 64
        write_json(path, value)
        with self.assertRaisesRegex(MigrationError, 'toolchain inputs absent/changed'):
            ce._build(self.source, self.bundle, self.expected)
        value['after'] = dict(value['before']); write_json(path, value)
        self.compiler.write_bytes(b'new compiler bytes at same pathname')
        with self.assertRaisesRegex(MigrationError, 'compiler/SDK changed since captured build'):
            ce._build(self.source, self.bundle, self.expected)

    def test_build_summary_cannot_invent_compilation_commands(self):
        path = self.artifacts / 'compile-commands.json'
        values = read_json(path)
        values[0]['build_log_line'] = 999
        write_json(path, values)
        with self.assertRaisesRegex(MigrationError, 'summary differs from original log'):
            ce._build(self.source, self.bundle, self.expected)

    def test_preprocess_arguments_keep_semantics_and_reject_unsafe_actions(self):
        argv = [str(self.compiler), '-DSELECTED=1', '-include', str(self.source / 'prefix.h'),
                '-c', str(self.main), '-o', '/tmp/output.o', '-MMD', '-MF', '/tmp/output.d']
        observed = ce.preprocess_argv(argv)
        self.assertIn('-DSELECTED=1', observed)
        self.assertIn('-include', observed)
        self.assertNotIn('-c', observed)
        self.assertNotIn('/tmp/output.o', observed)
        self.assertNotIn('/tmp/output.d', observed)
        for option in ('-E', '-P', '-fplugin=/tmp/plugin.so', '-ivfsoverlay'):
            with self.subTest(option=option), self.assertRaisesRegex(MigrationError, 'unsupported compiler'):
                ce.preprocess_argv(argv + [option])


if __name__ == '__main__':
    unittest.main()
