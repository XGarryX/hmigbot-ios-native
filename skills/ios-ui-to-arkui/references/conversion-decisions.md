# 原生 UI 语义到 ArkUI 的决策顺序

| iOS 输入 | 必须保留的事实 | 目标实现方向（需核验 API） |
|---|---|---|
| VStack/HStack/ZStack | 子视图顺序、对齐、间距、条件 | Column/Row/Stack 与目标布局约束 |
| List/ForEach | identity、选择、更新与复用 | List/Repeat 等；显式稳定键 |
| @State | 持有者、初值、身份重置边界 | 页面本地状态；按目标状态版本实现 |
| @Binding | getter/setter、回写目标与校验 | 参数下传+事件上抛；保留单一真值 |
| StateObject/ObservedObject/Observable | 创建/借用、共享引用、销毁边界 | 明确模型 owner；不是装饰器名字替换 |
| Environment | 注入值、覆盖子树、依赖 | Provider/Consumer 或明确参数；保持作用域 |
| task(id:)/onAppear | 重启、取消、重入、副作用 | 显式任务/生命周期适配；防旧结果覆写 |
| NavigationPath/sheet(item:) | 路由值、目的地分派、dismiss | Navigation/NavPathStack 与呈现状态模型 |
| UIViewController | containment、出现/消失、Scene | 页面/组件/生命周期适配对象 |
| Auto Layout | 优先级、relation、intrinsic size | 布局规则与条件；不能只拷固定像素 |
| IB outlet/action | 连接 ID、实际 handler、参数 | 组件字段/回调和真实 VM 接线 |
| delegate/data source | 弱引用、调用顺序、复用状态 | 接口/事件适配、显式 owner 与注销 |
| Representable/HostingController | make/update/dismantle/Coordinator | 拆分双边生命周期与反馈环 |

`padding().background()` 与反序效果不同；保存原链并验证目标边界，而不是全局排序属性。
源 nil/Optional、枚举 associated value、Swift 值复制、Objective-C nil message
在 UI 状态里也可能影响分支，类型适配不能省略。
系统默认外观随系统版本变化，截图注明版本/trait；目标默认样式不能当视觉等价证明。
视觉不等价走 fix 记录，平台行为不等价走 decision，未知源行为回源分析。
