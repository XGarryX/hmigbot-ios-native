# 接口文档 **IM SDK for HarmonyOS** 

## **IMSDK** 简介 

### **1.** 功能目标 

开发者在成功接入 IMSDK 后,无需部署任何服务器即可拥有双人及多人的即时通讯能力。 

### **2.SDK** 目录讲解 

库 

`@youme/im` 包含了必须的接口和 so 库,请导入 HarmonyOS 工程。 

### **3.** 关键类及描述 

#### YIMClient 

`IM SDK` 引擎服务类 `,` 单例模式。该类提供 `SDK` 操作的相关方法 `,` 例如 `:` 初始化,登录,登出,消 息发送等。 

#### YIMObserver 

观察者类,监听 `IM` 被动收到的消息,例如收到文本语音消息、他人进出房间等。 

#### YIMDe�ne 

`IM` 类型定义的命名空间,用法例如: `YIMDefine.YIMErrorcode` 或者 

```
YIMDefine.YIMChatType.ChatType_PrivateChat
```

#### YIMMessage 

消息类的命名空间,用法例如: `YIMMessage.Msg` 

#### YIMMessage.Msg 

`IM` 消息类,包含消息体和消息基本属性:例如消息 `ID` ,消息类型,发送者 `ID` ,接收者 `ID` 等信 息。 

YIMMessage.BodyBase 

Page 1 of 37 

`IM` 消息体基类 

#### YIMMessage.BodyAudio 

- `IM` 语音消息类,包含语音消息除基本属性外的其它信息:例如语音时长,语音本地存放地址, 

- 语音文件大小等信息。 

#### YIMMessage.BodyText 

- `IM` 文本消息类,包含文本消息除基本属性外的其它信息:文本内容。 

#### YIMMessage.BodyCustom 

- `IM` 自定义消息类,包含自定义消息除基本属性外的其它信息:自定义消息内容。 

#### YIMMessage.BodyFile 

- `IM` 文件消息类,包含文件消息除基本属性外的其它信息:文件名,文件大小,文件类型,文件 

- 扩展信息等。 

#### YIMMessage.BodyGift 

- `IM` 礼物消息类,包含礼物消息除基本属性外的其它信息:礼物 `ID` ,礼物数量,主播 `ID` ,礼物信 

- 息。 

### **4.** 消息类型定义 

`//` 消息类型 

```
export enum YIMMessageBodyType
  {
```

`MessageBodyType_Unknow = 0, MessageBodyType_TXT = 1, //` 文本消息 `MessageBodyType_CustomMesssage = 2, MessageBodyType_Emoji = 3, MessageBodyType_Image = 4, MessageBodyType_Voice = 5, //` 语音消息 `MessageBodyType_Video = 6, MessageBodyType_File = 7, MessageBodyType_Gift = 8 }` 

### **5.** 聊天类型定义 

Page 2 of 37 

`export enum YIMChatType { ChatType_Unknow = 0, ChatType_PrivateChat = 1, //` 私聊 `ChatType_RoomChat = 2, //` 聊天室 `ChatType_Multi = 3, }` 

## **IMSDK** 操作指引 

### 申请使用游密 **IM** 引擎 **SDK** 

- 首先请与游密商务联系,提供公司名称、游戏的名称、联系人电话、邮箱、 QQ 等以申请 IM 引擎 的使用权限。审批通过后会得到有效的 AppKey 和 AppSecret ,这些信息属于私密信息,请妥善保 管。 

#### **3.** 导人 **SDK** 

在模块的 oh-package.json5 中 dependencies 增加 har 包依赖,配置如下: 

```
"dependencies": {
  "@youme/im": "3.0.11"
}
```

依赖设置完成后,需要执行 `ohpm install` 命令安装依赖包,依赖包会安装在该模块的 oh_modules 目录下。 

#### **4.** 权限配置 

在模块的 module.json5 中 requestPermissions 添加网络和麦克风权限,配置如下: 

```
"requestPermissions": [
  {
    "name": "ohos.permission.INTERNET",
  },
  {
    "name": "ohos.permission.MICROPHONE",
    "reason": "$string:mic_reason",
    "usedScene": {
      "abilities": [
```

Page 3 of 37 

```
        "FormAbility"
      ],
      "when": "inuse"
    }
  }
```

#### **5.** 使用 **Native C++** 接口 

har 包安装在该模块的 oh_modules 目录,目录下有提供 Native C++ 的 include 头文件 和 so 库文件。 若要使用 Native C++ 接口,可以再 CMake 里配置使用。 C++ 接口 API 说明书请参考 IM SDK for C++ 使用指南 

`#CMakeLists.txt` 示例 

#### `#` 包含 `include` 目录 

`include_directories(${CMAKE_CURRENT_SOURCE_DIR}/../../../oh_modules/@youm #` 包含 `so` 的目录 

`link_directories("../../../oh_modules/@youme/im/libs/${OHOS_ARCH}") #` 把 `libyim.so` 添加到链接库里 

```
target_link_libraries(entry PUBLIC libace_napi.z.so libhilog_ndk.z.so lib
```

`//papi_init.cpp` 引用示例 

```
#include "YIM.h"
#include "YIMPlatformDefine.h"
...
```

`//` 使用 `C++` 回调接口 `IYIMLoginCallback class CNAPICallback: public IYIMLoginCallback { public: /*` 

`*` 功能:登录回调 

`* @param errorcode` :错误码 

`* @param userID` :用户 `ID */` 

```
virtual void OnLogin(YIMErrorcode errorcode, const XCHAR * userID) {
        OH_LOG_INFO(LOG_APP, "login with code %d", errorcode);
        if(errorcode == YIMErrorcode_Success) {
            YIMManager::CreateInstance()->GetChatRoomManager()->JoinChatR
        }
    }
```

Page 4 of 37 

```
};
...
```

`//` 使用 `YIMManager` 主接口 

```
    XString ver = YIMManager::CreateInstance()->GetSDKVersion();
    static auto cb = new CNAPICallback;
    YIMManager::CreateInstance()->SetLoginCallback(cb);
    YIMManager::CreateInstance()->SetServerZone(ServerZone_China);
    auto code = YIMManager::CreateInstance()->Init(APP_KEY, APP_SECRET, "
```

### **import** 接口和定义 

```
import { YIMClient, YIMObserver, YIMDefine, YIMMessage } from '@youme/im'
```

### 初始化 **SDK** 

功能: 初始化 IM SDK 。 

#### 原型: 

- `/**` 

- 初始化 `IM` 引擎 

- `@param appKey` 申请的 `appkey` 

- `@param appSecret` 申请得到的 `secretKey` 

- `@param serverZone IM` 服务器区域 

- `@param packageName` 所属包 

- `@param sdkValidDomain` 指定 `sdk` 验证服务域名 

- `@param drDomain` 指定 `dr` 上报服务域名 

- `@param sdkValidBackupip` 指定 `sdk` 验证备用服务域名 

- `@param drBackupip` 指定 `dr` 上报备用服务域名 

```
   */
init(appKey:string, appSecret:string, serverZone: YIMDefine.YIMServerZo
```

#### 返回: 

错误码,详细描述见错误码定义。 

备注: 该方法必须在调用其它 SDK API 之前调用。 

Page 5 of 37 

IM 引擎底层对于耗时操作都采用异步回调的方式,函数调用会立即返回。因此,用户须实现 YIMObserver 观察者接口中感兴趣的消息通知,并在初始化完成以后注册到 YIMClient 。 

设置监听示例:添加一个观察者 

`observer: YIMObserver = new YIMObserver(); ... this.observer .onReceiveMessage((msg: YIMMessage.Msg) => { //` 接收文本语音消息 `}) .onReceiveMessageNotify((chatType: YIMDefine.YIMChatType, targetID: //` 新消息通知(默认自动接收消息,只有调用 `SetReceiveMessageSwitch` 设置为不自 `}) .onOtherJoinRoom((room, user) => { //` 他人进入房间 `}) .onOtherLeaveRoom((room, user) => { //` 他人离开房间 `}) .onUpdateReadStatus((recvID: string, chatType: number, msgSerial: b //` 消息已读通知 `}) .onKickOff(() => { //` 被踢出房间 `}) .onStartReconnect(() => { //` 开始重连 `}) .onRecvReconnectResult((result: number) => { //` 重连结果 `})` 

```
    YIMClient.getInstance().addObserver(this.observer);
```

添加移除观察者 

Page 6 of 37 

`/** *` 注册一个回调观察者 `* @param observer YIMObserver` 类型的观察者对象 `*/ addObserver(observer: YIMObserver) /** *` 卸载一个回调观察者 `* @param observer YIMObserver` 类型的观察者对象 `*/ deleteObserver(observer: YIMObserver)` 

`/** *` 开始重连回调类型 `* @return */ export type funcOnStartReconnect = () => void /** *` 重连结果通知回调类型 `* @param result` 错误码 `*/ export type funcOnRecvReconnectResult = (result: YIMDefine.YIMErrorcode) /** *` 监听开始重连事件 `* @param callback ()=>void */ onStartReconnect(callback: funcOnStartReconnect) : YIMObserver /** *` 监听重连结果返回事件 `* @param callback ()=>void */` 

```
onRecvReconnectResult(callback: funcOnRecvReconnectResult) : YIMObserve
```

Page 7 of 37 

```
/**
```

`*` 他人加入聊天室回调类型 `* @param room` 频道 `/` 房间 `ID * @param user` 加入用户 `id */ export type funcOnOtherJoinRoom = ( room: string, user: string) => void /** *` 他人离开聊天室回调类型 `* @param room` 频道 `/` 房间 `ID * @param user` 离开用户 `id */ export type funcOnOtherLeaveRoom = ( room: string, user: string) => void /** *` 监听他人加入房间事件 `* @param callback  (room: string, user: string) => void */ onOtherJoinRoom(callback: funcOnOtherJoinRoom) : YIMObserver- /** *` 监听他人离开房间事件 `* @param callback  (room: string, user: string) => void */ onOtherLeaveRoom(callback: funcOnOtherLeaveRoom) : YIMObserver` 

`/** *` 被踢出房间回调类型 `* @return */ export type funcOnKickOff = ()=>void /** *` 监听被踢出房间事件 `* @param callback ()=>void` 

Page 8 of 37 

```
   */
onKickOff(callback: funcOnKickOff) : YIMObserver
```

- `/*` 

#### `*` 接收消息回调类型 

- `@param message` 接收消息类 `YIMMessage.Msg` 

- `*/` 

- `/**` 

- `Msg` 接收消息类 

- `@class Msg` 

- `@property msgId` 消息 `ID` 

- `@property chatType` 谈话类型 `: ChatType_PrivateChat = 1, //` 私聊 `ChatType_Ro` 

- `@property msgType` 消息类型 `: MessageBodyType_TXT = 1,//` 文本 `MessageBodyTyp` 

- `@property sender` 发送人 

- `@property receiver` 接收者 `(` 聊天室:频道 `ID)` 

- `@property createTime` 发送时间 

- `@property isRead` 消息是否已读 

- `@property distance` 距离 

- `@property body` 消息体,具体的消息内容 

- `*/` 

```
export type funcOnReceiveMessage= (message: YIMMessage.Msg) =>void
onReceiveMessage(callback: funcOnReceiveMessage) : YIMObserver
/**
```

- 新消息通知(默认自动接收消息,只有调用 `SetReceiveMessageSwitch` 设置为不自动接收消 

- `@param chatType` 聊天类型 `YIMDefine.YIMChatType` 

- `@param targetID` 房间或用户 `ID` 

- `*/` 

```
export type funcOnReceiveMessageNotify= (chatType: YIMDefine.YIMChatType
```

#### 设置消息已读回调方法: 

Page 9 of 37 

```
/*
```

#### `*` 接收端消息已读回调类型,更新发送端消息显示状态 

`* @param recvId` 接收端用户 `Id` 

`* @param chatType` 聊天类型 

`* @param msgSerial` 最新一条已读消息的消息 `Id` 

```
  */
export type funcOnUpdateReadStatus= (
recvID: string,
chatType: YIMDefine.YIMChatType,
msgSerial: bigint) =>void
/**
```

`*` 监听消息已读通知事件 

```
   * @param callback  (recvID: string, chatType: YIMDefine.YIMChatType, m
   */
onUpdateReadStatus(callback: funcOnUpdateReadStatus) : YIMObserver
```

#### 备注: 该回调接口不设置,则消息已读未读功能不生效。 

- 功能: 指定用户 ID 登录 IM 系统 , 登录为异步过程,通过回调参数返回是否成功,成功后方能进行 后续操作。 

原型: 

```
/**
```

- 登录 `IM` 

- `@param user` 用户 `ID` ,由调用者分配,不可为空字符串,只可由字母或数字或下划线组成 

- `@param password` 用户密码,不可为空字符串,如无特殊要求可以设置为固定字符串 

- `@param token` 登录 `token` ,使用服务器 `token` 验证模式时使用,如不使用 `token` 验证传入 

- `@param callback` 登录回调原型 `(errCode: YIMDefine.YIMErrorcode, user: s` 

- `@param callback` 参数 `errCode` 错误码 

- `@param callback` 参数 `user` 用户 `ID */` 

```
login(user: string, password:string, token: string, callback: (errCode:
```

Page 10 of 37 

功能: 登出游密 IM 云服务器,这是一个异步操作,操作结果会通过回调参数返回。 原型: 

`/** *` 登出 `IM * @param callback` 登出回调 `,` 参数 `errCode` 错误码 `*/` 

```
logout(callback: (errCode: YIMDefine.YIMErrorcode)  =>void) : YIMDefin
```

同一个用户 ID 在多台设备上登录时,后登录的会把先登录的踢下线,收到 onKickOff() 通知。 

原型 

```
/**
```

- 监听被踢出房间事件 

```
   * @param callback ()=>void
   */
onKickOff(callback: funcOnKickOff) : YIMObserver
```

功能: 加入聊天频道进行群组聊天,这是一个异步操作,操作结果会通过回调参数返回。 原型: 

```
/**
```

- 加入聊天室 

`* @param room` 频道 `ID` ,由调用者定义,如果频道不存在则后台自动创建,仅支持数字、字母 

`* @param callback` 加入频道回调 

`* @param callback` 参数 `errCode` 错误码 

`* @param callback` 参数 `room` 频道 `ID */` 

```
joinChatRoom(room: string, callback: (errCode: YIMDefine.YIMErrorcode,
```

Page 11 of 37 

功能: 退出聊天频道,这是一个异步操作,操作结果会通过回调参数返回。 原型: 

`/** *` 退出聊天室 `* @param room` 频道 `ID * @param callback` 退出频道回调 `* @param callback` 参数 `errCode` 错误码 `* @param callback` 参数 `room` 频道 `ID */` 

```
leaveChatRoom(room: string, callback: (errCode: YIMDefine.YIMErrorcode,
```

功能: 离开所有频道,这是一个异步操作,操作结果会通过回调参数返回。 原型: 

`/** *` 离开所有频道 `* @param callback` 离开所有频道回调 `* @param callback` 参数 `errCode` 错误码 `*/` 

```
leaveAllChatRooms(callback: (errCode: YIMDefine.YIMErrorcode)=>void) :
```

此功能默认不开启,需要的请联系我们开启此服务。联系我们,可以通过专属游密支持群或者技术支 持的大群。 

```
/**
```

`*` 他人加入聊天室回调类型 

`* @param room` 频道 `/` 房间 `ID * @param user` 加入用户 `id */ export type funcOnOtherJoinRoom = ( room: string, user: string) => void` 

```
/**
```

`*` 他人离开聊天室回调类型 

`* @param room` 频道 `/` 房间 `ID` 

Page 12 of 37 

`* @param user` 离开用户 `id */ export type funcOnOtherLeaveRoom = ( room: string, user: string) => void /** *` 监听他人加入房间事件 `* @param callback  (room: string, user: string) => void */ onOtherJoinRoom(callback: funcOnOtherJoinRoom) : YIMObserver - /** *` 监听他人离开房间事件 `* @param callback  (room: string, user: string) => void */ onOtherLeaveRoom(callback: funcOnOtherLeaveRoom) : YIMObserver` 

这是一个异步操作,操作结果会通过回调参数返回。 

原型: 

```
/**
```

- 功能:获取频道 `/` 房间成员数量 

- `@param room` :频道 `/` 房间 `ID(` 已成功加入此频道才能获取该频道的人数 `)` 

- `@param callback` 获取频道 `/` 房间成员数量回调 

`* @param callback` 参数 `errCode` 错误码 

- `@param callback` 参数 `room` 频道成 `/` 房间 `ID` 

- `@param callback` 参数 `count` 频道 `/` 房间成员数量 `*/` 

```
getRoomMemberCount(room: string, callback:  (errCode: YIMDefine.YIMErro
```

备注: 

`room` : 频道 ID , string 类型。 `count` : 频道内成员数量, number 类型。 

游密 IM 可以进行多种消息类型的交互,比如文本,自定义,表情,图片,语音,文件,礼物等。 

Page 13 of 37 

功能: 消息接收采用异步回调的方式,在 YIMObserver 接口中的 onReceiveMessage 中处理。 

```
/*
```

#### `*` 接收消息回调类型 

- `@param message` 接收消息类 `YIMMessage.Msg` 

- `*/` 

```
/**
```

`* Msg` 接收消息类 

- `@class Msg` 

- `@property msgId` 消息 `ID` 

`* @property chatType` 谈话类型 `: ChatType_PrivateChat = 1, //` 私聊 `ChatType_Ro` 

- `@property msgType` 消息类型 `: MessageBodyType_TXT = 1,//` 文本 `MessageBodyTyp` 

- `@property sender` 发送人 

- `@property receiver` 接收者 `(` 聊天室:频道 `ID)` 

- `@property createTime` 发送时间 

- `@property isRead` 消息是否已读 

- `@property distance` 距离 

- `@property body` 消息体,具体的消息内容 

- `*/` 

```
/**
```

- 文本消息体 

- `@class BodyText` 

- `@property content` 消息内容 

- `@property attach` 发送文本附加信息( `SendTextMessage` 传入,格式及如何解析由调用方 

- `*/` 

- `/**` 

#### `*` 语音消息体 

- `@class BodyAudio` 

- `@property audioTime` 语音时长(单位:秒) 

- `@property text` 语音翻译文字 

- `@property fileSize` 语音大小(单位:字节) 

- `@property extra` 

- `@property localPath` 

- `@property isPlayed` 

- `*/` 

- `/**` 

#### `*` 自定义消息体 

- `@class BodyCustom` 

- `@property custom` 消息内容 

Page 14 of 37 

```
 */
/**
```

#### `*` 文件消息体 

- `@class BodyFile` 

- `@property fileName` 原文件名 

- `@property fileExtension` 文件扩展名 

- `@property fileSize` 文件大小(单位:字节) 

- `@property extra` 发送文件附加信息( `SendFile` 传入,格式及如何解析由调用方自定) 

- `@property localPath` 文件路径 

- `@property fileType` 文件类型 

- `*/` 

- `/**` 

#### `*` 礼物消息体 

- `@class BodyGift` 

- `@property giftID` 礼物 `ID` 

- `@property giftCount` 数量 

- `@property anchor` 主播 

- `@property extra` 附加信息 

```
  */
```

- `/**` 

#### `*` 礼物附加信息 

- `@class YIMExtraGifParam` 

- `@property nickname` 昵称 

- `@property server_area` 区服 

- `@property location` 位置 

- `@property score` 积分 

- `@property level` 等级 

- `@property vip_level VIP` 等级 

- `@property extra` 附加参数 

- `*/` 

```
export type funcOnReceiveMessage= (message: YIMMessage.Msg) =>void
onReceiveMessage(callback: funcOnReceiveMessage) : YIMObserver
```

#### 示例: 

```
this.observer
onReceiveMessage(msg: YIMMessage.Msg) => {
```

- `if (msg.msgType == YIMDefine.YIMMessageBodyType.MessageBodyType_T` 

`//` 文本消息 

```
let body = msg.body as YIMMessage.BodyText;
```

Page 15 of 37 

`hilog.info(0x0000, 'YOUMEIM_DEMO_UI', `callback:text messege co } else if (msg.msgType == YIMDefine.YIMMessageBodyType.MessageBod //` 语音消息 `YIMClient.getInstance().downloadFile(msg.msgId, "", (errCode: Y if (errCode == YIMDefine.YIMErrorcode.YIMErrorcode_Success) { let body = msg.body as YIMMessage.BodyAudio; ... } }); } else { ... } })` 

- 功能: 发送文本消息到指定接收者,这是一个异步操作,操作结果会通过回调参数返回。 

- 原型: 

```
/**
```

- 发送文本消息 

- `@param receiver` 消息接收者 `ID` 

- `@param chatType` 聊天类型 `: ChatType_PrivateChat = 1, //` 私聊 `ChatType_Ro` 

- `@param msg` 消息内容 

- `@param callback` 函数原型 `funcOnSendMessage (reqId: bigint, errCode: YIM` 

- `reasonType: number, forbidEndTime: number, msgId: bigint) => void` 

- `@param callback` 参数 `reqId` 请求 `ID` (与 `SendXXMessage` 发送消息的输出参数 `request` 

- `@param callback` 参数 `errCode` 错误码 

- `@param callback` 参数 `sendTime` 发送时间戳,精确到毫秒 

- `@param callback` 参数 `isForbidRoom` 是否被禁言 

- `@param callback` 参数 `reasonType` 禁言原因 `, 0-` 未知, `1-` 发广告, `2-` 侮辱, `3-` 政治敏 

- `@param callback` 参数 `forbidEndTime` 禁言结束时间 

- `@param callback` 参数 `msgId` 消息 `ID` 

- `@return [YIMDefine.YIMErrorcode` 错误码 `, bigint` 请求 `ID]` 

- `*/` 

```
sendTextMessage(receiver: string, chatType: number, msg: string, param:
callback: funcOnSendMessage) : [YIMDefine.YIMErrorcode, bigint]
```

Page 16 of 37 

功能: 接收端用户查看聊天框信息后,给发送端确认消息已读,调用此接口。接收端给发送端 发送已读状态信息后,发送端会收到 onUpdateReadStatus 回调。 

原型: 

- `/**` 

#### `*` 通知对端消息已读 

- `@param receiver` 对端发送消息的 `userId` 

- `@param chatType` 聊天类型,详见 `ChatType` 

- `@param messageID` 最新消息的 `msgId` 

- `*/` 

```
sendMessageReadStatus(receiver: string, chatType: YIMDefine.YIMChatType
```

注意: receiver 需要注意下,是发送被标记为已读消息的用户 Id ,而并非调用此接口的用户 Id 。 messageID 表示接收到最新一条消息的 messageID ,有可能发送端发过来的消息有多条。确认消 息已读,接收端只给发送端发送最新一条消息的 messageID 为已读。 

功能: 用于群发文本消息的接口,每次不要超过 **200** 个用户。 

原型: 

```
/**
```

- 功能:群发文本消息 

- `@param receivers` :接收方 `ID` 列表 

- `@param text` :消息内容 

- `@return` 错误码 

```
  */
multiSendTextMessage(receivers: Array<string>, msg: string) : YIMDefi
```

#### 返回: 

#### 错误码,详细描述见错误码定义。 

功能: 给主播发送礼物消息的接口,支持在游密主播后台查看礼物消息信息和统计信息。客户 端还是通过 `onReceiveMessage` 接收消息。 `giftID` 为 `0` 可以表示普通的主播留言。 原型: 

```
/**
```

`*` 发送礼物 

Page 17 of 37 

- `@param anchor` :游密后台设置的对应的主播游戏 `id` 

- `@param channel` :主播频道 `ID` ,通过 ``JoinChatRoom`` 进入频道的用户可以接收到消息。 

- `@param giftID` :礼物物品 `ID` ,特别的是 ``0`` 表示只是留言 

- `@param giftCount` :礼物数量 

- `@param extraParam` :附加参数(格式为 `json {"nickname":"` 昵称 `","server_area"` 

- `@param callback` 函数原型 `funcOnSendMessage (reqId: bigint, errCode: YIM` 

- `reasonType: number, forbidEndTime: number, msgId: bigint) => void` 

- `@param callback` 参数 `reqId` 请求 `ID` (与 `SendXXMessage` 发送消息的输出参数 `reques` 

- `@param callback` 参数 `errCode` 错误码 

- `@param callback` 参数 `sendTime` 发送时间戳,精确到毫秒 

- `@param callback` 参数 `isForbidRoom` 是否被禁言 

- `@param callback` 参数 `reasonType` 禁言原因 `, 0-` 未知, `1-` 发广告, `2-` 侮辱, `3-` 政治敏 

- `@param callback` 参数 `forbidEndTime` 禁言结束时间 

- `@param callback` 参数 `msgId` 消息 `ID` 

- `@return [YIMDefine.YIMErrorcode` 错误码 `, bigint` 请求 `ID]` 

- `*/` 

```
sendGift(anchor: string, channel: string, giftID: number, giftCount:
callback: funcOnSendMessage): [YIMDefine.YIMErrorcode, bigint]
```

   - 功能: 发送用户自定义消息,自定义数据是二进制数据。异步返回结果通过回调参数返回。 原型: 

- `/**` 

#### `*` 发送自定义消息 

- `@param receiver` :接收方 `ID` 

- `@param chatType` :聊天类型 `: ChatType_PrivateChat = 1, //` 私聊 `ChatType_Ro` 

- `@param data` :消息内容 

- `@param callback` 函数原型 `funcOnSendMessage (reqId: bigint, errCode: YIM` 

- `reasonType: number, forbidEndTime: number, msgId: bigint) => void` 

- `@param callback` 参数 `reqId` 请求 `ID` (与 `SendXXMessage` 发送消息的输出参数 `reques` 

- `@param callback` 参数 `errCode` 错误码 

- `@param callback` 参数 `sendTime` 发送时间戳,精确到毫秒 

- `@param callback` 参数 `isForbidRoom` 是否被禁言 

- `@param callback` 参数 `reasonType` 禁言原因 `, 0-` 未知, `1-` 发广告, `2-` 侮辱, `3-` 政治敏 

- `@param callback` 参数 `forbidEndTime` 禁言结束时间 

- `@param callback` 参数 `msgId` 消息 `ID` 

- `@return [YIMDefine.YIMErrorcode` 错误码 `, bigint` 请求 `ID]` 

- `*/` 

```
sendCustomMessage(recerver: string, chatType: YIMDefine.YIMChatType, da
callback: funcOnSendMessage) : [YIMDefine.YIMErrorcode, bigint]
```

Page 18 of 37 

功能: 发送文件类型消息,支持上传进度(可选) 原型: 

```
  /**
```

- 发送文件 

- `@param receiver` 消息接收者 `ID` 

- `@param chatType` 聊天类型 `: ChatType_PrivateChat = 1, //` 私聊 `ChatType_Ro` 

- `@param fileUri` 发送文件的 `uri` 地址(以 `file://` 开头),注意不是沙箱路径。例如 `uri` 

- `@param extra` 额外信息 

- `@param fileType` 发送文件的类型: `FileType_Other = 0, //` 其他; `FileT *` 

- 

- `@param callback` 发送完成回调 `funcOnSendMessage=(reqId: bigint, errCode: reasonType: number, forbidEndTime: number, msgId: bigint) => void` 

- `@param callback` 参数 `reqId` 请求 `ID` (与 `SendXXMessage` 发送消息的输出参数 `reques` 

- `@param callback` 参数 `errCode` 错误码 

- `@param callback` 参数 `sendTime` 发送时间戳,精确到毫秒 

- `@param callback` 参数 `isForbidRoom` 是否被禁言 

- `@param callback` 参数 `reasonType` 禁言原因 `, 0-` 未知, `1-` 发广告, `2-` 侮辱, `3-` 政治敏 

- `@param callback` 参数 `forbidEndTime` 禁言结束时间 

- `@param callback` 参数 `msgId` 消息 `ID` 

- 

- 

- `@param progressCallback? (` 可选 `)` 上传进度回调 `funcOnUploadProgress=(reqId` 

- `@param reqId` 请求 `ID` (与 `SendXXMessage` 发送消息的输出参数 `requestID` 一致) 

- `@param percent` 上传进度 `0-100` 

- `@return [YIMDefine.YIMErrorcode` 错误码 `, bigint` 请求 `ID] */` 

```
  sendFile(recerver: string, chatType: YIMDefine.YIMChatType, fileUri: st
    callback: funcOnSendMessage, progressCallback?: funcOnUploadProgress)
```

功能: 下载文件消息的文件内容 , 这是一个异步操作,操作结果会通过回调接口返回。 原型: 

```
/**
```

`*` 下载消息文件 

Page 19 of 37 

- `@param messageID` 语音消息 `ID` 

- `@param path` 本地缓存路径,必须保证该路径有可写权限 

- `@param callback` 原型 `(errCode: YIMDefine.YIMErrorcode, message: YIMMes` 

- `@param callback` 参数 `errCode` 错误码 

- `@param callback` 参数 `message` 所属消息类 

- `@param callback` 参数 `path` 下载文件的存储路径 

```
   */
downloadFile(messageID: bigint, path: string, callback: (errCode: YIMDe
```

#### **url** 下载文件 

- 功能: 通过 url 下载文件 , 这是一个异步操作,操作结果会通过回调接口返回。 ( 通过 

- onStopAudioSpeechStatus 收到 url 地址后,通过这个接口下载。 ) 原型: 

```
/**
```

- 根据 `Url` 下载文件 

- `@param fromUrl` 下载地址 

- `@param savePath` 本地缓存路径,必须保证该路径有可写权限 

- `@param fileType` 文件类型 

- `@param callback` 下载文件回调 

```
   */
downloadFileByUrl(fromUrl: string, savePath: string, fileType: YIMDefin
callback: (errCode: YIMDefine.YIMErrorcode, fromUrl: string, path: st
```

#### 功能: 设置是否自动下载语音消息。 

- setDownloadAudioMessageSwitch() 在初始化之后,启动语音之前调用 ; 若设置了自动下载语音消 

- 息,不需再调用 downloadAudioMessage() 接口,收到语音消息时会自动下载,自动下载完成会收 到 YIMObserver 的 onDownload() 回调。 

#### 原型: 

```
/**
```

- 是否自动下载语音消息。当设置为 `true` ,语音文件自动下载成功后在 `OnDownload` 中通知 

- `@param download` :自动下载语音消息 `false` :不自动下载语音消息 `(` 默认 `)` 

- `@return` 

```
   */
setDownloadAudioMessageSwitch(download: boolean) : YIMDefine.YIMErrorco
```

Page 20 of 37 

#### 返回: 

#### 错误码,详细描述见错误码定义。 

#### 功能: 开始录音。 

#### 原型: 

```
/**
```

#### `*` 开始发送语音消息 

- `@param receiver` 消息接收者 `ID` 

- `@param chatType` 聊天类型 `: ChatType_PrivateChat = 1, //` 私聊 `ChatType_Ro` 

`* @param msg` 消息内容 

- `@param complete` 发送语音完成的消息回调 

- `@param before_send?` 可选,录音完成之后开始发送语音之前的通知回调 

- `@param callback` 参数 `reqId` 请求 `ID` (与 `SendXXMessage` 发送消息的输出参数 `reques` 

`* @param callback` 参数 `errCode` 错误码 

`* @param callback` 参数 `text` 语音识别结果 

- `@param callback` 参数 `audioPath` 语音文件路径 

- `@param callback` 参数 `audioTime` 语音时长(单位:秒) 

- `@param callback` 参数 `sendTime` 发送时间戳,精确到毫秒 

- `@param callback` 参数 `isForbidRoom` 是否被禁言 

- `@param callback` 参数 `reasonType` 禁言原因 

- `@param callback` 参数 `forbidEndTime` 禁言结束时间 

- `@param callback` 参数 `msgId` 消息 `ID` 

- `@return [YIMDefine.YIMErrorcode` 错误码 `, bigint` 请求 `ID]` 

```
   */
StartRecordAudioMessage(receiver: string, chatType: number,
complete: (reqId: bigint, errCode: YIMDefine.YIMErrorcode, text: stri
sendTime: number, isForbidRoom: boolean, reasonType: number, forbid
    before_send?: (reqId: bigint, errCode: YIMDefine.YIMErrorcode, text:
: [YIMDefine.YIMErrorcode, bigint]
```

#### 返回: 

#### 启动录音是否成功,请求 ID 。 

#### 功能: 取消录音 

原型: 

Page 21 of 37 

`/** *` 取消录音 `* @return */ cancelAudioMessage() : YIMDefine.YIMErrorcode` 

返回: 

错误码,详细描述见错误码定义。 

功能: 停止录音并发送出去 , 这是一个异步操作,操作结果会通过回调参数返回。 原型: 

`/** *` 停止录音并发送 `* @param extra` 语音消息附带信息 `*/ StopAndSendAudioMessage(extra: string) : YIMDefine.YIMErrorcode` 

接收消息接口参考收消息通过 msgType 分拣出语音消息类型: MessageBodyType_Voice 。然后调用函 数 downloadFile 下载语音消息,下载完成后调用方播放。 

备注: 

详细定义查看接收消息备注。 

功能: 可以使用 SDK 内置的播放接口进行播放。 原型: 

`/** *` 播放语音 `* @param path` 语音文件路径 `*/` 

```
startPlayAudio(path: string, callback?: (errCode: YIMDefine.YIMErrorcod
```

回调参数: 

Page 22 of 37 

`errCode: YIMDefine.YIMErrorcode //` 播放语音的错误码 `path: string //` 语音文件路径 

功能: 停止播放当前语音。 原型: `/** *` 停止语音播放 `* @return */ stopPlayAudio() : YIMDefine.YIMErrorcode` 

返回: 错误码,详细描述见错误码定义。 

功能: 设置语音音量。 原型: 

`/** *` 设置语音播放音量 `* @param volume` 音量值,取值范围 `0.0` 到 `1.0 */ setVolume(volume: number)` 

- 功能: 设置录音时用于保存录音文件的缓存目录,如果没有设置, SDK 会在 APP 默认缓存路径下 创建一个文件夹用于保存音频文件。 

原型: 

```
/**
```

- 设置语音消息录制的缓存目录 

- `@param dir` 缓存目录 

```
   */
setAudioCacheDir(dir: string)
```

Page 23 of 37 

#### 功能: 清空当前设置的录音缓存目录。 

#### 原型: 

#### `/**` 

- 清理语音缓存目录(注意清空语音缓存目录后历史记录中会无法读取到音频文件,调用清理历 

#### `* @return` 

```
   */
clearAudioCachePath()
```

#### 功能: 设置语音消息或者文件的保存目录 

- 下载保存目录是 cache/downloads 的默认下载目录,对下载语音消息和文件均适用;设置下载保 存目录在初始化之后,启动语音之前调用,若设置了下载保存目录,调用 ddownloadFile() 时其中 的 savePath 参数可以为空字符串(若 savePath 参数为空字符串时,下载语音消息和文件会生成以 时间戳为前缀的文件)。 

原型: 

#### `/**` 

- 设置下载语音消息的缓存目录 

- `@param dir` 缓存目录 

```
   */
setDownloadDir(dir: string)
```

#### 返回: 

错误码,详细描述见错误码定义。 

#### 原型: 

#### `/**` 

- 开始语音(不通过游密发送该语音消息,由调用方发送,调用 `StopAudioSpeech` 完成上传后 

- `*` 暂不支持语音识别 

- `@param callback` 录音结果回调 

- `@param callback` 参数 `errCode` 错误码 

Page 24 of 37 

`* @param callback` 参数 `audio` 录音信息 

- `@return` 错误码 

```
   */
```

- `/**` 

- 录音信息 

- `@class AudioSpeechInfo` 

- `@property reqID requestID(StartAudioSpeech` 返回 `)` 

- `@property text` 语音翻译文字,不支持翻译的返回空串 

- `@property fileSize` 语音文件大小(单位:字节) 

- `@property audioTime` 语音时长(单位:秒) 

- `@property localPath` 语音文件本地路径 

- `@property url` 语音文件下载路径 

- `*/` 

```
startAudioSpeech(callback: (errCode: YIMDefine.YIMErrorcode, audio: YIM
```

#### 返回: 

#### 消息发送结果,包含错误码和和消息序列号。 

功能: 该接口只返回音频文件的下载链接,不会自动发送 , 这是一个异步操作,操作结果会通过 回调参数返回。 

原型: 

`/** *` 停止语音 `*/ stopAudioSpeech() : YIMDefine.YIMErrorcode` 

#### 根据 **url** 下载语音 

功能: 通过 startAudioSpeech 收到 AudioSpeechInfo 的 url 地址后,可以通过 url 下载文件进行下 载。 

#### 功能: 收到消息后,设置消息为已读。 

原型: 

Page 25 of 37 

```
/**
```

#### `*` 设置本地消息已读 

`* @param messageID` 消息 `ID` 

`* @param readed` 是否已读, `true-` 已读, `false-` 未读 

```
   * @return
   */
setMessageRead(messageID: bigint, readed: boolean) : YIMDefine.YIMError
```

#### 返回: 

错误码,详细描述见错误码定义。 

功能: 收到消息后,设置消息为已读。 

原型: 

```
/**
```

#### `*` 设置所有消息为已读 

- `@param user` 发消息的用户 `ID` ;用户 `ID` 为空字符串时,将登录用户的所有消息设置为已读 

- `@param readed` 是否已读, `true-` 已读, `false-` 未读 

- `@return` 

```
   */
setAllMessageRead(user: string, readed: boolean) : YIMDefine.YIMErrorco
```

#### 返回: 

错误码,详细描述见错误码定义。 

- 功能: 在自动接收消息和手动接收消息间切换,默认是自动接收消息。不自动接收消息 , 有新消 息达到时, SDK 会发出 onReceiveMessageNotify 回调,调用方需要调用 GetMessage 获取新消息 原型: 

```
/**
```

- 设置是否自动接收消息(房间消息 ) 

- `@param targets` 频道 `/` 房间 `ID` 列表 

- `@param autoReceive true:` 自动接收 `(` 默认 `) false:` 不自动接收消息 `,` 有新消息达到 

- `@return` 

```
   */
SetReceiveMessageSwitch(targets: Array<string>, autoReceive: boolean) :
```

Page 26 of 37 

返回: 

#### 错误码,详细描述见错误码定义。 

- 功能: 在手动接收消息模式,需要调用该接口后才能收到 `onReceiveMessage` 通知。 原型: 

#### `/**` 

- 获取新消息(只有 `setReceiveMessageSwitch` 设置为不自动接收消息,才需要在收到 `OnR` 

- `@param targets` 房间 `ID` 列表 

- `@return` 

- `*/` 

```
GetNewMessage(targets: Array<string>) : YIMDefine.YIMErrorcode
```

#### 返回: 

#### 错误码,详细描述见错误码定义。 

备注: 这是一个异步操作,操作结果会通过回调接口返回。 

- 功能: setReceiveMessageSwitch(false) 后,进入手动接收消息模式,有新消息的时候会通知该 回调,频道消息会通知消息来自哪个频道 ID 。 

#### 原型: 

```
/**
```

- 新消息通知(默认自动接收消息,只有调用 `SetReceiveMessageSwitch` 设置为不自动接收 

- `@param chatType` 聊天类型 `YIMDefine.YIMChatType` 

- `@param targetID` 房间或用户 `ID` 

- `*/` 

```
onReceiveMessageNotify(callback: funcOnReceiveMessageNotify)
  type funcOnReceiveMessageNotify= (chatType: YIMDefine.YIMChatType, tar
```

- 功能: 设置是否在本地保存频道聊天记录,默认不保存。私聊历史记录默认保存。 原型: 

Page 27 of 37 

```
/**
```

- 功能:是否保存频道 `/` 房间消息到本地历史记录 

- `@param rooms` :频道 `/` 房间 `ID` 列表 

- `@param isSave` :是否保存(默认不保存) 

- `@return` 错误码 

- `*/` 

```
setRoomHistoryMessageSwitch(rooms: Array<string>, isSave: boolean) : YI
```

#### 返回: 

错误码,详细描述见错误码定义。 

- 功能: 从服务器拉取频道最近的聊天历史记录。这个功能默认不开启,需要的请联系我们修改 服务器配置。联系我们,可以通过专属游密支持群或者技术支持的大群。这是一个异步操作,操 作结果会通过回调接口返回。 

#### 原型: 

```
/**
```

- 从服务器查询房间最近历史消息 

- `@param roomID` 频道 `/` 房间 `id` 

- `@param count` 消息数量 `(` 最大 `30` 条 `)` 

- `@param direction` 历史消息排序方向 `0` :按时间戳升序 `1` :按时间戳逆序 

- `@param callback` 查询历史记录回调 

- `*/` 

```
queryRoomHistoryMessageFromServer(roomID: string, count: number, direct
callback: (code: YIMDefine.YIMErrorcode, target: string, remain: numb
```

#### 回调参数: 

`code` :错误码 

`target` : 获取频道 ID , string 类型。 

`remain` : 获取剩余消息记录数量, number 类型。 

`messages` : 获取消息记录列表。 

`YIMMessage.Msg` 类详细定义查看接收消息备注。 

功能: 从服务器按页拉取频道最近的聊天历史记录。这个功能默认不开启,需要的请联系我们 修改服务器配置。联系我们,可以通过专属游密支持群或者技术支持的大群。这是一个异步操 作,操作结果会通过回调接口返回。 

Page 28 of 37 

原型: 

```
/**
```

- 从服务器查询房间最近历史消息 `(` 按页查询 `)` 

- `@param roomID` 频道 `/` 房间 `id` 

- `@param count` 消息数量 

- `@param direction` 历史消息排序方向 `0` :按时间戳升序 `1` :按时间戳逆序 

- `@param lastMessageID` 上一分页最后消息 `ID,` 第一页可传空 

- `@param callback` 查询历史记录回调 

- `*/` 

```
queryRoomHistoryMessageFromServerByPage(roomID: string, count: number,
callback: (code: YIMDefine.YIMErrorcode, target: string, remain: numb
```

#### 回调参数: 

`code` :错误码 

`target` : 获取频道 ID , string 类型。 

`remain` : 获取剩余消息记录数量, number 类型。 

`messages` : 获取消息记录列表。 

`YIMMessage.Msg` 类详细定义查看接收消息备注。 

- 功能 : 获取本地消息历史记录,这是一个异步操作,操作结果会通过回调接口返回。 原型 : 

```
/**
```

- 功能:查询本地历史消息记录 

- `@param target` :目标 `(` 用户或频道 `)ID` 

- `@param chatType` :表示查询私聊或者频道聊天的历史记录, `1` 是私聊, `2` 是频道聊天 

- `@param startMessageID` :起始消息 `ID` (与 `requestid` 不同,默认为 `0` ,从最新一条消息 `I` 

- `@param count` :消息数量(一次最大 `100` 条) 

- `@param direction` :查询方向 `0` :向前查找(比 `startMessageID` 时间更早) `1` :向后 

- `@param callback:` 查询本地历史记录回调 

- `@return` 错误码 

- `*/` 

```
queryHistoryMessage(target: string, chatType: YIMDefine.YIMChatType, st
callback: (code: YIMDefine.YIMErrorcode, target: string, remain: numb
```

#### 相关函数: 

对于房间本地记录,需要先设置自动保存房间消息。 `setRoomHistoryMessageSwitch` 。 

Page 29 of 37 

#### 回调参数: 

`code` :错误码 

`target` : 获取频道 ID , string 类型。 

`remain` : 获取剩余消息记录数量, number 类型。 

`messages` : 获取消息记录列表。 

`YIMMessage.Msg` 类详细定义查看接收消息备注。 

功能: 清理本地历史记录 原型: 

```
/**
```

- 功能:删除指定时间之前的历史消息 

#### `* @param chatType` :聊天类型 

- `@param time` :时间戳(毫秒级,删除指定时间之前的消息) `,` 当传入的时间戳为小于等于 `0` 时 

`* @return` 错误码 

```
  */
deleteHistoryMessageBeforeTime(chatType: YIMDefine.YIMChatType, time: n
```

返回: 

错误码,详细描述见错误码定义。 

备注: 建议定期清理本地历史记录。 

##### 根据消息 **ID** 清理本地聊天历史记录 

功能: 清理本地历史记录。 原型: 

```
/**
```

- 功能:删除指定 `messageID` 对应消息 

- `@param id` :消息 `ID` 

`* @return` 错误码 

```
  */
deleteHistoryMessageByID(id: bigint) : YIMDefine.YIMErrorcode
```

返回: 

错误码,详细描述见错误码定义。 

备注: 建议定期清理本地历史记录。 

##### 根据用户 **ID** 或者频道 **ID** 清理指定的本地聊天历史记录 

Page 30 of 37 

- 功能: 根据用户 ID 或者频道 ID 删除对应的本地聊天历史记录,保留消息 ID 白名单中的消息记录 , 白名单列表为空时删除与该用户 ID 或频道 ID 有关的所有本地聊天历史记录。 原型: 

#### `/**` 

- 删除指定用户或频道的本地聊天历史记录,保留指定的消息 `ID` 列表记录 

- `*@param targetID:` 用户 `ID` 或者频道 `ID` 

- `*@param chatType:` 聊天类型,私聊 `/` 频道聊天, `1` 是私聊, `2` 是频道聊天 

`*@param excludeMesList:` 保留的消息 `ID` 列表 

`*@return` 错误码 

```
   */
deleteSpecifiedHistoryMessage(target: string, chatType:  YIMDefine.YIMC
```

#### 返回: 

错误码,详细描述见错误码定义。 

备注: 建议定期清理本地历史记录。 

##### 根据用户 **ID** 或者频道 **ID** 清理本地聊天历史记录 

- 功能: 根据用户 ID 或者频道 ID 删除以指定的起始消息 ID 开始的 n 条本地聊天历史记录,起始消息 ID 和消息数量使用默认值时则删除所有消息。 

- 原型: 

#### `/**` 

- 功能:删除历史消息(删除 `startMessageID` 时间之前 `count` 条消息) 

- `@param target` : `userID` 或 `roomID` 

- `@param chatType` :聊天类型 

- `@param startMessageID` :起始消息 `ID` (默认 `0` 最近一条消息) 

- `@param count` :消息数量(默认 `0` 删除所有消息) 

- `@return` 错误码 

- `*/` 

```
deleteHistoryMessageByTarget(target: string, chatType: YIMDefine.YIMCha
```

#### 返回: 

错误码,详细描述见错误码定义。 

备注: 建议定期清理本地历史记录。 

- 功能: 该接口是根据本地历史消息记录生成的最近联系人列表,按最后聊天时间倒序排列。该 列表会受清理历史记录消息的接口影响。这是一个异步操作,操作结果会通过回调接口返回。 原型: 

Page 31 of 37 

```
/**
```

#### `*` 获取最近联系人 

- `@param callback` 获取最近联系人回调 

- `@param callback` 参数 `errCode` 错误码 

- `@param callback` 参数 `contacts` 联系人列表 

```
   */
getHistoryContact(callback: (errCode: YIMDefine.YIMErrorcode, contact
```

回调参数: 

```
/**
```

#### `*` 最近联系人消息 

- `@class ContactMessageInfo` 

- `@property id` 联系人 `ID` 

- `@property ctime` 消息创建时间 

- `@property content` 消息内容 

- `@property type` 消息类型, `0-` 未知类型, `1-` 文本消息, `2-` 自定义消息, `3-` 表情, `4-` 图片 

- `@property path` 如果是语音或者文件消息,文件存放路径 

- `@property notreaded` 接收端消息未读数量 

```
   */
```

考虑到客户端可能需要传递一些自定义消息,关键字过滤方法就直接提供出来,客户端可以选择是否 过滤关键字,可以在发送时选择不发送或发送替换后的方字。接收方在收到文本消息时,也可以调用 该接口进行过滤,自定义是否显示过滤后的文本。 

功能: 过滤敏感词。 

原型: 

```
/**
```

- 功能:消息关键词过滤 

- `@param message` :消息内容 

- `@param level` :过滤等级,匹配到的敏感词等级会返回,具体数值意义暂未启用,保留字段 

- `@return [` 过滤后的字符串(敏感词替换为 `"***"` ) `,` 过滤等级 `]` 

```
  */
getFilterText (message: string, level: number) : [string, number]
```

Page 32 of 37 

#### 返回: 

#### "***" 过滤后的字符串,敏感词替换为 。 

#### 例: 

```
filerText(message: string) : string {
if(this.FilterEnabled) {
letret: [string, number] = YIMClient.getInstance().getFilterText(m
return ret[0];
    } else {
return message;
    }
  }
```

#### 功能: 建议游戏切入后台时通知该接口,以便于得到更好重连效果。 

- 调用 onPause(false), 在游戏切入后台后 , 若 IM 是登录状态,依旧接收 IM 消息。 

- 调用 onPause(true), 游戏切入后台,即使 IM 是登录状态也不会接收 IM 消息;在游戏恢复运行时会 主动拉取暂停期间未接收的消息,收到 onRecvMessage() 回调。 

- 原型: 

```
/**
```

#### `*` 功能:程序切到后台运行 

`* @param pauseReceiveMessage` :是否暂停接收消息 `true-` 暂停接收 `false-` 不暂停接收 

```
  */
onPause(pauseReceiveMessage: boolean)
```

- 功能: 建议游戏恢复运行时通知该接口,以便于得到更好重连效果。 原型: 

#### `/**` 

#### `*` 功能:程序切恢复前台运行 

```
  */
onResume()
```

Page 33 of 37 

```
enum YIMServerZone
```

|`{` `YIMServerZone`|`_China= 0, `|`//`中国|
|---|---|---|
|`YIMServerZone`|`_Singapore= 1, `|`//`新加坡|
|`YIMServerZone`|`_America= 2,`|`//`美国|
|`YIMServerZone`|`_HongKong= 3, //`|香港|
|`YIMServerZone`|`_Korea= 4, `|`//`韩国|
|`YIMServerZone`|`_Australia= 5, `|`//`澳洲|
|`YIMServerZone`|`_Deutschland= 6, `|`//`德国|
|`YIMServerZone`|`_Brazil= 7, `|`//`巴西|
|`YIMServerZone`|`_India= 8, `|`//`印度|
|`YIMServerZone`|`_Japan= 9, `|`//`日本|
|`YIMServerZone`|`_Ireland= 10, //`|爱尔兰|
|`YIMServerZone`|`_Thailand= 11, `|`//`泰国|
|`YIMServerZone`|`= 12,` `//`台湾||

```
    YIMServerZone_Unknow =9999
  }
```

|`enum YIMErrorcode {`|
|---|
|`YIMErrorcode_Success= 0, //`成功|
|`YIMErrorcode_EngineNotInit= 1, //`未初始化|
|`YIMErrorcode_NotLogin= 2, //`未登录|
|`YIMErrorcode_ParamInvalid= 3, //`参数错误|
|`YIMErrorcode_TimeOut= 4, //`超时|
|`YIMErrorcode_StatusError= 5, //`状态错误|
|`YIMErrorcode_SDKInvalid= 6, //SDK`验证识别|
|`YIMErrorcode_AlreadyLogin= 7, //`已经登录|
|`YIMErrorcode_ServerError= 8, //`服务器错误|
|`YIMErrorcode_NetError= 9, //`网络错误|
|`YIMErrorcode_LoginSessionError= 10, //session`错误|
|`YIMErrorcode_NotStartUp= 11, //`未启动|
|`YIMErrorcode_FileNotExist= 12, //`文件不存在|
|`YIMErrorcode_SendFileError= 13, //`发送文件失败|
|Page 34 o `YIMErrorcode_UploadFailed= 14, //`上传失败|

Page 34 of 37 

|`YIMErrorcode_UsernamePasswordError= 15, //`用户名密码错误|
|---|
|`YIMErrorcode_UserStatusError= 16, //`用户状态错误`(`无效用户`)`|
|`YIMErrorcode_MessageTooLong= 17, //`消息太长|
|`YIMErrorcode_ReceiverTooLong= 18, //`接收方`ID`过长`(`检查房间名`)`|
|`YIMErrorcode_InvalidChatType= 19, //`无效聊天类型`(`私聊、聊天室`)`|
|`YIMErrorcode_InvalidReceiver= 20, //`无效用户`ID`|
|`YIMErrorcode_UnknowError= 21, `|
|`YIMErrorcode_InvalidAppkey= 22, //`无效`APPKEY`|
|`YIMErrorcode_ForbiddenSpeak= 23, //`被禁言|
|`YIMErrorcode_CreateFileFailed= 24, //`创建文件失败|
|`YIMErrorcode_UnsupportFormat= 25, //`不支持的文件格式|
|`YIMErrorcode_ReceiverEmpty= 26, //`接收方为空|
|`YIMErrorcode_RoomIDTooLong= 27, //`房间名太长|
|`YIMErrorcode_ContentInvalid= 28, //`聊天内容严重非法|
|`YIMErrorcode_NoLocationAuthrize= 29, //`未打开定位权限|
|`YIMErrorcode_UnknowLocation= 30, //`未知位置|
|`YIMErrorcode_Unsupport= 31, //`不支持该接口|
|`YIMErrorcode_NoAudioDevice= 32, //`无音频设备|
|`YIMErrorcode_AudioDriver= 33, //`音频驱动问题|
|`YIMErrorcode_DeviceStatusInvalid= 34, //`设备状态错误|
|`YIMErrorcode_ResolveFileError= 35, //`文件解析错误|
|`YIMErrorcode_ReadWriteFileError= 36, //`文件读写错误|
|`YIMErrorcode_NoLangCode= 37, //`语言编码错误|
|`YIMErrorcode_TranslateUnable= 38, //`翻译接口不可用|
|`YIMErrorcode_SpeechAccentInvalid= 39, //`语音识别方言无效|
|`YIMErrorcode_SpeechLanguageInvalid= 40, //`语音识别语言无效|
|`YIMErrorcode_HasIllegalText= 41, //`消息含非法字符|
|`YIMErrorcode_AdvertisementMessage= 42, //`消息涉嫌广告|
|`YIMErrorcode_AlreadyBlock= 43, //`用户已经被屏蔽|
|`YIMErrorcode_NotBlock= 44, //`用户未被屏蔽|
|`YIMErrorcode_MessageBlocked= 45, //`消息被屏蔽|
|`YIMErrorcode_LocationTimeout= 46, //`定位超时|
|`YIMErrorcode_NotJoinRoom= 47, //`未加入该房间|
|`YIMErrorcode_LoginTokenInvalid= 48, //`登录`token`错误|
|`YIMErrorcode_CreateDirectoryFailed= 49, //`创建目录失败|
|`YIMErrorcode_InitFailed= 50, //`初始化失败|
|`YIMErrorcode_Disconnect= 51, //`与服务器断开|

`YIMErrorcode_TheSameParam = 52, //` 设置参数相同 `YIMErrorcode_QueryUserInfoFail = 53, //` 查询用户信息失败 `YIMErrorcode_SetUserInfoFail = 54, //` 设置用户信息失败 `YIMErrorcode_UpdateUserOnlineStateFail = 55, //` 更新用户在线状态失败 `YIMErrorcode_NickNameTooLong = 56, //` 昵称太长 `(> 64 bytes) YIMErrorcode_SignatureTooLong = 57, //` 个性签名太长 `(> 120 bytes)` 

Page 35 of 37 

`YIMErrorcode_NeedFriendVerify = 58, //` 需要好友验证信息 `YIMErrorcode_BeRefuse = 59, //` 添加好友被拒绝 

`YIMErrorcode_HasNotRegisterUserInfo = 60, //` 未注册用户信息 `YIMErrorcode_AlreadyFriend = 61, //` 已经是好友 `YIMErrorcode_NotFriend = 62, //` 非好友 `YIMErrorcode_NotBlack = 63, //` 不在黑名单中 `YIMErrorcode_PhotoUrlTooLong = 64, //` 头像 `url` 过长 `(>500 bytes) YIMErrorcode_PhotoSizeTooLarge = 65, //` 头像太大( `>100 kb` ) `YIMErrorcode_ChannelMemberOverflow = 66, //` 达到频道人数上限 

#### `//` 服务器的错误码 

```
    YIMErrorcode_ALREADYFRIENDS =1000,
    YIMErrorcode_LoginInvalid =1001,
```

#### `//` 语音部分错误码 

```
    YIMErrorcode_PTT_Start =2000,
    YIMErrorcode_PTT_Fail =2001,
```

`YIMErrorcode_PTT_DownloadFail = 2002, //` 下载语音失败 `YIMErrorcode_PTT_GetUploadTokenFail = 2003, //` 获取 `token` 失败 `YIMErrorcode_PTT_UploadFail = 2004, //` 上传失败 `YIMErrorcode_PTT_NotSpeech = 2005, //` 未检测到语音或未开始语音 `YIMErrorcode_PTT_DeviceStatusError = 2006, //` 音频设备状态错误 `YIMErrorcode_PTT_IsSpeeching = 2007, //` 正在录音 `YIMErrorcode_PTT_FileNotExist = 2008, //` 文件不存在 

`YIMErrorcode_PTT_ReachMaxDuration = 2009, //` 达到语音最大时长限制 `YIMErrorcode_PTT_SpeechTooShort = 2010, //` 语音时长太短 `YIMErrorcode_PTT_StartAudioRecordFailed = 2011, //` 启动录音失败 `YIMErrorcode_PTT_SpeechTimeout = 2012, //` 音频输入超时 `YIMErrorcode_PTT_IsPlaying = 2013, //` 正在播放 `YIMErrorcode_PTT_NotStartPlay = 2014, //` 未开始播放 `YIMErrorcode_PTT_CancelPlay = 2015, //` 主动取消播放 `YIMErrorcode_PTT_NotStartRecord = 2016, //` 未开始语音 `YIMErrorcode_PTT_NotInit = 2017, //` 未初始化 `YIMErrorcode_PTT_InitFailed = 2018, //` 初始化失败 `YIMErrorcode_PTT_Authorize = 2019, //` 录音权限 

`YIMErrorcode_PTT_StartRecordFailed = 2020, //` 启动录音失败 `YIMErrorcode_PTT_StopRecordFailed = 2021, //` 停止录音失败 `YIMErrorcode_PTT_UnsupprtFormat = 2022, //` 不支持的格式 `YIMErrorcode_PTT_ResolveFileError = 2023, //` 解析文件错误 `YIMErrorcode_PTT_ReadWriteFileError = 2024, //` 读写文件错误 `YIMErrorcode_PTT_ConvertFileFailed = 2025, //` 文件转换失败 `YIMErrorcode_PTT_NoAudioDevice = 2026, //` 无音频设备 `YIMErrorcode_PTT_NoDriver = 2027, //` 驱动问题 `YIMErrorcode_PTT_StartPlayFailed = 2028, //` 启动播放失败 

Page 36 of 37 

`YIMErrorcode_PTT_StopPlayFailed = 2029, //` 停止播放失败 `YIMErrorcode_PTT_RecognizeFailed = 2030, //` 识别失败 `YIMErrorcode_PTT_ShortConnectionMode = 2031, //` 短连接模式不支持发送 

```
    YIMErrorcode_Fail =10000
  }
```

Page 37 of 37
