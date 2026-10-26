---
name: android-fact-tree
description: 给**任意架构**的 Android 工程（纯 XML/Activity、纯 Jetpack Compose、或两者混合）产出一份 arkts-visual-verify
  / a2h-spec **能直接消费**的统一 `spec/toolkit-fact-tree.json`（schema_version=1）。它是**统一入口
  + 编排器**——自己不解析源码成树节点，而是先确定性判架构，再分发到对应生成器：纯 XML→toolkit-fact-indexer + app-relationship-tree，纯
  Compose→compose-fact-tree，混合→两者按序叠加 + 缝合跨架构边；最后用确定性闸校验产出。当用户说"给这个安卓项目产 fact-tree/关系树/导航图给
  visual-verify 用"、"分析这个 Android 项目产树"、"不知道是 XML 还是 Compose、先判架构再产树"、"混合架构产树"、"visual-verify
  的前置树"、"android fact-tree"时触发。即使用户只说"分析这个安卓工程"或"给 visual-verify 准备输入树"，也应触发。**入口动作永远是先跑
  `scripts/dispatch.py plan <src>` 判架构**。
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

> **路径约定**：下文 `$SKILLS_ROOT` = 本套 skills 的安装根目录。执行任何脚本前先设一次：`SKILLS_ROOT="$(cd "$(dirname 本SKILL.md)/.." && pwd)"`（用户级安装=`~/.agents/skills`；项目级=`<project>/.agents/skills` 或 `<project>/skills`）。

# android-fact-tree — visual-verify 前置树的统一产出入口（路由 + 编排）

## 0. 定位与角色边界（务必守住）

**使命**：输入任意架构的 Android 源码，输出一棵 **arkts-visual-verify 零改即可消费**的 `spec/toolkit-fact-tree.json`——三条架构路产出的树**字段同构**。

**它是编排器，不是生成器。** 硬边界：

| 角色 | 谁 | 碰源码解析成节点吗 |
|---|---|---|
| **生成器** | toolkit-fact-indexer / app-relationship-tree / compose-fact-tree | ✅ 是 |
| **功能维度生成器** | a2h-functional-registry(无 registry 则自产) → a2h-functional-merge(§3.5 注入 `functional_checks`) | 否(只注入功能维度字段) |
| **本 skill（编排/路由）** | 只做：①确定性判架构 ②分发到生成器（pure_traditional 链 ART∥registry 并行 fork/join，§2A.2） ③确定性校验产出 ④§3.5：无 registry 先自产 → merge 注入 → 机械闸验功能点入树 | ❌ **否** |

> 唯一的灰区：hybrid 路的「跨架构接缝边缝合」（§2C.3）会读一点源码——但它**只缝已有节点之间的边、不造节点**，且只在 hybrid 触发。这是编排器对「没有任何现成生成器能产跨架构边」这一客观空白的正当补位，**不是把生成器的活抢过来**。守住「不造节点」这条线，编排器纯度就在。

**两层结构**：
- **确定性调度/校验层**（`dispatch.py` + 三个闸脚本）——永不碰树内容，能脚本化的全脚本化。
- **生成-编排层**（调用子 skill / 派 agent）——LLM/子 skill 的活，自然语言编排，但**产出必须过校验层的闸**。

---

## 1. 入口：确定性调度（永远先跑）

```bash
python3 scripts/dispatch.py plan <android_source_root>
```
内部跑 `detect_arch.py`（确定性扫 `@Composable` 密度 / `setContentView(R.layout)` 宿主数 / Activity 数 / navigation-compose 依赖 / ComposeView / xml layout 数 + 从 manifest 取 launcher 宿主），输出**三态判定 + 该走哪条路的精确步骤计划**。

判据核心：真·XML 屏 = `setContentView(R.layout.*)` 的 Activity；孤立 ComposeView / appwidget 等非屏 layout **不**使纯 Compose 误判为 hybrid。

按判定结果走 §2 对应那一支。**别跳过本步靠主观判断架构**——架构判定是确定性脚本的事。

---

## 2. 三条生成路（分发，本 skill 只编排不解析）

### 2A. pure_traditional —— 委托传统链（v2026-07-10b：ART(主线,可收口) ∥ registry(后台 sub-agent) 并行）
1. **toolkit-fact-indexer**（确定性 ~20s）：跑 harmony-migration-toolkit → 产结构树。
2. **fork（并行——但按"需不需要收口协调"分层，v2026-07-10b 修正）**：
   toolkit 产完结构树后，查 `<hmos_project>/spec/a2h/functional_registry.json`：
   - **registry 已存在**（上游拷贝过/上次产过）→ 无需并行，只跑腿A。
   - **registry 不存在** → **fork 前先拍快照**：`mkdir -p spec/a2h/_work && cp spec/toolkit-fact-tree.json spec/a2h/_work/tree_snapshot.json`，然后：
     - **腿A（ART）= 主会话直接跑，绝不包成 sub-agent**：主会话调 `$app-relationship-tree` 富化（补 purpose / inbound_triggers / navigation_contract / preconditions / reach_paths，**写树**）。ART 会分批派 batch sub-agent 分摊上下文——这些 batch 是**主会话的直接子 agent（2 层）**；主会话**必须等齐所有 batch 完成通知 → apply 各 batch 的 patch 回树（收口）**，缺哪个 batch 就补派哪个。
     - **腿B（registry）= 后台 sub-agent**：同一时间并行派 sub-agent 执行 `$a2h-functional-registry`（子 agent 提示词里必须带 `$` 显式调用，该 skill 未开隐式路由）（§3.5 ① 的 XML 分支提前到这里跑），读全源码 + census，**只读快照、只写 `spec/a2h/{functional_registry,test_intents}.json`，不碰树**。
       > ⚠️ **腿B 的内部收口不许它自己嵌套下放（2026-07-15 实测事故 + 修）**：registry **对外**产独立文件（相对树无需协调，故它当 sub-agent 安全）；但它**内部**若控件多会「分域并行抽取 → 合并成 functional_points」，**这一步合并是收口协调**。registry 作为 sub-agent 时**禁止**再派后台分域 agent 然后 return —— 实测它派了 7 个 census 分片抽取 agent 即停，合并从未发生、functional_registry 从未落盘，靠主会话唤醒才收口。**派腿B 时必须在 prompt 里注明**：「你被当 sub-agent 调起，分域抽取要么自己同步做、要么把分域清单回报主会话代派；**绝不异步外派后自行退出**」（registry SKLL §S3 已补同款铁律，此处编排层双保险）。若嫌 registry 内部串行慢，正解是把**腿B 的分域抽取 agent 提为主会话直接子 agent**（与腿A 的 batch 同池并行），主会话统一收口——并行不丢、收口在不会停的主会话。
   - **⚠️ 为什么这样分层（收口协调，别改回"两个都 sub-agent"）**：ART 改**同一棵树**，需要"等齐 N 个 batch → apply 回同一棵树"的**收口协调**，只有主会话能做（sub-agent 一停止就丢收口）；registry **对外**产独立文件无需与树协调，下放 sub-agent 安全（但其**内部**分域合并的收口同样不许它嵌套下放，见上）。**2026-07-10 实测教训**：曾把 ART 也包成 sub-agent → ART 嵌套派 6 batch（3 层）→ 2 个 API stall + 主 ART 无法跨调用收口 → 46 个 patch 散落没 apply、树未富化。**分批是好设计（保留），嵌套是祸根（消除）**。**判据统一**：任何"等齐 N 片再合并"的收口，都必须由**不会中途 stop 的那一层（主会话）**持有——不管被合并的是树还是 registry。
   - **并行性不丢**：主会话跑 ART（含 batch 收口）∥ 后台 registry，墙钟仍 ≈ max(T_ART, T_reg)；两条链均 ≤2 层。
   - **⚠️ 脏读铁律**：腿A 在**原地反复重写**活树；腿B 若需页面清单**只准读 fork 快照** `spec/a2h/_work/tree_snapshot.json`，**禁读活树**（直读=可能吃到半截 JSON）。
   - **⚠️ join 铁律**：**腿A 收口完成（所有 batch patch 已 apply 回树）且腿B sub-agent 返回后**才准进 §3.5 ② merge——merge 同时消费腿A 的树字段（落点映射）和腿B 的 registry（注入源），缺任一即废。一腿失败：保留成功腿产物、只重派失败部分（batch patch 与 registry 均幂等可重跑）。
     - **⚠️⚠️ "返回"的唯一合法信号 = sub-agent 的完成通知（task status=completed），绝不是产物文件的存在/条数**。registry 在跑的过程中会**反复中途落盘**，条数会变——**2026-07-10 实测教训**：曾在 registry 还在跑时看到 `functional_registry.json` 已有 255 条就判它"完成"、提前跑了 merge；registry 其实随后才补了 HomeActivity 4 个底部 Tab（255→259），merge **侥幸**在它写完 259 后 1 分钟才读、才没漏那 4 条核心导航 Tab。若时机差一点 = 漏功能点，或读到半截 JSON 直接崩。**判 join 只认完成通知，禁看文件。**
   - **静默失败兜底（机械）**：任何一腿悄悄没跑成，最终都过不了 `dispatch.py gate`——腿A 缺 → 产出契约闸 `NEED:app-relationship-tree`；腿B/merge 缺 → 功能维度闸 FAIL。编排可以是散文，验收是脚本。
   > ⚠️ **腿A 不可省**。只跑 toolkit 是「薄树」（navigation_contract=null），visual-verify 会退化猜——这正是 §3 产出契约闸要拦的。

### 2B. pure_compose —— 委托 compose-fact-tree
派 `compose-fact-analyzer` agent 跑 compose-fact-tree 的 Phase 0–7（Phase 7 的 `enrich_parity.py` 产出与传统树同构的富化字段）。

### 2C. hybrid —— XML 先、Compose 补充式叠加、缝合（本 skill 的核心编排）
toolkit 啃不动 Compose、compose-fact-tree 不建 XML；各跑各的再并集 = **两座孤岛**（跨架构接缝边没人缝 → visual-verify BFS 在边界断）。所以用**顺序补充**，不是独立两棵 merge：

1. **XML 半边先**：跑 2A（toolkit + app-relationship-tree）产基础树（XML 屏 + 组件 + XML→XML 边）。给每个 XML 节点打 `"arch":"xml"`。
2. **Compose 补充式叠加**（compose-fact-tree 的 **supplement 模式**——读已有树、追加、不覆盖）：
   - 派 compose-fact-analyzer agent，prompt 强调：**读上一步产出的树，把 Compose 屏作新节点/边追加，绝不清空已有 XML 节点**。每个新节点打 `"arch":"compose"`。
   - **边界去重**：Compose 屏宿主若是已在树里的 Activity（ComposeView 宿主 / setContent 被 toolkit 当空壳建过），**按 `fq_class` 合一**，别重复建。
   - **红利**：因 XML 节点已存在，Compose 屏里 `startActivity(XmlActivity)` 的 target **直接解析到树里已有 XML 节点**，Compose→XML 跨架构边连得上（独立 merge 时这条只能丢）。
   - 跑 `compose-fact-tree/scripts/enrich_parity.py --in-place` 富化新增的 Compose 节点。
3. **反向接缝 XML→Compose**（toolkit 跑时 Compose 节点还不存在，缝不了，这步补）：扫 XML Activity/Fragment 找 `startActivity(ComposeHostActivity)` / `ComposeView.setContent{ XScreen() }` / `navigate(R.id.composeFragment)`，补边进 flow_graph + 两端 inbound/outbound。**这步是本 skill 唯一新增的源码分析——只缝边不造节点**；准头不够用 `unresolved_hints`/`uncertain` 标，别凭空连。

参考（直接复用，别重写）：`compose-fact-tree/references/{nav-dialects,enrichment-parity-spec}.md`、`scripts/{enrich_parity,factcheck}.py`。

---

## 3. 统一校验（确定性，不可跳过）—— 三条路产出后都跑

```bash
python3 scripts/dispatch.py gate <spec/toolkit-fact-tree.json> <android_source_root>
```
driver 按确定性顺序跑闸、任一红 `exit≠0`、**不得交付**：

1. **产出契约闸 = 复用 visual-verify 自己的门控**（`arkts-visual-verify/scripts/check_prereq_freshness.py`，**三路都跑**）：这是 visual-verify Step 1.0 认的那把尺（v6.6 架构感知），验 navigation_contract≥80% / reach≥50% / uncertain≤30%，兼容 reach_path(s) 双名、对 compose/hybrid 合法跳过 purpose。**「富化跑了没」的确定性兜底**：2A 漏跑 ART、2B 漏 Phase 7、hybrid 任一半边没富化 → 不达标 → 它直接输出 `NEED:<对应生成器>`（pure_traditional→app-relationship-tree / pure_compose→compose-fact-tree / hybrid→android-fact-tree）告诉你该补跑谁。dispatch.py gate 自动带 `--source` 让它判架构。**不自造闸**——复用 visual-verify 认的门控最准。
2. **连通闸**（`connectivity_gate.py`，**仅 hybrid 跑**，driver 据 detect_arch 自动决定）：从 launcher BFS 走全图（含跨架构边）。**跨架构断裂**（launcher 只到达一侧）= 接缝边没缝上 → 回 §2C.2/2C.3 补边。纯路不跑（其"不可达"多是 am-start 合法可达 / 由各自 factcheck B1 管，跑了会误报）。
3.（hybrid）compose-fact-tree 的 15 闸 factcheck 仅核验 Compose 半边自身；其 B 闸对 XML 节点误报，**以上面两闸为准**。

> 这套设计就是「检测=脚本、闸=脚本、编排顺序可自然语言、但每个 load-bearing 产出被脚本闸兜底」——agent 跳了哪步/富化没跑全，最终都过不了 `dispatch.py gate`，不靠信任。

---

## 3.5 条件接续 a2h-functional-merge（功能维度注入，A2H 项目专用）

树生成完成后、交付前（**pure_traditional 链**:§2A.2 fork/join 后先 merge、最终 gate 全绿收口;**Compose/hybrid 链**:结构 gate PASS 后接续本节）,**主代理必须检测 A2H Stage1 产物是否存在**,存在则接续注入功能维度——否则 visual-verify 的功能点双 oracle(Phase 0.5 grounding + B.4.5)会因树里没有 `functional_checks[]` 而**静默跳过,功能测试不发生且不报错**(已发生的真实漏测:整条 A2H 集成靠人记得手动跑 merge,忘了就等于没接)。

**检测 + 接续(确定性条件)**：
```
契约路径(唯一,不再"任意位置"搜——避免 workspace 多份 registry 摸错弱版/过期版):
    <hmos_project>/spec/a2h/functional_registry.json
    <hmos_project>/spec/a2h/test_intents.json
  上游(A2H 管线/人工)产完 Stage1 后,须把这两份**拷到上述契约路径**;visual-verify 只从这里读。

★ 按架构分流（dispatch 已判 XML / Compose / 混合）——XML 与 Compose 的功能链路实现不同：

① 若 <hmos_project>/spec/a2h/functional_registry.json **不存在** → **自产契约**（无条件）:
   • **XML / 混合** → $a2h-functional-registry（读全源码 + census + LLM 提取，锚点 = 真 resource-id）:
        android_src = <ANDROID_SRC>；hmos_project = <hmos_project>（产物落 spec/a2h/）
        ▸ **pure_traditional 链**:这步通常已在 §2A.2 fork 腿B **并行提前完成**——进入本节时 registry
          已存在,直接走 ②。走到这里 registry 仍缺失 = fork 被跳过,按本节原序补产（串行兜底,不算错误）。
        ▸ **hybrid 链**:不并行（compose 半边投影需最终树,XML 半边为简化统一串行）,按本节原序跑。
   • **纯 Compose** → `python3 $SKILLS_ROOT/a2h-functional-registry/scripts/compose_registry_from_tree.py <tree> <hmos_project>/spec/a2h`
        Compose 无 XML 布局 / 无 resource-id（testTag 实测 0 用）；compose-fact-tree 已把交互组件抽进树的 `components`，
        本脚本直接投影成 registry，**锚点 = 文案(text) + code_anchor**，并产 `compose_host_map.json`（merge 精确映射用）。
   产出 spec/a2h/{functional_registry,test_intents}.json 后进 ②。
   ⚠️ "无条件产"：纯 UI 项目也跑一次；确无功能点则 registry 近空、merge 注 0，由机械闸"registry 空"分支放行。

② 若 registry 存在（含 ① 刚产）且 树里尚无 functional_checks(jq '[.pages[],.fragments[],.dialogs[]]|map(.functional_checks//[])|add|length' == 0)
→ **按架构注入**:
   • **XML / 混合** → $a2h-functional-merge，**显式传契约路径**：
        registry = <hmos_project>/spec/a2h/functional_registry.json；intents = …/test_intents.json；src_root = <ANDROID_SRC>
   • **纯 Compose** → `python3 $SKILLS_ROOT/a2h-functional-merge/scripts/compose_merge_into_facttree.py <tree> <hmos_project>/spec/a2h --write`
        走 `compose_host_map.json` **精确映射**（无 resource-id grep / 无模糊 join），注入的 check 带 `tap_by=text` + `tap_text` + `code_anchor` 供 B.4.5 按文案点。
   • **混合(hybrid)** → 两条都跑（XML skill 覆盖 XML 派生点 + compose 脚本覆盖 Compose 组件）；compose_merge 按 fp_id 去重，安全叠加。
→ merge 返回后 **必跑下方"机械闸"** 确认功能点真入树（不跑闸不许宣告就绪）。
```
> ⚠️ **只认契约路径,不搜"任意位置"**:本次发现 workspace 里存在多份 registry(弱版 XML-only vs 富版 kt+impl 链),"任意位置"检测 + 无消歧会系统性吃错文件。固定单一契约路径后,放哪份是上游的显式责任,放错可追责、可一眼看出。

**铁律**(与 toolkit-fact-indexer 强制接续 app-relationship-tree 同模式)：
- **registry 无 → 自动产(无条件,用户拍板)**:缺 registry 时本 skill 按架构自产(①),不再把"无 registry"默认当纯 UI 跳过。merge 接续仍以"registry 存在"为条件(① 产完后恒成立)。
- **架构分流(XML vs Compose 实现不同,见 ①②)**:XML/混合走 `a2h-functional-registry` + `a2h-functional-merge`(skill,resource-id 锚点);纯 Compose 走 `compose_registry_from_tree.py` + `compose_merge_into_facttree.py`(脚本,文案锚点,因 compose-fact-tree 已抽组件、join 天然完成)。**都不拉起 A2H 黑盒二进制**。
- 提取/注入逻辑分别留在各自 skill/脚本,本 skill 只负责**按架构、按序在正确时机调它们**(XML 用 `Skill` 工具不 subprocess;Compose 直接 `python3` 调脚本,因它纯确定性投影、无 LLM 编排)。

**机械闸:功能点已入树——已内置进 `dispatch.py gate` 第三道闸（`functional_dimension_gate`，2026-07-10 从本节散文 jq 焊进代码，不再靠 agent 自觉手跑）**。语义（REG=registry entries 数，N=树内 functional_checks 总数）：
- `REG > 0 且 N == 0` → ❌ **gate FAIL**:registry 有 REG 条但树里 0 个 functional_check = merge 没注进去(契约路径错 / join 全 miss / 传参漏)。回查 merge 调用后重跑 gate。
- **registry 文件不存在 且 N == 0** → ❌ **gate FAIL**:§3.5 ① 没走(自产/拷贝都没发生)。先走 ① 再 ② 再重跑 gate。
- `REG > 0 且 N > 0` → ✅ 通过,gate 输出 `N/REG`(N≪REG 也算过,但提示映射命中率偏低可复查)。
- `REG == 0 且 N == 0` → ✅ 通过+警告:registry 近空(应用确无功能点 或 a2h-functional-registry 提取失败),纯 UI 合法放行,提示复查自产产物。
- merge 之后重跑 `dispatch.py gate`:结构闸确认 merge **只增** `functional_checks` 没破坏结构,功能维度闸此时应转绿——**gate 全绿才算树就绪**。

**禁止**:绕过 gate 直接宣告"树就绪"。功能维度闸红时不检测 registry、不自产、不 merge 就交付——现在会被 gate exit 1 机械拦下(以前是散文约束,真实漏接过)。

---

## 4. 交付物
- `<output_dir>/spec/toolkit-fact-tree.json`（统一树，三路字段同构；hybrid 含 `arch` 标 + 已缝跨架构边）
- A2H 项目额外:经 §3.5 接续 a2h-functional-merge 后,树带 `functional_checks[]`(功能维度,供 visual-verify 双 oracle)
- 终端：`架构=X | output_contract PASS | (hybrid) connectivity PASS | (A2H) functional_checks=N injected / (纯UI) no A2H artifacts, skipped`
- 字段与传统/纯 Compose 树同构 → arkts-visual-verify / a2h-spec **零改消费**。

## 5. 设计原则（别违背）
- **编排不生成**：解析源码成节点永远归三个生成器；本 skill 只调度 + 缝边 + 校验。hybrid 的缝合只缝边不造节点。
- **顺序不可换（hybrid）**：XML 必须先于 Compose——正因 XML 节点先存在，Compose→XML 边才解析得出。反过来退化成孤岛。
- **可并行的只有"文件集零交集"的两腿（pure_traditional 的 ART∥registry，§2A.2）**：并行的前提是腿B 不写树不读活树（读只准读 fork 快照）。任何新增并行前先做写盘/读盘交集分析；join 必须等两腿全部完成，merge 永远是 join 之后的第一步。
- **"需收口协调"的活留主线，"产独立文件"的活下放 sub-agent（v2026-07-10b；v2026-07-15 收紧）**：ART 改同一棵树、要"等齐 batch→apply 回同一棵树"，这种收口只有主会话能做（sub-agent 停止即丢），故 ART 走主线（它派的 batch 是主会话直接子 agent，可收口）；registry **对外**产独立文件、相对树无需协调，可下放后台 sub-agent。**判据是"有没有'等齐 N 片再合并'的收口步"，不是"重不重"、也不只是"改不改同一棵树"** —— 任何合并收口都必须落在**不会中途 stop 的那一层**。⚠️ **易漏点（实测事故）**：registry 对外虽产独立文件，但它**内部**"分域抽取→合并 functional_points"也是一次收口；把 registry 当 sub-agent 后，这层内部收口就落到了会 stop 的 sub-agent 手里 → 7 个抽取 agent 派完即停、合并从未发生。**所以"下放"只对'不含内部收口'的活成立**；含内部合并的（registry），要么让它内部同步不外派，要么把它的分域 agent 提为主会话直接子 agent。别把任何需收口的活（不管收口对象是树还是独立文件）包进会 stop 的 sub-agent。
- **能脚本化的全脚本化**：检测（detect_arch）、调度（dispatch plan）、校验（dispatch gate + 三闸）都是确定性脚本；只有生成与跨架构缝合（需源码语义理解）才用 LLM。
- **连通性 / 富化 > 节点数**：一棵节点齐但两座孤岛、或缺富化的薄树，对 visual-verify 不如一棵全连通、已富化的树。闸是终极验收。

## 6. 脚本清单
- `scripts/dispatch.py` — 确定性 driver：`plan <src>`（判架构+计划）/ `gate <tree> [<src>]`（跑全部闸，任一红 exit 1；连通闸仅 hybrid）。
- `scripts/detect_arch.py` — 确定性三态架构判定 + launcher 宿主。
- `scripts/connectivity_gate.py` — hybrid 专项跨架构连通闸（防孤岛；check_prereq 不做这事，故新增）。
- **复用现成审核闸**：`arkts-visual-verify/scripts/check_prereq_freshness.py`（v6.6 架构感知，产出契约闸，dispatch.py 直接调）——**不自造**。
- 复用生成器：`compose-fact-tree/scripts/{enrich_parity,factcheck}.py`、`toolkit-fact-indexer`、`app-relationship-tree`。
