#!/usr/bin/env bash
# audit_i18n_completeness.sh — i18n cross-locale key consistency audit.
#
# 单一职责：检测跨 locale 的 string.json / plural.json / strarray.json 的 key 一致性。
#   base 的全部 key 必须在每个 language locale（zh_CN / en_US / ...）都存在；
#   mode locale（dark / horizontal / vertical 等）按差异覆盖即可，豁免。
#
# 资源 value 内的未注册 [TODO: translate] / 裸 TODO 检测**不在本脚本范围**——
# 已由 arkts-structural-closure/scripts/audit_skeletons.py 的 L5 patterns 统一负责。
# 两者职责正交：本脚本专管"跨 locale 完整性"。
#
# 用法（由 arkts-i18n 任务完成后自调，不被其他 skill 跨引用）：
#   bash audit_i18n_completeness.sh \
#       --project-root <abs> \
#       --output-json docs/i18n-audit.json
#
# 退出码：
#   0  全 PASS（key 一致）
#   1  有 key_missing FAIL 项
#   2  脚本错误（参数缺失等）
#
# 输出 JSON 结构：
#   {
#     "locales": ["base", "zh_CN", ...],
#     "language_locales": ["zh_CN", ...],      # 参与 key 一致性校验的 locale
#     "mode_locales": ["dark", ...],            # 豁免 locale
#     "key_count_per_locale": { "base": N, "zh_CN": N, ... },
#     "findings": [
#       { "type": "key-missing", "locale": "zh_CN", "key": "home_feed", "base_locale": "base", "suggested_action": "..." }
#     ],
#     "summary": { "key_missing": N, "FAIL": N }
#   }

set -euo pipefail

PROJECT_ROOT=""
OUTPUT_JSON=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --project-root)   PROJECT_ROOT="$2"; shift 2 ;;
        --output-json)    OUTPUT_JSON="$2"; shift 2 ;;
        --help|-h)
            grep '^#' "$0" | head -40
            exit 0
            ;;
        *)
            echo "unknown arg: $1" >&2
            exit 2
            ;;
    esac
done

if [[ -z "$PROJECT_ROOT" ]]; then
    echo "error: --project-root required" >&2
    exit 2
fi

# Resolve to absolute path; on Git Bash use `pwd -W` to get Windows-style for Python interop
if pwd -W >/dev/null 2>&1; then
    PROJECT_ROOT="$(cd "$PROJECT_ROOT" && pwd -W)"
else
    PROJECT_ROOT="$(cd "$PROJECT_ROOT" && pwd)"
fi
OUTPUT_JSON="${OUTPUT_JSON:-/dev/stdout}"

RESOURCES_ROOT="$PROJECT_ROOT/entry/src/main/resources"

if [[ ! -d "$RESOURCES_ROOT" ]]; then
    echo "error: resources root not found: $RESOURCES_ROOT" >&2
    exit 2
fi

# ─── Python helper: cross-locale key consistency only ───────────────────────
PY_HELPER=$(cat <<'PYEOF'
import json, os, sys

project_root = sys.argv[1]
output_path = sys.argv[2]
resources_root = os.path.join(project_root, 'entry', 'src', 'main', 'resources')

# 仅对翻译类 element 文件做校验
TRANSLATION_ELEMENT_FILES = {'string.json', 'plural.json', 'strarray.json'}

# Mode locale 豁免（按差异覆盖即可）
MODE_LOCALES = {'dark', 'light', 'horizontal', 'vertical', 'land', 'port'}

def is_language_locale(name: str) -> bool:
    if name in MODE_LOCALES:
        return False
    if '_' in name:
        return True
    if 2 <= len(name) <= 3 and name.isalpha():
        return True
    return False

# Collect locales + key sets
locales = []
key_per_locale = {}
for entry in sorted(os.listdir(resources_root)):
    locale_dir = os.path.join(resources_root, entry)
    elem_dir = os.path.join(locale_dir, 'element')
    if not os.path.isdir(elem_dir):
        continue
    if entry in ('rawfile', 'profile'):
        continue
    locales.append(entry)
    key_per_locale[entry] = set()
    for fname in os.listdir(elem_dir):
        if fname not in TRANSLATION_ELEMENT_FILES:
            continue
        fpath = os.path.join(elem_dir, fname)
        try:
            with open(fpath, encoding='utf-8') as f:
                data = json.load(f)
        except Exception:
            continue
        for items in data.values():
            if not isinstance(items, list):
                continue
            for item in items:
                if isinstance(item, dict) and 'name' in item:
                    key_per_locale[entry].add(item['name'])

# Language vs mode locales
language_locales = [l for l in locales if is_language_locale(l)]
mode_locales = [l for l in locales if l in MODE_LOCALES]

# Key consistency check: base keys must exist in every language locale
findings = []
base_locale = 'base' if 'base' in key_per_locale else (locales[0] if locales else None)
if base_locale:
    base_keys = key_per_locale[base_locale]
    for locale in language_locales:
        if locale == base_locale:
            continue
        missing = base_keys - key_per_locale[locale]
        for k in sorted(missing):
            findings.append({
                "type": "key-missing",
                "locale": locale,
                "key": k,
                "base_locale": base_locale,
                "suggested_action": f"Add key `{k}` to {locale}/element/<file>.json with locale-appropriate value.",
            })

summary = {
    "key_missing": len(findings),
    "FAIL": len(findings),
}

out = {
    "locales": locales,
    "language_locales": language_locales,
    "mode_locales": mode_locales,
    "key_count_per_locale": {l: len(k) for l, k in key_per_locale.items()},
    "summary": summary,
    "findings": findings,
}

if output_path == '/dev/stdout':
    print(json.dumps(out, ensure_ascii=False, indent=2))
else:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"i18n audit complete: {output_path}")
    print(f"  locales={locales}  language={language_locales}  mode={mode_locales}")
    print(f"  FAIL={summary['FAIL']} (key_missing={summary['key_missing']})")

sys.exit(1 if summary["FAIL"] > 0 else 0)
PYEOF
)

python3 -c "$PY_HELPER" "$PROJECT_ROOT" "$OUTPUT_JSON"
