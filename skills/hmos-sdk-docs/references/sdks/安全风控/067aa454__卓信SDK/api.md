# **卓信ID SDK API 接口文档** 

**版本:V1.0.0** 

**更新时间:2024年08月02日** 

**中国信息通信研究院联合中国互联网协会共建 统一移动基础服务平台** 

## **1. 接口类说明** 

### **本文档所有接口所涉及的相关类及说明如下:** 

|**接口**|**说明**|
|---|---|
|ZXSDK|SDK功能接口类,用于调用卓信相关功能接口|

## **2. 初始化SDK** 

|**类名**|**ZXSDK**|
|---|---|
|接口|static async startSDK(appId: string, channel: string): Promise|

#### **说明:** 

- 初始化SDK,启动卓信SDK,成功后返回 true appID或者channel参数必须传一个 

#### **参数:** 

|**参数**|**类型**|**必要参数**|**说明**|
|---|---|---|---|
|appId|string|是|卓信官网生成的appId|
|channel|string|是|SDK服务商的channelId|

#### **返回:** 

boolean类型, 初始化成功为true, 失败为false 

#### **示例** 

```arkts
import { ZXSDK } from '@zx/zxsdk' const res = await ZXSDK.startSDK('#appId#', '#channelId#') if (res) { console.log('app: zxsdk start success'); } 
```

## **3. 配置ZXSDK模式** 

|**类名**|**ZXSDK**||
|---|---|---|
|接口 **说明** 该接口 **参数:** ZXSDKConfi|static setConfigOpt 需要在初始化接口之前调 gOption:配置参数|ion(config: ZXSDKConfigOption) 用,设置ZXSDK能力|
|**参数**|**类型必要参**|**说明**|
||**数**||
|privacy|number(0/1) 否|如已开通AID能力, 默认是不加密返回(privacy = 0)。如需设置加 密 (防止其他方获取到自己的aids),可将privacy设置为1|

#### **返回:** 

无 

#### **示例** 

// 引入 ZXSDK 以及配置相关类 import { ZXSDKConfigOption, ZXSDK } from '@zx/zxsdk' // 获取默认配置 const config = ZXSDKConfigOption.defaultConfig() 

// 按照需要修改配置 config.privacy = 0 ······ // 设置zxsdk配置 ZXSDK.setConfigOption(config) 

## **4. 获取卓信ID** 

|**类名**|**ZXSDK**|
|---|---|
|接口|static async getZXID(): Promise|

#### **说明:** 

获取zxid 

#### **参数:** 

无 

#### **返回:** 

ZXIDResult对象, 包含zxid, aid等内容 

#### **示例** 

import { ZXSDK, ZXIDResult } from '@zx/zxsdk'; 

/** export interface ZXIDResult { zxid: string        // 卓信id expireTime: string  // 过期时间 openid: string tags: Object aaid: string, vaid: string } */ try { const zxResult: ZXIDResult = await ZXSDK.getZXID() console.log('zxResult', JSON.stringify(zxResult)); } catch (err) { 

console.log(`ZXSDKError: code: ${err.code} message: ${err.message}`); } 

## **5. 获取SDK版本号** 

|**类名**|**ZXSDK**|
|---|---|
|接口|static version(): string|

#### **说明:** 

获取卓信SDK的版本号 

#### **参数:** 

无 

#### **返回:** 

SDK的版本号string 

#### **示例** 

import { ZXSDK } from '@zx/zxsdk'; 

console.log(ZXSDK.version()); 

## **6. 服务商初始化SDK** 

|**类名**|**ZXSDK**|
|---|---|
|接口|static initWith(appId: string, channel: string): Promise|

#### **说明:** 

服务商需初始化 ZXSDKInstance 的对象, 并维护其生命周期。 

#### **参数:** 

|**参数**|**类型**|**必要参数**|**说明**|
|---|---|---|---|
|appId|string|是|卓信官网生成的appId|
|channel|string|是|SDK服务商的channelId|

#### **返回:** 

ZXSDKInstance实例对象, 服务商可用该对象获取zxid 

#### **示例** 

import { ZXSDK } from '@zx/zxsdk' // 服务商初始化 ZXSDK 时, appId 和 channelId 都为必填项 const instance = await ZXSDK.initWith('#appId#', '#channelId#')
