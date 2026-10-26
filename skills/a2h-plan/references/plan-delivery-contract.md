<!-- when: 生成、检查或消费 spec_contract_version=2 的 Plan 产物时加载 -->
<!-- topics: plan 交付合同, indexed-v1, plan-items, plan_item_refs, 任务输入闭包 -->

# Plan 交付合同（profile 2）

本合同补齐 indexed-v1 的内容和来源映射，不替换原调度、覆盖检查或三份控制账本写者。新生成的 Spec/Plan 使用 `spec_contract_version: 2`；没有该字段的历史项目按原版本读取，已冻结profile 2的项目不能降回旧格式绕过检查。

## 产物、作者与消费者

所有路径相对项目根。模板是提纲和内容要求，JSON schema 与解析器检查机器字段；二者须同版本发布。

| 产物 | 生成者与内容边界 | 检查与下游 |
|---|---|---|
| `spec/baseline/plans/ui-plan.md` | P1-A；Context、逐 Batch 页面表、结算点、Summary、Plan items；页面表带 item_id/真实目标路径/唯一 owning_slice | 覆盖 ui-manifest 非 skipped 页面；Stage 1 converter 消费对应行及页面规格 |
| `spec/baseline/plans/feature-plan.md` | 主控 P2；Context、Base stub、Group/Slice 索引、FV、Summary、FV 的 Plan items；索引不复述 Base/Slice 正文 | detail 指针与实际文件对应；Stage 3 调度、FV 消费 |
| `spec/baseline/plans/base-plan.md` | P1-B；公共能力任务的输入节、精确输出、依赖与验收责任、Plan items | Stage 2；资源映射是 Execute Stage 0 的输出，Plan 只声明产出义务 |
| `spec/baseline/plans/slices/slice-NN-<fid>.md` | P1-C；只读接线投影、3a–3d的work_scope/精确输入、局部责任表与Plan items | worker消费实施输入；closer定点消费结构投影 |
| `spec/baseline/plans/coverage-matrix.md` | 主控从当轮检查结果汇总；Feature/UI/接线归属、AC、MD→JSON 映射、失败项与证据路径 | Gate 摘要和重排检查；数值从明细推导，不手填完成数 |
| `spec/placeholder-registry.md` | 原单写者/发号协议；沿用六字段及既有 kind 枚举 | 原 placeholder/closure 消费者；plan 期与执行期允许产生的 kind 按原规则区分 |
| Gate 摘要 | 主控按 gate-output-template 呈报；文件版本、检查结论、例外和待处理项 | 沿用当前用户授权；摘要不是新的控制账本，不以人工确认豁免失败门禁 |
| domains 输入及 plan-ir 产物 | 原 harness 命令生成/冻结；每个 typed task 带 `plan_item_refs`、AC、写权、依赖、验证义务与合同输入闭包 | plan-ir 校验后生成 blueprint/plan/prompts；执行只读冻结任务，原工具写三份账本 |

条件产物（chain-auth、多模块合同、平台专项 addenda）由 Spec 的范围与引用决定；没有实际来源时标明不适用，不能造空文件凑齐。`resource-mapping.md` 和 execution briefs 不要求在 Plan 阶段预生成。

## 稳定调度项与 JSON 投影

正文每个可执行单元有稳定 `item_id`：UI 表为 `PAGE-0001`，Base 为 `Base-0`（允许原有 `Base-6.5`），Slice Step 为 `3a/3b/3c/3d`，FV 为 `FV-1/FV-2`。全名分别为 `UI:PAGE-0001`、`BASE:Base-0`、`SLICE:F001:3a`、`FV:FV-1`；slice 编号调整不改变 F-ID 下的动作身份。

正文每个item在含该完整ref的独立标题之下恰有一张局部责任表（如`### SLICE:F001:3b`），固定两列表头`字段 | 值`、恰7行。值全部为JSON literal，item_id使用完整ref，不能用自然语言、逗号拼接或关键词猜测依赖/范围/验证义务。独立标题是冻结任务精确消费定位权威；该表是任务责任正文权威，页面概要/输入/work_scope供人读。格式如下：

### SLICE:F001:3b

| 字段 | 值 |
|---|---|
| item_id | "SLICE:F001:3b" |
| ac_ids | ["F001-AC01"] |
| ownership | ["entry/src/main/ets/viewmodels/LibraryViewModel.ets"] |
| parents | ["BASE:Base-1"] |
| page_ids | ["page_0001"] |
| scope | "product" |
| verification | "generated" |

每份含任务正文的MD再有且只有一个`plan_items_version: 2` JSON fence，逐字段严格等于本文件全部局部责任表；该块是正文的机器投影，不是第二份业务详案。feature-plan仅投影自身FV，Base/Slice投影放各自文件。字段固定如下：

```json
{
  "plan_items_version": 2,
  "items": [{
    "item_id": "SLICE:F001:3b",
    "ac_ids": ["F001-AC01"],
    "ownership": ["entry/src/main/ets/viewmodels/LibraryViewModel.ets"],
    "parents": ["BASE:Base-1"],
    "page_ids": ["page_0001"],
    "scope": "product",
    "verification": "generated"
  }]
}
```

- `ownership` 为本单元写入的精确相对路径，不用目录/通配符掩盖写权。只读最终验证可为 `[]`。
- `parents` 引用完整 item_id；根任务显式 `[]`。仅排序依赖形成串行边，契约依赖形成读取闭包；不能把二者混作同一依赖。
- `page_ids` 用 `page_NNNN`，与 manifest 一致；UI 项必填，正文表目标路径与块内写权一致。
- `ac_ids` 引用 active AC；UI/Slice 实施项不可空，Base/FV 的公共基础或验证项允许空并由其输入/验收解释。`scope` 为 `product|excluded`；排除项不进入活动执行任务。
- `verification` 为 `generated|compile|behavior|visual`，表示该单元承担的交付义务；代码生成、编译和结构收口不能自动满足行为/视觉义务。

正文概要（UI表中的目标路径/AC等）必须与局部责任表一致。正文表→聚合JSON的7字段全部exact对账；只证明任意位置出现相同ID/路径/词语不构成一致。局部表、聚合投影、typed task同步改变仍需通过Spec范围/AC/页面owner/原依赖与验证义务的检查，不能用机械一致代替独立源复核。

独立FV没有全工程写权限：profile 2 FV-1结构检查与FV-2编译检查使用只读ownership=[]（verification=compile，另保留结构检查义务），发现问题回文件原owner修复再重检。原Stage内部closer在冻结owned_files授权范围内仍执行接线/修复/收尾；不能把同一文件再分给独立FV来绕过唯一写者。

domains 的 typed task 使用 `plan_item_refs: ["SLICE:F001:3b"]`，不另造平行编号。一个 MD 单元拆为多个 task 或多个单元合为一个 task 时，填写非空 `mapping_reason`，逐项核验 AC、精确写权、父依赖和验证义务均保留；task的verification按generated/compile/behavior/visual顺序取最高调度义务，同时保留每个item的原义务，视觉不自动证明行为通过。调度器沿用文件全生命周期唯一owner：需要先生成再接线/修复同一文件的MD单元合并给同一typed task，由任务内部按原Stage顺序实施；parents只约束不同写权任务，不能豁免重叠。MD 正文、Plan items、typed task 三层不一致即修原作者产物后重新检查，不能只修 JSON 让它表面合法。

## 生成、检查与任务交接

1. P0 先从已过门 Spec 提取 active AC、目标接口/动作、排序依赖、契约依赖和唯一页面创建者。UI/feature/共享合同冲突时记录两端路径与标题/ID、源 anchor、受影响 AC，回 Spec 修正后重过门；Plan 不选取较方便的一种解释。
2. A/B/C 按本合同及各自模板写 MD 与其 Plan items，主控收拢后跑原覆盖检查，再跑 plan-ir 的 MD→typed JSON 对账。coverage-matrix 和 Gate 摘要引用同一轮结果与摘要，过期结果不构成通过。
3. 派发 packet 带本任务 `plan_item_refs`、`ac_ids`、`spec_refs` 精确章节和 `contract_refs` 传递闭包（引用的共享接口、状态/值域、动作完成事件、范围决策、相关 addenda）。合同全文只保留一处；任务携带可定位引用与冻结摘要，不把长正文复制进计划。
4. worker 在实施相关 AC 前读完这些精确章节；缺失引用、未解决 unknown、冲突或输入过期均返回对应 finding，不自行补造行为。addenda 超过一次读取预算时分批读取或拆 task，直到受影响 AC 输入全部消费；未读部分不能仅登记 deferred 后宣称完成。
5. closer 继续默认只读结构投影；只有发现业务语义冲突才按 finding 提供的指针定点读相关合同。该节约策略不免除实施 worker 的输入消费义务，也不授权 closer 裁定源行为。

## 状态解释

Plan 生成后只读。沿用 ui-manifest/feature-index 中旧 `verified` 作为结构与构建流程兼容值；它不代表独立行为或视觉通过。生成、编译、结构、行为、视觉结果分别凭当轮证据呈报；未执行写 `not_run`，输入/代码变化后的旧证据写 stale，不把旧状态文字自动升级为通过。

profile 2 的单元格进度豁免以随包 `schemas/spec-plan-artifacts.json` 的 `progress` 声明为准：仅 `spec/baseline/feature-index.md` 的“功能清单”和 `spec/baseline/ui-manifest.md` 的“页面与覆盖层”两张核心表，按 catalog 完整表头与真实分隔行识别；核心标题须唯一。功能行的 ID 须匹配 `F[0-9]+`，页面行须匹配 `page_[0-9]{4}`，同表 ID 不重复；当前仅这些行的“状态”单元格可写 `pending|converted|implemented|verified|generated|blocked|not_run|running|passed|failed|stale|PASS|FAIL`。其它单元格保留原文摘要。相邻表、额外业务表、普通 `status` 列及数据中出现“状态/status/目标”等词均无豁免，也不能改变本表列映射；不能复制一张核心表获得第二个可变区。

`skipped/excluded` 是范围决定，不是可变进度；owner、目标文件、依赖、页面归属/创建者、scope、结构及其它正文变化均使冻结输入失效，须由原作者与独立复核者重审、重过门，再显式 replan。另一种豁免仅是 `<!-- hmigbot-progress:begin -->` 到 `<!-- hmigbot-progress:end -->` 间下述白名单进度块，不能在块内隐藏业务合同。

## 上游索引与受管进度的精确格式

UI概要表ac_ids使用JSON数组（如`["F001-AC01"]`），owning_slice精确等于feature-index“创建页面”唯一creator；不按关联页或拓扑顺序猜创建者。Slice各步骤page_ids的并集与所属feature“关联页面”集合相等，共页多feature合法。索引的F-ID排序依赖必须进入Slice项DAG；base/Base表示所有活动BASE项先于该Slice。契约依赖为真实存在的`路径#精确标题`并进入读取传递闭包，兼容F-ID引用也只表示读取，不自动串行。

受管进度块只允许空行、`N of M`、`generation|acceptance|features|pages|registered|resolved: N`或`N/M`，以及`generation|compilation|behavior|visual: pending|not_run|running|passed|failed|stale|blocked|generated|unverified`；可带`- `前缀。竖线在此表示枚举选择，N/M为非负整数及可选总数。其它语句/表格/JSON/合同均拒绝；不能通过把业务文字藏入该块获得冻结豁免。


## 可选能力声明的计划静态引用

profile 2 的 domains 计划可在本轮已验证的权威计划文件（索引 feature-plan.md、
Base、已索引 Slice 等）中使用一个闭合的 `capability-declarations` 围栏；
整个已验证 projections 文件集合全局恰好一个，不扫描其它任意 Markdown。
正文为 JSON 对象，仅含 `declarations` 与 `seams`。同文件或跨文件重复均拒绝；
没有该围栏保持既有计划校验行为，普通代码围栏内嵌的示例不视为声明。
本轮仅支持 `"seams": "none"`，其它形态明确拒绝。声明数组必须非空，
每项恰有 key/kind/symbol/path/slot/lifecycle/provider/provenance 八个字符串字段；
kind 为 runtime-slot、scoped 或 artifact-only。仅非 runtime-slot 的 slot 可为空；
其余字段非空，key 不重复。坏 JSON、重复 JSON 键、多声明围栏、不闭合围栏、
未知字段（如 phase）均拒绝，不静默跳过。

provider 使用 `<项目相对POSIX文件>#<完整item_id>`，例如
`spec/baseline/plans/base-plan.md#BASE:Base-1` 或
`spec/baseline/plans/slices/slice-01-F001.md#SLICE:F001:3c`。
仅当已验证责任文件中 basename 唯一时，可缩写为 `base-plan.md#BASE:Base-1`。
文件及 item_id 精确匹配，不接受大小写/前缀/全文包含猜测；责任须为 product，
声明 path 须为该精确责任的 ownership 成员，仅属于全局写权不够。
文件与 path 都须为规范相对 POSIX 路径，禁止绝对路径、目录穿越和通配符。
责任表/聚合投影/索引 detail 仍先通过原校验；新模块也纳入 contract_revision，
冻结后规则变化仍须正式审阅与 replan。常见拒绝包括
capability-declaration-invalid、capability-declaration-ambiguous、
capability-provider-unknown、capability-provider-ambiguous 和
capability-provider-owner-mismatch。

此处只验证计划引用，不生成 manifest、不证明运行实例/初始化或生命周期闭集，
不把行为未验证升级为通过；behavior_verified 保持 false。


## 版本2：能力声明义务的静态闭集

旧八字段格式仍仅作引用校验，不生成闭集manifest。现代gen/gate要求全局唯一
`capability-declarations` JSON围栏，`capability_schema`严格为整数2。扫描范围仅为
原`plan_units/_projection`已验证的索引/Base/UI/已索引Slice计划，不搜索任意MD。

严格字段如下（对象不接受额外字段、JSON不接受重复键）：

| 对象 | 恰有字段与类型 |
|---|---|
| 顶层 | capability_schema:2、declarations:非空数组、initialization:对象、seams:"none"、absence:"none" |
| 每个声明 | key/kind/symbol/path/slot/provider/provenance/materialization:字符串；lifecycle:不重复方法名字符串数组 |
| kind | runtime-slot、scoped、artifact-only、framework-created；框架类别必须由精确SDK基类与注册共同证明 |
| materialization | materialized或pending；除非runtime-slot，slot须为空；runtime-slot槽名保持实际产品拼写 |
| initialization | hosts、chains、injections三个数组；hosts/chains不可空 |
| host/chain规则 | path、owner、method三个字符串，calls/guards数组，result；owner为空表示该文件的真实export function |
| call | receiver、method、slot字符串及arguments字符串数组；receiver是源码表达式，slot是目标规范槽；this本地调用或export function的slot为空 |
| guard | mode:"if"或"early-return"，condition:源码表达式字符串 |
| injection | slot、dependency、field字符串，parameter:从0开始的整数 |

`result`只支持四形态：字符串`"none"`；
`{"mode":"return-call","call":<上述call>}`；
`{"mode":"expression","expression":"this.library.error === null"}`；
`{"mode":"boolean-state","field":"error","error_method":"describe","early_returns":[{"condition":"this.opened","expression":"this.error === null"}]}`。
boolean-state检查同一真实方法的try成功返回true/状态清空，以及catch记录字符串错误后返回false；
不会因其它方法有return true而通过。guard必须真实控制该规则中的调用；额外的未声明条件、
闭包/复杂控制包装等不能仅凭token同现放行。方法阶段由精确path+owner+method指定；
安装/根生命周期不按install/hydrate前缀推断，不强迫在Ability中重复启动页面根。

义务集合为product `BASE:Base-1..6` 与 `SLICE:*:3c` 的确切.ets ownership；
Base-0/6.5/7不是能力义务。每个义务path至少一个真实导出声明，同path多导出合法。
provider仍绑定精确责任及该责任ownership，不能用全局ownership或excluded reason豁免。
absence与seams本轮只能none，不接受P-ID/D-ID批准缺席结构，不将未知结构当已验证。

从Base-6.5 ownership中定位唯一顶层export const capabilityTable，要求直接对象字面量
`slot: variable`，变量是顶层const（支持类型标注）并直接new解析到真实path+symbol。
支持相对import别名，注释/局部同名表、null、错模块同名类、表内外重复规范new均拒绝。
所有构造参数按injections逐位置绑定规范变量及同一构造字段，不允许换一个Preferences。
scoped需要真实外部consumer的局部方法/函数或非static实例字段构造；顶层或static字段全局
实例不能冒充scoped。artifact可为真实enum/interface/@Builder导出函数/纯static类，
不强制new；自实例/自返回静态factory拒绝。只覆盖声明symbol，不枚举文件内每个DTO为能力。

生命周期数组中的方法须在真实声明类存在且由hosts/chains的规范receiver调用覆盖。
规范this字段、表导入及构造注入须解析到同一实例，guards和返回来源按受限结构校验。
工具不是完整ArkTS编译器；无法绑定的构造器/表表达式、复杂控制结构或未知schema明确非零，
不会把无法理解当静态闭集PASS。framework-created仅支持下述两个SDK基类/注册模式，其它明确unsupported。

公开协议保持`gen_capability_manifest.py --project-root <project> [--output-json <file>]`
与`capability_ledger_gate.py --project-root <project> [--output-json <file>]`。
gen默认写spec/execution/capability-manifest.json，非空声明与义务全覆盖后可列pending；
缺规范源码时明确pending canonical evidence，不声称已实现。gate默认pending失败，重新派生
真值，已有manifest只对账摘要。input_digest含合同、计划原字节及工具contract_revision；
source_digest另含本轮已声明模块main/ets证据原字节，不能将计划摘要冒充源码证据。
现代--emit-interface明确exit2，不生成空实现；正常现代消费链不需要这个选项。
legacy profile/help的原argv/stdout/stderr/exit透传不改。

一次性pipeline的stage_runtime同时写gen/gate适配器，使用同一模型；失败保留非零、
passed=false、summary.FAIL/WARN与findings.kind。其它13-detector语义与原finalize引擎不改，
不制造CONVERGED。完整原应用pipeline/编译/运行仍各凭实际证据，不由本静态门替代。
全部结果runtime_verified=false，不能据此认领行为或视觉完成。

普通checkout可执行的完整不同命名示例在tests/test_capability_contract_v2.py：
`python -m unittest discover -s tests -p test_capability_contract_v2.py -v`。
真实C7集成另用显式HMIGBOT_C7_SOURCE冻结快照；未提供时明确skip，绝不报已验证C7。


### framework-created两个必要模式

框架能力slot为空且无任何产品侧同path+symbol人工new。导出class实际extends的别名
须从正确SDK具名import解析，不接受同名本地类、目录标签或注释：

- `@kit.FormKit`的`FormExtensionAbility`：在所属已声明模块的module.json5中，
  module.extensionAbilities恰有一条srcEntry精确指向该源，type严格为form。
- `@kit.AbilityKit`的`InsightIntentEntryExecutor<T>`：支持实际`<void>`等单一具名类型参数；
  同一个class必须实际使用由该SDK导入的`InsightIntentEntry`装饰器（支持别名），并在
  resources/base/profile/insight_intent.json的insightIntentsSrcEntry中恰一条srcEntry精确匹配。

srcEntry允许规范`ets/...`或`./ets/...`，不按basename/大小写/类名猜注册。
消费的module/profile JSON原字节与build-profile.json5均进入source_evidence/source_digest；
更改/删除注册、错srcEntry/type、假SDK基类/装饰器或人工new均非零。其它framework基类、
复杂未支持generic/JSON5写法明确unsupported；当前读取JSON-compatible JSON5，不执行SDK。
规则依据本轮本机SDK具名导出及基类定义，不声称所有SDK版本或运行时发现/权限均已验证。


表达式证据不会比较被lexer遮蔽的字面量内容：合同中的字符串/模板等表达式或常量布尔/
数字guard明确unsupported，不能把if(false)登记为绿色初始化。规范表为静态只读映射：
属性写入/删除、整表别名/传递或未支持的动态键非零，不凭初始字面量掩盖之后修改。
构造链只接受规范变量参数；复杂alias链/反射/未解析构造器及未声明的调用控制包装均不算证明。

静态路径证明的保守边界（C31定向修正）：注入构造器只支持简单命名类型参数和直接的
`this.field = parameter;`序列；分支、提前返回、参数替换或字段再次写入明确非零。
boolean-state的成功清空必须是try成功块中的直接语句，所声明错误字段只能在该清空与
对应catch各写一次；其它直接/复合/更新写入（包括其它成员内写入）不支持。catch必须
结束该方法，finally及未理解出口明确非零。规范表slot的复合赋值、前后更新、delete与
带括号的写目标同样拒绝；只读访问不受影响。这些限制是受限源码静态检查，不是完整AST。

词法位置只用同一lexer的源码字符区间区分真实相邻`!=`/`!==`比较与非空断言后
分离的`! =`、`!/*注释*/=`或换行赋值；后者不能冒充比较绕开规范表写保护。
原token的value/line/literal及相等语义保持，新增位置元数据也进入工具合同revision。
