"""
Build output/app_model/: layered JSON (index, screens, features, paths) plus
reference indices for navigation edges and UI points.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

from extractors.app_model_schema import (
    APP_MODEL_VERSION,
    behavior_id,
    feature_id_from_class,
    nav_edge_id,
    ui_point_id,
)


def _slug_filename(name: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9._-]+", "_", name).strip("_")
    return s[:120] or "unnamed"


def _attach_nav_edge_ids(paths: list[dict], nav_edges_enriched: list[dict]) -> None:
    """Mutate path action segments with nav_edge_id when (from,to,trigger) matches."""
    index: dict[tuple[str, str, str], str] = {}
    for e in nav_edges_enriched:
        key = (e.get("from", ""), e.get("to", ""), e.get("trigger", ""))
        if key not in index and e.get("nav_edge_id"):
            index[key] = e["nav_edge_id"]

    for p in paths:
        segs = p.get("segments") or []
        for i, seg in enumerate(segs):
            if seg.get("kind") != "action":
                continue
            to_cls = ""
            for j in range(i + 1, len(segs)):
                if segs[j].get("kind") == "screen":
                    to_cls = segs[j].get("screen_class", "") or ""
                    break
            if not to_cls:
                continue
            fr = seg.get("screen_class", "") or ""
            tr = seg.get("trigger") or ""
            nid = index.get((fr, to_cls, tr))
            if nid:
                seg["nav_edge_id"] = nid


def _collect_ui_points_from_gt_and_paths(
    gt: dict, paths: list[dict]
) -> dict[str, dict[str, Any]]:
    points: dict[str, dict[str, Any]] = {}

    for e in gt.get("static_elements", []):
        layout = e.get("layout", "") or ""
        eid = e.get("id", "") or ""
        if not layout:
            continue
        uid = ui_point_id(layout, eid, virtual=False)
        if uid in points:
            continue
        points[uid] = {
            "ui_point_id": uid,
            "layout": layout,
            "element_id": eid,
            "tag": e.get("tag", ""),
            "virtual": False,
            "text_raw": e.get("text", ""),
            "hint": e.get("hint", ""),
            "content_desc": e.get("content_desc", ""),
            "is_interactive": e.get("is_interactive", False),
            "behavior_refs": [],
        }
        for bi, b in enumerate(e.get("behaviors") or []):
            bid = behavior_id(
                str(b.get("file", "")),
                int(b.get("line") or 0),
                str(b.get("method", b.get("handler", ""))),
                bi,
            )
            points[uid]["behavior_refs"].append(bid)

    for p in paths:
        for seg in p.get("segments") or []:
            if seg.get("kind") != "action":
                continue
            uid = seg.get("ui_point_id")
            if not uid or uid in points:
                continue
            if seg.get("virtual"):
                points[uid] = {
                    "ui_point_id": uid,
                    "layout": seg.get("layout", ""),
                    "element_id": "",
                    "tag": seg.get("tag", ""),
                    "virtual": True,
                    "trigger": seg.get("trigger", ""),
                    "resolved_label": seg.get("resolved_label", ""),
                    "behavior_refs": [],
                }

    return points


def build_nav_edges_with_ids(nav: dict) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    class_layouts = nav.get("class_layouts", {})
    nodes = nav.get("nodes", {})
    for idx, e in enumerate(nav.get("edges") or []):
        fr = e.get("from", "")
        ec = dict(e)
        ec["nav_edge_id"] = nav_edge_id(
            fr, e.get("to", ""), e.get("trigger", ""), e.get("line"), idx
        )
        ec["from_layout"] = class_layouts.get(fr) or nodes.get(fr, {}).get("layout", "")
        if not ec.get("to_layout"):
            ec["to_layout"] = class_layouts.get(e.get("to", "")) or nodes.get(
                e.get("to", ""), {}
            ).get("layout", "")
        if "source" not in ec:
            ec["source"] = "regex"
        out.append(ec)
    return out


def build_and_write(
    out_dir: Path,
    project_root: str,
    paths: list[dict],
    nav: dict,
    gt: dict,
    static_xml: dict | None = None,
) -> dict[str, Any]:
    """
    Write output/app_model/ tree. Mutates paths in-place to add nav_edge_id on actions.
    Returns summary dict for logging.
    """
    model_dir = out_dir / "app_model"
    ref_dir = model_dir / "references"
    screens_dir = model_dir / "screens"
    features_dir = model_dir / "features"
    paths_dir = model_dir / "paths"
    for d in (model_dir, ref_dir, screens_dir, features_dir, paths_dir):
        d.mkdir(parents=True, exist_ok=True)

    static_xml = static_xml or {}
    nav_edges = build_nav_edges_with_ids(nav)
    _attach_nav_edge_ids(paths, nav_edges)

    (ref_dir / "nav_edges.json").write_text(
        json.dumps(nav_edges, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    ui_points = _collect_ui_points_from_gt_and_paths(gt, paths)
    (ref_dir / "ui_point_index.json").write_text(
        json.dumps(ui_points, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    # screens/*.json — group static_elements by layout
    by_layout: dict[str, list] = defaultdict(list)
    for e in gt.get("static_elements", []):
        lo = e.get("layout", "")
        if lo:
            by_layout[lo].append(e)

    screen_files: list[str] = []
    for layout, elems in sorted(by_layout.items()):
        fname = f"{_slug_filename(layout)}.json"
        outgoing: list[str] = []
        for e in nav_edges:
            if e.get("from_layout") == layout:
                outgoing.append(e["nav_edge_id"])
        payload = {
            "layout": layout,
            "ui_point_ids": [
                ui_point_id(layout, x.get("id", ""), virtual=False)
                for x in elems
                if x.get("id")
            ],
            "elements_preview": [
                {
                    "ui_point_id": ui_point_id(layout, x.get("id", ""), virtual=False),
                    "id": x.get("id", ""),
                    "tag": x.get("tag", ""),
                    "is_interactive": x.get("is_interactive", False),
                    "has_behaviors": bool(x.get("behaviors")),
                }
                for x in elems[:500]
            ],
            "outgoing_nav_edge_ids": list(dict.fromkeys(outgoing))[:200],
        }
        rel = f"screens/{fname}"
        (screens_dir / fname).write_text(
            json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        screen_files.append(rel)

    # features/*.json — by host class (no $)
    feature_points: dict[str, set] = defaultdict(set)
    feature_edges: dict[str, set] = defaultdict(set)
    class_for_layout = {}
    for cn, lo in nav.get("class_layouts", {}).items():
        class_for_layout[lo] = cn
    for n, node in nav.get("nodes", {}).items():
        if node.get("layout"):
            class_for_layout.setdefault(node["layout"], n)

    for uid, rec in ui_points.items():
        layout = rec.get("layout", "")
        cn = class_for_layout.get(layout, "")
        base = cn.split("$")[0] if cn else layout or "unknown"
        fid = feature_id_from_class(base)
        feature_points[fid].add(uid)

    for e in nav_edges:
        fr = e.get("from", "")
        fid = feature_id_from_class(fr.split("$")[0])
        feature_edges[fid].add(e["nav_edge_id"])

    feature_files: list[str] = []
    for fid in sorted(feature_points.keys()):
        fname = f"{_slug_filename(fid)}.json"
        related_paths: list[str] = []
        for p in paths:
            pid = p.get("path_id", "")
            if not pid:
                continue
            if any(
                s.get("kind") == "screen"
                and feature_id_from_class((s.get("screen_class") or "").split("$")[0])
                == fid
                for s in (p.get("segments") or [])
            ):
                related_paths.append(pid)
            if len(related_paths) >= 80:
                break
        payload = {
            "feature_id": fid,
            "related_ui_point_ids": sorted(feature_points[fid])[:2000],
            "related_nav_edge_ids": sorted(feature_edges.get(fid, set()))[:500],
            "entry_path_ids_sample": related_paths[:50],
        }
        rel = f"features/{fname}"
        (features_dir / fname).write_text(
            json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        feature_files.append(rel)

    # paths — shard if many
    chunk_size = 1500
    path_files: list[str] = []
    if len(paths) <= chunk_size:
        rel = "paths/all_paths.json"
        (paths_dir / "all_paths.json").write_text(
            json.dumps(paths, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        path_files.append(rel)
    else:
        for i in range(0, len(paths), chunk_size):
            part = i // chunk_size
            fname = f"part_{part:03d}.json"
            rel = f"paths/{fname}"
            (paths_dir / fname).write_text(
                json.dumps(
                    paths[i : i + chunk_size], indent=2, ensure_ascii=False
                ),
                encoding="utf-8",
            )
            path_files.append(rel)

    limitations = [
        "Compose-only and programmatic views are only partially represented (stub screens / gap).",
        "nav_edge_id on actions uses exact (from, to, trigger) match; ambiguous triggers may miss.",
        "RemoteViews and runtime-inflated hierarchies require gap_analysis / manual entries.",
    ]

    index = {
        "app_model_version": APP_MODEL_VERSION,
        "project_root": str(Path(project_root).resolve()),
        "limitations": limitations,
        "counts": {
            "ui_points": len(ui_points),
            "nav_edges": len(nav_edges),
            "paths": len(paths),
            "screens": len(screen_files),
            "features": len(feature_files),
        },
        "files": {
            "nav_edges": "references/nav_edges.json",
            "ui_point_index": "references/ui_point_index.json",
            "screens": screen_files,
            "features": feature_files,
            "paths": path_files,
        },
    }
    (model_dir / "index.json").write_text(
        json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    return index["counts"]
