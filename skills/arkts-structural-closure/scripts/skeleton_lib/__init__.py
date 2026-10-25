"""skeleton_lib — Skeleton detection taxonomy and patterns.

Used by audit_skeletons.py (CLI) and verify_slice_wiring.py (C5 was removed;
this lib is still useful when wiring loop needs to confirm `// FWD-REF` markers
match registry — see registry_resolver.is_legitimate).
"""
from .taxonomy import (
    Level,
    SkeletonFinding,
    is_fail,
    Severity,
)
from .patterns import (
    SKELETON_PATTERNS,
    EMPTY_BUILDER_HEURISTIC,
    ESCAPE_HATCH_PHRASES,
    FWD_REF_MARKER,
    PLACEHOLDER_MARKER,
)
from .classifier import scan_ets_files, scan_handoff_files, scan_dangling_fwd_refs
from .registry_resolver import RegistryResolver

__all__ = [
    "Level",
    "Severity",
    "SkeletonFinding",
    "is_fail",
    "SKELETON_PATTERNS",
    "EMPTY_BUILDER_HEURISTIC",
    "ESCAPE_HATCH_PHRASES",
    "FWD_REF_MARKER",
    "PLACEHOLDER_MARKER",
    "scan_ets_files",
    "scan_handoff_files",
    "scan_dangling_fwd_refs",
    "RegistryResolver",
]
