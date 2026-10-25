<!-- when: platform ios, Phase 2.5a 必读 -->
# iOS 框架 → HarmonyOS 能力候选

本表只向原 api-inventory.md 追加提示，不改变 JSON schema、阶段或门禁。候选不是 1:1 等价承诺：实施前核对项目实际 SDK 的 kits/*.d.ts、底层 API 声明中的 since/systemcap/permission 及官方服务配置。模块未列入本表或当前 SDK 未安装不能证明平台没有该能力。第三方供应商方案继续走 Phase 2.5b。

| 原生输入 | 目标候选 / 核验入口 | 必须保留的差异 |
|---|---|---|
| URLSession / URLRequest；Alamofire/Moya 语义 | NetworkKit http；RemoteCommunicationKit rcp | 请求、响应、拦截/签名、状态码、取消、会话与 TLS；不能仅替换类名 |
| URLSessionWebSocketTask / Starscream | NetworkKit webSocket | 连接、心跳、重连、关闭原因 |
| AsyncBytes / SSE / 流式响应 | 当前 SDK http/rcp 流式接口 | 分帧、字符边界、取消与重试；不宣称存在同名 SSE 客户端 |
| URLSessionDownloadTask | BasicServicesKit request.agent | 后台任务、沙箱、进度与恢复行为按目标真实能力核验 |
| Codable / CodingKeys / init(from:) / JSONSerialization | 显式模型映射与运行时 JSON 校验 | 字段别名、默认/缺失/null、数值类型和失败次序；类型断言不会校验 JSON |
| CryptoKit / CommonCrypto / Security 加密 | CryptoArchitectureKit cryptoFramework 等声明 | 算法、编码、密钥安全、签名原文与字节序必须逐项一致 |
| UserDefaults | ArkData preferences | 初始化完成时序、键/类型/默认与写入持久化 |
| Core Data / SwiftData / SQLite | ArkData relationalStore 等存储能力 | 数据模型、查询、迁移、事务与关系不自动等价 |
| Keychain / SecItem | AssetStoreKit / UniversalKeystoreKit 按用途核验 | 不降格为普通明文偏好；可访问性、重装/备份、密钥与凭据语义独立决策 |
| FileManager / 沙箱文件 | CoreFileKit fileIo / 文件访问能力 | 沙箱路径、生命周期、用户授权和 URI |
| UIDevice / identifierForVendor / IDFA | BasicServicesKit deviceInfo；ArkTS util UUID；授权广告标识能力 | 没有跨平台同一设备 ID 保证；持久 UUID 只有在服务契约允许时才可替代，不能冒充服务器身份 |
| StoreKit / 订阅 | IAPKit iap | 产品/订单、购买恢复、服务端验签、账户与取消/错误；缺商户配置不伪造成功 |
| UserNotifications / APNs | PushKit pushService + NotificationKit 本地通知 | token、应用签名、服务端通道、点击路由、授权与隐私；本地通知不能冒充远程推送 |
| ActivityKit / 实时活动 | LiveViewKit liveViewManager 候选 | 设备/系统支持、申请与配置、生命周期和更新限制；不先降级为普通通知，也不承诺灵动岛布局逐像素等价 |
| WidgetKit / AppIntents 扩展 | FormKit 卡片与目标交互能力 | 产品范围单独确认；不能因延后扩展而遗漏主应用入口、共享数据与引导 |
| WeatherKit | WeatherServiceKit weatherService 候选 | 地区/设备/服务资格、授权、字段、刷新与错误；存在 Kit 不证明已启用服务 |
| CoreLocation / MapKit | LocationKit / MapKit 候选 | 定位权限、后台、坐标系、地图资质与业务连续性 |
| HealthKit | HealthServiceKit 候选（依实际 SDK/服务资格） | 授权范围、数据类型、读写限制、隐私和历史数据连续性 |

写入提示来源列为 framework-kit-mapping.md，并注明核验用 SDK 版本/声明或尚待确认项。当前设备或服务不支持时按原 PD/AC/grill 决定替代、延期或范围调整，不能静默漏项。此表没有对任何项目的登录、支付、推送、Widget 或实时活动范围作默认决定。
