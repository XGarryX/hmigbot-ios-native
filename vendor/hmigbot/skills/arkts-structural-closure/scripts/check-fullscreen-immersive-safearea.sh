#!/bin/bash
# check-fullscreen-immersive-safearea.sh
# 全工程沉浸式 + 安全区四层架构兜底扫描（按【页面类型】判定，非 @Entry 字面串）。
#
# 设计思路：
#   即便 a2h-spec 阶段 page_type 自动判定、a2h-plan 阶段 skill 自动绑、a2h-execute
#   阶段 converter 默认契约都通过，仍可能因 converter 偷懒（如硬编码代替系统查询）
#   导致代码层四件套缺失。本脚本作为最终兜底。
#
# ⚠️ v2 修订（修两个致命缺陷，见 arkts-immersive-safearea/SKILL.md「核心不变量 + 验证」）：
#   缺陷 A（误报）：旧版 `grep -q "@Entry"` 抓的是【字面串】，子组件/页头注释里
#     "非 @Entry""@Entry Navigation 根" 等都会命中 → 子组件被当入口页、被要求四件套 → 假阳性。
#   缺陷 B（漏检）：旧版【只验 @Entry 页】。但 Navigation + pageMap 架构下，全工程通常
#     只有 1 个 @Entry（入口页），其余 N 个全屏页都是 NavDestination（非 @Entry）→ 这 N 个
#     真实全屏页的四件套从未被闸住，check 实际只验了入口页就 PASS。
#
#   v2 改为按【页面类型】判定（page_type 的权威源是 meta.json，本脚本用 .ets 结构等价判定）：
#     - full_screen_page = 真 `^@Entry` 装饰器  OR  build() 根是 `NavDestination(` → 必须有 Layer 3
#     - sub_component / overlay（@ComponentV2 且非上述）→ 宿主负责安全区 → 豁免，且抽查"不应自带 expandSafeArea"
#   覆盖率：入口页 + 全部 NavDestination 全屏路由页（含 GuideActivity 等子页）。
#
# 用法：
#   bash .agents/skills/arkts-structural-closure/scripts/check-fullscreen-immersive-safearea.sh
#
# 退出码：
#   0 = PASS（所有全屏页含 Layer 3 + EntryAbility 含 Layer 1 + 全工程 ≥1 处 Layer 2）
#   1 = FAIL（任一全屏页缺 Layer 3 / EntryAbility 缺 Layer 1 / 无 Layer 2）
#   2 = 用法错误 / entry/ 目录不存在
#
# 集成：
#   - a2h-execute SKILL.md §6 Final Structural Closure 的 H 维度调用本脚本
#   - 可单独运行作为开发时本地 lint / CI 检查

set -e

ETS_ROOT="${ETS_ROOT:-entry/src/main/ets}"
ENTRY_ABILITY="$ETS_ROOT/entryability/EntryAbility.ets"

if [ ! -d "$ETS_ROOT" ]; then
  echo "❌ $ETS_ROOT 不存在" >&2
  echo "用法: bash .agents/skills/arkts-structural-closure/scripts/check-fullscreen-immersive-safearea.sh" >&2
  exit 2
fi

FAIL=0
FS_TOTAL=0       # 全屏页总数（@Entry + NavDestination）
FS_PASS=0        # 含 Layer 3 的全屏页
SUB_EXEMPT=0     # 豁免的子组件 / overlay 数
SUB_WARN=0       # 子组件却自带 expandSafeArea（双重 inset 风险）

# Layer 3 合规关键字（任一即视为做了前景避让 / 复用了脚手架）
L3_RE='(expandSafeArea|windowModel|windowTopPadding|windowBottomPadding|ImmersiveScaffold|ImmersivePage)'

echo "🔍 按 arkts-immersive-safearea 四层架构扫描（v2：按页面类型判定）..."
echo ""

# ─── Layer 1: EntryAbility 启用 Window 沉浸 ─────────────────────────
if [ -f "$ENTRY_ABILITY" ]; then
  if grep -q "setWindowLayoutFullScreen" "$ENTRY_ABILITY"; then
    echo "✅ L1 [EntryAbility]: 含 setWindowLayoutFullScreen"
  else
    echo "❌ L1 [EntryAbility]: 缺 setWindowLayoutFullScreen"
    echo "   位置: $ENTRY_ABILITY"
    echo "   修复: 见 arkts-immersive-safearea/SKILL.md Layer 1 (onWindowStageCreate 六件套)"
    FAIL=1
  fi
else
  echo "⚠️  EntryAbility.ets 不存在于 $ENTRY_ABILITY，跳过 L1 检查"
fi
echo ""

# ─── Layer 2: 根 Navigation 含 expandSafeArea ───────────────────────
# grep -w（词边界，BSD/GNU 通用），避免 \b（GNU 扩展）在 BSD grep 漏匹配。
EXPAND_HITS=$(grep -rlw "expandSafeArea" "$ETS_ROOT" --include="*.ets" 2>/dev/null | wc -l | tr -d ' ')
if [ "$EXPAND_HITS" -ge 1 ]; then
  echo "✅ L2 [根 Navigation]: 全工程 $EXPAND_HITS 个文件含 expandSafeArea"
else
  echo "❌ L2 [根 Navigation]: 全工程未发现 expandSafeArea"
  echo "   修复: 在入口 page 的根 Navigation 加 .expandSafeArea([SYSTEM, CUTOUT], [START, END, TOP, BOTTOM])"
  echo "   详见 arkts-immersive-safearea/SKILL.md Layer 2"
  FAIL=1
fi
echo ""

# ─── Layer 3: 全屏页前景避让（contract-first，结构兜底）─────────────
# 逐 .ets 判定是否需要 Layer 3，优先级：
#   1) 显式契约（权威，源自 meta.json，converter 写进页头）：
#        needs_immersive_safearea=true  → 需要 Layer 3（哪怕是 overlay，如 SplashPage）
#        needs_immersive_safearea=false → 豁免（哪怕是 NavDestination，如透明跳板 ShortCutPage）
#   2) 无契约行时按结构兜底：`^@Entry` 真装饰器  OR  含 `NavDestination(` → 需要 Layer 3
#   需要 Layer 3 者必须命中 L3_RE；豁免者（含 @ComponentV2/struct 的子组件）只抽查
#   "不应自带 .expandSafeArea(" → WARN（双重 inset 风险）。非 UI 文件（service/model 等）不计。
while IFS= read -r FILE; do
  REL_FILE="${FILE#"$ETS_ROOT"/}"

  # 1) 读显式契约（权威）。true 优先于 false（若同时出现，以"需要"为准，宁严勿漏）。
  NEED_L3=-1
  if grep -qiE 'needs_immersive_safearea[ =:]*true' "$FILE"; then
    NEED_L3=1
  elif grep -qiE 'needs_immersive_safearea[ =:]*false' "$FILE"; then
    NEED_L3=0
  fi

  # 2) 无契约 → 结构兜底
  if [ "$NEED_L3" -eq -1 ]; then
    if grep -qE '^[[:space:]]*@Entry' "$FILE" || grep -q 'NavDestination(' "$FILE"; then
      NEED_L3=1
    else
      NEED_L3=0
    fi
  fi

  if [ "$NEED_L3" -eq 1 ]; then
    FS_TOTAL=$((FS_TOTAL + 1))
    if grep -qE "$L3_RE" "$FILE"; then
      FS_PASS=$((FS_PASS + 1))
      echo "✅ L3 [$REL_FILE]: 全屏页含安全区响应"
    else
      FAIL=1
      echo "❌ L3 [$REL_FILE]: 全屏页未发现任何安全区响应（Layer 3 缺失）"
      echo "   修复: 复用 components/common/ImmersiveScaffold 封装四层，"
      echo "         或前景手动 .padding({ top: windowModel.windowTopPadding, bottom: windowModel.windowBottomPadding })"
      echo "   （若本页确实无前景需避让，在页头标注 needs_immersive_safearea=false 即豁免）"
      echo "   详见 arkts-immersive-safearea/SKILL.md Layer 3 / router-pushed-pages.md"
    fi
  else
    # 豁免：仅统计真正的 UI 子组件（含 @ComponentV2 / struct），非 UI 文件不计
    if grep -qE '@ComponentV2|@Component[^V]|struct ' "$FILE"; then
      SUB_EXEMPT=$((SUB_EXEMPT + 1))
      # 子组件不应【真的调用】.expandSafeArea(（注释里提及不算）→ 双重 inset 风险
      if grep -qE '\.expandSafeArea\(' "$FILE"; then
        SUB_WARN=$((SUB_WARN + 1))
        echo "⚠️  [$REL_FILE]: 豁免页/子组件却调用 .expandSafeArea()（双重 inset 风险，应交宿主全屏页）"
      fi
    fi
  fi
done < <(find "$ETS_ROOT" -name "*.ets" 2>/dev/null)
echo ""

# ─── 汇总 ─────────────────────────────────────────────────────────
echo "----------------------------------------"
echo "扫描结果（v2 按页面类型）："
echo "  - 全屏页（@Entry + NavDestination）: $FS_TOTAL"
echo "  - L3 合规 (PASS): $FS_PASS"
echo "  - L3 缺失 (FAIL): $((FS_TOTAL - FS_PASS))"
echo "  - 子组件/overlay（豁免）: $SUB_EXEMPT"
echo "  - 子组件误带 expandSafeArea (WARN): $SUB_WARN"
echo ""

if [ $FAIL -eq 0 ]; then
  echo "✅ 沉浸式 + 安全区 四层合规校验 PASS"
  echo "📖 详见 arkts-immersive-safearea/SKILL.md 四层架构 + 核心不变量"
  exit 0
else
  echo "❌ 校验 FAIL"
  echo "📖 范式说明: Android 源码无沉浸式概念（系统默认处理），但 HarmonyOS 必须显式实施"
  echo "📖 核心不变量: 背景穿透 ≠ 前景避让；责任分层：入口给 L1/L2，全屏页(含 NavDestination)自扛 L3，子组件不碰"
  echo "📖 修复指引: arkts-immersive-safearea/SKILL.md（单一权威源）"
  exit 1
fi
