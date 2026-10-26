<!-- when: 生成/升级Spec、设计产物或Gate C交接时读取；topics: 产物清单、作者、版本、消费者、冻结 -->
# Spec产物合同目录

## 单源与版本

业务内容职责在本规程、[交付合同](spec-delivery-contract.md)及模板；机器核心章节、表头、字段和枚举在随包 [产物catalog](../../../schemas/spec-plan-artifacts.json) 及其引用schema。解析器消费同一catalog，不在每个prompt复制一套字段定义。新增格式必须同时接通模板、实际校验器和消费者，再登记测试，不能仅添加schema声明。

`.migbot/config.json.ios_harness.spec_contract_version` 是项目的内容profile。新项目采用2；既有profile 1继续走原兼容格式，显式升级时补齐v2内容、重做源复核和门禁并重排，不继承旧PASS。已经冻结profile 2的项目不得通过删标记、改回1或在文档声明1绕过检查。profile不等于所有JSON的schema_version：例如semantics/coverage/facts是v2，source index仍用原version 1，页面meta载荷仍保留schema_version 1并声明spec_contract_version 2。

核心标题/表头按模板精确写，固定表不追加/重排核心列；领域扩展放附加小节或另表，不允许靠改标题/挪内容逃避必需项。源能力不适用时写 `not_applicable: <具体理由；源路径:行号>`；有表头但零行不代表不适用。unknown写原因、影响范围和获取步骤，阻断受影响交接；空值、空表、仅“详见源码”不代表不适用。Markdown里的代码示例不算正文标题或实际动作定义。

## 主业务与范围产物

以下路径均相对目标工程。`冻结`指domains计划消费后纳入输入摘要；进度例外只限原授权写者的状态列，不能整文件豁免。未列新JSON附件不得自称已通过公共schema，须先补格式、读取者与实际检查。

| 产物/版本 | 生成顺序与唯一作者 | 权威内容/模板 | 适用条件与消费者 | 检查与冻结/失败回流 |
|---|---|---|---|---|
| `spec/ref/ios-project.md`；原分析MD格式 | 工程分析先生成 | target/configuration、入口、有效构建线索与未知 | 所有项目；四类分析与Spec消费 | 源锚点独立核对；相关合同由contract_refs进入冻结；工程范围问题回工程owner |
| `spec/ref/module-index.md`；原分片格式 | 大工程主分析者分片前生成 | 模块/文件/共享事实作者与消费方 | 按需；分片分析、Spec收口 | 不以文件数替代覆盖；作者冲突回主分析者 |
| `spec/ref/ios-{ui,feature,api}-facts.md`；原分析MD格式 | 各领域owner沿源链分析 | 入口、具体状态/布局/协议事实、证据、unknown与交接 | 相应源能力；Spec消费 | 按各analysis-v2规程复核；不得手写替代机器signals |
| `spec/baseline/feature-base.md`；profile 2 | 公共合同owner在feature/page前确定 | [base模板](../templates/feature-base-template.md)：模型、恢复、网络、事件、偏好、权限、服务、组件、跨栈基线 | 必交；无能力有据N/A；feature/Plan/Execute/Verify消费 | spec-check查核心结构，独立源复核语义；冻结；冲突回base owner |
| `spec/baseline/feature-index.md`；profile 2 | Spec主作者按行为边界生成 | [index模板](../templates/feature-index-template.md)：模型概览、12列功能表、依赖图、拓扑序 | 必交；Plan排期与恢复消费 | 核对ID/归属/元数据与主spec一致；仅进度可变；范围变更重排 |
| `spec/baseline/features/FNNN-name.md`；profile 2 | 功能owner，公共合同确定后生成 | [feature模板](../templates/feature-spec-template.md)：元数据、源语义、数据流、行为、接口、状态、接线、AC | 每个在范围F-ID；Plan/Execute/Verify消费 | spec-check＋源/差异/追踪检查及独立联读；冻结；源合同冲突回原owner |
| `features/F*.{state,protocol,...}.md`；原addendum合同 | 所属feature作者按复杂度外置 | 主spec保留全部稳定AC和精确impl指针；附件含完整状态机/协议/生命周期 | 按需；相关实施任务定向读取 | 原addenda closure检查；contract_refs传递冻结；未读影响任务不得完成 |
| `spec/baseline/ui-manifest.md`；profile 2 | UI主作者，页面候选审阅后生成 | [manifest模板](../templates/ui-manifest-template.md)：全局约定、页面表、显示态、状态口径、嵌入、证据 | 有UI项目；UI排期与父子装配消费 | spec-check核心结构＋UI覆盖；仅进度可变；归属/嵌入更改重排 |
| `spec/baseline/ui/page_NNNN_Name.md`；profile 2 | 页面唯一作者 | [page模板](../templates/page-spec-template.md)：组件、布局、状态、事件导航、具体映射、资源和接线 | 每个在范围page；UI转换/功能slice消费 | 四核心表/精确引用/状态映射＋独立源复核；冻结；布局/状态冲突回页面owner |
| `spec/baseline/ui-snapshots/<page_id>/meta.json`；载荷1/profile 2 | 对应页面作者，页面事实后生成 | [meta协议](../templates/meta-json-schema.md)：身份、源引用、呈现、条件、资源/导航、真实截图状态 | 每个page；源/页面检查与转换消费 | 格式与路径检查不证明截图场景完整；冻结；源证据变化需重审 |
| `spec/baseline/skip-list.md`；profile 2 | Spec收口作者，复用原决定 | [排除模板](../templates/skip-list-template.md)：范围/区间、原因、源证据、决策 | 必交；无排除有据N/A；源检查/Plan消费 | 精确Preview走既有哈希审阅；冻结；未经批准的排除回范围owner |
| `spec/baseline/source-coverage-report.md`；profile 2 | Spec收口作者 | [覆盖模板](../templates/source-coverage-report-template.md)：源归属、分母来源、限制、unknown | 必交；Gate C与Plan消费 | 源归属/义务绑定/运行状态分开；冻结；统计与明细不符先重建再复查 |
| `spec/decision-ledger.md`；原决策合同 | 原决策作者按授权维护 | D0、稳定decision ID、批准范围、替代数据流、supersedes和新AC | 必交D0，差异按需；全流水线消费 | 原差异检查及批准证据；冻结；不自动批准产品取舍 |
| `spec/baseline/api-inventory/common.md`、服务/系统/依赖JSON；各载荷原协议 | API owner，实际调用分析后 | method/path/protocol/auth、请求响应、权限、初始化/回调/释放、真实版本 | 按实际能力；feature及目标领域实施消费 | 必须声明格式/源锚点并由实际消费者检查；公共MD精确引用冻结；没有完整schema的附件需披露限制 |
| `spec/baseline/api-inventory.json`、可选`api-contract-links.json`；原服务协议/引用视图1 | API owner；服务合同后生成引用视图 | 原services形态保留；引用视图仅连接既有端点ID、F-ID、源锚点和精确MD标题 | 按实际网络能力；原Plan/网络消费者读inventory，检查器读视图 | [按需JSON协议](optional-json-contracts.md)及schema；不得以视图覆盖旧清单；摘要冻结 |
| `spec/baseline/features/*.state-machine.json`；载荷1 | 所属feature作者，复杂状态机按需外置 | states、transitions、AC、源锚点、反指主MD合同 | 按需；实施/验收读取主spec明确指向的附件 | [按需JSON协议](optional-json-contracts.md)及schema；from/to须已声明；输入改变重审 |
| 外置状态/类型JSON；登记的本地格式 | 公共合同/页面owner | 只在内联不足时外置，明确字段、版本、空值与接口 | 按需；登记实际读取者，不许无人消费附件 | 未有检查器时保持未核验，不能宣称schema通过；引用路径和内容需冻结 |
| `spec/ui-coverage-report.md`、`spec/gate-c-summary.md`；原报告/profile 2摘要 | 独立复核/主线程收口 | [Gate模板](../templates/gate-c-summary-template.md)：当前输入、实际检查、缺口及可排期范围 | 必交交接；Plan和用户审查消费 | 不手填脱离明细的通过数；输入改变旧结论过期；未运行保持not_run |

## 机器事实、审阅伴随件与派生产物

机器文件唯一写者仍是原工具，不得由模型补ID、改摘要或删义务。模型负责解释性伴随件；校验报告由实际命令生成。完整JSON结构分别见 [Harness](../../ios-source-analysis/references/harness-v2.md)、[原生事实](../../ios-source-analysis/references/native-facts.md)、[外部资料](../../ios-source-analysis/references/external-expertise.md)及相应schema/实际解析器。

| 产物/版本 | 唯一作者与生成条件 | 内容/消费者 | 时效、检查与失败回流 |
|---|---|---|---|
| `baseline/ios-source-index.json`；version 1 | source-index；后续source-refresh | 源路径/摘要/快照；所有源分析 | 源变化显式refresh审阅；不只换hash关闭旧finding |
| `baseline/ios-facts.json`、`ios-obligations.json`；schema 2 | facts；provider按实际可用执行 | 机器事实、义务、证据层级；semantics/coverage/Plan | validate_graph核对当前源；禁止手改；提取未知回provider/源分析 |
| `spec/ref/ios-*-signals.json`；schema 2 | facts-view相应scope | 分专业机器视图；分析者继续读源码 | 线索不等于绑定或运行；当前图不符重提取 |
| `baseline/ios-semantics.json`；schema 2 | page/feature事实作者 | typed known、fact_ids、evidence、unknown/N/A；source-check消费 | 必需维度与状态值核对；源证据变更重审；v1仅导入历史 |
| `baseline/ios-coverage.json`；schema 2 | Spec源复核作者 | obligation_id→ac_ids及source_review；harness/Plan消费 | 当前graph_sha256；义务/AC不可漏；精确Preview仅按支持协议排除 |
| `baseline/ios-source-disposition.json`；原范围协议 | 源范围作者按 `source_disposition` schema 维护，`spec-authoring` 序列化候选 | `files` 条目必须有 `path/disposition/reason/line/end_line/source_sha256`；顶层另绑定整件源快照摘要；owner归属写page/feature的source_anchors | 不按目录猜排除；混合文件继续读产品符号；不可未知变排除；排除证据在authoring/source-check即按当前文件字节与行数核验，Stage0消费者仍独立复核 |
| `baseline/literal-ledger.json`；schema 2 | literals，从真实源提取 | 原始字面量/表达式/单位/源摘要；harness与产品投影消费 | 禁止spec空扫描代替；源变化重提；产品投影不覆盖raw |
| `spec/ref/ios-expertise-plan.json`、`ios-expertise-reviews.json`、`ios-analysis-provenance.json`；schema 1 | expertise-plan；expertise-review保存真实源观察 | 固定专业资料、实际阅读、主题观察与来源；source门禁 | 当前源/资料包摘要；没有实际阅读/工具调用不能标used |
| `spec/ref/mcp-runs/*/artifact.json`、`ios-mcp-index.json`；schema 1 | mcp-query实际调用时 | 工具响应和源事实关联；声明tool_evidence_ids的claim消费 | 响应只为tool_response；原capture校验、失败/unknown保留 |
| `spec/ref/provider-runs/**`；provider协议2 | facts --providers实际执行 | SwiftSyntax/Clang/IB/构建等证据包；事实提取消费 | 只提高对应解析层级；失败保留failure，不伪造AST |
| `spec/ref/ios-manifest-evidence/<capture-id>/manifest.json`、`artifacts/**`；schema 1 | manifest-evaluate实际执行；模型不写报告或原始日志 | [清单证据规程](../../ios-source-analysis/references/source-input-evidence.md)及[清单schema](../../../schemas/source-manifest-evidence.schema.json)；facts --manifest-evidence、依赖盘点、validate_graph消费 | 绑定精确清单路径与当前源，回放原始命令/输出；domains冻结原始证据；失败/过期保留并重采，不代表依赖解析或构建成功 |
| 原`requirements-index.json`、追踪/literal派生索引 | 原HMigBot helper，从稳定AC派生 | 唯一活动AC身份及源/目标引用；Plan/Verify | 按原命令重建并核对摘要；不另建第二份AC集合 |
| `baseline/ios-source-check.json`、`spec/reports/ios-harness-check.json`、spec-check报告 | 实际检查命令 | 源归属/格式/义务/内容结果；阶段门禁 | 报告绑定当前输入；spec-check只读，原source-check管理自己的finding节 |

## 交给Plan的边界

Spec交付后，按 [Plan产物合同](../../a2h-plan/references/plan-delivery-contract.md) 生成indexed UI/Base/Slice责任计划及与执行JSON的显式映射。业务语义留在本目录主MD；Plan不得再自由生成另一份接口或完成时点。任务自动携带精确合同闭包与AC，独立复核者检查消费者是否完整读到。

`baseline/plans/resource-mapping.md`由Execute Stage 0记录真实转换结果，不是Spec/Plan提前伪造的必交物；规格阶段只记录源资源与转换责任。原三控制账本继续由原工具写入，本目录/catalog/报告均不是新进度账本。
