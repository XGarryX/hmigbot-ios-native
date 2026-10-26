1 

数犀安全组件 SDK 接口指南 

# **数犀安全组件 SDK 接口指南** 

**数犀安全组件 接口指南** 

2 

数犀安全组件 SDK 接口指南 

### **版本历史** 

|版本/状态|作者|参与者|日期|修改记录|
|---|---|---|---|---|
|V1.0.0|||2025/02/20|初始版本|
|V1.0.1|||2025/10/13|添加敏感词、水印配置、设置推 送消息、分享白名单等接口|
|V1.0.2|||2025/10/20|调整分享白名单接口|
|V1.0.3|||2025/11/1|添加设置是否开启管控提示接口|
|V1.0.4|||2026/04/23|添加了隐私合规相关接口|

3 

数犀安全组件 SDK 接口指南 

|目录 数犀安全组件SDK接口指南...................................................................................................................................... 1|
|---|
|1.简介......................................................................................................................................................................... 5|
|2. SDK集成.................................................................................................................................................................. 6|
|3. SDK接口说明.......................................................................................................................................................... 6|
|3.1 设置用户是否同意隐私协议...................................................................................................................... 7|
|3.2 设置是否隐私保护...................................................................................................................................... 7|
|3.3 设置唯一设备**_ID_**......................................................................................................................................... 8|
|3.4 初始化数犀安全组件**_SDK_**........................................................................................................................ 9|
|3.5 激活数犀安全组件服务............................................................................................................................ 10|
|3.6 获取激活状态............................................................................................................................................ 12|
|3.7 擦除数犀安全组件服务............................................................................................................................ 12|
|3.8 设置是否开启管控提示............................................................................................................................ 12|
|3.9 截录屏管控................................................................................................................................................ 13|
|3.10 相机管控.................................................................................................................................................. 13|
|3.11 地理位置管控.......................................................................................................................................... 14|
|3.12 打印机管控.............................................................................................................................................. 14|
|3.13 系统分享管控.......................................................................................................................................... 15|
|3.14 系统分享管控**_,_**设置隐式分享应用白名单........................................................................................... 15|
|3.15 系统分享管控**_,_**设置显式分享应用白名单........................................................................................... 16|
|3.16 系统麦克风管控...................................................................................................................................... 17|

4 

数犀安全组件 SDK 接口指南 

|3.17 剪切板分享管控...................................................................................................................................... 17|
|---|
|3.18 敏感词匹配.............................................................................................................................................. 18|
|3.19 获取用户水印配置.................................................................................................................................. 19|
|3.20 接入推送消息.......................................................................................................................................... 19|
|3.21 分享的方式获取日志.............................................................................................................................. 19|
|3.22 通过接口的方式获取日志...................................................................................................................... 20|
|4. SDK错误说明........................................................................................................................................................ 21|

5 

数犀安全组件 SDK 接口指南 

## **1. 简介** 

数犀安全组件 SDK 用于帮助第三方应用快速集成,实现对移动设备及应用的管理。第三 

方应用开发者只需要下载 HarmonyOS SDK 对应的开发包,导入当前项目中,完成 SDK 的集成 工作。 

通过本文档,开发人员可以快速地完成 SDK 的集成工作。另外,凡是文中没有明确说明 的 IDE,都默认使用 DevEco Studio。 

6 

数犀安全组件 SDK 接口指南 

## **2. SDK 集成** 

### 2.1 **_DevEco Studio_** 配置工程 

添加 SDK 

将 SecurityGuard.har 拷贝到 主项目的目录下并引用 @digitalsee/sandboxsdk,如图所示: 

## **3. SDK 接口说明** 

数犀安全组件 SDK 增加了隐私合规接口,开发者使用安全组件 SDK 需要保证用户同意隐 私协议,设置同意安全组件 SDK 的隐私协议后才能正常使用安全组件 SDK 功能。数犀安全组 件 SDK 调用的入口类为 SXConfiguration 和 SXSecurityGuard 。下面分别对数犀安全组件 SDK API 的接口及调用时机,传参,返回值进行说明。 

7 

数犀安全组件 SDK 接口指南 

### 3.1设置用户是否同意隐私协议 

- u **public static setUserAgreePrivacy(agree: boolean): void** 

接口说明:设置用户是否同意隐私协议,是安全沙箱SDK 初始化前的必选前置条件,如果未设置 

SXSecurityGuard.init 会返回未同意同意隐私协议错误。 

调用时机:需要在SXSecurityGuard.init 前调用。 

#### 传入参数说明: 

|输入参数|参数含义|类型|是否必填|备注|
|---|---|---|---|---|
|agree|**是否同意隐私协议**|**boolean**|是||

#### **Sample Code** : 

import { SXSecurityGuard, SXConfiguration } from '@digitalsee/sandboxsdk' 

SXConfiguration.setUserAgreePrivacy(true) 

### 3.2设置是否隐私保护 

- u **public static setPrivacyProtection(isPrivacyProtection: boolean): void** 

接口说明:设置是否隐私保护,开启后安全沙箱SDK 不再收集设备名称、设备类型、充电状态和电池 

电量状态。 

调用时机:可随时调用,调用后立即生效,建议在SXSecurityGuard.init 前调用。 

传入参数说明: 

8 

数犀安全组件 SDK 接口指南 

|输入参数|参数含义|类型|是否必填|备注|
|---|---|---|---|---|
|isPrivacyProtection|**是否隐私保护**|**boolean**|是||

#### **Sample Code** : 

import { SXSecurityGuard, SXConfiguration } from '@digitalsee/sandboxsdk' 

SXConfiguration.setPrivacyProtection(true) 

### 3.3设置唯一设备 **_ID_** 

#### u **public static setUserDeviceId(deviceId: string): void** 

接口说明:设置唯一设备ID, 是安全沙箱SDK 用户相关接口必选前置条件,如果未设置 

SXSecurityGuard.getAppSession()将返回undefined。 

调用时机:需要在SXSecurityGuard.init 前设置。 

#### 传入参数说明: 

|输入参数|参数含义|类型|是否必填|备注|
|---|---|---|---|---|
|deviceId|**唯一设备ID**|**string**|是|允许大小写字 母、数字、连字|
|||||符,长度 15~64|

9 

数犀安全组件 SDK 接口指南 

#### **Sample Code** : 

import { SXSecurityGuard, SXConfiguration } from '@digitalsee/sandboxsdk' 

SXConfiguration.setUserDeviceId(“deviceId-xxxxxxxxxxxxxxx”) 

### 3.4初始化数犀安全组件 **_SDK_** 

- u **public static init(context: Context, key: string): number** 

接口说明:初始化数犀安全组件SDK 

调用时机:EntryAbility 或者AbilityStage 的onCreate()生命周期方法内 

#### 传入参数说明: 

|输入参数|参数含义|类型|是否必填|备注|
|---|---|---|---|---|
|context|**Context**上下 文|**Context**|是||
|key|**授权码**|**String**|是||

返回值:int 

10 

数犀安全组件 SDK 接口指南 

#### **Sample Code** : 

let ret = SXSecurityGuard.init(this.context, "01b7edd7553778d4428177e556d26867") 

hilog.info(0x0000, 'testTag', 'SXSecurityGuard int: %{public}d', ret); 

- 3.5激活数犀安全组件服务 

- u **public setServerInfo(host: string, port: number, tenantId: string): void** 

- u **public activate(userId: string, callback: (currentType: boolean, err: number) => void):** 

- u **public idTokenActivate(idToken: string, callback: (currentType: boolean, err: number) =>** 

#### **void): void** 

接口说明:用于激活数犀安全服务 

- 调用时机:需要设置唯一设备ID 后才能生效 

- (1). 用户登录成功 

- (2). 进程冷启动时若数犀安全组件服务未激活成功 

传入参数说明: 

|输入参数|参数含义|类型|是否必填|备注|
|---|---|---|---|---|

11 

数犀安全组件 SDK 接口指南 

|host|激活服务器IP|string|是|
|---|---|---|---|
|port|激活服务器端口|number|是|
|tenantId|租户id|string|是|
|userId|用户Id|string|是|
|idToken|idToken|string|是|
|callback|回调类|callback|是|

#### **Sample Code** : 

let appSession = SXSecurityGuard.getAppSession() 

appSession.setServerInfo(serverIP, port, tenantID) 

//用户名方式激活 

appSession.activate(user, (currentType: boolean, err: number) => { 

this.message = '激活' + currentType ? "成功" : "失败" 

}); 

//idToken 方式激活 

appSession.idTokenActivate(idToken, (currentType: boolean, err: number) => { 

this.message = '激活' + currentType ? "成功" : "失败" 

}); 

12 

数犀安全组件 SDK 接口指南 

### 3.6获取激活状态 

- u **public userActivated(): boolean** 

接口说明:查询活数犀安全服务是否激活,需要设置唯一设备ID 后才能生效 

返回值说明:已激活返回true,未激活返回false 

#### **Sample Code** : 

SXSecurityGuard.getAppSession().userActivated() 

### 3.7擦除数犀安全组件服务 

- u **public deactivate()** 

接口说明:用于取消激活数犀安全服务,需要设置唯一设备ID 后才能生效 

调用时机,用户登出后 

#### **Sample Code** : 

let appSession = SXSecurityGuard.getAppSession() 

appSession. deactivate(); 

### 3.8设置是否开启管控提示 

- u **public setToastEnabled(enabled: boolean): void** 

接口说明:设置是否开启管控提示 

传入参数说明: 

13 

数犀安全组件 SDK 接口指南 

|输入参数|参数含义|类型|是否必填|备注|
|---|---|---|---|---|
|Enabled|是否开启管控提示|boolean|是||

#### **Sample Code** : 

SXSecurityGuard.getSandboxManager().setToastEnabled (true) 

### 3.9截录屏管控 

- u **public setScreenDisable(disabled: boolean): void** 

接口说明:设置应用是否允许截录屏 

#### 传入参数说明: 

|输入参数|参数含义|类型|是否必填|备注|
|---|---|---|---|---|
|disabled|是否禁用截录屏|boolean|是||

**Sample Code** : 

SXSecurityGuard.getSandboxManager().setScreenDisable(true) 

### 3.10相机管控 

- u **public setCameraDisable(disabled: boolean): void** 

接口说明:设置应用是否允许使用相机 

传入参数说明: 

14 

数犀安全组件 SDK 接口指南 

|输入参数|参数含义|类型|是否必填|备注|
|---|---|---|---|---|
|disabled|是否禁用相机|boolean|是||

#### **Sample Code** : 

SXSecurityGuard.getSandboxManager().setCameraDisable(true) 

### 3.11地理位置管控 

- u **public setLocationDisable(disabled: boolean): void** 

接口说明:设置应用是否允许使用系统定位 

#### 传入参数说明: 

|输入参数|参数含义|类型|是否必填|备注|
|---|---|---|---|---|
|disabled|是否禁用系统定 位|boolean|是||

#### **Sample Code** : 

SXSecurityGuard.getSandboxManager().setLocationDisable(true) 

### 3.12打印机管控 

- u **public setPrintDisable(disabled: boolean): void** 

接口说明:设置应用是否允许使用打印机 

15 

数犀安全组件 SDK 接口指南 

#### 传入参数说明: 

|输入参数|参数含义|类型|是否必填|备注|
|---|---|---|---|---|
|disabled|是否禁用打印机|boolean|是||

#### **Sample Code** : 

SXSecurityGuard.getSandboxManager().setPrintDisable(true) 

### 3.13系统分享管控 

- u **public setShareDisable(disabled: boolean): void** 

接口说明:设置应用是否允许使用系统分享 

#### 传入参数说明: 

|输入参数|参数含义|类型|是否必填|备注|
|---|---|---|---|---|
|disabled|是否禁用分享|boolean|是||

#### **Sample Code** : 

SXSecurityGuard.getSandboxManager().setShareDisable(true) 

- 3.14系统分享管控 **_,_** 设置隐式分享应用白名单 

- u **public setShareAppLaunchTrustList(string[]): void** 

16 

数犀安全组件 SDK 接口指南 

接口说明:开启禁用应用分享后可以调用此接口设置应用appIdentifier 白名单,白名单应用允许使用 

隐式系统分享,如钉钉appIdentifier 获取方式为hdc shell bm dump -n com.dingtalk.hmos  | 

grep appIdentifier 

#### 传入参数说明: 

|输入参数|参数含义|类型|是否必填|备注|
|---|---|---|---|---|
|trustList|允许分享的应用的appIdentifier 列表|String[]|是||

#### **Sample Code** : 

SXSecurityGuard.getSandboxManager().setShareAppLaunchTrustList(["5765880207854244859", 

"5765880207854012043"]) 

- 3.15系统分享管控 **_,_** 设置显式分享应用白名单 

#### u **public setShareBundleNameWhitelist (string[]): void** 

接口说明:开启禁用应用分享后可以调用此接口设置应用BundleName 白名单,白名单应用允许使用 

显式系统分享。 

#### 传入参数说明: 

|输入参数|参数含义|类型|是否必填|备注|
|---|---|---|---|---|
|whitelist|允许分享的应用的BundleName 列表,|String[]|是||

17 

数犀安全组件 SDK 接口指南 

#### **Sample Code** : 

SXSecurityGuard.getSandboxManager().setShareBundleNameWhitelist (["com.dingtalk.hmos", 

"com.tencent.wechat"]) 

### 3.16系统麦克风管控 

- u **public setMicrophoneDisable(disabled: boolean): void** 

接口说明:设置应用是否允许使用系统麦克风 

#### 传入参数说明: 

|输入参数|参数含义|类型|是否必填|备注|
|---|---|---|---|---|
|disabled|是否禁用麦克风|boolean|是||

#### **Sample Code** : 

SXSecurityGuard.getSandboxManager().setMicrophoneDisable(true) 

### 3.17剪切板分享管控 

- u **public setPasteboardDisable(disabled: boolean): void** 

接口说明:设置应用是否允许使用剪切板 

传入参数说明: 

18 

数犀安全组件 SDK 接口指南 

|输入参数|参数含义|类型|是否必填|备注|
|---|---|---|---|---|
|disabled|是否禁用剪切板|boolean|是||

#### **Sample Code** : 

SXSecurityGuard.getSandboxManager().setPasteboardDisable(true) 

### 3.18敏感词匹配 

#### u **public matchKeywords(message: string): boolean** 

接口说明:匹配文本消息中是否包含服务器下发的敏感词,需要设置唯一设备ID 后才能生效 

#### 传入参数说明: 

|输入参数|参数含义|类型|是否必填|备注|
|---|---|---|---|---|
|message|需要匹配的文本 消息|string|是||

返回值说明:匹配到敏感词返回true,未匹配到敏感词返回false 

#### **Sample Code** : 

let appSession = SXSecurityGuard.getAppSession() 

let find = appSession.matchKeywords(this.text) 

this.message =  (find ? "匹配到" : "未匹配到") 

19 

数犀安全组件 SDK 接口指南 

### 3.19获取用户水印配置 

- u **public getWatermarkConfig(): string** 

接口说明:获取服务器下发的水印配置,需要设置唯一设备ID 后才能生效 

返回值说明:服务器下发的水印配置,类型为JSON 字符串 

#### **Sample Code** : 

let appSession = SXSecurityGuard.getAppSession() 

let config = appSession. getWatermarkConfig() 

### 3.20接入推送消息 

- u **public processPushJson(msg: string): void** 

接口说明:设置钉钉或者其他推送服务,推送给钉保镖的推送消息,需要设置唯一设备ID 后才能生效 

#### 传入参数说明: 

|输入参数|参数含义|类型|是否必填|备注|
|---|---|---|---|---|
|msg|推送消息内容|string|是||

#### **Sample Code** : 

let appSession = SXSecurityGuard.getAppSession() 

let find = appSession. processPushJson (msg) 

### 3.21分享的方式获取日志 

20 

数犀安全组件 SDK 接口指南 

- u **public static async shareLogs(context: common.UIAbilityContext): Promise<void>** 

接口说明:通过分享的方式获取安全沙箱组件日志 

#### 传入参数说明: 

|输入参数|参数含义|类型|是否必填|备注|
|---|---|---|---|---|
|**context**|UI 上下文|**common.UIAbilityContext**|是||

#### **Sample Code** : 

SXSecurityGuard.shareLogs(EntryAbility.uiAbility?.context) 

### 3.22通过接口的方式获取日志 

- u **public static setLogFilter(callback: (level : number, tag: string, msg: string) => void): void** 

   - 接口说明:通过接口方式获取安全沙箱组件日志,应用可以调用此接口将安全沙箱组件日志保存到应 

   - 用的日志组件中,为了保证日志完整建议在SXSecurityGuard.init 调用。 

#### 传入参数说明: 

|输入参数|参数含义|类型|是否必填|备注|
|---|---|---|---|---|
|callback|日志回调|**(level : number, tag:string, msg: string) =>void**|是||

**Sample Code** : 

21 

数犀安全组件 SDK 接口指南 

SXSecurityGuard.setLogFilter((level : number, tag: string, msg: string) => { 

hilog.info(0x0000, TAG, 'SSG[%{public}d] %{public}s: %{public}s', level, tag, msg); }) 

## **4. SDK 错误说明** 

|错误码|错误说明|
|---|---|
|-2000|授权码异常|
|-2001|获取授权码失败|
|-2002|授权码不匹配|
|-3000|用户未同意隐私协议|
