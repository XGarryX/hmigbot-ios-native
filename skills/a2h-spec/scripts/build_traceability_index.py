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
# Data-file parity (issue #44): the bundled implementation resolves its
# default rules file relative to the bundled binary's directory. Keep a
# fresh copy of coverage-rules.json next to _entry so the default works
# even when callers don't pass --rules (the repo copy stays the single
# source of truth; the dist copy is refreshed when older).
try:
    _rules_src = os.path.join(_HERE, "coverage-rules.json")
    if os.path.exists(_rules_src):
        _rules_dst = os.path.join(_DIST, "coverage-rules.json")
        if not os.path.exists(_rules_dst) or os.path.getmtime(_rules_src) > os.path.getmtime(_rules_dst):
            import shutil
            shutil.copy2(_rules_src, _rules_dst)
except OSError:
    pass
if _OS == "macos":  # idempotent; failure must not block execution
    subprocess.run(["xattr", "-dr", "com.apple.quarantine", _DIST],
                   check=False, capture_output=True)
os.environ["ARKTS_SKILL_DIR"] = _HERE  # let bundled lib modules locate the real scripts/ dir
_argv = [_EXE, "build_traceability_index", *sys.argv[1:]]
if _OS == "windows":
    sys.exit(subprocess.run(_argv).returncode)
os.execv(_EXE, _argv)
