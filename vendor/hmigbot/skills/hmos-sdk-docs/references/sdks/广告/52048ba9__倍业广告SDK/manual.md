# 鸿蒙版 倍业 SDK 

SDK 集成 

手 动引 入har 包 

在 oh-package.json5 添加依赖 

{ 

"dependencies": { 

"mercurysdk": "file:../entry/libs/mercuryadhar.har" 

} 

} 

{ 

"dependencies": { 

"mercurysdk": "file:../entry/libs/mercuryadhar.har" 

} 

} 

# 配置权限 

打开 app 模块的 module.json5文 件 

添加以下权限:访问 网 络、获取 网 络状态、获取 广 告追踪标识 ( oaid )、定位(可选)、传感器(可选) 

"requestPermissions": [ 

{ 

"name": "ohos.permission.INTERNET", 

"reason": "$string:internet_permission_reason", 

}, 

{ 

"name": "ohos.permission.LOCATION", "reason": "$string:permission_LOCATION", 

}, 

{ 

"name": "ohos.permission.APPROXIMATELY_LOCATION", "reason": "$string:permission_LOCATION", 

}, 

{ 

"name": "ohos.permission.APP_TRACKING_CONSENT", "reason": "$string:oaid_permission_reason", 

}, 

{ 

"name": "ohos.permission.GET_NETWORK_INFO", "reason": "$string:net_permission_reason", 

}, 

{ 

"name": "ohos.permission.GET_WIFI_INFO", "reason": "$string:net_permission_reason", 

}, 

{ 

"name": "ohos.permission.ACCELEROMETER", "reason": "$string:permission_need", 

} 

] 

"requestPermissions": [ 

{ 

"name": "ohos.permission.INTERNET", 

"reason": "$string:internet_permission_reason", 

}, 

{ 

"name": "ohos.permission.LOCATION", "reason": "$string:permission_LOCATION", 

}, 

{ 

"name": "ohos.permission.APPROXIMATELY_LOCATION", "reason": "$string:permission_LOCATION", 

}, 

{ 

"name": "ohos.permission.APP_TRACKING_CONSENT", "reason": "$string:oaid_permission_reason", 

}, 

{ 

"name": "ohos.permission.GET_NETWORK_INFO", "reason": "$string:net_permission_reason", 

}, 

{ 

"name": "ohos.permission.GET_WIFI_INFO", "reason": "$string:net_permission_reason", 

}, 

{ 

"name": "ohos.permission.ACCELEROMETER", "reason": "$string:permission_need", 

} 

] 

SDK 初始化 

首先在倍联后台中新建媒体,获取到 appid 和 appkey 信息,具体操作 如下图: 

点击添加媒体选项后,选择鸿蒙系统,并填入必填项: 

填入必填信息后,将返回媒体列表,便可以查看到对应的 appid 和 appkey 信息 

在应 用入口 EntryAbility 

得 onWindowStageCreate(windowStage: window.WindowStage) 

在应 用入口 EntryAbility 

得 onWindowStageCreate(windowStage: window.WindowStage) 

方 法中调 用 以下 

# 代码来执 行SDK 初始化 

async onWindowStageCreate(windowStage: window.WindowStage) { 

****** 

****** 

// 隐私信息采集配置 MercuryAD.setPrivacyController(new MyPrivacy) 

//SDK 初始化 

MercuryAD.init(this.context, " 您在倍联后台申请得 appId", " 您在倍联 后台申请得 

// 设置 windowStage 

MercuryAD.initWindow(windowStage) 

} 

async onWindowStageCreate(windowStage: window.WindowStage) { 

****** 

****** 

// 隐私信息采集配置 MercuryAD.setPrivacyController(new MyPrivacy) 

//SDK 初始化 

MercuryAD.init(this.context, " 您在倍联后台申请得 appId", " 您在倍联 后台申请得 

// 设置 windowStage 

MercuryAD.initWindow(windowStage) 

} 

# 隐私配置说明 

import { BYPrivacyController,BYLocation } from 'mercurysdk'; 

// 新建继承于 BYPrivacyController 得类 文 件,配置以下相关 方 法得返 回值 export class MyPrivacy extends BYPrivacyController { 

/** 

- app 在项 目 中配置权限。在适当时机申请权限,然后 用 户授权。 

* 1 :如果 isCanUseAppTrackingConsent() 返回 false ,当 sdk 需要 oaid 时,则使 用get 

* 2 :如果 isCanUseAppTrackingConsent() 返回 true 。当 sdk 需要 oaid 

时,先去检查权 

- @returns 是否允许 SDK 获取系统 oaid 

*/ 

isCanUseAppTrackingConsent(): boolean { return super.isCanUseAppTrackingConsent() 

} 

/** 

* 

# * @returns 媒体传 入 的 oaid 

*/ 

getCusOaid(): string | undefined { return super.getCusOaid() 

} 

/** 

- app 在项 目 中配置权限。并在合适时机动态申请权限, 用 户授权。 

- 1 :当 isCanUseLocation() 返回 false 。当 sdk 需要地理位置信息时, 使 用 getCusLo 

- 2 :当 isCanUseLocation() 返回 true 。当 sdk 需要地理位置信息时,先 去检查是否已经得 

- @returns 是否允许 SDK 获取系统地理位置信息 

*/ 

isCanUseLocation(): boolean { return super.isCanUseLocation() 

} 

/** 

* 

- @returns 媒体传 入 的地理位置信息 

*/ 

getCusLocation(): BYLocation | undefined { return super.getCusLocation() 

} 

/** 

* 是否允许 SDK 使 用ohos.permission.GET_WIFI_INFO 权限对应的信 

息。 

* 返回 true ,如果应 用 申请了 ohos.permission.GET_WIFI_INFO 权限, sdk 则可以使 用 

- 返回 false , sdk 则不可以使 用 。 

* @returns 

*/ 

isCanUseWifiState(): boolean { return super.isCanUseWifiState() 

} 

/** 

* 媒体 isCanUseWifiState() 返回 false 时, SDK 使 用getMacAddress() 的 返回值作为 ma 

* @returns 

*/ 

getMacAddress(): string | undefined { return super.getMacAddress() 

} 

} 

/** 

* 

- @returns 媒体传 入 的地理位置信息 

*/ 

getCusLocation(): BYLocation | undefined { return super.getCusLocation() 

} 

/** 

* 是否允许 SDK 使 用ohos.permission.GET_WIFI_INFO 权限对应的信 息。 

* 返回 true ,如果应 用 申请了 ohos.permission.GET_WIFI_INFO 权限, sdk 则可以使 用 

- 返回 false , sdk 则不可以使 用 。 

- @returns 

*/ 

isCanUseWifiState(): boolean { return super.isCanUseWifiState() 

} 

/** 

* 媒体 isCanUseWifiState() 返回 false 时, SDK 使 用getMacAddress() 的 返回值作为 ma 

* @returns 

*/ 

getMacAddress(): string | undefined { return super.getMacAddress() 

} 

} 

# 更多配置调 用API 说明 

类名: MercuryAD 

方 法名 

- 方 法介绍 

getVersion(): string 

获取当前 SDK 版本号 

init(context: Context, appId: string, appKey: string) 

SDK 初始化 方 法 

setPrivacyController(controller: BYPrivacyController) 

隐私相关控制 

debug() 

调 用 后开启 debug 模式,默认不开启 

useHttps() 

调 用 后 网 络请求接 口 将使 用https 链接,默认使 用http 链接 

initWindow(windowStage: window.WindowStage) 

设置 WindowStage , 用 来部分 广 告加载展示 

子 窗 口 

广 告位接 入 

广告位创建指南: 

Blink 后台依次点击资源管理 - 广告位管理 - 添加广告位 

然后选择之前创建好的鸿蒙测试媒体,以及选择需要使用得广告位类 型信息, 

所有配置都选好后,点击右下角的提交按钮,即可完成广告位创建。 

提交成功后获取到广告位 id 如图: 

广 告位通 用API 参考: 

通 用 代码位配置参数类: MercuryEntry 

方 法名 

# 方 法介绍 

setCodeId(codeId: string): MercuryEntry 

设置代码位 id ,必须设置 

setAdSize(widthVP: number, heightVP: number): MercuryEntry 

设置 广 告渲染尺 寸 ,单位 VP ,不设置默认值为 0 ,代表宽度撑满, 高 度 自 适应,可选设置,建议在 banner 及模板信息流中使 用 

通 用广 告请求回调类: MercuryLoadListener 

方 法名 

方 法介绍 

onAdLoaded: () => void 

- 广 告加载成功 

onAdError: (err: MercuryErr) => void 

广 告获取失败 

通 用广 告关闭枚举类: MercuryCloseType 

字段 

含义 

UNKNOWN = 0 

未知 

AD_CLICK = 1 

广 告点击(部分位置适 用 ) 

SKIP_CLICK = 2 

点击了跳过 

COUNT_DOWN = 3 

倒计时结束 

通 用 渲染配置类: MercuryRenderOption 

字段 含义 

windowStage?: window.WindowStage 

设置 windowStage , 用 来启动 SubWindow 展示 广 告 

layoutFullScreen: boolean = false 

设置 SubWindow 是否全屏展示,仅开屏、插屏、激励位置 生 效 

# 开屏 

具体使 用方 法可参考 demo 中得 SplashDemoPage.ets 展示效果预览: 

# 请求 广 告: 

# // 回调监听 

private mLoadListener: MercuryLoadListener = { onAdLoaded: () => { 

console.log(` 回调 - onAdLoaded`); 

}, 

onAdError: (err: MercuryErr): void => { 

console.log(` 回调 - onAdError ; err = ${JSON.stringify(err)}`); 

} 

} 

# // 初始化请求参数,填 入广 告位 id 

let opt = new MercuryEntry().setCodeId(this.adID) 

// 初始化开屏 广 告 

this.splash = new MercurySplash(opt) 

//自 定义跳过按钮(可选) 

// this.splash.setCustomSkip(customCloseBtnBuilder) 

// 请求 广 告 this.splash.loadAd(this.mLoadListener) 

// 回调监听 

private mLoadListener: MercuryLoadListener = { onAdLoaded: () => { 

console.log(` 回调 - onAdLoaded`); 

}, 

onAdError: (err: MercuryErr): void => { 

console.log(` 回调 - onAdError ; err = ${JSON.stringify(err)}`); 

} 

} 

# // 初始化请求参数,填 入广 告位 id 

let opt = new MercuryEntry().setCodeId(this.adID) 

// 初始化开屏 广 告 

this.splash = new MercurySplash(opt) 

//自 定义跳过按钮(可选) 

// this.splash.setCustomSkip(customCloseBtnBuilder) 

// 请求 广 告 this.splash.loadAd(this.mLoadListener) 

# 展示 广 告 

方 法 1 :新打开 subWindow 窗 口 展示 

# // 设置渲染选项 

let renOp = new MercuryRenderOption() 

// 赋值 windowStage , 用 来新建 子 窗 口 renOp.windowStage = DemoConstants.windowStage 

// 展示 广 告 

this.splash.showAd(renOp) 

# // 设置渲染选项 

let renOp = new MercuryRenderOption() 

// 赋值 windowStage , 用 来新建 子 窗 口 renOp.windowStage = DemoConstants.windowStage 

// 展示 广 告 

this.splash.showAd(renOp) 

方 法 2 : view 展示 

# // 定义 NodeController 组件 

@State splashAdComponent?: NodeController = undefined 

........................ 

........................ 

# //广 告成功后对组件赋值 

this.splashAdComponent = this.splash.getAdComponent() //builder 中使 用 : 

NodeContainer(this.splashAdComponent) 

// 定义 NodeController 组件 

@State splashAdComponent?: NodeController = undefined 

........................ 

........................ 

# //广 告成功后对组件赋值 

this.splashAdComponent = this.splash.getAdComponent() 

//builder 中使 用 : 

NodeContainer(this.splashAdComponent) 

# 监听渲染回调 

this.splash.setRenderListener({ onShow: (): void => { //广 告曝光 

}, 

onClick: (): void => { //广 告点击 

}, 

onRenderErr: (err: MercuryErr): void => { //广 告渲染失败 }, 

onClose: (type: MercuryCloseType): void => {//广 告关闭 

} 

# }) 

this.splash.setRenderListener({ onShow: (): void => { //广 告曝光 

}, 

onClick: (): void => { //广 告点击 

}, 

onRenderErr: (err: MercuryErr): void => { //广 告渲染失败 }, 

onClose: (type: MercuryCloseType): void => {//广 告关闭 

} 

}) 

# 相关 API 接 口 说明 

开屏 广 告类: MercurySplash 

方 法名 

方 法介绍 

constructor(option: MercuryEntry) 

构造 方 法,初始化 广 告类 

loadAd(loadListener: MercuryLoadListener): void 

请求 广 告 

getPrice(): number 

获取价格,单位 人⺠ 币分 

getAdComponent(): NodeController | undefined 

获取 用 来渲染的 广 告组件 

showAd(renderOption: MercuryRenderOption): void 

展示 广 告,将开启 子 窗 口 展示开屏 广 告 

setRenderListener(splashRenderListener: MercurySplashRenderListener): void 

# 设置渲染回调 

setCustomSkip(customSkipBuilder?: WrappedBuilder<[closeBlock: () => void]>): void 

# 设置 自 定义跳过按钮 

开屏渲染回调类: MercurySplashRenderListener 

# 方 法名 

方 法介绍 

onShow: () => void 

广 告曝光 

onClick: () => void 

广 告点击 

onRenderErr: (err: MercuryErr) => void 

# 广 告渲染失败 

onClose: (type: MercuryCloseType) => void 

# 广 告关闭 

# 插屏 

具体使 用方 法可参考 demo 中得 InterstitialDemoPage.ets 展示效果预 览: 

# 请求 广 告: 

# // 回调监听 

private mLoadListener: MercuryLoadListener = { onAdLoaded: () => { 

console.log(` 回调 - onAdLoaded`); 

}, 

onAdError: (err: MercuryErr): void => { 

console.log(` 回调 - onAdError ; err = ${JSON.stringify(err)}`); 

} 

} 

let opt = new MercuryEntry().setCodeId(this.adID) 

this.mercuryAd = new MercuryInterstitial(opt) this.mercuryAd.loadAd(this.mLoadListener) 

# // 回调监听 

private mLoadListener: MercuryLoadListener = { onAdLoaded: () => { 

console.log(` 回调 - onAdLoaded`); 

}, 

onAdError: (err: MercuryErr): void => { 

console.log(` 回调 - onAdError ; err = ${JSON.stringify(err)}`); 

} 

} 

let opt = new MercuryEntry().setCodeId(this.adID) 

this.mercuryAd = new MercuryInterstitial(opt) this.mercuryAd.loadAd(this.mLoadListener) 

# 展示 广 告 

let renOp = new MercuryRenderOption() renOp.layoutFullScreen = false this.mercuryAd.showAd(renOp) 

let renOp = new MercuryRenderOption() renOp.layoutFullScreen = false this.mercuryAd.showAd(renOp) 

# 相关 API 接 口 说明 

插屏 广 告类: MercuryInterstitial 

# 方 法名 

方 法介绍 

constructor(option: MercuryEntry) 

构造 方 法,初始化 广 告类 

loadAd(loadListener: MercuryLoadListener): void 

# 请求 广 告 

getPrice(): number 

获取价格,单位 人⺠ 币分 

showAd(renderOption: MercuryRenderOption): void 

展示 广 告,将开启 子 窗 口 展示开屏 广 告 

setRenderListener(mRenderListener: MercuryInterstitialRenderListener): void 

# 设置渲染回调 

插屏渲染回调类: MercuryInterstitialRenderListener 

# 方 法名 

方 法介绍 

onShow: () => void 

广 告曝光 

onClick: () => void 

广 告点击 

onRenderErr: (err: MercuryErr) => void 

广 告渲染失败 

onClose: (type: MercuryCloseType) => void 

广 告关闭 

# 模板信息流 

具体使 用方 法可参考 demo 中得 LazyFeedDemoPage.ets 展示效果预览: 

# 请求 广 告: 

# // 回调监听 

private mLoadListener: MercuryLoadListener = { onAdLoaded: () => { 

console.log(` 回调 - onAdLoaded`); 

}, 

onAdError: (err: MercuryErr): void => { 

console.log(` 回调 - onAdError ; err = ${JSON.stringify(err)}`); 

} 

} 

let opt = new MercuryEntry().setCodeId(this.adID) 

this.mercuryAd = new MercuryFeed(opt) this.mercuryAd.loadAd(this.mLoadListener) 

# // 回调监听 

private mLoadListener: MercuryLoadListener = { onAdLoaded: () => { 

console.log(` 回调 - onAdLoaded`); 

}, 

onAdError: (err: MercuryErr): void => { 

console.log(` 回调 - onAdError ; err = ${JSON.stringify(err)}`); 

} 

} 

let opt = new MercuryEntry().setCodeId(this.adID) 

this.mercuryAd = new MercuryFeed(opt) this.mercuryAd.loadAd(this.mLoadListener) 

# 展示 广 告 

# // 定义列表数据 

dataSource: FeedListDataSource = FeedViewModel.getFeedListDataSource(20) 

........................ 

........................ 

# //广 告成功后插 入 数据 

```arkts
insert(element: MercuryFeed, index: number) { const dataItem = new DataItem(); dataItem.feedAd = element; this.dataSource.insertItem(dataItem, index ); 
```

} 

//builder 中使 用 : 

List() { 

LazyForEach(this.dataSource, (item: DataItem, idx: number) => ListItem() { 

if (item.feedAd) { 

// 展示 广 告 

NodeContainer(item.feedAd.getAdComponent()).width("100%" 

// .height(200) 

} else { 

FeedItemComponent({ itemInfo: item }) 

.reuseId("feeditemcomponent") 

} 

} 

}, (item: DataItem, idx: number) => { const feedAdItem = item.feedAd; if (feedAdItem) { 

return this?.getUniqueKey(idx); 

} 

// 示例 方 法,实际开发中需要开发者 自行 处理 

return item.title.toString(); 

} 

) 

} 

# 相关 API 接 口 说明 

广 告类: MercuryFeed 

方 法名 

方 法介绍 

constructor(option: MercuryEntry) 

构造 方 法,初始化 广 告类 

loadAd(loadListener: MercuryLoadListener): void 

请求 广 告 

getPrice(): number 

获取价格,单位 人⺠ 币分 

showAd(renderOption: MercuryRenderOption): void 

展示 广 告,将开启 子 窗 口 展示开屏 广 告 

setRenderListener(mRenderListener: MercuryFeedRenderListener): void 

# 设置渲染回调 

getAdComponent(): NodeController | undefined 

获取 用 来渲染的 广 告组件 

渲染回调类: MercuryFeedRenderListener 

方 法名 

方 法介绍 

onShow: () => void 

广 告曝光 

onClick: () => void 

广 告点击 

onRenderErr: (err: MercuryErr) => void 

广 告渲染失败 

onClose: (type: MercuryCloseType) => void 

广 告关闭 

激励视频 

具体使 用方 法可参考 demo 中得 RewardDemoPage.ets 展示效果预览: 

# 请求 广 告: 

# // 回调监听 

private mLoadListener: MercuryLoadListener = { onAdLoaded: () => { 

console.log(` 回调 - onAdLoaded`); 

}, 

onAdError: (err: MercuryErr): void => { 

console.log(` 回调 - onAdError ; err = ${JSON.stringify(err)}`); 

} 

} 

let opt = new MercuryEntry().setCodeId(this.adID) 

this.mercuryAd = new MercuryReward(opt) this.mercuryAd.loadAd(this.mLoadListener) 

# // 回调监听 

private mLoadListener: MercuryLoadListener = { onAdLoaded: () => { 

console.log(` 回调 - onAdLoaded`); 

}, 

onAdError: (err: MercuryErr): void => { 

console.log(` 回调 - onAdError ; err = ${JSON.stringify(err)}`); 

} 

} 

let opt = new MercuryEntry().setCodeId(this.adID) 

this.mercuryAd = new MercuryReward(opt) this.mercuryAd.loadAd(this.mLoadListener) 

# 展示 广 告 

let renOp = new MercuryRenderOption() renOp.layoutFullScreen = false this.mercuryAd.showAd(renOp) 

let renOp = new MercuryRenderOption() renOp.layoutFullScreen = false this.mercuryAd.showAd(renOp) 

# 相关 API 接 口 说明 

广 告类: MercuryReward 

# 方 法名 

# 方 法介绍 

constructor(option: MercuryEntry) 

构造 方 法,初始化 广 告类 

loadAd(loadListener: MercuryLoadListener): void 

# 请求 广 告 

getPrice(): number 

获取价格,单位 人⺠ 币分 

showAd(renderOption: MercuryRenderOption): void 

展示 广 告,将开启 子 窗 口 展示开屏 广 告 

setRenderListener(mRenderListener: MercuryRewardRenderListener): void 

# 设置渲染回调 

渲染回调类: MercuryRewardRenderListener 

方 法名 

方 法介绍 

onShow: () => void 

广 告曝光 

onClick: () => void 

广 告点击 

onRenderErr: (err: MercuryErr) => void 

广 告渲染失败 

onClose: (type: MercuryCloseType) => void 

广 告关闭 

onReward: () => void; 

激励达成 

# 相关 API 接 口 说明 

# 横幅 

具体使 用方 法可参考 demo 中得 BannerDemoPage.ets 展示效果预览: 

请求 广 告: 

// 回调监听 

private mLoadListener: MercuryLoadListener = { onAdLoaded: () => { 

console.log(` 回调 - onAdLoaded`); 

}, 

onAdError: (err: MercuryErr): void => { 

console.log(` 回调 - onAdError ; err = ${JSON.stringify(err)}`); 

} 

} 

let opt = new MercuryEntry() 

.setCodeId(this.adID) 

.setAdSize(390, 210) this.mercuryAd = new MercuryBanner(opt) this.mercuryAd.loadAd(this.mLoadListener) 

# // 回调监听 

private mLoadListener: MercuryLoadListener = { onAdLoaded: () => { 

console.log(` 回调 - onAdLoaded`); 

}, 

onAdError: (err: MercuryErr): void => { 

console.log(` 回调 - onAdError ; err = ${JSON.stringify(err)}`); 

} 

} 

let opt = new MercuryEntry() 

.setCodeId(this.adID) 

.setAdSize(390, 210) this.mercuryAd = new MercuryBanner(opt) this.mercuryAd.loadAd(this.mLoadListener) 

# 展示 广 告 

// 定义 NodeController 组件 

@State AdComponent?: NodeController = undefined 

//广 告成功后对组件赋值 

this.AdComponent = this.mercuryAd.getAdComponent() 

//builder 中使 用 : NodeContainer(this.AdComponent) 

// 定义 NodeController 组件 

@State AdComponent?: NodeController = undefined 

# //广 告成功后对组件赋值 

this.AdComponent = this.mercuryAd.getAdComponent() 

//builder 中使 用 : NodeContainer(this.AdComponent) 

# 相关 API 接 口 说明 

广 告类: MercuryBanner 

方 法名 

- 方 法介绍 

constructor(option: MercuryEntry) 

构造 方 法,初始化 广 告类 

loadAd(loadListener: MercuryLoadListener): void 

请求 广 告 

getPrice(): number 

获取价格,单位 人⺠ 币分 

showAd(renderOption: MercuryRenderOption): void 

展示 广 告,将开启 子 窗 口 展示开屏 广 告 

setRenderListener(mRenderListener: MercuryBannerRenderListener): void 

# 设置渲染回调 

渲染回调类: MercuryBannerRenderListener 

方 法名 

方 法介绍 

onShow: () => void 

广 告曝光 

onClick: () => void 

广 告点击 

onRenderErr: (err: MercuryErr) => void 

广 告渲染失败 

onClose: (type: MercuryCloseType) => void 

广 告关闭 

原 生自 渲染 

具体使 用方 法可参考 demo 中得 NativeDemoPage.ets 展示效果预览: 

# 请求 广 告: 

# // 回调监听 

private mLoadListener: MercuryLoadListener = { onAdLoaded: () => { 

console.log(` 回调 - onAdLoaded`); 

}, 

onAdError: (err: MercuryErr): void => { 

console.log(` 回调 - onAdError ; err = ${JSON.stringify(err)}`); 

} 

} 

let opt = new MercuryEntry() 

.setCodeId(this.adID) 

.setAdSize(390, 210) this.mercuryAd = new MercuryNative(opt) this.mercuryAd.loadAd(this.mLoadListener) 

# // 回调监听 

private mLoadListener: MercuryLoadListener = { onAdLoaded: () => { 

console.log(` 回调 - onAdLoaded`); 

}, 

onAdError: (err: MercuryErr): void => { 

console.log(` 回调 - onAdError ; err = ${JSON.stringify(err)}`); 

} 

} 

let opt = new MercuryEntry() 

.setCodeId(this.adID) 

.setAdSize(390, 210) this.mercuryAd = new MercuryNative(opt) this.mercuryAd.loadAd(this.mLoadListener) 

# 展示 广 告 

# //广 告成功后赋值 广 告信息 

let adData = native.getSelfRenderData() 

// 赋值 广 告数据信息,此时会联动刷新展示 广 告 if (adData) { 

this.nativeData.nativeAd = adData 

} 

//builder 中进 行广 告组件渲染 

NativeAdComponent({ itemInfo: this.nativeData }) 

# //广 告成功后赋值 广 告信息 

let adData = native.getSelfRenderData() 

// 赋值 广 告数据信息,此时会联动刷新展示 广 告 if (adData) { 

this.nativeData.nativeAd = adData 

} 

//builder 中进 行广 告组件渲染 

NativeAdComponent({ itemInfo: this.nativeData }) 

NativeAdComponent 组件代码示例: 

import { DataItem } from "../data/DataItem"; 

// 单独封装的 用 来展示 自 渲染 广 告样式的组件 

@Component 

export struct NativeAdComponent { 

// 数据来源 

@State itemInfo: DataItem = new DataItem(); 

// 广 告关闭标识 

@State isClosed: boolean = false 

// 是否返回了 广 告来源 logo 图 片 

@State hasSourceLogo: boolean = false 

videoController: VideoController = new VideoController() 

import { DataItem } from "../data/DataItem"; 

// 单独封装的 用 来展示 自 渲染 广 告样式的组件 

@Component 

export struct NativeAdComponent { 

# // 数据来源 

@State itemInfo: DataItem = new DataItem(); 

// 广 告关闭标识 

@State isClosed: boolean = false 

// 是否返回了 广 告来源 logo 图 片 

@State hasSourceLogo: boolean = false 

videoController: VideoController = new VideoController() 

// 是否使 用 推荐的渲染 方 式 renderSectionRecommend: boolean = true 

aboutToAppear(): void { 

let sourceLogo = this.itemInfo.nativeAd?.getADSourceLogo() this.hasSourceLogo = sourceLogo != undefined && sourceLogo != null & 

} 

build() { 

Column() { 

Text(' 顶部空 白') 

.fontSize(55) 

.backgroundColor(Color.Blue) 

.height(1000) 

if (!this.isClosed) { Column() { 

// 标题 + 关闭按钮 

Row() { Text(this.itemInfo.nativeAd?.getTitle()) 

.fontSize(13) 

.fontColor($r('app.color.text_h1')) 

.layoutWeight(1) 

.height('auto') Image($r('app.media.mry_ic_close')) 

.fillColor($r('app.color.text_h1')) 

.width(25) 

.height(25) 

.onClick(() => { 

//广 告关闭调 用 -- 必须 

this.isClosed = true this.itemInfo.nativeAd?.handleClose() 

}) 

} 

.alignItems(VerticalAlign.Center) 

.width('100%') 

.height(30) 

// 素材渲染区域 ----start------ 

if (this.renderSectionRecommend) { 

// 方 案 一( 推荐 ) :使 用SDK 内部封装好的素材渲染组件(内部处理好了 点击、曝 

NodeContainer(this.itemInfo.nativeAd?.getMaterialComponent() 

.width('100%') 

} else { 

// 方 案 二 : 自 渲染素材展示区域,需要 自 定义适配素材渲染、点击事 件、可 见 性 

Stack({ alignContent: Alignment.Center }) { 

// 视频类 广 告 

if (this.itemInfo.nativeAd?.isVideo()) { Video({ 

src: this.itemInfo.nativeAd?.getVideoUrl(), previewUri: this.itemInfo.nativeAd?.getVideoImage(), / controller: this.videoController 

}) 

.muted(true) 

.controls(false) 

.autoPlay(true) 

.width('100%') 

.objectFit(ImageFit.Fill) 

} else { // 图 片 类 广 告 

Image(this.itemInfo.nativeAd?.getImgList()[0]) 

.width('100%') 

} 

// 特殊交互组件( 比 如摇 一 摇、按钮等交互效果) --方 案 二 可选添加 NodeContainer(this.itemInfo.nativeAd?.getInteractionCompon 

} 

// 点击事件绑定 -- 方 案 二 必须添加 

.onClick((event: ClickEvent) => { this.itemInfo.nativeAd?.handleClick(getContext(this), even 

}) 

// 绑定可 见 检测事件 -- 方 案 二 必须添加 

.onVisibleAreaChange(this.itemInfo.nativeAd?.getVisibleAreaR (isExpanding: boolean, currentRatio: number) => { 

this.itemInfo.nativeAd?.handleVisibleAreaChange(isExpand 

}) 

} 

// 素材渲染区域 ----end------ 

// 底部交互区 Row() { 

// 描述 文 字 

Text(this.itemInfo.nativeAd?.getDesc()) 

.fontSize(12) 

.fontColor($r('app.color.text_h2')) 

.layoutWeight(1) 

// 广 告标识及来源 -- 必须 

Row() { 

if (this.hasSourceLogo) { Image(this.itemInfo.nativeAd?.getADSourceLogo()) 

.margin({ right: 4 

}) 

} 

Text(this.itemInfo.nativeAd?.getADSource()) 

.fontSize(10) 

.textAlign(TextAlign.Center) 

.fontColor($r('app.color.mry_color_white')) 

} 

.alignItems(VerticalAlign.Center) 

.padding(3) .margin(3) 

.borderRadius(3) 

.backgroundColor($r('app.color.mry_color_trans_gray')) 

// 

Button(' 查看详情 ') 

.onClick((event: ClickEvent) => { this.itemInfo.nativeAd?.handleClick(getContext(this), ev 

}) 

.height(30) 

} 

.margin({ top: 10 

}) 

} 

.padding(8) 

.width('100%') 

.backgroundColor(Color.White) 

} 

Text(' 底部空 白') 

.fontSize(55) 

.height(900) 

.backgroundColor(Color.Red) 

} 

} 

} 

相关 API 接 口 说明 

广 告类: MercuryNative 

方 法名 

方 法介绍 

constructor(option: MercuryEntry) 

构造 方 法,初始化 广 告类 

loadAd(loadListener: MercuryLoadListener): void 

请求 广 告 

getPrice(): number 

获取价格,单位 人⺠ 币分 

showAd(renderOption: MercuryRenderOption): void 

展示 广 告,将开启 子 窗 口 展示开屏 广 告 

setRenderListener(mRenderListener: MercuryNativeRenderListener): void 

设置渲染回调 

getSelfRenderData(): MercuryNativeData | undefined 

获取渲染元素信息 

渲染回调类: MercuryNativeRenderListener 

方 法名 

方 法介绍 

onShow: () => void 

广 告曝光 

onClick: () => void 

广 告点击 

onRenderErr: (err: MercuryErr) => void 

广 告渲染失败 

onClose: (type: MercuryCloseType) => void 

广 告关闭 

渲染元素信息类: MercuryNativeData 

方 法名 

方 法介绍 

getMaterialComponent(): NodeController | undefined 

( 推荐使 用) :使 用SDK 内部封装好的素材渲染组件(内部处理好了点 击、曝光等事 件),具体使 用 请参考 demo 示例 

getInteractionComponent(): NodeController | undefined 

获取互动组件、摇 一 摇、按钮等交互组件 

handleClick(context: Context, event: ClickEvent): void 

触发点击事件 

handleClose(): void 

触发 广 告关闭 行 为 

getVisibleAreaRatios(): number[] 

onVisibleAreaChange 入 参 1 ,可 见 区域监听数组 

handleVisibleAreaChange(isExpanding: boolean, currentRatio: number): void 

onVisibleAreaChange 入 参 2 回调 方 法中,进 

行 调 用 

getTitle(): string 

获取 广 告标题 

getDesc(): string 

获取 广 告描述 

getADSource(): string 

获取 广 告来源, 一 般是 ‘广 告 ’ 两个字 

getADSourceLogo(): string 

获取 广 告来源 logo , 小 图 片 , 用 来标记区分 

广 告上游 

getIconUrl(): string 

# 获取 Icon 图 片 地址, 小 图标 

isVideo(): boolean 

判断是否为视频类 广 告 

getVideoImage(): string 

获取视频定帧图 

getImgList(): string[] 

获取图 片 素材地址,可能有多张 

getVideoUrl(): string 

获取视频素材地址 

错误码 

code 含义 

1001 

网 络失败, 一 般是 http 返回状态码 非200 

1002 

网 络请求失败,查看执 行日 志了解具体原因 

1003 

- 网 络请求失败,不 支 持的接 口 返回类型 

1004 

- 广 告请求参数不全 

217 

- 广 告返回信息为空,未填充 

218 

- 广 告返回信息为空,未填充 

220 

- 广 告返回信息为空,未填充 

226 

广 告请求执 行 异常,查看执 行日 志了解具体原因 

301 

广 告渲染执 行 异常,查看执 行日 志了解具体原因 

问题 支 持 

如何获取 SDK 执 行日 志 

BYLog 

BYLog 

在 log 中筛选 关键字,获取 SDK 执 行日 志信息
