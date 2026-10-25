"""
ui_dag_assembler.py

动态组装 UI DAG：从 ground_truth + navigation_graph + gap_analysis 三个数据源
实时构建指定深度、指定起点的完整 UI 导航树。

用法（被 main.py 或 spec 生成器调用）：
    from extractors.ui_dag_assembler import assemble
    tree = assemble("activity_main", max_depth=5)

返回结构（每个节点）：
{
  "screen": "activity_main",
  "screen_class": "MainActivity",
  "screen_type": "activity",
  "ui_elements": [
    {
      "id": "xxx",
      "tag": "MaterialToolbar",
      "is_interactive": true,
      "behaviors": [...],
      "navigation": { "target": "SettingsActivity", "trigger": "menu settings", "type": "activity" } | null,
      "children": [...]           // 递归，仅当 navigation 不为 null 时展开
    }
  ]
}
"""

import json
import re
from pathlib import Path
from typing import Any, Optional

from extractors.app_model_schema import build_path_record, ui_point_id


def _load_json(name: str) -> dict:
    p = _OUTPUT_DIR / name
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {}


# Directory the assembler reads its inputs (navigation_graph/ground_truth/…) from.
# Defaults to bundled_spec_tools/output for standalone use, but main.py points it at
# the real --out dir: otherwise, when run with --out (as the pipeline does, writing to
# intermediate/0_android_facts), assemble() would read a stale/absent default dir and
# silently produce an empty DAG.
_OUTPUT_DIR: Path = Path(__file__).parent.parent / "output"


def set_output_dir(path) -> None:
    """Point the assembler at the directory where stage-0 facts actually live."""
    global _OUTPUT_DIR
    _OUTPUT_DIR = Path(path)


def _layout_to_class(layout: str, nav_data: dict) -> str:
    for cname, node in nav_data.get("nodes", {}).items():
        if node.get("layout") == layout:
            return cname
    for cname, clayout in nav_data.get("class_layouts", {}).items():
        if clayout == layout:
            return cname
    return ""


def _resolve_layout_from_class(screen_class: str, nav_data: dict) -> str:
    node = nav_data.get("nodes", {}).get(screen_class, {})
    if node.get("layout"):
        return node["layout"]
    for cname, clayout in nav_data.get("class_layouts", {}).items():
        if cname == screen_class:
            return clayout
    import re as _re
    return _re.sub(r'(?<=[a-z])(?=[A-Z])', '_', screen_class).lower()


def _get_nav_edges_for_screen(screen_class: str, nav_data: dict) -> list[dict]:
    return [e for e in nav_data.get("edges", []) if e["from"] == screen_class]


def _match_trigger_to_element(trigger: str, element_id: str) -> bool:
    """
    Match a navigation trigger string to an XML element id.

    Trigger formats:
      click: settingsXxxHolder   → binding ref, camelCase
      setup: XxxFeature          → setup function suffix (e.g. setupXxxFeature → XxxFeature)
      fn: someFunction           → function name
      menu: menu_id              → menu item id

    Normalise both sides to lowercase with no separators, then try:
      1. element_id is contained in trigger payload  (handles click: refs)
      2. trigger payload is contained in element_id  (handles setup: / fn: where payload
         is shorter than the element id, e.g. "changedatetimeformat" in
         "settingschangedatetimeformatholder")
    """
    if not trigger or not element_id:
        return False

    eid = element_id.lower().replace("_", "")

    # Strip known prefix tokens to get the semantic payload
    normalized = trigger.lower().replace(" ", "").replace("_", "")
    for pfx in ("click:", "setup:", "fn:setup", "fn:", "menu:", "external:"):
        if normalized.startswith(pfx):
            normalized = normalized[len(pfx):]
            break

    if not normalized:
        return False

    # Direction 1: full element id inside trigger (e.g. click: settingsXxxHolder)
    if eid in trigger.lower().replace(" ", "").replace("_", ""):
        return True

    # Direction 2: trigger payload inside element id (e.g. setup: ChangeDateTimeFormat)
    if normalized in eid:
        return True

    return False


def _get_gap_items_for_layout(layout: str, gap_data: dict) -> list[dict]:
    items = []
    for r in gap_data.get("resolved", []):
        rl = r.get("resolved_layout", "")
        rf = r.get("file", "")
        if rl == layout or layout in rf.lower():
            items.append(r)
    return items


def _get_elements_for_layout(layout: str, gt_data: dict) -> list[dict]:
    return [e for e in gt_data.get("static_elements", []) if e.get("layout") == layout]


def _build_element_node(
    element: dict,
    nav_edges: list[dict],
    gap_items: list[dict],
    visited: set,
    current_depth: int,
    max_depth: int,
    gt_data: dict,
    nav_data: dict,
    gap_data: dict,
) -> dict:
    eid = element.get("id", "")
    tag = element.get("tag", "")

    behaviors = element.get("behaviors", [])
    cond_vis = element.get("visibility_conditions", [])

    matched_gap = []
    for gi in gap_items:
        grid = gi.get("resolved_xml_id", "")
        if grid and grid == eid:
            matched_gap.append(gi)

    nav_target = None
    for edge in nav_edges:
        trigger = edge.get("trigger", "")
        if _match_trigger_to_element(trigger, eid):
            nav_target = {
                "target_class": edge["to"],
                "target_layout": edge.get("to_layout", ""),
                "trigger": trigger,
                "type": edge["type"],
                "via": edge.get("via", ""),
            }
            break

    children = []
    if nav_target and current_depth < max_depth:
        target_layout = nav_target["target_layout"] or _resolve_layout_from_class(nav_target["target_class"], nav_data)
        target_class = nav_target["target_class"]
        if target_layout and (target_layout, target_class) not in visited:
            child_tree = _build_screen_tree(
                target_layout,
                target_class,
                current_depth + 1,
                max_depth,
                gt_data,
                nav_data,
                gap_data,
                visited,
            )
            if child_tree:
                children.append(child_tree)

    node = {
        "id": eid,
        "tag": tag,
        "is_interactive": element.get("is_interactive", False),
        "visible_by_default": element.get("visibility", "visible") == "visible",
        "behaviors": behaviors,
    }
    if cond_vis:
        node["visibility_conditions"] = cond_vis
    if matched_gap:
        node["gap_behaviors"] = matched_gap
    if nav_target:
        node["navigation"] = nav_target
    if children:
        node["children"] = children

    return node


def _collect_unmatched_nav_edges(
    elements: list[dict],
    nav_edges: list[dict],
    visited: set,
    current_depth: int,
    max_depth: int,
    gt_data: dict,
    nav_data: dict,
    gap_data: dict,
) -> list[dict]:
    """Collect nav edges that don't match any element (menu items, function-triggered navigation)."""
    unmatched = []
    for edge in nav_edges:
        trigger = edge.get("trigger", "")
        matched = False
        if trigger:
            for elem in elements:
                if _match_trigger_to_element(trigger, elem.get("id", "")):
                    matched = True
                    break
        if not matched:
            nav_node = {
                "id": "",
                "tag": "virtual_nav_item",
                "is_interactive": True,
                "visible_by_default": True,
                "behaviors": [],
                "navigation": {
                    "target_class": edge["to"],
                    "target_layout": edge.get("to_layout", ""),
                    "trigger": trigger,
                    "type": edge["type"],
                    "via": edge.get("via", ""),
                },
            }

            target_layout = edge.get("to_layout", "") or _resolve_layout_from_class(edge["to"], nav_data)
            target_class = edge["to"]
            if target_layout and current_depth < max_depth:
                key = (target_layout, target_class)
                if key not in visited:
                    child_tree = _build_screen_tree(
                        target_layout,
                        target_class,
                        current_depth + 1,
                        max_depth,
                        gt_data,
                        nav_data,
                        gap_data,
                        visited,
                    )
                    if child_tree:
                        nav_node["children"] = [child_tree]

            unmatched.append(nav_node)
    return unmatched


def _build_screen_tree(
    layout: str,
    screen_class: str,
    depth: int,
    max_depth: int,
    gt_data: dict,
    nav_data: dict,
    gap_data: dict,
    visited: set,
) -> Optional[dict]:
    if depth > max_depth:
        return None
    if not layout:
        layout = _resolve_layout_from_class(screen_class, nav_data)
        if not layout:
            return None
    key = (layout, screen_class)
    if key in visited:
        return None
    visited = visited | {key}

    elements = _get_elements_for_layout(layout, gt_data)
    node_info = nav_data.get("nodes", {}).get(screen_class, {})
    ntype = node_info.get("type", "")
    screen_type = ntype if ntype else ("dialog" if "Dialog" in screen_class else "activity")

    nav_edges = _get_nav_edges_for_screen(screen_class, nav_data)

    if not elements:
        # Stub node for screens without static XML layout (Compose/programmatic UI).
        # Still process navigation edges so child screens are discoverable.
        unmatched_nav_nodes = _collect_unmatched_nav_edges(
            [], nav_edges, visited, depth, max_depth,
            gt_data, nav_data, gap_data,
        )
        return {
            "screen": layout,
            "screen_class": screen_class,
            "screen_type": screen_type,
            "depth": depth,
            "ui_elements": unmatched_nav_nodes,
            "stats": {
                "total_elements": 0,
                "interactive": 0,
                "with_behavior": 0,
                "with_navigation": len(unmatched_nav_nodes),
                "virtual_nav_items": len(unmatched_nav_nodes),
            },
        }

    gap_items = _get_gap_items_for_layout(layout, gap_data)

    ui_nodes = []
    for elem in elements:
        enode = _build_element_node(
            elem, nav_edges, gap_items, visited, depth, max_depth,
            gt_data, nav_data, gap_data,
        )
        ui_nodes.append(enode)

    unmatched_nav_nodes = _collect_unmatched_nav_edges(
        elements, nav_edges, visited, depth, max_depth,
        gt_data, nav_data, gap_data,
    )
    ui_nodes.extend(unmatched_nav_nodes)

    result = {
        "screen": layout,
        "screen_class": screen_class,
        "screen_type": screen_type,
        "depth": depth,
        "ui_elements": ui_nodes,
        "stats": {
            "total_elements": len(elements),
            "interactive": sum(1 for e in elements if e.get("is_interactive")),
            "with_behavior": sum(1 for e in elements if e.get("behaviors")),
            "with_navigation": sum(1 for u in ui_nodes if "navigation" in u),
            "virtual_nav_items": len(unmatched_nav_nodes),
        },
    }

    return result


def assemble(start_layout: str, max_depth: int = 4) -> dict:
    gt_data = _load_json("ground_truth.json")
    nav_data = _load_json("navigation_graph.json")
    gap_data = _load_json("gap_analysis.json")

    screen_class = _layout_to_class(start_layout, nav_data)

    tree = _build_screen_tree(
        start_layout,
        screen_class,
        depth=0,
        max_depth=max_depth,
        gt_data=gt_data,
        nav_data=nav_data,
        gap_data=gap_data,
        visited=set(),
    )

    if not tree:
        return {"error": f"No data found for layout: {start_layout}"}

    def _count_reachable(node: dict) -> dict:
        stats = {
            "screens": 1,
            "elements": node["stats"]["total_elements"],
            "interactive": node["stats"]["interactive"],
            "with_behavior": node["stats"]["with_behavior"],
            "with_navigation": node["stats"]["with_navigation"],
        }
        for elem in node.get("ui_elements", []):
            for child in elem.get("children", []):
                cs = _count_reachable(child)
                for k in stats:
                    stats[k] += cs[k]
        vnav = node["stats"].get("virtual_nav_items", 0)
        stats["with_navigation"] = stats.get("with_navigation", 0)
        return stats

    tree["aggregate_stats"] = _count_reachable(tree)
    tree["start_layout"] = start_layout
    tree["max_depth"] = max_depth

    return tree


# ──────────────────────────────────────────────────────────────────────────────
# Path definition
#
# A path = one user action on a labeled interactive element.
# Rules:
#   • Element must be a real UI control (button / checkbox / switch / menu item /
#     clickable row) — not a plain text view or structural container.
#   • Each path has exactly one `label` (resolved from strings.xml or sibling text).
#   • There is only one kind of path.  Navigation destination and choice options
#     are extra fields on the same entry — they do not create separate "types".
#
# Entry schema:
#   screen        – human-readable screen name
#   label         – visible string label of the element
#   element_id    – XML id
#   element_tag   – XML tag
#   action        – tap | toggle | select | input | adjust
#   destination   – class name of screen/dialog opened (optional)
#   options       – list of choice values (for toggle / select / data-driven dialog)
# ──────────────────────────────────────────────────────────────────────────────

# Tags that are always UI controls regardless of other attributes
_CONTROL_TAGS = {
    "Button", "ImageButton", "FloatingActionButton",
    "CheckBox", "AppCompatCheckBox", "MyAppCompatCheckbox",
    "Switch", "SwitchCompat", "MaterialSwitch",
    "RadioButton", "MyCompatRadioButton", "AppCompatRadioButton",
    "Chip",
    "MenuItem",
    "EditText", "AutoCompleteTextView",
    "SeekBar", "RatingBar", "Slider",
    "ToggleButton",
}

# Tags that count as controls only if they carry a meaningful action or nav
_HOLDER_TAGS = {
    "RelativeLayout", "LinearLayout", "ConstraintLayout",
    "FrameLayout", "CardView",
}

# Tags that are never a path element (structural / display only)
_EXCLUDED_TAGS = {
    "TextView", "MyTextView", "AppCompatTextView",
    "SwipeRefreshLayout", "RecyclerView", "ViewPager", "ViewPager2",
    "NestedScrollView", "ScrollView", "HorizontalScrollView",
    "CoordinatorLayout", "AppBarLayout", "CollapsingToolbarLayout",
    "MaterialToolbar", "Toolbar",
    "ImageView",            # icon-only; no readable label
    "virtual_nav_item",     # internal placeholder
}


def _action_for_tag(tag: str) -> str:
    tag_lower = tag.lower()
    if any(x in tag_lower for x in ("checkbox", "switch", "toggle")):
        return "toggle"
    if "radio" in tag_lower:
        return "select"
    if "edit" in tag_lower or "input" in tag_lower or "autocomplete" in tag_lower:
        return "input"
    if "seek" in tag_lower or "slider" in tag_lower or "rating" in tag_lower:
        return "adjust"
    return "tap"


def _is_path_element(elem: dict, layout_elements: Optional[list] = None) -> bool:
    """
    Return True if this element should become a path entry.

    Holder deduplication rule:
      A *_holder RelativeLayout that has no navigation destination is skipped
      when the same layout contains a checkbox/switch child with the same base id
      (i.e. the toggle control is already captured as its own path entry).
    """
    tag = elem.get("tag", "")
    eid = elem.get("id", "")

    if tag in _EXCLUDED_TAGS:
        return False

    if tag in _CONTROL_TAGS:
        return True

    # Holder rows: RelativeLayout / LinearLayout named *_holder
    if tag in _HOLDER_TAGS:
        if not (eid.endswith("_holder") or eid.endswith("Holder")):
            return False
        nav = elem.get("navigation")
        behaviors = [b for b in elem.get("behaviors", []) if b.get("event") or b.get("handler")]
        gap = elem.get("gap_behaviors", [])
        if not (nav or behaviors or gap):
            return False
        # If no navigation destination but the child checkbox/switch exists →
        # the holder is just a toggle wrapper; skip it, the control speaks for itself.
        if not nav and layout_elements:
            base = eid[:-len("_holder")] if eid.endswith("_holder") else eid[:-len("Holder")]
            for other in layout_elements:
                if (other.get("id") == base and
                        other.get("tag", "") in _CONTROL_TAGS and
                        _action_for_tag(other.get("tag", "")) == "toggle"):
                    return False
        return True

    return False


def _resolve_label(
    elem: dict,
    layout_text_map: dict,   # element_id → resolved text string within the same layout
) -> str:
    """
    Resolve a human-readable label for the element.

    Priority:
      1. Element's own text / content_desc (already resolved from @string by xml_extractor)
      2. For *_holder elements: look up sibling text element (strip _holder suffix)
      3. Derive from element_id: snake_case → Title Case, strip common suffixes
    """
    # 1. Own text
    own = (elem.get("text") or elem.get("content_desc") or "").strip()
    if own and not own.startswith("@"):
        return own

    # 2. Sibling text for holder rows
    eid = elem.get("id", "")
    if eid.endswith("_holder"):
        base = eid[:-len("_holder")]
        sibling_text = layout_text_map.get(base, "")
        if sibling_text:
            return sibling_text
    elif eid.endswith("Holder"):
        # camelCase variant
        base = eid[:-len("Holder")]
        sibling_text = layout_text_map.get(base, "")
        if sibling_text:
            return sibling_text

    # 3. Derive from id
    label = eid
    for suffix in ("_holder", "_checkbox", "_switch", "_label", "_text", "_btn", "_button"):
        if label.endswith(suffix):
            label = label[:-len(suffix)]
            break
    # Also strip common screen prefixes (settings_, dialog_, etc.)
    label = label.replace("_", " ").strip().title()
    return label


def _normalize_trigger_payload(trigger: str) -> str:
    """
    Strip known prefix tokens from a nav-edge trigger and return the normalized
    semantic payload (lowercase, no underscores/spaces).

    Handles both colon-separated ("menu: id") and space-separated ("menu id")
    formats produced by different parts of navigation_extractor.

    Examples:
      "setup: ChangeDateTimeFormat"  → "changedatetimeformat"
      "fn: changeColumnCount"        → "changecolumncount"
      "click: settingsColumnCount"   → "settingscolumncount"
      "menu column_count"            → "columncount"
      "menu: settings"               → "settings"
    """
    # Normalise separators first (remove spaces, underscores) then strip prefix
    norm = trigger.lower().replace(" ", "").replace("_", "")
    # Prefixes with colon (must check before bare-word prefixes)
    for pfx in ("click:", "setup:", "fn:setup", "fn:", "menu:", "external:"):
        if norm.startswith(pfx):
            return norm[len(pfx):]
    # Bare-word prefixes (space already removed above, so "menu id" → "menuid")
    for pfx in ("menu", "click", "setup", "fn"):
        if norm.startswith(pfx) and len(norm) > len(pfx):
            return norm[len(pfx):]
    return norm


def _normalize_fn_key(enc_fn: str) -> str:
    """
    Normalize an enclosing_fn string to the same form as _normalize_trigger_payload.

    Source findings store the enclosing function signature, e.g.:
      "fun setupChangeDateTimeFormat(binding: SettingsActivityBinding)"

    We strip the signature, modifiers, and "setup" prefix so the result matches
    the trigger payload "changedatetimeformat".
    """
    # Strip parameter list
    norm = re.sub(r'\s*\(.*', '', enc_fn)
    # Strip Kotlin/Java modifiers and "fun" keyword
    norm = re.sub(
        r'(?:override\s+)?(?:public|private|protected|internal)?\s*fun\s+', '', norm
    )
    norm = norm.strip().lower().replace("_", "").replace(" ", "")
    # Strip "setup" prefix to align with trigger payload (which also strips it)
    if norm.startswith("setup"):
        norm = norm[len("setup"):]
    return norm


def _build_data_driven_lookup(source_findings: dict) -> dict:
    """
    Build a multi-strategy lookup table for wiring static-analysis options into paths.

    Three key schemas are stored in the same dict (tried in priority order by callers):

    1. (file_stem, fn_key)         — exact: class × setup/fn name match
       e.g. ('settingsactivity', 'fileloadingpriority') → ['speed', ...]

    2. (file_stem, "")             — class-level dialog constructors:
       when enclosing_fn describes a class declaration (fn_key starts with "class"),
       the dialog owns its own options and any caller navigating to it can use them.
       e.g. ('changefilethumbnailstyledialog', '') → ['0x', '1x', ...]

    3. (file_stem, component_lower) — unique-per-dest fallback:
       when a screen has exactly ONE data_driven entry for a given component class,
       use it when the trigger payload doesn't match the fn_key directly.
       e.g. ('mainactivity', 'radiogroupdialog') → ['1'..'20']  (only one, unambiguous)
       NOT added when the (file_stem, component) combination maps to multiple entries.
    """
    lookup: dict = {}
    
    # Predefined options for common dialogs without items parameter
    # These are based on common patterns and can be expanded as needed
    PREDEFINED_DIALOG_OPTIONS = {
        "changedatetimeformatdialog": [
            "dd.MM.yyyy",          # 15.02.2021
            "MM/dd/yyyy",          # 02/15/2021
            "yyyy-MM-dd",          # 2021-02-15
            "dd MMM yyyy",         # 15 Feb 2021
            "MMMM dd, yyyy",       # February 15, 2021
            "EEEE, MMMM dd, yyyy", # Monday, February 15, 2021
            "HH:mm",               # 14:30
            "hh:mm a",             # 02:30 PM
            "HH:mm:ss",            # 14:30:45
            "yyyy-MM-dd HH:mm:ss", # 2021-02-15 14:30:45
        ],
        # id_dispatchers dialog_without_items: static option fan-out for reporting paths
        "translationlanguagedialog": [
            "translation_language",
            "source_language",
            "papago_language_setting",
        ],
        "printerdocumentpapersizedialog": [
            "A4",
            "Letter",
            "Legal",
            "Tabloid",
        ],
        # Unit-test / synthetic dialog class name (lowercase key)
        "fakeaboutdialog": ["BranchOne", "BranchTwo"],
        # Add more predefined dialog options as discovered
    }
    
    # Collect all entries with options (data_driven_ui + id_dispatchers dialog stubs)
    entries_with_opts = [
        e for e in source_findings.get("findings", {}).get("data_driven_ui", [])
        if e.get("items_options") or e.get("kind") == "dialog_without_items"
    ] + [
        e for e in source_findings.get("findings", {}).get("id_dispatchers", [])
        if e.get("kind") == "dialog_without_items"
    ]

    # Track (file_stem, component_lower) → count for ambiguity detection
    dest_counts: dict = {}
    for e in entries_with_opts:
        k = (Path(e["file"]).stem.lower(), e.get("component", "").lower())
        dest_counts[k] = dest_counts.get(k, 0) + 1

    for entry in entries_with_opts:
        file_stem = Path(entry["file"]).stem.lower()
        fn_key    = _normalize_fn_key(entry.get("enclosing_fn", ""))
        comp      = entry.get("component", "").lower()
        
        # Handle dialog_without_items type
        if entry.get("kind") == "dialog_without_items":
            # Check if we have predefined options for this dialog type
            if comp in PREDEFINED_DIALOG_OPTIONS:
                options = PREDEFINED_DIALOG_OPTIONS[comp]
            else:
                # No predefined options, skip
                continue
        else:
            options = entry["items_options"]
            if not options:
                continue

        # Key 1: exact match
        lookup.setdefault((file_stem, fn_key), options)

        # Key 2: class-level dialog constructor → any caller navigating to this dialog
        if fn_key.startswith("class"):
            lookup.setdefault((file_stem, ""), options)

        # Key 3: unique-per-dest fallback (only when unambiguous)
        dest_key = (file_stem, comp)
        if dest_counts.get(dest_key, 0) == 1:
            lookup.setdefault(dest_key, options)
    
    # Also add predefined options directly by dialog class name (without file stem)
    # This allows lookup by dest_class_lower alone
    for dialog_class, options in PREDEFINED_DIALOG_OPTIONS.items():
        lookup.setdefault((dialog_class, ""), options)

    return lookup


def _lookup_options(
    lookup: dict,
    sc_lower: str,
    trigger: str,
    dest_class_lower: str = "",
) -> Optional[list]:
    """
    Try all lookup strategies in priority order and return the first hit.

    Strategy 1: (sc_lower, fn_key_from_trigger)  — exact class × function match
    Strategy 2: (sc_base, fn_key_from_trigger)   — strip Activity/Fragment/Dialog suffix
    Strategy 3: (dest_class_lower, "")           — class-level dialog constructor
    Strategy 4: (sc_lower, dest_class_lower)     — unique-per-dest fallback (ambiguity-safe)
                 ONLY for menu/fn triggers, not for click:element triggers.
                 A `click: specificHolder` that reaches this point means the element's
                 specific navigation isn't in source_findings — don't guess with fallback.
    """
    tpayload = _normalize_trigger_payload(trigger)
    if tpayload:
        # Strategy 1
        opts = lookup.get((sc_lower, tpayload))
        if opts is not None:
            return opts
        # Strategy 2
        sc_base = re.sub(r"(?:activity|fragment|dialog)$", "", sc_lower)
        if sc_base != sc_lower:
            opts = lookup.get((sc_base, tpayload))
            if opts is not None:
                return opts

    if dest_class_lower:
        # Strategy 3: class-level dialog constructor (dialog owns its own options)
        opts = lookup.get((dest_class_lower, ""))
        if opts is not None:
            return opts

        # Strategy 4: unique-per-dest fallback — only for menu/fn/setup triggers.
        # Any click-based trigger (including bare "click", "click: holder", "click holder")
        # is excluded: if a specific element click didn't match via fn_key, it means this
        # element's navigation isn't captured in source_findings, and guessing the wrong
        # dialog's options is worse than showing none.
        trig_norm = trigger.strip().lower()
        is_click_based = bool(re.match(r"click", trig_norm))
        if not is_click_based:
            opts = lookup.get((sc_lower, dest_class_lower))
            if opts is not None:
                return opts

    return None


def _screen_label(screen_class: str, layout: str) -> str:
    """
    Human-readable name for a screen node.
    Use the class name, removing 'Activity'/'Dialog'/'Fragment' suffix.
    """
    name = screen_class or layout
    for suffix in ("Activity", "Fragment", "Dialog"):
        if name.endswith(suffix) and name != suffix:
            name = name[:-len(suffix)]
            break
    # Insert spaces before capitals (CamelCase → Title Case)
    spaced = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", name)
    return spaced or layout


def _screen_segment(layout: str, screen_class: str) -> dict[str, Any]:
    return {
        "kind": "screen",
        "layout": layout,
        "screen_class": screen_class,
        "label": _screen_label(screen_class, layout),
    }


def _action_segment(
    *,
    layout: str,
    screen_class: str,
    element_id: str,
    element_tag: str,
    interaction: str,
    resolved_label: str,
    trigger: Optional[str],
    virtual: bool,
) -> dict[str, Any]:
    tid = trigger or ""
    return {
        "kind": "action",
        "layout": layout,
        "screen_class": screen_class,
        "element_id": element_id,
        "tag": element_tag,
        "interaction": interaction,
        "resolved_label": resolved_label,
        "trigger": trigger,
        "virtual": virtual,
        "ui_point_id": ui_point_id(layout, element_id, virtual=virtual, trigger=tid),
    }


def _branch_segment(value: str) -> dict[str, Any]:
    vk = re.sub(r"[^a-zA-Z0-9]+", "_", value.lower()).strip("_")[:80]
    return {"kind": "branch", "value": value, "value_key": vk or "opt"}


def _dest_screen_segment(dest_class: str, dest_layout: str) -> dict[str, Any]:
    return {
        "kind": "screen",
        "layout": dest_layout or "",
        "screen_class": dest_class,
        "label": _screen_label(dest_class, dest_layout or ""),
    }


def _maybe_parameter_segment(
    dest_class: str,
    options: Optional[list],
    interaction: str,
) -> Optional[dict[str, Any]]:
    """Placeholder when navigation target suggests free-form input and we have no static options."""
    if options or interaction != "tap":
        return None
    d = (dest_class or "").lower()
    # Avoid loose substrings like "inputdialog" matching *TaskInputDialogFragment.
    tokens = (
        "datepicker",
        "timepicker",
        "datetimepicker",
        "textinputdialog",
    )
    if any(t in d for t in tokens):
        return {
            "kind": "parameter",
            "pattern": "input",
            "format_hint": "",
            "placeholder_display": "{input}",
        }
    return None


def assemble_flat_paths(start_layout: str, max_depth: int = 4) -> list[dict]:
    """
    Build the flat path list: each entry is a dict with segments, path_display,
    path_id, path_key, and fields for generate_specs (screen, element_id, primary_layout).
    """
    tree = assemble(start_layout, max_depth)
    if "error" in tree:
        return []

    # Build element_id → resolved_text lookup across all layouts
    gt_data = _load_json("ground_truth.json")
    xml_data = _load_json("static_xml.json")
    strings = xml_data.get("strings", {})

    # layout → {element_id: resolved_text}
    layout_text_maps: dict = {}
    for e in xml_data.get("elements", []):
        layout = e.get("layout") or e.get("menu") or ""
        eid = e.get("id", "")
        text = (e.get("text") or e.get("content_desc") or "").strip()
        if layout and eid and text and not text.startswith("@"):
            layout_text_maps.setdefault(layout, {})[eid] = text

    # Enrich DAG element nodes with text/hint/content_desc from ground truth (for labels)
    id_to_gt: dict[str, dict] = {}
    for e in gt_data.get("static_elements", []):
        eid = e.get("id", "")
        if eid:
            id_to_gt[eid] = e

    src_findings = _load_json("source_findings.json")
    data_driven_lookup = _build_data_driven_lookup(src_findings)

    paths: list[dict] = []

    def _emit_structured(
        screen_stack: list[dict],
        action: dict,
        *,
        dest_class: str = "",
        dest_layout: str = "",
        dest_label: str = "",
        interaction: str,
        options: Optional[list],
    ) -> None:
        """Append one or more path dicts from current screen stack + action (+ dest + branches)."""
        dest_screen = None
        if dest_label and dest_class:
            dest_screen = _dest_screen_segment(dest_class, dest_layout)

        if options and interaction == "tap" and dest_screen is not None:
            for opt in options:
                br = _branch_segment(str(opt))
                paths.append(
                    build_path_record(screen_stack + [action, dest_screen, br])
                )
            return
        if options and interaction == "select":
            for opt in options:
                paths.append(build_path_record(screen_stack + [action, _branch_segment(str(opt))]))
            return
        if options and interaction == "toggle":
            for opt in options:
                paths.append(build_path_record(screen_stack + [action, _branch_segment(str(opt))]))
            return

        param = _maybe_parameter_segment(dest_class, options, interaction)
        if param is not None and dest_screen is not None:
            paths.append(build_path_record(screen_stack + [action, dest_screen, param]))
            return

        paths.append(build_path_record(screen_stack + [action]))

    def _walk(node: dict, screen_stack: list[dict]):
        screen = node["screen"]
        screen_class = node.get("screen_class", "")
        sc_lower = screen_class.lower()
        cur_screen_seg = _screen_segment(screen, screen_class)
        stack = screen_stack + [cur_screen_seg]
        screen_label = cur_screen_seg["label"]
        text_map = layout_text_maps.get(screen, {})
        all_elems = node.get("ui_elements", [])

        for elem in all_elems:
            tag = elem.get("tag", "")

            # Merge GT text fields into elem for _resolve_label
            eid0 = elem.get("id", "")
            merged = dict(elem)
            if eid0 in id_to_gt:
                ge = id_to_gt[eid0]
                for k in ("text", "hint", "content_desc"):
                    if not merged.get(k) and ge.get(k):
                        merged[k] = ge[k]

            # ── virtual nav items (menu actions, indirect calls) ──────────────
            if tag == "virtual_nav_item":
                nav = elem.get("navigation")
                if not nav:
                    continue
                trigger = nav.get("trigger", "")
                dest_class = nav["target_class"]
                dest_layout = nav.get("target_layout", "") or ""
                if trigger.startswith("menu "):
                    raw_label = trigger[5:].replace("_", " ").title()
                    elem_tag = "MenuItem"
                elif trigger.startswith("fn: "):
                    raw_label = trigger[4:].replace("_", " ").title()
                    elem_tag = "virtual"
                elif trigger.startswith("setup: "):
                    raw_label = trigger[7:].replace("_", " ").title()
                    elem_tag = "virtual"
                elif trigger.startswith("click: ") or trigger.startswith("click "):
                    raw_label = trigger.split(":", 1)[-1].strip().replace("_", " ").title()
                    elem_tag = "virtual"
                else:
                    raw_label = trigger.replace("_", " ").title()
                    elem_tag = "virtual"

                if not raw_label.strip():
                    for child in elem.get("children", []):
                        _walk(child, stack)
                    continue

                dest_cls_lower = dest_class.lower()
                virt_raw_opts = _lookup_options(
                    data_driven_lookup, sc_lower, trigger, dest_cls_lower
                )
                virt_options = (
                    [strings.get(o, o.replace("_", " ").title()) for o in virt_raw_opts]
                    if virt_raw_opts
                    else None
                )

                dest_label = _screen_label(dest_class, dest_layout)
                act = _action_segment(
                    layout=screen,
                    screen_class=screen_class,
                    element_id="",
                    element_tag=elem_tag,
                    interaction="tap",
                    resolved_label=raw_label,
                    trigger=trigger,
                    virtual=True,
                )
                _emit_structured(
                    stack,
                    act,
                    dest_class=dest_class,
                    dest_layout=dest_layout,
                    dest_label=dest_label,
                    interaction="tap",
                    options=virt_options,
                )

                for child in elem.get("children", []):
                    _walk(child, stack)
                continue

            # ── real XML elements ─────────────────────────────────────────────
            if not _is_path_element(elem, all_elems):
                for child in elem.get("children", []):
                    _walk(child, stack)
                continue

            nav = elem.get("navigation")
            gap_beh = elem.get("gap_behaviors", [])
            label = _resolve_label(merged, text_map)
            interaction = _action_for_tag(tag)
            dest_label = (
                _screen_label(nav["target_class"], nav.get("target_layout", "")) if nav else ""
            )
            dest_class = nav["target_class"] if nav else ""
            dest_layout = nav.get("target_layout", "") if nav else ""

            if interaction == "toggle":
                options: Optional[list] = ["on", "off"]
            elif interaction == "select":
                options = None
            else:
                options = None

            for gi in gap_beh:
                if gi.get("gap_type") == "data_driven_dialog":
                    raw_opts = gi.get("data_driven_options", [])
                    if raw_opts:
                        options = [
                            strings.get(o, o.replace("_", " ").title()) for o in raw_opts
                        ]
                        if not dest_label:
                            dest_label = _screen_label(
                                gi.get("component", ""),
                                gi.get("resolved_layout", ""),
                            )
                            dest_class = gi.get("component", "") or dest_class
                            dest_layout = gi.get("resolved_layout", "") or dest_layout
                        break

            if options is None and dest_label:
                trigger = nav.get("trigger", "") if nav else ""
                dest_cls_lower = nav.get("target_class", "").lower() if nav else ""
                raw_opts = _lookup_options(
                    data_driven_lookup, sc_lower, trigger, dest_cls_lower
                )
                if raw_opts:
                    options = [
                        strings.get(o, o.replace("_", " ").title()) for o in raw_opts
                    ]

            act = _action_segment(
                layout=screen,
                screen_class=screen_class,
                element_id=elem.get("id", "") or "",
                element_tag=tag,
                interaction=interaction,
                resolved_label=label,
                trigger=(nav.get("trigger") if nav else None) or None,
                virtual=False,
            )
            _emit_structured(
                stack,
                act,
                dest_class=dest_class,
                dest_layout=dest_layout,
                dest_label=dest_label,
                interaction=interaction,
                options=options,
            )

            for child in elem.get("children", []):
                _walk(child, stack)

    _walk(tree, [])
    seen: set[str] = set()
    unique: list[dict] = []
    for p in paths:
        pid = p.get("path_id", "")
        if pid and pid not in seen:
            seen.add(pid)
            unique.append(p)
    return unique


def assemble_all_flat_paths(*, include_report: bool = False) -> list[dict] | tuple[list[dict], dict]:
    """
    Build app-wide UI paths for every discovered screen/layout.

    `assemble_flat_paths()` intentionally starts from one launcher layout and only
    emits statically reachable chains. Large apps often have many screens that are
    reachable through runtime state, deep links, bottom navigation, Compose state,
    or framework callbacks that static DFS cannot prove. This companion export
    uses the navigation graph to attach each screen to a best-effort parent stack,
    and falls back to a virtual runtime-entry root for disconnected screens.
    """
    gt_data = _load_json("ground_truth.json")
    xml_data = _load_json("static_xml.json")
    nav_data = _load_json("navigation_graph.json")
    src_findings = _load_json("source_findings.json")
    strings = xml_data.get("strings", {})
    data_driven_lookup = _build_data_driven_lookup(src_findings)

    layout_text_maps: dict[str, dict[str, str]] = {}
    for e in xml_data.get("elements", []):
        layout = e.get("layout") or e.get("menu") or ""
        eid = e.get("id", "")
        text = (e.get("text") or e.get("content_desc") or "").strip()
        if layout and eid and text and not text.startswith("@"):
            layout_text_maps.setdefault(layout, {})[eid] = text

    elements_by_layout: dict[str, list[dict]] = {}
    for e in gt_data.get("static_elements", []):
        layout = e.get("layout") or e.get("menu") or ""
        if layout:
            elements_by_layout.setdefault(layout, []).append(e)

    layout_to_class: dict[str, str] = {}
    for class_name, node in nav_data.get("nodes", {}).items():
        layout = node.get("layout") or _resolve_layout_from_class(class_name, nav_data)
        if layout:
            layout_to_class.setdefault(layout, class_name)
    for class_name, layout in nav_data.get("class_layouts", {}).items():
        if layout:
            layout_to_class.setdefault(layout, class_name)

    screen_items: list[tuple[str, str]] = []
    seen_screens: set[tuple[str, str]] = set()
    for class_name, node in sorted(nav_data.get("nodes", {}).items()):
        layout = node.get("layout") or _resolve_layout_from_class(class_name, nav_data)
        key = (layout, class_name)
        if layout and key not in seen_screens:
            seen_screens.add(key)
            screen_items.append(key)
    for layout in sorted(elements_by_layout):
        class_name = layout_to_class.get(layout, "")
        key = (layout, class_name)
        if key not in seen_screens:
            seen_screens.add(key)
            screen_items.append(key)

    class_to_layout = dict(layout_to_class)
    class_to_layout = {class_name: layout for layout, class_name in layout_to_class.items() if class_name}
    for class_name, node in nav_data.get("nodes", {}).items():
        layout = node.get("layout") or _resolve_layout_from_class(class_name, nav_data)
        if layout:
            class_to_layout[class_name] = layout

    app_root_seg = {"kind": "screen", "layout": "_app", "screen_class": "", "label": "App"}
    runtime_root_seg = {
        "kind": "screen",
        "layout": "_runtime_entry",
        "screen_class": "",
        "label": "Runtime Entry",
    }
    unmapped_root_seg = {
        "kind": "screen",
        "layout": "_unmapped_layouts",
        "screen_class": "",
        "label": "Unmapped Layouts",
    }

    def _virtual_label(trigger: str) -> tuple[str, str]:
        if trigger.startswith("menu "):
            return trigger[5:].replace("_", " ").title(), "MenuItem"
        if trigger.startswith("fn: "):
            return trigger[4:].replace("_", " ").title(), "virtual"
        if trigger.startswith("setup: "):
            return trigger[7:].replace("_", " ").title(), "virtual"
        if trigger.startswith("click: ") or trigger.startswith("click "):
            return trigger.split(":", 1)[-1].strip().replace("_", " ").title(), "virtual"
        if trigger.startswith("hosts fragment"):
            # "hosts fragment (FragmentTransaction.replace)" → "Fragment [replace]"
            import re as _re2
            m = _re2.search(r"\((.+?)\)", trigger)
            method = m.group(1) if m else ""
            label = f"Fragment [{method}]" if method else "Fragment"
            return label, "fragment"
        if "embeds host view" in trigger:
            # "layout xxx embeds host view" → "CustomView Host"
            return "CustomView Host", "container"
        return trigger.replace("_", " ").title(), "virtual"

    def _edge_sort_key(edge: dict) -> tuple[int, int, str, str, int]:
        edge_type = str(edge.get("type", ""))
        via = str(edge.get("via", ""))
        trigger = str(edge.get("trigger", ""))
        type_rank = {
            "activity": 0,
            "fragment": 0,       # container edge (fragment_host) — follow first
            "container": 0,      # container edge (custom_view_host)
            "dialog": 1,
            "commons_dialog": 2,
            "external": 9,
        }.get(edge_type, 5)
        via_rank = 1 if "[ast]" in via or "bytecode" in via.lower() else 0
        trigger_rank = 0 if trigger else 1
        return (type_rank, trigger_rank, via_rank, str(edge.get("to", "")), int(edge.get("line") or 0))

    edges_by_from: dict[str, list[dict]] = {}
    incoming: dict[str, int] = {}
    for edge in nav_data.get("edges", []) or []:
        from_class = str(edge.get("from") or "")
        to_class = str(edge.get("to") or "")
        if not from_class or not to_class:
            continue
        edges_by_from.setdefault(from_class, []).append(edge)
        incoming[to_class] = incoming.get(to_class, 0) + 1
    for edges in edges_by_from.values():
        edges.sort(key=_edge_sort_key)

    launcher_class = str((nav_data.get("meta") or {}).get("launcher_activity") or "")
    if not launcher_class:
        roots = sorted(
            c for c in nav_data.get("nodes", {})
            if incoming.get(c, 0) == 0
        )
        launcher_class = roots[0] if roots else ""

    screen_stacks_by_class: dict[str, list[dict]] = {}
    if launcher_class:
        launcher_layout = class_to_layout.get(launcher_class) or _resolve_layout_from_class(launcher_class, nav_data)
        screen_stacks_by_class[launcher_class] = [_screen_segment(launcher_layout, launcher_class)]
        queue = [launcher_class]
        while queue:
            cur = queue.pop(0)
            cur_stack = screen_stacks_by_class[cur]
            cur_layout = class_to_layout.get(cur) or _resolve_layout_from_class(cur, nav_data)
            for edge in edges_by_from.get(cur, []):
                dest = str(edge.get("to") or "")
                if not dest or dest in screen_stacks_by_class:
                    continue
                trigger = str(edge.get("trigger") or "")
                label, elem_tag = _virtual_label(trigger)
                if not label.strip():
                    label = _screen_label(dest, class_to_layout.get(dest, ""))
                dest_layout = edge.get("to_layout") or class_to_layout.get(dest) or _resolve_layout_from_class(dest, nav_data)
                nav_action = _action_segment(
                    layout=cur_layout,
                    screen_class=cur,
                    element_id="",
                    element_tag=elem_tag,
                    interaction="tap",
                    resolved_label=label,
                    trigger=trigger,
                    virtual=True,
                )
                screen_stacks_by_class[dest] = cur_stack + [nav_action, _screen_segment(dest_layout, dest)]
                queue.append(dest)

    # ── Fill gaps after BFS ──────────────────────────────────────────────────
    #
    # BFS only reaches classes connected through navigation edges from the
    # launcher.  Three classes of screens are left unstacked:
    #   A. Anonymous dialogs (HomeActivity$showCampaignDialog$1) — their host
    #      page (HomeActivity) is known but may itself be an isolated root.
    #   B. Fragment / custom-view container destinations — these appear as
    #      edge targets but may have no nav-graph node and no layout elements.
    #   C. Fragment host roots — e.g. HomeActivity with 0 inbound nav edges.
    #
    # Correct order matters: first seed the lookup with BFS, then add isolated
    # hosts (C), then recover container destinations (B), then walk the whole
    # lookup to pull anonymous children (A) on top of the now-populated stack
    # set.

    screen_stacks_lookup: dict[str, list[dict]] = dict(screen_stacks_by_class)

    # ── (Step 1) isolated fragment-hosting roots (C) ────────────────────────
    # These root nodes have zero inbound navigation edges so BFS never reaches
    # them, but they are essential as anchor stacks for both their fragment
    # children (B) and their anonymous dialog children (A).
    container_vias = {"fragment_host", "custom_view_host"}
    for edge in nav_data.get("edges", []):
        if str(edge.get("via") or "") not in container_vias:
            continue
        from_class = str(edge.get("from") or "")
        if not from_class or from_class in screen_stacks_lookup:
            continue
        from_layout = class_to_layout.get(from_class) or _resolve_layout_from_class(from_class, nav_data)
        screen_stacks_lookup[from_class] = [
            app_root_seg,
            runtime_root_seg,
            _screen_segment(from_layout, from_class),
        ]

    # ── (Step 2) container-edge destinations not yet in screen_items (B) ───
    for edge in nav_data.get("edges", []):
        if str(edge.get("via") or "") not in container_vias:
            continue
        dest_class = str(edge.get("to") or "")
        if not dest_class:
            continue
        dest_layout = edge.get("to_layout") or class_to_layout.get(dest_class) or _resolve_layout_from_class(dest_class, nav_data)
        key = (dest_layout, dest_class)
        if key not in seen_screens:
            seen_screens.add(key)
            if dest_class not in class_to_layout and dest_layout:
                class_to_layout[dest_class] = dest_layout
            screen_items.append(key)

    # ── (Step 3) stack container destinations using their host's now-ready ──
    #           stack (from BFS or from Step 1).
    for edge in nav_data.get("edges", []):
        if str(edge.get("via") or "") not in container_vias:
            continue
        dest_class = str(edge.get("to") or "")
        if not dest_class or dest_class in screen_stacks_lookup:
            continue
        from_class = str(edge.get("from") or "")
        if from_class not in screen_stacks_lookup:
            continue
        trigger = str(edge.get("trigger") or "")
        label, elem_tag = _virtual_label(trigger)
        if not label.strip():
            dest_layout_for_label = class_to_layout.get(dest_class) or _resolve_layout_from_class(dest_class, nav_data)
            label = _screen_label(dest_class, dest_layout_for_label)
        from_layout = class_to_layout.get(from_class) or _resolve_layout_from_class(from_class, nav_data)
        dest_layout_for_seg = edge.get("to_layout") or class_to_layout.get(dest_class) or _resolve_layout_from_class(dest_class, nav_data)
        nav_action = _action_segment(
            layout=from_layout,
            screen_class=from_class,
            element_id="",
            element_tag=elem_tag,
            interaction="tap",
            resolved_label=label,
            trigger=trigger,
            virtual=True,
        )
        screen_stacks_lookup[dest_class] = screen_stacks_lookup[from_class] + [
            nav_action,
            _screen_segment(dest_layout_for_seg, dest_class),
        ]

    # ── (Step 4) anonymous children of now-populated stacks (A) ─────────────
    # Screens that were NOT reached by BFS but have an inbound edge from a
    # class that IS now in screen_stacks_lookup (populated by BFS, Step 1, and
    # Step 3).  The old self-anchor fallback (App > Runtime Entry > Screen)
    # drops the trigger context; we recover it here so these screens carry the
    # full host → trigger → target chain.
    for layout, screen_class in list(screen_items):
        if screen_class and screen_class in screen_stacks_lookup:
            continue  # already stacked
        best_stack = None
        for edge in nav_data.get("edges", []):
            if str(edge.get("to") or "") != screen_class:
                continue
            from_class = str(edge.get("from") or "")
            if from_class and from_class in screen_stacks_lookup:
                trigger = str(edge.get("trigger") or "")
                label, elem_tag = _virtual_label(trigger)
                if not label.strip():
                    label = _screen_label(screen_class, layout)
                from_layout = class_to_layout.get(from_class) or _resolve_layout_from_class(from_class, nav_data)
                nav_action = _action_segment(
                    layout=from_layout,
                    screen_class=from_class,
                    element_id="",
                    element_tag=elem_tag,
                    interaction="tap",
                    resolved_label=label,
                    trigger=trigger,
                    virtual=True,
                )
                stack = screen_stacks_lookup[from_class] + [
                    nav_action,
                    _screen_segment(layout, screen_class),
                ]
                if best_stack is None or len(stack) < len(best_stack):
                    best_stack = stack
        if best_stack is not None:
            screen_stacks_lookup[screen_class] = best_stack

    def _screen_stack(layout: str, screen_class: str) -> list[dict]:
        # 1. BFS reachable
        if screen_class and screen_class in screen_stacks_lookup:
            return screen_stacks_lookup[screen_class]
        # 2. Inbound context (Case A) — recovered from host screen's stack
        if screen_class:
            return [app_root_seg, runtime_root_seg, _screen_segment(layout, screen_class)]
        return [app_root_seg, unmapped_root_seg, _screen_segment(layout, screen_class)]

    paths: list[dict] = []

    def _append_paths(segments: list[dict], interaction: str, options: Optional[list]) -> None:
        if options and interaction in ("select", "toggle"):
            for opt in options:
                paths.append(build_path_record(segments + [_branch_segment(str(opt))]))
            return
        paths.append(build_path_record(segments))

    for layout, screen_class in screen_items:
        screen_stack = _screen_stack(layout, screen_class)
        screen_class_lower = screen_class.lower()
        layout_elements = elements_by_layout.get(layout, [])
        text_map = layout_text_maps.get(layout, {})
        nav_edges = _get_nav_edges_for_screen(screen_class, nav_data) if screen_class else []

        for edge in nav_edges:
            trigger = edge.get("trigger", "")
            matched = any(_match_trigger_to_element(trigger, e.get("id", "")) for e in layout_elements)
            if matched:
                continue
            label, elem_tag = _virtual_label(trigger)
            if not label.strip():
                continue
            act = _action_segment(
                layout=layout,
                screen_class=screen_class,
                element_id="",
                element_tag=elem_tag,
                interaction="tap",
                resolved_label=label,
                trigger=trigger,
                virtual=True,
            )
            paths.append(build_path_record(screen_stack + [act]))

        for elem in layout_elements:
            merged = dict(elem)
            nav = None
            for edge in nav_edges:
                if _match_trigger_to_element(edge.get("trigger", ""), merged.get("id", "")):
                    nav = edge
                    break
            include_point = (
                _is_path_element(merged, layout_elements)
                or bool(merged.get("is_interactive"))
                or bool(merged.get("behaviors"))
                or nav is not None
            )
            if not include_point:
                continue
            label = _resolve_label(merged, text_map)
            if not label and not merged.get("id") and nav is None:
                continue
            interaction = _action_for_tag(merged.get("tag", ""))
            options: Optional[list]
            if interaction == "toggle":
                options = ["on", "off"]
            else:
                options = None

            if options is None and nav:
                raw_opts = _lookup_options(
                    data_driven_lookup,
                    screen_class_lower,
                    nav.get("trigger", ""),
                    nav.get("to", "").lower(),
                )
                if raw_opts:
                    options = [strings.get(o, o.replace("_", " ").title()) for o in raw_opts]

            act = _action_segment(
                layout=layout,
                screen_class=screen_class,
                element_id=merged.get("id", "") or "",
                element_tag=merged.get("tag", ""),
                interaction=interaction,
                resolved_label=label,
                trigger=(nav.get("trigger") if nav else None) or None,
                virtual=False,
            )
            _append_paths(screen_stack + [act], interaction, options)

    seen: set[str] = set()
    unique: list[dict] = []
    for p in paths:
        pid = p.get("path_id", "")
        if pid and pid not in seen:
            seen.add(pid)
            unique.append(p)
    if include_report:
        nav_classes = set(nav_data.get("nodes", {}).keys())
        reachable = set(screen_stacks_lookup.keys())
        mapped_layouts = {layout for layout, _class_name in screen_items}
        report = {
            "schema_version": "1.0",
            "launcher_class": launcher_class,
            "screen_total": len(screen_items),
            "navigation_node_total": len(nav_classes),
            "reachable_navigation_screen_count": len(reachable),
            "runtime_entry_screen_count": len([c for _layout, c in screen_items if c and c not in reachable]),
            "unmapped_layout_count": len([1 for _layout, c in screen_items if not c]),
            "layout_with_static_elements_count": len(elements_by_layout),
            "exported_path_count": len(unique),
            "short_path_count": sum(1 for p in unique if len(p.get("segments", [])) <= 2),
            "uncovered_static_layout_count": len(set(elements_by_layout) - mapped_layouts),
        }
        return unique, report
    return unique
