# **HJPusher SDK 接入文档** 

适用SDK:@hj-live/hjpusher 1.0.13 更新日期:2026-05-09 

## **一、文档目的** 

本文档用于指导HarmonyOS 应用在真实业务中接入HJPusher SDK。内容基于 examples/harmony/hjpusher、examples/harmony/entry 中推流接入代码,以及native 层 src/entry/pusher 与src/entry/hsys 公共导出实现整理。 

如果README 与当前代码存在差异,以Index.ets 暴露的ETS API、示例Store/Component 调用顺序、 native NAPI 注册与参数解析为准。 

## **二、审阅范围与层边界** 

|**层级**|**代码依据**|**接入责任**|
|---|---|---|
|业务ArkUI 层|examples/harmony/entry/src/main/ets/pusher、 camera|申请运行时权限;创建页面Store;管理 CameraKit 预览输出;绑定XComponent surface;在页面生命周期内停止推流并释 放相机。|
|SDK ETS 层|examples/harmony/hjpusher/Index.ets、 HJPusher.ets、HJPusherTypes.ets、 HJCommTypes.ets|提供HJPusher、PreviewInfo、 PusherConfig、SetWindowInfo、 PusherStateType、图节点配置等公共接 口。|
|Harmony NAPI 层|src/entry/pusher/hsys/napi_init.cpp、 HJPusherNapi.cpp、HJPusherBridge.cpp|将ETS JSON 参数解析为C++ 结构;维 护native handle;通过 ThreadSafeFunctionWrapper 回调推流/ 预览/统计状态。|
|Native 媒体层|src/entry/pusher/hsys/verify/HJNAPILiveStream.*、 src/entry/hsys/HJNativeExportCommon.*|创建渲染图、NativeImage 预览 surface、RTMP 推流图、录制、语音数 据、人脸/图节点公共能力和 NativeWindow 生命周期。|

src/entry/pusher 当前文档只描述HarmonyOS hsys 接入路径;Android/iOS 入口不应被写成Harmony API。 

## **三、SDK 概述** 

- 基础能力:摄像头预览、麦克风采集、H.264/H.265 视频编码、AAC 音频编码、RTMP 推流、推流状 态回调。 

- 扩展能力:本地录制、PNG 序列/礼物叠加、双屏推流、静音、预览旋转、语音数据获取、人脸检测联 动、FaceU/图节点控制。 

- 最小接入只需要HJPusher、PreviewInfo、PusherConfig、SetWindowInfo、CameraKit 与 XComponent;图节点、人脸、录制和语音能力均为可选扩展。 

## **四、工程集成** 

### **4.1 包名与安装** 

|**项目**|**当前代码值**|
|---|---|
|ohpm 包名|@hj-live/hjpusher|
|版本|1.0.13|
|入口文件|Index.ets|
|HAR module name|hjpusher|
|native 库|libHJPusher.so|

# 独立业务工程 ohpm install @hj-live/hjpusher 

// 推荐导入 import { HJPusher, PreviewInfo, PusherConfig, VideoCodecType, AudioCodecType, SetWindowInfo, SetWindowState, LogMode } from '@hj-live/hjpusher'; 

同仓库联调时,示例entry 可通过file 依赖引用本地examples/harmony/hjpusher 模块;发布接入时以 @hj-live/hjpusher 为准。 

### **4.2 权限配置** 

|**权限**|**用途**|**业务侧要求**|
|---|---|---|
|ohos.permission.CAMERA|摄像头画面采集|需要在宿主entry 申请运行时授权。|
|ohos.permission.MICROPHONE|麦克风音频采集|需要在宿主entry 申请运行时授权。|
|ohos.permission.INTERNET|RTMP 推流连接|在module.json5 声明;无需运行时 弹窗。|

HJPusher HAR 自身module.json5 已声明CAMERA、MICROPHONE、INTERNET;业务应用仍应在使 用相机/麦克风前主动申请权限,并在用户拒绝时阻止openPreview/openPusher。 

## **五、标准接入流程** 

示例中的真实主链路位于PusherPreviewStore.ets、PusherXComponent.ets、CameraService.ets。推 荐按下面顺序接入: 

1. 调用HJPusher.contextInit(...) 初始化日志上下文;该方法内部有静态m_contextInitFlag,同一进程只 初始化一次。 

2. 创建HJPusher 实例并调用createPusher(),得到native HJPusherBridge handle。 

3. 构造PreviewInfo,设置realWidth、realHeight、previewFps 和可选m_graphConfig。 

4. 调用openPreview(previewInfo, previewCallback),native 层创建渲染图与NativeImage,返回用 于CameraKit PreviewOutput 的surfaceId。 

5. 业务侧CameraService.initCamera(context),bindSurfaceId(surfaceId), startPreview(front/rear),并把getLastPreviewRotation()/updatePreviewRotation() 同步给 setPreviewRotation(...)。 

6. 在XComponent onSurfaceCreated/onSurfaceChanged 中调用setWindow({ classStyle, insName, surfaceId, width, height, state }) 绑定预览UI。 

7. 业务侧填写PusherConfig 与MediaStateInfo 后调用openPusher(config, stateInfo, statCallback)。 

8. 页面退出或停止直播时,依次closePusher()、释放CameraKit、closePreview()、destroyPusher(); 如surface 生命周期提前销毁,应先发送TARGET_DESTROY。 

```arkts
const logPath = '/data/storage/el2/base/haps/entry/files/'; HJPusher.contextInit(true, logPath, 2, LogMode.CONSOLE | LogMode.FILE, 5 * 1024 * 1024, 5); const hjPusher = new HJPusher(); hjPusher.createPusher(); const previewInfo = new PreviewInfo(); previewInfo.realWidth = 1280; previewInfo.realHeight = 720; previewInfo.previewFps = 30; previewInfo.m_graphConfig = HJRteGraphConfigConstructor.constructGraph({ type: HJRteGraphConstructorType.HJRteGraphConstructorType_PlaceHolder }); const previewSurfaceId = hjPusher.openPreview(previewInfo, (json: string) => { const notify = JSON.parse(json); // { type, msgInfo } }); 
cameraService.initCamera(getContext() as Context); 
cameraService.bindSurfaceId(previewSurfaceId.toString()); await cameraService.startPreview(1); // 1: front camera in demo const rotation = cameraService.getLastPreviewRotation(); if (rotation !== undefined) { hjPusher.setPreviewRotation(rotation); 
```

#### } 

// XComponentController 生命周期 onSurfaceCreated(surfaceId: string): void { hjPusher.setWindow({ 

classStyle: HJRteGraphConfig.HJNodeClass_TargetUI_0, insName: HJRteGraphConfig.HJNodeClass_TargetUI_0, surfaceId, width: 1, height: 1, state: SetWindowState.TARGET_CREATE }); } 

onSurfaceChanged(surfaceId: string, rect: SurfaceRect): void { hjPusher.setWindow({ 

classStyle: HJRteGraphConfig.HJNodeClass_TargetUI_0, insName: HJRteGraphConfig.HJNodeClass_TargetUI_0, surfaceId, width: rect.surfaceWidth, height: rect.surfaceHeight, state: SetWindowState.TARGET_CHANGE }); } 

const pusherConfig: PusherConfig = { videoConfig: { 

codecID: VideoCodecType.HJVCodecH265, width: 720, height: 1280, bitrate: 2 * 1024 * 1024, frameRate: 30, gopSize: 60, videoIsROIEnc: true }, audioConfig: { codecID: AudioCodecType.HJCodecAAC, bitrate: 164 * 1000, sampleFmt: 1, samplesRate: 48000, channels: 2 }, url: 'rtmp://your-domain/live/stream' }; 

```arkts
hjPusher.openPusher(pusherConfig, { uid: 2342, device: 'Harmony', sn: 'HJPusher' }, (json: string) => { const stat = JSON.parse(json); // { name, type, info } }); 
```

## **六、核心接口与参数** 

|**接口**|**调用阶段**|**说明**|
|---|---|---|
|HJPusher.contextInit(valid, logDir, logLevel, logMode, maxSize, maxFiles)|进程初始化|初始化HJEntryContext。valid 控制日志是 否启用,logMode 可使用CONSOLE |
FILE。|
|createPusher()|页面进入|创建native HJPusherBridge; openPreview/openPusher/setWindow 都 依赖该handle。|
|openPreview(previewInfo, callback): bigint|相机预览前|创建preview/render 图并返回 NativeImage surfaceId;native 会校验 width/height/fps 大于0。|
|setWindow(setWindowInfo): number|XComponent surface 生命周期|将ArkUI XComponent surface 绑定到指定 TargetUI 节点;classStyle/insName 必 填。|
|openPusher(pusherConfig, stateInfo, stateCall)|开始直播|解析videoConfig/audioConfig/url; stateInfo 用于统计上下文;异常时抛出 openPusher failed。|
|closePusher()|停止直播|停止RTMP 推流图,但不销毁预览和相机。|
|closePreview()|页面退出|释放preview/render 图、 NativeWindow、NativeSource。|
|destroyPusher()|最终释放|删除native bridge handle;应在 closePusher/closePreview 之后调用。|

|**结构**|**字段**|**说明**|
|---|---|---|
|PreviewInfo|realWidth, realHeight, previewFps, m_graphConfig|预览输入尺寸、渲染帧率、可选RTE 图配置。|
|SetWindowInfo|classStyle, insName, surfaceId, width, height, state|窗口绑定目标。示例使用 HJNodeClass_TargetUI_0 作为 classStyle/insName。|
|PusherConfig|videoConfig, audioConfig, url|直播推流参数;url 为空无法完成真实RTMP 推流。|
|VideoConfig|codecID, width, height, bitrate, frameRate, gopSize, videoIsROIEnc|native 映射到HJPusherVideoInfo,bitrate 单位为bps。|
|AudioConfig|codecID, bitrate, sampleFmt, samplesRate, channels|native 同时作为采集和编码采样率/声道; sampleFmt=1 对应S16。|
|MediaStateInfo|uid, device, sn|统计上下文字段,示例使用{ uid: 2342, device: 'Harmony', sn: 'HJPusher' }。|

## **七、通知与回调** 

|**回调来源**|**JSON 形态**|**常见type**|
|---|---|---|
|openPreview callback|{ type, msgInfo }|HJ_PUSHER_NOTIFY_LIVE_INFO(8) 时 msgInfo 可解析为{ kbps, fps, delay}。|
|openPusher statCallback|{ name, type, info }|native 统计回调,业务可按 name/type/info 上报或日志记录。|
|openSpeechRecognizer callback|ArrayBuffer|返回音频帧数据,适合语音识别扩展;基础 推流不需要接入。|

PusherStateType 与native HJPusherNofityType 保持一致:连接成功、连接失败、断开、重试、丢帧、 自动码率、LiveInfo、Muxer/Codec/AudioFIFO/Capturer 错误等。 

## **八、可选能力** 

|**能力**|**ETS API**|**接入要点**|
|---|---|---|
|静音|setMute(mute)|示例中麦克风按钮翻转后调 用;true 为静音。|
|本地 录制|openRecorder({ recordUrl }), closeRecorder()|recordUrl 使用业务可写路 径;示例录制到tempDir 并 保存到相册。|
|PNG /礼 物|openPngSeq(url), setGiftPusher(flag)|与图节点/推礼物场景配合使 用。|
|双屏|setDoubleScreen(flag)|native 根据预览宽高判断横竖 屏并调整图处理。|
|预览 旋转|setPreviewRotation(rotation)|CameraService 在 startPreview 和 windowSizeChange 后调 用。|
|语音 识别 数据|openSpeechRecognizer(cb), closeSpeechRecognizer()|native 以ArrayBuffer 形式回 调音频数据。|
|人脸 检测 /Fac eU|setFaceInfo, nativeSourceOpen/Acquire/Close, nodeEnable/openFaceu|由HJNativeExportCommon 公共导出;示例优先用 nodeEnable(HJNodeClass_ SourceFaceu, ...) 控制 FaceU。|

动态 nodeCreate/nodeConnect/nodeSetParam/nodeEnable/nodeDelete/nod 用于运行时调整RTE 图;参 图节 eDisconnect/nodeGetPre/nodeGetNext 数以JSON 字符串传入。 点 

## **九、Native 实现约束** 

- openPreview 在native 层要求realWidth、realHeight、previewFps 均大于0;重复openPreview 会返回错误。 

- openPreview 返回的是NativeImage surfaceId,业务必须把它交给CameraKit PreviewOutput;不 要把相机videoOutput 直接当作推流输入。 

- setWindow 的surfaceId 会被native 转成OH_NativeWindow,并在TARGET_DESTROY 或 closePreview 时销毁;业务不要重复复用已销毁surfaceId。 

- openPusher 会把videoConfig/audioConfig/url 映射到HJPusherVideoInfo、 HJPusherAudioInfo、HJPusherRTMPInfo;audio samplesRate 同时作为采集和编码采样率。 

- 人脸、NativeSource、FaceU 和node* API 由src/entry/hsys/HJNativeExportCommon.cpp 公共注 册,HJPusher.ets 已包装为实例方法。 

- obfuscation-rules.txt 已保留Index.ets 公共API 与n_* bridge 名称;发布前不要删除这些keep 规 则。 

## **十、生命周期与排查** 

|**现象**|**优先检查**|
|---|---|
|预览黑屏|确认openPreview 返回surfaceId 后才bindSurfaceId/startPreview;检 查runtime CAMERA 权限;检查setWindow classStyle/insName 是否为 TargetUI 节点。|
|推流无数据|确认CameraService 已startPreview;确认pusherConfig.url 非空且网络 可达;确认openPusher 在openPreview 后调用。|
|旋转方向错误|在startPreview 后读取getLastPreviewRotation,并在 windowSizeChange 时调用updatePreviewRotation + setPreviewRotation。|
|快速进出页面异常|按示例CameraService 的startNum/promise 方式串行释放相机;页面退 出时先停止推流再释放预览和native handle。|
|发布后API 找不到|检查obfuscation-rules.txt/consumer-rules.txt 是否保留公共导出与n_* property name。|

## **十一、参考路径** 

- examples/harmony/hjpusher/Index.ets 

- examples/harmony/hjpusher/src/main/ets/native/HJPusher.ets 

- examples/harmony/hjpusher/src/main/ets/native/HJPusherTypes.ets 

- examples/harmony/hjpusher/src/main/ets/native/HJCommTypes.ets 

- examples/harmony/hjpusher/src/main/ets/native/HJRteGraphSetupInfo.ets 

- examples/harmony/entry/src/main/ets/pusher/store/PusherPreviewStore.ets 

- examples/harmony/entry/src/main/ets/pusher/component/PusherXComponent.ets 

- examples/harmony/entry/src/main/ets/camera/service/CameraService.ets 

- src/entry/pusher/hsys/napi_init.cpp 

- src/entry/pusher/hsys/bridge/HJPusherNapi.cpp 

- src/entry/pusher/hsys/verify/HJNAPILiveStream.cpp 

- src/entry/hsys/HJNativeExportCommon.cpp
