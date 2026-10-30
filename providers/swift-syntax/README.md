# SwiftSyntax provider

官方依赖：[swiftlang/swift-syntax](https://github.com/swiftlang/swift-syntax)。SwiftParser/SwiftSyntax 提供源准确语法树、词项边界、字符串/正则语法和字面量静态解码；不执行传入的 App，不解析完整跨模块类型绑定或证明运行行为。适配器由本工具维护。

原生 source-analysis 默认通过 xcrun 选择当前 swiftc 与同工具链的 SwiftSyntax/SwiftParser host 模块，使用优化编译（swiftc -O），显式指定 macOS SDK、独立 ModuleCache 和库加载路径。Provider 源码与二进制摘要进入配置；输出固定后供 facts、literals、候选、专业审阅和门禁回放消费。包中不分发本机验收二进制或 ModuleCache。

Package.swift 保留 Swift 6.0 / SwiftSyntax 600.0.1 的显式 SwiftPM 构建入口；使用其他工具链时先核对版本兼容性，不能把工具链 host 模块的验证宣称为该网络依赖构建已通过。显式配置例见 provider.example.json。

stdin 为 UTF-8 JSON files[{path,sha256,source}]；stdout 为 protocol_version=1、lexical_protocol_version=1。files 含声明、函数、变量、调用、属性、条件节点，以及带 UTF-8 范围的 lexical_items、解析诊断。完整字符串/正则表达式保持不透明，不能激活字符串内部的迁移规则；可静态解码的 Swift 字符串/数字交给官方 representedLiteralValue 接口，插值和无法求值的内容保留未知。

消费者验证源集合、原始文件摘要、位置、行号和产物摘要后再读取。原生解析错误阻断事实发布并保留原诊断，不能退回 Python 后把对应原生步骤记为通过。旧未带 lexical 协议的外部 Provider 和显式 static 模式保留有限兼容，收据明确 Python fallback。compiler_binding 仍 unresolved，宏展开、活跃编译分支和真正类型/调用绑定仍需要相应 Xcode/编译器证据。

0.13.2 的独立 analyze/generate 和候选入口也使用实际 SwiftParser；Python SwiftUI Parser 已删除。files.arkui_rule 是本工具维护的 Swift AST → 受限 ArkUI 规则输出，非官方迁移器；未覆盖 AST 明确 unsupported，语法错误不能生成草稿。lexical_items.migration_kind 由 Swift tokenKind 生成；旧协议缺该字段只用于证据兼容。独立调用的编译/解析原始日志写入宿主临时目录，进程内复用已编译适配器但不缓存源码结论。

0.13.3 会识别本工具 0.13.0/0.13.1 的已知适配器源码摘要。若旧配置没有自定义扩展，先核验原二进制摘要，再实际构建并消费当前本地源码适配器，保存 requested/effective 配置与源码/二进制摘要和原始 CLI 日志；不改写旧配置或旧产物。未知第三方源码不替换，已知旧配置带未知扩展则明确拒绝自动迁移。编译失败不回落到旧 Python Swift 解析并宣称新版消费完成。

0.13.4 增补 `VisibilityFacts.swift`，与 `main.swift` 一同编译。配置的 `provider_sources_sha256` 记录两个源文件摘要，`provider_source_sha256` 为该映射规范 JSON 的组合摘要；二进制摘要继续独立验证。合法旧单文件 Provider 继续用于原有能力；缺少新协议时，可选 visibility 输出 `needs_refresh`，不增加基本转换流程门禁。

每文件 `visibility_protocol_version=1` 表示包含渲染上下文的条件、动态 opacity、UIKit isHidden/alpha 赋值等语法候选。按钮动作与生命周期动作不会被当作渲染闭包；未知闭包保持 unresolved。WidgetKit 的 AppIntentConfiguration、StaticConfiguration、IntentConfiguration、ActivityConfiguration、DynamicIsland 和 DynamicIslandExpandedRegion 闭包槽位按公开初始化签名适配，见 [AppIntentConfiguration](https://developer.apple.com/documentation/widgetkit/appintentconfiguration)、[ActivityConfiguration](https://developer.apple.com/documentation/widgetkit/activityconfiguration)、[DynamicIsland](https://developer.apple.com/documentation/widgetkit/dynamicisland)。本机验收额外核对了安装 SDK 的公开 swiftinterface；库的语法树本身不提供重载解析，用户同名类型、自定义 builder、宏和未列明签名仍需语义复核。包内不分发 SDK 接口文件。

可选入口 `python3 scripts/ios_ui.py visibility <iOS源码目录> --project-root <迁移工程目录> --output spec/execution/source-ui/visibility.json` 实际消费已发布 Git facts 的 SwiftSyntax 产物与正式活动编译视图，不在 Swift 上重新运行正则。需先完成 source-analysis；输出严格限于调用者工程的 `spec/execution/source-ui`。meta/view 也从同一入口提供，view 只是调用点轮廓，不是运行时视图树。visibility 的 rows 是待复核候选；`semantic_resolution=false`、`runtime_observed=false`，不证明目标代码已经实现这些行为，也不证明运行时可见性。Objective-C 原有词法候选单独标注较弱证据，正式语义仍使用已有 Clang 链。
