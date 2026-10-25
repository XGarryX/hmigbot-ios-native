"""
containment_linker.py
Build *containment* edges so the reachable-screen DAG sees Fragment- and
bottom-nav-hosted screens, not only Activity `startActivity` jumps.

Background: the navigation graph models screen transitions discovered from
`startActivity`/Intent analysis. Apps whose main navigation is Fragment- or
bottom-nav-based (a host shows its tabs by swapping Fragments, never calling
startActivity) end up with a hub Activity that has almost no out-edges, so a BFS
from the launcher dead-ends there. The hosted screens are all extracted (they are
in fragments.json / app_model), they are simply not *linked* to their host.

This module adds two deterministic containment links — every edge is backed by a
concrete source site or layout tag, never inferred:

  (a) host → fragment      from fragments.json; the host class is resolved from an
                           inner class to its outermost enclosing class so an
                           adapter/inner helper (e.g. `NavAdapter`) is attributed
                           to the real screen/view that declares it
                           (`WPMainNavigationView`).
  (b) screen → custom-view when a fragment-hosting custom View appears as a tag in
                           that screen's layout (from static_xml elements). This
                           bridges Activity → custom bottom-nav View → its tabs.

Only custom Views that actually host Fragments are linked in (b), so unrelated
views never become spurious screen nodes.
"""
from pathlib import Path

from extractors.ast_index import (
    parse_file as _ast_parse_file,
    _walk as _ast_walk,
    _class_name as _ast_class_name,
    _source_files as _ast_source_files,
    _language_for as _ast_language_for,
)

_CLASS_KINDS = {"class_declaration", "object_declaration"}


def _build_inner_to_outer(project_root: str, dep_roots: list[str] | None,
                          file_prefix: str) -> dict[str, str]:
    """Map every nested class name → its outermost (top-level) enclosing class.

    Top-level classes are not included (they map to themselves implicitly).
    """
    mapping: dict[str, str] = {}
    roots = [(project_root, file_prefix)]
    if dep_roots:
        roots.extend((d, Path(d).name) for d in dep_roots)
    for root_path, _prefix in roots:
        root = Path(root_path)
        for src_path in _ast_source_files(root):
            if not _ast_language_for(src_path):
                continue
            parsed = _ast_parse_file(src_path)
            if parsed is None:
                continue
            source, root_node = parsed
            for node in _ast_walk(root_node):
                if node.kind() not in _CLASS_KINDS:
                    continue
                name = _ast_class_name(source, node)
                if not name:
                    continue
                outer = name
                cur = node.parent()
                while cur is not None:
                    if cur.kind() in _CLASS_KINDS:
                        nm = _ast_class_name(source, cur)
                        if nm:
                            outer = nm
                    cur = cur.parent()
                if outer != name:
                    mapping[name] = outer
    return mapping


def _layout_of(cls: str, nodes: dict, class_layouts: dict) -> str:
    node = nodes.get(cls)
    if node and node.get("layout"):
        return node["layout"]
    return class_layouts.get(cls, "")


def _type_of(cls: str, nodes: dict, default: str) -> str:
    node = nodes.get(cls)
    if node and node.get("type"):
        return node["type"]
    return default


def build_containment_edges(nav_graph: dict, fragments: list[dict],
                            static_xml: dict, project_root: str,
                            dep_roots: list[str] | None = None,
                            file_prefix: str = "") -> list[dict]:
    """Return new containment edges to merge into nav_graph['edges'].

    Edges use the same schema as navigation edges
    ({from, to, to_layout, type, via, trigger, line}) so the DAG assembler and
    app_model consume them unchanged. `via` is `fragment_host` / `custom_view_host`
    so downstream can tell containment from real navigation.
    """
    nodes = nav_graph.get("nodes", {})
    class_layouts = nav_graph.get("class_layouts", {})
    inner2outer = _build_inner_to_outer(project_root, dep_roots, file_prefix)

    def root_of(c: str) -> str:
        return inner2outer.get(c, c)

    # layout → owning screen classes
    layout_to_screens: dict[str, set[str]] = {}
    for cname, node in nodes.items():
        lay = node.get("layout", "")
        if lay:
            layout_to_screens.setdefault(lay, set()).add(cname)
    for cname, lay in class_layouts.items():
        if lay:
            layout_to_screens.setdefault(lay, set()).add(cname)

    existing = {(e["from"], e["to"]) for e in nav_graph.get("edges", [])}
    new_edges: list[dict] = []

    # (a) host_root → fragment. Also record which classes host fragments so (b)
    #     only links custom Views that are real hosts.
    host_roots: set[str] = set()
    for fr in fragments:
        host = fr.get("host_class", "")
        cls = fr.get("class", "")
        if not host or not cls:
            continue
        hr = root_of(host)
        host_roots.add(hr)
        if hr == cls or (hr, cls) in existing:
            continue
        existing.add((hr, cls))
        new_edges.append({
            "from": hr,
            "to": cls,
            "to_layout": _layout_of(cls, nodes, class_layouts),
            "type": _type_of(cls, nodes, "fragment"),
            "via": "fragment_host",
            "trigger": f"hosts fragment ({fr.get('attach_method', '')})",
            "line": fr.get("line", 0),
        })

    # (b) screen → custom-view host (a fragment-hosting custom View embedded in the
    #     screen's layout). static_xml stores the view's last-segment name as `tag`.
    for el in static_xml.get("elements", []):
        view_cls = el.get("tag", "")
        lay = el.get("layout", "")
        if not view_cls or not lay or view_cls not in host_roots:
            continue
        for screen in layout_to_screens.get(lay, ()):
            if screen == view_cls or (screen, view_cls) in existing:
                continue
            existing.add((screen, view_cls))
            new_edges.append({
                "from": screen,
                "to": view_cls,
                "to_layout": _layout_of(view_cls, nodes, class_layouts),
                "type": _type_of(view_cls, nodes, "container"),
                "via": "custom_view_host",
                "trigger": f"layout {lay} embeds host view",
                "line": 0,
            })

    return new_edges


def merge_into_nav(nav_graph: dict, fragments: list[dict], static_xml: dict,
                   project_root: str, dep_roots: list[str] | None = None,
                   file_prefix: str = "") -> dict:
    """Append containment edges to nav_graph in place and update node back-refs.

    Returns a small stats dict: {added, by_via}.
    """
    new_edges = build_containment_edges(
        nav_graph, fragments, static_xml, project_root, dep_roots, file_prefix
    )
    edges = nav_graph.setdefault("edges", [])
    nodes = nav_graph.get("nodes", {})
    by_via: dict[str, int] = {}
    for e in new_edges:
        edges.append(e)
        by_via[e["via"]] = by_via.get(e["via"], 0) + 1
        # keep node navigates_to/navigated_from back-refs consistent when both ends
        # are known nodes (the DAG reads edges, but app_model and reports read these)
        src, dst = e["from"], e["to"]
        if src in nodes:
            lst = nodes[src].setdefault("navigates_to", [])
            if dst not in lst:
                lst.append(dst)
            nodes[src]["edges_out"] = nodes[src].get("edges_out", 0) + 1
        if dst in nodes:
            lst = nodes[dst].setdefault("navigated_from", [])
            if src not in lst:
                lst.append(src)
            nodes[dst]["edges_in"] = nodes[dst].get("edges_in", 0) + 1
    return {"added": len(new_edges), "by_via": by_via}
