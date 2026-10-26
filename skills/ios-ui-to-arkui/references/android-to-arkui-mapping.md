# 原生 UI 映射

| iOS 来源 | ArkUI 意图 | 必须核验 |
|---|---|---|
| App/Scene、NavigationStack、UIViewController | 页面/导航容器 | 路由、参数、返回、窗口与生命周期 |
| State/Binding/Observable、Combine | 按计划的 V2 状态与事件 | 所有权、双向更新、异步取消与可观察结果 |
| VStack/HStack/ZStack、UIKit 约束、Storyboard/XIB | Column/Row/Stack 与真实布局约束 | modifier 顺序、intrinsic size、优先级、safe area、动态尺寸 |
| List/ForEach、table/collection cell | List/Grid/行组件 | 稳定 identity、复用、选择、分页、空态 |
| sheet/alert/UIMenu、presentation controller | 模态/弹窗/菜单 | 呈现绑定、关闭/取消和结果回传 |
| Asset Catalog、SF Symbols、字体/颜色变体 | 原资源映射与目标系统图标 | 实际尺寸、语义、颜色与深浅色变体，不能编造统一倍率 |

点数与 vp 需结合实际设计和约束核验；不能只换单位。目标 width(100%)+水平 margin 的溢出风险按原规则处理：用父 padding 或有依据的宽度表达式。静态 outline 不等于设备视图树；复杂绘制/媒体/后台接缝交计划绑定专项技能，收尾及真实编译按 a2h-execute。
