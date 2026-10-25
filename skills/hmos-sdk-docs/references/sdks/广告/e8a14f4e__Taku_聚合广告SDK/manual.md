# Taku SDK使用指南

# 集成

## 1.SDK下载

您可以从TaKu SDK下载中心获取最新版SDK。下载的SDK压缩包,解压后里面会有taku_sdk文件夹和

network_sdk文件夹

● taku_sdk中包含anythink_sdk.har(TaKu SDK)

● network_sdk中包含第三方广告平台的 anythink_network_xx.har(第三方Network的Adapter)

和XXX.har(第三方 Network SDK)

## 2.SDK集成

Demo示例:Harmony Demo Github地址(点击跳转)

●手动导入har包

1.在项目的根目录新建libs文件夹,把taku_sdk和network_sdk的har包放进去。

2.在Module的oh-package.json5中添加依赖:

```
{
"dependencies": {
"anythink_sdk": "file:../libs/anythink_sdk",
"anythink_network_ks": "file:../libs/anythink_network_ks", //network
adapter
"ksadsdk":"file:../libs/KSAdSDK-xxx.har"//network sdk
  }
}
```

注意:network adapter的依赖名称必须和har包名字一致,如上述的anythink_network_ks。

3.在项目的根目录下的oh-package.json5中添加以下配置(因为network adpater的Har需要依

赖快手和anythink sdk的Har,所以这里需要用到overrides属性配置):

```
{
"overrides": {
'ksadsdk': 'file:./libs/KSAdSDK-xxx.har',
'anythink_sdk': 'file:./libs/anythink_sdk.har'
    }
}
```

●添加权限

打开app模块的module.json5文件,添加以下权限:访问网络、获取网络状态

```
{
"requestPermissions": [
      {
"name": "ohos.permission.GET_NETWORK_INFO"
      },
      {
"name": "ohos.permission.INTERNET"
      }
    ]
}
```

## 3.SDK初始化

```
letconfiguration: ATInitConfiguration = {
appId: "your app id",
appKey: "your app key"
}
ATSDK.init(getContext().getApplicationContext(), configuration)
ATSDK.start().then((result) => {
// result: true -> sdk init success
})
```

# 激励视频

## 1.加载广告

```
let rewardAd = newATRewardVideoAd("your placement id");
this.rewardAd = rewardAd;
rewardAd.setAdListener({
onAdLoaded: (): void => { },
onAdShow: (adInfo: ATAdInfo): void => { },
onAdClick: (adInfo: ATAdInfo): void => { },
onAdClose: (adInfo: ATAdInfo): void => { },
onAdReward: (adInfo: ATAdInfo): void => { },
onAdLoadFailed: (adError: ATAdError): void => { },
onAdVideoPlayStart: (adInfo: ATAdInfo): void => { },
onAdVideoPlayEnd: (adInfo: ATAdInfo): void => { },
onAdVideoPlayFailed: (adError: ATAdError, adInfo?: ATAdInfo | undefined):
void => { },
onAdOtherStatus: (adInfo?: ATAdInfo): void => { }
});
constlocalExtraMap: Record<string, Object> = {};
// 仅针对快手平台的广告配置
localExtraMap[ATKSConfig.VIDEO_SOUND_ENABLE_KEY] = false; //设置静音
localExtraMap[ATKSConfig.VIDEO_AUTO_PLAY_TYPE_KEY] = 3; //设置不自动播放
rewardAd.loadAd({
context: getContext(),
localExtraMap: localExtraMap
});
```

## 2.展示广告

```
if (rewardAd.isAdReady()) {
    rewardAd.showAd();
}
```

 

## 3.API说明

●ATRewardVideoAd

激励视频广告的操作类,负责广告加载、监听、显示等。

● ATRewardVideoAdListener

广告位层级的广告事件回调

# 插屏广告

## 1.加载广告

```
let interstitialAd = newATInterstitialAd("your placement id");
this.interstitialAd = interstitialAd;
interstitialAd.setAdListener({
onAdLoaded: (): void => { },
onAdShow: (adInfo: ATAdInfo): void => { },
onAdClick: (adInfo: ATAdInfo): void => { },
onAdClose: (adInfo: ATAdInfo): void => { },
onAdLoadFailed: (adError: ATAdError): void => { },
onAdVideoPlayStart: (adInfo: ATAdInfo): void => { },
onAdVideoPlayEnd: (adInfo: ATAdInfo): void => { },
onAdVideoPlayFailed: (adError: ATAdError, adInfo?: ATAdInfo): void => { }
})
constlocalExtraMap: Record<string, Object> = {};
// 仅针对快手平台的广告配置
localExtraMap[ATKSConfig.VIDEO_SOUND_ENABLE_KEY] = false; //设置静音
localExtraMap[ATKSConfig.VIDEO_AUTO_PLAY_TYPE_KEY] = 3; //设置不自动播放
interstitialAd.loadAd({ context: getContext(), localExtraMap: localExtraMap });
```

 

## 2.展示广告

```
if (interstitialAd.isAdReady()) {
  interstitialAd.showAd(getContext());
}
```

 

## 3.API说明

● ATInterstitialAd

插屏广告的操作类,负责广告加载、监听、显示等。

 

● ATInterstitialAdListener

广告位层级的广告事件回调

# 开屏广告

## 1.加载广告

```
let splashAd = newATSplashAd("your placement id");
splashAd.setAdListener({
onAdLoaded: (isTimeout: boolean): void => { },
onAdShow: (adInfo: ATAdInfo): void => { },
onAdClick: (adInfo: ATAdInfo): void => { },
onAdClose: (adInfo: ATAdInfo): void => { },
onAdLoadTimeout: (): void => { },
onAdLoadFailed: (adError: ATAdError): void => { }
});
constlocalExtraMap: Record<string, Object> = {};
// 仅针对快手平台的广告配置
localExtraMap[ATKSConfig.VIDEO_SOUND_ENABLE_KEY] = false; //设置静音
localExtraMap[ATKSConfig.VIDEO_AUTO_PLAY_TYPE_KEY] = 1; //设置自动播放
splashAd.loadAd({
context: getContext(),
fetchAdTimeout: 5000,
localExtraMap: localExtraMap,
});
```

 

## 2.展示广告

```
BuildATSplashAdView(this.splashAd)
1
```

 

## 3.API说明

● ATSplashAd

开屏广告的操作类,负责广告加载、监听、显示等。

 

● ATSplashAdListener

广告位层级的广告事件回调

# 原生广告

## 1.加载广告

```
const atNativeAd = newATNativeAd("your placement id");
atNativeAd.setAdListener({
onAdLoaded: (): void => { },
onAdLoadFailed: (adError: ATAdError): void => { }
});
atNativeAd.loadAd({
context: getContext()
});
```

 

## 2.展示广告

```
(1)先通过ATNative#getNativeAd()获取广告对象NativeAd
const nativeAd = atNativeAd.getNativeAd();
if (!nativeAd) {
this.adMsg = "ad is not ready";
return;
}
nativeAd?.setNativeAdEventListener({
onAdShow: (adInfo: ATAdInfo): void => { },
onAdClose: (adInfo: ATAdInfo): void => { },
onAdClick: (adInfo: ATAdInfo): void => { },
onAdDislikeClick: (adInfo: ATAdInfo): void => { },
onAdVideoResume: (adInfo: ATAdInfo): void => { },
onAdVideoPause: (adInfo: ATAdInfo): void => { },
onAdVideoPlayStart: (adInfo: ATAdInfo): void => { },
onAdVideoPlayEnd: (adInfo: ATAdInfo): void => { },
onAdVideoPlayFailed: (adError: ATAdError, adInfo?: ATAdInfo | undefined):
void => { }
})
```

(2)再通过NativeAd的isNativeExpress方法判断是自渲染还是模板渲染

```
if (nativeAd?.isNativeExpress()) {
// 模板渲染
  ...
} else {
// 自渲染
  ...
}
```

 

●模板渲染

```
@Component
struct NativeAdPage {
build() {
    ...
BuildATNativeAdExpressView(nativeAd);
    ...
  }
}
```

●自渲染

通过NativeAd的getAdMaterial方法获取素材进行渲染,详情请参考Demo示例:

NativeAdItemComponent。

## 3.API说明

● ATNativeAd

原生广告的操作类,负责广告加载、监听、显示等。

 

● ATNativeAdLoadListener

广告位层级的广告事件回调

 

● NativeAd

原生广告对象,用于展示广告

 

● ATNativeAdEventListener

广告展示相关的事件监听回调

 

● ATNativeAdMaterial

自渲染广告返回的广告素材对象

## 注意事项

广告曝光

广告曝光逻辑按照页面展示比例来计算,开发者需要在自渲染的广告组件上监听展示比例并且回调给

SDK,示例:

```
// 添加可见区域监听,SDK内部处理曝光逻辑
.onVisibleAreaChange(this.itemInfo.nativeAd?.getVisibleAreaRatios(),
this.itemInfo.nativeAd?.getVisibleAreaChangeListener())
```

广告点击

目前SDK内部无法自动给开发者的UI组件添加点击事件,对于点击后需要触发转化的控件,需要手动

添加点击事件

并且回调给SDK,示例:

```
.onClick((e: ClickEvent) => {
// 点击转化
this.itemInfo?.nativeAd?.getClickHandler()(getContext(this) as
common.UIAbilityContext,
e)
})
```

# 回调信息说明

## 1.ATAdInfo

 

## 2.ATAdSource

 

## 3.ATAdConfig

 

## 4.ATAdPrice

 

## 5.ATAdStatusInfo
