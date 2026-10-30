# TradPlus SDK使用指南

## SDK 版本支持列表

## SDK集成

### 添加仓库到.ohpmrc

-
TradPlus发布在openharmony中,无需单独引用仓库

-
开发者根据集成的平台添加穿山甲或者Sigmob的仓库

      - https://artifact.bytedance.com/repository/byted-ohpm/为穿山甲远程仓库

      - https://ohpm.sigmob.com/repos/ohpm为Sigmob远程仓库

      - 快手SDK需要跟快手商务申请,开启权限后才能获取

      - 腾讯SDK需要跟腾讯商务申请,开启权限后才能获取

如图:可以通过Settings找到项目.ohpm文件位置
```
1
registry=https://ohpm.openharmony.cn/ohpm/,https://artifact.bytedance.com/repos
itory/byted-ohpm/,https://ohpm.sigmob.com/repos/ohpm
```

### 添加依赖

-
在应用中主module的oh-package.json5中引入TradPlus、TradPlus适配adapter和广告平台模

块,配置如下:
```
dependencies: {
"@tradplus/tradplusads": "1.0.1",
"@tradplus/csj_adapter": "file:libs/csj_adapter.har",
"@tradplus/gdt_adapter": "file:libs/gdt_adapter.har",
"@tradplus/sigmob_adapter": "file:libs/sigmob_adapter.har",
"@tradplus/huawei_adapter": "file:libs/huawei_adapter.har",
"@tradplus/ks_adapter": "file:libs/ks_adapter.har",
// sigmob sdk
"@sigmob/adsdk": "1.1.2"
// 穿山甲 SDK
"@csj/openadsdk": "6.7.0",
// 向快手申请获取har包
"ksadsdk": "file:libs/KSAdSDK-3.0.6.har",
// 向腾讯申请获取har包
"@gdt/gdt-union-sdk": "file:libs/GDTUnionSDK-default-release.har"
}
```

-
adapter har包下载地址

| 版本号 | 下载地址 | 更新日期 |
|---|---|---|
| V1.0.0 | adapter下载 | 2025-04-25 |

-
在项目中主module的build-profile.json5中配置动态import的文件和依赖的包名:
```
"buildOption": {
"arkOptions": {
"runtimeOnly":{
"packages": [
"@tradplus/csj_adapter",
"@tradplus/gdt_adapter",
"@tradplus/sigmob_adapter",
"@tradplus/huawei_adapter",
"@tradplus/ks_adapter"
        ]
      }
    }
}
```

-
在工程级别的build-profile.json5中配置,校验导入文件的大小写,以防引用错误
```
1
"buildOption": {"strictMode": {"useNormalizedOHMUrl":true}}
```

-
工程完成依赖接入后,执行ohpm install执行har包的安装

### 权限申请

广告依赖部分设备信息进行转化,需要媒体在module.json5文件中添加以下权限:

-
必选权限

```
{
"name": "ohos.permission.INTERNET"//访问网络
},
{
"name": "ohos.permission.GET_NETWORK_INFO"//访问网络信息
}
```

-
可选权限(均为三方平台要求)
```
{
"name": "ohos.permission.APPROXIMATELY_LOCATION"//模糊地理位置
},
{
"name": "ohos.permission.LOCATION"//获取米级别位置
},
{
"name": "ohos.permission.APP_TRACKING_CONSENT"//获取oaid
}
```

## 初始化SDK

-
在创建任何一个广告位对象前,必须先调用初始化TradPlus SDK。
```
import { TradPlus } from '@tradplus/tradplusads';
if (!TradPlus.isInitialized())
   TradPlus.initSDK("在TradPlus后台创建的应用ID", (error: Error) => {
if (error === undefined) {
// 初始化成功
   } else {
// 初始化失败
   HiAdLog.i("初始失败 error : " + error.name + " , message:" + error.message)
  }
})
```

## 激励视频

## 加载广告

-
创建广告位对象

```
1
``````
lettpReward = newTPReward()
```

-
设置请求广告位ID 
```
1
this.tpReward.setAdUnitID("在TradPlus后台创建的激励广告位ID")
```

-
设置请求监听
```
let loadListener:TPRewardLoadListener = {
  onAdLoaded: (adInfo: TPAdInfo): void => {
// 请求一次广告,有广告加载成功,一轮请求只会返回一次
  },
  onAdLoadFail: (adInfo: TPAdInfo, error: Error): void => {
// 请求一次广告,所有广告加载失败,一轮请求只会返回一次
  },
  onAdStartLoad: (adInfo: TPAdInfo): void => {
// 广告开始加载
  },
  onAdOneLayerStartLoad: (adInfo: TPAdInfo): void => {
// 每层广告开始加载
  },
  onAdBidStart: (adInfo: TPAdInfo): void => {
// Bidding开始
  },
  onAdBidEnd: (adInfo: TPAdInfo, error?: Error | undefined): void => {
// Bidding结束,error == undefined表示Bidding成功,有error表示Bidding失败
  },
  onAdOneLayerLoaded: (adInfo: TPAdInfo): void => {
// 单层广告加载成功
  },
  onAdOneLayerLoadFail: (adInfo: TPAdInfo, error: Error): void => {
// 单层广告加载加载失败
  },
  onAdAllLoaded: (adInfo: TPAdInfo, success: boolean): void => {
```

// 请求一次广告,一轮结束会收到一次回调,success true表示有广告加载成功,false表示

所有广告加载失败

```
  },
  onAdIsLoading: (adInfo: TPAdInfo): void => {
// 一轮请求还没有结束,又发起了一轮请求
  },
}
this.tpReward.loadListener = loadListener
```

-
请求广告
```
1
this.tpReward.load()
```

## 展示广告

-
广告是否加载成功:收到onAdLoaded回调,或者通过isReady()方法检查
```
1
letisReady = await this.tpReward.isReady()
```

-
设置展示监听
```
let showListener:TPRewardShowListener = {
  onAdImpression: (adInfo: TPAdInfo): void => {
// 展示成功
  },
  onAdShowFailed: (adInfo: TPAdInfo): void => {
// 展示失败
  },
  onAdClosed: (adInfo: TPAdInfo): void => {
// 广告关闭
  },
  onAdVideoStart: (adInfo: TPAdInfo): void => {
  },
  onAdVideoEnd: (adInfo: TPAdInfo): void => {
  },
  onAdClicked: (adInfo: TPAdInfo): void => {
// 用户触发点击
  },
  onAdRewarded: (adInfo: TPAdInfo, rewardInfo?: Map<string, string>):void =>{
// 奖励回调
  }
}
this.tpReward.showListener = showListener
```

-
展示广告
```
1
this.tpReward.show(windowStage)
```

## 插屏广告

## 加载广告

-
创建广告位对象
```
1
lettpInterstital = newTPInterstitial()
```

-
设置请求广告位ID 
```
1
this.tpInterstital.setAdUnitID("在TradPlus后台创建的插屏广告位ID")
```

-
设置请求监听
```
let loadListener:TPInterstitialLoadListener = {
  onAdLoaded: (adInfo: TPAdInfo): void => {
// 请求一次广告,有广告加载成功,一轮请求只会返回一次
  },
  onAdLoadFail: (adInfo: TPAdInfo, error: Error): void => {
// 请求一次广告,所有广告加载失败,一轮请求只会返回一次
  },
  onAdStartLoad: (adInfo: TPAdInfo): void => {
// 广告开始加载
  },
  onAdOneLayerStartLoad: (adInfo: TPAdInfo): void => {
// 每层广告开始加载
  },
  onAdBidStart: (adInfo: TPAdInfo): void => {
// Bidding开始
  },
  onAdBidEnd: (adInfo: TPAdInfo, error?: Error | undefined): void => {
// Bidding结束,error == undefined表示Bidding成功,有error表示Bidding失败
  },
  onAdOneLayerLoaded: (adInfo: TPAdInfo): void => {
// 单层广告加载成功
  },
  onAdOneLayerLoadFail: (adInfo: TPAdInfo, error: Error): void => {
// 单层广告加载加载失败
  },
  onAdAllLoaded: (adInfo: TPAdInfo, success: boolean): void => {
```

// 请求一次广告,一轮结束会收到一次回调,success true表示有广告加载成功,false表示

所有广告加载失败

```
  },
  onAdIsLoading: (adInfo: TPAdInfo): void => {
// 一轮请求还没有结束,又发起了一轮请求
  },
}
this.tpInterstital.loadListener = loadListener
```

-
请求广告
```
1
this.tpInterstital.load()
```

## 展示广告

-
广告是否加载成功:收到onAdLoaded回调,或者通过isReady()方法检查
```
1
letisReady = await this.tpInterstital.isReady()
```

-
设置展示监听
```
let showListener:TPInterstitialShowListener = {
  onAdImpression: (adInfo: TPAdInfo): void => {
// 展示成功
  },
  onAdShowFailed: (adInfo: TPAdInfo): void => {
// 展示失败
  },
  onAdClosed: (adInfo: TPAdInfo): void => {
// 广告关闭
  },
  onAdClicked: (adInfo: TPAdInfo): void => {
// 用户触发点击
  }
}
this.tpInterstital.showListener = showListener
```

-
展示广告
```
1
this.tpInterstital.show(windowStage)
```

## 开屏广告

## 加载广告

-
创建广告位对象
```
1
lettpSplash = newTPSplash()
```

-
设置请求广告位ID 
```
1
this.tpSplash.setAdUnitID("在TradPlus后台创建的开屏广告位ID")
```

-
设置请求监听
```
let loadListener:TPSplashLoadListener = {
  onAdLoaded: (adInfo: TPAdInfo): void => {
// 请求一次广告,有广告加载成功,一轮请求只会返回一次
  },
  onAdLoadFail: (adInfo: TPAdInfo, error: Error): void => {
// 请求一次广告,所有广告加载失败,一轮请求只会返回一次
  },
  onAdStartLoad: (adInfo: TPAdInfo): void => {
// 广告开始加载
  },
  onAdOneLayerStartLoad: (adInfo: TPAdInfo): void => {
// 每层广告开始加载
  },
  onAdBidStart: (adInfo: TPAdInfo): void => {
// Bidding开始
  },
  onAdBidEnd: (adInfo: TPAdInfo, error?: Error | undefined): void => {
// Bidding结束,error == undefined表示Bidding成功,有error表示Bidding失败
  },
  onAdOneLayerLoaded: (adInfo: TPAdInfo): void => {
// 单层广告加载成功
  },
  onAdOneLayerLoadFail: (adInfo: TPAdInfo, error: Error): void => {
// 单层广告加载加载失败
  },
  onAdAllLoaded: (adInfo: TPAdInfo, success: boolean): void => {
```

// 请求一次广告,一轮结束会收到一次回调,success true表示有广告加载成功,false表示

所有广告加载失败

```
  },
  onAdIsLoading: (adInfo: TPAdInfo): void => {
// 一轮请求还没有结束,又发起了一轮请求
  },
}
this.tpSplash.loadListener = loadListener
```

-
请求广告
```
1
this.tpSplash.load(this.getUIContext())
```

## 展示广告

-
广告是否加载成功:收到onAdLoaded回调,或者通过isReady()方法检查
```
1
letisReady = await this.tpSplash.isReady()
```

-
设置展示监听
```
let showListener:TPSplashShowListener = {
  onAdImpression: (adInfo: TPAdInfo): void => {
// 展示成功
  },
  onAdShowFailed: (adInfo: TPAdInfo): void => {
// 展示失败
  },
  onAdClosed: (adInfo: TPAdInfo): void => {
// 广告关闭
  },
  onAdClicked: (adInfo: TPAdInfo): void => {
// 用户触发点击
  }
}
this.tpSplash.showListener = showListener
```

-
展示广告
```
1
this.tpSplash.show(windowStage)
```

## 原生广告

## 加载广告

-
创建广告位对象
```
1
lettpNative = newTPNative()
```

-
设置请求广告位ID 
```
1
this.tpNative.setAdUnitID("在TradPlus后台创建的原生广告位ID")
```

-
设置请求监听
```
let loadListener:TPNativeLoadListener = {
  onAdLoaded: (adInfo: TPAdInfo): void => {
// 请求一次广告,有广告加载成功,一轮请求只会返回一次
  },
  onAdLoadFail: (adInfo: TPAdInfo, error: Error): void => {
// 请求一次广告,所有广告加载失败,一轮请求只会返回一次
  },
  onAdStartLoad: (adInfo: TPAdInfo): void => {
// 广告开始加载
  },
  onAdOneLayerStartLoad: (adInfo: TPAdInfo): void => {
// 每层广告开始加载
  },
  onAdBidStart: (adInfo: TPAdInfo): void => {
// Bidding开始
  },
  onAdBidEnd: (adInfo: TPAdInfo, error?: Error | undefined): void => {
// Bidding结束,error == undefined表示Bidding成功,有error表示Bidding失败
  },
  onAdOneLayerLoaded: (adInfo: TPAdInfo): void => {
// 单层广告加载成功
  },
  onAdOneLayerLoadFail: (adInfo: TPAdInfo, error: Error): void => {
// 单层广告加载加载失败
  },
  onAdAllLoaded: (adInfo: TPAdInfo, success: boolean): void => {
```

// 请求一次广告,一轮结束会收到一次回调,success true表示有广告加载成功,false表示

所有广告加载失败

```
  },
  onAdIsLoading: (adInfo: TPAdInfo): void => {
// 一轮请求还没有结束,又发起了一轮请求
  },
}
this.tpNative?.loadListener = loadListener
```

-
请求广告
```
1
this.tpNative.load(uiContext)
```

## 展示广告

-
广告是否加载成功:收到onAdLoaded回调,或者通过isReady()方法检查
```
1
letisReady = await this.tpNative?.isReady()
```

-
设置展示监听
```
let showListener:TPNativeShowListener = {
  onAdImpression: (adInfo: TPAdInfo): void => {
// 展示成功
  },
  onAdShowFailed: (adInfo: TPAdInfo): void => {
// 展示失败
  },
  onAdClosed: (adInfo: TPAdInfo): void => {
// 广告关闭
  },
  onAdClicked: (adInfo: TPAdInfo): void => {
// 用户触发点击
  }
}
this.tpNative.showListener = showListener
```

### 自渲染展示

1.创建Class TPNodeController继承并实现NodeController
```
1
lettpNodeController = newTPNodeController()
```

2.通过tpNative获取自渲染类型素材对象TPNativeView
```
1
consttpNativeView = await this.tpNative.getTPNativeAd(this.getUIContext())
```

3.将tpNative和tpNativeView传给TPNodeController,用于添加组件和注册监听
```
1
this.tpNodeController?.show(this.getUIContext(),this.tpNative,this.tpNativeView
)
```

4.TPNodeController中构建广告组件,在封装的广告组件AdComponent中绘制布局并注册监听
```
//点击Id集合,缺少注册将无法点击
@Stateprivate clickViewIds: TPNativeArrayList<string> = new
TPNativeArrayList();
// 广告布局根节点Id
private rootComponentId: string = util.generateRandomUUID()
  build() {
    Column() {
      Row() {
        Row() {
// icon
          Image(this.tpNativeView?.iconImageUrl)
            .height(32)
            .width(32)
            .borderRadius(5)
            .margin({ right: 5 })
            .id(this.clickViewIds?.addAdId(util.generateRandomUUID()))//设置组件
```

Id,需要全局保证唯一性,涉及计费

```
            .onClick((e: ClickEvent) => {
// 点击转化
this.tpNative?.getClickHandler(getContext(this) as
common.UIAbilityContext, e)
            })
// 描述内容
          Text(this.tpNativeView!.subTitle)
            .fontSize(12)
            .textAlign(TextAlign.Start)
            .maxLines(2)
            .textOverflow({ overflow: TextOverflow.Ellipsis })
            .id(this.clickViewIds?.addAdId(util.generateRandomUUID()))//设置组件
```

Id,需要全局保证唯一性,涉及计费

```
            .onClick((e: ClickEvent) => {
// 点击转化
this.tpNative?.getClickHandler(getContext(this) as
common.UIAbilityContext, e)
            })
        }
        .height(35)
        .width("85%")
        .justifyContent(FlexAlign.Start);
      }
      .justifyContent(FlexAlign.SpaceBetween)
      .height(35)
      .width("100%")
      .padding({ left: 10, right: 10, bottom: 4 })
      Stack({ alignContent: Alignment.BottomStart }) {
if (this.tpNativeView?.mainImageUrl) {
// 大图是图片
this.buildImageLayout()
        } else {
// 大图是视频
          NodeContainer(this.tpNativeView?.videoNodeController)
        }
      }.height(200)
      Row() {
// 标题
        Text(this.tpNativeView?.title)
          .fontSize(12)
          .textAlign(TextAlign.Center)
          .id(this.clickViewIds?.addAdId(util.generateRandomUUID()))//设置组件
```

Id,需要全局保证唯一性,涉及计费

```
          .onClick((e: ClickEvent) => {
// 点击转化
this.tpNative?.getClickHandler(getContext(this) as
common.UIAbilityContext, e)
          })
// CTA
        Button(this.tpNativeView?.callToAction, { type: ButtonType.Normal })
          .fontSize(12)
          .borderRadius(5)
          .id(this.clickViewIds?.addAdId(util.generateRandomUUID()))//设置组件
```

Id,需要全局保证唯一性,涉及计费

```
          .onClick((e: ClickEvent) => {
// 点击转化
this.tpNative?.getClickHandler(getContext(this) as
common.UIAbilityContext, e)
          })
      }
      .justifyContent(FlexAlign.SpaceBetween)
      .height(35)
      .width("100%")
      .padding({
        top: 5,
        bottom: 5,
        left: 10,
```

5.通过NodeContainer容器承载TPNodeController进行广告的展示
```
1
NodeContainer(this.tpNodeController)
```

### 模版展示

-
三方平台后台配置的是模版类型的广告位ID

直接通过NodeContainer容器承载tpNative进行广告的展示
```
1
NodeContainer(this.tpNative)
```

## 横幅广告

## 加载广告

-
创建广告位对象
```
1
lettpBanner = newTPBanner()
```

-
设置请求广告位ID
```
1
this.tpBanner.setAdUnitID("在TradPlus后台创建的横幅广告位ID")
```

-
设置请求监听
```
let loadListener:TPBannerLoadListener = {
  onAdLoaded: (adInfo: TPAdInfo): void => {
// 请求一次广告,有广告加载成功,一轮请求只会返回一次
  },
  onAdLoadFail: (adInfo: TPAdInfo, error: Error): void => {
// 请求一次广告,所有广告加载失败,一轮请求只会返回一次
  },
  onAdStartLoad: (adInfo: TPAdInfo): void => {
// 广告开始加载
  },
  onAdOneLayerStartLoad: (adInfo: TPAdInfo): void => {
// 每层广告开始加载
  },
  onAdBidStart: (adInfo: TPAdInfo): void => {
// Bidding开始
  },
  onAdBidEnd: (adInfo: TPAdInfo, error?: Error | undefined): void => {
// Bidding结束,error == undefined表示Bidding成功,有error表示Bidding失败
  },
  onAdOneLayerLoaded: (adInfo: TPAdInfo): void => {
// 单层广告加载成功
  },
  onAdOneLayerLoadFail: (adInfo: TPAdInfo, error: Error): void => {
// 单层广告加载加载失败
  },
  onAdAllLoaded: (adInfo: TPAdInfo, success: boolean): void => {
```

// 请求一次广告,一轮结束会收到一次回调,success true表示有广告加载成功,false表示

所有广告加载失败

```
  },
  onAdIsLoading: (adInfo: TPAdInfo): void => {
// 一轮请求还没有结束,又发起了一轮请求
  },
}
this.tpBanner.loadListener = loadListener
```

-
请求广告
```
1
this.tpBanner.load(uiContext)
```

## 展示广告

-
广告是否加载成功:收到onAdLoaded回调,或者通过isReady()方法检查
```
1
letisReady = await this.tpBanner.isReady()
```

-
设置展示监听
```
let showListener:TPBannerShowListener = {
  onAdImpression: (adInfo: TPAdInfo): void => {
// 展示成功
  },
  onAdShowFailed: (adInfo: TPAdInfo): void => {
// 展示失败
  },
  onAdClosed: (adInfo: TPAdInfo): void => {
// 广告关闭
  },
  onAdClicked: (adInfo: TPAdInfo): void => {
// 用户触发点击
  }
}
this.tpBanner?.showListener = showListener
```

-
自动展示:通过NodeContainer容器承载tpBanner进行广告的展示
```
1
NodeContainer(this.tpBanner)
```
