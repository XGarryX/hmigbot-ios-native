目     录 

SDK介绍 工程准备 

获取AnyChatHarmonySDK 导入SDK文件 混淆加固 开发流程 初始化SDK 初始化及自动登录 退出及释放连接 版本信息查询 登录方式说明 服务器连接断开通知事件 会话保持注册和销毁事件 房间管理 注册房间管理事件 注销房间管理事件 进入房间 获取房间中的用户列表 房间内的文字交流 退出房间 音视频操作 音视频互动 本地麦克风管理 打开本地麦克风 关闭本地麦克风 本地摄像头管理 打开本地摄像头 关闭本地摄像头 切换本地摄像头 接收/终止对方音频流 接收远程音频流 关闭远程音频流 接收/终止对方视频流 获取远程视频流 关闭远程视频流 

视频呼叫 

注册视频呼叫事件 客户呼叫 客户取消呼叫 

本文档使用 看云 构建 

- 2 - 

接听视频呼叫 拒绝接听 挂断通话 注销视频呼叫事件 录制(录音录像) 开始录制 在录制文件中添加图片水印 在录制文件中添加文字水印 在录像中插入图片 更新录像参数 结束录制 视频拍照 抓拍 音视频参数配置 视频参数配置 音频参数配置 文件传输 初始化文件模块 注册文件接收通知事件 注销文件接收通知事件 创建文件传输任务 文件管理 初始化文件模块 创建文件上传任务 创建文件下载任务 透明通道 发送透明通道 注册接收透明通道通知事件 注销接收透明通道通知事件 智能排队 初始化排队模块 营业厅操作 获取营业厅列表 进入营业厅 席座服务状态设置 离开营业厅 排队操作 进入队列 取消排队 状态查询 查询坐席状态 查询队伍排队人数 

本文档使用 看云 构建 

- 3 - 

查询当前排队时间 查询用户所在队列的当前位置 查询服务区域内排队的用户数 查询营业厅内的坐席数 注册队列状态变化事件的监听 注销队列状态变化事件的监听 

#### 双录 

基本流程 

自助双录 远程双录 双录接口说明 PPT资源下载 下载任务初始化 开始下载 取消下载 查询资源下载状态 查询资源详细信息 资源播放 媒体资源播放 播放 暂停 停止 销毁 获取当前播放信息 播放状态回调接口 时间戳 水印 用户相关的查询接口 查询用户名 错误码 

本文档使用 看云 构建 

- 4 - 

SDK介绍 

# SDK介绍 

# SDK介绍 

### SDK 介绍 

AnyChat Harmony SDK综合运用音视频编解码、流媒体处理以及P2P等专业技术,提供基于SDK的一站式音视 频通信能力解决方案。它包含了音视频通话、录制(录音录像)、文字交流、文件传输、文件上传,透明通道, 视频呼叫,智能排队,桌面共享和远程协助等功能模块,满足远程视频开户、视频会议、在线教育、应急指挥、 远程医疗,智能设备、互联网金融以及即时通讯等业务场景的需要。 

#### 面向的读者 

本文提供给具有一定的鸿蒙编程经验的读者使用,不要求具备音视频开发方面的经验,您在使用遇到任何问题, 都可以通过访问bbs.anychat.cn反馈给我们。 

#### 技术支持 

在您使用本 SDK 的过程中,遇到任何困难,请与我们联系,我们将热忱为您提供帮助。 您可以通过如下方式与我们取得联系: 

- 1 、在线论坛: http://bbs.anychat.cn/ 

- 2 、知识中心: http://www.anychat.cn/faq/ 

- 3 、官方网站: http://www.anychat.cn 

- 4 、电子邮件: service@bairuitech.com 

- 5 、 24 小时客服电话: +86 ( 020 ) 85276986 、 38109065 、 38103410 

本文档使用 看云 构建 

- 5 - 

工程准备 

# 工程准备 

##### 获取AnyChatHarmonySDK 

导入SDK文件 混淆加固 

本文档使用 看云 构建 

- 6 - 

获取AnyChatHarmonySDK 

# 获取AnyChatHarmonySDK 

### 下载sdk 

##### 点击这里下载SDK。 

AnyChat HarmonyOS SDK包提供了开发指南、Demo源代码、sdk接口代码,其解压之后的目录结构如下所 示: 

- |----doc 客户端开发指南 

- |----demo Demo程序源代码 

- |----sdk sdk接口源码 

本文档使用 看云 构建 

- 7 - 

导入SDK文件 

# 导入SDK文件 

### 导入SDK文件 

将sdk工程作为library添加到您的项目依赖中之后就能正常使用sdk所提供的功能。 

本文档使用 看云 构建 

- 8 - 

混淆加固 

# 混淆加固 

### SDK混淆加固说明 

##### 混淆说明: 

在obfuscation-rules中加入 

SO库和代码都都不建议混淆 

加固说明:SO文件不建议加固。 

本文档使用 看云 构建 

- 9 - 

开发流程 

# 开发流程 

### 开发流程 

##### 在工程准备好了之后,只需简单的几步,即可实现基础的音视频通话。 

#### 1.初始化SDK 

##### 加载资源,应用程序中只需要执行一次,其他的功能接口都必须在初始化之后才能正常使用。 

```arkts
const anychatSDK: AnyChatSDK  = AnyChatSDK.getInstance(); // 注册重连失败监听 anychatSDK.registerLinkCloseEvent(this); const loginEvent : AnyChatLoginEvent = { // 连接成功通知 
```

onLogin(userId: number) { //data.userId 登录人账户 } // 连接断开,原因可能有签名错误,重复登录,网络异常断开 ... 

onDisconnect(result: AnyChatResult) { //result.errCode 错误码 //result.errMsg 错误描述 } 

}; // 登录人账户 (nickName:'demo@anychat.cn') //AnyChat 服务器地址,如连接云平台,地址为 cloud.anychat.cn ,端口为 8906(serverIp: " demo.anychat.cn") 

//AnyChat 服务器端口号 (serverPort: 8906) 

const initOpt: AnyChatInitOpt = new AnyChatInitOpt("demo@anychat.cn","demo. anychat.cn",8906,loginEvent); 

anychatSDK.sdkInit(initOpt); 

#### 2.进入房间 

const anychatSDK: AnyChatSDK = AnyChatSDK.getInstance(); const enterRoomCallback: AnyChatCallbackEvent =  { 

onCallbackEvent(result : AnyChatResult , JsonData: object) { //result.errCode == 0 success, 其他为相应错误代码 //JsonData.roomId 成功进入的房间号 

} 

}; 

anychatSDK.enterRoom("1","123",enterRoomCallback) { 

本文档使用 看云 构建 

- 10 - 

开发流程 

#### 3.打开自己的麦克风以及摄像头 

const anychatSDK: AnyChatSDK = AnyChatSDK.getInstance(); 

// 获取本地麦克风对象列表,通常只有一个 

let microphones = anychatSDK.getMicrophones(); 

for (let microphone of microphones) { //microphone.deviceName 名称 //...... } 

// 打开其中一个麦克风 microphone.open(); 

// 获取本地摄像头对象列表,通常只有一个 

let cameras = anychatSDK.getCameras(getContext()); 

for (let camera of cameras) { //camera.getVideoCapture() 名称 //...... 

} 

// 打开其中一个摄像头 , 并在页面上显示视频画面 camera.open(); 

#### 4.接收对方的音视频流 

const anychatSDK = AnyChatSDK.getInstance(); // 接收对方音频流 //remoteUserId: 对方用户 ID anychatSDK.getRemoteAudioStream(remoteUserId); 

// 接收对方视频流,并在页面上显示 

//context //remoteUserId: 对方用户 ID anychatSDK.getRemoteVideoStream(context, remoteUserId); 

#### 5.结束音视频通话 

结束通话时,需停止接收对方的音视频流,关闭自己的麦克风以及摄像头,退出房间以及退出sdk。 

const anychatSDK = AnyChatSDK.getInstance(); 

本文档使用 看云 构建 

- 11 - 

开发流程 

##### // 终止对方视频流 

//remoteUserId: 对方用户 ID anychatSDK.cancelRemoteVideoStream(remoteUserId); 

// 终止对方音频流 //remoteUserId: 对方用户 ID anychatSDK.cancelRemoteAudioStream(remoteUserId); 

// 关闭摄像头 camera.close(); // 关闭麦克风 microphone.close(); // 离开房间 anychatSDK.leaveRoom(); // 退出 sdk anychatSDK.release() 

本文档使用 看云 构建 

- 12 - 

初始化SDK 

# 初始化SDK 

### 初始化SDK 

#### 模块简述: 

##### 其他的功能接口都必须在初始化成功之后才能正常使用 

本文档使用 看云 构建 

- 13 - 

初始化及自动登录 

# 初始化及自动登录 

### 初始化 

sdkInit(initOpt: AnyChatInitOpt): AnyChatSDK 

#### 接口说明: 

- 此接口方法内部实现 sdk 的初始化及登录服务器两个功能 . 其中登录有两种模式, 

- 1 、密码登录:需传入 nickName 和 password 即可登录,其中 password 可不传; 

- 2 、签名登录:需传入 nickName 和 sign 、 appId 、 timestamp ,其他字段为可选 。 

##### 登录方式详述可参考"登录方式说明"章节 

#### 返回值: 

sdk 单例,一个客户端对象,后续各类模块 API 操作,修改配置、注册模块事件都针对该对象。 

#### 接口参数简介: 

|名称|类型|说明|是否必须|
|---|---|---|---|
|initOpt|AnyChatInitOpt|SDK初始化配置类|是|

#### AnyChatInitOpt 配置类简介: 

#### 通用属性 

|名称|类型|说明|是否必须|
|---|---|---|---|
|serverIp|string|服务器地址(IP地 址或域名) ,AnyChat服务器 地址 (demo.anychat.cn ),如连接云平 台,地址为 cloud.anychat.cn|是|
|serverPort|number|服务器通信端口, AnyChat服务器 端口号:8906|是|
|nickName|string|用户昵称|是|
||AnyChatLoginEv|||

本文档使用 看云 构建 

- 14 - 

初始化及自动登录 

## ent 

#### 使用普通登录需要注意的属性 

|名称|类型|说明|是否必须|
|---|---|---|---|
|password 使用签名登录时需要|string 注意的属性|密码|否|
|名称|类型|说明|是否必须|
|appId|string|应用id|否|
|sign|string|应用签名|否|
|timeStamp|number|时间戳|否|
|strUserId|string|业务系统用户身份 唯一标识,普通登 录该参数无效|否|

#### AnyChatLoginEvent回调简介: 

|返回值|名称|参数(类型)说 明|接口说明|备注|
|---|---|---|---|---|
|void|onLogin|userId(numb er)|登录成功|登录用户Id|
|void|onDisconne ct|result(AnyCh atResult)|连接断开|原因可能有签 名错误,重复 登录,网络异 常断开...|

#### 示例代码: 

// anychatSDK is the instance of sdk 

let initOpt: AnyChatInitOpt = new AnyChatInitOpt( nickName,  strUserId,  passwo rd,  serverIp,  serverPort, loginEvent) anychatSDK.sdkInit(initOpt);// 初始化 

本文档使用 看云 构建 

- 15 - 

退出及释放连接 

# 退出及释放连接 

### 释放sdk 

void release() 

#### 接口说明: 

释放 sdk 实例以及 sdk 持有的资源 

#### 返回值: 

无 

#### 示例代码: 

// anychatSDK is the instance of sdk anychatSDK.release(); 

本文档使用 看云 构建 

- 16 - 

版本信息查询 

# 版本信息查询 

### 版本信息查询 

getVersionInfo(): string 

#### 接口说明: 

获取 sdk 版本信息 ( 版本号和版本发布时间 ) 

#### 返回值: 

SDK 版本信息 

#### 示例代码: 

- // anychatSDK is the instance of sdk 

const info: string =  anychatSDK.getVersionInfo(); 

本文档使用 看云 构建 

- 17 - 

登录方式说明 

# 登录方式说明 

#### 登录方式说明 

#### AnyChat sdk支持两种登录方式,分别如下: 

##### 1. 密码登录 

密码登录,只需要在AnyChat初始化接口中传入服务器ip,端口号以及用户账号和密码(密码字段为可 选),即可登录。 

const anychatSDK: AnyChatSDK = AnyChatSDK.getInstance(); 

// anychatSDK is the instance of sdk 

let initOpt: AnyChatInitOpt = new AnyChatInitOpt(nickName,strUserId,password,se rverIp,serverPort,loginEvent) 

anychatSDK.sdkInit(initOpt);// 初始化 

##### 2. 签名登录 

一种更高安全级别的登录方式,只有AnyChat服务集群与云平台才支持签名登录,终端客户登录时,需要向 身份验证系统获取签名,签名由应用的私钥生成,AnyChat服务器使用应用公钥认证签名,并根据认证结果 决定是否让应用终端接入。 

客户如果购买的是AnyChat服务器集群,需在集群控制台配置应用ID和公钥;如果购买的是AnyChat视频云 服务,应用ID由购买应用时生成,密钥由应用激活时生成。 

const anychatSDK: AnyChatSDK = AnyChatSDK.getInstance(); // anychatSDK is the instance of sdk 

let initOpt: AnyChatInitOpt = new AnyChatInitOpt(nickName,strUserId,  password, serverIp,serverPort,loginEvent) 

// 需要传入应用 id 签名 和时间戳 

initOpt.setAppId(appId); initOpt.setSign(sign); initOpt.setTimeStamp(timeStamp); 

anychatSDK.sdkInit(initOpt);// 初始化 

#### 签名登录具体流程如下: 

本文档使用 看云 构建 

- 18 - 

登录方式说明 

1. 业务系统需部署身份验证系统,当用户在业务系统的登录页面输入用户账号和密码进行登录时,身份验证系 统首先验证用户登录信息的合法性,如验证通过,则根据应用id和用户账号生成签名信息,并将签名信息返 回给前端。 

2. 前端使用签名信息登录AnyChat服务器,AnyChat服务器返回登录结果. 

#### 应用签名的生成请参考以下示例程序: 

|语言|下载包|
|---|---|
|java|AnyChatSignDemo.rar|
|PHP|AnyChatSignDemoForPHP.rar|
|Nodejs|AnyChatSignDemoForNodejs.rar|

本文档使用 看云 构建 

- 19 - 

服务器连接断开通知事件 

# 服务器连接断开通知事件 

#### 1.注册连接断开事件 

registerLinkCloseEvent(linkCloseEvent: AnyChatLinkCloseEvent) 

#### 接口说明: 

注册连接断开事件的监听 

#### 返回值: 

无 

#### 示例代码: 

- // anychatSDK is the instance of sdk anychatSDK.registerLinkCloseEvent(linkCloseEvent); 

#### 2.注销连接断开事件 

unregisterLinkCloseEvent(linkCloseEvent: AnyChatLinkCloseEvent) 

#### 接口说明: 

注销连接断开事件的监听 

#### 返回值: 

无 

#### 示例代码: 

- // anychatSDK is the instance of sdk anychatSDK.unregisterLinkCloseEvent(linkCloseEvent); 

本文档使用 看云 构建 

- 20 - 

会话保持注册和销毁事件 

# 会话保持注册和销毁事件 

#### 1.注册会话保持事件 

registerSessionKeepEvent(sessionKeepEvent: AnyChatSessionKeepEvent) 

#### 接口说明: 

注册会话保持事件的监听 

#### 返回值: 

无 

#### 示例代码: 

// anychatSDK is the instance of sdk anychatSDK.registerSessionKeepEvent(sessionKeepEvent); 

#### 2.注销会话保持事件 

void unregisterSessionKeepEvent(sessionKeepEvent: AnyChatSessionKeepEvent) 

#### 接口说明: 

注销会话保持事件的监听 

#### 返回值: 

无 

#### 示例代码: 

- // anychatSDK is the instance of sdk anychatSDK.unregisterSessionKeepEvent(sessionKeepEvent); 

本文档使用 看云 构建 

- 21 - 

房间管理 

# 房间管理 

### 房间管理 

#### 房间概述: 

AnyChat SDK 提出了房间的概念,房间与房间之间相互隔离,同一个房间内的 用户才能进行交流, 音视频通话、文字沟通、录音录像、拍照等功能都需要在房间内完成。 

#### 模块简述: 

除了音视频交互功能需要本流程之外,没有特殊说明,其他功能都不需要本流程,应用层将房间 Id 传 入,进入指定的房间,只有在同一个房间内的用户才能进行音视频交互,简而言之,要进行视频通话的双方 必须要在同一房间内。 

#### 简要流程: 

注册房间管理事件 -> 进入房间 -> 获取房间中的用户列表 -> 房间内音视频操作(详情请查看音 视频操作模块介绍)或者文字交流 -> 注销房间管理事件及退出房间 

本文档使用 看云 构建 

- 22 - 

注册房间管理事件 

# 注册房间管理事件 

### 注册房间管理事件 

registerRoomEvent(roomEvent: AnyChatRoomEvent); 

#### 接口说明: 

注册房间管理事件有如下几类: 

1. 用户进出房间通知事件 

2. 房间用户数变化通知事件 

3. 文字消息接收通知事件 

#### 返回值: 

无 

#### 接口参数简介: 

|名称|类型|说明|是否必须|
|---|---|---|---|
|roomEvent|AnyChatRoomEv ent|房间内管理事件通 知|是|

#### AnyChatRoomEvent回调简介: 

|返回值|名称|参数(类型):说 明|接口说明|备注|
|---|---|---|---|---|
|void|onRoomUse rInAndOut|userId:用户 id action:1表示 进入房间,0 表示退出房间|用户进出房间 通知事件|无|
|void|onRoomUse rChanged|userNum:房 间里的人数 roomId:房间 Id|房间用户数变 化通知事件|无|
|void 本文档使用看云构建|onRoomUse rMsgReceive d|dwFromUser id:发送方用户 Id dwToUserid: 接收方用户Id bSecret:是否|文字消息接收 方需要在sdk 初始化配置 项,设置接收 消息的回调函 数,才能接收|无 - 23 -|

- 23 - 

注册房间管理事件 

私发 数,才能接收 msg:消息内 他人发过来的 容 消息 

#### 示例代码: 

// anychatSDK is the instance of sdk anychatSDK.registerRoomEvent(roomEvent);// 注册 

本文档使用 看云 构建 

- 24 - 

注销房间管理事件 

# 注销房间管理事件 

### 注销房间管理事件 

unregisterRoomEvent(roomEvent: AnyChatRoomEvent); 

#### 接口说明: 

注销房间管理事件 

#### 返回值: 

无 

#### 接口参数简介: 

|名称|类型|说明|是否必须|
|---|---|---|---|
|roomEvent|AnyChatRoomEv ent|房间内管理事件通 知|是|

#### 示例代码: 

// anychatSDK is the instance of sdk anychatSDK.unregisterRoomEvent(roomEvent);// 注销 

本文档使用 看云 构建 

- 25 - 

进入房间 

# 进入房间 

### 进入房间 

enterRoom(roomId: string, password: string, callbackEvent: AnyChatCallbackEven t) 

#### 接口说明: 

进入指定房间,密码由业务服务器( anychat 服务器)设置 

#### 返回值: 

无 

#### 接口参数简介: 

|名称|类型|说明|是否必须|
|---|---|---|---|
|roomId|string|房间id|是|
|password|string|密码|否|
|callbackEvent|AnyChatCallbac kEvent|进入房间回调|是|

#### AnyChatCallbackEvent回调简介: 

|返回值|名称|参数(类型):说 明|接口说明|备注|
|---|---|---|---|---|
|void|onCallbackE vent|result(AnyCh atResult) :执 行结果 JsonData(ob ject):返回数 据|进入房间回调|result.errCod e: 0表示成 功,其他表示 错误代号 result.errMs g: 错误描述 JsonData["ro omId"]:房间 Id|

#### 示例代码: 

// anychatSDK is the instance of sdk 

// 执行进入指定房间 password 可以为空 

anychatSDK.enterRoom(mRoomID,password,callbackEvent); 

本文档使用 看云 构建 

- 26 - 

进入房间 

本文档使用 看云 构建 

- 27 - 

获取房间中的用户列表 

# 获取房间中的用户列表 

### 获取房间中的用户列表 

getRoomUsers(): ArrayList<number> 

#### 接口说明: 

获取当前所在房间内的所有用户 id ,包括自己 

#### 返回值: 

当前房间内的所有用户 id 

#### 示例代码: 

// anychatSDK is the instance of sdk // 获取房间内所有成员列表 

const roomUsers: ArrayList<number> = anychatSDK.getRoomUsers(); 

本文档使用 看云 构建 

- 28 - 

房间内的文字交流 

# 房间内的文字交流 

### 房间内的文字交流 

sendMsg(msg: string, targetUsers: ArrayList<number>) 

#### 接口说明: 

向当前房间内指定的用户发送文字消息,当 targetUsers 为空时,为群发消息,房间内所有成员可见。 

#### 返回值: 

无 

#### 接口参数简介: 

|名称|类型|说明|是否必须|
|---|---|---|---|
|msg|string|文字消息|是|
|targetUsers|ArrayList<numb er>|接收消息的目标用 户,此参数不设置 默认为群聊|无|

#### 示例代码: 

// anychatSDK is the instance of sdk // 发送信息 

anychatSDK.sendMsg(msg,targetUsers); 

本文档使用 看云 构建 

- 29 - 

退出房间 

# 退出房间 

### 退出房间 

leaveRoom() 

#### 接口说明: 

退出当前所在的房间 , 在退出房间时需要执行该方法 

#### 返回值: 

无 

#### 示例代码: 

// anychatSDK is the instance of sdk anychatSDK.leaveRoom();// 退出房间 

本文档使用 看云 构建 

- 30 - 

音视频操作 

# 音视频操作 

##### 音视频互动 

视频呼叫 

录制(录音录像) 

视频拍照 音视频参数配置 

本文档使用 看云 构建 

- 31 - 

音视频互动 

# 音视频互动 

## 音视频互动 

#### 模块简述: 

注意 : 通话双方如果需要进行音视频通话,前提是需要进入到同一个房间才能进行通话。 

#### 简要流程: 

打开本地音视频设备 -> 接收对方音视频流 -> 开始音视频通话 -> 通话结束, 结束对方音视频流 -> 关闭本 地音视频设备 

本文档使用 看云 构建 

- 32 - 

本地麦克风管理 

# 本地麦克风管理 

##### 打开本地麦克风 

##### 关闭本地麦克风 

本文档使用 看云 构建 

- 33 - 

本地麦克风管理 

# 打开本地麦克风 

## 打开本地麦克风 

// anychatSDK is the instance of sdk 

const microphones: ArrayList<AnyChatMicrophone> = anychatSDK.getMicrophones 

##### ();// 获取本地麦克风对象列表 

const microphone: AnyChatMicrophone = microphones[0];// 选择第一个本地麦克风对象 microphone.open();// 打开本地麦克风 

#### 接口说明 

打开本地麦克风 

#### 接口返回值 

无 

#### 接口参数简介 

无 

本文档使用 看云 构建 

- 34 - 

本地麦克风管理 

# 关闭本地麦克风 

## 关闭本地麦克风 

microphone.close(); 

#### 接口说明 

关闭本地麦克风 

#### 接口返回值 

无 

#### 接口参数简介 

无 

本文档使用 看云 构建 

- 35 - 

本地摄像头管理 

# 本地摄像头管理 

##### 打开本地摄像头 

关闭本地摄像头 切换本地摄像头 

本文档使用 看云 构建 

- 36 - 

本地摄像头管理 

# 打开本地摄像头 

## 打开本地摄像头 

- // anychatSDK is the instance of sdk 

- const cameras: ArrayList<AnyChatCamera> = anychatSDK.getCameras(context);// 

- 获取本地摄像头对象列表 

   - AnyChatCamera camera = cameras[0];// 选择前置摄像头对象 

   - camera.open();// 打开摄像头 

#### 接口说明 

打开本地摄像头 

#### 接口返回值 

无 

#### 接口参数简介 

|名称|类型|说明|是否必须|
|---|---|---|---|
|context|Context|上下文|是|

本文档使用 看云 构建 

- 37 - 

本地摄像头管理 

# 关闭本地摄像头 

## 关闭本地摄像头 

camera.close(); 

#### 接口说明 

关闭本地摄像头 

#### 接口返回值 

无 

#### 接口参数简介 

无 

本文档使用 看云 构建 

- 38 - 

本地摄像头管理 

# 切换本地摄像头 

## 切换本地摄像头 

camera.switchCamera(); 

#### 接口说明 

切换本地摄像头( camera 为获取的本地摄像头数组) 

#### 接口返回值 

无 

#### 接口参数简介 

无 

本文档使用 看云 构建 

- 39 - 

接收/终止对方音频流 

# 接收/终止对方音频流 

##### 接收远程音频流 关闭远程音频流 

本文档使用 看云 构建 

- 40 - 

接收/终止对方音频流 

# 接收远程音频流 

## 接收远程音频流 

getRemoteAudioStream(remoteUserId: number): number 

#### 接口说明 

##### 接收远程音频流 

#### 接口返回值 

|名称|类型|说明|
|---|---|---|
|status|number|指令是否执行,0表示执 行,否则为其它错误码|

#### 接口参数简介 

|名称|类型|说明|是否必须|
|---|---|---|---|
|remoteUserId|number|远程对方的 userID|是|

本文档使用 看云 构建 

- 41 - 

接收/终止对方音频流 

# 关闭远程音频流 

## 关闭远程音频流 

cancelRemoteAudioStream(remoteUserId: number): number 

#### 接口说明 

关闭远程音频流 

#### 接口返回值 

|名称|类型|说明|
|---|---|---|
|status|number|指令是否执行,0表示执 行,否则为其它错误码|

#### 接口参数简介 

|名称|类型|说明|是否必须|
|---|---|---|---|
|remoteUserId|number|远程对方的 userID|是|

本文档使用 看云 构建 

- 42 - 

接收/终止对方视频流 

# 接收/终止对方视频流 

##### 获取远程视频流 

##### 关闭远程视频流 

本文档使用 看云 构建 

- 43 - 

接收/终止对方视频流 

# 获取远程视频流 

## 获取远程视频流 

getRemoteVideoStream(context: Context ,xComponentId: string,remoteUserId: numbe r): number 

#### 接口说明 

获取远程视频流 

#### 接口返回值 

|名称|类型|说明|
|---|---|---|
|status|number|执行结果 0为正常,其他 为错误|

#### 接口参数 

|名称|类型|说明|是否必须|
|---|---|---|---|
|context|Context|上下文|是|
|xComponentId|string|渲染组件id|是|
|remoteUserId|number|远程对方的 userID|是|

本文档使用 看云 构建 

- 44 - 

接收/终止对方视频流 

# 关闭远程视频流 

## 关闭远程视频流 

cancelRemoteVideoStream(xComponentId: string, remoteUserId: number) 

#### 接口说明 

关闭远程视频流 

#### 接口返回值 

无 

#### 接口参数简介 

|名称|类型|说明|是否必须|
|---|---|---|---|
|xComponentId|string|渲染组件id|是|
|remoteUserId|int|远程对方的 userID|是|

本文档使用 看云 构建 

- 45 - 

视频呼叫 

# 视频呼叫 

## 视频呼叫 

#### 模块简述: 

- 视频呼叫业务逻辑主要实现两个终端(PC、手机、Pad等)之间的通话请求流程控制。 

- 包括请求、回复、开始以及结束等过程。 

- 可以形象理解为打电话的流程:拨号、等待、通话、挂断。 

#### 简要流程: 

注册视频呼叫事件 -> 视频呼叫初始化 -> 发起视频呼叫 -> 接受呼叫请求 -> 开始音视频通话(详情请查 看音视频操作模块介绍) -> 通话过程结束,注销视频呼叫事件 

本文档使用 看云 构建 

- 46 - 

注册视频呼叫事件 

# 注册视频呼叫事件 

### 注册视频呼叫事件 

registerVideoCallEvent(videoCallEvent: AnyChatVideoCallEvent) 

#### 接口说明: 

注册视频呼叫回调事件通知 

#### 返回值: 

无 

#### 接口参数简介: 

|名称|类型|说明|是否必须|
|---|---|---|---|
|videoCallEvent|AnyChatVideoC allEvent|视频呼叫回调类|是|

#### AnyChatVideoCallEvent回调简介: 

|返回值|名称|参数(类型):说 明|接口说明|备注|
|---|---|---|---|---|
|void|onReceiveVi deoCallRequ est|JsonData(str ing):状态数据|接收视频呼叫 请求|JsonData.us erId:对方用户 id|
|void|onReceiveVi deoCallStart|JsonData(str ing):状态数据|接收视频呼叫 开始通知|JsonData.us erId 对方用户 id JsonData.ro omId 系统分 配的房间号, 呼叫双方进入 到该房间,打 开自己的摄像 头,请求对方 的视频流,开 始视频通话, 具体参见音视 频呼叫接口|
|本文档使用看云构建||||JsonData.err - 47 -|

- 47 - 

~~注册视频呼叫事件~~ 

|void ~~注册视频呼叫事件~~|onReceiveVi deoCallFinis h|JsonData(str ing):状态数据|接收视频呼叫 结束通知|orCode错误 码 JsonData.err orMsg错误信 息|
|---|---|---|---|---|
|void|onReceiveVi deoCallError|JsonData(str ing):状态数据|接收视频呼叫 异常通知|JsonData.err orCode错误 码 JsonData.err orMsg错误信 息 100101呼叫 方取消视频请 求 100102被呼 叫方不在线 100103被呼 叫方忙 100104对方 拒绝视频请求 100105会话 请求超时 100106网络 断线 100107被呼 叫方不在呼叫 状态|

#### 示例代码: 

// anychatSDK is the instance of sdk anychatSDK.registerVideoCallEvent(videoCallEvent);// 注册 

本文档使用 看云 构建 

- 48 - 

客户呼叫 

# 客户呼叫 

### 客户呼叫 

requestVideoCall(userId: number): number 

#### 接口说明: 

呼叫指定用户,被呼叫方会接收到视频呼叫请求通知( AnyChatVideoCallEvent 事件中的 onReceiveV ideoCallRequest 回调通知) 

#### 返回值: 

0— 成功 其他错误代码 

#### 接口参数简介: 

|名称|类型|说明|是否必须|
|---|---|---|---|
|userId|number|被呼叫方用户ID|是|

#### 示例代码: 

// anychatSDK is the instance of sdk 

int  status = anychatSDK.requestVideoCall(userId);// 发起呼叫 

本文档使用 看云 构建 

- 49 - 

客户取消呼叫 

# 客户取消呼叫 

### 客户取消呼叫 

cancelVideoCall(userId: number): number 

#### 接口说明: 

视频呼叫发起方取消呼叫,被呼叫方会接收到视频呼叫异常通知( AnyChatVideoCallEvent 事件中的 onR eceiveVideoCallError 回调通知) 

#### 返回值: 

0— 成功 其他错误代码 

#### 接口参数简介: 

|名称|类型|说明|是否必须|
|---|---|---|---|
|userId|number|被呼叫方用户ID|是|

#### 示例代码: 

// anychatSDK is the instance of sdk 

let status = anychatSDK.cancelVideoCall(userId);// 取消呼叫 

本文档使用 看云 构建 

- 50 - 

接听视频呼叫 

# 接听视频呼叫 

### 接受视频呼叫 

acceptVideoCall(userId: number): number 

#### 接口说明: 

接受呼叫请求,双方将会收到视频通话开始通知( AnyChatVideoCallEvent 事件中的 onReceiveVideo CallStart 回调通知) 

#### 返回值: 

0— 成功 其他错误代码 

#### 接口参数简介: 

|名称|类型|说明|是否必须|
|---|---|---|---|
|userId|number|呼叫方用户ID|是|

#### 示例代码: 

// anychatSDK is the instance of sdk 

let status =  anychatSDK.acceptVideoCall(userId);// 接受呼叫 

本文档使用 看云 构建 

- 51 - 

拒绝接听 

# 拒绝接听 

### 拒绝接听 

rejectVideoCall(userId: number): number 

#### 接口说明: 

拒绝视频呼叫请求 , 呼叫方将会收到被拒绝通知( AnyChatVideoCallEvent 事件中的 onReceiveVideoC allError 回调通知) 

#### 返回值: 

0— 成功 其他错误代码 

#### 接口参数简介: 

|名称|类型|说明|是否必须|
|---|---|---|---|
|userId|int|呼叫方用户ID|是|

#### 示例代码: 

// anychatSDK is the instance of sdk 

let  status = anychatSDK.rejectVideoCall(userId);// 拒绝接听 

本文档使用 看云 构建 

- 52 - 

挂断通话 

# 挂断通话 

### 挂断通话 

hungupVideoCall(userId: number): number 

#### 接口说明: 

挂断 , 可由视频呼叫任何一方执行,双方将会收到视频通话挂断通知( AnyChatVideoCallEvent 事件中的 onReceiveVideoCallFinish 回调通知) 

#### 返回值: 

0— 成功 其他错误代码 

#### 接口参数简介: 

|名称|类型|说明|是否必须|
|---|---|---|---|
|userId|number|对方用户ID|是|

#### 示例代码: 

// anychatSDK is the instance of sdk 

let  status = anychatSDK.hungupVideoCall(userId);// 挂断通话 

本文档使用 看云 构建 

- 53 - 

注销视频呼叫事件 

# 注销视频呼叫事件 

### 注销视频呼叫事件 

unregisterVideoCallEvent(videoCallEvent: AnyChatVideoCallEvent) 

#### 接口说明: 

注销视频呼叫回调事件通知 

#### 返回值: 

无 

#### 接口参数简介: 

|名称|类型|说明|是否必须|
|---|---|---|---|
|videoCallEvent|AnyChatVideoC allEvent|视频呼叫回调类|是|

#### 示例代码: 

// anychatSDK is the instance of sdk 

anychatSDK.unregisterVideoCallEvent(videoCallEvent);// 注销 

本文档使用 看云 构建 

- 54 - 

录制(录音录像) 

# 录制(录音录像) 

## 录制(录音录像) 

#### 模块简述: 

录制时,支持多个录像或者个人录像,请确保正在视频通话中, SDK 提供如下相应的接口 

1. 开始录制 

2. 在录像中添加图片水印(可选) 

3. 在录像中添加文字水印(可选) 

4. 在录像中插入图片(可选) 

5. 更新录像参数 

6. 结束录制 

#### 简要流程: 

开始录制 --> 结束录制 

本文档使用 看云 构建 

- 55 - 

开始录制 

# 开始录制 

### 开始录制 

startRecord(recordOpt: AnyChatRecordOpt, recordEvent: AnyChatRecordEvent): numb er 

#### 接口说明: 

开始录制,录像可以录制单方视频流,也可以录制多方视频流。 

#### 返回值: 

录制操作返回的状态码( 0 代表录制成功 ) 

#### 接口参数简介 : 

|名称|类型|说明|是否必须|
|---|---|---|---|
|recordOpt|AnyChatRecord Opt|录制配置类|是|
|recordEvent|AnyChatRecordE vent|录制结果回调事件|是|

### 开始录制(主要用于录像状态检测) 

startRecord( recordOpt: AnyChatRecordOpt, notifyEvent: AnyChatRecordNotifyEvent , recordEvent: AnyChatRecordEvent): number 

#### 接口说明: 

开始录制,主要用于服务器录制、服务器合成流录制时,检测录像状态是否正常。 

#### 返回值: 

录制操作返回的状态码( 0 代表录制成功 ) 

#### 接口参数简介 : 

|名称|类型|说明|是否必须|
|---|---|---|---|
|recordOpt|AnyChatRecord Opt|录制配置类|是|

本文档使用 看云 构建 

- 56 - 

开始录制 

|notifyEvent|AnyChatRecord NotifyEvent|录像状态回调(针 对服务器录制、服 务器合成流)|是|
|---|---|---|---|
|recordEvent|AnyChatRecordE vent|录制结果回调事件|是|

AnyChatRecordOpt录制配置类简介: 

|名称|类型|说明|是否必须|
|---|---|---|---|
|userID|number|用户id|是|
|recordLayoutOp t|AnyChatRecordL ayoutOpt|录制画面布局配置 类|是|
|width|number|录制画面宽度|否|
|height mode|number number|录制画面高度 录制模式 BRAC_RECORD_ LOCAL_MODE-- 本地录制(默认) BRAC_RECORD_ SERVER_MODE - -服务器端录制 BRAC_RECORD_ STREAM_MODE --服务器端合成流 录制|否 否|
|content fileType 本文档使用看云构建|number number|录制内容 BRAC_RECORD_ DEFAULT_CONT ENT--既录音又录 像(默认) BRAC_RECORD_ AUDIO--只录音 BRAC_RECORD_ VIDEO--只录像 录制文件类型 BRAC_RECORD_ FILE_TYPE_MP4- - MP4(默认) BRAC_RECORD_ FILE_TYPE_WMV —WMV|否 否 - 57 -|

- 57 - 

|开始录制||BRAC_RECORD_ FILE_TYPE_FLV-- FLV BRAC_RECORD_ FILE_TYPE_MP3- - MP3||
|---|---|---|---|
|fileName|string|录制文件名|否|
|category|string|设置录像文件保存 目录(针对服务器 录制有效)|否|
|localFilePath|string|本地录制文件存放 目录|否|
|encryptionKey|string|本地录制文件加密 的密钥 为空不加密,传了 密钥普通加密|否|
|recordClipMode 本文档使用看云构建|number|裁剪模式 BRAC_RECORD_ CLIPMODE_UNK NOW--未知模 式,不需要做裁剪 时使用 BRAC_RECORD_ CLIPMODE_AUT O--以最大比例进 行裁剪,然后再整 体拉伸,画面保持 比例,但被裁剪画 面较大 BRAC_RECORD_ CLIPMODE_OVE RLAP--重叠模 式,只取最大有效 部分,对边缘进行 裁剪 BRAC_RECORD_ CLIPMODE_SHRI NK--缩小模式, 缩小到合适的比 例,不进行裁剪 BRAC_RECORD_ CLIPMODE_STRE||

- 58 - 

|开始录制||TCH--平铺模式, 不进行裁剪,但可 能导致画面不成比 例||
|---|---|---|---|
|statusnotify|number|录像状态回调通知 时间设置,默认时 间为10秒(针对服 务器录制、服务器 合成流录制有效)|否|
|videobitrate|number|录制视频码率 单 位:bps|否|
|audiobitrate|number|录制音频码率 单 位:bps|否|
|fps|number|录像帧率|否|
|channels|number|录制音频通道: 1 单通道,2双通道|否|
|isOpenMD5|boolean|录像完成回调是否 返回文件MD5值|否|

AnyChatRecordLayoutOpt 录制画面布局配置类简介: 

|返回值|名称|说明|备注|
|---|---|---|---|
|recordlayout|number|视频布局,视频流 数量,即多少个视 频画面|是|
|layoutstyle|number|三路流和四路流的 视频画面布局风 格:0-并列风格 (默认) ,1-画 中画风格,2-三画 面并列风格|否|
|本文档使用看云构建||录制对象 AnyChatRecordS treamOpt的list集 合。 AnyChatRecordS treamOpt对象包 含三个属性: 1、 userID(string)录 制对象ID||

- 59 - 

开始录制 

|2、 streamIndex(nu mber):录制对象 的视频流号,移动 端默认为0; 3、 recordIndex(nu mber):录制对象 在录制视频上的位 置|
|---|

##### AnyChatRecordNotifyEvent回调简介: 

|返回值|名称|说明|备注|
|---|---|---|---|
|void|onRecordStatus Done|result(AnyChatR esult): 操作状态 信息 JsonData(JSON Object):返回结果|result.errCode: 0 表示成功 其他表示错误代 号. result.msg: 错误 描述|

##### AnyChatRecordEvent回调简介: 

|返回值|名称|说明|备注|
|---|---|---|---|
|void|onRecordStart|result(AnyChatR esult): 操作状态 信息 JsonData(object) :返回结果|result.errCode: 0 表示成功 其他表示错误代 号. result.msg: 错误 描述. JsonData.userId: 用户id JsonData.status: 录像状态,值 为"prepare" "start" JsonData.statusc ode:录像状态,1 为prepare 2为 start|
|本文档使用看云构建|||result.errCode: 0 表示成功 其他表示错误代 - 60 -|

- 60 - 

|void 开始录制|onRecordDone|result(AnyChatR esult): 操作状态 信息 JsonData(object) :返回结果|其他表示错误代 号. result.msg: 错误 描述. JsonData.filePat h:录像文件地址 JsonData.elapse: 录像文件时长 JsonData.startTi me:录像开始时间 JsonData.endTi me:录像结束时间 JsonData.filemd 5:录像md5|
|---|---|---|---|

##### 示例代码 

startRecord(): number { 

let recordOpt: AnyChatRecordOpt = new AnyChatRecordOpt(); 

recordOpt.setMode(AnyChatRecordMode.BRAC_RECORD_LOCAL_MODE);// 设置为本地录制 if (null != flePath) { 

recordOpt.setLocalFilePath(flePath + "/record");// 设置本地存储路径 

} 

recordOpt.setRecordClipMode(AnyChatRecordClipMode.BRAC_RECORD_CLIPMODE_AUTO );// 设置裁剪模式 

recordOpt.setUserID(-1); 

recordOpt.setContent(AnyChatRecordContent.BRAC_RECORD_DEFAULT_CONTENT);// 设置既录音又录像 

let streamlist: ArrayList<AnyChatRecordStreamOpt> = new ArrayList<AnyChatRe cordStreamOpt>(); 

let recordEntity: AnyChatRecordStreamOpt = new AnyChatRecordStreamOpt(); recordEntity.setUserID(-1); 

// 设置录制对象的视频流号 recordEntity.setStreamindex(0); // 设置录制对象在录制画面上的位置 recordEntity.setRecordindex(0); streamlist.add(recordEntity); 

let recordEntity_1: AnyChatRecordStreamOpt = new AnyChatRecordStreamOpt(); recordEntity_1.setUserID(dwTargetUserId); 

// 设置录制对象的视频流号 recordEntity_1.setStreamindex(0); 

// 设置录制对象在录制画面上的位置 recordEntity_1.setRecordindex(1); streamlist.add(recordEntity_1); 

本文档使用 看云 构建 

- 61 - 

开始录制 

recordOpt.setImagepath(picPath); 

let fileName: string = "" + System.currentTimeMillis(); 

recordOpt.setFileName(fileName); 

let anyChatRecordLayoutOpt: AnyChatRecordLayoutOpt = new AnyChatRecordLayou tOpt(); 

anyChatRecordLayoutOpt.setRecordlayout(2); 

anyChatRecordLayoutOpt.setStreamlist(streamList); 

recordOpt.setAnyChatRecordLayoutOPt(anyChatRecordLayoutOpt); return AnyChatSDK.getInstance().startRecord(recordOpt, this); 

} 

本文档使用 看云 构建 

- 62 - 

在录制文件中添加图片水印 

# 在录制文件中添加图片水印 

## 在录制文件中添加图片水印 

如需在录制文件中添加图片水印,则在开始录制方法中的 AnyChatRecordOpt 的配置类中添加图片水印 如下的属性。 

注意:使用该功能需要具有双录授权 

|名称|类型|说明|是否必须|
|---|---|---|---|
|picAlpha|number|透明度, 默认100, 不透明|否|
|picPosx|number|图片水印在x轴方 向上的起始位置 (百分比,范围 0~100),默认为5|否|
|picPosy|number|图片水印在y轴方 向上的起始位置 (百分比,范围 0~100),默认 为5|否|
|overlayimgwidth|number|水印图片宽度,默 认75|否|
|overlayimgheigh t|number|水印图片高度,默 认35|否|
|imagepath|string|传入水印图片路径 (若传该值则添加 了图片水印)|是|

本文档使用 看云 构建 

- 63 - 

在录制文件中添加文字水印 

# 在录制文件中添加文字水印 

## 在录制文件中添加文字水印 

如需在录制文件中添加文字水印,则在开始录制方法中的 AnyChatRecordOpt 的配置类中添加图片水印 如下的属性。 

注意:使用该功能需要具有双录授权 

|名称|类型|说明|是否必须|
|---|---|---|---|
|fontcolor|string|水印文字颜色,文 字默认为白色 (0xffffff,颜色 值采用十六进制 rgb格式),可不 传(不传时,将应 用默认值)|否|
|textAlpha|number|水印文字的透明 度,默认为100, 可不传(不传时, 将应用默认值)|否|
|textPosx|number|文字水印在x轴方 向上的起始位置 (百分比,范围 0~100)|否|
|textPosy|number|文字水印在y轴方 向上的起始位置 (百分比,范围 0~100)|否|
|fontsize|number|水印文字大小,默 认为23号大小, 可不传(不传时, 将应用默认值)|否|
|useservertime|number|时间戳使用时间 1:服务器时间 0:本地时间(默 认)|否|
|text 本文档使用看云构建|string|文字内容,若加上 [timestamp],则 表示增加时间戳, 例|是 - 64 -|

- 64 - 

在录制文件中添加文字水印 

|||如“HelloAnyCh at[timestamp]”||
|---|---|---|---|
|fontfile|string|文字水印字体库绝 对路径信息|是|

本文档使用 看云 构建 

- 65 - 

在录像中插入图片 

# 在录像中插入图片 

### 在录像中插入图片 

##### 注意:使用该功能需要具有双录授权 

insertFileDuringRecord(recordindex: number, fileName: string): number 

#### 接口说明: 

在录像中插入图片 , 在录制开启之后,可以在录制画面的某个区域插入图片,本接口可以重复调用,实现 图片切换的效果(常用场景为 PPT 播放) 

#### 返回值: 

##### 插入图片操作的状态码( 0 为成功) 

#### 接口参数简介: 

|名称|类型|说明|是否必须|
|---|---|---|---|
|recordIndex|number|录制流编号|是|
|fileName|string|插入的图片|是|

本文档使用 看云 构建 

- 66 - 

更新录像参数 

# 更新录像参数 

### 更新录像参数 

##### mAnyChatSDK.updateRecord(recordOpt) 

##### 接口说明 

开始录制后,可调用该接口修改录像的画面数及画面布局。 

##### 返回值 

录制操作返回的状态码( 0 代表录制成功 ) 

##### 接口参数简介 

|名称|类型|说明|是否必须|
|---|---|---|---|
|recordOpt|AnyChatRecord Opt|录制配置类|是|
|recordOpt对象可传属性简 名称|介 类型|说明|是否必须|
|recordLayoutOp t|AnyChatRecordL ayoutOpt|录制画面布局配置|是|

##### recordLayoutOpt 录制画面布局配置类简介: 

|返回值|名称|说明|备注|
|---|---|---|---|
|recordlayout|number|视频布局,视频流 数量,即多少个视 频画面|是|
|layoutstyle|number|三路流和四路流的 视频画面布局风 格:0-并列风格 (默认) ,1-画 中画风格,2-三画 面并列风格|是|
|本文档使用看云构建||录制画面各个区域 对应的视频流。视||

- 67 - 

|streamlist 更新录像参数|ArrayList<Anych atRecordStream Opt>|频流对象包含三个 属性: 1、userid录制对 象ID; 2、 streamindex:录 制对象的视频流 号; 3、recordindex: 录制画面编号|是|
|---|---|---|---|

本文档使用 看云 构建 

- 68 - 

结束录制 

# 结束录制 

### 结束录制 

completeRecord(): number 

#### 接口说明: 

停止录制 

#### 返回值: 

无 

#### 接口参数简介: 

无 

本文档使用 看云 构建 

- 69 - 

视频拍照 

# 视频拍照 

### 视频拍照 

模块简述: 

##### 在音视频通话中,可以抓拍音视频通话房间中任一用户的视频 

本文档使用 看云 构建 

- 70 - 

抓拍 

# 抓拍 

## 抓拍 

takeSnapShot(snapShotEntity: AnyChatSnapShotOpt, snapshotEvent: AnyChatSnapshot Event): number 

#### 接口说明 

视频抓拍接口 

#### 接口返回值 

|名称|类型|说明|
|---|---|---|
|status|number|视频抓拍操作返回的状态 码(0为成功)|

#### 接口参数简介 

|名称|类型|说明|是否必须|
|---|---|---|---|
|snapShotEntity|AnyChatSnapSh otOpt|抓拍实例化对象|是|
|snapshotEvent|AnyChatSnapsh otEvent|抓拍事件回调|是|

#### AnyChatSnapShotOpt简介 

|名称|类型|说明|是否必须|
|---|---|---|---|
|userId|number|抓拍对象ID|是|
|streamIdx|string|抓拍对象视频流编 号|是|
|fileName|string|抓拍文件自定义文 件名|是|
|localFilePath|string|抓拍文件保存地址|是|

#### AnyChatSnapshotEvent回调简介 

|返回值|名称|说明|备注|
|---|---|---|---|
|void 本文档使用看云构建|onSnapshotDon|result(AnyChatR esult): 操作状态 信息|result.errCode: 0 表示成功, 其他表示错误代 号. - 71 -|

- 71 - 

抓拍 

|void|e 信息|result.msg: 错误|
|---|---|---|
||JsonData(object)|描述.|
||:返回结果|JsonData.filePat|
|||h:抓拍文件地址|

本文档使用 看云 构建 

- 72 - 

音视频参数配置 

# 音视频参数配置 

### 音视频参数配置 

#### 模块简述: 

用户可以根据自己的需求,用过参数配置类设置音视频的各性能参数 

本文档使用 看云 构建 

- 73 - 

视频参数配置 

# 视频参数配置 

## 视频参数配置 

##### setVideoOpt(videoOpt: AnyChatVideoOpt); 

#### 接口说明: 

##### 有需要可设置视频参数,不然则采用系统默认参数 

#### 返回值: 

无 

#### 接口参数简介: 

|名称|类型|说明|是否必须|
|---|---|---|---|
|videoOpt|AnyChatVideoO pt|视频配置类|是|

AnyChatVideoOpt配置类简介: 

|名称|类型|说明|是否必须|
|---|---|---|---|
|width|number|分辨率-宽 [默 认]:320|否|
|height|number|分辨率-高[默 认]:240|否|
|fps|number|本地视频帧率[默 认]: 10|否|
|bitRate|number|本地视频码率[默 认]:400000|否|
|mCameraFacing|number|使用前置摄像头 [默认]:1,后置 摄象头:0|否|

本文档使用 看云 构建 

- 74 - 

音频参数配置 

# 音频参数配置 

## 音频参数配置 

setAudioOpt(audioOpt: AnyChatAudioOpt); 

#### 接口说明: 

##### 有需要可设置音频参数,不然则采用系统默认参数 

#### 返回值: 

无 

#### 接口参数简介: 

|名称|类型|说明|是否必须|
|---|---|---|---|
|audioOpt|AnyChatAudioO pt|音频配置类|是|
|AnyChatAudioOpt音 名称|频配置类简介: 类型|说明|是否必须|
|vadctrl|number|音频静音检测控制 (参数为:int 型:1打开,0关 闭)|否|
|nsctrl|number|音频噪音抑制控制 (参数为:int 型:1打开,0关 闭)|否|
|echoctrl|number|音频回音消除控制 (参数为:int 型:1打开,0关 闭)|否|
|agcctrl|number|音频自动增益控制 (参数为:int 型:1打开,0关 闭)|否|
|本文档使用看云构建||音频采集模式设置 音频采集模式设置|- 75 -|

- 75 - 

音频参数配置 

|capturemode|number|(参数为:int 型:0 发言模式, 1 放歌模式,2 卡|否|
|---|---|---|---|
|||拉OK模式,3// 线路输入模式)||

本文档使用 看云 构建 

- 76 - 

文件传输 

# 文件传输 

### 文件传输 

#### 模块简述: 

支持客户端之间、客户端跟服务器之间的文件传输功能,支持断点续传 

##### 简要流程: 

初始化文件模块 -> 注册文件发送通知事件 -> 创建文件操作任务 -> 执行开始任务操作 

##### 文件操作任务类型有2种: 

1. 文件下载(需要登录,无需进入房间) 

2. 文件发送到指定用户(需要登录,无需进入房间) 

本文档使用 看云 构建 

- 77 - 

初始化文件模块 

# 初始化文件模块 

### 初始化文件模块 

initFileOpt(AnyChatFileOpt fileOpt) 

#### 接口说明: 

重要流程,初始化文件模块的基本配置 , 文件的各种操作才能执行 

#### 返回值: 

无 

#### 接口参数简介: 

|名称|类型|说明|是否必须|
|---|---|---|---|
|fileOpt|AnyChatFileOpt|文件配置类|是|

#### AnyChatFileOpt 配置类简介: 

|名称|类型|说明|是否必须|
|---|---|---|---|
|setSavePath(Stri ng path )|类方法|自定义接受文件的 路径方法,返回参 数为0,即设置成 功|否|

#### 示例代码: 

```arkts
let fileOpt: AnyChatFileOpt = new AnyChatFileOpt(); fileOpt.setSavePath(path);// 可以自定义文件存储路径,没需要可以不设置 // anychatSDK is the instance of sdk anychatSDK.initFileOpt(fileOpt);// 初始化文件传输模块 
```

本文档使用 看云 构建 

- 78 - 

注册文件接收通知事件 

# 注册文件接收通知事件 

### 注册文件接收通知事件 

registerFileReceivedEvent(e: AnyChatFileReceivedEvent) 

#### 接口说明: 

注册用户间发送文件时接收文件通知事件 

#### 返回值: 

无 

#### 接口参数简介: 

|名称|类型|说明|是否必须|
|---|---|---|---|
|e|AnyChatFileRece ivedEvent|注册用户间发送文 件时接收文件通知 事件|是|

#### AnyChatFileReceivedEvent回调简介: 

|返回值|名称|参数(类型):说 明|接口说明|备注|
|---|---|---|---|---|
|void 本文档使用看云构建|onFileReceiv ed|JsonData(ob ject):返回数 据|收到文件通知 事件|JsonData.file Name:文件名 JsonData.dw Userid: 用户 id,指示发送用 户 JsonData.Te mpFilePath: 接收完成后, SDK 保存在 本地的临时文 件(包含完整 路径) JsonData.dw FileLength:文 件总长度 JsonData.dw - 79 -|

- 79 - 

注册文件接收通知事件 

TaskId:该文件 所对应的任务 编号 

##### 示例代码: 

// anychatSDK is the instance of sdk anychatSDK.registerFileReceivedEvent( { 

onFileReceived(JsonData: object) { 

// TODO Auto-generated method stub 

} 

});// 注册通知事件 

本文档使用 看云 构建 

- 80 - 

注销文件接收通知事件 

# 注销文件接收通知事件 

### 注销文件接收通知事件 

unRegisterFileReceivedEvent(e: AnyChatFileReceivedEvent ) 

#### 接口说明: 

注销用户间发送文件时接收文件通知事件 

#### 返回值: 

无 

#### 接口参数简介: 

|名称|类型|说明|是否必须|
|---|---|---|---|
|e|AnyChatFileRece ivedEvent|注销用户间发送文 件时接收文件通知 事件|是|

##### 示例代码: 

// anychatSDK is the instance of sdk anychatSDK.unregisterFileReceivedEvent(mFileReceived);// 注销通知事件 

本文档使用 看云 构建 

- 81 - 

创建文件传输任务 

# 创建文件传输任务 

### 创建文件传输任务 

createFileTransferTask(int userId,String localPath,int intervalTime, AnyChatFi leTransferEvent e): AnyChatTransferTask 

#### 接口说明: 

##### 创建文件传输任务,把文件发给对方(注:需要初始化) 

#### 返回值: 

文件传输任务类 

##### 接口参数说明: 

|名称|类型|说明|是否必须|
|---|---|---|---|
|userId|number|接收方用户id|是|
|localPath|string|要发送文件的路径|是|
|intervalTime|number|返回文件发送状态 的时间间隔(单 位:秒)|是|
|e|AnyChatFileTran sferEvent|状态结果回调|是|

#### AnyChatTask任务类简介: 

方法 说明 返回参数 start( ) 开始传输 void cancel( ) 取消传输 void AnyChatTaskState 对象 AnyChatTaskState.proc ess 传输进度 (0.0100.0) getStatus( ) 主动查询发送状态 AnyChatTaskState.bitR ate 传输码率,单位为 bps AnyChatTaskState.statu s 1--准备; 2--传输中; 3- - 完成; 4--任务被取消 

本文档使用 看云 构建 

- 82 - 

创建文件传输任务 

#### AnyChatFileTransferEvent回调简介: 

|返回值|名称|参数(类型):说 明|接口说明|备注|
|---|---|---|---|---|
|void|onFileTransf erDone|result(AnyCh atResult) :执 行结果 JsonData(ob ject):返回数 据|文件发送完成 通知事件|result.code: 0表示成功, 其他表示错误 代号 result.msg: 错误描述 JsonData.file Path: 接收完 成后保存的文 件路径(包含 文件名称) JsonData.file Length: 文件 长度 JsonData.file name: 文件 名称|
|void|OnTaskStatu sChanged|JsonData(ob ject):返回数 据|文件发送过程 状态通知事件|JsonData.tas kId 任务ID JsonData.pr ocess 传输进 度 (0.0- 100.0) JsonData.bit Rate 传输码 率,单位为 bps JsonData.sta tus 1--准备; 2--传输中; 3- -完成; 4--任 务被取消|

#### 示例代码: 

// anychatSDK is the instance of 

let transfertask = anychatSDK.createFileTransferTask(userId, localPath, interva lTime, { 

onFileTransferDone( result: AnyChatResult, JsonData: object) { 

本文档使用 看云 构建 

- 83 - 

创建文件传输任务 

} 

onTaskStatusChanged(JsonData: object) { 

} 

- });// 创建任务 

transfertask.start();// 开始文件传输 

本文档使用 看云 构建 

- 84 - 

文件管理 

# 文件管理 

### 文件上传到服务器 

#### 模块简述: 

提供用户将文件上传到服务器,支持断点续传 

#### 简要流程: 

初始化文件模块 -> 创建文件操作任务 -> 执行开始任务操作 

#### 文件操作任务类型有1种: 

1. 文件上传到服务器(需要登录,无需进入房间) 

本文档使用 看云 构建 

- 85 - 

初始化文件模块 

# 初始化文件模块 

### 初始化文件模块 

initFileOpt(fileOpt: AnyChatFileOpt) 

#### 接口说明: 

重要流程,初始化文件模块的基本配置 , 文件的各种操作才能执行 

#### 返回值: 

无 

#### 接口参数简介: 

|名称|类型|说明|是否必须|
|---|---|---|---|
|fileOpt|AnyChatFileOpt|文件配置类|是|

#### AnyChatFileOpt 配置类简介: 

|名称|类型|说明|是否必须|
|---|---|---|---|
|setSavePath(pat h: string)|类方法|自定义接受文件的 路径方法,返回参 数为0,即设置成 功|否|

#### 示例代码: 

// anychatSDK is the instance of let fileOpt: AnyChatFileOpt = new AnyChatFileOpt(); fileOpt.setSavePath(path);// 可以自定义文件存储路径,没需要可以不设置 anychatSDK.initFileOpt(fileOpt);// 初始化文件传输模块 

本文档使用 看云 构建 

- 86 - 

创建文件上传任务 

# 创建文件上传任务 

### 创建上传文件任务 

AnyChatUploadTask.createFileUploadTask(uploadOpt: AnyChatFileUploadOpt, e: Any ChatFileUploadEvent) 

#### 接口说明: 

##### 创建文件上传到服务器的任务(注:需要初始化) 

#### 接口参数简介: 

|名称|类型|说明|是否必须|
|---|---|---|---|
|uploadOpt|AnyChatFileUplo adOpt|文件上传配置类|是|
|e|AnyChatFileUplo adEvent|文件上传状态与结 果回调|是|

#### AnyChatFileUploadOpt 文件上传配置类简介: 

|名称|类型|说明|是否必须|
|---|---|---|---|
|localPath|string|要上传文件的绝对 路径|是|
|intervalTime|number|返回文件上传状态 时间间隔,单位: s|否|
|filename|string|指定文件上传后的 目标文件名|否|
|category|string|表示文件上传分类 子目录,通过设置 改字段可将文件上 传到不同分类子目 录中|否|
|encryptionKey 本文档使用看云构建|string|上传一个已加密录 像视频文件(参考 录制章节),在上 传到服务器时,该 文件将自动被解 密。根据加密的录 像视频文件的加密|否 - 87 -|

- 87 - 

|创建文件上传任务||秘钥,设置相同的 解密密钥||
|---|---|---|---|
|isOverlayUpload|boolean|是否覆盖上传(默 认值true相同文件 覆盖上传)|否|
|maxBitrate|number|文件上传传输最大 码率控制(为0时表 示不限制,以最快 速率传输[默认]; 否则表示限制码 率,单位为: bps)|否|
|strJson|string|文件上传用户自定 义参数(标准json 字符串形式)|否|

#### AnyChatUploadTask任务类简介: 

|方法|说明|返回参数|
|---|---|---|
|start( )|开始传输|void|
|cancel( )|取消传输|void|
|getStatus( )|主动查询发送状态|AnyChatTaskState 对象 AnyChatTaskState.proc ess 传输进度 (0.0- 100.0) AnyChatTaskState.bitR ate 传输码率,单位为 bps AnyChatTaskState.statu s 1--准备; 2--传输中; 3- -完成;4--任务被取消|

#### AnyChatFileUploadEvent回调简介: 

|返回值|名称|参数(类型):说 明|接口说明|备注|
|---|---|---|---|---|
|本文档使用看云构建||||result.code: 0表示成功, 其他表示错误 代号 result.msg: 错误描述 JsonData.Fil eName:文件 - 88 -|

- 88 - 

|void 创建文件上传任务|onFileUploa dDone|result(AnyCh atResult) :执 行结果 JsonData(ob ject):返回数 据|文件上传成功 通知事件|名 JsonData.dw Userid: 用户 id,指示发送用 户 JsonData.Te mpFilePath: 接收完成后, SDK 保存在 本地的临时文 件(包含完整 路径) JsonData.dw FileLength:文 件总长度 JsonData.dw TaskId:该文件 所对应的任务 编号|
|---|---|---|---|---|
|||||JsonData.tas kId任务ID|
|||||JsonData.tas kId 任务ID JsonData.pr ocess 传输进 度 (0.0- 100.0)|
|void|OnTaskStatu sChanged|JsonData(ob ject):返回数 据|文件上传过程 状态通知事件|JsonData.bit Rate 传输码 率,单位为 bps JsonData.sta tus 1--准备; 2--传输中; 3- -完成; 4--任 务被取消|

#### 示例代码: 

// 文件上传配置类 

let uploadOpt = new AnyChatFileUploadOpt(); // 设置上传文件的绝对路径信息 

uploadOpt.setLocalPath(filePath); 

本文档使用 看云 构建 

- 89 - 

创建文件上传任务 

##### // 设置返回文件上传状态时间间隔,单位: s 

uploadOpt.setIntervalTime(1); // 创建文件上传任务 

```arkts
let uploadTask: AnyChatUploadTask = instance.createFileUploadTask(uploadOpt, { onFileUploadDone(result: AnyChatResult, json: object) { } onTaskStatusChanged(json: object) { } }); // 开始上传 uploadTask.start(); 
```

本文档使用 看云 构建 

- 90 - 

创建文件下载任务 

# 创建文件下载任务 

### 创建文件下载任务 

createFileDownloadTask( savepath: string,String fileid,fileurl: string,filemd5 : string,filetype: number,intervalTime: number,e: AnyChatTaskStatusChangedEvent ): AnyChatDownloadTask 

#### 接口说明: 

创建文件下载任务(注:需要初始化) 

#### 返回值: 

文件下载任务类 

#### 接口参数简介: 

|名称|类型|说明|是否必须|
|---|---|---|---|
|savaPath|string|下载保存路径|是|
|fileid|string|文件id|是|
|fileurl|string|文件下载地址|是|
|filemd5|string|文件md5|否|
|filetype|number|文件类型,1:ppt 文件 2:视频文件 3:音频文件 4:普通 zip文件|是|
|intervalTime|number|返回文件状态时间 间隔,单位:s|是|
|e|AnyChatTaskStat usChangedEvent|下载文件状态与结 调|是|

#### AnyChatDownloadTask任务类简介: 

|方法|说明|返回参数|
|---|---|---|
|start( )|开始传输|void|
|cancel( )|取消传输|void|

AnyChatTaskState 对象 AnyChatTaskState.proc ess 传输进度 (0.0- 

本文档使用 看云 构建 

- 91 - 

创建文件下载任务 

getStatus( ) 

## 主动查询发送状态 

100.0) AnyChatTaskState.bitR ate 传输码率,单位为 bps AnyChatTaskState.statu s 1--准备; 2--传输中; 3- - 完成; 4--任务被取消 

#### AnyChatTaskStatusChangedEvent回调简介: 

|返回值|名称|参数(类型):说 明|接口说明|备注|
|---|---|---|---|---|
|void|onDownload Done|result(AnyCh atResult) :执 行结果 JsonData(ob ject):返回数 据|下载成功通知 事件|result.code: 0表示成功, 其他表示错误 代号 result.msg: 错误描述|
|void|OnTaskStatu sChanged|JsonData(ob ject):返回数 据|文件下载过程 状态通知事件|JsonData.tas kId 任务ID JsonData.pr ocess 传输进 度 (0.0- 100.0) JsonData.bit Rate 传输码 率,单位为 bps JsonData.sta tus 1--准备; 2--传输中; 3- -完成; 4--任 务被取消|

#### 示例代码: 

// anychatSDK is the instance of 

let downloadTask = anychatSDK.createFileDownloadTask(savepath, fileid, fileurl, filemd5, filetype,intervalTime, { 

onDownloadDone(result: AnyChatResult, jsondata: object) { 

} 

OnTaskStatusChanged(jsondata: object) { 

本文档使用 看云 构建 

- 92 - 

创建文件下载任务 

##### } 

##### });// 创建任务 

downloadTask.start();// 开始文件下载 

本文档使用 看云 构建 

- 93 - 

透明通道 

# 透明通道 

### 透明通道 

##### 模块简述: 

提供了数据传输的能力,支持客户端之间、服务器与客户端之间的缓冲区数据传输,传输的内容没有限 制。上层应用可利用透明通道传输业务层自定义的指令,并进行对应的业务逻辑处理。 

本文档使用 看云 构建 

- 94 - 

发送透明通道 

# 发送透明通道 

### 发送透明通道(扩展接口) 

transBufferEx(msg: string, targetUsers: ArrayList<number>,time: number, e: AnyC hatTransBufferReceivedEvent): number 

#### 接口说明: 

##### 透明通道传输数据,大小没有限制 

#### 返回值: 

发送透明通道请求码 

#### 接口说明: 

|名称|类型|说明|是否必须|
|---|---|---|---|
|msg|string|消息|是|
|targetUsers|ArrayList<numb er>|接受方用户id列表|是|
|time|number|判读是否发送成功 的时间间隔,单 位:s|是|
|e|AnyChatTransBu fferReceivedEve nt|发送消息是否成功 的通知事件|是|

#### AnyChatTransBufferReceivedEvent回调简介: 

|返回值|名称|参数(类型)说 明|接口说明|备注|
|---|---|---|---|---|
|void|transBufferS|status(boole|透明通道发送|true:成功 ,|
||tatus|an)|状态回调|false:失败|

#### 示例代码: 

anychatSDK.transBufferEx(msg, targetUsers,time, { transBufferStatus(status: boolean) { 

} 

});// 扩展接口发送透明通道消息 

本文档使用 看云 构建 

- 95 - 

发送透明通道 

本文档使用 看云 构建 

- 96 - 

注册接收透明通道通知事件 

# 注册接收透明通道通知事件 

### 注册接收透明通道通知事件 

registerTransBufferEvent(e: AnyChatReceiveBufferEvent) 

#### 接口说明: 

注册透明消息接收的状态通知的回调 

#### 返回值: 

无 

#### 接口参数简介: 

|名称|类型|说明|是否必须|
|---|---|---|---|
|e|AnyChatReceive BufferEvent|透明通道接收消息 的回调|是|

#### AnyChatReceiveBufferEvent回调简介: 

|返回值|名称|参数(类型):说 明|接口说明|备注|
|---|---|---|---|---|
|void|onReceiveBu ffer|JsonData(ob ject):返回数 据|接受到透明通 道通知事件|JsonData.us erId :发送方 用户ID JsonData.ms g:消息内容|

#### 示例代码: 

// anychatSDK is the instance of anychatSDK.registerTransBufferEvent({ onReceiveBuffer(JsonData: object) { 

} 

- });// 注册通知事件 

本文档使用 看云 构建 

- 97 - 

注销接收透明通道通知事件 

# 注销接收透明通道通知事件 

### 注销接收透明通道通知事件 

unregisterTransBufferEvent(e: AnyChatReceiveBufferEvent) 

#### 接口说明: 

注销透明消息接收的状态通知的回调 

#### 返回值: 

无 

#### 接口参数简介绍: 

|名称|类型|说明|是否必须|
|---|---|---|---|
|e|AnyChatReceive BufferEvent|透明通道接收消息 的回调|是|

#### 示例代码: 

// anychatSDK is the instance of anychatSDK.unregisterTransBufferEvent(bracReceiveBufferEvent); 

本文档使用 看云 构建 

- 98 - 

智能排队 

# 智能排队 

### 智能排队 

##### 模块简述: 

AnyChat 提供了业务排队功能,抽象出了业务排队应用场景中需要的营业厅、队列、坐席、客户等业务对 象,通 过调用提供的客户端 API 来操作这些对象的属性、方法及事件,如:进出营业厅、进出队列方法 ;获取排队人数、在队列中所排位置属性;进出队列、坐席服务响应事件等。通过响应不同的业务对象事件 来实现排队业务逻辑功能,开发人员只需关注业务逻辑的实现, AnyChat 会自动的维护业务对象的数据变 化。 

##### 简要流程: 

获取营业厅列表 -> 进入营业厅 -> 获取营业厅队列列表 -> 进入队列 -> 视频呼叫等音视频操作(详细请查 看音视频操作) 

本文档使用 看云 构建 

- 99 - 

初始化排队模块 

# 初始化排队模块 

### 初始化 

initQueueOpt(queueOpt: AnyChatQueueOpt) 

#### 接口说明: 

初始化智能排队配置 

#### 返回值: 

无 

#### 接口参数简介: 

|名称|类型|说明|是否必须|
|---|---|---|---|
|queueOpt|AnyChatQueue Opt|智能排队配置类|是|
|AnyChatQueueOpt 配置 名称|类简介: 类型|说明|是否必须|
|role|number|角色 0-客户 2-坐 席|是|
|priority|number|优先级|是|
|attribute|number|业务属性|否|
|setIsAutoMode( )|boolean|自动路由 0 打开 1关闭|否|
|setQueueType( )|number|队列组|否|
|setAttribute( )|number|业务属性,可以根 据业务需求传入 JSON对象|否|

#### AnyChatQueueRole类简介: 

|名称|类型|说明|
|---|---|---|
|BRAC_QUEUE_OPT_RO LE_CLIENT|number|客户|
|BRAC_QUEUE_OPT_RO LE_AGENT|number|坐席|

本文档使用 看云 构建 

- 100 - 

营业厅操作 

# 营业厅操作 

获取营业厅列表 

进入营业厅 席座服务状态设置 离开营业厅 

本文档使用 看云 构建 

- 101 - 

获取营业厅列表 

# 获取营业厅列表 

### 获取营业厅列表 

getAreas(onSyncAreasEvent: AnyChatSyncAreasEvent) 

#### 接口说明: 

获取系统配置的营业厅列表 

#### 返回值: 

无 

#### 接口参数简介: 

|名称|类型|说明|是否必须|
|---|---|---|---|
|onSyncAreasEve|AnyChatSyncAre|获取营业厅列表数 |是|
|nt|asEvent|据回调||

AnyChatSyncAreasEvent回调简介: 

|返回值|名称|参数(类型):说 明|接口说明|备注|
|---|---|---|---|---|
|void|onSyncAreas Done|result(AnyCh atResult): 执 行结果 JsonData(ob ject): 返回数 据|获取营业厅列 表结果|Result.code: 0表示成功, 其他表示错误 代号 Result.msg: 错误描述 JsonData["ar eas"] { data["id"]: 营 业厅ID data["name" ]: 营业厅名 data["desc"]: 营业厅描述 }|

本文档使用 看云 构建 

- 102 - 

进入营业厅 

# 进入营业厅 

### 进入营业厅 

enterArea(areaId: string, onEnterAreaEvent: AnyChatEnterAreaEvent) 

接口说明: 

进入指定营业厅 

#### 返回值: 

无 

#### 接口参数简介: 

|名称|类型|说明|是否必须|
|---|---|---|---|
|areadid|string|营业厅ID|是|
|onEnterAreaEve|AnyChatEnterAr|进入营业厅操作回 |是|
|nt|eaEvent|调||

AnyChatEnterAreaEvent回调简介: 

|返回值|名称|参数(类型):说 明|接口说明|备注|
|---|---|---|---|---|
|本文档使用看云构建||||result.code: 0表示成功, 其他表示错误 代号 result.msg: 错误描述. JsonData.are aId: 营业厅Id JsonData.are aName: 营业 厅名称 JsonData.are aDesc: 营业 厅描述 JsonData.gu estCount: 当 - 103 -|

|void 进入营业厅|onEnterArea Done|result(AnyCh atResult): 执 行结果 JsonData (object):返回 数据|进入营业厅回 调|前营业厅访客 的用户数(没 有排入队列的 用户) JsonData.qu eningUserCo unt: 当前营业 厅正在排队的 用户数量 JsonData.qu eueCount: 当 前营业厅的队 列数量 JsonData.qu eues: 营业厅 下的队列列表 JsonData.ag entcount: 服 务区域坐席用 户数 JsonData.idl eagentcount : 服务区域空 闲坐席数量. for (queue in data.queues) {queue.id: 队 列ID queue.name: 队列名称 queue.desc: 队列描述}|
|---|---|---|---|---|

本文档使用 看云 构建 

- 104 - 

席座服务状态设置 

# 席座服务状态设置 

### 席座服务状态设置 

agentServiceCtrl( ctrlCode: AnyChatAgentServiceCtrlCode, onServiceCtrlEvent: An yChatServiceCtrlEvent) 

#### 接口说明: 

席座的服务状态设置 ,ctrlCode 用 AnyChatAgentServiceCtrlCode 枚举类内部定义值 : BRAC_AGENT_SERVICE_WAITTING-- 示闲 

BRAC_AGENT_SERVICE_FINISHSERVICE-- 结束服务 BRAC_AGENT_SERVICE_PAUSED-- 示忙 

BRAC_AGENT_SERVICE_FINISHSERVICE_TIMEOUT-- 转移下一个坐席 

#### 返回值: 

无 

#### 接口参数简介: 

|名称|类型|说明|是否必须|
|---|---|---|---|
|ctrlCode|enum|状态控制码|是|
|onServiceCtrlEve nt|AnyChatService CtrlEvent|状态设置回调|是|

AnyChatServiceCtrlEvent回调简介: 

|返回值|名称|参数(类型):说 明|接口说明|备注|
|---|---|---|---|---|
|void|onServiceCtr lDone|result(AnyCh atResult): 执 行结果 JsonData(ob ject): 返回数 据|服务状态改变 通知||

AnyChatAgentServiceCtrlCode枚举类简介: 

|名称|类型|值|说明|
|---|---|---|---|
|BRAC_AGENT_S||||
|ERVICE_WAITTI NG|number|0|示闲|

本文档使用 看云 构建 

- 105 - 

席座服务状态设置 

|BRAC_AGENT_S ERVICE_FINISHS ERVICE number|1|结束服务|
|---|---|---|
|BRAC_AGENT_S ERVICE_PAUSED number|2|示忙|
|BRAC_AGENT_S|||
|ERVICE_FINISHS ERVICE_TIMEOU T number|3|转移下一个坐席|

本文档使用 看云 构建 

- 106 - 

离开营业厅 

# 离开营业厅 

### 离开营业厅 

leaveArea(onLeaveAreaEvent: AnyChatLeaveAreaEvent) 

#### 接口说明: 

离开当前所在营业厅 

#### 返回值: 

无 

#### 接口参数简介: 

|名称|类型|说明|是否必须|
|---|---|---|---|
|onLeaveAreaEve|AnyChatLeaveAr|离开营业厅操作状 |是|
|nt|eaEvent|态回调||

AnyChatLeaveAreaEvent回调简介: 

|返回值|名称|参数(类型):说 明|接口说明|备注|
|---|---|---|---|---|
|void|onLeaveAre aDone|result(AnyCh atResult): 执 行结果 JsonData(ob ject): 返回数 据|离开营业厅的 通知回调|result.code: 0表示成功,其 他表示错误代 号result.msg: 错误描述|

本文档使用 看云 构建 

- 107 - 

排队操作 

# 排队操作 

##### 进入队列 

##### 取消排队 

本文档使用 看云 构建 

- 108 - 

进入队列 

# 进入队列 

### 进入队列 

enterQueue(queueId: string, onEnterQueueEvent: AnyChatEnterQueueEvent) 

接口说明: 

进入队列 

返回值: 

无 

#### 接口参数简介: 

|名称|类型|说明|是否必须|
|---|---|---|---|
|queueId|string|队伍ID|是|
|onEnterQueueEv ent|AnyChatEnterQu eueEvent|进入排队的操作状 态回调|是|

AnyChatEnterQueueEvent回调简介: 

|返回值|名称|参数(类型):说 明|接口说明|备注|
|---|---|---|---|---|
|void|onEnqueue Done|result(AnyCh atResult): 执 行结果 JsonData(JS ONObject): 返回数据|进入队列结果 通知|result.code: 0表示成功,其 他表示错误代 号 result.msg: 错误描述 JsonData.us erNumInQu eue: 排队的 人数 JsonData.cur rentPos: 当前 排在第几位 JsonData.en queueTime: 进入队列时 间}|

本文档使用 看云 构建 

- 109 - 

进入队列 

|void|onProcessCh anged|JsonData(ob ject):返回数 据|排队进度通知|JsonData.us erNumInQu eue: 排队的 人数 JsonData.cur rentPos: 当前 排在第几位 JsonData.wai tingTime: 自 己在队列中的 等待时间(单 位:秒)|
|---|---|---|---|---|

本文档使用 看云 构建 

- 110 - 

取消排队 

# 取消排队 

### 取消排队 

cancelQueuing(onCancelQueuingEvent: AnyChatCancelQueuingEvent) 

接口说明: 

取消排队 

返回值: 

无 

#### 接口参数简介: 

|名称|类型||说明||是|否必须|
|---|---|---|---|---|---|---|
|onCancelQ gEvent|ueuin AnyChatC QueuingE|ancel vent|取消排 态回调|队的操作状|是||
|AnyChatCancel 返回值|QueuingEvent回调简 名称|介: 参数( 明|类型):说|接口说明||备注|
|void|onCancelQu euingDone|result atRes 行结果 JsonD ject): 据|(AnyCh ult): 执 ata(ob 返回数|取消排队状 回调|态|result.errCod e:0表示成功, 其他为错误代 号.result.err Msg:错误描 述|

本文档使用 看云 构建 

- 111 - 

状态查询 

# 状态查询 

##### 查询坐席状态 

查询队伍排队人数 查询当前排队时间 查询用户所在队列的当前位置 查询服务区域内排队的用户数 查询营业厅内的坐席数 

本文档使用 看云 构建 

- 112 - 

查询坐席状态 

# 查询坐席状态 

### 查询席座状态 

getAgentStatus(): object 

#### 接口说明: 

用户查询当前服务坐席的服务状态 

#### 返回值: 

当前坐席的服务状态 

#### 接口参数简介: 

无 

本文档使用 看云 构建 

- 113 - 

查询队伍排队人数 

# 查询队伍排队人数 

### 查询队列排队人数 

getQueueLength(queueId: string): number 

#### 接口说明: 

查询指定队列的排队人数 

#### 返回值: 

队伍中的排队人数 

#### 接口参数简介: 

|名称|类型|说明|是否必须|
|---|---|---|---|
|queueId|string|队列ID|是|

本文档使用 看云 构建 

- 114 - 

查询当前排队时间 

# 查询当前排队时间 

### 查询当前排队时间 

getQueueTime(queueId: string): number 

#### 接口说明: 

查询客户当前已排队时间 

#### 返回值: 

以秒为单位的排队时间 

#### 接口参数简介: 

|名称|类型|说明|是否必须|
|---|---|---|---|
|queueId|string|队列ID|是|

本文档使用 看云 构建 

- 115 - 

查询用户所在队列的当前位置 

# 查询用户所在队列的当前位置 

### 查询用户所在队列的当前位置 

getQueuePos(queueId: string): number 

##### 接口说明 

获取用户所在队列的当前位置 

##### 返回值 

用户所在队列的当前位置 

##### 接口参数简介 

|名称|类型|说明|是否必须|
|---|---|---|---|
|queueId|number|队列id|是|

本文档使用 看云 构建 

- 116 - 

查询服务区域内排队的用户数 

# 查询服务区域内排队的用户数 

### 查询服务区域内排队的用户数 

getAreaQueueUserCount(areaId: string): number 

##### 接口说明 

获取服务区域内排队的用户数 

##### 返回值 

服务区域内排队的用户数 

##### 接口参数简介 

|名称|类型|说明|是否必须|
|---|---|---|---|
|areaId|string|营业厅id|是|

本文档使用 看云 构建 

- 117 - 

查询营业厅内的坐席数 

# 查询营业厅内的坐席数 

### 查询营业厅内的坐席数 

getAgentCountArea(areaId: number): string 

##### 接口说明 

用户查询当前营业厅内的坐席总数以及空闲坐席数 

##### 返回值 

包含当前营业厅内的坐席总数以及空闲坐席数的对象 

##### 接口参数简介 

|名称|类型|说明|是否必须|
|---|---|---|---|
|areaId|number|营业厅ID|是|

##### 示例代码 

JSONObject jsonObject = AnyChatSDK.getInstance().getAgentCount(agentId); // 坐席总数 

let agentCount = jsonObject["agentCount"]; // 空闲坐席数 

let idleAgentCount = jsonObject["idleAgentCount"]; 

本文档使用 看云 构建 

- 118 - 

注册队列状态变化事件的监听 

# 注册队列状态变化事件的监听 

### 注册智能排队事件的监听 

registerQueueChangeEvent(queueChangeEvent: AnyChatQueueChangeEvent) 

接口说明: 

注册智能排队事件的监听 

#### 返回值: 

无 

#### 接口参数简介: 

|名称|类型|说明|是|否必须|
|---|---|---|---|---|
|queueChange ent|Ev AnyChatQ hangeEve|ueueC nt 智能排 调|队事件的回 是||
|AnyChatQueueCh |angeEvent回调简介 |: 参数(类型):说|||
|返回值|名称|明|接口说明|备注|
|void|onAreaChan ged|JsonData(ob ject): 返回数 据|营业厅状态变 化|JsonData.ag entcount 服 务区域客服用 户数 JsonData.idl eagentcount 服务区域空闲 坐席数量|
|void 本文档使用看云构建|onAgentStat usChanged|JsonData(ob ject):状态变 化数据|座席状态变化 通知|JsonData.sta te 0--关闭,不 对外提供服务 1--等待中, 可随时接受用 户服务 2--工作中, 正在为用户服 务 - 119 -|

|注册队列状态变化|事件的监听|||3--暂停服务 10--离线|
|---|---|---|---|---|
|void|onAgentSer viceInfoNoti fy|JsonData(ob ject): 状态变 化数据|座席服务信息 变化通知,服 务信息包括: 当前服务的开 始时间、服务 累计时间、累 计服务的用户 数|JsonData.ser viceBeginTi me:当前服务 的开始时间 JsonData.ser viceTotalTim e:服务累计时 间 JsonData.ser viceUserCou nt:累计服务 的用户数|
|void|onServiceNo tify|JsonData(ob ject): 状态变 化数据|用户出队列开 始服务通知事 件,收到此通 知后,由业务 系统决定由其 中一方发起视 频呼叫|JsonData. queueId: 队 列id JsonData. agentId: 座 席id JsonData. customerId: 客户id|

本文档使用 看云 构建 

- 120 - 

注销队列状态变化事件的监听 

# 注销队列状态变化事件的监听 

### 注销智能排队事件的监听 

unregisterQueueChangeEvent(queueChangeEvent: AnyChatQueueChangeEvent) 

#### 接口说明: 

注销智能排队事件的监听 

#### 返回值: 

无 

#### 接口参数简介: 

|名称|类型|说明|是否必须|
|---|---|---|---|
|queueChangeEv ent|AnyChatQueueC hangeEvent|智能排队事件的回 调|是|

本文档使用 看云 构建 

- 121 - 

双录 

# 双录 

##### 模块简述: 

什么是AnyChat双录: 

AnyChat双录以“音视频+交易”为核心,对金融交易过程进行风险揭示,实现录音录像留底,记录业务办理的 全过程,满足监管要求,同时规范销售行为,保障交易双方的利益。 

AnyChat双录特点: 

AnyChat双录支持多种风险揭示方式,包括语音、视频、图片、PPT等,并支持将多路语音、画面合成同一录像 文件,同时在录像画面叠加水印;基于AnyChat双录基础能力可以满足临柜双录、自助双录、远程双录等多种场 景的业务需求。 

本章节主要描述了双录的基本流程,并重点描述了双录相关接口的定义,双录基本流程中用到的通用接口将不再 重复描述,可参见上面其他相关章节。同时我们也提供了相关的双录demo,可在工程准备章节中进行下载体 验。 

本文档使用 看云 构建 

- 122 - 

基本流程 

# 基本流程 

##### 自助双录 

远程双录 

本文档使用 看云 构建 

- 123 - 

自助双录 

# 自助双录 

本文档使用 看云 构建 

- 124 - 

远程双录 

# 远程双录 

本文档使用 看云 构建 

- 125 - 

双录接口说明 

# 双录接口说明 

##### PPT资源下载 

资源播放 

时间戳 

水印 

本文档使用 看云 构建 

- 126 - 

PPT资源下载 

# PPT资源下载 

##### 双录风险播报资源概述: 

目前支持的资源类型包括了MP3,MP4,PPT压缩包,其中PPT压缩包用于实现PPT画面关联语音播报,需要参考 PPT资源下载章节下载资源。 

点击下载PPT压缩包生成工具 

本文档使用 看云 构建 

- 127 - 

PPT资源下载 

# 下载任务初始化 

PPT下载封装在AnyChatDownload类中。 

获取单例对象: 

public static getInstance(): AnyChatDownload 

下载任务初始化: 

public initAnyChatDownload(savepath: string) 

|参数|说明|
|---|---|
|savepath|下载完保存的本地路径|

本文档使用 看云 构建 

- 128 - 

PPT资源下载 

# 开始下载 

##### 开始下载: 

public start(params: HashMap<string,string> ,iAnyChatDownload: AnyChatDownloadE vent ): string 

##### params 该传入值为以下列表: 

|参数||说明|
|---|---|---|
|fileurl||文件网络链接地址|
|fileid||资源ID ,资源文件的唯一标识,用于 定位文件,类型为数字型字符串,由调 用该接口的业务层代码设定。|
|filemd5||资源文件的MD5值,用于文件下载的 完整性校验以及防止重复下载|
|filetype||资源类型|
|//文件类型定义常量:filetype|||
|BRPPT_FILETYPE_PPT =|0x01|// ppt压缩包文件|
|BRPPT_FILETYPE_VIDEO|= 0x02|//视频文件|
|BRPPT_FILETYPE_AUDIO|= 0x03|//音频文件|

##### 注意:下载之前请确保SDK客户端已经连接登录成功。 

##### 下载回调接口: 

##### AnyChatDownloadEvent接口回调说明 

##### a、下载进度接口回调 

onProgress(progress: number); 

##### 备注:progress下载进度总进度为100 

b、下载结果接口回调 

onFinish(pptDetail: string); 

备注:pptDetail下载完成后返回的信息 

{ 

本文档使用 看云 构建 

- 129 - 

PPT资源下载 

"details":{ 

"audio_address":"audio\1.mp3",  // ppt 音频文件相对压缩包根目录路径 "pptlist":[ { "audio_end":5,              // 第一页 ppt 播放结束时间( s ) "audio_start":0,             // 第一页 ppt 播放开始时间( s ) "ppt_address":"ppt\1.jpg"    // 第一页 ppt 相对压缩包根目录路径 }, { "audio_end":24, "audio_start":5, "ppt_address":"ppt\2.jpg" }, ...... ] }, "errorcode":0, "fileid":"20170516",             // 文件 id "filepath":"d:\video\temp\ppt\20170516\"  // 压缩包解压后的所在目录路径 } 

本文档使用 看云 构建 

- 130 - 

PPT资源下载 

# 取消下载 

##### 取消下载: 

public cancel(fileid: string): string 

|参数|说明|
|---|---|
|fileid|初始化时设置的资源文件ID|

本文档使用 看云 构建 

- 131 - 

PPT资源下载 

# 查询资源下载状态 

##### 查询资源下载状态: 

public getStatus(fileid: string): string 

|参数|说明|
|---|---|
|fileid|初始化时设置的资源文件ID|

本文档使用 看云 构建 

- 132 - 

PPT资源下载 

# 查询资源详细信息 

##### 查询资源详细信息: 

public getInfo(fileid: string): string 

|参数|说明|
|---|---|
|fileid|初始化时设置的资源文件ID|

本文档使用 看云 构建 

- 133 - 

资源播放 

# 资源播放 

##### 媒体资源播放 

本文档使用 看云 构建 

- 134 - 

资源播放 

# 媒体资源播放 

##### 媒体资源播放相关api封装在AnyChatMediaPlayer类中。 初始化媒体资源播放器: 

##### // 提供构造方法,可根据需求选择初始化资源播放器 // 初始化视频播放器 

public constructor(mediaPlayerOpt: MediaPlayerOpt,e: AnyChatMediaPlayerEvent) 

|参数|类型|说明|是否必须|
|---|---|---|---|
|mediaPlayerOpt|MediaPlayerOpt|媒体播放配置类|是|
|e|AnyChatMediaPl ayerEvent|媒体播放事件通知|是|

##### MediaPlayerOpt 媒体播放配置类简介: 

|名称|类型|说明|是否必须|
|---|---|---|---|
|encryptionKey|string|播放一个加密的录 像视频文件(参考 录制章节),实时 自动解密并播放。 设置播放文件的解 密方式:为空不解 密,传密钥普通解 密|否|
|patn|string|文件路径|是|
|mediaType|number|播放控件|否|
|isOpenMixAudio|boolean|是否开启混音录制|否|

本文档使用 看云 构建 

- 135 - 

资源播放 

# 播放 

##### 播放: 

public start(): number 

备注:返回播放信息,0为成功。 

本文档使用 看云 构建 

- 136 - 

资源播放 

# 暂停 

##### 暂停: 

public pause(): number 

备注:返回播放信息,0为成功。 

本文档使用 看云 构建 

- 137 - 

资源播放 

# 停止 

停止: 

public stop(): number 

备注:返回播放信息,0为成功。 

本文档使用 看云 构建 

- 138 - 

资源播放 

# 销毁 

##### 销毁: 

public destroy(): number 

本文档使用 看云 构建 

- 139 - 

资源播放 

# 获取当前播放信息 

##### 获取当前播放信息: 

public getPlayStatus(): string 

##### 备注:返回播放信息 

{ "audiobitrate":256, "audiocodec":23, "audioduration":45540, "bitspersample":16, "channels":1, "errorcode":0, "filebitrate":256, "fileduration":45540,// 媒体总时间 "filename":"2.mp3", "playspeed":1, "playstatus":0, "playtime":0, // 播放到进度时间 "samplespersec":16000, "taskguid":"E444CCD1-4D27-48FE-A9D5-BD0074A0B557" } 

本文档使用 看云 构建 

- 140 - 

资源播放 

# 播放状态回调接口 

##### 播放回调接口: 

a.播放状态回调接口 

onPlayStatus(playStatus: number); 

备注playStatus播放状态:1-->开始播放;2-->暂停播放; 

3-->停止播放;4-->播放完成。 

本文档使用 看云 构建 

- 141 - 

时间戳 

# 时间戳 

##### 录像之前视频录制配置: 

AnyChat sdk支持视频画面叠加时间戳水印功能,调用该接口后,在视频通话本地画面和远程画面以及录像文件 里面会显示当前时间戳。 

AnyChatCoreSDK.SetSDKOptionInt(AnyChatDefine.BRAC_SO_LOCALVIDEO_OVERLAYTIMESTAM P,1); 

##### 备注: 

该时间戳与录像章节文字水印中的时间戳是有区别的: 

- 1.调用该接口后,时间戳会被添加在本地视频中,对方请求本地视频时,对方亦能看到该时间戳,并且该时间戳 能被录制进视频文件中; 

- 2.录像章节文字水印中的时间戳是指在录像中添加时间戳文字水印,在视频中是不会显示的。 

本文档使用 看云 构建 

- 142 - 

水印 

# 水印 

##### 水印: 

AnyChat sdk支持在录像文件画面中叠加文字水印或者图片水印,如企业名称或企业logo,用于录像文件防伪, 有关录像添加水印的详细内容,请参考录制章节。 

本文档使用 看云 构建 

- 143 - 

用户相关的查询接口 

# 用户相关的查询接口 

### 用户相关的查询接口 

##### 模块简述 

该模块主要用于获取用户当前的相关状态或者多媒体流相关信息。 

##### 简要流程 

无 

本文档使用 看云 构建 

- 144 - 

查询用户名 

# 查询用户名 

### 查询用户名 

getUserName(number userId) : string 

##### 接口说明 

获取指定用户的用户名。 

##### 返回值 

指定用户的用户名。 

##### 接口参数简介 

|名称|类型|说明|是否必须|
|---|---|---|---|
|userId|number|用户ID|是|

本文档使用 看云 构建 

- 145 - 

错误码 

# 错误码 

#### 操作错误码 

|错误码|错误描述|
|---|---|
|0|成功|
|系统错误码||
|错误码|错误描述|
|1|数据库错误|
|2|系统没有初始化|
|3|还未进入房间|
|4|内存不足|
|5|出现异常|
|6|操作被取消|
|7|通信协议出错|
|8|会话不存在|
|9|数据不存在|
|10|数据已经存在|
|11|无效GUID|
|12|资源被回收|
|13|资源被占用|
|14|Json解析出错|
|15|对象被删除|
|16|会话已存在|
|17|会话没有初始化|
|18|数据没有准备好|
|19|收到SIGTERM信号(kill指令)|
|20|函数功能不允许|
|21|函数参数错误|
|22|设备打开错误或设备未被安装|
|23|没有足够的资源|
|24|指定的格式不能被显示设备所支持|
|25|指定的IP地址不是有效的组播地址|
|26 ~~本文档使用看云 构建~~|不支持多实例运行 ~~- 146 -~~|

~~本文档使用 看云 构建~~ 

~~- 146 -~~ 

错误码 

|27|文件签名验证失败|
|---|---|
|28|授权验证失败|
|29|授权证书用户数验证失败|
|30|所指定的主服务器是热备服务器,不支 持再次热备|
|31|主服务器没有经过授权认证,不支持热 备|
|32|版本不匹配|
|33|第二次授权验证失败|
|34|服务器安全验证失败|
|35|客户端授权验证失败|
|36|授权功能校验失败|
|37|远程控制|
|38|ServiceGuid重复|
|39|目录错误|
|40|解压文件失败|
|41|启动进程失败|
|42|服务已启动|
|43|磁盘空间不足|
|44|业务服务发送请求失败|
|45|无效的物理机对象|
|46|获取授权信息失败|
|47|集群属性不匹配|
|48|集群ID为空|
|49|同台物理机创建多个相同服务,一类服 务暂时不允许创建多个|
|50|拷贝文件失败|
|51|云平台内部数据库出错|
|52|云平台OSS文件上传失败|
|53|服务绑定关系变化|
|54|服务没有被绑定|
|55|服务绑定失败|
|56|PipeLine通信用户ID出错|
|57 ~~本文档使用看云 构建~~|PipeLine通信会话出错 ~~- 147 -~~|

~~本文档使用 看云 构建~~ 

~~- 147 -~~ 

~~错误码~~ 

|58 |服务被关闭|
|---|---|
|59|文件已被加密过|
|60|解密无效(文件校验不通过)|
|61|解密失败,可能密码错误|
|62|缓冲区太长|
|63|服务器版本太旧|
|64|不支持的文件类型|
|65|文件内容出错|
|66|密钥校验失败|
|67|缺少证书链|
|68|证书校验失败|
|69|证书日期校验失败|
|70|证书URL地址校验失败|
|71|缺少公钥|
|72|服务器没有配置SSL证书所对应的私钥|
|73|服务器没有配置SSL证书|
|74|安全级别限制,不允许连接|
|75|安全协商失败|
|76|算法协商失败|
|77|缺少CertHelper库文件|
|78|安全协商超时|
|79|准备的缓冲区太小|
|连接错误码||
|错误码|错误描述|
|100|连接服务器超时|
|101|与服务器的连接中断|
|102|连接服务器认证失败(服务器设置了认 证密码)|
|103|域名解析失败|
|104|超过授权用户数|
|105|服务器功能受限制(演示模式)|
|106|只能在内网使用|
|107 ~~本文档使用看云 构建~~|版本太旧,不允许连接 ~~- 148 -~~|

~~本文档使用 看云 构建~~ 

~~- 148 -~~ 

~~错误码~~ 

|108 |Socket出错|
|---|---|
|109|设备连接限制(没有授权)|
|110|服务已被暂停|
|111|热备服务器不支持连接(主服务在启动 状态)|
|112|授权用户数校验出错,可能内存被修改|
|113|IP被禁止连接|
|114|连接类型错误,服务器不支持当前类型 的连接|
|115|服务器IP地址不正确|
|116|连接被主动关闭|
|117|没有获取到服务器列表|
|118|连接负载均衡服务器超时|
|119|服务器不在工作状态|
|120|服务器不在线|
|121|网络带宽受限|
|122|网络流量不足|
|123|不支持IPv6Only网络|
|124|没有Master服务器在线|
|125|没有上报工作状态|
|126|数据还没准备好|

#### 登录错误码 

|错误码|错误描述|
|---|---|
|200|认证失败,用户名或密码有误|
|201|该用户已登录|
|202|帐户已被暂时锁定|
|203|IP地址已被暂时锁定|
|204|游客登录被禁止(登录时没有输入密 码)|
|205|无效的用户ID(用户不存在)|
|206|与业务服务器连接失败,认证功能失效|
|207|业务服务器执行任务超时|
|208|没有登录|
|209|该用户在其它计算机上登录|

~~本文档使用 看云 构建~~ 

~~- 149 -~~ 

错误码 

|210|用户名为空|
|---|---|
|211|被服务器踢掉|
|212|业务服务器重启|
|213|操作被禁止,没有权限|
|214|签名信息为空,禁止登录|
|215|签名验证失败|
|216|签名验证公钥为空|
|217|签名私钥为空|
|218|签名参数为空|
|219|签名参数出错|
|220|签名时间失效|
|221|应用没有被激活|
|222|应用被用户暂停|
|223|应用被用户锁定|
|224|应用已过期|
|225|应用未知状态|
|226|签名已经被使用|
|227|获取用户角色失败|
|228|坐席无效(不存在)|
|229|客户端校验服务器签名失败|

#### 进入房间错误码 

|错误码|错误描述|
|---|---|
|300|房间已被锁住,禁止进入|
|301|房间密码错误,禁止进入|
|302|房间已满员,不能进入|
|303|房间不存在|
|304|房间服务时间已到期|
|305|房主拒绝进入|
|306|房主不在,不能进入房间|
|307|不能进入房间|
|308|已经在房间里面了,本次进入房间请求 忽略|
|309|不在房间中,对房间相关的API操作失 败|

~~本文档使用 看云 构建~~ 

~~- 150 -~~ 

错误码 

|310|超过房间数限制|
|---|---|
|311|没有可用端口|

#### 数据流错误码 

|错误码|错误描述|
|---|---|
|350|过期数据包|
|351|相同的数据包|
|352|数据包丢失|
|353|数据包出错,帧序号存在误差|
|354|媒体流缓冲时间不足|
|355|无效的流序号|

#### 私聊错误码 

|错误码|错误描述|
|---|---|
|401|用户已经离开房间|
|402|用户拒绝了私聊邀请|
|403|不允许与该用户私聊,或是用户禁止私 聊|
|420|私聊请求ID号错误,或请求不存在|
|421|已经在私聊列表中|
|431|私聊请求超时|
|432|对方正在私聊中,繁忙状态|
|433|对方用户关闭私聊|
|434|用户自己关闭私聊|
|435|私聊请求被取消|

#### 视频呼叫错误码 

|错误码|错误描述|
|---|---|
|440|正在通话中|
|500|说话时间太长,请休息一下|
|501|有高级别用户需要发言,请休息一下|
|100101|源用户主动放弃会话|
|100102|目标用户不在线|
|100103|目标用户忙|
|100104|目标用户拒绝会话|

~~本文档使用 看云 构建~~ 

~~- 151 -~~ 

###### 错误码 

|100105|会话请求超时|
|---|---|
|100106|网络断线|
|100107|用户不在呼叫状态|
|集群总线错误码 错误码|错误描述|
|610|本地总线为Master状态|
|611|有其它总线存在|
|612|优先级不够|
|613|总线Master申请中|

#### 传输错误码 

|错误码|错误描述|
|---|---|
|700|创建任务失败|
|701|没有该任务,或是任务已完成|
|710|打开文件出错|
|711|文件长度为0|
|712|文件长度太大|
|713|读文件出错|
|714|文件正在下载中|
|715|文件下载失败|
|716|没有该任务,或是任务已完成|

#### 录制错误码 

|错误码|错误描述|
|---|---|
|720|没有录像任务|
|721|创建录像任务失败|
|722|等待用户相关信息,暂时不能录像|
|723|视频参数出错|
|724|音频参数出错|
|725|创建录像文件失败|
|726 排队错误码|录像服务离线|
|错误码|错误描述|
|750|无效的队列ID|

本文档使用 看云 构建 

- 152 - 

~~错误码~~ 

|751 |准备接受服务,离开队列|
|---|---|
|752|排队超时,离开队列|
|sdk错误码 错误码|错误描述|
|780|与服务器的UDP通信异常,流媒体服务 将不能正常工作|
|781|SDK加载brMiscUtil.dll动态库失败,部 分功能将失效|
|782|SDK加载brMediaUtil.dll动态库失败, 部分功能将失效|
|783|SDK加载brMediaCore.dll动态库失 败,部分功能将失效|
|784|SDK加载brMediaShow.dll动态库失 败,部分功能将失效|
|785|操作摄像头失败|
|786|操作Mic失败|
|授权错误码||
|错误码|错误描述|
|800|获取授权信息失败|
|801|授权已过期|
|802|证书解码失败|
|810|解析硬件特征码失败(可能是证书存在 问题)|
|811|CPU特征码不匹配(CPU数量)|
|812|CPU特征码不匹配(CPU主频)|
|813|内存特征码不匹配(内存容量)|
|814|网卡特征码不匹配(MAC地址)|
|815|CPU特征码不匹配(CPU型号)|
|816|硬盘特征码不匹配(磁盘ID)|
|821|不在升级周期内|
|830|UKey信息不正常|
|831|没有查询到UKey设备|
|832|获取UKey信息特征码失败|
|833 ~~本文档使用看云 构建~~|绑定的UKey和当前插入的UKey不匹配 ~~- 153 -~~|

~~本文档使用 看云 构建~~ 

~~- 153 -~~ 

错误码 

|834|加载UKey动态库失败|
|---|---|
|840|域名解析验证失败|
|842|域名解析失败|
|850|绑定的IP地址和服务器本地IP地址不匹 配|
|860|域名信息错误|
|861|UKey信息错误|
|862|IP地址错误|

#### 视频设备错误码 

|错误码|错误描述|
|---|---|
|10001|打开视频设备失败|
|10002|未知视频输出格式|
|10003|驱动不支持 VIDIOC_G_FMT|
|10004|驱动不支持 VIDIOC_S_FMT|
|10005|驱动不支持 VIDIOC_G_PARM|
|10006|驱动不支持 VIDIOC_S_PARM|
|10007|驱动不支持 VIDIOC_QUERYCAP|
|10008|当前设备非视频采集设备|
|10009|采集发生错误|
|10010|设备不支持 mmap 和usermap 模式|
|10011|获取块物理地址失败|
|10012|物理地址映射到虚拟地址失败|
|10013|视频预缓存失败|
|10014|获取视频失败|
|10015|QBUF失败|
|10016|VIDIOC_STREAMON失败|
|10017|VIDIOC_STREAMOFF失败|
|10018|当前摄像头可能被其他进程使用|
|10019|不支持视频采集模式|
|10020|请求的缓冲类型不支持, 或者 VIDIOC_TRY_FMT 被使用和不支持这 种缓冲类型.|

#### 音频设备错误码 

~~本文档使用 看云 构建~~ 

~~- 154 -~~ 

###### 错误码 

|错误码 |错误描述|
|---|---|
|10500|打开音频设备失败|
|10501|请求 hwparams失败|
|10502|设置 interleaved模式失败|
|10503|设置wBitsPerSample失败|
|10504|设置SamplesPerSec失败|
|10505|设置channels失败|
|10506|设置periods失败|
|10507|设置缓存尺寸失败|
|10508|函数:snd_pcm_hw_params调用失败|
|10509|设置rebuffer time失败|
|10510|设置 rebuffer frames失败|
|10511|获取period time失败|
|10512|获取 period frame失败|
|10513|请求swparams失败|
|10514|设置 start threshoid失败|
|10515|设置 start avail min失败|
|10516|函数snd_pcm_prepare调用失败|
|10517|函数read调用失败|
|10518|音频capmode出错|
|20000|无效的流|
|30000|创建会话失败|
|业务对象错误码||
|错误码|错误描述|
|100201|已经进入一个服务区域|
|100202|已经进入一个服务队列|

APP ID错误码 

|错误码|错误描述|
|---|---|
|100300|默认的应用ID(空)不被支持|
|100301|应用登录需要签名|
|100302|应用签名校验失败|
|100303|应用ID不存在|
|100304|应用ID被系统锁定|

~~本文档使用 看云 构建~~ 

~~- 155 -~~ 

错误码 

|100305|应用ID与当前服务不匹配|
|---|---|
|100306|连接的服务器不是云平台地址|
|100307|应用所对应的计费服务器不足|
|100308|应用计费模式改变|
|100309|应用运营商改变|
|100310|应用空闲|

#### 创建用户错误码 

|错误码|错误描述|
|---|---|
|100400|用户密码长度过短|
|100401|用户名重名|
|100402|权限受限|
|100403|不允许创建该用户名|

#### 升级服务过程错误码 

|错误码|错误描述|
|---|---|
|100500|升级服务开始|
|100501|升级服务,正在停止当前服务...|
|100502|升级服务,正在备份当前服务...|
|100503|升级服务,正在删除当前服务...|
|100504|升级服务,正在拷贝新服务...|
|100505|升级服务,正在启动新服务...|
|100506|升级服务,正在恢复老版本...|
|100507|升级服务,已经是目标版本|
|100508|升级服务,当前服务需要停止,才能执 行升级操作|
|100509|升级服务,备份失败|
|100510|升级服务,删除失败|
|100511|升级服务,拷贝失败|
|100512|升级服务,恢复老版本失败|
|100513|升级服务,通讯桥未注册|
|100514|升级服务,写入配置文件失败|
|100515|升级服务,获取备份文件夹失败|
|100516|升级服务结束|
|100517 ~~本文档使用看云 构建~~|无法获取维护信息 ~~- 156 -~~|

~~本文档使用 看云 构建~~ 

~~- 156 -~~ 

错误码 

不能重命名文件夹 

100518 

#### 停止进程错误码 

|错误码|错误描述|
|---|---|
|100600|停止进程,超时|
|100601|停止进程,失败(被回复失败)|
|100602|停止进程,强行杀死失败|
|启动进程错误码 错误码|错误描述|
|100603|启动进程,规定时间内没有收到通讯桥通 知|
|100604|service 正在被控制中(e.g 正在执行升 级任务的时候,还收到了其他控制命 令)|
|100605|在启动或解压之前,发现除目标之外还 存在其他版本|
|100606|不支持此操作(e.g 对PMServer下达 挂起命令等)|
|100607|不存在该版本的升级包|
|100608|升级包中不存在该服务|
|100609|扩展的配置参数非法(e.g LUServer 的 serviceBaseInfo 的扩展参数解析错 误)|
|100610|移动临时文件到升级目录时失败|
|100611|不兼容当前OS平台|
|100612|获取rootserverconnect失败|

#### 业务服务器错误码 

|错误码|错误描述|
|---|---|
|100701|无效参数|
|100702|应用ID不存在|
|100703|Body无效|
|100704|签名验证失败|
|100705|签名时间戳无效|
|100706|可用内存不够|
|100707|出现异常|

~~本文档使用 看云 构建~~ 

~~- 157 -~~ 

错误码 

|100708|通信协议出错|
|---|---|
|100709|业务服务器执行任务超时|
|100710|文件不存在|

#### 数据库服务器错误码 

|错误码|错误描述|
|---|---|
|100801|数据库执行错误|
|100802|数据库查询不到数据|
|100803|数据库读取行数据错误|
|100804|出现异常|
|100805|连接异常|

#### PPT播放相关错误码 

|错误码|错误描述|
|---|---|
|100901|无效URL地址|
|100902|页面不存在|
|100903|主机或代理失败|

#### 文件存储操作 

|错误码|错误描述|
|---|---|
|101101|无效输入参数|
|101102|无效输出参数|
|101103|日志初始化失败|
|101104|文件不存在|
|101105|文件打开失败|
|101106|文件读取失败|
|101107|文件写入失败|
|101108|内存分配失败|
|101109|文件id加密失败|
|101110|文件id解密失败|
|101111|初始化客户端失败|
|101112|连接tracker失败|
|101113|连接storage失败|
|101114|文件操作失败|
|101115|创建实例失败|

~~本文档使用 看云 构建~~ 

~~- 158 -~~ 

错误码 

|101116|参数未设置|
|---|---|
|101117|校验失败|

#### AI机器人错误代码 

|错误码|错误描述|
|---|---|
|200000|用户不存在|
|200001|用户已经存在|
|200002|AI对象不存在|
|200003|AI参数错误|
|200004|AI能力不支持|
|200005|未知AI能力|
|200006|HTTP请求失败|
|200007|AI请求初始化失败|
|200008|AI请求失败|
|200009|AI请求超时|
|200010|内部数据无效|
|200011|内部数据不存在|
|200012|内部对象无效|
|200013|心跳超时|
|200014|机器人离线|
|200015|内容超长|
|200016|信令超长|
|200017|AI请求超过并发|
|200018|媒体参数无效|
|200019|请求ID已存在|
|200020|AI异常错误|
|200021|AI参数设置对象不存在|
|200022|不支持的AI处理|
|200023|无效地址|

#### AnyChat业务数据传输控制错误代码 

|错误码|错误描述|
|---|---|
|1000010|业务请求超时|
|1000011|业务请求参数错误|

本文档使用 看云 构建 

- 159 -
