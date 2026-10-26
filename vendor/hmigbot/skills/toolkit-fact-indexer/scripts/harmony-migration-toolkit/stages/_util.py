from __future__ import annotations

import hashlib
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Iterable


def toolkit_root() -> Path:
    return Path(__file__).resolve().parent.parent


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    path.write_text(text, encoding="utf-8", newline="\n")


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def normalize_android_paths(obj: Any, android_root: Path) -> Any:
    """Recursively replace absolute paths under android_root with posix relative paths."""
    roots = {str(android_root), str(android_root.resolve())}
    roots_norm = {r.replace("\\", "/") for r in roots}
    for r in list(roots):
        roots_norm.add(r.lower().replace("\\", "/"))

    def norm_one(s: str) -> str:
        if not isinstance(s, str) or not s:
            return s
        sl = s.replace("\\", "/")
        for prefix in sorted(roots_norm, key=len, reverse=True):
            pref = prefix.rstrip("/")
            if sl.lower().startswith(pref.lower() + "/") or sl.lower() == pref.lower():
                rel = sl[len(pref) :].lstrip("/")
                return rel
        return s

    if isinstance(obj, dict):
        return {k: normalize_android_paths(v, android_root) for k, v in obj.items()}
    if isinstance(obj, list):
        return [normalize_android_paths(x, android_root) for x in obj]
    if isinstance(obj, str):
        return norm_one(obj)
    return obj


def is_synthetic_kotlin_class(name: str) -> bool:
    if "$" not in name:
        return False
    tail = name.split("$", 1)[1].lower()
    if "lambda" in tail or "inlined" in tail:
        return True
    if re.search(r"\$\d+", name):
        return True
    if tail.startswith("setup") or tail.startswith("access$"):
        return True
    return False


def kotlin_outer_host_class(class_name: str) -> str:
    """Fold Kotlin synthetic / inner classes to a stable outer host name (deterministic)."""
    name = class_name
    for _ in range(128):
        if not is_synthetic_kotlin_class(name):
            return name
        if "$" not in name:
            return class_name.split("$", 1)[0] if "$" in class_name else name
        name = name.rsplit("$", 1)[0]
    return class_name.split("$", 1)[0] if "$" in class_name else class_name


def read_gradle_app_config(android_root: Path) -> dict[str, str]:
    """Read applicationId and namespace from the app module Gradle files (Groovy or Kotlin DSL)."""
    out: dict[str, str] = {"application_id": "", "namespace": ""}
    for rel in ("app/build.gradle.kts", "app/build.gradle"):
        p = android_root / rel
        if not p.is_file():
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for pat in (
            r"applicationId\s*=\s*[\"']([^\"']+)[\"']",
            r"applicationId\s+[\"']([^\"']+)[\"']",
        ):
            m = re.search(pat, text)
            if m and not out["application_id"]:
                out["application_id"] = m.group(1).strip()
                break
        for pat in (
            r"namespace\s*=\s*[\"']([^\"']+)[\"']",
            r"namespace\s+[\"']([^\"']+)[\"']",
        ):
            m = re.search(pat, text)
            if m and not out["namespace"]:
                out["namespace"] = m.group(1).strip()
                break
    return out


def discover_gradle_modules(android_root: Path) -> list[dict[str, str]]:
    modules: list[dict[str, str]] = []
    for name in ("settings.gradle.kts", "settings.gradle"):
        p = android_root / name
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8", errors="ignore")
        for m in re.finditer(r"""include\s*\(\s*["']([^"']+)["']\s*\)""", text):
            mod = m.group(1).strip(":").replace(":", "/")
            modules.append({"name": m.group(1).strip(":"), "path": mod})
        for m in re.finditer(r"""include\s+['"]([^'"]+)['"]""", text):
            raw = m.group(1).strip(":")
            modules.append({"name": raw, "path": raw.replace(":", "/")})
        if modules:
            break
    if not modules:
        if (android_root / "app").is_dir():
            modules.append({"name": "app", "path": "app"})
    return modules


def read_application_id(android_root: Path) -> str:
    g = read_gradle_app_config(android_root)
    if g["application_id"]:
        return g["application_id"]
    candidates = list(android_root.rglob("build.gradle*"))
    for p in sorted(candidates, key=lambda x: len(str(x))):
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for pat in (
            r"applicationId\s+['\"]([^'\"]+)['\"]",
            r"applicationId\s*=\s*[\"']([^\"']+)[\"']",
        ):
            m = re.search(pat, text)
            if m:
                return m.group(1).strip()
    return ""


def parse_manifest_launcher(android_root: Path) -> tuple[str, str, str]:
    """Returns (package, launcher_activity_short, launcher_activity_qualified)."""
    gradle_ns = read_gradle_app_config(android_root).get("namespace", "") or ""
    preferred = android_root / "app" / "src" / "main" / "AndroidManifest.xml"
    manifests = []
    if preferred.is_file():
        manifests.append(preferred)
    manifests.extend(
        sorted(
            (p for p in (android_root / "app" / "src" / "main").glob("AndroidManifest.xml") if p != preferred),
            key=lambda x: str(x),
        )
    )
    if not manifests:
        manifests = sorted(android_root.rglob("AndroidManifest.xml"), key=lambda x: len(str(x)))
    if not manifests:
        return "", "", ""
    path = manifests[0]
    text = path.read_text(encoding="utf-8", errors="ignore")
    pkg_m = re.search(r"""package\s*=\s*["']([^"']+)["']""", text)
    package = (pkg_m.group(1) if pkg_m else "").strip() or gradle_ns
    short = _launcher_activity_name(path, text)
    if short.startswith("."):
        short = short[1:]
        qualified = f"{package}.{short}" if package else short
    elif "." in short:
        qualified = short
    else:
        qualified = f"{package}.{short}" if package else short
    return package, short, qualified


_ANDROID_NS = "{http://schemas.android.com/apk/res/android}"


def _intent_filter_is_launcher(elem: ET.Element) -> bool:
    for intent_filter in elem.iter("intent-filter"):
        actions = {a.get(f"{_ANDROID_NS}name", "") for a in intent_filter.iter("action")}
        categories = {c.get(f"{_ANDROID_NS}name", "") for c in intent_filter.iter("category")}
        if "android.intent.action.MAIN" in actions and "android.intent.category.LAUNCHER" in categories:
            return True
    return False


def _launcher_activity_name(path: Path, text: str) -> str:
    """Short/relative class name of the MAIN+LAUNCHER entry point.

    Parsed with ElementTree so the launcher is the activity whose own
    intent-filter declares both action.MAIN and category.LAUNCHER — not, as a
    cross-element regex would yield, the first ``<activity>`` in the document
    that happens to be followed somewhere by a MAIN action. ``activity-alias``
    is resolved to its ``targetActivity``. Falls back to the first activity only
    when no launcher entry exists (e.g. a library module manifest).
    """
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError:
        # Malformed XML — fall back to a name-only regex (no MAIN/LAUNCHER claim).
        m = re.search(r"""<activity[^>]+android:name\s*=\s*["']([^"']+)["']""", text, re.IGNORECASE)
        return m.group(1) if m else ""
    first_activity = ""
    for tag in ("activity", "activity-alias"):
        for elem in root.iter(tag):
            name = elem.get(f"{_ANDROID_NS}name", "")
            if not first_activity and tag == "activity" and name:
                first_activity = name
            if _intent_filter_is_launcher(elem):
                if tag == "activity-alias":
                    return elem.get(f"{_ANDROID_NS}targetActivity", "") or name
                return name
    return first_activity
