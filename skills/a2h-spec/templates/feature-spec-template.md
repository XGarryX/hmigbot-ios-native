# F001: 功能名称

```yaml
complexity: complex
tier: core
depth: full
source_platform: ios
spec_contract_version: 2
action_contracts: required
source_languages: [swift]
ios_frameworks: [nonvisual]
contract_refs:
  - spec/baseline/feature-base.md#数据模型
source_anchors:
  - role: service
    path: Services/ExampleService.swift
    symbol: ExampleService.perform
    line: 20
```

## 范围
用户目标、target/extension、所有入口、页面和 feature-base 依赖。

## iOS 源语义
引用 ios-semantics.json 同 F ID，保留 Swift 或 Objective-C 的行为相关语义。
值/引用、Optional/关联值枚举、ARC、actor/Task/委托、错误/取消和资源生命周期逐项有证据。

## 数据流
输入 → 校验/转换 → 服务 → 持久化/副作用 → UI。写单位、值域、线程和失败路径。
HARD-DIV 的替代数据流引用 PD-ID，显式给跨边界转换责任。

## 源行为表
| 前态/输入 | 事件 | 条件/运算 | 后态/结果 | 错误/取消 | 源文件:行 |
|---|---|---|---|---|---|

## 动作合同
按 [共享动作合同](../references/action-contracts.md) 定义或引用适用的异步/取消/共享副作用动作。逐个区分即时效果、完成事件、最终效果、错误与取消，不重复定义公共动作。定义在公共合同的feature使用action-use并声明contract_refs。

确无适用动作时将元数据改为action_contracts: not_applicable，填写action_contracts_reason: <具体理由；源路径:行号>及具体源锚点；不能用N/A隐藏实际取消或跨层副作用。稳定action_id与AC一起供plan/execute/verify消费。

## 服务层（ArkTS 目标接口）
| 目标接口 | 输入/输出/值域 | 错误/取消 | 状态/线程/生命周期 |
|---|---|---|---|

写明确的 Owner.method 签名，或通过 contract_refs 引用已定义接口。公共目标合同在 spec 确定，plan 分配实施与接线责任。源签名留在源语义节。

## API 接口
引用 api-inventory 端点 ID、静态 method/path/protocol 和公共 auth。未知字段不猜。

## 实现映射（Source→ArkTS）
| 源机制 | 目标实现 | 数据/生命周期契约及依据 | 迁移分类 | 决策 |
|---|---|---|---|---|

## 状态管理
状态持有者、更新方向、共享范围、恢复与清理；区分源事实和目标装饰器选择。

## 对接点（与 UI 页面的接口）
page.handler ← ViewModel/Service；包含参数与结果，交 a2h-plan 分配唯一接线 owner。
写明action_id、调用参数、页面状态投影和返回/完成边界；公共行为仅精确引用，不因页面需要而改写服务终态。

## 验收标准
- [ ] F001-AC01 <单个可观察断言>　`源:<源符号> → 标:<目标方法>`　`判:unit | <输入与期望结果>`　`真:src:<源相对路径>:<行号>`

源真值从本功能已声明的 `source_anchors` 中选择真实路径和当前行号；按 [原生规格生成协议](../references/native-authoring.md) 交给 `spec-authoring` 渲染令牌。路径不匹配时回读源行为，修正真实归属或真值选择；不能为过门禁添加无关源文件、移动断言或改业务源码。

`标:`必须是已在目标接口/状态/实现映射合同声明的`Owner.method`或`Owner.state`，UI布局验收也要定位已声明的组件构建/渲染入口。例如先在公开接口表声明`CounterPage.render(): void`，再用`标:CounterPage.render`；只写`标:CounterPage`、源符号或未声明的目标会被阻断。此锚点用于施工追踪，不能把“render存在”当作布局或行为验收。

AC ID 稳定且不回收；主文件保留全部 AC。细节可移 addendum，但有 impl 指针。
独立真值也可用 test/trace/device；批准差异用 `决:PD-ID` 与 `真:decision:PD-ID`。
HARD-DIV 同时给 PD-ID、替代数据流、supersedes 旧 AC、新差异 AC；不自行批准替代。
