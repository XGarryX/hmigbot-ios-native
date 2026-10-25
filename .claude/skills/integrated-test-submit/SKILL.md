---
name: integrated-test-submit
description: 交互式引导生成 migbot 三仓 merge 验证的 PR 描述（multica 变量块）——通过分步提问收集 Profile、Test App、迁移阶段、运行时等变量，产出可直接复制、且能零告警通过 GitHub Action 机器校验契约的 PR message。当用户想"生成 PR 的 multica 变量块""为 merge 验证写 PR 描述""发起一次迁移验证""提测 DiceRoller/AIPPT 迁移"，或提到 Multica 提交、变量块、merge 验证、PR comment 规范等时使用本 skill，即使用户没有明确说"生成 message"。
---

# integrated-test-submit：PR → 真实端到端迁移测试的 message 生成器

把 `docs/Multica_Submission_Spec.md`（下称 Spec）定义的 PR 用户输入变量，通过交互式提问收集齐，生成一份能被 observability-squad 各 Agent 确定性解析、并通过 Spec §3 机器校验契约（GitHub Action）的 PR 描述。

**本 skill 仅支持 merge 验证 PR 这一种提交模式**。用户想要缺陷修复 Issue、无 PR 手动验证或 /multica 评论命令时，告知这些模式已归档（`docs/Multica_Submission_Spec_Archive.md`）、当前不再由本 skill 生成。

## 权威来源

开始前先读取仓库中的 `docs/Multica_Submission_Spec.md`，以其中的变量定义、默认值总表（§2.8）、校验规则为准——Spec 会演进，本 skill 内嵌的速览可能滞后。读不到 Spec 时使用 [references/templates.md](references/templates.md) 末尾的快照，并向用户说明可能过期。

## 核心原则

1. **先提取，后提问**。用户的请求里往往已带了一半答案（App 名、仓库、模型、"merge 场景"等），已明确的信息直接采用，不重复问。
2. **分批提问，逐组展开**。使用交互式提问工具（AskUserQuestion），每批不超过 4 题；**每个语义组单独成题并把默认值写进选项**——用户未必知道默认是什么，不得用一道"其余全部用默认？"总开关概括多个分组。默认选项标注"(推荐)"（Test App 例外：按代码量级陈列、不设推荐）。
3. **提问极简，输出全量（路径除外）**。默认值只用于减少提问——用户没被问到/没改的项自动取默认；生成的 message 渲染**全量显式变量块**：所有生效值（含默认值）逐项列出。**唯一例外是路径类字段**（`local_workspace` / `test_app.local_path` / `migration.decisions_path`）：不再渲染，由 Instruction 路径规则在执行侧自动派生；仅当用户显式要求覆盖路径时才渲染，块内值优先。理由：Squad Agent 以 message 正文为唯一确定性输入，默认值解析逻辑只存在于 Spec 文档而不在 Instruction 中，省略字段等于让 Agent 猜；全量块使 message 自包含且便于提交前人工核对。对来自默认值的行加行内注释标注（如 `# 默认`），用户指定的行标注来源。
4. **校验后生成**。收集完成后按下方校验规则检查，违规时向用户解释原因并给出修正建议，不生成明知非法的 message。
5. **复合自由文本回答要归置**。用户经常在一个回答里带出多重诉求（如"不挂起等人，但要输出到报告"）。逐项拆解：能映射到变量的落为变量取值；已由 Instruction 既有机制覆盖的（如问答强制记入 migration_interactions）明确告知"无需变量、机制已保证"；两者都不是的，向用户确认是否属于新需求（可能要改 Spec 而非硬造字段）。

## Step 1：问题流

**每个语义组都要展开提问，并把默认值作为明确选项呈现**——用户未必知道默认是什么，禁止用一道"其余变量是否全部用默认？"的总开关问题概括多个分组。已从用户消息中明确的项跳过对应问题。固定两批（每批 ≤4 题）：

**第一批**：

1. **触发仓库**：migbot-server / hmigbot / migbot-runtime-src / hmigbot-CodeX / migbot-codex-runtime-src。触发仓为 migbot-server 时在第二批追加 `validation.profile` 问题（缺省 migbot_codex，由生成器显式渲染标识）；其他仓由仓名强制确定，不问 Profile。
2. **Test App**（**不设推荐项**，按代码量级陈列供用户按测试强度选择；注册表详情见 references/templates.md）：

   | App | 代码量级 | 简称 | 呈现方式 |
   | --- | --- | --- | --- |
   | DiceRoller | <1k 行 | dice | 选项 1 |
   | AIPPT | ~2 万行 | aippt | 选项 2 |
   | AntennaPod | ~10 万行 | antennapod | 选项 3 |
   | Meshtastic | ~20 万行 | mesh | 选项 4 |
   | Jetsnack | ~6k 行 | jetsnack | **不列为选项**，Other 自填触达 |

   提问时列前四个 App 为选项；末位选项描述中注明"Jetsnack（~6k 行）及表外 App 请通过 Other 备注指定"。用户经 Other 填 Jetsnack 时同样命中注册表。**注册表内五个 App 一律不追问 url**——直接渲染注册表固定值（用户可在解析预告中核对）；**仅表外 App** 才请用户提供 https 链接。iOS 工程路径不渲染，由路径规则从 url 派生。
3. **验证平台 platform**（三个平级选项，全部列出）：
   - `mac`（默认，标注推荐）：Mac 单平台执行迁移与 Session 捕获；
   - `windows`：Windows 单平台执行；路径由 Windows 执行机本机配置 + 路径规则派生，PR 无需携带；提醒确保该执行机本机配置就绪；
   - `dual`：**Mac 与 Windows 两台执行机均各跑一轮完整迁移**——具体派发由下游 Multica Agent（Lead 双平台调度）解读；Windows blocked 不阻塞 Mac 结果与 Session 上传；两台执行机各按自身本机配置派生路径。

   `test_date` 并入本题说明：默认生成日 MMDD，需自定义时在备注写明（不单独设题）。
**第二批**：

4. **迁移阶段 stages**：全流水线（默认）/ 环境冒烟 `[a2h-init, a2h-build]` / 不含复盘 `[init…verify]` / 自定义列表。**凡包含 `a2h-verify` 的选项，描述中必须注明：需要执行机提前开启 iOS 模拟器与 HarmonyOS 模拟器（行为核验依赖双端运行时）**。
5. **问答策略与决策集**：`blocked` + 默认目录 `decision/<app_name>.md`（默认）/ `wait_human` 挂起等人 / 自定义 decisions_path。
6. **运行时**：`codex_cli + gpt-5.6-sol + high`（默认：CLI 无人值守直启）/ `codex_app` 桌面版优先自动降级 / 换模型或力度（备注说明）。
7. **工具 Release**：最新 published 稳定 Release（默认）/ 指定 `release_tag`（migbot_version 的权威来源，v8.4 Release Gate）。

**条件第三批（自动评测，单题）**——**问不问只由"该 App 有无评测包注册"决定**（当前 **AntennaPod / AIPPT**；正本为 migbot-utils `AutoEval/gt_eval_registry.json`）：

- **有包** → 提下面第 8 题；
- **无包**（DiceRoller / Meshtastic / Jetsnack 等）→ **不出本题**，直接渲染 `gt_eval: "off"`。用户主动要求评测时**也不改为提问**，而是说明："该 App 尚无评测包，执行侧会判 `not_applicable` 跳过（不阻断流程），本轮渲染 `off`；需要评测请先为该 App 提供评测 kit 与注册表条目（migbot-utils `AutoEval/`）。"——**不生成明知触发 MC-18 warning 的 message**（那会违反本 skill 的零告警契约）。

8. **自动评测 gt_eval**（迁移成功后由评测 Agent 对产物做 GT 功能完备度评测，与 Review 并行、纯 advisory 不影响验证结论）：
   - `off`（默认，标注推荐）：本轮不评测；
   - `smoke`：最小子集验环境与链路（AIPPT 约 5 分钟；AntennaPod H4 单批约 40 分钟）；
   - `full`：全量评测（AIPPT 约 20 分钟；**AntennaPod 两包 595 条约 20 小时且鸿蒙模拟器全程独占**——选项描述必须写明时长）。

## Step 2：校验规则（生成前逐条过）

生成的 message 必须能**零 error、零 warning** 通过 Spec §3 机器校验契约（MC-01 ~ MC-19，GitHub Action 同规则执行）；以下为交互期就要拦住的重点：

1. **Profile 配对**（MC-05）：hmigbot ↔ migbot-runtime-src（cc）、hmigbot-CodeX ↔ migbot-codex-runtime-src（codex）；触发仓与 profile、profile 与 launch_mode 出现禁配组合时拒绝生成并解释。
2. **app_name 规范**：全小写、无分隔符、尽量短。已知别名：DiceRoller→dice、AIPPT→aippt。不合规时给出建议值请用户确认。
3. **migration_stages**：成员应属于已知流水线 skill（a2h-init/a2h-build/a2h-spec/a2h-plan/a2h-execute/a2h-verify/a2h-retrospect 及工具仓文档声明的其他 skill）；出现未知 stage 时提醒"执行侧无法识别会导致 blocked"，允许用户坚持。
4. **枚举拼写**：runtime.effort 禁止 `extraHigh` 拼写（合法如 `high` / `xhigh`，以 CLI 枚举为准）；unanswered_policy 为 blocked/wait_human；platform 为 mac/windows/dual。
5. **不可指定项拦截**：用户试图指定候选 commit、三仓 SHA、工具安装来源、validation_run_id 时，解释这些由 Plan/Lead 自动解析（Spec §2.9），不写入变量块。用户想指定"工具版本号"时引导到 `release_tag`（migbot_version 权威 = 工具仓 GitHub Release Tag，v8.4 门禁）；`test_date` 只是 DevEco 命名标签。
6. **禁跨 Runtime**：migbot_codex 只允许 codex_app/codex_cli，migbot 只允许 Claude Code 方式（v8.4 Runtime Consistency Gate）；用户要求跨 Runtime 组合时解释并拒绝。
7. **Mock 语义**：v8.4 下正文出现任何真实 Migbot 标识即禁 Mock；生成的导语必须包含"真实迁移（非 Mock）"声明，用户明确要 Mock 演练时提醒其与真实标识互斥（须走独立的 mock 任务，不用本 skill 模板）。
8. **URL 格式**：test_app.url 必须是 `https://github.com/<owner>/<repo>` 或 `.../tree/<ref>/<subdir>`；子项目 App 必须用 tree 形式。
9. **路径变量**：路径类字段默认不渲染；用户显式覆盖时才写入块（migration.decisions_path / test_app.local_path / local_workspace），格式须为执行机本地路径（~ 展开在执行机发生），不校验本机存在性。
10. **自动评测**（MC-17/18）：`gt_eval` 枚举限 off/smoke/full。**无评测包的 App 一律渲染 `"off"`**——硬规则，不因用户坚持而破例（生成带 MC-18 warning 的 message 违反零告警契约）；向用户解释执行侧行为（判 `not_applicable` 跳过、**不阻断流程**）与开通路径（提供评测 kit + 注册表条目）。评测器 Runtime/模型、评测包版本、档位→批次映射均不可经 PR 指定（执行侧资产），用户试图指定时按不可指定项处理。

## Step 3：生成输出

读取 [references/templates.md](references/templates.md)，按类型选模板填充：

- 输出物 = **一段可直接复制的完整 message**（Issue 正文 / PR 描述 / 评论命令），放在 fenced code block 中。
- **导语行默认渲染（推荐非强制）**：yaml 块上方渲染 2-3 行自然语言意图声明（Profile 具体标识的仓库对名、"真实迁移非 Mock"、Runtime），使用 Instruction v8.4 语义分流认得的词汇。v8.4 下块内标识已足以正确判定 Profile 与 Mock 禁令，导语只是兜底（块被渲染破坏、server 手写漏块）与人类摘要；用户要求精简 message 时可省略，省略不影响正确运行。渲染时导语与块内容必须一致。
- 变量块遵循全量显式原则（见核心原则 3，路径类字段除外），块首行固定 `# multica`；必含 `deveco_project` 渲染组（派生的 project_name、`sdk`（缺省 21，用户点名换 SDK 时覆盖）与 created_by）。工程创建位置、iOS 工程路径、决策集路径由 Instruction 路径规则派生，不进块。
- **所有渲染值必须是具体值**：`test_date` 落死为生成日 MMDD、`project_name` 渲染实名（如 `dice_v728_codex`）——禁止 `{MMDD}` 等占位符或"自动取触发日"机制，Agent 侧没有展开逻辑。生成日与 merge 日可能不同，向用户说明即可。
- message 之后附一个简短的"解析预告"：列出 Squad 将如何解析这份提交（profile 解析结果、DevEco 工程名、将执行的 stage 序列、migbot_version 的 Release 来源、哪些行来自默认值），让用户提交前能核对意图——这是对 message 正确性的最后一道人工确认。
- **evaluation 组恒渲染**：变量块末尾（runtime 组之后）渲染 `evaluation:` 组，`gt_eval` 按用户选择或默认 `off`（加 `# 默认` 注释）——全量显式原则同样适用，Lead 由此判定是否在 Plan 写入 `gt_eval_plan` 授权。**值必须加引号**（`gt_eval: "off"`）：YAML 1.1 会把裸 `off` 解析成布尔 `False`，各下游解析方行为不一；引号消除歧义（校验脚本对不带引号的手写块做布尔归一兜底）。
- **模拟器提醒**：`migration.stages` 包含 `a2h-verify` 时，在解析预告末尾固定输出："本轮包含 a2h-verify——请提前在执行机开启 iOS 模拟器与 HarmonyOS 模拟器，行为核验依赖双端运行时。"
- **评测提醒**：`gt_eval ≠ off` 时，解析预告增加评测行（档位、预计时长、"与 Review 并行、advisory 不影响验证结论"），并固定输出："本轮开启自动评测——请确认执行机鸿蒙模拟器可用、签名 profile 在 14 天有效期内；full 档期间模拟器独占。"
- **标签提醒（固定输出）**：提交后必须给 PR 打 `integrated_test` 标签——它是集成测试的 opt-in 声明：无标签则格式检查跳过、（Instruction 同步后）merge 也不触发端到端测试；打了标签而缺变量块会被 MC-01 阻断，标签与变量块构成完整的参与契约。
- 主动询问是否需要顺手生成 `gh issue create` / `gh pr create` 命令（默认不生成，仅输出 message 文本）。
