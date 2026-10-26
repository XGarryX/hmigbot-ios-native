# Apple 官方能力与实际使用状态

核查日期：2026-10-24。Apple Xcode 27 提供可导出的 agent skills，官方 WWDC 演示
`xcrun agent skills export --output-dir <path>`。外部 agent 可通过 `xcrun mcpbridge` 连接 Xcode MCP，
需要 Mac、Xcode 打开工程并启用 Intelligence 中的访问选项。

- 官方 skills：从用户自己的 Xcode 导出，记录 Xcode 版本、原目录和文件 hashes；
  本包不把第三方镜像标成官方发布，也不伪造 Apple SKILL.md。已导出的 Markdown
  可辅助理解对应框架；并不构成 iOS→HarmonyOS 迁移能力或源行为真值。
- Xcode MCP：只有当前宿主实际连通且工具返回成功才记 used；Windows 上未连通时
  记 unavailable。配置示例不代表已接入；普通云端构建也不等于持续 MCP 会话。
- SwiftSyntax：Swift 官方语法解析库；本包 providers/swift-syntax 是自编调用适配器。
- SourceKit-LSP/Clang：按实际配置、实际输出记录，不能把文档提及算成使用。

本包默认四类源分析 skill 由 HMigBot-iOS 编写。将每次实际读取的官方资料/skill、
可调用工具、执行状态、版本及 evidence 写 `spec/ref/ios-analysis-provenance.json`。
没有拿到官方 export 时 `apple_skills.status=not_loaded`；不阻止已有源文件分析。

官方依据：
- https://developer.apple.com/videos/play/wwdc2026/278/
- https://developer.apple.com/documentation/xcode/extending-and-customizing-agents
- https://developer.apple.com/documentation/xcode/giving-external-agents-access-to-xcode
- https://www.swift.org/documentation/source-code/

0.13.0 的自动选择、逐步执行与权限边界见 [自动编排协议](auto-orchestration.md)。官方技能与只读 MCP 优先，实际不可用时显式降级；设备远程控制不在默认调用范围。


## 0.13.1 实际消费与保留边界

SwiftParser/SwiftSyntax 产物在 facts 提取前采集并固定；Swift 词项、字符串/正则边界、声明及继承结构、字符串与数字静态解码被原事实/字面量/候选/专业审阅/Preview 门禁消费者实际读取。语法错误阻断该原生产物的发布，不能回退 Python 词法后宣告原生通过。Python 仍把语法信息映射为迁移信号和义务，symbol_binding 保持 unresolved；语法库不能证明跨模块调用绑定、宏展开或运行行为。明确 static 模式与旧无 lexical 协议的外部 Provider 维持兼容备用，收据明确 Python fallback，不算官方解析。

官方 skill 资料加载与实际应用分开：Apple 条目的 expertise-review 每条观察必须带 official_basis（path、sha256、section、application）并绑定真实源行。没有覆盖主题的官方 skill、MCP 未授权、缺少所选构建上下文都逐项保留缺失原因。Xcode MCP 不可用时同类确定性工程读取使用已授权的官方 CLI；不自行启用全局 MCP 或操作界面。
