# **集成HarmonyOS NEXT播放器SDK** 

通过阅读本文档,您可以了解鸿蒙 HarmonyOS NEXT 播放器 SDK 的集成方法与 Demo 。该 SDK 的大部分 API 设计方式 与 Android 端播放器 SDK 类似。 

## **功能清单** 

#### 当前版本的主要功能如下: 

|**分类**|**功能**|**说明**|
|---|---|---|
||直播播放|支持常见的RTMP、HLS(M3U8)、FLV等直播场景的视频格式。|
||点播播放|支持常见的HLS(M3U8)、MP4等点播场景的视频格式。 支持MP3等点播场景的音频格式。|
|播放协议与格式|H.264编码协议|支持播放H.264编码协议的视频流。 支持软硬解切换、支持硬解失败降级至软解。|
||H.265编码协议|支持播放H.265编码协议的视频流。 支持软硬解切换、支持硬解失败降级至软解。|
||URL播放|支持在线视频、本地视频以URL的方式播放。|
||基础控制|支持开始、结束、暂停、seek、自动播放等播放控制功能。|
|播放控制|Seek|支持拖动到指定位置(UI支持手势)。 支持已经缓冲的视频内容在拖动时不清除缓冲内容并快速拖动。|
||精确Seek|支持精确到帧级别拖动到指定位置。|
||自定义播放器尺寸|支持自定义设置播放器的宽高。|
|视频效果|显示模式|支持设置填充、旋转、镜像3类显示模式。|
||亮度调节|支持系统的亮度调节(UI支持手势)。|
||音量调节|支持调用系统接口调节观看视频的音量。|
|音频效果|静音|支持开启和关闭静音功能。|
|播放性能|播放失败重试|播放失败时自动重试。|
||自动重连|支持直播的自动重连功能。|
||日志上报|支持上报播放器SDK日志,统计音视频点播、直播相关播放埋点信息。|

质量服务 

支持对播放状态回调、首帧回调、播放完成或失败回调。 

事件回调 

## **Demo&最佳实践** 

### **获取Demo** 

|**项目**|**下载地址**|
|---|---|
|Demo|https://videocloudqa.oss-cn- shanghai.aliyuncs.com/apsaravideo_player_demo_harmonyosnext_20240904.zip|

#### **说明** 

- 编译本 Demo 时,需要基于自己的华为账号更新项目的签名后,方可运行。 

- 您可以在任何平台上编译和运行该 Demo ,包括 macOS x86 、 macOS M1 和 Windows 设备。有关具体的集成方法, 。 

- 请参阅 ./AliPlayerDemo/ReadMe.md 

- 该 Demo 仅供集成 SDK 时参考,我们计划在后续发布版本中提供更多的演示内容。如果在集成过程中遇到任何问题, 请随时与我们联系。 

### **HarmonyOS Next最佳实践集成参考** 

为了降低您在集成 HarmonyOS Next 播放器 SDK 时的学习和开发成本,我们建议您下载 Demo 并查阅工程目录下的 ReadMe.md 文件,按照相关指引来实现推荐的最佳实践方案。目前 Demo 已包含以下常见视频播放场景: 

- 最简接入方式。 

- 实现自定义 VideoComponent 组件,多场景复用。 

- 多实例播放方案。 

- 播放控制、全屏、手势调节等 UI 实践。 

- 短视频滑动场景列表播放方案。 

## **环境要求** 

|**类别**|**说明**|
|---|---|
|系统版本|鸿蒙HarmonyOS Next Next.0.0.26及其之后的稳定版本。|
|手机设备|推荐Huawei Mate 60系列手机,例如Huawei Mate 60 Pro(ALN-AL80)。|
|开发工具|IDE版本:5.0.3.402,不限Windows、Mac或Linux等设备系统。|

## **SDK集成** 

#### **说明** 

- 目前仅支持通过本地配置的方式集成鸿蒙 HarmonyOS NEXT 版播放器 SDK ,目前以 har 包的形式对外发布。未来将逐 步完善更新,提供功能更全面、性能更稳定的 SDK 版本。 

SDK License 通过与应用标识一一绑定,以实现对该应用调用 SDK 进行授权。您需要先提交宜搭表单申请授权。 

### **获取SDK** 

SDK 下载,请参见 HarmonyOS 播放器 SDK 。 

#### **重要** 

目前 HarmonyOS NEXT 版播放器 SDK 已支持在 mac m1 、 m2 设备上运行模拟器,不支持在 x86 设备上运行模拟器。 

## **配置SDK** 

#### har 包位置如下: 

#### image.png 

在 oh-package.json5 中配置依赖: 

"dependencies": { 

"premierlibrary": "file:../amdemos-player-ohos-listapp/libs/premierlibrary.har", 

} 

## **配置License** 

#### **说明** 

- 必须配置 License ,才能正常使用播放器 SDK 。 

- 播放器 SDK 目前免费提供, License 有效期为 1 年,到期后请重新申请 License 。 

- License 配置完成后,查看日志若无 License 相关报错,则表示 License 配置成功。 

- 配置的 License 文件和 LicenseKey 和申请 License 时的应用信息( PackageName 和 bundleName )有严格的对应关 系,请确保 License 文件和 LicenseKey 和申请 License 时的信息保持一致,否则会出现鉴权失败的情况。 

#### 1. 申请 License 授权。 

2. 申请授权成功后,将获取到的 License 证书文件拷⻉到 DevEco Studio 项目中,建议放到 rawfile 目录下。 

3. 在 module.json5 文件中添加如下字段。 

key 为 com.aliyun.alivc_license.licensekey (全小写), value 为 LicenseKey 的值。 

( ) 为步 中 书文件的放 路径 请根据实 情 

为 

key 为 com.aliyun.alivc_license.licensefile (全小写), value 为步骤 2 中证书文件的放置路径,请根据实际情 况填写。 

"metadata": [ { "name": "com.aliyun.alivc_license.licensekey", "value": "********" }, { "name": "com.aliyun.alivc_license.licensefile", "value": "license.crt" }, ] 

## **基础功能** 

#### 1. 创建播放器。 

// 推荐下载 Demo 工程,参阅 ReadMe.md 了解最佳实践方式,帮助您快速集成。 

// 从 SDK har 包中 import 播放器相关定义 import { AliPlayerFactory, AliPlayer } from 'premierlibrary'; 

##### // 创建播放器实例 

const player: AliPlayer = AliPlayerFactory.createAliPlayer(getContext(), traceId); 

##### // 创建列表播放器(滑动播放场景) 

const listPlayer: AliListPlayer = AliPlayerFactory.createAliListPlayer(getContext(), traceId); 

// getContext() 为鸿蒙系统函数; traceId 由业务指定独特的会话 ID ,可以为空字符串 '' 或 null 

#### 2. 设置播放器回调监听。 

// 推荐下载 Demo 工程,参阅 ReadMe.md 了解最佳实践方式,帮助您快速集成。 

// 按需 引入播放器事件回调类型定义 import { OnPreparedListener, OnCompletionListener, OnAudioInterruptEventListener,OnErrorListener,OnInfoListener,OnLoadingStatusListener, AudioStatus } from 'premierlibrary/src/main/ets/com/aliyun/player/IPlayer'; 

// 播放器实例 const player: AliPlayer = AliPlayerFactory.createAliPlayer(getContext(), traceId); 

// 定义回调监听 const mPreparedEventHandler: OnPreparedListener = { // prepare 完成 onPrepared: () => { console.log("prepared"); } }; const mCompletionEventHandler: OnCompletionListener = { // 播放完成 onCompletion: () => { console.log("play complete"); } } const mOnAudioInterruptListener: OnAudioInterruptEventListener = { // 音频打断 onAudioInterruptEvent: (audioStatus: AudioStatus) => { if (player) { console.log("[HOS DEMO] [AUDIO INTERRUPT]: " + audioStatus); let statusInfo: string = ""; switch (audioStatus) { case AudioStatus.AUDIO_STATUS_DEFAULT: statusInfo = "AUDIO_STATUS_DEFAULT" 

```arkts
break; case AudioStatus.AUDIO_STATUS_RESUME: statusInfo = "AUDIO_STATUS_RESUME" player.start(); // 继续播放 break; case AudioStatus.AUDIO_STATUS_PAUSE: statusInfo = "AUDIO_STATUS_PAUSE" player.pause(); // 暂停播放 break; case AudioStatus.AUDIO_STATUS_STOP: statusInfo = "AUDIO_STATUS_STOP" player.stop(); // 停止播放 break; case AudioStatus.AUDIO_STATUS_DUCK: statusInfo = "AUDIO_STATUS_DUCK" break; case AudioStatus.AUDIO_STATUS_UNDUCK: statusInfo = "AUDIO_STATUS_UNDUCK" break; default: break; } showToast("CALLBACK: onAudioInterrupt " + statusInfo); } } } const mOnErrorEventListener: OnErrorListener = { // 错误回调 onError:(errorInfo) => { let errorCode:PlayerErrorCode = errorInfo.getCode(); // 错误码 let errorMsg:string = errorInfo.getMsg(); // 错误描述 //errorExtra 为额外错误信息,形式为 json 字符串,示例如下,需要注意 ModuleCode 并不完全等同于 errorCode // { "Url": "xxx", 
```

// "Module": "NetWork", // "ModuleCode": "-377", //  "ModuleMessage": "Redirect to a url that is not a media"} let errorExtra:string = errorInfo.getExtra(); 

出错后需要停止掉播放器。 

```arkts
player.stop(); } } const mOnVideoInfo: OnInfoListener = { // 视频信息回调 // 播放器中的一些信息,包括:当前进度、缓存位置等等。 onInfo: (bean: InfoBean) => { 
```

- 当前进度: InfoCode.CurrentPosition 

当前缓存位置: InfoCode.BufferedPosition 

if (bean.getCode() === InfoCode.CurrentPosition) { 

this.videoProgress = bean.getExtraValue() / this.mVideoDuration * 100; 

```arkts
this.mDuration = CommonUtils.getDurationString(this.mVideoDuration, bean.getExtraValue()); } else if (bean.getCode() === InfoCode.BufferedPosition) { this.buffer = CommonUtils.secondToTime(Math.floor(bean.getExtraValue() / 1000)); this.bufferedProgress = bean.getExtraValue() / this.mVideoDuration * 100; } } } const mOnLoadingProgressEventListener: OnLoadingStatusListener = { // 加载、卡顿状态下回调 onLoadingBegin: () => { // 开始加载。画面和声音不足以播放。 // 一般在此处显示圆形加载 }, onLoadingProgress: (percent: number, netSpeed: number) => { // 加载进度。百分比和网速。 
```

} 

}, onLoadingEnd: () => { 

// 结束加载。画面和声音可以播放。 

// 一般在此处隐藏圆形加载。 

} } 

##### // 将监听注册到播放器实例中 

player.setOnPreparedListener(mPreparedEventHandler); player.setOnCompletionListener(mCompletionEventHandler); player.setOnAudioInterruptEventListener(mOnAudioInterruptListener); player.setOnErrorListener(mOnErrorEventListener); player.setOnInfoListener(mOnVideoInfo); player.setOnLoadingStatusListener(mOnLoadingProgressEventListener); 

#### 3. 设置播放方式。 

鸿蒙 HarmonyOS NEXT 版播放器 SDK 支持 4 种点播播放方式,包括: UrlSource 播放、 VidAuth 播放(视频点播用户推 荐使用)、 VidSts 播放、加密播放。 

鸿蒙 HarmonyOS NEXT 版播放器 SDK 仅支持 1 种直播播放方式, UrlSource 播放。 

#### **说明** 

UrlSource 是直接通过 URL 播放, VidSts , VidAuth 是通过 Vid 进行播放。 

。 接入地域 Region 的设置,请参见点播地域标识 

#### **点播视频播放** 

## **点播UrlSource播放** 

#### 使用点播 UrlSource 播放方式播放点播视频,需要将播放器的 setUrl 属性设置为播放地址。 

- 阿里云视频点播服务中的播放地址:可以调用 **GetPlayInfo** 接口获取。建议您集成点播服务端 SDK 来获取音视频播放地 。 

- 址,免去自签名的麻烦。调用接口获取音视频播放地址的示例请参见开发者门户开发者门户 

- 本地视频地址:请确保有访问权限,可以通过系统 API 获取到可访问的本地视频文件完整路径,例 

- 。 

- 如: /sdcard/xxx/xxx/xxx.mp4 或 content://xxx/xxx/xx.mp4 

import { AliPlayerFactory, AliPlayer } from 'premierlibrary'; 

import { UrlSource } from 'premierlibrary/src/main/ets/com/aliyun/player/source/UrlSource'; @Preview 

@Component 

export struct MyPlayerComponent { 

private videoUrl: string = 'http 播放地址 '; 

private aliPlayer: AliPlayer = AliPlayerFactory.createAliPlayer(getContext(), ''); 

- playByUrl() { 

let urlSource: UrlSource = new UrlSource(); 

- urlSource.setUri(this.videoUrl);// 必选参数,播放地址,可以是第三方点播地址,或阿里云视频点播服务中的播放地 址,也可以是本地视频地址。 

this.aliPlayer.setUrlDataSource(urlSource); 

- } } 

## **点播VidAuth播放(推荐)** 

- 使用 VidAuth 播放方式播放点播视频,需要将播放器的 vid 属性设置为音视频 ID ,将 playauth 属性设置为音视频播放凭证。 

   - 音视频 ID :可以在音视频上传完成后通过控制台(路径: **媒资库** > **音/视频** 。)或服务端接口 ( SearchMediaSearchMedia )获取。 

   - 音视频播放凭证:可以调用 **GetVideoPlayAuth** 接口获取。建议您集成点播服务端 SDK 来获取音视频播放凭证,免去 。 

   - 自签名的麻烦。调用接口获取音视频播放凭证的示例请参见开发者门户开发者门户 

推荐视频点播用户采用此播放方式。相比 STS 播放方式, PlayAuth 播放方式在易用性和安全性上更有优势,对比详情请参 见凭证方式与 STS 方式对比。 

```arkts
import { AliPlayerFactory, AliPlayer, VidAuth } from 'premierlibrary'; interface IAuthInfo { videoId: string, playAuth: string } @Preview @Component export struct MyPlayerComponent { private authInfo: IAuthInfo = { videoId: ' 点播 vid', playAuth: 'playauth', }; private aliPlayer: AliPlayer = AliPlayerFactory.createAliPlayer(getContext(), ''); playByVidAndAuth() { const vidAuthSource: VidAuth = new VidAuth(); vidAuthSource.setVid(this.authInfo.videoId);// 必选参数,视频 ID ( VideoId )。 vidAuthSource.setPlayAuth(this.authInfo.playAuth);// 必选参数,播放凭证,需要调用点播服务的 GetVideoPlayAuth 接口生成。 this.aliPlayer.setVidAuthDataSource(vidAuthSource); } } 
```

## **点播VidSts播放** 

使用点播 VidSts 播放方式播放点播视频是指用 STS 临时凭证而非点播音视频播放凭证播放。 STS 安全令牌和 STS 临时 AK 对 ( AccessKeyId 和 AccessKeySecret )需要提前获取,获取方式请参见使用 STS 临时授权方案上传视频。 

```arkts
import { AliPlayerFactory, AliPlayer, VidSts } from 'premierlibrary'; interface ISTSInfo { videoId: string, accessKeyId: string, securityToken: string, accessKeySecret: string, region: string } @Preview @Component export struct MyPlayerComponent { private stsInfo: ISTSInfo = { videoId: ' 点播 vid', accessKeyId: 'STS-accessKeyId', securityToken: 'STS-token', accessKeySecret: 'STS-accessKeySecret', region: 'regionId' }; private aliPlayer: AliPlayer = AliPlayerFactory.createAliPlayer(getContext(), ''); playByVidAndSTS() { const vidStsSource: VidSts = new VidSts(); vidStsSource.setVid(this.stsInfo.videoId);// 必选参数,视频 ID ( VideoId )。 vidStsSource.setAccessKeyId(this.stsInfo.accessKeyId);// 必选参数, STS 临时 AK 对的访问密钥 ID ,需要调用 ST S 服务的 AssumeRole 接口生成。 vidStsSource.setAccessKeySecret(this.stsInfo.accessKeySecret);// 必选参数, STS 临时 AK 对的访问密钥,需 要调用 STS 服务的 AssumeRole 接口生成。 vidStsSource.setSecurityToken(this.stsInfo.securityToken);// 必选参数, STS 安全令牌,需要调用 STS 服务的 AssumeRole 接口生成。 vidStsSource.setRegion(this.stsInfo.region);// 必选参数,点播服务的接入地域,默认为 cn-shanghai 。 this.aliPlayer.setVidStsDataSource(vidStsSource); } } 
```

## **点播加密播放** 

点播视频支持 HLS 标准加密、阿里云私有加密。加密播放请参见如何播放加密视频。 

**直播视频播放** 

## **直播UrlSource播放** 

使用 UrlSource 播放方式播放直播视频,需要将播放器的 setUrl 属性设置为直播拉流地址。播放地址可以是第三方直播地址 或阿里云直播服务中的拉流地址。 

。 阿里云直播拉流地址可以通过直播控制台的地址生成器生成。详情请参见直播地址生成器 

```arkts
import { AliPlayerFactory, AliPlayer } from 'premierlibrary'; import { UrlSource } from 'premierlibrary/src/main/ets/com/aliyun/player/source/UrlSource'; @Preview @Component export struct MyPlayerComponent { private videoUrl: string = ' 直播播放地址 '; private aliPlayer: AliPlayer = AliPlayerFactory.createAliPlayer(getContext(), ''); playByUrl() { 
let urlSource: UrlSource = new UrlSource(); urlSource.setUri(this.videoUrl);// 播放地址,可以是第三方直播地址,或阿里云直播服务中的拉流地址。 this.aliPlayer.setUrlDataSource(urlSource); } } 
```

4. 绑定播放器与鸿蒙 XComponent 组件,实现视频画面渲染。 

// 推荐下载并查看 Demo 最佳实践中,原子接入方案 // 以下代码为鸿蒙 arkTs 环境 @Component 组件示例 

/** * 原子接入 鸿蒙播放器 SDK * 基于最底层鸿蒙 XC 能力,最简单方式集成,为客户自制开发提供高自由度 * 三步 - 实现视频播放 */ 

import { AliPlayerFactory, AliPlayer } from 'premierlibrary'; import { UrlSource } from 'premierlibrary/src/main/ets/com/aliyun/player/source/UrlSource'; 

```arkts
@Preview @Component export struct MyPlayerComponent { private videoUrl: string = 'http 播放地址 '; private xComponentController = new XComponentController(); private aliPlayer: AliPlayer = AliPlayerFactory.createAliPlayer(getContext(), ''); 
build() { XComponent({ id: '0', // unique XC id type: XComponentType.SURFACE, libraryname: 'premierlibrary', controller: this.xComponentController }) .onLoad(async () => { // 准备 URL 对象 let urlSource: UrlSource = new UrlSource(); urlSource.setUri(this.videoUrl); // 绑定 URL & XC_SurfaceId this.aliPlayer.setUrlDataSource(urlSource); this.aliPlayer.setSurfaceId('0'); // surface ID 对应 XC ID 
```

// 播放视频 this.aliPlayer.setAutoPlay(true); this.aliPlayer.prepare(); }) .width('100%') .height(200) } aboutToDisappear(): void { if (this.aliPlayer) { this.aliPlayer.stop(); this.aliPlayer.release(); } } } 

#### **重要** 

XComponent 需要通过 libraryname: 'premierlibrary' 来加载播放器 SO ,同时需要指定唯一的 id 来区分不同的 XComponent ,以避免视频渲染出现冲突问题。 

#### 5. **可选:** 开启自动播放,默认为关闭状态。 

// player 为播放器实例 player.setAutoPlay(true); 

#### 6. 准备播放,调用 prepare() 开始读取并解析数据。若开启自动播放,数据解析完成后将开始自动播放视频。 

// player 为播放器实例 player.prepare(); 

#### 7. 开始播放。通过调用 start 方法主动开始播放视频。 

// player 为播放器实例 player.start(); 

## **API参考** 

对于普通播放器,以 IPlayer 提供的接口为准, IPlayer 文件可以从 har 包中读取到。 当前 IPlayer 代码如下: 

```arkts
import { ErrorInfo } from './bean/ErrorInfo'; import { InfoBean } from './bean/InfoBean'; import { PlayerConfig } from './nativeclass/PlayerConfig'; /** * 未知状态 */ /**** * Unknown status. */ export const unKnow: number = -1; /** * 空状态。刚创建出来的状态。 */ /**** * Blank. The player enters this state after it is created. */ export const idle: number = 0; /** * 初始化了的状态,设置播放源之后的状态 */ /**** * Initialized. The player enters this state after a media source is specified for the player. */ export const initalized: number = 1; /** * 准备成功的状态 */ /**** * Prepared. */ export const prepared: number = 2; /** * 正在播放的状态 */ /**** * The player is playing video or audio. */ export const started: number = 3; 
```

/** 

* 播放已暂停的状态 */ /**** * The player is paused. */ export const paused: number = 4; /** * 播放已停止的状态 */ /**** * The player is stopped. */ export const stopped: number = 5; 

/** * 播放完成状态 */ /**** * The player has completed playing the video or audio. */ export const completion: number = 6; 

/** * 出错状态 */ /**** * The player has an error. */ export const error: number = 7; 

export interface IPlayer { /** * 开始播放。 */ /**** * Start the player. */ start: () => void; /** * 暂停播放 */ /**** * Pause the player. */ pause: () => void; /** * 停止播放 */ /**** * Stop the player. */ stop: () => void; 

/** * 设置自动播放。如果是自动播放,则接受不到 {@link OnPreparedListener} 回调。 * * @param on true :是。默认否。 */ 

/**** * Enable autoplay. If autoplay is enabled, then the {@link OnPreparedListener} callback is not returned. * * @param on Value true indicates that autoplay is enabled. Default: disabled. */ setAutoPlay: (isAutoPlay: boolean) => void; /** * 准备。成功结果通过 {@link OnPreparedListener} 回调,或者失败 {@link OnErrorListener} */ /**** * Prepare the player. Call {@link OnPreparedListener} to return success messages. Call {@link OnErr orListener} to return error messages. */ prepare: () => void; /** * 设置 surfaceId ,将播放器的显示 surface 与 XComponent 绑定。不同的 XComponent 的 XComponentId 应不重复 * * @param surfaceId :实际上是 XComponentId 。 */ /**** * Set the surfaceId to bind the player's display surface with XComponent. The XComponent id ofSet the surfaceId to bind the player's display surface with XComponent. The XComponent id of different XComponents should not be duplicated. * * @param surfaceId : it's XComponentId actually 。 */ setSurfaceId: (surfaceId: string) => void; /** * 设置倍数播放。 * * @param speed 范围 [0.5,5] */ /**** * Set the playback speed. * * @param speed Valid values: [0.5,5]. */ setSpeed: (speed: number) => void; /** * 设置音量(非系统音量),范围 0.0~2.0 ,当音量大于 1.0 时,可能出现噪音,不推荐使用。 * * @param gain 范围 [0,1] */ /**** * Set the volume of the player(Not system volume). The range is 0.0~2.0 , it maybe lead to noise if set volume more then 1.0, not recommended. * * @param gain Valid values: [0,1]. */ setVolume: (volume: number) => void; /** * 获取音量。 * * @return 范围 [0, 1] */ /**** 

* Query the volume of the player. * * @return Valid values: [0, 1]. */ getVolume: () => number; //position is based on the unit of getDuration /** * 跳转到。不精准。 * * @param position 位置。单位毫秒。 */ /**** * Specify a position for inaccurate seeking. Unit: millisecond. * * @param position The specified position. */ seekTo: (position: number, mode: number) => void; /** * 获取总时长。 * * @return 总时长。单位 ms 。 */ /**** * Query the total length of the stream. * * @return The total length of the stream. Unit: milliseconds. */ getDuration: () => number; /** * 获取当前播放位置。 * * @return 播放位置。单位 ms 。 */ /**** * Query the current playback position. * * @return The current playback position. Unit: milliseconds. */ getCurrentPosition: () => number; /** * 获取缓冲进度位置。注意:与 {@link OnLoadingStatusListener} 的区别。 * * @return 缓冲进度位置。单位 ms 。 */ /**** * Query the current buffer progress. Note: Pay close attention to the difference between this metho d and {@link OnLoadingStatusListener}. * * @return The current buffer progress. Unit: milliseconds. */ getBufferedPosition: () => number; /** * 是否启用硬解码 * * @param enable true: 启用。 false: 关闭。 */ /**** 

* Enable or disable hardware decoding 

* Enable or disable hardware decoding. 

* * @param enable Set to true to enable hardware decoding and set to false to disable hardware decoding. */ enableHardwareDecoder: (enabled: boolean) => void; /** * 释放。 */ /**** * Release. */ release: () => void; /** * 设置静音 * * @param on true: 静音。默认 false 。 */ /**** * Mute the player. * * @param on Set to true to mute the player. Default: false. */ setMute: (mute: boolean) => void; /** * 是否静音 * * @return true: 静音。默认 false 。 */ /**** * Query whether the player is muted. * * @return Value true indicates that the player is muted. Default: false. */ isMuted: () => boolean; /** * 设置画面缩放模式 * * @param scaleMode 缩放模式。默认 {@link ScaleMode#SCALE_TO_FILL}. 见 {@link ScaleMode} 。 */ /**** * Set a zoom mode. * * @param scaleMode The specified zoom mode. Default: {@link ScaleMode#SCALE_TO_FILL}. See {@link ScaleMode}. */ setScaleMode: (mode: ScaleMode) => void; /** * 获取画面缩放模式 * * @return 缩放模式。默认 {@link ScaleMode#SCALE_TO_FILL}. */ /**** * Query the current zoom mode. * * @return The current zoom mode. Default: {@link ScaleMode#SCALE_TO_FILL}. */ 

getScaleMode: () => ScaleMode; 

g 

() 

; 

/** 

##### 设置循环播放。如果本地有了缓存,那么下次循环播放则播放本地文件。 

* @param on true :开启循环播放。默认关闭。 */ /**** * Enable loop playback. If the media file is already downloaded to the local host, then the downloa ded media file will be used for loop playback. * * @param on true : Enable loop playback. Default: disabled. */ setLoop: (on: boolean) => void; 

/** * 是否循环播放 * * @return true :开启了循环播放。默认关闭。 */ /**** * Query whether loop playback is enabled. * * @return Value true indicates that loop playback is enabled. Default: disabled. */ isLoop: () => boolean; /** * 获取视频宽度 * * @return 视频宽度 */ /**** * Query the width of the video. * * @return The width of the video. */ getVideoWidth: () => number; 

/** * 获取视频高度 * * @return 视频高度 */ /**** * Query the height of the video. * * @return The height of the video. */ getVideoHeight: () => number; 

/** * 获取视频旋转角度 * * @return 视频旋转角度 */ /**** * Query the rotate angle of the video. * * @return The rotate angle of the video. */ getVideoRotation: () => number; 

/** * 重新加载。比如网络超时时,可以重新加载。 */ /**** * Reload. Call this method when the network connection times out. */ reload: () => void; /** * 设置画面旋转模式 * * @param rotateMode 旋转模式。见 {@link RotateMode} */ /**** * Set a rotate mode. * * @param rotateMode The specified rotate mode. See {@link RotateMode}. */ setRotateMode: (mode: RotateMode) => void; /** * 获取画面旋转模式 * * @return 旋转模式。见 {@link RotateMode} */ /**** * Query the current rotate mode. * * @return The current rotate mode. See {@link RotateMode}. */ getRotateMode: () => RotateMode; /** * 设置镜像模式 * * @param mirrorMode 镜像模式。 见 {@link MirrorMode} 。 */ /**** * Set a mirroring mode * * @param mirrorMode The specified mirroring mode. See {@link MirrorMode}. */ setMirrorMode: (mode: MirrorMode) => void; 

/** * 获取当前镜像模式。 * * @return 镜像模式。 见 {@link MirrorMode} 。 */ /**** * Query the current mirroring mode. * * @return The current mirroring mode. See {@link MirrorMode}. */ getMirrorMode: () => MirrorMode; /** * 设置视频的背景色 * * @param color  ARGB * */ 

/**** 

/**** * Set video background color * @param color  ARGB */ setVideoBackgroundColor: (color: number) => void; 

/** * 获取倍数播放值。 * * @return 倍数播放值。范围 [0.5,5] */ /**** * Query the playback speed. * * @return The playback speed. Valid values: [0.5,2]. */ getSpeed: () => number; /** * 是否自动播放。 * * @return true :是。默认否。 */ /**** * Query whether autoplay is enabled. * * @return Value true indicates that autoplay is enabled. Default: disabled. */ isAutoPlay: () => boolean; /** * 设置播放器配置。 * * @param config 播放器配置。见 {@link PlayerConfig} */ /**** * Modify the player configuration. * * @param config The configuration of the player. See {@link PlayerConfig}. */ setConfig: (config:PlayerConfig) => void; /** * 获取播放器配置 * * @return 播放器配置 */ /**** * Query the player configuration. * * @return The player configuration. */ getConfig: () => PlayerConfig | undefined; getNativeContextAddr: () => number; /** * 设置准备成功通知。如果失败,则会通知 {@link OnErrorListener} 。 * * @param l 准备成功通知 */ /**** * Set a preparation success callback. If the preparation failed, the {@link OnErrorListener} is triggered 

triggered. * 

* @param l Preparation success notification. */ setOnPreparedListener: (l: OnPreparedListener) => void; 

/** * 设置渲染开始通知。可以监听首帧显示事件等,用于隐藏封面等功能。 * * @param l 渲染开始通知。 */ /**** * Set a rendering start callback. You can use this callback to listen to first frame display events and hide the album cover. * * @param l Rendering start notification. */ setOnRenderingStartListener: (l: OnRenderingStartListener) => void; 

/** * 设置播放器状态变化通知 * * @param l 播放器状态变化通知 */ /**** * Set a player status update callback. * * @param l Player status update notification. */ setOnStateChangedListener: (l: OnStateChangedListener) => void; 

/** 

* 设置播放完成通知 . 注意:循环播放不会发出此通知。 * * @param l 播放完成通知 . */ /**** * Set a playback completion callback. Note: No notification is sent if loop playback is enabled. * * @param l Playback completion notification. */ setOnCompletionListener: (l: OnCompletionListener) => void; 

/** * 设置加载状态通知。 * * @param l 加载状态通知 */ /**** * Set a loading status callback. * * @param l Loading status notification. */ setOnLoadingStatusListener: (l: OnLoadingStatusListener) => void; 

/** * 设置出错通知 * * @param l 出错通知 */ /**** * Set an error callback. * 

* @param l Error message. 

setOnErrorListener: (l: OnErrorListener) => void; 

设置信息监听 * @param l 信息监听 * Set a notification callback. * @param l The notification. setOnInfoListener: (l: OnInfoListener) => void; 

##### 设置视频宽高变化通知 

* @param l 视频宽高变化通知 * Set a video size change callback. * @param l Video size change notification. 

setOnVideoSizeChangedListener: (l: OnVideoSizeChangedListener) => void; 

设置拖动完成通知 

* @param l 拖动完成通知 * Set a seeking completion callback. * @param l Seeking completion notification. 

setOnSeekCompleteListener: (l: OnSeekCompleteListener) => void; 

##### 设置字幕显示通知 

* @param l 字幕显示通知 * Set a subtitle display callback. * @param l Subtitle display notification. setOnSubtitleDisplayListener: (l: OnSubtitleDisplayListener) => void; 

##### 设置视频渲染回调 

* @param l 视频渲染回调。见 {@linkplain OnVideoRenderedListener} */ /**** * set the video render callback * @param l video render callback. See {@linkplain OnVideoRenderedListener} */ setOnVideoRenderedListener: (l: OnVideoRenderedListener) => void; } 

/** * 准备成功通知 */ /**** * Preparation success callback. */ export interface OnPreparedListener { /** * 准备成功 */ /**** * Preparation is complete. */ onPrepared: () => void; } /** * 信息通知 */ /**** * Notification callback. */ export interface OnInfoListener { /** * 信息 * * @param infoBean 信息对象。见 {@linkplain InfoBean} */ /**** * Indicate a notification. * * @param infoBean The notification object. See {@linkplain InfoBean}. */ onInfo: (infoBean: InfoBean) => void; } /** * 渲染开始通知 */ /**** * Rendering start callback. */ export interface OnRenderingStartListener { /** * 渲染开始。 */ /**** * Rendering starts. */ onRenderingStart: () => void; } /** * 播放器状态变化通知 */ /**** * Player status update callback. */ export interface OnStateChangedListener { /** * 状态变化 

* 

* @param newState 新状态 */ /**** * The player status is updated. * * @param newState The updated status. */ onStateChanged: (newState: number) => void; } /** * 播放完成通知 . */ /**** * Playback completion callback. */ export interface OnCompletionListener { /** * 播放完成 */ /**** * The player has completed playing the video or audio. */ onCompletion: () => void; } /** * 加载状态通知 */ /**** * Loading status callback. */ export interface OnLoadingStatusListener { /** * 开始加载。 */ /**** * Start loading. */ onLoadingBegin: () => void; /** * 加载进度 * * @param percent 百分比, [0,100] * @param netSpeed 当前网速。 kbps */ /**** * Loading progress. * * @param percent  The loading progress in percentage. Valid values: [0,100]. * @param netSpeed The current bandwidth. Unit: kbit/s. */ onLoadingProgress: (percent: number, netSpeed: number) => void; /** * 加载结束 */ /**** * Loading is complete. */ onLoadingEnd: () => void; 

g 

() 

; 

} 

/** * 出错通知 */ /**** * Error callback. */ export interface OnErrorListener { /** * 出错 * * @param errorInfo 错误信息 */ /**** * An error occurs. * * @param errorInfo Error message. */ onError: (errorInfo: ErrorInfo) => void; } /** * 视频宽高变化通知 */ /**** * Video size change callback. */ export interface OnVideoSizeChangedListener { /** * 视频宽高变化 * * @param width 宽 * @param height 高 */ /**** * Video size changes. * * @param width  Width. * @param height Height. */ onVideoSizeChanged: (width: number, height: number) => void; } /** * 拖动完成通知 */ /**** * Seeking completion callback. */ export interface OnSeekCompleteListener { /** * 拖动完成 */ /**** * Seeking is complete. */ onSeekComplete: () => void; } 

/** * 字幕显示通知 

*/ /**** * Subtitle display callback. */ export interface OnSubtitleDisplayListener { 

/** * 外挂字幕被添加 * @param trackIndex 流 id * @param url 字幕 url */ /**** * External subtitles have been added * @param trackIndex stream id * @param url subtitle url */ onSubtitleExtAdded: (trackIndex: number, url: string) => void; /** * 显示字幕 * * @param tackIndex 流 id * @param id 索引 * @param data 内容 */ /**** * Show subtitles. * * @param id   Index. * @param data Content. */ onSubtitleShow: (trackIndex: number, id: number, data: string) => void; /** * 隐藏字幕 * @param trackIndex 流 id * @param id 字幕 id */ /**** * Hide subtitles. * * @param trackIndex track index * @param id subtitle Index. */ onSubtitleHide: (trackIndex: number, id: number) => void; /** * 字幕头信息 * @param trackIndex 流 id * @param header 头信息 */ /**** * Subtitle header. * * @param trackIndex track index * @param header subtitle header. */ onSubtitleHeader: (trackIndex: number, header: string) => void; } /** * 视频渲染回调 */ 

*/ /**** 

* video render callback */ export interface OnVideoRenderedListener { /** * 视频帧被渲染 * @param timeMs 渲染的时间点 * @param pts 渲染的 pts */ /**** * video frames are rendered * @param timeMs render point in time * @param pts rendered pts */ onVideoRendered: (timeMs: number, pts: number) => void; } 

export enum IPResolveType { /** * 任意类型 */ /**** * default */ IpResolveWhatEver, /** * 只使用 ipV4 */ /**** * only ip v4 */ IpResolveV4, /** * 只使用 ipV6 */ /*** * only ip v6 */ IpResolveV6 } export enum ScaleMode { /** * 宽高比适应 */ /**** * Auto zoom to fit. */ SCALE_ASPECT_FIT = 0, /** * 宽高比填充 */ /**** * Fill to fit. */ SCALE_ASPECT_FILL, /** * 拉伸填充 */ /**** * Stretch to fit. */ 

/ SCALE_TO_FILL } 

export enum MirrorMode { /** * 无镜像 */ /**** * Disable mirroring. */ MIRROR_MODE_NONE = 0, /** * 水平镜像 */ /**** * Horizontal mirroring. */ MIRROR_MODE_HORIZONTAL, /** * 垂直镜像 */ /**** * Vertical mirroring. */ MIRROR_MODE_VERTICAL, } export enum RotateMode { /** * 顺时针旋转 0 度 */ /**** * Do not rotate. */ ROTATE_0 = 0, /** * 顺时针旋转 90 度 */ /**** * Rotate 90 degree clockwise. */ ROTATE_90 = 90, /** * 顺时针旋转 180 度 */ /**** * Rotate 180 degree clockwise. */ ROTATE_180 = 180, /** * 顺时针旋转 270 度 */ /**** * Rotate 270 degree clockwise. */ ROTATE_270 = 270, } 

**已知问题** 

切换前后台可能会导致视频播放中断,您可以在 APP 上层设置长时任务来解决。 

## **相关文档** 

HarmonyOS 播放器 SDK 合规配置指引
