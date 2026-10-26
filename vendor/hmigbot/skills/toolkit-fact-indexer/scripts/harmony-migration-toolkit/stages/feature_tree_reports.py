from __future__ import annotations

from pathlib import Path
from typing import Any


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _norm_path(value: Any) -> str:
    return str(value or "").replace("\\", "/")


def _function_node_id(symbol_id: str) -> str:
    return f"function_symbol:{symbol_id}"


def _collect_downstream(start: str, edges: list[dict[str, Any]], limit: int = 500) -> set[str]:
    outgoing: dict[str, list[str]] = {}
    for edge in edges:
        outgoing.setdefault(str(edge.get("from") or ""), []).append(str(edge.get("to") or ""))
    seen = {start}
    queue = list(outgoing.get(start, []))
    while queue and len(seen) < limit:
        cur = queue.pop(0)
        if not cur or cur in seen:
            continue
        seen.add(cur)
        queue.extend(outgoing.get(cur, []))
    return seen


def build_feature_spec_evidence(ir: dict[str, Any]) -> dict[str, Any]:
    nodes = list(ir.get("nodes") or [])
    edges = list(ir.get("edges") or [])
    by_id = {str(n.get("node_id")): n for n in nodes}
    features: list[dict[str, Any]] = []
    for feature in sorted((n for n in nodes if n.get("kind") == "feature"), key=lambda n: str(n.get("node_id"))):
        fid = str(feature.get("node_id"))
        reachable = _collect_downstream(fid, edges)
        scoped_nodes = [by_id[nid] for nid in sorted(reachable) if nid in by_id]
        anchors = []
        for node in scoped_nodes:
            evidence = node.get("evidence") or {}
            file_path = evidence.get("source_file") or evidence.get("file")
            if file_path and evidence.get("line") is not None:
                anchors.append(
                    {
                        "node_id": node.get("node_id"),
                        "symbol_id": evidence.get("symbol_id") or evidence.get("entry_symbol_id") or "",
                        "file": file_path,
                        "function": evidence.get("function_name") or "",
                        "line": evidence.get("line"),
                        "kind": node.get("kind"),
                    }
                )
        entry_functions = sorted(
            {
                (n.get("evidence") or {}).get("entry_symbol_id")
                for n in scoped_nodes
                if n.get("kind") == "behavior" and (n.get("evidence") or {}).get("entry_symbol_id")
            }
        )
        gaps = []
        if not anchors:
            gaps.append("missing_source_anchor")
        if not entry_functions:
            gaps.append("missing_entry_function")
        features.append(
            {
                "feature_id": feature.get("logical_feature_id") or fid.replace("feature:", ""),
                "node_id": fid,
                "label": feature.get("label") or "",
                "screens": [n.get("node_id") for n in scoped_nodes if n.get("kind") == "screen"],
                "behaviors": [
                    {
                        "node_id": n.get("node_id"),
                        "label": n.get("label"),
                        "evidence": n.get("evidence") or {},
                    }
                    for n in scoped_nodes
                    if n.get("kind") == "behavior"
                ],
                "entry_functions": entry_functions,
                "call_chains": [
                    {
                        "from": e.get("from"),
                        "to": e.get("to"),
                        "callsite_file": e.get("callsite_file"),
                        "callsite_line": e.get("callsite_line"),
                    }
                    for e in edges
                    if e.get("rel") == "calls" and e.get("from") in reachable
                ],
                "source_anchors": anchors,
                "coverage_gaps": gaps,
            }
        )
    return {
        "schema_version": "1.0",
        "source": "feature_tree.v1.json",
        "features": features,
        "meta": {
            "feature_count": len(features),
            "features_with_anchors": sum(1 for f in features if f["source_anchors"]),
            "features_with_entry_functions": sum(1 for f in features if f["entry_functions"]),
        },
    }


def _line_exists(android_root: Path, file_path: Any, line: Any) -> bool:
    path = android_root / _norm_path(file_path)
    line_no = _safe_int(line)
    if line_no <= 0 or not path.is_file():
        return False
    try:
        return len(path.read_text(encoding="utf-8", errors="ignore").splitlines()) >= line_no
    except OSError:
        return False


def build_verify_report(ir: dict[str, Any], android_root: Path, unresolved_calls: list[dict[str, Any]]) -> dict[str, Any]:
    nodes = list(ir.get("nodes") or [])
    node_ids = {str(n.get("node_id")) for n in nodes}
    issues: list[dict[str, Any]] = []
    for node in nodes:
        evidence = node.get("evidence") or {}
        file_path = evidence.get("source_file") or evidence.get("file")
        if file_path and evidence.get("line") is not None and not _line_exists(android_root, file_path, evidence.get("line")):
            issues.append(
                {
                    "severity": "warn",
                    "kind": "stale_source_anchor",
                    "node_id": node.get("node_id"),
                    "file": file_path,
                    "line": evidence.get("line"),
                }
            )
        for key in ("symbol_id", "entry_symbol_id"):
            sid = evidence.get(key)
            if sid and _function_node_id(str(sid)) not in node_ids:
                issues.append({"severity": "fail", "kind": "missing_symbol_node", "node_id": node.get("node_id"), "symbol_id": sid})
    for call in unresolved_calls[:500]:
        issues.append(
            {
                "severity": "warn",
                "kind": "unresolved_call",
                "symbol_id": call.get("from_symbol_id"),
                "callee_name": call.get("callee_name"),
                "file": call.get("callsite_file"),
                "line": call.get("callsite_line"),
                "reason": call.get("reason"),
            }
        )
    status = "pass"
    if any(i["severity"] == "fail" for i in issues):
        status = "fail"
    elif issues:
        status = "warn"
    return {
        "schema_version": "1.0",
        "source": "feature_tree.v1.json",
        "status": status,
        "summary": {
            "node_count": len(nodes),
            "issue_count": len(issues),
            "fail_count": sum(1 for i in issues if i["severity"] == "fail"),
            "warn_count": sum(1 for i in issues if i["severity"] == "warn"),
        },
        "issues": issues,
    }
