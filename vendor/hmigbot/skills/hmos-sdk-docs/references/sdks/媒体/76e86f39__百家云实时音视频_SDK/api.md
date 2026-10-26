百家云-开发文档 

https://docs.baijiayun.com/rtc/client_api/HarmonyOS/Overview.html 

## **开发者中心文档中心 (https://www.baijiayun.com/brtcDeveloperCenter) 下载中心 (/resources/docs/open/download/tpl.html)** 实时音视频 (/rtc/index.html) > 客户端 API > HarmonyOS (/rtc/client_api/HarmonyOS/Overview.html) 

## **www.baijiayun.cfrom=brtc) 注册 (https://auth?/ 登录** 

|实时音视频|**HarmonyOS**||
|---|---|---|
|产品介绍|||
|性能数据(/rtc/performance/|||
|performance.html)|API概览(/rtc/client_api/HarmonyOS/Overview.html) BRTC (/rtc/client_api/HarmonyOS/BRTC.html)||
|发版说明(/rtc/release/|BrtcListener (/rtc/client_api/HarmonyOS/BrtcListener.html) BrtcDeviceManager (/rtc/client_api/HarmonyOS/BrtcDevice|Manager.html)|
|Android.html)|枚举和类(/rtc/client_api/HarmonyOS/EnumClass.html) 常见问题(/rtc/client_api/HarmonyOS/Other.html)||
|快速入门|||
|基础功能|BRTC提供可以灵活搭配的API组合,为移动端到移动端以及移动端到Web端提供质量可靠的实时音视|频通信功能。|
|进阶功能|BRTC (/rtc/client_api/HarmonyOS/BRTC.html) BRTC功能的主要接口类||
|客户端API|BrtcListener (/rtc/client_api/HarmonyOS/BrtcListener.html) BRTC事件回调接口||
|Android (/rtc/client_api/ Android/overview.html)|BrtcDeviceManager (/rtc/client_api/HarmonyOS/BrtcDeviceManager.html) BRTC设备管理接口 枚举与类(/rtc/client_api/HarmonyOS/EnumClass.html) BRTC关键类型定义||
|iOS (/rtc/client_api/iOS/ overview.html)|**API概览**||
|小程序(/rtc/client_api/|||
|MiniProgram/overview.html)|||
|Web (/rtc/client_api/Web/ overview.html)|**创建实例和事件回调**||
|Electron (/rtc/client_api/|函数列表|描述|
|Electron/BRTC.html)|||
|C++ (/rtc/client_api/c++/|createEngine (/rtc/client_api/HarmonyOS/BRTC.html#createEngine)|创建BRTC引擎|
|overview.html)|destroyEngine (/rtc/client_api/HarmonyOS/BRTC.html#destroyEngine)|销毁BRTC引擎|
|uni-app (/rtc/client_api/uni-app/|||
|BRTC.html)|on (/rtc/client_api/HarmonyOS/BrtcListener.html)|监听事件|
|Mac (/rtc/client_api/Mac/|||

第1页 共9页 

2025/2/12 18:49 

百家云-开发文档 

https://docs.baijiayun.com/rtc/client_api/HarmonyOS/Overview.html 

## **开发者中心文档中心 (https://www.baijiayun.com/brtcDeveloperCenter) 下载中心 (/resources/docs/open/download/tpl.html) 房间相关接口函数** 

## **www.baijiayun.cfrom=brtc) 注册 (https://auth?/ 登录** 

|实时音视频|函数列表||描述|
|---|---|---|---|
|产品介绍|enterRoom (/rtc/client_api/HarmonyOS/BRTC.html#enterRoom)||进入房间|
|性能数据(/rtc/performance/ performance.html)|exitRoom (/rtc/client_api/HarmonyOS/BRTC.html#exitRoom)||离开房间|
|发版说明(/rtc/release/ Android.html)|setDefaultStreamRecvMode (/rtc/client_api/HarmonyOS/BRTC.html#s|etDefaultStreamRecvMode)|设置默认的订阅模式|
|快速入门||||
|基础功能|**视频相关接口函数**|||
|进阶功能 客户端API|函数列表|描述||
|Android (/rtc/client_api/ Android/overview.html)|startLocalPreview (/rtc/client_api/HarmonyOS/ BRTC.html#startLocalPreview)|开启本地视频的预览画面||
|iOS (/rtc/client_api/iOS/ overview.html)|stopLocalPreview (/rtc/client_api/HarmonyOS/ BRTC.html#stopLocalPreview)|停止本地视频采集及预览||
|小程序(/rtc/client_api/||||
|MiniProgram/overview.html)|muteLocalVideo (/rtc/client_api/HarmonyOS/|暂停送本地的||
|Web (/rtc/client_api/Web/|BRTC.html#muteLocalVideo)|/恢复推视频数据||
|overview.html)||||
|Electron (/rtc/client_api/ Electron/BRTC.html)|startRemoteView (/rtc/client_api/HarmonyOS/ BRTC.html#startRemoteView)|开始拉取并显示指定用户的远端画面||
|C++ (/rtc/client_api/c++/ overview.html)|stopRemoteView (/rtc/client_api/HarmonyOS/ BRTC.html#stopRemoteView)|停止显示远端视频画面,同时不再拉取|该远端用户的视频数据流|
|uni-app (/rtc/client_api/uni-app/ BRTC.html) Mac (/rtc/client_api/Mac/|muteRemoteVideo (/rtc/client_api/HarmonyOS/ BRTC.html#muteRemoteVideo)|暂停/恢复接收指定的远端视频流||

第2页 共9页 

2025/2/12 18:49 

百家云-开发文档 

https://docs.baijiayun.com/rtc/client_api/HarmonyOS/Overview.html 

|**开发者中心文档**|函数列表 **中心 (https://www.baijiayun.com/brtcDeveloperCenter)**|描述 **下载中心 (/resources/docs/open/download/tpl.html)**|**注册/登录(https://www.baijiayun.cauth?from=brtc)**|
|---|---|---|---|
|实时音视频|setVideoEncoderParam (/rtc/client_api/HarmonyOS/ BRTC.html#setVideoEncoderParam)|设置视频编码器相关参数||
|产品介绍|setNetworkQosParam (/rtc/client_api/HarmonyOS/|设置网络流控相关参数||
|性能数据(/rtc/performance/ |BRTC.html#setNetworkQosParam)|||
|performance.html)||||
|发版说明(/rtc/release/ Android.html)|setRenderParams (/rtc/client_api/HarmonyOS/ BRTC.html#setRenderParams)|设置本地或远端用户视频画面渲染模式||
|快速入门|setVideoEncoderMirror (/rtc/client_api/HarmonyOS/|设置视频编码输出的画面方向,||
|基础功能|BRTC.html#setVideoEncoderMirror)|即设置远端用户观看到的和服务器录制的画面方向||
|进阶功能|setVideoEncoderRotation (/rtc/client_api/HarmonyOS/|设置视频编码器输出的画面方向||
|客户端API|BRTC.html#setVideoEncoderRotation)|||
|Android (/rtc/client_api/ Android/overview.html)|enableSmallVideoStream (/rtc/client_api/HarmonyOS/ BRTC.html#enableSmallVideoStream)|开启大小画面双路编码模式||
|iOS (/rtc/client_api/iOS/||||
|overview.html)|setRemoteVideoStreamType (/rtc/client_api/HarmonyOS/|切换指定远端用户的大小画面||
|小程序(/rtc/client_api/|BRTC.html#setRemoteVideoStreamType)|||
|MiniProgram/overview.html)||||
|Web (/rtc/client_api/Web/||||
|overview.html)|**音频相关接口**|||
|Electron (/rtc/client_api/||||
|Electron/BRTC.html)|函数列表|描述||
|C++ (/rtc/client_api/c++/ overview.html)|startLocalAudio (/rtc/client_api/HarmonyOS/BRTC.html#startLo|calAudio) 开启本地音频的采集和上行||
|uni-app (/rtc/client_api/uni-app/ BRTC.html)|stopLocalAudio (/rtc/client_api/HarmonyOS/BRTC.html#stopLo|calAudio) 关闭本地音频的采集和上行||
|Mac (/rtc/client_api/Mac/||||

第3页 共9页 

2025/2/12 18:49 

百家云-开发文档 

https://docs.baijiayun.com/rtc/client_api/HarmonyOS/Overview.html 

|**开发者中心文档** |函数列表 muteLocalAudio (/rtc/client_api/HarmonyOS/BRTC.html#muteLocalAudio) **中心 (https://www.baijiayun.com/brtcDeveloperCenter)下载中心 (/resources/do**|描述 静音/取消静音本地的音频 **cs/open/download/tpl.html)注册/登录(https://www.baijiayunauth?from=brtc)**|
|---|---|---|
|实时音视频|||
|产品介绍|muteRemoteAudio (/rtc/client_api/HarmonyOS/BRTC.html#muteRemoteAudio)|静音/取消静音指定的远端用户的声音|
|性能数据(/rtc/performance/ performance.html)|muteAllRemoteAudio (/rtc/client_api/HarmonyOS/BRTC.html#muteAllRemoteAudio)|静音/取消静音所有远端用户的声音|
|发版说明(/rtc/release/|||
|Android.html)|**设备管理相关接口**||
|快速入门|||
|基础功能|函数列表|描述|
|进阶功能|getDeviceManager (/rtc/client_api/HarmonyOS/BRTC.html#BRTCDeviceManager)|获取设备管理类BRTCDeviceManager|
|客户端API|||
|Android (/rtc/client_api/ Android/overview.html)|**屏幕分享相关接口**||
|iOS (/rtc/client_api/iOS/ overview.html)|函数列表|描述|
|小程序(/rtc/client_api/ MiniProgram/overview.html)|startScreenCapture (/rtc/client_api/HarmonyOS/BRTC.html#startScreenCapture)|开始屏幕分享|
|Web (/rtc/client_api/Web/ overview.html)|stopScreenCapture (/rtc/client_api/HarmonyOS/BRTC.html#stopScreenCapture)|停止屏幕分享|
|Electron (/rtc/client_api/|||
|Electron/BRTC.html)|**调试相关接口函数**||
|C++ (/rtc/client_api/c++/|||
|overview.html)|函数列表|描述|
|uni-app (/rtc/client_api/uni-app/ BRTC.html)|getSdkVersion (/rtc/client_api/HarmonyOS/BRTC.html#getSdkVersion)|获取SDK版本信息|
|Mac (/rtc/client_api/Mac/|||

## **开发者中心文档中心** 函数列表 **(https://www.baijiayun.com/brtcDeveloperCenter) 下载中心 (/resources/docs/open/download/tpl.html)** 描述 **www.baijiayun.cfrom=brtc) 注册 (https://auth?/ 登录** 

第4页 共9页 

2025/2/12 18:49 

百家云-开发文档 

https://docs.baijiayun.com/rtc/client_api/HarmonyOS/Overview.html 

|**开发者中心文档**|函数列表 setLogLevel (/rtc/client_api/HarmonyOS/BRTC.html#setLogLevel) **中心 (https://www.baijiayun.com/brtcDeveloperCenter)下载中心 (/resources/docs/open**|描述 设置日志输出级别 **/download/tpl.html)注册/登录(https://www.baijiayunauth?from=brtc)**|
|---|---|---|
|实时音视频|||
|产品介绍|setConsoleEnabled (/rtc/client_api/HarmonyOS/BRTC.html#setConsoleEnabled)|启用或禁用控制台日志打印|
|性能数据(/rtc/performance/|setLogPath (/rtc/client_api/HarmonyOS/BRTC.html#setLogPath)|设置日志保存路径|
|performance.html) 发版说明(/rtc/release/|setLogListener (/rtc/client_api/HarmonyOS/BRTC.html#setLogListener)|设置日志回调|
|Android.html)|callExperimentalApi (/rtc/client_api/HarmonyOS/BRTC.html#callExperimentalApi)|调用实验性API接口|
|快速入门|||
|基础功能|**BrtcListener回调**||
|进阶功能|||
|客户端API|||
|Android (/rtc/client_api/ Android/overview.html) iOS (/rtc/client_api/iOS/|函数列表 **房间事件回调**|描述|
|overview.html)|onEnterRoom (/rtc/client_api/HarmonyOS/BrtcListener.html#onEnterRoom)|已加入房间的回调|
|小程序(/rtc/client_api/|||
|MiniProgram/overview.html)|onExitRoom (/rtc/client_api/HarmonyOS/BrtcListener.html#onExitRoom)|本地用户离开房间的事件回调|
|Web (/rtc/client_api/Web/ overview.html)|||
|Electron (/rtc/client_api/ Electron/BRTC.html)|**成员事件回调**||
|C++ (/rtc/client_api/c++/|函数列表|描述|
|overview.html)|||
|uni-app (/rtc/client_api/uni-app/|onRemoteUserEnterRoom (/rtc/client_api/HarmonyOS/BrtcListener.html#onRemoteUserEnterRoom)|远端用户加入当前房间通知|
|BRTC.html) Mac (/rtc/client_api/Mac/|onRemoteUserLeaveRoom (/rtc/client_api/HarmonyOS/BrtcListener.html#onRemoteUserLeaveRoom)|远端用户离开当前房间通知|

## **开发者中心文档中心** 函数列表 **(https://www.baijiayun.com/brtcDeveloperCenter) 下载中心 (/resources/docs/open/download/tpl.html)** 描述 **www.baijiayun.cfrom=brtc) 注册 (https://auth?/ 登录** 

第5页 共9页 

2025/2/12 18:49 

百家云-开发文档 

https://docs.baijiayun.com/rtc/client_api/HarmonyOS/Overview.html 

## **开发者中心文档中心 (https://www.baijiayun.com/brtcDeveloperCenter) 音视频事件回调** 

## **下载中心 (/resources/docs/open/download/tpl.html)** 

**www.baijiayun.cfrom=brtc) 注册 (https://auth?/ 登录** 

|实时音视频|函数列表|描述|
|---|---|---|
|产品介绍 性能数据(/rtc/performance/ |onUserVideoAvailable (/rtc/client_api/HarmonyOS/ BrtcListener.html#onUserVideoAvailable)|远端用户的视频可用或不可用状态发生状态变化时通知|
|performance.html)|onUserSubStreamAvailable (/rtc/client_api/HarmonyOS/|远端用户的辅流(通常是屏幕共享)|
|发版说明(/rtc/release/ Android.html)|BrtcListener.html#onUserSubStreamAvailable)|的可用或不可用状态发生状态变化时通知|
|快速入门 基础功能|onUserAudioAvailable (/rtc/client_api/HarmonyOS/ BrtcListener.html#onUserAudioAvailable)|远端用户的音频可用或不可用状态发生状态变化时通知|
|进阶功能|onFirstVideoFrameDecoded (/rtc/client_api/HarmonyOS/|远端用户视频首帧解码完毕回调通知|
|客户端API|BrtcListener.html#onFirstVideoFrameDecoded)||
|Android (/rtc/client_api/ Android/overview.html)|onFirstAudioFrame (/rtc/client_api/HarmonyOS/ BrtcListener.html#onFirstAudioFrame)|已接收到某个远端用户的音频首帧的回调|
|iOS (/rtc/client_api/iOS/ overview.html) 小程序(/rtc/client_api/|onSendFirstLocalVideoFrame (/rtc/client_api/HarmonyOS/ BrtcListener.html#onSendFirstLocalVideoFrame)|已发送本地视频首帧的回调|
|MiniProgram/overview.html) Web (/rtc/client_api/Web/ overview.html)|onSendFirstLocalAudioFrame (/rtc/client_api/HarmonyOS/ BrtcListener.html#onSendFirstLocalAudioFrame)|已发送本地音频首帧的回调|
|Electron (/rtc/client_api/|||
|Electron/BRTC.html) C++ (/rtc/client_api/c++/|**统计和质量回调**||
|overview.html)|函数列表|描述|
|uni-app (/rtc/client_api/uni-app/|||
|BRTC.html) Mac (/rtc/client_api/Mac/|onStatistics (/rtc/client_api/HarmonyOS/BrtcListener.html#onStatistics)|技术指标统计回调|

第6页 共9页 

2025/2/12 18:49 

百家云-开发文档 

https://docs.baijiayun.com/rtc/client_api/HarmonyOS/Overview.html 

**开发者中心文档中心 (https://www.baijiayun.com/brtcDeveloperCenter) 下载中心 (/resources/docs/open/download/tpl.html) www.baijiayun.cfrom=brtc) 注册 (https://auth?/ 登录 屏幕分享回调** 

|实时音视频|函数列表|描述||
|---|---|---|---|
|产品介绍|onScreenCaptureStarted (/rtc/client_api/HarmonyO|S/BrtcListener.html#onScreenCaptureStarted) 当屏幕分享开始时|,SDK会通过此回调通知|
|性能数据(/rtc/performance/ performance.html)|onScreenCaptureStoped (/rtc/client_api/HarmonyO|S/BrtcListener.html#onScreenCaptureStoped) 当屏幕分享停止时|,SDK会通过此回调通知|
|发版说明(/rtc/release/||||
|Android.html)||||
|快速入门|**调试信息回调**|||
|基础功能|函数列表|描述||
|进阶功能|L //lii/HOS/|||
|客户端API|onog (rtccent_aparmony BrtcListener.html#onLog)|有日志打印时的回调||
|Android (/rtc/client_api/ Android/overview.html)|onError (/rtc/client_api/HarmonyOS/|错误回调,表示SDK不可恢复的错误,||
|iOS (/rtc/client_api/iOS/|BrtcListener.html#onError)|一定要监听并分情况给用户适当的界面提示||
|overview.html)||||
|小程序(/rtc/client_api/ MiniProgram/overview.html)|**枚举**|||
|Web (/rtc/client_api/Web/||||
|overview.html)|**视频相关枚举值定义**|||
|Electron (/rtc/client_api/||||
|Electron/BRTC.html)|枚举类型|||
|C++ (/rtc/client_api/c++/||||
|overview.html)|BrtcVideoStreamType (/rtc/client_api/HarmonyOS|/EnumClass.html#BrtcVideoStreamType)|视频流类型|
|uni-app (/rtc/client_api/uni-app/ BRTC.html)|BrtcVideoResolutionMode (/rtc/client_api/Harmon|yOS/EnumClass.html#BrtcVideoResolutionMode)|视频宽高比模式|
|Mac (/rtc/client_api/Mac/||||

第7页 共9页 

2025/2/12 18:49 

百家云-开发文档 

https://docs.baijiayun.com/rtc/client_api/HarmonyOS/Overview.html 

|**开发者中心文档** 实时音视频|枚举类型 BrtcVideoRotation (/rtc/client_api/HarmonyOS/EnumClass.html#BrtcVideoRotation) **中心 (https://www.baijiayun.com/brtcDeveloperCenter)下载中心 (/resources/docs/open/dow**|视频画面旋转方向 **nload/tpl.html)注册/登录(https://www.baijiayunauth?from=brtc)**|
|---|---|---|
|产品介绍|BrtcVideoFillMode (/rtc/client_api/HarmonyOS/EnumClass.html#BrtcVideoFillMode)|视频画面填充模式|
|性能数据(/rtc/performance/|||
|performance.html)|**音频相关枚举值定义**||
|发版说明(/rtc/release/|||
|Android.html)|枚举类型||
|快速入门|||
|基础功能|BrtcAudioQuality (/rtc/client_api/HarmonyOS/EnumClass.html#BrtcAudioQuality)|声音音质|
|进阶功能|||
|客户端API|**网络相关枚举值定义**||
|Android (/rtc/client_api/|||
|Android/overview.html)|枚举类型||
|iOS (/rtc/client_api/iOS/ overview.html)|BrtcVideoQosPreference (/rtc/client_api/HarmonyOS/EnumClass.html#BrtcVideoQosPreference)|网络调整策略|
|小程序(/rtc/client_api/|||
|MiniProgram/overview.html)|||
|Web (/rtc/client_api/Web/|**其他**||
|overview.html)|||
|Electron (/rtc/client_api/|枚举类型||
|Electron/BRTC.html)|BrtcLogLevel (/rtc/client_api/HarmonyOS/EnumClass.html#BrtcLogLevel)|日志级别|
|C++ (/rtc/clientapi/c++/|||
|_ overview.html)|||
|uni-app (/rtc/client_api/uni-app/ BRTC.html)|**类**||
|Mac (/rtc/client_api/Mac/|||

## **开发者中心文档中心** 枚举类型 **(https://www.baijiayun.com/brtcDeveloperCenter) 下载中心 (/resources/docs/open/download/tpl.html) www.baijiayun.cfrom=brtc) 注册 (https://auth?/ 登录** 

第8页 共9页 

2025/2/12 18:49 

百家云-开发文档 

https://docs.baijiayun.com/rtc/client_api/HarmonyOS/Overview.html 

## **开发者中心文档中心** 类名 **(https://www.baijiayun.com/brtcDeveloperCenter) 下载中心 (/resources/docs/open/download/tpl.html)** 说明 **www.baijiayun.cfrom=brtc) 注册 (https://auth?/ 登录** 

||BrtcEngineAdvancedConfig (/rtc/client_api/HarmonyOS/EnumClass.html#BrtcEngineAdvancedConfig)|BRTC引擎配置|
|---|---|---|
|实时音视频|||
|产品介绍|BrtcRoomParams (/rtc/client_api/HarmonyOS/EnumClass.html#BrtcRoomParams)|进房参数|
|性能数据(/rtc/performance/|BrtcRenderParams (/rtc/client_api/HarmonyOS/EnumClass.html#BrtcRenderParams)|视频渲染参数|
|performance.html) 发版说明(/rtc/release/|BrtcNetworkQosParam (/rtc/client_api/HarmonyOS/EnumClass.html#BrtcNetworkQosParam)|网络流控相关参数|
|Android.html)|BrtcVideoEncParam (/rtc/client_api/HarmonyOS/EnumClass.html#BrtcVideoEncParam)|视频配置参数|
|快速入门|||
|基础功能|||
|进阶功能|||
|客户端API|||
|Android (/rtc/client_api/ Android/overview.html)|||
|iOS (/rtc/client_api/iOS/|||
|
overview.html)|||
|小程序(/rtc/client_api/ MiniProgram/overview.html)|||
|Web (/rtc/client_api/Web/ overview.html)|||
|Electron (/rtc/clientapi/|||
|_ Electron/BRTC.html)|||
|C++ (/rtc/client_api/c++/ overview.html)|||

uni-app (/rtc/client_api/uni-app/ BRTC.html) 

Mac (/rtc/client_api/Mac/ 

第9页 共9页 

2025/2/12 18:49 

百家云-开发文档 

https://docs.baijiayun.com/rtc/client_api/HarmonyOS/BRTC.html 

## **开发者中心文档中心** 实时音视频 **(https://www.baijiayun.com/brtcDeveloperCenter)** (/rtc/index.html) > 客户端 API > HarmonyOS (/rtc/client_api/HarmonyOS/Overview.html) **下载中心 (/resources/docs/open/download/tpl.html) www.baijiayun.cfrom=brtc) 注册 (https://auth?/ 登录** 

|实时音视频|**HarmonyOS**|
|---|---|
|产品介绍||
|性能数据(/rtc/performance/||
|performance.html)|API概览(/rtc/client_api/HarmonyOS/Overview.html) BRTC (/rtc/client_api/HarmonyOS/BRTC.html)|
|发版说明(/rtc/release/|BrtcListener (/rtc/client_api/HarmonyOS/BrtcListener.html) BrtcDeviceManager (/rtc/client_api/HarmonyOS/BrtcDeviceManager.html)|
|Android.html)|枚举和类(/rtc/client_api/HarmonyOS/EnumClass.html) 常见问题(/rtc/client_api/HarmonyOS/Other.html)|
|快速入门||
|基础功能|**BRTC**|
|进阶功能||
|客户端API|**基础接口**|
|Android (/rtc/client_api/ Android/overview.html)|函数列表 描述|
|iOS (/rtc/client_api/iOS/ overview.html)|createEngine 创建引擎,设置配置信息|
|小程序(/rtc/client_api/ MiniProgram/overview.html)|destroyEngine 销毁引擎|
|Web (/rtc/client_api/Web/|getSdkVersion 获取SDK版本|
|overview.html) Electron (/rtc/client_api/|callExperimentalApi 设置试验性参数|
|Electron/BRTC.html)|setDefaultStreamRecvMode 设置自动拉流模式|
|C++ (/rtc/client_api/c++/||
|overview.html)|setNetworkQosParam 设置网络自适应策略|
|uni-app (/rtc/client_api/uni-app/ BRTC.html)|on或off 监听或取消SDK回调事件|
|Mac (/rtc/client_api/Mac/||

第1页 共24页 

2025/2/12 18:50 

百家云-开发文档 

https://docs.baijiayun.com/rtc/client_api/HarmonyOS/BRTC.html 

|**开发者中心文档**|**房间相关接口中心 (https://www.baijiayun.com/brtc**|**DeveloperCenter)下载中心 (/resources/docs/open/download/tpl.html)注册/登录(https://www.baijiayunauth?from=brtc)**|
|---|---|---|
||函数列表|描述|
|实时音视频|||
||enterRoom|进入房间|
|产品介绍|||
|性能数据(/rtc/performance/|exitRoom|离开房间|
|performance.html)|||
|发版说明(/rtc/release/|**音视频相关接口**||
|Android.html)|||
|快速入门|函数列表|描述|
|基础功能|startLocalPreview|开启本地摄像头的预览画面|
|进阶功能|||
|客户端API|stopLocalPreview|停止摄像头预览|
|Android (/rtc/client_api/|startLocalAudio|开启本地音频的采集和发布|
|Android/overview.html)|||
|iOS (/rtc/client_api/iOS/|stopLocalAudio|停止本地音频的采集和发布|
|overview.html)|muteLocalAudio|暂停/恢复发布本地的音频流|
|小程序(/rtc/client_api/|||
|MiniProgram/overview.html)|muteLocalVideo|暂停/恢复发布本地的视频流|
|Web (/rtc/client_api/Web/ overview.html)|startRemoteView|订阅远端用户的视频流,并绑定视频渲染控件|
|Electron (/rtc/client_api/ Electron/BRTC.html)|stopRemoteView|停止订阅远端用户的视频流,并释放渲染控件|
|C++ (/rtc/client_api/c++/|muteRemoteAudio|暂停/恢复播放远端的音频流|
|overview.html)|||
||muteRemoteVideo|暂停/恢复订阅远端用户的视频流|
|uni-app (/rtc/client_api/uni-app/|||
|BRTC.html)|muteAllRemoteAudio|暂停/恢复播放所有远端用户的音频流|
|Mac (/rtc/client_api/Mac/|||

**www.baijiayun.cfrom=brtc) 注册 (https://auth?/ 登录** 

第2页 共24页 

2025/2/12 18:50 

百家云-开发文档 

https://docs.baijiayun.com/rtc/client_api/HarmonyOS/BRTC.html 

|**开发者中心文档**|函数列表 setVideoEncoderParam **中心 (https://www.baijiayun.com/br**|描述 设置视频编码器的编码参数 **tcDeveloperCenter)下载中心 (/resources/docs/open/download/tpl.html)注册/登录(https://www.baijiayunauth?from=brtc)**|
|---|---|---|
|实时音视频|||
|产品介绍|setVideoEncoderMirror|设置是否开启视频编码水平镜像|
|性能数据(/rtc/performance/|setVideoEncoderRotation|设置视频编码旋转角度|
|performance.html)|enableSmallVideoStream|设置是否开启推流小画面|
|发版说明(/rtc/release/|||
|Android.html)|setRemoteVideoStreamType|设置远端用户流类型(大小流切换)|
|快速入门|||
|基础功能|setRenderParams|设置本地或远端用户视频画面渲染模式|
|进阶功能|**屏幕分享相关接口**||
|客户端API|||
|Android (/rtc/client_api/|函数列表|描述|
|Android/overview.html)|||
|iOS (/rtc/client_api/iOS/|startScreenCapture|开始全系统的屏幕分享(仅支持安卓系统)|
|overview.html)|stopScreenCapture|停止屏幕分享|
|小程序(/rtc/client_api/|||
|MiniProgram/overview.html)|||
|Web (/rtc/client_api/Web/|**日志相关**||
|overview.html)|||
|Electron (/rtc/client_api/|函数列表|描述|
|Electron/BRTC.html)|setConsoleEnabled|是否将SDK日志输出到IDE控制台|
|C++ (/rtc/client_api/c++/|||
|overview.html)|setLogLevel|设置SDK输出日志级别|
|uni-app (/rtc/client_api/uni-app/ BRTC.html)|setLogPath|设置SDK保存路径|
|Mac (/rtc/client_api/Mac/|||

## **www.baijiayun.cfrom=brtc) 注册 (https://auth?/ 登录** 

第3页 共24页 

2025/2/12 18:50 

百家云-开发文档 

https://docs.baijiayun.com/rtc/client_api/HarmonyOS/BRTC.html 

## **开发者中心文档中心详细信息 (https://www.baijiayun.com/brtcDeveloperCenter) 下载中心 (/resources/docs/open/download/tpl.html)** 

## **www.baijiayun.cfrom=brtc) 注册 (https://auth?/ 登录** 

实时音视频 **createEngine** 产品介绍 创建引擎,设置配置信息 性能数据 (/rtc/performance/ performance.html) createEngine(config: BrtcEngineAdvancedConfig | null): Promise<BrtcEngineImpl | null> 发版说明 (/rtc/release/ Android.html) **参数** 快速入门 基础功能 名称 描述 进阶功能 config 创建引擎传入的配置信息。建议至少传入 ApplicationContext ,否则部分功能可能表现不正常 客户端 API Android (/rtc/client_api/ Android/overview.html) **返回** iOS (/rtc/client_api/iOS/ BRTC 引擎实例对象 overview.html) 小程序 (/rtc/client_api/ **详情** MiniProgram/overview.html) Web (/rtc/client_api/Web/ 此方法是所有功能的起点,必须获取到合法的 BRTC 引擎实例对象才能进行后续操作。 overview.html) 引擎配置信息是一个字符串数组,不同的版本支持的配置信息不同。具体参见类与枚举中的说明。 Electron (/rtc/client_api/ Electron/BRTC.html) **destroyEngine** C++ (/rtc/client_api/c++/ overview.html) 销毁 BRTC 引擎 uni-app (/rtc/client_api/uni-app/ BRTC.html) 

Mac (/rtc/client_api/Mac/ 

第4页 共24页 

2025/2/12 18:50 

百家云-开发文档 

https://docs.baijiayun.com/rtc/client_api/HarmonyOS/BRTC.html 

## **开发者中心文档中心** destroyEngine(): **(https://www.baijiayun.com/brtcDeveloperCenter)** void 

## **下载中心 (/resources/docs/open/download/tpl.html) www.baijiayun.cfrom=brtc) 注册 (https://auth?/ 登录** 

> 实时音视频 **详情** 

> 产品介绍 该方法释放 BRTC SDK 使用的所有资源 性能数据 (/rtc/performance/ 调用 destroyEngine 方法后,你将无法再使用 SDK 的其它方法和回调 

> performance.html) 如需再次使用实时音视频通信功能,你必须重新调用 createEngine 方法创建一个新的 BRTC 引擎实例 发版说明 (/rtc/release/ 由于 destroyEngine 执行释放需要一些时间,因此如果在销毁后需要再次创建 BRTC 引擎实例,建议最好控制调用频率,减少可能 

> Android.html) 存在的表现异常隐患。 快速入门 

> 基础功能 **getSdkVersion** 进阶功能 获取 SDK 版本信息 客户端 API Android (/rtc/client_api/ getSdkVersion(): string Android/overview.html) iOS (/rtc/client_api/iOS/ overview.html) **callExperimentalApi** 小程序 (/rtc/client_api/ MiniProgram/overview.html) 调用实验性 API 接口 Web (/rtc/client_api/Web/ overview.html) callExperimentalApi(jsonStr: string): void Electron (/rtc/client_api/ Electron/BRTC.html) 

> C++ (/rtc/client_api/c++/ **参数** overview.html) uni-app (/rtc/client_api/uni-app/ 名称 描述 BRTC.html) Mac (/rtc/client_api/Mac/ 

第5页 共24页 

2025/2/12 18:50 

百家云-开发文档 

https://docs.baijiayun.com/rtc/client_api/HarmonyOS/BRTC.html 

## **开发者中心文档中心** 名称 **(https://www.baijiayun.com/brtcDeveloperCenter)** 描述 **下载中心 (/resources/docs/open/download/tpl.html)** 

**www.baijiayun.cfrom=brtc) 注册 (https://auth?/ 登录** 

jsonStr 接口及参数描述的 JSON 字符串 实时音视频 产品介绍 **详情** 性能数据 (/rtc/performance/ performance.html) SDK 内部存在一些只针对特殊用户、特殊场景下的参数、方法。这些内容通常情况下,不适用于大多数普通用户,因此不会作为标准 发版说明 (/rtc/release/ 接口提供出来。如果在标准接口中未能找到您需要的功能,您可以与我们联系来确认是否在试验性接口中可以开启或者设置。 Android.html) 快速入门 **setDefaultStreamRecvMode** 基础功能 进阶功能 设置默认的订阅模式 客户端 API setDefaultStreamRecvMode(autoRecvAudio: boolean, autoRecvVideo: boolean): void Android (/rtc/client_api/ Android/overview.html) iOS (/rtc/client_api/iOS/ **详情** overview.html) 小程序 (/rtc/client_api/ 默认情况下, SDK 在感知到有远端用户推流时,会自动拉取其音视频流,并进行解码。目的是当需要播放远端用户声音和画面时,可 MiniProgram/overview.html) 以立刻播放,达到 “ 秒开 ” 的效果。但这会需要额外的带宽和计算资源。 Web (/rtc/client_api/Web/ overview.html) 您可以根据使用场景,设置不自动拉流解码,在需要播放的时候再订阅远端音视频流,缺点是播放耗时要长一些。 Electron (/rtc/client_api/ Electron/BRTC.html) **注意:需要在进入房间( enterRoom )前调用该接口,设置才能生效。** C++ (/rtc/client_api/c++/ overview.html) uni-app (/rtc/client_api/uni-app/ **参数** BRTC.html) 

Mac (/rtc/client_api/Mac/ 

第6页 共24页 

2025/2/12 18:50 

百家云-开发文档 

https://docs.baijiayun.com/rtc/client_api/HarmonyOS/BRTC.html 

|**开发者中心文档** 实时音视频|名称 描述 autoRecvAudio true表示自动订阅该远端用户的音频流, false与之相反 **中心 (https://www.baijiayun.com/brtcDeveloperCenter)下载中心 (/resources/docs/open/download/tpl.html)注册/登录(https://www.baijiayunauth?from=brtc)**|
|---|---|
|产品介绍|autoRecvVideo true表示自动订阅该远端用户的视频流, false与之相反|
|性能数据(/rtc/performance/||
|performance.html)|**setNetworkQosParam**|
|发版说明(/rtc/release/||
|Android.html)|设置网络流控相关参数|
|快速入门||
|基础功能|setNetworkQosParam(qosParam: brtc.BrtcNetworkQosParam): void|
|进阶功能||
|客户端API|**参数**|
|Android (/rtc/client_api/||
|Android/overview.html)|名称 描述|
|iOS (/rtc/client_api/iOS/ overview.html)|qosParam 网络流控参数,详见BrtcNetworkQosParam (/rtc/client_api/HarmonyOS/enumclass.html#BrtcNetworkQosParam)|
|小程序(/rtc/client_api/||
|MiniProgram/overview.html)|**详情**|
|Web (/rtc/client_api/Web/ overview.html)|该设置决定SDK在各种网络环境下的调控策略(运行条件受限下,优先选择“保清晰”或“保流畅”)|
|Electron (/rtc/client_api/||
|Electron/BRTC.html)|**on/off**|
|C++ (/rtc/client_api/c++/||
|overview.html)|设置回调接口|
|uni-app (/rtc/client_api/uni-app/||
|BRTC.html) Mac (/rtc/client_api/Mac/|on<EventType extends keyof BrtcListener>(event: EventType, callback: BrtcListener[EventType])|

## **www.baijiayun.cfrom=brtc) 注册 (https://auth?/ 登录** 

第7页 共24页 

2025/2/12 18:50 

百家云-开发文档 

https://docs.baijiayun.com/rtc/client_api/HarmonyOS/BRTC.html 

# **参数 开发者中心文档中心 (https://www.baijiayun.com/brtcDeveloperCenter) 下载中心 (/resources/docs/open/download/tpl.html)** 

## **www.baijiayun.cfrom=brtc) 注册 (https://auth?/ 登录** 

名称 描述 实时音视频 event 事件名称,必须是 BrtcListener 中提供的 产品介绍 性能数据 (/rtc/performance/ callback 用来处理该事件的方法 performance.html) 发版说明 (/rtc/release/ **详情** Android.html) 快速入门 您可以先通过 createEngine() 获得引擎实例,然后调用 engineInstance.on('event', (...) => {}) 获得来自 SDK 的各种状态、事 件通知,根据这些回调决定业务的后续动作。 基础功能 进阶功能 客户端 API **enterRoom** Android (/rtc/client_api/ Android/overview.html) 加入房间 iOS (/rtc/client_api/iOS/ enterRoom(roomParams: brtc.BrtcRoomParams): void overview.html) 小程序 (/rtc/client_api/ MiniProgram/overview.html) **参数** Web (/rtc/client_api/Web/ overview.html) 名称 描述 Electron (/rtc/client_api/ Electron/BRTC.html) roomParams 进房参数,详见 BrtcRoomParams (/rtc/client_api/HarmonyOS/enumclass.html#BrtcRoomParams) C++ (/rtc/client_api/c++/ overview.html) **详情** uni-app (/rtc/client_api/uni-app/ BRTC.html) 

必须加入房间才能发布或订阅音视频流。 “ 发布 ” 是指将自己的音、视频推送到服务器; “ 订阅 ” 是指从服务器拉取房间里其他用户的音视 Mac (/rtc/client_api/Mac/ 

第8页 共24页 

2025/2/12 18:50 

百家云-开发文档 

https://docs.baijiayun.com/rtc/client_api/HarmonyOS/BRTC.html 

频流。调用接口后,您会收到来自 BrtcListener 中的 onEnterRoom(result) 回调: **开发者中心文档中心 (https://www.baijiayun.com/brtcDeveloperCenter) 下载中心 (/resources/docs/open/download/tpl.html) www.baijiayun.cfrom=brtc) 注册 (https://auth?/ 登录** 如果加入成功,result 会是一个正数(result > 0),表示加入房间的时间消耗,单位是毫秒(ms) 实时音视频 如果加入失败,result 会是一个负数(result < 0),表示进房失败的错误码 产品介绍 不管进房是否成功, enterRoom 都必须与 exitRoom 配对使用,在调用 exitRoom 前再次调用 enterRoom 函数会导致不可预期的错误问 性能数据 (/rtc/performance/ 题。 performance.html) 发版说明 (/rtc/release/ Android.html) **exitRoom** 快速入门 离开房间 基础功能 进阶功能 exitRoom(): void 客户端 API Android (/rtc/client_api/ **详情** Android/overview.html) 调用 exitRoom 接口会执行退出房间的相关逻辑,例如释放音视频设备资源和编解码器资源等 iOS (/rtc/client_api/iOS/ overview.html) 待资源释放完毕,SDK 会通过 BrtcListener 中的 onExitRoom() 回调通知到您 如果您要再次调用 enterRoom() 或者切换到其他的音视频 SDK,请等待 onExitRoom() 回调到来之后再执行相关操作,否则可能会 小程序 (/rtc/client_api/ MiniProgram/overview.html) 遇到摄像头或麦克风被占用等各种异常问题 Web (/rtc/client_api/Web/ overview.html) **startLocalPreview** Electron (/rtc/client_api/ Electron/BRTC.html) 开启本地视频的预览画面 C++ (/rtc/client_api/c++/ overview.html) startLocalPreview(useFront: boolean): void uni-app (/rtc/client_api/uni-app/ BRTC.html) 

Mac (/rtc/client_api/Mac/ 

第9页 共24页 

2025/2/12 18:50 

百家云-开发文档 

https://docs.baijiayun.com/rtc/client_api/HarmonyOS/BRTC.html 

# **参数 开发者中心文档中心 (https://www.baijiayun.com/brtcDeveloperCenter) 下载中心 (/resources/docs/open/download/tpl.html)** 

## **www.baijiayun.cfrom=brtc) 注册 (https://auth?/ 登录** 

|实时音视频|名称 描述|
|---|---|
|产品介绍|useFront true:开启前置摄像头;false:开启后置摄像头|
|性能数据(/rtc/performance/ performance.html)|**详情**|
|发版说明(/rtc/release/ Android.html) 快速入门|请在enterRoom之后调用此函数 此方法调用后,会打开摄像头,请确保您的应用程序申请了摄像头访问权限|
|基础功能|**注意**|
|进阶功能||
|客户端API|与其他端的SDK不同,HarmonyOS SDK不需要您设置渲染视图对象。您只需要遵守命名规则(/rtc/client_api/|
|Android (/rtc/client_api/ Android/overview.html)|HarmonyOS/Other.html#XcomponentNameRule)在您的页面上创建XComponent控件即可。 目前尚不支持在进入房间前调用此方法,建议您在收到onEnterRoom回调中来调用|
|iOS (/rtc/client_api/iOS/ overview.html) 小程序(/rtc/client_api/|如果当前正在屏幕共享,且设置的流类型是BrtcVideoStreamTypeBig,调用此接口后,将会停止屏幕共享,恢复 显示摄像头画面|
|MiniProgram/overview.html)||
|Web (/rtc/client_api/Web/ overview.html)|**stopLocalPreview**|
|Electron (/rtc/client_api/ Electron/BRTC.html)|停止本地视频采集及预览|
|C++ (/rtc/client_api/c++/ overview.html)|stopLocalPreview(): void|
|uni-app (/rtc/client_api/uni-app/ BRTC.html)||
|Mac (/rtc/client_api/Mac/|**startLocalAudio**|

第10页 共24页 

2025/2/12 18:50 

百家云-开发文档 

https://docs.baijiayun.com/rtc/client_api/HarmonyOS/BRTC.html 

## 开启本地音频的采集和上行 **开发者中心文档中心 (https://www.baijiayun.com/brtcDeveloperCenter)** 

## **下载中心 (/resources/docs/open/download/tpl.html)** 

**www.baijiayun.cfrom=brtc) 注册 (https://auth?/ 登录** 

startLocalAudio(quality: brtc.BrtcAudioQuality): void 

### 实时音视频 

# **参数** 

> 产品介绍 **参数** 性能数据 (/rtc/performance/ 

> performance.html) 名称 描述 发版说明 (/rtc/release/ Android.html) quality 声音音质,详见 BrtcAudioQuality (/rtc/client_api/HarmonyOS/EnumClass.html#BrtcAudioQuality) 快速入门 基础功能 **详情** 

> 进阶功能 SDK 默认不会采集您的麦克风声音数据,您需要主动调用该函数来开启麦克风采集,并将音频数据传输给房间里的其他用户 客户端 API 请确保您的应用程序已经申请了麦克风权限。可以参考华为开发者中心的申请应用权限 (https://developer.huawei.com/consumer/ cn/doc/harmonyos-guides-V5/request-app-permissions-V5) 的介绍来完成权限申请。 Android (/rtc/client_api/ Android/overview.html) 

> iOS (/rtc/client_api/iOS/ **stopLocalAudio** overview.html) 小程序 (/rtc/client_api/ 关闭本地音频的采集和上行 MiniProgram/overview.html) Web (/rtc/client_api/Web/ stopLocalAudio(): void overview.html) Electron (/rtc/client_api/ 

> Electron/BRTC.html) **详情** C++ (/rtc/client_api/c++/ 调用此方法,会停止传递本地麦克风音频数据给房间里其他用户,并释放对麦克风设备的占用 overview.html) uni-app (/rtc/client_api/uni-app/ BRTC.html) 

# **muteLocalAudio** 

Mac (/rtc/client_api/Mac/ 

第11页 共24页 

2025/2/12 18:50 

百家云-开发文档 

https://docs.baijiayun.com/rtc/client_api/HarmonyOS/BRTC.html 

## 静音 / 取消静音本地的音频 **开发者中心文档中心 (https://www.baijiayun.com/brtcDeveloperCenter) 下载中心 (/resources/docs/open/download/tpl.html)** 

## **www.baijiayun.cfrom=brtc) 注册 (https://auth?/ 登录** 

muteLocalAudio(mute: boolean): void 

### 实时音视频 

# **参数** 

> 产品介绍 **参数** 性能数据 (/rtc/performance/ 

> performance.html) 名称 描述 发版说明 (/rtc/release/ Android.html) mute true :静音; false :取消静音 快速入门 基础功能 **详情** 

> 进阶功能 当静音本地音频后,房间里的其它成员会收到 onUserAudioAvailable(userId, false) 回调通知 客户端 API 当取消静音本地音频后,房间里的其它成员会收到 onUserAudioAvailable(userId, true) 回调通知 与 stopLocalAudio 不同之处在于,muteLocalAudio(true) 并不会释放对麦克风设备的占用,只是同步一个状态,服务器将不再下发 Android (/rtc/client_api/ 音频数据给房间里的其它成员 Android/overview.html) iOS (/rtc/client_api/iOS/ overview.html) **muteLocalVideo** 小程序 (/rtc/client_api/ MiniProgram/overview.html) 暂停 / 恢复推送本地的视频数据 Web (/rtc/client_api/Web/ overview.html) muteLocalVideo(streamType: brtc.BrtcVideoStreamType, mute: boolean): void Electron (/rtc/client_api/ Electron/BRTC.html) C++ (/rtc/client_api/c++/ **参数** overview.html) uni-app (/rtc/client_api/uni-app/ 名称 描述 BRTC.html) streamType 流类型,参见 BrtcVideoStreamType (/rtc/client_api/HarmonyOS/EnumClass.html#BrtcVideoStreamType) Mac (/rtc/client_api/Mac/ 

第12页 共24页 

2025/2/12 18:50 

百家云-开发文档 

https://docs.baijiayun.com/rtc/client_api/HarmonyOS/BRTC.html 

## **开发者中心文档中心** 名称 **(https://www.baijiayun.com/brtcDeveloperCenter)** 描述 **下载中心 (/resources/docs/open/download/tpl.html)** 

## **www.baijiayun.cfrom=brtc) 注册 (https://auth?/ 登录** 

mute true :暂停; false :恢复 实时音视频 产品介绍 **详情** 性能数据 (/rtc/performance/ performance.html) 该接口可以暂停(或恢复)发布本地的视频画面,暂停之后,同一房间中的其他用户将无法继续看到自己的画面。调用此接口,并不 发版说明 (/rtc/release/ 会操作物理摄像头设备,比较适合频繁开关视频的场景。 Android.html) 快速入门 注意:如果您还调用了 startScreenCapture 接口启动了屏幕共享,并设置了 streamType 是 基础功能 BrtcVideoStreamTypeSub ,此时摄像头和屏幕共享将会是两个独立的视频流在发布。在这种情况下,调用此接口, 进阶功能 只作用于摄像头流。 客户端 API 当暂停推送本地视频后,房间里的其它成员将会收到 onUserVideoAvailable(userid, false) 回调通知 Android (/rtc/client_api/ 当恢复推送本地视频后,房间里的其它成员将会收到 onUserVideoAvailable(userid, true) 回调通知 Android/overview.html) iOS (/rtc/client_api/iOS/ overview.html) **startRemoteView** 小程序 (/rtc/client_api/ MiniProgram/overview.html) 开始拉取并显示指定用户的远端画面 Web (/rtc/client_api/Web/ overview.html) startRemoteView(userId: string, streamType: brtc.BrtcVideoStreamType) Electron (/rtc/client_api/ Electron/BRTC.html) **参数** C++ (/rtc/client_api/c++/ overview.html) 名称 描述 uni-app (/rtc/client_api/uni-app/ BRTC.html) userId 远端用户 ID Mac (/rtc/client_api/Mac/ 

第13页 共24页 

2025/2/12 18:50 

百家云-开发文档 

https://docs.baijiayun.com/rtc/client_api/HarmonyOS/BRTC.html 

## **开发者中心文档中心** 名称 **(https://www.baijiayun.com/brtcDeveloperCenter)** 描述 **下载中心 (/resources/docs/open/download/tpl.html)** 

## **www.baijiayun.cfrom=brtc) 注册 (https://auth?/ 登录** 

streamType 流类型,参见 BrtcVideoStreamType (/rtc/client_api/HarmonyOS/EnumClass.html#BrtcVideoStreamType) 

实时音视频 产品介绍 **详情** 性能数据 (/rtc/performance/ 与其他端的 SDK 不同,HarmonyOS SDK 不需要您设置渲染视图对象。您只需要遵守命名规则 (/rtc/client_api/HarmonyOS/ performance.html) Other.html#XcomponentNameRule)在您的页面上创建 XComponent 控件即可。 发版说明 (/rtc/release/ 您必须在等待来自 SDK 的 onUserVideoAvailable(userId, true) 回调通知后再调用此方法来显示远端用户的视频 Android.html) SDK 支持同时观看某 userid 的大画面和辅路,或者小画面和辅路,但不支持同时观看大画面和小画面 快速入门 只有当指定的 userid 通过 enableSmallVideoStream() 开启双路编码后,才能观看该用户的小画面 基础功能 如果该用户的小画面不存在,则默认显示大画面 进阶功能 客户端 API **stopRemoteView** Android (/rtc/client_api/ Android/overview.html) 停止显示远端视频画面,同时不再拉取该远端用户的视频数据流 iOS (/rtc/client_api/iOS/ overview.html) stopRemoteView(userId: string, streamType: brtc.BrtcVideoStreamType) 小程序 (/rtc/client_api/ MiniProgram/overview.html) **参数** Web (/rtc/client_api/Web/ overview.html) 名称 描述 Electron (/rtc/client_api/ Electron/BRTC.html) userId 远端用户 ID C++ (/rtc/client_api/c++/ overview.html) streamType 流类型,参见 BrtcVideoStreamType (/rtc/client_api/HarmonyOS/EnumClass.html#BrtcVideoStreamType) uni-app (/rtc/client_api/uni-app/ BRTC.html) **详情** Mac (/rtc/client_api/Mac/ 

第14页 共24页 

2025/2/12 18:50 

百家云-开发文档 

https://docs.baijiayun.com/rtc/client_api/HarmonyOS/BRTC.html 

调用此接口后, SDK 会清理关联到该远端用户的相关视频显示资源 **开发者中心文档中心 (https://www.baijiayun.com/brtcDeveloperCenter) 下载中心 (/resources/docs/open/download/tpl.html) www.baijiayun.cfrom=brtc) 注册 (https://auth?/ 登录** 

调用此接口后,无论在手动订阅模式还是自动订阅模式下,都会停止接收该远端用户的视频流。区别是: 实时音视频 在手动订阅模式下,会释放掉该用户视频流相关的全部资源。如果需要再次恢复显示,需要重新发起订阅。 产品介绍 在自动订阅模式下,不需要重新订阅,再次恢复显示,画面显示速度更快。 性能数据 (/rtc/performance/ performance.html) 发版说明 (/rtc/release/ **muteRemoteAudio** Android.html) 快速入门 静音 / 取消静音指定的远端用户的声音 基础功能 进阶功能 muteRemoteAudio(userId: string, mute: boolean): void 客户端 API Android (/rtc/client_api/ **参数** Android/overview.html) iOS (/rtc/client_api/iOS/ 名称 描述 overview.html) userId 远端用户 ID 小程序 (/rtc/client_api/ MiniProgram/overview.html) mute true :静音; false :取消静音 Web (/rtc/client_api/Web/ overview.html) Electron (/rtc/client_api/ **详情** Electron/BRTC.html) 当您静音某用户的远端音频时,SDK 会停止播放指定用户的声音。 C++ (/rtc/client_api/c++/ 自动订阅模式下,还会继续拉取该远端用户的音频数据。需要恢复播放时速度较快。 overview.html) 手动订阅模式下,会停止拉取该用户的音频数据数据。恢复播放的速度比自动订阅模式下稍慢一些。 uni-app (/rtc/client_api/uni-app/ 在调用了 muteAllRemoteAudio 后,仍然可以调用此方法单独针对某一个当前已订阅的远端用户进行设置 BRTC.html) 

Mac (/rtc/client_api/Mac/ 

第15页 共24页 

2025/2/12 18:50 

百家云-开发文档 

https://docs.baijiayun.com/rtc/client_api/HarmonyOS/BRTC.html 

### 实时音视频 

# **muteRemoteVideo 开发者中心文档中心 (https://www.baijiayun.com/brtcDeveloperCenter)** 

## 暂停 / 恢复接收指定的远端视频流 

## **下载中心 (/resources/docs/open/download/tpl.html)** 

## **www.baijiayun.cfrom=brtc) 注册 (https://auth?/ 登录** 

muteRemoteVideo(userId: string, streamType: brtc.BrtcVideoStreamType, mute: boolean): void 产品介绍 性能数据 (/rtc/performance/ performance.html) **参数** 发版说明 (/rtc/release/ Android.html) 名称 描述 快速入门 userId 远端用户 ID 基础功能 进阶功能 streamType 流类型,参见 BrtcVideoStreamType (/rtc/client_api/HarmonyOS/EnumClass.html#BrtcVideoStreamType) 客户端 API mute true :暂停; false :恢复 Android (/rtc/client_api/ Android/overview.html) **详情** iOS (/rtc/client_api/iOS/ overview.html) 该接口仅暂停/恢复接收指定的远端用户的视频流,但并不释放显示资源 小程序 (/rtc/client_api/ 手动订阅模式下,如果是首次针对此远端用户调用此方法并设置 mute 为 false,会自动订阅该远端用户的流 MiniProgram/overview.html) 当设置 mute 为 true 时: Web (/rtc/client_api/Web/ 自动订阅模式下,调用此方法不会停止拉取视频流数据,也不会停止解码 overview.html) 手动订阅模式下,调用此方法,服务器会停止下发视频流数据 Electron (/rtc/client_api/ Electron/BRTC.html) 

C++ (/rtc/client_api/c++/ overview.html) 

# **muteAllRemoteAudio** 

> uni-app (/rtc/client_api/uni-app/ 静音 / 取消静音所有用户的声音 BRTC.html) 

Mac (/rtc/client_api/Mac/ 

第16页 共24页 

2025/2/12 18:50 

百家云-开发文档 

https://docs.baijiayun.com/rtc/client_api/HarmonyOS/BRTC.html 

## **开发者中心文档中心** muteAllRemoteAudio(mute: **(https://www.baijiayun.com/brtcDeveloperCenter)** boolean): void 

**下载中心 (/resources/docs/open/download/tpl.html) www.baijiayun.cfrom=brtc) 注册 (https://auth?/ 登录** 

|实时音视频|**参数**|
|---|---|
|产品介绍||
|性能数据(/rtc/performance/|名称 描述|
|performance.html)|mute true:静音;false:取消静音|
|发版说明(/rtc/release/||
|Android.html)||
|快速入门|**详情**|
|基础功能|mute设置为true时,会停止播放所有远端用户的音频流|
|进阶功能|mute设置为false时,会恢复播放所有远端用户的音频流|
|客户端API Adid /t/liti/|注意:当设置mute为false时,会自动拉取所有远端用户的音频流。因此,在手动订阅模式下,建议谨慎使用此接|
|nro (rccen_ap Android/overview.html)|口。|
|iOS (/rtc/client_api/iOS/||
|overview.html)||
|小程序(/rtc/client_api/|**setVideoEncoderParam**|
|MiniProgram/overview.html)||
|Web (/rtc/client_api/Web/|设置视频编码器相关参数|
|overview.html)||
|Electron (/rtc/client_api/|setVideoEncoderParam(encParam: brtc.BrtcVideoEncParam): void|
|Electron/BRTC.html)||
|C++ (/rtc/client_api/c++/ overview.html)|**参数**|
|uni-app (/rtc/client_api/uni-app/ BRTC.html)|名称 描述|
|Mac (/rtc/client_api/Mac/||

第17页 共24页 

2025/2/12 18:50 

百家云-开发文档 

https://docs.baijiayun.com/rtc/client_api/HarmonyOS/BRTC.html 

## **开发者中心文档中心** 名称 **(https://www.baijiayun.com/brtcDeveloperCenter)** 描述 **下载中心 (/resources/docs/open/download/tpl.html)** 

## **www.baijiayun.cfrom=brtc) 注册 (https://auth?/ 登录** 

encParam 视频编码参数,详情 BrtcVideoEncParam (/rtc/client_api/HarmonyOS/EnumClass.html#BrtcVideoEncParam) 实时音视频 产品介绍 **详情** 性能数据 (/rtc/performance/ 该设置决定了远端用户看到的画面质量(同时也是云端录制出的视频文件的画面质量) performance.html) 发版说明 (/rtc/release/ Android.html) **setVideoEncoderMirror** 快速入门 基础功能 设置编码器输出的画面镜像模式 进阶功能 setVideoEncoderMirror(mirror: boolean): void 客户端 API Android (/rtc/client_api/ Android/overview.html) **参数** iOS (/rtc/client_api/iOS/ overview.html) 名称 描述 小程序 (/rtc/client_api/ mirror true :开启远端画面水平镜像; false :关闭远端画面水平镜像,默认值: false MiniProgram/overview.html) Web (/rtc/client_api/Web/ overview.html) **详情** Electron (/rtc/client_api/ 该接口不改变本地摄像头的预览画面,但会改变另一端用户看到的(以及服务器录制的)画面效果 Electron/BRTC.html) 即便是在推流过程中,您也可以随时调用此接口来改变编码的镜像效果 C++ (/rtc/client_api/c++/ 该接口只针对于主画面有效。如果当前同时在推流摄像头和屏幕共享流,则只有摄像头会有镜像效果 overview.html) uni-app (/rtc/client_api/uni-app/ BRTC.html) **setVideoEncoderRotation** Mac (/rtc/client_api/Mac/ 

第18页 共24页 

2025/2/12 18:50 

百家云-开发文档 

https://docs.baijiayun.com/rtc/client_api/HarmonyOS/BRTC.html 

## 设置视频编码器输出的画面方向 **开发者中心文档中心 (https://www.baijiayun.com/brtcDeveloperCenter) 下载中心 (/resources/docs/open/download/tpl.html)** 

## **www.baijiayun.cfrom=brtc) 注册 (https://auth?/ 登录** 

setVideoEncoderRotation(rotation: brtc.BrtcVideoRotation): void 

实时音视频 产品介绍 **参数** 性能数据 (/rtc/performance/ performance.html) 名称 描述 发版说明 (/rtc/release/ Android.html) roation 旋转角度。参见 BrtcVideoRotation (/rtc/client_api/HarmonyOS/EnumClass.html#BrtcVideoRotation) 快速入门 基础功能 **详情** 进阶功能 该设置不影响本地画面的预览方向,但会影响房间中其他用户所观看到(以及云端录制文件)的画面方向。 客户端 API Android (/rtc/client_api/ Android/overview.html) **enableSmallVideoStream** iOS (/rtc/client_api/iOS/ overview.html) 开启大小画面双路编码模式 小程序 (/rtc/client_api/ MiniProgram/overview.html) enableSmallVideoStream(enable: boolean, encParam: brtc.BrtcVideoEncParam): void Web (/rtc/client_api/Web/ overview.html) **参数** Electron (/rtc/client_api/ Electron/BRTC.html) 名称 描述 C++ (/rtc/client_api/c++/ overview.html) enable true :开启; false :不开启,默认值: false uni-app (/rtc/client_api/uni-app/ BRTC.html) encParam 详见详情 BrtcVideoEncParam (/rtc/client_api/HarmonyOS/EnumClass.html#BrtcVideoEncParam) Mac (/rtc/client_api/Mac/ 

该设置不影响本地画面的预览方向,但会影响房间中其他用户所观看到(以及云端录制文件)的画面方向。 

第19页 共24页 

2025/2/12 18:50 

百家云-开发文档 

https://docs.baijiayun.com/rtc/client_api/HarmonyOS/BRTC.html 

**开发者中心文档中心详情 (https://www.baijiayun.com/brtcDeveloperCenter) 下载中心 (/resources/docs/open/download/tpl.html) www.baijiayun.cfrom=brtc) 注册 (https://auth?/ 登录** 开启该模式后,当前用户会同时编码输出【高清大画面】和【低清小画面】两个规格的视频画面(但只有一路音频流) 实时音视频 对于开启该模式的当前用户,会占用更多的网络带宽,并且会消耗更多的 CPU 计算资源 对于同一房间的远程观众而言: 产品介绍 如果下行网络很好,或者显示区域较大,可以选择观看【高清大画面】 性能数据 (/rtc/performance/ 如果下行网络较差,或者显示区域较小,可以选择观看【低清小画面】 performance.html) 发版说明 (/rtc/release/ 考虑到同时编码两个规格的视频画面,需要更多的计算资源,在硬件设备较差的系统上请谨慎开启此功能 Android.html) 快速入门 基础功能 **setRemoteVideoStreamType** 进阶功能 切换指定远端用户的大小画面 客户端 API Android (/rtc/client_api/ setRemoteVideoStreamType(userId: string, streamType: brtc.BrtcVideoStreamType) Android/overview.html) iOS (/rtc/client_api/iOS/ overview.html) **参数** 小程序 (/rtc/client_api/ MiniProgram/overview.html) 名称 描述 Web (/rtc/client_api/Web/ overview.html) userId 用于指定要观看的 userId Electron (/rtc/client_api/ streamType 流类型,参见 BrtcVideoStreamType (/rtc/client_api/HarmonyOS/EnumClass.html#BrtcVideoStreamType) Electron/BRTC.html) C++ (/rtc/client_api/c++/ overview.html) **详情** uni-app (/rtc/client_api/uni-app/ 只有在远端用户调用 enableSmallVideoStream 提前开启双路编码模式,切换动作才有效果 BRTC.html) 在不通过此接口进行设置的情况下,默认订阅的视频画面为大画面 Mac (/rtc/client_api/Mac/ 

第20页 共24页 

2025/2/12 18:50 

百家云-开发文档 

https://docs.baijiayun.com/rtc/client_api/HarmonyOS/BRTC.html 

# **setRenderParams 开发者中心文档中心 (https://www.baijiayun.com/brtcDeveloperCenter)** 

## **下载中心 (/resources/docs/open/download/tpl.html)** 

## 设置视频画面的渲染参数 

实时音视频 setRenderParams(userId: string, streamType: brtc.BrtcVideoStreamType, params: brtc.BrtcRenderParams) 产品介绍 性能数据 (/rtc/performance/ performance.html) **参数** 发版说明 (/rtc/release/ Android.html) 名称 描述 快速入门 userId 本地或远端用户的 userId 基础功能 进阶功能 streamType 流类型,参见 BrtcVideoStreamType (/rtc/client_api/HarmonyOS/EnumClass.html#BrtcVideoStreamType) 客户端 API params 渲染参数,详见 BrtcRenderParams (/rtc/client_api/HarmonyOS/EnumClass.html#BrtcRenderParams) Android (/rtc/client_api/ Android/overview.html) **详情** iOS (/rtc/client_api/iOS/ overview.html) 可设置的参数包括有:画面的填充模式、旋转角度(待开放)以及镜像模式(待开放)等。 小程序 (/rtc/client_api/ MiniProgram/overview.html) Web (/rtc/client_api/Web/ overview.html) **startScreenCapture** Electron (/rtc/client_api/ Electron/BRTC.html) 开始屏幕分享 C++ (/rtc/client_api/c++/ overview.html) startScreenCapture(xComponentSurfaceId:string, streamType: brtc.BrtcVideoStreamType, encParam: brtc.BrtcVideoEncParam): void uni-app (/rtc/client_api/uni-app/ BRTC.html) Mac (/rtc/client_api/Mac/ 

**www.baijiayun.cfrom=brtc) 注册 (https://auth?/ 登录** 

第21页 共24页 

2025/2/12 18:50 

百家云-开发文档 

https://docs.baijiayun.com/rtc/client_api/HarmonyOS/BRTC.html 

# **参数 开发者中心文档中心 (https://www.baijiayun.com/brtcDeveloperCenter) 下载中心 (/resources/docs/open/download/tpl.html)** 

## **www.baijiayun.cfrom=brtc) 注册 (https://auth?/ 登录** 

|实时音视频|名称 描述|
|---|---|
|产品介绍|xComponentSurfaceId (1.0.0尚不支持)用于回显屏幕共享的XComponent控件的surfaceId。|
|性能数据(/rtc/performance/ fhtl|streamType 流类型,参见BrtcVideoStreamType (/rtc/client_api/HarmonyOS/EnumClass.html#BrtcVideoStreamType)|
|perormance.m)||
|发版说明(/rtc/release/|encParam 屏幕共享编码参数。参考:BrtcVideoEncParam (/rtc/client_api/HarmonyOS/EnumClass.html#BrtcVideoEncParam)|
|Android.html)||
|快速入门|**详情**|
|基础功能|如果设置streamType是BrtcVideoStreamType.BIG,屏幕共享将会替换当前主摄像头流(如有),否则将独立于主摄像头流单独|
|进阶功能|推送一路辅流。|
|客户端API||
|Android (/rtc/client_api/ Android/overview.html)|**stopScreenCapture**|
|iOS (/rtc/client_api/iOS/ overview.html)|停止屏幕采集|
|小程序(/rtc/client_api/ MiniProgram/overview.html)|stopScreenCapture(): void|
|Web (/rtc/client_api/Web/||
|overview.html) Electron (/rtc/client_api/ Electron/BRTC.html)|**setConsoleEnabled**|
|C++ (/rtc/client_api/c++/|启用或禁用控制台日志打印(在DevEco Studio中,控制台可以理解为是Log面板)|
|overview.html) uni-app (/rtc/client_api/uni-app/|setConsoleEnabled(enabled: boolean): void|
|BRTC.html)||
|Mac (/rtc/client_api/Mac/||

第22页 共24页 

2025/2/12 18:50 

百家云-开发文档 

https://docs.baijiayun.com/rtc/client_api/HarmonyOS/BRTC.html 

## **开发者中心文档中心参数 (https://www.baijiayun.com/brtcDeveloperCenter) 下载中心 (/resources/docs/open/download/tpl.html) www.baijiayun.cfrom=brtc) 注册 (https://auth?/ 登录** 

|实时音视频|名称 描述|
|---|---|
|产品介绍|enabled 指定是否启用,默认为禁止。如果不调用,SDK默认行为是启用|
|性能数据(/rtc/performance/||
|performance.html)|**setLogLevel**|
|发版说明(/rtc/release/||
|Android.html)||
|快速入门|设置日志输出级别|
|基础功能|setLogLevel(level: brtc.BrtcLogLevel): void|
|进阶功能||
|客户端API|**参数**|
|Android (/rtc/client_api/||
|Android/overview.html)|名称 描述|
|iOS (/rtc/client_api/iOS/||
|overview.html)|level log级别,详见BrtcLogLevel (/rtc/client_api/HarmonyOS/EnumClass.html#BrtcLogLevel)|
|小程序(/rtc/client_api/||
|MiniProgram/overview.html)||
|Web (/rtc/client_api/Web/|**setLogPath**|
|overview.html)||
|Electron (/rtc/client_api/ Electron/BRTC.html)|设置日志保存路径|
|C++ (/rtc/client_api/c++/|setLogPath(path: string): void|
|overview.html)||
|uni-app (/rtc/client_api/uni-app/ BRTC.html)|**参数**|
|Mac (/rtc/client_api/Mac/||

第23页 共24页 

2025/2/12 18:50 

百家云-开发文档 

https://docs.baijiayun.com/rtc/client_api/HarmonyOS/BRTC.html 

## **开发者中心文档中心** 名称 **(https://www.baijiayun.com/brtcDeveloperCenter)** 描述 

## **下载中心 (/resources/docs/open/download/tpl.html)** 

## **www.baijiayun.cfrom=brtc) 注册 (https://auth?/ 登录** 

path 日志文件保存路径 实时音视频 产品介绍 **详情** 性能数据 (/rtc/performance/ 请务必在所有其他接口之前调用此方法来设置,并且保证您指定的目录是存在的,并且您的应用程序拥有对该目录的读写权限,否 performance.html) 则可能无法成功记录日志 发版说明 (/rtc/release/ SDK 不会自动清理保存下来的日志,需要您自行完成过期日志的清理工作 Android.html) 单个日志文件的最大尺寸是 10MB,超过的会产生多个日志文件 快速入门 基础功能 进阶功能 客户端 API 

Android (/rtc/client_api/ Android/overview.html) iOS (/rtc/client_api/iOS/ overview.html) 小程序 (/rtc/client_api/ MiniProgram/overview.html) 

Web (/rtc/client_api/Web/ overview.html) Electron (/rtc/client_api/ Electron/BRTC.html) C++ (/rtc/client_api/c++/ overview.html) 

uni-app (/rtc/client_api/uni-app/ BRTC.html) 

Mac (/rtc/client_api/Mac/ 

第24页 共24页 

2025/2/12 18:50
