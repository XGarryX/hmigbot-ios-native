# 0.6.0 原生事实与执行协议

本规程是七个 iOS 技能共同的控制协议。程序检查范围是确定性合同和已检测信号；业务解释、动态绑定与设备行为需要独立复核。不得把 token_signal 写成 compiler_binding 或 runtime。

规格交付按 [公共合同](../../a2h-spec/references/spec-delivery-contract.md) 形成。0.8.0 的只读 spec-check 校验正文、目标锚点、状态映射和显式共享引用，source-check --harness 内置同一检查；字段齐全仍不证明语义正确。精确 Preview 义务的哈希审阅排除、旧 baseline 升级及共享引用写法见该合同。import 仅为依赖线索，不产生持久化行为义务。

内容profile与harness载荷分别版本化：新项目 `ios_harness.spec_contract_version=2`，旧profile 1按兼容路径；升级补齐 [产物合同](../../a2h-spec/references/artifact-contracts.md)、独立复核并重跑门禁，不继承旧PASS，已冻结profile 2不得降级绕过。核心MD提纲/表头、页面meta、动作定义/引用与按需附件格式由随包catalog/schema及实际校验器限定；自然语言语义仍按 [独立联读](../../a2h-spec/references/spec-content-review.md) 裁定。

0.7.0 增加 [外部专业 skill/MCP 规程](external-expertise.md)：facts 后运行 expertise-plan，
由对应分析 owner 读取固定原文并用 expertise-review 保存源观察。source-check --harness
要求此清单/审阅通过，包括 0.6.0 项目升级。可选 mcp-query 保存实际响应，known claim
以 tool_evidence_ids 关联；响应本身只为 tool_response。domains 计划冻结这些证据。

## 初始化与机器事实

从配置读取源、目标。源不可读即阻断。首次依次执行随包 runtime 的：

```text
python <runtime>/scripts/a2h_ios.py harness-init --project <target>
python <runtime>/scripts/a2h_ios.py source-index --project <target>
python <runtime>/scripts/a2h_ios.py facts --project <target>
python <runtime>/scripts/a2h_ios.py literals --project <target>
```

有 0.5.0 baseline 时用 `import-legacy` 代替 `harness-init`；旧声明存入 history 并转 unknown，稳定 page/F/AC ID 保留。已有外来 state.json 时拒绝混用写者，先审阅迁移方案，不能删除账本绕过。

facts 生成 ios-facts.json 与 ios-obligations.json。这两件禁止模型手改。fact ID 与行号分离，源片段、文件摘要、owner、symbol、kind、value、解析层级和构建范围均保留。状态初值保留源表达式文本，不擅自求值。

identity 信号保留原有 ID 与数量，附加可重提回放的 token_index/identity_usage。普通 `.id` 成员读取（含比较、optional 链、key path）的判据候选为 unit/contract/ui；`ForEach` 和 `.id(...)` 调用仍需 UI，未知接收者也不例外。`ForEach(id: \.id)` 中 key path 的读取不取代 ForEach 自身的 UI 义务。缺失/未知用法元数据保持原 UI 规则；泛型、写入等歧义形式保守处理，不根据目录或 import 猜语义。这仍是 token_signal，不证明业务受到正确测试。上下文 selector 与规则一同进入 rules_sha256；旧 baseline 需运行原 `facts` 重提取、复审受影响的 semantics/coverage/AC 并重跑门禁，不能手补 metadata 或继承旧 PASS。

仓库扫描包含未选中的配置，effective_build=unresolved。`--variant` 的 selected-build 必须携 source_build 证据包及已哈希 source-files.json；导入文件的完整性不证明捕获真实性。遇到条件编译、宏、动态派发或解析未知，不能用扫描数量声称有效构建已解析。

需要解除具体 `Package.swift` 的未求值问题，或从真实Xcode工程推导产品/测试成员时，按 [清单求值与产品成员证据](source-input-evidence.md) 使用 `manifest-evaluate`、`facts --manifest-evidence` 和/或 `facts --variant` 的 `project-targets`。输入、证据回放、失败边界与旧图复审以该规程为单源；它们不提升为有效构建或行为证据。

`--providers <provider-plan.json>` 执行指定 SwiftSyntax/Clang/构建设置/IB/资源 provider，记录源摘要和实际产物。provider 只提升自身证据层级，不自动消除业务未知。工具失败保留 failure.json；不伪造 AST。配置格式见 [provider 计划示例](../assets/provider-plan.json)。

## 模型事实与覆盖

依赖/测试/批准替代范围按 [单一源责任合同](../../a2h-spec/references/source-responsibility.md) 消费；原 helper 重建活动与历史 AC，所有门禁/计划/调度统一验证和冻结，不能只补文件名。

工具审计和项目执行必须遵循 [结果分离规则](../../a2h-run/references/tool-project-status-separation.md)。批准替代保留 source_history 与源 unknown，活动目标 AC 来自原 helper 重新计算；投影输入与规则代码均进入计划冻结。

页面/功能清单确定后先按 [原生规格生成协议](../../a2h-spec/references/native-authoring.md) 运行 `spec-authoring`，让工具枚举全部文档、条件维度、处置必填字段和各AC允许的源位置。候选不写baseline或控制账本；原作者复核落盘后仍运行原门禁。

逐 page/feature 维护 `ios-semantics.json` v2，每个必需维度仍按 native-facts.md 枚举。known 的 value 必须是对象，fact_ids 指向所属源码的机器事实，evidence 必须落在这些事实片段内。复杂语义说明放 value 中，但须解释操作、状态、错误和观察结果。

state_ownership.value 固定为 `{ "states": [{ "fact_id", "owner", "storage", "type", "initializer" }] }`，内容精确匹配状态事实。0、false、nil 与 Optional 默认值分别保留。

unknown 必须带原因并阻断受影响实现。not_applicable 只有在完整调用链审阅后才可记录具体理由；源码信号与不适用矛盾时程序拒绝。不准用“已处理”“无特殊情况”覆盖全部维度。

`ios-coverage.json` v2 的每条 mapping 包含 obligation_id、ac_ids、source_review。review 必填 status=reviewed、input、processing、observable、reviewer；说明来自源行为。义务只能由规则生成，不能自行少列一个。AC 沿用原稳定 ID 和 `判:... | 真:...`，判定方式至少满足 ios-obligations 给出的候选之一。义务可共享 AC，但必须确实被该 AC 的具体场景覆盖。

执行 `harness-check` 或 `source-check --harness`。只运行无旗标 source-check 是旧消费者兼容检查，不能进入新版实现。检查将问题写入原 open-findings 的 spec.ios-harness section，不清空其他 section。

## 计划与四拍

原 indexed UI/Base/Slice 计划继续保留作为可读责任合同。再将任务交给 `plan-ir --input <typed-plan.json>`。输入包含 schema_version=2、wave=domains、graph_sha256、tasks、max_parallel（缺省 1）、decisions。

每 task 必填 id、role、goal、ownership（具体文件，禁止通配）、fact_ids、ac_ids、parents。角色必须随包存在；共享导航、资源和注册文件必须分配单一 owner。所有 AC 进入任务，不能遗漏检测义务的事实。代码任务包含原资源、UI、Base、Feature、组装责任，按实际依赖排 DAG。将占位、接口及平台差异决定写入计划/决策，禁止在执行时临场造替代行为。

计划生成器写 canonical blueprint、原版 plan IR、任务书。计划、任务书和 baseline 均按摘要冻结。不要自写 state.json、dispatch.json 或 journal.json。

```text
next-batch --project <target> --wave domains
按 action=dispatch 返回的任务书执行
任务产出同一路径的 ios-receipt v2
land-results --project <target> --wave domains
```

以上命令均经 a2h_ios.py 调用。宿主不可派代理时串行执行同一任务书并写同样回执，不另造计划。wait 只等待在途任务；escalate 保留失败并修根因；done 只代表代码任务已落账。每次 land-results 成功后、阶段门收口和 verify 结束时，实际执行下节派生报告命令；部分执行也报告当前事实。原版最多重派一次，源合同错误不能通过欠账放行。

回执示例见 [receipt](../assets/receipt.json)。source_sha256、plan_sha256、task_id、ac_ids、file_hashes 必须真实。generated + final_state=PASS 表示生成已完成，behavior_verified=false；blocked + BLOCKED 表示未完成。原版兼容字段 domain、fixed、skipped、files_touched 同时保留。禁止把 blocked 回执改 PASS，缺产物、越权文件、摘要不符和开放 findings 均拒绝落账。

## 派生汇总与可检查报告

通过随包 runtime 依次执行，`<target>` 使用绝对目标路径：

```text
python <runtime>/scripts/a2h_ios.py spec-summary --project <target> --output <target>/spec/reports/spec-summary.json
python <runtime>/scripts/a2h_ios.py migration-report --project <target> --output <target>/spec/migration-report.md
python <runtime>/scripts/a2h_ios.py migration-report --project <target> --check <target>/spec/migration-report.md
```

有当前真实构建 JSON 报告时，三条均追加同一 `--build-evidence <build-report.json>`。读取产物和实际退出码；`--check` 重算当前证据，拒绝过期或手改结果。目标、规格、回执、落账或验证证据变化后重建报告并重检。缺证据时保留工具返回的未知/未跑/未落账/过期，不用 brief 的 PASS 或旧 verified 替换。Markdown 由生成器完整维护；阶段说明另写并链接，两类派生产物都不改控制账本。

summary 的逐页关联包含 `page_id`、`plan_item_refs`、`task_ids`、`target_paths`、`ac_ids`。生成只认冻结计划、当前 receipt/产物摘要和原内核成功落账；编译只说明当前全工程构建输入覆盖声明页面文件，不证明注册或可达性。行为按该页真实 AC 观测与判定层级计算，不把全局 PASS 分摊到页面，不把 host 逻辑测试称为设备 UI。逐页视觉尚无可校验协议时保持 not_run，旧报告只作 legacy_unclassified；真实视觉与结构仍分别引用对应 verifier 和结构门的证据。

## 验证与恢复

调用原结构、编译、UT、UI/视觉技能执行真实检查。构建与设备环境不足时，记录受影响范围，继续独立任务；不得声明该范围 PASS。

维护 ios-behavior.json v2：事件链为 input→processing→feedback；存储链为 save→reload→business_effect。每节点携 target path/line/symbol/sha256。review 指明独立审阅者。源 oracle 绑定 source_fact、expected、reviewer；目标用真实命令/设备 provider 观察，不能将目标实现生成的期望反过来当真值。

`behavior-check` 默认只查链路，未运行用例返回 UNVERIFIED（exit 3）。`behavior-check --run` 才执行声明命令、保存 stdout/stderr/退出码，并比较独立 expected。单个 unit 结果不能证明 ui/device AC，任何未覆盖 AC 保持待验。源码或目标改动后必须重测；结构检查不能证明功能等价。

源码变化后 `facts` 归档旧图并重提取，重审覆盖、规格和计划。冻结计划不会自动重写；续跑前对变更及已落账范围做明确重排，不继承过期回执。失败按原 finding owner 处理，复跑产生该 finding 的检查才能关闭。

源索引更新使用 `source-refresh --review <review.json>`，必填 reviewer/reason/previous_source_sha256/source_sha256；仍须重审并复跑门禁。已冻结计划用 `replan --input <typed-plan.json>`，附 replan_review 的 reviewer/reason。在途任务须先落账或明确终止，旧三账和任务书归档，新 run 不继承旧成功。行为用例必须携 target_hashes，执行前后核对实际目标输入未变。


## 显式终止旧在途 blocked attempt（review v1）

已审 Spec 更正后，普通 `land-results` 仍先检查旧冻结输入，`replan` 仍拒在途。
确认所有相关 worker 已停后，独立审阅者固定下列 JSON 原字节，执行：

```text
python scripts/a2h_ios.py recover-blocked --project <target> --review <review.json>
python scripts/a2h_ios.py replan --project <target> --input <target>/spec/ref/replan-request.json
python scripts/a2h_ios.py next-batch --project <target> --wave domains
```

review v1 为严格对象（未知/缺失字段拒绝），字段如下。所有 `*_sha256` 和
`contract_revision` 是非空64位小写十六进制；输入集合摘要为 `digest(json_bytes(mapping))`，
沿用 core.json_bytes 的排序和换行，不能用文件大小或手工拼接替代。

```json
{
  "version": 1,
  "wave": "domains",
  "task_id": "original-task-id",
  "attempt": 1,
  "reviewer": "具体独立审阅者及已审记录身份",
  "reason": "具体已审差异与失败终止原因",
  "workers_stopped": true,
  "old": {
    "plan_sha256": "<原plan文件摘要>",
    "contract_sha256": "<原contracts.json摘要>",
    "dispatch_sha256": "<原dispatch.json摘要>",
    "dispatch_evidence_sha256": "<原ios-dispatch-wave.json摘要>",
    "receipt_sha256": "<原诚实blocked收据摘要>",
    "source_sha256": "<原合同source_sha256>",
    "graph_sha256": "<原合同graph_sha256>",
    "baseline_inputs_sha256": "<原合同input_hashes集合摘要>",
    "contract_revision": "<原合同工具revision>"
  },
  "new": {
    "contract_revision": "<当前已审工具contract_revision>",
    "baseline_inputs_sha256": "<当前baseline_inputs集合摘要>"
  },
  "changes": [{
    "path": "spec/baseline/ui/page_0001_Example.md",
    "old_sha256": "<原input_hashes值>",
    "new_sha256": "<当前input_hashes值>"
  }],
  "replan_request": {
    "path": "spec/ref/replan-request.json",
    "sha256": "<真实且经plan-check完整验证的新版计划请求原字节摘要>"
  }
}
```

这是字段示意，不是可直接提交的伪摘要。仅支持**唯一在途的 attempt 1**：旧收据协议
无 attempt 字段，后续 attempt 无法可靠区分陈旧收据，因此保守拒绝。Spec差异只允许
原已冻结的 `spec/baseline/**/*.md`，逐项旧/新摘要恰好覆盖全部baseline差异；必要派生
文件仅允许一个实际通过新版 `plan-check` 的 `spec/ref/*.json` replan request。
不支持其它派生差异时应保留阻断，不能扩写review允许表来授权App、配置或控制面修改。

源/图、六件原合同、plan IR、prompt、dispatch身份、完整封存fence、receipt身份与
ownership/文件摘要/AC均须吻合；工具升级精确绑定旧/新revision，普通冻结检查不变。
恢复前所有校验均完成，首次证据保存在
`spec/reports/ios-blocked-recovery/<review内容摘要>/`；原控制文件、原收据、旧新输入
集合、真实原writer结果均保留。只调用原 `land_results --missing-as-failed` writer；
结果 `blocked_attempt_terminated` 仅表示失败终止，绝不是生成/构建/行为通过。
相同完成请求重放只读返回首次结果；中断后只有不完整归档则拒绝自动重试，交人工审计。
随后正常replan归档旧控制面并新冻结，旧成功状态不继承。此入口不自动停止worker，
不代表平台自动恢复或实际设备验收。


唯一可选字段 `authoring_rebind` 用于原生作者输入的库存绑定更新：
`{"path":"spec/ref/native-authoring-reviewed-input.json","previous_copy":"<已保存旧原件的绝对路径>","old_sha256":"<dispatch.before_files原摘要>","new_sha256":"<现原字节摘要>"}`。
仅此精确路径；旧副本须匹配原dispatch可信摘要，删去`inventory_sha256`后的JSON须深相等，
新库存摘要由现有native_authoring._inventory重新计算且source仍绑定原图。其它正文/配置/
disposition改动一律拒绝。旧新原件纳入首次归档；不全局豁免该输入文件。


完成缓存只有在最后写入的`seal.json`完整列举首次文件集合及原字节摘要时才可只读重放；
同时核固定失败结果/false布尔、review与task/attempt身份、原blocked收据和原writer归档
journal/state/action一致。单改result或同步改seal仍伪装成功均拒绝；不把损坏字段改回false
后静默接受。缺seal或首证据不完整保留拒绝，不迁移/补写/覆盖旧归档。seal是本地完整性
与事故取证边界，不能代替独立审阅或防御对整份历史及审阅输入的恶意一致重写。


### 两份公开托管说明升级的恢复证明

可选`managed_upgrade`只接纳`.agents/skills/ios-source-analysis/SKILL.md`和
`.agents/skills/ios-source-analysis/references/harness-v2.md`实际发生变化的子集：
`{"install_manifest_sha256":"<当前.hmigbot-ios/install.json原字节摘要>","old_runtime_revision":"<review.old.contract_revision>","current_runtime_revision":"<review.new.contract_revision>","files":[{"path":"<上述精确公开路径>","old_sha256":"<原dispatch.before_files值>","new_sha256":"<当前官方清单/公开文件/包内skills三方相同摘要>","old_copy":"<原派发版本已保存原字节的绝对路径>"}]}`。

须经实际已安装的公开runtime调用。旧hash直接绑定原dispatch，不要求等于最近一次升级
之前版本；支持原任务跨已接受中间升级。当前清单owner/schema与清单原字节摘要须吻合，
公开文件和包内对应skills字节须相同且两条清单记录同时吻合。不能将其它.agents、配置、
App或任意JSON放入证明。首次归档保留`managed-install.json`原清单与`managed-upgrade.json`
证明/旧公开原字节/当前公开及包内原字节（base64）；完整纳入seal，重复时重新校验归档
证明和旧dispatch绑定，不依赖后来又升级的当前文件。此证明只解释托管说明变化，不能
声称任务生成/行为成功；其它普通冻结和恢复保护保持。
