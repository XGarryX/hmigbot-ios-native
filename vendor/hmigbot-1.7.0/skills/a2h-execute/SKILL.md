---
name: a2h-execute
description: A2H 迁移执行引擎（四拍循环调度器）：读 a2h-plan 产出的 plan-<wave>.json，next_batch 取批 → 单条消息并行派发注册 agent → 一行回执 → land_results 落账，循环至 done；派谁/派多少/门禁/审批/重试/升级全部由脚本裁决，主会话零开放决策。当用户说"执行迁移""开始执行""按 plan 开始做""继续执行"时触发，支持 --wave/--domain/--retry-failed/--resume 部分执行与断点/换会话/换宿主续跑。不要用于：生成 Spec（用 a2h-spec）或计划（用 a2h-plan）；plan 未就绪先跑 a2h-plan。
metadata:
  arkts.stage: impl,fix
  arkts.consumption: stage-entry
  type: pipeline
  domain: migration
  tags:
  - pipeline
  - migration
  layer: pipeline
---

> **Codex subagent dispatch convention.** This skill dispatches subagents. In Codex, spawn them with the `spawn_agent` tool, passing `fork_turns` **verbatim from the batch entry** (拍① 下发；按波固定：understand/infra/domains=`none`——任务书是唯一输入，继承父上下文纯属浪费且带污染风险；修复/接线波=`all`。取自参照运行 236 次派发的实际编排，**不得临场裁量**) and `agent_type` = the role name **exactly as written in this skill** — the roles registered under `.codex/agents/*.toml` use the same hyphenated names, so no translation step is involved: `a2h-activity-converter`, `a2h-android-analyzer`, `a2h-domain-worker`, `a2h-factchain-runner`, `a2h-migration-worker`, `ad-profile-builder`, `compose-fact-analyzer`, `hmos-builder`, `scenario-builder`, `visual-fixer`, `visual-fixer-reviewer`. The built-in `general-purpose` agent_type is unchanged. (Claude's `subagent_type` field is written `agent_type` for Codex; `Agent(...)` dispatch calls are `spawn_agent(...)`; there is no `Task` tool in Codex.)
>
> **Join 协议（收口五条款）。** Codex 子代理完成后**不会**唤醒主会话——结果必须由派发方主动收口，违者=静默卡死（实测事故）。
> ① **循环 wait**：每个 `spawn_agent` 句柄用循环调用 `wait_agent` 收口；单次超时只代表"还在跑"，继续再调；**禁止以"等待子代理"为由结束回合**。醒后必调 `list_agents` 确认是谁完成——**完成的唯一合法信号 = `agent_status` 为 `{"completed": …}`，绝不是产物文件的存在/条数**（文件会中途落盘，读半截=实测事故）；completed 态会在数轮后从 list 中消失，所以每次醒来都要及时查。正文所有"等待完成 / join / 到点即收"表述一律指此循环。
> ② **死句柄与验收**：连续 3 次超时后调 `list_agents` 核对，可配 `wait_for_artifact.py` 探产物活性；已 completed 且 summary 可读 → 直接消费；句柄消失且从未观测到 completed → 按断点重派（带原 prompt + 已落盘产物，上限 2 次），禁止继续等待。**completed ≠ 验收通过**：join 点跑 `python3 .agents/skills/a2h-join/scripts/join_gate.py --project .` 验产物完整性，FAIL 视同未取回、按本条重派。
> ③ **收口锚点**：本 skill 最终完成报告前必须收口全部句柄（join_gate exit 0）；正文写明的显式 join 点优先按正文执行。发用户门（Gate）时允许句柄跨 Gate 存活，但 Gate 摘要必须列明未收口句柄清单 + 各自的指定 join 点。
> ④ **放行 ≠ 遗弃**：正文"非阻塞放行/到点即收/降级继续"只推迟收口时机，不豁免收口义务。
> ⑤ **fire-and-forget**：仅正文显式声明"结果丢弃/不 gate"的派发（如 a2h-execute 的 env-prewarm）免收口；审计只认 join_gate 内静态 allowlist，正文声明只是文档层。
> **派发纪律**：`task_name` 必须唯一（带 page-id/slice-id/round-N 后缀）；并行派发前把预期产物清单写 `spec/a2h/_work/expected_<join点>.json`（join_gate 对账用，契约只认派发方、不认子代理自报）；**谁派谁收**——sub-agent 内部需要"等齐 N 片再合并"时禁止嵌套外派后自行退出，要么同步自做、要么把分片清单回报主会话代派（sub-agent 一停止，收口能力即丢）。**契约产物必须出自承担任务的子代理**：重派上限后仍产不出 → 如实报缺并停在未完成态；禁止派发方代写占位产物让 gate 转绿（声明过也不行——绿账必须对应真产物）。

# a2h-execute（四拍循环执行引擎）

## 0. 约定

- `$EXE` = 本 skill 目录（运行期取 `ARKTS_SKILL_DIR` 环境变量，冻结分发同形态）；工程根为当前目录。
- 产物路径固定：计划 IR 在 `spec/waves/plan-<wave>.json`（a2h-plan 产出，schema 见 DESIGN §4.1），prompt 在 `spec/waves/prompts/<wave>/`，结果在 `spec/waves/results/<wave>/`，状态在 `spec/state/`。一律落工程 `spec/`，禁落会话 scratchpad。
- 脚本退出码统一：0=PASS/有动作，1=FAIL/契约违规，2=用法错误；`land_results.py` 单列：0=落账完成回拍①，1=FAIL 或用法错误，2=专属「审批/升级材料已呈报」挂起等用户。`--json` 时 stdout 只有单个 JSON 对象，人读信息走 stderr。
- **单写者分区**（主会话与 worker 一律不得手改这三个文件，越权即 PROCESS_VIOLATION）：

| 文件 | 唯一写者 | 内容 |
|---|---|---|
| `spec/state/state.json` | `state_update.py`（land_results 经 subprocess 调它） | 任务/门禁状态账本 |
| `spec/state/dispatch.json` | `next_batch.py` | 已吐批次记录（防重派） |
| `spec/state/journal.json` | `land_results.py` | DBOS 双表形状：`workflow_status[]` + `operation_outputs[]`（resume_key/宿主/状态/result_path/tokens/起止时间） |

## 1. 前置自检

**一键起跑（E208）**：`python3 $EXE/scripts/a2h_run.py --android-src <安卓源码根>`——自检（skill 已装 / SDK / hvigorw / codex）、按 `.agents/templates/CODEX_PROMPT.md` 渲染驱动提示词（已有不覆盖）、调 `unattended_runner.py` 无人值守整跑（撞限自动改判在途并重启）；`--status` 看进度，`--dry-run` 只自检。手动起 runner 的命令见 references/runbook-recovery.md。

不满足则**停在说明页呈报用户，不静默降级**：① 能执行 `python3`；② 权限允许无人值守派发与执行脚本（`host_parallel_check.py`）。四拍之外在飞代理 ≤ `gates.side_agent_reserve`（缺省 1，E19）。

通过后读 plan：`spec/waves/plan-<wave>.json` 存在且非空（缺 → 回 a2h-plan）。主会话只看 `wave` / `max_parallel` / tasks 数，**不读 tasks 正文、不读任何 prompt/结果正文**——一切判断在脚本里。

## 2. 四拍循环（本文件的全部剧本）

```
① 取批  python3 $EXE/scripts/next_batch.py --plan spec/waves/plan-<wave>.json --state spec/state/state.json --json
② 派发  action=dispatch → 单条消息并行派发 batch 内全部任务（纪律见 §3）
③ 回执  每个 worker 完整结果写自己的 result_path，最终消息只回一行 OK/FAIL
④ 落账  python3 $EXE/scripts/land_results.py --plan spec/waves/plan-<wave>.json --state spec/state/state.json --json --then-next
        exit 0 → 输出已含拍①结果（`next.action` / 文本「── 拍①（已代跑）──」），直接按 action 表走②，**不要再单独跑①**
        exit 2 → 呈现审批/升级材料等用户 ； exit 1 → FAIL 停
```

E199：只在波首（尚无落账）与恢复剧本里才单独跑①；落账后再手跑 `next_batch` 只得 `wait`。

拍①用 `--brief`（V21）：stdout 第一行 `action=… batch=N reason=…`，随后每任务两行（`id | agent | model | result` + `prompt: <dispatch_prompt>`），派发时逐行照抄。按 action 分派（**除本表动作外主会话无任何开放决策**）：

| action | 主会话动作 |
|---|---|
| `dispatch` | 拍②：并行派发 batch 全部任务；batch 元素 = `{id, agent, prompt_file, result_path, resume_key, model}` |
| `gate` | 就绪节点是 reduce 门禁 → 直接跑拍④（land_results 扫描就绪 reduce 并 subprocess 执行 gate_check / contract_sync / report_aggregate；主会话不亲手跑门禁命令） |
| `approval` | 呈现 reason 指向的审批材料（suspend payload 文件），等用户批复；批复按材料内指引落账后回①。**无人值守（E157）**：审批材料落盘时 land_results 已自动批复（摘要 `approval.auto_approved=true`，留痕 kind=approve）——**不停、直接拍①**；只有 `gates.unattended` 未开时才等人 |
| `wait` | 存在 DISPATCHED 未落账（`missing[]` 列明）→ **任一代理回执到达即跑拍④**（在跑的记 `pending[]`），拍①自动补吐——**禁止等整批全部回来才落账**。代理已终止却无 result → `land_results.py ... --missing-as-failed <id>`；超 `--stale-minutes`（缺省 90）只列入 `stale_dispatches[]`（E50）：先 `list_agents`——在跑就 SendMessage 催写回执，已终止再判缺失。带 `health_probe:true` → 剧本 R8：先派 1 个极小探测任务，重派前先跑 `resume_guard.py`，再 `next_batch.py --assume-healthy`，**禁止立刻整批重派** |
| （拍④输出）`next` | E199：`--then-next` 下 `next.ran=true`，`next.action` 就是拍①结果——按本表处置，不再跑①。未带 `--then-next`（V21）输出 `next.cmd`——**同一条消息里紧接着执行**，不等、不问、不总结。`stale_results[]` 非空 = 重派后旧结果被跳过，属预期 |
| `done` | 本 wave 完成，**读输出的 `next` 字段照走（K0.2：交接由脚本给指令，不再散文交棒）**：`next.kind=wave` 且 `exists=false` → 先跑 `next.generate` 生成下一波 plan 再回①；`exists=true` → 换 `next.plan` 回①；`next.kind=skill` → `cat next.message`（`spec/reports/handoff-message.md`）逐字转发给用户，再 `$a2h-verify`。无 `next` = 场景 profile 自定义波，按 profile 收尾 |
| `escalate` | 重试超限 / 门禁升级 → 呈现升级材料，按 `references/recovery-playbook.md` 处置；禁自动续跑。输出带 `hint` 时照 hint 走：门禁根因修复后用 `land_results.py --rerun-reduce <id>` 复位重跑（剧本 R7），**禁归档重建账本**。closure 判 STALLED 时 `next.kind=escalate`（E52）：`closure-backlog.json.resolution` 的 `allow_stalled` / `defer` **只能由用户裁决后写入**（同 E47 批复：带 by + quote 原话），主会话自己写 = 伪造裁决，交棒时 E49 会把它列给用户核对 |

- 错峰（E34/E80/E133/E134）：`wait` / `dispatch` 附 `retry_after_sec` → 等够秒数再拍①，不等回执；附 `next.cmd` → 派完本批直接执行；`wait_agent` 超时 = `retry_after_sec`（秒→毫秒）。
- next_batch **exit 1 = 契约违规**（典型：plan `contract_hash` 与 state 记录不一致）→ 停，契约变更必须显式走重生成 + 部分重跑（runbook-partial-execution.md），禁改 state 硬闯。
- 契约接线（I5）：**禁止自造路由名或在本域重造别域符号**。修复类侧代理（hmos-builder / repair）**只能在本波零在途时派**。
- 无人值守（U1，`gates.unattended: true`）：停点由脚本裁决留痕；`action=repair` → 按 `repair` 字段派**一次** a2h-migration-worker，按 `then` 重跑门。**主会话仍禁止自己写审批 / resolution / 契约**。
- 审批文件只能在用户明确答复后写（E47）：`{"approved": true, "by": "user", "quote": "<用户原话>"}`；不得替用户批。
- 前波 ERROR 未收口不得开新波（E46）：不得 generate_waves 下一波、不得改契约六件绕过；用户裁决才加 `--allow-open-prev`。
- 拍①不可重复调用（E41）：batch 在同一条消息里 `spawn_agent` 完毕才可再拍①；没 spawn → `--missing-as-failed <ids>`。
- 滚动窗口由脚本裁决，**不存在「第 M 批」**，不得自行切批/限流/重排。
- **硬规则：主会话不得修改产品文件（`entry/**`）与 `.agents/skills/**`；脚本报错（exit 1 / traceback / 脚本自己解不开的契约违规）= 停机呈报**——按 `references/recovery-playbook.md` + `references/runbook-recovery.md` 呈现材料等用户裁决，不得热改脚本/数据绕过。阶段门 FAIL → 按 `retry_hint` 派修复并重跑；按统一处置阶梯（E266）：能修的必须真派修、**最多 2 轮**；2 轮仍不过或确定模型修不了 → **记欠账放行**（账要记全：修过几轮、每轮失败原因、判「修不了」的依据）；要拍板的模型自决并留痕；**任何分支不得停机呈报人工**（`gates.stage_debt=true` 时例外：仅设备/账号类门允许欠账，需显式开启）。

## 3. 派发纪律（拍②③，硬禁令）

- 每任务 = `spawn_agent`：`agent_type` = **batch.agent_type**（E70：不含版本；`batch.agent` 是 `名@版本` 供 lint），`prompt` = **batch.dispatch_prompt 原文**。**任务书正文不进主会话上下文**（V20）。
- **单条消息**并行发出 batch 内全部 Task，不分先后、不挑顺序、不附加解说。
- 硬禁令三条（journal 抽查项，违者即纪律事故）：
  1. **不改写 prompt**——dispatch_prompt 原样发出；任务书文件（prompt_file）不增删改一字、不摘要、不「优化措辞」；
  2. **不总结任务**——派发消息只含 Task 调用本体；
  3. **不读结果正文**——`result_path` 的内容主会话永不 Read，回执一行是主会话可见的全部。
- 回执：worker 写 `result_path`，只回一行 `OK <result_path>` / `FAIL <result_path> <一句原因>`；违纪不追问不补救；已终止仍无文件 → `--missing-as-failed <id>`（最多重派一次）。
- 基础设施失败（K7）：FAIL（529/限流/断连）且 result 未落盘 → `land_results.py … --infra-fail <id>[,<id>]`（不耗配额；幂等——已改判且未再派发的自动跳过，E237）；不写占位文件。
- **每一条回执到达即跑拍④→拍①**（E38）；**重派前先确认代理已终止**（V21：在跑就催写回执）。
- **重派用哪份任务书由脚本定、主会话照抄 `dispatch_prompt`**：机械可判且修法自带的两类退回（`STATIC_RUNTIME:` P0 / `UI_FORM:` P1）改派**补漏小任务**（E262，只带违规清单与标准写法，实测 token 约为整任务重派的 30%、修复成功率相同）；深度浅页与主题回执仍整任务重派。配额不变（首派 1 + 重派 1）。
- **主会话不写检查脚本**（V21）：查状态一律 `python3 $EXE/scripts/wave_status.py --plan <plan> --state spec/state/state.json`；`--json` **禁止** `| python3 -c` 二次加工。
- `contract_hash` 只比对 plan ↔ dispatch.json，不对 contracts.json 实时重算。
- **主会话不写产物**（E24）；唯一例外编译门判 `quick_fix`（≤ `gates.quick_fix_threshold`）。**禁止**：非编译门 FAIL 后亲手改产物；亲手重跑门禁覆盖报告（只经 `land_results.py --rerun-reduce <gate>`）；亲手跑 `state_update.py` 补账。
- 孤儿/接线临时任务按 owner 切分（`spec/reports/orphan-tasks.<gate>.json`）。降级兜底（无 subagent → 逐个亲自执行）须先呈报用户，禁静默降级。恢复 = 同一工程目录再跑拍①。

## 4. 读取时机（references）

| 触发时机 | 必读文件 |
|---|---|
| `wait` 带 `retry_after_sec` / `stale_dispatches[]` / `health_probe:true` / `paused:true` / `pending_repair_instructions[]`；`more_ready`；`action=repair`；exit 1 | runbook-dispatch-mechanisms.md |
| `action=escalate`；REDUCE_FAIL（R7）；`health_probe:true`（R8）；主会话崩溃（E115）；中断 / 换会话 / 换宿主 | recovery-playbook.md + runbook-recovery.md |
| 触发语「重跑失败 / 只重跑某域 / 从断点继续 / 只跑基建 / 全部重新执行」 | runbook-partial-execution.md |
| `done` 且 `next.generate` 出 `plan-specfix` / `plan-depthfix` / `plan-wiring`；`gate:spec-depth` / `gate:depth` / `reduce:backlog-settle` | runbook-conditional-waves.md |
| `done`（closeout / debt）或 `escalate` 带 `next.wave=debt`（handoff-check BLOCKED 机械补账，E207）；`reduce:grill-autodecide`；`spec/reports/debt-exhausted.json` | runbook-conditional-waves.md |
| `gate:fence-audit`（写 `spec/state/fence-ack.json`）/ `reduce:product-write-audit`；编译门 `quick_fix` | runbook-fence-and-product-write.md + conservative-mode.md §3 |
| `FILES_MISSING` / `DEFERRED_LOCATION_MISSING` / `rejected[]`；`gate:round0-clear` / `findings-gate.json` / `safearea-layers` / `escalated-ratio` | runbook-receipt-trust.md |
| 派 hmos-builder / 修复 worker；CLI 构建僵死或 `00303208` / `00303217` / `00305008` | runbook-build-discipline.md |
| `done` 且 `next.wave=closeout`；`gate:compile-4` / `gate:handoffs` / `gate:cold-start` / `gate:smoke-1page` / `gate:render-static`（off 档静态回退） / `gate:handoff-check` | runbook-closeout.md |
| `done.next` 出 closure 波；`gate:closure-scan` / `gate:closure-rescan`；STALLED（`next.kind=escalate`） | runbook-closure.md |
| 换宿主；无 subagent 能力 | runbook-hosts.md |

## 8. references

- `references/recovery-playbook.md`：八条故障恢复剧本——把执行期开放决策收窄为选择题。
- `references/runbook-*.md`（触发见 §4）：dispatch-mechanisms / conditional-waves / fence-and-product-write / hosts / recovery / partial-execution / receipt-trust / build-discipline / closeout / closure / evidence。
- `references/fragments/`：规则片段（含 0818 蒸馏五件与 v3 蒸馏 runtime-patterns）+ `index.json` sidecar 索引——触发词 / stage 门控 / 字节数元数据 / **catalog（每片段 provenance 来源等级，V5）**，assemble_prompt.py 查表消费（片段增删必须同步 catalog，组装期硬校验；人不必读）。
- `references/conservative-mode.md` / `references/templates/wave-*.js`：**已废弃**（单一形态收敛，见 IMPL-PLAN §7 / DESIGN §7），归档保留勿用。

> **Remember**：主会话只做三件事——跑①④两条命令、照单派发、呈现脚本给的材料。派谁/重试/门禁/审批/收尾全在脚本与 plan 里；不改写 prompt、不总结任务、不读结果正文；state/dispatch/journal 三文件各有唯一写者，谁都不许手改。主会话不改 `entry/**` 与 `.agents/skills/**`；脚本报错 = 停机呈报；阶段门 FAIL 修到 PASS，按统一处置阶梯（E266）：能修的必须真派修、**最多 2 轮**；2 轮仍不过或确定模型修不了 → **记欠账放行**（账要记全：修过几轮、每轮失败原因、判「修不了」的依据）；要拍板的模型自决并留痕；**任何分支不得停机呈报人工**。

---

## 收尾：上报本阶段用量

本 skill 的最后一步（无论经 `$a2h-run` 还是单独触发都要做）：

```bash
.migbot/bin/a2h mark-stage a2h-execute
```

标记 `a2h-execute` 阶段水位（写 stage-marks fact + sentinel，受授权门控、尽力而为）。token 用量由生命周期 hook 上传的会话记录在服务端解析得出，本步不采集。**忽略退出码，绝不阻断。**
