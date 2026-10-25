# 安胜 API 安全 SDK 接口集成文档 

V1.0 

# 北京安胜华信科技有限公司 

2024-12 

目录 

1 SDK 简介 3 

2 SDK 内容 3 

3 接口说明 3 

3.1 初始化接口 3 

3.2 获取安全 sdk 请求头接 口 4 

SDK 简介 

安胜 API 安全 SDK 是 一 款专注于 风 险采集与识别的 SDK ,具备 生 成唯 一 设 

# 备 ID 、 风 险监测和设备信息收集等核 心 功能。 

SDK 内容 

HarmonySDK 包含如下内容: 

Har 文件: security_sdk.har 

接口说明 

初始化接口 

对 sdk 进行初始化操作,请在调用 sdk 相关功能前先执行以下初始化操 作 

引入 SDK : import SwSDK from '@ansheng/security_sdk'; 

function init(context: Context): Promise<string> 

参数说明: 

1.Context :上下文 

2.Promise<string> :设备信息 

调用示例: 

import SwSDK from '@ansheng/security_sdk'; 

// SDK 初始化 

SwSDK.init(this.context.getApplicationContext()) 

获取安全 sdk 请求头接 口 

function getHeaders(): Map<string,string> 

参数说明: 

Map 对象,返回获取到的设备信息。 

调用示例: 

const headers=new Map<string,string>(); let swHeaders=SwSDK.getHeaders();
