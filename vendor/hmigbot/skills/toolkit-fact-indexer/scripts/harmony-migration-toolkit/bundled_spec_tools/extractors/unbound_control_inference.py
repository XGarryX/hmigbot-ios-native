from __future__ import annotations

from collections import defaultdict

_TAG_TO_EVENT_TYPE = {
    "Button": "click", "ImageButton": "click",
    "CheckBox": "value_change", "RadioButton": "value_change",
    "Switch": "value_change", "ToggleButton": "value_change",
    "EditText": "text_change", "Spinner": "select",
    "SeekBar": "value_change", "RatingBar": "value_change",
    "TabLayout": "tab_select",
    "ViewPager": "page_change", "ViewPager2": "page_change",
    "RecyclerView": "item_interaction", "ListView": "item_interaction",
    "ScrollView": "scroll", "HorizontalScrollView": "scroll",
    "NestedScrollView": "scroll",
}

_VALUE_INPUT_TAGS = frozenset({
    "CheckBox", "RadioButton", "EditText", "Spinner",
    "Switch", "ToggleButton", "SeekBar", "RatingBar",
})

_FRAMEWORK_BINDINGS = {
    "TabLayout": ("tab_select", "framework:TabLayout.setupWithViewPager"),
    "ViewPager": ("page_change", "framework:ViewPager.setAdapter"),
    "ViewPager2": ("page_change", "framework:ViewPager.setAdapter"),
    "RecyclerView": ("item_interaction", "framework:RecyclerView.setAdapter"),
    "ListView": ("item_interaction", "framework:ListView.setAdapter"),
    "ScrollView": ("scroll", "framework:scroll_container"),
    "HorizontalScrollView": ("scroll", "framework:scroll_container"),
    "NestedScrollView": ("scroll", "framework:scroll_container"),
}

_DIALOG_SCREEN_TYPES = frozenset({"dialog", "commons_dialog"})


def build_layout_contexts(nav: dict, adapter_layouts: list[dict] | None = None) -> dict[str, dict]:
    raw_contexts: dict[str, dict[str, set[str]]] = defaultdict(lambda: {
        "owner_classes": set(),
        "screen_types": set(),
        "adapter_classes": set(),
        "adapter_hosts": set(),
    })

    for class_name, layout_name in (nav.get("class_layouts") or {}).items():
        if layout_name:
            raw_contexts[layout_name]["owner_classes"].add(class_name)

    for class_name, node in (nav.get("nodes") or {}).items():
        layout_name = node.get("layout", "")
        if not layout_name:
            continue
        raw_contexts[layout_name]["owner_classes"].add(class_name)
        node_type = node.get("type", "")
        if node_type:
            raw_contexts[layout_name]["screen_types"].add(node_type)

    for adapter in adapter_layouts or []:
        layout_name = adapter.get("item_layout", "")
        if not layout_name:
            continue
        adapter_class = adapter.get("adapter_class", "")
        host_class = adapter.get("host_class", "")
        if adapter_class:
            raw_contexts[layout_name]["adapter_classes"].add(adapter_class)
        if host_class:
            raw_contexts[layout_name]["adapter_hosts"].add(host_class)

    contexts: dict[str, dict] = {}
    for layout_name, ctx in raw_contexts.items():
        owner_classes = sorted(ctx["owner_classes"])
        screen_types = sorted(ctx["screen_types"])
        adapter_classes = sorted(ctx["adapter_classes"])
        adapter_hosts = sorted(ctx["adapter_hosts"])
        is_dialog = (
            "dialog" in layout_name
            or "bubble" in layout_name
            or any(screen_type in _DIALOG_SCREEN_TYPES for screen_type in screen_types)
            or any("Dialog" in class_name or "BottomSheet" in class_name for class_name in owner_classes)
        )
        is_adapter_item = (
            layout_name.startswith("item_")
            or layout_name.startswith("editor_")
            or "adapter_item" in screen_types
            or bool(adapter_classes)
        )
        contexts[layout_name] = {
            "owner_classes": owner_classes,
            "screen_types": screen_types,
            "adapter_classes": adapter_classes,
            "adapter_hosts": adapter_hosts,
            "is_dialog": is_dialog,
            "is_adapter_item": is_adapter_item,
        }

    return contexts


def classify_unbound_control(
    tag: str,
    layout_name: str,
    layout_context: dict | None = None,
) -> str:
    ctx = layout_context or {}
    is_dialog = bool(ctx.get("is_dialog")) or "dialog" in layout_name or "bubble" in layout_name
    is_item = bool(ctx.get("is_adapter_item")) or layout_name.startswith("item_") or layout_name.startswith("editor_")

    if tag in _FRAMEWORK_BINDINGS:
        return "framework_managed"
    if is_dialog and tag in _VALUE_INPUT_TAGS:
        return "value_read_on_confirm"
    if is_dialog and tag in ("Button", "ImageButton"):
        return "dialog_action"
    if is_item:
        return "adapter_bindview"
    return "programmatic"


def _find_confirm_handler(elements: list[dict]) -> str:
    for elem in elements:
        for behavior in elem.get("behaviors", []):
            if behavior.get("event") == "click" and behavior.get("method"):
                return behavior["method"]
    return ""


def _build_inferred_binding(
    elem: dict,
    layout_name: str,
    category: str,
    confirm_handler: str,
    layout_context: dict,
) -> dict:
    tag = elem.get("tag", "")
    event_type = _TAG_TO_EVENT_TYPE.get(tag, "interaction")
    adapter_classes = layout_context.get("adapter_classes", []) or []

    binding = {
        "layout": layout_name,
        "element_id": elem.get("id", ""),
        "event_type": event_type,
        "handler_method": "",
        "effect_chain": [],
        "effect_summary": [],
        "chain_depth": 0,
        "confidence": "inferred",
        "binding_source": "unbound_inference",
        "inference_category": category,
        "claim_hints": {
            "owner_classes": layout_context.get("owner_classes", []),
            "screen_types": layout_context.get("screen_types", []),
            "adapter_classes": adapter_classes,
        },
    }

    if tag in _FRAMEWORK_BINDINGS:
        inferred_event, summary_tag = _FRAMEWORK_BINDINGS[tag]
        binding["event_type"] = inferred_event
        binding["effect_summary"] = [summary_tag]
    elif category == "value_read_on_confirm":
        binding["handler_method"] = confirm_handler
        binding["effect_summary"] = ["value_read:on_dialog_confirm"]
    elif category == "dialog_action":
        binding["event_type"] = "click"
        binding["handler_method"] = confirm_handler
        binding["effect_summary"] = ["ui_feedback:dismiss_dialog"]
    elif category == "adapter_bindview":
        binding["handler_method"] = "onBindViewHolder"
        if adapter_classes:
            binding["effect_summary"] = [
                f"adapter_bindview:{adapter_classes[0]}.onBindViewHolder"
            ]
        else:
            binding["effect_summary"] = ["adapter_bindview:onBindViewHolder"]
    else:
        binding["effect_summary"] = ["programmatic:handler_in_code"]

    return binding


def infer_unbound_event_bindings(
    static_elements: list[dict],
    layout_contexts: dict[str, dict],
) -> tuple[list[dict], dict]:
    elements_by_layout: dict[str, list[dict]] = defaultdict(list)
    for elem in static_elements:
        layout_name = elem.get("layout", "")
        if layout_name:
            elements_by_layout[layout_name].append(elem)

    inferred_bindings: list[dict] = []
    category_counts: dict[str, int] = defaultdict(int)
    total_unbound = 0

    for layout_name, elements in elements_by_layout.items():
        layout_context = layout_contexts.get(layout_name, {})
        confirm_handler = _find_confirm_handler(elements)
        for elem in elements:
            if not elem.get("is_interactive") or elem.get("behaviors"):
                continue
            total_unbound += 1
            category = classify_unbound_control(
                elem.get("tag", ""),
                layout_name,
                layout_context,
            )
            inferred_bindings.append(
                _build_inferred_binding(
                    elem,
                    layout_name,
                    category,
                    confirm_handler,
                    layout_context,
                )
            )
            category_counts[category] += 1

    covered = sum(
        count for category, count in category_counts.items()
        if category != "programmatic"
    )

    return inferred_bindings, {
        "total_unbound_interactive": total_unbound,
        "total_bindings": len(inferred_bindings),
        "covered": covered,
        "uncovered": category_counts.get("programmatic", 0),
        "by_category": dict(category_counts),
    }
