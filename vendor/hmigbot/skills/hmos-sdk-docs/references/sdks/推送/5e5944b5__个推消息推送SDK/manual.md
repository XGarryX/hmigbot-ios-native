# **集成指南** 

## **前言** 

开发环境介绍:下述版本中通过验证 

|**DevEco Studio版本号**|**HarmonyOS SDK版本号**|**设备系统版本号**|
|---|---|---|
|DevEco Studio NEXT|API12 Release|5.0.0.26 Beta|
|Beta1(5.0.3.800)|SDK|1|

- 本文档适用 GTSDK 版本:1.0.6 及以后 

- 本文默认读者已经具有基础的鸿蒙知识,以及项目工程结构如下: 

GtsdkDemo/ 

|- entry/ (项目主模块) | |- libs/ (第三方库,用户手动创建) | |- src/ (代码目录) | |- oh-package.json5(模块级oh-package.json5文件) |- build-profile.json5 |- hvigorfile.ts |- oh-package.json5 (顶层oh-package.json5文件) | ...... 注:其中 “......” 表示省略其他与本教程无关的内容,以下 “......” 表示相同意义,不再重复说明。 ## **1.重点提示** ### **1.1开发环境配置** |**DevEco Studio版本号**|**HarmonyOS SDK版本号**|**设备系统版本号**|
|---|---|---|
|DevEco Studio NEXT|API12 Release|5.0.0.26 Beta|
|Beta1(5.0.3.800)|SDK|1|

## **2. 创建个推应用** 

请参考 创建应用 获取相应的 AppID 信息。该信息在之后的步骤配置中将会使用。 

## **3. 通过Partner SDK 方式集成** 

**3.1 打开工程项目,点击Tools —》点击Partner SDK,如下图:** 

### **3.2 找到Push SDK专区的个推消息推送SDK,点击Install即完成了通过 Partner SDK仓库依赖集成,如下图:** 

## **4. 本地集成** 

### **4.1 下载配置SDK的har包** 

通过官网下载或技术支持获取GT-HM-1.0.6.har 

- 在项目主模块entry下创建libs文件夹 

将下载好的har包gtsdk.har放到libs文件夹下 

GtsdkDemo/ 

|- entry/ (项目主模块) | |- libs/ (第三方库,用户手动创建) | |-GT-HM-1.0.6.har (个推推送SDK) | ...... ### **4.2 配置依赖** #### 1. 找到entry模块级oh-package.json5文件,依赖gtsdk.har GtsdkDemo/ |- entry/ (项目主模块) | |- libs/ (第三方库,用户手动创建) | |- src/ (代码目录) | |- oh-package.json5(模块级oh-package文件) | ...... #### 2. oh-package.json5 配置如下: { "license": "", "devDependencies": {}, "author": "", "name": "entry", "description": "Please describe the basic information.", "main": "", "version": "1.0.0", "dependencies": { //依赖gtsdk.har "@getui/push": "file:./libs/GT-HM-1.0.6.har" } } 注意:个推 har 为字节码,必须使用 DevEco Studio 5.0.3.800 及以上版本,并在工程级(最外层)buildprofile.json5,配置"useNormalizedOHMUrl": true { "app": { "products": [ { "buildOption": { "strictMode": { "useNormalizedOHMUrl": true } } } ] } } 3. 运行指令ohpm install - 在控制台进入entry目录,执行ohpm install - 在entry目录下出现oh_modules文件夹,代表依赖成功 ## **5. 配置参数** ### **5.1. 找到entry模块级module.json5文件** GtsdkDemo/ |- entry/ (项目主模块) | |- src/ (代码目录) | | |-mian | | | |-module.json5 |...... ### **5.2. 配置推送参数** { "module": { "metadata": [ { "name": "GETUI_APPID", "value": "AppID信息" } ] } } 注意:如果要支持鸿蒙离线推送,还需要开通鸿蒙推送 并在客户端 module.json5 中配置鸿蒙的 client_id ## **6. 编写集成代码** ### **6.1初始化 SDK** 调用个推初始化代码: PushManager.initialize(Context context) 进行 SDK 的初始化。 为了保证 SDK 服务稳定,开发者需在 App《隐私政策》的 “与授权合作伙伴共享”条款中,将 个推的用户隐私 政策 加入其中。并确保在 App 首次运行时通过明显方式提示终端用户阅读您的 App《隐私政策》,取得终端 用户的合法授权后,再初始化 SDK ,详情可查看:个推合规指南 。

我们建议开发者在 EntryAbility.onCreate()` 方法中初始化个推 SDK。多次调用 SDK 初始化并无影响。 

```arkts
import Want from '@ohos.app.ability.Want'; //引入个推SDK对外接口类PushManager import PushManager from 'GtSDK'; // 通过Parten SDK方式集成时,使用此种方式引入 // import PushManager from 'library'; //通过本地集成时,使用此种方式引入 export default class EntryAbility extends UIAbility { onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void { hilog.info(0x0000, 'EntryAbility', '%{public}s', 'Ability onCreate'); //初始化GTSDK PushManager.initialize({ context: this.context as common.UIAbilityContext, onSuccess: (cid:string) => { " hilog.debug(0x0download/getui/harmonyos/000, "EntryAbility", '%{public}s', 个 推SDK初始化成功,cid = " + cid); }, onFailed: (error:string) => { " hilog.debug(0x0000, "EntryAbility", '%{public}s', 个推SDK初始化失败,error = " + error); } }) } } 
```

另外,为了保证推送通知更好的触达用户,降低用户对于通知开关设置的难度。 我们建议在应用代码中引导用户打开允许应用通知开关。 

```arkts
export default class EntryAbility extends UIAbility { onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void { hilog.info(0x0000, 'EntryAbility', '%{public}s', 'Ability onCreate'); //开启应用通知开关 notificationManager.requestEnableNotification().then(() => { hilog.debug(0x0000, "EntryAbility", '%{public}s', 'requestEnableNotification success'); }).catch((err: BusinessError) => { hilog.debug(0x0000, "EntryAbility", '%{public}s', "error = " + err); }) } } 
```

### **6.2自定义接收推送服务事件** 

- 在项目源码中调用 PushManager.setPushCallback ,用于接收 CID、透传消息以及其他推送服务事件。请参 考下列代码实现各个事件回调方法: 

##### //引入个推SDK对外封装类 

import PushManager, { GTCmdMessage, GTNotificationMessage, GTTransmitMessage } from 'GtSDK'; // 通过Parten SDK方式集成时,使用此种方式引入 

// import PushManager, { GTCmdMessage, GTTransmitMessage, GTNotificationMessage } from 'library'; // 通过本地集成时,使用此种方式引入 

export default class EntryAbility extends UIAbility { 

```arkts
onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void { hilog.info(0x0000, 'testTag', '%{public}s', 'Ability onCreate'); PushManager.setPushCallback({ // 接收 cid onReceiveClientId: (clientId:string) => { hilog.debug(0x0000, 'EntryAbility', '%{public}s', "clientId = " + clientId); }, //接收厂商token onReceiveDeviceToken: (token:string) => { hilog.debug(0x0000, 'EntryAbility', '%{public}s', "token = " + token); }, // cid 离线上线通知 onReceiveOnlineState: (onLine:boolean) => { hilog.debug(0x0000, 'EntryAbility', '%{public}s', "onLine = " + onLine); }, //命令相应回复 onReceiveCommandResult: (result: GTCmdMessage) => { hilog.debug(0x0000, 'EntryAbility', '%{public}s', "cmd = " + JSON.stringify(result)); }, //sdk 收到透传消息 
```

onReceiveMessageData: (message: GTTransmitMessage) => { hilog.debug(0x0000, 'EntryAbility', '%{public}s', "message = " + JSON.stringify(message)); }, //通知到达回调 onNotificationMessageArrived: (message: GTNotificationMessage)  => { hilog.debug(0x0000, 'EntryAbility', '%{public}s', "message = " + JSON.stringify(message)); }, //通知点击回调, 需要配合PushManager.setClickWant(want)使用 onNotificationMessageClicked: (message: GTNotificationMessage) => { hilog.debug(0x0000, 'EntryAbility', '%{public}s', "message = " + JSON.stringify(message)); }, }) } } 

### **6.3 上报个推在线通知点击** 

- 通过个推在线渠道展示的通知类消息,待通知点击打开目的页面后,由客户必须调用 PushManager.setClickWant(want) 完善报表和完成后续业务,以免影响消息业务使用 (重要) 

   - 通知点击打开应用页面(目的页面由下发通知时决定) 通知点击打开浏览器 

   - ..... 

##### //引入个推SDK对外封装类 

import PushManager, { GTCmdMessage, GTTransmitMessage, GTNotificationMessage } from 'GtSDK'; // 通过Parten SDK方式集成时,使用此种方式引入 

// import PushManager, { GTCmdMessage, GTTransmitMessage, GTNotificationMessage } from 'library'; // 通过本地集成时,使用此种方式引入 

export default class EntryAbility extends UIAbility { 

```arkts
onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void { hilog.info(0x0000, 'testTag', '%{public}s', 'Ability onCreate'); 
```

if (want && want.parameters && want.parameters['gtdata']) { 

//注意这里的判断条件,在线点击通知回执和离线报表补全有区别 if (!JsonUtils.hasGttask(want.parameters['gtdata'])) { PushManager.setClickWant(want); 

hilog.info(0x0000, 'EntryAbility', 'onCreate PushManager.setClickWant'); } } } onNewWant(){ 

if (want && want.parameters && want.parameters['gtdata']) { 

if (!JsonUtils.hasGttask(want.parameters['gtdata'])) { PushManager.setClickWant(want); 

hilog.info(0x0000, 'EntryAbility', 'onCreate PushManager.setClickWant'); } } } } 

//上述的JsonUtils.hasGttask方法,需要您创建一个ts类来处理解析json数据,示例代码如下 static hasGttask(gtdata: any): boolean { return gtdata['gttask'] !== undefined; } 

### **6.4 上报透传消息的展示和点击数据** 

**透传消息** :个推只传递数据,不做任何处理,客户端接收到透传消息后需要自己去做后续动作处理,如通知栏展 示、弹框等。 

如果开发者自己本地将 “透传消息” 创建了通知栏展示,建议执行相应动作后,将 ”展示“ 和 ”点击“ 回执上报给个 推。可帮助您完善推送数据、且支持更精确的运营场景。 

以下是上报 **展示和点击** 数据的示例代码,taskid 和 messageid 字段从 GTTransmitMessage 获取: 

PushManager.setPushCallback({ /** *sdk 收到透传消息 */ onReceiveMessageData: (message: GTTransmitMessage) => { hilog.debug(0x0000, 'EntryAbility', '%{public}s', "message = " + JSON.stringify(message)); 

//上报自定义回执使用,PushManager.sendFeedbackMessage let taskid = message.taskId let messageid = message.messageId } }) /** 

* 上报个推透传消息的展示回执。如果透传消息本地创建通知栏消息“展示”了,则调用此方法上报。 */ let gtactionid = 60001;//gtactionid传入60001表示个推渠道消息展示了 let result = PushManager.sendFeedbackMessage(taskid,messageid,gtactionid); /** 

* 上报个推透传消息的点击回执。如果透传消息本地创建通知栏消息“点击”了,则调用此方法上报。 */ let gtactionid = 60002;//gtactionid传入60002表示个推渠道消息点击了 let result = PushManager.sendFeedbackMessage(taskid,messageid,gtactionid); 

### **6.5 鸿蒙厂商离线通知消息报表补全** 

- 如果服务端使用 通知+want 方式推送消息。需要在 want/parameters 中添加 "gttask":"" 参数,添加后个 推会自动在 [want] 里拼接 taskid 和 actionid,app 端接收到参数以后,上报埋点。 app 端接收到拼接之后的 want示例 如下: 

{"deviceId":"","bundleName":"com.getui.push","abilityName":"TestAbility","uri":"https://www.test.com: 8080/push/test","action":"com.test.action","parameters":{"name":"Getui","age":12,"gtdata":{"gtaction": "60090","gttask": "RASS_0514_5e49aa9c73ac8a8881dd95d3c27216af"}}} 

由于鸿蒙没有点击数报表返回,所以需要您在客户端埋点 **上报点击数据** 。点击厂商通知以后,在触发的Ability的 onCreate() 和 onNewWant方法里面接收相关参数,上报离线厂商消息的点击数据。 

#### 客户端示例代码: 

##### //引入个推SDK对外封装类 

import PushManager, { GTCmdMessage, GTTransmitMessage, GTNotificationMessage } from 'GtSDK'; // 通过Parten SDK方式集成时,使用此种方式引入 

// import PushManager, { GTCmdMessage, GTTransmitMessage, GTNotificationMessage } from 'library'; // 通过本地集成时,使用此种方式引入 

export default class EntryAbility extends UIAbility { 

```arkts
onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void { hilog.info(0x0000, 'testTag', '%{public}s', 'Ability onCreate'); 
```

if (want && want.parameters && want.parameters['gtdata']) { 

//注意这里的判断条件,在线点击通知回执和离线报表补全有区别 

if (JsonUtils.hasGttask(want.parameters['gtdata'])) { 

JsonUtils.feedback(want.parameters['gtdata'], this.context); 

hilog.info(0x0000, 'EntryAbility', 'onCreate PushManager feedback'); } } } onNewWant(){ 

if (want && want.parameters && want.parameters['gtdata']) { 

if (JsonUtils.hasGttask(want.parameters['gtdata'])) { 

JsonUtils.feedback(want.parameters['gtdata'], this.context); 

hilog.info(0x0000, 'EntryAbility', 'onCreate PushManager feedback'); } } } } 

//上述的JsonUtils.hasGttask、JsonUtils.feedback方法,需要您创建一个ts类来处理解析json数据、封 装、上报埋点,示例代码如下 

static hasGttask(gtdata: any): boolean { 

return gtdata['gttask'] !== undefined; 

} static async feedback(gtdata: any, con: common.UIAbilityContext) { try { let taskid = gtdata['gttask']; let uuid = util.generateRandomUUID(true).replace("-", ""); let clientid = PushManager.getClientId(); let md5str = await md5Str(taskid + uuid + clientid, 'hex'); //md5方法需要您编写,返回 hex类型 let mesageId = md5str.substring(0, 16); console.log('mesageId = ' + mesageId); PushManager.initialize({ context: con, onSuccess: (cid)=> { // this.cid = '推送ID: ' + cid; }, onFailed: (err)=> { } }) PushManager.sendFeedbackMessage(taskid, mesageId, gtdata['gtaction']); } catch (e) { console.log('err = ' + JSON.stringify(e)); } } 

## **7.Ability页面skills标签配置规范** 

建议按照如下说明进行配置,以免鸿蒙系统包管理模块找不到对应的Ability,影响消息展示、页面跳转等。 

1. module.json5文件中的skills标签下的可以存在多个对象, 每一个skill对应一种能力; 

2. Push的action跳转可以单独写一个: 

"skills":[ { "actions": [ "com.test.action" ] } ] 

3. Push的uris跳转可以这么设置,所在的skill必须同时设置actions参数: 

"skills":[ { "actions": [ "" ], 

"uris": [ { "scheme": "https", "host": "www.xxx.com", "port": "8080", "path": "push/test" } ] } ] 

#### 4. Push既有action跳转,又有uris跳转,也需要分开写{action的skill},{uri的skill} 

"skills":[ { "actions": [ "com.test.action" ] }, { "actions": [ "" ], "uris": [ { "scheme": "https", "host": "www.xxx.com", "port": "8080", "path": "push/test" } ] } ] 

## **8.Ability页面中接收自定义参数** 

//此处是您需要打开的应用Ability页面的onCreate方法 onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void { //接收自定义参数 if (want && want.parameters && want.parameters['自定义key']) { let key = want.parameters['自定义key'] 

hilog.info(0x0000, 'TestAbility-onCreate', '%{public}s', '接收鸿蒙自定义参数:'+key) } } 

//或者在onNewWant接收 onNewWant(want: Want, launchParam: AbilityConstant.LaunchParam): void { //接收自定义参数 

if (want && want.parameters && want.parameters['自定义key']) { let key = want.parameters['自定义key'] 

hilog.info(0x0000, 'TestAbility-onNewWant', '%{public}s', '接收鸿蒙自定义参数:'+key) } } 

## **9.厂商开通** 

略,详情参考《鸿蒙系统华为推送厂商开通&集成指南》 

## **10. 验证推送** 

#### 1. 查看调试日志信息 

EntryAbility.onCreate()` 方法中初始化个推 SDK 

//引入个推SDK对外接口类PushManager import PushManager from 'GtSDK'; // 通过Parten SDK方式集成时,使用此种方式引入 // import PushManager from 'library'; // 通过本地集成时,使用此种方式引入 export default class EntryAbility extends UIAbility { onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void { hilog.info(0x0000, 'EntryAbility', '%{public}s', 'Ability onCreate'); //初始化GTSDK PushManager.initialize({ context: this.context as common.UIAbilityContext, onSuccess: cid => { " hilog.debug(0x0000, "EntryAbility", '%{public}s', 个推SDK初始化成功,cid = " + cid); }, onFailed: error => { " hilog.debug(0x0000, "EntryAbility", '%{public}s', 个推SDK初始化失败,error = " + error); } }) } } 

- 连接手机或启动鸿蒙模拟器,编译运行你的工程,查看 logcat 信息。如果看到 个推SDK初始化成功,cid = = xxx 日志输出,则说明 SDK 初始化成功。 

D 个推SDK初始化成功,cid = c3dbb50ec68c3c45b86559c47eb859d9 D clientId = c3dbb50ec68c3c45b86559c47eb859d9 D token = D onLine = true 

#### 2. 测试推送功能 

登录 个推 ,点击相应应用创建推送,进入待测试应用的推送通知界面: 

依次填写通知标题和通知内容,点击发送按钮即可向该推送应用名下所有 CID 推送通知消息。具体推送 操作方法详见:创建推送通知,下拉通知栏,如果手机或模拟器收到消息,那么恭喜您,个推 SDK 接入 测试已经成功完成!
