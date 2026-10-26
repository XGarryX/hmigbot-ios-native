---
name: ios-source-analysis
description: "iOS→HarmonyOS 迁移源分析的统一入口与编排器：组织工程（ios-project-inspector）、UI（ios-ui-analyzer）、功能（ios-feature-analyzer）、API（ios-api-inventory）四类分析，把 Swift/Objective-C/SwiftUI/UIKit/Interface Builder 的真实证据并入 ios-facts/ios-semantics/ios-coverage，经 source-check 门禁收口后交给 a2h-spec。当用户说“分析这个 iOS 项目”“理解这个 iOS 源码”“整理 iOS 源事实”或 a2h-spec 的源分析阶段时使用。不是 iOS 应用生成器——不要用于：生成审查 baseline 后的计划（用 a2h-plan）、写鸿蒙生产代码（用 a2h-execute）、资源转换（用 ios-resources-convert）。"
metadata:
  type: orchestrator
  domain: migration
  tags:
  - ios
  - source-analysis
  - evidence
  - orchestration
---

> **调用关系**：本 skill 是四类源分析的**统一入口 + 编排器**，自己不解析源码成业务节点——四类分析由四个 skill 承担（工程=ios-project-inspector、UI=ios-ui-analyzer、功能=ios-feature-analyzer、API=ios-api-inventory），本 skill 只做：①确定性机器事实基线 ②按类别派发(或顺序执行) ③合并证据与归属核对 ④门禁收口。若宿主支持 subagent，可把四类分析作为子代理派发；此时一律 `fork_turns:"none"`（任务书自足，写清源锚点、scope 与输出契约），并遵守 **Join 协议（收口五条款）**：
> ① **循环 wait**：完成的唯一合法信号是 `agent_status=completed`，绝不是产物文件存在（文件会中途落盘，读半截=事故）；② **死句柄与验收**：连续 3 次超时后 `list` 核对，completed≠验收通过，join 点跑本 skill 门禁验产物；③ **收口锚点**：最终报告前必须收口全部句柄；④ **放行≠遗弃**：非阻塞放行只推迟收口，不豁免；⑤ **fire-and-forget** 仅正文显式声明的派发免收口。
> **派发纪律**：`task_name` 唯一（带 scope/id 后缀）；派发前写清预期产物清单给 join 门对账；**谁派谁收**（sub-agent 不能嵌套外派后退出）；契约产物必须出自承担任务的子代理，禁止派发方代写占位产物让 gate 转绿。
>
> 路径约定：`$IOS_SRC` 从 `<target>/.migbot/config.json` 的 `ios` 字段读取（缺配置文件 → 先执行 a2h-init）；`<runtime>` = 本包 runtime（`scripts/a2h_ios.py` 所在根）。产物一律落 `<target>/spec/`（baseline/ref/reports/.a2h），**禁落会话临时目录**。机器信号与账本由随包命令单写，主会话/作者禁手改。

# ios-source-analysis — iOS 源仓理解与证据收口（统一入口）

## 0. 定位与纪律

- **前置**：`<target>/.migbot/config.json` 存在且 `source_platform=ios`；首次由 `source-analysis` 自动完成 harness-init、索引与适用证据编排；已规划项目走受审刷新流程。读写机器事实、审阅外部资料都随本 skill 的命令执行。**源不可读是阻塞**，不以文件夹名或文件数量补造行为。
- **输入**：iOS 源码（Xcode 工程 / SwiftPM / 混合 Swift+ObjC + SwiftUI/UIKit/IB）+ 用户预知（既有决策、平台侧分工）+ `<target>`。源工程与目标工程必须分离。
- **输出**：机器事实 `spec/baseline/{ios-source-index,ios-facts,ios-obligations}.json`、语义 `spec/baseline/ios-semantics.json`、覆盖 `spec/baseline/ios-coverage.json`、归属 `spec/ref/ios-source-disposition.json`、四个分析 skill 的 `spec/ref/*.md` 事实（ios-project.md / ios-ui-facts.md / ios-feature-facts.md / api-inventory）。**契约定稿与计划 IR 归 a2h-plan**，本 skill 不请求审批。
- **唯一交互点**：无。机械检查由 exit code 判定（0=PASS，非 0=FAIL）；不经猜测填表。
- **第一条可见输出必须是一行阶段计划**（机器事实基线 → 工程 → UI → 功能 → API → 合并归属 → 门禁），然后才执行 §1。
- **编排器边界（红线）**：本 skill 不解析源码成业务节点、不写语义结论，四类分析才是唯一事实作者；本 skill 只做基线/派发/合并/门禁。发现事实缺口时派对应 skill 补，**不替子代理代写事实**（代写会让 gate 转绿，绿账不对应真产物）。

### 无人值守处置阶梯（每道门禁 FAIL 一律套用）

> FAIL → 按命令 `retry_hint`/错误原文派修复并重跑同一命令，**最多 2 轮**；仍不过或无可执行修复时保留失败、修复记录与恢复条件，依赖失败输入的部分保持 **blocked**；独立分析可继续。静态门（facts/语义/溯源）与源合同必须重跑PASS，重试次数不能豁免；设备/账号缺失只保留未执行，不升级为成功。新产品取舍按当前授权或明确产品决策处理，模型不得自行批准替代行为。

## 1. 机器事实基线（确定性入口，先跑）

| # | 命令 | 产物 | exit / 处置 |
|---|---|---|---|
| 1.1 | `python <runtime>/scripts/a2h_ios.py source-analysis --project <target> --plan-only` | 只读决策计划：宿主、工程、范围、证据与缺失输入 | 歧义必须根据实际工程/既定决策补足，不猜产品范围 |
| 1.2 | `python <runtime>/scripts/a2h_ios.py source-analysis --project <target>` | 自动选择官方技能/MCP、原生采集或当前冻结回放、SwiftSyntax、构建配置、Clang、条件编译、IB/资源、本地化、facts、literals、expertise-plan 及待审规格 | 逐步进度输出到 stderr；失败收据保留；已有计划和旧源索引拒绝修改 |
| 1.3 | 读取 `spec/reports/derived/source-analysis.json`、`spec/ref/analysis-runs/*/plan.json` 与 `progress.json` | 决策理由、当前步骤、总数、处理/失败/阻塞、原命令和产物 | unavailable 代表缺失证据，不是对应能力通过 |
| 1.4 | `python <runtime>/scripts/a2h_ios.py facts-view --project <target> --scope {project,ui,feature,api}`（四类各跑） | 四类机器信号 | 对应作者补充源语义；视图不批准语义 |
| 1.5 | 按 `ios-expertise-plan.json` 实际读取当前官方资源，沿源码形成观察，再用 expertise-review 记录 | 真实源锚点、固定资源摘要和观察 | 官方资源不足的主题显式使用第三方备用；审阅仍必须完成 |
| 1.6 | 显式需要底层重采时使用 facts/providers、manifest-evaluate、conditional-capture 或 mcp-query | 保留既有低层能力及配置入口 | 普通流程使用 1.2 自动编排；低层调用不能代替完整收口 |

默认配置为 `spec/ref/ios-analysis-config.json`，支持 auto/native/replay/static、已确认的 selection、证据路径及 MCP 配置；完整字段和自动选择规则见 [自动编排协议](references/auto-orchestration.md)。不得为通过门禁随意改成 static。远程控制设备类能力排除在默认调用范围；其他官方能力逐项说明来源、用途、读写范围和实际结果。

### 单写者分区（违者 PROCESS_VIOLATION）

| 文件 | 唯一写者 | 内容 |
|---|---|---|
| `spec/baseline/ios-source-index.json` | source-index 命令 | 文件快照/索引 |
| `spec/baseline/ios-facts.json` + `ios-obligations.json` | facts 命令 | 机器事实/义务 |
| `spec/ref/ios-*-signals.json` | facts-view 命令 | 四类机器信号 |
| `spec/baseline/ios-semantics.json` + `ios-coverage.json` | 各分析 skill 作者（唯一 owner） | 语义/覆盖 |
| `spec/.a2h/open-findings.json` | 产生该 finding 的检查 | 未关闭发现 |

- **工具与来源分级（红线）**：本包四类分析 skill 是 HMigBot-iOS 自编分析规程；Apple 官方文档用于校核语义。SwiftSyntax 是官方语法库、本包 provider 是自编适配器（不是 Apple skill）；**Clang AST 与 SourceKit-LSP 的输出不能冒充运行行为**。没有连接时走文件分析，状态记 `unavailable`，**不能伪造官方执行**。详见 `references/apple-capabilities.md`。
- **harness v2 协议**：本 skill 先加载 `references/harness-v2.md`（决定输入、机器门禁与状态写者）。事实/义务/计划/回执由随包命令检查；本正文的分析责任继续适用，v2 协议决定机器产物与状态，旧版 source-check 不能代替新版门禁。

## 2. 四类分析派发（本 skill 只编排不解析）

| 技能 | 事实主责 | 不越权决定 |
|---|---|---|
| ios-project-inspector | 编译单元、语言、依赖、目标入口与条件 | 目标架构和替代 SDK |
| ios-ui-analyzer | SwiftUI/UIKit/IB 结构、状态、布局、交互、导航 | 业务计算规则 |
| ios-feature-analyzer | 行为链、数据变换、错误、生命周期与验收依据 | 未经授权的平台差异 |
| ios-api-inventory | 外部服务、系统能力、协议、权限、三方依赖 | 仅凭同名 API 宣告等价 |

1. **工程**：识别 workspace、project、targets、schemes、SwiftPM、本地包、Pods、二进制 framework、构建条件与 app/extension 边界。没有 Xcode 时静态读文件，**不能声称已解析有效 build settings**；构建成员标 `static-inferred`，绝不改标 compiler binding。**不以 Swift 文件扩展名推定 SwiftUI，不把 Objective-C 当另一种 UI 框架**。
2. **UI**：按实际框架提取视图组合、状态/事件与导航。无可视主界面的 target 也记录入口与平台行为，不能凭没有页面宣告无需迁移。
3. **功能**：沿用户动作、生命周期与后台入口追至可观察效果，覆盖成功、错误、取消、重入、权限拒绝、持久化恢复等源码存在的分支。
4. **API**：补全服务、存储、系统框架、权限与三方接缝，与 UI/功能事实去重；平台能力无法等价时交 decision-ledger。

### 2.1 分派协议（四类分析作为子代理时的契约）

本 skill 是唯一收口方：四类分析可以由主会话**顺序执行**（无 subagent 环境，本 skill 逐一调用）或**并行派发**（有 subagent 环境）。无论哪种，每条派发都满足：

| 项 | 契约 |
|---|---|
| `task_name` | 唯一，带 scope 后缀（`ios-ui-analyzer-<scope>`、`ios-feature-analyzer-<scope>`…）；重派加 `-r<N>` |
| `fork_turns` | 一律 `none`（任务书自足：scope、源锚点、目标产物路径全写清） |
| 预期产物清单 | 派发前写入 join 门对账（`spec/ref/ios-project.md` / `ios-ui-facts.md` / `ios-feature-facts.md` / `api-inventory` 各自契约文件） |
| 输出契约 | 每个 skill 只写自己的 `spec/ref/*` 事实 + `ios-semantics.json`/`ios-coverage.json` 中**派发时划定的 page/feature 范围**（唯一 owner） |
| 收口 | 谁派谁收；完成态以 `agent_status=completed` 为准，join 点重跑本 skill 门禁验产物 |

**四类分析的派发契约（每类一条，派发前写死）**：

| 分析类 | 输入 scope | 契约产物（写入 join 门对账） | 唯一 owner 范围 |
|---|---|---|---|
| ios-project-inspector | workspace/project/targets/SwiftPM/Pods/conditions | `spec/ref/ios-project.md` | 工程事实 |
| ios-ui-analyzer | 计划划定的 page/screen 范围 | `spec/ref/ios-ui-facts.md` + `ios-semantics.json` 对应 page 段 | 划定的 page |
| ios-feature-analyzer | 计划划定的 feature 范围 | `spec/ref/ios-feature-facts.md` + `ios-semantics.json` 对应 feature 段 | 划定的 feature |
| ios-api-inventory | 全仓 API/协议/权限/三方依赖 | `spec/ref/ios-api-facts.md` + api 信号 | API 事实 |

- **无 subagent 环境（顺序执行）**：本 skill 按 工程 → UI → 功能 → API 顺序逐一调用四个 skill，每个返回后核对契约产物在预期路径且**非空壳**（有 fact 条目与 source_anchor/fact_id，不是“已处理”覆盖），再进下一个；顺序执行的“收口”就是逐一核对契约产物，跳过 order 靠本 skill 的序列约束兜底。

- **并行边界**：四类分析读共享源、写**不同归属范围**的事实；工程/API 写 project/api 信号与 ref 事实，UI/功能写 ui/feature 事实与 `ios-semantics`/`ios-coverage` 各自划定的 page/feature 段。并行前先做**写盘交集分析**：`ios-semantics.json`/`ios-coverage.json` 由各 owner 按“计划划定的 page/feature 范围”分区写，主会话在合并时核对无跨 owner 覆盖；谁写哪段在派发前写死。
- **责任不越权**：工程分析不改 UI 语义、UI 分析不定业务计算规则、功能分析不判平台差异、API 分析不因同名 API 宣告等价。越权内容拆回对应 skill 处理，本 skill 不替子代理补事实。

### 2.2 完成判定与对账（join 门）

每个分析 skill 完成后，join 点不做“文件存在”判定，而是：

1. `agent_status=completed`（派发）或该 skill 显式返回（顺序）；
2. 契约产物在预期路径且**非空壳**（有 fact 条目、有 source_anchor/fact_id，不是“已处理”覆盖）；
3. 对应 `facts-view --scope <x>` 信号补齐（§1.4 任一非 0 的 scope 重跑）；
4. 越权/冲突内容已回本 skill 或拆回对应分析类。

> completed ≠ 验收通过；join 门只判定“到了 join 点该验什么”，验收在 §6 门禁。

## 3. 源语义（iOS 语义，逐 framework 建模）

- 先读 `references/source-semantics.md` 与 `references/native-facts.md`。语言与 UI 框架分开建模：Swift/ObjC/ObjC++/C/C++ 是语言；SwiftUI/UIKit/IB/引擎承载是界面形态。首次快照（Index）只是范围与线索。
- 逐 page/feature 维护 `spec/baseline/ios-semantics.json` v2：`known` 必须是对象 value + 当前机器 `fact_ids` + 落于事实片段内的证据；`unknown` 必须带原因并阻断受影响实现；`not_applicable` 只有完整调用链审阅后才可记录具体理由。**不用“已处理”“无特殊情况”覆盖全部维度**。
- SwiftUI 的 body/modifier/state/binding/identity/environment/task/导航、UIKit 的 controller/view/constraint/outlet/action/delegate/生命周期分别保留；**IB 与程序化改动共同决定运行布局**。宏/二进制/动态配置无法确认时说明所需额外证据，不伪造解析结果。
- Preview/mock 数据与实际入口分开；**没有 iPhone 录制不生成运行观察结论**（runtime=not_run 合法）。已有截图只能证明该场景下的显示，不能推导全部导航/状态。

### 3.1 建模维度（逐 framework，不混谈）

| 承载 | 保留维度 |
|---|---|
| SwiftUI | body 组合、modifier 有序链、@State/@Binding/StateObject/ObservedObject、identity/ForEach id、Environment、task(id:)、NavigationStack/sheet 呈现 |
| UIKit | controller containment、约束（relation/priority/intrinsic size/hugging/compression）、outlet/action、delegate/data source、生命周期、Scene |
| IB（Storyboard/XIB） | 连接 ID、segue、约束、自定义运行时属性——与程序化改动共同决定运行布局 |
| 引擎/自绘 | Metal/SceneKit/SpriteKit/Core Graphics/游戏循环 → 标注界外，不自造行为；WKWebView/相机/视频/地图叠层归 UI 分析 |
| ObjC/ObjC++/C/C++ | 语言事实与 Swift 桥接分开；协议/分类/消息语义分别保留 |

## 4. 外部资料与 MCP 证据（可选项）

1. 按 §1.5 清单实际读取上游资料，沿源实现形成观察：`python <runtime>/scripts/a2h_ios.py expertise-review --project <target> --input <review.json>`。resources 摘要必须与清单一致；空壳“已处理”不代替分析。
2. 需要符号证据时 `python <runtime>/scripts/a2h_ios.py mcp-query --project <target> --server <server.json> --request <query.json>`（示例见 `assets/mcp-server.example.json` / `assets/mcp-query.example.json`）。只有固定源读工具白名单可调用；失败/超时写 failure.json，绝不写成功索引。返回标 `resolution=tool_response`、`build_context=unverified`，不自动升级为 compiler_binding/runtime。
3. 记录证据工具来源、版本、实际是否执行：`spec/ref/ios-analysis-provenance.json`。源码、Apple 文档、运行 trace 三源分列；只有实际加载才标 `used`，未接入标 `unavailable`/`not_loaded`，**不把自编规程冠为官方**。

## 5. 合并、归属与恢复（收口协议）

1. 合并四类证据，核对每个业务源文件归属 page/feature；不在迁移范围内的文件写 `spec/ref/ios-source-disposition.json`，逐文件说明依赖、测试或不适用理由。**不用目录白名单把未理解业务一笔略过**。
2. 每个 page/feature 有一个事实作者；可按 target/module 分工，但派发前写清文件所有权。身份信号（`.id`/ForEach）判据候选为 unit/contract/ui，缺失/歧义保守处理，**不根据目录或 import 猜语义**。
3. 源码变化时按快照差异重读受影响调用链，再更新相关事实；保留旧版本与变更原因。**只刷新 hash 不能关闭过期 source finding**；路径歧义必须回真实目录消歧。复跑产生该 finding 的检查才能关闭。
4. 已审 Spec 变更与旧在途死锁时：先停止 worker，固定 review v1，仅用 harness-v2 的 `recover-blocked` 显式失败终止，再正常 replan；不得回退 Spec、手写三账本或把 blocked 伪装 PASS。

### 5.1 合并与归属核对步骤（逐条，不跳）

1. **收口前置**：四类分析全部 `completed`（或顺序执行全部返回）后，本 skill 先跑 `facts-view` 四类各一次确认信号补齐，再进入合并。
2. **归属核对**：以 `ios-source-index.json` 的文件快照为主键，逐源文件核对归属 page/feature；四类分析的 ref 事实交叉引用同一源文件时，若归属冲突，回真实目录消歧，**不按目录名/import 猜语义**。
3. **去重与单一 owner**：同一维度跨两 skill 重复出现时（如 UI 与功能都提同一状态），用 ID 引用共享事实，不准重复登记两份 owner——单一 owner 由计划划定，合并时核对无跨 owner 覆盖。
4. **语义闭合**：`ios-semantics.json` 每个 page/feature 的 `known` 落证据、`unknown` 带原因、`not_applicable` 附理由；`ios-coverage.json` 覆盖源文件与语义维度，缺处标 unknown，不标“已处理”覆盖。
5. **归属账本**：未进入迁移范围的源文件逐条写入 `ios-source-disposition.json`（依赖/测试/不适用），不用白名单略过。

- **归属核对红线（三签缺一不可）**：源签名 / 快照 hash / 事实片段证据。只有机器 hash 不算理解业务、只有人工结论不算机器可核验；合并结果必须能被 `source-check --harness` 复算，**不靠“我说归属就是归属”**。

## 6. 门禁与交接（收口完整步骤）

- **门禁命令**：`python <runtime>/scripts/a2h_ios.py source-check --harness --project <target>`，exit 0 才交接（含 external-expertise 门禁与溯源检查；`--report-only` 只诊断不更新 findings）。FAIL 按 §0 处置阶梯最多修 2 轮；结构 PASS 不能代替源语义审阅。
- **外部证据门禁（红线）**：`source-check --harness` 含 external-expertise 门禁（只看已加载并留痕的外部资料）与溯源检查（provenance 三源分列、工具版本、是否实际执行）。引用 Apple 文档却未 `used`、把自编规程冠为官方、把 `tool_response` 升级为 compiler_binding/runtime，都会 FAIL。详见 `references/apple-capabilities.md` 与 §4。
- **门禁收口顺序**：
  1. 四类派发全部收口（Join 五条款，连续超时 3 次后 `list` 核对，completed≠通过）；
  2. 合并与归属核对完成（§5.1 五步）、`source-disposition.json` 落全；
  3. 跑 `source-check --harness`；FAIL 读错误原文/`retry_hint` 修后重跑（≤2 轮），静态门照修到 PASS；
  4. 规范独立复核：提交前按 `../a2h-spec/references/spec-content-review.md` 完成 finding→原 owner 返修→独立复查（共享事实单一 owner、ID 引用，避免重复登记）；
  5. exit 0（`source-check --harness` 绿）即本阶段收口。
- 移交产物：`spec/baseline/{ios-source-index,ios-facts,ios-obligations,ios-semantics,ios-coverage}.json`、`spec/ref/{ios-project,ios-ui-facts,ios-feature-facts,ios-api-facts,ios-source-disposition}` 相关文件、未关闭 findings。随后交 a2h-spec（同会话可直接续跑 Phase B/Phase C）。
- 本 skill 无独立 stage 水位（无 mark-stage）；`source-check --harness` 绿即源分析阶段收口。

### 6.1 移交产物清单（文件名级，交接前逐项核对）

| 产物 | 规范来源 |
|---|---|
| `spec/baseline/ios-source-index.json` | source-index 命令（文件快照/索引） |
| `spec/baseline/ios-facts.json` + `ios-obligations.json` | facts 命令 |
| `spec/baseline/ios-semantics.json` + `ios-coverage.json` | 各分析 skill 作者（分区 owner） |
| `spec/ref/ios-source-disposition.json` | 合并归属账本 |
| `spec/ref/ios-project.md` / `ios-ui-facts.md` / `ios-feature-facts.md` / `ios-api-facts.md` | 四类分析各自产物 |
| `spec/ref/ios-*-signals.json` | facts-view 四类信号 |
| `spec/ref/ios-analysis-provenance.json` | 证据溯源 |
| `spec/.a2h/open-findings.json` | 未关闭发现 |

- 上述文件任一缺失/空壳即不算完成交接；交接后进入 a2h-spec。

## 7. 读取时机（references）

| 触发时机 | 必读文件 |
|---|---|
| 执行前；机器产物/状态写者存疑 | references/harness-v2.md |
| 源事实字段、identity/state/维度规则 | references/native-facts.md |
| SwiftUI/UIKit/ObjC/桥接语义读法 | references/source-semantics.md |
| expertise-plan/review、MCP 查询边界 | references/external-expertise.md + assets/mcp-{server,query}.example.json |
| Apple skill/MCP/宿主能力三态与 provenance | references/apple-capabilities.md |
| 运行指定 provider（SwiftSyntax/Clang/IB/资源） | assets/provider-plan.json |
| Package.swift 未求值 / 产品成员证据 | references/source-input-evidence.md |
| 产物 profile/格式/作者/消费者 | ../a2h-spec/references/artifact-contracts.md |
| 独立跨文档复核 | ../a2h-spec/references/spec-content-review.md |
| 异步/取消动作契约 | ../a2h-spec/references/action-contracts.md |
| 四类分析各自分派与产物契约 | 各分析 skill 的 SKILL.md（ios-project-inspector / ios-ui-analyzer / ios-feature-analyzer / ios-api-inventory） |

## 8. 收尾：上报本阶段用量

```bash
python <runtime>/scripts/a2h_ios.py usage-finish --project <target> --run-id <run-id>   # 若存在；否则等价物
```

最后一步执行、**忽略退出码、绝不阻断流水线**；token 用量由宿主生命周期采集，本步不采集。


补充业务/设计参考文档时，可按 [Garry 业务设计提纲](references/garry-business-design-outline.md) 检查遗漏维度；本技能的事实、章节、源责任与正式规格合同继续优先。
