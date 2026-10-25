#!/usr/bin/env bash
# preflight_check.sh — 检查 fact-tree 是否完成所有 LLM phase
#
# 每个 LLM phase 的完成判定:
#   Phase 2   补 purpose:            所有 record.purpose != null
#   Phase 2.5 补 inbound_triggers:   有 inbound 的 record 必有 inbound_triggers
#   Phase 2.6 补 navigation_contract: 所有 Fragment/Dialog/Activity 都有 contract，
#                                     且 contract_uncertain==false（除 host_default）
#   Phase 2.7 补 preconditions:      有 preconditions 字段的 record，其 source 不能全是 toolkit
#
# 用法:
#   preflight_check.sh [path/to/toolkit-fact-tree.json]
#
# 退出码:
#   0  所有 LLM phase 完成（可进入下游）
#   1  存在未完成 LLM phase（打印明确指令）
#   2  fact-tree 不存在 / 损坏

set -eo pipefail

SKILLS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"  # <SKILLS_ROOT>/<skill>/scripts → SKILLS_ROOT
TREE="${1:-spec/toolkit-fact-tree.json}"

if [[ ! -f "$TREE" ]]; then
  echo "❌ fact-tree not found: $TREE" >&2
  echo "   先跑 toolkit-fact-indexer:" >&2
  echo "   python3 $SKILLS_ROOT/toolkit-fact-indexer/scripts/toolkit_to_fact_tree_draft.py \\" >&2
  echo "       --toolkit-out . --android-root <ANDROID_ROOT> --out spec/.cache/fact-tree" >&2
  exit 2
fi

if ! jq empty "$TREE" >/dev/null 2>&1; then
  echo "❌ fact-tree 损坏: $TREE" >&2
  exit 2
fi

INCOMPLETE=0
MESSAGES=()

# Phase 2: purpose 完整度
purpose_null=$(jq '[(.pages[],.fragments[],.dialogs[]) | select(.purpose==null)] | length' "$TREE")
purpose_total=$(jq '[(.pages[],.fragments[],.dialogs[])] | length' "$TREE")
if [[ "$purpose_null" -gt 0 ]]; then
  MESSAGES+=("📌 Phase 2 (LLM 补 purpose): $purpose_null / $purpose_total record purpose=null")
  MESSAGES+=("   派 sub-agent: 跑 app-relationship-tree Phase 2 LLM 补 purpose")
  INCOMPLETE=$((INCOMPLETE+1))
fi

# Phase 2.5: inbound_triggers —— 对齐 SKILL Phase 5 HARD 契约：**每条 record 都必须有"有效"inbound_triggers（≥1）**
# 旧口径只查"有 toolkit inbound 边但缺 label"，隐含假设 toolkit 必给边骨架。字符串路由框架
# （ARouter/TheRouter/WMRouter）项目 toolkit 追不到边 → navigation.inbound 全空 → 孤儿 record
# 对旧闸完全不可见（Fitness 实测 131/137 孤儿只报 22 欠账，下游 67 页被误判 structurally_unreachable）。
# v2 口径（2026-07-13，堵"纸面边"空子）：**有效边 = trigger_label 是真实可点文案**——
#   非空、非 *unknown*、非方法名/代码锚点形态（含 . / ( 的纯标识符串，如 "initView/onClick"）。
#   无效边照样凑得出 reach_path≥3 的纸面链，chain_walk 到那跳必匹配不到 → 不许计入分子。
#   确实查无入口的 LLM 应填 trigger_label_unknown + notes（诚实），该 record 计入欠账但不算违规。
trigger_missing=$(jq '
  def actionable: ((.trigger_label // "") != "")
    and ((.trigger_label | test("unknown"; "i")) | not)
    and ((.trigger_label | test("^[A-Za-z_$][A-Za-z0-9_$]*([./(][A-Za-z0-9_$/.()]*)+$")) | not);
  [(.pages[],.fragments[],.dialogs[]) | select([(.inbound_triggers // [])[] | select(actionable)] | length == 0)] | length' "$TREE")
orphan_missing=$(jq '[(.pages[],.fragments[],.dialogs[]) | select((.navigation.inbound|length)==0 and (.inbound_triggers==null or .inbound_triggers==[]))] | length' "$TREE")
if [[ "$trigger_missing" -gt 0 ]]; then
  MESSAGES+=("📌 Phase 2.5 (LLM 补 inbound_triggers): $trigger_missing record 缺**有效**inbound_triggers（label 须为真实可点文案；其中 $orphan_missing 个连 toolkit inbound 边也没有——若占比高，App 很可能用 ARouter/TheRouter 等字符串路由，toolkit 追不到边，必须靠本 phase 读源码反查：@Route 注解建路由表 → 解常量拼接 → 找 build() 调用点连边 → 从调用点 onClick/layout 抽真实按钮文案）")
  MESSAGES+=("   派 sub-agent: 跑 app-relationship-tree Phase 2.5 LLM 读源码反查 onClick 按钮文案")
  INCOMPLETE=$((INCOMPLETE+1))
fi

# Phase 2.3: reach_path 链契约 —— 焊死 SKILL Phase 5 HARD 契约"非 launcher 至少 3 元素(root+token+self)"
# （2026-07-13：此契约原只存在于 SKILL 散文，无脚本执行 → Fitness 97/137 单节点纸面链静默过闸，
#   烧掉一轮设备时间后才暴露。单节点 = 无"根→目标"链 = 下游 chain_walk 必卡 + 鸿蒙侧无链可镜像。）
# ⚠️ 编排顺序坑：run_all_phases 里 2.3 跑在 2.5 之前——2.5 补完有效边后**必须重跑 compute_reach_paths.py**，
#   否则新边不入链。本闸红时若 2.5 已完成，多半就是漏了重跑 2.3。
launcher_id=$(jq -r '.app.launcher_short // ""' "$TREE")
chain_missing=$(jq --arg L "$launcher_id" '
  [(.pages[],.fragments[],.dialogs[]) | select(.id != $L and ((.reach_path // []) | length) < 3)] | length' "$TREE")
if [[ "$chain_missing" -gt 0 ]]; then
  MESSAGES+=("📌 Phase 2.3 (reach 链合成): $chain_missing record reach_path<3（单节点=纸面链，无根→目标可走链）")
  MESSAGES+=("   修法: 先补 Phase 2.5 有效边 → 再重跑 python3 \$SKILLS_ROOT/app-relationship-tree/scripts/compute_reach_paths.py <tree>")
  INCOMPLETE=$((INCOMPLETE+1))
fi

# Phase 2.6: navigation_contract.contract_uncertain
contract_uncertain=$(jq '[(.pages[],.fragments[],.dialogs[]) | select(.navigation_contract.contract_uncertain==true)] | length' "$TREE")
contract_total=$(jq '[(.pages[],.fragments[],.dialogs[]) | select(.navigation_contract!=null)] | length' "$TREE")
if [[ "$contract_uncertain" -gt 0 ]]; then
  MESSAGES+=("📌 Phase 2.6 (LLM 补 navigation_contract.label): $contract_uncertain / $contract_total contract_uncertain=true")
  MESSAGES+=("   派 sub-agent: 跑 app-relationship-tree Phase 2.6 LLM 补 contract.label + verify_signal")
  MESSAGES+=("   清单: spec/visual-verify/contracts_uncertain.md")
  INCOMPLETE=$((INCOMPLETE+1))
fi

# Phase 2.7: preconditions LLM 扩充（toolkit enhancer 已抽的 5 类基础不算 LLM）
# 检查是否有 record 的 preconditions 含 source: app_relationship_tree:* 前缀
llm_preconditions=$(jq '[(.pages[],.fragments[],.dialogs[]) | select(.preconditions!=null) | .preconditions[] | select(.source | startswith("app_relationship_tree:"))] | length' "$TREE")
toolkit_preconditions=$(jq '[(.pages[],.fragments[],.dialogs[]) | select(.preconditions!=null) | .preconditions[] | select(.source=="preconditions_enhancer")] | length' "$TREE")
if [[ "$toolkit_preconditions" -gt 0 && "$llm_preconditions" -eq 0 ]]; then
  MESSAGES+=("📌 Phase 2.7 (LLM 扩 preconditions): 仅有 $toolkit_preconditions 条 toolkit 抽的基础，0 条 LLM 扩充")
  MESSAGES+=("   派 sub-agent: 跑 app-relationship-tree Phase 2.7 LLM 从 page_*.md 扩 preconditions")
  INCOMPLETE=$((INCOMPLETE+1))
fi

# 输出
if [[ "$INCOMPLETE" -eq 0 ]]; then
  echo "✅ preflight OK: 所有 LLM phase 完成 (purpose / inbound_triggers / contract / preconditions)"
  exit 0
fi

echo "❌ fact-tree 未完成 $INCOMPLETE 个 LLM phase："
echo ""
for msg in "${MESSAGES[@]}"; do
  echo "$msg"
done
echo ""
echo "怎么补："
echo "  方法 A: 在对话里说 \"跑 app-relationship-tree 完整流程\" / \"补全 fact-tree LLM phase\""
echo "  方法 B: 跑 orchestrator: bash $SKILLS_ROOT/app-relationship-tree/scripts/run_all_phases.sh"
echo "  方法 C: 单 phase 派: 在对话里说 \"跑 Phase 2.6 LLM 补 contract\"（或其它 phase）"
echo ""
echo "补完后再跑下游（visual-verify 等）。"
exit 1
