# Phase 1b：原生网络与鉴权补扫

按实际 Xcode target、SwiftPM/CocoaPods/二进制依赖选择策略，不必把所有栈全扫。仅使用 Source 选定的 Release 文件与文本；发现候选后沿调用链确认，正则未命中不等于无行为。

| 技术栈 | 搜索起点 | 必须追踪 |
|---|---|---|
| Foundation 网络 | URLSession、URLRequest、dataTask、uploadTask、downloadTask、data(for:) | URL 组装、httpMethod、headers、httpBody、响应码、取消和回调线程 |
| Alamofire / Moya | AF.request、Session、RequestAdapter、RequestInterceptor、TargetType、MoyaProvider、PluginType | baseURL/path/method/task、参数编码、插件与认证处理；枚举分支不可仅靠 URL 常量 |
| WebSocket | URLSessionWebSocketTask、webSocketTask、Starscream、ws://、wss:// | 连接/心跳、收发、重连、关闭和生命周期 |
| 流式 / GraphQL / gRPC | AsyncBytes、bytes(for:)、text/event-stream、Apollo、GraphQL、GRPC、generated client | 帧/消息协议、错误、取消、背压、生成接口来源 |
| SDK 黑盒 | Package.resolved、Package.swift、Podfile.lock、framework/xcframework 引用 | 只编目实际 SDK 调用点；内部协议未知则记录 uncertainty，不能捏造 endpoint |
| 编码 / 解码 | JSONEncoder、JSONSerialization、CodingKeys、init(from:)、decodeIfPresent、NSJSONSerialization | JSON key、可空/默认、业务码、数值类型及前序失败导致后续兼容分支不可达的真实行为 |

HMOS 补扫继续用 http/rcp/webSocket 和 oh-package.json5 依赖的实际调用者。

## auth 链专项（Phase 2.75）

| 层 | 搜索起点 | 产物 |
|---|---|---|
| L2 签名 / 加密 | sign、nonce、signature、CryptoKit、CommonCrypto、HMAC、SecKey、encrypt | 算法、字节编码、参数排序、时间来源、header/body 注入和失效条件；保留源码 file:line，不外传密钥值 |
| L3 身份 | Keychain、SecItem、identifierForVendor、UUID、ASIdentifierManager、guest、visitorToken、deviceLogin | 身份值来源、获取/清除/保留、是否进入签名或登录请求；权限拒绝、跨平台连续性和恢复语义 |
| L0 配置 | Bundle、Info.plist、PRODUCT_BUNDLE_IDENTIFIER、MARKETING_VERSION、xcconfig、baseURL、tenantCode、appId | 读取有效 Release 配置与源码消费点，未展开变量不能当真值；不以工程默认值替代被选变体 |

token 获取→存储→注入→失效→清除→UI/存储副作用逐层追踪。隐私门控 L1 归 feature/base，但 chain-auth 须交叉核 owner。签名未发现应复查，不推断每个项目都必须有签名。二进制黑盒缺真值记 MISSING-TRUTH/uncertainty，不能推定没有加密。排除 DerivedData、生成缓存和未选 target，但不能把业务依赖当缓存排掉。

## 产物与降级

沿用原 raw_apis.json 结构补充，或写 raw_apis_supplemental.json 供 Phase 3 汇总。最终 schema、auth_model/data_flows、chain-auth 投影与 uncertainties 规则不变。

混合 RN/Flutter 工程按真实 JS/Dart 业务层分流，原生壳扫描不能代表业务全集；保留原 degraded/gaps 规则并说明范围。只有调用、依赖、动态配置补扫均无网络证据时才确认离线；services/hardcoded_urls 为空本身不足以确认。离线仍保留实际文件/媒体/系统 API 依赖。
