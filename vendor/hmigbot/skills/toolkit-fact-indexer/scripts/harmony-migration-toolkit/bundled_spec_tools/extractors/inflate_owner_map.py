"""
inflate_owner_map.py

Derive a deterministic class → layout mapping from layout-inflation sites.

The class that inflates a layout (`inflater.inflate(R.layout.foo, ...)` or
`FooBinding.inflate(...)`) is the strongest possible signal of layout ownership —
stronger than name heuristics. Navigation analysis misses screens that are never
the target of an explicit Intent/transaction (helper fragments, recycler adapters,
sub-dialogs), leaving their layouts with no owning class. This module recovers
those mappings by joining `source_findings.inflates` (which carry
`enclosing_symbol_id`) with the call-graph symbol table (which resolves a symbol
to its `class_name`).

Pure function over already-extracted artifacts — no source rescan.
"""
from __future__ import annotations

from collections import defaultdict


def build_inflate_class_layouts(
    source_findings: dict,
    call_graph: dict,
) -> dict[str, list[str]]:
    """Return {class_name: [layout, ...]} derived from inflate sites.

    Layouts are sorted for determinism. A class may inflate several layouts
    (e.g. a fragment that also shows a sub-dialog).
    """
    symbols_by_id = {
        s.get("symbol_id", ""): s
        for s in call_graph.get("symbols", [])
        if s.get("symbol_id")
    }

    class_layouts: dict[str, set[str]] = defaultdict(set)
    for inf in source_findings.get("findings", {}).get("inflates", []):
        layout = inf.get("layout", "")
        sym_id = inf.get("enclosing_symbol_id", "")
        if not layout or not sym_id:
            continue
        cls = symbols_by_id.get(sym_id, {}).get("class_name", "")
        if not cls:
            continue
        class_layouts[cls].add(layout)

    return {cls: sorted(layouts) for cls, layouts in class_layouts.items()}


def merge_into_nav(nav: dict, inflate_class_layouts: dict[str, list[str]]) -> int:
    """Merge inflate-derived mappings into the navigation graph's `class_layouts`.

    Only fills classes that have no mapping yet, so navigation-derived ownership
    stays authoritative. A 1:1 primary mapping is deliberate: it flows through the
    existing `class_layouts` consumers (layout_to_classes, class_to_layout_set,
    screen_type inference) without over-claiming chains into multiple specs when a
    class happens to inflate several layouts.

    Returns the number of newly added primary mappings.
    """
    primary = nav.setdefault("class_layouts", {})
    added = 0
    for cls, layouts in inflate_class_layouts.items():
        if not layouts or cls in primary:
            continue
        primary[cls] = layouts[0]
        added += 1
    return added
