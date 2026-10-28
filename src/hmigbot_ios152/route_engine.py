"""Shared invocation of the bundled original HMigBot route engine."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import platform
import subprocess

from hmigbot_ios.core import MigrationError


def roots(scripts, argv):
    parser = argparse.ArgumentParser(add_help=False)
    for name in ('out-dir', 'hmos-root', 'ios-root', 'android-root', 'src', 'platform'):
        parser.add_argument('--' + name)
    args, _ = parser.parse_known_args(argv)
    root = Path(args.hmos_root or os.environ.get('ROUTE_VERIFY_ROOT') or Path.cwd()).resolve()
    if not args.hmos_root and not os.environ.get('ROUTE_VERIFY_ROOT'):
        anchored = next((p for p in [Path(scripts), *Path(scripts).parents] if (p / '.agents').is_dir()), None)
        if anchored:
            root = anchored
    out = Path(args.out_dir or os.environ.get('ROUTE_VERIFY_OUT') or root / 'spec/verify/route').resolve()
    return args, root, out


def compiled(scripts, stage, argv=(), env=None):
    system = {'Darwin': 'macos', 'Linux': 'linux', 'Windows': 'windows'}.get(platform.system())
    arch = 'arm64' if platform.machine().lower() in {'arm64', 'aarch64'} else 'x64'
    exe = Path(scripts) / 'bin' / (system + '-' + arch) / '_entry.dist' / ('_entry.exe' if system == 'windows' else '_entry.bin')
    if not exe.is_file():
        raise MigrationError('Missing original route engine: ' + str(exe))
    if system == 'macos':
        subprocess.run(['xattr', '-dr', 'com.apple.quarantine', str(exe.parent)], capture_output=True, check=False)
    return subprocess.run([str(exe), stage, *argv], env={**os.environ, 'ARKTS_SKILL_DIR': str(scripts), **(env or {})},
                          capture_output=True, text=True)
