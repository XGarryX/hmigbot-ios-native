# **HJPlayer SDK 使用指南** 

适用包:@hj-live/hjplayer 版本:1.0.13 更新日期:2026-05-09 

|**项目**|**说明**|
|---|---|
|文档定位|面向HarmonyOS 应用开发者,说明SDK 的 安装、初始化、常用功能、FAQ 和排障方法。|
|适用平台|HarmonyOS Stage 模型;SDK 以HAR 包形 式集成。|
|许可|proprietary|
|参考代码|examples/harmony 对应SDK 模块、 examples/harmony/entry 业务示例,以及 docs/huawei 中的接入文档。|

## 一、产品概述 

HJPlayer 是面向HarmonyOS 直播和点播场景的播放SDK,用于拉流播放、本地/缓存播放、 XComponent 渲染、SEI 回调以及礼物、FaceU 等扩展媒体能力。 

- 核心场景:RTMP/HTTP-FLV 等直播流播放、点播播放、XComponent 渲染、静音/暂 停、时长和播放时间查询。 

- 扩展场景:URL 预加载、下载缓存、SEI UUID 过滤回调、透明礼物播放、人脸检测 /FaceU、运行时RTE 图节点控制。 

- 接入边界:业务层负责URL、缓存目录、XComponent 生命周期和页面关闭流程;SDK 负责native 播放图、解码、渲染、缓存下载和状态回调。 

|**层级**|**主要职责**|**参考路径**|
|---|---|---|
|业务ArkUI 层|创建播放器页面、配置 播放参数、管理 XComponent 和关闭时 机。|examples/harmony/entry/src/main/ets/player|
|SDK ETS 层|暴露HJPlayer、 OpenPlayerInfo、下载 缓存、SEI、|examples/harmony/hjplayer/Index.ets|

||SetWindowInfo 和图节 点接口。||
|---|---|---|
|Native 媒体层|创建播放图、渲染图、|src/entry/player/hsys/verify|
||NativeWindow,并执||
||行解码、同步、缓存和||
||回调。||

## 二、安装和设置步骤 

|**步骤**|**操作**|**说明**|
|---|---|---|
|1|安装HAR 包|执行ohpm install @hj- live/hjplayer,或在entry/oh- package.json5 中使用 file:../hjplayer 做本地联调。|
|2|声明权限|播放网络流需要INTERNET;本 地文件播放不需要额外系统权 限,但缓存目录必须可写。|
|3|导入接口|从@hj-live/hjplayer 导入 HJPlayer、OpenPlayerInfo、 HJPlayerContextInitConfig、 SetWindowInfo、LogMode 等。|
|4|初始化SDK|调用 HJPlayer.contextInit(config)。 当前签名接收 HJPlayerContextInitConfig 对 象,不是旧版多参数签名。|
|5|准备窗口和缓存|使用 XComponentType.SURFACE 获取渲染surface;为 medias_dir、gift、shorts 等配 置应用可写目录。|

### **2.1** 初始化示例 

const config: HJPlayerContextInitConfig = { 

valid: true, 

logDir: '/data/storage/el2/base/haps/entry/files/playerLog/', 

logLevel: 2, logMode: LogMode.CONSOLE | LogMode.FILE, 

maxSize: 5 * 1024 * 1024, maxFiles: 5, medias_dir: '/data/storage/el2/base/haps/entry/files/hjmedias', 

medias_cache_max: 200, 

other_dirs_options: [{ name: '/data/storage/el2/base/haps/entry/files/gift', max: 100 }], 

download_retry_max: 10 

}; 

HJPlayer.contextInit(config); 

## 三、功能操作指南 

|**操作**|**推荐顺序**|**关键接口**|
|---|---|---|
|最小播放|contextInit -> createPlayer -> openPlayer -> setWindow|openPlayer(openPlayerInfo, stateCall, stateInfo, statCall, seiCall?)|
|绑定窗口|surface create/change 时发 送窗口信息;surface destroyed 时发送 TARGET_DESTROY|setWindow(setWindowInfo)|
|关闭播放|先TARGET_DESTROY,再 closePlayer,等待 CLOSEDONE 后 exitPlayer/destroyPlayer|closePlayer(), exitPlayer(), destroyPlayer()|
|静音/暂停|播放器打开后按业务状态调用|setMute(), setPause()|
|进度查询|播放器打开后查询|getDuration(), getCurrentTimestamp()|
|下载缓存|初始化缓存目录后发起下载; 保存rid 以便取消|download(), cancelDownload(), preloadUrl()|
|SEI 回调|OpenPlayerInfo 中配置 m_enableSEIUUids,并传入 seiCall|setEnableSEIUUids(), seiCall|

|礼物/FaceU/图节点|在播放器handle 有效后启用|openFaceu(), nodeEnable(),|
|---|---|---|
||扩展能力|nodeSetParam()|

### **3.1** 打开播放器 

const hjPlayer = new HJPlayer(); 

hjPlayer.createPlayer(); 

const openPlayerInfo: OpenPlayerInfo = { 

url, 

localDir: '/data/storage/el2/base/haps/entry/files/hjmedias', rid: '', fps: 30, repeats: 0, 

videoCodecType: HJPlayerVideoCodecType.HJPlayerVideoCodecType_OHCODEC, 

sourceType: HJPlayerSourceType.HJPlayerSourceType_SERIES, 

playerType: HJPlayerType.HJPlayerType_LIVESTREAM, bSplitScreenMirror: false, disableMFlag: 0, m_graphConfig: '', m_enableSEIUUids: new Map<string, boolean>() 

}; 

hjPlayer.openPlayer(openPlayerInfo, stateCall, { uid: 2342, device: 'Harmony', sn: 'HJPlayer' }, statCall, seiCall); 

### **3.2** 绑定 **XComponent** 

hjPlayer.setWindow({ 

classStyle: HJRteGraphConfig.HJNodeClass_TargetUI_0, 

insName: HJRteGraphConfig.HJNodeClass_TargetUI_0, 

surfaceId, 

width: rect.surfaceWidth, height: rect.surfaceHeight, state: SetWindowState.TARGET_CHANGE 

}); 

**说明:** HJPlayer.ets 只有在isOpen=true 后才向native 下发setWindow,因此示例采用先 openPlayer,再由XComponent surface 回调绑定窗口。 

### **3.3** 关闭播放器 

hjPlayer.setWindow({ 

classStyle: HJRteGraphConfig.HJNodeClass_TargetUI_0, 

insName: HJRteGraphConfig.HJNodeClass_TargetUI_0, surfaceId, width: 0, height: 0, state: SetWindowState.TARGET_DESTROY }); hjPlayer.closePlayer(); // 在 HJ_PLAYER_NOTIFY_CLOSEDONE 回调中: hjPlayer.exitPlayer(); hjPlayer.destroyPlayer(); 

### **3.4** 下载缓存 

```arkts
const info: HJPlayerDownloadInfo = { url, dir: '/data/storage/el2/base/haps/entry/files/hjmedias', rid: '', preCacheSize: -1, priority: 1 }; const rid = HJPlayer.download(info, (json: string) => { const notify = JSON.parse(json); }); HJPlayer.cancelDownload(rid); 
```

## 四、常见问题解答 

|**问题**|**回答**|
|---|---|
|HJPlayer.contextInit 应该怎么调用?|当前版本接收HJPlayerContextInitConfig 对象;不要 使用旧版contextInit(valid, logDir, ...) 多参数写法。|
|setWindow 可以在openPlayer 前调 用吗?|当前ETS 封装会在isOpen=false 时忽略 setWindow。推荐先openPlayer,再绑定 XComponent surface。|
|closePlayer 后能马上destroyPlayer 吗?|不建议。closePlayer 是异步关闭,必须等待 HJ_PLAYER_NOTIFY_CLOSEDONE 后再exitPlayer 和 destroyPlayer。|
|直播和点播如何区分?|通过OpenPlayerInfo.playerType 指定 HJPlayerType_LIVESTREAM 或HJPlayerType_VOD, 业务也可根据URL 协议做默认判断。|
|SEI 为什么没有回调?|确认m_enableSEIUUids 使用Map<string, boolean>,UUID 与流内数据一致,并传入seiCall。|
|下载缓存目录怎么选?|使用应用沙箱可写目录,例如 /data/storage/el2/base/haps/entry/files/hjmedias, 并配置medias_cache_max。|

## 五、故障排除 

|**现象**|**排查方向**|**处理建议**|
|---|---|---|
|画 面 不 显 示|openPlayer 是否成功, XComponent surface 是否 创建, setWindow 是否被 isOpen 放 行。|先查看stateCall 回调;确认onSurfaceCreated/onSurfaceChanged 后 发送TargetUI 节点和有效尺寸。|
|播 放 失 败 或|URL 可达性、 协议、网络、 解码方式、缓 存目录。|用浏览器或命令行验证URL;切换videoCodecType;确认日志目录和缓 存目录可写。|

|首 帧 慢|||
|---|---|---|
|没 有 声 音|静音状态、音 频流、系统音 量。|确认没有调用setMute(true),检查 HJ_PLAYER_NOTIFY_AUDIO_START_BUFFERING/STOP_BUFFERING。|
|退 出 崩 溃|释放顺序和异 步关闭。|按TARGET_DESTROY -> closePlayer -> CLOSEDONE -> exitPlayer - > destroyPlayer 顺序释放。|
|SEI 无|UUID 配置、 seiCall、流内|打印m_enableSEIUUids;确认key 帧SEI 过滤参数与业务预期一致。|
|数|是否携带||
|据|SEI。||
|下|URL、rid、目|确认HJPlayer.download 返回rid;检查notify.totalSize/validSize;必|
|载|录、磁盘空间|要时cancelDownload 后重试。|
|无 进 度|和回调解析。||

## 六、发布前检查清单 

- 确认oh-package 依赖使用正确包名@hj-live/hjplayer。 

- 确认宿主声明INTERNET 权限,缓存目录位于应用可写目录。 

- 确认contextInit 使用HJPlayerContextInitConfig 对象,并配置合理的日志和缓存上 限。 

- 确认打开、关闭、页面切换、切后台、网络弱化、重复进入播放页等场景无崩溃。 

- 确认问题定位时能提供SDK 日志、播放URL、OpenPlayerInfo、stateCall 和statCall 回调日志。 

## 七、参考路径 

- SDK 导出:examples/harmony/hjplayer/Index.ets 

- SDK 封装:examples/harmony/hjplayer/src/main/ets/native/HJPlayer.ets 

- 业务示例:examples/harmony/entry/src/main/ets/player 

- 下载示例:examples/harmony/entry/src/main/ets/player/pages/PlayerPage.ets 

- 接入文档:docs/huawei/hjplayer/HJPlayer SDK 接入文档.docx
