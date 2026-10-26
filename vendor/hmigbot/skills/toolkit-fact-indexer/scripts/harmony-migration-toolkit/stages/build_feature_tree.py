from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from stages.feature_taxonomy_miner import mine_generated_taxonomy
from stages.feature_tree_reports import build_feature_spec_evidence, build_verify_report
from stages.feature_tree_taxonomy import build_taxonomy_report, load_taxonomy, taxonomy_match
from stages._util import dump_json, kotlin_outer_host_class, load_json


def _nav_edge_to_rel(edge_type: str) -> str:
    t = (edge_type or "").lower()
    if t == "activity":
        return "navigates_to"
    if t in ("dialog", "commons_dialog"):
        return "presents_modal"
    if "fragment" in t:
        return "embeds_fragment"
    return "navigates_to"


def _screen_kind_from_nav_type(ntype: str) -> str:
    t = (ntype or "").lower()
    if t == "activity":
        return "activity"
    if t in ("dialog", "commons_dialog"):
        return "dialog"
    return "other"


def _iter_finding_lists(findings_root: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    out: list[tuple[str, dict[str, Any]]] = []
    findings = findings_root.get("findings") or {}
    for bucket, val in sorted(findings.items()):
        if not isinstance(val, list):
            continue
        for item in val:
            if isinstance(item, dict) and item.get("file") and item.get("line") is not None:
                out.append((bucket, item))
    out.sort(key=lambda x: (x[1].get("file", ""), int(x[1].get("line", 0)), x[0]))
    return out


def _infer_screen_class_from_source_path(file_path: str) -> str | None:
    norm = file_path.replace("\\", "/")
    base = Path(norm).name
    if not base.endswith(".kt") and not base.endswith(".java"):
        return None
    return base[: -len(Path(base).suffix)]


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _stable_token(value: Any, fallback: str) -> str:
    raw = str(value or "").strip() or fallback
    token = re.sub(r"[^A-Za-z0-9_.:-]+", "_", raw)
    return token.strip("_") or fallback


def _normalize_label(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def _iter_effect_paths(effect_root: Any) -> list[dict[str, Any]]:
    if isinstance(effect_root, dict):
        paths = effect_root.get("paths") or []
    elif isinstance(effect_root, list):
        paths = effect_root
    else:
        paths = []
    return [p for p in paths if isinstance(p, dict)]


def _screen_from_display_path(path_display: str, screen_hosts: dict[str, dict[str, Any]]) -> str | None:
    first = re.split(r"\s*(?:›|>)\s*", path_display.strip(), maxsplit=1)[0].strip()
    if not first:
        return None
    first_norm = _normalize_label(first)
    for screen in sorted(screen_hosts):
        screen_norm = _normalize_label(screen)
        if screen_norm == first_norm or screen_norm.startswith(first_norm) or first_norm.startswith(screen_norm):
            return screen
    return None


def _resolve_effect_screen(item: dict[str, Any], screen_hosts: dict[str, dict[str, Any]]) -> str | None:
    for key in ("target", "screen_class", "class_name"):
        raw = str(item.get(key) or "").strip()
        if not raw:
            continue
        candidate = kotlin_outer_host_class(raw)
        if candidate in screen_hosts:
            return candidate

    inferred = _infer_screen_class_from_source_path(str(item.get("source_file") or item.get("file") or ""))
    if inferred:
        candidate = kotlin_outer_host_class(inferred)
        if candidate in screen_hosts:
            return candidate

    return _screen_from_display_path(str(item.get("path_display_report") or item.get("path_display_legacy") or ""), screen_hosts)


def _node_has_line_evidence(node: dict[str, Any]) -> bool:
    evidence = node.get("evidence") or {}
    if not isinstance(evidence, dict):
        return False
    has_file = bool(evidence.get("file") or evidence.get("source_file"))
    return has_file and evidence.get("line") is not None


def _norm_path(value: Any) -> str:
    return str(value or "").replace("\\", "/")


def _function_node_id(symbol_id: str) -> str:
    return f"function_symbol:{symbol_id}"


def _load_function_symbols(facts_dir: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    symbols_path = facts_dir / "function_symbols.json"
    call_graph_path = facts_dir / "call_graph.json"
    symbols_payload = load_json(symbols_path) if symbols_path.is_file() else {}
    call_graph = load_json(call_graph_path) if call_graph_path.is_file() else {}
    symbols = list(symbols_payload.get("symbols") or call_graph.get("symbols") or [])
    calls = list(call_graph.get("calls") or [])
    unresolved = list(call_graph.get("unresolved_calls") or [])
    return symbols, calls, unresolved


def _symbols_by_file(symbols: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    out: dict[str, list[dict[str, Any]]] = {}
    for sym in symbols:
        out.setdefault(_norm_path(sym.get("file")), []).append(sym)
    for rows in out.values():
        rows.sort(key=lambda s: (_safe_int(s.get("start_line")), _safe_int(s.get("end_line"))))
    return out


def _find_symbol_for_anchor(
    symbols_by_file: dict[str, list[dict[str, Any]]],
    file_path: Any,
    line: Any,
) -> dict[str, Any] | None:
    norm = _norm_path(file_path)
    line_no = _safe_int(line)
    candidates = symbols_by_file.get(norm) or []
    containing = [
        s
        for s in candidates
        if _safe_int(s.get("start_line")) <= line_no <= _safe_int(s.get("end_line"), _safe_int(s.get("start_line")))
    ]
    if containing:
        return sorted(containing, key=lambda s: (_safe_int(s.get("end_line")) - _safe_int(s.get("start_line")), str(s.get("symbol_id"))))[0]
    preceding = [s for s in candidates if _safe_int(s.get("start_line")) <= line_no]
    if preceding:
        return preceding[-1]
    return candidates[0] if candidates else None


def _feature_line_coverage(nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> dict[str, Any]:
    by_id = {str(n.get("node_id")): n for n in nodes if n.get("node_id")}
    outgoing: dict[str, list[str]] = {}
    for edge in edges:
        src = str(edge.get("from") or "")
        dst = str(edge.get("to") or "")
        if src and dst:
            outgoing.setdefault(src, []).append(dst)

    feature_nodes = sorted(
        (n for n in nodes if n.get("kind") == "feature" and n.get("node_id") != "feature:unmatched"),
        key=lambda n: str(n.get("node_id")),
    )
    with_line: list[str] = []
    without_line: list[str] = []
    for feature in feature_nodes:
        fid = str(feature.get("node_id"))
        seen = {fid}
        queue = list(outgoing.get(fid, []))
        found = False
        while queue:
            nid = queue.pop(0)
            if nid in seen:
                continue
            seen.add(nid)
            node = by_id.get(nid)
            if node and _node_has_line_evidence(node):
                found = True
                break
            queue.extend(outgoing.get(nid, []))
        if found:
            with_line.append(fid)
        else:
            without_line.append(fid)

    return {
        "feature_total": len(feature_nodes),
        "features_with_line_evidence": len(with_line),
        "features_without_line_evidence": without_line,
        "line_evidence_node_count": sum(1 for n in nodes if _node_has_line_evidence(n)),
    }


def _function_coverage(nodes: list[dict[str, Any]], edges: list[dict[str, Any]], unresolved_calls: list[dict[str, Any]]) -> dict[str, Any]:
    call_sources = {str(e.get("from")) for e in edges if e.get("rel") == "calls"}
    behavior_nodes = [n for n in nodes if n.get("kind") == "behavior"]
    with_symbol = 0
    with_call_chain = 0
    for node in behavior_nodes:
        evidence = node.get("evidence") or {}
        entry = str(evidence.get("entry_symbol_id") or "")
        if entry:
            with_symbol += 1
            if _function_node_id(entry) in call_sources:
                with_call_chain += 1
    return {
        "function_symbol_node_count": sum(1 for n in nodes if n.get("kind") == "function_symbol"),
        "behavior_total": len(behavior_nodes),
        "behaviors_with_entry_symbol": with_symbol,
        "behaviors_with_call_chain": with_call_chain,
        "unresolved_call_count": len(unresolved_calls),
    }


def _stable_edge_id(from_id: str, to_id: str, rel: str, idx: int) -> str:
    # Positional id, unique within the file. from/to/rel are already first-class
    # edge fields, so embedding them here only duplicated long symbol-id endpoints
    # (worst on the ~7k calls edges). idx already disambiguates; keep it compact.
    return f"e{idx}"


def build_feature_tree(
    android_facts_path: Path,
    facts_dir: Path,
    out_path: Path,
    *,
    taxonomy_path: Path | None = None,
    taxonomy_overlay_paths: list[Path] | None = None,
    harmony_arch_path: Path | None = None,
) -> dict[str, Any]:
    af = load_json(android_facts_path)
    nav = load_json(facts_dir / "navigation_graph.json") if (facts_dir / "navigation_graph.json").is_file() else {}
    nav_nodes: dict[str, Any] = nav.get("nodes") or {}
    nav_edges: list[dict[str, Any]] = list(nav.get("edges") or [])
    specs_dir = facts_dir / "specs"
    source_path = facts_dir / "source_findings.json"
    sf = load_json(source_path) if source_path.is_file() else {}
    effect_path = facts_dir / "ui_effect_paths.json"
    effect_paths = _iter_effect_paths(load_json(effect_path)) if effect_path.is_file() else []
    chains_path = facts_dir / "behavior_chains.json"
    behavior_chains = list((load_json(chains_path) or {}).get("behavior_chains") or []) if chains_path.is_file() else []
    enum_path = facts_dir / "ui_paths_enumerated.json"
    enum_payload = load_json(enum_path) if enum_path.is_file() else {}
    enumerated_paths: list[dict[str, Any]] = list(enum_payload.get("paths") or []) if isinstance(enum_payload, dict) else []
    function_symbols, call_edges, unresolved_calls = _load_function_symbols(facts_dir)
    symbols_for_file = _symbols_by_file(function_symbols)

    taxonomy_version, tax_rows, taxonomy_meta = load_taxonomy(taxonomy_path, taxonomy_overlay_paths)
    manifest = af.get("manifest") or {}
    app_label = (manifest.get("application_id") or manifest.get("package") or "application").strip() or "application"

    ha: dict[str, Any] = {}
    if harmony_arch_path and harmony_arch_path.is_file():
        ha = load_json(harmony_arch_path)
    routes_by_class: dict[str, dict[str, Any]] = {}
    for r in ha.get("routes") or []:
        cn = r.get("android_screen_class")
        if isinstance(cn, str) and cn:
            routes_by_class[cn] = r
    abilities = ha.get("abilities") or []
    modules = ha.get("modules") or []
    default_ability = str(abilities[0].get("name")) if abilities and isinstance(abilities[0], dict) else "EntryAbility"
    default_module = str(modules[0].get("name")) if modules and isinstance(modules[0], dict) else "harmony_entry"

    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []

    product_id = "product_root"
    nodes.append(
        {
            "node_id": product_id,
            "kind": "product_root",
            "label": app_label,
            "evidence": {"manifest_application_id": manifest.get("application_id", ""), "launcher": manifest.get("launcher_activity_qualified", "")},
        }
    )

    def host(name: str) -> str:
        return kotlin_outer_host_class(name)

    screen_hosts: dict[str, dict[str, Any]] = {}
    for raw_name, meta in sorted(nav_nodes.items(), key=lambda x: x[0]):
        h = host(raw_name)
        if h not in screen_hosts:
            ntype = (meta or {}).get("type") or "other"
            screen_hosts[h] = {
                "class_name": h,
                "layout": (meta or {}).get("layout") or "",
                "nav_type": ntype,
                "screen_kind": _screen_kind_from_nav_type(str(ntype)),
                "package": (meta or {}).get("package") or "",
                "source_path": (meta or {}).get("source_path") or (meta or {}).get("file") or "",
            }
        else:
            if not screen_hosts[h].get("layout") and (meta or {}).get("layout"):
                screen_hosts[h]["layout"] = (meta or {}).get("layout") or ""

    for e in nav_edges:
        for k in ("from", "to"):
            if e.get(k):
                h = host(str(e[k]))
                if h not in screen_hosts:
                    screen_hosts[h] = {
                        "class_name": h,
                        "layout": "",
                        "nav_type": "other",
                        "screen_kind": "other",
                        "package": "",
                        "source_path": "",
                    }

    # ── Fill empty layouts for fragment / container nodes ─────────────────────
    # Fragment destinations from containment edges and anonymous dialog classes
    # often have no nav-graph node (hence layout="").  Without a layout, downstream
    # spec-to-screen matching breaks and the node acts as a silent dead-end.
    # Try, in order: (1) class_layouts from the nav graph, (2) CamelCase→snake_case
    # conversion (honouring the same convention the old v1 path used).
    _class_layouts = nav.get("class_layouts") or {}
    _camel_to_snake = __import__("re").compile(r"(?<=[a-z])(?=[A-Z])")
    for h in screen_hosts:
        if screen_hosts[h].get("layout"):
            continue
        # (1) explicit class→layout mapping from the nav graph (incl. inflate owner)
        ly = _class_layouts.get(h) or ""
        if not ly:
            # (2) CamelCase → snake_case heuristic (last resort, tagged)
            ly = _camel_to_snake.sub("_", h).lower()
        if ly:
            screen_hosts[h]["layout"] = ly
            # Keep screen_kind but mark the layout source
            if screen_hosts[h].get("nav_type") == "other" and not _class_layouts.get(h):
                screen_hosts[h]["layout_source"] = "name_heuristic"

    for sym in sorted(function_symbols, key=lambda s: (str(s.get("class_name") or ""), str(s.get("file") or ""))):
        cls = str(sym.get("class_name") or "").strip()
        if not cls:
            continue
        h = host(cls)
        if h not in screen_hosts:
            continue
        file_path = str(sym.get("file") or "").strip()
        if file_path and not screen_hosts[h].get("source_path"):
            screen_hosts[h]["source_path"] = file_path
        if "." in cls and not screen_hosts[h].get("package"):
            screen_hosts[h]["package"] = cls.rsplit(".", 1)[0]

    feature_ids_used: set[str] = set()
    screen_to_feature: dict[str, str] = {}
    screen_to_rule: dict[str, str] = {}
    for h, meta in sorted(screen_hosts.items(), key=lambda x: x[0]):
        fid, flab, rule_id = taxonomy_match(h, meta, tax_rows)
        if fid:
            feature_ids_used.add(fid)
            screen_to_feature[h] = fid
            screen_to_rule[h] = rule_id or fid

    generated_screen_to_feature, generated_screen_to_rule, generated_taxonomy_report = mine_generated_taxonomy(
        screen_hosts,
        [{**e, "from": host(str(e.get("from", ""))), "to": host(str(e.get("to", "")))} for e in nav_edges],
        screen_to_feature,
    )
    for h, fid in sorted(generated_screen_to_feature.items(), key=lambda x: x[0]):
        if h in screen_to_feature:
            continue
        feature_ids_used.add(fid)
        screen_to_feature[h] = fid
        screen_to_rule[h] = generated_screen_to_rule.get(h, fid)

    feature_labels: dict[str, str] = {str(r.get("id")): str(r.get("label") or r.get("id")) for r in tax_rows}
    generated_features_by_id = {
        str(f.get("feature_id")): f for f in generated_taxonomy_report.get("generated_features", [])
    }
    for fid, row in generated_features_by_id.items():
        feature_labels[fid] = str(row.get("label") or fid)

    for fid in sorted(feature_ids_used):
        generated = generated_features_by_id.get(fid)
        evidence: dict[str, Any] = {"taxonomy": taxonomy_meta.get("sources", [])}
        if generated:
            evidence.update(
                {
                    "taxonomy_source": "generated",
                    "top_tokens": generated.get("top_tokens") or [],
                    "representative_screens": generated.get("representative_screens") or [],
                }
            )
        nodes.append(
            {
                "node_id": f"feature:{fid}",
                "kind": "feature",
                "label": feature_labels.get(fid, fid),
                "logical_feature_id": fid,
                "evidence": evidence,
            }
        )

    # ── Build inbound edge index for anonymous-dialog reach_paths ───────────
    # Anonymous inner-class dialogs ($showCampaignDialog$1) are not reachable
    # via BFS from the launcher, but they have real trigger edges in the nav
    # graph (e.g. HomeActivity –fn:showCampaignDialog→ HomeActivity$showCampaignDialog$1).
    # We surface that trigger context as reach_paths on the screen node so
    # downstream consumers (feature tree, agent bundle) can see "how do I get to
    # this dialog?" instead of seeing an orphan node.
    #
    # Note: screen_hosts keys are the host()-processed names (e.g.
    # HomeActivity$showCampaignDialog, without the final $1), but nav graph
    # edges use the full raw names.  We build a reverse map from processed →
    # raw to bridge the two.
    edges_by_to: dict[str, list[dict[str, Any]]] = {}
    for edge in nav_edges:
        t = str(edge.get("to") or "")
        if t and t != str(edge.get("from") or ""):
            edges_by_to.setdefault(t, []).append(edge)

    # processed host-name → set of raw nav names that map to it
    raw_via_processed: dict[str, list[str]] = {}
    for raw_name in list(nav_nodes.keys()):
        ph = host(raw_name)
        if ph != raw_name:
            raw_via_processed.setdefault(ph, []).append(raw_name)

    def _host_label(cls: str) -> str:
        # Returns a short human-readable label from a class name
        for suffix in ("Activity", "Fragment", "Dialog"):
            if cls.endswith(suffix) and cls != suffix:
                return cls[: -len(suffix)]
        return cls

    def _trigger_label(edge: dict) -> str:
        trigger = str(edge.get("trigger") or "")
        if trigger.startswith("fn: "):
            return trigger[4:].strip()
        if trigger.startswith("fn:"):
            return trigger[3:].strip()
        if trigger.startswith("hosts fragment"):
            return trigger.strip()
        if trigger:
            return trigger.strip()[:80]
        via = str(edge.get("via") or "")
        return via.strip() or "navigate"

    for h, meta in sorted(screen_hosts.items(), key=lambda x: x[0]):
        sid = f"screen:{h}"
        sk = meta.get("screen_kind") or "other"
        node: dict[str, Any] = {
            "node_id": sid,
            "kind": "screen",
            "label": h,
            "screen_class": h,
            "layout": meta.get("layout") or "",
            "screen_kind": sk,
            "evidence": {"navigation_graph": "navigation_graph.json"},
        }
        fid = screen_to_feature.get(h)
        if fid:
            node["logical_feature_id"] = fid
        if ha:
            route = routes_by_class.get(h)
            harm: dict[str, Any] = {"ability_name": default_ability, "module": default_module}
            if route:
                harm["route_placeholder"] = route.get("path_placeholder") or ""
            else:
                harm["gap_ref"] = "UNMAPPED_ROUTE"
            if af.get("ui_fidelity") == "low_for_compose":
                prev = harm.get("gap_ref", "")
                harm["gap_ref"] = (prev + "|" if prev else "") + "UI_COMPOSE_LOW_FIDELITY"
            node["projection"] = {"harmony": harm}

        # ── reach_paths for anonymous / orphan dialogs ─────────────────────
        # When a dialog is an inner class (contains $ in its name), the
        # reach stack is often "host page → trigger function → dialog".
        # Build that from the navigation graph's inbound edges so the fact
        # tree carries the full reach context instead of an orphan node.
        rps: list[dict[str, Any]] = []
        if "$" in h:
            # screen_hosts keys are host()-processed (e.g.
            # HomeActivity$showCampaignDialog, without the terminal $1).
            # Nav edges use the full raw name.  Bridge via the reverse map.
            lookup_names = [h] + raw_via_processed.get(h, [])
            for raw_name in lookup_names:
                for edge in edges_by_to.get(raw_name, []):
                    from_cls = str(edge.get("from") or "")
                    rp = {
                        "from_class": from_cls,
                        "trigger": _trigger_label(edge),
                        "via": str(edge.get("via") or ""),
                        "display": f"{_host_label(from_cls)} > {_trigger_label(edge)}",
                    }
                    if edge.get("line"):
                        rp["line"] = int(edge.get("line"))
                    rps.append(rp)

                # Also pull reach paths from enumerated paths that end at any
                # raw-name variant of this screen.
                for ep in enumerated_paths:
                    leaf = str(ep.get("leaf_class") or "")
                    if leaf == raw_name:
                        rps.append({
                            "from_class": "",
                            "trigger": "",
                            "via": "enumerated",
                            "display": str(ep.get("path_display") or ""),
                            "depth": int(ep.get("depth") or 0),
                        })

        if rps:
            node["reach_paths"] = rps

        nodes.append(node)

    for fid in sorted(feature_ids_used):
        edges.append(
            {
                "edge_id": _stable_edge_id(product_id, f"feature:{fid}", "parent_of", len(edges)),
                "from": product_id,
                "to": f"feature:{fid}",
                "rel": "parent_of",
                "determinism": "rule",
                "source": "generated_taxonomy" if fid in generated_features_by_id else "explicit_taxonomy",
            }
        )

    for h, fid in sorted(screen_to_feature.items(), key=lambda x: x[0]):
        edges.append(
            {
                "edge_id": _stable_edge_id(f"feature:{fid}", f"screen:{h}", "parent_of", len(edges)),
                "from": f"feature:{fid}",
                "to": f"screen:{h}",
                "rel": "parent_of",
                "determinism": "rule",
                "source": "generated_taxonomy" if fid in generated_features_by_id else "explicit_taxonomy",
            }
        )

    for h in sorted(screen_hosts.keys()):
        if h not in screen_to_feature:
            edges.append(
                {
                    "edge_id": _stable_edge_id(product_id, f"screen:{h}", "parent_of", len(edges)),
                    "from": product_id,
                    "to": f"screen:{h}",
                    "rel": "parent_of",
                    "determinism": "rule",
                    "source": "taxonomy_unmatched_screen",
                }
            )

    for sym in sorted(function_symbols, key=lambda s: (str(s.get("file") or ""), _safe_int(s.get("start_line")), str(s.get("symbol_id") or ""))):
        symbol_id = str(sym.get("symbol_id") or "").strip()
        if not symbol_id:
            continue
        nodes.append(
            {
                "node_id": _function_node_id(symbol_id),
                "kind": "function_symbol",
                "label": f"{sym.get('class_name', '')}.{sym.get('function_name', '')}",
                "symbol_id": symbol_id,
                "function_name": str(sym.get("function_name") or ""),
                "signature": str(sym.get("signature") or ""),
                "evidence": {
                    # function_name/signature live at node top level above — not
                    # repeated here. evidence keeps only what the node fields don't
                    # carry (location + provenance) to avoid ~4k×2 duplicate strings.
                    "source": "function_symbols.json",
                    "file": _norm_path(sym.get("file")),
                    "start_line": _safe_int(sym.get("start_line")),
                    "end_line": _safe_int(sym.get("end_line")),
                    "class_name": sym.get("class_name") or "",
                    "confidence": sym.get("confidence") or "",
                },
            }
        )

    symbol_node_ids = {n["node_id"] for n in nodes if n.get("kind") == "function_symbol"}
    for call in sorted(call_edges, key=lambda c: (str(c.get("callsite_file") or ""), _safe_int(c.get("callsite_line")), str(c.get("from_symbol_id") or ""), str(c.get("to_symbol_id") or ""))):
        src_id = _function_node_id(str(call.get("from_symbol_id") or ""))
        dst_id = _function_node_id(str(call.get("to_symbol_id") or ""))
        if src_id not in symbol_node_ids or dst_id not in symbol_node_ids:
            continue
        edges.append(
            {
                "edge_id": _stable_edge_id(src_id, dst_id, "calls", len(edges)),
                "from": src_id,
                "to": dst_id,
                "rel": "calls",
                "determinism": "static_analysis",
                "callsite_file": _norm_path(call.get("callsite_file")),
                "callsite_line": _safe_int(call.get("callsite_line")),
                "callee_name": call.get("callee_name") or "",
                "confidence": call.get("confidence") or "",
            }
        )

    seen_nav: set[tuple[str, str, str, str, str, str]] = set()
    for e in sorted(nav_edges, key=lambda x: (str(x.get("from", "")), str(x.get("to", "")), int(x.get("line", 0)))):
        a = host(str(e.get("from", "")))
        b = host(str(e.get("to", "")))
        if not a or not b or a == b:
            continue
        rel = _nav_edge_to_rel(str(e.get("type", "")))
        via = str(e.get("via") or "")
        trig = str(e.get("trigger") or "")
        src = str(e.get("source") or "")
        key = (a, b, rel, via, trig, src)
        if key in seen_nav:
            continue
        seen_nav.add(key)
        ne: dict[str, Any] = {
            "edge_id": _stable_edge_id(f"screen:{a}", f"screen:{b}", rel, len(edges)),
            "from": f"screen:{a}",
            "to": f"screen:{b}",
            "rel": rel,
            "determinism": "static_analysis",
        }
        if via:
            ne["via"] = via
        if trig:
            ne["trigger"] = trig
        if src:
            ne["source"] = src
        if e.get("line") is not None:
            ne["line"] = _safe_int(e.get("line"))
        edges.append(ne)

    if specs_dir.is_dir():
        for spec_path in sorted(specs_dir.glob("*_spec.json")):
            try:
                spec = load_json(spec_path)
            except (OSError, ValueError):
                continue
            cls = str(spec.get("class") or "").strip()
            layout = str(spec.get("layout") or "").strip()
            if not cls:
                continue
            h = host(cls)
            surf_id = f"ui_surface:{layout or spec_path.stem}"
            if any(n.get("node_id") == surf_id for n in nodes):
                continue
            nodes.append(
                {
                    "node_id": surf_id,
                    "kind": "ui_surface",
                    "label": layout or spec_path.stem,
                    "evidence": {"spec": spec_path.name},
                }
            )
            edges.append(
                {
                    "edge_id": _stable_edge_id(f"screen:{h}", surf_id, "owns_ui", len(edges)),
                    "from": f"screen:{h}",
                    "to": surf_id,
                    "rel": "owns_ui",
                    "determinism": "static_analysis",
                    "source": spec_path.name,
                }
            )
            for el in spec.get("ui", {}).get("elements") or []:
                if not isinstance(el, dict):
                    continue
                eid = str(el.get("id") or el.get("android:id") or "").strip()
                if not eid:
                    continue
                ctrl = f"ui_control:{layout}:{eid}"
                if any(n.get("node_id") == ctrl for n in nodes):
                    continue
                nodes.append(
                    {
                        "node_id": ctrl,
                        "kind": "ui_control",
                        "label": eid,
                        "evidence": {"spec": spec_path.name},
                    }
                )
                edges.append(
                    {
                        "edge_id": _stable_edge_id(surf_id, ctrl, "owns_ui", len(edges)),
                        "from": surf_id,
                        "to": ctrl,
                        "rel": "owns_ui",
                        "determinism": "static_analysis",
                        "source": spec_path.name,
                    }
                )

    impl_idx = 0
    screen_ids = {n["node_id"] for n in nodes}
    for bucket, item in _iter_finding_lists(sf):
        impl_idx += 1
        line = int(item.get("line", 0))
        file_path = str(item.get("file") or "")
        iid = f"implementation:{bucket}:{impl_idx}"
        inferred = _infer_screen_class_from_source_path(file_path)
        ih = host(inferred) if inferred else None
        sym = _find_symbol_for_anchor(symbols_for_file, file_path, line)
        symbol_id = str((sym or {}).get("symbol_id") or "")
        nodes.append(
            {
                "node_id": iid,
                "kind": "implementation",
                "label": f"{Path(file_path).name}:{line}",
                "evidence": {
                    "bucket": bucket,
                    "file": _norm_path(file_path),
                    "line": line,
                    "kind": item.get("kind"),
                    "method": item.get("method") or "",
                    "enclosing_fn": item.get("enclosing_fn") or "",
                    "symbol_id": symbol_id,
                    "function_name": (sym or {}).get("function_name") or "",
                },
            }
        )
        if symbol_id and _function_node_id(symbol_id) in symbol_node_ids:
            edges.append(
                {
                    "edge_id": _stable_edge_id(_function_node_id(symbol_id), iid, "evidence_in_file", len(edges)),
                    "from": _function_node_id(symbol_id),
                    "to": iid,
                    "rel": "evidence_in_file",
                    "determinism": "static_analysis",
                    "source": bucket,
                }
            )
        scr = f"screen:{ih}" if ih else ""
        if scr and scr in screen_ids:
            edges.append(
                {
                    "edge_id": _stable_edge_id(scr, iid, "implements", len(edges)),
                    "from": scr,
                    "to": iid,
                    "rel": "implements",
                    "determinism": "static_analysis",
                    "source": bucket,
                }
            )

    behavior_idx = 0
    effect_stats = {
        "effect_path_total": len(effect_paths),
        "effect_path_with_line": 0,
        "effect_path_attached_to_screen": 0,
        "effect_path_attached_to_feature": 0,
        "effect_path_unmatched": 0,
        "effect_path_without_line": 0,
    }
    for item in sorted(
        effect_paths,
        key=lambda x: (
            str(x.get("source_file") or x.get("file") or ""),
            _safe_int(x.get("line")),
            str(x.get("path_id") or ""),
        ),
    ):
        source_file = str(item.get("source_file") or item.get("file") or "").strip()
        if not source_file or item.get("line") is None:
            effect_stats["effect_path_without_line"] += 1
            continue
        effect_stats["effect_path_with_line"] += 1
        behavior_idx += 1
        line = _safe_int(item.get("line"))
        path_id = str(item.get("path_id") or "")
        bid = f"behavior:effect:{_stable_token(path_id, str(behavior_idx))}"
        label = str(item.get("label") or item.get("path_display_report") or item.get("action_token") or Path(source_file).name).strip()
        screen = _resolve_effect_screen(item, screen_hosts)
        feature = screen_to_feature.get(screen or "")
        sym = _find_symbol_for_anchor(symbols_for_file, source_file, line)
        symbol_id = str((sym or {}).get("symbol_id") or "")
        nodes.append(
            {
                "node_id": bid,
                "kind": "behavior",
                "label": label,
                "logical_feature_id": feature or "",
                "evidence": {
                    "source": "ui_effect_paths.json",
                    "source_file": source_file,
                    "file": source_file,
                    "line": line,
                    "path_id": path_id,
                    "path_display_report": item.get("path_display_report") or "",
                    "path_display_legacy": item.get("path_display_legacy") or "",
                    "effect_kind": item.get("effect_kind") or "",
                    "action_token": item.get("action_token") or "",
                    "target": item.get("target") or "",
                    "entry_symbol_id": symbol_id,
                    "function_name": (sym or {}).get("function_name") or "",
                },
            }
        )
        if symbol_id and _function_node_id(symbol_id) in symbol_node_ids:
            edges.append(
                {
                    "edge_id": _stable_edge_id(bid, _function_node_id(symbol_id), "enters", len(edges)),
                    "from": bid,
                    "to": _function_node_id(symbol_id),
                    "rel": "enters",
                    "determinism": "static_analysis",
                    "source": "function_symbols.json",
                }
            )
        if screen and f"screen:{screen}" in screen_ids:
            effect_stats["effect_path_attached_to_screen"] += 1
            edges.append(
                {
                    "edge_id": _stable_edge_id(f"screen:{screen}", bid, "triggers", len(edges)),
                    "from": f"screen:{screen}",
                    "to": bid,
                    "rel": "triggers",
                    "determinism": "static_analysis",
                    "source": "ui_effect_paths.json",
                }
            )
        if feature:
            effect_stats["effect_path_attached_to_feature"] += 1
            edges.append(
                {
                    "edge_id": _stable_edge_id(f"feature:{feature}", bid, "parent_of", len(edges)),
                    "from": f"feature:{feature}",
                    "to": bid,
                    "rel": "parent_of",
                    "determinism": "static_analysis",
                    "source": "ui_effect_paths.json",
                }
            )
        else:
            effect_stats["effect_path_unmatched"] += 1
            edges.append(
                {
                    "edge_id": _stable_edge_id(product_id, bid, "parent_of", len(edges)),
                    "from": product_id,
                    "to": bid,
                    "rel": "parent_of",
                    "determinism": "static_analysis",
                    "source": "ui_effect_paths_unmatched",
                }
            )

    # Behavior chains (event → handler → effect) are the core "what happens when you
    # interact" signal for migration. They live in behavior_chains.json (385 on
    # AntennaPod); ui_effect_paths.json above is a separate, often-empty path view, so
    # without this loop the bundle reports behavior_count=0 and the translator gets no
    # behavior at all. Each chain becomes a `behavior` node, attached to its owning
    # screen via the deterministic claim hints (then handler class), and linked into
    # the call graph via the handler's entry symbol.
    chain_stats = {
        "behavior_chain_total": len(behavior_chains),
        "behavior_chains_attached_to_screen": 0,
        "behavior_chains_with_entry_symbol": 0,
        "behavior_chains_unclaimed": 0,
    }

    def _chain_sort_key(c: dict[str, Any]) -> tuple[str, int, str, str]:
        h = c.get("handler") or {}
        return (
            _norm_path(h.get("file")),
            _safe_int(h.get("line")),
            str(c.get("element_id") or ""),
            str(c.get("event_type") or ""),
        )

    for cidx, chain in enumerate(sorted(behavior_chains, key=_chain_sort_key)):
        handler = chain.get("handler") if isinstance(chain.get("handler"), dict) else {}
        event_type = str(chain.get("event_type") or "").strip()
        element_id = str(chain.get("element_id") or chain.get("view_ref") or "").strip()
        bid = f"behavior:chain:{cidx + 1}"
        owner_classes = [str(c) for c in (chain.get("claim_hints") or {}).get("owner_classes") or []]
        owner_candidates = list(owner_classes)
        if handler.get("class"):
            owner_candidates.append(str(handler.get("class")))
        screen = ""
        for cand in owner_candidates:
            hc = host(cand)
            if hc in screen_hosts:
                screen = hc
                break
        feature = screen_to_feature.get(screen or "")
        entry_symbol_id = str(handler.get("symbol_id") or "")
        effect_steps = [
            str(s.get("target") or "")
            for s in (chain.get("effect_chain") or [])
            if isinstance(s, dict) and s.get("target")
        ]
        nodes.append(
            {
                "node_id": bid,
                "kind": "behavior",
                "label": f"{event_type or 'event'}:{element_id or 'view'}",
                "logical_feature_id": feature or "",
                "evidence": {
                    "source": "behavior_chains.json",
                    "event_type": event_type,
                    "element_id": element_id,
                    "view_ref": chain.get("view_ref") or "",
                    "handler_class": handler.get("class") or "",
                    "handler_method": handler.get("method") or "",
                    "file": _norm_path(handler.get("file")),
                    "line": _safe_int(handler.get("line")),
                    "entry_symbol_id": entry_symbol_id,
                    "effect_steps": effect_steps,
                    "chain_depth": _safe_int(chain.get("chain_depth")),
                    "confidence": chain.get("confidence") or "",
                    "owner_classes": [host(c) for c in owner_classes],
                },
            }
        )
        if entry_symbol_id:
            chain_stats["behavior_chains_with_entry_symbol"] += 1
            if _function_node_id(entry_symbol_id) in symbol_node_ids:
                edges.append(
                    {
                        "edge_id": _stable_edge_id(bid, _function_node_id(entry_symbol_id), "enters", len(edges)),
                        "from": bid,
                        "to": _function_node_id(entry_symbol_id),
                        "rel": "enters",
                        "determinism": "static_analysis",
                        "source": "behavior_chains.json",
                    }
                )
        if screen and f"screen:{screen}" in screen_ids:
            chain_stats["behavior_chains_attached_to_screen"] += 1
            edges.append(
                {
                    "edge_id": _stable_edge_id(f"screen:{screen}", bid, "triggers", len(edges)),
                    "from": f"screen:{screen}",
                    "to": bid,
                    "rel": "triggers",
                    "determinism": "static_analysis",
                    "source": "behavior_chains.json",
                }
            )
        if not screen:
            chain_stats["behavior_chains_unclaimed"] += 1
        parent = f"feature:{feature}" if feature else product_id
        edges.append(
            {
                "edge_id": _stable_edge_id(parent, bid, "parent_of", len(edges)),
                "from": parent,
                "to": bid,
                "rel": "parent_of",
                "determinism": "static_analysis",
                "source": "behavior_chains.json" if feature else "behavior_chains_unclaimed",
            }
        )

    for i, e in enumerate(edges):
        if not e.get("edge_id"):
            e["edge_id"] = _stable_edge_id(str(e.get("from")), str(e.get("to")), str(e.get("rel")), i)

    coverage = _feature_line_coverage(nodes, edges)
    coverage.update(effect_stats)
    coverage.update(chain_stats)
    coverage.update(_function_coverage(nodes, edges, unresolved_calls))
    taxonomy_report = build_taxonomy_report(
        screen_hosts,
        screen_to_feature,
        screen_to_rule,
        tax_rows,
        taxonomy_meta,
        generated_taxonomy_report,
    )

    ir: dict[str, Any] = {
        "schema_version": "1.0",
        "platform": "android",
        "android_root": af.get("android_root", ""),
        "ui_fidelity": af.get("ui_fidelity"),
        "taxonomy_version": taxonomy_version,
        "nodes": nodes,
        "edges": edges,
        "meta": {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "spec_tools_navigation": "navigation_graph.json",
            "coverage": coverage,
            "taxonomy": taxonomy_report["summary"],
        },
    }
    dump_json(out_path, ir)
    dump_json(out_path.parent / "feature_spec_evidence.json", build_feature_spec_evidence(ir))
    dump_json(out_path.parent / "verify_report.json", build_verify_report(ir, Path(str(af.get("android_root") or "")), unresolved_calls))
    dump_json(out_path.parent / "taxonomy_report.json", taxonomy_report)
    return ir
