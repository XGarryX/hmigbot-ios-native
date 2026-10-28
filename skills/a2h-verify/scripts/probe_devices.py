# Native iOS read-only device prerequisites; legacy source retains original launcher.
from pathlib import Path as _Path
import sys as _sys
_here = _Path(__file__).resolve()
for _parent in _here.parents:
    _runtime = _parent / 'runtime.json'
    if _runtime.is_file():
        import json as _json
        _root = (_parent / _json.loads(_runtime.read_text(encoding='utf-8'))['runtime_relative']).resolve()
        if (_root/'src/hmigbot_ios152').is_dir():
            _sys.path.insert(0,str(_root/'src'));break
    if (_parent/'src/hmigbot_ios152').is_dir():
        _sys.path.insert(0,str(_parent/'src'));break
from hmigbot_ios152.source import config as _native_config
import argparse as _argparse
_probe_parser=_argparse.ArgumentParser(add_help=False,allow_abbrev=False)
_probe_parser.add_argument('--project-root',type=_Path)
_probe_args,_=_probe_parser.parse_known_args(_sys.argv[1:])
_project=_probe_args.project_root
if _project is None:
    _project=next((p for p in (_Path.cwd(),*_Path.cwd().parents) if (p/'.migbot/config.json').is_file()),None)
if _project is None:
    _project=next((p for p in _here.parents if (p/'.hmigbot-ios/install.json').is_file()),_Path.cwd())
try:
    _cfg = _native_config(_project)
except (OSError,ValueError) as _exc:
    import json as _json
    print(_json.dumps({'status':'error','error':'Invalid project configuration: '+str(_exc)}),file=_sys.stderr)
    raise SystemExit(2)
if _cfg.get('source_platform') == 'ios' or _cfg.get('ios'):
    from hmigbot_ios152.native_verify_devices import main as _native_probe
    _native_argv=_sys.argv[1:]
    if _probe_args.project_root is None: _native_argv=['--project-root',str(_project),*_native_argv]
    raise SystemExit(_native_probe(_native_argv))

# AUTO-GENERATED launcher — the real implementation is compiled in ./bin/<platform>/.
import os
import platform
import subprocess
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_OS = {"Darwin": "macos", "Linux": "linux", "Windows": "windows"}.get(platform.system())
_ARCH = "arm64" if platform.machine().lower() in ("arm64", "aarch64") else "x64"
if _OS is None:
    sys.stderr.write("unsupported platform: %s\n" % platform.system())
    sys.exit(2)
_DIST = os.path.join(_HERE, "bin", "%s-%s" % (_OS, _ARCH), "_entry.dist")
# Nuitka names the standalone binary <name>.exe on Windows, <name>.bin elsewhere.
_EXE = os.path.join(_DIST, "_entry" + (".exe" if _OS == "windows" else ".bin"))
if not os.path.exists(_EXE):
    sys.stderr.write("no bundled binary for %s-%s at %s\n" % (_OS, _ARCH, _EXE))
    sys.exit(2)
if _OS == "macos":  # idempotent; failure must not block execution
    subprocess.run(["xattr", "-dr", "com.apple.quarantine", _DIST],
                   check=False, capture_output=True)
os.environ["ARKTS_SKILL_DIR"] = _HERE  # let bundled lib modules locate the real scripts/ dir
_argv = [_EXE, "probe_devices", *sys.argv[1:]]
if _OS == "windows":
    sys.exit(subprocess.run(_argv).returncode)
os.execv(_EXE, _argv)
