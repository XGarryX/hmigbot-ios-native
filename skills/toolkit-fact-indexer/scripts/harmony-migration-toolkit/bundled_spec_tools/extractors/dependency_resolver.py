"""
dependency_resolver.py
解析 Gradle 依赖配置，自动下载 GitHub 库源码到本地缓存。

支持两种依赖声明方式：
  1. libs.versions.toml 中的 com.github.Xxx:Yyy:commit_hash (JitPack)
  2. settings.gradle.kts 中的 includeBuild 指向的本地路径

用法（被 main.py 调用）：
  from extractors.dependency_resolver import resolve_dependencies
  extra_roots = resolve_dependencies(project_root)
"""

import json
import re
import shutil
import urllib.request
import zipfile
import io
from pathlib import Path

GITHUB_JITPACK_RE = re.compile(
    r'com\.github\.([A-Za-z0-9_.-]+):([A-Za-z0-9_.-]+)'
)

_CACHE_DIR = None


def _cache_dir() -> Path:
    global _CACHE_DIR
    if _CACHE_DIR is None:
        _CACHE_DIR = Path(__file__).parent.parent / ".dep_cache"
        _CACHE_DIR.mkdir(exist_ok=True)
    return _CACHE_DIR


def parse_toml_versions(toml_path: Path) -> list[dict]:
    """
    解析 gradle/libs.versions.toml，提取 GitHub JitPack 依赖。
    返回 [{"owner": "SimpleMobileTools", "repo": "Simple-Commons", "ref": "9e60e24790"}, ...]
    """
    deps = []
    try:
        content = toml_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return deps

    libraries_section = False
    for line in content.splitlines():
        stripped = line.strip()
        if stripped == "[libraries]":
            libraries_section = True
            continue
        if stripped.startswith("[") and stripped.endswith("]"):
            libraries_section = False
            continue
        if not libraries_section:
            continue

        m = re.match(
            r'\w[\w-]*\s*=\s*\{\s*module\s*=\s*"([^"]+)"\s*,\s*version\.ref\s*=\s*"([^"]+)"',
            stripped,
        )
        if not m:
            continue

        module_str = m.group(1)
        version_ref = m.group(2)

        gm = GITHUB_JITPACK_RE.match(module_str)
        if not gm:
            continue

        owner = gm.group(1)
        repo = gm.group(2)

        version_re = re.compile(
            rf'{re.escape(version_ref)}\s*=\s*"([a-f0-9]{{7,40}})"'
        )
        vm = version_re.search(content)
        if vm:
            deps.append({
                "owner": owner,
                "repo": repo,
                "ref": vm.group(1),
                "module": module_str,
            })

    return deps


def _github_zip_url(owner: str, repo: str, ref: str) -> str:
    return f"https://github.com/{owner}/{repo}/archive/{ref}.zip"


def download_dep(dep: dict) -> str | None:
    """
    下载 GitHub 仓库 zip 到 .dep_cache/{owner}_{repo}_{ref}/。
    如果已存在则跳过。
    返回解压后的根目录路径，失败返回 None。
    """
    owner = dep["owner"]
    repo = dep["repo"]
    ref = dep["ref"]
    cache_key = f"{owner}_{repo}_{ref}"
    dest = _cache_dir() / cache_key

    if dest.exists() and any(dest.rglob("src/main")):
        return str(dest)

    if dest.exists():
        shutil.rmtree(dest)

    url = _github_zip_url(owner, repo, ref)
    print(f"  Downloading {owner}/{repo}@{ref}...")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "spec-tools/1.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read()
    except Exception as e:
        print(f"  FAILED to download {url}: {e}")
        return None

    try:
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            top_dir = zf.namelist()[0].split("/")[0]
            zf.extractall(_cache_dir())
            extracted = _cache_dir() / top_dir
            if extracted != dest:
                extracted.rename(dest)
    except Exception as e:
        print(f"  FAILED to extract: {e}")
        return None

    print(f"  Cached at {dest}")
    return str(dest)


def parse_settings_gradle(settings_path: Path, project_root: str) -> list[str]:
    """
    解析 settings.gradle.kts 中的 includeBuild 指令（非注释行）。
    返回已解析为绝对路径的列表。
    """
    paths = []
    try:
        content = settings_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return paths

    root = Path(project_root).resolve()
    for m in re.finditer(r'includeBuild\(["\']([^"\']+)["\']', content):
        line_start = content.rfind("\n", 0, m.start()) + 1
        line = content[line_start:m.end()]
        if line.strip().startswith("//"):
            continue
        dep = (root / m.group(1)).resolve()
        if dep.exists():
            paths.append(str(dep))

    return paths


def resolve_dependencies(project_root: str) -> list[str]:
    """
    完整的依赖解析入口：
      1. 解析 settings.gradle(.kts) 中的 includeBuild（本地依赖）
      2. 解析 libs.versions.toml 中的 JitPack GitHub 依赖
      3. 自动下载缺失的远程依赖
    返回所有额外扫描根目录的路径列表。
    """
    root = Path(project_root).resolve()
    extra_roots = []

    for name in ("settings.gradle.kts", "settings.gradle"):
        sf = root / name
        if sf.exists():
            extra_roots.extend(parse_settings_gradle(sf, str(root)))
            break

    toml_path = root / "gradle" / "libs.versions.toml"
    if toml_path.exists():
        github_deps = parse_toml_versions(toml_path)
        for dep in github_deps:
            local_path = download_dep(dep)
            if local_path:
                extra_roots.append(local_path)

    return extra_roots
