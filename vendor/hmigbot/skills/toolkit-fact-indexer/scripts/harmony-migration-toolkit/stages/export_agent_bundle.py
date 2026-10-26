from __future__ import annotations

from pathlib import Path
from typing import Any

from stages._util import dump_json, load_json


def _load_if_present(path: Path) -> Any:
    if not path.is_file():
        return None
    return load_json(path)


def _intermediate_manifest(intermediate_dir: Path) -> dict[str, Any]:
    artifacts: dict[str, Any] = {}
    omitted_by_prefix: dict[str, int] = {}
    total_artifact_count = 0

    # High-cardinality trees add little value in the bundle itself and can dominate
    # LLM context. Keep them out of the inline artifact index and expose omission stats.
    noisy_prefixes = (
        "0_android_facts/specs/",
        "0_android_facts/app_model/features/",
        "0_android_facts/app_model/screens/",
        "0_android_facts/app_model/paths/",
    )

    def _omit_prefix(rel: str) -> str | None:
        for prefix in noisy_prefixes:
            if rel.startswith(prefix):
                return prefix
        return None

    if intermediate_dir.is_dir():
        for p in sorted(x for x in intermediate_dir.rglob("*") if x.is_file()):
            total_artifact_count += 1
            rel = p.relative_to(intermediate_dir).as_posix()
            omitted_prefix = _omit_prefix(rel)
            if omitted_prefix:
                omitted_by_prefix[omitted_prefix] = omitted_by_prefix.get(omitted_prefix, 0) + 1
                continue
            artifacts[rel] = {
                "bytes": p.stat().st_size,
            }
    return {
        "root": intermediate_dir.as_posix(),
        "artifact_count": total_artifact_count,
        "included_artifact_count": len(artifacts),
        "omitted_artifact_count": total_artifact_count - len(artifacts),
        "omitted_by_prefix": omitted_by_prefix,
        "artifacts": artifacts,
    }


def _feature_tree_summary(feature_tree: dict[str, Any]) -> dict[str, Any]:
    nodes = feature_tree.get("nodes") or []
    edges = feature_tree.get("edges") or []
    by_kind: dict[str, int] = {}
    by_rel: dict[str, int] = {}
    for n in nodes:
        kind = str((n or {}).get("kind") or "unknown")
        by_kind[kind] = by_kind.get(kind, 0) + 1
    for e in edges:
        rel = str((e or {}).get("rel") or "unknown")
        by_rel[rel] = by_rel.get(rel, 0) + 1
    return {
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes_by_kind": by_kind,
        "edges_by_rel": by_rel,
        "coverage": (feature_tree.get("meta") or {}).get("coverage") or {},
    }


def _feature_outline(feature_tree: dict[str, Any], limit: int = 256) -> list[dict[str, Any]]:
    nodes = feature_tree.get("nodes") or []
    edges = feature_tree.get("edges") or []
    screen_counts: dict[str, int] = {}
    for edge in edges:
        src = str((edge or {}).get("from") or "")
        dst = str((edge or {}).get("to") or "")
        if src.startswith("feature:") and dst.startswith("screen:"):
            screen_counts[src.removeprefix("feature:")] = screen_counts.get(src.removeprefix("feature:"), 0) + 1
    out = []
    for node in nodes:
        if (node or {}).get("kind") != "feature":
            continue
        fid = str(node.get("logical_feature_id") or str(node.get("node_id", "")).removeprefix("feature:"))
        evidence = node.get("evidence") if isinstance(node.get("evidence"), dict) else {}
        out.append(
            {
                "feature_id": fid,
                "label": node.get("label") or fid,
                "screen_count": screen_counts.get(fid, 0),
                "source": evidence.get("taxonomy_source") or "taxonomy",
                "top_tokens": evidence.get("top_tokens") or [],
                "representative_screens": evidence.get("representative_screens") or [],
            }
        )
    out.sort(key=lambda x: (-int(x.get("screen_count") or 0), str(x.get("feature_id"))))
    return out[:limit]


def _summary(
    feature_tree: dict[str, Any],
    taxonomy: dict[str, Any],
    verification: dict[str, Any],
    framework_map: dict[str, Any],
    intermediate_manifest: dict[str, Any],
) -> dict[str, Any]:
    ft = _feature_tree_summary(feature_tree)
    kinds = ft["nodes_by_kind"]
    tax_summary = taxonomy.get("summary") or {}
    issues = verification.get("issues") or []
    return {
        "feature_count": int(kinds.get("feature", 0)),
        "screen_count": int(kinds.get("screen", 0)),
        "ui_surface_count": int(kinds.get("ui_surface", 0)),
        "ui_control_count": int(kinds.get("ui_control", 0)),
        "behavior_count": int(kinds.get("behavior", 0)),
        "implementation_count": int(kinds.get("implementation", 0)),
        "function_symbol_count": int(kinds.get("function_symbol", 0)),
        "node_count": int(ft.get("node_count", 0)),
        "edge_count": int(ft.get("edge_count", 0)),
        "gap_count": len(framework_map.get("gap_items") or []),
        "verification_issue_count": len(issues) if isinstance(issues, list) else 0,
        "taxonomy_matched_screen_count": int(tax_summary.get("matched_screen_count", 0)),
        "taxonomy_unmatched_screen_count": int(tax_summary.get("unmatched_screen_count", 0)),
        "intermediate_artifact_count": int(intermediate_manifest.get("artifact_count", 0)),
    }


def _artifact_ref(rel: str, intermediate_manifest: dict[str, Any]) -> dict[str, Any]:
    artifact = (intermediate_manifest.get("artifacts") or {}).get(rel) or {}
    return {"path": f"intermediate/{rel}", **artifact}


def _android_summary(android_facts: dict[str, Any] | None, facts_dir: Path) -> dict[str, Any]:
    android_facts = android_facts or {}
    stage0_manifest = _load_if_present(facts_dir / "manifest.json") or {}
    path_coverage = _load_if_present(facts_dir / "ui_paths_coverage_report.json")
    ui_paths_legacy = _load_if_present(facts_dir / "ui_paths_legacy.json")
    return {
        "android_root": android_facts.get("android_root") or stage0_manifest.get("android_root") or "",
        "manifest": android_facts.get("manifest") or {},
        "gradle_modules": android_facts.get("gradle_modules") or [],
        "navigation_summary": android_facts.get("navigation_summary") or {},
        "ui_fidelity": android_facts.get("ui_fidelity") or "",
        "screens_count": len(android_facts.get("screens") or []),
        "stage0_artifact_checks": stage0_manifest.get("artifact_checks") or {},
        "ui_paths_legacy_count": len(ui_paths_legacy) if isinstance(ui_paths_legacy, list) else 0,
        "ui_paths_coverage": path_coverage or {},
    }


def export_agent_bundle(
    *,
    feature_tree_path: Path,
    evidence_path: Path,
    verify_report_path: Path,
    taxonomy_report_path: Path,
    framework_map_path: Path,
    harmony_arch_path: Path,
    android_facts_path: Path,
    facts_dir: Path,
    intermediate_dir: Path,
    out_path: Path,
) -> dict[str, Any]:
    feature_tree = load_json(feature_tree_path)
    verification = _load_if_present(verify_report_path) or {}
    taxonomy = _load_if_present(taxonomy_report_path) or {}
    framework_map = _load_if_present(framework_map_path) or {}
    harmony_arch = _load_if_present(harmony_arch_path) or {}
    android_facts = _load_if_present(android_facts_path) or {}
    intermediate_manifest = _intermediate_manifest(intermediate_dir)
    summary = _summary(feature_tree, taxonomy, verification, framework_map, intermediate_manifest)

    bundle = {
        "schema_version": "1.0",
        "bundle_kind": "harmony_migration_agent_bundle",
        "meta": {
            "feature_tree": _feature_tree_summary(feature_tree),
            "verification_status": verification.get("status", ""),
            "taxonomy_summary": taxonomy.get("summary") or {},
            "framework_rules_version": framework_map.get("rules_version", ""),
            "harmony_bundle_name": harmony_arch.get("bundle_name", ""),
        },
        "agent_hints": {
            "primary_graph": "Open outline.artifacts.feature_tree.path for the full canonical migration graph.",
            "stage0_inventory": "Open outline.artifacts.stage0_manifest.path — sha256/bytes index of each *.json under 0_android_facts/ produced by the static scan (the manifest file itself is written last and is not self-listed).",
            "source_evidence": "Open outline.artifacts.evidence.path and feature_tree node evidence for deterministic source anchors.",
            "verification": "Treat verification.status=warn as usable with listed issues; unresolved calls indicate static-analysis limits.",
            "gaps": "Use outline.migration.gap_count first, then open the framework map artifact for full gap details.",
            "harmony_projection": "Open outline.artifacts.harmony_projection.path for deterministic HarmonyOS module/ability/route scaffolding input.",
            "intermediate_artifacts": "intermediate_manifest lists reproducible stage artifacts for debugging; the bundle is the default agent input.",
        },
        "summary": summary,
        "outline": {
            "app": _android_summary(android_facts, facts_dir),
            "features": _feature_outline(feature_tree),
            "migration": {
                "harmony_bundle_name": harmony_arch.get("bundle_name", ""),
                "module_count": len(harmony_arch.get("modules") or []),
                "ability_count": len(harmony_arch.get("abilities") or []),
                "route_count": len(harmony_arch.get("routes") or []),
                "framework_rules_version": framework_map.get("rules_version", ""),
                "gap_count": summary["gap_count"],
            },
            "verification": {
                "status": verification.get("status", ""),
                "issue_count": summary["verification_issue_count"],
                "report_ref": _artifact_ref("5_feature_tree/verify_report.json", intermediate_manifest),
            },
            "taxonomy": {
                "summary": taxonomy.get("summary") or {},
                "source": taxonomy.get("source") or "",
                "generated": {
                    "strategy": ((taxonomy.get("generated") or {}).get("strategy") or ""),
                    "generated_feature_count": ((taxonomy.get("generated") or {}).get("generated_feature_count") or 0),
                    "assigned_screen_count": ((taxonomy.get("generated") or {}).get("assigned_screen_count") or 0),
                },
                "report_ref": _artifact_ref("5_feature_tree/taxonomy_report.json", intermediate_manifest),
            },
            "artifacts": {
                "stage0_manifest": _artifact_ref("0_android_facts/manifest.json", intermediate_manifest),
                "feature_tree": _artifact_ref("5_feature_tree/feature_tree.v1.json", intermediate_manifest),
                "evidence": _artifact_ref("5_feature_tree/feature_spec_evidence.json", intermediate_manifest),
                "verification": _artifact_ref("5_feature_tree/verify_report.json", intermediate_manifest),
                "taxonomy": _artifact_ref("5_feature_tree/taxonomy_report.json", intermediate_manifest),
                "harmony_projection": _artifact_ref("3_harmony_arch/harmony_arch.v1.json", intermediate_manifest),
                "framework_mapping": _artifact_ref("2_framework_map/framework_map.v1.json", intermediate_manifest),
                "android_facts": _artifact_ref("1_android_facts/android_facts.v1.json", intermediate_manifest),
            },
        },
        "intermediate_manifest": intermediate_manifest,
    }
    dump_json(out_path, bundle)
    return bundle
