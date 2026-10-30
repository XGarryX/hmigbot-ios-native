"""EtsRefGraph — Project-wide reference graph.

Nodes: .ets files
Edges:
  - import:        importer → imported file
  - instantiation: file → class (resolved across imports to find owner file)

Orphan detection: given a set of candidate "VM/Repo" files, check that each
exported class has at least one UI file (page/component/widget) that
imports + instantiates it.
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

from .ets_parser import EtsFileInfo, parse_ets_file
from .import_resolver import resolve_import_path


_UI_PATH_HINTS = ("/pages/", "/components/", "/widgets/", "/views/", "/dialogs/", "/dialog/")
# Symmetric matcher for Windows backslashes
_UI_PATH_HINTS_BS = tuple(p.replace("/", "\\") for p in _UI_PATH_HINTS)

# Type-level exports: consumed via member access (Enum.Member) or type position
# (`: IFoo`), never via `new X(` — instantiation-based orphan checks don't apply.
# (Known-FP class: enums like HomeUiState flagged IMPORTED_BUT_NOT_INSTANTIATED.)
_TYPE_LEVEL_KINDS = ("enum", "interface")


@dataclass
class OrphanFinding:
    file: str               # repo-relative path of the orphan VM/Repo file
    class_name: str
    reason: str             # NO_IMPORTER | IMPORTED_BUT_NOT_INSTANTIATED | ONLY_INSTANTIATED_BY_VMS
    importers: list[str] = field(default_factory=list)
    instantiators: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


class EtsRefGraph:
    def __init__(self, project_root: Path, skip_parts: Optional[set[str]] = None):
        self.project_root = project_root.resolve()
        self.skip_parts = skip_parts or {"oh_modules", "node_modules", "build", ".cxx", ".preview", ".claude", ".agents", ".codex"}
        self.files: list[Path] = []
        self.info: dict[Path, EtsFileInfo] = {}
        # class_name → set of files that export it
        self.export_index: dict[str, set[Path]] = {}
        # class_name → set of files that instantiate it
        self.instantiator_index: dict[str, set[Path]] = {}
        # importer_file → set of (imported_file, named_set)
        self.import_edges: dict[Path, list[dict]] = {}
        # path → comment-stripped source text (lazy cache for usage_evidence)
        self._text_cache: dict[Path, str] = {}

    # ─── Build ───────────────────────────────────────────────────────────────
    def build(self) -> "EtsRefGraph":
        # 1. Discover .ets files (pruned walk — rglob would descend into
        #    oh_modules/build before filtering)
        import sys as _sys
        _scripts_dir = str(Path(__file__).resolve().parent.parent)
        if _scripts_dir not in _sys.path:
            _sys.path.insert(0, _scripts_dir)
        from fswalk import walk_files
        self.files = walk_files(self.project_root, ".ets", self.skip_parts)

        # 2. Parse each
        for f in self.files:
            self.info[f] = parse_ets_file(f)

        # 3. Build export & instantiator indexes
        for f, info in self.info.items():
            for cls in info.exports:
                self.export_index.setdefault(cls, set()).add(f)
            for cls in info.instantiations:
                self.instantiator_index.setdefault(cls, set()).add(f)

        # 4. Resolve import edges to actual file paths
        for f, info in self.info.items():
            edges = []
            for imp in info.imports:
                src = imp.get("src", "")
                resolved = resolve_import_path(src, f, self.project_root)
                if resolved is not None:
                    edges.append({
                        "target": resolved,
                        "names": imp.get("names") or ([imp["name"]] if imp.get("name") else []),
                        "kind": imp["kind"],
                    })
            self.import_edges[f] = edges

        return self

    # ─── Queries ─────────────────────────────────────────────────────────────
    def importers_of(self, target_file: Path) -> list[Path]:
        """Files that have an `import ... from <target>` edge."""
        target = target_file.resolve()
        return [f for f, edges in self.import_edges.items()
                if any(e["target"] == target for e in edges)]

    def importers_of_class(self, class_name: str) -> list[Path]:
        """Files whose import names include `class_name` from a file that exports it."""
        out: list[Path] = []
        exporting_files = self.export_index.get(class_name, set()) | {
            f for f, info in self.info.items() if class_name in info.reexports
        }
        if not exporting_files:
            return out
        for f, edges in self.import_edges.items():
            for e in edges:
                if e["target"] in exporting_files and (
                    not e["names"] or class_name in e["names"]
                    or e["kind"] in ("ns", "default")
                ):
                    out.append(f)
                    break
        return out

    def instantiators_of_class(self, class_name: str) -> list[Path]:
        return list(self.instantiator_index.get(class_name, set()))

    # ─── Orphan detection ────────────────────────────────────────────────────
    def find_orphans(self, candidate_files: list[Path]) -> list[OrphanFinding]:
        """For each candidate (typically VM/Repo file), check every exported
        class for: at-least-one importer AND at-least-one instantiator AND
        at-least-one UI-wired instantiator.

        Exemptions (known false-positive classes, see pokedex retrospective):
        - enum / interface exports: type-level, consumed via member access or
          type position — `new`-based checks don't apply, skipped entirely.
        - self-consumed helper: a class instantiated/typed-ref'd inside its own
          defining file (e.g. UI-state class built by static factories) is not
          an orphan when its defining file is itself UI-wired.
        - transitive instantiation: the "UI-layer instantiator" check accepts
          UI-*reachable* files (Repo instantiated by a VM that a page
          instantiates counts as wired), not only direct /pages|components/.
        """
        results: list[OrphanFinding] = []
        ui_reach = self._ui_reachable_files()
        for vm_file in candidate_files:
            vm_file = vm_file.resolve()
            info = self.info.get(vm_file)
            if info is None:
                continue
            exported = info.exports
            if not exported:
                continue

            for cls in exported:
                # Exemption 1: type-level exports (enum / interface)
                if info.export_kinds.get(cls) in _TYPE_LEVEL_KINDS:
                    continue

                # Exemption 2: self-consumed helper in a UI-wired file
                self_use = cls in info.instantiations or cls in info.typed_refs
                if self_use and vm_file in ui_reach:
                    continue

                importers = self.importers_of_class(cls)
                # Exclude self-import edge cases
                importers = [i for i in importers if i != vm_file]

                if not importers:
                    results.append(OrphanFinding(
                        file=self._rel(vm_file),
                        class_name=cls,
                        reason="NO_IMPORTER",
                    ))
                    continue

                instantiators = self.instantiators_of_class(cls)
                instantiators = [i for i in instantiators if i != vm_file]

                # Allow @Param/@Local typed-ref to count toward "in use"
                typed_ref_files = [
                    f for f, fi in self.info.items()
                    if cls in fi.typed_refs and f != vm_file
                ]

                if not instantiators and not typed_ref_files:
                    results.append(OrphanFinding(
                        file=self._rel(vm_file),
                        class_name=cls,
                        reason="IMPORTED_BUT_NOT_INSTANTIATED",
                        importers=[self._rel(p) for p in importers],
                    ))
                    continue

                # Check UI-wired instantiator (Exemption 3: transitive closure —
                # an instantiator counts if it is a UI file OR is itself
                # instantiated by a UI-reachable file, e.g. Page→VM→Repo).
                ui_instantiators = [
                    p for p in instantiators + typed_ref_files
                    if p in ui_reach
                ]
                if not ui_instantiators and (instantiators or typed_ref_files):
                    results.append(OrphanFinding(
                        file=self._rel(vm_file),
                        class_name=cls,
                        reason="ONLY_INSTANTIATED_BY_NON_UI",
                        instantiators=[self._rel(p) for p in instantiators + typed_ref_files],
                    ))

        return results

    def _ui_reachable_files(self) -> set[Path]:
        """Files transitively wired to the UI layer.

        Seed: files under a UI path hint (/pages|components|widgets|views|dialogs/).
        Closure: a file joins the set when any class it exports is instantiated
        (or typed-ref'd) by a file already in the set. This models the
        Page → ViewModel → Repository/Callbacks instantiation chain so that
        deep-layer classes instantiated by a UI-wired VM are not flagged
        ONLY_INSTANTIATED_BY_NON_UI (known false-positive class).
        """
        reach: set[Path] = {f for f in self.files if self._is_ui_file(f)}
        changed = True
        while changed:
            changed = False
            for f, info in self.info.items():
                if f in reach:
                    continue
                for cls in info.exports:
                    users = set(self.instantiator_index.get(cls, set())) | {
                        uf for uf, fi in self.info.items() if cls in fi.typed_refs
                    }
                    users.discard(f)
                    if users & reach:
                        reach.add(f)
                        changed = True
                        break
        return reach

    def find_orphan_components(self, candidate_files: list[Path]) -> list[OrphanFinding]:
        """Component-struct inbound check (E1: Fragment/child-page inbound edge).

        UI components are rendered via `Foo()` (not `new`), so the VM
        instantiation checks don't apply. The one reliable orphan signal for a
        component is NO_IMPORTER: ArkUI requires an `import` to reference a
        component, so a /components|views|widgets|dialogs/ struct that no other .ets file
        imports is never embedded anywhere. Only NO_IMPORTER is emitted — an
        imported-but-render-invoked component has an importer and is NOT flagged,
        so there is no false-positive on legitimately-embedded components.
        """
        results: list[OrphanFinding] = []
        for comp_file in candidate_files:
            comp_file = comp_file.resolve()
            info = self.info.get(comp_file)
            if info is None or not info.exports:
                continue
            for cls in info.exports:
                if info.export_kinds.get(cls) in _TYPE_LEVEL_KINDS:
                    continue   # enum/interface exported alongside a struct — type-level
                importers = [i for i in self.importers_of_class(cls) if i != comp_file]
                if not importers:
                    results.append(OrphanFinding(
                        file=self._rel(comp_file),
                        class_name=cls,
                        reason="NO_IMPORTER",
                    ))
        return results

    def find_unrendered_components(self, candidate_files: list[Path]) -> list[OrphanFinding]:
        """E1 residual (WARN, non-blocking): a component IMPORTED by some file but never
        used as a `Name(` call anywhere (not rendered, not new'd, not a typed @Param/@Local).
        Distinct from NO_IMPORTER. Heuristic — a component rendered indirectly (assigned to a
        variable first) is not detected, hence WARN rather than a blocking orphan.
        """
        results: list[OrphanFinding] = []
        for comp_file in candidate_files:
            comp_file = comp_file.resolve()
            info = self.info.get(comp_file)
            if info is None or not info.exports:
                continue
            for cls in info.exports:
                if info.export_kinds.get(cls) in _TYPE_LEVEL_KINDS:
                    continue   # enum/interface — never "rendered", type-level
                importers = [i for i in self.importers_of_class(cls) if i != comp_file]
                if not importers:
                    continue   # NO_IMPORTER handled by find_orphan_components
                if self.instantiators_of_class(cls):
                    continue   # new C() / C.getInstance() — used
                if any(cls in fi.typed_refs for fi in self.info.values()):
                    continue   # @Param/@Local typed ref — used
                call_re = re.compile(r"\b" + re.escape(cls) + r"\s*\(")
                rendered = any(
                    call_re.search(re.sub(r"//[^\n]*", "", p.read_text(encoding="utf-8", errors="replace")))
                    for p in importers
                )
                if not rendered:
                    results.append(OrphanFinding(
                        file=self._rel(comp_file),
                        class_name=cls,
                        reason="IMPORTED_BUT_NOT_RENDERED",
                        importers=[self._rel(p) for p in importers],
                    ))
        return results

    # ─── Utilities ───────────────────────────────────────────────────────────
    def _is_ui_file(self, p: Path) -> bool:
        s = str(p)
        return any(h in s for h in _UI_PATH_HINTS) or any(h in s for h in _UI_PATH_HINTS_BS)

    def _rel(self, p: Path) -> str:
        try:
            return str(p.relative_to(self.project_root))
        except ValueError:
            return str(p)

    def _raw_text(self, p: Path) -> str:
        """Comment-stripped source text, cached. Used by usage_evidence so a
        commented-out reference is never mistaken for a real usage."""
        cached = self._text_cache.get(p)
        if cached is None:
            try:
                raw = p.read_text(encoding="utf-8", errors="replace")
            except Exception:
                raw = ""
            cached = re.sub(r"//[^\n]*", "", raw)
            self._text_cache[p] = cached
        return cached

    def usage_evidence(self, class_name: str, defining_file_rel: str) -> Optional[str]:
        """Positive evidence that `class_name` is USED via a NON-`new` mechanism —
        precisely the blind spot of the instantiation-based orphan check (it only
        recognizes `new X()` / `X.getInstance()`). Returns an evidence tag string
        if such usage exists anywhere, else None.

        Four legitimate non-instantiation usages (validated against the aippt/
        pokedex retrospectives — these are the recurring orphan false positives):
          - supertype     `extends X` / `implements X`   → abstract base / interface
          - static-access `X.member` in another file     → static facade / const-path holder
          - own-file-use  `X.` / `: X` / `new X` in X's own file → file-private helper
          - typed-ref     `: X` / `<X>` type position     → consumed by type, not by new

        fail-tight contract: a class with NO evidence anywhere returns None and
        therefore STAYS a real orphan finding. Exemption never fires on a class
        that is genuinely referenced nowhere (a true orphan / unwired symbol).
        """
        cls = class_name
        sup = re.compile(r"(?:extends|implements)\s+(?:[\w.]+\s*,\s*)*" + re.escape(cls) + r"\b")
        static = re.compile(r"(?<!new\s)\b" + re.escape(cls) + r"\s*\.")
        typ = re.compile(r"[:<]\s*" + re.escape(cls) + r"\b")
        newre = re.compile(r"\bnew\s+" + re.escape(cls) + r"\b")

        # 1. supertype use anywhere (abstract base / implemented interface)
        for f in self.files:
            if sup.search(self._raw_text(f)):
                return f"supertype:{self._rel(f)}"
        # 2. static member access in ANOTHER file (static facade / const-path holder)
        for f in self.files:
            if self._rel(f) == defining_file_rel:
                continue
            src = self._raw_text(f)
            if static.search(src) and not newre.search(src):
                return f"static-access:{self._rel(f)}"
        # 3. used inside its OWN defining file (file-private helper)
        for f in self.files:
            if self._rel(f) != defining_file_rel:
                continue
            src = self._raw_text(f)
            if static.search(src) or typ.search(src) or newre.search(src):
                return f"own-file-use:{defining_file_rel}"
            break
        # 4. typed-ref anywhere (consumed by type position, not instantiated)
        for f in self.files:
            if typ.search(self._raw_text(f)):
                return f"typed-ref:{self._rel(f)}"
        return None
