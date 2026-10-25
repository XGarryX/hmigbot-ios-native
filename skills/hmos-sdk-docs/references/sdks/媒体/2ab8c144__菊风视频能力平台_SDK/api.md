# **JRTCSDK** 

## **使用说明** 

### **多方通话2.0集成** 

```
import {
  JRTClient,
  JRTCClientCallback,
  JRTCMediaDevice,
  JRTCMediaDeviceCallback,
  JRTCall,
  JRTCCallCallback
 from '@juphoon/jrtcsdk';
```

- JRTCClient 用于初始化 SDK 以及登录登出 Juphoon RTC 平台 JRTCClientCallback 用于回调登录登出相关事件 

- JRTCMediaDevice 用于管理媒体设备 

- JRTCMediaDeviceCallback 用于回调媒体设备相关事件 

- JRTCCall 用于管理多方通话2.0 

- JRTCCallCallback 用于回调多方通话2.0相关事件 

#### **接口说明** 

##### **登录登出管理** 

|**方法**|**描述**|
|---|---|
|create|创建 JRTCClient 对象|
|destroy|销毁 JRTCClient 对象|
|setForeground|设置是否是前台|
|getUserId|获取用户ID|
|getState|获取当前登录状态|
|getDisplayName|获取用户昵称|
|setDisplayName|设置用户昵称|
|getServer|获取接入服务器地址|

|**方法**|**描述**|
|---|---|
|setServer|设置接入服务器地址|
|getAppKey|获取 Appkey|
|setAppKey|设置 Appkey|
|getAppName|获取应用名称|
|setAppName|设置应用名称|
|login|登录 Juphoon RTC 平台|
|logout|登出 Juphoon RTC 平台|
|sendOnlineMessage|发送在线消息|
|requestFileUploadInfo|获取文件上传或断点续传信息|
|completeFileUpload|文件上传完成确认|
|getUploadFileInfo|获取上传文件信息列表|

##### **登录登出事件** 

|**事件**|**描述**|
|---|---|
|onLogin|登录结果回调|
|onLogout|登出回调|
|onClientStateChanged|登录状态变化通知|
|onSDKEvent|上报事件回调|
|onOnlineMessageSendResult|在消息发送结果回调|
|onOnlineMessageReceived|收到在线消息回调|
|onRequestFileUploadInfoResponse|获取文件上传或断点续传信息响应|
|onCompleteFileUploadResponse|文件上传完成确认响应|
|onGetUploadFileInfoResponse|获取上传文件信息列表响应|
|onFileUploadPlatformNotify|文件上传到影像平台结果通知|

##### **设备管理** 

|**方法**|**描述**|
|---|---|
|create|创建 JRTCMediaDevice 对象|

|**方法**|**描述**|
|---|---|
|destroy|销毁 JRTCMediaDevice 对象|
|isCameraOpen|检查摄像头是否打开|
|isSpeakerOn|检查扬声器是否开启|
|getCurrentCamera|获取当前使用的摄像头|
|getCameras|获取设备上所有可用的摄像头列表|
|isAudioInputStart|音频输入是否打开|
|isAudioOutputStart|音频输出是否打开|
|startAudio|启动音频|
|stopAudio|停止音频|
|startAudioInput|打开音频输入设备|
|stopAudioInput|关闭音频输入设备|
|startAudioOutput|打开音频输出设备|
|stopAudioOutput|关闭音频输出设备|
|startCamera|开启摄像头|
|stopCamera|关闭摄像头|
|switchCamera|切换摄像头|
|switchCameraBetweenFrontAndBack|切换摄像头,用于手机前置和后置摄像头的切换|
|specifyCamera|指定要开启的摄像头|
|specifyCameraAngle|指定摄像头采集角度|
|setCameraProperty|设置摄像头采集属性|
|setScreenCaptureProperty|获取摄像头类型|
|enableSpeaker|开启/关闭扬声器|
|isVideoFileOpen|是否开启文件视频源|
|getVideoFileId|获取文件视频源ID|
|startVideoFile|逐帧采集视频画面|
|setVideoFileFrame|获取文件视频源ID|
|stopVideoFile|关闭视频文件作为视频输入源|
|getAudioRouteType|获得当前音频输出通道类型|

|**方法**|**描述**|
|---|---|
|setVideoAngle|设置有效的发送镜头旋转角度和本地渲染旋转角度|
|getVideoAngle|获取视频窗体角度|
|setVideoScreenOrientation|设置屏幕转向|
|startVideoCaptureRecord|开启视频录制|
|stopVideoCaptureRecord|关闭视频录制|
|startAudioRecord|开启音频录制|
|stopAudioRecord|关闭音频录制|
|recoveryRecordFile|恢复录制文件|
|getScreenCaptureId|获取屏幕共享采集Id|
|enableScreenCapture|开启/关闭屏幕采集|
|snapshotWithStreamId|截图|
|setScreenCaptureData|设置屏幕采集数据为指定图片数据|
|resetScreenCaptureData|重置屏幕采集数据|
|startAudioTest|检测音频设备是否正常|
|stopAudioTest|停止检测音频设备|
|getMicLevel|获取当前本地音量级别|
|getSpkLevel|获取当前扬声器音量级别|
|getAnrNoiseLevel|获取当前噪声强度|
|getAnrNoiseRatio|获取当前信噪比强度|
|startRing|开始播放音频|
|stopRing|结束播放音频|
|enableAudioInputFromFile|开始/结束播放本地音频文件作为音频源输入|
|suspendAudioInputFromFile|暂停/继续播放语音文件作为音频源输入|
|setAec|设置开启自适应回声消除|
|setAgc|设置是否开启自动增益控制|

##### **设备事件** 

|**事件**|**描述**|
|---|---|
|onAudioError|音频异常回调|
|onAudioRouteTypeChanged|音频输出通道变化回调|
|onCameraUpdate|摄像头变化回调|
|onVideoCaptureDidStart|视频采集开始回调|
|onRenderReceived|收到第一帧视频数据回调|
|onRenderStart|视频渲染开始回调|
|onRenderResized|视频宽高比例变化回调|
|onScreenSharePermissionResult|屏幕采集权限申请结果回调|
|onVideoError|视频异常回调|
|onSnapshotComplete|截图完成回调|
|onMemoryAvailable|设备剩余可用内存回调|
|onRingPlayFinish|铃声播放完成回调|
|onFileAudioInputDidFinish|本地文件音频源输入完成回调|
|onTessarEvent|天赛事件上报回调|

##### **多方通话2.0管理** 

|**方法**|**描述**|
|---|---|
|create|创建 JRTCCall 对象|
|destroy|销毁 JRTCCall 对象|
|join|加入通话|
|leave|离开通话|
|stop|结束通话|
|invite|邀请其他成员加入通话|
|cancelInvite|取消邀请|
|acceptInvite|接受邀请|
|rejectInvite|拒绝邀请|
|getState|获取自己当前在通话中的状态|
|getParticipants|获取所有成员列表|

|**方法**|**描述**|
|---|---|
|getParticipant|根据用户ID获取成员对象|
|getCallId|获取通话唯一标识|
|getSerialId|获取业务流水号|
|getUploadLocalAudio|获取本地音频数据是否在上传|
|getUploadLocalVideo|获取本地视频数据是否在上传|
|getAudioOutput|获取音频是否输出|
|getShareStreamId|获取屏幕共享的视频流ID|
|getShareUserId|获取发起屏幕共享者的用户ID|
|getStatistics|获取统计信息|
|getJsonStats|获取实时统计信息|
|getSupportVideoSizes|获取当前通话支持的视频分辨率列表|
|sendMessage|发送消息|
|enableUploadAudioStream|开启/关闭发送本地音频流|
|enableUploadVideoStream|开启/关闭发送本地视频流|
|enableAudioOutput|开启/关闭音频输出|
|sendAudioEmptyPack|发送音频空包|
|sendVideoEmptyPack|发送视频空包|
|enableScreenShare|开启/关闭屏幕共享|
|suspendScreenShare|暂停/继续屏幕共享|
|isSuspendScreenShare|获取屏幕共享是否处于暂停状态|
|setRatio|设置本端视频宽高比|
|getRequestSize|获取视频请求尺寸|
|setRequestSize|设置视频请求尺寸|
|requestVideo|订阅通话中其他成员的视频流|
|unRequestVideo|取消订阅通话中其他成员的视频流|
|requestScreenVideo|订阅通话中屏幕共享的视频流|
|unRequestScreenVideo|取消订阅通话中屏幕共享的视频流|
|createExtraStream|创建额外视频流|

|**方法**|**描述**|
|---|---|
|deleteExtraStream|删除额外视频流|
|requestExtraStreamVideo|订阅通话中其他用户的额外视频流|
|unRequestExtraStreamVideo|取消订阅通话中其他用户的额外视频流|
|enableLocalRecord|开启/关闭本地录制|
|updateLocalRecordLayout|更新本地录制自定义布局|
|isLocalRecording|是否正在本地录制|
|enableRemoteRecord|开启/关闭远程视频录制|
|updateRemoteRecordLayout|更新远程录制自定义布局|
|updateRemoteRecordWatermark|更新远程录制水印信息|
|getRemoteRecordState|获取远程视频录制状态|
|setVideoDot|远程录制视频打点|
|enableMicAgc|开启或关闭本地麦克风的增益(软件增益)|
|setSubScreenShare|设置是否订阅屏幕共享|
|isSubScreenShare|获取是否订阅屏幕共享|

##### **多方通话2.0事件** 

|**事件**|**描述**|
|---|---|
|onJoin|加入通话结果回调|
|onLeave|离开通话结果回调|
|onCallPropertyChanged|通话属性变化回调|
|onInviteResult|邀请结果回调|
|onCancelInviteResult|取消邀请结果回调|
|onAcceptInviteResult|接受邀请结果回调|
|onRejectInviteResult|拒绝邀请结果回调|
|onInviteReceived|收到邀请通知|
|onInviteCanceled|对方取消邀请通知|
|onInviteAccepted|对方接受邀请通知|
|onInviteRejected|对方拒绝邀请通知|

|**事件**|**描述**|
|---|---|
|onParticipantJoin|新成员加入回调|
|onParticipantLeft|成员离开回调|
|onParticipantUpdate|成员属性更新回调|
|onMessageReceived|收到消息回调|
