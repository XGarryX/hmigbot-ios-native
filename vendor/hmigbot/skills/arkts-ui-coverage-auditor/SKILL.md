---
name: arkts-ui-coverage-auditor
description: Android→ArkTS 迁移 UI 覆盖率审计。三层对账（Android Screen × ArkTS Page × spec/baseline/ui/page_*.md），强制识别 a2h-spec 阶段漏掉的二三层 UI（Fragment / ViewPager 子页 / Step 子页 / Dialog 内嵌页 / Activity 内含 Component）。基于 android-ui-graph-builder 的 Screen.json + Containment_Edge.json 做深度遍历，对 ArkTS 端 main_pages.json 做枚举对账。当用户说"UI 覆盖率"、"漏页"、"补页"、"二三层 UI"、"哪些页缺了"、"我的页没生成"、"查一下页面是不是齐了"时触发。即使用户只说"对一下页面"或"看看 spec 全不全",也应触发。不判断视觉一致性（由 arkts-visual-verify 负责），只做 UI 结构覆盖率对账。
metadata:
  type: domain
  domain: migration
  tags:
  - domain
  - migration
  - audit
  - ui-graph
  - coverage
---
# a2h-ui-coverage-auditor

## 1. 定位

Pipeline 中段的**强制审计步**，在 `a2h-spec` 完成后、`a2h-plan` 启动前必跑一次；在 `a2h-verify` 阶段也再跑一次做回归。

回答一个问题：**Android 项目里所有 UI 节点（含二/三层）在 spec 和 ArkTS 端是否都对应得上？**

```
a2h-spec → a2h-ui-coverage-auditor（本 skill）★ → a2h-plan
                       ↓
              [缺口报告] → a2h-spec 增量补 spec
                       ↓
                 重跑本 skill 直到通过

a2h-execute → a2h-verify → a2h-ui-coverage-auditor（回归）→ a2h-retrospect
```

**为什么必须前置**：本次 Fitness 迁移踩坑实证（见报告 §问题 3）—— 84 个 page spec 只覆盖 Activity 入口，二三层（PartTwo 5 个 step / PartFive 6 个 step / Course 二三级详情 / Section 详情子页）大量丢失，靠后续 9+ 条「补齐」commit 手工救火。本 skill 在 spec 阶段就把这些缺口暴露出来，避免一路漏到 verify 才发现。

---

## 2. 输入

| 来源 | 用途 |
|---|---|
| `<android-ui-graph>/Screen.json` | Android 端所有 Screen 节点（深度遍历产物） |
| `<android-ui-graph>/Component.json` | 组件清单（ViewPager / Tab / Fragment 子项） |
| `<android-ui-graph>/Containment_Edge.json` | Screen → 子页面 / 子组件的容器边 |
| `<android-ui-graph>/Navigation_Edge.json` | 跳转关系（识别独立子页 vs 内嵌页） |
| `spec/baseline/ui/page_*.md` | 当前已生成 page spec 列表 |
| `entry/src/main/ets/pages/*.ets` | 当前已落地的 ArkTS 页面 |
| `entry/src/main/resources/base/profile/main_pages.json` | 已注册的可路由页 |

如果 ui-graph 不存在，先调 `android-ui-graph-builder` 生成。

### 启动校验 — builder 产物完整性检查

读取 `Screen.json` 后，扫描 `type` 字段分布。**多 type 是 Android 项目的常态**（任何包含设置/对话框/Tab 的 App 都应有 Activity + Fragment + DialogFragment 等多种 type）：

| `type` 分布 | 判定 | 行动 |
|---|---|---|
| 仅含 `Activity`（无 Fragment / Dialog） | 🔴 BUILDER_INCOMPLETE | 警告 "builder 可能漏识别二三层"，建议重跑 builder Step 3；本次审计仍继续但报告标注不可信 |
| 含 ≥ 2 种 type（Activity + Fragment 等） | ✅ PASS | 进入对账阶段 |

---

## 3. 输出

### 3.1 主报告 `spec/ui-coverage-report.md`

```markdown
# UI 覆盖率审计

- 扫描时间：<ISO date>
- Android Screen 总数（含二三层）：<N>
- spec/baseline/ui/page_*.md 数量：<M>
- entry/src/main/ets/pages/*.ets 数量：<K>
- main_pages.json 注册数：<L>

## 三层对账总览

| 维度 | Android | spec | ArkTS pages | main_pages | 状态 |
|---|---|---|---|---|---|
| 一层 Activity | 99 | 84 | 83 | 83 | 🟡 spec 缺 15，ArkTS 缺 1 |
| 二层 Fragment / ViewPager 子页 | 47 | 0 | 12 | 0 | ❌ spec 全缺，ArkTS 仅手补 12 |
| 三层 Step / Dialog 内嵌页 | 38 | 0 | 6 | 0 | ❌ spec 全缺，ArkTS 仅手补 6 |
| **总计** | **184** | **84** | **101** | **83** | **覆盖率 spec 46% / arkts 55%** |

## 缺口清单（按优先级）

### P0（被多入口引用，必须补）

| Android Screen | 引用入口数 | spec 缺失 | ArkTS 缺失 | 建议 |
|---|---|---|---|---|
| GyPartTwoStep1Fragment（身高页） | 1 主入口 + 重置入口 | ✓ | ✓ | 立即补 spec + page |
| GyPartTwoStep2Fragment（体重页） | 同上 | ✓ | ✓ | 立即补 |
| GyPartFiveJiliFragment | 主流入口 | ✓ | ✓ | 立即补 |
| GyCourseSectionDetailDialog | CourseSectionPage 列表项 | ✓ | ✓ | 立即补 |

### P1（单入口，可延后）

...

### P2（仅工具页/调试页）

...
```

### 3.2 增量任务清单 `spec/ui-coverage-tasks.md`

直接喂给 `a2h-spec`（增量模式）和 `a2h-plan`：

```markdown
## a2h-spec 增量任务

- [ ] 补 page_0085_GyPartTwoStep1Fragment.md（来源：android-ui-graph Screen#234）
- [ ] 补 page_0086_GyPartTwoStep2Fragment.md
- [ ] 补 page_0087_GyPartFiveJiliFragment.md
...

## a2h-plan 增量任务

- [ ] 把上述 page 加入 ui-plan.md Batch 9
- [ ] 在 plans/slices/slice-07-f002.md 增加任务行 / 执行单元（feature-plan.md 为只读索引，账本在 slice 文件）
```

### 3.3 通过/失败信号

```text
通过条件：
  - 一层 Activity spec 覆盖率 ≥ 95%
  - 二层 Fragment spec 覆盖率 ≥ 90%
  - 三层 Step / Dialog spec 覆盖率 ≥ 80%
失败时：return 非零码 + 阻断 a2h-plan
```

---

## 4. 核心算法

### 4.1 数据来源（不重新解析 Android 项目）

> **重要**：本 skill **不重新解析 Android 项目**。所有 Screen（含一/二/三层）来自 [android-ui-graph-builder Step 3](../android-ui-graph-builder/SKILL.md) 的 `Screen.json` 产物。
>
> 依赖 builder 已识别所有二三层 UI（若发现漏识别则报 BUILDER_INCOMPLETE）（含 ViewPager 子页 / Tab Fragment / Step Fragment / DialogFragment / BottomSheet / PopupWindow / XPopup / FragmentTransaction / Compose composable —— 详见 builder Step 3 的"二三层来源清单"）。
>
> **如发现 builder 漏识别**：报告中标注 `BUILDER_INCOMPLETE` + 建议重跑 builder（不在本 skill 内重新解析 — 避免双源不一致）。

### 4.2 ArkTS Page 枚举

1. `entry/src/main/ets/pages/*.ets` 文件名扁平枚举
2. `main_pages.json` profile 已注册项
3. `Component-style` 子页：扫 `@ComponentV2` + 文件路径在 `pages/` 下且文件名以 `Component.ets` 结尾的视为二层产物
4. `RouteConst` + `RouterUtil.push` 调用集合

### 4.3 三层对账规则

| Android 名 | spec 文件 | ArkTS 文件 | 判定 |
|---|---|---|---|
| `Gy<Name>Activity` | `page_NNNN_Gy<Name>Activity.md` | `<Name>Page.ets` | 一层正常 |
| `Gy<Name>Fragment` | `page_NNNN_Gy<Name>Fragment.md` 或 `page_NNNN_Gy<Activity>.md#子页-<Name>` | `<Name>Component.ets` 或 `<Name>Page.ets` | 二层正常 |
| `Gy<Step>StepFragment` (ViewPager 子) | 内嵌在父 Activity spec 的子页章节 | `<Step>Component.ets` | 三层正常 |
| `*Dialog` / `*XPopup` | `dialogs/<Name>.md` 或父 spec 的对话框章节 | `dialogs/<Name>.ets` | 三层正常 |

模糊匹配：去掉 Gy 前缀、`Activity/Fragment/Dialog` 后缀，做 case-insensitive 同名匹配。

---

## 5. 与 pipeline 的集成

### 触发时机

| 时机 | 行为 |
|---|---|
| `a2h-spec` 完成后 | 必跑；不通过则阻断 `a2h-plan` |
| `a2h-execute` 完成后 | 必跑；不通过则阻断 `a2h-verify` |
| 用户主动说「漏页/UI 覆盖率」 | 立即跑增量审计（不依赖 pipeline 状态） |
| `a2h-retrospect` 阶段 | 跑最终回归，作为本轮迁移的 KPI 写入回顾报告 |

### 修复回环

```
本 skill 不通过
  ↓
生成 ui-coverage-tasks.md
  ↓
派发给 a2h-spec（增量模式）/ a2h-plan / a2h-execute
  ↓
重跑本 skill 直到通过
```

---

## 6. 边界

**做**：

- 三层覆盖率统计 + 缺口清单 + 增量任务派发

**不做**：

- 不生成 spec 内容（这是 `a2h-spec` 增量模式的事）
- 不写 ArkTS 代码（这是 `a2h-execute` 的事）
- 不判断 UI 视觉一致性（那是 `arkts-visual-verify` 的事）—— 本 skill 只看「页是否存在」，不看「页好不好看」

---

## 7. Failure Modes

| 现象 | 处理 |
|---|---|
| android-ui-graph 不存在 | 自动调 android-ui-graph-builder 先生成 |
| Screen.json 中名字带项目特定前缀（Gy/Th/CS/Cs） | 内置常见前缀字典做归一化 |
| ArkTS 端用了非约定命名（如 `XxxScreen.ets`） | 模糊匹配 + 警告，不直接判失败 |
| 二三层匹配歧义（一个 Fragment 被多 Activity 共享） | 都标记为 hit，不重复计数 |
| Android 端 Compose Screen | 走 `composable("xxx")` 路由名匹配 |
