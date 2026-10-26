"""Public validation entry, real setup implementation, macOS bash 3.2."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


class NativeValidateEntry(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='native entry check ')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.workspace = self.base / 'workspace with spaces'
        self.workspace.mkdir()
        self.runtime = self.workspace / '.agents/hmigbot-runtime'
        self.install_runtime(self.runtime)
        self.entry = self.workspace / '.migbot/bin/a2h-tool'
        self.entry.parent.mkdir(parents=True)
        shutil.copy2(ROOT / 'bin/a2h-tool', self.entry)
        (self.workspace / 'source').mkdir()
        (self.workspace / 'hvigorw').write_text('# path probe only, never executed\n')
        (self.workspace / '.migbot/config.json').write_text(json.dumps({
            'source_platform': 'ios', 'tool_package': 'hmigbot-ios152', 'ios': {'source_root': 'source'},
            'harmonyos': '.', 'hvigorw': 'hvigorw'}))
        (self.workspace / '.hmigbot-ios').mkdir()
        (self.workspace / '.hmigbot-ios/install.json').write_text('{}')

    def install_runtime(self, path):
        for rel in ['scripts/ios_setup.py', 'src/hmigbot_ios152/setup.py']:
            target = path / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / rel, target)

    def run_entry(self, *args, cwd=None, entry=None):
        return subprocess.run(['/bin/bash', str(entry or self.entry), 'validate', *map(str, args)],
                              cwd=cwd or self.workspace, capture_output=True, text=True,
                              env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1', 'A2H_SKIP_EMU_CHECK': '1'}, timeout=15)

    def assert_valid(self, result):
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(json.loads(result.stdout)['ok'])
        self.assertFalse(json.loads(result.stdout)['source_build_verified'])

    def test_project_root(self):
        self.assert_valid(self.run_entry())

    def test_other_cwd_uses_installed_workspace(self):
        self.assert_valid(self.run_entry(cwd=self.base))

    def test_relative_symlink_uses_installed_workspace(self):
        link = self.base / 'entry link'
        link.symlink_to('workspace with spaces/.migbot/bin/a2h-tool')
        self.assert_valid(self.run_entry(cwd=self.base, entry=link))

    def test_same_workspace_and_language_forwarded(self):
        self.assert_valid(self.run_entry('--workspace', self.workspace / 'source/..', '--lang', 'en', cwd=self.base))

    def test_conflicting_workspace_rejected(self):
        result = self.run_entry('--workspace', self.base)
        self.assertEqual(result.returncode, 2)
        self.assertIn('conflicts', result.stdout)

    def test_conflicting_duplicate_workspace_cannot_be_hidden(self):
        result = self.run_entry('--workspace', self.base, '--workspace', self.workspace)
        self.assertEqual(result.returncode, 2)
        self.assertIn('conflicts', result.stdout)

    def test_missing_runtime_never_falls_back_to_android(self):
        shutil.rmtree(self.runtime)
        result = self.run_entry()
        self.assertEqual(result.returncode, 2)
        self.assertIn('iOS runtime missing', result.stderr)
        self.assertNotIn('android 路径未设置', result.stdout + result.stderr)

    def test_old_install_layout(self):
        shutil.rmtree(self.runtime)
        self.install_runtime(self.workspace / '.hmigbot-ios/plugin')
        self.assert_valid(self.run_entry(cwd=self.base))

    def test_source_package_entry_uses_current_workspace(self):
        shutil.rmtree(self.runtime)
        self.assert_valid(self.run_entry(entry=ROOT / 'bin/a2h-tool'))

    def test_source_package_explicit_workspace_from_elsewhere(self):
        self.assert_valid(self.run_entry('--workspace', self.workspace, cwd=self.base, entry=ROOT / 'bin/a2h-tool'))

    def test_cdpath_does_not_pollute_resolution(self):
        with patch.dict(os.environ, {'CDPATH': str(self.base)}):
            self.assert_valid(self.run_entry(cwd=self.base))

    def test_abbreviated_workspace_is_rejected(self):
        self.assertEqual(self.run_entry('--works', self.workspace).returncode, 2)

    def test_old_ios_config_missing_runtime_cannot_fall_back(self):
        shutil.rmtree(self.runtime)
        shutil.rmtree(self.workspace / '.hmigbot-ios')
        (self.workspace / '.migbot/config.json').write_text(json.dumps({'ios': {'source_root': 'source'}}))
        result = self.run_entry()
        self.assertEqual(result.returncode, 2)
        self.assertIn('iOS runtime missing', result.stderr)

    def test_malformed_config_missing_runtime_cannot_fall_back(self):
        shutil.rmtree(self.runtime)
        shutil.rmtree(self.workspace / '.hmigbot-ios')
        (self.workspace / '.migbot/config.json').write_text('{')
        result = self.run_entry()
        self.assertEqual(result.returncode, 2)
        self.assertIn('invalid configuration', result.stderr)

    def test_legacy_android_branch_remains_available_without_ios_markers(self):
        shutil.rmtree(self.runtime)
        shutil.rmtree(self.workspace / '.hmigbot-ios')
        (self.workspace / '.migbot/config.json').write_text(json.dumps({'language': 'zh'}))
        result = self.run_entry()
        self.assertEqual(result.returncode, 1)
        self.assertIn('android 路径未设置', result.stdout)


if __name__ == '__main__':
    unittest.main()
