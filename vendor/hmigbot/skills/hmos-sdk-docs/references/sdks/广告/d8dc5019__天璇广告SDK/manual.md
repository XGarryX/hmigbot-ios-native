# **UBiX SDK 接入文档** 

## **更新记录** 

|**日期**|**版本**|**更近记录**|
|---|---|---|
|2024-09-23|1.0.0|【功能】支持开屏、插屏、原生、激励视频、横幅广告样式|

No. 1 / 13 

## **一** **、Android集成说明文档** 

### **1、添加SDK到工程** 

解压UBiX_Merak.SDK_x.x.x.zip压缩包,把ubixsdk对应的har文件放到libs文件夹下 

###### **在工程oh-package.json5文件中添加依赖** 

dependencies { ubixsdk: 'file:../libs/ubixsdk.har'//引用项目的libs目录 } 

###### **module.json5 添加权限** 

"requestPermissions": [ {     //用于联网功能 "name": "ohos.permission.INTERNET", "reason": "$string:why_use_app_internet", "usedScene": { "abilities": [ "EntryAbility" ], "when": "always" } }, {   //用于获取OAID,广告投放相关 "name": "ohos.permission.APP_TRACKING_CONSENT", "reason": "$string:why_use_app_tracking_consent", "usedScene": { "abilities": [ "EntryAbility" ], "when": "always" } }, {   //用于获取当前网络状态(非必须) "name": "ohos.permission.GET_NETWORK_INFO", "reason": "$string:why_use_app_tracking_consent", "usedScene": { "abilities": [ "EntryAbility" ], "when": "always" } }] 

No. 2 / 13 

### **2、SDK初始化说明** 

#### **注意:广告请求前都要有过一次初始化** 

在启动页或者主页调用init 

//初始化全局AdSetting 

let builder: UBiXInitBuilder = new UBiXInitBuilder(); 

//初始化SDK UBiXInitManager.getInstance().init(context, Constants.app_id, builder); 

###### UBiXInitBuilder设置 

//是否可以使用OAID,如不允许使用OAID,需要通过接口传递OAID数据 builder.canUseOAID //是否可以使用定位 builder.canUseLocation //传入地理位置 builder.location(location:UBiXLocation) //传入OAID builder.userOAID(oaid:string) //false表示关闭个性化广告关,其余均表示开启个性化开 builder.personalizedState(sw:boolean) //false表示关闭程序化广告关,true表示开启个性化开 builder.setProgrammaticRecommendState(sw:boolean) //传入用户ID builder.userId(userId:string) //传入性别 builder.gender(gender:number) //传入年龄 builder.age(age:number) 

No. 3 / 13 

### **二、请求广告** 

##### **1、开屏广告** 

###### //初始化开屏广告,传入参数广告位Id,UBiXSplashAdListener 

let splashManager = new UBiXSplashAdManager(Constants.splash_ad, this.adListener) //加载广告并渲染,结果通过UBiXSplashAdListener接口回调 

splashManager.loadAd() 

###### **UBiXSplashAdListener 开屏事件监听接口类** 

|**方法**|**描述**|
|---|---|
|onAdLoadSucceed(ad: UBiXAd)|广告加载成功|
|onAdLoadFailed(error: UBiXError)|广告加载失败|

###### **展示广告** 

###### //在build()方法中构建布局 

//加载广告并渲染,ad为通过接口返回的UBiXAd,同时添加交互状态监听UBiXSplashAdInteractionListener, 用于监听广告交互 

SplashView({ ad: this.ad, listener: this.interactionListener }) 

###### **UBiXSplashAdInteractionListener 开屏事件监听接口类** 

|**方法**|**描述**|
|---|---|
|onAdExposed()|广告曝光|
|onAdClicked()|广告点击|
|onAdClosed()|广告关闭|

No. 4 / 13 

##### **2、原生模板广告** 

//初始化原生模板广告,并传入广告位Id和回调接口UBiXNativeExpressAdListener 

let nativeExpressAd: UBiXNativeExpressManager =new 

UBiXNativeExpressManager(Constants.native_ad_stxw, this.expressListener) //加载广告 

nativeExpressAd.loadAd() 

###### **UBiXNativeExpressAdListener** :原生模板请求交互接口类 

|**方法**|**描述**|
|---|---|
|onAdLoadSucceed(ad: UBiXAd)|广告加载成功|
|onAdLoadFailed(error: UBiXError)|广告加载失败|

###### **展示广告** 

###### //在build()方法中构建布局 

//ad为通过接口返回的UBiXAd,同时添加交互状态监听UBiXNativeExpressInteractionListener,用于监听广 告交互 

NativeExpressView({ ad: this.ad, listener: this.expressInteractionListener }) 

###### **UBiXNativeExpressInteractionListener** :原生模板交互回调接口类 

|**方法**|**描述**|
|---|---|
|onAdExposed()|广告展示回调|
|onAdClicked()|广告点击回调|
|onAdClosed()|广告关闭回调|
|onAdRenderSucceed()|广告渲染成功回调|
|onAdRenderFailed()|广告渲染失败回调|

No. 5 / 13 

##### **3、原生自渲染广告** 

###### //初始化原生自渲染广告,传入广告位Id和监听接口 

let nativeExpressAd: UBiXNativeManager = new UBiXNativeManager(Constants.native_ad_zxr, this.nativeAdListener) 

//加载广告 

nativeExpressAd.loadAd() 

###### **UBiXNativeAdListener** :原生自渲染请求交互接口类 

|**方法**|**描述**|
|---|---|
|onAdLoadSucceed(ads: UBiXNativeAd[])|加载广告数据模型回调|
|onAdLoadFailed(error: UBiXError)|广告加载失败|

###### **UBiXNativeAd** :原生自渲染广告体接口类 

|**变量名称**|**描述**|**类型**|
|---|---|---|
|registerViews(clickViews:FrameNode[], closeView:FrameNode, UBiXNativeInteractionListener listener);|绑定回传||
|getPrice()|广告价格,单 位:分|Long|
|getTitle()|广告标题|String|
|getDesc()|广告描述|String|
|getVideo()|创意类别|Integer|
|isVideo()|是否视频广告|String|
|getImageList()|获取图片地址 列表|UBiXNativeImage[]|
|getDownloadInfo()|获取下载合规 要素|UBiXNativeDownloadInfo|

No. 6 / 13 

###### **UBiXNativeImage** :原生自渲染图片接口类 

|**变量名称**|**描述**|
|---|---|
|getUrl()|图片地址|
|getWidth()|图片宽|
|getHeight()|图片高|

###### **UBiXNativeDownloadInfo** :下载要素接口 

|**变量名称**|**描述**|
|---|---|
|getDownloadAppName()|下载应用的名称|
|getDownloadBundleName()|下载应用的包名|
|getDownloadAppVersion()|下载应用的版本|
|getDownloadAppPublisher()|下载应用的开发商|
|getDownloadAppIntroUrl()|下载应用的介绍链接|
|getDownloadAppPrivacyUrl()|下载应用的隐私链接|
|getDownloadAppPermissionUrl()|下载应用的权限链接|
|getDownloadAppICPNumber()|下载应用的ICP编号|
|getDownloadAppSuitableAge()|下载应用的实用年龄|
|getDownloadAppIconUrl()|下载应用的图标地址|

###### **UBiXNativeInteractionListener** :原生自渲染交互回调接口类 

|**变量名称**|**描述**|
|---|---|
|onAdExposed()|广告曝光回调|
|onAdClicked()|广告点击|
|onAdClosed()|广告关闭|

###### 具体实现可参考demo代码 

No. 7 / 13 

##### **4、激励视频广告** 

//初始化激励视频广告,请求广告位Id,监听接口 

let rewardVideoManager = new UBiXRewardVideoAdManager(Constants.rewardVideo_ad, this.adListener) 

//加载激励视频广告 rewardVideoManager.loadAd() //展示广告(在广告响应成功之后) rewardVideoManager?.show() 

###### **UBiXRewardVideoAdListener 激励视频事件监听接口类** 

|**方法**|**描述**|
|---|---|
|onAdLoadASuccess(ad: UBiXAd)|广告加载成功回调|
|onAdLoadFailed(error: UBiXError)|广告加载失败回调|
|onAdExposed()|广告展示回调|
|onAdExposeFailed()|广告展示失败回调|
|onAdClicked()|广告点击回调|
|onAdPlayStarted()|视频开始播放回调|
|onAdPlayCompleted()|视频完成播放回调|
|onAdRewarded()|广告获得奖励回调|
|onAdClosed()|广告关闭回调|

No. 8 / 13 

##### **5、插屏广告** 

###### //初始化插屏广告,请求广告并传入参数 

let interstitialManager = new UBiXInterstitialAdManager(Constants.interstitial_ad, 

this.adListener) 

//加载广告 

interstitialManager.loadAd() 

//展示广告(在广告响应成功之后) 

interstitialManager?.show(this.getUIContext()) 

###### **UBiXInterstitialAdListener 插屏事件监听接口类** 

|**方法**|**描述**|
|---|---|
|onAdExposed()|广告展示回调|
|onAdExposeFailed()|广告展示失败回调|
|onAdClicked()|广告点击回调|
|onAdClosed()|广告关闭回调|
|onAdLoadSucceed(ad: UBiXAd)|广告加载成功|
|onAdLoadFailed(error: UBiXError)|广告加载失败|

No. 9 / 13 

##### **6、横幅广告** 

###### //初始化横幅广告,请求广告并传入参数 

let bannerManager = new UBiXBannerAdManager(Constants.banner_ad, this.adListener) //加载横幅广告 

bannerManager.loadAd() 

###### **UBiXBannerAdListener 插屏事件监听接口类** 

|**方法**|**描述**|
|---|---|
|onAdLoadSucceed(ad: UBiXAd)|广告加载成功|
|onAdLoadFailed(error: UBiXError)|广告加载失败|

###### **展示广告** 

###### //在build()方法中构建布局 

//ad为通过接口返回的UBiXAd,同时添加交互状态监听UBiXBannerAdListener,用于监听广告交互 BannerView({ ad: this.ad, listener: this.expressInteractionListener }) 

###### **UBiXBannerAdListener 插屏事件监听接口类** 

|**方法**|**描述**|
|---|---|
|onAdExposed()|广告展示回调|
|onAdClicked()|广告点击回调|
|onAdClosed()|广告关闭回调|

###### **UBiXAd通用广告体接口内容** 

|**方法**|**描述**|
|---|---|
|getPrice()|获取广告价格|
|getAdType()|获取广告类型|
|isVideoAd()|是否是视频广告|
|isValid()|广告是否有效|

No. 10 / 13 

#### 

### **三、错误码** 

|**错误码**|**错误原因**|
|---|---|
|10001|APPID为空|
|10002|POSID为空|
|10003|AdSize数据错误|
|10004|未初始化|
|10005|SDK已关闭|
|10006|参数错误|
|10007|其他SDK请求/初始化错误(ClassNotFound...)|
|10008|超过请求频次限制|
|10009|adm解析异常|
|20001|请求成功,但无填充|
|20002|网络异常|
|20003|请求超时|
|30001|外层/广告容器为空/不可见|
|30002|广告资源过期|
|30003|展示多次限制|
|30004|模版渲染失败|
|30005|视频加载出错|
|30006|视频播放中出错|
|30007|其他错误|
|99999|内部错误码|

No. 11 / 13 

### **四、App隐私信息** 

##### **1、说明** 

本文档将说明UBiX_Merak.SDK收集的隐私信息,及对个人信息的处理和保护策略。 

##### **2、SDK收集的信息** 

|**参数**|**说明**|
|---|---|
|操作 系统|设备的操作系统|
|系统 版本 名|设备的系统版本名|
|系统 版本 号|设备的系统版本号|
|应用 包名|当前应用的包名|
|应用 版本 名|当前应用版本名|
|设备 品牌|移动设备的品牌名称|
|设备 型号|移动设备的型号名称|
|分辨 率|设备的屏幕分辨率|
|屏幕 方向|设备的屏幕方向(如:1:竖屏,2:横屏)|
|网络 类型|网络类型(如:WiFi、3G、4G)|
|移动||
|网络|移动设备网络代码|
|代码||
|移动||
|国家 代码|移动设备国家代码|

No. 12 / 13 

|系统 语言|系统语言(如:zh-CN)|
|---|---|
|IP地 址|设备的IP地址|
|User Agent|User Agent信息|
|OAID|设备标识符|
|设备 信息|CPU型号 如ARM64E设备名称MCC移动国家代码MNC移动网络代码硬盘大小 单位字节内存大小 单位字节设备电量 百分比时区 如东八区经纬度(如果有通过位置权限)|
|UBiX_Me|rak.SDK收集的设备信息将用于以下用途|

|1)开发者可以基于设备信息,在UBiX_Merak Platform中调整广告投放策略;|
|---|

- 2) UBiX_Merak.SDK基于设备信息分析广告行为(如广告加载、展示、点击等); 

3) UBiX_Merak.SDK尊重开发者的设备信息共享选择权,如果开发者不希望其设备信息被UBiX_Merak.SDK处理,可 以联系商务同学关停数据收集权限。 

##### **3、SDK隐私协议** 

https://ubixai.com/ubix_sdk_Merak_privacy.html 

No. 13 / 13
