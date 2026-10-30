# 快手广告 **HarmonyOS-SDK** 接入文档 

## [TOC] **1.** 接入准备 

接入快手广告 SDK 前,请在快手广告平台申请您的 AppId,广告位 id 等 注:当前 **SSP** 平台创建鸿蒙应用为白名单机制,如有接入需求请联系对应商务 

## **2. SDK** 集成 

### 手动引入 **har** 包 

在 oh-package.json5 添加依赖 

{ "dependencies": { "ksadsdk": "file:./KSAdSDK-{version}.har" } } 

工程级 build-profile.json5 中设置 useNormalizedOHMUrl 为 true 

{ "app": { "products": [ { "buildOption": { "strictMode": { "useNormalizedOHMUrl": true } } } ] } } 

##### 注: **useNormalizedOHMUrl** 设置需要在 **Build Version: 5.0.3.500** 以上 

### 添加权限 

- 1.打开 app 模块的 module.json5 文件 

- 2.添加以下权限:访问网络、获取网络状态、获取广告追踪标识(oaid)、传感器(可选)、振 动(可选) 

{ "requestPermissions": [ { "name": "ohos.permission.INTERNET", //访问网络 "reason": "$string:request_network" }, { "name": "ohos.permission.GET_NETWORK_INFO", //获取网络状态 "reason": "$string:request_network_info" }, { "name": "ohos.permission.APP_TRACKING_CONSENT", //获取广告标识 "reason": "$string:request_track" }, { "name": "ohos.permission.ACCELEROMETER", // 传感器,用于实现扭动摇动 "reason": "$string:request_sensor" }, { "name": "ohos.permission.GYROSCOPE", // 传感器,用于实现扭动摇动 "reason": "$string:request_sensor" }, { "name": "ohos.permission.VIBRATE", // 振动,用于交互反馈 "reason": "$string:request_vibrate" } ] } 

## **3. SDK** 初始化 

请在应用入口(entryability)中调用以下代码来执行 SDK 初始化 

```arkts
import { KSAdSDK, KSAdSDKInitConfig } from 'ksadsdk'; const initConfig: KSAdSDKInitConfig = { appId: '90009', } // 初始化 SDK 
```

// windowStage 对象用于使用子 window 方式展示激励、全屏广告,传空则使用 router 方式跳 转 KSAdSDK.init( initConfig, applicationContext, //windowStage ); // 启动 SDK KSAdSDK.start().then((success: boolean) => { Logger.d('ksad', "sdk init result:" + success); }); 

### **3.1** 初始化接口说明 

##### // 设置配置参数 

static init(initConfig: KSAdSDKInitConfig, context: common.ApplicationContext, windowStage?: window.WindowStage) { // 固定配置,防止外部修改影响内部逻辑 KSAdSDKImpl.instance().init(JSON.parse(JSON.stringify(initConfig)), context); } // 启动 SDK static start(): Promise<boolean> { return KSAdSDKImpl.instance().start(); } 

### **3.2** 初始化参数说明 

/** * SDK 初始化配置 */ export interface KSAdSDKInitConfig { // 媒体 appId appId: string; // 媒体 app 名称 appName?: string; // 媒体 app 标签 appTag?: string; 

// 是否允许程序化推荐,默认 true enableProgrammaticRecommend?: boolean; // 是否允许个性化推荐,默认 true enablePersonalRecommend?: boolean; } 

## **4.** 场景接入 

### **4.1** 激励视频广告 

激励视频是一种全屏播放的视频广告,用户可以在观看视频一定时长后获取奖励 接入示例参考 demo 中的 TestRewardVideoPage 

#### 加载广告 

import { KSAdSDK, KSAdScene, KSRewardAd, KSAdScreenDirection } from 'ksadsdk' 

```arkts
const scene = new KSAdScene() .setposId("your posId") .setScreenOrientation(KSAdScreenDirection.vertical) // 请求广告 KSAdSDK.getLoadManager().loadRewardAd(scene, { onAdLoad(ad: KSRewardAd) { ToastUtil.show("激励视频加载成功"); ad.setInteractListener({ onAdShow() { console.log("Reward ad show"); ToastUtil.show("激励视频曝光"); }, onVideoPlayStart() { ToastUtil.show("激励视频开始播放"); }, onVideoPlayEnd() { ToastUtil.show("激励视频播放结束"); }, onVideoPlayError(code: number, extra: string) { ToastUtil.show("激励视频播放失败:" + extra); }, onAdClick() { ToastUtil.show("激励视频点击"); }, 
```

onRewardVerify() { ToastUtil.show("激励视频获取奖励"); }, onAdClose() { ToastUtil.show("激励视频关闭"); } }) }, onError(code: number, msg: string) { ToastUtil.show("激励视频加载失败:" + msg); }, onRequestSuccess(adNum: number) { } }) 

#### 展示激励视频 

// 展示广告 ad.show({ videoSoundEnable: true }) 

#### 激励相关回调 

// 广告点击 onAdClick?: () => void; // 广告关闭 onAdClose?: () => void; // 广告曝光 onAdShow?: () => void; // 视频播放开始 onVideoPlayStart?: () => void; // 视频播放结束 onVideoPlayEnd?: () => void; // 视频播放失败 

onVideoPlayError?: (code: number, extra: string) => void; 

// 视频直接跳过 onVideoSkipToEnd?: (playDurationMs: number) => void; 

// 获取奖励 onRewardVerify?: () => void; 

#### 激励视频的服务端回调支持 

激励视频的有效性回调,支持开发者服务端回调,SDK 会在激励视频有效的时候,GET 请求回调 url(该 url 需要开发者在 SSP 平台中进行配置),这样开发者可以在自己的服务端对激励视频的有 效性进行再次验证。 

整体的调用流程如下: 

sequenceDiagram participant 联盟 SDK participant 联盟服务器 participant 开发者服务器 participant 开发者客户端 

联盟 SDK ->> 联盟服务器: 发起奖励回调请求 联盟服务器 ->> 联盟 SDK: 下发开发者配置的 callbackUrlInfo 联盟 SDK ->> 联盟服务器: 拼接参数请求 open/callback 联盟服务器 ->> 开发者服务器: 透传参数 开发者服务器 ->> 联盟服务器: 返回结果 联盟服务器 ->> 联盟 SDK: 返回结果 开发者服务器 -->> 开发者客户端: 告知客户端是否发放奖励 联盟 SDK ->> 开发者客户端: SDK 回调通知 

在 SSP 平台配置回调 url 的时候,需要按照以下格式进行配置: 

https://your_callback_url? userId=__UID__&transId=__TRANSID__&sign=__SIGN__&amount=__RAMOUNT__&na me=__RNAME__&extra=__EXTRA__ 

其中 “https://your_callback_url” 为客户的服务端回调 url 的地址,后面为各个参数的设置,客 户可以按照需要进行配置。例如: 

https://your_callback_url?userId=__UID__&transId=__TRANSID__ 

这样配置的话,则 SDK 在调用客户服务端 url 的时候,只会包含 `userId` 和 `transId` 这两个参 数,而不包含其他的。 

注意:回调 **url** 仅支持 **https** 协议。 

在 SSP 配置完成后,开发者使用该功能的时候,需要在请求激励视频的时候,通过 KSAdScene 对 象设置相关的参数,参数示例如下: 

const scene = new KSAdScene() .setPosId(POS_ID_REWARD) .setAdNum(1) .setScreenOrientation(KSAdScreenDirection.vertical) .setRewardExtraData({ thirdUserId: "thirdUserId", extraData: "extraData", }) 

联盟 SDK 在调用开发者指定的回调 url 的时候,会附加一些参数(形式为 GET 请求的参数,配置方 法在上文中)供开发者服务端使用,参数示例如下: 

http://your_callback_url?userId=your- 

uerid&transId=test_trans_id&sign=11121222&amount=0&name=name&extra=your -extra-data 

##### GET 请求的各个参数说明: 

|参数名|参数类|参数说明|
|---|---|---|
|称|型||
|extra|String|开发者在SDK中请求激励视频时设置的自定义附加参数|
|||“extraData”|
|userId|String|开发者在SDK中请求激励视频时设置的 “thirdUserId”参数|
|transId|String|完成观看的唯一交易ID|
|sign|String|签名|
|name|String|奖励名称|

amoun int 奖励数量 t 

##### 上表中提到的 **sign** 为唯一签名,计算方式为 **:** 

##### **sign = md5(appSecurityKey:transId)** ,所有字母均为小写。 

其中 **appSecurityKey** 为在 **SSP** 平台设置回调 **url** 时获得, **transId** 为请求中的参数。 

SDK 在请求开发者的指定 url 的时候,开发者需要按照一定的格式返回给 SDK 结果,返回数据为 json 的格式,详情如下: 

|字段名|字段定|字段类|备注|
|---|---|---|---|
|称|义|型||
|isValid|校验结 果|bool|判定结果,是否发放奖励。|

{ "isValid" : true } 

### **4.2** 全屏视频广告 

全屏视频广告为全屏展示,一定时间后可跳过 接入示例参考 demo 中的 TestFullScreenVideoPage 

#### 加载广告 

```arkts
const scene = new KSAdScene() .setposId("your posId") .setScreenOrientation(KSAdScreenDirection.vertical) // 请求广告 KSAdSDK.getLoadManager().loadFullScreenAd(scene, { onAdLoad(ad: KSFullScreenAd) { ToastUtil.show("全屏视频加载成功"); ad.setInteractListener({ onAdShow() { ToastUtil.show("全屏视频曝光"); }, onVideoPlayStart() { ToastUtil.show("全屏视频开始播放"); }, onVideoPlayEnd() { 
```

ToastUtil.show("全屏视频播放结束"); }, onVideoPlayError(code: number, extra: string) { ToastUtil.show("全屏视频播放失败:" + extra); }, onAdClick() { ToastUtil.show("全屏视频点击"); }, onAdClose() { ToastUtil.show("全屏视频关闭"); } }) }, onError(code: number, msg: string) { ToastUtil.show("全屏视频加载失败:" + msg); }, onRequestSuccess(adNum: number) { } }) 

#### 展示全屏视频 

// 展示广告 ad.show({ videoSoundEnable: true }) 

#### 全屏相关回调 

{ // 广告点击 onAdClick?: () => void; // 广告关闭 onAdClose?: () => void; // 广告曝光 onAdShow?: () => void; // 视频播放开始 

onVideoPlayStart?: () => void; 

// 视频播放结束 onVideoPlayEnd?: () => void; 

// 视频播放失败 onVideoPlayError?: (code: number, extra: string) => void; // 视频直接跳过 onVideoSkipToEnd?: (playDurationMs: number) => void; } 

### **4.3** 开屏广告 

开屏广告为用户在进入 App 时展示的广告,SDK 提供的是一个 Builder 方法 接入示例参考 demo 中的 TestSplashPage 

加载广告 

// 开始请求开屏广告 const scene : KSAdScene = new KSAdScene() .setposId(posId_SPLASHSCREEN) const that = this; KSAdSDK.getLoadManager().loadSplashAd(scene, { onRequestSuccess(adNumber) { // 广告请求成功 }, onError(code: number, msg: string) { // 广告请求失败 Logger.d('ksad', 'request failed:' + code + ":" + msg); ToastUtil.show("开屏广告加载失败:" + msg); router.back(); }, onAdLoad(splashAd: KSSplashAd) { // 广告成功加载,可以展示 Logger.d('ksad', 'request success:' + splashAd); that.splashAd = splashAd; that.splashAd.interactListener = { onAdShowStart() { Logger.d('ksad', 'on show start'); ToastUtil.show("开屏广告曝光") 

}, onAdShowEnd() { Logger.d('ksad', 'on show end'); ToastUtil.show("开屏广告展示结束") router.back(); }, onAdClick() { Logger.d('ksad', 'on ad click'); ToastUtil.show("开屏广告点击") }, onAdSkip() { Logger.d('ksad', 'on ad skip'); ToastUtil.show("开屏广告跳过") router.back(); } } that.hasSplash = true; } }); 

#### 开屏相关回调 

/** * 开屏广告交互监听器 */ export interface KSSplashAdInteractListener { // 广告展示、曝光 onAdShowStart?: () => void; // 广告展示结束 onAdShowEnd?: () => void; // 广告展示失败 onAdShowError?: (code: number, extra: string) => void; // 广告点击 onAdClick?: () => void; // 广告跳过 onAdSkip?: () => void; } 

### **4.4** 信息流广告 

信息流广告为卡片样式,支持图片和视频,由 SDK 根据配置展示特定样式 接入示例参考 demo 中的 TestFeedPage 

#### 加载广告 

// 加载广告 let scene: KSAdScene = new KSAdScene() .setposId("your posId") .setAdNum(5) const that = this; KSAdSDK.getLoadManager().loadFeedAd(scene, { onAdLoad(ads: KSNativeAd[]) { ToastUtil.show("feed 广告加载完成:" + ads.length); // 添加广告数据 for (let index = 0; index < ads.length; index++) { const element = ads[index]; ... } }, onError(errorCode: number, msg: string) { ToastUtil.show("feed 广告加载失败:" + errorCode + ":" + msg); }, onRequestSuccess(adNum: number) { } }) 

#### 信息流相关回调 

/** * 信息流广告交互回调 */ export interface KSFeedAdInteractListener { // 广告曝光 onAdShow?: () => void; // 广告点击 onAdClick?: () => void; // 不喜欢按钮点击 onDislikeClicked?: () => void; } 

#### 展示逻辑 

build() { BuildFeedAdView(feedAd) } 

注:SDK 内部信息流组件自带了 reuseId,如果需要将 SDK 内部信息流组件包装到自定义容器,需 要手动指定容器的 reuseId,确保信息流广告不会重复渲染 

具体复用逻辑参考官方文档:https://developer.huawei.com/consumer/cn/doc/harmonyosguides/bpta-best-practices-long-list 

### **4.5** 插屏广告 

插屏广告为卡片展示的广告,支持图片和视频,SDK 对外提供的为 Builder 方法,默认宽高 100% 接入示例参考 demo 中的 TestInterstitialPage 

#### 加载广告 

import { KSBuildInterstitialAdView, KSAdScene, KSAdSDK, KSInterstitialAd } from 'ksadsdk' 

```arkts
const scene = new KSAdScene() .setposId('your posId') .setScreenOrientation(KSAdScreenDirection.vertical) // 请求广告 KSAdSDK.getLoadManager().loadInterstitialAd(scene, { onAdLoad(ad: KSInterstialAd) { ToastUtil.show("插屏加载成功"); }, onError(code: number, msg: string) { ToastUtil.show("插屏加载失败:" + msg); }, onRequestSuccess(adNum: number) { } }) }) 
```

#### 插屏相关回调 

/** 

##### * 插屏视频广告交互回调 

*/ export interface KSInterstitialAdInteractListener { // 广告曝光 onAdShow?: () => void; // 广告点击 onAdClick?: () => void; // 广告关闭 onAdClose?: () => void; // 视频播放开始 onVideoPlayStart: () => void; // 视频播放结束 onVideoPlayEnd: () => void; // 视频播放失败 onVideoPlayError?: (code: number, extra: number) => void; // 视频直接跳过 onVideoSkipToEnd?: (playDuration: number) => void; } 

#### 插屏展示 

build() { Stack() { KSBuildInterstitialAdView(this.interstitialAd!) } } 

### **4.6** 媒体自渲染广告 

自渲染广告可自定义布局的广告,SDK 提供广告信息,由开发者自行决定展示样式 接入示例参考 demo 中的 TestNativePage 

加载广告 

// 加载广告 let scene: KSAdScene = new KSAdScene() .setposId("your posId") .setAdNum(5) const that = this; KSAdSDK.getLoadManager().loadNativeAd(scene, { onAdLoad(ads: KSNativeAd[]) { ToastUtil.show("native 广告加载完成:" + ads.length); // 添加广告数据 for (let index = 0; index < ads.length; index++) { const element = ads[index]; element.videoPlayListener = { onVideoReady() { }, onVideoPlayStart() { }, onVideoPlayComplete() { }, onVideoResume() { }, onVideoPause() { }, onVideoPlayError() { } }; element.interactListener = { onAdShow() { ToastUtil.show("自渲染广告曝光"); }, onAdClick() { ToastUtil.show("自渲染广告点击"); } } } }, 

onError(errorCode: number, msg: string) { ToastUtil.show("native 广告加载失败:" + errorCode + ":" + msg); }, onRequestSuccess(adNum: number) { } }) 

#### 自渲染相关回调 

/** * 自渲染广告交互回调 */ export interface KSNativeAdInteractListener { // 广告曝光 onAdShow?: () => void; // 广告点击 onAdClick?: () => void; } /** * 视频播放回调 */ export interface KSVideoPlayListener { // 视频广告即将播放 onVideoReady?: () => void; // 视频广告播放回调 onVideoPlayStart?: () => void; // 视频广告播放完成回调 onVideoPlayComplete?: () => void; // 视频广告暂停 onVideoPause?: () => void; // 视频广告播放 onVideoResume?: () => void; // 视频广告加载失败 onVideoPlayError?: (code: number, extra: number) => void; } 

开放字段 

// 广告描述 abstract getAdDescription(): string; // 广告来源,可能为空 abstract getAdSource(): string; // 获取广告角标的 logo abstract getAdSourceLogoUrl(logoType: KSAdSourceLogoType): string; // 广告图片集合,单图和组图类型广告素材有返回,视频类素材返回为空 abstract getImageList(): Array<KSAdImage>; // 广告 Icon 链接 abstract getAppIconUrl(): string; // 下载类型的 AppName,非下载返回为空 abstract getAppName(): string; // 应用下载次数文案,非下载返回为空 eg:1000W 此下载 abstract getAppDownloadCountDes(): string; // 应用下载评分,取值 0~5.0; 非下载返回为 0 abstract getAppScore(): number; // 获取开发者主体 abstract getCorporationName(): string; // 获取应用权限信息 abstract getPermissionInfo(): string; // 获取应用权限信息链接 abstract getPermissionInfoUrl(): string; // 获取产品介绍信息 abstract getIntroductionInfo(): string; // 获取产品介绍信息链接 abstract getIntroductionInfoUrl(): string; // 获取隐私条款链接 abstract getAppPrivacyUrl(): string; // 获取隐私条款链接 abstract getAppVersion(): string; // 获取 App 包名 abstract getAppPackageName(): string; // 获取下载包大小 abstract getAppPackageSize(): number; // 获取产品名 abstract getProductName(): string; // 素材类型 abstract getMaterialType(): KSAdMaterialType; // 交互类型 

abstract getInteractionType(): KSAdInteractionType; // 视频封面 url abstract getCoverUrl(): KSAdImage; // 视频 url abstract getVideoUrl(): string; // 视频时长 abstract getVideoDuration(): number; // 按钮文案 abstract getActionDescription(): string; // 唯一标识,用于 LazyForEach 标识广告 abstract getUniqueKey(): string; // 可见区域监听数组 abstract getVisibleAreaRatios(): number[]; // 可见区域监听方法,用于 SDK 内部判断页面展示比例,处理广告曝光&视频播放等 abstract getVisibleAreaChangeListener(): (isVisible: boolean, currentRatio: number) => void; // 控件点击监听 

abstract getClickHandler(): (context: common.UIAbilityContext, event: ClickEvent) => void; 

#### 注意事项 

##### 广告曝光 

广告曝光逻辑按照页面展示比例来计算,开发者需要在自渲染的广告组件上监听展示比例并且回调 给 SDK,示例: 

// 添加可见区域监听,SDK 内部处理曝光逻辑 

.onVisibleAreaChange(this.itemInfo.nativeAd?.getVisibleAreaRatios(), this.itemInfo.nativeAd?.getVisibleAreaChangeListener()) 

##### 广告点击 

目前 SDK 内部无法自动给开发者的 UI 组件添加点击事件,对于点击后需要触发转化的控件,需要 手动添加点击事件并且回调给 SDK,示例: 

.onClick((e: ClickEvent) => { // 点击转化 this.itemInfo?.nativeAd?.getClickHandler()(getContext(this) as common.UIAbilityContext, e) }) 

### **4.7** 通用接口 

#### **1.** 获取 **ECPM** 

通过 getEcpm()的方法获取 ecpm 

/** * 获取 ecpm,单位:分,默认为 0 */ abstract getEcpm(): number; 

#### **2.** 竞价成功回传价格 

通过 setBidEcpm()方法上报竞价信息 

/** * 广告竞胜之后,上报竞价信息,备注:广告展示前调用 * * @param bidEcpm 竞胜报价,单位:分/千次 */ abstract setBidEcpm(i171: number): void; 

#### **3.** 竞价成功回传价格和竞败方的最高价格 

如果媒体有使用Bidding 竞价,需要在竞价成功后调用对应广告接口的 setBidEcpmAndHighestLoss(bidEcpm: number, lossBidEcpm: number)的方法。回传竞胜 相关信息。 

/** * 广告竞胜之后,在广告展示前调用回传竞价成功信息 * @param bidEcpm 单位:分 此竞胜的价格 * @param lossBidEcpm 单位:分 竞败方的最高价格 */ 

abstract setBidEcpmAndHighestLoss(bidEcpm: number, lossBidEcpm: number): void; 

**4.** 广告曝光失败回传接口 快速广告曝光失败时需要调用对应广告接口的 reportExposureFail(errorCode: KSAdExposureFailCode, reason: KSAdExposureFailReason)方法,回传失败原因信息。 

/** 

##### * 广告曝光失败后上报失败原因 

* 

* @param errorCode 失败类型 

* 当失败类型为 KSAdExposureFailCode.BID_FAILED 时曝光失败原因请上报胜出的 KSAdExposureFailReason.winEcpm 值 

* @param reason 曝光失败原因描述 

*/ 

abstract reportExposureFail(errorCode: KSAdExposureFailCode, reason: KSAdExposureFailReason): any; 

●AdExposureFailureCode 枚举类型 

export declare const enum KSAdExposureFailCode { OTHER = 0, //其他 MEDIA_SIDE_PRICE_FILTER = 1, //媒体侧底价过滤 BID_FAILED = 2, //快手广告竞价失败 CACHE_INVALID = 3, //快手广告缓存失效 PRIORITY_REDUCED = 4 //快手广告曝光优先级降低 } 

●KSAdExposureFailReason 接口说明 当广告曝光失败的原因是 KSAdExposureFailCode.BID_FAILED 快手广告竞价失败时,需要上报 AdExposureFailedReason 失败详细原因,具体参数如下; 

export interface KSAdExposureFailReason { winEcpm?: number; //竞胜方,报价,单位分/千次 adnType?: KSAdnType; //竞胜方来源 adnName?: KSAdnName;//竞胜方为第三方ADN 时 } 

export declare const enum KSAdnType { KS_AD = 1, //输给快手其他广告时,上报此枚举值 THIRD_PARTY_AD = 2, //输给第三方ADN 时,上报此枚举值,并上报第三方ADN 平台名 INDIVIDUAL_AD = 3  //输给自售广告主时,上报此枚举值 } 

export declare const enum KSAdnName { 

CHUANSHANJIA = "chuanshanjia", //穿山甲广告平台 GUANGDIANTONG = "guangdiantong",  //广点通广告平台 BAIDU = "baidu",  //百度广告平台 OTHER = "other"  //其他广告平台 } 

## **5.** 错误码 

|code|说明|
|---|---|
|40001|没有网络|
|40002|数据解析失败|
|40003|广告数据为空|
|40004|缓存视频资源失败|
|100001|参数有误|
|100002|服务器错误|
|100003|不允许的操作|
|100004|服务不可用|
|310001|appId未注册|
|310002|appId无效|
|310003|appId已封禁|
|310004|packageName与注册的packageName 不一致|
|310005|操作系统与注册的不一致|
|320002|appId对应账号无效|
|320003|appId对应账号已封禁|
|330001|posId未注册|
|330002|posId无效|

|330003|posId已封禁|
|---|---|
|330004|posId与注册的appId信息不一致|

## **6. FAQ** 

请求视频广告失败: 

_1._ 请核对广告 _SDK_ 初始化的 _AppID_ 是否正确; 

_2._ 请核对请求广告时传入的广告场景参数 _posId_ 是否正确。 

_3._ 请根据返回的错误吗,参考错误码对照表知晓问题
