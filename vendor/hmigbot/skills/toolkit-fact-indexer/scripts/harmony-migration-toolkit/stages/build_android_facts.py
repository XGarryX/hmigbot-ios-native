from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from stages._util import (
    discover_gradle_modules,
    is_synthetic_kotlin_class,
    load_json,
    parse_manifest_launcher,
    read_application_id,
    dump_json,
)


def _nav_screens(nav: dict[str, Any]) -> list[dict[str, Any]]:
    nodes = nav.get("nodes") or {}
    out: list[dict[str, Any]] = []
    for class_name, node in nodes.items():
        layout = (node or {}).get("layout") or ""
        ntype = (node or {}).get("type") or "other"
        if ntype == "activity":
            kind = "activity"
        elif ntype in ("dialog", "commons_dialog"):
            kind = "dialog"
        else:
            kind = "other"
        noise = "synthetic" if is_synthetic_kotlin_class(class_name) else "clean"
        if not layout and noise == "clean":
            noise = "unknown"
        out.append(
            {
                "class_name": class_name,
                "layout": layout,
                "noise": noise,
                "kind": kind,
            }
        )
    out.sort(key=lambda x: x["class_name"])
    return out


def _ui_fidelity(static_xml: dict[str, Any], nav: dict[str, Any]) -> str:
    stats = static_xml.get("stats") or {}
    interactive = int(stats.get("interactive", 0))
    nodes = nav.get("nodes") or {}
    synthetic = sum(1 for k in nodes if is_synthetic_kotlin_class(k))
    if interactive < 15 and synthetic > 30:
        return "low_for_compose"
    if interactive < 40:
        return "mixed"
    return "high_xml"


def build_android_facts(android_root: Path, facts_dir: Path, out_path: Path) -> dict[str, Any]:
    android_root = android_root.resolve()
    nav_path = facts_dir / "navigation_graph.json"
    static_path = facts_dir / "static_xml.json"
    nav = load_json(nav_path) if nav_path.is_file() else {}
    static_xml = load_json(static_path) if static_path.is_file() else {}

    pkg, launcher_short, launcher_qualified = parse_manifest_launcher(android_root)
    app_id = read_application_id(android_root)

    nav_stats = nav.get("stats") or {}
    ir: dict[str, Any] = {
        "schema_version": "1.0",
        "android_root": android_root.as_posix(),
        "ui_fidelity": _ui_fidelity(static_xml, nav),
        "gradle_modules": discover_gradle_modules(android_root),
        "manifest": {
            "application_id": app_id,
            "package": pkg,
            "launcher_activity_class": launcher_short,
            "launcher_activity_qualified": launcher_qualified,
        },
        "navigation_summary": {
            "total_nodes": int(nav_stats.get("total_nodes", 0)),
            "total_edges": int(nav_stats.get("total_edges", 0)),
            "activity_nodes": int(nav_stats.get("activity_nodes", 0)),
            "dialog_nodes": int(nav_stats.get("dialog_nodes", 0)),
        },
        "spec_tools_artifacts": {
            "navigation_graph": "navigation_graph.json",
            "ground_truth": "ground_truth.json",
            "static_xml": "static_xml.json",
            "source_findings": "source_findings.json",
            "specs_dir": "specs",
        },
        "screens": _nav_screens(nav),
    }
    dump_json(out_path, ir)
    return ir
