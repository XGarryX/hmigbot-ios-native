---
name: a2h-execute
description: "iOS→HarmonyOS 迁移第三步（Execute，四拍执行引擎）：读 a2h-plan 冻结的 indexed 计划与 plan IR（plan-understand.json / plan-domains.json），next-batch 取批 → 按任务书派 a2h-ios-converter/a2h-migration-worker/a2h-closer、hmos-builder → 同路径 ios-receipt v2 回执 → land-results 落账，循环至 done；把 Swift/ObjC、SwiftUI/UIKit 源行为落成 ArkTS 目标代码，资源前置/UI Pipeline/Feature Base/Feature Slices 与结构、编译闭环均在其中收口。当用户说“执行迁移”“开始执行”“按 plan 开始做”“继续执行”时触发，支持 --wave understand|domains 与重试/断点/换会话续跑部分执行。不要用于：生成 Spec（用 a2h-spec）、排计划（用 a2h-plan）、验证产出（用 a2h-verify）；spec/plan 未就绪时先跑 a2h-spec/a2h-plan。"
metadata:
  type: pipeline
  domain: migration
  tags:
  - ios
  - execute
  - migration
  layer: pipeline
---

本统一版本先读 [单一流程、环境前置与兼容范围](../a2h-run/references/unified-workflow.md)；其中明确的写入、准备时机和行为范围规则优先于下文的旧调用示例。


> **派发约定**：本 skill 在四拍循环中**派发 subagent 执行任务书**（Stage 1 converter=`a2h-ios-converter`；Stage 2/3 worker=`a2h-migration-worker`；各级收尾=`a2h-closer`（mode=batch/base/group/final）；编译=`hmos-builder`）。按本轮授权读取随包角色规程、使用宿主实际支持的派发/等待接口，**不照抄不存在的 agent_type 参数**；具名角色不可用时按同样文件所有权顺序在主会话自行执行，写同样回执，不另造计划。派发变体只由 batch 元素与派发点模板决定，主会话零开放决策。
>
> **Join 协议（收口五条款）**：① **循环 wait**：完成的唯一合法信号 = 代理完成状态，绝不是产物文件存在/条数（文件会中途落盘，读半截=事故）；② **死句柄与验收**：超时后核对句柄，可探产物活性；已 completed 且摘要可读 → 消费；completed≠验收通过，join 点跑门禁验产物（v2 由 `land-results` 落账门禁验真，FAIL 视同未取回）；③ **收口锚点**：最终报告前必须收口全部句柄；④ **放行≠遗弃**：非阻塞放行只推迟收口时机，不豁免收口义务；⑤ **fire-and-forget**：仅正文显式声明“结果丢弃、不 gate”的派发（如 Stage 0 env-prewarm）免收口。
>
> **派发纪律**：`task_name` 唯一（带 page-id/slice-id/round-N 后缀）；并行派发前写预期产物清单供 join 对账（契约只认派发方、不认子代理自报）；**谁派谁收**——sub-agent 禁止嵌套外派后自行退出；**契约产物必须出自承担任务的子代理**：重派上限后仍产不出 → 如实报缺停在未完成态，禁止代写占位产物让门禁转绿。
>
> **路径约定**：`$IOS_SRC` 从 `<target>/.migbot/config.json` 的 `ios` 字段读取；`<target>` = 鸿蒙目标工程根；`<runtime>` = 本包 runtime（`scripts/a2h_ios.py` 所在根，命令统一写成 `python <runtime>/scripts/a2h_ios.py <cmd> …`）。产物一律落 `<target>/spec/`（禁落会话临时目录）：计划 IR `spec/waves/plan-<wave>.json`、任务书 `spec/waves/prompts/<wave>/`、回执 `spec/waves/results/<wave>/`、控制账本 `spec/state/`、过程记录 `spec/execution/`。

# a2h-execute — 三阶段执行引擎（四拍循环）

## 0. 定位与纪律

- **前置**：`<target>/.migbot/config.json` 存在且 `source_platform=ios`；a2h-plan 已产出冻结计划（`spec/baseline/plans/{ui-plan,feature-plan}.md` 与 `spec/waves/plan-<wave>.json`）且通过 `plan-check`。缺配置 → 先 a2h-init；缺计划 → 回 a2h-plan，**不代跑上游**。
- **输入**：冻结计划（indexed ui-plan/feature-plan/base-plan/slices + plan IR）、`spec/baseline/` 规格、`spec/decision-ledger.md`（已批准决策）、`spec/placeholder-registry.md`。
- **输出**：落账状态（`spec/state/` 三账）、`spec/execution/` 过程记录（brief/writeback/autofix-log）、产物 ArkTS 代码与资源、`spec/baseline/impl-claims.json`、派生报告（`spec/summary`/`spec/migration-report.md`）。**契约定稿归 a2h-spec/a2h-plan**——本 skill 不请示、不改业务预期。
- **唯一交互点 = 新产品决策**：执行按已批准 decision-ledger 推进，未命中/冲突回流写「决策缺口」阻断受影响任务；仅**新的不可推断产品决策**用决策卡呈报用户，其余禁交互追问（`references/execution-discipline.md` 规定 D-ID 定点读与缺口 schema）。阶段门沿用已有授权，不重复索取阶段批准。
- **无人值守**：停点由脚本裁决留痕；`gates.unattended: true` 时脚手架自动批复（`workflow-params.json` 缺省 `unattended: false`）。门禁 FAIL 一律按 E266 处置阶梯（见 §2）。
- **第一条可见输出必须是**一行阶段计划（四拍启动 → Stage 0 → Stage 1 → Stage 2 → Stage 3 → FV → 派生汇总 → 交接），然后才执行 §1。
- **exit code 语义**（随包命令逐条列明，不套用统一 0/1/2）：一般 `0=PASS/有动作`，`2=FAIL/用法错/契约违规`（`MigrationError` 统一走 2）；`build` 为 `0=build_passed / 1=未通过`；`behavior-check` 为 `0=PASS / 3=UNVERIFIED / 2=FAIL`；`next-batch`/`land-results` 为 `0=有动作/落账完成 / 2=契约违规或升级`。
- **单写者分区**（主会话与 worker 一律不得手改下列控制账本，越权即 PROCESS_VIOLATION）：

| 文件 | 唯一写者 | 内容 |
|---|---|---|
| `spec/state/state.json` | 原版 `state_update.py`（plan-ir/land-results 经 subprocess 调用） | 任务/门禁状态账本 |
| `spec/state/dispatch.json` | 原版 `next_batch.py` | 已吐批次记录（防重派） |
| `spec/state/journal.json` | 原版 `land_results.py` | `workflow_status[]` + `operation_outputs[]` |
| `spec/placeholder-registry.md` / `spec/baseline/ui-manifest.md` / `spec/baseline/feature-index.md` / `spec/.a2h/impl-claims.json` | `apply_writeback.py`（唯一落盘手；变更由 a2h-closer 写进 writeback manifest） | 占位登记与页面/功能状态 |

- 恢复与已有基线：先读 `spec/.a2h/open-findings.json`（findings 只能由产生它的检查重跑后关闭，不能整文件重写成空）；已冻结计划不会自动重写，续跑前对源变更与已落账范围显式重排（§2 replan）。

## 1. 启动检查 — 待办 findings

读 `spec/.a2h/open-findings.json`（不存在 = 首轮，直接开工）：

| 情况 | 行动 |
|---|---|
| 有 `owner_stage: execute` 的条目 | 先处理这些，再做本轮正常工作；处理完重跑 `scripts/lint_execute_coverage.py` 确认消失 |
| 有 `owner_stage` 属**上游阶段**且 `severity: blocking` 的条目 | 🔴 **拒绝开工**，列出条目并提示用户回到该阶段（a2h-spec / a2h-plan） |
| 条目标记 `escalate: true`（同一问题连续 3 轮） | 🔴 停止自动重试，按 a2h-spec `templates/decision-card.md` §连续未收敛 出决策卡 |
| 本阶段 section 标记 `halted`（进度停滞 3 轮 / 累计 10 轮） | 🔴 **停止修复尝试**，按 decision-card §连续未收敛 出决策卡；用户裁决后 `--clear-halt <决策ID>` 解除 |
| 无条目 | ✅ 正常开工 |

路由不靠猜：每个 linter 比对两份产物，**哪一侧缺条目就由哪一侧负责**。责任无法机械判定时（典型：AC 按当前描述实现不了），用决策卡上报，由用户指定 owner。**findings 只能由「原 linter 重跑后不再报」关闭**，不能由任一方声明「已修复」关闭。

## 2. 四拍循环与命令表（本文件的全部剧本）

**控制面入口（harness v2）**：先读取 `../ios-source-analysis/references/harness-v2.md`，以该协议决定输入、机器门禁与状态写者。v2 项目执行四拍——**这是唯一的调度循环**：

```
① 取批  python <runtime>/scripts/a2h_ios.py next-batch --project <target> --wave <wave>
② 派发  按返回任务书执行（支持 subagent 则派发对应角色，否则主会话按同一任务书顺序执行）
③ 回执  任务产出同一路径 ios-receipt v2（source_sha256/plan_sha256/task_id/ac_ids/file_hashes 必须真实）
④ 落账  python <runtime>/scripts/a2h_ios.py land-results --project <target> --wave <wave>
```

每次 `land-results` 成功后**立即**执行 §11 的派生汇总与一致性检查（部分执行同样执行），随后进入下一批或阶段门。旧正文 Stage 0/1/2/3 是任务内实施细则，**不再作为第二调度循环**。`done` 仅表示代码任务已落账；源合同错误**不能记债务放行**，随后继续真实结构与编译门。

**核心命令表**（flags 经 `--help` 核对，不得虚构）：

| 命令 | 用途 | 关键 flags | exit code 语义 | FAIL 处置 |
|---|---|---|---|---|
| `plan-check` | 只校验 plan 请求（validate_only，不生成） | `--project`、`--input <typed-plan.json>`（必填） | 0=PASS，2=FAIL | 读错误修请求重跑，≤2 轮；仍 FAIL → blocked，保留恢复条件（E266） |
| `plan-ir` | 生成并冻结 plan IR（blueprint/plan/prompts/contracts） | `--project`、`--input`（必填） | 0=生成完成，2=FAIL（契约/门禁不通过） | 同上；existing plan 不可变，用 replan |
| `next-batch` | 拍①取批（含冻结输入/围栏/源/图校验） | `--project`、`--wave`（缺省 `domains`）、`--usage-ledger <path>` + `--usage-run-id`（派发前用量门） | 0=有动作，2=契约违规/升级/失败 | 按 `action` 处置（下表） |
| `land-results` | 拍④落账（验回执、越权文件、摘要、findings） | `--project`、`--wave` | 0=落账完成，2=有 blocked/escalate/失败落账 | 按 `action` + `landed[]` 处置 |
| `replan` | 显式重排：归档旧控制面，不继承旧成功 | `--project`、`--input`（含 `replan_review.reviewer/reason`） | 0=成功，2=FAIL | 读错误（在途未落账/源变更/门禁）修后重跑 |
| `recover-blocked` | 显式终止唯一在途 blocked attempt（严格 review v1 对象） | `--project`、`--review <review.json>` | 0=终止记录归档，2=FAIL | 仅支持 attempt 1；字段不符保守拒绝，交人工审计 |
| `build` | 真实构建（产出 build evidence，独立于两源根） | `--project` | 0=`build_passed`，1=未通过 | 读 `evidence` 路径回读真实报告；修复后重跑 |
| `behavior-check` | 行为链校验（默认只查链路） | `--project`、`--run`（才执行声明命令） | 0=PASS，3=UNVERIFIED，2=FAIL | UNVERIFIED 保留未验范围，不伪造 PASS |

辅助：`resolve --source <source> --anchor <anchor>`（0=OK / 3=AMBIGUOUS / 2=MISS）用于解析源锚点，不参与门禁裁决。

**拍①后按 `action` 分派（除本表动作外主会话无任何开放决策）**：

| action | 主会话动作 |
|---|---|
| `dispatch` | 拍②：并行派发 batch 全部任务；batch 元素 = `{id, agent(role@version), prompt_file, result_path, resume_key, model}`；**任务书正文不进主会话上下文**，prompt 原文照发 |
| `wait` | 存在 DISPATCHED 未落账（`missing[]` 列明）→ 任一代理回执到达即跑拍④，**禁止等整批全部回来才落账**；代理已终止却无 result → 改判缺失 |
| `done` | 本 wave 任务已落账；读 `escalate`/`next` 字段照走，交接由脚本给指令，不再散文交棒 |
| `escalate` | 门禁升级/重试超限 → 呈报升级材料，按根因修后 `replan`，**禁归档重建账本**；输出带 `hint` 时照 hint 走 |

- `next-batch`/`land-results` **exit 2 = 契约违规**（典型：plan `contract_hash` 与 state 不一致 / 源快照变化 / 任务的冻结输入被改）→ 停，契约变更**必须显式走 replan + 部分重跑**，禁改 state/blueprint 硬闯。
- **无人值守处置阶梯（E266）**：FAIL → 按 `retry_hint` 派修复并重跑同一命令，**最多 2 轮**；仍不过或无可执行修复时保留失败、修复记录与恢复条件，依赖失败输入的部分保持 **blocked**，独立工作可继续。源合同、静态、冻结输入与本阶段硬门必须重跑PASS；仅设备/账号缺失按对应规则保留未执行，不升级为成功。重试超限不能改控制账本或降低门禁，产品取舍不能由模型自行批准。
- **主会话不得修改产品文件（`entry/**`）与 skill/脚本自身**；脚本报错（exit 2 / traceback / 解不开的契约违规）= 停机呈报，按材料等用户裁决，**不得热改脚本/数据绕过**。

## 3. Stage 0：资源前置（HARD-GATE，必须最先执行）

**env-prewarm（与 Stage 0 并行，后台 1 个 subagent）**：Stage 0 起跑的同时派发，一次完成 ① env-doctor（read-first 只补缺：local.properties 已有有效 `hwsdk.dir` 即跳过）② 依赖解析（ohpm install / hvigorw --sync）③ daemon 预热（assembleHap）——细则复用 `hmos-fix-build-errors` 环境段。**预热构建结果丢弃：不 gate、不修复、不记录 `[fire-and-forget]`**（与 Stage 0 资源写并行可能产生假编译错，无视）。此后全程禁冷启。

完整流程 **MUST 加载** [references/stage-0-resources.md](./references/stage-0-resources.md)。

调 `ios-resources-convert` → 全部 `$r(...)` 引用可解析或显式 `MISSING_xxx` → 自动派 `arkts-i18n` skill 处理 `[TODO: translate]` 占位 → 自动派 `arkts-app-identity`（`scope=dev-identity`）落地 app_name / versionName / 图标（**跳过 bundleName / vendor**，属部署期，与签名 / AGC 强绑定）→ HARD-GATE 通过后进 Stage 1。

## 4. Stage 1：UI Pipeline

> **前置依赖**：Stage 0 必须 PASS。`ui-plan.md` 中所有 `$r(...)` 引用在本阶段开始前应可解析或显式 MISSING。

Stage 1 读取 `ui-plan.md`，按批次调用 `a2h-ios-converter` agent 将 iOS 页面转换为 ArkTS。

**执行流程**：读 `ui-plan.md`，逐 Batch 执行：**批内页面默认全并行**派 `a2h-ios-converter` agent（单写者纪律各写各文件，导航目标未建由 FWD-REF 兜，无需逐页并行标注）→ 等本批全部完成 → 派发**批收尾 subagent（§4b：资源 sweep → writeback manifest，无编译，单写者）** → 下一 Batch，直到所有 Batch 完成；末尾 §4d 统一收口。

### 4a-pre. 数据完整性预检查（Stage 1 每页派发前）

必读 references/data-prep.md，核对 iOS 源锚点、native facts、page spec、meta 与源版本。

### 4a. 子代理派发方式（Stage 1 专用）

按 references/agent-prompts/1-converter.md 传 page_id、source_root、page_spec、ui_info、target、所有权与占位信息，使用 `ios-ui-to-arkui`。Stage 1 使用 `a2h-ios-converter` agent（**不是** a2h-migration-worker）。

完整 converter prompt **MUST 加载** [references/agent-prompts/1-converter.md](./references/agent-prompts/1-converter.md) + [_common.md](./references/agent-prompts/_common.md) 作为派发模板（占位禁令 / `// FWD-REF:` marker 规则 / forward-ref 与 SDK 占位的合法形式等**不得简化为本 body 摘要**）。HARD-GATE 验收：

- stub 命中 → 必须读 `source_anchors` 指向的源文件再生成；anchor 缺失 / 读取失败 → **FAIL，禁止 placeholderCard 占位**。
- 合法占位遵循 §2.1 六类 kind：converter 可产 4 类——`// FWD-REF:`（forward-ref，自行发现，**写 marker 前先登记 registry**）/ registry 已登记的 `// PLACEHOLDER:`（thirdparty-sdk）/ fallback 资产 `// FWD-REF:`（resource-pending-asset）/ 已登记 `// TODO:`（forward-ref-uncertain）；未登记 TODO / 空回调 / 假 console.info / 空 try-catch 一律 FAIL。
- 返回报告 `failed_stubs`（stub 无法展开清单，与编译无关——converter 禁止自行编译）必须为空才 PASS。

**批内并行**：批内页面默认全并行派发；每批所有子代理全部完成后执行该批收尾结算（§4b，无编译）。

### 4a-bis. 入口页 Navigation 装配 + 注册 + Hello World 剔除（ONE-TIME，HARD-GATE）

Stage 1 **全部 Batch 完成后**（§4d 收口第一步）一次性执行：① 入口页加入 `main_pages.json` 并同步改 `EntryAbility.loadContent('pages/{MainPage}')` → ② 入口页装配 `Navigation` 外壳 + `@Builder pageMap` 路由表（届时所有 NavDestination struct 已存在，一次定稿）→ ③ **HARD-GATE**：剔除 DevEco Hello World 模板——grep `Index.ets` 命中默认模板特征则三联清理（编译验证并入 §4d single-pass，不单独派发）。

**关键不变量**：`main_pages.json` 的 `"src"` 最终**只保留入口页一项**——NavDestination 子页面由入口页 `pageMap` 路由，不逐页登记。完整分步流程 **MUST 加载** [references/entry-navigation-setup.md](./references/entry-navigation-setup.md)。

### 4b. Batch 收尾 subagent（per-Batch, HARD-GATE）

本批所有并发 converter 完成后，派**一个**Batch 收尾 subagent（**`a2h-closer`，mode=batch**；派发参数模板 **MUST 加载** [references/agent-prompts/2-batch-closer.md](./references/agent-prompts/2-batch-closer.md) + [_common.md](./references/agent-prompts/_common.md)）。该 subagent 是本批 **brief 与账本变更的唯一作者 + 资源残量兜底者**，依次串行两步（**批内无编译**——统一编译在 §4d 收口）：

1. **资源 sweep（残量兜底，只读校验为主）**：grep 本批生成/改动的 .ets 全部静态 `$r(...)` 引用（**完整性来自 grep 穷举，不依赖 converter 申报**），与 `resources/` 比对解析性 → 仍缺失的调 `ios-resources-convert` 扫 iOS 源补齐 → 仍无源写 `MISSING_xxx`。
2. **产 writeback manifest**：本批页 `pending → converted` 记入 manifest（结算即翻）＋ draft batch brief 全文（schema 见 [references/brief-schemas.md §1](./references/brief-schemas.md)）＋ 账本翻转集合，一次写 `spec/execution/writeback/writeback-batch-NN.json`（schema：brief-schemas §4）后 return——closer turn 内**不直写** brief / 账本。

**域巡检波（批/组收口后无条件，与后续施工并行）**：`apply_writeback` 成功时会**直接打印本批的巡检派发指令**——照打印的指令立即执行，不是可选建议；凭证缺失会被 binding_gate 的 patrol-receipt 检查判 FAIL。协议全文按 [references/patrol-routing.md](./references/patrol-routing.md) 路由表**立即后台派发**域巡检 agent（派发模板 MUST 加载 [agent-prompts/9-patrol.md](./references/agent-prompts/9-patrol.md)）。巡检只读、与施工零竞态；**join 硬点=本批 converted→verified 翻转前**；findings→1 轮修复→机械闸复验→清零才翻 verified，未清记债转 FV 审计段，流水线不等。

**writeback 协议（四模式通用，§5 各段、§7 同此）**：closer 返回后主线程跑 `python <a2h-execute>/scripts/apply_writeback.py <manifest> --project-root .`——确定性落盘 brief + 翻账本（registry / ui-manifest / feature-index），幂等可重放；**崩溃恢复 = manifest 在则重跑 apply，绝不重做接线/编译/结构**。

**HARD-GATE**：writeback manifest 必产 + apply 成功才进入下一 Batch（**批间无编译门**）；缺失 → 阻断。

### 4c. 骨架审计 gate

Stage 编译 PASS 后**调用 `$arkts-structural-closure` skill（参数：`mode=stage target=<1|2|3>`）** 做骨架兜底。绝大多数情况 0 findings 直接 PASS；CONTINUE 时按 dispatch_prompt 派 repair worker 修后重调，≤ 2 轮仍 CONTINUE → BLOCKED。Stage 3 末尾自动启用 L4.dangling-fwd-ref 检测。细节 **MUST 加载** [references/skeleton-audit.md](./references/skeleton-audit.md)。

### 4d. Stage 1 完成标志

所有 Batch 执行完毕后，顺序收口：① **§4a-bis 入口装配** → ② **§4c 骨架审计 gate**（扫描范围 = Stage 1 起点以来 git diff 改动的 .ets + 全部 `batch_NN_brief.md`；FAIL 阻断）→ ③ **single-pass 编译**：派发 Codex 子代理 `hmos-builder`（CALLER=a2h-execute, STAGE_HINT=stage-1-close，**限 1 轮**：build 一趟分类——undefined Base 符号 = 预期跳过不追修；parse / 语法 / 资源 JSON 语法 = 真错必修或标记）→ ④ 输出 Stage 1 统计（总页面 / 成功 converted / 失败需人工 / single-pass 真错数）。

## 5. Stage 2：Feature Base（水平基础设施）

> **前置依赖**：Stage 0 资源前置已完成。Base-0 已上移至 §3（Stage 0），本阶段直接从 Base-1 开始。

Stage 2 读取 base-plan.md 实际 Base 任务及依赖执行公共基础设施，包含计划声明的组装根等非整数编号任务；不根据固定编号范围裁剪。旧 plan 无 base-plan.md 时回退旧 Phase 0 段。

### 5a. 执行流程

按 base-plan 的实际 item_id/parents 派发 worker，依赖先行；Stage 0 已完成的资源项依据真实 receipt 跳过。Base-7 为原默认阻断编译项，按计划实际验证任务执行，不能遗漏 Base-6.5 等组装任务。

### 5b. 子代理派发方式（Stage 2/3 通用）

Stage 2 和 Stage 3 的 **codegen worker** 统一使用 `a2h-migration-worker`；各级**收尾**统一使用 `a2h-closer`（mode=batch/base/group/final）：

完整通用 worker prompt **MUST 加载** [references/agent-prompts/3-worker.md](./references/agent-prompts/3-worker.md) + [_common.md](./references/agent-prompts/_common.md)。**派发 prompt 禁复述** agent 定义 / _common.md 已载纪律（一行指针即可）；但**任务专属 scope（锚点 / 契约差异 / 文件清单）不得省略**。合法占位遵循 §2.1 六类 kind：Base signature 桩登记 `kind=forward-ref` + `resolve_by=Slice {N} Step 3c`；**skill 库未覆盖的三方 SDK** 登记 `kind=thirdparty-sdk` + `trigger=<业务类别> SDK 入仓`；fallback 资产登记 `kind=resource-pending-asset`。每个占位 6 字段齐全。

### 5c. Base 层任务详情

任务内容与 `suggested_skills` 的权威 = `plans/base-plan.md` 各任务 stanza（本 body 不复述）。执行须知两条：**Base-6 公共组件库**是 Stage 3 全部 UI 工作的样式锚点（Design Tokens + 原子/复合组件）；**Base-7** 派子代理 hmos-builder（STAGE_HINT=stage-2-base-7）。

### 5d. 编译检查点（per-phase）

> 编译派发 + placeholder 回填完整流程与**构建操作纪律**（cache / checkpoint / CLI→IDE 降级）**MUST 加载** [references/build-loop.md](./references/build-loop.md)——纪律注入所有构建 subagent 的派发 prompt。

Base 层所有任务完成后（Base-7）：派发子代理 `hmos-builder`（STAGE_HINT=stage-2-base-7，最多 20 轮自动修复）。BUILD_STATUS=PASS → **执行 §4c 骨架审计 gate**（扫描范围 = Stage 2 git diff 改动的 .ets + 全部 `base_NN_brief.md`）→ FAIL 则阻断进入 Stage 3；BUILD_STATUS=FAIL → 阻断（Base 层是所有 Slice 的前置依赖），把 REMAINING_ERRORS 写入 `base_NN_brief.md` evidence 段。

### 5e. Base Task brief（HARD-GATE）

每个实际 Base 任务完成后，派 a2h-closer（mode=base）核对并产 writeback manifest（brief 全文在内，经主线程 apply）：manifest 不产 / apply 未过 → 不允许进入下一个 Base 任务；Base-7（编译验证）brief 未 PASS → 阻断 Stage 3 启动。**brief schema 模板 + 字段读取来源**见 [references/brief-schemas.md §2](./references/brief-schemas.md)（`generated_files` / `modified_files` / `unresolved_placeholders` / `evidence` / `next_dependency`）。

### 5f. Stage 2 完成标志

输出 Stage 2 统计（总数/成功/失败、公共组件数、编译状态；FAIL 阻断）。**产 `spec/execution/base-contracts.md`（as-built 接口摘要，一页内）**：Stage 3 全部 worker 派发**传此指针、禁内联 Base 契约正文**。

## 6. Stage 3：Feature Slices（垂直切片）

Stage 3 读取 `feature-plan.md` 的 Slice 任务，按拓扑排序逐功能执行。每个 Slice 内部有 4 个步骤（3a/3b/3c + 3d/3e 接线验证合一）。

### 6a. 执行流程

读 `feature-plan.md` **索引**拓扑排序后的 Slice 列表，**按 `parallel_group` 批粒度编排**（组间拓扑串行，组内并行）。每个 parallel_group 三步：

1. **组内 worker 派发（每 slice 恒 1 个 worker + 长杆先行）**：组内按 pages_owned **降序**派发；每个 slice worker 跑 Step 3a/3b/3c + **自身页内**接线。**安全阀（判断式，默认不拆）**：slice 明显过大 → 按**依赖断面**拆 2~3 个 worker（文件集不相交），**禁止按 Step 3b/3c/3d 逐步拆**。所有 worker 只写自身 scope 文件，禁碰共享文件（两项 append-only 例外见 `_common.md`）。派发 prompt 附 `Base 契约: spec/execution/base-contracts.md` **指针，禁内联契约正文**。
2. **group-closer（单写者，1 个）**：本组 worker 全部完成后，派一个 group-closer（**`a2h-closer`，mode=group**；派发参数模板 **MUST 加载** [references/agent-prompts/8-group-closer.md](./references/agent-prompts/8-group-closer.md) + [_common.md](./references/agent-prompts/_common.md)）；**末组**（索引 FV 前最后一个 Group）追加参数 `defer_structural_to_fv: true`，中间组禁用）：跨文件接线（cross_slice_edits + HomePage embed wires；registry 状态变更记 writeback manifest，plan 产物零回填）→ 资源 sweep → **1 次** compile-fix loop（`hmos-fix-build-errors`，≤20 轮）→ **结构 fix-forward**（自调 `mode=group` + 自修 ≤3 轮直到 CONVERGED，非收敛才冒泡）→ 产 writeback manifest（group brief 全文 + 账本变更集合，主线程 apply 落盘，协议同 §4b）。
3. **主线程仅处置冒泡**：结构验证（`mode=group`）已合入 group-closer 自身 fix-forward；主线程**只在 closer 回传 escalation（STALLED/REGRESSED/EXHAUSTED）时**介入——按 dispatch_prompt 派专家 repair worker（feat→worker / ui→converter）/ 标 BLOCKED。

**编排规则**：组容量上限与拆组优先级的权威 = a2h-plan Step 5；组间 `depends_on`：group N 的 group-closer 把共享文件定稿 + brief PASS 后，group N+1 才启动；**同族子组（同数字前缀）worker 波合并并行、closer 按字母序链式串行**（禁并行）；**group 内仅 1 个 slice → 退化为「1 worker + 1 closer」**。降级（共享文件耦合过紧）只改组的拆分粒度（拆成 size-1 组），不引入第二条协议。**depth=stub feature 的按需升级**：slice 真正触及时**就地升级**补齐 standard 档深度（锚定覆盖率 ≥30%），更新 feature spec 与 `source-coverage-report.md` 后再派 worker，**不回 a2h-spec 全量重跑**。

### 6b. Step 3a: UI 补充

主线程按 ui-manifest 中目标页面（+ 子组件表内嵌子组件）的 status 分支调度：

| status | 处置 |
|---|---|
| `converted` | 确认 .ets 存在，**不跳过 Slice**（接线移交 Step 3d——整体跳过是孤儿 VM 根因之一） |
| `pending` / 不在 ui-plan | ui-snapshots 存在 → 调 a2h-ios-converter；缺失 → 触发 §9 Phase A 按需模式；转换后 status→converted + 派 hmos-builder 验证 |
| `verified` | 兼容旧结构收口，跳过重复建页；仍消费本 slice 的接口与接线义务 |

UI 补充必须引用 Base-6 公共组件库。worker 同时承担 `forward-ref-uncertain` 二次审视。完整流程 **MUST 加载** [references/agent-prompts/4-step3a-ui.md](./references/agent-prompts/4-step3a-ui.md) + [_common.md](./references/agent-prompts/_common.md)。

### 6c. Step 3b: ViewModel + 状态管理（C7 三段式）

<HARD-GATE>
生成本切片 ViewModel。**complex 强制三段式**（源码理解 → 差异清单 → 实现，一次调用），simple 仅第三段；**anchors 经 `source_anchors_ref.source` 读 spec**（grep-first 定点消费，不整读源文件）；complex 必产 `spec/execution/source-understanding/{slice}-source-notes.md`。判据 **MUST 加载** [references/agent-prompts/5-step3b-vm.md](./references/agent-prompts/5-step3b-vm.md) + [_common.md](./references/agent-prompts/_common.md)。
</HARD-GATE>

### 6d. Step 3c: 数据层接入

<HARD-GATE>
为该功能切片创建 Repository / Service、连接数据源，数据流 UI ← ViewModel ← Repository ← API/DB 闭环。完整任务清单（complex 的 source-notes 对齐 / impl: 指针精读 / **多子仓契约约束**）**MUST 加载** [references/agent-prompts/6-step3c-data.md](./references/agent-prompts/6-step3c-data.md) + [_common.md](./references/agent-prompts/_common.md)。worker 报告的「决策缺口」由主线程按 §1.1 阻断。
</HARD-GATE>

### 6e. Step 3d 接线 + 3e 验证 + Slice brief（per-group，HARD-GATE）

<HARD-GATE>

**执行者（单一路径）**：slice worker 只做**自身页内** 3d 接线（MUST READ [agent-prompts/7-step3d-wiring.md](./references/agent-prompts/7-step3d-wiring.md) + [_common.md](./references/agent-prompts/_common.md)）；**跨文件 3d 接线 + 资源 sweep + 1 次编译 + 3e 结构 fix-forward + 组单文件 group brief 全部由 group-closer（`a2h-closer` mode=group）一手做完**。**主线程仅在 closer 回传 escalation 时介入**。

**不变契约（缺一即该 slice 标 BLOCKED、不 retry）**：
1. **3d 接线**：补 import + 实例化 ViewModel、grep `// FWD-REF:` marker 逐个换真实调用。**slice 文件只读，零回填**——接线完成性由 `verify_slice_wiring.py` C2 按结构化对从代码机械判定；`resolve_by=本 slice` 的 forward-ref 必须全解除。
2. **3e CONVERGED 后非 loop 校验**：本 slice 前缀每个占位 P-ID 有对应 marker + registry 6 字段 + trigger 白名单；complex slice 必有 source-notes.md；`deferred_items` 每条含 `owner_skill` + 闭环条件。
3. **Writeback manifest 必产**（`spec/execution/writeback/writeback-group-NN.json`，schema MUST READ [brief-schemas.md §3/§4](./references/brief-schemas.md)）：全契约 PASS → manifest 记 brief `final_state: PASS` + 页面 `converted → verified` + **feature `pending → implemented`** + **收组清行集合**（registry.resolve）→ 主线程 **apply 成功** → 进下一 group/slice。

</HARD-GATE>

### 6f. Stage 3 完成标志

Stage 3 所有 Slice 执行完毕 + §4c 一次性骨架审计通过后，输出统计，然后进入 **主题收货闸**（`python3 <a2h-execute>/scripts/theme_gate.py --project <工程根>`，无 resolved-theme.json 不阻塞）→ **字面量收货闸**（`literal_gate.py`，真值源 `spec/baseline/literal-ledger.json`；无 ledger 不阻塞）→ **死壳检测**（`dead_shell_gate.py`）→ **载体降级检测**（`carrier_gate.py`，WARN 报表级不阻断）→ **交互命中闸**（`hit_test_gate.py`：无条件字面或显示时 `HitTestMode.Block` 挂含交互子节点的容器 → FAIL）→ **资源名闭集闸**（`resource_name_gate.py`：按名取资源的字面名必须在 resources 闭集；缺席未登记 = 静默缺席 FAIL）→ **§7 Final Structural Closure（FV-1）→ FV-2 终态全量编译** → **冷启冒烟探针**（设备在线时 `bash <a2h-execute>/scripts/cold_start_probe.sh <bundleName>`；无设备 → exit 3，记 `unverified-cold-start` 粘性债交 a2h-verify）→ a2h-verify。五闸 + deadshell/carrier/resname 已收编为 structural-closure pipeline 模式必需 detector，§7 FV-1 会再机械跑一遍并计入完成度闸。

## 7. Final Structural Closure（Stage 3 全部完成后 HARD-GATE）

<HARD-GATE>
Stage 3 全部 group brief 落地 + §6f 统计输出后，派 **`a2h-closer`（mode=final）**——其内部**调用 `$arkts-structural-closure` skill（参数：`mode=pipeline target=final`）** 跑整工程兜底（与 Stage 3 解耦，独立一次性 loop），CONVERGED 后产 `writeback-final.json`（主线程 apply，协议同 §4b）。⚠️ **禁止用 grep 替代**。

**收尾 evidence（缺失或 `final_state ≠ PASS` → 不允许进 a2h-verify）**：
- `spec/execution/autofix-log/round-<R>/loops-final-structural-closure.json` — `final_state == PASS`
- `spec/execution/briefs/final_structural_closure_brief.md` — 嵌入 loops.pipeline 段

CONVERGED + evidence 就位 → FV-1 完成。CONTINUE 按 dispatch_prompt 派 repair worker（feat → `a2h-migration-worker` / ui → `a2h-ios-converter`）后重调。

**FV-2 终态全量编译**：FV-1 通过后派发子代理 `hmos-builder`（STAGE_HINT=fv-final-build，≤20 轮）。**必须为真实构建**：`all tasks up-to-date` 秒级空转不构成 PASS 证据，命中则 touch 入口文件或动用本轮唯一 clean 强制重编。回读构建器真实 JSON 报告路径，按 §11 将其作为 `--build-evidence` 传入报告命令；brief 中一句「编译 PASS」不构成可消费证据。
</HARD-GATE>

## 8. 状态追踪与完成性契约

### 8a. 机械完成性契约（plan 零回填）

**plan 产物生成后只读**——execute 不在其中打 `[x]`、不回填 evidence。完成事实凭据分两层：**接线完成性**由 `verify_slice_wiring.py` C2 按 slice 文件结构化对直接机械判定（调用方页面存在 + handler 已接 + target 被实例化）；**过程记录**写入 brief（final_state / deferred_items / 未解占位 / pages_verified）。

### 8b. 页面与 feature 状态生命周期

`pending → converted → verified`（ui-manifest）/ `pending → implemented → verified`（feature-index，唯一账本）：实现态由 group-closer 记入 writeback manifest、主线程 apply 翻；verified 为旧流程兼容值，不能推导独立行为/视觉通过。交叉护栏：feature=implemented 时其 owned 页不得仍 pending。

## 9. Phase A 按需触发机制

Stage 3 Step 3a 发现目标页面 ui-snapshots 数据缺失（status 非 converted/verified **且** `ui-snapshots/page_NNNN/` 缺失或不完整）→ 自动触发 a2h-spec Phase A 按需模式：单页源码分析 → 最小数据集 → 增量更新 ui-manifest + page spec → 继续 converter，不中断 Pipeline。完整触发条件 / 流程 / 降级处理 **MUST 加载** [references/phase-a-ondemand.md](./references/phase-a-ondemand.md)。

## 10. Skill 绑定机制

**主路径 = plan 标注（三层承载）**：Base/FV 任务读 stanza `suggested_skills:`；Slice 4 步默认映射 = 3a `a2h-ios-converter` / 3b `arkts-state-manager` / 3c `arkts-data-layer` / 3d=closer 链；Slice 差异化增量读 slice 文件 `suggested_skills+:` 字段——**必须并入派发**。**覆盖 / 注入 / 降级**：runtime 上下文检查可**覆盖** plan 建议、按 `style_set` **注入**风格 skills、对不存在的 skill **降级**；原则**只升级不降级**。完整覆盖表 / 注入逻辑 / 降级流程 **MUST 加载** [references/skill-binding-override.md](./references/skill-binding-override.md)。

## 11. 迁移报告（派生汇总，禁止手填）

<HARD-GATE>
每次任务落账、Stage 收口、FV 结束及部分执行交付前，主线程实际运行以下命令并读取退出码及产物（`<target>` 使用配置中的绝对目标路径）：

```text
python <runtime>/scripts/a2h_ios.py spec-summary --project <target> --output <target>/spec/reports/spec-summary.json
python <runtime>/scripts/a2h_ios.py migration-report --project <target> --output <target>/spec/migration-report.md
python <runtime>/scripts/a2h_ios.py migration-report --project <target> --check <target>/spec/migration-report.md
```

有当前真实构建 JSON 报告时，三条均追加同一 `--build-evidence <build-report.json>`；未构建则不传。`--check` 失败须更新证据或重新生成，**禁止手改成功数、逐页状态或摘要来消除差异**。报告结构见 [templates/migration-report-template.md](./templates/migration-report-template.md)；`spec/migration-report.md` 完全由工具重建，不手工补正文。
</HARD-GATE>

## 12. 触发 / 部分执行

- **完整执行**：「执行迁移」/「开始执行」/「Plan 我看过了没问题，开始执行」
- **部分执行**：「只执行 Stage 1」/「从 Stage 2 开始」/「只执行 Slice 3」
- **重试与继续**：「重试 FAILED 的 slice」/「继续执行（从上次中断的地方继续）」

| 用户指令 | 行为 |
|---------|------|
| "只执行 Stage 1" | 只读 ui-plan.md，只执行页面转换批次 |
| "只执行 Stage 2" | 只读 plans/base-plan.md（旧 plan 回退 feature-plan.md 旧 Phase 0 段） |
| "只执行 Stage 3" | 只读 feature-plan.md 的 Slice 列表（前提：Stage 2 已完成） |
| "重试 FAILED 的 slice" | 从 summary / 原调度器失败任务 / 阶段 brief 定位 slice；原 owner 按 **size-1 组**重跑，v2 仍走四拍并重建派生报告 |
| "只执行 Slice N" | 把该 Slice 作为 **size-1 组**执行其 4 步（前提：其依赖已完成） |
| "继续执行"（resume） | 读 feature-index 状态列判定已完成 slice，从首个 pending 的 parallel_group 续跑 |

`--wave` 语义：v2 计划分 `understand`（只写 spec 的理解波）与 `domains`（实现波，缺省）；部分执行/续跑不改 wave，只改起点与范围。

## 13. 读取时机（references）

| 触发时机 | 必读文件 |
|---|---|
| 执行 §2 之前；机器产物/状态写者/四拍纪律存疑 | ../ios-source-analysis/references/harness-v2.md |
| 派发任意 worker/closer 前；占位禁令 / FWD-REF marker / 单写者 / 信封 | references/agent-prompts/_common.md（随读）+ 对应单段文件（路由见 references/agent-prompts.md） |
| 启动读决定 / 决策缺口 / 冲突回流 | references/execution-discipline.md |
| 公开合同冲突 / 对接点标锚 | ../a2h-spec/references/spec-delivery-contract.md + ../a2h-plan/references/plan-delivery-contract.md |
| Stage 0 资源前置 | references/stage-0-resources.md |
| Stage 1 每页派发前数据完整性 | references/data-prep.md |
| §4a-bis 入口装配 | references/entry-navigation-setup.md |
| §4c 骨架审计 | references/skeleton-audit.md |
| 编译派发 / 构建纪律 / CLI→IDE 降级 | references/build-loop.md |
| §4b/§5e 域巡检 / patrol 凭证 | references/patrol-routing.md |
| brief / writeback manifest schema | references/brief-schemas.md |
| §9 Phase A 按需 | references/phase-a-ondemand.md |
| §10 skill 覆盖/注入/降级 | references/skill-binding-override.md |
| §11 派生报告结构 | templates/migration-report-template.md |

## 14. references 索引

- `references/agent-prompts.md`（路由索引）+ `references/agent-prompts/{1-converter,2-batch-closer,3-worker,4-step3a-ui,5-step3b-vm,6-step3c-data,7-step3d-wiring,8-group-closer,9-patrol,_common}.md`：各派发点 prompt 模板（触发见 §13，单段加载勿整份求全）。
- `references/{execution-discipline,build-loop,data-prep,entry-navigation-setup,skeleton-audit,patrol-routing,stage-0-resources,skill-binding-override,phase-a-ondemand,brief-schemas,ios-source-protocol}.md`：分节细则。
- `scripts/{apply_writeback,lint_execute_coverage,theme_gate,literal_gate,dead_shell_gate,carrier_gate,hit_test_gate,resource_name_gate,theme_brief}.py`、`scripts/cold_start_probe.sh`：本 skill 自有脚本（正文按名引用，主线程只经这些脚本查状态/落账，不手写检查）。接线完成性判定的 `verify_slice_wiring.py` 属 `$arkts-structural-closure` skill（`../arkts-structural-closure/scripts/verify_slice_wiring.py`），由 §4c/§6e/§7 的结构闭环调用，非本 skill 脚本。
- `templates/migration-report-template.md`：派生报告结构。

## 交接

- **前置门闸**：本 wave `done`（代码任务全部落账）+ §7 FV-1 evidence（`loops-final-structural-closure.json` PASS + brief md）+ FV-2 真实编译通过 + `spec/state` 无未落账 ERROR/blocked 在途 → 才可交接。
- **移交产物清单**：`spec/execution/briefs/*`、`spec/execution/writeback/*`、`spec/execution/base-contracts.md`、`spec/execution/autofix-log/**`、`spec/.a2h/impl-claims.json`、`spec/migration-report.md`、`spec/reports/spec-summary.json`、构建证据 JSON 路径。
- **下一步**：提示进入 `a2h-verify`（同会话可直接续跑）；需继续沉淀经验时再由 verify 之后进入 `a2h-retrospect`。

---

## 收尾：上报本阶段用量

本 skill 的最后一步（无论经 a2h-run 还是单独触发）：

```bash
.migbot/bin/a2h mark-stage a2h-execute
```

标记 `a2h-execute` 阶段水位（写 stage-marks fact，受授权门控、尽力而为）。token 用量由宿主生命周期采集，本步不采集。**忽略其退出码，绝不阻断流水线。**
