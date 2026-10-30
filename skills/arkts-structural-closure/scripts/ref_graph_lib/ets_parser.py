"""Parse a single .ets file for: imports, exported class/struct names,
class instantiations (new X(), X.getInstance(), `: X =`, `@Param/@Local: X`).

Phase 1: regex-based. Phase 4 will replace with tree-sitter AST.
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


# ─── Regex patterns ──────────────────────────────────────────────────────────
# import { X, Y } from '<path>'        — named imports
# import { X as Z } from '<path>'      — aliased
# import * as Foo from '<path>'        — namespace
# import Foo from '<path>'             — default
_IMPORT_NAMED = re.compile(
    r"import\s*\{\s*(?P<names>[^}]+)\s*\}\s*from\s*['\"](?P<src>[^'\"]+)['\"]",
)
_IMPORT_NS = re.compile(
    r"import\s+\*\s+as\s+(?P<alias>\w+)\s+from\s*['\"](?P<src>[^'\"]+)['\"]",
)
_IMPORT_DEFAULT = re.compile(
    r"^import\s+(?P<name>\w+)\s+from\s*['\"](?P<src>[^'\"]+)['\"]",
    re.MULTILINE,
)

# export struct / export class / export default class
# Note: ArkUI uses `@ComponentV2\n@Entry\nstruct Foo { }`; export is implicit when
# inside an ets file referenced via main_pages.json. We capture both forms.
_EXPORT_NAMED = re.compile(
    r"(?:^|\n)\s*(?:export\s+)?(?:default\s+)?(?:const\s+)?"
    r"(?P<kind>class|struct|interface|enum)\s+(?P<name>[A-Z][A-Za-z0-9_]*)",
    re.MULTILINE,
)
# `export { Foo, Bar }` re-exports (barrel files)
_EXPORT_REEXPORT = re.compile(
    r"^export\s*\{\s*(?P<names>[^}]+)\s*\}",
    re.MULTILINE,
)

# Instantiations:
#   new ClassName(
#   ClassName.getInstance(
#   = new ClassName
#   : ClassName =        (type annotation on field; counts as wired if value is new)
#   @Param vm: ClassName
#   @Local vm: ClassName
_NEW_EXPR = re.compile(r"\bnew\s+(?P<cls>[A-Z][A-Za-z0-9_]*)\s*\(")
_GET_INSTANCE = re.compile(r"\b(?P<cls>[A-Z][A-Za-z0-9_]*)\.getInstance\s*\(")
_TYPED_FIELD_NEW = re.compile(
    r":\s*(?P<cls>[A-Z][A-Za-z0-9_]*)\s*=\s*new\s+(?P=cls)\s*\("
)
_PARAM_LOCAL_TYPED = re.compile(
    r"@(?:Param|Local)\s+\w+\s*[:：]\s*(?P<cls>[A-Z][A-Za-z0-9_]*)"
)


@dataclass
class EtsFileInfo:
    path: Path
    exports: set[str] = field(default_factory=set)          # class/struct/interface names exported
    export_kinds: dict[str, str] = field(default_factory=dict)  # name → 'class'|'struct'|'interface'|'enum'
    imports: list[dict] = field(default_factory=list)        # [{src, names: [...] | None, kind: 'named'|'ns'|'default'}]
    instantiations: set[str] = field(default_factory=set)    # class names instantiated in this file
    instantiation_lines: dict[str, list[int]] = field(default_factory=dict)
    typed_refs: set[str] = field(default_factory=set)        # class names referenced as @Param/@Local type
    reexports: set[str] = field(default_factory=set)         # names re-exported via `export { ... }`

    def has_instantiation(self, class_name: str) -> bool:
        return class_name in self.instantiations

    def has_typed_ref(self, class_name: str) -> bool:
        return class_name in self.typed_refs


def _read_text(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def parse_ets_file(path: Path) -> EtsFileInfo:
    """Parse a single .ets file into EtsFileInfo."""
    info = EtsFileInfo(path=path)
    text = _read_text(path)
    if not text:
        return info

    # Strip line comments first to avoid false positives in commented-out code.
    # We don't strip block comments because regex pass is line-based and the
    # `new X(` patterns rarely live inside multi-line comments in ArkUI code.
    cleaned = re.sub(r"//[^\n]*", "", text)

    # ── Imports ──
    for m in _IMPORT_NAMED.finditer(cleaned):
        names = [n.strip().split(" as ")[0].strip() for n in m.group("names").split(",")]
        info.imports.append({
            "src": m.group("src"),
            "names": [n for n in names if n],
            "kind": "named",
        })
    for m in _IMPORT_NS.finditer(cleaned):
        info.imports.append({"src": m.group("src"), "alias": m.group("alias"), "kind": "ns"})
    for m in _IMPORT_DEFAULT.finditer(cleaned):
        if "{" in m.group(0):  # don't double-count named-import lines
            continue
        info.imports.append({"src": m.group("src"), "name": m.group("name"), "kind": "default"})

    # ── Exports ──
    for m in _EXPORT_NAMED.finditer(cleaned):
        info.exports.add(m.group("name"))
        info.export_kinds[m.group("name")] = m.group("kind")
    for m in _EXPORT_REEXPORT.finditer(cleaned):
        for n in m.group("names").split(","):
            name = n.strip().split(" as ")[0].strip()
            if name:
                info.reexports.add(name)

    # ── Instantiations ──
    for m in _NEW_EXPR.finditer(cleaned):
        cls = m.group("cls")
        info.instantiations.add(cls)
        info.instantiation_lines.setdefault(cls, []).append(cleaned.count("\n", 0, m.start()) + 1)
    for m in _GET_INSTANCE.finditer(cleaned):
        cls = m.group("cls")
        info.instantiations.add(cls)
        info.instantiation_lines.setdefault(cls, []).append(cleaned.count("\n", 0, m.start()) + 1)
    for m in _TYPED_FIELD_NEW.finditer(cleaned):
        cls = m.group("cls")
        info.instantiations.add(cls)
        info.instantiation_lines.setdefault(cls, []).append(cleaned.count("\n", 0, m.start()) + 1)
    for m in _PARAM_LOCAL_TYPED.finditer(cleaned):
        # @Param/@Local typed reference: not full instantiation, but counts as
        # "used as VM by this component" for orphan detection.
        info.typed_refs.add(m.group("cls"))

    return info
