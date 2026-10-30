|
 
 
 
|XYLINK Developer Center 易 小 |
 
 
 
 
 
 
|
|---|---|---|
|
 
 
 
|**音视频SDK_Harmony_API概览-description_html2** 小鱼 |
 
 
 
 
 
 
|
|音视频SDK_Ha 易连|rmony_API概览-description_html2 |1 |
|API概览 |
 
 
 
 
连
|2 |
|初始化 |
 
 
 
连
鱼易
|2 |
|登录 |
 
 
 
易
小
|2 连 |
|呼叫 |
 
 
 
鱼
|2 易 |
|请流&布局 |
 
 
 
小
|2 鱼 |
|媒体管理 |
 
 
 
 
|2 |
|会控操作 |
 
 
 
 
连|3
 
 
 
 
 
 
|
|录制操作 |
 
 
 
 
|3 |
|内容共享 |
 
 
 
连
|3 |
|统计信息 小|
 
 
连
易
|4 |
|其他 |
 
 
易
鱼
|4 |
|回调 |
 
 
 
 
|4 |

第 1 页/共 5 页

XYLINK Developer Center 

API 概览 

# 初始化 

|方法 小|描述 易 小鱼 |
|---|---|
|getInstance |SDK 单例(请在同一线程中使用) 小鱼 |
|init 易连|初始化 SDK 连 |
|getVersion 登录 连           小鱼|获取sdk版本 小鱼易连 小鱼易 |
|方法 鱼易连 |描述 连 |
|loginXYLinkAccount 小 |小鱼账号密码登录 易连 鱼易 |
|loginExternalAccount |三方账号登录 小鱼 小 |
|loginExtToken 易连|tokne登录 |
|loginXYAccount 小鱼|账号密码登录 连 易连 |
|loginExtUserId |authcod登录 鱼易 小鱼 |
|logout 连|退出登录 小 |

|呼叫 小鱼 |易 |
 
 
 
|
|---|---|---|
|方法 |小鱼 |描述 小 |
|makeCall 连|呼叫 |
 
 
|
|setCallMode 鱼易|更改会议模式 易连 |
易连
 
|
|hangup 小|挂断 小鱼 |
小鱼
 
|
|endMeeting 连|结束全体会议 |
 
 
|
|请流&布局 易连 |
 
 
|
易连
 
|

方法 setUnityLayoutConfig 统一layout配置 changeLayout 统一layout请流 

描述 

媒体管理

第 2 页/共 5 页 

XYLINK Developer Center 

方法 

描述 

setLocalVideoEnabled 本地视频 关闭,打开 videoMute 设置视频是否mute getLocalSourceID 获取本地视频source ID setLocalVideoFlip 设置本地镜像 switchPreviewCamera 切换系统摄像头 startAudio 开启音频 stopAudio 停止音频 isRunAudio 音频是否启动 micMute 麦克风静音 speakerMute 扬声器静音 

# 会控操作 

## 方法 

## 描述 

checkHostMeetingPermission getHostMeetingUrl speakingReq speakingEnd 

获取主持会议配置信息 获取会控地址 举手发言/取消举手 结束发言 

setNeedConsentWhenHostReqUnmute 设置会控解除静音是否需要终端同意 unmuteAsRequiredByHost 会控解除静音申请 replyMeetingControlMuteAction 终端回调会控是否开启/关闭摄像头 

录制操作 方法 startCloudRecord stopCloudRecord 

描述 开启云端录制 结束录制 

# 内容共享 

第 3 页/共 5 页 

XYLINK Developer Center 

|startContentSharing 连|方法 连 |开启内容共享 |描述 小鱼 |
|---|---|---|---|
|stopContentSharing |
 
 
 
鱼易
|停止内容共享 连 |
 
 
 
 
 
|
|startScreenCapture |
 
 
 
小
|开启屏幕录制 鱼易 |
 
 
易连
 
 
|
|stopScreenCapture |
 
 
 
|停止屏幕录制 小 |
 
 
小鱼
 
|
|updateScreenCaptureM 易连|icMute |屏幕录制是否采集音频 |
 
 
 
 
|
|putContentData 小鱼|
 
 
 
|发送content数据 鱼易连 |
 
 
易连
 
|
|统计信息 连|
 
 
 
|
 
 
 
小
|
 
 
小鱼
 
|
 
 
|方法 易连 |
 
 
连
 
|描述 |
|getStatistics |
 
 
小鱼
|获取会中简单统计 鱼易 |连 |
|getDetailStatistics |
 
 
|获取会中详细统计 小 |小鱼易 |
|其他 小鱼易连|方法 |
 
 
小鱼易连
|描述 鱼易连 |
|addDelegate 连|
 
 
|添加回调 |小 |
|removeDelegate |
 
易连
|移除回调 |
 
 
 
|
|log |
 
小鱼
|写入log 易连 |
 
 
 
|
|saveCrashFile |
 
|保存crash日志 小鱼 |
小鱼
 
|
|logUpload 连|
 
|日志上传 |
 
 
|
|getDumpFlagValue 鱼易|
 
|获取日志标识 连 |
连
 
|
|setMediaDumpMask 小|
 
|更新dump日志 鱼易 |
鱼易
 
|
|saveDump |
 
|保存详细日志dump 小 |
小
 
|
|saveAudioDump 连|
 
|保存音频dump |
 
 
|
|enableAudioDump |易连 |音频dump设置 易 |
 
 
|

# 回调 

|方法 易连 |
易连
|描述 易连|
|---|---|---|
|onNetworkStateChanged 小鱼 |网络链接 小鱼 |
 
小鱼|
|onLoginStateChanged |登录结果 |
 
|
|onKickOut 连 连|用户被踢 |
 
连|
|onCallStateChanged 鱼易|入会状态 |
 
鱼易|

第 4 页/共 5 页 

~~XYLINK Developer Center~~ 

会中请流 

onVideoStreamChanged 

会议信息 

onConfInfoChanged 会议信息 onCallInvited 点对点邀请 onCallError 会议呼叫错误 onConfInOutNotification 出入会通知 onRemoteNetworkRecv 网络状态变化 onApplySpeakingResult 申请发言回调 onSetUserNameInMeetingResult 会中改名结果回调 onConfCallModeChanged 切换会议模式回调 onNetworkIndicatorLevelChanged 本地网络质量等级 onConfPropertyChanged 会议室状态回调 onHostAuthorityChanged 主持人身份变更回调 onCoChairAuthorityChanged 联席主持人权限变更 onModifyNameAuthority 会议中改名权限变更通知 onMeetingControlEnableSort 会控排序 回调 onMeetingControlMuteActionChange 会控静音/取消静音 onMeetingControlVideoMuteActionChange 会控开启/关闭摄像头 onSpeakersChanged 会中最新发言人 onEndDynamicGroupResult 结束分组回调 

onEndDynamicGroupResult 

onHowlingDetected onRecordResult onRecordErrorResult onHostMeetingUrlResult onConfMgmtChanged 

onMeetingControlMuteResult 

是否检测到啸叫(用户可降低声音或关闭麦克风结束啸叫) 云端录制状态回调 云端录制失败回调 获取会控H5链接回调 会控状态变化回调 会控静音回调 

onGetMeetingControlConfigResult 获取主持会议的相关配置信息和状态回调 onCloudRecordPermissionChanged 云端录制权限回调 onLogUploadResult 日志上传结果回调 onScreenCaptureStop 屏幕录制结束回调 onScreenCaptureStart 屏幕录制开始回调 

onScreenCaptureStart 

第 5 页/共 5 页
