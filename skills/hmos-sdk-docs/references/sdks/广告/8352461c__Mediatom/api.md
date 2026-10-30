# **Mediatom Harmony SDK 接入说明** 

# **前置说明** 

使用Mediatom SDK前必须满足以下条件。 

## **参数申请** 

目前聚合广告SDK需要的参数为各广告联盟平台的APPID和各广告位对应ID,请在广告联盟官方指定平 台申请或联系具体负责人! 

## **支持的广告联盟和广告类型** 

|**广告联盟**|**开屏广告**|**插屏广告**|**横幅广告**|**信息流广告**|**激励视频广告**|
|---|---|---|---|---|---|
|穿山甲|✔|✔|✔|✔|✔|
|快手|✔|✔|❌|✔|✔|
|优量汇|✔|✔|✔|✔|✔|
|华为|✔|✔|❌|✔|✔|

## **Mediatom平台配置** 

接入方需事先在各三方广告联盟SDK平台申请相关广告参数,然后在Mediatom聚合平台进行配置。在 Mediatom聚合平台配置之后,才能正常使用本SDK的聚合功能。 

## **一、准备工作** 

### **1.SDK集成** 

##### **ad_common.har为核心包,其他的都是联盟的适配器和SDK** 

#### **1.1:核心包集成** 

将我们提供的ad_common.har放置到媒体的工程libs目录,在工程oh-package.json5文件中以本地har 包形式引入,参考代码如下 

```
"dependencies": {
  //广告核心库中有使用,必须依赖
  "@ohos/crypto-js": "2.0.4",
  //广告核心库中有使用,必须依赖
  "class-transformer": "0.5.1",
  //广告核心包
  "@mediatom/ad_common": "libs/ad_common.har",
}
```

#### **1.2:聚合其他SDK集成** 

##### **SDK版本和联盟SDK版本严格对应,不一致会出现加载不出广告或者编译时就会报错** 

将我们提供的其他联盟适配器和sdk包对应的har放置到媒体的工程libs目录,在工程oh-package.json5 文件中以本地har包形式引入,参考代码如下 按照实际使用的联盟添加联盟对应的配置 

```
"dependencies": {
    //穿山甲适配器
    "@mediatom/adapter_csj": "file:libs/adapter_csj.har",
    //穿山甲SDK
    "@csj/openadsdk": "file:libs/openadsdk_7.3.0.har",
    //快手适配器(包含广告SDK)
    "@mediatom/adapter_ks": "file:libs/adapter_ks.har",
    //优量汇适配器(包含广告SDK)
    "@mediatom/adapter_gdt": "file:libs/adapter_gdt.har",
    //华为适配器(包含广告sdk)
    "@mediatom/adapter_huawei": "file:libs/adapter_huawei.har"
}
```

### **2.必要配置** 

工程级build-profile.json5中设置useNormalizedOHMUrl为true 

```
{
  "app": {
    "products": [
      {
        "buildOption": {
          "strictMode": {
            "useNormalizedOHMUrl": true
          }
        }
      }
    ]
  }
}
```

聚合功能联盟的适配器采用动态导包的方式加载,为了将这部分模块加入编译,还需要额外增加一个 runtimeOnly的buildOption配置,用于配置动态导包的变量实际的模块名。在工程build-profile.json5 中配置 

按照实际使用的联盟添加联盟对应的配置 

```
{
  "buildOption": {
    "arkOptions": {
      "runtimeOnly": {
        "packages": [
          "@mediatom/adapter_csj",
          "@mediatom/adapter_ks",
          "@mediatom/adapter_gdt",
          "@mediatom/adapter_huawei"
        ]
      }
    }
  }
}
```

### **3.权限说明** 

广告依赖部分设备信息进行转化,需要媒体在module.json5文件中添加以下权限: 

```
{
  "requestPermissions": [
    {
      "name": "ohos.permission.INTERNET",   //访问网络必选
      "reason": "$string:request_network"
    },
    {
      "name": "ohos.permission.GET_NETWORK_INFO", //获取网络状态
      "reason": "$string:request_network_info"
    },
    {
      "name": "ohos.permission.APP_TRACKING_CONSENT", //获取广告标识
      "reason": "$string:request_track"
      "usedScene": {
          "when": "always"
        }
    },
    {
      "name": "ohos.permission.ACCELEROMETER", // 传感器,用于实现扭动摇动
      "reason": "$string:request_sensor"
    },
    {
      "name": "ohos.permission.GYROSCOPE", // 传感器,用于实现扭动摇动
      "reason": "$string:request_sensor"
    },
    {
      "name": "ohos.permission.VIBRATE", // 振动,用于交互反馈
      "reason": "$string:request_vibrate"
    }
  ]
}
```

## **二、SDK初始化** 

### **初始化代码** 

```
letparamsConfig
    :
AdParamsConfig=newAdParamsConfig()
paramsConfig.appId='5de629d305ea550d'//在mediatom平台申请到的appid
paramsConfig.isDebug=true//是否打开debug开关输出日志,正式上线后建议设置为false
MTConfig.getInstance().init(DemoConstants.context,
DemoConstants.windowStage, paramsConfig).then((result) => {
if (result) {
''
ToastUtil.showToast(初始化成功)
this.hasInitSdk=true
        } else {
''
ToastUtil.showToast(初始化失败)
this.hasInitSdk=false
        }
    })
```

### **初始化SDK更多可选参数说明** 

```
export classAdParamsConfig {
public
appId
    : string=''; //appId
public
channelId
    : string=''; //渠道
public
subChannel
    : string=''; //子渠道
public
isDebug
    : boolean=true; //是否开启debug模式,true打印日志
public
customMap
    : HashMap
<string
    , string
>|null=null; //自定义参数
public
personalizedState
    : boolean=true; //是否允许个性化
public
canUseOaid
    : boolean=true; //是否允许收集oaid
public
canUseMac
    : boolean=true; //是否允许收集mac地址
public
customOaid
    : string='';
public
customMac
    : string='';
}
```

## **三、广告接入** 

### **1. 开屏广告** 

展示在开屏页的位置:启动进入应用时,加载开屏页广告,广告展示完毕,根据各应用的逻辑跳转到相 应页面。 

当用户点击广告跳转到广告详情页面后onAdClose()方法仍然可能会被调用,为了保证落地页效果,此 时开发者还不能打开自己的App主页 

,当从广告落地页返回以后才可以跳转。所以使用canJump字段配合页面生命周期辅助判断正确的跳转 时机,具体实现可以曹侃demo中SpreadPage页面的实现。 

```
constbuild
            :
AdViewSpreadBuilder=newAdViewSpreadBuilder();
build.key="41ee1e15554ede05";
build.uiContext=this.getUIContext()
letspread
            :
MTSpread=newMTSpread(build);
spread.setEventListener({
onAdLoadSuccess: ()
                :
void
=>
                {
//广告加载成功回调
console
                .
log
                (
"MTSpread:onAdShow"
                )
spread
                .
showAd
                (
                )
            },
onAdShow:
            ():
void=>
            {
//广告成功展示回调
console.log("MTSpread:onAdShow")
}
            ,
onAdClick: ():
void=>
            {
//广告点击回调
console.log("MTSpread:onAdClick")
}
            ,
onAdClose: ():
void=>
            {
//广告关闭回调
console.log("MTSpread:onAdClose")
spread.destroy()
router.back()
}
            ,
onAdFailed: (error:
MTError
            )
            :
void=>
            {
//广告加载失败回调
console.log("MTSpread", error.errorMsg)
ToastUtil.showToast(error.errorMsg)
}
            }
            )
spread.requestSpread()
```

### **2. 插屏广告** 

插屏广告为卡片展示的广告,支持图片和视频 

```
constbuild: AdViewInterstitialBuilder=new
AdViewInterstitialBuilder();
build.key="dc649c9a6ede2c7d";
build.uiContext=this.getUIContext()
letinterstitial: MTInterstitial=newMTInterstitial(build);
interstitial.setEventListener({
//广告加载成功回调
onAdLoadSuccess: (): void=> {
console.log("MTInterstitial:onAdLoadSuccess")
interstitial.showAd()
              },
//广告展示回调
onAdShow: (): void=> {
console.log("MTInterstitial:onAdShow")
              },
//广告点击回调
onAdClick: (): void=> {
console.log("MTInterstitial:onAdClick")
              },
//广告关闭回调
onAdClose: (): void=> {
console.log("MTInterstitial:onAdClose")
              },
//广告加载失败回调
onAdFailed: (error: MTError): void=> {
console.log("MTInterstitial:onAdFailed")
ToastUtil.showToast(error.errorMsg)
              }
            })
interstitial.requestInterstitial()
```

### **3. 激励视频** 

##### 激励视频是一种收益较高的广告类型,广告播放结束后会触发奖励回调。 

```
constbuild: AdViewRewardVideoBuilder=new
AdViewRewardVideoBuilder();
build.key="9678eda700de98cf";
build.uiContext=this.getUIContext()
letrewardVideo: MTRewardVideo=newMTRewardVideo(build);
rewardVideo.setEventListener({
onAdLoadSuccess: (): void=> {
console.log("MTRewardVideo :onAdLoadSuccess")
rewardVideo.showAd()
              },
onReward: (price: number): void=> {
"
console.log("MTRewardVideo :onReward:+price)
              },
onCheckReward: (transID: string): void=> {
console.log("MTRewardVideo :onCheckReward")
              },
onAdShow: (): void=> {
console.log("MTRewardVideo :onAdShow")
              },
onAdClick: (): void=> {
console.log("MTRewardVideo :onAdClick")
              },
onAdClose: (): void=> {
console.log("MTRewardVideo :onAdClose")
              },
onAdFailed: (error: MTError): void=> {
console.log("MTRewardVideo :onAdFailed")
ToastUtil.showToast(error.errorMsg)
              }
            })
rewardVideo.requestRewardVideo()
```

### **4. Banner广告** 

Banner广告是在应用程序顶部、中部或底部占据一个位置的矩形图片,广告内容每隔一段时间会自动 刷新。 

Banner广告分为自渲染广告和模板广告,但是自渲染广告只有当三方SDK支持时才会返回。 

#### **4.1:加载广告** 

width和height为想要请求的模版信息流宽高,单位为vp,也可不传,默认全屏,高度自适应 

```
constbuild: AdViewBannerBuilder=newAdViewBannerBuilder();
build.key="105006e35bab3619";
build.uiContext=this.getUIContext()
build.width=350
build.height=150
letbanner: MTBanner=newMTBanner(build);
banner.setEventListener({
//广告加载成功
onAdLoadSuccess: (bannerAd: BannerAd): void=> {
console.log("MTBanner:onAdLoadSuccess");
      },
//广告加载失败
onAdFailed: (error: MTError): void=> {
"
console.log("MTBanner:+error.errorMsg);
ToastUtil.showToast(error.errorMsg)
      }
    })
banner.requestBanner()
```

#### **4.2:广告设置监听** 

##### **4.2.1:设置Banner广告交互监听** 

```
bannerAd.setBannerAdInteractionListener({
//广告点击回调
onBannerAdClickEvent: (): void=> {
console.log("MTBanner:onBannerAdClickEvent");
          },
//广告展示回调
onBannerAdShowEvent: (): void=> {
console.log("MTBanner:onBannerAdShowEvent");
          },
//广告关闭回调,自己处理广告的移除
onBannerAdCloseEvent: (): void=> {
console.log("MTBanner:onBannerAdCloseEvent");
          }
        })
```

##### **4.2.2:设置Banner广告视频监听,广告资源为视频时回调,仅供参考** 

```
bannerAd.setBannerAdVideoListener({
//视频广告资源加载成功
onVideoLoad: () => {
console.log("MTBanner==onVideoLoad......");
          },
/**
* 视频广告加载失败
* @param errorCode 错误类型:
*
*/
onVideoError: (errorCode: number, errorMsg: string) => {
console.log("MTBanner==onVideoError......errorCode="+errorCode+
",errorMsg="+errorMsg);
          },
/**
* 视频广告播放回调
*
* @param ad
*/
onVideoAdStartPlay: () => {
console.log("MTBanner==onVideoAdStartPlay......");
          },
/**
* 视频广告暂停回调
*
* @param ad
*/
onVideoAdPaused: () => {
console.log("MTBanner==onVideoAdPaused......");
          },
/**
* 视频广告续播
*
* @param ad
*/
onVideoAdContinuePlay: () => {
console.log("MTBanner==onVideoAdContinuePlay......");
          },
/**
* 视频播放进度
*
* @param current
* @param duration
*/
onProgressUpdate: (current: number, duration: number) => {
// console.log("MTBanner==onProgressUpdate......current=" + current
+ ",duration=" + duration);
          },
/**
* 视频广告播放完成回调
*
* @param ad
*/
onVideoAdComplete: () => {
console.log("MTBanner==onVideoAdComplete......");
          }
        })
```

#### **4.3. 广告展示** 

##### **4.3.1:模版Banner广告展示** 

调用render()方法,然后在onRenderSuccess回调中通过getAdComponent方法获取 NodeController, 

##### 渲染到NodeContainer中 

```
bannerAd.render(this.getUIContext(), {
//广告渲染成功
onRenderSuccess: (width: number, height: number): void=> {
          },
//广告渲染失败
onRenderFail: (code: number, msg: string): void=> {
          }
        })
build() {
   Column() {
     NodeContainer(item.getAdComponent())
   }
   .width('100%')
}
```

##### **4.3.2:自渲染Banner广告展示** 

##### 调用render() 

方法,然后在onRenderSuccess回调中通过BannerAd的各个方法获取相关信息自行渲染,如果是视频 素材通过getAdComponent方法获取封装好的视频NodeController,渲染到NodeContainer中 

最后调用registerViewForInteraction来注册计费时间,具体方法介绍如下,具体实现情况可以参照 demo中 

BannerPage.ets 

```
export interfaceBannerAd {
/**
* 是否是模版广告
* @return s
*/
isExpress(): boolean
/**
* 获取素材渲染类型
* 模版渲染时为空
* @return s
*/
getMaterialType(): MTAdMaterialType
/**
* 广告标题
* 模版渲染时为空
* @return s
*/
getTitle(): string
/**
* 广告描述
* 模版渲染时为空
* @return s
*/
getDescription(): string
/**
* 广告按钮文案
* 模版渲染时为空
* @return s
*/
getCAT(): string
/**
* 应用下载次数文案
* 模版渲染时为空,非下载为空
* @return s
*/
getAppDownloadCountDes(): string|undefined
/**
* 广告APP评论数
* @return s
*/
getAppCommentNum(): number
/**
* 广告app评分
* @return s
*/
getAppScore(): number
/**
* 广告角标logo
* 字符串类型有可能是文字有可能是图片,需要判断内容来决定使用Text还是Image加载
* 模版渲染时为空
* @return s
*/
getAdLogo(): string|Resource|undefined
/**
* 图片素材列表
* 模版渲染时为空
* @return s
*/
getImageList(): ArrayList<MTImage>|undefined
/**
* 广告ICON链接
* 模版渲染时为空
* @return s
*/
getAppIconUrl(): string|undefined
/**
* 应用下载合规信息
* 模版渲染时为空
* @return s
*/
getComplianceInfo(): MTComplianceInfo|undefined
/**
* 注册原生自渲染广告组件
* 所有组件id需保证不能重复(鸿蒙系统要求)
* @param rootAdComponentId 广告根组件id
* @param uiContext 显示广告组件所在页面上下文
* @param clickViewIds 点击组件id集合
* @param closeViewIds 关闭组件id集合,可以空自己处理关闭
*/
registerViewForInteraction(rootAdComponentId: string, uiContext: UIContext,
clickViewIds: MTArrayList<string>,
closeViewIds?: MTArrayList<string>): void
/**
* 模板广告渲染方法,渲染成功后通过getAdComponent()可获取到渲染成功的广告
* @param context
*/
render(context: UIContext, listener: MTNativeExpressReaderListener): void
/**
* 获取广告UI组件(模版广告,自渲染广告中视频)可能为空
* @return s
*/
getAdComponent(): NodeController|undefined
/**
* 设置广告交互监听
* @param listener
*/
setBannerAdInteractionListener(listener: MTBannerInteractionListener): void
/**
* 设置广告视频相关监听,可能没有回调
* @param listener
*/
setBannerAdVideoListener(listener: MTNativeVideoListener): void
/**
* 广告销毁
*/
destroy(): void
}
```

##### 素材类型MTAdMaterialType: 

```
export enum
MTAdMaterialType
{
IMAGE_MODE_UNKNOWN=0, //未知的其他类型,不进行渲染
IMAGE_MODE_SINGLE_IMG=1, //单图
IMAGE_MODE_GROUP_IMG=2, //组图
IMAGE_MODE_VIDEO=3//视频
}
```

##### 应用下载合规信息MTComplianceInfo: 

```
export interface
MTComplianceInfo
{
//应用名称
getAppName: () =>string
//应用版本
getAppVersion: () =>string
//应用开发者
getDeveloperName: () =>string
//隐私协议链接
getPrivacyUrl: () =>string
//权限列表链接
getPermissionUrl: () =>string
//权限名称及权限描述列表
getPermissionsMap: () =>Map<
string, string>|undefined
//产品功能链接
getFunctionDescUrl: () =>string
}
```

### **5.原生混合广告** 

原生混合广告是将 **自渲染信息流广告** , **模版信息流广告** 封装到同一个API中的广告请求方式。开发者可 以在同一个广告位中配置上述不同的广告样式混用。 

#### **5.1:加载广告** 

width和height为想要请求的模版信息流宽高,单位为vp,也可不传,默认全屏,高度自适应 

```
constbuild: AdViewMixNativeBuilder=newAdViewMixNativeBuilder();
build.key="0c1ddd0ae9eabd7e";
build.uiContext=this.getUIContext()
build.width=350
build.height=150
letmixNative: MTMixNative=newMTMixNative(build);
mixNative.setEventListener({
onAdLoadSuccess: (nativeAd: NativeAd): void=> {
      },
onAdFailed: (error: MTError): void=> {
ToastUtil.showToast(error.errorMsg)
      }
    })
mixNative.requestMixNative()
```

#### **5.2:广告设置监听** 

##### **5.2.1:设置原生混合广告交互监听** 

```
nativeAd.setNativeAdInteractionListener({
//点击回调
onNativeAdClickEvent: (): void=> {
console.log("MTMixNative:onNativeAdClickEvent")
          },
//展示回调
onNativeAdShowEvent: (): void=> {
console.log("MTMixNative:onNativeAdShowEvent")
          },
//关闭回调,自己处理广告的移除
onNativeAdCloseEvent: (): void=> {
console.log("MTMixNative:onNativeAdCloseEvent")
constindex=this.listArray.indexOf(nativeAd)
this.listArray.splice(index, 1)
          }
        })
```

##### **5.2.2:设置原生混合广告视频监听,广告资源为视频时回调,仅供参考** 

```
nativeAd.setNativeAdVideoListener({
onVideoLoad: () => {
console.log("MTMixNative==onVideoLoad......");
          },
/**
* 视频广告加载失败
* @param errorCode 错误类型:
*
*/
onVideoError: (errorCode: number, errorMsg: string) => {
console.log("MTMixNative==onVideoError......errorCode="+errorCode
+",errorMsg="+errorMsg);
          },
/**
* 视频广告播放回调
*
* @param ad
*/
onVideoAdStartPlay: () => {
console.log("MTMixNative==onVideoAdStartPlay......");
          },
/**
* 视频广告暂停回调
*
* @param ad
*/
onVideoAdPaused: () => {
console.log("MTMixNative==onVideoAdPaused......");
          },
/**
* 视频广告续播
*
* @param ad
*/
onVideoAdContinuePlay: () => {
console.log("MTMixNative==onVideoAdContinuePlay......");
          },
/**
* 视频播放进度
*
* @param current
* @param duration
*/
onProgressUpdate: (current: number, duration: number) => {
// console.log("MTMixNative==onProgressUpdate......current=" +
current + ",duration=" + duration);
          },
/**
* 视频广告播放完成回调
*
* @param ad
*/
onVideoAdComplete: () => {
console.log("MTMixNative==onVideoAdComplete......");
          }
        })
```

#### **5.3. 广告展示** 

##### **5.3.1:模版信息流广告展示** 

调用render()方法,然后在onRenderSuccess回调中通过getAdComponent方法获取 NodeController, 

渲染到NodeContainer中 

```
nativeAd.render(this.getUIContext(), {
//广告渲染成功
onRenderSuccess: (width: number, height: number): void=> {
          },
//广告渲染失败
onRenderFail: (code: number, msg: string): void=> {
          }
        })
build() {
   Column() {
     NodeContainer(item.getAdComponent())
   }
   .width('100%')
}
```

##### **5.3.2:自渲染信息流广告展示** 

##### 调用render() 

方法,然后在onRenderSuccess回调中通过NativeAd的各个方法获取相关信息自行渲染,如果是视频 素材通过getAdComponent方法获取封装好的视频NodeController,渲染到NodeContainer中 

最后调用registerViewForInteraction来注册计费时间,具体方法介绍如下,具体实现情况可以参照 demo中 

MixNativePage.ets 

```
export interfaceNativeAd {
/**
* 是否是模版广告
* @return s
*/
isExpress(): boolean;
/**
* 获取素材渲染类型
* 模版渲染时为空
* @return s
*/
getMaterialType(): MTAdMaterialType;
/**
* 广告标题
* 模版渲染时为空
* @return s
*/
getTitle(): string;
/**
* 广告描述
* 模版渲染时为空
* @return s
*/
getDescription(): string;
/**
* 广告按钮文案
* 模版渲染时为空
* @return s
*/
getCAT(): string;
/**
* 应用下载次数文案
* 模版渲染时为空,非下载为空
* @return s
*/
getAppDownloadCountDes(): string|undefined;
/**
* 广告APP评论数
* @return s
*/
getAppCommentNum(): number;
/**
* 广告app评分
* @return s
*/
getAppScore(): number;
/**
* 广告角标logo
* 字符串类型有可能是文字有可能是图片,需要判断内容来决定使用Text还是Image加载
* 模版渲染时为空
* @return s
*/
getAdLogo(): string|Resource|undefined;
/**
* 图片素材列表
* 模版渲染时为空
* @return s
*/
getImageList(): ArrayList<MTImage>|undefined;
/**
* 广告ICON链接
* 模版渲染时为空
* @return s
*/
getAppIconUrl(): string|undefined;
/**
* 应用下载合规信息
* 模版渲染时为空
* @return s
*/
getComplianceInfo(): MTComplianceInfo|undefined;
/**
* 视频封面,可能为空
* 模版渲染时为空
* @return s
*/
getCoverUrl(): string|undefined;
/**
* 视频链接,可能为空
* 模版渲染时为空
* @return s
*/
getVideoUrl(): string|undefined;
/**
* 视频时长
* @return s
*/
getVideoDuration(): number;
/**
* 注册原生自渲染广告组件
* 所有组件id需保证不能重复(鸿蒙系统要求)
* @param rootAdComponentId 广告根组件id
* @param uiContext 显示广告组件所在页面上下文
* @param clickViewIds 点击组件id集合
* @param closeViewIds 关闭组件id集合,可以空自己处理关闭
*/
registerViewForInteraction(rootAdComponentId: string, uiContext: UIContext,
clickViewIds: MTArrayList<string>, closeViewIds?: MTArrayList<string>): void;
/**
* 模板广告渲染方法,渲染成功后通过getAdComponent()可获取到渲染成功的广告
* @param context
*/
render(context: UIContext, listener: MTNativeExpressReaderListener): void;
/**
* 获取广告UI组件(模版广告,自渲染广告中视频)可能为空
* @return s
*/
getAdComponent(): NodeController|undefined;
/**
* 设置广告交互监听
* @param listener
*/
setNativeAdInteractionListener(listener: MTNativeInteractionListener): void;
/**
* 设置广告视频相关监听
* @param listener
*/
setNativeAdVideoListener(listener: MTNativeVideoListener): void;
/**
* 广告销毁
*/
destroy(): void;
}
```

##### 素材类型MTAdMaterialType: 

```
export enum
MTAdMaterialType
{
IMAGE_MODE_UNKNOWN=0, //未知的其他类型,不进行渲染
IMAGE_MODE_SINGLE_IMG=1, //单图
IMAGE_MODE_GROUP_IMG=2, //组图
IMAGE_MODE_VIDEO=3//视频
}
```

##### 应用下载合规信息MTComplianceInfo: 

```
export interface
MTComplianceInfo
{
//应用名称
getAppName: () =>string
//应用版本
getAppVersion: () =>string
//应用开发者
getDeveloperName: () =>string
//隐私协议链接
getPrivacyUrl: () =>string
//权限列表链接
getPermissionUrl: () =>string
//权限名称及权限描述列表
getPermissionsMap: () =>Map<
string, string>|undefined
//产品功能链接
getFunctionDescUrl: () =>string
}
```

## **四、获取ecpm** 

通过getEcpm()方法可以获取,单位为分。 

## **五、错误码说明** 

|**错误码**|**说明**|
|---|---|
|20400|广告位id为空,请检查请求时传入的广告位ID是否正确|
|20401|获取广告配置异常,请检查广告位ID是否正确,广告位中是否正确配置了广告|
|20402|广告没有填充,请检查广告位中是否正确配置了广告,如果有配置广告属于正常现象可 以换台测试设备进行测试|
|20403|没有初始化SDK,请先初始化SDK再请求广告|
|20404|context传入异常,检查请求广告传入的context是否正常|
|20405|展示时广告内容为null|
|20406|内部错误,可以使用MT_SDK过滤日志联系我们查看具体原因|
|20407|联盟返回的报错|
|**六、备**|**注**|

demo仅供参考,具体以文档为准。如有疑问,请联系开发人员,谢谢~
