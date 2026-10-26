# **MobPush接口文档** 

## **ZztSDK.init** 

init(context: Context, appkey: string, secret: string):void 

#### 初始化sdk 

### **参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|context|Context|是|上下文context|
|appkey|string|是|sdk的appkey|
|secret|string|是|sdk的secret|

### **返回值:** 

|**类型**|**说明**|
|---|---|
|void|无|

### **示例:** 

ZztSDK.init(getContext(this), 'your appkey', 'your secret') 

## **ZztSDK.submitPolicyGrantResult** 

submitPolicyGrantResult(granted: boolean): void 

#### 提交隐私结果 

### **参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|context|Context|是|上下文context|

### **返回值:** 

|**类型**|**说明**|
|---|---|
|void|无|

### **示例:** 

ZztSDK.submitPolicyGrantResult(true) 

## **mobPush.init** 

export function init(context: Context, appKey?: string, appSecret?: string): void 

#### MobPush初始化 

#### **注意:请确保在调用ZztSDK初始化和隐私提交方法之后调用该方法** 

### **参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|context|Context|是|上下文context|
|appkey|string|否|sdk的appkey|
|secret|string|否|sdk的secret|

### **返回值:** 

|**类型**|**说明**|
|---|---|
|void|无|

### **示例:** 

" " mobPush.init(getContext(), 您的AppKey", 您的AppSecret") 

## **getRegistrationId** 

getRegistrationId(callback: AsyncCallback): void 

getRegistrationId(): Promise 

获取缓存的注册id(可与用户id绑定,实现向指定用户推送消息) 

### **参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|callback|AsyncCallback|否|返回RID的回调|

### **返回值:** 

|**类型**|**说明**|
|---|---|
|void|使用参数AsyncCallback方法 返回值为void|
|Promise|使用无参数方法返回为Promise,其中string值为rid|

### **示例:** 

```arkts
import { BusinessError } from '@ohos.base'; //AsyncCallback let getRegistrationIdCallback = (err: BusinessError, data: string): void => { let message = "RID:" + data; console.log(message) } mobPush.getRegistrationId(getRegistrationIdCallback) 
```

//Promise mobPush.getRegistrationId().then((data: string) => { console.log(`RID: ${data}`) }) 

## **addPushReceiver** 

addPushReceiver(receiver: MobPushReceiver):void 

设置推送监听(建议在AbilityStage中设置) 

### **参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|receiver|MobPushReceiver|是|推送相关监听回调|
|**类型返回值:**||**说明**||
|void||无||

### **示例:** 

let receive: mobPush.MobPushReceiver = { 

onCustomMessageReceive: (message: mobPush.MobPushCustomMessage) => { //接收到自定义消息(透传消息) 

```arkts
let messageId = message.messageId;//获取任务ID let content = message.content//获取推送内容 ... }, onNotifyMessageReceive: (message: mobPush.MobPushNotifyMessage) => { 
```

//通知消息到达 let mobNotifyId = message.mobNotifyId//获取消息ID let messageId = message.messageId//获取任务ID let title = message.title//获取推送标题 let content = message.content//获取推送内容 ... }, onNotifyMessageOpenedReceive: (message: mobPush.MobPushNotifyMessage) => { //通知被点击事件 //需在通知打开的ability中调用mobPush.notificationClickAck() let mobNotifyId = message.mobNotifyId//获取消息ID let messageId = message.messageId//获取任务ID let title = message.title//获取推送标题 let content = message.content//获取推送内容 ... }, //type=1:RID更新  type=2:厂商deviceToken更新 onCommandReceive: (type: number, map: HashMap<string, Object>) => { //channel:mobpush/harmony let channel = map.get(mobPush.KEY_CHANNEL) //对应channel的更新token let token = map.get(mobPush.KEY_TOKEN) } } mobPush.addPushReceiver(receive) 

## **notificationClickAck** 

notificationClickAck(want: Want): void 

通知点击回执上报 

为了能接收到通知点击后回调的对应数据 **在通知跳转页面UIAbility的onCreate、onNewWant中调用传入want** 会通过上面设置的回调接口MobPushReceiver类中的onNotifyMessageOpenedReceive方法回调 

### **参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|want|Want|是|通知跳转页面UIAbility的want|

### **返回值:** 

|**类型**|**说明**|
|---|---|
|void|无|

### **示例:** 

```arkts
export default class EntryAbility extends UIAbility { onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void { hilog.info(0x0000, 'testTag', '%{public}s', 'Ability onCreate'); console.log("EntryAbility onCreate") mobPush.notificationClickAck(want) if (want) { if (want.parameters) { //获取推送设置的额外内容 if (want.parameters["pushData"]) { console.log("pushData:" + JSON.stringify((want.parameters["pushData"]))) } } } } onWindowStageCreate(windowStage: window.WindowStage): void { // Main window is created, set main page for this ability hilog.info(0x0000, 'testTag', '%{public}s', 'Ability onWindowStageCreate'); 
windowStage.loadContent('pages/Index', (err, data) => { if (err.code) { hilog.error(0x0000, 'testTag', 'Failed to load the content. Cause: %{public}s', '' JSON.stringify(err) ?? ); return; } hilog.info(0x0000, 'testTag', 'Succeeded in loading the content. Data: %{public}s', '' JSON.stringify(data) ?? ); }); } 
onNewWant(want: Want, launchParam: AbilityConstant.LaunchParam): void { console.log("EntryAbility onNewWant") mobPush.notificationClickAck(want) if (want) { if (want.parameters) { //获取推送设置的额外内容 if (want.parameters["pushData"]) { console.log("pushData:" + JSON.stringify((want.parameters["pushData"]))) } } } } } 
```

## **removePushReceiver** 

removePushReceiver(receiver: MobPushReceiver):void 

移除设置的推送监听 

**参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|receiver|MobPushReceiver|是|推送相关监听回调类|

### **返回值:** 

|**类型**|**说明**|
|---|---|
|void|无|

### **示例:** 

mobPush.removePushReceiver(receive) 

## **stopPush** 

stopPush():void 

#### 停止推送 

停止后将不会收到推送消息,仅可通过restartPush重新打开 

### **参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|无|无|否|无|

### **返回值:** 

|**类型**|**说明**|
|---|---|
|void|无|

### **示例:** 

mobPush.stopPush() 

## **restartPush** 

restartPush():void 

重新打开推送服务 

### **参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|无|无|否|无|

### **返回值:** 

|**类型**|**说明**|
|---|---|
|void|无|

### **示例:** 

mobPush.restartPush() 

## **isPushStoppedAsync** 

isPushStoppedAsync(): Promise 

isPushStoppedAsync(callback: AsyncCallback): void 

判断推送服务是否已经停止 

### **参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|callback|AsyncCallback|否|返回是否关闭推送的结果的回调|

### **返回值:** 

|**类型**|**说明**|
|---|---|
|void|使用参数AsyncCallback方法 返回值为void|
|Promise|使用无参数方法返回为Promise,其中boolean值为是否关闭推送的结果|

### **示例:** 

//AsyncCallback 

let callback = (err: Base.BusinessError, isStopped: boolean): void => { 

this.showMessage("isStopped:" + isStopped) } 

mobPush.isPushStoppedAsync(callback) //Promise 

mobPush.isPushStoppedAsync().then((isStopped) => { this.showMessage("isStopped:" + isStopped) }) 

## **setAlias** 

setAlias(alias: string, callback: AsyncCallback): void 

setAlias(alias: string): Promise 

设置别名 

### **参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|alias|string|是|需要设置的别名|
|callback|AsyncCallback|否|返回设置别名结果的回调|

### **返回值:** 

|**类型**|**说明**|
|---|---|
|void|使用参数AsyncCallback方法 返回值为void|
|Promise|使用无参数方法返回为Promise,其中AliasResult值为设置别名的结果|

### **示例:** 

```arkts
import { BusinessError } from '@ohos.base'; //AsyncCallback 
```

let setAliasCallback = (err: BusinessError, data: mobPush.AliasResult): void => { console.log("setAlias:" + JSON.stringify(data)) console.log("alias:" + data.alias) console.log("errCode:" + data.errorCode) } mobPush.setAlias("alias", setAliasCallback) //Promise 

mobPush.setAlias("alias").then((data: mobPush.AliasResult) => { console.log("setAlias:" + JSON.stringify(data)) console.log("alias:" + data.alias) console.log("errCode:" + data.errorCode) }) 

## **getAlias** 

getAlias(callback: AsyncCallback): void 

getAlias(): Promise 

获取别名 

**参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|callback|AsyncCallback|否|返回获取别名结果的回调|

### **返回值:** 

|**类型**|**说明**|
|---|---|
|void|使用参数AsyncCallback方法 返回值为void|
|Promise|使用无参数方法返回为Promise,其中AliasResult值为获取别名的结果|

### **示例:** 

```arkts
import { BusinessError } from '@ohos.base'; 
```

let getAliasCallback = (err: BusinessError, data: mobPush.AliasResult): void => { console.log("getAlias:" + JSON.stringify(data)) console.log("alias:" + data.alias) console.log("errCode:" + data.errorCode) } mobPush.getAlias(getAliasCallback) 

mobPush.getAlias().then((data: mobPush.AliasResult) => { console.log("getAlias:" + JSON.stringify(data)) console.log("alias:" + data.alias) console.log("errCode:" + data.errorCode) }) 

## **deleteAlias** 

deleteAlias(callback: AsyncCallback): void 

deleteAlias(): Promise 

删除别名 

### **参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|callback|AsyncCallback|否|返回删除别名结果的回调|

### **返回值:** 

|**类型**|**说明**|
|---|---|
|void|使用参数AsyncCallback方法 返回值为void|
|Promise|使用无参数方法返回为Promise,其中AliasResult值为删除别名的结果|

### **示例:** 

```arkts
import { BusinessError } from '@ohos.base'; let getAliasCallback = (err: BusinessError, data: mobPush.AliasResult): void => { console.log("deleteAlias:" + JSON.stringify(data)) console.log("alias:" + data.alias) console.log("errCode:" + data.errorCode) } mobPush.deleteAlias(getAliasCallback) mobPush.deleteAlias().then((data: mobPush.AliasResult) => { console.log("deleteAlias:" + JSON.stringify(data)) console.log("alias:" + data.alias) console.log("errCode:" + data.errorCode) }) 
```

## **addTags** 

addTags(tags: string[], callback: AsyncCallback): void 

addTags(tags: string[]): Promise 

添加标签 

### **参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|tags|string[]|是||
|callback|AsyncCallback|否|返回添加标签结果的回调|

### **返回值:** 

|**类型**|**说明**|
|---|---|
|void|使用参数AsyncCallback方法 返回值为void|
|Promise|使用无参数方法返回为Promise,其中TagsResult值为添加标签的结果|

### **示例:** 

```arkts
import { BusinessError } from '@ohos.base'; 
```

let addTagsCallback = (err: BusinessError, data: mobPush.TagsResult): void => { console.log("addTags:" + JSON.stringify(data)) console.log("tags:" + data.tags) console.log("errCode:" + data.errorCode) } 

mobPush.addTags(["tag"] , addTagsCallback) 

mobPush.addTags(["tag"]).then((data: mobPush.TagsResult) => { console.log("addTags:" + JSON.stringify(data)) console.log("tags:" + data.tags) console.log("errCode:" + data.errorCode) }) 

## **getTags** 

getTags(callback: AsyncCallback): void 

getTags(): Promise 

获取标签 

### **参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|callback|AsyncCallback|否|返回获取标签结果的回调|

### **返回值:** 

|**类型**|**说明**|
|---|---|
|void|使用参数AsyncCallback方法 返回值为void|
|Promise|使用无参数方法返回为Promise,其中TagsResult值为获取标签的结果|

### **示例:** 

```arkts
import { BusinessError } from '@ohos.base'; 
```

let getTagsCallback = (err: BusinessError, data: mobPush.TagsResult): void => { console.log("getTags:" + JSON.stringify(data)) console.log("tags:" + data.tags) console.log("errCode:" + data.errorCode) } 

mobPush.getTags(getTagsCallback) 

mobPush.getTags().then((data: mobPush.TagsResult) => { console.log("getTags:" + JSON.stringify(data)) console.log("tags:" + data.tags) console.log("errCode:" + data.errorCode) }) 

## **deleteTags** 

deleteTags(tags: string[], callback: AsyncCallback): void 

#### deleteTags(tags: string[]): Promise 

#### 删除标签 

### **参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|tags|string[]|是|需要删除的标签|
|callback|AsyncCallback|否|返回删除标签结果的回调|

### **返回值:** 

|**类型**|**说明**|
|---|---|
|void|使用参数AsyncCallback方法 返回值为void|
|Promise|使用无参数方法返回为Promise,其中TagsResult值为删除标签的结果|

### **示例:** 

```arkts
import { BusinessError } from '@ohos.base'; 
```

let deleteTagsCallback = (err: BusinessError, data: mobPush.TagsResult): void => { console.log("deleteTags:" + JSON.stringify(data)) console.log("tags:" + data.tags) console.log("errCode:" + data.errorCode) } mobPush.deleteTags(["tag"] , deleteTagsCallback) 

mobPush.deleteTags(["tag"]).then((data: mobPush.TagsResult) => { console.log("deleteTags:" + JSON.stringify(data)) console.log("tags:" + data.tags) console.log("errCode:" + data.errorCode) }) 

## **cleanTags** 

cleanTags(callback: AsyncCallback): void 

cleanTags(): Promise 

清空所有标签 

### **参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|callback|AsyncCallback|否|返回清空标签结果的回调|

### **返回值:** 

|**类型**|**说明**|
|---|---|
|void|使用参数AsyncCallback方法 返回值为void|
|Promise|使用无参数方法返回为Promise,其中TagsResult值为清空标签的结果|

### **示例:** 

```arkts
import { BusinessError } from '@ohos.base'; 
```

let cleanTagsCallback = (err: BusinessError, data: mobPush.TagsResult): void => { console.log("cleanTags:" + JSON.stringify(data)) console.log("tags:" + data.tags) console.log("errCode:" + data.errorCode) } mobPush.cleanTags(cleanTagsCallback) 

mobPush.cleanTags().then((data: mobPush.TagsResult) => { console.log("cleanTags:" + JSON.stringify(data)) console.log("tags:" + data.tags) console.log("errCode:" + data.errorCode) }) 

## **setShowBadge** 

setShowBadge(show: boolean) 

用于设置接收通知时是否显示⻆标 

### **参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|show|boolean|是|true:开启⻆标false:关闭⻆标|

### **返回值:** 

|**类型**|**说明**|
|---|---|
|无|无|

### **示例:** 

//设置显示⻆标 mobPush.setShowBadge(true) //设置不显示⻆标 mobPush.setShowBadge(false) 

## **getShowBadgeAsync** 

getShowBadgeAsync(): Promise 

getShowBadgeAsync(callback: AsyncCallback): void 

获取是否显示⻆标 

### **参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|callback|AsyncCallback|否|返回是否显示⻆标结果的回调|

### **返回值:** 

|**类型**|**说明**|
|---|---|
|void|使用参数AsyncCallback方法 返回值为void|
|Promise|使用无参数方法返回为Promise,其中boolean值为是否显示⻆标的结果|

### **示例:** 

//AsyncCallback let callback = (err: Base.BusinessError, isShow: boolean) => { this.showMessage("⻆标显示状态:" + isShow) } mobPush.getShowBadgeAsync(callback) //Promise mobPush.getShowBadgeAsync().then((isShow) => { this.showMessage("⻆标显示状态:" + isShow) }) 

## **setBadgeCounts** 

setBadgeCounts(count: number) 

设置⻆标数 

### **参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|count|number|是|⻆标数|

### **返回值:** 

|**类型**|**说明**|
|---|---|
|无|无|

### **示例:** 

mobPush.setBadgeCounts(99) 

## **clearAllNotification** 

clearAllNotification() 

清除所有通知 

### **参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|无|无|否|无|

### **返回值:** 

|**类型**|**说明**|
|---|---|
|无|无|

### **示例:** 

mobPush.clearAllNotification() 

## **getDeviceTokenAsync** 

getDeviceTokenAsync(): Promise 

getDeviceTokenAsync(callback: AsyncCallback): void 

获取厂商token 

### **参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|callback|AsyncCallback|否|返回获取厂商token结果的回调|

### **返回值:** 

|**类型**|**说明**|
|---|---|
|void|使用参数AsyncCallback方法 返回值为void|
|Promise|使用无参数方法返回为Promise,其中string值为获取厂商token的结果|

### **示例:** 

//AsyncCallback 

let callback = (err: Base.BusinessError, token: string) => { this.showMessage("厂商Token:" + token) } mobPush.getDeviceTokenAsync(callback) //Promise 

mobPush.getDeviceTokenAsync().then((token) => { this.showMessage("厂商Token:" + token) }) 

## **isNotificationEnabled** 

isNotificationEnabled(callback: AsyncCallback): void 

isNotificationEnabled(): Promise 

判断是否开启通知权限 

### **参数:** 

|**参数名**|**类型必填**|**说明**|
|---|---|---|
|callback|AsyncCallback 否|返回是否开启通知权限结果的回调|
|**类型返回值:**|**说明**||
|void Promise|使用参数AsyncCallback方法 返回值为 使用无参数方法返回为Promise,其中bo|void olean值为是否开启通知权限的结果|

### **示例:** 

```arkts
import { BusinessError } from '@ohos.base'; 
```

//AsyncCallback let isNotificationEnabledCallback = (err: BusinessError, data: boolean): void => { let message = "" if (err) { message = `获取通知权限是否开启失败, code is ${err.code}, message is ${err.message}`; } else { message = `通知权限是否开启: ${JSON.stringify(data)}`; } console.log(message) } mobPush.isNotificationEnabled(isNotificationEnabledCallback) //Promise mobPush.isNotificationEnabled().then((data: boolean) => { ` console.log( 通知权限是否开启: ${data}`) }) 

## **checkTcpStatus** 

checkTcpStatus(callback: Callback): void 

checkTcpStatus(): Promise 

检测推送tcp连接状态 

### **参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|callback|Callback|否|返回推送tcp连接状态的回调|

### **返回值:** 

|**类型**|**说明**|
|---|---|
|void|使用参数Callback方法 返回值为void|
|Promise|使用无参数方法返回为Promise,其中boolean值为推送tcp连接状态的结果|

### **示例:** 

//AsyncCallback let tcpStatusCallback = (data: boolean): void => { let message = `TCP状态: ${JSON.stringify(data)}`; console.log(message) } mobPush.checkTcpStatus(tcpStatusCallback) //Promise mobPush.checkTcpStatus().then((data: boolean) => { console.log(`TCP状态: ${data}`) }) 

## **receiveMessage** 

receiveMessage(ability: UIAbility, pushType?: 'IM' | 'VoIP' | 'BACKGROUND' | 'EMERGENCY') 

接收厂商透传消息 

### **参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|ability|UIAbility|是|返回推送tcp连接状态的回调|
|pushType|'IM' | 'VoIP'|'BACKGROUND'| 'EMERGENCY'|否|消息类型,默认BACKGROUND|

### **返回值:** 

|**类型**|**说明**|
|---|---|
|无|无|

### **示例:** 

onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void { 

mobPush.notificationClickAck(want) 

mobPush.receiveMessage(this) 

} 

## **setGeofenceStatus** 

setGeofenceStatus(isOpen: boolean) 

设置地理围栏功能状态开关 

### **参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|isOpen|boolean|是|true:开启地理围栏false:关闭地理围栏|

### **返回值:** 

|**类型**|**说明**|
|---|---|
|无|无|

### **示例:** 

//打开地理围栏功能 mobPush.setGeofenceStatus(true) //关闭地理围栏功能 mobPush.setGeofenceStatus(false) 

## **getGeofenceStatus** 

getGeofenceStatus(callback: Callback): void 

getGeofenceStatus(): Promise 

获取地理围栏功能状态开关 

### **参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|callback|Callback|否|返回地理围栏功能状态的回调|

### **返回值:** 

|**类型**|**说明**|
|---|---|
|void|使用参数Callback方法 返回值为void|
|Promise|使用无参数方法返回为Promise,其中boolean值为地理围栏功能状态的结果|

### **示例:** 

//callback mobPush.getGeofenceStatus((isopen) => { console.log("GeofenceStatus:" + isopen) }) //Promise mobPush.getGeofenceStatus().then((isopen) => { this.showMessage("GeofenceStatus:" + isopen) }) 

## **deleteGeofence** 

deleteGeofence(geofenceId: string) 

删除地理围栏 

### **参数:** 

|**参数名**|**类型**|**必填**|**说明**|
|---|---|---|---|
|geofenceId|string|是|地理围栏id|

### **返回值:** 

**类型 说明** 无 无 

### **示例:** 

" mobPush.deleteGeofence( 围栏id") 

## **setGeofenceReceiver** 

setGeofenceReceiver(receiver: MobPushGeofenceReceiver) 

设置触发围栏回调 

### **参数:** 

参数名 类型 必填 说明
receiver MobPushGeofenceReceiver 是 地理围栏触发回调
返回值:
类型 说明
无 无

### **示例:** 

##### //示例代码 

```arkts
let gfReceive: mobPush.MobPushGeofenceReceiver = { onGeofenceReceiver: (data: mobPush.MobPushGeofence[]): void => { let msg = "触发地理围栏:" + JSON.stringify(data) console.log(msg) } } mobPush.setGeofenceReceiver(gfReceive)
```
