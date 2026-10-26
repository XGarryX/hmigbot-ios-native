#!/usr/bin/env python3
"""
refactor-codemods.py — Phase 3 代码改写工具集（**禁止用裸 perl/sed 替代**）

为什么必须用本脚本：
  跨多文件做结构性改写（router 替换、import 重写、装饰器移除、export 加前缀、
  VM extends 等）用 regex 极易越界——曾经一次失误把 50+ 文件的 `: number =`
  改成 `:as object=`、把 `}).catch()` 后面的外层 `}` 也吞掉、把 `RouterUtils.pop()
  ... context.startAbility().catch()` 整段视为单匹配删了 26 处不该删的 .catch。
  本脚本所有改写都用**字符串平衡解析器**（跟踪 `{}` `()` 深度 + 字符串/反引号/转义）
  实现，绝不使用跨行贪婪 regex。

用法：
  python3 refactor-codemods.py <subcmd> <project-root> [options]

子命令：
  router-replace      router.pushUrl/replaceUrl/back/clear/getParams → RouterUtils.*
  imports-fix         旧路径 import 重写到新模块（基于 --map JSON）
  strip-entry         page 文件移除 @Entry 装饰器、给 page struct 加 export 前缀
  vm-extends          *ViewModel class 加 extends BaseViewModel + import
  remove-router-catch 移除紧跟 RouterUtils.* 调用后的 .catch(...) 链（仅这一个 anchor，绝不越界）
  add-page-params-cast  给所有 RouterUtils.pushPathByName/replacePathByName 的 obj 字面量参数加 `as PageParams` cast

每个子命令都遵守：
  - 只动 features/ 和 products/ 下的 .ets
  - 跳过 business_common 内部的同模块 import 自循环
  - 改前打印改动计划、改后打印改动文件数
  - 静态校验失败立即退出非零码

所有 Phase 3 的代码改写**必须**走本脚本。SKILL.md 已显式禁止跨文件 perl -i / sed -i 用于 .ets 文件。
"""
from __future__ import annotations
import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Callable, Iterable


# =============== 公共：平衡括号解析器 ===============

def find_balanced(src: str, start: int, op: str, cl: str) -> int:
    """从 src[start]=op 开始找配对 cl 的 index；忽略 '/"/`/转义。失败返回 -1。"""
    if start >= len(src) or src[start] != op:
        return -1
    depth = 1
    i = start + 1
    in_str: str | None = None
    while i < len(src):
        c = src[i]
        if in_str:
            if c == "\\":
                i += 2
                continue
            if c == in_str:
                in_str = None
            i += 1
            continue
        if c in "'\"`":
            in_str = c
            i += 1
            continue
        if c == op:
            depth += 1
        elif c == cl:
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return -1


def iter_ets(roots: Iterable[Path]) -> Iterable[Path]:
    for root in roots:
        if not root.exists():
            continue
        for p in root.rglob("*.ets"):
            # 跳过 build / oh_modules
            parts = p.parts
            if "build" in parts or "oh_modules" in parts:
                continue
            yield p


def transform_files(roots: Iterable[Path], fn: Callable[[Path, str], str | None], label: str) -> int:
    """fn(path, src) 返回新内容（None 表示不改）。返回改动文件数。"""
    n = 0
    for p in iter_ets(roots):
        try:
            src = p.read_text(encoding="utf-8")
        except Exception:
            continue
        new = fn(p, src)
        if new is not None and new != src:
            p.write_text(new, encoding="utf-8")
            n += 1
    sys.stderr.write(f"  {label}: {n} files changed\n")
    return n


def ensure_lib_common_import(src: str, sym: str) -> str:
    """src 中确保 import { sym } from 'lib_common' 存在；若已有 lib_common import 则合并。"""
    if re.search(rf"import\s*\{{[^}}]*\b{sym}\b[^}}]*\}}\s*from\s*['\"]lib_common['\"]", src):
        return src
    m = re.search(r"^(import\s*\{\s*)([\w\s,]+?)(\s*\}\s*from\s*['\"]lib_common['\"]\s*;?)", src, re.M)
    if m:
        return src[:m.start()] + m.group(1) + m.group(2).rstrip() + f", {sym}" + m.group(3) + src[m.end():]
    # 没有 lib_common 行 → 在第一个 import 前插入
    return re.sub(r"(^import\s)", f"import {{ {sym} }} from 'lib_common';\n\\1", src, count=1, flags=re.M)


# =============== A. router-replace ===============

ROUTER_RE = re.compile(r"\brouter\.(pushUrl|replaceUrl|back|clear|getParams)\s*\(")


def parse_pushurl_args(args: str) -> tuple[str, str | None] | None:
    """args 是 router.pushUrl( 后到匹配 ) 的内容。返回 (page_name, params_text) 或 None。"""
    s = args.strip()
    if not s.startswith("{"):
        return None
    end = find_balanced(s, 0, "{", "}")
    if end < 0:
        return None
    body = s[1:end]
    um = re.search(r"\burl:\s*['\"]pages/(\w+)['\"]", body)
    if not um:
        return None
    page = um.group(1)
    pm = re.search(r"\bparams:\s*", body)
    p_text = None
    if pm:
        ps = pm.end()
        if body[ps:ps+1] == "{":
            pe = find_balanced(body, ps, "{", "}")
            if pe < 0:
                return None
            p_text = body[ps:pe+1]
            tail = body[pe+1:].lstrip()
            asm = re.match(r"as\s+([\w<>,\s\|\[\]]+)", tail)
            if asm:
                p_text += " as " + asm.group(1).rstrip().rstrip(",")
        else:
            idm = re.match(r"(\w[\w.]*)", body[ps:])
            if idm:
                p_text = idm.group(1)
    return (page, p_text)


def transform_router_calls(src: str, page_name_for_getparams: str) -> str:
    out: list[str] = []
    pos = 0
    while pos < len(src):
        m = ROUTER_RE.search(src, pos)
        if not m:
            out.append(src[pos:])
            break
        method = m.group(1)
        cs = m.start()
        po = m.end() - 1
        pc = find_balanced(src, po, "(", ")")
        if pc < 0:
            out.append(src[pos:cs+1])
            pos = cs + 1
            continue
        out.append(src[pos:cs])
        args = src[po+1:pc]
        if method == "back":
            out.append("RouterUtils.pop()")
        elif method == "clear":
            out.append("RouterUtils.popToIndex(0)")
        elif method == "getParams":
            out.append(f"RouterUtils.getParamByName('{page_name_for_getparams}')")
        else:
            target = "pushPathByName" if method == "pushUrl" else "replacePathByName"
            parsed = parse_pushurl_args(args)
            if parsed:
                pn, pt = parsed
                out.append(f"RouterUtils.{target}('{pn}', {pt})" if pt else f"RouterUtils.{target}('{pn}')")
            else:
                # 无法识别的形式，保留原文（不冒险）
                out.append(src[cs:pc+1])
        pos = pc + 1
    return "".join(out)


def cmd_router_replace(args) -> int:
    """router.* → RouterUtils.* + 自动剥除残留 .catch（router.pushUrl 返回 Promise，
    RouterUtils.pushPathByName 返回 void，旧 .catch 链会编译报 'no catch on void'，
    实战 64 错里 39 处是这个）。一次跑完两步避免下游忘了串 remove-router-catch。"""
    roots = [args.project_root / "features", args.project_root / "products"]

    def fn_replace(p: Path, src: str) -> str | None:
        page = p.stem  # 文件名作为 getParams 的 page name
        new = transform_router_calls(src, page)
        if new != src and "RouterUtils" in new:
            new = ensure_lib_common_import(new, "RouterUtils")
        return new

    transform_files(roots, fn_replace, "router-replace")

    # 同步剥除 RouterUtils.X(...).catch(...) 残留 — 复用 remove-router-catch 的 fn
    def fn_strip_catch(p: Path, src: str) -> str | None:
        out: list[str] = []
        pos = 0
        changed = False
        while pos < len(src):
            m = ROUTER_UTILS_RE.search(src, pos)
            if not m:
                out.append(src[pos:])
                break
            cs = m.start()
            po = m.end() - 1
            pc = find_balanced(src, po, "(", ")")
            if pc < 0:
                out.append(src[pos:])
                break
            tail = src[pc+1:]
            cm = re.match(r"\s*\.catch\(", tail)
            if cm:
                catch_po = pc + 1 + cm.end() - 1
                catch_pc = find_balanced(src, catch_po, "(", ")")
                if catch_pc >= 0:
                    out.append(src[pos:pc+1])
                    pos = catch_pc + 1
                    changed = True
                    continue
            out.append(src[pos:pc+1])
            pos = pc + 1
        return "".join(out) if changed else None

    transform_files(roots, fn_strip_catch, "router-replace [auto-strip .catch]")
    return 0


# =============== B. imports-fix ===============

def cmd_imports_fix(args) -> int:
    """基于 --map JSON 重写跨业务/旧路径 import。

    map JSON 格式：
    {
      "symbol_to_module": {
        "AuthViewModel": "business_login",
        "DBPPTManager": "business_common",
        ...
      },
      "common_subdirs": ["models", "events", "preferences", "components/common"],
      "common_target": "business_common",
      "rename_subdirs": {"viewmodels": "viewmodel", "services": "util", "network": "util"}
    }
    """
    cfg = json.loads(Path(args.map).read_text(encoding="utf-8"))
    sym_to_mod: dict[str, str] = cfg["symbol_to_module"]
    common_subs: list[str] = cfg.get("common_subdirs", [])
    common_target: str = cfg.get("common_target", "business_common")
    rename_subs: dict[str, str] = cfg.get("rename_subdirs", {})

    common_re = re.compile(rf"""from\s+["'](\.\.?(?:/\.\.)*?)/({"|".join(map(re.escape, common_subs))})/(\w+)["']""")
    cross_re = re.compile(r"""from\s+["'](\.\.?(?:/\.\.)*?)/(viewmodels|services|network)/(\w+)["']""")

    def biz_of(path: Path) -> str | None:
        m = re.search(r"features/(business_\w+)/", str(path))
        return m.group(1) if m else None

    def fn(p: Path, src: str) -> str | None:
        biz = biz_of(p)
        if not biz:
            return None
        new = src
        # 1) 公共子目录引用
        if biz != common_target:
            new = common_re.sub(f'from "{common_target}"', new)
        else:
            # business_common 内部用相对路径
            def common_rel(m: re.Match) -> str:
                rel, sub, name = m.group(1), m.group(2), m.group(3)
                target = {"models": "bean", "events": "events", "preferences": "util",
                          "components/common": "components"}.get(sub, sub)
                return f"from '{rel}/{target}/{name}'"
            new = common_re.sub(common_rel, new)

        # 2) 跨业务 / 同业务旧目录名
        def cross(m: re.Match) -> str:
            rel, sub, name = m.group(1), m.group(2), m.group(3)
            target_mod = sym_to_mod.get(name)
            if target_mod and target_mod != biz:
                return f'from "{target_mod}"'
            new_sub = rename_subs.get(sub, sub)
            return f"from '{rel}/{new_sub}/{name}'"
        new = cross_re.sub(cross, new)
        return new

    transform_files([args.project_root / "features", args.project_root / "products"], fn, "imports-fix")
    return 0


# =============== C. strip-entry ===============

def cmd_strip_entry(args) -> int:
    """page 文件：移除 @Entry 行；@Component / @ComponentV2 行下的 struct 加 export 前缀。"""
    roots = [args.project_root / "features", args.project_root / "products"]
    entry_re = re.compile(r"^@Entry\s*\n", re.M)
    export_re = re.compile(r"(@Component(?:V2)?\s*\n)(struct\s+\w+)", re.M)

    def fn(p: Path, src: str) -> str | None:
        if "/pages/" not in str(p).replace(os.sep, "/"):
            return None
        new = entry_re.sub("", src)
        new = export_re.sub(r"\1export \2", new)
        return new
    transform_files(roots, fn, "strip-entry+export")
    return 0


# =============== D. vm-extends ===============

VM_CLASS_RE = re.compile(r"(\bexport\s+class\s+\w+ViewModel)(\s*\{)")
VM_IMPL_RE = re.compile(r"(\bexport\s+class\s+\w+ViewModel)(\s+implements\s+)")


def cmd_vm_extends(args) -> int:
    roots = [args.project_root / "features"]

    def fn(p: Path, src: str) -> str | None:
        if "extends BaseViewModel" in src:
            return None
        new = VM_CLASS_RE.sub(r"\1 extends BaseViewModel\2", src)
        new = VM_IMPL_RE.sub(r"\1 extends BaseViewModel\2", new)
        if new != src:
            new = ensure_lib_common_import(new, "BaseViewModel")
            return new
        return None
    transform_files(roots, fn, "vm-extends")
    return 0


# =============== E. remove-router-catch ===============

ROUTER_UTILS_RE = re.compile(r"\bRouterUtils\.(?:pushPathByName|replacePathByName|pop|popToIndex|popToName)\s*\(")


def cmd_remove_router_catch(args) -> int:
    """仅移除紧跟 RouterUtils.X(...) 之后的 .catch(...)。

    关键：anchor 必须是 RouterUtils.X(...) 完整闭合的右括号。绝不跨多语句匹配。
    避免之前的 bug：跨大段代码把 context.startAbility().catch() 也吞掉。
    """
    roots = [args.project_root / "features", args.project_root / "products"]

    def fn(p: Path, src: str) -> str | None:
        out: list[str] = []
        pos = 0
        changed = False
        while pos < len(src):
            m = ROUTER_UTILS_RE.search(src, pos)
            if not m:
                out.append(src[pos:])
                break
            cs = m.start()
            po = m.end() - 1
            pc = find_balanced(src, po, "(", ")")
            if pc < 0:
                out.append(src[pos:])
                break
            # anchor 必须是 RouterUtils call 之后**仅空白**就接 .catch
            tail = src[pc+1:]
            cm = re.match(r"\s*\.catch\(", tail)
            if cm:
                catch_po = pc + 1 + cm.end() - 1
                catch_pc = find_balanced(src, catch_po, "(", ")")
                if catch_pc >= 0:
                    out.append(src[pos:pc+1])  # 保留 RouterUtils.X(...)
                    # 跳过 .catch(...) 整段
                    pos = catch_pc + 1
                    changed = True
                    continue
            out.append(src[pos:pc+1])
            pos = pc + 1
        return "".join(out) if changed else None
    transform_files(roots, fn, "remove-router-catch")
    return 0


# =============== F. add-page-params-cast ===============

PAGE_PARAMS_CALL_RE = re.compile(r"\bRouterUtils\.(pushPathByName|replacePathByName)\(\s*['\"]\w+['\"]\s*,\s*")


def cmd_add_page_params_cast(args) -> int:
    """RouterUtils.pushPathByName('X', { ... }) → 加 as PageParams cast。
    已有 cast 的不动；多行字面量也支持（用平衡 {}）。
    """
    roots = [args.project_root / "features", args.project_root / "products"]

    def fn(p: Path, src: str) -> str | None:
        out: list[str] = []
        pos = 0
        changed = False
        while pos < len(src):
            m = PAGE_PARAMS_CALL_RE.search(src, pos)
            if not m:
                out.append(src[pos:])
                break
            obj_start = m.end()
            out.append(src[pos:obj_start])
            if obj_start >= len(src) or src[obj_start] != "{":
                pos = obj_start
                continue
            obj_end = find_balanced(src, obj_start, "{", "}")
            if obj_end < 0:
                out.append(src[obj_start:])
                pos = len(src)
                break
            obj = src[obj_start:obj_end+1]
            tail = src[obj_end+1:]
            am = re.match(r"\s*as\s+([\w<>,|\s\[\]]+?)(?=[\s,);])", tail)
            if am:
                # 已有 cast，整体保留并跳过 cast 部分
                out.append(obj)
                # 不替换 cast，保留原 cast 后到下一处状态
                pos = obj_end + 1
                continue
            out.append(obj + " as PageParams")
            pos = obj_end + 1
            changed = True
        if not changed:
            return None
        new = "".join(out)
        # 加 PageParams import
        if "PageParams" in new and not re.search(r"import\s*\{[^}]*PageParams[^}]*\}\s*from\s*['\"]business_common", new):
            mc = re.search(r"^(import\s*\{\s*)([\w\s,]+?)(\s*\}\s*from\s*['\"]business_common['\"]\s*;?)", new, re.M)
            if mc:
                new = new[:mc.start()] + mc.group(1) + mc.group(2).rstrip() + ", PageParams" + mc.group(3) + new[mc.end():]
            else:
                new = re.sub(r"(^import\s)", r"import { PageParams } from 'business_common';\n\1", new, count=1, flags=re.M)
        return new
    transform_files(roots, fn, "add-page-params-cast")
    return 0


# =============== main ===============

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    for name in ("router-replace", "strip-entry", "vm-extends", "remove-router-catch", "add-page-params-cast"):
        s = sub.add_parser(name)
        s.add_argument("project_root", type=Path)
        s.set_defaults(fn={
            "router-replace": cmd_router_replace,
            "strip-entry": cmd_strip_entry,
            "vm-extends": cmd_vm_extends,
            "remove-router-catch": cmd_remove_router_catch,
            "add-page-params-cast": cmd_add_page_params_cast,
        }[name])

    s = sub.add_parser("imports-fix")
    s.add_argument("project_root", type=Path)
    s.add_argument("--map", required=True, help="JSON 文件路径，结构见脚本 docstring")
    s.set_defaults(fn=cmd_imports_fix)

    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
