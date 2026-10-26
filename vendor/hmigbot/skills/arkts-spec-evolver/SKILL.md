---
name: arkts-spec-evolver
description: 增量 Spec 演进管理（V2 优先，API 12+）。当用户需要补全功能、修复 Bug、性能优化、审计 spec 与代码差距、或任何 "spec 先行" 的变更时触发，审计/回归扫描兼容 V2/V1 两套装饰器。即使用户只说"这个功能缺失""这个有 bug""检查下还缺什么"也应触发。不适用于 baseline 初始生成（由 a2h-spec 负责）。
metadata:
  type: domain
  domain: engineering
  tags:
  - spec-management
  - incremental
  - migration
---
# arkts-spec-evolver

## 定位

Post-V1 增量 spec 演进管理 skill。在 `a2h-spec` 完成初始 baseline（ui-manifest + feature-index/base/features）生成后接管，负责后续所有变更的 spec 管理与执行编排。

**核心原则**：强制 "spec 先行" 纪律——**任何代码变更必须先有 spec，spec 是唯一变更驱动源**。

### 执行纪律（所有模式、所有步骤共享，最高优先级）

<HARD-GATE>
本 skill 定义的每一个步骤、每一个 HARD-GATE、每一个子 skill 调用都是**强制执行项**，不是建议或参考。

**绝对禁止以下行为**：

1. **跳过步骤**：不得因为"觉得没必要"、"应该没问题"、"时间紧"等理由跳过任何步骤。每个步骤存在都有原因——跳过 Step 3.5 导致无回归范围、跳过 Step 9.5 导致实际改动未被追踪、跳过 Step 10.6 导致用户失去选择权。

2. **简化替代**：不得用自认为等效的简化方式替代 skill 要求的操作。典型违规：
   - skill 要求调用 `arkts-visual-verify` → 自己截图看一眼就判通过
   - skill 要求派生回归范围清单 → 脑中过了一遍觉得没影响就跳过
   - skill 要求输出结构化报告 → 用一句话"验证通过"替代
   - skill 要求等用户确认（Gate 1/2/§S2） → 自动跳过继续执行

3. **默默降级**：当某个步骤确实无法执行时（如设备不可用、子 skill 不存在），不得默默跳过。必须：
   - 按 skill 定义的降级路径处理（如无设备 → `verifying(visual-pending)`）
   - 如果 skill 没有定义降级路径 → 停下来向用户说明，等待指示
   - 在 spec 的验证记录中显式记录跳过原因和证据

4. **事后补文档**：不得先写代码再补 spec / 回归范围 / plan。流程顺序是硬性的：create → plan → execute → verify，每个阶段的产物是下个阶段的输入。

**自检规则**：在执行每个 Step 之前，对照本 skill 原文确认：
- 这个 Step 的前置条件满足了吗？
- 这个 Step 要求产出什么文档/调用什么 skill？
- 这个 Step 有 HARD-GATE 吗？门禁条件过了吗？

如果对某个步骤的要求理解模糊，重新读一遍该步骤的原文，不要凭记忆执行。
</HARD-GATE>

### 适用场景

- **功能补全**：baseline 遗漏的功能需要补录并实现
- **Bug 修复**：开发/测试中发现的问题需要先记录为 spec 再修复
- **优化迭代**：V1 交付后的性能优化、UI 对齐、V2 增强
- **差距审计**：定期检查 spec 与代码的差距，发现遗漏

### 在整体工作流中的位置

```
a2h-spec（Phase A/B/C）→ a2h-plan → a2h-execute（3 Stage 引擎）→ a2h-verify → a2h-retrospect
    │
    ▼
交付 V1 → baseline 固化（ui-manifest + feature-index + features/ 移入 baseline/）
    │
    ▼
后续迭代（spec-evolver 接管）
    ├─ 用户/测试发现问题 → create + execute
    ├─ 定期审计 → audit → 批量 create → 逐个 execute
    └─ V2 规划 → 多个 create → 逐个 execute
```

---

## 七种工作模式

| 模式 | 触发 | 说明 |
|------|------|------|
| `create` | "XX功能缺失，生成spec" | 创建增量 spec，不执行 |
| `plan` | "为 F-xxx 生成实现计划" | 为已有增量 spec 生成实现计划 |
| `execute` | "执行 spec/features/...-F031-...md" | 按计划执行代码变更 |
| `create+plan+execute+verify` | "XX功能缺失，生成spec并实现" | 全流程（含两道门禁，见下方） |
| `verify` | "验证 F-xxx 的实现" | 按验收标准验证已完成的变更 |
| `audit` | "检查spec还缺什么" | 审计 baseline 与代码差距，批量生成增量 spec |
| `status` | "查看所有增量spec状态" | 列出所有增量 spec 的状态 |

### 全流程执行逻辑

<HARD-GATE>
全流程模式自动推进各阶段，但必须在以下两个节点暂停等待用户确认：

```
create（生成 spec）
    │
    ▼
★ Gate 1: 输出 spec 摘要，等待用户确认
    │ 用户确认
    ▼
plan（生成实现计划）
    │
    ▼
★ Gate 2: 输出 plan 摘要，等待用户确认
    │ 用户确认
    ▼
execute（执行代码变更）
    │
    ▼
verify（静态：编译 + 验收 grep + 回归；视觉：UI 改动时调 arkts-visual-verify 定向扫单页）
```

用户在任一门禁处可以：
- 确认 → 自动进入下一阶段
- 要求修改 → 修改后重新等待确认
- 终止 → 停止流程，保留已生成的 spec/plan

绝对禁止在用户确认前进入下一阶段。
</HARD-GATE>

---

## 完整工作流程（对齐 Pipeline 五步）

> **MUST**：执行增量演进前，逐步遵循 `references/workflow.md`（Step 1-12 完整规程 + 「强制执行检查清单」+ Verify 三阶段门控）。下为步骤骨架，硬门控细节全在 references/workflow.md。

- **Create（Step 1-5）**：定位变更 → 读 spec-index → 生成/更新增量 spec（feature_acs = 清单A ∪ 清单B）→ 占位登记 → status=planned
- **Plan（Step 6-7）**：按影响面拆 plan（≤2 文件用简化 plan）→ 人工审批
- **Execute（Step 8-9）**：Subagent 执行 → 编译通过 → status=implemented
- **Verify（Step 10-12）**：Step 10 静态/页面审计 → Step 11a dt-verifier 回归 + Step 11b visual-verify → Step 12 status 升级

⚠️ **status 升级护栏**：仅当 Step 10 ✅ + Step 11a ✅/N/A + Step 11b 通过（无设备 → visual-pending）才升 verifying/verified；严禁跳过回归直接升 verified。完整判定见 references/workflow.md。

---

## 简化流程（适用于简单 bugfix）

```
复杂度判断:
  影响 ≤2 个文件 + 单一 section → 简化流程
  影响 >2 个文件 或 多层 → 完整流程
```

<HARD-GATE>
简化流程仅简化 plan 的存储形式（嵌入 spec 而非独立文件），
两道门禁同样不可跳过。
</HARD-GATE>

简化流程步骤：
```
create → ★ Gate 1（用户确认 spec）→
plan（嵌入 spec 的"实现计划"区域）→ ★ Gate 2（用户确认 plan）→
execute → verify
```

状态流转完整保留：pending → planned → in_progress → verifying → done

简化的是 plan 文件形式（嵌入 spec 而非独立文件），不是流程步骤。

---

## 回退处理

验证失败时，按失败类型分别处理:

### 编译失败
- `hmos-fix-build-errors` 自动修复（最多 20 轮）
- 20 轮后仍失败 → `knowledge-verifier` 介入诊断
- 修复后重新 verify
- **不回退代码**（修复前进策略）

### 验收失败
- 分析失败原因
- 若实现方案有误 → 调整 plan，重新 execute 失败的 task
- 若 spec 本身有误 → 更新增量 spec，重新 plan + execute

### 回归失败（dt-verifier 退化 / visual-verify 已有元素消失变形）

回归失败有 3 种**根本不同**的子类型，处理路径完全不同。**不得**统一走"git revert + 重新 plan"——会导致合理改动被反复打回。先分类，再走对应路径：

```
回归失败 → 诊断子类型（必须先做）：
  1. 读 dt-verifier 报告 / visual-verify 多模态描述，定位飘红的具体 AC + 现象
  2. 读 spec 的 ## 回归范围 + ## 验收标准，对照判断飘红是否"该飘红"
  3. 按下表分类 → 走对应路径
```

#### 子类 A：真 bug（最常见）

**特征**：本次改动写错了，飘红 AC 反映的是真实 broken 行为。

**例**：F-021 改 `deleteSelected` 时忘过滤本地上传项的负 id，dt-verifier 在 R3 飘红显示批量删除 AC 失败；或 visual-verify 显示原列表项被新增 FAB 遮挡。

**处理**：
- 飘红根因在 H_TARGETS 内 → 直接修，重跑 Step 10 / 11a / 11b。**不回到 Gate 1/2**
- 飘红根因在 H_TARGETS 外 → 走 §M3.3 越界请示流程，扩展 H_TARGETS 后再修
- 修复后 spec status：`verifying`（未升级 done，等下一轮 verify 通过）
- spec `## 验证记录` 追加该轮飘红 + 修复 commit

**绝大多数回归失败属于此类**，处理路径最短。

#### 子类 B：设计冲突（需 spec 重审）

**特征**：本次新增功能与某条 baseline AC 在设计上无法共存——不是实现问题，是规则矛盾。

**例**：新增 spec 要求"AI 作品列表项默认带选中态"，但 baseline F006-AC2 明确"列表项默认未选中"。两者都按 spec 实现都"对"，但同一个 UI 不可能同时满足。

**处理**：
- 回 evolver Gate 1 重审，向用户出示冲突详情：
  ```
  ⚠ 设计冲突：
    本次 spec：<冲突 AC 文本>
    baseline：<冲突 baseline AC 路径 + 文本>
    冲突现象：<dt-verifier / visual-verify 报告原文>
  
  请选择：
    (a) 放弃本次 spec → status: deprecated，保留 baseline
    (b) 解决冲突 → 调整本次 spec 或 baseline AC 后重新走流程（具体方案由用户决定）
  ```
- 用户回复 (a/b) 前 status 维持 `failed`，不擅自决策

#### 子类 C：测试本身错（少见但要承认）

**特征**：dt-verifier 生成的 it() 断言写错了——选错 selector / 期望值过时 / 异步等待不足。spec 和实现都正确，是测试代码的 bug。

**例**：dt-verifier 给 P0009-UI-INTERACT_tab_switch 生成的 selector 找的是中文文案"我的收藏"，但 HMOS 端实装文案是"我收藏的"，导致 selector 永远命不中。

**处理**：
- 标记该 it() `test_fix_needed`
- 调 dt-verifier 重生成对应 it()（filter 到该单条），人工 review 新断言后再跑
- spec 不动，spec status 保持 `verifying`
- 修复后再跑 Step 11a，仍飘红 → 重新走分类（很可能其实是子类 A）

**最大循环次数：10 次**（防死循环硬闸门）：
- 同一条 it() 反复进入子类 C 累计达 10 次仍无法命中合理断言 → 强制停下
- 该 AC 自动标记 `manual_verify`，加入"待人工审核清单"
- spec 不阻塞：该 AC 不再参与自动回归判定，spec status 可升级为 `done(manual-pending)`
- spec `## 验证记录` 显式列出该 AC + 10 次失败的最后一次报错，作为人工审核时的参考
- spec-index.md 同步标注 `done(manual-pending)`，后续可批量人工验收，验完更新为 `done`

**核心原则**：承认"有的 AC 当前自动测不了"是事实（动画过程、跨进程交互、模糊指标等），给 spec 一个**有出口的**路径——不阻塞业务交付，但欠的债清晰可追溯。

#### 分类决策树（避免分类困难）

```
飘红时先问两个问题：
  Q1. 读飘红 AC 文本 + 实际 HMOS 行为 → 行为对得上 spec 描述吗？
       ├─ 不对 → 子类 A（真 bug）
       └─ 对   → Q2

  Q2. 飘红 AC 描述的行为 vs 本次 spec 描述的行为 → 矛盾吗？
       ├─ 矛盾 → 子类 B（设计冲突）
       └─ 不矛盾 → 子类 C（测试错，因为行为对得上但测试还是飘红）
```

#### 通用原则

- **不得无差别 git revert**：只有子类 A 在严重破坏不可修复时才考虑回退代码
- **每轮飘红必须分类后再处理**：spec `## 验证记录` 必须记录"本轮飘红 N 条，分类：A=x B=y C=z"
- **同一 spec 反复进入子类 A → 实现方案有问题**，回 Gate 2 调整 plan
- **同一 spec 反复进入子类 B → spec 设计有问题**，回 Gate 1 重审或废弃

---

## audit 模式

> **MUST**：audit（spec↔代码差距审计）的检测范围与流程见 `references/audit-mode.md`。

审计 spec↔代码差距时，把 `spec/baseline/source-coverage-report.md`（及多子仓 `module-dep-graph.json` / `cross-module-contracts.md`）纳入「已覆盖范围」基线——被某 feature 锚定或已登记 skip-list 的源码包视为「已规约」，避免把已锚定能力误报为缺失差异。

---

## 增量 spec 文件格式

> **MUST**：增量 spec 的 frontmatter 字段与正文格式见 `references/spec-format-and-structure.md`。

增量产出与 baseline 同格式、**不得回退**：feature spec 顶部 YAML 必带 `complexity` + `tier`(core/standard/peripheral) + `depth`(full/stub)；complex 的每条 AC 末尾附**二型锚点之一**——`源:<Kotlin 符号> → 标:<ArkTS 方法>`（parity）或 `决:<PD/D/G-ID> → 标:<ArkTS 方法>`（平台差异 AC，仅当 ID 存在于 decision-ledger 时合法；产生入口唯一 = `## 实现映射` HARD-DIV 行 4 件套协议，见 a2h-spec feature-spec-template §实现映射；**既有 `决:` 锚 AC 与 `〔superseded by …〕` 标注不得在增量演进中被剥除或"规范化"掉**）——并保留 `## 实现映射（Source→ArkTS）` 与 `## 服务层（ArkTS 目标接口）` 节；AC 数量遵守 a2h-spec 的 AC 预算（`score_complexity.py`，parity 与差异 AC 分账）与质量护栏（防凑数 / 三无 AC 禁止 / 同 `源` 符号去重 / 跨 feature 归 owner；护栏对两型锚 AC 同等适用）。

---

## 命名约定

| 类型 | 前缀 | 编号规则 | 示例 |
|------|------|---------|------|
| 功能补全/新功能 | F | 延续 baseline feature-index.md 的 F-xxx 编号 | `YYYY-MM-DD-Fxxx-description.md` |
| Bug 修复 | BF | 独立编号 | `YYYY-MM-DD-BFxxx-description.md` |
| 优化 | OPT | 独立编号 | `YYYY-MM-DD-OPTxxx-description.md` |

Plan 文件命名与增量 spec 对应:
- `spec/features/plans/YYYY-MM-DD-Fxxx-plan.md`
- `spec/bugfixes/plans/YYYY-MM-DD-BFxxx-plan.md`
- `spec/optimizations/plans/YYYY-MM-DD-OPTxxx-plan.md`

---

## 状态生命周期

增量 spec 的 `status` 字段支持 9 种状态:

| 状态 | 含义 | 对应阶段 |
|------|------|---------|
| `pending` | 已创建 spec，待确认 | create 完成 |
| `planned` | 实现计划已生成，待确认 | plan 完成 |
| `in_progress` | 正在执行代码变更 | execute 中 |
| `verifying` | 代码变更完成，验证中 | verify 中 |
| `verifying(manual-regression)` | 静态通过，用户选择人工回归，等待反馈 | verify Step 10.6 用户选 (b) |
| `verifying(visual-pending)` | 静态/回归通过，视觉验证因无设备待补 | verify Step 11b 设备不可达 |
| `done` | 验证通过，全部完成 | verify 通过 |
| `done(manual-pending)` | 自动验证通过，但有 AC 需人工审核 | 子类 C 触发 manual_verify |
| `failed` | 验证失败，需回退/重做 | verify 失败 |
| `deprecated` | 已废弃，不再有效 | 任意阶段可标记 |

### 状态流转图

```
pending → planned → in_progress → verifying → done
                                      │           │
                                      │           └→ done(manual-pending)（部分 AC 待人工审核 → 人工验完回 done）
                                      ├→ verifying(visual-pending)（设备恢复后回 verifying）
                                      └→ failed → pending（回退重做）
任意状态 → deprecated（废弃）
```

### 废弃处理

废弃时在 frontmatter 中增加 `deprecated_by` 和/或 `deprecated_reason`:

```yaml
status: deprecated
deprecated_reason: "被 BF-005 替代，提供了更好的修复方案"
deprecated_by: BF-005
```

---

## 有效状态合成

baseline 不可变 + 增量独立存在，意味着 "当前状态" 需要合成。

### 合成规则

增量 spec 对 baseline 是**严格追加**语义:

| 操作 | 语义 | 示例 |
|------|------|------|
| 新增行 | 在 baseline 表中追加新行 | D4 新增 F-xxx |
| 修正行 | 标注 baseline 中某行的修正值 | SS6 中 F-005 从 V2 改为 V1 |
| 删除行 | 标注 baseline 中某行已废弃 | F-014 标记 `deprecated` |

### 多个增量影响同一 section 时

按时间顺序（创建日期）依次叠加。后创建的增量覆盖先创建的（同一字段时）。

### 读取 "当前状态" 的标准流程（5 步）

```
1. 读 spec-index.md
2. 读 baseline 对应 section
3. 扫描增量表中 status=done 且 affects 包含该 section 的增量
4. 按创建日期排序，依次叠加
5. 得到有效状态
```

---

## Skill 调度顺序

post-V1 增量执行不走完整 3 Stage 流程（UI Pipeline → Feature Base → Feature Slices），而是按影响层精简调度:

```
增量 spec affects 分析
    │
    ├─ 仅影响 feature-index 元数据 → 不改代码，仅更新 spec
    │
    ├─ 影响 feature-base (数据模型) → arkts-data-layer 优先
    │   └─ 若同时影响 ui pages → 再调 arkts-component-builder
    │
    ├─ 影响 ui-manifest / ui pages → arkts-navigation-builder
    │   └─ 若同时影响 ui pages → 再调 arkts-component-builder
    │
    ├─ 仅影响 ui page specs → arkts-component-builder / arkts-ui-alignment
    │
    └─ 影响多层 → 按依赖顺序:
        arkts-data-layer → arkts-navigation-builder → arkts-state-manager → arkts-component-builder
```

### spec-evolver 与下游 skill 的关系

spec-evolver 是**编排层**，不替代任何现有 skill:

```
spec-evolver (编排)
    ├─ feature → 按影响层选择:
    │   ├─ affects feature-base → arkts-data-layer
    │   ├─ affects ui pages → arkts-navigation-builder
    │   ├─ affects ui pages → arkts-component-builder / arkts-ui-alignment
    │   ├─ affects WebView → arkts-webview
    │   └─ affects 多层 → 按依赖顺序依次调用
    ├─ bugfix →
    │   ├─ 先 arkts-knowledge-verifier 诊断
    │   └─ 再调用对应 skill 修复
    ├─ optimization →
    │   ├─ 性能 → arkts-component-builder
    │   ├─ UI 对齐 → arkts-ui-alignment
    │   └─ 动画 → arkts-animation-builder
    └─ verify 阶段（所有类型共享）:
        ├─ 编译 → hmos-fix-build-errors
        └─ 视觉（affects 含 ui/ui-manifest 时必调）→ arkts-visual-verify (targeted-single-page)
```

---

## 触发 Prompt 示例

| 场景 | Prompt | 模式 |
|------|--------|------|
| 全流程 | `播放速度控制功能缺失，生成 spec 并实现` | create+plan+execute+verify |
| 只生成 spec | `播放速度控制功能缺失，只生成 spec` | create |
| 为已有 spec 生成计划 | `为 F-xxx 生成实现计划` | plan |
| 执行已有计划 | `执行 spec/features/...-F031-...md` | execute |
| 验证已完成的变更 | `验证 F-xxx 的实现` | verify |
| 修复 bug 全流程 | `AVPlayer seek 到末尾会崩溃，修复` | create+plan+execute+verify |
| 优化全流程 | `列表滚动卡顿，优化` | create+plan+execute+verify |
| 审计 | `检查下 spec 和代码的差距` | audit |
| 查看状态 | `查看所有增量 spec 的状态` | status |

---

## a2h-spec vs spec-evolver

| 职责 | a2h-spec | spec-evolver |
|------|----------|-------------|
| 何时用 | 初始迁移（0→1），Phase A/B/C 三阶段 | V1 交付后，持续迭代（1→N） |
| 输入 | Android 源码 + ref + ui-snapshots | 用户描述的变更需求 |
| 输出 | baseline（ui-manifest + feature-index/base/features） | 增量 spec 文件 |
| 修改 baseline | 生成 baseline | 不修改 baseline（只读） |
| 驱动代码 | 不驱动（只产 spec） | 驱动（spec → plan → code → verify 闭环） |
| 目录 | `spec/baseline/` | `spec/features/` `spec/bugfixes/` `spec/optimizations/` |
| 调用频次 | 项目初始一次 | 持续迭代多次 |
| 路由关系 | baseline 已存在时自动委托 spec-evolver | 被 a2h-spec 透传调用 |

### baseline 冻结约束

一旦 baseline 固化，**a2h-spec 不得在同一项目上重新运行**生成新的 baseline（否则 F-xxx 编号冲突）。a2h-spec 检测到 `spec/baseline/` 已存在时，自动委托 spec-evolver 处理。如需纳入新的 Android 功能，使用 spec-evolver create 模式生成增量 spec。

---

## Spec 目录结构 & spec-index 格式

> **MUST**：spec 目录布局与 spec-index.md 统一入口格式见 `references/spec-format-and-structure.md`。

---

## References

- `references/workflow.md` — Step 1-12 完整规程 + 强制执行检查清单 + Verify 门控
- `references/audit-mode.md` — audit 模式检测范围与流程
- `references/spec-format-and-structure.md` — 增量 spec 文件格式 + 目录结构 + spec-index 格式

- 增量 spec 模板: `templates/increment-spec-template.md`
- a2h-spec skill: `arkts-skills/skills/a2h-spec/SKILL.md`
- 迁移 Spec baseline: `spec/baseline/`（固化后）
- 统一索引入口: `spec/spec-index.md`
