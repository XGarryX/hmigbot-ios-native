# **HJPlayer SDK 接入文档** 

适用SDK:@hj-live/hjplayer 1.0.13 更新日期:2026-05-09 

## **一、文档目的** 

本文档用于指导HarmonyOS 应用接入HJPlayer SDK。内容基于examples/harmony/hjplayer、 examples/harmony/entry 中播放器业务接入代码,以及native 层src/entry/player 与src/entry/hsys 公共导出实现整理。 

本版重点修正README 中旧版初始化签名的误导:当前HJPlayer.contextInit 接收 HJPlayerContextInitConfig 对象,不是多参数contextInit。 

## **二、审阅范围与层边界** 

|**层级**|**代码依据**|**接入责任**|
|---|---|---|
|业务ArkUI 层|examples/harmony/entry/src/main/ets/player|准备播放URL/缓存目录;创建 PlayerXComponent;响应页面显示/隐藏;处 理关闭完成、礼物叠加、静音和可选FaceU 开 关。|
|SDK ETS 层|examples/harmony/hjplayer/Index.ets、 HJPlayer.ets、HJPlayerTypes.ets、 HJCommTypes.ets|提供HJPlayer、OpenPlayerInfo、 SetWindowInfo、 HJPlayerContextInitConfig、下载缓存、SEI 与图节点接口。|
|Harmony NAPI 层|src/entry/player/hsys/napi_init.cpp、 HJPlayerNapi.cpp、HJPlayerBridge.cpp|将ETS 参数序列化JSON 后解析为C++ 结 构;维护native handle;通过线程安全回调 返回播放器、统计、SEI 和下载状态。|
|Native 媒体层|src/entry/player/hsys/verify/HJNAPIPlayer.*、 src/entry/hsys/HJNativeExportCommon.*|创建播放图和渲染图;管理NativeWindow; 执行closePlayer 异步释放;提供预加载、下 载缓存、SEI 和公共图节点能力。|

src/entry/player 还包含Android asys 与iOS isys 入口;本文只把HarmonyOS hsys 的 ETS/NAPI/native 路径写成SDK 接入要求。 

## **三、SDK 概述** 

- 基础能力:直播流播放、点播播放、ArkUI XComponent 渲染、静音/暂停、时长与当前时间戳查询、 播放状态通知。 

- 扩展能力:预加载、下载缓存、SEI UUID 过滤与回调、透明分屏礼物播放、人脸检测/FaceU、运行时 RTE 图节点控制。 

- 最小接入只需要HJPlayer.contextInit、createPlayer、openPlayer、setWindow、closePlayer、 exitPlayer、destroyPlayer;下载、SEI、人脸和图节点能力均可按需接入。 

## **四、工程集成** 

|**项目**|**当前代码值**|
|---|---|
|ohpm 包名|@hj-live/hjplayer|
|版本|1.0.3|
|入口文件|Index.ets|
|HAR module name|hjplayer|
|native 库|libHJMediaPlayer.so|
|权限|ohos.permission.INTERNET|

# 独立业务工程 ohpm install @hj-live/hjplayer // 推荐导入 import { HJPlayer, HJPlayerContextInitConfig, HJOptionDir, LogMode, OpenPlayerInfo, HJPlayerType, HJPlayerSourceType, HJPlayerVideoCodecType, SetWindowState } from '@hj-live/hjplayer'; 

HJPlayer HAR 的module.json5 声明INTERNET。业务宿主也需要声明网络权限;本地文件播放无需额外 权限,但缓存目录必须位于应用可写目录。 

## **五、初始化SDK** 

初始化入口为HJPlayer.contextInit(config: HJPlayerContextInitConfig)。示例PlayerPage.ets 在 

aboutToAppear 中初始化,并配置日志、媒体缓存目录、其他缓存目录和下载重试次数。 

const workDir = '/data/storage/el2/base/haps/entry/files/'; const config: HJPlayerContextInitConfig = { valid: true, logDir: workDir, logLevel: 2, 

logMode: LogMode.CONSOLE | LogMode.FILE, maxSize: 5 * 1024 * 1024, maxFiles: 5, medias_dir: workDir + 'hjmedias', medias_cache_max: 200, other_dirs_options: [ { name: workDir + 'gift', max: 100 } as HJOptionDir, { name: workDir + 'shorts', max: 200 } as HJOptionDir ], download_retry_max: 10 }; HJPlayer.contextInit(config); 

|**字段**|**说明**|
|---|---|
|valid/logDir/logLevel/logMode/maxSize/maxFiles|日志开关、目录、级别、输出模式和滚动策略;native 映射到 HJEntryContextPlayerInfo。|
|medias_dir|播放器媒体缓存目录,download/openPlayer localDir 可与 该目录配合使用。|
|medias_cache_max|媒体缓存目录容量上限,单位按native 缓存实现解释。|
|other_dirs_options|额外缓存目录及上限,例如gift、shorts。|
|download_retry_max|下载缓存重试次数,默认建议10。|

## **六、最小播放接入流程** 

1. 进程或页面入口调用HJPlayer.contextInit(config)。 

2. 创建HJPlayer 实例并调用createPlayer()。 

3. 构造OpenPlayerInfo,明确url、localDir、rid、fps、videoCodecType、sourceType、playerType 等字段。 

4. 调用openPlayer(openPlayerInfo, stateCall, stateInfo, statCall, seiCall?)。ETS 层会把 OpenPlayerInfo 序列化为JSON,native 层解析后创建render graph 与player graph。 

5. 在XComponent onSurfaceCreated/onSurfaceChanged 中调用setWindow(...)。注意HJPlayer.ets 只有在isOpen=true 后才会向native 传递setWindow,因此示例先openPlayer,再由surface 回调 绑定窗口。 

6. 页面退出时先发送TARGET_DESTROY,再closePlayer()。不要立即destroyPlayer;等待 HJ_PLAYER_NOTIFY_CLOSEDONE 后调用exitPlayer() 与destroyPlayer()。 

const hjPlayer = new HJPlayer(); hjPlayer.createPlayer(); 

const openInfo: OpenPlayerInfo = { url: 'https://example.com/live.flv', localDir: '/data/storage/el2/base/haps/entry/files/hjmedias', rid: '', 

fps: 30, repeats: 0, videoCodecType: HJPlayerVideoCodecType.HJPlayerVideoCodecType_OHCODEC, sourceType: HJPlayerSourceType.HJPlayerSourceType_SERIES, playerType: HJPlayerType.HJPlayerType_LIVESTREAM, bSplitScreenMirror: false, disableMFlag: 0, m_graphConfig: '', m_enableSEIUUids: new Map<string, boolean>() }; 

```arkts
hjPlayer.openPlayer(openInfo, (json: string) => { const notify = JSON.parse(json); // { type, msgInfo } if (notify.type === HJPlayerNotifyType.HJ_PLAYER_NOTIFY_CLOSEDONE) { hjPlayer.exitPlayer(); hjPlayer.destroyPlayer(); } }, { uid: 2342, device: 'Harmony', sn: 'HJPlayer' }, (json: string) => { const stat = JSON.parse(json); // { name, type, info } }); 
// XComponentController 生命周期 onSurfaceCreated(surfaceId: string): void { store.dispatch(new WindowAction({ classStyle: HJRteGraphConfig.HJNodeClass_TargetUI_0, insName: HJRteGraphConfig.HJNodeClass_TargetUI_0, surfaceId, width: 1, height: 1, state: SetWindowState.TARGET_CREATE })); } 
onSurfaceChanged(surfaceId: string, rect: SurfaceRect): void { store.dispatch(new WindowAction({ classStyle: HJRteGraphConfig.HJNodeClass_TargetUI_0, insName: HJRteGraphConfig.HJNodeClass_TargetUI_0, surfaceId, width: rect.surfaceWidth, height: rect.surfaceHeight, state: SetWindowState.TARGET_CHANGE })); } onSurfaceDestroyed(surfaceId: string): void { store.dispatch(new WindowAction({ classStyle: HJRteGraphConfig.HJNodeClass_TargetUI_0, insName: HJRteGraphConfig.HJNodeClass_TargetUI_0, surfaceId, width: 0, height: 0, state: SetWindowState.TARGET_DESTROY })); } 
```

## **七、核心接口与参数** 

|**接口**|**调用阶段**|**说明**|
|---|---|---|
|HJPlayer.contextInit(config)|进程/页面初始化|当前唯一正确初始化签名。内部有 m_contextInitFlag,同进程只初始化一 次。|
|preloadUrl(url)|播放前可选|通过HJNetManager 预加载网络URL。|
|download(info, stateCall): string|缓存下载|返回rid;stateCall 回调下载进度和结 果。|
|cancelDownload(rid)|取消下载|参数是download 返回或传入的rid,不 是URL。|
|createPlayer()|播放前|创建native HJPlayerBridge handle。|
|openPlayer(openInfo, stateCall, stateInfo, statCall, seiCall?)|开始播放|第6 个SEI 回调可选;native 校验参数并 创建播放图。|
|setWindow(setWindowInfo)|XComponent surface 生命周期|仅在isOpen=true 时生效; classStyle/insName 必须与图节点 TargetUI 对齐。|
|closePlayer()|关闭播放|native 异步释放player graph 和render graph,并回调 HJ_PLAYER_NOTIFY_CLOSEDONE。|
|exitPlayer()|收到 CLOSEDONE 后|等待并释放closePlayer 创建的退出线 程。|
|destroyPlayer()|最终释放|删除native handle;必须在close/exit 完成后调用。|

|**结构**|**字段**|**说明**|
|---|---|---|
|OpenPlayerInfo|url, localDir, rid, fps, repeats|播放地址、缓存目录、资源ID、渲染帧率、 VOD 重复次数。fps=0 时native 进入 manualDrive 逻辑,常规接入建议30。|
|OpenPlayerInfo|videoCodecType|SoftDefault=0、OHCODEC=1、 VIDEOTOOLBOX=2、MEDIACODEC=3; Harmony示例使用OHCODEC。|
|OpenPlayerInfo|sourceType|SERIES 为普通播放;SPLITSCREEN 用于左 右分屏透明礼物;Bridge 暂不作为普通业 务首选。|
|OpenPlayerInfo|playerType|LIVESTREAM=1 使用直播图与key strategy;VOD=2 使用点播图并支持 repeats。|
|OpenPlayerInfo|bSplitScreenMirror, disableMFlag, m_graphConfig, m_enableSEIUUids|控制分屏镜像、禁用媒体类型、RTE 图配 置、SEI UUID 过滤。|

|SetWindowInfo|classStyle, insName, surfaceId,|窗口绑定信息;示例使用|
|---|---|---|
||width, height, state|HJNodeClass_TargetUI_0。|
|MediaStateInfo|uid, device, sn|统计上下文字段。|

## **八、下载缓存与预加载** 

PlayerPage.ets 演示了HJPlayer.download(info, callback) 与HJPlayer.cancelDownload(rid)。native 层HJPlayerNapi::download 会回调 

HJ_RENDER_NOTIFY_CACHE_START/PROGRESS/COMPLETED/FAILED,并返回rid。 

```arkts
const info: HJPlayerDownloadInfo = { url: mediaUrl, dir: workDir + 'hjmedias', rid: '', preCacheSize: -1, priority: 1 }; const rid = HJPlayer.download(info, (json: string) => { const notify = JSON.parse(json); const progress = notify.totalSize > 0 ? notify.validSize * 100 / notify.totalSize : 0; }); 
```

HJPlayer.cancelDownload(rid); 

|**字段**|**说明**|
|---|---|
|url|下载的网络媒体地址。|
|dir|缓存保存目录,应为应用可写目录。|
|rid|业务可传资源ID;为空时native 可返回生成的rid。|
|preCacheSize|预缓存大小;-1 表示按默认策略。|
|priority|下载优先级。|

## **九、SEI 接入** 

- openPlayer 的第6 个参数seiCall 可选,类型为(seiInfo: HJPlayerSeiInfo) => void。 

- m_enableSEIUUids 是Map<string, boolean>,key 为UUID,value 表示key frame 是否必须回 调;序列化由serializeOpenPlayerInfo 手动完成。 

- 播放打开后可调用setEnableSEIUUids(uuid, bKeyMustCb) 动态调整。 

- 回调中的HJPlayerSeiData.data 是ArrayBuffer;示例PlayerXComponentStore 将其转为UTF-8 和 hex 日志。 

## **十、礼物、FaceU 与图节点** 

|**能力**|**接口/示例**|**说明**|
|---|---|---|
|透明 分屏 礼物|PlayerXComponent sourceType=SPLITSCREEN, playerType=VOD|LivePlayerPage 叠 加第二个 PlayerXComponent 播放本地礼物视频, HitTest 设为 Transparent。|
|静音|setMute(mute)|LivePlayerStore 通 过emitter 通知 PlayerXComponent Store 调用。|
|暂停|setPause(pause)|基础控制接口,需在 isOpen=true 后调 用。|
|人脸 检测|HJFaceDetectMgr + nativeSourceOpen/Acquire/Close + setFaceInfo|由 HJNativeExportCo mmon 公共导出, 基础播放不需要接 入。|
|Fac eU|openFaceu/closeFaceu 或nodeEnable(HJNodeClass_SourceFaceu,...)|示例通过emitter 将 开关传给 PlayerXComponent Store。|
|动态 图节 点|nodeCreate/nodeConnect/nodeSetParam/nodeEnable/nodeDelete/nodeDiscon nect/nodeGetPre/nodeGetNext|用于高级RTE 图调 整;参数为 classStyle、 insName 与JSON 字符串。|

## **十一、通知与状态** 

|**类型**|**值**|**建议处理**|
|---|---|---|
|HJ_PLAYER_NOTIFY_VIDEO_FIRST_RENDER|5|首帧上屏,可用于埋点或隐藏 loading。|
|HJ_PLAYER_NOTIFY_AUDIO_FRAME|6|音频帧通知,通常只做调试或统 计。|
|HJ_PLAYER_NOTIFY_EOF|7|点播/礼物播放结束;示例用于关|

|||闭礼物叠加。|
|---|---|---|
|HJ_PLAYER_NOTIFY_DURATION|50|时长通知。|
|HJ_PLAYER_NOTIFY_SEI_INFOS|51|SEI 信息通知;也可使用可选 seiCall 获取结构化 ArrayBuffer。|
|HJ_PLAYER_NOTIFY_AUDIO_START_BUFFERING/STOP_BUFFERING|52/53|音频缓冲状态。|
|HJ_PLAYER_NOTIFY_CLOSEDONE|90|closePlayer 异步释放完成;此 时再exitPlayer() + destroyPlayer()。|
|HJ_RENDER_NOTIFY_CACHE_*|200- 203|下载缓存开始、进度、完成、失 败。|

## **十二、Native 实现约束** 

- HJPlayer.ets 的setWindow、setMute、setPause、getDuration、getCurrentTimestamp、 setEnableSEIUUids 都要求m_playerHandler 存在且isOpen=true;调用顺序必须先openPlayer。 

- HJPlayerNapi::openPlayer 至少需要5 个参数,第6 个SEI callback 可选;如果第6 个参数存在但不 是function/null/undefined,会抛出类型错误。 

- closePlayer 会在native 创建退出线程异步释放graph,并在完成后回调 

   - HJ_PLAYER_NOTIFY_CLOSEDONE;业务不得在closePlayer 之后立即destroyPlayer。 

- exitPlayer 用于等待并清理closePlayer 的退出线程;这是与destroyPlayer 不同的释放阶段。 

- getDuration/getCurrentTimestamp 返回BigInt,展示到UI 时需要转换为number/string 并注意溢 出。 

- obfuscation-rules.txt 已保留公共ETS 类型、方法名、字段名与n_* bridge 名称;发布前不要删除 keep 规则。 

## **十三、生命周期与排查** 

|**现象**|**优先检查**|
|---|---|
|画面不显示|确认openPlayer 已成功且isOpen=true 后setWindow;检查 XComponent 是否发送TARGET_CREATE/CHANGE; classStyle/insName 是否为TargetUI 节点。|
|关闭后崩溃或资源泄漏|按TARGET_DESTROY -> closePlayer -> CLOSEDONE -> exitPlayer -> destroyPlayer 顺序释放。|
|下载进度不动|检查INTERNET 权限、URL 可访问性、dir 是否为应用可写目录、rid 是否 用于cancelDownload。|

|SEI 无回调|确认m_enableSEIUUids 或setEnableSEIUUids 的UUID 与流内UUID 一|
|---|---|
||致;检查是否传入第6 个seiCall。|
|礼物播放方向或透明异常|确认sourceType=SPLITSCREEN、playerType=VOD、|
||bSplitScreenMirror 与图节点配置。|

## **十四、参考路径** 

- examples/harmony/hjplayer/Index.ets 

- examples/harmony/hjplayer/src/main/ets/native/HJPlayer.ets 

- examples/harmony/hjplayer/src/main/ets/HJPlayerTypes.ets 

- examples/harmony/hjplayer/src/main/ets/native/HJCommTypes.ets 

- examples/harmony/entry/src/main/ets/player/pages/PlayerPage.ets 

- examples/harmony/entry/src/main/ets/player/component/PlayerXComponent.ets 

- examples/harmony/entry/src/main/ets/player/store/PlayerXComponentStore.ets 

- examples/harmony/entry/src/main/ets/player/store/LivePlayerStore.ets 

- src/entry/player/hsys/napi_init.cpp 

- src/entry/player/hsys/bridge/HJPlayerNapi.cpp 

- src/entry/player/hsys/verify/HJNAPIPlayer.cpp 

- src/entry/hsys/HJNativeExportCommon.cpp
