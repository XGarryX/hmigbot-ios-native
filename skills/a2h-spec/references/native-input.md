# 共享原生源输入

这是下游 Garry 指令到 Git 源合同的路径适配，不新增解析器、配置选择或规格门禁。

先读取 `ios-source-analysis/SKILL.md` 及其 `references/harness-v2.md`、
`references/native-facts.md`、`references/source-semantics.md`。正式规格按本技能的
`native-authoring.md`、`spec-delivery-contract.md`、`artifact-contracts.md` 和
`source-responsibility.md` 执行，事实与义务只由原工具生产。

工程根由 `hmigbot_ios.native_pipeline.context(project)` 读取本项目 `.migbot/config.json`。
下游源码读取统一使用 `hmigbot_ios.execution_source.Source(source_root, project)`；
它重新校验 Git facts、当前源摘要、选定 target 和实际配置，并消费同一官方 SwiftSyntax
证据。条件视图缺失、未知或过期时停止相应判断，保留错误和恢复条件。

不从目录名、类型后缀或关键字搜索结果推定页面、产品范围或可达性。沿真实 App/Scene、
AppDelegate、SwiftUI/UIKit 导航、IB、URL/推送处理、后台任务和已选扩展核对正式源锚点。
配置查询、静态 outline 和源代码分析各自保留证据边界，不能声明设备、视觉、编译或业务等价。

执行阶段交接见 `a2h-run/references/execution-boundary.md`。禁止桌面接管、无关应用和系统授权设置操作；
指定测试应用/模拟器的截图、控件查询和固定回放按已确认范围执行，Preview 仅作组件证据。
录屏、未指定个人真机和范围外操作不在截图许可内；没有真实结果的观察保持未知，不伪造通过。
