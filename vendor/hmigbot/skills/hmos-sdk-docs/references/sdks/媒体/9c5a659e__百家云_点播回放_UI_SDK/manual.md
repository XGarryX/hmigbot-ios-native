# # 鸿蒙 点播回放 UI SDK 

###### 鸿蒙 点播回放 UI SDK 

- N. 简介 

- O. 快速集成 

   - O.N. 包依赖 

O.O. 公开导出(VideoPlayerUi/Index.ets) 

   - O.P. 初始化 SDK 

   - O.Q. BJYPlayerSDK 全局静态配置 

- P. 快速集成 

   - P.N. 调起点播播放页面 

   - P.O. 调起回放播放页面 

P.P. Page 路由注册 

P.Q. VideoPlayerConfig 

- P.S. 回放合集 

P.T. 点播签到 

- P.V. 点播分享 

- P.W. 点播/回放试看 

- P.X. 点播/回放禁止拖拽 

P.NL. HorseLampConfig / NotificationConfig 

- Q. 功能介绍 

   - Q.N. 包结构 

   - Q.O. 自定义点播 UI 

   - Q.P. UI 组件清单 

- S. 回调注入 - CallbackManager 

   - S.N. 获取实例 

   - S.O. 注册 / 注销 API 

   - S.P. 接口签名 

- T. 平台适配差异(鸿蒙 vs Android) 

- V. 已知限制 

1 

W. 完整对外导出清单 

## 鸿蒙 点播回放 UI SDK 

- 包名: `@baijia/videoplayerui` (har 包) 

- OHPM 仓库: `https://ohpm.openharmony.cn/#/cn/detail/@baijia%2Fvideoplayer ui` 

- Core 仓库: `https://ohpm.openharmony.cn/#/cn/detail/@baijia%2Fvideoplayer` 

- 依赖: `@baijia/videoplayer` (Core SDK,详见 Core 文档) 

- Platform:HarmonyOS NEXT,runtimeOS: `HarmonyOS` ,compileSdkVersion: `6.0.2(22)` 

- IDE:DevEco Studio 6.0.2 Release 

### 1. 简介 

带 UI 的点播 / 回放 SDK 基于 Core SDK,提供标准的 ArkUI 实现,方便快速集成。鸿蒙端使用 `@Ent ry({ routeName })` 装饰器注册命名路由,由 `router.pushNamedRoute` 调起,等价于 Android 通过 `Intent` 调起 `Activity` 。 

鸿蒙端实现与 Android `videoplayer-ui` 接口逐行对齐,平台差异主要体现在: 

- Android `Activity` → 鸿蒙 `@Entry({ routeName }) struct` Page 

- Android `Intent.putExtra` → 鸿蒙 `router.pushNamedRoute({ name, params })` 

- Android `Fragment` + XML 布局 → 鸿蒙 `@Component struct` (ArkTS 声明式 UI) 

- Android `BJYPlayerSDK.Builder` 全局静态字段 → 鸿蒙 `BJYPlayerSDK` (静态字段)+ `BJYPlayerSDKBuilder` 

### 2. 快速集成 

#### 2.1. 包依赖 

`oh-package.json5` 引入: 

```
1{
2  "dependencies": {
3    "@baijia/videoplayerui": "^1.0.0"
4}
```

2 

#### 2.2. 公开导出( **`VideoPlayerUi/Index.ets`** ) 

|类别|导出符号|行号|
|---|---|---|
|Page|`VideoPlayPage`/ `Video` `PlayTriplePage`/ `PBRoo` `mPage`|1-3|
|入口工具类|`PBRoomUI`、 `OnEnterPBR`|4|
||`oomFailedListener`、 `Vi` `deoInfoModel`||
|配置|`VideoPlayerConfig`、 `S` `ignModel`、 `VisitorMode` `l`、 `DragControllerMode` `l`、 `HorseLampConfig`|5|
|全局SDK|`BJYPlayerSDK`、 `BJYPla` `yerSDKBuilder`|6|
|Core再导出|`VideoPlayerFactory`、|9-16|
||`IBJYVideoPlayer`、 `Play`||
||`erStatus`、 `PBRoom`、 `Do` `wnloadManager` 等||

#### 2.3. 初始化 SDK 

参考 Core SDK 的 `BJYPlayerConfig` ,或使用 UI 层提供的 `BJYPlayerSDKBuilder` 链式 API (对齐 Android `BJYPlayerSDK.Builder` ): 

|`1` `2`|`import {BJYPlayerSDKBuilder }from '@baijia/videoplayerui';`|
|---|---|
|`3`|`new BJYPlayerSDKBuilder()`|
|`4`|`.setDevelopMode(true)//`开发者模式(正式发版请关闭)|
|`5`|`.setEncrypt(true)//`加密|
|`6`|`.setCustomDomain('demo123')//`专属域名前缀|
|`7`|`.enablePlaybackUserSignalSetting()//`解析回放`user`信令|
|`8`|`.build();//`构建并同步到`BJYPlayerConfig / PlayerData` `Loader`|

`BJYPlayerSDKBuilder` API( `common/constant/BJYPlayerSDK.ets` ): 

3 

|方法|说明|行号|
|---|---|---|
|`setDevelopMode(isDevel` `opMode: boolean): BJYPl` `ayerSDKBuilder`|设置开发者模式|145|
|`setCustomDomain(domai` `n: string): BJYPlayerSD` `KBuilder`|设置专属域名|155|
|`setEncrypt(isEncrypt:`|设置加密|164|
|`boolean): BJYPlayerSDK` `Builder`|||
|`enablePlaybackUserSign` `alSetting(): BJYPlayerS` `DKBuilder`|开启回放user信令|173|
|`build(): void`|完成构建,同步配置到 `BJYPl` `ayerConfig` 与 `PlayerDa` `taLoader`|189|

`build()` 中已跳过 Android 端的 X5、MMKV、Glide、RxJavaPlugins 等无对应能力项。 

#### 2.4. BJYPlayerSDK 全局静态配置 

除 Builder 外, `BJYPlayerSDK` 提供大量公开静态字段供高级定制( `common/constant/BJYPla yerSDK.ets:13` ): 

|字段|类型|默认值|说明|行号|
|---|---|---|---|---|
|`CUSTOM_DOMAI` `N`|string|`''`|个性域名|15|
|`customEnviro`|string|`'at'`|私有化域名中缀|18|
|`nmentInfix`|||||
|`customEnviro`|string|`'baijiayun.c`|私有化域名后缀|21|
|`nmentSuffix`||`om'`|||
|`customAPIPre` `fix`|string|`'www'`|私有化API前缀|4 24|

|`IS_ENCRYPT`|boolean|`true`|加密开关(对在 线和下载均有 效)|27|
|---|---|---|---|---|
|`DEPLOY_TYPE`|number|`2`(PRODUCTIO N)|部署环境 (0/1/2)|31|
|`IS_DEVELOP_M` `ODE`|boolean|`false`|开发模式|34|
|`enablePlayba` `ckUserSignal`|boolean|`false`|解析回放user信 令|37|
|`STATIC_PPT_D` `EFAULT_SIZE`|number|`1080`|静态课件默认压 缩尺寸|40|
|`DISABLE_ANIM` `_PPT`|boolean|`false`|是否禁用动态 PPT|43|
|`MAX_SUPPORT_` `SHAPE_APPEND_` `COUNT`|number|`8000`|最大画笔轨迹还 原数|46|
|`supportPiP`|boolean|`true`|是否支持画中画|49|
|`isVideoList`|boolean|`false`|是否视频列表模 式(默认开启缓 存)|52|
|`enableSubtit` `leShadow`|boolean|`true`|字幕是否显示阴 影|55|
|`subtitleFore` `groundColor`|number|`-1`|字幕前景色(-1= 白色)|58|
|`playerVolume`|number|`1.0`|播放器音量 (0.0~1.0)|61|
|`enableScreen` `shot`|boolean | null|`null`|是否允许截屏 (null走配置 项)|64|

5 

|`enableScreen` `Recording`|boolean | null|`null`|是否允许录屏|67|
|---|---|---|---|---|
|`bjyUnknownEr`|string|`''`|自定义错误提示|70-75|
|`ror`/ `bjyVid` `eoUnknownErro` `r`/ `bjyVideo` `PlayError`/ `bjyVideoUrlEr` `ror`/ `bjyTok` `enInvalidErro` `r`/ `bjyDefau` `ltError`|||文案||
|`playerNumber`|string|`''`|播放器编号|78|
|`supportAD`|boolean|`false`|是否支持片头/片 尾|81|
|`customPlayba` `ckStr`/ `cust` `omPlaybackExt` `Data`|string|`''`|自定义上报内容|84/87|
|`enableCustom`|boolean|`false`|是否允许自定义|90|
|`PlaybackRepor` `t`|||上报||
|`hideChatLand` `scape`|boolean|`false`|横屏时是否隐藏 聊天|93|
|`filterDefini`|`VideoDefinit`|`[]`|指定可选清晰度|96|
|`tionList`|`ion[]`||过滤||
|`supportBackg` `roundAudio`|boolean|`true`|后台音频(鸿蒙 端补充字段)|99|
|`supportLoopi` `ng`|boolean|`false`|循环播放(鸿蒙 端补充字段)|102|

6 

启用记忆播放 

```
supportBreak
```

boolean 

105 

```
true
PointPlay
```

##### 工具方法: 

`1 BJYPlayerSDK.getWebHost(): string;   //` 拼接当前环境 `web host` , `line 111` 

### 3. 快速集成 

一 `PBRoomUI` ( `VideoPlayerUi/src/main/ets/PBRoomUI.ets` )是 UI SDK 的唯 入口工具 一 类,提供 系列静态方法。所有方法内部通过 `router.pushNamedRoute` 跳转到对应命名路由。 

#### 3.1. 调起点播播放页面 

##### 在线点播(路由 `VideoPlayPage` ,行号 217): 

- `import { PBRoomUI, VideoPlayerConfig } from '@baijia/videoplayerui';` 

- `PBRoomUI.startPlayVideo(videoId, token, playerConfig /*` 可传 `null */);` 

- `/**` 

- `*` 进入标准在线点播播放界面 `3 *` 对应 `Android startPlayVideo(context, videoId, token, playerConfig) 4 */ 5 static startPlayVideo(videoId: number, token: string, 6 playerConfig: VideoPlayerConfig | null): void` 

##### 点播专辑(行号 236): 

- `PBRoomUI.startPlayVideoAlbum(albumId, playerConfig);` 

##### 三分屏点播(路由 `VideoPlayTriplePage` ,行号 253): 

- `PBRoomUI.startPlayVideoTriple(videoId, token, playerConfig); 2 PBRoomUI.startPlayVideoTripleAlbum(albumId, playerConfig);   // line 272` 

##### 离线点播(行号 289): 

- `PBRoomUI.startPlayLocalVideo(downloadModel, playerConfig);` 

视频列表(行号 311,路由 `VideoListPage` ): 

7 

```
1PBRoomUI.startPlayVideoList(videoInfoModelList: VideoInfoModel[],
2playerConfig, position);
```

⚠ `VideoListPage` 路由已注册但页面实现未交付(鸿蒙端 `pages/` 目录下无 `VideoListPag e.ets` ,参考 `pages/` 仅有 `PBRoomPage.ets` 、 `VideoPlayPage.ets` 、 `VideoPlayTri plePage.ets` 三个)。 `startPlayVideoList` 当前调用会因找不到命名路由而失败。 

#### 3.2. 调起回放播放页面 

##### 所有回放接口都跳到路由 `PBRoomPage` 。 

标准回放(无配置,sessionId 非长期课传 `'-1'` ,行号 48): 

- `import { PBRoomUI, OnEnterPBRoomFailedListener } from '@baijia/videoplayeru i';` 

- `class MyFailListener implements OnEnterPBRoomFailedListener { 4 onEnterPBRoomFailed(msg: string): void { /* ... */ } 5 }` 

- `PBRoomUI.enterPBRoom(roomId, roomToken, sessionId, new MyFailListener());` 

##### 标准回放 with config(行号 58): 

- `PBRoomUI.enterPBRoomWithConfig(roomId, roomToken, sessionId, 2 playerConfig, failListener);` 

##### 裁剪回放(行号 69): 

- `PBRoomUI.enterPBRoomWithVersion(roomId, roomToken, sessionId, 2 version /* 0=` 原视频, `-1=` 主版本 `*/, 3 playerConfig, failListener);` 

##### 合并回放(行号 106 / 116): 

- `PBRoomUI.enterMixedPBRoom(mixedId, mixedToken, failListener);` 

- `PBRoomUI.enterMixedPBRoomWithConfig(mixedId, mixedToken, playerConfig, fail Listener);` 

##### 回放合集(行号 148): 

- `PBRoomUI.enterAlbumPBRoom(albumNo, playerConfig, failListener);` 

离线回放(行号 171 / 179): 

8 

- `PBRoomUI.enterLocalPBRoom(videoModel, signalModel);` 

- `PBRoomUI.enterLocalPBRoomWithConfig(videoModel, signalModel, playerConfig);` 

`videoModel` / `signalModel` 来自 Core SDK 的 `DownloadManager.newPlaybackDownl` 一 `oadTask` ,鸿蒙 UI 入口统 使用 `@baijia/videoplayer` 中的 `DownloadModel` (参见 `PB RoomUI.ets:13` )。 

##### `OnEnterPBRoomFailedListener` 接口(行号 19): 

- `export interface OnEnterPBRoomFailedListener { 2 onEnterPBRoomFailed(msg: string): void; 3 }` 

##### `VideoInfoModel` 视频列表项(行号 27): 

- `export class VideoInfoModel {` 

- `videoId: number = 0;` 

- `''` 

- `token: string = ; ''` 

- `title: string = ; 5 }` 

#### 3.3. Page 路由注册 

|Page|路由名|文件|对应Android|
|---|---|---|---|
|`VideoPlayPage`|`'VideoPlayPage'`|`pages/VideoPlayP`|`VideoPlayActivi`|
|||`age.ets:142`|`ty`|
|`VideoPlayTripleP`|`'VideoPlayTriple`|`pages/VideoPlayT`|`VideoPlayTriple`|
|`age`|`Page'`|`riplePage.ets:91`|`Activity`|
|`PBRoomPage`|`'PBRoomPage'`|`pages/PBRoomPag`|`PBRoomActivity`|
|||`e.ets:250`||
|`VideoListPage`|`'VideoListPage'`|未实现|`VideoListActivi` `ty`|

`PBRoomUI.buildPBRoomParams()` (行号 334)将 `VideoPlayerConfig` 扁平化为 router params,主要透传字 

段: `userName` 、 `userId` 、 `videoTitle` 、 `enableDragController` 、 `supportBackgro undAudio` 、 `userGroup` 、 `defaultAlbumIndex` 、 `isLandscape` 、 `isVideoMain` 、 `vis` 

9 

`itorSeconds/positiveText/negativeText/content` 、 `dragControllerContent/posit iveText` 、 `horseLampContent/fontSize/fontColor/fontAlpha` 。 

#### 3.4. VideoPlayerConfig 

##### 定义在 `VideoPlayerUi/src/main/ets/bean/VideoPlayerConfig.ets:98` 。 

- `import { VideoPlayerConfig, HorseLampConfig, SignModel,` 

- `VisitorModel, DragControllerModel } from '@baijia/videoplayerui';` 

- `3` 

- `const cfg = new VideoPlayerConfig('userName', 'userId')` 

- `.setHorseLamp(new HorseLampConfig())` 

- `.setSignModelList([new SignModel()])` 

- `.setVisitorModel(new VisitorModel())` 

- `.setEnableDragController(true)` 

- `.setDragControllerModel(new DragControllerModel())` 

- `.setUserGroup(1);` 

##### 全部字段: 

|字段|类型|默认值|说明|行号|
|---|---|---|---|---|
|`supportBackg` `roundAudio`|boolean|`false`|后台音频播放|100|
|`supportLoopi` `ng`|boolean|`false`|循环播放|102|
|`supportBreak` `PointPlay`|boolean|`true`|记忆播放|104|
|`userName`|string|`''`|用户名(上报)|106|
|`userId`|string|`''`|用户ID(上报)|108|
|`userGroup`|number|`-1`|用户分组|110|
|`horseLamp`|`HorseLampCon` `fig | null`|`null`|跑马灯|112|
|`notification`|`Notification` `Config`|`new Notifica` `tionConfig` `('','','')`|后台播放通知配 置|114|
|`supportSeek`|boolean|`true`|支持进度条拖动|10 116|

|`maxWatchTime`|number|`2147483647`|最大可观看时长 (秒)|118|
|---|---|---|---|---|
|`supportVideo` `Rate`|boolean|`true`|支持倍速|120|
|`isVideoMain`|boolean|`true`|视频为主(false 表示PPT为主)|122|
|`isLandscape`|boolean|`false`|默认横屏|124|
|`enableToggle` `Screen`|boolean|`true`|允许横竖屏切换|126|
|`loginToken`|string|`''`|点播评论token|128|
|`avatar`|string|`''`|用户头像URL|130|
|`signModelLis` `t`|`SignModel[]`|`[]`|签到列表|132|
|`defaultAlbum` `Index`|number|`0`|合集默认索引|134|
|`visitorModel`|`VisitorModel` `| null`|`null`|试看|136|
|`enableDragCo` `ntroller`|boolean|`true`|允许拖拽|138|
|`dragControll` `erModel`|`DragControll` `erModel | nul` `l`|`null`|禁拖弹窗文案|140|
|`videoTitle`|string|`''`|自定义视频标题 (鸿蒙端字段)|142|

##### 构造函数(行号 147): 

```
''''
1constructor(userName: string=, userId: string=);
```

Builder 链式 setter(均返回 `VideoPlayerConfig` ): 

方法 

行号 

11 

|`setHorseLamp(horseLamp: HorseLampCo` `nfig)`|152|
|---|---|
|`setSignModelList(signModelList: Sig` `nModel[])`|157|
|`setVisitorModel(visitorModel: Visit` `orModel)`|162|
|`setEnableDragController(enable: boo` `lean)`|167|
|`setDragControllerModel(dragControll`|172|
|`erModel: DragControllerModel)`||
|`setUserGroup(userGroup: number)`|177|

Android 端 `VideoPlayerConfig.albumItemDataList` 在鸿蒙端未在 

`VideoPlayerConfig` 类内提供,回放合集请用 `PBRoomUI.enterAlbumPBRoom(albumNo, ...)` 直接传 `albumNo` 字符串。 

#### 3.5. 回放合集 

使用专辑号入口(详见 §3.2 `enterAlbumPBRoom` ),由 Core SDK 内部从服务端拉取专辑详情。 

#### 3.6. 点播签到 

通过 `VideoPlayerConfig.setSignModelList()` 配置签到打点;通过 `CallbackManager.s etSignListener()` 监听签到事件。 

`SignModel` 字段( `bean/VideoPlayerConfig.ets:19` ): 

|字段|类型|默认值|说明|行号|
|---|---|---|---|---|
|`seconds`|number|`0`|触发时间点 (秒)|21|
|`logo`|string|`''`|弹窗logo URL|23|
|`title`|string|`''`|标题|25|
|`content`|string|`''`|正文|12 27|

按钮文案 

```
''
btnText
```

29 

string 

##### 监听签到按钮点击: 

- `import { CallbackManager, SignConsumer } from '@baijia/videoplayerui';` 

- `import { SignModel } from '@baijia/videoplayerui';` 

- `3` 

- `class MySignConsumer implements SignConsumer {` 

- `accept(model: SignModel): void { /* ... */ } 6 }` 

- `CallbackManager.getInstance().setSignListener(new MySignConsumer());` 

#### 3.7. 点播分享 

##### 注册分享回调后,UI 上会显示分享按钮(默认不显示)。 

- `import { CallbackManager, ShareListener } from '@baijia/videoplayerui';` 

- `2` 

- `class MyShareListener implements ShareListener {` 

- `onShareClicked(videoId: string): void { /* ... */ } 5 }` 

- `CallbackManager.getInstance().setShareListener(new MyShareListener());` 

##### 接口签名( `common/CallbackManager.ets:35` ): 

- `export interface ShareListener {` 

- `onShareClicked(videoId: string): void; 3 }` 

#### 3.8. 点播/回放试看 

`VideoPlayerConfig.visitorModel` 设置试看, `VisitorModel` ( `bean/VideoPlayerCon fig.ets:36` )字段: 

|字段|类型|默认值|说明|行号|
|---|---|---|---|---|
|`seconds`|number|`2147483647`|试看时长(秒)|38|
|`positiveText`|string|`''`|确认按钮文案|40|

13 

|`negativeText`|string|`''`|取消按钮文案|42|
|---|---|---|---|---|
|`navigateText`|string|`''`|跳转按钮文案|44|
|`content`|string|`''`|弹窗正文|46|
|`navigateLink`|string|`''`|跳转链接|48|

##### 监听试看弹窗按钮: 

- `import { CallbackManager, VisitorListener } from '@baijia/videoplayerui'; 2 import { IBJYVideoPlayer } from '@baijia/videoplayer';` 

- `3` 

- `class MyVisitorListener implements VisitorListener {` 

- `onPositiveClick(dialogId: string, player: IBJYVideoPlayer): void { } 6 onNavigateClick(dialogId: string, player: IBJYVideoPlayer): void { } 7 } 8 CallbackManager.getInstance().setVisitorListener(new MyVisitorListener());` 

Android 端 `onPositiveClick(DialogFragment, IBJYVideoPlayer)` 在鸿蒙端用 `dialog Id: string` ( `CustomDialog` 控制器 ID)替代 `DialogFragment` 。 

#### 3.9. 点播/回放禁止拖拽 

- `const cfg = new VideoPlayerConfig()` 

- `.setEnableDragController(false)   //` 禁止拖拽 `3 .setDragControllerModel(new DragControllerModel());` 

##### `DragControllerModel` ( `bean/VideoPlayerConfig.ets:55` ): 

|字段|类型|默认值|说明|行号|
|---|---|---|---|---|
|`positiveText`|string|`''`|按钮文案|57|
|`content`|string|`''`|弹窗正文|59|

##### 监听用户拖拽尝试: 

14 

- `import { CallbackManager, DragConsumer } from '@baijia/videoplayerui';` 

- `import { DragControllerModel } from '@baijia/videoplayerui';` 

- `3` 

- `class MyDragConsumer implements DragConsumer {` 

- `accept(model: DragControllerModel): void { /*` 自行弹窗 `*/ } 6 }` 

- `CallbackManager.getInstance().setDragListener(new MyDragConsumer());` 

#### 3.10. HorseLampConfig / NotificationConfig 

##### `HorseLampConfig` ( `bean/VideoPlayerConfig.ets:85` )跑马灯: 

|字段|类型|默认值|行号|
|---|---|---|---|
|`content`|string|`''`|86|
|`fontSize`|number|`14`|87|
|`fontColor`|string|`'#FFFFFF'`|88|
|`fontAlpha`|number|`1.0`|89|
|`speed`|number|`50`|90|
|`displayStyle`|number|`0`|91|

`NotificationConfig` ( `bean/VideoPlayerConfig.ets:66` )后台播放通知(鸿蒙系统对后 

##### 台媒体通知能力有限制): 

|字段|类型|默认值|行号|
|---|---|---|---|
|`smallIcon`|string|`''`|68|
|`largeIcon`|string|`''`|70|
|`contentString`|string|`''`|72|

构造函数(行号 74): `new NotificationConfig(smallIcon, largeIcon, contentStrin g)` 。 

### 4. 功能介绍 

15 

#### 4.1. 包结构 

|`1`|`VideoPlayerUi/src/main/ets/` |
|---|---|
|`2`|`├── Index.ets                          #`公开导出 |
|`3`|`├── PBRoomUI.ets                       # UI`入口工具类 |
|`4`|`├── bean/` |
|`5`|`│   └── VideoPlayerConfig.ets          #`配置模型(`VideoPlayerConfig / Sign`|
||`Model / VisitorModel / DragControllerModel / HorseLampConfig / Notificatio` `nConfig`) |
|`6`|`├── common/` |
|`7`|`│   ├── CallbackManager.ets            #`全局回调注册 |
|`8`|`│   ├── LPError.ets` |
|`9`|`│   └── constant/`|
|`10`|`│       └── BJYPlayerSDK.ets           #`全局静态配置`+ Builder` |
|`11`|`├── pages/                             #`路由页面(`@Entry`装饰) |
|`12`|`│   ├── VideoPlayPage.ets` |
|`13`|`│   ├── VideoPlayTriplePage.ets` |
|`14`|`│   └── PBRoomPage.ets` |
|`15`|`├── component/                         #`通用`UI`组件 |
|`16`|`│   ├── LoadingComponent.ets` |
|`17`|`│   ├── GestureComponent.ets` |
|`18`|`│   ├── ControllerComponent.ets` |
|`19`|`│   ├── ErrorComponent.ets` |
|`20`|`│   ├── MenuComponent.ets` |
|`21`|`│   ├── LampComponent.ets              #`跑马灯 |
|`22`|`│   ├── CommentComponent.ets` |
|`23`|`│   ├── MediaPlayerDebugComponent.ets` |
|`24`|`│   ├── playback/                      #`回放专用:`PBChatComponent / Announ`|
||
`cementComponent / PBToolboxComponents / PPTTripleComponent`等
|
|`25`|`│   ├── toolbox/                       #`答题、问答、测验 |
|`26`|`│   ├── subtitle/                      #`字幕组件|
|`27`|`│   ├── roomoutline/                   #`大纲|
|`28`|`│   ├── studyreport/`|
|`29`|`│   └── keyframe/` |
|`30`|`└── widget/                            #`弹窗、合集等小部件(如`VideoAlbumDia`|
||`log`)|

#### 4.2. 自定义点播 UI 

鸿蒙端使用 ArkTS 声明式 UI,在 `VideoPlayPage` / `VideoPlayTriplePage` / 

`PBRoomPage` 中通过 `@Component struct` 组合各个组件。未提供 Android 端 `ComponentMan ager` / `ComponentContainer` / `BaseVideoView` / `BJYVideoView` 等运行时容器化注册体 系;如需定制 UI,请 fork 对应 Page 自行修改。 

16 

#### 4.3. UI 组件清单 

##### 通用组件( `component/` ): 

|组件|文件|说明|
|---|---|---|
|`LoadingComponent`|`LoadingComponent.ets`|加载转圈|
|`GestureComponent`|`GestureComponent.ets`|手势控制(音量、亮度、快进)|
|`ControllerComponent`|`ControllerComponent.et` `s`|控制条(进度、播放、清晰度、 倍速)|
|`ErrorComponent`|`ErrorComponent.ets`|错误提示|
|`MenuComponent`|`MenuComponent.ets`|菜单项(清晰度、倍速选择)|
|`LampComponent`|`LampComponent.ets`|跑马灯|
|`CommentComponent`|`CommentComponent.ets`|点播评论|
|`MediaPlayerDebugCompon`|`MediaPlayerDebugCompon`|调试面板( `IS_DEVELOP_MOD`|
|`ent`|`ent.ets`|`E` 开启时显示)|

回放专用( `component/playback/` 、 `component/toolbox/` 、 `component/subtitle/` 、 `component/roomoutline/` ):聊天、公告、答题、问答、测验、字幕、大纲、三分屏 PPT、学习 报告、关键帧等。 

弹窗与小部件( `widget/` ):合集对话框 `VideoAlbumDialog` 等。 

### 5. 回调注入 - CallbackManager 

`CallbackManager` ( `common/CallbackManager.ets:91` )单例,对齐 Android `com.baiji ayun.videoplayer.ui.listener.CallbackManager` 。 

#### 5.1. 获取实例 

```
1constcb=CallbackManager.getInstance();   // line 106
```

#### 5.2. 注册 / 注销 API 

17 

|回调接口|注册方法|行号|
|---|---|---|
|`SignConsumer`|`setSignListener(consum` `er)`|114|
|`ShareListener`|`setShareListener(liste` `ner)`|124|
|`VisitorListener`|`setVisitorListener(lis`|136|
||`tener)`||
|`DragConsumer`|`setDragListener(consum` `er)`|144|
|`OuterPlayerListener`|`setOuterPlayerListener` `(listener)`|148|
|`ExternalAlbumListener`|`setExternalAlbumListen` `er(listener)`|156|
|`OnVideoListRefreshList`|`setOnVideoListRefreshL`|168|
|`ener`|`istener(listener)`||
|`OnVideoListCallback`|`setOnVideoListCallback` `(callback)`|176|
|全部清空|`clearListener()`|180|

每个 set 方法都有对应的 getter(命名 `getXxx()` )供 SDK 内部调用。 

#### 5.3. 接口签名 

18 

- `//` 签到( `line 28` ) 

- `export interface SignConsumer { accept(model: SignModel): void; }` 

- `3` 

- `//` 分享( `line 35` ) 

- `export interface ShareListener { onShareClicked(videoId: string): void; }` 

- `6` 

- `//` 试看( `line 44` ) 

- `export interface VisitorListener {` 

- `onPositiveClick(dialogId: string, player: IBJYVideoPlayer): void;` 

- `onNavigateClick(dialogId: string, player: IBJYVideoPlayer): void; 11 }` 

- `12` 

- `//` 拖拽( `line 52` ) 

- `export interface DragConsumer { accept(model: DragControllerModel): void; }` 

- `15` 

- `//` 播放器事件外发( `line 59` ) 

- `export interface OuterPlayerListener {` 

- `onPlayerStatusChanged(status: PlayerStatus): void;` 

- `onPlayTimeChanged(current: number, duration: number): void;` 

- `onPlayerError(error: LPError): void;` 

- `}` 

- `22` 

- `//` 外部合集按钮( `line 68` ) 

- `export interface ExternalAlbumListener {` 

- `onExternalAlbumClick(): void;` 

- `}` 

- `27` 

- `//` 视频列表刷新( `line 75` ) 

- `export interface OnVideoListRefreshListener {` 

- `onRefresh(): void;` 

- `onLoadMore(): void;` 

- `}` 

- `33` 

- `//` 视频列表数据( `line 83` ) 

- `export interface OnVideoListCallback {` 

- `onDataChange(videoInfoModelList: VideoInfoModel[]): void;` 

- `onLoadNoMoreData(): void;` 

- `}` 

### 6. 平台适配差异(鸿蒙 vs Android) 

鸿蒙 

概念 

Android 

19 

|页面承载|`Activity`+ `Intent`|`@Entry({ routeName })` Page + `router.pushNamed` `Route`|
|---|---|---|
|Fragment / Layout XML|`Fragment`+ XML|`@Component` `struct`(ArkTS声明式)|
|上下文参数|入口方法首参 `Context con` `text`|入口方法不需要context (router隐式承载)|
|`VideoPlayerConfig` 传递|`Intent.putExtra(Consta`|`router.pushNamedRoute`|
||`ntUtil.VIDEO_PLAYER_CON` `FIG, config)`|扁平params( `buildPBRoom` `Params`)|
|回调实现|匿名内部类/ lambda|必须用具名 `class impleme` `nts`(ArkTS严格模式)|
|试看弹窗参数|`DialogFragment`|`dialogId: string`( `Cu` `stomDialog` 控制器ID)|
|组件容器化|`ComponentManager`/ `Co`|未实现,UI在Page级直接组|
||`mponentContainer`/ `Bas` `eVideoView`/ `BJYVideoV`|合|
||`iew`||
|视频列表|`VideoListActivity`|未实现(仅入口方法预留)|

### 7. 已知限制 

1. `VideoListPage` 未实现: `PBRoomUI.startPlayVideoList` 已写入路由 `'VideoListP age'` ,但 `pages/` 目录无对应文件。 

2. ArkTS 严格模式:所有 listener 必须用具名 `class implements` ,不允许匿名对象字面量。 

3. `ComponentManager` 体系未提供:自定义 UI 组件需直接 fork Page 并改写 `@Component` , 无法在运行时插拔。 

4. 后台播放通知: `NotificationConfig` 字段保留但鸿蒙系统对后台音频通知限制较严,需结 合 `ContinuousTask` (持续任务)申请。 

5. 签名 / 证书: `videoplayeruiDebug.p7b` / `videoplayeruiRelease.p7b` / `.cer` / `.p12` 已包含在仓库根,正式发布需自行申请并替换。 

20 

### 8. 完整对外导出清单 

|符号|类别|来源文件|Index.ets行号|
|---|---|---|---|
|`VideoPlayPage`|Page|`pages/VideoPlayP` `age.ets`|1|
|`VideoPlayTripleP`|Page|`pages/VideoPlayT`|2|
|`age`||`riplePage.ets`||
|`PBRoomPage`|Page|`pages/PBRoomPag` `e.ets`|3|
|`PBRoomUI`|入口|`PBRoomUI.ets`|4|
|`OnEnterPBRoomFai` `ledListener`|接口|`PBRoomUI.ets`|4|
|`VideoInfoModel`|模型|`PBRoomUI.ets`|4|
|`VideoPlayerConfi` `g`|配置|`bean/VideoPlayer` `Config.ets`|5|
|`SignModel`/ `Vis`|配置子项|`bean/VideoPlayer`|5|
|`itorModel`/ `Drag`||`Config.ets`||
|`ControllerModel` / `HorseLampConfi` `g`||||
|`BJYPlayerSDK`/|全局配置|`common/constant/`|6|
|`BJYPlayerSDKBuil` `der`||`BJYPlayerSDK.ets`||
|Core再导出( `Video`|透传|`@baijia/videopla`|9-16|
|`PlayerFactory`/ `IBJYVideoPlayer` / `PlayerStatus`/ `PBRoom`/ `PBRoom`||`yer`||
|`Impl`/ `DownloadM`||||
|`anager`/ `Downloa`||||
|`dModel`/ `Downloa`||||
|`dTask` 等)||||

21 

`CallbackManager` 及其接口( `SignConsumer` / `ShareListener` / `VisitorListener` / `DragConsumer` / `OuterPlayerListener` 等)未在 `Index.ets` 顶层 re-export,需要 通过相对路径或从 `@baijia/videoplayerui` 内部模块路径引入(视项目打包时是否扁平化导出 一 而定,必要时可在 `Index.ets` 追加 行 `export *` )。 

22
