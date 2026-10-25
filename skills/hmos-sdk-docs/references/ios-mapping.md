# iOS SDK 到鸿蒙的候选查找

保持原流程：从本轮真实源依赖与调用识别能力 → 同厂鸿蒙候选优先 → 无同厂时比较能力替代 → 按 l0-index/厂商文档/online-lookup 核实。候选名称或本机 Kit 声明不是已安装、服务已开通、后端接受或行为等价证明。

## 识别真实源输入

读取选定 Xcode target 的工程链接/嵌入信息、SwiftPM Package.resolved、实际 Podfile.lock/Cartfile.resolved、xcframework/framework/module 与初始化调用。不能把其他平台的包名、命名空间或锁文件名称改成 iOS 就作为来源；同厂不同平台也可能使用不同类型和 API。

系统能力接缝先读 [原生框架映射](../../ios-api-inventory/references/framework-kit-mapping.md)，保持其证据与不确定项边界。

| 实际源能力 | 鸿蒙查找方向 | 必须核对 |
|---|---|---|
| StoreKit / 实际会员支付链 | IAPKit 或已批准支付通道 | 商品/订单/取消/待处理/恢复、服务端验单及配置差异 |
| UserNotifications / 实际远端推送注册 | PushKit 及实际通知能力 | 权限、token、通道、后台落地和注销 |
| ActivityKit / 实际主应用实时活动 | LiveViewKit 等实际候选 | 版本、设备、服务配置、样式与生命周期；不能假设自动等价 |
| CoreLocation / MapKit 或真实地图厂商库 | 原定位/地图专项及同厂候选 | 权限、精度、坐标、轨迹、后台与取消 |
| LocalAuthentication / AuthenticationServices | 真实身份认证候选及已批准账号方案 | 系统认证与服务端账号不是同一合同，不默认为账号互通 |
| URLSession / 实际三方网络与解码库 | NetworkKit/RemoteCommunicationKit 等原候选 | 请求、响应、编码、取消、鉴权和错误链 |
| 实际客服/IM/RTC/统计/广告/分享 SDK | l0-index 同厂能力分类，随后原 online-lookup | 真实厂商、版本、许可、初始化、回调、标识与后台配置 |

## 三方厂商匹配

以实际依赖供应商和调用合同匹配 l0-index，不凭类名相似或其他平台的命名空间判断。已有厂商和运营后台的项目优先核实同厂鸿蒙版本；换厂商、Web 承载、自研或降级仍走原决策流程。没有材料时登记真实缺口，不编造源 module、目标包名或 SDK 已就绪状态。

原 SDK 文档快照保留其原文与时间；需要当前版本时按 [online-lookup](online-lookup.md) 核查官方材料，不将快照未收录推断为不存在鸿蒙能力。
