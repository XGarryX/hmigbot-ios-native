---
name: swiftui-fact-tree
description: 从 SwiftUI App/Scene、导航、Tab、模态、状态与组件源码生成原格式 fact-tree，保留真实类型、参数、Binding、任务和取消语义。
metadata:
  title: SwiftUI 源码 → fact-tree（原生源码分析器）
  type: domain
---

> **.33 共享事实输入**：源分析可用 runtime 的 `scripts/ios_visual.py facts` 生成当前 target/Release 语法脚手架与 native facts；随后仍须按本 skill 补页面/fragment 分类、行为、前置条件与功能账并过原数据闸。脚手架不是 runtime dump，也不是已验证的功能 oracle。详见 [原生视觉源流程](../arkts-visual-verify/references/native-xcode-source.md)。


# SwiftUI Fact Tree

按 [原生输入协议](../a2h-spec/references/native-input.md) 接原生源，保持 1.5.2 的七个生成阶段及原同构树 schema；先读 `references/fact-tree-schema.md` 与 `references/enrichment-parity-spec.md`。

0. 预扫真实 SwiftUI 视图、App/Scene 根与导航方言：NavigationStack/path、NavigationLink、TabView、sheet/fullScreenCover、状态路由、UIKit 桥接。无标准导航时沿实际根视图/状态分支，未知处写 notes。
1. 源页面建模：只把实际根、路由、Tab/模态目的页作为页面，普通 View 留作组件，保持 activities/fragments 历史 payload。
2. 导航图：触发控件、前置条件、目的页、参数、返回/取消全部从源码链读出；fan-in 只共用节点，不复制页面，不发明边。
3. 组件：扁平列表 + parent_id + triggers；保留 Binding、状态所有权、ForEach ID、modifier 次序、异步 task/cancellation 语义。
4. 功能聚类、应用元信息、stats：按原树 schema 装配，不另建 obligation/AC 对照表。
5. 原 HARD 自检：复用原 schema/connectivity/parity 检查；源语法条件按 SwiftUI 真实构造检查，数据关系约束不变。
6. 可选页面签名：供真实视觉比对，缺设备不伪造坐标或截图。
7. 富化：按原 enrichment parity 补 preconditions/navigation_contract/inbound_triggers/reach_paths，交原 visual-verify 消费。

references 使用原公共数据关系；源识别以 SwiftUI 和原生输入协议为准，不运行不支持原生语法的识别器。共享 schema 不改变源码事实。
