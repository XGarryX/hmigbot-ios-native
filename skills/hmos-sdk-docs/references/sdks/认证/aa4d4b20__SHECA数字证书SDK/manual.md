
> **原生输入边界**：本文件保留 Garry 的目标平台算法、私有 wire 字段和平台对照示例。
> 源输入只来自当前 git facts/semantics/page spec；历史源设备命令和旧语言扫描不适用于 iOS，
> 不得实际调用或用它们的缺省结果表示源端通过。源扫描缺少原生适配时保持 unresolved；
> 当前范围的屏幕采集/设备控制记 not_run。目标 hdc/hvigor 的适用部分也须遵守当前授权。

> **iOS 源输入**：读取 Swift/Objective-C、SwiftUI/UIKit、Xcode 工程及原生资源；实际源构建与设备观测依赖可用的源平台环境。鸿蒙侧构建和验收保持原流程。源侧操作详见 `ios-source-analysis/SKILL.md`。

# @sheca/digit-cert 使用指南 

一、前置准备 

确保 DevEco Studio 已安装 HarmonyOS SDK ( API12+ ),本地部 署合规数字证书 SDK 依赖包; 

申请并获取合法数字证书(含公钥、证书链文件),确保证书未过期 且已完成安全校验。 

# 二、集成配置 

在模块级 build.gradle 中添加 SDK 依赖(如 implementation ' 合规厂 商 :cert-sdk: 版本号 ' ),同步工程; 

在 config.json 中声明网络、文件读取权限(如 ohos.permission.INTERNET 、 ohos.permission.CAMERA )。 

三、核心使用步骤 

初始化 SDK :调用初始化接口,传入证书路径、证书链信息及配置参 数(如超时时间); 

证书校验:调用 SDK 校验接口,验证证书合法性、完整性及有效 期,拒绝无效 / 篡改证书; 

加密 / 签名操作:通过 SDK 提供的 API 实现数据加密、签名验签 (仅使用公钥,私钥不存储在应用侧); 

资源释放:操作完成后调用销毁接口,释放 SDK 占用资源,避免内 存泄漏。 

四、注意事项 

定期更新 SDK 版本及数字证书,适配 HarmonyOS 系统迭代; 留存使用日志,配合合规核查,异常情况及时捕获并处理。
