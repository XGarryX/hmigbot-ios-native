from __future__ import annotations

from pathlib import Path

from extractors.class_parser import parse_class

_ANDROID_FRAGMENT_BASES_SHORT = {
    "Fragment", "DialogFragment", "BottomSheetDialogFragment",
    "PreferenceFragmentCompat", "PreferenceFragment",
    "PreferenceDialogFragmentCompat", "ListFragment",
    "MapFragment", "SupportMapFragment",
    "AppCompatDialogFragment",
}

_ANDROID_ACTIVITY_BASES_SHORT = {
    "Activity", "AppCompatActivity", "FragmentActivity",
    "ComponentActivity", "ListActivity", "PreferenceActivity",
}


_IGNORE_PARTS = {".gradle", ".git", ".idea", ".dep_cache"}


# Dagger-Hilt generates an intermediate base class `Hilt_<OriginalName>` between a
# source @AndroidEntryPoint Activity/Fragment and its framework superclass. These
# synthetic classes exist only in bytecode (never in source), so they always appear
# as bytecode_only and would otherwise read as hundreds of false "AST misses". The
# `Hilt_` prefix is a fixed Hilt naming convention, not project-specific. We split
# them into their own bucket rather than dropping them, so the exclusion stays
# auditable and a genuine miss is never hidden by it.
def _is_synthetic_generated(name: str) -> bool:
    return name.startswith("Hilt_")


# Compiled-class output layouts vary by AGP/Kotlin version. `javac` holds Java
# classes; Kotlin classes land in `tmp/kotlin-classes` (older AGP) or
# `intermediates/built_in_kotlinc` (newer AGP's built-in Kotlin compilation);
# `intermediates/classes` is the per-variant merged Java+Kotlin set. Scanning all
# of them — and deduping class names downstream — keeps the verifier from silently
# missing every Kotlin Fragment when only the old two patterns exist. The `build/`
# anchor pins these to a module build dir so unrelated `classes/` dirs are ignored.
_CLASS_DIR_PATTERNS = (
    "build/intermediates/javac",
    "build/intermediates/classes",
    "build/intermediates/built_in_kotlinc",
    "build/tmp/kotlin-classes",
)


def _class_dirs(project_root: str | Path) -> list[tuple[Path, str]]:
    root = Path(project_root)
    items: list[tuple[Path, str]] = []
    seen_variants: set[Path] = set()
    for pattern in _CLASS_DIR_PATTERNS:
        for parent_dir in root.rglob(pattern):
            if set(parent_dir.parts) & _IGNORE_PARTS:
                continue
            if not parent_dir.is_dir():
                continue
            # parent_dir is like app/build/intermediates/javac; the module is the
            # directory containing build/, three levels above parent_dir.
            module_dir = parent_dir.parent.parent.parent
            module_name = module_dir.name if module_dir != root else root.name
            for variant in parent_dir.iterdir():
                if variant.is_dir() and variant not in seen_variants:
                    seen_variants.add(variant)
                    items.append((variant, module_name))
    return items


def bytecode_hierarchy(project_root: str | Path) -> tuple[dict[str, str | None], dict[str, str]]:
    hierarchy: dict[str, str | None] = {}
    class_module: dict[str, str] = {}
    seen: set[str] = set()
    for class_dir, module_name in _class_dirs(project_root):
        for cf in class_dir.rglob("*.class"):
            try:
                cls = parse_class(cf)
            except Exception:
                continue
            full_name: str = cls.get("class", "")
            raw = full_name.rsplit(".", 1)[-1] if "." in full_name else full_name
            name = raw.split("$")[-1]
            if name in seen:
                continue
            seen.add(name)
            class_module[name] = module_name
            super_full: str = cls.get("super", "") or ""
            if super_full and "." in super_full:
                hierarchy[name] = super_full.rsplit(".", 1)[-1].split("$")[-1]
            else:
                hierarchy[name] = super_full or None
    return hierarchy, class_module


def _resolve_bytecode_base(
    name: str,
    bc_hierarchy: dict[str, str | None],
    visited: set[str] | None = None,
) -> str:
    if visited is None:
        visited = set()
    if name in visited:
        return "other"
    visited.add(name)

    super_short = bc_hierarchy.get(name)
    # class not found in bytecode at all — unknown, not a guess
    if super_short is None:
        return "unknown"

    if super_short in _ANDROID_FRAGMENT_BASES_SHORT:
        return "fragment"
    if super_short in _ANDROID_ACTIVITY_BASES_SHORT:
        return "activity"
    return _resolve_bytecode_base(super_short, bc_hierarchy, visited)


def bytecode_verifier(
    project_root: str | Path,
    ast_hierarchy: dict,
    resolve_android_base,
) -> dict:
    bc_hierarchy, class_module = bytecode_hierarchy(project_root)

    result: dict = {
        "bytecode_available": bool(bc_hierarchy),
        "bytecode_class_count": len(bc_hierarchy),
        "modules_scanned": sorted(set(class_module.values())),
    }

    if not bc_hierarchy:
        result["bytecode_fragment_count"] = 0
        result["bytecode_activity_count"] = 0
        result["bytecode_fragments"] = []
        result["bytecode_activities"] = []
        result["ast_vs_bytecode_fragment_diff"] = {
            "note": "no bytecode data — build project first or check find_class_dir()",
            "ast_only": [], "bytecode_only": [], "matched": [],
        }
        result["ast_vs_bytecode_activity_diff"] = {
            "note": "no bytecode data — build project first or check find_class_dir()",
            "ast_only": [], "bytecode_only": [], "matched": [],
        }
        return result

    bc_fragments: set[str] = set()
    bc_activities: set[str] = set()
    for name in bc_hierarchy:
        kind = _resolve_bytecode_base(name, bc_hierarchy)
        if kind == "fragment":
            bc_fragments.add(name)
        elif kind == "activity":
            bc_activities.add(name)

    result["bytecode_fragment_count"] = len(bc_fragments)
    result["bytecode_activity_count"] = len(bc_activities)
    result["bytecode_fragments"] = sorted(bc_fragments)
    result["bytecode_activities"] = sorted(bc_activities)

    ast_fragments = {
        info.name for fqn, info in ast_hierarchy.items()
        if resolve_android_base(fqn, ast_hierarchy) == "fragment"
    }
    ast_activities = {
        info.name for fqn, info in ast_hierarchy.items()
        if resolve_android_base(fqn, ast_hierarchy) == "activity"
    }

    def _diff_with_diagnostics(ast_set, bc_set, label):
        ast_only = sorted(ast_set - bc_set)
        bc_only_all = sorted(bc_set - ast_set)
        matched = sorted(ast_set & bc_set)
        # Hilt-generated intermediate bases are bytecode-only by construction; keep
        # them out of the actionable miss list but record them for auditability.
        bc_only = [n for n in bc_only_all if not _is_synthetic_generated(n)]
        synthetic_excluded = [n for n in bc_only_all if _is_synthetic_generated(n)]
        ast_only_details = []
        for name in ast_only:
            bc_type = _resolve_bytecode_base(name, bc_hierarchy) if name in bc_hierarchy else "not_in_hierarchy"
            mod = class_module.get(name, "N/A")
            ast_only_details.append({
                "class": name,
                "in_bytecode_hierarchy": name in bc_hierarchy,
                "bytecode_type": bc_type,
                "module": mod,
            })
        bc_only_details = []
        for name in bc_only:
            ast_type = resolve_android_base(name, ast_hierarchy) if name in ast_hierarchy else "not_in_ast"
            mod = class_module.get(name, "N/A")
            bc_only_details.append({
                "class": name,
                "in_ast_hierarchy": name in ast_hierarchy,
                "ast_type": ast_type,
                "module": mod,
            })
        matched_details = []
        for name in matched:
            mod = class_module.get(name, "N/A")
            matched_details.append({"class": name, "module": mod})
        return {
            "ast_only": ast_only,
            "ast_only_details": ast_only_details,
            "bytecode_only": bc_only,
            "bytecode_only_details": bc_only_details,
            "synthetic_excluded": synthetic_excluded,
            "synthetic_excluded_count": len(synthetic_excluded),
            "matched": matched,
            "matched_details": matched_details,
        }

    result["ast_vs_bytecode_fragment_diff"] = _diff_with_diagnostics(
        ast_fragments, bc_fragments, "fragment"
    )
    result["ast_vs_bytecode_activity_diff"] = _diff_with_diagnostics(
        ast_activities, bc_activities, "activity"
    )

    return result
