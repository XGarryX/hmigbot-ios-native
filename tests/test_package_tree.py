"""The source directory owns the package layout, bytes and metadata."""
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(os.environ.get('HMIGBOT_TEST_RUNTIME', Path(__file__).resolve().parents[1])).resolve()
sys.path.insert(0, str(ROOT / 'scripts'))
import package_tree


class PackageTreeTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='source package 中文 ')
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name).resolve()
        self.source = self.base / 'hmigbot-ios-main'
        self.source.mkdir()
        (self.source / 'new-configuration.json').write_text('{"new":true}\n')
        (self.source / 'binary.plist').write_bytes(b'bplist00\x80\xff')
        (self.source / 'empty-directory').mkdir()
        (self.source / 'helper.sh').write_text('#!/bin/sh\nexit 0\n')
        (self.source / 'helper.sh').chmod(0o640)
        os.utime(self.source / 'helper.sh', (1600000001, 1600000001))
        self.output = self.base / 'delivery.zip'

    def test_source_name_new_root_file_binary_empty_directory_and_metadata_are_preserved(self):
        result = package_tree.build_package(self.source, self.output)
        self.assertEqual(result['status'], 'passed')
        self.assertEqual(result['source_root_name'], self.source.name)
        with zipfile.ZipFile(self.output) as archive:
            self.assertEqual(archive.read('hmigbot-ios-main/binary.plist'), b'bplist00\x80\xff')
            self.assertIn('hmigbot-ios-main/new-configuration.json', archive.namelist())
            self.assertIn('hmigbot-ios-main/empty-directory/', archive.namelist())
            info = archive.getinfo('hmigbot-ios-main/helper.sh')
            self.assertEqual(info.external_attr >> 16 & 0o777, (self.source / 'helper.sh').stat().st_mode & 0o777)
            expected = zipfile.ZipInfo.from_file(self.source / 'helper.sh').date_time
            self.assertEqual(info.date_time, (*expected[:5], expected[5] & ~1))

    def test_only_declared_local_artifacts_are_excluded_and_listed(self):
        (self.source / '.DS_Store').write_bytes(b'local')
        (self.source / '__pycache__').mkdir()
        (self.source / '__pycache__/local.pyc').write_bytes(b'cache')
        result = package_tree.build_package(self.source, self.output)
        self.assertEqual({item['path'] for item in result['excluded']}, {'.DS_Store', '__pycache__'})
        self.assertEqual(result['files'], 3)

    def test_modified_added_and_deleted_source_files_are_detected(self):
        package_tree.build_package(self.source, self.output)
        (self.source / 'binary.plist').write_bytes(b'changed')
        (self.source / 'new-configuration.json').unlink()
        (self.source / 'added.txt').write_text('new')
        result = package_tree.verify_package(self.output, self.source)
        self.assertEqual(result['status'], 'failed')
        self.assertEqual({item['path'] for item in result['differences'] if 'path' in item}, {'binary.plist', 'new-configuration.json', 'added.txt'})

    def test_archive_tampering_and_wrong_root_are_rejected(self):
        package_tree.build_package(self.source, self.output)
        with zipfile.ZipFile(self.output, 'a') as archive:
            archive.writestr('hmigbot-ios-main/injected.txt', b'injected')
        result = package_tree.verify_package(self.output)
        self.assertEqual(result['status'], 'failed')
        self.assertIn('archive-checksum', [item['rule'] for item in result['differences']])
        manifest_path = package_tree.sidecars(self.output)[1]
        manifest = json.loads(manifest_path.read_text())
        manifest['source_root_name'] = '../elsewhere'
        manifest_path.write_text(json.dumps(manifest))
        with self.assertRaises(ValueError):
            package_tree.verify_package(self.output)

    def test_in_source_output_overwrite_and_links_are_rejected(self):
        with self.assertRaises(ValueError):
            package_tree.build_package(self.source, self.source / 'archive.zip')
        self.output.write_bytes(b'existing delivery')
        with self.assertRaises(ValueError):
            package_tree.build_package(self.source, self.output)
        self.assertEqual(self.output.read_bytes(), b'existing delivery')
        if os.name != 'nt':
            (self.source / 'linked.txt').symlink_to(self.output)
            with self.assertRaises(ValueError):
                package_tree.inventory(self.source)

    def test_source_mutation_during_build_cannot_get_completion_sidecars(self):
        real = package_tree.inventory
        calls = []
        def changing(root):
            if calls:
                (self.source / 'binary.plist').write_bytes(b'concurrent change')
            calls.append(True)
            return real(root)
        with patch.object(package_tree, 'inventory', side_effect=changing):
            with self.assertRaises(ValueError):
                package_tree.build_package(self.source, self.output)
        self.assertFalse(any(path.exists() for path in package_tree.sidecars(self.output)))


if __name__ == '__main__':
    unittest.main()
