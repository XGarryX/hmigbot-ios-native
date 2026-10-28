"""Mac subprocess compatibility for the original compiled visual engine.

Distribution binaries stay byte-for-byte original. A content-addressed private
cache renames the Python dylib using Apple's tools, re-signs affected Mach-O
files ad hoc, and gives sys.executable a real interpreter forwarding shim.
The original engine, comparison algorithms and child entry names are retained.
"""
from __future__ import annotations
import fcntl
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile

from hmigbot_ios.core import MigrationError, atomic_write, write_json

MAGIC = {b'\xcf\xfa\xed\xfe', b'\xfe\xed\xfa\xcf', b'\xca\xfe\xba\xbe', b'\xbe\xba\xfe\xca'}
SHIM = '''#!/bin/sh
if [ -n "$HMIGBOT_HOST_PYTHON" ]; then
  exec "$HMIGBOT_HOST_PYTHON" "$(dirname "$0")/hmigbot-reentry.py" "$@"
fi
exec python3 "$(dirname "$0")/hmigbot-reentry.py" "$@"
'''
REENTRY = '''import json, os, pathlib, sys
if sys.version_info < (3, 11):
    sys.stderr.write("HMigBot requires Python >=3.11 for compiled child dispatch\\n"); sys.exit(2)
args = sys.argv[1:]
if not args:
    sys.stderr.write("Missing compiled child entry\\n"); sys.exit(2)
scripts = pathlib.Path(os.environ['HMIGBOT_SCRIPT_DIR']).resolve()
first = pathlib.Path(args[0])
# Original Nuitka embeds __file__ under dist, where its public .py is absent.
# Remap only to a real shipped public script, preserving all remaining argv.
if first.suffix == '.py' and first.parent.resolve() == pathlib.Path(__file__).parent.resolve():
    target = scripts / first.name
    if not target.is_file():
        sys.stderr.write("Unknown compiled child entry: " + first.name + "\\n"); sys.exit(2)
    args[0] = str(target)
log = os.environ.get('HMIGBOT_REENTRY_LOG')
if log:
    with open(log, 'a') as stream: stream.write(json.dumps({'original':sys.argv[1:], 'forwarded':args}) + '\\n')
os.execv(sys.executable, [sys.executable, '-B', *args])
'''


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _macho(path):
    with path.open('rb') as f:
        return f.read(4) in MAGIC


def _run(argv, records):
    value = subprocess.run(list(map(str, argv)), capture_output=True, text=True, timeout=30)
    records.append({'argv': list(map(str, argv)), 'exit_code': value.returncode,
                    'stdout': value.stdout, 'stderr': value.stderr})
    if value.returncode:
        raise MigrationError('Compiled runtime adaptation failed: ' + ' '.join(map(str, argv[:3])) + ': ' + value.stderr.strip())
    return value


def _files(root):
    result = {}
    for path in sorted(root.rglob('*')):
        if path.is_symlink():
            raise MigrationError('Compiled runtime contains a link: '+str(path))
        if path.is_file(): result[str(path.relative_to(root))] = _sha(path)
    return result


def _native_execution(root, expected, commands, *, remove_quarantine=False):
    """Prepare only byte-verified members in this private cache, never source."""
    records = []
    for name, sha in expected.items():
        path = root/name
        if path.is_symlink() or not path.is_file() or _sha(path) != sha:
            raise MigrationError('Compiled runtime hash differs before execution preparation: '+str(path))
        if not _macho(path): continue
        _run(['/usr/bin/codesign','--verify','--strict',path],commands)
        attrs = _run(['/usr/bin/xattr',path],commands).stdout.splitlines()
        record = {'path':name,'sha256':sha,'quarantine':'not_present','signature':'verified'}
        if 'com.apple.quarantine' in attrs:
            record['original_quarantine'] = _run(['/usr/bin/xattr','-p','com.apple.quarantine',path],commands).stdout.strip()
            if not remove_quarantine:
                raise MigrationError('Download quarantine reappeared on verified private runtime: '+str(path))
            if _sha(path) != sha:
                raise MigrationError('Compiled runtime changed before metadata preparation: '+str(path))
            _run(['/usr/bin/xattr','-d','com.apple.quarantine',path],commands)
            if 'com.apple.quarantine' in _run(['/usr/bin/xattr',path],commands).stdout.splitlines() or _sha(path) != sha:
                raise MigrationError('Private runtime metadata preparation failed: '+str(path))
            record['quarantine'] = 'removed_download_quarantine'
        records.append(record)
    return records


def prepare(scripts):
    scripts = Path(scripts).resolve()
    if platform.system() != 'Darwin' or platform.machine().lower() not in {'arm64', 'aarch64'}:
        raise MigrationError('This runtime adaptation requires the shipped macOS arm64 engine')
    original = scripts / 'bin/macos-arm64/_entry.dist'
    records = _files(original)
    allowlist = json.loads(Path(__file__).with_name('compiled_visual_runtime.json').read_text())['files']
    if records != allowlist:
        changed = sorted(set(records)^set(allowlist) | {n for n in set(records)&set(allowlist) if records[n] != allowlist[n]})
        raise MigrationError('Original compiled runtime differs from shipped allowlist: '+', '.join(changed))
    if '_entry.bin' not in records or not any(k.lower() == 'python' for k in records):
        raise MigrationError('Original compiled runtime is incomplete')
    public = {p.name: _sha(p) for p in sorted(scripts.iterdir()) if p.is_file() and p.suffix in {'.py','.json'}}
    tool_identity = {str(p):_sha(p.resolve()) for p in (Path('/usr/bin/install_name_tool'),Path('/usr/bin/codesign'))}
    identity = {'original': records, 'public_entries':public, 'apple_tools':tool_identity,
                'installed_scripts':str(scripts),
                'adapter_sha256': _sha(Path(__file__)), 'arch': platform.machine()}
    key = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()
    project = next((p for p in scripts.parents if (p/'.hmigbot-ios/install.json').is_file()),None)
    # Installed projects never share a mutable runtime cache. Uninstalled source
    # packages use their own source-path namespace, or an explicit QA directory.
    fallback = (project/'.hmigbot-ios/cache/compiled-visual' if project else
                Path.home()/'Library/Caches/hmigbot-ios/source-tools'/hashlib.sha256(str(scripts).encode()).hexdigest()/'compiled-visual')
    base = Path(os.environ.get('HMIGBOT_COMPILED_CACHE', fallback))
    base.mkdir(parents=True, exist_ok=True)
    cache = base / key
    with (base / (key + '.lock')).open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        stamp = cache / 'adaptation.json'
        rebuild_reason = None
        if stamp.is_file() and not stamp.is_symlink():
            try:
                data = json.loads(stamp.read_text())
                actual = _files(cache); actual.pop('adaptation.json',None)
                modes = {str(p.relative_to(cache)):p.stat().st_mode & 0o777 for p in cache.rglob('*') if p.is_file()}
                modes.pop('adaptation.json',None)
                if data.get('identity') == identity and data.get('adapted') == actual and data.get('modes') == modes:
                    _native_execution(cache,actual,[],remove_quarantine=False)
                    return cache / '_entry.bin'
                rebuild_reason = 'cache identity, bytes, file set or modes differ'
            except (MigrationError,ValueError,OSError) as exc:
                rebuild_reason = str(exc)
        if cache.exists(): shutil.rmtree(cache)
        stage = Path(tempfile.mkdtemp(prefix=key + '.', dir=base))
        commands = []
        try:
            shutil.copytree(original, stage, dirs_exist_ok=True)
            if _files(stage) != allowlist:
                raise MigrationError('Private runtime copy differs from shipped allowlist')
            execution = _native_execution(stage,allowlist,commands,remove_quarantine=True)
            binary = stage / '_entry.bin'
            signature = subprocess.run(['/usr/bin/codesign', '-dv', '--verbose=4', str(binary)], capture_output=True, text=True)
            if signature.returncode == 0 and 'Signature=adhoc' not in signature.stderr:
                raise MigrationError('Refusing to replace a non-ad-hoc distribution signature')
            python = next(p for p in stage.iterdir() if p.name.lower() == 'python')
            library = stage / 'libhmigbot-python.dylib'
            python.rename(library)
            for file in sorted(p for p in stage.rglob('*') if p.is_file() and _macho(p)):
                before = _run(['/usr/bin/otool', '-L', file], commands).stdout
                dependencies = [line.strip().split(' (', 1)[0] for line in before.splitlines()[1:]]
                changed = False
                for dependency in dependencies:
                    if dependency in {'@executable_path/Python', '@loader_path/Python'}:
                        replacement = dependency.rsplit('/', 1)[0] + '/libhmigbot-python.dylib'
                        _run(['/usr/bin/install_name_tool', '-change', dependency, replacement, file], commands)
                        changed = True
                if file == library:
                    _run(['/usr/bin/install_name_tool', '-id', '@rpath/libhmigbot-python.dylib', file], commands)
                    changed = True
                if changed:
                    _run(['/usr/bin/codesign', '--force', '--sign', '-', file], commands)
                    _run(['/usr/bin/codesign', '--verify', '--strict', file], commands)
                after = _run(['/usr/bin/otool', '-L', file], commands).stdout
                if '@executable_path/Python ' in after or '@loader_path/Python ' in after:
                    raise MigrationError('Unadapted Python dependency remains: ' + file.name)
            atomic_write(stage / 'python', SHIM.encode())
            (stage / 'python').chmod(0o755)
            atomic_write(stage / 'hmigbot-reentry.py', REENTRY.encode())
            # Original in-process gates check __file__.parent/child.py before
            # spawning it. Mirror byte-identical public entries so gates execute.
            for name in public:
                shutil.copy2(scripts / name, stage / name)
            write_json(stage/'runtime.json', {'runtime_relative':str(Path(__file__).resolve().parents[2])})
            write_json(stage/'.hmigbot-public-scripts.json', {'scripts':str(scripts), 'sha256':public})
            binary.chmod(binary.stat().st_mode | 0o111)
            adapted = {str(p.relative_to(stage)): _sha(p) for p in sorted(stage.rglob('*')) if p.is_file()}
            final_execution = _native_execution(stage,adapted,commands,remove_quarantine=False)
            modes = {str(p.relative_to(stage)):p.stat().st_mode & 0o777 for p in stage.rglob('*') if p.is_file()}
            write_json(stage / 'adaptation.json', {'identity': identity, 'original_signature': signature.stderr,
                                                  'commands': commands, 'adapted': adapted,
                                                  'modes':modes,'native_execution':execution,
                                                  'final_native_execution':final_execution,'rebuild_reason':rebuild_reason,
                                                  'note': 'Private cache dependency-name adaptation and ad-hoc signing; shipped binaries unchanged'})
            stage.rename(cache)
        except BaseException:
            shutil.rmtree(stage, ignore_errors=True)
            raise
    return cache / '_entry.bin'


def execute(command, argv, scripts, *, cwd=None, env=None, capture_output=False, text=True):
    engine = prepare(scripts)
    environment = {**os.environ, **(env or {}), 'ARKTS_SKILL_DIR': str(Path(scripts).resolve()),
           'HMIGBOT_SCRIPT_DIR': str(Path(scripts).resolve()), 'HMIGBOT_HOST_PYTHON': sys.executable,
           'PYTHONDONTWRITEBYTECODE': '1'}
    return subprocess.run([str(engine), command, *argv], env=environment, cwd=cwd,
                          capture_output=capture_output, text=text)


def run(command, argv, scripts):
    return execute(command, argv, scripts).returncode
