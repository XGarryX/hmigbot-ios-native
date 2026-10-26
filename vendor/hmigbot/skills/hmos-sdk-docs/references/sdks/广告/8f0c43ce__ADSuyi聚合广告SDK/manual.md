# **ADSuyi广告聚合 HarmonyOS Sdk——接入文 档 V1.0.0** 

## **1. 概述** 

### **1.1 概述** 

尊敬的开发者朋友,欢迎您使用ADSuyi广告聚合SDK。通过本文档,您可以快速完成广告SDK的 集成。 

### **2. 支持的广告类型** 

|**类型**|**简介**|**适用场景**|
|---|---|---|
|开屏广告|开屏广告以APP启动作为曝光时机的模板广 告,需要将开屏广告视图添加到承载的广告容 器中,提供5s可感知广告展示|APP启动界面常会使 用开屏广告|
|信息流模板广告|信息流模板广告,支持上文下图、下图上文、 左图右文、右图左文、纯图|信息流列表,轮播控 件,固定位置都是较 为适合|
|插屏广告|插屏广告是移动广告的一种常见形式,在应用 流程中弹出,当应用展示插屏广告时,用户可 以选择点击广告,访问其目标网址,也可以将 其关闭并返回应用|在应用执行流程的自 然停顿点,适合投放 这类广告|
|激励视频广告|将短视频融入到APP场景当中,用户观看短视 频广告后可以给予一些应用内奖励|常出现在游戏的复 活、任务等位置,或 者网服类APP的一些 增值服务场景|

## **3. 安装命令** 

1 2 // ADSuyi广告聚合sdk 3 ohpm install @admobile/adsuyi 4 // 天目广告 5 ohpm install @admobile/tianmu 

6 

## **4. SDK版本说明** 

## **5. SDK接入流程** 

### **5.1 添加SDK到工程中** 

接入环境: **DevEco Studio** , **Ohos_sdk_public 5.0.0.102** 

### **5.3 权限申请** 

|**权限名称**|**权限说明**|**使用目的**|
|---|---|---|
|ohos.permission.INTERNET|允许使用Internet 网络|允许使用Internet 网络|
|ohos.permission.GET_NETWORK_INFO|允许应用获取数据 网络信息|允许应用获取数据 网络信息|
|ohos.permission.APP_TRACKING_CONSENT|允许应用读取开放 匿名设备标识符|允许应用读取开放 匿名设备标识符|
|ohos.permission.APPROXIMATELY_LOCATION|允许应用获取设备 模糊位置信息|允许应用获取设备 模糊位置信息|

### **5.4 兼容配置** 

#### **5.4.1 混淆配置** 

如果打包时开启了混淆配置,请按需添加以下混淆内容,并保证广告资源文件不被混淆 

### **5.5 隐私信息控制开关** 

1 

### **5.6 设备标识** 

#### **5.6.1 OAID支持** 

1 // 传入获取到的OAID 2 ADSuyi.SDK.setOaid(oaid) 

## **6. 示例代码** 

### **6.1 SDK初始化** 

在适当位置进行SDK的初始化 

#### **6.1.1 初始化主要 API** 

#### **ADSuyi** 

ADSuyi.Sdk 

|**方法名**|**介绍**|
|---|---|
|setDebug(isDebug: boolean)|设置是否是Debug模式。参数说明:debug(true:开启,false: 关闭, 默认:false)开发阶段以及提交测试阶段可设置为true, 方便异常排查。|
|setInitListener(listener: ADSSPInitListener)|初始化状态回调。|
|init(context: Context, appid: string)|初始化方法。参数说明:context(初始化SDK的上下文对象)、 appid(应用初始化id)。|

#### **ADSSPInitListener** 

ADSSPInitListener 

|**方法名**||**介绍**|
|---|---|---|
|onSuccess()|初始化成功。||
|onFailed(code: number, msg:|初始化失败。参数说明:|code(错误码)、msg(错误|
|string)|信息)。||

#### **6.1.2 初始化接入示例** 

1 // 设置debug状态,开发阶段建议设置true 2 ADSuyi.Sdk.setDebug(true) 3 const listener: InitListener = { 4 onFailed(code: number, msg: string) { 

5 console.log(TAG, 'onFailed code :: ' + code + ' msg :: ' + msg) 6 }, 7 8 onSuccess() { 9 console.log(TAG, 'onSuccess') 10 } 11 12 } 13 // 设置初始化状态监听 14 ADSuyi.Sdk.setInitListener(listener) 15 // 初始化广告 16 ADSuyi.Sdk.init(getContext(this), 'appid') 

### **6.2 开屏广告** 

开屏广告建议在闪屏页进行展示,开屏广告的宽度和高度取决于容器的宽高,会撑满广告容器。 

#### **6.2.1 开屏广告主要 API** 

#### **SplashAd** 

|**参数名**|**介绍**|
|---|---|
|SplashAd(context: context: common.Context)|开屏广告构造方法。参数说明:context(当前页面 context: common.Context对象)|
|setListener(listener:|设置广告加载监听。参数说明:listener(广告加载监|
|ADSSPSplashAdListener)|听)。|
|loadAd(posId: string)|加载广告。参数说明:posId(广告位id)。|

#### **ADSSPSplashAdListener** 

|**参数名**||**介绍**|
|---|---|---|
|onFailed: (code: number, msg: string)|广告加载失败。 误原因)|参数说明:code(错误码)、msg(错|
|onSuccess: (adInfos: IADSSPAdInfo[])|广告加载成功。|参数说明:adInfos(广告对象数组)。|

#### **ADSSPSplashComponent** 

开屏广告视图,用于展示开屏广告 

|**参数名**|**类型介绍**|
|---|---|

adSSPAdInfo IADSSPAdInfo 请传入onSuccess中获取到的广告对象。 adSSPStatusListener ADSSPStatusListener 广告事件监听。 

#### **ADSSPStatusListener** 

|**参数名**|**介绍**|
|---|---|
|onStatusChanged: (status: string,|广告事件监听回调。参数说明:status(广告事|
|platform: string)|件)、platform(广告平台)|

#### **6.2.2 开屏广告接入示例** 

|1 2 3|@Entry @Component struct SplashPage|
|---|---|
|4 |{|
|5|...|
|6|@StateisAdVisibilityState :Visibility =Visibility.None|
|7|@StateadInfo ? :IADSSPAdInfo = undefined|
|8|...|
|9||
|10|build() {|
|11|...|
|12|ADSSPSplashComponent({|
|13|adSSPAdInfo : this.adInfo,|
|14|adSSPStatusListener : {|
|15|onStatusChanged : (status : string,platform : string) => {|
|16|switch (status) {|
|17|caseAdStatusAction.AD_SHOW :|
|18|console.log(TAG, 'onAdShow')|
|19|break|
|20|caseAdStatusAction.AD_CLICK :|
|21|console.log(TAG, 'onAdClick')|
|22|break|
|23|caseAdStatusAction.AD_SKIP :|
|24|console.log(TAG, 'onAdSkip')|
|25|break|
|26|caseAdStatusAction.AD_CLOSE :|
|27|console.log(TAG, 'onAdClose')|
|28|this.hideAd()|
|29|break|
|30|caseAdStatusAction.AD_RENDER_FAILED :|
|31|console.log(TAG, 'onAdRenderFailed msg :: ')|
|32|this.hideAd()|
|33|break|
|34|}|
|35|}|
|36|}|

37 }) 38 .visibility(this.isAdVisibilityState) 39 ... 40 } 41 ... 42 loadAd() { 43 // 广告请求回调监听 44 const adSSPLoadListener: ADSSPSplashAdListener = { 45 onFailed: (code: number, msg: string) => { 46 ... 47 }, 48 49 onSuccess: (adInfos: IADSSPAdInfo[]) => { 50 ... 51 this.adInfo = adInfos[0] 52 ... 53 } 54 } 55 56 // 创建广告对象 57 const splashAd: SplashAd = new SplashAd(this.context) 58 // 设置监听 59 splashAd.setListener(adSSPLoadListener) 60 // 加载广告 61 splashAd.loadAd('请填写广告位') 62 } 63 ... 64 } 

### **6.3 信息流模版广告** 

信息流列表,轮播控件,固定位置都是较为适合 

#### **6.3.1 信息流模版广告 API** 

#### **NativeExpressAd** 

|**参数名**|**介绍**|
|---|---|
|NativeExpressAd(context:|开屏广告构造方法。参数说明:context(当前页面|
|context: common.Context)|context: common.Context对象)|
|setListener(listener:|设置广告加载监听。参数说明:listener(广告加载监|
|ADSSPNativeExpressAdListener)|听)。|
|loadAd(posId: string)|加载广告。参数说明:posId(广告位id)。|

#### **ADSSPNativeExpressAdListener** 

|**参数名**||**介绍**|
|---|---|---|
|onFailed: (code: number, msg: string)|广告加载失败。 误原因)|参数说明:code(错误码)、msg(错|
|onSuccess: (adInfos: IADSSPAdInfo[])|广告加载成功。|参数说明:adInfos(广告对象数组)。|

#### **ADSSPNativeExpressComponent** 

信息流广告视图,用于展示开屏广告 

|**参数名**|**介绍**||
|---|---|---|
|adSSPAdInfo|请传入onSuccess中获取到的广|告对象。|
|adWidth|广告宽度。||
|muted|是否静音,默认静音。||
|**参数名**|**类型**|**介绍**|
|adSSPAdInfo|IADSSPAdInfo|请传入onSuccess中获取到的广告对象。|
|adWidth|number|广告宽度。|
|muted|boolean|是否静音,默认静音。|
|adSSPStatusLi|stener ADSSPStatusListener|广告事件监听。|

#### **ADSSPStatusListener** 

|**参数名**|**介绍**|
|---|---|
|onStatusChanged: (status: string,|广告事件监听回调。参数说明:status(广告事|
|platform: string)|件)、platform(广告平台)|

#### **6.3.2 信息流模版广告接入示例** 

1 @Entry 2 @Component 3 struct NativeExpressPage 4 { 5 ... 6 @State itemList: Array<object> = [] 7 ... 8 9 aboutToAppear(): void { 

10 this.getData() 11 

12 

} 

13 build() { 

- 14 RelativeContainer() { 

15 ... 

- 16 List() { 

- 17 ForEach(this.itemList, (item: object, index: number) => { 18 ListItem() { 

- 19 if (item instanceof IADSSPAdInfo) { 20 ADSSPNativeExpressComponent({ 21 adSSPAdInfo: item, 22 adWidth: px2vp(display.getDefaultDisplaySync().width), 23 muted: false, 

- 24 adSSPStatusListener: { 

25 onStatusChanged: (status: string, platform: string) => { 26 switch (status) { 27 case AdStatusAction.AD_SHOW: 28 console.log(TAG, 'onAdShow') 29 break 30 case AdStatusAction.AD_CLICK: 31 console.log(TAG, 'onAdClick') 32 break 33 case AdStatusAction.AD_SKIP: 34 console.log(TAG, 'onAdSkip') 35 break 36 case AdStatusAction.AD_CLOSE: 37 console.log(TAG, 'onAdClose') 38 break 39 case AdStatusAction.AD_RENDER_FAILED: 40 console.log(TAG, 'onAdRenderFailed msg :: ') 41 break 42 } 43 } 44 } 45 }) 46 .backgroundColor('#ffffff') 47 } else { 48 Text('测试数据' + index) 49 .width('100%') 50 .height('200') 51 } 52 } 53 .height('undefined') 54 }) 55 } 56 .width('100%') 57 .alignRules({ 58 'top': { 'anchor': 'titleBar', 'align': VerticalAlign.Bottom }, 59 'bottom': { 'anchor': '__container__', 'align': VerticalAlign.Bottom } 60 }) 61 } 62 .height('100%') 

|63|.width('100%')|
|---|---|
|64|.backgroundColor('#fff3f3f3')|
|65|}|
|66||
|67|getData() {|
|68|//广告请求回调监听|
|69|constadSSPLoadListener :ADSSPNativeExpressAdListener = {|
|70|onFailed : (code : number,msg : string) => {|
|71|...|
|72|},|
|73||
|74|onSuccess : (adSSPAdInfoList : Array <IADSSPAdInfo >) => {|
|75|for (letindex = 0;index <adSSPAdInfoList.length;index ++) {|
|76|constelement =adSSPAdInfoList[index];|
|77|this.itemList.push(element)|
|78|}|
|79||
|80|for (letindex = 0;index < 10;index ++) {|
|81|this.itemList.push(new String('1'))|
|82|}|
|83|}|
|84|}|
|85||
|86|//创建广告对象|
|87|constnativeExpressAd = new NativeExpressAd(this.context)|
|88|//设置监听|
|89|nativeExpressAd.setListener(adSSPLoadListener)|
|90|//加载广告|
|91|nativeExpressAd.loadAd('请填写广告位')|
|92|}|
|93||
|94|}|

### **6.4 插屏广告示例** 

插屏广告是移动广告的一种常见形式,在应用流程中弹出,当应用展示插屏广告时,用户可以选 择点击广告,也可以将其关闭并返回应用。 

#### **6.4.1 插屏广告主要 API** 

#### **InterstitialAd** 

|**参数名**|**介绍**|
|---|---|
|InterstitialAd(context:|开屏广告构造方法。参数说明:context(当前页面|
|common.Context)|context: common.Context对象)|
|setListener(listener:|设置广告加载监听。参数说明:listener(广告加载监|
|ADSSPInterstitialAdListener)|听)。|

加载广告。参数说明:posId(广告位id)。 

loadAd(posId: string) 

#### **ADSSPInterstitialAdListener** 

|**参数名**||**介绍**|
|---|---|---|
|onFailed: (code: number, msg: string)|广告加载失败。 (错误原因)|参数说明:code(错误码)、msg|
|onSuccess: (adInfos:|广告加载成功。|参数说明:adInfos(广告对象数|
|InterstitialAdInfo[])|组)。||

#### **InterstitialAdInfo** 

开屏广告视图,用于展示开屏广告 

|**参数名**|**介绍**|
|---|---|
|show(uiContext: UIContext,|展示广告。参数说明:uiContext|
|adStatusListener:|(UIContext)、adStatusListener(广告事件监|
|ADSSPStatusListener)|听)|

#### **ADSSPStatusListener** 

|**参数名**|**介绍**|
|---|---|
|onStatusChanged: (status: string,|广告事件监听回调。参数说明:status(广告事|
|platform: string)|件)、platform(广告平台)|

#### **6.4.2 插屏广告接入示例** 

1 2 @Entry 3 @Component 4 struct SuyiInterstitialPage { 5 6 ... 7 private adInfo?: InterstitialAdInfo 8 private interstitialAd?: InterstitialAd 9 ... 10 11 build() { 12 ... 13 } 14 15 loadAd() { // 广告请求回调监听 

16 const adSSPLoadListener: ADSSPInterstitialAdListener = { 17 onFailed: (code: number, msg: string) => { 18 ... 19 }, 20 21 onSuccess: (adInfos: InterstitialAdInfo[]) => { 22 ... 23 this.adInfo = adInfos[0] 24 ... 25 } 26 } 27 28 // 创建广告对象 29 this.interstitialAd = new InterstitialAd(this.context) 30 // 设置监听 31 this.interstitialAd.setListener(adSSPLoadListener) 32 // 加载广告 33 this.interstitialAd.loadAd('请填写广告位') 34 } 35 36 showAd() { 37 if (!this.adInfo) { 38 // 没有广告填充 39 return 40 } 41 42 const adSSPStatusListener: ADSSPStatusListener = { 43 onStatusChanged: (status: string, platform: string) => { 44 switch (status) { 45 case AdStatusAction.AD_SHOW: 46 console.log(TAG, 'onAdShow') 47 break 48 case AdStatusAction.AD_CLICK: 49 console.log(TAG, 'onAdClick') 50 break 51 case AdStatusAction.AD_CLOSE: 52 console.log(TAG, 'onAdClose') 53 break 54 case AdStatusAction.AD_RENDER_FAILED: 55 console.log(TAG, 'onRenderFailed') 56 break 57 } 58 } 59 } 60 61 this.adInfo?.show(this.getUIContext(), adSSPStatusListener) 62 } 63 ... 64 } 65 

**6.5 激励视频广告示例** 

将短视频融入到APP场景当中,用户观看短视频广告后可以给予一些应用内奖励。 

#### **6.5.1 激励视频广告主要 API** 

#### **InterstitialAd** 

|**参数名**|**介绍**|
|---|---|
|RewardAd(context: common.Context)|开屏广告构造方法。参数说明:context(当前页面 context: common.Context对象)|
|setListener(listener:|设置广告加载监听。参数说明:listener(广告加载监|
|ADSSPRewardAdListener)|听)。|
|loadAd(posId: string)|加载广告。参数说明:posId(广告位id)。|

#### **ADSSPRewardAdListener** 

|**参数名**|**介绍**|
|---|---|
|onFailed: (code: number, msg: string)|广告加载失败。参数说明:code(错误码)、msg(错 误原因)|
|onSuccess: (adInfos: RewardAdInfo[]) **RewardAdInfo** 开屏广告视图,用于展示开屏广告|广告加载成功。参数说明:adInfos(广告对象数组)。|
|**参数名**|**介绍**|
|show(uiContext: UIContext, adStatusListener: ADSSPStatusListener)|展示广告。参数说明:uiContext (UIContext)、adStatusListener(广告事件监 听)|

#### **ADSSPStatusListener** 

|**参数名**|**介绍**|
|---|---|
|onStatusChanged: (status: string,|广告事件监听回调。参数说明:status(广告事|
|platform: string)|件)、platform(广告平台)|

#### **6.5.2 激励视频广告接入示例** 

1 @Entry 2 @Component 3 struct SuyiRewardPage { 4 5 ... 6 private adInfo?: RewardAdInfo 7 private rewardAd?: RewardAd 8 ... 9 10 build() { 11 ... 12 } 13 14 loadAd() { 15 // 广告请求回调监听 16 const adSSPLoadListener: ADSSPRewardAdListener = { 17 onFailed: (code: number, msg: string) => { 18 console.log(TAG, 'onAdError code :: ' + code + ' msg :: ' + msg) 19 }, 20 21 onSuccess: (adInfos: RewardAdInfo[]) => { 22 console.log(TAG, 'onAdSuccess') 23 promptAction.showToast({ 24 message: '广告加载成功', 25 duration: 2000 26 }); 27 this.adInfo = adInfos[0] 28 } 29 } 30 31 // 创建广告对象 32 this.rewardAd = new RewardAd(this.context) 33 // 设置监听 34 this.rewardAd.setListener(adSSPLoadListener) 35 // 加载广告 36 this.rewardAd.loadAd('请填写广告位') 37 } 38 39 showAd() { 40 if (!this.adInfo) { 41 promptAction.showToast({ 42 message: '没有广告填充', 43 duration: 2000 44 }); 45 return 46 } 47 48 const adSSPStatusListener: ADSSPStatusListener = { 49 onStatusChanged: (status: string, platform: string) => { 50 switch (status) { 51 case AdStatusAction.AD_SHOW: 52 console.log(TAG, 'onAdShow') 

53 break 54 case AdStatusAction.AD_CLICK: 55 console.log(TAG, 'onAdClick') 56 break 57 case AdStatusAction.AD_REWARD: 58 console.log(TAG, 'onAdReward') 59 break 60 case AdStatusAction.AD_CLOSE: 61 console.log(TAG, 'onAdClose') 62 break 63 case AdStatusAction.AD_RENDER_FAILED: 64 console.log(TAG, 'onRenderFailed') 65 break 66 } 67 } 68 } 69 70 this.adInfo?.show(this.getUIContext(), adSSPStatusListener) 71 } 72 } 

### **6.6 广告状态主要 API** 

#### **ADSSPStatusListener** 

|**方法名**|**介绍**|
|---|---|
|onStatusChanged: (status: string,|参数说明:status(回调状态AdStatus)、|
|platform: string)|platform(广告平台名)。|

#### **AdStatusAction** 

|**参数名**|**介绍**|
|---|---|
|AD_SHOW|广告曝光回调。|
|AD_CLICK|广告点击回调。|
|AD_SKIP|广告跳过回调。在此处不要对广告进行关闭操作。|
|AD_CLOSE|广告关闭回到。在此处移除广告。|
|AD_REWARD|广告激励回调。|
|AD_RENDER_FAILED|广告渲染失败回调。|

**7.错误码** 

|**错误码**|**介绍**|
|---|---|
|-10006|初始化接口数据为空。|
|-10007|初始化接口KEY为空。|
|-20002|context为空。|
|-20104|初始化数据为空,可能是没有本地缓存的初始化数据并且初始接口请求失败。|
|-20106|没有找到当前PosId的配置信息,主要有以下三种情况 :1、初始化失败,本地没有 初始化配置信息并且远程拉取初始化配置失败了,请检查网络或AppId是否正确; 2、传入的PosId有误;3、如果前两条均正常,请后台检查该PosId是否配置并开 启了三方平台的广告位信息。|
|-20107|平台的广告位信息为空。|
|-20109|暂不支持当前广告类型。|
|-20110|瀑布流轮询完毕,无广告返回。|
|-20112|已达到展示上限。|
|-20122|广告位获取广告超时/广告源获取广告超时。|

## **8.备注** 

具体的接入代码和流程,请参考Demo 

## **9.商务合作** 

邮箱 : yuxingcao@admobile.top
