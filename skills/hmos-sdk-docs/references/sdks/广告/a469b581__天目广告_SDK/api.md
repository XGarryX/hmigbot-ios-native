# **天目广告SDK** 

## **接口说明** 

### **Tianmu.Sdk 初始化** 

|**方法名**|**入参**|**介绍**|
|---|---|---|
|setDebug(isDebug: boolean)|isDebug: boolean|设置是否是Debug模式。参数说明: debug(true:开启,false:关闭, 默 认:false)开发阶段以及提交测试阶段 可设置为true,方便异常排查。|
|setInitListener(listener: InitListener)|listener: InitListener|初始化状态回调。|
|init(context: Context, appid: string)|context: Context appid: string|初始化方法。参数说明: context(初始化SDK的上下文对象) appid(应用初始化id)|
|setOaid(oaid: string)|oaid: string|设置oaid。参数说明:oaid(oaid参 数)。|
|isCanReadNetworkInfo(b: boolean)|b: boolean|是否可读取网络信息。参数说明: b(true:允许,false:不允许,默认 允许)。|
|isCanReadLocation(b: boolean)|b: boolean|是否可读取位置信息。参数说明: b(true:允许,false:不允许,默认 允许)。|

### **InitListener 初始化监听** 

|**方法名**|**入参**|**介绍**|
|---|---|---|
|onSuccess()||初始化成功。|
|||初始化失败。参数说明:|
|onFailed(code: number, msg: string)||code(错误码)|

msg(错误信息) 

### **Tianmu.AdLoader 广告加载器** 

|**方法名**|**入参**|**介绍**|
|---|---|---|
|loadAd( adParam: AdRequestParams, listener: AdLoadListener )|adParam: AdRequestParams, listener: AdLoadListener|广告加载。参数说明: adParam(广告位配置信 息)、 listener(广告获取回 调)。|
|showAd( uiContext: UIContext, adInfo: AdInfo, adDisplayOptions: AdDisplayOptions, adStatusListener: AdStatusListener )|uiContext: UIContext, adInfo: AdInfo, adDisplayOptions: AdDisplayOptions, adStatusListener: AdStatusListener|插屏、激励视频广告展示方 法。参数说明: uiContext: uiContext上下 文对象; adInfo: 广告对象; adDisplayOptions:展示参 数 adStatusListener:广告状 态|

### **AdLoadListener 广告加载监听** 

|**方法名**|**入参**|**介绍**|
|---|---|---|
|onSuccess(ads: Array)|ads: Array|广告获取成功。参数说明:ads (广告数组)|
|onFailed(code: number, msg: string)|code: number, msg: string|广告获取失败。参数说明: code(错误码) msg(错误信息)|

### **AdRequestParams 广告请求参数配置** 

|**参数名**|**介绍**|
|---|---|
|adId|广告位id,广告后台获取|
|adType|广告位类型,可参考AdType|

adCount 广告获取数量,目前仅支持1个 

### **AdType 广告类型** 

|**参数名**|**介绍**|
|---|---|
|SPLASH_AD|开屏|
|BANNER_AD|banner|
|NATIVE_EXPRESS_AD|信息流模版|
|INTERSTITIAL_AD|插屏|
|REWARD_AD|激励视频|

### **AdInfo 广告对象** 

|**方法名**|**入参**|**介绍**|
|---|---|---|
|getPrice()||广告价格。|
|getExpireSeconds()||广告过期剩余时间。|
|isAvailable()||广告是否可用。可用:true, 不可用:false|
|sendWinNotice()||竞价成功上报。|
|sendLossNotice(price: number, reason: number)|price: number, reason: number|竞价失败上报。 参数说明: price(竞赢方价格)、 reason(竞败原因)|

### **SplashComponent 开屏广告展示布局** 

|**参数名**|**介绍**|
|---|---|
|adInfo|onSuccess: (ads: Array) 中获取到的广告对象。|
|adStatusListener|广告状态AdStatusListener。|

### **BannerComponent 横幅广告展示布局** 

|**参数名**|**介绍**|
|---|---|
|adInfo|onSuccess: (ads: Array) 中获取到的广告对象。|
|adStatusListener|广告状态AdStatusListener。|

### **NativeExpressComponent 信息流模版广告布局** 

|**参数名**|**介绍**|
|---|---|
|adInfo|onSuccess: (ads: Array) 中获取到的广告对象。|
|adWidth|广告宽度,不传则使用屏幕宽度。|
|muted|是否静音。静音:true,不静音:false,默认静音。|
|isAutoPlay|是否自动播放。自动播放:true,不自动播放:false,默认自动 播放。|
|adStatusListener|广告状态AdStatusListener。|

### **AdStatusListener 广告状态监听** 

|**方法名**|**入参**|**介绍**|
|---|---|---|
|onStatusChanged( status: string, ad: AdInfo, data: string )|status: string, ad: AdInfo, data: string|广告状态回调。参数说明: status(回调状态AdStatus)、 ad(广告对象)、 data(其它参数)|

### **AdStatus 广告状态事件** 

|**参数名**||**介绍**|
|---|---|---|
|AD_SHOW|广告曝光回调。||
|AD_CLICK|广告点击回调。||
|AD_SKIP|广告跳过回调。|在此处不要对广告进行关闭操作。|
|AD_CLOSE|广告关闭回到。|在此处移除广告。|
|AD_REWARD|广告奖励回调。||

广告渲染失败回调。 

AD_RENDER_FAILED 

### **错误码介绍** 

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

### **备注** 

具体的接入代码和流程,请参考Demo 

### **商务合作** 

邮箱 : yuxingcao@admobile.top
