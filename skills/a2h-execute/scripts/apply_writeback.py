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
_argv = [_EXE, "apply_writeback", *sys.argv[1:]]
from registry_table_format import apply_if_requested
from feature_status_writeback import apply_if_requested as _apply_feature_status
def _original_writeback_chain(args):
    result = apply_if_requested(args, lambda native_args: subprocess.run([_EXE, "apply_writeback", *native_args]).returncode)
    return result if result is not None else subprocess.run([_EXE, "apply_writeback", *args]).returncode
try:
    _feature_result = _apply_feature_status(sys.argv[1:], _original_writeback_chain)
except (OSError, ValueError) as _feature_error:
    sys.stderr.write("feature_index.verified: %s\n" % _feature_error)
    sys.exit(1)
if _feature_result is not None:
    raise SystemExit(_feature_result)
try:
    _formatted_result = apply_if_requested(
        sys.argv[1:], lambda args: subprocess.run([_EXE, "apply_writeback", *args]).returncode)
except (OSError, ValueError) as _error:
    sys.stderr.write("registry table formatting: %s\n" % _error)
    sys.exit(2)
if _formatted_result is not None:
    sys.exit(_formatted_result)
if _OS == "windows":
    sys.exit(subprocess.run(_argv).returncode)
os.execv(_EXE, _argv)
