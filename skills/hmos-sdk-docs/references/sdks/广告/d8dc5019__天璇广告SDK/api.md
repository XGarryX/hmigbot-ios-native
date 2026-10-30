# **SDK接口文档** 

## **初始化模块相关接口** 

### **UBiXInitManager** 

#### **获取SDK版本号以及初始化接口** 

getVersion(): string 

获取版本号 返回值: 

|**类型**|**说明**|
|---|---|
|string|获取当前SDK版本|

getInstance():UBiXInitManager 返回值: 

|**类型**|**说明**|
|---|---|
|InitManager|获取单例对象|

### **InitManager** 

#### **主动初始化接口** 

init(context: Context, appId: string, initBuilder: UBiXInitBuilder | null): void 

初始化 

参数: 

|**参数名**|**类型**|**说明**|
|---|---|---|
|context|Context|获取当前上下文对象|
|appId|string|该App所申请的应用ID|
|initBuilder|UBiXInitBuilder|初始化设置对象,用于设置隐私相关参数|

No. 1 / 27 

### **UBiXInitBuilder** 

#### **初始化设置隐私相关参数对象** 

personalizedState(value: boolean):void 

是否限制个性化广告开关 

参数: 

|**参数名**|**类型**|**说明**|
|---|---|---|
|value|boolean|是否限制个性化广告开关,默认false允许(可选)|

personalizedState():boolean 

获取当前个性化开关状态 

返回值: 

|**类型**|**说明**|
|---|---|
|boolean|获取当前个性化开关状态 (可选)|

programRecommendsState(value: boolean) 

是否限制程序化广告开关 

参数: 

|**参数名**|**类型**|**说明**|
|---|---|---|
|value|boolean|是否限制程序化广告开关,默认false允许 (可选)|

programRecommendsState(): boolean 

获取当前程序化开关状态 

返回值: 

|**类型**|**说明**|
|---|---|
|boolean|获取当前程序化开关状态(可选)|

userOAID(value: string) 传入设备OAID 参数: 

No. 2 / 27 

|**参数名**|**类型**|**说明**|
|---|---|---|
|value|boolean|传入设备的OAID(可选)|

userOAID(): string 

##### 获取传入的OAID 

返回值: 

|**类型**|**说明**|
|---|---|
|string|获取传入的OAID(可选)|

##### userId(value: string) 

##### 传入用户ID 

参数: 

|**参数名**|**类型**|**说明**|
|---|---|---|
|value|boolean|传入用户ID(可选)|

userId(): string 

##### 获取传入的用户ID 

##### 返回值: 

|**类型**|**说明**|
|---|---|
|string|获取传入的用户ID(可选)|

location(value: UBiXLocation | null) 传入设备经纬度 参数: 

|**参数名**|**类型**|**说明**|
|---|---|---|
|value|UBiXLocation、null|传入设备当前经纬度(可选)|

location(): UBiXLocation | null 

##### 获取传入的设备经纬度 

返回值: 

|**类型**|**说明**|
|---|---|
|UBiXLocation、null|获取传入的设备经纬度 (可选)|

No. 3 / 27 

##### canUseOAID(value: boolean) 

##### 设置是否可以获取OAID 

##### 参数: 

|**参数名**|**类型**|**说明**|
|---|---|---|
|value|boolean|设置是否可以获取OAID,默认true允许(可选)|

canUseOAID(): boolean 

##### 获取传入是否允许获取OAID的状态 

##### 返回值: 

|**类型**|**说明**|
|---|---|
|boolean|获取传入是否允许获取OAID的状态(可选)|

gender(value: number) 传入用户性别(可选) 参数: 

|**参数名**|**类型**|**说明**|
|---|---|---|
|value|number|传入用户性别0未知,1男 ,2女(可选)|

gender(): number 

##### 获取传入的性别 

返回值: 

|**类型**|**说明**|
|---|---|
|number|获取传入的性别(可选)|

age(value: number) 传入用户年龄 参数: 

|**参数名**|**类型**|**说明**|
|---|---|---|
|value|number|传入用户年龄(可选)|

age(): number 

获取传入的年龄 

返回值: 

No. 4 / 27 

|**类型**|**说明**|
|---|---|
|number|获取传入的年龄(可选)|

### **UBiXLocation** 

#### **经纬度封装类** 

constructor(longitude: number, latitude: number) 构造方法传入经纬度 参数: 

|**参数名**|**类型**|**说明**|
|---|---|---|
|longitude|number|经度|
|latitude|number|纬度|

##### **初始化相关代码示例** 

//获取SDK版本 UBiXInitManager.getVersion() //设置初始化参数 

let builder: UBiXInitBuilder = new UBiXInitBuilder(); 

builder.personalizedState = true builder.programRecommendsState = true builder.userOAID = "YOUR_OAID" builder.location = new UBiXLocation(0, 0) builder.userId = "USER_ID" builder.gender = 1 builder.age = 18 //初始化 

UBiXInitManager.getInstance().init(context, "YOUR_APP_ID", builder); 

## **广告模板相关接口** 

### **开屏** 

### **UBiXSplashAdManager** 

No. 5 / 27 

#### **创建开屏广告请求接口** 

constructor(posId: string, listener: UBiXSplashAdListener) 初始化请求广告参数 

参数: 

|**参数名**|**类型**|**说明**|
|---|---|---|
|posId|string|申请的广告位ID|
|listener|UBiXSplashAdListener|开屏回调接口|

返回值: 

|**类型**|**说明**|
|---|---|
|UBiXSplashAdManager|开屏广告对象|

loadAd():void 开始请求广告 

### **UBiXSplashAdListener** 

#### **开屏广告响应接口** 

onAdLoadASuccess: (ad: UBiXAd) => void 参数: 

|**参数名**|**类型**|**说明**|
|---|---|---|
|ad|UBiXAd|响应的广告结构体|

onAdLoadFailed: (error: UBiXError | null) => void 

参数: 

|**参数名**|**类型**|**说明**|
|---|---|---|
|error|UBiXError|响应的错误码|

### **SplashView** 

#### **开屏广告布局** 

SplashView({ ad: this.ad, listener: this.interactionListener }) 展示开屏广告 

参数: 

No. 6 / 27 

|**参数名**|**类型**|**说明**|
|---|---|---|
|ad|UBiXAd|响应的广告结构体|
|listener|UBiXSplashAdInteractionListener|广告交互监听接口|

### **UBiXSplashAdInteractionListener** 

#### **开屏广告交互接口** 

onAdExposed: () => void 广告曝光时回调 

onAdClicked: () => void 广告点击时回调 

onAdClosed: () => void 广告关闭被点击时回调 

##### **开屏相关代码示例** 

##### //设置监听接口 

```arkts
adListener: UBiXSplashAdListener = { onAdLoadASuccess: (ad: UBiXAd): void => { console.log(SplashPage.name, "onAdLoadASuccess") this.ad = ad console.log("price", this.ad.getPrice() + "") console.log("type", this.ad.getAdType() + "") console.log("isVideo", this.ad.isVideoAd() + "") }, onAdLoadFailed: (error: UBiXError | null): void => { console.log(SplashPage.name, "onAdLoadFailed") } } interactionListener: UBiXSplashAdInteractionListener = { onAdExposed: (): void => { console.log(SplashPage.name, "onAdExposed") }, onAdClicked: (): void => { console.log(SplashPage.name, "onAdClicked") }, onAdClosed: (): void => { console.log(SplashPage.name, "onAdClosed") router.back() } } //请求广告 
```

UBiXSplashAdManager splashManager = new UBiXSplashAdManager(Constants.splash_ad, this.adListener) 

splashManager.loadAd() 

No. 7 / 27 

//广告展示 build() { Column() { RelativeContainer() { if (null != this.ad) { SplashView({ ad: this.ad, listener: this.interactionListener }) } }.width("100%").height("80%").id("Splash_Container") Column() { Text("LOGO").width("100%").textAlign(TextAlign.Center) }.height("20%").backgroundColor("#ff0000").id("Logo") 

}.height("100%") 

} 

### **插屏** 

### **UBiXInterstitialAdManager** 

#### **创建插屏广告请求接口** 

constructor(posId: string, listener: UBiXInterstitialAdListener) 初始化请求广告参数 

参数: 

|**参数名**|**类型**|**说明**|
|---|---|---|
|posId|string|申请的广告位ID|
|listener|UBiXInterstitialAdListener|开屏回调接口|

返回值: 

|**类型**|**说明**|
|---|---|
|UBiXInterstitialAdManager|插屏对象|

loadAd():void 开始请求广告 

show(context: UIContext) void 开始展示 参数: 

No. 8 / 27 

|**参数名**|**类型**|**说明**|
|---|---|---|
|context|UIContext|当前界面的UIContext,用于展示广告|

### **UBiXInterstitialAdListener** 

#### **插屏广告响应交互接口** 

onAdLoadASuccess: (ad: UBiXAd) => void 参数: 

|**参数名**|**类型**|**说明**|
|---|---|---|
|ad|UBiXAd|响应的广告结构体|

onAdLoadFailed: (error: UBiXError | null) => void 参数: 

|**参数名**|**类型**|**说明**|
|---|---|---|
|error|UBiXError|响应的错误码|

onAdExposed: () => void 广告曝光时回调 

onAdClicked: () => void 广告点击时回调 

onAdClosed: () => void 广告关闭时回调 

##### **插屏相关代码示例** 

##### //设置监听接口 

```arkts
adListener: UBiXInterstitialAdListener = { onAdLoadASuccess: (ad: UBiXAd): void => { console.log(InterstitialPage.name, "onAdLoadASuccess") }, onAdLoadFailed: (error: UBiXError | null): void => { console.log(InterstitialPage.name, "onAdLoadFailed " + error?.getErrorMessage()) }, onAdExposed: (): void => { console.log(InterstitialPage.name, "onAdExposed") }, onAdClicked: (): void => { console.log(InterstitialPage.name, "onAdClicked") }, onAdClosed: (): void => { console.log(InterstitialPage.name, "onAdClosed") 
```

No. 9 / 27 

} 

} 

//请求广告 

interstitialManager = new UBiXInterstitialAdManager(Constants.interstitial_ad, this.adListener) 

interstitialManager.loadAd() 

//广告展示 interstitialManager?.show(this.getUIContext()) 

### **激励视频** 

### **UBiXRewardVideoAdManager** 

#### **创建激励视频广告请求接口** 

constructor(posId: string, listener: UBiXRewardVideoAdListener) 初始化请求广告参数 

参数: 

|**参数名**|**类型**|**说明**|
|---|---|---|
|posId|string|申请的广告位ID|
|listener|UBiXRewardVideoAdListener|激励视频回调接口|

返回值: 

|**类型**|**说明**|
|---|---|
|UBiXRewardVideoAdManager|激励视频对象|

loadAd():void 开始请求广告 show():void 开始展示广告 

### **UBiXRewardVideoAdListener** 

#### **激励视频响应交互接口** 

onAdLoadASuccess: (ad: UBiXAd) => void 参数: 

No. 10 / 27 

|**参数名**|**类型**|**说明**|
|---|---|---|
|ad|UBiXAd|响应的广告结构体|

onAdLoadFailed: (error: UBiXError | null) => void 参数: 

|**参数名**|**类型**|**说明**|
|---|---|---|
|error|UBiXError|响应的错误码|

onAdExposed: () => void 广告曝光时回调 

onAdExposeFailed: () => void 广告曝光失败时回调 

onAdClicked: () => void 广告点击时回调 

onAdClosed: () => void 广告关闭时回调 onAdRewarded: () => void 广告获得奖励时回调 

onAdPlayStarted: () => void 广告播放开始时回调 

onAdPlayCompleted: () => void 广告播放结束时回调 

##### **激励视频相关代码示例** 

##### //设置监听接口 

```arkts
adListener: UBiXRewardVideoAdListener = { onAdLoadASuccess: (ad: UBiXAd): void => { console.log(RewardVideoPage.name, "onAdLoadASuccess") }, onAdLoadFailed: (error: UBiXError | null): void => { console.log(RewardVideoPage.name, "onAdLoadFailed") }, onAdExposed: (): void => { console.log(RewardVideoPage.name, "onAdExposed") }, onAdClicked: (): void => { console.log(RewardVideoPage.name, "onAdClicked") }, onAdClosed: (): void => { console.log(RewardVideoPage.name, "onAdClosed") router.back(); 
```

No. 11 / 27 

    },
onAdExposeFailed: (): void => {
console.log(RewardVideoPage.name, "onAdExposeFailed")
    },
onAdRewarded: (): void => {
console.log(RewardVideoPage.name, "onAdRewarded")
    },
onAdPlayStarted: (): void => {
console.log(RewardVideoPage.name, "onAdPlayStarted")
    },
onAdPlayCompleted: (): void => {
console.log(RewardVideoPage.name, "onAdPlayCompleted")
    }
  }
//请求广告
rewardVideoManager = new UBiXRewardVideoAdManager(Constants.rewardVideo_ad,
this.adListener)
rewardVideoManager.loadAd()
//广告展示
rewardVideoManager?.show()

### **横幅** 

### **UBiXBannerAdManager** 

#### **创建横幅广告请求接口** 

constructor(posId: string, listener: UBiXBannerAdListener) 初始化请求广告参数 

参数: 

|**参数名**|**类型**|**说明**|
|---|---|---|
|posId|string|申请的广告位ID|
|listener|UBiXBannerAdListener|激励视频回调接口|
|返回值:|||

|**类型**|**说明**|
|---|---|
|UBiXBannerAdManager|激励视频对象|

loadAd():void 开始请求广告 

No. 12 / 27 

### **UBiXBannerAdListener** 

#### **横幅广告响应接口** 

onAdLoadASuccess: (ad: UBiXAd) => void 参数: 

|**参数名**|**类型**|**说明**|
|---|---|---|
|ad|UBiXAd|响应的广告结构体|

onAdLoadFailed: (error: UBiXError | null) => void 

参数: 

|**参数名**|**类型**|**说明**|
|---|---|---|
|error|UBiXError|响应的错误码|

### **BannerView** 

#### **横幅广告布局** 

BannerView({ ad: this.ad, listener: this.adInteractionListener }) 展示横幅广告 

参数: 

|**参数名**|**类型**|**说明**|
|---|---|---|
|ad|UBiXAd|响应的广告结构体|
|listener|UBiXBannerInteractionListener|广告交互监听接口|

### **UBiXBannerInteractionListener** 

#### **横幅广告交互接口** 

onAdExposed: () => void 广告曝光时回调 

onAdClicked: () => void 广告点击时回调 

onAdClosed: () => void 

广告关闭被点击时回调(需要手动移除) 

No. 13 / 27 

**横幅相关代码示例** 

//设置监听接口 adListener: UBiXBannerAdListener = { onAdLoadASuccess: (ad: UBiXAd): void => { console.log(BannerPage.name, "onAdLoadASuccess") this.ad = ad }, onAdLoadFailed: (error: UBiXError | null): void => { console.log(BannerPage.name, "onAdLoadFailed " + error?.getErrorMessage()) } } adInteractionListener: UBiXBannerInteractionListener = { onAdExposed: (): void => { console.log(BannerPage.name, "onAdExposed") }, onAdClicked: (): void => { console.log(BannerPage.name, "onAdClicked") }, onAdClosed: (): void => { console.log(BannerPage.name, "onAdClosed") } } //请求广告 bannerManager = new UBiXBannerAdManager(Constants.banner_ad, this.adListener) bannerManager.loadAd() 

//广告展示 build() { Column() { if (null != this.ad) { BannerView({ ad: this.ad, listener: this.adInteractionListener }) } }.height("100%") } 

### **UBiXNativeExpressManager** 

#### **创建原生模板广告请求接口** 

constructor(posId: string, listener: UBiXNativeExpressAdListener) 初始化请求广告参数 

参数: 

No. 14 / 27 

|**参数名**|**类型**|**说明**|
|---|---|---|
|posId|string|申请的广告位ID|
|listener|UBiXNativeExpressAdListener|原生模板回调接口|

返回值: 

|**类型**|**说明**|
|---|---|
|UBiXNativeExpressManager|开屏广告对象|

loadAd():void 开始请求广告 

### **UBiXNativeExpressAdListener** 

#### **原生模板广告响应接口** 

onAdLoadASuccess: (ad: UBiXAd) => void 参数: 

|**参数名**|**类型**|**说明**|
|---|---|---|
|ad|UBiXAd|响应的广告结构体|

onAdLoadFailed: (error: UBiXError | null) => void 参数: 

|**参数名**|**类型**|**说明**|
|---|---|---|
|error|UBiXError、null|响应的错误码|

### **NativeExpressView** 

#### **原生模板广告布局** 

NativeExpressView({ ad: item, listener: this.expressInteractionListener }) 原生模板广告 

参数: 

|**参数名**|**类型**|**说明**|
|---|---|---|
|ad|UBiXAd|响应的广告结构体|
|listener|UBiXNativeExpressInteractionListener|广告交互监听接口|

No. 15 / 27 

### **UBiXNativeExpressInteractionListener** 

#### **原生模板广告交互接口** 

onAdRendered: () => void 广告渲染成功时回调 

onAdRenderFailed: () => void 广告渲染失败时回调 

onAdExposed: () => void 广告曝光时回调 onAdClicked: () => void 广告点击时回调 onAdClosed: () => void 广告关闭被点击时回调(需要手动移除) 

##### **原生模板相关代码示例** 

//设置监听接口 expressListener: UBiXNativeExpressAdListener = { onAdLoadASuccess: (bean: UBiXAd): void => { console.log(NativeExpressPage.name, "onAdLoadASuccess") this.arr.pushData(bean) }, onAdLoadFailed: (error: UBiXError | null): void => { console.log(NativeExpressPage.name, "onAdLoadFailed " + error?.getErrorMessage()) } } expressInteractionListener: UBiXNativeExpressInteractionListener = { onAdRendered: (): void => { console.log(NativeExpressPage.name, "onAdRendered") }, onAdRenderFailed: (): void => { console.log(NativeExpressPage.name, "onAdRenderFailed") }, onAdExposed: (): void => { console.log(NativeExpressPage.name, "onAdExposed") }, onAdClicked: (): void => { console.log(NativeExpressPage.name, "onAdClicked") }, onAdClosed: (): void => { console.log(NativeExpressPage.name, "onAdClosed") } } //请求广告 

No. 16 / 27 

nativeExpressAd = new UBiXNativeExpressManager(Constants.native_ad_stxw, this.expressListener) 

nativeExpressAd.loadAd() 

//广告展示 build() { Column() { if (null != this.ad) { NativeExpressView({ ad: item, listener: this.expressInteractionListener }) } }.height("100%") } 

### **UBiXNativeManager** 

#### **创建原生自渲染广告请求接口** 

constructor(posId: string, listener: UBiXNativeAdListener) 初始化请求广告参数 

参数: 

|**参数名**|**类型**||**说明**|
|---|---|---|---|
|posId|string||申请的广告位ID|
|listener|UBiXNativeAdListener||原生回调接口|
|返回值:||||
|**类型**||**说明**||
|UBiXNativeManager||开屏广|告对象|

loadAd():void 开始请求广告 

### **UBiXNativeAdListener** 

#### **原生自渲染广告响应接口** 

onAdLoadASuccess: (bean: UBiXNativeAd[]) => void 参数: 

|**参数名**|**类型**|**说明**|
|---|---|---|
|bean|UBiXNativeAd[]|响应的广告结构体|

No. 17 / 27 

onAdLoadFailed: (error: UBiXError | null) => void 

参数: 

|**参数名**|**类型**|**说明**|
|---|---|---|
|error|UBiXError|响应的错误码|

### **UBiXNativeAdListener** 

#### **原生自渲染广告响应接口** 

register(clickView: (FrameNode | null)[], closeView: FrameNode | null, interactionListener: UBiXNativeInteractionListener): void 参数: 

|**参数名**|**类型**|**说明**|
|---|---|---|
|clickView|FrameNode、null|可点击的FrameNode队列|
|closeView|FrameNode、null|用于处理关闭的FrameNode|
|interactionListener|UBiXNativeInteractionListener|触发交互时的监听接口|

getPrice(): number | Long | null | undefined 获取当前广告价格 

返回值: 

|**类型**|**说明**|
|---|---|
|number、Long、null、undefined|获取当前广告ecpm|
|getTitle(): string | null | undefined 获取当前广告标题 返回值:||

|**类型**|**说明**|
|---|---|
|number、null、undefined|获取当前广告标题|

getDesc(): string | null | undefined 获取当前广告描述 返回值: 

|**类型**|**说明**|
|---|---|
|number、null、undefined|获取当前广告描述|

No. 18 / 27 

getImageList(): UBiXNativeImage[] 获取当前图片素材列表 返回值: 

|**类型**|**说明**|
|---|---|
|UBiXNativeImage[]|获取当前图片素材列表|
|getVideo(): UBiXNativeVideo | null 获取当前视频素材 返回值:||
|**类型**|**说明**|
|UBiXNativeVideo、null|获取当前视频素材|
|getAdType(): number | null | undefined 获取当前广告类型 返回值:||
|**类型**|**说明**|
|number、null、undefined|获取当前广告类型|
|isVideoAd(): boolean | null | undefined 获取当前广告是否为视频广告 返回值:||
|**类型**|**说明**|
|boolean、null、undefined|获取当前广告是否为视频广告|
|getRewardStatus(): boolean 获取当前广告是否获得奖励 返回值:||

|**类型说明**||
|---|---|
|boolean 获取当前广告是否获得奖励||
|getDownloadInfo(): UBiXNativeDownloadInfo | null 获取当前素材的下载信息 返回值:||
|**类型**|**说明**|
|UBiXNativeDownloadInfo、null|获取当前素材的下载信息|

No. 19 / 27 

getExtra(key: string): string | number | boolean | HashMap<string, string> | undefined | null 获取当前广告的附加信息 

参数: 

|**参数名**|**类型**|**说明**|
|---|---|---|
|key|string|附加值的key值(暂无可用信息)|

返回值: 

|**类型**|**说明**|
|---|---|
|string、number、boolean、HashMap<string, string>、undefined、|获取当前广告的附加信|
|null|息|

### **UBiXNativeImage** 

#### **图片资源结构体** 

getUrl(): string | null 获取图片地址 

返回值: 

|**类型**|**说明**|
|---|---|
|string null|图片地址|

getWidth(): number 获取图片宽 返回值: 

|**类型**|**说明**|
|---|---|
|number|图片宽|

getHeight(): number 获取图片高 

返回值: 

|**类型**|**说明**|
|---|---|
|number|图片高|

No. 20 / 27 

### **UBiXNativeVideo** 

#### **视频资源结构体** 

getUrl(): string | null 获取视频地址 

返回值: 

|**类型**|**说明**|
|---|---|
|string null|视频地址|
|getWidth(): number 获取视频宽||
|返回值:||

|**类型**|**说明**|
|---|---|
|number|视频宽|
|getHeight(): number 获取视频高||
|返回值:||

|**类型**|**说明**|
|---|---|
|number|视频高|

getDuration(): number 获取视频时长 

返回值: 

|**类型**|**说明**|
|---|---|
|number|视频市场|

### **UBiXNativeDownloadInfo** 

#### **下载信息结构体** 

getDownloadAppName(): string | null | undefined 获取被下载应用名称 

返回值: 

No. 21 / 27 

|**类型**|**说明**|
|---|---|
|string、null、undefined|被下载应用名称|

getDownloadBundleName(): string | null | undefined 获取被下载应用包名 

返回值: 

|**类型**|**说明**|
|---|---|
|string、null、undefined|被下载应用包名|

getDownloadAppVersion(): string | null | undefined 获取被下载应用版本 

返回值: 

|**类型**|**说明**|
|---|---|
|string、null、undefined|被下载应用版本|

getDownloadAppPublisher(): string | null | undefined 获取被下载应用开发商 

返回值: 

|**类型**|**说明**|
|---|---|
|string、null、undefined|被下载应用开发商|

getDownloadAppIntroUrl(): string | null | undefined 获取被下载应用介绍地址 

返回值: 

|**类型**|**说明**|
|---|---|
|string、null、undefined|被下载应用介绍地址|

getDownloadAppPrivacyUrl(): string | null | undefined 获取被下载应用隐私地址 

返回值: 

|**类型**|**说明**|
|---|---|
|string、null、undefined|被下载应用隐私地址|

No. 22 / 27 

getDownloadAppPermissionUrl(): string | null | undefined 获取被下载应用权限地址 

返回值: 

|**类型**|**说明**|
|---|---|
|string、null、undefined|被下载应用权限地址|

getDownloadAppICPNumber(): string | null | undefined 获取被下载应用ICP 

返回值: 

|**类型**|**说明**|
|---|---|
|string、null、undefined|被下载应用ICP|
|getDownloadAppSuitableAge(): string | null | undefined 获取被下载应用适用年龄||

|返回值:||
|---|---|
|**类型**|**说明**|
|string、null、undefined|被下载应用适用年龄|

getDownloadAppIconUrl(): string | null | undefined 获取被下载应用图标地址 

返回值: 

|**类型**|**说明**|
|---|---|
|string、null、undefined|被下载应用图标地址|

### **UBiXNativeInteractionListener** 

#### **原生广告响应交互接口** 

onAdExposed: () => void 广告曝光时回调 

onAdClicked: () => void 广告点击时回调 

onAdClosed: () => void 广告关闭时回调 

No. 23 / 27 

##### **原生自渲染相关代码示例** 

##### //设置监听接口 

```arkts
expressListener: UBiXNativeExpressAdListener = { onAdLoadASuccess: (bean: UBiXAd): void => { console.log(NativeExpressPage.name, "onAdLoadASuccess") this.arr.pushData(bean) }, onAdLoadFailed: (error: UBiXError | null): void => { console.log(NativeExpressPage.name, "onAdLoadFailed " + error?.getErrorMessage()) } } expressInteractionListener: UBiXNativeExpressInteractionListener = { onAdRendered: (): void => { console.log(NativeExpressPage.name, "onAdRendered") }, onAdRenderFailed: (): void => { console.log(NativeExpressPage.name, "onAdRenderFailed") }, onAdExposed: (): void => { console.log(NativeExpressPage.name, "onAdExposed") }, onAdClicked: (): void => { console.log(NativeExpressPage.name, "onAdClicked") }, onAdClosed: (): void => { console.log(NativeExpressPage.name, "onAdClosed") } } 
```

##### //请求广告 

nativeExpressAd = new UBiXNativeManager(Constants.native_ad_zxr, this.expressListener) nativeExpressAd.loadAd() 

//广告展示 build() { Column({}) { Column() { //获取标题 Text(item?.getTitle()).id(this.native_template_title) //获取图片 Image(item.getImageList()[0].getUrl()).aspectRatio(16 / 9).id(this.native_template_single_image) //是否视频广告 item.isVideo(); //获取视频 item.getVideo(); //更多get内容请参考文档 //展示关闭按钮 " " Text( 关闭 ).id(this.native_template_close) 

No. 24 / 27 

}.padding(8).onVisibleAreaChange([0.0, 1.0], (isVisible: boolean, currentRatio: number) => { let clickViews = 

[this.getUIContext().getAttachedFrameNodeById(this.native_template_single_image) as FrameNode, 

this.getUIContext().getAttachedFrameNodeById(this.native_template_title) as
FrameNode]
let closeView =
this.getUIContext().getAttachedFrameNodeById(this.native_template_close) as FrameNode
//注册自定义广告布局监听
item.register(clickViews, closeView, {
onAdExposed: (): void => {
console.log(NativePage.name, "onAdExposed")
          },
onAdClicked: (): void => {
console.log(NativePage.name, "onAdClicked")
          },
onAdClosed: (): void => {
console.log(NativePage.name, "onAdClosed")
          }
        })
this.native_template_single_image = util.generateRandomUUID(true)
this.native_template_title = util.generateRandomUUID(true)
this.native_template_close = util.generateRandomUUID(true)
      })
    }.width('100%').width('100%').alignItems(HorizontalAlign.Start)
  }
}

### **通用接口** 

### **UBiXAd** 

#### **广告结构体接口** 

getPrice(): number | Long | null | undefined 返回广告价格 返回值: 

|**类型**|**说明**|
|---|---|
|number、Long、null、undefined|广告价格|
|getAdType(): number | null | undefined 返回广告类型 返回值:||

No. 25 / 27 

|**类型**|**说明**|
|---|---|
|number、null、undefined|广告类型|

isVideoAd(): boolean | null | undefined 返回是否为视频广告 返回值: 

|**类型**|**说明**|
|---|---|
|boolean、null、undefined|是否为视频广告|

isValid(): boolean 返回广告是否有效 返回值: 

|**类型**|**说明**|
|---|---|
|boolean|广告是否有效|

### **UBiXError** 

#### **错误码接口** 

getErrorCode(): number 返回错误码 返回值: 

|**类型**|**说明**|
|---|---|
|number|错误码|
|getErrorMessage(): string 返回错误信息 返回值:||

|**类型**|**说明**|
|---|---|
|string|错误信息|

|**错误码值对照表**|
|---|

No. 26 / 27 

|**码值**|**说明**|
|---|---|
|10001|APPID为空|
|10002|POSID为空|
|10003|AdSize数据错误|
|10004|未初始化|
|10005|SDK已关闭|
|10006|参数错误|
|10007|其他SDK请求/初始化错误|
|10009|adm解析异常|
|20001|请求成功,但无填充|
|20002|网络异常|
|20003|请求超时|
|30001|广告容器为空/不可见|
|30002|广告资源过期|
|30003|展示多次限制|
|30004|模版渲染失败|
|30005|视频加载出错|
|30006|视频播放中出错|
|30007|其他错误|
|40001|视频缓存失败|
|50001|曝光失败|
|50003|曝光容器不可用|
|50010|视频播放失败|
|99999|内部错误码|

No. 27 / 27
