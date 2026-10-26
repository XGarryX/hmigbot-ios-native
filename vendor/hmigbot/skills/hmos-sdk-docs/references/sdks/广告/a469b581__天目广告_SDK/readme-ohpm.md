> 来源: ohpm 中央仓 README(T1 信源) | 包: `@admobile/tianmu` | ohpm 最新版: 1.1.3 | 抓取: 2026-07-16
> 注意: 版本可能比市场快照新,以此为准时核对 CHANGELOG

# 天目 Ads SDK HarmonyOS 版接入文档 V1.1.3

```
SDK名称: 天目 Ads SDK
开发者: 杭州艾狄墨搏信息服务有限公司
更新日期: 2025-12-12
功能介绍: 天目Ads SDK是一款全面的 APP 广告变现解决方案,支持多种广告格式,包括横幅、插屏和视频广告。它具有精准和详细的数据分析功能,帮助开发者优化广告投放和提升收益。
```

[SDK 下载地址](https://doc.admobile.top/AndroidSDK/Tianmu%E9%B8%BF%E8%92%99har.zip)

[查看接入文档](https://doc.admobile.top/ssp/pages/tmsdkhm/)

[隐私政策](https://www.admobile.top/privacyPolicy.html)

[合规指引](https://doc.admobile.top/ssp/pages/tianmu_compliance/)

[用户协议](https://doc.admobile.top/ssp/pages/contract/)

## 1. 概述

尊敬的开发者朋友,欢迎您使用天目 Ads SDK。通过本文档,您可以快速完成广告SDK的集成。

### 2. 支持的广告类型

<table>
  <tr>
    <th style="width:150px">类型</th>
    <th>简介</th>
    <th>适用场景</th>
  </tr>
  <tr>
    <td><a href="#ad_splash">开屏广告</a></td>
    <td>开屏广告以APP启动作为曝光时机的模板广告,需要将开屏广告视图添加到承载的广告容器中,提供5s可感知广告展示</td>
    <td>APP启动界面常会使用开屏广告</td>
  </tr>
  <tr>
    <td><a href="#ad_banner">Banner广告</a></td>
    <td>Banner广告是横向贯穿整个可视页面的模板广告,需要将Banner广告视图添加到承载的广告容器中</td>
    <td>应用程序顶部、中部或底部占据一个位置的矩形图片</td>
  </tr>
  <tr>
    <td><a href="#ad_native_express">信息流模板广告</a></td>
    <td>信息流模板广告,支持上文下图、下图上文、左图右文、右图左文、纯图</td>
    <td>信息流列表,轮播控件,固定位置都是较为适合</td>
  </tr>
  <tr>
    <td><a href="#ad_native_express">信息流自渲染广告</a></td>
    <td>信息流自渲染广告,可自行设计样式,以满足不同的样式需求</td>
    <td>信息流列表,轮播控件,固定位置都是较为适合</td>
  </tr>
  <tr>
    <td><a href="#ad_interstitial">插屏广告</a></td>
    <td>插屏广告是移动广告的一种常见形式,在应用流程中弹出,当应用展示插屏广告时,用户可以选择点击广告,访问其目标网址,也可以将其关闭并返回应用</td>
    <td>在应用执行流程的自然停顿点,适合投放这类广告</td>
  </tr>
  <tr>
    <td><a href="#ad_reward">激励视频广告</a></td>
    <td>将短视频融入到APP场景当中,用户观看短视频广告后可以给予一些应用内奖励</td>
    <td>常出现在游戏的复活、任务等位置,或者网服类APP的一些增值服务场景</td>
  </tr>
</table>

## 2. 安装命令

### 2.1 安装命令

```typescript

ohpm install @admobile/tianmu
  
  ```

```

### 2.1 权限申请

  <table>
  <tr>
    <th style="width:150px">权限名称</th>
    <th>权限说明</th>
    <th>使用目的</th>
  </tr>
  <tr>
    <td>ohos.permission.INTERNET</td>
    <td>允许使用Internet网络</td>
    <td>允许使用Internet网络</td>
  </tr>
  <tr>
    <td>ohos.permission.GET_NETWORK_INFO</td>
    <td>允许应用获取数据网络信息</td>
    <td>允许应用获取数据网络信息</td>
  </tr>
  <tr>
    <td>ohos.permission.APP_TRACKING_CONSENT</td>
    <td>允许应用读取开放匿名设备标识符</td>
    <td>允许应用读取开放匿名设备标识符</td>
  </tr>
  <tr>
    <td>ohos.permission.APPROXIMATELY_LOCATION</td>
    <td>允许应用获取设备模糊位置信息</td>
    <td>允许应用获取设备模糊位置信息</td>
  </tr>
</table>

## 3. 示例代码

### 3.1 SDK初始化

在适当位置进行SDK的初始化

#### 3.1.1 初始化主要 API

#### Tianmu.Sdk 初始化

| 方法名                                     | 入参                                 | 介绍                                                                              |
|-----------------------------------------|------------------------------------|---------------------------------------------------------------------------------|
| setDebug(isDebug: boolean)              | isDebug: boolean                   | 设置是否是Debug模式。参数说明:debug(true:开启,false:关闭, 默认:false)开发阶段以及提交测试阶段可设置为true,方便异常排查。 |
| setInitListener(listener: InitListener) | listener: InitListener             | 初始化状态回调。                                                                        |
| init(context: Context, appid: string)   | context: Context appid: string | 初始化方法。参数说明: context(初始化SDK的上下文对象) appid(应用初始化id)                        |
| setOaid(oaid: string)                   | oaid: string                       | 设置oaid。参数说明:oaid(oaid参数)。                                                       |
| isCanReadNetworkInfo(b: boolean)        | b: boolean                         | 是否可读取网络信息。参数说明: b(true:允许,false:不允许,默认允许)。                                  |
| isCanReadLocation(b: boolean)           | b: boolean                         | 是否可读取位置信息。参数说明: b(true:允许,false:不允许,默认允许)。                                  |
| setPersonalizedAdEnabled(b: boolean)    | b: boolean                         | 设置个性化开关。参数说明: b(true:开启,false:关闭,默认开启)。                                     |

#### InitListener 初始化监听

| 方法名                                 | 入参 | 介绍                                      |
|-------------------------------------|----|-----------------------------------------|
| onSuccess()                         |    | 初始化成功。                                  |
| onFailed(code: number, msg: string) |    | 初始化失败。参数说明: code(错误码) msg(错误信息) |

#### 3.1.2 初始化接入示例

```typescript
// 设置debug状态,开发阶段建议设置true
Tianmu.Sdk.setDebug(true)
const listener: InitListener = {
  onFailed(code: number, msg: string) {
    ...
  },

  onSuccess() {
    ...
  }

}
// 设置初始化状态监听
Tianmu.Sdk.setInitListener(listener)
// 初始化广告
Tianmu.Sdk.init(getContext(this), 'appid')
```

### 3.2 广告获取

#### 3.2.1 广告获取主要 API

#### Tianmu.AdLoader 广告加载器

| 方法名                                                                                                                         | 入参                                                                                                           | 介绍                                                                                                     |
|-----------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------|
| loadAd( adParam: AdRequestParams, listener: AdLoadListener )                                                                  | adParam: AdRequestParams, listener: AdLoadListener                                                      | 广告加载。参数说明: adParam(广告位配置信息)、 listener(广告获取回调)。                                                 |
| showAd( uiContext: UIContext, adInfo: AdInfo)        | uiContext: UIContext, adInfo: AdInfo, adDisplayOptions: AdDisplayOptions, adStatusListener: AdStatusListener | 插屏、激励视频广告展示方法。参数说明: uiContext: uiContext上下文对象; adInfo: 广告对象; |

#### AdLoadListener 广告加载监听

| 方法名                                 | 入参                        | 介绍                                       |
|-------------------------------------|---------------------------|------------------------------------------|
| onSuccess(ads: Array\<AdInfo\>)     | ads: Array\<AdInfo\>      | 广告获取成功。参数说明:ads(广告数组)                    |
| onFailed(code: number, msg: string) | code: number, msg: string | 广告获取失败。参数说明: code(错误码) msg(错误信息) |

#### AdRequestParams 广告请求参数配置

| 参数名          | 介绍              |
|--------------|-----------------|
| adId         | 广告位id,广告后台获取    |
| adType       | 广告位类型,可参考AdType |
| adCount      | 广告获取数量,目前仅支持1个  |
| adWidth      | 广告宽度            |
| adHeight     | 广告高度            |
| muted        | 是否静音            |
| isAutoPlay   | 是否自动播放          |
| isShowShadow | 是否自动播放          |

#### AdType 广告类型

| 参数名               | 介绍     |
|-------------------|--------|
| SPLASH_AD         | 开屏     |
| BANNER_AD         | banner |
| NATIVE_EXPRESS_AD | 信息流模版  |
| INTERSTITIAL_AD   | 插屏     |
| REWARD_AD         | 激励视频   |

#### AdInfo 广告对象

| 方法名                                                     | 入参                                 | 介绍                                               |
|---------------------------------------------------------|------------------------------------|--------------------------------------------------|
| getPrice()                                              |                                    | 广告价格。                                            |
| getExpireSeconds()                                      |                                    | 广告过期剩余时间。                                        |
| isAvailable()                                           |                                    | 广告是否可用。可用:true,不可用:false                         |
| getAdComponent()                                        |                                    | 获取广告视图。(仅开屏、横幅、信息流模版支持)                          |
| setAdStatusListener(adStatusListener: AdStatusListener) |                                    | 设置广告状态监听。                                        |
| sendWinNotice()                                         |                                    | 竞价成功上报。                                          |
| sendLossNotice(price: number, reason: number)           | price: number, reason: number | 竞价失败上报。 参数说明: price(竞赢方价格)、 reason(竞败原因) |

#### 3.2.2 广告请求示例

```typescript
@Entry
@Component
struct SplashPage
{
  @State adInfo?: AdInfo = undefined
  ...
  // 普通广告请求参数
  adParams: AdRequestParams = {
    adId: '广告位id',
    adType: AdType.SPLASH_AD,
    adCount: 1,
  }
  ...

  loadAd() {
      // 广告请求回调监听
    const adLoaderListener: AdLoadListener = {
      onFailed: (code: number, msg: string) => {
        console.log(TAG, 'onAdError code :: ' + code + ' msg :: ' + msg)
      },
    
      onSuccess: (ads: Array<AdInfo>) => {
        this.adInfo = ads[0]
      }
    }
    
    // 创建AdLoader广告对象
    const load: Tianmu.AdLoader = new Tianmu.AdLoader();
    load.loadAd(this.adParams, adLoaderListener)
  }
  
}
```

### <a name="ad_splash">3.3 开屏广告</a>

开屏广告建议在闪屏页进行展示,开屏广告的宽度和高度取决于容器的宽高,会撑满广告容器。

#### 3.3.1 开屏广告接入示例

```typescript
@Entry
@Component
struct SplashPage
{
    @State adInfo?: AdInfo = undefined
    @State splashAdComponent: NodeController | undefined = undefined
    ...
    
    build() {
      ...
      if (this.splashAdComponent) {
        NodeContainer(this.splashAdComponent)
      }
      ...
    }

    showAd() {
      if (this.adInfo == undefined) {
        promptAction.showToast({
          message: '没有广告填充',
          duration: 2000
        });
        return
      }
    
      const onStatusChanged: AdStatusListener = {
        onStatusChanged: (status: string, ad: AdInfo, data: string) => {
          switch (status) {
            case AdStatus.AD_SHOW:
              console.log(TAG, 'onAdShow')
              break
            case AdStatus.AD_CLICK:
              console.log(TAG, 'onAdClick')
              break
            case AdStatus.AD_SKIP:
              console.log(TAG, 'onAdSkip')
              break
            case AdStatus.AD_CLOSE:
              console.log(TAG, 'onAdClose')
              this.hideAd()
              break
            case AdStatus.AD_RENDER_FAILED:
              console.log(TAG, 'onAdRenderFailed msg :: ' + data)
              this.hideAd()
              break
          }
        }
      }
    
      this.adInfo.setAdStatusListener(onStatusChanged)
    
      this.splashAdComponent = this.adInfo.getAdComponent()
    }
    
    hideAd() {
      this.splashAdComponent = undefined
      this.adInfo = undefined
    }
  
}
```

### <a name="ad_banner">3.4 横幅广告</a>

Banner横幅广告建议放置在 **固定位置**。

#### 3.4.1 横幅广告接入示例

```typescript
@Entry
@Component
struct BannerPage
{
  @State adInfo?: AdInfo = undefined
  @State bannerAdComponent: NodeController | undefined = undefined
  ...

  build() {
    ...
    if (this.bannerAdComponent) {
      NodeContainer(this.bannerAdComponent)
          .alignRules({
            top: { anchor: 'titleBar', align: VerticalAlign.Bottom },
          })
          .width('100%')
    }
    ...
  }

  ...
  
  showAd() {
    if (this.adInfo == undefined) {
    promptAction.showToast({
      message: '没有广告填充',
      duration: 2000
    });
    return
    }
    
    this.adInfo.setAdStatusListener({
    onStatusChanged: (status: string, ad: AdInfo, data: string) => {
      switch (status) {
        case AdStatus.AD_SHOW:
          console.log(TAG, 'onAdShow')
          break
        case AdStatus.AD_CLICK:
          console.log(TAG, 'onAdClick')
          break
        case AdStatus.AD_CLOSE:
          console.log(TAG, 'onAdClose')
          this.hideAd()
          break
        case AdStatus.AD_RENDER_FAILED:
          console.log(TAG, 'onAdRenderFailed msg :: ' + data)
          this.hideAd()
          break
      }
    }
    })
    
    this.bannerAdComponent = this.adInfo.getAdComponent()
    
  }
    
  hideAd() {
    this.bannerAdComponent = undefined
    this.adInfo = undefined
  }
  
}
```

### <a name="ad_native_express">3.5 信息流模版广告</a>

信息流列表,轮播控件,固定位置都是较为适合

#### 3.5.1 信息流模版广告接入示例

```typescript
@Entry
@Component
struct NativeExpressPage {

  @State itemList: Array<object> = []

  aboutToAppear(): void {
    this.getData()
  }

  build() {
    RelativeContainer() {
      List() {
        ForEach(this.itemList, (item: object, index: number) => {
          ListItem() {
            if (item instanceof AdInfo) {
              NodeContainer(item.getAdComponent()).width("100%")
            } else {
              Text('测试数据' + index)
                .width('100%')
                .height('200')
            }
          }
          .height('undefined')
        })
      }
      .width('100%')
        .alignRules({
          'top': { 'anchor': 'titleBar', 'align': VerticalAlign.Bottom },
          'bottom': { 'anchor': '__container__', 'align': VerticalAlign.Bottom }
        })
    }
    .height('100%')
      .width('100%')
      .backgroundColor('#fff3f3f3')
  }

  getData() {
    // 广告请求回调监听
    const adLoaderListener: AdLoadListener = {
      onFailed: (code: number, msg: string) => {
        console.log(TAG, 'onAdError code :: ' + code + ' msg :: ' + msg)
      },

      onSuccess: (ads: Array<AdInfo>) => {
        console.log(TAG, 'onAdReceive price :: ' + ads[0].getPrice())
        for (let index = 0; index < ads.length; index++) {
          const ad = ads[index]
          ad.setAdStatusListener({
            onStatusChanged: (status: string, ad: AdInfo, data: string) => {
              switch (status) {
                case AdStatus.AD_SHOW:
                  console.log(TAG, 'onAdShow')
                  break
                case AdStatus.AD_CLICK:
                  console.log(TAG, 'onAdClick')
                  break
                case AdStatus.AD_CLOSE:
                  console.log(TAG, 'onAdClose')
                  this.itemList.splice(this.itemList.indexOf(ad))
                  break
                case AdStatus.AD_RENDER_FAILED:
                  console.log(TAG, 'onAdRenderFailed msg :: ' + data)
                  this.itemList.splice(this.itemList.indexOf(ad))
                  break
              }
            }
          })
          this.itemList.push(ad)
        }
        for (let index = 0; index < 10; index++) {
          this.itemList.push(new String('1'))
        }
      }
    }

    // 创建AdLoader广告对象
    const load: Tianmu.AdLoader = new Tianmu.AdLoader();
    load.loadAd(this.adParams, adLoaderListener)
  }
}
```

### <a name="ad_native_express">3.6 信息流自渲染广告</a>

信息流列表,轮播控件,固定位置都是较为适合

#### 3.6.1 信息流自渲染广告接入示例

```typescript
@Entry
@Component
struct NativeFeedPage {

  @State itemList: Array<object> = []

  ...

  aboutToAppear(): void {
    this.getData()
  }

  build() {
    RelativeContainer() {
      TitleComponent({
        title: '信息流模版广告'
      })
        .id('titleBar')

      List() {
        ForEach(this.itemList, (item: object, index: number) => {
          ListItem() {
            if (item instanceof AdInfo) {
              if (item.isExpressAd()) {
                NodeContainer(item.getAdComponent()).width("100%")
              } else {
                this.buildAdLayout(item);
              }
            } else {
              Text('测试数据' + index)
                .width('100%')
                .height('200')
            }
          }
          .height('undefined')
        })
      }
      .width('100%')
      .alignRules({
        'top': { 'anchor': 'titleBar', 'align': VerticalAlign.Bottom },
        'bottom': { 'anchor': '__container__', 'align': VerticalAlign.Bottom }
      })
    }
    .height('100%')
    .width('100%')
    .backgroundColor('#fff3f3f3')
  }

  getData() {
    // 广告请求回调监听
    const adLoaderListener: AdLoadListener = {
      onFailed: (code: number, msg: string) => {
        console.log(TAG, 'onAdError code :: ' + code + ' msg :: ' + msg)
        this.mockData()
      },

      onSuccess: (ads: Array<AdInfo>) => {
        console.log(TAG, 'onAdReceive price :: ' + ads[0].getPrice())
        for (let index = 0; index < ads.length; index++) {
          const ad = ads[index]
          ad.setAdStatusListener({
            onStatusChanged: (status: string, ad: AdInfo, data: string) => {
              switch (status) {
                case AdStatus.AD_SHOW:
                  console.log(TAG, 'onAdShow')
                  break
                case AdStatus.AD_CLICK:
                  console.log(TAG, 'onAdClick')
                  break
                case AdStatus.AD_CLOSE:
                  console.log(TAG, 'onAdClose')
                  this.itemList.splice(this.itemList.indexOf(ad))
                  break
                case AdStatus.AD_RENDER_FAILED:
                  console.log(TAG, 'onAdRenderFailed msg :: ' + data)
                  this.itemList.splice(this.itemList.indexOf(ad))
                  break
              }
            }
          })
          this.itemList.push(ad)
        }
        this.mockData()
      }
    }

    // 创建AdLoader广告对象
    const load: Tianmu.AdLoader = new Tianmu.AdLoader();
    load.loadAd(this.adParams, adLoaderListener)
  }

  mockData() {
    for (let index = 0; index < 10; index++) {
      this.itemList.push(new String('1'))
    }
  }

  @Builder
  private buildAdLayout(ad: AdInfo, clickViewIds: AdIdArrayList<string> = new AdIdArrayList(),
    creativeViewIds: AdIdArrayList<string> = new AdIdArrayList(), rootComponentId: string = util.generateRandomUUID()) {
    Column() {
      Row() {
        Row() {
          //广告主Icon
          Image(ad.getIcon())
            .height(32)
            .width(32)
            .borderRadius(5)
            .margin({ right: 5 })
            .id(creativeViewIds.addAdId(util.generateRandomUUID())) //设置组件Id,需要全局保证唯一性,涉及计费

          //描述内容
          Text(ad.getDesc())
            .fontSize(12)
            .textAlign(TextAlign.Start)
            .maxLines(2)
            .textOverflow({ overflow: TextOverflow.Ellipsis })
            .id(creativeViewIds.addAdId(util.generateRandomUUID())) //设置组件Id,需要全局保证唯一性,涉及计费
        }
        .height(35)
        .width("85%")
        .justifyContent(FlexAlign.Start);

        Row() {
          Image($r('app.media.icon_close')).onClick(() => {
            // 关闭操作
          })
            .height(16)
            .width(16)
            .borderRadius(8)
        }.height(35)
        .width("10%")
        .justifyContent(FlexAlign.End);
      }
      .justifyContent(FlexAlign.SpaceBetween)
      .height(35)
      .width("100%")
      .padding({ left: 10, right: 10, bottom: 4 })

      //视频|图片区域
      Stack({ alignContent: Alignment.BottomStart }) {

        // 广告view
        if (ad.isVideo()) {
          NodeContainer(ad.getVideoComponent())
        } else if (ad.getImage()) {
          this.buildImageLayout(ad, creativeViewIds)
        }

        // 广告logo
        Flex({ direction: FlexDirection.Column, justifyContent: FlexAlign.End }) { // 子组件在容器主轴上行布局
          Image(ad.getAdLogo())
            .height(20)
            .width(30)
            .objectFit(ImageFit.Auto)
        }.width("100%")
        .height(20)

      }.height(200)

      Row() {
        //标题
        Text(ad.getTitle())
          .fontSize(12)
          .textAlign(TextAlign.Center)
          .id(creativeViewIds.addAdId(util.generateRandomUUID())) //设置组件Id,需要全局保证唯一性,涉及计费

        //创意按钮
        Button(ad.getButtonText())
          .fontSize(12)
          .borderRadius(5)
          .id(clickViewIds.addAdId(util.generateRandomUUID()))
      }
      .justifyContent(FlexAlign.SpaceBetween)
      .height(35)
      .width("100%")
      .padding({
        top: 5,
        bottom: 5,
        left: 10,
        right: 10
      })
    }
    .backgroundColor("#08000000")
    .id(rootComponentId) //设置广告容器组件rootId
    .onAppear(() => {
      //注册计费事件
      ad.registerViewForInteraction(rootComponentId, this.getUIContext(), clickViewIds, creativeViewIds)
    })
  }

  /**
   * 图片类型广告布局
   * @param ad
   */
  @Builder
  buildImageLayout(ad: AdInfo, creativeViewIds: AdIdArrayList<string>) {
    Image(ad.getImage())
      .objectFit(ImageFit.Contain)
      .backgroundColor('#000000')
      .id(creativeViewIds.addAdId(util.generateRandomUUID())) //设置组件Id,需要全局保证唯一性,涉及计费
  }
}
```

### <a name="ad_interstitial">3.7 插屏广告示例</a>

插屏广告是移动广告的一种常见形式,在应用流程中弹出,当应用展示插屏广告时,用户可以选择点击广告,也可以将其关闭并返回应用。

#### 3.7.1 插屏广告主要 API

#### Tianmu.AdLoader 广告加载器

| 方法名                                                                                                                         | 入参                                                                                                           | 介绍                                                                                                     |
|-----------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------|
| showAd( uiContext: UIContext, adInfo: AdInfo, adDisplayOptions: AdDisplayOptions, adStatusListener: AdStatusListener )        | uiContext: UIContext, adInfo: AdInfo | 插屏、激励视频广告展示方法。参数说明: uiContext: uiContext上下文对象; adInfo: 广告对象; |

#### 3.7.2 插屏广告接入示例

```typescript
@Entry
@Component
struct InterstitialPage
{
  private adLoader?: Tianmu.AdLoader
  private adInfo?: AdInfo
  private adDisplayOptions: AdDisplayOptions = {
      muted: false,
  }
  ...

  build() {
      ...
  }

  showAd() {
      if (this.adInfo === undefined || this.adInfo === null) {
        promptAction.showToast({
          message: '没有广告填充',
          duration: 2000
        });
        return
      }
      if (this.adLoader === undefined) {
        return
      }
    
      const adStatusListener: AdStatusListener = {
        onStatusChanged: (status: string, ad: AdInfo, data: string) => {
          switch (status) {
            case AdStatus.AD_SHOW:
              console.log(TAG, 'onAdShow')
              break
            case AdStatus.AD_CLICK:
              console.log(TAG, 'onAdClick')
              break
            case AdStatus.AD_REWARD:
              console.log(TAG, 'onAdReward')
              break
            case AdStatus.AD_CLOSE:
              console.log(TAG, 'onAdClose')
              this.hideAd()
              break
            case AdStatus.AD_RENDER_FAILED:
              console.log(TAG, 'onAdRenderFailed msg :: ' + data)
              this.hideAd()
              break
          }
        }
      }
      this.adInfo.setAdStatusListener(adStatusListener)
      this.adLoader.showAd(this.getUIContext(), this.adInfo)
  }
  
}
```

### <a name="ad_reward">3.8 激励视频广告示例</a>

将短视频融入到APP场景当中,用户观看短视频广告后可以给予一些应用内奖励。

#### 3.8.1 激励视频广告主要 API

#### Tianmu.AdLoader 广告加载器

| 方法名                                                                                                                         | 入参                                                                                                           | 介绍                                                                                                     |
|-----------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------|
| showAd( uiContext: UIContext, adInfo: AdInfo, adDisplayOptions: AdDisplayOptions, adStatusListener: AdStatusListener )        | uiContext: UIContext, adInfo: AdInfo | 插屏、激励视频广告展示方法。参数说明: uiContext: uiContext上下文对象; adInfo: 广告对象; |

#### 3.8.2 激励视频广告接入示例

```typescript
@Entry
@Component
struct RewardPage
{
  private adInfo?: AdInfo
  private adLoader?: Tianmu.AdLoader
  private adDisplayOptions: AdDisplayOptions = {
      muted: false
  }
  ...

  build() {
      ...
  }

  showAd() {
      if (this.adInfo === undefined || this.adInfo === null) {
        promptAction.showToast({
          message: '没有广告填充',
          duration: 2000
        });
        return
      }
      if (this.adLoader === undefined) {
        return
      }
    
      const adStatusListener: AdStatusListener = {
        onStatusChanged: (status: string, ad: AdInfo, data: string) => {
          switch (status) {
            case AdStatus.AD_SHOW:
              console.log(TAG, 'onAdShow')
              break
            case AdStatus.AD_CLICK:
              console.log(TAG, 'onAdClick')
              break
            case AdStatus.AD_REWARD:
              console.log(TAG, 'onAdReward')
              break
            case AdStatus.AD_CLOSE:
              console.log(TAG, 'onAdClose')
              this.hideAd()
              break
            case AdStatus.AD_RENDER_FAILED:
              console.log(TAG, 'onAdRenderFailed msg :: ' + data)
              this.hideAd()
              break
          }
        }
      }
      this.adInfo.setAdStatusListener(adStatusListener)
      this.adLoader.showAd(this.getUIContext(), this.adInfo)
  }
  
}
```

### 3.9 广告状态主要 API

#### AdStatusListener 广告状态监听

| 方法名                                                                             | 入参                                                  | 介绍                                                                   |
|---------------------------------------------------------------------------------|-----------------------------------------------------|----------------------------------------------------------------------|
| onStatusChanged( status: string, ad: AdInfo, data: string )   | status: string, ad: AdInfo, data: string  | 广告状态回调。参数说明: status(回调状态AdStatus)、 ad(广告对象)、 data(其它参数)  |

#### AdStatus 广告状态事件

| 参数名              | 介绍                     |
|------------------|------------------------|
| AD_SHOW          | 广告曝光回调。                |
| AD_CLICK         | 广告点击回调。                |
| AD_SKIP          | 广告跳过回调。在此处不要对广告进行关闭操作。 |
| AD_CLOSE         | 广告关闭回到。在此处移除广告。        |
| AD_REWARD        | 广告激励回调。                |
| AD_RENDER_FAILED | 广告渲染失败回调。              |

## 4.错误码介绍

| 错误码         | 介绍                                 |
|-------------|------------------------------------|
| -1000       | 初始化异常。                             |
| -1007       | 初始化接口KEY为空。                        |
| -2012       | 获取广告时发生未知异常。                       |
| -2013       | PosId不能为空。                         |
| -2014       | 初始化数据为空,可能是没有本地缓存的初始化数据并且初始接口请求失败。 |
| -2016       | 没有找到当前PosId的配置信息。                  |
| -2018       | 该PosId对应的广告类型不匹配。                  |
| -2110       | 返回的广告数据为空。                         |
| -2111       | 返回的广告数据为空。                         |

## 5.备注

具体的接入代码和流程,请参考Demo

## 6.商务合作

邮箱 : yuxingcao@admobile.top
