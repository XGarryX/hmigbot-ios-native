#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_static_runtime.py —— 落账期静态运行期 lint 的可导入内核（static_runtime_lint.py CLI / round0_precheck.py 共用）。

为什么要这个（AIPPT_930_token2 实装实证）：
  1. 冷启 ReferenceError：`static instance = new XxxApiService()` / 顶层 `export const svc = new Service()` 在**模块加载期**
     求值，构造函数触碰 getContext / AppStorage / preferences / window 这类运行期（EntryAbility.onCreate 之后）才就绪的
     单例 → 编译门看不见、装机即崩。fragments/runtime-patterns.md「模块加载期禁止触碰运行期才初始化的单例」有规则，
     本模块把它做成机械判据（module-init-runtime-dependency）。
  2. 首页顶部空白带：`getWindowAvoidArea(...).topRect.height`（px）直接当 vp 用在 padding({top}) 上。
     fragments/safearea.md 明令 avoid-area / windowRect 都是 px 须 px2vp()；本模块机械判（avoid-area-px-as-vp）。
  3. float.json 与安卓 dimens 同名异值（dimen-binding-literal-drift）：只在 spec/baseline/android-literals.json 存在时判。
  4. import 环 + 模块加载期求值 = TDZ 冷启崩（module-init-cycle-tdz）：ES 模块里 A↔B 互相 import，谁先被求值由入口决定；
     后求值那一方的绑定在前一方的**加载期**被读到就是 `ReferenceError: X is not initialized`。编译门看不见（类型都对），
     规则 1 也看不见（右值不触碰运行期单例，只是读了个同环模块的导出）。fragments/runtime-patterns.md 同节给规则文字。

判据（全部在**去注释、去字符串字面量**后的代码上匹配；宁可少报不可假报）：

  module-init-runtime-dependency（P0 / runtime）
    构造点（模块加载期求值的三种形态）：
      a) 顶层（花括号深度 0）`[export] const|let|var X = new Y(...)` / `= Y.getInstance()` / `= Y.instance`，
         `export default new Y()`；
      b) 类静态字段 `[public|private|protected] static [readonly] x = new Y(...)` / `= Y.getInstance()` / `= Y.instance`；
      c) 顶层裸语句 `new Y(...)` / `Y.getInstance()...`。
    以及 a/b 的右值**直接**含运行期标记（如 `static ctx = getContext()`）。
    Y 的解析：同文件 class 声明，否则沿本文件 `import { Y [as Z] } from './相对路径'` 在工程内解析到目标文件的 class；
    包导入（@kit/@ohos/第三方）与解析不到的类 → 不判。
    触碰判定 = Y 的 constructor 体 + 实例字段初始化式 + 静态字段初始化式 含任一标记：
      getContext( / AppStorage / AppStorageV2 / PersistenceV2 / preferences. / window. / getUIContext( / UIContext /
      router. / abilityContext / common.UIAbilityContext，
      或读取「只在 entryability/*.ets 里初始化的符号」（启发式：entryability 文件里 `Foo.bar = …` 的赋值目标 `Foo.bar`、
      `globalThis.x = …` 的 `globalThis.x`、`Foo.init|initialize|setup|configure|install|bootstrap(...)` 的
      `Foo.instance` / `Foo.getInstance(` / `Foo.shared` / `Foo.current`）。
    一跳链：Y 的构造链里再 `new Z()` / `Z.getInstance()` / `Z.instance` → 按同法解析 Z（只追一跳）。
    不判的形态（负例）：惰性 getter（`static get instance() { … new Y() … }`）、函数体内条件构造、struct 实例字段
    （组件构造期而非模块加载期）、`() => new Y()` 之类的延迟表达式。

  module-init-cycle-tdz（P0 / runtime）
    ① 建 ES 模块 import 图：只认相对路径导入（包导入不参与环）；`import type` / 导入名在去注释去字面量的代码里**从未按值
       使用**（典型值位 `new X` / `X.y` / `X(` / `instanceof X` / `extends X` / 实参·右值；或抹掉类型标注 `: T`、`as T`、
       泛型实参 `<…>`、`implements` 之后名字仍在——两条口径取并）→ 编译期擦除，不成运行期边；
       `export … from` 计边。
    ② Tarjan 求强连通分量（size>1）= import 环。
    ③ 环内文件在**模块加载期**读取来自同环模块的绑定 → 判：加载期 = 顶层语句 / 顶层 `const|let|var` 初始化 / 类体第一层
       `static` 字段初始化式 / `class X extends Y` 的 Y。不算加载期：函数体、方法体、getter 体、`import`/`export {…}`/
       `export … from` 语句本身、类型标注位置（`: T` / `as T` / 泛型实参 `<…>` / `implements`）、箭头与函数表达式的体
       （`const f = () => new Cyc()` 只是造了个闭包）、函数形参默认值。
    环外的互相 import 不判（正常依赖）；环内但加载期不读对方绑定也不判（只在函数里用 = 安全）。

  avoid-area-px-as-vp（P1 / visual）
    语句含 `getWindowAvoidArea(` / `.topRect.height` / `.bottomRect.height` / `.leftRect.width` / `.rightRect.width` /
    `getWindowProperties().windowRect.*` / `getWindowProperties().drawableRect.*` 且该处未被 `px2vp(` 包裹时：
      · 语句本身就是尺寸上下文（`.padding( .margin( .height( .width( .size( .offset( .position(` 或 `top:|bottom:|left:|right:`
        键）→ 直接判；
      · 语句是赋值（`const x =` / `this.f =` / `Obj.f =` / `AppStorage.setOrCreate('k', …)`）→ 追该字段/键的后续使用：
        `this.f`/局部量只查同文件，`Obj.f` 与 AppStorage 键（经 @StorageProp/@StorageLink('k') 声明的变量）查全部扫描文件；
        有一处在尺寸上下文里未经 px2vp( 使用 → 判在赋值行并附使用位置；从未在尺寸上下文使用 → 不判（可能后续再转换）。
      · `let area = win.getWindowAvoidArea(t)`（取对象非取数）不判——数值读取处另行匹配。

  dimen-binding-literal-drift（P2 / visual）
    仅当 spec/baseline/android-literals.json 存在：对扫描文件里的 `$r('app.float.<name>')`，若 <name>（安卓 dimens 名经
    seed_resources 同款 sanitize）也在 android-literals values_map.dimens 里、且模块 float.json 里该名的数值 ≠ 安卓值
    → 每名一条，file = 该 float.json。

--fix（机械修复，幂等、只做安全变换；其余一律留 finding 给模型）：
  · avoid-area-px-as-vp：把违规的 px 取值表达式原地包成 `px2vp(...)`——仅限简单成员链
    （`a.b.topRect.height` / `win.getWindowAvoidArea(x.y).bottomRect.height` / `w.getWindowProperties().windowRect.width`），
    已包裹 / 可选链 / 链前后还有调用或下标的一律不改；
  · module-init-runtime-dependency：仅限类内单行 `[修饰符] static [readonly] <name>[: T] = new Y(args);` →
    私有静态后备字段 `_<name>: T | undefined` + 惰性 `static get <name>(): T`（类名取自包围的 class 头；
    工程内任何 `Cls.<name> =` / 类内 `this.<name> =` 赋值、或已存在 `_<name>` 成员 → 不改）；
    顶层 `export const x = new Y()` 不自动改（调用方 import 的是值），留 finding。
  · module-init-cycle-tdz：同一套惰性 getter 变换，但右值放宽到**任何单行表达式**——类型取显式 `: T` 标注，
    没标注则取 `new Y(...)` 的 Y；两者都拿不到（如 `static x = someConst;` 无标注）→ 不改留 finding。
    读取点在顶层语句 / 顶层 const 的一律不自动改（改法要看调用方，留给模型断环）。
  修复后重新 lint，JSON 多出 fixed:[{code,file,line,detail}]，findings 为修复后剩余。

Python 3.9 兼容、stdlib only。
"""

from __future__ import annotations

import json
import re
from pathlib import Path

SKIP_PARTS = {"build", "oh_modules", "__probe", "node_modules", ".preview", ".hvigor", ".git", ".idea", ".cxx"}

FIX_MODULE_INIT = "改为惰性 getter / 首次使用时构造（见 fragments/runtime-patterns.md 模块加载期一节）"
FIX_AVOID_AREA = "取值后先 px2vp() 再存入字段 / 用作尺寸（见 fragments/safearea.md：avoid-area 与 windowRect 都是 px）"
FIX_DIMEN_DRIFT = "以安卓 dimens 值为准修正 float.json 该条目（dp→vp / sp→fp 等值），或改引用正确的资源名"
FIX_CYCLE_TDZ = ("断开 import 环（把双方共用的类型/常量抽到第三个模块），或把加载期读取改成惰性 getter / 首次使用时再读"
                 "（见 fragments/runtime-patterns.md 模块加载期一节）")

# ── 运行期标记（在去注释/去字符串代码上匹配）────────────────────────────────────
_MARKERS = (
    (re.compile(r"\bgetContext\s*\("), "getContext("),
    (re.compile(r"\bAppStorageV2\b"), "AppStorageV2"),
    (re.compile(r"\bAppStorage\b"), "AppStorage"),
    (re.compile(r"\bPersistenceV2\b"), "PersistenceV2"),
    (re.compile(r"(?<![\w$.])preferences\."), "preferences."),
    (re.compile(r"(?<![\w$.])window\."), "window."),
    (re.compile(r"\bgetUIContext\s*\("), "getUIContext("),
    (re.compile(r"\bUIContext\b"), "UIContext"),
    (re.compile(r"(?<![\w$.])router\."), "router."),
    (re.compile(r"\babilityContext\b"), "abilityContext"),
    (re.compile(r"\bcommon\.UIAbilityContext\b"), "common.UIAbilityContext"),
)

_ENTRY_ASSIGN_RE = re.compile(r"\b([A-Z][\w$]*)\.([\w$]+)\s*=(?!=)")
_ENTRY_GLOBAL_RE = re.compile(r"\bglobalThis\.([\w$]+)\s*=(?!=)")
_ENTRY_INIT_CALL_RE = re.compile(r"\b([A-Z][\w$]*)\.(?:init|initialize|initialise|setup|configure|install|bootstrap)\w*\s*\(")
_ENTRY_INIT_SKIP = {"Promise", "Object", "Array", "JSON", "Math", "Date", "String", "Number", "AppStorage",
                    "AppStorageV2", "PersistenceV2", "Reflect", "Symbol"}

_TOP_DECL_RE = re.compile(r"^\s*(?:export\s+)?(?:const|let|var)\s+([\w$]+)\s*(?::\s*[^=]+?)?\s*=\s*(.+?)\s*;?\s*$")
_TOP_DEFAULT_RE = re.compile(r"^\s*export\s+default\s+(.+?)\s*;?\s*$")
_TOP_BARE_RE = re.compile(r"^\s*((?:new\s+[\w$]+|[\w$]+\.getInstance)\s*\(.*)$")
_STATIC_FIELD_RE = re.compile(
    r"^\s*(?:(?:public|private|protected)\s+)?static\s+(?:readonly\s+)?([\w$]+)\s*(?:[?!])?\s*(?::\s*[^=]+?)?\s*=\s*(.+?)\s*;?\s*$")
_CTOR_NEW_RE = re.compile(r"^new\s+([\w$]+)\s*\(")
_CTOR_GETINST_RE = re.compile(r"^([\w$]+)\.getInstance\s*\(")
_CTOR_INSTANCE_RE = re.compile(r"^([\w$]+)\.instance\b")
_BODY_NEW_RE = re.compile(r"\bnew\s+([A-Z][\w$]*)\s*\(")
_BODY_GETINST_RE = re.compile(r"\b([A-Z][\w$]*)\.getInstance\s*\(")
_BODY_INSTANCE_RE = re.compile(r"\b([A-Z][\w$]*)\.instance\b")
_CLASS_RE = re.compile(r"\b(?:export\s+)?(?:default\s+)?(?:abstract\s+)?class\s+([\w$]+)\b[^{;]*\{")
_DEFAULT_CLASS_RE = re.compile(r"\bexport\s+default\s+(?:abstract\s+)?class\s+([\w$]+)")
_IMPORT_RE = re.compile(r"\bimport\s+(?:type\s+)?([^;]*?)\s+from\s+(['\"])([^'\"]+)\2", re.S)
_FIELD_INIT_RE = re.compile(
    r"^\s*(?:(?:public|private|protected|readonly|declare|override)\s+)*(?!static\b)(?!get\b)(?!set\b)([\w$]+)\s*(?:[?!])?\s*(?::\s*[^=]+?)?\s*=\s*(.+)$", re.S)
_STATIC_INIT_RE = re.compile(
    r"^\s*(?:(?:public|private|protected)\s+)*static\s+(?:readonly\s+)?([\w$]+)\s*(?:[?!])?\s*(?::\s*[^=]+?)?\s*=\s*(.+)$", re.S)

# ── avoid-area ────────────────────────────────────────────────────────────────
_AREA_RE = re.compile(r"getWindowAvoidArea\s*\(|\.(?:topRect|bottomRect)\.height\b|\.(?:leftRect|rightRect)\.width\b"
                      r"|getWindowProperties\s*\(\s*\)\s*\.\s*(?:windowRect|drawableRect)\s*\.")
_AREA_NUMERIC_RE = re.compile(r"\.(?:topRect|bottomRect)\.height\b|\.(?:leftRect|rightRect)\.width\b"
                              r"|getWindowProperties\s*\(\s*\)\s*\.\s*(?:windowRect|drawableRect)\s*\.\s*[\w$]+")
_DIM_CALL_RE = re.compile(r"\.(?:padding|margin|height|width|size|offset|position|translate|lineHeight|borderWidth|borderRadius)\s*\(")
_DIM_KEY_RE = r"\b(?:top|bottom|left|right|start|end|height|width|x|y)\s*:\s*"
_ASSIGN_LOCAL_RE = re.compile(r"^\s*(?:export\s+)?(?:const|let|var)\s+([\w$]+)\s*(?::\s*[^=]+?)?\s*=(?!=)")
_ASSIGN_THIS_RE = re.compile(r"^\s*this\.([\w$]+)\s*=(?!=)")
_ASSIGN_OBJ_RE = re.compile(r"^\s*([\w$]+(?:\.[\w$]+)*)\.([\w$]+)\s*=(?!=)")
_ASSIGN_STORAGE_RE = re.compile(r"\bAppStorage\s*\.\s*(?:setOrCreate|set)\s*(?:<[^>]*>)?\s*\(\s*['\"]([\w$.-]+)['\"]")

# ── import 环（TDZ）────────────────────────────────────────────────────────────
_EXPORT_FROM_RE = re.compile(r"\bexport\s+(?:\*(?:\s+as\s+[\w$]+)?|\{[^}]*\})\s*from\s*(['\"])([^'\"]+)\1")
_IMPORT_STMT_RE = re.compile(r"\bimport\s[^;]*?from\s*(['\"])[^'\"]+\1\s*;?", re.S)
_TYPE_ANNOT_RE = re.compile(r":\s*[\w.<>\[\]| ]+(?=[=,;)]|$)")
_AS_TYPE_RE = re.compile(r"\bas\s+[\w.<>\[\]]+")
_IMPLEMENTS_RE = re.compile(r"\bimplements\s+[\w.<>, ]+")
# 顶层语句里不算「加载期求值」的头（函数/方法/类型声明/再导出）
_NOT_LOAD_TIME_HEAD_RE = re.compile(
    r"^\s*(?:export\s+)?(?:default\s+)?(?:declare\s+)?(?:async\s+)?"
    r"(?:function\b|interface\b|type\s+[\w$]+\s*[=<]|enum\b|namespace\b|module\b|import\b|export\s*[{*]|@)")
_CLASS_HEAD_RE = re.compile(r"^\s*(?:export\s+)?(?:default\s+)?(?:abstract\s+)?(?:class|struct)\s+[\w$]+")

_FLOAT_REF_RE = re.compile(r"\$r\(\s*['\"]app\.float\.([A-Za-z0-9_]+)['\"]")
_DIM_VALUE_RE = re.compile(r"^\s*(\d+(?:\.\d+)?)\s*(dp|dip|sp|px|vp|fp)?\s*$")


# ══════════════════════════════════════════════════════════════════════════════
# 文本工具
# ══════════════════════════════════════════════════════════════════════════════

def strip_code(src: str) -> str:
    """去注释（//、/* */）与字符串字面量内容（'…'、"…"、`…`），以空格占位、保留换行与引号——行号不变。"""
    out = []
    i, n = 0, len(src)
    state = None  # None | "line" | "block" | "'" | '"' | "`"
    while i < n:
        c = src[i]
        if state is None:
            if c == "/" and i + 1 < n and src[i + 1] == "/":
                state = "line"; out.append("  "); i += 2; continue
            if c == "/" and i + 1 < n and src[i + 1] == "*":
                state = "block"; out.append("  "); i += 2; continue
            if c in ("'", '"', "`"):
                state = c; out.append(c); i += 1; continue
            out.append(c); i += 1; continue
        if state == "line":
            if c == "\n":
                state = None; out.append(c)
            else:
                out.append(" ")
            i += 1; continue
        if state == "block":
            if c == "*" and i + 1 < n and src[i + 1] == "/":
                state = None; out.append("  "); i += 2; continue
            out.append("\n" if c == "\n" else " "); i += 1; continue
        # 字符串态
        if c == "\\" and i + 1 < n:
            out.append("  "); i += 2; continue
        if c == state:
            state = None; out.append(c); i += 1; continue
        if c == "\n" and state != "`":
            state = None; out.append(c); i += 1; continue   # 未闭合单行字符串：行尾强制收口
        out.append("\n" if c == "\n" else " "); i += 1
    return "".join(out)


def _line_of(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


def _match_brace(code: str, open_pos: int) -> int:
    """code[open_pos] == '{'，返回配对 '}' 的下标；找不到返回 len(code)-1。"""
    depth = 0
    for j in range(open_pos, len(code)):
        ch = code[j]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return j
    return len(code) - 1


def _depth_at_line_starts(code: str) -> list:
    """每行起始处的花括号深度（下标 = 行号-1）。"""
    depths = [0]
    d = 0
    for ch in code:
        if ch == "{":
            d += 1
        elif ch == "}":
            d = max(0, d - 1)
        elif ch == "\n":
            depths.append(d)
    return depths


def split_members(body: str) -> list:
    """类体（不含外层花括号）切成成员文本 [(相对偏移, 文本)]：相对深度 0 处按 `;`/换行（括号平衡时）切分。"""
    members = []
    start = None
    dp = db = dc = 0
    i, n = 0, len(body)
    while i < n:
        ch = body[i]
        if start is None:
            if not ch.isspace() and ch != ";":
                start = i
            i += 1
            continue
        if ch == "(":
            dp += 1
        elif ch == ")":
            dp = max(0, dp - 1)
        elif ch == "[":
            db += 1
        elif ch == "]":
            db = max(0, db - 1)
        elif ch == "{":
            dc += 1
        elif ch == "}":
            dc = max(0, dc - 1)
            if dp == 0 and db == 0 and dc == 0:
                # 方法体/对象字面量收口即成员结束
                members.append((start, body[start:i + 1])); start = None; i += 1; continue
        elif ch in (";", "\n") and dp == 0 and db == 0 and dc == 0:
            seg = body[start:i]
            nxt = body[i + 1:i + 40].lstrip()
            if ch == "\n" and seg.rstrip().endswith((",", "=", "+", "-", "*", "/", "&&", "||", "?", ":", "(", "[", ".")) \
                    or (ch == "\n" and nxt.startswith((".", "?.", "&&", "||"))):
                i += 1; continue   # 续行
            members.append((start, seg)); start = None
        i += 1
    if start is not None:
        members.append((start, body[start:]))
    return members


def split_statements(code: str) -> list:
    """按行聚合成语句 [(起始行号, 文本)]：括号未平衡 / 行尾运算符 / 下一行以 . 开头 → 续行；行尾 `{`（块开始）处切断并清零。"""
    stmts = []
    lines = code.split("\n")
    buf: list = []
    start = 0
    dp = db = dc = 0
    for idx, raw in enumerate(lines):
        line = raw.rstrip()
        if not buf:
            start = idx + 1
        buf.append(raw)
        for ch in line:
            if ch == "(":
                dp += 1
            elif ch == ")":
                dp = max(0, dp - 1)
            elif ch == "[":
                db += 1
            elif ch == "]":
                db = max(0, db - 1)
            elif ch == "{":
                dc += 1
            elif ch == "}":
                dc = max(0, dc - 1)
        stripped = line.strip()
        if stripped.endswith("{") and dp == 0 and db == 0:
            stmts.append((start, "\n".join(buf))); buf = []; dp = db = dc = 0; continue
        nxt = lines[idx + 1].lstrip() if idx + 1 < len(lines) else ""
        cont = dp > 0 or db > 0 or dc > 0 or stripped.endswith((",", "=", "+", "*", "&&", "||", "?", ":", "(", "[", ".")) \
            or nxt.startswith((".", "?.", "&&", "||"))
        if cont and idx + 1 < len(lines):
            continue
        stmts.append((start, "\n".join(buf))); buf = []; dp = db = dc = 0
    if buf:
        stmts.append((start, "\n".join(buf)))
    return stmts


def _wrapped_in_px2vp(stmt: str, pos: int) -> bool:
    """stmt[pos] 处是否处于某个 px2vp( 的括号内。"""
    depth = 0
    j = pos - 1
    while j >= 0:
        ch = stmt[j]
        if ch == ")":
            depth += 1
        elif ch == "(":
            if depth == 0:
                if re.search(r"px2vp\s*$", stmt[max(0, j - 12):j]):
                    return True
            else:
                depth -= 1
        j -= 1
    return False


# ══════════════════════════════════════════════════════════════════════════════
# 模块上下文
# ══════════════════════════════════════════════════════════════════════════════

class ClassInfo:
    def __init__(self, name: str, file: Path, line: int, body: str):
        self.name, self.file, self.line = name, file, line
        self.ctor_body = ""
        self.instance_inits: list = []   # [(line, rhs)]
        self.static_inits: list = []     # [(line, rhs)]
        m = re.search(r"\bconstructor\s*\([^)]*\)\s*\{", body)
        if m:
            end = _match_brace(body, m.end() - 1)
            self.ctor_body = body[m.end():end]
        for off, text in split_members(body):
            head = text.lstrip()
            if head.startswith(("constructor", "get ", "set ", "static get", "static set")):
                continue
            if re.match(r"^(?:(?:public|private|protected|async|override)\s+)*[\w$]+\s*(?:<[^>]*>)?\s*\(", head):
                continue   # 方法
            ms = _STATIC_INIT_RE.match(text)
            if ms:
                self.static_inits.append((off, ms.group(2))); continue
            mi = _FIELD_INIT_RE.match(text)
            if mi:
                self.instance_inits.append((off, mi.group(2)))


class ModuleContext:
    """跨文件解析上下文：懒加载源码/去注释代码/class 表/import 表；entryability 初始化位点表。"""

    def __init__(self, project: Path, module_files: list):
        self.project = Path(project)
        self.files = [Path(f) for f in module_files]
        self._src: dict = {}
        self._code: dict = {}
        self._classes: dict = {}
        self._imports: dict = {}
        self._value_imports: dict = {}
        self._graph = None
        self._cycles = None
        self._entry_sites = None

    # ── 读取 ──
    def src(self, f: Path) -> str:
        f = Path(f)
        if f not in self._src:
            try:
                self._src[f] = f.read_text(encoding="utf-8", errors="replace")
            except OSError:
                self._src[f] = ""
        return self._src[f]

    def code(self, f: Path) -> str:
        f = Path(f)
        if f not in self._code:
            self._code[f] = strip_code(self.src(f))
        return self._code[f]

    def rel(self, f: Path) -> str:
        try:
            return Path(f).resolve().relative_to(self.project.resolve()).as_posix()
        except ValueError:
            return Path(f).as_posix()

    # ── class 表 ──
    def classes(self, f: Path) -> dict:
        f = Path(f)
        if f in self._classes:
            return self._classes[f]
        code = self.code(f)
        table: dict = {}
        for m in _CLASS_RE.finditer(code):
            open_pos = m.end() - 1
            end = _match_brace(code, open_pos)
            info = ClassInfo(m.group(1), f, _line_of(code, m.start()), code[open_pos + 1:end])
            table.setdefault(info.name, info)
        dm = _DEFAULT_CLASS_RE.search(code)
        if dm and dm.group(1) in table:
            table.setdefault("default", table[dm.group(1)])
        self._classes[f] = table
        return table

    # ── import 表 ──
    def imports(self, f: Path) -> dict:
        """{本地名: (目标文件 Path|None, 原名)}——只解析相对路径导入。"""
        f = Path(f)
        if f in self._imports:
            return self._imports[f]
        table: dict = {}
        code = self.code(f)
        src = self.src(f)
        for m in _IMPORT_RE.finditer(src):
            spec, target = m.group(1), m.group(3)
            if not target.startswith("."):
                continue
            resolved = self._resolve_import(f, target)
            spec = re.sub(r"\s+", " ", spec)
            # 形态：`X` / `X, { A, B as C }` / `{ A, B as C }` / `* as NS`
            default_name = None
            braces = re.search(r"\{([^}]*)\}", spec)
            head = spec[:braces.start()] if braces else spec
            head = head.strip().strip(",").strip()
            if head and not head.startswith("*"):
                default_name = head
            if default_name:
                table[default_name] = (resolved, "default")
            if braces:
                for item in braces.group(1).split(","):
                    item = item.strip()
                    if not item:
                        continue
                    item = re.sub(r"^type\s+", "", item)
                    parts = re.split(r"\s+as\s+", item)
                    orig = parts[0].strip()
                    local = parts[1].strip() if len(parts) > 1 else orig
                    table[local] = (resolved, orig)
        self._imports[f] = table
        return table

    def _resolve_import(self, f: Path, target: str):
        base = (Path(f).parent / target)
        cands = [base.with_suffix(base.suffix + ".ets") if base.suffix != ".ets" else base,
                 Path(str(base) + ".ets"), base / "index.ets", base / "Index.ets"]
        for c in cands:
            try:
                if c.is_file():
                    rc = c.resolve()
                    rc.relative_to(self.project.resolve())
                    return rc
            except (OSError, ValueError):
                continue
        return None

    # ── import 环（TDZ）──
    def value_imports(self, f: Path) -> dict:
        """{本地名: 目标文件} —— 只留「在本文件按值用到」的相对导入（纯类型导入编译期擦除，不是运行期依赖）。"""
        f = Path(f)
        if f in self._value_imports:
            return self._value_imports[f]
        body = _blank_generics(_AS_TYPE_RE.sub(_blank, _IMPORT_STMT_RE.sub(_blank, self.code(f))))
        typeless = _TYPE_ANNOT_RE.sub(_blank, _IMPLEMENTS_RE.sub(_blank, body))
        table = {}
        for local, (target, _orig) in self.imports(f).items():
            if target is None:
                continue
            # 两条口径取并（都只认「按值用到」，各自会漏一点）：典型值位模式；或抹掉类型位置后名字仍在
            if _value_used(body, local) or re.search(r"(?<![\w.$])%s\b" % re.escape(local), typeless):
                table[local] = target
        self._value_imports[f] = table
        return table

    def import_graph(self, seeds=None) -> dict:
        """{文件: {被它在运行期依赖的文件}}（值导入 + export…from 再导出）。

        seeds 给定时只从这些文件正向 BFS——含 seed 的强连通分量必定整个落在 seed 的正向可达集里，
        所以按任务白名单落账时不必给整模块去注释（ds 522 文件：全量 4.7s → 白名单 9 文件约 1s）。"""
        if seeds is None and self._graph is not None:
            return self._graph
        graph = {}
        # _resolve_import 回的是 resolve() 后的路径，self.files 可能没 resolve（临时目录符号链接）——按 resolve 后对齐
        canon = {}
        for x in self.files:
            try:
                canon[Path(x).resolve()] = Path(x)
            except OSError:
                canon[Path(x)] = Path(x)
        if seeds is None:
            queue = list(canon.values())
        else:
            queue = []
            for x in seeds:
                try:
                    c = canon.get(Path(x).resolve())
                except OSError:
                    c = None
                if c is not None and c not in queue:
                    queue.append(c)
        while queue:
            f = queue.pop()
            if f in graph:
                continue
            deps = set(self.value_imports(f).values())
            for m in _EXPORT_FROM_RE.finditer(self.src(f)):
                t = self._resolve_import(f, m.group(2))
                if t is not None:
                    deps.add(t)
            graph[f] = {canon[d] for d in deps if d in canon and canon[d] != f}
            queue.extend(d for d in graph[f] if d not in graph)
        if seeds is None:
            self._graph = graph
        return graph

    def cycles(self, seeds=None) -> list:
        """import 环列表（每个是文件集合，size>1）；seeds 给定时只覆盖 seeds 的正向可达子图。"""
        if seeds is not None:
            return _tarjan_scc(self.import_graph(seeds))
        if self._cycles is None:
            self._cycles = _tarjan_scc(self.import_graph())
        return self._cycles

    def resolve_class(self, name: str, f: Path):
        """在文件 f 的视角解析类名 → ClassInfo|None（同文件优先，否则沿相对 import）。"""
        f = Path(f)
        info = self.classes(f).get(name)
        if info:
            return info
        imp = self.imports(f).get(name)
        if not imp or imp[0] is None:
            return None
        target, orig = imp
        return self.classes(target).get(orig)

    # ── entryability 初始化位点 ──
    def entry_sites(self) -> dict:
        """{"assign": {"Foo.bar", "globalThis.x"}, "init": {"Foo"}}"""
        if self._entry_sites is not None:
            return self._entry_sites
        assign: set = set()
        init: set = set()
        for f in self.files:
            if "entryability" not in Path(f).parts:
                continue
            code = self.code(f)
            for m in _ENTRY_ASSIGN_RE.finditer(code):
                assign.add("%s.%s" % (m.group(1), m.group(2)))
            for m in _ENTRY_GLOBAL_RE.finditer(code):
                assign.add("globalThis.%s" % m.group(1))
            for m in _ENTRY_INIT_CALL_RE.finditer(code):
                if m.group(1) not in _ENTRY_INIT_SKIP:
                    init.add(m.group(1))
        self._entry_sites = {"assign": assign, "init": init}
        return self._entry_sites


# ══════════════════════════════════════════════════════════════════════════════
# 规则 1：module-init-runtime-dependency
# ══════════════════════════════════════════════════════════════════════════════

def _direct_marker(text: str, ctx: ModuleContext):
    for rx, label in _MARKERS:
        if rx.search(text):
            return label
    sites = ctx.entry_sites()
    for sym in sorted(sites["assign"]):
        if re.search(r"(?<![\w$.])" + re.escape(sym) + r"\b", text):
            return "%s（仅在 entryability 里初始化）" % sym
    for cls in sorted(sites["init"]):
        if re.search(r"(?<![\w$.])" + re.escape(cls) + r"\.(?:instance\b|getInstance\s*\(|shared\b|current\b)", text):
            return "%s.instance（%s 仅在 entryability 里 init）" % (cls, cls)
    return None


def _class_touches(info: ClassInfo, ctx: ModuleContext, hop: int, seen: set):
    """返回 (标记描述, 位置串) 或 None。检查 constructor 体 + 实例/静态字段初始化式；一跳内递归。"""
    key = (str(info.file), info.name)
    if key in seen:
        return None
    seen.add(key)
    bodies = [("constructor", info.ctor_body)] + [("字段初始化", rhs) for _, rhs in info.instance_inits] \
        + [("静态初始化", rhs) for _, rhs in info.static_inits]
    for kind, text in bodies:
        if not text:
            continue
        mk = _direct_marker(text, ctx)
        if mk:
            return ("%s 的%s触碰 %s" % (info.name, kind, mk), "%s:%d" % (ctx.rel(info.file), info.line))
    if hop >= 1:
        return None
    for kind, text in bodies:
        if not text:
            continue
        names = []
        for rx in (_BODY_NEW_RE, _BODY_GETINST_RE, _BODY_INSTANCE_RE):
            names += [m.group(1) for m in rx.finditer(text)]
        for nm in dict.fromkeys(names):
            if nm == info.name:
                continue
            sub = ctx.resolve_class(nm, info.file)
            if not sub:
                continue
            r = _class_touches(sub, ctx, hop + 1, seen)
            if r:
                return ("%s 的%s构造 %s → %s" % (info.name, kind, nm, r[0]), r[1])
    return None


def _construction_target(rhs: str):
    rhs = rhs.strip()
    for rx in (_CTOR_NEW_RE, _CTOR_GETINST_RE, _CTOR_INSTANCE_RE):
        m = rx.match(rhs)
        if m:
            return m.group(1)
    return None


def check_module_init(ctx: ModuleContext, f: Path) -> list:
    f = Path(f)
    code = ctx.code(f)
    lines = code.split("\n")
    depths = _depth_at_line_starts(code)
    out = []
    seen_lines: set = set()

    def emit(lineno: int, lhs: str, rhs_head: str, why: str, where: str):
        if lineno in seen_lines:
            return
        seen_lines.add(lineno)
        out.append({"code": "module-init-runtime-dependency", "file": ctx.rel(f), "line": lineno,
                    "severity": "P0", "kind": "runtime",
                    "message": "模块加载期求值 `%s = %s`：%s（%s）——冷启即 ReferenceError/未初始化崩溃"
                               % (lhs, rhs_head[:60], why, where),
                    "fix": FIX_MODULE_INIT})

    for idx, line in enumerate(lines):
        lineno = idx + 1
        depth = depths[idx] if idx < len(depths) else 0
        lhs = rhs = None
        if depth == 0:
            m = _TOP_DECL_RE.match(line)
            if m:
                lhs, rhs = m.group(1), m.group(2)
            else:
                m = _TOP_DEFAULT_RE.match(line)
                if m:
                    lhs, rhs = "export default", m.group(1)
                else:
                    m = _TOP_BARE_RE.match(line)
                    if m:
                        lhs, rhs = "<顶层语句>", m.group(1)
        else:
            m = _STATIC_FIELD_RE.match(line)
            if m:
                lhs, rhs = "static " + m.group(1), m.group(2)
        if rhs is None:
            continue
        rhs_s = rhs.strip()
        if rhs_s.startswith(("(", "async", "function")) or "=>" in rhs_s.split("(")[0]:
            continue   # 延迟表达式
        mk = _direct_marker(rhs_s, ctx)
        if mk:
            emit(lineno, lhs, rhs_s, "右值直接触碰 %s" % mk, ctx.rel(f) + ":%d" % lineno)
            continue
        target = _construction_target(rhs_s)
        if not target:
            continue
        info = ctx.resolve_class(target, f)
        if not info:
            continue
        r = _class_touches(info, ctx, 0, set())
        if r:
            emit(lineno, lhs, rhs_s, r[0], r[1])
    return out


# ══════════════════════════════════════════════════════════════════════════════
# 规则 4：module-init-cycle-tdz（import 环 + 加载期求值）
# ══════════════════════════════════════════════════════════════════════════════

def _value_used(code: str, name: str) -> bool:
    """name 在 code 里是否落在典型**值位**（`new X` / `X.y` / `X(` / instanceof / extends / 实参·右值）。"""
    n = re.escape(name)
    return bool(re.search(r"\bnew\s+%s\b|(?<![\w.])%s\s*\.\s*\w|(?<![\w.])%s\s*\(|\binstanceof\s+%s\b"
                          r"|\bextends\s+%s\b|[=,(\[]\s*%s\s*[,);\]]" % (n, n, n, n, n, n), code))


def _blank(m) -> str:
    """按位抹平匹配段（保留换行，行号不变）。"""
    return re.sub(r"[^\n]", " ", m.group(0))


def _blank_generics(text: str) -> str:
    """抹平紧跟标识符的 `<…>` 泛型实参段（`new Map<A, B>()` 里的 A/B 是类型不是值）；`=>` 的 `>` 不当收口。"""
    out = list(text)
    i, n = 0, len(text)
    while i < n:
        if text[i] == "<" and i > 0 and (text[i - 1].isalnum() or text[i - 1] in "_$)]"):
            depth, j, closed = 0, i, False
            while j < n:
                if text[j] == "=" and j + 1 < n and text[j + 1] == ">":
                    j += 2; continue
                if text[j] == "<":
                    depth += 1
                elif text[j] == ">":
                    depth -= 1
                    if depth == 0:
                        closed = True; break
                elif text[j] in ";{}":
                    break
                j += 1
            if closed:
                for k in range(i, j + 1):
                    if out[k] != "\n":
                        out[k] = " "
                i = j + 1
                continue
        i += 1
    return "".join(out)


def _member_init_split(text: str):
    """成员/声明文本 → (声明头, 右值)，按第一个顶层 `=` 切（跳过 `=>` `==` `!=` `<=` `>=`，括号与泛型内不算）；切不动 → None。"""
    dp = db = dc = da = 0
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c == "=" and i + 1 < n and text[i + 1] == ">":
            i += 2; continue
        if c in "=!<>" and i + 1 < n and text[i + 1] == "=":
            i += 2; continue
        if c == "(":
            dp += 1
        elif c == ")":
            dp = max(0, dp - 1)
        elif c == "[":
            db += 1
        elif c == "]":
            db = max(0, db - 1)
        elif c == "{":
            dc += 1
        elif c == "}":
            dc = max(0, dc - 1)
        elif c == "<" and i > 0 and (text[i - 1].isalnum() or text[i - 1] in "_$)]"):
            da += 1
        elif c == ">" and da > 0:
            da -= 1
        elif c == "=" and dp == db == dc == da == 0:
            return text[:i], text[i + 1:]
        i += 1
    return None


_LAZY_BODY_RE = re.compile(r"=>|(?<![\w$.])function\s*[\w$]*\s*\(")


def _blank_lazy_bodies(text: str) -> str:
    """箭头/函数表达式的体不在加载期执行——从第一个 `=>` / `function(` 起整段抹平（宁可少报不可假报）。"""
    m = _LAZY_BODY_RE.search(text)
    if not m:
        return text
    return text[:m.start()] + re.sub(r"[^\n]", " ", text[m.start():])


def _value_probe(text: str, is_class_head: bool) -> str:
    """把文本里只作类型的位置抹平，剩下的即「加载期按值读」的面（行号不变）。"""
    t = _IMPLEMENTS_RE.sub(_blank, text)
    if is_class_head:
        t = t.split("{")[0]
        if "extends" not in t:
            return ""
        t = " " * t.index("extends") + t[t.index("extends"):]
    else:
        t = _TYPE_ANNOT_RE.sub(_blank, t)
    return _blank_lazy_bodies(_blank_generics(_AS_TYPE_RE.sub(_blank, t)))


def _tarjan_scc(graph: dict) -> list:
    """强连通分量（迭代版，size>1 才返回）。"""
    index: dict = {}
    low: dict = {}
    onstack: set = set()
    stack: list = []
    out: list = []
    counter = [0]
    for root in list(graph):
        if root in index:
            continue
        work = [(root, iter(sorted(graph.get(root, ()), key=str)))]
        index[root] = low[root] = counter[0]; counter[0] += 1
        stack.append(root); onstack.add(root)
        while work:
            v, it = work[-1]
            advanced = False
            for w in it:
                if w not in index:
                    index[w] = low[w] = counter[0]; counter[0] += 1
                    stack.append(w); onstack.add(w)
                    work.append((w, iter(sorted(graph.get(w, ()), key=str))))
                    advanced = True
                    break
                if w in onstack:
                    low[v] = min(low[v], index[w])
            if advanced:
                continue
            work.pop()
            if work:
                low[work[-1][0]] = min(low[work[-1][0]], low[v])
            if low[v] == index[v]:
                comp = []
                while True:
                    w = stack.pop(); onstack.discard(w); comp.append(w)
                    if w == v:
                        break
                if len(comp) > 1:
                    out.append(set(comp))
    return out


def _static_init_sites(code: str) -> list:
    """类体第一层 static 字段初始化式 → [(行号, 右值文本)]（模块加载期求值）。"""
    sites = []
    for m in _CLASS_RE.finditer(code):
        open_pos = m.end() - 1
        end = _match_brace(code, open_pos)
        body = code[open_pos + 1:end]
        for off, text in split_members(body):
            head = text.lstrip()
            if head.startswith(("constructor", "get ", "set ", "static get", "static set")):
                continue
            if re.match(r"^(?:(?:public|private|protected|async|override)\s+)*static\s+[\w$]+\s*(?:<[^>]*>)?\s*\(", head):
                continue   # 静态方法
            sp = _member_init_split(text)
            if not sp:
                continue
            if not re.match(r"^\s*(?:(?:public|private|protected|readonly|override|declare)\s+)*static\s+"
                            r"(?:readonly\s+)?[\w$]+\s*[?!]?\s*(?::|$)", sp[0]):
                continue
            sites.append((_line_of(code, open_pos + 1 + off), sp[1]))
    return sites


def _load_time_reads(code: str, names) -> list:
    """加载期读取 names 里的绑定 → [(行号, 绑定名, 语句摘要)]。"""
    if not names:
        return []
    name_re = re.compile(r"(?<![\w.$])(%s)\b" % "|".join(sorted((re.escape(x) for x in names), key=len, reverse=True)))
    blanked = _IMPORT_STMT_RE.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), code)
    blanked = _EXPORT_FROM_RE.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), blanked)
    depths = _depth_at_line_starts(blanked)
    hits = []
    seen = set()

    def note(lineno, nm, text):
        if (lineno, nm) in seen:
            return
        seen.add((lineno, nm))
        hits.append((lineno, nm, " ".join(text.split())[:110]))

    for start, stmt in split_statements(blanked):
        if depths[start - 1] if start - 1 < len(depths) else 0:
            continue                                   # 非顶层
        head = stmt.lstrip()
        if _NOT_LOAD_TIME_HEAD_RE.match(head):
            continue
        probe = _value_probe(stmt, bool(_CLASS_HEAD_RE.match(head)))
        for m in name_re.finditer(probe):
            note(start + probe.count("\n", 0, m.start()), m.group(1), stmt)
    for lineno, rhs in _static_init_sites(blanked):
        for m in name_re.finditer(_blank_lazy_bodies(_blank_generics(_AS_TYPE_RE.sub(_blank, rhs)))):
            note(lineno, m.group(1), "static … = " + rhs)
    return hits


def check_cycle_tdz(ctx: ModuleContext, targets: list) -> list:
    """import 环内、加载期读同环模块绑定 → P0。findings 只出在 targets 里的文件（环仍按整模块算）。"""
    tset = set(Path(t) for t in targets)
    cycles = ctx.cycles(seeds=tset if len(tset) < len(ctx.files) else None)
    if not cycles:
        return []
    out = []
    for comp in cycles:
        for f in sorted(comp & tset, key=str):
            names = {nm: t for nm, t in ctx.value_imports(f).items() if t in comp}
            for lineno, nm, text in _load_time_reads(ctx.code(f), set(names)):
                out.append({"code": "module-init-cycle-tdz", "file": ctx.rel(f), "line": lineno,
                            "severity": "P0", "kind": "runtime",
                            "message": "模块加载期读取同 import 环模块的绑定 `%s`（← %s，环含 %d 个模块）：`%s`"
                                       "——环内另一侧可能尚未求值，冷启 ReferenceError: %s is not initialized"
                                       % (nm, ctx.rel(names[nm]), len(comp), text, nm),
                            "fix": FIX_CYCLE_TDZ})
    return out


# ══════════════════════════════════════════════════════════════════════════════
# 规则 2：avoid-area-px-as-vp
# ══════════════════════════════════════════════════════════════════════════════

def _is_dim_context(stmt: str, name_pat: str) -> bool:
    if _DIM_CALL_RE.search(stmt) and re.search(name_pat, stmt):
        return True
    return re.search(_DIM_KEY_RE + name_pat, stmt) is not None


def _dim_usage(ctx: ModuleContext, files: list, name_pat: str):
    """在 files 里找 name_pat 在尺寸上下文且未被 px2vp 包裹的使用 → (file, line) | None。"""
    rx = re.compile(name_pat)
    for f in files:
        for start, stmt in split_statements(ctx.code(f)):
            if not _is_dim_context(stmt, name_pat):
                continue
            if re.match(r"^\s*(?:this\.)?[\w$.]+\s*=(?!=)", stmt.strip()) and not _DIM_CALL_RE.search(stmt) \
                    and not re.search(_DIM_KEY_RE + name_pat, stmt):
                continue
            for m in rx.finditer(stmt):
                if not _wrapped_in_px2vp(stmt, m.start()):
                    return (f, start)
    return None


def _storage_bound_names(ctx: ModuleContext, files: list, key: str) -> list:
    """AppStorage 键 → 各文件里 @StorageProp/@StorageLink('key') 声明的变量名 [(file, name)]。"""
    out = []
    rx = re.compile(r"@(?:StorageProp|StorageLink|LocalStorageProp|LocalStorageLink)\s*\(\s*['\"]%s['\"]\s*\)\s*"
                    r"(?:(?:public|private|protected|readonly)\s+)*([\w$]+)" % re.escape(key))
    for f in files:
        for m in rx.finditer(ctx.src(f)):
            out.append((f, m.group(1)))
    return out


def check_avoid_area(ctx: ModuleContext, f: Path) -> list:
    f = Path(f)
    code = ctx.code(f)
    out = []
    seen: set = set()

    def emit(lineno: int, snippet: str, usage):
        if lineno in seen:
            return
        seen.add(lineno)
        where = "" if usage is None else "；使用处 %s:%d" % (ctx.rel(usage[0]), usage[1])
        out.append({"code": "avoid-area-px-as-vp", "file": ctx.rel(f), "line": lineno,
                    "severity": "P1", "kind": "visual",
                    "message": "安全区/窗口 px 值 `%s` 未经 px2vp() 直接用作 vp 尺寸%s——3x 屏顶出三倍空白带"
                               % (snippet.strip()[:70], where),
                    "fix": FIX_AVOID_AREA})

    src = ctx.src(f)
    for start, s0, s1 in _statement_offsets(code):
        stmt = code[s0:s1]
        hits = [m for m in _AREA_RE.finditer(stmt) if not _wrapped_in_px2vp(stmt, m.start())]
        if not hits:
            continue
        one_line = " ".join(src[s0:s1].split())
        # 语句本身就是尺寸上下文
        if _DIM_CALL_RE.search(stmt) or re.search(_DIM_KEY_RE + r"[^,}\n]*?(?:topRect|bottomRect|leftRect|rightRect|windowRect|drawableRect)", stmt):
            emit(start, one_line, None)
            continue
        # 赋值：追字段/键的后续使用（只追数值读取的赋值；取 avoid-area 对象本身不判）
        if not _AREA_NUMERIC_RE.search(stmt):
            continue
        ms = _ASSIGN_STORAGE_RE.search(src[s0:s1])   # 键名在字符串里——用原文
        if ms:
            for uf, var in _storage_bound_names(ctx, ctx.files, ms.group(1)):
                u = _dim_usage(ctx, [uf], r"\bthis\.%s\b" % re.escape(var))
                if u:
                    emit(start, one_line, u); break
            else:
                u = _dim_usage(ctx, ctx.files, r"AppStorage\s*\.\s*get\s*(?:<[^>]*>)?\s*\(\s*['\"]%s['\"]\s*\)" % re.escape(ms.group(1)))
                if u:
                    emit(start, one_line, u)
            continue
        m = _ASSIGN_LOCAL_RE.match(stmt)
        if m:
            u = _dim_usage(ctx, [f], r"(?<![\w$.])%s\b" % re.escape(m.group(1)))
            if u:
                emit(start, one_line, u)
            continue
        m = _ASSIGN_THIS_RE.match(stmt)
        if m:
            u = _dim_usage(ctx, [f], r"\bthis\.%s\b" % re.escape(m.group(1)))
            if u:
                emit(start, one_line, u)
            continue
        m = _ASSIGN_OBJ_RE.match(stmt)
        if m:
            u = _dim_usage(ctx, ctx.files, r"\.%s\b" % re.escape(m.group(2)))
            if u:
                emit(start, one_line, u)
    return out


# ══════════════════════════════════════════════════════════════════════════════
# 规则 3：dimen-binding-literal-drift
# ══════════════════════════════════════════════════════════════════════════════

def _sanitize_name(name: str) -> str:
    n = re.sub(r"[^A-Za-z0-9_]", "_", str(name or "")).strip("_") or "r"
    if not re.match(r"^[A-Za-z_]", n):
        n = "r_" + n
    return n


def dim_number(v) -> float:
    m = _DIM_VALUE_RE.match(str(v if v is not None else ""))
    return float(m.group(1)) if m else None


def _float_tables(project: Path, modules: list) -> list:
    """[(float.json Path, {name: value}, {name: line})]"""
    out = []
    for mod in modules:
        fj = Path(project) / mod / "src" / "main" / "resources" / "base" / "element" / "float.json"
        if not fj.is_file():
            continue
        try:
            text = fj.read_text(encoding="utf-8")
            rows = json.loads(text).get("float") or []
        except (OSError, ValueError, AttributeError):
            continue
        table, lines = {}, {}
        for r in rows:
            if isinstance(r, dict) and r.get("name"):
                table[r["name"]] = r.get("value")
        for i, ln in enumerate(text.split("\n")):
            m = re.search(r'"name"\s*:\s*"([^"]+)"', ln)
            if m:
                lines.setdefault(m.group(1), i + 1)
        out.append((fj, table, lines))
    return out


def check_dimen_drift(ctx: ModuleContext, targets: list, modules: list) -> list:
    lit = Path(ctx.project) / "spec" / "baseline" / "android-literals.json"
    if not lit.is_file():
        return []
    try:
        dimens = (json.loads(lit.read_text(encoding="utf-8")).get("values_map") or {}).get("dimens") or {}
    except (OSError, ValueError, AttributeError):
        return []
    android = {}
    for an, raw in dimens.items():
        num = dim_number(raw)
        if num is not None:
            android.setdefault(_sanitize_name(an), (num, str(raw)))
    if not android:
        return []
    refs: dict = {}
    for f in targets:
        for m in _FLOAT_REF_RE.finditer(ctx.src(f)):
            refs[m.group(1)] = refs.get(m.group(1), 0) + 1
    out = []
    for fj, table, lines in _float_tables(ctx.project, modules):
        for name in sorted(refs):
            if name not in android or name not in table:
                continue
            pv = dim_number(table[name])
            av, araw = android[name]
            if pv is None or abs(pv - av) < 1e-6:
                continue
            out.append({"code": "dimen-binding-literal-drift", "file": ctx.rel(fj), "line": lines.get(name, 0),
                        "severity": "P2", "kind": "visual",
                        "message": "float.json %s=%s 与安卓 dimens %s=%s 数值漂移（被 %d 处 $r('app.float.%s') 引用）"
                                   % (name, table[name], name, araw, refs[name], name),
                        "fix": FIX_DIMEN_DRIFT})
    return out


# ══════════════════════════════════════════════════════════════════════════════
# 入口
# ══════════════════════════════════════════════════════════════════════════════

def _module_dirs(project: Path, module) -> list:
    project = Path(project)
    if module:
        return [module]
    mods = []
    try:
        for d in sorted(project.iterdir()):
            if d.is_dir() and d.name not in SKIP_PARTS and (d / "src" / "main" / "ets").is_dir():
                mods.append(d.name)
    except OSError:
        pass
    return mods


def collect_module_files(project: Path, module=None) -> list:
    """<module>/src/main/ets/**/*.ets（module=None → 所有含 src/main/ets 的顶层模块），跳过 build/oh_modules/__probe。"""
    project = Path(project)
    files = []
    for mod in _module_dirs(project, module):
        base = project / mod / "src" / "main" / "ets"
        if not base.is_dir():
            continue
        for p in sorted(base.rglob("*.ets")):
            if any(part in SKIP_PARTS for part in p.relative_to(project).parts):
                continue
            files.append(p)
    return files


def _lint_once(ctx: ModuleContext, targets: list, modules: list) -> list:
    findings: list = []
    for f in targets:
        findings += check_module_init(ctx, f)
        findings += check_avoid_area(ctx, f)
    findings += check_cycle_tdz(ctx, targets)
    findings += check_dimen_drift(ctx, targets, modules)
    findings.sort(key=lambda x: (x["severity"], x["file"], x["line"], x["code"]))
    return findings


# ══════════════════════════════════════════════════════════════════════════════
# --fix：安全机械变换
# ══════════════════════════════════════════════════════════════════════════════

_CHAIN_RE = re.compile(
    r"(?:this\.)?[\w$]+(?:\.[\w$]+)*"
    r"(?:\.getWindowAvoidArea\(\s*[\w$.]*\s*\)|\.getWindowProperties\(\s*\))?"
    r"\.(?:topRect\.height|bottomRect\.height|leftRect\.width|rightRect\.width|(?:windowRect|drawableRect)\.[\w$]+)")
_STATIC_NEW_LINE_RE = re.compile(
    r"^(\s*)((?:(?:public|private|protected)\s+)?)static\s+(?:readonly\s+)?([\w$]+)\s*(?::\s*([^=]+?))?\s*=\s*"
    r"(new\s+([\w$]+)\s*\(.*\))\s*;?\s*$")
_STATIC_ANY_LINE_RE = re.compile(
    r"^(\s*)((?:(?:public|private|protected)\s+)?)static\s+(?:readonly\s+)?([\w$]+)\s*(?::\s*([^=]+?))?\s*=\s*"
    r"(\S.*?)\s*;?\s*$")


def _statement_offsets(code: str) -> list:
    """split_statements 的偏移版：[(起始行号, 起始偏移, 结束偏移)]。"""
    out = []
    pos = 0
    for start, text in split_statements(code):
        out.append((start, pos, pos + len(text)))
        pos += len(text) + 1
    return out


def _fix_avoid_area(ctx: ModuleContext, f: Path, lineno: int) -> list:
    """返回 [(start, end, replacement, detail)]（原文偏移）。"""
    code = ctx.code(f)
    src = ctx.src(f)
    edits = []
    for start, s0, s1 in _statement_offsets(code):
        if start != lineno:
            continue
        stmt = code[s0:s1]
        for m in _CHAIN_RE.finditer(stmt):
            a, b = m.start(), m.end()
            if _wrapped_in_px2vp(stmt, a):
                continue
            before = stmt[a - 1] if a > 0 else ""
            after = stmt[b] if b < len(stmt) else ""
            if before in (")", "]", "?", "."):
                continue   # 链前还有别的调用/下标/可选链 → 非简单链
            if after in ("(", "[", ".", "?"):
                continue
            edits.append((s0 + a, s0 + b, "px2vp(%s)" % src[s0 + a:s0 + b], src[s0 + a:s0 + b]))
        break
    return edits


def _enclosing_class(ctx: ModuleContext, f: Path, offset: int):
    """包含 offset 的最内层 class → 名字 | None。"""
    code = ctx.code(f)
    best = None
    for m in _CLASS_RE.finditer(code):
        open_pos = m.end() - 1
        end = _match_brace(code, open_pos)
        if open_pos < offset < end and (best is None or open_pos > best[1]):
            best = (m.group(1), open_pos, end)
    return best


def _fix_static_new(ctx: ModuleContext, f: Path, lineno: int, require_new: bool = True) -> list:
    """单行 static 字段初始化 → 私有后备字段 + 惰性 getter。require_new=False（TDZ）时右值放宽到任意单行表达式，
    但类型必须能确定（显式 `: T` 标注，或右值是 `new Y(...)` 取 Y）。"""
    src = ctx.src(f)
    code = ctx.code(f)
    lines = src.split("\n")
    if lineno < 1 or lineno > len(lines):
        return []
    line = lines[lineno - 1]
    m = _STATIC_NEW_LINE_RE.match(line)
    if not m and not require_new:
        m = _STATIC_ANY_LINE_RE.match(line)
        if m:
            mn = _CTOR_NEW_RE.match(m.group(5).strip())
            m = (m.group(1), m.group(2), m.group(3), m.group(4), m.group(5), mn.group(1) if mn else None)
            if not (m[3] or m[5]):
                return []       # 类型定不了 → 不改
    if not m:
        return []
    if not isinstance(m, tuple):
        m = (m.group(1), m.group(2), m.group(3), m.group(4), m.group(5), m.group(6))
    indent, vis, name, typ, ctor, ycls = m
    if ctor.count("(") != ctor.count(")") or ctor.count("[") != ctor.count("]"):
        return []
    if ctor.startswith(("(", "async", "function")) or "=>" in ctor.split("(")[0]:
        return []
    off = sum(len(x) + 1 for x in lines[:lineno - 1])
    enc = _enclosing_class(ctx, f, off)
    if not enc:
        return []
    cls, open_pos, end = enc
    body = code[open_pos + 1:end]
    backing = "_" + name
    if re.search(r"(?<![\w$])%s\b" % re.escape(backing), body):
        return []
    if re.search(r"\bthis\.%s\s*=(?!=)" % re.escape(name), body):
        return []
    assign_rx = re.compile(r"\b%s\.%s\s*=(?!=)" % (re.escape(cls), re.escape(name)))
    for g in ctx.files:
        gcode = ctx.code(g)
        for am in assign_rx.finditer(gcode):
            if g == f and _line_of(gcode, am.start()) == lineno:
                continue
            return []
    typ = (typ or ycls).strip()
    vis = vis.strip()
    getter_mod = (vis + " ") if vis else ""
    i2 = indent + "  "
    i3 = indent + "    "
    new = ("%sprivate static %s: %s | undefined = undefined;\n" % (indent, backing, typ)
           + "%s%sstatic get %s(): %s {\n" % (indent, getter_mod, name, typ)
           + "%sif (!%s.%s) {\n" % (i2, cls, backing)
           + "%s%s.%s = %s;\n" % (i3, cls, backing, ctor)
           + "%s}\n" % i2
           + "%sreturn %s.%s;\n" % (i2, cls, backing)
           + "%s}" % indent)
    return [(off, off + len(line), new, "%s.%s → 惰性 getter" % (cls, name))]


def apply_fixes(ctx: ModuleContext, findings: list) -> list:
    """按 findings 做安全变换并写盘；返回 fixed [{code, file, line, detail}]。"""
    per_file: dict = {}
    fixed = []
    for x in findings:
        f = ctx.project / x["file"]
        if not f.is_file():
            continue
        if x["code"] == "avoid-area-px-as-vp":
            edits = _fix_avoid_area(ctx, f, x["line"])
        elif x["code"] == "module-init-runtime-dependency":
            edits = _fix_static_new(ctx, f, x["line"])
        elif x["code"] == "module-init-cycle-tdz":
            edits = _fix_static_new(ctx, f, x["line"], require_new=False)
        else:
            edits = []
        for a, b, rep, detail in edits:
            per_file.setdefault(f, []).append((a, b, rep))
            fixed.append({"code": x["code"], "file": x["file"], "line": x["line"], "detail": detail})
    for f, edits in per_file.items():
        src = ctx.src(f)
        edits.sort(key=lambda e: e[0], reverse=True)
        last = None
        for a, b, rep in edits:
            if last is not None and b > last:
                continue   # 重叠编辑：只应用一处
            src = src[:a] + rep + src[b:]
            last = a
        try:
            with open(str(f), "w", encoding="utf-8", newline="") as fh:
                fh.write(src)
        except OSError:
            continue
    return fixed


def run_lint(project, module="entry", files=None, fix=False) -> dict:
    """返回 {ok, findings, counts, scanned[, fixed]}。files=None → 扫描整个模块；否则只对这些工程相对路径出 findings
    （模块其余文件仍加载作解析上下文）。fix=True → 先做安全机械修复再重新 lint，findings 为剩余。"""
    project = Path(project).resolve()
    modules = _module_dirs(project, module)
    context_files = collect_module_files(project, module)
    if files is None:
        targets = list(context_files)
    else:
        targets = []
        for rel in files:
            rel = str(rel).strip()
            if not rel or not rel.endswith(".ets"):
                continue
            p = Path(rel)
            p = p if p.is_absolute() else project / p
            try:
                p = p.resolve()
                p.relative_to(project)
            except (OSError, ValueError):
                continue
            if p.is_file() and p not in targets:
                targets.append(p)
        ctx_set = set(context_files)
        for t in targets:
            if t not in ctx_set:
                context_files.append(t)
    ctx = ModuleContext(project, context_files)
    findings = _lint_once(ctx, targets, modules)
    fixed: list = []
    if fix and findings:
        fixed = apply_fixes(ctx, findings)
        if fixed:
            ctx = ModuleContext(project, context_files)   # 缓存作废，重新读盘
            findings = _lint_once(ctx, targets, modules)
    counts: dict = {}
    for x in findings:
        counts[x["code"]] = counts.get(x["code"], 0) + 1
    out = {"ok": not findings, "findings": findings, "counts": counts, "scanned": len(targets)}
    if fix:
        out["fixed"] = fixed
    return out
