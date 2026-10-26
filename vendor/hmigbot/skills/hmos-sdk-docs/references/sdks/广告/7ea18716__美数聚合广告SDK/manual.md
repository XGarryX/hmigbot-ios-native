# 美数 SDK 使用指南 

## 1. 安装 

### 1.1 SDK下载 

```
ohpm install ms_sdk
```

### 1.2 添加权限 

|名称|说明|
|---|---|
|ohos.permission.APPROXIMATELY_LOCATION|匿名广告id|
|ohos.permission.APPROXIMATELY_LOCATION|位置信息|
|ohos.permission.INTERNET|网络请求|
|ohos.permission.GET_NETWORK_INFO|网络信息|
|ohos.permission.GET_WIFI_INFO|wifi信息|
|ohos.permission.ACCELEROMETER|加速器传感器|
|ohos.permission.GYROSCOPE|陀螺仪传感器|

打开app模块中的 `module.json5` 文件,添加权限: 

```
"requestPermissions": [{
  "name": "ohos.permission.APPROXIMATELY_LOCATION",
  "reason": "$string:reason",
  "usedScene": {"abilities": ['EntryAbility']}
}, {
  "name": "ohos.permission.APP_TRACKING_CONSENT",
  "reason": "$string:app_tracking_permission_reason",
  "usedScene": {
    "abilities": [
      "EntryAbility"
  ],
  "when": "always"
  }
}, {
  "name": "ohos.permission.INTERNET"
}, {
  "name": "ohos.permission.GET_NETWORK_INFO"
}, {
  "name": "ohos.permission.GET_WIFI_INFO"
}, {
  "name": "ohos.permission.ACCELEROMETER"
}, {
  "name": "ohos.permission.GYROSCOPE"
}]
```

## 2 初始化 

在ability的 `onCreate` 回调中添加以下代码 

`await new  MsManager('` 媒体 `ID').init()` 

3 创建广告实例 

```
import { Ms, AD_TYPES, MsAdListener } from'ms_sdk'
```

`const  adParam: Ms.AdParam = {pid:  '` 广告位 `ID', type:  AD_TYPES.BANNER}` 

```
const  adOptions: Ms.AdOptions = {}
const  listener: Ms.AdInteractionListener = new  MsAdListener({
    onAdOpen: () => {},
    onAdLoad: () => {},
    onAdShow: () => {},
    onAdClick: () => {},
    onAdFail: () => {},
    onAdClose: () => {},
    onAdOpenFail: () => {},
    onIntervalDone: () => {},
    onAdReward: () => {},
    onMediaStart: () => {},
    onMediaPause: () => {},
    onMediaStop: () => {},
    onMediaComplete: () => {},
    onMediaError: () => {},
    onMediaResume: () => {},
    onMediaSkip: () => {},
    onMediaMute: () => {},
    onMediaUnmute: () => {},
    onMediaReplay: () => {}
})
const  adController = new  AdManager(adParam, adOptions, listener)
```

## MsAdEventOptions 方法说明 

|方法名|说明|
|---|---|
|`onAdOpen`|广告打开时触发|
|`onAdLoad`|广告加载成功时触发|
|`onAdShow`|广告展示时触发|
|`onAdClick`|广告点击时触发|
|`onAdClose`|广告关闭时触发|
|`onAdFail`|广告加载失败时触发|
|`onAdOpenFail`|广告打开失败时触发|
|`onIntervalDone`|广告间隔完成时触发|
|`onAdReward`|广告奖励时触发|
|`onMediaStart`|媒体开始播放时触发|
|`onMediaPause`|媒体暂停时触发|
|`onMediaStop`|媒体停止时触发|
|`onMediaComplete`|媒体播放完成时触发|
|`onMediaError`|媒体播放错误时触发|
|`onMediaResume`|媒体恢复播放时触发|
|`onMediaSkip`|媒体跳过时触发|
|`onMediaMute`|媒体静音时触发|
|`onMediaUnmute`|媒体取消静音时触发|
|`onMediaReplay`|媒体重播时触发|

4 加载广告 

```
adController.loadAd()
```

## 5展示广告 

```
adConteoller.showAd()
```

## 6.模板渲染 

|类名|说明|
|---|---|
|`SplashAd`|开屏|
|NativeAd|信息流|
|BannerAd|横屏|
|InterstitialAd|插屏|
|IncentiveAd|激励|
|PopupadAd|贴片|
|VideoAd|全屏视频|

### 6.1使用说明 

这里拿开屏举例 

`import { SplashAd,Ms } from 'ms_sdk' import { Ms, AD_TYPES, MsAdListener } from 'ms_sdk' const  adParam: Ms.AdParam = { pid:  '` 广告位 `ID', type:  AD_TYPES.BANNER } const  adOptions: Ms.AdOptions = {} const  listener: Ms.AdInteractionListener = new  MsAdListener({ //... }) SplashAd({ adOptions:  adOptions, adParam:  adParam, interationListener:  listener })` 

## 7 DEMO地址 

https://gitee.com/zhangnan555/ms_harmony_sdk_demo
