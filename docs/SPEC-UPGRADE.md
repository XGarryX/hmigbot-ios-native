# 旧 Spec 诊断与候选升级

`spec-upgrade`帮助已有原生 iOS 项目定位旧格式和 profile 2 的增量要求，并提出可核对的格式补丁。它不是迁移验收，也不补写缺失的业务行为、目标接口或独立复核结论。正式 Spec、源门禁和 Plan 门禁保持有效。

## 先诊断，原项目零写入

在目标工程目录执行；工具位置使用安装后的本地 runtime：

```powershell
python .hmigbot-ios/plugin/scripts/a2h_ios.py spec-upgrade --project .
python .hmigbot-ios/plugin/scripts/a2h_ios.py spec-upgrade --project . --output spec/reports/spec-upgrade.json
```

默认只输出 JSON，不修改项目文件。指定`--output`时，只允许规范路径`spec/reports/spec-upgrade.json`或`spec/reports/derived/`下的 JSON，不能覆盖执行证据、baseline、配置、控制账本或项目外文件。诊断完成的退出码为0，报告内的 profile 检查仍如实记录 PASS/FAIL；退出码0不能解释为规格通过。

诊断器先物化源和目标的非生成文件副本，拒绝符号链接/目录链接，再只在临时配置中分别选择 profile 1和2。原配置不变。报告按以下口径归类，同一缺件保留两套规则来源而只登记一次：

| 分类 | 含义 | 处理责任 |
|---|---|---|
| `missing` | 缺少公共或页面产物 | 原作者补真实内容，不能创建空文件消除计数 |
| `legacy` | profile 1已能发现的问题 | 修正旧目标合同、行为或证据；保持稳定 ID |
| `v2_added` | profile 2增加的结构/内容要求 | 联读新模板与源代码补齐，不复制未经确认的示例 |

报告包含源摘要、原配置与 baseline/ref 输入摘要、保留的 feature/page/AC ID、两个 profile 的完整发现、候选补丁与需人工处理项。JSON格式见[升级报告 schema](../schemas/spec-upgrade.schema.json)。报告是独立诊断材料，不写入三份控制账本，也不更新`open-findings.json`。

## 候选只转换已存在且无歧义的信息

当前可提出以下候选：

- 页面 meta 的对象式`source_refs`转为`path:line`或行范围字符串。源文件/行范围必须当前有效，与既有`source_anchors`一致；对象中额外的已知证据信息保留在`extensions.legacy_source_refs`，既有源 hash 过期时不转换。
- meta 顶层的`presentation_evidence`、`non_product_ranges`、`limitations`归入`extensions`，原值保留。未知键、已有扩展值冲突保留人工处理。扩展仍是说明，不能替代正式源范围处置或门禁结果。
- 可见 AC 正式`源:… → 标:X`合同槽中，只有本功能或其显式共享引用已经声明唯一匹配的`Owner.X`时，才提出限定名称补丁。代码示例、普通文案和判字段不改；没有明确合同槽、声明或存在多个 owner 时，保留人工处理；不从 feature 名、文件名、页面名推断 owner。

候选不会创建缺失的章节、接口或行为，不改 feature/page/AC ID、AC勾选状态、页面 runtime、项目 profile、决定或验收状态。无法证明格式等价的部分进入`manual`，继续作为待解决问题。

## 显式选择并应用

先阅读报告中的`patches`，核对`operations`、原文件摘要、候选全文和`manual`。将实际报告里的候选 ID替换到命令中：

```powershell
python .hmigbot-ios/plugin/scripts/a2h_ios.py spec-upgrade --project . --apply spec/reports/spec-upgrade.json --patch UP-实际候选ID
python .hmigbot-ios/plugin/scripts/a2h_ios.py spec-upgrade --project . --apply spec/reports/spec-upgrade.json --all-candidates
```

`--patch`可重复，`--all-candidates`表示明确选择报告中的全部候选，两者互斥。应用必须给出一种选择；诊断不能携带选择参数；应用不接受`--output`。应用结果输出到标准输出。

应用前重新读取源与全部绑定输入、重算当前合法候选，逐项比对候选全文和操作。源、配置、规格或工具合同变化都会使旧诊断失效；新增/删除输入也会被检查。被篡改的候选、重复/不存在的候选 ID和非允许路径均拒绝，所有选择先完成检查再开始写入。写入范围只包括 baseline 下的功能 MD和页面 meta。AC目标的局部修改保留原 BOM、换行和勾选状态。

成功返回`applied_requires_review`，不返回规格或行为 PASS。一批候选应用后输入已经变化；如需处理下一批，重新诊断并使用新报告，不能复用旧摘要。

## 补内容、复核、正式过门，再重新规划

1. 重新诊断，确认实际消除的问题与剩余`missing/legacy/v2_added/manual`。原作者沿真实源入口补行为、错误/取消、状态生命周期、目标接口、共享引用和页面接线；保留原稳定 ID与真实未知。
2. 由独立复核者联读源、公共合同、功能、页面、AC和排除范围。格式转换不替代独立源/内容复核，新增字段也不能补造运行证据。
3. 确认迁移目标和当前授权后，由用户或已获授权的施工步骤**显式**选择项目`.migbot/config.json`的`ios_harness.spec_contract_version`。工具不自动从1切到2，也不修改既有 JSON载荷版本。仍使用1时，只能声明当前 profile 1的真实结果。
4. 运行正式 Spec与源门禁，重新生成匹配该 profile 的 indexed MD计划和 typed request，再运行 Plan检查：

```powershell
python .hmigbot-ios/plugin/scripts/a2h_ios.py spec-check --project .
python .hmigbot-ios/plugin/scripts/a2h_ios.py source-check --project . --harness
python .hmigbot-ios/plugin/scripts/a2h_ios.py plan-check --project . --input domains.json
```

正式命令的非零结果仍阻断后续阶段。`source-check --harness --report-only`可用作只读调查，不更新既有发现或报告；发现失败时仍返回非零，不能用它豁免正式门禁。普通兼容`source-check`不能替代 harness 检查。

5. 首次计划通过后才能使用`plan-ir`创建控制产物；已有冻结计划发生合同变化时，按原协议补`replan_review`并显式执行`replan`。先收口已有 in-flight任务，不直接修改原控制账本。历史 PASS、旧回执和旧编译/行为报告不会因升级继承为当前成功；重新运行各自需要的验证。

本辅助工具不替代完整迁移流程。阶段输入和原调度协议继续见[Spec/Plan合同说明](SPEC-PLAN-CONTRACT-0.9.md)与[Plan交付合同](../skills/a2h-plan/references/plan-delivery-contract.md)。
