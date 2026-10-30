# 安胜 API 安全 SDK 使用指南 

V1.0 

# 北京安胜华信科技有限公司 

2024-12 

目录 

- 1 SDK 简介 3 

- 2 SDK 内容 3 

- 3 使用指南 3 

- 3.1 添加网络权限 3 

- 3.2 SDK 初始化 3 

- 3.3 获取安全 sdk 请求头接 口 3 

- 3.4 请求头中添加 SDK 获取到的信息 3 

# SDK 简介 

安胜 API 安全 SDK 是 一 款专注于 风 险采集与识别的 SDK ,具备 生 成唯 一 设 备 ID 、 风 险监测和设备信息收集等核 心 功能。 

SDK 内容 

HarmonySDK 包含如下内容: Har 文件: security_sdk.har 

使用指南 

添加网络权限 

添加 SDK 依赖权限 SDK 依赖 网 络权限,需要在 工 程的 module.json5 添加 网 络权限。 

SDK 初始化 

引入 SDK : import SwSDK from '@ansheng/security_sdk'; 

创建 AbilityStage 的 子 类,然后在 onCreate() 的 方 法 里面 调 用 SwSDK.init(...)API 进 行SDK 初始化,另外需要在 工 程 module.json5文 件 里面 添加 AbilityStage 的 子 类的 入口 的声明。 

SwSDK.init(this.context.getApplicationContext()) 

获取安全 sdk 请求头接 口 

function getHeaders(): Map<string,string> 

参数说明: 

Map 对象,返回获取到的设备信息。 

const headers=new Map<string,string>(); 

let swHeaders=SwSDK.getHeaders(); 

请求头中添加 SDK 获取到的信息 

在所有业务的 HTTP 请求中添加安胜 SDK 提供的请求头信息。如果 HTTP 请求框架 支 持拦截器,也可以通过拦截器添加。另外需要注意的 是,如果某个功能不需要 风 险监控,可以省略添加该 风 险请求头信 

息。
