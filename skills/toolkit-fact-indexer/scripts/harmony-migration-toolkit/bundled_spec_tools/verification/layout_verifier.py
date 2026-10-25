from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from extractors.android_project import ANDROID_NS, res_dirs
from extractors.ast_index import lookup_class


def layout_fragment_refs(project_root: str | Path) -> dict[str, list[str]]:
    refs: dict[str, list[str]] = {}
    ns = ANDROID_NS
    for res_dir in res_dirs(project_root):
        layout_dir = res_dir / "layout"
        if not layout_dir.is_dir():
            continue
        for xml_file in sorted(layout_dir.rglob("*.xml")):
            try:
                tree = ET.parse(xml_file)
            except ET.ParseError:
                continue
            for elem in tree.iter():
                tag = elem.tag
                if tag != "fragment" and not (isinstance(tag, str) and tag.endswith("}fragment")):
                    continue
                name_attr = (
                    elem.get(f"{{{ns}}}name", "")
                    or elem.get("android:name", "")
                    or elem.get("class", "")
                )
                if not name_attr:
                    continue
                short = name_attr.rsplit(".", 1)[-1]
                rel = xml_file.relative_to(Path(project_root)).as_posix()
                refs[short] = refs.get(short, []) + [rel]
    return refs


def layout_verifier(
    project_root: str | Path,
    ast_hierarchy: dict,
    resolve_android_base,
) -> dict:
    refs = layout_fragment_refs(project_root)
    result = {
        "layout_fragment_ref_count": len(refs),
        "ast_fragment_count": 0,
        "ast_fragment_matched": [],
        "ast_fragment_missed": [],
        "layout_only": [],
    }
    for short_name in sorted(refs):
        info = lookup_class(ast_hierarchy, short_name)
        if info is not None:
            kind = resolve_android_base(info.fqn, ast_hierarchy)
            if kind == "fragment":
                result["ast_fragment_count"] += 1
                result["ast_fragment_matched"].append(short_name)
            else:
                result["ast_fragment_missed"].append({
                    "class": short_name,
                    "ast_kind": kind,
                    "layout_files": refs[short_name],
                })
        else:
            result["layout_only"].append({
                "class": short_name,
                "layout_files": refs[short_name],
            })
    return result
