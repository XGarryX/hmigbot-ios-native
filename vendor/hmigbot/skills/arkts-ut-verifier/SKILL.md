---
name: arkts-ut-verifier
description: |
  ArkTS/HarmonyOS **单元测试（逻辑层）**验证工具。按 Spec 限定范围，以 Android 源码行为为依据，
  三步流水线（测试设计 → 测试生成 → 执行）自动产出 arkxtest（`@ohos/hypium`）单元测试，
  在真机/模拟器上验证，修复生产实现并按需更新、新增强断言测试。

  **使用场景**：

  - "验证逻辑层实现率"、"从 spec 生成单元测试"、"单元测试 TDD 验证"
  - "测量逻辑层覆盖/通过率"、"哪些业务逻辑没实现"
  - "逻辑层 RED/GREEN 报告"、"单元实现率报告"

  **不验证 UI 渲染与交互**（页面 / 控件 / 导航效果）—— UI 层验证用 `arkts-ui-verifier`；修复逻辑功能包含其必要生产接线。
metadata:
  type: domain
  domain: migration
  tags: [verification, testing, tdd, coverage, hypium, arkxtest, 验证, 测试, 单元测试, 逻辑层, 实现率]
---

# ArkTS Spec 单元测试（逻辑层）验证工具

（可选第零步：安卓 oracle 采集）+ 三步流水线（设计 → 生成 → 执行）+ 一段 **fix-loop**（默认开）。Spec `## 验收标准` 限定迁移范围；功能点的完善、修改和新增实现以及测试预期以 Android 源码实际行为为准，明确批准的平台差异须引用决策。fixer 修生产代码并完成必要应用接线，按需更新、新增测试及记录，独立执行验证后才判 GREEN。

> **第零步（默认开，可跳过采集）**：从 Spec 的 `android_source_anchors` 追到 Android 实现，采集行为、分支和带溯源的字段级预期。跳过采集不代表可以跳过证据：可直接读取 Android 源码或复用核验仍适用的 oracle；证据不足的条目记 `needs_review`，不凭 Spec 猜造功能或预期，其余验证继续。详见 `references/android-oracle-protocol.md`。

> **功能依据与测试质量**：各阶段必读 `references/fixer-test-policy.md`。禁止弱断言、没有实质行为验证的简单测试，以及为通过而删测试、改预期或扩大 mock；短小但能精确区分行为的测试有效。Spec 与同一口径的 Android 行为不同时，以已核实的 Android 行为为准并记录差异；源码或批准差异依据仍不明才保留缺口。

> **验证范围**：android-oracle 补充预期值，不自动增加已执行的调用链。渲染与 UI 交互不属于本 skill；跨模块逻辑和可从 ArkTS 调用的系统/native 接口是否可测，取决于真实入口、运行环境与可观测结果，不能一概判不可达。`golden-degraded` 不等于已覆盖；`partial` 的具体缺口应列明。

> **框架**：arkxtest 的 ArkTS 单元框架 `@ohos/hypium`（`describe/it/expect`），编译进测试 HAP、随
> `aa test` 在设备上跑。与 PC 端的 DevEco Testing Hypium（Python 黑盒）无关。
>
> **只验证逻辑行为**：UI 渲染、控件和导航交互效果由 `arkts-ui-verifier` 验证；fixer 为完成逻辑功能所需的页面/启动入口业务接线仍在本 skill 修复范围内。
>
> **MODE 参数**：`verify_only` = 只跑三步出报告；`verify_fix`（默认）= 三步跑完后若有 RED 自动进 fix-loop。

## 依赖与版本规则

各阶段先读 `references/mock-policy.md`：默认真实执行，只 mock 有明确必要原因的最小边界；被测行为与真实持久化链路不能被替换。开始设计前核对目标 Hypium 锁定/安装版本、SDK API、Stage 模型及编译模式，使用 `references/api/hypium.md` 中对应版本的接口。

主线程和 executor 必读 [执行检查点](references/execution-checkpoints.md)：公共设施预检和首批试生成先行，修复按完整依赖批次编译，编译返工在本轮闭环；最终质量检查和完整双 HAP 编译通过后再提交、全量实跑。

生成 agent 及获得对应所有权的 fixer 写 Feature 独占测试与 mock 请求；executor 在 barrier 后单点维护 `List.test.ets`、合并 `src/mock/mock-config.json5` 并分运行组。具体规则见 `references/import-mock.md`。测试版本、Context、mock 接线问题先修测试侧，不以公开 private 字段或添加全局 Context 回退凑绿。

## Join 协议（收口五条款）

1. **主动收口**：主线程记录每个实例的唯一任务名、句柄、工作范围、文件所有权和预期产物，使用宿主等待工具持续跟进，并以宿主返回的任务完成状态确认交回。单次等待超时、文件存在或日志静默均不代表完成，不因这些信号终止重派，也不以“等待子代理”为由结束任务。
2. **完成后验收**：任务完成后回读准确产物，核对范围、ID、数量及本阶段契约；完成状态不等于验收通过。失败或句柄失联时先核实实际状态和已保存进度，确认旧实例不能继续写入后才恢复任务，不与原写者重复派发。
3. **按依赖汇合**：每个已完成且验收通过的 Feature/页面可以进入其下一阶段，无需等待无依赖的其它设计；共享注册、构建及设备执行严格遵循本文 barrier、冻结窗口和单一 owner 约束。最终报告前须收口全部本轮任务并对账产物，尚有阻塞时准确报告未完成范围。
4. **继续不等于遗弃**：局部缺口不妨碍独立任务继续，但主线程须持续记录并处理对应任务和恢复条件；不会因暂时放行或用户交互遗忘句柄，也不能以占位文件冒充子代理交付。
5. **派发方负责结果**：本 skill 的角色只执行分配阶段，不递归派发或 fire-and-forget；主线程统一接收、验收和协调返工。并发 owner 不覆盖其他任务或用户的改动；角色未注册时明确报告配置缺口。

## 执行模型

**入口**：必须用 `$arkts-ut-verifier` 在主对话中调用。各阶段派发已注册的具名 Codex agent，只传本轮运行参数，不重复拼接整份 prompt。角色定义位于本包 `codex/agents/arkts-ut-*.toml`，安装后位于 `.codex/agents/`；各角色继承会话模型。

主线程将当前 skill 目录解析为绝对路径 `SKILL_DIR`，每次派发均传入；agent 中 `references/`、`scripts/` 相对该目录解析。下文 `dispatch_codex_subagent(...)` 是具名派发的伪代码，执行时使用宿主提供的子 agent 工具及已注册角色；角色缺失时反馈具体配置错误，不把伪代码当作可调用工具。**oracle、设计、生成的每个实例只处理一个 Feature，各最多 8 路并发**，有空位即补下一个 Feature，除首批预检窗口外不按固定小批等齐。设计与生成使用独立队列，可以同时运行；修复阶段按文件所有权及完整依赖批次划分工作项。

**准确输入**：主线程先运行本 skill 的 `scripts/feature_inputs.py --project-root <项目绝对路径> [--scope F001,F003]`，读取返回的 Feature 清单。脚本兼容 `F001-xxx.md` 和 `F001_xxx.md`，仅在选中范围校验主文件 ID 唯一性；`F001-xxx.state-machine.md` 等同名补充文档进入 `addendum_files`，不占用另一个 Feature ID。清单给出各阶段独占产物的绝对路径。主线程再逐 Feature 运行 `scripts/ac_inputs.py --feature-file <feature_file> --feature-id <feature_id>`，将返回数组写入该清单项的 `ac_inputs`，保存完整清单供各阶段使用。脚本提取已勾选与未勾选 AC，保留源稳定 ID；输入错误先核对源文件或既有映射，禁止按行号重新发号、修改基线或静默漏掉 AC。每次派发都从同一清单取值：

- 共用：`SKILL_DIR`、`PROJECT_ROOT`、`ANDROID_SOURCE_ROOT`、单个 ID 的 `FEATURE_SCOPE`、`FEATURE_FILE`（实际主 Spec 文件）、`ADDENDUM_FILES`（清单的 `addendum_files`）、`AC_INPUTS`（清单的 `ac_inputs`）。补充文档只读，按主文件 `addenda` 和 `impl` 指针核对关联与完整性，缺失指针目标返回具体输入错误；不读取范围外 Feature。
- oracle：另传 `ANDROID_SOURCE_ROOT`、`ORACLE_SCRIPT`（实际 skill 目录下 `scripts/android-oracle.sh` 的绝对路径）、`ORACLE_FILE`。
- 设计：另传 `ORACLE_FILE`（本轮无 oracle 则为空）、`DESIGN_FILE`、`UNIMPLEMENTED_FILE`。
- 设计/生成/修复另传 `PREFLIGHT_FILE`（主线程指定的实际预检记录路径，缺口也须传递）；生成另传 `MODE=generate`、`DESIGN_FILE`、`GENERATION_FILE`、`TEST_FILE`。
- 注册与执行：传本轮完整 `FEATURE_INPUTS` 清单（含上述实际文件路径），以它确定范围及有效产物，不从残留文件反推本轮范围。预检/编译检查另传 `CHECKPOINT_ID`、准确 `OWNED_FILES`，编译子集用 `CHECK_FEATURE_INPUTS`、结果用 `CHECKPOINT_FILE`；最终完整范围不随子集缩小。
- 修复：传 `ANDROID_SOURCE_ROOT`、受影响 `FEATURE_INPUTS`、准确问题文件和生产/测试/设计记录的 `OWNED_FILES`；有已核验公共根因时另传 `ROOT_CAUSE_GROUPS`，逐 ID 义务仍保留。Feature 输入字段沿用脚本输出；独占 mock 文件及请求路径按实际依赖补入，不猜路径。

agent 不再自行拼接 `F001_*.md`、英文别名或项目根下的脚本路径；路径缺失或 Feature 不匹配时反馈具体输入错误。主线程在派发前修正清单，不能用另一个文件兜底。实例完成并回读产物后，按宿主机制释放其占用槽位，再补就绪任务；保存的文件承担交接，不保留空闲实例挤占并发容量。

**并发容量**：派发前核对宿主可用槽位；设计和生成各 8 路重叠时，工作池须容纳最多 16 个子任务（主线程另按宿主计数）。宿主实际限制较低时如实报告有效并发并保留就绪队列，不能声称已按 8 路执行。仅状态轮询可以分段等待，**不设置 oracle/设计/生成的时间预算，不因静默、等待次数或运行时长终止重派**；按真实完成、明确错误或用户取消处理。恢复同一 Feature 时复用已保存的进度，避免重复探索。

**第零步开关**：`UT_ANDROID_ORACLE=on`（缺省）且安卓根可达时执行；barrier⓪ 等本轮采集任务全部返回，允许各 Feature 以 `full/partial/spec_only/SKIPPED` 收口，不要求每项都有 oracle 文件。无锚点先走发现阶梯；off 或根不可达时仍可设计盘点和运行已有测试，新增功能/预期按证据门处理，`spec_only` 不构成已验证行为依据。

| 步骤 | 做什么 | 并发？ | Codex Agent |
|------|--------|------|------|
| 第零步：安卓 oracle 采集（可选·默认开） | 解析锚点、保存已确认事实，完成后回读 oracle 表 | ✅ 8 路，每实例一个 Feature | `arkts-ut-oracle-collector` |
| 第一步：测试用例设计 | 记录真实入口、隔离方式、可执行类型和实现状态；输出设计及未实现诊断 | ✅ 8 路，单 Feature 完成即进入生成队列 | `arkts-ut-test-designer` |
| 第二步：测试用例生成 | 可执行行生成强断言；其余逐条记录原因；最后统一注册 | ✅ 8 路，与设计重叠；注册单发 | `arkts-ut-test-generator` |
| 第三步：注册与执行 | 单点注册，补基础设施 → 编译双 HAP → 跑设备 → 出报告（含 oracle 来源分布 + 溯源行号回校） | ❌ 全局单步 | `arkts-ut-test-executor` |
| Fix-loop：功能与测试修复 | 按 Android 行为修复实现及必要生产接线，按需更新、新增强断言测试和记录 | ✅ 最多 8 路，按文件所有权划分 | `arkts-ut-fixer` |

> **第零步是 step1 的可选前置**。只有 `collection_complete: true` 的本轮 oracle 产物才供设计使用；增量保存的草稿不是完成信号。

```
主线程：解析准确 Feature 清单与独占产物路径
  [executor · MODE=preflight] 核对版本/设备，补齐并验证公共测试设施
  （oracle/设计分析可继续；工程构建期间无其它工程输入写者）
  ↓
Step 0  ┌ [oracle F001] … [oracle F008] ┐  最多 8 路，完成一个补一个
（可选）  └──── barrier⓪ 容忍部分 SKIPPED ──┘  → spec/verify/ut/android-oracle/F*.md
  ↓
Step 1  [设计 F001] … [设计 F008]         最多 8 路
          ↓ 每个 Feature 完成并校验后立即入队
Step 2  [首批完整 Feature 生成 → executor 编译/代表性试跑 → 其余生成滚动并行]
        最多 8 路，与其余设计同时运行；缺设备时保留缺口并继续离线生成
        └── barrier②：全部设计和生成任务完成，逐 ID 对账 ──┘
        [执行 agent · MODE=register]           单发一次，重建 List.test.ets
  ↓
Step 3  执行（编译 + 跑设备 + spec/verify/ut/ut-report.md + 双写 spec/verify/ut/round-0/ut/）  全局单步
  ↓
[MODE=verify_fix 且 round-0/ut/ 有失败]
  ↓
fix-loop  循环：完整依赖批次内 fixer 最多 8 路 → 批次编译/本轮返工
          → 最终质量/影响对账 → 单点注册/完整编译 → commit → 全量设备复测 → reconcile
```

每个 agent 返回结构化摘要。Spec/设计输入缺失、产物无法写入等真实错误在对应 Feature 上报 `BLOCKERS` 并由主线程处理；其它独占任务可继续，真实阻塞未解决前不能宣告全量完成。**未实现项数量、诊断格式警告，以及有依据的 `no_entry/needs_review/ui_only` 分类不构成全局 blocker**。不能把分类当作测试通过或伪造占位断言。

> **Feature 完成检查**：收到设计 agent 的完成返回后，回读其准确 `DESIGN_FILE`，核对用例 ID、分类、调用入口和数量，再派该 Feature 的生成器；仅文件存在不算完成。设计在生成读取期间冻结，需修正时先收停同 Feature 的生成写入再更新。fix-loop 中可按所有权更新受影响设计、generation、诊断及测试，源码入口变化后不得继续冻结旧 `no_entry`。最终 barrier② 汇总产物并单发注册，共享 List/mock 始终单点写入。

## 未实现项诊断（不阻断流程）

每个 Feature 设计完成时，主线程顺带汇总其 `UNIMPLEMENTED_FILE`，列出功能点、状态、`spec_ref`、`source` 和关联用例。这是**设计期高/中置信初判**，不是实跑结论；诊断汇总不等待其它 Feature，不延迟已就绪的生成任务。

- **设计与断言不减弱**：保留全部范围内逻辑测试点，按 Android 行为及已批准差异确定预期。证据明确且 `testability=ut` 的用例即使实现占位、缺分支或预期会失败，也必须生成强断言；只有已核实无入口或依据待确认的行才进入缺口清单。缺入口后补实现时同步补测，不能沿用旧分类。
- **汇总不要求用户确认**：不等待“已补全”通知，不要求清单清空，也不要求用户额外放行。诊断汇总后继续工作，不能把汇总报告当成本轮 UT 已完成。
- **诊断格式不控制流程**：主线程按 `references/unimplemented-schema.md §五` 校验，格式问题交对应设计 agent 修正；仍不合格的文件标注诊断警告，不纳入可信计数，也不阻断测试生成。已有诊断文件中的额外控制字段不参与流程判断。
- **结果以实际验证为准**：诊断清单不直接给用例判 RED/GREEN，也不作为 `arkts-ut-fixer` 的派单输入；step3 产出真实执行报告后，`MODE=verify_only` 出报告结束，`MODE=verify_fix` 按运行结果进入既有 fix-loop。

```pseudocode
on FeatureDesignCompleted(feature):
    回读并核对 feature.design_file 的契约、分类和 ID
    校验并汇总该 Feature 诊断（格式问题修正或记警告）
    将 feature 放入生成就绪队列；先按 execution-checkpoints.md 完成首批试生成
    首批窗口结束或明确离线降级后，生成运行数 < 8 时立即派发
    设计运行数 < 8 时补下一个尚未设计的 Feature
# 所有设计与生成完成后：核对设计总量 = 已生成 + no_entry + needs_review
# ui_only 另列；注册实际测试文件，继续编译和执行
```

## Fix-Loop 主线程编排（MODE=verify_fix）

第三步 execute 跑完写完 `spec/verify/ut/round-0/ut/`（baseline）后，主线程依据下列伪代码循环修复直到收敛。详细字段定义见 `references/fix-file-schema.md` + `references/reconcile-rules.md`；fixer 行为由具名 agent `arkts-ut-fixer` 定义。

**修复固定使用最多 8 路工作池**：按 `references/fixer-dispatch.md` 先分配准确问题文件和源码文件所有权，本批独立任务足够就派满 8 个实例，有空位即补本批下一个；批次交回后统一编译再开下一批。每个实例只处理自己的工作项；涉及同一源码文件的问题交同一所有者，不能单靠 Feature 切分。任务不足或存在文件/前置依赖时如实报告有效并发，不派空任务。修复也不设时间预算，不因运行时长终止重派。

每个 fixer 独占 `round-{N+1}/fixers/<WORK_ITEM_ID>.md`，不操作共享暂存区。所有权请求在本轮内协调续跑，不转成业务 `skipped/manual_review`；每批交回后由唯一 executor 编译，本轮处理可修编译问题；全部工作项完成、最终独立质量检查和完整双 HAP 编译通过后，主线程才写全局 `fixer-summary-ut.md`、统一提交，再由一个执行 agent 全量复测。不同修复轮次不重叠。

**必要测试更新**：纯实现修复且原测试仍适用时保持测试不变；入口从无到有、必要调用接口变化或测试自身错误时，fixer 按 `references/fixer-test-policy.md` 更新受影响测试和记录。主线程反查变更入口关联的旧 `no_entry`、生产调用方及 GREEN 测试，补齐工作项与文件所有权；不能仅因旧证据失效或测试职责而转人工。已标人工/跳过但原因仅是这些内部衔接问题的条目，经主线程核实清回 null 后恢复处理，真正缺证据的条目保持明确原因。

**逻辑函数一比一复刻与完整交付**：主线程与 fixer 必读 [生产接线策略](references/fixer-wiring-policy.md)。有逻辑的函数修复时逐条对照 Android 语句与控制流程，保留全部行为分支、执行顺序、状态/异常/副作用；通过 `ANDROID_EVIDENCE.function_parity` 交付源函数到真实目标实现的对应关系，不能仅凭 UT 通过判定等价。默认直接修原函数/已有 ViewModel 或 Service，不新增 Coordinator 或等价转调层；必要业务类和既有架构例外按接线策略核验。把实现、实际调用方、结果消费、必要生命周期和声明分给同一工作项，允许 fixer 修改准确获授权的页面/common/启动入口等业务接线。fixer 同步受影响测试和记录，主线程协调额外所有权并复核失效 round 分类；内部接线待办须本轮续跑，不能止于新建服务或转交需求。必要接线未完成保持 `partial/BLOCKED`，不能计完整实现。

```pseudocode
if MODE == "verify_only":  exit
if round-0 实际测试全 GREEN and 无未验证设计点/TEST_REWORK/DISPOSITION_RECHECK/陈旧分类:
    write final-summary.md (PASS); exit

N = 0; no_progress = 0
MAX_ROUNDS = 10; NO_PROGRESS_ROUNDS = 2

while N < MAX_ROUNDS:
  # Step 1: 先合并共同根因/共享写文件，按完整依赖安排批次，批内最多 8 路滚动派发
  work_items = plan_owned_work_items(round-{N}/ut/)  # 见 fixer-dispatch.md
  for batch in plan_dependency_batches(work_items):
    while 有本批就绪工作项 or 有运行实例 or 有待协调所有权请求:
        while 有本批就绪工作项 and running_fixers < 8 and 宿主有可用槽位:
            item = pop_ready(batch)
            dispatch_codex_subagent("arkts-ut-fixer",
                    SKILL_DIR=SKILL_DIR, PROJECT_ROOT=..., ROUND=N+1, INPUT_DIR=...,
                    ANDROID_SOURCE_ROOT=..., FEATURE_INPUTS=item.feature_inputs,
                    WORK_ITEM_ID=item.id, ISSUE_FILES=item.issue_files,
                    PREFLIGHT_FILE=实际预检路径, ROOT_CAUSE_GROUPS=item.root_cause_groups 或 [],
                    OWNED_FILES=item.owned_files, SUMMARY_FILE=item.summary_file)
        等待完成返回或所有权请求；回读摘要、核对实际改动
        协调所需文件，续跑未完成问题；完成实例释放槽位并补本批任务
    停止派发写者；核实所有工程输入写者已交回且无依赖半成品
    dispatch_codex_subagent("arkts-ut-test-executor",
            SKILL_DIR=SKILL_DIR, PROJECT_ROOT=..., ROUND=N+1, MODE=compile_check,
            FEATURE_INPUTS=完整清单, CHECK_FEATURE_INPUTS=累计完成及受影响清单, CHECKPOINT_ID=round_N+1_batch_ID,
            ANDROID_SOURCE_ROOT=..., PREFLIGHT_FILE=实际预检路径,
            ANDROID_EVIDENCE=累计函数等价证据, TEST_UPDATES=累计更新摘要, WIRING_EVIDENCE=累计接线证据,
            OWNED_FILES=准确检查点写权限, CHECKPOINT_FILE=本批记录路径)
    消费 COMPILE_REWORK/TEST_REWORK；需要语义修改则结束构建并交回原 owner，同轮修正后重验
    修正尝试按检查点累计；达到上限或确认无法继续时写 compile-failure.md 并结束，不能首次失败就退出或跳到下一轮
  # barrier：无活跃源码写入、无未处理工作项/所有权请求；逐 ID、逐文件对账
  汇总 EDITED / RETEST / SKIPPED / BLOCKED / FILES_MODIFIED / DISPOSITION_HINTS / ANDROID_EVIDENCE / WIRING_EVIDENCE / TEST_UPDATES
  反查变更入口关联的旧 no_entry/UNREACHABLE、依赖测试与生产调用方
  未完成的必要接线/补测/分类同步本轮协调原 fixer 续跑，再回到 barrier；真实外部/证据阻塞准确保留
  dispatch_codex_subagent("arkts-ut-test-executor",
          SKILL_DIR=SKILL_DIR, PROJECT_ROOT=..., MODE=register,
          FEATURE_INPUTS=完整清单, ANDROID_SOURCE_ROOT=..., ANDROID_EVIDENCE=本轮函数等价证据, TEST_UPDATES=本轮更新摘要,
          WIRING_EVIDENCE=本轮接线证据, PREFLIGHT_FILE=实际预检路径, OWNED_FILES=准确注册与共享设施写权限)
  回读独立质量检查和注册结果；TEST_REWORK 退回对应所有者并在本轮修正后重验
  若有未完成内部接线/补测/质量退回/陈旧分类：保持开放，本轮协调续跑后重验，禁止进入收敛判断
  dispatch_codex_subagent("arkts-ut-test-executor",
          SKILL_DIR=SKILL_DIR, PROJECT_ROOT=..., ROUND=N+1, MODE=compile_check,
          FEATURE_INPUTS=完整清单, CHECK_FEATURE_INPUTS=完整清单, CHECKPOINT_ID=round_N+1_final,
          ANDROID_SOURCE_ROOT=..., PREFLIGHT_FILE=实际预检路径,
          ANDROID_EVIDENCE=本轮函数等价证据, TEST_UPDATES=本轮更新摘要, WIRING_EVIDENCE=本轮接线证据,
          OWNED_FILES=准确检查点写权限, CHECKPOINT_FILE=最终记录路径)
  若有编译/质量退回：同轮修正并重验受影响质量、ID、接线与完整构建，未通过不得提交
  主线程写 round-{N+1}/fixer-summary-ut.md

  if EDITED.count == 0 and RETEST.count == 0 and BLOCKED.count == 0:
      # 仍有仅缺外部证据/真实不可达等残留时只能 CONVERGED，不能 PASS
      write final-summary.md (CONVERGED / FAIL, 准确残留与无可处理原因); break

  # Step 2: 按 DISPOSITION_HINTS 更新 round-{N}/ut/<id>.md frontmatter
  apply disposition_hints to prev round files

  # Step 3: 最终质量与完整双 HAP 编译通过后提交；保留用户和其它任务原有工作区/暂存区改动
  if 有本轮确认的文件改动:
      git add <本轮确认的 FILES_MODIFIED 及汇总产物>
      git commit -m "autofix-ut: round-{N+1}"
  # 仅需复测时保留依据，不制造源码/测试改动或空提交

  # Step 4–5: executor 核验最终构建指纹，失效则重编；安装并全量实跑，写问题与 delta
  dispatch_codex_subagent("arkts-ut-test-executor",
          SKILL_DIR=SKILL_DIR, PROJECT_ROOT=..., ROUND=N+1, MODE=verify_only,
          ANDROID_SOURCE_ROOT=..., FEATURE_INPUTS=完整清单, TEST_UPDATES=本轮更新摘要,
          ANDROID_EVIDENCE=本轮函数等价证据, WIRING_EVIDENCE=本轮接线证据, PREFLIGHT_FILE=实际预检路径,
          CHECKPOINT_FILE=最终记录路径, OWNED_FILES=准确执行写权限, ...)
  后续若需写源码/测试/配置：结束执行，同轮返工并补验收/编译/提交，再从最终快照全量实跑
  主线程核实 DISPOSITION_RECHECK，清除仅因旧禁测/陈旧分类等失效原因的处置后再 reconcile
  TEST_REWORK 保持开放并派回独占所有者；不能把待修测试计为通过或收敛
  UNVERIFIED_CASES 逐 ID 纳入最终未验证范围；缺行为证据不是 GREEN，也不凭空派生产修复
  若编译在 executor 的既有修正流程后仍阻塞：写 compile-failure.md 并 FAIL，不能先行一错即退

  # Step 6: 收敛判定（读 round-{N+1}/_ut_delta.md）
  # 「可修失败数」= round-{N+1}/ut/ 下 disposition==null 的开放问题文件（manual_review / skipped 不算 actionable）
  if 可修失败数(disposition==null) == 0 and 无TEST_REWORK/DISPOSITION_RECHECK/待更新测试/陈旧分类:
      # 只有全范围实际 GREEN 且无未验证设计点才 PASS；真实缺证据/不可达等残留只能 CONVERGED
      write final-summary.md (PASS / CONVERGED); break
  if delta.REGRESSED.count > 0:
      write regressed.md  # 区分源码回归与测试质量重分类；可修项保持开放，不仅因回归自动转人工
  if delta.RESOLVED == 0 and delta.TRULY_NEW == 0:   # TRULY_NEW = _ut_delta「Newly opened」(不含 regressed)；regressed 是净负功，不算进展
      no_progress += 1
      if no_progress >= NO_PROGRESS_ROUNDS:
          write stalled.md (FAIL); break
  else:
      no_progress = 0

  N += 1

if N >= MAX_ROUNDS:  write final-summary.md (FAIL, "达 MAX_ROUNDS")
```

### 退出条件

| 场景 | 状态 | 产物 |
|---|---|---|
| baseline 实际测试全 GREEN，且无未验证设计点、待补测/复核或陈旧分类 | PASS | `spec/verify/ut/round-0/_ut_summary.md` |
| 循环全范围验证通过，且无未验证设计点、待补测/复核或陈旧分类 | PASS | `spec/verify/ut/round-{N}/final-summary.md` |
| 内部可处理项清空，仅真实缺证据/外部前置/不可达等残留 | CONVERGED | `final-summary.md` 明示未验证范围，状态文件不得写 passed |
| 达 MAX_ROUNDS | FAIL | 同上 |
| 连续 NO_PROGRESS_ROUNDS 轮无进展 | FAIL | `spec/verify/ut/round-{N}/stalled.md` |
| Step 1 无 EDITED/RETEST/BLOCKED | CONVERGED / FAIL | `final-summary.md` 按准确残留与退出原因判定，不等于 PASS |
| executor 编译修正流程后仍失败 | FAIL | `compile-failure.md` |

### 铁律（违反 = 流程作废）

1. **修改后 commit**：有本轮改动时 Step 3 提交失败不得跳过；只复测时不制造空提交
2. **fixer EDITED ≠ PASS**：fixer 报"修了 N 个"是机械计数；真假由本轮修复后的独立 execute 实测（reconcile）
3. **REGRESSED 独立诊断**：保留其它已验证修复，不 git reset；按 Android 依据区分生产回归与测试质量问题，可修项继续派发，只有实际缺证据/需裁决才转人工
4. **Android 源码决定范围内功能行为**：完善与补实现必须追溯 Android 分支、数据流和副作用；已批准的平台差异引用决策，不盲搬 Android API。Android 来源的 RED 经依据与适配核对后正常修复，不一律转人工；缺 golden 不以宽松断言凑通过。预期变更必须有独立 Android/决策证据，由 executor 复核。
5. **并发只改独占文件，构建独占工程输入**：8 路 fixer 不共享生产/测试/设计记录写权限、摘要或暂存区；每批交回后编译，构建期间无其它工程输入写者。全部完成并通过最终质量/完整编译后才提交和全量复测，检查点不推进轮次。
6. **补能力必须补验证**：新增入口和必要测试更新在本轮内闭环；禁止弱断言、简单存在性测试及为凑绿修改预期，不能通过删用例、旧 `no_entry` 或转人工代替验证。

## 前置准备

### 目录约定

```
<project_root>/
├── spec/
│   ├── baseline/features/      ← 输入：功能 Spec（F001_xxx.md …，frontmatter 带 android_source_anchors）
│   └── verify/ut/              ← 本 skill 独占根目录（ui-verifier 在 spec/verify/ui/、visual 在 spec/fix/，三者互不读写、无共享状态）
│       ├── android-oracle/     ← 第零步产出（可选）：安卓 oracle 表（每有锚点 Feature 一份；arkts-ut-fixer 禁写、arkts-ut-test-executor 只读）
│       ├── ut-design/          ← 第一步产出：测试设计（每功能点一份）
│       ├── generation/         ← 第二步产出：每 Feature 一份逐用例生成/缺口记录
│       ├── unimplemented/      ← 第一步附带产出：未实现功能点清单（每有命中项 Feature 一份 F*.json；仅作诊断、不阻断流程，schema 见 references/unimplemented-schema.md）
│       ├── preflight.json      ← 版本、公共设施已验证用法及环境缺口；不计业务结果
│       ├── checkpoints/        ← 独占编译证据与本轮返工记录；不推进轮次
│       ├── ut-report.md        ← 第三步产出：执行报告
│       ├── _state.yaml         ← 本 skill 私有轮次状态（current_round 等）
│       ├── round-0/            ← baseline = step3 execute 首跑
│       │   ├── _ut_index.md / _ut_summary.md
│       │   └── ut/<id>.md
│       ├── round-1/            ← fix-loop 第 1 轮回跑
│       │   ├── _ut_index.md / _ut_summary.md / _ut_delta.md
│       │   ├── fixer-summary-ut.md
│       │   ├── fixers/             ← 每个修复工作项独占摘要，主线程汇总到上方文件
│       │   └── ut/<id>.md
│       └── round-N/ …
└── entry/src/
    ├── main/ets/               ← 源码（设计/生成时读；fixer 按准确所有权修实现及页面/common/启动入口等必要业务接线）
    └── ohosTest/ets/test/ut/   ← 第二步产出：测试代码
```

### 环境变量

```bash
export HDC=/Applications/DevEco-Studio.app/Contents/sdk/default/openharmony/toolchains/hdc
export BUNDLE=com.example.your_app      # 实际包名（AppScope/app.json5）
export DEVICE=127.0.0.1:5555            # 模拟器 / 真机设备 ID
# 第零步（可选）：被迁移的安卓源码仓根；不可达时已有验证继续，受影响新行为须有已核验证据
export ANDROID_SOURCE_ROOT=             # 调用方提供，不硬编码（skill 不假设它在哪）
export UT_ANDROID_ORACLE=on             # on（缺省）| off：控制批量采集，不关闭 Android 行为依据要求
```

## 前置检查（派发前）

主线程先派唯一 executor 的 `MODE=preflight`，传 `PROJECT_ROOT/SKILL_DIR/FEATURE_INPUTS`、准确设施 `OWNED_FILES` 与 `PREFLIGHT_FILE=spec/verify/ut/preflight.json` 的绝对路径。先保存版本/路径及已知设备状态，供分析阶段读取；补设施和构建时独占工程输入。首批业务用例准备好后，用同一记录及 `CHECK_FEATURE_INPUTS=首批完整清单` 续跑预检，按检查点策略试跑、处理测试侧返工后释放其余生成队列。预检模式和首批试跑均不推进 round。

```bash
python3 "<实际 skill 绝对路径>/scripts/feature_inputs.py" --project-root "<项目绝对路径>"
# 读取 JSON 清单；有范围时加 --scope F001,F003，后续派发只使用清单中的准确路径
$HDC list targets                                        # 开始即探测；设备实跑前必须可用
# 第零步（可选）：校验安卓源码可达；缺失只降级提示，不 exit
if [ "${UT_ANDROID_ORACLE:-on}" = "on" ] && [ -n "$ANDROID_SOURCE_ROOT" ] && [ -d "$ANDROID_SOURCE_ROOT" ]; then
  echo "[step0] android oracle 已启用：$ANDROID_SOURCE_ROOT"
else
  echo "[step0] 跳过（未设 ANDROID_SOURCE_ROOT 或不可达或 off）→ 继续范围盘点与已有验证；新增行为/预期须有已核验 Android 证据"
fi
```

派 step1 前，主线程先解析本轮 `FEATURE_SCOPE`，仅清理这些 Feature 对应的已确认旧诊断文件；不清理范围外文件。设计 agent 重新读取源码并生成本轮诊断，主线程只汇总本轮文件，避免混入旧结论。

Spec 为空 → 告知用户先运行 Spec 生成 skill，**终止**，不要让 Agent 自己造 Spec。**（此 spec 硬终止不变；安卓源不可达只降级，绝不终止。）**

## 输出清单

- **执行前证据**：`preflight.json` 和 `checkpoints/<CHECKPOINT_ID>.json`，分别记录设施验证与编译结果，不计正式业务运行。

0. **安卓 oracle 表**（可选·第零步）：`spec/verify/ut/android-oracle/F*.md`（每有锚点 Feature 一份，含枚举值/wire tag/算法 I-O/完整集/golden 降级 + 逐行溯源）
1. **测试设计**：`spec/verify/ut/ut-design/F*.md`（第一步）
1.5. **未实现功能点清单**（第一步附带·仅有命中项·不阻断流程）：`spec/verify/ut/unimplemented/F*.json`（每条注明出自哪个 Feature、功能点是什么、有源码就附源码片段；设计期高/中置信初判，不替代实跑结论；汇总后照常生成并执行测试；schema 见 `references/unimplemented-schema.md`）
2. **测试代码及生成记录**：`entry/src/ohosTest/ets/test/ut/F*.test.ets` + `List.test.ets`；`spec/verify/ut/generation/F*.json` 逐 ID 记录已生成和未生成原因（第二步）
3. **测试基础设施 + 双 HAP**：`entry/src/ohosTest/...` + `entry/build/.../*-signed.hap`（第三步）
4. **执行报告**：`spec/verify/ut/ut-report.md`（第三步）
5. **Fix-loop 产物**（仅 `MODE=verify_fix`）：`spec/verify/ut/round-N/ut/<id>.md` + `_ut_index.md` + `_ut_summary.md` + `_ut_delta.md`（N≥1）+ `fixers/<WORK_ITEM_ID>.md` 与主线程 `fixer-summary-ut.md`（N≥1）+ `final-summary.md`（退出时）

## 快速检查清单

- [ ] 已解析准确 Feature 清单，输入路径唯一且存在；三个阶段各 8 路并发，无时间预算
- [ ] **（可选·step0 后）**：`UT_ANDROID_ORACLE=on` 且 `ANDROID_SOURCE_ROOT` 可达时，有锚点的 Feature 已产 `spec/verify/ut/android-oracle/F*.md` 且 `oracle_status=full/partial`（带 `oracle:path:line` 溯源、golden 项未写硬字面量、完整集用脚本点清）；off 或无可用事实时继续已有验证，受影响新行为/预期须有直接源码或已核验证据，否则明确 `needs_review`；已保存 oracle 须为 `collection_complete: true`
- [ ] 第一步后：`spec/verify/ut/ut-design/` 每个 Feature 一份设计，每条逻辑层 AC 有用例行；`## 服务层 / ## 数据流`（英文同义 `## Service layer / ## Data flow`）列出的输出模式 / 基数布局分支也各有一行；有 oracle 表时「预期结果」为字段级具体值 + 来源标 `样本(安卓)`；**读源码高置信看出没实现的功能点已记进 `spec/verify/ut/unimplemented/F*.json`**（注明 Feature + 功能点 + 源码片段；无明显未实现则无文件，且设计本身一字未减）
- [ ] 设计行已记录真实入口、隔离方式、可执行类型及实现状态；UI AC 单列；每个 Feature 完成即入生成队列，不等待全量设计或诊断汇总
- [ ] 预检：已核对版本/设备，公共 Context/存储/必要 mock 用法有验证证据或明确缺口；首批编译/试跑不计正式业务结果
- [ ] 依赖方案：每个替换点有必要原因，被测真实链路保留；Hypium/SDK 版本已核对；共享 mock 配置由 executor 单点合并，运行组冲突已处理
- [ ] 第二步后：每 Feature 的 `it()` ID 集合等于生成记录中 `generated` 的 ID 集合；设计行数 = 已生成 + no_entry + needs_review，UI 另列；无占位断言；统一注册全部实际测试文件
- [ ] 第三步后：双 HAP 编译通过，设备已连接，报告基于真实运行日志；`spec/verify/ut/round-0/ut/` 已就位 + `_state.yaml.current_round=0`
- [ ] 修复阶段最多 8 路 `arkts-ut-fixer`：Android 行为证据明确；生产/测试/设计文件所有权互斥；必要生产接线、测试和记录同步已完成并通过独立复核，失效 `no_entry/UNREACHABLE` 已更新；按依赖批次编译，本轮处理编译返工，最终质量/完整编译通过后提交并全量复测
- [ ] **Fix-loop 退出后**：`spec/verify/ut/round-{final}/final-summary.md` 含 PASS / CONVERGED / FAIL 结论 + 每轮原始通过率、设计验证比例与 AC 完成比例演进表 + 端到端对比（round-0 → round-final）
