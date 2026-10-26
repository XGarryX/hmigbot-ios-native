# 产品概述 

更新时间: 2024/09/11 11:35:13 

## 云平台概述 

云屋云平台覆盖全球200多个国家和地区和国内几十家运营商网络,可支持百万人同时在线,平台采用集群机制,99.99% 高可用。 

## 私有化部署 

可以在用户自有网络进行整套系统的私有化部署,适用于金融、军队、政府等安全性要求较高的场景。 

## 技术优势 

- 高保真、高还原度的语音效果,支持智能回声消除、自动增益和噪声抑制。 

- 视频传输支持动态网络流控和丢包补偿,在低带宽的较差网络下也能保障视频的清晰流畅。 平台稳定可靠,支持大并发下的高可用性。 

## 平台兼容 

支持iOS、Android、Web、Windows、MacOS、Linux、小程序、Flutter等全平台互通,支持Chrome、Safari、Firefox等主流 浏览器,适配了5000多款不同的移动终端。详情见下表: 

|平台|支持版本|支持架构|
|---|---|---|
|Android|4.2 及以上版本|armeabi-v7a arm64-v8a x86 x86_64|
|iOS|8.0 及以上版本|armv7 arm64|
|HarmonyOS|NEXT DB1及以上版本|arm64-v8a x86_64|
|Windows ActiveX|Vista 及以上版本|x86|
|Windows c++|Vista 及以上版本|x86 x86_64|
|macOS|10.11 及以上版本|x86_64|
|Linux|CentOS:7 及以上版本 Ubuntu:12.04 及以上版本 Redhat:7 及以上版本 麒麟 统信UOS|x86_64 arm64|
|Electron|Electron 5.0.0 及以上 Mac 11及以上 win7 及以上|macOS: x86_64 Windows: x86_64、x86|
|小程序|微信 7.0.4 及以上 详见 浏览器兼容性说明|-|

|~~Web~~ 平台|~~详见 Web SDK浏览器兼容性说明~~ 支持版本|~~-~~ 支持架构|
|---|---|---|
|网页插件|~~Windows:~~ IE:8.0 及以上 Chrome:44 及以下|-|
|Flutter|Flutter 2.0.0 及以上 iOS 11.0 及以上 Android 4.4 及以上|-|
|uni-app|HBuilderX 3.0.0 及以上 iOS 11.0 及以上 Android 4.4 及以上|-|

## 特性指标 

|特性|指标|
|---|---|
|标准SDK包体积|安装包增量大小如下: iOS(arm64):24.3MB Android(arm64):25.1MB HarmonyOS(arm64-v8a):17.5MB macOS(x86_64):26.8MB Windows(x86):19.4 MB Linux(x86_64):20.2 MB|
|仅音视频SDK包体积|安装包增量大小如下: iOS(arm64):6.3MB Android(arm64):6.31MB|
||可联系商务获取。|
|多人音视频|支持 4000 路以上实时音视频互动 支持最大同时开麦32人|
|多视频设备|单方最大支持8个视频设备,方便类似远程医疗这种多视角应用|
|视频质量|最高支持 4K 分辨率、 1~60 帧率|
|音频质量|音频采样率:16 kHz ~ 48 kHz 回声消除:32方同时讲话 支持单、双声道|
|低延迟|正常网络延时在 200 ms 左右|
|海量并发|支持同时向多方直播平台推流,实现多平台同播、海量用户观看|

# 主要功能 

更新时间: 2024/09/11 11:35:13 

## 基本功能 

|功能|功能说明|典型场景|
|---|---|---|
|音视频|多方同时音视频交互;支持多摄像头,网络 摄像头,大小流,在互联网即可体验会议室 级的逼真效果。|音视频会议 音视频客服|
|录制|可在会议进行的任意时间进行本地录制或云 端录制。|金融双录 互动直播|

## 进阶功能 

进阶功能是云屋SDK提供的各类音视频高级功能,帮助开发者实现特殊场景中的功能。 

|功能|功能说明|典型场景|
|---|---|---|
|屏幕共享|屏幕分享、远程协助。|会议中分享桌面软件或文档|
|影音共享|本地音视频文件远程与本地同步观看。|远程教学的视频案例分析 金融业务的风险播报|
|自定义音频数据|支持第三方音频源的音频输入,例如本地音 频流、第三方音频采集模块。提高音频链路 模块之间的灵活性。具有定制能力的客户可 以根据自己需要实现音频采集模块并能通过 云屋SDK进行音频传输。|语音处理 非标音频设备接入|
|自定义视频数据|支持多格式的自定义的视频源输入,满足多 场景的非摄像头的视频源的输入,例如自定 义视频文件、外接视频设备、自定义的美颜 库或有前处理库等。丰富互动直播、视频会 议等场景的用户体验。|自定义数据输入源 图像识别|
|房间消息|可在会议房间内进行实时文字消息互动,既 可选择房间内全部用户,也可向特定用户发 起私聊。|互动直播|
|房间/成员属性|可设置会议房间属性和房间内人员属性。|房间/成员属性|

# 关键词 

更新时间: 2024/09/11 11:35:13 

## SDK管理平台 

是云屋提供给SDK注册用户的管理平台。 可以进行帐户管理、项目管理、录像管理、队列管理、 通信记录查询、用量监控 等操作。 

点此注册一个账号,或者联系商务代为开通,或在网站咨询客服。 

## App ID 

用于区分不同的项目。每个项目都有属于自己唯一的App ID,不同App ID的项目完全独立,无法相互通信。 可以通过管理平台中的“项目管理”来创建App ID和维护相关配置。 

## App Secret 

App ID对应的密码,可登录云屋管理后台修改。 

## token 

云屋提供的token生成器生成的授权令牌。它具有动态性、时效性,可以替换appSecret用于登录鉴权。 

## 房间 

平台当前提供的音视频、白板、屏幕共享、IM群聊服务都是基于房间的,在使用这些服务之前,必须要先创建房间,只有 加入到同一个房间的用户才能够使用这些业务互相通信。房间创建后如果不主动销毁将会长期有效。 

## 房间号 

房间的唯一标识,用户需要先调用创建房间的api,然后在创建成功的回调通知中获取该房间的信息结构体。房间号来自该 结构体。 

## UserID 

用户ID,在登录和加入房间时传入,用于标识不同的用户。 同一个项目下的UserID需要保证唯一。 

## 发布视频流 

用户加入房间后,可以向房间内的其他用户发送本地采集的音视频数据流,也就是发布视频流。 

## 订阅视频流 

用户加入房间后,可以选择接收房间内其他用户发布的音视频数据流,也就是订阅视频流。 

## 大小流模式 

大小流指视频大流和视频小流。发布端可以开启大小流模式,同时发送大流和小流,订阅端根据自己的网络情况选择接收 大流或小流。大流和小流是一个相对的概念,通常小流占用的带宽会低于大流,适用于网络较差的场景。PC平台性能通常 较强,最多可以支持发布3个不同大小的视频流,移动平台只支持发布一大一小两个视频流。 

云端录制 

云端录制 

在服务器上对房间内的音视频、白板、屏幕共享等通讯内容进行录制,支持自定义录制内容和布局,录制文件在服务器保 存,可以通过API下载到本地。 

## 透明通道 

用于多个客户端之间传递用户的自定义内容,支持文件和信令两种模式,透明通道可以在房间外使用。 

## cookie 

指接口cookie参数,提供给业务层的命令上下文本地缓存机制(cookie不会在网络上传输)。 在命令响应回调接口里传回 给业务层,回调之后cookie数据就会自动消毁。 

用法举例:业务层分别向A、B各发一条消息(将目标用户的id存在cookie里), 在失败回调接口里可从cookie取回用户 id, 就能知道发给谁的消息失败了。 

# 实时音视频计费 

更新时间: 2024/09/11 11:35:13 

关于云屋如何按月统计使用语音通话、视频通话、云端录制的计费说明。 

## 费用组成 

视频单价按照集合分辨率分为5个档位,分档定价。基础的计费公式如下: 

费用 = 音频时长用量 × 音频单价 + 各档位视频的时长用量 × 相应视频单价 

### 时长用量 

音频:语音通信按照分钟数和人数进行收费,通话费用=音频通信每分钟价格*总通话分钟数,如用户有接收视频,则不计 算音频时长,仅计算视频时长。 

视频:按照集合分辨率计费,即以接收端订阅的所有视频流的分辨率之和为准,仅计算接收端时长,不计算发送端时长。 屏幕共享和影音播放都按一路视频计算。 

其他:按分钟计费,不足一分钟的记为一分钟。预充值形式,账户实时扣费 

### 单价 

音视频时长用量的单价如下: 

|用量类型|单价(元/千分钟)|
|---|---|
|音频|5.5|
|视频(SD)|12|
|视频(HD)|20|
|视频(HD+)|50|
|视频(2K)|90|
|视频(2K+)|250|

根据用户接收到的所有视频的集合分辨率,将视频分为如下5个类型并分别计算各类型视频的费用: 

|视频用量类型|用户订阅视频的集合分辨率|
|---|---|
|视频(SD)|集合分辨率≤307,200(640×480)|
|视频(HD)|307,200(640×480)<集合分辨率≤921,600(1280×720)|
|视频(HD+)|921,600(1280×720)<集合分辨率≤2,073,600(1920×1080)|
|视频(2K)|2,073,600 (1920×1080) <集合分辨率≤3,686,400(2560×1440)|
|视频(2K+)|3,686,400(2560×1440)<集合分辨率≤8,847,360(4096×2160)|

##### 说明: 

例如,用户A同时订阅两路分辨率为960×720的视频流,则该用户订阅的视频集合分辨率为 960×720+960×720=1,382,400,其 视频用量按视频(HD+)类型的单价计费。 

计费示例 

本节说明如何计算视频的集合分辨率、每种服务类型的时长用量以及相关费用。 

##### 说明: 

假设有5位用户同时加入一个房间,并且进行了60分钟的音视频互动。 

在音视频互动中,有3位用户(A、B和C)发布了自己的视频,其中每位用户的视频分辨率为960×720。另外2位用户(D和E)订阅 了他们的视频流。此外,用户A向房间内的所有其他用户共享了自己的屏幕,屏幕共享流的分辨率均为1920×1080。 

### 计算视频的集合分辨率 

#### 下表展示了如何计算每位用户订阅视频流的集合分辨率,以确定各用户视频用量的类型和单价: 

|用户|订阅的视频流|视频的集合分辨率|总分辨率 视频|用量类型|
|---|---|---|---|---|
|用户A|2位用户|960×720×2|1,382,400 视频|(HD+)|
|用户B|2位用户+用户A 共享的屏幕|(960×720×2)+(1920x1080)|3,456,000 视频|(2K)|
|用户C|2位用户+用户A 共享的屏幕|(960×720×2)+(1920x1080)|3,456,000 视频|(2K)|
|用户D|3位用户+用户A 共享的屏幕|(960×720×3)+(1920x1080)|4,147,200 视频|(2K+)|
|用户E|3位用户+用户A 共享的屏幕|(960×720×3)+(1920x1080)|4,147,200 视频|(2K+)|

### 计费 

下表展示了如何计算音视频互动中产生的总费用: 

|收费服务(视频 用量类型)|总时长用量(分钟) = 各用 户时长用量总和|单价(元/ 千分钟)|各类型费用( 元)|总费用(元)(四舍五入至 小数点后两位)|
|---|---|---|---|---|
|视频(HD+)|60|50|(60/1000)×5 0=3||
|视频(2K)|60×2=120|90|(120/1000)× 90=10.8|43.8|
|视频(2K+)|60×2=120|250|(120/1000)× 250=30||

### 双流分辨率 

说明: 

双流模式下,用户的分辨率计算方式如下: 

如果订阅的是大流,则用户的集合分辨率根据发送端设置的大流分辨率计算。 

如果订阅的是小流,则用户的集合分辨率根据用户实际收到的分辨率计算。 

### 屏幕共享流的分辨率 

#### 如果你的场景中涉及屏幕共享,则屏幕共享流的视频单价以实际的视频分辨率为准。 

在Web端,由于设备和浏览器的限制,部分浏览器对设置的屏幕属性不一定能全部适配。这种情况下浏览器会自动调整分 辨率,计费也将按照实际分辨率计算。 

### 其他产品或服务计费 

说明: 

在你的场景中,如果除视频通话外还涉及其他云屋产品或服务,如云端录制或互动白板等。 互动白板: 可查看https://sdk.cloudroom.com/pages/price了解详情。 

云端录制: 可以理解为在房间内多增加了一个“用户”,该“用户”按照开发人员配置的录制方案去订阅视频,因此计费方法与视频计 算一样,按集合分辨率来计算。 

#### 云端录制时长用量的单价如下: 

|用量类型|单价(元/千分钟)|
|---|---|
|音频|7|
|视频(SD)|15|
|视频(HD)|27|
|视频(HD+)|80|
|视频(2K)|130|
|视频(2K+)|280|
|互动白板|10|

# 信息安全说明 

更新时间: 2024/09/11 11:35:13 

## 通信数据安全说明 

使用云屋sdk登录鉴权和业务通信描述图: 

如上图,以https通道进行鉴权,以及通过https通道获得本次通讯的aes密钥,对后续tcp,udp数据进行aes加解密处理。 只要业务服务器不泄漏鉴权帐号信息,通信就是安全的。 

## token机制说明 

云屋的token采用的是jwt这种开放标准(RFC 7519)生成的。 

在token的payload中携带appID、授权有效期,并使用appSecret进行SHA256签名操作,在签名过程中会进行加盐(salt)处 理。 

由于appSecret是保密的, 所以外界无法伪造token。 再加上token设置了有效期,时间一到token就会失效,所以安全性相 比采用appSecret会更高一些。 

# 准备工作 

更新时间: 2024/09/14 16:49:23 

## 帐号申请 

点此注册 一个账号,或者联系商务代为开通,或在网站咨询客服。 

## 创建项目 

可以在 管理平台 中创建新的项目(系统有一个默认项目,可以直接使用),如下图: 

为了保障接口安全,后台不再显示App Secret,所以请在创建项目成功显示App Secret时妥善保存好。 如果遗忘只能如下 图更换App Secret: 

防火墙开通 

#### 在使用云屋SDK提供的相关服务之前,您需要打开下面这些特定的端口: 

|端口|功能说明|Windows, Linux, Android , iOS, macOS, 网页插件|H5 SDK|小程序S DK|直播观 看SDK|后台管 理页面|
|---|---|---|---|---|---|---|
|TCP 2725|后台管理服务端口|||||√|
|TCP 2726|https服务端口 (SDK缺省使用https)|√|√|√|√||
|TCP 2728|信令服务端口|√|||||
|TCP 1935|服务器音视频流端口(rtmp)|||√|√||
|UDP 2698|服务器音视频流端口|√|||||
|UDP 2699|服务器音视频流端口(H5)||√||||

至此,准备工作已经完成,可以开始集成SDK了。 

# 集成SDK 

更新时间: 2024/09/14 16:49:23 

## 示例项目 

云屋在 GitHub 上提供开源的音视频通话示例项目API-Demo,体验云屋音视频通话的基本/进阶功能。 

## 开发环境准备 

在开始集成 SDK 前,请确保开发环境满足以下要求: 

- 已通过授权的华为开发者账号。可在华为开发者联盟注册账号。 

- 华为 DevEco Studio 5.0.3.200 或以上版本 

- HarmonyOS NEXT Developer Beta1 或以上版本的操作系统的真机或模拟器,且已开启“允许调试”选项。 已注册云屋开发者账号,并获取到AppID和AppSecret。 

## 集成到已有项目 

### OHPM方式(推荐) 

1. 使用命令行窗口进入工程目录,执行以下命令安装 SDK。 

sh
cd entry
ohpm install @cloudroom/hormony_rtcsdk

2. 重新启动DevEco studio,DevEco studio会自动下载SDK。 

### 手动方式 

1. 前往SDK下载页面,下载HarmonyOS SDK。 

2. 将har文件拷贝到工程目录 entry/libs 文件夹下。 

3. 使用命令行窗口进入工程目录,执行以下命令安装 SDK。 

sh
cd entry
ohpm install ./libs/hormony_rtcsdk.har

## 添加权限 

打开工程目录下 entry/src/main/module.json5 文件,添加必要的权限声明。 

{
"requestPermissions": [
{
"name": "ohos.permission.INTERNET"
},
{
"name": "ohos.permission.MICROPHONE",
"usedScene": {
"abilities": [
"EntryAbility"
],
"when": "always"
}

json

}, "reason": "$string:permissionReason" }, { "name": "ohos.permission.CAMERA", "usedScene": { "abilities": [ "EntryAbility" ], "when": "always" }, "reason": "$string:permissionReason" }, ... //其他APP权限 ] } 

在 entry/src/main/resources/base/element/string.json 中,添加变量 

{
"string": [
{
"name": "permissionReason",
"value": "用于音视频通话"
}
]
}

json

## 开始使用 

```arkts
import { CRVideoSDKEx } from "@cloudroom/hormony_rtcsdk"; ` console.log(`SDK版本号: ${CRVideoSDKEx.getSDKVersion()} ) //输出版本号 const cacheDir = getContext().getApplicationContext().cacheDir; // SDK工作目录 let sdk_engine = CRVideoSDKEx.create(cacheDir, '{}'); //创建SDK实例 
```

js

至此,集成工作已经完成,可以开始实现音视频通话了。 

# 实现音视频通话 

更新时间: 2024/09/14 16:49:23 

## 简要说明 

快速创建并进入房间,开始音视频通话;代码部分均为 arkTS 代码,详细代码请参考 API-Demo 代码。 

## 1. 初始化SDK 

初始化是整个SDK的使用基础,通常在程序启动的时候进行实例的创建(create),退出后进行销毁实例(destroy)操作,整个 程序的生命周期中只进行一次初始化和反初始化。 

//初始化 sdkUsePath 是SDK工作目录,用于存储配置文件、临时文件等。

js 

```arkts
import { CRVideoSDKEx } from '@cloudroom/hormony_rtcsdk'; const cacheDir = getContext().getApplicationContext().cacheDir; //获取缓存目录 
let sdk_engine = CRVideoSDKEx.create(cacheDir, JSON.stringify({ Timeout: 120000, //网络通信超时时间,单位是毫秒,取值范围:10000-120000, 缺省值:60000(60秒) })); 
```

#### 设置回调函数 

import { CRVideoSDKCallBack } from '@cloudroom/hormony_rtcsdk';
const CallbackObj: CRVideoSDKCallBack = {
//登录结果回调
loginRslt: (sdkErr) => {
//...
},
//通知掉线回调 可以弹出提示,或调用登录接口再次重试登录
notifyLineOff: (sdkErr) => {
//...
},
//创建房间成功
createMeetingSuccess: (roomID) => {
//...
},
//创建房间失败
createMeetingFail: (sdkErr) => {
//...
},
//进入房间的完成响应
enterMeetingRslt: (sdkErr) => {
//...
}
}
sdk_engine.on('loginRslt', CallbackObj.loginRslt); //订阅回调函数
sdk_engine.off('loginRslt', CallbackObj.loginRslt); //注销回调函数

js 

##### 说明: 

调用SDK接口前,应先订阅SDK回调消息,以便接收SDK回调消息 伴随SDK销毁时,应同时销毁所有监听器 如果在多处订阅了同一个回调事件,SDK不会覆盖原有事件,各个回调函数都会进入 

相关API请参考: 

create 

destroy 

on 

off 

## 2. 登录连接视频服务器 

设置视频服务器地址,然后使用appID和md5加密后的appSecret登录。(获取App ID及App Secret) 

调用接口: 

|//如果使用云屋的云服务时填sdk.cloudroom.com,使用私有化部署的服务器时要填部署的服务器地址; //此处以云屋的云服务为例。 js|
|---|

import { CRVSDK_AUTHTYPE, CRVSDK_WEBPROTOCOL } from '@cloudroom/hormony_rtcsdk'; sdk_engine.login({ sdkAuthType: CRVSDK_AUTHTYPE.CRVSDK_AUTHTP_SECRET, serverAddr: "sdk.cloudroom.com", appID: AppID, md5_appSecret: MD5.digestSync(AppSecret), token: '', userID: "userID", nickName: "昵称", webProtocol: CRVSDK_WEBPROTOCOL.CRVSDK_WEBPTC_HTTPS, userAuthCode: '' }); 

#### 回调通知: 

js //登录结果 sdk_engine.on('loginRslt', (sdkErr, cookie) => { //若失败 可以弹出错误提示,或调用登录接口再次重试登录 if (sdkErr !== CRVSDK_ERR_DEF.CRVSDKERR_NOERR) { ` console.log( 登录失败(错误码: ${sdkErr})`) return; } ' ' console.log( 登录成功 ) }); //通知掉线 可以弹出提示,或调用登录接口再次重试登录 sdk_engine.on("notifyLineOff", (sdkErr) => { ` console.log( 与服务器的连接中断!(错误码: ${sdkErr})`); }) 

相关API请参考: 

login logout loginRslt notifyLineOff 

## 3. 创建房间 

调用接口: 

js 

//创建房间 sdk_engine.createMeeting(); 

#### 回调通知: 

##### //创建房间成功 

js 

sdk_engine.on("createMeetingSuccess", (meetID, cookie) => { ` ` console.log( 创建房间成功,房间号:${meetID} ) }) 

##### //创建房间失败 

sdk_engine.on("createMeetingFail", (sdkErr, cookie) => { ` console.log( 创建房间失败(错误码: ${sdkErr})`); }) 

#### 相关API请参考: 

createMeeting 

- createMeetingSuccess 

- createMeetingFail 

## 4. 进入房间 

用创建成功的房间信息(房间ID)进入房间,其他用户也是利用此房间信息进入该房间。 

#### 调用接口: 

##### //进入房间 

sdk_engine.enterMeeting(meetID); 

#### 回调通知处理: 

##### //进入房间的完成响应 

js js 

sdk_engine.on("enterMeetingRslt", (sdkErr) => { //若失败 可以弹出错误提示,或调用登录接口再次重试登录 if (sdkErr !== CRVSDK_ERR_DEF.CRVSDKERR_NOERR) { ` console.log( 进入房间失败(错误码: ${sdkErr})`) return; } ' ' console.log( 进入房间成功 ) }) 

##### //监控房间结束 

sdk_engine.on("notifyMeetingStopped", () => { ' ' console.log( 房间已结束 ) }) 

#### 相关API请参考: 

enterMeeting 

- enterMeetingRslt notifyMeetingStopped 

## 5. 打开麦克风/摄像头 

进入房间成功后,打开自己的麦克风和摄像头,以便本地、远端显示自己的视频图像 

js 

//打开自己的麦克风 

sdk_engine.openMic(myUserID); //打开自己的摄像头 sdk_engine.openVideo(myUserID); 

#### 相关API请参考: 

openMic 

closeMic openVideo 

closeVideo 

## 6. 观看自己/他人视频 

成功进入房间后,根据自己/他人登录id ,设置并观看其视频图像 

js
import { CRMeetingMember, CRVSDK_SCALE_MODE, CRVSDK_STREAM_VIEWTYPE, CRVSDK_VSTEAMLV_TYPE, CR_LIB_N
AME } from '@cloudroom/hormony_rtcsdk';
@Component
struct VideoCall {
  @State memberList: CRMeetingMember[] = []
aboutToAppear(): void {
//从会议中取到所有参会者,然后按业务逻辑选取想观看他人视频;(以下代码是观看所有人的视频)
this.memberList = sdk_engine.getAllMembers();
}
build() {
Grid() {
ForEach(this.memberList, (member: CRMeetingMember) => {
GridItem() {
XComponent({ id: member.userId, type: XComponentType.SURFACE, libraryname: CR_LIB_NAME })
.onLoad(() => {
              sdk_engine.addCanvas({
viewId: member.userId,
type: CRVSDK_STREAM_VIEWTYPE.CRVSDK_VIEWTP_VIDEO,
videoId: { userID: member.userId, videoID: -1 },
videoLv: CRVSDK_VSTEAMLV_TYPE.CRVSDK_VSTP_LV0,
showMode: CRVSDK_SCALE_MODE.CRVSDK_RENDERMD_FIT
});
})
.onDestroy(() => {
              sdk_engine.rmCanvas(member.userId)
})
.width('33.3333%')
}
}, (item: CRMeetingMember) => item.userId)
}
.layoutDirection(GridDirection.Column)
.columnsGap(10)
.rowsGap(10)
.padding(10)
}
}

#### 相关API请参考: 

getAllMembers addCanvas 

rmCanvas 

XComponent 

## 7.退出房间 

//退出房间 sdk_engine.exitMeeting(); 

js

#### 相关API请参考: 

exitMeeting 

## 8.注销登录 

//注销本次登录 sdk_engine.logout(); 

|js|
|---|

#### 相关API请参考: 

logout 

## 9.销毁实例 

执行反销毁后SDK功能不再可用。 

|//反初始化|js|
|---|---|
|sdk_engine.destroy(); sdk_engine= null;||

#### 相关API请参考: 

destroy 

# 登录鉴权 

更新时间: 2024/09/14 16:49:23 

## SDK登录鉴权的目的 

确保只有合法的身份才能使用sdk接入到服务器。 

## SDK登录鉴权方案 

密码鉴权方案: 此方案简单,配合https通信,适用于一般的安全要求; 

动态token鉴权方案: 此方案每次登录token都不一样,并且可自定义token的有效期,具有更高的安全性; 

### 密码鉴权方案说明 

1. 在云屋web管理页面上,创建appID及密码,然后保存到业务服务器上; 

2. 在app连接到业务服务器时,通过安全通道将“appID及md5(密码)”下发给app并配置给sdk; 

3. sdk通过https向云屋服务器发起登录时携带“appID及md5(密码)”; 

4. 云屋服务器校验密码是否正确; 

### 动态token鉴权方案说明 

1. 在云屋web管理页面上,创建appID及密码,然后保存到业务服务器上; 

2. App调用sdk登录之前,去业务服务器请求“token”; 

3. 业务服务器调用云屋token生成器,生成token并返回给App; 

4. App收到token后,调用sdk登录; 

5. sdk通过https向云屋服务器发起登录时携带“appID及token”; 

6. 云屋服务器校验token; 

7. 在token即将过期前30秒,服务器通知sdk,sdk会通知app; 

8. app应该尽快从业务服务器获取到新的token并提交给sdk,sdk将其更新到云屋服务器后,就可保证通信不中断;(如 果token到期前没有更新有效token,通信将被结束) 

# 使用云代理 

更新时间: 2024/09/14 16:49:23 

## 云代理介绍 

对于安全需求较高的企业用户比如金融、医院、高校、大型企业,设置防火墙可以限制员工访问不安全网站,保护内部信 息安全。 

云屋提供了云代理服务来接入这类有防火墙限制的用户,只需要在防火墙上将特定的域名及端口列入白名单,就可以正常 访问云屋的音视频云服务。 

## 使用云代理 

- 1、将云屋云代理服务器和端口添加到企业防火墙的白名单 

- 云屋云代理服务器域名: proxy.cloudroom.com 

- 云屋云代理服务端口与云屋SDK需要的端口保持一致,无需暴露额外端口 

- 2、设置到登录服务器 

- 把登录服务器地址替换为:proxy.cloudroom.com 

# 设置音频属性 

更新时间: 2024/09/14 16:49:23 

## 功能介绍 

成功进入房间后,可以设置音频设备、音量等。 

注意:成功进入房间后,才可以设置音频属性。 

## 1.设置音频参数 

调用接口: 

##### //获取所有的麦克风和扬声器设备 

js

const micDevs = sdk_engine.getAudioMics(); const spkDevs = sdk_engine.getAudioSpks(); 

//显示当前配置 const aCfg = sdk_engine.getAudioCfg(); 

//设置当前的麦克风/扬声器 aCfg._micGuid = micId; aCfg._spkGuid = spkId; sdk_engine.setAudioCfg(aCfg); 

#### 相关API请参考: 

- getAudioMics 

- getAudioSpks 

- getAudioCfg 

- setAudioCfg 

## 2.开关麦克风 

const userID = "myUserID"; //打开麦克风 sdk_engine.openMic(userID) //关闭麦克风 sdk_engine.closeMic(userID) 

js 

#### 相关API请参考: 

openMic 

- closeMic 

- notifyMicStatusChanged 

## 3.设置通话音量 

//设置扬声器音量 

|js|
|---|

sdk_engine.setSpkVolume(volume); 

相关API请参考: 

setSpkVolume 

setSpeakerMute 

## 4.麦克风音量调整 

##### //麦克风音量调整 

js

sdk_engine.setMicVolume(volume) 

#### 相关API请参考: 

- setMicVolume 

notifyMicEnergy 

# 设置视频属性 

更新时间: 2024/09/14 16:49:23 

## 功能介绍 

在通话过程中可以根据实际业务场景,调整视频画面的清晰度和流畅度,提升用户体验。 

视频属性包含设置默认摄像头、视频分辨率、帧率、码率、降噪等。 

注意:成功进入房间后,才可以设置视频属性。 

## 1.默认摄像头设置 

#### 调用接口: 

const myUserId = 'myUserId'; //获取所有摄像头设备 const camDevs = sdk_engine.getAllVideoInfo(myUserId); 

js 

//获取当前默认摄像头 const defCam = sdk_engine.getDefaultVideo(myUserId); 

//将编号为camId的摄像头设置为默认摄像头 sdk_engine.setDefaultVideo(camId) 

#### 相关API请参考: 

- getAllVideoInfo 

- getDefaultVideo 

- setDefaultVideo 

## 2.编码参数设置 

调用接口: 

##### //获取摄像头编码参数 

js 

const vCfg = sdk_engine.getVideoCfg(); 

//设置摄像头编码输出为1280*720,帧率15,其他参数不变 vCfg.size = '1280*720'; vCfg.fps = 15; const sdkErr = sdk_engine.setVideoCfg(vCfg); 

#### 相关API请参考: 

- getVideoCfg 

- setVideoCfg 

# 多方视频通话 

更新时间: 2024/09/14 16:49:23 

## 功能介绍 

多方视频通话时,根据当前业务场景合理设置视频编码参数,可以在较低的带宽占用下实现流畅清晰的音视频沟通,下面 将针对几种常见场景进行介绍。 

## 1.一对一 

#### 画中画布局示例图: 

常用于如双人视频聊天场景,双方通常都希望看到对方比较清晰的视频,此时可以使用较高的视频编码分辨率,比如720P 或480P。 

```arkts
import { CRMeetingMember, CRVideoSDKCallBack, CRVSDK_SCALE_MODE, CRVSDK_STREAM_VIEWTYPE, CRVSDK_VSTEAMLV_TYPE, CR_LIB_NAME } from '@cloudroom/hormony_rtcsdk'; @Component struct VideoCall { viewID1 = 'viewID1'; viewID2 = 'viewID2'; myUserID = 'myUserID'; CallbackObj: CRVideoSDKCallBack = { // 如果对方后入会,需要监听回调再订阅绘制 notifyUserEnterMeeting: (userID) => { sdk_engine.addCanvas({ viewId: this.viewID2, //视图id type: CRVSDK_STREAM_VIEWTYPE.CRVSDK_VIEWTP_VIDEO, //视图类型 
```

js

showMode: CRVSDK_SCALE_MODE.CRVSDK_RENDERMD_FIT, //显示模式 videoId: { userID: userID, videoID: -1 }, //用户视频id videoLv: CRVSDK_VSTEAMLV_TYPE.CRVSDK_VSTP_LV0, //视频流等级 }) } } 

aboutToAppear(): void { // 注册回调函数 

sdk_engine.on('notifyUserEnterMeeting', this.CallbackObj.notifyUserEnterMeeting) sdk_engine.openVideo(myUserID) //打开自己的摄像头 

sdk_engine.addCanvas({ 

viewId: this.viewID1, //视图id 

type: CRVSDK_STREAM_VIEWTYPE.CRVSDK_VIEWTP_VIDEO, //视图类型 showMode: CRVSDK_SCALE_MODE.CRVSDK_RENDERMD_FIT, //显示模式 videoId: { userID: myUserID, videoID: -1 }, //用户视频id 

videoLv: CRVSDK_VSTEAMLV_TYPE.CRVSDK_VSTP_LV0, //视频流等级 }) 

const memberList = sdk_engine.getAllMembers(); 

// 使用排他法,查询另一个用户的成员信息 

const member: CRMeetingMember | undefined = memberList.find(member => member.userId !== myUserID); 

if (member) { sdk_engine.addCanvas({ viewId: this.viewID2, //视图id 

type: CRVSDK_STREAM_VIEWTYPE.CRVSDK_VIEWTP_VIDEO, //视图类型 showMode: CRVSDK_SCALE_MODE.CRVSDK_RENDERMD_FIT, //显示模式 videoId: { userID: member.userId, videoID: -1 }, //用户视频id 

videoLv: CRVSDK_VSTEAMLV_TYPE.CRVSDK_VSTP_LV0, //视频流等级 }) 

} } 

aboutToDisappear(): void { 

sdk_engine.off('notifyUserEnterMeeting', this.CallbackObj.notifyUserEnterMeeting) } 

build() { 

Stack({ alignContent: Alignment.TopEnd }) { 

XComponent({ id: this.viewID1, type: XComponentType.SURFACE, libraryname: CR_LIB_NAME }) .width('100%') 

.height('100%') 

XComponent({ id: this.viewID2, type: XComponentType.SURFACE, libraryname: CR_LIB_NAME }) .width('30%') 

.aspectRatio(9 / 16) 

.margin({ right: 10, top: 10 }) } .height('100%') .width('100%') } } 

#### 相关API请参考: 

openVideo 

getAllMembers 

notifyUserEnterMeeting addCanvas 视频组件 

2 多方视频 

2.多方视频 

#### 多方视频示例图: 

常用于在线教育场景,老师的视频画面比较大,可以使用较高的分辨率比如720P,下面学生的视频画面比较小,应采用较 低的视频编码分辨率,比如360P或256P。 

#### 示例代码如下: 

import { CRMeetingMember, CRVideoSDKCallBack, CRVSDK_SCALE_MODE, CRVSDK_STREAM_VIEWTYPE, CRVSDK_VSTEAMLV_TYPE, CR_LIB_NAME } from '@cloudroom/hormony_rtcsdk'; 

js 

```arkts
@Entry @Component export struct VideoCall { @State memberList: CRMeetingMember[] = []; teacherViewID = 'teacherViewID'; teacherID = 'teacherID' CallbackObj: CRVideoSDKCallBack = { 
```

// 如果对方后入会,需要监听回调再添加订阅绘制 notifyUserEnterMeeting: (userID) => { const member = sdk_engine.getMemberInfo(userID); this.memberList.push(member); }, notifyUserLeftMeeting: (userID) => { 

const idx = this.memberList.findIndex(member => member.userId === userID) if (idx > -1) { 

this.memberList.splice(idx, 1); } } } 

aboutToAppear(): void { // 注册回调函数 

##### // 注册回调函数 

sdk_engine.on('notifyUserEnterMeeting', this.CallbackObj.notifyUserEnterMeeting) sdk_engine.on('notifyUserLeftMeeting', this.CallbackObj.notifyUserLeftMeeting) sdk_engine.openVideo(this.teacherID) //打开自己的摄像头 

sdk_engine.addCanvas({ 

viewId: this.teacherViewID, //视图id 

type: CRVSDK_STREAM_VIEWTYPE.CRVSDK_VIEWTP_VIDEO, //视图类型 showMode: CRVSDK_SCALE_MODE.CRVSDK_RENDERMD_FIT, //显示模式 videoId: { userID: this.teacherID, videoID: -1 }, //用户视频id 

videoLv: CRVSDK_VSTEAMLV_TYPE.CRVSDK_VSTP_LV0, //视频流等级 }) 

##### //查询所有用户信息,排除掉老师的userID 

this.memberList = sdk_engine.getAllMembers().filter(item => item.userId !== this.teacherID); } 

aboutToDisappear(): void { 

sdk_engine.off('notifyUserEnterMeeting', this.CallbackObj.notifyUserEnterMeeting) sdk_engine.off('notifyUserLeftMeeting', this.CallbackObj.notifyUserLeftMeeting) 

} 

build() { Column() { //渲染老师 

XComponent({ id: this.teacherViewID, type: XComponentType.SURFACE, libraryname: CR_LIB_NAME }) .width('100%') 

.layoutWeight(1) 

Row() { //渲染学生列表 

ForEach(this.memberList, (member: CRMeetingMember) => { 

XComponent({ id: member.userId, type: XComponentType.SURFACE, libraryname: CR_LIB_NAME }) .onLoad(() => { sdk_engine.addCanvas({ viewId: member.userId, //视图id 

type: CRVSDK_STREAM_VIEWTYPE.CRVSDK_VIEWTP_VIDEO, //视图类型 showMode: CRVSDK_SCALE_MODE.CRVSDK_RENDERMD_FIT, //显示模式 videoId: { userID: member.userId, videoID: -1 }, //用户视频id videoLv: CRVSDK_VSTEAMLV_TYPE.CRVSDK_VSTP_LV0, //视频流等级 }) }) .onDestroy(() => { sdk_engine.rmCanvas(member.userId) }) .width('30%') .aspectRatio(9 / 16) }, ((member: CRMeetingMember) => member.userId)) } } .height('100%') .width('100%') } } 

#### 相关API请参考: 

getAllMembers 

notifyUserEnterMeeting 

notifyUserLeftMeeting 

addCanvas 

rmCanvas 

视频组件 

# 本地录制 

更新时间: 2024/09/14 16:49:23 

## 功能介绍 

用户可以对通讯过程进行录制并保存到终端设备,有以下特性: 

- 录制画面可以根据业务场景自由拼接组合,包括本地摄像头、远端摄像头、远端共享的屏幕、影音播放、图片。支持 同时启动多个录制。 

- 录制格式支持mp4、ts、flv、aiv, mp3,如果选择了flv和ts两种格式,即使录制过程中程序出现异常了,崩溃之前的录 像仍然可用。 

- 对于金融双录等安全性要求高的特定领域,支持对录制的文件进行加密,录制后直接把录像传到标准http服务器、 OSS或者云屋服务器。 

- 本地加密过的录像只能通过SDK提供的播放器播放。 

## 1. 创建混图器 

#### 左右布局示例图 

#### 接口调用: 

```arkts
import { CRLocMixerCfgObj, CRMixerContentObj, CRVSDK_ERR_DEF } from '@cloudroom/hormony_rtcsdk'; const mixerID = '1'; //混图器唯一标识 //混图器参数配置 const mixerCfgObj: CRLocMixerCfgObj = { width: 1280, height: 720, frameRate: 15, bitRate: 1000000, defaultQP: 26, gop: 15, } const mixerContentsObj: CRMixerContentObj[] = [{ type: 0, top: 0, left: 0, width: 640, height: 720, 
```

js 

param: { camid: "userID1.-1" } }, { type: 0, top: 0, left: 640, width: 640, height: 720, param: { camid: "userID2.-1" } }] 

// 创建混图器, 设置混图器编号为1 

```arkts
const sdkErr = sdk_engine.createLocMixer(mixerID, mixerCfgObj, mixerContentsObj); if (sdkErr === CRVSDK_ERR_DEF.CRVSDKERR_NOERR) { //创建成功 } 
```

#### 相关API请参考: 

createLocMixer 

相关结构定义请参考: 

- CRLocMixerCfgObj 

- CRMixerContentObj 

错误码 

## 2. 添加输出到录像文件 

import { CRVSDK_MIXER_OUTPUT_TYPE, CRVSDK_ERR_DEF } from '@cloudroom/hormony_rtcsdk'; 

js 

```arkts
const dir = getContext().getApplicationContext().tempDir; const fileName = `/${dir}/2024-09-14_13-47-41_HarmonyOS_73542046.mp4`; 
```

const mixerOutput: CRLocMixerOutputObj[] = [{ type: CRVSDK_MIXER_OUTPUT_TYPE.CRVSDK_MIXER_OUTPUT_FILE, filename: fileName 

}] 

const sdkErr = sdk_engine.addLocMixerOutput(mixerID, mixerOutput); 

if (sdkErr === CRVSDK_ERR_DEF.CRVSDKERR_NOERR) { //启动成功 } 

#### 相关API请参考: 

addLocMixerOutput 

相关结构定义请参考: 

CRLocMixerOutputObj 

## 3. 录像回调处理 

在此可获得录像文件的时长、大小、录像文件异常等信息 

import { CRVSDK_LOCMIXER_OUTPUT_STATE } from '@cloudroom/hormony_rtcsdk'; 

js 

sdk_engine.on("notifyLocMixerOutputInfo", (mixerID, nameOrUrl, outputInfo) => { if (outputInfo.state === CRVSDK_LOCMIXER_OUTPUT_STATE.CRVSDK_LOCMO_FAIL) { //录像文件出错,errCode中有错误原因 } }) 

#### 相关API请参考: 

notifyLocMixerOutputInfo 

#### 相关结构定义请参考: 

CRLocMixerOutputInfoObj 

## 4. 更新图像内容 

#### 画中画布局示例图 

#### 接口调用: 

import { CRMixerContentObj, CRVSDK_ERR_DEF } from '@cloudroom/hormony_rtcsdk'; 

js 

// 录制参数列表中,越靠后的元素会覆盖之前的元素 const mixerContents: CRMixerContentObj[] = [{ //大窗的视频 type: 0, top: 0, left: 0, width: 1280, height: 720, param: { camid: "userID2.-1" } }, { //小窗口视频 type: 0, 

```arkts
yp , top: 1280 - 256, left: 720 - 144, width: 256, height: 144, param: { camid: "userID1.-1" } }] // 更新混图器 const sdkErr = sdk_engine.updateLocMixerContent(mixerID, mixerContents); if (sdkErr !== CRVSDK_ERR_DEF.CRVSDKERR_NOERR) { //更新成功 } 
```

#### 相关API请参考: 

updateLocMixerContent 

## 5. 结束录制 

##### //停止混图器输出,录制文件将自动保存 

js 

sdk_engine.rmLocMixerOutput(mixerID, fileName) //销毁混图器 sdk_engine.destroyLocMixer(mixerID); 

#### 相关API请参考: 

rmLocMixerOutput 

destroyLocMixer 

# 云端录制 

更新时间: 2024/09/14 16:49:23 

## 功能介绍 

云端录制支持两种模式: 

单流模式:可以为房间内指定人员或全部人员的摄像头和声音生成独立的录像文件; 

- 合流模式:可以将房间内摄像头、屏幕共享、影音共享、白板、声音等内容混合录制成一个录像文件;(录制内容和 布局支持自定义) 

一个房间可以开启一个单流录制和多个合流录制, 录制文件存储支持: 

存储到云屋服务器:可以通过WEB API下载和管理 

存储到第三方网盘:可通过第三方网盘接口下载和管理; 

## 1.开通云端录制服务 

请确保您已成功注册了一个帐号。 

请联系商务为对应帐号开通“云端录制服务”。 

## 2.开始云端录制 

录制左右布局示例图: 

#### 调用接口: 

##### import { CRCloudMixerCfgObj } from '@cloudroom/hormony_rtcsdk'; 

js 

//配置混图器编码参数:1280*720,  15帧 const cloudMixerCfg: CRCloudMixerCfgObj = { mode: 0, 

videoFileCfg: { svrPathName: "/2024-09-14/2024-09-14_13-47-41_HarmonyOS_73542046.mp4", vWidth: 1280, vHeight: 720, vFps: 15, layoutConfig: [{ type: 0, 

top: 180 

top: 180,
left: 0,
width: 640,
height: 360,
keepAspectRatio: 1,
param: {
camid: "userID1.-1"
}
}, {
type: 0,
top: 180,
left: 640,
width: 640,
height: 360,
keepAspectRatio: 1,
param: {
camid: "userID2.-1"
}
}]
}
}
const mixerID = sdk_engine.createCloudMixer(cloudMixerCfg);

如果录像需要保存到第三方云存储,请在createCloudMixer时,传storageConfig参数; 相关API请参考: 

createCloudMixer 

## 3.更新云端录制内容 

更新成画中画布局示例图: 

接口调用: 

js 

import { CRCloudMixerCfgObj } from '@cloudroom/hormony_rtcsdk'; 

//混图器内容:画中画布局(示例图如下, 底层1280*720, 上层400*225) //底层为userID1的默认摄像头, 上层为userID2的默认摄像头 const cloudMixerCfg: CRCloudMixerCfgObj = { mode: 0, videoFileCfg: { svrPathName: "/2024-09-14/2024-09-14_13-47-41_HarmonyOS_73542046.mp4", vWidth: 1280, vHeight: 720, vFps: 15, layoutConfig: [{ //大视频窗口 type: 0, top: 0, left: 0, width: 1280, height: 720, keepAspectRatio: 1, param: { camid: "userID1.-1" } }, { //小视频窗口 type: 0, top: 495, left: 880, width: 400, height: 225, keepAspectRatio: 1, param: { camid: "userID2.-1" } }] } } sdk_engine.updateCloudMixerContent(mixerID, cloudMixerCfg); //mixerID由createCloudMixer接口返回 

相关API请参考: 

updateCloudMixerContent 

## 4.停止云端录制 

停止云端录制后,也会触发事件notifyCloudMixerStateChanged 

接口调用: 

sdk_engine.destroyCloudMixer(mixerID); 

js 

相关API请参考: 

destroyCloudMixer 

## 5.云端录制回调通知 

录制过程中都会录制状态变化事件、录制文件信息变化通知。在此可以实时获得录制状态、录制文件当前的时长、大小, 以及录制异常等信息。 

回调通知: 

js 

//云端录制状态变化通知

sdk_engine.on("notifyCloudMixerStateChanged", (mixerID, state, exParam, operUserID) => {
//状态处理
...
})
//云端录制输出内容变化通知
sdk_engine.on("notifyCloudMixerOutputInfoChanged", (mixerID, outputInfo) => {
//状态处理, 文件时长、大小等处理
})

相关API请参考: 

notifyCloudMixerStateChanged 

notifyCloudMixerOutputInfoChanged 

## 6.获取录像 

录像停止后,录像文件会开始上传到录像文件存储服务器中(可关注notifyCloudMixerOutputInfoChanged通知,得到上传 完成事件)。 

可以通过WEB API进行录像文件查询、下载和删除等处理。 

#### 也可以登录管理后台,在管理页面上回放和下载录像: 

如果将录像保存到第三方云存储上,请使用第三方提供的接口或管理页来获取。 

# 屏幕共享 

更新时间: 2024/09/14 16:49:23 

## 功能介绍 

在视频会话中为了提高沟通效率,可以将自己的屏幕内容分享给其他参与方观看。 

使用场景如下: 

- 视频会议场景中,屏幕共享可以将讲话者本地的文件、数据、网页、PPT 等画面分享给其他与会人; 在线课堂场景中,屏幕共享可以将老师的课件、笔记、讲课内容等画面展示给学生观看。 

注意:同一个房间中,不支持多人同时开启屏幕共享。 

## 共享端 

共享端功能暂未开放 

## 观看端 

### 1.准备屏幕共享图像播放容器 

##### import { util } from '@kit.ArkTS'; 

|js|
|---|

import { CRVSDK_STREAM_VIEWTYPE, CRVSDK_SCALE_MODE, CR_LIB_NAME } from '@cloudroom/hormony_rtcsdk' viewId = util.generateRandomUUID(); //viewId取随机数,保证唯一 

- XComponent({ id: this.viewId, type: XComponentType.SURFACE, libraryname: CR_LIB_NAME }) .onLoad(() => { 

- //开始订阅视图,SDK会根据传入的参数在XComponent组件上绘制视图 

- sdk_engine.addCanvas({ viewId: this.viewId, type: CRVSDK_STREAM_VIEWTYPE.CRVSDK_VIEWTP_SCREEN, showMode: CRVSDK_SCALE_MODE.CRVSDK_RENDERMD_FIT videoId: undefined, videoLv: undefined, 

- }); 

- }) 

- .onDestroy(() => { 

- //取消订阅视图,SDK会停止在XComponent组件上绘制视图,并释放资源 

- sdk_engine.rmCanvas(this.viewId) 

- }) 

### 2.收到共享通知,创建UI组件 

##### //通知屏幕共享开始 

|js|
|---|

- sdk_engine.on("notifyScreenShareStarted", (userID) => { //此时可以把XComponent组件渲染出来 

- }) 

#### 相关API请参考: 

notifyScreenShareStarted 

addCanvas 

rmCanvas 视图组件 

js 

### 3.通知停止共享 

##### //收到他人停止了屏幕共享的通知 

sdk_engine.on("notifyScreenShareStopped", (operatorID) => { //此时可以把XComponent组件销毁 }) 

#### 相关API请参考: 

notifyScreenShareStopped 

# 影音播放 

更新时间: 2024/09/14 16:49:23 

## 功能介绍 

把一个本地视频文件、或网络流媒体播放给房间内其他用户观看,支持暂停、设置放位置等; 

支持的影音文件格式有: mov、rmvb、rm、flv、mp4、3gp、mp3、wav等市面上常见格式;支持http、rtmp、rtsp网络流 媒体; 

一个房间中同一时间只支持进行一个影音播放; 

## 实现介绍 

### 1.准备影音图像播放容器 

import { util } from '@kit.ArkTS'; 

js 

import { CRVSDK_STREAM_VIEWTYPE, CRVSDK_SCALE_MODE, CR_LIB_NAME } from '@cloudroom/hormony_rtcsdk' viewId = util.generateRandomUUID(); //viewId取随机数,保证唯一 

XComponent({ id: this.viewId, type: XComponentType.SURFACE, libraryname: CR_LIB_NAME }) .onLoad(() => { 

//开始订阅视图,SDK会根据传入的参数在XComponent组件上绘制视图 sdk_engine.addCanvas({ viewId: this.viewId, type: CRVSDK_STREAM_VIEWTYPE.CRVSDK_VIEWTP_MEDIA, showMode: CRVSDK_SCALE_MODE.CRVSDK_RENDERMD_FIT videoId: undefined, videoLv: undefined, }); }) .onDestroy(() => { 

//取消订阅视图,SDK会停止在XComponent组件上绘制视图,并释放资源 sdk_engine.rmCanvas(this.viewId) }) 

### 2.开始播放并观看影音 

每次只能播放一个视频,停止正在播放的视频才能播放下一个视频。通过设置播放配置,还可以控制房间内其他人看到的 效果。 

#### 接口调用: 

// 配置影音共享参数1920*1080,帧率24(如果视频文件清晰度比配置低,则以文件为准) const mediaCfg = JSON.parse(sdk_engine.getMediaCfg()); mediaCfg.size = "1920*1080"; mediaCfg.fps = 24; sdk_engine.setMediaCfg(JSON.stringify(mediaCfg)); 

js 

//开始播放影音 sdk_engine.startPlayMedia("/data/xxx/xxx.mp4"); 

观看影音需要监听以下的回调通知: 

js 

//观看端和播放端都会收到开始播放影音的通知,此时显示影音播放UI,即可观看影音 sdk_engine.on("notifyMediaStart", (userID) => { 

}) 

#### 相关API请参考: 

- getMediaCfg 

- setMediaCfg 

- startPlayMedia 

- notifyMediaStart 

- addCanvas 

- rmCanvas 

- 视图组件 

### 3.设置播放进度 

调用接口: 

// 设置播放进度,单位:毫秒.例如:设置到2秒处. sdk_engine.setMediaPlayPos(2000); 

js 

#### 相关API请参考: 

setMediaPlayPos 

### 4.暂停、停止播放 

调用接口: 

##### // 暂停或恢复播放影音:ture为暂停,false为恢复 

js 

sdk_engine.pausePlayMedia(true); //停止播放影音 sdk_engine.stopPlayMedia(); 

回调通知: 

注意:主动调用stopPlayMedia停止播放,或者影音文件播放到结尾,都会触发事件notifyMediaStop,房间内所有人都会收 到。 

##### //媒体暂停播放通知 

js 

sdk_engine.on("notifyMediaPause", (userID, bPause) => { 

}) 

//影音停止播放通知,观看端和播放端都会收到此通知。reason 为停止原因 sdk_engine.on("notifyMediaStop", (userID, reason) => { 

}) 

#### 相关API请参考: 

pausePlayMedia 

stopPlayMedia 

- notifyMediaPause 

notifyMediaStop 

# 排队 

更新时间: 2024/09/14 16:49:23 

## 功能介绍 

在呼叫中心的业务场景下,有多个客户呼叫进来,有多个坐席提供服务,简单的一对一呼叫无法满足业务需求。此时可以 使用我们的排队功能,客户不再直接呼叫某个坐席,而是呼叫到一个坐席队列,由系统自动给客户分配一个空闲的坐席。 

多个坐席可以服务于一个队列,客户排队这个队列时,系统会自动分配一个空闲坐席来提供服务。 

一个坐席可以同时服务多个队列,优先服务高优先级队列里的客户,队列优先级相同时优先服务最早排队的客户。 业务高峰期没有空闲的坐席时,客户将在队列中排队等待,当有坐席空闲时,将为最早排队的客户提供服务。 同一队列的坐席可以配置不同的坐席优先级,队列中的客户优先由空闲的高优先级的坐席来提供服务。 

注意:在登录成功并且启用呼叫功能的情况下才可以使用排队功能 

## 1.创建队列 

可以通过两种方式创建队列: 

第一种是登录云屋SDK后台并创建。如下图: 

第二种是通过Web API创建。 

## 2.初始化队列 

在登录成功后,初始化队列信息 

调用接口: 

##### sdk_engine.initQueueDat(); // 初始化队列数据 

js 

#### 回调通知: 

##### //队列初始化操作结果 

js 

sdk_engine.initQueueDatRslt.callback = function(sdkErr, cookie){ if(sdkErr === CRVSDK_ERR_DEF.CRVSDKERR_NOERR){ //初始化队列成功后,才可以获取队列相关信息并展示。 }else{ " console.log( 初始化队列信息 失败,错误码: "+ sdkErr); } } 

相关API请参考: 

initQueueDat 

initQueueDatRslt 

## 3.获取队列信息 

在初始化队列成功后,才可以使用获取队列信息。并且可以多次获取。 

#### 调用接口: 

|//获取队列信息 js|
|---|

const queueList = sdk_engine.getAllQueueInfo(); 

相关API请参考: 

getAllQueueInfo 

相关结构定义请参考: 

CRQueInfo 

## 4.1坐席:服务队列 

调用接口: 

|sdk_engine.startService(queID); //开始服务某个队列(可以多次调用,开启对多个队列的服务) . js|
|---|
|sdk_engine.stopService(queID); //停止服务某个队列|
|回调通知: js|

##### // 开始服务队列操作结果 

sdk_engine.on("startServiceRslt", (queID, sdkErr, cookie) => { if(sdkErr === CRVSDK_ERR_DEF.CRVSDKERR_NOERR){ //开始服务队列成功 } else { " console.log( 开始服务队列 失败,错误码: "+ sdkErr); } }) //停止服务队列操作结果 sdk_engine.on("stopServiceRslt", (queID, sdkErr, cookie) => { if(sdkErr === CRVSDK_ERR_DEF.CRVSDKERR_NOERR){ //停止服务队列成功 } else { " console.log( 停止服务队列 失败,错误码: "+ sdkErr); } }) // 开始/停止服务队列,会触发队列状态变化通知 sdk_engine.on("notifyQueueStatusChanged", (queStatus) => { }) 

#### 相关API请参考: 

startService 

stopService 

startServiceRslt 

stopServiceRslt 

stopServiceRslt 

notifyQueueStatusChanged 

#### 相关结构定义请参考: 

CRQueStatus 

## 4.2客户:排队 

客户选择一个队列进行排队,每次只能排一个队列 

调用接口: 

js sdk_engine.startQueuing(queID); // 客户开始排队 sdk_engine.stopQueuing(queID); //客户停止排队 回调通知: js 

// 开始排队操作结果 sdk_engine.on("startQueuingRslt", (sdkErr, cookie) => { if(sdkErr === CRVSDK_ERR_DEF.CRVSDKERR_NOERR){ //开始排队操作成功 } else { " " console.log( 开始排队操作失败,错误码: + sdkErr); } }) // 停止排队操作结果 sdk_engine.on("stopQueuingRslt", (sdkErr, cookie) => { if(sdkErr === CRVSDK_ERR_DEF.CRVSDKERR_NOERR){ //停止排队操作成功 } else { " " console.log( 停止排队操作失败,错误码: + sdkErr); } }) 

##### //开始/停止排队,会触发队列状态变化通知 

js 

sdk_engine.on("notifyQueueStatusChanged", (queStatus) => { }) //排队信息变化通知 sdk_engine.on("notifyQueuingInfoChanged", (queuingInfo) => { }) 

#### 相关API请参考: 

- startQueuing 

- stopQueuing 

- startQueuingRslt 

- stopQueuingRslt 

- notifyQueueStatusChanged 

- notifyQueuingInfoChanged 

相关结构定义请参考: 

CRQueStatus 

CRQueuingInfo 

## 5.系统给坐席分配客户 

#### 客户分配模式有自动和手动两种: 

- 在自动分配模式下,坐席一旦空闲系统就会立即分配当前排队的客户过来,适用于坐席可以持续提供服务的业务场 景。 

- 在手动分配模式下,坐席空闲后系统不自动分配客户,而是坐席准备好后手动触发分配一个当前排队的客户,适用于 坐席接待完客户后需要进行信息录入之类的善后工作,或者需要在接待新客户之前进行一些准备工作的业务场景。 

#### 自动分配模式: 

#### 回调通知: 

##### // 系统自动安排客户 

js 

sdk_engine.on("notifyAutoAssignUser", (queUserInfo) => { if(/*接受系统分配的客户*/){ 

sdk_engine.acceptAssignUser(queUserInfo._queID, queUserInfo._usrID); //接下来做其他任务......  例如:创建房间 

##### } else { 

//拒绝系统分配的客户 

sdk_engine.rejectAssignUser(queUserInfo._queID, queUserInfo._usrID); } 

}) 

##### //接受系统分配的客户结果 

sdk_engine.on("acceptAssignUserRslt", (sdkErr, cookie) => { 

if(sdkErr === CRVSDK_ERR_DEF.CRVSDKERR_NOERR){ 

" " console.log( 接受系统分配的客户成功 ); 

} else { 

" console.log( 接受系统分配的客户失败,错误码: "+ sdkErr); } 

}) 

##### //拒绝系统分配的客户结果 

sdk_engine.on("rejectAssignUserRslt", (sdkErr, cookie) => { 

if(sdkErr === CRVSDK_ERR_DEF.CRVSDKERR_NOERR){ " " console.log( 接受系统分配的客户成功 ); 

} else { 

" console.log( 接受系统分配的客户失败,错误码: "+ sdkErr); } 

}) 

##### //系统取消已经安排的客户 

sdk_engine.on("notifyAssignUserCanceled", (queID, userID) => { " console.log( 系统取消已经安排的客户,坐席不应该再进入房间......"); }) 

#### 相关API请参考: 

- acceptAssignUser 

- rejectAssignUser 

- acceptAssignUserRslt 

- rejectAssignUserRslt 

- notifyAutoAssignUser 

- notifyAssignUserCanceled 

#### 手动分配模式: 

#### 调用接口: 

//坐席请求客户分为 2步: //1.开启免打扰状态 sdk_engine.setDNDStatus(1): 

|js|
|---|

// 2. 请求分配一个客户 sdk_engine.reqAssignUser(); 

#### 回调通知: 

##### //设置免打扰状态操作失败响应 

js 

sdk_engine.on("setDNDStatusRslt", (sdkErr, cookie) => { if(sdkErr === CRVSDK_ERR_DEF.CRVSDKERR_NOERR) { //设置免打扰成功 } else { //设置免打扰失败 } }) //请求分配客户操作结果 sdk_engine.on("reqAssignUserRslt", (sdkErr, queUserInfo, cookie) => { if(sdkErr === CRVSDK_ERR_DEF.CRVSDKERR_NOERR){ //请求分配客户成功,接下来做其他任务......  例如:创建房间 } else { " console.log( 请求分配客户失败,错误码: " + sdkErr); } }) 

#### 相关API请参考: 

setDNDStatus 

- setDNDStatusRslt reqAssignUser reqAssignUserRslt 

## 6.坐席呼叫客户 

接受系统分配的客户后, 就可以向客户发起呼叫处理, 相关流程参见:呼叫功能 

# 呼叫 

更新时间: 2024/09/14 16:49:23 

## 功能介绍 

实现用户之间的呼叫功能,流程是:A用户先创建一个房间,然后呼叫B用户,如果B用户接受呼叫,AB进入房间进行通 讯。 

注意:在登录成功后才可以使用呼叫功能 

## 主叫 

### 1.创建房间 

调用接口: 

##### //创建房间 

sdk_engine.createMeeting() 

#### 回调通知: 

##### //创建房间成功 

|js js|
|---|

sdk_engine.on("createMeetingSuccess", (meetID, cookie) => { //创建成功,获取房间信息meetObj,用于呼叫他人 

}) 

- //创建房间失败 

sdk_engine.on("createMeetingFail", (sdkErr, cookie) => { 

//创建失败,可以弹出错误提示,不能再执行 进入房间 

- }) 

#### 相关API请参考: 

createMeeting 

createMeetingSuccess 

- createMeetingFail 

### 2.发起呼叫 

注意:当用户A呼叫用户B时,只有B成功登录了,才可以收到被呼叫通知 

#### 调用接口: 

##### //A发起呼叫,邀请用户B进入房间。 

const callID = sdk_engine.call(calledUserID, meetID); 

#### 回调通知: 

##### //呼叫操作的结果 

js js 

sdk_engine.on("callRslt", (callID, sdkErr, cookie) => { if(sdkErr === CRVSDK_ERR_DEF.CRVSDKERR_NOERR) { //呼叫发送成功 } else { //呼叫发送失败 

呼叫发送失败 } }) 

呼叫他人相关API请参考: 

call 

callRslt 

### 3.接受/拒绝呼叫 

回调通知: 

##### //当 B 接受呼叫时,A会收到如下通知: 

js

sdk_engine.on("notifyCallAccepted", (callID, meetID) => { //A此时可以进入房间 sdk_engine.enterMeeting(meetID); }) //当 B 拒绝呼叫时,A会收到如下通知: sdk_engine.on("notifyCallRejected", (callID, sdkErr) => { " " console.log( 客户拒绝呼叫了 ); }) 

呼叫者相关API请参考: 

notifyCallAccepted 

notifyCallRejected 

### 4.挂断 

调用接口: 

js //挂断呼叫 sdk_engine.hungupCall(callID); 回调通知: js sdk_engine.on("hangupCallRslt", (callID, sdkErr, cookie) => { if(sdkErr === CRVSDK_ERR_DEF.CRVSDKERR_NOERR) { //挂断发送成功 sdk_engine.exitMeeting(); //退出房间 } else { //挂断发送失败 } }) //通知被他人挂断 sdk_engine.on("notifyCallHungup", (callID, usrExtDat) => { sdk_engine.exitMeeting(); //退出房间 }) 

#### 相关API请参考: 

hungupCall 

hangupCallRslt 

notifyCallHungup itM ti g 

exitMeeting 

## 被叫 

### 1.被呼叫 

#### 回调通知: 

##### // 通知有呼叫到来 

js 

sdk_engine.on("notifyCallIn", (callID, meetID, callerID) => { if(/* B 接受呼叫, 进入房间*/){ sdk_engine.acceptCall(callID, meetID, meetID); //meetID作为cookie } else { // B 拒绝呼叫 sdk_engine.rejectCall(callID) } }) 

##### //接受呼叫的响应 

sdk_engine.on("acceptCallRslt", (callID, sdkErr, cookie) => { if(sdkErr === CRVSDK_ERR_DEF.CRVSDKERR_NOERR) { //接受呼叫成功 sdk_engine.enterMeeting(cookie); } else { //接受呼叫失败 } }) 

##### //拒绝呼叫的响应 

sdk_engine.on("rejectCallRslt", (callID, sdkErr, cookie) => { if(sdkErr === CRVSDK_ERR_DEF.CRVSDKERR_NOERR) { //拒绝呼叫成功 } else { //拒绝呼叫失败 } }) 

#### 相关API请参考: 

- acceptCall 

- acceptCallRslt rejectCall 

- rejectCallRslt 

- notifyCallIn 

- enterMeeting 

### 2.免打扰 

如果用户当前不希望被呼叫,可以把自己的状态设置为免打扰,注意在免打扰状态下不会被呼叫,但是可以主动发起呼 叫。 

#### 调用接口: 

sdk_engine.setDNDStatus(1); //开启免打扰 

js 

sdk_engine.setDNDStatus(0); //关闭免打扰 

回调通知: 

回调通知 

js 

##### //设置免打扰状态操作失败响应 

sdk_engine.on("setDNDStatusRslt", (sdkErr, cookie) => { if(sdkErr === CRVSDK_ERR_DEF.CRVSDKERR_NOERR) { 

//设置免打扰成功 

} else { //设置免打扰失败 } }) 

#### 相关API请参考: 

setDNDStatus 

setDNDStatusRslt 

# 本地直播推流 

更新时间: 2024/09/14 16:49:24 

## 功能介绍 

用于1个或多个主播实时连麦互动,然后图像和声音将在SDK本地进行混合,然后直接向CDN流媒体服务器推流,直播观众 就可以获取RTMP或HLS流观看直播了。 

## 1.创建混图器 

左右布局示例图 

#### 接口调用: 

```arkts
import { CRLocMixerCfgObj, CRMixerContentObj, CRVSDK_ERR_DEF } from '@cloudroom/hormony_rtcsdk'; const mixerID = '1'; //混图器唯一标识 //混图器参数配置 const mixerCfgObj: CRLocMixerCfgObj = { width: 1280, height: 720, frameRate: 15, bitRate: 1000000, defaultQP: 26, gop: 15, } const mixerContentsObj: CRMixerContentObj[] = [{ type: 0, top: 0, left: 0, width: 640, height: 720, param: { camid: "userID1.-1" } }, { type: 0, top: 0, left: 640, width: 640, 
```

js 

height: 720 

height: 720, param: { camid: "userID2.-1" } }] 

// 创建混图器, 设置混图器编号为1 

```arkts
const sdkErr = sdk_engine.createLocMixer(mixerID, mixerCfgObj, mixerContentsObj); if (sdkErr === CRVSDK_ERR_DEF.CRVSDKERR_NOERR) { //创建成功 } 
```

#### 相关API请参考: 

#### createLocMixer 

#### 相关结构定义请参考: 

- CRLocMixerCfgObj 

- CRMixerContentObj 错误码 

## 2.添加直播推流 

接口调用: 

js import { CRLocMixerOutputObj, CRVSDK_MIXER_OUTPUT_TYPE, CRVSDK_ERR_DEF } from '@cloudroom/hormony_rtcsdk'; 

##### //推流到A,B两个直播平台 

```arkts
const outputObjs: CRLocMixerOutputObj[] = []; outputObjs.push({ type: CRVSDK_MIXER_OUTPUT_TYPE.CRVSDK_MIXER_OUTPUT_LIVE, liveUrl: "rtmp://A/xxx" }); 
```

outputObjs.push({ type: CRVSDK_MIXER_OUTPUT_TYPE.CRVSDK_MIXER_OUTPUT_LIVE, liveUrl: "rtmp://B/xxx" 

}); 

const errCode = sdk_engine.addLocMixerOutput("1", outputObjs) if (errCode === CRVSDK_ERR_DEF.CRVSDKERR_NOERR) { //启动成功 } 

#### 相关API请参考: 

#### addLocMixerOutput 

#### 相关结构定义请参考: 

CRLocMixerOutputObj 

## 3.直播推流回调处理 

import { CRLocMixerOutputInfoObj } from '@cloudroom/hormony_rtcsdk'; 

js 

sdk_engine.on("notifyLocMixerOutputInfo", (mixerID, nameOrUrl, outputInfo) => { if (outputInfo.state === CRVSDK_LOCMIXER_OUTPUT_STATE.CRVSDK_LOCMO_FAIL) { //推流出错,errCode中有错误原因 } 

} }) 

#### 相关API请参考: 

notifyLocMixerOutputInfo 

## 4. 更新直播内容 

画中画布局示例图 

#### 接口调用: 

import { CRMixerContentObj, CRVSDK_ERR_DEF } from '@cloudroom/hormony_rtcsdk'; 

js 

// 录制参数列表中,越靠后的元素会覆盖之前的元素 const mixerContents: CRMixerContentObj[] = [{ //大窗的视频 type: 0, top: 0, left: 0, width: 1280, height: 720, param: { camid: "userID2.-1" } }, { //小窗口视频 type: 0, top: 1280 - 256, left: 720 - 144, width: 256, height: 144, param: { camid: "userID1.-1" } }] 

// 更新混图器 

// 更新混图器 const sdkErr = sdk_engine.updateLocMixerContent(mixerID, mixerContents); if (sdkErr === CRVSDK_ERR_DEF.CRVSDKERR_NOERR) { //更新成功 } 

#### 相关API请参考: 

updateLocMixerContent 

## 5.结束 

//销毁混图器, 输出自动结束 

js 

sdk_engine.destroyLocMixer(mixerID); 

#### 相关API请参考: 

destroyLocMixer 

# 云端直播推流 

更新时间: 2024/09/14 16:49:24 

## 功能介绍 

用于多个主播实时连麦互动。技术实现上,我们会把房间里多个主播的音视频在服务器合成一路流后推流到CDN流媒体服 务器,直播观众可以获取RTMP或HLS流观看直播。 

#### 互动直播架构图: 

## 1.创建直播间并获得推流地址 

创建直播间请参见:Web API 创建直播。 

获取直播推流地址请参见:Web API 获取推流地址。 

## 2.开始云端直播推流 

#### 直播左右布局示例图: 

调用接 

调用接口: 

##### import { CRCloudMixerCfgObj } from '@cloudroom/hormony_rtcsdk'; 

js

//配置混图器编码参数:1280*720, 15帧, 推流到两个地方 

const cloudMixerCfg: CRCloudMixerCfgObj = { mode: 0, 

videoFileCfg: { 

svrPathName: "rtmp://A/xxx", //带路径的文件名,文件格式支持:mp4、flv、ts、avi、rtmp://、rtsp://,可选一个或多个,以“;”分隔 ;示例:”/xxx/xxx.mp4;rtmp://xxx1;rtmp://xxx2;” 

vWidth: 1280, //视频宽度 

vHeight: 720, //视频高度 layoutConfig: [{ type: 0, // 录制视频 

left: 0, // 在混图画面中的区域(水平位置) 

top: 0, // 在混图画面中的区域(垂直位置) 

width: 640, // 在混图画面中的区域宽 

height: 720, // 在混图画面中的区域高 

param: { camid: 'userID1.-1' } //请见后面param支持的参数; 

}, { 

type: 0, // 录制视频 

left: 640, // 在混图画面中的区域(水平位置) 

top: 0, // 在混图画面中的区域(垂直位置) 

width: 640, // 在混图画面中的区域宽 

height: 720, // 在混图画面中的区域高 

param: { camid: 'userID2.-1' } //请见后面param支持的参数; },] //布局内容列表 

} } 

##### //启动云端直播推流 

const mixerID = sdk_engine.createCloudMixer(cloudMixerCfg); 

//开启云端直播出错, 关注回调createCloudMixerFailed sdk_engine.on("createCloudMixerFailed", (mixerID) => { 

##### }) 

##### //通知云端录制/推流状态变化 

sdk_engine.on("notifyCloudMixerStateChanged", (mixerID, state, exParam, operUserID) => { 

##### }) 

#### 相关API请参考: 

#### createCloudMixer 

createCloudMixerFailed 

notifyCloudMixerStateChanged 

## 3.更新互动直播内容 

更新成画中画布局示例图: 

接口调用: 

##### import { CRCloudMixerCfgObj, CRVSDK_ERR_DEF } from '@cloudroom/hormony_rtcsdk'; 

js 

```arkts
const cloudMixerCfg: CRCloudMixerCfgObj = { mode: 0, videoFileCfg: { svrPathName: "rtmp://A/xxx", //带路径的文件名,文件格式支持:mp4、flv、ts、avi、rtmp://、rtsp://,可选一个或多个,以“;”分隔 ;示例:”/xxx/xxx.mp4;rtmp://xxx1;rtmp://xxx2;” vWidth: 1280, //视频宽度 vHeight: 720, //视频高度 layoutConfig: [{ //大视频窗口 type: 0, top: 0, left: 0, width: 1280, height: 720, keepAspectRatio: 1, param: { camid: "userID1.-1" } }, { //小视频窗口 type: 0, top: 495, left: 880, width: 400, height: 225, keepAspectRatio: 1, param: { camid: "userID2.-1" } }] } } 
```

##### //更新云端直播推流画面 

```arkts
const sdkErr = sdk_engine.updateCloudMixerContent(mixerID, cloudMixerCfg); //mixerID由createCloudMixer接口返回 if (sdkErr === CRVSDK_ERR_DEF.CRVSDKERR_NOERR) { //没有错误 } 
```

#### 相关API请参考: 

updateCloudMixerContent 

相关结构定义请参考: 

CRCloudMixerCfgObj 

错误码 

## 4.观众观看直播 

通过 播放器SDK观看直播。 

## 5.停止互动直播 

停止云端直播推流后,会触发事件notifyCloudMixerStateChanged 

接口调用: 

sdk_engine.destroyCloudMixer(mixerID) 

js 

相关API请参考: 

- destroyCloudMixer 

notifyCloudMixerStateChanged 

## 6.回放点播 

通过 云屋点播API回放点播。 

# 点对点消息 

更新时间: 2024/09/14 16:49:24 

## 功能介绍 

实现点对点的透明消息发送功能, 根据发送内容可选择:发送命令数据, 发送内存数据二种类型。 

## 1.发送命令数据 

此接口发送的数据不能被cancelSend,一次性发送,也不会有进度通知。 

调用接口: 

##### //发送小块数据,taskId为分配的任务ID 

const taskId = sdk_engine.sendCmd(targetUserId, data); 

#### 回调通知: 

##### //发送数据的结果通知 

js js 

sdk_engine.on("sendCmdRslt", (taskId, sdkErr, cookie) => { if(sdkErr !== CRVSDK_ERR_DEF.CRVSDKERR_NOERR){ " " console.log( 发送失败,错误码: + sdkErr); } }) 

##### //收到远端命令数据 

sdk_engine.on("notifyCmdData", (sourceUserId, data) => { //sourceUserId发送者 //data数据内容 }) 

#### 相关API请参考: 

sendCmd 

sendCmdRslt 

notifyCmdData 

#### 相关结构定义请参考: 

错误码 

## 2.发送内存数据 

分块发送,进度通知事件notifySendProgress, 调用cancelSend取消发送。 

#### 调用接口: 

##### //发送内存数据,taskId为分配的任务ID 

js 

const taskId = sdk_engine.sendBuffer(UID, data); 

#### 回调通知: 

js 

//发送数据的结果通知 

dk i ( dB ff R l ( kId dkE ki ) { 

sdk_engine.on("sendBufferRslt", (taskId, sdkErr, cookie) => { if(sdkErr !== CRVSDK_ERR_DEF.CRVSDKERR_NOERR){ " " console.log( 发送失败,错误码: + sdkErr); } }) 

//收到远端数据 

sdk_engine.on("notifyCmdData", (sourceUserId, data) => { //sourceUserId发送者 //data数据内容 }) 

#### 相关API请参考: 

sendBuffer 

- sendBufferRslt 

- notifySendProgress 

- notifyBufferData 

## 3.发送文件 

分块发送,进度通知事件notifySendProgress, 调用cancelSend取消发送。 

#### 调用接口: 

const taskId = sdk_engine.sendFile(targetUserId, locPathFileName); 

#### 回调通知: 

##### //发送文件的结果通知 

js js 

sdk_engine.on("sendFileRslt", (taskId, fileName, sdkErr, cookie) => { if(sdkErr !== CRVSDK_ERR_DEF.CRVSDKERR_NOERR){ 

- //发送失败,错误码:sdkErr; 

- } else { 

//成功 

} 

}) 

##### //收到远端的文件通知 

sdk_engine.on("notifyFileData", (sourceUserId, tmpFile, orgFileName) => { //sourceUserId发送者 

//tmpFile本地临时文件 

//orgFileName原文件名(不带路径) 

}) 

#### 相关API请参考: 

#### sendFile 

sendFileRslt 

- notifySendProgress 

- notifyFileData 

## 4.取消发送 

#### 调用接口: 

js 

//取消发送数据,taskId为要取消的任务ID 

cancelSend(taskId); 

#### 回调通知: 

sdk_engine.on("cancelSendRslt", (taskId, sdkErr, cookie) => { if(sdkErr !== CRVSDK_ERR_DEF.CRVSDKERR_NOERR){ //发送失败,错误码:sdkErr; 

js 

} else { //取消成功 } }) 

#### 相关API请参考: 

cancelSend 

cancelSendRslt 

# 房间广播消息 

更新时间: 2024/09/14 16:49:24 

## 功能介绍 

实现房间内消息广播。此接口只能在进入房间后才能使用,房间内所有在线人员都能收到。 

## 发送房间广播消息 

#### 调用接口: 

```arkts
interface Msg { CmdType: "IM", IMMsg: string } const msg: Msg = { CmdType: "IM", IMMsg: "xxxxxxxxxxx" } sdk_engine.sendMeetingCustomMsg(JSON.stringify(msg)); //发送自定义广播消息 
```

#### 回调通知: 

##### //发送数据的结果通知 

|js|
|---|
|js|

sdk_engine.on("sendMeetingCustomMsgRslt", (sdkErr, cookie) => { if(sdkErr !== CRVSDK_ERR_DEF.CRVSDKERR_NOERR){ ` ` console.log( 发送失败,错误码:${sdkErr} ); } }) 

#### 相关API请参考: 

sendMeetingCustomMsg 

sendMeetingCustomMsgRslt 

#### 相关结构定义请参考: 

错误码 

## 处理房间广播消息 

##### //通知收到房间广播消息 

|js|
|---|

sdk_engine.on("notifyMeetingCustomMsg", (fromUserID, msg) => { }) 

#### 相关API请参考: 

notifyMeetingCustomMsg 

# 房间和成员自定义属性 

更新时间: 2024/09/14 16:49:24 

## 功能介绍 

支持增删改查房间自定义属性、房间内人员自定义属性 

## 1.设置房间属性 

调用接口: 

sdk_engine.setMeetingAttrs(JSON.stringify({ key1: "value1", //即将设置的属性 key2: "value2" }), JSON.stringify({ notifyAll: 1, //立即通知所有人 })); 

#### 回调通知: 

##### //设置会议属性结果 

js js 

sdk_engine.on("setMeetingAttrsRslt", (sdkErr, cookie) => { if(sdkErr !== CRVSDK_ERR_DEF.CRVSDKERR_NOERR){ ` ` console.log( 设置房间属性失败,错误码: ${sdkErr} ) } }) 

#### 相关API请参考: 

- setMeetingAttrs 

- setMeetingAttrsRslt 

- notifyMeetingAttrsChanged 

相关结构定义请参考: 

错误码 

## 2.获取所有的房间属性 

#### 调用接口: 

//获取的所有属性 sdk_engine.getMeetingAllAttrs(); 

#### 回调通知: 

//获取所以的房间属性成功 sdk_engine.on("getMeetingAllAttrsSuccess", (attrs, cookie) => { }) //获取所以的房间属性失败 sdk_engine.on("getMeetingAllAttrsFail", (sdkErr, cookie) => { ` ` console.log( 获取所有的房间属性失败,错误码: ${sdkErr} ) }) 

js js 

#### 相关API请参考: 

- getMeetingAllAttrs 

- getMeetingAllAttrsSuccess 

- getMeetingAllAttrsFail 

- notifyMeetingAttrsChanged 

## 3.获取房间特定属性 

#### 调用接口: 

##### //获取的指定的属性 

const keys = ["MeetingName", "CompanyName"]; sdk_engine.getMeetingAttrs(JSON.stringify(keys)); 

#### 回调通知: 

##### //获取到特定的房间属性成功 

js js 

sdk_engine.on("getMeetingAttrsSuccess", (attrs, cookie) => { ` ` console.log( 获取特定的房间属性成功 ) }) sdk_engine.on("getMeetingAttrsFail", (sdkErr, cookie) => { ` ` console.log( 获取特定的房间属性失败,错误码: ${sdkErr} ) }) 

#### 相关API请参考: 

- getMeetingAttrs 

- getMeetingAttrsSuccess 

- getMeetingAttrsFail 

## 4.添加或更新属性 

#### 调用接口: 

js sdk_engine.addOrUpdateMeetingAttrs(JSON.stringify({ key1: "value1", //即将设置的属性 key2: "value2" }), JSON.stringify({ notifyAll: 1, //全部通知 })); 回调通知: js sdk_engine.on("addOrUpdateMeetingAttrsRslt", (sdkErr, cookie) => { if(sdkErr !== CRVSDK_ERR_DEF.CRVSDKERR_NOERR){ ` ` console.log( 更新房间属性失败,错误码: ${sdkErr} ) } }) 

#### 相关API请参考: 

addOrUpdateMeetingAttrs 

addOrUpdateMeetingAttrsRslt notifyMeetingAttrsChanged 

## 5.删除房间特定属性 

调用接口: 

```arkts
const keys = ["key1", "key2"]; sdk_engine.delMeetingAttrs(JSON.stringify(keys), JSON.stringify({ notifyAll: 1 })); 
```

#### 回调通知: 

sdk_engine.on("delMeetingAttrsRslt", (sdkErr, cookie) => { if(sdkErr !== CRVSDK_ERR_DEF.CRVSDKERR_NOERR){ ` ` console.log( 删除房间属性失败,错误码: ${sdkErr} ) } }) 

#### 相关API请参考: 

- delMeetingAttrs 

- delMeetingAttrsRslt notifyMeetingAttrsChanged 

## 6.清除房间全部属性 

调用接口: 

sdk_engine.clearMeetingAttrs(JSON.stringify({ notifyAll: 1 })); 

#### 回调通知: 

sdk_engine.on("clearMeetingAttrsRslt", (sdkErr, cookie) => { if(sdkErr !== CRVSDK_ERR_DEF.CRVSDKERR_NOERR){ ` ` console.log( 清除房间属性失败,错误码: ${sdkErr} ) } }) 

js js js js 

#### 相关API请参考: 

clearMeetingAttrs 

clearMeetingAttrsRslt 

- notifyMeetingAttrsChanged 

## 7.设置成员属性 

#### 调用接口: 

```arkts
const userID = 'harMonyOS_xxxx'; sdk_engine.setUserAttrs(userID, JSON.stringify({ key1:"value1", key2:"value2" }), JSON.stringify({ notifyAll: 1 
```

|js|
|---|

y })) 

#### 回调通知: 

sdk_engine.on("setUserAttrsRslt", (sdkErr, cookie) => { if(sdkErr !== CRVSDK_ERR_DEF.CRVSDKERR_NOERR){ ` ` console.log( 设置成员属性失败,错误码: ${sdkErr} ) } }) 

js 

#### 相关API请参考: 

setUserAttrs 

setUserAttrsRslt 

notifyUserAttrsChanged 

## 8.获取当前指定成员所有属性 

#### 调用接口: 

const userIDs = ["userID1", "userID2"]; //传空字符串代表获取所有属性,传数组代表或者特定的成员属性 "" sdk_engine.getUserAttrs(JSON.stringify(userIDs), || JSON.stringify(["key1","key2"])); 

js 

#### 回调通知: 

##### //获取房间内成员属性成功 

js 

sdk_engine.on("getUserAttrsSuccess", (attrs, cookie) => { 

}) //获取房间内成员属性失败 sdk_engine.on("getUserAttrsFail", (sdkErr, cookie) => { ` ` console.log( 获取特定的成员属性失败,错误码: ${sdkErr} ) }) 

#### 相关API请参考: 

getUserAttrs 

getUserAttrsSuccess 

getUserAttrsFail 

## 9.添加或更新指定成员指定的属性 

#### 调用接口: 

```arkts
const userID = 'harMonyOS_xxxx'; js const options = ; //全部通知 sdk_engine.addOrUpdateUserAttrs(userID, JSON.stringify({ key1: "value1", key2: "value2" }), JSON.stringify({ notifyAll: 1 })); 
```

通 

回调通知: 

##### //更新成员属性的结果 

|js|
|---|

sdk_engine.on("addOrUpdateUserAttrsRslt", (sdkErr, cookie) => { if(sdkErr !== CRVSDK_ERR_DEF.CRVSDKERR_NOERR){ ` ` console.log( 更新成员属性失败,错误码: ${sdkErr} ) } }) 

#### 相关API请参考: 

addOrUpdateUserAttrs 

addOrUpdateUserAttrsRslt 

notifyUserAttrsChanged 

## 10.删除指定成员的指定属性 

#### 调用接口: 

```arkts
const userID = 'harMonyOS_xxxx'; const keys = ["key1","key2"]; sdk_engine.delUserAttrs(userID, JSON.stringify(keys), JSON.stringify({ notifyAll: 1 })); 
```

#### 回调通知: 

##### //删除成员属性的结果 

js js 

sdk_engine.on("delUserAttrsRslt", (sdkErr, cookie) => { if(sdkErr !== CRVSDK_ERR_DEF.CRVSDKERR_NOERR){ ` ` console.log( 删除房间属性失败,错误码: ${sdkErr} ) } }) 

#### 相关API请参考: 

delUserAttrs 

delUserAttrsRslt 

notifyUserAttrsChanged 

## 11.清除当前指定成员全部属性 

调用接口: 

```arkts
const userID = "harMonyOS_xxx"; //用户ID sdk_engine.clearUserAttrs(userID, JSON.stringify({ notifyAll: 1 })); 
```

#### 回调通知: 

##### //清空指定成员的属性的结果 

js js 

sdk_engine.on("clearUserAttrsRslt", (sdkErr, cookie) => { if(sdkErr !== CRVSDK_ERR_DEF.CRVSDKERR_NOERR){ ` ` console.log( 清除特定成员属性失败,错误码: ${sdkErr} ) } }) 

相关API请参考: 

相关 请参考 

#### clearUserAttrs 

- clearUserAttrsRslt 

- notifyUserAttrsChanged 

## 12.清除当前房间内所有成员全部属性 

#### 调用接口: 

sdk_engine.clearAllUserAttrs(JSON.stringify({ notifyAll: 1 })); 

js 

#### 回调通知: 

##### //清空所有成员的属性的结果 

js 

sdk_engine.on("clearAllUserAttrsRslt", (sdkErr, cookie) => { if(sdkErr !== CRVSDK_ERR_DEF.CRVSDKERR_NOERR){ ` ` console.log( 清除所有成员属性失败,错误码: ${sdkErr} ) } }) 

#### 相关API请参考: 

clearAllUserAttrs 

clearAllUserAttrsRslt 

notifyUserAttrsChanged 

更新时间: 2024/09/14 16:49:24 

# SIP/H.323设备支持 

## 功能介绍 

云屋SDK支持通过SIP和H.323标准协议与硬件视频会议系统或PSTN电话系统对接,可支持以下几种场景: 

1. SDK呼叫单个对接端:从SDK端向对接端发起呼叫,对接端用户应答后与SDK一起进入房间; 

2. SDK邀请多个对接端:SDK端先进入房间,然后向一个或多个对接端用户发起邀请,被邀请用户接受邀请后加入该房 间; 

3. 对接端呼叫SDK:SDK端在线,对接端向SDK端发起呼叫,SDK端应答后与对接端一起加入房间; 

4. 对接端直接加入房间:SDK房间提前建好,对接端呼叫房间号后加入房间; 

- 以上对接端可以是支持SIP/H.323的硬件终端、传统电话、MCU会议 

## 功能开通 

1. 联系商务开通SIP/H.323对接功能,或在网站咨询客服。 

2. 登录 SDK后台 ,选择SIP配置/H.323配置,打开配置开关;如需配置中继模式,则填入对应的终端地址、端口号、协 议(且SIP设备支持选择协议)。 

SIP配置: 

- H.323配置: 

## SDK呼叫单个对接端 

注意: 

注意: 

1. 当用户A呼叫SIP/H.323设备时,对端设备需要在线,如果呼叫的是E.164号码,需要对应设备已注册,否则被呼叫端无法收到 被呼叫的消息;设备收到呼叫消息后,根据其自身设置的应答机制,会自动进入房间或在按下接听后进入房间。 

2. 如果在 功能开通 的"SIP配置"或者"H.323配置"界面配置了中继地址,呼叫时不需要填写对端设备IP,直接填写"sip:号码"或者" h323:号码"即可 

#### 调用接口: 

//被呼叫的SIP/H.323设备的IP或E.164号码,以sip:或h323:为前缀 const calledUID = "sip:192.168.0.10"; // 呼叫IP为192.168.0.10的SIP设备 

js 

// const calledUID = "h323:149689338";  // 呼叫E.164号码为14989338的H.323设备 const meetID = 88888888; sdk_engine.call(calledUID, meetID); 

#### 回调通知: 

sdk_engine.on("callRslt", (callID, sdkErr, cookie) => { 

js 

if(sdkErr === CRVSDK_ERR_DEF.CRVSDKERR_NOERR) { 

//呼叫操作失败 

- } else { 

- //呼叫操作成功 

- } 

}) 

呼叫相关API请参考: 

call 

callRslt 

## SDK邀请多个对接端 

注意: 

注意: 

1. 仅当用户A已经进入房间议,才可以邀请SIP/H.323设备。 

2. 当用户A邀请SIP/H.323设备时,对应设备需要在线,如果呼叫的是E.164号码,需要对应设备已注册,否则被呼叫端无法收到 被呼叫的消息;设备收到呼叫消息后,根据其自身设置的应答机制,会自动进入房间或在按下接听后进入房间。 

被呼叫的消息;设备收到呼叫消息后,根据其自身设置的应答机制,会自动进入房间或在按下接听后进入房间。 

3. 如果在 功能开通 的"SIP配置"或者"H.323配置"界面配置了中继地址,邀请时不需要填写对端设备IP,直接填写"sip:号码"或者" h323:号码"即可 

#### 调用接口: 

interface Meeting { ID: number } interface UsrExtDat { meeting: Meeting } 

js

//被邀请的SIP/H.323设备的IP或E.164号码,以sip:或h323:为前缀 const inviteeUsrID = "sip:192.168.0.10"; // 邀请IP为192.168.0.10的SIP设备 // const inviteeUsrID = "h323:149689338";  // 邀请E.164号码为14989338的H.323设备 const usrExtDat: UsrExtDat = { meeting: { ID: 88888888 } }; const inviteID = sdk_engine.invite(inviteeUsrID, JSON.stringify(usrExtDat)); 

#### 回调通知: 

js

##### //邀请他人的结果 

sdk_engine.on("inviteRslt", (inviteID, sdkErr, cookie) => { if(sdkErr === CRVSDK_ERR_DEF.CRVSDKERR_NOERR) { //邀请发送成功 

- } else { 

//邀请发送失败 } }) 

##### //通知邀请被接受 

sdk_engine.on("notifyInviteAccepted", (inviteID, usrExtDat) => { 

- //邀请被接受,等待被邀请方进入房间等处理 

}) 

##### //通知邀请被拒绝 

sdk_engine.on("notifyInviteRejected", (inviteID, sdkErr, usrExtDat) => { 

- //邀请被拒绝,弹出提示框等处理 

}) 

#### 相关API请参考: 

invite 

inviteRslt 

- notifyInviteAccepted 

notifyInviteRejected 

## 对接端呼叫SDK 

被呼叫的SDK端收到被他人呼叫通知,具体请参考 SDK被呼叫 部分 

## 对接端直接加入房间 

下面以 Linphone 为例演示直接加入房间的方法: 

1. 二次拨号方式,呼叫 sip:116.63.139.166 或者 h323:116.63.139.166 ,呼通后根据界面提示输入房间号,再输 入"#"键以进入对应房间 

拨号界面 

输入房间号界面 

2. 直接呼叫房间号方式,呼叫 10252565@116.63.139.166 ,进入对应房间 

## 配置终端 

下面以宝利通硬终端和Linphone软终端为例,说明终端的配置方法。 

### 宝利通终端 

登录web管理页面,左侧导航栏选择管理设置→网络→IP网络 

启用SIP呼叫,注:如果在SDK后台配置SIP时选择了协议,此处应选择一致的传输协议 

#### 启用H.323呼叫: 

### Linphone软终端 

打开偏好设置,选择视频,在下方添加H264解码器并确保开启 

# 监控设备对接 

更新时间: 2024/09/14 16:49:24 

## 功能介绍 

云屋SDK支持通过邀请的方式把监控设备加入到房间,房间内用户可以订阅观看监控设备的视频,也可以对监控设备的视 频进行录制。 目前已支持的协议有:RTSP、RTMP、ONVIF、GB28181。 

## 使用方法 

### 邀请监控设备 

注意: 

注意: 

1. SDK需要先进入房间,才可以发起邀请。 

2. 本功能仅用于私有化部署环境,因为需要服务器能直接访问监控设备的IP地址,也就需要服务器和监控设备部署在同一个内网 环境。 

3. GB28181协议需要对接注册,用法详询销售. 

#### 调用接口: 

##### //被邀请的监控设备的url 

js 

const targetUrl = "rtsp://192.168.1.163:554/live/av0"; //string targetUrl = "rtmp://192.168.1.2/live/livestream0"; 

//string targetUrl = "onvif://admin:8888@192.168.1.3:8080/live"; 

//string targetUrl = "gb28181:44010200402000000123";  //44010200402000000123表示通道号 const usrExtDat = { meeting: { ID: xxx }, devInfo: { userID: "会议中用户ID", nickName: "会议中用户昵称" } }; const inviteID = sdk_engine.invite(targetUrl, JSON.stringify(usrExtDat)); 

#### 回调通知: 

##### //邀请他人的结果 

js 

sdk_engine.on("inviteRslt", (inviteID, sdkErr, cookie) => { if(sdkErr === CRVSDK_ERR_DEF.CRVSDKERR_NOERR) { 

//邀请发送成功 

- } else { 

- //邀请发送失败 

- } 

}) 

#### 相关API请参考: 

invite 

inviteRslt 

设备接受邀请 

#### 回调通知: 

##### //通知邀请被接受 

js 

sdk_engine.on("notifyInviteAccepted", (inviteID, usrExtDat) => { //邀请被接受,等待被邀请方进入房间等处理 

}) 

##### //通知邀请被拒绝 

sdk_engine.on("notifyInviteRejected", (inviteID, sdkErr, usrExtDat) => { //邀请被拒绝,弹出提示框等处理 

}) 

#### 相关API请参考: 

notifyInviteAccepted 

notifyInviteRejected 

### 设备进入房间 

#### 回调通知: 

##### //通知设备进入房间 

js 

sdk_engine.on("notifyUserEnterMeeting", (userID) => { 

//设备做为一个成员进入到房间中, 此时可观看它的视频, 也可以在不需要的时候,把它请出房间 }) 

#### 相关API请参考: 

notifyUserEnterMeeting 

kickout 

更新时间: 2024/09/14 16:49:25 

# API 

## 模块 

|实例模式|获取实例|
|---|---|
||基础函数|
||登录/注销|
||透明通道|
|房间外接口|队列管理|
||呼叫|
||邀请|
||房间管理|
||进出房间|
||房间成员管理|
||房间属性|
||用户属性|
||音频管理|
|房间内接口|视频管理|
||视频自定义采集|
||虚拟视频设备|
||影音共享|
||屏幕共享|
||本地录制/本地直播|
||云端录制/互动直播|

### 获取实例 

|方式||接口||描述|
|---|---|---|---|---|
|主调|create||获取实例||

### 基础函数 

|方式|接口|描述|
|---|---|---|
||getVersion|获取SDK版本号|
|主调|on|注册SDK回调函数|
||off|销毁SDK回调函数|
||destroy|销毁SDK实例|

### 登录/注销 

|方式|接口|描述|
|---|---|---|
||setNetworkProxy|设置网络代理|
||login|登录|
||logout|登出|
||updateToken|更新token|
||getUserAuthErrCode|第三方鉴权错误码获取|
|主调|getUserAuthErrDesc|第三方鉴权错误原因获取|
||setDNDStatus|设置免打扰|
||getUserStatus|获取本AppID下的所有登录用户的状态信息|
||getOneUserStatus|获取本AppID下指定用户的在线状态|
||startUserStatusNotify|开启AppID下的用户登录状态消息推送|
||stopUserStatusNotify|关闭appID下的用户在线状态消息推送|
||loginRslt|登录结果回调|
||notifyTokenWillExpire|Token即将失效的通知,失效前30秒通知|
||notifyLineOff|通知本端SDK掉线|
||setDNDStatusRslt|设置免打扰结果|
|回调|getUserStatusSuccess|获取用户登录状态信息成功|
||getUserStatusFail|获取用户登录状态信息失败|
||notifyUserStatus|通知某用户登录状态变化|
||startUserStatusNotifyRslt|开启用户状态通知结果|
||stopUserStatusNotifyRslt|关闭用户状态通知结果|

### 透明通道 

|方式|接口|描述|
|---|---|---|
||sendCmd|发送点对点消息|
|主调|sendBuffer|发送点对点大数据|
||sendFile|发送文件|
||cancelSend|取消大数据、文件的发送|
||sendCmdRslt|发送点对点消息结果|
||sendBufferRslt|发送点对点大数据结果|
||sendFileRslt|发送点对点文件结果|
|回调|cancelSendRslt|取消发送结果|
||notifySendProgress|通知大数据、文件的发送进度|
||notifyCmdData|通知收到点对点透明通道消息|

|方式|notifyBufferData 接口|通知收到点对点大数据 描述|
|---|---|---|
||notifyFileData|通知收到点对点文件|

### 队列管理 

|方式|接口|描述|
|---|---|---|
||initQueueDat|初始化队列功能|
||getAllQueueInfo|获取AppID下的所有队列基础信息|
||getQueueStatus|获取指定队列的排队状况|
||getQueuingInfo|获取我的排队信息|
||getServingQueues|获取我服务的所有队列|
||startQueuing|客户开始排队|
|主调|stopQueuing|客户停止排队|
||startService|座席开始服务某队列|
||stopService|座席停止服务某队列|
||reqAssignUser|座席手动分配下一位客户(开启免打扰后使用)|
||reqAssignUser2|座席手动分配指定客户(开启免打扰后使用)|
||acceptAssignUser|接受系统分配的客户|
||rejectAssignUser|拒绝系统分配的客户|
||initQueueDatRslt|初始化队列功能结果|
||notifyQueueStatusChanged|队列排队状态更新|
||notifyQueuingInfoChanged|我的排队信息更新|
||startQueuingRslt|客户开始排队结果|
||stopQueuingRslt|客户停止排队结果|
||startServiceRslt|座席开始服务结果|
|回调|stopServiceRslt|座席开始服务结果|
||acceptAssignUserRslt|接受系统分配的客户结果|
||rejectAssignUserRslt|拒绝系统分配的客户结果|
||reqAssignUserRslt|座席手动分配客户结果|
||notifyAutoAssignUser|座席自动分配客户结果|
||notifyAssignUserCanceled|通知分配的客户取消了|
||notifyUserEnterQueue|通知客户进入了某队列|
||notifyUserLeaveQueue|通知客户离开了某队列|

### 呼叫 

|方式||接口||描述|
|---|---|---|---|---|
||call||发起呼叫||

|方式|acceptCall 接口|接受他人的呼叫 描述|
|---|---|---|
|主调|rejectCall|拒接他人的呼叫|
||hungupCall|挂断通话|
||callMoreParty|发起多方呼叫(或呼转)|
||cancelCallMoreParty|取消多方呼叫|
||callRslt|发起的呼叫结果|
||acceptCallRslt|接受他人呼叫的结果|
||rejectCallRslt|拒绝他人呼叫的结果|
||hangupCallRslt|挂断通话结果|
||notifyCallIn|通知呼入|
|回调|notifyCallAccepted|通知呼叫被接受|
||notifyCallRejected|通知呼叫被拒接|
||notifyCallHungup|通知呼叫被挂断|
||callMorePartyRslt|发起多方呼叫结果|
||cancelCallMorePartyRslt|取消多方呼叫结果|
||notifyCallMorePartyStatus|通知多方呼叫状态|

### 邀请 

|方式|接口||描述|
|---|---|---|---|
||invite|邀请他人||
|主调|acceptInvite|接受邀请||
||rejectInvite|拒接邀请||
||cancelInvite|取消邀请||
||inviteRslt|邀请他人结果||
||cancelInviteRslt|取消邀请结果||
||acceptInviteRslt|接受邀请结果||
|回调|rejectInviteRslt|拒接邀请结果||
||notifyInviteIn|通知收到邀请||
||notifyInviteAccepted|通知邀请被接受||
||notifyInviteRejected|通知邀请被拒接||
||notifyInviteCanceled|通知邀请被取消||

### 房间管理 

|方式|接口||描述|
|---|---|---|---|
|主调|createMeeting destroyMeeting|创建房间 销毁房间||

|~~方式~~|~~destroyMeeting~~ ~~createMeetingSuccess~~ ~~接口~~|~~销毁房间~~ ~~通知创建房间成功~~|~~描述~~|
|---|---|---|---|
|回调|createMeetingFail|通知创建房间失败||
||destroyMeetingRslt|销毁房间结果||

### 进出房间 

|方式|接口|描述|
|---|---|---|
||enterMeeting|进入房间|
|主调|exitMeeting|离开房间|
||getNetState|获取当前网络状态评分|
||getNetState2|获取网络状态详细信息|
||enterMeetingRslt|进入房间结果|
|回调|notifyMeetingStopped|通知房间已结束|
||notifyMeetingDropped|与房间断开|
||notifyNetStateChanged|通知本端与房间服务器的网络状态变化|

### 房间成员管理 

|方式|接口|描述|
|---|---|---|
||isUserInMeeting|检查用户是否在房间中|
||getAllMembers|获取房间中所有成员信息|
|主调|getMemberInfo|获取房间中指定成员信息|
||setNickName|修改房间中成员昵称|
||kickout|将他人请出房间|
||sendMeetingCustomMsg|房间内发送广播消息|
||notifyUserEnterMeeting|通知有人进入房间|
||notifyUserLeftMeeting|通知有人离会|
||setNickNameRslt|修改昵称结果|
|回调|notifyNickNameChanged|通知昵称变化|
||kickoutRslt|请出房间结果|
||sendMeetingCustomMsgRslt|发送房间内广播消息结果|
||notifyMeetingCustomMsg|通知房间内广播消息|

### 房间属性 

|方式|接口||描述|
|---|---|---|---|
||getMeetingAllAttrs|获取所有房间属性||
||getMeetingAttrs|获取部份房间属性||
||setMeetingAttrs|重置所有房间属性||

|主 |~~setMeetingAttrs~~ |~~重置所有房间属性~~ |
|---|---|---|
|调 方式|~~接口~~|~~描述~~|
||~~addOrUpdateMeetingAttrs~~ |~~添加或更新房间属性~~ |
||delMeetingAttrs|删除房间属性|
||clearMeetingAttrs|清空所有房间属性|
||getMeetingAllAttrsSuccess|获取所有房间属性成功|
||getMeetingAllAttrsFail|获取所有房间属性失败|
||getMeetingAttrsSuccess|获取部份房间属性成功|
||getMeetingAttrsFail|获取部份房间属性失败|
|回调|setMeetingAttrsRslt|重置所有房间属性结果|
||addOrUpdateMeetingAttrsRslt|添加或更新房间属性结果|
||delMeetingAttrsRslt|删除房间属性结果|
||clearMeetingAttrsRslt|清空所有房间属性结果|
||notifyMeetingAttrsChanged|通知房间属性改变|

### 用户属性 

|方式|接口|描述|
|---|---|---|
||getUserAttrs|获取指定用户的所有属性|
||setUserAttrs|重置指定用户的属性|
|主调|addOrUpdateUserAttrs|添加或更新指定用户的属性|
||delUserAttrs|删除指定用户的属性|
||clearUserAttrs|清空指定用户的属性|
||clearAllUserAttrs|清空所有用户的属性|
||getUserAttrsSuccess|获取指定用户的所有属性成功|
||getUserAttrsFail|获取指定用户的所有属性失败|
||setUserAttrsRslt|重置指定用户的属性结果|
|回调|addOrUpdateUserAttrsRslt|添加或更新指定用户的属性结果|
||delUserAttrsRslt|删除指定用户的属性结果|
||clearUserAttrsRslt|清空指定用户的属性结果|
||clearAllUserAttrsRslt|清空所有用户的属性结果|
||notifyUserAttrsChanged|通知用户属性改变|

### 音频管理 

|方式|接口|描述|
|---|---|---|
||getAudioMics|获取系统麦克风设备列表|
||getAudioSpks|获取系统扬声器设备列表|
||getAudioCfg|获取当前音频配置|
||tA di Cfg|设置音频参数|

|方式|~~setAudioCfg~~ ~~接口~~|~~设置音频参数~~ ~~描述~~|
|---|---|---|
||~~getMicVolume~~|~~获取麦克风音量~~|
||setMicVolume|配置麦克风音量|
||getSpkVolume|获取扬声器音量|
||setSpkVolume|配置扬声器音量|
||getSpeakerMute|获取扬声器静音状态|
||setSpeakerMute|配置扬声器静音|
||startEchoTest|开始本地语音环回测试|
|主调|stopEchoTest|停止本地语音环回测试|
||isEchoTesting|检查是否在本地语音环回测试|
||openMic|打开麦克风|
||closeMic|关闭麦克风|
||closeAllMic|全体关麦|
||getMicStatus|获取指定人员的麦克风状态|
||getLocMicDevEnergy|获取本地麦克风设备能量等级|
||getUserMicEnergy|获取房间中指定人员麦克风能量等级|
||getVoiceChangeType|获取目标用户变声类型|
||setVoiceChange|设置目标用户变声|
||setAudioSubscribeMode|设置语音订阅模式|
||setAudioSubscribeListForSeparateMode|设置独立音频订阅名单|
||notifyAudioDevChanged|通知本地音频设备变化|
||notifyAudioErr|通知本地音频相关错误|
|回调|notifyMicStatusChanged|通知房间中有人麦克风状态变化|
||notifyMicEnergy|通知房间有人麦克风能量变化|
||notifySetVoiceChange|通知房间中有人变声状态变化|
||notifyCloseAllMic|通知有人发起了全体关麦操作|

### 视频管理 

|方式|接口|描述|
|---|---|---|
||addCanvas|订阅绘制视图画面|
||rmCanvas|取消订阅绘制视图画面|
||getAllVideoInfo|获取指定成员的所有摄像头信息|
||getVideoCfg|获取本地视频全局配置|
||setVideoCfg|设置本地视频全局配置|
||openVideo|打开指定人的摄像头|
||closeVideo|关闭指定人的摄像头|

|~~主调~~ 方式|getVideoStatus 接口|获取房间中指定成员的视频状态 描述|
|---|---|---|
||setDefaultVideo|配置默认摄像头|
||getDefaultVideo|获取默认摄像头|
||setMutiVideos|配置本地多摄像头|
||getMutiVideos|获取本地的或他人的多摄像头列表|
||setLocVideoAttributes|设置本地指定设备私有配置|
||getLocVideoAttributes|获取本地指定设备私有配置|
||setVideoEffects|配置视频效果参数|
||getVideoEffects|获取视频效果参数|
||notifyVideoDevChanged|通知房间中用户视频设备变化|
|回调|notifyDefaultVideoChanged|通知用户默认视频设备变化|
||openVideoDevRslt|本地视频设备打开结果|
||notifyVideoStatusChanged|通知用户视频状态变化|

### 视频自定义采集 

|方式|接口|描述|
|---|---|---|
||createCustomVideoDev|创建自定义摄像头|
|主调|destroyCustomVideoDev|销毁自定义摄像头|
||inputCustomVideoDat|送入自定义摄像头数据|

### 虚拟视频设备 

|方式||接口||描述|
|---|---|---|---|---|
|主调|addIPCam||添加网络摄像头||
||delIPCam||删除网络摄像头||

### 影音共享 

|方式|接口|描述|
|---|---|---|
||setMediaCfg|设置影音共享配置|
||getMediaCfg|获取影音共享配置|
||startPlayMedia|开始影音共享|
||pausePlayMedia|暂停影音共享|
|主调|stopPlayMedia|停止影音共享|
||setMediaPlayPos|设置播放位置|
||getMediaInfo|获取当前影音共享信息|
||getMediaStreamInfo|获取当前影音共享流信息|
||setMediaVolume|配置影音播放音量|

|方式|getMediaVolume 接口|获取影音播放音量 描述|
|---|---|---|
||startPlayMediaFail|影音共享开启失败|
||notifyMediaStart|通知影音共享开启|
|回调|notifyMediaOpened|本地影音共享文件打开成功通知|
||notifyMediaStop|通知影音共享停止|
||notifyMediaPause|通知影音共享暂停|

### 屏幕共享 

|方式|接口||描述|
|---|---|---|---|
|回调|notifyScreenShareStarted|通知屏幕共享开始||
||notifyScreenShareStopped|通知屏幕共享停止||

### 本地录制/本地直播 

|方式|接口|描述|
|---|---|---|
||createLocMixer|创建本地混图器|
||updateLocMixerContent|更新本地混图器内容|
||destroyLocMixer|销毁本地混图器|
|主调|getLocMixerState|获取本地混图器状态|
||addLocMixerOutput|开启本地录制、开启直播推流|
||rmLocMixerOutput|停止本地录制、直播推流|
||setPicResource|配置图片资源(设置空的帧代表移除)|
|回调|notifyLocMixerStateChanged|本地混图器状态变化通知|
||notifyLocMixerOutputInfo|本地录制文件、本地直播信息通知|

### 云端录制/互动直播 

|方式|接口|描述|
|---|---|---|
||createCloudMixer|创建云端混图器|
||updateCloudMixerContent|更新云端混图器|
|主调|destroyCloudMixer|销毁云端混图器|
||getCloudMixerInfo|获取云端混图器信息|
||getAllCloudMixerInfo|获取所有云端混图器|
||createCloudMixerFailed|通知创建云端录制/推流失败|
|回调|notifyCloudMixerInfoChanged|通知云端录制/推流信息变化|
||notifyCloudMixerStateChanged|通知云端录制/推流状态变化|
||notifyCloudMixerOutputInfoChanged|通知云端录制/推流输出信息变化|

接口详情 

接口详情 

### create 

功能: 获取实例 

返回值: SDK实例 

##### CRVideoSDKEx.create(sdkDatSavePath, jsonParam) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|sdkDatSavePath|string|SDK工作目录,用于存储配置文件、临时文件、日志等文件;|
|jsonParam|string|扩展参数,JSON格式,参见CRSDKCreateParams|

补充说明: 

参见示例代码 

### getVersion 

功能: 获取SDK版本号 

返回值: SDK版本号(String) 

sdk_engine.getVersion() 

js 

### on 

- 功能: 注册SDK回调函数 

返回值: 无 

sdk_engine.on(event, fn) 

js 

|参数|类型|说明|
|---|---|---|
|event|string|事件名称,例如:loginRslt|
|fn|function|回调函数,参数见各回调函数说明|

补充说明: 

示例参见初始化SDK 

### off 

功能: 销毁SDK回调函数 

返回值: 无 

sdk_engine.off(event, fn) 

js 

|参数|类型|说明|
|---|---|---|
|event|string|事件名称,例如:loginRslt|
|fn|function|注销时必须传入函数的引用地址|

参数 补充说明: 

类型 

说明 

示例参见初始化SDK 

### destroy 

功能: 销毁SDK实例 

返回值: 无 

sdk_engine.destroy() 

js 

### setNetworkProxy 

功能: 设置网络代理 

返回值: 无 

##### sdk_engine.setNetworkProxy(proxy) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|proxy|string|网络代理,json格式,参见CRNetworkProxy|

### login 

功能: 登录 返回值: 无 

##### sdk_engine.login(CRLoginDat, cookie) 

js 

|参数|类型|说明|
|---|---|---|
|CRLoginDat|object|登录配置|
|cookie|string|详细介绍见cookie|

补充说明: 

登录结果参见loginRslt 

### logout 

功能: 注销登录 

返回值: 无 

##### sdk_engine.logout() 

js 

补充说明: 

退出程序时,必须注销本次登录,然后再进行SDK反初始化操作 

### updateToken 

功能: 更新token 

返回值: 无 

返回值: 无 

js 

sdk_engine.updateToken(token) 

|参数|类型|说明|
|---|---|---|
|token|string|Token鉴权码,详细介绍见关键词|

#### 补充说明: 

更新Token, 防止token因过期而掉线。 Token即将到期前30秒左右,将收到通知:notifyTokenWillExpire Token过期后,将引发掉线notifyLineOff,码值为18 

### getUserAuthErrCode 

- 功能: 第三方鉴权错误码获取 

- 返回值: 错误码,值含义第三方鉴权方提供 

sdk_engine.getUserAuthErrCode() 

js 

### getUserAuthErrDesc 

- 功能: 第三方鉴权错误原因获取 

- 返回值: string,值由第三方鉴权方自由定义。 

sdk_engine.getUserAuthErrDesc() 

js 

### setDNDStatus 

- 功能: 开关免打扰 

- 返回值: 无 

##### sdk_engine.setDNDStatus(DNDStatus, cookie) 

js 

|参数|类型|说明|
|---|---|---|
|DNDStatus|number|0代表关闭免打扰, 其它值代表开启免打扰,含义自由定义|
|cookie|string|详细介绍见cookie|

补充说明: 

#### 设置结果请参见setDNDStatusRslt; 

开启免打扰后,他人呼叫本人时,系统自动回绝呼叫,错误码原因为602; 

- 开启免打扰后,系统将不再自动为座席分配客户notifyAutoAssignUser,座席可以调用reqAssignUser来手动分配客户 (叫号模式); 

### getUserStatus 

- 功能: 获取本AppID下的所有登录用户的状态信息 返回值: 无 

js 

sdk_engine.getUserStatus(cookie) 

|参数|类型|说明|
|---|---|---|
|cookie|string|详细介绍见cookie|

补充说明: 

结果请参见getUserStatusSuccess / getUserStatusFail 只返回在线用户状态信息,获取不到的代表未登录 

### getOneUserStatus 

功能: 获取本AppID下指定用户的在线状态 返回值: 无 

##### sdk_engine.getOneUserStatus(userID, cookie) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|userID|string|用户ID, 详细介绍见关键词|
|cookie|string|详细介绍见cookie|

补充说明: 

结果请参见getUserStatusSuccess / getUserStatusFail 

### startUserStatusNotify 

- 功能: 开启AppID下的用户登录状态消息推送 返回值: 无 

##### sdk_engine.startUserStatusNotify(cookie) 

js 

|参数|类型|说明|
|---|---|---|
|cookie|string|详细介绍见cookie|

补充说明: 

开启后他人状态变化将收到notifyUserStatus通知 开启结果请参见startUserStatusNotifyRslt 如果在线用户量很大时,将带来很大的开销请谨慎开启 

### stopUserStatusNotify 

- 功能: 关闭appID下的用户在线状态消息推送 返回值: 无 

##### sdk_engine.stopUserStatusNotify(cookie) 

js 

|参数|类型|说明|
|---|---|---|
|cookie|string|详细介绍见cookie|

补充说明: 

补充说明: 

结果请参见stopUserStatusNotifyRslt 

### loginRslt 

功能: 登录结果回调 

|sdk_engine.on("lo|ginRslt", (sdkErr,cookie) => {})|js|
|---|---|---|
|参数|类型|说明|
|sdkErr|CRVSDK_ERR_DEF|错误码|
|cookie|string|详细介绍见cookie|

### notifyTokenWillExpire 

功能: Token即将失效的通知,失效前30秒通知 

##### sdk_engine.on("notifyTokenWillExpire", () => {}) 

js 

补充说明: 

采用Token模式登录,才会收到此回调; 

Token到期前30秒左右回调,应尽快调用updateToken将授权更久的Token设置给SDK; 

### notifyLineOff 

功能: 通知本端SDK掉线 

|sdk_engine.on("notifyLineOff", (sdkErr) => {})|js|
|---|---|
|参数 类型|说明|
|sdkErr CRVSDK_ERR_DEF|错误码|

#### 补充说明: 

#### 掉线的原因参见错误码; 

掉线时,如果正在房间中也将自动离开房间; 掉线时,之前的所有未完成的请求都将失败; 掉线之后,可以按业务需求稍后重新登录; 

### setDNDStatusRslt 

#### 功能: 设置免打扰结果 

##### sdk_engine.on("setDNDStatusRslt", (sdkErr, cookie) => {}) 

js 

|参数|类型|说明|
|---|---|---|
|sdkErr|CRVSDK_ERR_DEF|错误码|
|cookie|string|详细介绍见cookie|

getUserStatusSuccess 

#### 功能: 获取用户登录状态信息成功 

|sdk_engine.on("getUserStatusSuccess", (ustArray,cookie) => {})|
|---|

|js|
|---|

|参数|类型|说明|
|---|---|---|
|ustArray|Array<CRUserStatus>|用户登录状态信息的数组形式|
|cookie|string|详细介绍见cookie|

### getUserStatusFail 

功能: 获取用户登录状态信息失败 

sdk_engine.on("getUserStatusFail", (sdkErr, cookie) => {}) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|sdkErr|CRVSDK_ERR_DEF|错误码|
|cookie|string|详细介绍见cookie|

### notifyUserStatus 

功能: 通知某用户登录状态变化 

##### sdk_engine.on("notifyUserStatus", (userStatus) => {}) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|userStatus|CRUserStatus|用户登录状态信息|

补充说明: 

只在startUserStatusNotify后,才会收到变化通知; 

### startUserStatusNotifyRslt 

功能: 开启用户状态通知结果 

##### sdk_engine.on("startUserStatusNotifyRslt", (sdkErr, cookie) => {}) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|sdkErr|CRVSDK_ERR_DEF|错误码|
|cookie|string|详细介绍见cookie|

### stopUserStatusNotifyRslt 

功能: 关闭用户状态通知结果 

js 

sdk_engine.on("stopUserStatusNotifyRslt", (sdkErr, cookie) => {}) 

|参数|类型|说明|
|---|---|---|
|sdkErr|CRVSDK_ERR_DEF|错误码|
|cookie|string|详细介绍见cookie|

### sendCmd 

功能: 发送点对点消息 返回值: 任务ID(String) 

##### sdk_engine.sendCmd(targetUserId, data, cookie) 

js 

|参数|类型|说明|
|---|---|---|
|targetUserId|string|目标用户ID, 参见CRLoginDat的userID字段|
|data|string|发送的数据(最大64KB)|
|cookie|string|详细介绍见cookie|

补充说明: 

发送结果请参见sendCmdRslt 目标用户将收到通知notifyCmdData 房间内群发消息参见sendMeetingCustomMsg 

### sendBuffer 

功能: 发送点对点大数据 返回值: 任务ID(String) 

##### sdk_engine.sendBuffer(targetUserId, data, cookie) 

js 

|参数|类型|说明|
|---|---|---|
|targetUserId|string|目标用户ID, 参见CRLoginDat的userID字段|
|data|Uint8Array|发送的数据(最大100MB)|
|cookie|string|详细介绍见cookie|

补充说明: 

数据将被分块发送,发送进度参见notifySendProgress 取消发送参见cancelSend 结果请参见sendBufferRslt 目标用户将收到通知notifyBufferData 

### sendFile 

功能: 发送文件 

返回值: 任务ID(String) 

js 

sdk_engine.sendFile(targetUserId, fileName, cookie) 

|参数|类型|说明|
|---|---|---|
|targetUserId|string|目标用户ID, 参见CRLoginDat的userID字段|
|fileName|string|本地完整路径的文件名(文件内容最大100MB)|
|cookie|string|详细介绍见cookie|

#### 补充说明: 

数据将被分块发送,发送进度参见notifySendProgress 取消发送参见cancelSend 结果请参见sendFileRslt 目标用户将收到通知notifyFileData 

### cancelSend 

功能: 取消大数据、文件的发送 

返回值: 无 

##### sdk_engine.cancelSend(taskId, cookie) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|taskId|string|任务ID,sendBuffer、sendFile的返回值|
|cookie|string|详细介绍见cookie|

### sendCmdRslt 

#### 功能: 发送点对点消息结果 

sdk_engine.on("sendCmdRslt", (taskId, sdkErr, cookie) => {}) 

js 

|参数|类型|说明|
|---|---|---|
|taskId|string|任务ID,sendCmd的返回值|
|sdkErr|CRVSDK_ERR_DEF|错误码|
|cookie|string|详细介绍见cookie|

### sendBufferRslt 

#### 功能: 发送点对点大数据结果 

sdk_engine.on("sendBufferRslt", (taskId, sdkErr, cookie) => {}) 

js 

|参数|类型|说明|
|---|---|---|
|taskId|string|任务ID,sendBuffer的返回值|
|sdkErr|CRVSDK_ERR_DEF|错误码|
|cookie|string|详细介绍见cookie|

sendFileRslt 

#### 功能: 发送点对点文件结果 

|sdk_engine.on("sendFileRslt", (taskId,fileName,sdkErr,cookie) => {})|
|---|

|js|
|---|

|参数|类型|说明|
|---|---|---|
|taskId|string|任务ID,sendFile的返回值|
|fileName|string|本地完整路径的文件名(文件内容最大100MB)|
|sdkErr|CRVSDK_ERR_DEF|错误码|
|cookie|string|详细介绍见cookie|

### cancelSendRslt 

#### 功能: 取消发送结果 

sdk_engine.on("cancelSendRslt", (taskId, sdkErr, cookie) => {}) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|taskId|string|任务ID,sendBuffer、sendFile的返回值|
|sdkErr|CRVSDK_ERR_DEF|错误码|
|cookie|string|详细介绍见cookie|

### notifySendProgress 

#### 功能: 通知大数据、文件的发送进度 

|sdk_engine.on("notifySendProgress", (taskId,sendedLen,totalLen,cookie) => {})|
|---|

|js|
|---|

|参数|类型|说明|
|---|---|---|
|taskId|string|任务ID,sendBuffer、sendFile的返回值|
|sendedLen|number|已发送大小|
|totalLen|number|总大小|
|cookie|string|详细介绍见cookie|

### notifyCmdData 

功能: 通知收到点对点透明通道消息 

sdk_engine.on("notifyCmdData", (sourceUserId, data) => {}) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|sourceUserId|string|发送者UserID, 参见CRLoginDat的userID字段|
|data|string|消息内容|

### notifyBufferData 

#### 功能: 通知收到点对点大数据 

sdk_engine.on("notifyBufferData", (sourceUserId, data) => {}) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|sourceUserId|string|发送者UserID, 参见CRLoginDat的userID字段|
|data|string|消息内容|

### notifyFileData 

#### 功能: 通知收到点对点文件 

sdk_engine.on("notifyFileData", (sourceUserId, tmpFile, orgFileName) => {}) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|sourceUserId|string|发送者UserID, 参见CRLoginDat的userID字段|
|tmpFile|string|本地完整路径文件名(接收到的文件存放在系统Tmp目录下)|
|orgFileName|string|原始文件名(不包含路径)|

### initQueueDat 

- 功能: 初始化队列功能 返回值: 无 

sdk_engine.initQueueDat(cookie) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|cookie|string|详细介绍见cookie|

补充说明: 

初始化队列结果请参见initQueueDatRslt; 队列初始化成功后才可进行其它队列操作; 

### getAllQueueInfo 

- 功能: 获取AppID下的所有队列基础信息 

返回值: Array<CRQueInfo>,队列基础信息数组 

sdk_engine.getAllQueueInfo() 

|js|
|---|

### getQueueStatus 

- 功能: 获取指定队列的排队状况 

- 返回值: CRQueStatus,队列状态 

js 

sdk_engine.getQueueStatus(queID) 

g g (q ) 

_ 

|参数|类型|说明|
|---|---|---|
|queID|number|队列ID|

### getQueuingInfo 

- 功能: 获取我的排队信息 

- 返回值: CRQueuingInfo,我的排队信息 

sdk_engine.getQueuingInfo() 

js 

### getServingQueues 

- 功能: 获取我服务的所有队列 

返回值: Array<Number>, 队列Id列表 

sdk_engine.getServingQueues() 

js 

### startQueuing 

- 功能: 客户开始排队 

- 返回值: 无 

##### sdk_engine.startQueuing(queID, usrExtDat, cookie) 

js 

|参数|类型|说明|
|---|---|---|
|queID|number|队列ID|
|usrExtDat|string|自定义扩展参数,对端将收到此参数|
|cookie|string|详细介绍见cookie|

补充说明: 

客户同一时间,只能排一个队列; 排队结果请参见startQueuingRslt; 

### stopQueuing 

- 功能: 客户停止排队 

- 返回值: 无 

##### sdk_engine.stopQueuing(cookie) 

js 

|参数|类型|说明|
|---|---|---|
|cookie|string|详细介绍见cookie|

补充说明: 

排队结果请参见stopQueuingRslt; 

### startService 

- 功能: 座席开始服务某队列 

- 返回值: 无 

sdk_engine.startService(queID, priority, cookie) 

js

|参数|类型|说明|
|---|---|---|
|queID|number|队列ID|
|priority|number|坐席优先级 (缺省为0,取值为0~1000内整数。值越小优先级越高。0为最高优先级)|
|cookie|string|详细介绍见cookie|

补充说明: 

可以多次调用,开启对多个队列的服务; 开启服务结果请参见startServiceRslt ; 开启成功后: 

- a. 如果没有开启免打扰setDNDStatus,那么系统会自动分配客户:notifyAutoAssignUser; 

- b. 如果开启免打挽,系统就不会分配客户,如需服务客户可调用:reqAssignUser; 座席优先级描述: 

- a. 客户优先分配给服务此队列优先级最高的,且空闲的座席; 

- b. 优先级相同时,则分配给最先空闲的座席; 

- c. 优先级高的座席变空闲时,不抢夺已分配的客户; 

### stopService 

- 功能: 座席停止服务某队列 

返回值: 无 

##### sdk_engine.stopService(queID, cookie) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|queID|number|队列ID|
|cookie|string|详细介绍见cookie|

补充说明: 

停止服务结果请参见stopServiceRslt; 

### reqAssignUser 

- 功能: 座席手动分配下一位客户(开启免打扰后使用) 

返回值: 无 

##### sdk_engine.reqAssignUser(cookie) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|cookie|string|详细介绍见cookie|

补充说明: 

补充说明 

开启免打扰后手动分配客户接口;(当关闭免打扰时,系统将自动分配客户,无需调用此接口) 分配结果请参见reqAssignUserRslt ; 

### reqAssignUser2 

- 功能: 座席手动分配指定客户(开启免打扰后使用) 返回值: 无 

##### sdk_engine.reqAssignUser2(queID, userID, cookie) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|queID|number|队列ID|
|userID|string|请求分配指定用户|
|cookie|string|详细介绍见cookie|

补充说明: 

开启免打扰后手动分配客户接口;(当关闭免打扰时,系统将自动分配客户) 可以要求分配指定队列、指定客户,满足客户分配给历史座席类的需求; 分配结果请参见reqAssignUserRslt ; 

### acceptAssignUser 

功能: 接受系统分配的客户 返回值: 无 

sdk_engine.acceptAssignUser(queID, userID, cookie) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|queID|number|队列ID|
|userID|string|用户ID, 详细介绍见关键词|
|cookie|string|详细介绍见cookie|

补充说明: 

结果请参见acceptAssignUserRslt 

### rejectAssignUser 

功能: 拒绝系统分配的客户 

返回值: 无 

##### sdk_engine.rejectAssignUser(queID, userID, cookie) 

js 

|参数|类型|说明|
|---|---|---|
|queID|number|队列ID|
|userID|string|用户ID, 详细介绍见关键词|
|cookie|string|详细介绍见cookie|

~~cookie string 详细介绍见cookie 参数 类型 说明~~ 

补充说明: 

结果请参见rejectAssignUserRslt 

### initQueueDatRslt 

功能: 初始化队列功能结果 

sdk_engine.on("initQueueDatRslt", (sdkErr, cookie) => {}) 

js

|参数|类型|说明|
|---|---|---|
|sdkErr|CRVSDK_ERR_DEF|错误码|
|cookie|string|详细介绍见cookie|

### notifyQueueStatusChanged 

功能: 队列排队状态更新 

sdk_engine.on("notifyQueueStatusChanged", (queStatus) => {}) 

js

|参数|类型|说明|
|---|---|---|
|queStatus|CRQueStatus|队列排队状态信息|

### notifyQueuingInfoChanged 

功能: 我的排队信息更新 

|sdk_engine.on("notifyQueuingInfoChanged", (queuingInfo) => {})|js|
|---|---|
|参数 类型|说明|
|queuingInfo CRQueuingInfo|我的排队信息|

### startQueuingRslt 

功能: 客户开始排队结果 

##### sdk_engine.on("startQueuingRslt", (sdkErr, cookie) => {}) 

js 

|参数|类型|说明|
|---|---|---|
|sdkErr|CRVSDK_ERR_DEF|错误码|
|cookie|string|详细介绍见cookie|

### stopQueuingRslt 

功能: 客户停止排队结果 

js 

sdk_engine.on("stopQueuingRslt", (sdkErr, cookie) => {}) 

|参数|类型|说明|
|---|---|---|
|sdkErr|CRVSDK_ERR_DEF|错误码|
|cookie|string|详细介绍见cookie|

### startServiceRslt 

#### 功能: 座席开始服务结果 

sdk_engine.on("startServiceRslt", (queID, sdkErr, cookie) => {}) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|queID|number|队列ID|
|sdkErr|CRVSDK_ERR_DEF|错误码|
|cookie|string|详细介绍见cookie|

### stopServiceRslt 

功能: 座席开始服务结果 

sdk_engine.on("stopServiceRslt", (queID, sdkErr, cookie) => {}) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|queID|number|队列ID|
|sdkErr|CRVSDK_ERR_DEF|错误码|
|cookie|string|详细介绍见cookie|

### acceptAssignUserRslt 

#### 功能: 接受系统分配的客户结果 

sdk_engine.on("acceptAssignUserRslt", (sdkErr, cookie) => {}) 

js 

|参数|类型|说明|
|---|---|---|
|sdkErr|CRVSDK_ERR_DEF|错误码|
|cookie|string|详细介绍见cookie|

### rejectAssignUserRslt 

#### 功能: 拒绝系统分配的客户结果 

sdk_engine.on("rejectAssignUserRslt", (sdkErr, cookie) => {}) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|sdkErr|CRVSDK ERR DEF|错误码|

错误码 ~~说明~~ 详细介绍见cookie 

_ _ 

~~参数 类型~~ cookie string 

### reqAssignUserRslt 

功能: 座席手动分配客户结果 

sdk_engine.on("reqAssignUserRslt", (sdkErr, queUserInfo, cookie) => {}) 

js

|参数|类型|说明|
|---|---|---|
|sdkErr|CRVSDK_ERR_DEF|错误码|
|queUserInfo|CRQueUserInfo|队列用户信息|
|cookie|string|详细介绍见cookie|

### notifyAutoAssignUser 

功能: 座席自动分配客户结果 

|sdk_engine.on("notifyAutoAssignUser", (queUserInfo) => {})|js|
|---|---|
|参数 类型|说明|
|queUserInfo CRQueUserInfo|队列用户信息|

#### 补充说明: 

如果不需要系统的自动分配,请通setDNDStatus开启免打扰功能; acceptAssignUser后,还需要调用call去呼叫对方进入目标房间; 收到系统分配的客户后,如果座席不acceptAssignUser也不rejectAssignUser,系统将在30秒后取消本次分 配notifyAssignUserCanceled,然后将客户放回到队首; 

### notifyAssignUserCanceled 

#### 功能: 通知分配的客户取消了 

|sdk_engine.on("notifyAssignUserCanceled", (queID,userID) => {}) js|
|---|

|参数|类型|说明|
|---|---|---|
|queID|number|队列ID|
|userID|string|用户ID, 详细介绍见关键词|

#### 补充说明: 

被取消的原因,可能是用户取消排队了,或者用户掉线了,或者收到notifyAutoAssignUser后没有及 时acceptAssignUser / rejectAssignUser 

### notifyUserEnterQueue 

#### 功能: 通知客户进入了某队列 

js 

sdk_engine.on("notifyUserEnterQueue", (queID, queUserInfo) => {}) 

|参数|类型|说明|
|---|---|---|
|queID|number|队列ID|
|queUserInfo|CRQueUserInfo|队列用户信息|

补充说明: 

只有座席服务的队列,才会收到此通知。 

### notifyUserLeaveQueue 

功能: 通知客户离开了某队列 

##### sdk_engine.on("notifyUserLeaveQueue", (queID, queUserInfo, reason) => {}) 

js 

|参数|类型|说明|
|---|---|---|
|queID|number|队列ID|
|queUserInfo|CRQueUserInfo|队列用户信息|
|reason|CRVSDK_LEFT_QUEUE_REASON|原因值|

补充说明: 

只有座席服务的队列,才会收到此通知。 

### call 

功能: 发起呼叫 

返回值: 呼叫ID(String) 

##### sdk_engine.call(calledUserID, meetID, usrExtDat, cookie) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|calledUserID|string|被叫用户ID|
|meetID|number|房间号|
|usrExtDat|string|自定义扩展参数,对端将收到此参数|
|cookie|string|详细介绍见cookie|

#### 补充说明: 

发起的呼叫结果参见callRslt; 

呼叫时,对方迟迟不acceptCall / rejectCall,30秒后将超时而自动结束呼叫; 

### acceptCall 

功能: 接受他人的呼叫 返回值: 无 

js 

sdk_engine.acceptCall(callID, meetID, usrExtDat, cookie) 

|参数|类型|说明|
|---|---|---|
|callID|string|呼叫ID, 参见call/callMoreParty/notifyCallIn接口|
|meetID|number|房间号|
|usrExtDat|string|自定义扩展参数,对端将收到此参数|
|cookie|string|详细介绍见cookie|

补充说明: 

接受结果参见acceptCallRslt; 

### rejectCall 

功能: 拒接他人的呼叫 返回值: 无 

##### sdk_engine.rejectCall(callID, usrExtDat, cookie) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|callID|string|呼叫ID, 参见call/callMoreParty/notifyCallIn接口|
|usrExtDat|string|自定义扩展参数,对端将收到此参数|
|cookie|string|详细介绍见cookie|

补充说明: 

拒绝结果参见rejectCallRslt; 

### hungupCall 

功能: 挂断通话 返回值: 无 

##### sdk_engine.hungupCall(callID, usrExtDat, cookie) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|callID|string|呼叫ID, 参见call/callMoreParty/notifyCallIn接口|
|usrExtDat|string|自定义扩展参数,对端将收到此参数|
|cookie|string|详细介绍见cookie|

补充说明: 

挂断结果参见hangupCallRslt; 

### callMoreParty 

功能: 发起多方呼叫(或呼转) 

返回值: 呼叫ID(String) 

js 

sdk_engine.callMoreParty(calledUserID, meetID, usrExtDat, cookie) 

|参数|类型|说明|
|---|---|---|
|calledUserID|string|被叫用户ID|
|meetID|number|房间号|
|usrExtDat|string|自定义扩展参数,对端将收到此参数|
|cookie|string|详细介绍见cookie|

#### 补充说明: 

呼叫结果参见callMorePartyRslt; 

呼叫进度参见notifyCallMorePartyStatus; 

呼转实现思路: A、B通话已建立(假设callID为IdAB),B想由C来服务A,B callMoreParty C(假设callID为IdBC), 在 C接受进入通话后,A便可挂断IdAB通话并离开房间。 

### cancelCallMoreParty 

功能: 取消多方呼叫 

返回值: 无 

sdk_engine.cancelCallMoreParty(callID, usrExtDat, cookie) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|callID|string|呼叫ID, 参见call/callMoreParty/notifyCallIn接口|
|usrExtDat|string|自定义扩展参数,对端将收到此参数|
|cookie|string|详细介绍见cookie|

补充说明: 

取消结果参见cancelCallMorePartyRslt; 

### callRslt 

#### 功能: 发起的呼叫结果 

sdk_engine.on("callRslt", (callID, sdkErr, cookie) => {}) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|callID|string|呼叫ID, 参见call/callMoreParty/notifyCallIn接口|
|sdkErr|CRVSDK_ERR_DEF|错误码|
|cookie|string|详细介绍见cookie|

### acceptCallRslt 

#### 功能: 接受他人呼叫的结果 

sdk_engine.on("acceptCallRslt", (callID, sdkErr, cookie) => {}) 

js 

参数 

类型 

说明 

|~~参数~~|~~类型~~|~~说明~~|
|---|---|---|
|~~callID~~ ~~参数~~|~~string~~ ~~类型~~|~~呼叫ID, 参见call /callMoreParty /notifyCallIn接口~~ ~~说明~~|
|sdkErr|CRVSDK_ERR_DEF|错误码|
|cookie|string|详细介绍见cookie|

### rejectCallRslt 

功能: 拒绝他人呼叫的结果 

sdk_engine.on("rejectCallRslt", (callID, sdkErr, cookie) => {}) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|callID|string|呼叫ID, 参见call/callMoreParty/notifyCallIn接口|
|sdkErr|CRVSDK_ERR_DEF|错误码|
|cookie|string|详细介绍见cookie|

### hangupCallRslt 

功能: 挂断通话结果 

sdk_engine.on("hangupCallRslt", (callID, sdkErr, cookie) => {}) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|callID|string|呼叫ID, 参见call/callMoreParty/notifyCallIn接口|
|sdkErr|CRVSDK_ERR_DEF|错误码|
|cookie|string|详细介绍见cookie|

### notifyCallIn 

功能: 通知呼入 

sdk_engine.on("notifyCallIn", (callID, meetID, callerID, usrExtDat) => {}) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|callID|string|呼叫ID, 参见call/callMoreParty/notifyCallIn接口|
|meetID|number|房间号|
|callerID|string|主叫用户ID|
|usrExtDat|string|自定义扩展参数,对端将收到此参数|

### notifyCallAccepted 

功能: 通知呼叫被接受 

js 

sdk_engine.on("notifyCallAccepted", (callID, meetID, usrExtDat) => {}) 

|参数 参数|类型 类型|说明 说明|
|---|---|---|
|callID|string|呼叫ID, 参见call/callMoreParty/notifyCallIn接口|
|meetID|number|房间号|
|usrExtDat|string|自定义扩展参数,对端将收到此参数|

### notifyCallRejected 

#### 功能: 通知呼叫被拒接 

sdk_engine.on("notifyCallRejected", (callID, sdkErr, usrExtDat) => {}) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|callID|string|呼叫ID, 参见call/callMoreParty/notifyCallIn接口|
|sdkErr|CRVSDK_ERR_DEF|错误码|
|usrExtDat|string|自定义扩展参数,对端将收到此参数|

### notifyCallHungup 

#### 功能: 通知呼叫被挂断 

sdk_engine.on("notifyCallHungup", (callID, usrExtDat) => {}) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|callID|string|呼叫ID, 参见call/callMoreParty/notifyCallIn接口|
|usrExtDat|string|自定义扩展参数,对端将收到此参数|

### callMorePartyRslt 

#### 功能: 发起多方呼叫结果 

sdk_engine.on("callMorePartyRslt", (callID, sdkErr, cookie) => {}) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|callID|string|呼叫ID, 参见call/callMoreParty/notifyCallIn接口|
|sdkErr|CRVSDK_ERR_DEF|错误码|
|cookie|string|详细介绍见cookie|

### cancelCallMorePartyRslt 

#### 功能: 取消多方呼叫结果 

sdk_engine.on("cancelCallMorePartyRslt", (callID, sdkErr, cookie) => {}) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|callID|string|呼叫ID, 参见call/callMoreParty/notifyCallIn接口|

g 呼叫 , 参见 / y / y 接口 ~~参数 类型 说明~~ sdkErr CRVSDK_ERR_DEF 错误码 cookie string 详细介绍见cookie 

### notifyCallMorePartyStatus 

功能: 通知多方呼叫状态 

sdk_engine.on("notifyCallMorePartyStatus", (callID, status) => {}) 

js 

|参数|类型|说明|
|---|---|---|
|callID|string|呼叫ID, 参见call/callMoreParty/notifyCallIn接口|
|status|number|多方呼叫状态,参见CALLMORE_STATE|

### invite 

功能: 邀请他人 

返回值: 邀请ID(String) 

sdk_engine.invite(invitedUserID, usrExtDat, cookie) 

js 

|参数|类型|说明|
|---|---|---|
|invitedUserID|string|受邀者用户ID|
|usrExtDat|string|自定义扩展参数,对端将收到此参数|
|cookie|string|详细介绍见cookie|

补充说明: 

邀请结果参见inviteRslt; 如果邀请监控设备进入房间, usrExtDat必须为: {"meeting":{"ID":会议号}, "devInfo":{"userID":"会议中用户ID", "nickName":"会议中用户昵称"}}; 

### acceptInvite 

- 功能: 接受邀请 返回值: 无 

##### sdk_engine.acceptInvite(inviteID, usrExtDat, cookie) 

js 

|参数|类型|说明|
|---|---|---|
|inviteID|string|邀请ID|
|usrExtDat|string|自定义扩展参数,对端将收到此参数|
|cookie|string|详细介绍见cookie|

补充说明: 

接受结果参见acceptInviteRslt; 

rejectInvite 

#### 功能: 拒接邀请 

返回值: 无 

##### sdk_engine.rejectInvite(inviteID, usrExtDat, cookie) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|inviteID|string|邀请ID|
|usrExtDat|string|自定义扩展参数,对端将收到此参数|
|cookie|string|详细介绍见cookie|

补充说明: 

接受结果参见rejectInviteRslt; 

### cancelInvite 

功能: 取消邀请 

返回值: 无 

##### sdk_engine.cancelInvite(inviteID, usrExtDat, cookie) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|inviteID|string|邀请ID|
|usrExtDat|string|自定义扩展参数,对端将收到此参数|
|cookie|string|详细介绍见cookie|

补充说明: 

取消结果参见cancelInviteRslt; 

### inviteRslt 

功能: 邀请他人结果 

##### sdk_engine.on("inviteRslt", (inviteID, sdkErr, cookie) => {}) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|inviteID|string|邀请ID|
|sdkErr|CRVSDK_ERR_DEF|错误码|
|cookie|string|详细介绍见cookie|

### cancelInviteRslt 

功能: 取消邀请结果 

js 

sdk_engine.on("cancelInviteRslt", (inviteID, sdkErr, cookie) => {}) 

|参数|类型|说明|
|---|---|---|
|inviteID|string|邀请ID|
|sdkErr|CRVSDK_ERR_DEF|错误码|
|cookie|string|详细介绍见cookie|

### acceptInviteRslt 

功能: 接受邀请结果 

sdk_engine.on("acceptInviteRslt", (inviteID, sdkErr, cookie) => {}) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|inviteID|string|邀请ID|
|sdkErr|CRVSDK_ERR_DEF|错误码|
|cookie|string|详细介绍见cookie|

### rejectInviteRslt 

#### 功能: 拒接邀请结果 

sdk_engine.on("rejectInviteRslt", (inviteID, sdkErr, cookie) => {}) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|inviteID|string|邀请ID|
|sdkErr|CRVSDK_ERR_DEF|错误码|
|cookie|string|详细介绍见cookie|

### notifyInviteIn 

#### 功能: 通知收到邀请 

sdk_engine.on("notifyInviteIn", (inviteID, invitedUserID, usrExtDat) => {}) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|inviteID|string|邀请ID|
|invitedUserID|string|邀请人ID|
|usrExtDat|string|自定义扩展参数,对端将收到此参数|

### notifyInviteAccepted 

功能: 通知邀请被接受 

js 

sdk_engine.on("notifyInviteAccepted", (inviteID, usrExtDat) => {}) 

|**参数**|**类型**|**说明**|
|---|---|---|
|inviteID|string|邀请ID|
|usrExtDat|string|自定义扩展参数,对端将收到此参数|

### notifyInviteRejected 

#### 功能: 通知邀请被拒接 

sdk_engine.on("notifyInviteRejected", (inviteID, sdkErr, usrExtDat) => {}) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|inviteID|string|邀请ID|
|sdkErr|CRVSDK_ERR_DEF|错误码|
|usrExtDat|string|自定义扩展参数,对端将收到此参数|

### notifyInviteCanceled 

#### 功能: 通知邀请被取消 

|sdk_engine.on("notifyInviteCanceled", (inviteID,sdkErr,usrExtDat) => {})|
|---|

|js|
|---|

|参数|类型|说明|
|---|---|---|
|inviteID|string|邀请ID|
|sdkErr|CRVSDK_ERR_DEF|错误码|
|usrExtDat|string|自定义扩展参数,对端将收到此参数|

### createMeeting 

功能: 创建房间 

返回值: 无 

##### sdk_engine.createMeeting(undefined, cookie) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|undefined|undefined|保留参数,参入undefined即可,非必填|
|cookie|string|详细介绍见cookie|

#### 补充说明: 

创建结果参见createMeetingSuccess / createMeetingFail; 房间创建后,此房间ID将一直存在,直到调用destroyMeeting销毁它; 

没有人使用房间时,系统会在一定时间后释放资源,并在下次使用是再临时分配,房间ID是保持不变的; 

### destroyMeeting 

功能: 销毁房间 返回值: 无 

值 

sdk_engine.destroyMeeting(meetID, cookie) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|meetID|number|房间号|
|cookie|string|详细介绍见cookie|

补充说明: 

创建结果参见destroyMeetingRslt 房间被销毁后,房间中的其他人将收到notifyMeetingStopped 

### createMeetingSuccess 

功能: 通知创建房间成功 

sdk_engine.on("createMeetingSuccess", (meetID, cookie) => {}) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|meetID|number|房间号|
|cookie|string|详细介绍见cookie|

### createMeetingFail 

功能: 通知创建房间失败 

sdk_engine.on("createMeetingFail", (sdkErr, cookie) => {})

|js|
|---|

|参数|类型|说明|
|---|---|---|
|sdkErr|CRVSDK_ERR_DEF|错误码|
|cookie|string|详细介绍见cookie|

### destroyMeetingRslt 

功能: 销毁房间结果 

sdk_engine.on("destroyMeetingRslt", (sdkErr, cookie) => {}) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|sdkErr|CRVSDK_ERR_DEF|错误码|
|cookie|string|详细介绍见cookie|

### enterMeeting 

功能: 进入房间 返回值: 无 

js 

js 

sdk_engine.enterMeeting(meetID) 

|参数|类型|说明|
|---|---|---|
|meetID|number|房间号|

补充说明: 

进入房间结果:enterMeetingRslt 

进入房间成功时,房间中其他人员将收到通知:notifyUserEnterMeeting 

### exitMeeting 

功能: 离开房间 

返回值: 无 

sdk_engine.exitMeeting() 

js 

补充说明: 

离开房间不需要等待服务器响应(网络不好,或网络断开时不会影响离开房间),调用之后即代表离开房间了; 离开房间后,不会再收房间中任何消息; 

离开房间时,如果网络正常,房间中其他人会立即收到notifyUserLeftMeeting通知,如果网络不正常,服务器会在sdk 内部握手超时后发出notifyUserLeftMeeting通知; 

需要销毁房间,请参见destroyMeeting; 

### getNetState 

功能: 获取当前网络状态评分 

返回值: number,当前网络状态(0~10,10为最佳网络) 

sdk_engine.getNetState() 

js 

### getNetState2 

- 功能: 获取网络状态详细信息 

- 返回值: CRNetStateInfo 

sdk_engine.getNetState2() 

js 

### enterMeetingRslt 

功能: 进入房间结果 

##### sdk_engine.on("enterMeetingRslt", (sdkErr) => {}) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|sdkErr|CRVSDK_ERR_DEF|错误码|

### notifyMeetingStopped 

功能: 通知房间已结束 

js 

sdk_engine.on("notifyMeetingStopped", () => {}) 

### notifyMeetingDropped 

功能: 与房间断开 

sdk_engine.on("notifyMeetingDropped", (reason) => {}) 

js

|参数|类型|说明|
|---|---|---|
|reason|CRVSDK_MEETING_DROPPED_REASON|断开原因。|

### notifyNetStateChanged 

功能: 通知本端与房间服务器的网络状态变化 

sdk_engine.on("notifyNetStateChanged", (level) => {}) 

js 

|参数|类型|说明|
|---|---|---|
|level|number|网络评分0~10(10分为最佳网络)|

### isUserInMeeting 

- 功能: 检查用户是否在房间中 

返回值: true:在房间中, false:不在房间中 

sdk_engine.isUserInMeeting(userID) 

js 

|参数|类型|说明|
|---|---|---|
|userID|string|用户ID, 详细介绍见关键词|

### getAllMembers 

- 功能: 获取房间中所有成员信息 

返回值: 成员信息数组(Array<CRMeetingMember>) 

sdk_engine.getAllMembers() 

js 

### getMemberInfo 

- 功能: 获取房间中指定成员信息 

返回值: 成员信息(CRMeetingMember) 

##### sdk_engine.getMemberInfo(userID) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|userID|string|用户ID, 详细介绍见关键词|

### setNickName 

- 功能: 修改房间中成员昵称 

返回值: 无 

##### sdk_engine.setNickName(userID, nickName) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|userID|string|用户ID, 详细介绍见关键词|
|nickName|string|用户新的昵称|

补充说明: 

设置结果请参见setNickNameRslt 

调用此接口如果设置成功,其他房间内用户会收到notifyNickNameChanged通知 

### kickout 

- 功能: 将他人请出房间 

返回值: 无 

##### sdk_engine.kickout(userID) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|userID|string|用户ID, 详细介绍见关键词|

补充说明: 

#### 请出结果请参见kickoutRslt; 

被请出人将收到notifyMeetingDropped通知,原因值是:CRVSDK_DROPPED_KICKOUT; 房间中剩余人员(包括操作者)将收到notifyUserLeftMeeting通知; 

### sendMeetingCustomMsg 

- 功能: 房间内发送广播消息 

返回值: 无 

##### sdk_engine.sendMeetingCustomMsg(msg, cookie) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|msg|string|自定义消息内容,最大8KB字节|
|cookie|string|详细介绍见cookie|

补充说明: 

发送结果请参见sendMeetingCustomMsgRslt; 只有当前在房间内的人员才能收到此消息; 

### notifyUserEnterMeeting 

功能: 通知有人进入房间 

js 

sdk_engine.on("notifyUserEnterMeeting", (userID) => {}) 

|参数|类型|说明|
|---|---|---|
|userID|string|用户ID, 详细介绍见关键词|

### notifyUserLeftMeeting 

功能: 通知有人离会 

sdk_engine.on("notifyUserLeftMeeting", (userID) => {}) 

js 

|参数|类型|说明|
|---|---|---|
|userID|string|用户ID, 详细介绍见关键词|

### setNickNameRslt 

功能: 修改昵称结果 

sdk_engine.on("setNickNameRslt", (userID, sdkErr) => {}) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|userID|string|用户ID, 详细介绍见关键词|
|sdkErr|CRVSDK_ERR_DEF|错误码|

### notifyNickNameChanged 

功能: 通知昵称变化 

sdk_engine.on("notifyNickNameChanged", (userID, oldName, newName, operatorID) => {}) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|userID|string|用户ID, 详细介绍见关键词|
|oldName|string|旧昵称|
|newName|string|新昵称|
|operatorID|string|操作者的用户ID|

### kickoutRslt 

#### 功能: 请出房间结果 

sdk_engine.on("kickoutRslt", (userID, sdkErr) => {}) 

js 

|参数|类型|说明|
|---|---|---|
|userID|string|用户ID, 详细介绍见关键词|

sdkErr CRVSDK_ERR_DEF 错误码 参数 类型 说明 

### sendMeetingCustomMsgRslt 

功能: 发送房间内广播消息结果 

sdk_engine.on("sendMeetingCustomMsgRslt", (sdkErr, cookie) => {}) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|sdkErr|CRVSDK_ERR_DEF|错误码|
|cookie|string|详细介绍见cookie|

### notifyMeetingCustomMsg 

功能: 通知房间内广播消息 

sdk_engine.on("notifyMeetingCustomMsg", (fromUserID, msg) => {}) 

js 

|参数|类型|说明|
|---|---|---|
|fromUserID|string|发送者用户ID|
|msg|string|自定义消息内容|

### getMeetingAllAttrs 

- 功能: 获取所有房间属性 

返回值: 无 

sdk_engine.getMeetingAllAttrs(cookie) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|cookie|string|详细介绍见cookie|

补充说明: 

获取结果请参见:getMeetingAllAttrsSuccess 或 getMeetingAllAttrsFail 

### getMeetingAttrs 

- 功能: 获取部份房间属性 

- 返回值: 无 

sdk_engine.getMeetingAttrs(jsonKeys, cookie) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|jsonKeys|string|需要查询的房间属性key,json格式,如:["key1", "key2"]|
|cookie|string|详细介绍见cookie|

补充说明: 

获取结果请参见:getMeetingAttrsSuccess 或 getMeetingAttrsFail 

### setMeetingAttrs 

功能: 重置所有房间属性 

返回值: 无 

##### sdk_engine.setMeetingAttrs(jsonAttrs, options, cookie) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|jsonAttr s|strin g|房间属性集,json格式,如:{"key1":"value1", "key2":"value2"} (key最大长度为64B,value最大长 度为8KB)|
|options|strin g|操作选项,json格式,参见CRMeetingAttrOptions|
|cookie|strin g|详细介绍见cookie|

补充说明: 

设置结果请参见:setMeetingAttrsRslt 

### addOrUpdateMeetingAttrs 

功能: 添加或更新房间属性 

返回值: 无 

##### sdk_engine.addOrUpdateMeetingAttrs(jsonAttrs, options, cookie) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|jsonAttr s|strin g|房间属性集,json格式,如:{"key1":"value1", "key2":"value2"} (key最大长度为64B,value最大长 度为8KB)|
|options|strin g|操作选项,json格式,参见CRMeetingAttrOptions|
|cookie|strin g|详细介绍见cookie|

#### 补充说明: 

结果请参见:addOrUpdateMeetingAttrsRslt 

### delMeetingAttrs 

功能: 删除房间属性 

返回值: 无 

sdk_engine.delMeetingAttrs(jsonKeys, options, cookie) 

|js|
|---|

参数 类型 说明 jsonKeys string 需要删除的房间属性key,json格式,如:["key1", "key2"] 

|~~jsonKeys~~|~~string~~|~~需要删除的房间属性key,json格式,如:[ key1 , key2 ]~~|
|---|---|---|
|~~options~~ ~~参数~~|~~string~~ ~~类型~~|~~操作选项,json格式,参见CRMeetingAttrOptions~~ ~~说明~~|
|cookie|string|详细介绍见cookie|

补充说明: 

结果请参见:delMeetingAttrsRslt 

### clearMeetingAttrs 

功能: 清空所有房间属性 

返回值: 无 

##### sdk_engine.clearMeetingAttrs(options, cookie) 

js 

|参数|类型|说明|
|---|---|---|
|options|string|操作选项,json格式,参见CRMeetingAttrOptions|
|cookie|string|详细介绍见cookie|

补充说明: 

结果请参见:clearMeetingAttrsRslt 

### getMeetingAllAttrsSuccess 

功能: 获取所有房间属性成功 

sdk_engine.on("getMeetingAllAttrsSuccess", (attrs, cookie) => {}) 

js 

|参数|类型|说明|
|---|---|---|
|attrs|string|房间属性集,json结构体请参见CRAttrObjs|
|cookie|string|详细介绍见cookie|

### getMeetingAllAttrsFail 

功能: 获取所有房间属性失败 

sdk_engine.on("getMeetingAllAttrsFail", (sdkErr, cookie) => {}) 

js 

|参数|类型|说明|
|---|---|---|
|sdkErr|CRVSDK_ERR_DEF|错误码|
|cookie|string|详细介绍见cookie|

### getMeetingAttrsSuccess 

功能: 获取部份房间属性成功 

js 

sdk_engine.on("getMeetingAttrsSuccess", (attrs, cookie) => {}) 

|参数 参数|类型 类型|说明 说明|
|---|---|---|
|attrs|string|房间属性集,json结构体请参见CRAttrObjs|
|cookie|string|详细介绍见cookie|

### getMeetingAttrsFail 

功能: 获取部份房间属性失败 

sdk_engine.on("getMeetingAttrsFail", (sdkErr, cookie) => {}) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|sdkErr|CRVSDK_ERR_DEF|错误码|
|cookie|string|详细介绍见cookie|

### setMeetingAttrsRslt 

功能: 重置所有房间属性结果 

sdk_engine.on("setMeetingAttrsRslt", (sdkErr, cookie) => {}) 

js 

|参数|类型|说明|
|---|---|---|
|sdkErr|CRVSDK_ERR_DEF|错误码|
|cookie|string|详细介绍见cookie|

### addOrUpdateMeetingAttrsRslt 

功能: 添加或更新房间属性结果 

sdk_engine.on("addOrUpdateMeetingAttrsRslt", (sdkErr, cookie) => {}) 

js 

|参数|类型|说明|
|---|---|---|
|sdkErr|CRVSDK_ERR_DEF|错误码|
|cookie|string|详细介绍见cookie|

### delMeetingAttrsRslt 

功能: 删除房间属性结果 

##### sdk_engine.on("delMeetingAttrsRslt", (sdkErr, cookie) => {}) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|sdkErr|CRVSDK_ERR_DEF|错误码|
|cookie|string|详细介绍见cookie|

clearMeetingAttrsRslt 

功能: 清空所有房间属性结果 

js 

sdk_engine.on("clearMeetingAttrsRslt", (sdkErr, cookie) => {}) 

|参数|类型|说明|
|---|---|---|
|sdkErr|CRVSDK_ERR_DEF|错误码|
|cookie|string|详细介绍见cookie|

### notifyMeetingAttrsChanged 

功能: 通知房间属性改变 

sdk_engine.on("notifyMeetingAttrsChanged", (adds, updates, delKeys) => {}) 

js 

|参数|类型 说明|
|---|---|
|adds|string 增加房间属性集,json结构体请参见CRAttrObjs|
|updates|string 变化的用户属性集,json结构体请参见CRAttrObjs|
|delKeys|string 被删除的用户属性列表,json格式,如:["key1", "key2"]|
|getUserAttr 功能: 获 返回值: 参数 sdk_engine.|s 取指定用户的所有属性 无 类型 说明 getUserAttrs(jsonUIds,jsonKeys,cookie) js|
|jsonUIds|string 目标用户id列表,一次最多包含50个用户,json格式, 如:["uid1","uid2"]|
|jsonKeys|string 将要获取的用户属性key列表(空串代表获取全部),json格式,如:["key1","key2"]|
|cookie|string 详细介绍见cookie|

补充说明: 

结果请参见:getUserAttrsSuccess 或 getUserAttrsFail 

### setUserAttrs 

功能: 重置指定用户的属性 返回值: 无 

sdk_engine.setUserAttrs(userID, jsonAttrs, options, cookie) 

js 

|参数|类型|说明|
|---|---|---|
|userID|strin g|用户ID, 详细介绍见关键词|
|jsonAttr|strin|用户属性集, json格式,如:{"key1":"value1", "key2":"value2"} (key最大长度为64B,value最大|

|s 参数|g 类型|长度为8KB) 说明|
|---|---|---|
|options|strin g|操作选项,json格式,参见CRMeetingAttrOptions|
|cookie|strin g|详细介绍见cookie|

补充说明: 

结果请参见:setUserAttrsRslt 

### addOrUpdateUserAttrs 

功能: 添加或更新指定用户的属性 

返回值: 无 

##### sdk_engine.addOrUpdateUserAttrs(userID, jsonAttrs, options, cookie) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|userID|strin g|用户ID, 详细介绍见关键词|
|jsonAttr s|strin g|用户属性集, json格式,如:{"key1":"value1", "key2":"value2"} (key最大长度为64B,value最大 长度为8KB)|
|options|strin g|操作选项,json格式,参见CRMeetingAttrOptions|
|cookie|strin g|详细介绍见cookie|

#### 补充说明: 

结果请参见:addOrUpdateUserAttrsRslt 

### delUserAttrs 

功能: 删除指定用户的属性 返回值: 无 

sdk_engine.delUserAttrs(userID, jsonKeys, options, cookie) 

js 

|参数|类型|说明|
|---|---|---|
|userID|string|用户ID, 详细介绍见关键词|
|jsonKeys|string|需要删除的用户属性key列表,json格式,如:["key1","key2"]|
|options|string|操作选项,json格式,参见CRMeetingAttrOptions|
|cookie|string|详细介绍见cookie|

补充说明: 

结果请参见:delUserAttrsRslt 

clearUserAttrs 

#### 功能: 清空指定用户的属性 

返回值: 无 

##### sdk_engine.clearUserAttrs(userID, options, cookie) 

js 

|参数|类型|说明|
|---|---|---|
|userID|string|用户ID, 详细介绍见关键词|
|options|string|操作选项,json格式,参见CRMeetingAttrOptions|
|cookie|string|详细介绍见cookie|

补充说明: 

结果请参见:clearUserAttrsRslt 

### clearAllUserAttrs 

功能: 清空所有用户的属性 返回值: 无 

##### sdk_engine.clearAllUserAttrs(options, cookie) 

js 

|参数|类型|说明|
|---|---|---|
|options|string|操作选项,json格式,参见CRMeetingAttrOptions|
|cookie|string|详细介绍见cookie|

补充说明: 

结果请参见:clearAllUserAttrsRslt 

### getUserAttrsSuccess 

功能: 获取指定用户的所有属性成功 

sdk_engine.on("getUserAttrsSuccess", (attrs, cookie) => {}) 

js 

|参数|类型|说明|
|---|---|---|
|attrs|string|用户属性集,json结构体请,参见CRUsrAttrObjs|
|cookie|string|详细介绍见cookie|

### getUserAttrsFail 

功能: 获取指定用户的所有属性失败 

sdk_engine.on("getUserAttrsFail", (sdkErr, cookie) => {}) 

js 

|参数|类型|说明|
|---|---|---|
|sdkErr|CRVSDK_ERR_DEF|错误码|

cookie参数 类型string 

说明详细介绍见cookie 

### setUserAttrsRslt 

#### 功能: 重置指定用户的属性结果 

sdk_engine.on("setUserAttrsRslt", (sdkErr, cookie) => {}) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|sdkErr|CRVSDK_ERR_DEF|错误码|
|cookie|string|详细介绍见cookie|

### addOrUpdateUserAttrsRslt 

功能: 添加或更新指定用户的属性结果 

sdk_engine.on("addOrUpdateUserAttrsRslt", (sdkErr, cookie) => {}) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|sdkErr|CRVSDK_ERR_DEF|错误码|
|cookie|string|详细介绍见cookie|

### delUserAttrsRslt 

#### 功能: 删除指定用户的属性结果 

sdk_engine.on("delUserAttrsRslt", (sdkErr, cookie) => {}) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|sdkErr|CRVSDK_ERR_DEF|错误码|
|cookie|string|详细介绍见cookie|

### clearUserAttrsRslt 

#### 功能: 清空指定用户的属性结果 

sdk_engine.on("clearUserAttrsRslt", (sdkErr, cookie) => {}) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|sdkErr|CRVSDK_ERR_DEF|错误码|
|cookie|string|详细介绍见cookie|

### clearAllUserAttrsRslt 

功能: 清空所有用户的属性结果 

js 

sdk engine on("clearAllUserAttrsRslt" (sdkErr cookie) > {}) 

sdk_engine.on( clearAllUserAttrsRslt , (sdkErr, cookie) => {}) 

|参数|类型|说明|
|---|---|---|
|sdkErr|CRVSDK_ERR_DEF|错误码|
|cookie|string|详细介绍见cookie|

### notifyUserAttrsChanged 

功能: 通知用户属性改变 

sdk_engine.on("notifyUserAttrsChanged", (userID, adds, updates, delKeys) => {}) 

js 

|参数|类型|说明|
|---|---|---|
|userID|string|用户ID, 详细介绍见关键词|
|adds|string|增加的用户属性集,json结构体请参见CRUsrAttrObjs|
|updates|string|变化的用户属性集,json结构体请参见CRUsrAttrObjs|
|delKeys|string|被删除的用户属性列表,json格式,如:["key1", "key2"]|

### getAudioMics 

- 功能: 获取系统麦克风设备列表 

返回值: Array<CRAudioDevInfo>,麦克风设备列表 

##### sdk_engine.getAudioMics() 

js 

### getAudioSpks 

- 功能: 获取系统扬声器设备列表 

返回值: Array<CRAudioDevInfo>,麦克风设备列表 

sdk_engine.getAudioSpks() 

js 

### getAudioCfg 

- 功能: 获取当前音频配置 

- 返回值: CRAudioCfg 

sdk_engine.getAudioCfg() 

js 

### setAudioCfg 

- 功能: 设置音频参数 

- 返回值: 无 

sdk_engine.setAudioCfg(cfg) 

js 

参数 

类型 

说明 

参数cfg 类型CRAudioCfg 

说明音频配置 

### getMicVolume 

- 功能: 获取麦克风音量 

返回值: number,音量,0~255 

sdk_engine.getMicVolume() 

js 

### setMicVolume 

- 功能: 配置麦克风音量 

- 返回值: 无 

##### sdk_engine.setMicVolume(volume) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|volume|number|音量,0~255|

### getSpkVolume 

- 功能: 获取扬声器音量 

返回值: number,音量,0~255 

sdk_engine.getSpkVolume() 

js 

### setSpkVolume 

- 功能: 配置扬声器音量 

- 返回值: 无 

sdk_engine.setSpkVolume(volume) 

js 

|参数|类型|说明|
|---|---|---|
|volume|number|音量,0~255|

### getSpeakerMute 

- 功能: 获取扬声器静音状态 

返回值: true:静音、false:不静音 

sdk_engine.getSpeakerMute() 

|js|
|---|

### setSpeakerMute 

- 功能: 配置扬声器静音 

- 返回值: 无 

js 

sdk engine.setSpeakerMute(bMute) 

sd _e g e setSpea e ute(b ute) 

|参数|类型|说明|
|---|---|---|
|bMute|boolean|true:静音、false:不静音|

### startEchoTest 

- 功能: 开始本地语音环回测试 

返回值: 错误码,详细见错误码定义 

sdk_engine.startEchoTest() 

js 

### stopEchoTest 

- 功能: 停止本地语音环回测试 

- 返回值: 无 

sdk_engine.stopEchoTest() 

js 

### isEchoTesting 

- 功能: 检查是否在本地语音环回测试 

- 返回值: 是否在测试中(boolean) 

sdk_engine.isEchoTesting() 

js 

### openMic 

- 功能: 打开麦克风 

- 返回值: 无 

sdk_engine.openMic(userID) 

js 

|参数|类型|说明|
|---|---|---|
|userID|string|用户ID, 详细介绍见关键词|

#### 补充说明: 

打开自已的麦克风时,先会进入到CRVSDK_AST_OPENING状态,等服务器处理后才会进入CRVSDK_AST_OPEN状态; 当用户的麦克风状态变为CRVSDK_AST_OPEN状态时,说话才能被采集到; 一个房间最大开麦数为8,超出的开麦人将保持在CRVSDK_AST_OPENING状态; 

CRVSDK_AST_OPENING状态的麦不会在有人关麦时自动打开,需要按需再次执行openMic; 麦克风状态改变时,房间中所有人将收到notifyMicStatusChanged通知; 

### closeMic 

功能: 关闭麦克风 返回值: 无 

js 

sdk_engine.closeMic(userID) 

|参数|类型|说明|
|---|---|---|
|userID|string|用户ID, 详细介绍见关键词|

补充说明: 

关麦操作是立即生效的,本地会立即停止采集; 房间中所有人将收到notifyMicStatusChanged通知; 

### closeAllMic 

功能: 全体关麦 

返回值: 无 

##### sdk_engine.closeAllMic() 

js

补充说明: 

全体关麦时,不关闭操作者自已的麦; 

### getMicStatus 

功能: 获取指定人员的麦克风状态 

返回值: CRVSDK_ASTATUS 

##### sdk_engine.getMicStatus(userID) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|userID|string|用户ID, 详细介绍见关键词|

### getLocMicDevEnergy 

- 功能: 获取本地麦克风设备能量等级 

返回值: 能量等级0~9 ,9为最大能量等级(number) 

##### sdk_engine.getLocMicDevEnergy() 

|js|
|---|

#### 补充说明: 

房间中关麦仍能获取当前麦设备的能量值; 如果想获取在房间中的能量值,请使用getUserMicEnergy; 

### getUserMicEnergy 

功能: 获取房间中指定人员麦克风能量等级 

返回值: 能量等级0~9 ,9为最大能量等级(number) 

##### sdk_engine.getUserMicEnergy(userID) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|userID|string|用户ID, 详细介绍见关键词|

#### 补充说明: 

房间中关麦后,获取的麦能量值将为0 

如果想获取当前麦设备实际能量值,请使用getLocMicDevEnergy; 

### getVoiceChangeType 

#### 功能: 获取目标用户变声类型 

返回值: number,预定义变声类型:CRVSDK_VOICECHANGE_TYPE
自定义变声:取值100~200, 150为原 声,<150为降调,>150为升调 

##### sdk_engine.getVoiceChangeType(userID) 

js 

|参数|类型|说明|
|---|---|---|
|userID|string|用户ID, 详细介绍见关键词|

### setVoiceChange 

功能: 设置目标用户变声 

返回值: 无 

##### sdk_engine.setVoiceChange(userID, type) 

js

|参数|类型|说明|
|---|---|---|
|userID|string|用户ID, 详细介绍见关键词|
|type|number|预定义变声类型:CRVSDK_VOICECHANGE_TYPE 自定义变声:取值100~200, 150为原声,<150为降调,>150为升调|

补充说明: 

变声功能为服务器实现,所以本地录制、本地声音环回测试,声音都是不变声过的; 

### setAudioSubscribeMode 

功能: 设置语音订阅模式 

返回值: 无 

##### sdk_engine.setAudioSubscribeMode(mode) 

js 

|参数|类型|说明|
|---|---|---|
|mode|CRVSDK_ASUBSCRIB_MODE|订阅模式|

#### 补充说明: 

sdk内部默认为CRVSDK_ASM_MIXED模式,此模式进入房间成功就能听到房间内所有开麦人的声音; 配置为CRVSDK_ASM_SEPARATE模式后,默认不订阅任何人的声音,需要调 用setAudioSubscribeListForSeparateMode设置要订阅的人员名单; 此接口在进入房间前可调用, 程序退出后失效; 

### setAudioSubscribeListForSeparateMode 

功能: 设置独立音频订阅名单 

js 

#### 返回值: 无 

##### sdk_engine.setAudioSubscribeListForSeparateMode(type, userIds) 

|参数|类型|说明|
|---|---|---|
|type|CRVSDK_ASUBSCRIB_LISTTYPE|列表类型|
|userIds|string|用户ID列表,使用";"分割|

#### 补充说明: 

只有在CRVSDK_ASM_SEPARATE音频订阅模式下才能设置,可调用setAudioSubscribeMode修改模式; 切换到其它音频订阅模式时,之前设置的名单自动失效; 此接口在进入房间前可调用,程序退出后失效; 白名单和黑名单不共存,后面的数据将覆盖之前的数据; 其他人员进出房间、开关麦,不影响设置的名单;sdk内部会退订离开或关麦的流,在开麦后再次订阅; 

### notifyAudioDevChanged 

功能: 通知本地音频设备变化 

sdk_engine.on("notifyAudioDevChanged", () => {}) 

js 

### notifyAudioErr 

功能: 通知本地音频相关错误 

##### sdk_engine.on("notifyAudioErr", (sdkErr) => {}) 

js 

|参数|类型|说明|
|---|---|---|
|sdkErr|CRVSDK_ERR_DEF|错误码|

### notifyMicStatusChanged 

#### 功能: 通知房间中有人麦克风状态变化 

##### sdk_engine.on("notifyMicStatusChanged", (userID, oldStatus, newStatus, operatorID) => {}) 

js 

|参数|类型|说明|
|---|---|---|
|userID|string|用户ID, 详细介绍见关键词|
|oldStatus|number|旧的麦克风状态|
|newStatus|number|新的麦克风状态|
|operatorID|string|操作者的用户ID|

### notifyMicEnergy 

功能: 通知房间有人麦克风能量变化 

js 

js 

sdk_engine.on("notifyMicEnergy", (userID, oldLevel, newLevel) => {}) 

|参数|类型|说明|
|---|---|---|
|userID|string|用户ID, 详细介绍见关键词|
|oldLevel|number|之前的说话声音强度(0~10)|
|newLevel|number|现在的说话声音强度(0~10)|

### notifySetVoiceChange 

#### 功能: 通知房间中有人变声状态变化 

sdk_engine.on("notifySetVoiceChange", (userID, type, operatorID) => {}) 

js 

|参数|类型|说明|
|---|---|---|
|userID|string|用户ID, 详细介绍见关键词|
|type|number|预定义变声类型:CRVSDK_VOICECHANGE_TYPE 自定义变声:取值100~200, 150为原声,<150为降调,>150为升调|
|operatorID|string|操作者的用户ID|

### notifyCloseAllMic 

#### 功能: 通知有人发起了全体关麦操作 

sdk_engine.on("notifyCloseAllMic", (operatorID) => {}) 

js 

|参数|类型|说明|
|---|---|---|
|operatorID|string|操作者的用户ID|

### addCanvas 

功能: 订阅绘制视图画面 

返回值: 无 

##### sdk_engine.addCanvas(config) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|config|CRCanvas|视图控件配置|

#### 补充说明: 

界面上需要显示摄像头、影音共享、屏幕共享的画面,都需要通过该接口订阅视频,示例代码参见视图组件 

### rmCanvas 

功能: 取消订阅绘制视图画面 返回值: 无 

js 

sdk engine rmCanvas(viewID) 

sdk_engine.rmCanvas(viewID) 

|参数|类型|说明|
|---|---|---|
|viewID|string|要销毁的视图控件ID,参见addCanvas|

### getAllVideoInfo 

- 功能: 获取指定成员的所有摄像头信息 

返回值: Array<CRVideoDevInfo>,视频设备信息 

##### sdk_engine.getAllVideoInfo(userID) 

js 

|参数|类型|说明|
|---|---|---|
|userID|string|用户ID, 详细介绍见关键词|

### getVideoCfg 

- 功能: 获取本地视频全局配置 

- 返回值: 视频全局配置,请参见CRVideoCfg 

sdk_engine.getVideoCfg() 

js 

### setVideoCfg 

- 功能: 设置本地视频全局配置 

- 返回值: 错误码,详细见错误码定义 

##### sdk_engine.setVideoCfg(cfg) 

js 

|参数|类型|说明|
|---|---|---|
|cfg|CRVideoCfg|视频全局配置|

### openVideo 

- 功能: 打开指定人的摄像头 

返回值: 无 

##### sdk_engine.openVideo(userID) 

js 

|参数|类型|说明|
|---|---|---|
|userID|string|用户ID, 详细介绍见关键词|

补充说明: 

打开用户的摄像头,以便本地、远端显示视频图像; 开启摄像头后可通过视频组件将画面渲染到界面上; 打开多个摄像头,参见setMutiVideos; 

closeVideo 

#### 功能: 关闭指定人的摄像头 

返回值: 无 

##### sdk_engine.closeVideo(userID) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|userID|string|用户ID, 详细介绍见关键词|

### getVideoStatus 

- 功能: 获取房间中指定成员的视频状态 

返回值: CRVSDK_VSTATUS 

##### sdk_engine.getVideoStatus(userID) 

js 

|参数|类型|说明|
|---|---|---|
|userID|string|用户ID, 详细介绍见关键词|

### setDefaultVideo 

- 功能: 配置默认摄像头 

返回值: 无 

##### sdk_engine.setDefaultVideo(videoID) 

js 

|参数|类型|说明|
|---|---|---|
|videoID|number|摄像头ID|

#### 补充说明: 

sdk内部会自动产生默认摄像头,除非系统没有任何真实摄像头、自定义摄像头、网络摄像头等; 当默认摄像头被移除时,sdk内部会自动产生一个新的默认摄像头; sdk内部产生默认摄像头时,优先将将打开的多摄像头上选择; 

### getDefaultVideo 

- 功能: 获取默认摄像头 

返回值: 摄像头ID(number), 0代表没有默认摄像头 

##### sdk_engine.getDefaultVideo(userID) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|userID|string|用户ID, 详细介绍见关键词|

### setMutiVideos 

- 功能: 配置本地多摄像头 

返回值: 无 

js 

sdk_engine.setMutiVideos(moreVideos, count) 

|参数|类型|说明|
|---|---|---|
|moreVideos|Array<Number>|需要开启的摄像头ID列表(不应该包含默认摄像头,即使传入也会被忽略)|
|count|number|moreVideoIDs个数,0代表关闭多摄像头功能|

### getMutiVideos 

- 功能: 获取本地的或他人的多摄像头列表 

返回值: Array<Number>,摄像头ID列表 

##### sdk_engine.getMutiVideos(userID) 

js 

|参数|类型|说明|
|---|---|---|
|userID|string|用户ID, 详细介绍见关键词|

### setLocVideoAttributes 

- 功能: 设置本地指定设备私有配置 

返回值: 无 

##### sdk_engine.setLocVideoAttributes(videoID, jsonAttributes) 

js 

|参数|类型|说明|
|---|---|---|
|videoID|number|摄像头ID|
|jsonAttributes|string|json格式,请参见CRVideoAttributesObj|

### getLocVideoAttributes 

- 功能: 获取本地指定设备私有配置 

返回值: string, json格式,请参见CRVideoAttributesObj 

##### sdk_engine.getLocVideoAttributes(videoID) 

js

|参数|类型|说明|
|---|---|---|
|videoID|number|摄像头ID|

### setVideoEffects 

功能: 配置视频效果参数 

返回值: 无 

sdk_engine.setVideoEffects(efs) 

js 

参数 类型 说明 efs string 视频效果配置 json字符串 请参见CRVideoEffectsObj 

~~efs string 视频效果配置,json字符串,请参见CRVideoEffectsObj 参数 类型 说明~~ 

### getVideoEffects 

- 功能: 获取视频效果参数 

返回值: 视频效果配置,json字符串,请参见CRVideoEffectsObj 

sdk_engine.getVideoEffects() 

js

### notifyVideoDevChanged 

- 功能: 通知用户视频设备变化(设备个数、设备能力参数、默认设备、启停多摄像头等) 

sdk_engine.on("notifyVideoDevChanged", (userID) => {}) 

js 

|参数|类型|说明|
|---|---|---|
|userID|string|用户ID, 详细介绍见关键词|

### notifyDefaultVideoChanged 

功能: 通知用户默认视频设备变化 

sdk_engine.on("notifyDefaultVideoChanged", (userID, videoID) => {}) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|userID|string|用户ID, 详细介绍见关键词|
|videoID|number|摄像头ID|

### openVideoDevRslt 

功能: 本地视频设备打开结果 

sdk_engine.on("openVideoDevRslt", (videoID, isSucceed) => {}) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|videoID|number|摄像头ID|
|isSucceed|boolean|打开结果|

### notifyVideoStatusChanged 

功能: 通知用户视频状态变化 

sdk_engine.on("notifyVideoStatusChanged", (videoID, oldStatus, newStatus, operatorID) => {}) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|videoID|number|摄像头ID|
|oldStatus|number|旧的视频状态|

|newStatus 参数|number 类型|新的视频状态 说明|
|---|---|---|
|operatorID|string|操作者的用户ID|

### createCustomVideoDev 

#### 功能: 创建自定义摄像头 

返回值: >=0添加成功,返回值为videoID(摄像头ID); <0代表添加失败,参见错误码 

##### sdk_engine.createCustomVideoDev(camName, pixFmt, width, height) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|camName|string|摄像头名|
|pixFmt|CRVSDK_VIDEO_FORMAT|图像格式,CRVSDK_VFMT_YUV420P格式性能最佳;|
|width|number|图像宽|
|height|number|图像高|

补充说明: 

#### 最多支持添加5个; 

添加成功后与本地摄像头处理一致;本地通过getAllVideoInfo接口可以识别哪些是自定义摄像头; 添加的摄像头在反初始化时删除; 

创建成功后,调用inputCustomVideoDat送入摄像头图像数据; 

### destroyCustomVideoDev 

- 功能: 销毁自定义摄像头 

返回值: 无 

##### sdk_engine.destroyCustomVideoDev(videoID) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|videoID|number|摄像头ID|

### inputCustomVideoDat 

- 功能: 送入自定义摄像头数据 

返回值: 错误码,详细见错误码定义 

##### sdk_engine.inputCustomVideoDat(videoID, frm) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|videoID|number|摄像头ID|
|frm|CRVideoFrame|图像数据(请保证格式、和尺寸与摄像头一致)|

### addIPCam 

功能: 添加网络摄像头 

返回值: 返回值>=0代表添加成功 返回值为videoID(摄像头ID);返回值<0代表添加失败 参见错误码 

返回值: 返回值>=0代表添加成功,返回值为videoID(摄像头ID); 返回值<0代表添加失败,参见错误码 

js 

##### sdk_engine.addIPCam(url, jsonParam) 

|参数|类型|说明|
|---|---|---|
|url|string|网络摄像头url,支持协议:rtmp,rtsp|
|||json格式参数,可不传, 支持:|
|jsonParam|string|name:摄像头名称,不配置则为url maxRetry:连接失败或中断连时重试连接次数,<0代表无限重试,默认值-1|

#### 示例代码: 

```arkts
const rtmp = 'rtmp://xxxx'; const jsonParam = { name: '摄像头名称' } const videoID = sdk_engine.addIPCam(rtmp, JSON.stringify(jsonParam)); if (videoID < 0) { 
```

js 

//小于0,添加失败 ' console.log( 添加失败,错误码: ' + videoID); } else { 

sdk_engine.setDefaultVideo(videoID); //设置为默认摄像头 } 

补充说明: 

#### 最多支持添加5个; 

添加成功后与本地摄像头处理一致;本地通过getAllVideoInfo接口可以识别哪些是网络摄像头; 添加的摄像头在反初始化时删除; 

### delIPCam 

- 功能: 删除网络摄像头 

返回值: 无 

sdk_engine.delIPCam(videoID) 

js 

|参数|类型|说明|
|---|---|---|
|videoID|number|摄像头ID|

### setMediaCfg 

- 功能: 设置影音共享配置 

返回值: 错误码,详细见错误码定义 

|sdk_engine.setM|ediaCfg(jsonCfg)|js|
|---|---|---|
|参数|类型|说明|
|jsonCfg|string|影音共享配置,json格式,请参见CRVideoCfg|

getMediaCfg 

#### 功能: 获取影音共享配置 

返回值: 影音共享配置,json格式,请参见CRVideoCfg 

##### sdk_engine.getMediaCfg() 

|js|
|---|

### startPlayMedia 

#### 功能: 开始影音共享 

返回值: 无 

|sdk_engine.startPlayMedia(fileName,bLocPlay,bPauseWhenFinished)|
|---|

|js|
|---|

|参数|类型|说明|
|---|---|---|
|fileName|string|文件全路径或者网络地址|
|bLocPlay|boolea n|是否本地播放。本地播放时,声音图像不会送入房间,适用于本地录像检测,默认 值false|
|bPauseWhenFinish ed|boolea n|文件正常播放完成时,暂停在文件未尾,默认值false|

补充说明: 

#### 开启后可通过视频组件将画面渲染到界面上 

支持本地完整路径文件,支持mp4、flv、avi、wmv、mkv、mov、3gp、wma、mp3、m4a、wav等常见文件格式; 支持网络媒体流,支持的协议有:http、rtmp、rtsp; 

一个房间同一时间只能一个影音共享(本地播放除外); 

开启共享失败时,将有startPlayMediaFail回调; 

开启共享成功时,房间内所有人都将收到notifyMediaStart通知; 

开启共享成功后,共享端开始向房间内播放文件,共享者在文件打开成功时将收回notifyMediaOpened回调; 共享中,如果文件打开失败、或中途读取失败、或播放结果, sdk内部将自动停止影音共享,房间内所有人都将收 到notifyMediaStop通知; 

### pausePlayMedia 

功能: 暂停影音共享 

返回值: 无 

##### sdk_engine.pausePlayMedia(bPause) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|bPause|boolean|暂停共享true/恢复共享false|

补充说明: 

共享暂停后,房间内所有人将收到notifyMediaPause通知; 

### stopPlayMedia 

功能: 停止影音共享 返回值: 无 

js 

sdk engine.stopPlayMedia() 

sd _e g e stop ay ed a() 

补充说明: 

可以停止本地或他人的影音共享; 

影音共享被停止时,房间内所有人将收到notifyMediaStop通知; 

### setMediaPlayPos 

- 功能: 设置播放位置 

返回值: 无 

sdk_engine.setMediaPlayPos(ms) 

js 

|参数|类型|说明|
|---|---|---|
|ms|number|设置播放位置,单位:毫秒|

### getMediaInfo 

- 功能: 获取当前影音共享信息 

- 返回值: 共享信息,参见CRMediaInfo 

##### sdk_engine.getMediaInfo() 

js 

### getMediaStreamInfo 

- 功能: 获取当前影音共享流信息 

- 返回值: CRVStreamInfo 

sdk_engine.getMediaStreamInfo() 

|js|
|---|

### setMediaVolume 

- 功能: 配置影音播放音量 

返回值: 无 

|sdk_engine.setMediaVolume(volume) js|
|---|

|参数|类型|说明|
|---|---|---|
|volume|number|影音音量,范围:0~255|

补充说明: 

此调整同时影响本地影音的播放音量,也影晌他人的影音播放音量; 此调整不影响他人的说话声音大小; 

### getMediaVolume 

功能: 获取影音播放音量 

返回值: 影音音量,范围:0~255 

js 

sdk engine getMediaVolume() 

j 

sdk_engine.getMediaVolume() 

### startPlayMediaFail 

#### 功能: 影音共享开启失败 

|sdk_engine.on("startPlayMediaFail", (sdkErr) => {})|js|
|---|---|
|参数 类型|说明|
|sdkErr CRVSDK_ERR_DEF|错误码|

### notifyMediaStart 

功能: 通知影音共享开启 

sdk_engine.on("notifyMediaStart", (userID) => {}) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|userID|string|用户ID, 详细介绍见关键词|

补充说明: 

收到通知后可通过视频组件将画面渲染到界面上 

### notifyMediaOpened 

功能: 本地影音共享文件打开成功通知 

sdk_engine.on("notifyMediaOpened", (totalTime, w, h) => {}) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|totalTime|number|文件总时长(ms), -1代表没有总时长(通常为网络摄像头、直播流等)|
|w|number|图像宽|
|h|number|图像高|

### notifyMediaStop 

#### 功能: 通知影音共享停止 

|sdk_engine.on("notifyMediaStop", (userID,reason) => {})|
|---|

|js|
|---|

|参数|类型|说明|
|---|---|---|
|userID|string|用户ID, 详细介绍见关键词|
|reason|CRVSDK_MEDIA_STOPREASON|停止的原因|

### notifyMediaPause 

功能: 通知影音共享暂停 

js 

sdk_engine.on("notifyMediaPause", (userID, bPause) => {}) 

|参数|类型|说明|
|---|---|---|
|userID|string|用户ID, 详细介绍见关键词|
|bPause|boolean|是否暂停|

### notifyScreenShareStarted 

功能: 通知屏幕共享开始 

##### sdk_engine.on("notifyScreenShareStarted", (userID) => {}) 

js 

|参数|类型|说明|
|---|---|---|
|userID|string|用户ID, 详细介绍见关键词|

补充说明: 

收到通知后可通过视频组件将画面渲染到界面上 

### notifyScreenShareStopped 

功能: 通知屏幕共享停止 

##### sdk_engine.on("notifyScreenShareStopped", (operatorID) => {}) 

js 

|参数|类型|说明|
|---|---|---|
|operatorID|string|操作者的用户ID|

### createLocMixer 

- 功能: 创建本地混图器 

返回值: 错误码 

##### sdk_engine.createLocMixer(mixerID, mixerCfg, mixerContents) 

js 

|参数|类型|说明|
|---|---|---|
|mixerID|string|混图器唯一标识|
|mixerCfg|CRLocMixerCfgObj|混图器规格配置|
|mixerContents|Array<CRMixerContentObj>|混图器内容配置|

#### 补充说明: 

创建本地混图器(用于本地录制、本地推流),当需要多个不同内容的录制、或直播时,就要创建多个混图器 。混 图器开消比较大,多个同样图像的输出应该有一个混图器加上多个输出实现; 开启成功后,可以通过updateLocMixerContent更新内容; 

开启成功后,可以通过addLocMixerOutput添加输出目标,如输出到文件,或输出到网络直播流; 混图器如果异常停止时,将通过notifyLocMixerStateChanged回调用户; 

### updateLocMixerContent 

- 功能: 更新本地混图器内容 

- 返回值: 错误码 

##### sdk_engine.updateLocMixerContent(mixerID, mixerContents) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|mixerID|string|混图器唯一标识|
|mixerContents|Array<CRMixerContentObj>|混图器内容配置|

### destroyLocMixer 

- 功能: 销毁本地混图器 

- 返回值: 无 

sdk_engine.destroyLocMixer(mixerID) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|mixerID|string|混图器唯一标识|

补充说明: 

销毁本地混图器时,内部将自动正常移除所有输出; 

### getLocMixerState 

- 功能: 获取本地混图器状态 

- 返回值: CRVSDK_MIXER_STATE 

##### sdk_engine.getLocMixerState(mixerID) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|mixerID|string|混图器唯一标识|

### addLocMixerOutput 

- 功能: 开启本地录制、开启直播推流 

- 返回值: 错误码 

##### sdk_engine.addLocMixerOutput(mixerID, mixerOutput) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|mixerID|string|混图器唯一标识|
|mixerOutput|Array<CRLocMixerOutputObj>|本地输出对象|

补充说明: 

添加输出节点后 可以通过notifyLocMixerOutputInfo关注输出信息 

添加输出节点后,可以通过notifyLocMixerOutputInfo关注输出信息 

### rmLocMixerOutput 

- 功能: 停止本地录制、直播推流 

返回值: 无 

##### sdk_engine.rmLocMixerOutput(mixerID, nameOrUrls) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|mixerID|string|混图器唯一标识|
|nameOrUrls|string|要移除的输出的filename或liveUrl, 支持多值,以";"分隔;|

补充说明: 

移除输出时,内部将结束文件录制,或结束直播推流; 

### setPicResource 

- 功能: 配置图片资源(设置空的帧代表移除) 返回值: 无 

##### sdk_engine.setPicResource(picID, frm) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|picID|string|本地资源唯一标识|
|frm|CRVideoFrame|图像数据(请保证格式、和尺寸与摄像头一致)|

#### 补充说明: 

设置本地图像资源,可在本地混图器中引用,参见录制内容类型CRVSDK_MIXER_CONTENT_TYPE的 CRVSDK_MIXCONT_PIC; 

当资源不再需要时,应将此picID设置空的图像帧,以便sdk内部将释放相关资源; 离开房间时,设置的相关图片资源,将自动被移除; 

### notifyLocMixerStateChanged 

#### 功能: 本地混图器状态变化通知 

##### sdk_engine.on("notifyLocMixerStateChanged", (mixerID, state) => {}) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|mixerID|string|混图器唯一标识|
|state|CRVSDK_MIXER_STATE|混图器状态|

### notifyLocMixerOutputInfo 

功能: 本地录制文件、本地直播信息通知 

js 

sdk_engine.on("notifyLocMixerOutputInfo", (mixerID, nameOrUrl, outputInfo) => {}) 

|参数|类型|说明|
|---|---|---|
|mixerID|string|混图器唯一标识|
|nameOrUrl|string|录像名称、或直播url|
|outputInfo|CRLocMixerOutputInfoObj|通知内容|

### createCloudMixer 

- 功能: 创建云端混图器 

返回值: 云端混图器ID 

##### sdk_engine.createCloudMixer(cfg) 

js 

|参数|类型|说明|
|---|---|---|
|cfg|CRCloudMixerCfgObj|云端混图器配置|

补充说明: 

可以开启多个云端混图器,具体个数和企业购买的授权相关; 

开启云端混图器后,房间内所有人都将收到notifyCloudMixerStateChanged通知进入CRVSDK_MIXER_STARTING(启动 中状态); 

云端混图器部署有少量耗时,如果在部署过程遇到异常,将收到createCloudMixerFailed回调; 云端混图器启动完成并进入录制或推流状态时,将收到notifyCloudMixerStateChanged通知,进 入CRVSDK_MIXER_RUNNING(工作中状态); 

开启云端混图器在进入CRVSDK_MIXER_STARTING状态后,可以通过updateCloudMixerContent更新内容; 混图器如果在工作中遇到异常而停止时,将收到notifyCloudMixerStateChanged通知,进入CRVSDK_MIXER_NULL并携 带错误原因; 

### updateCloudMixerContent 

功能: 更新云端混图器 

返回值: 错误码 

##### sdk_engine.updateCloudMixerContent(mixerID, cfg) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|mixerID|string|混图器ID, 参见createCloudMixer|
|cfg|CRCloudMixerCfgObj|云端混图器配置|

#### 补充说明: 

更新混图器内容时,只能更新内容和布局,不能更改混图器规格、输出目标; 更新混图器内容时,房间内所有人都将收到notifyCloudMixerInfoChanged通知; 

### destroyCloudMixer 

功能: 销毁云端混图器 

返回值: 无 

js 

sdk_engine.destroyCloudMixer(mixerID) 

|参数|类型|说明|
|---|---|---|
|mixerID|string|混图器ID, 参见createCloudMixer|

补充说明: 

消毁云端混图器时,调用者将收到notifyCloudMixerStateChanged通知进入CRVSDK_MIXER_STOPPING状态,在停止完 成后,房间内所有人都将收到notifyCloudMixerStateChanged通知进入CRVSDK_MIXER_NULL状态; 

### getCloudMixerInfo 

- 功能: 获取云端混图器信息 

返回值: 云端混图器信息,参见CRCloudMixerInfo 

sdk_engine.getCloudMixerInfo(mixerID) 

js 

|参数|类型|说明|
|---|---|---|
|mixerID|string|混图器ID, 参见createCloudMixer|

### getAllCloudMixerInfo 

- 功能: 获取所有云端混图器 

返回值: Array<CRCloudMixerInfo>,云端混图器信息列表 

sdk_engine.getAllCloudMixerInfo() 

js 

### createCloudMixerFailed 

功能: 通知创建云端录制/推流失败 

##### sdk_engine.on("createCloudMixerFailed", (mixerID, sdkErr) => {}) 

js 

|参数|类型|说明|
|---|---|---|
|mixerID|string|混图器ID, 参见createCloudMixer|
|sdkErr|CRVSDK_ERR_DEF|错误码|

### notifyCloudMixerInfoChanged 

功能: 通知云端录制/推流信息变化 

##### sdk_engine.on("notifyCloudMixerInfoChanged", (mixerID) => {}) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|mixerID|string|混图器ID, 参见createCloudMixer|

补充说明: 

可调用:getCloudMixerInfo获取相关信息 

### notifyCloudMixerStateChanged 

#### 功能: 通知云端录制/推流状态变化 

|sdk_engine.on("notifyCloudMixerStateChanged", (mixerID,state,exParam,operUserID) => {}) js|
|---|

|参数|类型|说明|
|---|---|---|
|mixerID|string|混图器ID, 参见createCloudMixer|
|state|CRVSDK_MIXER_STATE|录制状态|
|exParam|string|json格式扩展参数,state状态及参数定义: MIXER_NULL:包含err(错误码), errDesc字段; MIXER_STARTING:包含jsonCfg字段|
|operUserID|string|操作者用户ID|

### notifyCloudMixerOutputInfoChanged 

#### 功能: 通知云端录制/推流输出信息变化 

##### sdk_engine.on("notifyCloudMixerOutputInfoChanged", (mixerID, outputInfo) => {}) 

|js|
|---|

|参数|类型|说明|
|---|---|---|
|mixerID|string|混图器ID, 参见createCloudMixer|
|outputInfo|CRCloudMixerOutputInfoObj|云端混图器输出信息|

# 视图组件 

更新时间: 2024/09/14 16:49:26 

## XComponent组件 

在HarmonyOS RTC SDK中,底层会在XComponent组件上绘制图形,它可以用于观看摄像头、屏幕共享、影音共享画面, 其中包括观看自己或他人的视图画面。用户只需将XComponent组件渲染到界面上并传入对应参数即可。 本文将介绍SDK层如何使用XComponent组件绘制视图。 

XComponent是HarmonyOS提供的组件,您可以跳转至HarmonyOS开发文档了解相关接口。 

## 创建视图容器 

示例代码: 

```arkts
import { util } from '@kit.ArkTS'; import { CRUserVideoID, CRVSDK_SCALE_MODE, CRVSDK_STREAM_VIEWTYPE, CRVSDK_VSTEAMLV_TYPE, CR_LIB_NAME } from '@cloudroom/hormony_rtcsdk'; @Component export struct VideoComponent { viewId: string = util.generateRandomUUID(); //视图id @Prop type: CRVSDK_STREAM_VIEWTYPE = CRVSDK_STREAM_VIEWTYPE.CRVSDK_VIEWTP_VIDEO; //视图类型 @Prop videoId?: CRUserVideoID = { userID: 'userID', videoID: -1 }; //用户视频id 
```

js 

@Prop videoLv?: CRVSDK_VSTEAMLV_TYPE = CRVSDK_VSTEAMLV_TYPE.CRVSDK_VSTP_LV0; //视频流等级 @Prop showMode?: CRVSDK_SCALE_MODE = CRVSDK_SCALE_MODE.CRVSDK_RENDERMD_FIT; //视频填充模式 

build() { XComponent({ id: this.viewId, type: XComponentType.SURFACE, libraryname: CR_LIB_NAME }) .onLoad((xComponentContext) => { //开始订阅视图,SDK会根据传入的参数在XComponent组件上绘制视图 sdk_engine.addCanvas({ viewId: this.viewId, type: this.type, videoId: this.videoId, videoLv: this.videoLv, showMode: this.showMode }); }) .onDestroy(() => { //取消订阅视图,SDK会停止在XComponent组件上绘制视图,并释放资源 sdk_engine.rmCanvas(this.viewId) }) } } 

sdk_engine是SDK的实例,由create接口创建,addCanvas和rmCanvas API无需在onLoad或onDestroy时机调用,当前封装 在组件内部按需订阅或取消订阅即可。 

XComponent: 

|参数|类型|说明|
|---|---|---|
|id|string|每个视图组件唯一,并且保持与addCanvas、rmCanvas传入的viewId一致|

|~~id~~|~~string~~|~~每个视图组件唯~~ ~~,并且保持与addCanvas、rmCanvas传入的viewId~~ ~~致~~|
|---|---|---|
|~~type~~ ~~参数~~|~~XComponentType~~ ~~类型~~|~~传入XComponentType.SURFACE~~ ~~说明~~|
|libraryname|string|参见HarmonyOS文档,这里必须使用SDK导出的值,CR_LIB_NAME|

#### 相关API请参考: 

addCanvas 

rmCanvas 

# 常量定义 

更新时间: 2024/09/14 16:49:26 

## CRVSDK_ERR_DEF 错误码 

|代码|数值|含义|
|---|---|---|
|CRVSDKERR_NOERR|0|没有错误|
|CRVSDKERR_VCAM_URLERR|-1|ipcam url不正确|
|CRVSDKERR_VCAM_ALREADYEXIST|-2|已存在|
|CRVSDKERR_VCAM_TOOMANY|-3|添加太多|
|CRVSDKERR_VCAM_INVALIDFMT|-4|不支持的格式|
|CRVSDKERR_VCAM_INVALIDMONITOR|-5|无效的屏幕id|
|CRVSDKERR_UNKNOWERR|1|未知错误|
|CRVSDKERR_OUTOF_MEM|2|内存不足|
|CRVSDKERR_INNER_ERR|3|sdk内部错误|
|CRVSDKERR_MISMATCHCLIENTVER|4|不支持的sdk版本|
|CRVSDKERR_PARAM_ERR|5|参数错误|
|CRVSDKERR_ERR_DATA|6|无效数据|
|CRVSDKERR_ANCTPSWD_ERR|7|帐号密码不正确|
|CRVSDKERR_SERVER_EXCEPTION|8|服务异常|
|CRVSDKERR_LOGINSTATE_ERROR|9|登录状态错误|
|CRVSDKERR_KICKOUT_BY_RELOGIN|10|帐号在别处被使用|
|CRVSDKERR_NOT_INIT|11|sdk未初始化|
|CRVSDKERR_NOT_LOGIN|12|还没有登录|
|CRVSDKERR_BASE64_COV_ERR|13|base64转换失败|
|CRVSDKERR_CUSTOMAUTH_NOINFO|14|启用了第三方鉴权,但没有携带鉴权信息|
|CRVSDKERR_CUSTOMAUTH_NOTSUPPORT|15|没有启用第三方鉴权,但携带了鉴权信息|
|CRVSDKERR_CUSTOMAUTH_EXCEPTION|16|访问第三方鉴权服务异常|
|CRVSDKERR_CUSTOMAUTH_FAILED|17|第三方鉴权不通过|
|CRVSDKERR_TOKEN_TIMEOUT|18|token已过期|
|CRVSDKERR_TOKEN_AUTHINFOERR|19|鉴权信息错误|
|CRVSDKERR_TOKEN_APPIDNOTEXIST|20|appid不存在|
|CRVSDKERR_TOKEN_AUTH_FAILED|21|鉴权失败|
|CRVSDKERR_TOKEN_NOTTOKENTYPE|22|非token鉴权方式|
|CRVSDKERR_API_NO_PERMISSION|23|没有api访问权限|
|CRVSDKERR_ACCOUNT_EXPIRED|24|账号已过期|

|CRVSDKERR_CLIENT_NO_PERMISSION 代码|25 数值|所有终端未授权 含义|
|---|---|---|
|CRVSDKERR_CLIENT_SIP_NO_PERMISSION|26|sip/h323终端未授权|
|CRVSDKERR_CLIENT_IPC_NO_PERMISSION|27|IPC终端未授权|
|CRVSDKERR_CLIENT_PLATFORM_NO_PERMISSION|28|当前使用的终端平台未授权|
|CRVSDKERR_CLIENT_PLATFORM_UNSPPORT|29|不支持当前使用的终端平台|
|CRVSDKERR_NETWORK_INITFAILED|200|网络初始化失败|
|CRVSDKERR_NO_SERVERINFO|201|没有服务器信息|
|CRVSDKERR_NOSERVER_RSP|202|服务器没有响应|
|CRVSDKERR_CREATE_CONN_FAILED|203|创建连接失败|
|CRVSDKERR_SOCKETEXCEPTION|204|socket异常|
|CRVSDKERR_SOCKETTIMEOUT|205|网络超时|
|CRVSDKERR_FORCEDCLOSECONNECTION|206|连接被关闭|
|CRVSDKERR_CONNECTIONLOST|207|连接丢失|
|CRVSDKERR_VOICEENG_INITFAILED|208|语音引擎初始化失败|
|CRVSDKERR_SSL_ERR|209|ssl通信错误|
|CRVSDKERR_RSPDAT_ERR|210|响应数据不正确|
|CRVSDKERR_DATAENCRYPT_ERR|211|数据加密失败|
|CRVSDKERR_DATADECRYPT_ERR|212|数据加密失败|
|CRVSDKERR_QUE_ID_INVALID|400|队列ID错误|
|CRVSDKERR_QUE_NOUSER|401|没有用户在排队|
|CRVSDKERR_QUE_USER_CANCELLED|402|排队用户已取消|
|CRVSDKERR_QUE_SERVICE_NOT_START|403|队列服务还未开启|
|CRVSDKERR_ALREADY_OTHERQUE|404|已在其它队列排队(客户只能在一个队列排队)|
|CRVSDKERR_INVALID_CALLID|600|无效的呼叫ID|
|CRVSDKERR_CALL_EXIST|601|已在呼叫中|
|CRVSDKERR_PEER_BUSY|602|对方忙|
|CRVSDKERR_PEER_OFFLINE|603|对方不在线|
|CRVSDKERR_PEER_NOANSWER|604|对方无应答|
|CRVSDKERR_PEER_NOT_FOUND|605|用户不存在|
|CRVSDKERR_PEER_REFUSE|606|对方拒接|
|CRVSDKERR_MEETNOTEXIST|800|房间不存在或已结束|
|CRVSDKERR_AUTHERROR|801|房间密码不正确|
|CRVSDKERR_MEMBEROVERFLOW|802|房间终端数量已满(购买的license不够)|
|CRVSDKERR_RESOURCEALLOCATEERROR|803|分配房间资源失败|
|CRVSDKERR_MEETROOMLOCKED|804|房间已加锁|

|CRVSDKERR_BALANCELESS 代码|805 数值|余额不足 含义|
|---|---|---|
|CRVSDKERR_SEVICE_NOTENABLED|806|业务权限未开启|
|CRVSDKERR_ALREADYINMEETING|807|不能再次进入房间|
|CRVSDKERR_MIC_NORIGHT|808|没有mic权限|
|CRVSDKERR_MIC_BEING_USED|809|mic已被使用|
|CRVSDKERR_MIC_UNKNOWERR|810|mic未知错误|
|CRVSDKERR_SPK_NORIGHT|811|没有扬声器权限|
|CRVSDKERR_SPK_BEING_USED|812|扬声器已被使用|
|CRVSDKERR_SPK_UNKNOWERR|813|扬声器未知错误|
|CRVSDKERR_PIC_ISNULL|814|图像为空|
|CRVSDKERR_DEV_NOTEXIST|815|设备不存在|
|CRVSDKERR_MIC_OPENTOOMUCH|816|开麦达到上限|
|CRVSDKERR_NOT_INMEETING|817|还没有进入房间|
|CRVSDKERR_REPEAT_FAIL|818|数据重复 或 功能重复开启失败|
|CRVSDKERR_MEMBEROVERFLOW_LIVE|819|直播观众用户数量已满(购买的直播观众用户不够)|
|CRVSDKERR_MEMBEROVERFLOW_SIP|820|sip用户数量已满(购买的sip用户数不够)|
|CRVSDKERR_MEMBEROVERFLOW_IPC|821|ipc用户数量已满(购买的ipc用户数不够)|
|CRVSDKERR_CATCH_SCREEN_ERR|900|抓屏失败|
|CRVSDKERR_RECORD_MAX|901|单次录制达到最大时长(8h)|
|CRVSDKERR_RECORD_NO_DISK|902|磁盘空间不够|
|CRVSDKERR_RECORD_SIZE_ERR|903|录制尺寸超出了允许值|
|CRVSDKERR_CFG_RESTRICTED|904|录制超出限制|
|CRVSDKERR_FILE_ERR|905|录制文件操作出错|
|CRVSDKERR_RECORDSTARTED|906|录制已开启|
|CRVSDKERR_NOMORE_MCU|907|录制服务器资源不足|
|CRVSDKERR_SVRRECORD_SPACE_FULL|908|云端录像空间已满|
|CRVSDKERR_SENDFAIL|1000|发送失败|
|CRVSDKERR_CONTAIN_SENSITIVEWORDS|1001|有敏感词语|
|CRVSDKERR_SENDCMD_LARGE|1100|发送信令数据过大|
|CRVSDKERR_SENDBUFFER_LARGE|1101|发送数据过大|
|CRVSDKERR_SENDDATA_TARGETINVALID|1102|目标用户不存在|
|CRVSDKERR_SENDFILE_FILEINERROR|1103|文件错误|
|CRVSDKERR_TRANSID_INVALID|1104|无效的发送id|
|CRVSDKERR_RECORDFILE_STATE_ERR|1200|状态错误不可上传/取消上传|
|CRVSDKERR_RECORDFILE_NOT_EXIST|1201|录制文件不存在|
|CRVSDKERR RECORDFILE UPLOAD FAILED|1202|上传失败 失败原因参考日志|

|~~CRVSDKERR_RECORDFILE_UPLOAD_FAILED~~ |~~1202~~ |~~上传失败,失败原因参考日志~~ |
|---|---|---|
|~~CRVSDKERR_RECORDFILE_DEL_FAILED~~ ~~代码~~|~~1203~~ ~~数值~~|~~移除本地文件失败~~ ~~含义~~|
|CRVSDKERR_FILE_NOT_EXIST|1400|文件不存在|
|CRVSDKERR_FILE_READ_ERR|1401|文件读失败|
|CRVSDKERR_FILE_WRITE_ERR|1402|文件写失败|
|CRVSDKERR_FILE_ALREADY_EXIST|1403|目标文件已存在|
|CRVSDKERR_FILE_OPERATOR_ERR|1404|文件操作失败|
|CRVSDKERR_FILE_SIZE_UNSUPPORT|1405|不支持的文件尺寸|
|CRVSDKERR_NETDISK_NOT_EXIST|1500|网盘不存在|
|CRVSDKERR_NETDISK_PERMISSIONDENIED|1501|没有网盘权限|
|CRVSDKERR_NETDISK_INVALIDFILENAME|1502|不合法文件名|
|CRVSDKERR_NETDISK_FILEALREADYEXISTS|1503|文件已存在|
|CRVSDKERR_NETDISK_FILEORDIRECTORYNOTEXISTS|1504|文件或目录不存在|
|CRVSDKERR_NETDISK_FILENOTTRANSFORM|1505|文件没有转换|
|CRVSDKERR_NETDISK_TRANSFORMFAILED|1506|文件转换失败|
|CRVSDKERR_NETDISK_NOSPACE|1507|空间不足|

## CRVSDK_LOG_LEVEL 日志等级 

|代码|数值|含义|
|---|---|---|
|CRVSDK_LOGLV_TRACE|0|详细调试信息(默认不打开)|
|CRVSDK_LOGLV_DEBUG|1|普通信息|
|CRVSDK_LOGLV_WARN|2|警告信息|
|CRVSDK_LOGLV_ERR|3|错误信息|

## CRVSDK_AUTHTYPE 登录鉴权方式 

|代码|数值|含义|
|---|---|---|
|CRVSDK_AUTHTP_TOKEN|0|token鉴权方式|
|CRVSDK_AUTHTP_SECRET|1|appID + appSecret鉴权方式|
|CRVSDK_WEBPROTOCOL web通 代码|讯协议类 数值|型 含义|
|CRVSDK_WEBPTC_DEFAULT|-1|内部默认类型为:CRVSDK_WEBPTC_HTTPS|
|CRVSDK_WEBPTC_HTTP|0|http|
|CRVSDK_WEBPTC_HTTPS|1|标准https|
|CRVSDK_WEBPTC_HTTPS_NOVERRIFY|2|不验证服务器SSL证书,支持自签证书|

## CRVSDK_USER_STATUS 用户登录状态 

|代码|数值|含义|
|---|---|---|
|CRVSDK_USERST_OFFLINE|0|sdk用户未登录|
|CRVSDK_USERST_ONLINE|1|sdk用户已登录|
|CRVSDK_USERST_BUSY|2|sdk用户已登录,且呼叫中或会议中|

## CRVSDK_MEETING_DROPPED_REASON 与房间断开原因 

|代码|数值|含义|
|---|---|---|
|CRVSDK_DROPPED_KICKOUT|1|被他人请出房间|
|CRVSDK_DROPPED_BALANCELESS|2|余额不足|

## CRVSDK_LEFT_QUEUE_REASON 排队客户离开队列原因 

|代码|数值|含义|
|---|---|---|
|CRVSDK_LQR_STOPQUEUE|0|用户停止排队|
|CRVSDK_LQR_INSERVICE|1|用户分配给了某座席|

## CRVSDK_CALLMORE_STATE 呼叫多方状态 

|代码|数值|含义|
|---|---|---|
|CRVSDK_CALLMORE_RING|0|被叫振铃中|
|CRVSDK_CALLMORE_ACCEPTED|1|被叫接听|
|CRVSDK_CALLMORE_REJECTED|2|被叫拒接|
|CRVSDK_CALLMORE_NOANSWER|3|被叫无应签|
|CRVSDK_CALLMORE_HUNGUP|4|被叫结束通话|

## CRVSDK_HTTPVERB_TYPE http请求类型 

|代码|数值|含义|
|---|---|---|
|CRVSDK_HTTPV_AUTO|0|自动, 当请求body有内容时用post,否则用get|
|CRVSDK_HTTPV_GET|1|http get|
|CRVSDK_HTTPV_POST|2|http post|

## CRVSDK_FILETRANSFER_STATE 文件传输状态 

|代码|数值|含义|
|---|---|---|
|CRVSDK_FILEST_NULL|0|未开始|
|CRVSDK_FILEST_QUEUE|1|排队中|

CRVSDK_FILEST_TRANSFERING 2 传输(上传 / 下载)中 代码 数值 含义 CRVSDK_FILEST_FINISHED 3 传输完成 

## CRVSDK_FILETRANSFER_RESULT 文件传输结果 

|代码|数值|含义|
|---|---|---|
|CRVSDK_FILERSLT_SUCCESS|0|成功|
|CRVSDK_FILERSLT_UNKNOWERR|1|内部错误|
|CRVSDK_FILERSLT_PARAMERR|2|参数错误|
|CRVSDK_FILERSLT_NETWORKFAIL|3|网络不通 / 地址不对|
|CRVSDK_FILERSLT_NETWORKTIMEOUT|4|超时失败|
|CRVSDK_FILERSLT_FILEOPERATIONFAIL|5|文件操作失败|
|CRVSDK_FILERSLT_PATHNOTSUPPROT|6|不支持的路径|
|CRVSDK_FILERSLT_FILETRANSFERING|7|文件正在传输|
|CRVSDK_FILERSLT_HTTPERR_BEGIN|1000|HTTP错误码启始(10404: 代表HTTP 404)|
|CRVSDK_FILERSLT_HTTPERR_END|1999|HTTP错误码结束|

## CRVSDK_VDEV_TYPE 视频设备类型 

|代码|数值|含义|
|---|---|---|
|CRVSDK_VDEVTP_UNKNOW|0|未知类型|
|CRVSDK_VDEVTP_SYSDV|1|系统物理设备|
|CRVSDK_VDEVTP_IP|2|网络摄像头|
|CRVSDK_VDEVTP_CUSTOM|3|自定义摄像头|
|CRVSDK_VDEVTP_SCREEN|4|屏幕摄像头|

## CRVSDK_ASTATUS 麦状态 

|代码|数值|含义|
|---|---|---|
|CRVSDK_AST_UNKNOWN|0|未知,正在从系统获取|
|CRVSDK_AST_NULL|1|没有麦克风设备|
|CRVSDK_AST_CLOSE|2|麦克风关闭|
|CRVSDK_AST_OPEN|3|麦克风打开|
|CRVSDK_AST_OPENING|4|开麦申请中|
|CRVSDK_AST_OPENING2|5|帮助他人开麦中|

## CRVSDK_VSTATUS 视频状态 

|代码|数值 含义|
|---|---|

|CRVSDK_VST_UNKNOWN 代码|0 数值|未知,正在从系统获取 含义|
|---|---|---|
|CRVSDK_VST_NULL|1|无摄像头|
|CRVSDK_VST_CLOSE|2|摄像头关闭|
|CRVSDK_VST_OPEN|3|摄像头打开|
|CRVSDK_VST_OPENING|4|打开摄像头申请中|

## CRVSDK_AUDIO_FORMAT 音频格式 

|代码|数值|含义|
|---|---|---|
|CRVSDK_AFMT_INVALID|-1|无效格式|
|CRVSDK_AFMT_PCM16BIT|0|pcm 16bit|

## CRVSDK_VSTEAMLV_TYPE 视频大小流类型 

|代码|数值|含义|
|---|---|---|
|CRVSDK_VSTP_LV0|0|视频标准流|
|CRVSDK_VSTP_LV1|1|视频第二档流|

## CRVSDK_VIDEO_FORMAT 图像格式 

|代码|数值|含义|
|---|---|---|
|CRVSDK_VFMT_INVALID|-1|无效格式|
|CRVSDK_VFMT_YUV420P|0|yuv420p, 3个平面数据|
|CRVSDK_VFMT_ARGB32|1|rgb32, 1个平面数据,0xAARRGGBB|
|CRVSDK_VFMT_RGBA32|2|rgb32, 1个平面数据,0xRRGGBBAA|
|CRVSDK_VFMT_H264|3|h264裸数据,1个平面数据|
|CRVSDK_VFMT_OESTEXTURE|4|保留值|
|CRVSDK_VFMT_NV21|5|nv21, 2个平面数据|
|CRVSDK_VFMT_NV12|6|nv12, 2个平面数据|
|CRVSDK_VFMT_0RGB32|7|rgb32, 1个平面数据,0xXXRRGGBB(忽略alpha通道)|
|CRVSDK_VFMT_RGB032|8|rgb32, 1个平面数据,0xRRGGBBXX(忽略alpha通道)|
|CRVSDK_VFMT_BGR032|9|rgb32, 1个平面数据,0xBBGGRRXX(忽略alpha通道)|
|CRVSDK_VFMT_0BGR32|10|rgb32, 1个平面数据,0xXXBBGGRR(忽略alpha通道)|
|CRVSDK_VFMT_BGRA32|11|1个平面数据,0xBBGGRRAA|
|CRVSDK_VFMT_ABGR32|12|1个平面数据,0xAABBGGRR|
|CRVSDK_VFMT_D3D11|13|windows ID3D11Texture2D纹理,第一个平面指针为ID3D11Texture2D指针|

CRVSDK_COLORSPACE 图像颜色空间 

|代码 代码|数 值 数 值|含义 含义|
|---|---|---|
|CRVSDK_COLSPC_UNSPECIFI ED|0|未指定(可按CRVSDK_COLSPC_BT601处理)|
|CRVSDK_COLSPC_BT709|1|also ITU-R BT1361 / IEC 61966-2-4 xvYCC709 / SMPTE RP177 Annex B|
|CRVSDK_COLSPC_BT601|5|also ITU-R BT601-6 625 / ITU-R BT1358 625 / ITU-R BT1700 625 PAL & S ECAM|

## CRVSDK_COLORRANGE 图像颜色范围 

|代码|数值|含义|
|---|---|---|
|CRVSDK_COLRG_UNSPECIFIED|0|未指定(可按CRVSDK_COLRG_MPEG处理)|
|CRVSDK_COLRG_MPEG|1|the range of 16-240 for 8 bits|
|CRVSDK_COLRG_JPEG|2|the range of 1-255 for 8 bits|

## CRVSDK_MOUSEMSG_TYPE 远程控制鼠标消息类型 

|代码|数值|含义|
|---|---|---|
|CRVSDK_MOUSEMSG_MOVE|0|鼠标移动|
|CRVSDK_MOUSEMSG_DOWN|1|鼠标按下|
|CRVSDK_MOUSEMSG_UP|2|鼠标松开|
|CRVSDK_MOUSEMSG_DBCLICK|3|鼠标双击|

## CRVSDK_MOUSEKEY_TYPE 远程控制鼠标键类型 

|代码|数值|含义|
|---|---|---|
|CRVSDK_MOUSEKEY_NULL|0|无按键|
|CRVSDK_MOUSEKEY_L|1|鼠标左键|
|CRVSDK_MOUSEKEY_M|2|鼠标中键|
|CRVSDK_MOUSEKEY_R|3|鼠标右键|
|CRVSDK_MOUSEKEY_WHEEL|4|鼠标滚轮|
|CRVSDK_MOUSEKEY_X|5|鼠标侧键|

## CRVSDK_KEYMSG_TYPE 远程控制键盘消息类型 

|代码|数值|含义|
|---|---|---|
|CRVSDK_KEYMSG_DWON|0|按下|
|CRVSDK_KEYMSG_UP|1|弹起|

## CRVSDK_MEDIA_STATE 影音共享状态 

|代码|数值|含义|
|---|---|---|
|CRVSDK_MEDIAST_PLAYING|0|播放中|
|CRVSDK_MEDIAST_PAUSED|1|暂停中|
|CRVSDK_MEDIAST_STOPPED|2|未播放|

## CRVSDK_MEDIA_STOPREASON 影音停止原因 

|代码|数值|含义|
|---|---|---|
|CRVSDK_MEDIASR_CLOSE|0|被关闭|
|CRVSDK_MEDIASR_FINI|1|播放完成|
|CRVSDK_MEDIASR_FILEOPEN_ERR|2|打开失败|
|CRVSDK_MEDIASR_FORMAT_ERR|3|格式错误|
|CRVSDK_MEDIASR_UNSUPPORTCODEC|4|不支持的编码|
|CRVSDK_MEDIASR_EXCEPTION|5|不支持的编码|

## CRVSDK_SCALE_MODE 图像显示模式 

|代码|数值|含义|
|---|---|---|
|CRVSDK_RENDERMD_FIT|0|等比缩放到在窗口大小并完整显示,空区域填黑|
|CRVSDK_RENDERMD_HIDDEN|1|等比缩放到完整覆盖窗口,超出区域图像被裁剪掉|
|CRVSDK_RENDERMD_FILL|2|缩放图像充满窗口(图像可能变形)|

## CRVSDK_MIXER_CONTENT_TYPE 混图器内容类型 

|代码|数值|含义|
|---|---|---|
|CRVSDK_MIXCONT_VIDEO|0|摄像头|
|CRVSDK_MIXCONT_PIC|1|图片|
|CRVSDK_MIXCONT_SCREEN|2|本地屏幕|
|CRVSDK_MIXCONT_MEDIA|3|影音共享|
|CRVSDK_MIXCONT_DEPRECATED_4|4|(已废弃)|
|CRVSDK_MIXCONT_SCREEN_SHARED|5|共享中的屏幕|
|CRVSDK_MIXCONT_WBOARD|6|白板|
|CRVSDK_MIXCONT_DEPRECATED7|7|(已废弃)|
|CRVSDK_MIXCONT_DEPRECATED8|8|(已废弃)|
|CRVSDK_MIXCONT_DEPRECATED9|9|(已废弃)|
|CRVSDK_MIXCONT_TEXT|10|文本、时戳|

## CRVSDK_MIXER_STATE 录制、直播状态 

|代码|数值|含义|
|---|---|---|
|CRVSDK_MIXER_NULL|0|已停止|
|CRVSDK_MIXER_STARTING|1|启动中|
|CRVSDK_MIXER_RUNNING|2|工作中|
|CRVSDK_MIXER_PAUSED|3|暂停中(仅本地录制、直播支持)|
|CRVSDK_MIXER_STOPPING|4|停止中|

## CRVSDK_MIXER_OUTPUT_TYPE 录制、直播输出类型 

|代码|数值|含义|
|---|---|---|
|CRVSDK_MIXER_OUTPUT_FILE|0|录制文件|
|CRVSDK_MIXER_OUTPUT_LIVE|1|直播推流|

## CRVSDK_LOCMIXER_OUTPUT_STATE 本地混图输出状态 

|代码|数值|含义|
|---|---|---|
|CRVSDK_LOCMO_STARTED|0|录制/直播开始|
|CRVSDK_LOCMO_RUNNING|1|录制/直播中|
|CRVSDK_LOCMO_STOPPED|2|录制/直播结束|
|CRVSDK_LOCMO_FAIL|3|录制/直播失败|

## CRVSDK_CLOUDMIXER_OUTPUT_STATE 云端混图输出状态 

|代码|数值|含义|
|---|---|---|
|CRVSDK_CLOUDMO_STARTED|0|录制/直播开始|
|CRVSDK_CLOUDMO_RUNNING|1|录制/直播中|
|CRVSDK_CLOUDMO_STOPPED|2|录制/直播结束|
|CRVSDK_CLOUDMO_FAIL|3|录制/直播失败|
|CRVSDK_CLOUDMO_UPLOADING|4|录像文件上传中|
|CRVSDK_CLOUDMO_UPLOADED|5|录像文件上传完成|
|CRVSDK_CLOUDMO_UPLOADFAIL|6|录像文件上传失败|

## CRVSDK_VOICECHANGE_TYPE 变声类型 

|代码|数值|含义|
|---|---|---|
|CRVSDK_VOICETYPE_NULL|0|原声|
|CRVSDK_VOICETYPE_NEUTRALFEMALE|1|中性女声, 适合女用|
|CRVSDK_VOICETYPE_NEUTRALMALE|2|中性男声, 适合男用|
|CRVSDK_VOICETYPE_SWEETFEMALE|3|甜美女声, 适合女用|

|CRVSDK_VOICETYPE_DEEPMALE 代码|4 数值|低沉男声,适合男用 含义|
|---|---|---|
|CRVSDK_VOICETYPE_BOY|5|娃娃音, 适合女用|
|CRVSDK_VOICETYPE_GIRL|6|娃娃音, 适合男用|

## 视频流默认码率定义 

#### 其它分辨率,将按面积进行对应档位换算处理 

|分辨率|默认码率|可设置的最大码率|
|---|---|---|
|80*48|48kbps|96kbps|
|112*64|53kbps|106kbps|
|160*96|75kbps|150kbps|
|224*128|100kbps|200kbps|
|288*160|123kbps|246kbps|
|352*192|160kbps|320kbps|
|448*256|230kbps|440kbps|
|512*288|260kbps|520kbps|
|576*320|300kbps|600kbps|
|640*360|350kbps|700kbps|
|704*400|420kbps|840kbps|
|848*480|500kbps|1mbps|
|1024*576|650kbps|1300kbps|
|1280*720|1mbps|2mbps|
|1920*1080|2mbps|4mbps|
|2560*1440|3mbps|4.5mbps|
|3840*2160|5mbps|8mbps|

## CRVSDK_STREAM_VIEWTYPE 视图类型 

|代码|数值|含义|
|---|---|---|
|CRVSDK_VIEWTP_VIDEO|0|摄像头显示View|
|CRVSDK_VIEWTP_SCREEN|1|屏幕共享显示View|
|CRVSDK_VIEWTP_MEDIA|2|影音共享显示View|

## CRVSDK_CODEC_ID 编码类型 

|代码|数值|含义|
|---|---|---|
|CRVSDK_CODECID_NONE|0|未定义|
|CRVSDK_CODECID_H264|27|H.264/AVC|

代码 数值 含义 CRVSDK_CODECID_VP8 139 VP8 CRVSDK_CODECID_H265 173 H.265/HEVC 

## CRVSDK_ASUBSCRIB_MODE 音频订阅模式 

|代码|数值|含义|
|---|---|---|
|CRVSDK_ASM_MIXED|0|房间的混音流,此模式特点: 1. 只有一个语音流,带宽占用小; 2. 终端cpu开销小|
|CRVSDK_ASM_SEPARATE|1|每个的独立流, 此模式优点: 1. 可以控制订阅指定人员的流;|

## CRVSDK_ASUBSCRIB_LISTTYPE 音频订阅名单类型 

|代码|数值|含义|
|---|---|---|
|CRVSDK_ASLT_INCLUDE|0|白名单|
|CRVSDK_ASLT_EXCLUDE|1|黑名单|

## CRVSDK_SCREENCAPTURESOURCE_TYPE 屏幕共享采集源类型 

|代码|数值|含义|
|---|---|---|
|CRVSDK_CAPSOURCE_NULL|0|空类型|
|CRVSDK_CAPSOURCE_SCREEN|1|屏幕|
|CRVSDK_CAPSOURCE_WINDOW|2|窗口|

## CRVSDK_AUDIO_CHLAYOUT 声道布局 

|代码|数值|含义|
|---|---|---|
|CRVSDK_ACHL_MONO|1|单声道|
|CRVSDK_ACHL_STEREO|3|左右双声道|

# 数据结构体定义 

更新时间: 2024/09/14 16:49:27 

## CRNetworkProxy 

json 

{"type":1,"addr":"192.168.0.2","port":8080} 

|参数|类型|说明|
|---|---|---|
|type|number|网络代理类型(0:无代理, 1:http代理)|
|addr|string|代理服务器地址|
|port|number|代理服务器端口|
|name|string|可选参数,代理帐号|
|pswd|string|可选参数,代理密码|

## CRSDKCreateParams sdk创建扩展参数 

|参数|类型|说明|
|---|---|---|
|Timeout|number|网络通信超时时间,单位是毫秒,取值范围:10000-120000, 缺省值:60000(60秒)|

## CRLoginDat 登录数据 

|参数|类型|说明|
|---|---|---|
|sdkAuth Type|CRVSDK_AUTH TYPE|鉴权类型,请参见SDK登录鉴权方案|
|appID|string|_sdkAuthType为CRVSDK_AUTHTP_SECRET时为必选参数; App ID的相关说明,请参见关键词|
|md5_ap pSecret|string|appSecret的md5值,_sdkAuthType为CRVSDK_AUTHTP_SECRET为必选参数|
|token|string|登录鉴权token,_sdkAuthType为CRVSDK_AUTHTP_TOKEN时为必选参数|
|webProt ocol|CRVSDK_WEB PROTOCOL|访问web服务协义类型|
|serverAd dr|string|服务器地址,_webProtocol不同取值,请带正确的网络端口|
|userID|string|用户ID,长度不能大于128。业务方自由填写,保证同一appID下具有唯一性|
|nickNam e|string|用户昵称,长度不能大于128|
|userAuth Code|string|默认填空。只有开启第三方认证才需要填写。(开启第三方认证时,云屋SDK服务器将 连接提前配好的业务方服务器进行实时验证。)|

CRUserStatus 用户在线状态信息 

CRUserStatus 用户在线状态信息 

|参数|类型|说明|
|---|---|---|
|userID|string|用户ID, 请参见关键词|
|userStatus|CRVSDK_USER_STATUS|客户端状态|
|DNDType|number|用户自定义免打扰状态,0:未开启免打扰|

## CRQueInfo 队列信息 

|参数|类型|说明|
|---|---|---|
|queID|number|队列ID|
|name|string|队列名称|
|desc|string|队列描述信息|
|prio|number|队列优先级(为优先级最高)|

## CRQueUserInfo 排队用户信息 

|参数|类型|说明|
|---|---|---|
|queID|number|队列ID|
|usrID|string|排队的用户ID|
|name|string|用户的昵称|
|usrExtDat|string|用户排队时的扩展数据|
|queuingTime|number|排队的时长(单位:秒)|

## CRQueStatus 队列状态 

|参数|类型|说明|
|---|---|---|
|queID|number|队列ID|
|agentNum|number|坐席数|
|waitNum|number|等待人数|
|srvNum|number|服务中人数|

## CRQueuingInfo 我的排队信息 

|参数|类型|说明|
|---|---|---|
|queID|number|排的队列ID(<0:代表我没有排队)|
|position|number|当前位置(0为队首,即将被服务)|
|queuingTime|number|我排队的时长(单位:秒)|

## CRTransReqInfo 文件传输请求信息 

|参数|类型|说明|
|---|---|---|
|filePat hNam e|string|本地路径文件名|
|dstUrl|string|目标URL|
|bUploa dType|boolean|传输类型(上传:true、下载:false)|
|extPar ams|string|扩展信息,如:http头部扩展,json格式,{"header1":"value1", "header2":"value2"}|
|transfe rCfg|string|传输控制参数,josn格式,例如{"decodeCREEFile":0} 详细如下: (1)decodeCREEFile:此参数仅http上传有效。0:上传原始文件,1:上传解密的文件(云屋录 制加密文件) (2)extParamsTransfType:此参数仅http上传有效。当取值缺省或为0时:extParams在heade r中传送。取值为1时:extParams在multipart/form-data中传送|

## CRFileTransInfo 文件传输状态信息 

|参数|类型|说明|
|---|---|---|
|filePathName|string|本地路径文件名|
|dstUrl|string|目标URL|
|bUploadType|boolean|传输类型(上传:true、下载:false)|
|extParams|string|参见CRTransReqInfo对应描述|
|transferCfg|string|参见CRTransReqInfo对应描述|
|state|CRVSDK_FILETRANSFER_STATE|传输状态|
|fileSize|number|文件大小|
|finishedSize|number|已传输大小|

## CRMeetingMember 房间成员信息 

|参数|类型|说明|
|---|---|---|
|userId|string|用户ID|
|nickName|string|姓名|
|audioStatus|CRVSDK_ASTATUS|音频状态|
|videoStatus|CRVSDK_VSTATUS|视频状态|

## CRAudioDevInfo 音频设备信息 

|参数|类型|说明|
|---|---|---|
|id|string|设备id|
|name|string|设备名称|

## CRVideoDevInfo 视频设备信息 

|参数|类型|说明|
|---|---|---|
|videoID|number|设备编号(程序重启后可能变化)|
|devName|string|设备名称|
|devMaxSz|CRSize|摄像头支持的最大分辨率|
|devGuid|string|设备guid, 仅获取本地设备有效|
|bDisabled|boolean|设备是否被禁用, 仅获取本地设备有效|
|devType|CRVSDK_VDEV_TYPE|设备类型|

## CRUserVideoID 用户视频ID 

|参数|类型|说明|
|---|---|---|
|userID|string|用户id|
|videoID|number|设备id|

## CRAudioCfg 音频配置 

|参数|类型|说明|
|---|---|---|
|micGuid|string|麦克风设备(空代表系统默认设备)|
|spkGuid|string|扬声器设备(空代表系统默认设备)|
|agc|boolean|是否启用声音增益|
|ans|boolean|是否启用降噪|
|aec|boolean|是否启用回声消除|

## CRVideoCfg 视频配置 

|参数|类型|说明|
|---|---|---|
|size|string|分辨率:"w*h"|
|fps|number|视频帧率(1~30)|
|maxbps|number|可选参数默认值,视频码率 单位为bps,如100kbps填值:100000,1mkbps填值1000000|
|min_qp|number|可选参数(默认值22),最佳质量(18~51, 越小质量越好)|
|max_qp|number|可选参数(默认值32),最低质量(18~51, 越小质量越好) , sdk在网络不好时,智能调低质量, 以便降低码率来提升流畅性|

## CRAudioFrame 音频帧数据 

|参数|类型|说明|
|---|---|---|
|format|CRVSDK AUDIO FORMAT|音频格式|

|~~format~~ ~~sampleRate~~ ~~参数~~|~~CRVSDK_AUDIO_FORMAT~~ ~~number~~ ~~类型~~|~~音频格式~~ ~~采样率~~ ~~说明~~|
|---|---|---|
|chLayout|CRVSDK_AUDIO_CHLAYOUT|声道布局|
|timestamp|number|时间戳(ms)|
|data|Uint8Array|音频数据(可被修改)|
|datLen|number|音频数据长度|

## CRAudioFrame2 音频帧数据 

|参数|类型|说明|
|---|---|---|
|format|CRVSDK_AUDIO_FORMAT|音频格式|
|sampleRate|number|采样率|
|chLayout|CRVSDK_AUDIO_CHLAYOUT|声道布局|
|timestamp|number|时间戳(ms)|
|data|Uint8Array|音频数据|

## CRVideoFrame 视频帧数据 

|参数|类型|说明|
|---|---|---|
|format|CRVSDK_VIDEO_FORMAT|图像格式|
|width|number|视频宽度|
|height|number|视频高度|
|pts|number|时间戳(ms)|
|data|Uint8Array|音频数据|

## CRScreenCaptureSourceInfo 屏幕共享采集源信息 

|参数|类型|说明|
|---|---|---|
|type|CRVSDK_SCREENCAPTURESO URCE_TYPE|类型|
|sourceId|number|采集源ID,对于窗口,表示窗口 ID(Window ID);对于屏幕,表示 屏幕 ID(Display ID)|
|sourceTitle|string|采集源标题,适用窗口类型|
|sourceNam e|string|采集源名称|
|thumbImag e|CRVideoFrame|采集源缩略图|
|iconImage|CRVideoFrame|采集源图标,适用窗口类型|
|primaryMon itor|boolean|是否为主屏,适用屏幕类型|

~~minimizeWi~~ 参数 boolean类型 窗口是否已最小化,适用Windows平台说明 ndow 

## CRScreenShareInfo 屏幕共享状态信息 

|参数|类型|说明|
|---|---|---|
|state|number|共享状态, 0:未共享,1:共享中|
|sharerUserID|string|共享者用户ID|
|ctrlerUserID|string|当前控制者用户ID|

## CRMediaInfo 影音共享状态信息 

|参数|类型|说明|
|---|---|---|
|state|CRVSDK_MEDIA_STATE|共享状态|
|userID|string|共享者用户ID|
|mediaName|string|共享的文件名|

## CRVStreamInfo 图像流信息 

|参数|类型|说明|
|---|---|---|
|w|short|图像宽|
|h|short|图像高|
|fps|number|帧率|
|bps|number|码率,单位:bit/秒|
|codecID|CRVSDK_CODEC_ID|编码类型|

## CRNetStateInfo 网络状态信息 

|参数|类型|说明|
|---|---|---|
|lv|number|网络评价0~10(10分为最佳)|
|delay|number|网络延时,单位ms|
|aSndLost|number|语音发送丢包率|
|aRcvLost|number|语音接收丢包率|
|vSndLost|number|视频发送丢包率|
|vRcvLost|number|视频接收丢包率|

## CRVideoAttributesObj 摄像头私有属性 

//只开大流,清晰度为720p 

{ "size":"1280*720", "fps":15, "maxbps":1000000, "quality2":{"size":"228*160", "maxbps":120000} } 

json 

{ "size":"1280*720", "fps":15, "maxbps":1000000 } //开启大小流,大流720p, 小流160p 

|参数|类型|说明|
|---|---|---|
|disabled|number|可选参数,取值0:不禁用此设备(默认值),1:禁用此设备;|
|effects|CRVideoEffectsObj|可选参数,视频效果配置,未配置时采用全局配置setVideoEffects|
|fps|number|可选参数,参见CRVideoCfg的描述,未配置时采用全局配置setVideoCfg|
|size|string|可选参数,参见CRVideoCfg的描述,未配置时采用全局配置setVideoCfg|
|maxbps|number|可选参数,参见CRVideoCfg的描述,未配置时采用全局配置setVideoCfg|
|qp_min|number|可选参数,参见CRVideoCfg的描述,未配置时采用全局配置setVideoCfg|
|qp_max|number|可选参数,参见CRVideoCfg的描述,未配置时采用全局配置setVideoCfg|
|quality2|object|可选参数,第二档质量配置,支持的属性有:size, maxbps, qp_min, qp_max; quality2未配置或配为空,代表关闭第二流; 配置quality2,代表开启第二流,将带来较大的cpu开销; 通过setVideo2可以选择观看的标准流或第二流;|

## CRVideoEffectsObj 视频效果参数 

{"denoise":1,"mirror":1} 

json

|参数|类型|说明|
|---|---|---|
|denoise|number|视频降噪, 取值:0/1, 默值为1|
|mirror|number|视频镜像(左右翻转),取值:0/1, 默认为0。|
|upsideDown|number|视频上下翻转,取值:0/1, 默认为0|
|deinterlace|number|视频反交错,取值:0/1, 默认为0 (除非视频采集设备为隔行扫描设备,否则不要开启)|
|degree|number|旋转角度,<0代表自动,旋转取值:0、90、180、270、360, 默认为自动模式|

## CRLocMixerCfgObj 本地混图器规格配置 

{ "width":640, "height":360, "frameRate":8, "bitRate":500000, "defaultQP":28, "gop":120 } 

json

|参 数|类型|说明||
|---|---|---|---|
|wid th|number|图像宽度|(要求16的倍数)|
|hei ght|number|图像高度|(要求8的倍数)|
|fra||||

|me Rat ~~e~~ 参 数|number 类型|图像帧率,取值范围:1-30(值越大,cpu要求更高,录像推荐15帧,直播推存25帧) 说明|
|---|---|---|
|bit Rat|number|最高码率(例如1m:1000000),当图像变化小时,平均码率会低于此值|
|e|||
|def ault QP|number|目标质量,缺省值:25。取值范围:0~51,0表示完全无损, 51表示质量非常差,推荐高质量取值 18,中质量25, 低质量34|
|gop|number|I帧周期(I帧周期越大码率越小,但直播延时会越大); 文件录制建议15秒一个I帧,取值:frameR ate x 15(frameRate的15倍); 直播建议4秒一个I帧,取值: frameRate x 4(frameRate的4倍);|

## CRMixerContentObj 混图器内容 

{ "type": 0, "left": 5, "top": 10, "width": 633, "height": 356, "keepAspectRatio": 1, "param": {"camid":"usr1.1"} } 

json

|参数|类型|说明|
|---|---|---|
|left|number|在混图画面中的区域(水平位置)|
|top|number|在混图画面中的区域(垂直位置)|
|width|number|在混图画面中的区域宽|
|height|number|在混图画面中的区域高|
|type|number|CRVSDK_MIXER_CONTENT_TYPE,请见后面type描述;|
|keepAspectRatio|number|内容保持原始比例,0不保持,1保持|
|param|obj|如:{"camid":"usrxxx.1"}。请见后面param支持的参数;|

#### type描述: 

当type=CRVSDK_MIXCONT_VIDEO时,表示混图的是摄像头,param必须包含camid; 

- 当type=CRVSDK_MIXCONT_PIC时,表示混图的是指定的图片,param必须包含resourceid;(仅用于本地混图) 当type=CRVSDK_MIXCONT_SCREEN时,表示混图的是本地屏幕,param可以增加附加参数 screenid/pid/area/window;(仅用于本地混图) 

- 当type=CRVSDK_MIXCONT_MEDIA时,表示混图的是影音共享,不用附加任何参数; 

- 当type=CRVSDK_MIXCONT_SCREEN_SHARED时,表示混图的是共享的屏幕,不用附加任何参数; 

- 当type=CRVSDK_MIXCONT_WBOARD时,表示混图的是白板,不用附加任何参数;(仅用于云端混图,本地混图 应该生成图像用MIXVTP_PIC) 

- 当type=CRVSDK_MIXCONT_TEXT时,表示混图的是文本,width和height将被忽略,元素大小由文本信息自动确 定。 param必须包含text,可选color,background,font-size,text-margin; 

#### param 支持的参数如下: 

camid:用户id.摄像头id, 如:"testuser.1" 

- resourceid:具有唯一属性的字符串id,通过setPicResource将图片存储到sdk内供混图模块使用 screenid:屏幕序号,-1表示主屏 

- pid:进程号 

- area:抓屏区域:"x,y,w,h" 

- text:文本内容,支持时间戳参数"%timestamp%",格式为:YYYY-MM-DD HH:MM:SS 

- color:文本颜色,格式:#RRGGBB[AA], 默认#FFFFFF 

- background:背景色,格式:#RRGGBB[AA], 默认#0000007D font-size:字体大小,默认18 

- text-margin:边距,默认5 

## CRLocMixerOutputObj 本地混图器输出配置 

输出到文件配置:{"type":0,"filename":"D:/1.mp4"} 直播推流配置:{"type":1,"liveUrl":"rtmp://xxx"} 

json

#### 当输出到文件时,参数如下: 

|参数|类 型|说明|
|---|---|---|
|type|num ber|录制文件CRVSDK_MIXER_OUTPUT_FILE|
|filenam e|strin g|录像路径文件名(如:d:/1.mp4),支持的文件格式为mp4/ts/flv/avi,其中flv和ts两种格式在程 序异常结束时产生的录制文件仍可用。|
|encrypt Type|num ber|可选参数,录像文件是否加密,0:不加密(默认值),1:加密;|

#### 当输出推流时,参数如下: 

|参数|类型|说明|
|---|---|---|
|type|number|直播推流CRVSDK_MIXER_OUTPUT_LIVE|
|liveUrl|string|直播推流地址,支持rtmp/rtsp;|
|errRetryTimes|number|可选参数,直播推流异常时,重试次数,默认值0|

## CRLocMixerOutputInfoObj 本地混图器输出信息 

json 

{ "state":2, "duration":100,"fileSize":10000 } 

|参数|类型|说明|
|---|---|---|
|state|CRVSDK_LOCMIXER_OUTPUT_STAT E|状态 state为CRVSDK_LOCMO_RUNNING时:duration, fileSize参数有效 ; state为CRVSDK_LOCMO_STOPPED时:duration, fileSize参数有效 |
|||; state为CRVSDK_LOCMO_FAIL时:errCode参数有效;|
|duratio|||

|~~duratio~~ n 参数|number 类型|录像文件时长,单位:毫秒 说明|
|---|---|---|
|fileSize|number|录像文件大小,单位:字节|
|errCode|CRVSDK_ERR_DEF|错误码|

## CRCloudMixerCfgObj 云端混图器配置 

//为房间中所有人录制独立的声音文件,独立的默认摄像头视频文件 { "mode": 1, "audioFileCfg": { "svrFileNameSuffix": ".mp3", "svrPath": "/xxx", "subscribeAudios": ["_cr_all_"] }, "videoFileCfg": { "aStreamType": 1, "svrFileNameSuffix": ".mp4", "svrPath": "/xxx", "subscribeVideos": ["_cr_allDefCam_"] } } //录制一个2分屏左右布局图像+房间声音的mp4文件 { "mode": 0, "videoFileCfg": { "svrPathName": "/2021-09-24/2021-09-24_13-47-41_Win32_73542046.mp4", "vWidth": 1280, "vHeight": 720, "vFps": 15, "layoutConfig": [ { "type": 0, "top": 180, "left": 0, "width": 640, "height": 360, "keepAspectRatio": 1, "param": {"camid": "1.-1"} }, { "type": 0, "top": 180, "left": 640, "width": 640, "height": 360, "keepAspectRatio": 1, "param": {"camid": "2.-1"} } ] } } 

json

|参数|类型|说明|是否 必传|
|---|---|---|---|
|mode|number|录制模式,取值范围: 0-合流模式:将声音录制到一个声音文件、或将声音图像录制成一个视 频文件;|是|

|参数|类型|~~频文件;~~ 1-单流模式:将涉及到的声音流、图像流存到各自独立的文件中; 说明|是否 ~~必传~~|
|---|---|---|---|
|~~audioFile~~ Cfg|~~CRCloudMixerAudi~~ oFileCfg|~~生成音频文件配置,生成规则:进入房间并开启麦克风开始生成文件,~~ 离开房间结束生成文件|否 |
|videoFile Cfg|CRCloudMixerVide oFileCfg|生成视频文件配置,生成规则:进入房间并开启摄像头开始生成文件, 离开房间结束生成文件|否|
|storageC onfig|CRCloudStorageCo nfig|云存储配置,不配置时将存储在云屋服务器上|否|

## CRCloudMixerAudioFileCfg 云端录制语音文件配置 

#### 单流模式参数: 

|参数|类型|说明|是否必传|
|---|---|---|---|
|svrPath|string|服务器存储路径,默认为空|否|
|svrFileNameSuffix|string|文件名后缀,支持:“.mp3”、“.wav” 文件命名规则:昵称_房间号_开始时间.后缀|是|
|subscribeAudios|string[]|指定生成哪些人的音频文件; 取值:["_cr_all_"]或["userId1","userId2"]; _cr_all_代表生成所有人;|是|

#### 合流模式参数: 

|参数|类 型|说明|是否 必传|
|---|---|---|---|
|svrPathNa me|stri ng|带服务器存储路径的文件名,文件格式支持“mp3”、“wav”,示例:/xxx/xxx/xxx.mp3|是|
|aChannelT ype|num ber|音频通道类型,取值范围:0-单声道,1-左右双声道,默认为0|否|
|||音频通道内容。||
|aChannelC ontent|stri ng[]|左右声道模式时:必须传入两个用户ID,如:["UserID1", "UserID2"],第一个人的为 左声道,第二个人为右声道)|否|
|||单声道模式时:可选参数(默认为空),空代表所有人声音,要指定人员声音时传入 :["UserID1","UserID2", "UserID3"]||

## CRCloudMixerVideoFileCfg 云端录制视频文件配置 

#### 单流模式参数: 

|参数|类型|说明|是否必 传|
|---|---|---|---|
|svrPath|string|服务器存储路径,默认为空|否|
|svrFileNameSuf fix|string|文件名后缀,当前只支持:”.mp4” 文件命名规则:昵称_cam摄像头编号_房间号_开始时间.后缀|是|
|||指定生成哪些人的摄像头对应的视频文件; 取值:[" cr all "]或[" cr allDefCam "]或["userId1 camId" "userId2 camId||

|subscribeVideo s 参数|string[ ] 类型|~~取值:[ _cr_all_ ]或[ _cr_allDefCam_ ]或[ userId1.camId , userId2.camId~~ ", ...]; _cr_all_代表所有人所有摄像头,_cr_allDefCam_代表生成所有人的默认摄像 说明|是 是否必 传|
|---|---|---|---|
|||头||
|aStreamType|numb er|视频文件内音频内容,取值:0-自己声音,1-所有人声音,默认0|否|

#### 合流模式参数: 

|参数|类型|说明|是否 必传|
|---|---|---|---|
|svrPathN ame|string|带路径的文件名,文件格式支持:mp4、flv、ts、avi、rtmp://、rtsp://,可选 一个或多个,以“;”分隔; 示例:”/xxx/xxx.mp4;rtmp://xxx1;rtmp://xxx2;”|是|
|aChannel Type|number|音频通道类型,取值:0-单声道,1-左右双声道,默认为0|否|
|||音频通道内容。||
|aChannel Content|string[]|左右声道模式时:必须传入两个用户ID,如:["UserID1", "UserID2"],第一个 人的为左声道,第二个人为右声道) 单声道模式时:可选参数(默认为空),空代表所有人声音,要指定人员声音 时传入:["UserID1","UserID2", "UserID3"]|否|
|vWidth|number|视频宽度|是|
|vHeight|number|视频高度|是|
|vFps|number|视频帧率,取值0-30, 默认值12|否|
|vBps|number|视频码率,取值参见视频流默认码率定义默认会根据视频尺寸生成码率|否|
|vQP|number|视频质量,取值0~51(0表示完全无损, 51表示质量非常差),推荐高质量取值18 ,中质量25,低质量34, 默认值19|否|
|layoutCon fig|CRMixerCon tentObj[]|布局内容列表|是|

## CRCloudStorageConfig 云端录制存储配置 

|参数|类型|说明|是否必传|
|---|---|---|---|
|vendor|number|第三方云存储平台: 1-阿里云|是|
|region|string|第三方云存储指定的地区信息|是|
|bucket|string|第三方云存储的 bucket|是|
|accessKey|string|第三方云存储的 access key|是|
|secretKey|string|第三方云存储的 secret key|是|
|endPoint|string|第三方云存储的完整路径,当设置该参数后,region参数不生效|否|

## CRCloudMixerInfoList 云端混图器信息列表 

CRCloudMixerInfo列表,参见CRCloudMixerInfo 

## CRCloudMixerInfo 云端混图器信息 

|参数|类型|说明|
|---|---|---|
|ID|string|混图器ID|
|owner|string|创建者用户ID|
|cfg|string|录制配置,json格式串,参见CRCloudMixerCfgObj|
|state|number|录制状态,参见CRVSDK_MIXER_STATE|

## CRCloudMixerOutputInfoObj 云端混图器输出信息 

|参数|类型|说明|
|---|---|---|
|id|string|混图器ID|
|state|number|状态,参见CRVSDK_CLOUDMIXER_OUTPUT_STATE state为CRVSDK_CLOUDMO_STOPPED时:startTime, duration, fileSize参数有 效; state为CRVSDK_CLOUDMO_FAIL时:errCode, errDesc参数有效; state为CRVSDK_CLOUDMO_UPLOADING时:progress参数有效; state为CRVSDK_CLOUDMO_UPLOADFAIL时:errCode, errDesc参数有效;|
|svrFilePathNam e|string|录像路径文件名|
|startTime|number|创建时间(从1970年1月1日00:00:00起的毫秒数)|
|duration|number|录像时长(ms)|
|fileSize|number|文件大小(Byte)|
|errCode|CRVSDK_ERR_DE F|错误码|
|errDesc|string|错误描述|
|progress|number|上传进度(0~100.0)|

## CRMeetingAttrOptions 操作房间属性选项 

|参数|类型|说明|
|---|---|---|
|notifyAll|number|0(默认值):不通知,1:通知房间所有人员|

## CRAttrObjs 房间属性集 

{ "KeyXX": { "value": "11111", "lastModifyUserID": "111", "lastModifyTs": 11111 }, "KeyYY": { "value": "22222", "lastModifyUserID": "222", 

"lastModifyTs": 22222 

json 

lastModifyTs : 22222 } } 

|参数|类型|说明|
|---|---|---|
|User defined Key|string|自定义的属性Key|
|value|string|属性值|
|lastModifyUserID|string|最后修改的用户ID|
|lastModifyTs|number|最后修改的时间点,1970-1-1 00:00:00以来的秒数|

## CRUsrAttrObjs 用户属性集 

{ "userid1": { "KeyXX": { "value": "11111", "lastModifyUserID": "111", "lastModifyTs": 11111 }, "KeyYY": { "value": "22222", "lastModifyUserID": "222", "lastModifyTs": 22222 } }, "userid2": { "KeyXX": { "value": "11111", "lastModifyUserID": "111", "lastModifyTs": 11111 }, "KeyYY": { "value": "22222", "lastModifyUserID": "222", "lastModifyTs": 22222 } } } 

json 

|参数|类型|说明|
|---|---|---|
|UserID|string|用户ID|
|User defined Key|string|自定义的属性Key|
|value|string|属性值|
|lastModifyUserID|string|最后修改的用户ID|
|lastModifyTs|number|最后修改的时间点,1970-1-1 00:00:00以来的秒数|

## CRScreenMarkData 屏幕共享标注数据 

|参数|类型|说明|
|---|---|---|
|markid|string|标注ID,唯一标识一个标注|
|userid|string|标注所属用户ID|

|~~userid~~ ~~penType~~ ~~参数~~|~~string~~ ~~number~~ ~~类型~~|~~标注所属用户ID~~ ~~画笔类型,1:铅笔, 2:水笔。默认:1~~ ~~说明~~|
|---|---|---|
|penWidth|number|画笔宽度,默认:2|
|color|string|颜色,格式为:#RRGGBB|
|points|array|点数据,每个点是unumber32类型,其中高16位是x,低16位是y|

## CRSize 尺寸 

|参数|类型|说明|
|---|---|---|
|width|number|宽度|
|height|number|高度|

## CRCanvas 视图控件 

|参数|类型|说明|
|---|---|---|
|viewId|string|视图id|
|type|CRVSDK_STREAM_VIEWTYPE|视图类型|
|showMode|CRVSDK_SCALE_MODE|显示模式|
|videoId|CRUserVideoID|用户视频id|
|videoLv|CRVSDK_VSTEAMLV_TYPE|视频流等级|
