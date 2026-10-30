# 开发指南 **IM SDK for HarmonyOS** 

游密即时通讯 SDK ( IM SDK )为玩家提供完整的游戏内互动服务,游戏开发者无需关注 IM 通讯复杂的 内部工作流程,只需调用 IM SDK 提供的接口,即可快速实现世界聊天、公会聊天、组队聊天、文字、 表情、语音等多项功能。 

## **IM SDK** 接口调用顺序 

IM SDK 接口调用顺序 

## 四步集成 **IM SDK** 

### 第一步 注册账号 

在游密官网注册游密账号。 

### 第二步 添加游戏,获取 **Appkey** 

在控制台添加游戏,获得接入需要的 Appkey 、 Appsecret 。 

第三步 下载 **IM SDK** 包体 

#### 下载地址 

第四步 开发环境配置 

开发环境配置 

### **1.** 导入 **IM SDK** 

Page 1 of 17 

DevEco Studio 版本: 5.0.0 Release(Build Version: 5.0.3.910) 及以上 

HarmonyOS SDK 版本: 5.0.0 Release(API Version 12 Release) 及以上 

手机系统 OpenHarmony 版本: 5.0.0.31(Beta2) 及以上 

#### 安装 **SDK** 包 

在模块的 oh-package.json5 中 dependencies 增加 har 包依赖,配置如下: 

```
"dependencies": {
  "@youme/im": "3.0.11"
}
```

依赖设置完成后,需要执行 `ohpm install` 命令安装依赖包,依赖包会安装在该模块的 oh_modules 目录下。 

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
        "FormAbility"
      ],
      "when": "inuse"
    }
  }
```

#### 使用 **Native C++** 接口 

har 包安装在该模块的 oh_modules 目录,目录下有提供 Native C++ 的 include 头文件 和 so 库文件。 若要使用 Native C++ 接口,可以再 CMake 里配置使用。 C++ 接口 API 说明书请参考 IM SDK for C++ 使用指南。 

Page 2 of 17 

`#CMakeLists.txt` 示例 

#### `#` 包含 `include` 目录 

`include_directories(${CMAKE_CURRENT_SOURCE_DIR}/../../../oh_modules/@youm #` 包含 `so` 的目录 `link_directories("../../../oh_modules/@youme/im/libs/${OHOS_ARCH}") #` 把 `libyim.so` 添加到链接库里 `target_link_libraries(entry PUBLIC libace_napi.z.so libhilog_ndk.z.so lib` 

`//papi_init.cpp` 引用示例 `#include "YIM.h" #include "YIMPlatformDefine.h" ...` 

`//` 使用 `C++` 回调接口 `IYIMLoginCallback class CNAPICallback: public IYIMLoginCallback { public: /*` 

`*` 功能:登录回调 

`* @param errorcode` :错误码 `* @param userID` :用户 `ID */ virtual void OnLogin(YIMErrorcode errorcode, const XCHAR * userID) { OH_LOG_INFO(LOG_APP, "login with code %d", errorcode); if(errorcode == YIMErrorcode_Success) { YIMManager::CreateInstance()->GetChatRoomManager()->JoinChatR` 

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

Page 3 of 17 

### **2.** 初始化 

#### 成功导入 SDK 后,应用启动的第一时间需要调用初始化接口。 

#### **import** 包名 

```
import { YIMClient, YIMObserver, YIMDefine, YIMMessage } from '@youme/im'
```

YIMClient 是一个单例类,可以通过 .getInstance() 获取到它的实例。通过它就可以调用 IM SDK 的 API 接 口。 

#### 初始化 **IM SDK** 

```
let error: YIMDefine.YIMErrorcode =
YIMClient.getInstance().init(this.appCustom.appKey,
this.appCustom.appSecret, this.selectedZone);
```

#### 初始化接口 : 

```
init(appKey:string, appSecret:string, serverZone:
YIMDefine.YIMServerZone, packageName:string = "",
sdkValidDomain:string = "", drDomain:string = "",
sdkValidBackupip:string = "", drBackupip:string = ""):
YIMDefine.YIMErrorcode
```

#### `appKey` :用户游戏产品区别于其它游戏产品的标识,可以在游密官网获取、查看。 

#### `appSecret` :用户游戏产品的密钥,可以在游密官网获取、查看。 

#### `serverZone` : IM 服务器区域,一般使用 `0` - 中国,其余设置值查看服务器部署地区定义。 

#### `YIMErrorcode` :错误码,详细描述见错误码定义。 

此接口本是异步操作,未给出异步回调,一般返回的错误码是 Success 即表示初始化成功。 

### **3.** 监听全局回调 

IM 引擎的一些消息通知是需要设置全局回调来接收的,比如其他人进出房间,消息接收等。 

新建一个 YIMObserver 对象,处理您感兴趣的回调,然后添加到 IM 引擎的观察者列表,就可以完成了。 

Page 4 of 17 

如果不需要接收消息了,可以从观察者列表中删除。 具体的全局回调类型请查看 API 接口。 

`import { YIMClient, YIMObserver, YIMDefine, YIMMessage } from '@y ... observer: YIMObserver = new YIMObserver(); ... //` 设置监听 `YIMClient.getInstance().addObserver(this.observer); ... //` 回调接口实现 `this.observer .onReceiveMessage((msg: YIMMessage.Msg) => { //` 接收别人发送的消息 `... }) .onOtherJoinRoom((room, user) => { //` 其他人进入房间 `... }) .onOtherLeaveRoom((room, user) => { //` 其他人离开房间 `... }) .onUpdateReadStatus((recvID: string, chatType: YIMDefine.YIMChatT //` 其他人已读了某条消息 `... }) ... }` 

添加观察者接口 : 

```
addObserver(observer: YIMObserver)
```

Page 5 of 17 

移除观察者接口 : 

```
deleteObserver(observer: YIMObserver)
```

### **4.** 登录 **IM** 系统 

成功初始化 IM 后,调用 IM SDK 登录接口登录 IM 系统。 

`Button('` 用户登录 `') .onClick(() => { let errcode: YIMDefine.YIMErrorcode = YIMClient.getInstance().log (errCode: YIMDefine.YIMErrorcode, user: string) => { if(errCode == YIMDefine.YIMErrorcode.YIMErrorcode_Success) { ... } else { hilog.error(0x0000, 'YOUMEIM_DEMO_UI', `callback:login err:${ .. } }); })` 

登录接口 : 

```
login(user: string, password:string, token: string, callback:
(errCode: YIMDefine.YIMErrorcode, user: string) => void) :
YIMDefine.YIMErrorcode
```

`user` :由调 者分配,不可为空字符串,只可由字母或数字或下划线组成,用户首次登 录会自动注册所用的用户 ID 和密码。 

- `password` 户密码,不可为空字符串,由调用者分配,二次登录时需与首次登录一 

致,否则会报 UsernamePasswordError 。 

`token` :用户验证 token ,可选,如不使用 token 验证传入 :"" 。 

`callback` :登录回调。 

### **5.** 进入聊天频道 

登录成功后,如果有群组聊天需要,比如游戏里面的世界、工会、区域等,需要进入聊天频道;调用 方为聊天频道设置一个唯一的频道 ID ,可以进入多个频道。 

Page 6 of 17 

`Button('` 加入聊天室 `') .onClick(() => { let errcode :YIMDefine.YIMErrorcode = YIMClient.getInstance().joi if(err == YIMDefine.YIMErrorcode.YIMErrorcode_Success) { this.getRoomMemberCount(room); ... } else { hilog.error(0x0000, 'YOUMEIM_DEMO_UI', `callback:join_room er ... } }); if(errcode != YIMDefine.YIMErrorcode.YIMErrorcode_Success) { ... } })` 

进入频道接口 : 

```
joinChatRoom(room: string, callback: (errCode:
YIMDefine.YIMErrorcode, room: string) => void) :
YIMDefine.YIMErrorcode
```

`room` :请求加入的频道 ID ,仅支持数字、字母、下划线组成的字符串,区分大小写,长 度限制为 255 字节。 

`callback` :加入频道回调。 

### **6.** 发送文本消息 

在成功登录 IM 后,即可发送 IM 消息。 

`//` 发送文本消息 

`Button('` 发送文字 `')` 

```
  .onClick(() => {
letout: [YIMDefine.YIMErrorcode, bigint] = YIMClient.getInstance
      YIMDef.YIMChatType.ChatType_PrivateChat, this.msgToSend, "",
      (reqId: bigint, errCode: YIMDefine.YIMErrorcode, sendTime: numb
if(errCode == YIMDefine.YIMErrorcode.YIMErrorcode_Success) {
```

Page 7 of 17 

```
...
        } else {
          hilog.error(0x0000, 'YOUMEIM_DEMO_UI', `callback:send_msg_s
...
        }
      });
if(out[0] == YIMDefine.YIMErrorcode.YIMErrorcode_Success) {
...
    } else {
...
    }
  })
```

#### 发文本消息接口 : 

```
sendTextMessage(receiver: string, chatType: number, msg: string,
param: string, callback: funcOnSendMessage) :
[YIMDefine.YIMErrorcode, bigint]
```

#### `receiver` :接收者 ID ,私聊传入用户 ID ,频道聊天传入频道 ID 。 

`chatType` :聊天类型 , 私聊传 `1` ,频道聊天传 `2` ;需要频道聊天得先成功进入频道后发 文本消息,此频道内的成员才能接收到消息。 

`msg` :聊天内容。 

`param` : 发送文本附加信息。 

`callback` :发送文本消息回调。 

#### 发送文本消息回调:: 

```
funcOnSendMessage = (reqId: bigint, errCode: YIMDefine.YIMErrorcode,
sendTime: number, isForbidRoom: boolean, reasonType: number,
```

`forbidEndTime: number, msgId: bigint) => void` : 

`reqId` : 消息序列号,用于校验一条消息发送成功与否的标识, long 类型。 

`errCode` : 错误码。 

`sendTime` : 消息发送时间, long 类型。 

`isForbidRoom` : 若发送的是频道消息,显示在此频道是否被禁言, true- 被禁言, false- 未被禁 言, boolean 类型。 

`reasonType` : 若在频道被禁言,禁言原因类型, 0- 未知, 1- 发广告, 2- 侮辱, 3- 政治敏感, 4- 恐怖主义, 5- 反动, 6- 色情, 7- 其它, int 类型。 

Page 8 of 17 

`forbidEndTime` : 若在频道被禁言,禁言结束时间, long 类型。 

`msgId` : 返回服务器 messageID, 与接收消息时的 getMessageID() 是统一的。 

发送消息时,可以将玩家头像、昵称、角色等级、 vip 等级等要素打包成 json 格式发送。 

### **7.** 发送语音消息 

在成功登录 IM 后,可以发送语音消息。 

按住语音按钮时,调用 `StartRecordAudioMessage` 接口,启动录音。 松开按钮,调用 `StopAndSendAudioMessage` 接口,发送语音消息。 按住过程若需要取消发送,调用 `cancelAudioMessage` 取消本次语音发送。 

`Button(this.speek_btn_text) .onTouch(async (event:TouchEvent) => { if(event.type == TouchType.Down) { //` 启动语音 `let out: [YIMDefine.YIMErrorcode, bigint] = YIMClient.getInstan (reqId: bigint, errCode: YIMDefine.YIMErrorcode, text: string if(errCode == 0) { ... } else { hilog.error(0x0000, 'YOUMEIM_DEMO_UI', `callback:send_aud ... } }, (reqId: bigint, errCode: YIMDefine.YIMErrorcode, text: string hilog.info(0x0000, 'YOUMEIM_DEMO_UI',  `` 开始发送语音回调,请求 `}); if(out[0] == YIMDefine.YIMErrorcode.YIMErrorcode_Success) { ... } }else if(event.type == TouchType.Up) { //` 停止并发送语音消息 `let ret: YIMDefine.YIMErrorcode = YIMClient.getInstance().StopA } })` 

Page 9 of 17 

#### 发送语音消息接口 : 

```
StartRecordAudioMessage(receiver: string, chatType: number,
complete: (reqId: bigint, errCode: YIMDefine.YIMErrorcode, text:
string, audioPath: string, audioTime: number, sendTime: number,
isForbidRoom: boolean, reasonType: number, forbidEndTime: number,
msgId: bigint) => void, before_send?: (reqId: bigint, errCode:
YIMDefine.YIMErrorcode, text: string, audioPath: string,
audioTime: number) => void) : [YIMDefine.YIMErrorcode, bigint]
```

#### 结束录音接口 : 

```
StopAndSendAudioMessage(extra: string) : YIMDefine.YIMErrorcode
```

#### 取消录音接口 : 

```
cancelAudioMessage() : YIMDefine.YIMErrorcode
```

`receiver` :接收者 ID 户 ID 或者频道 ID )。 

#### `chatType` :消息类型,表示私聊还是频道消息。 

#### `extra` :发送语音消息附加信息,主要用于调用方特别需求。 

发送完成回调 `complete` : (reqId: bigint, errCode: YIMDe�ne.YIMErrorcode, text: string, 

audioPath: string, audioTime: number, 

sendTime: number, isForbidRoom: boolean, reasonType: number, forbidEndTime: number, msgId: bigint) => void 

录音完成,开始发送时回调 `before_send` : (reqId: bigint, errCode: YIMDe�ne.YIMErrorcode, text: string, audioPath: string, audioTime: number) => void 

#### `reqId` : 消息序列号,用于校验一条消息发送成功与否的标识, long 类型。 

`errCode` : 错误码。 

`text` : 语音转文字识别的文本内容,如果带语音转文字参数为 false ,该字段为空字符串。 

`audioPath` : 录音生成的 wav 文件的本地完整路径。 

`audioTime` : 录音时长 ( 单位秒 ) 。 

`sendTime` : 消息发送时间, long 类型。 

`isForbidRoom` : 若发送的是频道消息,显示在此频道是否被禁言, true- 被禁言, false- 未被禁 言, boolean 类型。 

`reasonType` : 若在频道被禁言,禁言原因类型, 0- 未知, 1- 发广告, 2- 侮辱, 3- 政治敏感, 4- 恐怖主义, 5- 反动, 6- 色情, 7- 其它, int 类型。 

`forbidEndTime` : 若在频道被禁言,禁言结束时间, long 类型。 

`msgId` : 返回服务器 messageID, 与接收消息时的 getMessageID() 是统一的。 

Page 10 of 17 

语音消息发送成功,接收方会收到 `onReceiveMessage` 回调,能从该回调中下载语音文件。 

### **8.** 接收消息 

通过 `onReceiveMessage` 接口被动接收消息,需要开发者实现 

```
this.observer
```

`.onReceiveMessage((msg: YIMMessage.Msg) => { if (msgType == YIMDef.YIMMessageBodyType.MessageBodyType_TXT) { //` 收到文本消息 `... } else if (msgType == YIMDef.YIMMessageBodyType.MessageBodyType //` 收到语音消息 `... //` 下载这条语音消息 `YIMClient.getInstance().downloadFile(msg.msgId, "", (errCode: if (errCode == 0) { //` 下载成功 `... //` 播放这条语音 `YIMClient.getInstance().startPlayAudio(path); } else { hilog.error(0x0000, 'YOUMEIM_DEMO_UI', `callback:download ... } }); return; } else { //` 收到其他类型消息 `... return; } })` 

### **9.** 接收语音消息并播放 

Page 11 of 17 

#### 通过 `msgType` 分拣出语音消息 

( `YYIMDefine.IMMessageBodyType.MessageBodyType_Voice` ) 。 用 `msgId` 获得消息 ID 。 调用 `downloadFile` 接口下载语音消息。 成功下载语音消息后,调用 `startPlayAudio` 接口播放语音消息。 

`//` 下载这条语音消息 `YIMClient.getInstance().downloadFile(msgId, "", (errCode: YIMDefine.Y if (errCode == 0) { //` 下载成功 `... //` 播放这条语音 `YIMClient.getInstance().startPlayAudio(path); } else { hilog.error(0x0000, 'YOUMEIM_DEMO_UI', `callback:download_file er ... } });` 

#### 下载语音消息接口 : 

```
downloadFile(messageID: bigint, path: string, callback: (errCode:
YIMDefine.YIMErrorcode, message: YIMMessage.Msg, path: string) =>
void
```

#### 播放语音消息接口 : 

```
startPlayAudio(path: string) : YIMDefine.YIMErrorcode
```

`messageID` :消息 ID 。 

`path` :语音文件保存路径。 

`path` :待播放文件路径。 `callback` :回调。 

下载语音接口是异步操作,下载语音成功的标识是 `onDownload` 回调的错误码为 Success ,调 

用 `downloadFile` 接口同步返回值是 Success 才能收到 `onDownload` 回调。成功下载语音消息 后即可播放语音消息。 

Page 12 of 17 

下载回调接口 : `(errCode: YIMDefine.YIMErrorcode, message:` 

`YIMMessage.Msg, path: string) => void` : 

`errCode` :错误码。 `message` :消息基类。 

`path` :保存路径。 

### **10.** 登出 **IM** 系统 

注销账号时,调用登出接口 `logout` 登出 IM 系统。 

`Button('` 用户登出 `') .onClick(() => { YIMClient.getInstance().logout((errCode:nuYIMDefine.YIMErrorcodem if(errCode == 0) { ... } else { hilog.error(0x0000, 'YOUMEIM_DEMO_UI', `callback:logout err:$ ... } }); })` 

登出接口 : `logout(callback: (errCode: YIMDefine.YIMErrorcode) => void) : YIMDefine.YIMErrorcode` 

主要分为世界频道聊天,用户私聊,直播聊天室;集成的时都需要先初始化 SDK ,登录 IM 系统。 

### 启动应用,初始化 **SDK** 

应用启动的第一时间需要调用初始化接口。 

Page 13 of 17 

#### `init` :初始化接口。 

- `appKey` :用户游戏产品区别于其它游戏产品的标识,可以在游密官网获取、查看。 

- `appSecret` :用户游戏产品的密钥,可以在游密官网获取、查看。 

- `serverZone` : IM 服务器区域,一般使用 `0` - 中国,其余设置值查看服务器部署地区定 

- 义。 

#### HarmonyOS 示例。 

### 登录应用时,登录 **IM** 系统 

#### 登录界面介绍 

点击 登录 按钮时,调用 IM SDK 登录接口。 

`login` :登录接口。 

- `user` :由调 者分配,不可为空字符串,只可由字母或数字或下划线组成。 

- `password` 户密码,不可为空字符串。 

- `token` :用户验证 token ,可选,如不使用 token 验证传入 :"" 。 

- `callback` :登录回调。 

#### HarmonyOS 示例。 

#### 频道 

- 进入应用后,调用加入频道接口,进入世界、公会、区域等需要进入的聊天频道。 应用需要为各个聊天频道设置一个唯一的频道 ID 。 

- 成功进入频道后,发送频道消息,文本、语音消息等。 

   - `joinChatRoom` :加入频道。 

   - `room` :请求加入的频道 ID 。 

   - `callback` :加入频道回调。 

Page 14 of 17 

#### HarmonyOS 示例。 

直播聊天室

- 成功登录 IM 系统后,可和其它登录 IM 的用户发私聊消息,文本、语音消息等;发文本消 息接口的聊天类型参数使用 `1` - 私聊类型。 

调用流程查看发送文本消息,发送语音消息。 

- 用户集成直播 SDK 后,导入 IM SDK 。 

- 初始化 IM SDK 。 

- 登录 IM 系统。 

- 进入指定的聊天频道。 

- 发送频道消息(例如:弹幕式),调用流程查看发送文本消息。 

#### 频道 

- 点击发送按钮,调用发消息接口,将输入框中的内容发送出去。 发送出的消息出现在聊天框右侧。 

- 表情消息可以将表情信息打包成 Json 格式发送。 

#### `sendTextMessage` :发文字消息接口。 

- `receiver` :接收者 ID ,私聊传入用户 ID ,频道聊天传入频道 ID 。 

- `chatType` :聊天类型,私聊 / 频道聊天。 

- `msg` :聊天内容。 

- `param` : 发送文本附加信息。 

- `callback` :发送文本消息回调。 

#### HarmonyOS 示例。 

发送消息时,可以将玩家头像、昵称、角色等级、 vip 等级等要素打包成 json 格式发送。 

Page 15 of 17 

#### 发送语音消息 

- 按住语音按钮时,调用 `StartRecordAudioMessage` 。 

- 松开按钮,调用 `StopAndSendAudioMessage` 接口,发送语音消息。 

- 按住过程若需要取消发送,调用 `cancelAudioMessage` 取消发送。 

`StartRecordAudioMessage` :发送语音消息接口。 

- `StopAndSendAudioMessage` :结束录音接口。 

- `cancelAudioMessage` :取消录音接口。 

- `receiver` :接收者 ID 户 ID 或者频道 ID )。 

- `chatType` :消息类型,表示私聊还是频道消息。 

- `extra` :语音消息附带信息。 

#### HarmonyOS 示例 

#### 接收消息 

- 通过 `onReceiveMessage` 接口被动接收消息,需要开发者实现,接收消息进行相应的 展示,如果是语音消息需要下载语音,以及下载完成后的语音播放。 

`onReceiveMessage` :收消息接口。 

#### HarmonyOS 示例。 

#### 接收语音消息 

- 通过 `msgType` 分拣出语音消息 

- ( `YIMMessageBodyType.MessageBodyType_Voice` ) 。 

- `msgId` 获得消息 ID 。 

- 点击语音气泡,调用 `downloadFile` 接口下载语音文件。 调用方播放语音文件。 

Page 16 of 17 

#### `downloadFile` :下载语音文件接口。 

#### `startPlayAudio` :播放语音文件接口。 

`messageID` :消息 ID 。 

- `path` :保存路径。 `callback` :回调。 

#### HarmonyOS 示例。 

### 登出 **IM** 系统 

#### 更换账号 

- 如下两种情况需要登出 IM 系统: 

- 注销账号时,调用 `logout` 接口登出 IM 系统。 

- 退出应用时,调用 `logout` 接口登出 IM 系统。 

#### `logout` :登出接口。 

#### HarmonyOS 示例。 

Page 17 of 17
