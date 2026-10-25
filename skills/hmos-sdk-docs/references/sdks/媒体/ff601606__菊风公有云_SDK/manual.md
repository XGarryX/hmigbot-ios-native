# HarmonyOS Next快速开始

# 准备开发环境

本章将介绍如何将 HarmonyOS Next SDK 集成到您自己创建的项目中。

## 前提条件

-
HarmonyOS  SDK:  HarmonyOS 5.0.0 Release SDK

-
DevEco-Studio:HarmonyOS NEXT Release(V5.0.3.900)及以上

-
有效的菊风开发者账号,菊风官网控制台注册获取账号

-
有效的菊风AppKey ,控制台创建应用获取

-
若应用开启Token鉴权模式,通过您的服务生成有效Token 。未开启Token鉴权,则无需生成。

## 创建 Harmony 项目

参考以下步骤创建一个 Harmony 项目。若已有 Harmony 项目,可以直接查看【集成 SDK】。

-
打开 DevEco-Studio,点击create project。

-
在 Choose Your Ability Template 界面,选择 Application -> Empty Ability,然后点击 Next。

-
在 Configure Your Project 界面,依次填入以下内容:

## ◦

Project name:您的 Harmony 项目名称,如 HelloJuphoon

## ◦

Bundle name:您的项目包的名称,如 io.helloJuphoon

## ◦

Save location:项目的存储路径

## ◦

Compatible SDK:HarmonyOS SDK 兼容版本

## ◦

Module name :项目模块名称

## 集成 SDK

您可以通过以下方式集成 HarmonyOS Next SDK:

### 手动导入 SDK

1.下载 HarmonyOS Next SDK并解压。

2.拷贝 SDK 文件夹内的 JCSDK.har 到您工程目录中的 libs 目录下。

3.为确保能够连接到 so 库,需要在您工程的 oh-package.json5 中添加设置:

```
"dependencies": {
"@juphoon/jcsdk": 'file:./libs/JCSDK.har'
}
```

## 添加项目权限

根据场景需要,在 src/main/module.json5 文件中添加如下行,获取相应的设备权限:

```
"requestPermissions": [
  {
"name" : "ohos.permission.INTERNET",
  },
  {
"name" : "ohos.permission.GET_NETWORK_INFO",
  },
  {
"name" : "ohos.permission.GET_WIFI_INFO",
  },
  {
"name" : "ohos.permission.MODIFY_AUDIO_SETTINGS",
  },
  {
"name" : "ohos.permission.USE_BLUETOOTH",
  },
  {
"name" : "ohos.permission.MICROPHONE",
"reason": "$string:reasonUseMicrophone",
"usedScene": {
"abilities": [
"EntryAbility"
      ],
"when":"always"
    }
  },
  {
"name" : "ohos.permission.CAMERA",
"reason": "$string:reasonUseCamera",
"usedScene": {
"abilities": [
"EntryAbility"
      ],
"when":"always"
    }
  }
],
```

注意:您在 module.json5 中进行权限配置时,请确保您能够获得打开摄像头、音视频录制等相关权

限。

# 登录

本章节将介绍如何初始化 HarmonyOS Next SDK 并登录。

## 初始化

在主线程调用JCClient.create,创建JCClient实例对象。传入获取到的appKey,即可初始化

JCClient。

```
export class JCManagerimplements JCClientCallback {
// JCClient 对象
public client: JCClient | undefined;
// 初始化函数
initialize(context: Context, createParam: CreateParam): boolean {
this.mContext = context
// 登录类想
this.client =
JCClient.create(context, "用户 appKey", this, createParam);
// 获取初始化状态(用来判断初始化状态)
return this.client.getState() == ClientState.STATE_IDLE
    }
// 所有登录接口回调的实现
    ...
}
```

初始化成功后,JCClient.ClientState 状态从 ClientState.STATE_NOT_INIT(未初始化)变为

ClientState.STATE_IDLE(未登录)。

## 发起登录

SDK 初始化之后,即可进行登录的集成。登录接口调用流程如下所示:

先创建LoginParam实例以调整登录参数。后调用login,发起登录:

```
let mLoginParam = newLoginParam();
let logined = this.client?.login("userID", "password", this.mLoginParam);
```

1.userID 用户名不能为空,可由英文、数字和+、-、_、.

组成(特殊字符不能作为第一个字符),大小写不敏感,长度不能超过64 个字符。

2.password 密码,不能为空,长度不能超过 128 字符。

3.调用该接口返回 true 时只代表调用接口成功,并不代表登录成功。登录的结果会通过 onLogin 回

调上报。

调用接口成功后,首先会触发登录状态改变回调onClientStateChange。您可以通过重写

onClientStateChange 执行逻辑操作。

```
onClientStateChange(state: number, oldState: number): void {
if (state == ClientState.STATE_IDLE) { // 未登录...
   } elseif (state == ClientState.STATE_LOGINING) { // 正在登录...
   } elseif (state == ClientState.STATE_LOGINED) { // 登录成功...
   } elseif (state == ClientState.STATE_LOGOUTING) { // 登出中...
   }
}
```

之后触发onLogin回调。您可以通过重写onLogin执行逻辑操作。

```
onLogin(result: boolean, reason: number): void {
if (result) {// 登录成功
     ...
 }
if (reason == ClientReason.REASON_AUTH) {// 账号密码错误
     ...
 }
}
```

登录成功之后,SDK 会自动保持与服务器的连接状态,直到用户主动调用登出接口,或者因为帐号在

其他设备登录导致该设备登出。登录成功/失败原因参考 ClientReason。

## 登出

登出接口调用流程如下所示:

调用logout可以发起登出。

```
onLogout(reason: number): void {
if (reason == ClientReason.REASON_SERVER_LOGOUT) {// 强制登出...
  }
}
```

更多登出原因参考: ClientReason。

# 实现一对一音视频通话

本章将介绍如何实现多个APP 应用间的视频通话,视频通话的 API 调用时序见下图:

## 获取设备权限

使用 reqPermissionsFromUser 方法,获取设备的麦克风和相机使用权限。

```
import abilityAccessCtrl, { Permissions } from '@ohos.abilityAccessCtrl';
const permissions: Array<Permissions> = ['ohos.permission.MICROPHONE',
'ohos.permission.CAMERA'];
async aboutToAppear() {
    ...
// 获取设备权限
reqPermissionsFromUser(permissions,this.context)
}
```

/*申请权限*/

```
static reqPermissionsFromUser(permissions: Array<Permissions>, context:
common.UIAbilityContext | undefined): void {
let atManager: abilityAccessCtrl.AtManager =
abilityAccessCtrl.createAtManager();
// requestPermissionsFromUser会判断权限的授权状态来决定是否唤起弹窗
  atManager.requestPermissionsFromUser(context, permissions).then((data) => {
let grantStatus: Array<number> = data.authResults;
let length: number = grantStatus.length;
for (let i = 0; i < length; i++) {
if (grantStatus[i] === 0) {
// 用户授权,可以继续访问目标操作
console.log('授权成功');
      } else {
```

// 用户拒绝授权,提示用户必须授权才能访问当前页面的功能,并引导用户到系统设置中

打开相应的权限

```
console.log('授权失败');
return;
      }
    }
// 授权成功
  }).catch((err: BusinessError) => {
console.error(`Failed to request permissions from user. Code is
${err.code}, message is ${err.message}`);
  })
}
```

## 初始化

调用JCMediaDevice.create和JCCall.create以初始化实现一对一通话需要的模块。

```
export class JCManagerimplements JCCallCallback, JCMediaDeviceCallback {
// 声明对象
public call: JCCall | undefined;
public mediaDevice: JCMediaDevice | undefined;
// 初始化函数
initialize(context: Context, createParam: CreateParam): boolean {
//1. 媒体类
this.mediaDevice = JCMediaDevice.create(this.client, this);
//2. 通话类
this.call = JCCall.create(this.client, this.mediaDevice, this);
    }
// 所有一对一接口回调的实现
    ...
// 所有媒体接口回调的实现
    ...
}
```

## 拨打通话

调用call发起语音通话,需要填写的参数有:

-
userID填写对方的用户ID。

-
video选择是否为视频通话, true 表示拨打视频通话, false 表示拨打语音通话。

-
callParam通话参数对象,此参数可为空,详细定义见:CallParam

```
let callParam = new CallParam("extraParam", "ticket");
this.call?.call("userId", isVideo, callParam)
```

拨打通话后,主叫和被叫均会收到新增通话的回调onCallItemAdd,此时通话状态变为

CallState.STATE_PENDING 。您可以通过重写onCallItemAdd执行逻辑操作。

示例代码

```
// 1. 发起语音通话
this.call("userID", isVideo , newJCCall.CallParam("extraParam", "ticket"));
// 2. 重写回调
onCallItemAdd(item: JCCallItem): void {// 业务逻辑
if (item.getDirection() == CallDirection.DIRECTION_IN) {// 如果是被叫...
    } else {// 如果是主叫...
    }
}
```

如果主叫想取消通话,可以直接转到挂断通话部分。调用挂断接口后,通话状态变为

CallState.STATE_CANCEL。

## 创建本端视频画面

1.调用 startCamera 开启摄像头,获取本端采集的摄像头id。

```
@StatecameraId: string | undefined = undefined
startCamera(){
if (!this.mediaDevice.isCameraOpen()) {
this.mediaDevice.startCamera()
 }
this.cameraId = this.mediaDevice.getCamera()?.cameraId
}
```

2.JCSDK提供自定义组件JCVideoComponent用于视频画面的渲染。JCVideoComponent在加载完

成时,根据传入的streamId进行渲染。当需要渲染本地采集的视频流时,需要传入本端采集的摄像

头id。

```
build() {
Column(){
JCVideoComponent({
streamId: this.cameraId,
mediaDevice: this.mediaDevice
   })
  .backgroundColor(Color.Black)
  .align(Alignment.Center)
  }
}
```

## 应答通话

1.被叫收到onCallItemAdd回调,在回调中调用JCCallItem中的getVideo 方法获取video属性来

判断是视频呼入还是语音呼入,从而做出相应的处理。

```
onCallItemAdd(item: JCCallItem): void {
// 1. 如果是语音呼入且在振铃中
if (item.getDirection() == CallDirection.DIRECTION_IN &&
!item.getVideo()) {
// 2. 做出相应的处理,如在界面上显示“振铃中”
        ...
    }
}
```

2.调用answer接听通话。

```
this.call?.answer(item, false);
1
```

通话接听后,通话状态变为 CallState.STATE_CONNECTING。

如果被叫要在此时拒绝通话,请调用挂断通话的接口。这种情况下调用挂断后,通话状态变为

CallState.STATE_CANCELED。

## 创建远端视频画面

1.当需要渲染远端画面的视频流时,一对一通话通过JCCallItem.getRenderId获取远端视频流id

```
@StateremoteStreamId: string | undefined = undefined
// 1. 获取当前活跃通话
letitem = this.call?.getActiveCallItem();
if (item != null) {
// 2. 获取远端视频流id
this.remoteStreamId = this.call?.getRenderId();
}
```

2.JCSDK提供自定义组件JCVideoComponent用于视频画面的渲染。JCVideoComponent在加载完

成时,根据传入的视频流renderId进行渲染。

```
build() {
Column(){
JCVideoComponent({
streamId: this.remoteStreamId,
mediaDevice: this.mediaDevice
   })
  .backgroundColor(Color.Black)
  .align(Alignment.Center)
  }
}
```

## 挂断通话

主叫或者被叫均可以挂断通话

1.调用getActiveCallItem获取当前活跃的通话对象:

```
this.call?.getActiveCallItem()
1
```

2.调用term挂断当前活跃通话:

```
this.call?.term(item, reason, description);
1
```

示例代码

```
// 1. 获取当前活跃通话
letitem = this.call?.getActiveCallItem();
if (item != null) {
// 2. 挂断当前活跃通话
this.call?.term(item, 0, "reason");
}
```

# 实现多方音视频通话

本章将介绍如何实现多方音视频通话,多方音视频通话的 API 调用时序见下图:

## 获取设备权限

使用 reqPermissionsFromUser 方法,获取设备的麦克风和相机使用权限。

```
import abilityAccessCtrl, { Permissions } from '@ohos.abilityAccessCtrl';
const permissions: Array<Permissions> = ['ohos.permission.MICROPHONE',
'ohos.permission.CAMERA'];
async aboutToAppear() {
    ...
// 获取设备权限
reqPermissionsFromUser(permissions,this.context)
}
```

/*申请权限*/

```
static reqPermissionsFromUser(permissions: Array<Permissions>, context:
common.UIAbilityContext | undefined): void {
let atManager: abilityAccessCtrl.AtManager =
abilityAccessCtrl.createAtManager();
// requestPermissionsFromUser会判断权限的授权状态来决定是否唤起弹窗
  atManager.requestPermissionsFromUser(context, permissions).then((data) => {
let grantStatus: Array<number> = data.authResults;
let length: number = grantStatus.length;
for (let i = 0; i < length; i++) {
if (grantStatus[i] === 0) {
// 用户授权,可以继续访问目标操作
console.log('授权成功');
      } else {
```

// 用户拒绝授权,提示用户必须授权才能访问当前页面的功能,并引导用户到系统设置中

打开相应的权限

```
console.log('授权失败');
return;
      }
    }
// 授权成功
  }).catch((err: BusinessError) => {
console.error(`Failed to request permissions from user. Code is
${err.code}, message is ${err.message}`);
  })
}
```

## 初始化

调用JCMediaDevice.create和JCMediaChannel.create以初始化实现多方通话需要的模块。

```
export class JCManagerimplements JCMediaChannelCallback,
JCMediaDeviceCallback {
// 声明对象
public mediaDevice: JCMediaDevice | undefined;
public mediaChannel: JCMediaChannel | undefined;
// 初始化函数
initialize(context: Context, createParam: CreateParam): boolean {
//1. 媒体类
this.mediaDevice = JCMediaDevice.create(this.client, this);
//2. 媒体通道类
this.mediaChannel = JCMediaChannel.create(this.client,
this.mediaDevice, this);
      ...
    }
// 所有多方接口回调的实现
    ...
// 所有媒体接口回调的实现
    ...
}
```

## 加入频道

1.调用enableUploadAudioStream 开启音频流。

```
this.mediaChannel?.enableUploadAudioStream(true);
1
```

2.调用join,创建并加入频道。需要传入channelIdOrUri和JoinParam。

-
channelId:媒体频道标识。

-
JoinParam:加入参数,没有则填 NULL。

```
this.mediaChannel?.join("222", null);
1
```

3.加入频道后自身会收到onJoin回调。其他成员会收到onParticipantJoin回调。

```
onJoin(result: boolean, reason: number, channelId: string): void {
if (result) {
// 加入频道成功
  } else {
// 加入频道失败
  }
}
onParticipantJoin(participant: JCMediaChannelParticipant): void {
}
```

## 创建本端视频画面

1.调用 startCamera 开启摄像头。入会前可通过JCMediaDevice.getCamera()?.cameraId 获取本端

采集的摄像头id。

```
@StatecameraId: string | undefined = undefined
startCamera(){
if (!this.mediaDevice.isCameraOpen()) {
JCManager.getInstance().mediaDevice?.startCamera().then((result) => {
if (result) {
//摄像头开启成功
this.cameraId = this.mediaDevice.getCamera()?.cameraId
    }
  })
 }
}
```

2.JCSDK提供自定义组件JCVideoComponent用于视频画面的渲染。JCVideoComponent在加载完

成时,根据传入的streamId进行渲染。当需要渲染本地采集的视频流时,需要传入本端采集的摄像

头id。

```
build() {
Column(){
JCVideoComponent({
streamId: this.cameraId,
mediaDevice: this.mediaDevice
   })
  .backgroundColor(Color.Black)
  .align(Alignment.Center)
  }
}
```

## 创建成员的视频画面

1.入会成功后,当需要渲染成员画面的视频流时,多方通话通过

JCMediaChannelParticipant.startVideo订阅其他成员视频流,通过

JCMediaChannelParticipant.getStreamId获取其他成员的视频流id。本端视频流id也可通过本端

多方成员对象 JCMediaChannelParticipant.getStreamId获取。

```
@StateremoteStreamId: string | undefined = undefined
@StatepictureSize: PictureSize = PictureSize.PICTURESIZE_MIN
@StaterenderType: RenderType = RenderType.RENDER_FULL_SCREEN
// 1. 获取当前多方通话所有的成员对象
let participants = mediaChannel?.getParticipants();
// 2. 获取远端视频流id
this.participantArray.forEach((participant: JCMediaChannelParticipant,
index?: number) => {
//3.筛选指定的成员对象
if (!participant.isSelf() && participant.isVideo()) {
//4.订阅成员视频流
    participant?.startVideo(this.renderType, this.pictureSize);
//5.获取成员的视频流id
this.remoteStreamId = participant.getStreamId();
  }
});
```

2.JCSDK提供自定义组件JCVideoComponent用于视频画面的渲染。JCVideoComponent在加载完

成时,根据传入的视频流renderId进行渲染。

```
build() {
Column(){
JCVideoComponent({
streamId: this.remoteStreamId,
mediaDevice: this.mediaDevice
    })
      .backgroundColor(Color.Black)
      .align(Alignment.Center)
  }
}
```

## 离开频道

调用leave方法可以离开当前频道。

```
this.mediaChannel?.leave()
1
```

离开频道后,自身收到onLeave回调,其他成员同时收到onParticipantLeft回调。

## 解散频道

如果想解散频道,可以调用下面的接口,此时所有成员都将被退出。

```
// 结束频道
this.mediaChannel?.stop()
```

解散频道后,发起结束的成员收到onStop回调,其他成员同时收到onLeave回调。解散失败原因枚

举值请参考MediaChannelReason。

```
onStop(result: boolean, reason: number): void {
}
```
