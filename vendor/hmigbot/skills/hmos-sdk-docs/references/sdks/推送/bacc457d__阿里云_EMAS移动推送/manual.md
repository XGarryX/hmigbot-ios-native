# **HarmonyOS SDK接入** 

本章节介绍了 HarmonyOS SDK 的接入方法。 

## **前言** 

本 SDK 基于 HarmonyOS API 12 Release 开发, compileSdkVersion 为 5.0.0(12) 。 

## **准备工作** 

1. 请参考 HarmonyOS 应用开发文档准备 HarmonyOS 应用开发环境。 

2. 请参考 Native 应用开发流程创建鸿蒙应用,在应用设置中查看 AppKey 和 AppSecret 。 

3. 请参考 HarmonyOS Push Kit 开发准备,配置应用,获取鸿蒙 Push Token 。 

4. 请参考请求通知授权实现应用请求授权逻辑。 

5. 如需推送通知扩展消息,请参考发送通知扩展消息申请相关权益。 

## **第一步:安装SDK** 

在 HarmonyOS 应用根目录执行以下命令来安装 SDK : 

ohpm install @aliyun/push 

ohpm 工具及更多关于 OpenHarmony 安装第三方 SDK 的信息请参考 OpenHarmony 三方库中心仓说明。 SDK 的最新版本及更新记录请参考 SDK 信息和更新记录。 

## **第二步:初始化SDK** 

在 Ability onCreate 生命周期回调中执行以下代码初始化配置 SDK : 

```arkts
import { AbilityConstant, UIAbility, Want } from '@kit.AbilityKit'; import { window } from '@kit.ArkUI'; import { aliyunPush } from '@aliyun/push'; export default class EntryAbility extends UIAbility { onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void { // ************* 初始化配置 begin ************* aliyunPush.init({ appKey: ' 请填入在准备工作中查询的应用 AppKey', appSecret: ' 请填入在准备工作中查询的应用 AppSecret', context: this.context, }) // ************* 初始化配置 end ************* } // 省略其它代码 } 
```

其中 appKey , appSecret 请配置为在准备工作中获取的 AppKey 和 AppSecret 。 

## **第三步:设置推送回调接口** 

### 在 UIAbility 的 onCreate 回调方法中并且在初始化 SDK 之后设置推送回调接口,用于接收推送数据。示例代码如下: 

```arkts
import { AbilityConstant, UIAbility, Want } from '@kit.AbilityKit'; import { window } from '@kit.ArkUI'; 
```

import { aliyunPush, ExtensionNotification, IPushListener, PushMessage, PushNotification } from 

p { y , '@aliyun/push'; 

, 

, 

g , 

} 

// ************* IPushListener 接口实现 begin ************* /** * 推送回调接口实现,用于接收推送数据 */ class MyPushListener implements IPushListener { onReceiveNotification(data: PushNotification | ExtensionNotification): boolean { // 处理推送通知 // 返回 false 表示不定制通知。返回 true ,表示定制通知。 return false; } onShowNotification(data: PushNotification | ExtensionNotification): void { // 处理通知展示事件 } onReceiveMessage(data: PushMessage): void { // 处理推送消息 } } // ************* IPushListener 接口实现 end ************* export default class EntryAbility extends UIAbility { onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void { aliyunPush.init({ appKey: ' 请填入在 SDK 接入准备工作中查询的应用 AppKey', appSecret: ' 请填入在 SDK 接入准备工作中查询的应用 AppSecret', context: this.context, }) // ************* 注册 IPushListener 接口 begin ************* aliyunPush.setPushListener(new MyPushListener()); // ************* 注册 IPushListener 接口 end ************* } // 省略其它代码 onDestroy(): void { } onWindowStageCreate(windowStage: window.WindowStage): void { // Main window is created, set main page for this ability windowStage.loadContent('pages/Index', (err) => { if (err.code) { return; } }); } onWindowStageDestroy(): void { // Main window is destroyed, release UI related resources } onForeground(): void { // Ability has brought to foreground } onBackground(): void { 

// Ability has back to background } } 

### 关于推送回调接口的详细说明,请参考接收推送通知 / 消息。 

## **第四步:调用推送通知点击处理接口** 

调用 SDK 的 handleClickNotification 方法,用于处理用户点击通知的行为,获取推送的数据。调用的位置有两处: 

1. 在 UIAbility 的 onCreate 回调方法中并且在初始化 SDK 之后 

2. 在 UIAbility 的 onNewWant 回调方法中 

示例代码如下: 

```arkts
import { aliyunPush, Channel, ExtensionNotification, PushMessage, PushNotification, PushNotificationHandler } from '@aliyun/push'; import { AbilityConstant, UIAbility, Want } from '@kit.AbilityKit'; 
// ************* 自定义推送数据的处理类 begin ************* class MyPushNotificationHandler implements PushNotificationHandler { onClickNotification(data: PushNotification | PushMessage | ExtensionNotification, from: Channel): vo id { // 根据业务处理推送的数据 } 
noPushData(): void { // 没有推送数据,不是用户点击推送通知拉起的界面 } } // ************* 自定义推送数据的处理类 end ************* 
// 点击通知要打开的 Ability 
export class TargetAbility extends UIAbility { onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void { // ************* 初始化 Push begin ************* aliyunPush.init({ appKey: ' 请填入在准备工作中查询的应用 AppKey', appSecret: ' 请填入在准备工作中查询的应用 AppSecret', context: this.context, }) // ************* 初始化 Push end ************* // ************* 处理推送数据 begin ************* aliyunPush.handleClickNotification(want, new MyPushNotificationHandler()) // ************* 处理推送数据 end ************* 
```

} 

onNewWant(want: Want, launchParam: AbilityConstant.LaunchParam): void { // 页面已经启动的场景 // ************* 处理推送数据 begin ************* aliyunPush.handleClickNotification(want, new MyPushNotificationHandler()) // ************* 处理推送数据 end ************* } 

// 省略其它代码 } 

关于 handleClickNotification 方法的详细说明,请参考从通知中获取推送数据。 

## **第五步:注册设备获取设备ID** 

在 UIAbility 的 onCreate 回调方法中,初始化 SDK 之后,需要调用 SDK 的 register 方法注册设备。 

注册设备是推送的必要步骤,在成功注册设备之后,才可以请求注册鸿蒙 PushToken ,绑定账号、添加别名、绑定标签等一 系列 API 。 

示例代码如下: 

import { aliyunPush } from '@aliyun/push'; aliyunPush.register((err) => { if (err) { console.error(` 注册设备失败,错误码 :${err.code} 错误信息 ${err.message}`); return; } console.info(` 注册设备成功,设备 ID 为 ${aliyunPush.getDeviceId()}`); }); 

设备注册成功后, SDK 会和服务端建立长连接,此时就可以调用 getDeviceId 方法获取设备 ID ,通过控制台或者 OpenAPI 按 终端向应用推送。 

## **第六步:注册鸿蒙PushToken(可选)** 

要使用鸿蒙厂商通道,需要通过 SDK 把鸿蒙的 PushToken 注册到移动推送平台。需要在注册设备成功之后调用。示例代码如 下: 

```arkts
import { aliyunPush } from '@aliyun/push'; import { pushService } from '@kit.PushKit'; import { BusinessError } from '@kit.BasicServicesKit'; pushService.getToken().then((pushToken) => { // ************* 注册 PushToken begin ************* aliyunPush.registerThirdToken(pushToken, (error) => { if (error) { console.error(` 注册 PushToken 失败,错误码 :${error.code} 错误信息 ${error.message}`); return; } console.info(` 注册 PushToken 成功 `); }) // ************* 注册 PushToken end ************* }).catch((error: BusinessError) => { console.error(` 获取 PushToken 失败,错误码 :${error.code} 错误信息 ${error.message}`); }) 
```

。 关于鸿蒙厂商通道,请参考厂商通道 

## **第七步:实现鸿蒙厂商通道的通知扩展消息接收(可 选)** 

如果接入了鸿蒙厂商通道,同时要推送通知扩展消息,需要在接收到通知扩展消息时,调用 SDK 接口解析获取推送数据,进 行下一步操作。 

RemoteNotificationExtensionAbility 接收通知扩展消息的处理代码示例如下: 

```arkts
import { pushCommon, RemoteNotificationExtensionAbility } from '@kit.PushKit'; import { aliyunPush, ExtensionNotification } from '@aliyun/push'; import { hilog } from '@kit.PerformanceAnalysisKit'; import { common } from '@kit.AbilityKit'; 
```

export default class SampleRemoteNotification extends RemoteNotificationExtensionAbility { async onReceiveMessage(remoteNotificationInfo: pushCommon.RemoteNotificationInfo): Promise<pushCommon.RemoteNotificationContent> { // ************* 通知扩展消息处理 begin ************* // 初始化推送参数,用于解析推送数据 aliyunPush.init({ appKey: ' 请填入在准备工作中查询的应用 AppKey', appSecret: ' 请填入在准备工作中查询的应用 AppSecret', context: this.context as common.Context, }) 

// 调用 parseExtensionPushData 解析推送的参数 const notification: ExtensionNotification = await aliyunPush.parseExtensionPushData(remoteNotificationInfo); 

// 这里可以获取通知扩展消息的参数进行业务处理 

// SDK 提供辅助方法 getRemoteNotificationContent 构建返回值 , 传参 EntryAbility 是本次通知点击要打开的 Ability 名 称 const result = aliyunPush.getPushHelper().getRemoteNotificationContent('EntryAbility', notificatio n); return result; // 如果要修改通知的内容,可以返回想要修改的内容, wantAgent 建议还是保留。如果不保留,后续就无法在用户点击时识别推送 的参数,会丢失通知的点击数据 

// return { //   // 省略其它修改的字段, wantAgent 建议还是使用 getRemoteNotificationContent 方法构造的参数。 //   wantAgent: result.wantAgent // } // ************* 通知扩展消息处理 end ************* } } 

### pushService.receiveMessage 接收通知扩展消息的处理代码示例如下: 

```arkts
export default class EntryAbility extends UIAbility { onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void { // ************* 初始化 SDK begin ************* aliyunPush.init({ appKey: ' 请填入在准备工作中查询的应用 AppKey', appSecret: ' 请填入在准备工作中查询的应用 AppSecret', context: this.context, }) // ************* 初始化 SDK end ************* // 省略其它初始化配置方法 // ************* 设置应用在前台时鸿蒙厂商通道的通知扩展消息接收接口 begin ************* pushService.receiveMessage("IM", this, async (data: pushCommon.PushPayload) => { // 解析推送参数 const extensionNotification: ExtensionNotification = await aliyunPush.parseExtensionPushData(data); // 这里根据获取的通知扩展消息参数进行业务处理 }) // ************* 设置应用在前台时鸿蒙厂商通道的通知扩展消息接收接口 end ************* } // 省略其它代码 } 
```

关于 RemoteNotificationExtensionAbility 和 pushService.receiveMessage 的改动请参考通知扩展消息的开发步骤说 明。 

。 关于如何使用阿里云推送平台推送通知扩展消息,请参考通知扩展消息 

## **第八步:发起推送** 

通过控制台的推送通知、推送消息或者 OpenAPI 的推送相关接口,使用按设备推送,即可发起推送, SDK 在接收到推送之 后,会回调第三步:设置推送回调接口中设置的回调接口。 

对于推送的通知, SDK 在接收到之后,会回调 onReceiveNotification 方法,告知应用收到通知。 SDK 创建并发布通知之 后,会回调 onShowNotification 方法,告知应用通知已发布。 

对于推送的消息, SDK 在接收到之后,会回调 onReceiveMessage 方法,告知应用收到消息。 

## **关于合规使用和延迟初始化** 

### SDK 使用的权限如下: 

|权限名称|权限说明|使用目的|权限申请时机|
|---|---|---|---|
|ohos.permission.INTERNET|允许使用Internet网络|在建立推送通道时,用于访问 网络数据|安装应用时,系统自动授权|
|ohos.permission.GET_NET WORK_INFO|允许应用获取数据网络信息|在管理推送通道时,用于监听 网络变化,在网络恢复时,即 时恢复推送通道|安装应用时,系统自动授权|

### 以上权限由系统在安装时自动授权,所以 SDK 并不需要主动向用户申请权限。 

对于通知授权,请参考请求通知授权实现应用请求授权逻辑, SDK 默认不会向用户申请通知授权。 对于 SDK 信息及隐私政策,请参考 SDK 信息。 

在用户同意使用 SDK 及同意通知授权之前,应用需要考虑延迟初始化 SDK ,我们的建议如下: 

第五步:注册设备获取设备 ID 和 第六步:注册鸿蒙 PushToken (可选)可以延迟到用户同意使用 SDK 之后执行。 

其它步骤,包括第二步:初始化 SDK ,仅为设置推送相关变量数据,不需要延迟执行。 

示例代码请参考 SDK 接入完整代码示例。 

## **SDK接入完整代码示例** 

### 为了方便理解 SDK 接入过程中的代码执行顺序,请参考以下代码: 

```arkts
import { AbilityConstant, UIAbility, Want } from '@kit.AbilityKit'; import { window } from '@kit.ArkUI'; import { aliyunPush, Channel, ExtensionNotification, IPushListener, PushDataType, PushMessage, PushNotification, PushNotificationHandler } from '@aliyun/push'; import { pushCommon, pushService } from '@kit.PushKit'; import { hilog } from '@kit.PerformanceAnalysisKit'; 
```

/** * 自定义的推送回调接口实现 */ class MyPushListener implements IPushListener { onReceiveNotification(data: PushNotification | ExtensionNotification): boolean { if (data.type === PushDataType.Notification) { // 处理推送通知 } else if (data.type === PushDataType.ExtensionNotification) { // 处理通知扩展消息 } return false; } onShowNotification(data: PushNotification | ExtensionNotification): void { // 处理通知展示事件 } onReceiveMessage(data: PushMessage): void { // 处理推送消息 } } /** * 自定义推送数据的处理类 */ class MyPushNotificationHandler implements PushNotificationHandler { onClickNotification(data: PushNotification | PushMessage | ExtensionNotification, from: Channel): vo id { // 由用户点击通知拉起的页面,获取推送数据,处理业务逻辑 } noPushData(): void { // 不是由用户点击通知拉的页面 , 或者不是阿里云推送的数据 } } export default class EntryAbility extends UIAbility { onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void { 

// ************* 初始化 SDK begin ************* 

// 初始化 S beg 

aliyunPush.init({ 请填入在准备工作中查询的应用 AppKey', appSecret: ' 请填入在准备工作中查询的应用 AppSecret', 

context: this.context, // ************* 初始化 SDK end ************* 

// ************* 设置推送回调接口 begin ************* aliyunPush.setPushListener(new MyPushListener()); // ************* 设置推送回调接口 end ************* 

// ************* 调用推送通知点击处理接口 begin ************* aliyunPush.handleClickNotification(want, new MyPushNotificationHandler()) // ************* 调用推送通知点击处理接口 end ************* 

这里需要应用获取用户是否已经同意使用 SDK 的标记 

const userAgreed = false; if(userAgreed) { 

用户同意使用再初始化注册推送 

this.registerPush(); 

// ************* 设置应用在前台时鸿蒙厂商通道的通知扩展消息接收接口 begin ************* 

pushService.receiveMessage("IM", this, async (data: pushCommon.PushPayload) => { 解析推送参数 

const extensionNotification: ExtensionNotification = await aliyunPush.parseExtensionPushData(data); // 这里根据获取的通知扩展消息参数进行业务处理 

}) // ************* 设置应用在前台时鸿蒙厂商通道的通知扩展消息接收接口 end ************* } 

- /** * 此方法可以延迟到用户同意使用 SDK 之后再执行 

private async registerPush() { // ************* 注册设备获取设备 ID begin ************* await aliyunPush.register(); 

const deviceId = aliyunPush.getDeviceId(); // ************* 注册设备获取设备 ID end ************* 

```arkts
const pushToken = await pushService.getToken(); // ************* 注册鸿蒙 PushToken begin ************* await aliyunPush.registerThirdToken(pushToken); // ************* 注册鸿蒙 PushToken end ************* } 
```

onNewWant(want: Want, launchParam: AbilityConstant.LaunchParam): void { // ************* 调用推送通知点击处理接口 begin ************* aliyunPush.handleClickNotification(want, new MyPushNotificationHandler()) // ************* 调用推送通知点击处理接口 end ************* } 

- // 省略其它代码 

onDestroy(): void { } 

onWindowStageCreate(windowStage: window.WindowStage): void { // Main window is created, set main page for this ability 

windowStage.loadContent('pages/Index', (err) => { 

```arkts
if (err.code) { return; } }); } onWindowStageDestroy(): void { // Main window is destroyed, release UI related resources } onForeground(): void { // Ability has brought to foreground } onBackground(): void { // Ability has back to background } } 
```

## **后续步骤** 

。 如果要通过别名、标签等方式推送,或者定制通知的样式等功能,可以参考 HarmonyOS SDK API
