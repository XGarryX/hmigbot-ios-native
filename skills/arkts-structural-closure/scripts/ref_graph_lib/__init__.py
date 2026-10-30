"""ref_graph_lib — Build project-wide reference graph from .ets sources.

Used to detect L4 orphan-vm (file exists but no importer + no instantiation).
"""
from .ets_parser import EtsFileInfo, parse_ets_file
from .import_resolver import resolve_import_path
from .graph import EtsRefGraph, OrphanFinding

__all__ = [
    "EtsFileInfo",
    "parse_ets_file",
    "resolve_import_path",
    "EtsRefGraph",
    "OrphanFinding",
]
