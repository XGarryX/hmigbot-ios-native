# **Shiply Harmony SDK** 接口文档 

## 概述 

Shiply Harmony SDK 为鸿蒙应用提供动态配置下发、资源管理等功能。 SDK 包含两个主要模 块: 

- **RDelivery** : 配置发布模块 

- **ResHub** : 资源发布模块 

## 认证机制 

所有接口调用都需要在初始化时提供以下认证信息: 

- `appId` : 应用 ID ,从 Shiply 平台获取 

- `appKey` : 应用密钥,从 Shiply 平台获取 

- `userId` : 用户 ID 

- `deviceId` : 设备 ID 

## **RDelivery** 配置发布接口 

### **1. SDK** 初始化 

#### 接口名称 

```
RDelivery.SdkStart
```

#### 调用方式 

static SdkStart(dbPath: string, config: RDeliveryConfig, logger: (level: number, log: string) => void): boolean 

#### 请求参数 

|参数名|类型|必|填 描述|
|---|---|---|---|
|dbPath stri|ng|是|存储配置的mmkv路径|
|confg RD|eliveryConfg|是|SDK初始化配置|
|logger fun|ction|是|日志输出回调函数|
|**RDeliveryConfg**配 参数名|置参数 类型|必 填|描述|
|logicEnvironment|string|否|逻辑环境,""为正式环境,"1"为测试环 境|
|appId|string|是|应用ID|
|appKey|string|是|应用密钥|
|userId|string|是|用户ID|
|deviceId|string|是|设备ID|
|language|string|否|语言设置|
|appVersion|string|是|应用版本号|
|osVersion|string|是|操作系统版本|
|bundleId|string|是|应用包名|
|updateInterval|number|否|配置更新间隔(秒)|
|updateStrategy|RDUpdateStrategy|否|更新策略|
|is_debugPackage|boolean|否|是否为调试包|
|target|RDPullTarget|否|拉取目标|

#### 返回参数 

|参数名|类型|描述|
|---|---|---|
|success|boolean|初始化是否成功|

调用示例 

```arkts
let config: RDeliveryConfig = new RDeliveryConfig(); "" config.logicEnvironment = ; config.appId = "your_app_id"; config.appKey = "your_app_key"; config.userId = "your_user_id"; config.deviceId = "your_device_id"; config.language = "en"; config.appVersion = "1.0.0"; config.osVersion = "16.2"; config.bundleId = "com.example.app"; 
let logOutput = (level: number, log: string) => { hilog.info(0x0000, 'ShiplyLog', '%{public}s', log); }; 
let context = getContext(this) as common.UIAbilityContext; let filesDir = context.filesDir; RDelivery.SdkStart(filesDir, config, logOutput); 
```

### **2.** 拉取全量配置 

#### 接口名称 

```
RDelivery.RequestFullRemoteData
```

#### 调用方式 

static RequestFullRemoteData( custom_properties: Record<string, any>, 

onResult: (error_code: number, configList: Array<RDeliveryData>) => void ): void 

#### 请求参数 

|参数名|类型|必填|描述|
|---|---|---|---|
|custom_properties|Record<string, any>|否|自定义属性|
|onResult|function|是|结果回调函数|

#### 返回参数 

|参数名|类型|描述|
|---|---|---|
|error_code|number|错误码,0表示成功|
|confgList|Array|配置数据列表|

#### 调用示例 

```arkts
let custom_properties = {age: 100}; RDelivery.RequestFullRemoteData(custom_properties, (error_code: number, configList: Array<RDeliveryData>) => { 
```

if (error_code === 0) { 

configList.forEach((data: RDeliveryData) => { 

console.log(`key: ${data.key}, value: ${data.value}`); }); } }); 

### **3.** 按场景 **ID** 拉取配置 

#### 接口名称 

```
RDelivery.RequestBatchRemoteDataByScene
```

#### 调用方式 

static RequestBatchRemoteDataByScene( 

sceneId: number, 

custom_properties: Record<string, any>, 

- onResult: (error_code: number, configList: Array<RDeliveryData>) => void 

- ): void 

#### 请求参数 

|参数名|类型|必填|描述|
|---|---|---|---|
|sceneId|number|是|场景ID|
|custom_properties|Record<string, any>|是|自定义属性|
|onResult|function|是|结果回调函数|

返回参数 

#### 同拉取全量配置接口 

#### 调用示例 

```arkts
let scene_id = 100780; let custom_properties = {age: 100}; 
```

RDelivery.RequestBatchRemoteDataByScene(scene_id, custom_properties, (error_code: number, configList: Array<RDeliveryData>) => { 

// 处理结果 }); 

### **4.** 按多个场景 **ID** 拉取配置 

#### 接口名称 

```
RDelivery.RequestBatchRemoteDataByScenes
```

#### 调用方式 

static RequestBatchRemoteDataByScenes( 

sceneIds: number[], 

custom_properties: Record<string, any>, 

onResult: (error_code: number, configList: Array<RDeliveryData>) => void ): void 

#### 请求参数 

|参数名|类型|必填|描述|
|---|---|---|---|
|sceneIds|number[]|是|场景ID列表|
|custom_properties|Record<string, any>|是|自定义属性|
|onResult|function|是|结果回调函数|

#### 调用示例 

let scene_ids = [100780, 100782, 100699]; RDelivery.RequestBatchRemoteDataByScenes(scene_ids, custom_properties, (error_code: number, configList: Array<RDeliveryData>) => { 

// 处理结果 }); 

### **5.** 按配置 **Key** 拉取单个配置 

#### 接口名称 

```
RDelivery.RequestSingleRemoteDataByKey
```

#### 调用方式 

static RequestSingleRemoteDataByKey( key: string, 

custom_properties: Record<string, any>, 

onResult: (error_code: number, configList: Array<RDeliveryData>) => void ): void 

#### 请求参数 

|参数名|类型|必填|描述|
|---|---|---|---|
|key|string|是|配置Key|
|custom_properties|Record<string, any>|是|自定义属性|
|onResult|function|是|结果回调函数|

### **6.** 按多个配置 **Key** 拉取配置 

#### 接口名称 

```
RDelivery.RequestRemoteDataByKeys
```

#### 调用方式 

static RequestRemoteDataByKeys( keys: string[], 

custom_properties: Record<string, any>, 

onResult: (error_code: number, configList: Array<RDeliveryData>) => void ): void 

#### 请求参数 

|参数名|类型|必填|描述|
|---|---|---|---|
|keys|string[]|是|配置Key列表|
|custom_properties|Record<string, any>|是|自定义属性|
|onResult|function|是|结果回调函数|

### **7.** 同步读取单个配置 

#### 接口名称 

```
RDelivery.SyncGetRDeliveryDataByKey
```

#### 调用方式 

static SyncGetRDeliveryDataByKey(key: string): RDeliveryData | undefined 

#### 请求参数 

参数名 类型 必填 描述
key string 是 配置 Key
返回参数
参数名 类型 描述
data RDeliveryData | undefined 配置数据,不存在时返回 undefined

### **8.** 异步读取单个配置 

#### 接口名称 

```
RDelivery.GetRDeliveryDataByKey
```

#### 调用方式 

static GetRDeliveryDataByKey(key: string, onResult: (errorCode: number, data: RDeliveryData | undefined) => void): void 

### **9.** 同步读取所有配置 

#### 接口名称 

```
RDelivery.SyncGetRDeliveryAllDataMap
```

#### 调用方式 

static SyncGetRDeliveryAllDataMap(): Map<string, RDeliveryData> 

### **10.** 切换用户 

#### 接口名称 

```
RDelivery.SwitchUserId
```

#### 调用方式 

static SwitchUserId(userId: string, onResult: (error_code: number) => void): boolean 

### **11.** 切换环境 

#### 接口名称 

```
RDelivery.SwitchEnvironment
```

#### 调用方式 

static SwitchEnvironment(envId: string, onResult: (error_code: number) => void): boolean 

## **ResHub** 资源发布接口 

### **1.** 初始化资源中心 

#### 接口名称 

```
ResHub.initResHubCenter
```

#### 调用方式 

static initResHubCenter( param: ResHubParam, appId: string, appKey: string, logicEnv: string, logger: (level: number, log: string) => void ): void 

#### 请求参数 

|参数名|类型|必填|描述|
|---|---|---|---|
|param|ResHubParam|是|资源中心参数|
|appId|string|是|应用ID|
|appKey|string|是|应用密钥|
|logicEnv|string|是|逻辑环境|
|logger|function|是|日志回调函数|

#### **ResHubParam** 参数 

|参数名|类型|必填|描述|
|---|---|---|---|
|appVersion|string|是|应用版本|
|qimei|string|是|设备标识|
|deviceType|string|是|设备类型|
|systemVersion|string|是|系统版本|
|isDebugPackage|boolean|是|是否为调试包|
|resStoragePath|string|是|资源存储路径|
|resConfgStoragePath|string|是|资源配置存储路径|
|callbackOnMainThread|boolean|否|是否在主线程回调|

### **2.** 异步加载资源(锁定版本) 

#### 接口名称 

```
ResHub.loadWithId
```

#### 调用方式 

static loadWithId( resId: string, onProgress: (progress: number) => void, 

onResult: (success: boolean, error: ResHubError, resModel: ResHubModel) => void 

): void 

#### 请求参数 

|参数名|类型|必填|描述|
|---|---|---|---|
|resId|string|是|资源ID|
|onProgress|function|是|进度回调|
|onResult|function|是|结果回调|

### **3.** 同步获取最新资源 

#### 接口名称 

```
ResHub.latestResWithId
```

#### 调用方式 

static latestResWithId(resId: string, needValidate: boolean): ResHubModel 

### **4.** 异步加载最新资源 

#### 接口名称 

```
ResHub.loadLatestWithId
```

#### 调用方式 

static loadLatestWithId( resId: string, onProgress: (progress: number) => void, 

onResult: (success: boolean, error: ResHubError, resModel: ResHubModel) => void 

): void 

### **5.** 异步加载实时最新资源 

#### 接口名称 

```
ResHub.loadRealtimeLatestWithId
```

#### 调用方式 

static loadRealtimeLatestWithId( resId: string, onProgress: (progress: number) => void, 

onResult: (success: boolean, error: ResHubError, resModel: ResHubModel) => void 

): void 

### **6.** 获取资源配置 

#### 接口名称 

```
ResHub.fetchResConfigWithId
```

#### 调用方式 

static fetchResConfigWithId( resId: string, onResult: (success: boolean, error: ResHubError, resModel: ResHubModel) => void 

): void 

### **7.** 删除指定资源 

#### 接口名称 

```
ResHub.deleteWithId
```

#### 调用方式 

static deleteWithId(resId: string): void 

### **8.** 删除所有资源 

#### 接口名称 

```
ResHub.deleteAll
```

#### 调用方式 

static deleteAll(): void 

## 数据结构 

### **RDeliveryData** 

export class RDeliveryData { public key: string; // 配置 key public value: string; // 配置内容 public valueType: RDValueType; // 配置内容类型 public switchState: RDSwitchState; // 开关状态 public debugInfo: string; // 调试信息 } 

### **ResHubModel** 

export class ResHubModel { public resId: string; // 资源 ID public version: number; // 版本号 public size: number; // 文件大小 public md5: string; // MD5 校验值 public downloadUrl: string; // 下载 URL public localPath: string; // 本地路径 public timestamp: number; // 时间戳 public isPresetResource: boolean; // 是否为预置资源 } 

## 错误码 

||错误码||描述|
|---|---|---|---|
|0||成功||
|-1||网络错误||
|-2||参数错误||
|-3||初始化失败||
|-4||资源不存在||
|-5||文件校验失败||
|-6||存储空间不足||
|-7||权限不足||
|-8||配置解析失败||
|-9||服务器错误||
|-10||超时错误||

## 枚举类型 

### **RDValueType** 

export enum RDValueType { String = 0, Json = 1, Int = 2, Bool = 3, Float = 4, List = 5, Map = 6, } 

### **RDSwitchState** 

export enum RDSwitchState { NoSwitch = 0, // 非开关 On = 1, // 开 Off = 2 // 关 } 

### **RDUpdateStrategy** 

export enum RDUpdateStrategy { None = 0, SdkInit = 1, // sdk 初始化时更新 Schedual = 1 << 1, // 定时更新 EnterForceground = 1 << 2, // 热启动更新 NetworkReconnect = 1 << 3 // 断网重连时更新 }
