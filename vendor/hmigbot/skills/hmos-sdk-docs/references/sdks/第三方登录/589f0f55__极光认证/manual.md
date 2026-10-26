开发者支持 关于极光 语言 

### 产品 解决方案 成功案例 海外消息服务 

文档中心 合规指南 开发者社区 

极光安全认证 极光文档 > 极光安全认证 > 客户端 SDK > HarmonyOS SDK > HarmonyOS SDK 集成指南 HarmonyOS SDK 集成指南 入门指南 最近更新:2024-09-03 控制台指南 客户端 SDK 使用提示 Android SDK 本文是 JVerification HarmonyOS SDK 标准的集成指南文档。 HarmonyOS SDK 匹配的 SDK 版本为:v1.0.0 及以后版本。 如果您想要快速地测试、请参考本文在几分钟内跑通 Demo。 HarmonyOS SDK 集成 指南 极光认证文档网站上,有相关的所有指南、API、教程等全部的文档。包括本文档的更新版本,都会及时地发布到该网站上。 HarmonyOS SDK API HarmonyOS SDK 错误 产品说明 码 极光认证整合了三大运营商的网关认证能力,为开发者提供了一键登录和号码认证功能,优化用户注册 / 登录、号码验证体验,提高安全性。 iOS SDK Web SDK 主要场景 

客户端集成插件 

注册 运营商错误码 登陆 二次验证 

本页目录 使用提示 产品说明 主要场景 获取应用信息 配置签名 集成方式 技术支持 

REST API 

常见问题 最近更新 资源下载 

# 获取应用信息 

在控制台上 创建应用 后,可以进入【认证设置】-【集成设置】页面获取用以标识应用的 AppKey。 

配置签名 

需要在极光后台配置应用签名,以下为获取签名方式: 

//在程序里调用该方法获取当前签名 

getSign(): string { 

let bundleFlags = bundleManager.BundleFlag.GET_BUNDLE_INFO_WITH_SIGNATURE_INFO; let bundleInfo = bundleManager.getBundleInfoForSelfSync(bundleFlags) 

return bundleInfo.signatureInfo.fingerprint 

} 

集成方式 

集成压缩包下载链接: 前往下载 

jverification-hmos-x.x.x-release.zip 集成压缩包内容 

jverification-hmos-x.x.x-release.har 

极光开发者服务的核心包。 

doc 

文档 

entry 是一个 hmos demo 项目代码,通过这个演示了 JVerification SDK 的基本用法,可以用来做参考。 

## har 文件集成 

## 解压缩 jverification-hmos-x.x.x-release.zip 集成压缩包。 

复制 jverification-hmos-x.x.x-release.har 到你的工程的 entry/hars/ 目录下。(hars 这个目录可以自定义) 

说明 :关联 jverification-hmos-x.x.x-release.har,如,你复制 har 到 entry/hars/ 目录下,那么在 entry 模块下的 oh-package.json5 文件添加 

"dependencies" : { 

> "jverify" : "./hars/jverification-hmos-x.x.x-release.har" //这里的路径是你存放 jverification-hmos-x.x.x-release.har 的位置, "pako" : "^2.1.0" , //需要使用的第三方压缩库 "js-sha256" : "^0.9.0" //需要使用的第三方 sha256 库 

} 

引入  UI  资源
需要将  SDK  用的图片导入至  AppScope/resources/base/media  文件夹内,示例图片在压缩包内的  media  文件夹中
文件名  说明
jverify_background.png  一键登录主背景图片
jverify_ctlogo.png  电信logo

jverify_culogo.png 联通logo 

jverify_dialog_background.png 一键登录弹窗背景图片 

jverify_dialog_close.png  一键登录弹窗关闭按钮

修改工程级  build-profile.json  文件

说明 :根据联通  sdk  需求需要增加该配置,只需要配置  useNormalizedOHMUrl  到如下位置即可
"products" : [
{
"name" :  "default" ,
"signingConfig" :  "default" ,
"compatibleSdkVersion" :  "5.0.0(12)" ,
"runtimeOS" :  "HarmonyOS" ,
"buildOption" : {
"strictMode" : {
"useNormalizedOHMUrl" :  true
}
},buildOption
}
],

配置 权限
在module.json5中配置一键登录需要使用的权限
"requestPermissions" : [
{
"name" :  "ohos.permission.INTERNET"
} ,
{
"name" :  "ohos.permission.GET_NETWORK_INFO"
} ,
{
"name" :  "ohos.permission.GET_WIFI_INFO"
} ,
{
"name" :  "ohos.permission.SET_NETWORK_INFO"
} ,
] ,
配置  极光平台信息
主要步骤为:
在极光平台创建  App,有两个信息包名和  AppKey
说明1:
在本地工程配置包名,方式,  在  AppScope  工程下的  app.json5  文件添加
{
"app" : {
"bundleName" :  "你的包名" ,
}
}
说明2:
在本地工程配置  AppKey,代码配置  如:
export  default  class  MyAbilityStage  extends  AbilityStage  {
onCreate ( ) {
JVerificationInterface. init ( "你的  APPKEY" , ( code,  msg )  =>  {
});
}
}
其他功能
请参考: HarmonyOS  SDK  接口说明
技术支持
邮件联系: support@jiguang.cn

文档内容是否对您有帮助?
提交评分
