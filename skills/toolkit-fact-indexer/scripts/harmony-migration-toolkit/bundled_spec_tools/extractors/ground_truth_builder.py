"""
ground_truth_builder.py
合并 xml_extractor + source_extractor 输出，生成完整 ground truth。

绑定逻辑（通用，不依赖框架）：
  1. event_registrations  → view_ref (camelCase) 对齐 XML id (snake_case) → 绑定行为
  2. id_dispatchers       → item_id 直接对齐 XML id → 绑定行为
  3. visibility_controls  → view_ref / item_id 对齐 → 标记条件可见
  4. inflates             → layout 未在 XML 中出现的 → dynamic_gap
  5. data_driven_ui       → 独立的 data_driven_gap，含 items_options 字段

误报抑制：
  - unmatched 列表排除已知非 View 系统对象的注册（decorView、contentResolver 等）
  - unmatched 列表排除 PascalCase view_ref（类型名，非实例变量）
"""
import json
import re
from pathlib import Path

from .view_ref_utils import camel_to_snake as _camel_to_snake
from .view_ref_utils import clean_view_ref as _clean_ref
from .view_ref_utils import resolve_view_id as _resolve_view_id
from .unbound_control_inference import build_layout_contexts, infer_unbound_event_bindings


def build(xml_result: dict, source_result: dict, *,
          view_ref_id_map: dict | None = None,
          nav_result: dict | None = None,
          adapter_layouts: list[dict] | None = None) -> dict:
    elements = {e["id"]: e for e in xml_result["elements"] if e.get("id")}
    findings = source_result["findings"]
    file_maps = view_ref_id_map or {}

    # ── 1. event_registrations → 绑定到 XML 元素 ─────────────────
    unmatched = []
    non_ui_bindings = []
    for reg in findings.get("event_registrations", []):
        raw_ref = _clean_ref(reg.get("view_ref", ""))
        file_map = file_maps.get(reg.get("file", ""))
        view_id = _resolve_view_id(raw_ref, elements, file_map)

        if view_id:
            elements[view_id].setdefault("behaviors", []).append({
                "event":        reg["event_type"],
                "method":       reg["method"],
                "file":         reg["file"],
                "line":         reg["line"],
                "enclosing_fn": reg.get("enclosing_fn", ""),
            })
        elif reg.get("is_view") is False:
            non_ui_bindings.append(reg)
        else:
            reg["_resolved_id_attempt"] = _camel_to_snake(raw_ref) if raw_ref else ""
            unmatched.append(reg)

    # ── 2. id_dispatchers → 绑定 menu / action items ──────────────
    for disp in findings.get("id_dispatchers", []):
        item_id = disp.get("item_id", "")
        if item_id and item_id in elements:
            elements[item_id].setdefault("behaviors", []).append({
                "event":        "id_dispatch",
                "handler":      disp.get("handler", ""),
                "file":         disp["file"],
                "line":         disp["line"],
                "enclosing_fn": disp.get("enclosing_fn", ""),
            })
        else:
            unmatched.append(disp)

    # ── 3. visibility_controls → 标记条件可见 ────────────────────
    for vc in findings.get("visibility_controls", []):
        raw = _clean_ref(vc.get("view_ref", "") or vc.get("item_id", ""))
        vc_file_map = file_maps.get(vc.get("file", ""))
        vid = _resolve_view_id(raw, elements, vc_file_map)

        if vid:
            elem = elements[vid]
            elem["conditional_visibility"] = True
            elem.setdefault("visibility_conditions", []).append({
                "property":  vc.get("property") or "isVisible",
                "condition": vc.get("condition", ""),
                "file":      vc["file"],
                "line":      vc["line"],
            })

    # ── 4. inflates → dynamic_gap ────────────────────────────────
    static_layouts = {e.get("layout", "") for e in xml_result["elements"]}
    gap_elements   = []
    seen_layouts   = set()

    for inf in findings.get("inflates", []):
        layout = inf.get("layout", "")
        if not layout or layout in seen_layouts:
            continue
        seen_layouts.add(layout)
        gap_elements.append({
            "source":       inf["kind"],   # inflate_layout / inflate_binding / static_binding
            "layout":       layout,
            "binding_class": inf.get("binding_class", ""),
            "enclosing_fn": inf.get("enclosing_fn", ""),
            "file":         inf["file"],
            "line":         inf["line"],
            "in_static_xml": layout in static_layouts,
        })

    # ── 5. data_driven_ui → 独立 gap ─────────────────────────────
    for dd in findings.get("data_driven_ui", []):
        gap_elements.append({
            "source":        "data_driven_ui",
            "component":     dd["component"],
            "items_source":  dd.get("items_source", ""),
            "items_range":   dd.get("items_range", ""),
            "items_options": dd.get("items_options", []),
            "enclosing_fn":  dd.get("enclosing_fn", ""),
            "file":          dd["file"],
            "line":          dd["line"],
            "in_static_xml": False,
            "note":          dd.get("note", ""),
        })

    # ── 6. 推断未绑定 interactive controls ───────────────────────
    layout_contexts = build_layout_contexts(nav_result or {}, adapter_layouts)
    inferred_bindings, inferred_stats = infer_unbound_event_bindings(list(elements.values()), layout_contexts)

    # ── 7. 统计 ──────────────────────────────────────────────────
    all_elems      = list(elements.values())
    with_behaviors = [e for e in all_elems if e.get("behaviors")]
    conditional    = [e for e in all_elems if e.get("conditional_visibility")]
    pure_dynamic   = [g for g in gap_elements if not g["in_static_xml"]]
    data_driven    = [g for g in gap_elements if g.get("source") == "data_driven_ui"]
    interactive_or_bound = [e for e in all_elems
                           if e.get("is_interactive") or e.get("behaviors")]

    stats = {
        "xml_elements_total":         len(all_elems),
        "xml_interactive":            sum(1 for e in all_elems if e.get("is_interactive")),
        "xml_with_behavior_bound":    len(with_behaviors),
        "xml_interactive_or_bound":   len(interactive_or_bound),
        "xml_conditional_visibility": len(conditional),
        "dynamic_gap_total":          len(gap_elements),
        "dynamic_gap_pure_new":       len(pure_dynamic),
        "data_driven_ui":             len(data_driven),
        "non_ui_bindings":            len(non_ui_bindings),
        "unmatched":                  len(unmatched),
        "inferred_unbound_bindings":  len(inferred_bindings),
        "inferred_unbound_covered":   inferred_stats.get("covered", 0),
        "inferred_unbound_uncovered": inferred_stats.get("uncovered", 0),
    }

    return {
        "static_elements": all_elems,
        "dynamic_gap":     gap_elements,
        "non_ui_bindings": non_ui_bindings,
        "unmatched":       unmatched,
        "inferred_event_bindings": inferred_bindings,
        "inferred_event_binding_stats": inferred_stats,
        "coverage_stats":  stats,
    }


if __name__ == "__main__":
    import sys
    xml_path = Path("output/static_xml.json")
    src_path = Path("output/source_findings.json")

    if not xml_path.exists() or not src_path.exists():
        print("Run xml_extractor.py and source_extractor.py first.")
        sys.exit(1)

    xml_result = json.loads(xml_path.read_text(encoding="utf-8"))
    src_result = json.loads(src_path.read_text(encoding="utf-8"))
    result     = build(xml_result, src_result)

    out = Path("output/ground_truth.json")
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False))

    s = result["coverage_stats"]
    print("Ground truth built:")
    for k, v in s.items():
        print(f"  {k}: {v}")
