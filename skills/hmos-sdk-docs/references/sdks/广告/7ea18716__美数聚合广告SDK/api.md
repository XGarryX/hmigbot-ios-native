# MsManager

```
import {MsManager, Ms} from'ms_sdk'
MsManager(appId:string, options: Ms.MsOptions)
```

## 参数说明

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| appId | string | true | undefined | 应用ID |
| options | Ms.MsOptions | false | undefined | 总体配置,请见MsOptions |

## MsOptions说明

| 参数名 | 类型 | 默认值 | 说明 |  |
|---|---|---|---|---|
| url | string | default: '' | 广告的请求地址 |  |
| isTest | boolean | default: false | 如果没有填写url, 如果 则请求美数的测试地址, 则请求默认地址 true false |  |

## MsManager方法

```
1.init(): Promise<boolean>
```

:初始化,获取环境参数,必须执行,只能在之后才能实例化AdManager。true为成功false为失败

```
2.static readErrorFileSync:string
```

:读取错误日志

# AdManager

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| adParam | Ms.adParam | true | null | 广告请求字段 |
| adOptions | Ms.adOptions | false | null | 广告配置字段 |
| interationListener | Ms.AdInterationListener | false | null | 广告监测的观测者类 |

```
import {AdManager, Ms} from'ms_sdk'
AdManager(adParam: Ms.adParam, adOptions: Ms.adOptions, interationListener: Ms.AdInterationListener
```

## adParam说明

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| pid | string | true | null | 广告位id |
| type | AD TYPES _ | true | null | 广告位类型 |

## adOptions说明

| 参数名 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| url | string | null | 如果填写,广告关闭时会跳转此url的页面 |
| hideCloseBtn | boolean | false | 是否隐藏关闭按钮 |
| timeCount | number | 5 | 倒计时时间,优先视频时长,没有则取用此时间 |
| autoPlay | boolean | false | 视频素材是否自动播放 |

| 参数名 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| muted | boolean | false | 视频素材是否自动静音 |
| loop | boolean | false | 视频素材是否自动循环 |
| VideoController | VideoController | undefined | 如果提供,在广告素材点击时会执行提供的 VideoController的pause方法,关闭时会执行start方法 。 目的是为了当媒体有自己的视频正在播放,保证用户体 验 。 |
| CloseIconModify | AttributeModifier<ColumnAttribute> | null | 关闭按钮样式修改器 |
| AdvertiserIconModify | AttributeModifier<ColumnAttribute> | null | 广告角标样式修改器 |
| ButtonIconModify | AttributeModifier<ColumnAttribute> | null | 区域文字按钮样式修改器 |
| DownloadInfoModify | AttributeModifier<FlexAttribute> | null | 广告底部下载六要素修改器 |

## interationListener说明

观测类,使用方法:

```
interface EventOptions {
 onAdOpen: Function ...}
...
class AdInteractionListener implements Ms.AdInteractionListener {
 onAdOpen: Function = () => {}
constructor(options: EventOptions) { this.onAdOpen = options.onAdOpen } onStatusChanged(status: AdStatus, adData: Ms.AdData)
...
@State Listener: Ms.AdInteractionListener = new AdInteractionListener({
 onAdOpen: (adData:Ms.AdData) => { ... }})
```

## AdManager属性

1.adData:获取的广告信息

2.adParam:请求的广告参数

3.adOptions:请求的广告配置

4.downloadDialog:下载广告的弹框

5.hasBeenShow:广告是否展示

6.hasBeenClick:广告是否被点击

7.hasBeenOpen:广告是否被打开

8.hasBeenClose:广告是否被关闭

9.hasBeenLoad:广告是否加载

10.hasBeenPlay视频是否正在播放

11.hasBeenMute视频是否静音

12.hasBeenComplete视频是否播放完成

13.hasBeenPause视频是否暂停

```
14.VideoController视频的控制器
```

15.downloadDialog下载类广告弹窗类

16.appInfoDialog下载的app详情弹窗类

17.webDialogh5落地页弹窗类

## AdManager方法

```
1.loadAd(): Promise<void>请求广告
```

2.showAd()展示广告`

3.closeAd()关闭广告

4.clickAd()点击广告

5.setInterval()开始一个计时器

```
6.pauseTimeCount()暂停计时器
7.destroy()销毁广告,closeAd会执行destroy
8.getAdSize(size:SizeOptions)获取广告组件的实际大小
9.getClickEvent(event: TouchEvent)获取广告点击坐标
```

## MsAdListener

```
import { MsAdListener } from'ms_sdk'
@State adState: adState = {
 show: false, load: false,click: false, open: false, fail: false, close: false}
listener: Ms.AdInteractionListener = new MsAdListener({
 onAdOpen: () => this.adState.open = true, onAdLoad: () => this.adState.load = true, onAdShow: () => this.adState.show = true,
```

# 组件说明

## SplashAd

开屏组件

```
import { SplashAd,Ms } from'ms_sdk'
SplashAd({
     adOptions: Ms.AdOptions
     adParam: Ms.AdParam,
     interationListener: Ms.AdInterationListener
})
```

## NativeAd

信息流组件

```
import { NativeAd,Ms } from'ms_sdk'
NativeAd({
    adOptions: Ms.AdOptions,
    adParam: Ms.AdParam,
    interationListener: Ms.AdInterationListener
})
```

## InterstitialAd

插屏组件

```
import { InterstitialAd,Ms } from'ms_sdk'
InterstitialAd({
 adOptions: Ms.AdOptions,
 adParam: Ms.AdParam,
 interationListener: Ms.AdInterationListener
})
```

## BannerAd

横幅组件

```
import { BannerAd,Ms } from'ms_sdk'
BannerAd({
 adOptions: Ms.AdOptions,
 adParam: Ms.AdParam,
 interationListener: Ms.AdInterationListener
})
```

## IncentiveAd

激励广告

```
import { IncentiveAd,Ms } from'ms_sdk'
IncentiveAd({
 adOptions: Ms.AdOptions,
 adParam: Ms.AdParam,
 interationListener: Ms.AdInterationListener
})
```

## PopupadAd

贴片广告

```
import { PopupadAd,Ms } from'ms_sdk'
PopupadAd({
 adOptions: Ms.AdOptions,
 adParam: Ms.AdParam,
 interationListener: Ms.AdInterationListener
})
```

## VideoAd

视频广告

```
import { VideoAd,Ms } from'ms_sdk'
VideoAd({
 adOptions: Ms.AdOptions,
 adParam: Ms.AdParam,
 interationListener: Ms.AdInterationListener
})
```

## 模板自渲染

可以自己实例化AdManager实现组件,也可以采用模板组件并修改样式

所有组件都有四个参数这里拿开屏组件举例:

```
import { SplashAd,Ms } from'ms_sdk'
SplashAd({
    adOptions: Ms.AdOptions,
    adParam: Ms.AdParam,
    interationListener: Ms.AdInterationListener,
    customRender: this.customRender,
    customCloseIcon: this.customCloseIcon,
    customAdvertiserIcon: this.customAdvertiserIcon,
    customButtonIcon: this.customButtonIcon
})
```

说明

| 参数名 | 类型 | 默认值 | 参数 | 说明 |
|---|---|---|---|---|
| customRender | Builder | null | Ms.AdData | 广告素材自渲染 |
| customCloseIcon | Builder | null | Ms.AdData | 关闭按钮自渲染 |
| customAdvertiserIcon | Builder | null | Ms.AdData | 角标自渲染 |
| customButtonIcon | Builder | null | Ms.AdData | 区域按钮文字自渲染 |

使用方法

```
import { SplashAd,Ms } from'ms_sdk'
@Component
struct Parent {
 ....
@Builder customRender(adData?: Ms.AdData) {
     Text(adData?.title) //显示广告标题
         .fontColor(Color.Blue)
}
     ....
builder() {
     SplashAd({
         adOptions: Ms.AdOptions,
         adParam: Ms.AdParam,
         interationListener: Ms.AdInterationListener,
         customRender: this.customRender
     })
}}
```

## 枚举

### ACTION_TYPES 广告位类型

| 广告类型 | 枚举值 | 描述 |
|---|---|---|
| NATIVE | 1 | 原生广告 |
| NATIVE TEMP _ | 2 | 模版原生广告 |
| BANNER | 3 | 横幅广告 |
| SPLASH | 4 | 闪屏广告 |
| INTERSTITIAL | 5 | 插屏广告 |
| POPUPAD | 6 | 弹窗广告 |
| INCENTIVE | 7 | 激励广告 |
| VIDEO | 9 | 视频广告 |
| BAIDU | 11 | 百度广告 |

### ACTION_TYPES广告交互类型

| 交互类型 | 枚举值 | 描述 |
|---|---|---|
| ALL | 1 | 全部类型 |
| LOCAL | 2 | 点击热点 |
| SHAKE | 4 | 摇一摇 |
| TWIST | 8 | 扭一扭 |
| LEFT SWITCH _ | 16 | 向左滑 |
| UP SWITCH _ | 32 | 向上滑 |
| DOUBLE SHAKE _ | 64 | 双向摇动 |
| MULTIP DIRECTION _ | 128 | 多方向滑动 |

## ERROR_CODE 错误代码说明

| 错误代码 | 值 | 描述 |
|---|---|---|
| MSErrorCodeADLoadImageError | -1 | 广告图片加载错误 |
| MSErrorCodeADLoadStyleError | 3 | 广告样式加载错误 |
| MSErrorCodeNOADError | 204 | 没有可用广告 |
| MSErrorCodeADCancleError | 700 | 广告取消错误 |
| MSErrorCodeADMaterialError | 1001 | 广告素材错误 |
| MSErrorCodeADNetWorkError | 3001 | 网络错误 |

| 错误代码 | 值 | 描述 |
|---|---|---|
| MSErrorCodeADTypeError | 4003 | 广告类型错误 |
| MSErrorCodeADLoadVideoError | 6020 | 视频广告加载错误 |
| MSErrorCodeADPidError | 6021 | 广告位 ID 错误 |
| MSErrorCodeADNotValidError | 6022 | 广告无效错误 |
| MSErrorCodeUndefinedError | 6666 | 未定义错误 |
| MSErrorCodeADLoadFailError | 800001 | 广告加载失败 |
| MSErrorCodeADNotSupportSDKError | 800002 | SDK 不支持错误 |
| MSErrorCodeADNotValidParamError | 800003 | 参数无效错误 |
| MSErrorCodeADNotValidClassNameError | 800004 | 类名无效错误 |
| MSErrorCodeADContentParseError | 800005 | 广告内容解析错误 |
