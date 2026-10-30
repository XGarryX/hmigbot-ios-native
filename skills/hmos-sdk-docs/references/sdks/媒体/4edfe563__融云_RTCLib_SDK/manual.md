# **RTC** 融云音视频 ( ) 客户端 **SDK** 快速接入 HarmonyOS RTCLib 

## 导入 **SDK** 

融云支持使用 DevEco Studio 中自动导入和手动导入两种方式 ,将 RTCLib SDK 导入到您的应用工程中。 

##### 环境要求 

- . DevEco Studio NEXT Release(5.0.3.900) 及以上。 

- .  HarmonyOS SDK API 12 及以上。 

- .  手机(真机)系统版本号 :NEXT.0.0.31 

##### 自动导入 **SDK** 

- 1.0.0 版本开始支持 OpenHarmony三方库中心获取 SDK 

1. 在 entry 目录中的 oh-package.json5 中添加 SDK 依赖 ,然后点击 "Sync Now"。 

###### **JSON** 

- **/** entry 目录中的 oh-package.json5 

- { "name": "entry", "version": "1.0.0", "description" : "Please describe the basic information.", "main" : "", "author": "", "license" : "", "dependencies": { "@rongcloud/imlib" : "x.y.z", "@rongcloud/rtclib" : "x.y.z" 

- } 

- } 

###### 注意 

   - .  各个 SDK 的最新版本号可能不相同 ,具体 x.y.z 值可前往融云官网 SDK 下载页面 或 OpenHarmony三方库中心 查询。 

1.    安装 SDK 成功后 ,您可以在项目根目录的 **oh_modules/.ohpm/** 中找到融云 RTCLib SDK。 

2.    查看更多其他融云 SDK。 打开OpenHarmony三方库中心 ,搜索关键字 **rongcloud** 

- 6 - 

##### 手动导入 **SDK** 

1. 在导入 SDK 前 ,您需要前往融云官网 SDK 下载页面 ,将音视频通话(无 UI)SDK 下载到本地。 

2. 创建 **./libs** 文件夹 ,将 SDK **har** 包 放入其中。 

#### 命令行安装 **SDK** 

1. 在工程根路径下执行以下命令行 : 

###### **shell** 

ohpm install libs/rtclib.har 

2. 执行完后 ,工程根路径的 oh-package.json5 就会依赖 SDK。 

###### **JSON** 

**/** 工程根路径下的 oh-package.json5 

{ "name": "xxx", "version": "1.0.0", "description" : "Please describe the basic information.", "main" : "", "author": "", "license" : "", "dependencies": { "@rongcloud/rtclib": "file:libs/rtclib.har", **/** 该配置由命令行生成 }, "devDependencies": { "@ohos/hypium": "1.0.16", "@ohos/hamock" : "1.0.0" } } 

- 7 - 

#### **entry** 配置文件依赖 **SDK** 

在 **entry** 同级目录的 oh-package.json5 手动配置 SDK 依赖。 

###### **JSON** 

- **/** entry 同级目录下的 oh-package.json5 需要手动配置 

- { 

"name": "xxx", 

"version": "1.0.0", 

"description" : "Please describe the basic information.", 

"main" : "", 

"author": "", 

"license" : "", 

"dependencies": { 

"@rongcloud/imlib": "file:../libs/RongIMLib.har", **/** 该配置手动依赖 

"@rongcloud/rtclib": "file:../libs/RTCLib.har" **/** 该配置手动依赖 

}, "devDependencies": { "@ohos/hypium": "1.0.16", "@ohos/hamock" : "1.0.0" } } 

#### 同步项目 

在 entry/oh-package.json5 中点击 **Sync Now** 同步工程 ,同步成功之后即可正常使用 RTCLib SDK。 

### Q 提示 

如果您同步之后依然无法导入 SDK ,这可能是 DevEco Studio 的编译缓存导致的问题。您可以尝试把 DevEco Studio 完全关闭之后重新打开 APP 工程来解决问题。 

- 8 - 

##### 配置项目 

#### 配置 **useNormalizedOHMUrl** 

1.0.0 版本开始 SDK 支持字节码 ,为了支持字节码 ,app 需要在项目根路径配置 **useNormalizedOHMUrl** 。 

// app 根路径下的 build-profile.json5 { "app": { "products": [ { "buildOption": { "strictMode": { "useNormalizedOHMUrl": true } } } ] } } 

##### 添加 **SDK** 依赖权限 

###### SDK 需要权限如下 : 

|权限名称|权限说明|使用目的|
|---|---|---|
|ohos.permission.GET_NETWORK_INFO|获取网络信息|网络变化之后获取网络信息 ,进行IM重连|
|ohos.permission.INTERNET|使用网络|连接IM、 收发消息需要网络连接|
|ohos.permission.MICROPHONE|麦克风权限|音频通话需要麦克风采集能力|
|ohos.permission.CAMERA|摄像头权限|视频通话需要摄像头采集能力|

1. 找到项目 entry/src/main/ 目录下的 module.json5  文件 ,添加 requestPermissions  配置 ,以配置摄像头权限为 

   - 例: 

###### **JSON** 

- 9 - 

"requestPermissions": [ 

{ "name": "ohos.permission.CAMERA", "reason": "$string:Camera", "usedScene": { "abilities": [ "EntryAbility", ], "when": "always" } }, ... **/** 配置其他权限 ] 

具体权限配置参数含义 ,请参考鸿蒙的应用权限管控文档。 

2. 配置权限时 ,按照规则需要考虑国际化问题 ,在项目 entry/src/main/resources/base/element 目录下找到 string.json  文件 ,对应增加配置字符变量 ,以配置摄像头字符变量为例 : 

###### **JSON** 

{ "string" : [ { "name": "Camera", "value": "Camera in RTC" }, ... **/** 定义其他 ] } 

## 实现音视频会议 

融云开发者账户是使用融云 SDK 产品的必要条件。在开始之前 ,请先前往融云官网注册开发者账户。注册后 ,控制台将自动 为你创建一个应用 ,默认为开发环境应用 ,使用国内数据中心。请获取该应用的 App Key ,在本教程中使用。 

首次使用融云音视频的用户 ,建议参考文档运行示例项目 ,以完成开发者账号注册、音视频服务开通等工作。 

Q 提示 房间人数上限 

- 10 - 

考虑移动设备的带宽(主要是在多路视频情况下)和 UI 交互效果 ,建议单次通话或房间内 ,视频不超过 16 人 ,纯音 频不超过 32 人。超过此上限可能影响通话效果。 

##### 环境要求 

. DevEco Studio NEXT Release(5.0.3.900) 及以上。 

- .  HarmonyOS SDK API 12 及以上。 

- .  手机(真机)系统版本号 :NEXT.0.0.31 

##### 步骤 **1** :服务开通 

您在融云创建的应用默认不会启用音视频服务。在使用融云提供的任何音视频服务前 ,您需要前往控制台 ,为应用开通音视频 服务。 

具体步骤请参阅开通音视频服务。 

Q 提示 

服务开通、 关闭等设置完成后 15 分钟后生效。 

##### 步骤 **2** : **SDK** 导入 

您需要导入融云音视频核心能力库 RTCLib ,和 RTC 业务所依赖的即时通讯能力库 IMLib。根据您的业务需求 ,可选择导入美 颜扩展库和 CDN 扩展库。 

具体步骤请参阅导入 SDK。 

##### 步骤 **4** :权限配置 

在 module.json5 中声明 SDK 需要的所有权限。 

###### **JSON** 

- 11 - 

{ 

"requestPermissions": [ { "name": "ohos.permission.INTERNET", "reason": "音视频需要网络权限" }, { "name": "ohos.permission.GET_NETWORK_INFO", "reason": "监听网络状态权限" }, { "name": "ohos.permission.CAMERA", "reason": "摄像头采集需要" }, { "name": "ohos.permission.MICROPHONE", "reason": "音频采集需要" } ] } 

##### 步骤 **5** :使用 **App Key** 初始化 

RTCLib 依赖融云即时通讯客户端( IM)SDK 提供信令通道。要在您的应用程序中集成和运行 ,您需要先对 IM SDK 进行初 始化。在成功建立 IM 连接后再初始化 RTCLib SDK。 

融云即时通讯客户端 SDK 核心类为 RongCoreClient 和 RongIMClient。在 Application 的 onCreate() 方法中 ,调用 RongIMClient 的初始化方法 ,传入生产或开发环境的 App Key。如果不换 AppKey ,在整个应用生命周期中 ,初始化一次 即可。 

如果 IM SDK 版本 ≧ 5.4.2 ,请使用以下初始化方法。 

###### **typescript** 

const appKey = "Your_AppKey"; **/** example: bos9p5rlcm2ba const initOption = new InitOption.Builder().build(); 

RongIMClient.init(getApplicationContext(), appKey, initOption); 

初始化配置( InitOption)中封装了区域码(AreaCode) ,导航服务地址( naviServer)、 文件服务地址 ( fileServer)、 数据统计服务地址( statisticServer)配置 ,以及是否开启推送的开关( enablePush)和主进程开关( isMainProcess)。 不传入任何配置表示全部使用默认配置。 SDK 默认连接北京数据中心。 

如果 App Key 不属于中国(北京)数据中心 ,则必须传入有效的初始化配置。 

- 12 - 

**typescript** 

RongIMClient.init(this, "<!--public-cloud-only start-->从控制台申请的 <!--public-cloud-only end-->AppKey"); 

关于 IM SDK 初始化的更多配置请参见初始化。 

##### 步骤 **6** :连接融云服务器 

音视频用户之间的信令传输依赖于融云的即时通信( IM)服务 ,因此需要先调用 connect 与 IM 服务建立好 TCP 长连接。建 议在功能模块的加载位置处调用 ,之后再进行音视频业务。 当模块退出后调用 disconnect 或 logout 断开该连接。 

IM 连接成功建立后可以初始化 RTCLib SDK。部分 RTC 引擎必须在初始化时提供 ,详见引擎配置。 

###### **typescript** 

try { 

const userId = await RongIMClient.connect("从您服务器端获取的 Token"); 

**/** 连接成功 

- **/** RTCLib 初始化 

const config = RCRTCConfig.Builder.create(); RCRTCEngine.getInstance().init(context, config.build()); 

} catch (error) { 

- **/** 连接失败 

' console.error( 连接失败:', error); } 

##### 步骤 **7** :加入房间 

1.    调用 RCRTCEngine.getInstance().joinRoom() 加入房间。通过 try-catch 或 Promise 的 resolve/reject 判断是否 加入房间成功。 

###### **typescript** 

try { 

const rcrtcRoom = await RCRTCEngine.getInstance().joinRoom("Your_Room_ID"); 

   - **/** 加入房间成功 

- } catch (rtcErrorCode: RTCErrorCode) { 

   - **/** 加入房间失败 

} 

2.    进入房间成功后调用 RCRTCRoom.registerRoomListener() 注册房间信息回调。 

3.   调用 RCRTCEngine.getInstance().getDefaultVideoStream().setVideoView() 方法设置本地视频的预览视图。 

- 13 - 

**typescript** 

/** 

- 初始化本地视频 

- */ 

initLocalVideoView(): void { 

- **/** 初始化视图 

const localVideoView = new RCRTCVideoView(getApplicationContext()); 

- **/** 绑定视图 

RCRTCEngine.getInstance().getDefaultVideoStream().setVideoView(localVideoView); 

- **/** 打开摄像机 

RCRTCEngine.getInstance().getDefaultVideoStream().startCamera(null); 

} 

/** 

- 处理入会成功后流程 

- */ 

async afterJoinRoomSuccess(rcrtcRoom: RCRTCRoom): Promise<void> { 

- **/** 注册房间事件回调 

rcrtcRoom .registerRoomListener({ 

**/** 此处省略 

}); 

**/** 开始推流 

await this.publishDefaultAVStream(rcrtcRoom); 

- **/** 订阅用户资源 

await this.subscribeAVStream(rcrtcRoom); } 

##### 步骤 **8** :发布资源 

1.    调用 RCRTCEngine.getInstance().getDefaultVideoStream().startCamera() 开启摄像头。不开启摄像头 ,会导 致对端订阅默认视频流后黑屏问题。 

2.   调用 RCRTCLocalUser 中的 publishDefaultStreams 方法发布默认音频视频资源。 

###### **typescript** 

- 14 - 

/** 

- 发布默认视频流 

- */ 

async publishDefaultAVStream(room: RCRTCRoom): Promise<void> { try { await room.getLocalUser().publishDefaultStreams(); 

   - **/** 发布成功 

- } catch (errorCode: RTCErrorCode) { 

**/** 发布失败 } } 

##### 步骤 **9** :订阅资源 

1.    调用 RCRTCLocalUser 中的 subscribeStreams 方法订阅会议参与者的资源 ,当远端用户发布资源时 ,会通过 onRemoteUserPublishResource 回调通知 ,需要订阅音视频流并显示视图。 

###### **typescript** 

- 15 - 

- /** 

- 主动订阅远端用户发布的流 

- 视频流需要用户设置用于显示载体的 VideoView 

- */ 

async subscribeAVStream(): Promise<void> { 

const inputStreams: RCRTCInputStream[] = []; 

for (const remoteUser of this.mRtcRoom.getRemoteUsers()) { 

if (remoteUser.getStreams().length === 0) { 

continue; 

} 

const userStreams = remoteUser.getStreams(); 

for (const inputStream of userStreams) { 

if (inputStream.getMediaType() === RCRTCMediaType.VIDEO) { 

const videoInputStream = inputStream as RCRTCVideoInputStream; 

**/** 如果未绑定过VideoView,则需要创建并绑定VideoView 

if (videoInputStream.getVideoView() === null) { 

**/** 创建流对应的视图 

const videoView = new RCRTCVideoView(getApplicationContext()); 

**/** 将视图和 stream 进行绑定 

videoInputStream.setVideoView(videoView); 

**/** 将远端视图添加至布局 

this.frameyout_remoteUser.addView(videoView); 

} 

} 

} 

inputStreams.push(...remoteUser.getStreams()); 

} 

if (inputStreams.length === 0) { 

return; 

} 

try { 

await this.mRtcRoom.getLocalUser().subscribeStreams(inputStreams); 

**/** 订阅成功 

} catch (error: { failedStreams: RCRTCInputStream[], errorCode: RTCErrorCode }) { 

**/** 订阅失败 

**/** 如果 SDK ≧ 5. 3. 4 ,error 会包含订阅失败的流列表和错误码。 **/** 如果 SDK < 5. 3. 4 ,error 仅包含错误码。 } } 

2.   在注册的房间事件回调中可根据业务需求监听远端用户发布的资源 ,并进行订阅。 

- 16 - 

**typescript** 

const roomEventsListener = { /** * 房间内用户发布资源 * * @param rcrtcRemoteUser 远端用户 * @param list   发布的资源 */ 

onRemoteUserPublishResource: async (rcrtcRemoteUser: RCRTCRemoteUser, list: RCRTCInputStream[]): Promise<void> => { await this.subscribeAVStream(); } }; 

- 64 -
