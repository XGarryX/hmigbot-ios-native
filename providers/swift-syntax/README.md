# Mac Swift source provider

当前发行版在 macOS 使用选择的完整 Xcode 自带 SwiftParser、SwiftSyntax、SwiftIfConfig。`hmigbot_ios.apple_tools` 负责官方工具发现、按工具链及源码身份构建小型 provider，以及校验缓存哈希；构建目录在安装归属之外。

- 原语法协议继续带 `protocol_version=1`，新增 `schema_version=2`，保留 `semantic_resolution=false`。返回 AST 声明、枚举、官方词法 tokens、字符串解码、UTF-8 位置和解析诊断。
- 条件请求协议 2 要求实际 `compiler_context`。查询通过 Apple swiftc 的 JSON AST 探针取得；生成的探针不含 App 实现，也不执行。SwiftIfConfig 在原始树上选择分支并生成位置不变的源码掩码。
- 历史协议 1 的 custom-boolean 模式只作内部兼容，不是 SDK/编译器语义能力。
- 未知或失败不能变成空成功。Xcode host 库是版本相关兼容接口；不将它描述为稳定 API。SwiftSyntax 的 SwiftPM 清单保留固定 604.0.0 作为源码来源参考，当前 Mac 入口实际使用的库版本取自所选 Xcode。

类型绑定、App 构建、签名、运行及行为等价不由语法 provider 证明。
