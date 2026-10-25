# **HarmonyOS** 用户运营 **SDK** 集成指南 

## 前言 

* 本文档介绍 DevEco Studio 版本 5.0.3.402 ,鸿蒙 API 12 ,个推用户运营 SDK 集成方式 * 本文档 适用 IDO SDK 版本: 1.0.0.0 及以后 - 本文默认读者已经具有基础的鸿蒙知识,以及项目工程结 构如下: 

Demo/ 

|- entry/ (项目主模块) | |- libs/ (第三方库 , 用户手动创建) | |- src/ (代码目录) | |- oh-package.json5 (模块级 oh-package.json5 文件) |- build-profile.json5 |- hvigorfile.ts |- oh-package.json5 (顶层 oh-package.json5 文件) | ...... 注:其中 “......” 表示省略其他与本教程无关的内容,以下 “......” 表示相同意义,不再重复说明。 ## **1.** 重点提示 ### **1.1** 开发环境配置 - DevEco Studio 版本 5.0.3.402 及以上,鸿蒙 API 12 及以上。 早期需要联系华为技术人员获 取,在其指导下搭建好开发环境 ## **2.** 创建个推应用 请参考 创建应用 获取相应的 `AppID` 信息。该信息在之后的步骤配置中将会使用。 ## **3.** 本地集成 注意:当前只支持本地集成 ### **3.1** 下载配置 **SDK** 的 **har** 包 - 通过官网下载或技术支持获取 ido.har - 在项目主模块 entry 下创建 libs 文件夹 #### 将下载好的 har 包 ido.har 放到 libs 文件夹下 Demo/ |- entry/ (项目主模块) | |- libs/ (第三方库 , 用户手动创建) | |-IDO-HM-1.0.0.0-beta.har ( 个推用户运营 SDK) | ...... ### **3.2** 配置依赖及参数 #### 1. 找到 entry 模块级 oh-package.json5 文件,依赖 ido.har Demo/ |- entry/ (项目主模块) | |- libs/ (第三方库 , 用户手动创建) | |- src/ (代码目录) | | |- main/ | | | |- module.json5 (模块级基本配置文件) | |- oh-package.json5 (模块级 oh-package 文件) | ...... #### 2. oh-package.json5 配置如下: { "name": "entry", "version": "1.0.0", "description": "Please describe the basic information.", "main": "", "author": "", "license": "", "dependencies": { "@getui/ido": "file:./libs/IDO-HM-1.0.0.0-beta.har" } } #### 3. module.json5 配置如下:

配置注册好的 个推 `AppId` 和权限 

{ "module": { ..... "metadata": [ { "name": "GETUI_APPID", "value": " 替换您注册个推 AppId" } ], "requestPermissions": [ { "name": "ohos.permission.INTERNET" }, { "name": "ohos.permission.GET_NETWORK_INFO" }, { "name": "ohos.permission.GET_WIFI_INFO" }, { "name": "ohos.permission.APP_TRACKING_CONSENT", "reason" : "$string:oaid_reason", "usedScene": { "when": "always" } } ] } } 

#### 4. 运行指令 ohpm install 

- 在控制台进入 entry 目录,执行 ohpm install 

- 在 entry 目录下出现 oh_modules 文件夹,代表依赖成功 

## **4.** 集成代码 

### **4.1** 预初始化 

在 `@ohos.app.ability.AbilityStage` 的 `onCreate` 方法中进行预初始化: `Ido.preInit(context: Context)` 

import { Ido, IdoConfig } from '@getui/ido' 

```arkts
export default class MyAbilityState extends AbilityStage { onCreate(): void { // 日志开关 IdoConfig.setDebugEnable(true) // 设置 channel IdoConfig.setChannel('getui_channel') // 预初始化 Ido.preInit(this.context) Ido.setUserId('getui_ido_user') } 
```

### **4.2** 初始化 

在适当时机进行初始化: `init(context: Context): Promise<string>` 

Ido.init(this.context).then((gtcId) => { hilog.info(0x0000, 'IDOAbility', 'IDO init Succeeded. GtcId: (%{public}s)', gtcId); }) 

### **4.3** 应用活跃时长统计 

应用时长统计用于统计应用启动次数和真实活跃时长,初始化 SDK 后不需要开发者调用额外的接 口。 

其中鸿蒙平台一次完整的启动包括如下两种情况: 

1. 从启动应用到关闭应用; 

2. 从启动应用到应用退至后台,且在后台时间超过 30 秒(该值可通过下面的方法修改,单位毫 秒); 

IopConfig.setSessionTimeoutMillis(sessionTimeoutMillis: number) 

### **4.4** 自定义事件 

自定义事件可以统计某些用户自定义埋点的发生时间以及次数,例如广告点击、短信数量等。 

一 通常由 `event_id` 作为一个事件的唯 标识。 

#### 自定义事件分为: 

#### 1. 统计事件: 

   - 计数统计事件:统计指定行为被触发的次数。 

   - 计时统计事件:统计指定行为消耗的时间,单位毫秒。需要 `eventBegin` 和 `eventEnd` 接 口成对使用才可生效。 

2. 用户属性事件:统计对应用户的相关信息。 

每类事件都支持使用 `Map<string, string | number | Date | boolean>` 参数类型,其 中 `key` 必须为字符串类型, `value` 目前支持类型 

有 `string` 、 `Number` 、 `Boolean` 、 `Date` 。 

// 计数统计事件 const map1 = new Map<string, string | number | Date | boolean>() map1.set('test1', 1) map1.set('test2', '2') map1.set('test3', true) map1.set('test4', new Date()) Ido.onEvent('event1', map1) // 计时统计事件 Ido.onBeginEvent('event2') const map2 = new Map<string, string | number | Date | boolean>() map2.set('test1', 1) map2.set('test2', '2') map2.set('test3', true) map2.set('test4', new Date()) Ido.onEndEvent('event2', map2) // 用户属性事件 const map3 = new Map<string, string | number | Date | boolean>() map3.set('test1', 1) map3.set('test2', '2') map3.set('test3', true) map4.set('test4', new Date()) Ido.onProfile(map3) 

## **5.** 预置事件说明 

预置事件主要应用于系统中所有事件相关功能,如 app_start 可在事件分析、用户群等模块选用, 进行对应的分析。 

#### 预置事件由 SDK 自动采集填充,开发者不可修改。 

|事件名称|描述|说明|
|---|---|---|
|`sys_$app_start`|启动app|不区分前后台|
|`sys_$foreground_start`|打开app|仅前台|

## **6.** 预置属性说明 

一 预置属性中包含日常分析常用的 些维度,会由 SDK 自动采集,系统的看板等功能中会用到这些 预置属性用于筛选分析。 

##### 统计事件预置属性 

#### 统计事件的预置属性由 sdk 自动采集填充,开发者不可以修改 : 

|字段名称|类型|说明|
|---|---|---|
|`sys_$wifi`|布尔值|是否使用wif|
|`sys_$carrier`|字符串|运营商名称|
|`sys_$network_type`|字符串|网络类型|
|`sys_$app_version`|字符串|应用版本|
|`sys_$lib_version`|字符串|SDK版本|
|`sys_$manufacturer`|字符串|设备制造商|
|`sys_$model`|字符串|设备型号|
|`sys_$os`|字符串|操作系统|
|`sys_$os_version`|字符串|操作系统版本|
|`sys_$package_name`|字符串|应用包名|

##### 用户属性事件预置属性 

用户属性事件的预置属性分为两部分。一部分是由 SDK 自动采集填充的,如下表: 

|字段名称|类型|说明|
|---|---|---|
|`sys_$app_version`|字符串|应用版本|
|`sys_$channelId`|字符串|渠道|
|`sys_$lib_version`|字符串|SDK版本|
|`sys_$manufacturer`|字符串|设备制造商|
|`sys_$model`|字符串|设备型号|
|`sys_$os`|字符串|操作系统|
|`sys_$os_version`|字符串|操作系统版本|
|`sys_$screen_width`|数值|屏幕宽度|
|`sys_$screen_height`|数值|屏幕高度|
|`sys_$firstvisittime`|日期|首次访问时间|
|`sys_$package_name`|字符串|应用包名|

#### 另一部分需由用户手动设置,如下表: 

|字段名称|类型|说明|
|---|---|---|
|`sys_$country`|字符串|国家|
|`sys_$city`|字符串|城市|
|`sys_$province`|字符串|省份|
|`sys_$name`|字符串|姓名|
|`sys_$sex`|字符串|性别|
|`sys_$phone`|字符串|手机号|
|`sys_$email`|字符串|邮箱|
|`sys_$birthday`|日期|出生日期|
|`sys_$signup_time`|日期|注册时间|
