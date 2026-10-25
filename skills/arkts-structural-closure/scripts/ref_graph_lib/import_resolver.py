"""Resolve a TypeScript/ArkTS import specifier to an absolute file path within
the project. Handles relative paths, barrel exports (Index.ets re-exports),
and "@/..." or similar path aliases (best-effort; falls back to None).
"""
from __future__ import annotations
import re
from pathlib import Path
from typing import Optional

# .ets resolution order: try in order
_RESOLUTION_SUFFIXES = ["", ".ets", ".ts", "/Index.ets", "/index.ets", "/Index.ts"]


def resolve_import_path(src: str, importer_file: Path, project_root: Path) -> Optional[Path]:
    """Resolve `src` (the string in `import ... from '<src>'`) to an absolute Path.

    - Relative imports (`./foo`, `../bar/Baz`) → resolved against importer's dir
    - Bare specifiers (`@kit.ArkUI`, `@ohos.router`) → return None (external)
    - Project aliases (e.g. `@/`, `~/`) — basic fallback to project_root
    """
    if not src:
        return None

    # External / system module
    if src.startswith("@kit.") or src.startswith("@ohos.") or src.startswith("@hms."):
        return None

    if src.startswith("./") or src.startswith("../"):
        base_dir = importer_file.parent
    elif src.startswith("@/") or src.startswith("~/"):
        # Treat as project-root relative
        base_dir = project_root
        src = src[2:] if src.startswith("@/") else src[2:]
    elif src.startswith("/"):
        base_dir = project_root
        src = src.lstrip("/")
    else:
        # Bare module name — could be a HAR/HSP module; outside graph scope
        return None

    for suffix in _RESOLUTION_SUFFIXES:
        cand = (base_dir / (src + suffix)).resolve()
        if cand.exists() and cand.is_file():
            return cand
        # Without suffix, also try directory + Index variants
        if suffix == "":
            for idx in ("Index.ets", "index.ets", "Index.ts"):
                cand2 = (base_dir / src / idx).resolve()
                if cand2.exists() and cand2.is_file():
                    return cand2

    return None
