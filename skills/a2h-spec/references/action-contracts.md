<!-- when: 共享、异步、取消或分层副作用动作需要统一定义时读取；topics: 单源行为、完成边界、动作引用 -->
# 共享动作合同

## 适用与归属

先沿源代码确认动作，不从“取消”“清理”等词自动推断时序。涉及异步完成、取消/重入、UI和磁盘分层副作用，或被多个页面/功能消费的动作，在 `feature-base.md` 或拥有该行为的主feature中定义一次。公共设施归base，领域行为归对应F-ID；API清单和页面是消费者。

新项目使用 `.migbot/config.json` 的 `ios_harness.spec_contract_version=2`。feature YAML 声明 `action_contracts: required`；确无适用动作时写 `action_contracts: not_applicable` 和 `action_contracts_reason: <具体理由；源路径:行号>`，并以该feature的真实source_anchors支持。独立复核者确认适用性，机器只核验显式合同，不能证明分析者未漏判高风险动作。

## 定义形态

每个动作使用唯一精确标题，以下块的字段和枚举由随包 `schemas/spec-plan-artifacts.json` 及配套schema/解析器限定。块内是JSON，围栏info必须为 `action-contract`；不要改成普通说明文字或在use块内复制整个定义。

```action-contract
{
  "action_id": "F001-A01",
  "owner": "F001",
  "target": "ExampleService.cancel",
  "source_anchors": [{"role": "handler", "path": "Services/ExampleService.swift", "symbol": "ExampleService.cancel", "line": 20}],
  "immediate_effect": "按真实源码记录调用时立即发生的状态变化；没有变化明确说明",
  "completion_event": "记录实际完成回调/同步返回及其条件，不能把请求返回当作完成",
  "final_effect": "完成事件后可观察的状态与副作用",
  "failure_cancel": "源中的错误、取消、重入和清理；无分支时说明源依据",
  "scope": "active",
  "ac_ids": ["F001-AC01"]
}
```

示例仅示范格式；发行规格必须替换为真实路径、类型和具体行为。`action_id` 使用所属F-ID加 `-A` 和稳定序号，不回收。`owner` 是所属稳定F-ID（定义可在base共享节，归属仍是实际功能），`target` 是已在目标接口节声明的 `Owner.method`；不能在AC里临时创建接口。`scope` 仅取 `active`/`skipped`；跳过需要在正文链接排除依据和批准决策，不能把活动AC改为skipped规避验证。同步动作的 `completion_event` 应明确同步返回边界，不捏造回调。

`scope: skipped` 时块内还必须给 `skip_ref`（skip-list精确标题）和 `decision_ref`（decision-ledger精确标题）。本版只支持与既有reviewed Preview disposition相符的非产品排除；生产路径即使附有决定文字也继续blocked，不能藉该块减少facts/obligations覆盖分母。排除真实性仍需独立源复核。活动消费者不可引用skipped定义。

正文补充源事实、目标设计和批准差异，仍以Markdown为业务真源。公开接口签名/类型放服务层；复杂时序放可引用addendum，动作块保留确定的合同摘要与AC。不得在多个文件复制同一action_id后分别修改终态。

## 消费形态

消费者在YAML的 `contract_refs` 中声明精确合同路径/标题，再在相关交互/对接点附以下块；同文件内引用仍使用项目相对路径。`contract_ref` 必须指向含对应定义的精确标题，不是文件首页或计划文档。

```action-use
{
  "action_id": "F001-A01",
  "contract_ref": "spec/baseline/feature-base.md#示例动作",
  "ac_ids": ["F001-AC01"]
}
```

页面只描述该页面如何触发、绑定哪些显示状态及导航；功能AC写具体输入与观察。二者引用同一动作，不重定义其完成事件。消费者可以描述UI投影，但必须接受独立联读：例如“正在取消”可投影请求态，“已完成”必须有合同对应的完成证据。

## 生成和冲突处理

1. 先以源调用链划清即时效果、完成事件、最终效果、失败/取消，后确定唯一作者及公开目标接口。
2. 作者生成定义；页面/功能/API作者引用并核对参数、时点和AC。范围排除/批准差异同步更新主定义及所有引用，旧AC保留supersedes关系。
3. 独立复核者按 [内容复核](spec-content-review.md) 联读源码→定义→页面/功能→AC→排除/决策。机器通过只证明已检查的结构、引用和范围关系。
4. 冲突进入原 `spec/.a2h/open-findings.json` 对应检查节，由原owner修改，独立复查后重跑产生finding的检查；不新增第二套活动问题账本。

以下均应返修：页面写点击立即移除而定义写回调移除；UI清空被写作磁盘删除完成；active消费者引用skipped动作；两个定义争用同一ID；把unknown写成无副作用。句子是否同义、时间边界是否忠于源代码由复核者裁定，不能用字符串相同或关键词计数替代。
