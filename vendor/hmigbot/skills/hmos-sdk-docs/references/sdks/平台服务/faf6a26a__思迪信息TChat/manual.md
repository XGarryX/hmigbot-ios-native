# 思迪视频客户端 **SDK** 开发手册 

# ( ) **HarmonyOS** 

#### 版本历史 

|版本|更新日期||备注|
|---|---|---|---|
|9.0|2024-3-15|初始版本||

##### 目录 

|1. 准备工作....................................................................................................................................... 6|
|---|
|1.1引入开发包.......................................................................................................................... 6|
|1.2引入界面元素...................................................................................................................... 6|
|1.3函数调用顺序...................................................................................................................... 7 |
|2. 数据结构及常量定义................................................................................................................... 8|
|2.1内核参数定义...................................................................................................................... 8|
|2.2显示容器定义...................................................................................................................... 9|
|2.3设备类型定义...................................................................................................................... 9|
|2.4音频类型定义...................................................................................................................... 9|
|2.5呼叫类型定义.................................................................................................................... 10|
|2.6呼叫事件定义.................................................................................................................... 10 |
|2.7用户标志定义.................................................................................................................... 10|
|2.8用户状态定义.................................................................................................................... 10|
|2.9录像类型定义.................................................................................................................... 10|
|2.10快照标志定义.................................................................................................................. 10|
|2.11媒体播放标志.................................................................................................................. 11|
|2.12媒体播放控制.................................................................................................................. 11|
|3. 接口说明..................................................................................................................................... 12|
|3.1初始化与资源释放............................................................................................................ 12|
|3.1.1初始化SDK..............................................................................................................12|
|3.1.2激活日志................................................................................................................. 12|
|3.1.3设置内核参数(number型)...............................................................................13|
|3.1.4设置内核参数(string型)...................................................................................13|
|3.1.5获取内核参数(number型)...............................................................................13|
|3.1.6获取内核参数(string型)...................................................................................14|
|3.1.7释放SDK资源.........................................................................................................14|
|3.2业务流程............................................................................................................................ 15|
|3.2.1设置认证密码.........................................................................................................15|
|3.2.2连接服务器.............................................................................................................15|
|3.2.3登录系统................................................................................................................. 15|
|3.2.4进入房间................................................................................................................. 16|
|3.2.5进入房间扩展.........................................................................................................16|
|3.2.6离开房间................................................................................................................. 16|
|3.2.7登出系统................................................................................................................. 17|
|3.2.8呼叫控制................................................................................................................. 17|
|3.2.9获取房间名称.........................................................................................................18|
|3.2.10获取用户状态(string)........................................................................................... 18|
|3.2.11获取用户状态(number)........................................................................................18|
|3.2.12获取房间用户列表...............................................................................................19|
|3.3媒体及设备操作................................................................................................................ 20|
|3.3.1视频控制................................................................................................................. 20|
|3.3.2获取当前设备.........................................................................................................20|
|3.3.3获取设备数量.........................................................................................................20|

|3.3.4获取设备名称.........................................................................................................21|
|---|
|3.3.5选择当前设备.........................................................................................................21|
|3.3.6显示用户视频.........................................................................................................21|
|3.3.7停止显示视频.........................................................................................................22|
|3.3.8使能扬声器.............................................................................................................22 |
|3.3.9音频控制................................................................................................................. 22|
|3.3.10发送文本消息.......................................................................................................23|
|3.3.11发送透明通道消息...............................................................................................23|
|3.3.12获取音量...............................................................................................................24|
|3.3.13设置音量...............................................................................................................24|
|3.3.14获取网络质量.......................................................................................................24|
|3.3.15获取发送速度.......................................................................................................25|
|3.3.16获取网络接收速度...............................................................................................25 |
|3.3.17开始录像...............................................................................................................25|
|3.3.18停止录像...............................................................................................................26|
|3.3.19拍照截图...............................................................................................................26|
|3.3.21媒体播放初始化...................................................................................................27 |
|3.3.22媒体播放控制.......................................................................................................27|
|3.3.23媒体播放隐藏.......................................................................................................28|
|3.3.24外部视频导入.......................................................................................................28|
|3.3.25外部音频导入.......................................................................................................29 |
|3.3.26获取音频缓存.......................................................................................................30|
|3.3.27释放媒体资源.......................................................................................................30|
|3.3.28媒体播放信息获取...............................................................................................30|
|3.3.29设置音频导入格式...............................................................................................31|
|3.3.30设置视频导入格式...............................................................................................31|
|3.3.31导入音频数据.......................................................................................................32|
|3.3.32导入视频数据.......................................................................................................32 |
|3.3.33设置媒体服务.......................................................................................................32|
|3.3.34设置视频旋转度数...............................................................................................33|
|4. 回调通知..................................................................................................................................... 34|
|4.1基础通知............................................................................................................................ 34 |
|4.1.1连接通知................................................................................................................. 34|
|4.1.2登录通知................................................................................................................. 34|
|4.1.3自己进入房间通知.................................................................................................34 |
|4.1.4房间在线人数通知.................................................................................................35|
|4.1.5音频控制................................................................................................................. 35|
|4.1.6视频控制................................................................................................................. 35|
|4.1.7用户进入房间通知.................................................................................................36|
|4.1.8用户离开房间通知.................................................................................................36|
|4.1.9视频就绪通知.........................................................................................................36|
|4.1.10音频就绪通知.......................................................................................................36|
|4.1.11连接断开通知.......................................................................................................37|
|4.1.12离开房间通知.......................................................................................................37|

|4.1.13初始化通道通知...................................................................................................37|
|---|
|4.1.14初始化通道通知扩展...........................................................................................37|
|4.1.15网络质量通知.......................................................................................................38|
|4.1.16网络码率通知.......................................................................................................38|
|4.1.17音频状态改变通知...............................................................................................38|
|4.1.18视频状态改变通知...............................................................................................39|
|4.1.19媒体播放完成通知...............................................................................................39|
|4.1.20音频中断通知.......................................................................................................39|
|4.1.21视频中断通知.......................................................................................................39|
|4.1.22文本消息通知.......................................................................................................40|
|4.1.23透明通道消息通知...............................................................................................40|
|4.1.24本地视频数据回调通知.......................................................................................41|
|4.1.25本地音频数据回调通知.......................................................................................41|
|4.1.26呼叫回调通知.......................................................................................................42|
|4.1.27快照回调通知.......................................................................................................42|
|4.2视频录像通知.................................................................................................................... 44|
|4.2.1视频录像开始.........................................................................................................44|
|4.2.2视频录像停止.........................................................................................................44|
|4.2.3视频录像出错.........................................................................................................45|
|5.错误码........................................................................................................................................... 46|

## **1.** 准备工作 

### **1.1** 引入开发包 

将 tchatsdk_framework_v9.0.0_20240311.har 拷贝进工程目录下,然后在 

oh-package.json5 中配置如下依赖模块,至此sdk 引入成功。 

"dependencies": { "@ohos/tchatsdk-framework": "file:../TChatSDKLib/tchatsdk_framework_v9 .0.0 _20240311.har" } 

### **1.2** 引入界面元素 

在 HarmonyOS 页面 page.ets 中引入XComponent 组件并设置type: 'surface',用于渲 染本地和对端视频。 

XComponent({ id: DefineUtil.TKCC_XCOMPONENT_REMOTE, type: 'surface', libraryname: 'tchatsdk', controller: this.mXComponentController }) .onLoad(() => { }) .width('480px') .height('640px') .padding(10) 

### **1.3** 函数调用顺序 

|调用顺序|函数|功能|备注|
|---|---|---|---|
|1|InitSDK|初始化SDK|初始化|
||SetSDKOption|设置SDK内核参数||
||SetServerAuthPass|设置认证密码||
|2|Connect|连接服务器|进入系统|
||Login|登录系统||
||EnterRoom|进入房间||
||GetRoomName|获取当前房间名称||
||GetRoomOnlineUser|获取当前房间用户列表||
||GetUserState|获取用户状态||
||SendTextMessage|发送文本消息||
|3|TransBuffer|传送透明通道|常用功能|
||UserVideoControl|用户视频控制||
||UserAudioControl|用户音频控制||
||ShowUserVideo|显示用户视频||
||StopUserVideo|隐藏用户视频||
||CallControl|呼叫控制||
||LeaveRoom|离开房间||
|4|Logout|登出系统|退出系统|
||Release|释放SDK资源||

注意:正常情况下,只需要调用一次 **TKCC_InitSDK** 。如已调用 **TKCC_Release** ,需要再次 调用 **TKCC_InitSDK** 才能视频。 

## **2.** 数据结构及常量定义 

### **2.1** 内核参数定义 

DefineUtil.TKCC_SO_CORESDK_MAIN_VERSION; DefineUtil.TKCC_SO_CORESDK_SUB_VERSION; DefineUtil.TKCC_SO_CORESDK_BUILD_TIME; DefineUtil.TKCC_SO_TMPDIR_RECORD; DefineUtil.TKCC_SO_TMPDIR_SNAPSHOT; DefineUtil.TKCC_SO_TMPDIR_CORESDK; DefineUtil.TKCC_SO_RECONNECT; 1) DefineUtil.TKCC_SO_LOG_LEVEL; 2) 

DefineUtil.TKCC_SO_LOCAL_VIDEO_BITRATE; 240) DefineUtil.TKCC_SO_LOCAL_VIDEO_FPS; 15) DefineUtil.TKCC_SO_LOCAL_VIDEO_GOP; 15;多方视频下有效) DefineUtil.TKCC_SO_LOCAL_VIDEO_WIDTH; 240) 

DefineUtil.TKCC_SO_LOCAL_VIDEO_HEIGHT; 320) 

DefineUtil.TKCC_SO_LOCAL_AUDIO_AEC_LEVEL; 0;-1:不启用) DefineUtil.TKCC_SO_RECORD_VIDEO_BITRATE; kbps) 

DefineUtil.TKCC_SO_RECORD_AUDIO_BITRATE; kbps) DefineUtil.TKCC_SO_RECORD_VIDEO_WIDTH; DefineUtil.TKCC_SO_RECORD_VIDEO_HEIGHT; DefineUtil.TKCC_SO_RECORD_AUDIO_FORMAT; DefineUtil.TKCC_SO_RECORD_VIDEO_FORMAT; 12:mp4) 

DefineUtil.TKCC_SO_ENABLE_OTM_MODE; 0) 

DefineUtil.TKCC_SO_ENABLE_AUDIO_TRANS; 1) DefineUtil.TKCC_SO_ENABLE_VIDEO_TRANS; 1) DefineUtil.TKCC_SO_CORESDK_STAGE_VERSION; DefineUtil.TKCC_SO_VIDEO_STRECH_FILLING; 

///< SDK 主版本号(整型) ///< SDK 从版本号(整型) ///< SDK 编译时间(字符串型) ///< 录像文件目录(字符串型) ///< 快照文件目录(字符串型) ///< 日志文件目录(字符串型) ///< 启用自动重连(整型;默认为 ///< 视频日志级别(整型;默认为 ///< 视频编码码率(整型;默认为 ///< 视频编码帧率(整型;默认为 ///< 视频关键帧距(整型;默认为 ///< 视频采集宽度(整型;默认为 ///< 视频采集高度(整型;默认为 ///< 回声消除开关(整型;默认为 ///< 录像视频码率(整型;单位: ///< 录像音频码率(整型;单位: ///< 录像视频宽度(整型) ///< 录像视频高度(整型) ///< 录像音频格式(整型;1:mp3) ///< 录像视频格式(整型;11:flv; 

///< 启用多方视频(整形;默认为 ///< 启用音频传输(整形;默认为 ///< 启用视频传输(整形;默认为 ///< SDK 阶段版本号(整型) ///< 拉伸显示(整形;默认为0) 

DefineUtil.TKCC_SO_OUTPUT_AUDIO_DATA; 认为0) DefineUtil.TKCC_SO_OUTPUT_VIDEO_DATA; 认为0) DefineUtil.TKCC_SO_OUTPUT_PEER_AUDIO_DATA; 认为0) DefineUtil.TKCC_SO_OUTPUT_PEER_VIDEO_DATA; 认为0) DefineUtil.TKCC_SO_VIDEO_RC_MODES; 认为1;0:质量优先;1:码率优先) DefineUtil.TKCC_SO_ENABLE_VOICE_COMMUNICATION; 形; 默认为1) DefineUtil.TKCC_SO_VIDEO_TRANS_MODE; UDP;1:始终TCP;2:优先UDP;3:优先TCP) DefineUtil.TKCC_SO_RECONNECT_TIMEOUT; DefineUtil.TKCC_SO_LOG_MODE; 1:关联日志) DefineUtil.TKCC_SO_LOG_COLLECTION; DefineUtil.TKCC_SO_MON_COLLECTION; DefineUtil.TKCC_SO_MUTE_SELF_AUDIO; 0) DefineUtil.TKCC_SO_MUTE_PEER_AUDIO; 0) 

///< 导出本地音频数据(整形;默 ///< 导出本地视频数据(整形;默 ///< 导出对端音频数据(整形;默 ///< 导出对端视频数据(整形;默 ///< 视频码率控制模式(整形;默 ///< OPENSLES 录音配置参数(整 ///< 视频传输模式(整形;0:始终 ///< 重连超时(整型) ///< 日志模式(整形;0:普通日志; ///< 日志收集(整形;默认为1) ///< 监控收集(整形;默认为0) ///< 本地音频静音(整形;默认为 ///< 对端音频静音(整形;默认为 

### **2.2** 显示容器定义 

DefineUtil.TKCC_XCOMPONENT_LOCAL; DefineUtil.TKCC_XCOMPONENT_REMOTE; 

///< 本地XComponent id ///< 对端XComponent id 

### **2.3** 设备类型定义 

DefineUtil.TKCC_DT_VIDEOCAPTURE; DefineUtil.TKCC_DT_AUDIOCAPTURE; DefineUtil.TKCC_DT_AUDIOPLAYER; 

///< 视频采集设备 ///< 音频采集设备 ///< 音频播放设备 

### **2.4** 音频类型定义 

DefineUtil.TKCC_AD_WAVEIN; DefineUtil.TKCC_AD_WAVEOUT; 

///< 音频输入设备 ///< 音频输出设备 

### **2.5** 呼叫类型定义 

DefineUtil.TKCC_CT_VIDEO; DefineUtil.TKCC_CT_AUDIO; 

///< 视频呼叫 ///< 音频呼叫 

### **2.6** 呼叫事件定义 

DefineUtil.TKCC_VIEDOCALL_EVENT_REQUEST; DefineUtil.TKCC_VIEDOCALL_EVENT_REPLY; DefineUtil.TKCC_VIEDOCALL_EVENT_START; DefineUtil.TKCC_VIEDOCALL_EVENT_FINISH; 

///< 视频呼叫请求事件 ///< 视频呼叫回复事件 ///< 视频呼叫开始事件 ///< 视频呼叫完成事件 

### **2.7** 用户标志定义 

DefineUtil.TKCC_USERSTATE_USERID; DefineUtil.TKCC_USERSTATE_USERSTATUS; DefineUtil.TKCC_USERSTATE_RECORDING; DefineUtil.TKCC_USERSTATE_NICKNAME; DefineUtil.TKCC_USERSTATE_DEVICETYPE; 

///< 用户ID ///< 用户状态 ///< 用户录像(音)状态 ///< 指定用户的昵称 ///< 指定用户的终端类型 

### **2.8** 用户状态定义 

DefineUtil.TKCC_USERSTATE_UNKNOWN DefineUtil.TKCC_USERSTATE_CONNECTED; DefineUtil.TKCC_USERSTATE_LOGINED; DefineUtil.TKCC_USERSTATE_INROOM; DefineUtil.TKCC_USERSTATE_LINKCLOSED; 

///< 未知用户状态 ///< 用户已连接 ///< 用户已登录 ///< 用户在房间 ///< 用户断开连接 

### **2.9** 录像类型定义 

DefineUtil.TKCC_RECORD_FLAGS_CLIENT; DefineUtil.TKCC_RECORD_FLAGS_STREAM; DefineUtil.TKCC_RECORD_FLAGS_SERVER; DefineUtil.TKCC_RECORD_FLAGS_AUDIO; DefineUtil.TKCC_RECORD_FLAGS_VIDEO; 

///< 客户端录像 ///< 合成流录像 ///< 服务器录像 ///< 只录制音频 ///< 录制音视频 

### **2.10** 快照标志定义 

DefineUtil.TKCC_SNAPSHOT_FLAGS_FILE; DefineUtil.TKCC_SNAPSHOT_FLAGS_DATA; 

///< 文件路径 ///< 文件数据(base64) 

### **2.11** 媒体播放标志 

DefineUtil.TKCC_STREAMPLAY_FLAGS_LOOP; DefineUtil.TKCC_STREAMPLAY_FLAGS_INPUT; 

///< 循环播放 ///< 导入播放 

### **2.12** 媒体播放控制 

DefineUtil.TKCC_STREAMPLAY_CTRL_PLAY; DefineUtil.TKCC_STREAMPLAY_CTRL_PAUSE; DefineUtil.TKCC_STREAMPLAY_CTRL_STOP; 

///< 开始播放 ///< 暂停播放 ///< 停止播放 

## **3.** 接口说明 

### **3.1** 初始化与资源释放 

### **3.1.1** 初始化 **SDK** 

TChatSDK.getInstance().InitSDK( context: Context, osver: number ):number; 

功能: 初始化SDK。 参数: context: 应用上下文 osver: 扩展参数 返回: 0:成功;-1:失败。 说明: 在应用全局初始化 sdk。 

### **3.1.2** 激活日志 

TChatSDK.getInstance().ActiveCallLog( active: boolean ):number; 功能: 激活 SDK 日志。 参数: active: 为真表示开启日志;否则表示关闭日志。 返回: 0:成功;-1:失败。 

### **3.1.3** 设置内核参数( **number** 型) 

TChatSDK.getInstance().SetSDKOptionInt( 

optname: number, optvalue: number ):number; 

功能: 

设置整形内核参数。 参数: optname: 内核参数名称;见2.1 小节中的“内核参数定义” optvalue: 内核参数数据 返回: 0:成功;-1:失败。 

### **3.1.4** 设置内核参数( **string** 型) 

TChatSDK.getInstance().SetSDKOptionString( optname: number, optvalue: string ):number; 功能: 设置字符串型内核参数。 参数: optname: 内核参数名称;见2.1 小节中的“内核参数定义” optvalue: 内核参数数据 返回: 0:成功;-1:失败。 

### **3.1.5** 获取内核参数( **number** 型) 

TChatSDK.getInstance().GetSDKOptionInt( 

optname: number ):number; 功能: 获取整形内核参数。 描述: optname: 内核参数名称;见2.1 小节中的“内核参数定义” 

返回: 

内核参数。 

### **3.1.6** 获取内核参数( **string** 型) 

TChatSDK.getInstance().GetSDKOptionString( optname: number ):number; 功能: 获取字符串型内核参数。 参数: optname: 内核参数名称;见2.1 小节中的“内核参数定义” 返回: 内核参数。 

### **3.1.7** 释放 **SDK** 资源 

TChatSDK.getInstance().Release():number; 

功能: 释放 SDK 占用的所有资源。 参数: 无 返回: 0:成功;-1:失败。 

### **3.2** 业务流程 

### **3.2.1** 设置认证密码 

TChatSDK.getInstance().SetServerAuthPass( 

password: string ):number; 

功能: 

设置服务器连接认证密码,确保 SDK 能正常连接到中心服务器 参数: password : 认证密码 返回: 0:成功;-1:失败。 

### **3.2.2** 连接服务器 

TChatSDK.getInstance().Connect( 

serverip: string, port: number ):number; 

功能: 

用于与信令服务器建立连接。 参数: serverip: 服务器ip port: 端口号 返回: 0:成功;-1:失败。 

### **3.2.3** 登录系统 

TChatSDK.getInstance().Login( 

username: string, password: string ):number; 

功能: 

登录服务器。 参数: 

username: 用户名 password: 用户密码;保留 返回: 0:成功;-1:失败。 

### **3.2.4** 进入房间 

TChatSDK.getInstance(). EnterRoom( 

roomid: number, roompass: string ):number; 

功能: 进入房间。 

参数: roomid: 房间id roompass: 房间密码 返回: 0:成功;-1:失败。 

### **3.2.5** 进入房间扩展 

TChatSDK.getInstance(). EnterRoomEx( 

roomname: string, roompass: string ):number; 

功能: 

进入房间。 参数: roomname: 房间名称 roompass: 房间密码 返回: 0:成功;-1:失败。 

### **3.2.6** 离开房间 

TChatSDK.getInstance(). LeaveRoom():number; 

功能: 

离开房间。 参数: 无 返回: 0:成功;-1:失败。 

### **3.2.7** 登出系统 

TChatSDK.getInstance(). Logout():number; 

功能: 登出系统。 参数: 无 返回: 0:成功;-1:失败。 

### **3.2.8** 呼叫控制 

TChatSDK.getInstance(). CallControl( 

|calltype:|number,|
|---|---|
|eventtype:|number|
|userid:|number,|
|errorcode:|number,|
|userparam:|number,|
|userstr:|string|

):number; 

功能: 

|视频呼叫。 参数:||
|---|---|
|calltype:|呼叫类型;见2.5 小节中的“呼叫类型定义”。|
|eventtype:|事件类型;见2.6 小节中的“呼叫事件定义”。|
|userid:|用户id|
|errorcode:|错误码|
|userparam:|自定义参数(整型)|
|userstr:|自定义参数(字符串型)|
|返回:||
|0:成功;-1:|失败。|

### **3.2.9** 获取房间名称 

TChatSDK.getInstance(). GetRoomName():string; 

功能: 

获取房间名称。 参数: 无 返回: 房间名称。 

### **3.2.10** 获取用户状态 **(string)** 

TChatSDK.getInstance(). GetUserStateString( userid: number, infoname: number 

):string; 

功能: 

获取字符串型用户状态 参数: userid: 用户id infoname: 状态名称;见2.7 小节中的“用户标志定义”。 返回: 用户状态。 

### **3.2.11** 获取用户状态 **(number)** 

TChatSDK.getInstance(). GetUserStateInt( userid: number, infoname: number ):number; 

功能: 

获取整形用户状态 参数: userid: 用户id infoname: 状态名称;见2.7 小节中的“用户标志定义”。 返回: 用户状态。 

### **3.2.12** 获取房间用户列表 

TChatSDK.getInstance().GetRoomOnlineUser():Int32Array; 

功能: 

获取当前房间的用户列表 参数: 无 返回: 在线用户列表 

### **3.3** 媒体及设备操作 

### **3.3.1** 视频控制 

TChatSDK.getInstance().UserVideoControl( 

userid: number, open: boolean ):number; 

功能: 用户视频控制,打开或关闭本地摄像头,或请求对方视频。 参数: userid: 用户id;为-1 表示本地视频,否则表示远程视频。 open: 为真表示开启;否则表示关闭。 返回: 0:成功;-1:失败。 

### **3.3.2** 获取当前设备 

TChatSDK.getInstance().GetCurDevice( devicetype: number ):string; 

功能: 

获取当前的设备名称 参数: devicetype: 设备类型;见2.3 小节中的“设备类型定义”。 返回 : 当前设备名称。 

### **3.3.3** 获取设备数量 

TChatSDK.getInstance().GetDeviceNum( 

devicetype: number ):number; 

功能: 获取设备数量 参数: devicetype: 设备类型;见2.3 小节中的“设备类型定义”。 

返回 : 

当前设备个数。 

### **3.3.4** 获取设备名称 

TChatSDK.getInstance().GetDeviceName( 

devicetype: number, index: number ):string; 功能: 获取设备名称 参数: devicetype: 设备类型;见2.3 小节中的“设备类型定义”。 index: 设备节点 返回 : 当前设备名称。 

### **3.3.5** 选择当前设备 

TChatSDK.getInstance().SelectDevice( 

devicetype: number, devicename: string ):number; 功能: 选择要使用的设备 参数: devicetype: 设备类型;见2.3 小节中的“设备类型定义”。 devicename: 设备名称 返回: 0:成功;-1:失败。 

### **3.3.6** 显示用户视频 

TChatSDK.getInstance().ShowUserVideo( 

userid: number, surfaceId: string mirror: boolean ):number; 

功能: 

显示视频 

参数: userid: 用户id surfaceId: XComponent 的surfaceId mirror: 为真表示开启镜像;否则表示关闭镜像 返回: 0:成功;-1:失败。 

### **3.3.7** 停止显示视频 

TChatSDK.getInstance().StopUserVideo( 

userid: number ):number; 功能: 停止视频 参数: userid: 用户id 返回: 0:成功;-1:失败。 

### **3.3.8** 使能扬声器 

TChatSDK.getInstance().EnableSpeaker( enable: boolean ):number; 功能: 使能扬声器 参数: enable: 为真表示开启;否则表示关闭 返回: 0:成功;-1:失败。 

### **3.3.9** 音频控制 

TChatSDK.getInstance().UserAudioControl( userid: number, 

open: boolean ):number; 

功能: 

用户音频控制,打开或关闭本地麦克风,或请求对方音频。 参数: userid: 用户id;为-1,表示本地音频,否则表示远程音频。 open: 为真表示开启;否则表示关闭。 返回: 0:成功;-1:失败。 

### **3.3.10** 发送文本消息 

TChatSDK.getInstance().SendTextMessage( userid: number, secret: boolean, msg: string ):number; 

功能: 发送文本消息 参数: userid: 用户id secret: 为真表示私密;否则表示广播 msg: 消息内容 返回: 0:成功;-1:失败。 

### **3.3.11** 发送透明通道消息 

TChatSDK.getInstance().TransBuffer( userid: number, buf: ArrayBuffer, len: number ):number; 功能: 发送透明消息 参数: 

userid: 用户id buf: 消息内容 len: 消息长度 返回: 0:成功;-1:失败。 

### **3.3.12** 获取音量 

TChatSDK.getInstance().AudioGetVolume( audiodevice: number ):number; 功能: 获取音量 参数: audiodevice: 音频设备;见2.4 小节中的“音频设备定义”。 返回: 0:成功;-1:失败。 

### **3.3.13** 设置音量 

TChatSDK.getInstance().AudioSetVolume( 

audiodevice: number, volume: number, ):number; 功能: 设置音量 参数: audiodevice: 音频设备;见2.4 小节中的“音频设备定义”。 volume: 设置音量 返回: 0:成功;-1:失败。 

### **3.3.14** 获取网络质量 

TChatSDK.getInstance().GetNetQuality( local: boolean ):number; 

功能: 

获取网络质量 参数: local: 为真表示本地;否则表示对端。 返回: 0:成功;-1:失败。 

### **3.3.15** 获取发送速度 

TChatSDK.getInstance().GetSendRate( local: boolean ):number; 功能: 获取网络上传速度 参数: local: 为真表示本地;否则表示对端。 返回: 0:成功;-1:失败。 

### **3.3.16** 获取网络接收速度 

TChatSDK.getInstance().GetRecvRate( local: boolean ):number; 功能: 获取网络接收速度 参数: local: 为真表示本地;否则表示对端。 返回: 0:成功;-1:失败。 

### **3.3.17** 开始录像 

TChatSDK.getInstance().StartRecord( 

user_array: Array<number>, num: number, flags: number, param: number, user_str: string ):number; 

功能: 开始录像 参数: user_array: 录像用户id 数组 num: 录像用户id 数组长度 flags: 录像类型;见2.9 小节中的录像类型定义。 param: 自定义参数(整形) user_str: 自定义参数(字符串型) 

返回: 

0:成功;-1:失败。 

### **3.3.18** 停止录像 

TChatSDK.getInstance().StopRecord( task_id: number ):number; 功能: 停止录像 参数: task_id: 录像任务id 返回: 0:成功;-1:失败。 

### **3.3.19** 拍照截图 

TChatSDK.getInstance().SnapShot( 

user_id: number, flags: number param: number, user_str: string ):number; 

功能: 

拍照截图 

参数: user_id: 用户id flags: 拍照类型;见2.10 小节中的快照功能定义。 param: 自定义参数(整型) user_str: 自定义参数(字符串型) 

返回: 

0:成功;-1:失败。 

### **3.3.21** 媒体播放初始化 

TChatSDK.getInstance().StreamPlayInit( 

|task_id:|number,|
|---|---|
|stream_path:|string|
|flags:|number,|
|param:|string|
|):number;||

功能: 

|媒体播放初始化||
|---|---|
|参数:||
|task_id:|任务id|
|stream_path:|媒体路径|
|flags:|播放标志;见2.11 小节中的播放标志定义。|
|param:|自定义参数(字符串型)|

返回: 0:成功;-1:失败。 

### **3.3.22** 媒体播放控制 

TChatSDK.getInstance().StreamPlayControl( 

task_id: number, ctrl_code: number, ctrl_param: number, flags: number, param: string ):number; 

功能: 

媒体播放控制 

参数: 

task_id: 任务id ctrl_code: 播放控制;见2.12 小节中的播放控制定义。 ctrl_param: 播放参数;保留 flags: 播放标志;保留 param: 自定义参数(字符串型) 返回: 0:成功;-1:失败。 

### **3.3.23** 媒体播放隐藏 

TChatSDK.getInstance().StreamPlayHide( task_id: number ):number; 功能: 媒体播放隐藏 参数: task_id: 任务id 返回: 0:成功;-1:失败。 

### **3.3.24** 外部视频导入 

TChatSDK.getInstance().StreamPlayInputVideoData( 

task_id: number, format: number, width: number, heigth: number, fps: number, flags: number, buf: ArrayBuffer, len: number, time_stamp: number ):number; 

功能: 外部视频导入 

参数: 

|task_id:|任务id|
|---|---|
|format:|视频格式|
|width:|视频宽|
|height:|视频高|
|fps:|视频帧率|
|flags:|导入类型|
|buf:|视频原始数据|
|len:|视频长度|
|time_stamp:|时间戳|

返回: 

0:成功;-1:失败。 

### **3.3.25** 外部音频导入 

TChatSDK.getInstance().StreamPlayInputAudioData( 

|task_id:|number,|
|---|---|
|format:|number,|
|channel:|number,|
|samples_per_second:|number,|
|bits_per_sample:|number,|
|flags:|number,|
|buf:|ArrayBuffer,|
|len:|number,|
|time_stamp:|number|
|):number;||

##### 功能: 

|外部音频导入||
|---|---|
|参数:||
|task_id:|任务id|
|format:|音频格式|
|channel:|通道数|
|samples_per_second:|采样率|
|bits_per_sample:|位宽|
|flags:|导入类型|
|buf:|音频原始数据|
|len:|音频长度|
|time_stamp:|时间戳|

##### 返回: 

0:成功;-1:失败。 

### **3.3.26** 获取音频缓存 

TChatSDK.getInstance().StreamPlayGetAudioCache( task_id: number ):number; 

功能: 获取音频缓存 参数: task_id: 任务id 返回: 音频缓存大小。 

### **3.3.27** 释放媒体资源 

TChatSDK.getInstance().StreamPlayDestory( task_id: number ):number; 功能: 释放媒体资源 参数: task_id: 任务id 返回: 0:成功;-1:失败。 

### **3.3.28** 媒体播放信息获取 

TChatSDK.getInstance().StreamPlayGetInfo( task_id: number ):string; 

功能: 获取媒体信息 参数: task_id: 任务id 返回: 媒体信息。 

### **3.3.29** 设置音频导入格式 

|TChatSDK.getInstance().SetInput channel:|AudioFormat( number,|
|---|---|
|samples_per_second:|number,|
|bits_per_sample:|number,|
|flags:|number|
|):number;||

功能: 

设置音频导入格式 

参数: 

channel: 通道数 samples_per_second: 采样率 bits_per_sample: 位宽 flags: 导入类型 

返回: 

0:成功;-1:失败。 

### **3.3.30** 设置视频导入格式 

TChatSDK.getInstance().SetInputVideoFormat( 

|format:|number,|
|---|---|
|width:|number,|
|heigth:|number,|
|fps:|number,|
|flags:|number|
|):number;||

功能: 设置视频导入格式 参数: format: 视频格式 width: 视频宽度 height: 视频高度 fps: 视频帧率 flags: 导入类型 返回: 0:成功;-1:失败。 

### **3.3.31** 导入音频数据 

|TChatSDK.getInstance().InputAudioData( |
|---|
|buf: ArrayBuffer,|
|len: number,|
|time_stamp: number|
|):number;|

功能: 

导入音频数据 

|参数:||
|---|---|
|buf:|音频数据|
|len:|数据长度|
|time_stamp:|时间戳|

返回: 

0:成功;-1:失败。 

### **3.3.32** 导入视频数据 

|TChatSDK.getInstance().InputVideoData( |
|---|
|buf: ArrayBuffer,|
|len: number,|
|time_stamp: number|
|):number;|

功能: 

导入视频数据 

|参数:||
|---|---|
|buf:|视频数据|
|len:|数据长度|
|time_stamp:|时间戳|
|返回:||
|0:成功;-1:|失败。|

### **3.3.33** 设置媒体服务 

TChatSDK.getInstance().SetMediaServer( ms_addr: string ):number; 

功能: 

用于媒体服务器地址外设。 

参数: 

ms_addr: 媒体服务器地址 返回: 

0:成功;-1:失败。 

### **3.3.34** 设置视频旋转度数 

TChatSDK.getInstance().RotateUserVideo( userid: number, degree: number ):number; 

功能: 旋转视频。 参数: userid: 用户id degree: 旋转度数 返回: 0:成功;-1:失败。 

## **4.** 回调通知 

### **4.1** 基础通知 

### **4.1.1** 连接通知 

OnConnect(success:boolean, errorCode:number):void 

功能: 

连接通知 参数: success: 连接状态true:成功false:失败 errorCode: 错误码 

### **4.1.2** 登录通知 

OnLogin(userId:number, errorCode:number):void 

功能: 

登录通知 参数: userId: 用户id errorCode: 错误码 

### **4.1.3** 自己进入房间通知 

OnEnterRoom(roomId:number, errorCode:number):void 

功能: 

自己进入房间 参数: roomId: 房间号id errorCode: 错误码 

### **4.1.4** 房间在线人数通知 

OnRoomOnlineUser(userNum:number, roomId:number):void 

功能: 

房间在线人数 

参数: userNum: 房间人数 roomId: 房间号 

### **4.1.5** 音频控制 

OnUserAudioCtl(userId:number, lparam:number):void 

功能: 

音频控制 

参数: userId: 用户id lparam: 控制动作及错误代码 高16 位表示控制动作;0 表示关闭,1 表示打开。 低16 位表示错误代码;0 表示成功,否则表示失败。 如控制动作:(lparam & 0xFFFF0000) >> 16) 

### **4.1.6** 视频控制 

OnUserVideoCtl(userId:number, lparam:number):void 

功能: 

视频控制 

参数: 

userId: 用户id lparam: 控制动作及错误代码 高16 位表示控制动作;0 表示关闭,1 表示打开。 低16 位表示错误代码;0 表示成功,否则表示失败。 如控制动作:(lparam & 0xFFFF0000) >> 16) 

### **4.1.7** 用户进入房间通知 

OnUserEnterRoom(userId:number):void 

功能: 

用户进入房间 参数: userId: 用户id 

### **4.1.8** 用户离开房间通知 

OnUserLeaveRoom(userId:number):void 

功能: 

用户离开房间 参数: userId: 用户id 

### **4.1.9** 视频就绪通知 

OnUserVideoDataReady(wparam:number, lparam:number):void 

功能: 

视频就绪通知 参数: wparam: 就绪状态 lparam: 高16 位表示视频宽度 低16 位表示视频高度 高:(lparam & 0x0000FFFF) 宽:(lparam & 0xFFFF0000) >> 16 

### **4.1.10** 音频就绪通知 

OnUserAudioDataReady(wparam:number, lparam:number):void 

功能: 

音频就绪通知 

参数: 

wparam: 就绪状态 lparam: 保留参数 

### **4.1.11** 连接断开通知 

OnLinkClose(errorCode:number):void 

功能: 

连接断开通知 

参数: errorCode: 错误码 

### **4.1.12** 离开房间通知 

OnLeaveRoom(roomId:number):void 

功能: 

离开房间通知 参数: roomId: 房间id 

### **4.1.13** 初始化通道通知 

OnInitChannel(errorCode:number):void 

功能: 

初始化通道通知 参数: errorCode: 错误码 

### **4.1.14** 初始化通道通知扩展 

OnInitChannelEx(userId:number, errorCode:number):void 

功能: 

初始化通道通知扩展 参数: userId: 用户id 

错误码 

errorCode: 

### **4.1.15** 网络质量通知 

OnNetQuality(local:number, qos:number):void 

功能: 

网络质量通知 

参数: 

local: 本地标志 qos: 网络质量: 0:获取失败; 1:网络很好; 2:网络较好; 3:网络较差; 4:网络很差; 

### **4.1.16** 网络码率通知 

OnNetBitRate(SenBps:number, RecvBps:number):void 功能: 网络码率通知 参数: SenBps: 发送码率 RecvBps: 接收码率 

### **4.1.17** 音频状态改变通知 

OnUserAudioStatusChg(userId:number, status:number):void 

功能: 

音频状态改变通知 参数: userId: 用户id status: 状态(0:关闭1:开启) 

### **4.1.18** 视频状态改变通知 

OnUserVideoStatusChg(userId:number, status:number):void 

功能: 

视频状态改变通知 参数: userId: 用户id status: 状态(0:关闭1:开启) 

### **4.1.19** 媒体播放完成通知 

OnStreamPlayFinished(taskId:number, param:number):void 功能: 媒体播放完成通知 参数: taskId: 任务id param: 保留参数 

### **4.1.20** 音频中断通知 

OnAudioInterrupt(wparam:number, lparam:number):void 

功能: 

音频中断通知 参数: wparam: 用户id lparam: 0:表示断流;1:表示恢复。 

### **4.1.21** 视频中断通知 

OnVideoInterrupt(wparam:number, lparam:number):void 

功能: 

音频中断通知 

参数: wparam: 用户id lparam: 0:表示断流;1:表示恢复。 

### **4.1.22** 文本消息通知 

OnTextMessageCallBack( 

fromUserId: number, toUserId: number, secret: boolean, msgBuf: string):void 

功能: 

文本消息通知回调 参数: fromUserId: 文本发送者id toUserId: 文本接收者id secret: 为真表示私密发送,为假表示广播发送 msgBuf: 收到消息内容 

### **4.1.23** 透明通道消息通知 

OnTransBufferCallBack( 

userId: number, buf: ArrayBuffer, len: number):void 

功能: 

透明通道消息通知回调 参数: userId: 文本发送者id buf: 收到消息内容 len: 内容长度 

### **4.1.24** 本地视频数据回调通知 

OnVideoDataCallBack( 

userId: number, buf: ArrayBuffer, len: number, width: number, height: number):void 

功能: 

本地视频数据回调 参数: userId: 用户id buf: 视频数据 len: 数据长度 width: 视频宽度 height: 视频高度 

### **4.1.25** 本地音频数据回调通知 

OnAudioDataCallBack( 

userId: number, buf: ArrayBuffer, len: number, channels: number, samplesPerSec: number, bitPerSample: number):void 

##### 功能: 

##### 本地音频数据回调 

参数: userId: 用户id buf: 音频数据 len: 数据长度 channels: 通道数 samplesPerSec: 采样率 

bitPerSample: 

位宽 

### **4.1.26** 呼叫回调通知 

OnCallEventCallBack( 

callType: number, eventType: number, userId: number, errorCode: number, param: number, userStr: string):void 功能: 呼叫回调 参数: calltype: 呼叫类型;见2.5 小节中的“视频呼叫类型定义”。 eventType: 事件类型;见2.6 小节中的“视频呼叫事件定义”。 userid: 用户id errorcode: 错误码 userparam: 自定义参数(整型) userstr: 自定义参数(字符串) 

### **4.1.27** 快照回调通知 

OnSnapShotCallBack( taskId: number, filePath: string, errorCode: number, flags: number, param: number, userStr: string):void 功能: 快照回调 参数: taskId: 任务id filePath: 文件路径/快照数据(RGB24 的base64 编码) 

|errorCode:|错误码|
|---|---|
|flags:|快照类型;见2.10 小节中的快照标志定义。|
|param:|自定义参数(整型)|
|userStr:|自定义参数(字符串)|

### **4.2** 视频录像通知 

### **4.2.1** 视频录像开始 

OnStartRecordCallBack( taskId: number, filePath: string, errorCode: number, flags: number, param: number, userStr: string):void 

##### 功能: 

视频录制开始 

参数: taskId: 任务id filePath: 文件路径 errorCode: 错误码 flags: 录像类型;见2.9 小节中的录像类型定义。 param: 自定义参数(整型) userStr: 自定义参数(字符串) 

### **4.2.2** 视频录像停止 

OnStopRecordCallBack( 

taskId: number, filePath: string, errorCode: number, elapse: number, flags: number, param: number, userStr: string):void 

##### 功能: 

视频录制停止 参数: taskId: 任务id 

filePath: 文件路径 errorCode: 错误码 elapse: 录像时长 flags: 录像类型;见2.9 小节中的录像类型定义。 param: 自定义参数(整型) userStr: 自定义参数(字符串) 

### **4.2.3** 视频录像出错 

OnRecordErrorCallBack( taskId: number, filePath: string, errorCode: number, flags: number, param: number, userStr: string):void 功能: 视频录制出错 参数: taskId: 任务id filePath: 文件路径 errorCode: 错误码 flags: 录像类型;见2.9 小节中的录像类型定义。 param: 自定义参数(整型) userStr: 自定义参数(字符串) 

## **5.** 错误码 

TKCC_ERR_SUCCESS: 0; ///< 成功 TKCC_ERR_SYSTEM_UNKNOWN: -1; ///< 未知错误 TKCC_ERR_CONNECT_TIMEOUT: 100; ///< 连接服务器超时 TKCC_ERR_CONNECT_ABORT: 101; ///< 与服务器的连接中断 TKCC_ERR_CONNECT_DNSERROR: 102; ///< 域名解析失败 TKCC_ERR_CONNECT_AUTHFAIL: 103; ///< 连接服务器认证失败 TKCC_ERR_CONNECT_OLDVERSION: 104; ///< 版本太旧,不允许连接 TKCC_ERR_CONNECT_EXPIRE: 105; ///< 与服务器的连接过期 TKCC_ERR_CONNECT_CHANGE: 106; ///< 与服务器的连接变化 TKCC_ERR_CONNECT_MAXSIZE: 107; ///< 连接数超过最大限制 TKCC_ERR_CERTIFY_FAIL: 200; ///< 认证失败,用户名或密码有误 TKCC_ERR_VISITOR_DENY: 201; ///< 游客登录被禁止 TKCC_ERR_ALRADY_LOGIN: 202; ///< 用户已登录 TKCC_ERR_USER_TYPE: 203; ///< 用户类型不支持 TKCC_ERR_ROOM_PASSERR: 300; ///< 房间密码错误,禁止进入 TKCC_ERR_ROOM_FULLUSER: 301; ///< 房间已满员,不能进入 TKCC_ERR_ROOM_ENTERFAIL: 302; ///< 禁止进入房间 TKCC_ERR_ROOM_IDINVALID: 303; ///< 房间ID 错误 TKCC_ERR_ROOM_ALREADYIN: 304; ///< 用户已在房间内 TKCC_ERR_ROOM_NOTEXIST: 305; ///< 房间不存在 TKCC_ERR_MAX_ROOM_NUMBER: 306; ///< 房间数已满 TKCC_ERR_USER_NOTINROOM: 400; ///< 用户不在房间内 TKCC_ERR_USER_OFFLINE: 401; ///< 用户不在线 TKCC_ERR_USER_IDINVALID: 402; ///< 用户ID 错误 TKCC_ERR_USER_LOGINED: 403; ///< 用户已登录 TKCC_ERR_STREAM_TIMEOUT: 500; ///< 通道建立超时 TKCC_ERR_CALL_DENY: 600; ///< 呼叫受限 TKCC_ERR_CALL_BUSY: 601; ///< 对方繁忙 TKCC_ERR_CALL_REFUSE: 602; ///< 对方拒绝 TKCC_ERR_CALL_CANCEL: 603; ///< 对方拒绝 TKCC_ERR_RECORD_CREATEFAIL: 700; ///< 创建录像任务失败 TKCC_ERR_RECORD_AUTHFAIL: 701; ///< 合成录像认证失败 TKCC_ERR_RECORD_CREATEFILEFAIL: 702; ///< 创建录像文件失败 TKCC_ERR_RECORD_WRITEFILEFAIL: 703; ///< 写入录像文件失败 TKCC_ERR_RECORD_ALREADYSTARTED: 704; ///< 房间录像已被启动 TKCC_ERR_RECORD_TIMEOUT: 705; ///< 录像响应超时 TKCC_ERR_RECORD_INVALID: 706; ///< 录像任务无效 TKCC_ERR_RECORD_NOTSTART: 707; ///< 录像尚未启动 TKCC_ERR_RECORD_INTERRUPT: 708; ///< 录像媒体断流 TKCC_ERR_RECORD_INTERNAL: 709; ///< 录像内部错误 TKCC_ERR_RECORD_DISCONNECTED: 710; ///< 录像连接中断 

TKCC_ERR_RECORD_STARTTIMEOUT: 711; ///< 录像启动超时 TKCC_ERR_RECORD_STOPTIMEOUT: 712; ///< 录像停止超时 TKCC_ERR_SERVER_NOMEDIA: 800; ///< 无在线媒体服务器 TKCC_ERR_SERVER_NORECORD: 801; ///< 无在线录像服务器 TKCC_ERR_SERVER_MEDIAOFFLINE: 802; ///< 媒体服务器已下线
