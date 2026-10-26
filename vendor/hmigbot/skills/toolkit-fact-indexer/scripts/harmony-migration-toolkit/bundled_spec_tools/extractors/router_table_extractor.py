"""
router_table_extractor.py

字符串路由框架解析 pass —— 识别 TheRouter / ARouter / WMRouter 这类
「注解声明 + 字符串路由」框架的页面跳转，补上 navigation_graph 里缺失的
Activity→Activity / Activity→Fragment 边。

四步（全部确定性静态分析，regex-first，无 LLM）：
  Step 1  建路由表    @Route(path=X) + 常量求值   → { 路由串: 目标类 }
  Step 2  wrapper白名单  识别 theRouter(path) 封装 → { 函数名 }
  Step 3  连边         调用点常量实参 → 路由表查 to → nav 边
  Step 4  兜底         运行时表达式解不出 → uncertain（不进主边集）

被 navigation_extractor.run() 调用：
  from extractors import router_table_extractor
  result = router_table_extractor.run(project_root, dep_roots, layout_resolver=...)
  all_edges.extend(result["edges"])
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Callable

from extractors import android_project


# ── 框架配置：注解名 + 直接 build 入口 + wrapper 基础白名单 ─────────────────
# 每家框架用同一个 pass。annotation 是贴在目标类头上的路由声明；build_entries 是
# 直接发起入口；wrapper_bases 是常见封装函数名（项目自定义 wrapper 会额外扫出）。
_FRAMEWORKS = {
    "therouter": {
        "annotation": "Route",
        "build_entries": ("TheRouter.build",),
        "wrapper_bases": ("theRouter", "theRouterFragment", "theRouterIntent"),
    },
    "arouter": {
        "annotation": "Route",
        "build_entries": ("ARouter.getInstance().build",),
        "wrapper_bases": (),   # ARouter 项目自定义 wrapper 靠名称启发式检出
    },
    "wmrouter": {
        "annotation": "RouterUri",
        "build_entries": ("Router.startUri",),
        "wrapper_bases": (),
    },
}

# 注解名集合（@Route / @RouterUri）
_ANNOTATION_NAMES = {fw["annotation"] for fw in _FRAMEWORKS.values()}
# 直接 build 入口（求值实参用）
_BUILD_ENTRIES = tuple(e for fw in _FRAMEWORKS.values() for e in fw["build_entries"])
# wrapper 基础白名单
_WRAPPER_BASES = frozenset(w for fw in _FRAMEWORKS.values() for w in fw["wrapper_bases"])

# 发起终结符：调用链里出现这些才算真发起（过滤 build 后不 navigation 的）
_DISPATCH_TERMINALS = ("navigation", "createFragment", "createIntent", "navigationForResult", "startUri")


# ── Step 1a: 收集常量定义 ────────────────────────────────────────────────
# const val NAME = "..."  /  const val NAME = A + B  /  static final String NAME = ...
_CONST_KT = re.compile(
    r'(?:const\s+val|val)\s+([A-Za-z_]\w*)\s*(?::\s*String\s*)?=\s*([^\n]+)'
)
_CONST_JAVA = re.compile(
    r'(?:static\s+final\s+String|final\s+static\s+String)\s+([A-Za-z_]\w*)\s*=\s*([^;\n]+)'
)
# 找 object / companion object 名字（给常量加限定前缀）
_OBJECT_DECL = re.compile(r'\bobject\s+([A-Za-z_]\w*)')


def _iter_sources(project_root: str, dep_roots: list[str] | None) -> list[tuple[Path, str]]:
    """返回 [(path, source)]，覆盖主工程 + 依赖库。"""
    out: list[tuple[Path, str]] = []
    roots = [project_root, *(dep_roots or [])]
    seen: set[str] = set()
    for r in roots:
        for p in android_project.source_files(r):
            key = str(p)
            if key in seen:
                continue
            seen.add(key)
            try:
                out.append((p, p.read_text(encoding="utf-8", errors="ignore")))
            except OSError:
                continue
    return out


def _collect_constants(sources: list[tuple[Path, str]]) -> dict[str, str]:
    """
    收集常量原始表达式。key 同时索引限定名 (Obj.NAME) 和简单名 (NAME)。
    简单名多处定义时：若所有定义求值后相等（常见：export 常量类 + 工具类私有副本，
    值一致）则保留；值不一致才丢弃（避免误连）。
    返回 { name: raw_rhs }（raw_rhs 是可被 _eval_expr 求值的表达式串）。
    """
    raw: dict[str, str] = {}
    bare_defs: dict[str, list[str]] = {}
    for path, source in sources:
        obj_names = _OBJECT_DECL.findall(source)
        obj = obj_names[0] if obj_names else ""
        is_java = path.suffix == ".java"
        pat = _CONST_JAVA if is_java else _CONST_KT
        for m in pat.finditer(source):
            name, rhs = m.group(1), m.group(2).strip().rstrip(";").strip()
            if '"' not in rhs and not re.search(r'[A-Z_]{2,}', rhs):
                continue
            if obj:
                raw[f"{obj}.{name}"] = rhs
            bare_defs.setdefault(name, []).append(rhs)

    # 简单名去冲突：值一致才保留
    tmp_cache: dict[str, str | None] = {}
    for name, rhs_list in bare_defs.items():
        if "." in name:
            continue
        if len(rhs_list) == 1:
            raw.setdefault(name, rhs_list[0])
            continue
        # 多处定义 → 求值比对
        vals = set()
        for rhs in rhs_list:
            v = _eval_expr(rhs, raw, tmp_cache, frozenset())
            vals.add(v)
        if len(vals) == 1 and next(iter(vals)) is not None:
            # 一致：用字面量形式存回（避免再次歧义）
            raw[name] = '"' + next(iter(vals)) + '"'
        # 不一致：不加入 raw（bare 名不可靠）
    return raw


# ── Step 1b: 常量求值（编译期折叠） ──────────────────────────────────────
_STR_LIT = re.compile(r'"([^"\\]*(?:\\.[^"\\]*)*)"')


def _eval_const(name: str, raw: dict[str, str], cache: dict[str, str | None],
                stack: frozenset[str] = frozenset()) -> str | None:
    """
    递归求值一个常量为字符串。支持：字面量、A + B 拼接、引用其它常量。
    失败（含函数调用/未知变量/循环引用）返回 None。
    """
    if name in cache:
        return cache[name]
    if name in stack:  # 循环引用
        return None
    expr = raw.get(name)
    if expr is None:
        # name 可能本身就是限定名的尾段，试简单名
        return None
    result = _eval_expr(expr, raw, cache, stack | {name})
    cache[name] = result
    return result


def _eval_expr(expr: str, raw: dict[str, str], cache: dict[str, str | None],
               stack: frozenset[str]) -> str | None:
    """求值一个表达式（字面量 / 拼接 / 常量引用）。"""
    expr = expr.strip()
    # 纯字面量
    m = _STR_LIT.fullmatch(expr)
    if m:
        return m.group(1)
    # 顶层按 + 切分（不在引号内的 +）
    parts = _split_top_level_plus(expr)
    if len(parts) > 1:
        acc = ""
        for part in parts:
            v = _eval_expr(part, raw, cache, stack)
            if v is None:
                return None
            acc += v
        return acc
    # 单项且非字面量 → 常量引用
    token = expr.strip()
    m2 = _STR_LIT.fullmatch(token)
    if m2:
        return m2.group(1)
    if re.fullmatch(r'[A-Za-z_][\w.]*', token):
        # 先按原名，再按尾段简单名
        v = _eval_const(token, raw, cache, stack)
        if v is not None:
            return v
        tail = token.rsplit(".", 1)[-1]
        if tail != token:
            return _eval_const(tail, raw, cache, stack)
        return None
    return None


def _split_top_level_plus(expr: str) -> list[str]:
    """按不在引号内的 '+' 切分表达式。"""
    parts: list[str] = []
    buf = ""
    in_str = False
    esc = False
    for ch in expr:
        if esc:
            buf += ch
            esc = False
            continue
        if ch == "\\":
            buf += ch
            esc = True
            continue
        if ch == '"':
            in_str = not in_str
            buf += ch
            continue
        if ch == "+" and not in_str:
            parts.append(buf)
            buf = ""
            continue
        buf += ch
    parts.append(buf)
    return [p for p in parts if p.strip()]


# ── Step 1c: 建路由表 { 路由串: 目标类 } ─────────────────────────────────
# @Route(path = X) 或 @Route(path = "..."), 后跟 class Xxx
_ROUTE_ANNOTATION = re.compile(
    r'@(' + '|'.join(re.escape(a) for a in _ANNOTATION_NAMES) + r')\s*\('
    r'[^)]*?\bpath\s*=\s*([^,)\n]+)[^)]*\)'
    r'(?P<after>(?:\s*@\w+\s*(?:\([^)]*\))?)*\s*'          # 跳过后续注解
    r'(?:public\s+|final\s+|open\s+|internal\s+|abstract\s+|data\s+|sealed\s+)*'
    r'class\s+([A-Za-z_]\w*))',
    re.DOTALL,
)


def _build_route_table(sources: list[tuple[Path, str]], raw_consts: dict[str, str],
                       const_cache: dict[str, str | None]) -> tuple[dict, int, int]:
    """
    返回 (route_table, decl_total, decl_resolved)。
    route_table: { route_string: {class, path_expr, decl_file, decl_line} }
    """
    route_table: dict[str, dict] = {}
    decl_total = 0
    decl_resolved = 0
    for path, source in sources:
        for m in _ROUTE_ANNOTATION.finditer(source):
            decl_total += 1
            path_expr = m.group(2).strip()
            target_class = m.group(4)
            route_str = _eval_expr(path_expr, raw_consts, const_cache, frozenset())
            if not route_str:
                continue
            decl_resolved += 1
            line = source[: m.start()].count("\n") + 1
            route_table[route_str] = {
                "class": target_class,
                "path_expr": path_expr,
                "decl_file": _rel(path),
                "decl_line": line,
            }
    return route_table, decl_total, decl_resolved


# ── Step 2: wrapper 白名单 ───────────────────────────────────────────────
# fun theRouter(path: String ...) = ... TheRouter.build(path) ...
_WRAPPER_DEF = re.compile(
    r'\bfun\s+(?:<[^>]+>\s*)?(?:[A-Za-z_][\w.]*\.)?'     # 可选泛型 + 可选接收者
    r'([A-Za-z_]\w*)\s*\('                                # 函数名
    r'\s*([A-Za-z_]\w*)\s*:\s*String'                     # 首个 String 形参
)


# 泛函数名 denylist：SDK 方法或通用 builder，绝不当路由 wrapper
_WRAPPER_DENYLIST = frozenset({
    "build", "startActivity", "startActivityForResult", "getFragmentTarget",
    "with", "apply", "let", "run", "also",
})


def _collect_wrappers(sources: list[tuple[Path, str]]) -> set[str]:
    """
    识别封装函数：首参 String，函数体内 build(该参)。返回函数名集合。
    为压制误报，检测出的名字必须满足以下之一：
      - 在基础白名单 _WRAPPER_BASES 中，或
      - 名字里含 rout / navigat（大小写不敏感）
    且不在 denylist 中。
    """
    wrappers: set[str] = set(_WRAPPER_BASES)
    for _path, source in sources:
        for m in _WRAPPER_DEF.finditer(source):
            fn_name, param = m.group(1), m.group(2)
            if fn_name in _WRAPPER_DENYLIST:
                continue
            window = source[m.end(): m.end() + 400]
            if not re.search(r'\.build\s*\(\s*' + re.escape(param) + r'\b', window):
                continue
            if fn_name in _WRAPPER_BASES or re.search(r'rout|navigat', fn_name, re.I):
                wrappers.add(fn_name)
    # 基础白名单里若混入 denylist（配置疏漏）也剔除
    return {w for w in wrappers if w not in _WRAPPER_DENYLIST}


# ── Step 3: 连边 ─────────────────────────────────────────────────────────
def _first_arg(call_text: str) -> str | None:
    """从 'foo(ARG, ...)' 里取第一个实参（顶层逗号切分）。"""
    depth = 0
    in_str = False
    esc = False
    buf = ""
    started = False
    for ch in call_text:
        if not started:
            if ch == "(":
                started = True
            continue
        if esc:
            buf += ch; esc = False; continue
        if ch == "\\":
            buf += ch; esc = True; continue
        if ch == '"':
            in_str = not in_str; buf += ch; continue
        if in_str:
            buf += ch; continue
        if ch in "([{":
            depth += 1; buf += ch; continue
        if ch in ")]}":
            if depth == 0:
                break
            depth -= 1; buf += ch; continue
        if ch == "," and depth == 0:
            break
        buf += ch
    arg = buf.strip()
    return arg or None


def _class_of_line(source: str, pos: int) -> str:
    """找 pos 之前最近的 class/object 声明名作为 from。"""
    head = source[:pos]
    names = re.findall(r'\b(?:class|object|interface)\s+([A-Za-z_]\w*)', head)
    return names[-1] if names else ""


def _collect_edges(sources: list[tuple[Path, str]], route_table: dict,
                   raw_consts: dict[str, str], const_cache: dict[str, str | None],
                   wrappers: set[str],
                   layout_resolver: Callable[[str], str] | None) -> tuple[list[dict], list[dict], int]:
    """
    扫调用点连边。返回 (edges, unresolved, call_total)。
    """
    edges: list[dict] = []
    unresolved: list[dict] = []
    call_total = 0

    # 调用名集合：wrapper 函数名 + 直接 build 入口
    call_names = sorted(wrappers, key=len, reverse=True)
    build_names = _BUILD_ENTRIES

    for path, source in sources:
        # 3a: 直接 build 入口
        for entry in build_names:
            for m in re.finditer(re.escape(entry) + r'\s*\(', source):
                call_total += 1
                tail = source[m.end() - 1: m.end() - 1 + 300]
                _emit(source, path, m.start(), tail, route_table, raw_consts,
                      const_cache, layout_resolver, edges, unresolved, via_kind="direct")
        # 3b: wrapper 调用
        for fn in call_names:
            for m in re.finditer(r'\b' + re.escape(fn) + r'\s*\(', source):
                # 排除函数定义本身（前面是 fun）
                pre = source[max(0, m.start() - 6): m.start()]
                if pre.rstrip().endswith("fun"):
                    continue
                call_total += 1
                tail = source[m.end() - 1: m.end() - 1 + 300]
                _emit(source, path, m.start(), tail, route_table, raw_consts,
                      const_cache, layout_resolver, edges, unresolved, via_kind="wrapper")

    return edges, unresolved, call_total


def _emit(source: str, path: Path, pos: int, call_tail: str, route_table: dict,
          raw_consts: dict[str, str], const_cache: dict[str, str | None],
          layout_resolver: Callable[[str], str] | None,
          edges: list[dict], unresolved: list[dict], *, via_kind: str) -> None:
    """求值一个调用点的路由实参并连边（或记 unresolved）。"""
    arg = _first_arg(call_tail)
    line = source[:pos].count("\n") + 1
    from_class = _class_of_line(source, pos)
    if not arg:
        return
    route_str = _eval_expr(arg, raw_consts, const_cache, frozenset())
    if not route_str or route_str not in route_table:
        # 运行时表达式 / 未知常量 → uncertain
        unresolved.append({
            "from": from_class,
            "route_expr": arg[:120],
            "call_file": _rel(path),
            "call_line": line,
            "reason": "route_string_unresolved" if not route_str else "route_not_in_table",
        })
        return
    target = route_table[route_str]
    to_class = target["class"]
    if not from_class or from_class == to_class:
        return
    to_layout = layout_resolver(to_class) if layout_resolver else ""
    etype = "fragment" if "Fragment" in to_class else "activity"
    edges.append({
        "from": from_class,
        "to": to_class,
        "to_layout": to_layout,
        "type": etype,
        "via": "router:therouter",
        "trigger": f"route: {route_str}",
        "line": line,
        "confidence": "static",
        "evidence": {
            "call_file": _rel(path),
            "call_line": line,
            "route_string": route_str,
            "decl_file": target.get("decl_file", ""),
            "decl_line": target.get("decl_line", 0),
            "via_kind": via_kind,
        },
    })


def _rel(path: Path) -> str:
    """尽量返回 module/src/... 相对路径，退化为文件名。"""
    parts = path.as_posix().split("/")
    if "src" in parts:
        i = parts.index("src")
        start = max(0, i - 1)
        return "/".join(parts[start:])
    return path.name


# ── 入口 ─────────────────────────────────────────────────────────────────
def run(project_root: str, dep_roots: list[str] | None = None,
        layout_resolver: Callable[[str], str] | None = None) -> dict:
    """
    返回 {
      "edges": [...],            # 可直接并入 navigation_graph
      "route_table": {...},      # { 路由串: {class, ...} }
      "unresolved": [...],       # 运行时/未知 → uncertain
      "stats": {...},
    }
    """
    sources = _iter_sources(project_root, dep_roots)
    if not sources:
        return {"edges": [], "route_table": {}, "unresolved": [], "stats": {}}

    raw_consts = _collect_constants(sources)
    const_cache: dict[str, str | None] = {}

    route_table, decl_total, decl_resolved = _build_route_table(
        sources, raw_consts, const_cache
    )
    wrappers = _collect_wrappers(sources)
    edges, unresolved, call_total = _collect_edges(
        sources, route_table, raw_consts, const_cache, wrappers, layout_resolver
    )

    stats = {
        "route_decl_total": decl_total,
        "route_decl_resolved": decl_resolved,
        "route_table_size": len(route_table),
        "wrappers_detected": sorted(wrappers),
        "call_sites_total": call_total,
        "edges_connected": len(edges),
        "unresolved": len(unresolved),
    }
    return {
        "edges": edges,
        "route_table": route_table,
        "unresolved": unresolved,
        "stats": stats,
    }
