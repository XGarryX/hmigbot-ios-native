#!/usr/bin/env bash
# run_full_pipeline.sh — toolkit-fact-indexer 的"一键链路"入口
#
# 链路：
#   Stage A: harmony-migration-toolkit/pipeline.py 跑出 intermediate/* + agent_bundle.v1.json
#   Stage B: toolkit_to_fact_tree_draft.py 把 toolkit 产物加工成 spec/toolkit-fact-tree.json
#
# v2 切换（2026-07-06，两步完成）：
#   - vendored 的 scripts/harmony-migration-toolkit 已整体替换为 behaviour-modified
#     新版（tree-sitter AST / behavior_chains / fragments / 容器边 / extra_roots 枚举）；
#     旧版留档在 scripts/harmony-migration-toolkit.old-v1.bak-20260706。
#     环境变量 HARMONY_TOOLKIT_DIR 可覆盖 toolkit 路径（如指向开发者迭代中的工作副本）。
#   - Stage B 的 toolkit_to_fact_tree_draft.py 已是 v2 适配版（新版 spec schema v2.2
#     归一化 + behavior_chains 锚点回填 + 猜测布局名防御；旧格式产物直通兼容）；
#     仅适配旧格式的 v1 备份在 toolkit_to_fact_tree_draft.py.bak-20260706。
#   - 新版 toolkit 硬依赖 tree-sitter + tree_sitter_language_pack（缺失时 Fragment/AST
#     检测会**静默**塌方到比旧版还差），故 Stage A 前强制预检，缺则自动 pip 安装，
#     装不上直接 exit 2，绝不带病运行。
#
# 设计目标：用户只给 --android-root 一个参数就能从零跑出 fact-tree，
# 不再要求用户先单独跑 toolkit。intermediate/ 已存在则自动跳过 Stage A。
#
# 用法:
#   bash run_full_pipeline.sh \
#       --android-root /path/to/android/project \
#       [--toolkit-out  .]                          # 默认当前目录
#       [--project-root .]                          # spec/ 落盘根目录，默认当前目录
#       [--force-toolkit]                           # 即使 intermediate/ 存在也强制重跑 Stage A
#
# 退出码:
#   0  完整链路成功，spec/toolkit-fact-tree.json 已就位
#   2  python/pip 环境问题（提示用户介入）
#   3  Stage A 失败
#   4  Stage B 失败

set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SKILLS_ROOT="$(cd "$SKILL_DIR/.." && pwd)"  # 安装根目录（用户级=~/.agents/skills；项目级=<project>/.agents/skills 或 <project>/skills）

# ─── Toolkit 目录解析（env 覆盖 > vendored 默认位；默认位已是 behaviour-modified 新版）───
if [[ -n "${HARMONY_TOOLKIT_DIR:-}" && -d "${HARMONY_TOOLKIT_DIR}" ]]; then
  TOOLKIT_DIR="$HARMONY_TOOLKIT_DIR"
else
  TOOLKIT_DIR="$SCRIPT_DIR/harmony-migration-toolkit"
fi
# 新版 toolkit 硬依赖 tree-sitter，统一做预检（对任何 toolkit 版本都无害）
TOOLKIT_IS_MODIFIED=1

ANDROID_ROOT=""
TOOLKIT_OUT=""
PROJECT_ROOT=""
FORCE_TOOLKIT=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --android-root) ANDROID_ROOT="$2"; shift 2 ;;
    --toolkit-out) TOOLKIT_OUT="$2"; shift 2 ;;
    --project-root) PROJECT_ROOT="$2"; shift 2 ;;
    --force-toolkit) FORCE_TOOLKIT=1; shift ;;
    *) echo "❌ unknown arg: $1" >&2; exit 2 ;;
  esac
done

if [[ -z "$ANDROID_ROOT" ]]; then
  echo "❌ --android-root required" >&2
  echo "Usage: $0 --android-root <PATH> [--toolkit-out DIR] [--project-root DIR] [--force-toolkit]" >&2
  exit 2
fi
if [[ ! -d "$ANDROID_ROOT" ]]; then
  echo "❌ android-root not found: $ANDROID_ROOT" >&2
  exit 2
fi
# 绝对化（必须！）：Stage A 会 pushd 进 TOOLKIT_DIR 再跑 pipeline.py，相对路径会就地解析成
# toolkit 自己的目录 → toolkit 分析自己 → 树塌方成 2/1/0（2026-07-06 AIPPT 实测事故）。
ANDROID_ROOT="$(cd "$ANDROID_ROOT" && pwd)"

# 默认: toolkit_out 和 project_root 都是当前目录
TOOLKIT_OUT="${TOOLKIT_OUT:-$(pwd)}"
PROJECT_ROOT="${PROJECT_ROOT:-$(pwd)}"
TOOLKIT_OUT="$(cd "$TOOLKIT_OUT" 2>/dev/null && pwd || echo "$TOOLKIT_OUT")"
PROJECT_ROOT="$(cd "$PROJECT_ROOT" 2>/dev/null && pwd || echo "$PROJECT_ROOT")"

echo "═══ toolkit-fact-indexer 一键链路 ═══"
echo "  android-root : $ANDROID_ROOT"
echo "  toolkit-out  : $TOOLKIT_OUT"
echo "  project-root : $PROJECT_ROOT"
echo "  toolkit-dir  : $TOOLKIT_DIR"
echo ""

# ─── Stage A: harmony-migration-toolkit pipeline ───
if [[ ! -d "$TOOLKIT_DIR" ]]; then
  echo "❌ harmony-migration-toolkit 不在 $TOOLKIT_DIR" >&2
  echo "   skill 内嵌路径错位，检查 $SKILLS_ROOT/toolkit-fact-indexer/scripts/" >&2
  exit 3
fi

NEED_STAGE_A=1
if [[ $FORCE_TOOLKIT -eq 0 && -d "$TOOLKIT_OUT/intermediate" && -f "$TOOLKIT_OUT/agent_bundle.v1.json" ]]; then
  NEED_STAGE_A=0
  echo "── Stage A: skip（intermediate/ + agent_bundle.v1.json 都已存在；--force-toolkit 可强制重跑）──"
fi

if [[ $NEED_STAGE_A -eq 1 ]]; then
  # 探测 / 装依赖（幂等）
  if ! python3 -c 'import jsonschema, yaml' 2>/dev/null; then
    echo "── 装 toolkit Python 依赖（jsonschema / PyYAML）──"
    if ! pip install -q -r "$TOOLKIT_DIR/requirements.txt" 2>&1 | tail -5; then
      # 尝试 --user 兜底（macOS PEP 668）
      pip install -q --user -r "$TOOLKIT_DIR/requirements.txt" 2>&1 | tail -5 || {
        echo "❌ pip install 失败，请人工跑：" >&2
        echo "   pip install -r $TOOLKIT_DIR/requirements.txt" >&2
        exit 2
      }
    fi
    # 二次确认
    if ! python3 -c 'import jsonschema, yaml' 2>/dev/null; then
      echo "❌ 装完依赖仍 import 失败；可能装到错误 python 环境，检查 PYTHONPATH / venv" >&2
      exit 2
    fi
  fi

  # ── tree-sitter 前置硬检查（仅新版 toolkit；缺则自动装，装不上硬失败）──
  # 新版 ast_index.py 实际 import 的是 tree_sitter_language_pack（toolkit 自带的
  # requirements.txt 漏列了它）。缺失时 toolkit 不报错、静默退化到纯正则：
  # AIPPT 实测 Fragment 挂载 88→20、声明检测 39→0、导航节点 64→40（比旧版还少）。
  # 宁可 fail 也不产出带病事实。
  if [[ $TOOLKIT_IS_MODIFIED -eq 1 ]]; then
    if ! python3 -c 'import tree_sitter, tree_sitter_language_pack' 2>/dev/null; then
      echo "── tree-sitter 缺失，自动安装（tree-sitter + tree_sitter_language_pack）──"
      if ! pip install -q tree-sitter tree_sitter_language_pack 2>&1 | tail -3; then
        pip install -q --user tree-sitter tree_sitter_language_pack 2>&1 | tail -3 || true
      fi
      if ! python3 -c 'import tree_sitter, tree_sitter_language_pack' 2>/dev/null; then
        echo "❌ tree-sitter 安装失败。新版 toolkit 缺它会静默产出残缺事实，拒绝继续。" >&2
        echo "   请人工执行: python3 -m pip install --user tree-sitter tree_sitter_language_pack" >&2
        echo "   （或临时退回旧版: 移走 $SCRIPT_DIR/harmony-migration-toolkit-behaviour-modified）" >&2
        exit 2
      fi
    fi
    echo "✓ tree-sitter 预检通过 ($(python3 -c 'import tree_sitter; print(getattr(tree_sitter, "__version__", "?"))' 2>/dev/null))"
  fi

  echo "── Stage A: 跑 harmony-migration-toolkit pipeline ──"
  pushd "$TOOLKIT_DIR" >/dev/null
  python3 pipeline.py --android-root "$ANDROID_ROOT" --out "$TOOLKIT_OUT" 2>&1 | tail -10
  rc=${PIPESTATUS[0]}
  popd >/dev/null
  if [[ $rc -ne 0 ]]; then
    echo "❌ Stage A 失败 (rc=$rc)" >&2
    exit 3
  fi
  if [[ ! -d "$TOOLKIT_OUT/intermediate" ]]; then
    echo "❌ Stage A 跑完但 $TOOLKIT_OUT/intermediate/ 没出来" >&2
    exit 3
  fi
  echo "✓ Stage A 完成"
fi
echo ""

# ─── Stage B: toolkit_to_fact_tree_draft ───
echo "── Stage B: toolkit-fact-tree 生成 ──"
CACHE_DIR="$PROJECT_ROOT/spec/.cache/fact-tree"
mkdir -p "$CACHE_DIR"
python3 "$SCRIPT_DIR/toolkit_to_fact_tree_draft.py" \
  --toolkit-out "$TOOLKIT_OUT" \
  --android-root "$ANDROID_ROOT" \
  --out "$CACHE_DIR" 2>&1 | tail -5
rc=${PIPESTATUS[0]}
if [[ $rc -ne 0 ]]; then
  echo "❌ Stage B 失败 (rc=$rc)" >&2
  exit 4
fi

# 把 draft 复制成最终 spec/toolkit-fact-tree.json
DRAFT="$CACHE_DIR/draft.json"
FINAL="$PROJECT_ROOT/spec/toolkit-fact-tree.json"
if [[ ! -f "$DRAFT" ]]; then
  echo "❌ Stage B 跑完但 $DRAFT 没出来" >&2
  exit 4
fi
mkdir -p "$(dirname "$FINAL")"

# v1.2: 防覆盖 — 如果现有 fact-tree 含 LLM 数据（purpose 已填），重命名备份再写新版
if [[ -f "$FINAL" ]]; then
  EXISTING_PURPOSE_COUNT=$(python3 -c "
import json
try:
    d = json.load(open('$FINAL'))
    print(sum(1 for r in (d.get('pages',[])+d.get('fragments',[])+d.get('dialogs',[])) if r.get('purpose')))
except Exception:
    print(0)
" 2>/dev/null || echo 0)
  if [[ "$EXISTING_PURPOSE_COUNT" -gt 0 ]]; then
    BACKUP="${FINAL}.before-pipeline.$(date +%s).json"
    cp "$FINAL" "$BACKUP"
    echo "⚠️  现有 fact-tree 含 $EXISTING_PURPOSE_COUNT 条 LLM purpose 数据"
    echo "    → 已备份到 $BACKUP"
    echo "    新 fact-tree 仅含结构事实，LLM 数据需重新跑 app-relationship-tree skill"
  fi
fi

cp "$DRAFT" "$FINAL"
echo "✓ Stage B 完成 → $FINAL"

# ─── 手势覆盖对账 + 反哺（warn-only, 不阻塞; grep 级耗时 <5s）───
# Pass A 重算组件 triggers(含 widget 类名手势) / B1 挂 gesture_hints / B2 仅警告
echo ""
echo "── 手势覆盖对账(audit_gesture_coverage) ──"
python3 "$SCRIPT_DIR/audit_gesture_coverage.py" "$FINAL" --source "$ANDROID_ROOT" || \
  echo "⚠ gesture audit 异常(不阻塞链路), 可手动重跑: audit_gesture_coverage.py $FINAL --source $ANDROID_ROOT"

# ─── H5/WebView 页面标注（capture_mode=web, 确定性 grep; 漏标会让 H5 页被整图 diff 产假 finding）───
echo ""
echo "── capture_mode 标注(annotate_capture_mode) ──"
python3 "$SCRIPT_DIR/annotate_capture_mode.py" "$FINAL" --source "$ANDROID_ROOT" || \
  echo "⚠ capture_mode 标注异常(不阻塞链路), 可手动重跑: annotate_capture_mode.py $FINAL --source $ANDROID_ROOT"

# ─── 摘要 ───
echo ""
echo "═══ 链路完成 ═══"
PAGES=$(python3 -c "import json,sys; d=json.load(open('$FINAL')); print(len(d.get('pages',[])))")
FRAGMENTS=$(python3 -c "import json,sys; d=json.load(open('$FINAL')); print(len(d.get('fragments',[])))")
DIALOGS=$(python3 -c "import json,sys; d=json.load(open('$FINAL')); print(len(d.get('dialogs',[])))")
echo "  pages=$PAGES fragments=$FRAGMENTS dialogs=$DIALOGS"

# ─── 产出合理性绊线（宁可 fail 也不静默交付带病树）───
# 症状库: 2026-07-06 相对路径事故产出 2/1/0 的"合法"小树, 链路照报完成。
# 规则: ①总节点数 < 8 的树对任何真实 app 都可疑 → 硬失败
#       ②有塌方备份对照时, 新树总节点 < 旧树 30% → 硬失败(结构性缩水须人工确认)
TOTAL=$((PAGES + FRAGMENTS + DIALOGS))
if [[ $TOTAL -lt 8 ]]; then
  echo "❌ 产出绊线: 全树仅 $TOTAL 个节点, 对真实 app 不可信(疑似 android-root 错位/源码不可读)。" >&2
  echo "   检查上方 Stage A 的 android_root 是否指向真实工程; 备份见 spec/ 下 .before-pipeline.*" >&2
  exit 4
fi
PREV_BACKUP=$(ls -t "$PROJECT_ROOT"/spec/toolkit-fact-tree.json.before-pipeline.*.json 2>/dev/null | head -1)
if [[ -n "$PREV_BACKUP" ]]; then
  PREV_TOTAL=$(python3 -c "
import json
d=json.load(open('$PREV_BACKUP'))
print(len(d.get('pages',[]))+len(d.get('fragments',[]))+len(d.get('dialogs',[])))" 2>/dev/null || echo 0)
  if [[ "$PREV_TOTAL" -gt 0 && $TOTAL -lt $((PREV_TOTAL * 30 / 100)) ]]; then
    echo "❌ 产出绊线: 新树 $TOTAL 节点 < 上一版($PREV_TOTAL)的 30%, 结构性塌方须人工确认。" >&2
    echo "   若确属 app 大改版, 删除旧备份后重跑即可放行。" >&2
    exit 4
  fi
fi
echo "  toolkit-fact-tree.json: $FINAL"
echo ""
echo "下一步：跑 app-relationship-tree skill 补 purpose / contracts / preconditions"
exit 0
