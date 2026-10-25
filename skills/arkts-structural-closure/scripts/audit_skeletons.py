# Bundled-engine launcher; current-stage source selection is maintained here.
import argparse
import os
import platform
import subprocess
import sys

def _stage_source_arguments(argv):
    """Use the current source tree with the original stage detector and severity."""
    if "--help" in argv or "-h" in argv:
        return argv
    parser = argparse.ArgumentParser(add_help=False, allow_abbrev=False)
    parser.add_argument("--scope")
    parser.add_argument("--project-root")
    parser.add_argument("--diff-base")
    parser.add_argument("--scope-files", nargs="*", default=None)
    args, _ = parser.parse_known_args(argv)
    if (args.scope != "stage" or args.scope_files is not None
            or not args.project_root or not args.diff_base):
        return argv
    root = os.path.abspath(args.project_root)

    def git(*options):
        result = subprocess.run(["git", "-C", root, *options], capture_output=True)
        if result.returncode:
            detail = result.stderr.decode("utf-8", errors="replace").strip()
            raise RuntimeError(detail or "git source selection failed")
        return result.stdout

    # Resolve the caller's baseline before passing it as a diff operand.
    base = os.fsdecode(git("rev-parse", "--verify", "--end-of-options", args.diff_base)).strip()
    options = ("--name-only", "--relative", "--no-ext-diff", "--no-textconv", "-z")
    changed = (git("diff", *options, base, "HEAD", "--", "*.ets")
               + git("diff", *options, "--cached", "HEAD", "--", "*.ets")
               + git("diff", *options, "--", "*.ets"))
    untracked = git("ls-files", "--others", "--exclude-standard", "-z", "--", "*.ets")
    names = sorted({os.fsdecode(name) for name in (changed + untracked).split(b"\0") if name})
    files = [("./" + name if name.startswith("-") else name) for name in names
             if name.endswith(".ets") and os.path.isfile(os.path.join(root, name))]
    return [*argv, "--scope-files", *files]


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
try:
    _source_argv = _stage_source_arguments(sys.argv[1:])
except (OSError, RuntimeError) as exc:
    sys.stderr.write("audit_skeletons: current stage source selection failed: %s\n" % exc)
    sys.exit(2)
_argv = [_EXE, "audit_skeletons", *_source_argv]
if _OS == "windows":
    sys.exit(subprocess.run(_argv).returncode)
os.execv(_EXE, _argv)
