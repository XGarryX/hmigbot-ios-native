"""
App model JSON shapes and stable id helpers.

See output/app_model/index.json (produced by app_model_builder) for the
on-disk layout. This module centralizes id rules so paths, screens, and
navigation edges stay joinable without relying on string path equality.
"""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any

APP_MODEL_VERSION = "1"


def ui_point_id(layout: str, element_id: str, *, virtual: bool = False, trigger: str = "") -> str:
    """Stable id for an XML-backed control or a virtual nav item."""
    layout = layout or "_"
    if virtual:
        raw = f"v|{layout}|{trigger}|{element_id}"
        h = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
        return f"up:v:{h}"
    eid = element_id or "_none_"
    return f"up:{layout}:{eid}"


def nav_edge_id(from_class: str, to_class: str, trigger: str, line: int | None, idx: int) -> str:
    """Stable id for a navigation graph edge (regex or bytecode)."""
    raw = f"{from_class}|{to_class}|{trigger}|{line if line is not None else ''}|{idx}"
    h = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]
    return f"ne:{h}"


def behavior_id(file: str, line: int, method: str, idx: int) -> str:
    raw = f"{file}|{line}|{method}|{idx}"
    h = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]
    return f"bh:{h}"


def feature_id_from_class(screen_class: str) -> str:
    """Coarse feature bucket: outer Activity / Fragment name without inner classes."""
    base = screen_class.split("$")[0] if screen_class else "unknown"
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", base).strip("_").lower() or "unknown"
    return f"ft:{slug}"


def segment_key(seg: dict[str, Any]) -> str:
    """Single-token key for path_key assembly."""
    k = seg.get("kind", "")
    if k == "screen":
        return "scr:" + _slug(seg.get("layout") or seg.get("label") or "x")
    if k == "action":
        if seg.get("virtual"):
            return "act:v:" + _slug(seg.get("trigger") or seg.get("resolved_label") or "x")
        return "act:" + _slug(seg.get("element_id") or seg.get("resolved_label") or "x")
    if k == "branch":
        return "br:" + _slug(str(seg.get("value_key") or seg.get("value") or "x"))
    if k == "parameter":
        return "param:" + _slug(seg.get("pattern", "unknown"))
    return "unk:" + _slug(k)


def path_id_from_segments(segments: list[dict[str, Any]]) -> str:
    """Deterministic id from ordered segments (canonical json)."""
    blob = json.dumps(segments, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "path:" + hashlib.sha256(blob.encode("utf-8")).hexdigest()[:20]


def _slug(s: str) -> str:
    s = (s or "").lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    return s.strip("_")[:64] or "x"


def _string_key_guess(s: str) -> str:
    """Map display-ish text to likely strings.xml key (best-effort)."""
    t = (s or "").lower()
    t = re.sub(r"[^a-z0-9]+", "_", t)
    return t.strip("_")[:96] or "x"


def path_display_report_from_segments(
    segments: list[dict[str, Any]],
    strings: dict[str, str],
) -> str:
    """
    Human-oriented path for stakeholder reports: resolve menu / string keys via static_xml.strings.
    Uses ' › ' separator to distinguish from machine-oriented path_display (' > ').
    """
    parts: list[str] = []
    for seg in segments:
        k = seg.get("kind", "")
        if k == "screen":
            lab = str(seg.get("label") or seg.get("layout") or "")
            sk = _string_key_guess(lab)
            parts.append(strings.get(sk, lab))
        elif k == "action":
            lab = str(seg.get("resolved_label") or seg.get("element_id") or "")
            tr = str(seg.get("trigger") or "")
            if tr.lower().startswith("menu "):
                raw = tr[5:].strip()
                keys = [
                    raw.replace("-", "_").lower(),
                    raw.replace(" ", "_").lower(),
                    _string_key_guess(raw),
                ]
                resolved = lab
                for key in keys:
                    if key and key in strings:
                        resolved = strings[key]
                        break
                parts.append(resolved)
            else:
                sk = _string_key_guess(lab)
                parts.append(strings.get(sk, lab))
        elif k == "branch":
            v = str(seg.get("value") or "")
            vk = str(seg.get("value_key") or "")
            parts.append(strings.get(vk, strings.get(_string_key_guess(v), v)))
        elif k == "parameter":
            pat = str(seg.get("pattern", "input"))
            parts.append(strings.get(f"param_{pat}", str(seg.get("placeholder_display") or f"{{{pat}}}")))
    return " › ".join(p for p in parts if p)


def path_display_from_segments(segments: list[dict[str, Any]], *, template: bool = False) -> str:
    """Human-oriented chain (legacy separator ' > ')."""
    parts: list[str] = []
    for seg in segments:
        k = seg.get("kind", "")
        if k == "screen":
            parts.append(str(seg.get("label") or seg.get("layout") or ""))
        elif k == "action":
            parts.append(str(seg.get("resolved_label") or seg.get("element_id") or ""))
        elif k == "branch":
            parts.append(str(seg.get("value") or ""))
        elif k == "parameter":
            if template:
                pat = seg.get("pattern", "value")
                hint = seg.get("format_hint") or ""
                parts.append(f"{{{pat}{':' + hint if hint else ''}}}")
            else:
                parts.append(str(seg.get("placeholder_display") or f"{{{seg.get('pattern', 'input')}}}"))
    return " > ".join(p for p in parts if p)


def build_path_record(segments: list[dict[str, Any]]) -> dict[str, Any]:
    """Attach path_id, path_key, path_display, optional template, spec helpers."""
    pid = path_id_from_segments(segments)
    pkey = ".".join(segment_key(s) for s in segments)
    has_param = any(s.get("kind") == "parameter" for s in segments)
    rec: dict[str, Any] = {
        "path_id": pid,
        "path_key": pkey,
        "segments": segments,
        "path_display": path_display_from_segments(segments, template=False),
    }
    if has_param:
        rec["path_display_template"] = path_display_from_segments(segments, template=True)
    # Spec / legacy consumers
    screen_label, element_id, primary_layout = _spec_fields_from_segments(segments)
    rec["screen"] = screen_label
    rec["element_id"] = element_id
    rec["primary_layout"] = primary_layout
    rec["path_display_legacy"] = rec["path_display"]
    return rec


def _spec_fields_from_segments(segments: list[dict[str, Any]]) -> tuple[str, str, str]:
    """(screen_label, element_id, primary_layout) for generate_specs."""
    element_id = ""
    action_layout = ""
    last_screen_label = ""
    last_screen_layout = ""
    for seg in segments:
        if seg.get("kind") == "screen":
            last_screen_label = str(seg.get("label") or "")
            last_screen_layout = str(seg.get("layout") or "")
        elif seg.get("kind") == "action":
            element_id = str(seg.get("element_id") or "")
            action_layout = str(seg.get("layout") or "")
    # Screen containing the action (preferred) else last visited screen
    primary_layout = action_layout or last_screen_layout
    screen_label = last_screen_label
    if action_layout:
        for seg in segments:
            if seg.get("kind") == "screen" and seg.get("layout") == action_layout:
                screen_label = str(seg.get("label") or screen_label)
                break
    return screen_label, element_id, primary_layout
