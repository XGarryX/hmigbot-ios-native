# ohos_jcsdk

# 介绍

菊风云为开发者提供专业稳定的实时音视频通信云服务。开发者通过集成 Juphoon Cloud

SDK(JC SDK),即可轻松快速实现全行业多场景应用,应用领域覆盖社交、直播、教

育、智能硬件、金融、医疗、政企、会议、呼叫中心等。

JC SDK 在音视频编解码、图像处理、回声消除等方面具有独特的技术优势,为开发者带

来高清流畅的通话体验的同时,极大简化了音视频会话应用开发的研发过程。开发者只需

调用相应的 API,便能快速开发具有优异性能的音视频应用。

在这里您将学习如何集成 JC SDK。让我们开启音视频集成开发之旅吧!

Juphoon Cloud SDK (JC SDK) - Usable, Simple, Elegant !

# 安装

ohpm install @juphoon/jcsdk

# 使用说明

import {

  JCClient,

  JCCall,

  JCMediaDevice,

  JCMediaChannel,

} from 'JCSDK';

# 前提条件

•

HarmonyOS SDK: HarmonyOS 5.0.0 Release SDK

•

DevEco-Studio:HarmonyOS NEXT Release(V5.0.3.900)及以上

•

有效的菊风开发者账号,菊风官网控制台注册获取账号

•

有效的菊风AppKey ,控制台创建应用获取

•

若应用开启Token鉴权模式,通过您的服务生成有效Token 。未开启Token鉴权,则

无需生成。

# 接口说明

•

JCClient 用于初始化sdk以及登录 Juphoon Cloud 平台

•

JCClientCallback 用于回调登录相关事件

•

JCMediaDevice 用于管理设备

•

JCMediaDeviceCallback 用于回调设备相关事件

•

JCMediaVolumeCallback 用于回调音量相关事件

•

JCCall 用于管理一对一通话

•

JCCallCallback 用于回调一对一通话相关事件

•

JCMediaChannel 用于管理多方通话

•

JCMediaChannelCallback 用于回调多方通话相关事件

## 登录管理

| 方法 | 描述 |
|---|---|
| JCClient.create | 创建 JCClient 对象 |
| JCClient.destroy | 销毁 JCClient 对象 |
| JCClient.getAppkey | 获取Appkey |
| JCClient.setForeground | 设置是否为前台 |
| JCClient.getState | 获取当前状态 |
| JCClient.login | 登录 Juphoon Cloud 平台 |

| 方法 | 描述 |
|---|---|
| JCClient.logout | 登出 Juphoon Cloud 平台 |

## 登录事件

| 事件 | 描述 |
|---|---|
| JCClientCallback.onLogin | 登录结果回调 |
| JCClientCallback.onLogout | 登出回调 |
| JCClientCallback.onClientStateChange | 登录状态变化通知 |

## 账号管理

| 方法 | 描述 |
|---|---|
| JCClient.setDisplayName | 设置昵称 |
| JCClient.getDisplayName | 获取昵称 |
| JCClient.getCreateParam | 获取创建参数 |
| JCClient.getLoginParam | 获取登录参数 |
| JCClient.getUserId | 获得用户标识 |

## 在线消息

| 方法 | 描述 |
|---|---|
| JCClient.sendOnlineMessage | 发送在线消息 |

## 在线消息事件

| 方法 | 描述 |
|---|---|
| JCClientCallback.onOnlineMessageSendResult | 在线消息发送结果 |
| JCClientCallback.onOnlineMessageReceive | 收到在线消息 |

## 订阅消息事件

| 方法 | 描述 |
|---|---|
| JCClientCallback.onServerMessageReceive | 收到订阅消息 |

## 设备管理

| 事件 | 描述 |
|---|---|
| JCMediaDevice.create | 创建 JCMediaDevice 对象 |
| JCMediaDevice.destroy | 销毁 JCMediaDevice 对象 |

## 音频管理

| 方法 | 描述 |
|---|---|
| JCMediaDevice.isSpeakerOn | 扬声器是否已打开 |
| JCMediaDevice.isAudioStart | 音频是否已打开 |
| JCMediaDevice.startAudio | 启动音频 |
| JCMediaDevice.stopAudio | 停止音频 |
| JCMediaDevice.enableSpeaker | 开启关闭扬声器 |
| JCMediaDevice.getAudioRouteType | 音频路由类型 |

| 方法 | 描述 |
|---|---|
| JCMediaDevice.addVolumeCallback | 添加音量上报回调 |
| JCMediaDevice.removeVolumeCallback | 删除音量上报回调 |

## 音频事件

| 事件 | 描述 |
|---|---|
| JCMediaDeviceCallback.onAudioOutputType Change | 音频输出类型变化 |
| JCCallCallback.onEarlyMediaReceived | 收到早期媒体的回调 |
| JCCallCallback.onSipRingInfoReceived | 收到早期媒体的回调收到sip振铃信 息 |
| JCMediaVolumeCallback.outputVolume | 音频播放数据音量,发送的事件通知 类型 |
| JCMediaVolumeCallback.inputVolume | 音频采集数据音量,发送的事件通知 类型 |

## 视频管理

| 方法 | 描述 |
|---|---|
| JCMediaDevice.isCameraOpen | 摄像头是否已打开 |
| JCMediaDevice.getCamera | 获取当前的摄像头 |
| JCMediaDevice.getCameras | 获取摄像头列表 |
| JCMediaDevice.startCamera | 开启摄像头 |
| JCMediaDevice.stopCamera | 关闭摄像头 |
| JCMediaDevice.switchCameraBetweenFrontAndBack() | 切换摄像头 |

| 方法 | 描述 |
|---|---|
| JCMediaDevice.switchCamera | 切换摄像头(指定摄像头) |
| JCMediaDevice.getCameraType | 获得摄像头类型 |
| JCMediaDevice.setVideoFrameCallback | 设置视频观测器对象 |

## 视频事件

| 事件 | 描述 |
|---|---|
| JCMediaDeviceCallback.onCameraUpdate | 摄像头变化 |
| JCMediaDeviceCallback.onRenderReceived | 收到第一帧数据 |
| JCMediaDeviceCallback.onRenderStart | 渲染开始 |

## 一对一通话管理

| 方法 | 描述 |
|---|---|
| JCCall.create | 创建 JCCall 对象 |
| JCCall.destroy | 销毁 JCCall 对象 |
| JCCall.call | 发起一对一呼叫 |
| JCCall.term | 挂断 |
| JCCall.answer | 接听 |
| JCCall.mute | 静音 |
| JCCall.muteSpeaker | 音频输出静音 |
| JCCall.muteMicrophone | 音频输入静音 |
| JCCall.setMicScale | 麦克风声音放大 |

| 方法 | 描述 |
|---|---|
| JCCall.hold | 呼叫保持 |
| JCCall.becomeActive | 切换活跃通话 |
| JCCall.getCallItems | 获得通话对象列表 |
| JCCall.getActiveCallItem | 获得当前活跃的通话 |
| JCCall.getStatistics | 获得当前通话统计信息 |

## 一对一通话事件

| 事件 | 描述 |
|---|---|
| JCCallCallback.onCallItemAdd | 新增通话回调 |
| JCCallCallback.onCallItemRemove | 移除通话回调 |
| JCCallCallback.onCallItemUpdate | 通话状态更新回调 |
| JCCallCallback.onMissedCallItem | 上报服务器拉取的未接来电 |

## 通话录音管理

| 方法 | 描述 |
|---|---|
| JCCall.audioRecord | 语音通话录音 |
| JCCall.videoRecord | 视频通话录制 |

## DTMF

| 方法 | 描述 |
|---|---|
| JCCall.sendDtmf | 发送DTMF信息 |

## DTMF事件

| 方法 | 描述 |
|---|---|
| JCCallCallback.onDtmfReceived | 通话中收到DTMF回调 |

## 通话中消息管理

| 方法 | 描述 |
|---|---|
| JCCall.sendMessage | 通过通话建立的通道发送数据 |

## 通话中消息事件

| 方法 | 描述 |
|---|---|
| JCCallCallback.onMessageReceive | 通话中收到消息的回调 |

## 通话媒体参数管理

| 方法 | 描述 |
|---|---|
| JCCall.updateMediaConfig | 更新媒体参数 |
| JCCall.getMediaConfig | 获得当前的媒体参数 |

## 通话视频流管理

| 方法 | 描述 |
|---|---|
| JCCall.enableUploadVideoStream | 开启关闭视频流发送 |

## 频道管理

| 方法 | 描述 |
|---|---|
| JCMediaChannel.create | 创建 JCMediaChannel 对象 |
| JCMediaChannel.destroy | 销毁 JCMediaChannel 对象 |
| JCMediaChannel.getChannelUri | 获得频道 Uri |
| JCMediaChannel.getChannelId | 获得频道标识 |
| JCMediaChannel.getPassword | 获得频道密码 |
| JCMediaChannel.getChannelNumber | 获得频道号 |
| JCMediaChannel.getTitle | 返回频道标题 |
| JCMediaChannel.getState | 返回当前在频道中的状态 |
| JCMediaChannel.query | 查询频道相关信息 |
| JCMediaChannel.join | 加入频道 |
| JCMediaChannel.leave | 离开频道 |
| JCMediaChannel.stop | 关闭频道 |
| JCMediaChannel.setCustomProperty | 设置频道自定义属性 |
| JCMediaChannel.getCustomProperty | 获取自定义频道属性 |
| JCMediaChannel.setCustomRole | 设置自定义角色 |
| JCMediaChannel.getCustomRole | 获得自定义角色 |
| JCMediaChannel.setCustomState | 设置自定义状态 |
| JCMediaChannel.getCustomState | 获得自定义状态 |
| JCMediaChannel.getSelfParticipant | 获得自身 JCMediaChannelParticipant 对象 |

## 频道事件

| 事件 | 描述 |
|---|---|
| JCMediaChannelCallback.onMediaChannelStateChange | 自身状态变化回调 |
| JCMediaChannelCallback.onMediaChannelPropertyChange | 属性变化回调 |
| JCMediaChannelCallback.onJoin | 加入频道结果回调 |
| JCMediaChannelCallback.onLeave | 离开频道结果回调 |
| JCMediaChannelCallback.onStop | 解散频道结果回调 |
| JCMediaChannelCallback.onQuery | 查询频道信息结果回调 |

## 频道音视频管理

| 方法 | 描述 |
|---|---|
| JCMediaChannel.getAudioOutput | 获取音频是否输出 |
| JCMediaChannel.enableUploadVideoStream | 开启关闭发送本地视频流 |
| JCMediaChannel.enableAudioOutput | 开启关闭音频输出 |
| JCMediaChannel.requestVideo | 请求频道中其他用户的视频流 |
| JCMediaChannel.getStatistics | 获取统计信息 |
| JCMediaChannel.enableSelfVideoRatio | 设置自身视频宽高比 |
| JCMediaChannel.getMaxResolution | 获得频道最大分辨率 |

## 成员管理

| 事件 | 描述 |
|---|---|
| JCMediaChannel.getParticipants | 获得所有频道中的成员 |

| 事件 | 描述 |
|---|---|
| JCMediaChannel.getParticipant | 获取频道成员 |
| JCMediaChannel.kick | 将成员踢出会议 |
| JCMediaChannel.subscribeParticipantAudio | 订阅或取消订阅指定用户的声音 |

## 成员事件

| 事件 | 描述 |
|---|---|
| JCMediaChannelCallback.onParticipantJoin | 新成员加入回调 |
| JCMediaChannelCallback.onParticipantLeft | 成员离开回调 |
| JCMediaChannelCallback.onParticipantUpdate | 成员更新回调 |
| JCMediaChannelCallback.onParticipantVolumeChange | 成员声音变化 |

## Cdn推流

| 事件 | 描述 |
|---|---|
| JCMediaChannel.enableCdn | 开关Cdn推流 |
| JCMediaChannel.getCdnState | 获得cdn推流状态 |

## 服务器录制

| 事件 | 描述 |
|---|---|
| JCMediaChannel.enableRecord | 开关视频录制 |
| JCMediaChannel.getRecordState | 获取视频录制状态 |

## 音频数据上传

| 事件 | 描述 |
|---|---|
| JCMediaChannel.getUploadLocalAudio | 获取本地音频数据是否在上传 |

## 视频数据上传

| 事件 | 描述 |
|---|---|
| JCMediaChannel.getUploadLocalVideo | 获取本地视频数据是否在上传 |

## 频道消息管理

| 事件 | 描述 |
|---|---|
| JCMediaChannel.sendMessage | 发送消息 |
| JCMediaChannel.sendCommand | 发送指令 |
| JCMediaChannel.sendCommandToDelivery | 发送命令给推流或录制器 |

## 频道消息事件

| 事件 | 描述 |
|---|---|
| JCMediaChannelCallback.onChannelMessageReceive | 接收频道消息的回调 |

## 屏幕共享

| 事件 | 描述 |
|---|---|
| JCMediaChannel.requestScreenVideo | 请求屏幕共享的视频流 |
| JCMediaChannel.enableScreenShare | 开关屏幕分享 |

| 事件 | 描述 |
|---|---|
| JCMediaChannel.getScreenRenderId | 获取屏幕共享渲染标识 |
| JCMediaChannel.getScreenUserId | 获取开启屏幕共享的用户标识 |
| JCMediaChannel.startScreenShareVideo | 启动屏幕共享视频渲染 |

# 约束与限制

在下述版本验证通过:

DevEco Studio: NEXT Release(5.0.3.900), SDK: API12 (5.0.0.71)

# 目录结构

|----JCSDK |     |---- libs  # SDK库文件夹 |                |---- cpp # c/c++接口 |                |---- ets # 接口声明 |     |---- index.ets  # 对外接口 |     |---- README.md  # 安装使用方法 |     |---- CHANGELOG.md  # SDK更新说明
