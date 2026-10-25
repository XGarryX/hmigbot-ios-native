"""
fragment_detector.py
Detect Fragment subclasses and their attachment patterns in Android source code.
Outputs structured JSON with fragment metadata.

Uses regex for attachment patterns and tree-sitter AST for comprehensive
class-declaration scanning with inheritance chain resolution.
"""
import re
from pathlib import Path
from xml.etree import ElementTree as ET

from extractors import android_project
from extractors.ast_index import (
    build_class_hierarchy, _resolve_android_base, lookup_class,
    _walk as _ast_walk, _node_text as _ast_node_text,
    _line as _ast_line, _source_files as _ast_source_files,
    _language_for as _ast_language_for, _rel_path as _ast_rel_path,
    _class_name as _ast_class_name_node,
    _first_named_child as _ast_first_child,
    parse_file as _ast_parse_file,
)

try:
    from tree_sitter_language_pack import get_parser as _get_parser
except Exception:
    _get_parser = None

ANDROID_NS = "http://schemas.android.com/apk/res/android"

# Pattern 1: FragmentTransaction.replace/add
_FRAGMENT_TX_RE = re.compile(
    r'\.(?:replace|add)\s*\(\s*R\.id\.(\w+)\s*,\s*'
    r'(?:new\s+)?(\w+)\s*[\(.]',
    re.MULTILINE,
)

# Pattern 1b: Kotlin-ktx reified FragmentTransaction extensions —
# `transaction.add<SomeFragment>(R.id.container)` /
# `replace<SomeFragment>(R.id.container)`. The fragment class is the type
# argument, not a constructor argument, so Pattern 1 misses it entirely. The
# call is often bare (no receiver dot) inside a `commit { add<T>(...) }` lambda,
# so the leading delimiter is `.`, whitespace, `{`, `(`, or line start; the
# `_is_fragment_name` gate keeps this from matching unrelated generic calls.
_FRAGMENT_TX_REIFIED_RE = re.compile(
    r'(?:^|[.\s({])(replace|add)\s*<\s*(\w+)\s*>\s*\(\s*(?:R\.id\.(\w+))?',
    re.MULTILINE,
)

# Pattern 1c: full-screen-dialog content binding —
# `FullScreenDialogFragment.Builder(ctx).setContent(SomeFragment::class.java, bundle)`
# (Kotlin) / `.setContent(SomeFragment.class, bundle)` (Java). The class literal
# passed to setContent is the fragment hosted inside the dialog, so it is a real
# mount; `_is_fragment_name` gates out non-fragment class literals.
_SETCONTENT_CLASS_RE = re.compile(
    r'\.setContent\s*\(\s*([A-Z]\w*)\s*(?:::\s*class\s*\.\s*java|::\s*class|\.\s*class)\b',
    re.MULTILINE,
)

# Pattern 2: Fragment adapter classes
_FRAGMENT_ADAPTER_CLASS_RE = re.compile(
    r'class\s+(\w+)\s*[^{]*(?:extends|:)\s*'
    r'(?:FragmentPagerAdapter|FragmentStateAdapter|FragmentStatePagerAdapter)',
)
_POSITION_BRANCH_RE = re.compile(
    r'(\d+)\s*(?:->|:)\s*(?:return\s+)?(?:new\s+)?(\w+)\s*\(',
)

# Pattern 3: XML <fragment> tag (handled via XML parsing)

# Host class detection: find enclosing class name
_CLASS_DECL_RE = re.compile(
    r'class\s+(\w+)',
)

# Priority for dedup: lower index = higher priority
_ATTACH_PRIORITY = {
    "FragmentTransaction.replace": 0,
    "FragmentTransaction.add": 0,
    "ViewPager2+FragmentStateAdapter": 1,
    "nav_graph_destination": 2,
    "xml_fragment_tag": 2,
    "fullscreen_dialog_content": 2,
    "class_declaration": 3,
}


def _find_host_class(content: str, line_idx: int) -> str:
    best = ""
    for m in _CLASS_DECL_RE.finditer(content):
        if m.start() <= _offset_for_line(content, line_idx):
            best = m.group(1)
    return best


def _offset_for_line(content: str, line_idx: int) -> int:
    offset = 0
    for i, line in enumerate(content.split("\n")):
        if i >= line_idx:
            break
        offset += len(line) + 1
    return offset


def _line_number(content: str, match_start: int) -> int:
    return content[:match_start].count("\n") + 1


# Names that contain "Fragment" but are framework infrastructure, not Fragment
# subclasses. The loose `"Fragment" in name` substring check below would otherwise
# admit them: getSupportFragmentManager() -> "SupportFragmentManager", a
# FragmentStateAdapter subclass -> "...FragmentAdapter", etc. These end up as fake
# mount records and as containment edges pointing at nodes that do not exist.
_NON_FRAGMENT_SUFFIXES = (
    "FragmentManager", "FragmentTransaction", "FragmentActivity",
    "FragmentAdapter", "FragmentPagerAdapter", "FragmentStateAdapter",
    "FragmentStatePagerAdapter",
)


def _is_fragment_name(name: str) -> bool:
    # Must be a class name, not a method: class names start uppercase. This filters
    # lowercase factory methods such as createDetailFragmentForNote().
    if not name or not name[0].isupper():
        return False
    # Framework infrastructure that merely contains the substring "Fragment".
    if name.endswith(_NON_FRAGMENT_SUFFIXES):
        return False
    fragment_suffixes = ("Fragment", "BottomSheet", "DialogFragment",
                         "BottomSheetDialogFragment", "PreferenceFragment")
    return any(name.endswith(s) for s in fragment_suffixes) or "Fragment" in name


def _ast_fragment_declarations(project_root: str, dep_roots: list[str] | None = None,
                                file_prefix: str = "",
                                hierarchy: dict | None = None) -> tuple[list[dict], dict]:
    """使用 AST 继承链解析找到所有 Fragment 子类声明。返回 (results, hierarchy)。"""
    if hierarchy is None:
        hierarchy = build_class_hierarchy(project_root, dep_roots, file_prefix)
    results = []
    for fqn, info in hierarchy.items():
        base_type = _resolve_android_base(fqn, hierarchy)
        if base_type == "fragment":
            results.append({
                "class": info.name,
                "source_file": info.source_file,
                "line": info.line,
                "base_class": info.base_class or "",
                "detection": "ast",
            })
    return results, hierarchy


def _find_enclosing_class(source: bytes, node) -> str:
    cur = node.parent()
    while cur is not None:
        if cur.kind() in {"class_declaration", "object_declaration"}:
            return _ast_class_name_node(source, cur)
        cur = cur.parent()
    return ""


def _find_enclosing_function(source: bytes, node) -> str:
    cur = node.parent()
    while cur is not None:
        if cur.kind() in {"function_declaration", "method_declaration"}:
            name_node = cur.child_by_field_name("name")
            if name_node is not None:
                return _ast_node_text(source, name_node)
            child = _ast_first_child(cur, {"simple_identifier", "identifier"})
            return _ast_node_text(source, child) if child else ""
        cur = cur.parent()
    return ""


_FRAGMENT_TX_METHODS = {"replace", "add", "show", "commit", "beginTransaction"}
_TX_ATTACH_METHODS = {"replace", "add"}


def _resolve_fragment_arg(source: bytes, arg_node, scope_node, hierarchy) -> str | None:
    """Resolve a fragment argument to a class name.

    Handles:
      - Direct constructor: SomeFragment() / new SomeFragment()
      - Companion newInstance: SomeFragment.newInstance(...)
      - Java method_invocation: SomeFragment.newInstance(...)
      - Variable reference: val f = SomeFragment(); tx.replace(..., f)
    """
    text = _ast_node_text(source, arg_node).strip()

    # 1. Kotlin call_expression: SomeFragment() or SomeFragment.newInstance(...)
    if arg_node.kind() == "call_expression":
        callee = arg_node.named_child(0) if arg_node.named_child_count() > 0 else None
        if callee is not None:
            callee_text = _ast_node_text(source, callee)
            if ".newInstance" in callee_text or ".Companion." in callee_text:
                cls = callee_text.split(".")[0].strip()
                if cls and cls[0].isupper():
                    return cls
            if callee.kind() in {"simple_identifier", "identifier"}:
                cls = callee_text.strip()
                if cls and cls[0].isupper() and _is_fragment_class(cls, hierarchy):
                    return cls

    # 2. Java: new SomeFragment()
    if arg_node.kind() == "object_creation_expression":
        type_node = arg_node.child_by_field_name("type") or _ast_first_child(
            arg_node, {"type_identifier", "scoped_type_identifier"}
        )
        if type_node is not None:
            cls = _ast_node_text(source, type_node).split(".")[-1].split("<")[0].strip()
            if cls and _is_fragment_class(cls, hierarchy):
                return cls

    # 3. Java method_invocation: SomeFragment.newInstance(...)
    if arg_node.kind() == "method_invocation":
        obj = arg_node.child_by_field_name("object")
        name = arg_node.child_by_field_name("name")
        if obj is not None and name is not None:
            method = _ast_node_text(source, name)
            if method == "newInstance":
                cls = _ast_node_text(source, obj).split(".")[-1].strip()
                if cls and cls[0].isupper() and _is_fragment_class(cls, hierarchy):
                    return cls

    # 4. Variable reference: look up declaration in scope
    if arg_node.kind() in {"simple_identifier", "identifier"}:
        var_name = text
        return _trace_variable_to_fragment(source, var_name, scope_node, hierarchy)

    # 5. Text fallback: extract class from common patterns
    return _extract_fragment_from_text(text, hierarchy)


def _extract_fragment_from_text(text: str, hierarchy) -> str | None:
    """Regex fallback: extract fragment class name from expression text."""
    # SomeFragment.newInstance(...)
    m = re.search(r'(\w+)\.newInstance\s*\(', text)
    if m:
        cls = m.group(1)
        if cls[0].isupper() and _is_fragment_class(cls, hierarchy):
            return cls
    # new SomeFragment(...)
    m = re.search(r'new\s+(\w+)\s*\(', text)
    if m:
        cls = m.group(1)
        if _is_fragment_class(cls, hierarchy):
            return cls
    # SomeFragment(...)  — Kotlin constructor
    m = re.search(r'(\w+)\s*\(', text)
    if m:
        cls = m.group(1)
        if cls[0].isupper() and _is_fragment_class(cls, hierarchy):
            return cls
    return None


def _trace_variable_to_fragment(source: bytes, var_name: str, scope_node, hierarchy) -> str | None:
    """Walk backwards through scope to find where var_name was assigned a Fragment."""
    for node in _ast_walk(scope_node):
        if node.kind() == "property_declaration":
            text = _ast_node_text(source, node)
            m = re.match(r'(?:val|var)\s+' + re.escape(var_name) + r'\s*(?::\s*([\w.]+))?\s*=', text)
            if m:
                # An explicit type annotation `val f: XFragment = newInstance(...)`
                # names the fragment directly. Prefer it: the RHS is often a bare
                # `newInstance(...)` (statically-imported companion) with no class
                # prefix, which the RHS parsing below cannot resolve.
                type_ann = m.group(1)
                if type_ann:
                    type_cls = type_ann.rsplit(".", 1)[-1]
                    if _is_fragment_class(type_cls, hierarchy):
                        return type_cls
                eq_pos = text.find("=")
                if eq_pos >= 0:
                    init = text[eq_pos + 1:].strip()
                    ctor = re.match(r'([A-Z]\w*)\s*[.(]', init)
                    if ctor:
                        cls = ctor.group(1)
                        if _is_fragment_class(cls, hierarchy):
                            return cls
                    ni = re.match(r'([A-Z]\w*)\.(?:newInstance|Companion)', init)
                    if ni:
                        cls = ni.group(1)
                        if _is_fragment_class(cls, hierarchy):
                            return cls

        elif node.kind() in {"local_variable_declaration", "variable_declarator"}:
            for i in range(node.named_child_count()):
                child = node.named_child(i)
                if child.kind() == "variable_declarator":
                    name_node = child.child_by_field_name("name") or _ast_first_child(
                        child, {"identifier"}
                    )
                    if name_node and _ast_node_text(source, name_node) == var_name:
                        val_node = child.child_by_field_name("value")
                        if val_node:
                            return _resolve_fragment_arg(source, val_node, scope_node, hierarchy)
    return None


def _is_fragment_class(name: str, hierarchy) -> bool:
    if _is_fragment_name(name):
        return True
    if hierarchy:
        info = lookup_class(hierarchy, name)
        if info is not None:
            return _resolve_android_base(info.fqn, hierarchy) == "fragment"
    return False


def _extract_container_id(source: bytes, args_node) -> str:
    """Extract R.id.xxx from the first argument of replace/add."""
    if args_node is None or args_node.named_child_count() == 0:
        return ""
    first_arg = args_node.named_child(0)
    text = _ast_node_text(source, first_arg)
    m = re.search(r'R\.id\.(\w+)', text)
    return m.group(1) if m else ""


def _ast_fragment_transactions(project_root: str, dep_roots: list[str] | None = None,
                                file_prefix: str = "",
                                hierarchy: dict | None = None) -> list[dict]:
    """Use AST to find FragmentTransaction.replace/add calls and resolve fragment arguments."""
    if _get_parser is None:
        return []

    if hierarchy is None:
        hierarchy = build_class_hierarchy(project_root, dep_roots, file_prefix)

    results: list[dict] = []
    roots = [(project_root, file_prefix)]
    if dep_roots:
        roots.extend((d, Path(d).name) for d in dep_roots)

    for root_path, prefix in roots:
        root = Path(root_path)
        for src_path in _ast_source_files(root):
            language = _ast_language_for(src_path)
            if not language:
                continue
            parsed = _ast_parse_file(src_path)
            if parsed is None:
                continue
            source, root_node = parsed
            rel = _ast_rel_path(src_path, root, prefix)

            for node in _ast_walk(root_node):
                if node.kind() not in {"call_expression", "method_invocation"}:
                    continue
                call_text = _ast_node_text(source, node)

                # Match .replace(...) / .add(...) on fragment transaction
                method_name = _get_call_method_name(source, node)
                if method_name not in _TX_ATTACH_METHODS:
                    continue

                # Check receiver looks like a FragmentTransaction
                if not _looks_like_fragment_transaction(source, node, call_text):
                    continue

                # Get arguments
                args_node = _get_args_node(node)
                if args_node is None or args_node.named_child_count() < 2:
                    continue

                container_id = _extract_container_id(source, args_node)
                frag_arg = args_node.named_child(1)

                # Find the enclosing function/class to use as scope
                scope = _find_enclosing_function_node(node)
                if scope is None:
                    scope = root_node

                frag_class = _resolve_fragment_arg(source, frag_arg, scope, hierarchy)
                if not frag_class:
                    continue

                host_class = _find_enclosing_class(source, node)
                line = _ast_line(node)
                results.append({
                    "class": frag_class,
                    "container_id": container_id,
                    "attach_method": f"FragmentTransaction.{method_name}",
                    "host_class": host_class,
                    "host_file": rel,
                    "line": line,
                    "source_file": rel,
                    "detection": "ast_dataflow",
                })

    return results


_LOAD_FRAGMENT_METHODS = {"loadFragment", "loadChildFragment"}


def _ast_load_fragment_calls(project_root: str, dep_roots: list[str] | None = None,
                              file_prefix: str = "",
                              hierarchy: dict | None = None) -> list[dict]:
    """Detect loadFragment(Fragment)/loadChildFragment(Fragment) calls via AST.

    Covers patterns like:
      - loadChildFragment(new SomeFragment())
      - loadChildFragment(SomeFragment.newInstance(...))
      - ((MainActivity) getActivity()).loadChildFragment(someFragment)
    Host is resolved from the class that defines loadFragment/loadChildFragment.
    """
    if _get_parser is None:
        return []
    if hierarchy is None:
        hierarchy = build_class_hierarchy(project_root, dep_roots, file_prefix)

    # Find which classes define loadFragment/loadChildFragment
    host_classes = _find_load_fragment_hosts(project_root, dep_roots, file_prefix, hierarchy)

    results: list[dict] = []
    roots = [(project_root, file_prefix)]
    if dep_roots:
        roots.extend((d, Path(d).name) for d in dep_roots)

    for root_path, prefix in roots:
        root = Path(root_path)
        for src_path in _ast_source_files(root):
            language = _ast_language_for(src_path)
            if not language:
                continue
            parsed = _ast_parse_file(src_path)
            if parsed is None:
                continue
            source, root_node = parsed
            rel = _ast_rel_path(src_path, root, prefix)
            source_text = source.decode("utf-8", errors="ignore")

            for node in _ast_walk(root_node):
                if node.kind() not in {"call_expression", "method_invocation"}:
                    continue
                method_name = _get_call_method_name(source, node)
                if method_name not in _LOAD_FRAGMENT_METHODS:
                    continue

                args_node = _get_args_node(node)
                if args_node is None or args_node.named_child_count() < 1:
                    continue

                frag_arg = args_node.named_child(0)
                scope = _find_enclosing_function_node(node) or root_node
                frag_class = _resolve_fragment_arg(source, frag_arg, scope, hierarchy)
                if not frag_class:
                    continue

                # Determine host: cast target or class defining the method
                host = _resolve_load_fragment_host(source, node, host_classes)
                if not host:
                    host = _find_enclosing_class(source, node)

                line = _ast_line(node)
                results.append({
                    "class": frag_class,
                    "container_id": "",
                    "attach_method": f"FragmentTransaction.replace",
                    "host_class": host,
                    "host_file": rel,
                    "line": line,
                    "source_file": rel,
                    "detection": "ast_load_fragment",
                })

    return results


def _find_load_fragment_hosts(project_root: str, dep_roots: list[str] | None,
                               file_prefix: str, hierarchy: dict) -> set[str]:
    """Find classes that define loadFragment/loadChildFragment methods."""
    hosts: set[str] = set()
    if _get_parser is None:
        return hosts
    roots = [(project_root, file_prefix)]
    if dep_roots:
        roots.extend((d, Path(d).name) for d in dep_roots)
    for root_path, prefix in roots:
        root = Path(root_path)
        for src_path in _ast_source_files(root):
            language = _ast_language_for(src_path)
            if not language:
                continue
            try:
                parser = _get_parser(language)
                source = src_path.read_bytes()
                tree = parser.parse(source.decode("utf-8"))
            except Exception:
                continue
            for node in _ast_walk(tree.root_node()):
                if node.kind() not in {"function_declaration", "method_declaration"}:
                    continue
                name_node = node.child_by_field_name("name")
                if name_node is None:
                    name_node = _ast_first_child(node, {"simple_identifier", "identifier"})
                if name_node and _ast_node_text(source, name_node) in _LOAD_FRAGMENT_METHODS:
                    cls = _find_enclosing_class(source, node)
                    if cls:
                        hosts.add(cls)
    return hosts


def _resolve_load_fragment_host(source: bytes, call_node, host_classes: set[str]) -> str:
    """Resolve the host from cast expressions like ((MainActivity) getActivity())."""
    text = _ast_node_text(source, call_node)
    # Java cast: ((MainActivity) getActivity()).loadChildFragment(...)
    m = re.search(r'\(\((\w+)\)\s*(?:getActivity|requireActivity)\s*\(\)\)', text)
    if m and m.group(1) in host_classes:
        return m.group(1)
    # Kotlin cast: (activity as MainActivity).loadChildFragment(...)
    m = re.search(r'as\s+(\w+)', text)
    if m and m.group(1) in host_classes:
        return m.group(1)
    # Direct call inside host class: loadChildFragment(...)
    for host in host_classes:
        if f"{host}." in text or text.startswith("loadChildFragment") or text.startswith("loadFragment"):
            return host
    return ""


def _ast_show_fragment_calls(project_root: str, dep_roots: list[str] | None = None,
                              file_prefix: str = "",
                              hierarchy: dict | None = None) -> list[dict]:
    """Detect DialogFragment.show(fragmentManager, tag) calls via AST.

    Covers patterns like:
      - new SomeDialog().show(getSupportFragmentManager(), tag)
      - SomeDialog.newInstance(...).show(getChildFragmentManager(), tag)
    """
    if _get_parser is None:
        return []
    if hierarchy is None:
        hierarchy = build_class_hierarchy(project_root, dep_roots, file_prefix)

    results: list[dict] = []
    roots = [(project_root, file_prefix)]
    if dep_roots:
        roots.extend((d, Path(d).name) for d in dep_roots)

    for root_path, prefix in roots:
        root = Path(root_path)
        for src_path in _ast_source_files(root):
            language = _ast_language_for(src_path)
            if not language:
                continue
            parsed = _ast_parse_file(src_path)
            if parsed is None:
                continue
            source, root_node = parsed
            rel = _ast_rel_path(src_path, root, prefix)

            for node in _ast_walk(root_node):
                if node.kind() not in {"call_expression", "method_invocation"}:
                    continue
                method_name = _get_call_method_name(source, node)
                if method_name != "show":
                    continue

                text = _ast_node_text(source, node)
                lower = text.lower()
                if "fragmentmanager" not in lower and "getsupportfragmentmanager" not in lower \
                        and "getchildfragmentmanager" not in lower \
                        and "getparentfragmentmanager" not in lower:
                    continue

                frag_class = _extract_show_receiver_class(source, node, hierarchy)
                if not frag_class:
                    continue

                host = _find_enclosing_class(source, node)
                line = _ast_line(node)
                results.append({
                    "class": frag_class,
                    "container_id": "",
                    "attach_method": "FragmentTransaction.add",
                    "host_class": host,
                    "host_file": rel,
                    "line": line,
                    "source_file": rel,
                    "detection": "ast_show",
                })

    return results


def _extract_show_receiver_class(source: bytes, show_node, hierarchy) -> str | None:
    """Extract the fragment class from the receiver of .show()."""
    text = _ast_node_text(source, show_node)

    # new SomeDialog(...).show(...)  — allow nested parens
    m = re.search(r'new\s+(\w+)\s*\(', text)
    if m:
        cls = m.group(1)
        if _is_fragment_class(cls, hierarchy):
            return cls

    # SomeDialog.newInstance(...).show(...) — tolerate a newline/whitespace between
    # the class and `.newInstance`, as in the common fluent form
    #   X
    #     .newInstance(...)
    #     .show(fm, TAG)
    m = re.search(r'(\w+)\s*\.\s*newInstance\s*\(', text)
    if m:
        cls = m.group(1)
        if _is_fragment_class(cls, hierarchy):
            return cls

    # SomeDialog(...).show(...) — Kotlin constructor
    m = re.search(r'([A-Z]\w+)\s*\(', text)
    if m:
        cls = m.group(1)
        if _is_fragment_class(cls, hierarchy):
            return cls

    # variable.show(...) — try to trace
    m = re.match(r'(\w+)\.show', text)
    if m:
        var_name = m.group(1)
        scope = _find_enclosing_function_node(show_node)
        if scope:
            return _trace_variable_to_fragment(source, var_name, scope, hierarchy)

    return None


# ── Pattern 8: switch/case fragment factory ──

_SWITCH_FACTORY_RE = re.compile(
    r'case\s+(\w+)\.TAG\s*:\s*(?:.*\n)*?.*?'
    r'(?:fragment\s*=\s*)?(?:new\s+)?(\w+)\s*[\(.]',
    re.MULTILINE,
)

_RETURN_FACTORY_RE = re.compile(
    r'case\s+(\w+)\.TAG\s*:\s*(?:.*\n)*?.*?'
    r'return\s+(?:new\s+)?(\w+)\s*[\(.]',
    re.MULTILINE,
)


def _ast_switch_factory(project_root: str, dep_roots: list[str] | None = None,
                         file_prefix: str = "",
                         hierarchy: dict | None = None) -> list[dict]:
    """Detect switch-case fragment factories like createFragmentInstance().

    Pattern: switch(tag) { case SomeFragment.TAG: fragment = new SomeFragment(); }
    Host = the class containing the factory method.
    """
    if hierarchy is None:
        hierarchy = build_class_hierarchy(project_root, dep_roots, file_prefix)

    results: list[dict] = []
    roots = [(project_root, file_prefix)]
    if dep_roots:
        roots.extend((d, Path(d).name) for d in dep_roots)

    for root_path, prefix in roots:
        root = Path(root_path)
        for f in android_project.source_files(root_path):
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            rel = android_project.relative_to_root(f, root, prefix)
            host = ""
            for m in _CLASS_DECL_RE.finditer(content):
                host = m.group(1)

            for pattern in (_SWITCH_FACTORY_RE, _RETURN_FACTORY_RE):
                for m in pattern.finditer(content):
                    tag_class = m.group(1)
                    frag_class = m.group(2)
                    if not _is_fragment_class(frag_class, hierarchy):
                        continue
                    line = _line_number(content, m.start())
                    results.append({
                        "class": frag_class,
                        "container_id": "",
                        "attach_method": "FragmentTransaction.replace",
                        "host_class": host,
                        "host_file": rel,
                        "line": line,
                        "source_file": rel,
                        "detection": "switch_factory",
                    })

    return results


# ── Pattern 9: fragment instantiation in return/assignment context ──

_RETURN_NEW_FRAG_RE = re.compile(
    r'return\s+(?:new\s+)?(\w+)\s*\(',
    re.MULTILINE,
)

_ASSIGN_NEW_FRAG_RE = re.compile(
    r'\b\w+\s*=\s*new\s+(\w+)\s*\(',
    re.MULTILINE,
)

_ASSIGN_KT_FRAG_RE = re.compile(
    r'\b\w+\s*=\s*([A-Z]\w*Fragment\w*|[A-Z]\w*Dialog\w*|[A-Z]\w*Section\w*|[A-Z]\w*BottomSheet\w*)\s*\(',
    re.MULTILINE,
)

_ADD_SECTION_RE = re.compile(
    r'addSection\s*\(\s*(?:new\s+)?(\w+)\s*\(',
    re.MULTILINE,
)

# when(step){ INTENTS -> SiteCreationIntentsFragment() } or
# WHEN -> HomePagePickerFragment.newInstance(...); also Java switch-arrow.
_ARROW_FRAG_RE = re.compile(
    r'->\s*([A-Z]\w+)\s*[.(]',
    re.MULTILINE,
)

# X.newInstance(...) as the RHS of an assignment / return / when-arm, or passed
# directly as an argument. The assignment/instantiation regexes above require a
# bare constructor (`= X(`), so the very common companion-factory form
# (`val f = X.newInstance(...)`, `return X.newInstance(...)`,
# `loadFragment(X.newInstance(...))`) slips through. Class is gated by
# _is_fragment_class so non-fragment newInstance calls are ignored.
_NEWINSTANCE_FACTORY_RE = re.compile(
    r'(?:[=(,]|->|\breturn\b)\s*([A-Z]\w*)\.newInstance\s*\(',
    re.MULTILINE,
)


def _scan_fragment_instantiations(project_root: str, dep_roots: list[str] | None = None,
                                    file_prefix: str = "",
                                    hierarchy: dict | None = None) -> list[dict]:
    """Detect fragment instantiations via return/assignment/addSection patterns.

    Catches fragments created in:
      - ViewPager adapter createFragment(): return new SomeFragment()
      - if-else factory: prefFragment = new SomeFragment()
      - addSection(new SomeFragment())
    Host = enclosing class.
    """
    if hierarchy is None:
        hierarchy = build_class_hierarchy(project_root, dep_roots, file_prefix)

    results: list[dict] = []
    roots = [(project_root, file_prefix)]
    if dep_roots:
        roots.extend((d, Path(d).name) for d in dep_roots)

    for root_path, prefix in roots:
        root = Path(root_path)
        for f in android_project.source_files(root_path):
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            rel = android_project.relative_to_root(f, root, prefix)

            for pattern in (_RETURN_NEW_FRAG_RE, _ASSIGN_NEW_FRAG_RE,
                           _ASSIGN_KT_FRAG_RE, _ADD_SECTION_RE, _ARROW_FRAG_RE,
                           _NEWINSTANCE_FACTORY_RE):
                for m in pattern.finditer(content):
                    cls = m.group(1)
                    if not _is_fragment_class(cls, hierarchy):
                        continue
                    line = _line_number(content, m.start())
                    host = _find_host_class(content, line - 1)
                    results.append({
                        "class": cls,
                        "container_id": "",
                        "attach_method": "FragmentTransaction.replace",
                        "host_class": host,
                        "host_file": rel,
                        "line": line,
                        "source_file": rel,
                        "detection": "instantiation_context",
                    })

    return results


def _get_call_method_name(source: bytes, node) -> str:
    """Extract the method name from a call_expression or method_invocation."""
    if node.kind() == "method_invocation":
        name_node = node.child_by_field_name("name")
        return _ast_node_text(source, name_node) if name_node else ""
    # Kotlin call_expression: navigation_member_expression . simple_identifier
    if node.named_child_count() > 0:
        first = node.named_child(0)
        text = _ast_node_text(source, first)
        if "." in text:
            return text.rsplit(".", 1)[-1].strip()
    return ""


def _looks_like_fragment_transaction(source: bytes, node, call_text: str) -> bool:
    """Heuristic: receiver contains 'transaction', 'beginTransaction', 'childFragmentManager',
    'supportFragmentManager', or 'fragmentManager'."""
    lower = call_text.lower()
    keywords = ("transaction", "fragmentmanager", "begintransaction",
                "childfragmentmanager", "supportfragmentmanager")
    if any(k in lower for k in keywords):
        return True
    # Also match: variable.replace(...) where variable was assigned from beginTransaction
    if node.kind() == "method_invocation":
        obj = node.child_by_field_name("object")
        if obj is not None:
            obj_text = _ast_node_text(source, obj).lower()
            return any(k in obj_text for k in keywords)
    return False


def _get_args_node(node):
    """Get the arguments/value_arguments node from a call."""
    args = node.child_by_field_name("arguments")
    if args is not None:
        return args
    return _ast_first_child(node, {"value_arguments", "argument_list"})


def _find_enclosing_function_node(node):
    cur = node.parent()
    while cur is not None:
        if cur.kind() in {"function_declaration", "method_declaration",
                          "function_body", "class_body"}:
            return cur
        cur = cur.parent()
    return None


def _scan_source_files(project_root: str, dep_roots: list[str] | None,
                       file_prefix: str) -> list[tuple[Path, str, str]]:
    roots = [project_root] + (dep_roots or [])
    files = []
    for root in roots:
        prefix = file_prefix
        if root != project_root:
            prefix = Path(root).name
        for f in android_project.source_files(root):
            rel = android_project.relative_to_root(f, root, prefix)
            files.append((f, rel, root))
    return files


def run(project_root: str, dep_roots: list[str] | None = None,
        file_prefix: str = "") -> dict:
    fragments: list[dict] = []
    files_scanned = 0

    source_files = _scan_source_files(project_root, dep_roots, file_prefix)

    for fpath, rel_path, root in source_files:
        try:
            content = fpath.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        files_scanned += 1

        # Pattern 1: FragmentTransaction.replace/add
        for m in _FRAGMENT_TX_RE.finditer(content):
            container_id = m.group(1)
            frag_class = m.group(2)
            if not _is_fragment_name(frag_class):
                continue
            line = _line_number(content, m.start())
            host = _find_host_class(content, line - 1)
            method = "replace" if ".replace" in m.group(0) else "add"
            fragments.append({
                "class": frag_class,
                "container_id": container_id,
                "attach_method": f"FragmentTransaction.{method}",
                "host_class": host,
                "host_file": rel_path,
                "line": line,
                "source_file": rel_path,
            })

        # Pattern 1b: ktx reified add<T>()/replace<T>()
        for m in _FRAGMENT_TX_REIFIED_RE.finditer(content):
            method = m.group(1)
            frag_class = m.group(2)
            container_id = m.group(3) or ""
            if not _is_fragment_name(frag_class):
                continue
            line = _line_number(content, m.start())
            host = _find_host_class(content, line - 1)
            fragments.append({
                "class": frag_class,
                "container_id": container_id,
                "attach_method": f"FragmentTransaction.{method}",
                "host_class": host,
                "host_file": rel_path,
                "line": line,
                "source_file": rel_path,
            })

        # Pattern 1c: FullScreenDialogFragment.Builder.setContent(X::class.java)
        for m in _SETCONTENT_CLASS_RE.finditer(content):
            frag_class = m.group(1)
            if not _is_fragment_name(frag_class):
                continue
            line = _line_number(content, m.start())
            host = _find_host_class(content, line - 1)
            fragments.append({
                "class": frag_class,
                "container_id": "",
                "attach_method": "fullscreen_dialog_content",
                "host_class": host,
                "host_file": rel_path,
                "line": line,
                "source_file": rel_path,
            })

        # Pattern 2: FragmentPagerAdapter/FragmentStateAdapter
        for m_cls in _FRAGMENT_ADAPTER_CLASS_RE.finditer(content):
            adapter_class = m_cls.group(1)
            adapter_start = m_cls.start()
            body_re = re.compile(
                r'(?:getItem|createFragment)\s*\([^)]*\)\s*[:{]',
            )
            body_match = body_re.search(content, adapter_start)
            if not body_match:
                continue
            body_start = body_match.end()
            search_end = min(body_start + 2000, len(content))
            body_text = content[body_start:search_end]
            for m_pos in _POSITION_BRANCH_RE.finditer(body_text):
                frag_class = m_pos.group(2)
                if not _is_fragment_name(frag_class):
                    continue
                position = int(m_pos.group(1))
                line = _line_number(content, body_start + m_pos.start())
                fragments.append({
                    "class": frag_class,
                    "container_id": "",
                    "attach_method": "ViewPager2+FragmentStateAdapter",
                    "host_class": adapter_class,
                    "host_file": rel_path,
                    "line": line,
                    "position": position,
                    "source_file": rel_path,
                })

    # Pattern 3: XML <fragment> tags
    roots_to_scan = [project_root] + (dep_roots or [])
    for root in roots_to_scan:
        prefix = file_prefix if root == project_root else Path(root).name
        for res_dir in android_project.res_dirs(root):
            for layout_dir in res_dir.glob("layout*"):
                for xml_file in layout_dir.glob("*.xml"):
                    try:
                        tree = ET.parse(xml_file)
                    except ET.ParseError:
                        continue
                    for elem in tree.iter():
                        tag = elem.tag
                        if not isinstance(tag, str):
                            continue
                        is_fragment_tag = tag == "fragment" or tag.endswith("}fragment")
                        # FragmentContainerView with android:name is a *static* mount,
                        # equivalent to <fragment>. Without android:name it is a dynamic
                        # container filled by transactions (no class to bind here).
                        is_static_container = tag.endswith("FragmentContainerView")
                        if not (is_fragment_tag or is_static_container):
                            continue
                        name_attr = elem.get(f"{{{ANDROID_NS}}}name", "") or elem.get("android:name", "") or elem.get("class", "")
                        if not name_attr:
                            continue
                        frag_class = name_attr.rsplit(".", 1)[-1]
                        # NavHostFragment is a navigation container, not a real screen block.
                        if frag_class == "NavHostFragment":
                            continue
                        container_id = (elem.get(f"{{{ANDROID_NS}}}id", "") or "").replace("@+id/", "").replace("@id/", "")
                        rel = android_project.relative_to_root(xml_file, root, prefix)
                        fragments.append({
                            "class": frag_class,
                            "container_id": container_id,
                            "attach_method": "xml_fragment_tag" if is_fragment_tag else "xml_fragment_container",
                            "host_class": "",
                            "host_file": rel,
                            "line": 0,
                            "source_file": rel,
                        })

            # Navigation Component graphs (res/navigation/*.xml). Every <fragment>
            # and <dialog> destination is a hosted screen; android:name carries its
            # class. <activity> is an external launch, and <argument>/<action>/
            # <deepLink>/<include> are not classes, so they are skipped by tag.
            for nav_dir in res_dir.glob("navigation*"):
                for xml_file in nav_dir.glob("*.xml"):
                    try:
                        tree = ET.parse(xml_file)
                    except ET.ParseError:
                        continue
                    for elem in tree.iter():
                        tag = elem.tag
                        if not isinstance(tag, str):
                            continue
                        local = tag.rsplit("}", 1)[-1]
                        if local not in ("fragment", "dialog"):
                            continue
                        name_attr = elem.get(f"{{{ANDROID_NS}}}name", "") or elem.get("android:name", "")
                        if not name_attr or "." not in name_attr:
                            continue
                        frag_class = name_attr.rsplit(".", 1)[-1]
                        if frag_class == "NavHostFragment":
                            continue
                        container_id = (elem.get(f"{{{ANDROID_NS}}}id", "") or "").replace("@+id/", "").replace("@id/", "")
                        rel = android_project.relative_to_root(xml_file, root, prefix)
                        fragments.append({
                            "class": frag_class,
                            "container_id": container_id,
                            "attach_method": "nav_graph_destination",
                            "host_class": "",
                            "host_file": rel,
                            "line": 0,
                            "source_file": rel,
                        })

    # Build class hierarchy once, share between AST passes
    hierarchy = build_class_hierarchy(project_root, dep_roots, file_prefix)

    # Pattern 4: AST-based fragment class declarations (inheritance chain aware)
    ast_decls, hierarchy = _ast_fragment_declarations(project_root, dep_roots, file_prefix,
                                                       hierarchy=hierarchy)

    # Pattern 5: AST data-flow fragment transactions
    ast_tx = _ast_fragment_transactions(project_root, dep_roots, file_prefix,
                                         hierarchy=hierarchy)
    for tx in ast_tx:
        fragments.append(tx)

    # Pattern 6: loadFragment/loadChildFragment calls
    load_frags = _ast_load_fragment_calls(project_root, dep_roots, file_prefix,
                                           hierarchy=hierarchy)
    for lf in load_frags:
        fragments.append(lf)

    # Pattern 7: DialogFragment.show() calls
    show_frags = _ast_show_fragment_calls(project_root, dep_roots, file_prefix,
                                           hierarchy=hierarchy)
    for sf in show_frags:
        fragments.append(sf)

    # Pattern 8: switch-case fragment factory (createFragmentInstance etc.)
    factory_frags = _ast_switch_factory(project_root, dep_roots, file_prefix,
                                         hierarchy=hierarchy)
    for ff in factory_frags:
        fragments.append(ff)

    # Pattern 9: fragment instantiation in return/assignment/addSection
    inst_frags = _scan_fragment_instantiations(project_root, dep_roots, file_prefix,
                                                hierarchy=hierarchy)
    for inf in inst_frags:
        fragments.append(inf)

    attached_names = {f["class"] for f in fragments}
    for decl in ast_decls:
        if decl["class"] not in attached_names:
            fragments.append({
                "class": decl["class"],
                "container_id": "",
                "attach_method": "class_declaration",
                "host_class": "",
                "host_file": "",
                "line": decl["line"],
                "source_file": decl["source_file"],
            })

    # Dedup: keep highest-priority attach_method per fragment class
    deduped: dict[str, dict] = {}
    for frag in fragments:
        cls = frag["class"]
        if cls not in deduped:
            deduped[cls] = frag
        else:
            existing_priority = _ATTACH_PRIORITY.get(deduped[cls]["attach_method"], 99)
            new_priority = _ATTACH_PRIORITY.get(frag["attach_method"], 99)
            if new_priority < existing_priority:
                deduped[cls] = frag
            elif new_priority == existing_priority and frag["attach_method"] != "class_declaration":
                key = f"{cls}@{frag.get('container_id', '')}@{frag.get('host_class', '')}"
                if key not in deduped:
                    deduped[key] = frag

    result_fragments = sorted(deduped.values(), key=lambda f: (f["source_file"], f["line"]))

    by_method: dict[str, int] = {}
    for f in result_fragments:
        m = f["attach_method"]
        by_method[m] = by_method.get(m, 0) + 1

    # Coverage: all Fragment classes from AST hierarchy
    ast_class_names = {d["class"] for d in ast_decls}
    attached_classes = {f["class"] for f in result_fragments if f["attach_method"] != "class_declaration"}

    # A declared fragment that is the supertype of another class is an abstract base:
    # it reaches the screen through its subclasses, not directly, so it does not need
    # its own host. Exclude such bases (when not themselves directly attached) from the
    # orphan set, otherwise they inflate the "no host" count as false positives.
    base_class_names = {info.base_class for info in hierarchy.values() if info.base_class}
    base_fragment_names = (ast_class_names & base_class_names) - attached_classes

    needs_host = ast_class_names - base_fragment_names
    attached_for_host = attached_classes & needs_host
    orphan_classes = sorted(needs_host - attached_for_host) if ast_decls else []

    coverage: dict = {
        "ast_available": bool(ast_decls),
        "declared_fragment_count": len(ast_class_names),
        "base_class_count": len(base_fragment_names),
        "needs_host_count": len(needs_host),
        "attached_fragment_count": len(attached_for_host),
        "orphan_classes": orphan_classes,
    }

    return {
        "fragments": result_fragments,
        "stats": {
            "total": len(result_fragments),
            "by_attach_method": by_method,
            "source_files_scanned": files_scanned,
            "coverage": coverage,
        },
    }
