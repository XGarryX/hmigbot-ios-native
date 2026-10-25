from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml


def _load_yaml(path: Path) -> dict[str, Any]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        raise ValueError(f"Taxonomy must be a YAML object: {path}")
    return raw


def load_taxonomy(
    path: Path | None,
    overlay_paths: list[Path] | None = None,
) -> tuple[str, list[dict[str, Any]], dict[str, Any]]:
    """Load explicit taxonomy rows from optional YAML files only (no bundled defaults).

    Merge order: each overlay is prepended before the previous rows so earlier overlays win
    on first-match; optional ``path`` acts as the lowest-precedence base file.
    """
    overlay_paths = overlay_paths or []
    rows: list[dict[str, Any]] = []
    version = "1.0"
    sources: list[str] = []

    if path is not None:
        base = _load_yaml(path)
        version = str(base.get("version", "1.0"))
        rows = list(base.get("features") or [])
        sources.append(str(path.resolve()))

    for overlay_path in overlay_paths:
        overlay = _load_yaml(overlay_path)
        overlay_rows = list(overlay.get("features") or [])
        rows = overlay_rows + rows
        sources.insert(0, str(overlay_path.resolve()))

    _validate_taxonomy_rows(rows, sources if sources else ["<implicit:empty_base>"])
    meta = {
        "sources": sources,
        "base": str(path.resolve()) if path is not None else "",
        "overlays": [str(p.resolve()) for p in overlay_paths],
    }
    return version, rows, meta


def taxonomy_report_source(
    explicit_rows: list[dict[str, Any]],
    generated_report: dict[str, Any] | None,
) -> str:
    gen = generated_report or {}
    has_gen = int(gen.get("generated_feature_count") or 0) > 0 or int(gen.get("assigned_screen_count") or 0) > 0
    has_explicit = bool(explicit_rows)
    if has_explicit and has_gen:
        return "generated+explicit_taxonomy"
    if has_gen:
        return "generated_taxonomy"
    if has_explicit:
        return "explicit_taxonomy"
    return "none"


def _validate_taxonomy_rows(rows: list[dict[str, Any]], sources: list[str]) -> None:
    seen: set[str] = set()
    for idx, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ValueError(f"Taxonomy row {idx} is not an object ({sources})")
        fid = str(row.get("id") or "").strip()
        if not fid:
            raise ValueError(f"Taxonomy row {idx} is missing id ({sources})")
        if fid in seen:
            raise ValueError(f"Duplicate taxonomy feature id: {fid}")
        seen.add(fid)
        if not str(row.get("label") or "").strip():
            raise ValueError(f"Taxonomy feature {fid} is missing label")
        match = row.get("match") or {}
        if not isinstance(match, dict) or not match:
            raise ValueError(f"Taxonomy feature {fid} is missing match rules")
        for key in ("class_name_regex", "package_regex", "path_regex", "layout_regex", "effect_kind", "action_token"):
            value = match.get(key)
            if value:
                re.compile(str(value))


def _regex_matches(pattern: Any, value: Any) -> bool:
    if not pattern:
        return True
    return re.search(str(pattern), str(value or "")) is not None


def _equals_if_present(expected: Any, actual: Any) -> bool:
    if expected is None or expected == "":
        return True
    return str(expected).lower() == str(actual or "").lower()


def taxonomy_match(
    class_name: str,
    meta: dict[str, Any],
    rows: list[dict[str, Any]],
) -> tuple[str | None, str | None, str | None]:
    for row in rows:
        match = row.get("match") or {}
        inferred_package = class_name.rsplit(".", 1)[0] if "." in class_name else ""
        package_value = meta.get("package") or inferred_package
        if not _regex_matches(match.get("class_name_regex"), class_name):
            continue
        if not _regex_matches(match.get("package_regex"), package_value):
            continue
        if not _regex_matches(match.get("path_regex"), meta.get("source_path") or meta.get("file") or ""):
            continue
        if not _regex_matches(match.get("layout_regex"), meta.get("layout") or ""):
            continue
        if not _equals_if_present(match.get("nav_type"), meta.get("nav_type")):
            continue
        fid = str(row.get("id", "")).strip()
        if fid:
            return fid, str(row.get("label") or fid), fid
    return None, None, None


def build_taxonomy_report(
    screen_hosts: dict[str, dict[str, Any]],
    screen_to_feature: dict[str, str],
    screen_to_rule: dict[str, str],
    rows: list[dict[str, Any]],
    taxonomy_meta: dict[str, Any],
    generated_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    feature_labels = {str(r.get("id")): str(r.get("label") or r.get("id")) for r in rows}
    by_feature: dict[str, int] = {}
    rule_hits: dict[str, int] = {}
    unmatched: list[dict[str, Any]] = []

    for screen, meta in sorted(screen_hosts.items(), key=lambda x: x[0]):
        feature_id = screen_to_feature.get(screen)
        if feature_id:
            by_feature[feature_id] = by_feature.get(feature_id, 0) + 1
            rule_id = screen_to_rule.get(screen) or feature_id
            rule_hits[rule_id] = rule_hits.get(rule_id, 0) + 1
            continue
        unmatched.append(
            {
                "screen_class": screen,
                "layout": meta.get("layout") or "",
                "nav_type": meta.get("nav_type") or "",
                "screen_kind": meta.get("screen_kind") or "",
                "package": meta.get("package") or "",
                "source_path": meta.get("source_path") or "",
            }
        )

    return {
        "schema_version": "1.0",
        "source": taxonomy_report_source(rows, generated_report),
        "taxonomy": taxonomy_meta,
        "summary": {
            "screen_total": len(screen_hosts),
            "matched_screen_count": len(screen_to_feature),
            "unmatched_screen_count": len(unmatched),
            "feature_count": len(by_feature),
            "generated_feature_count": int((generated_report or {}).get("generated_feature_count") or 0),
            "generated_assigned_screen_count": int((generated_report or {}).get("assigned_screen_count") or 0),
        },
        "features": [
            {"feature_id": fid, "label": feature_labels.get(fid, fid), "screen_count": count}
            for fid, count in sorted(by_feature.items())
        ],
        "rule_hits": [{"rule_id": rid, "screen_count": count} for rid, count in sorted(rule_hits.items())],
        "generated": generated_report or {},
        "unmatched_screens": unmatched,
    }
