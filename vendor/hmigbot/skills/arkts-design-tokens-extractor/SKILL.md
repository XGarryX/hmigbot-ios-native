---
name: arkts-design-tokens-extractor
description: ArkTS / HarmonyOS 工程的「魔鬼数字」量化与资源化工具。扫描 *.ets 中所有 `.width(<int>) / .height(<int>) / .fontSize(<int>) / .padding/margin({...:<int>}) / .borderRadius(<int>) / '#RRGGBB' / 'rgba(...)' / linearGradient hex` 字面量，按值 × 出现频次聚合，自动建议归并到 `DesignTokens.ets` / `resources/base/element/float.json` / `color.json`，并产出 codemod 补丁把字面量替换为 `$r('app.float.dp_xx')` / `DesignTokens.xx` 引用。当用户说"魔鬼数字"、"硬编码"、"设计系统"、"DesignTokens"、"资源化"、"字面量去重"、"代码里全是数字"、"颜色没归类"时触发。即使用户只说"清一下硬编码"或"扫一下尺寸",也应触发。
metadata:
  type: domain
  domain: engineering
  tags:
  - domain
  - refactor
  - code-quality
  - design-tokens
  - codemod
---
# arkts-design-tokens-extractor

## 1. 定位

ArkTS 工程**代码质量域** skill。回答两个问题：

1. 我的工程里魔鬼数字到底有多严重？
2. 哪些数字应该归并到设计系统？给我可执行的 codemod 补丁。

```
.ets 全量扫描
   ↓
字面量聚合（按值 × 出现次数 × 文件分布）
   ↓
归并候选评分
   ↓
输出 magic-numbers-report.md（量化）
       + DesignTokens.ets 增量补丁（命名 + 落地）
       + float.json / color.json 增量补丁（资源化）
       + codemod patch（一键替换）
```

**为什么需要**：本次 Fitness 迁移踩坑实证（见报告 §问题 5）—— `entry/src/main/ets` 全仓 1095 处硬编码 `.width/.height/.fontSize` + 736 处硬编码 `#RRGGBB` 颜色。`#D0FE37→#FFF965` 渐变在 4 个文件各自字面量。改设计系统时根本 grep 不出语义。

---

## 2. 输入

| 来源 | 用途 |
|---|---|
| `entry/src/main/ets/**/*.ets`（默认；可指定子目录） | 字面量扫描源 |
| `entry/src/main/ets/components/common/DesignTokens.ets`（如有） | 现有 token 命名 / 值映射，避免重复 |
| `entry/src/main/resources/base/element/float.json` / `color.json` | 现有资源，避免重复 |
| `arkts-skills/skills/arkts-design-tokens-extractor/references/naming-conventions.md`（本 skill 自带，待 Phase 4.1 补建） | DesignTokens 命名风格指南 |

可选用户参数：

- `--scope <dir>`：限定扫描范围（默认全 ets/）
- `--threshold <n>`：归并候选频次阈值（默认 3，即同值出现 ≥ 3 次才建议归并）
- `--apply`：直接落地 codemod（默认 dry-run，只产报告）

---

## 3. 输出（4 项产物）

| # | 产物 | 文件路径 | 说明 |
|---|---|---|---|
| ① | `magic-numbers-report.md` | `spec/magic-numbers-report.md` | 所有 `<number>` / `#hex` 字面量按 (值, 文件, 行号) 列表 + 频次排序 |
| ② | 归并候选清单 | 同 ① 文档内独立段 | 频次 ≥ 3 的全部建议（含 Token 命名建议，参考 [`references/naming-conventions.md`](references/naming-conventions.md)） |
| ③ | 资源化增量补丁 | `spec/design-tokens-patch.diff` | DesignTokens.ets + float.json + color.json 增量；dry-run 输出 patch；`--apply` 直接改源码 |
| ④ | codemod patch | `spec/codemod-magic-numbers.diff` | 把字面量替换为 `$r('app.float.dp_xx')` / `$r('app.color.xxx')` / `DesignTokens.xx` 引用；同 ③ 落地策略 |

### 3.1 主报告 `spec/magic-numbers-report.md`

```markdown
# Magic Numbers Report — <project>

- 扫描时间：<ISO date>
- 扫描范围：entry/src/main/ets
- .ets 文件数：242
- 命中行数：1831
  - 数值字面量：1095
  - hex 颜色：736

## 高频数值字面量 Top 30（建议归并）

| 值 | 出现次数 | 主要分布 | 推断语义 | 建议命名 |
|---|---|---|---|---|
| 14 | 87 | `.fontSize / .borderRadius` | 卡片标题字号 / 卡片圆角 | `Typography.bodySmall=14` / `Radius.lg=14`（已有 Token） |
| 12 | 76 | `.padding / .margin / .fontSize` | 卡片内距 / caption 字号 | `Spacing.md=12` / `Typography.caption=12`（已有 Token） |
| 8  | 58 | `.padding / .margin` | 紧凑间距 | `Spacing.sm=8`（已有 Token） |
| 160 | 31 | `.height` | 卡片封面高度 | `Card.coverHeight=160` ← **新增** |
| 200 | 24 | `.width` | 横滑卡宽度 | `Card.scrollerWidth=200` ← **新增** |
| 38  | 18 | VIP 徽标 width | VIP 徽标 width | `Badge.vip.width=38` ← **新增** |
| 20  | 16 | VIP 徽标 height | VIP 徽标 height | `Badge.vip.height=20` ← **新增** |
| 48  | 13 | 圆按钮 width/height | 完成态浮层按钮 | `Button.circle.lg=48` ← **新增** |
| 33  | 11 | dialog padding L/R | 弹窗水平内距 | `Dialog.paddingHorizontal=33` ← **新增** |
| ...

## 高频颜色 Top 20（建议归并）

| 值 | 出现次数 | 推断语义 | 建议命名 |
|---|---|---|---|
| `#D0FE37` | 9 | 品牌亮绿（CTA 起色） | `Colors.brand.lime` ← **新增** |
| `#FFF965` | 7 | 品牌亮黄（CTA 终色） | `Colors.brand.lemon` ← **新增** |
| `#2D2D2D` | 142 | 主文字色 | `Colors.textPrimary`（已有 → 1 次替换 142 处） |
| `#999999` | 88 | 次文字色 | `Colors.textSecondary`（已有） |
| `#F2F2F2` | 23 | 骨架背景色 | `Colors.skeleton`（已有 / 否则新增） |
| `rgba(50, 209, 120, 0.21)` | 4 | 高亮带（target 体重） | `Colors.scaleHighlight=#3632D178`（按 ARGB 推算） |
| ...

## 长尾（频次 < 3，仅记录不强制归并）

合计 481 处长尾字面量，预估 2/3 是真实业务一次性常量，1/3 是潜在归并候选。

## 建议归并矩阵

- ✅ 自动归并（高置信度）：Top 30 + Top 20
- ⚠️ 人工 review（中置信度）：长尾 ≥ 频次 2 但语义不明
- ❌ 不归并（低置信度）：仅出现 1 次的奇数（127 / 19 / 73 等）

## 修复后预期

- DesignTokens 净增 14 项
- float.json 净增 11 项
- color.json 净增 5 项
- 字面量替换：1095 → ~280（剩余为长尾业务常量）
```

### 3.2 DesignTokens / 资源增量补丁

`spec/design-tokens-patch.diff`：

```diff
+++ entry/src/main/ets/components/common/DesignTokens.ets
   ...
+  static readonly Card = {
+    coverHeight: $r('app.float.dp_160'),
+    scrollerWidth: 200,    // 横滑卡，运行时 vp 直接传 number
+  };
+  static readonly Badge = {
+    vip: { width: 38, height: 20 },
+  };
   ...

+++ entry/src/main/resources/base/element/float.json
   ...
+  { "name": "card_cover_height", "value": "160vp" },
+  { "name": "scroller_card_width", "value": "200vp" },
   ...

+++ entry/src/main/resources/base/element/color.json
   ...
+  { "name": "brand_lime",  "value": "#FFD0FE37" },
+  { "name": "brand_lemon", "value": "#FFFFF965" },
   ...
```

### 3.3 codemod 补丁 `spec/codemod-magic-numbers.diff`

把所有 `.width(160)` → `.width($r('app.float.card_cover_height'))`、`#D0FE37` → `$r('app.color.brand_lime')`、`#2D2D2D` → `DesignTokens.Colors.textPrimary` 等。

dry-run 默认只产 diff；`--apply` 真正落地。

---

## 4. 核心算法

### 4.1 字面量识别正则

```regex
# 数值（容器尺寸 / 字号 / 间距 / 圆角）
\.(width|height|fontSize|borderRadius)\(\s*(\d+)\s*\)
\.(padding|margin)\(\{[^}]*\b(top|bottom|left|right|start|end)\s*:\s*(\d+)
\.position\(\{[^}]*\b(top|bottom|left|right)\s*:\s*(\d+)
\.fontSize\(\s*(\d+)\s*\)
\.borderRadius\(\{[^}]*\b(topLeft|topRight|bottomLeft|bottomRight)\s*:\s*(\d+)

# hex 颜色（含 alpha）
#[0-9A-Fa-f]{6}\b
#[0-9A-Fa-f]{8}\b
rgba?\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*(?:,\s*[\d.]+\s*)?\)
linearGradient\([^)]*colors:\s*\[\s*\[\s*['"]#[0-9A-Fa-f]{6,8}['"]
```

### 4.2 排除项

- `.zIndex(<int>)` / `.opacity(<float>)` / `.flexGrow(<int>)` ——非视觉尺寸
- `.duration(<int>) / .delay(<int>)`（动画时长）—— 单独章节统计但不强制归并
- `objectFit(<int>)` / `placement(<int>)` —— 枚举值
- `0` 这种"无效尺寸"（占比过高，频次不计入）
- 被 `if (this.windowModel.isWide())` 包裹的分支值（响应式硬编码，归到 `arkts-responsive-layout-planner` 范畴）

### 4.3 命名推断

按字面量出现的上下文（`.fontSize` / `.width` 容器 / `.padding` 等）分类，再套现成命名词典：

```
fontSize 12 → caption
fontSize 14 → bodySmall
fontSize 16 → body
fontSize 18 → title3
fontSize 20 → title2
fontSize 24 → title1

width 160 + 在 Image / 卡片 height 上下文 → Card.coverHeight
height 39 + 在 Row / Button 上下文 → Button.height.md
borderRadius 50 + 在 Button 上下文 → Button.radius.pill
```

颜色按出现频次 + 上下文（`.fontColor` / `.backgroundColor` / `linearGradient`）分类：

- 频次最高的 ≥ 3 个色阶 → `textPrimary / textSecondary / textTertiary`
- 含 `D0FE37` / `FFF965` / `FF852A` 等品牌色 → `brand.lime / lemon / orange`
- 半透明（含 alpha）→ `overlay.<透明度>`

---

## 5. 与 pipeline 的集成

### 5.1 双调用模式（核心）

本 skill 支持两种调用模式：

| 模式 | 触发方 | 输入 | 输出 |
|---|---|---|---|
| **轻量扫描**（`--scope <file>`） | `a2h-execute` Stage 1 每页生成后（`a2h-activity-converter` agent 内部固定挂钩）| 单页 ets 文件 | 仅本页字面量增量，**追加**到 `spec/magic-numbers-report.md`（不覆盖、不阻断）|
| **全量 audit**（默认） | `a2h-verify` Phase 7 CHECK-MAGIC + 用户主动触发 | `entry/src/main/ets/**/*.ets` 全量 | 完整 4 项产物（见 §3）|

> ⚠️ **a2h 管线豁免（2026-08-25）**：在 a2h-spec/plan/execute 主管线的工程上，本 skill 的 converter 内部挂钩**停用**——主题层已由 resolve_theme.py → theme_brief.py → theme_gate.py 机械链承载，且本 skill 的 `DesignTokens.ets` 归并产物与主管线「一律 `$r` 资源引用」纪律互斥（会被 theme_gate 判 UNBOUND）。管线工程上仅允许用户显式调用，且 `--apply` 只走 `float.json` / `color.json` 路线、不建 `DesignTokens.ets`。

### 5.2 触发时机

| 时机 | 模式 |
|---|---|
| `a2h-execute` Stage 1 每页 `a2h-activity-converter` agent 完成后 | **轻量扫描**（`--scope <该页> --threshold 3`） |
| `a2h-verify` 阶段 CHECK-MAGIC | **全量 audit**（结果计入 verify 通过条件） |
| 用户说「清下硬编码」 / 「扫一下尺寸」 | 全量 audit + dry-run |
| 用户说「跑 codemod」 / 「应用补丁」 | 全量 audit + `--apply` |

### 5.3 a2h-verify CHECK-MAGIC 阈值

```text
警告条件：每 100 行 .ets 中数值字面量 > 8
失败条件：每 100 行 .ets 中数值字面量 > 15  或  hex 字面量 > 5
```

---

## 6. 边界

**做**：

- 字面量统计、归并候选打分、Token 命名建议、codemod patch 生成

**不做**：

- 不直接修改源码（默认 dry-run；`--apply` 才真改）
- 不发明新的设计系统（沿用 DesignTokens 现有命名风格）
- 不处理响应式布局相关的硬编码（归 `arkts-responsive-layout-planner`）
- 不处理 Resource 已有但被字面量替代的"误用"——这是 `arkts-codebase-debug` 的事

---

## 7. Failure Modes

| 现象 | 处理 |
|---|---|
| `DesignTokens.ets` 不存在 | 自动初始化骨架 |
| `float.json / color.json` 不存在 | 自动从 `resources/base/element/` 创建空 |
| 字面量在模板字符串里（如 `'rgba(50, 209, ${alpha})'`） | 跳过（不可静态归并） |
| 字面量在注释里（已有大量 `// padding 12 / 16` 注释） | 排除（注释里讲解，不是真值） |
| `--apply` 后编译失败 | 输出可恢复 patch（保留原文件 .bak） |

---

## 8. 复用价值

不仅本次迁移用，长期维护项目每月运行一次本 skill做技术债稽核。


---

## See Also

- [arkts-codebase-modifier](../arkts-codebase-modifier/SKILL.md) — 给修改方案不动代码（本 skill 直接出 codemod 落地）
