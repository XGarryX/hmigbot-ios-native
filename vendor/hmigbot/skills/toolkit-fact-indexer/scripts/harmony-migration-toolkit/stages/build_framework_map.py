from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from stages._util import dump_json, load_json, toolkit_root


def build_framework_map(
    android_facts_path: Path,
    out_path: Path,
    rules_path: Path | None = None,
) -> dict[str, Any]:
    facts = load_json(android_facts_path)
    rules_file = rules_path or (toolkit_root() / "data" / "framework_map" / "rules.yaml")
    raw = yaml.safe_load(rules_file.read_text(encoding="utf-8"))
    rules_version = str(raw.get("rules_version", "unknown"))
    rows = raw.get("mappings") or []

    mappings: list[dict[str, Any]] = []
    for row in rows:
        mappings.append(
            {
                "rule_id": row["rule_id"],
                "android_concept": row["android_concept"],
                "harmony_concept": row["harmony_concept"],
                "notes": row.get("notes", ""),
                "confidence": "rule",
            }
        )

    gap_items: list[dict[str, Any]] = []
    for i, sc in enumerate(facts.get("screens") or []):
        if sc.get("noise") == "synthetic":
            gap_items.append(
                {
                    "id": f"SYN_{i}_{sc.get('class_name', 'x')[:48]}",
                    "kind": "synthetic_kotlin_screen",
                    "source_ref": f"navigation:{sc.get('class_name')}",
                    "reason": "Kotlin compiler synthetic / lambda class; fold in manual model or LLM before mapping to ArkUI pages.",
                }
            )

    if facts.get("ui_fidelity") == "low_for_compose":
        gap_items.append(
            {
                "id": "UI_COMPOSE_001",
                "kind": "compose_coverage",
                "source_ref": "android_facts:ui_fidelity",
                "reason": "Static XML ground truth is sparse; ArkUI page specs require LLM or manual design from Kotlin/Compose sources.",
            }
        )

    ir: dict[str, Any] = {
        "schema_version": "1.0",
        "rules_version": rules_version,
        "mappings": mappings,
        "gap_items": gap_items,
        "android_facts_ref": android_facts_path.name,
    }
    dump_json(out_path, ir)
    return ir
