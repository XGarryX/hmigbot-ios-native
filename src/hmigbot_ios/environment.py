"""Action-scoped checks: an iOS static scan never depends on ADB or a device."""
from pathlib import Path
import platform
import shutil

from .core import MigrationError, digest


def preflight(config, action):
    source = config["source"]
    if source["platform"] != "ios":
        return {"action": action, "status": "delegate_android", "provider": "standalone-hmigbot",
                "message": "Legacy Android config is readable; use the existing HMigBot Android workflow"}
    checks = [{"name": "source_directory", "available": Path(source["root"]).is_dir()}]
    tools = config.get("tools", {})
    def tool(name):
        explicit = tools.get(name)
        resolved = str(Path(explicit).resolve()) if explicit else shutil.which(name)
        checks.append({"name": name, "available": bool(resolved and Path(resolved).is_file()), "path": resolved})
    if action == "source-build":
        checks.append({"name": "macOS_host", "available": platform.system() == "Darwin"})
        tool("xcodebuild")
        checks.append({"name": "source_scheme", "available": bool(source.get("scheme"))})
    elif action == "target-build":
        tool("hvigorw")
        checks.append({"name": "target_build_profile", "available": (Path(config["target"]["root"]) / "build-profile.json5").is_file()})
    elif action == "target-device":
        tool("hdc")
        checks.append({"name": "device_id", "available": bool(config["target"].get("device_id"))})
    elif action != "scan":
        raise MigrationError(f"Unknown action: {action}")
    return {"action": action, "status": "ready_to_attempt" if all(c["available"] for c in checks) else "unavailable",
            "checks": checks, "tools_executed": False, "note": "Discovery only; execution/version compatibility is not verified"}


BASELINE_FILES = [".codex-plugin/plugin.json", "docs/PORTING.md", "bin/a2h-tool.ps1",
                  "skills/a2h-run/SKILL.md", "skills/a2h-plan/scripts/lint_plan_coverage.py",
                  "skills/toolkit-fact-indexer/scripts/toolkit_to_fact_tree_draft.py",
                  "skills/arkts-structural-closure/scripts/plan_lib/feature_plan_parser.py",
                  "install.ps1", "install.sh", "validate.sh"]


def audit_baseline(root: Path):
    from .core import read_json
    manifest = read_json(root / ".codex-plugin/plugin.json")
    if manifest.get("name") != "migbot" or manifest.get("version") != "1.6.1":
        raise MigrationError("This compatibility baseline expects standalone migbot 1.6.1")
    files = []
    for name in BASELINE_FILES:
        path = root / name
        if not path.is_file():
            raise MigrationError(f"Missing baseline entry: {name}")
        data = path.read_bytes()
        files.append({"path": name, "sha256": digest(data), "bytes": len(data),
                      "compiled_launcher": b"_entry.dist" in data})
    return {"plugin": "standalone HMigBot Codex", "version": "1.6.1", "files": files,
            "strategy": "Source-level iOS companion; original binaries and Android entry points remain external",
            "legacy_full_pipeline_integration": "not_implemented", "telemetry_runtime_invoked": False}
