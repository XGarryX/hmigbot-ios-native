# 故障恢复剧本（a2h-execute v2）

> 定位：把执行期的开放决策收窄为选择题（设计册 3 §3.6 六条剧本的可执行展开）。
> 每条剧本固定四段：**触发信号 → 动作序列 → state 记账 → 验证**。
> 路径约定同 SKILL.md §0：`$EXE` = 本 skill 目录（ARKTS_SKILL_DIR），`$SKILLS` = skills 根目录，工程根为当前目录。
> 通用原则：所有落账只经 `state_update.py`；所有回滚以 `ownership.json` 的 glob 为唯一边界；任何剧本都不触发交互追问（决策缺口走 G-ID 上报）。

<!-- GAP(已解决): R5 的 deferred 项汇入 contracts.json#deferred 已由 contract_sync.py --merge-deferred 承载（ID 分配/幂等去重/不变式校验在脚本内，lint_blueprint 复检仍保留为双保险）。 -->

---

## R1 代理零产出死亡（断连）

**触发信号**
- wave 返回值 `missing[]` 含该任务（模板对失败代理返回 null 统一 `.filter(Boolean)` 容错并列入 missing）；
- state.json `waves[<wave>].tasks` 中该任务无 done 记录；
- 该任务 ownership 白名单 glob 下无任何新落盘文件（`git status --porcelain` 过滤为空）。

**动作序列**
1. 失败落账（reason 固定 `zero-output`，供 --retry-failed 识别）：
   ```bash
   echo '{"wave":"infra","task":"api-pay","status":"failed","reason":"zero-output"}' | \
     python3 $EXE/scripts/state_update.py --state spec/state/state.json --op task-done --payload - --json
   ```
2. **折叠进下一 wave**（infra 任务 → domains；DB_CONTRACT 机制的模板化）——两半：
   a. **契约段条件注入（自动）**：contracts.json 中该模块 `status` 保持 `planned`，其契约段
      （exports 签名 cheat sheet）由 assemble_prompt ④段照常注入所有 `depends_on_infra` 含该模块的
      域 prompt——依赖方按契约名编码、不本地重实现，失败模块不阻塞域波；
   b. **失败任务本体重派（主循环显式）**：`state_update --op fold` 记 `folded_into:"domains"` 留痕后，
      在 domains 波运行期（或波尾快修窗口）以
      `generate_waves.py --wave infra --retry-failed` 重生成仅含失败模块的补波并派发
      （generate_waves 不自动跨波合并任务书——折叠是主循环编排动作）。
3. 若失败任务是 **domains 波域任务**（下一 wave 是 auditfix，折叠无意义）→ 当波定向重派一次：
   ```bash
   python3 $EXE/scripts/generate_waves.py --blueprint spec/blueprint --out spec/waves --wave domains --domain <key> --retry-failed --json
   ```
   重派仍零产出 → 该域记 `final_state: ESCALATED`，进 B4 核账（占比超 `escalated_block_ratio` 由 gate final 阻断）。

**state 记账**
- `waves[<wave>].tasks[]`：该任务 `status=failed`；
- `waves[<wave>].folded_into = "<下一 wave 名>"`（折叠路径）；
- 域任务重派失败：`domains[<key>].final_state = "ESCALATED"` + `escalation.reason`。

**验证**
- 折叠后重新生成的 `spec/waves/prompts/<下一波>/*.txt` 中，依赖域的 prompt 能 grep 到被折叠模块的契约段（符号名 + 签名）；
- state.json 中该任务无重复 done 记录；重入前 `gate_check.py --gate <上一门>` 退出码确认无重复收尾。

---

## R2 代理半产出死亡（限额）

**触发信号**
- wave 返回值 `missing[]` 含该任务（无 StructuredOutput 返回），**但** ownership 白名单 glob 下存在新落盘文件（`git status --porcelain -- <glob>` 非空）——典型为上下文/输出限额中断。

**动作序列**
1. **盘点落盘文件**（只看该任务白名单，不读文件正文）：
   ```bash
   git status --porcelain -- 'entry/src/main/ets/api/**'   # glob 来自 ownership.json#owners
   ```
2. **抽实盘导出、修订 cheat sheet**（半成品当真相处理，防后续依赖方按过期契约编码）：
   ```bash
   python3 $EXE/scripts/contract_sync.py --blueprint spec/blueprint --ets-root <project.root>/entry/src/main/ets --apply-class1 --json
   ```
   ①纯增量自动回写；②兼容收窄批量批复后回写；③破坏性漂移逐条裁决——三类处置完成后 contracts.json 即为修订后 cheat sheet，下次 generate_waves/assemble_prompt 自动消费。
3. 失败落账（reason 固定 `partial-output`）+ 盘点结果写入 `files_touched`：
   ```bash
   echo '{"wave":"infra","task":"api-pay","status":"failed","reason":"partial-output","files_touched":["entry/src/main/ets/api/PayApi.ets"]}' | \
     python3 $EXE/scripts/state_update.py --state spec/state/state.json --op task-done --payload - --json
   ```
4. **残余任务折叠**：同 R1 步骤 2/3——折叠任务书注明"以下文件已存在半成品，续写而非重建"，并列出步骤 1 的盘点清单。

**state 记账**
- `waves[<wave>].tasks[]`：`status=failed` + `files_touched`（半产出证据）；`folded_into` 同 R1。

**验证**
- contracts.json `modules[].status` 与实盘一致：磁盘上真实存在且导出可抽取的模块才是 `implemented`，其余保持 `planned`；
- 折叠任务的 prompt 含修订后契约段与半成品文件清单；
- `contract_sync.py` 复跑退出码 0（对账无残余漂移）。

---

## R3 单域编译三轮不收敛

**触发信号**
- `gate_check.py` 输出 `verdict: degrade:[<domains>]`——同一域连续 3 轮出现在编译门 `by_domain` 错误归因且未清零；
- **全局分支信号**：编译错误总数 > 域数×5（错误爆炸，非单域问题）。

**动作序列（局部分支，默认）**——仅处置超限域，绿域产物一概不动：
1. 按 ownership 精确回滚该域（已跟踪文件恢复 + 未跟踪新文件清除，glob 逐字来自 `ownership.json#owners["domain:<key>"]`）：
   ```bash
   git checkout -- 'entry/src/main/ets/pages/member/**' 'entry/src/main/ets/components/member/**'
   git clean -fd -- 'entry/src/main/ets/pages/member/**' 'entry/src/main/ets/components/member/**'
   ```
2. 回滚落账：
   ```bash
   echo '{"key":"member-pay","final_state":"ROLLED_BACK"}' | \
     python3 $EXE/scripts/state_update.py --state spec/state/state.json --op domain --payload - --json
   ```
3. **降档重跑该域**（粒度回退为保守档批次，仅此一域）：
   ```bash
   python3 $EXE/scripts/generate_waves.py --blueprint spec/blueprint --out spec/waves --wave domains --domain member-pay --profile conservative --json
   ```
   按 `references/conservative-mode.md` §3 的批量派发流程执行该域批次（≤5 页/批，每批一道编译门）。
4. 重跑后复检编译门 #2：`gate_check.py --gate compile#2 --build-log <新日志>`。

**动作序列（全局分支）**——错误总数 > 域数×5：
1. **呈报用户**（降档是档位决定，禁止静默）：给出错误归因表 + 建议"中止本波并整波降档重跑"；
2. 用户确认后：全部未绿域按步骤 1 逐域回滚（绿域仍保留）→ `generate_waves.py --wave domains --retry-failed --profile conservative` 重生成，按保守档剧本执行。

**state 记账**
- `domains[<key>].final_state`: `ROLLED_BACK` → 重跑后按结果改 `PASS` / `ESCALATED`；
- `gates["compile#2"].by_domain` 每轮更新（收敛轨迹留痕）；
- 全局分支：`waves.domains` 记录降档重跑批次，`workflow-params.json#profile` 不改（仅该波降档，全局档位仍以审批为准）。

**验证**
- 绿域零污染：`git diff --stat -- <每个绿域 glob>` 为空；
- 回滚域白名单下无残留未跟踪文件；
- 复检编译门退出码 0，`by_domain` 中该域清零。

---

## R4 workflow 引擎中断

**触发信号**
- 引擎报错 / 会话断开 / 宿主重启；state.json `waves[<wave>].run_id` 存在但该 wave 无波尾落账（tasks 有 pending 且无 gate 记录）。

**动作序列**（双轨，优先级固定）
1. **重入前防重复收尾**（旧 Batch8 重复派发的对冲）——先查上一完成门的 state：
   ```bash
   python3 $EXE/scripts/gate_check.py --state spec/state/state.json --gate <上一完成门名> --blueprint spec/blueprint --json
   ```
   该门已 green → 跳过其收尾步骤（contract-sync/收束/落账不得重做，deferred 不得重复申报）。
2. **轨道 A（run_id 有效）**：同会话或引擎存活 → 以 `waves[<wave>].run_id` 调引擎 `resumeFromRunId` 续跑，已完成任务由引擎跳过。
3. **轨道 B（run_id 失效，跨会话/引擎重启）**：以 state.json `waves[<wave>].tasks` 为准，只重生成残余任务：
   ```bash
   python3 $EXE/scripts/generate_waves.py --blueprint spec/blueprint --out spec/waves --wave <wave> --resume --json
   ```
   生成的脚本任务集 = `tasks[status != done]`；启动新 wave 脚本，新 run_id 落账。
   （wave 脚本与 prompt 均在工程 `spec/waves/` 随工程持久——scratchpad 路径失效不影响重入，这正是禁落 scratchpad 的原因。）

**state 记账**
- `waves[<wave>].run_id` 更新为新值（轨道 B）；
- 已 done 任务记录原样保留，不得清空重写；
- 残余任务完成后正常 task-done 落账，deferred ID 不重复申报（ID 永不复用不变式由残余任务集裁剪保证）。

**验证**
- 重生成脚本的 TASKS 数 == state.json 中非 done 任务数（`--json` 输出核对）；
- contracts.json `deferred[].id` 无重复（对账脚本 / lint 复跑）；
- 上一完成门无二次收尾痕迹（reports 目录无重复产物）。

---

## R5 页面三源数据缺失（理解期漏合成）

**触发信号**
- 域代理 StructuredOutput 的 `escalation`/`decision_gaps` 上报某 page 的 `meta.json`/`view.xml` 缺失或为空；
- 或 assemble/生成期校验发现 prompt 引用的三源路径不存在（domain-map `pages[]` 与磁盘对账不符）。

**动作序列**
1. **现场合成**（synthesize 两脚本，旧 Phase A 运行期兜底随迁；产物写回该 page 三源目录）：
   ```bash
   python3 $SKILLS/android-ui-graph-builder/scripts/synthesize_view_xml.py  <该 page 三源目录>
   python3 $SKILLS/android-ui-graph-builder/scripts/synthesize_meta_json.py <该 page 三源目录>
   ```
2. 合成成功 → 定向补跑受影响任务：
   ```bash
   python3 $EXE/scripts/generate_waves.py --blueprint spec/blueprint --out spec/waves --wave domains --domain <key> --retry-failed --json
   ```
3. **仍失败** → 双保留兜底：该页按**低置信骨架**继续（域代理按 spec 文字面实现，不阻塞整域），同时登记 deferred：
   - 条目：`kind: "forward-ref-uncertain"`（必带 `resolve_by`，不变式 2）、`location` 指向该页 ets、`trigger` 指向三源补齐条件；
   - 写入 contracts.json#deferred：条目 JSON 经 stdin 透传 `contract_sync.py --blueprint spec/blueprint --merge-deferred - --json`（ID 分配与不变式校验在脚本内）；复跑 `lint_blueprint.py --blueprint spec/blueprint --json` 双保险。

**state 记账**
- `pages[<page>].status` 保持正常生命周期（converted 但低置信，不伪造 verified）；
- 该域 task-done 正常落账；deferred 登记 `status: registered`。

**验证**
- 三源文件存在且非空（`test -s`）；
- deferred 条目：ID 全局唯一、`resolve_by` 非空、`trigger` 结构化（禁散文式 defer）；
- 补跑任务在 state.json 有新 done 记录且未产生重复 deferred ID。

---

## R6 归档 skill 需临时恢复（在途 v1 项目续跑）

**触发信号**
- 在途 v1 项目需要续跑，依赖的 skill 已按 5 册去向表归档到 `arkts-skills/archive/`（工具调用报 skill 不存在 / plugin 发现不到）。

**动作序列**（标准运维动作，非临场发挥）
1. 拷回：
   ```bash
   cp -R $SKILLS/../archive/<skill-name> $SKILLS/<skill-name>
   ```
2. 同步 `arkts-skills/README.md` 的 skill 计数行（check-counts 闸口径）；
3. 环境可跑 CI 时复跑计数闸：`bash scripts/ci/check-counts.sh`（仓库根）；
4. v1 项目续跑完成后**逆操作**：删除拷回目录、计数还原、复跑计数闸。

**state 记账**
- 不涉及 state.json（非迁移工程状态）；在 `spec/reports/` 追加一行运维记录（何时恢复、何 skill、何时归还），供迁移报告聚合留痕。

**验证**
- 恢复期间：`$SKILLS/<skill-name>/SKILL.md` 存在，plugin/CLI 能发现该 skill；
- 归还后：`skills/` 下无该目录、README 计数与实际一致、计数闸退出码 0。

---

## R7 门禁 REDUCE_FAIL 复位重跑（人工裁决修复根因后）

> AIPPT-0818 实证（ADJ-04/ADJ-10）：gate:contract-sync 与 gate:compile-2 首败后，根因修好、
> `gate_check` 独立跑出 green，但 journal 末条仍是 REDUCE_FAIL → 拍① 恒出 escalate。
> 当时无合规复位路径，两次都归档重建三账本（执行历史仅剩归档件、pages 明细丢失）。
> 现由 `land_results.py --rerun-reduce` 承载——**禁再归档重建账本**。

**触发信号**
- `next_batch.py` 输出 `action=escalate` 且 `failed_gates` 含目标 reduce（输出附 R7 hint）；
- 人工裁决已修复根因（独立复跑该门命令得 PASS/green）。

**动作序列**
1. 独立复验根因已修（用 plan 里该 reduce 的 run 命令原样跑一遍，工程根为 cwd，确认 exit 0）；
2. 复位重跑并落账：
   ```bash
   python3 $EXE/scripts/land_results.py --plan <plan> --state spec/state/state.json \
       --rerun-reduce <reduce-id> --json
   ```
   仅接受 journal 终态为 REDUCE_FAIL 的 reduce；重跑成功 append `REDUCE_PASS` 新行
   （append-only，不改历史账）；
3. 回拍①（`next_batch.py`）确认 escalate 解除、动作恢复正常推进。

**state 记账**
- reduce 状态在 journal（land_results 唯一写者），--rerun-reduce 即合规写路径；state.json 不需人工动。
- **下游折叠不自动复活**：若该门带 `on_fail.skip` 且首败时已把下游任务折叠为 folded/SKIPPED，
  rerun 通过后需对这些任务走 `generate_waves --retry-failed` 重生成前先经
  `state_update.py --op task-done` 将其复位（escalate 型门禁无 skip 闭包，rerun 即干净收场）。
- 若复位涉及契约件修改（如 contract-sync 裁决改了 contracts.json），contract_hash 已变——
  按拒绝规则 2 走「重生成 plan + 部分重跑」，不得在旧派发账上续跑。

**验证**
- journal 中该 reduce 末行 status=REDUCE_PASS；`next_batch.py` 不再输出该门的 escalate；
- 曾被折叠的下游任务状态与预期一致（复活或维持折叠均为显式裁决结果）。

---

## R8 平台侧集群故障（529 潮 / 整批白跑）

> AIPPT-0818 实证：domains 波首派 19/19 全部 API 529 零产出；当时每任务仅剩 1 次重试配额，
> 盲目重派会一轮打满 escalate。现已机械化：land_results 对非结构化失败命中
> 529/overloaded/连接类特征记 `INFRA_FAIL`（state 回 pending、attempts 豁免）；
> next_batch 见尾部连续 INFRA_FAIL ≥3 输出 `health_probe:true` 的 wait。

**触发信号**
- 一批 worker 集中死亡（API Error / 零工具调用白跑），或 `next_batch.py` 输出
  `{"action":"wait","health_probe":true}`。

**动作序列**
0. **先看代理是否还活着**（V21）：限流 429 与 529 不同——代理通常没死，只是在等配额。`ListAgents` /
   `TaskOutput` 见其仍在跑 → 对每个 SendMessage 一句「平台限流已过，按任务书回执纪律写 result 并回一行」，
   然后 `wave_status.py` 盯着 result 出现即拍④；**不重派、不写占位、不 --missing-as-failed**。
1. 落账分类（代理确已终止）：`land_results.py --plan <plan> --state spec/state/state.json --infra-fail <id>[,<id>]`
   直接记 INFRA_FAIL（V21；旧手法「把一行 FAIL 回执原文写进 result_path 让分类器猜」仍兼容但不推荐）；
   重派后 land_results 会自动跳过早于本次派发时刻的旧 result（`stale_results[]`），不再重复扫成 INFRA_FAIL；
2. 健康探测：派 1 个极小子代理任务（如「读一个 JSON 字段并回一行」）确认 subagent 通道恢复；
   未恢复 → 退避数分钟重探，**禁止整批重派**；
3. **半成品审查（V14，重派前必做）**：`python3 $SKILLS/a2h-execute/scripts/resume_guard.py --plan <plan> --state spec/state/state.json --json`——对被击杀任务的 ownership 白名单跑 `git status`，有半成品则生成 `<prompt>.resume.txt`（原任务书 + 半成品清单 + 审阅指令）。next_batch 派发时自动优先用它，worker 先 `git diff` 审阅再续作/回退，避免半成品被静默吸收（v3 E-11：R8 重派吸收 19 worker 半成品无审查）。
4. 恢复后放行：`next_batch.py --plan <plan> --state spec/state/state.json --assume-healthy --json`
   ——INFRA_FAIL 任务有效派发计数为 0，按新任务整批重吐（可先降并发：改 plan 前先观察首批）。

**state 记账**
- INFRA_FAIL 行在 journal 留痕（status=INFRA_FAIL）；state 侧任务回 pending 附 reason；
  attempts 豁免由 `_wavelib.infra_waived` 在取批/落账两侧统一计算，无需人工修账。

**验证**
- journal 中这批任务的 INFRA_FAIL 行存在且后续 attempt 正常落 OK；
- 重试配额未受损（真实失败仍有完整的重派一次机会）。

## R9 同根错误（≥2 域独立犯同一错 → 先查共同输入，再改代码）

> aippt_new_v3 实证：5 个域独立写出 11 处 `HitTestMode.Block` 死区——共同输入是
> arkui-enums 片段第 9 行的错误映射（由编译修复统计直接铸成「正确」知识注入 16/18 份任务书）。
> 逐处改代码修不掉根因：片段不改，下个工程原样复发。

**触发信号**
- 审计/真机发现同一错误模式在 ≥2 个域独立出现（同型 API 误用、同型枚举值、同型结构）。

**动作序列**
1. **先找共同输入**：`grep -rn "<错误模式关键词>" spec/waves/prompts/ $SKILLS/a2h-execute/references/fragments/`
   ——命中片段/契约段/CONTRACT 模板 = 知识源错误，不是 N 个 worker 各自的失误；
2. **改知识源**：修正片段正文，同步 index.json catalog 的 provenance（错误知识多为 compile/prior 级
   ——修正后升 runtime 并注明实证工程）；
3. **再批量改代码**：同模式全改，仅对逐处真机复核过的点保留——禁用文本窗口正则签发「安全」证书
   （v3 F-008：正则漏了 4 处，营销弹窗链吞掉 4 个 tab）；
4. round-0 有对应静态规则的（如 hittest-block），修完重跑确认清零。

**验证**
- 片段 diff 已提交且 catalog provenance 更新；全仓 grep 该模式 = 0 残留（或逐处有真机复核记录）。
