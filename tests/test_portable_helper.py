"""Real compiled payload in a Unicode location, without changing vendor bytes."""
import hashlib
import os
from pathlib import Path
import platform
import shutil
import sys
import tempfile
import unittest

ROOT = Path(os.environ.get('HMIGBOT_TEST_RUNTIME', Path(__file__).resolve().parents[1])).resolve()
sys.path.insert(0, str(ROOT / 'src'))
from hmigbot_ios.portable_helper import command, run


@unittest.skipUnless(platform.system() == 'Darwin', 'macOS standalone binary path regression')
class PortableHelperTests(unittest.TestCase):
    def test_unicode_payload_executes_original_helper_and_keeps_bytes(self):
        architecture = 'arm64' if platform.machine().lower() in {'arm64', 'aarch64'} else 'x64'
        source = ROOT / 'vendor/hmigbot/skills/a2h-spec/scripts'
        with tempfile.TemporaryDirectory(prefix='portable 原工具 ') as temporary:
            scripts = Path(temporary).resolve() / 'scripts'
            payload = scripts / 'bin' / ('macos-' + architecture) / '_entry.dist'
            shutil.copytree(source / 'bin' / ('macos-' + architecture) / '_entry.dist', payload)
            helper = scripts / 'lint_addenda_closure.py'
            shutil.copy2(source / helper.name, helper)
            before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in payload.iterdir() if p.is_file()}
            with command(helper, ['--help']) as (argv, _):
                staged = Path(argv[0])
                self.assertTrue(str(staged).isascii())
                self.assertEqual(staged.read_bytes(), (payload / '_entry.bin').read_bytes())
            self.assertFalse(staged.exists())
            result = run(helper, ['--help'], capture_output=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(b'--spec', result.stdout)
            self.assertEqual(before, {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in payload.iterdir() if p.is_file()})
