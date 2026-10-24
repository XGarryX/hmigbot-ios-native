"""Direct Xcode capture lifecycle, with real Clang AST observations."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(os.environ.get('HMIGBOT_TEST_RUNTIME', Path(__file__).resolve().parents[1])).resolve()
sys.path.insert(0, str(ROOT / 'src'))
from hmigbot_ios.core import MigrationError, snapshot
from hmigbot_ios.providers import clang_ast, xcodebuild_settings


class DirectProviderTests(unittest.TestCase):
    def test_response_header_and_ast_are_consumed_before_derived_data_cleanup(self):
        compiler = shutil.which('clang')
        if not compiler:
            self.skipTest('Real Clang unavailable')
        compiler = str(Path(compiler).resolve())
        real_run = subprocess.run
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            source = root / 'Main.c'
            source.write_text('#include "Generated.h"\nint result = VALUE;\n')
            config = root / 'provider.json'
            config.write_text(json.dumps({'xcodebuild': {'project': 'Example.xcodeproj'},
                                          'version_command': [compiler, '--version']}))
            seen = []
            def run(command, **kwargs):
                if command[0] != 'xcodebuild':
                    return real_run(command, **kwargs)
                derived = Path(command[command.index('-derivedDataPath') + 1])
                seen.append(derived)
                (derived / 'Generated.h').write_text('#define VALUE 41\n')
                response = derived / 'common.rsp'
                import shlex
                response.write_text('-I ' + shlex.quote(str(derived)))
                args = [compiler, '@' + str(response), '-c', str(source), '-o', str(derived / 'Main.o')]
                return subprocess.CompletedProcess(command, 0, shlex.join(args).encode(), b'')
            with patch('hmigbot_ios.providers.subprocess.run', side_effect=run):
                value, issues, payload = clang_ast(root, snapshot(root)['files'], config)
            self.assertFalse(issues)
            ast = json.loads(next(v for k, v in payload.items() if k.endswith('.stdout.json')))
            declarations = [n for n in ast['inner'] if n.get('kind') == 'VarDecl']
            self.assertEqual(declarations[0]['name'], 'result')
            self.assertEqual(declarations[0]['inner'][0]['value'], '41')
            self.assertEqual(value['xcodebuild_capture']['exit_code'], 0)
            self.assertTrue(all(not path.exists() for path in seen))
            self.assertFalse((root / 'Main.o').exists())

    def test_failed_build_does_not_supply_successful_ast_evidence(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config = root / 'config.json'
            config.write_text(json.dumps({'xcodebuild': {'project': 'Example.xcodeproj'}}))
            failed = subprocess.CompletedProcess([], 65, b'/usr/bin/clang -c fake.c', b'build failed')
            with patch('hmigbot_ios.providers.subprocess.run', return_value=failed) as run:
                with self.assertRaisesRegex(MigrationError, 'xcodebuild failed'):
                    clang_ast(root, [], config)
                self.assertEqual(run.call_count, 1)

    def test_settings_preserve_selection_and_actual_failure(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'Example.xcodeproj').mkdir()
            response = subprocess.CompletedProcess([], 0, json.dumps([
                {'target': 'Example', 'buildSettings': {'ARCHS': 'arm64'}}]).encode(), b'warning')
            with patch('hmigbot_ios.providers.subprocess.run', return_value=response) as run:
                value = xcodebuild_settings(root, {})
                self.assertEqual(value['selection']['configuration'], 'Debug')
                self.assertIn('-showBuildSettings', run.call_args.args[0])
                self.assertEqual(value['xcodebuild_stderr'], 'warning')
            with patch('hmigbot_ios.providers.subprocess.run', return_value=subprocess.CompletedProcess([], 65, b'', b'bad SDK')):
                with self.assertRaisesRegex(MigrationError, 'bad SDK'):
                    xcodebuild_settings(root, {})
