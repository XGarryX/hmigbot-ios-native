"""
view_ref_utils.py
Shared utilities for resolving Android view references (camelCase ViewBinding
names) to XML element ids (snake_case).
"""
from __future__ import annotations

import re


def camel_to_snake(name: str) -> str:
    s = re.sub(r"(?<=[a-z])(?=[A-Z])", "_", name)
    s = re.sub(r"(?<=[a-zA-Z])(?=[0-9])", "_", s)
    return s.lower()


def clean_view_ref(ref: str) -> str:
    """Strip binding./viewBinding./view./this. prefixes from a view reference."""
    ref = re.sub(r'^(?:viewBinding|binding|view|this)\s*[\.\?]\s*', '', ref)
    return ref.strip()


def resolve_view_id(raw_ref: str, known_ids: dict | set,
                    file_ref_map: dict | None = None) -> str:
    """Resolve a raw view reference to a known XML id.

    Tries: exact match, camelCase→snake_case, then file_ref_map lookup.
    known_ids can be a dict (keyed by id) or a set of id strings.
    """
    if not raw_ref:
        return ""
    if raw_ref in known_ids:
        return raw_ref
    snake = camel_to_snake(raw_ref)
    if snake != raw_ref and snake in known_ids:
        return snake
    if file_ref_map:
        mapped_id = file_ref_map.get(raw_ref, "")
        if mapped_id and mapped_id in known_ids:
            return mapped_id
    return ""
