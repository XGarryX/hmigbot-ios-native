实现音视频互动 | 文档中心 | 声网 

2025/10/15 10:57 

文档中心 / 实时互动 / 快速开始 / 实现音视频互动 

# **实现音视频互动** 

 更新时间2025/06/27 16:17:14 

复制页面 

- 本文介绍如何集成声网实时互动 SDK,通过少量代码从 0 开始实现一个简单的实时互动 App,适用于互动直播和视频通话场景。 首先,你需要了解以下有关音视频实时互动的基础概念: 

   - 声网实时互动 SDK:由声网开发的、帮助开发者在 App 中实现实时音视频互动的 SDK。 

   - 频道:用于传输数据的通道,在同一个频道内的用户可以进行实时互动。 

   - 主播:可以在频道内 **发布** 音视频,同时也可以 **订阅** 其他主播发布的音视频。 

   - 观众:可以在频道内 **订阅** 音视频,不具备 **发布** 音视频权限。 

#### 更多概念详见关键概念。 

#### 下图展示在 App 中实现音视频互动的基本工作流程: 

声网视频 声网视频
[
SDK SDK
主播 观众
A
1.加入频道 1.加入频道
2.发布流、 2.订阅流
订阅流
- TM
声网SD RTN M

1. 所有用户调用 `joinChannel` 方法加入频道,并根据需要设置用户⻆色: 互动直播:如果用户需要在频道中发流,则设为主播;如果用户只需要收流,则设为观众。 

第1/15页 

https://doc.shengwang.cn/doc/rtc/harmonyos/get-started/quick-start 

实现音视频互动 | 文档中心 | 声网 

2025/10/15 10:57 

视频通话:将所有的用户⻆色都为主播。 

2. 加入频道后,不同⻆色的用户具备不同的行为: 

   - 所有用户默认都可以接收频道中的音视频流。 

主播可以在频道内发布音视频流。 

观众如果需要发流,可在频道内调用 `setClientRole` 方法修改用户⻆色,使其具备发流权限。 

## **前提条件** 

在实现功能以前,请按照以下要求准备开发环境: 

DevEco Studio NEXT Beta1 及以上版本。 API Version 11 的 HarmonyOS NEXT SDK 及以上版本。 API Version 11 的 HarmonyOS NEXT 2.0.0.59 操作系统及以上版本。 华为开发者账号。可在华为开发者联盟 注册账号。 

两台支持 HarmonyOS 的设备,建议使用 Mate 60 Pro 及更高性能的设备。 可以访问互联网的计算机。如果你的网络环境部署了防火墙,参考应对防火墙限制以正常使用声网服务。 一个有效的声网账号以及声网项目。请参考开通服务从声网控制台获得 App ID 和临时 Token。 

#### **注意** 

临时 Token 的有效期是 24 小时。Token 过期会导致加入频道失败。 

## **创建项目** 

本小节介绍如何创建项目并为项目添加体验实时互动所需的权限。 

1. 参考创建和运行 Hello World ,创建一个新工程。 

2. 打开 **entry/src/main** 中的 `module.json5` 文件,在 `module` 模块中声明网络和设备权限: 

JSON `1 "requestPermissions": [ 2 //` 访问互联网的权限 `3 { 4 "name": "ohos.permission.INTERNET", 5 "reason": "$string:Internet_reason",` 

第2/15页 

https://doc.shengwang.cn/doc/rtc/harmonyos/get-started/quick-start 

实现音视频互动 | 文档中心 | 声网 

2025/10/15 10:57 

`6 "usedScene": { 7 "abilities": [ 8 "EntryAbility" 9 ], 10 "when": "always" //` 始终需要该权限 `11 } 12 }, 13 //` 访问麦克风的权限 `14 { 15 "name": "ohos.permission.MICROPHONE", 16 "reason": "$string:Audio_reason", 17 "usedScene": { 18 "abilities": [ 19 "EntryAbility" 20 ],`  展开全部 35 行 

3. 打开 **src/main/resources/base/element** 中的 `string.json` 文件,添加如下代码,定义所需要的权限。 

JSON 

```
1{
2  "name":"Internet_reason",
3  "value":"access internet"
4},
5{
6  "name":"Audio_reason",
7  "value":"access audio"
8},
9{
10  "name":"Video_reason",
11  "value":"access video"
12}
```

## **集成 SDK** 

1. 在下载页面下载最新版本的鸿蒙视频 SDK,并在本地解压。 

2. 打开解压文件,将 `AgoraRtcSdk.har` 文件复制到项目 **entry -> libs** 目录下(libs 文件夹需要手动创建)。 

3. 在 **entry** 下的 `oh-pacakge.json5` 文件中添加如下依赖,然后点击 **Sync** 开始同步。 

第3/15页 

https://doc.shengwang.cn/doc/rtc/harmonyos/get-started/quick-start 

实现音视频互动 | 文档中心 | 声网 

2025/10/15 10:57 

JSON

```
1"dependencies": {
2  "@shengwang/rtc-full":"file:./libs/AgoraRtcSdk.har"
3}
```

## **实现步骤** 

本小节介绍如何实现一个实时音视频互动 App。你可以先复制完整的示例代码到你的项目中,快速体验实时音视频互动的基础功能, 再按照实现步骤了解核心 API 调用。 

下图展示了使用声网 RTC SDK 实现音视频互动的基本流程: 

App:主播 RTC SDK App:观众
初始化引擎
1 创建并初始化引擎
2 创建并初始化引擎
设置视频属性
3 启用视频模块
4 启用视频模块
5 初始化本地视图
6 开启本地视频预览
加入频道
7 加入频道并设置用户角色为主播
8 加入频道并设置用户角色为观众
9 通知主播端已加入频道
10 通知观众端已加入频道
设置远端视图
11 初始化远端视图
开始音视频互动

第4/15页 

https://doc.shengwang.cn/doc/rtc/harmonyos/get-started/quick-start 

实现音视频互动 | 文档中心 | 声网 

2025/10/15 10:57 

结束音视频互动
12 离开频道
13 通知主播端已离开频道
14 通知主播端已离开频道
15 离开频道
16 通知观众端已离开频道
17 销毁引擎
18 销毁引擎
App:主播 RTC SDK App:观众

下面列出了一段实现实时互动基本流程的完整代码以供参考。复制以下代码到 `pages/Index.ets` 文件中替换原有内容,即可快速 体验实时互动基础功能。 

#### **信息** 

在 `appId` 、 `token` 和 `channelName` 字段中传入你在控制台获取到的 App ID、临时 Token,以及生成临时 Token 时填入的频道 名。 

#### 实现实时音视频互动示例代码 

ArkTS

```
1import {
2    ChannelMediaOptions,
3    Constants,
4    RtcEngine,
5    RtcEngineConfig,
6    RtcStats,
7    VideoCanvas,
8} from"AgoraRtcSdk"
9import { common } from'@kit.AbilityKit';
10
11@Entry
12@Component
```

第5/15页 

https://doc.shengwang.cn/doc/rtc/harmonyos/get-started/quick-start 

实现音视频互动 | 文档中心 | 声网 

2025/10/15 10:57 

`13 struct Index { 14` _`private`_ `rtcEngine: RtcEngine |` _`null`_ `=` _`null`_ `; 15 @State isJoined: boolean = false; 16` _`private`_ `channel = "hmostest"; 17 18 build() { 19 Flex({ direction: FlexDirection.Column }) { 20 Stack({ alignContent: Alignment.TopStart }) {`  展开全部 129 行 

### **处理权限请求** 

#### 本小节介绍如何获取设备的摄像头、录音等权限。 

1. 在项目中打开 **entryablility** -> `EntryAbility.ets` 文件,在 `EntryAbility` 之前添加权限申请,示例代码如下所示。 启动应用程序时,检查是否已在 App 中授予了实现实时互动所需的权限。 

##### ArkTS 

`1` _`const`_ `permissions: Array<Permissions> = ['ohos.permission.INTERNET','ohos.permission.MICROPHONE',"ohos.permission.CAMERA"]; 2 3 4` _`async function`_ `checkAccessToken(permission: Permissions): Promise<abilityAccessCtrl.GrantStatus> { 5` _`let`_ `atManager = abilityAccessCtrl.createAtManager(); 6` _`let`_ `grantStatus: abilityAccessCtrl.GrantStatus = abilityAccessCtrl.GrantStatus.PERMISSION_DENIED; 7 //` 获取应用程序的 `accessTokenID 8` _`let`_ `tokenId: number = 0; 9` _`try`_ `{ 10` _`let`_ `bundleInfo: bundleManager.BundleInfo =` _`await`_ `bundleManager.getBundleInfoForSelf(bundleManager.BundleFlag.GET_BUNDLE_INFO_WITH_APPLICATION); 11` _`let`_ `appInfo: bundleManager.ApplicationInfo = bundleInfo.appInfo; 12 tokenId = appInfo.accessTokenId; 13 }` _`catch`_ `(error) { 14` _`let`_ `err: BusinessError = error` _`as`_ `BusinessError; 15 console.error(`Failed to get bundle info for self. Code is ${err.code}, message is ${err.message}`);` 

第6/15页 

https://doc.shengwang.cn/doc/rtc/harmonyos/get-started/quick-start 

实现音视频互动 | 文档中心 | 声网 

2025/10/15 10:57 

`16 } 17 //` 校验 `App` 是否被授予权限 `18` _`try`_ `{ 19 grantStatus =` _`await`_ `atManager.checkAccessToken(tokenId, permission); 20 }` _`catch`_ `(error) { 21` _`let`_ `err: BusinessError = error` _`as`_ `BusinessError; 22 console.error(`Failed to check access token. Code is ${err.code}, message is ${err.message}`); 23 } 24` _`return`_ `grantStatus; 25 } 26 27` _`export default class`_ `EntryAbility` _`extends`_ `UIAbility { 28 onCreate(want: Want, launchParam: AbilityConstant.LaunchParam) { 29 hilog.info(0x0000, 'testTag', '%{public}s', 'Ability onCreate'); 30` _`let`_ `context =` _`this`_ `.context; 31` _`let`_ `atManager = abilityAccessCtrl.createAtManager(); 32 // requestPermissionsFromUser` 会判断权限的授权状态来决定是否唤起弹窗 `33` _`for`_ `(` _`let`_ `i=0;i<permissions.length;i++) { 34` _`let`_ `permission: Permissions = permissions[i] 35` _`let`_ `granted : boolean = false; 36` _`let`_ `toGrantedPerm: Array<Permissions> =` _`new`_ `Array<Permissions>(); 37 toGrantedPerm.push(permission) 38 checkAccessToken(permission).then((value)=>{ 39` _`if`_ `(value == abilityAccessCtrl.GrantStatus.PERMISSION_GRANTED){ 40 granted = true; 41 hilog.info(0x0000, 'testTag', '%{public}s', 'Permission granted'); 42 }` _`else`_ `{ 43 atManager.requestPermissionsFromUser(context, toGrantedPerm).then((data) => { 44` _`let`_ `grantStatus: Array<number> = data.authResults; 45` _`let`_ `length: number = grantStatus.length; 46` _`for`_ `(` _`let`_ `i = 0; i < length; i++) { 47` _`if`_ `(grantStatus[i] === 0) { 48 //` 用户授权,可以继续访问目标操作 `49 }` _`else`_ `{ 50 //` 用户拒绝授权,提示用户必须授权才能访问当前页面的功能,并引导用户到系统设置中打开相应的权限 `51 hilog.info(0x0000, 'testTag', '%{public}s', 'Permission denied'); 52` _`return`_ `; 53 } 54 } 55 //` 授权成功 `56 }).catch((err: BusinessError) => { 57 hilog.info(0x0000, 'testTag', '%{public}s',`Failed to request permissions from user. Code is ${err.code}, message is ${err.message}`);` 

第7/15页 

https://doc.shengwang.cn/doc/rtc/harmonyos/get-started/quick-start 

实现音视频互动 | 文档中心 | 声网 

2025/10/15 10:57 

58           })
59         }
60       })
61     }
62   }
63
64 }
  折叠 44 行

### **导入声网组件** 

打开 `src/main/ets/pages/Index.ets` 文件,导入如下所需的声网 SDK 组件。 

ArkTS

```
1import {
2    ChannelMediaOptions,
3    Constants,
4    RtcEngine,
5    RtcEngineConfig,
6    RtcStats,
7    VideoCanvas,
8} from"@shengwang/rtc-full"
```

### **添加视频渲染组件** 

在 `Index.ets` 文件中添加视频渲染组件 `XComponent` 。 

ArkTS 

```
1@Entry
2@Component
3struct Index {
4@State message:string='Hello World';
5
6build() {
7Row() {
8Column() {
9XComponent({
```

第8/15页 

https://doc.shengwang.cn/doc/rtc/harmonyos/get-started/quick-start 

实现音视频互动 | 文档中心 | 声网 

2025/10/15 10:57 

`10 // id` 必须在当前页面是唯一的 `11 id: 'local', 12 // type` 必须设置为 `surface 13 type: 'surface', 14 // libraryname` 必须设置为 `Constants.AGORA_LIB_NAME 15 libraryname: Constants.AGORA_LIB_NAME, 16 }) 17 .width('100%') 18 .height('100%') 19 .align(Alignment.TopStart) 20 XComponent({ 21 id: 'remote', 22 type: 'surface', 23 libraryname: Constants.AGORA_LIB_NAME, 24 }) 25 .width('100%') 26 .height('50%') 27 .margin({ bottom: 10 }) 28 29 Text(` _`this`_ `.message) 30 .fontSize(50) 31 .fontWeight(FontWeight.Bold) 32 } 33 .width('100%') 34 } 35 .height('100%') 36 } 37 }`  折叠 17 行 

### **初始化引擎** 

调用 `create` 方法初始化 `RtcEngine` 。 

#### **注意** 

在初始化 SDK 前,需确保终端用户已经充分了解并同意相关的隐私政策。 

ArkTS 

第9/15页 

https://doc.shengwang.cn/doc/rtc/harmonyos/get-started/quick-start 

实现音视频互动 | 文档中心 | 声网 

2025/10/15 10:57 

`1` _`let`_ `config:RtcEngineConfig =` _`new`_ `RtcEngineConfig(); 2` _`let`_ `context = getContext(` _`this`_ `)` _`as`_ `common.UIAbilityContext; 3 config.mContext = context; 4 //` 在这里输入你在声网控制台中获取的 `App ID 5 config.mAppId = "<#Your App ID#>"; 6 config.mEventHandler = {}; 7 8 //` 创建并初始化 `RtcEngine 9` _`this`_ `.rtcEngine = RtcEngine.create(config);` 

### **启用视频模块** 

#### 按照以下步骤启用视频模块: 

1. 调用 `enableVideo` 方法,启用视频模块。 

2. 调用 `setupLocalVideo` 方法初始化本地视图,同时设置本地的视频显示属性。 

3. 调用 `startPreview` 方法,开启本地视频预览。 

##### ArkTS 

|`1` `2` `3`|_`this`_`.rtcEngine.enableVideo();` `//`设置本地视图|
|---|---|
|`4`|`// local`为用于渲染本地图像的`XComponent`的`ID`|
|`5`|_`let`_`canvas: VideoCanvas= `_`new`_ `VideoCanvas("local");`|
|`6`|`canvas.uid= 0;`|
|`7`|`canvas.renderMode= VideoCanvas.RENDER_MODE_HIDDEN;`|
|`8`|`canvas.mirrorMode= VideoCanvas.VIDEO_MIRROR_MODE_ENABLED;`|
|`9`|_`this`_`.rtcEngine.setupLocalVideo(canvas);`|
|`10`|_`this`_`.rtcEngine.startPreview();`|

### **加入频道并发布音视频流** 

- 调用 `joinChannelWithOptions` 加入频道。在 `options` 中进行如下配置: 

   - 设置频道场景为 `BROADCASTING` (直播场景) 并设置用户⻆色设置为 `BROADCASTER` (主播) 或 `AUDIENCE` (观众)。 

   - 将 `publishMicrophoneTrack` 和 `publishCameraTrack` 设置为 `true` ,发布麦克风采集的音频和摄像头采集的视频。 

   - 将 `autoSubscribeAudio` 和 `autoSubscribeVideo` 设置为 `true` ,自动订阅所有音视频流。 

第10/15页 

https://doc.shengwang.cn/doc/rtc/harmonyos/get-started/quick-start 

实现音视频互动 | 文档中心 | 声网 

2025/10/15 10:57 

##### ArkTS 

`1` _`let`_ `option:ChannelMediaOptions  =` _`new`_ `ChannelMediaOptions(); 2 //` 自动订阅所有音频流 `3 option.autoSubscribeAudio = true; 4 //` 自动订阅所有视频流 `5 option.autoSubscribeVideo = true; 6 //` 发布摄像头采集的视频 `7 option.publishCameraTrack = true; 8 //` 发布麦克风采集的音频 `9 option.publishMicrophoneTrack = true; 10 //` 设置频道场景为直播 `11 option.channelProfile = Constants.ChannelProfile.LIVE_BROADCASTING; 12 //` 设置用户⻆色为主播;如果要将用户⻆色设置为观众,保持默认值即可 `13 option.clientRoleType = Constants.ClientRole.BROADCASTER; 14 //` 使用临时 `Token` 加入频道,在这里传入你的项目的 `Token` 和频道名 `15 // uid` 为 `0` ,表示由服务器分配 `uid` ,分配的 `uid` 将通过 `onJoinChannelSuccess` 回调返回 `16` _`this`_ `.rtcEngine.joinChannelWithOptions(<#Your Token#>, <#Your Channel Name#>, 0,option);` 

### **设置远端视图** 

调用 `setupRemoteVideo` 方法初始化远端用户视图,同时设置远端用户的视图在本地显示属性。你可以通过 `onUserJoined` 回调 获取远端用户的 `uid` 。 

##### ArkTS 

- `config.mEventHandler.onUserJoined = (uid: number, collapse: number) => { 2 //` 设置远端渲染 

- `// remote` 为用于渲染远端图像的 `XComponent` 的 `ID 4` _`let`_ `canvas:VideoCanvas =` _`new`_ `VideoCanvas('remote'); 5 canvas.uid = uid; 6` _`this`_ `.rtcEngine!.setupRemoteVideo(canvas); 7 };` 

### **实现常用回调** 

根据使用场景,定义必要的回调。以下示例代码展示如何实现 `onJoinChannelSuccess` 和 `onUserOffline` 回调。 

第11/15页 

https://doc.shengwang.cn/doc/rtc/harmonyos/get-started/quick-start 

实现音视频互动 | 文档中心 | 声网 

2025/10/15 10:57 

##### ArkTS 

```
1config.mEventHandler.onJoinChannelSuccess= (cid:string, uid:number, elapsed:number) => {
2console.info("mEventHandler.onJoinChannelSuccess: "+ cid +" , "+ uid);
3};
4
5config.mEventHandler.onUserOffline= (uid:number, reason:number) => {
6console.info("mEventHandler.onUserOffline: "+ uid +" , "+ reason);
7};
```

### **开始音视频互动** 

- 在 `onClick` 中调用一系列方法加载界面布局、检查 App 是否获取实时互动所需权限,并加入频道开始音视频互动。 

ArkTS 

```
1Button("Join")
2.enabled(!this.isJoined)
3.fontSize(20)
4.width("40%")
5.margin({ left:"5%", right:"5%" })
6.align(Alignment.Center)
7.onClick(() => {
8this.initEngineAndJoinChannel();
9})
```

### **结束音视频互动** 

#### 按照以下步骤结束音视频互动: 

1. 调用 `stopPreview` 停止视频预览。 

2. 调用 `leaveChannel` 离开当前频道,释放所有会话相关的资源。 

3. 调用 `destroy` 销毁引擎,并释放声网 SDK 中使用的所有资源。 

#### **注意** 

- 调用 `destroy` 后,你将无法再使用 SDK 的所有方法和回调。如需再次使用实时音视频互动功能,你必须重新创建一个新的引 

- 擎。详见初始化引擎。 

- 该方法为同步调用。需要等待引擎资源释放后才能执行其他操作,因此建议在子线程中调用该方法,避免主线程阻塞。 

第12/15页 

https://doc.shengwang.cn/doc/rtc/harmonyos/get-started/quick-start 

实现音视频互动 | 文档中心 | 声网 

2025/10/15 10:57 

##### ArkTS 

```
1this.rtcEngine!.stopPreview();
2this.rtcEngine!.leaveChannel();
3RtcEngine.destroy();
4this.rtcEngine =null;
```

## **调试 App** 

#### 按照以下步骤测试直播 App: 

1. 开启鸿蒙 NEXT 设备的开发者选项,打开 USB 调试,通过 USB 连接线将鸿蒙 NEXT 设备接入电脑。 

2. 在 DevEcho Studio 中,点击 **Sync and Refresh Project** 进行同步。 

3. 待同步成功后,点击 **Run 'app'** 开始编译。片刻后,App 便会安装到你的鸿蒙 NEXT 设备上。 

4. 启动 App,授予录音和摄像头权限,如果你将用户⻆色设置为主播,便会在本地视图中看到自己。 

5. 使用第二台鸿蒙 NEXT 设备,重复以上步骤,在该设备上安装 App、打开 App 加入频道,观察测试结果: 如果两台设备均作为主播加入频道,则可以看到对方并且听到对方的声音。 

   - 如果两台设备分别作为主播和观众加入,则主播可以在本地视频窗口看到自己;观众可以在远端视频窗口看到主播、并听到 主播的声音。 

第13/15页 

https://doc.shengwang.cn/doc/rtc/harmonyos/get-started/quick-start 

实现音视频互动 | 文档中心 | 声网 

2025/10/15 10:57 

## **后续步骤** 

在完成音视频互动后,你可以阅读以下文档进一步了解: 

- 本文的示例使用了临时 Token 加入频道。在测试或生产环境中,为保证通信安全,声网推荐从服务器中获取 Token,详情请参 考使用 Token 鉴权。 

- 如果你想要实现极速直播场景,可以在实时音视频互动的基础上,通过修改观众端的延时级别为低延时 ( `LOW_LATENCY` ) 实现。 详见实现极速直播。 

HarmonyOS 

## **参考信息** 

### **示例项目** 

- 声网提供了开源的实时音视频互动示例项目供你参考,你可以前往下载或查看其中的源代码。 

**JoinVideoChannel JoinVideoChannel** 

第14/15页 

https://doc.shengwang.cn/doc/rtc/harmonyos/get-started/quick-start 

实现音视频互动 | 文档中心 | 声网 

2025/10/15 10:57 

**文 档 反 馈** 

### **常见问题** 

直播场景下,如何监听远端观众⻆色用户加入/离开频道的事件? 如何处理视频黑屏问题? 为什么我无法打开摄像头? 如何处理频道相关常见问题? 如何设置日志文件? 为什么部分鸿蒙版本 App 锁屏或切后台音视频采集无效? 

### **相关文档** 

错误码 频道连接状态管理 

> 文档内容对你是否有帮助?   有帮助   没帮助 

隐私政策 服务条款 可接受的使用政策 安全合规 沪公网安备31011002006829号 沪ICP备2024090791号-1 上海声网科技有限公司 

第15/15页 

https://doc.shengwang.cn/doc/rtc/harmonyos/get-started/quick-start
