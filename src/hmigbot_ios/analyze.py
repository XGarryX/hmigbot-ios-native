"""Read-only native iOS inventory. Lexical hints and structured facts stay distinct."""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import plistlib
import re
import xml.etree.ElementTree as ET

from . import __version__
from .core import SCHEMA, MigrationError, anchor, digest, snapshot
from .swiftui import tokenize, parse_view

SERVICES = {
    "URLSession": "network", "Alamofire": "network", "CoreData": "persistence",
    "SwiftData": "persistence", "UserDefaults": "preferences", "Security": "keychain",
    "CoreLocation": "location", "MapKit": "map", "AVFoundation": "media",
    "Photos": "photos", "CoreBluetooth": "bluetooth", "StoreKit": "payments",
    "CloudKit": "cloud", "HealthKit": "health", "ARKit": "ar",
    "WidgetKit": "widget", "ActivityKit": "live_activity", "BackgroundTasks": "background",
    "UserNotifications": "notifications", "AuthenticationServices": "identity",
    "WebKit": "webview", "Metal": "gpu", "SpriteKit": "game",
}


def analyze(root: Path):
    root = root.resolve()
    source = snapshot(root)
    facts, issues, pages, languages, frameworks = [], [], [], Counter(), set()
    fact_ids = set()

    def add(kind, value, file, line=1, evidence="structured_static", **location):
        ref = anchor(file["path"], file["sha256"], line, **location)
        identity = json.dumps([kind, ref, value], sort_keys=True, default=str)
        fact = {"id": "fact-" + digest(identity.encode())[:20], "kind": kind,
                "value": value, "evidence": evidence, "source_platform": "ios",
                "source_anchors_ref": [ref]}
        if fact["id"] not in fact_ids:
            fact_ids.add(fact["id"])
            facts.append(fact)
        return fact

    def issue(code, message, file=None):
        issues.append({"code": code, "message": message, "status": "needs_review",
                       "path": file["path"] if file else None})

    for file in source["files"]:
        path = root / file["path"]
        suffix = path.suffix.lower()
        try:
            if path.name == "Package.swift":
                add("dependency_manifest", {"format": path.name, "resolution": "needs_provider"}, file)
            if suffix in {".swift", ".m", ".mm", ".h", ".cpp", ".c"}:
                lang = {".swift": "Swift", ".m": "Objective-C", ".mm": "Objective-C++",
                        ".h": "C-family-header", ".cpp": "C++", ".c": "C"}[suffix]
                languages[lang] += 1
                text = path.read_text(encoding="utf-8-sig")
                tokens = tokenize(text, skip_pragma_marks=suffix != ".swift")
                for i, token in enumerate(tokens):
                    if token.kind == "string":
                        continue
                    if token.value == "import" and i + 1 < len(tokens):
                        framework = tokens[i + 1].value
                        if framework not in {"<", '"'} and tokens[i + 1].kind == "identifier":
                            frameworks.add(framework)
                            add("import", {"module": framework}, file, token.line, "lexical_hint")
                    if token.value in {"struct", "class", "enum", "protocol", "func", "interface", "implementation"} and i + 1 < len(tokens):
                        if tokens[i + 1].kind == "identifier":
                            add("declaration", {"kind": token.value, "name": tokens[i + 1].value,
                                                "language": lang}, file, token.line, "lexical_hint")
                    if token.value in SERVICES:
                        add("platform_service", {"symbol": token.value, "category": SERVICES[token.value]},
                            file, token.line, "lexical_hint")
                    if token.value in {"performSelector", "NSClassFromString", "NSSelectorFromString", "objc_msgSend"}:
                        issue("dynamic_dispatch", "Dynamic Objective-C dispatch needs runtime/compiler evidence", file)
                if suffix == ".swift":
                    values = [t.value for t in tokens if t.kind != "string"]
                    if "SwiftUI" in values:
                        frameworks.add("SwiftUI")
                    if "View" in values:
                        try:
                            view = parse_view(text)
                            page = {"status": "convertible_subset", "path": file["path"],
                                    "sha256": file["sha256"], "view": view}
                            add("ui_tree", view, file, evidence="restricted_parser")
                        except MigrationError as exc:
                            page = {"status": "unsupported", "path": file["path"],
                                    "sha256": file["sha256"], "reason": str(exc)}
                            issue("swiftui_rule_gap", str(exc), file)
                        pages.append(page)
                    if any(tokens[i].value == "#" and tokens[i + 1].value in {"if", "elseif"}
                           for i in range(len(tokens) - 1)):
                        issue("conditional_compilation", "Effective sources require Xcode build settings", file)
                if suffix in {".m", ".mm", ".h"}:
                    for match in re.finditer(r"#\s*import\s*[<\"]([^>\"]+)", text):
                        if "/" in match.group(1):
                            frameworks.add(match.group(1).split("/")[0])
                        add("header_import", {"header": match.group(1)}, file,
                            text[:match.start()].count("\n") + 1, "lexical_hint")
            elif suffix in {".plist", ".entitlements", ".xcprivacy"}:
                value = plistlib.loads(path.read_bytes())
                if not isinstance(value, dict):
                    issue("plist_shape", "Expected dictionary root", file)
                    continue
                for key, val in value.items():
                    if key.startswith(("NS", "UI", "CFBundle", "com.apple.")):
                        # plist data/date values remain explicitly string representations.
                        safe = json.loads(json.dumps(val, default=str))
                        add("declaration_config", {"key": key, "value": safe}, file, key=key)
            elif suffix in {".storyboard", ".xib"}:
                data = path.read_bytes()
                if b"<!DOCTYPE" in data.upper() or b"<!ENTITY" in data.upper():
                    raise MigrationError("DTD/entity declarations are not supported")
                tree = ET.fromstring(data)
                for element in tree.iter():
                    if element.get("id") or element.tag in {"outlet", "action", "segue", "constraint"}:
                        add("interface_builder", {"tag": element.tag, "attributes": element.attrib},
                            file, element_id=element.get("id"))
                pages.append({"status": "unsupported", "path": file["path"], "sha256": file["sha256"],
                              "reason": "IB objects/connections extracted; Auto Layout lowering is not implemented"})
                frameworks.add("UIKit")
                issue("ib_layout_gap", "Storyboard/XIB needs constraint, event and navigation mapping", file)
            elif suffix == ".xcstrings":
                value = json.loads(path.read_text(encoding="utf-8-sig"))
                for key, val in value.get("strings", {}).items():
                    add("localization", {"key": key, "source_language": value.get("sourceLanguage"),
                                         "localizations": val.get("localizations", {})}, file, key=key)
            elif path.name == "Contents.json" and any(p.endswith(".xcassets") for p in path.parts):
                value = json.loads(path.read_text(encoding="utf-8-sig"))
                add("asset_catalog", {"name": path.parent.stem, "contents": value}, file)
            elif path.name == "Package.resolved":
                value = json.loads(path.read_text(encoding="utf-8-sig"))
                for pin in value.get("pins", value.get("object", {}).get("pins", [])):
                    add("dependency", pin, file)
            elif path.name in {"Podfile.lock", "Cartfile.resolved", "Package.swift", "Podfile"}:
                add("dependency_manifest", {"format": path.name, "resolution": "needs_provider"}, file)
            elif suffix == ".pbxproj":
                add("build_project", {"format": "Xcode", "effective_configuration": "unresolved"}, file)
            elif path.name == "pubspec.yaml" or path.suffix in {".unity", ".dart"}:
                issue("non_native_route", "Cross-platform component requires a separate adapter", file)
        except (OSError, ValueError, ET.ParseError, plistlib.InvalidFileException) as exc:
            issue("unreadable_source", str(exc), file)
    if not languages and not pages:
        raise MigrationError("No native iOS source or Interface Builder files were found")
    issue("effective_build_unresolved", "Inventory is repository-wide; active target/scheme and compiler symbols are not resolved")
    issue("runtime_unverified", "Source/target build, runtime behavior and device checks have not been executed")
    return {"schema_version": SCHEMA, "tool_version": __version__, "source_platform": "ios",
            "source_root": str(root), "source_snapshot": source,
            "inventory": {"languages": dict(languages), "frameworks": sorted(frameworks),
                          "files": len(source["files"]), "facts": len(facts)},
            "facts": facts, "pages": pages, "issues": issues,
            "analysis_level": "repository_static", "migration_status": "not_verified"}


def migration_plan(report):
    tasks = []
    for index, page in enumerate(report["pages"], 1):
        tasks.append({"id": f"UI-{index:04}", "source_path": page["path"],
                      "operation": "generate_and_validate" if page["status"] == "convertible_subset" else "implement_mapping",
                      "status": "planned", "rule": page.get("view", {}).get("rule"),
                      "reason": page.get("reason"), "source_anchors_ref": [anchor(page["path"], page["sha256"])],
                      "verification": ["target_build", "source_behavior_comparison", "visual_comparison"]})
    for fact in report["facts"]:
        if fact["kind"] in {"platform_service", "dependency", "asset_catalog", "localization", "declaration_config"}:
            tasks.append({"id": fact["id"], "operation": "map_" + fact["kind"], "status": "planned",
                          "source_anchors_ref": fact["source_anchors_ref"], "value": fact["value"]})
    covered = {p["path"] for p in report["pages"]}
    for file in report["source_snapshot"]["files"]:
        if Path(file["path"]).suffix.lower() in {".swift", ".m", ".mm", ".c", ".cpp", ".h"} and file["path"] not in covered:
            tasks.append({"id": "SRC-" + digest(file["path"].encode())[:12],
                          "operation": "review_source_behavior", "status": "planned", "source_path": file["path"],
                          "source_anchors_ref": [anchor(file["path"], file["sha256"])],
                          "reason": "No complete behavioral lowering rule covers this source file"})
    return {"schema_version": SCHEMA, "source_sha256": report["source_snapshot"]["sha256"],
            "tasks": tasks, "issues": report["issues"], "status": "review_required"}


def render_report(report, plan):
    lines = ["# 原生 iOS 迁移分析", "", f"源目录：`{report['source_root']}`", "",
             f"文件 {report['inventory']['files']} 个；事实 {len(report['facts'])} 条。",
             "", "这是仓库静态分析。未解析生效构建配置，未证明行为等价。", "",
             "| 文件 | 处理状态 | 说明 |", "| --- | --- | --- |"]
    for page in report["pages"]:
        reason = page.get("reason", "可生成规则覆盖范围内的 ArkUI 草稿，仍需编译与双端验证")
        clean = lambda s: s.replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {clean(page['path'])} | {page['status']} | {clean(reason)} |")
    lines += ["", f"迁移计划包含 {len(plan['tasks'])} 项待处理操作。", "", "## 未决项", ""]
    lines.extend(f"- {item['code']}：{item['message']} ({item.get('path') or 'project'})" for item in report["issues"])
    return "\n".join(lines) + "\n"
