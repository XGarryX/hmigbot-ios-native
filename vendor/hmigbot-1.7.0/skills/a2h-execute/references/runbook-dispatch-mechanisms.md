# a2h-execute · 拍①–④机制细则（脚本已强制）

> 本文件由 `a2h-execute/SKILL.md` 原文**逐字搬出**（M1 token 减量：主会话 runbook 只留循环所需，细则集中于此）。读取时机：拍①返回 `wait`（含 `retry_after_sec` / `stale_dispatches[]` / `health_probe:true` / `paused:true` / `pending_repair_instructions[]`）、`dispatch` 带 `more_ready`、`repair`、`approval`、`escalate`、next_batch exit 1、编译门 `graph-mismatch`，或需要解释某条 runbook 一行规则时。

## §1 前置自检原文

只查两件事，不满足则**停在说明页呈报用户，不静默降级**：

1. 会话能执行 `python3`（`python3 --version` 有输出）；
2. 会话权限模式允许无人值守派发 subagent 与执行脚本（宿主子代理并行上限自检：`host_parallel_check.py`，install.sh 装机时自动跑；上限低于计划 max_parallel 时超出的子代理会静默挂住）。**四拍之外的原生子代理与窗口共用同一宿主额度**（E19）：a2h-spec 的 api-inventory 后台代理、主会话同期清单里派出的任何 agent 都占线程；计划并行度 = 宿主上限 − `gates.side_agent_reserve`（缺省 1），主会话保证四拍之外同时在飞的代理不超过该预留数——超了就是 test1 那种「在飞零产出」。

通过后读 plan：`spec/waves/plan-<wave>.json` 存在且非空（缺 → 回 a2h-plan）。主会话只看 `wave` / `max_parallel` / tasks 数，**不读 tasks 正文、不读任何 prompt/结果正文**——一切判断在脚本里。

## §2 四拍循环 action 表原文

E199（拍④⑤合一）：`--then-next` 让落账命令在同一进程里接跑拍①，主会话每轮少发一次请求（AIPPT_930 主会话 land_results 196 次 + next_batch 222 次，每次请求重发约 27 万上下文）。只在波首（还没有任何落账）与恢复剧本里才单独跑①；落账后再手跑 `next_batch` 只会得到 `wait`（E41 在途语义不变，不会重派）。

拍①用 `--brief`（V21）：stdout 第一行 `action=… batch=N reason=…`，随后每任务两行（`id | agent | model | result` + `prompt: <dispatch_prompt>`），派发时逐行照抄；`--json` 仍输出 `{action, batch[], reason, missing[]}` 供脚本消费。按 action 分派（**除本表动作外主会话无任何开放决策**）：

| action | 主会话动作 |
|---|---|
| `dispatch` | 拍②：并行派发 batch 全部任务；batch 元素 = `{id, agent, prompt_file, result_path, resume_key, model}`。**`prompt_file` 由脚本选，主会话照抄**：半成品任务优先 `<任务书>.resume.txt`（V14 resume_guard 产）；因静态运行期 P0 / 界面形态 P1 判退的任务优先 `<任务书>.repair.txt`（E262 land_results 产的**补漏小任务书**，只带违规清单 + 修法 + 标准写法 + 回执增量指令，元素带 `mode: "repair"`），深度浅页 / 主题回执判退仍派原任务书 |
| `gate` | 就绪节点是 reduce 门禁 → 直接跑拍④（land_results 扫描就绪 reduce 并 subprocess 执行 gate_check / contract_sync / report_aggregate；主会话不亲手跑门禁命令） |
| `approval` | 呈现 reason 指向的审批材料（suspend payload 文件），等用户批复；批复按材料内指引落账后回①。**无人值守（E157）**：审批材料落盘时 land_results 已自动批复（摘要 `approval.auto_approved=true`，留痕 kind=approve）——**不停、直接拍①**；只有 `gates.unattended` 未开时才等人 |
| `wait` | 存在 DISPATCHED 未落账（`missing[]` 列明）→ **任一代理回执到达即跑拍④**（V20：land_results 只落账已有 result 的任务，仍在跑的记 `pending[]` 不判违纪、不计 attempts），拍①按 `max_parallel − 在途数` 自动补吐——**禁止等整批全部回来才落账**（AIPPT-v4 实证：整批等待 + 缺 result 误判让 18 域切成三波 61 分钟）。代理终止通知已到却无 result → `land_results.py ... --missing-as-failed <id>` 显式判缺失；派发超 `--stale-minutes`（缺省 90）**只列入 `stale_dispatches[]` 不判缺失（E50）**：先 `list_agents` 确认终态——仍在跑就 SendMessage 催写回执，已终止再 `--missing-as-failed`；`--stale-as-missing` 才恢复自动判缺。AIPPT_0903 test4 实证（2026-09-05 01:48–03:29）：宿主休眠 1h41m，主会话与 3 个 closure 代理同时冻结，醒来后阈值把 2 个正要回执的存活代理判 RETRY_NEEDED 重派。带 `health_probe:true` 时（尾部连续 INFRA_FAIL ≥3，疑似 529 潮）→ 按剧本 R8：先派 1 个极小探测任务确认平台恢复，**重派前先跑 `resume_guard.py --plan <plan> --state spec/state/state.json --json`**（V14 半成品审查：被中断任务的白名单有遗留改动时生成 `<prompt>.resume.txt`，拍②自动优先用它），再以 `next_batch.py --assume-healthy` 重取批，**禁止立刻整批重派** |
| （拍④输出）`next` | E199：`--then-next` 下 `next.ran=true`，`next.action` 就是拍①结果（brief 文本紧随落账行）——按本表处置，不再跑①。未带 `--then-next` 时退回 V21：输出 `next.cmd`（拍①命令）——**同一条消息里紧接着执行**，不等、不问、不总结（v5 实证主线落账 8 次没接拍①，3 域白等 9.5 分钟）。`stale_results[]` 非空 = 重派后旧结果被跳过，属预期 |
| `done` | 本 wave 完成，**读输出的 `next` 字段照走（K0.2：交接由脚本给指令，不再散文交棒）**：`next.kind=wave` 且 `exists=false` → 先跑 `next.generate` 生成下一波 plan 再回①；`exists=true` → 换 `next.plan` 回①；`next.kind=skill` → `cat next.message`（`spec/reports/handoff-message.md`）逐字转发给用户，再 `$a2h-verify`。无 `next` = 场景 profile 自定义波，按 profile 收尾 |
| `escalate` | 重试超限 / 门禁升级 → 呈现升级材料，按 `references/recovery-playbook.md` 处置；禁自动续跑。输出带 `hint` 时照 hint 走：门禁根因修复后用 `land_results.py --rerun-reduce <id>` 复位重跑（剧本 R7），**禁归档重建账本**。closure 判 STALLED 时 `next.kind=escalate`（E52）：`closure-backlog.json.resolution` 的 `allow_stalled` / `defer` **只能由用户裁决后写入**（同 E47 批复：带 by + quote 原话），主会话自己写 = 伪造裁决，交棒时 E49 会把它列给用户核对 |

## §3 派发纪律原文（拍②③）

- 每任务 = `spawn_agent` 派发：`agent_type` = **batch.agent_type**（E70：不含版本的角色名；`batch.agent` 仍是 `名@版本` 供 lint 校验，宿主 spawn_agent 不认带版本的名字），`prompt` = **batch.dispatch_prompt 原文**（一句任务书文件指针，worker 第一步 Read 任务书全文）。**任务书正文不进主会话上下文**（V20，AIPPT-v4 实证：逐个 cat 100KB 任务书派发耗 0.6 分钟/个，缓存读占成本 46%）。
- **单条消息**并行发出 batch 内全部 Task，不分先后、不挑顺序、不附加解说。
- 硬禁令三条（journal 抽查项，违者即纪律事故）：
  1. **不改写 prompt**——dispatch_prompt 原样发出；任务书文件（prompt_file）不增删改一字、不摘要、不「优化措辞」；
  2. **不总结任务**——派发消息只含 Task 调用本体；
  3. **不读结果正文**——`result_path` 的内容主会话永不 Read，回执一行是主会话可见的全部。
- 回执纪律：worker 把完整结果写 `result_path`，最终消息只回一行 `OK <result_path>` 或 `FAIL <result_path> <一句原因>`。违纪（多话/缺行）不追问不补救；缺文件分两种：代理仍在跑 → land_results 记 pending 等它；代理终止通知已到仍无文件 → `--missing-as-failed <id>` 落账 `RETRY_NEEDED` 由下一拍①重派（最多一次）。

## §2/§3 机制 bullet 原文


> E173（AIPPT_930 移植）：`round0_precheck.py` 定位 legacy skills 根时优先本脚本所在安装根（`<skills>/a2h-execute/scripts` → `<skills>`），显式 `--skills-root` / `ARKTS_SKILL_DIR` 仍优先——Codex 装机（`.agents/skills`）无 `arkts-skills/skills` 祖先，此前退到默认根后 lint R7 误报检查脚本缺席。

2. 会话权限模式允许无人值守派发 subagent 与执行脚本（宿主子代理并行上限自检：`host_parallel_check.py`，install.sh 装机时自动跑；上限低于计划 max_parallel 时超出的子代理会静默挂住）。**四拍之外的原生子代理与窗口共用同一宿主额度**（E19）：a2h-spec 的 api-inventory 后台代理、主会话同期清单里派出的任何 agent 都占线程；计划并行度 = 宿主上限 − `gates.side_agent_reserve`（缺省 1），主会话保证四拍之外同时在飞的代理不超过该预留数——超了就是 test1 那种「在飞零产出」。

E199（拍④⑤合一）：`--then-next` 让落账命令在同一进程里接跑拍①，主会话每轮少发一次请求（AIPPT_930 主会话 land_results 196 次 + next_batch 222 次，每次请求重发约 27 万上下文）。只在波首（还没有任何落账）与恢复剧本里才单独跑①；落账后再手跑 `next_batch` 只会得到 `wait`（E41 在途语义不变，不会重派）。

- **错峰派发（E34，AIPPT_0903 实证）**：拍①每次最多新派 `gates.dispatch_burst` 个（缺省 4），距上一批派发不足 `gates.dispatch_stagger_sec`（缺省 60）时返回 `wait` + `retry_after_sec`——主会话**等够该秒数再拍①**，不派新任务、不催代理。窗口本身不变，只是分批填满：同一分钟起跑 11 个代理各读 15 万 token 是 429 的直接原因，回执驱动的逐个补位从未撞限。两个键读自 workflow-params.gates，不参与契约哈希比对。**错峰不等于等回执（E80）**：`dispatch` 返回带 `more_ready` + `retry_after_sec` 时，说明还有就绪任务被错峰扣住而窗口有空位——到秒数就再拍①补位，**不要等这批回执齐了再拍**（AIPPT_0903 r3 实证：11 槽只跑 4 个，9 分钟一轮）。只想看下一拍会派什么而不真派，用 `next_batch.py --dry-run`（E82：不写 dispatch.json、不拍快照、不自动批复；不带它的拍①一律是真派发）。操作上：拍③的 `wait_agent` 超时要设成 `retry_after_sec`（秒→毫秒），超时返回即拍①，不是无限期 wait （r4 实证：提示给了，主会话仍连续 wait 7 分钟、4 槽空转）。**E134**：`gates.unattended` 下错峰**缺省关闭**（每拍填满窗口；要限流就显式写 `gates.dispatch_burst`）——主会话只在回执到达时拍①，任何按秒补位的提示/命令都不会被执行，每拍 4 个的上限等于把窗口压成 4 槽。**E133**：错峰 wait 与带 `more_ready` 的 dispatch 自带 `next.cmd`（`sleep N; next_batch …`）——派完本批代理后**直接执行该命令**（它自己会睡够秒数再拍①），不要先 wait 回执（AIPPT 2026-09-06 16:13–16:54 实证：11 槽只跑 4 个、四批派发间隔 11/8/22 分钟）。**运行期在途上限 `gates.max_in_flight`（E35）**：与计划 max_parallel 取小值，0 = 不限；账号被限流到只承受 1–2 个代理时改它，不重生成计划（改 waves.*.max_parallel 会变契约哈希、撞 dispatch 冻结记录）。**暂停开关 `gates.dispatch_paused`（E36）**：`true` 或波名列表，命中本波时拍①只出 `wait` + `paused:true`（在途照常落账，不派新任务），用于波边界切并发或等额度；解除后再拍①。
- next_batch **exit 1 = 契约违规**（典型：plan `contract_hash` 与 state 记录不一致）→ 停，契约变更必须显式走重生成 + 部分重跑（§6），禁改 state 硬闯。
- **契约接线是任务书的一部分（I5）**：所有写码任务书末尾带「契约接线」段（来自 `contracts.json#wires`，由 a2h-plan `a3_finalize --op wires` 从各域 spec 的 INTERFACE 第八维汇成）：消费方看到要发起的导航（目标路由名、参数、提供方）与要 import 的别域符号，提供方看到谁会跳进来、谁依赖自己的符号。**禁止自造路由名或在本域重造别域符号**。写产物的波在 build 后挂 `reduce:wires-check`（`verify_wires.py` 逐条 nav-edge 核销：消费方有 pushPath 到目标路由名 + 提供方有 `<Page>PageBuilder`），只报不判，handoff-check 呈报接线率。AIPPT_0903 实证：wires=0 时接线率被探针托到 1.13，实际 38 处 startActivity 只接了 5 处、运行白屏。
> **接线核销的三把尺子（E102/E103/E100）**：`verify_wires` 除 nav-edge 外还静态核销 service-call / event / store 三类 wire（只报不判），并以 `spec/reports/source-inventory.json` 的源码导航调用点为**绝对分母**算接线率（契约里没有的边也算），旅程链（spec/journeys.json）逐链判通；`handoff_check` 呈报 symbol-wires / nav-sites / journeys / class-coverage（E94：安卓类 → 鸿蒙声明，UI 缺页即 blocked）。页面块任务书的接线段只带本块页面的边（E79）。E170（AIPPT_930 移植）：`verify_wires` 的消费方文件集沿真实使用的本地 import 图追到委托导航的共享 ViewModel（未使用/type-only/外部包不跟）；`verify_handoffs` 对 `<配置>.json5#<字段或权限>` 型 forward-ref 触发器按真实配置求值（requestPermissions 实际声明或字段非空，注释/描述文本不算），此前 corpus 只含 .ets 永判「文件不存在」。
- **修复类侧代理（hmos-builder / repair）只能在本波零在途时派**：编译门 verdict 提示派 builder，先 `list_agents` 确认没有本波代理在跑；有则等回执落账再派。并发改同一文件必互相覆盖（AIPPT_0903 2026-09-05：builder 与 closure converter 同时改 MemberCenterBody.ets，修好的 19 错下一拍回魂）。无人值守下脚本同样只在零在途时出 `repair`。
- **无人值守模式（U1，`gates.unattended: true`，运行期开关不进哈希）**：用户裁决「全自动、多做派」时开启。每个人工停点由脚本按确定性策略裁决并留痕 `spec/state/auto-adjudications.json`，handoff-check 逐条呈报：① 审批门材料已产 → 自动 approve（多做）；② 阻断型门（compile/build/pagemap/fence-audit/round0）升级 → 拍①出 `action=repair`，主会话按 `repair` 字段派**一次** a2h-migration-worker，落地后按 `then` 重跑该门，仍红 → 记欠账继续；③ 其它 escalate=True 的质量线门 / 重试耗尽任务 → 记欠账（waive）继续，下游按 failed_handled 就绪；④ closure STALLED 首次 → 自动 allow_stalled 重跑一轮（任务书处方由 E53 补），二次 → 自动 defer 进 closeout；⑤ 前波 ERROR 不拦；⑥ 超时在途按缺失重派。**主会话仍禁止自己写审批 / resolution / 契约**——需要决定的点脚本已替你决定并记账，无需也不得再伪造。关闭开关即回到人在环内（E46/E47/E52 全部生效）。
- **审批文件只能在用户明确答复之后写（E47）**：`approval` 动作到手 → 把 suspend payload 的要点呈给用户 → **停下等答复** → 按原话写 `{"approved": true, "by": "user", "quote": "<用户原话>"}`；缺 by/quote 的批复脚本不认，主会话不得替用户批。AIPPT_0903 test4 实证（2026-09-04 17:15）：fix-backlog 13 条 open / 7 条 P0 待批，主会话自写 approved:true by:user，随后 escalated-ratio 红灯被它当作可跳过的障碍。
- **主会话自己崩了怎么办（E115）**：用 `python3 $SKILLS/a2h-execute/scripts/unattended_runner.py --project <root> --prompt <prompt.md> --log <events.jsonl>` 起主会话；它在 turn.failed / 模型满载 / 429 退出后把在途任务 `--infra-fail` 改判（不耗配额）、退避后原 prompt 重启（SKILL 按 state 续跑），最多 3 次，留痕 `spec/state/unattended-runner.json`。AIPPT r6 实证：两次满载崩溃的恢复此前全靠人手。
- **U1 repair 的任务书与次数（E139/E139b）**：compile 门 repair 任务书带**全量**编译错误清单（按文件分组、去重，上限 120 条；ArkTS strict 规则错也列入），不再只给前 14 条；第一次 repair 后错误数下降但仍红 → 允许第二次（上限 2），仍红才记欠账（AIPPT 2026-09-06：每轮 repair 都把错误压到 1 条然后记账，最后那条永远没人修）。E171（AIPPT_930 移植）：`repair` 动作的任务书同时落盘 `spec/a2h/_work/repair-prompts/<task_name>.txt`（`repair.prompt_path` / `dispatch_prompt`），在途期间拍①的 `wait` 带 `pending_repair_instructions[]` 原样回投同一份——宿主截断 repair 动作输出时仍能派出去，不是二次裁决。
- **资源引用回填（E138）**：各实现波尾 `reduce:resource-sweep` 带 `--backfill-refs`——扫产物 `$r('app.*')` 引用、没播种的机械补写（string 反查字面量台账/人话化；color/float 反查不到给显眼占位并记 `spec/reports/resource-backfill.json`；media/integer 只报不造），编译门不再被『Unknown resource name』刷屏（wiring 波 212 错里 167 条）。E174（AIPPT_930 移植）：sweep 对回执显式请求的资源名『同值也保留请求名』（页面已 $r() 引用该名，只回既有别名会落空）；E138 回填的占位（洋红/1vp 哨兵、人话化 string，报告每条带 `value_source`）进 `spec/reports/resource-placeholders-<module>.json` 来源账，后续 sweep 收到同名真实值时只对『账上 pending 且当前值仍精确等于占位值』的条目原名替换，其余仍记 conflicts；E155 哨兵与纯密度目录（xxldpi 等）已转换资产同名时，回填先把真实字节复制成 base 回退并删哨兵（报告 `assets_restored`），纯密度目录已有的资产也不再播哨兵（dark/语言/方向变体不算）。
- **闭包看类级覆盖（E140）**：`gate:closure-scan/rescan` 带 `--class-coverage`——source_inventory I3 缺失的安卓类按域归 owner 进 closure-backlog（code=class-unmigrated，CV-*），有未迁移类就不算收敛；此前 rescan 只看 detector，非 UI 137/212 也能判『收敛』直接 closeout。
- **closure 欠账全无主（E116）**：无人值守下不 escalate，记 `closure-unowned-defer` 进 auto-adjudications 后跳过 closure 波进 closeout，handoff 逐条呈报。
- **前波 ERROR 未收口不得开新波（E46）**：拍①出 `escalate` = 人裁决，唯一合法下一步是呈报用户；不得 generate_waves 下一波、不得改契约六件绕过。脚本侧：前波 `workflow_status=ERROR` 时新波拍①只出 escalate，用户明确裁决跳过才加 `--allow-open-prev`。同一实证：主会话跳过 escalated-ratio 升级直接生成 wiring 波，遇「owner app-entry 无白名单」又改了 `spec/blueprint/ownership.json`，auditfix / closeout 两份 plan 契约哈希随即失配。
- **拍①不可重复调用（E41）**：`next_batch` 每次调用都把返回的 batch 记为在途（契约冻结记录），**它不知道你有没有真的 spawn**。一次拍①返回的 batch 必须在同一条消息里逐个 `spawn_agent` 完毕，才允许再拍①；中途换 workdir 重跑、或「再确认一下」重跑拍①，脚本会把上一批当作已在途、吐出下一批——上一批就永远没人跑，直到 `--stale-minutes` 或主会话判缺失才重派、白耗一次 attempts。AIPPT_0903 test4 实证（2026-09-04 20:47:51 拍① 得 p1–p4 → 未 spawn → 20:49:03 又拍① 得 p5–p8 只 spawn 后者）：p1–p4 空等 40 分钟后按缺失重派，attempts 直接到 2。若拍①后发现没 spawn，正确处置是 `land_results.py --missing-as-failed <ids>` 立即判缺失让下一拍①重吐，不要再拍①。
- 滚动窗口由脚本裁决：`max_parallel=0` 一次吐出整个就绪 map 组；`>0` 首批 N 个、此后回执驱动补位（完成一个补一个）。**实现里不存在「第 M 批」概念**，主会话不得自行切批/限流/重排。
- 四条拒绝规则（非终态未落账拒吐新批 / hash 不一致拒续跑 / 待审批出 approval / 重试超限出 escalate）使「跳过落账」在机制上不可能——拍①④两条命令不跑则无法推进。

- 回读申报（消费信任协议）：任务书注入信任分级纪律（T1 契约段/摘要机器节禁回读；T2/T3 矛盾回读须在输出 `rereads[]` 申报）；land_results 把申报计数留痕 journal，复盘聚合为定级质量报告——主会话不干预、不追问。
- 基础设施失败例外（K7，V21 改法）：worker 回 FAIL（529/限流/断连）且 result 未落盘 → `land_results.py … --infra-fail <id>[,<id>]` 直接落账 `INFRA_FAIL`（不再把回执写成占位文件——v5 实证占位文件在重派后被重复扫成 INFRA_FAIL 四次、误触 health_probe）；旧手法（把一行 FAIL 回执原文写进 result_path）仍兼容；land_results 对命中 529/overloaded/连接类特征的非结构化失败记 `INFRA_FAIL`：state 回 pending、**不耗重试配额**，由拍①按新任务重吐。落账时白名单内的机械 schema 偏差（对象数组→字符串/标量→数组/domain 从任务 id 推导）会被自动规范化后入账（journal `normalized` 字段留痕），不再为此 RETRY。

- **每一条回执到达即跑拍④→拍①**（E38）：`wait_agent` 醒来只要 `list_agents` 见任一代理 completed，立刻 `land_results` 落账它、再 `next_batch` 补位，其余仍在跑的记 `pending[]` 不影响。**不得等本批全部回来再落账**——AIPPT_0903 test4 实证（2026-09-04 20:00–20:25）：主会话按「批」等最后一个回执，在途从 4 空转到 0 才补 4，窗口 11 从未填满，批间空窗 4–10 分钟。缺回执（worker 确认终止）也照跑④，重派与否由脚本裁决。
- **重派前先确认代理已终止**（V21，§15-4）：限流（429）时代理多半仍存活、只是暂停——`ListAgents`/`TaskOutput` 见其在跑就 **SendMessage 催写**（「按任务书回执纪律写 result 并回一行」），不重派、不 `--missing-as-failed`；确认终态仍无 result 才走 `--missing-as-failed`。v5 实证：8 个「重派」任务原代理还活着，重派 = 双倍付费 + 两份半成品。
- **主会话不写检查脚本**（V21 硬禁令 4）：查状态一律 `python3 $EXE/scripts/wave_status.py --plan <plan> --state spec/state/state.json`（每任务状态/attempts/派发时刻/已用分钟/result 新旧 + journal 尾部非 OK + reduce 终态）；`--json` 输出**禁止** `| python3 -c` 二次加工（v5 execute 期 98 段手写 python、176 次二次加工）；需要新查询面就改 wave_status 并回流 bundle。E167（AIPPT_930 移植）：重入波的 reduce 终态与 journal 尾部按本轮 run 标签取（输出带 `run_tag`），与 next_batch/land 的 E55 同源，第二轮不再显示首轮的 REDUCE_PASS/FAIL。
- `contract_hash` 只在 plan ↔ dispatch.json 之间比对（派发时冻结），**不对 contracts.json 实时重算**——修 contracts.json（如 merge-deferred 回写、手工置 resolved）是安全的，不会触发拒绝规则；只有重生成 plan 才会换 hash（v5 实证主线误以为改契约会撞门，绕路修复）。
- 孤儿/接线类临时任务（编译门 `graph-mismatch` 后的接线）**按 owner 切分派发**：用 `spec/reports/orphan-tasks.<gate>.json`（gate_check 产出，每份 ≤12 文件）一份一个代理，禁「N 个文件一个 agent」（v5：49 个孤儿一个代理两次撞 80 轮上限、382k token 无报告）。
