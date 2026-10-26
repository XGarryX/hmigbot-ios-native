# iOS 到 ArkUI 的语义接缝

从事实出发选择目标实现，不能按 API 名称一一替换。每个接缝形成 fact→decision→task→AC→observation 的映射，源 unknown 不能由目标代码“补齐”。

| 源特征 | 实施检查 | 独立验收 |
|---|---|---|
| @State / StateObject / ObservedObject | 明确谁创建、持有、观察；ArkUI V2 @Local/@ObservedV2/@Trace 不自动等于源生命周期 | 初值、父重建、身份变化、重复进入与销毁 |
| Binding | 上行写回与下行刷新；选择 @Param/@Event 或受控接口时保留单一 owner | 子组件修改后父与兄弟读到同一状态 |
| Environment | 注入范围、缺省值、覆盖关系与响应更新；不擅自扩大为全局 | 两个作用域隔离和更新 |
| ForEach / id | 稳定 key、增删重排、身份变化时的重置 | 交换位置不串状态，换 id 按源重置 |
| modifier | 保留 padding/background/frame/clip 的顺序效果，token 顺序只是线索 | 两端实际尺寸、点击区、裁剪与安全区 |
| .task(id:) / Task / actor | 进入、id 改变、离开时的启动取消；过期响应隔离、线程约束与错误传播 | 快速切页、重入、取消和乱序完成 |
| Navigation / sheet / UIKit present | 参数、栈、返回值、取消、模态和恢复；NavDestination 生命周期与源回调时机分别核对 | 真实入口到态、返回后状态及再次进入 |
| UIKit controller / delegate | 创建/包含/出现/离开/释放、weak 接收者与回调次序；不全塞进 aboutToAppear | 重复进入、系统打断与销毁后回调 |
| Auto Layout / IB | 约束关系、优先级、intrinsic size、hugging/compression；读取程序覆盖后的布局 | 长文、多语言、大字体及不同容器尺寸 |
| Optional / value-reference / ARC | nil、空值、默认值、错误分别建模；值复制与对象共享、弱引用清理单独设计 | 缺失/零/false、复制后修改、取消及释放 |
| 持久化 / API | 保存→重读→业务生效；请求→响应→错误/权限/恢复的真实契约 | 独立协议样本与实际观察 |

每个页面任务必须列明输入状态、事件、反馈、参数和清理；业务接口与共享接线由计划 owner 提供。空 handler、静态假列表或目标硬编码预期均不构成行为实现。

需要查目标 API 时使用 arkts-knowledge-verifier/hmos-sdk-docs，核对真实 SDK 版本。源语义参考 Apple StateObject、task(id:) 文档；目标参考 Huawei V2 和 NavDestination 生命周期文档。只有实际读过的资料写入 provenance，不能伪造官方 skill 或工具执行。
