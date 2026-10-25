# **RTC** 融云音视频 ( ) 客户端 **SDK** 快速入门 HarmonyOS CallLib 

## 导入 **CallLib SDK** 

融云支持使用 DevEco Studio 中自动导入和手动导入两种方式 ,将 CallLib SDK 导入到您的应用工程中。 

##### 环境要求 

- . DevEco Studio NEXT Release(5.0.3.900) 及以上。 

- .  HarmonyOS SDK API 12 及以上。 

- .  手机(真机)系统版本号 :NEXT.0.0.31 

##### 自动导入 **SDK** 

- 1.0.0 版本开始支持 OpenHarmony三方库中心获取 SDK 

1. 在 entry 目录中的 oh-package.json5 中添加 SDK 依赖 ,然后点击 "Sync Now"。 

###### **JSON** 

**/** entry 目录中的 oh-package.json5 

{ "name": "entry", "version": "1.0.0", "description" : "Please describe the basic information.", "main" : "", "author": "", "license" : "", "dependencies": { "@rongcloudenterprise/calllib" : "x.y.z", "@rongcloudenterprise/imlib" : "x.y.z", "@rongcloud-enterprise/rtclib" : "x.y.z" } } 

注意 

.  各个 SDK 的最新版本号可能不相同 ,具体 x.y.z 值可前往融云官网 SDK 下载页面 或 OpenHarmony三方库中心 查询。 

1.    安装 SDK 成功后 ,您可以在项目根目录的 **oh_modules/.ohpm/** 中找到融云 callLib SDK。 

2.    查看更多其他融云 SDK。 打开OpenHarmony三方库中心 ,搜索关键字 **rongcloud** 

- 5 - 

##### 手动导入 **SDK** 

1. 在导入 SDK 前 ,您需要前往融云官网 SDK 下载页面 ,将音视频通话(无 UI)SDK 下载到本地。 

2. 创建 **./libs** 文件夹 ,将 SDK **har** 包 放入其中。 

#### 命令行安装 **SDK** 

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

#### **entry** 配置文件依赖 **SDK** 

在 **entry** 同级目录的 oh-package.json5 手动配置 SDK 依赖。 

###### **JSON** 

- **/** entry 同级目录下的 oh-package.json5 需要手动配置 

{ "name": "xxx", "version": "1.0.0", "description" : "Please describe the basic information.", "main" : "", "author": "", "license" : "", "dependencies": { "@rongcloud-enterprise/calllib" : "file:../libs/CallLib.har", **/** 该配置手动依赖 "@rongcloud-enterprise/imlib": "file:../libs/RongIMLib.har", **/** 该配置手动依赖 "@rongcloud-enterprise/rtclib": "file:../libs/RTCLib.har" **/** 该 

配置手动依赖 }, 

```arkts
"devDependencies": { "@ohos/hypium": "1.0.16", "@ohos/hamock" : "1.0.0" } } 
```

#### 同步项目 

- 7 - 

在 entry/oh-package.json5 中点击 **Sync Now** 同步工程 ,同步成功之后即可正常使用 CallLib SDK。 

### Q 提示 

如果您同步之后依然无法导入 SDK ,这可能是 DevEco Studio 的编译缓存导致的问题。您可以尝试把 DevEco Studio 完全关闭之后重新打开 APP 工程来解决问题。 

##### 配置项目 

#### 配置 **useNormalizedOHMUrl** 

1.0.0 版本开始 SDK 支持字节码 ,为了支持字节码 ,app 需要在项目根路径配置 **useNormalizedOHMUrl** 。 

// app 根路径下的 build-profile.json5 { "app": { "products": [ { "buildOption": { "strictMode": { "useNormalizedOHMUrl": true } } } ] } } 

##### 添加 **SDK** 依赖权限 

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

## 实现音视频通话 

CallLib 是在 RTCLib 基础上 ,额外封装了一套音视频呼叫功能 SDK ,包含了单人、 多人音视频呼叫的各种场景和功能 ,通过 集成它 ,您可以自由的实现音视频呼叫场景的各种玩法。 

注意 

房间人数上限 

考虑移动设备的带宽(主要是在多路视频情况下) ,建议单次通话或房间内 ,视频不超过 16 人 ,纯音频不超过 32 人。超过此上限可能影响通话效果。 

##### 步骤 **1** :服务开通 

您在融云创建的应用默认不会启用音视频服务。在使用融云提供的任何音视频服务前 ,您需要前往控制台 ,为应用开通音视频 服务。 

具体步骤请参阅开通音视频服务。 

注意 服务开通、 关闭等设置完成后 15 分钟后生效。 

##### 步骤 **2** : **SDK** 导入 

您需要导入融云音视频通话能力库 CallLib ,和 RTC 业务所依赖的即时通讯能力库 IMLib。根据您的业务需求 ,可选择导入美 颜扩展库。 

具体步骤请参阅 导入 CallLib SDK。 

##### 步骤 **3** :初始化 

CallLib 是基于 IM 作为信令通道的 ,所以要先初始化 IM 。如果不换 AppKey ,在整个应用生命周期中 ,初始化一次即可。 建议调用位置放在应用启动位置处 ,或在音视频功能模块的加载位置处。 在 UIAbility 的 onCreate() 方法中 ,调用初始化方 法 ,传入生产或开发环境的 App Key。 

###### **TypeScript** 

- 10 - 

###### **/** 在 UIAbility 中获取 context 

let context = this.context 

```arkts
let initOption = new InitOption(); let appKey = "从融云后台获取的 appKey"; IMEngine.getInstance().init(context, appKey, initOption); 
```

##### 步骤 **4** :监听通话事件 

SDK 提供针对来电、 通话状态、 通话记录的事件处理机制。 

#### 设置监听 

以下示例代码 ,新建一个 CallListenerImpl 类实现 RCCallClientListener 接口。 并将实例设置给 SDK 。 

###### **TypeScript** 

**/** 在所需要的类声明 _ callClient 私有成员变量 ,后续示例中使用 private _callClient: RCCallClient | null = null ... /** * RCCallClient 单例 * export const CallClientInstance: RCCallClient = CallClientImpl.getInstance() */ **/** 创建 _ callClient 成员变量 ,供后续示例代码使用 this._callClient = CallClientInstance **/** 设置监听 this._callClient.callClientListener = new CallListenerImpl() 

#### 通话呼入 

通过实现 RCCallClientListener 中的 didReceiveCall 来监听通话呼入。 

###### **TypeScript** 

- 11 - 

export class CallListenerImpl implements RCCallClientListener { /** 

- 收到通话呼入的回调 * @param callSession 通话实例 

* @remarks 代理 */ didReceiveCall(callSession: RCCallSession): void { console.log('didReceiveCall', callSession) } } 

#### 通话状态变化 

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

#### 漏接电话 

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

#### 通话计时 

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

##### 步骤 **5** :连接 **IM** 服务 

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

##### 步骤 **6** :发起呼叫 

连接 IM 服务成功后 ,可调用 RCCallClient 中的startCall 方法来发起通话。 

#### 发起单人呼叫 

###### **TypeScript** 

- 15 - 

###### **/** 定义两个成员变量 

private _callClient: RCCallClient = CallClientInstance private _callSession: RCCallSession 

**/** 发起单人呼叫 

let callType = RCCallType.SINGLE; let targetId = 'userId' let userIds: string[] = ['userId'] let mediaType = RCCallMediaType.AUDIO let extra = 'extra' 

this._callClient.startCall(callType, targetId, userIds, mediaType, extra) .then((res) => { if(res.isSuccess){ this._callSession = res.callSession } else { " console.error( 呼叫失败, Code=" + RCCallErrorCode[res.code]) } }) 

#### 发起多人呼叫 

###### **TypeScript** 

###### **/** 发起多人呼叫 

```arkts
let callType = RCCallType.MULTI; let targetId = 'groupId' let userIds: string[] = ['userId'] let mediaType = RCCallMediaType.AUDIO let extra = 'extra' this._callClient.startCall(callType, targetId, userIds, mediaType, extra) .then((res) => { if(res.isSuccess){ this._callSession = res.callSession } else { " console.error( 呼叫失败, Code=" + RCCallErrorCode[res.code]) } }) 
```

##### 步骤 **7** :呼叫接听 

在收到 didReceiveCall 回调之后 ,调用如下方法接听通话。 

- 16 - 

**TypeScript** 

didReceiveCall(callSession: RCCallSession): void { 

this._callClient.accept() 

} 

- 35 -
