API 概览 | 文档中心 | 声网 

2025/9/29 17:26 

文档中心 / 实时互动 / API 参考 / API 概览 

### HarmonyOS 

# **API 概览** 

复制页面

声网通过全球部署的 SD-RTNTM,提供可以灵 活搭配的 API 组合,实现质量可靠的实时音视 频通信。 

## **初始化相关** 

|方法/回调|描述|
|---|---|
|createEngine|创建并初始化 RtcEngine。|
|create|创建并初始化 RtcEngine。|
|destroy|销毁 RtcEngine 对 象。|

## **频道相关** 

|方法/回调|描述||
|---|---|---|
|setChannelProfle|设置频道 场景。||
|joinChannel|加入频 道。|**文档**|
|joinChannelWithOptions|设置媒体 选项并加 入频道。|**反馈**|
|_api_overview|加入频||

文
档
反
馈

第1/25页 

https://doc.shengwang.cn/api-ref/rtc/harmonyos/API/rtc_api_overview 

API 概览 | 文档中心 | 声网 

2025/9/29 17:26 

|joinChannelEx|道。|
|---|---|
|updateChannelMediaOptions|加入频道 后更新频 道媒体选 项。|
|updateChannelMediaOptionsEx|加入频道 后更新频 道媒体选 项 。|
|leaveChannel|设置频道 选项并离 开频道。|
|leaveChannelEx|设置频道 选项并离 开频道。|
|renewToken|更新 Token。|
|setClientRole|设置直播 场景下的 用户⻆色 和观众端 延时级 别。|
|onJoinChannelSuccess|成功加入 频道回 调。|
|onRejoinChannelSuccess|成功重新 加入频道 回调。|
|_api_overview onClientRoleChanged|用户⻆ 色、观众 端延时级|

第2/25页 

https://doc.shengwang.cn/api-ref/rtc/harmonyos/API/rtc_api_overview 

API 概览 | 文档中心 | 声网 

2025/9/29 17:26 

||别已切换 回调。|
|---|---|
|onClientRoleChangeFailed|用户⻆色 切换失败 回调。|
|onLeaveChannel|离开频道 回调。|
|onUserJoined|远端用户 (通信场 景)/主播 (直播场 景)加入 当前频道 回调。|
|onUserOfine|远端用户 (通信场 景)/主播 (直播场 景)离开 当前频道 回调。|
|onConnectionLost|网络连接 中断,且 SDK 无法 在 10 秒内 连接服务 器回调。|
|onConnectionStateChanged|网络连接 状态已改 变回调。|
|onRequestToken|Token 已 过期回 调。|
|_api_overview|Token 即|

第3/25页 

https://doc.shengwang.cn/api-ref/rtc/harmonyos/API/rtc_api_overview 

API 概览 | 文档中心 | 声网 

2025/9/29 17:26 

|onTokenPrivilegeWillExpire|将在 30s 内过期回 调。|
|---|---|
|onError|发生错误 回调。|

## **发布和订阅** 

|方法/回调|描述|
|---|---|
|muteLocalAudioStream|取消或恢 复发布本 地音频 流。|
|muteLocalAudioStreamEx|取消或恢 复发布本 地音频 流。|
|muteRemoteAudioStream|取消或恢 复订阅指 定远端用 户的音频 流。|
|muteRemoteAudioStreamEx|停止/恢复 接收指定 的音频 流。|
|muteAllRemoteAudioStreams|取消或恢 复订阅所 有远端用 户的音频 流。|
|_api_overview muteAllRemoteAudioStreamsEx|取消或恢 复订阅所 有远端用|

第4/25页 

https://doc.shengwang.cn/api-ref/rtc/harmonyos/API/rtc_api_overview 

API 概览 | 文档中心 | 声网 

2025/9/29 17:26 

||户的音频 流。|
|---|---|
|muteLocalVideoStream|取消或恢 复发布本 地视频 流。|
|muteLocalVideoStreamEx|取消或恢 复发布本 地视频 流。|
|muteRemoteVideoStream|取消或恢 复订阅指 定远端用 户的视频 流。|
|muteRemoteVideoStreamEx|停止/恢复 接收指定 的视频 流。|
|muteAllRemoteVideoStreams|取消或恢 复订阅所 有远端用 户的视频 流。|
|muteAllRemoteVideoStreamsEx|取消或恢 复订阅所 有远端用 户的视频 流。|
|onAudioPublishStateChanged|音频发布 状态改变 回调。|
|_api_overview|音频订阅 状态发生|

第5/25页 

https://doc.shengwang.cn/api-ref/rtc/harmonyos/API/rtc_api_overview 

API 概览 | 文档中心 | 声网 

2025/9/29 17:26 

|onAudioSubscribeStateChanged|改变回 调。|
|---|---|
|onVideoSubscribeStateChanged|视频订阅 状态发生 改变回 调。|

## **音频基础功能** 

|方法/回调|描述|
|---|---|
|adjustUserPlaybackSignalVolume|调节 本地 播放 的指 定远 端用 户信 号音 量。|
||调节 本地|
||播放|
|adjustUserPlaybackSignalVolumeEx|的指 定远 端用 户信 号音 量。|
|_api_overview adjustPlaybackSignalVolume|调节 本地 播放 的所 有远 端用 户信 号音|

第6/25页 

https://doc.shengwang.cn/api-ref/rtc/harmonyos/API/rtc_api_overview 

API 概览 | 文档中心 | 声网 

2025/9/29 17:26 

|量。|
|---|
|enableAudio 启用 音频 模 块。|
|disableAudio 关闭 音频 模 块。|
|enableAudioVolumeIndication 启用 用户 音量 提 示。|
|enableAudioVolumeIndicationEx 启用 用户 音量 提 示。|
|setAudioProfle 设置 音频 编码 属 性。|
|setAudioScenario 设置 音频 场 景。|
|onAudioVolumeIndication 用户 音量 提示 回 调。|
|_api_overview 本地|

第7/25页 

https://doc.shengwang.cn/api-ref/rtc/harmonyos/API/rtc_api_overview 

API 概览 | 文档中心 | 声网 

2025/9/29 17:26 

|onLocalAudioStateChanged|音频 状态 发生 改变 回 调。|
|---|---|
||远端 用户 (通 信场|
|onUserMuteAudio|景)/ 主播 (直 播场 景) 停止|
||或恢|
||复发|
||送音 频流|
||回|
||调。|
||远端 音频|
||流状|
|onRemoteAudioStateChanged|态发|
||生改 变回|
||调。|
||通话 中本 地音|
|onLocalAudioStats|频流 的统|
||计信|
||息回|
||调。|

第8/25页 

https://doc.shengwang.cn/api-ref/rtc/harmonyos/API/rtc_api_overview 

API 概览 | 文档中心 | 声网 

2025/9/29 17:26 

||通话 中远|
|---|---|
||端音|
|onRemoteAudioStats|频流 的统|
||计信|
||息回|
||调。|

## **音频采集** 

|方法/回调|描述|
|---|---|
|enableLocalAudio|开启或关闭 本地音频采 集。|
|adjustRecordingSignalVolume|调节音频采 集信号音 量。|
|enableInEarMonitoring|开启耳返功 能。|
|setInEarMonitoringVolume|设置耳返音 量。|

## **自定义音频采集和渲染** 

方法/回调 描述
创建一个自定义
createCustomAudioTrack
音频采集轨道。
销毁指定的音频
destroyCustomAudioTrack
轨道。

## **视频基础功能** 

第9/25页 

https://doc.shengwang.cn/api-ref/rtc/harmonyos/API/rtc_api_overview 

API 概览 | 文档中心 | 声网 

2025/9/29 17:26 

|方法/回调|描述|
|---|---|
|enableVideo disableVideo|启用视频 模块。 关闭视频 模块。|
|setVideoEncoderConfguration|设置视频 编码属 性。|
|setVideoEncoderConfgurationEx|设置视频 编码属 性。|
|startPreview|开启视频 预览并指 定预览的 视频源。|
|stopPreview|停止视频 预览。|
|onLocalVideoStateChanged|本地视频 状态发生 改变回 调。|
|onLocalVideoStats|本地视频 流统计信 息回调。|
|onVideoPublishStateChanged|视频发布 状态改变 回调。|
|_api_overview onVideoSizeChanged|本地或远 端视频大 小和旋转 信息发生 改变回|

第10/25页 

https://doc.shengwang.cn/api-ref/rtc/harmonyos/API/rtc_api_overview 

API 概览 | 文档中心 | 声网 

2025/9/29 17:26 

||调。|
|---|---|
|onRemoteVideoStateChanged|远端视频 状态发生 改变回 调。|
|onRemoteVideoStats|通话中远 端视频流 的统计信 息回调。|
|onFirstLocalVideoFrame|已显示本 地视频首 帧回调。|
|onUserMuteVideo|远端用户 取消或恢 复发布视 频流回 调。|
|onUserEnableVideo|远端用户 开/关视 频模块回 调。|

## **视频采集** 

|方法/回调|描述|
|---|---|
|enableLocalVideo startCameraCapture|开关本地视频采集。 开始通过摄像头采集 视频。|
|stopCameraCapture|停止通过摄像头采集 视频。|

## **屏幕共享** 

第11/25页 

https://doc.shengwang.cn/api-ref/rtc/harmonyos/API/rtc_api_overview 

API 概览 | 文档中心 | 声网 

2025/9/29 17:26 

方法/回调 描述
开始屏幕
startScreenCapture
采集。
更新屏幕
updateScreenCaptureParameters 采集的参
数配置。
停止屏幕
stopScreenCapture
采集。

## **视频前处理和后处理** 

方法/回调 描述
开启/关闭本地截
enableContentInspect
图上传。
takeSnapshot 获取视频截图。
开启虚拟背景并
enableVirtualBackground 指定媒体源,或
关闭虚拟背景。
开启/关闭本地人
enableFaceDetection
脸检测。
报告本地人脸检
onFacePositionChanged
测结果。
视频截图结果回
onSnapshotTaken
调。

## **视频编码功能** 

方法/回调 描述
在发
送端

第12/25页 

https://doc.shengwang.cn/api-ref/rtc/harmonyos/API/rtc_api_overview 

API 概览 | 文档中心 | 声网 

2025/9/29 17:26 

|setDualStreamModeEx|设置 双流 模 式。|
|---|---|
|startLocalVideoTranscoder|开启 本地 合 图。|
|stopLocalVideoTranscoder|停止 本地 合 图。|
|updateLocalTranscoderConfguration|更新 本地 合图 配 置。|
|onLocalVideoTranscoderError|本地 合图 发生 错误 回 调。|

## **视频渲染** 

方法/回调 描述
更新本地视图显示
setLocalRenderMode
模式。
更新远端视图显示
setRemoteRenderMode
模式。
setupLocalVideo 初始化本地视图。
初始化远端用户视

第13/25页 

https://doc.shengwang.cn/api-ref/rtc/harmonyos/API/rtc_api_overview 

API 概览 | 文档中心 | 声网 

2025/9/29 17:26 

|setupRemoteVideo|图。|
|---|---|
|setupRemoteVideoEx|初始化远端用户视 图。|

## **自定义视频采集和渲染** 

|方法/回调|描述|
|---|---|
|createCustomVideoTrack|创建一个自 定义的视频 轨道。|
|destroyCustomVideoTrack|销毁指定的 视频轨道。|
|setExternalVideoSource|设置外部视 频源。|
|pushExternalVideoFrameById|将外部原始 视频帧通过 自定义视频 轨道发布到 频道中。|
|pushExternalVideoFrame|推送外部原 始视频帧到 SDK。|

## **音乐文件播放** 

|方法/回调|描述|
|---|---|
|startAudioMixing|开始播放 音乐文 件。|
|stopAudioMixing|停止播放 音乐文 件。|

第14/25页 

https://doc.shengwang.cn/api-ref/rtc/harmonyos/API/rtc_api_overview 

API 概览 | 文档中心 | 声网 

2025/9/29 17:26 

|pauseAudioMixing|暂停播放 音乐文 件。|
|---|---|
|resumeAudioMixing|恢复播放 音乐文 件。|
|adjustAudioMixingVolume|调节音乐 文件的播 放音量。|
|adjustAudioMixingPlayoutVolume|调节音乐 文件在本 地播放的 音量。|
|getAudioMixingDuration|获取音乐 文件总时 长。|
|getAudioMixingCurrentPosition|获取音乐 文件的播 放进度。|
|onAudioMixingStateChanged|音乐文件 的播放状 态已改变 回调。|
|onAudioMixingPositionChanged|音乐文件 播放进度 回调。|

## **音效文件播放** 

方法/回调 描述 播放指定的本地或在 playEffect 线音效文件。 

第15/25页 

https://doc.shengwang.cn/api-ref/rtc/harmonyos/API/rtc_api_overview 

API 概览 | 文档中心 | 声网 

2025/9/29 17:26 

|stopEfect onAudioEfectFinished|停止播放指定音效文 件。 本地音效文件播放已 结束回调。|
|---|---|

## **媒体播放器** 

更多有关媒体播放器的方法,详见内置媒体播 放器。 

|方法/回调|描述|
|---|---|
|createMediaPlayer|创建媒体播放器对 象。|
|IMediaPlayer|提供媒体播放器功能 的类,支持多实例。|
|IMediaPlayerObserver|提供媒体播放器的回 调。|

## **版权音乐** 

|方法/回调|描述|
|---|---|
|initialize|初始化 IAgoraMusicContentCenter。|
|release|释放音乐内容中心所占用的所 有资源。|
|createMusicPlayer|创建音乐播放器。|
|destroyMusicPlayer|销毁音乐播放器对象。|
|preload|预加载音乐资源。|
||检测音乐资源是否已被预加|

第16/25页 

https://doc.shengwang.cn/api-ref/rtc/harmonyos/API/rtc_api_overview 

API 概览 | 文档中心 | 声网 

2025/9/29 17:26 

|2025/9/29 17:26 isPreloaded 载。|
|---|
|open 通过音乐资源编号打开音乐资 源。|
|registerEventHandler 注册音乐内容中心回调事件。|
|unregisterEventHandler 取消注册音乐内容中心事件回 调。|
|renewToken 更新 Token。|
|getCaches 获取已缓存的音乐资源信息。|
|removeCache 删除已缓存的音乐资源。|
|getMusicCharts 获取全部音乐榜单。|
|getMusicCollectionByMusicChartId 通过音乐榜单的 ID 获取指定榜 单的音乐资源列表。|
|searchMusic 搜索音乐资源。|
|setPlayMode 设置音乐资源的播放模式。|
|searchMusic 搜索音乐资源。|
|renewToken 更新 Token。|
|getLyric 获取音乐资源的歌词下载地 址。|
|getInternalSongCode 创建音乐资源的副歌片段编 号。|
|getSongSimpleInfo 获取某一音乐资源的详细信 息。|
|第17/25页 _api_overview onPreLoadEvent 报告预加载音乐资源的事件。|

https://doc.shengwang.cn/api-ref/rtc/harmonyos/API/rtc_api_overview 

API 概览 | 文档中心 | 声网 

2025/9/29 17:26 

|onLyricResult|歌词下载地址回调。|
|---|---|
|onMusicChartsResult|获取音乐榜单回调。|
|onMusicCollectionResult|获取音乐资源列表回调。|
|onSongSimpleInfoResult|音乐资源的详细信息回调。|

## **音视频录制** 

|方法/回调|描述|
|---|---|
|createMediaRecorder|创建音视频录制对象。|
|setMediaRecorderObserver|注册 IMediaRecorderCallback 观测器。|
|startRecording|开启音视频流录制。|
|stopRecording|停止音视频流录制。|
|startAudioRecording|开始客户端录音。|
|startAudioRecordingWithConfguration|开始客户端录音并进行录 音配置。|
|stopAudioRecording|停止客户端录音。|
|destroyMediaRecorder|销毁音视频录制对象。|
|onRecorderStateChanged|录制状态发生改变回调。|
|onRecorderInfoUpdated|录制信息更新回调。|

## **跨频道媒体流转发** 

|方法/回调|描述 开始|
|---|---|

第18/25页 

https://doc.shengwang.cn/api-ref/rtc/harmonyos/API/rtc_api_overview 

API 概览 | 文档中心 | 声网 

2025/9/29 17:26 

|startOrUpdateChannelMediaRelay|或更 新跨 频道|
|---|---|
||媒体 流转 发。|
|startOrUpdateChannelMediaRelayEx|开始 或更 新跨 频道|
||媒体 流转|
||发。|
||停止|
||跨频|
||道媒|
||体流|
||转|
||发。|
||一旦|
|stopChannelMediaRelay|停|
||止,|
||主播|
||会退|
||出所|
||有目|
||标频|
||道。|
||暂停|
||向所|
||有目|
|aseAllChannelMediaRela|标频|
|puy|道转|
||发媒|
||体 流。|
||恢复|
|_api_overview|向所|

第19/25页 

https://doc.shengwang.cn/api-ref/rtc/harmonyos/API/rtc_api_overview 

API 概览 | 文档中心 | 声网 

2025/9/29 17:26 

||有目|
|---|---|
|resumeAllChannelMediaRelay|标频 道转|
||发媒|
||体|
||流。|

## **旁路推流** 

|方法/回调|描述|
|---|---|
|startRtmpStreamWithTranscoding|开始旁 路推流 并设置 转码属 性。|
|updateRtmpTranscoding|更新旁 路推流 转码属 性。|
|stopRtmpStream|结束旁 路推 流。|
|onRtmpStreamingEvent|旁路推 流事件 回调。|
|onRtmpStreamingStateChanged|旁路推 流状态 发生改 变回 调。|
|onTranscodingUpdated|旁路推 流转码 设置已|
||被更新|
||回调。|

第20/25页 

https://doc.shengwang.cn/api-ref/rtc/harmonyos/API/rtc_api_overview 

API 概览 | 文档中心 | 声网 

2025/9/29 17:26 

## **数据流** 

|方法/回调|描述|
|---|---|
|createDataStream|创建数据流。|
|createDataStreamEx|创建数据流。|
|sendStreamMessage|发送数据流。|
|onStreamMessage|接收到对方数据流 消息的回调。|
|onStreamMessageError|接收对方数据流消 息发生错误的回 调。|

## **音频路由** 

|方法/回调|描述|
|---|---|
|setDefaultAudioRouteToSpeakerphone|设置 默认 的音 频路 由。|
||开启 或关|
|setEnableSpeakerphone|闭扬 声器 播 放。|
||检查|
|_api_overview isSpeakerphoneEnabled|扬声 器状 态启 用状|

第21/25页 

https://doc.shengwang.cn/api-ref/rtc/harmonyos/API/rtc_api_overview 

API 概览 | 文档中心 | 声网 

2025/9/29 17:26 

|态。|
|---|

## **视频设备管理** 

|方法/回调|描述|
|---|---|
|switchCamera|切换前 置/后 置摄像 头。|
|setCameraCapturerConfguration|设置摄 像头采 集配 置。|
|getCameraMaxZoomFactor|获取摄 像头支 持最大 缩放比 例。|
|setCameraZoomFactor|设置摄 像头缩 放比 例。|
|isCameraFocusSupported|检测设 备是否 支持手 动对焦 功能。|
|setCameraExposureFactor|设置当 前摄像 头的曝 光系 数。|
|_api_overview|设置手 动对焦|

第22/25页 

https://doc.shengwang.cn/api-ref/rtc/harmonyos/API/rtc_api_overview 

API 概览 | 文档中心 | 声网 

2025/9/29 17:26 

|setCameraFocusPositionInPreview|位置, 并触发 对焦。|
|---|---|
|onCameraExposureAreaChanged|摄像头 曝光区 域已改 变回 调。|

## **网络及其他** 

|方法/回调|描述|
|---|---|
|startLastmileProbeTest|开始通话前 网络质量探 测。|
|stopLastmileProbeTest|停止通话前 网络质量探 测。|
|onLastmileQuality|网络上下行 last mile 质量报告回 调。|
|onLastmileProbeResult|通话前网络 上下行 Last mile 质量探测报 告回调。|
|getCurrentMonotonicTimeInMs|获取 SDK 当前的 Monotonic Time。|
|_api_overview|SDK 的 JSON 配置 信息,用于|

第23/25页 

https://doc.shengwang.cn/api-ref/rtc/harmonyos/API/rtc_api_overview 

API 概览 | 文档中心 | 声网 

2025/9/29 17:26 

|setParameters|提供技术预 览或特别定 制功能。|
|---|---|
|getCallId|获取通话 ID。|
|getCallIdEx|使用连接 ID 获取通 话 ID。|
|enableEncryption|开启或关闭 内置加密。|
|onEncryptionError|内置加密出 错回调。|
|onNetworkQuality|通话中每个 用户的网络 上下行 last mile 质量 报告回调。|
|onRtcStats|当前通话相 关的统计信 息回调。|
|onPermissionError|获取设备权 限出错回 调。|

文档内
有 没
容对你
  帮   帮
是否有
助 助
帮助?

第24/25页 

https://doc.shengwang.cn/api-ref/rtc/harmonyos/API/rtc_api_overview 

API 概览 | 文档中心 | 声网 

2025/9/29 17:26 

隐私政 服务条 可接受的使用政 安全合 策 款 策 规 沪公网安备 沪ICP备 上海声网科技 31011002006829 2024090791 有限公司 号 号-1 

第25/25页 

https://doc.shengwang.cn/api-ref/rtc/harmonyos/API/rtc_api_overview
