---
name: a2h-plan
description: Android→ArkTS 迁移的执行计划生成（Pipeline 第二步）：读已审批的 spec/baseline/，产出 UI 转换计划 ui-plan.md 和功能执行计划 feature-plan.md。当用户说"生成计划""怎么做这个迁移""下一步怎么做"时触发。不要用于：生成 Spec（用 a2h-spec）或执行代码（用 a2h-execute）；spec/baseline/ 未就绪时提示先跑 a2h-spec。
metadata:
  type: pipeline
  domain: migration
  tags:
  - pipeline
  - migration
---

> **Codex subagent dispatch convention.** This skill dispatches subagents. In Codex, spawn them with the `spawn_agent` tool and pass `agent_type` = the role name **exactly as written in this skill** — the roles registered under `.codex/agents/*.toml` use the same hyphenated names, so no translation step is involved: `a2h-activity-converter`, `a2h-android-analyzer`, `a2h-closer`, `a2h-fixer`, `a2h-migration-worker`, `ad-profile-builder`, `compose-fact-analyzer`, `hmos-builder`, `scenario-builder`, `visual-fixer`, `visual-fixer-reviewer`. The built-in `general-purpose` agent_type is unchanged. (Claude's `subagent_type` field is written `agent_type` for Codex; `Agent(...)` dispatch calls are `spawn_agent(...)`; there is no `Task` tool in Codex.)
>
> **Join 协议（收口五条款）。** Codex 子代理完成后**不会**唤醒主会话——结果必须由派发方主动收口，违者=静默卡死（实测事故）。
> ① **循环 wait**：每个 `spawn_agent` 句柄用循环调用 `wait_agent` 收口；单次超时只代表"还在跑"，继续再调；**禁止以"等待子代理"为由结束回合**。醒后必调 `list_agents` 确认是谁完成——**完成的唯一合法信号 = `agent_status` 为 `{"completed": …}`，绝不是产物文件的存在/条数**（文件会中途落盘，读半截=实测事故）；completed 态会在数轮后从 list 中消失，所以每次醒来都要及时查。正文所有"等待完成 / join / 到点即收"表述一律指此循环。
> ② **死句柄与验收**：连续 3 次超时后调 `list_agents` 核对，可配 `wait_for_artifact.py` 探产物活性；已 completed 且 summary 可读 → 直接消费；句柄消失且从未观测到 completed → 按断点重派（带原 prompt + 已落盘产物，上限 2 次），禁止继续等待。**completed ≠ 验收通过**：join 点跑 `python3 .agents/skills/a2h-join/scripts/join_gate.py --project .` 验产物完整性，FAIL 视同未取回、按本条重派。
> ③ **收口锚点**：本 skill 最终完成报告前必须收口全部句柄（join_gate exit 0）；正文写明的显式 join 点优先按正文执行。发用户门（Gate）时允许句柄跨 Gate 存活，但 Gate 摘要必须列明未收口句柄清单 + 各自的指定 join 点。
> ④ **放行 ≠ 遗弃**：正文"非阻塞放行/到点即收/降级继续"只推迟收口时机，不豁免收口义务。
> ⑤ **fire-and-forget**：仅正文显式声明"结果丢弃/不 gate"的派发（如 a2h-execute 的 env-prewarm）免收口；审计只认 join_gate 内静态 allowlist，正文声明只是文档层。
> **派发纪律**：`task_name` 必须唯一（带 page-id/slice-id/round-N 后缀）；并行派发前把预期产物清单写 `spec/a2h/_work/expected_<join点>.json`（join_gate 对账用，契约只认派发方、不认子代理自报）；**谁派谁收**——sub-agent 内部需要"等齐 N 片再合并"时禁止嵌套外派后自行退出，要么同步自做、要么把分片清单回报主会话代派（sub-agent 一停止，收口能力即丢）。**契约产物必须出自承担任务的子代理**：重派上限后仍产不出 → 如实报缺并停在未完成态；禁止派发方代写占位产物让 gate 转绿（声明过也不行——绿账必须对应真产物）。

# a2h-plan

## 启动检查 — 待办 findings

读 `spec/.a2h/open-findings.json`（不存在 = 首轮，直接开工）：

| 情况 | 行动 |
|---|---|
| 有 `owner_stage: plan` 的条目 | 先处理这些，再做本轮正常工作；处理完重跑 `scripts/lint_plan_coverage.py` 确认消失 |
| 有 `owner_stage` 属**上游阶段**且 `severity: blocking` 的条目 | 🔴 **拒绝开工**，列出条目并提示用户回到该阶段（a2h-spec） |
| 条目标记 `escalate: true`（同一问题连续 3 轮） | 🔴 停止自动重试，按 a2h-spec `templates/decision-card.md` §连续未收敛 出决策卡 |
| 本阶段 section 标记 `halted`（进度停滞 3 轮 / 累计 10 轮） | 🔴 **停止修复尝试**，按 decision-card §连续未收敛 出决策卡；用户裁决后 `--clear-halt <决策ID>` 解除，再继续 |
| 无条目 | ✅ 正常开工 |

路由不靠猜：每个 linter 比对两份产物，**哪一侧缺条目就由哪一侧负责**。责任无法机械判定时
（典型：AC 按当前描述实现不了），用决策卡上报，由用户指定 owner——选项与 owner 的对应关系
写死在卡里，避免推诿。

**findings 只能由「原 linter 重跑后不再报」来关闭**，不能由任何一方声明「已修复」而关闭。

**findings 修复与编排纪律（§3.0 HARD-GATE）的关系**——修复不豁免「三写产物主线程禁自写」：
- 仅涉 `plan-coverage.json` 的修复（补映射、更新 digest）→ 该账本**非**三写产物，主线程直写即可；
- 涉及 slice / base-plan / ui-plan **内容**的修复（如 `PLAN.REQUIREMENT_UNOWNED` 需把需求纳入某
  slice）→ **按增量重派对应 slice-writer subagent**（携带缺失/修正的 requirement 清单）；主线程
  直改仅限 §3.0 降级条件成立，且须在审批摘要「可调整项」注明——与首轮生成同一条纪律，无特权。
- 修复完成后重跑 `lint_plan_coverage.py --after-repair` 确认关闭（配合循环熔断计数）。

> **存量/legacy spec 首轮提示**：报 `PLAN.SPEC_INDEX_MISSING` 不是要求改写 spec——在 a2h-spec
> 侧跑一条命令 `python3 <a2h-spec>/scripts/build_traceability_index.py --project-root <ROOT>`
> 即从现有 Markdown **秒级派生** index（零内容改动），重跑本 linter 即关闭。

## 关键约束（Critical）

- **输入门槛**：`spec/baseline/` 就绪 **且** `spec/ui-coverage-report.md` 最近一次 PASS，才能生成 plan；否则阻断并提示回 a2h-spec。
- **indexed 布局唯一**：feature-plan.md = 纯调度索引（`plan_format: indexed-v1`；Base 层正文外置 `plans/base-plan.md`（只读，无 checkbox/evidence）、索引留 3 行 stub；slice 头部按 parallel_group 以 `## Group N` 分节），逐 slice 账本在 `plans/slices/slice-NN-<fid>.md`；无 single 模式。
- **slice 文件三铁律**：① 调度表非详案（scope 名字级 + `spec_refs` 指针，复制 spec 正文 = FAIL）；② 生成后只读（零 checkbox / evidence / 状态字段——完成性由 verify_slice_wiring 机械校验 + 组 brief 记录）；③ 不持有占位（plan 期占位**直接写** `spec/placeholder-registry.md`）。
- **域判据**：spec 重审才变 → feature-index/spec；重新排期才变 → plan；执行推进才变 → 状态账本（ui-manifest / feature-index）+ brief。plan 不承载任何执行态。
- **编排派发（§3.0，HARD-GATE）**：P1 三写产物（ui-plan / base-plan / plans/slices/*）**必须由 A/B/C subagent 生成，主线程禁自写**；降级自跑仅限 §3.0 三条件成立，且须在审批摘要「可调整项」注明降级原因——**静默自跑 = PROCESS_VIOLATION**。
- **`<HARD-GATE>` 覆盖率阈值（§7）**：P0 功能 100% / UI 页面覆盖（ui-plan ⊇ ui-manifest）/ placeholder trigger 白名单率 100%（对 registry 跑）/ complex anchor 完整率 100%（读 spec）/ 对接点归属率 100% / **组件嵌入归属率 100%** / **分层校验 5 项**，任一不达标 → 阻断 plan 输出。
- **接线工作**只能走 ① owned task（Step 3d）或 ② forward-ref；其余写法（placeholder / prose defer）一律 plan FAIL。
- **Final Verification 必带 2 task**：FV-1 Final Structural Closure（a2h-execute §6）+ FV-2 终态全量编译，缺一即 plan FAIL —— 结构兜底在前（其修复会改码），终编译在后兜住可构建性；这是确保 §6 pipeline loop 不被遗漏的强制 task 化锚点。
- **人工审批**：双计划生成后须用户确认才进 a2h-execute。
- **References / Templates 强制加载（HARD-GATE）**：本 skill body 中所有 `[references/X.md]` / `[templates/Y.md]` 引用，在对应步骤执行时**必须** Read 整个文件作为执行规范，不得仅靠 body 摘要或字段名提示执行（templates 中"必填字段"段不得删减或简化）。跳过加载 = PROCESS_VIOLATION。规则适用于 LLM 主线程和派发的 subagent。

---

## 1. 定位

Pipeline 层第二步，读取已审批的 Spec 生成**双执行计划**——UI 计划按优先级/confidence 分批调度，功能计划按拓扑排序组织 Base 水平任务 + Feature Slice 垂直切片，skill 路由三层承载（§4）让下游 a2h-execute 知道调用哪个 Domain Skill。

```
a2h-spec（Spec 审批通过）
  │
  ▼
a2h-plan（读 Spec → 生成双计划，indexed 布局）
  │
  ├─ ui-plan.md（UI 转换计划：按优先级分批 + 并行标注 + Agent 估算）
  ├─ feature-plan.md（L1 调度索引：Base stub + 按 Group 分节的 slice 头部 + FV，plan_format: indexed-v1）
  ├─ plans/base-plan.md（Base 层正文，仅 Stage 2 消费）
  └─ plans/slices/slice-NN-<fid>.md（L2 逐 slice 只读调度账本）
      │
      ▼
  a2h-execute（按双计划分阶段执行；worker 直接拿 slice 文件路径）
```

---

## 2. 输入

自动读取以下文件：

| 文件 | 用途 |
|------|------|
| `spec/baseline/ui-manifest.md` | UI 页面清单、优先级、confidence、共享组件、转换批次 |
| `spec/baseline/feature-index.md` | 功能总索引、依赖图、优先级、V1/V2 分配 |
| `spec/baseline/feature-base.md` | Base 层公共能力定义（Models, DB, Network, Events 等） |
| `spec/baseline/features/F-xxx.md` | 各功能的详细 Spec（每个功能一个文件，顶部含 `complexity`/`tier`/`depth`，complex 的 AC 带二型锚点追踪：`源→标` parity / `决→标` 平台差异——`决:` 锚 AC 无 Kotlin 源侧，其覆盖归属 = `标` 侧实现由某 slice 认领；HARD-DIV 行的替代实现照常入切片排期） |
| `spec/baseline/ui/page_NNNN.md` | 各页面的详细 UI Spec（每个页面一个文件） |
| `spec/baseline/source-coverage-report.md` | 源码侧功能覆盖审计（a2h-spec C4.6b 产出，ownership + skip-list）；排期时作「已认领能力」参照 |
| `spec/baseline/module-dep-graph.json` | 多子仓项目专有：子仓 DAG + seam 签名，用于排子仓级拓扑序 |
| `spec/baseline/cross-module-contracts.md` | 多子仓项目专有：跨模块 seam 语义契约，用于排 Base 层与跨子仓 slice 顺序 |

如果 `spec/baseline/` 不存在或关键文件缺失，提示用户先执行 `a2h-spec`。

检查规则：
- `ui-manifest.md` + `feature-index.md` 都存在 → 可以生成双计划
- 只有 `ui-manifest.md` → 只能生成 ui-plan.md，提示功能 Spec 缺失
- 只有 `feature-index.md` → 只能生成 feature-plan.md，提示 UI Spec 缺失
- 都不存在 → 阻断，提示执行 `a2h-spec`

**contract_mode 检查**：若存在 `spec/.a2h/pipeline-state.json`，读其 `contract_mode`（`legacy|shadow|v2`）；文件或字段缺失 → 按 `legacy` 运行（即现行为）。`spec/.a2h/` 下存在其他 v2 残留文件**不改变行为、不作为输入**（mode 只认 pipeline-state.json 显式声明）。**例外**：evidence-coverage 家族（`open-findings.json` / `requirements-index.json` / `plan-coverage.json` / `impl-claims.json` / `verification.json`）**独立于 contract_mode 始终生效**，不属本条「残留」范围——该家族无模式开关，启动检查与收尾对账在任何 mode 下照常执行。

### 启动检查 — UI 覆盖率硬关卡

<HARD-GATE>
在生成双计划之前，**必须**检查 [arkts-ui-coverage-auditor](../arkts-ui-coverage-auditor/SKILL.md) 的产物 `spec/ui-coverage-report.md`：

| 状态 | 行动 |
|---|---|
| `ui-coverage-report.md` 不存在 | 🔴 **阻断**，提示用户回到 a2h-spec 完成 Step C4.6 自动审计 |
| 报告存在但最近一次 FAIL（覆盖率不达标） | 🔴 **阻断**，提示用户先按 ui-coverage-tasks.md 补缺失页面，重跑 auditor 直到 PASS |
| 报告存在且 PASS | ✅ 进入双计划生成 |
</HARD-GATE>

## 3. 双计划生成

### 3.0 编排协议（执行者分配：P0–P2）

双计划生成按 3 段编排派发 subagent（编排段记 P0–P2，与 Base 层的「执行序 Phase 0」无关）。**判断规则全部原地不动**——本节只回答「谁执行」，各 Step 语义与模板契约照旧；派发参数模板 + 信封契约 **MUST 加载** [references/plan-dispatch.md](./references/plan-dispatch.md)。

| 编排段 | 执行者 | 覆盖步骤 |
|---|---|---|
| P0 内核裁决 | 主线程 | §2 门槛 + 3b Step 1/2（读取 + 拓扑 + Slice↔F-ID 定号）+ 归属消歧四级链（ui-plan-template）/ hub / 横切（Step 5 隐式关系兜底）裁决 + 对接点全局归属映射（§7 第 8 项同源复用）→ kernel 紧凑表随派发 prompt 内联下发，不落盘 |
| P1 三写并行 | A ∥ B ∥ C（3 subagent） | A = §3a 生成 ui-plan.md（owning_slice 只抄 kernel）；B = Step 3 生成 base-plan.md + Step 4.3 Base 侧注入；C = Step 4.0–4.3 生成全部 plans/slices/* + registry 直写（本窗口唯一写者） |
| P2 收拢 | 主线程 | Step 5 定组 → 索引 + Step 6 FV → §7 + coverage-matrix → §7.2 grill → §8 审批 |

- **单写者分配**：A→ui-plan.md；B→base-plan.md（P-B 占位信封带回，禁直写 registry）；C→plans/slices/* + placeholder-registry.md；主线程→feature-plan.md 索引 / coverage-matrix.md / B 信封行 append。
- **kernel 只抄不判**：归属 / 定号 / hub / 横切裁决权在主线程 P0；agent 发现 kernel 与 spec 冲突 → 信封报告，禁自行改判。
- **降级规则**：子代理派发不可用（无派发工具 / 用户要求单线程 / 局部复跑）→ 主线程按 §3a→§3b 原序自跑全部步骤，**零行为差异**。
- 升级通道（协议不变）：C 可按 `{slice_list}` 分片为 K=ceil(N/4) 个同构 writer；§7 校验可拆并行只读 agent。

### 3a. UI 转换计划（ui-plan.md）

UI 计划负责调度所有页面的 UI 转换工作，按优先级和 confidence 分批执行。编排 P1·A 派发生成（§3.0）；`owning_slice` 判定已在 P0 kernel 完成，writer 只抄结果表。

**生成步骤**：

**Step 1: 读取页面清单**

从 `spec/baseline/ui-manifest.md` 的页面清单表格中提取：
- 每个页面的 Android 源、ArkTS 目标文件、优先级（P0/P1/P2）、confidence（high/medium/low）、当前状态

**Step 2: 按优先级和 confidence 分批**

分批规则：
1. 同一优先级内，confidence: high 的页面排在前面（confidence 是**分批输入**，读 ui-manifest，**不输出成列**）；low 页行内标 ⚠️ 需人工补充数据（异常才显性）
2. P0 → P1 → P2 顺序编排批次；**批内页数无上限**（批 = 优先级的自然分组，批内全并行派发、并发由 runtime 自然限流；若 Stage 1 收口编译修复负载过重，可项目级重引软上限）
3. **页面依赖不约束分批**——导航 / 嵌入目标未建一律由 FWD-REF 机制兜底，且批内无编译（统一编译在 execute §3d 收口），跨批依赖零编译代价，无需依赖排序（**不输出逐页可并行列**——批内默认全并行，单写者纪律保证）
4. **size-1 Batch 禁止**——孤页批并入**前一批**末尾（行内保留其原优先级标注；此并批不视为违反优先级单调性）

**Step 3/4/5 已并入上表**（无 per-page agent 估算——每页恒 1 converter；结算检查点每 Batch 末尾注入，批内无编译——统一编译在 execute §3d 收口）。

---

### 3b. 功能执行计划（feature-plan.md）

功能计划负责编排从 Base 层公共能力到各功能垂直切片的完整执行计划。

**生成步骤**：

**Step 1: 读取依赖图**

从 `spec/baseline/feature-index.md` 提取：
- 所有功能 ID（F-xxx）及其优先级和 V1/V2 分配
- 功能之间的依赖关系（依赖图）
- 每个功能涉及的页面和数据层组件

从 `spec/baseline/feature-base.md` 提取：
- Base 层包含的公共能力列表（Models, DB, Network, Events, Preferences, 公共组件库）

**Step 2: 拓扑排序**

对功能依赖图执行拓扑排序，确定 Feature Slices 的执行顺序：
1. 无依赖的功能 → 可以最先执行（或并行执行）
2. 有前置依赖的功能 → 排在依赖项之后
3. 检测循环依赖 → 如存在，报告错误并建议解耦方案

**多子仓项目**（存在 `module-dep-graph.json`）：先按子仓 DAG 定**子仓级**拓扑序——被依赖子仓（叶 / 底座）先行，其 Base 层与 slice 排在调用方之前；再在各子仓内对功能依赖图拓扑排序。跨子仓调用的 seam 契约以 `cross-module-contracts.md` 为权威。子仓依赖成环时退化为稳定输入序、不阻断（seam 签名已由 a2h-spec Phase 0 全量抽出，环上 slice 仍能拿到接口桩）。

**Step 3: 生成 Base 层任务列表（写入 `plans/base-plan.md`；执行序 Phase 0）**

Base 层任务是水平执行的基础设施任务，在所有 Feature Slices 之前完成。任务正文写 `plans/base-plan.md`（仅 Stage 2 消费；**只读态——无 `- [ ]` checkbox、无 `evidence:` 槽，对齐 slice 文件三铁律②，Base 完成性由 execute `base_NN_brief.md` 记录**）；feature-plan.md 索引只留 3 行 stub（任务数 + blocking 标注 + `detail:` 指针）。Base-0..7 任务清单、各任务 suggested_skills / input / blocking 的**权威 = [templates/feature-plan-template.md](./templates/feature-plan-template.md)「文件二」段**（生成时 MUST 加载，本 body 不复述）；输入来源 = feature-base.md 公共能力清单 + feature-index.md 共享组件/服务 + Base-0 的全 spec 资源 ID 全集扫描。

**Step 4: 生成 Feature Slice 任务列表**

按拓扑排序的顺序，为每个 V1 功能生成一个 Slice。每个 Slice 包含 4 个步骤：

```
Slice N: [功能名]
  │
  ├─ Step 3a: UI 补充（页面 + 嵌入子组件）
  ├─ Step 3b: ViewModel + 状态管理
  ├─ Step 3c: 数据层接入
  └─ Step 3d/3e: 页面接线 + 切片级验证（接线 → 编译 → structural_loop 同一闭环）
```

各步骤详细定义见 Section 5b。

**Step 4.0: 复杂度判定**

读取 feature spec 顶部 `complexity` 字段（由 a2h-spec Step C4-pre 写入）：

| complexity | Slice 流程 | Step 3b prompt 形态 | 校验 |
|-----------|-----------|---------------------|------|
| `simple` | 现有 4 步流程 | 仅第三段（ViewModel 实现） | — |
| `complex` | 现有 4 步流程 | **三段式**（源码理解 + 差异清单 + ViewModel 实现，见 a2h-execute §5c） | **必须含 ≥ 1 个 `android_source_anchors`**，否则 plan 输出 FAIL |
| 未标 | 按白名单关键词自动推断（同 a2h-spec Step C4-pre 规则） | — | 推断为 `complex` 时同上校验 |

`complexity=complex` 的 Slice，slice 文件写 `android_source_anchors_ref: {count: N, source: <feature spec 路径>}` 结构化残端——**不复制 anchors 列表**（权威在 spec 顶部，worker 按 grep-first 纪律定点消费）。`simple` 时可省略。

**Step 4.0b: tier / depth 调度分档**

读取 feature spec 顶部 `tier`（core/standard/peripheral）+ `depth`（full/stub）字段（a2h-spec Step C4-pre 1b 写入），决定 Slice 的**排期优先级**（与拓扑序叠加，不改变依赖约束）：

| tier / depth | 排期 | 本轮处理 |
|---|---|---|
| `core` / `full` | 拓扑序内**最先** | 完整切片 |
| `standard` / `full` | 次之 | 完整切片 |
| `peripheral` / `stub` | **延后**（排在各 parallel_group 末尾） | baseline 仅占位 AC（3–8 条）；**plan 阶段不为其预排深挖**——由 a2h-execute 在 slice 真正触及时就地升级（镜像 a2h-spec Step C4.6c），首轮不占预算 |

`tier`/`depth` 缺失（旧格式 spec）→ 一律视为 `standard`/`full`，按原拓扑序排，行为不变。

**Step 4.1: 三方 SDK 处理**

扫 feature spec 中的三方 SDK 使用（微信登录 / 穿山甲广告 / 火山埋点等），逐 SDK 四判据（按序短路）：

0. **ledger 前置**：grep `spec/decision-ledger.md`——该 SDK/能力已有 approved 决策指向**原生 / 自建替代**（ArkWeb 渲染 / 自建埋点通道 / @kit.PushKit 类）→ **归 owned task**：落对应 Slice/Base 任务 Step 行 `suggested_skills+:`（如 H5→arkts-webview），**零 registry 条目**——这是已裁决的实现工作而非延迟工作（分类法第①类）；「等 SDK 入仓」trigger 对它永远不会 fire。决策存在但未 approved 的边缘情形才登记，trigger 用白名单 `D-{N} chosen`。
1. 按 [references/skill-binding-rules.md](./references/skill-binding-rules.md) 末尾「SDK 业务类别 → HMOS 适配 skill 映射」lookup。
2. **命中**（如广告→arkts-ad）→ 写入该 slice 文件对应 Step 行 `suggested_skills+:`（§4 第③层）；不登记 registry、零条目。
3. **未命中**（自研 / 小众 / 埋点等库未覆盖）→ **直接 append `spec/placeholder-registry.md`**：P-ID（P-S{N}-{seq}）+ location + kind=thirdparty-sdk + trigger=`<业务类别> SDK 入仓` + status=registered（写入规则见 [templates/placeholder-registry-template.md](./templates/placeholder-registry-template.md)）；build-loop 按 trigger 检测命中即 resolved。

registry 是占位**唯一写入位**——slice 文件不持有占位内容，索引头 `placeholders:` 只是 registry 派生计数。已登记的 `thirdparty-sdk` 占位允许 worker 在 Step 3b/3c 中以 `// PLACEHOLDER: P-S{N}-{seq} trigger=<条件>` 形式落地代码；未登记的占位将被 converter / hard-gate FAIL（见 a2h-execute §3a、§5e）。

**Step 4.2: 接线点提取**

a2h-spec Phase C Step C4 已在 feature spec 中生成「## 对接点」段（如 `CreateOutLinePage.@Local outlineData ← AIPptViewModel`）。本 Step 把它们 lift 进 slice 文件的结构化接线账本（VM 接线与组件嵌入已统一进 `wires`）：

- `integration_points:` —— 从 feature spec「## 对接点」整段**逐条 lift**，每条 = **单行纯结构化对** `<Page>.<handler|@Local 状态> ←/→ <Target>.<member>`——零 checkbox、零 evidence 槽、零语义复述（slice 文件只读；完成性由 verify_slice_wiring 从代码机械判定，记录在组 brief）。
- `wires:` —— **统一接线账本**，两类入边都写在这里、kind 由所用字段自动区分（不手标）：
  - **VM 入边**（`page` + `viewmodel`）：哪个页面 import 并实例化哪个 ViewModel → 闭环 C1。
  - **组件嵌入入边**（`page` + `slot` + `embed` + `resolve_by`）：把父页的 `@Builder <slot>` 占位填成本切片真实子页调用（如 HomePage 的 `feedContent` 槽位填 `FeedPage()`）→ 闭环 C4；从 `ui-manifest.md` 子组件表「父页 ⊇ 子页（Tab / 嵌入）」自动推导，按子页所属 feature 归到对应 Slice。
  无人 import 的孤儿组件由 structural-closure pipeline 的 NO_IMPORTER 检测兜底。
- `modifies_files:` —— 本 Slice 需回改的**他切片所建**已存在文件清单（**本切片自建文件禁列**——自建是 generates 事实，列出即噪音）；其中 `cross_slice_edits:` 是逐条登记 `{file, handler, resolve_by}` 的跨切片子集。**embed 槽位填充不双登**：slot 填充只在 `wires` embed 条（含 resolve_by）登记，cross_slice_edits 只收非 embed 的 handler 回改（closer 步骤 1-0/1a/1b 本就按 embed ∪ cross_slice_edits 并集消费）。

提取目标的粒度为「页面 **+ 其嵌入子组件**」——必须读 ui-manifest 子组件表（Tab 内嵌 / Guide 子页），HomePage 内嵌的 Tab 子组件 handler 不得遗漏。

> **规则**：接线 / 集成工作只能走「延迟工作分类法」的 ① owned task（某 Slice 的 Step 3d）或 ② forward-ref（`kind=forward-ref` + `resolve_by`）；确属残余才走 ③ `deferred_items` 且必须带 owner。其余写法（placeholder / 自由文本 prose defer 给 a2h-fixer）一律 plan FAIL。

**Step 4.3: 数据链路契约逐层扇出（仅当 `spec/baseline/api-inventory/data-chains/chain-auth.md` 存在）**

chain-auth 是**横切**链路的逐层装配契约（L0–L7），owner 分散在多个 Base 任务与 Slice——若不主动分发，L1 隐私/启动、L7 下游这类**非网络、非登录**层会没有 execute 消费者（复盘 RC1）。本 Step 读 chain-auth **§5.1 完备性总表**，把每层扇出注入其 owner 任务，execute 照常按任务执行即消费全链、无需改动：

| chain-auth 层 | 注入的目标任务 | 该层附加的 MUST |
|---|---|---|
| L0 身份常量 | Base-1 Models / 身份任务 | 读 §5.2 L0 块取 base_url / 身份常量真值（probe 回填后） |
| **L1 隐私同意 + 门控 SDK init** | **启动 / 隐私 owning Slice** | 实现隐私门控，且门控 L2/L3 的 SDK init（附 `DEP1`） |
| L2 / L3 签名·加密·设备身份 | Base-3 Network | 读 §5.2 + `chain-auth.golden.json` 做字节对账 |
| L4–L6 凭证·登录·token | login owning Slice | 读 §5.2（token 三处同步 + 冷启再水合） |
| L7 下游 IM/推送/埋点 | 各下游 owning Slice | 软前置、懒接入，无硬 MUST |

注入方式：在对应任务（Base 任务表 / Slice 头部 YAML）加一行 `data_chain_refs: chain-auth <层>`，后接上表该层的 MUST。**字段名必须是 `data_chain_refs:`——写进 input 指针不算数**（§7 第 10 项按字段名机械校验）。**只写指针不复制值**——值单一源在 chain-auth，probe 回填后自动生效，复制会 stale。每层 owner 已由 a2h-spec §C4.7 卫生闸保证映射到真实 feature/Base，故逐层都有落点；完整性由 §7 校验兜底。

**Step 5: 标注可并行的 Slices + 组大小上限**

根据拓扑排序结果，标注哪些 Slice 可以并行执行：
- 无依赖关系的 Slices → 可并行
- 有依赖关系的 Slices → 依赖方在前，被依赖方在后
- 并行组用 `parallel_group: N` 标注

**组容量 = 组内 slice 数，上限 `GROUP_HARD_LIMIT = 5`**（小项目可放宽到 8、超大项目收紧到 3；全 complex 组可判断式收紧，不设阈值）：a2h-execute 按 parallel_group 批粒度并行，plan 期控住 group-closer 收尾负载；超出强制拆为子组（如 `parallel_group: 2` 拆成 `2a` / `2b`，各配独立 group-closer；**子组 worker 波合并并行、closer 按字母序链式串行**——拆组只为控 closer 负载，worker 互依为零；closer 禁并行：编译门全局 + 状态账本单写者）。拆分时保持「无 `depends_on` 互依」不变。**size-1 组默认禁止（消除优先于默认上限）**：先拉同层无互依 slice 并组——并组后超默认上限时**先用放宽档吸收**（小项目 ≤8；消 size-1 的优先级高于默认 5，仅超放宽档才判不可并）；不行则附挂相邻组（stub 延后者挂最末组，宿主组不得依赖它，标 `（附挂）`、不自配 closer；**附挂不计入组内 slice 数**——上限保护的是 closer 收尾负载，附挂者无 closer）；仅拓扑根类无法处置时保留，Summary 注一句理由。Step 4.0b 的「延后」不豁免本条。

**隐式关系兜底**（拓扑序只认显式 `depends_on`，两类隐式关系另补规则、确定可复现）：
- **共享容器页**（ui-manifest 类型标 `hub` / 零自有 AC 的纯 Tab 容器，如 HomePage）→ owning_slice 归**拓扑序最早、承载其任一 Tab 的切片**，**不得归更晚组**（壳须在最早 Tab 切片就建好，否则早组 Tab 无壳可填、排期倒挂）；首启弹窗等壳自有逻辑与余 Tab 一律走 cross_slice_edit / §7 嵌入归属前向填充。
- **横切切片**（无独立 UI 且多 `resolve_by` 指向它，如埋点/遥测 F010）→ 排**最末组**，不随纯拓扑入首组（其 hook 须待上游切片先产出，否则 execute 接线目标缺失）。

**Step 6: Final Verification 段注入（2 个固定任务）**

所有 Slice 后追加 `## Final Verification` 段，含两个**必填 blocking task**（缺一不可，否则 a2h-execute 缺乏可追踪 task）：

| ID | 任务 | suggested_skills | acceptance |
|---|---|---|---|
| FV-1 | **Final Structural Closure**（a2h-execute §6） | `arkts-structural-closure`（pipeline 模式） | `final_state == PASS` |
| FV-2 | 终态全量编译 | `hmos-builder` (agent) | 编译 exit 0 |

**顺序依据**：最末 group 的 closer 已编译过，结构兜底前再编译是冗余；而 FV-1 的 fix-forward / repair worker / icon-sizing 自愈**会改码**——终编译必须放在其后才兜得住可构建性。FV-2 的编译修复仅限编译级小改，**不回跑 FV-1**（避免 ping-pong）。

**FV-1 的固定文案**（模板 [feature-plan-template.md](./templates/feature-plan-template.md) `## Final Verification` 段已展开）：调用 `arkts-structural-closure` skill 的 pipeline 模式入口（`scripts/run_loop.sh --mode pipeline`），Loop 内自动跑 audit_skeletons --scope=all + 跨 Slice orphan + 沉浸式四件套；5 类 verdict 处置见该 skill 的 SKILL.md §3.3（执行前 MUST 加载）。

> **为何强制 FV-1**：a2h-execute §6 Final Structural Closure 是 Stage 3 解耦的整工程兜底（非 per-Slice），靠 Slice brief 难以追踪。在 plan 阶段把它声明为显式 blocking task，强制 a2h-execute 跑完（完成性凭据 = §6 落 loops JSON + fv brief，plan 零回填），避免遗漏。

---

## 4. suggested_skills 标注规则

根据 task 内容自动标注应使用的 Domain Skill。完整的 task→skill 主映射表（含客服 / 登录 / 支付 / 广告 / 视频 / 多设备等 30+ 领域条目）见 [references/skill-binding-rules.md](./references/skill-binding-rules.md)，标注时读。下方两表是 body 必备的 Core 决策规则。

**承载字段（三层，单一权威源）**：① Base / FV 任务 → stanza `suggested_skills:`（base-plan.md / 索引）；② Slice 4 步默认映射 → **权威 = 下表**，slice 文件零复述；③ **per-slice 差异化追加 → slice 文件对应 Step 行 `suggested_skills+:` 字段（delta-only；命名含 `suggested_skills` 词根便于检索、`+` 表增量）**——plan 期读 spec 做出的语义判断（登录→arkts-login / 支付→arkts-payment / H5→arkts-webview 等），必须落字段，不得只靠 execute runtime 兜底。

### Feature Slice 步骤的默认 suggested_skills

| Step | suggested_skills |
|------|-----------------|
| Step 3a: UI 补充 | `a2h-activity-converter` |
| Step 3b: ViewModel + 状态管理 | `arkts-state-manager` |
| Step 3c: 数据层接入 | `arkts-data-layer` |
| Step 3d/3e: 页面接线 + 切片级验证 | `arkts-state-manager` + `hmos-fix-build-errors`（closer 内编译）+ `arkts-structural-closure`（group 模式，含 size-1 组）|

当功能涉及特殊领域时，把追加 skill 写入该 slice 文件对应 Step 行的 `suggested_skills+:`（例如媒体播放功能的 Step 3c 行 `suggested_skills+: arkts-media-playback`）。

### 风格 Skills 追加

`style_set != none` 时按 task 领域从风格集选取追加（domain=ui/state/navigation/data/engineering/system 匹配表 + 选取依据见 [references/skill-binding-rules.md](./references/skill-binding-rules.md)「风格 Skills 追加」节）；`none`（含字段缺失）不追加。风格 skills 追加在 domain skills 之后（叠加而非覆盖基线）。

---

## 5. Plan 格式

### 5a. UI 转换计划格式（ui-plan.md）

完整模板见 [templates/ui-plan-template.md](./templates/ui-plan-template.md)（生成 ui-plan.md 时读）。

Core：Batch 无页数上限（批次仅由优先级切分，页面依赖不参与——FWD-REF 兜底）；无逐批 `hard_limit/actual_pages` 自声明。`owning_slice` 列填**裸 F-ID**（`^F\d{3}$` 契约——Slice↔F-ID 1:1，编号见索引），供 converter 算 forward-ref `resolve_by` + §7 归属校验消费。**Summary 不再输出 owning_slice 全量映射段**（Batch 表行内已有，第三份副本禁止）。

### 5b. 功能执行计划格式（L1 索引 + L2 slice 文件）

**MUST 加载**两个模板：[templates/feature-plan-template.md](./templates/feature-plan-template.md)（L1 索引 + base-plan.md：Context 含 `plan_format: indexed-v1` / Base 层 stub（Base-0..7 正文写 `plans/base-plan.md`，只读无 checkbox/evidence）/ slice 头部按 parallel_group `## Group N` 分节、每组末尾 `> group-closer @ GN` 插入行、每 slice 头部含 `detail:` 指针 / FV / Summary，"必填规则"段不得删减）+ [templates/slice-plan-template.md](./templates/slice-plan-template.md)（L2 slice 文件：三铁律 / `android_source_anchors_ref` / 结构化接线账本 `integration_points`·`wires`·`modifies_files`·`cross_slice_edits`（含两条降噪规则），"字段规则"段不得删减）。

索引**不含**：依赖 ASCII 树、步骤契约文本、账本内容、状态列。slice 文件由 Step 4.0–4.3 生成账本；4 步任务行只写差异化 scope + input 指针（验收契约权威在 a2h-execute §5b–5e，plan 零复述）。

---

## 6. 存储

所有 plan 存储在 `spec/baseline/plans/` 目录下；占位符注册表在 `spec/` 根目录（plan 期直写）：

```
spec/
├── placeholder-registry.md       # ← 占位唯一写入位（plan Step 4.1 直写 + 执行期铸号；execute §8b trigger 唯一读取源）
└── baseline/plans/
    ├── ui-plan.md
    ├── feature-plan.md           # L1 调度索引（plan_format: indexed-v1；Base stub + Group 分节 slice 头部）
    ├── base-plan.md              # Base 层任务正文（Step 3 写入；只读无 checkbox/evidence；仅 Stage 2 消费）
    ├── slices/                   # L2 逐 slice 只读调度账本
    │   └── slice-NN-<fid>.md
    ├── coverage-matrix.md
    └── resource-mapping.md       # ← Stage 0 资源前置产出（execute §3.0）
```

execute 阶段的过程记录（brief，落 `spec/execution/briefs/`）由 a2h-execute 启动时自建目录并填充——**plan 不创建任何执行域目录**（过程记录是执行域产物）。

---

## 7. 覆盖率校验（Plan 生成后自动执行）

Plan 生成完毕后，必须执行覆盖率校验，确保所有 V1 功能都被 plan 覆盖，并校验本次激进瘦身引入的 placeholder / complex anchor 完整性。**本节为 F-ID/页面/对接点粒度；AC 粒度的第二层对账见 §7.3**——先本节后 §7.3，两层结果都进 §8 审批摘要。

校验算法：
1. 从 `feature-index.md` 提取所有功能 ID（F-xxx）及其优先级和 V1/V2 分配
2. 从 `feature-plan.md` 所有 Slice 的功能 ID 收集已覆盖集合
3. 从 `ui-plan.md` 所有 Batch 的页面收集已覆盖的 UI 页面集合
4. 交叉比对 `ui-manifest.md` 的页面清单，确认无遗漏
5. 计算覆盖率
6. **Placeholder 完整性校验（对 registry 本体跑）**：扫 `spec/placeholder-registry.md` 全部 plan 期写入条目，逐项验证：
   - `P-ID` 是否符合 `P-S{N}-{seq}` 或 `P-B{N}-{seq}` 格式
   - `location` 是否为有效文件路径形态
   - `trigger_condition` 是否命中 [templates/placeholder-registry-template.md](./templates/placeholder-registry-template.md) 中的白名单格式（含第 6 类 `Slice {N} Step {3c|3d}`），且不含黑名单关键词
   - `kind` 必须是 `thirdparty-sdk` 或 `forward-ref`；`kind=forward-ref` 必须含 `resolve_by`
7. **Complex Slice anchor 校验（直接读 feature spec）**：对全部 `complexity: complex` 的 feature：
   - spec 顶部必须含 `android_source_anchors` 段且非空；slice 文件的 `android_source_anchors_ref.count` 与之一致
   - 每条 anchor 的 `path` 在 `$ANDROID_SRC` 下必须实际存在（逐路径 `test -f`）
   - role 必须是 a2h-spec Step C4-pre 第 2 项定义的 9 类之一（presenter/viewmodel · service/repository · controller · manager · interceptor · base_class · util · data_model · partial_class）
8. **跨切片接线归属检测**：交叉读全部 feature spec「## 对接点」段，产出全局 `(文件, handler, slot?) → owning_slice` 接线归属映射（slot 仅撞键时填，缺省退化二元键），写入 coverage-matrix `Wiring Ownership Map` 段、供 converter 算 `resolve_by`：
   - 非首切片 handler 必须在其 owning Slice 生成显式 `cross_slice_edits:` 条目 `{file, handler, slot?, resolve_by}`；**slot 填充类例外**——归属由 `wires` embed 条（含 resolve_by）体现，不入 cross_slice_edits（禁双登）
   - 校验：「## 对接点」每条都能在某 Slice 的 `integration_points` 或 `cross_slice_edits` 找到归属，无归属 → 阻断
   - **组件嵌入归属**：`ui-manifest.md` 子组件表 ∪ `ui/page_NNNN.md` 嵌入关系（两源并集），每条「父页 ⊇ 子页」须在子页 owning Slice 的 `wires:` embed 条体现（`{page(父页), slot, embed}`），任一源无归属 → 阻断
9. **骨架审计预演（plan 期静态，仅 WARN 不阻断）**：扫 registry plan 期条目 location——路径须 `<file-path>[#<anchor>]` 格式；同 .ets 文件 ≥5 个 P-ID → WARN（整页占位嫌疑，建议拆 Slice 或标 deferred）。真正骨架审计 gate 在 execute §3c
10. **数据链路层扇出校验（chain-auth.md 存在时）**：chain-auth §5.1 层清单逐层确认已被 Step 4.3 注入某任务 `data_chain_refs:`（每层 ≥1 落点）；任一层（尤 L1 隐私/启动、L7 下游）无落点 → 阻断。chain-auth 不存在（纯 UI 项目）跳过
11. **分层校验（5 项，indexed 布局专有）**：
    1. 索引条目 ↔ `plans/slices/` 文件一一对应（无孤儿文件、无缺失/悬空 `detail:` 指针；含 Base 层 stub → `plans/base-plan.md` 指针存在）
    2. slice 文件内 `spec_refs` 路径逐条存在
    3. 索引 `complexity` / `tier` 快照与 feature spec 顶部一致
    4. slice 文件零 spec 复述（行数上限启发式）
    5. 状态交叉：feature-index status=implemented 的 feature，其 owned 页不得仍 pending

<HARD-GATE>
覆盖率 / 完整率校验阈值——任一指标不达标即阻断 plan 输出：

| 指标 | 阈值 | 失败动作 |
|------|------|---------|
| P0 (V1) 功能覆盖率 | = 100% | 阻断，自动补充缺失的 Slice |
| P1 (V1) 功能覆盖率 | ≥ 80% | 警告，列出缺失项（不阻断） |
| P2 / V2 / Skip | 允许 GAP | 仅记录 |
| UI 页面覆盖率 | ui-plan ⊇ ui-manifest 全部非 skipped 页 | 阻断，补漏页 |
| Placeholder trigger 白名单率 | = 100% | 阻断（trigger_condition 不合规） |
| Complex Slice anchor 完整率 | = 100% | 阻断（缺 anchor 或路径无效） |
| 对接点归属率 | = 100% | 阻断（「## 对接点」无 Slice 归属） |
| 组件嵌入归属率 | = 100% | 阻断（ui-manifest 子组件表 ∪ page_NNNN.md 嵌入关系未在 Slice `wires:` embed 条目中体现） |
| 数据链路层扇出完整率（chain-auth 存在时） | = 100% | 阻断（§5.1 某层无 `data_chain_refs:` 落点） |
| 分层校验 5 项（校验算法第 11 项） | 全部 PASS | 阻断（索引对应 / spec_refs 存在 / 快照 / 零复述 / 状态交叉任一失败） |
| Batch 优先级单调性 + 无 size-1 批 | 批序 P0→P1→P2 单调，每页只入其优先级（ui-manifest 权威）对应批段；**size-1 批 = 0**（孤页并入前一批、行内保留原优先级，此并批不算违规） | 阻断 |
</HARD-GATE>

输出文件：`spec/baseline/plans/coverage-matrix.md`

完整模板（Summary + Feature/UI Gaps + 各校验失败表 + Full Matrix + Wiring Ownership Map）见 [templates/coverage-matrix-template.md](./templates/coverage-matrix-template.md)。

### placeholder-registry.md（plan 期直写，无导出流程）

registry 由 Step 4.1 在 plan 生成过程中**直接写入**（`spec/` 根目录），§7 第 6 项校验对其本体跑——不存在 coverage-matrix 中转与导出步骤（Full Placeholder Matrix 已废除）。行 schema、status 生命周期、kind 枚举、**写入规则**（plan 直写 / 执行期铸号登记即占号 / resolved forward-ref 行即清）见 [templates/placeholder-registry-template.md](./templates/placeholder-registry-template.md)。

---

## 7.2 grill #2 — 技术侧决策清零（HARD-GATE）

> checklist：`../a2h-spec/references/migration-decision-categories.md` C0–C17。前置：a2h-spec grill #1 已完成，`spec/decision-ledger.md` 含 D0 产出定位且状态 `approved`。

§7 覆盖率校验通过后、§8 门控之前，**立即调用 `grill-with-docs`** Skill（传技术侧类目 C6–C11/C13–C14/C17）。**HARD-GATE**：每个 `thirdparty-sdk` placeholder 必有 C8 决策、每个 complex Slice 必有 C7 决策、`api-inventory.json` 的 `uncertainties[]` 无 `open` 遗留（C17，v1.3），否则阻断。

完整调用模式 / 前置检查 / 必问 vs 自答分流 / grill 流程（含 Step 0 用户预知收集）/ HARD-GATE 校验 → **MUST 读** [references/grill-2-decision-gates.md](./references/grill-2-decision-gates.md)。

---

## 7.3 AC 级覆盖对账（强制，结果进 §8 审批摘要）

§7 的覆盖率校验是 **F-ID / 页面 / 对接点粒度**（HARD-GATE）；本节是 **AC 粒度**的第二层对账
（findings 闭环）。两层互补：**先 §7 后本节**，各跑一遍，结果都进 §8 审批摘要。

三写产物（ui-plan / base-plan / slices）生成后，写 `spec/.a2h/plan-coverage.json`，把 Spec
发布的每条 active requirement 映射到认领它的**执行单元**：

```json
{"packets": [{"packet_id": "slice-03-F001",
              "requirement_ids": ["F001-AC01", "F001-AC02"],
              "requirement_digests": {"F001-AC01": "sha256:…"}}]}
```


**packet_id 词汇钉死（本节即定义源——上游编排未定义 packet，此处定义为执行单元 ID）**：
`packet_id := slice-NN-<fid>`（逐 slice 账本）| `base-plan`（Base 层）| `FV-N`（全量验证组，如有）。
**禁止自造编号**（PKT-003 之类自由 ID）——每轮 LLM 自造编号会使跨轮 digest 对账失效。

`requirement_digests` 取自 `spec/.a2h/requirements-index.json` 的 `assertion_digest`：
Spec 之后若修改了某条 AC，只有那一条会被判 stale 并重开，不会导致整份 plan 作废。

然后跑：

```bash
python3 scripts/lint_plan_coverage.py --project-root $PROJECT_ROOT
```

- 🔴 `PLAN.REQUIREMENT_UNOWNED`：active 需求无人认领——**这就是「plan 漏掉了 AC」的检出点**，
  必须清零（纳入某 packet，或回 a2h-spec 把该 AC 标 superseded / 不适用）。
- 🔴 `PLAN.REQUIREMENT_STALE` / `PLAN.UNKNOWN_REQUIREMENT`：绑定旧断言 / 引用不存在的 ID。
- 🟡 `PLAN.DUPLICATE_OWNER`：同一需求被多个 packet 认领——指定唯一主责，避免两处各自实现。

对账结果（🔴/🟡 清单）进 **§8 审批摘要**，选项式呈报（`[1] 通过 / [2] 记为例外 / [3] 先修 / [4] 中止`）；存在 🔴 未认领需求时 [1] 不可选。

---

---

## 8. 门控

双计划 **+ grill #2** 完成后需要**人工审批**（同时审批 **plan + decision-ledger**）。审批摘要输出模板（UI/功能计划概览 + 覆盖率 + Placeholder Registry + 骨架审计预演 + **grill #2 决策清单** + briefs 落点 + 可调整项）见 [templates/gate-output-template.md](./templates/gate-output-template.md)。

审批摘要必须附 **§7.3 AC 级对账结果**（🔴 未认领清单为空才可直接确认）。用户可直接确认 / 修改后确认 → 进入 a2h-execute（execute 按 ledger 查表执行，不再交互式追问）；或要求重新生成 → a2h-plan 重新执行。

---

## 9. 触发

触发语示例：「生成执行计划」/「怎么做这个迁移」/「为 spec 生成 plan」/「拆分迁移任务」/「Spec 我看过了没问题，下一步怎么做」。触发后先检查 `spec/baseline/` 是否存在且已审批；Spec 不存在 → 提示先执行 `a2h-spec`。

---

> **Remember**：`spec/baseline/` + `ui-coverage-report.md` PASS 才生成 plan；indexed 布局唯一（索引 + slices/ 只读账本）；占位直写 registry；§7 `<HARD-GATE>` 阈值任一不达标即阻断；双计划须人工审批后才进 a2h-execute。

---

## 收尾：上报本阶段用量

本 skill 的最后一步（无论经 `$a2h-run` 还是单独触发都要做）：

```bash
.migbot/bin/a2h mark-stage a2h-plan
```

标记 `a2h-plan` 阶段水位（写 stage-marks fact + sentinel，受授权门控、尽力而为）。token 用量由生命周期 hook 上传的会话记录在服务端解析得出，本步不采集。**忽略退出码，绝不阻断。**
