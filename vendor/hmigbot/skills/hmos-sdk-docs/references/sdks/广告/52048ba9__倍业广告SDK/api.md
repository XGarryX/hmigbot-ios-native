# **鸿蒙版 倍业SDK** 

## **1. SDK集成** 

### **手动引入har包** 

##### 在oh-package.json5添加依赖 

{ "dependencies": { "mercurysdk": "file:../entry/libs/mercuryadhar.har" } } 

### **配置权限** 

1. 打开app模块的module.json5文件 

2. 添加以下权限:访问网络、获取网络状态、获取广告追踪标识(oaid)、定位(可选)、 传感器(可选) 

"requestPermissions": [
      {
        "name": "ohos.permission.INTERNET",
        "reason": "$string:internet_permission_reason",
      },
      {
        "name": "ohos.permission.LOCATION",
        "reason": "$string:permission_LOCATION",
      },
      {
        "name": "ohos.permission.APPROXIMATELY_LOCATION",
        "reason": "$string:permission_LOCATION",
      },
      {
        "name": "ohos.permission.APP_TRACKING_CONSENT",
        "reason": "$string:oaid_permission_reason",
      },
      {
        "name": "ohos.permission.GET_NETWORK_INFO",
        "reason": "$string:net_permission_reason",
      },
      {
        "name": "ohos.permission.GET_WIFI_INFO",
        "reason": "$string:net_permission_reason",
      },
      {
        "name": "ohos.permission.ACCELEROMETER",
        "reason": "$string:permission_need",
      }
    ]

## **2. SDK初始化** 

建议在应用入口 EntryAbility 

得 onWindowStageCreate(windowStage: window.WindowStage) 方法中调用以下 代码来执行SDK初始化 

async onWindowStageCreate(windowStage: window.WindowStage) { ****** ****** //隐私信息采集配置 MercuryAD.setPrivacyController(new MyPrivacy) //SDK初始化 MercuryAD.init(this.context, "您在倍联后台申请得appId", "您在倍联后台申请得 //设置windowStage MercuryAD.initWindow(windowStage) } 

### **2.1 隐私配置说明** 

import { BYPrivacyController,BYLocation } from 'mercurysdk'; 

//新建继承于BYPrivacyController得类文件,配置以下相关方法得返回值 export class MyPrivacy extends BYPrivacyController { 

/** 

* app在项目中配置权限。在适当时机申请权限,然后用户授权。 

* 1:如果isCanUseAppTrackingConsent()返回false,当sdk需要oaid时,则使用get 

* 2:如果isCanUseAppTrackingConsent()返回true。当sdk需要oaid时,先去检查权限 

* @returns 是否允许SDK获取系统oaid 

*/ 

isCanUseAppTrackingConsent(): boolean { 

return super.isCanUseAppTrackingConsent() } 

/** * 

* @returns 媒体传入的oaid */ getCusOaid(): string | undefined { return super.getCusOaid() } /** 

* app在项目中配置权限。并在合适时机动态申请权限,用户授权。 * 1:当isCanUseLocation()返回false。当sdk需要地理位置信息时,使用  getCusLoc * 2:当isCanUseLocation()返回true。当sdk需要地理位置信息时,先去检查是否已经得 * @returns 是否允许SDK获取系统地理位置信息 */ isCanUseLocation(): boolean { return super.isCanUseLocation() } 

* @returns 媒体传入的地理位置信息 getCusLocation(): BYLocation | undefined { return super.getCusLocation() 是否允许SDK使用ohos.permission.GET_WIFI_INFO权限对应的信息。 返回true,如果应用申请了ohos.permission.GET_WIFI_INFO权限,sdk则可以使用 返回false,sdk则不可以使用。 * @returns isCanUseWifiState(): boolean { return super.isCanUseWifiState() 

/** * 媒体isCanUseWifiState()返回false时,SDK使用getMacAddress()的返回值作为ma * @returns */ getMacAddress(): string | undefined { return super.getMacAddress() } } 

### **2.2 更多配置调用API说明** 

类名:MercuryAD 

**方法名 方法介绍** getVersion(): string 获取当前SDK版本号 init(context: Context, appId: string, SDK初始化方法 appKey: string) setPrivacyController(controller: 隐私相关控制 BYPrivacyController) debug() 调用后开启debug模式,默认不开启 调用后网络请求接口将使用https链接,默认 useHttps() 使用http链接 initWindow(windowStage: 设置WindowStage,用来部分广告加载展示 window.WindowStage) 子窗口 

## **3. 广告位接入** 

### **广告位通用API参考:** 

通用代码位配置参数类:MercuryEntry 

**方法名 方法介绍** setCodeId(codeId: string): MercuryEntry 设置代码位id, **必须设置** setAdSize(widthVP: 设置广告渲染尺寸,单位VP,不设置默认值为0,代表宽 number, heightVP: 度撑满,高度自适应, **可选设置** ,建议在banner及模板 number): MercuryEntry 信息流中使用 

通用广告请求回调类:MercuryLoadListener 

|**方法名**|**方法介绍**|
|---|---|
|onAdLoaded: () => void|广告加载成功|
|onAdError: (err: MercuryErr) => void|广告获取失败|

- 通用广告关闭枚举类:MercuryCloseType 

|**字段**|**含义**|
|---|---|
|UNKNOWN = 0|未知|
|AD_CLICK = 1|广告点击(部分位置适用)|
|SKIP_CLICK = 2|点击了跳过|
|COUNT_DOWN = 3|倒计时结束|

通用渲染配置类:MercuryRenderOption 

|**字段**|**含义**|
|---|---|
|windowStage?: window.WindowStage|设置windowStage,用来启动SubWindow展示广告|
|layoutFullScreen: boolean = false|设置SubWindow是否全屏展示,仅开屏、插屏、激 励位置生效|

### **3.1 开屏** 

具体使用方法可参考demo中得SplashDemoPage.ets 

展示效果预览: 

#### **请求广告:** 

//回调监听 private mLoadListener: MercuryLoadListener = { onAdLoaded: () => { console.log(`回调 - onAdLoaded`); }, onAdError: (err: MercuryErr): void => { console.log(`回调 - onAdError ; err = ${JSON.stringify(err)}`); } } //初始化请求参数,填入广告位id let opt = new MercuryEntry().setCodeId(this.adID) //初始化开屏广告 this.splash = new MercurySplash(opt) //自定义跳过按钮(可选) // this.splash.setCustomSkip(customCloseBtnBuilder) //请求广告 this.splash.loadAd(this.mLoadListener) 

#### **展示广告** 

##### 方法1:新打开subWindow窗口展示 

//设置渲染选项 let renOp = new MercuryRenderOption() //赋值windowStage,用来新建子窗口 renOp.windowStage = DemoConstants.windowStage //展示广告 this.splash.showAd(renOp) 

##### 方法2:view展示 

//定义NodeController组件 @State splashAdComponent?: NodeController = undefined 

........................ ........................ //广告成功后对组件赋值 this.splashAdComponent = this.splash.getAdComponent() 

//builder中使用: NodeContainer(this.splashAdComponent) 

监听渲染回调 

```arkts
this.splash.setRenderListener({ onShow: (): void => { //广告曝光 }, onClick: (): void => { //广告点击 }, onRenderErr: (err: MercuryErr): void => { //广告渲染失败 }, onClose: (type: MercuryCloseType): void => {//广告关闭 } }) 
```

#### **相关API接口说明** 

##### 开屏广告类:MercurySplash 

|**方法名**|**方法介绍**|
|---|---|
|constructor(option: MercuryEntry)|构造方法,初始化广告类|
|loadAd(loadListener: MercuryLoadListener): void|请求广告|
|getPrice(): number|获取价格,单位人⺠币分|
|getAdComponent(): NodeController | undefned|获取用来渲染的广告组件|
|showAd(renderOption: MercuryRenderOption): void|展示广告,将开启子窗口 展示开屏广告|
|setRenderListener(splashRenderListener: MercurySplashRenderListener): void|设置渲染回调|
|setCustomSkip(customSkipBuilder?: WrappedBuilder<[closeBlock: () => void]>): void|设置自定义跳过按钮|

##### 开屏渲染回调类:MercurySplashRenderListener 

|**方法名**|**方法介绍**|
|---|---|
|onShow: () => void|广告曝光|
|onClick: () => void|广告点击|
|onRenderErr: (err: MercuryErr) => void|广告渲染失败|
|onClose: (type: MercuryCloseType) => void|广告关闭|

**3.2 插屏** 

具体使用方法可参考demo中得InterstitialDemoPage.ets 

##### 展示效果预览: 

#### **请求广告:** 

//回调监听 private mLoadListener: MercuryLoadListener = { onAdLoaded: () => { console.log(`回调 - onAdLoaded`); }, onAdError: (err: MercuryErr): void => { console.log(`回调 - onAdError ; err = ${JSON.stringify(err)}`); } } let opt = new MercuryEntry().setCodeId(this.adID) this.mercuryAd = new MercuryInterstitial(opt) this.mercuryAd.loadAd(this.mLoadListener) 

**展示广告** 

let renOp = new MercuryRenderOption() renOp.layoutFullScreen = false this.mercuryAd.showAd(renOp) 

#### **相关API接口说明** 

插屏广告类:MercuryInterstitial 

|**方法名**|**方法介绍**|
|---|---|
|constructor(option: MercuryEntry)|构造方法,初始化广告类|
|loadAd(loadListener: MercuryLoadListener): void|请求广告|
|getPrice(): number|获取价格,单位人⺠币分|
|showAd(renderOption: MercuryRenderOption): void|展示广告,将开启子窗口展 示开屏广告|
|setRenderListener(mRenderListener: MercuryInterstitialRenderListener): void|设置渲染回调|

##### 插屏渲染回调类:MercuryInterstitialRenderListener 

|**方法名**|**方法介绍**|
|---|---|
|onShow: () => void|广告曝光|
|onClick: () => void|广告点击|
|onRenderErr: (err: MercuryErr) => void|广告渲染失败|
|onClose: (type: MercuryCloseType) => void|广告关闭|

### **3.3 模板信息流** 

具体使用方法可参考demo中得LazyFeedDemoPage.ets 

展示效果预览: 

#### **请求广告:** 

//回调监听 private mLoadListener: MercuryLoadListener = { onAdLoaded: () => { console.log(`回调 - onAdLoaded`); }, onAdError: (err: MercuryErr): void => { console.log(`回调 - onAdError ; err = ${JSON.stringify(err)}`); } } let opt = new MercuryEntry().setCodeId(this.adID) this.mercuryAd = new MercuryFeed(opt) this.mercuryAd.loadAd(this.mLoadListener) 

#### **展示广告** 

###### //定义列表数据 

dataSource: FeedListDataSource = FeedViewModel.getFeedListDataSource(20) 

........................
........................
//广告成功后插入数据
  insert(element: MercuryFeed, index: number) {
    const dataItem = new DataItem();
    dataItem.feedAd = element;
    this.dataSource.insertItem(dataItem, index  );
  }
//builder中使用:
        List() {
          LazyForEach(this.dataSource, (item: DataItem, idx: number) => {
            ListItem() {
              if (item.feedAd) {
                // 展示广告
                NodeContainer(item.feedAd.getAdComponent()).width("100%"
                // .height(200)
              } else {
                FeedItemComponent({ itemInfo: item })
                  .reuseId("feeditemcomponent")
              }
            }
          }, (item: DataItem, idx: number) => {
              const feedAdItem = item.feedAd;
              if (feedAdItem) {
                return this?.getUniqueKey(idx);
              }
              // 示例方法,实际开发中需要开发者自行处理
              return item.title.toString();
            }
          )
        }

#### **相关API接口说明** 

广告类:MercuryFeed 

|**方法名**|**方法介绍**|
|---|---|
|constructor(option: MercuryEntry)|构造方法,初始化广告类|
|loadAd(loadListener: MercuryLoadListener): void|请求广告|
|getPrice(): number|获取价格,单位人⺠币分|
|showAd(renderOption: MercuryRenderOption): void|展示广告,将开启子窗口展 示开屏广告|
|setRenderListener(mRenderListener: MercuryFeedRenderListener): void|设置渲染回调|
|getAdComponent(): NodeController | undefned|获取用来渲染的广告组件|

##### 渲染回调类:MercuryFeedRenderListener 

|**方法名**|**方法介绍**|
|---|---|
|onShow: () => void|广告曝光|
|onClick: () => void|广告点击|
|onRenderErr: (err: MercuryErr) => void|广告渲染失败|
|onClose: (type: MercuryCloseType) => void|广告关闭|

### **3.4 激励视频** 

具体使用方法可参考demo中得RewardDemoPage.ets 

展示效果预览: 

#### **请求广告:** 

//回调监听 private mLoadListener: MercuryLoadListener = { onAdLoaded: () => { console.log(`回调 - onAdLoaded`); }, onAdError: (err: MercuryErr): void => { console.log(`回调 - onAdError ; err = ${JSON.stringify(err)}`); } } let opt = new MercuryEntry().setCodeId(this.adID) this.mercuryAd = new MercuryReward(opt) this.mercuryAd.loadAd(this.mLoadListener) 

#### **展示广告** 

let renOp = new MercuryRenderOption() renOp.layoutFullScreen = false this.mercuryAd.showAd(renOp) 

#### **相关API接口说明** 

##### 广告类:MercuryReward 

|**方法名**|**方法介绍**|
|---|---|
|constructor(option: MercuryEntry)|构造方法,初始化广告类|
|loadAd(loadListener: MercuryLoadListener): void|请求广告|
|getPrice(): number|获取价格,单位人⺠币分|
|showAd(renderOption: MercuryRenderOption): void|展示广告,将开启子窗口展 示开屏广告|
|setRenderListener(mRenderListener: MercuryRewardRenderListener): void|设置渲染回调|

渲染回调类:MercuryRewardRenderListener 

|**方法名**|**方法介绍**|
|---|---|
|onShow: () => void|广告曝光|
|onClick: () => void|广告点击|
|onRenderErr: (err: MercuryErr) => void|广告渲染失败|
|onClose: (type: MercuryCloseType) => void|广告关闭|
|onReward: () => void;|激励达成|

#### **相关API接口说明** 

### **3.5 横幅** 

具体使用方法可参考demo中得BannerDemoPage.ets 

展示效果预览: 

#### **请求广告:** 

//回调监听 private mLoadListener: MercuryLoadListener = { onAdLoaded: () => { console.log(`回调 - onAdLoaded`); }, onAdError: (err: MercuryErr): void => { console.log(`回调 - onAdError ; err = ${JSON.stringify(err)}`); } } let opt = new MercuryEntry() .setCodeId(this.adID) .setAdSize(390, 210) this.mercuryAd = new MercuryBanner(opt) this.mercuryAd.loadAd(this.mLoadListener) 

#### **展示广告** 

//定义NodeController组件 @State AdComponent?: NodeController = undefined 

###### //广告成功后对组件赋值 

this.AdComponent = this.mercuryAd.getAdComponent() 

//builder中使用: NodeContainer(this.AdComponent) 

#### **相关API接口说明** 

##### 广告类:MercuryBanner 

|**方法名**|**方法介绍**|
|---|---|
|constructor(option: MercuryEntry)|构造方法,初始化广告类|
|loadAd(loadListener: MercuryLoadListener): void|请求广告|
|getPrice(): number|获取价格,单位人⺠币分|
|showAd(renderOption: MercuryRenderOption): void|展示广告,将开启子窗口展 示开屏广告|
|setRenderListener(mRenderListener: MercuryBannerRenderListener): void|设置渲染回调|

##### 渲染回调类:MercuryBannerRenderListener 

|**方法名**|**方法介绍**|
|---|---|
|onShow: () => void|广告曝光|
|onClick: () => void|广告点击|
|onRenderErr: (err: MercuryErr) => void|广告渲染失败|
|onClose: (type: MercuryCloseType) => void|广告关闭|

### **3.6 原生自渲染** 

具体使用方法可参考demo中得NativeDemoPage.ets 

##### 展示效果预览: 

#### **请求广告:** 

//回调监听 private mLoadListener: MercuryLoadListener = { onAdLoaded: () => { console.log(`回调 - onAdLoaded`); }, onAdError: (err: MercuryErr): void => { console.log(`回调 - onAdError ; err = ${JSON.stringify(err)}`); } } let opt = new MercuryEntry() .setCodeId(this.adID) .setAdSize(390, 210) this.mercuryAd = new MercuryNative(opt) this.mercuryAd.loadAd(this.mLoadListener) 

#### **展示广告** 

//广告成功后赋值广告信息 let adData = native.getSelfRenderData() 

//赋值广告数据信息,此时会联动刷新展示广告 if (adData) { this.nativeData.nativeAd = adData } 

//builder中进行广告组件渲染 NativeAdComponent({ itemInfo: this.nativeData }) 

##### NativeAdComponent 组件代码示例: 

import { DataItem } from "../data/DataItem"; 

// 单独封装的用来展示自渲染广告样式的组件 @Component export struct NativeAdComponent { // 数据来源 @State itemInfo: DataItem = new DataItem(); // 广告关闭标识 @State isClosed: boolean = false // 是否返回了广告来源logo图片 @State hasSourceLogo: boolean = false videoController: VideoController = new VideoController() 

//是否使用推荐的渲染方式 renderSectionRecommend: boolean = true 

aboutToAppear(): void { let sourceLogo = this.itemInfo.nativeAd?.getADSourceLogo() 

this.hasSourceLogo = sourceLogo != undefined && sourceLogo != null && } build() { Column() { Text('顶部空白') .fontSize(55) .backgroundColor(Color.Blue) .height(1000) if (!this.isClosed) { Column() { //标题+关闭按钮 Row() { Text(this.itemInfo.nativeAd?.getTitle()) .fontSize(13) .fontColor($r('app.color.text_h1')) .layoutWeight(1) .height('auto') Image($r('app.media.mry_ic_close')) .fillColor($r('app.color.text_h1')) .width(25) .height(25) .onClick(() => { //广告关闭调用 -- 必须 this.isClosed = true this.itemInfo.nativeAd?.handleClose() }) } .alignItems(VerticalAlign.Center) .width('100%') .height(30) 

//素材渲染区域----start-----if (this.renderSectionRecommend) { 

// 方案一(推荐):使用SDK内部封装好的素材渲染组件(内部处理好了点击、曝光 NodeContainer(this.itemInfo.nativeAd?.getMaterialComponent() .width('100%') } else { 

// 方案二:自渲染素材展示区域,需要自定义适配素材渲染、点击事件、可见性检 

Stack({ alignContent: Alignment.Center }) { //视频类广告 if (this.itemInfo.nativeAd?.isVideo()) { Video({ src: this.itemInfo.nativeAd?.getVideoUrl(), previewUri: this.itemInfo.nativeAd?.getVideoImage(), // controller: this.videoController }) .muted(true) .controls(false) .autoPlay(true) .width('100%') .objectFit(ImageFit.Fill) } else { //图片类广告 Image(this.itemInfo.nativeAd?.getImgList()[0]) .width('100%') } // 特殊交互组件(比如摇一摇、按钮等交互效果)--方案二可选添加 NodeContainer(this.itemInfo.nativeAd?.getInteractionCompone } //点击事件绑定 -- 方案二必须添加 .onClick((event: ClickEvent) => { this.itemInfo.nativeAd?.handleClick(getContext(this), event }) //绑定可见检测事件 -- 方案二必须添加 .onVisibleAreaChange(this.itemInfo.nativeAd?.getVisibleAreaRa (isExpanding: boolean, currentRatio: number) => { this.itemInfo.nativeAd?.handleVisibleAreaChange(isExpandi }) } //素材渲染区域----end------ 

//底部交互区 Row() { // 描述文字 Text(this.itemInfo.nativeAd?.getDesc()) .fontSize(12) .fontColor($r('app.color.text_h2')) .layoutWeight(1) // 广告标识及来源 -- 必须 Row() { if (this.hasSourceLogo) { Image(this.itemInfo.nativeAd?.getADSourceLogo()) .margin({ right: 4 }) 

} Text(this.itemInfo.nativeAd?.getADSource()) .fontSize(10) .textAlign(TextAlign.Center) .fontColor($r('app.color.mry_color_white')) } .alignItems(VerticalAlign.Center) .padding(3) .margin(3) .borderRadius(3) .backgroundColor($r('app.color.mry_color_trans_gray')) // Button('查看详情') .onClick((event: ClickEvent) => { this.itemInfo.nativeAd?.handleClick(getContext(this), eve }) .height(30) } .margin({ top: 10 }) } .padding(8) .width('100%') .backgroundColor(Color.White) } Text('底部空白') .fontSize(55) .height(900) .backgroundColor(Color.Red) } } } 

#### **相关API接口说明** 

##### 广告类:MercuryNative 

|**方法名**|**方法介绍**|
|---|---|
|constructor(option: MercuryEntry)|构造方法,初始化广告类|
|loadAd(loadListener: MercuryLoadListener): void|请求广告|
|getPrice(): number|获取价格,单位人⺠币分|
|showAd(renderOption: MercuryRenderOption): void|展示广告,将开启子窗口展 示开屏广告|
|setRenderListener(mRenderListener: MercuryNativeRenderListener): void|设置渲染回调|
|getSelfRenderData(): MercuryNativeData | undefned|获取渲染元素信息|

##### 渲染回调类:MercuryNativeRenderListener 

|**方法名**|**方法介绍**|
|---|---|
|onShow: () => void|广告曝光|
|onClick: () => void|广告点击|
|onRenderErr: (err: MercuryErr) => void|广告渲染失败|
|onClose: (type: MercuryCloseType) => void|广告关闭|

渲染元素信息类:MercuryNativeData 

|**方法名**|**方法介绍**|
|---|---|
|getMaterialComponent(): NodeController | undefned|(推荐使用):使用SDK内部封装好的素材渲 染组件(内部处理好了点击、曝光等事 件),具体使用请参考demo示例|
|getInteractionComponent(): NodeController | undefned|获取互动组件、摇一摇、按钮等交互组件|
|handleClick(context: Context, event: ClickEvent): void|触发点击事件|
|handleClose(): void|触发广告关闭行为|
|getVisibleAreaRatios(): number[]|onVisibleAreaChange入参1,可见区域监听 数组|
|handleVisibleAreaChange(isExpanding: boolean, currentRatio: number): void|onVisibleAreaChange入参2回调方法中,进 行调用|
|getTitle(): string|获取广告标题|
|getDesc(): string|获取广告描述|
|getADSource(): string|获取广告来源,一般是‘广告’两个字|
|getADSourceLogo(): string|获取广告来源logo,小图片,用来标记区分 广告上游|
|getIconUrl(): string|获取Icon图片地址,小图标|
|isVideo(): boolean|判断是否为视频类广告|
|getVideoImage(): string|获取视频定帧图|
|getImgList(): string[]|获取图片素材地址,可能有多张|
|getVideoUrl(): string|获取视频素材地址|

## **4.错误码** 

|**code**|**含义**|
|---|---|
|1001|网络失败,一般是http返回状态码非200|
|1002|网络请求失败,查看执行日志了解具体原因|
|1003|网络请求失败,不支持的接口返回类型|
|1004|广告请求参数不全|
|217|广告返回信息为空,未填充|
|218|广告返回信息为空,未填充|
|220|广告返回信息为空,未填充|
|226|广告请求执行异常,查看执行日志了解具体原因|
|301|广告渲染执行异常,查看执行日志了解具体原因|

## **5.问题支持** 

如何获取SDK执行日志 

在log中筛选 BYLog 关键字,获取SDK执行日志信息
