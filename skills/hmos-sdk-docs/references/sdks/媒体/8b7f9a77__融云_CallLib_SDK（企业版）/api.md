**RTC** 融云音视频 ( ) 客户端 **SDK** 文档 HarmonyOS CallLib 

## 目录 

|导入CallLib SDK|5|
|---|---|
|环境要求|5|
|自动导入SDK|5|
|手动导入SDK|6|
|命令行安装SDK|6|
|entry配置文件依赖SDK|7|
|同步项目|7|
|配置项目|8|
|配置useNormalizedOHMUrl|8|
|添加 SDK依赖权限|8|
|实现音视频通话|10|
|步骤 1:服务开通|10|
|步骤 2:SDK导入|10|
|3:初始化步骤|10|
|步骤 4:监听通话事件|11|
|设置监听|11|
|通话呼入|11|
|通话状态变化|12|
|漏接电话|13|
|通话计时|14|
|步骤 5:连接 IM服务|15|
|步骤 6:发起呼叫|15|
|发起单人呼叫|15|
|发起多人呼叫|16|
|步骤 7:呼叫接听|16|
|通话管理|17|
|主叫方|17|
|发起呼叫|17|

- 2 - 

|挂断通话|18|
|---|---|
|邀请通话|18|
|被叫方|19|
|接听通话|19|
|默认接听|19|
|拒绝/挂断通话|19|
|通话监听|20|
|来电监听|20|
|通话建立、结束等状态相关的回调|20|
|设备相关回调|23|
|网络质量相关回调|23|
|视频管理|25|
|分辨率/帧率/码率|25|
|设置分辨率|25|
|设置帧率|25|
|设置码率|26|
|摄像头设置|26|
|开关摄像头|26|
|获取摄像头状态|26|
|切换前后置摄像头|27|
|设置视图|27|
|设置本地视图|27|
|设置远端视图|28|
|移除渲染视图|29|
|视频转音频|30|
|监听远端媒体切换|30|
|音频管理|31|
|麦克风设置|31|
|麦克风静音|31|
|获取麦克风状态|31|
|扬声器设置|32|

- 3 - 

|听筒/扬声器切换|32|
|---|---|
|获取扬声器状态|32|
|音频路由|32|
|使用 AVCastPicker切换音频路由|32|
|自定义样式实现|33|
|客户端API|34|
|状态码|34|

- 4 - 

#### 导入 **CallLib SDK** 

融云支持使用 DevEco Studio 中自动导入和手动导入两种方式 ,将 CallLib SDK 导入到您的应用工程中。 

###### 环境要求 

- . DevEco Studio NEXT Release(5.0.3.900) 及以上。 

- .  HarmonyOS SDK API 12 及以上。 

- .  手机(真机)系统版本号 :NEXT.0.0.31 

###### 自动导入 **SDK** 

1.0.0 版本开始支持 OpenHarmony三方库中心获取 SDK 

1. 在 entry 目录中的 oh-package.json5 中添加 SDK 依赖 ,然后点击 "Sync Now"。 

###### **JSON** 

**/** entry 目录中的 oh-package.json5 

{ "name": "entry", "version": "1.0.0", "description" : "Please describe the basic information.", "main" : "", "author": "", "license" : "", "dependencies": { "@rongcloudenterprise/calllib" : "x.y.z", "@rongcloudenterprise/imlib" : "x.y.z", "@rongcloud-enterprise/rtclib" : "x.y.z" } } 

###### 注意 

.  各个 SDK 的最新版本号可能不相同 ,具体 x.y.z 值可前往融云官网 SDK 下载页面 或 OpenHarmony三方库中心 查询。 

1.    安装 SDK 成功后 ,您可以在项目根目录的 **oh_modules/.ohpm/** 中找到融云 callLib SDK。 

2.    查看更多其他融云 SDK。 打开OpenHarmony三方库中心 ,搜索关键字 **rongcloud** 

- 5 - 

###### 手动导入 **SDK** 

1. 在导入 SDK 前 ,您需要前往融云官网 SDK 下载页面 ,将音视频通话(无 UI)SDK 下载到本地。 

2. 创建 **./libs** 文件夹 ,将 SDK **har** 包 放入其中。 

###### 命令行安装 **SDK** 

1. 在工程根路径下执行以下命令行 : 

###### **shell** 

ohpm i @rongcloud-enterprise/calllib 

2. 执行完后 ,工程根路径的 oh-package.json5 就会依赖 SDK。 

###### **JSON** 

- 6 - 

- **/** 工程根路径下的 oh-package.json5 

- { 

"name": "xxx", 

"version": "1.0.0", "description" : "Please describe the basic information.", 

"main" : "", "author": "", "license" : "", "dependencies": { "@rongcloud-enterprise/calllib" : "file:libs/CallLib.har", **/** 该配置 

由命令行生成 }, 

```arkts
"devDependencies": { "@ohos/hypium": "1.0.16", "@ohos/hamock" : "1.0.0" } } 
```

###### **entry** 配置文件依赖 **SDK** 

在 **entry** 同级目录的 oh-package.json5 手动配置 SDK 依赖。 

###### **JSON** 

- **/** entry 同级目录下的 oh-package.json5 需要手动配置 

{ "name": "xxx", "version": "1.0.0", "description" : "Please describe the basic information.", "main" : "", "author": "", "license" : "", "dependencies": { "@rongcloud-enterprise/calllib" : "file:../libs/CallLib.har", **/** 该配置手动依赖 "@rongcloud-enterprise/imlib": "file:../libs/RongIMLib.har", **/** 该配置手动依赖 "@rongcloud-enterprise/rtclib": "file:../libs/RTCLib.har" **/** 该 

配置手动依赖 }, 

```arkts
"devDependencies": { "@ohos/hypium": "1.0.16", "@ohos/hamock" : "1.0.0" } } 
```

###### 同步项目 

- 7 - 

在 entry/oh-package.json5 中点击 **Sync Now** 同步工程 ,同步成功之后即可正常使用 CallLib SDK。 

##### Q 提示 

如果您同步之后依然无法导入 SDK ,这可能是 DevEco Studio 的编译缓存导致的问题。您可以尝试把 DevEco Studio 完全关闭之后重新打开 APP 工程来解决问题。 

###### 配置项目 

###### 配置 **useNormalizedOHMUrl** 

1.0.0 版本开始 SDK 支持字节码 ,为了支持字节码 ,app 需要在项目根路径配置 **useNormalizedOHMUrl** 。 

// app 根路径下的 build-profile.json5 { "app": { "products": [ { "buildOption": { "strictMode": { "useNormalizedOHMUrl": true } } } ] } } 

###### 添加 **SDK** 依赖权限 

SDK 需要权限如下 : 

- 8 - 

|权限名称|权限说明|使用目的|
|---|---|---|
|ohos.permission.GET_NETWORK_INFO|获取网络信息|网络变化之后获取网络信息 ,进行IM重连|
|ohos.permission.INTERNET|使用网络|连接IM、 收发消息需要网络连接|
|ohos.permission.MICROPHONE|麦克风权限|音频通话需要麦克风采集能力|
|ohos.permission.CAMERA|摄像头权限|视频通话需要摄像头采集能力|

1. 找到项目 entry/src/main/ 目录下的 module.json5  文件 ,添加 requestPermissions  配置 ,以配置摄像头权限为 例: 

###### **JSON** 

"requestPermissions": [ { "name": "ohos.permission.CAMERA", "reason": "$string:Camera", "usedScene": { "abilities": [ "EntryAbility", ], "when": "always" } }, ... **/** 配置其他权限 ] 

具体权限配置参数含义 ,请参考鸿蒙的应用权限管控文档。 

2. 配置权限时 ,按照规则需要考虑国际化问题 ,在项目 entry/src/main/resources/base/element 目录下找到 string.json  文件 ,对应增加配置字符变量 ,以配置摄像头字符变量为例 : 

###### **JSON** 

{ "string" : [ { "name": "Camera", "value": "Camera in RTC" }, ... **/** 定义其他 ] } 

- 9 - 

#### 实现音视频通话 

CallLib 是在 RTCLib 基础上 ,额外封装了一套音视频呼叫功能 SDK ,包含了单人、 多人音视频呼叫的各种场景和功能 ,通过 集成它 ,您可以自由的实现音视频呼叫场景的各种玩法。 

注意 

房间人数上限 

考虑移动设备的带宽(主要是在多路视频情况下) ,建议单次通话或房间内 ,视频不超过 16 人 ,纯音频不超过 32 人。超过此上限可能影响通话效果。 

###### 步骤 **1** :服务开通 

您在融云创建的应用默认不会启用音视频服务。在使用融云提供的任何音视频服务前 ,您需要前往控制台 ,为应用开通音视频 服务。 

具体步骤请参阅开通音视频服务。 

注意 服务开通、 关闭等设置完成后 15 分钟后生效。 

###### 步骤 **2** : **SDK** 导入 

您需要导入融云音视频通话能力库 CallLib ,和 RTC 业务所依赖的即时通讯能力库 IMLib。根据您的业务需求 ,可选择导入美 颜扩展库。 

具体步骤请参阅 导入 CallLib SDK。 

###### 步骤 **3** :初始化 

CallLib 是基于 IM 作为信令通道的 ,所以要先初始化 IM 。如果不换 AppKey ,在整个应用生命周期中 ,初始化一次即可。 建议调用位置放在应用启动位置处 ,或在音视频功能模块的加载位置处。 在 UIAbility 的 onCreate() 方法中 ,调用初始化方 法 ,传入生产或开发环境的 App Key。 

###### **TypeScript** 

- 10 - 

###### **/** 在 UIAbility 中获取 context 

let context = this.context 

```arkts
let initOption = new InitOption(); let appKey = "从融云后台获取的 appKey"; IMEngine.getInstance().init(context, appKey, initOption); 
```

###### 步骤 **4** :监听通话事件 

SDK 提供针对来电、 通话状态、 通话记录的事件处理机制。 

###### 设置监听 

以下示例代码 ,新建一个 CallListenerImpl 类实现 RCCallClientListener 接口。 并将实例设置给 SDK 。 

###### **TypeScript** 

**/** 在所需要的类声明 _ callClient 私有成员变量 ,后续示例中使用 private _callClient: RCCallClient | null = null ... /** * RCCallClient 单例 * export const CallClientInstance: RCCallClient = CallClientImpl.getInstance() */ **/** 创建 _ callClient 成员变量 ,供后续示例代码使用 this._callClient = CallClientInstance **/** 设置监听 this._callClient.callClientListener = new CallListenerImpl() 

###### 通话呼入 

通过实现 RCCallClientListener 中的 didReceiveCall 来监听通话呼入。 

###### **TypeScript** 

- 11 - 

export class CallListenerImpl implements RCCallClientListener { /** 

- 收到通话呼入的回调 * @param callSession 通话实例 

* @remarks 代理 */ didReceiveCall(callSession: RCCallSession): void { console.log('didReceiveCall', callSession) } } 

###### 通话状态变化 

通过实现RCCallClientListener 的通话连接 ,断开连接 ,人员变动来监听通话状态的变化。 

###### **TypeScript** 

- 12 - 

export class CallListenerImpl implements RCCallClientListener { 

- /** 

- 挂断通话的回调 

- @param callSession 通话实例 

- @param callDisconnectReason 通话挂断原因 

- @remarks 代理 

- */ 

didCallDisconnected(callSession: RCCallSession, callDisconnectReason: RCCallDisconnectReason): void { 

} 

- /** 

- 远端用户加入通话的回调 

- @param callSession 通话实例 

- @param userId 用户 ID 

- @param mediaType 媒体类型 

- @remarks 代理 

- */ 

didRemoteUserJoined(callSession: RCCallSession, userId: string, mediaType: RCCallMediaType): void { 

- } 

- /** 

- 远端用户挂断通话的回调 

- @param callSession 通话实例 

- @param userId 用户 ID 

- @param callDisconnectReason 通话挂断原因 

- @remarks 代理 

- */ 

didRemoteUserLeft(callSession: RCCallSession, userId: string, callDisconnectReason: 

RCCallDisconnectReason): void { 

} 

} 

###### 漏接电话 

通过实现 RCCallClientListener 中的 didMissCall 来监听漏接的通话。 

###### **TypeScript** 

- 13 - 

- /** 

- 收到通话漏接的回调 

- @param callSession 通话实例 

- @remarks 代理 

- */ 

didMissCall(callSession: RCCallSession): void { 

} 

###### 通话计时 

CallLib SDK 无法直接获取通话时长 ,您可以在通话建立成功、音频首帧回调、或视频首帧回调方法中 ,使用当前时间减去通 话起始时间 ,获取通话时长。 

###### **TypeScript** 

- /** 

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

} 

- /** 

- 收到远端用户视频首帧的回调 

- @param callSession 通话实例 

- @param userId 用户 ID 

- @remarks 代理 

- */ 

didReceiveFirstRemoteVideo(callSession: RCCallSession, userId: string): void { 

} 

提示 

- 14 - 

如需在应用程序的服务端进行通话计时 ,建议使用融云提供的服务端回调音视频房间状态同步。通过实时回调事件 event 11(成员加入音视频房间)和 event 12(成员加入音视频房间)记录计费的开始和结束时间。 

###### 步骤 **5** :连接 **IM** 服务 

音视频用户之间的信令传输依赖于融云的即时通信( IM)服务 ,因此需要先调用 connect 与 IM 服务建立好 TCP 长连接。建 议在功能模块的加载位置处调用 ,之后再进行音视频呼叫业务。 当模块退出后调用 disconnect 断开该连接。 

###### **TypeScript** 

###### **/** 连接 IM 

IMEngine.getInstance().connect(token, 20).then(result => { 

if (EngineError.Success === result.code) { 

**/** 连接成功 

```arkts
let userId = result.userId; return } if (EngineError.ConnectTokenExpired === result.code) { 
```

**/** Token 过期 ,从 APP 服务请求新 token ,获取到新 token 后重新 connect() } else if (EngineError.ConnectionTimeout === result.code) { 

**/** 连接超时 ,弹出提示 ,可以引导用户等待网络正常的时候再次点击进行连接 } else { **/** 其它业务错误码 ,请根据相应的错误码作出对应处理。 } }); 

###### 步骤 **6** :发起呼叫 

连接 IM 服务成功后 ,可调用 RCCallClient 中的startCall 方法来发起通话。 

###### 发起单人呼叫 

###### **TypeScript** 

- 15 - 

###### **/** 定义两个成员变量 

private _callClient: RCCallClient = CallClientInstance private _callSession: RCCallSession 

**/** 发起单人呼叫 

let callType = RCCallType.SINGLE; let targetId = 'userId' let userIds: string[] = ['userId'] let mediaType = RCCallMediaType.AUDIO let extra = 'extra' 

this._callClient.startCall(callType, targetId, userIds, mediaType, extra) .then((res) => { if(res.isSuccess){ this._callSession = res.callSession } else { " console.error( 呼叫失败, Code=" + RCCallErrorCode[res.code]) } }) 

###### 发起多人呼叫 

###### **TypeScript** 

###### **/** 发起多人呼叫 

```arkts
let callType = RCCallType.MULTI; let targetId = 'groupId' let userIds: string[] = ['userId'] let mediaType = RCCallMediaType.AUDIO let extra = 'extra' this._callClient.startCall(callType, targetId, userIds, mediaType, extra) .then((res) => { if(res.isSuccess){ this._callSession = res.callSession } else { " console.error( 呼叫失败, Code=" + RCCallErrorCode[res.code]) } }) 
```

###### 步骤 **7** :呼叫接听 

在收到 didReceiveCall 回调之后 ,调用如下方法接听通话。 

- 16 - 

**TypeScript** 

didReceiveCall(callSession: RCCallSession): void { 

this._callClient.accept() 

} 

### 通话管理 

###### 主叫方 

###### 发起呼叫 

调用 RCCallClient 的 startCall 方法发起单人或多人音视频通话 ,该方法默认打开前置摄像头。 多人通话场景所有通话者必 须在一个群组内。 

###### .    参数说明 : 

|参数|类型|必填|说明|
|---|---|---|---|
|callType|RCCallType|是|会话类型|
|targetId|string|是|目标会话ID,单人通话为对方UserId,群组通话为GroupId|
|userIds|string[]|是|邀请参与通话的用户ID列表 ,不能为null|
|callMediaTyp|eRCCallMediaTy|pe 是|通话媒体类型 ,音频或者音视频|
|extra 返回值 :|string|否|附加信息 ,透传至对端 ,对端通过RCCallSession.extra()获取|
|返回值|返回类型|说明||
|isSuccess|boolean|发起呼叫|成功/失败|
|code|RCCallErrorCode|成功返回|SUCCESS,失败时返回对应错误码|
|callSession|RCCallSession|呼叫成功|,返回当前会话对象|

###### .    返回值 : 

.    示例代码 : 

###### **TypeScript** 

- 17 - 

###### **/** 定义两个成员变量 

private _callClient: RCCallClient = CallClientInstance private _callSession: RCCallSession 

**/** 发起单人呼叫 let callType = RCCallType.SINGLE; let targetId = 'userId' let userIds: string[] = ['userId'] let mediaType = RCCallMediaType.AUDIO let extra = 'extra' 

this._callClient.startCall(callType, targetId, userIds, mediaType, extra) .then((res) => { if(res.isSuccess){ this._callSession = res.callSession } else { " console.error( 呼叫失败, Code=" + RCCallErrorCode[res.code]) } }) 

###### 挂断通话 

调用 RCCallClient 类的 hangup 方法挂断通话 ,拒绝和挂断为同一个方法 ,SDK 内部会通过 didCallDisconnected 回调 拒绝原因以及相关信息。 

.    示例代码 : 

###### **TypeScript** 

**/** 引用上述私有变量 this._ callClient 

this._callClient.hangup() 

###### 邀请通话 

调用 RCCallClient 类的 invite 方法邀请用户加入当前通话(仅限群组) ,该方法必须在通话已经建立onCallConnected 之 后调用。 

.    参数说明 : 

参数          类型          必填   说明 

userIds   string[]   是     邀请的用户 ID 列表 

.    返回值 : 

- 18 - 

返回值   返回类型                    说明 

code   RCCallErrorCode   成功返回 SUCCESS ,失败有对应错误码 

示例代码 : 

###### **TypeScript** 

**/** 邀请必须是群呼模式 ,邀请的用户 id 必须是群组内的人员 

let res = this._callClient.invite(['userId1','userId2']) 

###### 被叫方 

###### 接听通话 

###### 默认接听 

当收到来自 didReceiveCall 的远端通话请求时 ,可使用 RCCallClient 的 accept 方法来接听。该方法默认打开前置摄像 头。 

.    示例代码 : 

###### **TypeScript** 

didReceiveCall(callSession: RCCallSession): void { 

this._callClient.accept() } 

###### 拒绝 **/** 挂断通话 

调用 RCCallClient 的 hangup 方法挂断通话 ,拒绝和挂断为同一个方法 ,SDK 内部会通过 didCallDisconnected 告知对 方挂断、拒绝原因。 

.    示例代码 : 

###### **TypeScript** 

**/** 引用上述私有变量 this._ callClient 

this._callClient.hangup() 

- 19 - 

###### 通话监听 

融云鸿蒙版 CallLib 库提供了 RCCallClientListener 监听, 用于处理呼叫相关的业务逻辑上报。 

###### 来电监听 

需要设置 CallLib 的全局通话监听RCCallClientListener ,来监听通话呼入。 

- . 收到新通话 ,返回当前通话的详细信息。 

- . 漏接的通话 ,返回当前通话的详细信息。 

###### **TypeScript** 

this._callClient.callClientListener = { 

- /** 

- 收到通话呼入的回调 

- @param callSession 通话实例 

- @remarks 代理 

- */ 

didReceiveCall(callSession: RCCallSession): void { 

}, 

- /** 

- 收到通话漏接的回调 

- @param callSession 通话实例 

- @remarks 代理 

- */ 

didMissCall(callSession: RCCallSession): void { 

} } 

###### 通话建立、 结束等状态相关的回调 

- . 收到新通话 ,返回当前通话的详细信息。 

- . 已建立通话 ,返回当前通话的详细信息。 

- . 通话结束。对方挂断 ,己方挂断 ,或者通话过程网络异常造成的通话中断 ,都会通过同一个回调返回原 因RCCallDisconnectReason 。 

- 被叫端正在振铃 ,返回振铃用户的用户 ID。 

- . 被叫端加入通话 ,返回加入者的用户信息和摄像头信息。 

- . 通话中的某一个参与者 ,邀请好友加入通话。返回被邀请者的信息和媒体类型。 

- 通话中的远端参与者离开 ,返回离开者的信息和离开原因RCCallDisconnectReason 。在多人通话与 1v1 通话中 ,对 端挂断均会先回调 didRemoteUserLeft ,再触发其他回调。 

- 20 - 

. 当通话中的某一个参与者切换通话类型 ,例如由视频切换至音频。返回切换操作者的信息、切换后的媒体类型等。 .  通话过程中 ,发生异常。返回错误码 RCCallErrorCode。 

需在 this._callClient.callClientListener 中添加以下监听 : 

###### **TypeScript** 

- /** 

- 收到通话呼入的回调 

- @param callSession 通话实例 

- @remarks 代理 

- */ 

didReceiveCall(callSession: RCCallSession): void { 

}, 

- /** 

- 接通通话的回调 

- @param callSession 通话实例 

- @remarks 代理 

- */ 

didCallConnected(callSession: RCCallSession): void { 

}, 

- /** 

- 挂断通话的回调 

- @param callSession 通话实例 

- @param callDisconnectReason 通话挂断原因 

- @remarks 代理 

- */ 

didCallDisconnected(callSession: RCCallSession, callDisconnectReason: RCCallDisconnectReason): void { 

}, 

- /** 

- 远端用户正在响铃的回调 

- @param callSession 通话实例 

- @param userId 用户 ID 

- @remarks 代理 

- */ 

didRemoteUserRinging(callSession: RCCallSession, userId: string): void { 

}, 

- /** 

- 远端用户被邀请加入通话的回调 

- @param callSession 通话实例 

- @param userId 用户 ID 

- 21 - 

@p  r       s  rI   用户 I 

* @remarks 代理 

###### */ 

didRemoteUserInvited(callSession: RCCallSession, userId: string): void { 

###### }, 

###### /** 

- 远端用户加入通话的回调 

- @param callSession 通话实例 

- @param userId 用户 ID 

- @param mediaType 媒体类型 

- @remarks 代理 

- */ 

didRemoteUserJoined(callSession: RCCallSession, userId: string, mediaType: RCCallMediaType): void { 

}, 

- /** 

- 远端用户挂断通话的回调 

- @param callSession 通话实例 

- @param userId 用户 ID 

- @param callDisconnectReason 通话挂断原因 

- @remarks 代理 

- */ 

didRemoteUserLeft(callSession: RCCallSession, userId: string, callDisconnectReason: 

RCCallDisconnectReason): void { 

}, 

###### /** 

- 远端用户切换了媒体类型的回调 

- @param callSession 通话实例 

- @param userId 用户 ID 

- @param mediaType 媒体类型 

- @remarks 代理 

- */ 

didRemoteUserChangeMediaType(callSession: RCCallSession, userId: string, mediaType: RCCallMediaType): void { 

###### }, 

###### /** 

- 错误回调 

- @param callSession 通话实例 

- @param code 错误码 

- 22 - 

@p  r  m        错误码 

* @remarks 代理 

- */ 

didOccurError(callSession: RCCallSession, code: RCCallErrorCode): void { 

} 

###### 设备相关回调 

- 远端参与者摄像头状态发生变化时 ,回调 didRemoteUserDisableCamera 通知状态变化。 

- .  远端参与者麦克风状态发生变化时 ,回调 didRemoteUserDisableMic 通知状态变化。 

需在 this._callClient.callClientListener 中添加以下监听 : 

###### **TypeScript** 

- /** 

- 远端用户开关麦克风的状态变化回调 

- @param callSession 通话实例 

- @param userId 用户 ID 

- @param disable 是否关闭 

- @remarks 代理 

- */ 

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

###### 网络质量相关回调 

.  音频声音大小的回调 ,返回用户 ID 及音量大小 

- . 发送丢包率信息回调 ,返回丢包率及发送端的网络延迟。 

- .  接收丢包率信息回调 ,返回远端用户 ID 及丢包率。 

- . 收到某个用户的第一帧视频数据 ,返回用户信息及宽高数据。 

- 23 - 

需在 this._callClient.callClientListener 中添加以下监听 : 

###### **TypeScript** 

- /** 

- 音频声音大小的回调 

- 

- @param callSession 通话实例 

- @param userId 用户 ID 

- @param audioLevel 声音级别 :0~9 ,0 为无声 ,依次变大 

- 

###### * @remarks 代理 

- */ 

didAudioLevelChanged(callSession: RCCallSession, userId: string, audioLevel: number): void { 

}, 

- /** 

- 上行丢包率及延迟信息的回调 

- 

- @param callSession 通话实例 

- @param packetLostRate 丢包率 ,0-100 

- @param delay 发送端的网络延迟 ,单位毫秒 

- 

- @discussion 每秒回调一次 

- @remarks 代理 

- */ 

didSendPacketLost(callSession: RCCallSession, packetLostRate: number, delay: number): void { 

}, 

###### /** 

- 下行丢包率及延迟信息的回调 

- 

- @param callSession 通话实例 

- @param userId 用户 ID 

- @param packetLostRate 丢包率 ,0-100 

- 

- @discussion 每秒回调一次 

- @remarks 代理 

- */ 

didReceivePacketLost(callSession: RCCallSession, usedId: string, packetLostRate: number): void { 

} 

/** 

- 24 - 

# /** 

/**
* 收到远端用户视频首帧的回
*

### 视频管理 

# * **/** 码率 userId 用户 ID @param 

###### 分辨率 **/** 帧率 **/** 码率 

CallLib 提供 RCCallVideoConfig 视频配置类 ,用户可以在发起通话和接听通话前创建此对象 ,预设分辨率、 帧率、码率 , * 在后续通话中生效。 

###### 设置分辨率 

默认情况下 ,* SDK 使用默认分辨率 @remarks RCCallVideoResolution.SIZE_480_360。 修改 RCCallVideoConfig 的 videoResolution 调整分辨率。 代理 

.  示例代码 : * **TypeScript** / 

**/** 创建 videoConfig 对象 ,后续示例使用该实例 let videoConfig = new RCCallVideoConfig() videoConfig.vidi **d** eoResolution = RCCallV **i** deoResolution.SIZE_480_360 this._callClient.videoConfig = videoConfig 

###### 设置帧率 

默认情况下 ,SDK 使用默认帧率 Fps_15。 

在发起通话和接听通话前 ,可以修改 RCCallVideoConfig 的 videoFps 调整设置帧率 ,支持的帧率为 FPS_10、 FPS_15、 FPS_24、 FPS_30。 } 

.  示例代码 : 

- 25 - 

###### **TypeScript** 

FPS_15 

this 

###### 设置码率 

码率需要设置 minBitrate 和 maxBitrate ,单位是 kb/s ,通话过程中 SDK 上行数据会在用户设置的码率范围之内浮动。 

.  示例代码 

###### **TypeScript** 

videoConfig.maxBitrate = 1500 videoConfig.minBitrate = 200 this._callClient.videoConfig = videoConfig 

###### 摄像头设置 

###### 开关摄像头 

调用 RCCallClient 的 setCameraEnabled 方法打开或者关闭摄像头采集。 通话前开启摄像头采集对端不会收到 didRemoteUserDisableCamera 通知。 

###### .    参数说明 

参数         类型           说明 enable   boolean   是否开启摄像头 

###### .    返回值 : 

返回值   类型                          说明 

code   RCCallErrorCode   成功返回 SUCCESS ,失败有对应错误码 

###### 示例代码 : 

###### **TypeScript** 

let res = this._callClient.setCameraEnabled(true); 

###### 获取摄像头状态 

在使用 setCameraEnabled 后 ,SDK 会记录对应摄像头是否开启状态 ,后续通过getCameraEnabled 方法获取摄像头状 

- 26 - 

态。 

示例代码 : 

###### **TypeScript** 

let cameraEnable = this._callClient.getCameraEnabled() 

###### 切换前后置摄像头 

在通话过程中 ,调用switchCamera 方法切换前后置摄像头 ,返回接口的调用结果 ,成功或者失败 ,该方法同样适用于采集 前。 

.    示例代码 : 

###### **TypeScript** 

let res = this._callClient.switchCamera(); 

###### 设置视图 

###### 设置本地视图 

1. 在发起呼叫前 ,可以通过开启摄像头和设置本地视图来实现预览效果 ,调用 RCCallClient 的 setVideoView 方法 ,将 创建好的 RCCallVideoView 对象以及当前用户的 userId 传入即可。 

2. 结合 ArkTS XComponent  组件渲染视图 ,保证 RCCallVideoView 的 viewId 与 XComponent 的 id 一致且唯 一 ,建议使用 userId  。 

.    参数说明 : 

参数               类型                           必填   说明 userId string 是 用户id videoView RCCallVideoView 否 渲染视图对象 

.    示例代码 : 

###### **TypeScript** 

- 27 - 

@Component 

export struct MyStruct { 

###### **/** 一般使用用户真实的 userId 

localViewId: string = 'localUserId' 

private _callClient: RCCallClient = CallClientInstance } 

###### **TypeScript** 

XComponent({ 

id: this.localViewId, 

type: XComponentType.SURFACE, 

libraryname: 'nativerender' }) 

.onLoad((xComponentContext) => { 

**/** 设置本地视图 

- **/** RCRTCVideoFillMode 表示渲染模式 

let videoView = new RCCallVideoView(this.localViewId, RCRTCVideoFillMode.ASPECT_FILL) this._callClient.setVideoView(this.localViewId, videoView) }) 

.onAreaChange((oldValue: Area, newValue: Area) => { 

console.info("onAreaChange: newValue:" + JSON.stringify(newValue) + " , oldValue:" + JSON.stringify(oldValue)) 

}) 

.onSizeChange((oldValue: SizeOptions, newValue: SizeOptions) => { 

console.info("onSizeChange: newValue:" + JSON.stringify(newValue) + " , oldValue:" + JSON.stringify(oldValue)) 

}) 

.height('100%') 

.width('100%') 

###### 设置远端视图 

使用远端用户的 userId 构建 RCCallVideoView 对象当做参数 ,同样使用 setVideoView 方式可设置远端视图 ,无论是在 通话前或者通话中设置 ,SDK 会在拿到远端视频流数据后 ,寻找对应用户设置的 RCCallVideoView 视图并按需渲染。 

.    参数说明 : 

参数           类型                                 必填   说明 

viewId string 是 视图id ,用来渲染时使用 ,保证唯一性 fillMode RCRTCVideoFillMode 是 渲染模式 ,默认是 ASPECT_FILL 

.    示例代码 : 

- 28 - 

**TypeScript** 

###### **/** 设置远端视图 

@Component export struct MyStruct { 

**/** 一般使用用户真实的 userId 

remoteViewId: string = 'remoteUserId' 

private _callClient: RCCallClient = CallClientInstance } 

###### **TypeScript** 

XComponent({ 

id: this.remoteViewId, 

type: XComponentType.SURFACE, libraryname: 'nativerender' 

}) .onLoad((xComponentContext) => { 

**/** 设置远端渲染视图 

**/** RCRTCVideoFillMode 表示渲染模式 

let videoView = new RCCallVideoView(this.remoteViewId, RCRTCVideoFillMode.ASPECT_FILL) this._callClient.setVideoView(this.remoteViewId, videoView) }) 

.onAreaChange((oldValue: Area, newValue: Area) => { console.info("onAreaChange: newValue:" + JSON.stringify(newValue) + " , oldValue:" + JSON.stringify(oldValue)) }) 

.onSizeChange((oldValue: SizeOptions, newValue: SizeOptions) => { console.info("onSizeChange: newValue:" + JSON.stringify(newValue) + " , oldValue:" + JSON.stringify(oldValue)) 

}) 

.height('100%') .width('100%') 

###### 移除渲染视图 

当设置过视图后 ,如果需要移除该视图 ,还是使用 setVideoView 方法传入相同 userId  ,参数 videoView 传 null ,SDK 会根据传入的 userId 移除对应的视图。 

.    示例代码 : 

**TypeScript** 

- 29 - 

###### **/** 移除远端视图 

this._callClient.setVideoView(this.remoteViewId, null) 

**/** 移除本地视图 

this._callClient.setVideoView(this.localViewId, null) 

###### 视频转音频 

###### 视频转音频 

当用户希望从视频通话转为音频时 ,可以调用 RCCallClient 的 changeCallMediaType 方法。 目前仅支持视频转音频 ,即参 数只能为 RCCallMediaType.AUDIO。 

###### .    参数说明 

参数                      类型                           说明 

callMediaType RCCallMediaType 通话媒体类型 

###### .    返回值 : 

返回值   类型                          说明 

code   RCCallErrorCode   成功返回 SUCCESS ,失败有对应错误码 

###### .    示例代码 : 

###### **TypeScript** 

let res = this._callClient.changeCallMediaType(RCCallMediaType.AUDIO) 

###### 监听远端媒体切换 

当通话中对端用户调用 changeCallMediaType 做音视频切换至音频时 ,本端会通过 RCCallClientListener 的 

didRemoteUserChangeMediaType 回调监听到结果。 

###### .  示例代码 : 

- **TypeScript** 

- 30 - 

```arkts
this._callClient.callClientListener = { /** * 远端用户切换了媒体类型的回调 * * @param callSession 通话实例 * @param userId 用户 ID * @param mediaType 媒体类型 * * @remarks 代理 */ didRemoteUserChangeMediaType(callSession: RCCallSession, userId: string, mediaType: RCCallMediaType): void { **/** TODO: 通知业务层 } } 
```

### 音频管理 

###### 麦克风设置 

###### 麦克风静音 

当通话中希望关闭麦克风 ,可调用 RCCallClient 的 setMute 接口 ,传入 true 达到本地静音效果 ;当需要再次打开时 ,传入 false 即可。默认值为 false ,即麦克风默认为打开状态。 

.    示例代码 : 

###### **TypeScript** 

this._callClient.setMute(true) 

###### 获取麦克风状态 

通过 setMute 方法设置麦克风是否静音 ,后续可以通过getMute 获取麦克风是否被静音。 正在通话中 ,对端可通过监听 didRemoteUserDisableMic ,收到远端用户麦克风开关状态变更通知。 

示例代码 : 

###### **TypeScript** 

- 31 - 

let mute = this._callClient.getMute() 

###### 扬声器设置 

###### 听筒 **/** 扬声器切换 

当通话中希望切换声音由扬声器或听筒输出时 ,可调用 RCCallClient 的 setSpeakerEnabled 来设置。传入 true 代表使用 扬声器播放 ;false 代表使用听筒播放。默认是 false ,即默认使用听筒播放。 

.    示例代码 : 

###### **TypeScript** 

**/** 设置扬声器播放 

this._callClient.setSpeakerEnabled(true); 

###### 获取扬声器状态 

通过 setSpeakerEnabled 设置扬声器 ,SDK 会记录该状态 ,后续可以通过 getSpeakerEnabled 来获取是否启用扬声器。 

.    示例代码 : 

###### **TypeScript** 

###### **/** 是否扬声器播放 

let enable = this._callClient.getSpeakerEnabled() 

###### 音频路由 

由于鸿蒙系统不再提供音频输出设备切换的API ,如果需要应用内切换音频输出设备 ,请实现系统提供的 AVCastPicker 组 件 ,相关参数可参考使用通话设备切换组件 

###### 使用 **AVCastPicker** 切换音频路由 

1. 创建 voice_call 类型的 AVSession ,AVSession  在构造方法中支持不同的类型参数 ,由 AVSessionType 定 义 ,voice_call  表示通话类型 ,如果不创建 ,将显示空列表。 

###### **TypeScript** 

- 32 - 

```arkts
import { avSession } from '@kit.AVSessionKit'; 
```

private session: avSession.AVSession | = ; 

###### **/** 通话开始时创建voice_ call类型的avsession 

this.session = await avSession.createAVSession(getContext(this), 'voiptest', 'voice_call'); 

###### 2. 在需要切换设备的通话界面创建 AVCastPicker 组件。 

###### **TypeScript** 

```arkts
import { AVCastPicker } from '@kit.AVSessionKit'; 
```

###### **/** 创建组件 ,并设置大小 

build() { Row() { Column() { AVCastPicker() .size({ height:45, width:45 }) } } } 

###### 自定义样式实现 

自定义样式通过设置CustomBuilder 类型的参数 customPicker 实现。 

实现自定义样式的步骤与实现默认样式基本相同 ,开发者可参考默认样式实现 ,完成创建 AVSession 、 实现音频播放等步 骤。 

###### **TypeScript** 

- 33 - 

```arkts
import { AVCastPicker } from '@kit.AVSessionKit'; 
```

@State pickerImage:ResourceStr = $r('app.media.earpiece'); **/** 自定义资源 

```arkts
build() { Row() { Column() { AVCastPicker( { customPicker: (): void => this.ImageBuilder() **/** 新增自定义参数 } ).size({ height: 45, width:45 }) } } } 
```

**/** 自定义内容 

```arkts
@Builder ImageBuilder(): void { Image(this.pickerImage) .size({ width: '100%', height: '100%' }) .backgroundColor('#00000000') .fillColor(Color.Black) 
```

} 

#### 客户端 **API** 

以下是鸿蒙版 CallLib 的 API 参考文档 : 

·  CallLib 音视频通话(不含 UI) 

#### 状态码 

0 

SUCCESS 

成功。 

1 FAILED 

- 34 - 

失败 

排查建议 :接口调用失败。 

2 ONE_CALL_EXISTED 已经处于通话中了 

排查建议 :当前正在通话中 ,例如重复发起通话时会出现此错误码。 

3 NOT_IN_CALL 不在通话中 

排查建议 :有些接口调用限制在通话中状态 ,例如非通话状态切换媒体类型。 

4 OPERATION_UNAVAILABL E 无效操作 

排查建议 :该返回表示非法调用 ,或者是多余调用。 

5 

INVALID_PARAM 参数错误 

排查建议 :请检查当前接口的入参是否符合该接口要求 

- 35 -
