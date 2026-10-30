# **API 接口文档** 

## **1. 接口类说明** 

### **本文档所有接口所涉及的相关类及说明如下:** 

|**接口**|**说明**|
|---|---|
|PushManager|SDK功能接口类,用于调用个推相关功能接口|

## **2. 初始化SDK** 

|**类名**|**PushManager**|
|---|---|
|接口|function initialize(params: GTInitializeParams)|

#### **说明:** 

初始化SDK,启动推送服务,成功后返回 clientId 

#### **参数:** 

GTInitializeParams:初始化参数 

|**参数**|**类型**|**必要参数**|**说明**|
|---|---|---|---|
|context|common.UIAbilityContext|是|UIAbilityContext是UIAbility所对应的context|
|onSuccess|(cid: string) => void|否|初始化成功后的回调|
|onFailed|(error: string) => void|否|初始化失败后的回调|

#### **示例** 

import PushManager from 'PushManager' PushManager.initialize({ context: context, onSuccess: (cid) => { //初始化成功 ` console.log( 初始化成功 : ${cid}}`) }, onFailed: (err) => { //初始化失败 ` console.log( 初始化失败 : ${err}`) } }) 

## **3. 自定义接收推送服务事件** 

|**类名**|**PushManager**|
|---|---|
|接口|function setPushCallback(params: GTPushCallback)|

#### **说明** 

- 用于接收 CID、透传消息以及其他推送服务事件 该接口建议在初始化接口之前调用 

#### **参数:** 

##### GTPushCallback:业务回调接口 

|**参数**|**类型**|**必要参数**|**说明**|
|---|---|---|---|
|onReceiveMessageData|(message: GTTransmitMessage) => void|否|sdk收到透传消息|
|onReceiveClientId|(clientId: string) => void|否|sdk获取到clientId|
|onReceiveDeviceToken|(deviceToken: string) => void|否|sdk获取到华为厂商token|
|onReceiveOnlineState|(online: boolean) => void|否|sdk在线状态回调|
|onReceiveCommandResult|(message: GTCmdMessage) => void|否|命令回执|
|onNotificationMessageArrived|(message: GTNotificationMessage) => void|否|通知到达回调|
|onNotificationMessageClicked|(message: GTNotificationMessage) => void|否|通知点击回调|

##### GTTransmitMessage:透传消息 

|**参数**|**类型**|**说明**|
|---|---|---|
|appId|string|个推appId|
|pkgName|string|应用包名(bundleNmae)|
|clientId|string|用户Id|
|taskId|string|任务Id|
|messageId|string|消息Id|
|payloadId|string|透传Id|
|payload|string|透传内容|
|isOffline|boolean|true:离线透传|

##### GTCmdMessage:命令回执消息 

|**参数**|**类型**|**说明**|
|---|---|---|
|appId|string|个推appId|
|pkgName|string|应用包名(bundleNmae)|
|clientId|string|用户Id|
|action|string|回执类型|

##### GTNotificationMessage:通知消息 

|**参数**|**类型**|**说明**|
|---|---|---|
|appId|string|个推appId|
|pkgName|string|应用包名(bundleNmae)|
|clientId|string|用户Id|
|taskId|string|任务Id|
|messageId|string|消息Id|
|title|string|通知标题|
|content|string|通知内容|
|payload|string|通知额外信息|
|url|string|跳转网页url|
|intentUri|string|跳转intentUri|

#### **示例** 

PushManager.setPushCallback({ onReceiveMessageData: (message) => { ` console.log( 收到透传消息 : ${message}`) }, onReceiveOnlineState: (state) => { console.log(`cid 离线上线通知 : ${state}`) }, onReceiveDeviceToken: (token) => { ` console.log( 接收厂商token : ${token}`) }, onReceiveClientId: (cid) => { ` console.log( 接收 cid : ${cid}`) }, onReceiveCommandResult: (message) => { ` console.log( 命令相应回复 : ${message}`) }, 

onNotificationMessageArrived: (message) => { ` console.log( 通知到达 : ${message}`) }, onNotificationMessageClicked: (message) => { ` console.log( 通知点击 : ${message}`) } }) 

## **4. 开启推送** 

|**类名**|**PushManager**|
|---|---|
|接口|function turnOnPush()|

#### **说明:** 

打开 Push 推送,默认是开启状态,可以使用 turnOffPush 接口关闭推送 

#### **参数:** 

无 

#### **示例** 

PushManager.turnOnPush() 

## **5. 关闭推送** 

**类名 PushManager** 接口 function turnOffPush() 

#### **说明:** 

关闭 Push 推送,关闭后则无法收到推送消息,若调用了该接口关闭了推送,则只能调用 turnOnPush 才能正常推 送 

#### **参数:** 

无 

**示例** 

PushManager.turnOffPush() 

## **6. 获取缓存的 CID** 

|**类名**|**PushManager**|
|---|---|
|接口|function getClientId()|

#### **说明:** 

获取当前用户缓存的 cid(长时间未登录或 AppId 发生变化造成的 cid 变化以 14. 获取 CID 接口中的 cid 为准) 

#### **参数:** 

无 

#### **返回:** 

当前用户的 cid,如果未初始化成功,返回 null 

#### **示例** 

const clientId = PushManager.getClientId() console.log(`clientId ${clientId}`) 

## **7. 绑定别名** 

|**类名**|**PushManager**|
|---|---|
|接口|function bindAlias(alias: string, sn: string)|

#### **说明:** 

- 绑定别名,后续可以使用该别名进行定向推送,重复绑定以最后一次为准,两次调用的间隔需大于 1s,单个 cid 在 24 小时内限制调用50次。 

- 可用于与客户账号系统关联,建议将邮箱、昵称、手机号等用户标识设为别名 

- 使用场景:同一个账号(比如手机号)分别登陆在 A、B、C 三台设备上的同一个 APP, 产生了 3 个不同的 cid, 想让这三台设备同时接收到推送,就可以考虑使用该接口,让三台设备的三个 cid 都绑定同一个别名也就 是你的账号(比如手机号),最多支持 10 台设备,也就是最多绑定 10 个 cid 

- 请求结果见推送服务事件中的 onReceiveCommandResult: (message: GTCmdMessage) 

#### **参数:** 

- alias:别名名称:长度 40 字节,支持中、英文(区分大小写)、数字以及下划线 sn:非必填,不能填写"" . 用户自定义的序列号,用来唯一标识该动作,推送服务事件中会回执该结果 

#### **示例** 

//调用 PushManager.bindAlias('alias1','sn1') 

//个推回调 PushManager.setPushCallback({ 

```arkts
onReceiveCommandResult: (result:GTCmdMessage) => { let action: Number = result.action; if(action === PushConst.BIND_ALIAS_RESULT){ let bindAliasCmdMessage = result as BindAliasCmdMessage; let code: Number = bindAliasCmdMessage.code /*  code 结果说明 0:成功 10099:SDK 未初始化成功 30001:绑定别名失败,频率过快,两次调用的间隔需大于 1s 30002:绑定别名失败,参数错误 30003:当前 cid 绑定别名次数超限 30004:绑定别名失败,未知异常 30005:绑定别名时,cid 未获取到 30006:绑定别名时,发生网络错误 30007:别名无效 30008:sn 无效 */ hilog.info(0x0000,'EntryAbility','%{public}s',"sn = "+bindAliasCmdMessage.sn+", clinetId = "+bindAliasCmdMessage.clientId+",pkgname = "+bindAliasCmdMessage.pkgName+ ",appId = "+bindAliasCmdMessage.appId+",action = "+result.action+",code = "+bindAliasCmdMessage.code) } } }) 
```

## **8. 解绑别名** 

|**类名**|**PushManager**|
|---|---|
|接口|function unBindAlias(alias: string, isSelf: boolean, sn: string)|

#### **说明:** 

- 解绑别名,两次调用的间隔需大于 1s。只能解绑与当前应用 cid 关联的别名,单个 cid 在 24 小时内限制调用 50次。 

请求结果见推送服务事件中的 onReceiveCommandResult: (message: GTCmdMessage) 

#### **参数:** 

##### alias:别名名称 

- isSelf:是否只对当前cid有效,如果是true,只对当前cid做解绑;如果是false,对所有绑定该别名的cid列表 做解绑 

- sn:非必填,不能填写"" .用户自定义的序列号,用来唯一标识该动作,推送服务事件中会回执该结果 

#### **示例** 

###### //调用 

PushManager.unBindAlias('alias1','sn1') 

###### //个推回调 

```arkts
PushManager.setPushCallback({ onReceiveCommandResult: (result:GTCmdMessage) => { let action: Number = result.action; if (action === PushConst.UNBIND_ALIAS_RESULT) { let unBindAliasCmdMessage = result as UnBindAliasCmdMessage let code: Number = unBindAliasCmdMessage.code /* code 结果说明 0:成功 10099:SDK 未初始化成功 30001:解绑别名失败,频率过快,两次调用的间隔需大于 1s 30002:解绑别名失败,参数错误 30003:当前 cid 解绑别名次数超限 30004:解绑别名失败,未知异常 30005:解绑别名时,cid 未获取到 30006:解绑别名时,发生网络错误 30007:别名无效 30008:sn 无效*/ hilog.info(0x0000,'EntryAbility','%{public}s',"sn = "+unBindAliasCmdMessage.sn+", clinetId = "+unBindAliasCmdMessage.clientId+",pkgname = "+unBindAliasCmdMessage.pkgName+ ",appId = "+unBindAliasCmdMessage.appId+",action = "+result.action+",code = "+unBindAliasCmdMessage.code) } } }) 
```

## **8. 设置用户标签** 

|**类名**|**PushManager**|
|---|---|
|接口|function setTag(tags: Tag[], sn: string)|

#### **说明:** 

##### 设置一组标签,后续可使用该标签定向推送 

- 需要在获取到 clientId 之后调用。两次调用间隔不能小于1s,默认一天只能成功设置一次(可联系技术支持进 行修改) 

请求结果见推送服务事件中的 onReceiveCommandResult: (message: GTCmdMessage) 

#### **参数:** 

##### tags:标签数组, 数组长度最大200 

- sn:用户自定义的序列号,用来唯一标识该动作,推送服务事件中会回执该结果 

#### **示例** 

###### //调用 

PushManager.setTag([new Tag().setName("tag1"), new Tag().setName("tag2")], "sn1") 

//个推回调 PushManager.setPushCallback({ onReceiveCommandResult: (result:GTCmdMessage) => { let action: Number = result.action; if(action === PushConst.SET_TAG_RESULT) { let setTagCmdMessage = result as SetTagCmdMessage let code: Number = setTagCmdMessage.code /*  code 值说明 0:成功 10099:SDK 未初始化成功 20001:tag 数量过大(单次设置的 tag 数量不超过 100) 20002:调用次数超限(默认一天只能成功设置一次) 20003:标签重复 20004:服务初始化失败 20005:setTag 异常 20006:tag 为空 20007:sn 为空 20008:离线,还未登陆成功 20009:该 appid 已经在黑名单列表(请联系技术支持处理) 20010:已存 tag 数目超限 20011:tag 内容格式不正确 */ hilog.info(0x0000, 'EntryAbility', '%{public}s', "sn = " + setTagCmdMessage.sn + ",clinetId = " + setTagCmdMessage.clientId + ",pkgname = " + setTagCmdMessage.pkgName + ",appId = " + setTagCmdMessage.appId + ",action = " + result.action + ",code = " + setTagCmdMessage.code) } } }) 

## **9. 查询用户标签** 

|**类名**|**PushManager**|
|---|---|
|接口|function queryTag(sn: string)|

#### **说明:** 

##### 返回用户的标签 

请求结果见推送服务事件中的 onReceiveCommandResult: (message: GTCmdMessage) 

#### **参数:** 

sn:用户自定义的序列号,用来唯一标识该动作, 推送服务事件中会回执该结果 

#### **示例** 

//调用 PushManager.queryTag("sn1") 

//个推回调 PushManager.setPushCallback({ onReceiveCommandResult: (result:GTCmdMessage) => { let action: Number = result.action; let queryTagCmdMessage = result as QueryTagCmdMessage let code: Number = queryTagCmdMessage.code /*  code 值说明 0:成功 20002:查询标签失败,频率过快 20007:sn为空 */ hilog.info(0x0000,'EntryAbility','%{public}s',"sn = "+queryTagCmdMessage.sn+", clinetId = "+queryTagCmdMessage.clientId+",pkgname = "+queryTagCmdMessage.pkgName+ ",appId = "+queryTagCmdMessage.appId+",action = "+result.action+",code = "+queryTagCmdMessage.code+",tags = "+queryTagCmdMessage.tags) } } }) 

## **10. 自定义actionId** 

|**类名**|**PushManager**|
|---|---|
|接口|function sendFeedbackMessage(taskId: string, messageId: string, actionId: number)|

#### **说明:** 

上行第三方自定义actionid 

#### **参数:** 

taskId:下发任务的任务ID messageId:下发任务的消息ID actionId:自定义的actionId,取值范围是 90001-90999 

## **11. 设置静默时间** 

|**类名**|**PushManager**|
|---|---|
|接口|function setSilentTime(beginHour: number, duration: number)|

#### **说明:** 

设置静默时间 

#### **参数:** 

beginHour:开始时间,beginHour >= 0 && beginHour < 24,单位 h duration:持续时间,duration > 0 && duration <= 23,持续时间为 0 则取消静默,单位 h 

## **12. 上报通知点击** 

|**类名**|**PushManager**|
|---|---|
|接口|function setClickWant(want: Want)|

#### **说明:** 

通过个推在线渠道展示的通知类消息,个推不监听通知点击事件。待通知点击打开目标页面后,由客户调用 PushManager.setClickWant(want) 完善报表 

#### **参数:** 

want:目标页面接受到的Want参数 

#### **示例** 

```arkts
export default class EntryAbility extends UIAbility { onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void { if (want && want.parameters && want.parameters['taskid']) { PushManager.setClickWant(want); hilog.info(0x0000, 'EntryAbility', 'onCreate PushManager.setClickWant'); } } onNewWant(want: Want, launchParam: AbilityConstant.LaunchParam): void { hilog.info(0x0000, 'EntryAbility', 'onCreate PushManager.setClickWant'); PushManager.setClickWant(want); } } 
```

## **13. 获取 SDK 版本号** 

|**类名**|**PushManager**|
|---|---|
|接口|function getSDKVersion()|

#### **说明:** 

获取当前 SDK 版本号 

#### **参数:** 

无 

**返回:** 

当前 SDK 版本号字符串 

## **14. 设置⻆标** 

|**类名**|**PushManager**|
|---|---|
|接口|function setBadgeNum(badgeNum: number)|

#### **说明:** 

设置APP的⻆标数字 

#### **参数:** 

badgeNum:⻆标数字 

#### **返回:** 

无 

**示例** 

PushManager.setBadgeNum(1)
