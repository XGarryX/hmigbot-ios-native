---
name: a2h-execute
description: iOS→ArkTS 迁移代码的三阶段执行引擎（Pipeline 第三步）：按 ui-plan.md/feature-plan.md 派发 subagent 完成页面转换、基础设施、功能切片，含编译闭环。当用户说"执行迁移""开始执行""按 plan 开始做"时触发，支持部分执行/重试/断点续跑。不要用于：生成 Spec（用 a2h-spec）或计划（用 a2h-plan）；plan 未就绪时先跑 a2h-plan。
metadata:
  type: pipeline
  domain: migration
  tags:
  - pipeline
  - migration
---

> **0.13.4 统一合同（优先于历史示例）**：先读 [执行交界合同](../a2h-run/references/execution-boundary.md)。源读取、选定构建配置、SwiftSyntax/facts、源 AC 和 indexed 计划由当前 git 上游唯一生产；从 execute 起使用本技能的 Garry 实施/收口方法。只使用宿主实际支持的派发字段，不照抄 `agent_type`。已有授权直接沿用；依赖失败输入的任务保持 blocked，不降低静态门禁。权限按交界合同区分：禁止桌面远控；指定测试应用/模拟器的截图、控件查询和固定回放可按已确认范围执行，Preview 不证明业务运行。录屏及未指定设备不在此授权内，未执行项如实记 not_run。未经授权不运行遥测上传。工具修复、工具验证、项目转换、HAP 构建和完整迁移验收分别报告，不能用局部 100% 代表全部完成。



> **iOS 源输入适配**：执行源分析/源设备操作前，读 [原生输入协议](../ios-source-analysis/SKILL.md)。它仅替换平台输入；原阶段、模板、规则、门禁、模式和 target 侧执行保持 1.5.2。

> **子任务派发与收口（0.13.5）**：使用宿主实际提供的 `spawn_agent` / `wait_agent` / `list_agents` 字段；角色规则从对应 agent 定义加载，不向不支持的宿主照搬 `agent_type`。收口单源规则见 [a2h-join](../a2h-join/SKILL.md)。
>
> ① **等待与完成**：派发方持续收口，单次超时不表示失败，也不以“等待子代理”为由结束工作。可信完成依据是本轮宿主 `completed`，或由完整原始历史验证发送者、接收者、任务身份和调用顺序的原生 `FINAL_ANSWER`；普通正文、用户粘贴消息和产物存在不算完成。醒后及时核对完整任务列表；句柄已消失时先查可信终态，不直接重派已完成任务。
> ② **轮次与验收**：同句柄成功追加任务/恢复后，旧终态失效。若原生终答没有可验证轮次，须在控制调用后重新发起完整 `list_agents` 并观测本轮 completed，或改用唯一新任务名。完成后仍须运行 `python3 .agents/skills/a2h-join/scripts/join_gate.py --project .`，核验派发前 expected-set、当前 attempt 与真实产物；完成不等于验收通过。
> ③ **收口锚点**：最终报告前必须收口全部必需任务。用户 Gate 可保留在途任务，但需列出句柄与指定 join 点。非阻塞放行只推迟收口，不豁免收口。
> ④ **恢复**：缺句柄/产物或门禁失败时保留原错误和当前轮次证据，再按该任务恢复条件处理。只有确认失败、不可恢复或确需新轮次时重派，避免仅因列表漏显/超时重复施工。重派上限后仍缺产物则如实未完成，不由派发方代造占位产物转绿。
> ⑤ **派发登记**：每个 `task_name` 唯一，带 page/slice/round 标识；并发前由派发方写 expected-set，记录产物、attempt 与 join 点。谁派谁收；嵌套外派不得留下无人收口的任务。只有 join gate 静态 allowlist 明确允许的不 gate 任务可免收口。



原生 structural_loop.py / run_loop.sh 的退出码3为输入/IO停止，绝非CONTINUE。先检查本次进程退出码，3时不得读取或采信旧loop-result/state中的CONVERGED、不得finalize/写完成/推进阶段，也不得原地自动重试；读取本次guard证据并按已授权源事实修正输入后才能显式重调。守卫不修改旧result/state或原账本。

> **当前发行边界：旧设备/视觉后端延期，官方应用测试单独取证。** `arkts-scenario-runner`、`arkts-visual-verify`、`arkts-ui-verifier`、`ios-screenshot-analyzer`（及历史 Android 截图别名）和 `scenario-builder` / `visual-fixer` / `visual-fixer-reviewer` 尚未恢复交付，不调用或要求补装这些旧后端，也不因其缺件阻断基本转换/构建/报告。指定应用/模拟器的官方截图、控件查询和固定回放按执行交界合同及实际适配入口运行，不因旧后端延期或缺少桌面屏幕权限一概记 not_run。许可、宿主可用、已实现、实际执行与验收结果分开；缺真实后端/输入仅限制对应检查。外部原始证据核对版本、配置、范围和来源，未执行不记 PASS，真实产品失败保留。下文旧调用/目录仅为兼容映射。


# a2h-execute

结构接线、动态图片证明及分组占位登记按 [当前证据范围](references/native-evidence-boundaries.md) 执行；失败报告区分实际缺陷、描述语法和未支持证明。

## 0.13.5 B0–B3 执行接线（优先于下文旧的整波/组间等待示例）

- 启动沿用已冻结的执行合同。UI交付清单须在Plan冻结前从正式Spec生成；执行期不补写正式库存/计划。按 [页面交付协议](references/ui-delivery-contract.md) 消费每页packet，完成组件、状态、弹窗、交互的generator/assembler责任，不能仅交页面壳。缺图保留明确gap；实际图片像素复核和静态文件读取分别报告。
- Stage 1每批按 [持续补位](references/stage1-dispatch.md) 执行 `indexed-dispatch next/bind/observe`：容量来自当前宿主真实限制和在飞任务；完成一个经F01验收后补一个本批可执行任务，限流等待、空结果不成功。F02预登记完整资源清单及唯一closer保持；不跨UI批次私自扩大范围。
- Stage 2按 [依赖派发](references/dependency-dispatch.md) 消费真实parents/ownership，独立Base任务可并行；共享文件仍单写者，Base-7实际构建成功才允许Stage 3。
- Stage 3按冻结的真实读依赖和稳定发布派发，group保留唯一closer的共享装配/资源/回写检查点。需要最终路由/公共导出时等待closer，不能以worker返回替代稳定输入。缺少稳定发布声明则保守等原收尾。
- 编译默认per-group。只有可冻结且当前消费者完整支持stage3-pilot时，group收尾可明确记录 GENERATED_PENDING_COMPILE / deferred-to-stage3-gate；这不是编译PASS。此模式的manifest只写brief/registry，不能提前翻ui verified/feature implemented；主线程apply额外传`--generated-checkpoint <checkpoint>`，由冻结调度器选择真实已生成任务并写独立收据，不改原账本。全部组收口后必须调用原hmos-builder，消费当前日志/诊断/HAP的独立stage3证明，才交FV；Base-7和FV最终真实构建都保留，构建错误退回有写权的责任任务。
- 行为按 [行为效果链](../a2h-verify/references/behavior-effect-review.md) 核验：设置默认/保存/重载/业务效果，点击输入/处理/副作用/反馈。执行原case与独立oracle；保存成功不等于实际生效，静态生成不算行为PASS。未选或缺后端保持原partial/not_run路径。
- 所有真实调度、等待、构建、返工、材料和回写按 [全流程计量](../a2h-run/references/execution-measurements.md) 记录。依赖阻断、预算耗尽和限流均保留具体原因；不降低原质量门换提速。


启动时先运行 `python3 <runtime>/scripts/a2h_ios.py execution-contract --project <target> --apply`。
该命令真实消费 git 的 source/spec gate、plan-ir 冻结输入和 indexed 计划；只在
`spec/execution/` 生成下游合同与静态 meta/outline，不补写已冻结 baseline。
失败则停在其恢复条件；成功后唯一执行顺序为 Stage 0 → UI Batch → Base → Slice Group → FV。
不同时启动旧 `next-batch/receipt/land-results` domains 循环。旧 v2 在途任务须先正常回收或受审终止，
工具升级改变合同 revision 时须 reviewed replan；不能自动沿用旧 PASS。
已有选定预算时，在每次实际新派发前给 execution-contract 同时传 `--usage-ledger <原账本> --usage-run-id <原run-id>`，由原预算服务检查 UNKNOWN/耗尽与身份；不可只在启动时检查。预算耗尽阻止新派发，不阻止 writeback/join/报告回收。
阶段开始和续跑都重跑 execution-contract 校验。页面 enrich 只写执行域，正式 spec/AC 变更回上游处理。


## 启动检查 — 待办 findings

读 `spec/.a2h/open-findings.json`（不存在 = 首轮，直接开工）：

| 情况 | 行动 |
|---|---|
| 有 `owner_stage: execute` 的条目 | 先处理这些，再做本轮正常工作；处理完重跑 `scripts/lint_execute_coverage.py` 确认消失 |
| 有上游当前有效的真实产品/源合同阻断 | 按 finding 的对象、消费者和任务依赖阻断受影响部分；独立诊断、构建和报告继续，不按整个队列拒绝开工 |
| 条目标记 `escalate: true`（同一路径多次无进展） | 停止该技术重试路径，读取原错误与恢复条件；可执行替代方案继续，不因次数生成产品决策卡 |
| 本阶段 section 标记 `halted` | 仅暂停该 section 的修复策略；修复真实缺陷或指定新的 `repair_strategy` 后重验。产品审批只用于真实的新产品取舍，预算/授权边界保留 |
| 无条目 | ✅ 正常开工 |

路由不靠猜：每个 linter 比对两份产物，**哪一侧缺条目就由哪一侧负责**。责任无法机械判定时
（典型：AC 按当前描述实现不了），用决策卡上报，由用户指定 owner——选项与 owner 的对应关系
写死在卡里，避免推诿。

**findings 只能由「原 linter 重跑后不再报」来关闭**，不能由任何一方声明「已修复」而关闭。

## 关键约束（Critical）

- **执行铁律**：execute 按 `spec/decision-ledger.md` 查表推进、**不交互式追问**；未命中时先区分技术可查证事实与新产品取舍；技术项自动查证，真实缺口只阻断受影响任务并给恢复路径，不强制下一轮 grill。启动先 Read 项目指令文件（宿主别名 `PROJECT_INSTRUCTIONS_FILE`：Codex=项目根 `AGENTS.md` / Codex=项目根 `AGENTS.md`）+ ledger 顶部「决策索引」段（status 须 `approved`；正文按需 grep D-编号，不整份吞全文）。
- **Stage 0 资源前置最先跑**（§3.0，HARD-GATE）：全部 `$r(...)` 引用可解析或显式 MISSING_xxx 才进 Stage 1。
- **合法占位 = 已登记的 5 类 kind 占位**（§2.1）：命中规范 marker（`// FWD-REF:` / `// PLACEHOLDER:` / 已登记 `// TODO:` / 资源 `[TODO: translate]`）**且** registry 6 字段齐全；未登记 / 自由文本（裸 `// TODO`、空回调、空 try-catch、假 `console.info('TODO')`、prose defer）一律 FAIL。§2.1 列 4 大延迟**归属**类，其中 placeholder 一类内部再细分 5 类 kind。
- **共享文件单写者纪律**（Stage 1 §3b / Stage 3 §5a）：并发 converter / slice worker 只写自身 page/VM/repository 文件；共享 element JSON 必须走 [资源增量协议](references/resource-deltas.md)，派发前 init 完整任务清单，每个 worker（含无新增者）submit，唯一 closer 提交 sweep 补项后统一 merge。禁止 read-modify-write 共享 JSON。`placeholder-registry.md` 登记行仍按 §2.1c append；跨文件接线、brief 与账本由唯一 closer 起草并通过 writeback 落盘，资源冲突在合并前拒绝，不能留给编译碰运气。
- **编译闭环**：Stage 3 group 的组编译在**收尾 subagent 内部**调 `hmos-fix-build-errors`；**Stage 1 批内无编译**（页面间零编译依赖，统一 single-pass 在 §3d 收口，真编译门 = Base-7）；Stage 2 Base-7（§4d）/ Stage 3 Step 3a 建页 / §3d 收口 / FV-2 终态全量编译（§6 之后）派发 Codex 子代理 `hmos-builder`（定义于 `.codex/agents/hmos-builder.toml`），Base-7 失败阻断后续全部 Slice。**主线程禁止直接调底层 build skill**（Batch/group 收尾是 subagent，不算主线程）。
- **结构性验证 = `$arkts-structural-closure` skill（参数：`mode=<stage|group|pipeline> target=<...>`）**（§3c stage / §5e group（含 size-1 组）/ §6 pipeline）：**禁止 grep / 自跑 scripts 替代**。中间步骤看 skill 返回的 verdict 即可；**§6 完整执行验收须有真实收尾 brief**；缺失时对应验收未完成，仍允许 verify 的独立诊断、构建和 partial 报告。
- **接线完成性机械判定**（§5e 配套）：plan 产物（索引 + slice 文件）只读、零回填——完成性由 verify_slice_wiring.py C2 按结构化对从代码直接判定（调用方页面存在 + handler 已接 + target 被实例化，孤儿 VM 防线不变；完整契约见 §9a）。
- **References / Templates 强制加载**（HARD-GATE）：body 中所有 `[references/X.md]` / `[templates/Y.md]` 引用，在对应步骤执行时**必须** Read 被引文件作为执行规范，不得仅靠 body 摘要执行（占位禁令 / FWD-REF 规则不得简化）。**派发 prompt 已按段拆分**：`references/agent-prompts/` 下 `1-converter.md` … `8-group-closer.md` 每个是对应派发点的完整模板，派发时 **Read 对应单段文件 + `agent-prompts/_common.md`（公共占位规则）即可**——**不要整份加载所有段**（旧单文件 413 行已废，索引见 `references/agent-prompts.md`）。跳过加载 = PROCESS_VIOLATION。规则适用于 LLM 主线程和派发的 subagent。

---

## 1. 定位

Pipeline 层第三步，**三阶段执行引擎**。读取 a2h-plan 生成的双计划（ui-plan.md + feature-plan.md），按三阶段顺序执行迁移。

```
a2h-spec → a2h-plan → a2h-execute（本 skill）
                          │
                          ├─ Stage 1: UI Pipeline
                          │   └─ a2h-ios-converter agent × N 页面
                          │
                          ├─ Stage 2: Feature Base
                          │   └─ a2h-migration-worker × Base 任务
                          │
                          └─ Stage 3: Feature Slices（按 parallel_group 批粒度）
                              └─ 组内 slice worker 并行 → group-closer（接线+编译+结构 fix-forward+brief）→ 主线程仅处置冒泡
```

**核心原则**：a2h-execute 是编排层，不实现任何迁移逻辑。所有实际工作通过 subagent 委托：Stage 1 使用 `a2h-ios-converter` agent，Stage 2/3 使用 `a2h-migration-worker` agent。

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

调 `ios-resources-convert` → 全部 `$r(...)` 引用可解析或显式 `MISSING_xxx` → 自动派 `arkts-i18n` skill 处理 `[TODO: translate]` 占位 → 自动派 `arkts-app-identity`（`scope=dev-identity`）落地 app_name / versionName / 图标（**跳过 bundleName / vendor**，属部署期 D-009、与签名 / AGC 强绑定）→ HARD-GATE 通过后进 Stage 1。

---

## 3. Stage 1: UI Pipeline

> **前置依赖**：Stage 0 必须 PASS。`ui-plan.md` 中所有 `$r(...)` 引用在本阶段开始前应可解析或显式 MISSING。

Stage 1 读取 `ui-plan.md`，按批次调用 `a2h-ios-converter` agent 将 iOS 页面转换为 ArkTS。

**执行流程**：读 `ui-plan.md`，逐 Batch 执行；每批派发前按 [资源增量协议](references/resource-deltas.md) init 当前 workers + closer 的完整清单和资源路径：**批内页面按真实容量滚动补位**派 `a2h-ios-converter` agent（单写者纪律各写各文件，导航目标未建由 FWD-REF 兜，无需逐页并行标注）→ 等本批全部完成 → 派发**批收尾 subagent（§3b：资源 sweep → writeback manifest，无编译，单写者）** → 下一 Batch，直到所有 Batch 完成；末尾 §3d 统一收口。

### 3a-pre. 数据完整性预检查（Stage 1 每页派发前）

对当前 Batch 每个待转换页面做三源数据完整性预检（meta.json × view.xml 状态 → enrich / 合成 / scaffold+Phase A 三模式）。判定表 + 两段 `synthesize_*.py` 脚本调用方式 **MUST 加载** [references/data-prep.md](./references/data-prep.md)（Batch 级批量执行、可并行合成）。

### 3a. 子代理派发方式（Stage 1 专用）

Stage 1 使用 `a2h-ios-converter` agent（**不是** a2h-migration-worker）。

每页用子代理派发，传入五参数 `activity_name` / `ui_info`（ui-snapshots 目录，含 view.xml + meta.json）/ `harmony_project_dir` / `references_dir`（ios-ui-to-arkui/references/）/ `ios_source_dir`，外加 `source_anchors`（page spec 顶部）、`registered_placeholders`（按本页 `owning_slice` 前缀 grep `spec/placeholder-registry.md` 所得已登记占位）、`wiring_ownership_map`（coverage-matrix）。converter 消费三源数据：view.xml（注明实际观测或合成 outline）+ meta.json（页面元数据）+ source_anchors 指向的 SwiftUI/UIKit/Storyboard/XIB 原生源码与资源样式。静态 outline 不代表运行时层级。

完整 converter prompt **MUST 加载** [references/agent-prompts/1-converter.md](./references/agent-prompts/1-converter.md) + [_common.md](./references/agent-prompts/_common.md) 作为派发模板（占位禁令 / `// FWD-REF:` marker 规则 / forward-ref 与 SDK 占位的合法形式等**不得简化为本 body 摘要**）。该 step 的 HARD-GATE 验收：

- stub 命中 → 必须读 `source_anchors` 指向的源文件再生成；anchor 缺失 / 读取失败 → **FAIL，禁止 placeholderCard 占位**。
- 合法占位遵循 §2.1：converter 可产 4 类——`// FWD-REF:`（forward-ref，自行发现，**写 marker 前先按 §2.1c 登记 registry**）/ registry 已登记的 `// PLACEHOLDER:`（thirdparty-sdk，plan 期直写）/ fallback 资产 `// FWD-REF:`（resource-pending-asset）/ 已登记 `// TODO:`（forward-ref-uncertain）；未登记 TODO / 空回调 / 假 console.info / 空 try-catch 一律 FAIL（完整定义见 agent-prompts/1-converter.md）。
- 返回报告 `failed_stubs`（stub 无法展开清单，与编译无关——converter 禁止自行编译）必须为空才 PASS。

**批内并行**：按stage1-dispatch在当前批次内持续补位，真实可用容量内并行派发（页面依赖不约束分批——导航 / 嵌入目标未建由 FWD-REF 兜底；批内单写者保证互不阻塞）；每批所有子代理全部完成后执行该批收尾结算（§3b，无编译）。

### 3a-bis. 入口页 Navigation 装配 + 注册 + Hello World 剔除（ONE-TIME，HARD-GATE）

Stage 1 **全部 Batch 完成后**（§3d 收口第一步）一次性执行：① 入口页加入 `main_pages.json` 并同步改 `EntryAbility.loadContent('pages/{MainPage}')` → ② 入口页装配 `Navigation` 外壳 + `@Builder pageMap` 路由表（届时所有 NavDestination struct 已存在，一次定稿）→ ③ **HARD-GATE**：剔除 DevEco Hello World 模板——grep `Index.ets` 命中默认模板特征则三联清理（编译验证并入 §3d single-pass，不单独派发）。

**关键不变量**：`main_pages.json` 的 `"src"` 最终**只保留入口页一项**——NavDestination 子页面由入口页 `pageMap` 路由，不逐页登记（Navigation 模型与旧 router 模型的关键差异）。

完整分步流程（grep 特征 / 三联清理 / 字段读取来源 / Navigation 外壳模板）**MUST 加载** [references/entry-navigation-setup.md](./references/entry-navigation-setup.md)。

### 3b. Batch 收尾 subagent（per-Batch, HARD-GATE）

本批所有并发 converter 完成后，派**一个**Batch 收尾 subagent（**`a2h-closer`，mode=batch**——收尾协议单源固化于 agent 定义；派发参数模板 **MUST 加载** [references/agent-prompts/2-batch-closer.md](./references/agent-prompts/2-batch-closer.md) + [_common.md](./references/agent-prompts/_common.md)）。该 subagent 是本批 **brief、账本变更与共享资源合并的唯一收尾者**（converter 只提交任务增量，closer 按预登记任务提交 sweep 补项，所有增量齐备后统一合并），依次串行两步（**批内无编译**——页面间零编译依赖，统一编译在 §3d 收口）：

1. **资源 sweep 与统一合并**：穷举本批 `.ets` 的静态 `$r('app.<type>.<name>')` 引用，对照源资源与各任务增量补漏，缺真实源值保留 `MISSING_xxx` 及原占位规则。补项提交到 closer 自身增量；所有预登记任务（含空增量）齐备后依次执行 `resource-delta check`、`merge`、`check --require-merged`，失败保留具体冲突/缺项和恢复条件，禁止直写共享 JSON。完整命令与收据规则见 [资源增量协议](references/resource-deltas.md)。
2. **产 writeback manifest**：本批页 `pending → converted` 记入 manifest（结算即翻——converted = 转换产出完成，编译验证在 verified 轴）；起草 batch brief 全文（schema 见 [references/brief-schemas.md §1](./references/brief-schemas.md)，只写结构化字段）+ 账本翻转集合，一次写 `spec/execution/writeback/writeback-batch-NN.json`（schema：brief-schemas §4）后 return——closer turn 内**不直写** brief / 账本。

**域巡检波（批/组收口后无条件，与后续施工并行）**：`apply_writeback` 成功时会**直接打印本批的巡检派发指令**（agent/task_name/考卷/落单路径）——照打印的指令立即执行，这不是可选建议；凭证缺失会被 binding_gate 的 patrol-receipt 检查判 FAIL。协议全文按 [references/patrol-routing.md](./references/patrol-routing.md) 路由表**立即后台派发**域巡检 agent（考卷=writeback 文件闭集+iOS真值锚点；派发模板 MUST 加载 [agent-prompts/9-patrol.md](./references/agent-prompts/9-patrol.md)）。巡检只读、与施工零竞态；**join 硬点=本批 converted→verified 翻转前**；findings→1 轮修复→机械闸复验→清零才翻 verified，未清记债转 FV 审计段，流水线不等；悬挂句柄按 join 协议条款②处置。设计依据与墙钟分析（全并行，暴露仅末批尾巴）见 patrol-routing.md。

**writeback 协议（四模式通用，§4e/§5e/§6 同此）**：closer 返回后主线程跑 `python <a2h-execute>/scripts/apply_writeback.py <manifest> --project-root .`；新协议 batch/group 必加 `--resource-scope <scope-id> --resource-closer <closer-id>`，先核验本批组计划归属与当前资源合并证明，再调用原引擎——确定性落盘 brief + 翻账本（registry / ui-manifest / feature-index），幂等可重放；**崩溃恢复**：若资源事务 pending，先按资源协议 recover；仅在当前合同、资源合并证明与原产物仍有效时重跑 apply，不把旧 PASS 当新证明，也不无故重做接线/编译/结构。closer 仍是全部账本变更与 brief 的**唯一作者**，脚本只是落盘手。

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

读 `feature-plan.md` **索引**拓扑排序后的 Slice 列表（主线程只读索引头部——账本在 slice 文件，worker 派发直接给 `detail:` 指向的文件路径），**按真实依赖派发、按 `parallel_group` 单写者收尾**（稳定输入可核验时跨组提前派独立worker；公共路由等仍等closer，缺声明保守沿用拓扑等待）。每个 parallel_group 三步：

1. **组内 worker 派发（每 slice 恒 1 个 worker + 长杆先行）**：派发前按 [资源增量协议](references/resource-deltas.md) init 本组完整 workers + closer 清单，绑定实际计划项、attempt 和资源路径。组内按 pages_owned **降序**派发——最长链路最早开跑；每个 slice worker 跑 Step 3a/3b/3c + **自身页内**接线。**安全阀（判断式，默认不拆）**：编排者判断某 slice 明显过大（页数 / 锚点异常多）→ 可按**依赖断面**拆 2~3 个 worker（如 VM/model 层 ∥ service+接线层），文件集不相交、各自报信封，closer 照常收口；**禁止按 Step 3b/3c/3d 逐步拆 subagent**（步骤横切丢上下文、不买墙钟）。
   - 所有 worker 只写自身 scope 文件，禁碰共享文件（单写者纪律、任务资源增量与 plan 产物只读契约见 agent-prompts/_common.md）。
   - 派发 prompt 附 `Base 契约: spec/execution/base-contracts.md`（§4f as-built 摘要）**指针，禁内联契约正文**。
2. **group-closer（单写者，1 个）**：本组 worker 全部完成后，派一个 group-closer（**`a2h-closer`，mode=group**——五步协议单源固化于 agent 定义；派发参数模板 **MUST 加载** [references/agent-prompts/8-group-closer.md](./references/agent-prompts/8-group-closer.md) + [_common.md](./references/agent-prompts/_common.md)；**末组**——索引 FV 前最后一个 Group——追加参数 `defer_structural_to_fv: true`，其结构验证由紧随的 FV-1 全工程扫描覆盖、免一次重复 group 扫描，中间组禁用）：跨文件接线（各 slice 的 cross_slice_edits + HomePage embed wires；registry 状态变更记 writeback manifest，plan 产物零回填）→ 资源 sweep、自身增量 submit、全任务资源 check/merge/require-merged → 按冻结compile policy执行真实组编译，或保留pending并交Stage3真实gate（不得把deferred记编译PASS）→ **结构 fix-forward**（自调 `mode=group` + 自修 ≤3 轮直到 CONVERGED，非收敛才冒泡）→ 产 writeback manifest（group brief 全文 + 账本变更集合，主线程 apply 落盘，协议同 §3b）。
3. **主线程仅处置冒泡**：结构验证（`mode=group`）已合入 group-closer 自身 fix-forward（§5e）；主线程**只在 closer 回传 escalation（STALLED/REGRESSED/EXHAUSTED）时**介入——按 dispatch_prompt 派专家 repair worker（feat→worker / ui→converter） / 标 BLOCKED。

**编排规则**：
- **组容量约束**（计数口径与上限的权威 = a2h-plan Step 5，此处不复述）：plan 已据此拆分 parallel_group；execute 遇超限组或多 complex 情况可进一步拆分。plan 标注**附挂**的孤立 slice 搭宿主组的编译与验证。
- **组间 `depends_on`**：按dependency-dispatch核对实际稳定输入；依赖共享装配的consumer等closer，已发布且不会再写的独立接口可让consumer提前开工。原group检查点和单写者不变。
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
| `pending` / 不在 ui-plan | ui-snapshots 存在 → 调 a2h-ios-converter；缺失 → 触发 §7 Phase A 按需模式；转换后 status→converted + 派 hmos-builder（STAGE_HINT=stage-3-slice-{name}）验证 |
| `verified` | 跳过 |

UI 补充必须引用 Base-6 公共组件库（Design Tokens + 共享组件）。worker 同时承担 `forward-ref-uncertain` 二次审视（返回 `uncertain_regions_resolved[]/retained[]`，主线程据此更新 registry）——完整流程与占位禁令 **MUST 加载** [references/agent-prompts/4-step3a-ui.md](./references/agent-prompts/4-step3a-ui.md) + [_common.md](./references/agent-prompts/_common.md) 作为派发模板，不得简化为 body 摘要。

### 5c. Step 3b: ViewModel + 状态管理（C7 三段式）

<HARD-GATE>
生成本切片 ViewModel。**complex 强制三段式**（源码理解 → 差异清单 → 实现，一次调用），simple 仅第三段；**anchors 经 `source_anchors_ref.source` 读 spec**（grep-first 定点消费，不整读源文件）；spec 已有『源码 5-role 摘要』时第一段只核对 + 产差异清单，source-notes.md 仅含差异清单；complex 必产 `spec/execution/source-understanding/{slice}-source-notes.md`。三段各自的判据（9-role 摘要含类名否则 FAIL / 二型锚点 `源:`·`决:` 落点规则 / `[真机]` 不豁免实现）**MUST 加载** [references/agent-prompts/5-step3b-vm.md](./references/agent-prompts/5-step3b-vm.md) + [_common.md](./references/agent-prompts/_common.md) 作为派发模板，不得简化为 body 摘要。
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

Stage 3 完成后，输出实际 Slice、页面和编译状态，按所选产品执行主题、字面量、死壳、载体、交互命中和资源引用检查。保留真实接线、状态、触摸、资源缺件等有具体产品后果的检查；名称、文本和风格候选只作提示。

这些 detector 在 FV-1 使用同一权威结果：规则版本、配置、产品范围和实际输入签名一致时复用当前完整原始报告及其摘要，不要求重复运行。相关修码、规则或 SDK 变化只使对应结果失效；不得把旧 PASS 用于新输入。

随后进入 FV-1 结构收口和 FV-2 当前 SDK 构建。冷启使用 `cold_start_probe.sh` 只读已有、已授权采集的 CLI 进程/日志文件，显式提供应用、PID 和时间窗；命令不主动操作设备或读取界面。只有已确认首启需联网的场景才检查该进程请求，缺少观察记 unverified/not_run；真实归因崩溃仍作为对应运行缺陷处理，不因设备或网络日志缺失令其他验证轴全局失败。

---

## 6. Final Structural Closure（Stage 3 全部完成后 HARD-GATE）

<HARD-GATE>
Stage 3 全部 group brief 落地 + §5f 统计输出后，派 **`a2h-closer`（mode=final）**——其内部**调用 `$arkts-structural-closure` skill（参数：`mode=pipeline target=final`）** 跑整工程兜底（与 Stage 3 解耦，独立一次性 loop），CONVERGED 后产 `writeback-final.json`（收尾 brief 全文 + defer 末组补翻集合，主线程 apply 落盘，协议同 §3b）。

> ⚠️ **禁止用 grep 替代**

**收尾 evidence（缺失或 `final_state ≠ PASS` → 不允许进 a2h-verify）**：

- `spec/execution/autofix-log/round-<R>/loops-final-structural-closure.json` — `final_state == PASS`（arkts-structural-closure finalize 产出）
- `spec/execution/briefs/final_structural_closure_brief.md` — 嵌入 loops.pipeline 段

CONVERGED + evidence 就位 → FV-1 完成。CONTINUE 按 dispatch_prompt 派 repair worker（feat → `a2h-migration-worker` / ui → `a2h-ios-converter`）后重调；其他 verdict 处置见 skill 自身 SKILL.md §3.3。

**FV-2 当前 SDK 构建**：FV-1 之后执行或引用真实构建命令。输入、产品、配置、SDK 与产物摘要绑定一致且命令成功时，合法的 `all tasks up-to-date` 缓存命中有效；不强制 touch 或 clean。旧产物、错产品/配置、真实编译错误或缺少当前命令证据不能通过。修码后重新核验其实际依赖的构建/结构结果；未影响的同签名结果可复用。

</HARD-GATE>

---

## 7. Phase A 按需触发机制

Stage 3 Step 3a 发现目标页面 ui-snapshots 数据缺失（status 非 converted/verified **且** `ui-snapshots/page_NNNN/` 缺失或不完整）→ 自动触发 a2h-spec Phase A 按需模式：单页源码分析 → 最小数据集 → 增量更新 ui-manifest + page spec → 继续 converter，不中断 Pipeline。完整触发条件 / 流程 / 降级处理（无静态 layout 时骨架 + registry 占位）**MUST 加载** [references/phase-a-ondemand.md](./references/phase-a-ondemand.md)。

---

## 8. Skill 绑定机制

### 8a. 主路径：plan 标注（三层承载）

- **Base / FV 任务**：读 base-plan.md / 索引 stanza 的 `suggested_skills:`。
- **Slice 4 步默认映射**：3a=`a2h-ios-converter` / 3b=`arkts-state-manager` / 3c=`arkts-data-layer` / 3d=closer 链（权威在 a2h-plan §4 表 + agent-prompts 模板绑定，plan 不复述）。
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

> **Remember**：结构性验证唯一入口 = `$arkts-structural-closure` skill，禁止 grep / 自跑 scripts 替代；中间步骤看 verdict 即可，§6 收尾必产 `loops-final-structural-closure.json` (PASS) + brief md；Stage 0 资源前置最先跑；plan 产物只读、接线完成性由 verify_slice_wiring 机械判定；跨文件接线与状态账本由 Batch 收尾 / group-closer 单写；资源 JSON 使用任务增量、唯一 closer 合并与回写前收据门禁；registry 登记仍按 `_common.md` 发号 append；合法占位 = 已登记的 5 类 kind 占位（§2.1），未登记 / 自由文本一律 FAIL；execute 按 §1.1 铁律查 decision-ledger 推进、不交互式追问（未命中写「决策缺口」阻断）。

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
