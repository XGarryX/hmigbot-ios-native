# 0.13.4 择优能力与基本流程

指定上游为 `XGarryX/hmigbot-ios-native` 的 `hmigbot-ios-1.5.2.32`。本地代码与该版逐能力比较，当前发行采用 macOS ARM64 profile。历史导入 manifest 记录原始来源，不等于当前能力完成率；本说明也不代表具体 App 已完成转换验收。

|方面|选择|能力与采用原因|
|---|---|---|
|环境与权限|本地 Git 为主，Garry .32 目标诊断适配|初始化按所选能力说明权限与替代路径；目标 SDK 诊断复用 .32 的 argv 调用、网络权限三态和真实产品声明。设备发现显式选择，签名缺件不阻断未签名诊断。|
|Swift 语法、字符串与源坐标|共享本地正式 Provider|SwiftParser/SwiftSyntax 处理词项、声明、字面量解码和原坐标，事实/字面量/候选消费同一发布证据，避免多份 Swift 解释器。|
|工程、构建配置和成员|本地 Git|保留真实 scheme/configuration/SDK/architecture、App 与实际嵌入扩展范围、原始编译成员及依赖；不把项目声明当已编译成员。OpenStep 格式交 Apple plutil，目标语义仍由 Xcode 证据核对。|
|Swift/ObjC/混合条件编译|本地 Git 共享源视图|SwiftIfConfig、Apple Swift 和 Clang 根据原编译上下文判定活动区域；保留每个翻译单元、桥接头及共享头文件的不同视图。证据不足保留未知。|
|渲染显隐候选|Garry .32 收集器 + 本地正式源视图|采用 SwiftSyntax Collector 区分 render/action/unresolved，补 WidgetKit 公开内容槽位；消费当前活动行与正式 Provider 协议，不另建事实源。候选不等于类型绑定或运行时几何。|
|资源与本地化|共享现有实现|Asset Catalog、本地化和目标资源衔接已有实际消费者；按产品引用和资源格式保留范围，不重复搬运同义模块。未支持变体明确报告。|
|规格与共享源责任|本地 Git|源锚点、稳定 AC、contract_refs 和多义务到真实 AC 的映射共用一套合同；不增加 .32 专用共享实例表作为所有项目必填输入。|
|计划与派发|本地冻结合同 + Garry indexed 执行|保留源/规格/写权身份，由已接线的执行链实施。单任务批次合法，plan-check 仅可选预览；plan-ir 自身执行真实校验。|
|完整源门复用|共享成功收据|正式交接进行完整源门；冻结合同后的复用必须核当前源、规则、消费输入、配置和原收据。旧合同或输入不符完整复检，复用不冒充新一次原生调用。|
|终态与登记表回写|Garry .32 开放扩展 + 本地严格回读|采用 final feature_index.verified 与显式表头修复；只允许已 implemented 的条目晋级，先原引擎 dry/apply，再核请求之外的字节未变。状态写回不替代行为证据。|
|目标构建与静态结构|现有目标 SDK 与结构引擎|实际 Hvigor/ETS 输出是编译轴依据；合同未完成仍能做独立诊断。重复 detector 仅复用同输入/规则/范围的完整原始测量。|
|验证范围与恢复|本地因果规则 + Garry 检查语义|基础检查按实际适用输入执行，高级页面/路由按范围，视觉/设备不进必经流程；真实已绑定失败保留，报告可输出 partial/not_run。技术重试不制造产品审批。|
|专用 Widget 绑定/孤儿 SDK 投影|本轮不加入基本发行|依赖额外声明与专用消费者，不能作为全部 iOS App 的新清单。现有源合同和真实 SDK 构建继续核验，需要该专用语义时再按明确输入增量接入。|
|设备场景学习、截图和视觉自动回放|延期，不随基本发行|需要项目私有场景、数据和额外授权；历史业务样例、默认测试图和设备脚本不进入基本转换包。可消费开发者显式提供的外部证据，但不宣称内置后端已经执行。|
|Intel/Windows/Linux|延期|不交付对应资产或兼容启动链；增量接入要求与恢复点见平台计划。|

## 官方依据与自编边界

- [Apple Xcode CLI](https://developer.apple.com/documentation/xcode/xcode-command-line-tool-reference) 与 [构建系统](https://developer.apple.com/documentation/xcode/build-system)：提供原工程构建/配置证据，不直接生成 HarmonyOS 实现。
- [Apple Xcode MCP](https://developer.apple.com/documentation/xcode/giving-external-agents-access-to-xcode)：开发者控制外部 agent 访问；服务、授权、工具发现和实际调用分别记录。
- [Swift 官方语法库](https://github.com/swiftlang/swift-syntax) 与 [条件编译规则](https://docs.swift.org/latest/documentation/the-swift-programming-language/statements/)：语法与编译条件有原生依据；本工具的证据协议、筛选和 ArkUI 映射属于自编适配。
- [SwiftUI 条件内容构建](https://developer.apple.com/documentation/swiftui/viewbuilder/buildeither(first:)) 与 [WidgetKit 内容闭包](https://developer.apple.com/documentation/widgetkit/creating-a-widget-extension)：用于解释受支持的渲染槽位；自定义同名类型与运行时效果仍需进一步证据。
- [Huawei Hvigor CLI](https://developer.huawei.com/consumer/en/doc/harmonyos-guides/ide-hvigor-commandline)：目标构建由真实 SDK 命令完成，通用环境诊断不代替构建、签名或行为通过。

Apple 没有提供整个 iOS→HarmonyOS 转换与责任账本的统一 API。源语义优先消费官方工具；迁移合同、证据编排、源目标对应和执行回读如实标为本地/Garry 工具实现。
