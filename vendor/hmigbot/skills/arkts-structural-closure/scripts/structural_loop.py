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
# Quarantine preparation is owned by the explicit project boundary.
os.environ.setdefault("ARKTS_SKILL_DIR", _HERE)  # let bundled lib modules locate the real scripts/ dir
from pathlib import Path
import json
for _parent in Path(__file__).resolve().parents:
    _runtime = _parent / 'runtime.json'
    if _runtime.is_file():
        _root = (_parent / json.loads(_runtime.read_text(encoding='utf-8'))['runtime_relative']).resolve()
        if (_root / 'src/hmigbot_ios').is_dir():
            sys.path.insert(0, str(_root / 'src')); break
    if (_parent / 'src/hmigbot_ios').is_dir():
        sys.path.insert(0, str(_parent / 'src')); break
from hmigbot_ios.native_image_guard import maybe_run
_native_result = maybe_run(_EXE, sys.argv[1:], _HERE)
if _native_result is not None:
    raise SystemExit(_native_result)

_argv = [_EXE, "structural_loop", *sys.argv[1:]]
if _OS == "windows":
    sys.exit(subprocess.run(_argv).returncode)
os.execv(_EXE, _argv)
