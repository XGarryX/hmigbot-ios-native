# **PlayerSDK 使用文档** 

[TOC] 

## **一、概述** 

### **SDK 介绍** 

PlayerSDK 是专门为鸿蒙平台设计的音视频直播播放 SDK,用于实现展动平台直播内容的播放。适用于需要集成直播功能的各类鸿蒙应用,如在线教育、直播电商等 场景。其主要功能包括视频播放、文档显示、聊天互动、问答交流、投票调查、文件管理、用户管理及其他交互功能。 

### **特性列表** 

**视频播放** :流畅播放展动平台的直播视频流。 

- **文档显示** :支持在直播过程中展示文档资料。 

- **聊天互动** :提供实时聊天功能,方便用户交流。 **问答交流** :实现用户提问和解答的交互。 

- **投票调查** :支持发起和参与投票活动。 

- **文件管理** :可进行文件的下载和管理。 

- **用户管理** :对用户信息进行管理和操作。 

- **其他交互** :包含如签到等互动功能。 

### **支持的环境** 

**操作系统** :HarmonyOS 

**编程语言** :ArkTS **最低版本要求** :5.0.1(13) **依赖项** : 

- "@ohos/axios": "2.2.6" 需要添加到根目录或者是sdk同级目录的 oh-package.json5 中 

##### **依赖方式** : 

将@gensee/playersdk.har放到lib目录或者其他目录下,通过file:路径/genseesdk.har进行依赖。 

"dependencies": { "@gensee/playersdk": "file:libs/genseesdk.har" } 

## **二、快速开始** 

### **1. 引入 SDK** 

确保在项目中正确引入 @gensee/playersdk 模块,可通过如下方式引入: 

import { PlayerSDK } from '@gensee/playersdk' 

### **2. 初始化 SDK** 

在使用 PlayerSDK 之前,需要先进行初始化操作: 

const playersdk = new PlayerSDK() playersdk.init() 

### **3. 输入参数加入直播** 

// 创建初始化参数对象 let initParam = new InitParam() // 设置域名或ip(必填) initParam.domain = this.liveDomin // 设置直播 ID(必填) initParam.number = this.liveId // 设置昵称(必填) initParam.nickName = this.nickname 

- // 设置加入密码 

initParam.joinPwd = this.passcode 

- // 设置分组号 

initParam.groupCode = this.groupCode 

- // 设置traning或webcast initParam.serviceType = this.serviceType 

- // 设置自定义用户ID 

initParam.userId = this.userId 

- // 设置站点登录账号 

initParam.loginAccount = this.userAccountName 

- // 设置站点登录密码 

initParam.loginPwd = this.userAccountPW // 设置认证 K 值 initParam.k = this.kValue 

- // 设置用户自定义参数 

initParam.userData = this.userExtraData 

// 使用初始化参数进行认证并加入直播 

playersdk.initWithParam(initParam).then((result) => { 

- // 认证成功,处理返回结果 

showToast("获取成功") 

- // 然后可以通过joinLive加入到直播 

playersdk.joinLive(getContext(), result) 

- }).catch((e: BusinessError | GSError) => { 

- // 处理认证失败的情况 

if (e instanceof GSError) { showToast(e.errMsg) 

} else { showToast("未知错误:" + e.message) } }) 

接下来可通过 playersdk.setPlayerListener(this.livePlayerListener) 中的 onJoin 回调判断是否加入成功 

```arkts
private livePlayerListener:LivePlayerListener = { onJoin: (result: JoinResultCode): void => { if (result == JoinResultCode.JOIN_OK) { showToast("加入成功") this.isBuffing = false 
```

- } else { 

- if (result == JoinResultCode.JOIN_TOO_EARLY) { showToast("加入失败:直播间还未开始") 

- } else if (result == JoinResultCode.JOIN_CONNECT_FAILED) { showToast("加入失败:连接失败") 

- } else if (result == JoinResultCode.JOIN_CONNECT_TIMEOUT) { showToast("加入失败:连接超时") 

- } else if (result == JoinResultCode.JOIN_RTMP_FAILED) { showToast("加入失败:连接服务器失败") 

- } else if (result == JoinResultCode.JOIN_LICENSE) { showToast("加入失败:直播间人数已满") 

} else if (result == JoinResultCode.JOIN_IP_FORBIDDEN) { showToast("加入失败:IP被封禁") } else { showToast("加入失败:"+result) } } }, //... } as LivePlayerListener 

## **三、各个模块及 API 使用** 

**PlayerSDK 主功能** 

#### **1. 初始化** 

在使用 PlayerSDK 前,需要先进行初始化操作。 

// 创建 PlayerSDK 实例 const playersdk = new PlayerSDK(); // 调用 init 方法初始化 playersdk.init(); 

#### **2. 开始认证** 

使用 initWithParam 方法开始认证,传入初始化参数 InitParam ,并处理认证结果。 

// 创建初始化参数对象 

```arkts
let initParam = new InitParam(); initParam.domain = "your_domain"; initParam.number = "your_live_id"; initParam.nickName = "your_nickname"; // 其他参数设置... 
```

playersdk.initWithParam(initParam).then((result) => { 

// 认证成功,处理返回结果 console.log("认证成功,直播间信息:", result); // 可以在这里进行后续操作,如显示对话框提示进入直播等 }).catch((e) => { // 处理认证失败的情况 if (e instanceof GSError) { console.error("认证失败,错误信息:", e.errMsg); } else { console.error("未知错误:", e.message); } }); 

#### **3. 加入直播间** 

调用 joinLive 方法加入直播间,需要传入上下文 context 和直播间参数信息 liveAttributes 。 

playersdk.joinLive(context, liveAttributes) 

#### **4. 接受连麦邀请** 

当收到 onInvite 消息后,使用 inviteAck 方法接受或拒绝本次连麦邀请,但需要注意在调用前确保应用有对应的麦克风和摄像头权限。 typescript // 假设本次邀请连麦类型为视频连麦,接受邀请 playersdk.inviteAck(InviteType.VIDEO, true); 

#### **5. 设置服务器端口** 

如果因网络安全等要求,需要设置服务器端口,可使用 setServerPort 方法,此操作要在加入直播前进行。正常使用场景不需要进行设置。 typescript // 设置 HTTP 端口和 WebSocket 端口 playersdk.setServerPort(port1, port2); 

#### **6. 获取当前登录用户信息** 

使用 getSelfUserInfo 方法获取当前登录的用户信息,若返回为空则表示未登录成功。 

```arkts
const userInfo = playersdk.getSelfUserInfo(); if (userInfo) { console.log("当前登录用户信息:", userInfo); } else { console.log("未登录成功"); } 
```

#### **7. 设置回调监听** 

通过 setPlayerListener 方法设置 LivePlayerListener 回调监听,以处理直播间的各种状态变化。 

```arkts
const livePlayerListener = { onJoin: (result) => { if (result === JoinResultCode.JOIN_OK) { console.log('加入直播间成功'); } else { console.log('加入直播间失败'); } }, onReconnecting: () => { console.log('因网络原因开始重新连接服务器'); }, onLeave: (reason) => { console.log('退出直播间,原因:', reason); }, // 实现其他回调方法... }; playersdk.setPlayerListener(livePlayerListener); 
```

#### **8. 离开直播间** 

当用户想退出直播间时,可以主动调用 leaveLive 离开直播间 ts playersdk.leaveLive() 

#### **9. 销毁SDK** 

不用SDK时,需主动释放SDK所占用的资源,需要在每次退出直播的时候进行清理。清理后如果再次进入直播,不需要重新创建PlayerSDK对象,直接复用即可。 ts playersdk.release() 

### **视频播放** 

#### **视频播放概述** 

视频播放我们提供了一个UI控件 VideoView ,直接将其添加到UI中,当有视频桢时即可自动绘制显示 

#### **实例代码** 

VideoView() .alignRules({ top: { anchor: 'title', align: VerticalAlign.Bottom }, middle: { anchor: '__container__', align: HorizontalAlign.Center } }) .id("Player") .width('100%') .height('500lpx') 

### **文档** 

#### **文档模块概述** 

为了方便客户使用,我们直接封装了一个 DocView 用于显示文档,在创建 DocView 的时候需要传入一个 DocManager 对象,并且这个对象需要一并设置给 PlayerSDK,这样即可实现文档的显示。 

#### **相关 API 使用** 

##### **绑定文档管理器** 

通过 playersdk.bindDocManager 方法将文档管理器与 playersdk 进行绑定,确保文档能够正常显示。 

private docManager = new DocManager() playersdk.bindDocManager(this.docManager) 

##### **显示文档视图** 

在UI组件中,使用 DocView 组件来显示文档。 

TabContent() { // 父控件随意,这里只是演示 DocView({manager:this.docManager}) .width('100%') .height('100%') } .tabBar('文档') 

**参数说明** : - manager : DocManager 类型的实例,用于管理文档的显示和切换。 

### **连麦** 

#### **概述** 

PlayerSDK 支持视频与语音连麦功能,支持老师与学员之间的互动、提问。 SDK本身是无法主动发起连麦的,观看端只能被动接收连麦请求后同意或拒绝连麦。 用户可在接收到连麦邀请后选择是否接受,同意前需确保应用有对应权限,SDK 内部会自动处理麦克风和摄像头的开关。 

#### **相关 API 使用** 

#### **连麦类型** 

export enum InviteType{ AUDIO = 1, // 音频 VIDEO = 2, // 视频 MULTI = 3 // 混合(音频+视频) } 

##### **连麦请求通知** 

连麦请求通知是通过 LivePlayerListener 的 onInvite() 回调中通知过来 

##### **接受、拒绝连麦** 

通过 playersdk.inviteAck() 方法处理连麦请求,示例如下 ts // 接受连麦 playersdk.inviteAck(InviteType.MULTI,true) **注意事项:在应用 进入后台的时候,必须结束当前的连麦,鸿蒙系统不允许后台应用使用麦克风,否则会产生崩溃。 在检测到应用进入后台后,需主动调用 plyaersdk.inviteAck(InviteType.MULTI,false) 结束全部连麦并关闭麦克风占用。** 

这里附一个相对完整的连麦邀请处理逻辑示例代码: ```ts private livePlayerListener:LivePlayerListener = { onInvite: (type: InviteType, isOpen: boolean): void => { if (isOpen) { if (type == InviteType.AUDIO) { this.inviteTypeStr = "音频" } else if (type == InviteType.VIDEO) { this.inviteTypeStr = "视频" } else { this.inviteTypeStr = "音 频/视频" } AlertDialog.show( { title: this.inviteTypeStr+'连麦邀请', message: '老师邀请你参与连麦', autoCancel: true, alignment: DialogAlignment.Bottom, gridCount: 4, offset: { dx: 0, dy: -20 }, primaryButton: { value: '取消', action: () => { // 拒绝连麦 playersdk.inviteAck(type,false) this.inviteType = playersdk.getCurrInviteType() } }, secondaryButton: { enabled: true, defaultFocus: true, style: DialogButtonStyle.HIGHLIGHT, value: '确认', action: async () => { try { // 检测并请求权限 await reqPermissionsFromUser(["ohos.permission.MICROPHONE","ohos.permission.CAMERA"],getContext(this) as common.UIAbilityContext) playersdk.inviteAck(type,true) } catch (e) { // 没有权限拒绝连麦 playersdk.inviteAck(type,false) showToast("没有获取到相应权限,请到设置中开启权限") } this.inviteType = playersdk.getCurrInviteType() console.info(TAG,"inviteType" + this.inviteType) 

} } } ) } else { this.inviteType = playersdk.getCurrInviteType() if (this.inviteType == undefined) { showToast("已关闭连麦") } else { showToast("已关闭一路连麦") } } }, 

} as LivePlayerListener ``` 

### **聊天模块** 

#### **概述** 

聊天模块提供了在直播中进行私聊和公聊的功能,支持发送纯文本和富文本内容,并且可以设置聊天相关的回调监听。 

**相关 API 使用** 

##### **获取聊天 API 实例** 

在使用聊天功能前,需要先获取 LiveChatApi 的实例。该实例需要通过 playersdk 主类获取聊天 API 对象: 

const liveChatApi = playersdk.getChatApi(); 

##### **发送公聊消息** 

可以使用 chatToPublic 方法发送公聊消息,该方法提供了较强的自定义属性的能力,但使用较为繁琐。示例如下: 

import { ChatMsg } from '@gensee/playersdk'; 

```arkts
const chatMsg = new ChatMsg(); chatMsg.content = '这是一条公聊消息'; chatMsg.richText = richText // 是ChatSpan[]类型,用来区分表情和文本 chatMsg.senderId = this.selfUserInfo!.id chatMsg.sender = this.selfUserInfo!.name chatMsg.senderRole = this.selfUserInfo!.role chatMsg.chatId = this.selfUserInfo!.chatId chatMsg.id = uuid liveChatApi.chatToPublic(chatMsg); 
```

**该方法需要自行构建 ChatMsg 类,尤其是需要自行组装 richText ,还需自行设置发送人的信息,较为复杂,如果是只是简单的想发送纯文本信息,那么更推 荐使用 sendContent 方法,使用方式见下文。 如果是需要发送带有表情的消息,那么推荐使用 sendRichTextSpans 方法也更为简单。** 

##### **发送私聊消息** 

使用 chatToPerson 方法发送私聊消息,示例如下: 

import { PrivateChatMsg } from '@gensee/playersdk'; 

```arkts
const private ChatMsg = new PrivateChatMsg(); // 设置消息内容等通用属性,与公聊一致 private ChatMsg.content = '这是一条私聊消息'; private ChatMsg.richText = richText // 是ChatSpan[]类型,用来区分表情和文本 private ChatMsg.senderId = this.selfUserInfo!.id private ChatMsg.sender = this.selfUserInfo!.name private ChatMsg.senderRole = this.selfUserInfo!.role private ChatMsg.chatId = this.selfUserInfo!.chatId // 设置接收用户信息 chatMsg.chatId = receiveUser.chatId chatMsg.targetName = receiveUser.name liveChatApi.chatToPerson(private ChatMsg); 
```

##### **发送纯文本消息** 

为了方便客户使用,现在提供了 sendContent 方法发送纯文本消息,减少一些通用参数的设置。 该方法可指定 receiveUser 用于设置私聊对象 ,若不指定 receiveUser 则为公聊,示例如下: 

// 公聊纯文本消息 liveChatApi.sendContent('这是一条公聊纯文本消息'); // 私聊纯文本消息 import { UserInfo } from '@gensee/playersdk'; const receiveUser: UserInfo = this.targetUser; liveChatApi.sendContent('这是一条私聊纯文本消息', receiveUser); 

##### **发送富文本消息** 

使用 sendRichTextSpans 方法发送表情和文本混合消息,其示例如下: 

import { ChatSpan } from '@gensee/playersdk'; 

const richTextSpans: ChatSpan[] = [ new ImgSpan('emotion/emotion.smile.gif'),// 参数必须为EmojiData中的model数据,否则其他端无法显示。 new TextSpan("", '',"你好") // 第一个参数为字体颜色,第二个参数是字体大小,如果需要特殊指定填入需求的大小和颜色即可 ]; // 公聊富文本消息 liveChatApi.sendRichTextSpans(richTextSpans); 

// 私聊富文本消息 const receiveUser: UserInfo = this.targetUser; liveChatApi.sendRichTextSpans(richTextSpans, receiveUser); 

##### 这里提供一个发送表情和文本的简单示例: 

##### 首先推荐使用鸿蒙提供的 RichEditor 这个控件来接受和显示输入的表情和文本数据 

controllerRich: RichEditorController = new RichEditorController(); // 输入框 RichEditor({ controller: this.controllerRich }) .height($r('app.integer.chat_with_expression_chat_input_height')) .layoutWeight(1) .margin({left:$r('app.integer.chat_with_expression_express_margin_left')}) .borderRadius($r('app.integer.chat_with_expression_chat_border_radius')) .backgroundColor($r('app.string.chat_with_expression_input_background')) .key(this.focusKey) .id(this.focusKey) .defaultFocus(false) .onClick(async () => { this.isFaceDlgOpen = false; this.isFaceClick = false; }) 

##### 在点击表情的时候通过 controllerRich 添加表情数据 

##### // 将表情添加到输入框中 

this.controllerRich!.addImageSpan($rawfile(this.EmojiItem?.imgSrc), { imageStyle: { size: [this.msgFontSize / 3.2, this.msgFontSize / 3.2], // 3.2 调整表情在输入框中的尺寸 verticalAlign: ImageSpanAlignment.CENTER, layoutStyle: { margin: FaceGridConstants.EMOJI_MARGIN } } }); 

##### 最后在点击发送按钮的时候通过 controllerRich 获取输入的表情和文字,组装 ChatSpan[] 

```arkts
async sendChatMsg(): Promise<void> { let msgBase:ChatSpan[] = [] // 获取发送信息 this.controllerRich.getSpans().forEach(item => { if (typeof (item as RichEditorImageSpanResult)['imageStyle'] !== 'undefined') { // 处理imagespan信息 const imageMsg: ResourceStr | undefined = (item as RichEditorImageSpanResult).valueResourceStr; if (imageMsg !== undefined) { const spanItem: ImgSpan = new ImgSpan(imageMsg.toString().replace("resource://RAWFILE/","")); msgBase.push(spanItem); } } else { // 处理文字span信息 const textMsg: string = (item as RichEditorTextSpanResult).value; const spanItem: TextSpan = new TextSpan("", '',textMsg); msgBase.push(spanItem); } }) if (msgBase.length > 0) { this.controllerRich.deleteSpans(); this.controllerRich.setCaretOffset(-1); if (this.private ChatUser) { // 发送给指定人 playersdk.getChatApi().sendRichTextSpans(msgBase,this.private ChatUser) } else { // 发送给所有人 playersdk.getChatApi().sendRichTextSpans(msgBase) } } this.scroller.scrollEdge(Edge.Bottom); } 
```

具体示例可Demo项目代码。 

##### **设置聊天接收回调监听** 

通过 setChatListener 方法设置聊天相关的回调监听,示例如下: 

```arkts
import { ChatListener } from '@gensee/playersdk'; const chatListener: ChatListener = { // 收到公聊消息的通知 onChatWithPublic: (msg:ChatMsg) => { console.log('收到聊天消息:', msg.content); }, // ... }; liveChatApi.setChatListener(chatListener); 
```

ChatListener 类具体方法及解释见 四、回调说明模块。 

##### **消息的显示** 

收到消息后,优先推荐显示的 ChatMsg 中的 richTextSpans 内容,其中包括了表情和文本,及文本的颜色和大小,可根据项目需求自由设置。示例如下: 

Text(){ 

ForEach(item.richTextSpans, (item: ChatSpan) => { // 分别使用ImageSpan、Span渲染图片、文字信息 if (item instanceof ImgSpan) { ImageSpan($rawfile(item.src)) .width('36lpx') .height('36lpx') .verticalAlign(ImageSpanAlignment.BOTTOM).objectFit(ImageFit.Cover) } else if (item instanceof TextSpan) { Span(item.text) .fontSize(item.fontSize) .fontColor(item.color) } }) } 

**问答模块** 

#### **概述** 

问答模块允许用户在直播过程中进行提问和同问操作,通过设置问答消息回调监听,以便及时处理问答的添加、更新、取消等事件。 

#### **相关类和接口** 

##### **LiveQAApi 接口** 

|LiveQAApi 定义了问答模块的主要操作接口,包括设置回调监听、提问和同问功能。|
|---|
|import { QAListener } from "../../callback/QAListener";|
|export interface LiveQAApi{ /** *设置问答消息回调监听 * @param qaListener */ setQAListener(qaListener:QAListener):void|
|/** *提问 * @param question问题内容 */ question(question:string):void|
|/** *同问(当前小班课功能,后续可能全产品覆盖),server要在5.2版本及以上支持 * @param questionUUid同问问题的问题id,也就是对应问答的id(UUID) */ sameQuestion(questionUUid:string):void }|

#### **API 使用示例** 

##### **获取问答模块 API** 

|const liveQAApi = playersdk.getQAApi(); **置问答消息回调监听**|
|---|
|const qaListener: QAListener = {|
|onQa: (qaMsg: QaMsg): void => { //处理问答的添加或更新 console.log('收到问答更新:', qaMsg);|
|}, //...|
|};|
|liveQAApi.setQAListener(qaListener);|
|const questionContent = "这是一个问题"; **问**|
|liveQAApi.question(questionContent); **问**|
|const questionUUid = "12345678-1234-5678-1234-567812345678";|
|liveQAApi.sameQuestion(questionUUid);|

##### **设置问答消息回调监听** 

##### **提问** 

##### **同问** 

### **投票模块** 

#### **概述** 

投票模块允许在直播或其他场景中发起投票活动,用户可以参与投票并提交答案。该模块提供了投票信息的解析、投票监听以及投票提交等功能。 

#### **API 使用示例** 

##### **LiveVoteApi 接口** 

定义了投票模块的主要操作接口,包括设置投票监听和提交投票答案。 

```arkts
export interface LiveVoteApi { /** * 设置投票回调监听 * @param listener */ setVoteListener(listener: VoteListener): void; /** * 提交答题卡 * @param voteSheet */ submitVote(voteSheet: VoteSheet): void; } 
```

##### **设置投票监听** 

在使用投票功能之前,需要设置投票监听,以便处理投票相关的事件。 

```arkts
import { VoteListener } from "@gensee/playersdk"; import { playersdk } from "../pages/Index"; const voteListener: VoteListener = { onVotePublish: (vote: BaseVote): void => { // 处理投票发布事件 console.log("收到投票发布通知", vote); }, onVotePublishResult: (vote: BaseVote): void => { // 处理投票结果公布事件 console.log("收到投票结果通知", vote); }, onVoteNotifyFinished: (voteId: string): void => { // 处理投票结束事件 console.log("投票结束,投票 ID:", voteId); }, onThirdVote: (url: string): void => { // 处理第三方投票链接回调 console.log("收到第三方投票链接:", url); }, }; playersdk.getVoteApi().setVoteListener(voteListener); 
```

##### **参与投票** 

当收到投票发布通知后,用户可以参与投票并提交答案。 

import { VoteSheet } from "@gensee/playersdk"; import { BaseVote, QuestionType } from "@gensee/playersdk"; 

// 假设 vote 是收到的投票信息 const vote: BaseVote = ...; // 这里需要传入要作答的投票信息 const voteSheet = new VoteSheet(vote); 

// 设置单选题答案 voteSheet.setAnswer("questionId1", "answerId1"); 

// 设置多选题答案 voteSheet.setAnswer("questionId2", "answerId2"); voteSheet.setAnswer("questionId2", "answerId3"); 

// 设置文本题答案 voteSheet.setAnswer("questionId3", "这是文本题的答案"); 

// 提交投票答案 playersdk.getVoteApi().submitVote(voteSheet); 

### **用户管理模块** 

#### **概述** 

用户管理模块主要负责对直播中的用户信息进行管理,包括设置用户相关回调监听、通过 ID 查询用户信息以及用户重命名等功能。 

**接口定义** 

##### LiveUserApi 接口定义了用户管理模块对外暴露的 API,具体如下: 

export interface LiveUserApi{ /** * 设置用户相关的回调监听 * @param listener */ setUserListener(listener:UserListener):void /** * 通过id查询完整的用户信息,结果会在UserListener中的onGetUserInfo回调 * @param ids */ getUserById(ids:number[]):void /** * 自己重命名 * @param newName 新名字 */ reName(newName:string):void } 

#### **API 详细说明** 

##### **设置用户相关的回调监听** 

import { UserListener } from "@gensee/playersdk"; import { UserInfo } from "@gensee/playersdk"; 

```arkts
const userListener: UserListener = { onUserJoin: (info: UserInfo): void => { // 处理新用户加入事件 }, // 其他回调... }; 
```

playersdk.getUserApi().setUserListener(userListener); 

##### **通过 ID 查询完整的用户信息** 

const userIds = [10001, 10002, 10003]; playersdk.getUserApi().getUserById(userIds); 

查询结果会通过 UserListener 中的 onGetUserInfo 方法回调,开发者需要在 setUserListener 中实现该方法来处理查询结果。 

##### **重命名** 

const newName = "NewUserName"; playersdk.getUserApi().reName(newName); 

如果 newName 为空字符串,则该方法不会执行任何操作。 

### **文件模块** 

#### **概述** 

文件模块提供了文件消息通知回调的设置以及文件下载的功能。 

#### **接口定义** 

```arkts
export interface LiveFileApi { /** * 设置文件消息的通知回调 * @param listener */ setFileListener(listener: FileListener): void; /** * 开始下载文件 * @param url 需要下载的文件地址 * @param fullFilePath 手机储存位置 */ downloadFile(url: string, fullFilePath: string): void; } 
```

#### **API 详细说明** 

##### **设置文件通知回调** 

import { FileListener } from "genseesdk/src/main/ets/gensee/callback/FileListener"; 

const fileListener: FileListener = { 

onFileShare: (wCmdType: number, strFileName: string, strFileUrl: string) => { // 处理文件共享事件 console.log(`文件共享: 类型 ${wCmdType}, 文件名 ${strFileName}, 下载地址 ${strFileUrl}`); }, 

onFileShareDl: (bIsOK: boolean, strFileUrl: string, strSavePath: string) => { // 处理文件下载事件 

if (bIsOK) { console.log(`文件下载成功,保存路径: ${strSavePath}`); } else { console.log(`文件下载失败`); } } }; 

playersdk.getFileApi().setFileListener(fileListener); 

##### **下载文件到指定的手机储存位置** 

```arkts
const liveFileApi = playersdk.getFileApi(); const fileUrl = strFileUrl; const savePath = path; 
```

liveFileApi.downloadFile(fileUrl, savePath); 

具体示例可参考Demo项目的 FileListView 代码 

### **其他交互模块** 

此模块主要提供直播中的互动功能,如点名、抽奖等。 

#### **接口定义** 

export interface LiveInterActiveApi{ /** 

- 设置互动监听器,用于接收互动相关的回调信息 

* @param listener 互动监听器对象 */ 

setListener(listener:InterActiveListener):void; 

/** 

##### * 对点名操作进行响应 

- @param isAccept 是否接受点名,true 表示接受,false 表示拒绝 */ 

- rollCallAck(isAccept:boolean) :void; } 

#### **API 详细说明** 

**设置回调监听** 

// 创建一个实现了 InterActiveListener 接口的监听器对象 

```arkts
const interActiveListener: InterActiveListener = { onRollCall: (time: number) => { console.log(`收到点名通知,时间为: ${time}`); }, 
```

onLottery: (cmd: number, lotteryInfo: string) => { console.log(`收到抽奖通知,命令: ${cmd},中奖人信息: ${lotteryInfo}`); } }; 

// 获取互动模块的 API 实例 

const liveInterActiveApi = playersdk.getInteractiveApi(); 

// 设置监听器 liveInterActiveApi.setListener(interActiveListener); 

##### **对点名操作进行响应** 

// 当需要对点名进行响应时,调用 rollCallAck 方法 const isAccept = true; // 接受点名 liveInterActiveApi.rollCallAck(isAccept); 

## **四、各个模块回调监听说明** 

### **核心监听 LivePlayerListener** 

export interface LivePlayerListener { 

/** 

* 加入直播间结果,在调用joinLive后回调 * @param result */ 

onJoin: (result: JoinResultCode) => void; 

/** 

* 因网络原因导致网络不稳定开始重新连接服务器 

*/ onReconnecting: () => void; /** * 退出直播间 * @param reason 离开的原因 */ onLeave: (reason: LeaveReason) => void; /** 

* 直播间开始缓冲或结束缓冲 

* @param isCaching */ onCaching: (isCaching: boolean) => void; /** * SDK发生错误时回调 

* @param err 错误内容 */ onErr: (err: string) => void; /** 

- 老师或组织者进行文档切换时通知。docName 文档名称。 

- @param docType 文档类型,(tip:docType=0 代表文档关闭) 

* @param docName 

*/ 

onDocSwitch: (docType: number, docName: string) => void; 

/** 

##### * 直播间开始有了视频桢 

*/ onVideoBegin: () => void; /** * 直播间视频没有视频桢 */ onVideoEnd: () => void; /** 

- 视频大小回调 

- @param width 

* @param height */ onVideoSize: (width: number, height: number) => void; 

  /**
   * 音频电频值可以根据需要处理以展示音调的高低,但请不要直接在回调做复杂的逻辑处理或执行占用时间长的代码,范围 0-90。
   * audioLevel 0-90
   * @param level 0 - 90
   */
  onAudioLevel: (level: number) => void;
  /**
   * 直播状态变更通知
   * @param isPlaying true 直播中,false 为直播暂停
   */
  onPublish: (isPlaying: boolean) => void;
  /**
   * 直播间内广播消息通知
   * @param userid
   * @param content 广播消息内容
   * @param sendtime 发送时间
   */
  onPublicMsg: (userid: number, content: string, sendtime: number) => void;
  /**
   * 直播间文字直播
   * @param language 本次文字直播的文字语言
   * @param text 内容
   */
  onLiveText: (language: string, text: string) => void;
  /**
   * 直播间不同事件的通知
   * 目前有老师锁屏通知 key=screenlock
   * @param key
   * @param value
   */
  onRoomData: (key: string, value: string) => void;
  /**
   * 多媒体(音频、视频)通话邀请,
   * 在收到该消息后,需再调用playersdk.inviteAck()方法同意或拒绝连麦
   * @param type 为纯音频,纯视频,或混合类型
   * @param isOpen 是否是邀请或者取消
   */
  onInvite: (type: InviteType, isOpen: boolean) => void;
  /**
   * 桌面共享开启或关闭时响应
   * @param isAs
   */
  onScreenStatus: (isAs: boolean) => void;
  /**
   * 一般是组织者控制的时候通知给 web 观看者,Playersdk 在大讲堂或 webcast 中可以响应
   * @param mode 0 文档为主  1 视频最大化 2文档最大化 3 视频为主
   */
  onModuleFocus: (mode: FocusMode) => void;
  /**
   * 双师课堂切换的时候回调,app根据回调更新相关的信息或提示。
   * 双师课堂关闭用户列表(后台系统管理- 系统设置-小班课用户列表-不显示)的话,
   * 聊天消息是不显示的。开启用户列表,学员只显示当前分组和老师、助教的消息。
   * @param status 0 切换到分课堂 1 切换到总课堂(名师课堂)
   */
  onDoubleTeacherStatusChange: (status: number) => void;
}

**聊天回调 ChatListener** 

export interface ChatListener{ /** * 收到私聊消息的通知 * @param msg 聊天消息 */ onChatWithPerson:(msg:PrivateChatMsg)=>void /** * 收到公聊消息的通知 * @param msg 聊天消息 */ onChatWithPublic:(msg:ChatMsg)=>void /** * 自己被禁言的通知 * @param isMute 是否禁言 */ onMute:(isMute:boolean)=>void /** * 房间全局聊天权限通知 * @param isMute 是否禁言 */ onRoomMute:(isMute:boolean)=>void /** * 消息通过审核处理后返回的结果,此借口返回的聊天信息需要从列表中删除 

- 通过判断type去区分id的类型,如果是msgID的话需要删除这个msgid的消息 

- 如果是userId的话需要删除这个用户的全部消息 

- @param type 是id的类型,可能为msgID或者是userId 

- @param id 

*/ onChatCensor:(type:CensorType,id:string)=>void } 

### **问答回调 QAListener** 

export interface QAListener{ 

/** * 问答的添加、更新都会走这个回调 * @param qaMsg */ onQa:(qaMsg:QaMsg)=>void /** * 问答被取消 * @param questionId */ onQaCancel:(questionId:string)=>void /** * 自己被禁止问答的通知 * @param isMute 是否是禁言 */ onQaMute:(isMute:boolean) => void /** * 直播间总体是否被禁止提问的回调 * @param isMute 是否是禁言 */ onRoomMute:(isMute:boolean) => void } 

### **投票回调 VoteListener** 

export interface VoteListener{ /** * 收到了投票发布的通知 * @param vote */ onVotePublish:(vote:BaseVote)=>void /** * 投票结束的通知 * @param voteId */ onVoteNotifyFinished:(voteId:string)=>void /** * 投票结果的通知 * @param vote */ onVotePublishResult:(vote:BaseVote)=>void /** * 第三方投票链接回调 * @param url */ onThirdVote: (url: string) => void; } 

### **文件回调 FileListener** 

export interface FileListener{ 

/** 

- 直播间文件共享功能事件回调 

- @param cmd 文件状态 

- @param fileName 文件名称 

- @param fileUrl 文件位置 

*/ 

onFileShare:(cmd: ShareFileCMD, fileName: string, fileUrl: string)=>void 

/** 

- 文件共享功能中的下载事件回调 

- @param bIsOK 下载结果 

- @param fileUrl 文件网络位置 

- @param savePath 本地存储地址 */ 

onFileShareDl: (bIsOK: boolean, fileUrl: string, savePath: string) => void; } 

### **其他交互回调 InterActiveListener** 

export interface InterActiveListener{ /** * 点名 * @param time 点名时长 */ onRollCall:(time:number)=>void /** * 抽奖 * @param cmd * @param lotteryInfo 中奖信息,为中奖人信息 */ onLottery: (cmd: LotteryCMD, lotteryInfo: string) => void; } 

# **VOD SDK 使用文档** 

## **一、概述** 

**SDK 介绍** 

VodSDK 是专门为鸿蒙平台设计的音视频点播播放 SDK,用于实现展动平台点播内容的播放。适用于需要集成点播回放功能的各类鸿蒙应用,如在线教育等场景。 

### **特性列表** 

**点播在线播放** :在线播放展动平台的点播视频。 **点播离线下载** :离线下载、播放展动平台的视频。 **文档显示** :支持回看录制过程中展示文档资料。 **聊天历史** :支持回看历史聊天功能。 **问答历史** :支持回看历史问答功能。 

### **支持的环境** 

**操作系统** :HarmonyOS **编程语言** :ArkTS **最低版本要求** :5.0.1(13) **依赖项** : 

"@ohos/axios": "2.2.6" 需要添加到根目录或者是sdk同级目录的 oh-package.json5 中 

**依赖方式** : 

将 genseesdk.har 放到lib目录或者其他目录下,通过 file:路径/genseesdk.har 进行依赖。 示例: ts "dependencies": { "@gensee/playersdk": "file:libs/genseesdk.har" } 

## **二、快速开始** 

### **1. 引入 SDK** 

确保在项目中正确引入 @gensee/playersdk 模块,可通过如下方式引入: 

import { VodSDK } from '@gensee/playersdk' 

### **2. 初始化 SDK** 

在使用 VodSDK 之前,需要先进行初始化操作: 

const vodsdk = new VodSDK() vodsdk.init() 

### **3. 输入参数获取点播信息** 

##### // 创建初始化参数对象 

let initParam = new InitParam() // 设置域名或ip(必填) initParam.domain = this.vodDomin // 设置点播 ID(必填) initParam.number = this.vodId 

// 设置昵称(必填) 

initParam.nickName = this.nickname 

// 设置加入密码 

initParam.joinPwd = this.passcode // 设置traning或webcast initParam.serviceType = this.serviceType 

// 设置自定义用户ID 

initParam.userId = this.userId 

// 设置站点登录账号 

initParam.loginAccount = this.userAccountName 

// 设置站点登录密码 

initParam.loginPwd = this.userAccountPW // 设置认证 K 值 initParam.k = this.kValue 

// 设置用户自定义参数 initParam.userData = this.userExtraData 

// 使用初始化参数进行认证获取点播信息 

vodsdk.getVodObject(initParam).then((result:VodParam) => { 

// 认证成功,获取到点播信息 showToast("获取成功") 

}).catch((e: BusinessError | GSError) => { 

// 处理认证失败的情况 

if (e instanceof GSError) { showToast(e.errMsg) } else { showToast("未知错误:" + e.message) } }) 

### **4. 开始播放** 

先创建一个播放器对象,然后调用其 play 方法,示例如下: 

// 设置点播消息通知回调监听 

vodsdk.setVodListener(this.vodListener) // 创建一个player,用于视频的控制,需要传入获取到的点播信息 this.vodPlayer = vodsdk.createPlayer(getContext(), this.vodParam!) // 开始播放 this.vodPlayer.play() 

调用 play 方法后,SDK会自动开始下载、缓存点播视频,当一切就绪会回调 VodListener 的 onInit 方法,随后就会自动开始播放。 

## **三、各个模块及 API 使用** 

### **VODSDK 主功能** 

#### **1. 初始化** 

在使用 VODSDK 的所有功能之前,必须先调用此方法进行初始化,完成日志工具、环境的初始化以及启动心跳机制。 

const vodSDK = new VodSDK(); // 如需启动多个实例,则通过new VodSDK(true)创建SDK对象 vodSDK.init(); 

#### **2. 获取点播件完整信息** 

这是观看点播的第一步,根据提供的初始化参数,获取点播件的完整信息。 

```arkts
const initParam: InitParam = { // 初始化参数 }; try { 
```

const vodParam:VodParam = await vodSDK.getVodObject(initParam); console.log('获取到的点播参数:', vodParam); 

} catch (error) { if (error instanceof GSError) { console.error('获取点播信息失败:', error.errMsg); } } 

#### **3. 创建视频播放器对象** 

创建一个视频播放器对象,调用该播放器的 play 方法后,SDK就开始进行获取点播视频流程。后续对视频的暂停、播放、倍速、停止等方法均需要通 

VodPlayer 该类控制。 createPlayer 方法需要传入从 getVodObject 方法中获取的 VodParam 对象或者是离线下载后的 VodDownLoadEntity 对 象。如果传入的是 VodDownLoadEntity ,那么则是离线播放,过程不需要网络。 

**API** : 

/** 

* 创建视频播放器对象,在调用播放器的play后,点播相关的回调才会正常回调 

- @param context 

- @param vodparam 从getVodObject获取的对象 

- @param cacheDir 可选,指定的缓冲存放目录,默认在cache目录下 

- @returns */ 

createPlayer(context:Context,vodparam:VodParam,cacheDir:string = ""):VodPlayer 

示例: 

```arkts
const vodParam = await vodSDK.getVodObject(initParam); console.log('获取到的点播参数:', vodParam); try { 
const vodPlayer = vodSDK.createPlayer(context, vodParam); // 使用 vodPlayer 进行播放操作 } catch (error) { console.error('创建播放器失败:', error); } 
```

#### **4. 设置点播事件回调** 

设置用于处理点播事件的监听器,当发生初始化完成、视频桢回调、开始缓冲等事件,会调用监听器中的对应方法。 

```arkts
const myListener: VodListener = { onInit: (bHaveVideo, dwTotalLength) => { console.log('初始化完成'); } // 其他回调... }; vodSDK.setVodListener(myListener); 
```

#### **5. 绑定文档管理器** 

将文档视图的管理器与 SDK 绑定,绑定后文档才能在播放器中正常显示。 

const docManager = new DocManager(); vodSDK.bindDocManager(docManager); 

将创建的 docManager 传入到 DocView 中,SDK的文档数据便可传输到 DocView 中 

#### **6. 获取离线下载管理器对象** 

获取用于离线下载的管理器对象,离线下载、播放操作均通过该管理器进行。 

```arkts
const context = getContext(); try { const downloaderManager = await vodSDK.getDownloaderManager(context); // 使用 downloaderManager 进行下载操作 downloaderManager.startDownload(vodParam!).then(()=>{ // 已添加到下载队列 }) } catch (error) { console.error('获取下载管理器失败:', error); } 
```

#### **7. 获取交互相关的操作类** 

获取用于处理交互操作(如聊天、问答等)的操作类。 

const discussionApi = vodSDK.getDiscussionApi(); // 使用 discussionApi 进行交互操作 // 获取历史聊天 discussionApi.getChatHistory(vodParam,0) // 获取历史问答 discussionApi.getQAHistory(vodParam,0) 

#### **8. 释放 SDK** 

不用SDK时,需主动释放SDK所占用的资源,需要在每次退出点播的时候进行清理。清理后如果再次进入点播,不需要重新创建VodSDK对象,直接复用即可。 **如果 当前有正在进行中的下载任务,那么调用该方法也会停止下载任务。** 

vodsdk.releaseSDK() 

### **视频播放** 

#### **视频播放概述** 

视频播放我们提供了一个UI控件 VideoView ,直接将其添加到UI中,当有视频桢时即可自动绘制显示 

#### **实例代码** 

VideoView() .alignRules({ top: { anchor: 'title', align: VerticalAlign.Bottom }, middle: { anchor: '__container__', align: HorizontalAlign.Center } }) .id("Player") .width('100%') .height('500lpx') 

如果 VodSDK 以多实例模式启动,需要多个 VideoView 的情况,这种情况需要在 VideoView 中显式绑定 canvasId 参数,用于播放控件与 VodSDK 进行对 应, canvasId 需要从sdk中获取。 typescript VideoView({canvasId: vodsdk.canvasId}) .width('100%') .height('500lpx') 

### **视频播放控制** 

#### **概述** 

视频播放控制模块提供了一系列方法来控制视频的播放,包括开始播放、暂停、恢复、停止、设置播放速度、快进等功能。 VodPlayer 是通过 VodSDK 的 createPlayer 方式创建。 

#### **相关 API 使用** 

##### **设置视频播放器相关的监听** 

设置一个监听器,用于处理视频播放过程中的各种事件。 

```arkts
const listener: VodPlayerListener = { onPlayStop: () => { console.log('视频播放停止'); }, // 实现回调 }; vodPlayer.setListener(listener); 
```

##### **开始播放** 

##### 根据点播参数开始播放视频,可以选择纯音频播放模式。 

##### **API 方法** : 

/** * 开始播放 * @param isAudioOnly 纯音频播放 */ play(isAudioOnly: boolean = false) 

##### **参数说明** : 

isAudioOnly :类型为 boolean ,可选参数,默认为 false ,表示是否开启纯音频播放模式。 

##### **使用示例** : 

vodPlayer.play(); // 正常播放 vodPlayer.play(true); // 纯音频播放 

##### **暂停视频** 

##### 暂停正在播放的视频。 

```arkts
const isPaused = vodPlayer.pause(); if (isPaused) { console.log('视频已暂停'); } else { console.log('暂停失败'); } 
```

##### **从暂停状态中恢复播放** 

##### 恢复暂停的视频继续播放。 

```arkts
const isResumed = vodPlayer.resume(); if (isResumed) { console.log('视频已恢复播放'); } else { console.log('恢复播放失败'); } 
```

##### **停止播放** 

##### 停止正在播放的视频 

vodPlayer.stop(); 

##### **3.4 设置倍速播放** 

设置视频的播放速度。 

##### **API 方法** : 

/** * 设置倍速播放 * @param speed 播放速率 */ setSpeed(speed: PlaySpeed) 

##### **参数说明** : 

speed :类型为 PlaySpeed ,表示播放速率。 

##### **使用示例** : 

vodPlayer.setSpeed(PlaySpeed.SPEED_200); // 设置为 2 倍速播放 

##### **快进到某个时间点** 

将视频快进到指定的时间点。 

**API 方法** : 

/** * 快进到某个时间点 * @param timestamp 单位:毫秒 */ seekTo(timestamp: number) 

##### **参数说明** : 

timestamp :单位:毫秒,表示要快进的时间点。 

**返回值** :无 **使用示例** : 

const timestamp = 60000; // 快进到 60000 毫秒处 vodPlayer.seekTo(timestamp); 

##### **静音视频** 

将视频静音。 

vodPlayer.mute(); 

##### **取消静音** 

取消视频的静音状态。 

vodPlayer.unmute(); 

### **文档** 

#### **文档模块概述** 

为了方便客户使用,我们直接封装了一个 DocView 用于显示文档,在创建 DocView 的时候需要传入一个 DocManager 对象,并且这个对象需要一并设置给 VodSDK,这样即可实现文档的显示。 

#### **相关 API 使用** 

##### **绑定文档管理器** 

通过 vodsdk.bindDocManager 方法将文档管理器与 vodsdk 进行绑定,确保文档能够正常显示。 

private docManager = new DocManager() vodsdk.bindDocManager(this.docManager) 

##### **显示文档视图** 

在UI组件中,使用 DocView 组件来显示文档。 

TabContent() { // 父控件随意,这里只是演示 DocView({manager:this.docManager}) .width('100%') .height('100%') } .tabBar('文档') 

**参数说明** : - manager : DocManager 类型的实例,用于管理文档的显示和切换。 

### **互动聊天** 

#### **概述** 

互动聊天模块提供了获取点播中聊天消息和问答列表的功能,包括在线点播的聊天历史和离线下载点播件的聊天信息。 

#### **相关 API 使用** 

##### **获取点播中全部的聊天消息** 

根据提供的点播信息和页码,获取指定页的聊天历史记录。 

##### **API 方法** : 

/** 

##### * 获取点播中全部的聊天消息 

* @param vodParam 点播信息 

* @param pageIndex 第几页 

* @returns 获取到的聊天信息 

*/ 

getChatHistory(vodParam: VodParam, pageIndex: number): Promise<VodChatMsg[]> 

##### **返回值** : 

成功时返回一个 VodChatMsg 数组,包含获取到的聊天信息;失败时抛出相应的错误。 

##### **使用示例** : 

```arkts
const discussionApi = vodSDK.getDiscussionApi(); const pageIndex = 1; discussionApi.getChatHistory(vodParam, pageIndex) .then((chatMessages) => { console.log('获取到的聊天消息:', chatMessages); }) .catch((error) => { console.error('获取聊天消息失败:', error); }); 
```

##### **获取离线下载的点播件的聊天信息** 

该方法用于获取离线下载后的点播中的聊天历史记录。在离线下载成功后,可以无网络使用。 

**API 方法** : 

/** * 获取离线下载的点播件的聊天信息 

* @param entity 离线下载的点播信息 

* @returns */ getOfflineChatHistory(entity: VodDownLoadEntity): Promise<VodChatMsg[]> 

##### **参数说明** : 

entity :类型为 VodDownLoadEntity ,包含了离线下载的点播相关信息。 

##### **返回值** : 

成功时返回一个 VodChatMsg 数组,包含获取到的聊天信息;失败时抛出相应的错误。 

##### **使用示例** : 

const discussionApi = vodSDK.getDiscussionApi(); let entitys = await downloadM.getDownloadList() 

// 例子中就已下载列表第一个点播为例,但是这里其实要判断该点播件是否下载完成,可能处于下载中的状态 discussionApi.getOfflineChatHistory(entitys[0]) 

.then((chatMessages) => { console.log('获取到的离线聊天消息:', chatMessages); }) .catch((error) => { console.error('获取离线聊天消息失败:', error); }); 

##### **获取点播中的问答列表** 

根据提供的点播信息和页码,获取指定页的问答历史记录。 离线点播也需要通过这个方法进行获取问答信息,此方法必须 **联网获取** 。 

**API 方法** : 

/** * 获取点播中的问答列表 

* @param vodParam * @param pageIndex * @returns */ getQAHistory(vodParam: VodParam, pageIndex: number): Promise<VodQaMsgResult> 

##### **参数说明** : 

vodParam :类型为 VodParam ,点播信息。 pageIndex :类型为 number ,要获取的页码。 

##### **返回值** : 

成功时返回一个 VodQaMsgResult 对象,其中包含 QaMsg 数组,包含获取到的问答信息;失败时抛出相应的错误。 

export class VodQaMsgResult{ /** * 当前页码 */ pageIndex:number = 0 /** * 问答数据 */ msgList:QaMsg[] = [] /** * 是否有更多的问答数据 */ isMore:boolean = false } 

##### **使用示例** : 

```arkts
const discussionApi = vodSDK.getDiscussionApi(); const pageIndex = 1; discussionApi.getQAHistory(vodParam, pageIndex) .then((result) => { console.log('获取到的问答消息:', result.msgList); }) .catch((error) => { console.error('获取问答消息失败:', error); }); 
```

### **离线下载** 

#### **概述** 

离线下载模块提供了用于管理和控制点播视频的离线下载任务,包括开始下载、停止下载、删除下载任务等操作。 

#### **API 列表** 

##### **获取下载的 vod 列表** 

根据用户 ID 获取下载的 vod 列表。如果传入指定的用户 ID,则只会返回该用户 ID 的下载数据;若不传入,则返回所有下载数据。 用户ID的作用是用于区分可能存在 的相同设备多账号登录的情况,如不考虑多账号登录的情况,那么不需要传入userID 

const downloadList = downloaderManager.getDownloadList("user123"); 

##### **开始下载** 

根据传入的 VodParam 开始下载任务。如果当前已有下载任务,新任务将被加入未下载队列;如果没有当前任务,则开始下载新任务。 

await downloaderManager.startDownload(vodParam); 

##### **停止下载** 

停止所有下载任务,包括当前正在下载的任务和未下载队列中的任务。 

downloaderManager.stopDownload(); 

##### **删除 vod 下载任务** 

删除指定的 vod 下载任务。如果该任务正在下载,会先停止下载。 

const vodEntity: VodDownLoadEntity = xxx; downloaderManager.deleteVod(vodEntity); 

##### **更改下载目录** 

如果想特殊指定点播的下载地址,那么更改点播下载后的存储位置,需要在 startDownload 前调用。 

downloaderManager.changeDownloadDir("/new/download/dir"); 

##### **设置下载监听器** 

设置一个监听器,用于处理下载过程中的各种事件,如准备下载、开始下载、下载完成、下载停止等。 

```arkts
const listener: DownloaderListener = { onDownloadPrepare: (downloadEntity) => { console.log('下载准备:', downloadEntity); }, // 实现其他监听器方法 }; downloaderManager.setDownloadListener(listener); 
```

## **四、各个回调监听说明** 

### **核心监听 VodListener** 

export interface VodListener { 

|/** *初始化完成 |
|---|
|* @param haveVideo是否有视频 |
|* @param duration点播时长|
|*/|
|onInit : (haveVideo: boolean, duration: number) => void|
|/**|
|*点播同步的聊天消息|
|*聊天消息会依据其发送时间,在视频播放进度播放至对应时刻时触发该调用。|
|* @param chatMsgs聊天消息列表|
|*/|
|onChat:(chatMsg: ChatMsg)=> void;|
|/**|
|*文档章节信息更新|
|* @param list章节列表,等同于onInit返回的docInfos|
|*/|
|onDocInfo:(list: Array<DocInfo>) => void;|
|/**|
|*点播广播消息回调 * @param bcMsgs广播消息列表 |
|*/ |
|onBroadCastMsg:(msg: string,msgId:string,sender:string,timestamp:number)=> void;|
|/**|
|*播放器布局设置 |
|* @param timeStamp时间戳|
|* @param layout布局类型|
|*/|
|onLayoutSet:(timeStamp: number, layout: number)=> void;|
|/**|
|*录制信息回调|
|* @param startTime点播录制的实际时间|
|* @param storage点播占用存储大小,单位Byte|
|* @param duration点播总时长,单位毫秒|
|*/|
|onRecordInfo:(startTime: number, storage: number, duration: number)=> void;|
|/**|
|*播放错误|
|* @param errCode错误码|
|*/|
|onError:(errCode: ErrCode)=> void;|
|}|

**播放相关回调 VodPlayerListener** 

export interface VodPlayerListener{ /** * 播放完成停止通知 */ onPlayStop:() => void; /** * 暂停通知 */ onPlayPause:() => void; /** * 恢复通知 */ onPlayResume:() => void; /** * 进度通知 * @param position 当前播放进度 */ onPosition:(position: number) => void; /** * 视频分辨率变化通知 * @param position 当前播放进度 * @param videoWidth 变化后的视频宽 * @param videoHeight 变化后的视频高 */ onVideoSize:(position: number, videoWidth: number, videoHeight: number) => void; /** * 任意位置定位播放响应 * @param position 快进、快退或拖动后的播放进度 */ onSeek:(position: number) => void; /** * 音频电平值 * @param level 电平大小 */ onAudioLevel:(level: number)=> void; /** * 缓冲状态 * @param isCaching true表示正在缓冲,false表示缓冲完成 */ onCaching:(isCaching: boolean)=> void; /** * 视频开始播放 */ onVideoStart:()=> void; /** * 视频播放结束 */ onVideoEnd:()=> void; } 

### **下载相关的回调 DownloaderListener** 

export interface DownloaderListener{ /** * 准备开始下载,已经加入到了下载队列 * @param vodId */ onDownloadPrepare:(downloadEntity:VodDownLoadEntity)=>void /** * 已经获取到点播的信息 * @param vodId */ onRecordInfo:(downloadEntity:VodDownLoadEntity)=>void /** * 开始下载 * @param downloadEntity */ onDownloadStart:(downloadEntity:VodDownLoadEntity)=>void /** * 下载暂停 * @param downloadEntity */ onDownloadStop:(downloadEntity:VodDownLoadEntity)=>void /** * 下载结束 * @param downloadEntity */ onDownloadFinish:(downloadEntity:VodDownLoadEntity)=>void /** * 下载发生错误 * @param downloadEntity * @param errorCode 错误码 * @param errorMsg 错误信息 */ onError:(downloadEntity:VodDownLoadEntity,errorCode:number,errorMsg:string)=>void /** * 下载中 * @param downloadEntity * @param percent 下载进度0~100 */ onDownloading:(downloadEntity:VodDownLoadEntity,percent:number)=>void }
