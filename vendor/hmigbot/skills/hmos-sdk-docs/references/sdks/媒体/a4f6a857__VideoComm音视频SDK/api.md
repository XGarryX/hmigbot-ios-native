# VideoComm Media SDK

# For Harmony

# 接口开发手册

(版本:V3.3)

VideoCommMediaSDKForHarmony 接口开发手册

### 目录

1.概述................................................................................................................................................5

1.1.产品简介............................................................................................................................ 5

1.2.我们的优势.........................................................................................................................5

1.3.目标人群.............................................................................................................................7

2. API 定义......................................................................................................................................... 8

2.1. API 概览...............................................................................................................................8

2.2. API使用指引..................................................................................................................... 9

2.3. SDK 事件管理管理...........................................................................................................11

2.3.1. VCOM_SetSDKEvent............................................................................................11

2.3.2. VCOM_RemoveSDKEvent....................................................................................11

2.4.初始化管理.......................................................................................................................12

2.4.1. VCOM_Initialize....................................................................................................12

2.4.2. VCOM_Release......................................................................................................12

2.4.3. VCOM_GetSDKVersion........................................................................................ 13

2.4.4. VCOM_SetLogLevel..............................................................................................13

2.4.5. VCOM_SetSDKParamInt...................................................................................... 14

2.4.6. VCOM_SetSDKParamString.................................................................................14

2.4.7. VCOM_SDKCommon........................................................................................... 15

2.5.用户管理...........................................................................................................................15

2.5.1. VCOM_SetUserConfig.......................................................................................... 15

2.5.2. VCOM_Login.........................................................................................................16

2.5.3. VCOM_Logout.......................................................................................................16

2.6.会议管理...........................................................................................................................17

2.6.1. VCOM_JoinConference.........................................................................................17

2.6.2. VCOM_LeaveConference......................................................................................17

2.6.3. VCOM_GetConferenceUsers.................................................................................18

2.7.音视频通信.......................................................................................................................18

2.7.1. VCOM_GetCameraDeviceCount...........................................................................18

2.7.2. VCOM_GetCameraDeviceName...........................................................................19

2.7.3. VCOM_GetMicrophoneDeviceCount....................................................................19

2.7.4. VCOM_GetMicrophoneDeviceName....................................................................20

2.7.5. VCOM_SetCaptureDevice.....................................................................................20

2.7.6. VCOM_OpenLocalMediaStream...........................................................................21

2.7.7. VCOM_CloseLocalMediaStream.......................................................................... 21

2.7.8. VCOM_GetRemoteMediaStream.......................................................................... 22

2.7.9. VCOM_CloseRemoteMediaStream.......................................................................22

2.7.10. VCOM_GetVideoParamConfigure...................................................................... 23

2.7.11. VCOM_SetVideoParamConfigure.......................................................................23

2.7.12. VCOM_ShowVideoTimestamp............................................................................24

2.7.13. VCOM_SetLocalVideoRender.............................................................................25

2.7.14. VCOM_SetRemoteVideoRender......................................................................... 25

第2页共63页

VideoCommMediaSDKForHarmony 接口开发手册

2.7.15. VCOM_SwapRender............................................................................................26

2.8.视频录制...........................................................................................................................26

2.8.1. VCOM_SetRecordPath.......................................................................................... 26

2.8.2. VCOM_SetRecordConfig...................................................................................... 27

2.8.3. VCOM_StartRecord...............................................................................................29

2.8.4. VCOM_StopRecord............................................................................................... 30

2.8.5. VCOM_SnapShot...................................................................................................30

2.9.文件传输...........................................................................................................................31

2.9.1. VCOM_SetSendFileConfig....................................................................................31

2.9.2. VCOM_SendFileControl........................................................................................32

2.9.3. VCOM_GetSendFileDetails...................................................................................32

2.10.数据通信.........................................................................................................................33

2.10.1. VCOM_SendMessage.......................................................................................... 33

2.10.2. VCOM_SendMessageByConf............................................................................. 33

2.11.智能排队.........................................................................................................................34

2.11.1. VCOM_QueueControl..........................................................................................34

2.12.视频呼叫.........................................................................................................................35

2.12.1. VCOM_VideoCallControl....................................................................................35

2.13.双录................................................................................................................................ 35

2.13.1. VCOM_MediaFileControl................................................................................... 35

2.13.2. VCOM_MediaResourceLoad...............................................................................36

2.13.3. VCOM_MediaResourceControl...........................................................................37

2.13.4. VCOM_MediaResourceUnload...........................................................................37

2.14.录屏.................................................................................................................................38

2.14.1. VCOM_SetScreenParamConfigure......................................................................38

2.14.2. VCOM_OpenLocalMediaStream.........................................................................38

2.14.3. VCOM_CloseLocalMediaStream........................................................................ 38

2.14.4. VCOM_SetLocalVideoRender.............................................................................39

2.15. AI 能力.............................................................................................................................39

2.15.1. VCOM_AIAbilityControl.................................................................................... 39

2.16. Volte 视频呼叫................................................................................................................ 39

2.16.1. VCOM_VideoCallControl....................................................................................39

3.通知事件......................................................................................................................................41

3.1.登录通知...........................................................................................................................41

3.2.连接断开通知...................................................................................................................41

3.3.服务器踢人通知...............................................................................................................42

3.4.进出会议室通知...............................................................................................................42

3.5.其他用户进出会议室通知...............................................................................................43

3.6.录像结果通知...................................................................................................................43

3.7.拍照结果通知...................................................................................................................44

3.8.文件传输状态通知...........................................................................................................45

3.9.接收消息通知...................................................................................................................46

3.10.智能排队事件通知.........................................................................................................47

3.11.视频呼叫事件通知.........................................................................................................47

第3页共63页

VideoCommMediaSDKForHarmony 接口开发手册

3.12.媒体文件控制事件通知.................................................................................................48

3.13.媒体资源事件通知.........................................................................................................48

3.14. AI 能力回调事件通知.....................................................................................................49

3.15. SDK 标准事件通知.........................................................................................................50

3.16. Volte 视频呼叫事件通知................................................................................................ 50

4.常量定义......................................................................................................................................52

4.1.会议动作定义常量...........................................................................................................52

4.2.发送文件控制常量...........................................................................................................52

4.3.媒体信息类型...................................................................................................................52

4.4.录像布局常量...................................................................................................................53

4.5.排队控制命令码...............................................................................................................53

4.6.排队回调事件类型...........................................................................................................53

4.7.视频呼叫的控制命令字...................................................................................................54

4.8.视频呼叫的事件类型.......................................................................................................54

4.9.媒体文件控制码...............................................................................................................55

4.10.媒体资源类型.................................................................................................................56

4.11.媒体资源控制指令.........................................................................................................56

4.12.媒体任务传输状态.........................................................................................................56

4.13. AI能力厂家定义............................................................................................................57

4.14. AI能力的控制码............................................................................................................57

4.15. AI能力的事件类型........................................................................................................58

4.16.队列控制的控制码.........................................................................................................58

4.17.队列控制的事件类型.....................................................................................................59

4.18.队列控制的常量定义.....................................................................................................59

4.19. Volte 视频呼叫的控制命令字........................................................................................ 60

4.20. Volte 视频呼叫的事件类型............................................................................................ 60

5.错误参考代码............................................................................................................................. 62

第4页共63页

VideoCommMediaSDKForHarmony 接口开发手册

# 1. 概述

非常感谢您使用我们的产品,我们将为您提供最好的服务。

本接口开发手册可能包含技术上不准确的地方或排版错误,本手册的内容将

做定期的更新,恕不另行通知;更新的内容将会随新版本在本接口开发手册中增

加,我们会随时改进或更新本接口开发手册中描述的接口定义和示例代码。

### 1.1.产品简介

VideoComm Media SDK 是我们核心团队成员基于多年的音视频通信领域的

技术积累,为客户提供跨终端、多平台互通、低成本、高品质、可定制的实时音

视频通信服务的开发平台,在平台中提供了音视频通信、音视频录制、文件传输、

数据通信、业务排队、屏幕共享等能力。我们的目标是让客户在无需音视频技术

基础的情况下,都可以通过本开发平台从零开始即刻搭建出自己的专属音视频通

信应用解决方案。

VideoCommMediaSDKforHarmony(以下简称:HarmonySDK)是基于

Harmony 内核提供的客户端组件,对上层应用提供纯ArkTS 语言的调用接口,

组件对应一系列的.so 库文件,定义和封装了一系列API 接口和事件,采用NAPI

技术实现ArkTS 层与内核层进行数据通信。

VideoComm Media SDK 由我们独立研发,具有自主知识产权。

### 1.2.我们的优势

我们的产品和市面上其他产品相比较,具有如下的一些优势:

### 1)全平台互通

主流终端完美适配,实时音视频支持在微信、手机QQ 通过H5 页面或

微信小程序发起/接受/断开音视频通话,也支持直接在网页或通过SDK 集成

的方式在PC、Mac 和App 中实现音视频通话。

### 2)低延迟

第5页共63页

VideoCommMediaSDKForHarmony 接口开发手册

音视频底层采用智能传输算法,有效降低实时音视频通话的延迟,提升

了在各种网络环境下的通话流畅性,抗丢包率达到业内领先水平。

### 3)网络自适应

音视频底层通过智能网络Qos 算法,自动评估和探测客户端的网络质量。

根据网络质量评估自动调节音视频传输码率、帧率、分辨率,实现在复杂网

络的通信环境下,VideoComm Media SDK 仍可保证高质量的音视频流畅通

话体验。

### 4)接口全开放、集成灵活

VideoComm Media SDK 采用模块化、微服务的技术体系架构,具有良好

的平台兼容性与可扩展性;同时全面开放了服务器端和客户端API 接口,支

持主流开发语言,提供详细的开发文档资料;并且所有的示例程序源代码都

是可供免费下载和使用的。基于开放的接口,可以根据业务应用场景的音视

频通信需求进行快速、灵活的集成。

### 5)部署架构灵活

VideoComm SDK 产品对于部署环境没有特殊要求,常用的PC 环境就可

以部署起来,方便用户自主快速部署进行验证、开发;同时支持私有化、集

群化部署;支持混合云(私有云+专有云)的网络架构部署;支持部署在互

联网的云端环境(如阿里云、腾讯云、华为云等),基于灵活的部署方式,

可以快速的实现混合云通信架构,耗带宽资源多的视频流通信可以走公有云

的方式、涉及私密和信息安全的数据在本地处理,降低整体运营成本、运维

也相对变得简单。

### 6)遵循国际安全标准

高安全性是每个行业的数据最需要优先考量的指标,VideoComm Media

SDK 采用IETF 确定的安全标准来完成端到端的数据传输,采用Https、secure

WebSocket、DTLS-SRTP 等安全协议实现信令数据、媒体流数据的传输安全。

而非开发者基于简单加密算法进行加密传输的方式来保证数据的安全,真正

第6页共63页

VideoCommMediaSDKForHarmony 接口开发手册

为用户业务数据的安全保驾护航

### 1.3.目标人群

有Harmony 开发基础的开发人员。

第7页共63页

VideoCommMediaSDKForHarmony 接口开发手册

# 2. API 定义

### 2.1.API 概览

Harmony SDK 提供的音视频通信、音视频录制、文件传输、数据通信等能力

都是基于API 接口来实现的,在应用集成开发中,只需要调用相应的API 接口

就能集成这些能力,像基本音视频通话的API 调用流程如下图所示:

第8页共63页

VideoCommMediaSDKForHarmony 接口开发手册

### 2.2.API使用指引

详细的API使用介绍请参见以下指引:

| 功能 | API 接口 | 描述 |
|---|---|---|
| SDK 事件管理 | VCOM SetSDKEvent _ | 设置SDK 事件对象 |
|  | VCOM RemoveSDKEvent _ | 移除SDK 事件对象 |
| 初始化管理 | VCOM Initialize _ | 初始化SDK 插件对象 |
|  | VCOM Release _ | 释放SDK 插件对象 |
|  | VCOM GetSDKVersion _ | 获取版本/编译信息 |
|  | VCOM SetLogLevel _ | 设置日志输出级别 |
| 用户管理 | VCOM SetUserConfig _ | 设置用户信息 |
|  | VCOM Login _ | 登录系统 |
|  | VCOM Logout _ | 注销系统 |
| 会议管理 | VCOM JoinConference _ | 加入会议 |
|  | VCOM LeaveConference _ | 退出会议 |
|  | VCOM GetConferenceUsers _ | 获取会议参会人数 |
| 音视频通信 | VCOM GetCameraDeviceCount _ | 获取摄像头设备数量 |
|  | VCOM GetCameraDeviceName _ | 获取摄像头设备名称 |
|  | VCOM GetMicrophoneDeviceCo _ unt | 获取麦克风设备数量 |
|  | VCOM GetMicrophoneDeviceNa _ me | 获取麦克风设备名称 |
|  | VCOM SetCaptureDevice _ | 设置捕获的音视频设备 |
|  | VCOM OpenLocalMediaStream _ | 打开本地视频流 |
|  | VCOM CloseLocalMediaStream _ | 关闭本地视频流 |
|  | VCOM GetRemoteMediaStream _ | 获取远端媒体流 |
|  | VCOM CloseRemoteMediaStream _ | 关闭远端媒体流 |
|  | VCOM GetVideoParamConfigure _ | 获取视频参数配置 |
|  | VCOM SetVideoParamConfigure _ | 设置视频参数配置 |

第9页共63页

VideoCommMediaSDKForHarmony 接口开发手册

|  | VCOM ShowVideoTimestamp _ | 显示/隐藏视频时间戳水印 (调用立即生效) |
|---|---|---|
|  | VCOM SetLocalVideoRender _ | 设置本地视频渲染 |
|  | VCOM SetRemoteVideoRender _ | 设置远程视频渲染 |
| 视频录制 | VCOM SetRecordPath _ | 设置录像文件地址 |
|  | VCOM SetRecordConfig _ | 设置录像参数 |
|  | VCOM StartRecord _ | 开始录像 |
|  | VCOM StopRecord _ | 停止录像 |
|  | VCOM Snapshot _ | 拍照 |
| 文件传输 | VCOM SetSendFileParam _ | 设置发送文件参数 |
|  | VCOM SendFile _ | 发送文件 |
|  | VCOM SendFile2Server _ | 发送文件至服务器 |
|  | VCOM SendFileControl _ | 发送文件控制 |
| 数据通信 | VCOM SendMessage _ | 为指定用户发送消息 |
|  | VCOM SendMessageByConf _ | 为指定会议房间发送消息(会 议内广播) |
| 智能排队 | VCOM QueueControl _ | 对排队模型进行业务逻辑控 制,包括用户进入/离开队列、 坐席示闲/示忙、坐席开始/结 束服务等逻辑控制 |
| 视频呼叫 | VCOM VideoCallControl _ | 视频呼叫控制接口 |
| Volte 视频呼叫 | VCOM VideoCallControl _ | Volte 视频呼叫控制接口 |
| 双录 | VCOM MediaFileControl _ | 对需要播报的媒体文件进行 控制 |
|  | VCOM MediaResourceLoad _ | 对媒体资源进行加载并启动 |
|  | VCOM MediaResourceControl _ | 对媒体资源进行控制 |
|  | VCOM MediaResourceUnload _ | 对媒体资源进行卸载并停止 |
| AI 能力 | VCOM AIAbilityControl _ | 实现 OCR、语音合成、语音 识别、人脸识别等能力的控制 |

第10页共63页

VideoCommMediaSDKForHarmony 接口开发手册

### 2.3.SDK 事件管理管理

### 2.3.1. VCOM_SetSDKEvent

调用此接口,添加鸿蒙SDK 事件对象。

|  |   语法示例 |  |  |  |  |
|---|---|---|---|---|---|
|  | public static VCOM SetSDKEvent(event: VComSDKEvent): void _ |  |  |  |  |
|  |   参数描述 |  |  |  |  |
| 参数 |  | 类型 | 是否必须 | 描述 |  |
| event |  | VComSDKE vent | 是 | VComSDKEvent 事件接口类对象 |  |
| return |  | void |  |  |  |

### 2.3.2.VCOM_RemoveSDKEvent

调用此接口,移除鸿蒙SDK 事件对象。

|  |   语法示例 |  |  |  |  |
|---|---|---|---|---|---|
|  | public static VCOM RemoveSDKEvent(event: VComSDKEvent): void _ |  |  |  |  |
|  |   参数描述 |  |  |  |  |
| 参数 |  | 类型 | 是否必须 | 描述 |  |
| event |  | VComSDKE vent | 是 | VComSDKEvent 事件接口类对象 |  |
| return |  | void |  |  |  |

第11页共63页

VideoCommMediaSDKForHarmony 接口开发手册

### 2.4.初始化管理

### 2.4.1. VCOM_Initialize

调用此接口,对Harmony SDK 进行初始化操作,在每个页面中只需要初始

化一次。

|  |   语法示例 |  |  |  |  |
|---|---|---|---|---|---|
|  | public static VCOM Initialize(iFlags: number, strParam: string, context?: _ Context): number |  |  |  |  |
|  |   参数描述 |  |  |  |  |
| 参数 |  | 类型 | 是否必须 | 描述 |  |
| iFlags |  | number | 否 | 初始化参数(暂保留) |  |
| strParam |  | string | 否 | 初始化参数(暂保留) |  |
| context |  | Context | 否 | uiAbilitContext 上下文参数 |  |
| return |  | number |  | 接口返回值,0:成功、非0:失败 |  |

### 2.4.2. VCOM_Release

调用此接口,释放已经注册的Harmony SDK 对象,在关闭页面时需要释放

一次。

|  |   语法示例 |  |  |  |  |
|---|---|---|---|---|---|
|  | public static VCOM Release(): number _ |  |  |  |  |
|  |   参数描述 |  |  |  |  |
| 参数 |  | 类型 | 是否必须 | 描述 |  |
| return |  | number |  | 接口返回值,0:成功、非0:失败 |  |

第12页共63页

VideoCommMediaSDKForHarmony 接口开发手册

### 2.4.3. VCOM_GetSDKVersion

调用此接口,获取当前系统环境安装的VideoComm Harmony SDK 的版本信

息、编译信息。

|  |   语法示例 |  |  |  |  |
|---|---|---|---|---|---|
|  | public static VCOM GetSDKVersion(): string _ |  |  |  |  |
|  |   参数描述 |  |  |  |  |
| 参数 |  | 类型 | 是否必须 | 描述 |  |
| return |  | string | 是 | 返回版本号+编译时间数据,json 格 式 , (eg. {"version":"V1.0.1", "build":"2015-10-22 12:04:40"}),为空 则表示失败! |  |

### 2.4.4. VCOM_SetLogLevel

调用此接口,设置Harmony SDK 的日志输出级别。

|  |   语法示例 |  |  |  |  |
|---|---|---|---|---|---|
|  | public static VCOM SetLogLevel(iLogLevel: number, iLogFlags: number): _ |  |  |  |  |
|  |   参数描述 |  |  |  |  |
| 参数 |  | 类型 | 是否必须 | 描述 |  |
| iLogLevel |  | number | 是 | 日志级别(值越低越详细) |  |
| iLogFlags |  | number | 是 | 日志标记,特别过滤标记,0 为未设 置标记 |  |

第13页共63页

VideoCommMediaSDKForHarmony 接口开发手册

| return | number |  | 接口返回值,0:成功、非0:失败 |
|---|---|---|---|

### 2.4.5. VCOM_SetSDKParamInt

调用此接口,设置Harmony SDK 参数。

|  |   语法示例 |  |  |  |  |
|---|---|---|---|---|---|
|  | public static VCOM SetSDKParamInt(iType: number, iParam: number): number _ |  |  |  |  |
|  |   参数描述 |  |  |  |  |
| 参数 |  | 类型 | 是否必须 | 描述 |  |
| iType |  | number | 是 | 参数类型 |  |
| iParam |  | number | 是 | 参数值 |  |
| return |  | number |  | 接口返回值,0:成功、非0:失败 |  |

### 2.4.6. VCOM_SetSDKParamString

调用此接口,设置Harmony SDK 参数。

###  语法示例

publicstaticVCOM_SetSDKParamString(iType:number,strParam:string):

number

|  |   参数描述 |  |  |  |  |
|---|---|---|---|---|---|
| 参数 |  | 类型 | 是否必须 | 描述 |  |
| iType |  | number | 是 | 参数类型 |  |
| strParam |  | string | 是 | 参数值 |  |
| return |  | number |  | 接口返回值,0:成功、非0:失败 |  |

第14页共63页

VideoCommMediaSDKForHarmony 接口开发手册

### 2.4.7. VCOM_SDKCommon

调用此接口,配置Harmony SDK 通用能力。

|  |   语法示例 |  |  |  |  |
|---|---|---|---|---|---|
|  | public static VCOM SDKCommon(iType: number, strParam: string): string _ |  |  |  |  |
|  |   参数描述 |  |  |  |  |
| 参数 |  | 类型 | 是否必须 | 描述 |  |
| iType |  | number | 是 | 参数类型 |  |
| strParam |  | string | 是 | 参数值 |  |
| return |  | number |  | 接口返回值,0:成功、非0:失败 |  |

### 2.5.用户管理

### 2.5.1. VCOM_SetUserConfig

调用此接口,设置登录的用户信息。

###  语法示例

publicstaticVCOM_SetUserConfig(strUserName:string,strUserCode:string,

strAppid: string, strToken: string, strParam: string): number

|  |   参数描述 |  |  |  |  |
|---|---|---|---|---|---|
| 参数 |  | 类型 | 是否必须 | 描述 |  |
| strUserName |  | string | 是 | 用户名称,最大长度100 字节 |  |
| strUserCode |  | string | 否 | 用户ID(字符串),若该字段为NULL 或者""则由服务器分配唯一用户ID, 最大长度100 字节 |  |

第15页共63页

VideoCommMediaSDKForHarmony 接口开发手册

| strAppid | string | 否 | 应用渠道ID,目前为空 |
|---|---|---|---|
| strToken | string | 否 | 鉴权token,由鉴权服务器生成 |
| strParam | string | 否 | 保留字符串 |
| return | number |  | 接口返回值,0:成功、非0:失败 |

### 2.5.2. VCOM_Login

调用此接口,将登录到系统。此接口需要在成功调VCOM_SetUserConfig 接

口之后调用。

在调用此接口后,系统会返回登录通知回调事件。

|  |   语法示例 |  |  |  |  |
|---|---|---|---|---|---|
|  | public static VCOM Login(strUrl: string, iTimeoutMS: number, strParam: string): _ number |  |  |  |  |
|  |   参数描述 |  |  |  |  |
| 参数 |  | 类型 | 是否必须 | 描述 |  |
| strUrl |  | string | 是 | 连接服务器地址,格式为『IP 或域名: 端口号』,如:"192.168.1.20:9600" |  |
| iTimeoutMS |  | number | 是 | 登录超时值,单位:毫秒,若为0 则 为异步请求 |  |
| strParam |  | string | 否 | 保留字符串 |  |
| return |  | number |  | 接口返回值,0:成功、非0:失败 |  |

### 2.5.3. VCOM_Logout

调用此接口,将退出系统。

###  语法示例

第16页共63页

| IP | 或域名: |
|---|---|

VideoCommMediaSDKForHarmony 接口开发手册

|  | public static VCOM Logout(): number _ |  |  |  |  |
|---|---|---|---|---|---|
|  |   参数描述 |  |  |  |  |
| 参数 |  | 类型 | 是否必须 | 描述 |  |
| return |  | number |  | 接口返回值,0:成功、非0:失败 |  |

### 2.6.会议管理

### 2.6.1. VCOM_JoinConference

调用此接口,将加入到指定的会议中去,在加入后,系统会返回3.4 定义的

进出会议室通知回调事件。

|  |   语法示例 |  |  |  |  |
|---|---|---|---|---|---|
|  | public static VCOM JoinConference(strConfId: string, strPassword: string, _ strParam: string): number |  |  |  |  |
|  |   参数描述 |  |  |  |  |
| 参数 |  | 类型 | 是否必须 | 描述 |  |
| strConfId |  | string | 是 | 会议ID,最大长度100 字节 |  |
| strPassword |  | string | 否 | 密码,最大长度100 字节 |  |
| strParam |  | string | 否 | 保留参数 |  |
| return |  | number |  | 接口返回值,0:成功、非0:失败 |  |

### 2.6.2. VCOM_LeaveConference

调用此接口,将退出之前加入的会议,在离开后,系统会返回3.4 定义的进

出会议室通知回调事件。

第17页共63页

VideoCommMediaSDKForHarmony 接口开发手册

###  语法示例

public static VCOM_LeaveConference(): number

|  |   参数描述 |  |  |  |  |
|---|---|---|---|---|---|
| 参数 |  | 类型 | 是否必须 | 描述 |  |
| return |  | number |  | 接口返回值,0:成功、非0:失败 |  |

### 2.6.3. VCOM_GetConferenceUsers

调用此接口,获取当前会议的参会人数。不能获取自己不在列的会议的人数。

###  语法示例

public static VCOM_GetConferenceUsers(strConfId: string): number

|  |   参数描述 |  |  |  |  |
|---|---|---|---|---|---|
| 参数 |  | 类型 | 是否必须 | 描述 |  |
| strConfId |  | string | 是 | 会议ID |  |
| return |  | number |  | 当前会议人数 |  |

### 2.7.音视频通信

### 2.7.1. VCOM_GetCameraDeviceCount

调用此接口,将获取摄像头设备的数量。

###  语法示例

第18页共63页

VideoCommMediaSDKForHarmony 接口开发手册

public static VCOM_GetCameraDeviceCount(): number

|  |   参数描述 |  |  |  |  |
|---|---|---|---|---|---|
| 参数 |  | 类型 | 是否必须 | 描述 |  |
| return |  | number |  | 摄像头设备的数量 |  |

### 2.7.2. VCOM_GetCameraDeviceName

调用此接口,将获取摄像头设备的名称,需和VCOM_GetCameraDeviceCount

接口配合使用。

###  语法示例

public static VCOM_GetCameraDeviceName(iDeviceIndex: number): string

|  |   参数描述 |  |  |  |  |
|---|---|---|---|---|---|
| 参数 |  | 类型 | 是否必须 | 描述 |  |
| iDeviceIndex |  | number | 是 | 设 备 序 号 , 从 0 到 VCOM GetCameraDeviceCount-1 _ |  |
| return |  | string |  | 返回设备名称,若为空则获取失败 |  |

### 2.7.3. VCOM_GetMicrophoneDeviceCount

调用此接口,将获取麦克风设备数量。

###  语法示例

public static VCOM_GetMicrophoneDeviceCount(): number

第19页共63页

VideoCommMediaSDKForHarmony 接口开发手册

|  |   参数描述 |  |  |  |  |
|---|---|---|---|---|---|
| 参数 |  | 类型 | 是否必须 | 描述 |  |
| return |  | number |  | 麦克风设备的数量 |  |

### 2.7.4. VCOM_GetMicrophoneDeviceName

调用此接口,将获取麦克风设备的名称,需和

VCOM_GetMicrophoneDeviceCount 接口配合使用。

###  语法示例

public static VCOM_GetMicrophoneDeviceName(iDeviceIndex: number): string

|  |   参数描述 |  |  |  |  |
|---|---|---|---|---|---|
| 参数 |  | 类型 | 是否必须 | 描述 |  |
| iDeviceIndex |  | number | 是 | 设 备 序 号 , 从 0 到 VCOM GetMicrophoneDeviceName _ -1 |  |
| return |  | string |  | 返回设备名称,若为空则获取失败 |  |

### 2.7.5. VCOM_SetCaptureDevice

调用此接口,设置可用的摄像头、麦克风设备。

|   语法示例 |  |
|---|---|
| public static VCOM SetCaptureDevice(iCameraDeviceIndex: number, _ iMicrophoneDeviceIndex: number): number |  |
|   参数描述 |  |

第20页共63页

VideoCommMediaSDKForHarmony 接口开发手册

| 参数 | 类型 | 是否必须 | 描述 |
|---|---|---|---|
| iCameraDevic eIndex | number | 是 | 设 备 序 号 , 从 0 到 VCOM GetCameraDeviceCount-1 _ |
| iMicrophoneD eviceIndex | number | 是 | 设 备 序 号 , 从 0 到 VCOM GetMicrophoneDeviceName _ -1 |
| return | number |  | 接口返回值,0:成功、非0:失败 |

### 2.7.6. VCOM_OpenLocalMediaStream

调用此接口,打开本地音视频流。

|  |   语法示例 |  |  |  |  |
|---|---|---|---|---|---|
|  | public static VCOM OpenLocalMediaStream(iChannelIndex: number, _ iEnableVideo: number, iEnableAudio: number, strParam: string): number |  |  |  |  |
|  |   参数描述 |  |  |  |  |
| 参数 |  | 类型 | 是否必须 | 描述 |  |
| iChannelIndex |  | number | 是 | 通道ID |  |
| bEnableVideo |  | number | 是 | 是否开启视频(1:开启,0:不开启) |  |
| bEnableAudio |  | number | 是 | 是否开启音频(1:开启,0:不开启) |  |
| strParam |  | string | 否 | 保留参数 |  |
| return |  | number |  | 接口返回值,0:成功、非0:失败 |  |

### 2.7.7. VCOM_CloseLocalMediaStream

调用此接口,关闭本地音视频流。

###  语法示例

第21页共63页

VideoCommMediaSDKForHarmony 接口开发手册

|  | public static VCOM CloseLocalMediaStream(iChannelIndex: number, strParam: _ string): number |  |  |  |  |
|---|---|---|---|---|---|
|  |   参数描述 |  |  |  |  |
| 参数 |  | 类型 | 是否必须 | 描述 |  |
| iChannelIndex |  | number | 是 | 通道ID |  |
| strParam |  | string | 否 | 保留参数 |  |
| return |  | number |  | 接口返回值,0:成功、非0:失败 |  |

### 2.7.8. VCOM_GetRemoteMediaStream

调用此接口,获取远端用户的媒体流。

|  |   语法示例 |  |  |  |  |
|---|---|---|---|---|---|
|  | public static VCOM GetRemoteMediaStream(strUserCode: string, iChannelIndex: _ number, iEnableVideo: number, iEnableAudio: number, strParam: string): number |  |  |  |  |
|  |   参数描述 |  |  |  |  |
| 参数 |  | 类型 | 是否必须 | 描述 |  |
| strUserCode |  | string | 是 | 用户ID(字符串) |  |
| iChannelIndex |  | number | 是 | 通道ID |  |
| bEnableVideo |  | number | 是 | 是否获取视频(1:获取,0:不获取) |  |
| bEnableAudio |  | number | 是 | 是否获取音频(1:获取,0:获取) |  |
| strParam |  | string | 否 | 保留参数 |  |
| return |  | number |  | 接口返回值,0:成功、非0:失败 |  |

### 2.7.9. VCOM_CloseRemoteMediaStream

调用此接口,关闭本地音视频流。

第22页共63页

VideoCommMediaSDKForHarmony 接口开发手册

|  |   语法示例 |  |  |  |  |
|---|---|---|---|---|---|
|  | public static VCOM CloseRemoteMediaStream(strUserCode: string, _ iChannelIndex: number, strParam: string): number |  |  |  |  |
|  |   参数描述 |  |  |  |  |
| 参数 |  | 类型 | 是否必须 | 描述 |  |
| strUserCode |  | string | 是 | 用户ID(字符串) |  |
| iChannelIndex |  | number | 是 | 通道ID |  |
| strParam |  | string | 否 | 保留参数 |  |
| return |  | number |  | 接口返回值,0:成功、非0:失败 |  |

### 2.7.10. VCOM_GetVideoParamConfigure

调用此接口,获取视频参数。

###  语法示例

public static VCOM_GetVideoParamConfigure(iChannelIndex: number): string

|  |   参数描述 |  |  |  |  |
|---|---|---|---|---|---|
| 参数 |  | 类型 | 是否必须 | 描述 |  |
| iChannelIndex |  | number | 是 | 通道ID |  |
| return |  | string |  | 返回视频参数,若为空则获取失败 |  |

### 2.7.11. VCOM_SetVideoParamConfigure

调用此接口,设置视频参数。

###  语法示例

第23页共63页

VideoCommMediaSDKForHarmony 接口开发手册

publicstaticVCOM_SetVideoParamConfigure(iChannelIndex:number,iWidth:

number,iHeight:number,iFps:number,iBitrate:number,iFlags:number):

number

|  |   参数描述 |  |  |  |  |
|---|---|---|---|---|---|
| 参数 |  | 类型 | 是否必须 | 描述 |  |
| iChannelIndex |  | number | 是 | 通道ID |  |
| iWidth |  | number | 否 | 视频宽 |  |
| iHeight |  | number | 否 | 视频宽 |  |
| iFps |  | number | 否 | 帧率 |  |
| iBitrate |  | number | 否 | 码率 |  |
| iFlags |  | number | 否 | 标记值 |  |
| return |  | number |  | 接口返回值,0:成功、非0:失败 |  |

### 2.7.12. VCOM_ShowVideoTimestamp

显示/隐藏视频时间戳水印。

|  |   语法示例 |  |  |  |  |
|---|---|---|---|---|---|
|  | public static VCOM ShowVideoTimestamp(iChannelIndex: number, iIsShow: _ number): number |  |  |  |  |
|  |   参数描述 |  |  |  |  |
| 参数 |  | 类型 | 是否必须 | 描述 |  |
| iChannelIndex |  | number | 是 | 通道ID |  |
| isShow |  | number | 是 | 显示标志(1:显示,0:隐藏) |  |
| return |  | number |  | 接口返回值,0:成功、非0:失败 |  |

第24页共63页

VideoCommMediaSDKForHarmony 接口开发手册

### 2.7.13. VCOM_SetLocalVideoRender

设置本地视频渲染

###  语法示例

publicstaticVCOM_SetLocalVideoRender(strUserCode:string,iChannelIndex:

number, strXComponentId: string, strParam: string): number

|  |   参数描述 |  |  |  |  |
|---|---|---|---|---|---|
| 参数 |  | 类型 | 是否必须 | 描述 |  |
| strUserCode |  | string | 是 | 用户ID |  |
| iChannelIndex |  | number | 是 | 通道ID |  |
| strXCompone ntId |  | string | 是 | XComponent 组件id 值 |  |
| strParam |  | string | 是 | 保留参数 |  |
| return |  | number |  | 接口返回值,0:成功、非0:失败 |  |

### 2.7.14. VCOM_SetRemoteVideoRender

设置远程视频渲染

|  |   语法示例 |  |  |  |  |
|---|---|---|---|---|---|
|  | public static VCOM SetRemoteVideoRender(strUserCode: string, iChannelIndex: _ number, strXComponentId: string, strParam: string): number |  |  |  |  |
|  |   参数描述 |  |  |  |  |
| 参数 |  | 类型 | 是否必须 | 描述 |  |
| strUserCode |  | string | 是 | 用户ID |  |
| iChannelIndex |  | number | 是 | 通道ID |  |
| strXCompone |  | string | 是 | XComponent 组件id 值 |  |

第25页共63页

VideoCommMediaSDKForHarmony 接口开发手册

| ntId |  |  |  |
|---|---|---|---|
| strParam | string | 是 | 保留参数 |
| return | number |  | 接口返回值,0:成功、非0:失败 |

### 2.7.15. VCOM_SwapRender

交换两路流的渲染器。

|  | public static VCOM SwapRender(strFirstUserCode: string, iFirstChannelIndex: _ number, strSecondUserCode: string, iSecondChannelIndex: number): number |  |  |  |  |
|---|---|---|---|---|---|
|  |   参数描述 |  |  |  |  |
| 参数 |  | 类型 | 是否 必须 | 描述 |  |
| strFirstUserCode |  | string | 是 | 第一个用户ID |  |
| iFirstChannelIndex |  | number | 是 | 第一个通道ID |  |
| strSenondUserCode |  | string | 是 | 第二个用户ID |  |
| iSenondChannelIndex |  | number | 是 | 第二个通道ID |  |
| return |  | number |  | 接口返回值,0:成功、非0:失败 |  |

### 2.8.视频录制

### 2.8.1. VCOM_SetRecordPath

调用此接口,设置录像地址。

|  |   语法示例 |  |  |  |  |
|---|---|---|---|---|---|
|  | public static VCOM SetRecordPath(strFilePath: string): number _ |  |  |  |  |
|  |   参数描述 |  |  |  |  |
| 参数 |  | 类型 | 是否必须 | 描述 |  |

第26页共63页

VideoCommMediaSDKForHarmony 接口开发手册

| strFilePath | string | 是 | 录像参数,见下方的:录像参数说明 |
|---|---|---|---|
| return | number |  | 接口返回值,0:成功、非0:失败 |

### 2.8.2. VCOM_SetRecordConfig

调用此接口,设置录像参数。

|  |   语法示例 |  |  |  |  |
|---|---|---|---|---|---|
|  | public static VCOM SetRecordConfig(strRecordParam: string, strBusinessParam: _ string): number |  |  |  |  |
|  |   参数描述 |  |  |  |  |
| 参数 |  | 类型 | 是否必须 | 描述 |  |
| strRecordPara m |  | string | 是 | 录像参数,见下方的:录像参数说明 |  |
| strBusinessPar am |  | string | 是 | 自定义的json 格式的业务参数 |  |
| return |  | string |  | 返 回 json 格 式 字 符 串 e.g: {errorcode:0, recordid:1} |  |

###  录像参数说明

第27页共63页

VideoCommMediaSDKForHarmony 接口开发手册

录像参数,json格式字符串说明:

{

"mode":"two-1",

///<必选,录像画面布局样式,参考《录像布局说明》

"format":"mp4",

///<可选,录像格式,默认为mp4

"video":"true",

///<可选,录像是否包含视频,默认为true

"audio":"true",

///<可选,录像是否包含音频,默认为true

"width":640,

///<可选,录像的分辨率宽度,默认为SDK 根据布局自适应

"height":240,

///<可选,录像的分辨率高度,默认为SDK 根据布局自适应

"bitrate":0,

///<可选,单位是kpbs,默认为底层自适应

"filename":"VCOM_record",///<可选,录像的文件名,若为空则默认由SDK 自动生成文件名

"serverrecord":"false",

///<可选,true 为服务器录像,false 为本地录像;默认为false

"rewrite": "true",

///<可选,默认为false

"overlaytext":

///<可选,叠加文字水印参数,若为空则不叠加文字水印

{

"text":"VCOM_Good_20151225[timestamp]",

///<若添加了文字水印,则必选参数。

[timestamp]为时间戳

"x":10,

///<若添加了文字水印,则必选参数。叠加

水印的x 轴坐标位置,范围: 0 < x < width

"y":10,

///<若添加了文字水印,则必选参数。叠加

水印的y 轴坐标位置,范围: 0 < y < heght

"rgb":"0xff0000",

///<可选,字体颜色,默认为黑色

"size":18

///<可选,字体大小,默认由SDK 自适应

},

"layout":[

///<必选,录像画面布局参数,布局样式参考《录像布局

说明》

{

"index":1,

///<必选,图像序号,参考《录像布局说明》

"usercode":"user_test",

///<必选,图像的用户编码

"channelindex":0

///<必选,图像的用户流通道号

},

{

"index":2,

"usercode":"user_agent",

"channelindex":0

}

]

}

###  录像布局说明

// 0. one:单画面

第28页共63页

VideoCommMediaSDKForHarmony 接口开发手册

// 3. two-3:双画面-上下模式(序号

为1、2)

### 1

### 1

// 1. two-1:双画面-左右并列模式(序号

为1、2)

### 2

| 1 | 2 |
|---|---|

// 4. three-1:三画面画面-画中画模

式(序号为1、2、3)(2、3 是画

中画)

// 2. two-2:双画面-画中画模式(序号为

1、2)

| 1 | 2 |  |
|---|---|---|
|  |  | 3 |

| 1 |  |
|---|---|
|  | 2 |

|

### 2.8.3. VCOM_StartRecord

调用此接口,开始录像。此接口需要在成功调用VCOM_SetRecordConfig 接

口之后调用。

###  语法示例

public static VCOM_StartRecord(iRecordId: number): number

第29页共63页

VideoCommMediaSDKForHarmony 接口开发手册

|  |   参数描述 |  |  |  |  |
|---|---|---|---|---|---|
| 参数 |  | 类型 | 是否必须 | 描述 |  |
| iRecordId |  | number | 是 | 录 像 句 柄 ID , 在 成 功 调 用 VCOM SetRecordConfig 后 返 回 的 _ recordid 值 |  |
| return |  | number |  | 接口返回值,0:成功、非0:失败 |  |

### 2.8.4. VCOM_StopRecord

调用此接口,停止录像。此接口需要在成功调用VCOM_StartRecord 接口之

后调用。

###  语法示例

public static VCOM_StopRecord(iRecordId: number): number

|  |   参数描述 |  |  |  |  |
|---|---|---|---|---|---|
| 参数 |  | 类型 | 是否必须 | 描述 |  |
| iRecordId |  | number | 是 | 录 像 句 柄 ID , 在 成 功 调 用 VCOM SetRecordConfig 后 返 回 的 _ recordid 值 |  |
| return |  | number |  | 接口返回值,0:成功、非0:失败 |  |

### 2.8.5. VCOM_SnapShot

调用此接口,进行拍照。

###  语法示例

第30页共63页

VideoCommMediaSDKForHarmony 接口开发手册

|  | public static VCOM Snapshot(strUserCode: string, iChannelIndex: number, _ iServer: number, strBusinessParam: string, strFileName: string, strExtParam: string): number |  |  |  |  |
|---|---|---|---|---|---|
|  |   参数描述 |  |  |  |  |
| 参数 |  | 类型 | 是否必须 | 描述 |  |
| strUserCode |  | string | 是 | 用户ID(字符串) |  |
| iChannelIndex |  | number | 是 | 通道ID |  |
| bServer |  | boolean | 是 | 是否上传服务器 |  |
| strBusinessPar am |  | number | 是 | 业务参数 |  |
| strFileName |  | string | 是 | 拍照生成的文件名称 |  |
| strExtParam |  | string | 否 | 保留参数 |  |
| return |  | number |  | 接口返回值,0:成功、非0:失败 |  |

### 2.9.文件传输

### 2.9.1. VCOM_SetSendFileConfig

调用此接口,设置发送文件的参数。

###  语法示例

publicstaticVCOM_SetSendFileConfig(strFilePath:string,strExtParam:string,

strBusinessParam: string): number

|  |   参数描述 |  |  |  |  |
|---|---|---|---|---|---|
| 参数 |  | 类型 | 是否必须 | 描述 |  |
| strFilePath |  | string | 是 | 发送文件的绝对路径 |  |
| strExtParam |  | string | 是 | 发送文件其他参数设置 |  |

第31页共63页

VideoCommMediaSDKForHarmony 接口开发手册

| strBusinessParam | string | 是 | 发送文件的业务随路参数 |
|---|---|---|---|
| return | number |  | 接口返回值,0:成功、非0:失败 |

### 2.9.2. VCOM_SendFileControl

调用此接口,对发送文件的过程进行相应的控制。此接口需要在成功调用

VCOM_SetSendFileConfig 接口之后调用。

|  |   语法示例 |  |  |  |  |
|---|---|---|---|---|---|
|  | public static VCOM SendFileControl(iFileId: number, iCtrlCode: number, _ iParam: number, strStrParam: string): number |  |  |  |  |
|  |   参数描述 |  |  |  |  |
| 参数 |  | 类型 | 是否必须 | 描述 |  |
| iFileld |  | number | 是 | 发 送 文 件 句 柄 ( 由 VCOM SetSendFileConfig 返回的句柄) _ |  |
| iCtrlCode |  | number | 是 | 控制指令,可参考[ 4.2 发送文件控制 常量 ]章节说明 |  |
| iParam |  | number | 是 | 整形指令数据 |  |
| strStrParam |  | string | 是 | 字符串指令数据 |  |
| return |  | number |  | 接口返回值,0:成功、非0:失败 |  |

### 2.9.3. VCOM_GetSendFileDetails

调用此接口,获取发送文件的详情信息。

###  语法示例

public static VCOM_GetSendFileDetails(iFileId: number, iCode: number): string

第32页共63页

VideoCommMediaSDKForHarmony 接口开发手册

|  |   参数描述 |  |  |  |  |
|---|---|---|---|---|---|
| 参数 |  | 类型 | 是否必须 | 描述 |  |
| iFileId |  | number | 是 | 返回发送文件句柄 |  |
| iCode |  | number | 是 | 指令码,可参考[ 4.2 发送文件控制常 量 ]掌节说明 |  |
| return |  | String |  | 获取详细信息 |  |

### 2.10.数据通信

### 2.10.1. VCOM_SendMessage

调用此接口,给指定用户发送消息。

###  语法示例

public

static

VCOM_SendMessage(strUserCode:

string,

iMsgType:

number,

strMessage: string): number

|  |   参数描述 |  |  |  |  |
|---|---|---|---|---|---|
| 参数 |  | 类型 | 是否必须 | 描述 |  |
| strUserCode |  | string | 是 | 用户ID(字符串) |  |
| iMsgType |  | number | 是 | 消息类型 |  |
| strMessage |  | string | 是 | 消息内容 |  |
| return |  | number |  | 接口返回值,0:成功、非0:失败 |  |

### 2.10.2. VCOM_SendMessageByConf

调用此接口,为会议房间内的全休用户发送消息(会议内广播)。

第33页共63页

VideoCommMediaSDKForHarmony 接口开发手册

|  |   语法示例 |  |  |  |  |
|---|---|---|---|---|---|
|  | public static VCOM SendMessageByConf(strConfId: string, iMsgType: number, _ strMessage: string): number |  |  |  |  |
|  |   参数描述 |  |  |  |  |
| 参数 |  | 类型 | 是否必须 | 描述 |  |
| strConfId |  | string | 是 | 会议ID |  |
| iMsgType |  | number | 是 | 消息类型 |  |
| strMessage |  | string | 是 | 消息内容 |  |
| return |  | number |  | 接口返回值,0:成功、非0:失败 |  |

### 2.11.智能排队

### 2.11.1. VCOM_QueueControl

调用此接口,对排队模型进行业务逻辑控制,包括用户进入/离开队列等逻辑

控制。

###  语法示例

public static VCOM_QueueControl(iCtrlCode: number, strCtrlValue: string): string

|  |   参数描述 |  |  |  |  |
|---|---|---|---|---|---|
| 参数 |  | 类型 | 是否必须 | 描述 |  |
| iCtrlCode |  | number | 是 | 控制指令,参考[ 4.17 队列控制的控 制码 ] |  |
| strCtrlValue |  | string | 是 | 控制数据(Json 结构数据) |  |
| return |  | string |  | 返回Json 格式字符串控制详细信息, 根据控制码不同而有差异 |  |

第34页共63页

VideoCommMediaSDKForHarmony 接口开发手册

### 2.12.视频呼叫

### 2.12.1. VCOM_VideoCallControl

调用此接口,对视频呼叫的模型进行业务逻辑控制,包括呼叫、应答、拒绝等。

|  |   语法示例 |  |  |  |  |
|---|---|---|---|---|---|
|  | public static VCOM VideoCallControl(iCtrlCode: number, strCtrlValue: string): string _ |  |  |  |  |
|  |   参数描述 |  |  |  |  |
| 参数 |  | 类型 | 是否必须 | 描述 |  |
| iCtrlCode |  | number | 是 | 控制指令,参考[ 4.7 视频呼叫控制 码 ] |  |
| strCtrlValue |  | string | 是 | 控制数据(Json 结构数据) |  |
| return |  | string |  | 返回Json 格式字符串控制详细信息, 根据控制码不同而有差异 |  |

### 2.13.双录

### 2.13.1. VCOM_MediaFileControl

调用此接口,对风险揭示的各类媒体文件(如:MP3、MP4、PPT等)进行

播放控制和AI 双录中TTS 文字播报功能。

|   语法示例 |  |
|---|---|
| public static VCOM MediaFileControl(iCmdCode: number, iMediaId: number, strCmdParam: _ string): string |  |
|   参数描述 |  |

第35页共63页

VideoCommMediaSDKForHarmony 接口开发手册

| 参数 | 类型 | 是否必须 | 描述 |
|---|---|---|---|
| iCmdCode | number | 是 | 控制指令,详见[ 4.9 媒体文件控制 码 ]章节说明 |
| iMediaId | number | 是 | 媒体文件id |
| strCmdParam | string | 是 | json 格式字符串控制参数,根据控制 码不同而有差异 |
| return | string |  | json 格式字符串返回值,根据控制码 不同而有差异,其中 errorcode 为 0 表示成功,非0 表示失败 |

### 2.13.2. VCOM_MediaResourceLoad

调用此接口,实现对风险揭示资源文件的下载。该接口为资源下载的预加载

功能。

|  |   语法示例 |  |  |  |  |
|---|---|---|---|---|---|
|  | public static VCOM MediaResourceLoad(strResourceGuid: string, iResourceType: number, _ strUrl: string, strBusinessParam: string, iParam: number, strParam: string): number |  |  |  |  |
|  |   参数描述 |  |  |  |  |
| 参数 |  | 类型 | 是否必须 | 描述 |  |
| strResourceGuid |  | string | 是 | 资源guid,业务层生成 |  |
| iResourceType |  | number | 是 | 资源类型,详见[ 4.10 媒体资源类型 ] 章节说明 |  |
| strUrl |  | string | 是 | 资源url |  |
| strBusinessPara m |  | string | 否 | 业务数据,执行完毕回调出来 |  |
| iParam |  | number | 否 | 保留参数,传0 |  |
| strParam |  | string | 否 | 保留参数,传空字符串 |  |
| return |  | number |  | 接口返回值,0:成功、非0:失败 |  |

第36页共63页

VideoCommMediaSDKForHarmony 接口开发手册

### 2.13.3. VCOM_MediaResourceControl

调用此接口,实现对风险揭示资源文件的下载。该接口为资源下载的控制功

能,包括开始下载、暂停、结束等控制操作。

|  |   语法示例 |  |  |  |  |
|---|---|---|---|---|---|
|  | public static VCOM MediaResourceControl(strResourceGuid: string, iCmdCode: number, iType: _ number, strInBuf: string): string |  |  |  |  |
|  |   参数描述 |  |  |  |  |
| 参数 |  | 类型 | 是否必须 | 描述 |  |
| strResourceGuid |  | string | 是 | 资源Guid |  |
| iCmdCode |  | number | 是 | 资源控制指令,详见[ 4.11 媒体资源 控制指令 ]章节说明 |  |
| iType |  | number | 是 | 控制指令执行类型,像查询指令,会 包含状态查询,进度查询,详细文件 信息查询等 |  |
| strInBuf |  | string | 否 | 输入参数buf |  |
| return |  | string |  | 根据控制码不同而有差异 |  |

### 2.13.4. VCOM_MediaResourceUnload

调用此接口,对媒体资源进行卸载并停止。

|  |   语法示例 |  |  |  |  |
|---|---|---|---|---|---|
|  | public static VCOM MediaResourceUnload(strResourceGuid: string, strParam: string): number _ |  |  |  |  |
|  |   参数描述 |  |  |  |  |
| 参数 |  | 类型 | 是否必须 | 描述 |  |

第37页共63页

VideoCommMediaSDKForHarmony 接口开发手册

| strResourceGuid | string | 是 | 资源Guid |
|---|---|---|---|
| strParam | string | 否 | 输入参数buf |
| return | number |  | 接口返回值,0:成功、非0:失败 |

### 2.14.录屏

### 2.14.1. VCOM_SetScreenParamConfigure

调用此接口,设置录屏参数。

###  语法示例

public static VCOM_SetScreenParamConfigure(iChannelIndex: number, iWidth: number, iHeight:

number, iFps: number, iBitrate: number, strParam: string): number

|  |   参数描述 |  |  |  |  |
|---|---|---|---|---|---|
| 参数 |  | 类型 | 是否必须 | 描述 |  |
| iChannelIndex |  | number | 是 | 媒体流号 |  |
| iWidth |  | number | 否 | 录屏宽 |  |
| iHeight |  | number | 否 | 录屏高 |  |
| iFps |  | number | 否 | 帧率 |  |
| iBitrate |  | number | 否 | 码率 |  |
| strParam |  | string | 是 | 保留参数 |  |
| return |  | number |  | 接口返回值,0:成功、非0:失败 |  |

### 2.14.2. VCOM_OpenLocalMediaStream

请参考[2.7.6媒体打开接口]章节说明。

### 2.14.3. VCOM_CloseLocalMediaStream

请参考[2.7.7媒体关闭接口]章节说明。

第38页共63页

VideoCommMediaSDKForHarmony 接口开发手册

### 2.14.4. VCOM_SetLocalVideoRender

请参考[2.7.13本地流渲染器设置]章节说明。

### 2.15.AI 能力

### 2.15.1. VCOM_AIAbilityControl

调用此接口,实现OCR、语音合成、语音识别、人脸识别等AI 能力进行控

制。

|  |   语法示例 |  |  |  |  |
|---|---|---|---|---|---|
|  | public static VCOM AIAbilityControl(iCtrlCode: number, strCtrlValue: string): string _ |  |  |  |  |
|  |   参数描述 |  |  |  |  |
| 参数 |  | 类型 | 是否必须 | 描述 |  |
| iCtrlCode |  | number | 是 | 控制码,详见[ 4.13 AI 能力的控制 码 ]章节说明 |  |
| StrCtrlValue |  | string | 是 | Json 格式字符串控制参数 |  |
| return |  | string |  | 返回Json 格式字符串控制详细信息, 根据控制码不同而有差异 |  |

### 2.16.Volte 视频呼叫

### 2.16.1. VCOM_VideoCallControl

调用此接口,对Volte 视频呼叫的模型进行业务逻辑控制,包括呼叫、应答、拒绝等。

###  语法示例

public static VCOM_VideoCallControl(iCtrlCode: number, strCtrlValue: string): string

###  参数描述

第39页共63页

VideoCommMediaSDKForHarmony 接口开发手册

| 参数 | 类型 | 是否必须 | 描述 |
|---|---|---|---|
| iCtrlCode | number | 是 | 控制指令,参考[ 4.19 Volte 视频呼叫 控制码 ] |
| strCtrlValue | string | 是 | 控制数据(Json 结构数据) |
| return | string |  | 返回Json 格式字符串控制详细信息, 根据控制码不同而有差异 |

第40页共63页

VideoCommMediaSDKForHarmony 接口开发手册

# 3. 通知事件

### 3.1.登录通知

用户在调用登录接口后系统会触发登录通知事件,需要由开发人员定义名称

为:onLoginSystem 的委托函数进行响应。

|  |   语法示例 |  |  |  |  |
|---|---|---|---|---|---|
|  | public OnLoginSystem(strUserCode: string, iErrorCode: number, iReConnect: number): void; |  |  |  |  |
|  |   参数描述 |  |  |  |  |
| 参数 |  | 类型 | 是否必须 | 描述 |  |
| strUserCode |  | string | 是 | 系统返回的userCode |  |
| iErrorCode |  | number | 是 | 系统返回的代码,0 表示成功,非 0 表示失败,可参考[ 5 错误参考代码 ] 章节说明 |  |
| iReConnect |  | number | 是 | 重连次数 |  |

### 3.2.连接断开通知

在插件运行过程中,因为外在原因、网络原因导致客户端和服务器的通信中

断时系统会触发连接断开通知事件,需要由开发人员定义名称为:onDisConnect

的委托函数进行响应。

|  |   语法示例 |  |  |  |  |
|---|---|---|---|---|---|
|  | public OnDisconnect(iErrorCode: number): void; |  |  |  |  |
|  |   参数描述 |  |  |  |  |
| 参数 |  | 类型 | 是否必须 | 描述 |  |

第41页共63页

VideoCommMediaSDKForHarmony 接口开发手册

| iErrorCode | number | 是 | 系统返回的代码,0 表示成功,非 0 表示失败,可参考[ 5 错误参考代码 ] 章节说明 |
|---|---|---|---|

### 3.3.服务器踢人通知

有些业务场景,需要服务器将某个登录的用户踢在系统,在执行后客户端会

收到系统会触发服务器踢人通知事件,需要由开发人员定义名称为:

onServerKickout 的委托函数进行响应。

|  |   语法示例 |  |  |  |  |
|---|---|---|---|---|---|
|  | public OnServerKickout(iErrorCode: number): void; |  |  |  |  |
|  |   参数描述 |  |  |  |  |
| 参数 |  | 类型 | 是否必须 | 描述 |  |
| iErrorCode |  | number | 是 | 系统返回的代码,0 表示成功,非 0 表示失败,可参考[ 5 错误参考代码 ] 章节说明 |  |

### 3.4.进出会议室通知

在调用JoinConference、LeaveConference 接口后,会收到服务器返回的进出

会议室的结果通知事件,需要由开发人员定义名称为:onConferenceResult 的委

托函数进行响应。

###  语法示例

public OnConferenceResult(iAction: number, strConfId: string, iErrorCode: number): void;

###  参数描述

第42页共63页

VideoCommMediaSDKForHarmony 接口开发手册

| 参数 | 类型 | 是否必须 | 描述 |
|---|---|---|---|
| iAction | number | 是 | 返回会议动作定义常量定义的值,详 见[ 4.1 进入会议动作类型 ]章节说明 |
| strConfId | string | 是 | 当前会议的会议Id |
| iErrorCode | number | 是 | 系统返回的代码,0 表示成功,非 0 表示失败,可参考[ 5 错误参考代码 ] 章节说明 |

### 3.5.其他用户进出会议室通知

在某个用户调用JoinConference、LeaveConference 接口进入某个会议室后,

在会议室内除此用户之外的其他用户会收到服务器返回的该用户进出会议室的

结果通知事件,需要由开发人员定义名称为:onConferenceUser 的委托函数进行

响应。

|  |   语法示例 |  |  |  |  |
|---|---|---|---|---|---|
|  | public OnConferenceUser(strUserCode: string, iAction: number, strConfId: string): void; |  |  |  |  |
|  |   参数描述 |  |  |  |  |
| 参数 |  | 类型 | 是否必须 | 描述 |  |
| strUserCode |  | string | 是 | 进出会议室的用户ID |  |
| iAction |  | number | 是 | 返回会议动作定义常量定义的值, 见:[ 4.1 进入会议动作类型 ] |  |
| strConfId |  | string | 是 | 当前会议的会议Id |  |

### 3.6.录像结果通知

在调用VCOM_StopRecord 接口后,会收到Harmony SDK 返回的录像结果通

第43页共63页

VideoCommMediaSDKForHarmony 接口开发手册

知事件,需要由开发人员定义名称为:onRecordResult 的委托函数进行响应。

###  语法示例

public

OnRecordResult(strUserCode:

string,

iRecordId:

number,

iErrorCode:

number,

strFileName:

string,

iFileLength:

number,

iDuration:

number,

strMD5:

string,

strBusinessParam: string): void;

|  |   参数描述 |  |  |  |  |
|---|---|---|---|---|---|
| 参数 |  | 类型 | 是否必须 | 描述 |  |
| strUserCode |  | string | 是 | 进出会议室的用户ID |  |
| iRecordId |  | number | 是 | 录像接口传入的录像句柄Id |  |
| iErrorCode |  | number | 是 | 系统返回的代码,0 表示成功,非 0 表示失败,可参考[ 5 错误参考代码 ] 章节说明 |  |
| strFileName |  | string | 是 | 录像生成的文件名,包括文件存放的 绝对路径 |  |
| iFileLength |  | number | 是 | 文件大小 |  |
| iDuration |  | number | 是 | 录像时长 |  |
| strMD5 |  | string | 是 | 文件的MD 校验值 |  |
| strBusinessPar am |  | string | 否 | 调用录像开始接口时传入的业务参 数 |  |

### 3.7.拍照结果通知

在调用VCOM_SnapShot 接口后,会收到Harmony SDK 返回的拍照结果通

知事件,需要由开发人员定义名称为:onSnapShotResult 的委托函数进行响应。

###  语法示例

第44页共63页

VideoCommMediaSDKForHarmony 接口开发手册

publicOnSnapShotResult(strUserCode:string,iChannelIndex:number,iErrorCode:number,

strFileName: string, strBusinessParam: string, strExtParam: string): void;

|  |   参数描述 |  |  |  |  |
|---|---|---|---|---|---|
| 参数 |  | 类型 | 是否必须 | 描述 |  |
| strUserCode |  | string | 是 | 进出会议室的用户ID |  |
| iChannelIndex |  | number | 是 | 通道ID |  |
| iErrorCode |  | number | 是 | 系统返回的代码,0 表示成功,非 0 表示失败,可参考[ 5 错误参考代码 ] 章节说明 |  |
| strFileName |  | string | 是 | 拍照生成的文件名称,包括文件存放 的绝对路径 |  |
| strbusinessPar am |  | number | 是 | 拍照接口传入的业务参数 |  |
| strExtParam |  | string | 否 | 保留参数 |  |

### 3.8.文件传输状态通知

在调用VCOM_SendFile、VCOM_SendFile2Server 接口后,会收到Harmony

SDK 返回的文件传输状态事件,需要由开发人员定义名称为:onSendFileStatus

的委托函数进行响应。

###  语法示例

public

OnSendFileStatus(iFileId:

number,

iErrorCode:

number,

iProgress:

number,

strFileName: string, iFileLength: number, iFlags: number, strBusinessParam: string): void;

|  |   参数描述 |  |  |  |  |
|---|---|---|---|---|---|
| 参数 |  | 类型 | 是否必须 | 描述 |  |

第45页共63页

VideoCommMediaSDKForHarmony 接口开发手册

| iHandle | number | 是 | 文件发送句柄,在调用文件传输接口 时返回的文件发送句柄参数 |
|---|---|---|---|
| iErrorCode | number | 是 | 系统返回的代码,0 表示成功,非 0 表示失败,可参考[ 5 错误参考代码 ] 章节说明 |
| iProgress | number | 是 | 传输进度,值为百分比的数值,如: 0、99、100 |
| strFileName | string | 是 | 传输文件名称 |
| strFileLength | number | 是 | 传输文件的大小 |
| iFlags | number | 是 | 标记值 |
| strParam | string | 否 | 上层自定义的参数,在传输接口时传 输的 |

### 3.9.接收消息通知

在某个用户调用VCOM_SendMessage、VCOM_SendMessageByConf 接口后,

指定的用户或会议室内的其他用户会收到Harmony SDK 返回的接收消息通知事

件,需要由开发人员定义名称为:onReceiveMessage 的委托函数进行响应。

###  语法示例

public OnReceiveMessage(strUserCode: string, iMsgType: number, strMessage: string): void;

|  |   参数描述 |  |  |  |  |
|---|---|---|---|---|---|
| 参数 |  | 类型 | 是否必须 | 描述 |  |
| strUserCode |  | string | 是 | 发送消息的用户ID |  |
| iMsgType |  | number | 是 | 消息类型 |  |
| strMessage |  | string | 是 | 消息内容 |  |

第46页共63页

VideoCommMediaSDKForHarmony 接口开发手册

### 3.10.智能排队事件通知

用户调用VCOM_QueueControl 等接口进行排队业务逻辑时,会触发这个事

件通知。需要由开发人员定义名称为:OnQueueEvent 的委托函数进行响应。

|  |   语法示例 |  |  |  |  |
|---|---|---|---|---|---|
|  | public OnQueueEvent(iEventType: number, iErrorCode: number, strEventValue: string): void; |  |  |  |  |
|  |   参数描述 |  |  |  |  |
| 参数 |  | 类型 | 是否必须 | 描述 |  |
| iEventType |  | number | 是 | 排队事件,参考「4.18 队列控制的事 件类型」 |  |
| iErrorCode |  | number | 是 | 错误码,参考[ 5 错误参考代码 ] |  |
| strEventValue |  | string | 是 | 事件数据(Json) |  |

### 3.11.视频呼叫事件通知

当客户端调用VCOM_VideoCallControl 等接口进行视频呼叫逻辑控制时,会

触发此回调。

###  语法示例

publicOnVideoCallEvent(iEventType:number,iErrorCode:number,strEventValue:string):

void;

|  |   参数描述 |  |  |  |  |
|---|---|---|---|---|---|
| 参数 |  | 类型 | 是否必须 | 描述 |  |
| iEventType |  | number | 是 | 呼叫事件,参考「4.8 视频呼叫控制 事件类型」 |  |
| iErrorCode |  | number | 是 | 错误码,参考[ 5 错误参考代码 ] |  |

第47页共63页

VideoCommMediaSDKForHarmony 接口开发手册

| strEventValue | string | 是 | 事件数据(Json) |
|---|---|---|---|

### 3.12.媒体文件控制事件通知

### 在调用VCOM_MediaFileControl 接口对媒体文件进行控制时,会触发这

个事件通知。需要由开发人员定义名称为:OnMediaFileControlEvent 的委托函数

进行响应。

|  |   语法示例 |  |  |  |  |
|---|---|---|---|---|---|
|  | public OnMediaFileControlEvent(iMediaFileId: number, iEventType: number, iErrorCode: number, strParam: string): void; |  |  |  |  |
|  |   参数描述 |  |  |  |  |
| 参数 |  | 类型 | 是否必须 | 描述 |  |
| iMediaFileId |  | number | 是 | 媒体文件id |  |
| iEventType |  | string | 是 | 事件类型 |  |
| iErrorCode |  | number | 是 | 返回的数值参数 |  |
| strParam |  | string | 是 | 返回的字符串参数 |  |

### 3.13.媒体资源事件通知

### 在调用VCOM_MediaResourceLoad、

### VCOM_MediaResourceControl、VCOM_MediaResourceUnload 接口媒

体资源进行加载、控制、卸载时会触发这个事件通知。需要由开发人员定义名称

为:OnMediaResourceResult 的委托函数进行响应。

|   语法示例 |  |
|---|---|
| public OnMediaResourceResult(strResourceGuid: string, iErrorCode: number, iResourceType: number, strBusinessParam: string, strMd5: string, strParam: string): void; |  |

第48页共63页

VideoCommMediaSDKForHarmony 接口开发手册

|  |   参数描述 |  |  |  |  |
|---|---|---|---|---|---|
| 参数 |  | 类型 | 是否必须 | 描述 |  |
| strResourceGuid |  | string | 是 | 资源guid |  |
| iErrorCode |  | number | 是 | 标准错误码,0->成功、非0->失败 |  |
| iResourceType |  | number | 是 | 资源类型 |  |
| strBusinessParam |  | string | 是 | 业务数据 |  |
| strMd5 |  | string | 是 | 下载资源文件MD5 值 |  |
| strParam |  | string | 是 | json 格式的执行结果返回值,不同的 资源类型返回的结果值有差异 |  |

### 3.14.AI 能力回调事件通知

### 在调用VCOM_AIAbilityControl 接口实现OCR、语音合成、语音识别、

人脸识别等能力进行控制时会触发这个事件通知。需要由开发人员定义名称为:

OnAIAbilityEvent 的委托函数进行响应。

|  |   语法示例 |  |  |  |  |
|---|---|---|---|---|---|
|  | public OnAIAbilityEvent(iEventType: number, iErrorCode: number, strEventValue: string): |  |  |  |  |
|  |   参数描述 |  |  |  |  |
| 参数 |  | 类型 | 是否必须 | 描述 |  |
| iEventType |  | number | 是 | 控制类型,参考[4.15 AI 能力回调事 件类型] |  |
| iErrorCode |  | number | 是 | 错误码,参考[ 5 错误参考代码 ] |  |
| strEventValue |  | string | 是 | 结果数据返回缓存buf |  |

第49页共63页

VideoCommMediaSDKForHarmony 接口开发手册

### 3.15.SDK 标准事件通知

### 在调用VCOM_SDKCommon 等接口时,会触发这个事件通知。需要由开

发人员定义名称为:OnSDKCommEvent 的委托函数进行响应。

|  |   语法示例 |  |  |  |  |
|---|---|---|---|---|---|
|  | public OnSDKCommEvent(iEventType: number, iParam1: number, iParam2: number, strEventValue: string): void; |  |  |  |  |
|  |   参数描述 |  |  |  |  |
| 参数 |  | 类型 | 是否必须 | 描述 |  |
| iEventType |  | number | 是 | 事件类型 |  |
| iParam1 |  | string | 是 | 参数1 |  |
| iParam2 |  | number | 是 | 参数2 |  |
| strEventStrParam |  | string | 是 | 返回的字符串参数 |  |

### 3.16.Volte 视频呼叫事件通知

当客户端调用VCOM_VideoCallControl 等接口进行Volte 视频呼叫逻辑控制

时,会触发此回调。

|  |   语法示例 |  |  |  |  |
|---|---|---|---|---|---|
|  | public OnVideoCallEvent(iEventType: number, iErrorCode: number, strEventValue: string): void; |  |  |  |  |
|  |   参数描述 |  |  |  |  |
| 参数 |  | 类型 | 是否必须 | 描述 |  |
| iEventType |  | number | 是 | 呼叫事件,参考「4.20 Volte 视频呼叫 控制事件类型」 |  |

第50页共63页

VideoCommMediaSDKForHarmony 接口开发手册

| iErrorCode | number | 是 | 错误码,参考[ 5 错误参考代码 ] |
|---|---|---|---|
| strEventValue | string | 是 | 事件数据(Json) |

第51页共63页

VideoCommMediaSDKForHarmony 接口开发手册

# 4. 常量定义

在Harmony SDK 中,对于业务对象、动作指令定义了一些常量,做为接口

的参数进行使用。

### 4.1.会议动作定义常量

| 序 号 | 参数 | 值 | 说明 |
|---|---|---|---|
| 1 | VCOM CONFERENCE ATICONCODE JOIN _ _ _ | 1 | 加入会议操作 |
| 2 | VCOM CONFERENCE ATICONCODE EXIT _ _ _ | 2 | 离开会议操作 |

### 4.2.发送文件控制常量

在文件发送时,进行控制的常量。

| 序 号 | 参数 | 值 | 说明 |
|---|---|---|---|
| 1 | VCOM SENDFILE CTRLCODE PAUSE _ _ _ | 1 | 暂停发送 |
| 2 | VCOM SENDFILE CTRLCODE STOP _ _ _ | 2 | 停止发送(停止之后,发送句 柄将回收释放) |
| 3 | VCOM SENDFILE CTRLCODE RESUME _ _ _ | 3 | 恢复发送 |
| 4 | VCOM SENDFILE CTRLCODE SPEED _ _ _ | 4 | 速率控制(ctrlvalue 携带相应 参数) |

### 4.3.媒体信息类型

| 序 号 | 参数 | 值 | 说明 |
|---|---|---|---|
| 1 | VCOM MEDIAINFO PLAYTIME _ _ | 2 | 播放时间(单位:ms) |

第52页共63页

VideoCommMediaSDKForHarmony 接口开发手册

| 2 | VCOM MEDIAINFO DURATION _ _ | 5 | 媒体文件时长(单位:ms) |
|---|---|---|---|

### 4.4.录像布局常量

| 序 号 | 参数 | 值 | 说明 |
|---|---|---|---|
| 1 | VCOM RECORD MODE ONE _ _ _ | one | 单画面 |
| 2 | VCOM RECORD MODE TWO 1 _ _ _ _ | two-1 | 双画面-并列模式 |
| 3 | VCOM RECORD MODE TWO 2 _ _ _ _ | two-2 | 双画面-画中画模式 |
| 4 | VCOM RECORD MODE TWO 3 _ _ _ _ | two-3 | 双画面-上下模式 |
| 5 | VCOM RECORD MODE THREE 1 _ _ _ _ | three- 1 | 三画面画面-画中画模式 |

### 4.5.排队控制命令码

| 序号 | 参数 | 值 | 说明 |
|---|---|---|---|
| 1 | VCOM QUEUECTRL ENTERQUEUE _ _ | 100 | 进入队列 |
| 2 | VCOM QUEUECTRL LEAVEQUEUE _ _ | 101 | 离开队列 |
| 3 | VCOM QUEUECTRL STARTSERVICE _ _ | 300 | 坐席示闲(开始路由服务) |
| 4 | VCOM QUEUECTRL STOPSERVICE _ _ | 301 | 坐席示忙(停止路由服务) |
| 5 | VCOM QUEUECTRL AGENTSERVICE _ _ | 302 | 坐席开始服务 |
| 6 | VCOM QUEUECTRL AGENTFINISH _ _ | 303 | 坐席结束服务 |

### 4.6.排队回调事件类型

| 序号 | 参数 | 值 | 说明 |
|---|---|---|---|

第53页共63页

VideoCommMediaSDKForHarmony 接口开发手册

| 1 | VCOM QUEUEEVENT ENTERRESULT _ _ | 100 | 进入队列结果事件 |
|---|---|---|---|
| 2 | VCOM QUEUEEVENT LEAVERESULT _ _ | 101 | 离开队列结果事件 |
| 3 | VCOM QUEUEEVENT QUEUESTATUS _ _ | 201 | 队列变化事件 |
| 4 | VCOM QUEUEEVENT AGENTERVICE _ _ | 300 | 路由分配 坐席/用户 服务 事件 |

### 4.7.视频呼叫的控制命令字

| 序号 | 参数 | 值 | 说明 |
|---|---|---|---|
| 1 | VCOM VIDEOCALL INVITE _ _ | 1 | 主叫,发起呼叫 |
| 2 | VCOM VIDEOCALL CANCEL _ _ | 2 | 主叫,取消呼叫 |
| 3 | VCOM VIDEOCALL ACCEPT _ _ | 3 | 被叫,同意呼叫请求 |
| 4 | VCOM VIDEOCALL REJECT _ _ | 4 | 被叫,拒绝呼叫请求 |
| 5 | VCOM VIDEOCALL BYE _ _ | 5 | 主叫、被叫,挂断通话 |
| 6 | VCOM VIDEOCALL FORWARDING _ _ | 6 | 邀请第三方(用户呼叫转移) |
| 7 | VCOM VIDEOCALL FORWARDING CA _ _ _ LCEL | 7 | 取消邀请第三方(用户呼叫 转移) |

### 4.8.视频呼叫的事件类型

| 序号 | 参数 | 值 | 说明 |
|---|---|---|---|
| 1 | VCOM VIDEOCALLEVENT RINGING _ _ | 101 | 被叫方收到呼叫振铃事件 |
| 2 | VCOM VIDEOCALLEVENT BYCANCE _ _ L | 102 | 被叫方收到呼叫取消事件 |
| 3 | VCOM VIDEOCALLEVENT BYREJECT _ _ | 103 | 主叫方收到拒绝呼叫事件 |
| 4 | VCOM VIDEOCALLEVENT VIDEOING _ _ | 104 | 开始通话事件(携带会议 号),主叫、被叫都会收到 这个事件 |
| 5 | VCOM VIDEOCALLEVENT VIDEOEND _ _ | 105 | 结束通话事件,当其中一方 调用挂断通话 或者 掉线 |

第54页共63页

VideoCommMediaSDKForHarmony 接口开发手册

|  |  |  | 时,主叫、被叫都会收到这 个事件 |
|---|---|---|---|
| 6 | VCOM VIDEOCALLEVENT ACK INVI _ _ _ TE | 1001 | 发起呼叫的应答事件(假设 对方正在通话中,可收到对 方通话中的错误码等) |
| 7 | VCOM VIDEOCALLEVENT ACK CAN _ _ _ CEL | 1002 | 取消呼叫的应答事件 |
| 8 | VCOM VIDEOCALLEVENT ACK ACCE _ _ _ PT | 1003 | 同意呼叫的应答事件 |
| 9 | VCOM VIDEOCALLEVENT ACK REJE _ _ _ CT | 1004 | 拒绝呼叫的应答事件 |
| 10 | VCOM VIDEOCALLEVENT ACK BYE _ _ _ | 1005 | 挂断呼叫的应答事件 |
| 11 | VCOM VIDEOCALLEVENT ACK FOR _ _ _ WARDING | 1011 | 发起邀请呼叫的应答事件 (若对方正在通话或不在 线,会触发收到对方通话中 的错误码) |
| 12 | VCOM VIDEOCALLEVENT ACK FOR _ _ _ WARDINGCANCEL | 1012 | 取消邀请呼叫的应答事件 |
| 13 | VCOM VIDEOCALLEVENT FORWARDI _ _ NG ACCEPT _ | 1013 | 发起邀请者收到接听事件 |
| 14 | VCOM VIDEOCALLEVENT FORWARDI _ _ NG REJECT _ | 1014 | 发起邀请者收到拒绝事件 |

### 4.9.媒体文件控制码

| 序号 | 参数 | 值 | 说明 |
|---|---|---|---|
| 1 | VCOM MEDIAFILE CMD LOAD _ _ _ | 1 | 加载 |
| 2 | VCOM MEDIAFILE CMD PLAY _ _ _ | 2 | 播放 |
| 3 | VCOM MEDIAFILE CMD JUMP _ _ _ | 3 | 跳转 |
| 4 | VCOM MEDIAFILE CMD PAUSE _ _ _ | 4 | 暂停 |
| 5 | VCOM MEDIAFILE CMD STOP _ _ _ | 5 | 停止 |
| 6 | VCOM MEDIAFILE CMD UNLOAD _ _ _ | 6 | 卸载 |
| 7 | VCOM MEDIAFILE CMD GETMEDIAI _ _ _ NFO | 7 | 获取媒体信息 |
| 8 | VCOM MEDIAFILE CMD GETSTATUS _ _ _ | 8 | 获取播放状态 |

第55页共63页

VideoCommMediaSDKForHarmony 接口开发手册

| 9 | VCOM MEDIAFILE CMD GETCURREN _ _ _ TPTS | 9 | 获取播放进度 |
|---|---|---|---|

### 4.10.媒体资源类型

| 序号 | 参数 | 值 | 说明 |
|---|---|---|---|
| 1 | VCOM MEDIARESOURCE TYPE UNK _ _ _ NOW | 0 | 未知文件 |
| 2 | VCOM MEDIARESOURCE TYPE PPT _ _ _ | 1 | ppt 文件 |
| 3 | VCOM MEDIARESOURCE TYPE VIDE _ _ _ O | 2 | 视频文件 |
| 4 | VCOM MEDIARESOURCE TYPE AUDI _ _ _ O | 3 | 音频文件 |
| 5 | VCOM MEDIARESOURCE TYPE IMAG _ _ _ E | 4 | 图片文件 |
| 6 | VCOM MEDIARESOURCE TYPE COM _ _ _ PRESSED | 5 | 压缩文件 |
| 7 | VCOM MEDIARESOURCE TYPE COM _ _ _ MONFILE | 6 | 普通文件 |

### 4.11.媒体资源控制指令

| 序号 | 参数 | 值 | 说明 |
|---|---|---|---|
| 1 | VCOM MEDIARESOURCE CONTROL _ _ _ UNKNOW | 0 | 未知指令 |
| 2 | VCOM MEDIARESOURCE CONTROL _ _ _ DOWNLOAD | 1 | 下载 |
| 3 | VCOM MEDIARESOURCE CONTROL _ _ _ UPLOAD | 2 | 上传 |
| 4 | VCOM MEDIARESOURCE CONTROL _ _ _ QUERY | 3 | 查询 |
| 5 | VCOM MEDIARESOURCE CONTROL _ _ _ CANCEL | 4 | 取消 |

### 4.12.媒体任务传输状态

| 序号 | 参数 | 值 | 说明 |
|---|---|---|---|

第56页共63页

VideoCommMediaSDKForHarmony 接口开发手册

| 1 | VCOM MEDIARESOURCE STATUS UN _ _ _ KNOW | 0 | 未知状态 |
|---|---|---|---|
| 2 | VCOM MEDIARESOURCE STATUS PR _ _ _ EPARE | 1 | 准备 |
| 3 | VCOM MEDIARESOURCE STATUS TR _ _ _ ANSMITTING | 2 | 传输中 |
| 4 | VCOM MEDIARESOURCE STATUS TR _ _ _ ANSFAIL | 3 | 传输失败 |
| 5 | VCOM MEDIARESOURCE STATUS PA _ _ _ USE | 4 | 暂停 |
| 6 | VCOM MEDIARESOURCE STATUS CA _ _ _ NCEL | 5 | 取消 |
| 7 | VCOM MEDIARESOURCE STATUS CO _ _ _ MPLETE | 6 | 完成 |
| 8 | VCOM MEDIARESOURCE STATUS ST _ _ _ OP | 7 | 停止 |

### 4.13.AI能力厂家定义

| 序号 | 参数 | 值 | 说明 |
|---|---|---|---|
| 1 | VCOM AIABILITY COMPANY BAIDU _ _ _ | 1 | 百度云 |
| 2 | VCOM AIABILITY COMPANY ALIYU _ _ _ N | 2 | 阿里云 |

### 4.14.AI能力的控制码

| 序号 | 参数 | 值 | 说明 |
|---|---|---|---|
| 1 | VCOM AIABILITY TTS _ _ | 1 | 语音合成 |
| 2 | VCOM AIABILITY ASR AWORD _ _ _ | 10 | 语音识别:一句话 |
| 3 | VCOM AIABILITY ASR FILE _ _ _ | 11 | 语音识别:录音文件识别 |
| 4 | VCOM AIABILITY ASR STREAM _ _ _ | 12 | 语音识别:实时流识别 |
| 5 | VCOM AIABILITY OCR IDCARD _ _ _ | 20 | OCR:身份证识别 |
| 6 | VCOM AIABILITY OCR BANKCARD _ _ _ | 21 | OCR:银行卡识别 |

第57页共63页

VideoCommMediaSDKForHarmony 接口开发手册

| 7 | VCOM AIABILITY AFR DETECT _ _ _ | 30 | 人脸识别:人脸检测 |
|---|---|---|---|
| 8 | VCOM AIABILITY AFR COMPARE _ _ _ | 31 | 人脸识别:人脸比对 |
| 9 | VCOM AIABILITY AFR LIVE _ _ _ | 32 | 人脸识别:活体检测 |

### 4.15.AI能力的事件类型

| 序号 | 参数 | 值 | 说明 |
|---|---|---|---|
| 1 | VCOM AIABILITY EVENT PROCESSIN _ _ _ G | 1 | 识别处理中(对于语音实时 流识别会存在中间结果) |
| 2 | VCOM AIABILITY EVENT RESULT _ _ _ | 2 | 识别结果 |

### 4.16.队列控制的控制码

| 序号 | 参数 | 值 | 说明 |
|---|---|---|---|
| 1 | VCOM QUEUECTRL ENTERQUEUE _ _ | 100 | 进入队列 |
| 2 | VCOM QUEUECTRL LEAVEQUEUE _ _ | 101 | 离开队列 |
| 3 | VCOM QUEUECTRL QUERYQUEUEIN _ _ FO | 200 | 查询队列信息 |
| 4 | VCOM QUEUECTRL QUREYQUEUELE _ _ NGTH | 201 | 查询队列长度、排队第几位 |
| 5 | VCOM QUEUECTRL CHECKIN _ _ | 300 | 坐席签入 |
| 6 | VCOM QUEUECTRL CHECKOUT _ _ | 301 | 坐席签出 |
| 7 | VCOM QUEUECTRL READYSERVICE _ _ | 302 | 坐席示闲 |
| 8 | VCOM QUEUECTRL BUSYSERVICE _ _ | 303 | 坐席示忙 |
| 9 | VCOM QUEUECTRL PAUSESERVICE _ _ | 304 | 坐席暂停(休息) |
| 10 | VCOM QUEUECTRL STARTVIDEO _ _ | 305 | 开始通话 |

第58页共63页

VideoCommMediaSDKForHarmony 接口开发手册

| 11 | VCOM QUEUECTRL HANGUPVIDEO _ _ | 306 | 挂断通话 |
|---|---|---|---|

### 4.17.队列控制的事件类型

| 序号 | 参数 | 值 | 说明 |
|---|---|---|---|
| 1 | VCOM QUEUEEVENT ENTERRESULT _ _ | 100 | 进入队列结果事件 |
| 2 | VCOM QUEUEEVENT LEAVERESULT _ _ | 101 | 离开队列结果事件 |
| 3 | VCOM QUEUEEVENT QUERYQUEUEI _ _ NFO | 200 | 查询队列信息事件 |
| 4 | VCOM QUEUEEVENT QUREYQUEUEL _ _ ENGTH | 201 | 查询队列长度、排队第几位 |
| 5 | VCOM QUEUEEVENT QUEUESTATUS _ _ | 202 | 队列变化事件 |
| 6 | VCOM QUEUEEVENT AGENTSERVICE _ _ | 300 | 路由分配 坐席/用户 服务事 件 |
| 7 | VCOM QUEUEEVENT AGENTSTATUS _ _ | 301 | 坐席状态改变事件 |
| 8 | VCOM QUEUEEVENT STARTVIDEO _ _ | 302 | 开始通话事件 |
| 9 | VCOM QUEUEEVENT HANGUPVIDEO _ _ | 303 | 挂断通话事件 |
| 10 | VCOM QUEUEEVENT ACTIONCODE _ _ | 400 | 控制命令字失败事件 |

### 4.18.队列控制的常量定义

| 序号 | 参数 | 值 | 说明 |
|---|---|---|---|
| 1 | VCOM AGENT SERVICE STATUS INIT _ _ _ _ | 0 | 初始化状态(签入前、签出后) |
| 2 | VCOM AGENT SERVICE STATUS PRE _ _ _ _ PARE | 1 | 准备状态 |
| 3 | VCOM AGENT SERVICE STATUS IDL _ _ _ _ E | 2 | 空闲状态 |
| 4 | VCOM AGENT SERVICE STATUS VID _ _ _ _ EO | 3 | 已路由分配,正在视频通话中 |
| 5 | VCOM AGENT SERVICE STATUS PAU _ _ _ _ SE | 4 | 暂停状态 |

第59页共63页

VideoCommMediaSDKForHarmony 接口开发手册

| 6 | VCOM AGENT SERVICE STATUS STO _ _ _ _ P | 5 | 停止状态 |
|---|---|---|---|
| 7 | VCOM AGENT SERVICE STATUS FILE _ _ _ _ | 6 | 归档状态,挂断后坐席需要归 档资料 |
| 8 | VCOM AGENT SERVICE STATUS CAL _ _ _ _ LING | 7 | 正在被叫振铃 |

### 4.19.Volte 视频呼叫的控制命令字

| 序号 | 参数 | 值 | 说明 |
|---|---|---|---|
| 1 | VCOM VOLTECALL INVITE _ _ | 21 | 主叫,发起呼叫 |
| 2 | VCOM VOLTECALL CANCEL _ _ | 22 | 主叫,取消呼叫 |
| 3 | VCOM VOLTECALL ACCEPT _ _ | 23 | 被叫,同意呼叫请求 |
| 4 | VCOM VOLTECALL REJECT _ _ | 24 | 被叫,拒绝呼叫请求 |
| 5 | VCOM VOLTECALL BYE _ _ | 25 | 主叫、被叫,挂断通话 |

### 4.20.Volte 视频呼叫的事件类型

| 序号 | 参数 | 值 | 说明 |
|---|---|---|---|
| 1 | VCOM VOLTECALLEVENT RINGING _ _ | 201 | 被叫方收到呼叫振铃事件 |
| 2 | VCOM VOLTECALLEVENT BYCANCE _ _ L | 202 | 被叫方收到呼叫取消事件 |
| 3 | VCOM VOLTECALLEVENT BYREJECT _ _ | 203 | 主叫方收到拒绝呼叫事件 |
| 4 | VCOM VOLTECALLEVENT VIDEOING _ _ | 204 | 开始通话事件(携带会议 号),主叫、被叫都会收到 这个事件 |
| 5 | VCOM VOLTECALLEVENT VIDEOEND _ _ | 205 | 结束通话事件,当其中一方 调用挂断通话 或者 掉线 时,主叫、被叫都会收到这 个事件 |
| 6 | VCOM VOLTECALLEVENT ACK INVI _ _ _ TE | 2001 | 发起呼叫的应答事件(假设 对方正在通话中,可收到对 方通话中的错误码等) |

第60页共63页

VideoCommMediaSDKForHarmony 接口开发手册

| 7 | VCOM VOLTECALLEVENT ACK CAN _ _ _ CEL | 2002 | 取消呼叫的应答事件 |
|---|---|---|---|
| 8 | VCOM VOLTECALLEVENT ACK ACC _ _ _ EPT | 2003 | 同意呼叫的应答事件 |
| 9 | VCOM VOLTECALLEVENT ACK REJE _ _ _ CT | 2004 | 拒绝呼叫的应答事件 |
| 10 | VCOM VOLTECALLEVENT ACK BYE _ _ _ | 2005 | 挂断呼叫的应答事件 |

第61页共63页

VideoCommMediaSDKForHarmony 接口开发手册

# 5. 错误参考代码

在VideoComm Media SDK 中,当集成开发调试或程序运行期间会产生一些

异常,可以通过系统定义的错误代码来参考异常出现的问题原因,主要的错误参

考代码如下(更多请参考:VComErrorCode.java):

| 序号 | 参数 | 值 | 说明 |
|---|---|---|---|
| 1 | VCOM ERROR SUCCESS _ _ | 0 | 成功 |
| 2 | VCOM NOTSUPPORT SDKPLUGIN _ _ | 10 | 浏览器不支持插件 |
| 3 | VCOM NOTINSTALL SDKPLUGIN _ _ | 11 | 未安装插件 |
| 4 | VCOM NOTVERSION SDKPLUGIN _ _ | 12 | 插件版本不对应 |
| 5 | VCOM NOTINIT SDKPLUGIN _ _ | 13 | 插件未初始化 |
| 6 | VCOM ERROR NOTINIT _ _ | 100 | 未初始化 |
| 7 | VCOM ERROR UNKNOWED _ _ | 101 | 未知异常 |
| 8 | VCOM ERROR SESSIONINVALID _ _ | 103 | 无效会话 |
| 9 | VCOM ERROR CHANNEL NOTEXIST _ _ _ | 130 | 通道号不存在 |
| 10 | VCOM ERROR USERCODE NOTEXIST _ _ _ | 131 | 用户不存在 |
| 11 | VCOM ERROR FUNCLIMITED _ _ | 400 | 功能限制(未授权) |
| 12 | VCOM ERROR HAD LOGINED _ _ _ | 410 | 用户ID 已被登录 |
| 13 | VCOM ERROR CERTIFY FAIL _ _ _ | 411 | 签名认证失败 |
| 14 | VCOM ERROR CONF NOTEXIST _ _ _ | 500 | 会议不存在 |
| 15 | VCOM ERROR CONF HADIN _ _ _ | 501 | 已在会议内 |
| 16 | VCOM ERROR CONF NOTIN _ _ _ | 502 | 不在会议内 |
| 17 | VCOM ERROR CONF HADINOTHER _ _ _ | 503 | 已在其他会议内 |

第62页共63页

VideoCommMediaSDKForHarmony 接口开发手册

| 18 | VCOM ERROR CERT INVALID _ _ _ | 750 | 无效证书 |
|---|---|---|---|
| 19 | VCOM ERROR CERT FILENOTEXIST _ _ _ | 751 | 证书不存在 |
| 20 | VCOM ERROR CERT DOMAIN NOTMAT _ _ _ _ CH | 755 | 域名不匹配 |
| 21 | VCOM ERROR CERT NOSUPPORTTYPE _ _ _ | 756 | 不支持的授权类型 |
| 22 | VCOM ERROR CERT DEADLINE _ _ _ | 757 | 证书已过期 |
| 23 | VCOM ERROR RECORD VIDEONONENT _ _ _ ITY | 700 | 视频不存在 |
| 24 | VCOM ERROR RECORD AUDIONONENT _ _ _ ITY | 701 | 音频不存在 |
| 25 | VCOM ERROR RECORD CREATEFILEFA _ _ _ IL | 704 | 创建录像文件失败 |
| 26 | VCOM ERROR RECORD PARAMS _ _ _ | 706 | 录像参数不正确 |
| 27 | VCOM ERROR RECORD CRATETASK _ _ _ | 707 | 创建录像任务失败 |
| 28 | VCOM ERROR RECORD NOTTASK _ _ _ | 709 | 不存在的录像任务 |

第63页共63页
