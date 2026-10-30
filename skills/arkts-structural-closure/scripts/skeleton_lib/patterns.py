"""Regex patterns for skeleton detection.

Format: list of (subtype, regex_str, suggested_action, method_kind_or_None).

method_kind is filled for L2 empty-body patterns so the suggested_action can
be specialized; None for L3 fakes which don't depend on the host method.

Phase 4 will introduce ast_scanner.py and demote regex patterns to fallback,
but the subtype/suggested_action strings stay stable.
"""
import re

# ─── L3 fake-content ──────────────────────────────────────────────────────────
# Shared keyword group: any "stub-intent" word in code triggers fake-content.
# Includes EN/CN stub markers + classic console fake patterns.
_STUB_KEYWORDS = r"TODO|stub|placeholder|pending|noop|navigate to|click|待|占位|临时|后续"
_CONSOLE_METHODS = r"info|log|warn|error|debug"
_TOAST_CALLS = r"Toast\.show|prompt\.showToast|promptAction\.showToast"

_FAKE_CONTENT = [
    # 1. console.<info|log|warn|error|debug>('<stub-keyword>...')  — covers all variants
    (
        rf"console\.(?:{_CONSOLE_METHODS})\(\s*['\"](?:{_STUB_KEYWORDS})",
        "Replace stub-level console call with real implementation, "
        "or emit `// FWD-REF: <P-ID> resolve_by=Slice N Step 3X` next to a no-op body. "
        "console.* with stub keywords (TODO/stub/placeholder/pending/noop/navigate to/click/待/占位/临时/后续) is forbidden.",
    ),
    # 2. Toast / prompt with stub keyword content
    (
        rf"(?:{_TOAST_CALLS})\([^)]*['\"](?:{_STUB_KEYWORDS})",
        "Replace stub Toast/prompt content with real localized text (via $r('app.string.xxx')) "
        "or add // FWD-REF marker if the message is owned by a later Slice.",
    ),
    # 3. Text('<stub-keyword>') literals in UI
    (
        rf"Text\(\s*['\"](?:{_STUB_KEYWORDS})",
        "Remove stub-literal Text() (TODO/stub/placeholder/pending/noop/待/占位/临时/后续); "
        "render real content or add // FWD-REF marker.",
    ),
    # 4. Static "Loading..." that should be state-driven (special-cased, kept separate)
    (
        r"Text\(\s*['\"]Loading\.\.\.['\"]",
        "Replace static 'Loading...' literal with state-driven loading indicator "
        "(e.g. LoadingProgress bound to @Local isLoading).",
    ),
    # 5. Generic Placeholder/placeholder literal
    (
        r"Text\(\s*['\"](?:Placeholder|placeholder)['\"]",
        "Remove 'Placeholder' literal placeholder.",
    ),
]

# ─── L3 naked-TODO ────────────────────────────────────────────────────────────
_NAKED_TODO = [
    (
        r"//\s*TODO:?\s*implement\b",
        "Implement, or replace with `// FWD-REF: <P-ID> resolve_by=Slice N Step 3X` "
        "pointing to the owning Slice.",
    ),
    (
        r"//\s*TODO\[",
        "Bracket-TODO is forbidden. Replace `// TODO[Slice N]` with "
        "`// FWD-REF: P-S{N}-{seq} resolve_by=Slice N Step 3X`.",
    ),
    (
        r"//\s*TODO:?\s*实现",
        "Implement, or replace with // FWD-REF marker.",
    ),
    (
        r"//\s*待实现\b",
        "Implement, or replace with // FWD-REF marker.",
    ),
    (
        r"//\s*待接入\b",
        "Implement, or replace with // FWD-REF marker pointing to the owning Slice.",
    ),
    # 通用 // TODO 注释 — 允许保留，但必须在 placeholder-registry 同步登记
    # （邻接 FWD-REF/PLACEHOLDER marker OR 按 file:line 反查 registry 命中即合法）
    (
        r"//\s*TODO\b",
        "// TODO comment must either have an adjacent // FWD-REF/PLACEHOLDER marker, "
        "or its file:line must appear in placeholder-registry.md (kind=forward-ref-uncertain "
        "/ resource-pending-* / etc.). Unregistered // TODO is forbidden.",
    ),
]

# ─── L3 throw-stub ────────────────────────────────────────────────────────────
_THROW_STUB = [
    (
        r"throw\s+['\"][^'\"]*Slice\s*\d",
        "Replace throw-stub with real implementation, "
        "or register this location in placeholder-registry.md (kind=forward-ref + resolve_by).",
    ),
    (
        r"throw\s+(?:new\s+)?Error\(\s*['\"]not implemented",
        "Implement the method, or register as kind=forward-ref in placeholder-registry.",
    ),
]

# ─── L2 empty-body (regex approximation; Phase 4 will use AST) ────────────────
_EMPTY_BODY = [
    (
        r"aboutToAppear\s*\(\)\s*\{\s*\}",
        "Add ViewModel/Repository call in aboutToAppear(), or add // FWD-REF marker "
        "if the wiring is owned by another Slice.",
        "lifecycle",
    ),
    (
        r"aboutToAppear\s*\(\)\s*\{\s*return\s*;?\s*\}",
        "aboutToAppear() should not be a bare return. Wire real initialization or add FWD-REF.",
        "lifecycle",
    ),
    (
        r"@Builder\s+\w+\s*\(\)\s*\{\s*\}",
        "Empty @Builder. Implement content or add FWD-REF marker next to a Stack { } stub.",
        "builder",
    ),
    (
        r"@Builder\s+\w+\s*\(\)\s*\{\s*Column\s*\(\)\s*\{\s*\}\s*\}",
        "Builder body is only `Column() { }`. Implement content or add FWD-REF marker.",
        "builder",
    ),
    (
        r"onClick\s*\(\s*\(\)\s*=>\s*\{\s*\}\s*\)",
        "Empty onClick handler. Implement or add FWD-REF marker pointing to owning Slice.",
        "handler",
    ),
    (
        r"onClick\s*:\s*\(\s*\)\s*=>\s*\{\s*\}",
        "Empty onClick handler. Implement or add FWD-REF marker.",
        "handler",
    ),
    # Handler body whose only content is a stub-keyword comment (no FWD-REF marker)
    # e.g. `() => { // TODO `, `() => { // 待实现 `, `() => { /* noop */ }`
    (
        rf"=>\s*\{{\s*(?://|/\*)\s*(?:{_STUB_KEYWORDS})",
        "Handler body is a stub-keyword comment only. Implement real logic or replace "
        "with `// FWD-REF: <P-ID> resolve_by=Slice N Step 3X` marker for forward reference.",
        "handler",
    ),
    # Layout container whose only body is a comment — a hidden child placeholder that
    # renders nothing and is invisible to @Builder/Text checks (E2). Promoted to legit
    # only when an adjacent // FWD-REF marker + registry entry exists.
    (
        r"\b(?:Column|Row|Stack|Flex)\s*\([^)]*\)\s*\{\s*(?://[^\n]*|/\*[^*]*\*/)\s*\}",
        "Layout container with a comment-only body is a hidden placeholder (renders nothing). "
        "Use a `@Builder <slot>() {}` slot + `// FWD-REF: <P-ID> ... kind=forward-ref` "
        "(registered as a wires embed), never a bare Column/Stack with only a comment.",
        "container",
    ),
]


# ─── Compiled pattern list ────────────────────────────────────────────────────
# Each entry: (subtype, compiled_regex, suggested_action, method_kind)
SKELETON_PATTERNS = []

for rx, action in _FAKE_CONTENT:
    SKELETON_PATTERNS.append(("fake-content", re.compile(rx), action, None))

for rx, action in _NAKED_TODO:
    SKELETON_PATTERNS.append(("naked-TODO", re.compile(rx), action, None))

for rx, action in _THROW_STUB:
    SKELETON_PATTERNS.append(("throw-stub", re.compile(rx), action, None))

for rx, action, kind in _EMPTY_BODY:
    SKELETON_PATTERNS.append(("empty-body", re.compile(rx), action, kind))


# ─── Heuristic: empty @Builder with prose placeholder ─────────────────────────
# WARN-level; flagged as L2 empty-body but with a distinct method_kind tag.
EMPTY_BUILDER_HEURISTIC = re.compile(
    r"@Builder\s+(\w+)\s*\(\)\s*\{\s*Column\s*\(\)\s*\{\s*Text\(\s*['\"]"
    r"(?:占位|TODO|pending|Coming soon|Placeholder)",
    re.MULTILINE,
)


# ─── Escape-hatch phrases (handoff prose, not .ets) ───────────────────────────
ESCAPE_HATCH_PHRASES = [
    "由 fixer",
    "后续接通",
    "a2h-fixer 完成",
    "后续 fixer",
    "已知不完整",
    "verify 阶段补齐",
    "fixer 补齐",
]


# ─── Legitimacy markers ───────────────────────────────────────────────────────
# `// FWD-REF: <P-ID> resolve_by=Slice <N> Step <3a|3b|3c|3d>`
FWD_REF_MARKER = re.compile(
    r"//\s*FWD-REF:\s*(?P<p_id>P-[A-Za-z0-9_-]+)\s+"
    r"resolve_by=Slice\s+(?P<slice>\d+)\s+Step\s+(?P<step>3[a-z])"
)

# `// PLACEHOLDER: <P-ID> trigger=<whitelist phrase>`
PLACEHOLDER_MARKER = re.compile(
    r"//\s*PLACEHOLDER:\s*(?P<p_id>P-[A-Za-z0-9_-]+)\s+trigger=(?P<trigger>.+?)$",
    re.MULTILINE,
)


# ─── L5 resource-pending ─────────────────────────────────────────────────────
# Patterns scanned only against resource JSON files (resources/<locale>/element/*.json).
# Each finding requires a matching entry in spec/placeholder-registry.md
# with kind=resource-pending-translation or kind=resource-pending-asset;
# otherwise classifier marks as L5 FAIL.

# `"value": "[TODO: translate] <fallback>"` — must be registered as resource-pending-translation
RESOURCE_TODO_TRANSLATE = re.compile(
    r'"value"\s*:\s*"\[TODO:\s*translate\][^"]*"'
)

# `"value": "[TODO: ...]" / "[FIXME: ...]" / "[XXX: ...]"` — any bracketed TODO marker in value
RESOURCE_BRACKETED_TODO = re.compile(
    r'"value"\s*:\s*"\[(?:TODO|FIXME|XXX)\b[^\]]*\][^"]*"'
)

# `"value": "...TODO..." / "...FIXME..." / "...XXX..."` — bare marker word inside value
# (after stripping the bracketed cases above; the classifier should test bracketed first)
RESOURCE_BARE_TODO_WORD = re.compile(
    r'"value"\s*:\s*"[^"]*\b(?:TODO|FIXME|XXX)\b[^"]*"'
)

# Compiled list (for classifier resource-json scan)
# suggested_action 末尾统一指令：检测到 i18n 占位即直接调用 arkts-i18n skill 自动完成翻译流程
_I18N_RECOMMENDATION = (
    " 检测到 i18n 占位即直接调用 arkts-i18n skill 完成翻译："
    "按其『硬编码字符串扫描与迁移』流程，LLM 借 skill 指导为每个 locale 产出真实翻译并落盘 → "
    "跑 scripts/audit_i18n_completeness.sh 验证 key 一致性 → "
    "将对应 P-ID 的 registry status 更新为 resolved。"
)

RESOURCE_PENDING_PATTERNS = [
    (
        "resource-pending-unregistered",
        RESOURCE_TODO_TRANSLATE,
        "Resource value contains [TODO: translate] but no matching "
        "kind=resource-pending-translation entry in spec/placeholder-registry.md. "
        "Either complete the translation OR register a P-RES-TRANS-{seq} entry "
        "with trigger=`<locale> 翻译就绪`." + _I18N_RECOMMENDATION,
    ),
    (
        "resource-pending-unregistered",
        RESOURCE_BRACKETED_TODO,
        "Resource value contains a bracketed [TODO/FIXME/XXX:...] marker but no matching "
        "placeholder-registry entry. Register with appropriate kind=resource-pending-* "
        "or complete the value." + _I18N_RECOMMENDATION,
    ),
    (
        "resource-pending-unregistered",
        RESOURCE_BARE_TODO_WORD,
        "Resource value contains a bare TODO/FIXME/XXX word. "
        "Complete the value or register as resource-pending placeholder." + _I18N_RECOMMENDATION,
    ),
]
