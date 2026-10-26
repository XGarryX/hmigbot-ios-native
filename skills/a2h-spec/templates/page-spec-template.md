# page_0001 — 页面名称

```yaml
source_platform: ios
spec_contract_version: 2
source_languages: [swift]
ios_frameworks: [swiftui]
source_anchors:
  - role: view
    path: Screens/ExampleView.swift
    symbol: ExampleView.body
    line: 10
```

## 页面与范围
真实入口、前置条件、所属 target/feature、目标页面和稳定 page ID。

## iOS 原生语义
引用 ios-semantics.json 同 page ID，并展开与迁移有关的事实。
SwiftUI：body 组合/条件/身份、modifier 顺序、状态所有权与 Binding、Environment、
task 取消、NavigationPath/sheet。UIKit：控制器层级/生命周期、约束优先级、
outlet/action/delegate 与程序化覆盖。混合页面分别列桥接边界。

## 页面结构与视觉
先按真实组合给页内节点ID，逐行填写以下四表；四表是固定核心提纲，领域细节可加小节。
源码事实与截图观察分开；Preview 不作为运行初始态。无适用资源/分支等给有源证据的not_applicable；unknown写原因与补证步骤，并阻断受影响实施。不得用模板空行、只有表头或“参考源码”交付。

## 组件层级
| 节点ID | 父节点 | 源控件/条件 | ArkUI组件 | 内容/事件 | 源证据 |
|---|---|---|---|---|---|

记录根节点、子组件、覆盖层、循环身份和条件分支。ArkUI组件给具体候选及保留约束，不能只写“布局容器”；无法确定的映射回流。根的父节点用 `-`，其余父节点必须指向本表节点ID，不伪造源XML树。

## 布局约束
| 节点ID | 尺寸/布局/安全区 | 条件/优先级 | 资源引用 | 源证据 |
|---|---|---|---|---|

包括布局轴/对齐/间距、源尺寸或内容测量、伸缩与截断、safe area、modifier顺序；UIKit保留relation/multiplier/priority及程序覆盖。trait/动态字体/深色/RTL/无障碍按源适用条件展开。源没有固定尺寸就说明真实测量关系，禁止猜通用数值。

## 状态接口
| 源状态与类型 | 初值/所有者/生命周期 | 读写者 | UI 影响 | 目标 Owner.state 与类型 |
|---|---|---|---|---|

## 交互与导航
| 前置态 | 事件/入口 | 状态与副作用 | 导航值/返回行为 | 源证据 | owning_feature |
|---|---|---|---|---|---|

异步/取消/跨层副作用/共享动作按 [动作合同](../references/action-contracts.md) 用action-use引用唯一定义，并在YAML声明contract_refs。页面只补充触发控件、显示投影和导航，不重新定义服务完成时点。

## ArkUI 映射决策
| 源机制 | 目标实现 | 约束/差异 | 源证据 |
|---|---|---|---|

按保留行为解释具体组件/状态/路由映射；原语义留在前文。无法等价引用decision ID、已批准替代和验证场景；没有证据的目标API不能标known。
目标状态与公开事件接口在 spec 明确；跨页公共合同用 contract_refs 精确引用。无状态页给源依据，不能用 stateless 隐藏真实状态。

## 资源引用
| 资源ID | 类型 | 目标引用 | 源证据 |
|---|---|---|---|

源文件、asset variant/scale、字符串/复数、符号和字体逐项引用。目标引用写明确资源名或Stage 0转换责任；规格阶段不能伪造已完成的resource-mapping。无适用项用not_applicable及源依据。

## 资源与运行证据
源文件、variant、字符串/复数、符号、字体。截图/录像若未采集明确 not_run。

## 验收与接线
页面检查与关联 F-AC；真实 handler 到目标 ViewModel/Service 的接线责任归 owning_slice。

## 模板使用检查（交付前删除本示例说明）

合格：根容器与条件子树有父子关系；条件来自实际状态；每个可见节点有布局来源、具体ArkUI映射及源锚点；Binding追到真正Owner；必要资源有引用；取消操作引用共享动作。

反例：“Column中展示标题和列表，遵循iOS风格”“布局详见截图”“其余条件按源码实现”。这些不能回答节点何时出现、尺寸从何处来、谁写回状态和哪个目标组件承载，标题和表头齐全也应退回作者补充。
