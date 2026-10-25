# 乐播投屏 SDK 使用指南(HarmonyOS) 

SDK 名称:乐播投屏 SDK(鸿蒙版) 

包名: @lebo/lelink-sdk 

适用平台:HarmonyOS 5.0 / API 12 及以上 

当前版本:1.0.13 

文档来源:https://cloud.lebo.cn/document/8a10384bcfe1e565.html 

## 概述 

本指南将帮助您将乐播 SDK 集成到您的 HarmonyOS 项目中,并顺利调用乐播 SDK 提供的 API 接口。集 成投屏 SDK 只需要简单的两步: 

1. SDK 导入及配置 

2. SDK 初始化 

## 一 、SDK 导入及配置 

### 1.1 导入 SDK 

请将 lelink-sdk.har 导入到工程中的 libs 目录下。 

然后在 entry/oh-package.json5 中添加以下依赖配置: 

"dependencies": { "@lebo/lelink-sdk": "file: ./libs/lelink-sdk.har" } 

完成上述配置后,您就可以调用 SDK 提供的 API 了。 

### 1.2 配置权限 

以下为投屏 SDK 所需要的权限: 

#### (1)SDK 已内置,无需重复申请 

ohos.permission.INTERNET ohos.permission.GET_NETWORK_INFO ohos.permission.GET_WIFI_INFO ohos.permission.STORE_PERSISTENT_DATA 

#### (2)需要在依赖 lelink-sdk 的模块的 module.json5 中添加 

ohos.permission.MICROPHONE ohos.permission.KEEP_BACKGROUND_RUNNING / keep-alive ohos.permission.CAMERA 

### 1.3 配置 keep-alive 

#### 说明:镜像投屏时需要保活,否则应用切换至后台后会被系统中断。 

文件位置: entry/src/main/module.json5 

#### 配置示例: 

{ "module": { "abilities": [ { "name": "EntryAbility", / . "backgroundModes": ["audioRecording"] } ] } } 

### 1.4 其他配置 

由于 lelink-sdk 是含字节码的 HAR,项目级 build-profile.json5 必须配置 "useNormalizedOHMUrl": true ,否则构建会失败。 

{ "app": { "products": [ { "name": "default", "signingConfig": "default", "compatibleSdkVersion": "5.0.0(12)", "runtimeOS": "HarmonyOS", "buildOption": { "strictMode": { "useNormalizedOHMUrl": true / } } } ] } } 

## 二、SDK 初始化 

关于 AppID 与 AppSecret 的获取,请参考乐播开发者中心的「控制台说明」。 

建议将 SDK 初始化代码放置在 EntryAbility#onCreate() 中执行。 

### 2.1 初始化代码示例 

/ EntryAbility#onCreate() 

```arkts
let appID: string = '${appID}' / let appSecret: string = '${appSecret}' / 
```

appID appSecret 

lelink.initial({ context: this.context, appID: "your appID", appSecret: "your appSecret", licenseSerialNumber: "your license serial number" }) 

### 2.2 初始化接口定义 

SDK 初始化只需传入 1 个参数,包含以下几个字段: 

interface LelinkSourceSDKOptions { /** * debug / debug : boolean, /** * UIAbilityContext / context: Context, /** * appID / appID: string, /** * appSecret / appSecret: string, /** * license / licenseSerialNumber : string, } 

### 2.3 参数说明 

|参数|类型|是否必 填|说明|
|---|---|---|---|
|context|Context|是|应用程序的context,建议传入UIAbilityContext。|
|appID|string|是|在乐播开发者中心申请的AppID。|
|appSecret|string|是|在乐播开发者中心申请的AppSecret。|
|licenseSerialNumber|string|否|设备唯一号,由开发者自主生成,需确保唯一性;开通 license授权时需要传递。|
|debug|boolean|否|是否开启debug模式,开启后将输出更详细的运行日志, 正式发布时建议关闭。|

© 乐播投屏 · SDK 使用指南(HarmonyOS)
