#!/usr/bin/env bash
# run_all_phases.sh — app-relationship-tree 完整 5 phase 编排
#
# 串行跑所有 phase；脚本能跑的直接跑，LLM phase 用 preflight 检测后打印明确指令
# 让用户在对话里派 sub-agent。
#
# 用法:
#   run_all_phases.sh --android-root <ANDROID_ROOT>
#     [--tree spec/toolkit-fact-tree.json]
#     [--page-md-dir spec/baseline/ui]
#     [--skip-llm-check]   仅跑确定性 phase，不强制 LLM phase 完成（debug 用）
#
# 退出码:
#   0  全部完成（含 LLM phase 都已补全）
#   1  确定性 phase 跑通，但 LLM phase 待人工派 sub-agent
#   2  脚本失败 / 输入缺失

set -eo pipefail

TREE="spec/toolkit-fact-tree.json"
ANDROID_ROOT=""
PAGE_MD_DIR="spec/baseline/ui"
SKIP_LLM_CHECK=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --android-root) ANDROID_ROOT="$2"; shift 2 ;;
    --tree) TREE="$2"; shift 2 ;;
    --page-md-dir) PAGE_MD_DIR="$2"; shift 2 ;;
    --skip-llm-check) SKIP_LLM_CHECK=1; shift ;;
    *) echo "unknown: $1" >&2; exit 2 ;;
  esac
done

if [[ -z "$ANDROID_ROOT" ]]; then
  echo "❌ --android-root required" >&2
  exit 2
fi
if [[ ! -d "$ANDROID_ROOT" ]]; then
  echo "❌ android-root not found: $ANDROID_ROOT" >&2
  exit 2
fi
if [[ ! -f "$TREE" ]]; then
  echo "❌ tree not found: $TREE  — 先跑 toolkit-fact-indexer" >&2
  exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "═══ app-relationship-tree 完整流程 ═══"
echo "tree: $TREE"
echo "android-root: $ANDROID_ROOT"
echo "page-md-dir: $PAGE_MD_DIR"
echo ""

# Phase 1.5: 节点校准（脚本）
echo "── Phase 1.5: 节点级校准 ──"
python3 "$SCRIPT_DIR/calibrate_nodes.py" "$TREE" \
  --android-root "$ANDROID_ROOT" --page-md-dir "$PAGE_MD_DIR"
echo ""

# Phase 1.6: 源码 popup 类正向扫描（v6.5 新增）
# 补 Phase 1.5 "page_*.md 反查" 的鸡生蛋盲区：a2h-spec 还没写 page_*.md 时
# 直接从源码扫 *Dialog/*Popup/*Window/*Sheet 类（+继承链白名单 + 命名兜底），
# 把 toolkit 漏识、page_*.md 也没写的 popup 一次性补进 fact-tree.dialogs[]。
echo "── Phase 1.6: 源码 popup 类正向扫描 ──"
python3 "$SCRIPT_DIR/scan_popup_classes.py" "$TREE" \
  --android-root "$ANDROID_ROOT"
echo ""

# Phase 2.3: 多源 BFS reach_path（脚本）
echo "── Phase 2.3: 多源 BFS reach_path ──"
python3 "$SCRIPT_DIR/compute_reach_paths.py" "$TREE"
echo ""

# Phase 2.6: navigation_contract 启发式骨架（脚本）
# LLM 补全部分由 preflight 检测后让用户派 sub-agent
echo "── Phase 2.6: navigation_contract 启发式骨架 ──"
python3 "$SCRIPT_DIR/compute_navigation_contract.py" "$TREE" \
  --android-root "$ANDROID_ROOT" --page-md-dir "$PAGE_MD_DIR"
echo ""

# 跑完确定性 phase，开始 preflight 看 LLM phase 状态
if [[ "$SKIP_LLM_CHECK" -eq 1 ]]; then
  echo "⏭️  --skip-llm-check 已设，不检查 LLM phase 完成度"
  exit 0
fi

echo "── preflight: LLM phase 完成度检查 ──"
if bash "$SCRIPT_DIR/preflight_check.sh" "$TREE"; then
  echo ""
  echo "✅ app-relationship-tree 完整流程已完成"
  exit 0
else
  echo ""
  echo "⚠️  确定性 phase 已跑完，LLM phase 待人工派 sub-agent（见上方提示）"
  exit 1
fi
