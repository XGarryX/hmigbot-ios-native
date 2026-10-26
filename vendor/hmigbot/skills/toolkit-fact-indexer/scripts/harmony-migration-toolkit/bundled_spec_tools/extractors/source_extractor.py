"""
source_extractor.py

通用语义模式提取器 —— 不依赖特定框架或方法名。

5 个核心模式（语义，非名称）：
  A. R.id 分发块   — 任何将 R.id.xxx 映射到 handler 的 when/switch 块
  B. 事件注册      — 任何 setOn*/addXxx*/doOn* 调用（监听器/回调注册）
  C. 可见性控制    — 任何对 visibility / isVisible / isGone / beXxx 的赋值或调用
  D. 布局膨胀      — 任何 inflate(R.layout.xxx) 或 XxxBinding.inflate()
  E. 数据驱动 UI   — 构建选项列表后传入弹窗/列表组件；提取静态选项文本

误报抑制：
  - view_ref 为 PascalCase（类型名而非实例变量）的事件注册被过滤
  - 已知非 View 系统对象（decorView、contentResolver、window 等）被过滤
  - 第三方库目录（rtl-viewpager 等）不扫描事件注册
"""

import json
import re
from pathlib import Path

try:
    from extractors import ast_index
except Exception:  # pragma: no cover - fallback for standalone execution
    ast_index = None  # type: ignore[assignment]

from extractors import android_project


# ══════════════════════════════════════════════════════
# 辅助函数
# ══════════════════════════════════════════════════════

def _camel_to_snake(name: str) -> str:
    s = re.sub(r"(?<=[a-z])(?=[A-Z])", "_", name)
    s = re.sub(r"(?<=[a-zA-Z])(?=[0-9])", "_", s)
    return s.lower()


def _binding_class_to_layout(cls: str) -> str:
    """ActivityMainBinding → activity_main"""
    name = cls.replace("Binding", "")
    return _camel_to_snake(name)


def _line_of(source: str, pos: int) -> int:
    return source[:pos].count("\n") + 1


def _enclosing_fn(lines: list[str], line_idx: int, search_range: int = 60) -> str:
    """向上找最近的函数/方法定义行"""
    fn_re = re.compile(
        r'(?:override\s+)?(?:public|private|protected|internal)?\s*'
        r'(?:fun |void |def |func |\w+\s+\w+\s*\()'
    )
    for i in range(line_idx - 1, max(0, line_idx - search_range), -1):
        if fn_re.search(lines[i]):
            return lines[i].strip()[:100]
    return ""


def _balanced_block(source: str, open_pos: int,
                    open_ch: str = "{", close_ch: str = "}",
                    max_len: int = 3000) -> str:
    """从 open_pos（'{' 处）提取平衡括号内的内容"""
    depth = 0
    for i, ch in enumerate(source[open_pos: open_pos + max_len]):
        if ch == open_ch:   depth += 1
        elif ch == close_ch: depth -= 1
        if depth == 0:
            return source[open_pos + 1: open_pos + i]
    return source[open_pos + 1: open_pos + max_len]


def _extract_r_id_handlers(block: str) -> list[tuple[str, str]]:
    """
    从 when/switch 块中提取 (item_id, handler_snippet) 对。
    支持 Kotlin `R.id.xxx ->` 和 Java `case R.id.xxx:`
    """
    kt_re   = re.compile(r'R\.id\.(\w+)\s*->\s*([^\n\r]{0,120})')
    java_re = re.compile(r'case\s+R\.id\.(\w+)\s*:([\s\S]{0,200}?)(?=case\s+R\.id\.|default\s*:|$)')
    pairs   = []
    for m in kt_re.finditer(block):
        pairs.append((m.group(1), m.group(2).strip()))
    for m in java_re.finditer(block):
        pairs.append((m.group(1), m.group(2).strip().replace("\n", " ")[:120]))
    return pairs


# ══════════════════════════════════════════════════════
# A. R.id 分发块
#    通用模式：任何含有 R.id.xxx 分支的 when / switch 块
#    不区分是 onOptionsItemSelected、actionItemPressed 还是自定义方法
# ══════════════════════════════════════════════════════

# 找所有 when(...) { 或 switch(...) { 开头，再用平衡括号提取 body
_DISPATCH_OPEN_RE = re.compile(
    r'(?:when\s*\([^)]{0,100}\)|switch\s*\([^)]{0,100}\))\s*\{',
    re.MULTILINE,
)

def extract_id_dispatchers(source: str, file_path: str) -> list[dict]:
    """
    找所有将 R.id.xxx 分发到 handler 的代码块。
    无论包装在哪个方法里（onOptionsItemSelected / actionItemPressed / lambda…）。
    """
    results = []
    lines   = source.splitlines()

    for m in _DISPATCH_OPEN_RE.finditer(source):
        brace_pos = source.index("{", m.start())
        body      = _balanced_block(source, brace_pos)

        if "R.id." not in body:
            continue  # 不含 R.id 分发，跳过

        line_idx  = _line_of(source, m.start())
        enclosing = _enclosing_fn(lines, line_idx - 1)
        pairs     = _extract_r_id_handlers(body)

        for (item_id, handler) in pairs:
            results.append({
                "kind":        "id_dispatch",
                "file":        file_path,
                "line":        line_idx,
                "item_id":     item_id,
                "handler":     handler,
                "enclosing_fn": enclosing,
        })

    # 处理没有items参数的对话框调用（新增逻辑）
    # 这些对话框可能包含动态生成的选项，如ChangeDateTimeFormatDialog
    for m in _ALL_DIALOG_RE.finditer(source):
        line_idx     = _line_of(source, m.start())
        enclosing    = _enclosing_fn(lines, line_idx - 1)
        dialog_class = m.group(1)
        
        # 检查是否已经在results中（避免重复）
        already_exists = any(
            r.get("component") == dialog_class and 
            r.get("line") == line_idx and
            r.get("file") == file_path
            for r in results
        )
        
        if already_exists:
            continue
            
        # 标记为无items参数的对话框
        results.append({
            "kind":          "dialog_without_items",
            "file":          file_path,
            "line":          line_idx,
            "component":     dialog_class,
            "items_source":  "unknown_dialog",
            "items_range":   "",
            "items_options": [],
            "enclosing_fn":  enclosing,
            "note":          f"dialog call without items parameter; options may be generated internally in {dialog_class}",
        })

    return results


# ══════════════════════════════════════════════════════
# B. 事件注册
#    通用模式：receiver.setOn*/addXxx*/doOn* { lambda } 或 (callback)
#    不依赖具体方法名列表
# ══════════════════════════════════════════════════════

_LISTENER_RE = re.compile(
    # receiver: binding.xxx. 或 someVar. 或 this.
    r'(?:(?:viewBinding|binding)\s*[\.\?]+\s*(\w+)|(\w+))\s*[\.\?]+'
    # 通用事件注册方法名模式（语义：注册一个回调）
    r'((?:set|add|do)On\w+|'
    r'\w+(?:Listener|Callback|Observer|Watcher|Handler)|'
    r'do(?:After|Before|On)\w+|'
    r'set\w+(?:Listener|Callback|Action|Changed|Click|Dismissed|Selected))'
    r'\s*[({]',
    re.MULTILINE,
)

# 链式 findViewById：R.id.xxx).setOnXxxListener(
_FIND_VIEW_LISTENER_RE = re.compile(
    r'R\.id\.(\w+)\s*\)'
    r'\s*[\.\?]+'
    r'((?:set|add|do)On\w+|'
    r'\w+(?:Listener|Callback|Observer|Watcher|Handler)|'
    r'do(?:After|Before|On)\w+|'
    r'set\w+(?:Listener|Callback|Action|Changed|Click|Dismissed|Selected))'
    r'\s*[({]',
    re.MULTILINE,
)

# 局部变量赋值：val/var xxx = yyy.findViewById(R.id.zzz)
_FIND_VIEW_ASSIGN_RE = re.compile(
    r'(\w+)\s*=\s*[\w.()]*\.?findViewById\s*\(\s*R\.id\.(\w+)\s*\)',
    re.MULTILINE,
)

# 非 View 的系统/基础设施对象 — 它们的事件注册对 UI 路径没有贡献
_NON_VIEW_RECEIVERS = {
    "decorView", "window", "contentResolver", "loaderManager",
    "handler", "executor", "lifecycle", "viewLifecycleOwner",
    "super", "this",
}

def _is_non_view_ref(view_ref: str) -> bool:
    """
    判断 view_ref 是否不代表实际的 View 实例：
      1. PascalCase 开头 → 类型名用作 SAM 接收者（e.g. SeekBar.OnSeekBarChangeListener）
      2. 在已知非 View 系统对象集合中
    """
    if not view_ref:
        return True
    if view_ref[0].isupper():
        return True
    if view_ref in _NON_VIEW_RECEIVERS:
        return True
    return False


def _infer_event_type(method: str) -> str:
    method_lower = method.lower()
    if "click"   in method_lower: return "click"
    if "check"  in method_lower or "change" in method_lower: return "value_change"
    if "text"   in method_lower: return "text_change"
    if "scroll" in method_lower: return "scroll"
    if "drag"   in method_lower or "touch" in method_lower: return "touch"
    if "select" in method_lower: return "select"
    if "dismiss" in method_lower or "close" in method_lower: return "dismiss"
    if "refresh" in method_lower: return "refresh"
    if "editor" in method_lower or "action" in method_lower: return "editor_action"
    if "page"   in method_lower: return "page_change"
    if "long"   in method_lower: return "long_click"
    return "interaction"


_CALLBACK_VAR_RE = re.compile(r'\s*([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)?)\s*\)')
_METHOD_REF_RE = re.compile(r'::(\w+)\b')
_ANON_LISTENER_HINT_RE = re.compile(r'\s*(?:object\s*:|new\s+[A-Za-z_]\w*(?:[.$][A-Za-z_]\w*)*(?:<[^>]+>)?\s*\()')


def _make_registration_snippet(source: str, start: int, end: int, limit: int = 180) -> str:
    snippet = source[start:min(len(source), end + limit)]
    return re.sub(r'\s+', ' ', snippet).strip()



def _detect_callback_metadata(source: str, start: int, end: int) -> tuple[str, str, str]:
    opener = source[end - 1:end] if end > start else ""
    tail = source[end:min(len(source), end + 240)]
    snippet = _make_registration_snippet(source, start, end)

    if opener == "{":
        return "lambda", "", snippet

    if opener == "(":
        m = _METHOD_REF_RE.search(tail)
        if m:
            return "method_ref", m.group(1), snippet
        if _ANON_LISTENER_HINT_RE.match(tail):
            return "anonymous_listener", "", snippet
        if "->" in tail[:160]:
            return "lambda", "", snippet
        m = _CALLBACK_VAR_RE.match(tail)
        if m:
            ref = m.group(1)
            if "." not in ref:
                return "callback_var", ref, snippet

    return "unknown", "", snippet



def extract_event_registrations(source: str, file_path: str) -> list[dict]:
    results = []
    lines   = source.splitlines()
    seen_positions: set[int] = set()

    # ── 局部变量 → R.id 映射（Step 2）──
    var_to_id: dict[str, str] = {}
    for m in _FIND_VIEW_ASSIGN_RE.finditer(source):
        var_to_id[m.group(1)] = m.group(2)

    # ── Pattern 1: 现有 binding.xxx / someVar 模式 ──
    for m in _LISTENER_RE.finditer(source):
        view_ref  = m.group(1) or m.group(2) or ""
        method    = m.group(3)

        if _is_non_view_ref(view_ref):
            continue
        if method.startswith("remove"):
            continue
        rest_after = source[m.end():m.end() + 20].lstrip()
        if rest_after.startswith("null"):
            continue

        # 变量追踪：如果 view_ref 在 var_to_id 中，替换为 XML id
        if view_ref in var_to_id:
            view_ref = var_to_id[view_ref]

        is_pending_intent = "PendingIntent" in method
        line_idx  = _line_of(source, m.start())
        enclosing = _enclosing_fn(lines, line_idx - 1)
        callback_kind, callback_ref, registration_snippet = _detect_callback_metadata(
            source, m.start(), m.end()
        )

        entry = {
            "kind":        "event_registration",
            "file":        file_path,
            "line":        line_idx,
            "view_ref":    view_ref,
            "method":      method,
            "event_type":  _infer_event_type(method),
            "enclosing_fn": enclosing,
            "callback_kind": callback_kind,
            "callback_ref": callback_ref,
            "registration_snippet": registration_snippet,
        }
        if is_pending_intent:
            entry["event_type"] = "pending_intent"
            entry["is_pending_intent"] = True
        results.append(entry)
        seen_positions.add(m.start())

    # ── Pattern 2: findViewById(R.id.xxx).setOnXxxListener( ──
    for m in _FIND_VIEW_LISTENER_RE.finditer(source):
        if m.start() in seen_positions:
            continue
        xml_id = m.group(1)
        method = m.group(2)

        if method.startswith("remove"):
            continue
        rest_after = source[m.end():m.end() + 20].lstrip()
        if rest_after.startswith("null"):
            continue

        line_idx  = _line_of(source, m.start())
        enclosing = _enclosing_fn(lines, line_idx - 1)
        callback_kind, callback_ref, registration_snippet = _detect_callback_metadata(
            source, m.start(), m.end()
        )

        results.append({
            "kind":        "event_registration",
            "file":        file_path,
            "line":        line_idx,
            "view_ref":    xml_id,
            "method":      method,
            "event_type":  _infer_event_type(method),
            "enclosing_fn": enclosing,
            "callback_kind": callback_kind,
            "callback_ref": callback_ref,
            "registration_snippet": registration_snippet,
        })

    return results


# ══════════════════════════════════════════════════════
# C. 可见性控制
#    通用模式：对 visibility / isVisible / isGone / beXxx 的赋值或调用
#    不依赖框架扩展函数名列表
# ══════════════════════════════════════════════════════

_VISIBILITY_RE = re.compile(
    r'([\w\.]+)\s*[\.\?]+'
    r'(visibility|isVisible|isGone|isInvisible|'
    r'be(?:Visible|Gone|Invisible|VisibleIf|GoneIf|InvisibleIf)|'
    r'setVisibility)\s*[=(]',
    re.MULTILINE,
)

# menu item: findItem(R.id.xxx).isVisible = condition
_MENU_VIS_RE = re.compile(
    r'findItem\s*\(\s*R\.id\.(\w+)\s*\)\s*[\.\?]+\s*isVisible\s*=\s*(.+)',
    re.MULTILINE,
)

def extract_visibility_controls(source: str, file_path: str) -> list[dict]:
    results = []
    lines   = source.splitlines()

    for m in _VISIBILITY_RE.finditer(source):
        line_idx  = _line_of(source, m.start())
        view_ref  = m.group(1)
        prop      = m.group(2)

        # 提取条件：向上找最近 if / when / else，或提取括号内参数
        condition = ""
        if prop.endswith("If"):
            rest  = source[m.end():]
            depth = 1
            end   = 0
            for i, ch in enumerate(rest):
                if ch == "(": depth += 1
                elif ch == ")": depth -= 1
                if depth == 0:
                    end = i
                    break
            condition = rest[:end].strip()
        else:
            for i in range(line_idx - 2, max(0, line_idx - 10), -1):
                s = lines[i].strip()
                if re.match(r'(?:if\s*\(|}\s*else|when\s*\(|else\s*\{)', s):
                    condition = s[:120]
                    break

        results.append({
            "kind":      "visibility_control",
            "file":      file_path,
            "line":      line_idx,
            "view_ref":  view_ref,
            "property":  prop,
            "condition": condition,
        })

    # menu item visibility
    for m in _MENU_VIS_RE.finditer(source):
        line_idx = _line_of(source, m.start())
        results.append({
            "kind":      "menu_item_visibility",
            "file":      file_path,
            "line":      line_idx,
            "item_id":   m.group(1),
            "condition": m.group(2).strip(),
        })

    return results


# ══════════════════════════════════════════════════════
# D. 布局膨胀
#    通用模式：inflate(R.layout.xxx) 或 XxxBinding.inflate()
#    识别三种形式：直接 inflate、Binding.inflate、by viewBinding 委托
# ══════════════════════════════════════════════════════

_LAYOUT_INFLATE_RE  = re.compile(r'inflate\s*\(\s*R\.layout\.(\w+)', re.MULTILINE)
_BINDING_INFLATE_RE = re.compile(r'(\w+Binding)\.inflate\s*\(', re.MULTILINE)
_BY_BINDING_RE      = re.compile(r'by\s+\w*[Bb]inding\w*\s*\(\s*(\w+Binding)\s*::', re.MULTILINE)

def extract_inflates(source: str, file_path: str) -> list[dict]:
    results = []
    lines   = source.splitlines()

    for m in _LAYOUT_INFLATE_RE.finditer(source):
        line_idx  = _line_of(source, m.start())
        enclosing = _enclosing_fn(lines, line_idx - 1)
        results.append({
            "kind":        "inflate_layout",
            "file":        file_path,
            "line":        line_idx,
            "layout":      m.group(1),
            "enclosing_fn": enclosing,
        })

    seen_bindings = set()
    for m in _BINDING_INFLATE_RE.finditer(source):
        cls = m.group(1)
        if cls in seen_bindings:
            continue
        line_idx  = _line_of(source, m.start())
        enclosing = _enclosing_fn(lines, line_idx - 1)
        # by viewBinding 是静态绑定，不算动态膨胀
        preceding = source[max(0, m.start()-20):m.start()]
        if "::" in preceding:
            continue
        seen_bindings.add(cls)
        results.append({
            "kind":          "inflate_binding",
            "file":          file_path,
            "line":          line_idx,
            "layout":        _binding_class_to_layout(cls),
            "binding_class": cls,
            "enclosing_fn":  enclosing,
        })

    for m in _BY_BINDING_RE.finditer(source):
        cls = m.group(1)
        results.append({
            "kind":          "static_binding",
            "file":          file_path,
            "line":          _line_of(source, m.start()),
            "layout":        _binding_class_to_layout(cls),
            "binding_class": cls,
            "enclosing_fn":  "class_level",
        })

    return results


# ══════════════════════════════════════════════════════
# E. 数据驱动 UI
#    通用模式：构建选项列表后传给弹窗/列表组件
#    支持三种构建方式：
#      E1. arrayListOf(RadioItem(id, getString(R.string.xxx)), ...) — 静态枚举选项
#      E2. arrayListOf(getString(R.string.xxx), ...) — 纯字符串选项
#      E3. for (i in a..b) { items.add(...) } — 数值范围动态选项
#      E4. forEach/map 遍历枚举/列表 — 运行时动态选项
# ══════════════════════════════════════════════════════

# 找 items 被传入弹窗/list 的调用（通用：任何接收 items/options 变量的构造调用）
_DATA_DIALOG_WITH_ITEMS_RE = re.compile(
    r'(\w+Dialog|\w+Sheet|\w+Picker|\w+Chooser)\s*\('
    r'(?:[^)]{0,200}?)\bitems\b',
    re.MULTILINE | re.DOTALL,
)

# 找所有对话框调用，无论是否有items参数（用于检测可能包含动态选项的对话框）
_ALL_DIALOG_RE = re.compile(
    r'(\w+Dialog|\w+Sheet|\w+Picker|\w+Chooser)\s*\(\s*this[^)]*\)',
    re.MULTILINE,
)

# for (i in a..b) 或 (a until b) / (a..<b) 范围循环
# Group 1 = lower bound, Group 2 = operator (.., until, ..<), Group 3 = upper bound
_ITEM_LOOP_RANGE_RE = re.compile(
    r'for\s*\(\s*\w+\s+in\s+(\w+|\d+)\s*(\.\.(?:<)?|until)\s*(\w+|\d+)',
    re.MULTILINE,
)

# 命名整数常量：const val NAME = 123  或  val NAME = 123（companion object 风格）
# 仅匹配全大写名称（SCREAMING_SNAKE_CASE），避免误匹配普通变量
_CONST_VAL_RE = re.compile(
    r'(?:const\s+)?val\s+([A-Z][A-Z0-9_]+)\s*(?::\s*Int)?\s*=\s*(\d+)',
    re.MULTILINE,
)

# forEach / map 遍历（运行时动态）
_ITEM_LOOP_FOREACH_RE = re.compile(
    r'(\w+)\s*\.\s*(?:forEach|map|filter|mapTo)\s*\{',
    re.MULTILINE,
)

# RadioItem(id, getString(R.string.label)) — 提取 label（资源键）
_RADIO_ITEM_STR_RE = re.compile(
    r'RadioItem\s*\([^,)]+,\s*getString\s*\(\s*R\.string\.(\w+)',
    re.MULTILINE,
)

# RadioItem(id, "literal string") — 提取字面量
_RADIO_ITEM_LIT_RE = re.compile(
    r'RadioItem\s*\([^,)]+,\s*"([^"]+)"',
    re.MULTILINE,
)

# getString(R.string.label) 作为直接列表元素 — 提取 label
_STRING_ITEM_RE = re.compile(
    r'getString\s*\(\s*R\.string\.(\w+)',
    re.MULTILINE,
)

# 找 arrayListOf / mutableListOf / listOf 关键字的位置
_ARRAY_LIST_KW_RE = re.compile(
    r'(?:arrayListOf|mutableListOf|listOf)\s*\(',
    re.MULTILINE,
)


def _extract_list_body(snippet: str) -> str:
    """
    在 snippet 中找最后一个 arrayListOf/mutableListOf/listOf(，
    然后用平衡括号提取完整的列表体（不被首个 ) 截断）。
    """
    best_pos = -1
    for m in _ARRAY_LIST_KW_RE.finditer(snippet):
        best_pos = m.end() - 1  # 指向开括号 (
    if best_pos == -1:
        return ""
    # 用平衡括号提取 arrayListOf(...) 完整内容，括号为 ( )
    return _balanced_block(snippet, best_pos, open_ch="(", close_ch=")", max_len=2000)


def _resolve_constants(project_root: str) -> dict:
    """
    Scan all Kotlin source files for named integer constants.
    Matches SCREAMING_SNAKE_CASE names: const val MAX_FOO = 20

    Returns {NAME: int_value} for use in expanding range loop bounds.
    Only reads files under src/main to avoid third-party library noise.
    """
    constants: dict = {}
    for kt in (p for p in android_project.source_files(project_root) if p.suffix == ".kt"):
        try:
            src = kt.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for m in _CONST_VAL_RE.finditer(src):
            name = m.group(1)
            try:
                constants[name] = int(m.group(2))
            except ValueError:
                pass
    return constants


def _extract_static_options(snippet: str) -> list[str]:
    """
    从 items 构建代码段中提取静态选项标签。
    优先从 RadioItem(..., getString(R.string.xxx)) 中提取资源名，
    其次从 getString(R.string.xxx) 直接提取。
    使用平衡括号提取列表体，避免被首个 ) 截断。
    """
    list_body = _extract_list_body(snippet)
    if not list_body:
        return []

    # 先尝试 RadioItem(id, getString(R.string.xxx)) 模式
    options = _RADIO_ITEM_STR_RE.findall(list_body)
    if options:
        return options

    # 再尝试 RadioItem(id, "literal") 模式
    options = _RADIO_ITEM_LIT_RE.findall(list_body)
    if options:
        return options

    # 最后尝试直接 getString(R.string.xxx) 模式
    options = _STRING_ITEM_RE.findall(list_body)
    return options


def extract_data_driven_ui(source: str, file_path: str,
                           constants: "dict | None" = None) -> list[dict]:
    """
    E. 数据驱动 UI 提取。
    constants: {NAME: int_value} 用于展开数值范围循环（如 1..MAX_COLUMN_COUNT → 1..20）。
    当 constants 提供时，range_loop 类型的 items_options 会被展开为完整列表。
    
    现在也捕获没有items参数的对话框调用，标记为"dialog_without_items"，
    用于后续分析动态生成的选项（如ChangeDateTimeFormatDialog）。
    """
    results = []
    lines   = source.splitlines()
    _consts = constants or {}
    
    # 处理有items参数的对话框（原有逻辑）
    for m in _DATA_DIALOG_WITH_ITEMS_RE.finditer(source):
        line_idx     = _line_of(source, m.start())
        enclosing    = _enclosing_fn(lines, line_idx - 1)
        dialog_class = m.group(1)

        # 向前 800 字符的代码段用于分析选项来源
        snippet_before = source[max(0, m.start() - 800): m.start()]

        # E3: 数值范围循环
        loop_range_m = _ITEM_LOOP_RANGE_RE.search(snippet_before)
        # E4: forEach/map 遍历
        loop_foreach_m = _ITEM_LOOP_FOREACH_RE.search(snippet_before)
        # E1/E2: 静态列表选项
        static_options = _extract_static_options(snippet_before)

        if static_options:
            items_source  = "static_list"
            items_range   = ""
            items_options = static_options
            note          = "options statically defined in source"
        elif loop_range_m:
            # Group 1 = lower, Group 2 = operator (.., until, ..<), Group 3 = upper
            lo_str = loop_range_m.group(1)
            op_str = loop_range_m.group(2)   # ".." or "until" or "..<"
            hi_str = loop_range_m.group(3)
            items_range = f"{lo_str}{op_str}{hi_str}"

            # Resolve named constants (e.g. MAX_COLUMN_COUNT → 20)
            lo_val = int(lo_str) if lo_str.isdigit() else _consts.get(lo_str)
            hi_val = int(hi_str) if hi_str.isdigit() else _consts.get(hi_str)

            if lo_val is not None and hi_val is not None:
                # "until" and "..<" are exclusive upper bounds; ".." is inclusive
                exclusive = op_str in ("until", "..<")
                hi_actual = hi_val if exclusive else hi_val + 1
                items_options = [str(i) for i in range(lo_val, hi_actual)]
                items_source  = "range_loop"
                note          = f"options from range {items_range} (resolved: {len(items_options)} items)"
            else:
                items_options = []
                items_source  = "range_loop"
                note          = f"options from range {items_range} (unresolved constants)"
        elif loop_foreach_m:
            items_source  = "foreach_loop"
            items_range   = loop_foreach_m.group(1)
            items_options = []
            note          = "options built by iterating collection at runtime"
        else:
            items_source  = "unknown"
            items_range   = ""
            items_options = []
            note          = "options built programmatically at runtime"

        results.append({
            "kind":          "data_driven_ui",
            "file":          file_path,
            "line":          line_idx,
            "component":     dialog_class,
            "items_source":  items_source,
            "items_range":   items_range,
            "items_options": items_options,
            "enclosing_fn":  enclosing,
            "note":          note,
        })

    return results


# ══════════════════════════════════════════════════════
# F. view_ref → XML id resolution via findViewById
# ══════════════════════════════════════════════════════

_FIND_VIEW_BY_ID_KT_RE = re.compile(
    r'(?:val|var)\s+(\w+)\s*(?::\s*\w+)?\s*=\s*'
    r'(?:\w+\s*\.\s*)?findViewById\w*\s*(?:<[^>]*>\s*)?\(\s*R\.id\.(\w+)',
)

_FIND_VIEW_BY_ID_JAVA_RE = re.compile(
    r'(\w+)\s*=\s*(?:\(\s*\w+\s*\)\s*)?'
    r'(?:\w+\s*\.\s*)?'
    r'findViewById\s*\(\s*R\.id\.(\w+)',
)


def _extract_viewref_id_map(source: str) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for m in _FIND_VIEW_BY_ID_KT_RE.finditer(source):
        mapping[m.group(1)] = m.group(2)
    for m in _FIND_VIEW_BY_ID_JAVA_RE.finditer(source):
        var_name = m.group(1)
        if var_name not in mapping:
            mapping[var_name] = m.group(2)
    return mapping


# ══════════════════════════════════════════════════════
# G. AST post-processing: receiver types + if/else id_dispatch
# ══════════════════════════════════════════════════════

def _ast_postprocess(findings: dict, project_root: str,
                     file_path_map: dict[str, Path]):
    """Single AST pass per file: annotate receiver types + detect if/else R.id dispatchers."""
    if ast_index is None or ast_index.get_parser is None:
        return

    hierarchy = ast_index.build_class_hierarchy(project_root)

    existing_dispatch = set()
    for d in findings.get("id_dispatchers", []):
        existing_dispatch.add((d.get("item_id", ""), d.get("file", "")))

    regs_by_file: dict[str, list[dict]] = {}
    for reg in findings.get("event_registrations", []):
        regs_by_file.setdefault(reg["file"], []).append(reg)

    for rel_path, actual_path in file_path_map.items():
        lang = ("kotlin" if actual_path.suffix == ".kt"
                else "java" if actual_path.suffix == ".java" else "")
        if not lang:
            continue

        parsed = ast_index.parse_file(actual_path)
        if parsed is None:
            continue
        source, root_node = parsed
        lines = source.decode("utf-8", errors="ignore").splitlines()

        # --- receiver type annotation ---
        var_types = ast_index.extract_variable_types(source, root_node, lang)
        for reg in regs_by_file.get(rel_path, []):
            view_ref = reg.get("view_ref", "")
            var_type = var_types.get(view_ref, "")
            reg["receiver_type"] = var_type
            if var_type:
                reg["is_view"] = ast_index.is_view_type(var_type, hierarchy)
            else:
                reg["is_view"] = None

        # --- if/else-if R.id.xxx dispatch detection ---
        for node in ast_index._walk(root_node):
            if node.kind() not in ("if_expression", "if_statement"):
                continue
            condition = node.child_by_field_name("condition")
            if condition is None:
                continue
            cond_text = ast_index._node_text(source, condition)
            for m in re.finditer(r"R\.id\.(\w+)", cond_text):
                item_id = m.group(1)
                if (item_id, rel_path) in existing_dispatch:
                    continue
                existing_dispatch.add((item_id, rel_path))
                line_idx = node.start_position().row + 1
                enclosing = _enclosing_fn(lines, line_idx - 1)
                consequence = node.child_by_field_name("consequence")
                handler = ""
                if consequence:
                    handler = (ast_index._node_text(source, consequence)
                               [:120].strip().replace("\n", " "))
                findings["id_dispatchers"].append({
                    "kind":        "id_dispatch",
                    "file":        rel_path,
                    "line":        line_idx,
                    "item_id":     item_id,
                    "handler":     handler,
                    "enclosing_fn": enclosing,
                })


# ══════════════════════════════════════════════════════
# Entry point
# ══════════════════════════════════════════════════════

def _is_app_source(path: Path, root: Path) -> bool:
    """
    只扫描项目自身的 app/src/main 源码，排除第三方库的 includeBuild 子目录
    （如 rtl-viewpager、Simple-Commons 等）。
    判断依据：路径中 app/src/main 之前必须没有其他模块根目录层级。
    简化实现：如果相对路径的第一段不是 app，视为第三方库，跳过事件注册扫描。
    """
    try:
        rel = path.relative_to(root)
        parts = rel.parts
        # 允许: app/src/... 或 app\src\...（单模块项目）
        # 也允许: commons/src/...（多模块同仓）
        # 排除：独立 includeBuild 仓库中的代码（通常是根目录直接有 src/）
        # 启发式：如果第一段是已知第三方库名，跳过
        third_party_roots = {"rtl-viewpager", "rtl_viewpager", "Simple-Commons",
                              "commons-lib", "libs", "vendor"}
        return parts[0] not in third_party_roots
    except ValueError:
        return True


def _enrich_findings_with_symbols(findings: dict[str, list], project_root: str, file_prefix: str = "") -> int:
    if ast_index is None:
        return 0
    try:
        index = ast_index.build_project_index(project_root, file_prefix=file_prefix)
    except Exception:
        return 0
    if not index.ast_available:
        return 0
    enriched = 0
    for rows in findings.values():
        for item in rows:
            if not isinstance(item, dict) or not item.get("file") or item.get("line") is None:
                continue
            symbol = index.find_enclosing_symbol(str(item.get("file")), int(item.get("line", 0)))
            if not symbol:
                continue
            item["enclosing_symbol_id"] = symbol.get("symbol_id", "")
            item["function_name"] = symbol.get("function_name", "")
            item["function_range"] = {
                "start_line": symbol.get("start_line", 0),
                "end_line": symbol.get("end_line", 0),
            }
            enriched += 1
    return enriched


def run(project_root: str, file_prefix: str = "",
        scan_events: bool = True) -> dict:
    constants = _resolve_constants(project_root)

    root = Path(project_root)
    src_files = android_project.source_files(root)

    findings: dict[str, list] = {
        "id_dispatchers":    [],
        "event_registrations": [],
        "visibility_controls": [],
        "inflates":          [],
        "data_driven_ui":    [],
    }
    view_ref_id_map: dict[str, dict[str, str]] = {}
    file_path_map: dict[str, Path] = {}

    for src in src_files:
        try:
            source = src.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        rel = str(src.relative_to(root))
        if file_prefix:
            rel = file_prefix + "/" + rel

        file_path_map[rel] = src

        findings["id_dispatchers"].extend(extract_id_dispatchers(source, rel))
        if scan_events:
            findings["event_registrations"].extend(extract_event_registrations(source, rel))
        findings["visibility_controls"].extend(extract_visibility_controls(source, rel))
        findings["inflates"].extend(extract_inflates(source, rel))
        findings["data_driven_ui"].extend(extract_data_driven_ui(source, rel, constants))

        ref_map = _extract_viewref_id_map(source)
        if ref_map:
            view_ref_id_map[rel] = ref_map

    _ast_postprocess(findings, project_root, file_path_map)

    enriched_count = _enrich_findings_with_symbols(findings, project_root, file_prefix=file_prefix)
    stats = {k: len(v) for k, v in findings.items()}
    stats["source_files_scanned"] = len(src_files)
    stats["findings_with_enclosing_symbol"] = enriched_count

    return {"findings": findings, "stats": stats, "view_ref_id_map": view_ref_id_map}


if __name__ == "__main__":
    import sys
    project = sys.argv[1] if len(sys.argv) > 1 else "."
    result  = run(project)
    out = Path("output/source_findings.json")
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False))
    print("Source scan complete:")
    for k, v in result["stats"].items():
        print(f"  {k}: {v}")
