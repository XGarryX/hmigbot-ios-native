from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path


ANDROID_NS = "{http://schemas.android.com/apk/res/android}"


def _is_ignored(path: Path) -> bool:
    ignored = {".git", ".gradle", ".idea", "build", ".dep_cache"}
    return any(part in ignored for part in path.parts)


def source_files(project_root: str | Path) -> list[Path]:
    """Return Kotlin/Java files under every Android-like src/main tree."""
    root = Path(project_root)
    files = []
    for pattern in ("src/main/**/*.java", "src/main/**/*.kt"):
        files.extend(p for p in root.rglob(pattern) if not _is_ignored(p))
    return sorted(files)


def source_dirs(project_root: str | Path) -> list[Path]:
    root = Path(project_root)
    dirs: set[Path] = set()
    for src in source_files(root):
        for parent in src.parents:
            if parent.as_posix().endswith("/src/main/java") or parent.as_posix().endswith("/src/main/kotlin"):
                dirs.add(parent)
                break
    return sorted(dirs)


def res_dirs(project_root: str | Path) -> list[Path]:
    root = Path(project_root)
    return sorted(p for p in root.rglob("src/main/res") if p.is_dir() and not _is_ignored(p))


def manifests(project_root: str | Path) -> list[Path]:
    root = Path(project_root)
    return sorted(
        p for p in root.rglob("src/main/AndroidManifest.xml")
        if p.is_file() and not _is_ignored(p)
    )


def relative_to_root(path: Path, root: str | Path, file_prefix: str = "") -> str:
    rel = path.relative_to(Path(root)).as_posix()
    return f"{file_prefix}/{rel}" if file_prefix else rel


def module_root_from_manifest(manifest_path: Path) -> Path:
    # module/src/main/AndroidManifest.xml -> module
    return manifest_path.parents[2]


def _manifest_has_launcher(activity_elem: ET.Element) -> bool:
    for intent_filter in activity_elem.iter("intent-filter"):
        actions = {
            action.get(f"{ANDROID_NS}name", "")
            for action in intent_filter.iter("action")
        }
        categories = {
            category.get(f"{ANDROID_NS}name", "")
            for category in intent_filter.iter("category")
        }
        if "android.intent.action.MAIN" in actions and "android.intent.category.LAUNCHER" in categories:
            return True
    return False


def _short_activity_name(name_attr: str, package_name: str) -> str:
    if name_attr.startswith("."):
        name_attr = package_name + name_attr
    return name_attr.rsplit(".", 1)[-1]


def launcher_activity_class(project_root: str | Path) -> str:
    """Return the short MAIN/LAUNCHER Activity from any module manifest."""
    for manifest_path in manifests(project_root):
        try:
            tree = ET.parse(manifest_path)
        except ET.ParseError:
            continue
        package_name = tree.getroot().get("package", "") or ""
        for activity_elem in tree.iter("activity"):
            name_attr = activity_elem.get(f"{ANDROID_NS}name", "")
            if name_attr and _manifest_has_launcher(activity_elem):
                return _short_activity_name(name_attr, package_name)
    return ""


def manifest_action_map(project_root: str | Path) -> dict[str, list[str]]:
    """Build android.intent.action.* -> short Activity names across all manifests."""
    action_map: dict[str, list[str]] = {}
    for manifest_path in manifests(project_root):
        try:
            tree = ET.parse(manifest_path)
        except ET.ParseError:
            continue
        package_name = tree.getroot().get("package", "") or ""
        for activity_elem in tree.iter("activity"):
            name_attr = activity_elem.get(f"{ANDROID_NS}name", "")
            if not name_attr:
                continue
            short_name = _short_activity_name(name_attr, package_name)
            for intent_filter in activity_elem.iter("intent-filter"):
                for action in intent_filter.iter("action"):
                    action_name = action.get(f"{ANDROID_NS}name", "")
                    if action_name and action_name.startswith("android.intent.action."):
                        action_map.setdefault(action_name, []).append(short_name)
    return action_map


def manifest_components(project_root: str | Path) -> dict[str, dict]:
    """Map non-UI Android components declared in manifests to their kind.

    Returns {short_class: {"kind", "name_attr", "manifest"}} for every
    <service>, <receiver> and <provider> across all module manifests. A
    <receiver> is reported as ``appwidget_provider`` when its subtree declares
    the AppWidget provider meta-data or the APPWIDGET_UPDATE intent action;
    otherwise it is a plain ``broadcast_receiver``.
    """
    components: dict[str, dict] = {}
    tag_kind = {
        "service": "service",
        "receiver": "broadcast_receiver",
        "provider": "provider",
    }
    for manifest_path in manifests(project_root):
        try:
            tree = ET.parse(manifest_path)
        except ET.ParseError:
            continue
        package_name = tree.getroot().get("package", "") or ""
        for tag, kind in tag_kind.items():
            for elem in tree.iter(tag):
                name_attr = elem.get(f"{ANDROID_NS}name", "")
                if not name_attr:
                    continue
                short_name = _short_activity_name(name_attr, package_name)
                elem_kind = kind
                if kind == "broadcast_receiver" and _is_appwidget_receiver(elem):
                    elem_kind = "appwidget_provider"
                # First declaration wins; manifests rarely re-declare a class.
                components.setdefault(short_name, {
                    "kind": elem_kind,
                    "name_attr": name_attr,
                    "manifest": manifest_path.as_posix(),
                })
    return components


def _is_appwidget_receiver(receiver_elem: ET.Element) -> bool:
    for meta in receiver_elem.iter("meta-data"):
        if meta.get(f"{ANDROID_NS}name", "") == "android.appwidget.provider":
            return True
    for action in receiver_elem.iter("action"):
        if action.get(f"{ANDROID_NS}name", "") == "android.appwidget.action.APPWIDGET_UPDATE":
            return True
    return False


def class_name_for_source(path: Path) -> str:
    return path.stem


def package_name_for_source(source: str) -> str:
    match = re.search(r"^\s*package\s+([\w.]+)", source, re.MULTILINE)
    return match.group(1) if match else ""
