"""
navigation_extractor.py

从 Kotlin/Java 源码中提取屏幕导航图：
  - Activity → Activity 跳转 (startActivity / startActivityForResult)
  - Activity/Fragment → Dialog 弹出
  - Menu → Activity/Dialog 跳转
  - 外部 Intent 入口 (intent-filter, ACTION_*)
  - 返回关系 (finish / onBackPressed)
  - 隐式 Intent 跳转 (AndroidManifest intent-filter 解析)
  - Adapter → Host Activity 绑定 (CAB 菜单、item 点击)

输出 navigation_graph.json，结构为：
{
  "nodes": { "ScreenA": { ... }, ... },
  "edges": [
    { "from": "ScreenA", "to": "ScreenB", "trigger": "click xxx", "type": "activity|dialog|external", "via": "startActivity|Dialog()" },
    ...
  ]
}
"""

import re
import xml.etree.ElementTree as ET
from pathlib import Path
from collections import OrderedDict

try:
    from extractors import ast_index
    from extractors.ast_index import build_class_hierarchy, _resolve_android_base
except Exception:  # pragma: no cover - optional AST layer
    ast_index = None  # type: ignore[assignment]
    build_class_hierarchy = None
    _resolve_android_base = None

from extractors import android_project


# ── Commons library launcher functions ───────────────────────────────────────
# These are extension functions defined in external library code (e.g. Simple-Commons).
# They are the only hint we need from "known" knowledge — everything else is derived
# from the project's own source files dynamically.
#
# Format: function_name → destination_class_name
# Use "EXTERNAL_*" for non-Activity destinations (links, store pages, etc.)
_COMMONS_LAUNCHERS = {
    "launchSettings":               "SettingsActivity",
    "launchAbout":                  "AboutActivity",
    "launchFAQ":                    "FAQActivity",
    "launchLicense":                "LicenseActivity",
    "launchCustomizationActivity":  "CustomizationActivity",
    "startCustomizationActivity":   "CustomizationActivity",
    "launchRateUsPrompt":           "EXTERNAL_RATE",
    "launchMoreAppsFromUsIntent":   "EXTERNAL_MORE_APPS",
    "launchApp":                    "EXTERNAL_LAUNCH",
}

# Function names that should NOT be traced as indirect navigation calls.
_SKIP_FN_NAMES = {
    'this', 'super', 'dismiss', 'cancel', 'show', 'hide', 'gone', 'visible',
    'invalidate', 'notifyDataSetChanged', 'update', 'refresh', 'init',
    'true', 'false', 'null', 'Unit', 'it', 'apply', 'also', 'let', 'run',
    'with', 'toast', 'finish', 'recreate', 'invalidateOptionsMenu',
}

# ── Dynamic class→layout mapping ─────────────────────────────────────────────
# Populated by run() from scanning ViewBinding / setContentView declarations.
# No app-specific hardcoding — works for any Android project.
_INFERRED_LAYOUTS: dict = {}
_ALL_KNOWN_LAYOUTS: set = set()
# Populated by run() when the router-framework pass runs; holds
# {edges, route_table, unresolved, stats} so main.py can persist route_table.json.
_ROUTER_RESULT: dict = {}


def get_router_result() -> dict:
    """Return the last router-framework pass result (route table, unresolved, stats)."""
    return _ROUTER_RESULT


def _scan_all_layouts(project_root: str) -> set:
    """Scan all res/layout* dirs (project + deps) to get every layout name."""
    layouts = set()
    for res_dir in android_project.res_dirs(project_root):
        for layout_dir in res_dir.glob("layout*"):
            for f in layout_dir.glob("*.xml"):
                layouts.add(f.stem)
    return layouts

_BINDING_DECL_RE = re.compile(
    r'by\s+\w*[Bb]inding\w*\s*\(\s*(\w+Binding)\s*::'  # by viewBinding(XxxBinding::inflate)
    r'|(\w+Binding)\.inflate\s*\('                        # XxxBinding.inflate(
    r'|setContentView\s*\(\s*R\.layout\.(\w+)'            # setContentView(R.layout.xxx)
)


def _binding_to_layout(binding_class: str) -> str:
    """ActivityManageFoldersBinding  →  activity_manage_folders"""
    name = re.sub(r'Binding$', '', binding_class)
    return re.sub(r'(?<=[a-z])(?=[A-Z])', '_', name).lower()


def _scan_class_layouts(project_root: str | Path) -> dict:
    """Scan source files; infer class→layout from ViewBinding / setContentView.

    Fully generic — no hardcoded class names required.
    """
    result = {}
    for src_file in android_project.source_files(project_root):
        source = src_file.read_text(encoding="utf-8", errors="ignore")
        class_name = src_file.stem
        for m in _BINDING_DECL_RE.finditer(source):
            binding_class = m.group(1) or m.group(2)
            direct_layout = m.group(3)
            if direct_layout:
                result[class_name] = direct_layout
                break
            if binding_class:
                result[class_name] = _binding_to_layout(binding_class)
                break
    return result


def _extract_class_name(filepath: Path) -> str:
    return filepath.stem


def _find_layout_for_class(class_name: str) -> str:
    """Return the layout file name for a class.

    Priority:
      1. Dynamically inferred from ViewBinding/setContentView in source (most accurate)
      2. Fallback: camelCase→snake_case conversion of the class name
      3. Fuzzy: search _ALL_KNOWN_LAYOUTS for a dialog layout matching class keywords
    """
    if class_name in _INFERRED_LAYOUTS:
        return _INFERRED_LAYOUTS[class_name]
    fallback = re.sub(r'(?<=[a-z])(?=[A-Z])', '_', class_name).lower()
    if fallback in _ALL_KNOWN_LAYOUTS:
        return fallback
    # Fuzzy: for XxxDialog, try dialog_xxx pattern
    if "Dialog" in class_name:
        keywords = re.findall(r'[A-Z][a-z]+', class_name.replace("Dialog", ""))
        for layout in _ALL_KNOWN_LAYOUTS:
            if not layout.startswith("dialog_"):
                continue
            if all(kw.lower() in layout for kw in keywords):
                return layout
    return fallback


# Leaf-name suffixes that are never a navigable screen — a callback, view holder,
# list adapter, listener or observer is an implementation collaborator, not a
# destination. They must be excluded even when their (often inner) name contains
# "Dialog"/"BottomSheet" (e.g. ReorderDialogAdapter$HeaderViewHolder,
# MainActivity$AntennaPodBottomSheetCallback), which would otherwise be typed as a
# dialog screen and pollute the navigation graph and feature taxonomy.
_NON_SCREEN_SUFFIXES = ("Callback", "ViewHolder", "Holder", "Adapter", "Listener", "Observer", "Builder")


def _is_non_screen_class(class_name: str) -> bool:
    leaf = (class_name or "").rsplit("$", 1)[-1]
    return leaf.endswith(_NON_SCREEN_SUFFIXES)


def _dereference_starter(class_name: str, known_by_lower: dict[str, str]) -> str:
    """Map a generated ActivityStarter wrapper to the real screen it launches.

    The ActivityStarter annotation processor emits `XxxActivityStarter` helpers whose
    `start()`/`getIntent()` are what navigation detection sees — but the actual screen
    is `XxxActivity`. Rewrite to the real known class only when the stripped name
    resolves (case-insensitively, since the generator may re-case it, e.g.
    `OnlineFeedviewActivityStarter` → `OnlineFeedViewActivity`), so we never invent a
    destination or a fabricated `xxx_activity_starter` layout.
    """
    if class_name.endswith("Starter"):
        base = class_name[: -len("Starter")]
        canonical = known_by_lower.get(base.lower()) if base else None
        if canonical:
            return canonical
    return class_name


def _is_dialog_class(class_name: str) -> bool:
    if _is_non_screen_class(class_name):
        return False
    return bool(class_name) and class_name[0].isupper() and ("Dialog" in class_name or "BottomSheet" in class_name)


def _is_activity_class(class_name: str) -> bool:
    return "Activity" in class_name


def _extract_edges_from_file(filepath: Path, source: str) -> list[dict]:
    edges = []
    class_name = _extract_class_name(filepath)

    # --- 1. startActivity(Intent(this, XxxActivity::class.java)) ---
    for m in re.finditer(
        r'startActivity(?:ForResult)?\([^)]*?Intent\([^,]*,\s*(\w+)::class\.java',
        source
    ):
        target = m.group(1)
        line = source[:m.start()].count('\n') + 1
        trigger = _find_trigger_context(source, m.start(), class_name)
        edges.append({
            "from": class_name,
            "to": target,
            "to_layout": _find_layout_for_class(target),
            "type": "activity",
            "via": "startActivity",
            "trigger": trigger,
            "line": line,
        })

    # --- 1b. Intent(this, Xxx::class.java).apply { someFn(this) } — indirect launch ---
    for m in re.finditer(
        r'Intent\(\s*this\s*,\s*(\w+)::class\.java\)',
        source
    ):
        target = m.group(1)
        line = source[:m.start()].count('\n') + 1
        if any(e["to"] == target and abs(e["line"] - line) < 5 for e in edges):
            continue
        after = source[m.end():m.end() + 500]
        if re.search(r'startActivity|startActivityForResult', after[:500]):
            continue
        trigger = _find_trigger_context(source, m.start(), class_name)
        edges.append({
            "from": class_name,
            "to": target,
            "to_layout": _find_layout_for_class(target),
            "type": "activity",
            "via": "indirect Intent",
            "trigger": trigger,
            "line": line,
        })

    # --- 2. startActivity(Intent(this, XxxActivity::class.java).apply { ... }) ---
    for m in re.finditer(
        r'startActivity(?:ForResult)?\([^)]*?Intent\(\s*this\s*,\s*(\w+)::class',
        source
    ):
        target = m.group(1)
        if not any(e["to"] == target and e["line"] == source[:m.start()].count('\n') + 1 for e in edges):
            line = source[:m.start()].count('\n') + 1
            trigger = _find_trigger_context(source, m.start(), class_name)
            edges.append({
                "from": class_name,
                "to": target,
                "to_layout": _find_layout_for_class(target),
                "type": "activity",
                "via": "startActivity",
                "trigger": trigger,
                "line": line,
            })

    # --- 3. XxxDialog(this) or XxxDialog(activity) — dialog instantiation ---
    for m in re.finditer(
        r'(\w+(?:Dialog|DialogFragment))\s*\([^)]*?(?:this|activity|requireContext)\b',
        source
    ):
        target = m.group(1)
        if _is_dialog_class(target):
            line = source[:m.start()].count('\n') + 1
            trigger = _find_trigger_context(source, m.start(), class_name)
            to_layout = _find_layout_for_class(target)
            dtype = "dialog" if target in _INFERRED_LAYOUTS else "commons_dialog"
            edges.append({
                "from": class_name,
                "to": target,
                "to_layout": to_layout,
                "type": dtype,
                "via": "Dialog()",
                "trigger": trigger,
                "line": line,
            })

    # --- 4. startCustomizationActivity / launchMoreAppsFromUs / specific named navigations ---
    for m in re.finditer(
        r'(?:binding|findViewById)\.(\w+?)\.setOn\w*Listener|\.setOnClickListener\s*\{',
        source
    ):
        line = source[:m.start()].count('\n') + 1
        view_id = m.group(1) if m.group(1) else ""
        block = _get_click_block(source, m.end())

        # check if block contains startActivity or Dialog
        for act_m in re.finditer(r'startActivity\([^)]*?Intent\([^,]*,\s*(\w+)::class', block):
            target = act_m.group(1)
            if not any(e["to"] == target and abs(e["line"] - line) < 5 for e in edges):
                trigger = f"click {view_id}" if view_id else "click"
                edges.append({
                    "from": class_name,
                    "to": target,
                    "to_layout": _find_layout_for_class(target),
                    "type": "activity",
                    "via": "click -> startActivity",
                    "trigger": trigger,
                    "line": line,
                })

        for dlg_m in re.finditer(r'(\w+(?:Dialog|DialogFragment))\s*\(', block):
            target = dlg_m.group(1)
            if _is_dialog_class(target):
                if not any(e["to"] == target and abs(e["line"] - line) < 5 for e in edges):
                    trigger = f"click {view_id}" if view_id else "click"
                    to_layout = _find_layout_for_class(target)
                    dtype = "dialog" if target in _INFERRED_LAYOUTS else "commons_dialog"
                    edges.append({
                        "from": class_name,
                        "to": target,
                        "to_layout": to_layout,
                        "type": dtype,
                        "via": "click -> Dialog()",
                        "trigger": trigger,
                        "line": line,
                    })

        # startCustomizationActivity
        if 'startCustomizationActivity' in block:
            if not any(e["to"] == "CustomizationActivity" and abs(e["line"] - line) < 5 for e in edges):
                trigger = f"click {view_id}" if view_id else "click"
                edges.append({
                    "from": class_name,
                    "to": "CustomizationActivity",
                    "to_layout": "CustomizationActivity",
                    "type": "activity",
                    "via": "click -> startCustomizationActivity()",
                    "trigger": trigger,
                    "line": line,
                })

    # --- 5. Menu item R.id.xxx -> startActivity/Dialog ---
    # Kotlin when blocks: R.id.xxx -> someCall() (single line) or R.id.xxx -> { block }
    for m in re.finditer(r'R\.id\.(\w+)\s*->\s*', source):
        menu_id = m.group(1)
        line = source[:m.start()].count('\n') + 1
        after = source[m.end():]

        # Check if it's a block { ... } or single line expression
        stripped = after.lstrip()
        if stripped.startswith('{'):
            block = _get_click_block(source, m.end() + after.index('{'))
        else:
            # Single line: take until newline or next ->
            nl_pos = after.find('\n')
            block = after[:nl_pos] if nl_pos != -1 else after[:200]

        # Check for commons launchers
        for launch_m in re.finditer(r'(\w+)\s*\(\)', block):
            fn_call = launch_m.group(1)
            if fn_call in _COMMONS_LAUNCHERS:
                target = _COMMONS_LAUNCHERS[fn_call]
                edge_type = "activity" if "Activity" in target else "external"
                if not any(e["to"] == target and abs(e["line"] - line) < 3 for e in edges):
                    edges.append({
                        "from": class_name,
                        "to": target,
                        "to_layout": _find_layout_for_class(target) if "Activity" in target else "",
                        "type": edge_type,
                        "via": f"menu -> {fn_call}()",
                        "trigger": f"menu {menu_id}",
                        "line": line,
                    })

        # Check for startActivity
        for act_m in re.finditer(r'startActivity\([^)]*?Intent\([^,]*,\s*(\w+)::class', block):
            target = act_m.group(1)
            if not any(e["to"] == target and abs(e["line"] - line) < 3 for e in edges):
                edges.append({
                    "from": class_name,
                    "to": target,
                    "to_layout": _find_layout_for_class(target),
                    "type": "activity",
                    "via": "menu -> startActivity",
                    "trigger": f"menu {menu_id}",
                    "line": line,
                })

        # Check for dialog
        for dlg_m in re.finditer(r'(\w+(?:Dialog|DialogFragment))\s*\(', block):
            target = dlg_m.group(1)
            if _is_dialog_class(target):
                if not any(e["to"] == target and abs(e["line"] - line) < 3 for e in edges):
                    to_layout = _find_layout_for_class(target)
                    dtype = "dialog" if target in _INFERRED_LAYOUTS else "commons_dialog"
                    edges.append({
                        "from": class_name,
                        "to": target,
                        "to_layout": to_layout,
                        "type": dtype,
                        "via": "menu -> Dialog()",
                        "trigger": f"menu {menu_id}",
                        "line": line,
                    })

        # Check for indirect function calls that lead to navigation
        for fn_m in re.finditer(r'(\w+)\s*\(\)', block):
            fn_call = fn_m.group(1)
            if fn_call not in _COMMONS_LAUNCHERS and fn_call not in ('this', 'super'):
                # Look up function body in the same source
                fn_body = _find_function_body(source, fn_call)
                if fn_body:
                    for act_m in re.finditer(r'startActivity\([^)]*?Intent\([^,]*,\s*(\w+)::class', fn_body):
                        target = act_m.group(1)
                        if not any(e["to"] == target and abs(e["line"] - line) < 3 for e in edges):
                            edges.append({
                                "from": class_name,
                                "to": target,
                                "to_layout": _find_layout_for_class(target),
                                "type": "activity",
                                "via": f"menu -> {fn_call}() -> startActivity",
                                "trigger": f"menu {menu_id}",
                                "line": line,
                            })
                    for dlg_m in re.finditer(r'(\w+(?:Dialog|DialogFragment))\s*\(', fn_body):
                        target = dlg_m.group(1)
                        if _is_dialog_class(target):
                            if not any(e["to"] == target and abs(e["line"] - line) < 3 for e in edges):
                                to_layout = _find_layout_for_class(target)
                                dtype = "dialog" if target in _INFERRED_LAYOUTS else "commons_dialog"
                                edges.append({
                                    "from": class_name,
                                    "to": target,
                                    "to_layout": to_layout,
                                    "type": dtype,
                                    "via": f"menu -> {fn_call}() -> Dialog()",
                                    "trigger": f"menu {menu_id}",
                                    "line": line,
                                })

    # --- 6. Specific: launchViewVideoIntent, sendViewPagerIntent ---
    for m in re.finditer(r'(?:launchViewVideoIntent|sendViewPagerIntent)\(', source):
        line = source[:m.start()].count('\n') + 1
        target = "ViewPagerActivity"
        trigger = _find_trigger_context(source, m.start(), class_name)
        if not any(e["to"] == target and abs(e["line"] - line) < 5 for e in edges):
            edges.append({
                "from": class_name,
                "to": target,
                "to_layout": _find_layout_for_class(target),
                "type": "activity",
                "via": m.group(0).rstrip('('),
                "trigger": trigger,
                "line": line,
            })

    # --- 7. R.id.xxx holder click patterns (e.g., settings_xxx_holder.setOnClickListener) ---
    for m in re.finditer(
        r'(?:binding)\.(\w+?)\.setOnClickListener',
        source
    ):
        holder_id = m.group(1)
        line = source[:m.start()].count('\n') + 1
        block = _get_click_block(source, m.end())

        for dlg_m in re.finditer(r'(\w+(?:Dialog|DialogFragment))\s*\(', block):
            target = dlg_m.group(1)
            if _is_dialog_class(target):
                if not any(e["to"] == target and abs(e["line"] - line) < 5 for e in edges):
                    to_layout = _find_layout_for_class(target)
                    dtype = "dialog" if target in _INFERRED_LAYOUTS else "commons_dialog"
                    edges.append({
                        "from": class_name,
                        "to": target,
                        "to_layout": to_layout,
                        "type": dtype,
                        "via": f"click {holder_id} -> Dialog()",
                        "trigger": f"click {holder_id}",
                        "line": line,
                    })

        for act_m in re.finditer(r'startActivity\([^)]*?Intent\([^,]*,\s*(\w+)::class', block):
            target = act_m.group(1)
            if not any(e["to"] == target and abs(e["line"] - line) < 5 for e in edges):
                edges.append({
                    "from": class_name,
                    "to": target,
                    "to_layout": _find_layout_for_class(target),
                    "type": "activity",
                    "via": f"click {holder_id} -> startActivity",
                    "trigger": f"click {holder_id}",
                    "line": line,
                })

        # Trace indirect function calls inside the click block.
        # Pattern: binding.settingsXxxHolder.setOnClickListener { changeSomething() }
        # where changeSomething() opens a dialog or starts an activity.
        for fn_m in re.finditer(r'\b(\w+)\s*\(\s*\)', block):
            fn_call = fn_m.group(1)
            if fn_call in _SKIP_FN_NAMES:
                continue
            if fn_call in _COMMONS_LAUNCHERS:
                target = _COMMONS_LAUNCHERS[fn_call]
                edge_type = "activity" if "Activity" in target else "external"
                if not any(e["to"] == target and abs(e["line"] - line) < 5 for e in edges):
                    edges.append({
                        "from": class_name,
                        "to": target,
                        "to_layout": _find_layout_for_class(target) if "Activity" in target else "",
                        "type": edge_type,
                        "via": f"click {holder_id} -> {fn_call}()",
                        "trigger": f"click {holder_id}",
                        "line": line,
                    })
                continue
            fn_body = _find_function_body(source, fn_call)
            if not fn_body:
                continue
            # Check dialogs in fn_body
            for dlg_m2 in re.finditer(r'(\w+(?:Dialog|DialogFragment))\s*\(', fn_body):
                target = dlg_m2.group(1)
                if _is_dialog_class(target):
                    if not any(e["to"] == target and abs(e["line"] - line) < 5 for e in edges):
                        to_layout = _find_layout_for_class(target)
                        dtype = "dialog" if target in _INFERRED_LAYOUTS else "commons_dialog"
                        edges.append({
                            "from": class_name,
                            "to": target,
                            "to_layout": to_layout,
                            "type": dtype,
                            "via": f"click {holder_id} -> {fn_call}() -> Dialog()",
                            "trigger": f"click {holder_id}",
                            "line": line,
                        })
            # Check startActivity in fn_body
            for act_m2 in re.finditer(
                r'startActivity\([^)]*?Intent\([^,]*,\s*(\w+)::class', fn_body
            ):
                target = act_m2.group(1)
                if not any(e["to"] == target and abs(e["line"] - line) < 5 for e in edges):
                    edges.append({
                        "from": class_name,
                        "to": target,
                        "to_layout": _find_layout_for_class(target),
                        "type": "activity",
                        "via": f"click {holder_id} -> {fn_call}() -> startActivity",
                        "trigger": f"click {holder_id}",
                        "line": line,
                    })
            # Check commons launchers called inside fn_body
            for launch_m2 in re.finditer(r'\b(\w+)\s*\(\s*\)', fn_body):
                launch_fn = launch_m2.group(1)
                if launch_fn in _COMMONS_LAUNCHERS:
                    target = _COMMONS_LAUNCHERS[launch_fn]
                    edge_type = "activity" if "Activity" in target else "external"
                    if not any(e["to"] == target and abs(e["line"] - line) < 5 for e in edges):
                        edges.append({
                            "from": class_name,
                            "to": target,
                            "to_layout": _find_layout_for_class(target) if "Activity" in target else "",
                            "type": edge_type,
                            "via": f"click {holder_id} -> {fn_call}() -> {launch_fn}()",
                            "trigger": f"click {holder_id}",
                            "line": line,
                        })

    # --- 8. Commons library launchers: launchSettings(), launchAbout(), etc. ---
    for m in re.finditer(r'(\w+)\s*\(\)', source):
        fn_call = m.group(1)
        if fn_call in _COMMONS_LAUNCHERS:
            target = _COMMONS_LAUNCHERS[fn_call]
            line = source[:m.start()].count('\n') + 1
            trigger = _find_trigger_context(source, m.start(), class_name)
            edge_type = "activity" if "Activity" in target else "external"
            if not any(e["to"] == target and abs(e["line"] - line) < 3 for e in edges):
                edges.append({
                    "from": class_name,
                    "to": target,
                    "to_layout": _find_layout_for_class(target) if "Activity" in target else "",
                    "type": edge_type,
                    "via": fn_call + "()",
                    "trigger": trigger,
                    "line": line,
                })

    # --- 9. External intent / action entries ---
    for m in re.finditer(r'isPickImageIntent|isPickVideoIntent|isGetImageContentIntent|isGetVideoContentIntent|isGetAnyContentIntent|isSetWallpaperIntent|isExternalIntent', source):
        line = source[:m.start()].count('\n') + 1
        method_name = m.group(0)
        if not any(e.get("trigger", "").startswith("external:") and e["line"] == line for e in edges):
            edges.append({
                "from": "EXTERNAL",
                "to": class_name,
                "to_layout": _find_layout_for_class(class_name),
                "type": "external_intent",
                "via": method_name,
                "trigger": f"external: {method_name}",
                "line": line,
            })

    return edges


def _find_trigger_context(source: str, pos: int, class_name: str) -> str:
    start = max(0, pos - 500)
    context = source[start:pos]

    # Use the LAST (nearest to call site) fun declaration, not the first.
    # re.search returns the first match; iterate and keep the last.
    fn_name = ""
    for fn_match in re.finditer(
        r'(?:private|public|protected|internal)?\s*fun\s+(\w+)', context
    ):
        fn_name = fn_match.group(1)
    if fn_name:
        setup_match = re.match(r'setup(\w+)', fn_name)
        if setup_match:
            return f"setup: {setup_match.group(1)}"
        return f"fn: {fn_name}"

    # Nearest setOnClickListener receiver within the context window
    click_name = ""
    for click_match in re.finditer(r'(\w+)\.setOnClickListener', context):
        click_name = click_match.group(1)
    if click_name:
        return f"click: {click_name}"

    menu_match = re.search(r'R\.id\.(\w+)', context)
    if menu_match:
        return f"menu: {menu_match.group(1)}"

    return ""


def _get_click_block(source: str, open_pos: int, max_len: int = 2000) -> str:
    brace_pos = source.find('{', open_pos)
    if brace_pos == -1:
        return source[open_pos:open_pos + max_len]
    depth = 0
    for i, ch in enumerate(source[brace_pos:brace_pos + max_len]):
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
        if depth == 0:
            return source[brace_pos + 1:brace_pos + i]
    return source[brace_pos + 1:brace_pos + max_len]


def _find_function_body(source: str, fn_name: str, max_len: int = 3000) -> str:
    pattern = re.compile(r'(?:private|public|protected|internal)?\s*(?:override\s+)?(?:suspend\s+)?fun\s+' + re.escape(fn_name) + r'\s*\(')
    m = pattern.search(source)
    if not m:
        return ""
    after = source[m.start():]
    brace_pos = after.find('{')
    if brace_pos == -1:
        return ""
    return _get_click_block(after, brace_pos, max_len)


_HIERARCHY: dict | None = None


def _node_type(class_name: str) -> str:
    if _HIERARCHY is not None and _resolve_android_base is not None:
        t = _resolve_android_base(class_name, _HIERARCHY)
        if t in ("activity", "dialog", "fragment"):
            # Keep fragment distinct from activity: HarmonyOS maps Activity→UIAbility
            # but Fragment→@Component, so collapsing the two misdirects translation.
            # A DialogFragment/BottomSheetDialogFragment resolves to "fragment" by
            # inheritance but is *presented* as a modal — map it to "dialog"
            # (CustomDialog) to match how it should migrate, not its base class.
            if t == "fragment" and _is_dialog_class(class_name):
                return "dialog"
            return t
    if _is_dialog_class(class_name):
        return "dialog"
    return "activity"


def _build_node(class_name: str, edges_from: list[dict], edges_to: list[dict]) -> dict:
    layout = _find_layout_for_class(class_name)
    node_type = _node_type(class_name)
    return {
        "name": class_name,
        "layout": layout,
        "type": node_type,
        "navigates_to": list(OrderedDict.fromkeys(e["to"] for e in edges_from)),
        "navigated_from": list(OrderedDict.fromkeys(e["from"] for e in edges_to)),
        "edges_out": len(edges_from),
        "edges_in": len(edges_to),
    }


_ANDROID_NS = "{http://schemas.android.com/apk/res/android}"


def _parse_manifest_intents(project_root: str) -> dict:
    """Parse AndroidManifest.xml to build action → Activity mapping.

    Returns:
        {
            "android.intent.action.EDIT": ["EditActivity"],
            "android.intent.action.VIEW": ["ViewPagerActivity"],
            ...
        }
    """
    return android_project.manifest_action_map(project_root)


def get_launcher_activity_class(project_root: str) -> str:
    """Return the short Activity class name for MAIN + LAUNCHER, or \"\"."""
    return android_project.launcher_activity_class(project_root)


def _resolve_implicit_intents(
    all_edges: list[dict],
    project_root: str | Path,
    action_map: dict[str, list[str]],
) -> list[dict]:
    """Resolve implicit Intent calls (openEditor, openPathIntent, etc.) to Activity edges.

    Pattern: source code calls openEditor/openEditorIntent/launchCamera etc.
    These use ACTION_EDIT/ACTION_VIEW etc. resolved via AndroidManifest.
    """
    if not action_map:
        return []

    _IMPLICIT_FN_TO_ACTION = {
        "openEditor": "android.intent.action.EDIT",
        "openEditorIntent": "android.intent.action.EDIT",
    }

    edges = []
    for src_file in android_project.source_files(project_root):
        source = src_file.read_text(encoding="utf-8", errors="ignore")
        class_name = src_file.stem

        for fn_name, action in _IMPLICIT_FN_TO_ACTION.items():
            targets = action_map.get(action, [])
            if not targets:
                continue
            for m in re.finditer(re.escape(fn_name) + r'\s*\(', source):
                line = source[:m.start()].count('\n') + 1
                trigger = _find_trigger_context(source, m.start(), class_name)
                for target in targets:
                    if not any(
                        e["to"] == target and abs(e["line"] - line) < 3
                        for e in all_edges + edges
                    ):
                        edges.append({
                            "from": class_name,
                            "to": target,
                            "to_layout": _find_layout_for_class(target),
                            "type": "activity",
                            "via": f"{fn_name}() [implicit:{action}]",
                            "trigger": trigger or f"fn: {fn_name}",
                            "line": line,
                        })

        # Generic: any startActivityForResult / startActivity with Intent.ACTION_XXX constant
        for m in re.finditer(
            r'(?:startActivity|startActivityForResult)\s*\([^)]*?Intent\.\s*(\w+)',
            source,
        ):
            action_const = m.group(1)
            action_map_to = {
                "ACTION_EDIT": "android.intent.action.EDIT",
                "ACTION_VIEW": "android.intent.action.VIEW",
                "ACTION_PICK": "android.intent.action.PICK",
                "ACTION_SEND": "android.intent.action.SEND",
                "ACTION_GET_CONTENT": "android.intent.action.GET_CONTENT",
                "ACTION_INSERT": "android.intent.action.INSERT",
            }
            action = action_map_to.get(action_const)
            if not action:
                continue
            targets = action_map.get(action, [])
            line = source[:m.start()].count('\n') + 1
            trigger = _find_trigger_context(source, m.start(), class_name)
            for target in targets:
                if not any(
                    e["to"] == target and abs(e["line"] - line) < 3
                    for e in all_edges + edges
                ):
                    edges.append({
                        "from": class_name,
                        "to": target,
                        "to_layout": _find_layout_for_class(target),
                        "type": "activity",
                        "via": f"startActivity [implicit:{action}]",
                        "trigger": trigger,
                        "line": line,
                    })

    return edges


_ADAPTER_RE = re.compile(
    r'(\w+Adapter)\s*\(\s*(?:this|activity|requireActivity)'
)
_ADAPTER_ASSIGN_RE = re.compile(
    r'(?:binding|findViewById)\.\w+\.adapter\s*=\s*(\w+Adapter)'
)


def _resolve_adapter_bindings(
    all_edges: list[dict],
    project_root: str | Path,
) -> list[dict]:
    """Bind Adapter edges to their host Activity/Fragment class.

    Scans for XxxAdapter(this, ...) constructors and binding.adapter = XxxAdapter(...)
    assignments, then copies the Adapter's out-edges to the host class.
    """
    adapter_to_host: dict[str, list[str]] = {}

    for src_file in android_project.source_files(project_root):
        source = src_file.read_text(encoding="utf-8", errors="ignore")
        class_name = src_file.stem

        for m in _ADAPTER_RE.finditer(source):
            adapter_class = m.group(1)
            adapter_to_host.setdefault(adapter_class, []).append(class_name)

        for m in _ADAPTER_ASSIGN_RE.finditer(source):
            adapter_class = m.group(1)
            adapter_to_host.setdefault(adapter_class, []).append(class_name)

    adapter_edges = {e["from"] for e in all_edges}
    edges = []

    for adapter_class, hosts in adapter_to_host.items():
        if adapter_class not in adapter_edges:
            continue
        adapter_out = [e for e in all_edges if e["from"] == adapter_class]
        for host in set(hosts):
            for ae in adapter_out:
                trigger = ae.get("trigger", "")
                if trigger.startswith("adapter:"):
                    continue
                new_trigger = f"adapter:{adapter_class}:{trigger}" if trigger else f"adapter:{adapter_class}"
                via = f"adapter:{adapter_class}"
                line = ae["line"]
                if not any(
                    e["to"] == ae["to"]
                    and e["trigger"] == new_trigger
                    and e["from"] == host
                    for e in all_edges + edges
                ):
                    edges.append({
                        "from": host,
                        "to": ae["to"],
                        "to_layout": ae.get("to_layout", ""),
                        "type": ae.get("type", "dialog"),
                        "via": via,
                        "trigger": new_trigger,
                        "line": line,
                    })

    return edges


def run(project_root: str, dep_roots: list[str] | None = None) -> dict:
    global _INFERRED_LAYOUTS, _ALL_KNOWN_LAYOUTS

    root = Path(project_root)
    src_files = android_project.source_files(root)
    if not src_files:
        return {"nodes": {}, "edges": [], "stats": {"total_nodes": 0, "total_edges": 0}}

    _INFERRED_LAYOUTS = _scan_class_layouts(root)

    _ALL_KNOWN_LAYOUTS = _scan_all_layouts(project_root)
    for dep in (dep_roots or []):
        _ALL_KNOWN_LAYOUTS.update(_scan_all_layouts(dep))

    for dep in (dep_roots or []):
        _INFERRED_LAYOUTS.update(_scan_class_layouts(dep))

    all_edges = []
    class_files = {}

    for src_file in src_files:
        source = src_file.read_text(encoding="utf-8", errors="ignore")
        class_name = _extract_class_name(src_file)
        class_files[class_name] = src_file
        edges = _extract_edges_from_file(src_file, source)
        all_edges.extend(edges)

    if ast_index is not None:
        try:
            ast_nav = ast_index.build_project_index(
                project_root,
                layout_resolver=_find_layout_for_class,
            )
            all_edges.extend(ast_nav.navigation_edges)
            for dep in dep_roots or []:
                dep_name = Path(dep).name
                dep_nav = ast_index.build_project_index(
                    dep,
                    file_prefix=dep_name,
                    layout_resolver=_find_layout_for_class,
                )
                all_edges.extend(dep_nav.navigation_edges)
        except Exception:
            pass

    # --- L2: generic createIntent / local Intent variable (nav_pipeline) ---
    from extractors import nav_pipeline

    _rules = nav_pipeline.load_nav_rules()
    for _kt_path, source, class_name, rel in nav_pipeline.gather_kt_sources(
        project_root, dep_roots
    ):
        all_edges.extend(
            nav_pipeline.extract_l2_create_intent_edges(
                source, class_name, rel, _find_layout_for_class
            )
        )
        all_edges.extend(
            nav_pipeline.extract_l2_variable_intent_edges(
                source, class_name, rel, _find_layout_for_class
            )
        )

    # --- Router framework pass (TheRouter / ARouter / WMRouter) ---
    # String-route frameworks declare destinations via @Route(path=CONST) and dispatch
    # via TheRouter.build(CONST).navigation() (often behind wrapper funcs). None of the
    # direct-mode patterns above match them, so heavily-routed apps produce a nav graph
    # with ~0 Activity→Activity edges. This pass builds a route table and connects edges.
    global _ROUTER_RESULT
    _ROUTER_RESULT = {}
    try:
        from extractors import router_table_extractor
        _ROUTER_RESULT = router_table_extractor.run(
            project_root, dep_roots, layout_resolver=_find_layout_for_class
        )
        all_edges.extend(_ROUTER_RESULT.get("edges", []))
    except Exception:
        _ROUTER_RESULT = {}

    # --- Fix Point 2: AndroidManifest implicit Intent resolution ---
    action_map = _parse_manifest_intents(project_root)
    implicit_edges = _resolve_implicit_intents(all_edges, root, action_map)
    all_edges.extend(implicit_edges)

    # --- Fix Point 1: Adapter-Host Activity binding (regex fallback) ---
    adapter_edges = _resolve_adapter_bindings(all_edges, root)
    all_edges.extend(adapter_edges)

    # --- Bytecode analysis (if available) ---
    try:
        from extractors.bytecode_navigation import extract_edges_from_classes, find_class_dir
        bc_dir = find_class_dir(project_root)
        if bc_dir:
            bc_edges = extract_edges_from_classes(bc_dir)
            for be in bc_edges:
                key = (be["from"], be["to"], be.get("trigger", ""))
                if not any((e["from"], e["to"], e.get("trigger", "")) == key for e in all_edges):
                    all_edges.append(be)
    except Exception:
        pass

    # --- L3: per-repo overlay ---
    all_edges = nav_pipeline.merge_overlay_edges(
        all_edges,
        nav_pipeline.load_navigation_overlay(project_root, _rules),
        _find_layout_for_class,
    )

    unique_edges = nav_pipeline.dedupe_edges(all_edges)

    # --- Launcher anchor: *Handler / *Delegate → parallel edges from MAIN/LAUNCHER ---
    _launcher = get_launcher_activity_class(project_root)
    _suffixes = _rules.get("handler_anchor_suffixes")
    unique_edges = nav_pipeline.apply_launcher_anchor_edges(
        unique_edges, _launcher, _suffixes
    )
    unique_edges = nav_pipeline.dedupe_edges(unique_edges)

    # Build AST hierarchy for Activity/Dialog type resolution
    global _HIERARCHY
    if build_class_hierarchy is not None:
        try:
            _HIERARCHY = build_class_hierarchy(str(root), dep_roots)
        except Exception:
            _HIERARCHY = None
    else:
        _HIERARCHY = None

    # Build nodes
    # First, dereference generated ActivityStarter wrappers (XxxActivityStarter →
    # XxxActivity) so edges point at the real screen and we don't fabricate a
    # `xxx_activity_starter` layout. Only rewrites when the stripped name is a real
    # known class. Clear stale to_layout so it's recomputed for the true target.
    known_leaf_names: set[str] = set()
    if _HIERARCHY:
        known_leaf_names = {info.name for info in _HIERARCHY.values()}
    known_leaf_names |= {e["from"] for e in unique_edges} | {e["to"] for e in unique_edges}
    # Case-insensitive index so a re-cased generated name still resolves to the real
    # class. Skip Starter wrappers themselves so they never become their own target.
    known_by_lower = {
        n.lower(): n for n in known_leaf_names if not n.endswith("Starter")
    }
    for e in unique_edges:
        new_from = _dereference_starter(e["from"], known_by_lower)
        new_to = _dereference_starter(e["to"], known_by_lower)
        if new_from != e["from"]:
            e["from"] = new_from
        if new_to != e["to"]:
            e["to"] = new_to
            e["to_layout"] = ""  # recomputed from the real target node below

    # Drop edges that touch a non-screen collaborator (adapter/holder/callback/…).
    # Adapter→host out-edges were already re-homed to the host earlier, so by this
    # point such endpoints are spurious destinations, not real navigation.
    unique_edges = [
        e for e in unique_edges
        if not _is_non_screen_class(e["from"]) and not _is_non_screen_class(e["to"])
    ]
    all_class_names = set()
    for e in unique_edges:
        all_class_names.add(e["from"])
        all_class_names.add(e["to"])
    # Add AST-detected Activity classes as explicit nodes
    if _HIERARCHY and _resolve_android_base is not None:
        for fqn, info in _HIERARCHY.items():
            if _is_non_screen_class(info.name):
                continue
            if _resolve_android_base(fqn, _HIERARCHY) in ("activity", "dialog"):
                all_class_names.add(info.name)
                if info.name not in _INFERRED_LAYOUTS and info.base_class:
                    _INFERRED_LAYOUTS[info.name] = _find_layout_for_class(info.name)

    nodes = {}
    for cn in sorted(all_class_names):
        if cn == "EXTERNAL":
            nodes[cn] = {
                "name": "EXTERNAL",
                "layout": "",
                "type": "external",
                "navigates_to": list(OrderedDict.fromkeys(e["to"] for e in unique_edges if e["from"] == cn)),
                "navigated_from": [],
                "edges_out": sum(1 for e in unique_edges if e["from"] == cn),
                "edges_in": 0,
            }
            continue
        edges_from = [e for e in unique_edges if e["from"] == cn]
        edges_to = [e for e in unique_edges if e["to"] == cn]
        nodes[cn] = _build_node(cn, edges_from, edges_to)

    # Backfill to_layout for edges missing it (e.g. bytecode edges)
    for e in unique_edges:
        if not e.get("to_layout"):
            target = e["to"]
            if target in nodes:
                e["to_layout"] = nodes[target].get("layout", "")
            else:
                e["to_layout"] = _find_layout_for_class(target)

    # Build class_layouts from nodes (covers Compose screens without XML)
    class_layouts = dict(_INFERRED_LAYOUTS)
    for cn, node in nodes.items():
        layout = node.get("layout", "")
        if layout and cn not in class_layouts:
            class_layouts[cn] = layout

    stats = {
        "total_nodes": len(nodes),
        "total_edges": len(unique_edges),
        "activity_nodes": sum(1 for n in nodes.values() if n["type"] == "activity"),
        "fragment_nodes": sum(1 for n in nodes.values() if n["type"] == "fragment"),
        "dialog_nodes": sum(1 for n in nodes.values() if n["type"] == "dialog"),
        "external_nodes": sum(1 for n in nodes.values() if n["type"] == "external"),
        "by_type": {},
    }
    for e in unique_edges:
        t = e["type"]
        stats["by_type"][t] = stats["by_type"].get(t, 0) + 1

    return {
        "nodes": nodes,
        "edges": unique_edges,
        "stats": stats,
        "class_layouts": class_layouts,
        "meta": {
            "nav_pipeline_version": nav_pipeline.NAV_PIPELINE_VERSION,
            "nav_rules_version": str(_rules.get("nav_rules_version", "0")),
            "launcher_activity": _launcher,
            "navigation_candidates_output": "navigation_candidates.json",
        },
    }
