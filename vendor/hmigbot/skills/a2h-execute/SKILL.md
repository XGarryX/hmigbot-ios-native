---
name: a2h-execute
description: Android→ArkTS 迁移代码的三阶段执行引擎（Pipeline 第三步）：按 ui-plan.md/feature-plan.md 派发 subagent 完成页面转换、基础设施、功能切片，含编译闭环。当用户说"执行迁移""开始执行""按 plan 开始做"时触发，支持部分执行/重试/断点续跑。不要用于：生成 Spec（用 a2h-spec）或计划（用 a2h-plan）；plan 未就绪时先跑 a2h-plan。
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

# a2h-execute

## 启动检查 — 待办 findings

读 `spec/.a2h/open-findings.json`（不存在 = 首轮，直接开工）：

| 情况 | 行动 |
|---|---|
| 有 `owner_stage: execute` 的条目 | 先处理这些，再做本轮正常工作；处理完重跑 `scripts/lint_execute_coverage.py` 确认消失 |
| 有 `owner_stage` 属**上游阶段**且 `severity: blocking` 的条目 | 🔴 **拒绝开工**，列出条目并提示用户回到该阶段（a2h-spec / a2h-plan） |
| 条目标记 `escalate: true`（同一问题连续 3 轮） | 🔴 停止自动重试，按 a2h-spec `templates/decision-card.md` §连续未收敛 出决策卡 |
| 本阶段 section 标记 `halted`（进度停滞 3 轮 / 累计 10 轮） | 🔴 **停止修复尝试**，按 decision-card §连续未收敛 出决策卡；用户裁决后 `--clear-halt <决策ID>` 解除，再继续 |
| 无条目 | ✅ 正常开工 |

路由不靠猜：每个 linter 比对两份产物，**哪一侧缺条目就由哪一侧负责**。责任无法机械判定时
（典型：AC 按当前描述实现不了），用决策卡上报，由用户指定 owner——选项与 owner 的对应关系
写死在卡里，避免推诿。

**findings 只能由「原 linter 重跑后不再报」来关闭**，不能由任何一方声明「已修复」而关闭。

## 关键约束（Critical）

- **执行铁律**：execute 按 `spec/decision-ledger.md` 查表推进、**不交互式追问**；未命中 → fail-fast 写「决策缺口」段并阻断，由下一轮 grill 补齐。启动先 Read 项目指令文件（宿主别名 `PROJECT_INSTRUCTIONS_FILE`：Codex=项目根 `AGENTS.md` / Codex=项目根 `AGENTS.md`）+ ledger 顶部「决策索引」段（status 须 `approved`；正文按需 grep D-编号，不整份吞全文）。
- **Stage 0 资源前置最先跑**（§3.0，HARD-GATE）：全部 `$r(...)` 引用可解析或显式 MISSING_xxx 才进 Stage 1。
- **合法占位 = 已登记的 5 类 kind 占位**（§2.1）：命中规范 marker（`// FWD-REF:` / `// PLACEHOLDER:` / 已登记 `// TODO:` / 资源 `[TODO: translate]`）**且** registry 6 字段齐全；未登记 / 自由文本（裸 `// TODO`、空回调、空 try-catch、假 `console.info('TODO')`、prose defer）一律 FAIL。§2.1 列 4 大延迟**归属**类，其中 placeholder 一类内部再细分 5 类 kind。
- **共享文件单写者纪律**（Stage 1 §3b / Stage 3 §5a）：并发 converter / slice worker **只写自身 page/VM/repository 文件**，共享文件禁碰（`feature-plan.md` 等 plan 产物、跨文件接线），**仅两项 append-only 例外**——① `placeholder-registry.md` 登记行 append（§2.1c 发号协议）② 共享资源 JSON 直写（写前 Read + 只 append 缺失键，纪律见 `_common.md`）；跨文件接线与状态账本回写一律由 **Batch 收尾 subagent** / **group-closer** 唯一作者（账本变更经 **writeback manifest** 由主线程 `apply_writeback.py` 落盘，§3b 协议），收尾者对资源只做**残量兜底 + 只读校验**（冲突由编译门自曝）。
- **编译闭环**：Stage 3 group 的组编译在**收尾 subagent 内部**调 `hmos-fix-build-errors`；**Stage 1 批内无编译**（页面间零编译依赖，统一 single-pass 在 §3d 收口，真编译门 = Base-7）；Stage 2 Base-7（§4d）/ Stage 3 Step 3a 建页 / §3d 收口 / FV-2 终态全量编译（§6 之后）派发 Codex 子代理 `hmos-builder`（定义于 `.codex/agents/hmos-builder.toml`），Base-7 失败阻断后续全部 Slice。**主线程禁止直接调底层 build skill**（Batch/group 收尾是 subagent，不算主线程）。
- **结构性验证 = `$arkts-structural-closure` skill（参数：`mode=<stage|group|pipeline> target=<...>`）**（§3c stage / §5e group（含 size-1 组）/ §6 pipeline）：**禁止 grep / 自跑 scripts 替代**。中间步骤看 skill 返回的 verdict 即可；**§6 收尾 evidence 必产 brief 文件**，缺失不允许进 a2h-verify。
- **接线完成性机械判定**（§5e 配套）：plan 产物（索引 + slice 文件）只读、零回填——完成性由 verify_slice_wiring.py C2 按结构化对从代码直接判定（调用方页面存在 + handler 已接 + target 被实例化，孤儿 VM 防线不变；完整契约见 §9a）。
- **References / Templates 强制加载**（HARD-GATE）：body 中所有 `[references/X.md]` / `[templates/Y.md]` 引用，在对应步骤执行时**必须** Read 被引文件作为执行规范，不得仅靠 body 摘要执行（占位禁令 / FWD-REF 规则不得简化）。**派发 prompt 已按段拆分**：`references/agent-prompts/` 下 `1-converter.md` … `8-group-closer.md` 每个是对应派发点的完整模板，派发时 **Read 对应单段文件 + `agent-prompts/_common.md`（公共占位规则）即可**——**不要整份加载所有段**（旧单文件 413 行已废，索引见 `references/agent-prompts.md`）。跳过加载 = PROCESS_VIOLATION。规则适用于 LLM 主线程和派发的 subagent。

---

## 1. 定位

Pipeline 层第三步，**三阶段执行引擎**。读取 a2h-plan 生成的双计划（ui-plan.md + feature-plan.md），按三阶段顺序执行迁移。

```
a2h-spec → a2h-plan → a2h-execute（本 skill）
                          │
                          ├─ Stage 1: UI Pipeline
                          │   └─ a2h-activity-converter agent × N 页面
                          │
                          ├─ Stage 2: Feature Base
                          │   └─ a2h-migration-worker × Base 任务
                          │
                          └─ Stage 3: Feature Slices（按 parallel_group 批粒度）
                              └─ 组内 slice worker 并行 → group-closer（接线+编译+结构 fix-forward+brief）→ 主线程仅处置冒泡
```

**核心原则**：a2h-execute 是编排层，不实现任何迁移逻辑。所有实际工作通过 subagent 委托：Stage 1 使用 `a2h-activity-converter` agent，Stage 2/3 使用 `a2h-migration-worker` agent。

---

## 1.1 执行铁律 — 决策来源与禁止交互

execute 期歧义已清零，本阶段只**按决策推进、不再交互式追问**。事实源 = `spec/decision-ledger.md`。遇范围 / 技术替代 / UX 行为差异 / 工程配置 / 数据策略类判断、或与 plan/spec 冲突、或既有段落写有「提示用户三选一 / 除非用户指定 blocking / 要求人工补 plan」等交互动作时，**必先 grep ledger 对应类目**：命中 → 按之执行**严禁询问**；**未命中 → fail-fast**，把缺口写入 `spec/migration-report.md`「决策缺口」段、**严禁交互式追问**；ledger 与他文档冲突 → ledger 优先。
完整 HARD-GATE 规则 + **启动必读**（先 Read 项目指令文件 `PROJECT_INSTRUCTIONS_FILE` + `decision-ledger.md` 决策索引段，校验 `status=approved`，正文按需 grep）+ 决策缺口 schema + 与各段落关系表 → **MUST READ** [references/execution-discipline.md](./references/execution-discipline.md)。

---

## 2. 输入

自动读取 `spec/baseline/plans/` 下已审批的双计划文件：

| 文件 | 用途 | 消费阶段 |
|------|------|---------|
| `spec/baseline/plans/ui-plan.md` | UI 转换计划：按批次分组的页面列表 | Stage 1 |
| `spec/baseline/plans/feature-plan.md` | **L1 调度索引**（`plan_format: indexed-v1`）：Base 层 stub + 按 Group 分节的 slice 头部（每组末尾 group-closer 插入行）+ detail 指针；主线程只读索引 | Stage 3 |
| `spec/baseline/plans/base-plan.md` | **Base 层任务正文**（索引 stub 的 detail 指向处；旧 plan 无此文件时回退读 feature-plan.md 旧 Phase 0 段） | Stage 2 |
| `spec/baseline/plans/slices/slice-NN-<fid>.md` | **L2 逐 slice 只读调度账本**（接线账本）；**worker 派发直接给文件路径，不读索引** | Stage 3 |

启动时检查：
- `spec/baseline/plans/` 目录是否存在
- `ui-plan.md` 和 `feature-plan.md` 是否存在
- 如果不存在或为空 → 提示用户先执行 `a2h-plan`
- feature-plan.md 无 `plan_format: indexed-v1` / slice 段无 `detail:` 指针（旧 monolith）→ **阻断**，提示重跑 a2h-plan 升级布局（执行进度存于 ui-manifest / feature-index / brief，重排零损失）
- 启动时创建 `spec/execution/{briefs, source-understanding}` 目录——执行域过程记录落点，由 execute 拥有（brief = 阶段小结，旧称 handoff；SESSION-HANDOFF / `// HANDOFF:` 责任移交 marker 不受此改名影响）
- **contract_mode 检查**：若存在 `spec/.a2h/pipeline-state.json`，读其 `contract_mode`（`legacy|shadow|v2`）；文件或字段缺失 → 按 `legacy` 运行（即现行为）。`spec/.a2h/` 下存在其他 v2 残留文件**不改变行为、不作为输入**（mode 只认 pipeline-state.json 显式声明）。**例外**：evidence-coverage 家族（`open-findings.json` / `requirements-index.json` / `plan-coverage.json` / `impl-claims.json` / `verification.json`）**独立于 contract_mode 始终生效**，不属本条「残留」范围

辅助文件（执行过程中读取）：

| 文件 | 用途                                               |
|------|--------------------------------------------------|
| `spec/baseline/ui-manifest.md` | 页面状态追踪（pending/converted/verified）               |
| `spec/baseline/feature-base.md` | Base 层公共能力定义                                     |
| `spec/baseline/features/F-xxx.md` | 各功能详细 Spec（complex 的 AC 带二型锚点：`源→标` parity / `决→标` 平台差异，worker 一律以 `标` 定位实现落点；`决:` 锚的行为契约查 decision-ledger） |
| `spec/baseline/ui/page_NNNN.md` | 各页面详细 UI Spec                                    |
| `spec/placeholder-registry.md` | 占位符注册表                                           |
| `spec/baseline/cross-module-contracts.md` | 多子仓专有：跨模块 seam 语义契约，跨子仓调用的权威依据                   |
| `spec/baseline/resolved-theme.json` | 主题层机械真值（resolve_theme.py 产）——theme_brief 注入与 theme_gate 对账的唯一来源；缺席=主题闸无事可对账 | 可选 |
| `spec/baseline/module-dep-graph.json` | 多子仓专有：被依赖子仓的接口签名桩                                |

---

## 2.1 延迟 / 待接工作分类法（贯穿全 Stage）

| 类别 | 适用                                                           | 归属机制                                                             | 闭环 gate                                                                 |
|---|--------------------------------------------------------------|------------------------------------------------------------------|-------------------------------------------------------------------------|
| ① **owned task** | 接线 / 集成工作（**首选**）                                            | 某 Slice 的 Step 3d/3e 页面接线                                        | Step 3d/3e 接线闭环维度（§5e）                                                  |
| ② **placeholder** | 指定后续 Slice 的代码桩 / 三方 SDK / 资源占位 / 不确定区域                      | placeholder-registry 5 类 `kind` 枚举                               | trigger_condition 满足 → resolved（§5e / §6） |
| ③ **deferred_item** | 既非 owned task 又非占位的**残余**（如 `module.json5` 配置、需另一 skill 的工作） | brief `deferred_items` 结构化字段 `{描述, owner_skill, 闭环条件, status}` | 非空且无 owner → Slice `BLOCKED`（§5e）                                       |
| ④ **自由文本「已知不完整」** | ——                                                           | ——                                                               | **禁止**——§3c 骨架审计扫到「由 verify / fixer / 后续接通 / a2h-fixer 完成」等措辞即 FAIL |

**marker 形态约定**（一切 marker 必先登记 registry 6 字段，未登记一律 FAIL）：

- `// FWD-REF: <P-ID> resolve_by=...` — `kind ∈ {forward-ref, resource-pending-asset}`；`// PLACEHOLDER: <P-ID> trigger=...` — `kind = thirdparty-sdk`（两者**不含 `TODO` 字样**）
- `// TODO: <description>` — `kind = forward-ref-uncertain`；`console.info('TODO:<ACTION>:<COMPONENT>')` — component-builder L3 签名占位专用
- 资源 JSON `"value": "[TODO: translate] ..."` — `kind=resource-pending-translation`
- 未登记 TODO / 空回调 / 空 try-catch / 未注册 `[TODO: ...]` → FAIL

---

## 3.0 Stage 0: 资源前置（HARD-GATE，必须最先执行）

**env-prewarm（与 Stage 0 并行，后台 1 个 subagent）**：Stage 0 起跑的同时派发，一次完成 ① env-doctor（read-first 只补缺：local.properties 已有有效 `hwsdk.dir` 即跳过）② 依赖解析（ohpm install / hvigorw --sync）③ daemon 预热（assembleHap）——细则复用 `hmos-fix-build-errors` 环境段。**预热构建结果丢弃：不 gate、不修复、不记录 `[fire-and-forget]`**（join_gate 静态 allowlist 已豁免此句柄）（与 Stage 0 资源写并行可能产生假编译错，无视）。此后全程禁冷启，首编（§3d 收口 single-pass）即热 daemon。

完整流程 **MUST 加载** [references/stage-0-resources.md](./references/stage-0-resources.md)。

调 `android2hmos-resources-convert` → 全部 `$r(...)` 引用可解析或显式 `MISSING_xxx` → 自动派 `arkts-i18n` skill 处理 `[TODO: translate]` 占位 → 自动派 `arkts-app-identity`（`scope=dev-identity`）落地 app_name / versionName / 图标（**跳过 bundleName / vendor**，属部署期 D-009、与签名 / AGC 强绑定）→ HARD-GATE 通过后进 Stage 1。

---

## 3. Stage 1: UI Pipeline

> **前置依赖**：Stage 0 必须 PASS。`ui-plan.md` 中所有 `$r(...)` 引用在本阶段开始前应可解析或显式 MISSING。

Stage 1 读取 `ui-plan.md`，按批次调用 `a2h-activity-converter` agent 将 Android 页面转换为 ArkTS。

**执行流程**：读 `ui-plan.md`，逐 Batch 执行：**批内页面默认全并行**派 `a2h-activity-converter` agent（单写者纪律各写各文件，导航目标未建由 FWD-REF 兜，无需逐页并行标注）→ 等本批全部完成 → 派发**批收尾 subagent（§3b：资源 sweep → writeback manifest，无编译，单写者）** → 下一 Batch，直到所有 Batch 完成；末尾 §3d 统一收口。

### 3a-pre. 数据完整性预检查（Stage 1 每页派发前）

对当前 Batch 每个待转换页面做三源数据完整性预检（meta.json × view.xml 状态 → enrich / 合成 / scaffold+Phase A 三模式）。判定表 + 两段 `synthesize_*.py` 脚本调用方式 **MUST 加载** [references/data-prep.md](./references/data-prep.md)（Batch 级批量执行、可并行合成）。

### 3a. 子代理派发方式（Stage 1 专用）

Stage 1 使用 `a2h-activity-converter` agent（**不是** a2h-migration-worker）。

每页用子代理派发，传入五参数 `activity_name` / `ui_info`（ui-snapshots 目录，含 view.xml + meta.json）/ `harmony_project_dir` / `references_dir`（android-ui-graph-query/references/）/ `android_source_dir`，外加 `android_source_anchors`（page spec 顶部）、`registered_placeholders`（按本页 `owning_slice` 前缀 grep `spec/placeholder-registry.md` 所得已登记占位）、`wiring_ownership_map`（coverage-matrix）。converter 消费三源数据：view.xml（运行时层级）+ meta.json（页面元数据）+ 源码 layout XML（样式，经 `setContentView` 定位）。

完整 converter prompt **MUST 加载** [references/agent-prompts/1-converter.md](./references/agent-prompts/1-converter.md) + [_common.md](./references/agent-prompts/_common.md) 作为派发模板（占位禁令 / `// FWD-REF:` marker 规则 / forward-ref 与 SDK 占位的合法形式等**不得简化为本 body 摘要**）。该 step 的 HARD-GATE 验收：

- stub 命中 → 必须读 `android_source_anchors` 指向的源文件再生成；anchor 缺失 / 读取失败 → **FAIL，禁止 placeholderCard 占位**。
- 合法占位遵循 §2.1：converter 可产 4 类——`// FWD-REF:`（forward-ref，自行发现，**写 marker 前先按 §2.1c 登记 registry**）/ registry 已登记的 `// PLACEHOLDER:`（thirdparty-sdk，plan 期直写）/ fallback 资产 `// FWD-REF:`（resource-pending-asset）/ 已登记 `// TODO:`（forward-ref-uncertain）；未登记 TODO / 空回调 / 假 console.info / 空 try-catch 一律 FAIL（完整定义见 agent-prompts/1-converter.md）。
- 返回报告 `failed_stubs`（stub 无法展开清单，与编译无关——converter 禁止自行编译）必须为空才 PASS。

**批内并行**：批内页面默认全并行派发（页面依赖不约束分批——导航 / 嵌入目标未建由 FWD-REF 兜底；批内单写者保证互不阻塞）；每批所有子代理全部完成后执行该批收尾结算（§3b，无编译）。

### 3a-bis. 入口页 Navigation 装配 + 注册 + Hello World 剔除（ONE-TIME，HARD-GATE）

Stage 1 **全部 Batch 完成后**（§3d 收口第一步）一次性执行：① 入口页加入 `main_pages.json` 并同步改 `EntryAbility.loadContent('pages/{MainPage}')` → ② 入口页装配 `Navigation` 外壳 + `@Builder pageMap` 路由表（届时所有 NavDestination struct 已存在，一次定稿）→ ③ **HARD-GATE**：剔除 DevEco Hello World 模板——grep `Index.ets` 命中默认模板特征则三联清理（编译验证并入 §3d single-pass，不单独派发）。

**关键不变量**：`main_pages.json` 的 `"src"` 最终**只保留入口页一项**——NavDestination 子页面由入口页 `pageMap` 路由，不逐页登记（Navigation 模型与旧 router 模型的关键差异）。

完整分步流程（grep 特征 / 三联清理 / 字段读取来源 / Navigation 外壳模板）**MUST 加载** [references/entry-navigation-setup.md](./references/entry-navigation-setup.md)。

### 3b. Batch 收尾 subagent（per-Batch, HARD-GATE）

本批所有并发 converter 完成后，派**一个**Batch 收尾 subagent（**`a2h-closer`，mode=batch**——收尾协议单源固化于 agent 定义；派发参数模板 **MUST 加载** [references/agent-prompts/2-batch-closer.md](./references/agent-prompts/2-batch-closer.md) + [_common.md](./references/agent-prompts/_common.md)）。该 subagent 是本批 **brief 与账本变更的唯一作者 + 资源残量兜底者**（converter 已按 `_common.md` 直写纪律 append 资源键；收尾只补漏不重写），依次串行两步（**批内无编译**——页面间零编译依赖，统一编译在 §3d 收口）：

1. **资源 sweep（残量兜底，只读校验为主）**：grep 本批生成/改动的 .ets 全部静态 `$r('app.<type>.<name>')` 引用（**完整性来自 grep 穷举，不依赖 converter 申报**），与 `resources/` 比对解析性 → 仍缺失的（converter 直写漏网），调 `android2hmos-resources-convert` 扫 Android 源补齐 → 仍无源写 `MISSING_xxx`（复用 Stage 0 契约）。
2. **产 writeback manifest**：本批页 `pending → converted` 记入 manifest（结算即翻——converted = 转换产出完成，编译验证在 verified 轴）；起草 batch brief 全文（schema 见 [references/brief-schemas.md §1](./references/brief-schemas.md)，只写结构化字段）+ 账本翻转集合，一次写 `spec/execution/writeback/writeback-batch-NN.json`（schema：brief-schemas §4）后 return——closer turn 内**不直写** brief / 账本。

**域巡检波（批/组收口后无条件，与后续施工并行）**：`apply_writeback` 成功时会**直接打印本批的巡检派发指令**（agent/task_name/考卷/落单路径）——照打印的指令立即执行，这不是可选建议；凭证缺失会被 binding_gate 的 patrol-receipt 检查判 FAIL。协议全文按 [references/patrol-routing.md](./references/patrol-routing.md) 路由表**立即后台派发**域巡检 agent（考卷=writeback 文件闭集+安卓真值锚点；派发模板 MUST 加载 [agent-prompts/9-patrol.md](./references/agent-prompts/9-patrol.md)）。巡检只读、与施工零竞态；**join 硬点=本批 converted→verified 翻转前**；findings→1 轮修复→机械闸复验→清零才翻 verified，未清记债转 FV 审计段，流水线不等；悬挂句柄按 join 协议条款②处置。设计依据与墙钟分析（全并行，暴露仅末批尾巴）见 patrol-routing.md。

**writeback 协议（四模式通用，§4e/§5e/§6 同此）**：closer 返回后主线程跑 `python <a2h-execute>/scripts/apply_writeback.py <manifest> --project-root .`——确定性落盘 brief + 翻账本（registry / ui-manifest / feature-index），幂等可重放；**崩溃恢复 = manifest 在则重跑 apply，绝不重做接线/编译/结构**。closer 仍是全部账本变更与 brief 的**唯一作者**，脚本只是落盘手。

**HARD-GATE**：writeback manifest 必产 + apply 成功才进入下一 Batch（**批间无编译门**）；缺失 → 阻断。

### 3c. 骨架审计 gate

Stage 编译 PASS 后**调用 `$arkts-structural-closure` skill（参数：`mode=stage target=<1|2|3>`）** 做骨架兜底。绝大多数情况 0 findings 直接 PASS；CONTINUE 时按 dispatch_prompt 派 repair worker 修后重调，≤ 2 轮仍 CONTINUE → BLOCKED。

Stage 3 末尾自动启用 L4.dangling-fwd-ref 检测。


### 3d. Stage 1 完成标志

所有 Batch 执行完毕后，顺序收口：① **§3a-bis 入口装配** → ② **§3c 骨架审计 gate**（扫描范围 = Stage 1 起点以来 git diff 改动的 .ets + 全部 `batch_NN_brief.md`；FAIL 阻断）→ ③ **single-pass 编译**：派发 Codex 子代理 `hmos-builder`（定义于 `.codex/agents/hmos-builder.toml`；CALLER=a2h-execute, STAGE_HINT=stage-1-close，**限 1 轮**：build 一趟分类——undefined Base 符号 = 预期跳过不追修；parse / 语法 / 资源 JSON 语法 = 真错必修或标记。skeleton 容忍保险丝，真编译门 = Base-7）→ ④ 输出 Stage 1 统计（总页面 / 成功 converted / 失败需人工 / single-pass 真错数）。

---

## 4. Stage 2: Feature Base（水平基础设施）

> **前置依赖**：Stage 0 资源前置已完成。Base-0 已上移至 §3.0 Stage 0，本阶段直接从 Base-1 开始。

Stage 2 读取 `plans/base-plan.md`（索引 Base 层 stub 的 `detail:` 指向处）的 Base 层任务（Base-1..Base-7），按顺序执行公共基础设施建设。旧 plan 无 base-plan.md → 回退读 feature-plan.md 旧 Phase 0 段（兼容层）。

### 4a. 执行流程

读 `plans/base-plan.md`，按顺序串行派发 `a2h-migration-worker`：Base-1 Models → Base-2 Database → Base-3 Network → Base-4 Events → Base-5 Preferences → Base-6 公共组件库 → Base-7 编译验证。Base-0 已在 Stage 0 完成，跳过。

### 4b. 子代理派发方式（Stage 2/3 通用）

Stage 2 和 Stage 3 的 **codegen worker** 统一使用 `a2h-migration-worker`；各级**收尾**统一使用 `a2h-closer`（mode=batch/base/group/final，§3b/§4e/§5a/§6）：

完整通用 worker prompt **MUST 加载** [references/agent-prompts/3-worker.md](./references/agent-prompts/3-worker.md) + [_common.md](./references/agent-prompts/_common.md) 作为派发模板（占位禁令 / FWD-REF marker 规则等**不得简化为 body 摘要**）。**派发 prompt 禁复述** agent 定义 / _common.md 已载纪律（单写者 / 占位禁令 / 信封等）——一行指针即可、稳定内容走 MUST-Read 通道；但**任务专属 scope（锚点 / 契约差异 / 文件清单）不得省略**——瘦身只砍跨派发不变内容。占位 / 前向引用规则：合法占位遵循 §2.1（已登记的 5 类 kind）；worker 阶段常用——Base signature 桩登记 `kind=forward-ref` + `resolve_by=Slice {N} Step 3c`；**skill 库未覆盖的三方 SDK** 登记 `kind=thirdparty-sdk` + `trigger=<业务类别> SDK 入仓`（已有适配 skill 的 SDK 直接走 task suggested_skills，不进 registry）；fallback 资产登记 `kind=resource-pending-asset`。每个占位 6 字段齐全；未登记 TODO / 假 console.info / 空回调一律禁止。

### 4c. Base 层任务详情

任务内容与 `suggested_skills` 的权威 = `plans/base-plan.md` 各任务 stanza（本 body 不复述）。执行须知两条：**Base-6 公共组件库**是 Stage 3 全部 UI 工作的样式锚点（Design Tokens + 原子/复合组件，Stage 3 必须引用）；**Base-7** 派 子代理 hmos-builder（CALLER=a2h-execute, STAGE_HINT=stage-2-base-7）。

### 4d. 编译检查点（per-phase）

> 编译派发 + placeholder 回填完整流程与**构建操作纪律**（cache / checkpoint / CLI→IDE 降级）**MUST 加载** [references/build-loop.md](./references/build-loop.md)——纪律注入所有构建 subagent 的派发 prompt。

Base 层所有任务完成后（Base-7）：

1. **派发 Codex 子代理 `hmos-builder`（定义于 `.codex/agents/hmos-builder.toml`）**（CALLER=a2h-execute, STAGE_HINT=stage-2-base-7, ROUND=1，最多 20 轮自动修复）
2. agent 返回 BUILD_STATUS=PASS → **执行 §3c 骨架审计 gate**（扫描范围 = Stage 2 git diff 改动的 .ets + 全部 `base_NN_brief.md`，重点抓 Base signature 桩 `throw ...'Slice N'`）；FAIL 则阻断进入 Stage 3
3. 骨架审计通过 → Stage 2 完成，进入 Stage 3
4. agent 返回 BUILD_STATUS=FAIL → 阻断（Base 层是所有 Slice 的前置依赖），把 REMAINING_ERRORS 写入 `base_NN_brief.md` 的 evidence 段

### 4e. Base Task brief（HARD-GATE）

> Stage 2 各 Base 任务（Base-1..Base-7）完成后也强制产 brief（与 §3b Batch brief 对称），便于跨 session 中断恢复与 placeholder 状态追溯。

每个 Base 任务（Base-1..Base-7）完成后，派 **`a2h-closer`（mode=base）** 核对产出并**强制**产 writeback manifest（brief 全文在内，主线程 apply 落盘 `spec/execution/briefs/base_NN_brief.md`——writeback 协议同 §3b）。

<HARD-GATE>
manifest 不产 / apply 未过 → 不允许进入下一个 Base 任务；Base-7 (编译验证) brief 未 PASS → 阻断 Stage 3 启动。

**brief schema 模板 + 字段读取来源**见 [references/brief-schemas.md § 2. Base Task brief](./references/brief-schemas.md)。段：`generated_files` / `modified_files` / `unresolved_placeholders` / `evidence` / `next_dependency`。
</HARD-GATE>

### 4f. Stage 2 完成标志

输出 Stage 2 统计（Base 任务 7 项成功/失败计数 / 公共组件库组件数 / 编译状态——FAIL 阻断）。

**产 `spec/execution/base-contracts.md`（as-built 接口摘要，一页内）**：主线程从各 base brief `generated_files` + 关键导出汇总——Base 各任务实际落盘的类名 / 公开 API / 常量 / 组件名。Stage 3 全部 worker 派发**传此指针、禁内联 Base 契约正文**（agent 读一次即前缀缓存命中；Base 冻结后基本不 stale）。

---

## 5. Stage 3: Feature Slices（垂直切片）

Stage 3 读取 `feature-plan.md` 的 Slice 任务，按拓扑排序逐功能执行。每个 Slice 内部有 4 个步骤（3a/3b/3c + 3d/3e 接线验证合一）。

### 5a. 执行流程

读 `feature-plan.md` **索引**拓扑排序后的 Slice 列表（主线程只读索引头部——账本在 slice 文件，worker 派发直接给 `detail:` 指向的文件路径），**按 `parallel_group` 批粒度编排**（组间拓扑串行，组内并行；类比 Stage 1 Batch 的「并发产出 + 单写者收尾」）。每个 parallel_group 三步：

1. **组内 worker 派发（每 slice 恒 1 个 worker + 长杆先行）**：组内按 pages_owned **降序**派发——最长链路最早开跑；每个 slice worker 跑 Step 3a/3b/3c + **自身页内**接线。**安全阀（判断式，默认不拆）**：编排者判断某 slice 明显过大（页数 / 锚点异常多）→ 可按**依赖断面**拆 2~3 个 worker（如 VM/model 层 ∥ service+接线层），文件集不相交、各自报信封，closer 照常收口；**禁止按 Step 3b/3c/3d 逐步拆 subagent**（步骤横切丢上下文、不买墙钟）。
   - 所有 worker 只写自身 scope 文件，禁碰共享文件（单写者纪律、两项 append-only 例外与 plan 产物只读契约见 agent-prompts/_common.md）。
   - 派发 prompt 附 `Base 契约: spec/execution/base-contracts.md`（§4f as-built 摘要）**指针，禁内联契约正文**。
2. **group-closer（单写者，1 个）**：本组 worker 全部完成后，派一个 group-closer（**`a2h-closer`，mode=group**——五步协议单源固化于 agent 定义；派发参数模板 **MUST 加载** [references/agent-prompts/8-group-closer.md](./references/agent-prompts/8-group-closer.md) + [_common.md](./references/agent-prompts/_common.md)；**末组**——索引 FV 前最后一个 Group——追加参数 `defer_structural_to_fv: true`，其结构验证由紧随的 FV-1 全工程扫描覆盖、免一次重复 group 扫描，中间组禁用）：跨文件接线（各 slice 的 cross_slice_edits + HomePage embed wires；registry 状态变更记 writeback manifest，plan 产物零回填）→ 资源 sweep → **1 次** compile-fix loop（`hmos-fix-build-errors`，≤20 轮）→ **结构 fix-forward**（自调 `mode=group` + 自修 ≤3 轮直到 CONVERGED，非收敛才冒泡）→ 产 writeback manifest（group brief 全文 + 账本变更集合，主线程 apply 落盘，协议同 §3b）。
3. **主线程仅处置冒泡**：结构验证（`mode=group`）已合入 group-closer 自身 fix-forward（§5e）；主线程**只在 closer 回传 escalation（STALLED/REGRESSED/EXHAUSTED）时**介入——按 dispatch_prompt 派专家 repair worker（feat→worker / ui→converter） / 标 BLOCKED。

**编排规则**：
- **组容量约束**（计数口径与上限的权威 = a2h-plan Step 5，此处不复述）：plan 已据此拆分 parallel_group；execute 遇超限组或多 complex 情况可进一步拆分。plan 标注**附挂**的孤立 slice 搭宿主组的编译与验证。
- **组间 `depends_on`**：group N 的 group-closer 把共享文件定稿 + brief PASS 后，group N+1 才启动。
- **同族子组（同数字前缀，如 2a/2b）**：worker 波**合并一波并行派发**（拆组只为控 closer 负载，互依为零由 plan 拆分规则保证）；closer 按字母序**链式串行**（C2a → C2b，编译门全局 + 账本单写者，禁并行）。
- **group 内仅 1 个 slice** → 退化为「1 worker + 1 closer（=该 slice 编译+接线+brief）」。
- **`depends_on` 就绪校验**：组启动前读上游组 group brief 对应 slice 小节，其 §5e 接线闭环维度必须 PASS。

> **降级**：若某组共享文件耦合过紧、不宜并行，把该组**拆成按拓扑序串行的 size-1 组**——每组仍是「1 worker + 1 closer」，协议与执行者完全不变。group 编排是唯一执行路径，降级只改组的拆分粒度，不引入第二条协议。

**depth=stub feature 的按需升级**：派 slice worker 前先看该 feature spec 顶部 `depth` 字段。`depth: stub`（tier=peripheral，baseline 仅 3–8 条占位 AC）的 feature 在本 slice 真正执行时**就地升级**——补齐 standard 档深度（锚定覆盖率 ≥30%、穷举分支/常量/专属类 AC，对齐 a2h-spec Step C4.6c），更新该 feature spec 与 `source-coverage-report.md` 后再派 worker；**不回 a2h-spec 全量重跑**。`depth: full` 或字段缺失 → 直接执行，无需升级。

### 5b. Step 3a: UI 补充

主线程按 ui-manifest 中目标页面（**+ 子组件表内嵌子组件**）的 status 分支调度：

| status | 处置 |
|---|---|
| `converted` | 确认 .ets 存在，**不跳过 Slice**（接线移交 Step 3d——整体跳过是孤儿 VM 根因之一） |
| `pending` / 不在 ui-plan | ui-snapshots 存在 → 调 a2h-activity-converter；缺失 → 触发 §7 Phase A 按需模式；转换后 status→converted + 派 hmos-builder（STAGE_HINT=stage-3-slice-{name}）验证 |
| `verified` | 跳过 |

UI 补充必须引用 Base-6 公共组件库（Design Tokens + 共享组件）。worker 同时承担 `forward-ref-uncertain` 二次审视（返回 `uncertain_regions_resolved[]/retained[]`，主线程据此更新 registry）——完整流程与占位禁令 **MUST 加载** [references/agent-prompts/4-step3a-ui.md](./references/agent-prompts/4-step3a-ui.md) + [_common.md](./references/agent-prompts/_common.md) 作为派发模板，不得简化为 body 摘要。

### 5c. Step 3b: ViewModel + 状态管理（C7 三段式）

<HARD-GATE>
生成本切片 ViewModel。**complex 强制三段式**（源码理解 → 差异清单 → 实现，一次调用），simple 仅第三段；**anchors 经 `android_source_anchors_ref.source` 读 spec**（grep-first 定点消费，不整读源文件）；spec 已有『源码 5-role 摘要』时第一段只核对 + 产差异清单，source-notes.md 仅含差异清单；complex 必产 `spec/execution/source-understanding/{slice}-source-notes.md`。三段各自的判据（9-role 摘要含类名否则 FAIL / 二型锚点 `源:`·`决:` 落点规则 / `[真机]` 不豁免实现）**MUST 加载** [references/agent-prompts/5-step3b-vm.md](./references/agent-prompts/5-step3b-vm.md) + [_common.md](./references/agent-prompts/_common.md) 作为派发模板，不得简化为 body 摘要。
</HARD-GATE>

### 5d. Step 3c: 数据层接入

<HARD-GATE>
为该功能切片创建 Repository / Service、连接数据源，数据流 UI ← ViewModel ← Repository ← API/DB 闭环。完整任务清单（complex 的 source-notes 对齐 / impl: 指针精读 / **多子仓契约约束**）**MUST 加载** [references/agent-prompts/6-step3c-data.md](./references/agent-prompts/6-step3c-data.md) + [_common.md](./references/agent-prompts/_common.md) 作为派发模板，不得简化为 body 摘要。worker 报告的「决策缺口」由主线程按 §1.1 阻断。
</HARD-GATE>

### 5e. Step 3d 接线 + 3e 验证 + Slice brief（per-group，HARD-GATE）

> 3a/3b/3c（§5b/5c/5d）由组内 slice worker 跑；**3d 接线 + 资源 sweep + 1 次编译 + 3e 结构验证 + brief** 由本组 group-closer 统一收尾。**任意组大小同一协议**——size-1 组（串行降级 / 重试单 slice / 只执行 Slice N）同样适用。

<HARD-GATE>

**执行者（单一路径）**：slice worker 只做**自身页内** 3d 接线（MUST READ [agent-prompts/7-step3d-wiring.md](./references/agent-prompts/7-step3d-wiring.md) + [_common.md](./references/agent-prompts/_common.md)）；**跨文件 3d 接线 + 资源 sweep + 1 次编译 + 3e 结构 fix-forward + 组单文件 group brief 全部由 group-closer（`a2h-closer` mode=group）一手做完**（五步协议在 agent 定义；派发参数模板 [agent-prompts/8-group-closer.md](./references/agent-prompts/8-group-closer.md)）。**主线程仅在 closer 回传 escalation（STALLED/REGRESSED/EXHAUSTED）时介入**：派专家 repair worker（feat→worker / ui→converter）+ git rollback / 标 BLOCKED。

**不变契约（缺一即该 slice 标 BLOCKED、不 retry）**：
1. **3d 接线**：补 import + 实例化 ViewModel、grep `// FWD-REF:` marker 逐个换真实调用。**slice 文件只读，零回填**——接线完成性由 `verify_slice_wiring` C2 按结构化对从代码机械判定（调用方页面存在 + handler 已接 + target 被实例化）；`resolve_by=本 slice` 的 forward-ref 必须全解除（marker 消失 + 真实实现存在）。
2. **3e CONVERGED 后非 loop 校验**：本 slice 前缀（grep registry `P-S{N}-`）的每个占位 P-ID 有对应 marker + registry 6 字段 + trigger 白名单；complex slice 必有 `spec/execution/source-understanding/<slice>-source-notes.md`（差异清单）；`deferred_items` 每条含 `owner_skill` + 闭环条件。STALLED/REGRESSED/EXHAUSTED 处置见 `arkts-structural-closure` SKILL.md §3.3。
3. **Writeback manifest 必产**（`spec/execution/writeback/writeback-group-NN.json`，brief_content 含本组全部 slice 小节；schema MUST READ [brief-schemas.md §3/§4](./references/brief-schemas.md)；主线程 apply 落盘 brief——旧 per-slice `slice_NN_brief.md` 为 legacy 兜底，脚本双形态解析）
全契约 PASS → manifest 记 brief `final_state: PASS` + 页面 `converted → verified`（`ui_manifest.verified`）+ **feature `pending → implemented`**（`feature_index.implemented`）+ **收组清行集合**（`registry.resolve`——apply 删 kind=forward-ref 行，历史留 brief；残留 marker 由 dangling-fwd-ref Class 1 兜底）→ 主线程 **apply 成功**（writeback 协议同 §3b）→ 进下一 group/slice。

</HARD-GATE>

### 5f. Stage 3 完成标志

Stage 3 所有 Slice 执行完毕 + §3c 一次性骨架审计通过后，输出统计（Slice 总数成功/失败 / verified 页面数 / 编译状态），然后进入 **主题收货闸**（`python3 <a2h-execute>/scripts/theme_gate.py --project <工程根>`：机械对账 resolved-theme 条目 ⊆ 产物绑定——色值未绑定/硬编码 hex/Button 形状落回胶囊/**必填回执键缺失**（闭集由 resolved-theme 推导，回执按页分片在 `spec/execution/theme-receipts/`）→ FAIL，派 1 轮修复后复跑，仍 FAIL → BLOCKED 记入报告；无 resolved-theme.json = 无事可对账，不阻塞。该闸已收编为 arkts-structural-closure pipeline 模式的必需 detector（`theme`），§6 FV-1 会再机械跑一遍并计入完成度闸——漏跑即 INCOMPLETE，不依赖本段散文被遵守）→ **字面量收货闸**（`python3 <a2h-execute>/scripts/literal_gate.py --project <工程根>`：spec 字面量 ⊆ 产物字面量的包含性对账——真值源 `spec/baseline/literal-ledger.json`（a2h-spec extract_literals.py 产）；页面级文案/色号缺失 FAIL、改写嫌疑与 ref 级缺失 WARN、尺寸/时长出覆盖率报表；无 ledger 不阻塞）→ **死壳检测**（`python3 <a2h-execute>/scripts/dead_shell_gate.py --project <工程根>`：视觉驱动变量零赋值=dead-driver FAIL（能编译能渲染但运行时死的那类）、@Param 默认值恒生效=WARN）。→ **载体降级检测**（`python3 <a2h-execute>/scripts/carrier_gate.py --project <工程根>`：spec 自定义弹窗/Toast 声明 vs 产物系统件使用——downgrade/mixed-usage/toast-systemized 全 WARN 报表级，由人核销或写 decision，不阻断）→ **交互命中闸**（`python3 <a2h-execute>/scripts/hit_test_gate.py --project <工程根>`：**无条件字面**或**显示时**（`visible ? Block : None`）`HitTestMode.Block` 挂在含交互子节点的容器 → FAIL——鸿蒙 Block 阻塞**子节点**触摸测试，弹窗按钮永久无响应（2026-08-26 实锤 18 弹窗 32 处全失灵；**2026-08-29 二次实锤**：条件形态曾被整类豁免，`ConfirmDialog` 一处 `visible ? Block : None` 让 6 个弹窗按钮全死、fixer 连修 5 轮落空）；**隐藏时** Block／纯遮罩／叶子组件合法不报）→ **资源名闭集闸**（`python3 <a2h-execute>/scripts/resource_name_gate.py --project <工程根>`：按名取资源（getStringByNameSync/getRawFileContent 等，含一跳包装函数传播）的字面名必须存在于全工程 resources 闭集；缺席且未登记（无 FWD-REF/P-ID、spec 债务面无此名）= 静默缺席 FAIL——注入槽无供值形态（AIPPT 实锤：aiPptAppId 资源从未创建、异常吞成 '' → AI 链路全部出网前即死且账面全绿）；缺席但已登记 / 计算名 = WARN）。五闸同样已收编为 pipeline 必需 detector（`literal`/`deadshell`/`carrier`/`hittest`/`resname`）→ **§6 Final Structural Closure（FV-1）→ FV-2 终态全量编译** → **冷启冒烟探针**（设备在线时：`bash <a2h-execute>/scripts/cold_start_probe.sh <bundleName>`，主判据=首个网络请求出网+不 crash，FAIL 按装配缺陷回修；无设备 → 探针 exit 3，记 `unverified-cold-start` 粘性债交 a2h-verify 门控）→ a2h-verify。

---

## 6. Final Structural Closure（Stage 3 全部完成后 HARD-GATE）

<HARD-GATE>
Stage 3 全部 group brief 落地 + §5f 统计输出后，派 **`a2h-closer`（mode=final）**——其内部**调用 `$arkts-structural-closure` skill（参数：`mode=pipeline target=final`）** 跑整工程兜底（与 Stage 3 解耦，独立一次性 loop），CONVERGED 后产 `writeback-final.json`（收尾 brief 全文 + defer 末组补翻集合，主线程 apply 落盘，协议同 §3b）。

> ⚠️ **禁止用 grep 替代**

**收尾 evidence（缺失或 `final_state ≠ PASS` → 不允许进 a2h-verify）**：

- `spec/execution/autofix-log/round-<R>/loops-final-structural-closure.json` — `final_state == PASS`（arkts-structural-closure finalize 产出）
- `spec/execution/briefs/final_structural_closure_brief.md` — 嵌入 loops.pipeline 段

CONVERGED + evidence 就位 → FV-1 完成。CONTINUE 按 dispatch_prompt 派 repair worker（feat → `a2h-migration-worker` / ui → `a2h-activity-converter`）后重调；其他 verdict 处置见 skill 自身 SKILL.md §3.3。

**FV-2 终态全量编译**：FV-1 通过后（其 fix-forward / repair / icon-sizing 自愈可能改码），派发 Codex 子代理 `hmos-builder`（定义于 `.codex/agents/hmos-builder.toml`；CALLER=a2h-execute, STAGE_HINT=fv-final-build，≤20 轮）确认可构建无回归——这是进 a2h-verify 前的最后 gate。**必须为真实构建**：`all tasks up-to-date` 秒级空转不构成 PASS 证据，命中则 touch 入口文件或动用本轮唯一 clean 强制重编（中间 closer 保持增量，发布门较真）。编译修复仅限编译级小改，**不回跑 FV-1**。

</HARD-GATE>

---

## 7. Phase A 按需触发机制

Stage 3 Step 3a 发现目标页面 ui-snapshots 数据缺失（status 非 converted/verified **且** `ui-snapshots/page_NNNN/` 缺失或不完整）→ 自动触发 a2h-spec Phase A 按需模式：单页源码分析 → 最小数据集 → 增量更新 ui-manifest + page spec → 继续 converter，不中断 Pipeline。完整触发条件 / 流程 / 降级处理（无静态 layout 时骨架 + registry 占位）**MUST 加载** [references/phase-a-ondemand.md](./references/phase-a-ondemand.md)。

---

## 8. Skill 绑定机制

### 8a. 主路径：plan 标注（三层承载）

- **Base / FV 任务**：读 base-plan.md / 索引 stanza 的 `suggested_skills:`。
- **Slice 4 步默认映射**：3a=`a2h-activity-converter` / 3b=`arkts-state-manager` / 3c=`arkts-data-layer` / 3d=closer 链（权威在 a2h-plan §4 表 + agent-prompts 模板绑定，plan 不复述）。
- **Slice 差异化增量**：slice 文件 Step 行 `suggested_skills+:` 字段（plan 期语义判断的确定性产出）——**必须并入派发**。

### 8b. 覆盖 / 注入 / 降级

派发前 runtime 上下文检查可**覆盖** plan 建议（触发词追加表：动画/视频/网络救火/knowledge-verifier 等）、按 `style_set` **注入**风格 skills、对不存在的 skill **降级**（语义匹配→migration tag 优先→无增强执行）。原则：**只升级不降级**——不得移除 plan 已建议的 skill（缺失降级除外），覆盖发生时记录进迁移报告覆盖记录表。完整覆盖表 / 注入逻辑 / 降级流程 **MUST 加载** [references/skill-binding-override.md](./references/skill-binding-override.md)。

---

## 9. 状态追踪与完成性契约

### 9a. 机械完成性契约（plan 零回填）

**plan 产物（索引 + slice 文件）生成后只读**——execute 不在其中打 `[x]`、不回填 evidence。完成事实的凭据分两层：

- **接线完成性**：`verify_slice_wiring.py` C2 按 slice 文件的结构化对（page.handler ← Target）**直接从代码机械判定**——调用方页面存在 + handler 已在页面接线 + target 被调用方实例化（`new` / `getInstance` / typed field / render call）。**孤儿 VM 根因防线不变**：VM 存在 ≠ 被接上，判定对象始终是调用方。
- **过程记录**：每 slice 的完成事实（final_state / deferred_items / 未解占位 / pages_verified）写入 brief；Base/FV 等索引 task 的 evidence 仍按 brief 记录（build log / loops JSON 路径）。

### 9b. 页面状态生命周期（ui-manifest.md）

`pending → converted → verified`：

| 状态 | 含义 | 更新时机 |
|------|------|---------|
| `pending` | 待转换 | Spec 生成时 |
| `converted` | UI 转换产出完成（编译验证在 verified 轴） | Stage 1 批结算 / Stage 3 Step 3a 后 |
| `verified` | 功能验证通过（ViewModel + 数据层 + 接线闭环） | Stage 3 Step 3d/3e 通过后 |

### 9c. feature 状态生命周期（feature-index.md 状态列——feature 级产物状态唯一账本）

`pending → implemented → verified`：

| 状态 | 含义 | 写者与时机 |
|------|------|---------|
| `pending` | slice 未完成 | Spec 生成时初始值 |
| `implemented` | slice brief `final_state: PASS` | **group-closer 记入 writeback manifest，主线程 apply 翻**（与 ui-manifest 页面回写同 manifest，§5e） |
| `verified` | FV-1 + FV-2 通过 | FV 收尾时批量翻（a2h-verify 逐 feature 细化为开放项） |

**读者**：§11 部分执行 / resume 按它判断哪些 slice 已完成（slice:feature 1:1）；gate 摘要与 a2h-verify 范围选择按它分支。**交叉护栏**：feature=implemented 时其 owned 页不得仍 pending（structural closure / a2h-plan §7 校验）。

---

## 10. 迁移报告

<HARD-GATE>
所有 Stage 与 §6 Final Structural Closure 执行完毕后生成 `spec/migration-report.md`。

**报告完整模板**见 [templates/migration-report-template.md](./templates/migration-report-template.md)。含：总览 / Stage 1 详情（+页面转换清单）/ Stage 2 详情 / Stage 3 详情 / Skill 使用统计 / 覆盖记录 / 产出文件清单 / FAILED 列表 / 页面状态汇总 / 最终编译 / Final Structural Closure（§6 收尾，取自 `loops-final-structural-closure.json` + brief）。

</HARD-GATE>

---

## 11. 触发 / 部分执行

- **完整执行**：「执行迁移」/「开始执行」/「Plan 我看过了没问题，开始执行」
- **部分执行**：「只执行 Stage 1」/「从 Stage 2 开始」/「只执行 Slice 3」/「只执行 Stage 1 的 Batch 2」
- **重试与继续**：「重试 FAILED 的 slice」/「继续执行（从上次中断的地方继续）」

自然语言触发时，a2h-execute 会列出待执行的 Stage 和任务数量，确认后开始执行。

### 11a. 部分执行的实现

| 用户指令 | 行为 |
|---------|------|
| "只执行 Stage 1" | 只读 ui-plan.md，只执行页面转换批次 |
| "只执行 Stage 2" | 只读 plans/base-plan.md（旧 plan 回退 feature-plan.md 旧 Phase 0 段） |
| "只执行 Stage 3" | 只读 feature-plan.md 的 Slice 列表（前提：Stage 2 已完成） |
| "从 Stage 2 开始" | 跳过 Stage 1，从 Base 层开始执行 |
| "重试 FAILED 的 slice" | 扫描迁移报告中的 FAILED slice，每个按 **size-1 组**重跑（1 worker + 1 closer） |
| "只执行 Slice N" | 把该 Slice 作为 **size-1 组**执行其 4 步（前提：其依赖已完成） |
| "继续执行"（resume） | **读 feature-index 状态列**判定已完成 slice（implemented/verified 跳过；slice:feature 1:1），从首个 pending 的 parallel_group 续跑；组内细节看该组 brief |

---

> **Remember**：结构性验证唯一入口 = `$arkts-structural-closure` skill，禁止 grep / 自跑 scripts 替代；中间步骤看 verdict 即可，§6 收尾必产 `loops-final-structural-closure.json` (PASS) + brief md；Stage 0 资源前置最先跑；plan 产物只读、接线完成性由 verify_slice_wiring 机械判定；跨文件接线与状态账本由 Batch 收尾 / group-closer 单写；资源 JSON / registry 是 worker 的两项 append-only 例外（直写纪律 + 发号协议见 `_common.md`），收尾者只做资源残量兜底；合法占位 = 已登记的 5 类 kind 占位（§2.1），未登记 / 自由文本一律 FAIL；execute 按 §1.1 铁律查 decision-ledger 推进、不交互式追问（未命中写「决策缺口」阻断）。

---

## 收尾 — 实现认领（强制，写者协议对齐 §3b writeback 单写者纪律）

**谁写 `impl-claims.json`：没有随机写者。** 账本唯一作者 = closer，唯一落盘手 = `apply_writeback.py`
——与 registry / ui-manifest / feature-index 同一条纪律：

1. 并发 worker **不直写**本账本，也无需逐 AC 汇报——认领由 closer **从 plan-coverage.json 机械
   派生**（该 packet 的 requirement_ids + requirement_digests 即认领集合；实现文件 = 单元产出
   清单，symbols 可选增补）——与「账本变更 100% 可从结果推导」同一原则；
2. 各收口 closer 在单元达完成条件时（group = 该 slice `final_state: PASS`；base-plan / FV-N /
   defer-to-FV 残余 = mode:final 补记）写入 writeback manifest 的 **`impl_claims` 段**
   （schema：brief-schemas §4，与 feature_index.implemented 同守双前置）；
3. 主线程跑 `apply_writeback.py` 统一落盘 `spec/.a2h/impl-claims.json`——append 语义、幂等可重放
   （同 `(requirement_id, packet_id, attempt)` 不重复；崩溃恢复 = 重跑 apply）。

manifest `impl_claims` 段形态：

```json
"impl_claims": {"claims": [{"requirement_id": "F001-AC01", "packet_id": "slice-03-F001",
                            "files": ["entry/src/main/ets/…/HomeCreateComponent.ets"],
                            "symbols": ["HomeCreateComponent.changeItem"],
                            "requirement_digest": "sha256:…", "attempt": 1}],
                "executed_packets": ["slice-03-F001"]}
```

`packet_id` 词汇与 plan §7.3 同源钉死：`slice-NN-<fid> | base-plan | FV-N`，**禁止自造编号**。

每个阶段收口（batch / group / slice 的 apply 成功后）跑：

```bash
python3 scripts/lint_execute_coverage.py --project-root $PROJECT_ROOT
```

- 🔴 `EXECUTE.REQUIREMENT_UNCLAIMED`：执行单元已收口但该需求无任何实现认领——**这就是
  「execute 跳过了 AC」的检出点**。确实无法按现描述实现时，用决策卡上报由用户指定 owner，
  不要静默跳过。
- 🔴 `EXECUTE.CLAIM_STALE`：AC 在 Spec 侧已变更，认领绑定的是旧断言。
- 🟡 `EXECUTE.DUPLICATE_IMPLEMENTATION`：同一需求被多个不同符号认领——**同一业务行为只保留
  一个主实现**，其余改为调用它；两套实现会让后续每次修改都要先判断运行时走哪条路。

---

## 收尾：上报本阶段用量

本 skill 的最后一步（无论经 `$a2h-run` 还是单独触发都要做）：

```bash
.migbot/bin/a2h mark-stage a2h-execute
```

标记 `a2h-execute` 阶段水位（写 stage-marks fact + sentinel，受授权门控、尽力而为）。token 用量由生命周期 hook 上传的会话记录在服务端解析得出，本步不采集。**忽略退出码，绝不阻断。**

---
