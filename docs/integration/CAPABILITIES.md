# 转换能力与当前发行范围

完整择优理由见 [0.13.4融合说明](../SELECTIVE-FUSION.md)。机器目录描述能力和入口，不是某个项目的执行记录；可用、获准、实际调用与通过分别记录。

|阶段|当前保留能力|实际依据与边界|
|---|---|---|
|Init|所选运行入口、宿主、目标环境与权限选择|macOS ARM64；未选后端不成为启动门。|
|Source|工程配置、编译成员、SwiftSyntax/Clang、Swift/ObjC混合条件视图|原始Xcode/编译证据；缺证据保持未知。|
|Spec|源锚点、行为/状态/错误/资源合同、稳定AC和共享接口|一份Source/facts；文档组织形式不创造产品义务。|
|UI候选|meta、静态outline、语法显隐候选|Swift正式Provider及活动区域；不宣称设备几何。|
|Resources|资产、本地化和目标资源转换|当前产品范围与真实资源引用；未支持变体明确报告。|
|Plan|MD/typed映射、写权/依赖、plan-ir冻结与受审replan|单任务可执行；plan-check可选预览。|
|Execute|Garry indexed实施与唯一writeback链|原引擎结果+严格回读，状态不等于行为验收。|
|Verify|真实SDK构建、适用结构/身份/占位/页面/路由与部分报告|共享当前证据；缩scope不隐藏真实失败。|
|Recovery|因果finding、具体备选方案、技术策略预算与收据|不凭修复轮数产生产品审批。|
|应用 UI 测试|指定应用截图、控件信息、固定回放与配对证据|官方适配按明确应用/模拟器/场景和真实入口/收据记录；许可不代替已实现或已执行，不要求桌面接管。|
|Deferred|旧设备/视觉扩展、Intel/Windows/Linux|不交付对应旧后端或其他平台资产；不据此一概禁止新的官方应用测试，见延期能力与平台计划。|

运行能力目录为 [semantic_capabilities.json](../../src/hmigbot_ios/semantic_capabilities.json)，旧原子任务入口为 [capabilities.json](../../src/hmigbot_ios/capabilities.json)。目录中的能力数量不表示完整性或项目验收百分比。工具自有回归、发布证据与真实项目产物均保存在工具目录外，不作为任意App启动转换的门禁。

[官方能力优先规则](../../rules/ios-official-capabilities-first.md)规定源语义采用官方skill/MCP、Xcode CLI、Swift库和Apple分发Clang；本工具的编排、合同与ArkUI映射如实标为自编适配。目标构建使用开发者安装的官方SDK，具体项目分别记录生成、编译与行为证据。
