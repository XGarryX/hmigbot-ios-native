实现纯语音互动 | 文档中心 | 声网 

2025/10/15 10:58 

文档中心 / 实时互动 / 基础功能 / 实现纯语音互动 

# **实现纯语音互动** 

 更新时间2025/06/27 16:17:14 

复制页面

- 本文介绍如何集成声网实时互动 SDK,通过少量代码从 0 开始实现一个简单的纯语音互动 App,适用于语音通话场景。 

- 首先,你需要了解以下有关音视频实时互动的基础概念: 

   - 声网实时互动 SDK:由声网开发的、帮助开发者在 App 中实现实时音视频互动的 SDK。 

   - 频道:用于传输数据的通道,在同一个频道内的用户可以进行实时互动。 

   - 主播:可以在频道内 **发布** 音视频,同时也可以 **订阅** 其他主播发布的音视频。 

   - 观众:可以在频道内 **订阅** 音视频,不具备 **发布** 音视频权限。 

#### 更多概念详见关键概念。 

#### 下图展示在 App 中实现纯语音互动的基本工作流程: 

1. 所有用户调用 `joinChannel` 方法加入频道,并将所有用户⻆色都设置为主播。 

2. 加入频道后,所有用户都可以在频道内发布音频流,并订阅对方的音频流。 

第1/10页 

https://doc.shengwang.cn/doc/rtc/harmonyos/basic-features/audio-quick-start 

实现纯语音互动 | 文档中心 | 声网 

2025/10/15 10:58 

## **前提条件** 

在实现功能以前,请按照以下要求准备开发环境: 

DevEco Studio NEXT Beta1 及以上版本。 API Version 11 的 HarmonyOS NEXT SDK 及以上版本。 API Version 11 的 HarmonyOS NEXT 2.0.0.59 操作系统及以上版本。 华为开发者账号。可在华为开发者联盟 注册账号。 

- 两台支持 HarmonyOS 的设备,建议使用 Mate 60 Pro 及更高性能的设备。 

- 可以访问互联网的计算机。如果你的网络环境部署了防火墙,参考应对防火墙限制以正常使用声网服务。 一个有效的声网账号以及声网项目。请参考开通服务从声网控制台获得 App ID 和临时 Token。 

#### **注意** 

临时 Token 的有效期是 24 小时。Token 过期会导致加入频道失败。 

## **创建项目** 

- 本小节介绍如何创建项目并为项目添加体验实时互动所需的权限。 

1. 参考创建和运行 Hello World ,创建一个新工程。 

2. 打开 **entry/src/main** 中的 `module.json5` 文件,在 `module` 模块中声明网络和设备权限: 

JSON `1 "requestPermissions": [ 2 //` 访问互联网的权限 `3 { 4 "name": "ohos.permission.INTERNET", 5 "reason": "$string:Internet_reason", 6 "usedScene": { 7 "abilities": [ 8 "EntryAbility" 9 ], 10 "when": "always" //` 始终需要该权限 `11 } 12 }, 13 //` 访问麦克风的权限 

第2/10页 

https://doc.shengwang.cn/doc/rtc/harmonyos/basic-features/audio-quick-start 

实现纯语音互动 | 文档中心 | 声网 

2025/10/15 10:58 

`14 { 15 "name": "ohos.permission.MICROPHONE", 16 "reason": "$string:Audio_reason", 17 "usedScene": { 18 "abilities": [ 19 "EntryAbility" 20 ], 21 "when": "always" //` 始终需要该权限 `22 } 23 }, 24 ]`  折叠 4 行 

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
8}
```

## **集成 SDK** 

1. 在下载页面下载最新版本的鸿蒙音频 SDK,并在本地解压。 

2. 打开解压文件,将 `AgoraRtcSdk.har` 文件复制到项目 **entry -> libs** 目录下(libs 文件夹需要手动创建)。 

3. 在 **entry** 下的 `oh-pacakge.json5` 文件中添加如下依赖,然后点击 **Sync** 开始同步。 

JSON `1 "dependencies": { 2 "@shengwang/rtc-voice":"file:./libs/AgoraRtcSdk.har" 3 }` 

第3/10页 

https://doc.shengwang.cn/doc/rtc/harmonyos/basic-features/audio-quick-start 

实现纯语音互动 | 文档中心 | 声网 

2025/10/15 10:58 

## **实现方法** 

#### 下图展示了使用声网 RTC SDK 实现纯语音互动的基本流程。 

App:用户 A RTC SDK App:用户 B
初始化引擎
1 创建并初始化引擎
2 创建并初始化引擎
加入频道
3 加入频道并设置用户角色为主播
4 加入频道并设置用户角色为主播
5 通知用户 A 已加入频道
6 通知用户 B 已加入频道
开始纯语音互动
App:用户 A RTC SDK App:用户 B

下面列出了一段实现纯语音互动基本流程的完整代码以供参考。复制以下代码到 `pages/Index.ets` 文件中替换原有内容,即可快 速体验纯语音互动。 

#### **信息** 

在 `appId` 、 `token` 和 `channelName` 字段中传入你在控制台获取到的 App ID、临时 Token,以及生成临时 Token 时填入的频道 名。 

实现纯语音互动示例代码 

### **处理权限请求** 

#### 本小节介绍如何获取设备的录音权限。 

1. 在 **entryablility** -> `EntryAbility.ets` 中的 `onCreate` 函数中添加权限申请。 

   - 启动应用程序时,检查是否已在 App 中授予了实现实时互动所需的权限。 

第4/10页 

https://doc.shengwang.cn/doc/rtc/harmonyos/basic-features/audio-quick-start 

实现纯语音互动 | 文档中心 | 声网 

2025/10/15 10:58 

##### ArkTS 

`1 //` 仅保留录音权限 `2` _`const`_ `permissions: Array<Permissions> = ['ohos.permission.INTERNET', 'ohos.permission.MICROPHONE']; 3 4` _`async function`_ `checkAccessToken(permission: Permissions): Promise<abilityAccessCtrl.GrantStatus> { 5` _`let`_ `atManager = abilityAccessCtrl.createAtManager(); 6` _`let`_ `grantStatus: abilityAccessCtrl.GrantStatus = abilityAccessCtrl.GrantStatus.PERMISSION_DENIED; 7 //` 获取应用程序的 `accessTokenID 8` _`let`_ `tokenId: number = 0; 9` _`try`_ `{ 10` _`let`_ `bundleInfo: bundleManager.BundleInfo =` _`await`_ `bundleManager.getBundleInfoForSelf(bundleManager.BundleFlag.GET_BUNDLE_INFO_WITH_APPLICATION); 11` _`let`_ `appInfo: bundleManager.ApplicationInfo = bundleInfo.appInfo; 12 tokenId = appInfo.accessTokenId; 13 }` _`catch`_ `(error) { 14` _`let`_ `err: BusinessError = error` _`as`_ `BusinessError; 15 console.error(`Failed to get bundle info for self. Code is ${err.code}, message is ${err.message}`); 16 } 17 //` 校验 `App` 是否被授予权限 `18` _`try`_ `{ 19 grantStatus =` _`await`_ `atManager.checkAccessToken(tokenId, permission); 20 }` _`catch`_ `(error) { 21` _`let`_ `err: BusinessError = error` _`as`_ `BusinessError; 22 console.error(`Failed to check access token. Code is ${err.code}, message is ${err.message}`); 23 } 24` _`return`_ `grantStatus; 25 } 26 27` _`export default class`_ `EntryAbility` _`extends`_ `UIAbility { 28 onCreate(want: Want, launchParam: AbilityConstant.LaunchParam) { 29 hilog.info(0x0000, 'testTag', '%{public}s', 'Ability onCreate'); 30` _`let`_ `context =` _`this`_ `.context; 31` _`let`_ `atManager = abilityAccessCtrl.createAtManager(); 32 // requestPermissionsFromUser` 会判断权限的授权状态来决定是否唤起弹窗 `33` _`for`_ `(` _`let`_ `i = 0; i < permissions.length; i++) { 34` _`let`_ `permission: Permissions = permissions[i]; 35` _`let`_ `granted: boolean = false;` 

第5/10页 

https://doc.shengwang.cn/doc/rtc/harmonyos/basic-features/audio-quick-start 

实现纯语音互动 | 文档中心 | 声网 

2025/10/15 10:58 

`36` _`let`_ `toGrantedPerm: Array<Permissions> =` _`new`_ `Array<Permissions>(); 37 toGrantedPerm.push(permission); 38 checkAccessToken(permission).then((value) => { 39` _`if`_ `(value == abilityAccessCtrl.GrantStatus.PERMISSION_GRANTED) { 40 granted = true; 41 hilog.info(0x0000, 'testTag', '%{public}s', 'Permission granted'); 42 }` _`else`_ `{ 43 atManager.requestPermissionsFromUser(context, toGrantedPerm).then((data) => { 44` _`let`_ `grantStatus: Array<number> = data.authResults; 45` _`let`_ `length: number = grantStatus.length; 46` _`for`_ `(` _`let`_ `i = 0; i < length; i++) { 47` _`if`_ `(grantStatus[i] === 0) { 48 //` 用户授权,可以继续访问目标操作 `49 }` _`else`_ `{ 50 //` 用户拒绝授权,提示用户必须授权才能访问当前页面的功能,并引导用户到系统设置中 打开相应的权限 `51 hilog.info(0x0000, 'testTag', '%{public}s', 'Permission denied'); 52` _`return`_ `; 53 } 54 } 55 //` 授权成功 `56 }).catch((err: BusinessError) => { 57 hilog.info(0x0000, 'testTag', '%{public}s', `Failed to request permissions from user. Code is ${err.code}, message is ${err.message}`); 58 }); 59 } 60 }); 61 } 62 } 63 }` 

 折叠 43 行 

### **导入声网组件** 

打开 `pages/Index.ets` 文件,导入声网 SDK 组件。 

##### ArkTS 

```
1import {
2    ChannelMediaOptions,
3    Constants,
```

第6/10页 

https://doc.shengwang.cn/doc/rtc/harmonyos/basic-features/audio-quick-start 

实现纯语音互动 | 文档中心 | 声网 

2025/10/15 10:58 

```
4    RtcEngine,
5    RtcEngineConfig,
6    RtcStats,
7} from"@shengwang/rtc-voice"
```

### **初始化引擎** 

调用 `create` 方法初始化 `RtcEngine` 。 

#### **注意** 

在初始化 SDK 前,需确保终端用户已经充分了解并同意相关的隐私政策。 

##### ArkTS 

`1` _`let`_ `config:RtcEngineConfig =` _`new`_ `RtcEngineConfig(); 2` _`let`_ `context = getContext(` _`this`_ `)` _`as`_ `common.UIAbilityContext; 3 config.mContext = context; 4 //` 在这里输入你在声网控制台中获取的 `App ID 5 config.mAppId = "<#Your App ID#>"; 6 config.mEventHandler = {}; 7 8 //` 创建并初始化 `RtcEngine 9` _`this`_ `.rtcEngine = RtcEngine.create(config);` 

### **加入频道并发布音频流** 

- 调用 `joinChannelWithOptions` 加入频道。在 `options` 中进行如下配置: 

设置频道场景为 `BROADCASTING` (直播场景) 并设置用户⻆色设置为 `BROADCASTER` (主播)。 

- 将 `publishMicrophoneTrack` 设置为 `true` ,发布麦克风采集的音频。 

- 将 `autoSubscribeAudio` 和 `autoSubscribeVideo` 设置为 `true` ,自动订阅所有音频流。 

##### ArkTS 

`1` _`let`_ `option:ChannelMediaOptions  =` _`new`_ `ChannelMediaOptions(); 2 //` 自动订阅所有音频流 `3 option.autoSubscribeAudio = true; 4 //` 发布麦克风采集的音频 

第7/10页 

https://doc.shengwang.cn/doc/rtc/harmonyos/basic-features/audio-quick-start 

实现纯语音互动 | 文档中心 | 声网 

2025/10/15 10:58 

`5 option.publishMicrophoneTrack = true; 6 //` 设置频道场景为直播 `7 option.channelProfile = Constants.ChannelProfile.LIVE_BROADCASTING; 8 //` 设置用户⻆色为主播 `9 option.clientRoleType = Constants.ClientRole.BROADCASTER; 10 //` 使用临时 `Token` 加入频道,在这里传入你的项目的 `Token` 和频道名 `11 // uid` 为 `0` ,表示由服务器分配 `uid` ,分配的 `uid` 将通过 `onJoinChannelSuccess` 回调返回 `12` _`this`_ `.rtcEngine.joinChannelWithOptions(<#Your Token#>, <#Your Channel Name#>, 0,option);` 

### **实现常用回调** 

根据使用场景,定义必要的回调。以下示例代码展示如何实现 `onJoinChannelSuccess` 和 `onUserOffline` 回调。 

##### ArkTS 

```
1config.mEventHandler.onUserJoined= (uid:number, collapse:number) => {
2console.info("mEventHandler.onUserJoined: "+ uid +" , "+ collapse);
3};
4
5config.mEventHandler.onJoinChannelSuccess= (cid:string, uid:number, elapsed:number) => {
6console.info("mEventHandler.onJoinChannelSuccess: "+ cid +" , "+ uid);
7};
8
9config.mEventHandler.onUserOffline= (uid:number, reason:number) => {
10console.info("mEventHandler.onUserOffline: "+ uid +" , "+ reason);
11};
```

### **开始音频互动** 

在 `onClick` 中调用一系列方法加载界面布局、检查 App 是否获取实时互动所需权限,并加入频道开始音频互动。 

##### ArkTS 

```
1Button("Join")
2.enabled(!this.isJoined)
3.fontSize(20)
4.width("40%")
5.margin({ left:"5%", right:"5%" })
6.align(Alignment.Center)
7.onClick(() => {
```

第8/10页 

https://doc.shengwang.cn/doc/rtc/harmonyos/basic-features/audio-quick-start 

实现纯语音互动 | 文档中心 | 声网 

2025/10/15 10:58 

```
8this.initEngineAndJoinChannel();
9})
```

### **结束音频互动** 

按照以下步骤结束音频互动: 2. 调用 `leaveChannel` 离开当前频道,释放所有会话相关的资源。 3. 调用 `destroy` 销毁引擎,并 释放声网 SDK 中使用的所有资源。 

#### **注意** 

- 调用 `destroy` 后,你将无法再使用 SDK 的所有方法和回调。如需再次使用实时音频互动功能,你必须重新创建一个新的引擎。详见 初始化引擎。 

该方法为同步调用。需要等待引擎资源释放后才能执行其他操作,因此建议在子线程中调用该方法,避免主线程阻塞。 

##### ArkTS 

- `1` _`this`_ `.rtcEngine!.leaveChannel();` 

- `RtcEngine.destroy(); 3` _`this`_ `.rtcEngine =` _`null`_ `;` 

## **测试 App** 

#### 按照以下步骤测试直播 App: 

1. 开启鸿蒙 NEXT 设备的开发者选项,打开 USB 调试,通过 USB 连接线将鸿蒙 NEXT 设备接入电脑。 

2. 在 DevEcho Studio 中,点击 **Sync and Refresh Project** 进行同步。 

3. 待同步成功后,点击 **Run 'app'** 开始编译。片刻后,App 便会安装到你的鸿蒙 NEXT 设备上。 

4. 启动 App,授予录音权限。 

5. 使用第二台鸿蒙 NEXT 设备,重复以上步骤,在该设备上安装 App、打开 App 加入频道,观察测试结果:双方可以听到彼此的 声音。 

## **后续步骤** 

在完成音频互动后,你可以阅读以下文档进一步了解: 

本文的示例使用了临时 Token 加入频道。在测试或生产环境中,为保证通信安全,声网推荐从服务器中获取 Token,详情请参考使 

第9/10页 

https://doc.shengwang.cn/doc/rtc/harmonyos/basic-features/audio-quick-start 

实现纯语音互动 | 文档中心 | 声网 

2025/10/15 10:58 

HarmonyOS 

用 Token 鉴权。 

## **相关信息** 

本节提供了额外的信息供参考。 

### **示例项目** 

声网提供了开源的纯语音互动示例项目供你参考,你可以前往下载或查看其中的源代码。 

**JoinAudioChannel JoinAudioChannel** 

### **常见问题** 

直播场景下,如何监听远端观众⻆色用户加入/离开频道的事件? 如何处理频道相关常见问题? 如何设置日志文件? 为什么部分鸿蒙版本 App 锁屏或切后台音视频采集无效? 错误码 频道连接状态管理 

### **相关文档** 

文档内容对你是否有帮助?   有帮助   没帮助
文
档
反
馈

隐私政策 服务条款 可接受的使用政策 安全合规 沪公网安备31011002006829号 沪ICP备2024090791号-1 上海声网科技有限公司 

第10/10页 

https://doc.shengwang.cn/doc/rtc/harmonyos/basic-features/audio-quick-start
