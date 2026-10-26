# **天目广告 HarmonyOS Sdk——接入文档 V1.0.1** 

## **1. 概述** 

尊敬的开发者朋友,欢迎您使用天目广告SDK。通过本文档,您可以快速完成广告SDK的 集成。 

### **2. 支持的广告类型** 

|**类型**|**简介**|**适用场景**|
|---|---|---|
|开屏广告|开屏广告以APP启动作为曝光时机的模板 广告,需要将开屏广告视图添加到承载的 广告容器中,提供5s可感知广告展示|APP启动界面常会 使用开屏广告|
|Banner广告|Banner广告是横向贯穿整个可视页面的模 板广告,需要将Banner广告视图添加到承 载的广告容器中|应用程序顶部、中 部或底部占据一个 位置的矩形图片|
|信息流模板广告|信息流模板广告,支持上文下图、下图上 文、左图右文、右图左文、纯图|信息流列表,轮播 控件,固定位置都 是较为适合|
|插屏广告|插屏广告是移动广告的一种常见形式,在 应用流程中弹出,当应用展示插屏广告 时,用户可以选择点击广告,访问其目标 网址,也可以将其关闭并返回应用|在应用执行流程的 自然停顿点,适合 投放这类广告|
|激励视频广告|将短视频融入到APP场景当中,用户观看 短视频广告后可以给予一些应用内奖励|常出现在游戏的复 活、任务等位置, 或者网服类APP的 一些增值服务场景|

## **2. 安装命令** 

**2.1 安装命令** 

1 

2 

3 

ohpm install @admobile/tianmu 

### **2.1 权限申请** 

|**权限名称**|**权限说明**|**使用目的**|
|---|---|---|
|ohos.permission.INTERNET|允许使用 Internet网络|允许使用 Internet网络|
|ohos.permission.GET_NETWORK_INFO|允许应用获取 数据网络信息|允许应用获取 数据网络信息|
|ohos.permission.APP_TRACKING_CONSENT|允许应用读取 开放匿名设备 标识符|允许应用读取 开放匿名设备 标识符|
|ohos.permission.APPROXIMATELY_LOCATION|允许应用获取 设备模糊位置 信息|允许应用获取 设备模糊位置 信息|

## **3. 示例代码** 

### **3.1 SDK初始化** 

在适当位置进行SDK的初始化 

#### **3.1.1 初始化主要 API** 

#### **Tianmu.Sdk 初始化** 

|**方法名**|**入参**|**介绍**|
|---|---|---|
|||设置是否是Debug模式。参数说明:|
|setDebug(isDebug:|isDebug:|debug(true:开启,false:关闭, 默|
|boolean)|boolean|认:false)开发阶段以及提交测试阶段|
|||可设置为true,方便异常排查。|
|setInitListener(listener:|listener:||

|InitListener)|InitListener|初始化状态回调。|
|---|---|---|
|init(context: Context, appid: string)|context: Context appid: string|初始化方法。参数说明: context(初始化SDK的上下文对象) appid(应用初始化id)|
|setOaid(oaid: string)|oaid: string|设置oaid。参数说明:oaid(oaid参 数)。|
|isCanReadNetworkInfo(b: boolean)|b: boolean|是否可读取网络信息。参数说明: b(true:允许,false:不允许,默认 允许)。|
|isCanReadLocation(b: boolean)|b: boolean|是否可读取位置信息。参数说明: b(true:允许,false:不允许,默认 允许)。|

#### **InitListener 初始化监听** 

|**方法名**|**入参**|**介绍**|
|---|---|---|
|onSuccess()||初始化成功。|
|onFailed(code: number, msg: string)||初始化失败。参数说明: code(错误码) msg(错误信息)|

#### **3.1.2 初始化接入示例** 

1 // 设置debug状态,开发阶段建议设置true 2 Tianmu.Sdk.setDebug(true) 3 const listener: InitListener = { 4 onFailed(code: number, msg: string) { 5 ... 6 }, 7 8 onSuccess() { 9 ... 10 } 11 12 } 13 // 设置初始化状态监听 

14 Tianmu.Sdk.setInitListener(listener) 15 // 初始化广告 16 Tianmu.Sdk.init(getContext(this), 'appid') 

### **3.2 广告获取** 

#### **3.2.1 广告获取主要 API** 

#### **Tianmu.AdLoader 广告加载器** 

|**方法名**|**入参**|**介绍**|
|---|---|---|
|loadAd( adParam: AdRequestParams, listener: AdLoadListener )|adParam: AdRequestParams, listener: AdLoadListener|广告加载。参数说明: adParam(广告位配置信 息)、 listener(广告获取回 调)。|
|showAd( uiContext: UIContext, adInfo: AdInfo, adDisplayOptions: AdDisplayOptions, adStatusListener: AdStatusListener )|uiContext: UIContext, adInfo: AdInfo, adDisplayOptions: AdDisplayOptions, adStatusListener: AdStatusListener|插屏、激励视频广告展示方 法。参数说明: uiContext: uiContext上下 文对象; adInfo: 广告对象; adDisplayOptions:展示参 数 adStatusListener:广告状 态|

#### **AdLoadListener 广告加载监听** 

|**方法名**|**入参**|**介绍**|
|---|---|---|
|onSuccess(ads: Array)|ads: Array|广告获取成功。参数说明:ads (广告数组)|
|onFailed(code: number, msg: string)|code: number, msg: string|广告获取失败。参数说明: code(错误码) msg(错误信息)|

#### **AdRequestParams 广告请求参数配置** 

|**参数名**|**介绍**|
|---|---|
|adId|广告位id,广告后台获取|
|adType|广告位类型,可参考AdType|
|adCount|广告获取数量,目前仅支持1个|

#### **AdType 广告类型** 

|**参数名**|**介绍**|
|---|---|
|SPLASH_AD|开屏|
|BANNER_AD|banner|
|NATIVE_EXPRESS_AD|信息流模版|
|INTERSTITIAL_AD|插屏|
|REWARD_AD|激励视频|

#### **AdInfo 广告对象** 

|**方法名**|**入参**|**介绍**|
|---|---|---|
|getPrice()||广告价格。|
|getExpireSeconds()||广告过期剩余时间。|
|isAvailable()||广告是否可用。可用:true, 不可用:false|
|sendWinNotice()||竞价成功上报。|
|sendLossNotice(price: number, reason: number)|price: number, reason: number|竞价失败上报。 参数说明: price(竞赢方价格)、 reason(竞败原因)|

**3.2.2 广告请求示例** 

1 @Entry 2 @Component 3 struct SplashPage 4 { 5 @State adInfo?: AdInfo = undefined 6 ... 7 // 普通广告请求参数 8 adParams: AdRequestParams = { 9 adId: '广告位id', 10 adType: AdType.SPLASH_AD, 11 adCount: 1, 12 } 13 ... 14 15 loadAd() { 16 // 广告请求回调监听 17 const adLoaderListener: AdLoadListener = { 18 onFailed: (code: number, msg: string) => { 19 console.log(TAG, 'onAdError code :: ' + code + ' msg :: ' + msg) 20 }, 21 22 onSuccess: (ads: Array<AdInfo>) => { 23 this.adInfo = ads[0] 24 } 25 } 26 27 // 创建AdLoader广告对象 28 const load: Tianmu.AdLoader = new Tianmu.AdLoader(); 29 load.loadAd(this.adParams, adLoaderListener) 30 } 31 32 } 

### **3.3 开屏广告** 

开屏广告建议在闪屏页进行展示,开屏广告的宽度和高度取决于容器的宽高,会撑满广告 容器。 

#### **3.3.1 开屏广告主要 API** 

#### **SplashComponent 开屏广告展示布局** 

|**参数名**|**介绍**|
|---|---|
|adInfo|onSuccess: (ads: Array) 中获取到的广告对象。|

adStatusListener 广告状态AdStatusListener。 

#### **3.3.2 开屏广告接入示例** 

1 @Entry 2 @Component 3 struct SplashPage 4 { 5 @State isShow: boolean = false 6 @State adInfo?: AdInfo = undefined 7 ... 8 9 build() { 10 SplashComponent({ 11 adInfo: this.adInfo, 12 adStatusListener: { 13 onStatusChanged: (status: string, ad: AdInfo, data: string) => { 14 switch (status) { 15 case AdStatus.AD_SHOW: 16 // 广告曝光 17 break 18 case AdStatus.AD_CLICK: 19 // 广告点击 20 break 21 case AdStatus.AD_SKIP: 22 // 广告跳过 23 break 24 case AdStatus.AD_CLOSE: 25 // 广告关闭 26 break 27 case AdStatus.AD_RENDER_FAILED: 28 // 广告渲染失败 29 break 30 } 31 } 32 } 33 }) 34 .visibility(this.isShow ? Visibility.Visible : Visibility.None) 35 } 36 37 } 

### **3.4 横幅广告** 

Banner横幅广告建议放置在 **固定位置** 。 

#### **3.4.1 横幅广告主要 API** 

#### **BannerComponent 横幅广告展示布局** 

**参数名 介绍** adInfo onSuccess: (ads: Array) 中获取到的广告对象。 adStatusListener 广告状态AdStatusListener。 **3.4.2 横幅广告接入示例** 1 @Entry 2 @Component 3 struct BannerPage 4 { 5 @State isShow: boolean = false 6 @State adInfo?: AdInfo = undefined 7 ... 8 9 build() { 10 BannerComponent({ 11 adInfo: adInfo, 12 adStatusListener: { 13 onStatusChanged: (status: string, ad: AdInfo, data: string) => { 14 switch (status) { 15 case AdStatus.AD_SHOW: 16 // 广告曝光 17 break 18 case AdStatus.AD_CLICK: 19 // 广告点击 20 break 21 case AdStatus.AD_CLOSE: 22 // 广告关闭 23 break 24 case AdStatus.AD_RENDER_FAILED: 25 // 广告渲染失败 26 break 27 } 28 } 29 } 30 }) 31 .visibility(this.isShow ? Visibility.Visible : Visibility.None) 32 } 33 34 } 

#### **3.4.2 横幅广告接入示例** 

### **3.5 信息流模版广告** 

信息流列表,轮播控件,固定位置都是较为适合 

#### **3.5.1 信息流模版广告 API** 

#### **NativeExpressComponent 信息流模版广告布局** 

|**参数名**|**介绍**|
|---|---|
|adInfo|onSuccess: (ads: Array) 中获取到的广告对象。|
|adWidth|广告宽度,不传则使用屏幕宽度。|
|muted|是否静音。静音:true,不静音:false,默认静音。|
|isAutoPlay|是否自动播放。自动播放:true,不自动播放:false,默认自动 播放。|
|adStatusListener|广告状态AdStatusListener。|

#### **3.5.2 信息流模版广告接入示例** 

1 @Entry 2 @Component 3 struct NativeExpressPage 4 { 5 @State adInfo?: AdInfo = undefined 6 ... 7 8 build() { 9 if (this.adInfo) { 10 NativeExpressComponent({ 11 adInfo: adInfo, 12 adWidth: px2vp(display.getDefaultDisplaySync().width), 13 muted: false, 14 isAutoPlay: true, 15 adStatusListener: { 16 onStatusChanged: (status: string, ad: AdInfo, data: string) => { 17 switch (status) { 18 case AdStatus.AD_SHOW: 19 // 广告曝光 20 break 21 case AdStatus.AD_CLICK: 22 // 广告点击 23 break 

24 case AdStatus.AD_CLOSE: 25 // 广告关闭 26 break 27 case AdStatus.AD_RENDER_FAILED: 28 // 广告渲染失败 29 break 30 } 31 } 32 } 33 }) 34 } 35 } 36 37 } 

### **3.6 插屏广告示例** 

插屏广告是移动广告的一种常见形式,在应用流程中弹出,当应用展示插屏广告时,用户 可以选择点击广告,也可以将其关闭并返回应用。 

#### **3.6.1 插屏广告主要 API** 

#### **Tianmu.AdLoader 广告加载器** 

**方法名 入参** 

**入参 介绍** 插屏、激励视频广告展示方 法。参数说明: uiContext: UIContext, uiContext: uiContext上下 adInfo: AdInfo, 文对象; adDisplayOptions: adInfo: 广告对象; AdDisplayOptions, adDisplayOptions:展示参 adStatusListener: 数 AdStatusListener adStatusListener:广告状 态 

showAd( uiContext: UIContext, adInfo: AdInfo, adDisplayOptions: AdDisplayOptions, adStatusListener: AdStatusListener ) 

#### **3.6.2 插屏广告接入示例** 

1 @Entry 2 @Component 3 struct InterstitialPage 4 { private adLoader?: Tianmu.AdLoader 

5 private adInfo?: AdInfo 6 private adDisplayOptions: AdDisplayOptions = { 7 muted: false, 8 } 9 ... 10 11 build() { 12 ... 13 } 14 15 showAd() { 16 if (this.adInfo === undefined || this.adInfo === null) { 17 promptAction.showToast({ 18 message: '没有广告填充', 19 duration: 2000 20 }); 21 return 22 } 23 if (this.adLoader === undefined) { 24 return 25 } 26 27 const adStatusListener: AdStatusListener = { 28 onStatusChanged: (status: string, ad: AdInfo, data: string) => { 29 switch (status) { 30 case AdStatus.AD_SHOW: 31 console.log(TAG, 'onAdShow') 32 break 33 case AdStatus.AD_CLICK: 34 console.log(TAG, 'onAdClick') 35 break 36 case AdStatus.AD_REWARD: 37 console.log(TAG, 'onAdReward') 38 break 39 case AdStatus.AD_CLOSE: 40 console.log(TAG, 'onAdClose') 41 this.hideAd() 42 break 43 case AdStatus.AD_RENDER_FAILED: 44 console.log(TAG, 'onAdRenderFailed msg :: ' + data) 45 this.hideAd() 46 break 47 } 48 } 49 } 50 this.adLoader.showAd(this.getUIContext(), this.adInfo, this.adDisplayOptions, adStatusListener) 51 } 52 53 } 54 

### **3.7 激励视频广告示例** 

将短视频融入到APP场景当中,用户观看短视频广告后可以给予一些应用内奖励。 

#### **3.7.1 激励视频广告主要 API** 

#### **Tianmu.AdLoader 广告加载器** 

**方法名 入参 介绍** 插屏、激励视频广告展示方 showAd( 法。参数说明: uiContext: UIContext, uiContext: UIContext, uiContext: uiContext上下 adInfo: AdInfo, adInfo: AdInfo, 文对象; adDisplayOptions: adDisplayOptions: adInfo: 广告对象; AdDisplayOptions, AdDisplayOptions, adDisplayOptions:展示参 adStatusListener: adStatusListener: 数 AdStatusListener AdStatusListener adStatusListener:广告状 ) 态 

#### **3.7.2 激励视频广告接入示例** 

1 @Entry 2 @Component 3 struct RewardPage 4 { 5 private adInfo?: AdInfo 6 private adLoader?: Tianmu.AdLoader 7 private adDisplayOptions: AdDisplayOptions = { 8 muted: false 9 } 10 ... 11 12 build() { 13 ... 14 } 15 16 showAd() { 17 if (this.adInfo === undefined || this.adInfo === null) { 18 promptAction.showToast({ 19 message: '没有广告填充', 20 duration: 2000 21 }); 22 return 

23 } 24 if (this.adLoader === undefined) { 25 return 26 } 27 28 const adStatusListener: AdStatusListener = { 29 onStatusChanged: (status: string, ad: AdInfo, data: string) => { 30 switch (status) { 31 case AdStatus.AD_SHOW: 32 console.log(TAG, 'onAdShow') 33 break 34 case AdStatus.AD_CLICK: 35 console.log(TAG, 'onAdClick') 36 break 37 case AdStatus.AD_REWARD: 38 console.log(TAG, 'onAdReward') 39 break 40 case AdStatus.AD_CLOSE: 41 console.log(TAG, 'onAdClose') 42 this.hideAd() 43 break 44 case AdStatus.AD_RENDER_FAILED: 45 console.log(TAG, 'onAdRenderFailed msg :: ' + data) 46 this.hideAd() 47 break 48 } 49 } 50 } 51 this.adLoader.showAd(this.getUIContext(), this.adInfo, this.adDisplayOptions, adStatusListener) 52 } 53 54 } 

### **3.8 广告状态主要 API** 

#### **AdStatusListener 广告状态监听** 

|**方法名**|**入参**|**介绍**|
|---|---|---|
|onStatusChanged( status: string, ad: AdInfo, data: string )|status: string, ad: AdInfo, data: string|广告状态回调。参数说明: status(回调状态AdStatus)、 ad(广告对象)、 data(其它参数)|

#### **AdStatus 广告状态事件** 

|**参数名**|**介绍**|
|---|---|
|AD_SHOW|广告曝光回调。|
|AD_CLICK|广告点击回调。|
|AD_SKIP|广告跳过回调。在此处不要对广告进行关闭操作。|
|AD_CLOSE|广告关闭回到。在此处移除广告。|
|AD_REWARD|广告激励回调。|
|AD_RENDER_FAILED|广告渲染失败回调。|

## **4.错误码介绍** 

|**错误码**|**介绍**|
|---|---|
|-1000|初始化异常。|
|-1007|初始化接口KEY为空。|
|-2012|获取广告时发生未知异常。|
|-2013|PosId不能为空。|
|-2014|初始化数据为空,可能是没有本地缓存的初始化数据并且初始接口请求失 败。|
|-2016|没有找到当前PosId的配置信息。|
|-2018|该PosId对应的广告类型不匹配。|
|-2110|返回的广告数据为空。|
|-2111|返回的广告数据为空。|

## **5.备注** 

具体的接入代码和流程,请参考Demo 

## **6.商务合作** 

邮箱 : yuxingcao@admobile.top
