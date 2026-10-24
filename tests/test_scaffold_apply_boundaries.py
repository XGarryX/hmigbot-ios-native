"""Source replay and competing-author boundaries; no application conversion."""
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from hmigbot_ios import native_scaffold as scaffold_module
from hmigbot_ios.core import MigrationError, read_json, write_json
from hmigbot_ios.native_pipeline import configure, index_source


class ScaffoldApplyBoundaryTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(dir='D:/Temp' if os.name == 'nt' else None,
                                                prefix='scaffold-boundaries-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.source, self.project = self.root / 'ios', self.root / 'harmony'
        self.source.mkdir()
        self.project.mkdir()
        self.source_file = self.source / 'MainScreen.swift'
        self.source_file.write_text('import SwiftUI\nstruct MainScreen: View { '
                                    'var body: some View { Text("hello") } }\n', encoding='utf-8')
        configure(self.source, self.project)
        index_source(self.project)
        self.candidate = scaffold_module.scaffold(self.project)
        self.paths = list(self.candidate['file_contents'])
        self.feature = self.project / next(p for p in self.paths if '/features/' in p)
        self.page = self.project / next(p for p in self.paths if '/ui/' in p)

    def change_source(self):
        self.source_file.write_text(self.source_file.read_text(encoding='utf-8').replace('hello', 'changed'),
                                    encoding='utf-8')

    def assert_no_outputs(self, except_paths=()):
        for relative in self.paths:
            path = self.project / relative
            if path not in except_paths:
                self.assertFalse(path.exists(), relative)

    def during_page_mkdir(self, action):
        original = Path.mkdir
        fired = []
        def interleave(path, *args, **kwargs):
            result = original(path, *args, **kwargs)
            if path == self.page.parent and not fired:
                fired.append(True)
                action()
            return result
        return patch.object(Path, 'mkdir', interleave)

    def test_index_file_metadata_and_membership_must_match_even_when_hash_matches(self):
        path = self.project / 'spec/baseline/ios-source-index.json'
        original = read_json(path)
        for mutation in ('hash', 'size', 'missing', 'duplicate'):
            with self.subTest(mutation=mutation):
                data = json.loads(json.dumps(original))
                if mutation == 'hash':
                    data['files'][0]['sha256'] = '0' * 64
                elif mutation == 'size':
                    data['files'][0]['bytes'] += 1
                elif mutation == 'missing':
                    data['files'] = []
                else:
                    data['files'].append(dict(data['files'][0]))
                write_json(path, data)
                for operation in (lambda: scaffold_module.scaffold(self.project),
                                  lambda: scaffold_module.apply_scaffold(self.project, self.candidate)):
                    with self.assertRaisesRegex(MigrationError, 'index files disagree'):
                        operation()
                self.assert_no_outputs()
        write_json(path, original)

    def test_different_existing_page_id_is_preserved_and_does_not_conflict(self):
        existing = self.page.parent / 'page_9999_Other.md'
        existing.parent.mkdir(parents=True)
        existing.write_text('existing unrelated page', encoding='utf-8')
        with self.assertRaisesRegex(MigrationError, 'file set'):
            scaffold_module.apply_scaffold(self.project, self.candidate)
        self.candidate = scaffold_module.scaffold(self.project)
        result = scaffold_module.apply_scaffold(self.project, self.candidate)
        self.assertTrue(result['created'])
        self.assertEqual(existing.read_text(), 'existing unrelated page')

    def test_same_page_id_with_different_name_is_rejected_before_any_write(self):
        existing = self.page.parent / 'page_0001_Other.md'
        existing.parent.mkdir(parents=True)
        existing.write_text('existing owner', encoding='utf-8')
        with self.assertRaisesRegex(MigrationError, 'page_0001'):
            scaffold_module.apply_scaffold(self.project, self.candidate)
        self.assert_no_outputs()
        self.assertEqual(existing.read_text(), 'existing owner')

    def test_new_competing_document_is_not_overwritten_and_earlier_files_roll_back(self):
        with self.during_page_mkdir(lambda: self.page.write_text('HUMAN DRAFT', encoding='utf-8')):
            with self.assertRaisesRegex(MigrationError, 'rolled back'):
                scaffold_module.apply_scaffold(self.project, self.candidate)
        self.assertEqual(self.page.read_text(), 'HUMAN DRAFT')
        self.assert_no_outputs(except_paths=(self.page,))

    def test_source_change_after_discovery_does_not_publish_candidate(self):
        discover = scaffold_module.discover_candidates
        def changing_discovery(*args):
            result = discover(*args)
            self.change_source()
            return result
        with patch.object(scaffold_module, 'discover_candidates', changing_discovery):
            with self.assertRaises(MigrationError):
                scaffold_module.scaffold(self.project)
        self.assert_no_outputs()

    def test_source_change_after_preflight_is_rejected_before_write(self):
        conflict = scaffold_module._fid_conflict
        def changing_preflight(base, path):
            result = conflict(base, path)
            if path == 'spec/baseline/ui-manifest.md':
                self.change_source()
            return result
        with patch.object(scaffold_module, '_fid_conflict', changing_preflight):
            with self.assertRaises(MigrationError):
                scaffold_module.apply_scaffold(self.project, self.candidate)
        self.assert_no_outputs()

    def test_source_change_during_apply_rolls_back_its_new_outputs(self):
        with self.during_page_mkdir(self.change_source):
            with self.assertRaises(MigrationError):
                scaffold_module.apply_scaffold(self.project, self.candidate)
        self.assert_no_outputs()

    def test_rollback_retains_another_authors_edit_to_our_new_file(self):
        def competing_edit():
            self.feature.write_text('HUMAN EDIT AFTER CREATION', encoding='utf-8')
            self.change_source()
        with self.during_page_mkdir(competing_edit):
            with self.assertRaisesRegex(MigrationError, 'retained changed/unremovable files'):
                scaffold_module.apply_scaffold(self.project, self.candidate)
        self.assertEqual(self.feature.read_text(), 'HUMAN EDIT AFTER CREATION')
        self.assert_no_outputs(except_paths=(self.feature,))

    def test_rollback_retains_replacement_even_with_identical_contents(self):
        def replace_created_file():
            contents = self.feature.read_bytes()
            # Keep the original alive at another name so its file identity cannot
            # be immediately recycled for the other author's replacement.
            self.feature.rename(self.feature.with_suffix('.moved'))
            self.feature.write_bytes(contents)
            self.change_source()
        with self.during_page_mkdir(replace_created_file):
            with self.assertRaisesRegex(MigrationError, 'retained changed/unremovable files'):
                scaffold_module.apply_scaffold(self.project, self.candidate)
        self.assertTrue(self.feature.is_file())
        self.assert_no_outputs(except_paths=(self.feature,))

    def test_interruption_rolls_back_files_already_created(self):
        def interrupt():
            raise KeyboardInterrupt('synthetic cancellation')
        with self.during_page_mkdir(interrupt):
            with self.assertRaises(KeyboardInterrupt):
                scaffold_module.apply_scaffold(self.project, self.candidate)
        self.assert_no_outputs()

    def test_partial_write_failure_removes_only_its_own_prefix(self):
        original_open = Path.open
        class PartialFailure:
            def __init__(self, stream):
                self.stream, self.writes = stream, 0
            def __enter__(self):
                self.stream.__enter__()
                return self
            def __exit__(self, *args):
                return self.stream.__exit__(*args)
            def fileno(self):
                return self.stream.fileno()
            def write(self, data):
                self.writes += 1
                if self.writes == 1:
                    return self.stream.write(data[:7])
                raise OSError('synthetic full disk')
        def failing_open(path, mode='r', *args, **kwargs):
            stream = original_open(path, mode, *args, **kwargs)
            return PartialFailure(stream) if path == self.feature and mode == 'xb' else stream
        with patch.object(Path, 'open', failing_open):
            with self.assertRaisesRegex(MigrationError, 'full disk'):
                scaffold_module.apply_scaffold(self.project, self.candidate)
        self.assert_no_outputs()


if __name__ == '__main__':
    unittest.main()
