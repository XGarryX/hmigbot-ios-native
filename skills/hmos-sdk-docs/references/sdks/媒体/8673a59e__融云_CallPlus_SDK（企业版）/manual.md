# 融云音视频(RTC) 客户端 **SDK** 快速入门 HarmonyOS CallPlus 

## 实现首次通话 

适用于 HarmonyOS 的 CallPlus 可在您的应用程序中为用户之间的一对一和多人通信提供语音和视频通话能力。 

CallPlus 支持一对一通话 和 多人通话。按照下面的指南使用 ArkTS / TypeScript 从头开始实现一对一通话和多人通话。 

##### 环境要求 

适用于 HarmonyOS 的 CallPlus SDK 的最低要求如下。 

- . DevEco Studio NEXT Release(5.0.3.900) 及以上。 

- . HarmonyOS SDK API 12 及以上。 

- . 手机系统版本号:NEXT.0.0.31 

##### 前置条件 

- . 注册开发者账号。注册成功后,控制台会默认自动创建您的首个应用,默认生成开发环境下的 App Key ,使用国内数 据中心。 

获取开发环境的应用AppApp Key。如不使用默认应用,请参考。如不使用默认应用,请参考 如何创建应用,并获取对应环境 App Key 和 App
Secret。。

- . 获取开发环境的应用AppApp Key。如不使用默认应用,请参考。如不使用默认应用,请参考 如何创建应用,并获取对应环境 App Key 和 App Secret。。 

注意 

每个应用具有两个不同的 App Key ,分别对应开发环境与生产环境,两个环境之间数据隔离。在您的应用正式上 线前,可切换到使用生产环境的 App Key ,以便上线前进行测试和最终发布。 

- . 完成开通音视频服务。您需要开通音视频通话服务。 

##### 快速上手 

您可以通过集成 CallPlus for HarmonyOS 进行一对一通话,或多人通话。 

### 步骤 **1** 创建项目 

打开 DevEco-Studio 并创建一个新项目,选择模版。 

- 5 - 

配置 quickDemo ,点击 创建 

- 6 - 

### 步骤 **2** 集成 **SDK** 

您可以使用ohpm 安装 @rongcloud/callplus ,也可以通过下载对应的 har 文件手动导入到工程中。 

#### **ohpm** 

1. 找到工程目录的 oh-package.json5 文件,增加 dependencies 依赖配置。 

2. 上一步完成后,点击 Sync Now 或者在项目当前目录打开终端,执行 ohpm install IDE 会自动对应下载好 har 包。 

注意 

注意每个 SDK 的最新版本号可能不相同,具体版本可前往OpenHarmony三方库中心仓 查询。 

### 步骤 **3** 工程配置 

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

### 步骤 **5** 使用 **App Key** 初始化 

CallPlus 是基于 IMLib 作为信令通道的,要在您的应用程序中集成和运行,您需要先对 IMLib 初始化,核心类为 IMEngine 在 UIAbility 的 onCreate() 方法中,调用初始化方法,传入生产或开发环境的 App Key。 

###### **TypeScript** 

- 10 - 

**/** 在UIAbility 中获取context 

let context = this.context 

let initOption = new InitOption(); let appKey = "从融云后台获取的 appKey" IMEngine.getInstance().init(context, appKey, initOption) 

初始化配置 InitOption 中封装了区域码 RCAreaCode ,导航服务地址 naviServer、统计服务地址 statisticServer ,文件 下载路径 mediaSavePath。不作设置表示全部使用默认配置。 SDK 默认连接北京数据中心。 

###### 注意 

每个融云应用提供开发环境与生产环境,分别使用不同的 App Key ,两个环境之间数据隔离。只要客户端应用使用同一 个环境的 App Key ,用户可以跨所有平台相互通信。 

### 步骤 **6** 添加通话所需代理 

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

### 步骤 **7** 获取用户 **Token** 

用户身份令牌( Token)与用户 ID 对应,是应用程序用户在融云的唯一身份标识。应用客户端在使用融云服务前必须与融云 建立 IM 连接,连接时必须传入 Token。 

在体验和调试阶段,我们将使用控制台「北极星」开发者工具箱,从 API 调试页面调用获取 Token 接口,获取到 **userId** 为 1 的用户的 Token。提交后,可在返回正文中取得 Token 字符串。 

###### **HTTP** 

HTTP/1.1 200 OK 

Content-Type: application/json; charset=utf-8 

{"code":200,"userId":"1","token":"gxld6GHx3t1eDxof1qtxxYrQcjkbhl1V@sgyu.cn.example.com;sgyu.cn.exam 

融云的客户端 SDK 不提供获取 token 的 API。在实际业务运行过程中,调用融云 Server API /user/getToken.json , 传入您的应用分配的用户标识( userId)申请 Token。详见 Server API 文档 注册用户。 

### 步骤 **8** 连接融云服务器 

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

##### 进行一对一通话 

CallPlus for HarmonyOS SDK 提供了仅限两位用户通话的一对一通话类型 RCCallPlusType.SINGLE。发起一对一类型通 话时,只允许传入一个被叫用户 ID ,仅在被叫接听成功后才会建立通话。融云会在被叫接听成功后开始计时。 

本节中将简单介绍如何发起一对一通话,如何接收来电,以及通话接通后双方通话界面如何显示。 

### 步骤 **9** 发起呼叫 

使用 RCCallPlusClient 的 startCallWithParams 方法发起一对一通话。方法调用后,SDK 内部会以异步方式执行。在主叫 与被叫端触发以下回调: 

- 本地主叫用户通过 startCallWithParams 的返回值 Promise 来获取方法的执行结果。 

- 远端被叫用户通过 ICallPlusEventListener 的 onReceivedCall 回调获取来电通知。 

###### **TypeScript** 

- 14 - 

private _startCall() { RCCallPlusClient.getInstance().startCallWithParams({ userIds: ['userId1'], mediaType: RCCallPlusMediaType.AUDIO, extra: 'extra', syncData: 'syncData' }).then((result) => { if (result.code === RCCallPlusCode.SUCCESS) { ' ' console.log( 发起通话成功 ); } else { ' ' console.log( 发起通话失败 , result.code); } }); } 

### 步骤 **10** 接听 

被呼叫端通过监听 onReceivedCall 方法接收通话,记录 callId 然后使用 accept 方法接听来电。 

###### **TypeScript** 

private _accept(callId: string) { RCCallPlusClient.getInstance().accept(callId).then((result) => { if (result.code === RCCallPlusCode.SUCCESS) { ' ' console.log( 接听成功 ); } else { ' ' console.log( 接听失败 , result.code); } }); } 

应用未启动,被叫方通过远程通知接收来电。点击收到的推送通知后启动 App ,在设置 RCCallPlusEventDelegate 代 理并连接 IM 成功后,还是通过 [didReceivedCall:extra:] 接收到通话。 

##### 进行多人通话 

CallPlus for HarmonyOS SDK 提供了支持多人呼叫的通话类型 RCCallPlusType.MULTI。发起多人通话与一对一通话使用 相同的方法,多人通话一旦发起成功,融云即开始计时计费。 

下文仅描述了发起多人通话的方法。在实际项目中,我们建议您先按照一对一通话 实现完整的通话流程,再按照多人通话补 充实现与一对一通话有差异的步骤。 

- 15 - 

在一对一通话过程中可以邀请用户加入通话。一旦邀请成功,通话类型会自动转为多人通话。详见多人通话。 

### 步骤 **11** 发起多人通话 

使用 startCallWithParams 方法,callType 参数必须为 RCCallPlusType.MULTI 多人通话类型。 

###### **TypeScript** 

private _startMultiCall() { 

RCCallPlusClient.getInstance().startCallWithParams({ userIds: ['userId1', 'userId2'], type: RCCallPlusType.MULTI, mediaType: RCCallPlusMediaType.AUDIO, extra: 'extra', syncData: 'syncData' }).then((result) => { if (result.code === RCCallPlusCode.SUCCESS) { ' ' console.log( 发起通话成功 ); } else { ' ' console.log( 发起通话失败 , result.code); } }); } 

###### 注意 

有关在您的应用程序中构建语音和视频通话功能的详细指南,请参阅完整的一对一通话和多人通话 文档。我们建议您先 按照一对一通话实现完整的通话流程,再按照多人通话补充实现与一对一通话有差异的步骤。 

- 57 -
