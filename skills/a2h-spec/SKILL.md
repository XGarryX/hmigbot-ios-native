---
name: a2h-spec
description: "iOS→HarmonyOS 迁移第一步（Spec）：从 Swift/ObjC、SwiftUI/UIKit、Xcode/IB 源行为生成可实施 baseline——工程/UI/功能/API 四类事实、ui-manifest 与 page_* 页面规格、feature-* 功能规格、稳定 AC 与决策账本，经程序门禁（spec-check/source-check/lint_*）收口后交给 a2h-plan。当用户说“分析这个 iOS 项目”“开始迁移”“生成迁移 spec”时使用。不要用于：排期与计划 IR（用 a2h-plan）、目标代码生成（用 a2h-execute）、已有规格的增量修改（按恢复路径走增量规程）。"
metadata:
  type: pipeline
  domain: migration
  tags:
  - ios
  - spec
  - source-evidence
  layer: pipeline
---

本统一版本先读 [单一流程、环境前置与兼容范围](../a2h-run/references/unified-workflow.md)；其中明确的写入、准备时机和行为范围规则优先于下文的旧调用示例。


> **调用关系**：本 skill 主会话执行，**不直接 spawn 迁移 worker**。四类源分析由主会话按 `ios-source-analysis` 技能组织（工程=ios-project-inspector、UI=ios-ui-analyzer、功能=ios-feature-analyzer、API=ios-api-inventory）。若宿主支持 subagent，可把四类分析按 `a2h-ios-analyzer` 角色派发；此时一律 `fork_turns:"none"`（任务书自足，写清源锚点、输出契约），并遵守 Join 协议：完成的唯一合法信号是 `agent_status=completed`，绝不是产物文件存在；completed≠验收通过，join 点跑本 skill 门禁验产物；谁派谁收；最终报告前必须收口全部句柄。
>
> 路径约定：`$IOS_SRC` 从 `<target>/.migbot/config.json` 的 `ios` 字段读取（缺配置文件 → 先执行 a2h-init）；`<runtime>` = 本包 runtime（`scripts/a2h_ios.py` 所在根）。产物一律落 `<target>/spec/`（baseline/ref/reports/.a2h），**禁落会话临时目录**。本 skill 自有脚本：`scripts/lint_addenda_closure.py`、`scripts/lint_divergence.py`、`scripts/extract_literals.py`、`scripts/build_traceability_index.py`。

工具修复与项目源事实补全分别按 [结果分离规则](../a2h-run/references/tool-project-status-separation.md) 记录；库/历史范围只能经当前受审责任合同投影，不删除机器义务或把源未知改成已知。

先读取 [iOS Harness v2](../ios-source-analysis/references/harness-v2.md)，以该协议决定输入、机器门禁和状态写者。以下原领域规程继续用于规格内容、indexed 计划、接线和真实验证；不得再手工调度或写入三份控制账本。

# a2h-spec — 从 iOS 源事实生成迁移规格

## 0. 定位与纪律

- **前置**：`<target>/.migbot/config.json` 存在且 `source_platform=ios`（缺 → 先跑 a2h-init，不代跑）；spec 真正的起步门 = §1 的 `harness-init`。
- **输入**：iOS 源码（Xcode 工程 / SwiftPM / 混合 Swift+ObjC）+ 用户预知（既有决策、平台侧分工）；**源不可读是阻塞**，不以文件夹名或旧报告补造行为。
- **输出**：`spec/baseline/{feature-index,feature-base}.md`、`spec/baseline/features/FNNN-*.md`、`spec/baseline/ui-manifest.md`、`spec/baseline/ui/page_NNNN_*.md`、`spec/baseline/{ios-semantics,ios-coverage,ios-facts,ios-obligations}.json`、`spec/ref/{ios-project,module-index,ios-ui-facts,ios-feature-facts,ios-api-facts}.md`、`spec/decision-ledger.md`、套靠九件门禁产物（§6）。**契约定稿与计划 IR 归 a2h-plan**——本 skill 不请求审批。
- **唯一交互点 = Gate C**（产品选择只问具体未决点，不能用阶段名要求重复批准已授权的开发）；其余禁交互追问，机械检查由 exit code 判定（0=PASS，1=FAIL，2=用法错）。
- **第一条可见输出必须是一行阶段计划**（harness 门 → 源分析 → UI baseline → 功能 baseline → 门禁 → Gate C），然后才执行 §1。
- **恢复与已有 baseline**：先读 `spec/.a2h/open-findings.json`（findings 只能由产生它的检查重跑后关闭，不同阶段队列分开，不能把整个文件重写成空）。已有完整 baseline → 比较源版本走增量规程（a2h-incremental-migration/arkts-spec-evolver）；部分 baseline 只续缺/受影响部分，**保留稳定 page/F/AC/decision ID**。

需要依赖内部或批准替代责任投影时，先读 [源责任合同](references/source-responsibility.md)。原 facts/obligations、源 unknown 和历史 AC 必须保留；未审 payload 不能授权排除或派发。

生成baseline前读取 [产物目录](references/artifact-contracts.md) 与 [交付合同](references/spec-delivery-contract.md)：先确定profile/适用产物/唯一作者，源事实、目标设计、批准差异分段，先形成行为模型和公共目标接口，再按模板生成文档与具体AC。不要从源码信号直接套通用句式。

## 1. 基线启动（顺序执行；每步带产物与 exit code）

| # | 命令 | 产物 | 失败处置 |
|---|---|---|---|
| 1.1 | `python <runtime>/scripts/a2h_ios.py source-analysis --project <target> --plan-only` | 只读自动编排计划和确切缺失输入 | 依据工程及已确认范围补足真实歧义 |
| 1.2 | `python <runtime>/scripts/a2h_ios.py source-analysis --project <target>` | harness、索引、官方技能/MCP、适用原生/冻结证据、facts、literals、expertise-plan 与待审候选 | 查看逐步进度及失败收据；过期索引走 source-refresh，禁止删除旧证据硬建 |
| 1.3 | 读取 `spec/reports/derived/source-analysis.json` 与 `spec/ref/analysis-runs/*/{plan,progress}.json` | 决策理由、实际调用、产物、处理/失败/阻塞数 | 缺失官方证据明确降级，不能改标通过 |
| 1.4 | `python <runtime>/scripts/a2h_ios.py facts-view --project <target> --scope {project,ui,feature,api}`（四类各跑） | 四类事实视图 | 对应分析作者补事实并重跑 |
| 1.5 | 按 `ios-expertise-plan.json` 读取适用官方资源和明确的备用资料，沿源码形成观察，再用 expertise-review 记录 | 真实来源、固定摘要与源观察 | 不用“已处理”替代分析；官方资料加载不代表语义审阅完成 |

自动编排字段、选择与恢复规则见 [自动编排协议](../ios-source-analysis/references/auto-orchestration.md)。优先适用 Apple 官方技能、只读 Xcode MCP、CLI 和 Swift/Clang；各项说明来源、用途、读写范围及真实结果。远程控制设备类能力排除在默认调用范围。

- **harness v2 协议**：本 skill 先加载 `../ios-source-analysis/references/harness-v2.md`（它决定输入、机器门禁与状态写者）。事实/义务/计划/回执由随包命令检查；本正文的分析责任继续适用，v2 协议决定机器产物和状态——旧版 source-check 不能代替新版门禁。
- **MCP 证据（可选项）**：需要符号证据时 `python <runtime>/scripts/a2h_ios.py mcp-query --project <target> --server <server.json> --request <query.json>`。只有固定源读工具白名单可调用；失败/超时写 failure.json，绝不写成功索引；真实服务缺工具保留 unavailable/unknown，**禁止换假服务凑通过**。返回标记 `resolution=tool_response`、`build_context=unverified`，不自动升级为 compiler_binding/runtime。

## 2. Phase 0：工程与范围

1. 按 `ios-source-analysis` 组织四类分析（§头注），建立工程、UI、功能、API 事实。
2. 明确 app/extension 目标、scheme/configuration、依赖与混合语言边界。**文件索引不代表有效编译成员**；没有 Xcode 时保留 `static-inferred`，绝不改标 compiler binding。
3. 大工程按 target/module/feature 分片，写 `spec/ref/module-index.md` 与范围归属。共享事实只有一个作者；分片结束核对文件归属，不能靠扫描目录数量认定完备。
4. 记录证据工具来源、版本、实际是否执行：`spec/ref/ios-analysis-provenance.json`。源码、Apple 文档、运行 trace 三源分列；未接入 Apple skill/MCP 时明确 unavailable，**不能把自编规程冠为官方**。

## 3. Phase A：源事实（iOS 语义）

- 源证据 = 真实文件/符号/行号/快照。SwiftUI 的 body/modifier/state/binding/identity/environment/task/导航，UIKit 的 controller/view/constraint/outlet/action/delegate/生命周期分别保留在 `spec/baseline/ios-semantics.json` 的对应记录；**IB 与程序化改动共同决定运行布局**。
- `known` 必须有源码证据；不适用给具体理由；未知保持 `unknown` 并回流分析。宏/二进制/动态配置无法确认时说明所需额外证据，**不伪造解析结果**。
- Preview/mock 数据与实际入口分开；**没有 iPhone 录制不生成运行观察结论**（runtime=not_run，screenshot=null 合法）。

## 4. Phase B：UI baseline

1. 按真实入口发稳定 page ID，写 `ui-manifest.md`：page_id、iOS 源符号、framework、目标页、功能归属、优先级、状态、spec 路径、证据置信度。
2. 写 `ui/page_NNNN_Name.md`（模板 `templates/page-spec-template.md`）：组件层级、布局约束、具体 ArkUI 映射、资源引用；公共段落（页面结构/视觉/状态接口/交互/导航/资源/验收/目标接线责任）与 `ios` 原生语义段**完整并保留**。
3. `ui-snapshots/<page_id>/meta.json` 存 source_platform、framework、source refs、状态条件与真实截图路径（若有）。**不创建伪造布局树**；程序化 UI 按真实代码与语义树表达。
4. 状态接口写明持有者、变化来源、消费者、清理边界、已确定目标接口；**原语义与 ArkTS 决策分段，不能用目标装饰器反向修改源事实**。
5. 门禁：`python <runtime>/scripts/a2h_ios.py source-check --harness --project <target>`；UI 覆盖用 `arkts-ui-coverage-auditor`（入口/页面/交互逐项核对），出 `spec/ui-coverage-report.md`。**静态覆盖与运行验证分别记录，不许互代**。

## 5. Phase C：功能 baseline

### C1 总分结构
写 `feature-index.md`、`feature-base.md`（模板 `templates/feature-base-template.md`）、`features/FNNN-name.md`（模板 `templates/feature-spec-template.md`）。公共基础设施与领域行为分开；功能以完整行为为粒度（文件/类不是 feature 边界）。复杂状态机/协议/生命周期放 addendum，主 spec 保留稳定 AC 与 impl 指针。

### C2 源原生语义
主 YAML 用 `source_platform: ios` + `source_anchors`（每条含 role、真实 path、symbol/line）。语言/UI 框架分别声明，**不使用旧平台字段**。Swift Optional/值 vs 引用/枚举载荷/throws/actor/task、ObjC nullability/ARC/delegate/block/selector 等影响行为的语义写"iOS 源语义"，不能压成普通类图。

### C3 行为与目标契约
- 源事实写状态转移、数据变换、错误/取消、并发、持久化恢复、平台条件。
- 适用动作先由唯一 owner 定义即时效果、完成事件、最终效果与错误/取消（`references/action-contracts.md`）；页面与 AC 只引用，不各自重新解释完成时点。无适用动作给有据 N/A。
- 目标服务层写 ArkTS 接口；实现映射与状态表只在受支持目标列声明 Owner.member（源描述里出现"目标/status"等词不声明目标、不改列映射）。对接点写 `page.handler ← ViewModel/Service`，保留数据域、单位、线程、资源生命周期约束。平台能力对应哪一 Kit/API **必须查目标版本证据**；业务常量/字面量保留实际值（`literal-ledger.json`）。

### C4 AC 与差异
每条 `- [ ] F001-AC01` 后给 `源:<符号> → 标:<目标方法>`、`判:<方式> | <可观察结果>`、`真:src:<路径>:<行>`（或独立 test/trace/device）。已批准替代用 `决:<ID>` 和 `真:decision:<ID>`；**禁止以生成的目标实现作真值**。不设 AC 数量门槛，核对实际入口/分支/常量/错误/副作用覆盖。同构组可列成员，但不能因分组省略真实不同行为；删减保留 skip-list 理由。HARD-DIV 按四件套：decision ID、替代数据流、supersedes 源 AC、新差异 AC。同名 API 不等于行为等价（StoreKit、iCloud、扩展、后台逐项决定）。没有设备的 device/visual AC 仍保留该验证强度，**不能改 static 凑通过**。

### C4.1 决策账本
读取 `references/migration-decision-categories.md`，写 `spec/decision-ledger.md` 的 D0 与适用决策：已有授权直接复用；未知技术事实继续查证；**产品取舍才提出具体选择**（Gate C 用）。plan 消费同一账本。

### C5 实际生成与校验
页面/功能清单确定后，按 `references/native-authoring.md` 跑 `spec-authoring`：先生成绑定当前源与 MD 的完整填报清单，再由原作者提交事实、处置与 AC 源位置，生成校验后候选。**全部页面/功能必须一一对应，不能只写示例中的两份**。候选仍须独立复核 + §6 门禁。

## 6. 程序门禁（全部通过才进 Gate C；FAIL 按 §0 处置阶梯最多修 2 轮）

```text
python <runtime>/scripts/a2h_ios.py spec-check --project <target>
python <runtime>/scripts/a2h_ios.py source-check --harness --project <target>
python <skills>/a2h-spec/scripts/lint_addenda_closure.py --spec <target>/spec/baseline
python <skills>/a2h-spec/scripts/lint_divergence.py --spec-dir <target>/spec/baseline/features --gate
python <skills>/a2h-spec/scripts/extract_literals.py --spec-dir <target>/spec/baseline --out <target>/spec/baseline/literal-ledger.json
python <skills>/a2h-spec/scripts/build_traceability_index.py --project-root <target>
```

- 审阅/升级诊断可用 `source-check --harness --report-only`（不更新 findings、不更新门禁报告）；正式 plan/execute 仍需实际源门禁。
- **facts checker 检查身份、条件字段与溯源，不声称证明完整语义理解**：文档/结构 PASS 不代表已编译或行为等价。
- 原 Android 源语言专用画像检查**不用于 iOS**（口径坑：不得把 android-* 检查套在 iOS 规格上）。
- 已冻结规格的进度可变区按 `../a2h-plan/references/plan-delivery-contract.md#状态解释` 限定到 catalog 核心索引表与合法稳定 ID 行；范围/owner/依赖/归属及结构变更先复核再显式 replan。
- `requirements-index.json` 仍由原 HMigBot helper 从稳定 AC 生成，交 a2h-plan。

## 7. 读取时机（references）

| 触发时机 | 必读文件 |
|---|---|
| 执行 §1 之前；机器产物/状态写者存疑 | ../ios-source-analysis/references/harness-v2.md |
| 源事实字段、identity/state 规则 | ../ios-source-analysis/references/native-facts.md + source-semantics.md |
| MCP 证据采集；expertise-plan/review | ../ios-source-analysis/references/external-expertise.md + source-input-evidence.md |
| 生成 baseline 前 | references/artifact-contracts.md + references/spec-delivery-contract.md |
| 共享/异步/取消动作生成 | references/action-contracts.md |
| Gate C 前复核 | references/spec-content-review.md + templates/gate-c-summary-template.md |
| 决策类目 | references/migration-decision-categories.md |
| spec-authoring | references/native-authoring.md |

## 8. 交接（Gate C）

- Gate C 前先按 §6 六条命令全部 exit 0。Gate C 交付 `feature/index/base/API/decision` 与未关闭 findings；**全部依赖明确后进入 plan**。
- 报告四轴分离，任意一种不能代替其他项：**已读源码 / 已生成规格 / 已编译源 / 已运行观察**。
- 移交产物清单：`spec/baseline/` 全部基线文档与 JSON、`spec/ref/` 分析与审阅记录、`spec/.a2h/open-findings.json`、`spec/reports/` 门禁报告、`spec/ui-coverage-report.md`、`requirements-index.json`。随后提示进入 `a2h-plan`（同会话可直接续跑）。

---

## 收尾：上报本阶段用量

本 skill 的最后一步（无论经 a2h-run 还是单独触发）：

```bash
.migbot/bin/a2h mark-stage a2h-spec
```

标记 `a2h-spec` 阶段水位（写 stage-marks fact，受授权门控、尽力而为）。token 用量由宿主生命周期采集，本步不采集。**忽略其退出码，绝不阻断流水线。**
