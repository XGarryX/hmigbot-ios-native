# 官方来源、可选能力与实际状态

## 0.7.0 实际新增接入（2026-10-12）

已随包固定三套第三方 MIT 资料：AvdLee SwiftUI/Concurrency、Axiom UIKit/内存主题。
expertise-plan/review 生成按主题清单与源审阅记录，source-check --harness 检查其来源和
当前源版本。真实文件与许可见 [第三方来源](THIRD-PARTY-NOTICES.md)，使用方法见
[外部接入规程](../skills/ios-source-analysis/references/external-expertise.md)。

新增 mcp-query stdio 客户端，支持 Serena、Xcode 和 SourceKit 类源读工具白名单、
版本协商、工具发现/分页、超时失败留档、原始响应/摘要与 known claim 引用检查。
当前测试只覆盖隔离协议服务；真实后端、Mac 工程配置与有效符号绑定未实测。
本版 MCP 输出保持 tool_response/unverified，不自动提升机器图为编译绑定或运行事实。
SwiftSyntax/Clang 的既有 facts --providers 保留；MCP 经独立采集入口保存可审阅证据。

下表保留 0.5.0 的 Apple 能力来源核查，不能把它的“未加载”理解为本版未导入第三方 skill。

核查日期：2026-09-29。默认迁移由本包原 a2h 主线执行，外部能力可提供附加事实。
“官方存在”“已配置”“已执行”必须分别记录，不能把链接或示例命令当调用成功。

| 能力 | 官方来源 | 本包状态 |
|---|---|---|
| Apple agent skills | [WWDC26：Modernize your UIKit app](https://developer.apple.com/videos/play/wwdc2026/278/) | Xcode 27 提供，官方命令 xcrun agent skills export；本次未导出/加载 |
| Xcode 外部 MCP | [Apple 文档](https://developer.apple.com/documentation/xcode/giving-external-agents-access-to-xcode) | 需 Mac/Xcode 打开工程并开启访问；本 Windows 环境未连接 |
| Agent 扩展规则 | [Apple 自定义 agents](https://developer.apple.com/documentation/xcode/extending-and-customizing-agents) | 作为环境配置依据，不作为应用行为事实 |
| SwiftSyntax / SourceKit-LSP | [Swift 官方源码工具](https://www.swift.org/documentation/source-code/) | 官方工具，不是 Apple skill；本包 provider 是自编适配代码 |
| Clang / LLDB | [Clang AST](https://clang.llvm.org/docs/IntroductionToTheClangAST.html) / [LLDB](https://lldb.llvm.org/) | 仅在实际 SDK/TU/运行上下文成立时采信输出 |

## 在具备 Mac/Xcode 时接入

先记录 xcodebuild -version 与 xcrun agent skills export --help，按当前 Xcode 支持的参数导出。
记录导出目录、文件哈希及来源，读取实际 Markdown 后按需使用；不自动以它的现代化建议修改源 App。
MCP 的官方 Codex 配置示例为 `codex mcp add xcode -- xcrun mcpbridge`；先在 Xcode 打开目标工程并启用访问。
连接是否成功以真实返回为准；普通云端编译任务不会自动成为当前 Windows 会话的 MCP。
这些操作是接入说明，本发行没有执行或伪装成功。第三方镜像不能冒充 Apple 官方分发。

每轮分析写 spec/ref/ios-analysis-provenance.json，记录实际读取的文档/skill、工具版本、调用状态和证据。
默认 `apple_skills.status=not_loaded`、`xcode_mcp.status=unavailable`，可继续静态源分析。

## 已保留的机械适配器

providers/swift-syntax 使用固定 swift-syntax 依赖解析语法；有效语义绑定仍取决于真实编译上下文。
providers/clang 处理实际 TU AST 与诊断；有 UIKit/Foundation 时需要 Apple SDK。
云端编译与 iPhone 签名路线见 [CLOUD-IPHONE](CLOUD-IPHONE.md)，工具清单不代表已在用户手机运行。
研究中的三方 MCP/Swift skills 和 Stars 仅是带日期的选型材料，不是运行依赖或官方认证。

Apple 目前提供的上述能力不等于现成 iOS→ArkUI 迁移器。源理解、spec、映射与目标实现由本包技能协作完成。
