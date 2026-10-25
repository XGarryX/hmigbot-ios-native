"""
xml_extractor.py
静态提取所有 XML 资源中的 UI 元素（layout / menu / navigation）
输出结构化 JSON，作为 ground truth 的基础层。
"""
import json
import re
from pathlib import Path
from xml.etree import ElementTree as ET

from extractors import android_project

ANDROID_NS = "http://schemas.android.com/apk/res/android"
APP_NS     = "http://schemas.android.com/apk/res-auto"

# 固有可交互 tag — 无需额外属性即可交互
INHERENT_INTERACTIVE_TAGS = {
    "Button", "ImageButton", "FloatingActionButton",
    "CheckBox", "RadioButton", "Switch", "ToggleButton",
    "EditText", "AutoCompleteTextView", "MultiAutoCompleteTextView",
    "Spinner", "SeekBar", "RatingBar",
    "BottomNavigationView", "NavigationView",
    "TabLayout", "SearchView",
    "com.google.android.material.floatingactionbutton.FloatingActionButton",
    "com.google.android.material.chip.Chip",
}

# 条件交互 tag — 只有显式声明 clickable/onClick 时才算交互
CONDITIONAL_INTERACTIVE_TAGS = {
    "TextView", "ImageView",
    "LinearLayout", "FrameLayout", "RelativeLayout", "ConstraintLayout",
    "RecyclerView", "ViewPager2",
    "com.google.android.material.appbar.MaterialToolbar",
    "com.google.android.material.chip.ChipGroup",
    "androidx.cardview.widget.CardView",
}

INTERACTIVE_TAGS = INHERENT_INTERACTIVE_TAGS | CONDITIONAL_INTERACTIVE_TAGS

def _attr(elem, local_name, ns=ANDROID_NS):
    return elem.get(f"{{{ns}}}{local_name}", "")

def _attr_any_ns(elem, local_name):
    for k, v in elem.attrib.items():
        if k.endswith("}" + local_name) or k == local_name:
            return v
    return ""

def _short_tag(full_tag: str) -> str:
    """去掉包名，只保留类名"""
    return full_tag.split(".")[-1]

# ──────────────────────────────────────────────
# Layout XML
# ──────────────────────────────────────────────

def extract_layout(xml_path: Path, source_prefix: str = "static_xml_layout",
                   file_prefix: str = "") -> list[dict]:
    try:
        tree = ET.parse(xml_path)
    except ET.ParseError:
        return []

    results = []
    for elem in tree.iter():
        tag = elem.tag
        short = _short_tag(tag)

        view_id       = _attr(elem, "id").replace("@+id/", "").replace("@id/", "")
        on_click_attr = _attr(elem, "onClick")
        clickable     = _attr(elem, "clickable")
        checkable     = _attr(elem, "checkable")
        visibility    = _attr(elem, "visibility") or "visible"
        text          = _attr(elem, "text")
        hint          = _attr(elem, "hint")
        content_desc  = _attr(elem, "contentDescription")

        is_interactive = (
            short in INHERENT_INTERACTIVE_TAGS
            or on_click_attr
            or clickable == "true"
            or checkable == "true"
            or (short in CONDITIONAL_INTERACTIVE_TAGS and (
                clickable == "true"
                or on_click_attr
                or _attr(elem, "longClickable") == "true"
            ))
        )

        if not (is_interactive or view_id):
            continue

        file_rel = str(xml_path.relative_to(xml_path.parents[3]))
        if file_prefix:
            file_rel = file_prefix + "/" + file_rel

        results.append({
            "source":       source_prefix,
            "file":         file_rel,
            "layout":       xml_path.stem,
            "tag":          short,
            "id":           view_id,
            "text":         text,
            "hint":         hint,
            "content_desc": content_desc,
            "on_click_attr": on_click_attr,
            "visibility":   visibility,
            "is_interactive": is_interactive,
        })

    return results


# ──────────────────────────────────────────────
# Layout XML — tree form (preserves hierarchy)
# ──────────────────────────────────────────────

def _build_tree_node(elem, include_resolver=None) -> dict:
    tag = elem.tag
    if tag == "include":
        layout_ref = _attr_any_ns(elem, "layout").replace("@layout/", "")
        if layout_ref and include_resolver:
            inc_path = include_resolver(layout_ref)
            if inc_path:
                try:
                    inc_tree = ET.parse(inc_path)
                except ET.ParseError:
                    inc_tree = None
                if inc_tree:
                    inc_root = inc_tree.getroot()
                    if _short_tag(inc_root.tag) == "merge":
                        children = [_build_tree_node(c, include_resolver) for c in inc_root]
                        return {"_merge_children": children}
                    return _build_tree_node(inc_root, include_resolver)
        return {
            "tag": "include",
            "id": "",
            "text": "", "hint": "", "content_desc": "",
            "is_interactive": False,
            "visibility": "visible",
            "source": "static_xml",
            "on_click_attr": "",
            "children": [],
        }

    short = _short_tag(tag)
    view_id = _attr(elem, "id").replace("@+id/", "").replace("@id/", "")
    on_click_attr = _attr(elem, "onClick")
    clickable = _attr(elem, "clickable")
    checkable = _attr(elem, "checkable")
    visibility = _attr(elem, "visibility") or "visible"
    text = _attr(elem, "text")
    hint = _attr(elem, "hint")
    content_desc = _attr(elem, "contentDescription")

    is_interactive = (
        short in INHERENT_INTERACTIVE_TAGS
        or bool(on_click_attr)
        or clickable == "true"
        or checkable == "true"
        or (short in CONDITIONAL_INTERACTIVE_TAGS and (
            clickable == "true"
            or bool(on_click_attr)
            or _attr(elem, "longClickable") == "true"
        ))
    )

    children = []
    for child in elem:
        node = _build_tree_node(child, include_resolver)
        if isinstance(node, dict) and "_merge_children" in node:
            children.extend(node["_merge_children"])
        else:
            children.append(node)

    return {
        "tag": short,
        "id": view_id,
        "text": text,
        "hint": hint,
        "content_desc": content_desc,
        "is_interactive": is_interactive,
        "visibility": visibility,
        "source": "static_xml",
        "on_click_attr": on_click_attr,
        "children": children,
    }


def extract_layout_tree(xml_path: Path, include_resolver=None) -> dict | None:
    try:
        tree = ET.parse(xml_path)
    except ET.ParseError:
        return None
    root = tree.getroot()
    return _build_tree_node(root, include_resolver)


# ──────────────────────────────────────────────
# Menu XML
# ──────────────────────────────────────────────

def extract_menu(xml_path: Path, source_prefix: str = "static_xml_menu",
                 file_prefix: str = "") -> list[dict]:
    try:
        tree = ET.parse(xml_path)
    except ET.ParseError:
        return []

    results = []
    for elem in tree.iter():
        if _short_tag(elem.tag) not in ("item", "Item"):
            continue

        item_id    = _attr(elem, "id").replace("@+id/", "").replace("@id/", "")
        title      = _attr(elem, "title")
        show_as    = _attr(elem, "showAsAction", ns=APP_NS)

        file_rel = str(xml_path.relative_to(xml_path.parents[2]))
        if file_prefix:
            file_rel = file_prefix + "/" + file_rel

        results.append({
            "source":         source_prefix,
            "file":           file_rel,
            "menu":           xml_path.stem,
            "tag":            "MenuItem",
            "id":             item_id,
            "text":           title,
            "show_as_action": show_as,
            "is_interactive": True,
        })

    return results


# ──────────────────────────────────────────────
# Navigation Graph XML
# ──────────────────────────────────────────────

def extract_navigation(xml_path: Path) -> list[dict]:
    try:
        tree = ET.parse(xml_path)
    except ET.ParseError:
        return []

    results = []
    root = tree.getroot()

    def _walk(node, parent_id=""):
        node_id    = _attr(node, "id").replace("@+id/", "")
        node_label = _attr(node, "label")
        short      = _short_tag(node.tag)

        if short in ("fragment", "activity", "dialog", "navigation"):
            results.append({
                "source":     "static_xml_nav",
                "file":       str(xml_path.relative_to(xml_path.parents[2])),
                "nav_graph":  xml_path.stem,
                "tag":        short,
                "id":         node_id,
                "label":      node_label,
                "is_interactive": False,
            })

        for action in node:
            if _short_tag(action.tag) == "action":
                action_id   = _attr(action, "id").replace("@+id/", "")
                destination = _attr(action, "destination").replace("@id/", "")
                results.append({
                    "source":      "static_xml_nav_action",
                    "file":        str(xml_path.relative_to(xml_path.parents[2])),
                    "nav_graph":   xml_path.stem,
                    "tag":         "NavAction",
                    "id":          action_id,
                    "from":        node_id,
                    "destination": destination,
                    "is_interactive": True,
                })
            _walk(action, node_id)

    _walk(root)
    return results


# ──────────────────────────────────────────────
# String resource loader
# ──────────────────────────────────────────────

def load_strings(project_root: str) -> dict:
    """
    Parse values/strings.xml (and values-en/ fallback) from the project.
    Returns {key: value} for use in resolving @string/xxx references.
    Only reads the default locale (values/strings.xml) — no translation variants.
    """
    strings: dict = {}
    # Collect all candidate strings.xml files; prefer app/src/main/res/values/
    candidates = [res / "values" / "strings.xml" for res in android_project.res_dirs(project_root)]
    candidates = [p for p in candidates if p.is_file()]
    if not candidates:
        root = Path(project_root)
        candidates = list(root.rglob("values/strings.xml"))
    for path in candidates:
        try:
            tree = ET.parse(path)
        except ET.ParseError:
            continue
        for elem in tree.iter("string"):
            name = elem.get("name", "")
            # Collapse whitespace and strip inner markup
            text = (elem.text or "").strip()
            if name and text:
                strings[name] = text
    return strings


def resolve_text(raw: str, strings: dict) -> str:
    """
    Resolve an @string/xxx reference to its human-readable value.
    If the key is not found (e.g. it lives in an external library), convert the
    key itself to Title Case words so labels stay readable.
    """
    if raw.startswith("@string/"):
        key = raw[len("@string/"):]
        if key in strings:
            return strings[key]
        # Key not in local strings (external library) — make it human-readable
        return key.replace("_", " ").title()
    return raw


# ──────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────

def run(project_root: str, source_prefix: str = "static_xml_layout",
        menu_prefix: str = "static_xml_menu",
        file_prefix: str = "") -> dict:
    res_dirs = android_project.res_dirs(project_root)

    # Build include resolver: layout_name → Path
    layout_file_map: dict[str, Path] = {}
    for res in res_dirs:
        for layout_dir in res.glob("layout*"):
            for f in layout_dir.glob("*.xml"):
                layout_file_map[f.stem] = f

    def _include_resolver(name: str) -> Path | None:
        return layout_file_map.get(name)

    strings = load_strings(project_root)
    all_elements = []
    layout_trees: dict[str, dict] = {}

    for res in res_dirs:
        for layout_dir in res.glob("layout*"):
            for f in layout_dir.glob("*.xml"):
                all_elements.extend(extract_layout(
                    f, source_prefix=source_prefix, file_prefix=file_prefix))
                tree_node = extract_layout_tree(f, include_resolver=_include_resolver)
                if tree_node is not None:
                    layout_trees[f.stem] = tree_node

        menu_dir = res / "menu"
        if menu_dir.exists():
            for f in menu_dir.glob("*.xml"):
                all_elements.extend(extract_menu(
                    f, source_prefix=menu_prefix, file_prefix=file_prefix))

        nav_dir = res / "navigation"
        if nav_dir.exists():
            for f in nav_dir.glob("*.xml"):
                all_elements.extend(extract_navigation(f))

    # Resolve @string/xxx references in text / hint / content_desc
    for e in all_elements:
        for field in ("text", "hint", "content_desc"):
            raw = e.get(field, "")
            if raw:
                e[field] = resolve_text(raw, strings)

    # 统计
    stats = {
        "total":          len(all_elements),
        "interactive":    sum(1 for e in all_elements if e.get("is_interactive")),
        "hidden_by_default": sum(1 for e in all_elements if e.get("visibility") in ("gone", "invisible")),
        "layout_tree_count": len(layout_trees),
        "by_source": {},
    }
    for e in all_elements:
        s = e["source"]
        stats["by_source"][s] = stats["by_source"].get(s, 0) + 1

    return {"elements": all_elements, "layout_trees": layout_trees, "stats": stats, "strings": strings}


if __name__ == "__main__":
    import sys
    project = sys.argv[1] if len(sys.argv) > 1 else "."
    result = run(project)
    out = Path("output/static_ground_truth.json")
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"✓ {result['stats']['total']} elements extracted "
          f"({result['stats']['interactive']} interactive)")
    print(f"  hidden_by_default: {result['stats']['hidden_by_default']}")
    print(f"  by source: {result['stats']['by_source']}")
