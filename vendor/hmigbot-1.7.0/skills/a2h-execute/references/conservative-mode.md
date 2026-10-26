> **已废弃**（单一形态收敛，见 IMPL-PLAN §7 / DESIGN §7），归档保留勿用。

# 保守档执行剧本（profile = conservative）

> 定位：Workflow 原语不可用（或旗舰模型不当班）时的完整执行路径（设计册 3 §3.7 / 1 册 §1.3）。
> 覆盖范围：**从阶段 A 就开始**——wave-understand 已依赖 Workflow，保守路径不能只管 execute。
> 路径约定同 SKILL.md §0：`$EXE` = 本 skill 目录，`$SKILLS` = skills 根目录，工程根为当前目录。

<!-- GAP: 保守档"派发计划 JSON"（generate_waves.py --profile conservative 的输出物）的 schema 未列入 schemas 7 件清单（IMPL-CONTRACT §7 schemas 所有权），字段形态需与 script-S1 / schemas 实现者对齐；本文 §3 给出消费侧假定形态。 -->
<!-- GAP(已解决): 批门名 compile#<wave>.b<n> 已被 gate_check.py（编译门族 compile#\S+）与
     state_update.py（compile_rounds 落账）接受；核账门用 escalated-ratio（别名 final）。 -->
<!-- GAP(已解决): deferred 项汇入 contracts.json#deferred 已由 contract_sync.py --merge-deferred 承载（§5 清单第 4 步已更新）。 -->

## 1. 进入条件与总原则

- **进入条件**：A0 Workflow 原语探测三分支之③——用户确认降档，脚本改写 `workflow-params.json#profile = "conservative"` 并记 audit 字段；审批门材料已带档位确认项。**任何路径都不得静默降级**：执行期发现环境与 profile 不符，一律停下呈报，回三分支重确认。
- **两档共用面（零差异清单）**：blueprint 六件、`spec/CONTRACT.md`、片段库与 `assemble_prompt.py` 组装器、agent-output schema（2 册 §2.7）、`state.json` 结构、三大恢复不变式（ID 永不复用 / 散文式 defer=FAIL / ownership 互斥）。保守档不是旧架构原样——契约、片段、脚本预检、状态 JSON 化的收益全部保留，**只有粒度与编排原语退化**。
- **数据面唯一差异**：保守档没有 StructuredOutput 工具（那是 Workflow harness 机制）。所有子代理输出契约改为**最终消息尾部围栏 JSON**（§4），由 `parse_agent_output.py` 解析回收；state 写入从"wave 边界结构触发"退化为"主循环每批边界的清单化纪律"（§5，损失明示见 §7）。

## 2. 阶段 A 保守路径（wave-understand → 分批串行读代理）

A0（环境体检/事实索引/域切分草案）、A1 主循环同期步骤（工程脚手架、Navigation 外壳、资源转换、i18n、种子 infra、CONTRACT.md）、A2 覆盖率审计、A3 契约生成与审批门——**全部与旗舰档相同**（本就是主循环脚本步骤，与编排原语无关）。唯一退化点是 A1 的 wave-understand：

1. **生成派发计划**（不产 .js，产计划 JSON）：
   ```bash
   python3 $EXE/scripts/generate_waves.py --blueprint spec/blueprint --out spec/waves --wave understand --profile conservative --json
   ```
   计划按 domain-map `domains[]` 排批：每批 = 一个域读代理（大域按 `split` 拆为多任务）；批间**串行**。
2. **逐批派发读代理**（普通 子代理派发）：prompt 用组装器产物（7 维度穷尽式模板 + 三源数据指针，与旗舰档同一份，见 `spec/waves/prompts/understand/<task>.txt`），仅第⑥输出段为围栏 JSON 约定（§4）。
3. 读代理职责不变：落盘 `spec/domains/<key>.md`（穷尽式 spec，单份 ≤60KB，大域多份分片）；最终消息围栏 JSON 走 `summary` schema（7 维度摘要 + `ac_candidates[]`，供 A3 生成 acceptance）。
4. 每批边界执行 §5 清单（parse → 落账 → 核账），全部域完成后进 A2。

三源数据缺失的兜底同 `recovery-playbook.md` R5（synthesize 两脚本 → 低置信骨架 + deferred）。

## 3. 阶段 B：批量 子代理派发流程

### 3.1 派发计划 JSON（生成器输出物）

`generate_waves.py --profile conservative` 对每个 wave 输出 `spec/waves/plan-<wave>.json`（假定形态，见文件头 GAP）：波次 → 批次序列 → 每批的 Agent 调用清单（task key、prompt 文件路径、ownership 白名单、schema 名、模型档）。主循环**按计划照单执行**，不自行编排。

### 3.2 粒度回退与批次纪律

- **B2 域波粒度回退**：domain-map 的域按 `pages` 拆为 **≤5 页/批** 的批次；同一域的批次连续执行（spec/契约段只组装一次，批间复用同一 prompt 骨架，仅 YOUR PAGES 清单变化）。
- **批间串行，批内可并行**：同批任务的 ownership 互斥（生成器保证），批内允许一次并行派发多个子代理；**无 pipeline 重叠、无同秒 fan-out**——上一批编译门绿之前不开下一批。
- **每批一道编译门**（沿用旧节奏，换来更小爆炸半径）：
  ```bash
  <build_cmd> > spec/reports/build-<wave>-b<n>.log 2>&1
  python3 $EXE/scripts/gate_check.py --state spec/state/state.json --gate compile#<wave>.b<n> --build-log spec/reports/build-<wave>-b<n>.log --blueprint spec/blueprint --json
  ```
  verdict 处理同旗舰档：`quick_fix` 主循环亲手修（阈值 `gates.quick_fix_threshold`、亲手上限 ≤10 条/边界）；超阈值派 hmos-builder；同批三轮不收敛 → R3 局部分支（回滚粒度到批内页面所属 glob）。
- **B1 infra 波**：任务本就按模块互斥，通常一批打包（模块多时按依赖亲和分 2–3 批）；波尾 `contract_sync.py --apply-class1` 对账回写后才开 B2——与旗舰档同一门禁。
- **主循环持有波状态**：当前批号、批任务清单、失败清单由主循环自持（引擎不在场）；为防上下文重建丢账，每批边界必须先落 state 再开下一批（§5 第 7 步是硬顺序）。

## 4. 围栏 JSON 输出契约（StructuredOutput 的替代数据面）

**schema 与 2 册 §2.7 完全一致，两档零差异——只有传输通道不同。**

### 4.1 prompt 输出段（组装器在保守档渲染的第⑥段）

> 你的最终消息必须以一个 ```json 围栏块结尾，内含**单个 JSON 对象**，符合任务书给出的 schema；
> 围栏块之后不得有任何文字，消息其余部分不得出现其他 ```json 围栏块；
> 重内容（代码、spec、分析过程）一律落盘到你的白名单文件，**不要**写进最终消息。

### 4.2 回收流程（引用 parse_agent_output.py）

1. 代理最终消息**原文落盘**：`spec/reports/agents/<wave>/<task>.txt`（主循环不通读正文，只交脚本）；
2. 解析：
   ```bash
   python3 $EXE/scripts/parse_agent_output.py --file spec/reports/agents/<wave>/<task>.txt --schema impl --json
   ```
   退出码 0 → stdout 单个 JSON 对象（即旗舰档 StructuredOutput 的等价物），直通 §5 清单第 2 步；
3. 退出码 1（无围栏块 / JSON 非法 / schema 必填缺失）→ **重派一次**：原 prompt 追加一行"上次输出无法解析（<脚本诊断>），严格按 schema 重发围栏 JSON"；
4. 重派仍失败 → 按落盘文件有无分流 `recovery-playbook.md` R1（零产出）/ R2（半产出）。

### 4.3 schema 选择表（--schema 参数）

| --schema | 使用场景 | 关键字段（必填）与枚举 |
|---|---|---|
| `impl` | infra / domains 实现代理 | `task`、`final_state`(`PASS\|ESCALATED\|ROLLED_BACK\|BLOCKED`)、`files[]`、`deferred_items[]`、`decision_gaps[]`；complex 域必填 `source_summary_roles[]`，沉浸式域必填 `safearea_layers[]`（4 层 file:line，脚本反查） |
| `findings` | audit 代理（round-1/2） | `domain`、`findings[].{file,line,severity(P0\|P1\|P2),kind(functional\|visual\|arkts\|nav\|runtime),summary,android_ref,fix}`；round-2 `failure_scenario` 必填 |
| `fix` | fix 代理 | `domain`、`fixed[]`、`skipped[].{finding_ref,reason,required_owner}`、`files_touched[]` |
| `summary` | 阶段 A 读代理 | 7 维度摘要 + `ac_candidates[]` |
| `exports` | infra 导出对账补充 | `file`、`exports[].{symbol,signature}` |

## 5. 每批边界 state_update 清单（逐条执行，不跳步）

> 损失明示：旗舰档由 wave 边界**结构保证**落账；保守档退化为**纪律约束**——本清单就是那条纪律，漏一步即漏账。

1. 收齐本批全部代理最终消息 → 原文落盘 `spec/reports/agents/<wave>/<task>.txt`；
2. 逐任务 `parse_agent_output.py`（§4.2）→ 解析结果直通落账：
   ```bash
   python3 $EXE/scripts/parse_agent_output.py --file spec/reports/agents/domains/member-pay-b1.txt --schema impl --json | \
     python3 $EXE/scripts/state_update.py --state spec/state/state.json --op task-done --payload - --json
   ```
3. 实现批：本批涉及页面逐页登记（`pending → converted`）：
   ```bash
   echo '{"page":"page_0012_MemberCenter","status":"converted","domain":"member-pay","ets":"pages/member/MemberCenterPage.ets"}' | \
     python3 $EXE/scripts/state_update.py --state spec/state/state.json --op page --payload - --json
   ```
4. `deferred_items[]` 汇入 contracts.json#deferred（批结果 JSON 经 stdin 透传 `contract_sync.py --merge-deferred - --json`；有拒绝项 exit 1 → 按 deferred-merge-report 补 resolve_by/结构化 trigger 重报）；
5. infra 批 / 半产出场景：`contract_sync.py --apply-class1` 对账回写（差异表②③类批复完才开下一批）；
6. 批编译门（§3.2 命令）→ verdict 处理；门绿后落账：
   ```bash
   echo '{"gate":"compile#domains.b1","status":"green","errors_fixed":3}' | \
     python3 $EXE/scripts/state_update.py --state spec/state/state.json --op gate --payload - --json
   ```
7. **核账后才开下一批**：本批每个任务在 state.json `waves[].tasks` 有终态（done/failed），页面登记数与批清单一致；
8. 失败任务登记折叠清单（R1/R2），到期 `cross_edits` 与遗留 skipped 项在本边界裁决（亲手 ≤10 条，超出派代理）。

## 6. audit→fix 两段式（B3 无 pipeline 原语时的替代）

**段 1：整批 audit 收齐**
1. round-0 脚本预检先跑（与旗舰档完全相同，零 token，机械 findings 落 `spec/reports/round0/`）；
2. 按域派 audit 代理（批内并行，audit 只读不写、天然无冲突），prompt = 组装器 round-1 同款（spec + source-notes 路径 + 该域 `acceptance[]` 双端核对）+ 围栏 JSON `findings` schema；
3. 全部收齐 → 逐份 parse → 与 round-0 机械 findings 合并去重 → 落 `spec/reports/audit/<domain>.findings.json`。

**段 2：逐域串行派 fix**
1. fix prompt 注入该域 findings JSON 路径 + 该域 ownership 白名单 + 复核否决权（"auditors sometimes misread"——允许否决误报）；
2. fix 围栏 JSON（`fix` schema）→ parse → 落账；`skipped[]` 带 `required_owner` 的跨域项归主循环边界统一裁决；
3. 轮次纪律与旗舰档同参：`repair_max_rounds=2`，超限记 ESCALATED。

**round-2 三横切镜头**：同两段式（镜头 audit 收齐 → 修复串行）；lens 代理以 round-0 grep 预筛的候选文件清单为导航；代码库 > `lens_shard_loc_threshold`（默认 5 万行）时每镜头按 ownership 分区并行派分片代理 + 1 个汇总去重代理，再进段 2。

**终态**：编译门 #3 全量编译 + `gate_check.py --gate final` 核账（ESCALATED > `escalated_block_ratio` 阻断）→ B4 与旗舰档完全一致。

## 7. 损失明示表

| 能力 | 旗舰档 | 保守档 | 损失与对冲 |
|---|---|---|---|
| audit→fix 衔接 | pipeline 原语，audit 落地即 fix | 两段式：整批收齐 → 逐域串行 fix | 端到端时延↑；对冲 = audit 批内并行 |
| 派发 | 同秒 fan-out，引擎持波状态 | 主循环批量 子代理派发，批间串行 | 无流水重叠；主循环上下文占用↑ |
| 输出数据面 | StructuredOutput（harness 结构保证） | 围栏 JSON + parse_agent_output.py | 解析失败重派成本（一次重试兜底）；schema 零差异 |
| 状态写入 | wave 边界结构触发 | 每批边界清单纪律（§5） | **结构保证 → 纪律约束**，漏账风险由清单 + 第 7 步硬顺序对冲 |
| 编译门 | 阶段边界 3 道 | 每批 1 道 | 门次数↑总时延↑；换更小爆炸半径与更早归因 |
| 任务粒度 | 功能域 | 域按 pages 拆 ≤5 页/批 | 跨页重复上下文部分回潮（同域批间复用 prompt 骨架对冲） |

**保留不变的收益**：契约四件、片段内嵌、prompt 组装确定性、round-0 脚本预检、状态 JSON 化——预期效率介于旧架构与旗舰档之间。
