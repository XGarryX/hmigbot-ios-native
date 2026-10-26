通过阅读本文,您可以了解实时音视频 Harmony SDK 接口详情。 

# **AliRtcEngine接口** 

## **目录** 

### **基础接口** 

|**API**|**功能描述**|
|---|---|
|getInstance|获取AliRtcEngine实例|
|destroyInstance|销毁AliRtcEngine实例|
|getSDKVersion|查询SDK当前版本号|
|setLogDirPath|设置SDK日志文件保存路径|
|setH5CompatibleMode|设置H5兼容模式|
|getH5CompatibleMode|获取H5兼容模式设置|
|setRtcEngineEventListener|设置自身相关监听事件回调|

### **频道相关接口** 

|**API**|**功能描述**|
|---|---|
|setAudioOnlyMode|设置音频模式还是音视频模式|
|setAudioOnlyMode|加入频道|
|joinChannelWithToken|加入频道(带token)|
|leaveChannel|离开频道|
|setChannelProfile|设置频道模式|
|setClientRole|设置直播场景用户角色|
|getCurrentClientRole|获取当前用户角色|
|refreshAuthInfo|刷新鉴权信息|

|refreshAuthInfo|刷新鉴权信息(带token)|
|---|---|
|setAudioProfile|设置音频profile|
|isInCall|获取状态:当前是否在频道中|

### **发布及订阅相关接口** 

|**API**|**功能描述**|
|---|---|
|publishLocalVideoStream|是否推送本地视频(摄像头)流|
|setVideoEncoderConfiguration|设置相机流视频编码属性|
|publishLocalAudioStream|是否推送本地音频流|
|publishLocalAudioStream|是否推送次要音频流|
|publishLocalDualStream|是否推送次要视频流|
|setRemoteVideoStreamType|设置订阅的相机流格式,大流或小流|
|setRemoteDefaultVideoStreamType|设置默认订阅的相机流格式,大流或小流|
|subscribeAllRemoteAudioStreams|停止/恢复接收所有远端音频流|
|subscribeAllRemoteDualAudioStreams|停止/恢复接收远端次要音频流|
|subscribeAllRemoteVideoStreams|停止/恢复接收所有远端视频流|
|subscribeRemoteAudioStream|手动拉音频流|
|subscribeRemoteVideoStream|手动拉视频流|
|subscribeRemoteMediaStream|合并订阅远端音视频流|
|subscribeRemoteDestChannelStream|订阅目标频道,指定用户的流|
|subscribeRemoteDestChannelStreamWithTra ck|设置是否默认接收音频流|
|setDefaultSubscribeAllRemoteAudioStreams|设置是否默认接收音频流|

|setDefaultSubscribeAllRemoteVideoStreams|设置是否默认订阅视频流|
|---|---|
|setDefaultAudioRouteToSpeakerphone|设置默认音频输出是否从扬声器出声|

### **音频设备管理相关接口** 

|**API**|**功能描述**|
|---|---|
|muteLocalMic|停止/恢复本地音频数据发送|
|setRemoteAudioVolume|调节本地播放的指定远端用户音量|
|muteRemoteAudioPlaying|停止/恢复远端指定用户的音频流的播放|
|muteAllRemoteAudioPlaying|停止/恢复远端的所有音频流的播放|
|enableSpeakerphone|设置音频输出为听筒还是扬声器|
|isSpeakerOn|获取当前音频输出为听筒还是扬声器|
|setRecordingVolume|设置录音音量|
|setPlayOutVolume|设置播放音量|
|startAudioCapture|开启音频采集|
|startAudioCaptureAndKeepAlive|开启音频采集并保持活动状态|
|stopAudioCapture|关闭音频采集|

### **音频变声与混响** 

|**API**|**功能描述**|
|---|---|
|setAudioEffectPitchValue|设置变调参数|
|setAudioEffectVoiceChangerMode|设置变声音效模式|
|setAudioEffectReverbMode|设置混响音效模式|
|setAudioEffectBeautifyMode|设置美声音效模式|

|setAudioEffectReverbParamType|设置混响音效类型|
|---|---|
|setAudioEffectEqualizationParam|设置均衡器音效类型|

### **音效文件** 

|**API**|**功能描述**|
|---|---|
|startAudioAccompany|开始伴奏混音|
|stopAudioAccompany|停止伴奏混音|
|setAudioAccompanyVolume|设置伴奏音量|
|setAudioAccompanyPublishVolume|设置伴奏推流音量|
|getAudioAccompanyPublishVolume|获取伴奏推流音量|
|setAudioAccompanyPlayOutVolume|设置伴奏本地播放音量|
|getAudioAccompanyPlayOutVolume|获取伴奏本地播放音量|
|pauseAudioAccompany|暂停伴奏混音|
|resumeAudioAccompany|重新开始伴奏混音|
|getAudioAccompanyDuration|获取伴奏文件时长|
|getAudioAccompanyCurrentPosition|获取伴奏文件播放进度|
|setAudioAccompanyPosition|设置伴奏文件的播放位置|
|preloadAudioEffect|预加载音效文件|
|unloadAudioEffect|删除预加载的音效文件|
|playAudioEffect|开始播放音效|
|stopAudioEffect|停止播放音效|
|stopAllAudioEffects|停止播放所有音效|
|setAudioEffectPublishVolume|设置音效推流混音音量|

|getAudioEffectPublishVolume|获取音效推流混音音量|
|---|---|
|setAudioEffectPlayOutVolume|设置音效本地播放音量|
|getAudioEffectPlayoutVolume|获取音效本地播放音量|
|setAllAudioEffectsPublishVolume|设置所有音效推流混音音量|
|setAllAudioEffectsPlayoutVolume|设置所有音效本地播音量|
|pauseAudioEffect|暂停音效|
|pauseAllAudioEffects|暂停所有音效|
|resumeAudioEffect|恢复指定音效文件|
|resumeAllAudioEffects|恢复所有音效文件|

### **视频设备管理相关接口** 

|**API**|**功能描述**|
|---|---|
|setLocalViewConfig|设置本地预览显示视图|
|startPreview|开启本地视频预览|
|stopPreview|关闭本地视频预览|
|setCameraCaptureConfiguration|设置摄像头采集偏好|
|enableLocalVideo|禁用或启用本地视频采集|
|muteLocalCamera|停止/恢复本地视频数据发送|
|setRemoteViewConfig|设置远端视频显示视图|
|switchCamera|切换前后摄像头|
|getCurrentCameraDirection|获取当前摄像头方向|
|setCameraZoom|设置摄像头缩放比例|
|getCameraMaxZoomFactor|获取摄像头最大缩放比例|

|getCurrentZoom|获取摄像头缩放比例|
|---|---|
|setExposure|设置摄像头曝光度|
|getCurrentExposure|获取摄像头曝光度|
|getMinExposure|获取摄像头最小曝光度|
|getMaxExposure|获取摄像头最大曝光度|
|setCameraFlash|设置摄像头闪光灯是否打开|
|isCameraFocusPointSupported|摄像头是否支持手动聚焦|
|isCameraExposurePointSupported|摄像头是否支持设置曝光区域|
|setCameraFocusPoint|设置摄像头手动聚焦|
|setCameraExposurePoint|设置摄像头曝光点|
|isCameraOn|检查当前是否打开摄像头|

### **直播旁路接口** 

|**API**|**功能描述**|
|---|---|
|updatePublishLiveStreamWithTaskId|更新旁路直播相关参数|
|stopPublishLiveStreamWithTaskId|停止旁路直播|

### **回调事件** 

|**API**|**功能描述**|
|---|---|
|onJoinChannel|加入频道回调|
|onLeaveChannel|离开频道回调|
|onAudioPublishStateChanged|音频推流变更回调|
|onVideoPublishStateChanged|视频推流变更回调|

|onDualStreamPublishStateChanged|次要流推流变更回调|
|---|---|
|onRemoteUserOnline|远端用户(通信模式)/(互动模式,主播角色)加入频道回调|
|onRemoteUserOffline|远端用户(通信模式)/(互动模式,主播角色)离开频道回调|
|onRemoteTrackAvailableNotify|远端用户的音视频流发生变化回调|
|onAudioSubscribeStateChanged|音频订阅情况变更回调|
|onVideoSubscribeStateChanged|相机流订阅情况变更回调|
|onSubscribeStreamTypeChanged|大小流订阅情况变更回调|
|onUpdateRoleNotify|当用户角色发生变化时通知|
|onNetworkQualityChanged|网络质量变化时发出的消息|
|onConnectionStatusChange|网络连接状态改变|
|onBye|被服务器踢出/会议结束频道的消息|
|onOccurError|错误通知|
|onFirstVideoFrameReceived|收到远端用户视频首帧的回调|
|onFirstAudioPacketReceived|音频首包接收回调|
|onFirstVideoPacketReceived|视频首包接收回调|
|onFirstRemoteAudioDecoded|已解码远端音频首帧回调|
|onFirstRemoteVideoFrameDrawn|远端用户的第一帧视频帧显示时触发这个消息|
|onFirstLocalVideoFrameDrawn|预览开始显示第一帧视频帧时触发这个消息|
|onAudioVolumeCallback|订阅的音频音量回调|
|onActiveSpeaker|订阅的当前说话人|
|onUserAudioMuted|远端用户静音/取消静音回调|
|onUserVideoMuted|对端用户发送视频黑帧数据发送通知|

|onUserVideoEnabled|对端用户关闭相机流采集发送通知|
|---|---|
|onVideoTextureCreate|OpenGL上下文创建回调|
|onVideoTextureUpdate|OpenGL纹理更新回调|
|onVideoTextureDestroy|OpenGL上下文销毁回调|
|onAudioAccompanyStateChanged|本地伴奏播放状态回调|
|onRemoteAudioAccompanyStarted|远端用户伴奏播放开始回调|
|onRemoteAudioAccompanyFinished|远端用户伴奏播放结束回调|
|onAudioEffectFinished|本地音效播放结束回调|
|onAuthInfoWillExpire|用户AliEngineAuthInfo authInfo即将过期通知|
|onAuthInfoExpired|用户调用需要鉴权的接口,服务端返回信息过期|
|onStats|当前会话统计信息回调|
|onLocalVideoStats|本地视频统计信息|
|onRemoteVideoStats|远端视频统计信息|
|onLocalAudioStats|本地音频统计信息|
|onRemoteAudioStats|远端音频统计信息|
|onMediaExtensionMsgReceived|收到媒体扩展信息回调|
|onPublishLiveStreamStateChangedWithTaskI d|旁路推流状态改变回调|
|onPublishTaskStateChangedWithTaskId|旁路任务状态改变回调|
|onLocalDeviceException|本地设备异常回调|
|onDataChannelMessage|dataChannel消息回调|
|onCapturedAudioFrame|采集裸数据回调|

|onProcessCapturedAudioFrame|3A后数据回调|
|---|---|
|onPublishAudioFrame|推流数据回调|
|onPlaybackAudioFrame|播放数据回调|
|onMixedAllAudioFrame|推流数据和播放数据混音后回调|
|onRemoteUserAudioFrame|远端拉流数据回调|

### **其他接口** 

|**API**|**功能描述**|
|---|---|
|setParameter|设置自定义属性|
|getParameter|获取自定义属性|
|setExtras|设置额外参数|
|setLogLevel|设置日志等级|
|enableUploadLog|设置是否上传日志文件|
|enableAudioFrameObserver|启用音频帧监听|
|enableAudioVolumeIndication|设置音量回调频率和平滑系数|
|registerLocalVideoTexture|注册本地相机流视频OpenGL纹理数据观测器|
|unregisterLocalVideoTexture|取消注册本地相机流视频OpenGL纹理数据观测器|
|snapshotVideo|视频截图功能|
|sendMediaExtensionMsg|发送媒体扩展信息|
|getVideoCodecType|获取视频编码类型|
|getCurrentEncoderManufacturer|获取当前使用的编码器类型|
|getNetworkTime|获取时间轴时间|
|sendDataChannelMsg|发送数据消息|

## **接口详情** 

### **setRtcEngineEventListener** 

**接口描述:** 设置自身相关监听事件回调 

#### **获取接口实例:** 

public setRtcEngineEventListener(listener: AliRtcEngineEventListener | null) : void {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|listener|AliRtcEngineEventListener|用于接收来自engine的消息|

### **getInstance** 

**接口描述:** 获取 AliRtcEngine 实例 

#### **获取接口实例:** 

public static getInstance(extras: string, context : common.Context): AliRtcEngine {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|extras|string|用于接收来自客户灰度下发的参数,通过 JSON配置SDK的特别功能,可以是空字符 串|
|context|common.Context|Android上下文|

### **destroyInstance** 

**接口描述:** 销毁 AliRtcEngine 实例 

#### **获取接口实例:** 

public static destroyInstance(): void {} 

### **getSDKVersion** 

**接口描述:** 查询 SDK 当前版本号 

#### **获取接口实例:** 

public static getSDKVersion(): string {} 

### **setLogDirPath** 

**接口描述:** 设置 SDK 日志文件保存路径 

#### **获取接口实例:** 

public static setLogDirPath(logDirPath: string): number {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|logDirPath|string|日志文件保存目录的绝对路径|

### **setLogLevel** 

**接口描述:** 设置日志等级 

#### **获取接口实例:** 

public static setLogLevel(logLevel: AliRtcLogLevel): void {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|logLevel|AliRtcLogLevel|Log级别,详见AliRtcLogLevel枚举类 型|

### **enableUploadLog** 

**接口描述:** 设置是否上传日志文件,默认上传 

#### **获取接口实例:** 

public static enableUploadLog(enable: boolean): void {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|enable|boolean|true上传日志文件false不上传日志文件|

### **setH5CompatibleMode** 

**接口描述:** 设置 H5 兼容模式 

#### **获取接口实例:** 

public static setH5CompatibleMode(enable: boolean): void {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|enable|boolean|true: 兼容H5 false: 传统模式,不兼 容H5|

### **getH5CompatibleMode** 

**接口描述:** 获取 H5 兼容模式设置 

**获取接口实例:** 

public static getH5CompatibleMode(): boolean {} 

### **setAudioOnlyMode** 

**接口描述:** 设置音频模式还是音视频模式 

#### **获取接口实例:** 

public setAudioOnlyMode(audioOnly: boolean): number {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|audioOnly|boolean|true: 只有音频推流和拉流false: 音视 频都支持|

### **joinChannel** 

#### **接口描述:** 加入频道 

#### **获取接口实例:** 

public joinChannel(authInfo: AliRtcEngineAuthInfo, userName: string) : number {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|authInfo|AliRtcEngineAuthInfo|认证信息,从App Server获取|
|userName|string|任意用于显示的用户名称。不是User ID|

### **joinChannelWithToken** 

**接口描述:** 加入频道 

#### **获取接口实例:** 

public joinChannelWithToken(token: string, channelId: string, userId: string, userName: string): num ber {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|token|string|认证信息,从App Server获取|
|channelId|string|入会频道,必须和产生token时一样|
|userId|string|入会的userid,必须和产生token时一样|
|userName|string|任意用于显示的用户名称,不是User ID|

### **setParameter** 

**接口描述:** 以 JSON 字符串的格式,设置自定义属性 

#### **获取接口实例:** 

public setParameter(param: string): number {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|param|string|自定义属性参数|

### **getParameter** 

**接口描述:** 以字符串的格式,获取自定义属性 

#### **获取接口实例:** 

public getParameter(paramKey: string): string {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|paramKey|string|自定义属性参数|

### **setExtras** 

**接口描述:** 以字符串的格式,设置自定义属性 

#### **获取接口实例:** 

public setExtras(extras: string): number {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|extras|string|自定义属性参数|

### **leaveChannel** 

**接口描述:** 离开频道,即挂断或者停止通话 

#### **获取接口实例:** 

public leaveChannel(): number {} 

### **setChannelProfile** 

**接口描述:** 设置频道模式 

#### **获取接口实例:** 

public setChannelProfile(channelProfile: AliRtcChannelProfile): number {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|channelProfile|AliRtcChannelProfile|频道模式类型,详细请参考 AliRtcChannelProfile|

### **setClientRole** 

**接口描述:** 设置直播场景 AliRtcClientRole 设置为:对应的用户角色 

#### **获取接口实例:** 

public setClientRole(clientRole: AliRtcClientRole): number {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|clientRole|AliRtcClientRole|用户角色类型AliRtcClientRole|

### **getCurrentClientRole** 

**接口描述:** 获取当前用户角色 

#### **获取接口实例:** 

public getCurrentClientRole(): AliRtcClientRole {} 

### **refreshAuthInfo** 

**接口描述:** 刷新鉴权信息 

#### **获取接口实例:** 

public refreshAuthInfo(authInfo: AliRtcEngineAuthInfo): number {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|authInfo|AliRtcEngineAuthInfo|鉴权信息|

### **refreshAuthInfoWithToken** 

**接口描述:** 刷新鉴权信息 

#### **获取接口实例:** 

public refreshAuthInfoWithToken(token: string): number {} 

#### **参数表格:** 

|**参数名称参数类型参数描述**|
|---|

鉴权 token 信息; channelid 、 userid 必 须和入会时一致 

token 

string 

### **setLocalViewConfig** 

**接口描述:** 设置本地预览显示视图 

#### **获取接口实例:** 

public setLocalViewConfig(canvas: AliRtcVideoCanvas, xComponentController: AliRtcXComponentController | null, track: AliRtcVideoTrack): number {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|canvas|AliRtcVideoCanvas|本地视频显示属性|
|xComponentController|AliRtcXComponentController|XComponent视图绑定的Controller|
|track|AliRtcVideoTrack|AliRtcVideoTrack|

### **startPreview** 

**接口描述:** 开启本地视频预览 

#### **获取接口实例:** 

public startPreview(): number {} 

### **stopPreview** 

**接口描述:** 关闭本地视频预览 

#### **获取接口实例:** 

public stopPreview(): number {} 

### **setCameraCaptureConfiguration** 

**接口描述:** 设置摄像头采集偏好 

#### **获取接口实例:** 

public setCameraCaptureConfiguration(cameraCaptureConfiguration: AliRtcCameraCaptureConfiguration): number {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|cameraCaptureConfiguration|AliRtcCameraCaptureConfiguration|采集偏好设置|

### **enableLocalVideo** 

**接口描述:** 禁用或启用本地视频采集 

**接口描述:** 禁用或启用本地视频采集 

#### **获取接口实例:** 

public enableLocalVideo(enabled: boolean): number {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|enabled|boolean|true: 启用本地视频采集false: 禁用 本地视频采集|

### **muteLocalCamera** 

**接口描述:** 停止 / 恢复本地视频数据发送 

#### **获取接口实例:** 

public muteLocalCamera(mute: boolean, track: AliRtcVideoTrack): number {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|mute|boolean|true表示视频数据发送黑帧;false表示恢 复正常|
|track|AliRtcVideoTrack|只支持AliEngineVideoTrackCamera|

### **publishLocalVideoStream** 

**接口描述:** 是否推送本地视频(摄像头)流 

#### **获取接口实例:** 

public publishLocalVideoStream(enabled: boolean): number {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|enabled|boolean|true: 开启视频流推送false: 关闭视频 流推送|

### **setVideoEncoderConfiguration** 

**接口描述:** 设置相机流视频编码属性 

#### **获取接口实例:** 

public setVideoEncoderConfiguration(config: AliRtcVideoEncoderConfiguration): void {} 

#### **参数表格:** 

**参数名称 参数类型** 

**参数描述** 

预定义的编码属性 

config 

AliRtcVideoEncoderConfiguration 

### **muteLocalMic** 

**接口描述:** 停止 / 恢复本地音频数据发送 

#### **获取接口实例:** 

public muteLocalMic(mute: boolean, mode: AliRtcMuteLocalAudioMode): number {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|mute|boolean|true表示静音本地音频,发送静音帧; false表示取消静音;|
|mode|AliRtcMuteLocalAudioMode|静音模式|

### **publishLocalAudioStream** 

**接口描述:** 是否推送本地音频流 

#### **获取接口实例:** 

public publishLocalAudioStream(enabled: boolean): number {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|enabled|boolean|true: 开启音频流推送false: 关闭音频 流推送|

### **publishLocalDualAudioStream** 

**接口描述:** 是否推送次要音频流 

#### **获取接口实例:** 

public publishLocalDualAudioStream(enabled: boolean): number {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|enabled|boolean|true: 开启次要音频流推送false: 关闭 次要音频流推送|

### **setRemoteViewConfig** 

**接口描述:** 设置远端视频显示视图 **获取接口实例:** 

public setRemoteViewConfig(canvas: AliRtcVideoCanvas, xComponentController: AliRtcXComponentController | null, uid: string, track: AliRtcVideoTrack): number {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|canvas|AliRtcVideoCanvas|本地视频显示属性|
|xComponentController|AliRtcXComponentController|XComponent视图绑定的Controller|
|uid|string|用户ID,从App server分配的唯一标示符|
|track|AliRtcVideoTrack|只支持AliEngineVideoTrackCamera 和AliEngineVideoTrackScreen|

### **setRemoteAudioVolume** 

**接口描述:** 调节本地播放的指定远端用户音量 

#### **获取接口实例:** 

public setRemoteAudioVolume(uid: string, volume: number): number {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|uid|string|用户ID,从App server分配的唯一标示符|
|volume|number|播放音量,取值范围[0,100] 0:静音; 100:原始音量|

### **muteRemoteAudioPlaying** 

**接口描述:** 停止 / 恢复远端指定用户的音频流的播放 

#### **获取接口实例:** 

public muteRemoteAudioPlaying(uid: string, mute: boolean): number {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|uid|string|用户ID,从App server分配的唯一标示符|
|mute|boolean|true: 停止播放false: 恢复播放|

### **muteAllRemoteAudioPlaying** 

**接口描述:** 停止 / 恢复远端的所有音频流的播放 

**获取接口实例:** 

public muteAllRemoteAudioPlaying(mute: boolean): number {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|mute|boolean|true: 停止播放false: 恢复播放|

### **publishLocalDualStream** 

**接口描述:** 是否推送次要视频流 

#### **获取接口实例:** 

public publishLocalDualStream(enable: boolean): number {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|enable|boolean|true: 开启次要视频流推送false: 关闭 次要视频流推送|

### **setRemoteVideoStreamType** 

**接口描述:** 设置订阅的相机流格式,大流或小流 

#### **获取接口实例:** 

public setRemoteVideoStreamType(uid: string, streamType: AliRtcVideoStreamType): number {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|uid|string|用户ID,从App server分配的唯一标示符|
|streamType|AliRtcVideoStreamType|流类型|

### **setRemoteDefaultVideoStreamType** 

**接口描述:** 设置默认订阅的相机流格式,大流或小流 

#### **获取接口实例:** 

public setRemoteDefaultVideoStreamType(streamType: AliRtcVideoStreamType): number {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|streamType|AliRtcVideoStreamType|流类型|

### **subscribeAllRemoteAudioStreams** 

**接口描述:** 停止 / 恢复接收所有远端音频流 

#### **获取接口实例:** 

public subscribeAllRemoteAudioStreams(sub: boolean): number {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|sub|boolean|true: 接收所有用户的音频流false: 停 止接收所有用户的音频流|

### **subscribeAllRemoteDualAudioStreams** 

**接口描述:** 停止 / 恢复接收远端次要音频流 

#### **获取接口实例:** 

public subscribeAllRemoteDualAudioStreams(sub: boolean): number 

#### **参数表格** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|sub|boolean|true: 接收音频流 false: 停止接收音频流|

### **subscribeAllRemoteVideoStreams** 

**接口描述:** 停止 / 恢复接收所有远端视频流 

#### **获取接口实例:** 

public subscribeAllRemoteVideoStreams(sub: boolean): number 

#### **参数表格** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|sub|boolean|true: 接收所有用户的视频流false: 停 止接收所有用户的视频流|

### **subscribeRemoteAudioStream** 

#### **接口描述:** 手动拉音频流 

#### **获取接口实例:** 

public subscribeRemoteAudioStream(uid: string, sub: boolean): number {} 

#### **参数表格:** 

**参数名称** 

**参数类型** 

**参数描述** 

|uid|string|uid|
|---|---|---|
|sub|boolean|true: 接收指定用户的音频流false: 停 止接收指定用户的音频流|

### **subscribeRemoteVideoStream** 

**接口描述:** 手动拉视频流 

#### **获取接口实例:** 

public subscribeRemoteVideoStream(uid: string, track: AliRtcVideoTrack, sub: boolean): number {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|uid|string|uid|
|track|AliRtcVideoTrack|视频流类型|
|sub|boolean|true: 接收指定用户的视频流false: 停 止接收指定用户的视频流|

### **subscribeRemoteMediaStream** 

#### **接口描述:** 合并订阅远端音视频流 

#### **获取接口实例:** 

public subscribeRemoteMediaStream(uid: string, videoTrack: AliRtcVideoTrack, subVideo: boolean, subAudio: boolean): number {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|uid|string|uid|
|videoTrack|AliRtcVideoTrack|视频流类型|
|subVideo|boolean|是否订阅视频|
|subAudio|boolean|是否订阅音频|

### **subscribeRemoteDestChannelStream** 

**接口描述:** 订阅目标频道,指定用户的流 

#### **获取接口实例:** 

public subscribeRemoteDestChannelStream(channelId: string, uid: string, track: AliRtcVideoTrack, sub _audio: boolean, sub: boolean): number {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|channelId|string|目标频道|
|uid|string|用户ID,从App server分配的唯一标示符|
|track|AliRtcVideoTrack|订阅的视频流类型|
|sub_audio|boolean|是否订阅远端用户的音频流|
|sub|boolean|是否订阅远端用户的流|

### **subscribeRemoteDestChannelStreamWithTrack** 

#### **接口描述:** 订阅目标频道,指定用户的流 

#### **获取接口实例:** 

public subscribeRemoteDestChannelStreamWithTrack(channelId: string, uid: string, videoTrack: AliRtcV ideoTrack, audioTrack: AliRtcAudioTrack, sub: boolean): number {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|channelId|string|目标频道|
|uid|string|用户ID,从App server分配的唯一标示符|
|videoTrack|AliRtcVideoTrack|视频流类型|
|audioTrack|AliRtcAudioTrack|音频流类型|
|sub|boolean|是否订阅远端用户的流|

### **setDefaultSubscribeAllRemoteAudioStreams** 

**接口描述:** 设置是否默认接收音频流 

#### **获取接口实例:** 

public setDefaultSubscribeAllRemoteAudioStreams(sub: boolean): number {} 

#### **参数表格:** 

|**参数名称参数类型参数描述**|
|---|

true : 接收用户的音频流 false : 停止接 收用户的音频流 

sub 

boolean 

### **setDefaultSubscribeAllRemoteVideoStreams** 

**接口描述:** 设置是否默认订阅视频流 

#### **获取接口实例:** 

public setDefaultSubscribeAllRemoteVideoStreams(sub: boolean): number {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|sub|boolean|true:(Default)默认订阅视频流 false:默认不订阅视频流|

### **setDefaultAudioRouteToSpeakerphone** 

**接口描述:** 设置默认音频输出是否从扬声器出声,默认从扬声器出声 

#### **获取接口实例:** 

public setDefaultAudioRouteToSpeakerphone(defaultToSpeakerphone: boolean): number {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|defaultToSpeakerphone|boolean|true: 扬声器模式(默认扬声 器)false: 听筒模式|

### **enableSpeakerphone** 

#### **接口描述:** 设置音频输出为听筒还是扬声器 

#### **获取接口实例:** 

public enableSpeakerphone(enable: boolean): number {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|enable|boolean|true:扬声器模式;false:听筒模式(默 认听筒)|

### **isSpeakerOn** 

**接口描述:** 获取当前音频输出为听筒还是扬声器 **获取接口实例:** 

public isSpeakerOn(): boolean {} 

### **setRecordingVolume** 

**接口描述:** 设置录音音量 

#### **获取接口实例:** 

public setRecordingVolume(volume: number): number {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|volume|number|录音音量,取值范围[0,400] 0:静音; >100:放大音量;<100:减小音量|

### **setPlayOutVolume** 

**接口描述:** 设置播放音量 

#### **获取接口实例:** 

public setPlayOutVolume(volume: number): number {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|volume|number|播放音量,取值范围[0,400] 0:静音; >100:放大音量;<100:减小音量|

### **setAudioProfile** 

**接口描述:** 设置音频 profile 

#### **获取接口实例:** 

public setAudioProfile(profile: AliRtcAudioProfile, scenario: AliRtcAudioScenario): number {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|profile|AliRtcAudioProfile|音频采集/编码模式参数|
|scenario|AliRtcAudioScenario|音频场景模式参数|

### **switchCamera** 

**接口描述:** 切换前后摄像头 

#### **获取接口实例:** 

public switchCamera(): number {} 

### **getCurrentCameraDirection** 

#### **接口描述:** 获取当前摄像头方向 **获取接口实例:** 

getCurrentCameraDirection(): AliRtcCameraDirection {} 

### **setCameraZoom** 

**接口描述:** 设置摄像头缩放比例 

#### **获取接口实例:** 

public setCameraZoom(zoom: number): number {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|zoom|number|缩放比例|

### **getCameraMaxZoomFactor** 

**接口描述:** 获取摄像头最大缩放比例 

#### **获取接口实例:** 

public getCameraMaxZoomFactor(): number {} 

### **getCurrentZoom** 

- **接口描述:** 获取摄像头缩放比例 **获取接口实例:** 

public getCurrentZoom(): number {} 

### **setExposure** 

**接口描述:** 设置摄像头曝光度 

#### **获取接口实例:** 

public setExposure(exposure: number): number {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|exposure|number|曝光度|

### **getCurrentExposure** 

**接口描述:** 获取摄像头曝光度 

#### **获取接口实例:** 

public getCurrentExposure(): number {} 

### **getMinExposure** 

**接口描述:** 获取摄像头最小曝光度 

#### **获取接口实例:** 

public getMinExposure(): number {} 

### **getMaxExposure** 

**接口描述:** 获取摄像头最大曝光度 

#### **获取接口实例:** 

public getMaxExposure(): number {} 

### **setCameraFlash** 

**接口描述:** 设置摄像头闪光灯是否打开 

#### **获取接口实例:** 

public setCameraFlash(flash: boolean): number {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|flash|boolean|是否允许闪光灯|

### **isCameraFocusPointSupported** 

**接口描述:** 摄像头是否支持手动聚焦 

#### **获取接口实例:** 

public isCameraFocusPointSupported(): boolean {} 

### **isCameraExposurePointSupported** 

**接口描述:** 摄像头是否支持设置曝光区域 

#### **获取接口实例:** 

public isCameraExposurePointSupported(): boolean {} 

### **setCameraFocusPoint** 

**接口描述:** 设置摄像头手动聚焦 

#### **获取接口实例:** 

public setCameraFocusPoint(x: number, y: number): number {} 

#### **参数表格:** 

**参数名称 参数类型 参数描述** 

|x|number|聚焦点x坐标|
|---|---|---|
|y|number|聚焦点y坐标|

### **setCameraExposurePoint** 

#### **接口描述:** 设置摄像头曝光点 

#### **获取接口实例:** 

public setCameraExposurePoint(x: number, y: number): number {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|x|number|聚焦点x坐标|
|y|number|聚焦点y坐标|

### **startAudioCapture** 

**接口描述:** 开启音频采集 

#### **获取接口实例:** 

public startAudioCapture(): number {} 

### **startAudioCaptureAndKeepAlive** 

**接口描述:** 开启音频采集并保持采集设备开启状态 

#### **获取接口实例:** 

public startAudioCaptureAndKeepAlive(keepAlive: boolean): number {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|keepAlive|boolean|离会后采集设备是否保持开启状态|

### **stopAudioCapture** 

**接口描述:** 关闭音频采集 

#### **获取接口实例:** 

public stopAudioCapture(): number {} 

### **startAudioPlayer** 

**接口描述:** 开启音频播放设备 

**获取接口实例:** 

public startAudioPlayer(): number {} 

### **stopAudioPlayer** 

**接口描述:** 关闭音频播放 

#### **获取接口实例:** 

public stopAudioPlayer(): number {} 

### **isCameraOn** 

**接口描述:** 检查当前是否打开摄像头 

#### **获取接口实例:** 

public isCameraOn(): boolean {} 

### **isInCall** 

- **接口描述:** 获取状态:当前是否在频道中 

**获取接口实例:** 

public isInCall(): boolean {} 

### **enableAudioFrameObserver** 

**接口描述:** 启用音频帧观察者 

#### **获取接口实例:** 

public enableAudioFrameObserver(enable: boolean, audioSource: AliRtcAudioSource, config: AliRtcAudio FrameObserverConfig): number {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|enable|boolean|是否启用|
|audioSource|AliRtcAudioSource|音频源|
|config|AliRtcAudioFrameObserverConfig|音频帧观察者配置|

### **enableAudioVolumeIndication** 

**接口描述:** 设置音量回调频率和平滑系数 

#### **获取接口实例:** 

public enableAudioVolumeIndication(interval: number, smooth: number, reportVad: number): number {} 

#### **参数表格:** 

**参数名称 参数类型 参数描述** 

|interval|number|时间间隔,单位毫秒|
|---|---|---|
|smooth|number|平滑系数|
|reportVad|number|说话人检测开关1: 开启0: 关闭|

### **registerLocalVideoTexture** 

**接口描述:** 注册本地相机流视频 OpenGL 纹理数据观测器 

#### **获取接口实例:** 

public registerLocalVideoTexture(observer: AliRtcEngineVideoTextureListener): void {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|observer|AliRtcEngineVideoTextureListener|OpenGL纹理数据观测器|

### **unregisterLocalVideoTexture** 

**接口描述:** 取消注册本地相机流视频 OpenGL 纹理数据观测器 

#### **获取接口实例:** 

public unregisterLocalVideoTexture(observer: AliRtcEngineVideoTextureListener): void {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|observer|AliRtcEngineVideoTextureListener|OpenGL纹理数据观测器|

### **pauseAudioEffect** 

**接口描述:** 暂停音效 

#### **获取接口实例:** 

public pauseAudioEffect(soundId: number): number {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|soundId|number|用户给该音效文件分配的ID|

### **pauseAllAudioEffects** 

**接口描述:** 暂停所有音效 

**获取接口实例:** 

public pauseAllAudioEffects(): number {} 

### **resumeAudioEffect** 

**接口描述:** 恢复指定音效文件 

#### **获取接口实例:** 

public resumeAudioEffect(soundId: number): number {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|soundId|number|用户给该音效文件分配的ID|

### **resumeAllAudioEffects** 

**接口描述:** 恢复所有音效文件 

#### **获取接口实例:** 

public resumeAllAudioEffects(): number {} 

### **setAudioEffectPitchValue** 

**接口描述:** 设置变调参数 

#### **获取接口实例:** 

public setAudioEffectPitchValue(value: number): number {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|value|number|变调参数,范围:[0.5, 2.0],1.0表示音 调不变|

### **setAudioEffectVoiceChangerMode** 

**接口描述:** 设置变声音效模式 

#### **获取接口实例:** 

public setAudioEffectVoiceChangerMode(mode: AliRtcAudioEffectVoiceChangerMode): number {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|mode|AliRtcAudioEffectVoiceChangerMode|参考 AliRtcAudioEffectVoiceChangerMode 对应的变声音效模式值|

### **setAudioEffectReverbMode** 

#### **接口描述:** 设置混响音效模式 

#### **获取接口实例:** 

public setAudioEffectReverbMode(mode: AliRtcAudioEffectReverbMode): number {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|mode|AliRtcAudioEffectReverbMode|参考AliRtcAudioEffectReverbMode对 应的混响模式|

### **setAudioEffectBeautifyMode** 

#### **接口描述:** 设置美声音效模式 

#### **获取接口实例:** 

public setAudioEffectBeautifyMode(mode: AliRtcAudioEffectBeautifyMode): number {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|mode|AliRtcAudioEffectBeautifyMode|参考AliRtcAudioEffectBeautifyMode 对应的美声音效模式|

### **setAudioEffectReverbParamType** 

#### **接口描述:** 设置混响音效类型 

#### **获取接口实例:** 

public setAudioEffectReverbParamType(type: AliRtcAudioEffectReverbParamType, value: number): number {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|type|AliRtcAudioEffectReverbParamType|参考 AliRtcAudioEffectReverbParamType 对应的混响类型|
|value|number|混响参数值,不同混响类型的取值范围参 考 AliRtcAudioEffectReverbParamType 中取值说明|

### **setAudioEffectEqualizationParam** 

**接口描述:** 设置均衡器音效类型 

#### **获取接口实例:** 

public setAudioEffectEqualizationParam(bandIndex: AliRtcAudioEffectEqualizationBandFrequency, gain: number): number {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|bandIndex|AliRtcAudioEffectEqualizationBandFr equency|均衡器段数[0,9] center frequency [31,62,125,250,500,1000,2000,4000 ,8000,16000] Hz|
|gain|number|均衡器增益db [-15,15] default 0|

### **startAudioAccompany** 

**接口描述:** 开始伴奏混音 

#### **获取接口实例:** 

public startAudioAccompany(fileName: string, config: AliRtcAudioAccompanyConfig): number {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|fileName|string|伴奏文件名|
|config|AliRtcAudioAccompanyConfig|伴奏播放配置|

### **stopAudioAccompany** 

**接口描述:** 停止伴奏混音 

#### **获取接口实例:** 

public stopAudioAccompany(): number {} 

### **setAudioAccompanyVolume** 

**接口描述:** 设置伴奏音量 

#### **获取接口实例:** 

public setAudioAccompanyVolume(volume: number): number {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|volume|number|伴奏音量,取值范围[0,100]|

### **setAudioAccompanyPublishVolume** 

**接口描述:** 设置伴奏推流音量 

#### **获取接口实例:** 

public setAudioAccompanyPublishVolume(volume: number): number {} 

**参数表格:** 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|volume|number|伴奏推流音量,取值范围[0,100]|

### **getAudioAccompanyPublishVolume** 

**接口描述:** 获取伴奏推流音量 

#### **获取接口实例:** 

public getAudioAccompanyPublishVolume(): number {} 

### **setAudioAccompanyPlayOutVolume** 

**接口描述:** 设置伴奏本地播放音量 

#### **获取接口实例:** 

public setAudioAccompanyPlayOutVolume(volume: number): number {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|volume|number|伴奏本地播放音量,取值范围[0,100]|

### **getAudioAccompanyPlayOutVolume** 

**接口描述:** 获取伴奏本地播放音量 

#### **获取接口实例:** 

public getAudioAccompanyPlayOutVolume(): number {} 

### **pauseAudioAccompany** 

**接口描述:** 暂停伴奏混音 

#### **获取接口实例:** 

public pauseAudioAccompany(): number {} 

### **resumeAudioAccompany** 

#### **接口描述:** 重新开始伴奏混音 

#### **获取接口实例:** 

public resumeAudioAccompany(): number {} 

### **getAudioAccompanyDuration** 

**接口描述:** 获取伴奏文件时长 , 单位为毫秒 

**获取接口实例:** 

public getAudioAccompanyDuration(): number {} 

### **getAudioAccompanyCurrentPosition** 

**接口描述:** 获取伴奏文件播放进度,单位为毫秒 

#### **获取接口实例:** 

public getAudioAccompanyCurrentPosition(): number {} 

### **setAudioAccompanyPosition** 

**接口描述:** 设置伴奏文件的播放位置 

#### **获取接口实例:** 

public setAudioAccompanyPosition(volume: number): number {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|volume|number|进度条位置,单位为毫秒|

### **preloadAudioEffect** 

#### **接口描述:** 预加载音效文件 

#### **获取接口实例:** 

public preloadAudioEffect(soundId: number, filePath: string): number {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|soundId|number|用户给该音效文件分配的ID|
|filePath|string|音效文件路径,支持本地文件和网络url|

### **unloadAudioEffect** 

**接口描述:** 删除预加载的音效文件 

#### **获取接口实例:** 

public unloadAudioEffect(volume: number): number {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|volume|number|用户给该音效文件分配的ID|

### **playAudioEffect** 

**接口描述:** 开始播放音效 

#### **获取接口实例:** 

public playAudioEffect(soundId: number, filePath: string, config: AliRtcAudioEffectConfig): number { } 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|soundId|number|用户给该音效文件分配的ID|
|filePath|string|文件路径,支持本地文件和网络url|
|config|AliRtcAudioEffectConfig|音效播放配置|

### **stopAudioEffect** 

**接口描述:** 停止播放音效 

#### **获取接口实例:** 

public stopAudioEffect(volume: number): number {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|volume|number|用户给该音效文件分配的ID|

### **stopAllAudioEffects** 

**接口描述:** 停止播放所有音效 

#### **获取接口实例:** 

public stopAllAudioEffects(): number {} 

### **setAudioEffectPublishVolume** 

**接口描述:** 设置音效推流混音音量 

#### **获取接口实例:** 

public setAudioEffectPublishVolume(soundId: number, volume: number): number {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|soundId|number|用户给该音效文件分配的ID|

推流混音音量,范围是: [0, 100] ,默认 值: 50 

volume 

number 

### **getAudioEffectPublishVolume** 

**接口描述:** 获取音效推流混音音量 

#### **获取接口实例:** 

public getAudioEffectPublishVolume(soundId: number): number {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|soundId|number|用户给该音效文件分配的ID|

### **setAudioEffectPlayOutVolume** 

**接口描述:** 设置音效本地播放音量 

#### **获取接口实例:** 

public setAudioEffectPlayOutVolume(soundId: number, volume: number): number {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|soundId|number|用户给该音效文件分配的ID|
|volume|number|音效本地播放音量,范围:[0, 100],默 认值:50|

### **getAudioEffectPlayoutVolume** 

**接口描述:** 获取音效本地播放音量 

#### **获取接口实例:** 

public getAudioEffectPlayoutVolume(soundId: number): number {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|soundId|number|用户给该音效文件分配的ID|

### **setAllAudioEffectsPublishVolume** 

**接口描述:** 设置所有音效推流混音音量 

#### **获取接口实例:** 

public setAllAudioEffectsPublishVolume(soundId: number): number {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|soundId|number|用户给该音效文件分配的ID|

### **setAllAudioEffectsPlayoutVolume** 

**接口描述:** 设置所有音效本地播音量 

#### **获取接口实例:** 

public setAllAudioEffectsPlayoutVolume(soundId: number): number {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|soundId|number|用户给该音效文件分配的ID|

### **snapshotVideo** 

#### **接口描述:** 视频截图功能 

#### **获取接口实例:** 

public snapshotVideo(userId: string, trackType: AliRtcVideoTrack): number {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|userId|string|用户ID,userId为""代表本地用户|
|trackType|AliRtcVideoTrack|视频流类型,只支持 AliEngineVideoTrackCamera和 AliEngineVideoTrackScreen|

### **sendMediaExtensionMsg** 

#### **接口描述:** 发送媒体扩展信息 

#### **获取接口实例:** 

public sendMediaExtensionMsg(message: Uint8Array, repeatCount: number, delay: number, isKeyFrame: bo olean): number {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|message|Uint8Array|媒体扩展信息,长度限制为最大4K字节|

|repeatCount|number|重复次数,代表消息冗余度,用于防止网 络丢包导致的消息丢失|
|---|---|---|
|delay|number|延迟,单位毫秒,调用API后,最短多少毫 秒发送扩展信息|
|isKeyFrame|boolean|是否只有关键帧才使用扩展信息|

### **updatePublishLiveStreamWithTaskId** 

#### **接口描述:** 更新旁路直播相关参数 

#### **获取接口实例:** 

public updatePublishLiveStreamWithTaskId(taskId: string, transcoding: AliRtcLiveTranscodingParam): n umber {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|taskId|string|任务id|
|transcoding|AliRtcLiveTranscodingParam|推流所需参数|

### **stopPublishLiveStreamWithTaskId** 

#### **接口描述:** 停止旁路直播 

#### **获取接口实例:** 

public stopPublishLiveStreamWithTaskId(taskId: string): number {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|taskId|string|任务id|

### **getVideoCodecType** 

#### **接口描述:** 获取视频编码类型 

#### **获取接口实例:** 

public getVideoCodecType(codecKind: AliRtcVideoCodecKindType): AliRtcVideoFormat {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|codecKind|AliRtcVideoCodecKindType|视频codec类型:编码/解码|

### **getCurrentEncoderManufacturer** 

**接口描述:** 获取当前使用的编码器类型 , 如未开始推流,返回无效类型 

#### **获取接口实例:** 

public getCurrentEncoderManufacturer(track: AliRtcVideoTrack): AliRtcVideoCodecManufacturer {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|track|AliRtcVideoTrack|AliRtcVideoTrack|

### **getNetworkTime** 

**接口描述:** 获取时间轴时间 

#### **获取接口实例:** 

public getNetworkTime(): number {} 

### **sendDataChannelMsg** 

**接口描述:** 发送数据消息 

#### **获取接口实例:** 

public sendDataChannelMsg(controlMsg: AliRtcDataChannelMsg): number {} 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|controlMsg|AliRtcDataChannelMsg|消息内容|

### **onRemoteUserOnline** 

**接口描述:** 远端用户(通信模式) / (互动模式,主播角色)加入频道回调 

#### **回调获取接口实例:** 

onRemoteUserOnline : (func : OnRemoteUserOnLineNotify) => AliRtcEngineEventListener; 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|uid|string|用户ID,从App server分配的唯一标示符|
|online|boolean|是否上线|

### **onRemoteUserOffline** 

**接口描述:** 远端用户(通信模式) / (互动模式,主播角色)离开频道回调 

**获取接口实例:** 

onRemoteUserOffline : (func : OnRemoteUserOffLineNotify) => AliRtcEngineEventListener; 

#### **回调参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|uid|string|用户ID,从App server分配的唯一标示符|
|reason|number|用户离线的原因|

### **onJoinChannel** 

**接口描述:** 加入频道回调 

#### **获取接口实例:** 

onJoinChannel : ( func : OnJoinChannelCallback) => AliRtcEngineEventListener; 

#### **回调参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|result|number|加入频道结果,0:成功,非0:失败|
|channel|string|加入频道名|
|userId|string|用户ID|
|elapsed|number|加入频道耗时|

### **onLeaveChannel** 

**接口描述:** 离开频道回调 

#### **获取接口实例:** 

onLeaveChannel : ( func : OnLeaveChannelCallback) => AliRtcEngineEventListener; 

#### **回调参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|result|number|离开频道结果,成功返回0,失败返回错 误码|
|stats|object|本次频道内会话的数据统计信息|

### **onAudioPublishStateChanged** 

**接口描述:** 音频推流变更回调 

**获取接口实例:** 

onAudioPublishStateChanged: ( func : OnAudioPublishStateChangedCallback) => AliRtcEngineEventListener; 

#### **回调参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|audioTrack|string|流标识|
|oldState|number|之前的推流状态|
|newState|number|当前的推流状态|
|elapseSinceLastState|number|状态变更时间间隔(毫秒)|
|channel|string|当前频道|

### **onVideoPublishStateChanged** 

#### **接口描述:** 视频推流变更回调 

#### **获取接口实例:** 

onVideoPublishStateChanged: ( func : OnVideoPublishStateChangedCallback) => AliRtcEngineEventListener; 

#### **回调参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|oldState|number|之前的推流状态|
|newState|number|当前的推流状态|
|elapseSinceLastState|number|状态变更时间间隔(毫秒)|
|channel|string|当前频道|

### **onDualStreamPublishStateChanged** 

#### **接口描述:** 次要流推流变更回调 

#### **回调获取接口实例:** 

onDualStreamPublishStateChanged: ( func : OnDualStreamPublishStateChangedCallback) => AliRtcEngineE ventListener; 

#### **回调参数表格:** 

**参数名称 参数类型 参数描述** 

|oldState|number|之前的推流状态|
|---|---|---|
|newState|number|当前的推流状态|
|elapseSinceLastState|number|状态变更时间间隔(毫秒)|
|channel|string|当前频道|

### **onRemoteTrackAvailableNotify** 

**接口描述:** 远端用户的音视频流发生变化回调 

#### **获取接口实例:** 

onRemoteTrackAvailableNotify: ( func : OnRemoteTrackAvailableNotifyCallback) => AliRtcEngineEventListener; 

#### **回调参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|uid|string|用户ID,从App server分配的唯一标示符|
|audioTrack|AliRtcAudioTrack|音频流类型|
|videoTrack|AliRtcVideoTrack|视频流类型|

### **onAudioSubscribeStateChanged** 

**接口描述:** 音频订阅情况变更回调 

#### **获取接口实例:** 

onAudioSubscribeStateChanged: ( func : OnAudioSubscribeStateChangedCallback) => AliRtcEngineEventListener; 

#### **回调参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|uid|string|用户ID|
|oldState|number|之前的订阅状态|
|newState|number|当前的订阅状态|
|elapseSinceLastState|number|状态变更时间间隔(毫秒)|
|channel|string|当前频道|

### **onVideoSubscribeStateChanged** 

#### **接口描述:** 相机流订阅情况变更回调 

#### **获取接口实例:** 

onVideoSubscribeStateChanged: ( func : OnVideoSubscribeStateChangedCallback) => AliRtcEngineEventListener; 

#### **回调参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|uid|string|用户ID|
|oldState|number|之前的订阅状态|
|newState|number|当前的订阅状态|
|elapseSinceLastState|number|状态变更时间间隔(毫秒)|
|channel|string|当前频道|

### **onSubscribeStreamTypeChanged** 

**接口描述:** 大小流订阅情况变更回调 

#### **获取接口实例:** 

onSubscribeStreamTypeChanged: ( func : OnSubscribeStreamTypeChangedCallback) => AliRtcEngineEventListener; 

#### **回调参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|uid|string|用户ID|
|oldStreamType|AliRtcVideoStreamType|之前的订阅状态|
|newStreamType|AliRtcVideoStreamType|当前的订阅状态|
|elapseSinceLastState|number|状态变更时间间隔(毫秒)|
|channel|string|当前频道|

### **onNetworkQualityChanged** 

**接口描述:** 网络质量变化时发出的消息 **获取接口实例:** 

onNetworkQualityChanged: ( func : OnNetworkQualityChangedCallback) => AliRtcEngineEventListener; 

#### **回调参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|uid|string|用户ID,为空时表示本地用户上下行网络 状态|
|upQuality|AliRtcNetworkQuality|上行网络状态|
|downQuality|AliRtcNetworkQuality|下行网络状态|

### **onBye** 

#### **接口描述:** 被服务器踢出 / 会议结束频道的消息 

#### **获取接口实例:** 

onBye: ( func : OnByeCallback) => AliRtcEngineEventListener; 

#### **回调参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|code|number|原因|

### **onOccurWarning** 

**接口描述:** 警告通知 

#### **获取接口实例:** 

onOccurWarning: ( func : OnOccurWarningCallback) => AliRtcEngineEventListener; 

#### **参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|warn|number|警告类型|
|message|string|警告消息|

### **onOccurError** 

**接口描述:** 错误通知 

#### **获取接口实例:** 

onOccurError: ( func : OnOccurErrorCallback) => AliRtcEngineEventListener; 

#### **回调参数表格:** 

**参数名称** 

**参数类型** 

**参数描述** 

|error|number|错误类型|
|---|---|---|
|msg|string|错误消息|

### **onFirstRemoteVideoFrameDrawn** 

**接口描述:** 远端用户的第一帧视频帧显示时触发这个消息。 

#### **获取接口实例:** 

onFirstRemoteVideoFrameDrawn: ( func : OnFirstRemoteVideoFrameDrawnCallback) => AliRtcEngineEventListener; 

#### **回调参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|uid|string|用户ID,从App server分配的唯一标示符|
|videoTrack|AliRtcVideoTrack|视频流类型(屏幕流或者相机流)|
|width|number|视频宽度|
|height|number|视频高度|
|elapsed|number|本地用户加入频道直至该回调触发的延迟 总耗时(毫秒)|

### **onFirstLocalVideoFrameDrawn** 

**接口描述:** 预览开始显示第一帧视频帧时触发这个消息 

#### **获取接口实例:** 

onFirstLocalVideoFrameDrawn: ( func : OnFirstLocalVideoFrameDrawnCallback) => AliRtcEngineEventListener; 

#### **回调参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|width|number|本地预览视频宽度|
|height|number|本地预览视频高度|
|elapsed|number|从本地用户加入频道直至该回调触发的延 迟总耗时(毫秒)|

### **onFirstAudioPacketSend** 

**接口描述:** 音频首包发送回调 

**获取接口实例:** 

onFirstAudioPacketSend: (func: OnFirstAudioPacketSendCallback) => AliRtcEngineEventListener; 

#### **回调参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|audioTrack|AliRtcAudioTrack|接收音频track|
|timeCost|number|发送耗时,从入会开始到音频首包发送的 耗时|

### **onFirstAudioPacketReceived** 

#### **接口描述:** 音频首包接收回调 

#### **获取接口实例:** 

onFirstAudioPacketReceived: ( func : OnFirstAudioPacketReceivedCallback) => AliRtcEngineEventListener; 

#### **回调参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|uid|string|远端用户ID,从App server分配的唯一标 识符|
|track|AliRtcAudioTrack|接收音频track|
|timeCost|number|接收耗时,从入会开始到音频首包接收到 的耗时|

### **onFirstRemoteAudioDecoded** 

#### **接口描述:** 已解码远端音频首帧回调 

#### **获取接口实例:** 

onFirstRemoteAudioDecoded: ( func : OnFirstRemoteAudioDecodedCallback) => AliRtcEngineEventListener; 

#### **回调参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|uid|string|远端用户ID,从App server分配的唯一标 识符|
|track|AliRtcAudioTrack|接收音频track|
|elapsed|number|从本地用户加入频道直至该回调触发的延 迟,单位为毫秒|

### **onFirstVideoPacketSend** 

**接口描述:** 视频首包发送回调 

#### **获取接口实例:** 

onFirstVideoPacketSend: ( func : OnFirstVideoPacketSendCallback) => AliRtcEngineEventListener; 

#### **回调参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|videoTrack|AliRtcVideoTrack|接收视频track|
|timeCost|number|发送耗时,从入会开始到视频首包发送的 耗时|

### **onFirstVideoPacketReceived** 

**接口描述:** 视频首包接收回调 

#### **获取接口实例:** 

onFirstVideoPacketReceived: ( func : OnFirstVideoPacketReceivedCallback) => AliRtcEngineEventListener; 

#### **回调参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|uid|string|远端用户ID,从App server分配的唯一标 示符|
|videoTrack|AliRtcVideoTrack|接收视频track|
|timeCost|number|耗时(毫秒)|

### **onFirstVideoFrameReceived** 

**接口描述:** 收到远端用户视频首帧的回调 

#### **获取接口实例:** 

onFirstVideoFrameReceived: ( func : OnFirstVideoFrameReceivedCallback) => AliRtcEngineEventListener; 

#### **回调参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|uid|string|用户ID,从App server分配的唯一标示符|
|videoTrack|AliRtcVideoTrack|接收视频track|

耗时(毫秒) 

timeCost 

number 

### **onConnectionStatusChange** 

**接口描述:** 网络连接状态改变 

#### **获取接口实例:** 

onConnectionStatusChange: ( func : OnConnectionStatusChangeCallback) => AliRtcEngineEventListener; 

#### **回调参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|status|number|连接状态|
|reason|number|连接状态变化原因|

### **onUserAudioMuted** 

**接口描述:** 远端用户静音 / 取消静音回调 

#### **获取接口实例:** 

onUserAudioMuted: ( func : OnUserAudioMutedCallback) => AliRtcEngineEventListener; 

#### **回调参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|uid|string|远端用户ID|
|isMute|boolean|该用户是否静音true: 静音false: 取 消静音|

### **onUserVideoMuted** 

**接口描述:** 对端用户发送视频黑帧数据发送通知 

#### **获取接口实例:** 

onUserVideoMuted: ( func : OnUserVideoMutedCallback) => AliRtcEngineEventListener; 

#### **回调参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|uid|string|执行muteVideo的用户ID|
|isMute|boolean|true: 推流黑帧false: 正常推流|

### **onUserVideoEnabled** 

**接口描述:** 对端用户关闭相机流采集发送通知 

#### **获取接口实例:** 

onUserVideoEnabled: ( func : OnUserVideoEnabledCallback) => AliRtcEngineEventListener; 

#### **回调参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|uid|string|执行EnableLocalVideo的用户ID|
|isEnable|boolean|true: 打开相机流采集false: 关闭相机 流采集|

### **onRemoteAudioAccompanyStarted** 

**接口描述:** 远端用户伴奏播放开始回调 

#### **获取接口实例:** 

onRemoteAudioAccompanyStarted: ( func : OnRemoteAudioAccompanyStartedCallback) => AliRtcEngineEvent Listener; 

#### **回调参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|uid|string|远端用户ID,从App server分配的唯一标 识符|

### **onRemoteAudioAccompanyFinished** 

**接口描述:** 远端用户伴奏播放结束回调 

#### **获取接口实例:** 

onRemoteAudioAccompanyFinished: ( func : OnRemoteAudioAccompanyFinishedCallback) => AliRtcEngineEventListener; 

#### **回调参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|uid|string|远端用户ID,从App server分配的唯一标 识符|

### **onUpdateRoleNotify** 

**接口描述:** 当用户角色发生变化时通知 

#### **获取接口实例:** 

onUpdateRoleNotify: ( func : OnUpdateRoleNotifyCallback) => AliRtcEngineEventListener; 

#### **回调参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|oldRole|AliRtcClientRole|变化前角色类型|
|newRole|AliRtcClientRole|变化后角色类型|

### **onAudioVolumeCallback** 

**接口描述:** 订阅的音频音量回调 

#### **获取接口实例:** 

onAudioVolumeCallback: ( func : OnAudioVolumeCallbackCallback) => AliRtcEngineEventListener; 

#### **回调参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|volumeInfo|AliRtcVolumeInfo[]|说话人音量信息|
|volumeInfoCount|number|回调的说话人的个数|
|totalVolume|number|混音后的总音量,范围[0,255]|

### **onActiveSpeaker** 

**接口描述:** 订阅的当前说话人,当前时间段说话可能性最大的用户 uid 

#### **获取接口实例:** 

onActiveSpeaker: ( func : OnActiveSpeakerCallback) => AliRtcEngineEventListener; 

#### **回调参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|uid|string|说话人的用户ID|

### **onAudioAccompanyStateChanged** 

**接口描述:** 本地伴奏播放状态回调 

#### **获取接口实例:** 

onAudioAccompanyStateChanged: ( func : OnAudioAccompanyStateChangedCallback) => AliRtcEngineEventListener; 

#### **回调参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|type|number|当前播放状态|

播放错误码 

errorCode 

number 

### **onAudioEffectFinished** 

**接口描述:** 本地音效播放结束回调 

#### **获取接口实例:** 

onAudioEffectFinished: ( func : OnAudioEffectFinishedCallback) => AliRtcEngineEventListener; 

#### **回调参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|soundId|number|用户给该音效文件分配的唯一ID|

### **onStats** 

**接口描述:** 当前会话统计信息回调 

#### **获取接口实例:** 

onStats: ( func : OnStatsCallback) => AliRtcEngineEventListener; 

#### **回调参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|stats|AliRtcStats|会话统计信息|

### **onLocalVideoStats** 

**接口描述:** 本地视频统计信息 

#### **获取接口实例:** 

onLocalVideoStats: ( func : OnLocalVideoStatsCallback) => AliRtcEngineEventListener; 

#### **回调参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|localVideoStats|AliRtcLocalVideoStats|本地视频统计信息|

### **onRemoteVideoStats** 

**接口描述:** 远端视频统计信息 

#### **获取接口实例:** 

onRemoteVideoStats: ( func : OnRemoteVideoStatsCallback) => AliRtcEngineEventListener; 

#### **回调参数表格:** 

**参数名称** 

**参数类型** 

**参数描述** 

remoteVideoStats AliRtcRemoteVideoStats[] 远端视频统计信息 

### **onLocalAudioStats** 

**接口描述:** 本地音频统计信息 

#### **获取接口实例:** 

onLocalAudioStats: ( func : OnLocalAudioStatsCallback) => AliRtcEngineEventListener; 

#### **回调参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|localAudioStats|AliRtcLocalAudioStats|本地音频统计信息|

### **onRemoteAudioStats** 

**接口描述:** 远端音频统计信息 

#### **获取接口实例:** 

onRemoteAudioStats: ( func : OnRemoteAudioStatsCallback) => AliRtcEngineEventListener; 

#### **回调参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|remoteAudioStats|AliRtcRemoteAudioStats[]|远端音频统计信息|

### **onMediaExtensionMsgReceived** 

**接口描述:** 收到媒体扩展信息回调 

#### **获取接口实例:** 

onMediaExtensionMsgReceived: ( func : OnMediaExtensionMsgReceivedCallback) => AliRtcEngineEventListener; 

#### **回调参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|uid|string|发送用户userId|
|message|Uint8Array|扩展信息内容|
|size|number|扩展信息长度|

### **onPublishLiveStreamStateChangedWithTaskId** 

#### **接口描述:** 旁路推流状态改变回调 

#### **获取接口实例:** 

onPublishLiveStreamStateChangedWithTaskId: ( func : OnPublishLiveStreamStateChangedWithTaskIdCallback) => AliRtcEngineEventListener; 

#### **回调参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|taskId|string|任务id|
|state|number|推流状态|
|errCode|number|错误码|

### **onPublishTaskStateChangedWithTaskId** 

#### **接口描述:** 旁路任务状态改变回调 

#### **获取接口实例:** 

onPublishTaskStateChangedWithTaskId: ( func : OnPublishTaskStateChangedWithTaskIdCallback) => AliRt cEngineEventListener; 

#### **回调参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|taskId|string|任务id|
|state|number|任务状态|

### **onAuthInfoWillExpire** 

**接口描述:** 用户 AliEngineAuthInfo authInfo 即将过期通知 ,30 秒后过期 

#### **获取接口实例:** 

onAuthInfoWillExpire: ( func : OnAuthInfoWillExpireCallback) => AliRtcEngineEventListener; 

### **onAuthInfoExpired** 

**接口描述:** 用户调用需要鉴权的接口,服务端返回信息过期 

#### **获取接口实例:** 

onAuthInfoExpired: ( func : OnAuthInfoExpiredCallback) => AliRtcEngineEventListener; 

### **onLocalDeviceException** 

**接口描述:** 本地设备异常回调 

**获取接口实例** 

onLocalDeviceException: ( func : OnLocalDeviceExceptionCallback) => AliRtcEngineEventListener; 

#### **回调参数名称** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|deviceType|AliRtcDeviceType|设备类型|
|exceptionType|AliRtcDeviceExceptionType|设备异常类型|
|msg|string|异常时携带的信息|

### **onDataChannelMessage** 

**接口描述:** dataChannel 消息回调 

#### **获取接口实例** 

onDataChannelMessage: ( func : OnDataChannelMessageCallback) => AliRtcEngineEventListener; 

#### **回调参数名称** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|uid|string|用户|
|msg|string|消息|

### **onVideoResolutionChanged** 

**接口描述:** 分辨率变化回调 

#### **获取接口实例:** 

onVideoResolutionChanged: (func: OnVideoResolutionChangedCallback) => AliRtcEngineEventListener; 

#### **回调参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|uid|string|用户id|
|track|AliRtcVideoTrack|变化视频track|
|width|number|当前视频宽|
|height|number|当前视频高|

### **onVideoTextureCreate** 

**接口描述:** OpenGL 上下文创建回调 

#### **获取接口实例:** 

onVideoTextureCreate : (func : OnVideoTextureCreateFunc) => AliRtcEngineVideoTextureListener; 

#### **回调参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|context|object|OpenGL上下文|

### **onVideoTextureUpdate** 

**接口描述:** OpenGL 纹理更新回调 

#### **获取接口实例:** 

onVideoTextureUpdate : (func : OnVideoTextureUpdateFunc) => AliRtcEngineVideoTextureListener; 

#### **回调参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|textureId|number|OpenGL纹理ID|
|width|number|OpenGL纹理高|
|height|number|OpenGL纹理宽|
|videoRawData|AliEngineVideoRawData|视频帧数据,详见{@link AliEngineVideoRawData}|

### **onVideoTextureDestroy** 

**接口描述:** OpenGL 上下文销毁回调 

#### **获取接口实例:** 

onVideoTextureDestroy : (func : OnVideoTextureDestroyFunc) => AliRtcEngineVideoTextureListener; 

#### **回调参数表格:** 

|**参数名称参数类型参数描述**|
|---|

### **onCapturedAudioFrame** 

**接口描述:** 采集裸数据回调 

#### **获取接口实例:** 

onCapturedAudioFrame : (func : OnAudioFrameFunc) => AliRtcEngineAudioFrameListener; 

**回调参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|audioRawData|AliRtcAudioRawData|音频数据|

### **onProcessCapturedAudioFrame** 

**接口描述:** 3A 后数据回调 

#### **获取接口实例:** 

onProcessCapturedAudioFrame : (func : OnAudioFrameFunc) => AliRtcEngineAudioFrameListener; 

#### **回调参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|audioRawData|AliRtcAudioRawData|音频数据|

### **onPublishAudioFrame** 

**接口描述:** 推流数据回调 

#### **获取接口实例:** 

onPublishAudioFrame : (func : OnAudioFrameFunc) => AliRtcEngineAudioFrameListener; 

#### **回调参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|audioRawData|AliRtcAudioRawData|音频数据|

### **onPlaybackAudioFrame** 

**接口描述:** 播放数据回调 

#### **获取接口实例:** 

onPlaybackAudioFrame : (func : OnAudioFrameFunc) => AliRtcEngineAudioFrameListener; 

#### **回调参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|audioRawData|AliRtcAudioRawData|音频数据|

### **onMixedAllAudioFrame** 

**接口描述:** 推流数据和播放数据混音后回调 **获取接口实例:** 

onMixedAllAudioFrame : (func : OnAudioFrameFunc) => AliRtcEngineAudioFrameListener; 

#### **回调参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|audioRawData|AliRtcAudioRawData|音频数据|

### **onRemoteUserAudioFrame** 

**接口描述:** 远端拉流数据回调 

#### **获取接口实例:** 

onRemoteUserAudioFrame : (func : OnRemoteUserAudioFrameFunc) => AliRtcEngineAudioFrameListener; 

#### **回调参数表格:** 

|**参数名称**|**参数类型**|**参数描述**|
|---|---|---|
|uid|string|用户id|
|audioRawData|AliRtcAudioRawData|音频数据|
