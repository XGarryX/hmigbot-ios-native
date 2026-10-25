"""
generate_specs.py
从 ground_truth + navigation_graph + ui_paths 生成每屏幕 spec。
用法：python generate_specs.py
"""
import json
import re
import sys
from pathlib import Path
from collections import defaultdict

from extractors.unbound_control_inference import build_layout_contexts

sys.path.insert(0, str(Path(__file__).parent))


def _normalize_layout(name: str) -> str:
    """Collapse underscores around digits for comparison: media3_video → media3video."""
    return re.sub(r'_+', '', name)


_SUMMARY_STEP_TYPES = frozenset({"navigate", "ui_feedback", "ui_update", "async"})


def _summarize_effects(steps: list[dict]) -> list[str]:
    """Flatten a nested effect_chain into deduplicated summary tags.

    Returns e.g. ["navigate:finish", "ui_feedback:Toast", "ui_update:setVisibility"].
    Skips generic 'call' and 'condition' steps — they don't carry translation-relevant info.
    """
    tags: list[str] = []
    seen: set[str] = set()

    def walk(slist: list[dict]) -> None:
        for s in slist:
            st = s.get("step", "")
            if st in _SUMMARY_STEP_TYPES:
                detail = s.get("target") or s.get("action") or s.get("destination") or s.get("via") or ""
                detail = detail.rstrip("()")
                tag = f"{st}:{detail}" if detail else st
                if tag not in seen:
                    seen.add(tag)
                    tags.append(tag)
            for key in ("nested", "then", "else"):
                child = s.get(key)
                if child and isinstance(child, list):
                    walk(child)

    walk(steps)
    return tags


def _dedupe_layout_variants(all_layouts: set[str], known_layouts: set[str]) -> set[str]:
    """Remove layout names that are snake_case variants of a known XML layout.

    When camelCase→snake_case produces 'media3video_player_activity' but the
    real XML file is 'media3_video_player_activity', drop the non-existent variant.
    """
    by_norm: dict[str, list[str]] = {}
    for name in all_layouts:
        norm = _normalize_layout(name)
        by_norm.setdefault(norm, []).append(name)

    result: set[str] = set()
    for norm, variants in by_norm.items():
        if len(variants) == 1:
            result.add(variants[0])
            continue
        in_known = [v for v in variants if v in known_layouts]
        if in_known:
            result.add(in_known[0])
        else:
            result.add(variants[0])
    return result



def _matches_claim_hints(binding: dict, layout_name: str, class_name: str, owner_classes: set[str]) -> bool:
    claim_hints = binding.get("claim_hints") or {}
    hinted_classes = set(claim_hints.get("owner_classes") or [])
    hinted_layout = binding.get("layout", "")
    if hinted_layout and hinted_layout == layout_name:
        return True
    if class_name and hinted_classes and class_name in hinted_classes:
        return True
    if hinted_classes and owner_classes and hinted_classes.intersection(owner_classes):
        return True
    return False


def _build_brief(ui_elements, event_bindings, nav_out_edges, nav_in_edges,
                 screen_fragments, screen_adapters, screen_lifecycle):
    """Build a concise LLM-friendly summary from v2 data."""
    eb_by_id: dict[str, list[str]] = {}
    for eb in event_bindings:
        eid = eb.get("element_id", "")
        if eid:
            eb_by_id.setdefault(eid, []).extend(eb.get("effect_summary", []))

    controls = []
    for e in ui_elements:
        eid = e.get("id", "")
        actions = list(dict.fromkeys(eb_by_id.get(eid, [])))
        if e.get("is_interactive") or actions:
            controls.append({
                "id": eid,
                "type": e.get("type", ""),
                "label": e.get("label", ""),
                "actions": actions,
            })

    return {
        "interactive_controls": controls,
        "nav_in": [f"{ep['from']} ({ep['type']})" for ep in nav_in_edges],
        "nav_out": [f"→ {ep['destination']} ({ep['trigger']})" for ep in nav_out_edges],
        "has_fragments": len(screen_fragments) > 0,
        "has_adapters": len(screen_adapters) > 0,
        "lifecycle_methods": list(screen_lifecycle.keys()) if screen_lifecycle else [],
    }


def generate_all_specs(nav, gt, paths, dag, specs_dir, *,
                       layout_trees=None, fragments=None,
                       dynamic_elements=None, behavior_chains=None,
                       lifecycle_hooks=None, adapter_layouts=None,
                       inflate_owner_layouts=None,
                       spec_version="1.0"):
    """为导航图中的每个屏幕生成 HarmonyOS 迁移 spec。"""
    specs_dir = Path(specs_dir)
    specs_dir.mkdir(parents=True, exist_ok=True)

    # ── 1. 按 layout 分组 static_elements ──
    by_layout = defaultdict(list)
    for e in gt["static_elements"]:
        layout = e.get("layout", "")
        if layout:
            by_layout[layout].append(e)

    # ── 2. 按 layout 分组 dynamic_gap ──
    gap_by_layout = defaultdict(list)
    for g in gt["dynamic_gap"]:
        layout = g.get("layout", "")
        if layout:
            gap_by_layout[layout].append(g)

    # ── 3. 从 ui_paths 提取唯一 screen → layout 映射 ──
    screen_layouts = {}
    if paths and isinstance(paths[0], dict):
        for p in paths:
            screen = p.get("screen", "")
            eid = p.get("element_id", "")
            prim = p.get("primary_layout", "")
            if eid:
                for e in gt["static_elements"]:
                    if e.get("id") == eid:
                        layout = e.get("layout", "")
                        if layout and layout not in screen_layouts.values():
                            screen_layouts[screen] = layout
                        break
            elif screen and prim and prim not in screen_layouts.values():
                screen_layouts[screen] = prim
    else:
        # paths 是形如 "Browser > Ondestroy" 的字符串列表
        for p in paths:
            parts = p.split(">", 1)
            screen = parts[0].strip() if parts else p
            if screen and screen not in screen_layouts:
                screen_layouts[screen] = ""

    for name, node in dag.get("nodes", {}).items():
        layout = node.get("layout", "")
        if layout and layout not in screen_layouts.values():
            screen_layouts[name] = layout

    # ── 4. 从 navigation_graph 提取边 ──
    edges_from = defaultdict(list)
    edges_to = defaultdict(list)
    for edge in nav.get("edges", []):
        edges_from[edge["from"]].append(edge)
        edges_to[edge["to"]].append(edge)

    # ── 5. 从 class_layouts 反查 ──
    class_to_layout = nav.get("class_layouts", {})

    # ── 6. 从 navigation_graph 节点提取 layout ──
    nav_layouts = set()
    for name, node in nav.get("nodes", {}).items():
        layout = node.get("layout", "")
        if layout:
            nav_layouts.add(layout)

    # ── 7. 构建所有屏幕的 layout 集合 ──
    all_layouts = (
        set(by_layout.keys())
        | set(gap_by_layout.keys())
        | set(screen_layouts.values())
        | set(class_to_layout.values())
        | nav_layouts
    )

    # ── 7b. 去重：合并仅因 snake_case 转换差异（数字边界等）产生的变体 ──
    known_layouts = set(by_layout.keys())
    if layout_trees:
        known_layouts |= set(layout_trees.keys())
    all_layouts = _dedupe_layout_variants(all_layouts, known_layouts)

    # ── 8. 构建 layout→classes 反向索引 ──
    # class_to_layout 已包含 inflate_owner_map 合并进来的主映射（见 main.py），
    # 因此 inflate 派生的所有权在此自动流入，无需额外多映射（避免一个类映射到
    # 多个 layout 时把同一 chain 重复塞进多个 spec）。
    layout_to_classes: dict[str, set[str]] = defaultdict(set)
    for cn, ly in class_to_layout.items():
        layout_to_classes[ly].add(cn)
    for cn, node in nav.get("nodes", {}).items():
        ly = node.get("layout", "")
        if ly:
            layout_to_classes[ly].add(cn)
    layout_contexts = build_layout_contexts(nav, adapter_layouts)
    inferred_bindings = gt.get("inferred_event_bindings", [])

    # ── 8b. 构建 class→layout 反向索引（用于 orphan chain fallback claiming）──
    class_to_layout_set: dict[str, set[str]] = defaultdict(set)
    for cn, ly in class_to_layout.items():
        if ly:
            class_to_layout_set[cn].add(ly)
    for cn, node in nav.get("nodes", {}).items():
        ly = node.get("layout", "")
        if ly:
            class_to_layout_set[cn].add(ly)
    for al in (adapter_layouts or []):
        ac = al.get("adapter_class", "")
        il = al.get("item_layout", "")
        if ac and il:
            class_to_layout_set[ac].add(il)
        hc = al.get("host_class", "")
        if hc and il:
            class_to_layout_set[hc].add(il)

    # ── 9. 为每个 layout 生成 spec ──
    generated = 0
    synthetic_counts: dict[str, int] = defaultdict(int)
    assigned_chain_ids: set[int] = set()
    total_assignments = 0
    for layout_name in sorted(all_layouts):
        if not layout_name:
            continue

        elements = by_layout.get(layout_name, [])
        gaps = gap_by_layout.get(layout_name, [])

        # 查找对应的 class 名（先查 class_to_layout，再查 nav nodes）
        class_name = ""
        for cn, cl in class_to_layout.items():
            if cl == layout_name:
                class_name = cn
                break
        if not class_name:
            for cn, node in nav.get("nodes", {}).items():
                if node.get("layout", "") == layout_name:
                    class_name = cn
                    break
        # Fill-only fallback: a layout that no navigation-derived mapping owns
        # (audioplayer_fragment, fragment_subscriptions, item layouts …) gets its
        # owner from the real inflate site (R.layout.x inside class Y). This is
        # deterministic ground truth, kept single-owner so shared/partial layouts
        # (headers, cards, include-only views) stay honestly unowned. It only fills
        # gaps — never overrides a mapping the navigation graph already produced.
        if not class_name and inflate_owner_layouts:
            class_name = inflate_owner_layouts.get(layout_name, "")

        # 查找导航边
        nav_out = []
        nav_in = []
        for cn in [class_name] if class_name else []:
            nav_out = edges_from.get(cn, [])
            nav_in = edges_to.get(cn, [])

        # ui_elements
        ui_elements = []
        for e in elements:
            ui_elements.append({
                "id": e.get("id", ""),
                "type": e.get("tag", ""),
                "label": e.get("text", "") or e.get("hint", "") or e.get("content_desc", ""),
                "visibility": "conditional" if e.get("conditional_visibility") else "always",
                "condition": "; ".join(
                    vc.get("condition", "")
                    for vc in e.get("visibility_conditions", [])
                ),
                "is_interactive": e.get("is_interactive", False),
            })

        # dynamic_ui (from gaps)
        dynamic_ui = []
        for g in gaps:
            entry = {
                "source": g.get("source", ""),
                "layout": g.get("layout", ""),
                "enclosing_fn": g.get("enclosing_fn", ""),
                "file": g.get("file", ""),
            }
            if g.get("items_options"):
                entry["options"] = g["items_options"]
                entry["items_source"] = g.get("items_source", "")
            dynamic_ui.append(entry)

        # navigation
        navigation = []
        for edge in nav_out:
            navigation.append({
                "trigger": edge.get("trigger", ""),
                "destination": edge.get("to", ""),
                "destination_layout": edge.get("to_layout", ""),
                "type": edge.get("type", ""),
                "via": edge.get("via", ""),
            })

        entry_points = []
        for edge in nav_in:
            entry_points.append({
                "from": edge.get("from", ""),
                "trigger": edge.get("trigger", ""),
                "type": edge.get("type", ""),
            })

        # screen_type（优先从 nav node type 推断）
        screen_type = "unknown"
        if class_name:
            node_type = nav.get("nodes", {}).get(class_name, {}).get("type", "")
            if node_type:
                screen_type = node_type
            elif "Activity" in class_name:
                screen_type = "activity"
            elif "Fragment" in class_name:
                screen_type = "fragment"
            elif "Dialog" in class_name:
                screen_type = "dialog"
            elif "Adapter" in class_name:
                screen_type = "adapter_item"
        if screen_type == "unknown" and layout_name.startswith("dialog_"):
            screen_type = "dialog"
        elif screen_type == "unknown" and (layout_name.startswith("item_") or layout_name.startswith("editor_")):
            screen_type = "adapter_item"

        source = "library" if any(
            e.get("source", "").startswith("library_") for e in elements
        ) else "project"

        # ── v2 extensions (compute before building spec dict) ──
        screen_fragments = []
        screen_dynamic = []
        event_bindings = []
        screen_lifecycle = {}
        screen_adapters = []
        brief = {}
        ui_tree = None
        behavior_entry = {}
        all_ids = {e.get("id", "") for e in elements if e.get("id")}
        owner_classes = layout_to_classes.get(layout_name, set())
        if class_name:
            owner_classes = owner_classes | {class_name}

        if spec_version >= "2.0":
            if layout_trees and layout_name in layout_trees:
                ui_tree = layout_trees[layout_name]

            if fragments:
                for frag in fragments:
                    cid = frag.get("container_id", "")
                    host = frag.get("host_class", "")
                    if cid in all_ids or (class_name and host == class_name):
                        screen_fragments.append({
                            "class": frag.get("class", ""),
                            "container_id": cid,
                            "attach_method": frag.get("attach_method", ""),
                        })

            if dynamic_elements:
                for de in dynamic_elements:
                    if class_name and de.get("host_class", "") == class_name:
                        screen_dynamic.append({
                            "view_type": de.get("view_type", ""),
                            "creation_method": de.get("creation_method", ""),
                            "container_id": de.get("container_id", ""),
                            "properties": de.get("properties", {}),
                        })

            if behavior_chains:
                for bc_idx, bc in enumerate(behavior_chains):
                    eid = bc.get("element_id", "")
                    handler_class = bc.get("handler", {}).get("class", "")
                    handler_file = bc.get("handler", {}).get("file", "")
                    bc_owner_classes = set(bc.get("claim_hints", {}).get("owner_classes") or [])
                    if not bc_owner_classes and handler_class:
                        bc_owner_classes = {handler_class}
                    if eid in all_ids or (bc_owner_classes and bc_owner_classes & owner_classes):
                        chain = bc.get("effect_chain", [])
                        event_bindings.append({
                            "element_id": eid,
                            "event_type": bc.get("event_type", ""),
                            "handler_method": bc.get("handler", {}).get("method", ""),
                            "handler_file": bc.get("handler", {}).get("file", ""),
                            "handler_line": bc.get("handler", {}).get("line", 0),
                            "effect_summary": _summarize_effects(chain),
                            "effect_chain": chain,
                            "chain_depth": bc.get("chain_depth", 0),
                            "confidence": bc.get("confidence", "static_analysis"),
                        })
                        assigned_chain_ids.add(bc_idx)
                        total_assignments += 1
                    elif bc_owner_classes and any(
                        layout_name in class_to_layout_set.get(oc, set())
                        for oc in bc_owner_classes
                    ):
                        chain = bc.get("effect_chain", [])
                        event_bindings.append({
                            "element_id": eid,
                            "event_type": bc.get("event_type", ""),
                            "handler_method": bc.get("handler", {}).get("method", ""),
                            "handler_file": bc.get("handler", {}).get("file", ""),
                            "handler_line": bc.get("handler", {}).get("line", 0),
                            "effect_summary": _summarize_effects(chain),
                            "effect_chain": chain,
                            "chain_depth": bc.get("chain_depth", 0),
                            "confidence": bc.get("confidence", "static_analysis"),
                            "binding_source": "handler_class_layout_fallback",
                        })
                        assigned_chain_ids.add(bc_idx)
                        total_assignments += 1

            if lifecycle_hooks and class_name in lifecycle_hooks:
                screen_lifecycle = lifecycle_hooks[class_name]

            if adapter_layouts:
                for al in adapter_layouts:
                    if al.get("host_class", "") == class_name:
                        screen_adapters.append({
                            "container_id": al.get("host_id", ""),
                            "adapter_class": al.get("adapter_class", ""),
                            "item_layout": al.get("item_layout", ""),
                        })

            # ── Attach inferred bindings for unbound interactive controls ──
            bound_ids = {eb.get("element_id", "") for eb in event_bindings}
            for inferred in inferred_bindings:
                eid = inferred.get("element_id", "")
                if not eid or eid in bound_ids:
                    continue
                if not _matches_claim_hints(inferred, layout_name, class_name, owner_classes):
                    continue
                event_bindings.append({
                    "element_id": eid,
                    "event_type": inferred.get("event_type", ""),
                    "handler_method": inferred.get("handler_method", ""),
                    "handler_file": inferred.get("handler_file", ""),
                    "handler_line": inferred.get("handler_line", 0),
                    "effect_summary": inferred.get("effect_summary", []),
                    "effect_chain": inferred.get("effect_chain", []),
                    "chain_depth": inferred.get("chain_depth", 0),
                    "confidence": inferred.get("confidence", "inferred"),
                    "binding_source": inferred.get("binding_source", "unbound_inference"),
                    "inference_category": inferred.get("inference_category", ""),
                    "claim_hints": inferred.get("claim_hints", {}),
                })
                synthetic_counts[inferred.get("inference_category", "programmatic")] += 1
                bound_ids.add(eid)

            if event_bindings:
                behavior_entry["event_bindings"] = event_bindings
            if screen_lifecycle:
                behavior_entry["lifecycle_hooks"] = screen_lifecycle
            if screen_fragments:
                behavior_entry["fragments"] = screen_fragments
            if screen_adapters:
                behavior_entry["adapter_bindings"] = screen_adapters

            # Keep ui.elements.is_interactive consistent with brief: a control with a
            # resolved event binding is interactive even when its XML tag (ImageView,
            # TextView, …) is not inherently interactive. Otherwise the same control
            # reads as interactive in brief.interactive_controls but is_interactive=false
            # in ui.elements, which is contradictory for a translating agent.
            bound_ui_ids = {eb.get("element_id", "") for eb in event_bindings if eb.get("element_id")}
            for ue in ui_elements:
                if ue.get("id") in bound_ui_ids:
                    ue["is_interactive"] = True

            brief = _build_brief(
                ui_elements, event_bindings, navigation, entry_points,
                screen_fragments, screen_adapters, screen_lifecycle,
            )

        # ── Build spec dict in progressive-disclosure order ──
        # brief 最前（LLM 概览先读），其后才是身份/导航/UI/行为/统计。
        stats = {
            "conditional_visibility": sum(1 for e in elements if e.get("conditional_visibility")),
            "inflated_layouts": len(gaps),
            "nav_out": len(nav_out),
            "nav_in": len(nav_in),
        }
        if spec_version >= "2.0":
            stats["fragments"] = len(screen_fragments)
            stats["programmatic_views"] = len(screen_dynamic)
            stats["event_bindings"] = len(event_bindings)
            stats["event_bindings_with_chain"] = sum(
                1 for eb in event_bindings if eb.get("effect_chain")
            )

        spec = {}
        if brief:
            spec["brief"] = brief
        spec["screen_type"] = screen_type
        spec["class"] = class_name
        spec["layout"] = layout_name
        spec["source"] = source
        spec["navigation"] = {
            "entry_points": entry_points,
            "exit_points": navigation,
        }
        ui_section = {"elements": ui_elements}
        if spec_version >= "2.0":
            ui_section["tree"] = ui_tree
        ui_section["inflated_layouts"] = dynamic_ui
        if spec_version >= "2.0":
            ui_section["programmatic_views"] = screen_dynamic
        spec["ui"] = ui_section
        if behavior_entry:
            spec["behavior"] = behavior_entry
        spec["stats"] = stats

        out_path = specs_dir / f"{layout_name}_spec.json"
        out_path.write_text(json.dumps(spec, indent=2, ensure_ascii=False), encoding="utf-8")
        generated += 1
        print(f"  [{screen_type:12s}] {layout_name:50s}  elems={len(elements):3d}  gaps={len(gaps):2d}  nav={len(nav_out):2d}in/{len(nav_in):2d}out")

    print(f"\nGenerated {generated} specs in {specs_dir}")

    # ── screen_index.json — global summary for LLM overview ──
    index_entries = []
    for spec_path in sorted(specs_dir.glob("*_spec.json")):
        try:
            spec = json.loads(spec_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        brief = spec.get("brief", {})
        all_actions: list[str] = []
        for ctrl in brief.get("interactive_controls", []):
            all_actions.extend(ctrl.get("actions", []))
        index_entries.append({
            "layout": spec.get("layout", ""),
            "class": spec.get("class", ""),
            "type": spec.get("screen_type", ""),
            "controls": len(spec.get("ui", {}).get("elements", [])),
            "interactive": sum(1 for e in spec.get("ui", {}).get("elements", []) if e.get("is_interactive")),
            "event_bindings": spec.get("stats", {}).get("event_bindings", 0),
            "nav_in": brief.get("nav_in", []),
            "nav_out": brief.get("nav_out", []),
            "tags": list(dict.fromkeys(all_actions)),
            "spec_file": spec_path.name,
        })

    index_path = specs_dir.parent / "screen_index.json"
    index_data = {
        "total_screens": len(index_entries),
        "screens": index_entries,
    }
    index_path.write_text(json.dumps(index_data, indent=2, ensure_ascii=False), encoding="utf-8")

    total_chains = len(behavior_chains) if behavior_chains else 0
    assigned = len(assigned_chain_ids)
    synthetic_total = sum(synthetic_counts.values())
    total_eb = sum(e.get("event_bindings", 0) for e in index_entries)

    fallback_claimed = 0
    for spec_path in sorted(specs_dir.glob("*_spec.json")):
        try:
            spec_data = json.loads(spec_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        for eb in spec_data.get("behavior", {}).get("event_bindings", []):
            if eb.get("binding_source") == "handler_class_layout_fallback":
                fallback_claimed += 1

    return {
        "total_chains": total_chains,
        "assigned": assigned,
        "orphan": total_chains - assigned,
        "duplicated": total_assignments - assigned,
        "synthetic": synthetic_total,
        "fallback_claimed": fallback_claimed,
        "total_event_bindings": total_eb,
        # Indices into `behavior_chains` that landed in some screen spec. Lets
        # callers derive the orphan set (chains not in this list) without
        # re-implementing the claim predicate.
        "assigned_chain_ids": sorted(assigned_chain_ids),
    }


if __name__ == "__main__":
    BASE = Path(__file__).parent / "output"
    OUT = BASE / "specs"

    gt = json.loads((BASE / "ground_truth.json").read_text(encoding="utf-8"))
    nav = json.loads((BASE / "navigation_graph.json").read_text(encoding="utf-8"))
    dag = json.loads((BASE / "ui_dag.json").read_text(encoding="utf-8"))
    paths = json.loads((BASE / "ui_paths.json").read_text(encoding="utf-8"))

    generate_all_specs(nav, gt, paths, dag, OUT)
