# **HJPusher SDK 使用指南** 

适用包:@hj-live/hjpusher 版本:1.0.13 更新日期:2026-05-09 

|**项目**|**说明**|
|---|---|
|文档定位|面向HarmonyOS 应用开发者,说明SDK 的 安装、初始化、常用功能、FAQ 和排障方法。|
|适用平台|HarmonyOS Stage 模型;SDK 以HAR 包形 式集成。|
|许可|proprietary|
|参考代码|examples/harmony 对应SDK 模块、 examples/harmony/entry 业务示例,以及 docs/huawei 中的接入文档。|

## 一、产品概述 

HJPusher 是面向HarmonyOS 直播业务的推流SDK,用于从CameraKit 和麦克风采集音视频数 据,经过SDK 内部媒体图处理后编码并推送到RTMP 服务。 

- 核心场景:摄像头预览、麦克风采集、H.264/H.265 视频编码、AAC 音频编码、RTMP 推流。 

- 扩展场景:本地录制、礼物/PNG 序列叠加、双屏推流、静音、预览旋转、语音数据获 取、人脸检测联动、FaceU 和动态图节点控制。 

- 接入边界:业务层负责权限、CameraKit、XComponent 生命周期和推流URL;SDK 负 责native 媒体图、编码、推流、状态回调和渲染节点。 

|**层级**|**主要职责**|**参考路径**|
|---|---|---|
|业务 ArkUI 层|申请权限、创建页面、管理 CameraKit 和XComponent 生 命周期。|examples/harmony/entry/src/main/ets/pusher|
|SDK ETS 层|暴露HJPusher、PreviewInfo、 PusherConfig、 SetWindowInfo 和图节点接 口。|examples/harmony/hjpusher/Index.ets|

|Native|创建预览图、推流图、|src/entry/pusher/hsys/verify|
|---|---|---|
|媒体层|NativeImage/NativeWindow,||
||并执行编码推流。||

## 二、安装和设置步骤 

|**步骤**|**操作**|**说明**|
|---|---|---|
|1|安装HAR 包|执行ohpm install @hj- live/hjpusher,或在 entry/oh-package.json5 中 使用file:../hjpusher 做本地 联调。|
|2|声明权限|宿主应用需要CAMERA、 MICROPHONE、 INTERNET。SDK HAR 已声 明权限,但运行时仍需由宿主 主动申请。|
|3|导入接口|从@hj-live/hjpusher 导入 HJPusher、PreviewInfo、 PusherConfig、 SetWindowInfo、LogMode 等。|
|4|初始化日志|调用 HJPusher.contextInit(valid, logDir, logLevel, logMode, maxSize, maxFiles)。同进程 只需初始化一次。|
|5|准备相机和窗口|使用CameraKit 获取预览 流;使用 XComponentType.SURFACE 获取ArkUI surface。|

### **2.1** 权限申请 

HJPusher 的最小权限为CAMERA、MICROPHONE、INTERNET。用户拒绝相机或麦克风权限 时,应阻止openPreview() 和openPusher()。 

const atManager = abilityAccessCtrl.createAtManager(); 

await atManager.requestPermissionsFromUser(getContext(), [ 

'ohos.permission.CAMERA', 

'ohos.permission.MICROPHONE' 

]); 

### **2.2** 初始化示例 

HJPusher.contextInit(true, '/data/storage/el2/base/haps/entry/files/', 2, 

LogMode.CONSOLE | LogMode.FILE, 5 * 1024 * 1024, 5); 

const hjPusher = new HJPusher(); 

hjPusher.createPusher(); 

## 三、功能操作指南 

|**操作**|**推荐顺序**|**关键接口**|
|---|---|---|
|打开预览|contextInit -> createPusher -> openPreview -> CameraKit bind/start -> setWindow|openPreview(), CameraService.bindSurfaceId(), setWindow()|
|开始推流|预览已启动后填写 PusherConfig,再调用 openPusher|openPusher(config, stateInfo, stateCall)|
|停止推流|先停止推流,再释放相机和预 览图|closePusher(), closePreview(), destroyPusher()|
|窗口生命周期|surface create/change 绑定 窗口;页面退出或surface 销 毁时发送TARGET_DESTROY|setWindow({ classStyle, insName, surfaceId, width, height, state })|
|静音/旋转|业务状态变化后即时下发|setMute(), setPreviewRotation()|
|录制|推流过程中打开录制,停止后 保存文件|openRecorder(), closeRecorder()|
|礼物和双屏|按业务模式启用礼物推送或双 屏|openPngSeq(), setGiftPusher(), setDoubleScreen()|
|人脸/FaceU|先打开人脸检测,再启用 FaceU 或图节点|nativeSourceOpen(), setFaceInfo(), nodeEnable()|
|语音数据|按需开启音频数据回调|openSpeechRecognizer(), closeSpeechRecognizer()|

### **3.1** 打开预览 

const previewInfo = new PreviewInfo(); 

previewInfo.realWidth = 1280; 

```arkts
previewInfo.realHeight = 720; const previewSurfaceId = hjPusher.openPreview(previewInfo, (json: string) => { const notify = JSON.parse(json); 
```

}); 

cameraService.initCamera(getContext() as Context); cameraService.bindSurfaceId(previewSurfaceId.toString()); await cameraService.startPreview(1); 

#### **说明:** openPreview() 返回的是给CameraKit PreviewOutput 使用的NativeImage 

#### surfaceId;不要把它当作ArkUI XComponent 的surfaceId。 

### **3.2** 绑定 **XComponent** 

hjPusher.setWindow({ 

classStyle: HJRteGraphConfig.HJNodeClass_TargetUI_0, 

insName: HJRteGraphConfig.HJNodeClass_TargetUI_0, surfaceId, width: rect.surfaceWidth, height: rect.surfaceHeight, state: SetWindowState.TARGET_CHANGE }); 

### **3.3** 开始推流 

```arkts
hjPusher.openPusher(pusherConfig, { uid: 2342, device: 'Harmony', sn: 'HJPusher' }, (json: string) => { const notify = JSON.parse(json); }); 
```

### **3.4** 生命周期建议 

1. 页面进入时申请权限、初始化SDK、创建pusher、打开预览。 

2. CameraKit 绑定openPreview() 返回的surfaceId 后再启动预览。 

3. XComponent surface 创建或尺寸变化时调用setWindow()。 

4. 开始直播时调用openPusher();停止直播时调用closePusher()。 

5. 页面退出时按closePusher -> CameraKit release -> closePreview -> destroyPusher 顺序释放。 

## 四、常见问题解答 

|**问题**|**回答**|
|---|---|
|HAR 已声明权限,为什么宿主还要申请?|module.json5 声明只表示SDK 需要能力; HarmonyOS 运行时权限仍由宿主应用向用户 申请。|
|openPreview() 返回的surfaceId 是什么?|它是native NativeImage surfaceId,用于绑 定CameraKit PreviewOutput,不是 XComponent surfaceId。|
|可以不打开预览直接推流吗?|不建议。当前示例链路依赖相机预览流进入 SDK,推荐先openPreview 和 startPreview,再openPusher。|
|支持H.265 吗?|PusherConfig.videoConfig.codecID 可选择 HJCodecH264 或HJVCodecH265,最终可 用性还取决于设备编码能力和推流服务支持。|
|停止时能直接destroyPusher 吗?|不建议。应先closePusher,再释放相机和 closePreview,最后destroyPusher。|
|FaceU 没效果怎么办?|确认人脸检测和nativeSource 已打开,图节 点insName/classStyle 正确,资源路径可访 问。|

## 五、故障排除 

|**现象**|**排查方向**|**处理建议**|
|---|---|---|
|预览黑屏|权限、CameraKit|确认已申请CAMERA;openPreview() 返回值非|
||surface、XComponent surface、窗口尺寸。|0;CameraService.bindSurfaceId/startPreview 已执行;setWindow 传入TargetUI 节点。|
|推流无数据|相机预览是否已启动,推|先观察openPreview 回调和CameraKit 日志,再|
||流URL 是否有效。|确认openPusher 在预览后调用。|
|没有声音|MICROPHONE 权限、|重新申请麦克风权限,确认业务静音按钮没有置为|

||setMute 状态、设备麦 克风占用。|true。|
|---|---|---|
|RTMP 连接失败|URL、网络、服务端鉴 权、协议格式。|使用可用RTMP 地址验证;检查 HJ_PUSHER_NOTIFY_CONNECT_FAILED/ERROR 回调。|
|横竖屏方向错误|CameraKit rotation 与 setPreviewRotation 同 步。|窗口尺寸或方向变化后调用 cameraService.updatePreviewRotation() 并同步 setPreviewRotation。|
|退出页面崩溃或|释放顺序错误或surface|按closePusher -> releaseCamera ->|
|资源未释放|销毁未通知。|closePreview -> destroyPusher 顺序处理,必要 时发送TARGET_DESTROY。|

## 六、发布前检查清单 

- 确认oh-package 依赖使用正确包名@hj-live/hjpusher。 

- 确认宿主module.json5 声明并在运行时申请CAMERA、MICROPHONE、INTERNET。 

- 确认推流URL、编码格式、码率、帧率和分辨率符合服务端要求。 

- 确认冷启动、开始推流、停止推流、切后台、回前台、退出页面均无泄漏或崩溃。 

- 确认日志目录可写,出现问题时能提供SDK 日志和业务侧CameraKit 日志。 

## 七、参考路径 

- SDK 导出:examples/harmony/hjpusher/Index.ets 

- SDK 封装:examples/harmony/hjpusher/src/main/ets/native/HJPusher.ets 

- 业务示例:examples/harmony/entry/src/main/ets/pusher 

- 相机示例: 

   - examples/harmony/entry/src/main/ets/camera/service/CameraService.ets 

- 接入文档:docs/huawei/hjpusher/HJPusher SDK 接入文档.docx
