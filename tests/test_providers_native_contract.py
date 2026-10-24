import json
from pathlib import Path
import plistlib
import shutil
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from hmigbot_ios.core import MigrationError, json_bytes, snapshot
from hmigbot_ios.providers import swift_syntax
from hmigbot_ios.iphone import inspect_ipa
from hmigbot_ios.capture import capture


class ProviderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'ios'
        self.source.mkdir()
        (self.source / 'Unicode.swift').write_bytes('import Foundation\r\nstruct 你好 {}\r\n'.encode())

    def test_provider_preserves_crlf_utf8_bytes_and_rejects_missing_files(self):
        script = self.root / 'provider.py'
        script.write_text('''import json, sys, hashlib
request = json.load(sys.stdin.buffer)
files = []
for item in request['files']:
    assert hashlib.sha256(item['source'].encode()).hexdigest() == item['sha256']
    files.append({'path':item['path'], 'sha256':item['sha256'], 'parse_has_error':False,
        'nodes':[{'start_utf8':0, 'end_utf8':len(item['source'].encode()), 'line':1}]})
print(json.dumps({'protocol_version':1,'provider':'SwiftSyntax','semantic_resolution':False,'files':files}))
''', encoding='utf-8')
        config = self.root / 'provider.json'
        config.write_bytes(json_bytes({'command': [sys.executable, str(script)], 'version_command': [sys.executable, '--version']}))
        value, issues = swift_syntax(self.source, snapshot(self.source)['files'], config)
        self.assertFalse(issues)
        self.assertEqual(value['files'][0]['nodes'][0]['end_utf8'], len((self.source / 'Unicode.swift').read_bytes()))
        script.write_text('import json; print(json.dumps({"protocol_version":1,"provider":"SwiftSyntax","semantic_resolution":False,"files":[]}))')
        with self.assertRaises(MigrationError):
            swift_syntax(self.source, snapshot(self.source)['files'], config)

    def make_ipa(self, platform=2, profile=False):
        path = self.root / ('fixture-' + str(platform) + '.ipa')
        info = {'CFBundleExecutable': 'App', 'CFBundleIdentifier': 'com.example.fixture', 'CFBundleSupportedPlatforms': ['iPhoneOS'], 'MinimumOSVersion': '17.0'}
        macho = struct.pack('<8I', 0xfeedfacf, 0x0100000c, 0, 2, 1, 24, 0, 0) + struct.pack('<6I', 0x32, 24, platform, 0, 0, 0)
        with zipfile.ZipFile(path, 'w') as archive:
            archive.writestr('Payload/App.app/Info.plist', plistlib.dumps(info))
            archive.writestr('Payload/App.app/App', macho)
            if profile:
                archive.writestr('Payload/App.app/embedded.mobileprovision', b'not a valid profile')
        return path

    def test_ipa_profile_presence_does_not_certify_signature(self):
        result = inspect_ipa(self.make_ipa(profile=True))
        self.assertEqual(result['status'], 'device_ipa_structure_valid')
        self.assertTrue(result['bundles'][0]['provisioning_profile_present'])
        self.assertEqual(result['signature_validity'], 'not_verified')

    def test_arm64_simulator_cannot_masquerade_as_device_ipa(self):
        with self.assertRaises(MigrationError):
            inspect_ipa(self.make_ipa(platform=7))

    def test_capture_runs_actual_provider_and_records_failure(self):
        config = self.root / 'capture.json'
        config.write_bytes(json_bytes({'command': [sys.executable, '-c', 'print("actual provider stdout")'], 'version_command': [sys.executable, '--version']}))
        result = capture(self.source, config, self.root / 'pass', 'source_tests')
        self.assertEqual(result['status'], 'captured')
        self.assertEqual((self.root / 'pass/artifacts/provider.stdout.log').read_text().strip(), 'actual provider stdout')
        config.write_bytes(json_bytes({'command': [sys.executable, '-c', 'raise SystemExit(5)'], 'version_command': [sys.executable, '--version']}))
        result = capture(self.source, config, self.root / 'fail', 'source_tests')
        self.assertEqual(result['exit_code'], 5)
        self.assertEqual(result['status'], 'capture_failed')
        self.assertFalse((self.root / 'fail/evidence').exists())

    def test_source_changed_during_capture_is_not_bound_to_new_source(self):
        config = self.root / 'capture.json'
        command = [sys.executable, '-c', 'from pathlib import Path; Path("changed").write_text("x")']
        config.write_bytes(json_bytes({'command': command, 'version_command': [sys.executable, '--version']}))
        result = capture(self.source, config, self.root / 'capture', 'source_trace')
        self.assertEqual(result['status'], 'capture_failed')
        self.assertTrue(result['source_changed'])

    def test_all_installed_skill_wrappers_resolve_same_runtime(self):
        sys.path.insert(0, str(ROOT / 'scripts'))
        import manage_install
        from install_fixture import small_payload
        workspace = self.root / 'workspace'
        workspace.mkdir()
        with small_payload(manage_install):
            result = manage_install.manage(workspace, 'install')
        self.assertEqual(result['skills'], 4)
        import subprocess
        for name in ('ios-source-analysis', 'ios-resources-convert', 'ios-ui-to-arkui'):
            skill = workspace / '.agents/skills' / name
            proc = subprocess.run([sys.executable, str(skill / 'scripts/run.py'), '--runtime-root'], capture_output=True)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(Path(proc.stdout.decode().strip()), (workspace / '.hmigbot-ios/plugin').resolve())


if __name__ == '__main__':
    unittest.main()
