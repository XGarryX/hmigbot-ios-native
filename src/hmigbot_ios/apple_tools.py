"""Thin process adapters to the selected, installed Apple toolchain on macOS."""
from __future__ import annotations

import fcntl
from dataclasses import dataclass
from functools import lru_cache
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import tempfile

from .core import MigrationError, digest, json_bytes


def run(argv, *, data=None, env=None, timeout=120, cwd=None):
    try:
        result = subprocess.run(argv, input=data, capture_output=True, env=env,
                                timeout=timeout, cwd=cwd, shell=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise MigrationError(f'Apple tool unavailable: {argv[0]}: {exc}') from exc
    if result.returncode:
        detail = (result.stderr or result.stdout).decode('utf-8', errors='replace')[-3000:]
        raise MigrationError(f'Apple tool failed ({result.returncode}): {argv!r}\n{detail}')
    return result


def toolchain(developer_override=None):
    checked_environment()
    return _toolchain(developer_override)


def checked_environment():
    env = os.environ.copy()
    for name in ('XCODE_XCCONFIG_FILE', 'TOOLCHAINS'):
        if env.get(name):
            raise MigrationError('Unbound Apple toolchain/configuration override: ' + name)
    return env


@lru_cache(maxsize=8)
def _toolchain(developer_override=None):
    if platform.system() != 'Darwin':
        raise MigrationError('This distribution requires macOS and full Xcode')
    env = checked_environment()
    if developer_override:
        developer = Path(developer_override).resolve()
    else:
        selected = run(['/usr/bin/xcode-select', '-p']).stdout.decode().strip()
        developer = Path(selected)
        if not (developer / 'usr/bin/xcodebuild').is_file():
            # xcode-select can legitimately select CLT while full Xcode is installed.
            candidates = [Path('/Applications/Xcode.app/Contents/Developer')]
            found = run(['/usr/bin/mdfind', 'kMDItemCFBundleIdentifier == "com.apple.dt.Xcode"']).stdout.decode().splitlines()
            candidates += [Path(p) / 'Contents/Developer' for p in found]
            candidates = sorted({p.resolve() for p in candidates if (p / 'usr/bin/xcodebuild').is_file()})
            if len(candidates) != 1:
                raise MigrationError('Select one full Xcode with DEVELOPER_DIR')
            developer = candidates[0]
    if not (developer / 'usr/bin/xcodebuild').is_file():
        raise MigrationError('DEVELOPER_DIR does not identify full Xcode: ' + str(developer))
    env['DEVELOPER_DIR'] = str(developer)
    version = run(['/usr/bin/xcodebuild', '-version'], env=env).stdout.decode().strip()
    swiftc = run(['/usr/bin/xcrun', '--find', 'swiftc'], env=env).stdout.decode().strip()
    swift_version = run([swiftc, '--version'], env=env).stdout.decode().strip()
    sdk = run(['/usr/bin/xcrun', '--sdk', 'iphoneos', '--show-sdk-path'], env=env).stdout.decode().strip()
    mac_sdk = run(['/usr/bin/xcrun', '--sdk', 'macosx', '--show-sdk-path'], env=env).stdout.decode().strip()
    host = Path(swiftc).resolve().parent.parent / 'lib/swift/host'
    if not (host / 'libSwiftSyntax.dylib').is_file() or not (host / 'libSwiftIfConfig.dylib').is_file():
        raise MigrationError('Selected Xcode does not supply the required Swift source tools: ' + str(host))
    return {'developer_dir': str(developer), 'xcode_version': version, 'swiftc': swiftc,
            'swift_version': swift_version, 'sdk': sdk, 'mac_sdk': mac_sdk, 'host_libraries': str(host)}


def environment():
    env = checked_environment()
    info = toolchain(os.environ.get('DEVELOPER_DIR'))
    env['DEVELOPER_DIR'] = info['developer_dir']
    return info, env


def provider():
    info, env = environment()
    root = Path(__file__).resolve().parents[2]
    sources = sorted(p for p in (root / 'providers/swift-syntax').glob('*.swift') if p.name != 'Package.swift')
    if not sources:
        raise MigrationError('Bundled SwiftSyntax provider sources are missing')
    identity = {**info, 'sources': {p.name: digest(p.read_bytes()) for p in sources}}
    key = digest(json_bytes(identity))
    cache = Path(os.environ.get('HMIGBOT_APPLE_CACHE', Path.home() / 'Library/Caches/hmigbot-ios')) / 'swift-syntax' / key
    cache.mkdir(parents=True, exist_ok=True)
    binary, record = cache / 'hmigbot-swift-syntax', cache / 'build.json'
    with (cache / 'build.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        valid = False
        if binary.is_file() and record.is_file():
            try:
                previous = json.loads(record.read_text())
                valid = previous['identity'] == identity and previous['binary_sha256'] == digest(binary.read_bytes())
            except (OSError, ValueError, KeyError):
                pass
        if not valid:
            temporary = cache / ('provider-' + str(os.getpid()))
            argv = [info['swiftc'], '-O', '-sdk', info['mac_sdk'], '-I', info['host_libraries'], '-L', info['host_libraries'],
                    '-Xlinker', '-rpath', '-Xlinker', info['host_libraries'],
                    *map(str, sources), '-o', str(temporary)]
            result = run(argv, env=env, timeout=240)
            temporary.chmod(0o755)
            os.replace(temporary, binary)
            record.write_bytes(json_bytes({'identity': identity, 'argv': argv, 'exit_code': result.returncode,
                'stdout': result.stdout.decode(), 'stderr': result.stderr.decode(),
                'binary_sha256': digest(binary.read_bytes())}))
    return binary, info, env


def syntax(files):
    binary, info, env = provider()
    result = run([str(binary)], data=json_bytes({'files': files}), env=env)
    try:
        value = json.loads(result.stdout)
    except (ValueError, UnicodeError) as exc:
        raise MigrationError('Official Swift provider did not return JSON') from exc
    if value.get('schema_version') != 2 or value.get('provider') != 'SwiftSyntax' or value.get('semantic_resolution') is not False:
        raise MigrationError('Unexpected official Swift syntax protocol')
    expected = {f['path']: f for f in files}
    found = {}
    for item in value.get('files', []):
        name = item.get('path')
        if name not in expected or name in found or item.get('sha256') != expected[name]['sha256']:
            raise MigrationError('Official Swift provider returned an unknown, duplicate or stale input')
        if item.get('parse_has_error') is not False:
            raise MigrationError('SwiftParser diagnostics in ' + name + ': ' + str(item.get('diagnostics')))
        text = expected[name]['source']
        offsets = {0: 0}
        byte = 0
        for index, char in enumerate(text):
            byte += len(char.encode('utf-8'))
            offsets[byte] = index + 1
        for field in ('tokens', 'nodes'):
            if not isinstance(item.get(field), list):
                raise MigrationError('Official Swift provider omitted ' + field)
            for token in item[field]:
                start, end = token.get('start_utf8'), token.get('end_utf8')
                if type(start) is not int or type(end) is not int or start not in offsets or end not in offsets or end < start:
                    raise MigrationError('Invalid UTF-8 source span from SwiftParser')
                token['start'], token['end'] = offsets[start], offsets[end]
                if token.get('line') != text.count('\n', 0, token['start']) + 1:
                    raise MigrationError('SwiftParser returned an invalid source line')
        found[name] = item
    if set(found) != set(expected):
        raise MigrationError('Official Swift provider omitted input files')
    return found


@dataclass(frozen=True)
class Token:
    value: str
    line: int
    kind: str = 'symbol'
    hash_count: int = 0
    quote_count: int = 0
    end_line: int = 0
    start: int = 0
    end: int = 0
    literal_value: str | None = None
    literal_is_static: bool = False
    number_literal: str | None = None


def mapped_tokens(data):
    return [Token(**{key: item[key] for key in Token.__dataclass_fields__ if key in item}) for item in data]


def tokenize(text, path='Input.swift'):
    data = syntax([{'path': path, 'source': text, 'sha256': digest(text.encode('utf-8'))}])
    return mapped_tokens(data[path]['tokens'])
