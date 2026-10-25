# **Ping++ 鸿蒙 next 聚合支付类库使用说明** 

## **版本** 

1.2.3 

## **说明** 

- 仅支持 live 模式的 charge 和 order 支付 

- 当前 SDK 仅支持鸿蒙 next 系统 

- 编译 IDE 版本: DevEco Studio 6.0.0 Release 

- 编译 鸿蒙 SDK 版本: 5.0.0(API12) 

- 目前支持支付宝 app 支付,银联云闪付 app 支付,微信 app 支付 

- 类库已经导入了支付宝/云闪付以及微信支付的 SDK 三方库,项目依赖中不能重复导入 

## **下载安装** 

ohpm i @pingplusplus/pingppsdk 

## **使用说明** 

import { Pingpp } from '@pingplusplus/pingppsdk'; 

//同时支持 charge 和 order 对象 Pingpp.createPayment(string) 

### **常见问题:** 

- 微信支付成功后无法在 onResp 内获取到微信回调 

   - 解决在 App module 的 module.json5 里面的 scheme 声明去掉 wxopensdk 

##### 报错 

- Please check useNormalizedOHMUrl in the project-level build-profile.json5 file. 

   - 解决:鸿蒙要求上架的 SDK 支持字节码编译,DevEco-Studio 5.0.3.502 开始支持字节码。 

   - app 根路径下的 build-profile.json5 配置 useNormalizedOHMUrl 。 

{ "app": { "products": [ { "buildOption": { "strictMode": { "useNormalizedOHMUrl": true } } } ] } } 

### **支付宝 app 支付** 

- 请确认 entry 模块的 module.json5 是否配置了"querySchemes": ["https"] 不再需要配置 "querySchemes": ["alipays"],除非你需要非 sdk 场景打开支付宝 

#### **使用示例** 

```arkts
Button('支付宝') .onClick(async () => { //传入调用 charge 或者 order 支付接口返回的 json 字符串 let data = '{"id":"ch_101240731394713026560003","object":"charge",......}' 
```

let result = await Pingpp.createPayment(data) let resultStatus = result?.get('resultStatus') let memo = result?.get('memo') }) 

#### **支付宝支付响应 resultStatus 结果码含义** 

该参数仅建议作为前端 UI 结果处理展示使用,用户实际支付结果请使用查询接口或者支付回调 webhook 事件中状态判断 

|**返回码**|**含义**|
|---|---|
|9000|订单支付成功。|
|8000|正在处理中,支付结果未知(有可能已经支付成功),请查询商家订单列表中订单的支付状态。|
|4000|订单支付失败。|
|5000|重复请求。|
|6001|用户中途取消。|
|6002|网络连接出错。|
|6004|支付结果未知(有可能已经支付成功),请查询商家订单列表中订单的支付状态。|
|其它|其它支付错误。|

### **微信app 支付** 

微信支付调用会同步返回拉起微信的状态通过 appInvokeResult 属性获取是否拉起成功 微信支付回调中errCode值列表 

|**名称**|**描述**|**解决方案**|
|---|---|---|
|0|成功|展示成功页面|
|-1|错误|可能的原因:签名错误、未注册AppID、项目设置AppID不正确、注册的AppID与设置的不 匹配、其他异常等。|
|-2|用户 取消|无需处理。发生场景:用户不支付了,点击取消,返回App。|

##### EntryAbility.ets 配置 onNewWant 回调处理 

```arkts
onNewWant(want: Want, launchParam: AbilityConstant.LaunchParam): void { let WXApi = wxopensdk.WXAPIFactory.createWXAPI("您的微信 app 支付应用 id") if(this.uiContext && want?.parameters && want?.parameters['ohos.aafwk.param.callerB WXApi.handleWant(want, WXEventHandler) } } 
```

WXEventHandler 参考 

import { wxopensdk } from "pingppsdk" 

export type OnWXReq = (req: wxopensdk.BaseReq) => void export type OnWXResp = (resp: wxopensdk.BaseResp) => void 

```arkts
const kTag = "WXApiEventHandlerImpl" class WXApiEventHandlerImpl implements wxopensdk.WXApiEventHandler { private onReqCallbacks: Map<OnWXReq, OnWXReq> = new Map private onRespCallbacks: Map<OnWXResp, OnWXResp> = new Map registerOnWXReqCallback(on: OnWXReq) { this.onReqCallbacks.set(on, on) } unregisterOnWXReqCallback(on: OnWXReq) { this.onReqCallbacks.delete(on) } registerOnWXRespCallback(on: OnWXResp) { this.onRespCallbacks.set(on, on) } unregisterOnWXRespCallback(on: OnWXResp) { this.onRespCallbacks.delete(on) } onReq(req: wxopensdk.BaseReq): void { wxopensdk.Log.i(kTag, "wxonReq:%s", JSON.stringify(req)) this.onReqCallbacks.forEach((on) => { on(req) }) } onResp(resp: wxopensdk.BaseResp): void { //微信回调 wxopensdk.Log.i(kTag, "wxonResp:%s", JSON.stringify(resp)) this.onRespCallbacks.forEach((on) => { on(resp) }) } } export const WXEventHandler = new WXApiEventHandlerImpl 
```

### **云闪付 app 支付** 

##### canOpenLink 白名单配置 

在 module.json5 中的 querySchemes 下添加白名单,如下 module.json5 示例 

|**支付 APP scheme**|**对应支付 APP**|
|---|---|
|uppaysdk|云闪付APP|
|uppaywallet|云闪付APP|
|uppayvendor|华为Pay|

#### **使用示例** 

import { Pingpp } from '@pingplusplus/pingppsdk'; 

```arkts
Button('银联云闪付') .onClick(async () => { //传入调用 charge 或者 order 支付接口返回的 json 字符串 let data = '{"id":"ch_101240731413051801600003","object":"charge",....}' 
```

//附属参数 let extra: HashMap<string, Object> = new HashMap<string, Object>() //云闪付app 支付该参数必须填写 module.json5中 abilities[*].skills[*].uris.scheme 参数 //云闪付app 在支付成功或失败后会尝试使用 want 组件拉起商户 app extra.set('scheme', 'pingppsdkdemo') //云闪付支付同步返回的值为 void 需要在 want 中获取回调 await Pingpp.createPayment(data, extra) }) 

#### **module.json5 示例** 

{ "module": { "name": "entry", "type": "entry", "description": "$string:module_desc", "mainElement": "EntryAbility", "deviceTypes": [ "phone", "tablet", "2in1" ], "deliveryWithInstall": true, "installationFree": false, "pages": "$profile:main_pages", "querySchemes": [ "uppaysdk", "uppaywallet", "uppayvendor" ], "abilities": [ { "name": "EntryAbility", "srcEntry": "./ets/entryability/EntryAbility.ets", "description": "$string:EntryAbility_desc", "icon": "$media:layered_image", 

"label": "$string:EntryAbility_label", "startWindowIcon": "$media:ppp", "startWindowBackground": "$color:start_window_background", "exported": true, "skills": [ { "entities": [ "entity.system.home" ], "actions": [ "action.system.home" ], "uris": [ { "scheme": "pingppsdkdemo", } ] } ] } ], "extensionAbilities": [ { "name": "EntryBackupAbility", "srcEntry": "./ets/entrybackupability/EntryBackupAbility.ets", "type": "backup", "exported": false, "metadata": [ { "name": "ohos.extension.backup", "resource": "$profile:backup_config" } ], } ] } } 

#### **云闪付 app onNewWant 回调处理参考** 

- 在 EntryAbility.ets 文件中导入 

import { UpacpService, UPPayResult, UPPayResultStatus } from '@pingplusplus/pingppsdk'; 客户端回调参考 onNewWant 中处理 

```arkts
import { AbilityConstant, UIAbility, Want } from '@kit.AbilityKit'; import { hilog } from '@kit.PerformanceAnalysisKit'; import { window } from '@kit.ArkUI'; import { UpacpService, UPPayResult, UPPayResultStatus } from '@pingplusplus/pingppsdk'; export default class EntryAbility extends UIAbility { abilityWant: Want | undefined = undefined; uiContext: UIContext | undefined = undefined; 
onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void { 
hilog.info(0x0000, 'testTag', '%{public}s', 'Ability onCreate'); } onDestroy(): void { hilog.info(0x0000, 'testTag', '%{public}s', 'Ability onDestroy'); } onNewWant(want: Want, launchParam: AbilityConstant.LaunchParam): void { //接收并处理云闪付客户端回调 if (want?.uri && want.uri.includes('uppayresult') && this.uiContext) { hilog.info(0x0000, 'upacpWant', '%{public}s', '银联云闪付 app 支付回调'); console.log(want.uri) new UpacpService().handlePaymentResult(want.uri, (data: UPPayResult) => { switch (data.code) { case UPPayResultStatus.CANCEL: this.uiContext?.showAlertDialog({ title: '支付结果', message: '支付已取消!', alignment: DialogAlignment.Center }); break; case UPPayResultStatus.FAIL: this.uiContext?.showAlertDialog({ title: '支付结果', message: '支付失败!', alignment: DialogAlignment.Center }); break; case UPPayResultStatus.SUCCESS: this.uiContext?.showAlertDialog({ title: '支付结果', message: '支付成功!', alignment: DialogAlignment.Center }); break; default: this.uiContext?.showAlertDialog({ title: '支付结果', message: '取消!', alignment: DialogAlignment.Center }); break; } console.log('支付结果:' + JSON.stringify(data)); }); } } onWindowStageCreate(windowStage: window.WindowStage): void { // Main window is created, set main page for this ability hilog.info(0x0000, 'testTag', '%{public}s', 'Ability onWindowStageCreate'); windowStage.loadContent('pages/Index', (err) => { if (err.code) { hilog.error(0x0000, 'testTag', 'Failed to load the content. Cause: %{public}s', 
return; } let windowClass: window.Window; windowStage.getMainWindow((err, data) => { if (err.code) { console.error(`Failed to obtain the main window. Code is ${err.code}, message return; } windowClass = data; this.uiContext = windowClass.getUIContext(); }) hilog.info(0x0000, 'testTag', 'Succeeded in loading the content.'); }); } onWindowStageDestroy(): void { // Main window is destroyed, release UI related resources hilog.info(0x0000, 'testTag', '%{public}s', 'Ability onWindowStageDestroy'); } onForeground(): void { // Ability has brought to foreground hilog.info(0x0000, 'testTag', '%{public}s', 'Ability onForeground'); } onBackground(): void { // Ability has back to background hilog.info(0x0000, 'testTag', '%{public}s', 'Ability onBackground'); } } 
```

## **开源协议** 

本项目基于 Apache License 2.0
