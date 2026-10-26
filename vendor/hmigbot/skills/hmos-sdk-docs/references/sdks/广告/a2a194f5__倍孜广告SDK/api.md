# **SDK接入配置** 

# **SDK 接入配置** 

## **1. 概述** 

### **1.1 简介** 

### **1.2 说明** 

本文档旨在帮助 Harmony 应用开发者在程序中快速接入优加 SDK 提供广告填充,为媒体提供变现途径,作为 应用开发者,您只需要进行简单配置,就可以在您的应用中显示定制的广告。关于 SDK 的具体使用方法,请仔 细阅读下面的文档。 

## **2. 开发环境** 

### **2.1 基础配置要求** 

确保您的开发及部署环境符合以下标准: 

- 开发工具:推荐 NEXT Developer Beta3 及以上版本 部署目标:鸿蒙 Next 及以上版本 

- SDK 版本:HarmonyOS 12 及以上版本 

### **2.2 部署 SDK** 

Harmony SDK 支持通过 ohpm(OpenHarmony Package Manager) 工具实现自动化部署,该方式可确 保依赖管理的标准化与高效性。以下为详细操作指引,更多关于 ohpm 的使用细节可查阅 查阅官方文档 

#### **2.2.1 具体部署步骤** 

#### **方式一:通过 ohpm install 命令导入** 

**1、准备工作** 将目标 SDK 文件(如 AMPSSDK_5.3.0.har)存放至本地已知路径(例如 D:\ 目录)。 

**2、执行命令** 打开命令行工具,切换至项目根目录(示例路径:D:\BeiziAdDemo)。 在创建的项目目录下, 进入命令行输入:ohpm install SDK地址 输入以下命令安装依赖: 

D:\BeiziAdDemo> ohpm install  D:\AMPSSDK_5.3.0.0.har 

#### **方式二:通过 oh-package.json5 依赖同步** 

- **1、文件放置** 在项目 entry 目录下创建 libs 文件夹,将 AMPSSDK_5.3.0.har 复制到该目录中。 

- **2、配置依赖** 编辑项目根目录的 oh-package.json5 文件,在 dependencies 字段中添加以下配置: 

{ //... "dependencies": { "biz.beizi.adn": "file:./libs/AMPSSDK_5.3.0.0.har" } } 

至此依赖 Harmony SDK 完成。 

## **3. 配置权限说明** 

添加权限 **注意** :SDK不强制获取可选权限, 即使没有获取可选权限SDK也能正常运行; 获取可选 权限将帮助SDK优化投放广告精准度和用户的交互体验, 提高eCPM. **注意** :SDK本身不会发起动 态权限申请. 

### **3.1 SDK内部已有权限** 

SDK内部已经配置添加了【开放权限(系统授权)】、网络权限、加速度权限、陀螺仪权限,SDK内部必要权 限。开发者不用自己声明添加,这里进行说明。 

**注意** : 这三种权限均为系统授权(system_grant)的开放权限,面向所有应用开放。应用申请 了system_grant权限后,系统将在用户安装应用时,自动把相应权限授予给应用。 

//SDK内置权限 "requestPermissions": [ { "name": "ohos.permission.INTERNET", "reason": "$string:net_work" }, { "name": "ohos.permission.ACCELEROMETER", "reason": "$string:sensor" 

}, { "name": "ohos.permission.GYROSCOPE", "reason": "$string:sensor" } ] 

### **3.2 开发者可选权限** 

开发者可选权限有,获取设备模糊位置信息权限、跨应用关联权限。获取可选权限将帮助SDK优化投放广告 精准度和用户的交互体验, 提高eCPM。如果开发者配置,可以选择在module.json5文件中声明 

//可选权限 "requestPermissions": [ { "name": "ohos.permission.APPROXIMATELY_LOCATION",//获取设备模糊位置信息权限 "reason": "$string:location_reason", "usedScene": {"abilities": ["entry"]} }, { "name": "ohos.permission.APP_TRACKING_CONSENT",//获取OAID所需权限,需要动态申请 "reason": "$string:trancking_reason", "usedScene": { "abilities": [ "entry" ] } } ] 

#### 权限说明 

|系统平台 申请权限|调用时机|使用目的|
|---|---|---|

|Harmony|访问互联网|初始化时|检查设备连网络状态,确保SDK与服务端的 通讯求|
|---|---|---|---|
||加速度传感器数据|展示带有摇一摇和欧拉角组件并允 许使用传感器广告时|优化用户跳转广告方式|
||陀螺仪传感器数据|展示带有摇一摇和欧拉角组件并允 许使用传感器广告时|优化用户跳转广告方式|
||允许应用读取开放匿名设备标 识符|广告请求|广告投放及广告监测归因、精准度、反作 弊|
||访问粗略位置(可选)|广告请求|广告投放及广告监测归因、反作弊|

# **SDK初始化及API说明** 

# **SDK 初始化及 API 说明** 

## **1. 初始化 SDK** 

### **1.1 初始化方法使用** 

初始化 SDK,一般推荐在 Index.ets 或者EntryAbility 中进行,提前做好 SDK 相关的准备。也方 便开屏广告的加载展示。 

export default class EntryAbility extends UIAbility { 

```arkts
initAMPSSDK(){ //1、获取跨应用关联权限 requestOAIDTrackingPermissions() //2、初始化配置 let config: AMPSInitConfig = new AMPSInitConfig.Builder(appId,this.context) //.setApiKey(apiKey)//可选 //.setDebugSetting(true)//可选 //.setIsTestAd(false)//可选 //.set... .build() let callback: AMPSIInitCallback = { initSuccess: (): void => { this.startSplashAD() }, initializing: (): void => { console.log("--------asnp-initializing-----") }, alreadyInit: (): void => { console.log("--------asnp-alreadyInit-----") }, initFailed: (code: number, msg: string): void => { console.log("--------asnp-initFailed-----") } } //3、初始化SDK AMPSAdSdk.init(config,callback) 
```

} 

onWindowStageCreate(windowStage: window.WindowStage): void { let windowClass: window.Window = windowStage.getMainWindowSync() windowClass.setWindowLayoutFullScreen(true) 

this.requestPermission(this.context) 

windowStage.loadContent('pages/Index', (err) => { 

this.initAMPSSDK()//必须放在windowStage.loadContent之后【大多数媒体选择放在Index等启 动页面内,推荐使用】 

hilog.info(0x0000, 'testTag', 'Succeeded in loading the content.'); 

}); } 

} 

## **2. API 说明** 

### **2.1 AMPSAdSdk 方法说明** 

|方法|说明|
|---|---|
|init(config: AMPSInitConfig, callback: AMPSIInitCallback,context: common.Context=getContext())|初始化 SDK 入口|

### **2.2 AMPSAdSdk 初始化参数说明** 

|属性|说明|
|---|---|
|AMPSInitConfig|初始化配置类|
|AMPSIInitCallback|SDK 初始化回调接口|
|common.Context|上下文|

#### **2.2.1 AMPSInitConfig 方法说明** 

SDK 初始化配置类 

|属性|说明|
|---|---|
|setUiModel|设置深浅模式|
|setAdCustomController|设置自定义内容|
|setDebugSetting|开启测试|
|setUseHttps|是否使用https协议|

|属性|说明|
|---|---|
|set...|具体看下面介绍|

#### **2.2.2 AMPSInitConfig 参数说明** 

let config: AMPSInitConfig = new AMPSInitConfig.Builder(appId,this.context) 

#### //.setApiKey(apiKey) 

.setUiModel(ASNPConstants.UiModel.UI_MODEL_AUTO)//这个可以不写默认就 

是UI_MODEL_AUTO自动。可以设置【UI_MODEL_DARK、UI_MODEL_LIGHT】 

.setAdCustomController(new 

AMPSCustomController({isCanUseSensor:true,isSupportPersonalized:true}))//个性化,和传感器 等的设置 

- //.set... 

.setLandStatusBarHeight(true)//设置落地页是否适配状态栏。 

- .setDebugSetting(true)//是否开启debug 

- .setUseHttps(false)//是否使用https 

.setIsTestAd(false).build() 

|属性|所指|设置|必 传|
|---|---|---|---|
|appId|媒体的账户 ID|new AMPSInitConfig.Builder(appId,**this**.context)|是|
|apiKey|媒体的商户 ID|.setApiKey(apiKey)|否|
|_isDebugSetting|日志模式 :默认:falseDebug:打印 SDK 日志 release:不打印 SDK 日志|.setDebugSetting(**true**)|否|
|_isUseHttps|是否开启 HTTPS请求:默认 false 根据 HTTPS 和 HTTP 模式获取对应请求接 口获取对应数据模板|.setUseHttps(isUseHttps:boolean)|否|
|isTestAd|是否测试广告位默认:false 测试时:设置 true|.setIsTestAd(isTestAd: boolean)|否|
|countryCN|国家默 认:CountryType.COUNTRY_TYPE_CHINA_MAINLANDCountryType.COUNTRY_TYPE_OTHER|.setCountryCN(ASNPConstants.CountryType.COUNTRY_TYPE_CHINA_MAINLAND)|否|
|currency|支持的现金类型|.setCurrency(ASNPConstants.CurrencyType.CURRENCY_TYPE_CNY)|否|
|userId|用户 ID|.setUserId(userId: string)|否|
|optionFields|自定义字段 optionFields: HashMap|.setOptionFields(optionFields: HashMap)|否|
|setUiModel|设置 SDK 内部 UI 对手机系统深浅色的适配。|.setUiModel(uiModel: ASNPConstants.UiModel)|否|
|AMPSCustomController|用户自定义内容:new AMPSCustomController 1、isCanUsePhoneState :是否可以使用 PhoneState 权限 2、OAID:当开发者传入之后,默认就会使用传入的 OAID 3、isSupportPersonalized:是否支持个性化 4、getUnderageTag:适龄标记 【 UNKNOWN=-1,MATURITY=0,UNDERAGE=1】 5、userAgent:开发者可获取传入 6、isCanUseSensor:是否可以使用传感器【默认可以】设置为 false 传感 器会失效 7、isLocationEnabled:是否允许 SDK 获取位置。【默认可以】开发者可以 在注册 ohos.permission.APPROXIMATELY_LOCATION 权限,方便 SDK 内部 获取位置;当设置为 false 之后将不会主动获取位置,当然用户可以通过 location 上传位置相关信息。 8、location:类型 AMPSLocation longitude?:经度 latitude?:纬度 coordinate?AMPSConstants.CoordinateType:经 度[WGS84;GCJ02;BAIDU] timeStamp?:位置时间戳|.setAdCustomController(controller: AMPSCustomController)|否|
|setLandStatusBarHeight|设置落地页是否适配状态栏高度:默认适配了|.setLandStatusBarHeight(true)|否|
|setUseHttps|设置使用网络请求协议:默认http请求|.setUseHttps(true)|否|

#### **2.2.3 AMPSIInitCallback 参数说明** 

作为 SDK 初始化状态、成功与否,可以通过 AMPSIInitCallback 回调进行接收是否成功、失败、正在初始化、 已经初始化等状态。 

export interface AMPSIInitCallback { // 定义 initSuccess 方法,无参数 initSuccess(): void; 

// 定义 initializing 方法,无参数 initializing(): void; 

// 定义 alreadyInit 方法,无参数 alreadyInit(): void; 

// 定义 initFailed 方法,接收两个参数:code(数字类型)和 msg(字符串类型) initFailed(code: number, msg: string): void; 

} 

#### 回调方法说明 

|回调方法|回调说明|
|---|---|
|initSuccess|初始化成功|
|initializing|正在初始化|
|alreadyInit|已经初始化|
|initFailed|初始化失败|

## **3. 位置信息收集** 

   - SDK在获取广告时,会判断用户是否同意允许位置信息收集。如果用户配置了位置信息收集权限,SDK 将会默认获取设备位置信息。所以开发者可以选择声明位置信息权限,方便SDK收集信息,当然也可以 通过AMPSCustomControllerlocation的AMPSLocation参数主动上传位置信息。开发者可以选择 在module.json5文件中声明ohos.permission.APPROXIMATELY_LOCATION权限,方便SDK收集信 息,确保在配置中声明了下面权限。当然开发者也可以设置是否允许SDK收集位置信息,初始化配置参 数设置代码如下: 

- let config: AMPSInitConfig = new AMPSInitConfig.Builder(appId, this.context) //... 

.setAdCustomController(new AMPSCustomController({ 

isLocationEnabled:false //fale表示不允许SDK内部收集,默认是true })) 

.build() 

#### 注意:配置文件中需要声明模糊位置信息收集权限 

{ "name": "ohos.permission.APPROXIMATELY_LOCATION", "reason": "$string:location_reason", "usedScene": {"abilities": ["entry"]} } 

## **4. 个性化广告开关设置** 

### **4.1 功能说明** 

- 首先个性化设置会控制是否上传给服务端广告标识符 OAID,如果个性化设置是关闭的,在正式环境下服 务端是不会下发广告数据的。所以默认应该开启支持个性化设置。当然个性化开关的开启意味着,可以 上报给服务端广告标识符,后台才会下发广告。 

- 广告标识符在 Android 和鸿蒙中都是可以通过系统 API 获取唯一标识符的,也就是每台设备都具有唯 一的广告标识符。而在鸿蒙中广告标识符依赖于广告标识符服务,需要向用户动态申请权限。 首先鸿蒙系统中,通过广告标识服务获取 OAID,该服务需要向用户申请授 

- 权:ohos.permission.APP_TRACKING_CONSENT。 

- 此权限是需要用户动态申请授权,理应有用户授权弹窗,在最近 2024 年 8 月份 API 变化之后,默认是无 授权弹窗的,只要动态申请就给允许权限。当然,如果需要弹窗,需要用户在设置-->隐私和安全->跨应 用关联->点击打开【要求应用请求关联】,才会弹窗,有弹窗之后,需要用户点击允许才能决定其是否允 许。 

只有动态申请之后才,可以通过 identifier.getOAID()获取到 OAID。 

根据以上可见,默认个性化只能是开启,避免正式环境无广告下发,如果需要获取用户设备的唯一广告标识符 OAID,最好开发者动态申请权限,否则 SDK 会提供一个零时的未卸载周期内的 OAID。 

### **4.2 实现方式** 

#### **4.2.1 初始化跨应用关联权限【允许,拒绝】** 

根据上述说明:在 SDK 默认个性化是开启状态,开发者获取设备唯一的标识符建议动态申请权限: 

- 1、如果动态申请权限,且 【要求应用请求关联】为默认不勾选。无应用授权弹窗,直接默认会允许。 

- 2、如果用户手动设置【要求应用请求关联】为打开,需要用户点击【允许】才可以。 

注意:配置文件中需要声明跨应用关联权限"ohos.permission.APP_TRACKING_CONSENT" 

{ "name": "ohos.permission.APP_TRACKING_CONSENT", "reason": "$string:app_name", "usedScene": { "abilities": [ "entry" ] } } 

#### 代码检测是否授予权限代码如下: 

//获取OAID官方相关案例代码 

async function requestOAIDTrackingConsentPermissions(context: common.Context): Promise { // 进入页面时,向用户请求授权广告跨应用关联访问权限 

const atManager: abilityAccessCtrl.AtManager = abilityAccessCtrl.createAtManager(); try { 

- //检查用户是否授予了此权限为【允许】,这里需要注意动态申请是不会弹窗的,需要用户到应用跟踪 页面去设置 

let data = await atManager.requestPermissionsFromUser(context, 

- ["ohos.permission.APP_TRACKING_CONSENT"]) 

if (data.authResults[0] == 0) { //表示打开了权限 

//----------------------------OAID在SDK内部已经获取,下面获取OAID部分可以作为了解---------------------------------------- 

//权限打开并不意味着一定会拿到,此API并不适用所有设备类型,所以需要进行判断 

if (canIUse("SystemCapability.Advertising.OAID")) { 

identifier.getOAID((err: BusinessError, data: string) => { 

if (err.code) { 

//获取OAID成功 

const oaid: string = data; 

//----------------------------OAID在SDK内部已经获取,上面获取OAID部分可以作为了解---------------------------------------- 

}else{ //TODO 可以做引导,让用户授权打开跨应用关联未允许。 } 

} catch (err) { 

} } 

#### //检测跨应用关联权限是否授权 

async function requestOAIDTrackingConsentPermissions(context: common.Context): Promise { // 进入页面时,向用户请求授权广告跨应用关联访问权限 

const atManager: abilityAccessCtrl.AtManager = abilityAccessCtrl.createAtManager(); try { 

let data= await atManager.requestPermissionsFromUser(context, 

["ohos.permission.APP_TRACKING_CONSENT"]) return data.authResults[0] == 0 } catch (err) { return false } } 

如果需要关闭个性化,可以通过.setAdCustomController 设置 AMPSCustomController,并设置 isSupportPersonalized = false。【需要注意,如果关闭个性化设置,正式环境是不会返回广告的,所以默认 是 isSupportPersonalized return true】 

//1、创建AMPSCustomController,如果想获取用户设备真实的OAID,需保证应用是否真正允许了跟踪 权限。 

//2、检测是否开启了了个性化开关 //如果个性化开启需要保证动态申请和用户设置了【允许】 //可以使用一下代码判断并设置个性化开启 async  requestOAIDTrackingConsentPermissions(context: common.Context): Promise { // 进入页面时,向用户请求授权广告跨应用关联访问权限 

const atManager: abilityAccessCtrl.AtManager = abilityAccessCtrl.createAtManager(); try { 

let data = await atManager.requestPermissionsFromUser(context, 

["ohos.permission.APP_TRACKING_CONSENT"]) return data.authResults[0] == 0 } catch (err) { return false } } 

//动态申请权限,方便SDK内部获取设备唯一广告标识符 await this.requestOAIDTrackingConsentPermissions(this.context) 

//===初始化 

let config: AMPSInitConfig = new AMPSInitConfig.Builder(appId, this.context) 

//.setApiKey(apiKey) 

//.setDebugSetting(true) 

//.setIsTestAd(false) 

- //.setAdCustomController(new 

AMPSCustomController({isCanUseSensor:true,isSupportPersonalized:true}))//个性化,和传感器 等的设置 

.build() 

AMPSAdSdk.init(config, callback, this.context) 

#### 推荐方式:用户动态申请跨应用关联权限之后进行初始化SDK。 

#### 如果需要打开个性化设置,请认真阅读此篇文档 

由于鸿蒙目前需要动态申请权限,且如果用户点击【要求应用请求关联】,就需要引导用户再次 开启权限。 

#### 推荐实现方式: 

- (1)开发者主动在SDK初始化之前动态申请权限 

- (2)根据代码严格判断是否用户授予了此权限 

- (3)默认来说首次初始化动态申请,8月份版本之后的默认是true,只要保证在初始化SDK之前动态调用权限 申请即可。 

(4)用户如果之前在设置的-->隐私和安全->跨应用关联->点击打开了【要求应用请求关联】,启动SDK初 始化之后,会出现动态授权弹窗,如果用户点击不同意,需要用户再次去应用关联权限允许权限,下次应用初 始化或者轮询配置获取时候,会主动的获取OAID。 

# **原生(模板)广告接入及API说明** 

# **原生广告接入代码** 

## **1. 原生广告介绍** 

原生广告是在列表页或轮播图上显示的广告类型,目前原生广告仅支持模版渲染。 

## **2. 原生广告集成说明** 

1. 原生对象可以重复请求,广告请求成功后,媒体自行存储 NativeAdWrapper 对象数组,如果未存储,重新 loadAd 后,上一个 NativeAdWrapper 对象数组会被移除; 

2. 

   - 原生重复拉取过多后。媒体可根据自身情况手动进行移除,防止内存占用过大。 

3. 在 build 方法中添加 AMPSBuildNativeView({ nativeWrapper: NativeAdWrapper}),进行显示。 

## **3. 原生广告 API 说明** 

#### **3.1.1 AMPSNativeAd 说明** 

|方法|说明|
|---|---|
|**constructor**(uiContext:UIContext,,option:|构造方法创建广告对象,uiContext,option 参数配|
|ampsAd.AdOptions, callBack: INativeAdListener)|置,callBack:回调方法集|
|loadAd|广告请求|

#### **3.1.2 ampsAd.AdOptions 参数** 

|属性|说明|
|---|---|
|spaceId|广告位 ID|
|apiKey|商户 ID|
|timeoutInterval|拉取广告超时时间|
|adCount|请求广告数量|
|s2sImpl|S2S传入的bidToken|
|expressSize|广告宽高,单位 vp|

#### **3.1.3 AMPSNativeAdListener 回调接口说明** 

|方法|说明|
|---|---|
|loadOk: (adItems: Array) => void|原生广告加载成功|
|loadFail: (code: number, message: string) => void|原生广告加载失败|

#### **3.2 AMPSNativeAdWrapper 属性方法说明** 

|属性或方法|说明|
|---|---|
|renderCallBack?: INativeRenderListener|广告渲染数据是否准备成功回调接口|
|expressCallBack?: INativeExpressListener|广告显示相关回调接口|
|interactCallBack?: INativeInteractiveListener|广告交互相关回调接口|
|renderAd()|调用此方法开始准备渲染数据|
|getECPM|获取竞价|
|notifyRTBWin|竞价成功上报|
|notifyRTBLoss|竞价失败上报|

#### **3.2.1 AMPSNativeRenderListener 接口说明** 

|回调方法|说明|
|---|---|
|renderSuccess: (adWrapper: AMPSNativeAdWrapper) => void|广告渲染数据准备成功时回调|
|renderFailed: (adWrapper: AMPSNativeAdWrapper) => void|广告渲染数据准备失败时回调|

#### **3.2.2 AMPSNativeInteractiveListener 接口说明** 

|回调方法|说明|
|---|---|
|onAdShown: (bidId?: string) => void|原生广告视图显示|
|onAdExposure: (bidId?: string) => void|原生广告视图曝光|
|onAdClicked: (bidId?: string) => void|原生广告视图点击|
|toCloseAd: (bidId?: string) => void|原生广告视图关闭|

## **4. 原生广告代码示例** 

#### 广告加载与显示: 

import { AMPSNativeAdView, ampsAd, AMPSNativeAd, AMPSNativeAdWrapper } from 'biz.beizi.adn'; 

import { AMPSNativeAdListener, AMPSNativeInteractiveListener, AMPSNativeExpressListener, AMPSNativeRenderListener } from 'biz.beizi.adn'; 

```arkts
import { promptAction, router } from '@kit.ArkUI'; import { apiKey } from '../entryability/EntryAbility'; import { ParamModel } from './SplashPage'; 
```

@Entry @Component struct NativeAdPage { arr: string[] = ["element-1", "element-2", "element-3", "element-4", "element-5", "element-6", "element-7", "element-8", "element-9", "element-10"] 

@State adItems: Item[] = [] 

@State listHeight: number = 120 

@State heightMap: Map = new Map() 

```arkts
private mRenderCallback:AMPSNativeRenderListener ={ renderSuccess:(adWrapper: AMPSNativeAdWrapper)=>{ adWrapper.interactCallBack = this.mInterCallback adWrapper.expressCallBack = this.expressCallBack this.heightMap.set(adWrapper.adId, 202) setTimeout(()=>{ let ad = new AdItem(adWrapper) this.adItems.splice(2,0,ad) },10) }, renderFailed: (adWrapper: AMPSNativeAdWrapper)=>{ console.log("onAdShown:" + adWrapper.adId) } } private expressCallBack: AMPSNativeExpressListener = { onAdShown: (adId?: string): void => { console.log("onAdShown:" + adId) }, onAdExposure: (adId?: string): void => { console.log("onAdExposure" + adId) } } private mInterCallback: AMPSNativeInteractiveListener = { onAdClicked: (adId?: string): void => { console.log("客户端onAdClicked:" + adId) }, toCloseAd: (adId?: string): void => { 
let index = -1; for (let i = 0; i = 0) { this.adItems.splice(index, 1); } }, onOpenLandingPage: (adId?: string | undefined): void => { console.log("onOpenLandingPage:" + adId) }, onCloseLandingPage: (adId?: string): void => { console.log("onCloseLandingPage:" + adId) } } private callback: AMPSNativeAdListener = { loadOk: (adItems: AMPSNativeAdWrapper[]): void => { for (let adItemsElement of adItems) { adItemsElement.renderCallBack = this.mRenderCallback //adItemsElement.option.mExpressSize = [300,400] adItemsElement.renderAd() } }, loadFail: (code: number, message: string): void => { promptAction.showToast({ message }) } } aboutToAppear(): void { for (let i = 0; i  { ListItem() { Column() { if (item instanceof AdItem) { Column() { AMPSBuildNativeView({ nativeWrapper: item.wrapper }) } } else { Text(`第${item.index + 1}条=${item.message}`) .height("120") .width("100%") .backgroundColor(Color.Blue) .margin(10) .textAlign(TextAlign.Center) } }.width("100%") } }) } 
```

} .width('100%') .height("100%") 

} } class Item { index: number = 0 message: string = '' } class AdItem extends Item { wrapper: AMPSNativeAdWrapper suggestHeight = 200 constructor(aWrapper: AMPSNativeAdWrapper) { super() this.wrapper = aWrapper } } 

## **5. 原生广告注意事项** 

需要在 onAdClicked 回调用方法中,处理数据源,关闭广告。 原生广告高度可自适应,效果最优。 

# **新原生(模板/自渲染)广告接入及API说明** 

## **原生(模板\自渲染)广告集成说明** 

原生广告(模板\自渲染)包含模板和自渲染两种形式的广告,开发者集成的时候根据业务需求决定用模板还 是自渲染形式广告,多用于新闻信息流中,位于app顶部、中部、底部任意一处,横向贯穿整个app页面。 

### **1、原生(模板\自渲染)广告接口说明** 

#### **1.1 AMPSNativeAd 接口说明** 

原生(模板\自渲染),同原生(模板)接口入口都是AMPSNativeAd。 

class AMPSNativeAd { /** 

* uiContext:当前组件的uiContext 

* config: 请求参数 

- nativeAdCallBack:广告请求回调 

* @param uiContext 

* @param config 

* @param nativeAdCallBack */ 

```arkts
constructor(uiContext: UIContext, config: ampsAd.AdOptions, nativeAdCallBack: AMPSNativeAdListener); /** * 请求原生(模板\自渲染)广告 */ load(): void; } 
```

#### **1.2 AMPSNativeAdListener 接口说明** 

作为加载广告的回调结果,loadOk中拿到请求结果。loadFail中返回失败的相关信息。 

export interface AMPSNativeAdListener { loadOk: (adItems: Array) => void; loadFail: (code: number, message: string) => void; } 

#### **1.3 AMPSNativeAdWrapper 接口说明** 

作为广告的数据包装器,AMPSNativeAdWrapper提供了所需的数据和相关回调和接口。 

```arkts
export declare class AMPSNativeAdWrapper { //对应的广告ID readonly adId: string; //内部模板渲染相关的回调 renderCallBack?: AMPSNativeRenderListener; //点击、显示、曝光、关闭等显示 interactCallBack?: AMPSNativeInteractiveListener; //视频相关回调 videoPlayCallBack?: AMPSVideoPlayListener; constructor(asnpNativeAdWrapper?: ASNPNativeAdWrapper); setVideoPlayConfig(playConfig: AMPSAdVideoPlayConfig): void | undefined; //判断是否是模板渲染,false表示自渲染,true表示模板渲染 isNativeExpress(): boolean; //设置视频状态相关监听 setVideoPlayListener(videoPlayListener: AMPSVideoPlayListener): void; //获取视频时长 getVideoDuration(): number; //获取竞价 getECPM(): number; //竞胜上报 notifyRTBWin(winPrice: number, secPrice: number): void; //竞败上报 notifyRTBLoss(winPrice: number, secPrice: number, lossReason: string): void //开始渲染接口 renderAd(): void; //获取广告来源 getAdSource(): string | undefined; //获取标题 getTitle(): string | undefined; //获取描述 getDescription(): string | undefined; //获取 getIntroductionInfo(): string | undefined; //获取简介信息 getIntroductionInfoUrl(): string | undefined; //获取icon地址 getIconUrl(): string | undefined; //获取主图地址 getMainImageUrl(): string | undefined; //获取主题宽度 getMainImageWidth(): number | undefined; 
```

//获取主图高度 getMainImageHeight(): number | undefined; //获取图片列表 getImgList(): Array; //获取主图 getMainImage(): AMPSAdImage | undefined; //获取Action文本 getActionText(): string | undefined; //获取Logo地址 getLogoUrl(isGrey?: boolean): ResourceStr | undefined; //获取视频地址 getVideoUrl(): string | undefined; //获取视频封面 getVideoCoverImage(): AMPSAdImage | undefined; //获取素材类型 getMaterialType(): AMPSMaterialType | undefined; //获取下载信息 getDownloadInfo(): IUnifiedDownloadInfo | undefined; //用于三方【快手】等设置 getVisibleAreaRatios(): number[] | undefined; //用于三方【快手】等设置 getVisibleAreaChangeListener(): ((isVisible: boolean, currentRatio: number) => void) | undefined; //点击回调给SDK内部 getClickHandler(): (context: common.UIAbilityContext, event: ClickEvent, actionType?: AMPSAdItemClickType) => void; //给SDK内部传入绑定的id和容器组件Id prepare(rootAdComponentId: string, uiContext: UIContext, clickViewIds: AMPSArrayList, creativeViewIds: AMPSArrayList): void; } 

#### **1.4 AMPSNativeInteractiveListener 接口说明** 

广告加载成功之后,在loadOk中返回广告相关的数据AMPSNativeAdWrapper,可以通过 给AMPSNativeAdWrapper设置AMPSNativeInteractiveListener监听广告点击、关闭、显示、曝光相关信 息。 

export interface AMPSNativeInteractiveListener { onAdShown: (adId?: string) => void; onAdExposure: (adId?: string) => void; onAdClicked: (adId?: string) => void; toCloseAd: (adId?: string) => void; } 

#### **1.5 AMPSNativeRenderListener 接口说明** 

新原生(模板/自渲染)可能自渲染同时有模板,所以,需要开发者主动调用renderAd可 从AMPSNativeRenderListener接口回调渲染是否成功、失败信息。 

export interface AMPSNativeRenderListener { renderSuccess: (adWrapper: AMPSNativeAdWrapper) => void; renderFailed: (adWrapper: AMPSNativeAdWrapper) => void; } 

### **2、原生(模板\自渲染)广告请求示例** 

import { AMPSAdItemClickType, ampsAd, AMPSAdVideoPlayConfigBuilder, AMPSArrayList, AMPSMaterialType, AMPSNativeAd, AMPSNativeAdListener, AMPSNativeAdWrapper, AMPSNativeContainer, AMPSNativeInteractiveListener, AMPSVideoAutoPlayType, AMPSNativeRenderListener } from 'biz.beizi.adn'; 

```arkts
import { promptAction } from '@kit.ArkUI'; import { util } from '@kit.ArkTS'; import { AMPSBuildNativeAdVideoView } from 'biz.beizi.adn'; import { common } from '@kit.AbilityKit'; import { AdItem, Item } from '../model/Item'; 
```

const TAG: string = "NativeAdPage" 

```arkts
@Entry @Component struct NativeAdPage { private clickIds = new AMPSArrayList(); private rootComponentId: string = util.generateRandomUUID(); 
@State message: string = 'Hello World'; //制造假数据 arr: string[] = ["aaaaaaaaaaa", "bbbbbbbbb", "ccccccccc", "dddddddd", "eeeeeeeee", "aaaaaaaaaaa111", "bbbbbbbbb222", "ccccccccc333", "dddddddd444", "eeeeeeeee555"] @State adItems: Item[] = [] @State listHeight: number = 120 @State heightMap: Map = new Map() mInterCallback: AMPSNativeInteractiveListener = {//广告相关回调【关闭,点击,显示,曝光】 onAdClicked: (adId?: string): void => { console.log("客户端onAdClicked"); }, toCloseAd: (bidId?: string): void => {//关闭删除广告组件Item let index = -1; for (let i = 0; i = 0) { this.adItems.splice(index, 1); } }, onAdShown: (adId?: string): void => { 
```

}, onAdExposure: (adId?: string): void => { 

} } mRenderCallBack:AMPSNativeRenderListener = {//渲染是否完成回调 renderSuccess: (adWrapper: AMPSNativeAdWrapper): void => { //渲染完成,插入广告数据到列表,并显示 let ad = new AdItem(adWrapper) this.adItems.splice(2, 0, ad) }, renderFailed: (adWrapper: AMPSNativeAdWrapper): void => { 

} 

} private callback: AMPSNativeAdListener = {//广告加载回调 loadOk: (adItems: AMPSNativeAdWrapper[]): void => { for (let adItemsElement of adItems) { adItemsElement.interactCallBack = this.mInterCallback adItemsElement.renderCallBack = this.mRenderCallBack 

adItemsElement.setVideoPlayConfig(new AMPSAdVideoPlayConfigBuilder() .videoSoundEnable(true) 

.videoAutoPlayType(AMPSVideoAutoPlayType.AUTO_PLAY) 

.videoLoopReplay(true) .build()) 

```arkts
adItemsElement.setVideoPlayListener({ onVideoReady: () => { console.error("video::时长===" + adItemsElement.getVideoDuration()) }, onVideoPlayStart: () => { console.error("video::播放了?") }, onVideoPause: () => { console.error("video::播放暂停了?") }, onVideoResume: () => { console.error("video::暂停到播放?") }, onVideoPlayComplete: () => { console.error("video::播放完成了?") }, onVideoPlayError: (code, extra) => { console.error("video::错误?") } }) //需要注意,renderAd才会触发模板渲染回调结果。避免 adItemsElement.renderAd() } }, loadFail: (code: number, message: string): void => { promptAction.showToast({ message }) } } ad?: AMPSNativeAd aboutToAppear(): void { for (let i = 0; i  { Image(wrapper.getMainImageUrl()) .width('100%') .height(200) }) } else { Stack() { if (wrapper.getMainImageUrl()) { Image(wrapper.getMainImageUrl()) .width('100%') .height(200) } 
```

if (wrapper.getVideoUrl()) { // 展示视频 Column() { AMPSBuildNativeAdVideoView(wrapper) }.width(200).height('100%') } }.width('100%') .height(200) } if (wrapper.getDescription()) { Row() { Text(wrapper.getDescription()) .width('100%') .layoutWeight(1) .fontSize(14) .fontColor(Color.White) .textAlign(TextAlign.Start) .padding(5) .textShadow({ radius: 2, offsetY: 2, color: Color.Black }) if (wrapper.getActionText()) { Button(wrapper.getActionText()) .type(ButtonType.Normal) .height(20) .backgroundColor('#fffa97fa') .fontColor(Color.White) .fontSize(12) .border({ radius: 5, color: Color.White, width: 1 }) .shadow({ radius: 5, color: '#fffa97fa', offsetY: 3 }) .padding({ left: 5, right: 5, top: 1, bottom: 1 }) .margin({ right: 10, bottom: 5, top: 5 }) .id(this.clickIds.addAdId(util.generateRandomUUID()))//设置组件Id,需要全局保证唯一性, 涉及计费 .onClick((e) => { wrapper?.getClickHandler()(getContext(this) as common.UIAbilityContext, e,AMPSAdItemClickType.COMPLAIN) }) } } 

}.margin(10).shadow({ radius: 10, color: Color.Black, offsetY: 5 }).borderRadius(10) 

build() { Row() { Column() { Row() { List() { ForEach(this.adItems, (item: Item, index) => { ListItem() { Column() { if (item instanceof AdItem && !item.wrapper.isNativeExpress()) { AMPSNativeContainer({ mNativeWrapper: item.wrapper, buildContent: () => { this.buildASNPBody(item.wrapper) } }).id(this.rootComponentId).onAppear(() => { //需要传入根id和设置了点击事件的id item.wrapper.prepare( this.rootComponentId, this.getUIContext(), this.clickIds, new AMPSArrayList()) }) } else { Text(`第${item.index + 1}条=${item.message}`) .height("120") .width("100%") .backgroundColor(Color.Blue) .margin(10) .textAlign(TextAlign.Center) } }.width("100%") } }) }.width("100%") .height("100%") }.width("100%") }.width('100%').height("100%") } } } 

### **3、注意事项** 

开发者自定义自渲染组件,需要设置点击跳转、关闭、投诉的按钮, **跳转** 需要绑定唯一ID,并添加 到AMPSArrayList数组中,通过wrapper.prepare传入。对于自渲染容器AMPSNativeContainer在 其onAppear回调触发之后传入。否则不能点击转化。关键代码如下: 

//判断是广告数据类型且是非模板类型 if (item instanceof AdItem && !item.wrapper.isNativeExpress()) { AMPSNativeContainer({ mNativeWrapper: item.wrapper, buildContent: () => { this.buildBody(item.wrapper) } }).id(this.rootComponentId).onAppear(() => { //需要传入根id和设置了点击事件的id item.wrapper.prepare( this.rootComponentId, this.getUIContext(), this.clickIds, new AMPSArrayList()) }) } 

# **开屏广告接入及API说明** 

# **开屏广告接入** 

## **1. 开屏广告介绍** 

开屏广告是 app 启动时,显示的一种广告形式.提供两种方式显示广告: 

- 1.通过 router 跳转到广告页来显示广告,一键调用 splashAd?.showAd() 

   2. 将 AMPSBuildSplashView 添加到 build 方法中,在自主页面或者启动页中显示 

## **2. 开屏广告集成说明** 

1. 开屏对象可以重复请求,广告请求成功后,未调用显示前不要重复拉取; 

2. 广告关闭后可再次调用 loadAd 后会重新拉取广告。 

## **3. 开屏广告 API 说明** 

### **3.1 AMPSSplashAd 创建参数说明** 

#### **3.1.1 ampsAd.AdOptions 属性说明** 

|属性|说明|必传|
|---|---|---|
|spaceId|广告位 ID|是|
|apiKey|商户 ID|否|
|timeoutInterval|拉取广告超时时间|否|
|splashAdBottomBuilderHeight|开屏底部自定义高度|否|
|expressSize|原生广告的宽高|否|

#### **3.1.2 AMPSSplashAd 方法说明** 

|方法|说明|
|---|---|
|**constructor**(option: ampsAd.AdOptions, callBack: ampsAd.CallBack)|构造方法创建广告对象,option 参数配置,callBack:回调方法集|
|load|广告请求|

|方法|说明|
|---|---|
|showAd|显示广告|
|isReadyAd|是否有可使用的广告|
|getECPM|获取竞价|
|notifyRTBWin|竞价成功上报|
|notifyRTBLoss|竞价失败上报|

##### **showSlash:** 

调用 SDK 内部的开屏显示方法 showAd(splashConfig?: AMPSSplashConfig),有相关参数 AMPSSplashConfig 需要注意。 

export interface  AMPSSplashConfig { bottomWrappedBuilder?: WrappedBuilder//底部自定义内容 routerAnimal?: boolean | undefined | null //是否支持路由动画 } 

###### **3.1.2.1、bottomWrappedBuilder** 

是开发者可以根据自己的需求自定义开屏页底部显示自定义内容。但需要注意 ampsAd.AdOptions 的 splashAdBottomBuilderHeight 是需要和自定义底部内容高度一致的。 

###### **3.1.2.2、routerAnimal** 

调用 SDK 开屏显示,默认有路由动画会有推进来的交互。如果开发者不想要此动画需要设置 routerAnimal 为 boolean,其他情况都是默认路由动画。当然开屏广告页面退出时候,底部页面也需要开发者去除进入动画。 

#### **3.1.3 ampsAd.CallBack 回调方法说明** 

|方法|说明|
|---|---|
|onLoadSuccess?: () => void|开屏广告加载成功|
|onLoadFailure?: (code: number, message: string) => void|开屏广告加载失败|
|onRenderOk?: () => void|开屏广告渲染数据准备成功|
|onRenderFailure?: () => void|开屏广告渲染数据准备失败|
|onAdShow?: () => void|开屏广告显示|
|onAdExposure?: () => void|开屏广告曝光|

|方法|说明|
|---|---|
|onAdClicked?: () => void|开屏广告点击|
|onAdClosed?: () => void|开屏广告关闭|

## **4. 开屏广告代码示例** 

开屏示例根据公司需求具体有四种设置类型:每种设置都有其对应的案例,开发者可以查看 AMPSAdDemo 中相关的页面。 

1、调用 SDK 内部的开屏页、无底部自定义内容 =》无需给 SDK 设置自定义视图。 

#### 【 **SplashAdBySDKShowTestPage.ets** 】 

//TODO 只需要在回调中调用showSlash onRenderOk: () => { //TODO 调用SDK即可 this.splashAd?.showAd() } 

2、调用 SDK 内部的开屏页、需要底部自定义内容 =》需要给 SDK 设置自定义试图。 

#### 【 **SplashAdBySDKShowCmBottomTestPage.ets** 】 

onRenderOk: () => { 

//TODO 调用SDK即可,需要注意自定义底部内容:需要底部容器Builder的高度需要 和option.splashAdBottomBuilderHeight一致 this.splashAd?.showAd(wrapBuilder(SplashBottomVIew)) }, //这里的splashBottomHeightVP需要和SplashBottomVIew的高度一致。 this.option.splashAdBottomBuilderHeight = splashBottomHeightVP this.splashAd = new AMPSSplashAd(this.option, this.callback) 

3、自定义开屏页在自己页面、不需要自定义内容 =》无需自己定义容器。 

#### 【 **SplashAdCustomBuildTestPage.ets** 】 

```arkts
import { promptAction, router } from '@kit.ArkUI'; import { ampsAd, AMPSSplashAd, AMPSBuildSplashView } from 'biz.beizi.adn'; import { splashBottomHeightVP, SplashBottomVIew, WarmTopView } from '../../components/SplashBottomView'; import { SplashTopBarView } from '../../components/SplashTopBarView'; import { SplashWarnType } from '../../data/ItemModel'; /** 
```

#### * 注意: 

- 自己页面通过SplashTopBarView来调用开屏广告页面 

- 1、需要自己结合开屏页面状态处理onBackPress 

* 2、通过状态显示页面内容:例如:this.hasSplash = true */ @Entry @Component struct SplashAdCustomBuildTestPage { @State hasSplash: boolean = false splashAd?: AMPSSplashAd option: ampsAd.AdOptions = { spaceId: '15288', adCount: 1, timeoutInterval: 12000 } callback: ampsAd.CallBack = { onLoadSuccess: (): void => { }, 

```arkts
onLoadFailure: (code: number, message: string): void => { promptAction.showToast({ message: `${message}:code=${code}` }) 
```

onRenderOk: () => { //TODO 测量摆放约束计算成功,可去显示了 this.hasSplash = true 

onAdShown: (): void => { console.log('onAdShown') 

onAdExposure: (): void => { 

console.log('onAdExposure') 

onAdClicked: (): void => { console.log('onAdClicked') 

onAdClosed: (): void => { 

console.log('onAdClosed') this.hasSplash = false 

onOpenLandingPage: () => { this.hasSplash = false } } 

aboutToAppear(): void { let routerOption = router.getParams() as Record 

if (routerOption) { this.option.spaceId = routerOption['spaceId'] } this.splashAd = new AMPSSplashAd(this.option, this.callback) 

//TODO 一般会在aboutToAppear()中自动加载广告。当然建议开屏页面在EntryAbility内部初始化。 可参照EntryAbility进行配置。 this.splashAd?.load() } build() { Column() { Stack() { Column(){ SplashTopBarView($r('app.string.splash_ad')) WarmTopView(SplashWarnType.CUSTOM) 

Column({ space: 10 }) { Text("自己页面内容") .fontSize(18) .fontColor(Color.Red) .fontWeight(FontWeight.Normal) .textShadow({ color: Color.Black, radius: 2, offsetY: 2, offsetX: 2 }) .margin({ top: 50, bottom: 20 }) Button('加载开屏广告') .onClick(() => { this.splashAd?.load() }) } .justifyContent(FlexAlign.Center) .layoutWeight(1) .width('100%') } //TODO 通过状态控制开屏控件页面内容的显示与否 if (this.hasSplash) { AMPSBuildSplashView(this.splashAd) } } 

} } 

//TODO 开发者需要屏蔽开屏页面显示时不可被【侧滑、底部导航栏返回键】等影响,从而导致广告曝 光所受影响。 

/** * * @returns */ onBackPress(): boolean | void { //显示开屏广告是拦截返回 if (this.hasSplash) { return true } return false } } 

4、自定义开屏页在自己页面、需要添加底部内容 =》需自己在自身布局内部定义容器。 

#### 【 **SplashAdCustomBuildBottomTestPage.ets** 】 

```arkts
import { promptAction, router } from '@kit.ArkUI'; import { ampsAd, AMPSSplashAd, AMPSBuildSplashView } from 'biz.beizi.adn'; import { splashBottomHeightVP, SplashBottomVIew, WarmTopView } from '../../components/SplashBottomView'; import { SplashTopBarView } from '../../components/SplashTopBarView'; import { SplashWarnType } from '../../data/ItemModel'; /** 
```

* ����注意:SplashBottomView高度需要和option.splashAdBottomBuilderHeight一致 

- 1、自己定义底部内容以及底部高度 

* 2、option.splashAdBottomBuilderHeight = splashBottomHeightVP【需要和底部高度一致】 

* 3、需要自己结合开屏页面状态处理onBackPress */ @Entry @Component struct SplashAdCustomBuildBottomTestPage { @State hasSplash: boolean = false splashAd?: AMPSSplashAd option: ampsAd.AdOptions = { spaceId: '15288', adCount: 1, timeoutInterval: 12000 } callback: ampsAd.CallBack = { 

```arkts
onLoadSuccess: (): void => { }, onLoadFailure: (code: number, message: string): void => { promptAction.showToast({ message: `${message}:code=${code}` }) }, onRenderOk: () => { //TODO 测量摆放约束计算成功,可去显示了 this.hasSplash = true }, onAdShown: (): void => { console.log('onAdShown') }, onAdExposure: (): void => { console.log('onAdExposure') }, onAdClicked: (): void => { console.log('onAdClicked') }, onAdClosed: (): void => { console.log('onAdClosed') this.hasSplash = false }, onOpenLandingPage: () => { this.hasSplash = false } } aboutToAppear(): void { let routerOption = router.getParams() as Record if (routerOption) { this.option.spaceId = routerOption['spaceId'] } //TODO 别忘记底部自定义高度需要这里设置,保证测量正确 this.option.splashAdBottomBuilderHeight = splashBottomHeightVP this.splashAd = new AMPSSplashAd(this.option, this.callback) //TODO 一般会在aboutToAppear()中自动加载广告。当然建议开屏页面在EntryAbility内部初始化。 可参照EntryAbility进行配置。 this.splashAd?.load() } 
```

build() { Column() { Stack() { //TODO 通过状态控制开屏控件页面内容的显示与否 if (this.hasSplash) { 

Column() { Stack() { AMPSBuildSplashView(this.splashAd) } .flexGrow(1) .width('100%') .height(100) //TODO 自己写相关设计即可 //wrapBuilder(SplashBottomVIew).builder() Row() { Image($r("app.media.asnp_ad_logo")) .width(50) .height(50) .margin({ right: 20 }) Text("倍孜网络") .fontSize("20vp") .fontColor(Color.Black) } .alignItems(VerticalAlign.Center) .justifyContent(FlexAlign.Start) .backgroundColor(Color.White) .padding(20) .width('100%') .height(splashBottomHeightVP) } .width("100%") .height("100%") } } 

SplashTopBarView($r('app.string.splash_ad')) WarmTopView(SplashWarnType.CUSTOM_BOTTOM) 

Column({ space: 10 }) { Text("自己页面内容") .fontSize(18) .fontColor(Color.Red) .fontWeight(FontWeight.Normal) .textShadow({ color: Color.Black, radius: 2, offsetY: 2, offsetX: 2 }) 

.margin({ top: 50, bottom: 20 }) Button('加载开屏广告') .onClick(() => { this.splashAd?.load() }) } .justifyContent(FlexAlign.Center) .layoutWeight(1) .width('100%') } } //TODO 开发者需要屏蔽开屏页面显示时不可被【侧滑、底部导航栏返回键】等影响,从而导致广告曝 光所受影响。 /** * * @returns */ onBackPress(): boolean | void { //显示开屏广告是拦截返回 if (this.hasSplash) { return true } return false } } 

#### 开屏页广告长见在 EntryAbility 加载与显示: 

```arkts
import { abilityAccessCtrl, AbilityConstant, Permissions, UIAbility, Want } from '@kit.AbilityKit'; import { hilog } from '@kit.PerformanceAnalysisKit'; import { window } from '@kit.ArkUI'; 
```

import { ampsAd, AMPSAdSdk, AMPSIInitCallback, AMPSInitConfig, AMPSSplashAd } from 'biz.beizi.adn'; 

export  const appId = "12379" export  const apiKey = "10023" export default class EntryAbility extends UIAbility { 

//动态向用户申请跨应用关联权限,保证SDK能获取到广告标识符OAID requestPermission(context: Context) { let atManager = abilityAccessCtrl.createAtManager(); const permissions: Array = ['ohos.permission.APP_TRACKING_CONSENT']; //requestPermissionsFromUser会判断权限的授权状态来决定是否唤起弹窗 atManager.requestPermissionsFromUser(context, permissions).then((data) => { 

```arkts
let grantStatus: Array = data.authResults; let length: number = grantStatus.length; for (let i = 0; i ) => { 
```

console.error('ksadsdk', `requestPermissionsFromUser failed, code is ${err.code}, message is ${err.message}`); 

}); } //初始化广告SDK initAMPSSDK(){ //===初始化 let config: AMPSInitConfig = new AMPSInitConfig.Builder(appId,this.context) //.setApiKey(apiKey) //.setDebugSetting(false) //.setIsTestAd(false) .build() let callback: AMPSIInitCallback = { initSuccess: (): void => { console.log("--------asnp-initSuccess-----") this.startSplashAD() }, initializing: (): void => { console.log("--------asnp-initializing-----") }, alreadyInit: (): void => { console.log("--------asnp-alreadyInit-----") }, initFailed: (code: number, msg: string): void => { console.log("--------asnp-initFailed-----") } } AMPSAdSdk.init(config,callback) } //开屏广告 startSplashAD() { let adLoadCallback: ampsAd.CallBack = { onLoadSuccess: (): void => { }, onLoadFailure: (code:number,message:string)=>{ console.log('---------------asnp-onLoadFailure----code:' + code.toString() + "---message:" + message); }, onRenderOk: (): void => { splashAd.showAd() 

}, onAdShown: (): void => { console.log('-------onAdShown-------') }, onAdExposure: (): void => { console.log('-------onAdExposure-------') }, onAdClicked: (): void => { console.log('-------onAdClicked-------') }, onAdClosed: (): void => { console.log('-------onAdClosed-------') }, onOpenLandingPage: ()=>{ console.log('-------onOpenLandingPage-------') }, onCloseLandingPage:()=>{ console.log('-------onCloseLandingPage-------') } } let option: ampsAd.AdOptions = { apiKey: apiKey, spaceId: '15288', } 

```arkts
let splashAd: AMPSSplashAd = new AMPSSplashAd(option,adLoadCallback) splashAd.load() } onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void { hilog.info(0x0000, 'testTag', '%{public}s', 'Ability onCreate'); } 
onWindowStageCreate(windowStage: window.WindowStage): void { //建议动态申请权限放在初始化之前。 this.requestPermission(this.context) // Main window is created, set main page for this ability hilog.info(0x0000, 'testTag', '%{public}s', 'Ability onWindowStageCreate'); let windowClass: window.Window = windowStage.getMainWindowSync() windowClass.setWindowLayoutFullScreen(true) windowStage.loadContent('pages/Index', (err) => { if (err.code) { hilog.error(0x0000, 'testTag', 'Failed to load the content. Cause: %{public}s', JSON.stringify(err) ?? ''); return; 
```

this.initAMPSSDK() 

hilog.info(0x0000, 'testTag', 'Succeeded in loading the content.'); 

}); } } 

## **5. 开屏广告注意事项** 

- 开屏广告加载必须在 SDK 初始化完成之后。 

- 广告数据准备成功(onRenderOk)之后,在调用 showSlash 显示广告。 Splash 不支持横屏的应用。 

# **混淆配置** 

# **应用混淆** 

打release包时,需要注意不要将AMPSSDK的代码混淆。 

1. 打开entry目录下的build-profile.json5,在release代码块的arkOptions配置中添加如下内容(若已 经自动生成,则不用手动配置): 

"obfuscation": { "ruleOptions": { "enable": true, "files": [ "./obfuscation-rules.txt" ] } } 

2. 打开entry目录下的obfuscation-rules.txt文件,添加如下代码: 

-keep oh_modules/biz.beizi.adn -keep oh_modules/amps_common 

# **错误码说明** 

# **ASNP 错误码说明** 

目前 SDK 错误码分为三类,主要是方便开发者对于 SDK 初始化、广告加载显示、网络请求三个模块,快速进 行错误排查定位。 

根据模块分为三种类型【AMPSInitError】、【AMPSAdError】、【AMPSNetError】。 

# **1、AMPSInitError** 

|错误码|说明|排查方向|
|---|---|---|
|1001|init success|初始化成功|
|1002|already_init|重复调用 SDK 初始化|
|1004|config response error|全局配置解析失败|
|1005|config app id or apiKey error|检查 AppID 和 ApiKey 是否正确【空】|
|1009|error unexpected|初始化过程中意外错误【需仔细分析定位】|
|1010|error init storage fail|初始化本地数据库【kv、db】错误|

# **2、AMPSAdError** 

|错误码|说明|排查方向|
|---|---|---|
|2003|sdk not init|SDK 初始化全局配置失败|
|2004|request too often|过于频繁请求|
|2005|ad type being complained|广告请求被投诉期拦截|
|2006|request timeout|获取广告超时了|
|2007|request error|请求结果失败,广告信息不全|
|2008|invalid config|广告配置问题|
|2009|ad is requesting or has been gotten|重复请求加载广告接口|
|2010|unite control|联合控制策略尝试拦截广告请求错误|
|2011|render failed|弹窗渲染失败|

|错误码|说明|排查方向|
|---|---|---|
|2099|error unexpected|广告加载过程中异常|

# **3、AMPSNetError** 

|3|config parse fail|网络请求,解密,解析对象出错|
|---|---|---|
|4|response parse error|广告加载过程中异常【暂未使用】|
|7|request timeout|请求超时【暂未使用】|

# **常见问题** 

常见问题 

# **插屏广告接入及API说明** 

# **插屏广告接入** 

## **1. 插屏广告介绍** 

插屏广告是 app 运行时,以弹窗显示的一种广告形式。 

## **2. 插屏广告集成说明** 

1. 插屏对象可以重复请求,广告请求成功后,未调用显示前不要重复拉取; 

2. 广告关闭后可再次调用 loadAd 后会重新拉取广告。 

3. 提供两种集成方式 

- 1.通过AMPSInterstitialAd的showAd方法弹窗显示广告 

- 2.通过在布局中使用AMPSBuildInterstitialView直接加载 

## **3. 插屏广告 API 说明** 

### **3.1 AMPSInterstitialAd 创建参数说明** 

#### **3.1.1 ampsAd.AdOptions 属性说明** 

|属性|说明|必须|
|---|---|---|
|spaceId|广告位 ID|是|
|apiKey|商户 ID|否|
|timeoutInterval|拉取广告超时时间|否|

#### **3.1.2 AMPSInterstitialAd 方法说明** 

|方法|说明|
|---|---|
|**constructor**(option: ampsAd.AdOptions, callBack: ampsAd.CallBack)|构造方法创建广告对象,option 参数配置,callBack:回调方法集|
|loadAd|广告请求|

|方法|说明|
|---|---|
|showAd|通过弹窗形式展示广告,参数传当前组件 this|
|getECPM|获取竞价|
|notifyRTBWin|竞价成功上报|
|notifyRTBLoss|竞价失败上报|

#### **3.1.3 AMPSBuildInterstitialView 使用说明** 

AMPSBuildInterstitialView 是通过组件形式直接在布局中显示方式。结合Stack层叠布局达到弹窗效果。 

1.通过AMPSBuildInterstitialView开发者在布局中利用Stack自行根据回调显示和关闭控制。 

build() { Stack() { Scroll() { Column({ space: 10 }) { Text("页面显示内容") } } .height('100%') .padding({ top: 50 }) //通过AMPSBuildInterstitialView显示插屏内容 if (this.showFlag) { AMPSBuildInterstitialView(this.interAd) } } } 

2.在回调方法 onRenderOk 中 设置showFlag 为 true,刷新页面显示广告。在关闭回调中监听关闭,通 过showFlag状态移除广告组件。 

� onRenderOk: (): void => { this.showFlag = true }, onAdClosed: (): void => { this.showFlag = false } 

#### **3.1.4 ampsAd.CallBack 回调方法说明** 

|方法|说明|
|---|---|
|onLoadSuccess?: () => void|插屏广告加载成功|
|onLoadFailure?: (code: number, message: string) => void|插屏广告加载失败|
|onRenderOk?: () => void|插屏广告渲染数据准备成功|
|onRenderFailure?: () => void|插屏广告渲染数据准备失败|
|onAdShown?: () => void|插屏广告显示|
|onAdExposure?: () => void|插屏广告曝光|
|onAdClicked?: () => void|插屏广告点击|
|onAdClosed?: () => void|插屏广告关闭|
|onVideoPlayStart?: () => void|插屏素材视频播放开始|
|onVideoPlayEnd?: () => void|插屏视频素材播放结束|
|onVideoPlayError?: () => void|插屏视频素材播放异常|
|onVideoSkipToEnd?: () => void|插屏视频素材跳到结束|

## **4. 插屏广告代码示例** 

#### 广告加载与显示: 

@Entry @Component struct InterstitialPage { 

spaceId: string = TextIds.AMPS_SPACE_ID_INTERSTITIAL 

@State showAd: boolean = false 

@State isLoading: boolean = false 

pathStack: NavPathStack = new NavPathStack() 

callback: ampsAd.CallBack = { 

onLoadSuccess: (): void => { 

console.log('-----InterstitialPage-onLoadSuccess------') 

}, 

onLoadFailure: (code: number, message: string): void => { 

console.log('-----InterstitialPage-onLoadFailure:'+ message) promptAction.showToast({ message: `${message}:code=${code}` }) 

}, onRenderOk: (): void => { 

console.log('-----InterstitialPage-onRenderOk------') //方式一 if (this.interAd.hasSHowAdMethod()) { 

this.interAd.showAd({ windowStage: EntryAbility.windowStage,uiContext:this.getUIContext() }) 

} else { //方式二 this.showAd = true } 

}, onAdShow: (): void => { console.log('-----InterstitialPage-onAdShow------') }, onAdExposure: (): void => { console.log('-----InterstitialPage-onAdExposure------') }, onAdClicked: (): void => { console.log('-----InterstitialPage-onAdClicked------') }, onAdClosed: (): void => { this.showAd = false console.log('-----InterstitialPage-onAdClosed------') }, onVideoPlayStart(){ console.log('-----InterstitialPage-onVideoPlayStart------') }, onVideoPlayEnd(){ console.log('-----InterstitialPage-onVideoPlayEnd------') }, onVideoPlayError(){ console.log('-----InterstitialPage-onVideoPlayError------') }, onVideoSkipToEnd(){ console.log('-----InterstitialPage-onVideoSkipToEnd------') } } 

interAd: AMPSInterstitialAd = new AMPSInterstitialAd({ spaceId: this.spaceId, }, this.callback) 

requestInterAd() { this.interAd = new AMPSInterstitialAd({ spaceId: this.spaceId, }, this.callback) this.interAd.load() } 

build() { Stack() { Column() { Row() { Button("返回") .fontColor(Color.Black) .fontSize(22) .align(Alignment.BottomStart) .backgroundColor(Color.Transparent) .onClick(() => { router.back() }) } .alignItems(VerticalAlign.Bottom) .width('100%') .height("60") Column({ space: 10 }) { Row({ space: 5 }) { Text("spaceId:") TextInput({ placeholder: '请输入spaceId', text: $$this.spaceId }).layoutWeight(1) } .width('80%') if (this.isLoading) { Text("广告加载中。。。") } else { Button('加载插屏广告') .onClick(() => { this.requestInterAd() }) } } .justifyContent(FlexAlign.Center) .layoutWeight(1) .width('100%') } if (this.showAd) { Column() { Stack() { AMPSBuildInterstitialView(this.interAd) } .flexGrow(1) 

.width('100%') .height("100%") } .width("100%") .height("100%") } } } } 

## **5. 插屏广告注意事项** 

- 插屏广告加载必须在 SDK 初始化完成之后。 

- 广告数据准备成功(onRenderOk)之后,再调用 showAd 方法或者通过Stack方式通过 AMPSBuildInterstitialView组件进行显示。 

# **SDK更新日志** 

|版本号|更新日志|更新日期|
|---|---|---|
|5.0.0.14|AMPS 基础发布版本 beta|2025-01-21|
|5.0.0.15|AMPS 统一版本 beta|2025-04-10|
|5.0.0.16|AMPS 增加 S2S beta|2025-04-23|
|5.0.1.0|AMPS 多渠道竞价优化 beta|2025-05-21|
|5.0.1.1|AMPS 自渲染反作弊兼容性处理|2025-05-27|
|5.3.0|【修复】已知问题。【优化】渲染速度。【新增】原生自渲染广告形式。|2025-06-05|

# **S2S广告** 

## **S2S广告基本流程** 

1. 

2. 

3. 

   - 流量方App通过调用我方SDK方法获取请求Token 

   - 流量方App将token发送给流量方服务器. 

   - 流量方服务器请求我方服务器, 获取Bid广告返回. 并将返回中"respToken"内容下发给流量方App. 

4. 流量方App使用respToken返回内容. 调用我方SDK, 创建对应类型的广告示例, 通过我方SDK进行广 告的渲染展示. 

## **S2S广告接入及API说明** 

### **版本说明** 

S2S广告形式, 适用于AMPSSDK_5.0.0.15及以上版本 

### **获取S2S广告Token** 

通过AMPSSDK获取BidTokenManager对象, 并通过该对象获取token 

|方法名称|参数|描述|
|---|---|---|
|getBidToken|String|通过广告位ID获取token|

#### 示例: 

//获取bidToken 

//1、通过then获取。 

AMPSAdSdk.getBidingManager().getBidToken(this.option.spaceId).then((bidToken) => { 

#### }) 

#### //或者await 

let bidToken = await AMPSAdSdk.getBidingManager().getBidToken(this.option.spaceId) 

### **获取RespToken** 

请参看服务器相关文档.在AMPSDemo中也有简单请求案例。 

### **使用RespToken创建广告位** 

使用获取的RespToken创建广告对象. 通过给广告请求参数option的impAdInfo设 置RespToken. 之后创建广告位可根据广告位类型参考广告接入及API说明文档. 

|方法名称|参数|描述|
|---|---|---|
|s2sImpl|string|设置S2S广告RespToken, 设置非空字符串即视为以S2S方式使用广告位|

设置RespToken示例: 

option: ampsAd.AdOptions = { spaceId: '15288' } this.option.s2sImpl = s2sImpAdInfoModel?.respToken this.splashAd = new AMPSSplashAd(this.option, this.callback) this.splashAd.load() 

以开屏为例简单使用示例: 

//1、第一步获取bidToken AMPSAdSdk.getBidingManager().getBidToken(this.option.spaceId).then(async (bidToken) => { //2、第二步拿着bidToken和服务器去交互 let s2sImpAdInfoModel = await S2SHttpUtil.getImpAdInfoByHttp({ bidToken:bidToken, spaceId:this.option.spaceId, mAdType:"1", cpmBidFloor:"100" }) //3、拿到服务端返回respToken设置给option.s2sImpl this.option.s2sImpl = s2sImpAdInfoModel?.respToken this.splashAd = new AMPSSplashAd(this.option, this.callback) this.splashAd.load() }) 

# **RTB实时竞价广告** 

## **RTB实时竞价广告** 

所有广告形式均属于RTB竞价广告 当广告形式以RTB竞价形式使用时. 竞价成功和竞价失败接口 **必须调用** 以避免收益损失 

#### 1. 获取竞价ECPM 

一般广告形式, 通过调 用getECPM() 方法获取, 单位: 分 原生广告(模板/自渲染), 通 过 AMPSNativeAdWrapper实 例, 调 用getECPM(), 单位: 分 

#### 代码示例 

//以插屏举例 interstitialAd.getECPM(); 

#### 2. 调用竞价成功 

当广告竞价成功时, 需要调 用notifyRTBWin(int, int)方 法,通知SDK竞价成功结果. 传入竞胜价和 次高价. 

当使用medation能力时(初始化设 置.setIsMediation(true)传入true 时, 该接口可 以不调用) 

代码示例 

//以插屏举例 interstitialAd.notifyRTBWin(winPrice, secPrice); 

#### 3. 调用竞价失败 

当广告竞价失败时, 需要调 用notifyRTBLoss(int, int, string)方 法,通知SDK竞价失败结果. 传入 竞胜价和次高价及失败原因. 当使用medation能力时(初始化设 置.setIsMediation(true)传 入 true时 , 该接口可以不调用) 

代码示例 

//以插屏举例 

interstitialAd.notifyRTBLoss(winPrice, secPrice, lossReason);
