#!/usr/bin/env python3
"""
gen-page-map.py — 从 features/business_*/Index.ets 自动扫描 Page struct 导出，
                  生成正确的 products/phone/src/main/ets/pages/Index.ets。

⚠️ 本脚本是 SKILL.md Phase 3 Step 4「壳工程」的标准工具，**避免靠记忆手写 PageMap 漏 NavDestination**。

用法：
  python3 assets/gen-page-map.py <project-root> [--initial PageName]

参数：
  project-root        鸿蒙工程根目录（含 products/ + features/）
  --initial NAME      入口路由名（默认 SplashPage；项目无该 page 时给报错提示）

行为：
  1. 扫 features/business_*/Index.ets 中所有形如 `export { *Page } from ...` 的导出
  2. 按 (page_name, owning_business) 收集，输出 import + if/else if 分支
  3. 渲染 assets/page-map.template.ets → 写到 products/phone/src/main/ets/pages/Index.ets
  4. 末尾跑一次 grep 静态校验，确保 NavDestination 真的在生成结果里
  5. 如果指定的 --initial 在收集到的 page 名里找不到 → 退出码 2 + 明确错误

退出码：
  0  生成成功且静态校验通过
  1  扫不到任何 Page 导出（feature Index.ets 还没写完）
  2  --initial 指定的入口页未注册
  3  渲染后静态校验失败（NavDestination 不在产物中——本脚本 bug，应回报）
"""
import argparse
import re
import sys
from pathlib import Path


PAGE_EXPORT_RE = re.compile(
    r"export\s*\{\s*([^}]+?)\s*\}\s*from\s*['\"]\./src/main/ets/pages/[^'\"]+['\"]",
    re.MULTILINE,
)
PAGE_NAME_RE = re.compile(r"\b([A-Z]\w*Page)\b")


def collect_pages(project_root: Path) -> dict[str, list[str]]:
    """{page_name: [business_module, ...]} — 一个 page 名理论上只该出现在一个 business"""
    out: dict[str, list[str]] = {}
    features = project_root / "features"
    if not features.is_dir():
        sys.stderr.write(f"✗ no features/ under {project_root}\n")
        sys.exit(1)
    for biz_dir in sorted(features.iterdir()):
        if not biz_dir.is_dir() or not biz_dir.name.startswith("business_"):
            continue
        idx = biz_dir / "Index.ets"
        if not idx.exists():
            continue
        text = idx.read_text(encoding="utf-8")
        for m in PAGE_EXPORT_RE.finditer(text):
            for sym in m.group(1).split(","):
                sym = sym.strip()
                pm = PAGE_NAME_RE.match(sym)
                if pm:
                    out.setdefault(pm.group(1), []).append(biz_dir.name)
    return out


def render(template_path: Path, pages: dict[str, list[str]], initial: str) -> str:
    if initial not in pages:
        sys.stderr.write(
            f"✗ initial page '{initial}' not found in any business Index.ets\n"
            f"  Available: {sorted(pages)}\n"
            f"  Use --initial to pick one of them.\n"
        )
        sys.exit(2)

    # imports — 一个 business 一行
    by_biz: dict[str, list[str]] = {}
    for page, bizs in pages.items():
        # 选最早出现的 business（去重）
        by_biz.setdefault(bizs[0], []).append(page)
    imports = []
    for biz in sorted(by_biz):
        names = ", ".join(sorted(by_biz[biz]))
        imports.append(f"import {{ {names} }} from '{biz}';")

    # branches — 4 空格缩进 + NavDestination 内部 6 空格
    indent = "      "
    branches = []
    for i, page in enumerate(sorted(pages)):
        kw = "if" if i == 0 else "} else if"
        branches.append(f"{indent}{kw} (name === '{page}') {{")
        branches.append(f"{indent}  {page}()")
    if branches:
        branches.append(f"{indent}}}")

    tpl = template_path.read_text(encoding="utf-8")
    return (
        tpl.replace("__ROUTE_IMPORTS__", "\n".join(imports))
        .replace("__INITIAL_PAGE__", initial)
        .replace("__ROUTE_BRANCHES__", "\n".join(branches))
    )


def static_check(generated: str) -> bool:
    """生成后必跑 — NavDestination 必须在 PageMap 内部"""
    if "NavDestination(" not in generated:
        return False
    # PageMap 段必须包含 NavDestination
    m = re.search(r"PageMap\s*\([^)]*\)\s*\{([\s\S]+?)^\s*\}\s*$", generated, re.M)
    if not m:
        return False
    return "NavDestination(" in m.group(1)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("project_root", type=Path)
    ap.add_argument("--initial", default="SplashPage")
    args = ap.parse_args()

    project = args.project_root.resolve()
    pages = collect_pages(project)
    if not pages:
        sys.stderr.write("✗ no Page exports found in features/business_*/Index.ets\n")
        return 1

    # 模板与本脚本同目录
    template = Path(__file__).parent / "page-map.template.ets"
    out = render(template, pages, args.initial)
    if not static_check(out):
        sys.stderr.write("✗ post-render static check failed: NavDestination wrapper missing — bug in template\n")
        return 3

    target = project / "products" / "phone" / "src" / "main" / "ets" / "pages" / "Index.ets"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(out, encoding="utf-8")
    sys.stdout.write(
        f"✓ wrote {target.relative_to(project)} ({len(pages)} routes, initial={args.initial})\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
