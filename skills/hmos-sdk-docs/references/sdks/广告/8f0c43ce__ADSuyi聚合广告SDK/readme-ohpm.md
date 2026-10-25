> 来源: ohpm 中央仓 README(T1 信源) | 包: `@admobile/adsuyi` | ohpm 最新版: 1.0.4 | 抓取: 2026-07-16
> 注意: 版本可能比市场快照新,以此为准时核对 CHANGELOG

# ADSuyi广告聚合 HarmonyOS Sdk——接入文档 V1.0.3

## 1. 概述

### 1.1 概述

尊敬的开发者朋友,欢迎您使用ADSuyi广告聚合SDK。通过本文档,您可以快速完成广告SDK的集成。

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
    <td><a href="#ad_native_express">信息流模板广告</a></td>
    <td>信息流模板广告,支持上文下图、下图上文、左图右文、右图左文、纯图</td>
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

## 3. 导入Suyi聚合广告

### 3.1 安装命令

```typescript
// ADSuyi广告聚合sdk
ohpm install @admobile/adsuyi
```

### 3.2 本地har包引入三方广告适配器

打开项目下的oh-package.json5文件,导入要接入的广告渠道适配器

```json
{
  ...
  "dependencies": {
    "@admobile/adsuyi": "file:libs/adsuyisdk_1.0.4.har",
    // 天目广告适配器
    "@admobile/tianmuadapter": "file:libs/tianmuadapter.har",
    // 天目广告sdk
    "@admobile/tianmu": "file:libs/tianmusdk_1.1.1.har",
    // 穿山甲广告适配器
    "@admobile/toutiaoadapter": "file:libs/toutiaoadapter.har",
    // 穿山甲广告sdk
    "@csj/openadsdk": "file:./libs/toutiaosdk_7.2.0.har",
    // 优量汇广告适配器
    "@admobile/gdtadapter": "file:libs/gdtadapter.har",
    // 优量汇广告sdk
    "@gdt/gdt-union-sdk": "file:./libs/gdtsdk.har",
    // 快手广告适配器
    "@admobile/kuaishouadapter": "file:libs/kuaishouadapter.har",
    // 快手广告sdk
    "ksadsdk": "file:./libs/kuaishousdk_3.0.8.har",
    //华为广告适配器,华为广告sdk已内置到系统中,无需额外导入
    "@admobile/hwppsadapter": "file:libs/hwppsadapter.har"
  },
  ...
}
```

### 3.3 添加动态import配置

打开entry的build-profile.json5文件,添加动态import配置

```json
{
  ...
  "buildOption": {
    "arkOptions": {
      "runtimeOnly": {
        "packages": [
          "@admobile/adsuyi",
          "@admobile/toutiaoadapter",
          "@admobile/hwppsadapter",
          "@admobile/tianmuadapter",
          "@admobile/kuaishouadapter",
          "@admobile/gdtadapter",
          "@csj/openadsdk",
          "@admobile/tianmu",
          "@gdt/gdt-union-sdk",
          "ksadsdk"
        ]
      }
    }
  },
  ...
}
```

## 4. SDK版本说明
无

## 5. SDK接入流程

### 5.1 添加SDK到工程中

接入环境:**DevEco Studio**,**Ohos_sdk_public 5.0.0.102**

### 5.3 权限申请

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

### 5.4 兼容配置

#### 5.4.1 混淆配置

如果打包时开启了混淆配置,请按需添加以下混淆内容,并保证广告资源文件不被混淆

### 5.5 隐私信息控制开关

```typescript
ADSuyi.SDK.setPersonalizedAdEnabled(true)
```

### 5.6 设备标识

#### 5.6.1 OAID支持

```typescript
// 传入获取到的OAID
ADSuyi.SDK.setOaid(oaid)
```

## 6. 示例代码

### 6.1 SDK初始化

在适当位置进行SDK的初始化

#### 6.1.1 初始化主要 API
**ADSuyi**

ADSuyi.Sdk

| 方法名                                             | 介绍                                                 |
|-------------------------------------------------|----------------------------------------------------|
| setInitListener(listener: ADSSPInitListener)    | 初始化状态回调。                                           |
| init(context: Context, config: InitConfig)      | 初始化方法。参数说明:context(初始化SDK的上下文对象)、config(初始化配置)。    |
| setPersonalizedAdEnabled(personalized: boolean) | 个性化控制开关。参数说明:personalized(个性化控制,true:开启,false:关闭)。 |
| setOaid(oaid: string)                           | 设置oaid。参数说明:oaid。                                  |

**InitConfig**

| 方法名                                        | 介绍                                                                                                                    |
|--------------------------------------------|-----------------------------------------------------------------------------------------------------------------------|
| withAppId(appId: string)                   | 设置appId。参数说明:appId,初始化广告的AppId。                                                                                       |
| withIsDebug(debug: boolean)                | 设置是否是Debug模式。参数说明:debug(true:开启,false:关闭, 默认:false)开发阶段以及提交测试阶段可设置为true,方便异常排查。                                       |

**ADSSPInitListener**

ADSSPInitListener

| 方法名                                 | 介绍                                                                                         |
|-------------------------------------|--------------------------------------------------------------------------------------------|
| onSuccess()                         | 初始化成功。                                                                                     |
| onFailed(code: number, msg: string) | 初始化失败。参数说明:code(错误码)、msg(错误信息)。                                                            |

#### 6.1.2 初始化接入示例

```typescript
// 设置debug状态,开发阶段建议设置true
const listener: InitListener = {
  onFailed(code: number, msg: string) {
    console.log(TAG, 'onFailed code :: ' + code + ' msg :: ' + msg)
  },

  onSuccess() {
    console.log(TAG, 'onSuccess')
  }

}
// 设置初始化状态监听
ADSuyi.Sdk.setInitListener(listener)

const config = InitConfig.builder()
  .withAppId('appid')
  .withIsDebug(true)
  .build();
  
// 初始化广告
ADSuyi.Sdk.init(getContext(this), config)
```

### <a name="ad_splash">6.2 开屏广告</a>

开屏广告建议在闪屏页进行展示,开屏广告的宽度和高度取决于容器的宽高,会撑满广告容器。

#### 6.2.1 开屏广告主要 API

**SplashAd**

| 参数名                                                | 介绍                                                   |
|----------------------------------------------------|------------------------------------------------------|
| SplashAd(context: context: common.Context)         | 开屏广告构造方法。参数说明:context(当前页面context: common.Context对象) |
| setListener(listener: ADSSPSplashAdListener)       | 设置广告加载监听。参数说明:listener(广告加载监听)。                      |
| loadAd(requestParams: ADSSPRequestParams)          | 加载广告。参数说明:requestParams(请求广告配置)。                     |

**ADSSPSplashAdListener**

| 参数名                                   | 介绍                                |
|---------------------------------------|-----------------------------------|
| onFailed: (code: number, msg: string) | 广告加载失败。参数说明:code(错误码)、msg(错误原因)   |
| onSuccess: (adInfos: IADSSPAdInfo[])  | 广告加载成功。参数说明:adInfos(广告对象数组)。      |

**ADSSPRequestParams**

请求广告配置

| 参数名                   | 介绍            |
|-----------------------|---------------|
| adId                  | 广告位id(必传)。    |
| adWidth               | 广告显示宽度(必传)。   |
| adHeight              | 广告显示高度(必传)。   |

**IADSSPAdInfo**

请求广告返回的对象,用于获取广告状态和展示广告

| 参数名                                                        | 介绍        |
|------------------------------------------------------------|-----------|
| setAdStatusListener(adStatusListener: ADSSPStatusListener) | 广告事件监听。   |
| getAdComponent()                                           | 获取广告展示布局。 |

**ADSSPStatusListener**

| 参数名                                                        | 介绍                                        |
|------------------------------------------------------------|-------------------------------------------|
| onStatusChanged: (status: string, adInfo: IADSSPAdInfo)    | 广告事件监听回调。参数说明:status(广告事件)、platform(广告平台) |

#### 6.2.2 开屏广告接入示例

```typescript
import { ButtonComponent } from '../components/ButtonComponent'
import { TitleComponent } from '../components/TitleComponent'
import { NodeController, promptAction } from '@kit.ArkUI';
import {
  AdStatusAction,
  SplashAd,
  IADSSPAdInfo,
  ADSSPRequestParams,
  IADSSPLoadListener
} from '@admobile/adsuyi';
import { UIUtil } from '../tools/UIUtil';

const TAG = 'AdSuyiDemo Ads Splash';

let screenWidth: number = UIUtil.getScreenWidthVp()
let screenHeight: number = UIUtil.getScreenHeightVp()

let adWidth: number = Math.round(screenWidth)
let adHeight: number = Math.round(screenHeight)

@Entry
@Component
struct SuyiSplashPage {
  @State splashAdComponent: NodeController | undefined = undefined
  @State adInfo?: IADSSPAdInfo = undefined
  // 广告请求参数
  private requestParams: ADSSPRequestParams = {
    adId: '广告位id',
    adWidth: adWidth,
    adHeight: adHeight
  }

  build() {
    RelativeContainer() {
      TitleComponent({
        title: '聚合开屏广告'
      })
        .id('titleBar')

      Column() {
        ButtonComponent({
          text: '加载广告'
        })
          .onClick(() => {
            this.loadAd()
          })
          .margin({
            top: 15
          })
        ButtonComponent({
          text: '展示广告'
        })
          .margin({ top: 20 })
          .onClick(() => {
            this.showAd()
          })
      }
      .alignRules({
        top: { anchor: 'titleBar', align: VerticalAlign.Bottom },
        bottom: { anchor: '__container__', align: VerticalAlign.Bottom }
      })
        .padding(20)

      if (this.splashAdComponent) {
        NodeContainer(this.splashAdComponent)
      }
    }
    .height('100%')
      .width('100%')
      .backgroundColor('#fff3f3f3')
  }

  loadAd() {
    // 广告请求回调监听
    const adSSPLoadListener: IADSSPLoadListener = {
      onFailed: (code: number, msg: string) => {
        console.log(TAG, 'onAdError code :: ' + code + ' msg :: ' + msg)
      },

      onSuccess: (adInfos: IADSSPAdInfo[]) => {
        console.log(TAG, 'onAdSuccess')
        promptAction.showToast({
          message: '广告加载成功',
          duration: 2000
        });
        this.adInfo = adInfos[0]
      }
    }

    // 创建AdLoader广告对象
    const splashAd: SplashAd = new SplashAd(this.getUIContext())
    splashAd.setListener(adSSPLoadListener)
    splashAd.loadAd(this.requestParams)
  }

  showAd() {
    if (this.adInfo === undefined) {
      promptAction.showToast({
        message: '没有广告填充',
        duration: 2000
      });
      return
    }
    this.adInfo.setAdStatusListener({
      onStatusChanged: (status: string, adInfo: IADSSPAdInfo) => {
        switch (status) {
          case AdStatusAction.AD_SHOW:
            console.log(TAG, 'onAdShow')
            break
          case AdStatusAction.AD_CLICK:
            console.log(TAG, 'onAdClick')
            break
          case AdStatusAction.AD_SKIP:
            console.log(TAG, 'onAdSkip')
            break
          case AdStatusAction.AD_CLOSE:
            console.log(TAG, 'onAdClose')
            this.hideAd()
            break
          case AdStatusAction.AD_RENDER_FAILED:
            console.log(TAG, 'onAdRenderFailed msg :: ')
            this.hideAd()
            break
        }
      }
    }
    )
    this.splashAdComponent = this.adInfo.getAdComponent()
  }

  hideAd() {
    this.splashAdComponent = undefined
    this.adInfo = undefined
  }
}
```

### <a name="ad_native_express">6.3 信息流模版广告</a>

信息流列表,轮播控件,固定位置都是较为适合

#### 6.3.1 信息流模版广告 API

**NativeExpressAd**

| 参数名                                               | 介绍                                                    |
|---------------------------------------------------|-------------------------------------------------------|
| NativeExpressAd(context: context: common.Context) | 开屏广告构造方法。参数说明:context(当前页面context: common.Context对象)  |
| setListener(listener: IADSSPLoadListener)         | 设置广告加载监听。参数说明:listener(广告加载监听)。                       |
| loadAd(requestParams: ADSSPRequestParams)         | 加载广告。参数说明:requestParams(请求广告配置)。                      |

**IADSSPLoadListener**

| 参数名                                   | 介绍                                |
|---------------------------------------|-----------------------------------|
| onFailed: (code: number, msg: string) | 广告加载失败。参数说明:code(错误码)、msg(错误原因)   |
| onSuccess: (adInfos: IADSSPAdInfo[])  | 广告加载成功。参数说明:adInfos(广告对象数组)。      |

**ADSSPRequestParams**

请求广告配置

| 参数名                 | 介绍                                 |
|---------------------|------------------------------------|
| adId                | 广告位id(必传)。                         |
| adCount             | 广告数量(必传)。                          |
| muted               | 是否静音(必传,true:静音,false:不静音)。        |
| isAutoPlay          | 是否自动播放(必传,true:自动播放,false:不自动播放)。  |

**IADSSPAdInfo**

请求广告返回的对象,用于获取广告状态和展示广告

| 参数名                                                        | 介绍        |
|------------------------------------------------------------|-----------|
| setAdStatusListener(adStatusListener: ADSSPStatusListener) | 广告事件监听。   |
| getAdComponent()                                           | 获取广告展示布局。 |

**ADSSPStatusListener**

| 参数名                                                     | 介绍                                        |
|---------------------------------------------------------|-------------------------------------------|
| onStatusChanged: (status: string, platform: string)     | 广告事件监听回调。参数说明:status(广告事件)、platform(广告平台) |

#### 6.3.2 信息流模版广告接入示例

```typescript
import { TitleComponent } from '../components/TitleComponent'

import { ADSSPRequestParams, AdStatusAction, IADSSPAdInfo, NativeExpressAd, IADSSPLoadListener } from '@admobile/adsuyi';
import { UIUtil } from '../tools/UIUtil';

const TAG = 'AdSuyiDemo Ads Native Express';

let screenWidth: number = UIUtil.getScreenWidthVp()

let adWidth: number = Math.round(screenWidth)

@Entry
@Component
struct SuyiNativeExpressPage {

  @State itemList: Array<string | IADSSPAdInfo> = []

  // 广告请求参数
  private requestParams: ADSSPRequestParams = {
    adId: '广告位id',
    adCount: 1,
    adWidth: adWidth,
    muted: false,
    isAutoPlay: true
  }

  aboutToAppear(): void {
    this.getData()
  }

  build() {
    RelativeContainer() {
      TitleComponent({
        title: '聚合信息流模版广告'
      })
        .id('titleBar')

      List() {
        ForEach(this.itemList, (item: string | IADSSPAdInfo) => {
          ListItem() {
            if (item instanceof IADSSPAdInfo) {
              NodeContainer(item.getAdComponent())
                .width("100%")
            } else {
              Text('测试数据')
                .width('100%')
                .height('200')
            }
          }
          .height('undefined')
        }, (item: string | IADSSPAdInfo, index: number) => {
          return item.toString() + "_" + index
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
    const adSSPLoadListener: IADSSPLoadListener = {
      onFailed: (code: number, msg: string) => {
        console.log(TAG, 'onAdError code :: ' + code + ' msg :: ' + msg)
        this.mockDataList()
      },

      onSuccess: (adSSPAdInfoList: Array<IADSSPAdInfo>) => {
        console.log(TAG, 'onAdSuccess')
        this.itemList.push('1')

        for (let i = 0; i < adSSPAdInfoList.length; i++) {
          const adInfo = adSSPAdInfoList[i];
          adInfo.setAdStatusListener({
            onStatusChanged: (status: string, adInfo: IADSSPAdInfo) => {
              switch (status) {
                case AdStatusAction.AD_SHOW:
                  console.log(TAG, 'onAdShow')
                  break
                case AdStatusAction.AD_CLICK:
                  console.log(TAG, 'onAdClick')
                  break
                case AdStatusAction.AD_SKIP:
                  console.log(TAG, 'onAdSkip')
                  break
                case AdStatusAction.AD_CLOSE:
                  console.log(TAG, 'onAdClose')
                  this.itemList.splice(this.itemList.indexOf(adInfo), 1)
                  break
                case AdStatusAction.AD_RENDER_FAILED:
                  console.log(TAG, 'onAdRenderFailed msg :: ')
                  this.itemList.splice(this.itemList.indexOf(adInfo), 1)
                  break
              }
            }
          })
          this.itemList.push(adInfo)
        }

        this.mockDataList()
      }
    }

    // 创建AdLoader广告对象
    const nativeExpressAd = new NativeExpressAd(this.getUIContext())
    nativeExpressAd.setListener(adSSPLoadListener)
    nativeExpressAd.loadAd(this.requestParams)
  }

  mockDataList() {
    for (let index = 0; index < 10; index++) {
      this.itemList.push('1')
    }
  }
}
```

### <a name="ad_interstitial">6.4 插屏广告示例</a>

插屏广告是移动广告的一种常见形式,在应用流程中弹出,当应用展示插屏广告时,用户可以选择点击广告,也可以将其关闭并返回应用。

#### 6.4.1 插屏广告主要 API

**InterstitialAd**

| 参数名                                                | 介绍                                                   |
|----------------------------------------------------|------------------------------------------------------|
| InterstitialAd(context: common.Context)            | 开屏广告构造方法。参数说明:context(当前页面context: common.Context对象) |
| setListener(listener: ADSSPInterstitialAdListener) | 设置广告加载监听。参数说明:listener(广告加载监听)。                      |
| loadAd(requestParams: ADSSPRequestParams)          | 加载广告。参数说明:requestParams(请求广告配置)。                     |

**ADSSPInterstitialAdListener**

| 参数名                                        | 介绍                              |
|--------------------------------------------|---------------------------------|
| onFailed: (code: number, msg: string)      | 广告加载失败。参数说明:code(错误码)、msg(错误原因) |
| onSuccess: (adInfos: InterstitialAdInfo[]) | 广告加载成功。参数说明:adInfos(广告对象数组)。    |

**ADSSPRequestParams**

请求广告配置

| 参数名                 | 介绍                                 |
|---------------------|------------------------------------|
| adId                | 广告位id(必传)。                         |
| muted               | 是否静音(必传,true:静音,false:不静音)。        |
| isAutoPlay          | 是否自动播放(必传,true:自动播放,false:不自动播放)。  |

**IADSSPAdInfo**

请求广告返回的对象,用于获取广告状态和展示广告

| 参数名                                                          | 介绍                                                                |
|--------------------------------------------------------------|-------------------------------------------------------------------|
| setAdStatusListener(adStatusListener: ADSSPStatusListener)   | 广告事件监听。                                                           |
| show(uiContext: UIContext, windowStage: window.WindowStage)  | 展示广告。参数说明:uiContext(上下文对象),windowStageon(WindowStageCreate回调可获取)。 |

**ADSSPStatusListener**

| 参数名                                                     | 介绍                                        |
|---------------------------------------------------------|-------------------------------------------|
| onStatusChanged: (status: string, platform: string)     | 广告事件监听回调。参数说明:status(广告事件)、platform(广告平台) |

#### 6.4.2 插屏广告接入示例

```typescript
import { ButtonComponent } from '../components/ButtonComponent'
import { TitleComponent } from '../components/TitleComponent'
import { promptAction } from '@kit.ArkUI';

import {
  AdStatusAction,
  ADSSPStatusListener,
  InterstitialAd,
  IADSSPAdInfo,
  ADSSPRequestParams,
  IADSSPLoadListener} from '@admobile/adsuyi';
import { DemoConstants } from '../entryability/DemoConstants';

const TAG = 'AdSuyiDemo Ads Interstitial';

@Entry
@Component
struct SuyiInterstitialPage {
  private adInfo?: IADSSPAdInfo
  private interstitialAd?: InterstitialAd
  // 广告请求参数
  private requestParams: ADSSPRequestParams = {
    adId: '广告位id',
  }

  build() {
    RelativeContainer() {
      TitleComponent({
        title: '聚合插屏广告'
      })
        .id('titleBar')

      Column() {
        ButtonComponent({
          text: '加载广告'
        })
          .onClick(() => {
            this.loadAd()
          })
          .margin({
            top: 15
          })
        ButtonComponent({
          text: '展示广告'
        })
          .margin({ top: 20 })
          .onClick(() => {
            this.showAd()
          })
      }
      .alignRules({
        top: { anchor: 'titleBar', align: VerticalAlign.Bottom },
        bottom: { anchor: '__container__', align: VerticalAlign.Bottom }
      })
        .padding(20)

    }
    .height('100%')
      .width('100%')
      .backgroundColor('#fff3f3f3')
  }

  loadAd() {
    // 广告请求回调监听
    const adSSPLoadListener: IADSSPLoadListener = {
      onFailed: (code: number, msg: string) => {
        console.log(TAG, 'onAdError code :: ' + code + ' msg :: ' + msg)
      },

      onSuccess: (adInfos: Array<IADSSPAdInfo>) => {
        console.log(TAG, 'onAdSuccess')
        promptAction.showToast({
          message: '广告加载成功',
          duration: 2000
        });
        this.adInfo = adInfos[0]
      }
    }

    // 创建AdLoader广告对象
    this.interstitialAd = new InterstitialAd(this.getUIContext())
    this.interstitialAd.setListener(adSSPLoadListener)
    this.interstitialAd.loadAd(this.requestParams)
  }

  showAd() {
    if (this.interstitialAd === undefined) {
      promptAction.showToast({
        message: '没有广告填充',
        duration: 2000
      });
      return
    }

    const adSSPStatusListener: ADSSPStatusListener = {
      onStatusChanged: (status: string, adInfo: IADSSPAdInfo) => {
        switch (status) {
          case AdStatusAction.AD_SHOW:
            console.log(TAG, 'onAdShow')
            break
          case AdStatusAction.AD_CLICK:
            console.log(TAG, 'onAdClick')
            break
          case AdStatusAction.AD_CLOSE:
            console.log(TAG, 'onAdClose')
            this.hideAd()
            break
          case AdStatusAction.AD_RENDER_FAILED:
            this.hideAd()
            break
        }
      }
    }
    this.adInfo?.setAdStatusListener(adSSPStatusListener)
    this.adInfo?.show(this.getUIContext(), DemoConstants.windowStage)
  }

  hideAd() {
    this.adInfo = undefined
  }
}
```

### <a name="ad_reward">6.5 激励视频广告示例</a>

将短视频融入到APP场景当中,用户观看短视频广告后可以给予一些应用内奖励。

#### 6.5.1 激励视频广告主要 API

**InterstitialAd**

| 参数名                                             | 介绍                                                      |
|-------------------------------------------------|---------------------------------------------------------|
| RewardAd(context: common.Context)               | 开屏广告构造方法。参数说明:context(当前页面context: common.Context对象)    |
| setListener(listener: ADSSPRewardAdListener)    | 设置广告加载监听。参数说明:listener(广告加载监听)。                         |
| loadAd(requestParams: ADSSPRequestParams)       | 加载广告。参数说明:requestParams(请求广告配置)。                        |

**ADSSPRewardAdListener**

| 参数名                                    | 介绍                                  |
|----------------------------------------|-------------------------------------|
| onFailed: (code: number, msg: string)  | 广告加载失败。参数说明:code(错误码)、msg(错误原因)     |
| onSuccess: (adInfos: RewardAdInfo[])   | 广告加载成功。参数说明:adInfos(广告对象数组)。        |

**ADSSPRequestParams**

请求广告配置

| 参数名                 | 介绍                                 |
|---------------------|------------------------------------|
| adId                | 广告位id(必传)。                         |
| muted               | 是否静音(必传,true:静音,false:不静音)。        |
| isAutoPlay          | 是否自动播放(必传,true:自动播放,false:不自动播放)。  |

**IADSSPAdInfo**

请求广告返回的对象,用于获取广告状态和展示广告

| 参数名                                                         | 介绍                                                                |
|-------------------------------------------------------------|-------------------------------------------------------------------|
| setAdStatusListener(adStatusListener: ADSSPStatusListener)  | 广告事件监听。                                                           |
| show(uiContext: UIContext, windowStage: window.WindowStage) | 展示广告。参数说明:uiContext(上下文对象),windowStageon(WindowStageCreate回调可获取)。 |

**ADSSPStatusListener**

| 参数名                                                     | 介绍                                        |
|---------------------------------------------------------|-------------------------------------------|
| onStatusChanged: (status: string, platform: string)     | 广告事件监听回调。参数说明:status(广告事件)、platform(广告平台) |

#### 6.5.2 激励视频广告接入示例

```typescript
import { ButtonComponent } from '../components/ButtonComponent'
import { TitleComponent } from '../components/TitleComponent'
import { promptAction } from '@kit.ArkUI';

import {
  ADSSPStatusListener,
  AdStatusAction,
  RewardAd,
  RewardAdInfo,
  IADSSPAdInfo,
  ADSSPRequestParams,
  IADSSPLoadListener
} from '@admobile/adsuyi';
import { DemoConstants } from '../entryability/DemoConstants';

const TAG = 'AdSuyiDemo Ads Reward';

@Entry
@Component
struct SuyiRewardPage {
  private adInfo?: IADSSPAdInfo
  private rewardAd?: RewardAd

  // 广告请求参数
  private requestParams: ADSSPRequestParams = {
    adId: '广告位id',
  }

  build() {
    RelativeContainer() {
      TitleComponent({
        title: '聚合激励广告'
      })
        .id('titleBar')

      Column() {
        ButtonComponent({
          text: '加载广告'
        })
          .onClick(() => {
            this.loadAd()
          })
          .margin({
            top: 15
          })
        ButtonComponent({
          text: '展示广告'
        })
          .margin({ top: 20 })
          .onClick(() => {
            this.showAd()
          })
      }
      .alignRules({
        top: { anchor: 'titleBar', align: VerticalAlign.Bottom },
        bottom: { anchor: '__container__', align: VerticalAlign.Bottom }
      })
        .padding(20)

    }
    .height('100%')
      .width('100%')
      .backgroundColor('#fff3f3f3')
  }

  loadAd() {
    // 广告请求回调监听
    const adSSPLoadListener: IADSSPLoadListener = {
      onFailed: (code: number, msg: string) => {
        console.log(TAG, 'onAdError code :: ' + code + ' msg :: ' + msg)
      },

      onSuccess: (adInfos: IADSSPAdInfo[]) => {
        console.log(TAG, 'onAdSuccess')
        promptAction.showToast({
          message: '广告加载成功',
          duration: 2000
        });
        this.adInfo = adInfos[0]
      }
    }

    // 创建AdLoader广告对象
    this.rewardAd = new RewardAd(this.getUIContext())
    this.rewardAd.setListener(adSSPLoadListener)
    this.rewardAd.loadAd(this.requestParams)
  }

  showAd() {
    if (this.adInfo === undefined) {
      promptAction.showToast({
        message: '没有广告填充',
        duration: 2000
      });
      return
    }

    const adSSPStatusListener: ADSSPStatusListener = {
      onStatusChanged: (status: string, adInfo: IADSSPAdInfo) => {
        switch (status) {
          case AdStatusAction.AD_SHOW:
            console.log(TAG, 'onAdShow')
            break
          case AdStatusAction.AD_CLICK:
            console.log(TAG, 'onAdClick')
            break
          case AdStatusAction.AD_REWARD:
            console.log(TAG, 'onAdReward')
            break
          case AdStatusAction.AD_CLOSE:
            console.log(TAG, 'onAdClose')
            this.hideAd()
            break
          case AdStatusAction.AD_RENDER_FAILED:
            this.hideAd()
            break
        }
      }
    }
    this.adInfo?.setAdStatusListener(adSSPStatusListener)
    this.adInfo?.show(this.getUIContext(), DemoConstants.windowStage)
  }

  hideAd() {
    this.adInfo = undefined
  }
}
```

### 6.6 广告状态主要 API

**ADSSPStatusListener**

| 方法名                                                  | 介绍                                         |
|------------------------------------------------------|--------------------------------------------|
| onStatusChanged: (status: string, platform: string)  | 参数说明:status(回调状态AdStatus)、platform(广告平台名)。 |

**AdStatusAction**

| 参数名              | 介绍                     |
|------------------|------------------------|
| AD_SHOW          | 广告曝光回调。                |
| AD_CLICK         | 广告点击回调。                |
| AD_SKIP          | 广告跳过回调。在此处不要对广告进行关闭操作。 |
| AD_CLOSE         | 广告关闭回到。在此处移除广告。        |
| AD_REWARD        | 广告激励回调。                |
| AD_RENDER_FAILED | 广告渲染失败回调。              |

## 7.错误码

| 错误码          | 介绍                                                                                                                                   |
|--------------|--------------------------------------------------------------------------------------------------------------------------------------|
| -10006       | 初始化接口数据为空。                                                                                                                           |
| -10007       | 初始化接口KEY为空。                                                                                                                          |
| -20002       | context为空。                                                                                                                           |
| -20104       | 初始化数据为空,可能是没有本地缓存的初始化数据并且初始接口请求失败。                                                                                                   |
| -20106       | 没有找到当前PosId的配置信息,主要有以下三种情况 :1、初始化失败,本地没有初始化配置信息并且远程拉取初始化配置失败了,请检查网络或AppId是否正确;2、传入的PosId有误;3、如果前两条均正常,请后台检查该PosId是否配置并开启了三方平台的广告位信息。 |
| -20107       | 平台的广告位信息为空。                                                                                                                          |
| -20109       | 暂不支持当前广告类型。                                                                                                                          |
| -20110       | 瀑布流轮询完毕,无广告返回。                                                                                                                       |
| -20112       | 已达到展示上限。                                                                                                                             |
| -20122       | 广告位获取广告超时/广告源获取广告超时。                                                                                                                 |

## 8.备注

具体的接入代码和流程,请参考Demo

## 9.商务合作

邮箱 : yuxingcao@admobile.top
