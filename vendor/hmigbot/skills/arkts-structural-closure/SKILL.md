---
name: arkts-structural-closure
description: ArkTS 工程结构性验证 skill — 检测 skeleton 占位 / orphan VM / wiring 4 类闭包 / dangling FWD-REF / 沉浸式安全区四件套 + icon-sizing 图标尺寸自愈（pipeline 模式委托 arkts-icon-sizing）；支持一次性 sanity 与迭代收敛 loop 两种调用形态。被 a2h-execute §3c (stage 末尾 sanity) / §5e (Slice loop) / §6 (Pipeline-end loop) 三处调用。即使用户只说"做结构性验证"、"跑 wiring 检查"、"扫骨架"，也应触发此 skill。
metadata:
  type: domain
  domain: migration
  tags:
  - verification
  - structural-audit
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

# arkts-structural-closure

## 关键约束（Critical）

- **loop 调用前 MUST 读完本 SKILL.md §3** —— 5 类 verdict 处置 + 收敛常量 + repair worker 派发规则缺一不可
- **检测分层**：Stage 1/2 末尾 = **一次性 audit_skeletons sanity**（§2.1，非 loop）；Slice = **structural_loop slice 模式**（§2.2）；Pipeline-end = **structural_loop pipeline 模式**（§2.3）
- **3 套 verdict 处置完全一致**（slice / pipeline 共用 §3.3 表格），调用方差异仅在 mode 参数 + 作用域
- **不引入 `--mode=repair`**：repair worker 复用原 worker 完整上下文，仅追加 `dispatch_prompt` 字段作 findings 提示

---

## 1. 定位

ArkTS 迁移工程的结构性验证统一 skill：

- **检测维度**：skeleton 10 子类（L1-L4）/ wiring 4 类闭包（C1-C4）/ 跨 Slice orphan VM + 组件孤儿（E1）/ immersive 四件套 / icon-sizing 图标尺寸自愈（pipeline）/ 债务终结闸（registry 残留 + deferred_items 对账，pipeline）/ **装配闸（assembly，pipeline）——fail-closed 骨架未装配检测**
- **执行形态**：一次性 sanity（Stage 末尾）+ 迭代收敛 loop（Slice / Pipeline-end）
- **解耦原则**：与 `a2h-execute` 编排逻辑解耦，可被任何 a2h pipeline 阶段或独立场景调用

```
a2h-execute 编排
    │
    ├─ Stage 1/2 末尾 (§3c) ──→  arkts-structural-closure §2.1 一次性 sanity
    ├─ Stage 3 每 Slice (§5e)   ──→  arkts-structural-closure §2.2 slice 模式 loop
    └─ Stage 3 完成后 (§6)      ──→  arkts-structural-closure §2.3 pipeline 模式 loop
```

---

## 2. 三种调用入口

### 2.1 Stage 末尾 sanity（一次性 audit，**非 loop**）

适用 Stage 1 / Stage 2 末尾——99% iter 0 PASS，loop 5 类 verdict 在此无对应失败模式。

```bash
python3 scripts/audit_skeletons.py --project-root . --scope stage \
    --diff-base <STAGE_START_SHA> \
    --handoffs <Stage 产出 brief 路径> \
    --output-json spec/execution/autofix-log/round-<R>/audit-stage-<N>.json
```

| exit | 处置 |
|---|---|
| 0 | FAIL=0 → 进入下一 Stage |
| 1 | 有 FAIL findings → LLM Read JSON 的 `findings[]` → 派本 Stage primary worker 修一次 → 重跑本命令验证；连续 2 次仍 FAIL → 标 BLOCKED |

Stage 3 末尾自动启用 L4.dangling-fwd-ref 检测（`kind=forward-ref` 占位 `status=resolved` 但代码 marker 残留 → FAIL）。

> **registry 解析护栏（各 scope 通用）**：registry 文件存在且含 P-ID 数据行、但解析器加载 0 行 → 自动跳过 dangling 扫描，只发 1 条 `registry-parse-degraded` FAIL（工具链问题，**勿派 worker 改业务代码**，修表格式或 `skeleton_lib/registry_resolver.py` 后重跑）。解析按表头列名映射，兼容 status 列位漂移与 `**resolved**（批注）` 式单元格。

### 2.2 Slice 模式 loop（per-Slice 接线验证）

适用 Stage 3 每个 Slice Step 3e。**作用域 = 本 Slice modifies_files + cross_slice_edits**。

```bash
bash scripts/run_loop.sh --mode slice --target <N> --round <R> --project-root .
```

Loop 内部跑：
- `verify_slice_wiring.py --slice <N>` — C1 orphan / C2 integration_point / C3 cross_slice / C4 parent_replacement
- `audit_skeletons.py --scope=slice` — skeleton + dangling-fwd-ref（限本 Slice 文件）

CONVERGED 后由调用方追加非 loop 校验（placeholders / source-notes / deferred_items —— 见 a2h-execute §5e）。

### 2.2b Group 模式 loop（per parallel-group 接线验证）

适用 Stage 3 **以 parallel_group 为粒度**收尾时（a2h-execute §5e：group-closer 编译 PASS 后**自跑并 fix-forward** ≤3 轮直到 CONVERGED，非收敛才冒泡主线程）。**作用域 = 组内全部 slice 的 modifies_files + cross_slice_edits 并集**。

```bash
bash scripts/run_loop.sh --mode group --target <groupId> --slices <N,M,...> --round <R> --project-root .
```

Loop 内部跑（复用 slice 模式 primitive，只是一次覆盖整组）：
- `verify_slice_wiring.py --slice <每个组内切片>` — 逐切片 C1-C4，合并 categories + repair_actions
- `audit_skeletons.py --scope=slice --scope-files <组并集>` — 对整组文件**一次** skeleton + dangling-fwd-ref

verdict / dispatch_prompt / state 与 slice 模式同构（合并后的 wiring 喂同一套下游）。CONVERGED 后同样追加非 loop 校验（对组内每个 slice 逐一核 placeholders / source-notes / deferred_items）。**收益**：组内多切片共写的文件（如 HomePage 各 Tab 槽位）在终态一次性验，比 per-slice 看半成品更准，且编译只跑一次（在 group-closer 内）。

### 2.3 Pipeline 模式 loop（整工程兜底）

适用 Stage 3 全部 Slice 完成后**一次性**整工程兜底。**作用域 = 整工程 .ets**。

```bash
bash scripts/run_loop.sh --mode pipeline --target final --round <R> --project-root .
```

Loop 内部跑：
- `audit_skeletons.py --scope=all` — 全工程 skeleton + dangling-fwd-ref + intentional-default 反查
- 跨 Slice **orphan VM 检测**（候选 = `viewmodels/` / `store/` / `repository/` / `service/` / **`network/`** 下所有导出类；network/ 是基础设施层，只认 NO_IMPORTER / IMPORTED_BUT_NOT_INSTANTIATED 两类真死信号，ONLY_INSTANTIATED_BY_NON_UI 带证据豁免——拦截器由 HttpClient 等非 UI 装配是正常架构）+ **组件孤儿检测（E1）**（候选 = `components/` / `views/` / `widgets/` / `dialogs/` 下嵌入式组件：无任何 .ets `import` 的 `NO_IMPORTER` 阻断级 FAIL，`import` 了却从未渲染的 `IMPORTED_BUT_NOT_RENDERED` 浮为 WARN 复核）。**盲区豁免（fail-tight）**：orphan 检测基于实例化（`new X` / `X.getInstance()`），会误报"被用但非 new"的类——经 `extends`/`implements`（抽象基类/接口）、静态访问 `X.method()`（静态门面 / 常量路径 holder）、文件内自用（私有 helper）使用的类，由 `ref_graph_lib.usage_evidence()` 带**证据**移入 `exempted` 段、不进 fingerprint/不驱动循环；**零使用证据的类仍保留为 FAIL**（真孤儿 / 未接线绝不豁免）。`.agents/**` skill 模板 .ets 不属项目代码，已从扫描 skip。
- 沉浸式/安全区四件套（范式差异类）— structural_loop 内置 Python 单遍扫描（判定逻辑与 `check-fullscreen-immersive-safearea.sh` 一致，`.sh` 留 CI/手工；Python 版免每文件 grep 进程 spawn，Windows 上单轮 ~10s → <0.1s）
- **icon-sizing 自愈**（委托兄弟 skill `arkts-icon-sizing/scripts/icon_autofix.py`）— static under-constrained `Image` 自动补尺寸：审计→测量(px÷density)→修复 --apply→复审，一次收敛、**无人工介入、非阻断**（动态源 / 无 raster 仅记录）。**可选 `--android-res <res 根>` 提升密度精度，缺省回退 `--density 3`**
- **`verify_closure_ledger.py` — 债务终结闸**（registry 残留分类 + deferred_items 对账）：每条未解决 forward-ref，若 `resolve_by` 指向**终态切片**（PASS/ESCALATED/ROLLED_BACK）但仍 registered → GAP（FAIL）；`resolve_by=集成期…`/非 Slice → 合法外部延迟（D-007/D-008/R-005，PASS）。各 brief 的 open `deferred_items` 若依赖一个无 `.ets` 的工件（如某 ViewModel 从未创建）→ FAIL，否则 WARN 浮出复核。判定语义见 `skeleton_lib/deferral_policy.py`。**堵的洞**：旧 dangling-fwd-ref 仅对 PASS 切片报错，ESCALATED 切片的未解决 marker 被赦免 → FV-1 假 PASS（RCA 背景见 a2h-plan `templates/placeholder-registry-template.md` 的 dangling-fwd-ref 语义）。
- **`assembly_gate.py` — 装配闸**（fail-closed 骨架未装配 + 空对象占位；v2 经 2026-08-24 对抗审核加固）：
  ① `fail-closed-unassembled`：guarded 类（ready 标志 + 未就绪即 throw 守卫 + 置位装配方法）经全部别名（类名静态访问 / 定义文件内 new 赋给的导出 const）定义文件外零引用 → FAIL；
  ② `guard-consumed-assembly-never`：守卫方法有外部调用而装配方法零调用（有人在消费必抛方法）→ FAIL；
  ③ `capability-stubbed-no-real-impl` / `real-impl-never-installed`：空对象占位（命名前缀闭集 ∪ 行为特征"全方法平凡且含 throw/假值"）的接口无真实现，或真实现只有死接线（裸 new / 赋值后零引用）→ FAIL；placeholder-registry 有结构化 P-ID 行（status=registered/pending/due/deferred）的降级 WARN——散文/否定句提及不算。
  所有 usage 判定在 strip 注释与字符串后的文本上跑（注释里的 `new X` 不算装配）。
  **堵的洞**（三次实录）：AIPPT 0821 installApiClient / aippt_codex_v2 0823 NetworkRuntimeState.hydrate 零调用点 / AIPPT_830 DeviceIdentityService 登录路径消费必抛方法——编译、注释 marker 占位扫描、页面审计、账本四道门全部放行；失效本质 = **把「策略约束」（显式失败/fail-closed/缺配置降级）误当成「免除装配义务」**。修法永远是组装根补真实调用点 + 接行为验证，绝不是删守卫消音或加死 new。
  已知残余（P1）：对象字面量/鸭子类型实现不在 Tier-3 候选；"有效装配"未接 ref_graph 组装根可达性。穿刺自测集 `tests/test_assembly_gate.py`（13 用例=对抗审核全部绕过/误拦手法，红线：绕过必 FAIL、误拦必 0）。
  **新制（能力交付契约，2026-08-24 起）**：base-plan 含「组装根」任务的工程，assembly
  detector 槽位自动换装 `capability_ledger_gate.py`（分流锚 plan 产物——worker 只读，
  删代码文件不降级）。闭集收货五检：表形态（直接字面量/禁 as）/ 键集差集（缺席须
  P-ID+D 祝福键名）/ 槽位定义闭包 stub-lint / 规范实例（组装根外 new 槽位类=0）/
  生命周期装配（EntryAbility 调 installCapabilities）。键集由
  `gen_capability_manifest.py` 每轮从 plan 产物重新生成（防篡改）。设计全文与三轮
  对抗审核记录见会话侧 capability-ledger-design.md；自测集
  `tests/test_capability_ledger.py`（10 用例含三审四 P0 专项）。旧 assembly_gate
  保留为存量工程兜底。
- **`binding_gate.py` — 显隐绑定收货闸**（pipeline）：① dead-render-flag——条件渲染开关（@Local/@State boolean + if 渲染）零赋值 → 默认 false=FAIL（内容永久蒸发）/ true=WARN（阀门失灵）；② binding-dropped——`spec/baseline/ui/visibility-bindings.json`（a2h-spec 期 extract_visibility_bindings.py 从安卓源抽的真值账）逐条核销，runtime-toggle 的**数据驱动名**（只认数据字段，视图 id 形态不作判据——CC 基线 37 误报教训）零对应 → FAIL。实录：「我的」页四按钮消失 = showServiceCenter 绑定断裂 × fail-closed 默认（CC 同病异症，默认 true 侥幸）。清单缺席（存量工程）只跑①。测试 `tests/test_binding_gate.py`。

> ⚠️ **icon-sizing 是唯一会改源码的 detector**（自愈），其余 detector 只读。它确定性、幂等（重复跑无副作用）、git 可整体回滚；正常永远 `passed=true` 不进 verdict，仅脚本执行异常才计入（safety net）。缺 `arkts-icon-sizing` 时优雅跳过。

#### ⚠️ 降级执行：必须逐项跑齐（2026-07 事故教训）

`run_loop.sh` 若因环境问题跑不起来，**不允许"挑一两个 detector 补跑就宣告完成"**。
pipeline 的 5 项里 **icon-sizing 会改源码**，漏跑 = 图标尺寸缺陷（ArkUI 下无尺寸 `Image` 撑满父容器）静默流入产物，而编译 / 结构审计 / 债务闸 / 终态编译**四道静态门全部查不出来**——只有真机渲染才暴露。

各 detector 的独立入口（降级时照表逐项跑，一项不能少）：

| detector | 独立入口 | 产物 |
|---|---|---|
| skeleton | `audit_skeletons.py --project-root . --scope all --output-json <p>` | `audit-pipeline-iterN.json` |
| orphan VM | 内置（`structural_loop._run_pipeline_orphans`），无独立 CLI | `orphans-pipeline-iterN.json` |
| 沉浸式四件套 | 内置 Python；等价 shell 版 `check-fullscreen-immersive-safearea.sh` | `immersive-pipeline-iterN.json` |
| **icon-sizing 自愈** | `../arkts-icon-sizing/scripts/icon_autofix.py --project-root . --apply --android-res <res根...> --output-json <p>` | `icon-pipeline-iterN.json` |
| 债务终结闸 | `verify_closure_ledger.py --project-root . --output-json <p>` | `ledger-pipeline-iterN.json` |
| 装配闸 | `assembly_gate.py --project-root . --output-json <p>` | `assembly-pipeline-iterN.json` |

> **机械兜底**：`finalize` 会核对 `history[-1].detectors_run` 是否覆盖本 mode 的必需集（`_REQUIRED_DETECTORS`）。缺项直接判 `final_state: INCOMPLETE` 并列出 `missing`，**不会给 PASS**。所以降级跑完后仍须让 state 反映真实执行情况，不要手写一份"看起来通过"的 loops JSON。
>
> **另注**：单个 detector 崩溃现在由 `_safe_detector` 隔离（记 `passed:false` + 计入 FAIL），**不再中断同一轮的其余 detector** —— 上述事故中 `_run_audit` 抛异常直接带走了后面 4 项。

---

## 3. structural_loop 协议（slice + group + pipeline 共用）

<HARD-GATE>
调 `run_loop.sh` 后，按 exit code 处置。FAIL 不直接 BLOCK——按 verdict 升级。
</HARD-GATE>

### 3.1 收敛常量

常量见 `scripts/loop_runner.py`：

```
MAX_ITER             = 8     # 单 loop 最大迭代数（默认上限）
STALLED_THRESHOLD    = 2     # 连续 N 轮 findings fingerprint 相同 → 停滞
REGRESSION_THRESHOLD = 1.5×  # findings 数 > 前轮 × 此倍率 → 退化
```

> **风险域条件化迭代上限（item6）**：`MAX_ITER=8` 是默认上限，可经 `run_loop.sh … --max-iter <N>`（透传至 `structural_loop.py iterate`）按目标风险域下调——低风险 / 纯 UI 切片传 `--max-iter 2` 封顶 iter2 省迭代；**支付 / 会员 / 双签名 / 成环(pay↔basic) 等高危域保留默认 8**。封顶后若仍有未决 finding，照常 STALL→ESCALATED 浮出复核，**不静默放行**（迭代上限只省"空转轮次"，不降"问题暴露度"）。

### 3.2 调用契约

每次 `bash scripts/run_loop.sh --mode <slice|pipeline> --target <N|final> --round <R> --project-root .` 执行 **1 轮迭代**：
- state 文件自动累积 history：`spec/execution/autofix-log/round-<R>/loop-state-<mode>-<target>.json`
- latest result JSON：`spec/execution/autofix-log/round-<R>/loop-result-latest-<mode>-<target>.json`
- 各 detector 详细 JSON 由 structural_loop 内部产出：`audit-<target>-iter<N>.json` / `wiring-<target>-iter<N>.json` 等
- CONVERGED 后 finalize 收尾产物：`spec/execution/autofix-log/round-<R>/loops-<mode>-<target>.json`（stage/slice）/ `loops-final-structural-closure.json`（pipeline 收尾，即 Final Structural Closure）（含 `final_state`）—— 下游 a2h-execute §6 / a2h-plan FV-1 的 gate 对象

> **产物路径铁律**：全部 loop / audit / wiring JSON **只落 `spec/execution/autofix-log/round-<R>/`**。Windows 无 bash 时可手动驱动 `python structural_loop.py init/iterate/finalize`（等价 run_loop.sh 时序），但 `--state-file` / `--output-json` 必须仍指向上述目录——**`docs/autofix-log` 是已废弃落点，三脚本对其硬拒**（exit 2）。

调用方按 exit code 决定下一步：

### 3.3 verdict 处置表

| exit | verdict | 触发条件 | 调用方动作 |
|---|---|---|---|
| 0 | `CONVERGED` | findings 全 clean | 调 `python3 scripts/structural_loop.py finalize --state-file ... --output-json ...` 产 `loops.structural` JSON → 嵌入 brief `final_state: PASS` |
| 1 | `CONTINUE` | findings 仍存在 | Read 最新 result JSON 的 `dispatch_prompt` → 派 repair worker（按 fixer_layer 分轨：feat→`a2h-migration-worker` / ui→`a2h-activity-converter`）**原 prompt 末尾整段追加 dispatch_prompt** → 回 `run_loop.sh` |
| 2 | `STALLED` | 连续 2 轮 fingerprint 相同 | 调 finalize → brief `final_state: ESCALATED` + pipeline 继续 |
| 2 | `REGRESSED` | findings 数 > 前轮 × 1.5 | 调 finalize → `git stash` 本单元改动 + brief `final_state: ROLLED_BACK` + 阻断下游 `depends_on` |
| 2 | `EXHAUSTED` | 满 8 轮未 CONVERGED | 同 STALLED |

### 3.4 Stage 末尾闸

ESCALATED Slice 累计 > 10% → 阻断进下一 Stage / a2h-verify。该判定由 a2h-execute 主流程做，本 skill 不持有累计统计。

### 3.5 Repair worker 派发原则

- **复用原 worker 完整上下文**（spec + Android 源 + plan），**不引入 `--mode=repair`**
- 仅在原 prompt 末尾追加 `dispatch_prompt` 字段作 findings 提示
- 指令统一："按 suggested_action 修复，不做无关变更"
- 路由按 fixer_layer 分轨：feat 类（services / viewmodels / repository / store / utils）→ `a2h-migration-worker`；ui 类（pages / components / widgets / resources）→ `a2h-activity-converter`
- pipeline 模式按 finding/orphan 的 `file` 路径推断所属层

---

## 4. 实现脚本对照

| 文件 | 职责 |
|---|---|
| `scripts/run_loop.sh` | loop 入口；包装 structural_loop iterate 一轮，stderr 输出 verdict + 路径；自动派生 state/result 路径 |
| `scripts/structural_loop.py` | 单轮 iterate（detector 调度 + verdict 计算 + dispatch_prompt 生成）；finalize 子命令收尾 |
| `scripts/loop_runner.py` | 收敛 verdict 计算核心（5 类 verdict + 常量定义） |
| `scripts/audit_skeletons.py` | 被 structural_loop 内部调用（slice/all scope）；亦被 §2.1 直接一次性调用（stage scope） |
| `scripts/verify_slice_wiring.py` | 被 structural_loop slice 模式（单切片）/ group 模式（逐切片后合并）内部调用 |
| `scripts/assembly_gate.py` | 存量工程兜底：structural_loop pipeline 模式调用（plan 无组装根任务时）；fail-closed 骨架未装配检测 |
| `scripts/capability_ledger_gate.py` | 新制主闸：plan 含组装根任务时换装；闭集收货五检 |
| `scripts/gen_capability_manifest.py` | 能力键集清单生成（base-plan+slices 3c+contracts seam 三源，闸每轮重生成） |
| `scripts/check-fullscreen-immersive-safearea.sh` | 沉浸式判定逻辑权威源（CI/手工用）；pipeline 模式内由 structural_loop 的 Python 等价实现执行 |
| `scripts/fswalk.py` | 剪枝式文件遍历（audit / ref_graph / ledger 共用，跳过 oh_modules 等不再全树枚举） |
| `scripts/tests/` | Track-1 单测（registry 解析双列序/批注归一 + degraded 护栏 CLI 集成） |
| `scripts/verify_closure_ledger.py` | 债务终结闸 — 被 structural_loop **pipeline 模式**经 `_run_pipeline_ledger()` 调用（registry 残留分类 + deferred_items 对账）；亦可独立跑做回归 |
| `../arkts-icon-sizing/scripts/icon_autofix.py` | **跨 skill** — pipeline 模式经 `_run_icon_sizing()` 调用，图标尺寸自愈（唯一会 mutate 源码的 detector；缺失则跳过） |
| `scripts/skeleton_lib/` | taxonomy + patterns + classifier + registry_resolver + **deferral_policy**（外部延迟 vs 在管线内债务判定，P2/P3 共用） |
| `scripts/ref_graph_lib/` | 全工程 import + instantiation 引用图（orphan 检测）|
| `scripts/plan_lib/` | feature-plan 解析器（indexed 布局：索引 detail 指针 → plans/slices/ 文件；旧 monolith 报错提示重跑 a2h-plan） |
| `scripts/README.md` | CLI 与 sub-package 详细对照 |

---

## 5. 输出 JSON schema 速查

> **MUST**：各阶段（slice / pipeline / loop verdict）输出 JSON schema 速查见 `references/output-schema.md`。

---

## 6. 调用方对照（a2h-execute）

| 调用点 | a2h-execute 章节 | 本 skill 入口 |
|---|---|---|
| Stage 1 末尾骨架 sanity | §3c | §2.1（一次性 audit） |
| Stage 2 末尾骨架 sanity | §4d 编译验证后 → §3c | §2.1（一次性 audit） |
| Stage 3 每 parallel-group 接线验证（group-closer 收尾） | §5e group 收尾 | §2.2b（group 模式 loop） |
| Stage 3 size-1 组接线验证（串行降级 / 重试单 slice / 只执行 Slice N） | §5e Step 3e | §2.2b（group 模式，slices 单元素；复用 §2.2 slice primitive） |
| Stage 3 末尾整工程兜底 | §6 Final Structural Closure | §2.3（pipeline 模式 loop） |

a2h-plan 同步在 `feature-plan-template.md` 的 Step 3e 与 FV-1 task 中以 `suggested_skills: [..., arkts-structural-closure]` 显式声明。

> **icon-sizing 自愈随 §2.3 自动运行**：a2h-execute §6 已调本 skill `mode=pipeline`，故图标尺寸自愈无需额外接线即生效。**可选**：调用时给 args 追加 `android_res=<android>/app/src/main/res`（多模块传多个，空格分隔），透传给 `run_loop.sh --android-res` → `icon_autofix.py`，按 Android 源逐图取精确密度；不传则回退 `--density 3`（xxhdpi），多数单桶工程已足够。

---

> **Remember**：调本 skill 前必读 §3 协议；slice / group / pipeline 三种 loop 共享 verdict 处置表；一次性 sanity 仅用于 Stage 1/2 末尾这种"99% PASS"场景，不走 loop。
