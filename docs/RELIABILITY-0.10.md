# 0.10.0 可靠性工作流

本版将准备、模型解释、实施和独立验收分开记录。脚本的成功退出只表示该命令完成；候选、静态覆盖、构建成功和应用等价分别有自己的证据。未知、未支持及未验证项目保留在验收分母。

## 新工程准备

源与目标必须互不包含。以下在发行包根执行；安装后脚本位于工作区 `.hmigbot-ios/plugin/scripts/`。

```powershell
python scripts/a2h_ios.py init --source 'D:/Projects/sample-ios' --project 'D:/Projects/sample-harmony'
python scripts/a2h_ios.py source-analysis --project 'D:/Projects/sample-harmony' --apply-scaffold
```

`source-analysis` 校验或首次建立源索引、初始化 v2 harness、采集 facts/obligations/literals、派生规格候选。它返回小回执，完整产物留在工程内：

| 产物 | 用途 |
| --- | --- |
| `spec/baseline/ios-source-index.json` | 内容摘要与源文件分母 |
| `spec/baseline/ios-facts.json` / `ios-obligations.json` | 机器信号与待审义务 |
| `spec/baseline/literal-ledger.json` | 原始字面量与未解析动态表达式 |
| `spec/reports/derived/spec-scaffold.json` | 完整的规格候选及内容 |
| `spec/reports/derived/spec-authoring.json` | apply 后可继续填写的源绑定编写表单 |
| `spec/reports/derived/source-analysis.json` | 各阶段状态、摘要、计数及失败原因 |

默认不 apply；`--apply-scaffold` 只补齐缺失的规范候选文件。apply 重算当前 canonical 候选，拒绝改内容、外来文件、过期源码及 F-ID 冲突，已有正式规格不能被覆盖。候选没有业务 AC，`spec_complete`、`behavior_verified`、`enterable_plan` 均为 false。调用者必须读源码和候选未知项，完成真实特性归类、源语义、目标合同、AC、覆盖、专业资料审阅及独立真值。

只需要候选时：

```powershell
python scripts/a2h_ios.py spec-scaffold --project 'D:/Projects/sample-harmony' --output 'D:/Projects/sample-harmony/spec/reports/derived/spec-scaffold.json' --brief
python scripts/a2h_ios.py spec-scaffold --project 'D:/Projects/sample-harmony' --apply 'D:/Projects/sample-harmony/spec/reports/derived/spec-scaffold.json'
```

有执行计划时，本入口拒绝改动基线。源码改变必须保留旧索引，走已有 `facts`、`source-refresh --review` 和受审 `replan` 流程；相同大小/mtime 的内容变化同样失效。

## 文档与覆盖检查

中文和英文 F-ID 主文档使用同一可读发现规则，addendum 归属于主文档。原 vendor 仍决定 divergence/decision-ledger 的业务规则；临时 ASCII 派生视图只桥接命名限制，索引映射回真实路径。重复身份、孤立 addendum、实际消费数量/对象集不一致会失败。

默认拒绝零主文档及主文档无 AC。`--allow-empty` 只允许明确不适用的零主文档范围；它不能让有主文档的零 AC 草稿成为 PASS。索引输出不能覆盖输入、baseline、Markdown 决策账本或链接到它们的文件。

coverage 额外核对 AC 所属 feature 的源锚点，以及精确共享合同引用的消费者边界。App 与 Widget 的提取问题按稳定的项目、target、配置及 issue code 分别跟踪；新的 target 身份不会继承旧的歧义 path-only 决定。文件归属检查仍不证明任意自然语言断言真实。

同步 Xcode group 仅支持显式目标关系及可验证例外的保守子集；未知 flags、phase 例外、外部/生成文件与不明确路径继续阻断。项目声明范围不提升为实际 compiler membership 或 `#if` 生效分支证明。

Xcode 云采集在真实 device-build 后、清理 DerivedData 前，从 SwiftFileList 与构建日志采集 `source_build_membership`。selected-build 消费新合同需重放原始记录并检查完整性、成员内容摘要、选择身份及清单一致性；`incomplete`/`unresolved` 不可缩小源分母。调用者提供的 scheme/configuration/SDK/target 集与采集矛盾时拒绝。源图钉住 manifest、membership 的摘要和 selection；构建成员记录仍不证明 `#if` 分支、运行行为或构建真实性。旧版仅含 `source_files` 的无版本合同继续兼容，不能升级成新合同的完整证据。

facts 对每个当前文件只保留一份 bytes/text/lines，首次读取即核对快照摘要，token 与 snippet 使用同份内容，避免读取期间 A→B→A 后事实错绑。provider 运行使用原子独占 attempt，成功/失败原件分别保留；实际消费的配置与输入固定到临时副本，副本不进入工程证据。外部工具/SDK 身份尚无法完整证明，因此本版不自动复用任何 provider 成功结果；不把配置路径相同当作工具相同。

鸿蒙 `build-target` 保存原始日志及 `diagnostics.json`，并在 `build.json` 钉住诊断摘要。退出码为 0 但同时有错误/失败日志时拒绝构建 PASS。单独采集的日志可使用 [诊断入口](harmony-build-diagnostics.md)；建议只用于定位，不自动修改签名或应用。当前规则仅经合成日志检验，真实项目日志需另验。

## 用量与时间账本

在完整迁移的首次必要工作之前启动，直到构建、修复、等待及独立验证全部结束后再完成。开始前的工程目标准备与必要基线工作也应纳入计时范围。

```powershell
python scripts/a2h_ios.py usage-start --project 'D:/Projects/sample-harmony' --run-id 'sample-run-001'
python scripts/a2h_ios.py usage-record --project 'D:/Projects/sample-harmony' --input 'D:/Projects/call-usage.json'
python scripts/a2h_ios.py usage-summary --project 'D:/Projects/sample-harmony'
python scripts/a2h_ios.py usage-check --project 'D:/Projects/sample-harmony'
python scripts/a2h_ios.py usage-finish --project 'D:/Projects/sample-harmony' --run-id 'sample-run-001'
```

默认账本为 `spec/reports/derived/usage-budget.json`。可用 `--ledger` 指向 derived 子目录下同名文件，为新运行保留独立账本。开始拒绝覆盖；完成后调用记录不可追加。默认运行额度 19.9M，20M 严格不通过，时间上限 7200 秒。运行中 `usage-check` 为 UNKNOWN/退出 3；完成且证据充分才 PASS/退出 0；明确超限为 FAIL/退出 2。0.11.0 的 `can_continue` 同时考虑显式在途预留；它仍不会自动为未来调用估算/预留。见 [显式预留与结算](USAGE-RESERVATIONS.md)。

调用输入示例（用量为合成示例）：

```json
{
  "call_id": "worker1-attempt1",
  "run_id": "sample-run-001",
  "stage": "convert",
  "agent": "worker1",
  "provider": "openai",
  "attempt": 1,
  "normalization_mode": "openai_responses",
  "raw_usage": {
    "input_tokens": 100,
    "input_tokens_details": {"cached_tokens": 40},
    "output_tokens": 20
  }
}
```

本例共 120 token，缓存已包含在 input 内。Anthropic、canonical subset/separate 及 MultiCA 聚合使用各自明确的合同。reasoning/image 子集不重复相加；每个 agent、失败尝试和重试都计入。重复 call ID 只有原始用量及身份全部一致才幂等；冲突拒绝。

未报告用量须用 `raw_usage: null`、`normalization_mode: "unreported"` 保存为 UNKNOWN，不能按字符估算后通过。MultiCA 要显式确定 input 是否包含 cache，并保留 unreported task 数量。聚合与其组成调用不能同时记账；调用覆盖的完整性仍需运行编排器/独立验收核对。账本 PASS 仅说明已提交的用量证据符合预算，不认证 App、规模或遗漏调用。

派发新批次时可显式连接同一运行账本：

```powershell
python scripts/a2h_ios.py next-batch --project 'D:/Projects/sample-harmony' --usage-ledger 'spec/reports/derived/usage-budget.json' --usage-run-id 'sample-run-001'
```

两个选项必须同时提供。调度器在原 `next_batch` 更新控制状态之前，核对账本的工程和运行身份，并检查已登记用量、当前耗时、时钟及结束状态；未知、额度耗尽、超时或已结束均拒绝新派发。`land-results` 仍可收回已有工作的结果。此连接按次显式选择，未选择时保留旧调度行为；调用者须在每次 `next-batch` 传入这两个选项。它不采集宿主遗漏的调用、不自动预留并发调用额度，也不终止已经运行的模型请求；0.11.0 的显式usage-reserve/record/release由调用宿主接线，泛检查会考虑现有预留。

计时校验包含墙钟、单调钟、启动及主机身份，结束后仍复验身份。内部计时证据不一致会拒绝或保持 UNKNOWN；无法确认启动身份的平台不能伪造时间 PASS。缺失真实模型用量的订阅工具调用须保持未知，订阅额度充足不等于 token 目标达标。

## 性能与应用验收

[分阶段超时与截止时间](runtime-timeouts.md) 可覆盖原调度的 60 秒和结构流水线的 180 秒执行限制，并保留超时前的原始输出。默认值兼容旧行为；这些执行保护与用量账本分别使用，不自动证明两小时达标。

宿主逻辑回归只覆盖给定用例，不能替代真机 UI、源执行或完整源分析链。

[规模基准](fact-capture-benchmark.md) 可在 100k、200k、500k 合成源码上测 facts 采集的时间、内存及逻辑读取量；它不运行模型、编译、转换或视觉/功能验收，不能外推端到端两小时/20M 达标。

真实应用必须固定源快照、工具提交、配置、构建产物及两端证据，逐页/状态和逐功能 AC 核验。源端只有截图时，未观察到的行为继续待验。100% UI、100% 功能、十万行两小时/20M、二十万行支持均为独立待测目标；本工具发行检查不替代这些应用验收。
