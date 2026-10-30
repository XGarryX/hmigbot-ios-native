# **ADSuyi广告聚合 HarmonyOS** **Sdk** 

# **接口说明** 

### **ADSuyi.Sdk 初始化** 

|**方法名**|**参数**||**介绍**|
|---|---|---|---|
|setDebug(isDebug: boolean)|isDebug: bo|olean|设置是否是Debug模式。参数说明:debug(true:开 启,false:关闭, 默认:false)开发阶段以及提交测试 阶段可设置为true,方便异常排查。|
|setInitListener(listener: ADSSPInitListener)|listener: ADSSPInitLi|stener|初始化状态回调。|
|init(context: Context, appid: string)|context: Co appid: strin|ntext, g|初始化方法。参数说明:context(初始化SDK的上下文 对象)、appid(应用初始化id)。|
|**方法名ADSSPInitListener初**|**始化监听**|**介绍**||
|onSuccess()||初始化|成功。|
|onFailed(code: number, m|sg: string)|初始化|失败。参数说明:code(错误码)、msg(错误信息)。|

### **ADSSPInitListener 初始化监听** 

### **开屏广告主要 API** 

#### **SplashAd** 

|**参数名**|**入参**|**介绍**|
|---|---|---|
|SplashAd(context: context:|context: context:|开屏广告构造方法。参数说明:context(当前页面context:|
|common.Context)|common.Context|common.Context对象)|
|setListener(listener: ADSSPSplashAdListener)|listener: ADSSPSplashAdListener|设置广告加载监听。参数说明:listener(广告加载监听)。|
|loadAd(posId: string)|posId: string|加载广告。参数说明:posId(广告位id)。|

#### **ADSSPSplashAdListener** 

|**参数名**|**介绍**|
|---|---|
|onFailed: (code: number, msg: string)|广告加载失败。参数说明:code(错误码)、msg(错误原 因)|
|onSuccess: (adInfos: IADSSPAdInfo[])|广告加载成功。参数说明:adInfos(广告对象数组)。|

#### **ADSSPSplashComponent** 

开屏广告视图,用于展示开屏广告 

|**参数名**|**类型**|**介绍**|
|---|---|---|
|adSSPAdInfo|IADSSPAdInfo|请传入onSuccess中获取到的广告对象。|
|adSSPStatusListener|ADSSPStatusListener|广告事件监听。|

#### **ADSSPStatusListener** 

|**参数名**|**介绍**|
|---|---|
|onStatusChanged: (status: string,|广告事件监听回调。参数说明:status(广告事件)、|
|platform: string)|platform(广告平台)|

### **信息流模版广告 API** 

#### **NativeExpressAd** 

|**参数名**|**入参**|**介绍**|
|---|---|---|
|NativeExpressAd(context: context:|context: context:|开屏广告构造方法。参数说明:context(当前页面context:|
|common.Context)|common.Context|common.Context对象)|
|setListener(listener: ADSSPNativeExpressAdListener)|listener: ADSSPNativeExpressAdListener|设置广告加载监听。参数说明:listener(广告加载监听)。|
|loadAd(posId: string)|posId: string|加载广告。参数说明:posId(广告位id)。|

#### **ADSSPNativeExpressAdListener** 

|**参数名**|**介绍**|
|---|---|
|onFailed: (code: number, msg: string)|广告加载失败。参数说明:code(错误码)、msg(错误原因)|
|onSuccess: (adInfos: IADSSPAdInfo[])|广告加载成功。参数说明:adInfos(广告对象数组)。|

#### **ADSSPNativeExpressComponent** 

信息流广告视图,用于展示开屏广告 

|**参数名**|**介绍**|
|---|---|
|adSSPAdInfo|请传入onSuccess中获取到的广告对象。|
|adWidth|广告宽度。|
|muted|是否静音,默认静音。|

|**参数名**|**类型**|**介绍**|
|---|---|---|
|adSSPAdInfo|IADSSPAdInfo|请传入onSuccess中获取到的广告对象。|
|adWidth|number|广告宽度。|
|muted|boolean|是否静音,默认静音。|
|adSSPStatusListener|ADSSPStatusListener|广告事件监听。|

#### **ADSSPStatusListener** 

|**参数名**|**介绍**|
|---|---|
|onStatusChanged: (status: string,|广告事件监听回调。参数说明:status(广告事件)、|
|platform: string)|platform(广告平台)|

### **插屏广告主要 API** 

#### **InterstitialAd** 

|**参数名**|**入参**|**介绍**|
|---|---|---|
|InterstitialAd(context: common.Context)|context: common.Context|开屏广告构造方法。参数说明:context(当前页面context: common.Context对象)|
|setListener(listener: ADSSPInterstitialAdListener)|listener: ADSSPInterstitialAdListener|设置广告加载监听。参数说明:listener(广告加载监听)。|
|loadAd(posId: string)|posId: string|加载广告。参数说明:posId(广告位id)。|

#### **ADSSPInterstitialAdListener** 

|**参数名**|**介绍**|
|---|---|
|onFailed: (code: number, msg: string)|广告加载失败。参数说明:code(错误码)、msg(错误原 因)|
|onSuccess: (adInfos: InterstitialAdInfo[])|广告加载成功。参数说明:adInfos(广告对象数组)。|

#### **InterstitialAdInfo** 

开屏广告视图,用于展示开屏广告 

|**参数名**|**介绍**|
|---|---|
|show(uiContext: UIContext,|展示广告。参数说明:uiContext(UIContext)、|
|adStatusListener: ADSSPStatusListener)|adStatusListener(广告事件监听)|

#### **ADSSPStatusListener** 

|**参数名**|**介绍**|
|---|---|
|onStatusChanged: (status: string,|广告事件监听回调。参数说明:status(广告事件)、|
|platform: string)|platform(广告平台)|

### **激励视频广告主要 API** 

#### **InterstitialAd** 

|**参数名**|**入参**|**介绍**|
|---|---|---|
|RewardAd(context:|context:|开屏广告构造方法。参数说明:context(当前页面context:|
|common.Context)|common.Context|common.Context对象)|
|setListener(listener: ADSSPRewardAdListener)|listener: ADSSPRewardAdListener|设置广告加载监听。参数说明:listener(广告加载监听)。|
|loadAd(posId: string)|posId: string|加载广告。参数说明:posId(广告位id)。|

#### **ADSSPRewardAdListener** 

|**参数名**|**介绍**|
|---|---|
|onFailed: (code: number, msg: string)|广告加载失败。参数说明:code(错误码)、msg(错误原因)|
|onSuccess: (adInfos: RewardAdInfo[])|广告加载成功。参数说明:adInfos(广告对象数组)。|

#### **RewardAdInfo** 

开屏广告视图,用于展示开屏广告 

|**参数名**|**入参**|**介绍**|
|---|---|---|
|show(uiContext: UIContext,|uiContext: UIContext,|展示广告。参数说明:uiContext|
|adStatusListener:|adStatusListener:|(UIContext)、adStatusListener(广告|
|ADSSPStatusListener)|ADSSPStatusListener|事件监听)|

#### **ADSSPStatusListener** 

|**参数名**|**介绍**|
|---|---|
|onStatusChanged: (status: string,|广告事件监听回调。参数说明:status(广告事件)、|
|platform: string)|platform(广告平台)|

### **广告状态主要 API** 

#### **ADSSPStatusListener** 

|**方法名**|**介绍**|
|---|---|
|onStatusChanged: (status: string, platform: string)|参数说明:status(回调状态AdStatus)、platform(广告 平台名)。|
|**参数名AdStatusAction**|**介绍**|
|AD_SHOW|广告曝光回调。|
|AD_CLICK|广告点击回调。|
|AD_SKIP|广告跳过回调。在此处不要对广告进行关闭操作。|
|AD_CLOSE|广告关闭回到。在此处移除广告。|
|AD_REWARD|广告激励回调。|
|AD_RENDER_FAILED|广告渲染失败回调。|

#### **AdStatusAction** 

## **错误码** 

|**错误码**|**介绍**|
|---|---|
|-10006|初始化接口数据为空。|
|-10007|初始化接口KEY为空。|
|-20002|context为空。|
|-20104|初始化数据为空,可能是没有本地缓存的初始化数据并且初始接口请求失败。|
|-20106|没有找到当前PosId的配置信息,主要有以下三种情况:1、初始化失败,本地没有初始化配置信息 并且远程拉取初始化配置失败了,请检查网络或AppId是否正确;2、传入的PosId有误;3、如果 前两条均正常,请后台检查该PosId是否配置并开启了三方平台的广告位信息。|
|-20107|平台的广告位信息为空。|
|-20109|暂不支持当前广告类型。|
|-20110|瀑布流轮询完毕,无广告返回。|
|-20112|已达到展示上限。|
|-20122|广告位获取广告超时/广告源获取广告超时。|

## **备注** 

具体的接入代码和流程,请参考Demo 

## **商务合作** 

邮箱 : yuxingcao@admobile.top
