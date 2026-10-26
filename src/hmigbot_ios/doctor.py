"""Read-only environment doctor: what can work, what's missing, what to do next.

Design constraints (task contract):
- Read only. Never runs external programs, never writes, never touches the network.
- Source *static analysis* needs only Python + a real iOS source. Node / build
  tooling / a device are NOT source-analysis prerequisites.
- Explicit --config wins over default .migbot/config.json; corrupt/missing explicit
  config never falls back and never yields a ready state.
- Install manifest validated against scripts/manage_install.py schema (owner,
  schema_version, version, files). {} alone is invalid.
- Existence != version compatibility / executability / verified environment.
- SwiftPM pre-flight: a root ``Package.swift`` in the *configured iOS source*
  (never the HarmonyOS target) is reported as ``pending_evidence`` with the
  formal manifest-evaluate / facts --manifest-evidence path. Static source
  analysis may continue; the plan gate still needs genuine evaluation evidence.
  Doctor only stats the source root, never recurses, never runs Swift or an
  installer, and never reuses an old PASS.
- Never reads private keys or emits sensitive values.
- Proves read-only by comparing input digests before/after.
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import re
import shutil
import sys
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

from .core import MigrationError, safe_child
from .host import detect_host_profile

INSTALL_MANIFEST = ".hmigbot-ios/install.json"
MIGBOT_CONFIG = ".migbot/config.json"
_MANIFEST_REQUIRED_KEYS = ("owner", "schema_version", "version", "files")
_MANIFEST_EXPECTED_OWNER = "hmigbot-ios"
_MANIFEST_EXPECTED_SCHEMA = 1
_MANIFEST_SAMPLE_LIMIT = 3
_HEX_RE = re.compile(r"^[0-9a-f]{64}$")

_HARMONY_SDK_ENV = ("HOS_SDK_HOME", "DEVECO_SDK_HOME", "HDC_HOME")
_IOS_MARKERS = (".xcodeproj", ".xcworkspace", ".pbxproj", "Package.swift", "Podfile", "Package.resolved")
_HMOS_MARKERS = ("build-profile.json5", "oh-package.json5", "AppScope")

_SOURCE_MANIFEST_REFERENCE = "skills/ios-source-analysis/references/source-input-evidence.md"


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _has_marker(project: Path, marker: str) -> bool:
    if marker.startswith("."):
        try:
            return any(p.name.endswith(marker) for p in project.iterdir())
        except OSError:
            return False
    return (project / marker).exists()


def _check_tool(name: str, explicit_path: str | None = None,
                config_path: str | None = None) -> dict[str, Any]:
    """Static existence only. Priority: explicit > config tools > PATH."""
    for source, val in (("explicit", explicit_path), ("config", config_path)):
        if not val:
            continue
        p = Path(val)
        if p.is_file():
            return {"name": name, "required": True, "status": "ok",
                    "path": str(p), "source": source, "note": None}
        return {"name": name, "required": True, "status": "missing",
                "path": str(p), "source": source,
                "note": f"{source} path is not a file"}
    resolved = shutil.which(name)
    if resolved:
        return {"name": name, "required": True, "status": "ok",
                "path": resolved, "source": "path", "note": None}
    return {"name": name, "required": True, "status": "missing",
            "path": None, "source": "none",
            "note": "not found via explicit / config / PATH"}


def _check_python() -> dict[str, Any]:
    v = sys.version_info
    ok = v >= (3, 11)
    return {"name": "python", "required": True, "status": "ok" if ok else "unsupported",
            "version": f"{v.major}.{v.minor}.{v.micro}", "min_required": "3.11",
            "path": sys.executable,
            "note": None if ok else "Python 3.11+ required to run the tool"}


def _read_json_safe(path: Path) -> tuple[str, Any, str | None]:
    if not path.is_file():
        return "missing", None, "file not found"
    try:
        raw = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return "unreadable", None, str(exc)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        return "corrupt", None, f"invalid JSON: {exc}"
    if not isinstance(data, dict):
        return "invalid", None, "expected a JSON object"
    return "ok", data, None


def _classify_project(project: Path) -> dict[str, Any]:
    if not project.exists():
        return {"kind": "missing", "ios_markers": [], "harmonyos_markers": []}
    if not project.is_dir():
        return {"kind": "not_a_directory", "ios_markers": [], "harmonyos_markers": []}
    markers_ios = [m for m in _IOS_MARKERS if _has_marker(project, m)]
    markers_hmos = [m for m in _HMOS_MARKERS if _has_marker(project, m)]
    kind = "unknown"
    if markers_ios and not markers_hmos:
        kind = "ios_source"
    elif markers_hmos and not markers_ios:
        kind = "harmonyos_target"
    elif markers_ios and markers_hmos:
        kind = "mixed"
    return {"kind": kind, "ios_markers": markers_ios, "harmonyos_markers": markers_hmos}


def _resolve_against_project(value: Any, project: Path) -> Path | None:
    if not isinstance(value, str) or not value:
        return None
    p = Path(value).expanduser()
    if not p.is_absolute():
        p = project / p
    return p


def _check_migbot_config(project: Path, explicit_cfg: Path | None) -> dict[str, Any]:
    """Explicit --config wins; bad/missing explicit never falls back to default."""
    if explicit_cfg is not None:
        cfg_path = explicit_cfg
        source_of_cfg = "explicit"
    else:
        cfg_path = project / MIGBOT_CONFIG
        source_of_cfg = "default"
    status, data, note = _read_json_safe(cfg_path)
    result: dict[str, Any] = {"name": "migbot_config", "required": True, "path": str(cfg_path),
                              "source_of_config": source_of_cfg,
                              "status": status, "note": note}
    if status != "ok":
        if status == "missing" and source_of_cfg == "default":
            result["status"] = "not_configured"
            result["note"] = "no .migbot/config.json found under project"
        return result

    source_platform = data.get("source_platform")
    ios_val = data.get("ios")
    target_val = data.get("harmonyos")
    result["source_platform"] = source_platform

    findings: list[str] = []
    if source_platform != "ios":
        findings.append("source_platform must equal 'ios'")
    if not isinstance(ios_val, str) or not ios_val:
        findings.append("config 'ios' source path missing or wrong type")
    if not isinstance(target_val, str) or not target_val:
        findings.append("config 'harmonyos' target path missing or wrong type")

    if findings:
        result["status"] = "misconfigured"
        result["findings"] = findings
        return result

    source_path = _resolve_against_project(ios_val, project)
    target_path = _resolve_against_project(target_val, project)
    src_ok = bool(source_path and source_path.is_dir())
    tgt_ok = bool(target_path and target_path.is_dir())
    result["ios_source_path"] = str(source_path) if source_path else None
    result["harmonyos_target_path"] = str(target_path) if target_path else None
    result["source_exists"] = src_ok
    result["target_exists"] = tgt_ok

    if not src_ok:
        result["status"] = "source_unavailable"
        result["findings"] = ["configured iOS source directory does not exist"]
        return result

    # Native entry uses the real --project P as the HarmonyOS target, not the
    # config 'harmonyos' string. Bind to P:
    #   1. config.harmonyos must normalize-equal P (else it cannot hide overlap)
    #   2. source (resolved) must not equal / contain / be contained by P
    try:
        p_norm = project.resolve()
    except OSError:
        p_norm = None
    try:
        s_norm = source_path.resolve() if source_path else None
    except OSError:
        s_norm = None
    try:
        t_norm = target_path.resolve() if target_path else None
    except OSError:
        t_norm = None
    result["project_resolved"] = str(p_norm) if p_norm else None

    boundary: list[str] = []
    if t_norm is not None and p_norm is not None and t_norm != p_norm:
        boundary.append(
            "config 'harmonyos' target differs from --project; "
            "native entry uses the real project as the HarmonyOS target")
    if s_norm is not None and p_norm is not None:
        if s_norm == p_norm or s_norm.is_relative_to(p_norm) or p_norm.is_relative_to(s_norm):
            boundary.append(
                "iOS source must not equal / contain / be inside the real "
                "HarmonyOS project (matches native_pipeline.configure)")
    if boundary:
        result["status"] = "misconfigured"
        result["findings"] = boundary
        return result

    tools_field = data.get("tools") if isinstance(data.get("tools"), dict) else {}
    result["tools"] = {k: tools_field.get(k) for k in
                        ("hvigorw", "node", "deveco_sdk", "hdc", "ohpm", "java")
                        if isinstance(tools_field.get(k), str)}
    result["findings"] = []
    return result


def _check_install_manifest(project: Path) -> dict[str, Any]:
    """Validate against scripts/manage_install.py format. {} is NOT ok."""
    path = project / INSTALL_MANIFEST
    status, data, note = _read_json_safe(path)
    result: dict[str, Any] = {"name": "install_manifest", "path": str(path),
                              "status": status, "note": note}
    if status != "ok":
        if status == "missing":
            result["status"] = "not_installed"
            result["note"] = "install manifest absent; project was not installed via manage_install"
        return result

    problems: list[str] = []
    for key in _MANIFEST_REQUIRED_KEYS:
        if key not in data:
            problems.append(f"missing key '{key}'")
    if data.get("owner") != _MANIFEST_EXPECTED_OWNER:
        problems.append("owner != 'hmigbot-ios'")
    if data.get("schema_version") != _MANIFEST_EXPECTED_SCHEMA:
        problems.append("schema_version != 1")
    version = data.get("version")
    files = data.get("files")
    if not isinstance(version, str) or not version.strip():
        problems.append("version must be a non-empty string")
    if not isinstance(files, dict) or not files:
        problems.append("files must be a non-empty mapping")
    if problems:
        result["status"] = "invalid"
        result["findings"] = problems
        result["note"] = "manifest does not match installer schema; do not treat as installed"
        return result

    # Validate every entry lexically before any sample content is read. The
    # remaining entries stay unverified; this is not a full integrity scan.
    reserved = {"con", "prn", "aux", "nul"} | {f"{prefix}{i}" for prefix in ("com", "lpt") for i in range(1, 10)}
    for name, expected in files.items():
        parts = PurePosixPath(name).parts if isinstance(name, str) else ()
        if (not isinstance(name, str) or not name or not parts or "\\" in name or ":" in name
                or name.startswith("/") or ".." in parts
                or name != PurePosixPath(name).as_posix()
                or any(part.endswith((" ", ".")) or part.split(".")[0].lower() in reserved for part in parts)
                or not isinstance(expected, str) or not _HEX_RE.fullmatch(expected)):
            result.update(status="invalid", integrity="unknown",
                          findings=["manifest contains an unsafe path or invalid digest format"],
                          note="manifest entry format invalid; no sample content read")
            return result
    sample_names = list(files.keys())[:_MANIFEST_SAMPLE_LIMIT]
    sample_results = []
    all_ok = True
    for name in sample_names:
        expected = files[name]
        try:
            target = safe_child(project, name)
        except (MigrationError, OSError):
            result.update(status="invalid", integrity="unknown",
                          findings=["manifest sample path escapes project or cannot be safely resolved"],
                          note="unsafe sample not read; remaining files unverified")
            return result
        if not isinstance(expected, str) or not _HEX_RE.match(expected):
            sample_results.append({"path": name, "status": "invalid_digest_format"})
            all_ok = False
            continue
        if not target.is_file():
            sample_results.append({"path": name, "status": "missing"})
            all_ok = False
            continue
        try:
            actual = _sha256_bytes(target.read_bytes())
        except OSError as exc:
            sample_results.append({"path": name, "status": "unreadable", "note": str(exc)[:80]})
            all_ok = False
            continue
        sample_results.append({"path": name,
                                "status": "match" if actual == expected else "mismatch"})
        if actual != expected:
            all_ok = False

    total = len(files)
    checked = len(sample_results)
    if not all_ok:
        integrity = "sample_drift"
    elif checked == 0:
        integrity = "unknown"
    else:
        integrity = "sample_match"
    result["status"] = "ok"
    result["version"] = version
    result["owner"] = data.get("owner")
    result["schema_version"] = data.get("schema_version")
    result["files_count"] = total
    result["sample_checked"] = checked
    result["integrity"] = integrity
    result["integrity_scope"] = (f"only {checked}/{total} files hash-verified; "
                                  "remaining files reported as unknown")
    result["sample"] = sample_results
    result["note"] = ("manifest format valid; executability/compatibility NOT verified; "
                       "not a full integrity claim")
    return result


def _check_swiftpm_manifest(migbot_cfg: dict[str, Any]) -> dict[str, Any] | None:
    """Read-only SwiftPM gate hint for the *configured iOS source* (never the
    HarmonyOS target).

    Presence of a root-level ``Package.swift`` means the real source carries an
    executable SwiftPM manifest. The formal plan gate requires genuine
    evaluation evidence for it; static source analysis may still continue.
    This check only stats the source root's own ``Package.swift`` — it never
    recurses, never sweeps the disk, never runs Swift, never installs, and
    never emits or reuses an old PASS. File presence and any Swift found on
    PATH are clues only: they do NOT prove the manifest evaluates, is
    compatible, or was verified.
    """
    if migbot_cfg.get("status") != "ok" or not migbot_cfg.get("source_exists"):
        return None
    src = migbot_cfg.get("ios_source_path")
    if not isinstance(src, str) or not src:
        return None
    manifest = Path(src) / "Package.swift"
    if not manifest.is_file():
        return None
    return {
        "name": "swiftpm_manifest", "required": True, "status": "pending_evidence",
        "path": str(manifest),
        "evaluation_verified": False,
        "coverage": ("仅检查所配置 iOS 源根自身的 Package.swift；不递归、不扫描其它目录或磁盘，"
                     "嵌套包/其他清单不在本只读诊断枚举范围内。"),
        "finding": ("该源含可执行 SwiftPM 清单；当前正式门禁需要真实求值证据。"
                    "静态源分析可继续，进入计划前需完成正式证据链。"),
        "next_action": ("进入计划前完成正式证据链：对源根 Package.swift 运行 manifest-evaluate "
                        "采集当前宿主真实求值证据，再以 facts --manifest-evidence 消费"
                        f"（见 {_SOURCE_MANIFEST_REFERENCE}；doctor 不代执行、不代验证）。"),
        "formal_commands": [
            "python <runtime>/scripts/a2h_ios.py manifest-evaluate --project <target> "
            "--config <target>/spec/ref/manifest-evaluate.config.json "
            "--output <target>/spec/ref/ios-manifest-evidence/<capture-id>",
            "python <runtime>/scripts/a2h_ios.py facts --project <target> "
            "--manifest-evidence <target>/spec/ref/ios-manifest-evidence/<capture-id>",
        ],
        "tool_requirement": ("求值配置需给出显式 argv：command 含独立 package 与 dump-package，"
                             "version_command 含 --version，版本输出须含合法 Swift version。"
                             "Swift 可来自当前宿主或 WSL（如 [\"wsl\",\"--\",\"swift\", ...]）；"
                             "不要求在 Windows PATH 安装 Swift。工具不做自动 WSL 路径转换，"
                             "须提供真实映射目录。"),
        "reference": _SOURCE_MANIFEST_REFERENCE,
        "note": ("清单存在与 PATH 是否有 Swift 均只是线索：doctor 未执行 Swift、未求值、"
                 "未验证兼容性、未生成或复用旧 PASS，求值/兼容性未验证。"),
    }


def _check_harmony_sdk(sdk_path: str | None) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    if sdk_path:
        p = Path(sdk_path)
        items.append({"name": "explicit_sdk", "required": False,
                      "status": "ok" if p.is_dir() else "missing",
                      "path": str(p), "source": "explicit",
                      "note": None if p.is_dir() else "explicit SDK path is not a directory"})
    for name in _HARMONY_SDK_ENV:
        val = os.environ.get(name)
        if val and Path(val).is_dir():
            items.append({"name": name, "required": False, "status": "ok", "path": val,
                          "source": "env", "note": None})
        elif val:
            items.append({"name": name, "required": False, "status": "missing", "path": val,
                          "source": "env", "note": "env set but directory not found"})
        else:
            items.append({"name": name, "required": False, "status": "not_configured",
                          "source": "env", "note": "alternative SDK entry; not required"})
    return items


def _summarize_section(items: Iterable[dict[str, Any]]) -> dict[str, Any]:
    items = list(items)
    BLOCKING = ("missing", "unsupported", "source_unavailable", "invalid",
                "corrupt", "unreadable", "misconfigured")
    ok = [i for i in items if i.get("status") == "ok"]
    required_missing = [i for i in items if i.get("required") and i.get("status") in BLOCKING]
    optional_missing = [i for i in items if not i.get("required") and i.get("status") in
                        ("missing", "not_configured")]
    warnings = [i for i in items if i.get("status") in
                ("partial", "unknown", "not_verified", "not_configured", "pending_evidence")]
    can_do = "full" if not required_missing and not warnings else ("partial" if ok else "none")
    next_actions: list[str] = []
    for m in required_missing:
        if m["name"] == "migbot_config":
            can_do = "none"
            next_actions.append("fix selected migration configuration: provide valid JSON, source_platform='ios', "
                                "an existing iOS source directory and harmonyos matching --project; "
                                "keep source and target separate")
        else:
            next_actions.append(f"install or configure {m['name']}")
    for w in warnings:
        next_actions.append(w.get("next_action") or
                            f"verify {w['name']}: {w.get('note', 'unknown state')}")
    for o in optional_missing:
        next_actions.append(f"optional: {o['name']} not configured (alternative SDK entry)")
    return {"can_do": can_do, "ok_count": len(ok),
            "required_missing_count": len(required_missing),
            "optional_missing_count": len(optional_missing),
            "warning_count": len(warnings), "next_actions": next_actions[:6]}


def _input_digest(project: Path, config_path: Path | None) -> str:
    parts: list[bytes] = []
    try:
        for entry in sorted(project.iterdir(), key=lambda p: p.name):
            try:
                st = entry.stat()
                parts.append(f"{entry.name}\t{'d' if entry.is_dir() else 'f'}\t{st.st_size}\t{st.st_mtime_ns}".encode())
            except OSError:
                pass
    except OSError:
        pass
    for cfg in (config_path, project / MIGBOT_CONFIG, project / INSTALL_MANIFEST):
        if cfg and Path(cfg).is_file():
            try:
                parts.append(Path(cfg).read_bytes())
            except OSError:
                pass
    return _sha256_bytes(b"\n".join(parts))


def doctor(project: Path | str, config: Path | str | None = None,
           node_path: str | None = None, hvigor_path: str | None = None,
           ohpm_path: str | None = None, java_path: str | None = None,
           sdk_path: str | None = None) -> dict[str, Any]:
    """Read-only environment diagnostic. No external programs, no network, no mutations."""
    project = Path(project).resolve() if project else Path.cwd()
    config_path = Path(config).resolve() if config else None

    digest_before = _input_digest(project, config_path)

    python_check = _check_python()
    project_class = _classify_project(project)
    migbot_cfg = _check_migbot_config(project, config_path)
    install_manifest = _check_install_manifest(project)

    cfg_tools = migbot_cfg.get("tools") or {} if migbot_cfg.get("status") == "ok" else {}

    source_note_map = {"missing": "project path does not exist",
                        "not_a_directory": "project path is not a directory",
                        "unknown": "no recognized iOS source or HarmonyOS target markers"}
    source_note = source_note_map.get(project_class["kind"])
    source_status = ("missing" if project_class["kind"] in ("missing", "not_a_directory")
                     else ("unknown" if project_class["kind"] == "unknown" else "ok"))
    source_items = [python_check,
                    {"name": "project", "required": True, "path": str(project),
                     "status": source_status, "kind": project_class["kind"],
                     "ios_markers": project_class["ios_markers"],
                     "harmonyos_markers": project_class["harmonyos_markers"],
                     "note": source_note},
                    migbot_cfg, install_manifest]
    swiftpm = _check_swiftpm_manifest(migbot_cfg)
    if swiftpm is not None:
        source_items.append(swiftpm)

    build_items = [_check_tool("node", node_path, cfg_tools.get("node")),
                   _check_tool("hvigorw", hvigor_path, cfg_tools.get("hvigorw")),
                   _check_tool("ohpm", ohpm_path, cfg_tools.get("ohpm")),
                   _check_tool("java", java_path, cfg_tools.get("java"))]
    build_items.extend(_check_harmony_sdk(sdk_path or cfg_tools.get("deveco_sdk")))

    device_items = [_check_tool("hdc", None, cfg_tools.get("hdc"))] + [
        {"name": "device_id", "required": False, "status": "unknown",
         "note": "device connection requires a runtime check; static only, not verified"},
        {"name": "signing_profile", "required": False, "status": "not_verified",
         "note": "signing needs a private profile and runtime; static config presence only, no keys read"}]

    sections = {
        "source_analysis": {"items": source_items, "summary": _summarize_section(source_items)},
        "harmonyos_build": {"items": build_items, "summary": _summarize_section(build_items)},
        "device_verification": {"items": device_items, "summary": _summarize_section(device_items)},
    }

    digest_after = _input_digest(project, config_path)
    read_only = digest_before == digest_after

    result: dict[str, Any] = {
        "status": "diagnostic_complete",
        "platform": {"os": platform.system(), "arch": platform.machine(),
                     "python_platform": platform.platform()},
        "host_profile": detect_host_profile(),
        "sections": sections,
        "overall": _overall(python_check, migbot_cfg, project_class),
        "input_sha256": digest_before,
        "read_only_verified": read_only,
        "honest_granularity": "existence != version compatible / executable / verified environment",
        "tools_executed": False, "network_accessed": False, "mutations": False,
    }
    return result


def _overall(python_check: dict[str, Any], migbot_cfg: dict[str, Any],
             project_class: dict[str, Any]) -> str:
    """Blocked/config_error/needs_project when truth requires it.
    source_analysis_ready only when python ok AND config ok AND source exists."""
    if python_check["status"] != "ok":
        return "blocked"
    cfg_status = migbot_cfg.get("status")
    if cfg_status in ("corrupt", "invalid", "misconfigured", "missing",
                       "unreadable", "source_unavailable"):
        return "config_error"
    if cfg_status == "not_configured":
        return "needs_project" if project_class["kind"] == "missing" else "partial"
    # cfg_status == "ok": require source to actually exist
    if not migbot_cfg.get("source_exists"):
        return "config_error"
    return "source_analysis_ready"


def render_text(report: dict[str, Any]) -> str:
    lines = [f"HMigBot Doctor Report ({report['platform']['os']} {report['platform']['arch']})",
             f"Overall: {report['overall']}", ""]
    for section_name, section in report["sections"].items():
        lines.append(f"== {section_name} ==")
        summary = section["summary"]
        lines.append(f"   Can do: {summary['can_do']} (ok={summary['ok_count']}, "
                     f"required_missing={summary['required_missing_count']}, "
                     f"optional_missing={summary['optional_missing_count']}, "
                     f"warnings={summary['warning_count']})")
        for item in section["items"]:
            status = item.get("status", "?")
            note = f" -- {item['note']}" if item.get("note") else ""
            path = f" ({item['path']})" if item.get("path") else ""
            req = "" if item.get("required", True) else " [optional]"
            lines.append(f"   [{status}] {item['name']}{req}{path}{note}")
        if summary["next_actions"]:
            lines.append("   Next:")
            for a in summary["next_actions"]:
                lines.append(f"     - {a}")
        lines.append("")
    lines.append("Note: existence != version compatible / executable / verified. No tools were run.")
    if not report.get("read_only_verified", True):
        lines.append("WARNING: read-only check failed; inputs may have changed.")
    return "\n".join(lines)
