# 融云音视频(RTC) 客户端 **SDK** 文档 HarmonyOS CallPlus 

## 目录 

|实现首次通话 环境要求|5 5|
|---|---|
|前置条件|5|
|快速上手|5|
|步骤1 创建项目|5|
|步骤2集成SDK|7|
|ohpm|7|
|步骤3 工程配置|7|
|步骤5 使用App Key 初始化|10|
|步骤6 添加通话所需代理|11|
|步骤7获取用户Token|13|
|步骤8 连接融云服务器|13|
|进行一对一通话|14|
|9 发起呼叫步骤|14|
|步骤10 接听|15|
|进行多人通话|15|
|步骤11 发起多人通话|16|
|与IM业务集成|16|
|在会话页面插入通话结束消息|16|
|在IM 中插入通话结束消息|17|
|一对一通话|17|
|关键类介绍|17|
|设置监听器|18|
|连接融云服务器|19|
|处理本地与远端视频视图|20|
|本地预览|20|
|远端视频视图|21|
|发起呼叫|22|

- 2 - 

|来电处理|23|
|---|---|
|通话设置|24|
|开关麦克风|24|
|开关摄像头|25|
|切换前后摄像头|25|
|配置视频设置|26|
|切换媒体类型|26|
|发起请求|26|
|响应请求|27|
|取消请求|28|
|通话中接听来电|29|
|通话中精准计时|30|
|结束通话|30|
|管理通话记录|31|
|通话结束后获取通话记录|32|
|检索服务端通话记录|32|
|删除通话记录|32|
|管理通话质量|33|
|音视频首帧回调|34|
|多人通话|35|
|发起多人通话|35|
|接听多人通话|35|
|邀请他人加入通话|36|
|邀请用户|36|
|获取邀请详情|37|
|接受或拒绝邀请|37|
|结束通话|38|
|获取未结束的多人通话|39|
|配置推送属性|39|
|推送属性说明|40|
|自定义加密|40|

- 3 - 

步骤 1 创建加解密模块 

|步骤1 创建加解密模块|41|
|---|---|
|步骤2 实现加密方法|43|
|步骤3:实现自定义解密|47|
|步骤4:配置加解密库|51|
|步骤5:在CallPlus 中使用加解密|52|
|状态码|54|

- 4 - 

### 实现首次通话 

适用于 HarmonyOS 的 CallPlus 可在您的应用程序中为用户之间的一对一和多人通信提供语音和视频通话能力。 

CallPlus 支持一对一通话 和 多人通话。按照下面的指南使用 ArkTS / TypeScript 从头开始实现一对一通话和多人通话。 

###### 环境要求 

适用于 HarmonyOS 的 CallPlus SDK 的最低要求如下。 

- . DevEco Studio NEXT Release(5.0.3.900) 及以上。 

- . HarmonyOS SDK API 12 及以上。 

- . 手机系统版本号:NEXT.0.0.31 

###### 前置条件 

- . 注册开发者账号。注册成功后,控制台会默认自动创建您的首个应用,默认生成开发环境下的 App Key ,使用国内数 据中心。 

获取开发环境的应用AppApp Key。如不使用默认应用,请参考。如不使用默认应用,请参考 如何创建应用,并获取对应环境 App Key 和 App
Secret。。

- . 获取开发环境的应用AppApp Key。如不使用默认应用,请参考。如不使用默认应用,请参考 如何创建应用,并获取对应环境 App Key 和 App Secret。。 

注意 

每个应用具有两个不同的 App Key ,分别对应开发环境与生产环境,两个环境之间数据隔离。在您的应用正式上 线前,可切换到使用生产环境的 App Key ,以便上线前进行测试和最终发布。 

- . 完成开通音视频服务。您需要开通音视频通话服务。 

###### 快速上手 

您可以通过集成 CallPlus for HarmonyOS 进行一对一通话,或多人通话。 

##### 步骤 **1** 创建项目 

打开 DevEco-Studio 并创建一个新项目,选择模版。 

- 5 - 

配置 quickDemo ,点击 创建 

- 6 - 

##### 步骤 **2** 集成 **SDK** 

您可以使用ohpm 安装 @rongcloud/callplus ,也可以通过下载对应的 har 文件手动导入到工程中。 

###### **ohpm** 

1. 找到工程目录的 oh-package.json5 文件,增加 dependencies 依赖配置。 

2. 上一步完成后,点击 Sync Now 或者在项目当前目录打开终端,执行 ohpm install IDE 会自动对应下载好 har 包。 

注意 

注意每个 SDK 的最新版本号可能不相同,具体版本可前往OpenHarmony三方库中心仓 查询。 

##### 步骤 **3** 工程配置 

1. 您的用户需要授予您的应用访问设备上的权限,请在 quickDemo/entry/src/main/ 目录下找到 module.json5 文件 中添加 requestPermissions 如下所示,需要增加相机麦克风以及网络访问权限。 

###### **JSON** 

{ 

"module" : { 

- "name": "entry", 

- "type": "entry", 

- "description" : "$string:module_desc", " i El t" "E t Abilit " 

- 7 - 

"mainElement": "EntryAbility", "deviceTypes": [ "phone" ], "deliveryWithInstall": true, "installationFree": false, "pages": "$profile:main_pages", "abilities": [ { "name": "EntryAbility", "srcEntry": "./ets/entryability/EntryAbility.ets", "description" : "$string:EntryAbility_desc", "icon": "$media:layered_image", "label": "$string:EntryAbility_label", "startWindowIcon": "$media:startIcon", "startWindowBackground": "$color:start_window_background", "exported": true, "skills": [ { "entities": [ "entity.system.home" ], "actions": [ "action.system.home" ] } ] } ], "extensionAbilities": [ { "name": "EntryBackupAbility", "srcEntry": "./ets/entrybackupability/EntryBackupAbility.ets", "type": "backup", "exported": false, "metadata": [ { "name": "ohos.extension.backup", "resource" : "$profile:backup_config" } ], } ], "requestPermissions": [ { " " " h r i i CAMERA" 

- 8 - 

name : ohos.permission.CAMERA , "reason": "$string:Camera", "usedScene": { "abilities": [ "EntryAbility", ], "when": "always" } }, { "name": "ohos.permission.MICROPHONE", "reason": "$string:Microphone", "usedScene": { "abilities": [ "EntryAbility", ], "when": "always" } }, { "name": "ohos.permission.INTERNET", "reason": "$string:InterNet", "usedScene": { "abilities": [ "EntryAbility", ], "when": "always" } }, { "name": "ohos.permission.GET_NETWORK_INFO", "reason": "$string:InterNet", "usedScene": { "abilities": [ "EntryAbility", ], "when": "always" } } ] } } 

2. 配置权限时,按照规则需要考虑国际化问题,对应在 quickDemo/entry/src/main/resources/base/element 找到 string.json 文件对应增加配置字符变量,如下所示。 

- 9 - 

**JSON** 

{ "string" : [ { "name": "module_desc", "value": "module description" }, { "name": "EntryAbility_desc", "value": "description" }, { "name": "EntryAbility_label", "value": "label" }, { "name": "Microphone", "value": "Microphone in RTC" }, { "name": "Camera", "value": "Camera in RTC" }, { "name": "InterNet", "value": "InterNet" } ] } 

如需增加其他相关权限配置,参考鸿蒙官网文档权限配置 

##### 步骤 **5** 使用 **App Key** 初始化 

CallPlus 是基于 IMLib 作为信令通道的,要在您的应用程序中集成和运行,您需要先对 IMLib 初始化,核心类为 IMEngine 在 UIAbility 的 onCreate() 方法中,调用初始化方法,传入生产或开发环境的 App Key。 

###### **TypeScript** 

- 10 - 

**/** 在UIAbility 中获取context 

let context = this.context 

let initOption = new InitOption(); let appKey = "从融云后台获取的 appKey" IMEngine.getInstance().init(context, appKey, initOption) 

初始化配置 InitOption 中封装了区域码 RCAreaCode ,导航服务地址 naviServer、统计服务地址 statisticServer ,文件 下载路径 mediaSavePath。不作设置表示全部使用默认配置。 SDK 默认连接北京数据中心。 

###### 注意 

每个融云应用提供开发环境与生产环境,分别使用不同的 App Key ,两个环境之间数据隔离。只要客户端应用使用同一 个环境的 App Key ,用户可以跨所有平台相互通信。 

##### 步骤 **6** 添加通话所需代理 

CallPlus for HarmonyOS 提供了 ICallPlusEventListener 监听来处理通话相关事件。 

###### 注意 

如果未设置 ICallPlusEventListener 代理,则用户无法接收 onReceivedCall 回调事件。请务必在下文连接 

(connectWithToken)步骤之前使用 setCallEventDelegate 注册监听,否则用户在未连接的情况下,通过离线推送 打开应用连接 IM 后无法收到通话。 

初始化 callPlus 并设置 ICallPlusEventListener 监听 

###### **TypeScript** 

private _initCallPlus() { 

- **/** 初始化callPlus、注册应用层事件 

RCCallPlusClient.getInstance().init({ 

isPubTiny: false, 

}); 

RCCallPlusClient.getInstance().setCallPlusEventListener({ 

- /** 

- 呼入通知 

- 收到呼入时,可选择接听或挂断通话 

- @param session 通话实例 

- *@param extra 透传呼叫方发起呼叫时携带的附加信息 

- */ 

onReceivedCall: (session: RCCallPlusSession, extra?: string | undefined): void => { const callId = session.getCallId(); 

const syncData = session.getSyncData(); 

- 11 - 

const isSecret = session.isSecret(); 

' ' console.log( 呼入通知 , callId, extra, syncData, isSecret); 

}, 

/** 

- 通话已建立,sdk 内部会发布音视频资源 

*/ 

###### onCallConnected: (session: RCCallPlusSession): void => { 

const callId = session.getCallId(); 

' ' console.log( 本端加入通话 , callId); 

}, 

/** 

- 通话结束(群组通话时,客户端挂断不代表通话结束) 

- @param session 通话实例 

- *@param reason 通话结束原因 

- */ 

onCallEnded: (session: RCCallPlusSession, reason: RCCallPlusReason): void => { ' ' console.log( 通话结束 , session.getCallId(), reason); 

}, 

/** 

- 收到通话结束的消息记录,可用于在IM 聊天界面插入通话结束消息 * 仅单聊可收到 

- 触发时机: 

- 1.单聊在线通话结束后 

- 2.离线时收到单聊呼叫,通话结束后,重新连接IM 在线时 

- *@param message 通话记录的消息体 

- */ 

onReceivedCallPlusSummaryMessage(message: Message) { 

' console.log( 收到 Call Plus summary message', JSON.stringify(message)); 

}, /** 

- 收到远端人员被邀请加入通话通知 

- *@param inviteeUserList被邀请人员列表 

- @param inviterUserId 邀请人员ID 

- @param callId 通话ID 

- */ 

onRemoteUserInvited: (inviteeUserList: string[], inviterUserId: string, callId: string): void => { ' ' console.log( 收到远端人员被邀请加入通话通知 , inviteeUserList, inviterUserId, callId); 

}, 

/** 

- 远端用户的音视频首帧渲染 

- @param userId远端用户ID 

- @param mediaType 媒体类型 

- */ 

onFirstFrame: (userId: string, mediaType: RCCallPlusMediaType): void => { 

console.log(`${userId}的 ${(mediaType === RCCallPlusMediaType.AUDIO) ? '音频' : '视频' }可渲染`); 

- 12 - 

} }) 

} 

##### 步骤 **7** 获取用户 **Token** 

用户身份令牌( Token)与用户 ID 对应,是应用程序用户在融云的唯一身份标识。应用客户端在使用融云服务前必须与融云 建立 IM 连接,连接时必须传入 Token。 

在体验和调试阶段,我们将使用控制台「北极星」开发者工具箱,从 API 调试页面调用获取 Token 接口,获取到 **userId** 为 1 的用户的 Token。提交后,可在返回正文中取得 Token 字符串。 

###### **HTTP** 

HTTP/1.1 200 OK 

Content-Type: application/json; charset=utf-8 

{"code":200,"userId":"1","token":"gxld6GHx3t1eDxof1qtxxYrQcjkbhl1V@sgyu.cn.example.com;sgyu.cn.exam 

融云的客户端 SDK 不提供获取 token 的 API。在实际业务运行过程中,调用融云 Server API /user/getToken.json , 传入您的应用分配的用户标识( userId)申请 Token。详见 Server API 文档 注册用户。 

##### 步骤 **8** 连接融云服务器 

要拨打和接听一对一对呼叫或开始多人呼叫,必须先通过 IMEngine 的 connect 方法连接融云服务器,传入用户身份令牌 (Token),向融云服务器验证用户身份。 

获取 Token 以后,可以调用 connectWithToken 方法连接到融云服务器。 

###### **TypeScript** 

- 13 - 

**/** 连接IM 服务 

private _connectIM(token: string) { **/** 连接IM IMEngine.getInstance().connect(token, 20).then(result => { if (EngineError.Success === result.code) { 

**/** 连接成功 let userId = result.userId; return } if (EngineError.ConnectTokenExpired === result.code) { 

   - **/** Token 过期,从APP 服务请求新token ,获取到新token 后重新connect() 

- } else if (EngineError.ConnectionTimeout === result.code) { 

**/** 连接超时,弹出提示,可以引导用户等待网络正常的时候再次点击进行连接 } else { 

**/** 其它业务错误码,请根据相应的错误码作出对应处理。 } }); } 

###### 进行一对一通话 

CallPlus for HarmonyOS SDK 提供了仅限两位用户通话的一对一通话类型 RCCallPlusType.SINGLE。发起一对一类型通 话时,只允许传入一个被叫用户 ID ,仅在被叫接听成功后才会建立通话。融云会在被叫接听成功后开始计时。 

本节中将简单介绍如何发起一对一通话,如何接收来电,以及通话接通后双方通话界面如何显示。 

##### 步骤 **9** 发起呼叫 

使用 RCCallPlusClient 的 startCallWithParams 方法发起一对一通话。方法调用后,SDK 内部会以异步方式执行。在主叫 与被叫端触发以下回调: 

- 本地主叫用户通过 startCallWithParams 的返回值 Promise 来获取方法的执行结果。 

- 远端被叫用户通过 ICallPlusEventListener 的 onReceivedCall 回调获取来电通知。 

###### **TypeScript** 

- 14 - 

private _startCall() { RCCallPlusClient.getInstance().startCallWithParams({ userIds: ['userId1'], mediaType: RCCallPlusMediaType.AUDIO, extra: 'extra', syncData: 'syncData' }).then((result) => { if (result.code === RCCallPlusCode.SUCCESS) { ' ' console.log( 发起通话成功 ); } else { ' ' console.log( 发起通话失败 , result.code); } }); } 

##### 步骤 **10** 接听 

被呼叫端通过监听 onReceivedCall 方法接收通话,记录 callId 然后使用 accept 方法接听来电。 

###### **TypeScript** 

private _accept(callId: string) { RCCallPlusClient.getInstance().accept(callId).then((result) => { if (result.code === RCCallPlusCode.SUCCESS) { ' ' console.log( 接听成功 ); } else { ' ' console.log( 接听失败 , result.code); } }); } 

应用未启动,被叫方通过远程通知接收来电。点击收到的推送通知后启动 App ,在设置 RCCallPlusEventDelegate 代 理并连接 IM 成功后,还是通过 [didReceivedCall:extra:] 接收到通话。 

###### 进行多人通话 

CallPlus for HarmonyOS SDK 提供了支持多人呼叫的通话类型 RCCallPlusType.MULTI。发起多人通话与一对一通话使用 相同的方法,多人通话一旦发起成功,融云即开始计时计费。 

下文仅描述了发起多人通话的方法。在实际项目中,我们建议您先按照一对一通话 实现完整的通话流程,再按照多人通话补 充实现与一对一通话有差异的步骤。 

- 15 - 

在一对一通话过程中可以邀请用户加入通话。一旦邀请成功,通话类型会自动转为多人通话。详见多人通话。 

##### 步骤 **11** 发起多人通话 

使用 startCallWithParams 方法,callType 参数必须为 RCCallPlusType.MULTI 多人通话类型。 

###### **TypeScript** 

private _startMultiCall() { RCCallPlusClient.getInstance().startCallWithParams({ userIds: ['userId1', 'userId2'], type: RCCallPlusType.MULTI, mediaType: RCCallPlusMediaType.AUDIO, extra: 'extra', syncData: 'syncData' }).then((result) => { if (result.code === RCCallPlusCode.SUCCESS) { ' ' console.log( 发起通话成功 ); } else { ' ' console.log( 发起通话失败 , result.code); } }); } 

###### 注意 

有关在您的应用程序中构建语音和视频通话功能的详细指南,请参阅完整的一对一通话和多人通话 文档。我们建议您先 按照一对一通话实现完整的通话流程,再按照多人通话补充实现与一对一通话有差异的步骤。 

### 与 **IM** 业务集成 

您可以将 CallPlus 集成到基于 IMLib SDK 的应用程序中,为用户提供使用通话和聊天服务的无缝体验。 

###### 在会话页面插入通话结束消息 

应用程序可以通话结束时返回聊天视图,并在会话页面中展示通话结束的消息。 

CallPlus SDK 可在通话结束时通过回调 onReceivedCallPlusSummaryMessage 返回一个 IM 消息对象,其中包含消息内 容对象包含了通话信息。用户可以通过调用 IMLib SDK 的接口直接将该消息内容对象插入到会话中。 

- 16 - 

在 **IM** 中插入通话结束消息 

重要 

CallPlus SDK 暂仅支持在一对一通话(通话类型为 RCCallPlusType.SINGLE)结束时返回用于展示通话记录的消息内 容。暂不支持支持多人通话。 

通话正常、异常结束,或在未接听时挂断,CallPlus SDK 会触发 ICallPlusEventListener 的 onReceivedCallPlusSummaryMessage 回调方法,可在该回调方法获取到通话结束的消息内容对象。 

如果被叫时用户不在线,CallPlus SDK 会在下次成功连接 IM 后立即获取离线时产生的。为了确保 CallPlus SDK 可在 IM 连 接成功后立即获取到这些消息,请在 IM 连接之前调用 setCallPlusEventListener 注册监听器。 

收到通话结束消息时,可以将 message 通过 insertMessage 方法插入到本地会话中,并自行刷新 UI。 

###### **TypeScript** 

onReceivedCallPlusSummaryMessage(message: RCMessage) { 

- **/** CustomSummaryMessage 属于sdk提供的自定义消息,包含通话记录所需信息 

let summaryMsg = message.content as CustomSummaryMessage 

' console.log( 收到 Call Plus summary message', JSON.stringify(summaryMsg)) 

IMEngine.getInstance().insertMessage(message).then((result) => { 

if (result.code === EngineError.Success) { 

' ' console.log( 插入消息成功 ); 

- } else { 

' ' console.log( 插入消息失败 , result.code); 

} }); 

} 

### 一对一通话 

本页介绍了一对一呼叫的主要功能,包括如何从您的应用程序拨打、接听、处理和结束呼叫。 

###### 关键类介绍 

- RCCallPlusClient : RCCallPlusClient 单例对象是 CallPlus for HarmonyOS SDK 的核心类,用于管理客户端呼叫 行为,例如发起、接听、挂断通话,操作音视频设备,管理通话记录等。 

- 17 - 

- RCCallPlusSession :RCCallPlusSession 对象代表一则通话的所有信息,提供 

   - getCallId 、 getCallType 、 getMediaType 、 getUserList 等获取通话属性的方法。 

- IRCCallPlusCallRecord :IRCCallPlusCallRecord 代表一则通话记录,其中包含了与 RCCallPlusSession 类似的通 话信息,还提供了通话开始与结束的时间戳、通话时长、通话结束原因等信息。 

- ICallPlusEventListener :监听器 ICallPlusEventListener 提供了来电事件(onReceivedCall)、通话建立成功 

   - (onCallConnected)、收到通话记录([onReceivedCallPlusSummaryMessage])等事件相关回调。 

- IStatusReportListener :监听器 IStatusReportListener 提供通话中的通话质量数据后调。 

###### 设置监听器 

CallPlus for HarmonyOS SDK 提供了两个监听器: 

- . ICallPlusEventListener 监听器用于接收来自远端用户或服务端的事件。 

- . IStatusReportListener 监听器用于通话中音视频上下行丢包数据。 

###### 请在应用程序初始化或呼叫模块初始化时设置监听器: 

1. 调用 RCCallPlusClient.getInstance().setCallPlusEventListener 方法设置 ICallPlusEventListener 监听器。 

###### **TypeScript** 

RCCallPlusClient.getInstance().setCallPlusEventListener({ 

- /** * 呼入通知 * 收到呼入时,可选择接听或挂断通话 

- @param session 通话实例 

- *@param extra 透传呼叫方发起呼叫时携带的附加信息 

- */ 

```arkts
onReceivedCall: (session: RCCallPlusSession, extra?: string | undefined): void => { const callId = session.getCallId(); const syncData = session.getSyncData(); const isSecret = session.isSecret(); 
```

- ' ' 

- console.log( 呼入通知 , callId, extra, syncData, isSecret); 

- }, /** * 通话已建立,sdk 内部会发布音视频资源 

- */ 

onCallConnected: (session: RCCallPlusSession): void => { const callId = session.getCallId(); 

' ' console.log( 本端加入通话 , callId); }, /** 

- 通话结束(群组通话时,客户端挂断不代表通话结束) 

- @param session 通话实例 通话结束 

- 18 - 

*@param reason 通话结束原因 

###### */ 

onCallEnded: (session: RCCallPlusSession, reason: RCCallPlusReason): void => { 

' ' console.log( 通话结束 , session.getCallId(), reason); 

}, /** 

- 收到通话结束的消息记录,可用于在IM 聊天界面插入通话结束消息 

- 仅单聊可收到 

* 触发时机: 

- 1.单聊在线通话结束后 

- 2.离线时收到单聊呼叫,通话结束后,重新连接IM 在线时 

- *@param message 通话记录的消息体 */ 

onReceivedCallPlusSummaryMessage(message: Message) { 

' console.log( 收到 Call Plus summary message', JSON.stringify(message)); }, /** 

- 收到远端人员被邀请加入通话通知 

- @param inviteeUserList被邀请人员列表 

- @param inviterUserId 邀请人员ID 

- @param callId 通话ID 

- */ 

```arkts
onRemoteUserInvited: (inviteeUserList: string[], inviterUserId: string, callId: string): void => { ' ' console.log( 收到远端人员被邀请加入通话通知 , inviteeUserList, inviterUserId, callId); }, /** 
```

- 远端用户的音视频首帧渲染 

- @param userId远端用户ID 

- @param mediaType 媒体类型 

- */ 

onFirstFrame: (userId: string, mediaType: RCCallPlusMediaType): void => { 

console.log(`${userId}的 ${(mediaType === RCCallPlusMediaType.AUDIO) ? '音频' : '视频' }可渲 染`); 

} 

}) 

###### 连接融云服务器 

要使用 CallPlus SDK 的通话能力,必须先通过 IMEngine 的 connect 方法连接融云服务器,传入用户身份令牌 

(Token),向融云服务器验证用户身份。连接成功后,使用 RCCallPlusClient.getInstance().init() 方法初始化和配置 CallPlus SDK。 

注意 

- 19 - 

必须在连接成功之后调用 RCCallPlusClient.getInstance().init 方法初始化 CallPlus SDK。 

###### **TypeScript** 

let token = "用户Token"; 

IMEngine.getInstance().connect(token, 20).then(result => { 

if (EngineError.Success === result.code) { 

**/** 连接成功 let userId = result.userId; } else { **/** 连接失败 } }); 

###### 处理本地与远端视频视图 

在主叫方发起通话前,被叫方接听通话时需要使用setVideoView 方法设置视频视图,删除已设置的用户视频视图请调用 removeVideoView 方法。若远端用户没有设置视频渲染视图,则不会产生该用户的视频流的下行流量。 

在鸿蒙开发中的渲染通常需要结合 XComponent 组件,通过设置 viewId 来标识 RCCallPlusVideoView 与 XComponent 的唯一性。 

##### 本地预览 

一般在发起通话前使用 setVideoView 方法,传入当前 userId 以及 RCCallPlusVideoView 实例,同时需要配合 startCamera 接口开启摄像头,就可以实现本地预览。当通话连接成功,本地预览的流才会发布到远端。 

###### **TypeScript** 

- 20 - 

**/** 可以在.ets 文件,aboutToAppear 方法里面设置本地预览 

privite viewId: string 

aboutToAppear(): void { 

**/** currentUserId取当前的userId 

const currentUserId = 'current userId' this.viewId = currentUserId 

let videoView = new RCCallPlusVideoView(this.viewId, RCRTCVideoFillMode.ASPECT_FILL) 

RCCallPlusClient.getInstance().setVideoView([{userId: currentUserId, videoElement: videoView, isTiny: isTiny}]) 

} 

... 

XComponent({ 

id: this.viewId, 

type: XComponentType.SURFACE, 

libraryname: 'nativerender' 

}) 

.id(this.viewId) .height('100%') .width('70%') 

##### 远端视频视图 

远端视频渲染和本地视图渲染一样使用 setVideoView 方法,支持在通话前或者通话连接成功后设置,需要指定远端用户的 userId 并且需要设置 viewId 来标识唯一性。接通前设置时,只有接通后 SDK 收到对应视频首帧了,才会开始渲染。 

###### **TypeScript** 

- 21 - 

###### **/** 定义viewId成员变量 

private viewId: string 

let remoteUserId = "remote UserId" 

this.viewId = remoteUserId 

let remoteViewView = new RCCallPlusVideoView(this.viewId, RCRTCVideoFillMode.ASPECT_FILL) 

RCCallPlusClient.getInstance().setVideoView([{userId:remoteUserId, videoElement:.remoteViewView, isTiny:true}]) 

... 

**/** 使用Stack 容器组件,可在XComponent 叠加Text显示userId 

Stack({alignContent: Alignment.TopStart}) { XComponent({ 

id: this.viewId, 

type: XComponentType.SURFACE, libraryname: 'nativerender' }) Text(`${this.user.uid}`) 

.backgroundColor('#6a000000') .padding(5) .fontColor(Color.White) .fontSize(14) } .id(this.viewId) .width('70%') 

###### 发起呼叫 

CallPlus 定义了一对一通话类型( RCCallPlusType.SINGLE)。您可以使用 [startCallWithParams] 方法来发起一对一通 话。 

###### **TypeScript** 

- 22 - 

RCCallPlusClient.getInstance().startCallWithParams({ userIds: ['userId1'], type: RCCallPlusType.SINGLE, mediaType: RCCallPlusMediaType.AUDIO, extra: 'extra', syncData: 'syncData' 

}).then((result) => { if (result.code === RCCallPlusCode.SUCCESS) { ' ' console.log( 发起通话成功 ); } else { ' ' console.log( 发起通话失败 , result.code); } }); 

该方法调用后,SDK 内部会以异步方式执行。在主叫与被叫端触发以下回调: 

. 远端被叫用户通过 ICallPlusEventListener 的 onReceivedCall 回调获取来电通知。 

本地主叫用户将通过 ICallPlusEventListener 的 [onRemoteUserStateChanged] 回调获取到被叫用户状态变更。 

通话建立成功后,主叫端已经设置的setVideoView 中会自动渲染远端被叫用户的视图。 

###### 来电处理 

被叫方的客户端应用程序中必须先注册 ICallPlusEventListener 监听器,才能通过 onReceivedCall 接收来电通 

知。onReceivedCall 方法中会返回 RCCallPlusSession 对象,通过 getCallId() 可获取 callId ,使用 getCallType() 可获 取通话类型。 

###### 调用以下方法选择是否接听来电: 

. 接听来电,使用 RCCallPlusClient.getInstance().accept(callId) 方法。如果呼叫被接受,CallPlus SDK 将自动建立 媒体会话。 

- . 挂断来电,使用 RCCallPlusClient.getInstance().hangup(callId) 方法。 

您可以在收到来电事件后打开摄像头采集,并完成本地视图设置。 

###### **TypeScript** 

- 23 - 

onReceivedCall: (session: RCCallPlusSession, extra?: string | ): void => { 

const callId = session.getCallId(); 

const syncData = session.getSyncData(); const isSecret = session.isSecret(); 

' ' console.log( 呼入通知 , callId, extra, syncData, isSecret); **/** 接听 

const { code } = await RCCallPlusClient.getInstance().accept(callId); 

` ` console.log( 接听通话结果, code: ${code} ); } 

###### 同样在 onReceivedCall 监听到有新呼入的电话时,调用hangup 方法直接挂断。 

###### **TypeScript** 

onReceivedCall: (session: RCCallPlusSession, extra?: string | ): void => { 

const callId = session.getCallId(); 

```arkts
const syncData = session.getSyncData(); const isSecret = session.isSecret(); ' ' console.log( 呼入通知 , callId, extra, syncData, isSecret); **/** 来电拒接 
```

const { code } = await RCCallPlusClient.getInstance().hangup(callId); 

` ` console.log( 挂断通话结果, code: ${code} ); } 

###### 通话设置 

##### 开关麦克风 

在通话过程中,您可以使用 [startMicrophone] 方法来开启麦克风,stopMicrophone 方法来关闭麦克风。 

###### **TypeScript** 

**/** 开启麦克风,code 为当前接口的调用结果 

const {code} = await RCCallPlusClient.getInstance().startMicrophone(); 

**/** 停止麦克风采集 

const {code} = await RCCallPlusClient.getInstance().stopMicrophone(); 

当麦克风状态改变时,另一方将通过 ICallPlusEventListener 的 onRemoteMicrophoneStateChanged 回调方法接收事 件回调。 

- 24 - 

###### **TypeScript** 

RCCallPlusClient.getInstance().setCallPlusEventListener({ 

/** 

* 远端用户麦克风状态改变监听 

- 

- *@param callId 通话Id 

- @param userId 用户Id 

- @param disabled 麦克风是否可用,true:麦克风为关闭状态。false :麦克风为开启状态。 */ 

onRemoteMicrophoneStateChanged(callId: string, userId: string, disabled: boolean): void { ' ' console.log( 收到远端麦克风状态通知 , callId, userId, disabled) } 

}); 

##### 开关摄像头 

在通话过程中,您可以通过使用startCamera 或 stopCamera 方法来开启或关闭摄像头。可通过 ICallPlusEventListener 获取摄像头状态改变的通知。 

###### **TypeScript** 

**/** 开启摄像头数据采集 

let result = await RCCallPlusClient.getInstance().startCamera() **/** 关闭摄像头数据采集 

let result = await RCCallPlusClient.getInstance().stopCamera(); 

另一方将通过 ICallPlusEventListener 的 [onRemoteCameraStateChanged] 回调方法接收事件回调。 

###### **TypeScript** 

RCCallPlusClient.getInstance().setCallPlusEventListener({ 

/** 

* 远端摄像头开、关通知 

- *@param callId 通话id 

- *@param userId 用户id 

- @param disabled是否关闭 */ 

onRemoteCameraStateChanged(callId: string, userId: string, disabled: boolean): void { ' ' console.log( 收到摄像头状态通知 , callId, userId, disabled) } 

}); 

##### 切换前后摄像头 

- 25 - 

成功打开摄像头后,您可以使用switchCamera 方法切换前后摄像头。该方法是异步调用的,您可以通过该方法的返回值来 获取调用结果。 

###### **TypeScript** 

**/** 切换前后摄像头 

let result = await RCCallPlusClient.getInstance().switchCamera() 

##### 配置视频设置 

在视频通话开始前或通话过程中,您可以使用setVideoConfig 方法来调整摄像头采集的配置信息,调整本端发送视频流的分 辨率、码率、帧率: 

###### **TypeScript** 

RCCallPlusClient.getInstance(). ({ 

maxBitrate: 900, 

minBitrate: 200, 

frameRate: RCCallPlusFrameRate.FPS_15, 

resolution: RCCallPlusResolution.SIZE_640_480 

}); 

##### 切换媒体类型 

仅在一对一通话过程中,仅支持视频通话切换到音频通话媒体类型。 

- . 当从视频通话切换为音频通话后,SDK 内部会停止发送本端的视频流,并停止接收远端用户的视频流。这样做只会消耗 音频流量,不再涉及视频传输。 

###### 发起请求 

在一对一通话过程中,主叫方和被叫方用户可以随时切换通话的媒体类型。使用requestChangeMediaType 方法来发起媒 体切换请求。 SDK 内部以异步方式执行该方法,调用该方法后,触发以下回调: 

- . 请求发起方可以通过 API 调用结果的 Promise<{ code: number, transactionId?: string } 来获取调用结果,code 为 RCCallPlusCode.SUCCESS 时表示请求发起成功,transactionId 表示当前操作的唯一标识。 

- 远端用户会通过事件监听器 ICallPlusEventListener 的 onReceivedChangeMediaTypeRequest 回调方法接收到切 换通话媒体请求的事件回调。 

- . 请求成功后,若远端用户在 60 秒内未做出响应,双方均会收到ICallPlusEventListener 的 onReceivedChangeMediaTypeResult 回调。在这个回调中,参数 RCCallPlusMediaTypeChangeResult 若为 RCCallPlusMediaTypeChangeResult.CHANGE_MEDIA_TYPE_TIMEOUT ,则表示响应已超时。 

注意 

当发生网络断开或 IM 连接断开等情况导致请求失败时,该方法会根据 SDK 内部的策略进行重试。如果重试一直失败, 

- 26 - 

最长等待时间约为 47 秒,然后返回失败监听。 

###### **TypeScript** 

###### **/** 先注册结果回调监听 

RCCallPlusClient.getInstance().setCallPlusResultListener({ 

/** 

- 通话中请求切换媒体类型方法结果回调 

- 

- *@param code 方法请求结果 

- *@param callId 通话Id 

- @param transactionId 事务Id 

- @param mediaType 媒体类型 

- */ 

onReceivedChangeMediaTypeResult(info: { 

userId: string; 

transactionId: string; 

mediaType: RCCallPlusMediaType; 

code: RCCallPlusMediaTypeChangeResult; 

- }): void { 

' ' console.log( 收到媒体切换请求的结果 , userId, transactionId, mediaType, code) 

} 

}); 

###### **/** 请求切换为音频通话 

let {code, transactionId} = await 

RCCallPlusClient.getInstance().requestChangeMediaType(RCCallPlusMediaType.AUDIO) 

###### 响应请求 

如果本地用户在通话过程中收到媒体切换请求,使用 replyChangeMediaType 方法来同意或拒绝该请求。 SDK 内部以异步 方式执行该方法,调用该方法后,触发以下回调: 

- . 本地用户通过该方法的返回值来获取异步调用结果。 

- . 如果本地用户同意、拒绝请求,对端用户会会收到 ICallPlusEventListener 的 

- onReceivedChangeMediaTypeResult 回调。应用程序可以通过该回调中的 RCCallPlusMediaTypeChangeResult 参数来查看媒体切换的结果。 

###### 注意 

当发生网络断开或 IM 连接断开等情况导致请求失败时,该方法会根据 SDK 内部的策略进行重试。如果重试一直失败, 最长等待时间约为 47 秒,然后返回失败监听。 

###### **TypeScript** 

- 27 - 

RCCallPlusClient.getInstance().setCallPlusResultListener({ 

/** 

* 收到媒体类型变更请求(仅单聊)

   - *@param userId请求发起人 

   - *@param transactionId事物id ,本次请求和应答的唯一标识 

- *@param mediaType 请求变更的媒体类型 */ 

- onReceivedChangeMediaTypeRequest(userId: string, transactionId: string, mediaType: 

- RCCallPlusMediaType): void { ' ' 

- console.log( 收到媒体切换请求 , userId, transactionId, mediaType) **/** 同意切换 

- let isAgree = true let { code } = await RCCallPlusClient.getInstance().replyChangeMediaType(transactionId, isAgree) 

- }, /** * 媒体类型变更结果(仅单聊) *@param info. userId *@param info.transactionId事物id ,本次请求和应答的唯一标识 *@param info. mediaType 最终的媒体类型 *@param info.code - 升级结果 * - 请求方取消媒体类型变更 * - 应答方拒绝媒体类型切换 * - 服务仲裁允许媒体类型切换 */ 

- onReceivedChangeMediaTypeResult(info: { userId: string; transactionId: string; mediaType: RCCallPlusMediaType; code: RCCallPlusMediaTypeChangeResult; 

- }): void { 

' ' console.log( 收到媒体切换请求的结果 , userId, transactionId, mediaType, code) } }); 

###### 取消请求 

本地用户请求成功后,在远端用户响应之前可以取消请求。应用程序需要从 IRCCallPlusResultListener 的 

onRequestChangeMediaType 回调中获取请求的 transactionId ,在调用 cancelChangeMediaType 方法时传入以取消 指定请求。 

本地用户将通过该方法的返回值来判断接口是否成功,并可以通过 onReceivedChangeMediaTypeResult 回调中的 RCCallPlusMediaTypeChangeResult 参数来查看媒体切换的结果。 

注意 

- 28 - 

当发生网络断开或 IM 连接断开等情况导致请求失败时,该方法会根据 SDK 内部的策略进行重试。如果重试一直失败, 最长等待时间约为 47 秒,然后返回失败监听。 

###### **TypeScript** 

**/** 入参transactionId为onRequestChangeMediaType 回调中transactionId参数 

let {code} = await RCCallPlusClient.getInstance().cancelChangeMediaType(transactionId); 

###### 通话中接听来电 

您可以在通话过程中接听新的来电。由于一次只能进行一个通话,您可以通过以下代码逻辑判断收到的通话是否为第二次来 电。如果要接听第二次来电,只需调用 RCCallPlusClient.getInstance().accept 方法即可;或者,您也可以调用 RCCallPlusClient.getInstance().hangup 方法来挂断该通话。 

注意 

CallPlus SDK 不支持在通话过程中保持和恢复通话。 

###### **TypeScript** 

RCCallPlusClient.getInstance().setCallPlusEventListener({ 

/** 

- 呼入通知 

- 收到呼入时,可选择接听或挂断通话 

- @param session 通话实例 

- *@param extra 透传呼叫方发起呼叫时携带的附加信息 

- */ 

onReceivedCall: (session: RCCallPlusSession, extra?: string | ): void => { 

- const callId = session.getCallId(); 

const syncData = session.getSyncData(); 

const isSecret = session.isSecret(); 

' ' console.log( 呼入通知 , callId, extra, syncData, isSecret); 

let curSession = RCCallPlusClient.getInstance().getCurrentCallSession(); 

- if (curSession.getCallId() !== callId) { 

   - **/** SDK 会在内部主动挂断上一次通话,接新通话。 

let {code} = await RCCallPlusClient.getInstance().accpet(curSession.getCallId()) 

} 

}, 

}); 

- 29 - 

###### 通话中精准计时 

CallPlus 服务端可统一下发通话开始时间,确保各端计时准确、一致,具体支持以下两种方案: 

- . 加入通话成功开始计时:可通过 ICallPlusEventListener 的 onReceivedCallStartTime 方法获取开始时间 

- 收到首帧开始计时:可通过 ICallPlusEventListener 的 onReceivedCallFirstFrameTime 方法获取首个音频或视频帧 到达的时间 

CallPlus 会在通话连接成功后将两个时间戳都回调给 SDK 端(可能会因校准行为导致多次回调),应用程序可以通过计算回 调的时间戳与本地时间之间的差值得到精确的通话时长。 

注意 

为减小误差,CallPlus SDK 会根据用户的网络情况以及本地时间的差异,对通话开始的时间戳进行校准,因此可能存在 同一个通话多次回调该方法的情况。建议您在使用时注意及时更新。 

###### **TypeScript** 

/** 

- 收到通话开始计时 

- @param info.callId通话id 

- @param info.callType 单聊或群聊 

- @param info.callStartTime 通话开始时间 

- */ 

onReceivedCallStartTime(info: { 

- callId: string; 

callType: RCCallPlusType; callStartTime: number; 

- }): void { 

} 

/** 

- 收到首帧时间 

- 收到首帧开始计费 

- *@param callId 通话id 

- *@param callFirstFrameTime 通话首帧到达时间 

- */ 

onReceivedCallFirstFrameTime(callId: string, callFirstFrameTime: number): void { 

- **/** 用户可以在当前回调开启定通话计时 

} 

结束通话 

- 30 - 

在通话过程中,您可以使用 hangup 方法来挂断通话。 

###### **TypeScript** 

- **/** 如果不传入callId ,则是挂断当前通话,如果传入callId 则是挂断指定的通话 

let {code} = await RCCallPlusClient.getInstance().hangup(); 

###### 该方法在 SDK 内部是以异步方式调用的,执行后会触发以下回调: 

- . 本地用户通过 API 调用 hangup 的返回值来获取结果。 

- . 一旦成功挂断通话,所有参与通话的用户都将收到 ICallPlusEventListener 的 onCallEnded 回调,参数 RCCallPlusReason 为通话结束的原因。 

- . 一对一通话结束后,所有参与通话的用户都将收到 ICallPlusEventListener 的 

   - [onReceivedCallPlusSummaryMessage] 回调,返回该通话的通话记录信息。 

###### **TypeScript** 

###### **/** 注册挂断通话API结果回调监听 

RCCallPlusClient.getInstance().setCallPlusResultListener({ 

- /** * @param *@param */ 

- 通话结束(群组通话时,客户端挂断不代表通话结束) 

- @param session 通话实例 

- *@param reason 通话结束原因 

- onCallEnded(session: RCCallPlusSession, reason: RCCallPlusReason): void { ' ' 

- console.log( 通话结束 , reason); 

- } , /** * 收到通话结束的消息记录,可用于在IM 聊天界面插入通话结束消息 * 仅单聊可收到 * 触发时机: * 1.单聊在线通话结束后 * 2.离线时收到单聊呼叫,通话结束后,重新连接IM 在线时 *@param message 通话记录的消息体 */ 

onReceivedCallPlusSummaryMessage(message: Message): void { 

**/** 结合IM 插入本地消息,来是现实通话记录 } }) 

###### 管理通话记录 

- 31 - 

CallPlus 提供服务端通话记录管理能力,包括查询用户通话记录列表、删除通话记录等功能。一则通话记录对应一个 [RCCallPlusCallRecord] 对象,其中包含通话 ID、参与用户 ID、通话开始与结束的时间戳、通话时长等信息。 

###### 注意 

CallPlus SDK 通话记录区分两种 

   - 一种是 onReceivedCallRecord 通话结束后回调,由服务端记录。 

- . 还有一种是 onReceivedCallPlusSummaryMessage 通话结束后回调,本地生成对应的自定义消息,方便客户 配合使用IM 插入通话记录。 

##### 通话结束后获取通话记录 

通话结束(或拒接来电)后可以通过 ICallPlusEventListener 的回调方法 onReceivedCallRecord 获取到服务器下发的通 话记录。 

##### 检索服务端通话记录 

应用程序可以使用 [getCallRecords] 方法向服务端发起请求,获取当前用户的通话历史记录。参数说明 order 参数,支持 倒序查询通话记录。例如,分页获取最近的通话记录。首次可以将 syncTime 设置为 -1。如果需要继续查询,可以将返回的 syncTime 作为下次查询的 syncTime 值。 

###### **TypeScript** 

private _getCallRecords() { 

let syncTime = -1 **/** 获取通话记录的同步时间首次获取可传-1 ,倒序时,返回最新的通话记录,正序时,返回最早的 通话记录 

let count = 20 **/** 获取通话记录的数量 

let order: 0 | 1 = 1 **/** 获取通话记录的排序方式1 :正序,0 :倒序 

RCCallPlusClient.getInstance().getCallRecords(syncTime, count, order).then((res) => { 

- if (res.code === RCCallPlusCode.SUCCESS) { 

' ' console.log( 获取通话记录成功 , res.result); 

- } else { 

' ' console.log( 获取通话记录失败 , res.code); 

} 

}); 

} 

##### 删除通话记录 

- CallPlus SDK 提供两种删除通话记录的接口。deleteCallRecordsFromServer 和 deleteAllCallRecordsFromServer ,前 一个是根据 callId 数组批量从服务端删除属于当前用户的通话记录,后一个是全量删除。 

###### **TypeScript** 

- 32 - 

###### **/** 删除通话记录 

let callIds = ['callId1', 'callId2']; 

RCCallPlusClient.getInstance().deleteCallRecordsFromServer(callIds).then((res) => { if (res.code === RCCallPlusCode.SUCCESS) { 

' ' console.log( 删除通话记录成功 ); 

} else { 

' ' console.log( 删除通话记录失败 , res.code); 

} 

}); 

###### **/** 删除所有通话记录 

RCCallPlusClient.getInstance().deleteAllCallRecordsFromServer().then((res) => { 

if (res.code === RCCallPlusCode.SUCCESS) { 

' ' console.log( 删除所有通话记录成功 ); 

} else { 

' ' console.log( 删除所有通话记录失败 , res.code); 

} 

}); 

###### 管理通话质量 

在通话过程中,可使用 setCallPlusEventListener 注册 ICallPlusEventListener ,接收或发送丢包率等相关的信息。 

###### **TypeScript** 

- 33 - 

RCCallPlusClient.getInstance().setCallPlusEventListener({ 

- /** * 上行丢包率及延迟信息回调,每秒回调一次 

- *@parampacketLostRate 丢包率,0-100 

- *@param delay 发送端的网络延迟,单位毫秒 */ 

onSendPacketLoss(packetLostRate: number, delay: number): void { 

- } /** * 下行丢包率及延迟信息回调,每秒回调一次 *@param data key: userId, value: 接收丢包统计数据 * @param @param data[userId].packetLostRate *@param data[userId]. bitRate 码率大小,单位是kbps */ 

- @param @param data[userId].packetLostRate 丢包率:取值范围是0-100 

onReceivePacketLoss(data: { 

   - [userId: string]: RCCallPlusPacketLossStats; 

- }): void { 

} }); 

###### 音视频首帧回调 

可通过 ICallPlusEventListener 获取音频、视频首帧通知。 

###### **TypeScript** 

RCCallPlusClient.getInstance().setCallPlusEventListener({ 

/** 

- 音频或视频首帧可渲染 

- *@param userId 用户id 

- @param mediaType 媒体类型 

- */ 

onFirstFrame(userId: string, mediaType: RCCallPlusMediaType): void { ' ' console.log( 收到首帧 , userId, mediaType); 

} 

}); 

- 34 - 

### 多人通话 

###### 本文介绍了多人通话的主要功能,包括如何发起多人通话、单人通话转为多人通话等。 

注意 

因为 CallPlus for HarmonyOS 多人通话与一对一通话流程相似,本文仅介绍多人通话与一对一通话有差异的使用方 法。我们建议您先按照一对一通话实现完整的通话流程。 

###### 发起多人通话 

startCallWithParams 方法,支持在发起呼叫时通过配置推送属性自定义远程推送标题等属性。支持携带自定义数据。如不 需要配置推送属性,可选择不传。 

如需直接发起多人通话,请在 startCallWithParams 方法中传入多个远端用户 ID ,并设置通话类型为 

RCCallPlusType.MULTI。媒体类型可为视频或音频。您可以创建最多 16 名视频参与者的多人通话,或最多 32 名音频参与 者的多人通话。 

该方法内部为异步执行,结果在方法返回值中获取。被叫用户会通过 ICallPlusEventListener 协议的 onReceivedCall 方法 收到来电通知。 

###### **TypeScript** 

private _startMultiCall() { 

RCCallPlusClient.getInstance().startCallWithParams({ 

userIds: ['userId1', 'userId2'], 

type: RCCallPlusType.MULTI, 

mediaType: RCCallPlusMediaType.AUDIO, 

extra: 'extra', 

syncData: 'syncData' 

}).then((result) => { 

if (result.code === RCCallPlusCode.SUCCESS) { 

' ' console.log( 发起通话成功 ); } else { ' ' console.log( 发起通话失败 , result.code) } }); 

} 

接听多人通话 

- 35 - 

注意 

被叫用户必须先设置 ICallPlusEventListener 代理,并实现 didReceivedCall 方法。 . startCallWithParams 方法和 didReceivedCall: 回调参数包含 extra 字段,用户可以用来传递自定义数据。 

被叫用户收到来电通知后,可以选择接听或拒绝来电。应用程序可以通过 RCCallPlusSession 的 getCallId() 方法获取通话 ID ,可以通过 getCallType() 方法查询通话类型是否为多人通话。 

. 接听来电 

###### **TypeScript** 

RCCallPlusClient.getInstance().accept('callId').then((result) => { if (result.code === RCCallPlusCode.SUCCESS) { 

' ' console.log( 接听成功 ); } else { ' ' console.log( 接听失败 , result.code); } }); 

挂断来电 

###### **TypeScript** 

RCCallPlusClient.getInstance().hangup('callId').then((result) => { if (result.code === RCCallPlusCode.SUCCESS) { 

' ' console.log( 挂断成功 ); } else { ' ' console.log( 挂断失败 , result.code); } }); 

###### 邀请他人加入通话 

您可以向某些用户发送邀请来让用户进入多人通话。被邀请者可以接受或拒绝您的邀请。 

注意 

CallPlus 暂不支持取消邀请。 

##### 邀请用户 

- 36 - 

首先,本地用户需要已进入一个多人通话或一对一通话。要邀请其他用户,使用 invite 方法,并传入用户 ID。此方法是异步 调用的可以通过该方法的返回值来获取调用结果。如果受邀用户正在呼叫他人的过程中,仍会收到邀请,受邀用户可以选择接 听或者挂断该通话。邀请方会在返回值结果的 busylineUsers 参数中返回正在通话中的用户列表。 

###### **TypeScript** 

###### **/** 邀请用户加入通话,并携带推送配置和自定义数据 

RCCallPlusClient.getInstance().invite(['userId1', 'userId2']).then((result) => { if (result.code === RCCallPlusCode.SUCCESS) { 

' ' console.log( 邀请成功 ); } else { ' ' console.log( 邀请失败 , result.code); } }); 

成功发送邀请后,受邀用户的设备上将通过 ICallPlusEventListener 代理的 didReceivedCall 方法收到来电通知,通知他们 您已邀请他们加入通话。 

##### 获取邀请详情 

在通话中发起邀请后,被邀请者、正在通话中的用户、已退出多人通话的用户都将通过 ICallPlusEventListener 协议的 onRemoteUserInvited 方法收到通知,其中携带通话 ID、发起邀请者用户 ID 与所有受邀用户的 ID。 

###### **TypeScript** 

/** 

- 收到远端人员被邀请加入通话通知 

- @param inviteeUserList被邀请人员列表 

- @param inviterUserId 邀请人员ID 

- @param callId 通话ID 

- */ 

onRemoteUserInvited: (inviteeUserList: string[], inviterUserId: string, callId: string): void => { ' ' console.log( 收到远端人员被邀请加入通话通知 , inviteeUserList, inviterUserId, callId); 

} 

##### 接受或拒绝邀请 

当被邀请的用户接受或拒绝邀请时,邀请他们的用户将会收到通知。您可以添加 UI 更新,让邀请者知道他们邀请的用户是接 受还是拒绝邀请。 

. 被邀请者接受邀请 

###### **TypeScript** 

- 37 - 

###### **/** 接听 

RCCallPlusClient.getInstance().accept(callId).then((result) => { if (result.code === RCCallPlusCode.SUCCESS) { ' ' console.log( 接听成功 ); } else { ' ' console.log( 接听失败 , result.code); } }) **/** 也可以使用joinMultiCall加入通话 RCCallPlusClient.getInstance().joinMultiCall(callId).then((result) => { if (result.code === RCCallPlusCode.SUCCESS) { ' ' console.log( 加入多人通话成功 ); } else { ' ' console.log( 加入多人通话失败 , result.code); } }); 

###### . 被邀请者拒绝邀请 

###### **TypeScript** 

RCCallPlusClient.getInstance().hangup('callId').then((result) => { if (result.code === RCCallPlusCode.SUCCESS) { ' ' console.log( 挂断成功 ); } else { ' ' console.log( 挂断失败 , result.code); } }); 

接听方法、加入通话方法与挂断方法在 SDK 内部为异步执行,API 会通过 Promise 返回调用结果 RCCallPlusCode ,为 0 表示成功。 

如果原通话是一对一通话,受邀请者加入后,通话类型将变更为 RCCallPlusType.MULTI ,通话参与者(包括已退出的用户) 都会通过 onCallTypeChanged 方法收到通知。 

###### 结束通话 

挂断与拒绝接听动作均使用 hangup() 方法。方法结束当前正在进行中的通话,或者传入 callId 方法结束指定的通话。应用 程序可通过返回值确定 API 的执行结果。 

###### **TypeScript** 

- 38 - 

- **/** callId 是可选参数,不传是挂断当前通话,传入callId 指定挂断 

RCCallPlusClient.getInstance().hangup('callId').then((result) => { 

if (result.code === RCCallPlusCode.SUCCESS) { 

' ' console.log( 挂断成功 ); } else { ' ' console.log( 挂断失败 , result.code); } }); 

##### 获取未结束的多人通话 

用户可能拒绝一个多人通话邀请,或退出一个多人通话,只要该多人通话未结束,用户就可以再次加入。 

用户可以使用 getAvailableCallRecordsFromServer 方法向服务端查询本地用户所有曾经参与过(或曾经被邀请过)、且 仍在进行中的多人通话。该方法在 SDK 内部为异步执行,可通过 Promise 返回值获取调用结果。 

###### **TypeScript** 

RCCallPlusClient.getInstance().getAvailableCallRecordsFromServer().then((res) => { 

if (res.code === RCCallPlusCode.SUCCESS) { 

' ' console.log( 获取通话记录成功 , res.records); 

} else { ' ' console.log( 获取通话记录失败 , res.code); } }); 

获取未结束通话的记录后,通过 IRCCallPlusCallRecord 中 callId 属性获取通话 ID ,使用 joinMultiCall 方法传入通话 ID 可加入正在进行中的多人通话。 

### 配置推送属性 

CallPlus 支持对呼叫生成的信令消息的推送行为进行个性化配置。例如: 

- . 自定义推送标题 

- . 自定义通知栏图标 

- . 支持多语言推送 

- . 其他 APNs 或 Android 推送通道支持的个性化配置 

请在发起通话前和邀请通话前提供 配置。 

- 39 - 

###### 推送属性说明 

###### 提供以下参数: 

|参数|类型|说明|
|---|---|---|
|disablePushTitle|BOOL|是否屏蔽通知标题,此属性只针目标用户为iOS 平台时有效,Android 第三方 推送平台的通知标题为必填项,所以暂不支持。|
|pushTitle|NSString|推送标题,此处指定的推送标题优先级最高。如不设置,则使用CallPlus 服务 端默认标题。|
|templateId|NSString|推送模板ID ,设置后根据目标用户通过IM SDK 中的|
|||setPushLauguageCode 设置的语言环境,匹配模板中设置的语言内容进行推 送,未匹配成功时使用默认内容进行推送。模板内容在“控制台-自定义推送文 案”中进行设置,具体操作请参见配置和使用自定义多语言推送模板。|
|iOSConfg|IiOSPushConfg|iOS 平台相关配置。支持threadId、apnsCollapseId、richMediaUri ,用法 详见API 文档。|
|androidConfg|IAndroidPushConfg|Android 平台相关配置。支持针对小米、华为、荣耀、OPPO、vivo、魅族、 FCM 推送渠道配置消息分类、渠道ID、通知栏图片等。用法详见API 文档。|

### 自定义加密 

在实时音视频互动中,开发者可选择对媒体流进行加密,从而保障用户的数据安全。融云提供两套加密方案: 

1. 开发者对媒体数据的自定义加密。即加解密完全由开发者实现,融云服务只对数据做转发,适用于对安全性有特殊要求的 客户。此类加密方式,服务端无法做合流处理,所以不适用于直播。 

2. 使用自定义加密后,无法使用部分 RTC 服务端功能,包括:云端录制、云端截图、内容审核、云播放器。 

#### Q 提示 

- . 若使用自定义加密,需要确保发送端和接收端的加解密算法一致,否则会无法正常通话。 

- . 自定义加密,可分别针对音频或视频的原始数据执行,音频和视频的加密算法可以独立设置,或对其中之一进行 设置。 

- . 由于数据量大,考虑性能原因,自定义的加密算法需要在 C++ 层实现。注意 

- 无论何种加密方式,都会对客户端、服务器造成额外的资源消耗,在低性能设备上可能会影响体验。 

自定义加密 

- 40 - 

鸿蒙音视频通话想要实现自定义加解密,需要实现 C++ 层提供的加解密协议方法,通过构建加密解密实例,在开始呼叫前调 用 setEncryptor 和 setDecryptor 方法将指针传入 CallPlus 即可实现音视频数据加解密。 

##### 步骤 **1** 创建加解密模块 

打开在项目里面创建一个 C++ 模块。 

新增命名 rtc_custom_crypto_interface.h 的 C++ 头文件,增加加解密需要实现的协议方法声明。 

- 41 - 

具体增加 RTCCustomEncryptorInterface 加密协议和 RTCCustomDecryptorInterface 解密协议,代码如下。 

###### **cpp** 

#pragma once 

#include <cstdint> 

#include <cstddef> 

/** 

- 开发者实现该接口实现自定义加密,随RTCLib 提供 

- **/ 

class RTCCustomEncryptorInterface { public: 

virtual ~RTCCustomEncryptorInterface() = default; 

- /** 

- 开发者自定义加密方法 

- *@param payload_ data 加密前的数据起始地址 

- *@param payload_ size 加密前的数据大小 

- @param encrypted_ frame 加密后的数据起始地址,融云SDK已申请内存,开发者无需重新申请 

- *@param bytes_ written 加密后数据的大小 

- *@param media_ stream_ id当前音频或视频流的名称 

- *@param 媒体类型,0为"audio " 1为"video " 

- @return 0 :成功,非0 :失败 

- **/ 

virtual int Encrypt(const uint8_t* payload_data, size_t payload_size, 

uint8_t* encrypted_frame, size_t* bytes_written, 

const char* media_stream_id, int media_type) = 0; 

- 42 - 

/** 

- 计算加密后数据的长度 

- *@param frame_ size 明文大小 

- *@param media_ stream_ id当前音频或视频流的名称 

- *@param media_ type 媒体类型,0为"audio "1为"video " 

- *@return size_ t密文长度 

- **/ 

virtual size_t GetMaxCiphertextByteSize(size_t frame_size, const char* media_stream_id, int media_type) = 0; 

}; 

/** 

- 开发者实现该接口实现自定义解密,随RTCLib 提供 

- **/ 

class RTCCustomDecryptorInterface { 

public: 

virtual ~RTCCustomDecryptorInterface() = default; 

- /** 

- 开发者定义解密方法 

- @param encrypted_ frame 解密前的数据起始地址 

- *@param encrypted_ frame_ size 解密前的数据大小 

- @param frame 解密后的数据起始地址,融云SDK已申请内存,开发者无需重新申请 

- *@param bytes_ written 解密后数据的大小 

- *@param media_ stream_ id当前音频或视频流的名称 

- *@param media_ type 媒体类型,0为"audio "1为"video " 

- @return 0 :成功,非0 :失败 

- **/ 

virtual int Decrypt(const uint8_t* encrypted_frame, size_t encrypted_frame_size, 

uint8_t* frame, size_t* bytes_written, const char* media_stream_id, 

int media_type) = 0; 

/** 

- 计算解密后数据的长度 

- *@param frame_ size 密文大小 

- *@param media_ stream_ id当前音频或视频流的名称 

- *@param media_ type 媒体类型,0为"audio "1为"video " 

- *@return size_ t明文长度 

- **/ 

virtual size_t GetMaxPlaintextByteSize(size_t frame_size, const char* media_stream_id, int media_type) = 0; 

}; 

##### 步骤 **2** 实现加密方法 

- 43 - 

新增加密 NapiEncryptor C++ 类,在 .h 引入 rtc_custom_crypto_interface.h 实现 RTCCustomEncryptorInterface 的加密方法,代码如下。 

###### **cpp** 

#pragma once 

#include <napi/native_api.h> 

#include "rtc_custom_crypto_interface.h" 

class NapiEncryptor : public RTCCustomEncryptorInterface { public: 

NapiEncryptor(); ~NapiEncryptor(); 

static napi_value Init(napi_env env, napi_value exports); 

static napi_value New(napi_env env, napi_callback_info info); static void Destructor(napi_env env, void* nativeObject, void* finalize_hint); 

public: 

static napi_value GetEncryptor(napi_env env, napi_callback_info info); 

int Encrypt(const uint8_t* payload_data, size_t payload_size, 

uint8_t* encrypted_frame, size_t* bytes_written, const char* media_stream_id, int media_type) override; 

size_t GetMaxCiphertextByteSize(size_t frame_size, const char* media_stream_id, int media_type) override; 

private: 

napi_env env_; napi_ref wrapper_; }; 

在 NapiEncryptor.cpp 实现音视频流加密方法,以下示例代码中采用对数据的异或方式加密。 

###### **cpp** 

#include "napi/native_api.h" 

#include "NapiEncryptor.h" static thread_local napi_ref g_ref = nullptr; 

NapiEncryptor::NapiEncryptor() : env_(nullptr), wrapper_(nullptr) { 

} 

NapiEncryptor::~NapiEncryptor() { 

- 44 - 

NapiEncryptor:: NapiEncryptor() { 

napi_delete_reference(env_, wrapper_); 

} 

napi_value NapiEncryptor::Init(napi_env env, napi_value exports) { 

napi_property_descriptor desc[] = { 

{"encryptor", nullptr, nullptr, NapiEncryptor::GetEncryptor, nullptr, nullptr, napi_default, nullptr} }; 

int desc_count = sizeof(desc) / sizeof(desc[0]); napi_value cons = nullptr; 

if ( (env, "NapiEncryptor", NAPI_AUTO_LENGTH, New, nullptr, 

desc_count, desc, &cons) != napi_ok) { 

return nullptr; 

} 

if (napi_create_reference(env, cons, 1, &g_ref) != napi_ok) { 

return nullptr; 

} 

if (napi_set_named_property(env, exports, "NapiEncryptor", cons) != napi_ok) { 

return nullptr; 

} 

return exports; 

} 

napi_value NapiEncryptor::New(napi_env env, napi_callback_info info) { 

napi_value newTarget = nullptr; 

napi_get_new_target(env, info, &newTarget); 

if (newTarget != nullptr) { 

- napi_value jsThis = nullptr; 

- if (napi_get_cb_info(env, info, nullptr, nullptr, &jsThis, nullptr) == napi_ok && jsThis != nullptr) { NapiEncryptor* obj = new NapiEncryptor(); 

   - obj->env_ = env; 

   - **/** 通过napi_ wrap将ArkTS对象jsThis与C++对象obj绑定 

napi_status status = napi_wrap(env, jsThis, reinterpret_cast<void*>(obj), 

NapiEncryptor::Destructor, nullptr, nullptr); 

} 

return jsThis; 

} else { 

- **/** 使用`MyObject(...) `调用方式 

napi_status status; 

napi_value cons; 

status = napi_get_reference_value(env, g_ref, &cons); 

if (status != napi_ok) { 

return nullptr; 

} 

napi value jsObj = nullptr; 

- 45 - 

pi_ l js j llptr; status = napi_new_instance(env, cons, 0, nullptr, &jsObj); 

return jsObj; 

} 

} 

void NapiEncryptor::Destructor(napi_env env, void* nativeObject, void* finalize_hint) { reinterpret_cast<NapiEncryptor*>(nativeObject)->~NapiEncryptor(); 

} 

napi_value NapiEncryptor::GetEncryptor(napi_env env, napi_callback_info info) { napi_value result = nullptr; 

(env, &result); 

napi_value jsThis; 

napi_status status; 

status = napi_get_cb_info(env, info, nullptr, nullptr, &jsThis, nullptr); if (status != napi_ok || !jsThis) { 

return nullptr; 

} 

NapiEncryptor *napiEncryptor; 

status = napi_unwrap(env, jsThis, reinterpret_cast<void **>(&napiEncryptor)); if (status != napi_ok) { 

return nullptr; 

} 

napi_value jsObj; 

RTCCustomEncryptorInterface* encryptor = static_cast<RTCCustomEncryptorInterface 

###### *>(napiEncryptor); 

int64_t encryptorInt64 = reinterpret_cast<int64_t>(encryptor); 

status = napi_create_int64(env, encryptorInt64, &jsObj); 

return jsObj; 

} 

int NapiEncryptor::Encrypt(const uint8_t* payload_data, size_t payload_size, 

uint8_t* encrypted_frame, size_t* bytes_written, 

const char* media_stream_id, int media_type) { 

uint8_t fake_key_ = 0x88; 

if (media_type == 1) { 

for (size_t i = 0; i < payload_size; i++) { 

encrypted_frame[i] = payload_data[i] ^ fake_key_; 

} 

*bytes_written = payload_size; 

} else { 

encrypted_frame[0] = 0; encrypted_frame[1] = 1; 

encrypted frame[2] = 2; 

- 46 - 

n rypt _fr m [2] 2; encrypted_frame[3] = 3; encrypted_frame[4] = 3; encrypted_frame[5] = 2; encrypted_frame[6] = 1; encrypted_frame[7] = 0; for (size_t i = 0; i < payload_size; i++) { encrypted_frame[i + 8] = payload_data[i] ^ fake_key_; } *bytes_written = payload_size + 8; } return 0; } 

size_t NapiEncryptor::GetMaxCiphertextByteSize(size_t frame_size, const char* media_stream_id, int media_type) { if (media_type == 1) { return frame_size; } return frame_size + 8; } 

##### 步骤 **3** :实现自定义解密 

新增解密 NapiDecryptor C++ 类,实现 RTCCustomDecryptorInterface 解密方法。 

###### **cpp** 

- 47 - 

#include "rtc_custom_crypto_interface.h" 

#include <js_native_api_types.h> 

class NapiDecryptor : public RTCCustomDecryptorInterface { public: 

NapiDecryptor(); ~NapiDecryptor(); 

static napi_value Init(napi_env env, napi_value exports); 

static napi_value New(napi_env env, napi_callback_info info); static void Destructor(napi_env env, void* nativeObject, void* finalize_hint); 

public: 

static napi_value GetDecryptor(napi_env env, napi_callback_info info); 

int Decrypt(const uint8_t* encrypted_frame, size_t encrypted_frame_size, uint8_t* frame, size_t* bytes_written, const char* media_stream_id, int media_type) override; 

size_t GetMaxPlaintextByteSize(size_t frame_size, const char* media_stream_id, int media_type) override; 

private: 

napi_env env_; napi_ref wrapper_; }; 

在 NapiDecryptor.cpp 实现自定义解密方法,和上述加密方式一致也是采用对数据的异或方式。 

###### **cpp** 

#include "NapiDecryptor.h" 

#include <js_native_api.h> 

static thread_local napi_ref g_ref = nullptr; 

NapiDecryptor::NapiDecryptor() : env_(nullptr), wrapper_(nullptr) { 

} 

NapiDecryptor::~NapiDecryptor() { 

napi_delete_reference(env_, wrapper_); 

} 

napi_value NapiDecryptor::Init(napi_env env, napi_value exports) { napi property descriptor desc[] = { 

- 48 - 

pi_pr p rty_ script r sc[] { 

{"decryptor", nullptr, nullptr, NapiDecryptor::GetDecryptor, nullptr, nullptr, napi_default, nullptr} 

}; 

int desc_count = sizeof(desc) / sizeof(desc[0]); 

napi_value cons = nullptr; 

if ( (env, "NapiDecryptor", NAPI_AUTO_LENGTH, New, nullptr, 

desc_count, desc, &cons) != napi_ok) { 

return nullptr; 

} 

if (napi_create_reference(env, cons, 1, &g_ref) != napi_ok) { 

return nullptr; 

} 

if (napi_set_named_property(env, exports, "NapiDecryptor", cons) != napi_ok) { 

return nullptr; 

} 

return exports; 

} 

napi_value NapiDecryptor::New(napi_env env, napi_callback_info info) { 

napi_value newTarget = nullptr; 

napi_get_new_target(env, info, &newTarget); 

if (newTarget != nullptr) { 

napi_value jsThis = nullptr; 

if (napi_get_cb_info(env, info, nullptr, nullptr, &jsThis, nullptr) == napi_ok && jsThis != nullptr) { NapiDecryptor* obj = new NapiDecryptor(); 

obj->env_ = env; 

**/** 通过napi_ wrap将ArkTS对象jsThis与C++对象obj绑定 

napi_status status = napi_wrap(env, jsThis, reinterpret_cast<void*>(obj), NapiDecryptor::Destructor, nullptr, nullptr); 

} 

return jsThis; 

} 

else { 

**/** 使用`MyObject(...) `调用方式 

napi_status status; napi_value cons; 

status = napi_get_reference_value(env, g_ref, &cons); if (status != napi_ok) { return nullptr; 

} napi_value jsObj = nullptr; 

status = napi_new_instance(env, cons, 0, nullptr, &jsObj); 

return jsObj; 

} 

} 

- 49 - 

###### void NapiDecryptor::Destructor(napi_env env, void* nativeObject, void* finalize_hint) { reinterpret_cast<NapiDecryptor*>(nativeObject)->~NapiDecryptor(); 

} 

napi_value NapiDecryptor::GetDecryptor(napi_env env, napi_callback_info info) { napi_value result = nullptr; 

(env, &result); 

napi_value jsThis; napi_status status; 

status = napi_get_cb_info(env, info, nullptr, nullptr, &jsThis, nullptr); if (status != napi_ok || !jsThis) { 

return nullptr; 

} 

NapiDecryptor *napiDecryptor; 

status = napi_unwrap(env, jsThis, reinterpret_cast<void **>(&napiDecryptor)); if (status != napi_ok) { 

return nullptr; 

} 

napi_value jsObj; 

RTCCustomDecryptorInterface* decryptor = static_cast<RTCCustomDecryptorInterface 

###### *>(napiDecryptor); 

int64_t decryptorInt64 = reinterpret_cast<int64_t>(decryptor); 

status = napi_create_int64(env, decryptorInt64, &jsObj); 

return jsObj; 

} 

int NapiDecryptor::Decrypt(const uint8_t* encrypted_frame, size_t encrypted_frame_size, uint8_t* frame, size_t* bytes_written, const char* media_stream_id, 

int media_type) { 

uint8_t fake_key_ = 0x88; 

if (media_type == 1) { 

for (size_t i = 0; i < encrypted_frame_size; i++) { 

frame[i] = encrypted_frame[i] ^ fake_key_; 

} 

   - *bytes_written = encrypted_frame_size; 

- } else { 

if (encrypted_frame_size < 8) { 

return 0; 

} 

for (size_t i = 0; i < encrypted_frame_size; i++) { 

frame[i] = encrypted_frame[i + 8] ^ fake_key_; 

- } 

- *bytes_written = encrypted_frame_size - 8; 

} 

- 50 - 

} 

return 0; 

} 

size_t NapiDecryptor::GetMaxPlaintextByteSize(size_t frame_size, const char* media_stream_id, int media_type) { 

if (media_type == 1) { 

return frame_size; 

} else { 

return frame_size < 8 ?: frame_size - 8; } 

} 

##### 步骤 **4** :配置加解密库 

修改 CMakeLists.txt 文件,将 NapiEncryptor.cpp NapiDecryptor.cpp 添加 add_library 方法里,如下图所示: 

在 index.d.ts 中增加 napi 方法导出,方便后续在项目中使用。 

###### **TypeScript** 

export class NapiEncryptor { 

public get encryptor(): number; 

} 

export class NapiDecryptor { public get decryptor(): number; } 

- 51 - 

在 cpp 文件下找到 oh-package.json5 修改 .so 库名, 

###### **JSON** 

{ 

"name": "RTCCustomCrypto.so", "types": "./index.d.ts", "version": "1.0.0", "description" : "Please describe the basic information." } 

###### 对应在项目中修改 dependencies 保持库名和路径统一,修改如下: 

###### **JSON** 

{ "name": "entry", "version": "1.0.0", "description" : "Please describe the basic information.", "main" : "", "author": "", "license" : "", "dependencies": { "RTCCustomCrypto.so" : "file:./src/main/cpp/types/RTCCustomCrypto" } } 

#### Q 提示 

注意修改库名步骤非必须,如需修改则要保证定义的库名和外部引用一致。 

##### 步骤 **5** :在 **CallPlus** 中使用加解密 

引入前述步骤中创建的加解密类,在发起和接听前通过 RCCallPlusClient 的接口设置,示例代码如下: 

###### **TypeScript** 

- 52 - 

import {NapiDecryptor, NapiEncryptor} from "RTCCustomCrypto.so"; 

private _statCall(params: IRCCallPlusStartParams): void { 

let callPlusClient: RCCallPlusClient = RCCallPlusClient.getInstance(); 

###### **/** 设置加解密 

callPlusClient.setDecryptor(this.decryptor.decryptor) 

callPlusClient.setEncryptor(this.encryptor.encryptor); 

###### **/** 开始通话 

callPlusClient.startCallWithParams(params) 

.then((res) => { 

if(res.code === RCCallPlusCode.SUCCESS){ 

let callId = res.callId 

let busyUsers = res.busyUsers 

console.log(`startCallWithParams success, callId: ${callId}, busyUsers: ` ${JSON.stringify(busyUsers)} ) 

} 

else{ 

` console.log(`startCallWithParams failed, code: ${res.code} ) } 

}) 

} 

###### private _acceptCall(callId: string) :void { 

let callPlusClient: RCCallPlusClient = RCCallPlusClient.getInstance(); 

###### **/** 设置加解密 

callPlusClient.setDecryptor(this.decryptor.decryptor) callPlusClient.setEncryptor(this.encryptor.encryptor); 

###### **/** 接听 

callPlusClient.accept(callId).then((res) => { if(res.code === RCCallPlusCode.SUCCESS){ 

console.log('accept success') } else { ` console.log(`accept failed, code: ${res.code} ) } }) 

} 

- 53 - 

### 状态码 

###### 0 

SUCCESS 

调用函数时,方法入参的参数错误。 

排查建议:请通过API DOC检查接口参数类型是否正确。 

###### 80001 

PARAM_ERROR 参数错误 

排查建议:请检查当前方法的入参是否符合接口要求。 

80002 SESSION_EXIST 存在未结束的 session 

排查建议:请检查当前是否已经在通话中。 

###### 80003 

NOT_IN_CALL 

未加入通话 

排查建议:当前通话不存在,需要建立在通话基础上方法需要注意前置条件。 

###### 80004 

MEDIATYPE_INVALID 

媒体类型被禁止 

排查建议:切换媒体类型时,存在不合理的类型切换,当前仅支持音视频切换到音频。 

###### 80005 

NOT_VIDEO_CALL 当前不是视频通话 

排查建议:切换媒体类型时,存在不合理的类型切换,当前仅支持音视频切换到音频。 

###### 80004 

MEDIATYPE_INVALID 不允许切换通话媒体类型。 排查建议: 

不允许切换通话媒体类型。 

1. 请求切换的通话媒体类型与当前通话的媒体类型一致导致。 

2. 可通过 session.getMediaType() 确认当前的媒体类型。 

- 54 - 

80006 

RTC_SERVICE_UNAVAILA BLE 

开通的音视频服务没有及时生效或音视频服务已关闭。 

排查建议: 

1. 请检查融云控制台 > 应用配置 > 音视频服务 > 实时音视频服务是否已开通。 

2. 如果服务已开通,且时间间隔在 15 分钟以上,可以清空浏览器缓存( localstorage)刷新页面重试。 

###### 80007 

USER_LIST_INVAILD 

调用函数时,传入的用户列表为空错误。 

排查建议:参数为 Array 类型,并且长度大于 0。 

###### 80008 

CALL_ID_INVALID 

调用函数时,传入的通话 Id 为空错误。 

排查建议:参数为不为空,并且长度大于 0。 

###### 80009 

TRANSACTION_ID_INVALI 

D 

调用函数时,传入的事务 Id 为空错误。 

排查建议:参数为不为空,并且长度大于 0。 

###### 80010 

USER_ID_INVALID 

调用函数时,传入的用户 Id 为空错误。 

排查建议:参数为不为空,并且长度大于 0。 

###### 80011 

SINGLE_CALL_NOT_SUPP 

ORT_MULTI_PERSON 

发起单人呼叫时,人员列表中只能有一个人。 

排查建议:请检查发起呼叫传入的人员列表长度是否为 1。 

###### 80012 

SIGNAL_DISCONNECTED 

im 未连接。 

排查建议: 

1. 用户可调用 getConnectionStatus() 来确认当前连接状态。 

2. CallPlus SDK 异步接口需等 connect 连接 成功后才能调用。 

- 55 - 

80100 

CAMERA_CLOSED 

未打开摄像头。 

排查建议: 

1. 请检查当前设备的麦克风和摄像头是否正常。 

2. 请检查浏览器是否有权限获取麦克风和摄像头。 

3. 可通过线上地址检测媒体设备是否正常获取。 

4. 业务层按需执行 startCamera。 

###### 80101 

###### MICROPHONE_CLOSED 

麦克风未打开。 

排查建议: 

1. 请检查当前设备的麦克风和摄像头是否正常。 

2. 请检查浏览器是否有权限获取麦克风和摄像头。 

3. 可通过线上地址检测媒体设备是否正常获取。 

4. 业务层按需执行 startMicrophone。 

###### 80102 

MEDIA_RESOURCE_INVA 

LIED 

无媒体资源。 

排查建议: 

1. 播放指定人员的音视频媒体,播放指定单个用户的视频前,请确保已经调用setVideoView 方法为其设置视频视图。 

2. 如果播放本端自己失败,可通过线上地址检测媒体设备是否正常获取。 

3. 如果播放远端人员失败,可比对onUserMediaAvailable 监听返回的远端资源是否存在。 

###### 80103 

NOT_INSTALL_RTC_PLU 

G IN 

未 install RTC 插件。 

排查建议: 

1. IM 初始化后,需要先初始化 RTCLib ,并且使用 rtcClient 变量存储 RTCLib 实例。 

2. CallPlus 初始化时传入 rtcClient ,详情请参阅快速上手。 

- 57 -
