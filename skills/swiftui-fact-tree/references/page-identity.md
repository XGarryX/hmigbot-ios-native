# 原生页面与真实到态身份

静态 canonical page ID 不是设备运行时标识。SwiftUI 中同一宿主可承载多个状态页面，UIKit 中同一控制器也可显示不同业务状态；不能只凭宿主类名判断到达目标状态。

真实观测优先用足以区分状态的内容、选中 Tab、模态、稳定可见标识与明确前置态。accessibilityIdentifier、SwiftUI .id、ForEach key、restorationIdentifier、IB object ID 不等价。没有真实设备/Simulator 材料就记录 DEFERRED，不伪造层级、截图或已点击结果。

内容签名可保留 positive/negative/selected_tab/kind；动态文本、滚动离屏、共享宿主元素必须去歧义。视觉 alias 只用于观测对齐，不能合并真实导航节点或证明它们已到达。不要通过修改源 App、加隐藏入口或探针来制造真值；任何可选观测工具的使用都需要实际可用且如实记录。
