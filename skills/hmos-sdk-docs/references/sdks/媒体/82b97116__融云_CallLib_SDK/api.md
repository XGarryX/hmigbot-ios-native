# **RTC 融云音视频 ( ) SDK 客户端 文档** HarmonyOS CallLib 1.x 

2025-06-26 

## **目录** 

|导入CallLib SDK|8|
|---|---|
|环境要求|8|
|自动导入SDK|8|
|手动导入SDK|9|
|命令行安装SDK|9|
|entry配置文件依赖SDK|10|
|同步项目|10|
|配置项目|11|
|配置useNormalizedOHMUrl|11|
|添加SDK依赖权限|11|
|实现音视频通话|13|
|步骤1:服务开通|13|
|步骤2:SDK导入|13|
|步骤3:初始化|13|
|步骤4:监听通话事件|14|
|设置监听|14|
|通话呼入|14|
|通话状态变化|15|
|漏接电话|16|
|通话计时|17|
|步骤5:连接IM服务|18|
|步骤6:发起呼叫|18|
|发起单人呼叫|18|
|发起多人呼叫|19|
|步骤7:呼叫接听|19|
|通话管理|20|
|主叫方|20|
|发起呼叫|20|

- 2 - 

|挂断通话|21|
|---|---|
|邀请通话|21|
|被叫方|22|
|接听通话|22|
|默认接听|22|
|拒绝/挂断通话|22|
|通话监听|23|
|来电监听|23|
|通话建立、结束等状态相关的回调|23|
|设备相关回调|26|
|网络质量相关回调|26|
|视频管理|28|
|分辨率/帧率/码率|28|
|设置分辨率|28|
|设置帧率|28|
|设置码率|29|
|摄像头设置|29|
|开关摄像头|29|
|获取摄像头状态|29|
|切换前后置摄像头|30|
|设置视图|30|
|设置本地视图|30|
|设置远端视图|31|
|移除渲染视图|32|
|视频转音频|33|
|监听远端媒体切换|33|
|音频管理|34|
|麦克风设置|34|
|麦克风静音|34|
|获取麦克风状态|34|
|扬声器设置|35|

- 3 - 

|听筒/扬声器切换|35|
|---|---|
|获取扬声器状态|35|
|音频路由|35|
|使用AVCastPicker切换音频路由|35|
|自定义样式实现|36|
|版本说明|37|
|26.1.0 - 2026-2-3|37|
|新增|38|
|25.12.0 - 2025-12-31|38|
|新增|38|
|25.11.0 - 2025-11-28|38|
|修复|38|
|1.10.0 - 2025-10-31|38|
|新增|38|
|1.9.0 - 2025-09-26|38|
|新增|38|
|1.8.0 - 2025-08-29|39|
|修复|39|
|1.7.0 - 2025-07-24|39|
|变更|39|
|1.6.0 - 2025-06-27|39|
|修复|39|
|1.5.0 - 2025-05-29|39|
|新增|39|
|AI智能流式语音识别和翻译|39|
|AI智能流式语音识别|39|
|前置条件|40|
|设置源语言|40|
|参数说明|40|
|示例代码|40|
|注册语音识别结果回调|40|
|语音识别数据结构|40|

- 4 - 

|RCRTCASRContent|40|
|---|---|
|示例代码|41|
|开启语音识别服务|41|
|接口定义|41|
|示例代码|42|
|设置是否接收语音识别|42|
|接口定义|42|
|参数说明|42|
|示例代码|43|
|停止语音识别服务|43|
|接口定义|43|
|示例代码|43|
|语音识别语言代码列表|43|
|AI智能流式语音翻译|45|
|全场景适用|46|
|前置条件|46|
|注册语音翻译结果回调|46|
|语音翻译数据结构|46|
|RCRTCRealtimeTranslationContent|46|
|示例代码|46|
|开启语音翻译|47|
|接口定义|47|
|参数说明|47|
|示例代码|47|
|关闭语音翻译|48|
|接口定义|48|
|示例代码|48|
|语音翻译语言代码列表|48|
|AI智能总结|56|
|全场景适用|56|
|前置条件|56|
|服务开通|56|

- 5 - 

|功能依赖|56|
|---|---|
|注册智能总结回调|57|
|回调方法说明|57|
|didReceiveStartSummarization参数说明|57|
|didReceiveStopSummarization参数说明|57|
|示例代码|57|
|开启智能总结|58|
|接口原型|58|
|示例代码|58|
|关闭智能总结|59|
|接口原型|59|
|示例代码|59|
|生成智能总结|59|
|接口原型|60|
|参数说明|60|
|配置说明|60|
|示例代码|61|
|获取语音转文字|62|
|接口原型|62|
|参数说明|62|
|示例代码|63|
|客户端API|63|
|状态码|63|
|合规指南|64|
|实时音视频CallLib SDK合规使用说明|64|
|一、App个人信息保护的合规要求|65|
|二、App使用CallLib SDK时的合规指引|65|
|1. SDK所需的系统权限的说明|65|
|HarmonyOS操作系统SDK功能、接口配置方式及示例说明:|65|
|2. SDK初始化及业务功能调用时机说明|66|
|3. SDK隐私政策披露要求与示例说明|67|
|4.最终用户同意方式的建议方式说明及示例|67|

- 6 - 

|5.最终用户行使权利的配置说明|70|
|---|---|
|三、合规文件指引|71|
|四、联系方式|71|

- 7 - 

#### **导入 CallLib SDK** 

融云支持使用 DevEco Studio 中自动导入和手动导入两种方式,将 CallLib SDK 导入到您的应用工程中。 

###### **环境要求** 

DevEco Studio NEXT Release(5.0.3.900) 及以上。 

- HarmonyOS SDK API 12 及以上。 

- 手机(真机)系统版本号:NEXT.0.0.31 

###### **自动导入 SDK** 

1.0.0 版本开始支持 OpenHarmony三方库中心获取 SDK 

1. 在 entry 目录中的 oh-package.json5 中添加 SDK 依赖,然后点击 "Sync Now"。 

###### **JSON** 

// entry 目录中的 oh-package.json5 { "name": "entry", "version": "1.0.0", "description": "Please describe the basic information.", "main": "", "author": "", "license": "", "dependencies": { "@rongcloud/calllib" : "x.y.z", "@rongcloud/imlib" : "x.y.z", "@rongcloud/rtclib" : "x.y.z" } } 

###### **注意** 

   - 各个 SDK 的最新版本号可能不相同,具体 x.y.z 值可前往 融云官网 SDK 下载页面 或 OpenHarmony三方库中心 查询。 

1. 安装 SDK 成功后,您可以在项目根目录的 **oh_modules/.ohpm/** 中找到融云 callLib SDK。 

2. 查看更多其他融云 SDK。 打开OpenHarmony三方库中心,搜索关键字 **rongcloud** 

- 8 - 

###### **手动导入 SDK** 

1. 在导入 SDK 前,您需要前往融云官网 SDK 下载页面,将音视频通话(无 UI)SDK 下载到本地。 

2. 创建 **./libs** 文件夹,将 SDK **har 包** 放入其中。 

##### **命令行安装 SDK** 

1. 在工程根路径下执行以下命令行: 

###### **shell** 

ohpm install libs/Calllib.har 

2. 执行完后,工程根路径的 oh-package.json5 就会依赖 SDK。 

###### **JSON** 

- 9 - 

// 工程根路径下的 oh-package.json5 { "name": "xxx", "version": "1.0.0", "description": "Please describe the basic information.", "main": "", "author": "", "license": "", "dependencies": { "@rongcloud/calllib": "file:libs/CallLib.har", // 该配置由命令行生成 }, "devDependencies": { "@ohos/hypium": "1.0.16", "@ohos/hamock": "1.0.0" } } 

##### **entry 配置文件依赖 SDK** 

在 **entry** 同级目录的 oh-package.json5 手动配置 SDK 依赖。 

###### **JSON** 

// entry 同级目录下的 oh-package.json5 需要手动配置 { "name": "xxx", "version": "1.0.0", "description": "Please describe the basic information.", "main": "", "author": "", "license": "", "dependencies": { "@rongcloud/calllib": "file:../libs/CallLib.har",  // 该配置手动依赖 "@rongcloud/imlib": "file:../libs/RongIMLib.har",  // 该配置手动依赖 "@rongcloud/rtclib": "file:../libs/RTCLib.har" // 该配置手动依赖 }, "devDependencies": { "@ohos/hypium": "1.0.16", "@ohos/hamock": "1.0.0" } } 

##### **同步项目** 

- 10 - 

在 entry/oh-package.json5 中点击 **Sync Now** 同步工程,同步成功之后即可正常使用 CallLib SDK。 

提示

如果您同步之后依然无法导入 SDK,这可能是 DevEco Studio 的编译缓存导致的问题。您可以尝试把 DevEco Studio 完全关闭之后重新打开 APP 工程来解决问题。 

###### **配置项目** 

##### **配置 useNormalizedOHMUrl** 

1.0.0 版本开始 SDK 支持字节码,为了支持字节码,app 需要在项目根路径配置 **useNormalizedOHMUrl** 。 

// app 根路径下的 build-profile.json5 { "app": { "products": [ { "buildOption": { "strictMode": { "useNormalizedOHMUrl": true } } } ] } } 

###### **添加 SDK 依赖权限** 

SDK 需要权限如下: 

- 11 - 

|权限名称|权限说明|使用目的|
|---|---|---|
|ohos.permission.GET_NETWORK_INFO|获取网络信息|网络变化之后获取网络信息,进行IM重连|
|ohos.permission.INTERNET|使用网络|连接IM、收发消息需要网络连接|
|ohos.permission.STORE_PERSISTENT_DATA|数据存储|消息数据库需要本地存储|
|ohos.permission.MICROPHONE|麦克风权限|音频通话需要麦克风采集能力|
|ohos.permission.CAMERA|摄像头权限|视频通话需要摄像头采集能力|

1. 找到项目 entry/src/main/ 目录下的 module.json5 文件,添加 requestPermissions 配置,以配置摄像头权限为例: 

###### **JSON** 

"requestPermissions": [ { "name": "ohos.permission.CAMERA", "reason": "$string:Camera", "usedScene": { "abilities": [ "EntryAbility", ], "when": "always" } }, ... // 配置其他权限 ] 

###### 具体权限配置参数含义,请参考鸿蒙的应用权限管控文档。 

2. 配置权限时,按照规则需要考虑国际化问题,在项目 entry/src/main/resources/base/element 目录下找到 string.json 文件,对应增加配置字符变量,以配置摄像头字符变量为例: 

###### **JSON** 

{ "string": [ { "name": "Camera", "value": "Camera in RTC" }, ... // 定义其他 ] } 

- 12 - 

#### **实现音视频通话** 

CallLib 是在 RTCLib 基础上,额外封装了一套音视频呼叫功能 SDK,包含了单人、多人音视频呼叫的各种场景和功能,通过 集成它,您可以自由的实现音视频呼叫场景的各种玩法。 

**注意** 

**房间人数上限** 

考虑移动设备的带宽(主要是在多路视频情况下),建议单次通话或房间内,视频不超过 16 人,纯音频不超过 32 人。超过此上限可能影响通话效果。 

###### **步骤 1 :服务开通** 

您在融云创建的应用默认不会启用音视频服务。在使用融云提供的任何音视频服务前,您需要前往控制台,为应用开通音视频 服务。 

**注意** 

服务开通、关闭等设置完成后 15 分钟后生效。 

###### **步骤 2 : SDK 导入** 

您需要导入融云音视频通话能力库 CallLib,和 RTC 业务所依赖的即时通讯能力库 IMLib。根据您的业务需求,可选择导入美 颜扩展库。 

具体步骤请参阅 导入 CallLib SDK。 

###### **步骤 3 :初始化** 

###### 重要提示 

从 1.9.0 版本开始,必须先调用 CallClientInstance.install() 方法加载 CallLib 模块,且该方法必须在 IM 初始化之前调 用。 

CallLib 是基于 IM 作为信令通道的,所以要先初始化 IM。如果不换 App Key,在整个应用生命周期中,初始化一次即可。建 议调用位置放在应用启动位置处,或在音视频功能模块的加载位置处。 在 UIAbility 的 onCreate() 方法中,调用初始化方 法,传入生产或开发环境的 App Key。 

###### **TypeScript** 

- 13 - 

//1.9.0 版本新增方法:加载 CallLib 模块,必需在 IM 初始化之前调用。 CallClientInstance.install(); // 在 UIAbility 中获取 context let context = this.context let initOption = new InitOption(); let appKey = "从融云后台获取的 appKey"; IMEngine.getInstance().init(context, appKey, initOption); 

###### **步骤 4 :监听通话事件** 

SDK 提供针对来电、通话状态、通话记录的事件处理机制。 

##### **设置监听** 

以下示例代码,新建一个 CallListenerImpl 类实现 RCCallClientListener 接口。并将实例设置给 SDK 。 

###### **TypeScript** 

// 在所需要的类声明 _callClient 私有成员变量,后续示例中使用 private _callClient: RCCallClient | null = null ... /** * RCCallClient 单例 * export const CallClientInstance: RCCallClient = CallClientImpl.getInstance() */ // 创建 _callClient 成员变量,供后续示例代码使用 this._callClient = CallClientInstance // 设置监听 this._callClient.callClientListener = new CallListenerImpl() 

##### **通话呼入** 

通过实现 RCCallClientListener 中的 didReceiveCall 来监听通话呼入。 

###### **TypeScript** 

- 14 - 

```arkts
export class CallListenerImpl implements RCCallClientListener { /** * 收到通话呼入的回调 * @param callSession 通话实例 * @remarks 代理 */ didReceiveCall(callSession: RCCallSession): void { console.log('didReceiveCall', callSession) } } 
```

##### **通话状态变化** 

通过实现 RCCallClientListener 的通话连接,断开连接,人员变动来监听通话状态的变化。 

###### **TypeScript** 

- 15 - 

export class CallListenerImpl implements RCCallClientListener { 

/** 

- 挂断通话的回调 

- @param callSession 通话实例 

- @param callDisconnectReason 通话挂断原因 

- @remarks 代理 

*/ 

didCallDisconnected(callSession: RCCallSession, callDisconnectReason: RCCallDisconnectReason): void { 

} 

- /** 

- 远端用户加入通话的回调 

- @param callSession 通话实例 

- @param userId 用户 ID 

- @param mediaType 媒体类型 

- @remarks 代理 

*/ 

didRemoteUserJoined(callSession: RCCallSession, userId: string, mediaType: RCCallMediaType): void { 

} 

- /** 

- 远端用户挂断通话的回调 

- @param callSession 通话实例 

- @param userId 用户 ID 

- @param callDisconnectReason 通话挂断原因 

- @remarks 代理 

*/ 

didRemoteUserLeft(callSession: RCCallSession, userId: string, callDisconnectReason: 

RCCallDisconnectReason): void { 

} 

} 

##### **漏接电话** 

通过实现 RCCallClientListener 中的 didMissCall 来监听漏接的通话。 

###### **TypeScript** 

- 16 - 

/** 

* 收到通话漏接的回调 

- @param callSession 通话实例 

- @remarks 代理 

*/ 

didMissCall(callSession: RCCallSession): void { 

} 

##### **通话计时** 

CallLib SDK 无法直接获取通话时长,您可以在通话建立成功、音频首帧回调、或视频首帧回调方法中,使用当前时间减去通 话起始时间,获取通话时长。 

###### **TypeScript** 

/** 

- 接通通话的回调 

- @param callSession 通话实例 

- @remarks 代理 

- */ 

didCallConnected(callSession: RCCallSession): void { 

} 

- /** 

- 收到远端用户音频首帧的回调 

- @param callSession 通话实例 

- @param userId 用户 ID 

- @remarks 代理 

- */ 

didReceiveFirstRemoteAudio(callSession: RCCallSession, userId: string): void { 

- } /** 

- 收到远端用户视频首帧的回调 

- @param callSession 通话实例 

- @param userId 用户 ID 

- @remarks 代理 

- */ 

didReceiveFirstRemoteVideo(callSession: RCCallSession, userId: string): void { 

} 

提示

- 17 - 

如需在应用程序的服务端进行通话计时,建议使用融云提供的服务端回调音视频房间状态同步。通过实时回调事件 event 11(成员加入音视频房间)和 event 12(成员加入音视频房间)记录计费的开始和结束时间。 

###### **步骤 5 :连接 IM 服务** 

音视频用户之间的信令传输依赖于融云的即时通信(IM)服务,因此需要先调用 connect 与 IM 服务建立好 TCP 长连接。建 议在功能模块的加载位置处调用,之后再进行音视频呼叫业务。当模块退出后调用 disconnect 断开该连接。 

###### **TypeScript** 

###### // 连接 IM 

IMEngine.getInstance().connect(token, 20).then(result => { 

if (EngineError.Success === result.code) { 

   - // 连接成功 

   - let userId = result.userId; 

- return 

- } 

if (EngineError.ConnectTokenExpired === result.code) { 

   - // Token 过期,从 APP 服务请求新 token,获取到新 token 后重新 connect() 

- } else if (EngineError.ConnectionTimeout === result.code) { 

   - // 连接超时,弹出提示,可以引导用户等待网络正常的时候再次点击进行连接 

- } else { 

   - //其它业务错误码,请根据相应的错误码作出对应处理。 

- } 

}); 

###### **步骤 6 :发起呼叫** 

连接 IM 服务成功后,可调用 RCCallClient 中的 startCall 方法来发起通话。 

##### **发起单人呼叫** 

###### **TypeScript** 

- 18 - 

###### /// 定义两个成员变量 

private _callClient: RCCallClient = CallClientInstance 

private _callSession: RCCallSession 

###### /// 发起单人呼叫 

let callType = RCCallType.SINGLE; let targetId = 'userId' let userIds: string[] = ['userId'] let mediaType = RCCallMediaType.AUDIO let extra = 'extra' 

this._callClient.startCall(callType, targetId, userIds, mediaType, extra) .then((res) => { 

if(res.isSuccess){ this._callSession = res.callSession } else { 

" console.error( 呼叫失败, Code=" + RCCallErrorCode[res.code]) } }) 

##### **发起多人呼叫** 

###### **TypeScript** 

###### /// 发起多人呼叫 

let callType = RCCallType.MULTI; let targetId = 'groupId' let userIds: string[] = ['userId'] let mediaType = RCCallMediaType.AUDIO let extra = 'extra' 

this._callClient.startCall(callType, targetId, userIds, mediaType, extra) .then((res) => { if(res.isSuccess){ this._callSession = res.callSession } else { " console.error( 呼叫失败, Code=" + RCCallErrorCode[res.code]) } }) 

###### **步骤 7 :呼叫接听** 

在收到 didReceiveCall 回调之后,调用如下方法接听通话。 

- 19 - 

**TypeScript** 

didReceiveCall(callSession: RCCallSession): void { this._callClient.accept() 

} 

### **通话管理** 

###### **主叫方** 

##### **发起呼叫** 

调用 RCCallClient 的 startCall 方法发起单人或多人音视频通话,该方法默认打开前置摄像头。多人通话场景所有通话者必 须在一个群组内。 

###### 参数说明: 

|参数|类型|必填|说明|
|---|---|---|---|
|callType|RCCallType|是|会话类型|
|targetId|string|是|目标会话ID,单人通话为对方UserId,群组通话为GroupId|
|userIds|string[]|是|邀请参与通话的用户ID列表,不能为null|
|callMediaTyp|e RCCallMediaTy|pe 是|通话媒体类型,音频或者音视频|
|extra|string|否|附加信息,透传至对端,对端通过RCCallSession.extra()获取|
|返回值: 返回值|返回类型|说明||
|isSuccess|boolean|发起呼叫|成功/失败|
|code|RCCallErrorCode|成功返回|SUCCESS,失败时返回对应错误码|
|callSession|RCCallSession|呼叫成功|,返回当前会话对象|

示例代码: 

###### **TypeScript** 

- 20 - 

/// 定义两个成员变量 

private _callClient: RCCallClient = CallClientInstance private _callSession: RCCallSession 

/// 发起单人呼叫 let callType = RCCallType.SINGLE; let targetId = 'userId' let userIds: string[] = ['userId'] let mediaType = RCCallMediaType.AUDIO let extra = 'extra' 

this._callClient.startCall(callType, targetId, userIds, mediaType, extra) .then((res) => { if(res.isSuccess){ this._callSession = res.callSession } else { " console.error( 呼叫失败, Code=" + RCCallErrorCode[res.code]) } }) 

##### **挂断通话** 

调用 RCCallClient 类的 hangup 方法挂断通话,拒绝和挂断为同一个方法,SDK 内部会通过 didCallDisconnected 回调拒 绝原因以及相关信息。 

示例代码: 

###### **TypeScript** 

/// 引用上述私有变量 this._callClient this._callClient.hangup() 

##### **邀请通话** 

调用 RCCallClient 类的 invite 方法邀请用户加入当前通话(仅限群组),该方法必须在通话已经建立onCallConnected 之 后调用。 

###### 参数说明: 

参数 类型 必填 说明 userIds string[] 是 邀请的用户 ID 列表 

返回值: 

- 21 - 

返回值 返回类型 说明 

code RCCallErrorCode 成功返回 SUCCESS,失败有对应错误码 

示例代码: 

###### **TypeScript** 

/// 邀请必须是群呼模式,邀请的用户 id 必须是群组内的人员 let res = this._callClient.invite(['userId1','userId2']) 

###### **被叫方** 

##### **接听通话** 

##### **默认接听** 

当收到来自 didReceiveCall 的远端通话请求时,可使用 RCCallClient 的 accept 方法来接听。该方法默认打开前置摄像 头。 

示例代码: 

###### **TypeScript** 

didReceiveCall(callSession: RCCallSession): void { this._callClient.accept() } 

##### **拒绝 / 挂断通话** 

调用 RCCallClient 的 hangup 方法挂断通话,拒绝和挂断为同一个方法,SDK 内部会通过 didCallDisconnected 告知对方 挂断、拒绝原因。 

示例代码: 

###### **TypeScript** 

/// 引用上述私有变量 this._callClient this._callClient.hangup() 

- 22 - 

###### **通话监听** 

融云鸿蒙版 CallLib 库提供了 RCCallClientListener 监听, 用于处理呼叫相关的业务逻辑上报。 

##### **来电监听** 

需要设置 CallLib 的全局通话监听 RCCallClientListener,来监听通话呼入。 

- 收到新通话,返回当前通话的详细信息。 

- 漏接的通话,返回当前通话的详细信息。 

###### **TypeScript** 

this._callClient.callClientListener = { 

/** 

- 收到通话呼入的回调 

- @param callSession 通话实例 

- @remarks 代理 

didReceiveCall(callSession: RCCallSession): void { 

/** 

- 收到通话漏接的回调 

- @param callSession 通话实例 

- @remarks 代理 

didMissCall(callSession: RCCallSession): void { 

} } 

##### **通话建立、结束等状态相关的回调** 

- 收到新通话,返回当前通话的详细信息。 

- 已建立通话,返回当前通话的详细信息。 

- 通话结束。对方挂断,己方挂断,或者通话过程网络异常造成的通话中断,都会通过同一个回调返回原 因RCCallDisconnectReason 。 

被叫端正在振铃,返回振铃用户的用户 ID。 

- 被叫端加入通话,返回加入者的用户信息和摄像头信息。 

- 通话中的某一个参与者,邀请好友加入通话。返回被邀请者的信息和媒体类型。 

- 通话中的远端参与者离开,返回离开者的信息和离开原因 RCCallDisconnectReason 。在多人通话与 1v1 通话中,对 

- 端挂断均会先回调 didRemoteUserLeft ,再触发其他回调。 

- 23 - 

当通话中的某一个参与者切换通话类型,例如由视频切换至音频。返回切换操作者的信息、切换后的媒体类型等。 通话过程中,发生异常。返回错误码 RCCallErrorCode。 

需在 this._callClient.callClientListener 中添加以下监听: 

###### **TypeScript** 

/** 

- 收到通话呼入的回调 

- @param callSession 通话实例 

- @remarks 代理 

*/ 

didReceiveCall(callSession: RCCallSession): void { 

}, 

/** 

- 接通通话的回调 

- @param callSession 通话实例 

- @remarks 代理 

*/ 

didCallConnected(callSession: RCCallSession): void { 

}, 

/** 

- 挂断通话的回调 

- @param callSession 通话实例 

- @param callDisconnectReason 通话挂断原因 

- @remarks 代理 

*/ 

didCallDisconnected(callSession: RCCallSession, callDisconnectReason: RCCallDisconnectReason): void { 

}, 

/** 

- 远端用户正在响铃的回调 

- @param callSession 通话实例 

- @param userId 用户 ID 

- @remarks 代理 

- */ 

didRemoteUserRinging(callSession: RCCallSession, userId: string): void { 

}, 

/** 

- 远端用户被邀请加入通话的回调 

- @param callSession 通话实例 

- @param userId 用户 ID 

- 24 - 

用户 

@p 

###### * @remarks 代理 

*/ 

didRemoteUserInvited(callSession: RCCallSession, userId: string): void { 

}, 

/** 

- 远端用户加入通话的回调 

- @param callSession 通话实例 

- @param userId 用户 ID 

- @param mediaType 媒体类型 

- @remarks 代理 

*/ 

didRemoteUserJoined(callSession: RCCallSession, userId: string, mediaType: RCCallMediaType): void { 

}, 

/** 

- 远端用户挂断通话的回调 

- @param callSession 通话实例 

- @param userId 用户 ID 

- @param callDisconnectReason 通话挂断原因 

- @remarks 代理 

- */ 

didRemoteUserLeft(callSession: RCCallSession, userId: string, callDisconnectReason: RCCallDisconnectReason): void { 

}, 

/** 

- 远端用户切换了媒体类型的回调 

- @param callSession 通话实例 

- @param userId 用户 ID 

- @param mediaType 媒体类型 

- @remarks 代理 

*/ 

didRemoteUserChangeMediaType(callSession: RCCallSession, userId: string, mediaType: RCCallMediaType): void { 

}, 

/** 

- 错误回调 

- @param callSession 通话实例 

- @param code 错误码 

- 25 - 

p * @remarks 代理 */ 

didOccurError(callSession: RCCallSession, code: RCCallErrorCode): void { 

} 

##### **设备相关回调** 

远端参与者摄像头状态发生变化时,回调 didRemoteUserDisableCamera 通知状态变化。 

远端参与者麦克风状态发生变化时,回调 didRemoteUserDisableMic 通知状态变化。 

需在 this._callClient.callClientListener 中添加以下监听: 

###### **TypeScript** 

/** 

- 远端用户开关麦克风的状态变化回调 

- @param callSession 通话实例 

- @param userId 用户 ID 

- @param disable 是否关闭 

- @remarks 代理 

*/ 

didRemoteUserDisableMic(callSession: RCCallSession, userId: string, disable: boolean): void { 

}, 

/** 

- 远端用户开关摄像头的状态变化回调 

- @param callSession 通话实例 

- @param userId 用户 ID 

- @param disable 是否关闭 

- @remarks 代理 

- */ 

didRemoteUserDisableCamera(callSession: RCCallSession, userId: string, disable: boolean): void { 

} 

##### **网络质量相关回调** 

- 音频声音大小的回调,返回用户 ID 及音量大小 

- 发送丢包率信息回调,返回丢包率及发送端的网络延迟。 

- 接收丢包率信息回调,返回远端用户 ID 及丢包率。 

- 收到某个用户的第一帧视频数据,返回用户信息及宽高数据。 

- 26 - 

需在 this._callClient.callClientListener 中添加以下监听: 

###### **TypeScript** 

/** 

* 音频声音大小的回调 

* 

- @param callSession 通话实例 

- @param userId 用户 ID 

- @param audioLevel 声音级别:0~9,0 为无声,依次变大 

* 

###### * @remarks 代理 

*/ 

didAudioLevelChanged(callSession: RCCallSession, userId: string, audioLevel: number): void { 

}, 

/** 

* 上行丢包率及延迟信息的回调 

* 

- @param callSession 通话实例 

- @param packetLostRate 丢包率,0-100 

- @param delay 发送端的网络延迟,单位毫秒 

* 

- @discussion 每秒回调一次 

- @remarks 代理 

*/ 

didSendPacketLost(callSession: RCCallSession, packetLostRate: number, delay: number): void { 

}, 

/** 

- 下行丢包率及延迟信息的回调 

* 

- @param callSession 通话实例 

- @param userId 用户 ID 

- @param packetLostRate 丢包率,0-100 

* 

- @discussion 每秒回调一次 

- @remarks 代理 

*/ 

didReceivePacketLost(callSession: RCCallSession, usedId: string, packetLostRate: number): void { 

} 

/** 

- 27 - 

/** * 收到远端用户视频首帧的回调 * 

* @param callSession 通话实例 * @param userId 用户 ID * * @remarks 代理 */ 

didReceiveFirstRemoteVideo(callSession: RCCallSession, userId: string): void { 

} 

### **视频管理** 

###### **分辨率 / 帧率 / 码率** 

CallLib 提供 RCCallVideoConfig 视频配置类,用户可以在发起通话和接听通话前创建此对象,预设分辨率、帧率、码率, 在后续通话中生效。 

##### **设置分辨率** 

默认情况下,SDK 使用默认分辨率 RCCallVideoResolution.SIZE_480_360。 

修改 RCCallVideoConfig 的 videoResolution 调整分辨率。 

示例代码: 

###### **TypeScript** 

// 创建 videoConfig 对象,后续示例使用该实例 let videoConfig = new RCCallVideoConfig() videoConfig.videoResolution = RCCallVideoResolution.SIZE_480_360 this._callClient.videoConfig = videoConfig 

##### **设置帧率** 

默认情况下,SDK 使用默认帧率 Fps_15。 

在发起通话和接听通话前,可以修改 RCCallVideoConfig 的 videoFps 调整设置帧率,支持的帧率为 FPS_10、FPS_15、FPS_24、FPS_30。 

示例代码: 

- 28 - 

**TypeScript** 

videoConfig.videoFps = RCCallVideoFrameRate.FPS_15 this._callClient.videoConfig = videoConfig 

##### **设置码率** 

码率需要设置 minBitrate 和 maxBitrate,单位是 kb/s,通话过程中 SDK 上行数据会在用户设置的码率范围之内浮动。 

示例代码 

###### **TypeScript** 

videoConfig.maxBitrate = 1500 videoConfig.minBitrate = 200 this._callClient.videoConfig = videoConfig 

###### **摄像头设置** 

##### **开关摄像头** 

调用 RCCallClient 的 setCameraEnabled 方法打开或者关闭摄像头采集。 通话前开启摄像头采集对端 **不会收到** didRemoteUserDisableCamera 通知。 

###### 参数说明 

参数 类型 说明 enable boolean 是否开启摄像头 

返回值: 

返回值 类型 说明 code RCCallErrorCode 成功返回 SUCCESS,失败有对应错误码 

示例代码: 

###### **TypeScript** 

let res = this._callClient.setCameraEnabled(true); 

##### **获取摄像头状态** 

在使用 setCameraEnabled 后,SDK 会记录对应摄像头是否开启状态,后续通过 getCameraEnabled 方法获取摄像头状 

- 29 - 

态。 

###### 示例代码: 

###### **TypeScript** 

let cameraEnable = this._callClient.getCameraEnabled() 

##### **切换前后置摄像头** 

在通话过程中,调用 switchCamera 方法切换前后置摄像头,返回接口的调用结果,成功或者失败,该方法同样适用于采集 前。 

示例代码: 

###### **TypeScript** 

let res = this._callClient.switchCamera(); 

###### **设置视图** 

##### **设置本地视图** 

1. 在发起呼叫前,可以通过开启摄像头和设置本地视图来实现预览效果,调用 RCCallClient 的 setVideoView 方法,将 创建好的 RCCallVideoView 对象以及当前用户的 userId 传入即可。 

2. 结合 ArkTS XComponent 组件渲染视图,保证 RCCallVideoView 的 viewId 与 XComponent 的 id 一致且唯 一,建议使用 userId 。 

参数说明: 

|参数|类型|必填|说明|
|---|---|---|---|
|userId|string|是|用户id|
|videoView|RCCallVideoView|否|渲染视图对象|

示例代码: 

###### **TypeScript** 

- 30 - 

@Component 

export struct MyStruct { 

///一般使用用户真实的 userId localViewId: string = 'localUserId' private _callClient: RCCallClient = CallClientInstance } 

###### **TypeScript** 

XComponent({ 

id: this.localViewId, 

type: XComponentType.SURFACE, libraryname: 'nativerender' }) .onLoad((xComponentContext) => { 

/// 设置本地视图 

// RCRTCVideoFillMode 表示渲染模式 

let videoView = new RCCallVideoView(this.localViewId, RCRTCVideoFillMode.ASPECT_FILL) this._callClient.setVideoView(this.localViewId, videoView) 

}) 

.onAreaChange((oldValue: Area, newValue: Area) => { 

console.info("onAreaChange: newValue:" + JSON.stringify(newValue) + " , oldValue:" + JSON.stringify(oldValue)) 

}) 

.onSizeChange((oldValue: SizeOptions, newValue: SizeOptions) => { console.info("onSizeChange: newValue:" + JSON.stringify(newValue) + " , oldValue:" + JSON.stringify(oldValue)) 

}) .height('100%') .width('100%') 

##### **设置远端视图** 

使用远端用户的 userId 构建 RCCallVideoView 对象当做参数,同样使用 setVideoView 方式可设置远端视图, 无论是在 通话前或者通话中设置,SDK 会在拿到远端视频流数据后,寻找对应用户设置的 RCCallVideoView 视图并按需渲染。 

参数说明: 

|参数|类型|必填|说明|
|---|---|---|---|
|viewId|string|是|视图id,用来渲染时使用,保证唯一性|
|fllMode|RCRTCVideoFillMode|是|渲染模式,默认是ASPECT_FILL|

示例代码: 

- 31 - 

###### **TypeScript** 

###### /// 设置远端视图 

@Component export struct MyStruct { ///一般使用用户真实的 userId remoteViewId: string = 'remoteUserId' private _callClient: RCCallClient = CallClientInstance } 

###### **TypeScript** 

XComponent({ id: this.remoteViewId, type: XComponentType.SURFACE, libraryname: 'nativerender' 

}) .onLoad((xComponentContext) => { /// 设置远端渲染视图 

// RCRTCVideoFillMode 表示渲染模式 

let videoView = new RCCallVideoView(this.remoteViewId, RCRTCVideoFillMode.ASPECT_FILL) this._callClient.setVideoView(this.remoteViewId, videoView) }) 

.onAreaChange((oldValue: Area, newValue: Area) => { console.info("onAreaChange: newValue:" + JSON.stringify(newValue) + " , oldValue:" + JSON.stringify(oldValue)) 

}) 

.onSizeChange((oldValue: SizeOptions, newValue: SizeOptions) => { console.info("onSizeChange: newValue:" + JSON.stringify(newValue) + " , oldValue:" + JSON.stringify(oldValue)) }) .height('100%') .width('100%') 

##### **移除渲染视图** 

当设置过视图后,如果需要移除该视图,还是使用 setVideoView 方法传入相同 userId ,参数 videoView 传 null,SDK 会根据传入的 userId 移除对应的视图。 

示例代码: 

###### **TypeScript** 

- 32 - 

###### /// 移除远端视图 

this._callClient.setVideoView(this.remoteViewId, null) /// 移除本地视图 

this._callClient.setVideoView(this.localViewId, null) 

###### **视频转音频** 

##### **视频转音频** 

当用户希望从视频通话转为音频时,可以调用 RCCallClient 的 changeCallMediaType 方法。目前仅支持视频转音频,即参 数只能为 RCCallMediaType.AUDIO。 

###### 参数说明 

参数 类型 说明 callMediaType RCCallMediaType 通话媒体类型 返回值: 返回值 类型 说明 code RCCallErrorCode 成功返回 SUCCESS,失败有对应错误码 

示例代码: 

###### **TypeScript** 

let res = this._callClient.changeCallMediaType(RCCallMediaType.AUDIO) 

##### **监听远端媒体切换** 

当通话中对端用户调用 changeCallMediaType 做音视频切换至音频时,本端会通过 RCCallClientListener 的 didRemoteUserChangeMediaType 回调监听到结果。 

示例代码: 

###### **TypeScript** 

- 33 - 

```arkts
this._callClient.callClientListener = { /** * 远端用户切换了媒体类型的回调 * * @param callSession 通话实例 * @param userId 用户 ID * @param mediaType 媒体类型 * * @remarks 代理 */ didRemoteUserChangeMediaType(callSession: RCCallSession, userId: string, mediaType: RCCallMediaType): void { ///TODO: 通知业务层 } } 
```

### **音频管理** 

###### **麦克风设置** 

##### **麦克风静音** 

当通话中希望关闭麦克风,可调用 RCCallClient 的 setMute 接口,传入 true 达到本地静音效果;当需要再次打开时,传入 false 即可。默认值为 false,即麦克风默认为打开状态。 

示例代码: 

###### **TypeScript** 

this._callClient.setMute(true) 

##### **获取麦克风状态** 

通过 setMute 方法设置麦克风是否静音,后续可以通过 getMute 获取麦克风是否被静音。 正在通话中,对端可通过监听 didRemoteUserDisableMic,收到远端用户麦克风开关状态变更通知。 

示例代码: 

###### **TypeScript** 

- 34 - 

let mute = this._callClient.getMute() 

###### **扬声器设置** 

##### **听筒 / 扬声器切换** 

当通话中希望切换声音由扬声器或听筒输出时,可调用 RCCallClient 的 setSpeakerEnabled 来设置。传入 true 代表使用 扬声器播放;false 代表使用听筒播放。默认是 false,即默认使用听筒播放。 

示例代码: 

###### **TypeScript** 

/// 设置扬声器播放 

this._callClient.setSpeakerEnabled(true); 

##### **获取扬声器状态** 

通过 setSpeakerEnabled 设置扬声器,SDK 会记录该状态,后续可以通过 getSpeakerEnabled 来获取是否启用扬声器。 

示例代码: 

###### **TypeScript** 

/// 是否扬声器播放 

let enable = this._callClient.getSpeakerEnabled() 

###### **音频路由** 

由于鸿蒙系统不再提供音频输出设备切换的API,如果需要应用内切换音频输出设备,请实现系统提供的 AVCastPicker 组 件,相关参数可参考使用通话设备切换组件 

##### **使用 AVCastPicker 切换音频路由** 

1. 创建 voice_call 类型的 AVSession , AVSession 在构造方法中支持不同的类型参数,由 AVSessionType 定 义, voice_call 表示通话类型,如果不创建,将显示空列表。 

###### **TypeScript** 

- 35 - 

```arkts
import { avSession } from '@kit.AVSessionKit'; 
```

private session: avSession.AVSession | undefined = undefined; 

// 通话开始时创建voice_call类型的avsession this.session = await avSession.createAVSession(getContext(this), 'voiptest', 'voice_call'); 

2. 在需要切换设备的通话界面创建 AVCastPicker 组件。 

###### **TypeScript** 

```arkts
import { AVCastPicker } from '@kit.AVSessionKit'; 
```

// 创建组件,并设置大小 build() { Row() { Column() { AVCastPicker() .size({ height:45, width:45 }) } } } 

##### **自定义样式实现** 

自定义样式通过设置 CustomBuilder 类型的参数 customPicker 实现。 

实现自定义样式的步骤与实现默认样式基本相同,开发者可参考默认样式实现,完成创建 AVSession 、实现音频播放等步 骤。 

###### **TypeScript** 

- 36 - 

```arkts
import { AVCastPicker } from '@kit.AVSessionKit'; 
```

@State pickerImage:ResourceStr = $r('app.media.earpiece'); // 自定义资源 

```arkts
build() { Row() { Column() { AVCastPicker( { customPicker: (): void => this.ImageBuilder() // 新增自定义参数 } ).size({ height: 45, width:45 }) } } } // 自定义内容 @Builder ImageBuilder(): void { Image(this.pickerImage) .size({ width: '100%', height: '100%' }) .backgroundColor('#00000000') .fillColor(Color.Black) } 
```

#### **版本说明** 

版本说明按时间顺序列出了 CallLib 的所有新功能、变更、和已修复的问题。格式基于 Keep a Changelog。 变动类型: 

- **新增** ( Added ):新添加的功能。 

- **变更** ( Changed ):对现有功能的变更。 

- **废弃** ( Deprecated ):已经不建议使用,即将移除的功能。 

- **移除** ( Removed ):已经移除的功能。 

- **修复** ( Fixed ):对 bug 的修复。 

- **安全改进** ( Security ):对安全性的改进。 

###### **26.1.0 - 2026-2-3** 

- 37 - 

##### **新增** 

新增了 AI 智能总结功能。 

###### **25.12.0 - 2025-12-31** 

##### **新增** 

- RCCallClient 中新增 setCameraStatusCallback 方法,用于监听 PC 上外接摄像头的插拔等状态。 

- RCCallClient 中新增 getCameraList 方法,用于获取支持的摄像头列表。 

- RCCallClient 中新增 muteAllRemoteAudio 方法,用于静音远端所有音频。 

###### **25.11.0 - 2025-11-28** 

重要说明 

为更好的对 HarmonyOS SDK 进行版本管理,从此版本开始原版本号的第一位 1 改为年份 25,后面二、三位版本号 规则保持不变。 

更新后版本号第一位为年份、第二位为功能迭代版本号、第三位为补丁修复 hotfix 版本号。 

##### **修复** 

优化了部分内部逻辑。 

###### **1.10.0 - 2025-10-31** 

##### **新增** 

新增语音识别、实时翻译功能。 

###### **1.9.0 - 2025-09-26** 

##### **新增** 

RCCallClient 中新增 install 方法,用于提前加载模块。 

- 38 - 

###### **1.8.0 - 2025-08-29** 

##### **修复** 

修复了若干 bug。 

###### **1.7.0 - 2025-07-24** 

##### **变更** 

接口 RCCallClientListener 中的主要方法声明为必须实现。 

###### **1.6.0 - 2025-06-27** 

##### **修复** 

修复了若干 bug。 

###### **1.5.0 - 2025-05-29** 

##### **新增** 

首次发布了 CallLib SDK,支持带呼叫能力的1v1和群组音视频通话。 

### **AI 智能流式语音识别和翻译** 

###### **AI 智能流式语音识别** 

该功能支持在音视频通话、音视频会议、语聊房以及直播等多种场景下实时转写音频内容。AI 智能流式语音识别具有高准确率 和低延迟的特点。 

目前支持超过 50 种语言的识别,包括中文、英文、日语、韩语、阿拉伯语、法语、西班牙语、泰语、印尼语等,详见语言代 码列表。 

- 39 - 

##### **前置条件** 

AI 智能流式语音识别是融云 RTC SDK 的高级功能。若要使用,请在 AI 服务的服务购买页面开通此功能。 

##### **设置源语言** 

在发起通话或接听通话前,您需要通过 RCCallClient#setSrcLanguageCode 接口设置源语言。具体支持的语言请参考语言 代码列表。 

提示 

为提高语音识别的准确度,请根据您的业务需求设置合适的源语言。默认源语言为中文。 

##### **参数说明** 

参数 类型 说明 

srcLanguageCode String 语音识别的源语言代码,请参考语言代码列表。 

##### **示例代码** 

###### **TypeScript** 

CallClientInstance.setSrcLanguageCode("zh"); 

##### **注册语音识别结果回调** 

在发起通话或接听通话前,您需要通过赋值 RCCallClient#callASRListener 设置语音识别结果回调。通过此回调,您可以接 收以下通知: 

- 语音识别服务的开启和停止 

- 语音识别结果 

- 语音识别错误 

##### **语音识别数据结构** 

RCRTCASRContent 

- 40 - 

参数 类型 说明 userId String 当前语音识别关联用户的 ID msgId String 当前语音识别的 ID,用于关联当前语音识别结果 timeUTC long 当前语音识别的时间戳(单位:秒) msg String 当前语音识别结果 isEnd boolean 当前语音识别是否结束,true 表示已结束 

##### **示例代码** 

###### **TypeScript** 

CallClientInstance.callASRListener = { 

// 语音识别服务开启通知回调 

didReceiveStartASR() { 

// 处理语音识别服务开启事件 

}, 

// 语音识别服务停止通知回调 

didReceiveStopASR() { 

// 处理语音识别服务停止事件 

}, 

// 语音识别内容回调 

didReceiveASRContent(asrContent: RCRTCASRContent) { 

// 处理语音识别结果 

} } 

##### **开启语音识别服务** 

通话接通后,您需要调用 RCCallClient#startASR 方法开启语音识别服务。开启成功后,其他客户端会通过 IRCCallASRListener#didReceiveStartASR 方法收到通知。 

###### 注意 

任何加入通话的客户端都可以调用此接口开启语音识别服务。SDK 不限制调用权限,请根据您的业务需求进行权限控制。 

##### **接口定义** 

###### **TypeScript** 

- 41 - 

/** 

* 开启语音识别服务 

* 

- @returns 返回值为 RCCallErrorCode.SUCCESS 时,代表成功 

* 

###### * @description 

- 开启语音识别服务。如果房间内没有人发布流,则无法开启语音识别服务, 

- SDK 会在有人发布流后自动开启语音识别服务。 

*/ startASR(): Promise<RCCallErrorCode> 

##### **示例代码** 

###### **TypeScript** 

CallClientInstance.startASR(); 

##### **设置是否接收语音识别** 

通话建立连接成功后,您可以调用 RCCallClient#setEnableASR 方法来设置是否接收语音识别。 

提示 

开启语音识别服务后,您可以根据业务需求选择是否接收语音识别结果。如果选择接收,SDK 会通过 IRCCallASRListener#didReceiveASRContent 回调方法通知识别结果。 

##### **接口定义** 

###### **TypeScript** 

/** 

* 设置是否接收语音识别 

* 

- @param enable true 打开,false 关闭 

- @returns 返回值为 RCCallErrorCode.SUCCESS 时,代表成功 

* 

###### * @description 

- 默认关闭语音识别功能,开启后会在通话过程中自动识别用户语音并转换为文字。 */ 

setEnableASR(enable: boolean): Promise<RCCallErrorCode> 

##### **参数说明** 

- 42 - 

参数 

类型 

说明 

enable boolean true:接收语音识别 

false:停止接收语音识别 

##### **示例代码** 

###### **TypeScript** 

CallClientInstance.setEnableASR(true); 

##### **停止语音识别服务** 

您可以调用 RCCallClient#stopASR 方法停止语音识别服务。 

###### 注意 

- 停止语音识别服务生效后,所有房间内的所有语音流撰写任务都将停止,请谨慎使用。 

- 任何加入通话的客户端都可以调用此接口停止语音识别服务。SDK 不限制调用权限,请根据您的业务需求进行权限控 制。停止成功后,SDK 会通过 IRCCallASRListener#didReceiveStopASR 回调方法通知其他客户端。 

##### **接口定义** 

###### **TypeScript** 

/** * 停止语音识别服务 * * @returns 返回值为 RCCallErrorCode.SUCCESS 时,代表成功 * * @description * 停止语音识别服务。 */ stopASR(): Promise<RCCallErrorCode> 

##### **示例代码** 

###### **TypeScript** 

CallClientInstance.stopASR(); 

###### **语音识别语言代码列表** 

- 43 - 

|序号|语种中文首字母|语种中文名称|语种英文名称|语言代码|
|---|---|---|---|---|
|1|H|汉语|Chinese|zh|
|2|Y|英语|English|en|
|3|R|日语|Japanese|ja|
|4|X|西班牙语|Spanish|es|
|5|A|阿拉伯语|Arabic|ar|
|6|H|哈萨克语|Kazakh|kk|
|7|H|韩语|Korean|ko|
|8|T|泰语|Thai|th|
|9|Y|印尼语|Indonesia|id|
|10|E|俄语|Russian|ru|
|11|Y|越南语|Vietnamese|vi|
|12|F|法语|French|fr|
|13|D|德语|German|de|
|14|Y|意大利语|Italian|it|
|15|Y|印地语|Hindi|hi|
|16|M|马来语|Malay|ms|
|17|F|菲律宾语|Filipino|fl|
|18|T|泰米尔语|Tamil|ta|
|19|P|葡萄牙语|Portuguese|pt|
|20|T|土耳其语|Turkish|tr|
|21|B|波兰语|Polish|pl|
|22|L|罗马尼亚语|Romanian|ro|
|23|H|荷兰语|Dutch|nl|
|24|X|希腊语|Modern Greek|el|
|25|X|匈牙利语|Hungarian|hu|
|26|Z|爪哇语|Javanese|jv|
|27|M|孟加拉语|Bengali|bn|

- 44 - 

|28|M|缅甸语|Burmese|my|
|---|---|---|---|---|
|29|L|老挝语|Lao|lo|
|30|S|斯瓦希里语|Swahili|sw|
|31|A|阿塞拜疆语|Azerbaijani|az|
|32|B|波斯语|Persian|fa|
|33|S|僧伽罗语|Sinhala|si|
|34|J|加泰罗尼亚语|Catalan|ca|
|35|G|高棉语|Khmer|km|
|36|X|希伯来语|Hebrew|he|
|37|K|克罗地亚语|Serbo-Croatian|hbs|
|38|H|豪萨语|Hausa|ha|
|39|M|马拉地语|Marathi|mr|
|40|T|泰卢固语|Telugu|te|
|41|P|旁遮普语|Panjabi|pa|
|42|R|瑞典语|Swedish|sv|
|43|B|保加利亚语|Bulgarian|bg|
|44|D|丹麦语|Danish|da|
|45|N|挪威语|Norwegian|no|
|46|K|坎纳达语|Kannada|kn|
|47|M|马拉雅拉姆语|Malayalam|ml|
|48|J|捷克语|Czech|cs|
|49|W|乌尔都语|Urdu|ur|
|50|N|尼泊尔语|Nepali|ne|
|51|M|蒙古语(外蒙)|Mongolian|mn|
|52|W|乌兹别克语|Uzbek|uz|

###### **AI 智能流式语音翻译** 

- 45 - 

AI 智能流式语音翻译是在 AI 智能流式语音识别功能基础上增加的文本翻译功能。具备翻译延迟低、准确度高等特点,支持 200+ 语种的翻译,支持的语种详见语音翻译语言代码。 

##### **全场景适用** 

- **音视频通话** :跨国亲友聊天、海外客户对接,实时翻译让对话像母语交流般自然。 

- **多语言会议** :全球团队协作、国际研讨会,主讲内容同步译成多语言,参会者各取所需,决策效率翻倍。 

- **跨境直播** :电商出海直播、文化内容输出,实时翻译帮助主播触达全球观众,打破地域与语言的流量边界。 

##### **前置条件** 

AI 智能流式语音翻译是融云 RTC SDK 的高级功能。若要使用,请在 AI 服务的服务购买页面开通此功能。 

###### 注意 

AI 智能流式语音翻译是基于 AI 智能流式语音识别开发的功能,客户端使用该功能需要先集成AI 智能流式语音识别并打开语音 识别。 

##### **注册语音翻译结果回调** 

在发起通话或接听通话前,您需要给 RCCallClient#callASRListener 中添加语音翻译结果回调。通过 IRCCallASRListener#didReceiveRealtimeTranslationContent 回调方法可以接收语音翻译结果。 

##### **语音翻译数据结构** 

RCRTCRealtimeTranslationContent 

|参数|类型|说明|
|---|---|---|
|userId|String|当前语音翻译关联用户的ID|
|msgId|String|当前语音翻译的ID,用于关联当前语音翻译结果|
|timeUTC|long|当前语音翻译的时间戳(单位:秒)|
|msg|String|当前语音翻译结果|
|isEnd|boolean|当前语音翻译是否结束,true表示已结束|
|destLangCode|String|当前语音翻译的语言代码|

##### **示例代码** 

给 callASRListener 中增加如下监听: 

###### **TypeScript** 

- 46 - 

/*! 语音翻译内容回调 

@param content 语音翻译内容 

*/ 

didReceiveRealtimeTranslationContent(content: RCRTCRealtimeTranslationContent) { // 处理语音翻译结果 } 

##### **开启语音翻译** 

通话接通后,您需要调用 RCCallClient#startRealtimeTranslation 方法开启语音翻译。 

###### 注意 

语音翻译功能依赖语音识别服务,在开启语音翻译功能前必须先 开启语音识别服务 或在收到 IRCCallASRListener#didReceiveStartASR 回调通知后再开启语音翻译功能。 

##### **接口定义** 

###### **TypeScript** 

/** * 开启语音翻译 * 

* @param destLangCode 翻译目标语言代码 

* @returns 返回值为 RCCallErrorCode.SUCCESS 时,代表成功 

* 

* @description 

- 1. 语音翻译依赖语音识别服务,需要在收到 IRCCallASRListener 的 didReceiveStartASR 回调后,调用开启语音翻 译。 

* 2. 开启语音翻译后,会通过 IRCCallASRListener 的 didReceiveRealtimeTranslationContent 回调返回语音翻译结 果。 */ startRealtimeTranslation(destLangCode: string): Promise<RCCallErrorCode> 

##### **参数说明** 

参数 类型 说明 

destLangCode String 语音翻译语言代码 

##### **示例代码** 

- 47 - 

**TypeScript** 

CallClientInstance.startRealtimeTranslation("en"); 

##### **关闭语音翻译** 

通话接通后,您可以调用 RCCallClient#stopRealtimeTranslation 方法停止语音翻译。 

提示 

语音翻译依赖语音识别服务,如果关闭语音识别服务,语音翻译功能也会被同时关闭。 

##### **接口定义** 

###### **TypeScript** 

/** 

- 关闭语音翻译 

- 

- @returns 返回值为 RCCallErrorCode.SUCCESS 时,代表成功 

* 

- @description 

- 关闭语音翻译。 

- */ 

stopRealtimeTranslation(): Promise<RCCallErrorCode> 

##### **示例代码** 

###### **TypeScript** 

CallClientInstance.stopRealtimeTranslation(); 

###### **语音翻译语言代码列表** 

|序号|语种中文首字母|语种中文名称|语种英文名称|语言代码|
|---|---|---|---|---|
|1|A|阿布哈兹语|Abkhazian|ab|
|2||阿尔巴尼亚语|Albanian|sq|
|3||阿肯语|Akan|ak|
|4||阿拉伯语|Arabic|ar|
|5||阿拉贡语|A||

- 48 - 

|5|阿拉贡语|Aragonese|an|
|---|---|---|---|
|6|阿姆哈拉语|Amharic|am|
|7|阿萨姆语|Assamese|as|
|8|阿塞拜疆语|Azerbaijani|az|
|9|阿斯图里亚斯语|Asturian|ast|
|10|阿兹特克语|Central Huasteca Nahuatl|nch|
|11|埃维语|Ewe|ee|
|12|艾马拉语|Aymara|ay|
|13|爱尔兰语|Irish|ga|
|14|爱沙尼亚语|Estonian|et|
|15|奥杰布瓦语|Ojibwa|oj|
|16|奥克语|Occitan|oc|
|17|奥里亚语|Oriya|or|
|18|奥罗莫语|Oromo|om|
|19|奥塞梯语|Ossetian|os|
|20 B|巴布亚皮钦语|Tok Pisin|tpi|
|21|巴什基尔语|Bashkir|ba|
|22|巴斯克语|Basque|eu|
|23|白俄罗斯语|Belarusian|be|
|24|柏柏尔语|Berber languages|ber|
|25|班巴拉语|Bambara|bm|
|26|邦阿西楠语|Pangasinan|pag|
|27|保加利亚语|Bulgarian|bg|
|28|北萨米语|Northern Sami|se|
|29|本巴语|Bemba (Zambia)|bem|
|30|比林语|Blin|byn|
|31|比斯拉马语|Bislama|bi|
|32|俾路支语|Baluchi|bal|
|33|冰岛语|I l di|i|

- 49 - 

|33|冰岛语|Icelandic|is|
|---|---|---|---|
|34|波兰语|Polish|pl|
|35|波斯尼亚语|Bosnian|bs|
|36|波斯语|Persian|fa|
|37|博杰普尔语|Bhojpuri|bho|
|38|布列塔尼语|Breton|br|
|39 C|查莫罗语|Chamorro|ch|
|40|查瓦卡诺语|Chavacano|cbk|
|41|楚瓦什语|Chuvash|cv|
|42|聪加语|Tsonga|ts|
|43 D|鞑靼语|Tatar|tt|
|44|丹麦语|Danish|da|
|45|掸语|Shan|shn|
|46|德顿语|Tetum|tet|
|47|德语|German|de|
|48|低地德语|Low German|nds|
|49|低地苏格兰语|Scots|sco|
|50|迪维西语|Dhivehi|dv|
|51|侗语|Kam|kdx|
|52|杜順語|Kadazan Dusun|dtp|
|53 E|俄语|Russian|ru|
|54 F|法罗语|Faroese|fo|
|55|法语|French|fr|
|56|梵语|Sanskrit|sa|
|57|菲律宾语|Filipino|fl|
|58|斐济语|Fijian|fj|
|59|芬兰语|Finnish|f|
|60|弗留利语|Friulian|fur|
|61|富尔语|Fur|fvr|

- 50 - 

|61|富尔语|Fur|fvr|
|---|---|---|---|
|62 G|刚果语|Kongo|kg|
|63|高棉语|Khmer|km|
|64|格雷罗纳瓦特尔语|Guerrero Nahuatl|ngu|
|65|格陵兰语|Kalaallisut|kl|
|66|格鲁吉亚语|Georgian|ka|
|67|格罗宁根方言|Gronings|gos|
|68|古吉拉特语|Gujarati|gu|
|69|瓜拉尼语|Guarani|gn|
|70 H|哈萨克语|Kazakh|kk|
|71|海地克里奥尔语|Haitian|ht|
|72|韩语|Korean|ko|
|73|豪萨语|Hausa|ha|
|74|荷兰语|Dutch|nl|
|75|黑山语|Montenegrin|cnr|
|76|胡帕语|Hupa|hup|
|77 J|基里巴斯语|Gilbertese|gil|
|78|基隆迪语|Rundi|rn|
|79|基切语|K'iche'|quc|
|80|吉尔吉斯斯坦语|Kirghiz|ky|
|81|加利西亚语|Galician|gl|
|82|加泰罗尼亚语|Catalan|ca|
|83|捷克语|Czech|cs|
|84 K|卡拜尔语|Kabyle|kab|
|85|卡纳达语|Kannada|kn|
|86|卡努里语|Kanuri|kr|
|87|卡舒比语|Kashubian|csb|
|88|卡西语|Khasi|kha|
|89|康沃尔语|Cornish|kw|

- 51 - 

|89|康沃尔语|Cornish|kw|
|---|---|---|---|
|90|科萨语|Xhosa|xh|
|91|科西嘉语|Corsican|co|
|92|克里克语|Creek|mus|
|93|克里米亚鞑靼语|Crimean Tatar|crh|
|94|克林贡语|Klingon|tlh|
|95|克罗地亚语|Serbo-Croatian|hbs|
|96|克丘亚语|Quechua|qu|
|97|克什米尔语|Kashmiri|ks|
|98|库尔德语|Kurdish|ku|
|99 L|拉丁语|Latin|la|
|100|拉特加莱语|Latgalian|ltg|
|101|拉脱维亚语|Latvian|lv|
|102|老挝语|Lao|lo|
|103|立陶宛语|Lithuanian|lt|
|104|林堡语|Limburgish|li|
|105|林加拉语|Lingala|ln|
|106|卢干达语|Ganda|lg|
|107|卢森堡语|Letzeburgesch|lb|
|108|卢森尼亚语|Rusyn|rue|
|109|卢旺达语|Kinyarwanda|rw|
|110|罗马尼亚语|Romanian|ro|
|111|罗曼什语|Romansh|rm|
|112|罗姆语|Romany|rom|
|113|逻辑语|Lojban|jbo|
|114 M|马达加斯加语|Malagasy|mg|
|115|马恩语|Manx|gv|
|116|马耳他语|Maltese|mt|
|117|马拉地语|Marathi|mr|

- 52 - 

|117|马拉地语|Marathi|mr|
|---|---|---|---|
|118|马拉雅拉姆语|Malayalam|ml|
|119|马来语|Malay|ms|
|120|马里语(俄罗斯)|Mari (Russia)|chm|
|121|马其顿语|Macedonian|mk|
|122|马绍尔语|Marshallese|mh|
|123|玛雅语|Kekchí|kek|
|124|迈蒂利语|Maithili|mai|
|125|毛里求斯克里奥尔语|Morisyen|mfe|
|126|毛利语|Maori|mi|
|127|蒙古语|Mongolian|mn|
|128|孟加拉语|Bengali|bn|
|129|缅甸语|Burmese|my|
|130|苗语|Hmong|hmn|
|131|姆班杜语|Umbundu|umb|
|132 N|纳瓦霍语|Navajo|nv|
|133|南非语|Afrikaans|af|
|134|尼泊尔语|Nepali|ne|
|135|纽埃语|Niuean|niu|
|136|挪威语|Norwegian|no|
|137 P|帕姆语|Pam|pmn|
|138|帕皮阿门托语|Papiamento|pap|
|139|旁遮普语|Panjabi|pa|
|140|葡萄牙语|Portuguese|pt|
|141|普什图语|Pushto|ps|
|142 Q|齐切瓦语|Nyanja|ny|
|143|契维语|Twi|tw|
|144|切罗基语|Cherokee|chr|
|145 R|日语|Japanese|ja|

- 53 - 

|145 R|日语|Japanese|ja|
|---|---|---|---|
|146|瑞典语|Swedish|sv|
|147 S|萨摩亚语|Samoan|sm|
|148|桑戈语|Sango|sg|
|149|僧伽罗语|Sinhala|si|
|150|上索布语|Upper Sorbian|hsb|
|151|世界语|Esperanto|eo|
|152|斯洛文尼亚语|Slovenian|sl|
|153|斯瓦希里语|Swahili|sw|
|154|索马里语|Somali|so|
|155|斯洛伐克语|Slovak|sk|
|156 T|他加禄语|Tagalog|tl|
|157|塔吉克语|Tajik|tg|
|158|塔希提语|Tahitian|ty|
|159|泰卢固语|Telugu|te|
|160|泰米尔语|Tamil|ta|
|161|泰语|Thai|th|
|162|汤加语(汤加群岛)|Tonga (Tonga Islands)|to|
|163|汤加语(赞比亚)|Tonga (Zambia)|toi|
|164|提格雷尼亚语|Tigrinya|ti|
|165|图瓦卢语|Tuvalu|tvl|
|166|图瓦语|Tuvinian|tyv|
|167|土耳其语|Turkish|tr|
|168|土库曼语|Turkmen|tk|
|169 W|瓦隆语|Walloon|wa|
|170|瓦瑞语(菲律宾)|Waray (Philippines)|war|
|171|威尔士语|Welsh|cy|
|172|文达语|Venda|ve|
|173|沃拉普克语|Volapük|vo|

- 54 - 

|174|沃拉普克语 沃洛夫语|p Wolof|wo|
|---|---|---|---|
|175|乌德穆尔特语|Udmurt|udm|
|176|乌尔都语|Urdu|ur|
|177|乌孜别克语|Uzbek|uz|
|178 X|西班牙语|Spanish|es|
|179|西方国际语|Interlingue|ie|
|180|西弗里斯兰语|Western Frisian|fy|
|181|西里西亚语|Silesian|szl|
|182|希伯来语|Hebrew|he|
|183|希利盖农语|Hiligaynon|hil|
|184|夏威夷语|Hawaiian|haw|
|185|现代希腊语|Modern Greek|el|
|186|新共同语言|Lingua Franca Nova|lfn|
|187|信德语|Sindhi|sd|
|188|匈牙利语|Hungarian|hu|
|189|修纳语|Shona|sn|
|190|宿务语|Cebuano|ceb|
|191|叙利亚语|Syriac|syr|
|192|巽他语|Sundanese|su|
|193 Y|亚美尼亚语|Armenian|hy|
|194|亚齐语|Achinese|ace|
|195|伊班语|Iban|iba|
|196|伊博语|Igbo|ig|
|197|伊多语|Ido|io|
|198|伊洛卡诺语|Iloko|ilo|
|199|伊努克提图特语|Inuktitut|iu|
|200|意大利语|Italian|it|
|201|意第绪语|Yiddish|yi|

- 55 - 

y 

|202|因特语|Interlingua|ia|
|---|---|---|---|
|203|印地语|Hindi|hi|
|204|印度尼西亚语|Indonesia|id|
|205|印古什语|Ingush|inh|
|206|英语|English|en|
|207|约鲁巴语|Yoruba|yo|
|208|越南语|Vietnamese|vi|
|209 Z|扎扎其语|Zaza|zza|
|210|爪哇语|Javanese|jv|
|211|中文|Chinese|zh|
|212|中文繁体|Traditional Chinese|zh-tw|
|213|中文粤语|Cantonese|yue|
|214|祖鲁语|Zulu|zu|

###### **AI 智能总结** 

AI 智能总结是在 AI 智能流式语音识别功能基础上增加的智能总结功能。该功能能够自动分析通话内容,生成通话摘要、章节 摘要、待办事项、话题提取等多种形式的总结内容,帮助用户快速回顾通话要点。 

##### **全场景适用** 

- **音视频通话** :自动生成通话纪要,记录通话要点、决策事项和待办任务,提升通话效率。 

- **在线培训** :生成培训内容摘要和知识点总结,帮助学员快速回顾重点内容。 

- **客户沟通** :记录客户需求、沟通要点和后续跟进事项,确保信息不遗漏。 

##### **前置条件** 

AI 智能总结是融云 RTC SDK 的高级功能。使用前需要满足以下条件: 

##### **服务开通** 

请提交工单开通。 

##### **功能依赖** 

- 56 - 

注意 

AI 智能总结是基于 AI 智能流式语音识别开发的功能。使用该功能需要: 

1. 先集成 AI 智能流式语音识别 功能 

2. 在初始化 CallLib 时开启语音识别功能(具体配置方法请参考 AI 智能流式语音识别 文档) 

##### **注册智能总结回调** 

为了接收智能总结相关通知,您需要实现并注册相应的回调。通过回调,您可以接收智能总结任务的状态通知。 

在发起通话或接听通话前,您需要通过 RCCallClient 的 callASRListener 属性设置智能总结回调。设置后,您将通过 RCCallASRListener 的 didReceiveStartSummarization 和 didReceiveStopSummarization 方法获得智能总结任务状 态通知。 

##### **回调方法说明** 

方法 说明 didReceiveStartSummarization 智能总结任务开始回调 didReceiveStopSummarization 智能总结任务停止回调 

###### didReceiveStartSummarization **参数说明** 

参数 类型 说明 taskId string 智能总结任务 ID,用于后续生成智能总结 

didReceiveStopSummarization **参数说明** 

参数 类型 说明 taskId string 智能总结任务 ID 

##### **示例代码** 

实现 RCCallASRListener 中智能总结相关回调: 

###### **TypeScript** 

- 57 - 

CallClientInstance.callASRListener = { didReceiveStartASR() { // 处理语音识别服务开启事件 }, didReceiveStopASR() { // 处理语音识别服务停止事件 }, didReceiveStartSummarization(taskId:string) { // 处理 AI 智能总结开启事件 }, didReceiveStopSummarization(taskId:string) { // 处理 AI 智能总结停止事件 } } 

##### **开启智能总结** 

在开启语音识别成功后,您需要调用 RCCallClient 的 startSummarization 方法开启智能总结服务。 

开启成功后,其他客户端会通过 RCCallASRListener 的 didReceiveStartSummarization 方法收到通知。 

###### 注意 

智能总结依赖语音识别服务,需要在收到 RCCallASRListener 的 didReceiveStartASR 回调后,调用开启智能总结;智能 总结为通话级别功能,通话内任意用户开启后,所有用户都会收到开始通知。 

##### **接口原型** 

###### **TypeScript** 

startSummarization(): Promise<IRCCallProcessResult<string>> 

##### **示例代码** 

###### **TypeScript** 

- 58 - 

CallClientInstance.startSummarization() .then((result:IRCCallProcessResult<string>) => { if(result.code === RCCallErrorCode.SUCCESS) { // 开启成功,通过 result.data 获取任务 ID } else { // 开启失败 } }) .catch(() => { // 处理异常情况 }) 

##### **关闭智能总结** 

您可以通过 RCCallClient 的 stopSummarization 方法关闭智能总结。 

提示 

智能总结依赖语音识别服务,如果关闭语音识别,智能总结也会同时关闭。 

##### **接口原型** 

###### **TypeScript** 

stopSummarization(): Promise<IRCCallProcessResult<void>> 

##### **示例代码** 

###### **TypeScript** 

CallClientInstance.stopSummarization() .then((result:IRCCallProcessResult<void>) => { if(result.code === RCCallErrorCode.SUCCESS) { // 停止成功 } else { // 停止失败 } }) .catch(() => { // 处理异常情况 }) 

##### **生成智能总结** 

- 59 - 

在智能总结任务开启后,您可以通过 RCCallClient 的 generateSummarization 方法生成智能总结。该方法支持生成通话 摘要、章节摘要、待办事项、话题提取等多种形式的总结内容。 

##### **接口原型** 

###### **TypeScript** 

|generateSummarization( callId:string,|
|---|
|taskId:string,|
|startTime:number,|
|endTime:number,|
|confg: RCRTCGenerateSummarizationConfg,|
|callback: IRCCallStreamDataCallback<string> ):void|

##### **参数说明** 

|参数|类型|说明|
|---|---|---|
|callId|string|生成智能总结的通话ID|
|taskId|string|智能总结任务ID,通过didReceiveStartSummarization回调获 取到|
|startTime|number|本次需要总结的开始时间,UTC时间戳,单位秒,传入0,表示总 结开始的时间|
|endTime|number|本次需要总结的结束时间,UTC时间戳,单位秒,传入0,表示当 前时间,如果总结已经停止,则表示总结结束的时间|
|confg|RCRTCGenerateSummarizationConfg|生成智能总结配置,详见下方 **配置说明**|
|callback|IRCCallStreamDataCallback|内容结果回调,如果内容比较多,onDataReceived会回调多次|

###### **配置说明** 

RCRTCGenerateSummarizationConfig 配置类包含以下属性: 

- 60 - 

|属性|类型|说明|
|---|---|---|
|customPrompt|string|自定义提示词,最大长度100|
|destLang|string|输出智能总结的目标语言代码|
|enableSummarization|boolean|是否输出总结摘要,即对整个通话的高度概括|
|enableSummarizationDetails|boolean|是否输出总结详情,默认false|
|enableChapterSummary|boolean|是否输出章节摘要,即按时间线或话题划分的通 结,默认false|
|enableTodoList|boolean|是否输出待办事项提取,自动识别通话中达成的 配的任务,默认false|
|enableHashtag|boolean|是否输出话题提取,默认false|
|format|RCRTCGenerateSummarizationFormat|输出格式,默认 RCRTCGenerateSummarizationFormat.MA|

##### **示例代码** 

###### **TypeScript** 

- 61 - 

###### // 创建智能总结配置 

```arkts
const config = new RCRTCGenerateSummarizationConfig() config.destLang = "zh"; // 设置输出语言为中文 config.enableSummarization = true; // 启用总结摘要 config.enableSummarizationDetails = true; // 启用总结详情 config.enableChapterSummary = true; // 启用章节摘要 config.enableTodoList = true; // 启用待办事项提取 config.enableHashtag = true; // 启用话题提取 config.format = RCRTCGenerateSummarizationFormat.MARK_DOWN; // 设置输出格式为 MarkDown 
```

###### // 生成智能总结 

CallClientInstance.generateSummarization(callId, taskId, 0, 0, config, { onFailed(errorCode:RCCallErrorCode) { // 处理失败 }, onComplete() { // 处理完成 }, onDataReceived(data:string) { // 处理数据 } }) 

##### **获取语音转文字** 

在智能总结任务开启后,您可以通过 RCCallClient 的 getASRContent 方法获取指定时间段的语音转文字内容。该方法可以 获取通话期间的完整语音识别文本。 

##### **接口原型** 

###### **TypeScript** 

getASRContent( callId: string, taskId: string, startTime: number, endTime: number, destLang: string, callback: IRCCallStreamDataCallback<string> ): void 

##### **参数说明** 

- 62 - 

|参数|类型|说明|
|---|---|---|
|callId|string|获取语音转文字的通话ID|
|taskId|string|智能总结任务ID,通过didReceiveStartSummarization回调获取到|
|startTime|number|本次需要获取语音转文字的开始时间,UTC时间戳,单位秒,传入0,表示总 结开始的时间|
|endTime|number|本次需要获取语音转文字的结束时间,UTC时间戳,单位秒,传入0,表示当 前时间,如果总结已经停止,则表示总结结束的时间|
|destLang|string|目标语言代码,如果传入null或空字符串,则使用默认语言|
|callback|IRCCallStreamDataCallback|内容结果回调,如果内容比较多,onDataReceived会回调多次|

##### **示例代码** 

###### **TypeScript** 

// 获取语音转文字内容 

CallClientInstance.getASRContent(callId, taskId, 0, 0, "zh", { onFailed(errorCode:RCCallErrorCode) { // 处理失败 }, onComplete() { // 处理完成 }, onDataReceived(data:string) { // 处理数据 } }) 

#### **客户端 API** 

以下是鸿蒙版 CallLib 的 API 参考文档: 

CallLib 音视频通话(不含 UI) 

#### **状态码** 

- 63 - 

0 SUCCESS 

成功。 

1 FAILED 失败 **排查建议** :接口调用失败。 2 ONE_CALL_EXISTED 已经处于通话中了 

**排查建议** :当前正在通话中,例如重复发起通话时会出现此错误码。 

3 NOT_IN_CALL 不在通话中 

**排查建议** :有些接口调用限制在通话中状态,例如非通话状态切换媒体类型。 

4 OPERATION_UNAVAILABL E 无效操作 

**排查建议** :该返回表示非法调用,或者是多余调用。 

- 5 

INVALID_PARAM 

参数错误 

**排查建议** :请检查当前接口的入参是否符合该接口要求 

#### **合规指南** 

#### **实时音视频** CallLib SDK **合规使用说明** 

根据中国法律法规和监管部门规章要求,App 开发运营者(以下简称"开发者"或"您")在提供网络产品服务时应尊重和保护最 终用户个人信息,不得违法违规收集使用个人信息,保证和承诺个人信息处理行为获得最终用户的授权同意,遵循最小必要原 则,并且应当采取有效的技术措施和组织措施,确保个人信息安全。 

- 64 - 

为帮助开发者在使用 SDK 的过程中更好地落实用户个人信息保护相关要求,避免出现侵害用户个人信息权益情形,北京云中 融信网络科技股份有限公司(以下简称"我们")特制定本 SDK 合规使用说明文档(以下简称"文档")。 

###### **一、 App 个人信息保护的合规要求** 

为保护 App 最终用户的个人信息,App 及 App 的开发者需要满足如下合规要求: 

- App 开发者应该制定隐私政策,并在 App 界面中显著展示。 

- App 隐私政策应该单独成文,而不是作为用户协议等文件中的一部分进行展示。 

- App 隐私政策应该明示收集和使用个人信息的目的、方式和范围,并且确保隐私政策链接正常有效,易于访问和阅读。 

- App 隐私政策应逐项说明 App 各项业务功能以及对应收集的个人信息类型,不应使用"等、例如"等方式概括说明。 

- App 隐私政策应显著标识个人敏感信息类型(如:字体加粗等)。 

- App 隐私政策应逐项说明调用的第三方 SDK,包括明示 SDK 名称、SDK 开发者名称;SDK 收集和处理的个人信息类 型、目的、方式、范围;SDK 隐私政策链接。 

###### **二、 App 使用** CallLib SDK **时的合规指引** 

##### **1. SDK 所需的系统权限的说明** 

CallLib SDK 功能所需的权限,您可以参考如下表格,了解相关权限功能和时机。SDK 只会检查 App 是否获得相应授权,不 会主动向最终用户申请权限。 

权限配置,请查阅 实现音视频通话 。 

##### **HarmonyOS 操作系统 SDK 功能、接口配置方式及示例说明:** 

- 65 - 

|系统|业 务 功 能|相关个人信息|功能|
|---|---|---|---|
|HarmonyOS|登 录|IP地址、网络接入方式和类型、App Key下的用户ID、用户Token|用户登 录连接|
||连||时|
||接|||
|HarmonyOS|推|应用包名|使用推|
||送||送功能|
||功||时|
||能|||
|HarmonyOS|故 障 排|设备品牌、设备型号、操作系统版本、内存使用情况、App的AppKey、融云SDK版本号、 接口调用的错误码、链接失败的错误码、App版本号、时区、语言、运营商代码MNO(可 选)|故障排 查时|
||查|||

配置方式及示例: 

###### **TypeScript** 

// 连接 IM 

IMEngine.getInstance().connect(token, 20).then(result => { if (EngineError.Success === result.code) { 

// 连接成功 let userId = result.userId; return } if (EngineError.ConnectTokenExpired === result.code) { 

- // Token 过期,从 APP 服务请求新 token,获取到新 token 后重新 connect() 

} else if (EngineError.ConnectionTimeout === result.code) { 

- // 连接超时,弹出提示,可以引导用户等待网络正常的时候再次点击进行连接 

} else { 

- //其它业务错误码,请根据相应的错误码作出对应处理。 

} }); 

##### **2. SDK 初始化及业务功能调用时机说明** 

您应确保在登录注册页面及 App 首次运行时,通过简洁、明显且易于访问方式向最终用户告知涵盖个人信息处理主体、处理 目的、处理方式、处理类型、保存期限等内容的 App 个人信息处理规则(App 隐私政策)。 

您应确保在最终用户同意 App 隐私政策后,再进行 SDK 的初始化。并且,在用户同意隐私政策前,您应避免动态申请涉及用 户个人信息的敏感设备权限;也应避免私自采集和上报个人信息。如果最终用户不同意 App 隐私政策,则不能初始化 SDK, 

- 66 - 

无法使用 SDK 功能。 

SDK 初始化和相关功能配置,请查阅 HarmonyOS CallLib SDK 实现音视频通话 。 

##### **3. SDK 隐私政策披露要求与示例说明** 

请您根据集成 CallLib SDK 的实际情况,在您的 App 隐私政策中披露:第三方 SDK 名称、SDK 公司名称、SDK 使用目的和 功能场景、SDK 涉及个人信息类型、实现 SDK 功能所需的权限、SDK 隐私政策链接。 

请在您的 App 隐私政策中,以文字或列表的方式向公众披露第三方SDK的相关信息。 

第三方 SDK 披露示例(仅供参考): 

###### **HarmonyOS 示例** 

- SDK 名称:HarmonyOS CallLib SDK 

- SDK 公司名称:北京云中融信网络科技股份有限公司 

- SDK 使用目的和功能场景:提供音视频服务功能和服务 

- SDK 涉及的个人信息类型:设备品牌、设备型号、操作系统版本、内存使用情况、IP地址、网络接入方式和类型、App Key 下的用户 ID、应用包名、时区、语言、App 版本号、App 的 AppKey、用户 Token、融云 SDK 版本号、运营商代 码 MNO(可选)、接口调用的错误码、链接失败的错误码 

- 实现 SDK 功能所需权限:麦克风权限(ohos.permission.MICROPHONE,必要)、相机权限 

- (ohos.permission.CAMERA,必要)、网络相关权限(ohos.permission.GET_NETWORK_INFO、 

- ohos.permission.INTERNET,必要) 

- SDK 隐私政策链接:https://docs.rongcloud.cn/guides/privacy 

##### **4. 最终用户同意方式的建议方式说明及示例** 

App 首次运行时应当有隐私弹窗,隐私弹窗中应公示隐私政策内容并附完整隐私政策链接,并明确提示最终用户阅读并选择是 否同意隐私政策; 隐私弹窗应提供同意按钮和拒绝同意的按钮,并由最终用户主动选择。 App 取得敏感权限前,应通过隐私 弹窗获得用户单独授权同意。 

隐私政策授权和敏感个人信息授权弹窗示例: 

- 67 - 

- 68 - 

图 1:敏感个人信息授权弹窗示例 

- 69 - 

图 2:隐私政策授权弹窗示例 

##### **5. 最终用户行使权利的配置说明** 

开发者在其 App 中集成 SDK 后,SDK 的正常运行会收集和处理必要的最终用户的个人信息用于提供音视频服务。 

- 70 - 

SDK 提供以下接口配置,以便您帮助最终用户实现其个人信息权利的请求。在最终用户撤销同意处理其个人信息的授权时, 您可以通过调用接口,停止和关闭 SDK 功能,并停止收集相应的用户数据。 

App 开发者应根据相关法律法规为最终用户提供行使个人信息主体权利的路径功能,需要 SDK 配合的,请与 SDK 及时进行 联系。 

###### **三、合规文件指引** 

1. 《个人信息保护法》 

2. 《工业和信息化部关于开展信息通信服务感知提升行动的通知》 

3. 《工业和信息化部关于开展纵深推进 App 侵害用户权益专项整治行动的通知》 

4. 《工业和信息化部关于开展 App 侵害用户权益专项整治工作的通知》 

5. 《App 违法违规收集使用个人信息行为认定方法》 

6. 《App 违法违规收集使用个人信息自评估指南》 

7. 《常见类型移动互联网应用程序必要个人信息范围规定》 

8. 《GB/T 35273-2020信息安全技术个人信息安全规范》 

9. 《网络安全标准实践指南—移动互联网应用程序(App)使用软件开发工具包(SDK)安全指引》 

###### **四、联系方式** 

我们设立了专门的个人信息保护团队和负责人,如果您和/或最终用户对本规则或个人信息保护相关事宜有疑问或投诉、建议 时,可以通过提交工单与我们联系: 

我们将尽快审核所涉问题,并在 15 个工作日或法律法规规定的期限内予以反馈。 

- 71 -
