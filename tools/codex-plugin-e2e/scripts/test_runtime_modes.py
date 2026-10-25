"""Installer transaction tests. Tiny inert payloads are never executed as gates."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('installer', ROOT / 'scripts/manage_install.py')
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class RuntimeModes(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'package'
        self.workspace = Path(self.temp.name) / 'workspace'
        self.workspace.mkdir()
        (self.workspace / 'AGENTS.md').write_text('User instructions\n')
        self.files = {}
        records = {}
        self.lib = '.agents/skills/neutral/scripts/bin/macos-arm64/_entry.dist/Python'
        for relative, installed, execute in [
            ('bin/a2h-darwin-arm64', '.migbot/bin/a2h', True),
            ('skills/a2h-spec/scripts/bin/macos-arm64/_entry.dist/_entry.bin',
             '.agents/skills/a2h-spec/scripts/bin/macos-arm64/_entry.dist/_entry.bin', True),
            ('skills/neutral/scripts/bin/macos-arm64/_entry.dist/Python', self.lib, False),
        ]:
            source = self.root / relative
            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_bytes(b'\xcf\xfa\xed\xfe' + relative.encode())
            source.chmod(0o755)  # Deliberately polluted packaging permissions.
            self.files[installed] = source
            records[relative] = {'sha256': hashlib.sha256(source.read_bytes()).hexdigest(), 'executable': execute}
        for relative, value in [('docs/macos-runtime-modes.json', {'files': records}),
                                ('.codex-plugin/plugin.json', {'version': '1.5.2-ios.20'})]:
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(value))
        installer.runtime_modes.cache_clear()
        for replacement in [patch.object(installer, 'ROOT', self.root),
                            patch.object(installer, 'payload', return_value=self.files),
                            patch.object(installer, 'native_runtime_member', side_effect=lambda n, d: n in self.files),
                            patch.object(installer, 'prepare_native_execution', return_value={})]:
            replacement.start()
            self.addCleanup(replacement.stop)
        self.addCleanup(installer.runtime_modes.cache_clear)

    def install(self):
        return installer.manage(self.workspace, 'install')

    def test_polluted_source_and_mode_only_upgrade(self):
        self.install()
        lib = self.workspace / self.lib
        self.assertFalse(lib.stat().st_mode & 0o111)
        metadata = self.workspace / '.hmigbot-ios/install.json'
        old = json.loads(metadata.read_text())
        old.pop('file_modes')
        old['version'] = '1.5.2-ios.18'
        metadata.write_text(json.dumps(old))
        lib.chmod(0o755)
        content = lib.read_bytes()
        self.install()
        self.assertEqual(lib.read_bytes(), content)
        self.assertFalse(lib.stat().st_mode & 0o111)

    def test_reinstall_and_non_execution_mode_difference(self):
        self.install()
        lib = self.workspace / self.lib
        lib.chmod(0o664)
        before = lib.stat().st_mtime_ns
        self.install()
        self.assertEqual(lib.stat().st_mtime_ns, before)
        self.assertEqual(lib.stat().st_mode & 0o777, 0o664)

    def test_source_without_execution_bits(self):
        for source in self.files.values():
            source.chmod(0o644)
        self.install()
        self.assertTrue((self.workspace / '.migbot/bin/a2h').stat().st_mode & 0o111)
        self.assertFalse((self.workspace / self.lib).stat().st_mode & 0o111)

    def test_content_edits_still_refused(self):
        self.install()
        lib = self.workspace / self.lib
        lib.write_bytes(lib.read_bytes() + b'user edit')
        with self.assertRaisesRegex(ValueError, 'user-edited'):
            self.install()
        self.assertTrue(lib.read_bytes().endswith(b'user edit'))

    def test_late_failure_restores_original_mode_and_metadata(self):
        self.install()
        lib = self.workspace / self.lib
        lib.chmod(0o755)
        metadata = self.workspace / '.hmigbot-ios/install.json'
        original = metadata.read_bytes()
        agents = (self.workspace / 'AGENTS.md').read_bytes()
        with patch.object(installer, 'prepare_native_execution', side_effect=ValueError('injected late failure')):
            with self.assertRaisesRegex(ValueError, 'injected late failure'):
                self.install()
        self.assertEqual(lib.stat().st_mode & 0o777, 0o755)
        self.assertEqual(metadata.read_bytes(), original)
        self.assertEqual((self.workspace / 'AGENTS.md').read_bytes(), agents)


if __name__ == '__main__':
    unittest.main()
