# VideoComm Media SDK For Harmony 开发流程指南 (版本:V3.3) 

VideoComm Media SDK For Harmony 开发流程指南 

|目录 一、产品介绍........................................................................... 4|
|---|
|1.1. 面向的读者.................................................................. 4|
|二、工程准备........................................................................... 5|
|2.1 导入库文件................................................................... 5|
|2.2添加权限.......................................................................7|
|三、基本流程........................................................................... 9|
|3.1 获取SDK实例...............................................................9|
|3.2设置事件通知接口......................................................... 9|
|3.3移除事件通知接口......................................................... 9|
|3.4 初始化SDK ...................................................................9|
|3.5 设置用户参数并登陆SDK .............................................10|
|四、智能排队......................................................................... 11|
|4.1获取队列信息.............................................................. 11|
|4.2加入队列.....................................................................13|
|4.3离开队列.....................................................................13|
|4.4获取队列人数、等待时间..............................................14|
|4.5等待系统分配坐席(路由分配坐席事件)...................... 15|
|4.6开始通话.....................................................................16|

第 2 页共 22 页 

VideoComm Media SDK For Harmony 开发流程指南 

|4.7 用户主动挂断通话....................................................... 17|
|---|
|4.8 坐席主动挂断通话....................................................... 18|
|五、音视频通信......................................................................19|
|5.1加入会议.....................................................................19|
|5.2准备XComponent控件.................................................19|
|5.3开始音视频通信...........................................................20|
|5.4离开会议.....................................................................21|
|六、资源释放......................................................................... 22|
|6.1 退出(注销)..............................................................22|
|6.2 释放资源.....................................................................22|

第 3 页共 22 页 

VideoComm Media SDK For Harmony 开发流程指南 

## 一、产品介绍 

VideoComm Media SDK 是我们核心团队成员基于多年的音视频通信领域 的技术积累,为客户提供跨终端、多平台互通、低成本、高品质、可定制的实 时音视频通信服务的开发平台,在平台中提供了音视频通信、音视频录制、文 件传输、数据通信、业务排队、屏幕共享等能力。我们的目标是让客户在无需 音视频技术基础的情况下,都可以通过本开发平台从零开始即刻搭建出自己的 专属音视频通信应用解决方案。 

VideoComm Media SDK for Harmony(以下简称:Harmony SDK)是基 于 Harmony 内核提供的客户端组件,对上层应用提供 ArkTS 语言的调用接口, 组件对应一系列的.so 库文件,定义和封装了一系列 API 接口和事件,采用 NAPI 技术实现 ArkTS 层与内核层进行数据通信。 

VideoComm Media SDK 由我们独立研发,具有自主知识产权。 

### **1.1.** 面向的读者 

《VideoComm Media SDK for Harmony 开发流程指南》文档是 提供给具有一定 Harmony 编程经验和了解面向对象概念的读者使用, 不要求具备音视频开发方面的经验。 

第 4 页共 22 页 

VideoComm Media SDK For Harmony 开发流程指南 

## 二、工程准备 

本套开发指南用的工具是Harmony Studio。首先,新建一个 新的Harmony 工程,对工程进行以下配置,搭建VideoComm Media SDK 的开发环境。 

### **2.1** 导入库文件 

本SDK 支持arm64-v8a 架构的Harmony 设备,并为其提供了相 应的库文件,在Demo 工程的libs 目录下,有子目录arm64-v8a (适用于arm64-v8a 架构),这样APP 便可以支持arm64-v8a 的设 备。 

#### 2.1.1 Harmony Studio 导入.har 库文件 

##### (1)创建 libs 目录 

在 APP 的 src 平级目录中创建一个 libs 目录,如下图所示: 

- (2)引入 har 库 

第 5 页共 22 页 

VideoComm Media SDK For Harmony 开发流程指南 

   - 将 har 库放入 libs 目录,同时打开 oh-package.json5 配置文 

- 件,将 har 库引入到 APP 工程中,如下图所示: 

##### (3)重新编译工程即可 

第 6 页共 22 页 

VideoComm Media SDK For Harmony 开发流程指南 

### **2. 2** 添加权限 

##### VideoComm Media SDK 在通讯过程中,我们需要获取系统的 

网络、照相机和音频等权限,参考代码如下: 

"requestPermissions": [
{
"name": "ohos.permission.INTERNET"
},
{
"name": "ohos.permission.USE_BLUETOOTH"
},
{
"name": "ohos.permission.DISCOVER_BLUETOOTH"
},
{
"name": "ohos.permission.GET_NETWORK_INFO"
},
{
"name": "ohos.permission.GET_WIFI_INFO"
},
{
"name": "ohos.permission.MODIFY_AUDIO_SETTINGS"
},
{
"name": "ohos.permission.KEEP_BACKGROUND_RUNNING"
}
],

注:摄像头、麦克风权限需要主动请求获取申请,如下图所示: 

第 7 页共 22 页 

VideoComm Media SDK For Harmony 开发流程指南 

第 8 页共 22 页 

VideoComm Media SDK For Harmony 开发流程指南 

## 三、基本流程 

在工程准备好之后,需要实现以下基本流程,才能调用音视频 交互以及其他功能。 

### **3.1** 获取 **SDK** 实例 

VComMediaSDK 类是 SDK 的核心类,提供各种功能接口,如 登录、进入会议、操作音视频等。在使用这些接口构建应用之前, 需要引入 VComMediaSDK 对象类,这个对象是一个静态对象,它内 部的接口方法全是静态方法,可通过类对象直接调用。 

### **3.2** 设置事件通知接口 

继承 VComSDKEvent 事件接口类,将继承者对象设置设置给 SDK,接收服务器返回提示。参考代码如下: 

VComMediaSDK.VCOM_SetSDKEvent(this);// 设置事件通知接口 

### **3.3** 移除事件通知接口 

参考代码如下: 

VComMediaSDK.VCOM_RemoveSDKEvent(this);// 设置事件通知接口 

### **3.4** 初始化 **SDK** 

在获得 SDK 的对象之后,要使用各种功能接口之前,我们还 得对 SDK 进行一个初始化。参考代码如下: 

第 9 页共 22 页 

VideoComm Media SDK For Harmony 开发流程指南 

VComMediaSDK.VCOM_Initialize(0, "", this.context); 

) 

注:this.context 为 uiAbility 上下文对象,不传入的话 sdk 会自动获 取,但是调用初始化接口请在 uiAbility 加载完成 page 后再调用。调 用示例如下所示: 

### **3.5** 设置用户参数并登陆 **SDK** 

登陆 SDK 分为两步,分别是设置用户参数和登陆服务器。参 考代码如下: 

VComMediaSDK.VCOM_SetUserConfig( " lpUserName " , " lpUserCode " , "" , "" , "" );//设置用户参数 VComMediaSDK.VCOM_Login( "139.9.171.70:8080" , 0, "" );//开始登录 

第 10 页共 22 页 

VideoComm Media SDK For Harmony 开发流程指南 

## 四、智能排队 

VideoComm Media SDK 为开发者提供了排队功能。通过以下几 步操作,即可在您的应用中使用排队功能。 

### **4.1** 获取队列信息 

调用以下接口,可以查询队列中的信息。参考代码如下: 

VComMediaSDK.VCOM_QueueControl(VCOM_QUEUECTRL_QUERYQUEUEINFO , "");//查询队列信息 

##### 调用后会在 OnQueueEvent 方法的回调里收到信息,如下: 

_//_ 排队回调 **public** OnQueueEvent(iEventType: number, iErrorCode: number, strUserData: string) { if (iEventType == VCOM_QUEUEEVENT_QUERYQUEUEINFO) { _//_ 查询队列回调 **if** (iErrorCode == 0) { _//_ 可以执行解析 _lpUserData_ 数据( _Json_ 格式) } } } 

第 11 页共 22 页 

VideoComm Media SDK For Harmony 开发流程指南 

|_// lpUser_|_Data_参考值_(JSON)_:|
|---|---|
|_{_||
|_"que_|_ue_list": [{_|
||_"queueid": "100",_|
||_"property": 0,_|
||_"name": "_开户队列_",_|
||_"describe": "_开户队列描述信息_"_|
|_},{_||
||_"queueid": "101",_|
||_"property": 1,_|
||_"name": "_理财队列_",_|
||_"describe": "_理财队列描述信息_"_|
|_}]_||
|_}_||

第 12 页共 22 页 

VideoComm Media SDK For Harmony 开发流程指南 

### **4.2** 加入队列 

根据获取的队列信息,选择一个队列,调用接口加入队列。参 考代码如下: 

String lpCtrlValue = {"queueid": "100"};//queueid 需要进入的队列 id VComMediaSDK.VCOM_QueueControl(VCOM_QUEUECTRL_ENTERQUEUE, lpCtrlValue); //加入队列 

//如果要指定坐席服务,需在 agent 参数中指定坐席的 userCode 

String lpCtrlValue = {"queueid": "100", “agent”: “AgentUserCode”}; VComMediaSDK.VCOM_QueueControl(VCOM_QUEUECTRL_ENTERQUEUE, lpCtrlValue); //加入队列 

##### 调用后会在 OnQueueEvent 方法的回调里收到信息,如下: 

###### //排队回调 

public OnQueueEvent(iEventType: number, iErrorCode: number, strUserData: string) { 

if (iEventType == VCOM_QUEUEEVENT_ENTERRESULT) { 

//加入队列回调 

if (iErrorCode == 0){ } } } 

### **4.3** 离开队列 

调用以下接口,可离开队列。参考代码如下: 

调用后会在 OnQueueEvent 方法的回调里收到信息,如下: 

第 13 页共 22 页 

VideoComm Media SDK For Harmony 开发流程指南 

VComMediaSDK.VCOM_QueueControl(VCOM_QUEUECTRL_LEAVEQUEUE,lpCtrl Value); //离开队列 //排队回调 public OnQueueEvent(iEventType: number, iErrorCode: number, strUserData: string) { if (iEventType == VCOM_QUEUEEVENT_ENTERRESULT) { //离开队列回调 if (iErrorCode == 0) { // 离开队列成功 } else { // 离开队列失败 } } } 

### **4.4** 获取队列人数、等待时间 

加入队列后,可以调用接口查询此队列的人数,和等待的时间。 参考代码如下: 

//获取队列人数、排队时长、排第几位 VComMediaSDK. VCOM_QueueControl(VCOM_QUEUECTRL_QUREYQUEUELENGTH, ""); 

调用后会在 OnQueueEvent 方法的回调里收到信息,如下: 

第 14 页共 22 页 

VideoComm Media SDK For Harmony 开发流程指南 

###### //排队回调 

public OnQueueEvent(iEventType: number, iErrorCode: number, strUserData: string) { if (iEventType == VCOM_QUEUEEVENT_QUREYQUEUELENGTH ) { //查询队列回调 if (iErrorCode == 0){ //可以执行解析 lpUserData 数据(Json 格式) } } } 

_// lpUserData_ 参考值 _(JSON)_ : _{ "index": 2, "length": 10, "time": 50 } JSON_ 字段说明: _index_ ,当前排队在第几位,比如上图排在第 _2_ 位 _length_ ,当前队列一共有几人排队,比如上图一共有 _10_ 人 _time_ ,当前排队等待时长,单位秒 

### **4.5** 等待系统分配坐席(路由分配坐席事件) 

进入相应队列后,即开始等待系统分配空闲坐席。当系统分配 到坐席后,会自动对坐席发起呼叫,且用户端会触发以下回调。参 考代码如下: 

第 15 页共 22 页 

VideoComm Media SDK For Harmony 开发流程指南 

###### //排队回调 

public OnQueueEvent(iEventType: number, iErrorCode: number, strUserData: 

string) { 

if (iEventType == VCOM_QUEUEEVENT_AGENTSERVICE) { //查询队列回调 if (iErrorCode == 0){ //可以执行解析 lpUserData 数据(Json 格式) } } } 

_// lpUserData_ 参考值 _(JSON)_ : _{"agent": "AgentUserCode"} JSON_ 字段说明: _agent_ ,分配的坐席用户 _ID_ 

### **4.6** 开始通话 

当坐席接听呼叫后,双方会触发“开始通话”事件。进入事件中 指定的会议即可开始音视频交互,(音视频交互参考五、音视频通 信)。参考代码如下: 

第 16 页共 22 页 

VideoComm Media SDK For Harmony 开发流程指南 

###### //排队回调 

public OnQueueEvent(iEventType: number, iErrorCode: number, strUserData: string) { if (iEventType == VCOM_QUEUEEVENT_STARTVIDEO) { //开始通话回调 if (iErrorCode == 0){ //可以执行解析 lpUserData 数据(Json 格式) VComMediaSDK.VCOM_JoinConference(confid, "", ""); } } } 

_// lpUserData_ 参考值 _(JSON)_ : _{"confid": "C0034443-2B19-4822-82A9-18117811647A"}_ 

_JSON_ 字段说明: _confid_ 服务器分配的会议 _ID_ ,接受到事件后进入此会议进行视频通话 

### **4.7** 用户主动挂断通话 

视频通话过程中,用户可以主动挂断通话。参考代码如下: 

VComMediaSDK. VCOM_QueueControl(VCOM_QUEUECTRL_HANGUPVIDEO, "");//挂断通话 

调用后会在 OnQueueEvent 方法的回调里收到信息,如下: 

第 17 页共 22 页 

VideoComm Media SDK For Harmony 开发流程指南 

###### //排队回调 

public OnQueueEvent(iEventType: number, iErrorCode: number, strUserData: string) { 

if (iEventType == VCOM_QUEUEEVENT_HANDUPVIDEO) { 

//离开队列回调 if (iErrorCode == 0){ // iErrorCode 表示挂断原因,=0 为正常挂断,其他值为异常挂断,比如网 络掉线 } } } 

### **4.8** 坐席主动挂断通话 

##### 通话过程中,坐席可以主动挂断通话,用户端会触发 

##### OnQueueEvent 回调。参考代码如下: 

###### //排队回调 

public OnQueueEvent(iEventType: number, iErrorCode: number, strUserData: string) { 

if (iEventType == VCOM_QUEUEEVENT_HANDUPVIDEO) { 

###### //离开队列回调 

if (iErrorCode == 0){ 

// iErrorCode 表示挂断原因,=0 为正常挂断,其他值为异常挂断,比如网 络掉线 } } } 

第 18 页共 22 页 

VideoComm Media SDK For Harmony 开发流程指南 

## 五、音视频通信 

VideoComm Media SDK 为开发者提供音视频通信能力。通过以 下几个步骤,即可在您的应用中使用音视频通信功能。注意:只有 进入相同会议的用户才能进行音视频交互。 

### **5.1** 加入会议 

登陆成功之后,我们需要调用 SDK 的加入会议接口。参考代 码如下: 

VComMediaSDK.VCOM_JoinConference("会议号", "", "");//进入会议 

### **5.2** 准备 **XComponent** 控件 

(1)在布局文件中添加 XComponent 的控件,用户视频画面显示, 下面的控件主要用于显示自己的画面。包裹 XComponent 容器的大 小可以自定义。参考代码如下: 

Column() { XComponent({ type: XComponentType.SURFACE, id: "VComMainVideo", libraryname: "vcommediasdk" }) .width('100%') .height('50%') .backgroundColor($r('app.color.vcom_theme_blue')) } 

第 19 页共 22 页 

VideoComm Media SDK For Harmony 开发流程指南 

注:XComponent 控件 type 类型需要设置为 XComponentType.SURFACE,id 可以自定义但需要保证唯一,后面做视频渲染设置需要此 id,libraryname 值必须为 vcommediasdk。 

### **5.3** 开始音视频通信 

(1)本地音视频开启(必须在 OnConferenceResult 回调中接收到进入 会议成功才可以设置本地视频渲染)。参考代码如下: 

//1.设置视频容器并返回显示对象 SurfaceView VComMediaSDK.VCOM_SetLocalVideoRender(mUserSelfId, mIntLocalChannelIndex, "VComMainVideo", this); 

//2.打开本地音视频 

VComMediaSDK.VCOM_OpenLocalMediaStream(mIntLocalChannelIndex, "" mIntLocalVideoOpen, mIntLocalAudioOpen, ); 

(2) 远程音视频开启(必须在 OnConferenceUser 回调中接收到远程 用户进入会议成功才可以设置视频渲染)。参考代码如下: 

//1.设置视频容器并返回显示对象 SurfaceView VComMediaSDK.VCOM_SetRemoteVideoRender(userId, mIntRemoteChannelIndex, "VComSubVideo", this); //3.获取远程流渲染 SurfaceView VComMediaSDK.VCOM_GetRemoteMediaStream(userId, mIntRemoteChannelIndex, mIntRemoteVideoOpen, mIntRemoteAudioOpen, ""); 

注:VCOM_SetLocalVideoRender 与 VCOM_SetRemoteVideoRender 设置视 频渲染的第三个参数传入的便是 XComponent 控件的 ID 值。 

第 20 页共 22 页 

VideoComm Media SDK For Harmony 开发流程指南 

### **5.4** 离开会议 

App 或者当前 Activity 销毁或者退出时。我们需要离开会议。 参考代码如下: 

VComMediaSDK.VCOM_LeaveConference(); 

第 21 页共 22 页 

VideoComm Media SDK For Harmony 开发流程指南 

## 六、资源释放 

在 App 摧毁时,或者功能不用时。根据需要把资源释放。下 面模拟的是 App 摧毁时需要的步骤。参考代码如下: 

### **6.1** 退出(注销) 

断开与 SDK 服务器的通讯连接。参考代码如下: 

VComMediaSDK.VCOM_Logout(); 

### **6.2** 释放资源 

释放整个 SDK 的资源。注意:释放 SDK 之后,需要重新初始 

化 SDK 之后才能进行登录、加入会议等操作。参考代码如下: 

VComMediaSDK.VCOM_Release(); 

第 22 页共 22 页
