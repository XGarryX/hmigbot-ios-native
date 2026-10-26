"""
Tree-sitter backed Kotlin/Java source index.

The index owns language-structure facts only: packages, classes, functions,
call sites, source ranges, and a small set of navigation call candidates. Higher
level extractors still interpret business DSLs and project-specific rules.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    from tree_sitter_language_pack import get_parser
except Exception:  # pragma: no cover - optional runtime dependency
    get_parser = None  # type: ignore[assignment]


_SKIP_CALLS = {
    "if",
    "for",
    "while",
    "when",
    "switch",
    "catch",
    "return",
    "throw",
    "super",
    "this",
    "class",
    "fun",
}


@dataclass
class AstProjectIndex:
    project_root: str
    file_prefix: str = ""
    ast_available: bool = False
    symbols: list[dict[str, Any]] = field(default_factory=list)
    calls: list[dict[str, Any]] = field(default_factory=list)
    unresolved_calls: list[dict[str, Any]] = field(default_factory=list)
    navigation_edges: list[dict[str, Any]] = field(default_factory=list)

    def find_enclosing_symbol(self, file_path: str, line: int) -> dict[str, Any] | None:
        norm = _norm_path(file_path)
        candidates = [
            s
            for s in self.symbols
            if _norm_path(s.get("file")) == norm
            and int(s.get("start_line", 0)) <= line <= int(s.get("end_line", 0))
        ]
        if not candidates:
            return None
        return sorted(
            candidates,
            key=lambda s: (int(s.get("end_line", 0)) - int(s.get("start_line", 0)), str(s.get("symbol_id"))),
        )[0]

    def calls_in_symbol(self, symbol_id: str) -> list[dict[str, Any]]:
        return [c for c in self.calls if c.get("from_symbol_id") == symbol_id]

    def calls_by_name(self, name: str) -> list[dict[str, Any]]:
        return [c for c in self.calls if c.get("callee_name") == name]


def _norm_path(value: Any) -> str:
    return str(value or "").replace("\\", "/")


def _source_files(root: Path) -> list[Path]:
    return sorted(list(root.rglob("src/main/**/*.java")) + list(root.rglob("src/main/**/*.kt")))


# Parsed-tree cache. A single pipeline run parses the same source files many times
# (build_class_hierarchy alone is called from navigation, source, fragment and
# validation paths; fragment_detector re-scans every file per detection mode). The
# tree-sitter parse is the dominant cost, so cache (source_bytes, root_node) keyed by
# (abspath, mtime_ns, size). Trees are immutable once parsed and only read, so reuse is
# safe. The tree object is held in the tuple to keep its nodes alive.
_PARSE_CACHE: dict[str, tuple[int, int, bytes, Any, Any]] = {}


def parse_file(src_path: Path) -> tuple[bytes, Any] | None:
    """Parse a Kotlin/Java source file, returning (source_bytes, root_node).

    Cached by path + mtime + size so repeated parses across extractors are free.
    Returns None when tree-sitter is unavailable or the file fails to parse.
    """
    if get_parser is None:
        return None
    language = _language_for(src_path)
    if not language:
        return None
    try:
        st = src_path.stat()
    except OSError:
        return None
    key = str(src_path)
    cached = _PARSE_CACHE.get(key)
    if cached is not None and cached[0] == st.st_mtime_ns and cached[1] == st.st_size:
        return cached[2], cached[3]
    try:
        parser = get_parser(language)
        source = src_path.read_bytes()
        tree = parser.parse(source.decode("utf-8"))
    except Exception:
        return None
    root_node = tree.root_node()
    # Keep `tree` referenced in the tuple so its nodes stay valid.
    _PARSE_CACHE[key] = (st.st_mtime_ns, st.st_size, source, root_node, tree)
    return source, root_node


def _rel_path(path: Path, root: Path, file_prefix: str = "") -> str:
    rel = path.relative_to(root).as_posix()
    return f"{file_prefix}/{rel}" if file_prefix else rel


def _language_for(path: Path) -> str:
    if path.suffix == ".kt":
        return "kotlin"
    if path.suffix == ".java":
        return "java"
    return ""


def _node_text(source: bytes, node: Any) -> str:
    return source[node.start_byte() : node.end_byte()].decode("utf-8", errors="ignore")


def _line(node: Any) -> int:
    return int(node.start_position().row) + 1


def _end_line(node: Any) -> int:
    return int(node.end_position().row) + 1


def _walk(node: Any):
    yield node
    for i in range(node.child_count()):
        child = node.child(i)
        yield from _walk(child)


def _first_named_child(node: Any, types: set[str]) -> Any | None:
    for i in range(node.named_child_count()):
        child = node.named_child(i)
        if child.kind() in types:
            return child
    return None


def _last_identifier_text(source: bytes, node: Any) -> str:
    names: list[str] = []
    for child in _walk(node):
        if child.kind() in {"identifier", "simple_identifier", "type_identifier"}:
            names.append(_node_text(source, child))
    return names[-1] if names else ""


def _package_name(source: bytes, root: Any, language: str) -> str:
    for i in range(root.named_child_count()):
        child = root.named_child(i)
        if language == "kotlin" and child.kind() == "package_header":
            simples = [_node_text(source, n) for n in _walk(child) if n.kind() == "simple_identifier"]
            if simples:
                return ".".join(simples)
            ident = _first_named_child(child, {"identifier"})
            return _node_text(source, ident) if ident is not None else ""
        if language == "java" and child.kind() == "package_declaration":
            names = [_node_text(source, n) for n in _walk(child) if n.kind() == "identifier"]
            return ".".join(names)
    return ""


def _owner_stack(source: bytes, node: Any, fallback: str) -> list[str]:
    owners: list[str] = []
    cur = node.parent()
    while cur is not None:
        if cur.kind() in {"class_declaration", "object_declaration", "interface_declaration", "enum_declaration"}:
            name = _class_name(source, cur)
            if name:
                owners.append(name)
        cur = cur.parent()
    return list(reversed(owners)) or [fallback]


def _class_name(source: bytes, node: Any) -> str:
    by_field = node.child_by_field_name("name")
    if by_field is not None:
        return _node_text(source, by_field)
    child = _first_named_child(node, {"type_identifier", "identifier", "simple_identifier"})
    return _node_text(source, child) if child is not None else ""


def _function_name(source: bytes, node: Any, language: str) -> str:
    by_field = node.child_by_field_name("name")
    if by_field is not None:
        return _node_text(source, by_field)
    if language == "kotlin":
        child = _first_named_child(node, {"simple_identifier", "identifier"})
        return _node_text(source, child) if child is not None else ""
    child = _first_named_child(node, {"identifier"})
    return _node_text(source, child) if child is not None else ""


def _signature(source: bytes, node: Any) -> str:
    params = node.child_by_field_name("parameters")
    if params is None:
        params = _first_named_child(node, {"function_value_parameters", "formal_parameters"})
    return " ".join(_node_text(source, params).strip("()").split()) if params is not None else ""


def _arity(signature: str) -> int:
    if not signature.strip():
        return 0
    depth = 0
    count = 1
    for ch in signature:
        if ch in "([{<":
            depth += 1
        elif ch in ")]}>":
            depth = max(0, depth - 1)
        elif ch == "," and depth == 0:
            count += 1
    return count


def _symbol_id(package: str, owners: list[str], function_name: str, signature: str) -> str:
    owner = ".".join([x for x in [package, *owners] if x])
    return f"fn:{owner}.{function_name}/{_arity(signature)}" if owner else f"fn:{function_name}/{_arity(signature)}"


def _is_function_node(node: Any) -> bool:
    return node.kind() in {"function_declaration", "method_declaration", "constructor_declaration"}


def _call_name(source: bytes, node: Any) -> str:
    if node.kind() == "method_invocation":
        name = node.child_by_field_name("name")
        return _node_text(source, name) if name is not None else _last_identifier_text(source, node)
    if node.kind() == "object_creation_expression":
        typ = node.child_by_field_name("type") or _first_named_child(node, {"type_identifier", "scoped_type_identifier"})
        return _last_identifier_text(source, typ) if typ is not None else ""
    if node.kind() == "call_expression":
        first = node.named_child(0) if node.named_child_count() > 0 else None
        return _last_identifier_text(source, first) if first is not None else ""
    return ""


def _call_arg_count(source: bytes, node: Any) -> int:
    args = node.child_by_field_name("arguments")
    if args is None:
        args = _first_named_child(node, {"value_arguments", "argument_list"})
    if args is None:
        return 0
    count = 0
    for i in range(args.named_child_count()):
        c = args.named_child(i)
        if c.kind() not in {",", "(", ")"}:
            count += 1
    return count


def _call_receiver(source: bytes, node: Any) -> str:
    if node.kind() != "call_expression" or node.named_child_count() == 0:
        return ""
    first = node.named_child(0)
    text = _node_text(source, first)
    if "." not in text:
        return ""
    return text.rsplit(".", 1)[0].strip()


def _symbol_for_call(caller: dict[str, Any], name: str, by_name: dict[str, list[dict[str, Any]]]) -> tuple[str, str]:
    candidates = by_name.get(name) or []
    if not candidates:
        return "", "unresolved"
    same_class = [s for s in candidates if s.get("class_name") == caller.get("class_name")]
    if len(same_class) == 1:
        return str(same_class[0]["symbol_id"]), "ast_same_class"
    if len(candidates) == 1:
        return str(candidates[0]["symbol_id"]), "ast_unique_name"
    return "", "ambiguous"


def _extract_target_class(text: str) -> str:
    for pattern in (
        r"\b([A-Z]\w*)::class(?:\.java)?",
        r"\b([A-Z]\w*(?:Activity|Fragment|Dialog|BottomSheet))\s*\(",
    ):
        m = re.search(pattern, text)
        if m:
            return m.group(1)
    return ""


def _is_dialog_like(name: str) -> bool:
    return bool(name and name[0].isupper() and re.search(r"(Dialog|DialogFragment|BottomSheet)$", name))


@dataclass
class ClassInfo:
    name: str
    package: str
    base_class: str | None
    interfaces: list[str]
    source_file: str
    language: str
    line: int = 0
    is_interface: bool = False

    @property
    def fqn(self) -> str:
        return f"{self.package}.{self.name}" if self.package else self.name


_ANDROID_FRAGMENT_BASES = {
    "Fragment", "DialogFragment", "BottomSheetDialogFragment",
    "PreferenceFragmentCompat", "ListFragment", "MapFragment",
    "SupportMapFragment", "PreferenceFragment", "AppCompatDialogFragment",
}

_ANDROID_ACTIVITY_BASES = {
    "Activity", "AppCompatActivity", "FragmentActivity", "ComponentActivity",
    "ListActivity", "PreferenceActivity",
}

_ANDROID_DIALOG_BASES = {
    "Dialog", "AlertDialog", "BottomSheetDialog",
}

_ANDROID_VIEW_BASES = {
    "View", "ViewGroup",
    "TextView", "EditText", "AutoCompleteTextView", "MultiAutoCompleteTextView",
    "Button", "ImageButton", "FloatingActionButton", "ToggleButton",
    "CompoundButton", "CheckBox", "RadioButton", "Switch", "SwitchCompat",
    "ImageView", "AppCompatImageView", "AppCompatImageButton",
    "LinearLayout", "FrameLayout", "RelativeLayout", "ConstraintLayout",
    "CoordinatorLayout", "DrawerLayout", "NestedScrollView",
    "RecyclerView", "ListView", "GridView", "ViewPager", "ViewPager2",
    "Toolbar", "MaterialToolbar", "AppBarLayout", "CollapsingToolbarLayout",
    "ProgressBar", "SeekBar", "RatingBar",
    "BottomNavigationView", "NavigationView", "TabLayout",
    "Spinner", "SearchView",
    "CardView", "Chip", "ChipGroup",
    "WebView", "SurfaceView", "TextureView",
    "ScrollView", "HorizontalScrollView",
    "RadioGroup", "TableLayout", "TableRow",
    "ViewStub", "ViewFlipper", "ViewSwitcher",
    "AdapterView", "AbsListView", "AbsSpinner",
    "CalendarView", "DatePicker", "TimePicker", "NumberPicker",
    "Space", "CheckedTextView",
}


def _extract_supertypes(source: bytes, class_node, language: str) -> tuple[str | None, list[str]]:
    """Extract (base_class, interfaces) from a class declaration AST node."""
    if language == "java":
        return _extract_supertypes_java(source, class_node)
    return _extract_supertypes_kotlin(source, class_node)


def _extract_supertypes_java(source: bytes, class_node) -> tuple[str | None, list[str]]:
    base_class = None
    superclass = class_node.child_by_field_name("superclass")
    if superclass is not None:
        for i in range(superclass.named_child_count()):
            child = superclass.named_child(i)
            if child.kind() in {"type_identifier", "identifier"}:
                base_class = _node_text(source, child)
                break
        if base_class is None:
            text = _node_text(source, superclass)
            for token in text.split():
                token = token.strip()
                if token and token not in ("extends", "implements") and token[0].isupper():
                    base_class = token.split("<")[0].split(".")[-1]
                    break

    interfaces: list[str] = []
    iface_node = class_node.child_by_field_name("interfaces")
    if iface_node is not None:
        for i in range(iface_node.named_child_count()):
            child = iface_node.named_child(i)
            if child.kind() in {"type_identifier", "identifier", "type_list"}:
                text = _node_text(source, child)
                name = text.split("<")[0].split(".")[-1].strip()
                if name:
                    interfaces.append(name)
    return base_class, interfaces


def _extract_supertypes_kotlin(source: bytes, class_node) -> tuple[str | None, list[str]]:
    # Kotlin: constructor_invocation = class inheritance, user_type = interface
    ctor_candidates: list[str] = []
    type_candidates: list[str] = []
    for child in _walk(class_node):
        if child.kind() != "delegation_specifier":
            continue
        for i in range(child.named_child_count()):
            sub = child.named_child(i)
            if sub.kind() == "constructor_invocation":
                text = _node_text(source, sub)
                name = text.split("(")[0].split("<")[0].split(".")[-1].strip()
                if name:
                    ctor_candidates.append(name)
            elif sub.kind() == "user_type":
                text = _node_text(source, sub)
                name = text.split("<")[0].split(".")[-1].strip()
                if name:
                    type_candidates.append(name)

    if ctor_candidates:
        base_class = ctor_candidates[0]
        interfaces = type_candidates + ctor_candidates[1:]
    elif type_candidates:
        base_class = type_candidates[0]
        interfaces = type_candidates[1:]
    else:
        # Fallback: super_type_list (older tree-sitter grammars)
        for child in _walk(class_node):
            if child.kind() == "super_type_list":
                for i in range(child.named_child_count()):
                    sub = child.named_child(i)
                    text = _node_text(source, sub)
                    name = text.split("(")[0].split("<")[0].split(".")[-1].strip()
                    if name:
                        return name, []
                break
        return None, []

    return base_class, interfaces


def lookup_class(hierarchy: dict[str, ClassInfo], short_name: str) -> ClassInfo | None:
    """Look up a class by short name in a FQN-keyed hierarchy."""
    if short_name in hierarchy:
        return hierarchy[short_name]
    suffix = f".{short_name}"
    for key, info in hierarchy.items():
        if key.endswith(suffix) or info.name == short_name:
            return info
    return None


def _resolve_android_base(kind: str, hierarchy: dict[str, ClassInfo],
                          visited: set[str] | None = None) -> str:
    """沿继承链上溯，返回 fragment / activity / dialog / other。"""
    if visited is None:
        visited = set()
    if kind in visited:
        return "other"
    visited.add(kind)

    info = hierarchy.get(kind) or lookup_class(hierarchy, kind)
    if info is not None and info.is_interface:
        return "interface"
    if info is None or info.base_class is None:
        return _guess_type_from_name(kind)

    base = info.base_class
    if base in _ANDROID_FRAGMENT_BASES:
        return "fragment"
    if base in _ANDROID_ACTIVITY_BASES:
        return "activity"
    if base in _ANDROID_DIALOG_BASES:
        return "dialog"
    return _resolve_android_base(base, hierarchy, visited)


def _guess_type_from_name(name: str) -> str:
    """Name-only fallback when the class is not in the hierarchy.

    Only applies to classes whose base class is unknown (e.g. from a
    library not in the scan). Uses conservative rules to avoid false
    positives like 'ActivityFragment' being classified as activity.
    """
    # Check the LAST meaningful suffix — "ActivityFragment" → fragment, not activity
    if name.endswith("DialogFragment") or name.endswith("BottomSheetDialogFragment"):
        return "fragment"
    if name.endswith("Fragment"):
        return "fragment"
    if name.endswith("Dialog") or name.endswith("BottomSheet"):
        return "dialog"
    if name.endswith("Activity"):
        return "activity"
    return "other"


def is_view_type(type_name: str, hierarchy: dict[str, ClassInfo] | None = None) -> bool:
    """Determine whether *type_name* is an Android View subclass."""
    if not type_name:
        return False
    short = type_name.split(".")[-1]
    if short in _ANDROID_VIEW_BASES:
        return True
    if hierarchy:
        info = lookup_class(hierarchy, short)
        if info is not None:
            return _is_view_in_chain(info, hierarchy, set())
    return False


def _is_view_in_chain(info: ClassInfo, hierarchy: dict[str, ClassInfo],
                      visited: set[str]) -> bool:
    if info.fqn in visited:
        return False
    visited.add(info.fqn)
    if info.name in _ANDROID_VIEW_BASES:
        return True
    if info.base_class:
        if info.base_class in _ANDROID_VIEW_BASES:
            return True
        base_info = lookup_class(hierarchy, info.base_class)
        if base_info is not None:
            return _is_view_in_chain(base_info, hierarchy, visited)
    return False


_HIERARCHY_CACHE: dict[tuple, dict[str, "ClassInfo"]] = {}


def build_class_hierarchy(
    project_root: str,
    dep_roots: list[str] | None = None,
    file_prefix: str = "",
) -> dict[str, ClassInfo]:
    """构建项目全量类索引，含继承关系。Key 为 FQN（package.ClassName）。

    Memoized per (project_root, dep_roots, file_prefix): the source tree does not
    change within a run, and this is called from several extractors.
    """
    cache_key = (str(project_root), tuple(dep_roots or ()), file_prefix)
    cached = _HIERARCHY_CACHE.get(cache_key)
    if cached is not None:
        return cached

    hierarchy: dict[str, ClassInfo] = {}
    roots: list[tuple[str, str]] = [(project_root, file_prefix)]
    if dep_roots:
        roots.extend((d, Path(d).name) for d in dep_roots)

    for root_path, prefix in roots:
        root = Path(root_path)
        for src_path in _source_files(root):
            language = _language_for(src_path)
            if language is None or not language:
                continue
            parsed = parse_file(src_path)
            if parsed is None:
                continue
            source, root_node = parsed
            rel = _rel_path(src_path, root, prefix)
            package = _package_name(source, root_node, language)
            for node in _walk(root_node):
                if node.kind() not in ("class_declaration", "object_declaration", "interface_declaration"):
                    continue
                name = _class_name(source, node)
                if not name:
                    continue
                fqn = f"{package}.{name}" if package else name
                base_class, interfaces = _extract_supertypes(source, node, language)
                hierarchy[fqn] = ClassInfo(
                    name=name,
                    package=package,
                    base_class=base_class,
                    interfaces=interfaces,
                    source_file=rel,
                    language=language,
                    line=_line(node),
                    is_interface=node.kind() == "interface_declaration",
                )
    _HIERARCHY_CACHE[cache_key] = hierarchy
    return hierarchy


def _layout_for_class(class_name: str, resolver: Any | None) -> str:
    if resolver:
        try:
            return str(resolver(class_name))
        except Exception:
            return ""
    return ""


def build_project_index(
    project_root: str,
    file_prefix: str = "",
    *,
    layout_resolver: Any | None = None,
) -> AstProjectIndex:
    index = AstProjectIndex(project_root=str(project_root), file_prefix=file_prefix)
    if get_parser is None:
        return index

    root = Path(project_root)
    file_roots: list[tuple[Path, bytes, str, str, Any]] = []
    for src_path in _source_files(root):
        language = _language_for(src_path)
        if not language:
            continue
        parsed = parse_file(src_path)
        if parsed is None:
            continue
        source, root_node = parsed
        rel = _rel_path(src_path, root, file_prefix)
        file_roots.append((src_path, source, language, rel, root_node))
        package = _package_name(source, root_node, language)
        fallback_owner = src_path.stem
        for node in _walk(root_node):
            if not _is_function_node(node):
                continue
            function_name = _function_name(source, node, language)
            if not function_name:
                continue
            signature = _signature(source, node)
            owners = _owner_stack(source, node, fallback_owner)
            symbol_id = _symbol_id(package, owners, function_name, signature)
            class_name = owners[-1] if owners else fallback_owner
            index.symbols.append(
                {
                    "symbol_id": symbol_id,
                    "kind": "function",
                    "language": language,
                    "package": package,
                    "class_name": class_name,
                    "owner_chain": owners,
                    "function_name": function_name,
                    "signature": signature,
                    "file": rel,
                    "start_line": _line(node),
                    "end_line": _end_line(node),
                    "confidence": "ast",
                }
            )

    by_name: dict[str, list[dict[str, Any]]] = {}
    by_file: dict[str, list[dict[str, Any]]] = {}
    for sym in index.symbols:
        by_name.setdefault(str(sym.get("function_name")), []).append(sym)
        by_file.setdefault(str(sym.get("file")), []).append(sym)

    seen_calls: set[tuple[str, str, int, str]] = set()
    for _src_path, source, _language, rel, root_node in file_roots:
        file_symbols = by_file.get(rel, [])
        for node in _walk(root_node):
            if node.kind() not in {"call_expression", "method_invocation", "object_creation_expression"}:
                continue
            callee_name = _call_name(source, node)
            if not callee_name or callee_name in _SKIP_CALLS:
                continue
            line = _line(node)
            caller = next(
                (
                    s
                    for s in file_symbols
                    if int(s.get("start_line", 0)) <= line <= int(s.get("end_line", 0))
                    and s.get("function_name") != callee_name
                ),
                None,
            )
            if caller is None:
                continue
            to_symbol, confidence = _symbol_for_call(caller, callee_name, by_name)
            if to_symbol:
                key = (str(caller["symbol_id"]), to_symbol, line, callee_name)
                if key not in seen_calls:
                    seen_calls.add(key)
                    index.calls.append(
                        {
                            "from_symbol_id": caller["symbol_id"],
                            "to_symbol_id": to_symbol,
                            "callee_name": callee_name,
                            "receiver": _call_receiver(source, node),
                            "argument_count": _call_arg_count(source, node),
                            "callsite_file": rel,
                            "callsite_line": line,
                            "confidence": confidence,
                        }
                    )
            else:
                index.unresolved_calls.append(
                    {
                        "from_symbol_id": caller["symbol_id"],
                        "callee_name": callee_name,
                        "receiver": _call_receiver(source, node),
                        "argument_count": _call_arg_count(source, node),
                        "callsite_file": rel,
                        "callsite_line": line,
                        "reason": confidence,
                    }
                )

            text = _node_text(source, node)
            from_class = str(caller.get("class_name") or "")
            trigger = f"fn: {caller.get('function_name')}"
            if callee_name in {"startActivity", "startActivityForResult"}:
                target = _extract_target_class(text)
                if target:
                    index.navigation_edges.append(
                        {
                            "from": from_class,
                            "to": target,
                            "to_layout": _layout_for_class(target, layout_resolver),
                            "type": "activity",
                            "via": f"{callee_name} [ast]",
                            "trigger": trigger,
                            "line": line,
                            "source_file": rel,
                            "source": "ast_index",
                            "confidence": "ast",
                        }
                    )
            elif _is_dialog_like(callee_name):
                index.navigation_edges.append(
                    {
                        "from": from_class,
                        "to": callee_name,
                        "to_layout": _layout_for_class(callee_name, layout_resolver),
                        "type": "dialog",
                        "via": "Dialog() [ast]",
                        "trigger": trigger,
                        "line": line,
                        "source_file": rel,
                        "source": "ast_index",
                        "confidence": "ast",
                    }
                )

    index.ast_available = bool(index.symbols)
    index.symbols.sort(key=lambda s: (s["file"], s["start_line"], s["symbol_id"]))
    index.calls.sort(key=lambda c: (c["callsite_file"], c["callsite_line"], c["from_symbol_id"], c["callee_name"]))
    index.unresolved_calls.sort(key=lambda c: (c["callsite_file"], c["callsite_line"], c["from_symbol_id"], c["callee_name"]))
    return index


def symbols_payload(index: AstProjectIndex) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "symbols": index.symbols,
        "stats": {
            "source_files_scanned": len(_source_files(Path(index.project_root))),
            "symbol_count": len(index.symbols),
            "ast_symbol_count": sum(1 for s in index.symbols if s.get("confidence") == "ast"),
        },
    }


def call_graph_payload(index: AstProjectIndex) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "symbols": index.symbols,
        "calls": index.calls,
        "unresolved_calls": index.unresolved_calls,
        "stats": {
            "symbol_count": len(index.symbols),
            "call_count": len(index.calls),
            "unresolved_call_count": len(index.unresolved_calls),
            "ast_call_count": sum(1 for c in index.calls if str(c.get("confidence", "")).startswith("ast")),
        },
    }


# ── Variable type extraction (for receiver type annotation) ────

_KT_VAR_RE = re.compile(r'(?:val|var)\s+(\w+)')


def extract_variable_types(source: bytes, root_node, language: str) -> dict[str, str]:
    """Build {var_name: type_name} from declarations and parameters in the file."""
    types: dict[str, str] = {}
    for node in _walk(root_node):
        if language == "kotlin":
            if node.kind() == "property_declaration":
                _collect_kotlin_prop_type(source, node, types)
            elif node.kind() == "parameter":
                _collect_param_type(source, node, language, types)
        elif language == "java":
            if node.kind() in ("local_variable_declaration", "field_declaration"):
                _collect_java_decl_type(source, node, types)
            elif node.kind() == "formal_parameter":
                _collect_param_type(source, node, language, types)
    return types


def _collect_kotlin_prop_type(source: bytes, node, types: dict):
    text = _node_text(source, node)
    m = _KT_VAR_RE.search(text)
    if not m:
        return
    name = m.group(1)

    eq_pos = text.find("=")
    decl_part = text[:eq_pos] if eq_pos > 0 else text

    type_m = re.search(r":\s*([\w.]+)", decl_part)
    if type_m:
        types[name] = type_m.group(1).split(".")[-1]
        return

    if eq_pos < 0:
        return
    init = text[eq_pos + 1 :]

    fvb = re.search(r"findViewById\s*<\s*(\w+)", init)
    if fvb:
        types[name] = fvb.group(1)
        return

    ctor = re.search(r"^\s*([A-Z]\w*)\s*[.(]", init)
    if ctor:
        types[name] = ctor.group(1)
        return


def _collect_java_decl_type(source: bytes, node, types: dict):
    type_node = node.child_by_field_name("type")
    if type_node is None:
        type_node = _first_named_child(
            node, {"type_identifier", "generic_type", "scoped_type_identifier"}
        )
    if type_node is None:
        return
    type_text = _node_text(source, type_node).split("<")[0].split(".")[-1].strip()
    if not type_text:
        return
    for i in range(node.named_child_count()):
        child = node.named_child(i)
        if child.kind() == "variable_declarator":
            name_node = child.child_by_field_name("name")
            if name_node is None:
                name_node = _first_named_child(child, {"identifier"})
            if name_node is not None:
                types[_node_text(source, name_node)] = type_text


def _collect_param_type(source: bytes, node, language: str, types: dict):
    if language == "kotlin":
        name_node = _first_named_child(node, {"simple_identifier"})
        type_node = _first_named_child(node, {"user_type"})
    else:
        name_node = node.child_by_field_name("name")
        if name_node is None:
            name_node = _first_named_child(node, {"identifier"})
        type_node = node.child_by_field_name("type")
        if type_node is None:
            type_node = _first_named_child(node, {"type_identifier", "generic_type"})

    if name_node is not None and type_node is not None:
        var_name = _node_text(source, name_node)
        type_text = _node_text(source, type_node).split("<")[0].split(".")[-1].strip()
        if type_text:
            types[var_name] = type_text
