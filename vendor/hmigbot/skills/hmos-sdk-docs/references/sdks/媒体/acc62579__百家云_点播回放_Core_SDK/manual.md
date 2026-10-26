# # 鸿蒙 点播回放 Core SDK 

###### 鸿蒙 点播回放 Core SDK 

N. 简介 

N.N. 功能描述 

O. 快速集成 

O.N. 包依赖 

O.O. 初始化 SDK 

P. 点播部分 

P.N. 播放视频 

P.N.N. 创建播放器 

P.N.O. 视频渲染视图(XComponent) 

P.N.P. 绑定视频源 

P.O. 设置播放器 

P.O.N. 设置参数 

P.O.O. 获取播放器状态 

P.O.P. 视频控制 

P.P. 设置监听 

P.P.N. 播放器状态 

P.P.O. 播放进度 

P.P.P. seek 结束 

P.P.Q. 播放出错 

P.P.S. token 失效 

P.Q. 其它功能 

P.Q.N. 字幕 

P.Q.O. 弹题 

P.Q.P. 关键帧(书签) 

P.Q.Q. 水印 

P.Q.S. 视频缓存 

P.Q.T. EVO 加密 

1 

###### P.Q.V. 视频统计上报 

###### Q. 回放部分 

###### Q.N. 快速集成 

   - Q.N.N. 创建播放器 

   - Q.N.O. 创建 PBRoom 

   - Q.N.P. 绑定播放器 

   - Q.N.Q. 进入房间 

   - Q.N.S. 绑定课件 

- Q.O. 聊天 

- Q.P. 获取在线人员 

- Q.Q. 监听视频开关状态 

- Q.S. 教室工具 

   - Q.S.N. 公告 

   - Q.S.O. 答题器 

   - Q.S.P. 问答 

   - Q.S.Q. 红包(鸿蒙新增) 

- Q.T. 退出房间 

###### S. 下载 

###### S.N. DownloadManager 

###### S.N.N. 设置缓存路径(必需,必须在 loadDownloadInfo 之前) 

   - S.N.O. 加载下载记录 

   - S.N.P. 设置清晰度匹配规则 

   - S.N.Q. 获取下载记录 / 删除 

- S.O. 点播下载 

- S.P. 回放下载 

- S.Q. 下载状态回调 

###### S.S. DownloadTask 接口 

###### S.T. DownloadModel 字段说明 

###### T. 接口说明 

###### T.N. PlayerStatus 

###### T.O. VideoDefinition 

###### T.P. BJYVideoInfo 

2 

###### T.Q. VideoItem 关键字段 

- V. 错误码 

- W. 平台适配差异(鸿蒙 vs Android) 

- X. 已知限制 

## 鸿蒙 点播回放 Core SDK 

- 包名: `@baijia/videoplayer` (har 包) 

- OHPM 仓 库: `https://ohpm.openharmony.cn/#/cn/detail/@baijia%2Fvideoplayer` 

- Platform:HarmonyOS NEXT,runtimeOS: `HarmonyOS` ,compileSdkVersion: `6.0.2(22)` 

- IDE:DevEco Studio 6.0.2 Release(请通过 GUI 编译部署) 

- 底层依赖: `@baijia/ijkplayer` v2.0.6(har 预编译包) 

### 1. 简介 

一 百家云鸿蒙端点播回放 Core SDK 是一个集点播和回放于 体的无 UI 纯实现库,点播功能包括在线视 频、本地播放、视频缓存;回放功能在点播播放器基础上叠加 PPT、聊天、答题、画笔、在线人员等模 块,支持离线回放,还原直播场景。 

- 鸿蒙端实现逐行对齐 Android `videoplayer-core` 接口,并做了平台适配: 

- Android `bindPlayerView(BJYPlayerView)` → 鸿蒙端 `setContext(XComponent con text, string id)` (直接绑定 `XComponent` 的 surface) 

- Android `RxJava Observable` → 鸿蒙端 `Promise` 或自定义 `LPEventEmitter<T>` 

- Android `BJYPlayerSDK.Builder` 链式初始化 → 鸿蒙端在 Core 层提供 `BJYPlayerConf ig` 单例配置(UI 层再封装 `BJYPlayerSDKBuilder` ,见 UI 文档 §2.4) 

#### 1.1. 功能描述 

功能 描述 在线播放 支持百家云后台配置视频播放(鉴权、清晰度、 CDN) 播放器视图 通过 `XComponent` 承载渲染,无 UI 控件 

3 

|视频缓存|LRU缓存,基于 `relationalStore` 持久化|
|---|---|
||( `VideoCacheManager`)|
|离线播放|支持下载后的本地视频/回放,加密/不加密均支 持|
|回放|PPT、聊天、答题、画笔、在线人员、公告、红 包等信令模块|
|下载|点播下载、回放下载,断点续传,CDN兜底|

### 2. 快速集成 

#### 2.1. 包依赖 

`oh-package.json5` 引入: 

- `{ 2 "dependencies": { 3 "@baijia/videoplayer": "^1.0.0" 4 } 5 }` 

`@baijia/videoplayer` 已传递依赖 `@baijia/ijkplayer` ,无需额外声明。 

#### 2.2. 初始化 SDK 

通过 `BJYPlayerConfig` 单例配置全局参数(鸿蒙端在 Core 层等价于 Android `BJYPlayerSDK. Builder` )。 

- `import { BJYPlayerConfig, DeployType } from '@baijia/videoplayer';` 

- `const config = BJYPlayerConfig.getInstance(); 4 config.customDomain = 'demo123';        //` 专属域名前缀 `5 config.isEncrypt = true;                //` 启用加密 `6 config.isDevelopMode = false;            //` 正式发布请置 `false 7 config.deployType = DeployType.PRODUCTION;` 

`BJYPlayerConfig` 全部可配置项( `videoplayer/src/main/ets/config/BJYPlayerConfi g.ets:25` ): 

4 

|字段|类型|默认值|说明|行号|
|---|---|---|---|---|
|`customDomain`|`string`|`''`|专属域名前缀, 例如 `demo123.` `at.baijiayun.` `com` 中的 `dem` `o123`|29|
|`environmentI` `nfix`|`string`|`'at'`|域名中缀(私有 化部署使用)|31|
|`environmentS` `uffix`|`string`|`'baijiayun.c` `om'`|域名后缀|33|
|`apiPrefix`|`string`|`'www'`|API前缀|35|
|`deployType`|`DeployType`|`PRODUCTION`|部署环境( `TES` `T`=0 / `BETA`=1 / `PR` `ODUCTION`=2)|37|
|`isEncrypt`|`boolean`|`false`|是否加密,对在 线播放和下载均 有效|39|
|`isDevelopMod` `e`|`boolean`|`false`|开发者模式,开 启后打印关键日 志,正式发版请 关闭|41|

###### 工具方法: 

`1 config.getApiBaseUrl(): string;     //` 根据 `customDomain + deployType` 拼接 `A PI host 2 config.getClickUrl(): string;       //` 统计上报域名 

Android 端 `BJYPlayerSDK.STATIC_PPT_DEFAULT_SIZE` 、 `DISABLE_ANIM_PPT` 、 `waterM ark` 等全局静态字段,在鸿蒙端归到 UI 层 `BJYPlayerSDK` 类(详见 UI 文档 §2.4)。Core 层只 保留与播放器引擎相关的全局配置。 

### 3. 点播部分 

5 

#### 3.1. 播放视频 

##### 3.1.1. 创建播放器 

通过 `VideoPlayerFactory` 创建播放器( `videoplayer/src/main/ets/player/VideoPlay erFactory.ets:12` )。 

- `import { VideoPlayerFactory, IBJYVideoPlayer } from '@baijia/videoplayer';` 

- `const videoPlayer: IBJYVideoPlayer = VideoPlayerFactory.createPlayer();` 

|API|用途 行号|
|---|---|
|`static createPlayer():`|创建标准点播/回放播放器 18|
|`IBJYVideoPlayer`||
|`static createMixedPlay`|创建合并回放专用播放器(对齐 26|
|`er(): BJYVideoPlayerMix`|Android `Builder.setMixe`|
|`edImpl`|`dPlayback(true).build()` )|

Android 的 `VideoPlayerFactory.Builder` 链式参数( `setSupportLooping` / `setSuppo rtBackgroundAudio` / `setSupportBreakPointPlay` / `setLifecycle` 等)在鸿蒙端未 实现 Builder 模式,请通过 `IBJYVideoPlayer` 实例上的 setter 在创建后设置(见 §3.2.1)。 

##### 3.1.2. 视频渲染视图(XComponent) 

一 鸿蒙端不存在 `BJYPlayerView` 组件,统 使用 `XComponent` 承载视频渲染。声明 `XComponen` `t` 时必须指定 `libraryname: 'ijkplayer_napi'` ,并把 `XComponentController` 上下文 和 id 通过 `setContext(context, id)` 交给播放器(对应 Android `bindPlayerView` )。 

6 

`1 @Entry 2 @Component 3 struct PlayerPage { 4 private xComponentController: XComponentController = new XComponentContr oller(); 5 private xComponentId: string = 'videoXComponent'; 6 private videoPlayer: IBJYVideoPlayer = VideoPlayerFactory.createPlayer() ; 7 8 build() { 9 Stack() { 10 XComponent({ 11 id: this.xComponentId, 12 type: XComponentType.SURFACE, 13 libraryname: 'ijkplayer_napi', 14 controller: this.xComponentController 15 }) 16 .onLoad((event?: object) => { 17 // event` 由 `ijkplayer_napi` 注入,包含 `native context 18 this.videoPlayer.setContext(event as object, this.xComponentId); 19 }) 20 .width('100%') 21 .height(200) 22 } 23 } 24 }` 

视频画面裁剪/比例由 `XComponent` 的尺寸约束自行实现,Core SDK 不再提供 `AspectRatio` 枚举。 

##### 3.1.3. 绑定视频源 

`IBJYVideoPlayer` 提供 3 个数据源入口( `videoplayer/src/main/ets/player/IBJYVide oPlayer.ets` ): 

7 

`1 //` 在线视频(视频 `ID + token` , `accessKey` 可传空串) `2 setupOnlineVideoWithId(videoId: number, token: string, accessKey: string): void;   // line 41 3 4 //` 在线视频(已构建好的 `VideoItem` ) `5 setupOnlineVideoWithVideoItem(videoItem: VideoItem): void; // line 47 6 7 //` 本地视频( `DownloadManager` 下载后的 `DownloadModel` ) `8 setupLocalVideoWithDownloadModel(downloadModel: object): void; // line 35` 

设置完视频源后是否自动播放由 `setAutoPlay(boolean)` 决定,默认自动播放。 

#### 3.2. 设置播放器 

##### 3.2.1. 设置参数 

|`IBJYVideoPlayer` 提供的set|ter API( `videoplayer/src/ma`|`in/ets/player/IBJYVideoPl`|
|---|---|---|
|`ayer.ets`):|||
|API|说明|行号|
|`setUserInfo(userName:`|设置第三方用户信息,用于后台|128|
|`string, userIdentity:`|统计||
|`string): void`|||
|`setUserGroup(group: nu`|设置用户分组|131|
|`mber): void`|||
|`supportBackgroundAudio` `(enable: boolean):` `void`|是否后台播放音频|137|
|`supportLooping(loopin` `g: boolean): void`|是否循环播放|143|
|`setAutoPlay(autoPlay:` `boolean): void`|setup后是否自动播放|8 149|

enableBreakPointMemory 启用断点续播 152
(helper: BreakPointMemo
ryHelper, videoId: stri
ng): void
setPlayRate(rate: numb 倍速播放  [0.5 ~ 2.0]  134
er): void

##### 3.2.2. 获取播放器状态 

- `getCurrentPosition(): number;        //` 当前位置(秒) `line 76 2 getDuration(): number;               //` 视频总时长(秒) `line 79 3 getBufferPercentage(): number;       //` 缓冲百分比 `line 82 4 getPlayRate(): number;               //` 当前倍速 `line 88 5 isPlaying(): boolean;                //` 是否正在播放 `line 73 6 isPlayLocalVideo(): boolean;         //` 是否播放本地视频 `line 94 7 getPlayerStatus(): PlayerStatus;     //` 播放状态枚举(见 `§6.1` ) `line 85 8 getVideoInfo(): BJYVideoInfo | null; //` 视频信息(见 `§6.3` ) `line 91 9 getVideoMemoryPoint(): number;       //` 记忆播放位置 `line 100` 

- `getMediaPlayerDebugInfo(): object;   //` 调试信息 `line 97 11 getVideoWidth(): number;             //` 解码视频宽度(像素) `line 205 12 getVideoHeight(): number;            //` 解码视频高度(像素) `line 208 13 getBreakPoint(): number;             //` 断点位置(毫秒),无则 `0     line 155` 

##### 3.2.3. 视频控制 

- `play(): void;                                  // line 50 2 playFromOffset(startOffset: number): void;     //` 从指定秒数开始播放(对齐 `Andr oid play(int startOffset)` ) `line 53` 

- `rePlay(): void;                                // line 56 4 pause(): void;                                 // line 59 5 stop(): void;                                  // line 62 6 seekTo(timeSec: number): void;                 // seek` 到指定秒数(对齐 `Andro id seek(int)` ) `line 65` 

- `release(): void;                               // line 68` 

###### 清晰度与 CDN: 

9 

- `setPreferredDefinitions(definitions: VideoDefinition[]): void;   //` 清晰度偏 好(按数组顺序优先匹配) `line 114` 

- `changeDefinition(definition: VideoDefinition): boolean;          //` 切换清晰 度,播放中调用 `line 108` 

- `getCDNCount(): number;                                            // CDN` 线 路数量 `line 117` 

- `setCDNIndex(index: number): void;                                 //` 切换 `C DN` 线路 `line 120` 

- `getCDNIndex(): number;                                            //` 当前 `C DN` 线路 `index               line 123` 

###### 清晰度优先级示例: 

- `import { VideoDefinition } from '@baijia/videoplayer';` 

- `2` 

- `const preferred: VideoDefinition[] = [` 

- `VideoDefinition._720P, 5 VideoDefinition.SHD, 6 VideoDefinition.HD, 7 VideoDefinition.SD, 8 VideoDefinition._1080P,` 

- `VideoDefinition.Audio,` 

- `]; 11 videoPlayer.setPreferredDefinitions(preferred);` 

#### 3.3. 设置监听 

##### 3.3.1. 播放器状态 

```
1import { OnPlayerStatusChangeListener, PlayerStatus } from'@baijia/videop
layer';
```

- `class MyStatusListener implements OnPlayerStatusChangeListener { 4 onStatusChange(status: PlayerStatus): void {` 

- `if (status === PlayerStatus.STATE_PREPARED) { 6 //` 数据已准备好 `7 } 8 } 9 }` 

- `videoPlayer.addOnPlayerStatusChangeListener(new MyStatusListener());` 

⚠ ArkTS 严格模式不允许匿名对象字面量实现接口,必须用具名 class。 

10 

|`IBJYVideoPlayer` 监 add / remove|听器汇总( `IBJYVideoP` 监听接口|`layer.ets`): 说明|行号|
|---|---|---|---|
|`addOnPlayerStatu` `sChangeListener` / `removeOnPlayer` `StatusChangeList` `ener`|`OnPlayerStatusCh` `angeListener`|状态变化|212-213|
|`addOnPlayingTime` `ChangeListener`/ `removeOnPlayingT` `imeChangeListene` `r`|`OnPlayingTimeCha` `ngeListener`|播放进度|215-216|
|`addOnBufferingLi` `stener`/ `removeO` `nBufferingListen` `er`|`OnBufferingListe` `ner`|缓冲开始/结束|218-219|
|`addOnPlayerError` `Listener`/ `remov` `eOnPlayerErrorLi` `stener`|`OnPlayerErrorLis` `tener`|播放出错|221-222|
|`addOnPlayerLagLi`|`OnPlayerErrorLis`|卡顿|225-226|
|`stener`/ `removeO` `nPlayerLagListen` `er`|`tener`|||
|`addOnSeekComplet` `eListener`/ `remo`|`OnSeekCompleteLi` `stener`|seek结束|228-229|
|`veOnSeekComplete` `Listener`||||
|`addOnVideoSizeCh`|`OnVideoSizeChang`|视频宽高变化|231|
|`angeListener`|`eListener`|||

11 

|`addOnFirstFrameL`|`OnFirstFrameList`|首帧渲染|234-235|
|---|---|---|---|
|`istener`/ `remove`|`ener`|||
|`OnFirstFrameList`||||
|`ener`||||
|`addOnVideoTypeCh`|`OnVideoTypeChang`|视频类型变化(片头/|238-239|
|`angeListener`/ `r`|`eListener`|正片/片尾)||
|`emoveOnVideoType`||||
|`ChangeListener`||||
|`addOnSeekSwitchV`|`OnSeekSwitchVide`|合并回放切换视频|245|
|`ideoListener`|`oListener`|||
|`setOnTokenInvali`|`OnTokenInvalidLi`|token失效|247|
|`dListener`|`stener`|||

##### 3.3.2. 播放进度 

- `import { OnPlayingTimeChangeListener } from '@baijia/videoplayer';` 

- `class MyTimeListener implements OnPlayingTimeChangeListener { 4 // currentTime:` 当前位置(秒) 

- `// duration:` 总时长(秒) `6 onPlayingTimeChange(currentTime: number, duration: number): void { } 7 } 8 videoPlayer.addOnPlayingTimeChangeListener(new MyTimeListener());` 

##### 3.3.3. seek 结束 

###### 接口签名( `listeners/OnSeekCompleteListener.ets:5` ): 

- `export interface OnSeekCompleteListener {` 

- `// beforeSeekPosition: seek` 前位置(秒) 

- `// seekPosition:       seek` 目标位置(秒) 

- `onSeekComplete(beforeSeekPosition: number, seekPosition: number): void; 5 }` 

##### 3.3.4. 播放出错 

12 

###### 接口签名( `listeners/OnPlayerErrorListener.ets:7` ),错误信息以 `LPError` (重导自 `@baijia/livebase` )描述: 

- `export interface OnPlayerErrorListener {` 

- `onError(error: LPError): void; 3 }` 

##### 3.3.5. token 失效 

###### 接口签名( `listeners/OnTokenInvalidListener.ets` ): 

- `export interface OnTokenFetchedListener { 2 onTokenFetchSuccess(token: string): void; 3 } 4 5 export interface OnTokenInvalidListener { 6 onTokenInvalid(vid: string, callback: OnTokenFetchedListener): void; 7 }` 

- `class MyTokenListener implements OnTokenInvalidListener { 2 onTokenInvalid(vid: string, callback: OnTokenFetchedListener): void { 3 //` 调用集成方业务后端获取新 `token 4 const newToken = await fetchToken(vid); 5 callback.onTokenFetchSuccess(newToken); 6 } 7 } 8 videoPlayer.setOnTokenInvalidListener(new MyTokenListener());` 

#### 3.4. 其它功能 

##### 3.4.1. 字幕 

|`1`|`addCubChangeListener(listener: OnCubChangeListener):void;// lin` `e 160`|
|---|---|
|`2`|`toggleSubtitleEngine(shutDown: boolean):void;// lin` `e 163`|
|`3`|`changeSubtitlePath(subtitlePath: string):void;//`单|
||语`line 166`|
|`4`|`changeSubtitlePathBilingual(subtitleZhPath: string,subtitleEnPath: string)` `:void; //`双语`line 169`|
|`5`|`subtitleDefaultEnabled():boolean;//`默 认是否开启`line 172`|

13 

字幕引擎实现: `subtitle/SubtitleEngine.ets` 、 `subtitle/WebVttParser.ets` ,支持 WebVTT 格式。 

##### 3.4.2. 弹题 

- `getVideoQuizList(videoId: string, userNumber: string, token: string, 2 listener: OnVideoQuizListUpdateListener): void;     // lin e 191` 

- `sendVideoQuizAnswer(answerMap: Map<string, string>): void;           // lin e 195` 

##### 3.4.3. 关键帧(书签) 

- `requestKeyFrameModel(videoId: string): Promise<KeyFrameModel>;       // lin e 200` 

##### 3.4.4. 水印 

水印通过 `WatermarkOverlay` ( `widget/WatermarkView.ets` )ArkUI 组件叠加在 `XCompon ent` 之上,支持四⻆定位( `WatermarkPosition` )。 

- `import { WatermarkOverlay, WatermarkInfo, WatermarkPosition } from '@baiji a/videoplayer';` 

- `const info = new WatermarkInfo(); 4 info.url = 'https://...'; 5 info.position = WatermarkPosition.LEFT_TOP;` 

服务端配置的水印通过 `IBJYVideoPlayer.getVideoInfo()` → `VideoItem.waterMark` 透 传。 

##### 3.4.5. 视频缓存 

`VideoCacheManager` ( `cache/VideoCacheManager.ets` )使用 `relationalStore` LRU 缓存视频片段。 

`relationalStore` 无同步 API( `querySync` 等不存在),调用全部走 `async` 。 

##### 3.4.6. EV2 加密 

14 

`Ev2Decoder` ( `crypto/Ev2Decoder.ets` )解码加密视频 URL,加密视频对应 CDN 的 `enc_u rl` 字段。 

##### 3.4.7. 视频统计上报 

`StatisticsReporter` ( `network/StatisticsReporter.ets` )按 `reportInterval` 周 期向 `getClickUrl()/gs.gif` 上报播放行为,无需手动调用。 

### 4. 回放部分 

#### 4.1. 快速集成 

##### 4.1.1. 创建播放器 

参考 §3.1.1。 

##### 4.1.2. 创建 PBRoom 

鸿蒙端 PBRoom 实现类 `PBRoomImpl` ( `videoplayer/src/main/ets/playback/PlaybackR oom.ets` )通过静态工厂方法创建,对齐 Android `BJYPlayerSDK.newPlayBackRoom()` 系列重 载: 

|`import {PBRoomImpl, ` `1`|`PBRoom, DownloadModel }from '@baijia/videoplayer';`|
|---|---|
|工厂方法|用途 行号|
|`static createOnlineSim`|普通在线回放 329|
|`ple(classId: number, to`||
|`ken: string): PBRoomImp` `l`||
|`static createOnlineWit`|长期课分段回放 336|
|`hSession(classId: numbe`||
|`r, sessionId: number, t`||
|`oken: string): PBRoomIm`||
|`pl`|15|

|`static createOnline(cl`|裁剪回放(version为裁剪版|343|
|---|---|---|
|`assId: number, sessionI`|本)||
|`d: number, version: num`|||
|`ber, token: string): PB`|||
|`RoomImpl`|||
|`static createMixed(mix`|合并回放|363|
|`edId: string, mixedToke`|||
|`n: string): PBRoomImpl`|||
|`static createOffline(v`|离线回放|353|
|`ideoDownloadModel: Down`|||
|`loadModel, signalDownlo`|||
|`adModel: DownloadMode`|||
|`l): PBRoomImpl`|||

###### 示例: 

- `const pbRoom: PBRoom = PBRoomImpl.createOnlineWithSession(classId, sessionI d, classToken);` 

##### 4.1.3. 绑定播放器 

- `pbRoom.bindPlayer(videoPlayer);                  //` 主播放器 `2 pbRoom.bindCloudVideoPlayer(secondaryPlayer);    //` 可选:云端视频副播放器 

###### `PBRoom` 接口( `videoplayer/src/main/ets/playback/PlaybackInterfaces.ets:60` ) 

|主要API: |||
|---|---|---|
|API|说明|行号|
|`enterRoom(listener: LP`|进入回放房间|61|
|`LaunchListener): void`|||
|`bindPlayer(videoPlaye`|绑定主播放器|64|
|`r: IBJYVideoPlayer): vo`|||
|`id`|||

16 

|`bindCloudVideoPlayer(v` `ideoPlayer: IBJYVideoPl` `ayer): void`|绑定云端视频副播放器|67|
|---|---|---|
|`getPlayer(): IBJYVideo` `Player | null`|获取已绑定的播放器|70|
|`quitRoom(): void`|退出房间,释放资源|115|
|`isPlaybackOffline(): b` `oolean`|是否离线回放|127|
|`getRecordType(): numbe` `r`|录制类型(0普通/ 1大班 webrtc / 2小班webrtc / 3合 流)|133|
|`getTemplateType(): str` `ing`|模板类型字符串(如 "6"、"12")|175|
|`isVideoMain():` `boolean`|是否视频主区域|181|
|`getRoomId(): number`/ `getRoomToken():` `string`/ `getPlaybackId` `(): number`|房间元信息|148/151/154|
|`setOnSwitchPlaybackLis` `tener(listener: OnSwitc` `hPlaybackListener): voi` `d`|合并回放切换回调|178|

##### 4.1.4. 进入房间 

17 

`1 import { LPLaunchListener, PBRoom, PBLPError } from '@baijia/videoplayer'; 2 3 class MyLaunchListener implements LPLaunchListener { 4 onLaunchSteps(step: number, totalStep: number): void { 5 // step / totalStep` 即进房间进度百分比 `6 } 7 onLaunchError(error: PBLPError): void { } 8 onLaunchSuccess(room: PBRoom): void { } 9 } 10 pbRoom.enterRoom(new MyLaunchListener());` 

##### 4.1.5. 绑定课件 

鸿蒙端 PPT 组件 `PPTView` ( `videoplayer/src/main/ets/playback/PlaybackPPT.ets` , 从 `index.ets:61` 公开导出)由 `PPTController` 驱动: 

`1 import { PPTView, PPTController } from '@baijia/videoplayer'; PPTController` 内部从 `PBRoom` 信令引擎接收翻页、画笔事件并驱动 `PPTView` 渲染。详细参 数请参考 UI 模块中 `PBRoomPage` 的使用示例。 

#### 4.2. 聊天 

|`pbRoom.getChatVM().getObservableOfNotifyDataChange()` `.subscribe((messages: LPMessageModel[]) => {` `//`当前时刻的聊天消息集合 `});` `1` `2` `3` `4`|
|---|
|ViewModel 接口 说明|
|`LPChatViewModel` `getChatVM()` 聊天|
|`LPDocListViewModel` `getDocListVM()` 课件列表|
|`LPOnlineUsersViewModel` `getOnlineUserVM()` 在线人员|
|`LPToolBoxViewModel` `getToolBoxVM()` 答题/问答/测验|

#### 4.3. 获取在线人员 

18 

- `pbRoom.getOnlineUserVM().getObservableOfOnlineUser()` 

- `.subscribe((users: LPMessageUserModel[]) => { 3 //` 当前在线人员集合 `4 });` 

#### 4.4. 监听视频开关状态 

- `const recordType: number = pbRoom.getRecordType();   // 0/1/2/3` 

- `2` 

- `pbRoom.getObservableOfVideoStatus()` 

- `.subscribe((isVideoOn: boolean) => {` 

- `if (recordType !== 1 && recordType !== 3) {` 

- `// isVideoOn = false` 时可显示占位图 

- `}` 

- `});` 

#### 4.5. 教室工具 

##### 4.5.1. 公告 

- `pbRoom.getObservableOfAnnouncementChange() 2 .subscribe((announcement: IAnnouncementModel) => { 3 announcement.getContent(); 4 announcement.getLink(); 5 });` 

##### 4.5.2. 答题器 

- `pbRoom.getToolBoxVM().getObservableOfAnswerStart()` 

- `.subscribe((answer: LPAnswerModel) => {` 

- `answer.messageType; 4 answer.type; 5 });` 

##### 4.5.3. 问答 

19 

- `pbRoom.getToolBoxVM().getObservableOfQuestionQueue()` 

- `.subscribe((items: LPQuestionPullListItem[]) => { });` 

##### 4.5.4. 红包(鸿蒙新增) 

- `pbRoom.getObservableOfRedPackageConfig(playbackId, roomId, token)` 

- `.subscribe((config: RedPacketConfigBean) => { });` 

- `pbRoom.receiveRedPackage(playbackId, userNumber, userName, timeOffset, room Id, token)` 

- `.subscribe((red: RedPacketBean) => { });` 

#### 4.6. 退出房间 

- `// PPT` 资源回收(如使用 `PPTView` ) 

- `pptController.destroy();` 

- `//` 退出房间 

- `pbRoom.quitRoom();` 

### 5. 下载 

#### 5.1. DownloadManager 

###### `DownloadManager` ( `videoplayer/src/main/ets/download/DownloadManager.ets` ) 使用单例模式: 

- `import { DownloadManager } from '@baijia/videoplayer';` 

- `const downloadManager = DownloadManager.getInstance();      // line 77` 

##### 5.1.1. 设置缓存路径(必需,必须在 **`loadDownloadInfo`** 之前) 

- `downloadManager.setTargetFolder(context.filesDir + '/bb_video_downloaded/') ;   // line 90` 

##### 5.1.2. 加载下载记录 

20 

- `// context` 来自 `UIAbilityContext / Context` ; `userIdentify` 、 `reload` 均可选 `2 await downloadManager.loadDownloadInfo(context, userIdentify?, reload?); // line 119` 

鸿蒙端无 Android `Service` 概念,下载基于 `request` Kit + `taskpool` ,应用进入后台后系 统会限制网络任务时长,请在前台保活。 

##### 5.1.3. 设置清晰度匹配规则 

- `downloadManager.setPreferredDefinitionList([` 

- `VideoDefinition.Audio,` 

- `VideoDefinition._720P,` 

- `VideoDefinition.SHD,` 

- `VideoDefinition.HD,` 

- `VideoDefinition.SD,` 

- `VideoDefinition._1080P, 8 ]); // line 106` 

##### 5.1.4. 获取下载记录 / 删除 

- `const tasks: DownloadTask[] = downloadManager.getAllTasks(); 2 downloadManager.deleteTask(task);` 

#### 5.2. 点播下载 

- `const task: DownloadTask = await downloadManager.newVideoDownloadTask(` 

- `'video_filename',    //` 文件名(非法字符自动替换) 

- `videoId,             //` 点播 `vid` 

- `token,               //` 视频 `token` 

- `'extraInfo',         //` 透传字符串 

- `''` 

- `accessKey = ,      //` 可选第三方鉴权 `key` 

- `isEncrypt = true     //` 是否加密(仅当前下载有效) 

- `);` 

- `// DownloadManager.ets line 300` 

#### 5.3. 回放下载 

21 

`1 const task: DownloadTask = await downloadManager.newPlaybackDownloadTask( 2 'playback_filename', 3 roomId,              //` 房间 `ID 4 sessionId,           //` 长期房间分段 `ID` ,非长期传 `0 5 token, 6 'extraInfo', 7 version = -1,        //` 裁剪版本,主版本传 `-1 8 isEncrypt = true 9 ); 10 // DownloadManager.ets line 440` 

#### 5.4. 下载状态回调 

###### 通过 `DownloadTask.setDownloadListener(listener)` 注册: 

```
1import { DownloadListener, DownloadTask } from'@baijia/videoplayer';
2
3classMyDownloadListenerimplementsDownloadListener {
4onProgress(task: DownloadTask): void { }
5onError(task: DownloadTask, e: Error): void { }
6onStarted(task: DownloadTask): void { }
7onPaused(task: DownloadTask): void { }
8onFinish(task: DownloadTask): void { }
9onDeleted(task: DownloadTask): void { }
10}
11task.setDownloadListener(newMyDownloadListener());
```

#### 5.5. DownloadTask 接口 

`download/DownloadModels.ets` : 

22 

- `export interface DownloadTask {` 

- `start(): void; 3 pause(): void; 4 restart(): void; 5 cancel(): void; 6 deleteFiles(): void; 7 setDownloadListener(listener: DownloadListener): void;` 

- `8` 

- `getVideoDownloadInfo(): DownloadModel;` 

- `getSignalDownloadInfo(): DownloadModel | null; 11 getTaskStatus(): TaskStatus;` 

- `getSpeed(): number;             // byte/s 13 getProgress(): number;` 

- `getTotalLength(): number;       //` 总字节数 

- `getDownloadedLength(): number;  //` 已下载字节数 

- `getDownloadType(): DownloadType;` 

- `getVideoFileName(): string;` 

- `getSignalFileName(): string; 19 getVideoDuration(): number; 20 getVideoFilePath(): string; 21 getSignalFilePath(): string; 22 }` 

###### 枚举( `DownloadModels.ets` ): 

|枚举|值|说明|行号|
|---|---|---|---|
|`TaskStatus.New`|0|新建|98|
|`TaskStatus.Downl` `oading`|1|下载中|99|
|`TaskStatus.Pause`|2|暂停|100|
|`TaskStatus.Error`|3|出错|101|
|`TaskStatus.Finis` `h`|4|完成|102|
|`TaskStatus.Cance` `l`|5|已取消|23 103|

|`DownloadType.VID`|0|点播|110|
|---|---|---|---|
|`EO`||||
|`DownloadType.PLA`|1|回放(视频+信令)|111|
|`YBACK`||||
|`FileType.VIDEO`|0|视频|118|
|`FileType.SIGNAL`|1|信令|119|
|`FileType.UNKNOWN`|2|未知|120|
|`FileType.AUDIO`|3|纯音频|121|

#### 5.6. DownloadModel 字段说明 

###### `download/DownloadModels.ets:128` 起。主要字段: 

`1 class DownloadModel { 2 videoId: number;            // vid 3 sessionId: number;          // sessionId 4 roomId: number;             // roomId 5 url: string;                //` 当前 `CDN url 6 definition: VideoDefinition; 7 fileType: FileType; 8 targetName: string;         //` 保存的文件名 `9 targetFolder: string;       //` 保存目录 `10 status: TaskStatus; 11 totalLength: number;        //` 总字节数 `12 downloadLength: number;     //` 已下载字节数 `13 speed: number;              //` 瞬时速度 `14 isEncrypt: boolean; 15 videoToken: string;         //` 视频 `token 16 extraInfo: string;          //` 透传 `17 subtitleItems: SubtitleItem[]; 18 //` 回放节点链表,链尾为信令信息;点播仅链头 `19 nextModel: DownloadModel | null; 20 }` 

### 6. 接口说明 

24 

#### 6.1. PlayerStatus 

```
player/PlayerStatus.ets:4
```

|枚举|值|说明|
|---|---|---|
|`STATE_IDLE`|0|已创建未初始化|
|`STATE_INITIALIZED`|1|数据源已设置|
|`STATE_PREPARED`|2|已准备好,待播放|
|`STATE_STARTED`|3|播放中|
|`STATE_PAUSED`|4|暂停|
|`STATE_STOPPED`|5|停止|
|`STATE_COMPLETED`|6|播放结束|
|`STATE_ERROR`|7|出错|

⚠ 命名与 Android 略有差异:Android 为 `STATE_PLAYBACK_COMPLETED` ,鸿蒙为 `STATE_COM PLETED` 。 

#### 6.2. VideoDefinition 

###### `bean/VideoDefinition.ets:1` 

|枚举|值|服务端键|
|---|---|---|
|`UNKNOWN`|-1|—|
|`SD`|0|`low`|
|`HD`|1|`high`|
|`SHD`|2|`superHD`|
|`_720P`|3|`720p`|
|`_1080P`|4|`1080p`|
|`Audio`|5|`audio`|

辅助函数: 

25 

- `definitionFromString(type: string): VideoDefinition;   // line 29 2 definitionToString(def: VideoDefinition): string;       // line 37` 

#### 6.3. BJYVideoInfo 

###### `bean/BJYVideoInfo.ets:1` 

- `export interface BJYVideoInfo { 2 getVideoId(): number; 3 getDuration(): number;                              //` 服务端返回的时长 (秒) 

- `getDefinition(): VideoDefinition;                   //` 默认清晰度 `5 getSupportedDefinitionList(): VideoDefinition[];    //` 后端转码清晰度集合 `6 getVideoTitle(): string; 7 getSubtitleItemList(): SubtitleItemInfo[];          //` 字幕 `8 }` 

`SubtitleItemInfo` 字段: `id` / `videoId` / `name` / `url` / `zhUrl` / `enUrl` / `isD efault` ,提供静态工厂 `fromJson(json)` 。 

#### 6.4. VideoItem 关键字段 

`bean/VideoItem.ets` ,常用字段: `videoId` / `duration` / `videoName` / `definition` / `playInfo` / `audioUrl` / `subtitleItems` / `waterMark` / `horseLam` `p` / `initPicture` / `startVideo` / `endVideo` / `roomId` / `sessionId` 。 

CDN 信息 `CDNInfo` : `cdn` / `definition` / `url` / `encUrl` / `width` / `height` / `s` `ize` / `weight` 。 

### 7. 错误码 

错误信息封装在 `LPError` ( `@baijia/livebase` ),核心字段: `code: number` / `messag e: string` 。 

常见错误码沿用 Android 约定: 

|错误码|说明|
|---|---|
|-10000、-101|ijkplayer内部错误(文件异常等)|
|10087|视频文件路径错误|

26 

|10088 网络错误||
|---|---|
|-1 无网络连接||
|-2 移动网络播放||
|-4 未知错误||
|-5 没有找到对应清|晰度|
|-6 离线播放传入非|法路径|
|-7 离线播放对应路|径的文件不存在|
|5101 / 5102 / 5103 token异常||
|403 视频地址过期||
|8.平台适配差异(鸿蒙vs Android) 概念 Android|鸿蒙|
|SDK初始化 `BJYPlayerSDK.Builder(t` `his).build()`|Core层: `BJYPlayerConfi` `g.getInstance()`(字段直 赋值);UI层 `BJYPlayerSD` `KBuilder`|
|播放器创建 `VideoPlayerFactory.Bui` `lder()...build()`|`VideoPlayerFactory.cre` `atePlayer()`/ `createMi` `xedPlayer()`|
|视频视图 `BJYPlayerView extends` `FrameLayout`|直接使用 `XComponent`+ `s` `etContext(event, id)`|
|视频比例 `AspectRatio` 枚举|由外层布局尺寸决定|
|异步流 `RxJava Observable`|`Promise` 或 `LPEventEmi` `tter<T>`|
|PBRoom工厂 `BJYPlayerSDK.newPlayBa` `ckRoom(ctx, ...)`|27 `PBRoomImpl.createOnlin` `e*`/ `createMixed`/ `cr` `eateOffline`|

|监听器实现|匿名类/ lambda|必须用具名 `class impleme` `nts`|
|---|---|---|
|关键帧/字幕|`Observable<KeyFrameMod` `el>`|`Promise<KeyFrameModel>`|

### 9. 已知限制 

1. ArkTS 严格模式:不允许 `any` / `unknown` / 匿名对象字面量实现接口,监听器必须用具名 class, `throw` 只能抛 `Error` 子类。 

2. `IjkMediaPlayer` 参数全部 string 类型:例如 `seekTo(ms.toString())` 、 `setSpeed(\` ${rate}f`) 、 setVolume(vol.toString(), 

vol.toString())`。 

3. `@baijia/ijkplayer` 由 `@baijia/videoplayer` 传递依赖,业务方无需单独声明,但 `X` `Component` 必须正确设置 `libraryname: 'ijkplayer_napi'` ,否则找不到 native 库。 

4. `relationalStore` 无同步 API,缓存/下载记录全部 `async` 。 

5. JSON 字段名为 snake_case( `play_info` 、 `cdn_list` 、 `enc_url` 、 `vod_default_de finition` 等),在 `fromJson()` 中手动映射。 

6. `onPrepared` 后需手动 `start()` :即使设置了 `start-on-prepared=1` ,状态机需显式 更新。 

7. 后台播放限制:鸿蒙系统对后台网络/媒体任务时长有限制,超长后台播放需要使用 ContinuousTask(持续任务)申请。 

28
