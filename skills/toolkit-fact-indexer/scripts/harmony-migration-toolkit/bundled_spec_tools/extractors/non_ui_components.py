"""Group orphan behavior-chains by their owning non-UI class.

A behavior chain is an "orphan" when no screen spec can claim it (see
generate_specs.py). Most orphans are not screens at all — background services,
app-widget providers, broadcast receivers, sensor/scroll listeners, playback
infrastructure. They still carry real functionality that must be migrated, so
this module routes them to a component-level model tagged with a HarmonyOS
ability hint, instead of forcing them onto an unrelated screen.

Classification is deterministic and records its source for audit:
  1. AndroidManifest declaration  (authoritative, always present)
  2. compiled .class super chain   (if the project was built)
  3. class-name suffix heuristic   (last resort, tagged name_heuristic)

Adapters are UI (they render item layouts), so adapter-kind orphans are
excluded here and left for the screen/item-layout path.

Each component is also linked back to the rest of the app so it is not a
free-floating mapping target. Using the call graph (exact class-name match on
the callee), every component records ``used_by`` — the caller classes that
construct or invoke it — and marks which of those callers are screens (present
in the navigation class→layout map). For the reverse direction,
``inject_screen_backrefs`` writes a ``non_ui_dependencies`` note into each
affected screen spec, so the agent translating a screen also sees which non-UI
components that screen drives.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

HARMONY_ABILITY_HINT = {
    "service": "ServiceExtensionAbility (+ AVSession for media playback)",
    "appwidget_provider": "FormExtensionAbility (service widget / card)",
    "broadcast_receiver": "CommonEventSubscriber / background task",
    "provider": "DataShareExtensionAbility",
    "listener": "host-attached event/sensor API (no standalone ability)",
    "view_helper": "supporting class — migrate with its owner",
    "other": "supporting class — migrate with its owner",
}

# super-class name fragments → kind (first match while walking the chain wins).
# activity is tested before fragment so FragmentActivity resolves to activity.
_BYTECODE_BASE_KIND = [
    ("service", ("Service", "MediaBrowserService", "MediaLibraryService", "MediaSessionService")),
    ("appwidget_provider", ("AppWidgetProvider",)),
    ("broadcast_receiver", ("BroadcastReceiver",)),
    ("activity", ("Activity",)),
    ("fragment", ("Fragment",)),
    ("adapter", ("Adapter", "ViewHolder")),
    ("listener", ("Listener", "Callback", "Observer")),
    ("view_helper", ("ViewGroup", "View", "Layout")),
]

# class-name suffix → kind (last-resort heuristic; appwidget intentionally omitted
# — only the manifest can reliably tell a real AppWidgetProvider from a helper).
_NAME_KIND = [
    ("service", ("Service",)),
    ("broadcast_receiver", ("Receiver",)),
    ("provider", ("Provider",)),
    ("activity", ("Activity",)),
    ("fragment", ("Fragment",)),
    ("adapter", ("Adapter", "ViewHolder")),
    ("listener", ("Listener",)),
    ("view_helper", ("View",)),
]

# kinds that are actually UI — excluded from the non-UI artifact and left for the
# screen / item-layout path.
_UI_KINDS = {"activity", "fragment", "adapter"}


def _walk_bytecode(name: str, hier: dict[str, str | None]) -> str | None:
    """Return a kind by walking ``name``'s super chain, or None if unresolved."""
    if name not in hier:
        return None
    seen: set[str] = set()
    cur: str | None = name
    while cur and cur not in seen:
        seen.add(cur)
        sup = hier.get(cur)
        if sup is None:
            break
        for kind, frags in _BYTECODE_BASE_KIND:
            if any(f in sup for f in frags):
                return kind
        cur = sup
    return None


def _classify(cls: str, manifest_components: dict, bc_hierarchy: dict) -> tuple[str, str]:
    decl = manifest_components.get(cls)
    if decl:
        return decl["kind"], "manifest"
    bc_kind = _walk_bytecode(cls, bc_hierarchy)
    if bc_kind:
        return bc_kind, "bytecode"
    for kind, frags in _NAME_KIND:
        if any(f in cls for f in frags):
            return kind, "name_heuristic"
    return "other", "name_heuristic"


def _inbound_callers(call_graph: dict) -> dict[str, set[str]]:
    """Map each callee class to the set of caller classes that invoke it.

    Uses exact class-name match on the call graph symbols (the same short-name
    space the rest of the toolkit uses, e.g. navigation class_layouts), so a
    component is linked only to classes that genuinely call into it.
    """
    symbols = call_graph.get("symbols") or []
    id_to_class = {s.get("symbol_id"): s.get("class_name", "") for s in symbols}
    inbound: dict[str, set[str]] = defaultdict(set)
    for c in call_graph.get("calls") or []:
        tcls = id_to_class.get(c.get("to_symbol_id"))
        fcls = id_to_class.get(c.get("from_symbol_id"))
        if tcls and fcls and tcls != fcls:
            inbound[tcls].add(fcls)
    return inbound


def _used_by(cls: str, inbound: dict[str, set[str]], class_layouts: dict) -> list[dict]:
    """List the caller classes of ``cls``, marking which are screens.

    Screens (callers present in ``class_layouts``) are listed first and carry
    their layout id, giving a deterministic bridge from the non-UI component back
    to the screens that drive it. An empty list is meaningful: no static caller
    (e.g. a framework-driven widget updater), not an inference gap to paper over.
    """
    entries: list[dict] = []
    for fc in sorted(inbound.get(cls, set())):
        entry = {"class": fc, "is_screen": fc in class_layouts}
        if entry["is_screen"]:
            entry["screen"] = class_layouts[fc]
        entries.append(entry)
    entries.sort(key=lambda e: (not e["is_screen"], e["class"]))
    return entries


def build(orphan_chains: list[dict], manifest_components: dict,
          bc_hierarchy: dict | None = None, call_graph: dict | None = None,
          class_layouts: dict | None = None) -> dict:
    """Build the non_ui_components artifact from orphan behavior chains."""
    bc_hierarchy = bc_hierarchy or {}
    class_layouts = class_layouts or {}
    inbound = _inbound_callers(call_graph) if call_graph else {}

    groups: dict[str, list[dict]] = defaultdict(list)
    unclassified = 0
    for ch in orphan_chains:
        cls = (ch.get("handler") or {}).get("class", "")
        if cls:
            groups[cls].append(ch)
        else:
            unclassified += 1

    components: list[dict] = []
    excluded_ui: Counter = Counter()
    by_kind: Counter = Counter()
    by_source: Counter = Counter()
    screen_links = 0
    components_with_callers = 0
    for cls in sorted(groups):
        chains = groups[cls]
        kind, source = _classify(cls, manifest_components, bc_hierarchy)
        if kind in _UI_KINDS:
            excluded_ui[kind] += len(chains)
            continue
        source_file = ""
        for ch in chains:
            f = (ch.get("handler") or {}).get("file", "")
            if f:
                source_file = f
                break
        used_by = _used_by(cls, inbound, class_layouts)
        if used_by:
            components_with_callers += 1
        screen_links += sum(1 for u in used_by if u["is_screen"])
        components.append({
            "component_class": cls,
            "kind": kind,
            "kind_source": source,
            "harmony_ability_hint": HARMONY_ABILITY_HINT.get(kind, HARMONY_ABILITY_HINT["other"]),
            "source_file": source_file,
            "used_by": used_by,
            "behaviors": chains,
        })
        by_kind[kind] += len(chains)
        by_source[source] += len(chains)

    components.sort(key=lambda c: (c["kind"], c["component_class"]))

    return {
        "non_ui_components": components,
        "stats": {
            "components": len(components),
            "behaviors": sum(len(c["behaviors"]) for c in components),
            "by_kind": dict(sorted(by_kind.items())),
            "by_kind_source": dict(sorted(by_source.items())),
            "excluded_ui_chains": dict(sorted(excluded_ui.items())),
            "unclassified_orphan_chains": unclassified,
            "components_with_callers": components_with_callers,
            "screen_links": screen_links,
        },
    }


def inject_screen_backrefs(non_ui: dict, specs_dir: Path | str) -> dict:
    """Write a ``non_ui_dependencies`` note into each screen spec a component drives.

    The forward direction (component → screens) lives in each component's
    ``used_by``; this adds the reverse so the agent translating a screen sees
    which non-UI components it depends on. Returns link stats. Specs are
    regenerated fresh each run, so notes never accumulate.

    Reverse resolution is authoritative and deterministic: a caller class is
    linked to a screen spec only when that spec's own ``class`` field equals the
    caller class. The navigation layout id is not used here because it can differ
    from the spec's layout (e.g. ``audio_player_fragment`` vs
    ``audioplayer_fragment``); a caller that does not match a spec's class is left
    unlinked rather than fuzzily guessed.
    """
    specs_dir = Path(specs_dir)
    class_to_spec: dict[str, Path] = {}
    for sp in sorted(specs_dir.glob("*_spec.json")):
        try:
            data = json.loads(sp.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            continue
        cls = data.get("class")
        if cls:
            class_to_spec.setdefault(cls, sp)

    by_spec: dict[Path, dict[str, dict]] = defaultdict(dict)
    for comp in non_ui.get("non_ui_components", []):
        dep = {
            "component_class": comp["component_class"],
            "kind": comp["kind"],
            "harmony_ability_hint": comp["harmony_ability_hint"],
        }
        for u in comp.get("used_by", []):
            sp = class_to_spec.get(u.get("class"))
            if sp is not None:
                by_spec[sp][dep["component_class"]] = dep

    backref_edges = 0
    for sp, deps in by_spec.items():
        data = json.loads(sp.read_text(encoding="utf-8"))
        data["non_ui_dependencies"] = sorted(
            deps.values(), key=lambda d: (d["kind"], d["component_class"]))
        sp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        backref_edges += len(deps)

    return {"screen_specs_linked": len(by_spec), "backref_edges": backref_edges}
