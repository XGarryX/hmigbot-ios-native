免费注册

产品 解决方案 成功案例 海外消息服务 开发者支持 关于极光   语言 登录 免费注册 文档中心 合规指南 开发者社区 输入关键词搜索 极光推送 极光文档 > 极光推送 > 客户端 SDK > HarmonyOS SDK > SDK 集成指南 本页目录 使用提示 产品功能说明 SDK 集成指南 主要功能 产品简介 最近更新:2025-08-04 主要特点 快速开始 集成方式 自动集成 控制台指南 **使用提示** 手动集成 客户端 SDK SDK 本文是 JPush HarmonyOS SDK 标准的集成指南文档。用以指导 SDK 的使用方法,默认读者已经熟悉 DevEco Studio 的基本使用方法,以及具有一定的 HarmonyOS 配置 hmos平台信息 配置极光平台信息 编程知识基础。 Android SDK 配置通知跳转页 本篇指南匹配的 JPush HarmonyOS SDK 版本为:1.1.0 及以后版本。 HarmonyOS SDK 申请打开通知开关 目前支持 HarmonyOS API 12 及其以上版本。 配置自定义信息 SDK 集成指南集成指南 极光推送 文档网站 上,有极光推送相关的所有指南、API、教程等全部的文档。包括本文档的更新版本,都会及时地发布到该网站上。 配置通知扩展消息 SDK API 配置推送VoIP呼叫消息 配置「前台不展示功能」 厂商参数申请指南 **产品功能说明** 启用推送业务功能 错误码 极光推送(JPush)是一个端到端的推送服务,使得服务器端消息能够及时地推送到终端用户手机上,让开发者积极地保持与用户的连接,从而提高用户活跃度、提高应 配置权限 iOS SDK 用的留存率。极光推送客户端支持 Android,iOS,HarmonyOS,QuickApp 多个平台。 进阶功能 QuickApp 本 HarmonyOS SDK 方便开发者基于 JPush 来快捷地为 HarmonyOS App 增加推送功能。 获取 Registration ID 建议 其他功能 合规指引 技术支持 **主要功能** 客户端集成插件 保持与服务器的长连接,以便消息能够即时推送到达客户端 REST API 接收通知,并向开发者 App 传递相关信息 最佳实践指南 **主要特点** 常见问题 客户端维持连接占用资源少、耗电低 更新日志 SDK 丰富的接口,可定制通知栏提示样式 服务器大容量、稳定 **集成方式 自动集成** har **依赖 说明** :在 entry 模块下的 oh-package.json5 文件添加 `"dependencies": { "@jg/push": "x.x.x"//` 填写对应版本号,如: `"@jg/push": "1.3.0" }` **说明** 2:现在har为字节码,需升级ide到5.0.3.500以上,并在工程级(最外层)build-profile.json5,配置"useNormalizedOHMUrl": true `"products": [ { "buildOption": { "strictMode": { "useNormalizedOHMUrl": true` _`//`_ 打开 `} }, "name": "default", "signingConfig": "default", "compileSdkVersion": "5.0.0(12)", "compatibleSdkVersion": "5.0.0(12)", "runtimeOS": "HarmonyOS" } ]` **手动集成** 集成压缩包下载链接:前往下载,集成压缩包内容 jpush-hmos-x.x.x-release.zip **集成压缩包内容** jpush-hmos-x.x.x-release.har 极光开发者服务的核心包。 doc 文档 entry 是一个 hmos demo 项目代码,通过这个演示了 JPush SDK 的基本用法,可以用来做参考。 har **文件集成** 解压缩 jpush-hmos-x.x.x-release.zip 集成压缩包。 复制 jpush-hmos-x.x.x-release.har 到你的工程的 entry/hars/ 目录下。(hars这个目录可以自定义) **说明** :关联jpush-hmos-x.x.x-release.har,如,你复制 har 到 entry/hars/ 目录下,那么在 entry 模块下的 oh-package.json5 文件添加 `"dependencies": { "jg_harmony_har": "./hars/jpush-hmos-x.x.x-release.har"` _`//`_ 这里的路径是你存放 _`jpush-hmos-x.x.x-release.har`_ 的位置 `}` **说明** 2:现在har为字节码,需升级ide到5.0.3.500以上,并在工程级(最外层)build-profile.json5,配置"useNormalizedOHMUrl": true `"products": [ { "buildOption": { "strictMode": { "useNormalizedOHMUrl": true` _`//`_ 打开 `} }, "name": "default", "signingConfig": "default", "compileSdkVersion": "5.0.0(12)", "compatibleSdkVersion": "5.0.0(12)", "runtimeOS": "HarmonyOS" } ]` **配置** hmos **平台信息** 想要推送功能,需要配置 HarmonyOS 平台信息 主要步骤为: 在 hmos 平台获取到项目下所在应用对应的 client_id(注意不是项目的client_id) 特别注意,鸿蒙应用创建完成后,您一定要记得配置应用「SHA256证书/公钥指纹」:点击“SHA256证书/公钥指纹”后的“添加公钥指纹(HarmonyOS API 9及 以上)”,按照如下文描述「配置签署」。 在hmos平台开通推送服务 在本地工程配置应用 client_id 说明: 本地工程配置应用 client_id,需在 entry 模块下的 module.json5 文件添加 `"module": { "metadata": [ { "name": "client_id", " "value":` 你的 `id" } ] }` 配置签署 步骤1:准备签署文件 https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V5/ide-publish-app-0000001053223745-V5#section793484619307 步骤2:申请发布证书 https://developer.huawei.com/consumer/cn/doc/app/agc-help-add-releasecert-0000001946273961 步骤3:申请发布Profile,Profile格式为.p7b https://developer.huawei.com/consumer/cn/doc/app/agc-help-add-releaseprofile-0000001914714796 步骤4:在本地工程配置签署,如图 **配置极光平台信息** 上述步骤完成后,还需要配置极光平台信息 主要步骤为: 在极光平台创建应用,并确保如下两个信息:包名和 appKey,与极光平台一致。 说明1: 在本地工程配置包名,方式:在 AppScope 工程下的 app.json5 文件添加 `{ "app": { " " "bundleName":` 你的包名 `, } }` 说明2: 在本地工程配置极光appKey(极光控制台创建应用后自动生成的应用标识),代码配置 如: `export default class MyAbilityStage extends AbilityStage { onCreate() { JPushInterface.setAppKey("` 你的 `appKey")` _`//`_ 在 _`init`_ 之前调用 `} }` 说明3: 在本地工程配置接收回调信息, 代码配置 如: `export default class MyAbilityStage extends AbilityStage { onCreate() { JPushInterface.setCallBackMsg(` 继承 `CallBackMsg` 的实体类 `)` _`//`_ 接收回调信息,在 _`init`_ 之前调用 `} }` **配置通知跳转页** 通知支持跳转到指定页面 通过uris来匹配页面: uris,通过uri来匹配页面,推送时 url=你的scheme://你的host:你的port/你的path 注意:uris方式,actions 一定要配置为空字符串 `{ "exported": true, "skills": [ { "actions": [""],` _`//actions`_ 一定要配置为空字符串 `"uris": [ { "scheme": "` 你的 `scheme", "host": "` 你的 `host", "port": "` 你的 `port", "path": "` 你的 `path" } ] } ] }` 通过actions来匹配页面: actions 通过actions来匹配页面,actions填入你的对应值,推送时actions=你的actions `{ "exported": true, "skills": [ { "actions": ["` 你的 `actions"], } ] }` **申请打开通知开关** 如果没有打开通知开关,将收不到通知 主要步骤为: 在首页申请 `export default class EntryAbility extends UIAbility { onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void { notificationManager.requestEnableNotification().then(() => { hilog.info(0x0000, TAG, '%{public}s', `requestEnableNotification success`); }).catch((err: Base.BusinessError) => { hilog.error(0x0000, TAG, '%{public}s', `requestEnableNotification failed, code is ${err.code}, message is ${err.m essage}`); }); } }` **配置自定义信息** 如果需要处理通过鸿蒙通道下发的自定义消息,需按以下步骤配置: **步骤一** 在项目模块级目录的 src/main/resources/base/profile/ 下创建 PushMessage.json 文件,文件内容如下: `{ "path": "pushmessage/t_push_message", "type": "rdb", "scope": "application" }` path:固定值为 pushmessage/t_push_message,表示数据库和表名称。 type:固定值为 rdb,表示关系型数据库。 scope:表示数据库的范围,可填 application(应用级)或module(hap模块级)。 并且,在项目模块级目录的 src/main/module.json5 文件添加 proxyData 如下配置: `{ "module": { "proxyData":[{ "uri": "datashareproxy://{bundleName}/PushMessage", "requiredWritePermission": "ohos.permission.WRITE_PRIVACY_PUSH_DATA", "metadata":{ "name": "dataProperties", "resource": "$profile:PushMessage" } }] } }` uri:固定格式为 datashareproxy://{bundleName}/PushMessage,请将{bundleName}替换为您应用的bundleName,PushMessage为固定名称,请勿随意更 改。 requiredWritePermission:固定值为 ohos.permission.WRITE_PRIVACY_PUSH_DATA,推送服务需要使用该权限往数据库里写入BACKGROUND消息数据。 metadata:扩展配置,name固定值为dataProperties,resource固定格式为$profile:文件名称,文件名称固定为PushMessage。 **步骤二** 在您项目的ability(下以PushMessageAbility为例)内导入push模块, 注意,您仅能使用UIAbility接收BACKGROUND消息。 `import { UIAbility } from '@kit.AbilityKit'; import { JPushInterface } from '@jg/push'; import { pushCommon, pushService } from '@kit.PushKit'; import { hilog } from '@kit.PerformanceAnalysisKit'; const TAG: string = 'JPUSH-JLog-PushMessageAbility' export default class PushMessageAbility extends UIAbility { onCreate(): void { try {` _`// receiveMessage`_ 中的参数固定为 _`BACKGROUND-------`_ 后台自定义信息接收 `pushService.receiveMessage('BACKGROUND', this, async (data: pushCommon.PushPayload) => { let jg = await JPushInterface.customMessageBackgroundData(data) if (jg) {` _`//`_ 如果是 _`true`_ 为已经处理 `return } }); } catch (e) { hilog.info(0x0000, TAG, '%{public}s', 'BACKGROUND fail:'+JSON.stringify(e)); } }` 并且,在项目工程的 src/main/module.json5文件的abilities模块中配置skills中actions内容为action.ohos.push.listener(有且只能有一个ability定义该action,若 同时添加uris参数,则uris内容需为空)。 `"abilities": [ { "name": "PushMessageAbility", "srcEntry": "./ets/entryability/PushMessageAbility.ets", "launchType": "singleton", "startWindowIcon": "$media:icon", "startWindowBackground": "$color:start_window_background", "skills": [ { "actions": [ "action.ohos.push.listener" ] } ] } ]` **配置通知扩展消息** 如果有通知扩展消息需求,需以下配置 主要步骤为: **步骤一** 进程不存在会走这个流程(通知扩展进程),您在该进程中自行完成语音播报业务处理,并返回特定的消息内容(例如title、body等)覆盖当前消息内容后,Push Kit将弹出通知提醒。 在您的工程内创建一个ExtensionAbility类型的组件并且继承RemoteNotificationExtensionAbility,完成onReceiveMessage() 方法的覆写,调用 JPushInterface.receiveExtraDataMessage方法获取数据,代码示例如下: `import { pushCommon, RemoteNotificationExtensionAbility } from '@kit.PushKit'; import { hilog } from '@kit.PerformanceAnalysisKit'; import { JPushInterface } from '@jg/push'; const TAG: string = 'JPUSH-JLog-RemoteNotificationExtAbility' export default class RemoteNotificationExtAbility extends RemoteNotificationExtensionAbility { async onReceiveMessage(remoteNotificationInfo: pushCommon.RemoteNotificationInfo): Promise<pushCommon.RemoteNotificat ionContent> { hilog.info(0x0000, TAG, 'onReceiveMessage, remoteNotificationInfo: %{public}s', JSON.stringify(remoteNotificationInfo)); let jMessageExtra = await JPushInterface.receiveExtraDataMessage(this, remoteNotificationInfo); hilog.info(0x0000, TAG, 'onReceiveMessage jMessageExtra:' + JSON.stringify(jMessageExtra)); return {}` _`//`_ 如果要修改通知可以反回有数据通知 `} onDestroy(): void { hilog.info(0x0000, TAG, 'RemoteNotificationExtAbility onDestroy.'); } }` 并且,在项目工程的src/main/module.json5文件的extensionAbilities模块中配置RemoteNotificationExtAbility的type和actions信息(有且仅有一个 ExtensionAbility,配置如下,若同时添加uris参数,则uris内容需为空): `"extensionAbilities": [ { "name": "RemoteNotificationExtAbility", "type": "remoteNotification", "srcEntry": "./ets/entryability/RemoteNotificationExtAbility.ets", "description": "RemoteNotificationExtAbility test", "exported": false, "skills": [ { "actions": ["action.hms.push.extension.remotenotification"] } ] } ]` type:固定值为remoteNotification,表示通知扩展的ExtensionAbility类型。 actions:固定值为action.hms.push.extension.remotenotification,用于接收通知扩展消息。 **步骤二** 进程存在时会走这个流程,若您的应用进程存在,无论应用在前台或者在后台均不弹出通知提醒 您可以通过receiveMessage()方法实时获取通知扩展消息数据,示例代码如下: `import { UIAbility } from '@kit.AbilityKit'; import { JPushInterface } from '@jg/push'; import { pushCommon, pushService } from '@kit.PushKit'; import { hilog } from '@kit.PerformanceAnalysisKit'; const TAG: string = 'JPUSH-JLog-PushMessageAbility' export default class PushMessageAbility extends UIAbility { onCreate(): void { try {` _`// receiveMessage`_ 中的参数固定为 _`IM-------`_ 拓展通知接收 `pushService.receiveMessage('IM', this, async (data) => { let jg = await JPushInterface.extraMessageBackgroundData(data) if (jg) {` _`//`_ 如果是 _`true`_ 为已经处理 `return } }); } catch (e) { hilog.info(0x0000, TAG, '%{public}s', 'IM fail:'+JSON.stringify(e)); } }` 并且在项目模块的src/main/module.json5中的skills里配置actions内容为 action.ohos.push.listener(有且只能有一个ability定义该action,若同时添加uris参 数,则uris内容需为空): `"abilities": [ { "name": "PushMessageAbility", "srcEntry": "./ets/entryability/PushMessageAbility.ets", "launchType": "singleton", "startWindowIcon": "$media:icon", "startWindowBackground": "$color:start_window_background", "skills": [ { "actions": [ "action.ohos.push.listener" ] } ] } ]` **配置推送** VoIP **呼叫消息** 如果有推送VoIP呼叫消息需求,需以下配置 主要步骤为: **步骤一** 在您的工程内创建一个UIAbility类型的组件,如PushMessageAbility.ets(在项目工程的src/main/ets/entryability目录下),负责处理VoIP呼叫消息接收,代码示 例如下: `import { UIAbility } from '@kit.AbilityKit'; import { JPushInterface } from '@jg/push'; import { pushCommon, pushService } from '@kit.PushKit'; import { hilog } from '@kit.PerformanceAnalysisKit'; const TAG: string = 'JPUSH-JLog-PushMessageAbility' export default class PushMessageAbility extends UIAbility { onCreate(): void { try { pushService.receiveMessage('VoIP', this, async (data) => { let jg = await JPushInterface.voIPMessageBackgroundData(data) if (jg) {` _`//`_ 如果是 _`true`_ 为已经处理 `return } }); } catch (e) { hilog.info(0x0000, TAG, '%{public}s', 'VoIP fail:'+JSON.stringify(e)); } } }` 并且,在项目工程的 src/main/module.json5 文件的 abilities 模块中配置PushMessageAbility的actions信息。 `"abilities": [ { "name": "PushMessageAbility", "srcEntry": "./ets/entryability/PushMessageAbility.ets", "launchType": "singleton", "description": "PushMessageAbility test", "startWindowIcon": "$media:startIcon", "startWindowBackground": "$color:start_window_background", "exported": false, "skills": [ { "actions": ["action.ohos.push.listener"] } ] } ]` actions:内容为action.ohos.push.listener,有且只能有一个ability定义该action,若同时添加uris参数,则uris内容需为空。 **配置「前台不展示功能」** 如果有「前台不展示」功能需求,需以下配置 主要步骤为: **步骤一** 在您的工程内创建一个UIAbility类型的组件,如PushMessageAbility.ets(在项目工程的src/main/ets/entryability目录下),负责处理VoIP呼叫消息接收,代码示 例如下: `import { UIAbility } from '@kit.AbilityKit';` 

文档中心 合规指南
极光推送
产品简介
快速开始
控制台指南
客户端 SDK SDK
Android SDK
HarmonyOS SDK
SDK 集成指南集成指南
SDK API
厂商参数申请指南
错误码
iOS SDK
QuickApp
合规指引
客户端集成插件
REST API
最佳实践指南
常见问题
更新日志

import { JPushInterface } from '@jg/push';

```arkts
import { pushCommon, pushService } from '@kit.PushKit';
import { hilog } from '@kit.PerformanceAnalysisKit';
```

`const TAG: string = 'JPUSH-JLog-PushMessageAbility' export default class PushMessageAbility extends UIAbility { onCreate(): void { try { pushService.receiveMessage('DEFAULT', this, async (data: pushCommon.PushPayload) => { let jg = await JPushInterface.defaultMessageBackgroundData(data) if (jg) {` _`//`_ 如果是 _`true`_ 为已经处理 `return } }); } catch (e) { hilog.info(0x0000, TAG, '%{public}s', 'DEFAULT fail:'+JSON.stringify(e)); } } }` 并且,在项目工程的 src/main/module.json5 文件的 abilities 模块中配置PushMessageAbility的actions信息。 `"abilities": [ { "name": "PushMessageAbility", "srcEntry": "./ets/entryability/PushMessageAbility.ets", "launchType": "singleton", "description": "PushMessageAbility test", "startWindowIcon": "$media:startIcon", "startWindowBackground": "$color:start_window_background", "exported": false, "skills": [ { "actions": ["action.ohos.push.listener"] } ] } ]` actions:内容为action.ohos.push.listener,有且只能有一个ability定义该action,若同时添加uris参数,则uris内容需为空。 **启用推送业务功能** 主要步骤为: 在 init 之前要先设置 appKey 在 init 之前要先设置接收回调信息类 `export default class MyAbilityStage extends AbilityStage { onCreate() { JPushInterface.setCallBackMsg(` 继承 `CallBackMsg` 的实体类 `)` _`//`_ 接收回调信息 _`//`_ 在 _`init`_ 之前调用 `JPushInterface.setAppKey("` 你的 `appKey")` _`//`_ 在 _`init`_ 之前调用 `JPushInterface.init(this.context.getApplicationContext()) } }` **配置权限** 必选权限,为了更精准推送,申请结束后再调用 init 启用推送业务功能接口。 从 v1.1.1 版本开始,开发者不需要手动配置,SDK已经内置。 主要步骤为: 配置文件权限声明 

向用户申请授权,申请结束后再调用 init 启用推送业务功能接口 

说明1:
配置文件权限声明, 在 entry 模块下的 src/main/module.json5 文件添加
{
"module": {
"requestPermissions": [
    {
"name": "ohos.permission.APP_TRACKING_CONSENT",
"
"reason":  $string:reason",
"usedScene": {
"abilities": [
"EntryAbility" // 一般要用首页
        ],
"when": "always"
      }
    }
  ]
}
}
说明2:
向用户申请授权,在首页 EntryAbility 中申请,然后再启用推送业务功能,如:
const permissions: Array<Permissions> = ['ohos.permission.APP_TRACKING_CONSENT'];
export default class EntryAbility extends UIAbility {
onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void {
let context:Context = this.context;
let atManager:abilityAccessCtrl.AtManager = abilityAccessCtrl.createAtManager();
  atManager.requestPermissionsFromUser(context, permissions).then((data: PermissionRequestResult) => {
//  授权成功  // 然后启用推送业务功能
    JPushInterface.init(this.context.getApplicationContext())
  }).catch((err: BusinessError) => {
// 然后启用推送业务功能
    JPushInterface.init(this.context.getApplicationContext())
  })
}
进阶功能
获取  Registration ID  建议
由于极光推送所有形式的推送最后都会转化为对 Registration ID 推送,因此排查客户问题的时候需要提供 Registration ID。为了方便线上客户准确提供信息,减少沟通
成本,我们建议您完成 SDK 集成后,在 App 的【关于】、【意见反馈】、【我的】等比较不常用的 UI 中展示客户的 Registration ID 。
示例代码:
JPushInterface.getRegistrationID();
其他功能
请参考:
API:HarmonyOS SDK
技术支持
当出现问题时:
你可以到极光社区搜索类似问题
给我们的 support 发邮件 support@jiguang.cn
为了更快速的解决问题,在寻求帮助时,请提供下列信息:
你需要咨询的产品是 JPush,是否同时使用了极光其他的产品
你所调用的是什么 API,所传参数,完整的报错信息,出现异常的时间点
如果收不到消息,提供应用的 Appkey,消息的 Message ID,设备的 registration ID 信息
如果是 SDK 问题请提供对应的 SDK 版本和完整的日志记录,日志信息请使用 TXT 文件上传
出现异常的设备是 HarmonyOS ,列出具体的机型和系统

 
 
 
 

          

 

提交评分

文档内容是否对您有帮助? 提交评分 

Copyright 2011-2025, jiguang.cn, All Rights Reserved. 粤ICP备12056275号-13 深圳市和讯华谷信息技术有限公司
