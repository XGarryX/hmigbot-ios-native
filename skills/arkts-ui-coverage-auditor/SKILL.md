---
name: arkts-ui-coverage-auditor
description: iOS→ArkTS 迁移 UI 覆盖率审计。三层对账（iOS Screen × ArkTS Page × spec/baseline/ui/page_*.md），强制识别 a2h-spec 阶段漏掉的二三层 UI（Tab/嵌入子页 / 多步子页 / 模态内嵌页 / 页面内含 Component）。基于 ios-ui-graph-builder 的 Screen.json + Containment_Edge.json 做深度遍历，对 ArkTS 端 main_pages.json 做枚举对账。当用户说"UI 覆盖率"、"漏页"、"补页"、"二三层 UI"、"哪些页缺了"、"我的页没生成"、"查一下页面是不是齐了"时触发。即使用户只说"对一下页面"或"看看 spec 全不全",也应触发。不判断视觉一致性（由 arkts-visual-verify 负责），只做 UI 结构覆盖率对账。
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

> **iOS 源输入适配**：执行源分析/源设备操作前，读 [原生输入协议](../a2h-spec/references/native-input.md)。它仅替换平台输入；原阶段、模板、规则、门禁、模式和 target 侧执行保持 1.5.2。

# a2h-ui-coverage-auditor

## 1. 定位

Pipeline 中段的**强制审计步**，在 `a2h-spec` 完成后、`a2h-plan` 启动前必跑一次；在 `a2h-verify` 阶段也再跑一次做回归。

回答一个问题：**iOS 项目里所有 UI 节点（含二/三层）在 spec 和 ArkTS 端是否都对应得上？**

```
a2h-spec → a2h-ui-coverage-auditor（本 skill）★ → a2h-plan
                       ↓
              [缺口报告] → a2h-spec 增量补 spec
                       ↓
                 重跑本 skill 直到通过

a2h-execute → a2h-verify → a2h-ui-coverage-auditor（回归）→ a2h-retrospect
```

**为什么必须前置**：本次 Fitness 迁移踩坑实证（见报告 §问题 3）—— 84 个 page spec 只覆盖顶层入口，二三层（PartTwo 5 个 step / PartFive 6 个 step / Course 二三级详情 / Section 详情子页）大量丢失，靠后续 9+ 条「补齐」commit 手工救火。本 skill 在 spec 阶段就把这些缺口暴露出来，避免一路漏到 verify 才发现。

---

## 2. 输入

| 来源 | 用途 |
|---|---|
| `<ios-ui-graph>/Screen.json` | iOS 端所有 Screen 节点（深度遍历产物） |
| `<ios-ui-graph>/Component.json` | 组件清单（Tab / SwiftUI 子页 / UIKit child 子项） |
| `<ios-ui-graph>/Containment_Edge.json` | Screen → 子页面 / 子组件的容器边 |
| `<ios-ui-graph>/Navigation_Edge.json` | 跳转关系（识别独立子页 vs 内嵌页） |
| `spec/baseline/ui/page_*.md` | 当前已生成 page spec 列表 |
| `entry/src/main/ets/pages/*.ets` | 当前已落地的 ArkTS 页面 |
| `entry/src/main/resources/base/profile/main_pages.json` | 已注册的可路由页 |

如果 ui-graph 不存在，先调 `ios-ui-graph-builder` 生成。

### 启动校验 — builder 产物完整性检查

读取 Screen.type、导航与 containment，结合 A1 已有页面边界检查二三级页。SwiftUI 项目可能全部页面都是 SwiftUIView；类型种类多少不能独立证明完整或缺失。发现与真实导航/嵌入声明不一致时按原 BUILDER_INCOMPLETE 口径提示并继续审计、披露可信度，不凭单一类型增加硬门。

| builder 层级证据 | 原诊断 | 处理 |
|---|---|---|
| 仅根入口（App/Scene/根视图），Source 不能证明为单页 | 🔴 BUILDER_INCOMPLETE | 保持原默认诊断，建议补查 builder；继续审计并披露可信度，无法确认动态下一级时写原因 |
| 仅根入口，Source 已证明确为单页且无下一级 | ✅ PASS | 记录单页依据，进入原对账 |
| 已包含至少一个路由/Tab/模态/子容器下一级页面（同种原生类型也可） | ✅ PASS | 进入原对账；其他部分漏页仍由原逐页归属和二三级覆盖率处理，本条不额外加严 |

原生示例用例（本条诊断，不替代后续覆盖率）：纯 SwiftUI 有下一级→PASS；纯 UIKit 有下一级→PASS；仅根且源证明有下一级→BUILDER_INCOMPLETE；仅根且已证实单页→PASS；仅根且无法判断→BUILDER_INCOMPLETE 并说明；有下一级但部分漏页→本条 PASS，原覆盖规则另报。

---

## 3. 输出

### 3.1 主报告 `spec/ui-coverage-report.md`

```markdown
# UI 覆盖率审计

- 扫描时间：<ISO date>
- iOS Screen 总数（含二三层）：<N>
- spec/baseline/ui/page_*.md 数量：<M>
- entry/src/main/ets/pages/*.ets 数量：<K>
- main_pages.json 注册数：<L>

## 三层对账总览

| 维度 | iOS | spec | ArkTS pages | main_pages | 状态 |
|---|---|---|---|---|---|
| 一层主页面 | 99 | 84 | 83 | 83 | 🟡 spec 缺 15，ArkTS 缺 1 |
| 二层嵌入 / Tab 子页 | 47 | 0 | 12 | 0 | ❌ spec 全缺，ArkTS 仅手补 12 |
| 三层 Step / Dialog 内嵌页 | 38 | 0 | 6 | 0 | ❌ spec 全缺，ArkTS 仅手补 6 |
| **总计** | **184** | **84** | **101** | **83** | **覆盖率 spec 46% / arkts 55%** |

## 缺口清单（按优先级）

### P0（被多入口引用，必须补）

| iOS Screen | 引用入口数 | spec 缺失 | ArkTS 缺失 | 建议 |
|---|---|---|---|---|
| HeightStepView（身高页） | 1 主入口 + 重置入口 | ✓ | ✓ | 立即补 spec + page |
| WeightStepView（体重页） | 同上 | ✓ | ✓ | 立即补 |
| ActivityStepView | 主流入口 | ✓ | ✓ | 立即补 |
| CourseSectionDetailView | CourseSectionPage 列表项 | ✓ | ✓ | 立即补 |

### P1（单入口，可延后）

...

### P2（仅工具页/调试页）

...
```

### 3.2 增量任务清单 `spec/ui-coverage-tasks.md`

直接喂给 `a2h-spec`（增量模式）和 `a2h-plan`：

```markdown
## a2h-spec 增量任务

- [ ] 补 page_0085_HeightStepView.md（来源：ios-ui-graph Screen#234）
- [ ] 补 page_0086_WeightStepView.md
- [ ] 补 page_0087_ActivityStepView.md
...

## a2h-plan 增量任务

- [ ] 把上述 page 加入 ui-plan.md Batch 9
- [ ] 在 plans/slices/slice-07-f002.md 增加任务行 / 执行单元（feature-plan.md 为只读索引，账本在 slice 文件）
```

### 3.3 通过/失败信号

```text
通过条件：
  - 一层主页面 spec 覆盖率 ≥ 95%
  - 二层原生嵌入/Tab 子页 spec 覆盖率 ≥ 90%
  - 三层 Step / Dialog spec 覆盖率 ≥ 80%
失败时：return 非零码 + 阻断 a2h-plan
```

---

## 4. 核心算法

### 4.1 数据来源（不重新解析 iOS 项目）

> **重要**：本 skill **不重新解析 iOS 项目**。所有 Screen（含一/二/三层）来自 [ios-ui-graph-builder Step 3](../ios-ui-graph-builder/SKILL.md) 的 `Screen.json` 产物。
>
> 依赖 builder 已识别所有二三层 UI（若发现漏识别则报 BUILDER_INCOMPLETE）（含 Tab/嵌入子页、多步页面、sheet/present 模态、UIKit child 与 SwiftUI 组合 —— 依 builder 与 A1 原生口径）。
>
> **如发现 builder 漏识别**：报告中标注 `BUILDER_INCOMPLETE` + 建议重跑 builder（不在本 skill 内重新解析 — 避免双源不一致）。

### 4.2 ArkTS Page 枚举

1. `entry/src/main/ets/pages/*.ets` 文件名扁平枚举
2. `main_pages.json` profile 已注册项
3. `Component-style` 子页：扫 `@ComponentV2` + 文件路径在 `pages/` 下且文件名以 `Component.ets` 结尾的视为二层产物
4. `RouteConst` + `RouterUtil.push` 调用集合

### 4.3 三层对账规则

| iOS 名 | spec 文件 | ArkTS 文件 | 判定 |
|---|---|---|---|
| `<Name>View` | `page_NNNN_<Name>View.md` | `<Name>Page.ets` | 一层正常 |
| `<Name>ChildView` | `page_NNNN_<Name>ChildView.md` 或 `page_NNNN_<Host>View.md#子页-<Name>` | `<Name>Component.ets` 或 `<Name>Page.ets` | 二层正常 |
| `<Step>View` (多步容器子) | 内嵌在父页面 spec 的子页章节 | `<Step>Component.ets` | 三层正常 |
| 真实 alert / sheet / present 模态 | `dialogs/<Name>.md` 或父 spec 的对话框章节 | `dialogs/<Name>.ets` | 三层正常 |

模糊匹配：去掉 Gy 前缀、已核实的原生展示层后缀，做 case-insensitive 同名匹配。

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
| ios-ui-graph 不存在 | 自动调 ios-ui-graph-builder 先生成 |
| Screen.json 中名字带项目特定前缀（Gy/Th/CS/Cs） | 内置常见前缀字典做归一化 |
| ArkTS 端用了非约定命名（如 `XxxScreen.ets`） | 模糊匹配 + 警告，不直接判失败 |
| 二三层匹配歧义（一个原生子页被多个宿主共享） | 都标记为 hit，不重复计数 |
| iOS 端 SwiftUI 页面 | 走真实 NavigationStack/path、Tab 与模态引用匹配 |
