# **RTC 融云音视频 ( ) SDK 客户端 文档** HarmonyOS RTCLib 

## **目录** 

|导入SDK|6|
|---|---|
|环境要求|6|
|自动导入SDK|6|
|手动导入SDK|7|
|命令行安装SDK|7|
|entry配置文件依赖SDK|8|
|同步项目|8|
|配置项目|9|
|配置useNormalizedOHMUrl|9|
|添加SDK依赖权限|9|
|实现音视频会议|10|
|环境要求|11|
|步骤1:服务开通|11|
|步骤2:SDK导入|11|
|步骤4:权限配置|11|
|步骤5:使用App Key初始化|12|
|步骤6:连接融云服务器|13|
|步骤7:加入房间|13|
|步骤8:发布资源|14|
|步骤9:订阅资源|15|
|开通音视频服务|17|
|融云开发者账号|17|
|音视频服务类型|17|
|免费体验时长|18|
|开通步骤|18|
|初始化|19|
|注意事项|19|
|准备App Key|19|

- 2 - 

|初始化之前|20|
|---|---|
|初始化|20|
|初始化IM SDK|20|
|初始化RTC SDK|22|
|引擎配置|22|
|引擎配置速览|23|
|断线重连|23|
|状态报表数据回调时间间隔|23|
|媒体流加密功能(SRTP)|24|
|音频初始化配置|24|
|开启OpenSLES录制麦克风数据|24|
|修改音频编解码类型|24|
|修改音频录音来源|25|
|修改音频采样率|25|
|开启/关闭立体声|25|
|开启/关闭麦克风采集|26|
|视频初始化配置|26|
|设置硬编码码率控制模式|26|
|关闭硬件编码|26|
|关闭硬件解码|27|
|开启/关闭硬件高压缩编码|27|
|配置硬件编码帧率|27|
|开启/关闭 采集/解码 到纹理|27|
|房间管理|28|
|自定义房间属性|28|
|设置属性|28|
|获取属性|29|
|删除属性|29|
|属性变化回调|30|
|基本操作|31|
|创建/加入房间|31|
|退出房间|31|

- 3 - 

房间事件回调 

|房间事件回调|32|
|---|---|
|状态相关|32|
|资源相关|33|
|数据相关|34|
|发布与订阅(会议)|34|
|本地用户流|34|
|发布|34|
|取消发布|35|
|远端用户流|35|
|订阅|35|
|取消订阅|36|
|音频管理|37|
|混音|37|
|前提条件|37|
|从音频文件或网络音源混音|37|
|从音频数据混音|39|
|混音设置声道|39|
|设置混音状态监听|40|
|获取混音后的音频数据|41|
|音频模式|41|
|了解音频模式|42|
|了解音质与码率|42|
|如何匹配模式和音质|42|
|设置音频场景与音频质量|43|
|流处理|43|
|本地音频流处理|44|
|远端音频流处理|44|
|音量|45|
|设置采集音量|45|
|调节远端播放音量|45|
|静音本地音频流|46|
|静音远端音频流|46|

- 4 - 

|静音房间内全部远端音频流|46|
|---|---|
|视频管理|46|
|大小流|46|
|发布方开关大小流|47|
|订阅方切换大小流|48|
|流处理|48|
|本地视频流处理|48|
|本地视频流静默|49|
|远端视频流处理|49|
|远端视频流静默|50|
|分辨率/码率/帧率设置|50|
|设置分辨率|50|
|设置码率|51|
|设置帧率|51|
|API参考|51|
|对接第三方插件|51|
|步骤1:设置视频数据回调|51|
|步骤2:处理视频帧数据|52|
|水印处理|52|
|设置水印|52|
|函数声明|53|
|示例代码|53|
|注意事项|54|
|状态码|54|

- 5 - 

#### **导入 SDK** 

融云支持使用 DevEco Studio 中自动导入和手动导入两种方式,将 RTCLib SDK 导入到您的应用工程中。 

###### **环境要求** 

DevEco Studio NEXT Release(5.0.3.900) 及以上。 

- HarmonyOS SDK API 12 及以上。 

- 手机(真机)系统版本号:NEXT.0.0.31 

###### **自动导入 SDK** 

1.0.0 版本开始支持 OpenHarmony三方库中心获取 SDK 

1. 在 entry 目录中的 oh-package.json5 中添加 SDK 依赖,然后点击 "Sync Now"。 

###### **JSON** 

// entry 目录中的 oh-package.json5 { "name": "entry", "version": "1.0.0", "description": "Please describe the basic information.", "main": "", "author": "", "license": "", "dependencies": { "@rongcloud/imlib" : "x.y.z", "@rongcloud/rtclib" : "x.y.z" } } 

###### **注意** 

各个 SDK 的最新版本号可能不相同,具体 x.y.z 值可前往 融云官网 SDK 下载页面 或 OpenHarmony三方库中心 查询。 

1. 安装 SDK 成功后,您可以在项目根目录的 **oh_modules/.ohpm/** 中找到融云 RTCLib SDK。 

2. 查看更多其他融云 SDK。 打开OpenHarmony三方库中心,搜索关键字 **rongcloud** 

- 6 - 

###### **手动导入 SDK** 

1. 在导入 SDK 前,您需要前往融云官网 SDK 下载页面,将音视频通话(无 UI)SDK 下载到本地。 

2. 创建 **./libs** 文件夹,将 SDK **har 包** 放入其中。 

##### **命令行安装 SDK** 

1. 在工程根路径下执行以下命令行: 

###### **shell** 

ohpm install libs/rtclib.har 

2. 执行完后,工程根路径的 oh-package.json5 就会依赖 SDK。 

###### **JSON** 

// 工程根路径下的 oh-package.json5 { "name": "xxx", "version": "1.0.0", "description": "Please describe the basic information.", "main": "", "author": "", "license": "", "dependencies": { "@rongcloud/rtclib": "file:libs/rtclib.har", // 该配置由命令行生成 }, "devDependencies": { "@ohos/hypium": "1.0.16", "@ohos/hamock": "1.0.0" } } 

- 7 - 

##### **entry 配置文件依赖 SDK** 

在 **entry** 同级目录的 oh-package.json5 手动配置 SDK 依赖。 

###### **JSON** 

// entry 同级目录下的 oh-package.json5 需要手动配置 

{ 

"name": "xxx", "version": "1.0.0", 

"description": "Please describe the basic information.", 

"main": "", "author": "", "license": "", "dependencies": { 

"@rongcloud/imlib": "file:../libs/RongIMLib.har",  // 该配置手动依赖 

"@rongcloud/rtclib": "file:../libs/RTCLib.har" // 该配置手动依赖 }, 

```arkts
"devDependencies": { "@ohos/hypium": "1.0.16", "@ohos/hamock": "1.0.0" } } 
```

##### **同步项目** 

在 entry/oh-package.json5 中点击 **Sync Now** 同步工程,同步成功之后即可正常使用 RTCLib SDK。 

提示

如果您同步之后依然无法导入 SDK,这可能是 DevEco Studio 的编译缓存导致的问题。您可以尝试把 DevEco Studio 完全关闭之后重新打开 APP 工程来解决问题。 

- 8 - 

###### **配置项目** 

##### **配置 useNormalizedOHMUrl** 

1.0.0 版本开始 SDK 支持字节码,为了支持字节码,app 需要在项目根路径配置 **useNormalizedOHMUrl** 。 

// app 根路径下的 build-profile.json5 { "app": { "products": [ { "buildOption": { "strictMode": { "useNormalizedOHMUrl": true } } } ] } } 

###### **添加 SDK 依赖权限** 

###### SDK 需要权限如下: 

|权限名称|权限说明|使用目的|
|---|---|---|
|ohos.permission.GET_NETWORK_INFO|获取网络信息|网络变化之后获取网络信息,进行IM重连|
|ohos.permission.INTERNET|使用网络|连接IM、收发消息需要网络连接|
|ohos.permission.MICROPHONE|麦克风权限|音频通话需要麦克风采集能力|
|ohos.permission.CAMERA|摄像头权限|视频通话需要摄像头采集能力|

1. 找到项目 entry/src/main/ 目录下的 module.json5 文件,添加 requestPermissions 配置,以配置摄像头权限为 例: 

###### **JSON** 

- 9 - 

"requestPermissions": [ { "name": "ohos.permission.CAMERA", "reason": "$string:Camera", "usedScene": { "abilities": [ "EntryAbility", ], "when": "always" } }, ... // 配置其他权限 ] 

具体权限配置参数含义,请参考鸿蒙的应用权限管控文档。 

2. 配置权限时,按照规则需要考虑国际化问题,在项目 entry/src/main/resources/base/element 目录下找到 string.json 文件,对应增加配置字符变量,以配置摄像头字符变量为例: 

###### **JSON** 

{ "string": [ { "name": "Camera", "value": "Camera in RTC" }, ... // 定义其他 ] } 

#### **实现音视频会议** 

融云开发者账户是使用融云 SDK 产品的必要条件。在开始之前,请先前往融云官网注册开发者账户。注册后,控制台将自动 为你创建一个应用,默认为开发环境应用,使用国内数据中心。请获取该应用的 App Key,在本教程中使用。 

首次使用融云音视频的用户,建议参考文档运行示例项目,以完成开发者账号注册、音视频服务开通等工作。 

提示 **房间人数上限** 

- 10 - 

考虑移动设备的带宽(主要是在多路视频情况下)和 UI 交互效果,建议单次通话或房间内,视频不超过 16 人,纯音 频不超过 32 人。超过此上限可能影响通话效果。 

###### **环境要求** 

DevEco Studio NEXT Release(5.0.3.900) 及以上。 

HarmonyOS SDK API 12 及以上。 

- 手机(真机)系统版本号:NEXT.0.0.31 

###### **步骤 1 :服务开通** 

您在融云创建的应用默认不会启用音视频服务。在使用融云提供的任何音视频服务前,您需要前往控制台,为应用开通音视频 服务。 

具体步骤请参阅开通音视频服务。 

提示 服务开通、关闭等设置完成后 15 分钟后生效。 

###### **步骤 2 : SDK 导入** 

您需要导入融云音视频核心能力库 RTCLib,和 RTC 业务所依赖的即时通讯能力库 IMLib。根据您的业务需求,可选择导入美 颜扩展库和 CDN 扩展库。 

具体步骤请参阅导入 SDK。 

###### **步骤 4 :权限配置** 

在 module.json5 中声明 SDK 需要的所有权限。 

###### **JSON** 

- 11 - 

{ "requestPermissions": [ { "name": "ohos.permission.INTERNET", "reason": "音视频需要网络权限" }, { "name": "ohos.permission.GET_NETWORK_INFO", "reason": "监听网络状态权限" }, { "name": "ohos.permission.CAMERA", "reason": "摄像头采集需要" }, { "name": "ohos.permission.MICROPHONE", "reason": "音频采集需要" } ] } 

###### **步骤 5 :使用 App Key 初始化** 

RTCLib 依赖融云即时通讯客户端(IM)SDK 提供信令通道。要在您的应用程序中集成和运行,您需要先对 IM SDK 进行初 始化。在成功建立 IM 连接后再初始化 RTCLib SDK。 

融云即时通讯客户端 SDK 核心类为 RongCoreClient 和 RongIMClient。在 Application 的 onCreate() 方法中,调用 RongIMClient 的初始化方法,传入 **生产** 或 **开发** 环境的 App Key。如果不换 AppKey,在整个应用生命周期中,初始化一次 即可。 

如果 IM SDK 版本 ≧ 5.4.2,请使用以下初始化方法。 

###### **typescript** 

const appKey = "Your_AppKey"; // example: bos9p5rlcm2ba const initOption = new InitOption.Builder().build(); 

RongIMClient.init(getApplicationContext(), appKey, initOption); 

初始化配置(InitOption)中封装了区域码(AreaCode),导航服务地址(naviServer)、文件服务地址(fileServer)、 数据统计服务地址(statisticServer)配置,以及是否开启推送的开关(enablePush)和主进程开关(isMainProcess)。 不传入任何配置表示全部使用默认配置。SDK 默认连接北京数据中心。 

如果 App Key 不属于中国(北京)数据中心,则必须传入有效的初始化配置。 

- 12 - 

**typescript** 

RongIMClient.init(this, "<!--public-cloud-only start-->从控制台申请的 <!--public-cloud-only end-->AppKey"); 

关于 IM SDK 初始化的更多配置请参见初始化。 

###### **步骤 6 :连接融云服务器** 

音视频用户之间的信令传输依赖于融云的即时通信(IM)服务,因此需要先调用 connect 与 IM 服务建立好 TCP 长连接。建 议在功能模块的加载位置处调用,之后再进行音视频业务。当模块退出后调用 disconnect 或 logout 断开该连接。 

IM 连接成功建立后可以初始化 RTCLib SDK。部分 RTC 引擎必须在初始化时提供,详见引擎配置。 

###### **typescript** 

try { 

```arkts
const userId = await RongIMClient.connect("从您服务器端获取的 Token"); // 连接成功 // RTCLib 初始化 const config = RCRTCConfig.Builder.create(); RCRTCEngine.getInstance().init(context, config.build()); } catch (error) { // 连接失败 ' console.error( 连接失败:', error); } 
```

###### **步骤 7 :加入房间** 

1. 调用 RCRTCEngine.getInstance().joinRoom() 加入房间。通过 try-catch 或 Promise 的 resolve/reject 判断是否 加入房间成功。 

###### **typescript** 

try { 

const rcrtcRoom = await RCRTCEngine.getInstance().joinRoom("Your_Room_ID"); 

   - // 加入房间成功 

   - } catch (rtcErrorCode: RTCErrorCode) { 

   - // 加入房间失败 

   - } 

2. 进入房间成功后调用 RCRTCRoom.registerRoomListener() 注册房间信息回调。 

3. 调用 RCRTCEngine.getInstance().getDefaultVideoStream().setVideoView() 方法设置本地视频的预览视图。 

- 13 - 

**typescript** 

/** 

* 初始化本地视频 */ initLocalVideoView(): void { 

// 初始化视图 

const localVideoView = new RCRTCVideoView(getApplicationContext()); // 绑定视图 

RCRTCEngine.getInstance().getDefaultVideoStream().setVideoView(localVideoView); // 打开摄像机 

RCRTCEngine.getInstance().getDefaultVideoStream().startCamera(null); 

} 

/** 

* 处理入会成功后流程 */ 

async afterJoinRoomSuccess(rcrtcRoom: RCRTCRoom): Promise<void> { // 注册房间事件回调 

rcrtcRoom.registerRoomListener({ // 此处省略 }); // 开始推流 await this.publishDefaultAVStream(rcrtcRoom); // 订阅用户资源 await this.subscribeAVStream(rcrtcRoom); } 

###### **步骤 8 :发布资源** 

1. 调用 RCRTCEngine.getInstance().getDefaultVideoStream().startCamera() 开启摄像头。不开启摄像头,会导 致对端订阅默认视频流后黑屏问题。 

2. 调用 RCRTCLocalUser 中的 publishDefaultStreams 方法发布默认音频视频资源。 

###### **typescript** 

- 14 - 

/** * 发布默认视频流 

*/ 

async publishDefaultAVStream(room: RCRTCRoom): Promise<void> { try { 

   - await room.getLocalUser().publishDefaultStreams(); 

   - // 发布成功 

- } catch (errorCode: RTCErrorCode) { 

// 发布失败 } } 

###### **步骤 9 :订阅资源** 

1. 调用 RCRTCLocalUser 中的 subscribeStreams 方法订阅会议参与者的资源,当远端用户发布资源时,会通过 onRemoteUserPublishResource 回调通知,需要订阅音视频流并显示视图。 

###### **typescript** 

- 15 - 

/** 

* 主动订阅远端用户发布的流 

* 视频流需要用户设置用于显示载体的 VideoView 

*/ 

async subscribeAVStream(): Promise<void> { 

const inputStreams: RCRTCInputStream[] = []; 

for (const remoteUser of this.mRtcRoom.getRemoteUsers()) { 

if (remoteUser.getStreams().length === 0) { 

continue; } 

const userStreams = remoteUser.getStreams(); 

for (const inputStream of userStreams) { 

if (inputStream.getMediaType() === RCRTCMediaType.VIDEO) { 

const videoInputStream = inputStream as RCRTCVideoInputStream; 

//如果未绑定过VideoView,则需要创建并绑定VideoView 

if (videoInputStream.getVideoView() === null) { 

- // 创建流对应的视图 

const videoView = new RCRTCVideoView(getApplicationContext()); 

// 将视图和 stream 进行绑定 

setVideoView(videoView); 

// 将远端视图添加至布局 

this.frameyout_remoteUser.addView(videoView); 

} } } 

inputStreams.push(...remoteUser.getStreams()); 

} 

if (inputStreams.length === 0) { 

return; } 

try { 

await this.mRtcRoom.getLocalUser().subscribeStreams(inputStreams); // 订阅成功 

} catch (error: { failedStreams: RCRTCInputStream[], errorCode: RTCErrorCode }) { // 订阅失败 

// 如果 SDK ≧ 5.3.4,error 会包含订阅失败的流列表和错误码。 

// 如果 SDK < 5.3.4,error 仅包含错误码。 } } 

2. 在注册的房间事件回调中可根据业务需求监听远端用户发布的资源,并进行订阅。 

- 16 - 

###### **typescript** 

```arkts
const roomEventsListener = { /** * 房间内用户发布资源 * * @param rcrtcRemoteUser 远端用户 * @param list    发布的资源 */ onRemoteUserPublishResource: async (rcrtcRemoteUser: RCRTCRemoteUser, list: RCRTCInputStream[]): Promise<void> => { await this.subscribeAVStream(); } }; 
```

#### **开通音视频服务** 

###### **融云开发者账号** 

在开始之前,请确认您已注册融云开发者账户。控制台将自动为新注册用户创建一个应用,默认为开发环境应用,使用国内数 据中心。您也可以自动创建应用。集成客户端 SDK 时需要使用应用的 App Key。 

您在融云创建的应用默认不会启用音视频服务。在使用融云提供的任何音视频服务前,您需要前往控制台,为应用开通音视频 服务。 

提示 

服务开通、关闭等设置完成后 15 分钟后生效。 

###### **音视频服务类型** 

- 17 - 

根据您的应用类型及业务场景,您可能需要开通全部或部分音视频服务。 

|业务||控制台服务||
|---|---|---|---|
|类型|说明|名称|控制台链接|
|呼叫|基于CallKit/CallLib开发音视|**音视频通**|开通音视频通话服务|
||频电话类应用|**话**||
|会议|基于RTCLib开发音视频会议应|**音视频通**|开通音视频通话服务|
||用|**话**||
|直播|基于RTCLib开发低延迟直播应|**音视频直**|不支持自主开通。如需咨询该业务,请联系商务。您可以在音视频直|
||用|**播** 注1|播页面查看商务联系方式。|

注1:开通音视频直播服务前,需要先开通音视频通话服务。 

###### **免费体验时长** 

在开发环境下创建的每个应用均可享有 10000 分钟免费体验时长。 

###### **开通步骤** 

如果在开发环境下开通音视频服务,可直接按照以下步骤,开通音视频服务即可开始体验和测试。免费体验时长用完即止。 如果在生产环境下开通音视频服务,则需要先预存费用,才可开通。 

1. 登录 融云控制台,在页面顶部点击 **服务管理** 。 

2. 开通音视频服务以 App Key 为准。如果您拥有多个应用,请先选择应用名称(下图中标号 1)。每个应用都提供用于 隔离生产和开发环境的两套独立 App Key / Secret。应用时,请注意选择正确的环境(开发 / 生产,下图中标号 2)。 

提示 如果您尚未向融云申请应用上线,仅可使用开发环境。 

- 18 - 

3. 在页面左侧导航栏,找到「音视频服务」分类。点击该分类下的 **实时音视频** 或 **音视频直播** ,可进入相应页面开通服 务。 

4. 服务开通、关闭等设置完成,最长 15 分钟后生效。 

#### **初始化** 

在使用 SDK 其它功能前,必须先进行初始化。本文中将详细说明初始化的方法。 

###### **注意事项** 

- 必须在应用生命周期内调用初始化方法,只需要调用一次。 

- 初始化后,会启动应用主进程、与应用包名相关的 IPC 进程、以及融云默认推送进程。 

###### **准备 App Key** 

您必须拥有正确的 App Key,才能进行初始化。 

您可以登录融云控制台,从 **服务管理** 页面,查看您已创建的各个应用的 App Key。 

如果您拥有多个应用,请注意选择应用名称(下图中标号 1)。另外,融云的每个应用都提供用于隔离生产和开发环境的两套 独立 App Key / Secret。在获取应用的 App Key 时,请注意区分环境( **生产** / **开发** ,下图中标号 2)。 

提示 

如果您并非应用创建者,我们建议在获取 App Key 时确认页面上显示的 **数据中心** 是否符合预期。 如果您尚未向融云申请应用上线,仅可使用开发环境。 

- 19 - 

###### **初始化之前** 

部分配置必须在初始化之前完成,否则 SDK 功能无法正常工作。 

- **开通音视频服务** :音视频服务需要手动开通。请根据应用的具体业务类型,开通对应的音视频服务。详细说明请参见开通 音视频服务。 

- **海外数据中心** :因为音视频业务依赖即时通讯业务 IMLib 提供信令通道,如果您的应用使用海外数据中心,必须在初始 化之前修改 IMLib SDK 默认连接的服务地址为海外数据中心地址。否则 SDK 默认连接中国国内数据中心服务地址。详 细说明请参见配置海外数据中心服务地址。 

###### **初始化** 

音视频 SDK 是基于即时通信 SDK 作为信令通道的,所以要分别初始化 IM SDK 和 RTC SDK。 

##### **初始化 IM SDK** 

如果不换 AppKey,在整个应用生命周期中,初始化一次即可。建议调用位置放在 Application 的 onCreate() 方法内,或 在音视频功能模块的加载位置处。 

提示 

以下初始化方法要求 SDK 版本 ≧ 5.4.2。 

请在 Application 的 onCreate() 方法中初始化 SDK,传入 **生产** 或 **开发** 环境的 App Key。 

###### **typescript** 

- 20 - 

const appKey = "YourAppKey"; // example: bos9p5rlcm2ba const initOption = new InitOption.Builder().build(); 

RongCoreClient.init(this, appKey, initOption); 

初始化配置(InitOption)中封装了区域码(AreaCode)配置。SDK 将通过区域码获取有效的导航服务地址、文件服务地 址、数据统计服务地址、和日志服务地址等配置。 

- 如果 App Key 属于中国(北京)数据中心,您无需传入任何配置,SDK 会使用默认配置。 

- 如果 App Key 属于海外数据中心,则必须传入有效的区域码(AreaCode)配置。请务必在控制台核验当前 App Key 所属海外数据中心后,找到 AreaCode 中对应的枚举值进行配置。 

例如,使用新加坡数据中心的应用的 **生产** 或 **开发** 环境的 App Key: 

###### **typescript** 

const appKey = "Singapore_dev_AppKey"; const areaCode = AreaCode.SG; 

const initOption = new InitOption.Builder() 

.setAreaCode(areaCode) .build(); 

RongIMClient.init(context, appKey, initOption); 

除区域码外,初始化配置(InitOption)中还封装了以下配置: 

- 是否开启推送的开关( enablePush ):是否整体禁用推送。 

- 主进程开关( isMainProcess ):是否为主进程。默认情况下由 SDK 判断进程。 

- 导航服务地址( naviServer ):一般情况下不建议单独配置。SDK 内部默认使用与区域码对应的地址。 

- 文件服务地址( fileServer ):仅限私有云使用。 

- 数据统计服务地址( statisticServer ):一般情况下不建议单独配置。SDK 内部默认使用与区域码对应的地址。 

###### **typescript** 

- 21 - 

const appKey = "Your_AppKey"; const areaCode = AreaCode.BJ; 

const initOption = new InitOption.Builder() 

.setAreaCode(areaCode) 

.enablePush(true) 

.setFileServer("http(s)://fileServer") 

.setNaviServer("http(s)://naviServer") .setStatisticServer("http(s)://StatisticServer") .build(); 

RongIMClient.init(context, appKey, initOption); 

##### **初始化 RTC SDK** 

音视频用户之间的信令传输依赖于融云的即时通信(IM)服务,因此需要先与融云服务器建立 IM 链接,在连接成功后可以初 始化 RTC SDK。 

部分 RTC 引擎必须在初始化时提供,详见引擎配置。 

###### **typescript** 

```arkts
RongIMClient.connect("从您服务器端获取的 Token", { onSuccess(userId: string): void { // 连接成功 // RTCLib 初始化 const config = RCRTCConfig.Builder.create(); RCRTCEngine.getInstance().init(context, config.build()); }, onError(code: RongIMClient.ConnectionErrorCode): void { // 连接失败 }, onDatabaseOpened(databaseOpenStatus: RongIMClient.DatabaseOpenStatus): void { // 数据库打开失败 } }); 
```

#### **引擎配置** 

- 22 - 

###### **引擎配置速览** 

###### RTC 引擎提供以下配置,可按需修改。 

|适用平台|配置项|
|---|---|
|断线重连|默认开启|
|状态报表数据回调时间间隔|默认1000ms|
|媒体流加密功能(SRTP)|默认关闭|
|音频初始化配置- OpenSLES录制麦克风数据|默认关闭|
|音频初始化配置-编码类型|默认Opus|
|音频初始化配置-录音来源|默认来自语音通信|
|音频初始化配置-采样率|默认16000|
|音频初始化配置-立体声|默认开启|
|音频初始化配置-麦克风采集|默认开启|
|视频初始化配置-硬编码码率控制模式|默认CBR|
|视频初始化配置-硬件编码|默认开启|
|视频初始化配置-硬件解码|默认开启|
|视频初始化配置-高压缩编码|默认关闭|
|视频初始化配置-硬件编码帧率|默认30 Fps|
|视频初始化配置-采集/解码 到纹理|默认开启|

###### **断线重连** 

###### 断线重连功能默认开启,可以在引擎初始化时传入以下配置进行关闭: 

###### **typescript** 

RCRTCConfig.Builder config = RCRTCConfig.Builder.create(); config.enableAutoReconnect(false); config.build(); RCRTCEngine.getInstance().init(context, config); 

###### **状态报表数据回调时间间隔** 

- 23 - 

状态数据报表回调默认时间间隔为 1000ms,最小时间间隔为 100ms。请注意,过小的时间间隔会影响性能。 

可以在引擎初始化时传入以下配置进行修改: 

###### **typescript** 

RCRTCConfig.Builder config = RCRTCConfig.Builder.create(); config.setStatusReportInterval(2000); //修改回调时间间隔为 2 秒 config.build(); RCRTCEngine.getInstance().init(context, config); 

###### **媒体流加密功能( SRTP )** 

SDK 内置 SRTP 安全实时传输协议,即协议层的标准加密方式。以开关形式提供,使用简单。媒体流加密功能(SRTP)功能 默认关闭。请注意,开启该功能会对性能和用户体验有一定影响,如果没有该需求请不要打开。 

可以在引擎初始化时传入以下配置进行开启: 

###### **typescript** 

RCRTCConfig.Builder config = RCRTCConfig.Builder.create(); config.enableSRTP(true); config.build(); RCRTCEngine.getInstance().init(context, config); 

###### **音频初始化配置** 

##### **开启 OpenSLES 录制麦克风数据** 

默认关闭。可以在引擎初始化时传入以下配置进行开启: 

###### **typescript** 

RCRTCConfig.Builder config = RCRTCConfig.Builder.create(); config.enableLowLatencyRecording(true); config.build(); RCRTCEngine.getInstance().init(context, config); 

##### **修改音频编解码类型** 

目前支持 PCMU 和 OPUS 两种音频编解码方式,默认配置是 OPUS。 

可以在引擎初始化时传入以下配置进行修改: 

- 24 - 

###### **typescript** 

RCRTCConfig.Builder config = RCRTCConfig.Builder.create(); config.setAudioCodecType(AudioCodecType.PCMU); // 修改音频编解码类型为 PCMU config.build(); RCRTCEngine.getInstance().init(context, config); 

##### **修改音频录音来源** 

默认录音来源为语音通信。该配置适用于 SDK 中默认设置的音源在设备上 AudioRecord 采集音频异常场景。 

可以在引擎初始化时传入以下配置进行修改: 

###### **typescript** 

RCRTCConfig.Builder config = RCRTCConfig.Builder.create(); config.setAudioSource(myAudioSource); config.build(); RCRTCEngine.getInstance().init(context, config); 

myAudioSource 的枚举值对应 HarmonyOS SDK 中的 MediaRecorder.AudioSource。 

##### **修改音频采样率** 

引擎支持的采样率有:8000,16000, 32000, 44100, 48000。 默认为 16000。 

可以在引擎初始化时传入以下配置进行修改: 

###### **typescript** 

RCRTCConfig.Builder config = RCRTCConfig.Builder.create(); config.setAudioSampleRate(32000); // 修改音频采样率为 32000 config.build(); RCRTCEngine.getInstance().init(context, config); 

##### **开启 / 关闭立体声** 

默认开启,可以在引擎初始化时传入以下配置进行关闭: 

###### **typescript** 

RCRTCConfig.Builder config = RCRTCConfig.Builder.create(); config.enableStereo(false); config.build(); RCRTCEngine.getInstance().init(context, config); 

- 25 - 

##### **开启 / 关闭麦克风采集** 

默认开启,可以在引擎初始化时传入以下配置进行关闭: 

###### **typescript** 

RCRTCConfig.Builder config = RCRTCConfig.Builder.create(); config.enableMicrophone(false); config.build(); RCRTCEngine.getInstance().init(context, config); 

提示 

如配置麦克风关闭,则在整个引擎生命周期内都无法再次开启。 

###### **视频初始化配置** 

##### **设置硬编码码率控制模式** 

默认使用 RongRTCConfig.VideoBitrateMode.CBR。支持 CBR/VBR/CQ。 

可以在引擎初始化时传入以下配置进行修改: 

###### **typescript** 

RCRTCConfig.Builder config = RCRTCConfig.Builder.create(); config.setHardwareEncoderBitrateMode(RongRTCConfig.VideoBitrateMode.VBR); config.build(); RCRTCEngine.getInstance().init(context, config); 

##### **关闭硬件编码** 

默认开启。SDK 会根据硬件支持情况创建硬编码器,如果创建失败会使用软编。 

可以在引擎初始化时传入以下配置进行关闭: 

###### **typescript** 

RCRTCConfig.Builder config = RCRTCConfig.Builder.create(); config.enableHardwareEncoder(false); config.build(); RCRTCEngine.getInstance().init(context, config); 

- 26 - 

##### **关闭硬件解码** 

默认开启。SDK 会根据硬件支持情况创建硬解码器,如果创建失败会使用软解。 

可以在引擎初始化时传入以下配置进行关闭: 

###### **typescript** 

RCRTCConfig.Builder config = RCRTCConfig.Builder.create(); config.enableHardwareDecoder(false); config.build(); RCRTCEngine.getInstance().init(context, config); 

##### **开启 / 关闭硬件高压缩编码** 

默认关闭,可以在引擎初始化时传入以下配置进行开启: 

###### **typescript** 

RCRTCConfig.Builder config = RCRTCConfig.Builder.create(); config.enableHardwareEncoderHighProfile(true); config.build(); RCRTCEngine.getInstance().init(context, config); 

提示 

开启硬件高压缩编码可能会引发兼容性问题,请谨慎使用。 

##### **配置硬件编码帧率** 

取值范围 0~30 帧,默认 30 帧。 

可以在引擎初始化时传入以下配置进行修改: 

###### **typescript** 

RCRTCConfig.Builder config = RCRTCConfig.Builder.create(); config.setHardwareEncoderFrameRate(25); // 修改硬件编码帧率为 25 帧 config.build(); RCRTCEngine.getInstance().init(context, config); 

##### **开启 / 关闭 采集 / 解码 到纹理** 

默认开启,可以在引擎初始化时传入以下配置进行关闭: 

- 27 - 

**typescript** 

RCRTCConfig.Builder config = RCRTCConfig.Builder.create(); config.enableEncoderTexture(false); // 修改为 yuv 方式采集。 config.build(); RCRTCEngine.getInstance().init(context, config); 

###### 提示 

关闭后,采集/解码将通过 YUV 数据的形式进行,通常建议 HarmonyOS 5.0 以下的设备关闭此配置以换来更好的兼 容性。 

### **房间管理** 

###### **自定义房间属性** 

如开发者需要存储并通知给其他人房间相关的业务信息,可调用 RCRTCRoom 下的 setRoomAttribute 来存储和扩散自定义 属性键值。 

##### **设置属性** 

###### **typescript** 

setRoomAttribute(key: string, value: string, message: MessageContent, callback: IRCRTCResultCallback): void; 

###### 参数说明: 

|参数|类型|说明|
|---|---|---|
|key|字符串|属性名称|
|value|字符串|属性值|
|message|MessageContent|是否在设置属性的时候携带消息内容,传空则不往房间中发送消息|
|callback|IRCRTCResultCallback|设置完成回调|
|示例代码:|||

###### **typescript** 

- 28 - 

room.setRoomAttribute(userId, jsonObject.toString(), null, { 

```arkts
onSuccess(): void { }, onFailed(errorCode: RTCErrorCode): void { } }); 
```

API 参考: 

setRoomAttribute 

##### **获取属性** 

###### **typescript** 

getRoomAttributes(attributeKeys: string[], callback: IRCRTCResultDataCallback<Map<string, string>>): void; 

###### 参数说明: 

|参数|类型|说明|
|---|---|---|
|attributeKeys|string[]|属性名称列表,如果传null则表示获取所有属 性值|
|callback|IRCRTCResultDataCallback<Map<string,|属性获取的结果回调|
||string>>||

示例代码: 

###### **typescript** 

```arkts
room.getRoomAttributes(null, { onSuccess(data: Map<string, string>): void { }, onFailed(errorCode: RTCErrorCode): void { } }); 
```

API 参考: 

getRoomAttributes 

##### **删除属性** 

- 29 - 

###### **typescript** 

deleteRoomAttributes(attributeKeys: string[], message: MessageContent, callback: IRCRTCResultCallback): void; 

###### 参数说明: 

|参数|类型|说明|
|---|---|---|
|attributeKeys|string[]|属性Key值列表|
|message|MessageContent|是否在设置属性的时候携带消息内容,传空则不往房间中发送消息|
|callback|IRCRTCResultCallback|删除完成回调callback|

示例代码: 

###### **typescript** 

```arkts
room.deleteRoomAttributes(attributes, null, { onSuccess(): void { }, onFailed(errorCode: RTCErrorCode): void { } }); 
```

API 参考: 

deleteRoomAttributes 

##### **属性变化回调** 

在设置和删除自定义房间属性时,如果设置了 MessageContent 参数,则房间内的其他用户可以通过 

IRCRTCRoomEventsListener 里面的房间自定义状态消息回调监听房间属性的改变,如果未设置 MessageContent 参数则 不会回调此监听方法。 

###### **typescript** 

onReceiveMessage(message: Message): void; 

###### 参数说明: 

参数 类型 说明 message Message 接收到其他人发送到 room 里的消息体 

- 30 - 

###### **基本操作** 

##### **创建 / 加入房间** 

调用 RCRTCEngine 下的 joinRoom 方法加入房间,如果该房间之前不存在,则会在调用时自动创建并加入。 

提示 

每个房间在创建之初,会由融云服务生成一个在用户全网唯一的 SessionId,可用于后台业务查询或与融云进行问题 沟通。当房间内的所有人退出或被服务器判定掉线后,此 Session 结束。之后即便再用相同的 RoomId 创建房 间,SessionId 也会更新为不同值。 

会议模式下,推荐使用不带 RCRTCRoomConfig 的接口 joinRoom(roomId: string): Promise<RCRTCRoom>: 

###### **typescript** 

###### try { 

const data = await RCRTCEngine.getInstance().joinRoom(roomId); 

// 成功后的逻辑处理 ... 

- } catch (errorCode: RTCErrorCode) { 

- // 由于 SDK 未初始化,网络异常等原因,造成的加入房间失败后的逻辑处理 ... 

- // 失败原因参考 code 的具体含义。 

- // 处理逻辑可以是过段时间重新加入,或给用户弹通知等。 

} 

###### 参数说明如下: 

|参数|类型|说明|
|---|---|---|
|roomId|字符串|房间唯一ID。支持大小写英文字母、数字、部分特殊符号+ = - _的组合方式 最长|
|||64个字符。|
|confg|RCRTCRoomConfg|房间配置。参见表格下方对RCRTCRoomConfg的说明。|
|返回值|Promise<RCRTCRoom>|加入房间的Promise|

RCRTCRoomConfig 为房间配置,包含以下设置: 

###### setRoomType : 指定房间类型 

- setUserDatas : 用户属性扩展信息。用户加入房间时可携带的扩展信息。服务端可以通过 人员管理 接口查询用户属性 信息。 

- setJoinType : 用户进行多端登录时的加入策略。假设当前账号已在其他端加入房间,设置为 RCRTCJoinType.KICK 会 导致在用户其他端加入房间时踢掉已在房间的同账号用户。设置为 RCRTCJoinType.REFUSE ,则会保留已在房间的同 账号用户的登录状态,当前尝试登陆的用户会返回加入失败。 

##### **退出房间** 

- 31 - 

1. 如果用户开启了视频采集,在调用 leaveRoom 之前必须手动关闭视频采集。 

###### **typescript** 

RCRTCEngine.getInstance().getDefaultVideoStream().stopCamera(); 

提示 离开房间接口(leaveRoom)不会自动关闭视频采集。如不主动关闭,可能会导致耗电量增加等问题。 

2. 调用 RCRTCEngine 下的 leaveRoom 接口离开房间,离开时 SDK 内部会自动取消所有已发布和订阅的资源。 

###### **typescript** 

```arkts
RCRTCEngine.getInstance().leaveRoom({ onSuccess(): void { }, onFailed(rtcErrorCode: RTCErrorCode): void { } }); 
```

###### **房间事件回调** 

应用程序可以通过 RCRTCRoom 对象的 registerRoomListener(IRCRTCRoomEventsListener eventsListener) 方法注 册一个 IRCRTCRoomEventsListener 监听器。 

注册监听器后,App 可以监听房间的的状态及资源变化。在会议模式下,参会的远端用户的状态变化都会触发通知。 

##### **状态相关** 

1. 远端参会用户加入通知: 

当有远端参会用户加入时触发。用户加入房间后才能发布资源,因此该回调代表远端参会用户刚刚加入,此时并无任何 资源发布,所以此刻也订阅不到该用户的任何媒体流。 

###### **typescript** 

onUserJoined(remoteUser: RCRTCRemoteUser): void 

2. 远端参会用户(或远端主播用户)离开通知: 

- 32 - 

当有远端参会用户(或远端主播用户)离开房间时触发,此时 SDK 会自动取消订阅该用户已发布的流,无需手动调用 unsubscribeStream。 

###### **typescript** 

onUserLeft(remoteUser: RCRTCRemoteUser): void; 

3. 远端参会用户(或远端主播用户)掉线通知: 

当有远端参会用户(或远端主播用户)掉线时触发,代表该用户意外与融云服务断连超过 1 分钟。网络不好、App 意 外崩溃或用户主动杀进程等情况,都会造成客户端与融云服务断连。如 1 分钟内没有恢复,则会被服务判定掉线,此时 SDK 会自动取消订阅该用户的所有资源,无需手动调用 unsubscribeStream。 

###### **typescript** 

(remoteUser: RCRTCRemoteUser): void; 

4. 远端参会用户(或远端主播用户)音频静默状态变更通知: 

当远端参会用户(或远端主播用户)调用了音频流的 mute 方法时触发。参数 mute 为远端参会用户(或远端主播用 户)更新后的值,true 代表音频静默,false 代表恢复正常。 

###### **typescript** 

onRemoteUserMuteAudio(remoteUser: RCRTCRemoteUser, stream: RCRTCInputStream, mute: boolean): void; 

5. 远端参会用户(或远端主播用户)视频静默状态变更通知: 

当远端参会用户(或远端主播用户)调用了视频流的 mute 方法时触发。参数 mute 为远端参会用户(或远端主播用 户)更新后的值,true 代表视频静默,false 代表恢复正常。 

###### **typescript** 

onRemoteUserMuteVideo(remoteUser: RCRTCRemoteUser, stream: RCRTCInputStream, mute: boolean): void; 

##### **资源相关** 

1. 远端参会用户(或远端主播用户)资源发布通知: 

当远端参会用户(或远端主播用户)发布资源时触发,streams 为该用户当前发布流的集合。从中可以获取发送人 (userId),流标签(tag),媒体类型(type),当前状态(state)等信息,也可以调用 subscribeStream 接 口,订阅其中的流。 

###### **typescript** 

- 33 - 

onRemoteUserPublishResource(remoteUser: RCRTCRemoteUser, streams: RCRTCInputStream[]): void; 

2. 远端参会用户(或远端主播用户)资源取消发布通知: 

当远端参会用户(或远端主播用户)取消发布资源时触发,接收到后 SDK 会自动取消订阅这些流。开发者也可以根据 这些流中的信息,来给用户做出相应的提示 

###### **typescript** 

onRemoteUserUnpublishResource(remoteUser: RCRTCRemoteUser, streams: RCRTCInputStream[]): void; 

##### **数据相关** 

1. 第一个关键帧到达通知: 

###### **typescript** 

onFirstRemoteVideoFrame(userId: string, tag: string): void; 

2. 房间自定义消息到达通知: 

###### **typescript** 

onReceiveMessage(message: Message): void; 

### **发布与订阅(会议)** 

###### **本地用户流** 

用户进入音视频房间后,想让其他人看见你的画面、听见你的声音,需要发布(Publish)本地资源。想看到别人的画面、听 见别人的声音,需要订阅(Subscribe)其他人已发布的资源。 

##### **发布** 

开发者可在 joinRoom 成功后返回的 RCRTCRoom 拿到 RCRTCLocalUser 对象中通过 getLocalUser 获取本地用户对象, 然后调用其中的 publishDefaultStreams 来发布本地默认音视频流。这里定义的默认音视频流,是指麦克风采集的音频和摄 像头采集的视频;也可以调用 publishStream 或 publishStreams 由开发者指定资源进行发布,比如单独发布音频或视频, 亦或发布媒体文件或屏幕共享流。 

- 34 - 

**typescript** 

// 发布默认音视频流,即麦克风、摄像头采集数据 try { await room.getLocalUser().publishDefaultStreams(); // 发布成功 } catch (errorCode: RTCErrorCode) { // 发布失败 } 

##### **取消发布** 

当需要取消发布时,可调用 RCRTCLocalUser 中的 unpublishDefaultStreams 来取消默认发布的音视频流;也可以调用 unpublishStream 或 unpublishStreams 由开发者指定资源进行取消发布。取消发布接口通常跟发布接口配对使用,但如 果是用户想要退出房间,则不需要调用取消发布方法,在调用退出房间接口时,SDK 内部会自动进行取消处理。 

###### **typescript** 

// 取消发布默认音视频流,即麦克风、摄像头采集数据 try { await room.getLocalUser().unpublishDefaultStreams(); // 取消发布成功 } catch (rtcErrorCode: RTCErrorCode) { // 取消发布失败 } 

###### **远端用户流** 

用户进入音视频房间后,想让其他人看见你的画面、听见你的声音,需要发布(Publish)本地资源。想看到别人的画面、听 见别人的声音,需要订阅(Subscribe)其他人已发布的资源。 

##### **订阅** 

用户的订阅需要在两个地方进行处理:一是在加入房间的成功回调里,需要遍历 RCRTCRoom#getRemoteUsers 得到房间 内已经存在用户发布的流,并订阅;二是在收到远端用户刚刚发布流的通知,即 onRemoteUserPublishResource 时订阅。 可调用 RCRTCLocalUser 中的 subscribeStream 或 subscribeStreams 来订阅单个或多个媒体流,如果远端用户发布的 视频流开启了大小流功能,可以通过视频流 RCRTCVideoInputStream 对象的 setStreamType 方法,来选择订阅大流或小 流(默认). 

参数说明: 

- 35 - 

参数 类型 

说明 

streams List<? extends RCRTCInputStream> 音视频流集合 返回值 Promise<void> 订阅结果的 Promise 示例代码: 

###### **typescript** 

```arkts
for (const inputStream of inputStreams) { if (inputStream.getMediaType() === RCRTCMediaType.VIDEO){ const videoInputStream = inputStream as RCRTCVideoInputStream; //如果未绑定过VideoView,则需要创建并绑定VideoView if (videoInputStream.getVideoView() === null) { const videoView = new VideoView(XXXActivity.this); videoInputStream.setVideoView(videoView); //添加到 Activity 布局中 videoViewManager.add(videoView); } } } try { await rtcRoom.getLocalUser().subscribeStreams(inputStreams); // 订阅成功 } catch (error: { failedStreams: RCRTCInputStream[], errorCode: RTCErrorCode }) { // 订阅失败 // 如果 SDK ≧ 5.3.4,error 会包含订阅失败的流列表和错误码。 // 如果 SDK < 5.3.4,error 仅包含错误码。 } 
```

##### **取消订阅** 

当需要取消订阅时,可调用 RCRTCLocalUser 中的 unsubscribeStream 或 unsubscribeStreams 来取消订阅一道流或多 道流。取消订阅接口通常跟订阅接口配对使用,但如果是用户想要退出房间,则不需要调用取消订阅方法,在调用退出房间接 口时,SDK 内部会自动进行取消处理。 

参数说明: 

|参数|类型|说明|
|---|---|---|
|streams|List<? extends RCRTCInputStream>|要取消订阅的音视频流|
|返回值|Promise<void>|取消订阅结果的Promise|
|示例代码|:||

###### **typescript** 

- 36 - 

try { 

await rtcRoom.getLocalUser().unsubscribeStreams(unPublishResource); // 取消成功 } catch (errorCode: RTCErrorCode) { // 取消失败 } 

API 参考: 

- void unsubscribeStream(RCRTCInputStream stream, IRCRTCResultCallback callBack); 

- void unsubscribeStreams(List<? extends RCRTCInputStream> streams, IRCRTCResultCallback callBack); 

### **音频管理** 

###### **混音** 

音视频 SDK 支持两种方式的混音,分别是从指定音频文件混音和用户传入音频数据混音。 

- 早于 5.1.11 版本的 SDK,因为底层逻辑用的是一个通道,所以不支持同时使用两种混音方式。 

- 5.1.11 及之后版本,支持两种方式同时混音。 

##### **前提条件** 

从网络音源混音的能力依赖 player 插件。SDK 需要使用以下插件将网络文件下载后播放。如有需要,请集成以下插件: 

###### **Groovy** 

dependencies { // x.y.z,请填写具体的 SDK 版本号,新集成用户建议使用 SDK 和插件的最新版。 

... implementation 'cn.rongcloud.sdk:player:x.y.z' // CDN 扩展库(可选) 

... } 

##### **从音频文件或网络音源混音** 

混音功能支持将用户自定义的音频数据、音频文件或网络音源与本地麦克风采集的音频数据进行混合。支持的用户自定义音频 文件或网络音源格式有:MP3、AAC、M4A、WAV。 

- 37 - 

加入房间并发布默认资源成功后,调用 RCRTCAudioMixer.startMix 方法使用指定的音频文件混音,退出房间前需要调用 RCRTCAudioMixer.stop 结束混音。 

###### **typescript** 

const audioFile = "/sdcard/emulated/0/music.mp3"; 

RCRTCAudioMixer.getInstance().startMix(audioFile, RCRTCAudioMixer.Mode.MIX, true, -1); 

// 调节混音音量(修改的是对端听到的声音音量) RCRTCAudioMixer.getInstance().setMixingVolume(80); // 调节本地播放音量(修改的是本端听到的声音音量) RCRTCAudioMixer.getInstance().setPlaybackVolume(80); // 获取混音文件播放总时长(ms),方法一 RCRTCAudioMixer.getInstance().getDurationMillis(); // 获取混音文件播放总时长(ms),方法二 RCRTCAudioMixer.getInstance().getDurationMillis(path: string); // 获取混音进度,例如 0.2 表示播放了 20% RCRTCAudioMixer.getInstance().getCurrentPosition(); // 调节混音进度,例如 0.2 表示调节至 20% 处开始播放 RCRTCAudioMixer.getInstance().seekTo(position: number); // 暂停混音 RCRTCAudioMixer.getInstance().pause(); // 继续混音 RCRTCAudioMixer.getInstance().resume(); // 停止混音 RCRTCAudioMixer.getInstance().stop(); 

###### 提示 

调用之前应用必须已经授予 ohos.permission.READ_USER_STORAGE 权限。 

- 如果 HarmonyOS 10 手机上授予了权限后也出现了混音失败,请参考知识库 为什么 HarmonyOS 10 无法使 用 startMix 进行混音? 

从 5.2.5.4 开始,SDK 支持先设置播放位置( seekTo ),再调用开始混音( startMix )。 

在混音开始前后均可以设置播放位置。如果希望从混音文件指定位置开始混音,建议先设置播放位置,再调用开始混音。 

- 38 - 

|参数|类型|说明|
|---|---|---|
|path|String|文件的绝对路径,如/sdcard/emulated/0/music.mp3,或者是assets文件, 格式如fle:///ohos_asset/music.mp3;如果是网络音源,则填音源地址。|
|mode|RCRTCAudioMixer.Mode|混音模式,Mode.MIX:将音频文件的音频数据与麦克风采集的数据混音发送至对 端,Mode.REPLACE:将麦克风采集的数据替换为音频文件的音频数据发送至对 端,Mode.NONE:不做任何操作,对端仅听到本地麦克风发送的声音|
|playBack|boolean|是否在本地播放混音音频文件|
|loopCount|int|loopCount > 0 :循环混音loopCount次;loopCount = -1: 无限循环;其 他取值:混音一次|

##### **从音频数据混音** 

加入房间并发布默认资源成功后首先调用 RCRTCAudioMixer.getInstance().startWrite(),再调用 RCRTCAudioMixer.write 方法混音原始音频数据,取消发布音频资源或离开房间后需要调用 RCRTCAudioMixer.getInstance().stopWrite() 方法停止混音。 

示例代码: 

###### **typescript** 

// 循环写入音频数据 

while (keepAlive) { 

RCRTCAudioMixer.getInstance().write(pcmData, 48000, 2, AudioFormat.ENCODING_PCM_16BIT, RCRTCAudioMixer.Mode.MIX); 

} // 结束时需要调用 stop 停止混音 RCRTCAudioMixer.getInstance().stop(); 

##### **混音设置声道** 

采用上述方式混音时,还可以调用 setAudioDualMonoMode 单独选择混音的左右声道。例如,您可以通过左右声道切换实 现原唱、伴唱切换,以满足卡拉 OK 场景下的需求(通过声道切换原唱、伴唱要求音源支持,即原唱、伴唱音轨分别位于两个 独立声道)。 

此接口默认左右声道同时混,设置即时生效。 

示例代码: 

###### **typescript** 

// 当左声道为伴奏音轨,按如下方式调用即可开启卡拉 OK 模式 

RCRTCAudioMixer.getInstance().setAudioDualMonoMode(AudioDualMonoMode.AUDIO_DUAL_MONO_L); 

- 39 - 

开始混音、暂停/继续混音、结束混音、混音文件已自动混流完成、实时混音进度等状态监听。 

##### **设置混音状态监听** 

###### **typescript** 

RCRTCAudioMixer.getInstance().setAudioMixingStateChangeListener({ 

- onMixEnd(): void { 

- // 此方法从 5.1.4 版本开始废弃 

- }, 

onStateChanged(state: MixingState): void { 

- // 此方法从 5.1.4 版本开始废弃 

- }, 

- /** 

- Added from 5.1.4 

- 混音状态变化 

* 

- @param state 变更后的状态 

- @param reason 状态变更的原因 

*/ 

onStateChanged(state: MixingState, reason: MixingStateReason): void { 

- if (state === MixingState.STOPPED){ 

- // 混音完成,可能的原因有: 

if (reason === MixingStateReason.ALL_LOOPS_COMPLETED){ 

- // 调用startMix方法时,传入的loopCount > 0,并且loopCount次数的混音已经完成 

- }else if (reason === MixingStateReason.ONE_LOOP_COMPLETED){ 

- // 调用startMix方法时,传入的loopCount < 0(无限循环)或 > 1,混音完成一次。接下来会继续自动开 

- 始下一次混音。 

- }else if (reason === MixingStateReason.STOPPED_BY_USER){ 

- // 调用stopMix方法停止混音 

} 

- } else if (state === MixingState.PLAY){ 

- // 开始混音,可能的原因有: 

if (reason === MixingStateReason.STARTED_BY_USER){ 

- // 调用了 startMix 方法开始混音 

- }else if (reason === MixingStateReason.START_NEW_LOOP){ 

- // 调用了 startMix 且传入的 loopCount < 0(无限循环)或 > 1 时,自动开始下一次混音。 

- }else if (reason === MixingStateReason.RESUMED_BY_USER){ 

- // 调用了 resume方法继续开始混音 

- }else if (reason === MixingStateReason.FILE_LOAD_FINISHED){ 

- // 本地或网络混音文件已加载完成(SDK 必须等待资源加载完成后才能播放混音文件),该回调要求 SDK 

- 版本 ≧ 5.2.5.4。 

} 

- } else if (state === MixingState.PAUSED){ 

暂停混音 为 i i 

- 40 - 

// 暂停混音,reason 为 MixingStateReason.PAUSED_BY_USER } }, /** * Added from 5.1.4 * 混音播放进度,默认 200 毫秒回调一次 * @param progress 播放进度 [0,1] */ onReportPlayingProgress(progress: number): void { // 非UI线程,更新UI需要切换线程 } }); 

##### **获取混音后的音频数据** 

通过注册监听 RCRTCEngine.getInstance().getDefaultAudioStream().setMixedAudioDataListener 获取本地混音后的 PCM 音频流数据。 

参数说明: 

参数 类型 说明 Listener IRCRTCAudioDataListener 本地混音后的 PCM 数据采集回调 

回调参数: 

回调参数 回调类型 说明 rtcAudioFrame RCRTCAudioFrame 混音后的音频 PCM 数据对象 

示例代码: 

###### **typescript** 

RCRTCEngine.getInstance().getDefaultAudioStream().setMixedAudioDataListener({ onAudioFrame(rcrtcAudioFrame: RCRTCAudioFrame): byte[] { return rcrtcAudioFrame.getBytes(); } }); 

###### **音频模式** 

为了满足不同场景对音频设置的需求,同时降低使用复杂度,融云对音频码率(音频通话质量)和音频模式(音频通话模式) 

- 41 - 

进行了接口合并封装,并重新设计对外提供音频码率 + 音频模式的接口,推荐使用最新接口。 

音频模式与音质合称为音频属性。SDK 针对不同使用场景设计了音频模式,并提供了三个音质选项。音频模式与音质可任意 配合使用。 

##### **了解音频模式** 

SDK 提供三种音频模式(audioScenario)。请在推荐场景下使用。 

###### 提示 

- SDK 设置音频模式时会修改 HarmonyOS AudioManager 的 mode。如果您的应用中也需要对 AudioManager 进行相关操作,您可能需要尽量避免两者发生冲突,否则会影响融云音视频 SDK 声音播放效 果。 

- 受 HarmonyOS AudioManager 的 mode 的特性影响,SDK 提供的 DEFAULT 模式比其他两种模式播放音 量相对较小。 

音频模式枚举 使用场景建议 DEFAULT **仅推荐通话,会议或类似场景下使用** 。如果在语聊房、音乐教学场景中使用 DEFAULT 模式,可能 会出现音乐音质差、伴奏音量高低不稳定的问题. MUSIC_CHATROOM **语聊房,音乐播放场景** 。不可在会议场景下使用 MUSIC_CHATROOM,否则会影响 VOIP 应用的 音频模式规则。 MUSIC_CLASSROOM **音乐教学场景** 。不建议在会议、语聊房场景中使用 MUSIC_CLASSROOM,否则有出现回声问题的 风险。 

##### **了解音质与码率** 

|音质枚举|码率|推荐使用场景|
|---|---|---|
|SPEECH|人声音质,编码码率最大值为32Kbps|通话,会议场景(默认)|
|MUSIC|标清音乐音质,编码码率最大值为64Kbps|语聊房,音乐播放场景|
|MUSIC_HIGH|高清音乐音质,编码码率最大值为128Kbps|音乐教学场景|

##### **如何匹配模式和音质** 

音频通话模式与音质可以任意组合,达到特殊场景需求。下表列出了几种常见场景推荐值,您也可以直接参考上文中的示例代 码。 

- 42 - 

AudioScenario 音频模式 AudioQuality 音质 

场景 

通话,会议场景(默认) DEFAULT SPEECH 语聊房,音乐播放场景 MUSIC_CHATROOM MUSIC 音乐教学场景 MUSIC_CLASSROOM MUSIC_HIGH 

###### 提示 

由于 DEFAULT 模式和其他两种模式在播放音量上存在差别,会导致切换前后播放音量不一致,因此不建议使用 DEFAULT 模式和其他两种模式连续切换。 

##### **设置音频场景与音频质量** 

SDK 在 RCRTCMicOutputStream 类中提供了 setAudioQuality 方法,用于设置音频场景 AudioScenario 与音频质量 AudioQuality。您可以在加入房间前或者加入房间后,通过 RCRTCEngine.getInstance().getDefaultAudioStream() 实 例进行调用设置。详情如下: 

音频通话质量可以和音频通话模式进行任意组合,达到特殊场景需求,以下示例代码为几种常见场景推荐值。 

###### **typescript** 

###### /** 

普通通话模式(普通音质模式), 满足正常音视频场景,人声音质,编码码率最大值为32Kbps。音量调节 '通话音量'。 */ 

RCRTCEngine.getInstance().getDefaultAudioStream().setAudioQuality(AudioQuality.SPEECH, AudioScenario.DEFAULT); 

###### /** 

音乐教室模式, 提升声音质量, 适用对乐器演奏音质要求较高的场景,高清音乐音质,编码码率最大值为128Kbps。此模式 下需要收听一端静音麦克风,音量调节 ’媒体音量‘。 

*/ 

RCRTCEngine.getInstance().getDefaultAudioStream().setAudioQuality(AudioQuality.MUSIC_HIGH, AudioScenario.MUSIC_CLASSROOM); 

###### /** 

音乐聊天室模式, 提升声音质量, 适用对音乐演唱要求较高的场景,高清音乐音质,编码码率最大值为128Kbps。音量调节 ' ' 媒体音量。 

###### */ 

RCRTCEngine.getInstance().getDefaultAudioStream().setAudioQuality(AudioQuality.MUSIC_HIGH, AudioScenario.MUSIC_CHATROOM); 

###### **流处理** 

- 43 - 

##### **本地音频流处理** 

SDK 提供了本地音频流发送前上报,用户可以利用上报的音频数据做变声、录音等处理。注册监听 RCRTCEngine.getInstance().getDefaultAudioStream().setRecordAudioDataListener 获取本地 PCM 音频流数据。 

参数说明: 

参数 类型 说明 Listener IRCRTCAudioDataListener 本地音频 PCM 数据采集回调 回调参数: 回调参数 回调类型 说明 rtcAudioFrame RCRTCAudioFrame 音频 PCM 数据对象 

示例代码: 

###### **typescript** 

RCRTCEngine.getInstance().getDefaultAudioStream().setRecordAudioDataListener({ onAudioFrame(rcrtcAudioFrame: RCRTCAudioFrame): byte[] { 

//回调线程:AudioRecordJavaThread return rcrtcAudioFrame.getBytes(); } }); 

##### **远端音频流处理** 

SDK 提供远端音频流接收后上报,用户可以利用上报的音频数据做变声,录音等处理。注册监听 RCRTCRoom.setRemoteAudioDataListener 获取远端 PCM 音频流数据。 

参数说明: 

参数 类型 说明 Listener IRCRTCAudioDataListener 远端音频数据回调 回调参数: 回调参数 回调类型 说明 rtcAudioFrame RCRTCAudioFrame 音频 PCM 数据对象 

示例代码: 

###### **typescript** 

- 44 - 

// `room` 为 joinRoom 成功后获得的房间对象 room.setRemoteAudioDataListener({ onAudioFrame(rcrtcAudioFrame: RCRTCAudioFrame): byte[] { return rcrtcAudioFrame.getBytes(); } }); 

###### **音量** 

本文介绍如何设置音频采集音量、耳返播放的音量以及如何对播放音频进行静音。 

本文不介绍混音音量控制。请另行参见「混音」文档。 

##### **设置采集音量** 

采集是指音频信号由采集设备(麦克风)采集,然后传输到发送端的过程。App 可通过 RCRTCMicOutputStream 的 adjustRecordingVolume 设置麦克风为音频源的音频输出流音量大小。 

###### **typescript** 

/** * 调整音量 * * @group 音频配置 * @param volume    0-200 */ void adjustRecordingVolume(int volume); 

App 需要调用 RCRTCEngine 下的 getDefaultAudioStream 方法,获取 RCRTCMicOutputStream 对象或可进行设置: 

###### **typescript** 

RCRTCEngine.getInstance().getDefaultAudioStream().adjustRecordingVolume(150); 

##### **调节远端播放音量** 

App 可以调用 RCRTCEngine 下的 adjustRemotePlaybackVolume 方法调节远端播放音量。音量范围为 [0-200],0 表示 静音。加入房间前后均可调节音量。该方法调节的是本地播放的所有远端用户混音后的音量。 

###### **typescript** 

- 45 - 

###### // 调节远端播放音量 

RCRTCEngine.getInstance().adjustRemotePlaybackVolume(150); 

int currentVolume = RCRTCEngine.getInstance().getRemotePlaybackVolume(); 

##### **静音本地音频流** 

媒体流对象都可以调用 RCRTCStream 接口提供的 mute(boolean mute) 方法设置是否静默。 

对于本地音频流,如果 mute 为 true 则不再发送本地资源,也不能播放,但不影响音频数据采集。 

###### **typescript** 

RCRTCEngine.getInstance().getDefaultAudioStream().mute(mute); 

##### **静音远端音频流** 

媒体流对象都可以调用 RCRTCStream 接口提供的 mute(boolean mute) 方法设置是否静默。 

对于远端音频流,如果 mute 为 true 则不再播放远端音频,但不影响远端音频数据接收。 

###### **typescript** 

for (RCRTCInputStream inputStream : inputStreams) { if (inputStream.getMediaType() == RCRTCMediaType.AUDIO){ RCRTCAudioInputStream audioInputStream = (RCRTCAudioInputStream) inputStream; audioInputStream.mute(true); } } 

##### **静音房间内全部远端音频流** 

App 需要在用户加入房间后,在当前房间对象 RCRTCRoom 上调用 muteAllRemoteAudio,设置为 true 不再播放远端音 频流。默认不开启。 

### **视频管理** 

###### **大小流** 

大小流模式是指在发布资源时上传一大一小两道视频流。 

- 46 - 

SDK 默认打开发布大小流功能,即每个用户在发布视频资源时自动发布大小两个视频流。小流的分辨率默认跟随大流。 

提示

在多人音视频通话过程中,大小流模式可有效减少下行带宽占用。订阅方可按需订阅小流。 

###### 小视频流与大视频流的分辨率对应关系如下: 

|大流分辨率|小流分辨率|比例|
|---|---|---|
|176X144|176X144|11:9|
|180X180|180X180|1:1|
|256X144|256X144|16:9|
|240X180|240X180|4:3|
|320X180|256X144|16:9|
|240X240|180X180|1:1|
|320X240|240X180|4:3|
|360X360|180X180|1:1|
|480X360|240X180|4:3|
|640X360|256X144|16:9|
|480X480|180X180|1:1|
|640X480|240X180|4:3|
|720X480|240X180|3:2|
|848X480|256X144|9:5|
|960X720|240X180|4:3|
|1280X720|256X144|16:9|
|1920X1080|256X144|16:9|

##### **发布方开关大小流** 

需要在加入房间前打开或关闭大小流。在加入房间后修改不生效。开启后,发布资源时会发布大小两道流。 

###### **typescript** 

RCRTCEngine.getInstance().getDefaultVideoStream().enableTinyStream(enable); 

- 47 - 

参数 

类型 

说明 

enableTinyStream boolean 大小流开关 默认开启 

##### **订阅方切换大小流** 

如果远端用户在加入房间前开启了大小流功能,本地在订阅远端视频流时可以通过 RCRTCVideoInputStream#setStreamType 方法选择订阅大流或小流。 

###### **typescript** 

for (const inputStream of inputStreams) { 

if (inputStream.getMediaType() === RCRTCMediaType.VIDEO){ 

const videoInputStream = inputStream as RCRTCVideoInputStream; 

- // 默认值是 NORMAL 即大流,这里演示设置成订阅小流的情况。 

videoInputStream.setStreamType(RCRTCStreamType.TINY); 

} 

} 

//设置好订阅大流或小流后,执行订阅操作,即完成了切换大小流操作 rtcRoom.getLocalUser().subscribeStreams(inputStreams, { onSuccess(): void { 

}, 

// 如果 SDK ≧ 5.3.4,您可以使用 IRCRTCResultDataCallback,onFailed 方法会返回订阅失败的流列表和错误码。 // 如果 SDK < 5.3.4,仅支持使用 IRCRTCResultCallback,onFailed 方法仅返回错误码。 

onFailed(failedStreams: RCRTCInputStream[], errorCode: RTCErrorCode): void { 

} 

}); 

###### **流处理** 

##### **本地视频流处理** 

注册本地视频采集监听 RCRTCVideoOutputStream.setVideoFrameListener ,获取本地摄像头采集的视频流数据。 

###### **typescript** 

- 48 - 

RCRTCEngine.getInstance().getDefaultVideoStream().setVideoFrameListener({ processVideoFrame(rtcVideoFrame: RCRTCVideoFrame): RCRTCVideoFrame { 

//使用数据进行美颜/录像等处理后,需要把数据再返回给SDK做发送 return rtcVideoFrame; } }); 

|参数 类型|说明|
|---|---|
|videoFrameListener IRCRTCVideoO|utputFrameListener 本地视频流回调|
|回调参数processVideoFrame说明: 回调参数 回调类型|说明|
|rtcVideoFrame RCRTCVideoFrame|调用RCRTCVideoFrame.getTextureId()或RCRTCVideoFrame.getData()处 理视频数据后,需设置RCRTCVideoFrame.setTextureId(int textureId)或 RCRTCVideoFrame.setData(byte[] data)给对象并返回|

##### **本地视频流静默** 

媒体流对象都可以调用 mute(boolean mute) 方法设置是否静默。对于本地视频流,如果 mute 为 true 则不再发送本地资 源,也不能渲染,但不影响视频数据采集。 

###### **typescript** 

RCRTCEngine.getInstance().getDefaultVideoStream().mute(mute); 

##### **远端视频流处理** 

注册监听 RCRTCVideoInputStream.setVideoFrameListener 获取远端视频流数据。 

###### **typescript** 

```arkts
RCRTCVideoInputStream.setVideoFrameListener({ onFrame(videoFrame: RCRTCRemoteVideoFrame): void { // 远端视频数据 } }); 
```

参数 类型 说明 videoFrameListener IRCRTCVideoInputFrameListener 远端视频流回调 

回调参数 onFrame 说明: 

- 49 - 

回调参数 回调类型 

说明 

videoFrame RCRTCRemoteVideoFrame 远端视频流数据,需要注意:不可以在当前回调中执行长时间耗时操作,否则 会造成渲染卡顿 

##### **远端视频流静默** 

媒体流对象都可以调用 mute(boolean mute) 方法设置是否静默。对于远端视频流,如果 mute 为 true 则不再渲染远端 流,但不影响远端视频数据接收。 

###### **typescript** 

for (const inputStream of inputStreams) { 

```arkts
if (inputStream.getMediaType() === RCRTCMediaType.VIDEO){ const videoInputStream = inputStream as RCRTCVideoInputStream; videoInputStream.mute(true); } } 
```

###### **分辨率 / 码率 / 帧率设置** 

您可以调用 RCRTCCameraOutputStream 下的 setVideoConfig 设置音视频流(大流)的分辨率、码率、和帧率。支持通 话过程中动态设置。 

调用 setTinyVideoConfig 可设置小流的分辨率、码率、和帧率。支持通话过程中动态设置。 

提示 

RCRTCCameraOutputStream 对象只能通过 RCRTCEngine 中的 getDefaultVideoStream 获取,且只能 在 IM 连接成功并调用 RCRTCEngine.init 方法之后调用,否则会返回空指针。 

视频参数对象通过 RCRTCVideoStreamConfig.Builder 来创建。 

##### **设置分辨率** 

默认情况下,SDK 使用默认分辨率 RESOLUTION_480_640。 

调用 setVideoResolution 设置音视频流的分辨率。 

###### **typescript** 

- 50 - 

RCRTCVideoStreamConfig config = RCRTCVideoStreamConfig.Builder.create() 

.setMinRate(200) .setMaxRate(900) .setVideoFps(RCRTCParamsType.RCRTCVideoFps.Fps_15) .setVideoResolution(RCRTCParamsType.RCRTCVideoResolution.RESOLUTION_480_640) .build(); RCRTCEngine.getInstance().getDefaultVideoStream().setVideoConfig(config); 

##### **设置码率** 

默认情况下,SDK 根据当前分辨率进行匹配,自动适用对应的默认最小和最大码率设置。在通话过程中,实际视频码率在最 小码率和最大码率之间根据网络情况浮动。 

您可以调整本端的最小和最大码率。调用 setMinRate 设置最小码率。调用 setMaxRate 设置最大码率。码率单位为 kbps。 

##### **设置帧率** 

默认情况下,SDK 使用默认帧率 Fps_15。 

调用 setVideoFps 设置帧率,支持的帧率为 Fps_10、Fps_15、Fps_24、Fps_30。 

##### **API 参考** 

setVideoConfig(RCRTCVideoStreamConfig config) 

setTinyVideoConfig(RCRTCVideoStreamConfig config) 

###### **对接第三方插件** 

您可以自行对接第三方 SDK。通过 SDK 提供的视频帧数据回调接口,自行对接第三方美颜 SDK,更加灵活。 

##### **步骤 1 :设置视频数据回调** 

通过 RCRTCVideoOutputStream.setVideoFrameListener 注册要处理的视频流的采集监听: 

###### **typescript** 

- 51 - 

RCRTCEngine.getInstance().getDefaultVideoStream().setVideoFrameListener({ 

processVideoFrame(rtcVideoFrame: RCRTCVideoFrame): RCRTCVideoFrame { 

- // 使用数据进行美颜/录像等处理后,需要把数据再返回给 SDK 做发送。 

(rtcVideoFrame); 

return rtcVideoFrame; } }); 

##### **步骤 2 :处理视频帧数据** 

###### **typescript** 

const imageFilter = mVideoFilterHandler.getCurrentImageFilter(); 

... 

// 调用 imageFilter 对视频进行美颜处理 rcrtcVideoFrame.setTextureId(imageFilter.draw(rcrtcVideoFrame.getWidth(), rcrtcVideoFrame.getHeight(), rcrtcVideoFrame.getTextureId())); 

###### **水印处理** 

融云支持在视频流上添加水印,适用于 App 客户端用户自主添加个性化水印。 

添加水印有两种控制方式,本文仅介绍方案一: 

- 方案一:使用客户端 SDK 提供的 setWatermark 方法添加图片水印。客户端发布的视频流即带有图片水印,因此订阅 该视频流的用户均会看到带水印的视频流。 

- 方案二:使用服务端 API 的 /rtc/mcu/config 接口,在服务端处理,添加时间戳水印、文字水印或图片水印。这种方式 支持为单人视频流或合流视频添加水印。本文不介绍服务端的处理方案,如有需要,请参见服务端文档。 

方案一适用于实现 App 客户端用户自主添加个性化水印;方案二更适用于由 App 添加统一风格的水印。 

客户端与服务端添加的水印相互独立。如果同时使用,则订阅合流的用户可能会看到水印叠加。 

##### **设置水印** 

RCRTCVideoOutputStream 内置了设置水印的接口,通过调用 setWatermark(Bitmap icon, RCRect rect) 方法即可实现 为相机、自定义文件、共享桌面采集到的视频流添加水印的功能。每一道视频流水印设置是独立的。 

###### **typescript** 

boolean setWatermark(Bitmap icon, RCRect rect); 

- 52 - 

必 参数 类型 填 说明 icon Bitmap 是 水印图片,传入 null 时则清除水印。 rect RCRTCRect 是 水印的位置和尺寸参数。 注意:参数取值范围 0 ~ 1,SDK 内部会根据视频分辨率计算水印实际 的像素位置和尺寸。 

rect 是归一化的,左上角为原点,范围 0~1。 

- x:水印 x 坐标。取值范围 0~1 浮点数。 

- y:水印 y 坐标。取值范围 0~1 浮点数。 

- width:水印的宽度,取值范围 0~1。例如,宽度是 480 × 0.2 = 96px 

- height:无需设置,SDK 内部会根据水印图片的宽高比自动计算一个合适的高度 

例如,当前视频的编码分辨率是 480(宽) × 640(高),且 rect 参数被您设置为(0.1f,0.1f,0.2f)。那么水印的左上 坐标点就是(480 × 0.1,640 × 0.1),即(48,64),水印的宽度是 480 × 0.2 = 96px,水印的高度会根据水印图片 的宽高比由 SDK 自动算出。 

##### **函数声明** 

###### **typescript** 

- /** * 设置水印 * * @param logoIcon 水印图片, 如果参数null, 移除水印 * @param rect     水印大小位置尺寸 * @return 水印设置是否成功 * <p> * added from 5.1.16 </br> * rect 是归一化的,左上角为原点,范围 0~1 

- x: 水印x坐标 :取值范围0~1浮点数 

- y: 水印y坐标 :取值范围0~1浮点数 

- width: 水印的宽度,取值范围 0~1 exp:宽度是 480 × 0.2 = 96px 

- height: 无需设置,SDK内部会根据水印图片的宽高比自动计算一个合适的高度 

- 例如: 当前视频的编码分辨率是 480 × 640,且 rect 参数被您设置为(0.1,0.1,0.2) * 那么水印的左上坐标点就是(480 × 0.1,640 × 0.1)即(48,64) 

- 水印的宽度是 480 × 0.2 = 96px,水印的高度会根据水印图片的宽高比由 SDK 自动算出 */ 

boolean setWatermark(Bitmap logoIcon, RCRTCRect rect); 

##### **示例代码** 

###### **typescript** 

- 53 - 

###### //添加水印 

Bitmap icon = BitmapFactory.decodeFile(path); 

RCRTCRect rect = new RCRTCRect(0.5f, 0.5f, 0.2f); 

boolean ret = RCRTCEngine.getInstance().getDefaultVideoStream().setWatermark(icon, rect); 

###### // 清除水印 

boolean ret = RCRTCEngine.getInstance().getDefaultVideoStream().setWatermark(null, rect); 

##### **注意事项** 

- 添加水印图片不宜过大。建议图片宽高均不超过 200px,否则会影响图片转 Bitmap 的生成。 

- 禁止程序循环反复调用添加/清除水印接口。 

#### **状态码** 

- -1 

UnknownError 

###### 未知错误。 

**排查建议** :如果一直出现此问题,请提交工单与我们联系,并附上必要的的信息,用户的 App key 和 用户 ID。 

0 

OK 

成功。 

###### **排查建议** :无需处理。 

###### 50000 

RongRTCCodeSignalServ 

erNotConnect 

初始化失败或 IM 未连接。 

###### **排查建议** : 

1. 确认是否调用了 RongCoreClient.connect()连接方法,并且走了 onSuccess 回调。 

2. 可以调用 RongCoreClient.getInstance().getCurrentConnectionStatus()== 

   - IRongCoreListener.ConnectionStatusListener.ConnectionStatus.CONNECTED 判断当前是否处于连接状态。 

###### 50001 

RongRTCCodeParameter 

Error 

接口参数错误。 

**排查建议** :请确认调用接口传入的参数是否为空。 

- 54 - 

###### 50002 

###### RongRTCCodeJoinRepeat 

edRoom 

加入相同房间错误,表示用户在客户端重复加入相同的房间。 

**排查建议** :可以通过判断 RCRTCEngine.getInstance().getRoom()是否等于 null 来确认当前用户是否已经音视频房间 中。 

###### 50003 

RongRTCCodeNotInRoo 

m 

调用房间内接口时,不在房间中。 

###### **排查建议** : 

1. 可以通过判断 RCRTCEngine.getInstance().getRoom()是否等于 null 来确认当前用户是否已经音视频房间中。 

2. 如果需要确认没有加入房间的原因,请提交工单与我们联系,并且附上 App key 、用户 ID、房间 ID、问题时间等信 息。 

###### 50004 

RongRTCCodeVoIPNotAv 

ailable 

未开通音视频服务,请到融云控制台开启。 

**排查建议** 请在融云控制台开启音视频服务,如果您无法开启,请联系您的专属商务进行开启,开启之后,卸载重装应用重 试。 

###### 50006 

RongRTCCodeRTCTokenI 

sNull 

RTC Token 为空。 

**排查建议** :请提交工单与我们联系,并且附上 App key 、用户 ID、房间 ID、问题时间等信息。 

###### 50007 

ILLEGALSTATE 

非法状态。 

###### **排查建议** : 

1. 请确认调用音视频接口之前是否调用了 RCRTCEngine.getInstance().init 进行初始化音视频引擎。 

2. 检查代码,确认调用 joinRoom 时传入的 RCRTCRoomType 为 MEETING 时需要调用 publishStreams 接口发布 资源。 

###### 50010 

RongRTCCodeHttpTimeo 

utError 

HTTP 请求超时。 

- 55 - 

**排查建议** :稍后重试或者更换稳定网络后重试,仍然出现请提交工单与我们联系,并附上必要的的信息,如 App key,用 户 ID,房间 ID,问题发生时间等。 

###### 50011 

RongRTCCodeHttpError 

HTTP 响应错误(含 500,404,405 等错误)。 

**排查建议** :稍后重试或者更换稳定网络后重试,仍然出现请提交工单与我们联系,并附上必要的的信息,如 App key,用 户 ID,房间 ID,问题发生时间等。 

###### 50012 

RongRTCCodeNetworkU 

navailable 

网络不可用。 

**排查建议** :请确认网络是否可用。 

###### 50013 

InvalIDProtocolMessage 

Error 

SDK 内部解析协议消息无效错误。 

**排查建议** :请提交工单与我们联系,并附上必要的的信息,如 App key,用户 ID,房间 ID,问题发生时间等。 

###### 50021 

RongRTCCodeSessionNe 

gotiateOfferError 

本地会话协商错误。 

**排查建议** :请提交工单与我们联系,并附上必要的的信息,如 App key,用户 ID,房间 ID,问题发生时间等。 

###### 50022 

RongRTCCodeSessionNe 

gotiateSetRemoteError 

远端会话协商错误。 

**排查建议** :请提交工单与我们联系,并附上必要的的信息,如 App key,用户 ID,房间 ID,问题发生时间等。 

###### 50023 

RongRTCCodePublishStr 

eamsHasReachedMaxCo 

unt 

发布的流的个数已经到达上限。 

**排查建议** :默认发布资源个数上线为30,如需要提高上限请提交工单与我们联系,并附上必要的的信息,如 App key,用 户 ID,房间 ID,问题发生时间等。 

50027 

- 56 - 

INCOMPATIBLE_WITH_PR IVATE_SERVER 公有云 SDK 不能访问私有云服务。 

**排查建议** :请检查 SDK 的集成方式,私有云服务 SDK 需要在eportal 平台下载。 

###### 50028 

RCRTCCodeProxyUnavail ableError 无法使用设置的代理服务转发资源。 

**排查建议** :请提交工单与我们联系,并附上必要的的信息,如 App key,用户 ID,房间 ID,问题发生时间等。 

###### 50030 

RongRTCCodeSubscribe NotExistResources 订阅不存在的资源。 

**排查建议** :请检查订阅的资源是否为当前房间远端用户发布的资源,仍无法解决问题,请提交工单与我们联系,并附上必 要的的信息,如 App key,用户 ID,房间 ID,问题发生时间等。 

###### 50032 

RongRTCCodeUnsubscri beNotExistResources 

取消订阅不存在的资源。 

**排查建议** :请检查订阅的资源是否为当前房间远端用户发布的资源,仍无法解决问题,请提交工单与我们联系,并附上必 要的的信息,如 App key,用户 ID,房间 ID,问题发生时间等。 

###### 50065 

RongRTCCodeRTCConne ctionIsNull 

当前PeerConnection连接不可用 

**排查建议** :请提交工单与我们联系,并附上必要的的信息,如 App key,用户 ID,房间 ID,问题发生时间等。 

50066 

PublishMediaStreamIsNu ll 发布的 Stream 为空。 

**排查建议** :请检查发布资源时对传入的 RCRTCOutputStream 是否为空。 

50069 

JsonParseError 解析 JSON 错误。 

**排查建议** :请提交工单与我们联系,并附上必要的的信息,如 App key,用户 ID,房间 ID,问题发生时间等。 

50071 

- 57 - 

ConnectionAddStreamFa 

iled 

PeerConnection 添加Stream失败。 

**排查建议** :请提交工单与我们联系,并附上必要的的信息,如 App key,用户 ID,房间 ID,问题发生时间等。 

50072 

RongRTCCodeIMError IM 错误。 

**排查建议** :请提交工单与我们联系,并附上必要的的信息,如 App key,用户 ID,房间 ID,问题发生时间等。 

50074 

NOT_JOINED_MAIN_ROO M 

没有加入主房间错误。 

**排查建议** :请先通过 RCRTCEngine.getInstance().getRoom()确认用户是否在音视频主房间内,仍无法解决问题,请提 交工单与我们联系,并附上必要的的信息,如 App key,用户 ID,房间 ID,问题发生时间等。 

50075 

OTHER_ROOM_ID_CANN OT_THE_MAIN_ROOM 操作的副房间号码和主房间号码一致错误。 

**排查建议** :请检查加入、离开副房间接口传入的房间 ID 是否与 

RCRTCEngine.getInstance().getRoom().getRoomID()一致。 

50076 

CANCELLED_INVITATION _DOES_NOT_EXIST 取消的跨房间连麦请求不存在。 

**排查建议** :请确认调用 cancelRequestJoinOtherRoom 时传入的 inviteeRoomID 、inviteeUserID 和收到的请求跨房 间连麦的信息一致。 

50077 

RESPONDING_INVITATIO N_DOES_NOT_EXIST 

响应的跨房间连麦请求不存在。 

**排查建议** :确认调用 responseJoinOtherRoom 方法时传入的 inviterRoomID 、inviterUserID 和收到的请求跨房间连 麦信息一致。 

50079 

MCU_PUBLISH_LIST_IS_N 

ULL 

服务端返回的 mcuPublishList 为空。 

- 58 - 

**排查建议** :请检查调用 joinRoom 时传入的 RCRTCRoomType 是否为 LIVE_AUDIO_VIDEO 或者 LIVE_AUDIO,如果检 查没问题,请提交工单与我们联系,并附上必要的的信息,如 App key,用户 ID,房间 ID,问题发生时间等。 

###### 50100 

RECONNECT_ERROR 自动重连异常。 

**排查建议** :请提交工单与我们联系,并附上必要的的信息,如 App key,用户 ID,房间 ID,问题发生时间等。 

###### 51000 

HARDWARE_VIDEO_ENC ODER_INIT_ERROR 视频硬编码初始化失败。 

**排查建议** :视频硬编码初始化失败,SDK内部默认切换到软编码,应用层无需处理。 

51001 

HARDWARE_VIDEO_ENC ODER_ERROR 视频硬编码过程中失败。 

**排查建议** :视频硬编码过程中失败,SDK内部默认切换到软编码,应用层无需处理。 

###### 51002 

HARDWARE_VIDEO_DEC ODER_INIT_ERROR 视频硬解码初始化失败。 

**排查建议** :视频硬解码初始化失败,SDK内部默认切换到软解码,应用层无需处理。 

###### 51003 

HARDWARE_VIDEO_DEC ODER_ERROR 视频硬解码过程中失败。 

**排查建议** :视频硬解码过程中失败,SDK内部默认切换到软解码,应用层无需处理。 

###### 51006 

OPEN_CAMERA_FAILED 

打开摄像头时出现未知错误。 

**排查建议** :请提交工单与我们联系,并附上必要的的信息,如 App key,用户 ID,房间 ID,问题发生时间等。 

###### 51007 

RTC_INIT_TIMEOUT 初始化 RTCLib 超时。 

**排查建议** :请提交工单与我们联系,并附上必要的的信息,如 App key,用户 ID,房间 ID,问题发生时间等。 

51008 

- 59 - 

OPEN_CAMERA_NO_PER MISSION 未授予 Camera 权限。 

###### **排查建议** :请检查是否动态获取了 Camera 权限。 

51100 

CREATE_ANSWER_FAILU 

RE 

创建 SDP Answer 失败。 

**排查建议** :请提交工单与我们联系,并附上必要的的信息,如 App key,用户 ID,房间 ID,问题发生时间等。 

###### 51200 

CAMERA_IS_RELEASED 

CameraManager 已被释放。 

**排查建议** :请提交工单与我们联系,并附上必要的的信息,如 App key,用户 ID,房间 ID,问题发生时间等。 

###### 51201 

CANCEL_OPERATOR 取消操作。 

**排查建议** :发布资源还未返回成功,调用了离开房间或者反初始化的接口,请确保发布资源接口返回成功后再调用离开房 间或者反初始化的接口。 

51202 

AUDIO_MANAGER_IS_RE LEASED AudioManager 已被释放。 

**排查建议** :请提交工单与我们联系,并附上必要的的信息,如 App key,用户 ID,房间 ID,问题发生时间等。 

51203 

STOP_CAMERA_FAILED 

Camera 释放失败。 

**排查建议** :请提交工单与我们联系,并附上必要的的信息,如 App key,用户 ID,房间 ID,问题发生时间等。 

###### 51205 

START_SCREEN_CAPTUR 

E_FIRST 必须先启动屏幕捕获。 

**排查建议** :请确认调用 startCaptureAudio 前是否先调用了 startCaptureScreen 。 

54001 

PLAYER_MODULE_NPT_F OUND 

- 60 - 

没有集成 Player SDK。 

**排查建议** :请检查是否有集成 Player 插件 

###### 54002 

CDN_INFO_VIDEO_INTER RUPT 

服务挂掉,视频中断,一般是视频源异常或者不支持的视频类型。 

**排查建议** :检查视频源是否正常,确认视频格式融云是否支持。 

###### 54003 

CDN_INNER_ERROR 

CDN 内部错误。 

**排查建议** :请提交工单与我们联系,并附上必要的的信息,如 App key,用户 ID,房间 ID,问题发生时间等。 

54008 

CDN_INFO_VIDEO_INTER RUPT 数据连接中断 或 音视频源格式不支持。 

**排查建议** :检查视频源是否正常,确认视频格式融云是否支持。 

54009 

PLAYER_MODULE_INIT_E RROR 

初始化 Player 模块异常。 

**排查建议** :请提交工单与我们联系,并附上必要的的信息,如 App key,用户 ID,房间 ID,问题发生时间等。 

###### 54010 

SCREEN_SHARE_NO_PER MISSION_ERROR 获取屏幕共享权限失败。 

**排查建议** :请提交工单与我们联系,并附上必要的的信息,如 App key,用户 ID,房间 ID,问题发生时间等。 

###### 54011 

SCREEN_SHARE_ALREAD Y_CAPTURE 已经开启录屏功能。 

**排查建议** :已经调用过 startCaptureScreen 再次调用报错,可以第一次调用 startCaptureScreen 成功添加变量记 录,再次调用进行变量判断,如果调用过就不用再调用。 

###### 54012 

START_PRETEST_HARD WARE_FAILED 开始通话前质量检测失败。 

- 61 - 

**排查建议** : 

1. 请检查麦克风权限正常授予,并且麦克风是打开的。 

2. 请确认是否是等待第一次 startEchoTest 返回结果再调用的 startEchoTest 接口。 

###### 55002 

SAME_ROLE_ERROR 

切换的角色和当前角色相同错误。 

###### **排查建议** :请确保用户切换的身份不是当前身份。 

###### 56000 

SERVER_NOT_CONFIG_ WISSE Server 没有配置 Wisse。 

**排查建议** :需要您在融云控制台配置 Wisse 信息。 

###### 56001 

RTC_PROBE_TEST_NOT_ 

START 

RTC 网络探测未开始。 

**排查建议** :请检查接口调用的时机,用户需要在调用开始网络探测接口后,根据业务需求调用结束网络探测接口。 

###### 56002 

RTC_PROBE_TEST_START 

ED 

RTC 网络探测已开始。 

**排查建议** :请检查接口调用时机,不要重复调用该接口。 

###### 56003 

RTC_ICE_DISCONNECT 

RTC 通道连接断开。 

**排查建议** :请检查是否使用了 vpn 或者有什么特殊的网络策略,切换网络试下是否正常,仍无法解决问题,请提交工单与 我们联系,并附上必要的的信息,如 App key,用户 ID,房间 ID,问题发生时间等。 

###### 56004 

RTC_PROBE_INTERRUPT_ 

BY_INTERNAL 

RTC 网络探测被中断。 

**排查建议** :请提交工单与我们联系,并附上必要的的信息,如 App key,用户 ID,房间 ID,问题发生时间等。 

###### 56005 

ILLEGAL_OPERATION_FO 

R_JOINING 

- 62 - 

由于当前正处在加入房间过程中,不允许其他操作。 

**排查建议** :SDK 会使用默认的内部参数连接,一般不影响正常使用。 

###### 56006 

RCRTCCodeSEILengthRe achToLimit SEI 数据长度超出限制 4096 字节。 

**排查建议** :请检查接口传入的参数不要超出 4096 个字节。 

###### 56007 

RCRTCCodeSEIChannelN otExist 

SEI 通道未建立,请检查是否开启 SEI,或者发布音视频。 

###### **排查建议** : 

1. 请先检查是否调用了 cn.rongcloud.rtc.api.RCRTCLocalUser#setEnableSEI 开启了 SEI 功能。 

2. 请再检查本地是否有发布音视频资源。 

###### 56008 

RCRTCCodeSEISendUnk 

nownError 

SEI 发送失败。 

**排查建议** :请提交工单与我们联系,并附上必要的的信息,如 App key,用户 ID,房间 ID,问题发生时间等。 

###### 56009 

RCRTCCodeSEISendTime 

PerSecondReachToLimit 

SEI 频率超出限制,1秒内不超过 30 次。 

**排查建议** :请检查 SEI 发送的频率,不超过 1 秒钟 30 次。 

###### 57001 

PERMISSION_CAMERA_N OT__GRANTED 未授予相机权限。 

**排查建议** :请检查是否有动态获取成功相机权限。 

57002 

PERMISSION_AUDIO_NO T__GRANTED 未授予麦克风权限。 

**排查建议** :请检查是否有动态获取成功麦克风权限。 

- 63 - 

57003 

PERMISSION_READ_NOT __GRANTED 未授予可读权限。 

###### **排查建议** :请检查是否有动态获取成功可读权限。 

57004 

PERMISSION_WRITE_NO T__GRANTED 未授予可写权限。 

###### **排查建议** :请检查是否有动态获取成功可写权限。 

57005 

PERMISSION_BLUETOOT 

H_CONNECT_NOT__GRA 

NTED 

未授予蓝牙连接权限。 

**排查建议** :请检查是否有动态获取成功蓝牙连接权限。 

57006 

RCRTCCodeRTCPingSend 

RTC Ping 错误。 

**排查建议** :请检查您的网络是否正常,可以换个网络试试。 

57007 

INIT_AUDIOTRACK_FAILE 

D 

初始化 AudioTrack 失败。 

**排查建议** :请提交工单与我们联系,并附上必要的的信息,如 App key,用户 ID,房间 ID,问题发生时间等。 

###### 57008 

INIT_ADM_FAILED 

初始化 AudioDeviceManager 失败。 

**排查建议** :请提交工单与我们联系,并附上必要的的信息,如 App key,用户 ID,房间 ID,问题发生时间等。 

- 64 -
