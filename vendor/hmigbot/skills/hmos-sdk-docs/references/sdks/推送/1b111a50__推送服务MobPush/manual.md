# **Push-OHOS** 

# **SDK-集成** 

## **一** **.添加SDK依赖** 

#### 在 **Terminal** 窗口中,执行如下命令进行安装 

ohpm install @zztsdk/zztcore 

ohpm install @zztsdk/mobpush 

## **二.权限** 

ohos.permission.INTERNET 

### **建议权限** 

ohos.permission.APP_TRACKING_CONSENT // 用于产生设备ID ohos.permission.GET_NETWORK_INFO // 用于判断网络类型,进行连接与数据传输优化 

## **三.导入模块** 

import { ZztSDK } from '@zztsdk/zztcore'; 

import mobPush from '@zztsdk/mobpush'; 

## **四.华为推送服务配置** 

在项目模块级别下的 **src/main/module.json5** (例如entry/src/main/module.json5)中,新增metadata并配置 client_id 

#### 1.client_id申请教程: 

https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/push-preparations-000000172788525 0#section792641732919 

示例配置: 

"module": { "name": "entry", "type": "xxx", "description": "xxxx", "mainElement": "xxxx", 

"deviceTypes": [], "pages": "xxxx", 

"abilities": [], // 配置如下信息 "metadata": [ { "name": "client_id", // 配置为您的Client ID "value": "xxxxxx" } ] } 

#### 2.配置接收后台消息(透传消息) 

在项目工程的 **src/main/module.json5** 文件的abilities模块中配置 **skills** 中 **actions** 内容为 **action.ohos.push.listener** (有且只能有一个ability定义该action, **若同时添加uris参数,则uris内容需为空。** 在对应Ability中调用mobPush.receiveMessage(ability)方法 

#### 示例配置 

"abilities": [ { "name": "PushMessageAbility", "srcEntry": "./ets/abilities/PushMessageAbility.ets", "launchType": "singleton", "startWindowIcon": "$media:icon", "startWindowBackground": "$color:start_window_background", "exported": false, "skills": [ { "actions": [ "action.ohos.push.listener" ] } ] } ] 

# **SDK-API** 

## **约束** 

本模块首批接口从 OpenHarmony SDK API version 12 开始支持。 

## **ZztSDK初始化** 

#### **注意:请确保传入context非空** 

init()接口内部会做隐私授权状态的判断,在应用向ZztSDK提交隐私授权同意状态之前不会做任何业务的初始化,可 放心调用 

" " ZztSDK.init(context, 您的AppKey", 您的AppSecret") 

## **ZztSDK隐私提交** 

#### **注意:请确保在调用初始化方法后调用该方法** 

应用在向终端用户展示“隐私声明”弹框,并获取终端用户的隐私授权结果后,需将隐私授权结果回传给ZztSDK。 

//仅当授权结果为“true”时,ZztSDK各项功能才可正常使用。 ZztSDK.submitPolicyGrantResult(granted) 

## **MobPush初始化** 

#### **注意:请确保在调用ZztSDK初始化和隐私提交方法之后调用该方法** 

export function init(context: Context, appKey?: string, appSecret?: string): void //示例代码: " " mobPush.init(getContext(), 您的AppKey", 您的AppSecret") 

#### **MobPush初始化示例代码** : 

//ZztSDK初始化 " " ZztSDK.init(context, 您的AppKey", 您的AppSecret") //ZztSDK隐私提交 ZztSDK.submitPolicyGrantResult(true) //MobPush初始化 " " mobPush.init(getContext(), 您的AppKey", 您的AppSecret") 

## **获取RID** 

#### 获取缓存的注册id(可与用户id绑定,实现向指定用户推送消息) 

export function getRegistrationId(callback: AsyncCallback<string>): void 

export function getRegistrationId(): Promise<string> 

//示例代码: import { BusinessError } from '@ohos.base'; let getRegistrationIdCallback = (err: BusinessError, data: string): void => { let message = "RID:" + data; console.log(message) } mobPush.getRegistrationId(getRegistrationIdCallback) 

mobPush.getRegistrationId().then((data: string) => { 

console.log(`RID: ${data}`) 

}) 

## **设置推送监听** 

#### 建议在AbilityStage中设置 

export function addPushReceiver(receiver: MobPushReceiver) 

##### //示例代码: 

let receive: mobPush.MobPushReceiver = { 

onCustomMessageReceive: (message: mobPush.MobPushCustomMessage) => { //接收到自定义消息(透传消息) 

let messageId = message.messageId;//获取任务ID let content = message.content//获取推送内容 ... }, 

onNotifyMessageReceive: (message: mobPush.MobPushNotifyMessage) => { //通知消息到达 

let mobNotifyId = message.mobNotifyId//获取消息ID 

let messageId = message.messageId//获取任务ID let title = message.title//获取推送标题 let content = message.content//获取推送内容 ... }, 

onNotifyMessageOpenedReceive: (message: mobPush.MobPushNotifyMessage) => { //通知被点击事件 

//需在通知打开的ability中调用mobPush.notificationClickAck() let mobNotifyId = message.mobNotifyId//获取消息ID let messageId = message.messageId//获取任务ID let title = message.title//获取推送标题 let content = message.content//获取推送内容 ... }, //type=1:RID更新  type=2:厂商deviceToken更新 onCommandReceive: (type: number, map: HashMap<string, Object>) => { //channel:mobpush/harmony 

let channel = map.get(mobPush.KEY_CHANNEL) //对应channel的更新token let token = map.get(mobPush.KEY_TOKEN) } } mobPush.addPushReceiver(receive) 

## **通知点击回执上报** 

为了能接收到通知点击后回调的对应数据在通知跳转页面UIAbility的onCreate、onNewWant中调用传入want 

会通过上面设置的回调接口MobPushReceiver类中的onNotifyMessageOpenedReceive方法回调 

export function notificationClickAck(want: Want): void 

//示例代码 export default class EntryAbility extends UIAbility { onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void { hilog.info(0x0000, 'testTag', '%{public}s', 'Ability onCreate'); console.log("EntryAbility onCreate") mobPush.notificationClickAck(want) if (want) { if (want.parameters) { //获取推送设置的额外内容 if (want.parameters["pushData"]) { console.log("pushData:" + JSON.stringify((want.parameters["pushData"]))) } } } } onWindowStageCreate(windowStage: window.WindowStage): void { // Main window is created, set main page for this ability hilog.info(0x0000, 'testTag', '%{public}s', 'Ability onWindowStageCreate'); 

windowStage.loadContent('pages/Index', (err, data) => { if (err.code) { hilog.error(0x0000, 'testTag', 'Failed to load the content. Cause: %{public}s', '' JSON.stringify(err) ?? ); return; } hilog.info(0x0000, 'testTag', 'Succeeded in loading the content. Data: %{public}s', '' JSON.stringify(data) ?? ); }); } 

```arkts
onNewWant(want: Want, launchParam: AbilityConstant.LaunchParam): void { console.log("EntryAbility onNewWant") mobPush.notificationClickAck(want) if (want) { if (want.parameters) { //获取推送设置的额外内容 if (want.parameters["pushData"]) { console.log("pushData:" + JSON.stringify((want.parameters["pushData"]))) } } } } } 
```

## **移除推送监听** 

export function removePushReceiver(receiver: MobPushReceiver) 

//示例代码: mobPush.removePushReceiver(receive) 

## **停止推送** 

#### 停止后将不会收到推送消息,仅可通过restartPush重新打开 

export function stopPush() 

//示例代码: mobPush.stopPush() 

## **重新打开推送服务** 

export function restartPush() 

//示例代码: mobPush.restartPush() 

## **判断推送服务是否已经停止** 

//此方法已废弃 请使用isPushStoppedAsync方法 export function isPushStopped(): boolean 

export function isPushStoppedAsync(): Promise<boolean> 

export function isPushStoppedAsync(callback: AsyncCallback<boolean>): void 

##### //示例代码: 

let callback = (err: Base.BusinessError, isStopped: boolean): void => { this.showMessage("isStopped:" + isStopped) } 

mobPush.isPushStoppedAsync(callback) 

mobPush.isPushStoppedAsync().then((isStopped) => { this.showMessage("isStopped:" + isStopped) }) 

## **设置别名** 

#### errorCode为操作结果(0 成功,其他失败) 

export function setAlias(alias: string, callback: AsyncCallback<AliasResult>): void 

export function setAlias(alias: string): Promise<AliasResult> 

//示例代码 import { BusinessError } from '@ohos.base'; let setAliasCallback = (err: BusinessError, data: mobPush.AliasResult): void => { console.log("setAlias:" + JSON.stringify(data)) console.log("alias:" + data.alias) console.log("errCode:" + data.errorCode) } mobPush.setAlias("alias", setAliasCallback) mobPush.setAlias("alias").then((data: mobPush.AliasResult) => { console.log("setAlias:" + JSON.stringify(data)) console.log("alias:" + data.alias) console.log("errCode:" + data.errorCode) }) 

## **获取别名** 

errorCode为操作结果(0 成功,其他失败) 

export function getAlias(callback: AsyncCallback<AliasResult>): void 

export function getAlias(): Promise<AliasResult> 

//示例代码 import { BusinessError } from '@ohos.base'; let getAliasCallback = (err: BusinessError, data: mobPush.AliasResult): void => { console.log("getAlias:" + JSON.stringify(data)) console.log("alias:" + data.alias) console.log("errCode:" + data.errorCode) } mobPush.getAlias(getAliasCallback) 

mobPush.getAlias().then((data: mobPush.AliasResult) => { console.log("getAlias:" + JSON.stringify(data)) console.log("alias:" + data.alias) console.log("errCode:" + data.errorCode) }) 

## **删除别名** 

errorCode为操作结果(0 成功,其他失败) 

export function deleteAlias(callback: AsyncCallback<AliasResult>): void 

export function deleteAlias(): Promise<AliasResult> 

//示例代码 

```arkts
import { BusinessError } from '@ohos.base'; 
```

let getAliasCallback = (err: BusinessError, data: mobPush.AliasResult): void => { console.log("deleteAlias:" + JSON.stringify(data)) console.log("alias:" + data.alias) console.log("errCode:" + data.errorCode) } mobPush.deleteAlias(getAliasCallback) 

mobPush.deleteAlias().then((data: mobPush.AliasResult) => { console.log("deleteAlias:" + JSON.stringify(data)) console.log("alias:" + data.alias) console.log("errCode:" + data.errorCode) }) 

## **添加标签** 

errorCode为操作结果(0 成功,其他失败) 

export function addTags(tags: string[], callback: AsyncCallback<TagsResult>): void 

export function addTags(tags: string[]): Promise<TagsResult> 

##### //示例代码 

```arkts
import { BusinessError } from '@ohos.base'; let addTagsCallback = (err: BusinessError, data: mobPush.TagsResult): void => { console.log("addTags:" + JSON.stringify(data)) console.log("tags:" + data.tags) console.log("errCode:" + data.errorCode) } mobPush.addTags(["tag"] , addTagsCallback) mobPush.addTags(["tag"]).then((data: mobPush.TagsResult) => { console.log("addTags:" + JSON.stringify(data)) console.log("tags:" + data.tags) console.log("errCode:" + data.errorCode) }) 
```

## **获取标签** 

errorCode为操作结果(0 成功,其他失败) 

export function getTags(callback: AsyncCallback<TagsResult>): void 

export function getTags(): Promise<TagsResult> 

##### //示例代码 

```arkts
import { BusinessError } from '@ohos.base'; 
let getTagsCallback = (err: BusinessError, data: mobPush.TagsResult): void => { console.log("addTags:" + JSON.stringify(data)) console.log("tags:" + data.tags) console.log("errCode:" + data.errorCode) } mobPush.getTags(getTagsCallback) mobPush.getTags().then((data: mobPush.TagsResult) => { console.log("getTags:" + JSON.stringify(data)) console.log("tags:" + data.tags) console.log("errCode:" + data.errorCode) }) 
```

## **删除标签** 

errorCode为操作结果(0 成功,其他失败) 

export function deleteTags(tags: string[], callback: AsyncCallback<TagsResult>): void export function deleteTags(tags: string[]): Promise<TagsResult> 

##### //示例代码 

```arkts
import { BusinessError } from '@ohos.base'; let deleteTagsCallback = (err: BusinessError, data: mobPush.TagsResult): void => { console.log("deleteTags:" + JSON.stringify(data)) console.log("tags:" + data.tags) console.log("errCode:" + data.errorCode) } mobPush.deleteTags(["tag"] , deleteTagsCallback) 
```

mobPush.deleteTags(["tag"]).then((data: mobPush.TagsResult) => { console.log("deleteTags:" + JSON.stringify(data)) console.log("tags:" + data.tags) console.log("errCode:" + data.errorCode) }) 

## **清空所有标签** 

errorCode为操作结果(0 成功,其他失败) 

export function cleanTags(callback: AsyncCallback<TagsResult>): void 

export function cleanTags(): Promise<TagsResult> 

##### //示例代码 

```arkts
import { BusinessError } from '@ohos.base'; 
```

let cleanTagsCallback = (err: BusinessError, data: mobPush.TagsResult): void => { console.log("cleanTags:" + JSON.stringify(data)) 

console.log("tags:" + data.tags) console.log("errCode:" + data.errorCode) 

} mobPush.cleanTags(cleanTagsCallback) 

mobPush.cleanTags().then((data: mobPush.TagsResult) => { console.log("cleanTags:" + JSON.stringify(data)) console.log("tags:" + data.tags) console.log("errCode:" + data.errorCode) }) 

## **设置是否显示⻆标** 

#### 用于接收通知时显示⻆标数量 

export function setShowBadge(show: boolean) 

//示例代码 //设置显示⻆标 mobPush.setShowBadge(true) //设置不显示⻆标 mobPush.setShowBadge(false) 

## **获取是否显示⻆标** 

//此方法已废弃 请使用getShowBadgeAsync方法 export function getShowBadge() 

export function getShowBadgeAsync(): Promise<boolean> 

export function getShowBadgeAsync(callback: AsyncCallback<boolean>): void 

##### //示例代码 

let callback = (err: Base.BusinessError, isShow: boolean) => { this.showMessage("⻆标显示状态:" + isShow) } mobPush.getShowBadgeAsync(callback) 

mobPush.getShowBadgeAsync().then((isShow) => { this.showMessage("⻆标显示状态:" + isShow) }) 

## **设置⻆标数** 

设置显示的⻆标数 

export function setBadgeCounts(count: number) 

//示例代码 mobPush.setBadgeCounts(99) 

## **清除所有通知** 

export function clearAllNotification() 

//示例代码 mobPush.clearAllNotification() 

## **获取厂商token** 

//此方法已废弃 请使用getDeviceTokenAsync方法 export function getDeviceToken(): string 

export function getDeviceTokenAsync(): Promise<string> 

export function getDeviceTokenAsync(callback: AsyncCallback<string>): void 

//示例代码 

let callback = (err: Base.BusinessError, token: string) => { this.showMessage("厂商Token:" + token) } mobPush.getDeviceTokenAsync(callback) 

mobPush.getDeviceTokenAsync().then((token) => { this.showMessage("厂商Token:" + token) }) 

## **判断是否开启通知权限** 

export function isNotificationEnabled(callback: AsyncCallback<boolean>): void 

export function isNotificationEnabled(): Promise<boolean> 

//示例代码 

```arkts
import { BusinessError } from '@ohos.base'; 
let isNotificationEnabledCallback = (err: BusinessError, data: boolean): void => { let message = "" if (err) { message = `获取通知权限是否开启失败, code is ${err.code}, message is ${err.message}`; } else { message = `通知权限是否开启: ${JSON.stringify(data)}`; } console.log(message) 
```

} 

mobPush.isNotificationEnabled(isNotificationEnabledCallback) 

mobPush.isNotificationEnabled().then((data: boolean) => { ` console.log( 通知权限是否开启: ${data}`) }) 

## **检测推送tcp连接状态** 

export function checkTcpStatus(callback: Callback<boolean>): void 

export function checkTcpStatus(): Promise<boolean> 

##### //示例代码 

```arkts
let tcpStatusCallback = (data: boolean): void => { let message = `TCP状态: ${JSON.stringify(data)}`; console.log(message) } 
```

mobPush.checkTcpStatus(tcpStatusCallback) 

mobPush.checkTcpStatus().then((data: boolean) => { console.log(`TCP状态: ${data}`) }) 

## **接收厂商透传消息** 

#### 需在接收厂商透传消息的UIAbility中调用 

//pushType可指定类型,默认为'BACKGROUND' 

export function receiveMessage(ability: UIAbility, pushType?: 'IM' | 'VoIP' | 'BACKGROUND' | 'EMERGENCY') 

##### //示例代码 

onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void { 

mobPush.notificationClickAck(want) 

mobPush.receiveMessage(this) 

} 

## **设置地理围栏功能状态开关** 

export function setGeofenceStatus(isOpen: boolean) 

//示例代码 

//打开地理围栏功能 

mobPush.setGeofenceStatus(true) //关闭地理围栏功能 mobPush.setGeofenceStatus(false) 

## **获取地理围栏功能状态开关** 

export function getGeofenceStatus(callback: Callback<boolean>): void 

export function getGeofenceStatus(): Promise<boolean> 

##### //示例代码 

mobPush.getGeofenceStatus((isopen) => { console.log("GeofenceStatus:" + isopen) }) 

mobPush.getGeofenceStatus().then((isopen) => { this.showMessage("GeofenceStatus:" + isopen) }) 

## **删除地理围栏** 

export function deleteGeofence(geofenceId: string) 

//示例代码 "" mobPush.deleteGeofence( ) 

## **设置触发围栏回调** 

export function setGeofenceReceiver(receiver: MobPushGeofenceReceiver) 

//示例代码 

```arkts
let gfReceive: mobPush.MobPushGeofenceReceiver = { onGeofenceReceiver: (data: mobPush.MobPushGeofence[]): void => { let msg = "触发地理围栏:" + JSON.stringify(data) console.log(msg) } } mobPush.setGeofenceReceiver(gfReceive)
```
