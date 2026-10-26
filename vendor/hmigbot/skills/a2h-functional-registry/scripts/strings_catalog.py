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
_argv = [_EXE, "strings_catalog", *sys.argv[1:]]
if _OS == "windows":
    sys.exit(subprocess.run(_argv).returncode)
os.execv(_EXE, _argv)
