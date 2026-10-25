# TaKu Harmony SDK API 概览

# ●

# SDK 初始化

| 方法 | 描述 |
|---|---|
| ATSDK.init() | 初始化配置 |
| ATSDK.start() | 开始初始化 |

# 激励广告

# ●

### ● ATRewardVideoAd

激励视频广告的操作类,负责广告加载、监听、显示等。

| 方法 | 说明 |
|---|---|
| ATRewardVideoAd(placementId: string) | 广告的初始化方法 : placementID 激励视频样式的广告位,通 过后台创建激励视频广告位获取的 |
| setAdListener(listener: ATRewardVideoAdListener) | 设置广告位层级的广告监听回调 listener:广告位事件回调的接口类 |
| loadAd(adLoadConfig?: ATRewardVideoAdLoadConfig) | 发起广告加载 : adLoadConfig 加载广告配置 |
| isAdReady() | 判断当前广告位是否存在可展示的广告 返回值:true=存在可展示的广告,false= 不存在可展示的广告 |
| showAd(context?: Context, adShowConfig?: ATRewardVideoAdShowConfig) | 展示广告,传入展示广告时的自定义参数 : adShowConfig 展示广告配置,包括自定 义参数 |

| getAdCaches() | 查询当前广告位的所有缓存信息的ATAdInfo 对象 |
|---|---|
| getTopAdInfo() | 获取当前广告位优先级最高的广告缓存信 息 ATAdInfo对象 |

### ● ATRewardVideoAdListener

广告位层级的广告事件回调

| 方法 | 说明 |
|---|---|
| onAdLoaded: () | 广告加载成功回调 |
| onAdShow: (adInfo: ATAdInfo) | 广告展示回调 |
| onAdClick: (adInfo: ATAdInfo) | 广告点击回调 |
| onAdClose: (adInfo: ATAdInfo) | 广告关闭回调 |
| onAdReward: (adInfo: ATAdInfo) | 下发激励的时候会触发此回调,建议您在此 回调中下发奖励 |
| onAdLoadFailed: (adError: ATAdError) | 广告加载失败回调 |
| onAdVideoPlayStart: (adInfo: ATAdInfo) | 广告开始播放回调 |
| onAdVideoPlayEnd: (adInfo: ATAdInfo) | 广告播放结束回调 |
| onAdVideoPlayFailed: (adError: ATAdError, adInfo?: ATAdInfo) | 广告播放失败回调 |
| onAdOtherStatus: (adInfo?: ATAdInfo) | 广告其他状态的回调 |

# 插屏广告

# ●

### ● ATInterstitialAd

插屏广告的操作类,负责广告加载、监听、显示等。

| 方法 | 说明 |
|---|---|

| ATInterstitialAd(placementId: string) | 广告的初始化方法 : placementID 插屏样式的广告位,通过后 台创建插屏广告位获取的 |
|---|---|
| setAdListener(listener: ATInterstitialAdListener) | 设置广告位层级的广告监听回调 : listener 广告位事件回调的接口类 |
| loadAd(adLoadConfig?: ATInterstitialAdLoadConfig) | 发起广告加载 : adLoadConfig 加载广告配置 |
| isAdReady() | 判断当前广告位是否存在可展示的广告 返回值:true=存在可展示的广告,false= 不存在可展示的广告 |
| showAd(context?: Context, adShowConfig?: ATInterstitialAdShowConfig) | 展示广告,传入展示广告时的自定义参数 : adShowConfig 展示广告配置,包括自定 义参数 |
| getAdCaches() | 查询当前广告位的所有缓存信息的ATAdInfo 对象 |
| getTopAdInfo() | 获取当前广告位优先级最高的广告缓存信 息 ATAdInfo对象 |
| destroy() | 销毁广告 |

### ● ATInterstitialAdListener

广告位层级的广告事件回调

| 方法 | 说明 |
|---|---|
| onAdLoaded: () | 广告加载成功回调 |
| onAdShow: (adInfo: ATAdInfo) | 广告展示回调 |
| onAdClick: (adInfo: ATAdInfo) | 广告点击回调 |
| onAdClose: (adInfo: ATAdInfo) | 广告关闭回调 |
| onAdLoadFailed: (adError: ATAdError) | 广告加载失败回调 |

| onAdVideoPlayStart: (adInfo: ATAdInfo) | 广告开始播放回调 |
|---|---|
| onAdVideoPlayEnd: (adInfo: ATAdInfo) | 广告播放结束回调 |
| onAdVideoPlayFailed: (adError: ATAdError, adInfo?: ATAdInfo ) | 广告播放失败回调 |

# 开屏广告

# ●

### ● ATSplashAd

开屏广告的操作类,负责广告加载、监听、显示等。

| 方法 | 说明 |
|---|---|
| ATSplashAd(placementId: string) | 广告的初始化方法 : placementID 开屏样式的广告位,通过后 台创建开屏广告位获取的 |
| setAdListener(listener: ATSplashAdListener) | 设置广告位层级的广告监听回调 : listener 广告位事件回调的接口类 |
| loadAd(adLoadConfig?: ATSplashAdLoadConfig) | 发起广告加载 : adLoadConfig 加载广告配置 |
| BuildATSplashAdView(ATSplashAd) | 展示广告 |
| isAdReady() | 判断当前广告位是否存在可展示的广告 返回值:true=存在可展示的广告,false= 不存在可展示的广告 |
| getPlacementId() | 获取广告位ID |
| getAdListener() | 获取广告位层级的广告监听回调 |
| getAdCaches() | 查询当前广告位的所有缓存信息的ATAdInfo 对象 |
| getTopAdInfo() | 获取当前广告位优先级最高的广告缓存信 息 ATAdInfo对象 |

### ● ATSplashAdListener

广告位层级的广告事件回调

| 方法 | 说明 |
|---|---|
| onAdLoaded: () | 广告加载成功回调 |
| onAdShow: (adInfo: ATAdInfo) | 广告展示回调 |
| onAdClick: (adInfo: ATAdInfo) | 广告点击回调 |
| onAdClose: (adInfo: ATAdInfo) | 广告关闭回调 |
| onAdLoadFailed: (adError: ATAdError) | 广告加载失败回调 |
| onAdLoadTimeout() | 广告加载超时回调 |

# 原生广告

# ●

### ● ATNativeAd

原生广告的操作类,负责广告加载、监听、显示等。

| 方法 | 说明 |
|---|---|
| ATNativeAd(placementId: string) | 广告的初始化方法 : placementID 原生样式的广告位,通过后 台创建开屏广告位获取的 |
| setAdListener(listener: ATNativeAdLoadListener) | 设置广告位层级的广告监听回调 : listener 广告位事件回调的接口类 |
| loadAd(adLoadConfig?: ATNativeAdLoadConfig) | 发起广告加载 : adLoadConfig 加载广告配置 |
| getNativeAd(showConfig?: ATNativeAdShowConfig) | 获取广告对象,用于展示广告 |
| isAdReady() | 判断当前广告位是否存在可展示的广告 |

|  | 返回值:true=存在可展示的广告,false= 不存在可展示的广告 |
|---|---|
| getAdCaches() | 查询当前广告位的所有缓存信息的ATAdInfo 对象 |
| getTopAdInfo() | 获取当前广告位优先级最高的广告缓存信 息 ATAdInfo对象 |

### ● ATNativeAdLoadListener

广告位层级的广告事件回调

| 方法 | 说明 |
|---|---|
| onAdLoaded: () | 广告加载成功回调 |
| onAdLoadFailed: (adError: ATAdError) | 广告加载失败回调 |

### ● NativeAd

原生广告对象,用于展示广告

| 方法 | 说明 |
|---|---|
| setNativeAdEventListener(listener: NativeAdEventListener) | 设置广告展示相关的事件监听回调 |
| isNativeExpress() | 是否为模板渲染类型的广告 返回值:true=模板广告,false=自渲染广 告 |
| getAdMaterial() | 获取广告素材对象,仅自渲染广告支持 返回值:广告素材对象 |

### ● ATNativeAdEventListener

广告展示相关的事件监听回调

| 方法 | 说明 |
|---|---|
| onAdShow: (adInfo: ATAdInfo) | 广告展示回调 |
| onAdClose: (adInfo: ATAdInfo) | 广告关闭回调 |
| onAdClick: (adInfo: ATAdInfo) | 广告点击回调 |
| onAdDislikeClick: (adInfo: ATAdInfo) | 广告点击关闭回调 |
| onAdVideoResume: (adInfo: ATAdInfo) | 广告继续播放回调 |
| onAdVideoPause: (adInfo: ATAdInfo) | 广告暂停播放回调 |
| onAdVideoPlayStart: (adInfo: ATAdInfo) | 广告开始播放回调 |
| onAdVideoPlayEnd: (adInfo: ATAdInfo) | 广告播放结束回调 |
| onAdVideoPlayFailed: (adError: ATAdError, adInfo?: ATAdInfo \| undefined) | 广告播放失败回调 |

### ● ATNativeAdMaterial

自渲染广告返回的广告素材对象

| 方法 | 说明 |
|---|---|
| getAdTitle() | 获取广告标题 |
| getAdDesc() | 获取广告描述 |
| getAdMainImageUrl() | 获取广告主图url |
| getImageUrlList() | 获取图片列表-url |
| getImageList() | 获取广告图片列表对象 |
| getAdIconUrl() | 获取广告Icon |
| getAdFrom() | 获取广告来源/赞助商 |

| getAdChoiceUrl(choiceType?: ATAdChoiceType) | 获取广告角标 NORMAL = 0, GREY = 1 |
|---|---|
| getAdMaterialType() | 获取素材类型 UNKNOWN = 0, VIDEO = 1, IMAGE = 2, LIVE = 3 |
| getAdCallToActionText() | 获取广告按钮文案 |
| getAdInteractionType() | 获取广告的交互类型 UNKNOWN = 0, DOWNLOAD = 1, H5 = 2 |
| getAdAppInfo() | 获取广告应用相关的信息,比如隐私数据, 应用名 |
| getAdVideoInfo() | 获取视频相关信息 |
| getUniqueKey() | 获取唯一标识,用于LazyForEach标识广告 |
| getVisibleAreaRatios() | 获取可见区域监听数组 |
| getVisibleAreaChangeListener() | 可见区域监听方法,用于SDK内部判断页面 展示比例,处理广告曝光&视频播放等 |
| getClickHandler() | 控件点击监听 |

# 横幅广告

# ●

### ● ATBannerAd

横幅广告的操作类,负责广告加载、监听、显示等。

| 方法 | 说明 |
|---|---|
| ATBannerAd(placementId: string) | 广告的初始化方法 : placementID 横幅样式的广告位,通过后 台创建横幅广告位获取的 |
| setAdListener(listener: ATBannerAdListener) | 设置广告位层级的广告监听回调 : listener 广告位事件回调的接口类 |

| loadAd(adLoadConfig?: Nullable<ATBannerAdLoadConfig>) | 发起广告加载 : adLoadConfig 加载广告配置 |
|---|---|
| getBannerAd(showConfig?: ATBannerAdShowConfig) | 获取广告对象,用于展示广告 |

### ● ATBannerAdListener

广告位层级的广告加载事件回调

| 方法 | 说明 |
|---|---|
| onAdLoaded: () | 广告加载成功回调 |
| onAdLoadFailed: (adError: ATAdError) | 广告加载失败回调 |

### ● ATBannerAdEventListener

广告位层级的广告事件回调

| 方法 | 说明 |
|---|---|
| onAdShow: (adInfo: ATAdInfo) | 广告展示回调 |
| onAdClick: (adInfo: ATAdInfo) | 广告点击回调 |
| onAdClose?: (adInfo: ATAdInfo) | 广告关闭回调 |
| onAdAutoRefreshFailed?: (adError: ATAdError) | 广告自动加载刷新失败回调 |
| onAdAutoRefreshed: (adInfo: ATAdInfo) | 广告自动加载刷新成功回调 |

# 回调信息

# ●

### ● ATAdInfo

| 方法 | 说明 |
|---|---|

| getAdSourceInfo() | 获取广告源信息 |
|---|---|
| getAdConfig() | 获取广告配置信息 |
| getAdPrice() | 获取广告价格信息 |
| getAdStatusInfo() | 获取广告状态信息 |

### ● ATAdSource

| 参数 | 说明 |
|---|---|
| unitId | 广告源ID |
| placementId | 获取后台广告位ID |
| format | 获取广告类型,包 括:"Native" "RewardedVideo" "Banne 、 、 r""Interstitial" "Splash" 、 |
| showId | 获取每次展示广告时生成的独立ID |
| networkType | 获取Network类型 "Network":第三方广告平台 "Cross Promotion":交互推广 _ "Adx":Adx |
| networkPlacementId | 获取广告平台的广告位ID |
| networkFirmId | 获取广告平台对应的ID,用于区分广告平台 |
| ext info _ | 获取广告的自定义信息 |

### ● ATAdConfig

| 参数 | 说明 |
|---|---|
| segmentId | 获取流量分组ID |

| channel | 获取渠道信息 |
|---|---|
| subChannel | 获取子渠道信息 |
| country | 获取国家代码, 例如:”CN" |
| customRule | 获取Placement+App维度的自定义规则的 Json字符串 |
| abtestId | 获取AB测试ID 具体AB测试ID可以从AB测 。 试页面查询 。 |

### ● ATAdPrice

| 参数 | 说明 |
|---|---|
| ecpm | 获取预估eCPM 即每次广告展示的预估 。 eCPM:常规广告源是Taku后台对应广告源 填写的排序价格,竞价广告源是实时竞价返 回的价格 eCPM的货币单位可通过 。 currency获取,通常为元(CNY)或美元 (USD),精度可通过precision获取 。 eCPM含义:每千次广告展示收益 假设广 。 告源A的eCPM=1美元,则展示一次广告源 A之后,展示收益为0.001美元 。 |
| publisherRevenue | 获取 Taku广告位展示收益 即每次广告展 。 示后,预估可获得的收益 单位可通过 。 currency获取,通常为元(CNY)或美元 (USD),精度可通过 precision 获取 |
| currency | 获取收益货币单位 根据返回的货币单位, 。 确定当前eCPM或收益的价格,通常为元 (CNY)或美元(USD) 。 例如:"USD",则返回的价格为“美元”, ecpm 和publisherRevenue 返回的价格单位 均为“美元” 。 |
| precision | 获取eCPM精度 |

|  | "publisher defined":开发者在Taku后台为 _ 广告源定义的eCPM(交叉推广的eCPM也 属于该类型) "estimated": 在Taku后台开启广告源的自动 价格功能后,Taku根据历史数据计算出的 eCPM "exact":实时竞价的eCPM (Meta广告平台 除外) "ecpm api": 针对Meta广告源生效,根据 _ Meta的ReportAPI数据预估的历史eCPM API Taku SDK v5.9.60及以上版本支持 。 。 |
|---|---|

### ● ATAdStatusInfo

| 参数 | 说明 |
|---|---|
| adStatus | 广告的其他状态 -1:未知;1:激励视频直接跳过(仅针对 快手平台) |
