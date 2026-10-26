"""
dynamic_ui_extractor.py
Detect dynamically-created UI components in Android source code.

Three detection patterns:
  1. addView  — container.addView(new XxxView(ctx)) or container.addView(v)
  2. inflate+addView — val v = inflater.inflate(R.layout.xxx); container.addView(v)
  3. setAdapter — recyclerView.adapter = XxxAdapter(); find inflate in adapter class

Uses tree-sitter AST when available for reliable method-body scoping and
variable tracking. Falls back to regex when tree-sitter is not available.
"""
from __future__ import annotations

import re
from pathlib import Path

from extractors import android_project

try:
    from tree_sitter_language_pack import get_parser as _get_parser
except Exception:
    _get_parser = None

try:
    from extractors.ast_index import parse_file as _ast_parse_file
except Exception:
    _ast_parse_file = None

# ── Shared constants ──────────────────────────────────────────────────────────

_INIT_METHOD_NAMES = {
    "onCreate", "onCreateView", "onViewCreated",
    "initView", "initUI", "setupView", "setupUI",
    "initViews", "bindViews", "setupViews",
    "onActivityCreated", "onStart",
}

_VIEW_SUFFIXES = {
    "View", "Layout", "Button", "TextView", "ImageView",
    "EditText", "Switch", "CheckBox", "RadioButton",
    "Spinner", "ProgressBar", "SeekBar", "RatingBar",
    "Chip", "Card", "CardView", "Toolbar", "AppBarLayout",
    "FloatingActionButton", "RecyclerView", "ListView",
    "GridView", "ScrollView", "WebView", "FrameLayout",
    "LinearLayout", "RelativeLayout", "ConstraintLayout",
    "CoordinatorLayout", "ViewPager", "TabLayout",
}

_ADAPTER_BASES = {
    "RecyclerView.Adapter", "ArrayAdapter", "BaseAdapter",
    "ListAdapter", "PagingDataAdapter", "CursorAdapter",
    "SimpleCursorAdapter", "PagedListAdapter",
    "FragmentStateAdapter", "FragmentPagerAdapter",
}

# Property setter extraction (shared by both AST and regex paths)
_SETTER_PATTERNS = {
    "text": re.compile(r'(\w+)\s*\.\s*(?:text\s*=|setText\s*\()\s*["\']([^"\']{1,80})', re.MULTILINE),
    "hint": re.compile(r'(\w+)\s*\.\s*(?:hint\s*=|setHint\s*\()\s*["\']([^"\']{1,80})', re.MULTILINE),
    "content_description": re.compile(r'(\w+)\s*\.\s*(?:contentDescription\s*=|setContentDescription\s*\()\s*["\']([^"\']{1,80})', re.MULTILINE),
}


def _extract_properties(body: str, var_name: str) -> dict:
    props: dict[str, str] = {}
    for prop_name, pat in _SETTER_PATTERNS.items():
        for m in pat.finditer(body):
            if m.group(1) == var_name:
                props[prop_name] = m.group(2)
    return props


# ═══════════════════════════════════════════════════════════════════════════════
# AST path — tree-sitter based analysis
# ═══════════════════════════════════════════════════════════════════════════════

def _node_text(source: bytes, node) -> str:
    return source[node.start_byte():node.end_byte()].decode("utf-8", errors="ignore")


def _node_line(node) -> int:
    return node.start_position().row + 1


def _walk(node):
    yield node
    for i in range(node.child_count()):
        yield from _walk(node.child(i))


def _is_view_type(name: str) -> bool:
    return any(name.endswith(s) for s in _VIEW_SUFFIXES) or name in _VIEW_SUFFIXES


def _child_by_kind(node, kind: str):
    for i in range(node.child_count()):
        c = node.child(i)
        if c.kind() == kind:
            return c
    return None


def _scan_file_ast(source: bytes, root_node, language: str, rel_path: str,
                   dynamic_elements: list, adapter_usages: dict, adapter_layouts: list) -> bool:
    """Scan a file using tree-sitter AST. Returns True if AST was used."""
    # Find all class declarations
    for node in _walk(root_node):
        if node.kind() not in ("class_declaration", "object_declaration"):
            continue
        name_node = (node.child_by_field_name("name")
                     or _child_by_kind(node, "type_identifier")
                     or _child_by_kind(node, "identifier"))
        if name_node is None:
            continue
        class_name = _node_text(source, name_node)

        # Find all methods in this class
        for child in _walk(node):
            if child.kind() not in ("function_declaration", "method_declaration"):
                continue
            fn_name_node = (child.child_by_field_name("name")
                           or _child_by_kind(child, "simple_identifier")
                           or _child_by_kind(child, "identifier"))
            if fn_name_node is None:
                continue
            fn_name = _node_text(source, fn_name_node)

            # Check if this is an init method or override lifecycle method
            if fn_name not in _INIT_METHOD_NAMES:
                continue

            body_node = (child.child_by_field_name("body")
                         or _child_by_kind(child, "function_body")
                         or _child_by_kind(child, "block"))
            if body_node is None:
                body_node = child
            body_text = _node_text(source, body_node)

            # Collect variable declarations: var_name → (type_or_layout, kind)
            var_info: dict[str, tuple[str, str]] = {}
            _collect_var_declarations(source, body_node, language, var_info)

            # Find addView calls
            _find_addview_calls(source, body_node, body_text, class_name, fn_name,
                                rel_path, var_info, dynamic_elements)

            # Find setAdapter / adapter = calls
            _find_adapter_assignments(source, body_node, body_text, class_name,
                                      rel_path, adapter_usages)

        # Find adapter class inflate patterns
        _find_adapter_inflates(source, node, class_name, rel_path,
                               adapter_usages, adapter_layouts)

    return True


def _collect_var_declarations(source: bytes, body_node, language: str,
                              var_info: dict[str, tuple[str, str]]) -> None:
    """Collect local variable declarations and their initializer types."""
    for node in _walk(body_node):
        if node.kind() == "property_declaration" and language == "kotlin":
            _process_kotlin_var_decl(source, node, var_info)
        elif node.kind() == "local_variable_declaration" and language == "java":
            _process_java_var_decl(source, node, var_info)


def _process_kotlin_var_decl(source: bytes, node, var_info: dict) -> None:
    """Extract variable name and initializer from Kotlin property declaration."""
    # Find variable name — in Kotlin grammar: property_declaration > variable_declaration > simple_identifier
    var_name = ""
    var_decl = _child_by_kind(node, "variable_declaration")
    if var_decl is not None:
        id_node = _child_by_kind(var_decl, "simple_identifier")
        if id_node is not None:
            var_name = _node_text(source, id_node)
    if not var_name:
        for i in range(node.named_child_count()):
            child = node.named_child(i)
            if child.kind() == "simple_identifier":
                var_name = _node_text(source, child)
                break

    if not var_name:
        return

    # Find initializer value
    text = _node_text(source, node)

    # Check for View constructor: val v = TextView(ctx)
    ctor_match = re.search(r'=\s*(\w+)\s*\(', text)
    if ctor_match:
        type_name = ctor_match.group(1)
        if _is_view_type(type_name):
            var_info[var_name] = (type_name, "ctor")
            return

    # Check for inflate: val v = inflater.inflate(R.layout.xxx, ...)
    inflate_match = re.search(r'inflate\s*\(\s*R\.layout\.(\w+)', text)
    if inflate_match:
        var_info[var_name] = (inflate_match.group(1), "inflate")
        return

    # Check for findViewById: val v = findViewById<T>(R.id.xxx)
    fvbi_match = re.search(r'findViewById\w*\s*(?:<[^>]*>\s*)?\(\s*R\.id\.(\w+)', text)
    if fvbi_match:
        var_info[var_name] = (fvbi_match.group(1), "find_view")


def _process_java_var_decl(source: bytes, node, var_info: dict) -> None:
    """Extract variable name and initializer from Java local variable declaration."""
    text = _node_text(source, node)

    # Find variable name from declarator
    decl_match = re.search(r'(\w+)\s*=', text)
    if not decl_match:
        return
    var_name = decl_match.group(1)

    # Check for View constructor: View v = new TextView(ctx)
    ctor_match = re.search(r'new\s+(\w+)\s*\(', text)
    if ctor_match:
        type_name = ctor_match.group(1)
        if _is_view_type(type_name):
            var_info[var_name] = (type_name, "ctor")
            return

    inflate_match = re.search(r'inflate\s*\(\s*R\.layout\.(\w+)', text)
    if inflate_match:
        var_info[var_name] = (inflate_match.group(1), "inflate")
        return

    fvbi_match = re.search(r'findViewById\s*\(\s*R\.id\.(\w+)', text)
    if fvbi_match:
        var_info[var_name] = (fvbi_match.group(1), "find_view")


def _find_addview_calls(source: bytes, body_node, body_text: str,
                        class_name: str, method_name: str, rel_path: str,
                        var_info: dict, dynamic_elements: list) -> None:
    """Find addView calls and resolve container/child types from var_info."""
    for node in _walk(body_node):
        if node.kind() not in ("call_expression", "method_invocation"):
            continue
        text = _node_text(source, node)
        if "addView" not in text:
            continue

        add_match = re.match(r'(\w+)\s*\.\s*addView\s*\(\s*(\w+)', text)
        if not add_match:
            continue

        container_var = add_match.group(1)
        added_var = add_match.group(2)
        line = _node_line(node)

        # Resolve container id
        container_id = ""
        if container_var in var_info and var_info[container_var][1] == "find_view":
            container_id = var_info[container_var][0]

        if added_var in var_info:
            val, kind = var_info[added_var]
            if kind == "ctor":
                dynamic_elements.append({
                    "view_type": val,
                    "variable_name": added_var,
                    "container_variable": container_var,
                    "container_id": container_id,
                    "creation_method": "addView",
                    "host_class": class_name,
                    "host_method": method_name,
                    "file": rel_path,
                    "line": line,
                    "properties": _extract_properties(body_text, added_var),
                })
            elif kind == "inflate":
                dynamic_elements.append({
                    "view_type": "inflated_layout",
                    "layout_name": val,
                    "variable_name": added_var,
                    "container_variable": container_var,
                    "container_id": container_id,
                    "creation_method": "inflate+addView",
                    "host_class": class_name,
                    "host_method": method_name,
                    "file": rel_path,
                    "line": line,
                    "properties": {},
                })


def _find_adapter_assignments(source: bytes, body_node, body_text: str,
                              class_name: str, rel_path: str,
                              adapter_usages: dict) -> None:
    """Find adapter = XxxAdapter() or setAdapter(adapter) assignments."""
    adapter_re = re.compile(r'(\w+)\s*\.\s*(?:adapter\s*=\s*|setAdapter\s*\(\s*)(\w+)\s*[\(.\)]')
    for m in adapter_re.finditer(body_text):
        host_var = m.group(1)
        adapter_ref = m.group(2)
        # Resolve variable name to actual adapter class name
        adapter_class = adapter_ref
        if not adapter_ref.endswith("Adapter"):
            resolve_re = re.compile(
                rf'(?:val|var|final|\w+\s+)?{re.escape(adapter_ref)}\s*=\s*new\s+(\w+Adapter)\s*\(',
            )
            resolve_m = resolve_re.search(body_text)
            if resolve_m:
                adapter_class = resolve_m.group(1)
        # Try to resolve host variable's view id
        host_id = ""
        fvbi = re.search(
            rf'(?:val|var|final)\s+{re.escape(host_var)}\s*(?::\s*\w+)?\s*=\s*\w*\.?findViewById\w*\s*(?:<[^>]*>\s*)?\(\s*R\.id\.(\w+)',
            body_text,
        )
        if fvbi:
            host_id = fvbi.group(1)
        adapter_usages[adapter_class] = {
            "host_class": class_name,
            "host_variable": host_var,
            "host_id": host_id,
            "file": rel_path,
            "line": body_text[:m.start()].count("\n") + 1,
        }


def _find_adapter_inflates(source: bytes, class_node, class_name: str,
                           rel_path: str, adapter_usages: dict,
                           adapter_layouts: list) -> None:
    """Check if a class is an adapter and extract its item layout inflate calls."""
    if not class_name.endswith("Adapter"):
        return

    class_text = _node_text(source, class_node)
    is_adapter = any(base in class_text for base in _ADAPTER_BASES)
    if not is_adapter:
        return

    inflate_re = re.compile(r'inflate\s*\(\s*R\.layout\.(\w+)')
    for m in inflate_re.finditer(class_text):
        usage = adapter_usages.get(class_name, {})
        adapter_layouts.append({
            "adapter_class": class_name,
            "item_layout": m.group(1),
            "host_class": usage.get("host_class", ""),
            "host_variable": usage.get("host_variable", ""),
            "host_id": usage.get("host_id", ""),
            "file": rel_path,
            "line": _node_line(class_node) + class_text[:m.start()].count("\n"),
        })


# ═══════════════════════════════════════════════════════════════════════════════
# Regex fallback path
# ═══════════════════════════════════════════════════════════════════════════════

_INIT_METHOD_RE = re.compile(
    r'(?:fun\s+|\b\w+(?:\s+\w+)*\s+)'
    r'(' + '|'.join(_INIT_METHOD_NAMES) + r')\s*\(',
    re.MULTILINE,
)

_ADD_VIEW_RE = re.compile(r'(\w+)\s*\.\s*addView\s*\(\s*(\w+)', re.MULTILINE)

_VIEW_CTOR_RE = re.compile(
    r'(?:val|var|final)\s+(\w+)\s*(?::\s*\w+)?\s*=\s*(?:new\s+)?(\w+(?:'
    + '|'.join(sorted(_VIEW_SUFFIXES, key=len, reverse=True))
    + r'))\s*\(',
    re.MULTILINE,
)

_INFLATE_VAR_RE = re.compile(
    r'(?:val|var|final)\s+(\w+)\s*(?::\s*\w+)?\s*=\s*\w+\.inflate\s*\(\s*R\.layout\.(\w+)',
    re.MULTILINE,
)

_SET_ADAPTER_RE = re.compile(
    r'(\w+)\s*\.\s*(?:adapter\s*=\s*|setAdapter\s*\(\s*)(\w+)\s*[\(.\)]',
    re.MULTILINE,
)

_ADAPTER_CLASS_RE = re.compile(
    r'class\s+(\w+Adapter)\s*[^{]*(?:extends|:)\s*'
    r'(?:' + '|'.join(re.escape(b) for b in _ADAPTER_BASES) + r')',
    re.MULTILINE,
)

_ADAPTER_INFLATE_RE = re.compile(r'inflate\s*\(\s*R\.layout\.(\w+)', re.MULTILINE)

_CLASS_DECL_RE = re.compile(r'class\s+(\w+)', re.MULTILINE)


def _find_host_class(content: str, offset: int) -> str:
    best = ""
    for m in _CLASS_DECL_RE.finditer(content):
        if m.start() <= offset:
            best = m.group(1)
    return best


def _line_number(content: str, offset: int) -> int:
    return content[:offset].count("\n") + 1


def _find_method_body(content: str, method_match: re.Match) -> str:
    start = method_match.end()
    depth = 0
    body_start = -1
    for i in range(start, min(start + 5000, len(content))):
        ch = content[i]
        if ch == '{':
            if depth == 0:
                body_start = i
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0 and body_start >= 0:
                return content[body_start:i + 1]
    return content[start:start + 3000]


def _find_view_id_for_variable(body: str, var_name: str) -> str:
    pat = re.compile(
        rf'(?:val|var|final)\s+{re.escape(var_name)}\s*(?::\s*\w+)?\s*=\s*\w*\.?findViewById\w*\s*(?:<[^>]*>\s*)?\(\s*R\.id\.(\w+)',
    )
    m = pat.search(body)
    return m.group(1) if m else ""


def _scan_file_regex(content: str, rel_path: str,
                     dynamic_elements: list, adapter_usages: dict,
                     adapter_layouts: list) -> None:
    """Regex-based fallback when tree-sitter is not available."""
    for method_match in _INIT_METHOD_RE.finditer(content):
        method_name = method_match.group(1)
        body = _find_method_body(content, method_match)
        host_class = _find_host_class(content, method_match.start())
        body_offset = content.find(body, method_match.end() - 20)
        if body_offset < 0:
            body_offset = method_match.start()

        var_types: dict[str, str] = {}
        for m in _VIEW_CTOR_RE.finditer(body):
            var_types[m.group(1)] = m.group(2)

        var_layouts: dict[str, str] = {}
        for m in _INFLATE_VAR_RE.finditer(body):
            var_layouts[m.group(1)] = m.group(2)

        for m in _ADD_VIEW_RE.finditer(body):
            container_var = m.group(1)
            added_var = m.group(2)
            container_id = _find_view_id_for_variable(body, container_var)
            line = _line_number(content, body_offset + m.start())

            if added_var in var_types:
                dynamic_elements.append({
                    "view_type": var_types[added_var],
                    "variable_name": added_var,
                    "container_variable": container_var,
                    "container_id": container_id,
                    "creation_method": "addView",
                    "host_class": host_class,
                    "host_method": method_name,
                    "file": rel_path,
                    "line": line,
                    "properties": _extract_properties(body, added_var),
                })
            elif added_var in var_layouts:
                dynamic_elements.append({
                    "view_type": "inflated_layout",
                    "layout_name": var_layouts[added_var],
                    "variable_name": added_var,
                    "container_variable": container_var,
                    "container_id": container_id,
                    "creation_method": "inflate+addView",
                    "host_class": host_class,
                    "host_method": method_name,
                    "file": rel_path,
                    "line": line,
                    "properties": {},
                })

        for m in _SET_ADAPTER_RE.finditer(body):
            host_var = m.group(1)
            adapter_ref = m.group(2)
            # Resolve variable name to actual adapter class name
            adapter_class = adapter_ref
            if not adapter_ref.endswith("Adapter"):
                resolve_re = re.compile(
                    rf'(?:val|var|final|\w+\s+)?{re.escape(adapter_ref)}\s*=\s*new\s+(\w+Adapter)\s*\(',
                )
                resolve_m = resolve_re.search(body)
                if resolve_m:
                    adapter_class = resolve_m.group(1)
            host_id = _find_view_id_for_variable(body, host_var)
            line = _line_number(content, body_offset + m.start())
            adapter_usages[adapter_class] = {
                "host_class": host_class,
                "host_variable": host_var,
                "host_id": host_id,
                "file": rel_path,
                "line": line,
            }

    for m in _ADAPTER_CLASS_RE.finditer(content):
        adapter_class = m.group(1)
        class_start = m.start()
        depth = 0
        body_start = -1
        for i in range(class_start, min(class_start + 20000, len(content))):
            if content[i] == '{':
                if depth == 0:
                    body_start = i
                depth += 1
            elif content[i] == '}':
                depth -= 1
                if depth == 0 and body_start >= 0:
                    class_body = content[body_start:i + 1]
                    break
        else:
            class_body = content[class_start:class_start + 5000]

        for inflate_m in _ADAPTER_INFLATE_RE.finditer(class_body):
            item_layout = inflate_m.group(1)
            usage = adapter_usages.get(adapter_class, {})
            line = _line_number(content, class_start + inflate_m.start())
            adapter_layouts.append({
                "adapter_class": adapter_class,
                "item_layout": item_layout,
                "host_class": usage.get("host_class", ""),
                "host_variable": usage.get("host_variable", ""),
                "host_id": usage.get("host_id", ""),
                "file": rel_path,
                "line": line,
            })


# ═══════════════════════════════════════════════════════════════════════════════
# Entry point
# ═══════════════════════════════════════════════════════════════════════════════

def _language_for(path: Path) -> str:
    if path.suffix == ".kt":
        return "kotlin"
    if path.suffix == ".java":
        return "java"
    return ""


def run(project_root: str, dep_roots: list[str] | None = None,
        file_prefix: str = "") -> dict:
    roots = [(project_root, file_prefix)] + [
        (dep, Path(dep).name) for dep in (dep_roots or [])
    ]

    dynamic_elements: list[dict] = []
    adapter_usages: dict[str, dict] = {}
    adapter_layouts: list[dict] = []
    files_scanned = 0
    ast_used = False

    for root, prefix in roots:
        for fpath in android_project.source_files(root):
            try:
                content = fpath.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            files_scanned += 1
            rel = android_project.relative_to_root(fpath, root, prefix)

            # Try AST path first
            used_ast = False
            if _ast_parse_file is not None:
                lang = _language_for(fpath)
                if lang:
                    parsed = _ast_parse_file(fpath)
                    if parsed is not None:
                        source, root_node = parsed
                        try:
                            _scan_file_ast(source, root_node, lang, rel,
                                           dynamic_elements, adapter_usages, adapter_layouts)
                            used_ast = True
                            ast_used = True
                        except Exception:
                            pass

            if not used_ast:
                _scan_file_regex(content, rel, dynamic_elements,
                                 adapter_usages, adapter_layouts)

    # Backfill host info for adapter_layouts: the adapter class file may have
    # been scanned before its host Activity/Fragment file, leaving host fields
    # empty. Run a second pass to cross-reference with full adapter_usages.
    for al in adapter_layouts:
        ac = al.get("adapter_class", "")
        if ac and not al.get("host_class"):
            usage = adapter_usages.get(ac, {})
            if usage.get("host_class"):
                al["host_class"] = usage["host_class"]
                al["host_variable"] = usage.get("host_variable", "")
                al["host_id"] = usage.get("host_id", "")

    # Third pass: aggressively scan for adapter assignments in all source
    # files, not limited to init methods. This catches setAdapter calls in
    # constructor bodies, helper methods, and files where AST parsing failed.
    _AGGRESSIVE_SET_ADAPTER_RE = re.compile(
        r'(\w+)\s*\.\s*(?:adapter\s*=\s*|setAdapter\s*\(\s*)(\w+)\s*[\)]',
        re.MULTILINE,
    )
    _AGGRESSIVE_CLASS_RE = re.compile(
        r'setAdapter\s*\(\s*(\w+(?:Adapter|adapter))',
        re.MULTILINE,
    )
    _CLASS_DECL_RE = re.compile(
        r'class\s+(\w+)',
    )

    for root_path, prefix in roots:
        for fpath in android_project.source_files(root_path):
            try:
                content = fpath.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            rel = android_project.relative_to_root(fpath, root_path, prefix)

            # Find the enclosing class name
            class_match = _CLASS_DECL_RE.search(content)
            host_class = class_match.group(1) if class_match else ""

            for m in _AGGRESSIVE_SET_ADAPTER_RE.finditer(content):
                adapter_ref = m.group(2)
                adapter_class = adapter_ref
                line_num = content[:m.start()].count("\n") + 1

                # Variable resolution
                if not adapter_ref.endswith("Adapter"):
                    resolve_re = re.compile(
                        rf'(?:val|var|final|\w+\s+)?{re.escape(adapter_ref)}\s*=\s*new\s+(\w+Adapter)\s*\(',
                    )
                    resolve_m = resolve_re.search(content)
                    if resolve_m:
                        adapter_class = resolve_m.group(1)

                # Only store if this adapter_class is in our adapter_layouts
                # and doesn't already have a host
                target_al = None
                for al in adapter_layouts:
                    if al["adapter_class"] == adapter_class and not al.get("host_class"):
                        target_al = al
                        break

                if target_al:
                    host_id = ""
                    fvbi = re.search(
                        rf'(?:val|var|final)\s+{re.escape(m.group(1))}\s*=.*?findViewById\w*\(\s*R\.id\.(\w+)',
                        content,
                    )
                    if fvbi:
                        host_id = fvbi.group(1)

                    if not target_al.get("host_class"):
                        target_al["host_class"] = host_class
                        target_al["host_variable"] = m.group(1)
                        target_al["host_id"] = host_id

                    adapter_usages[adapter_class] = {
                        "host_class": host_class,
                        "host_variable": m.group(1),
                        "host_id": host_id,
                        "file": rel,
                        "line": line_num,
                    }

    by_method: dict[str, int] = {}
    for elem in dynamic_elements:
        m = elem["creation_method"]
        by_method[m] = by_method.get(m, 0) + 1

    return {
        "dynamic_elements": dynamic_elements,
        "adapter_layouts": adapter_layouts,
        "stats": {
            "total_dynamic_elements": len(dynamic_elements),
            "total_adapter_layouts": len(adapter_layouts),
            "by_creation_method": by_method,
            "source_files_scanned": files_scanned,
            "ast_used": ast_used,
        },
    }
