# 菊风视频能力平台SDK开发集成指南

一、系统概述

1.1系统介绍

1.2系统特性

二、关于菊风软件

2.1技术支持

2.2版权申明

三、快速集成SDK

3.1前提条件

3.2操作步骤

步骤一:获取 Juphoon_Rtc_SDK_for_Harmony

步骤二:导入SDK

步骤三:添加权限

关于蓝牙权限

步骤四:混淆规则

步骤五:编译运行

四、实现视频通话

4.1前提条件

4.2快速跑通Sample

4.3功能实现

4.3.1初始化

4.3.2登录

4.3.3加入通话

4.3.4邀请

4.3.5取消邀请

4.3.6收到邀请

4.3.6.1接收邀请

4.3.6.2拒绝邀请

4.3.7视频渲染

1

4.3.8新成员加入

4.3.9成员更新

4.3.10成员离开

4.3.11结束离开

4.3.12登出

4.3.13登录登出状态改变通知

4.3.14销毁SDK

五、通话管理

5.1设置用户角色

5.2获取统计信息

5.3获取通话唯一标识

5.4获取业务流水号

六、消息通道

6.1通话内消息

6.2在线消息

七、音频管理

7.1发送本地音频流

7.2音频输出

7.3自定义音频输入

7.4本地音频播放

7.5音频异常回调

7.6音频数据回调

7.6.1输入音频数据回调

7.6.2输出音频数据回调

八、视频管理

8.1发送本地视频流

8.2订阅/取消订阅视频流

8.3SVC 设置说明

8.4设置本地视频宽高比

8.5视频截图

8.6视频采集回调

8.7视频异常回调

2

九、设备管理

9.1音频设备管理

9.1.1音频参数设置

9.1.2扬声器的开启关闭

9.1.3获取麦克风音量级别

9.1.4获取扬声器音量级别

9.1.5获取当前噪声强度

9.1.6获取当前信噪比强度

9.1.7设置是否开启自动增益控制

9.1.8设置开启自适应回音消除

9.2视频设备管理

9.2.1获取摄像头列表

9.2.2指定摄像头/指定摄像头采集角度

9.2.3摄像头采集属性

9.2.4开启/关闭摄像头

9.2.5切换摄像头

十、体验提升

10.1通话中质量检测

10.1.1网络质量检测

10.1.2音频质量检测

10.1.3剩余可用内存检测

10.2文件上传

十一、屏幕共享

11.1开启/关闭屏幕共享

11.2共享视频采集

11.3暂停/恢复屏幕共享

11.4订阅/取消订阅屏幕共享的视频流

11.5渲染共享画面

十二、音视频录制

12.1本地录制

12.2本地录制(不需要建立通信)

12.3远程录制

3

12.3.1开启/关闭远程录制

12.3.2远程录制异常回调

12.3.3水印

12.3.3.1注意事项

12.3.3.2添加、修改或删除水印

12.3.4自定义布局

12.3.5更新远程录制自定义布局

12.3.6更新远程录制水印信息

十三、加密传输

13.1国密加密

13.2Token校验

十四、视频多流

# 开发指导手册(Harmony)

## 宁波菊风系统软件有限公司

## 2025年1月

版权所有©宁波菊风系统软件有限公司 2025。保留一切权利。

4

|  |  |  |  |
|---|---|---|---|
| 版本 | 作者 | 日期 | 说明 |
| v2401.0 | 杨象坤 | 2024.4 | 鸿蒙SDK音频通话集成文档初版 ● |
| v2501.0 | 王乐凯 | 2025.1 | ● 更新 api 接口链接 |

# 一、系统概述

非常感谢您使用菊风系统软件的产品,我们将为您提供最好的服务。本手册可能包含技术上不准确

的地方或排版错误。本手册的内容将做定期的更新,恕不另行通知;更新的内容将会在本手册的新版本

中加入。我们随时会改进或更新本手册中描述的产品或程序。

# 1.1 系统介绍

菊风视频能力平台在实际的项目中定位为音视频能力的提供方,除此之外还包装了一些和音视频通

讯强相关的业务。以银行项目为例可分为视频客服业务、视频房间业务、视频双录业务、AI 双录业务、

一对一通话及消息业务等。上述业务需要客户渠道类系统或者客户业务类系统集成我们 Jphoon RTC

SDK 或者插件才能形成完整的业务,在整个完整的业务中我们提供基础的音视频通讯能力和一些对应业

务上所需的特色能力。如视频客服业务的智能排队服务,视频房间业务的增强会控服务等。

菊风视频能力平台提供标准 Juphoon RTC SDK 用于给客户渠道类系统和客户业务类系统集成并

通过 Juphoon RTC SDK 接入到视频能力平台进行音视频通讯。

菊风为开发者提供 JRTC SDK 功能开发包,涵盖了音视频引擎终端、服务器和业务模块,支持实

现智能排队、全景录像、多人音视频等业务功能。

Juphoon RTC SDK 支持  iOS、Android、鸿蒙Next、Windows、UOS、Kylin、微信小程序、

H5  等操作系统平台。对于银行的其他公共平台或其他第三方平台,视频能力平台可提供标准第三方接

口和其他平台进行对接。实现和银行环境的整体融入。

# 1.2 系统特性

菊风视频能力平台(Juphoon Video Capability Platform)提供高可用、高品质、超低延时的实时

音视频通信服务,为远程银行、视频双录、视频房间、AI 双录、VoLTE 视频通话等泛金融场景化方案提

供平台支撑。具有业界领先的实时音视频编码技术,以及抗啸叫降噪、ARS 码率自适应、SPo 视频甜

点、智能路由等技术,应对网络质量非均衡性、网络异构性、多类型终端的接入的挑战,保证高音质、

高画质。Juphoon RTC for Harmony SDK 专为鸿蒙Next 平台设计,适用于鸿蒙手机等华为公

司移动终端设备。整个平台由宁波菊风系统软件有限公司独立研发,具有自主知识产权。

5

# 二、关于菊风软件

宁波菊风系统软件有限公司(简称“菊风”,英文简称“Juphoon”)成立于2005年,现有员工200

余人,注册资金2050万元,总部位于宁波,在北京、广州、长沙设有区域中心(研发、销售和交付),

在郑州和杭州设有交付中心,是一家提供实时音视频通信和RCS融合通信解决方案的供应商。宁波总部

研发中心主要负责客户端SDK 和 APP、音视频引擎、服务器等产品的研发;云平台和服务器系统的运

维、网管等支撑系统研发,现中心成员有180名。

菊风经过15年+音视频底层技术积累,为众多行业合作伙伴提供了超优音视频通信服务。凭借卓越的

产品以及优质的服务,迄今为止,已有数十亿终端用户以及众多企业用户通过菊风云实现了音视频场景

化沟通,涉及社交、教育、医疗、智能硬件、金融、电商等多个行业领域,为其提供了有针对性的行业

化解决方案。

菊风为开发者提供的优而小的 SDK 极简接入,快速助其实现实时音视频通信能力。基于客户不同需

求,菊风云提供灵活的部署模式——公有云,专有云,私有云,海外云以及混合云。对主流系统平台全

覆盖,支持 iOS、Android、鸿蒙Next、Windows、UOS、Kylin、微信小程序、H5 等。支持各移动设

备(电脑、手机、平板)、VTM机等多终端设备的适配。

# 2.1 技术支持

在您使用 Juphoon RTC SDK 的过程中,遇到任何困难,请与我们联系,我们将热忱为您提供帮助。

您可以通过如下方式与我们取得联系:

公司官网:https://rtc.juphoon.com

产品咨询:sales@juphoon.com

加急热线:13056832331

咨询电话:400-800-8708 / 0574-87901227

售前工程师微信二维码:

6

# 2.2 版权申明

“Juphoon RTC for Harmony SDK”是由宁波菊风系统软件有限公司开发,拥有自主知识产权(软

著正式编号2020SR0369466号)的系统平台,宁波菊风系统软件有限公司拥有与本产品所用技术相关

的知识产权。这些知识产权包括但不限于一项或多项发明专利或者正在进行申请的

专利(ZL202010288867.7 、ZL201911393580.4 )。

本产品发行所依照的许可协议限制其使用、复制分发和反编译。未经宁波菊风系统软件有限公司事

先书面授权,不得以任何形式或借助任何手段复制本产品的任何部分。随本SDK 一同发布的Demo 演示

程序源代码版权归宁波菊风系统软件有限公司。Juphoon 是宁波菊风系统软件有限公司的商标。

# 三、快速集成 SDK

本文为您介绍了Harmony 端集成 SDK 的操作步骤,帮助您快速集成 SDK 并实现多方视频通话的基

本功能。

# 3.1 前提条件

●

HarmonyOS 5.0.0(API 12) Release 及以上

●

DevEco Studio 5.0.0 Release(5.0.3.906)及以上

●

Command Line Tools for HarmonyOS 5.0.0 Release(5.0.3.906)及以上

# 3.2 操作步骤

7

## 步骤一:获取 Juphoon_Rtc_SDK_for_Harmony

您可在 Juphoon 的产品官方网站下载到最新版的Juphoon RTC SDK,

访问下载地址,示例如下:

注:首次访问,请先注册后登录。

Juphoon_Rtc_SDK_for_Harmony_版本号_CallCenter包里面提供了所有支持开发语言 demo 程

序的编译程序、开发指南、demo 程序源码和 SDK 文件,其解压之后的目录结构如下所示:

## 步骤二:导入 SDK

1.拷贝 SDK 文件夹内的 JRTCSDK.har 到您工程目录中的 sdk 目录下,并打开工程,如下图所示

2.为能连接到我们的 so 库,在您工程 oh-package.json5 文件中确保增加以下配置,如图:

## 步骤三:添加权限

根据工程需要,打开 src/main/module.json5 文件,配置权限。

8

JSON

| 权限 | 介绍 |
|---|---|
| ohos.permission.INTERNET | 网络权限,登录与通话必需 |
| ohos.permission.GET NETWORK INFO _ _ | 访问网络状态权限,登录与通话必需 |

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

9

|  |  |
|---|---|
| ohos.permission.GET WIFI INFO _ _ | 访问wifi状态权限,登录与通话必需 |
| ohos.permission.MODIFY AUDIO SETTINGS _ _ | 修改音量权限,音频控制需要 |
| ohos.permission.MICROPHONE | 麦克风权限,音频通话必需,需要动 态申请 |
| ohos.permission.CAMERA | 相机权限,视频通话必需,需要动态 申请 |
| ohos.permission.USE BLUETOOTH _ | 蓝牙通话切换需要 |

您在 module.json5 中进行权限配置时,请确保您能够获得打开摄像头、音视频录制等权限

关于蓝牙权限

## 步骤四:混淆规则

## 步骤五:编译运行

以上步骤进行完后,编译工程,如果没有报错,恭喜您,您已经成功配置 SDK,可以进行下一步了。

# 四、实现视频通话

# 4.1 前提条件

请确认您已完成以下操作:

○

已获取 App Key。

AppKey 作为同个环境的分域依据,同一个域的终端才能实现互通,AppKey 由 Juphoon 视频

平台提供。

○

集成 SDK(Harmony)。

# 4.2 快速跑通 Sample

1.在 Juphoon RTC SDK 文档中心,选择 Harmony 平台下载体验JCCSample示例项目。

10

访问下载地址,示例如下:

2.下载完成后,打开安装包,解压 JCCSample,然后安装 JCCSample.apk

3.打开应用程序后,设置正确的 appkey,环境地址以及账号。

a.首先点击初始化按钮,成功后,登入按钮变为可点击;

b.确认账号输入无误之后,点击登入按钮,按钮字样变为登出,即登录成功;

c.点击多方通话(MpCall)按钮,即可进入多方体验相关的功能;

d.进入网络电话页面后,输入房间号,如果有房间密码输入密码,点击加入,即可进入房间。

# 4.3 功能实现

11

JRTCSDK

Server

JRTCSDK

用户1

用户2

1初始化JRTCSDK(JRCCClient,JRTCMediaDevice,JRTCRoom)

|  |  |  | 2 登录login |  |  |  |  |
|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  |
|  |  |  |  | 4 登录结果 |  |  |  |
|  |  |  |  |  |  |  |  |
|  |  |  |  |  |  | 6 登录login |  |
|  |  |  |  |  |  |  |  |
|  |  |  |  |  | 8 登录结果 |  |  |
|  |  |  |  |  |  |  |  |
| 登录成 |  |  | 功 9 onLogin(true, reason) | 1 3 加入房间 | 1 7 加入房间 | 1 0 onLogin(true, reason) 1 5 加入房间join("roomId", JRTCRoomJoinParam) |  |
| 加入 alt 离 加 |  |  |  |  |  |  |  |
|  |  |  | 1 1 加入房间join("roomId", JRTCRoomJoinParam) |  |  |  |  |
|  |  |  | 1 2 房间状态改变onRoomStateChanged(STATE_JOINING, STATE_IDLE, JRTCRoom) |  |  |  |  |
|  |  |  |  |  |  |  |  |
|  |  |  |  | 1 4 加入房间结果 |  |  |  |
|  |  |  |  |  |  |  |  |
|  |  |  |  |  |  | 1 6 房间状态改变onRoomStateChanged(STATE_JOINING, STATE_IDLE, JRTCRoom) |  |
|  |  |  |  |  | 1 8 加入房间结果 |  |  |
|  |  |  |  |  |  |  |  |
|  | 加入 |  | 房间成功 1 9 房间状态改变onRoomStateChanged(STATE_JOINED, STATE_JOINING, JRTCRoom) |  |  | 2 1 房间状态改变onRoomStateChanged(STATE_JOINED, STATE_JOINING, JRTCRoom) 2 2 加入房间结果onJoin(true, reason, "roomId", JRTCRoom) |  |
|  | alt 离 |  |  |  |  |  |  |
|  |  |  | 2 0 加入房间结果onJoin(true, reason, "roomId", JRTCRoom) |  |  |  |  |
|  |  |  | 2 3 成员加入房间onParticipantJoin(participant, JRTCRoom) |  |  |  |  |
|  |  |  |  |  |  |  |  |
|  |  | alt | [业务操作] 2 4 业务操作房间属性变化onRoomPropertyChanged(propChangeParam, JRTCRoom) |  |  |  |  |
|  |  |  |  |  |  |  |  |
|  |  |  | 2 5 onParticipantUpdate(participant, changeParam, JRTCRoom) |  |  |  |  |
|  |  |  |  |  |  |  |  |
|  |  | 离 | 开房间 3 0 onParticipantLeft(participant, reason, JRTCRoom) | 2 9 成员离开房间 | 2 7 离开房间 | 2 6 离开房间leave() |  |
|  |  |  |  |  |  |  |  |
|  |  |  |  |  |  | 3 1 离开房间onLeave(reason, roomId, JRTCRoom) |  |
|  |  |  |  |  | 2 8 离开房间结果 |  |  |
|  |  |  |  |  |  |  |  |
|  |  | 加 | 入房间失败 3 2 房间状态改变onRoomStateChanged(STATE_IDLE, STATE_JOINING, JRTCRoom) |  |  |  |  |
|  |  |  |  |  |  |  |  |
|  |  |  | 3 3 加入房间结果onJoin(false, reason, null, JRTCRoom) |  |  |  |  |
|  |  |  | 3 4 房间状态改变onRoomStateChanged(STATE_IDLE, STATE_JOINING, JRTCRoom) |  |  |  |  |
|  |  |  |  |  |  |  |  |
|  |  | 登 | 录失败 3 5 onLogin(false, reason) |  |  | 3 6 onLogin(false, reason) |  |
|  |  |  |  |  |  |  |  |

用户1

用户2

JRTCSDK

Server

JRTCSDK

## 4.3.1 初始化

注:我们所有的方法都建议在主线程调用,否则可能会出现异常无法正常使用,回调接口也都在主线程

上报。

在使用业务接口前,需对 Juphoon RTC SDK 进行初始化操作。

| 类 | 模块 | 描述 |
|---|---|---|
| JRTCClient | 登录模块 | 负责视频平台的登录登出,只有登 录到视频平台才可以使用视频相关 的业务 |

12

|  |  |  |
|---|---|---|
| JRTCMediaDevice | 媒体模块 | 负责本地的媒体设备操作,视频画 面渲染等功能 |
| JRTCCall | 通话模块 | 可以通过流水号加入通话,邀请其 他成员加入通话 |
| JRTCRecord | 录制模块 | 实现本地音视频录制(不需要建立 通话),本地分片录制等功能 |

ArkTS

```
class JRTCManager implements JRTCClientCallback, JRTCCallCallback, JRTCMed
iaDeviceCallback {
  private client: JRTCClient;
  private mediaDevice: JRTCMediaDevice;
  private call: JRTCCall;
  private record: JRTCRecord;
  public init(context: Context) {
   let param: JRTCClientInitParam = new JRTCClientInitParam();
    param.appName = "appName"         // 设置应用名称
    param.SDKInfoDir = "SDKInfoDir"   // 设置SDK信息存储目录
    param.appKey = "appKey"           // 设置AppKey
    param.server = "server"           //设置接入服务器地址
    param.logConsole = true           // 设置是否控制台日志输出,默认true
    param.logLocalFile = true         // 获取是否是否本地文件日志输出,默认true
    param.looseTimeoutControl = true  // 设置是否开启 RPC 抗信令丢包控制(70%的
```

上下行信令丢包),默认false

```
    this.client = JRTCClient.create(context.getApplicationContext(), thi
s, initParam);
    this.mediaDevice = JRTCMediaDevice.create(this.mClient, this, undefine
d);
    this.call = JRTCCall.create(this.client, this.mediaDevice, this);
    this.record = JRTCRecord.create(this.client,this.mediaDevice, this);
    // 设置基本参数
    this.client.setServer("server"); // 设置接入服务器地址
    this.client.setAppKey("appKey"); // 设置AppKey
    this.client.setDisplayName("displayName"); // 设置显示名称
    this.client.setAppName("appName"); // 设置应用名称
  }
}
```

13

根据需求实现对应JRTCCallCallback的接口即可。

## 4.3.2 登录

SDK 初始化之后,即可进行登录的集成,登录接口调用流程如下所示:

用户

JRTCSDK

login()

登录成功

onLogin(true, reason)

登录失败

onLogin(false, reason)

用户

JRTCSDK

登录到 Juphoon 视频平台主要调用的是JRTCClient的登录接口login。

ArkTS

```
/**
```

* 登录 Juphoon RTC 平台,只有登录成功后才能进行平台上的各种业务

```
* <p>
* 登录结果通过 {@link JRTCClientCallback.onLogin onLogin} 回调通知
*
* @param { string } userId 用户ID
* @param { string } password 密码,不能为空
* @param { JRTCClientLoginParam? } clientLoginParam 登录参数,一般不需要设置,
```

如需设置请询问客服,传 undefined 则按默认值

```
* @return { boolean } 接口调用结果
```

*  - true:接口调用成功

*  - false:接口调用异常

* @warning 目前只支持免鉴权模式,服务器不校验账号密码,免鉴权模式下当账号不存在时会自动

去创建该账号

```
* @warning 用户名为英文数字和'+' '-' '_' '.',长度不要超过64字符,'-' '_' '.'不能
```

作为第一个字符

```
*/
public abstract login(userId: string, password: string, clientLoginPara
m?: JRTCClientLoginParam): boolean;
```

JRTCClientLoginParam属性介绍

| 属性 | 描述 |
|---|---|
|  |  |

14

|  |  |
|---|---|
| accountEntry | 设置账户分录参数,如果支持国密S3则需要设置 certificate 参 数,否则可以不设置 certificate 参数 |
| certificate | 设置 S3 国密证书 Base64 编码内容 |
| acceptExpiredCertificate | 设置是否允许过期证书校验通过 |
| token | 设置token |
| tokenType | 设置 token 校验类型 |
| deviceId | 设置设备id |
| logFilter | 设置日志过滤标签(用于日志管理平台过滤终端日志使用) |
| terminalType | 设置终端登录类型,支持多终端登录,默认所有终端相同会导致互 踢 |
| autoCreateAccount | 是否自动创建账号(免鉴权使用),默认true |
| accelerateKey | 设置加速云KEY |
| accelerateKeySecret | 设置加速云KEY密钥 |
| optimizeDataRouter | 设置是否开启数据路由优化,默认true |

登录的结果将会通过JRTCClientCallback的接口上报:

ArkTS

```
/**
```

* 登录结果回调

```
*
* @param { boolean } result 登录结果
*                           - true:表示登录成功,
*                           - false:表示登录失败
* @param { JRTCReasonCode } reason 登录失败原因,当 result 为 false 时该值有效
*/
onLogin?: (result: boolean, reason: JRTCReasonCode) => void;
```

示例代码:

15

ArkTS

```
// 创建登录配置参数
const loginParam: JRTCClientLoginParam = new JRTCClientLoginParam();
// 登录
client.login("juphoon", "123456", loginParam);
public onLogin(result: boolean, reason: number): void {
  if (result) {
    // 登录成功
  } else {
    // 登录失败,具体原因查询 reason 错误码
  }
}
```

## 4.3.3 加入通话

ArkTS

```
/**
```

* 加入通话

* @note 需要已经登录

```
* @note 该接口支持加入通话并且邀请其他用户加入,通过 {@link JRTCCallJoinParam#set
InviteCalleeUserId(string)} setInviteCalleeUserId}
* 和 {@link JRTCCallJoinParam#setInviteCalleeUserType(int)} setInviteCalle
```

eUserType} 设置需要邀请的用户ID和用户类型

```
*
* <p>
```

* 该方法让用户加入通话,在同一个通话内的用户可以互相视频语音。

* 如果用户已在通话中,必须退出当前通话,即处于空闲状态,才能进入其他通话,否则将直接返

回 false,且不会收到回调通知。

```
*
```

* @param serialId 业务流水号,保证唯一,必选

```
* @param param    加入通话参数,传 undefined 则使用默认参数
* @see JRTCCallJoinParam
* @return 接口调用结果
* - true: 接口调用成功,会收到 {@link JRTCCallCallback#onJoin onJoin} 回调
* - false: 接口调用异常
*/
public abstract join(serialId: string, param: JRTCCallJoinParam | undefine
d): boolean;
```

JRTCCallJoinParam参数介绍

16

|  |  |
|---|---|
| inviteCalleeUserId | 被邀请者用户ID。如果不为空,会在自身加入通话同时邀请 用户加入 |
| inviteCalleeUserType | 被邀请者用户类型,默认APP用户。当被邀请者用户ID不为 空时,该值有效 |
| routeId | 线路ID。当被邀请用户ID不为空,并且被邀请者用户类型是 SIP用户的时候有效 |
| extraInfo | 随路参数。当被邀请用户ID不为空时,该值有效 |

示例代码:

ArkTS

```
let param:JRTCCallJoinParam = new JRTCCallJoinParam()
...
param.video = true;
...
call.join("serialId",param))
onJoin: (result: boolean, reasonCode: JRTCReasonCode) => {
  if (result) {
     //登录成功
  }
}
```

## 4.3.4 邀请

17

ArkTS

```
/**
```

* 邀请其他成员加入通话

* @note 需要已经加入通话

```
*
* @param calleeUserId  被邀请者用户ID
* @param param         邀请参数
* @return
* - 操作id: 接口调用成功,对应 {@link JRTCCallCallback#onInviteResult onInvit
eResult} 回调的 operatorId 参数
```

* - -1: 接口调用异常,不会收到回调

```
*/
public abstract invite(calleeUserId: string, param: JRTCCallExtraParam | u
ndefined): number;
```

JRTCCallExtraParam参数介绍

| video | 是否视频通话 |
|---|---|
| serialId | 业务流水号 |
| callerUserId | 邀请人用户ID |
| callerDisplayName | 邀请人昵称 |
| calleeUserId | 被邀请者用户ID |
| calleeDisplayName | 被邀请者昵称 |
| calleeUserType | 被邀请者用户类型 |
| routeId | 线路ID |
| extraInfo | 随路参数 |

如果类型是JRTCCallUserType.App,被邀请人会收到onInviteReceived回调

18

ArkTS

```
/**
```

* 收到邀请通知

```
*
* @param param 其他参数
* @see JRTCCallExtraParam
*/
onInviteReceived?: (param: JRTCCallExtraParam) => void;
```

示例代码

ArkTS

```
const param: JRTCCallExtraParam = new JRTCCallExtraParam();
param.callerUserId = "userId";
param.video = true;
param.calleeUserType = JRTCCallUserType.APP;
param.routeId = "routeId";
call.invite("userId", param);
```

## 4.3.5 取消邀请

在被邀请人未回应邀请前,可以取消当前的邀请。

ArkTS

```
/**
```

 * 取消邀请

```
 *
 * @return
 * - 操作id: 接口调用成功,对应 {@link JRTCCallCallback#onCancelInviteResult(i
nt, boolean, string)} onCancelInviteResult} 回调的 operatorId 参数
```

 * - -1: 接口调用异常,不会收到回调

```
 */
public abstract cancelInvite(): number;
```

取消结果回调

19

ArkTS

```
/**
```

 * 取消邀请结果回调

```
 * @param operatorId 操作id,对应 {@link JRTCCall#cancelInvite() invite} 的返
```

回值

```
 * @param result 加入通话是否成功
 *               - true: 成功
 *               - false: 失败
 * @param reason  取消邀请失败原因
 */
onCancelInviteResult?: (operatorId: number, result: boolean, reason: strin
g) => void;
```

示例代码

ArkTS

```
call.cancelInvite()
1
```

同时对方将收到取消邀请通知

ArkTS

```
/**
```

 * 对方取消邀请通知

```
 *
 * @param param 其他参数
 * @see JRTCCallExtraParam
 */
onInviteCanceled?: (param: JRTCCallExtraParam) => void;
```

## 4.3.6 收到邀请

被邀请人收到邀请处理,可以接收或者拒绝邀请

示例代码:

20

ArkTS

```
/**
```

* 收到邀请通知

```
*
* @param param 其他参数
* @see JRTCCallExtraParam
*/
onInviteReceived?: (param: JRTCCallExtraParam) => void;
```

4.3.6.1 接收邀请

ArkTS

```
/**
```

* 接受邀请

```
*
* @param video  是否需要视频
*
* @return
* - 操作id: 接口调用成功,对应 {@link JRTCCallCallback#onAcceptInviteResult(i
nt, boolean, string)} onAcceptInviteResult} 回调的 operatorId 参数
```

* - -1: 接口调用异常,不会收到回调

```
*/
public abstract acceptInvite(video: boolean): number;
```

邀请处理结果回调

ArkTS

```
/**
```

* 接受邀请结果回调

```
* @param operatorId 操作id,对应 {@link JRTCCall#acceptInvite(boolean) accep
tInvite} 的返回值
* @param result 加入通话是否成功
*               - true: 成功
*               - false: 失败
* @param reason  接受邀请失败原因
*/
onAcceptInviteResult?: (operatorId: number, result: boolean, reason: strin
g) => void;
```

示例代码:

21

ArkTS

// 接受邀请

```
call.acceptInvite(true)
```

同时对方能收到接受邀请通知

ArkTS

```
/**
```

 * 对方接受邀请通知

```
 *
 * @param param 其他参数
 * @see JRTCCallExtraParam
 */
onInviteAccepted?: (param: JRTCCallExtraParam) => void;
```

4.3.6.2 拒绝邀请

ArkTS

```
/**
```

* 拒绝邀请

```
*
* @return
* - 操作id: 接口调用成功,对应 {@link JRTCCallCallback#onAcceptInviteResult(in
t, boolean, string)} onAcceptInviteResult} 回调的 operatorId 参数
```

* - -1: 接口调用异常,不会收到回调

```
*/
public abstract rejectInvite(): number;
```

示例代码

ArkTS

// 拒绝邀请

```
call.rejectInvite();
```

同时对方能收到拒绝邀请通知

22

ArkTS

```
/**
```

* 对方拒绝邀请通知

```
*
* @param param 其他参数
* @see JRTCCallExtraParam
*/
onInviteRejected?: (param: JRTCCallExtraParam) => void;
```

## 4.3.7 视频渲染

当加入房间后,除了本地的视频画面,还有房间内其他成员的视频画面,如果房间内其他成员有视频流

上传,本端可以获取到其他成员的的视频流并进行渲染;

当成员视频状态变化,比如该成员开始上传视频,此时可以去渲染该成员视频,该成员结束上传视频,

则可以去停止渲染该成员视频。

通过调用requestVideo方法订阅该视频,当成员离开需要调用unRequestVideo及时取消订阅该视频

流。

渲染视频画面需要调用 JRTCVideoComponent 组件传入视频流id即可渲染

23

ArkTS

```
/**
```

 * 订阅房间中其他用户的视频流

```
 *
 * @param participant JRTCRoomParticipant 成员对象
 * @param videoSize   视频请求的尺寸,详见 {@link JRTCVideoSize}
 * @return 接口调用结果
 * - true: 接口调用成功,会收到 {@link JRTCRoomCallback#onParticipantUpdate o
nParticipantUpdate} 回调
 * - false: 接口调用异常
 */
public abstract requestVideo(participant: JRTCRoomParticipant, videoSize:
JRTCVideoSize): boolean;
/**
```

 * 取消订阅房间中其他用户的视频流

```
 *
 * @param participant JRTCRoomParticipant 房间中其他成员对象
 * @return 调用是否正常
 * - true: 正常执行调用流程,会收到 {@link JRTCRoomCallback#onParticipantUpdat
e onParticipantUpdate} 回调
```

 * - false: 调用失败,不会收到回调通知

```
 */
public abstract unRequestVideo(participant: JRTCRoomParticipant): boolean;
```

示例代码

ArkTS

```
@State participantArray: Array<JRTCRoomParticipant> = [];
onParticipantUpdate: (participant: JRTCRoomParticipant | undefined,changeP
aram: JRTCRoomParticipantChangeParam | undefined) => {
  for (const participant of call.getParticipants() || []) {
    this.participantArray.push(participant);
  }
}
ForEach(this.participantArray, (participant: JRTCRoomParticipant) => {
  JRTCVideoComponent({
    streamId: participant.streamId,
    mediaDevice: JRTCManager.getInstance().mMediaDevice
  })
})
```

24

## 4.3.8 新成员加入

当新成员加入房间后,其他成员会收到onParticipantJoin成员加入的回调。

ArkTS

```
/**
```

* 成员加入回调

```
* <p>
```

* 当有用户调用 {@link JRTCRoom#join join} 接口加入房间成功时,已在房间中的成员会收到

此回调。

```
*
* @param participant JRTCRoomParticipant 成员对象
* @param room        当前 JRTCRoom 对象
*/
onParticipantJoin?: (participant: JRTCRoomParticipant | undefined) => void;
```

## 4.3.9 成员更新

当房间内成员状态发生改变时,其他成员能收到该成员状态变化通知onParticipantUpdate,具体成员

变化属性参考JRTCRoomParticipantChangeParam,包含成员音量、网络状态、音视频上传状态、成

员类型、视频订阅尺寸变化等。

ArkTS

```
/**
```

* 成员更新回调

```
*
* @param participant  成员对象
* @param changeParam  更新标识类
*/
onParticipantUpdate?: (participant: JRTCRoomParticipant, changeParam: C
JRTCRoomPropChangeParam) => void;
```

## 4.3.10 成员离开

当成员离开房间后,其他成员会收到成员离开的回调onParticipantLeft回调通知。

25

ArkTS

```
/**
```

* 成员离开回调

```
*
* @param participant  成员对象
* @param reason       成员离开原因
*/
onParticipantLeft?: (participant: JRTCRoomParticipant, reason: JRTCReasonCo
de) => void;
```

## 4.3.11 结束离开

成员可以自己离开通话或者结束通话。

ArkTS

```
/**
```

* 离开通话

```
* @note 仅自己离开
```

* @note 需要已经加入通话

```
*
* @return 接口调用结果
* - true: 接口调用成功,非空闲状态下,会收到 {@link JRTCCallCallback#onLeave on
Leave} 回调
* - false: 接口调用异常
*/
public abstract leave(): boolean;
/**
```

* 结束通话

* @note 自己离开并踢出通话中的其他成员

* @note 需要已经加入通话

```
*
* @return 接口调用结果
* - true: 接口调用成功,非空闲状态下,会收到 {@link JRTCCallCallback#onLeave on
Leave} 回调
* - false: 接口调用异常
*/
public abstract stop(): boolean;
```

离开或者结束通话会收到onLeave回调

26

ArkTS

```
/**
```

* 离开通话结果回调

```
* <p>
* 调用 {@link JRTCCall#leave leave} 接口成功后,会收到此回调。
*
* @param serialId    业务流水号
* @param reasonCode  离开原因,参见:{@link JRTCEnum.JRTCReasonCode 离开原因}
*/
onLeave?: (serialId: string, reasonCode: JRTCReasonCode) => void;
```

示例代码

ArkTS

```
// 离开通话
call.leave();
// 结束通话
call.stop();
// 离开或者结束回调
onLeave:(serialId: string, reasonCode: number) => {
}
```

## 4.3.12 登出

离开房间后,可以做登出操作,登出接口调用流程如下所示:

用户

JRTCSDK

|  |  |  |
|---|---|---|
| 登 | 出 | 成功 2 onLogout(reason) |
|  |  |  |
| 登 | 出 | 失败 强制登出 , 3 onLogout(reason) |
|  |  |  |

用户

JRTCSDK

登出结果通过JRTCClientCallback中的onLogout接口上报:

27

ArkTS

```
/**
```

* 登出 Juphoon RTC 平台,登出后不能进行平台上的各种业务

```
* <p>
* 登出结果通过 {@link JRTCClientCallback.onLogout onLogout} 回调通知
*
* @return { boolean } 接口调用结果
```

*  - true:接口调用成功

*  - false:接口调用异常

```
*/
public abstract logout(): boolean;
```

登出结果通过JRTCClientCallback中的onLogout接口进行上报。

ArkTS

```
/**
```

* 登出回调

```
*
* @param { JRTCReasonCode } reason 登出原因
*/
onLogout?: (reason: JRTCReasonCode) => void;
```

示例代码:

ArkTS

```
// 调用登出接口
client.logout();
// 监听登出结果回调
public onLogout(reason: number) {
    // 登出完成
}
```

## 4.3.13 登录登出状态改变通知

登录状态通过JRTCClientCallback中的onClientStateChanged接口上报

28

ArkTS

```
/**
```

* 登录状态变化通知

```
*
* @param { JRTCClientState } state 当前状态值
* @param { JRTCClientState } oldState 之前状态值
*/
onClientStateChanged?: (state: JRTCClientState, oldState: JRTCClientState)
=> void;
```

示例代码

ArkTS

```
//登录状态改变通知
onClientStateChanged:(state: JRTCClientState, oldState: JRTCClientState) =
> {
    //state 当前状态
    //oldState 之前状态
}
```

## 4.3.14 销毁SDK

每个模块都有对应的销毁接口。如不需再使用 SDK 的相关功能,可以强制释放 SDK 的资源。

注:该方法为同步调用,调用此方法后,你将无法再使用该模块的其它方法和回调。我们不建议在

JRTC SDK 的所有回调方法中调用此方法销毁对象,否则可能出现崩溃现象,如果一定要在回调方法中

调用,需要异步调用。

ArkTS

```
/**
* 销毁 JRTCCall 对象
*
```

* @note 该方法为同步调用,需要等待 JRTCCall 实例资源释放后才能执行其他操作,调用此方法

后,你将无法再使用 JRTCCall 的其它方法和回调。

* 我们 **不建议** 在 JRTCSDK 的回调中调用此方法销毁 JRTCCall 对象,否则可能出现崩溃现

```
象。

```

* 如需在销毁后再次创建 JRTCCall 实例,需要等待 destroy 方法执行结束后再创建实例。

```
*/
public static destroy(): void;
```

示例代码:

29

ArkTS

```
//建议按照初始化顺序反顺序销毁
JRTCCall.destroy();
JRTCMediaDevice.destroy();
JRTCClient.destroy();
```

//异步调用示例

// 登出回调

```
public onLogout(reason: number) {
    setTimeout(() => {
      JRTCCall.destroy();
      JRTCMediaDevice.destroy();
      JRTCClient.destroy();
    });
}
```

# 五、通话管理

本文将介绍多方视频中通话管理的相关功能。

# 5.1 设置用户角色

由于通用化录制需要区分不同用户角色,那么需要终端以特定的角色加入到通话中;

如果是终端直接调用加入接口加入通话,那么可以在通话参数里面设置用户角色,如下:

示例代码:

ArkTS

```
let joinParam:JRTCCallJoinParam = new JRTCCallJoinParam();
//设置访客身份加入
joinParam.role = JRTCCallCenterRole.GUEST
call.join("serialId", joinParam);
```

如果终端是通过被邀请加入,那么需要在接受邀请设置用户角色,如下:

30

ArkTS

```
  /**
```

   * 设置用户角色

   * @note 该接口只有在接受邀请前设置有效,主动加入通话,请使用加入通话参数设置

```
   *
   * @param role 用户角色
   */
  public abstract setRole(role: JRTCCallCenterRole);
```

示例代码:

ArkTS

```
onInviteReceived: (param: JRTCCallExtraParam) => {
      //收到邀请
    //设置访客身份加入
    call.setRole(JRTCCallCenterRole.MAIN_GUEST);
    //接受邀请
    call.acceptInvite(true);
}
```

# 5.2 获取统计信息

实时统计信息用于在通话中查看音视频收发情况,以及分辨率、帧率、码率,网络情况等。

31

ArkTS

```
/**
```

* 获取统计信息

```
*
* 以字符串形式返回,其中包含 "Config", "Network","Transport" 和 "Participant
s" 4个节点:
@verbatim
*      {
*         "Config":                                        // 音视频设置信
```

息

```
*              {
*                  "Audio Config:                          // 音频设置
*                  {
*                      "SRTP": off,                        // 是否对音频RT
```

P数据加密,以及加密会显示使用的加密协议,加密协议两端一致才会音频互通正常

```
*                      "Codec": opus,                      // 本端设置的音
```

频编码

```
*                      "Payload": 116,                     // 音频payload
```

的大小

```
*                      "Bitrate": 16000,                   // 音频码率
*                      "Pkt Len": 60,                      // 音频包长
*                      "Nack": off,                        // 丢包是否允许
```

数据包重传

```
*                      "RTX": off,                         // 是否允许RTX
```

技术

```
*                      "FEC/RED": off,                     // 是否开启FEC
*                      "AEC": on,                          // 是否开启回声
```

消除

```
*                      "Mode": OS,                         // AEC模式
*                      "HowlSupp": Auto,                   // AEC HowlSup
```

p模式

```
*                      "Sts": Auto,                        // AEC Sts模式
*                      "AGC": on,                          // 是否开启发送
```

端自动增益

```
*                      "Mode": Fixed,                      // 发送端AGC Mo
de
*                      "Target": 3,                        // 发送端AGC Ta
rget
*                      "Gain": 9,                          // 接收端AGC Ga
in
*                      "Rx AGC": off,                      // 是否开启接收
```

端自动增益

```
*                      "Mode": Fixed,                      // 接收端AGC Mo
de
*                      "Target": 3,                        // 接收端AGC Ta
rget
```

32

```
*                      "Gain": 9,                          // 接收端AGC Ga
in
*                      "VAD": off,                         // 是否开启VAD
*                      "Mode": Mid,                        // VAD Mode
*                      "ANR": off,                         // 是否开启发送
```

端噪音抑制

```
*                      "Mode": High,                       // ANR mode
*                      "Noise": N/A,                       // 噪音音量
*                      "SNR": N/A,                         // 信噪比
*                      "Rx ANR": off,                      // 是否开启接收
```

端噪音抑制

```
*                      "Mode": Low,                        // 接收端ANR mo
de
*                      "ARS": off,                         // 是否开启音频
```

码率控制

```
*                      "BR Min": N/A,                      // ARS码率最小
```

值

```
*                      "BR Max": N/A                       // ARS码率最大
```

值

```
*                  },
*                  "Video Config":                         // 视频设置
*                  {
*                      "SRTP": off,                        // 是否对音频RT
```

P数据加密,以及加密会显示使用的加密协议,加密协议两端一致才会音频互通正常

```
*                      "Codec": H264-SVC,                  // 双方通话采用
```

的编解码类型

```
*                      "Payload": 125,                     // 视频Payload
```

的大小

```
*                      "Bitrate": 2250,                    // 视频码率,单
位kbps
*                      "Framerate": 24,                    // 视频帧率,单
位fps
*                      "Resolution": 1280x720,             // 视频分辨率
*                      "FEC": on|124|123,                  // FEC是否打开
```

和payload的类型号

```
*                      "FIR": off,                         // 是否允许重发
```

关键帧

```
*                      "Key Interval": 0,                  // 允许的最小关
```

键帧间隔

```
*                      "Repeat": 0,                        // 关键帧丢失是
```

否允许重发

```
*                      "NACK": off,                        // 丢包是否允许
```

数据包重传

```
*                      "RTX": off,                         // 是否允许RTX
技术,RTX的payload类型
*                      "TMMBR": off,                       // 是否允许带宽
```

估计

```
58
```

33

```
*                      "RPSI": off,                        // 是否允许RPSI
```

技术

```
*                      "Small NALU": on,                   // 是否允许NALU
```

技术

```
*                      "ARS": off,                         // 是否开启ARS
```

自动码率检测

```
*                      "BR Min": 10,                       // ARS发送码率
```

下限

```
*                      "BR Max": 2000,                     // ARS发送码率
```

上限

```
*                      "FR Min": 1,                        // ARS发送帧速
```

率下限

```
*                      "FR Max": 30,                       // ARS发送帧速
```

率上限

```
*                      "Res. Ctrl": off,                   // 是否允许分辨
```

率控制

```
*                      "Res. Mode": 0,                     // 分辨率Mode
*                      "Fr Ctrl": on,                      // 是否允许帧速
```

率控制

```
*                      "CPU Load Ctrl": off,               // 是否允许CPU
```

控制

```
*                      "Target": 80,                       // CPU控制的最
```

大使用率

```
*                      "Bw Efficient": off,                // 是否采用节省
```

带宽模式

```
*                      "Error Conceal": off,               // 是否允许错误
```

隐藏技术,在解码出错的时候采用

```
*                      "Enhance color": off,               // 是否采用颜色
```

增强技术

```
*                      "Boost bright": off,                // 是否采用亮度
```

增强技术

```
*                      "Boost contrast": off,              // 是否采用对比
```

度增强技术

```
*                      "RTP Ext": CVO,                     // 使用的RTP扩
```

展的类型

```
*                      "Render Name": N/A,                 // 渲染图像的名
```

字

```
*                      "SVC": "320 180 250 640 360 600 1280 720 1400",
  // 会议SVC配置
*                      "TemporalLayers": 4,                // 取值1、2、
```

3、4,会议时间层设置

```
*                      "PreferMode":Clear                  // 偏好设置
*                  }
*          },
*          "Network":                                  // 网络统计信息
*          {
*              "Send Statistic:                        // 数据发送统计信息
*              {
```

34

```
*                  "Packets": 181|1305|0|0,            // 发送的数据包的个
```

数。正常包个数 | 探测包个数 | RED包个数 | NACK包个数

```
*                  "RTT": 4,                           // 网络双向延时的时
```

间,单位为毫秒

```
*                  "Jitter": 2,                        // 网络的扰动,表征数
```

据包抖动的时间,单位毫秒

```
*                  "Lost": 2,                          // 丢失的数据包的个数
*                  "LostRate": 0,                      // 当前的丢包率,单位
```

百分比

```
*                  "RelayLost": 0,                     // 服务器转发丢包率
*                  "RelayRtt": 0,                      // 服务器转发往返时
```

延,单位为毫秒

```
*                  "BitRate/BWE": 16/1345,             // BitRate表示当前
```

发送的数据包的码率,单位kbps;BWE表示当前发送带宽的估计值

```
*                  "AudioSend": 0|0,                   // 实际发送音频包次
```

数|估计发送音频包次数

```
*                  "VideoSend": 0|0,                   // 实际发送视频包次
```

数|估计发送视频包次数

```
*                  "ScreenSend": 0|0,                  // 实际发送屏幕共享包
```

次数|估计发送屏幕共享包次数

```
*                  "MaxPredKbps": 100,                 // 发送最大需求码率
*                  "Server(102679111220103708)": [2211(1): BWE(1345|697)
LOSS(0|0) OUT(A:37) IN(A:0;)] // 选用的第一个服务器
*              },
*              "Recv Statistic":                       // 数据接收统计信息
*              {
*                  "Packets": 1423|675|0|0,            // 收到的数据包的个
```

数。正常包个数 | 探测包个数 | RED包个数 | NACK包个数

```
*                  "Jitter": 1,                        // 网络的扰动,表征数
```

据包乱序的时间,单位毫秒

```
*                  "Lost": 0,                          // 丢失的数据包的个数
*                  "Lost Ratio": 0,                    // 当前的丢包率,单位
```

百分比

```
*                  "BitRate/BWE":178/2291,             // BitRate表示当前
```

接收的数据包的码率,单位kbps;BWE表示当前接收带宽的估计值

```
*                  "Server(102679111220103708)": [2211(3): BWE(1979|215
0) LOSS(0|0) OUT(A:37;FPS:24,FEC:10,SUB:00f0=3456) IN(A:17;V:2273=2211[00
```

f0]2273)] // 选用的第一个服务器

```
*              },
*          }
*          "Transport":                                // 运输通道
*          {
*              "Local": 2.1923737535:32414,            // 本地地址
*              "Remote": 2:11023,                      // 远端地址
*              "LastPaths": 2,2,                       // 最后使用通道
*              "Path": 2 [udp],                        // 通道名
*              "Step1": Delay/Loss(S/R): 4/0/0,        // 通道质量
*              "Cost": 7*(best: -1)                    // 通道分数
```

35

```
*          },
*          "Participants":
*          {
*          "2333":                                      // 成员为自己
*              {
*                  "Audio Sending Stats":              // 音频发送数据统计
*                  {
*                      "Packets": 143,                 // 发送的数据包的个数
*                      "BitRate": 18.5,                // 发送的数据包的码
```

率,单位kbps

```
*                      "FecPrecent": 0                 // 音频Fec保护百分
```

比,N/A表示未开启FEC保护

```
*                  },
*                  "Video Sending Stats":              // 视频发送数据统计
*                  {
*                      "Packets": 19502,               // 发送的数据包的个数
*                      "Capture Res": 640x360,         // 视频采集分辨率
*                      "Capture Fr": 30,               // 视频采集帧率
*                      "FPS/IDR": [0|0|24|0]/3,        // 当前视频发送帧速/
```

已发送的视频关键帧数

```
*                      "Resolution": 1280x720[0|0|0],  // 当前发送图像最大尺
```

寸。[]中为每种尺寸的帧率,取值范围为0到f(十六进制),0表示该层视频未被发送,值越大表示

该层视频帧率越高;

```
*                      "Bitrate/Setrate": 0/2250,      // Bitrate表示当前
```

发送的数据包的码率,单位kbps; Setrate表示视频编码的目标码率,单位kbps。

```
*                      "QP": 20,                       // 发送当前图像的量化
```

步长(0-51),越小图像画质越好。

```
*                      "EncodeTime": 10,               // 当前编码时间,可以
```

体现终端编码时占用的CPU性能,越大表示CPU占有越高,单位毫秒

```
*                      "Codec": H264-SVC,              // 采用的编解码类型
*                      "FecPrecent": 20                // 视频Fec保护百分
```

比,N/A表示未开启FEC保护

```
*                  },
*                  "Be Subscribed Stats":              // 被订阅统计信息
*                  {
*                      "Audio": true,                  // 音频是否被订阅
*                      "Video": [0|0|F|0]              // [S0|S1|S2|S3]表
```

示4个空间层被订阅

```
*                  },
*                  "Publish Stats":                    // 当前音视频发布状态
*                  {
*                      "Audio": true,                  // 当前音频发布状态
*                      "Video": true                   // 当前视频发布状态
*                  }
*              },
*              "6666":                                 // 成员不是自己
*              {
*                  "Audio Receiving Stats":            // 音频接收统计信息
```

36

```
*                  {
*                      "Packets": 40243,               // 接收的数据包的个数
*                      "BitRate": 18.5,                // 当前接收的数据包的
```

码率,单位kbps。

```
*                      "EpdRate/lr/dc": 0/0/0,         // expand rate/los
s rate/discard rate。neteq buffer中的扩展比例/丢包比例/丢弃比例
*                  },
*                  "Video Receiving Stats":            // 视频接收统计信息
*                  {
*                      "Packets": 19502,               // 接收的数据包的个数
*                      "BitRate": 161,                 // 当前发送的数据包的
```

码率,单位kbps

```
*                      "FPS/FIR": 24/0,                // 当前视频接收帧率/
```

视频关键帧请求个数

```
*                      "Resolution": 1280x720,         // 当前接收分辨率
*                      "Render FR": 24,                // 当前渲染帧速率
*                      "Codec": H264-SVC,              // 采用的编解码类型
*                      "PvMos": 4.9,                   // 表示过去5s平均流
```

畅度MOS分,每5s更新一次。体现视频画面的流畅程度。1到5分,1分最差,5分最好

```
*                      "SMOS": 5,                      // 表示当前清晰度MOS
```

分。体现视频画面的清晰程度。1到5分,1分最差,5分最好。前5s是0,是正常现象,因为PvMos

还没有值

```
*                  },
*                  "Subscribed Stats":                 // 订阅统计信息
*                  {
*                      "Channel Audio": true,          // 当前是否发布音频
*                      "Audio": true,                  // 当前音频订阅状态
*                      "Video": [0|0|F|0]              // [S0|S1|S2|S3]表
```

示4个空间层被订阅

```
*                  }
*              }
*          }
*      }
@endverbatim
*/
public abstract getStatistics(): string | undefined;
/**
```

* 获取实时统计信息

```
*
```

* 以Json字符串形式返回,包含以下信息:

```
@verbatim
*         {
*          "localActor": "[username:2333@100645.cloud.justalk.com]", // a
ctorID
*          "sendBWE": "1440",      // 发送带宽估计
*          "recvBWE": "929",       // 接收带宽估计
*          "sendBr": "16",         // 发送码率
```

37

```
*          "recvBr": "772",        // 接收码率
*          "sendJitter": "1",      // 发送jitter
*          "recvJitter": "0",      // 接收jitter
*          "sendLossRate": "0",    // 发送丢包率
*          "recvLossRate": "0",    // 接收丢包率
*          "encodeTime": "0",      // 编码时长
*          "rtt":"5",              // 往返延时
*          "audioSendBr": "19",    // 音频发送码率
*          "videoSendBr": "0",     // 视频发送码率
*          "audioLevel": "58",     // 音量
*          "event":""
*         }
@endverbatim
*/
public abstract getJsonStats(): string | undefined;
```

# 5.3 获取通话唯一标识

通话唯一标识getCallId对应于业务管理平台上的 callid,可用于查询录像数据、查询录像上传结果等

等。

ArkTS

```
/**
```

 * 获取唯一标识(服务器生成)

```
 *
 * @return 房间唯一标识
 */
public abstract getCallId(): string | undefined;
```

# 5.4 获取业务流水号

该业务流水号,用户可以在加入通话接口通过入参设置,也可以不传,不传则由服务端生成,且进入通

话后,可以由以下接口获取

38

ArkTS

```
/**
```

* 获取业务流水号

```
*
* @return 业务流水号
*/
public abstract getSerialId(): string | undefined;
```

# 六、消息通道

透明通道消息主要包含房间内消息(接口集成使用请查看章节6.1)和在线消息(接口集成使用请查看章

节6.2),具体使用要求和场景举例参考下表:

|  | 在线消息 | 房间内消息 |
|---|---|---|
| 一对一发送 | 支持 | 支持 |
| 群发消息 | 不支持 | 支持 |
| 是否支持异步发送结果上报 | 支持 | 不支持 |
| 是否需要登录 | 是 | 是 |
| 是否需要建立通话 | 否 | 是 |
| 使用场景举例 | 1、实现不依赖通话的一对一聊 天; 2、实现一些通话前的自定义信 令交互,比如呼叫、拒接/接听 等等; | 1、实现通话中的一些自定义信 令、通知等; 2、实现通话中单聊和群聊; |
| 消息内容支持 | 只支持文本消息 | 只支持文本消息 |
| 消息内容大小最大支持(bit) | 4K | 4K |

# 6.1 通话内消息

39

服务器

成员1

JRTCSDK

JRTCSDK

成员2

sendMessage()

消息发送

消息接收

onMessageReceived()

服务器

成员1

JRTCSDK

JRTCSDK

成员2

如果想在通话内给其他成员发送消息,可以调用sendMessage接口:

ArkTS

```
/**
```

* 发送消息,消息内容不能大于4K

```
*
* 指定成员会收到 {@link JRTCCallCallback#onMessageReceived onMessageReceive
```

d} 回调

```
* @param contentType 消息内容类型
* @param content 消息内容
```

* @param toUserId 指定成员的用户ID,传 undefined 给通话中全部成员发送消息

```
* @return 接口调用结果
* - true: 接口调用成功
* - false: 接口调用异常
*/
public abstract sendMessage(contentType: string, content: string, toUserI
d: string | undefined): boolean;
```

消息通过实现JRTCCallCallback的onMessageReceived接口上报。

40

ArkTS

```
/**
```

* 收到消息回调

```
*
* 通话中的成员可调用 {@link JRTCCall#sendMessage(string, string, string | und
```

efined)}  sendMessage} 接口给通话中的指定成员或全体成员发送文本消息,接收消息的成员

会收到此回调,由此获取消息具体信息。

```
* @param content 消息内容
* @param contentType 消息内容类型
* @param messageType 消息归属类型
* - {@link JRTCCallCenterMessageType#ONE_TO_ONE} : 一对一消息
* - {@link JRTCCallCenterMessageType#GROUP} : 群发消息(发送给通话中所有成员)
* @param fromUserId 发送方的用户ID
*/
onMessageReceived?: (content: string | undefined, contentType: string | un
defined, messageType: JRTCCallCenterMessageType, fromUserId: string) => vo
id;
```

示例代码:

ArkTS

```
//成员1发送消息给房间内所有成员
call.sendMessage(this.confMessageType, this.confMessageContent, "");
//成员1发送消息给成员2
call.sendMessage(this.confMessageType, this.confMessageContent, "成员2");
onMessageReceived: (content: string | undefined, contentType: string | unde
fined, messageType: JRTCMessageType, fromUserId: string) => {
  //成员2接收到来自成员1发送的消息
}
```

# 6.2 在线消息

41

成员1

JRTCSDK

Server

JRTCSDK

成员2

1client.sendOnlineMessage()

2在线消息发送

|  |  |  |  |  |  |
|---|---|---|---|---|---|
| 发送 | 成功 6 onOnlineMessageSendResult(true, messageId) | 5 在线消息发送结果 | 3 在线消息接收 | 4 onOnlineMessageReceived(message,userId) |  |
|  |  |  |  |  |  |
| 发送 | 失败 8 onOnlineMessageSendResult(false, messageId) | 7 在线消息发送失败 |  |  |  |
|  |  |  |  |  |  |

成员1

JRTCSDK

Server

JRTCSDK

成员2

只要登录到  Juphoon RTC 平台就可以通过JRTCClient的sendOnlineMessage实现在线消息的收

发,消息内容不能大于4K。

ArkTS

```
/**
```

* 发送在线消息

```
*
* @param { string } message 消息内容
* @param { string } userId 对端的用户名
* @return { number } 接口调用结果
*  - 操作id: 接口调用成功,对应 {@link JRTCClientCallback.onOnlineMessageSend
Result onOnlineMessageSendResult} 回调的 operatorId 参数
```

*  - -1: 接口调用异常,不会收到回调

* @note 消息大小不超过4k

```
*/
public abstract sendOnlineMessage(message: string, userId: string): numbe
r;
```

在线消息发送结果通过onOnlineMessageSendResult回调通知。

42

ArkTS

```
/**
```

* 在线消息发送结果回调

```
*
* @param { boolean } result 发送结果是否成功
*                           - true:发送成功
*                           - false:发送失败
* @param { number } operatorId 操作id,对应 {@link JRTCClient.sendOnlineMes
sage sendOnlineMessage} 的返回值
*/
onOnlineMessageSendResult?: (result: boolean, operatorId: number) => void;
```

示例代码:

ArkTS

```
@State operatorId
// 给用户 7777 发送在线消息
this.operatorId = client.sendOnlineMessage("消息内容", "777");
// 给用户 7777 发送在线消息结果
onOnlineMessageSendResult:(result: boolean, operatorId: number) => {
    if (this.operatorId === operatorId) {
        if(result) {
            // 在线消息发送成功
        } else {
            // 在线消息发送失败
        }
    }
}
// 收到在线消息
onOnlineMessageReceived:(message: string, userId: string) => {
    // 收到来自 userId 的消息,消息内容为 message
}
```

# 七、音频管理

43

Juphoon 音视频能力平台及终端的媒体引擎支持音频质量保障能力,Juphoon RTC SDK 提供视频通话

过程中访客端实现音频管理的功能。

# 7.1 发送本地音频流

通话中的成员可通过调用enableUploadAudioStream方法来开启关闭发送本地音频流。

ArkTS

```
/**
```

 * 开启/关闭发送本地音频流

```
 *
```

 * 通话中调用该方法可开启或关闭发送本地音频流。开启后,通话中的成员将听见本端声音;关闭

后,频道成员将听不见本端声音  

 * 通话中调用此方法成功后,服务器会更新状态并同步给通话中所有成员,即所有成员会收到 {@l

```
ink JRTCCallCallback#onParticipantUpdate onParticipantUpdate} 回调,具体可关
注 {@link JRTCRoomParticipant#audio  audio} 和 {@link JRTCRoomParticipant#
audio audio} 

```

 * 通话中调用此方法不影响接收其他成员的音频流

```
 * @param enable 开启/关闭发送本地音频流
```

 * - true: 开启,即发送本地音频流

 * - false: 关闭,即不发送本地音频流

```
 * @return 接口调用结果
 * - true: 接口调用成功
 * - false: 接口调用异常
 */
public abstract enableUploadAudioStream(enable: boolean): boolean;
```

1.在多方通话中,enableUploadAudioStream的作用是开启或关闭发送本地音频流。开启后,房间成

员将听见本端声音;关闭后,房间成员将听不见本端声音。房间中调用此方法不影响接收远端音

频。

2.初始化JRTCCall时,默认不发送本地音频流。若要加入房间时让房间内其他成员听见本端声音,

需要在调用join加入房间前设置,或者在JRTCCallJoinParam 设置。

3.房间中调用此方法开启或关闭发送本地音频流,服务器会更新状态并同步给其他房间成员同时,房

间中的其他成员会收到该成员“是否上传音频“的状态变化回调onParticipantUpdate。

4.此外,此方法还可以实现开启或关闭静音的功能。当 enable 值为 false ,将会停止发送本地音频

流,此时其他成员将听不到您的声音,从而实现静音功能。

44

ArkTS

```
/**
```

 * 成员更新回调

```
 *
 * @param participant  成员对象
 * @param changeParam  更新标识类
 */
onParticipantUpdate?: (participant: JRTCRoomParticipant, changeParam: JRTCR
oomParticipantChangeParam) => void;
```

示例代码:

ArkTS

```
// 关闭音频流发送
call.enableUploadAudioStream(false);
// 开启音频流发送
call.enableUploadAudioStream(true);
// 成员属性更新回调
onParticipantUpdate:(participant: JRTCRoomParticipant, changeParam: JRTCRo
omParticipantChangeParam) => {
    if(changeParam.audio){
      // 成员音频上传状态发生改变
      if(participant.audio){
        // 该成员音频流打开
      } else{
        // 该成员音频流关闭
      }
    }
}
```

# 7.2 音频输出

45

ArkTS

```
/**
```

* 开启/关闭音频输出

```
* <p>
```

* - 该方法可实现本地静音功能。关闭时听不到房间内其他成员的声音,不影响其他成员;开启时可

以听到其他成员声音

* - 初始化 JRTCRoom 时,音频输出功能默认是开启的。若要加入房间时听不见其他成员的声音,

```
建议在调用 {@link #join join} 加入房间前设置
*
* @param enable 是否开启音频输出
*               - true: 开启音频输出
*               - false: 关闭音频输出
* @return 接口调用结果
* - true: 接口调用成功,会收到 {@link JRTCCallCallback#onCallPropertyChanged
onCallPropertyChange} 回调
* - false: 接口调用异常
*/
public abstract enableAudioOutput(enable: boolean): boolean;
```

1.该方法可实现本地静音功能。关闭时听不到房间内其他成员的声音,不影响其他成员;开启时可以

听到其他成员声音。

2.初始化JRTCCall时,音频输出功能默认是开启的。若要加入房间时听不见其他成员的声音,建议

在调用join加入房间前设置。

3.该方法可以关闭或重新开启音频输出功能,在房间内和房间外均可调用,且在离开房间后该设置仍

然有效,也就是说这一次设置了关闭音频输出,那么下一次加入房间时也是默认关闭音频输出。

ArkTS

```
/**
```

* 通话属性改变,重点关注屏幕共享

```
*
* @param propChangeParam 通话改变的属性
*/
onCallPropertyChanged?: (propChangeParam: JRTCRoomPropChangeParam) => void;
```

示例代码:

46

ArkTS

```
// 关闭音频输出
call.enableAudioOutput(false);
// 开启音频输出
call.enableAudioOutput(true);
// 房间属性变化回调
onCallPropertyChanged:(changeParam: PropChangeParam) => {
 /**
```

 * 输出声音状态是否变化

```
 * - true: 变化
 * - false: 没变化
 */
  if (changeParam.audioOutput) {
  }
}
```

# 7.3 自定义音频输入

通话中可以自定义从外部音频文件作为音频源输入,使用场景举例:比如共享本地音频。

47

ArkTS

```
/**
```

* 开始/结束播放本地音频文件作为音频源输入

* @note 如果用户正在通话中,该音频将播放到通话内,通话中所有成员包括自己都能听到

```
*
* @param { boolean } enable 开始或者结束
* @param { string } filePath 音频文件路径,支持pcm,wav的格式(需要单声道,采样率
16K音频文件)
* @param { boolean } loop 是否循环播放
```

* @note 重复调用会覆盖

```
* @return { boolean } 接口调用结果
* - true: 接口调用成功
* - false: 接口调用异常
*/
public abstract enableAudioInputFromFile(enable: boolean, filePath: strin
g, loop: boolean): boolean;
/**
```

* 暂停/继续播放语音文件作为音频源输入

```
*
* @param { boolean } suspend
* - true:暂停播放
* - false:继续播放
* @return { boolean } 调用是否正常
```

* - true:正常执行调用流程

```
* - false:调用异常
*/
public abstract suspendAudioInputFromFile(suspend: boolean): boolean;
```

音频输入播放结束(非循环播放结束或者主动停止播放),会收到JRTCMediaDeviceCallback的

onFileAudioInputDidFinish回调通知

ArkTS

```
/**
```

* 本地文件音频源输入完成回调

```
*/
onFileAudioInputDidFinish?: () => void;
```

示例代码

48

ArkTS

```
// 开始分享本地文件音频输入到通话内
mediaDevice.enableAudioInputFromFile(true, "/sdcard/1.pcm", true);
mediaDevice.enableAudioInputFromFile(false, "", true);
onFileAudioInputFinish():void {
    // 分享本地文件音频输入到通话结束
}
```

# 7.4 本地音频播放

通话中可以播放一段本地音频,使用场景举例:比如播放来电铃声。

ArkTS

```
/**
```

* 开始播放音频

* @note 不管是否在通话中,该音频播放只有本地可以听到

```
*
* - 当播放音频文件完成后会收到 {@link JRTCMediaDeviceCallback#onRingPlayFinish
() onRingPlayFinish} 回调通知
* @param { string } filePath 音频文件路径,支持pcm,wav的格式(需要单声道,采样率
16K音频文件)
* @param { boolean } isLoop 是否循环播放
* @return { boolean } 接口调用结果
* - true: 接口调用成功
* - false: 接口调用异常
*/
public abstract startRing(filePath: string, isLoop: boolean): boolean;
/**
```

* 结束播放音频

```
*
* - 会收到 {@link JRTCMediaDeviceCallback#onRingPlayFinish() onRingPlayFini
```

sh} 回调通知

```
* @return { boolean } 接口调用结果
* - true: 接口调用成功
* - false: 接口调用异常
*/
public abstract stopRing(): boolean;
```

音频播放结束会收到JRTCMediaDeviceCallback的onRingPlayFinish回调通知

49

ArkTS

```
/**
```

* 音频播放完成

```
*/
onRingPlayFinish?: () => void;
```

示例代码:

ArkTS

```
mediaDevice.startRing("/sdcard/1.pcm", true);
// 结束播放本地音频
mediaDevice.stopRing();
onRingPlayFinish:() => {
  // 本地音频播放结束
}
```

# 7.5 音频异常回调

通过实现JRTCMediaDeviceCallback的onAudioError接口监听音频异常回调,具体错误查看参数

error 描述。

ArkTS

```
/**
```

* 音频异常

```
*
* @param { string } error 异常信息
*/
onAudioError?: (error: string) => void;
```

# 7.6 音频数据回调

获取音频数据建议创建worker线程接收回调数据

50

## 7.6.1 输入音频数据回调

ArkTS

```
/**
```

 * 设置音频输入数据回调

 * @note 因为回调数据比较频繁,建议创建独立的Worker线程调用该接口

 * 当Worker线程结束时,内部会自动清除回调,也可以手工设置null来主动删除回调

```
 * setAudioInputFrameCallback(null)
 *
```

 * @param callback 全局唯一的回调函数,回调参数说明如下:

```
 * @param { string } inputId 输入源的自定义字符串
 * @param { number } sampleRateHz 输入源的采样频率
 * @param { number } channels 输入源的频道数量
 * @param { ArrayBuffer } data 该帧的采样数据
 * @return { boolean }
 * -true  设置成功
 * -false 设置失败
 */
export function setAudioInputFrameCallback(callBack: ((inputId: string, sa
mpleRateHz: number, channels: number, data: ArrayBuffer) => void) | nul
l): boolean
```

示例代码

51

ArkTS

```
//主线程
let worker: worker.ThreadWorker = new worker.ThreadWorker("子线程文件路径");
worker.postMessage({"option":"StartInput"})
worker.postMessage({"option":"StopInput"})
//子线程
workerPort.onmessage = (e: MessageEvents) => {
  if (e.data.option as string == "StartInput"){
    setAudioInputFrameCallback((inputId: string, sampleRateHz: number, cha
nnels: number, data: ArrayBuffer) => {
      //具体操作
    });
  }else if(e.data.option as string == "StopInput"){
    setAudioInputFrameCallback(null);
  }
}
```

## 7.6.2 输出音频数据回调

ArkTS

```
/**
```

 * 设置音频输出数据回调

 * @note 因为回调数据比较频繁,建议创建独立的Worker线程调用该接口

 * 当Worker线程结束时,内部会自动清除回调,也可以手工设置null来主动删除回调

```
 * setAudioOutputFrameCallback(null)
 *
```

 * @param callback 全局唯一的回调函数,回调参数说明如下:

```
 * @param { string } inputId 输入源的自定义字符串
 * @param { number } sampleRateHz 输入源的采样频率
 * @param { number } channels 输入源的频道数量
 * @param { ArrayBuffer } data 该帧的采样数据
 * @return { boolean }
 * -true  设置成功
 * -false 设置失败
 */
export function setAudioOutputFrameCallback(callBack: ((inputId: string, s
ampleRateHz: number, channels: number, data: ArrayBuffer) => void) | nul
l): boolean
```

示例代码

52

ArkTS

```
//主线程
let worker: worker.ThreadWorker = new worker.ThreadWorker("子线程文件路径");
worker.postMessage({"option":"StartOutput"})
worker.postMessage({"option":"StopOutput"})
//子线程
workerPort.onmessage = (e: MessageEvents) => {
  if (e.data.option as string == "StartOutput"){
    setAudioOutputFrameCallback((inputId: string, sampleRateHz: number, ch
annels: number, data: ArrayBuffer) => {
      //具体操作
    });
  }else if(e.data.option as string == "StopOutput"){
    setAudioOutputFrameCallback(null);
  }
}
```

# 八、视频管理

# 8.1 发送本地视频流

房间内的成员可通过调用enableUploadVideoStream方法来开启关闭发送本地视频流。

53

ArkTS

```
/**
```

* 开启/关闭发送本地视频流

```
* <p>
```

* - 调用该方法可开启或关闭发送本地视频流。开启后,房间成员将可以看见本端视频画面;关闭

后,房间成员将看不见本端视频画面

* - 房间中调用此方法不影响接收远端视频

* - 初始化 JRTCRoom 时,默认发送本地视频流。若要加入房间时,让房间内其他成员看见本端视

频画面,建议在调用 {@link #join join} 加入房间前设置

* - 该方法在房间内和房间外均可调用,且在离开房间后该设置仍然有效。也就是说这一次设置了关

闭发送本地视频流,那么在下一次加入房间时默认会关闭发送本地视频流

* - 通话中也可调用此方法开启或关闭发送本地视频流,服务器会更新状态并同步给其他房间成员,

```
即房间中所有成员都会收到 {@link JRTCRoomCallback#onParticipantUpdate onPartici
pantUpdate} 回调
*
* @param enable 是否发送本地视频流
*               - true: 开启,即发送本地视频流
*               - false: 关闭,即不发送本地视频流
* @return 接口调用结果
* - true: 接口调用成功
```

* - 在调用此方法时,用户不在房间中,不会收到回调

```
* - 在调用此方法时,用户在房间中,会收到 {@link JRTCRoomCallback#onRoomPropertyC
hanged onRoomPropertyChange} 回调
* - false: 接口调用异常
*/
public abstract enableUploadVideoStream(enable: boolean): boolean;
```

1.enableUploadVideoStream的作用是设置“是否上传视频流数据。调用该方法可开启或关闭发送本

地视频流。开启后,房间成员将可以看见本端视频画面;关闭后,房间成员将看不见本端视频画

面。房间中调用此方法不影响接收远端音频。

2.初始化JRTCCall时,默认发送本地视频流。若要加入房间时,让房间内其他成员看见本端视频画

面,建议在调用join加入房间前设置。房间中调用此方法不影响接收远端视频。

3.房间中也可调用此方法开启或关闭发送本地视频流,服务器会更新状态并同步给其他房间成员,房

间中的其他成员会收到该成员“是否上传音频“的状态变化回调onParticipantUpdate。

4.该方法在房间内和房间外均可调用,且在离开房间该设置仍然有效。也就是说这一次设置了关闭发

送本地视频流,那么在下一次加入房间时默认会关闭发送本地视频流。

此外,调用该方法发送本地视频流数据还要依赖摄像头是否已经打开。

54

ArkTS

```
/**
```

* 成员属性更新回调

```
* <p>
```

* 当房间中有成员的属性发生变化时,房间中的其他成员会收到此回调,例如音频上传状态、视频上

传状态、网络状态等发生变化。

```
*
* @param participant JRTCRoomParticipant 成员对象
* @param changeParam {@link ChangeParam} 更新标识类对象
* @param room        当前 JRTCRoom 对象
*/
onParticipantUpdate?: (participant: JRTCRoomParticipant, changeParam: JRTC
RoomParticipantChangeParam) => void;
```

示例代码

ArkTS

```
// 关闭视频流发送
call.enableUploadVideoStream(false);
// 开启视频流发送
call.enableUploadVideoStream(true);
// 通话中成员属性更新回调
onParticipantUpdate:(participant: JRTCRoomParticipant, changeParam: JRTCRo
omParticipantChangeParam) => {
  if(participant.video){
    //该成员视频流打开
  } else{
    //该成员视频流关闭
  }
}
                                                     };
```

# 8.2 订阅/取消订阅视频流

55

ArkTS

```
/**
```

 * 订阅房间中其他用户的视频流

```
 *
 * @param participant JRTCRoomParticipant 成员对象
 * @param videoSize   视频请求的尺寸,详见 {@link JRTCVideoSize}
 * @return 接口调用结果
 * - true: 接口调用成功,会收到 {@link JRTCRoomCallback#onParticipantUpdate o
nParticipantUpdate} 回调
 * - false: 接口调用异常
 */
public abstract requestVideo(participant: JRTCRoomParticipant, videoSize:
JRTCVideoSize): boolean;
/**
```

 * 取消订阅房间中其他用户的视频流

```
 *
 * @param participant JRTCRoomParticipant 房间中其他成员对象
 * @return 调用是否正常
 * - true: 正常执行调用流程,会收到 {@link JRTCRoomCallback#onParticipantUpdat
e onParticipantUpdate} 回调
```

 * - false: 调用失败,不会收到回调通知

```
 */
public abstract unRequestVideo(participant: JRTCRoomParticipant): boolean;
```

示例代码

ArkTS

```
onParticipantUpdate: (participant: JRTCRoomParticipant | undefined,changePa
ram: JRTCRoomParticipantChangeParam | undefined) => {
  if (participant!.video) {
    room.requestVideo(participant, new JRTCVideoSize(width, height));
  }
}
```

# 8.3 SVC 设置说明

根据实际订阅需求和网络状况动态调整视频发送分辨率是 JSM 房间的特性之一,SVC 可用于设置房间

视频的每一层编码分辨率。该参数在房间创建时设置,且全局统一。

具体使用详见SVC 说明。

56

可在加入房间时,通过加入通话参数JRTCCallJoinParam的svcResolution属性进行设置,房间全局

属性,只有第一个加入房间用户设置有效。

ArkTS

```
/**
* svc分辨率,默认为 "1 180 250 360 600 720 1400"
*
* @note 当参数 {@link #setVideoDefinition(int)} videoDefinition} 为 {@link
JRTCRoomVideoDefinition#CUSTOM CUSTOM} 时有效
*
```

* 用于自定义分层参数和码率

```
*
```

* 格式:

* 高度公约数第一层高倍数第一层码率第二层高倍数第二层码率第三层高倍数第三层码率第

四层高倍数第四层码率 

```
* 说明 

* 1)默认宽高比16:9,即 @ref  wholeRatio 

```

* 2)编码宽高最后被裁成16整除 

```
* 例如 "1 180 250 360 600 720 1400" 

* 第一层分辨率宽320(180*1/9*16)高 180(180*1);码率250kbps 

* 第二层分辨率宽640(360*1/9*16)高 360(360*1);码率600kbps 

* 第三层分辨率宽1280(720*1/9*16)高 720(720*1);码率1400kbps 

* 此情况下只有三层,若需要四层,则需补充为 "1 180 250 360 600 720 1400 1080 160
0" 

* 第四层分辨率宽1920(1080*1/9*16)高 1080(1080*1);码率1600kbps
*
```

* @note 房间全局属性,第一个加入房间成员设置成效

```
*/
public set svcResolution(value: string);
```

示例代码

ArkTS

```
let param:JRTCRoomJoinParam = new JRTCRoomJoinParam();
// 设置svc参数
param.setSvcResolution("1 180 250 360 600 720 1400 1080 1600");
// 加入房间
call.join("10086", param);
```

# 8.4 设置本地视频宽高比

57

在通话内设置本地视频宽高比,会影响视频画面宽高比,用于适配不同屏幕的显示需求,需在进入房间

后调用。

ArkTS

```
/**
```

* 设置本端视频宽高比

```
* <p>
```

* 将自己的视频采集根据宽高比裁剪后进行发送,通话中其他成员收到的画面将是裁剪后的比例。<b

```
r>
```

* 该方法不影响其他成员的画面在本端的显示比例,也不影响其他成员相互之间的画面显示比例。<b

```
r>
* 必须 ***开始通话后*** 设置才能生效,即收到 {@link JRTCAgentCallback#onCallSta
teChanged onCallStateChanged} 回调且 type == {@link JRTCCallCenterAgentCall
StateChangeType#TALKING} 时设置才生效。
*
* @param ratio 视频宽高比
* @return 接口调用结果
* - true: 接口调用成功
* - false: 接口调用异常
*/
public abstract setRatio(ratio: number): boolean;
```

示例代码

ArkTS

```
onJoin: (result: boolean, reasonCode: JRTCReasonCode) => {
  call.setRatio(0.5625);
}
```

# 8.5 视频截图

58

ArkTS

```
/**
```

* 截图

```
*
* @param { string } streamId  要截图的视频流ID
* @param { string }path 要存放截图的文件路径
* @return 接口调用结果
* - true: 接口调用成功
* - false: 接口调用异常
*/
public abstract snapshotWithStreamId(streamId: string, path: string): bool
ean;
```

结果通过实现JRTCMediaDeviceCallback中的onSnapshotComplete接口上报

ArkTS

```
/**
```

* 截图完成回调

```
*
* @param { string } file 截图路径
* @param { number } width 图片像素宽
* @param { number } height 图片像素高
*/
onSnapshotComplete?: (file: string, width: number, height: number) => void;
```

示例代码:

ArkTS

```
```

// 截取指定视频流ID的帧图片并且保存到指定路径

// 视频流,可以是本地视频流、对端视频流或者屏幕共享视频流

```
mediaDevice.snapshotWithStreamId("user_renderId", "file_save_path");
// 截图完成回调
public void onSnapshotComplete(String file, int width, int height) {
//截图完成,可以从文件路径获取截图文件进行后续操作
}
onSnapshotComplete:(file: string, width: number, height: number) => {
}
```

# 8.6 视频采集回调

59

当打开本端摄像头视频预览或者打开本地屏幕采集时,通过实现JRTCMediaDeviceCallback的

onVideoCaptureDidStart接口能收到采集开始通知

ArkTS

```
/**
```

* 视频采集开始回调

```
*
* @param { string } streamId 视频流ID
* @param { number } ratio 视频宽高比
*/
onVideoCaptureDidStart?: (streamId: string, ratio: number) => void;
```

# 8.7 视频异常回调

通过实现JRTCMediaDeviceCallback的onVideoError接口来监听视频异常、采集异常、渲染错误等

事件,具体原因查看参数 error 描述。

ArkTS

```
/**
```

* 视频异常,渲染错误,包括摄像头采集错误、屏幕采集错误等回调

```
*
* @param { JRTCMediaDeviceVideoErrorType } errorType   异常类型
* @see JRTCMediaDeviceVideoErrorType.OTHER  其他未知异常
* @see JRTCMediaDeviceVideoErrorType.CAMERA 摄像头异常
* @see JRTCMediaDeviceVideoErrorType.SCREEN 屏幕采集异常
* @see JRTCMediaDeviceVideoErrorType.RENDER 视频渲染异常
* @param { string } errorDetail 异常详细描述
*/
onVideoError?: (errorType: JRTCMediaDeviceVideoErrorType, errorDetail: str
ing) => void;
```

# 九、设备管理

Juphoon RTC SDK 支持设备设置摄像头相关参数与配置,并在提供进入房间前的视频设备测试方法。

# 9.1 音频设备管理

在音频场景中,您可能需要根据实际的场地情况选择音频的采集设备和播放设备。

60

## 9.1.1 音频参数设置

设置audioParam音频参数,在加入通话前设置生效,若不设置参数,使用 SDK 默认值

| 参数 | 描述 |
|---|---|
| audioInputDevice | 音频输入设备 |
| audioOutputDevice | 音频输出设备 |
| audioInputSamplingRate | 音频输入采样率 |
| audioOutputSamplingRate | 音频输出采样率 |
| audioInputChannelNumber | 音频输入通道数量 |
| audioOutputChannelNumber | 音频输出通道数量 |

## 9.1.2 扬声器的开启关闭

ArkTS

```
/**
```

* 开启/关闭扬声器

* @note 只有在音频已经启动的情况下调用才会生效

```
*
* @param { boolean } enable 开启或关闭扬声器
* - true: 开启
* - false: 关闭
*/
public abstract enableSpeaker(enable: boolean): void
```

示例代码

ArkTS

```
//听筒模式
mediaDevice.enableSpeaker(false);
//外放模式
mediaDevice.enableSpeaker(true);
```

## 9.1.3 获取麦克风音量级别

打开音频采集后就可以实时调用getMicLevel接口获取当前的采集音量级别,与通话状态无关。

61

ArkTS

```
/**
```

 * 获取当前本地音量级别,音量级别范围为0-100,用以测试设备

 * 目前只在开始麦克风检测,或者当房间内有输入音频时,才能获取到有效的音量级别

```
 *
 * @return { number } 麦克风音量级别,返回-1获取失败
 */
public abstract getMicLevel(): number;
```

示例代码

ArkTS

//获取本地音量采集级别

```
mediaDevice.getMicLevel();
```

## 9.1.4 获取扬声器音量级别

打开音频输出后就可以实时调用getSpkLevel接口获取当钱的扬声器的音量级别,与通话状态无关。

ArkTS

```
/**
```

* 获取当前扬声器音量级别,音量级别范围为0-100,用以测试设备

* 目前只在开始扬声器检测,或者当房间内有输出音频时,才能获取到有效的音量级别

```
*
* @return { number } 扬声器音量级别,返回-1获取失败
*/
public abstract getSpkLevel(): number
```

示例代码

ArkTS

//获取本地扬声器的音量级别

```
mediaDevice.getSpkLevel();
```

## 9.1.5 获取当前噪声强度

62

ArkTS

```
/**
```

* 获取当前噪声强度

```
* 环境平均噪声强度(1s), 检测需要打开麦克风 {@link startAudio startAudio} 或者
{@link startAudioInput startAudioInput}
* @return { number } 噪声强度
```

* - -1:获取失败

* - 0-50dB:噪声非常微弱

```
* - 50-60dB:噪声较弱
* - 60-70dB:噪声较强
```

* - 70dB以上:噪声非常强

```
*/
public abstract getAnrNoiseLevel(): number;
```

## 9.1.6 获取当前信噪比强度

ArkTS

```
/**
```

* 获取当前信噪比强度

```
* 环境平均信噪比强度(1s), 检测需要打开麦克风 {@link startAudio startAudio} 或
者 {@link startAudioInput startAudioInput}
* @return { number } 噪声强度
```

* - -1:获取失败

* - 0-20dB:噪声明显,语音含糊,较难听清

* - 20-40dB:语音基本能听清,但有一定的噪声

* - 40dB以上:语音非常清晰

```
*/
public abstract getAnrNoiseRatio(): number;
```

## 9.1.7 设置是否开启自动增益控制

63

ArkTS

```
/**
```

* 设置是否开启自动增益控制

```
* @note 需要在打开音频输入设备 {@link startAudioInput} 或者 {@link startAudio}
```

前调用才生效

```
*
* @param { boolean } agcOn 是否开启自动增益控制
*/
public abstract setAgc(agcOn: boolean): void;
```

## 9.1.8 设置开启自适应回音消除

ArkTS

```
/**
```

* 设置开启自适应回声消除

```
* @note 需要在打开音频输入设备 {@link startAudioInput} 或者 {@link startAudio}
```

前调用才生效

```
*
* @param { boolean } aecOn 是否开启自适应回声消除
*/
public abstract setAec(aecOn: boolean): void;
```

# 9.2 视频设备管理

在视频场景中,您可能需要根据实际的情况选择视频的采集设备,以及相关的采集参数。

## 9.2.1 获取摄像头列表

ArkTS

```
/**
```

* 获取摄像头列表

```
*
* @return 摄像头列表
*/
public abstract getCameras(): ArrayList<JRTCMediaDeviceCamera>;
```

示例代码

64

ArkTS

// 获取所有可用的摄像头列表

```
const cameras: ArrayList<JRTCMediaDeviceCamera> = mediaDevice.getCameras();
```

## 9.2.2 指定摄像头/指定摄像头采集角度

ArkTS

```
/**
* 指定要开启的摄像头,在 {@link startCamera} 之前调用
*
* @param { JRTCMediaDeviceCamera } camera 摄像头对象
*/
public abstract specifyCamera(camera: JRTCMediaDeviceCamera): void;
/**
```

* 指定摄像头采集角度

```
*
* @param { JRTCMediaDeviceVideoAngle } angle 角度
*/
public abstract specifyCameraAngle(angle: JRTCMediaDeviceVideoAngle): voi
d;
```

示例代码

ArkTS

```
// 获取所有可用的摄像头列表
let cameras:ArrayList<JRTCMediaDeviceCamera> = mediaDevice.getCameras();
// 指定要开启的摄像头
mediaDevice.specifyCamera(cameras[0]);
// 指定摄像头采集角度为90度
mediaDevice.specifyCameraAngle(90);
```

## 9.2.3 摄像头采集属性

65

ArkTS

```
/**
```

* 设置摄像头采集属性

```
*
```

* 在调用 {@link startCamera} 接口开启摄像头前设置即可生效

```
* @param { number } width 采集宽度,默认为 640
* @param { number } height 采集高度,默认为 360
* @param { number } frameRate 采集帧速率,默认为 24
*/
public abstract setCameraProperty(width: number, height: number, frameRat
e: number): void;
```

示例代码

ArkTS

```
mediaDevice.setCameraProperty(640, 360, 24);
1
```

## 9.2.4 开启/关闭摄像头

66

ArkTS

```
/**
```

* 开启摄像头

```
*
```

* @note 调用此方法时需要保证默认摄像头不为空,即 {@link defaultCamera} 不为空,否

则将直接返回 false

```
*
* @return 接口调用结果
* - true: 接口调用成功
```

*  - 若调用此方法前摄像头已打开,不会收到回调通知

```
*  - 若调用此方法前摄像头未打开,会收到 {@link JRTCMediaDeviceCallback#onCamera
Update onCameraUpdate} 回调
* - false: 接口调用异常
*/
public abstract startCamera(): boolean;
/**
```

* 关闭摄像头

```
*
* @return 接口调用结果
* - true: 接口调用成功
```

*  - 调用此方法前摄像头未打开,不会收到回调通知

```
*  - 调用此方法前摄像头已打开,会收到 {@link JRTCMediaDeviceCallback#onCameraUp
date onCameraUpdate} 回调
* - false: 接口调用异常
*/
public abstract stopCamera(): boolean;
```

示例代码

ArkTS

```
// 打开本地摄像头
mediaDevice.startCamera();
// 关闭本地摄像头
mediaDevice.stopCamera();
```

## 9.2.5 切换摄像头

67

ArkTS

```
/**
```

* 切换摄像头

* @note 内部会根据当前摄像头类型来进行切换

```
*
```

* - 调用此方法时要保证摄像头已打开,否则将直接返回 false

* - 设备拥有两个以上摄像头,否则将直接返回 false

```
* - 满足以上两个条件后,内部会调用 {@link switchCamera switchCamera} 接口并提供返
```

回值

```
* @return 接口调用结果
* - true: 接口调用成功
* - false: 接口调用异常
*/
public abstract switchCamera(): Promise<boolean>;
/**
```

* 切换到指定摄像头

* @note调用此方法时需要保证摄像头已打开并且摄像头数大于0,否则将直接返回 false

```
*
* @param { JRTCMediaDeviceCamera } camera 摄像头对象
* @return 接口调用结果
* - true: 接口调用成功
```

*  - 摄像头个数 == 1,不会收到回调

```
*  - 摄像头个数 > 1,会收到 {@link JRTCMediaDeviceCallback#onCameraUpdate onC
ameraUpdate} 回调
```

* - false: 接口调用异常,不会收到回调

```
*/
public abstract switchCamera(camera: JRTCMediaDeviceCamera): Promise<boole
an>;
/**
```

* 切换摄像头,用于手机前置和后置摄像头的切换

```
*
* @return 接口调用结果
* - true: 接口调用成功
* - false: 接口调用异常
*/
public abstract switchCameraBetweenFrontAndBack(): Promise<boolean>;
```

示例代码

68

ArkTS

```
// 切换摄像头
mediaDevice.switchCamera();
// 切换至指定摄像头
mediaDevice.switchCamera(mediaDevice.getCameras[0]);
// 前后置摄像头切换
mediaDevice.switchCameraBetweenFrontAndBack();
```

# 十、体验提升

# 10.1 通话中质量检测

在通话场景中,开发者经常需要了解当前通话的通话质量、设备状态等信息,监测通话的整体体

验;也可将部分质量数据在 UI 层面展示给用户,使用户能够及时了解当前通话的整体质量。Juphoon

RTC SDK 支持将关键的音视频状况、网络状况、设备状态的相关指标实时回调给 APP 应用层,应用层

可以将收到的数据进行展示或统计。

## 10.1.1 网络质量检测

视频通话过程中,通话中成员的网络状态发生变化导致视频通话出现质量波动的时候,SDK 会通

JRTCCallCallback的onParticipantUpdate回调进行上报。

ArkTS

```
/**
```

* 成员更新回调

```
*
* @param participant  成员对象
* @param changeParam  更新标识类
*/
onParticipantUpdate?: (participant: JRTCRoomParticipant, changeParam: JRTCR
oomParticipantChangeParam) => void;
```

示例代码

69

ArkTS

```
onParticipantUpdate(participant: JRTCRoomParticipant, changeParam: JRTCRoo
mParticipantChangeParam) {
  if (changeParam.netStatus) {
      switch (participant.netStatus) {
        case JRTCNetStatus.DISCONNECTED:
          // 断开
          break;
        case JRTCNetStatus.VERY_BAD:
          // 非常差
          break;
        case JRTCNetStatus.BAD:
          // 差
          break;
        case JRTCNetStatus.NORMAL:
          // 一般
          break;
        case JRTCNetStatus.GOOD:
          // 好
          break;
        case JRTCNetStatus.VERY_GOOD:
          // 非常好
          break;
      }
    }
}
```

## 10.1.2 音频质量检测

视频通话过程中,通话中成员的说话声音状态发生变化,SDK 会通过JRTCCallCallback的

onParticipantUpdate回调进行上报。

示例代码:

70

ArkTS

```
onParticipantUpdate:(participant: JRTCRoomParticipant, changeParam: JRTCRo
omParticipantChangeParam) => {
  if (changeParam.volumeStatus) {
    switch (participant.volumeStatus) {
      case JRTCVolumeStatus.NONE:
        // 无声音 1-30
        break;
      case JRTCVolumeStatus.VERY_LOW:
        // 很低 30-40
        break;
      case JRTCVolumeStatus.LOW:
        // 低 40-50
        break;
      case JRTCVolumeStatus.MID:
        // 中 50-70
        break;
      case JRTCVolumeStatus.HIGH:
        // 高 70-80
        break;
      case JRTCVolumeStatus.VERY_HIGH:
        // 很高 >80
        break;
    }
  }
}
```

## 10.1.3 剩余可用内存检测

通话建立后,JRTCMediaDeviceCallback的onMemoryAvailable将定时上报系统中的内存剩余情况,

检测系统的运行情况。

ArkTS

```
/**
```

 * 上报剩余可用内存回调

```
 *
```

 * 周期性上报一次内存剩余情况

```
 * @param { number } memorySize  当前剩余可用内存空间(MB)
 */
onMemoryAvailable?: (memorySize: number) => void;
```

71

示例代码

ArkTS

```
onMemoryAvailable(memorySize: number) {
  if (memorySize < 100) {
    // 内存已严重不足,已不足100M,可能影响软件正常使用
  } else if (memorySize < 200) {
    // 剩余内存紧张,已不足200M
  } else if (memorySize < 300) {
    // 剩余内存低,已不足300M
  } else {
    return;
  }
}
```

# 10.2 文件上传

获取文件上传或断点续传信息requestFileUploadInfo

72

ArkTS

```
/**
```

* 获取文件上传或断点续传信息

```
*
```

* @param { string } serialId 业务id,必选,如果是通话业务相关文件,需要传通话唯一

```
标识 callId
* @param { JRTCRequestFileUploadParam } requestFileUploadParam 请求文件上传
```

信息参数,必选

```
* @return { boolean } 接口调用结果
*  - 操作id: 接口调用成功,对应 {@link JRTCClientCallback.onRequestFileUpload
InfoResponse onRequestFileUploadInfoResponse } 回调的 operatorId 参数
```

*  - -1: 接口调用异常,不会收到回调

* @note 目前仅支持视频和图片类型文件上传,服务端会通过文件后缀名判断

```
*/
public abstract requestFileUploadInfo(serialId: string, requestFileUploadP
aram: JRTCRequestFileUploadParam): number;
/**
```

* 获取文件上传或断点续传信息响应

```
*
* @param { number } operatorId 操作id,对应 {@link JRTCClient.requestFileUp
loadInfo requestFileUploadInfo} 的返回值
* @param { boolean } result 请求是否成功
*                           - true:请求成功
*                           - false:请求失败
```

* @param { string } url 上传地址,分片录制文件上传场景,首次请求分片上传信息时有效

* @param { string } token 文件上传所需token,用于校验上传合法性,需要在上传文件的

时候携带

```
* @param { number } requestTimestamp 本次请求发起时间戳,用于控制上传地址有效期,
```

需要在上传文件的时候携带

```
* @param { string } extraInfo 随路参数
* @param { number } fileSize 文件大小
* @param { number } offset 偏移量
* @param { string } fileType 文件类型
* @param { string } serverOid 上传目标服务Oid
* @param { string } reason 请求失败原因描述,当 result 为 false 时有效
*/
onRequestFileUploadInfoResponse?: (operatorId: number, result: boolean, ur
l: string, token: string, requestTimestamp: number, extraInfo: string, fil
eSize: number, offset: number, fileType: string, serverOid: string, reaso
n: string) => void;
```

示例代码

73

ArkTS

```
// 创建上传文件参数对象
const fileUploadParam = new JRTCRequestFileUploadParam();
fileUploadParam.setFileName("");
// ...
// 获取文件上传或断点续传信息
client.requestFileUploadInfo("serialId", fileUploadParam);
  onRequestFileUploadInfoResponse: (operatorId: number, result: boolean, u
rl: string, token: string, requestTimestamp: number, extraInfo: string, fi
leSize: number, offset: number, fileType: string, serverOid: string, reaso
n: string) => {
  if (result) {
    // 根据返回 url 进行文件上传
  } else {
    // 查看 reason 值(请求失败原因)
  }
}
```

文件上传成功后,再调用completeFileUpload接口确认文件已上传

74

ArkTS

```
/**
```

* 文件上传完成确认

```
*
```

* @param { string } serialId 业务id,必选,如果是通话业务相关文件,需要传通话唯一

```
标识 callId
* @param { JRTCCompleteFileUploadParam } completeFileUploadParam 文件上传完
```

成确认参数,必选

```
* @return { boolean } 接口调用结果
*  - 操作id: 接口调用成功,对应 {@link JRTCClientCallback.onCompleteFileUploa
dResponse onCompleteFileUploadResponse} 回调的 operatorId 参数
```

*  - -1: 接口调用异常,不会收到回调

* @note 通过 http 上传文件完成后,需要调用该接口确认完成,否则上传文件将无法在平台查询

到

```
*/
public abstract completeFileUpload(serialId: string, completeFileUploadPar
am: JRTCCompleteFileUploadParam): number;
/**
```

* 文件上传完成确认响应

```
*
* @param { number } operatorId 操作id,对应 {@link JRTCClient.completeFileU
pload completeFileUpload} 的返回值
* @param { boolean } result 请求是否成功
*                           - true:请求成功
*                           - false:请求失败
* @param { string } fileName 服务器合并后的文件名
* @param { string } extraInfo 随路参数
* @param { string } fileType 文件类型
* @param { string } reason 请求失败原因描述,当 result 为 false 时有效
*/
onCompleteFileUploadResponse?: (operatorId: number, result: boolean, fileN
ame: string, extraInfo: string, fileType: string, reason: string) => void;
```

示例代码

75

ArkTS

```
// 文件上传完成确认
const fileUploadParam = new JRTCCompleteFileUploadParam();
client.completeFileUpload("serialId", fileUploadParam);
// 文件上传完成确认响应
onCompleteFileUploadResponse: (operatorId: number, result: boolean, fileNa
me: string, extraInfo: string, fileType: string, reason: string) => {
  if (result) {
    // 处理上传成功的情况
  }
}
```

# 十一、屏幕共享

通过 Juphoon RTC SDK 可以在视频通话过程中实现屏幕共享,坐席可以将自己的屏幕内容,以视频的

方式分享给远端参会者,从而提升沟通效率,一般适用于一对一或多人视频通话、在线通话等在线金融

场景。

●

视频房间场景中,参会者可以在通话中将本地的文件、数据、网页、PPT 等画面分享给其他与会

者,让其他与会者更加直观的了解讨论的内容和主题。

●

在线金融场景中,坐席可以通过屏幕共享或者窗口共享将风险揭示等画面展示给远端的访客观看,

移动端访客也可将屏幕共享给坐席观看,提升沟通效率。

# 11.1 开启/关闭屏幕共享

76

ArkTS

```
  /**
```

   * 开启/关闭屏幕共享

```
   *
   * @param enable 开启或关闭屏幕共享
   *               - true: 开启屏幕共享
   *               - false: 关闭屏幕共享
   * @return 接口调用结果
   * - true: 接口调用成功
   * - false: 接口调用异常
   * @note 如果 {@link #setUseExternalScreenCaptureControl(boolean) setUse
ExternalScreenCaptureControl} 为 true,
```

   * 则该接口只负责信令通知,请确保开启屏幕共享前,已经开启了屏幕采集,否则远端用户收到

屏幕共享画面为黑屏

```
   */
  public abstract enableScreenShare( enable:boolean, sendScreenParam?:JRTC
SendScreenParam ):boolean;
```

开启/关闭屏幕共享通过实现JRTCCallCallback中的onCallPropertyChanged接口上报。

可通过getShareUserId获取当前正在屏幕共享的成员用户ID;

可通过getShareStreamId获取当前屏幕共享的视频流ID。

ArkTS

```
/**
```

* 获取屏幕共享时的视频流ID,无屏幕共享时为 undefined

```
* <p>
* 调用 {@link JRTCMediaDevice#startVideo startVideo} 接口渲染通话中其他成员的屏
```

幕共享画面时使用。

```
*
```

* @return 屏幕共享时的视频流ID

```
*/
public abstract getShareStreamId(): string;
/**
```

* 获取发起屏幕共享者的用户ID,无屏幕共享时为 undefined

```
* <p>
```

* 可用来判断当前通话中是否有成员发起屏幕共享。

```
*
```

* @return 发起屏幕共享者的用户ID

```
*/
public abstract getShareUserId(): string;
```

示例代码:

77

ArkTS

```
call.enableScreenShare(true);
1
```

# 11.2 共享视频采集

您可以调用JRTCMediaDevice类中的setScreenCaptureProperty方法设置屏幕共享采集属性,包括

采集的高度、宽度和帧速率。该方法可以在开启屏幕共享前调用,也可以在屏幕共享中调用;如果在屏

幕共享中调用,则设置的采集属性要在下次屏幕共享开启时生效。

ArkTS

```
/**
```

* 设置屏幕共享采集属性

```
*
* 在调用 {@link enableScreenCapture} 接口开启屏幕共享前设置即可生效
* @param { number } width 采集宽度,默认1280
* @param { number } height 采集高度,默认720
* @param { number } frameRate 采集帧速率,默认10
*/
public abstract setScreenCaptureProperty(width: number, height: number, fr
ameRate: number): void;
/**
```

* 开启/关闭屏幕采集

```
*
* @param { boolean } enable 是否开启
* @return { boolean } 开启/关闭是否成功
*/
public abstract enableScreenCapture(enable: boolean): boolean;
```

示例代码:

ArkTS

//开启/关闭采集

```
mediaDevice.enableScreenCapture(true);
```

# 11.3 暂停/恢复屏幕共享

78

ArkTS

```
/**
```

* 暂停/继续屏幕共享

```
*
* @param suspend true 暂停屏幕共享, false 继续屏幕共享
* @param tip     暂停屏幕共享后提示文字
* @return 接口调用结果
* - true: 接口调用成功, 会收到 {@link JRTCRoomCallback#onRoomPropertyChanged
onRoomPropertyChanged} 回调,可通过{@link #isSuspendScreenShare isSuspendScr
```

eenShare} 判断当前屏幕共享是否暂停

```
* - false: 接口调用异常
```

* @note 只有自己发起的屏幕共享可以使用该接口暂停,多次调用会覆盖

```
*/
public abstract suspendScreenShare(suspend: boolean, tip: string): boolea
n;
```

查询屏幕共享是否暂停

ArkTS

```
  /**
```

   * 是否屏幕共享暂停

```
   *
   * @return - true: 暂停屏幕共享
   * - false: 未暂停屏幕共享
   */
  public abstract isSuspendScreenShare(): boolean;
```

暂停/恢复屏幕共享变化事件通过实现JRTCCallCallback中的onCallPropertyChanged接口上报。

示例代码:

79

ArkTS

```
// 暂停屏幕共享
call.suspendScreenShare(true,"屏幕共享暂停中");
onCallPropertyChanged: (changeParam: JRTCRoomPropChangeParam | undefined)
=> {
 if (changeParam!.screenShare) {
    // 屏幕共享状态发生改变
    if(call.isSuspendScreenShare()) {
        // 屏幕共享暂停中
    }
  }
}
```

# 11.4 订阅/取消订阅屏幕共享的视频流

如果通话中有成员开启了屏幕共享,其他成员将收到onCallPropertyChanged的回调,并通过

getShareUserId获得发起屏幕共享的成员用户 ID。

ArkTS

```
/**
```

 * 通话属性改变,重点关注屏幕共享

```
 *
 * @param propChangeParam 通话改变的属性
 */
onCallPropertyChanged?: (propChangeParam: JRTCRoomPropChangeParam) => void;
```

此时可以调用requestScreenVideo方法请求订阅屏幕共享的视频流。

ArkTS

```
/**
```

* 订阅屏幕共享的视频流

```
*
* @param videoSize 视频请求的尺寸
* @return 接口调用结果
* - true: 接口调用成功
* - false: 接口调用异常
*/
public abstract requestScreenVideo(videoSize: JRTCVideoSize): boolean;
```

80

取消订阅屏幕共享的视频流,如果不需要屏幕共享视频流,此时可以调用unRequestScreenVideo方法

取消订阅屏幕共享的视频流,建议不使用时取消订阅屏幕共享的视频流,否则可能造成资源浪费。

ArkTS

```
/**
```

* 取消订阅屏幕共享的视频流

```
*
* @return 接口调用结果
* - true: 接口调用成功
* - false: 接口调用异常
*/
public abstract unRequestScreenVideo(): boolean;
```

# 11.5 渲染共享画面

获取屏幕共享相关参数getShareUserId和getShareStreamId

ArkTS

```
/**
```

* 获取屏幕共享时的视频流ID,无屏幕共享时为 undefined

```
* <p>
* 调用 {@link JRTCMediaDevice#startVideo startVideo} 接口渲染通话中其他成员的屏
```

幕共享画面时使用。

```
*
```

* @return 屏幕共享时的视频流ID

```
*/
public abstract getShareStreamId(): string;
/**
```

* 获取发起屏幕共享者的用户ID,无屏幕共享时为 undefined

```
* <p>
```

* 可用来判断当前通话中是否有成员发起屏幕共享。

```
*
```

* @return 发起屏幕共享者的用户ID

```
*/
public abstract getShareUserId(): string;
```

屏幕共享开始/结束均通过实现onCallPropertyChanged接口上报。

示例代码:

81

ArkTS

```
onCallPropertyChanged: (changeParam: JRTCRoomPropChangeParam | undefined) =
> {
  if (changeParam?.screenShare) {
    if (room.getShareUserId() !== undefined && room.getShareStreamId().leng
th > 0) {
      // 屏幕共享打开,可通过guest.getShareStreamId 渲染共享视频画面
    }else {
      // 屏幕共享关闭,可停止渲染共享视频画面
    }
  }
}
```

# 十二、音视频录制

在开展在线理财、开户、面签等业务时,应国家监管要求,必须提供录音录像服务,形成交易记录

的视频,存档备查。

Juphoon RTC SDK 在音视频通话过程中,支持全程进行实时的服务器录制或本地录制,录制的场

景画面覆盖座席画面和所有终端类型的访客画面,按需可支持多摄像头、多屏幕合成录制,满足用户记

录业务办理全过程录制的需求。

# 12.1 本地录制

本地录制支持实时的通话过程音频录制,录制文件保存在用户本地设备中,适用于通话过程录音录像场

景等其他音视频相关场景。优点不受网络影响,录制画面质量高,减少带宽压力。

录制通话在本地生成视频文件。

82

ArkTS

```
/**
```

* 开启/关闭本地录制

```
*
* @param enable      开启或关闭本地录制
*                    - true: 开启本地录制
*                    - false: 关闭本地录制
* @param recordParam 本地录制参数配置,当 enable == true 时,{@link JRTCRecord
LocalParam#filePath} 必须设置,其余参数不设置则使用默认配置;当 enable == false
时,recordParam 可传 undefined
* @return 接口调用结果
* - true: 接口调用成功
* - false: 接口调用异常
```

* @note 确保调用接口前本地录制文件所在目录已经存在,否则会录制失败

```
* @see JRTCRecordLocalParam
*/
public abstract enableLocalRecord(enable: boolean, recordParam: JRTCRecord
LocalParam | undefined): boolean;
/**
```

* 获取是否正在本地录制

```
*
```

* @return 是否正在本地录制

```
* - true: 本地录制中
* - false: 未进行本地录制
*/
public abstract isLocalRecording(): boolean;
```

本地录制参数详见JRTCRecordLocalParam。

示例代码:

83

ArkTS

```
let param: JRTCRecordLocalParam = new JRTCRecordLocalParam();
param.recVideo = true;//设置是否录制视频
param.recAudio = true;//设置是否录制音频
param.includeSelf = true;//设置录制是否包含自己
param.mergeMode = JRTCVideoMergeMode.INTELLIGENT_LAYOUT;//设置媒体录制视频合
```

并模式,默认智能分屏模式,当使用配置文件时,该参数无效

```
param.intelligentMergeMode = JRTCIntelligentMergeMode.FREE_LAYOUT;//智能分
屏模式下的布局样式(无屏幕共享)
param.scsMergeMode = JRTCScsMergeMode.SCREEN_SHARE;//智能分屏模式下的布局样式
```

(有屏幕共享)

```
param.frameRate = 18;//设置录制帧率,默认15
param.iBitrate = 0;//设置录制码率
param.videoWidth = 640;//设置录制视频的宽度
param.videoHeight = 360;//设置录制视频的高度
param.filePath = "";//设置保存的文件路径
```

更新本地录制自定义布局updateLocalRecordLayout,当本地录制已经在进行时,可以通过该接口实时

更新本地录制布局

ArkTS

```
/**
```

* 更新本地录制自定义布局

```
*
* @param layoutList 需要更新的布局列表
* @return 接口调用结果
* - true: 接口调用成功
* - false: 接口调用异常
*/
public abstract updateLocalRecordLayout(layoutList: ArrayList<JRTCRecordLoc
alLayout>): boolean;
```

示例代码:

84

ArkTS

```
let layoutList:ArrayList<JRTCRecordLocalLayout> = new ArrayList();
let layout1:JRTCRecordLocalLayout = new JRTCRecordLocalLayout();
layout1.setId("streamId0",false);
layout1.position = 0;
layoutList.add(layout1);
let layout2:JRTCRecordLocalLayout = new JRTCRecordLocalLayout();
layout1.setId("streamId1", false);
layout1.position = 1;
layoutList.add(layout2);
call.updateLocalRecordLayout(layoutList);
```

通过配置文件实现本地录制

流程图如下

导出录制配置文件

加入房间,发送流,订阅流

配置录制参数

1.导入配置文件 - 必选

2.配置是否录制音视频,是否录制自己

3.设置占位符内容 - 可选

4.配置每个流在布局中的位置 - 可选

开启录制

结束录制

本地录制配置文件示例如下:

85

ArkTS

```
{
  "default" : {   //录制配置类型, 固定值.
    "videoRecord" : {   //视频录制配置, 固定值.
      "layout" : [        //自定义布局,mergeMode 字段为自定义布局模式 {@link J
RTCVideoMergeMode#CUSTOM_LAYOUTCUSTOM_LAYOUT(4)} 时生效, JSON数组格式, 可同时
```

设置多个, 实际应用时通过窗口号区分.

```
        {
          "posX" : 0.25,                  //画面左上角的横坐标(双精度浮点数类
```

型), 代表占画面总宽度的比例.

```
          "posY" : 0.26805556000000003,   //画面左上角的纵坐标(双精度浮点数类
```

型), 代表占画面总高度的比例.

```
          "width" : 0.1140625,            //画面的宽度(双精度浮点数类型), 代表
```

占画面总宽度的比例.

```
          "height" : 0.47916666000000002, //画面的高度(双精度浮点数类型), 代表
```

占画面总高度的比例.

```
          "window" : 0                    //窗口号(大于或等于的整数), 在使用
{@link RecordLayout#setLayoutList(List) setLayoutList} 自定义视频窗口布局时需
要, 对应于用户自定义的位置信息 {@link RecordLayout#setPosition(int)} setPositi
```

on} 设置布局位置.

```
        },
        {
          "posX" : 0.49609375,            //画面左顶点的横坐标(双精度浮点数类
```

型), 范围为[0, 1], 代表占画面总宽度的比例.

```
          "posY" : 0.033333334999999999,  //画面左顶点的纵坐标(双精度浮点数类
```

型), 范围为[0, 1], 代表占画面总高度的比例.

```
          "width" : 0.36406250000000001,  //画面的宽度(双精度浮点数类型), 范围
```

为[0, 1], 代表占画面总宽度的比例.

```
          "height" : 0.94027775999999996, //画面的高度(双精度浮点数类型) 范围为
```

[0, 1], 代表占画面总高度的比例.

```
          "window" : 1                    //窗口号(大于或等于的整数), 在使用
{@link RecordLayout#setLayoutList(List) setLayoutList} 自定义视频窗口布局时需
要, 对应于用户自定义的位置信息 {@link RecordLayout#setPosition(int)} setPositi
```

on} 设置布局位置.

```
        }
      ],
        "mergeBitrate" : 0, //设置录制视频的码率, 单位为千比特每秒(kbps), 默认值
```

为0, 此时码率由内部媒体算法进行自适应调节

```
        "mergeFPS" : 30,    //设置录制视频的帧率, 单位为每秒传输帧数(fps), 默认值
为20.
        "mergeWidth" : 1280,//设置录制视频的宽度, 默认值为 640
        "mergeHeight" : 720,//设置录制视频的高度, 默认值为 360
        "mergeMode" : 4,    //设置媒体推流的视频合并模式, 默认值为 {@link JRTCV
ideoMergeMode#INTELLIGENT_LAYOUT INTELLIGENT_LAYOUT(5)}, 目前可支持自定义布
局 {@link JRTCVideoMergeMode#CUSTOM_LAYOUTCUSTOM_LAYOUT(4)} 和智能布局 {@lin
k JRTCVideoMergeMode#INTELLIGENT_LAYOUT INTELLIGENT_LAYOUT(5)}.
```

86

```
```

        "mergeModeI" : 1,   //设置智能分屏模式下的布局样式(无屏幕共享), 默认值为

```
自由布局 {@link JRTCIntelligentMergeMode#FREE_LAYOUT FREE_LAYOUT(1)}, 有效值
参考 {@link JRTCIntelligentMergeMode. 智能分屏模式下的布局样式(无屏幕共享)}, 本
字段仅在 mergeMode 为智能布局 {@link JRTCVideoMergeMode#INTELLIGENT_LAYOUT IN
TELLIGENT_LAYOUT(5)} 时生效.
```

        "screenShareType" : 1 //设置智能分屏模式下的布局样式(有屏幕共享), 默认值

```
为屏幕共享独占 {@link JRTCScsMergeMode#SCREEN_SHARE SCREEN_SHARE(1)}, 有效值
```

参考 {@link JRTCScsMergeMode 智能分屏模式下的布局样式(有屏幕共享)}, 本字段仅在 m

```
ergeMode 为智能布局 {@link JRTCVideoMergeMode#INTELLIGENT_LAYOUT INTELLIGEN
T_LAYOUT(5)} 时生效.
    },
    "watermark" : { //水印配置, 固定值.
      "picture" : [   //图片水印配置, 固定值, 图片水印目前只支持 png 格式.
        {
          "enable" : true,    //是否启用(布尔类型).
          "pcUrl" : "http://192.168.17.60:10042/protected_files/6afa960e-f
e4a-49ae-a939-48c788122192?attname=juphoon.png",    //图片水印链接地址.
          "index" : 1,        //水印的序号.
          "state" : 1,        //水印的状态. 设置值为1表示使用水印,设置值为2表示
```

关闭水印.

```
          "posX" : 0,         //相对于基准位置的水平偏移值(整数类型), 负值向左偏
```

移, 正值向右偏移, 实际大小非比例值.

```
          "posY" : 600        //相对于基准位置的垂直偏移值(整数类型), 负值向上偏
```

移, 正值向下偏移, 实际大小非比例值.

```
        }
      ],
        "text" : {  //文本水印配置, 固定值.
        "enable" : true,    //是否启用(布尔类型).
          "memo" : [          //文本水印样式配置(JSON数组类型), 如果不设置就使用
```

默认全局样式.

```
          "Dialogue: 0,0:00:00.0,60:00:00.0,Default,,0,0,0,,{\\pos(34, 56)
\\an7}菊风文本水印1$@name@$",
          "Dialogue: 0,0:00:00.0,60:00:00.0,Default,,0,0,0,,{\\pos(50, 10
0)\\an7}菊风文本水印2"
```

          //数组的每个元素为一条 ASS 字幕的 event 字符串, 支持通过标签来设置各种文字

特效, 添加的event字符串必须是utf-8编码, 否则中文会出现乱码. ASS 格式规范下载地址: ht

```
tp://www.perlfu.co.uk/projects/asa/ass-specs.doc
          //其中以 "$@" 开始并且以 "@$" 结束的部分内容"$@name@$"将提取出关键字"na
me", 通过解析用户通过 {@link #setWatermarkTextMap(Map) setWatermarkTextMap}
```

设置的自定义文本水印信息获取其对应值, "$@name@$"格式的内容被其对应值替换后就是实际应用

的 event 字符串, "$@xxx@$" 格式的内容支持同时设置多个.

```
        ],
          "style" : {         //文本水印格式, 固定值.
          "enable" : true,        //格式是否启用(布尔类型).
            "alignment" : 0,        //对齐方式, 有效值参考 0:左对齐;1:居中对
齐;2:右对齐;
            "backColor" : 16777215, //背景颜色(整数类型), 10进制颜色代码.
            "blod" : false,         //是否使用粗体(布尔类型).
```

87

```
            "fontColor" : 16777215, //字体颜色(整数类型), 10进制颜色代码.
            "fontFile" : "SourceHanSansCN-Normal.otf",//字体文件路径,Window
```

s系统上只能用相对路径(相对配置文件所在路径),不可以带盘符,建议和配置文件放在同个目录

下.

```
            "fontSize" : 36,        //字体尺寸(整数类型).
            "italic" : true,        //是否使用斜体(布尔类型).
            "underline" : false     //是否带有下划线(布尔类型).
        }
      },
      "timestamp" : { //时间戳水印配置, 固定值.
        "enable" : true,    //是否启用(布尔类型).
          "basePosType" : 0,  //水印基准位置类型(整数类型), 有效值参考 0:左上;
1:左下;2:右上;3:右下;4:居中;
          "borderWidth" : 2,  //字体边界宽度(整数类型), 取值范围为[0, 5].
          "fontFile" : "SourceHanSansCN-Normal.otf",//字体文件路径,Windows
```

系统上只能用相对路径(相对配置文件所在路径),不可以带盘符,建议和配置文件放在同个目录下.

```
          "fontColor" : 0, //字体颜色(整数类型), 有效值参考 0:红色;1:黄色;2:
绿色;3:青色;4:蓝色;5:洋红色;6:白色;7:中和色;8:黑色;
          "fontSize" : 36,    //字体尺寸(整数类型).
          "isMs" : true,      //是否显示毫秒值(布尔类型).
          "posX" : 0,         //相对于基准位置的水平偏移值(整数类型), 负值向左偏
```

移, 正值向右偏移, 实际大小非比例值.

```
          "posY" : 0          //相对于基准位置的垂直偏移值(整数类型), 负值向上偏
```

移, 正值向下偏移, 实际大小非比例值.

```
      }
    }
  }
}
```

配置样例文件(不带注解):

📎record.cfg.zip

# 12.2 本地录制(不需要建立通信)

视频录制参数详见: JRTCRecordVideoCaptureParam

88

| ArkTS |  |
|---|---|
|  |  |
| 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 | /** * 开启视频录制(本地录制,不需要建立通信,不能和音频录制 {@link startAudioRecord st artAudioRecord} 同时开启) * * @param { string } streamId 视频流ID, (包括摄像头ID、文件视频源ID、屏幕采集流ID 等) * @param { JRTCRecordVideoCaptureParam } recordParam 录制参数 * @return { boolean } 接口调用结果 * - true: 接口调用成功 * - false: 接口调用异常 */ public abstract startVideoCaptureRecord(streamId: string, recordParam: JRT CRecordVideoCaptureParam): boolean; /** * 关闭视频录制(本地录制,不需要建立通信) * * @param { string } streamId 视频流ID (包括摄像头ID、文件视频源ID、屏幕采集流ID 等) |
| 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 |  |

```
public abstract stopAudioRecord(): boolean;
```

录制水印(目前不支持):本地录制支持图片、文字、时间戳水印,通过录制参数设置,详见:Image

Text TimeStamp

示例代码:

ArkTS

```
// 打开摄像头
mediaDevice.startCamera();
// 打开麦克风
mediaDevice.startAudioInput();
let param: JRTCRecordVideoCaptureParam = new JRTCRecordVideoCaptureParam
();
param.filePath = "filePath";
param.audioSource = JRTCMediaDeviceRecordAudioSource.FROM_MICROPHONE;
param.fileType = JRTCMediaDeviceVideoRecordFileType.MP4_H264;
param.width = 640
param.height = 340
mMediaDevice.startVideoCaptureRecord(mMediaDevice.getCurrentCamera()!.came
raId!, param)
// 开启本地音频录制
mediaDevice.startAudioRecord("/sdcard/1.wav",param.audioSource, param.file
Type);
// 关闭本地音频录制
mediaDevice.stopAudioRecord();
```

# 12.3 远程录制

在线上金融的应用场景中,考虑取证、质检、审核、存档和回放等需求,常需要将整个视频通话过

程录制,并存储。

Juphoon RTC SDK 的远程录制,通过会场服务将收到的所有终端数据发送给录制服务器,进行实

时录制。在实际的集成中,当 SDK 初始化完成后,集成方通过加入会场的方式将需要进行录制的音视频

流上传至服务器并进行实时录制。

## 12.3.1 开启/关闭远程录制

访客在发起呼叫的时候可以携带JRTCCallCenterCallParam.autoRecord参数来设置是否在通话开始后

就进行远程录制。

90

如果该次通话没有设置自动远程录制,则可以通过终端来触发录制,在服务端形成通话过程的视频文

件。

录制的配置(如水印、时间戳等)与自动录制的相同,都来自系统管理平台后台的配置。

ArkTS

```
/**
```

* 开启/关闭远程视频录制

```
*
* 当呼叫参数 {@link JRTCCallCenterCallParam#autoRecord autoRecord} == fals
```

e 时,可通过此接口开启服务端录制。

```
* 可用过 {@link #getRemoteRecordState} 接口获取当前服务器录制状态。
* @param enable 开启或关闭视频录制
* - true: 开启视频录制
* - false: 关闭视频录制
* @param recordParam 录制参数,当 enable == false 时,可传 undefined;当 enabl
e == true 且按照默认配置进行录制可传 undefined
* @return 接口调用结果
* - true: 接口调用成功,录制状态通过 {@link JRTCGuestCallback#onCallPropertyCh
anged onCallPropertyChanged} 回调获得,具体可关注 {@link JRTCRoom.PropChangeP
aram#remoteRecordState remoteRecordState}
* - false: 接口调用异常
*/
public abstract enableRemoteRecord(enable: boolean, recordParam: JRTCRecor
dRemoteParam): boolean;
```

注意:该远程录制接口不经过排队机服务。

远端录制参数详见JRTCRecordRemoteParam。

录制状态改变通过onCallPropertyChanged回调通知到访客。

通话属性改变详见JRTCRoomPropChangeParam,录制状态具体可关注getRemoteRecordState。

ArkTS

```
/**
```

* 通话属性改变回调

```
* @note
* 重点关注屏幕共享,即当{@link PropChangeParam#screenShare screenShare} 属性为
```

true 时,去处理屏幕共享相关事件。

```
* 可根据 {@link JRTCGuest#getShareStreamId shareRenderId} 和 {@link JRTCGues
t#getShareUserId shareUserId} 属性进行屏幕共享画面的渲染和停止渲染。
* @param propChangeParam 通话改变的属性
*/
onCallPropertyChanged?: (propChangeParam: JRTCRoomPropChangeParam) => void;
```

91

示例代码:

ArkTS

```
let param:JRTCRecordRemoteParam = new JRTCRecordRemoteParam();
param.recordVideo = true
...
let map:HashMap<string,string> = new HashMap()
map.set("guest","juphoon001")
param.watermarkTextMap = map
if (guest.getRemoteRecordState() == JRTCRemoteRecordState.READY) {
  //开启远程录制
  call.enableRemoteRecord(true, param);
}
//关闭远程录制
call.enableRemoteRecord(false, new JRTCRecordRemoteParam());
//远程录制状态发生改变
onCallPropertyChanged: (propChangeParam: JRTCRoomPropChangeParam) => {
  if (propChangeParam.recordState) {
    if (call.getRemoteRecordState == JRTCRemoteRecordState.RUNNING) {
      //当前正在远程录制
    }
  }
}
```

## 12.3.2 远程录制异常回调

详见onDeliveryAbort。

92

ArkTS

```
/**
```

* 录制异常回调

```
* <p>
```

* 远程录制异常退出时会上报此回调。

```
*
```

* @param isShutDown  录制异常时服务器是否自动结束通话

```
*                    - true: 自动结束通话
*                    - false: 不自动结束通话
* @param deliveryUserId 录制异常的用户ID
* @param reason      录制异常的原因
* @param room        当前 JRTCRoom 对象
*/
onDeliveryAbort?: (isShutDown: boolean, deliveryUserId: string, reason: st
ring) => void;
```

## 12.3.3 水印

开启服务器音视频录制接口,支持配置文字水印,录制完成后视频保存于服务端。

Juphoon RTC SDK 支持以下三种画布水印设置:

●

文字水印:使用一段文字信息作为水印,支持设置字体和字号。

●

动态时间戳水印:使用当前时间戳作为水印,显示格式为“2021-03-18 14:30:35"。

●

静态图片水印:使用图片作为水印。

12.3.3.1 注意事项

●

其中自定义水印内容通过JRTCRecordRemoteParam对象watermarkTextMap方法配置,服务端

进行录制时将会把水印内容中的占位符替换成键值对中占位符对应Key的Value值。

ArkTS

```
/**
```

* 设置录制视频水印串

```
*/
public set watermarkTextMap(watermarkTextMap: HashMap<string, string> | und
efined);
```

12.3.3.2 添加、修改或删除水印

●

文字水印,如要求水印内容需具备客户经理工号、姓名、地理位置、经纬度;则需要终端开启录制

时通过watermarkTextMap设置: {"userInfo": "工号+姓名"} 、{"location":"地理位置"}、

{"JWD": "经纬度"}这样的键值对;具体体现和系统管理平台端配置如下 ,红框内就是文字水印,支持

在业务管理平台调整位置和字体颜色等,而$@xxx@$最终会替换成键xxx对应的值,如

$@userInfo@$,替换成“工号+姓名”,$@location@$,替换成“地理位置”,$@JWD@$,替换

成“经纬度”。

●

图片水印,在业务管理平台支持配置图片水印,目前知支持 png 格式图片,可以自由调整位置。

●

时间戳水印,在业务管理平台支持配置时间戳水印,可以自由调整位置,字体颜色、大小等。

## 12.3.4 自定义布局

在系统管理平台端中的录制配置目录下,可以配置录制的一些参数,为了录制布局更加灵活,还提供了

自定义布局,自定义布局可以配置每个录制流的位置和大小。

系统管理平台端默认使用的是智能分屏,如需切换自定义布局,在系统管理平台端修改如下:

配置每个成员的布局位置和大小,配置完成后点保存:

图中的0,1表示每个窗口对应的窗口位置,终端开启远程录制绑定视频流和窗口位置需要用到。

以上就是系统管理平台端的配置,实现自定义布局还需要在代码中绑定对应的窗口位置,参考代码如下:

ArkTS

```
let param:JRTCRecordRemoteParam = new JRTCRecordRemoteParam();
param.frameRate = 24;
param.iBitrate = 500;
// 设置录制合并模式为自定义布局模式
param.mergeMode = JRTCVideoMergeMode.CUSTOM_LAYOUT;
param.videoWidth = 640;
param.videoHeight = 360;
param.recordVideo = true;
```

param.layoutType = "default";//设置录制样式,对应业务管理平台上录制配置中的编号I

D, 不传则用默认

// 开启远程录制

```
call.enableRemoteRecord(true, param);
```

## 12.3.5 更新远程录制自定义布局

如果需要在远程录制已经开启的情况下更改录制布局,使用场景:比如录制中有新成员加入,需要调整

布局位置,可以使用如下接口,需要在远程录制进行中调用,详见: updateRemoteRecordLayout

96

ArkTS

```
/**
```

* 更新远程录制自定义布局

```
*
* @param layoutList 需要更新的布局列表
* @return 接口调用结果
* - true: 接口调用成功
* - false: 接口调用异常
*/
public abstract updateRemoteRecordLayout(layoutList: ArrayList<JRTCRecordRe
moteLayout>): boolean;
```

示例代码:

ArkTS

```
let param:JRTCRecordRemoteParam = new JRTCRecordRemoteParam();
```

// ......远程录制参数设置

// 开启远程录制

```
call.enableRemoteRecord(true, param);
let layoutList:ArrayList<JRTCRecordRemoteLayout> = new ArrayList();
let layout:JRTCRecordRemoteLayout = new JRTCRecordRemoteLayout();
layout.setId("成员用户ID", true);
// 设置系统管理平台中对应的窗口位置
layout.position = 0;
layoutList.add(layout);
```

//......设置其他成员视频流或者屏幕共享流对应窗口位置

//更新录制自定义布局

```
let result:boolean = call.updateRemoteRecordLayout(layoutList);
// 关闭远程录制
call.enableRemoteRecord(false, new JRTCRecordRemoteParam());
```

## 12.3.6 更新远程录制水印信息

如果需要在远程录制已经开启的情况下更改水印信息,使用场景:比如录制中有成员离开,需要修改该

成员原先位置水印标签(可能是用户名字),可以使用如下接口,需要在远程录制进行中调用,详见:

updateRemoteRecordWatermark

97

ArkTS

```
/**
```

* 更新远程录制水印信息

```
*
* @param watermarkTextMap 水印信息
* @return 接口调用结果
* - true: 接口调用成功
* - false: 接口调用异常
*/
public abstract updateRemoteRecordWatermark(watermarkTextMap: HashMap<strin
g, string>): boolean;
```

示例代码:

ArkTS

```
let param:JRTCRecordRemoteParam = new JRTCRecordRemoteParam();
let watermarkTextMap1:HashMap<string, string> = new HashMap();
watermarkTextMap1.set("w1", "张三");
watermarkTextMap1.set("w2", "李四");
param.watermarkTextMap = watermarkTextMap1;//初始水印
```

// ......远程录制参数设置

// 开启远程录制

```
call.enableRemoteRecord(true, param);
let watermarkTextMap2:HashMap<string, string> = new HashMap();
watermarkTextMap2.set("w1", "李四");//修改水印信息
watermarkTextMap2.set("w2", "王五");//修改水印信息
let result:boolean = call.updateRemoteRecordWatermark(watermarkTextMap
```

2);//更改录制水印信息

// 关闭远程录制

```
call.enableRemoteRecord(false, new JRTCRecordRemoteParam());
```

# 十三、加密传输

为了建立安全通道,就是通信双方建立连接通道后,在这个通道中传递的信息不可被第三方窃取,

或者即使窃取后,也不能识别信息内容。但是仅通信双方建立安全通道是不够的,还需要进行合法性确

认。

通常终端的合法性是基于用户名密码实现的,即服务器通过客户端提交的用户名和密码来进行鉴权,确

认此用户的合法性。

98

在建立安全通道以及身份合法性验证后,后续大量的信息交互需要高效率的加密和解密,通常我们会使

用对称加密方式进行处理。

# 13.1 国密加密

●

国密 SM4 分组密码算法是我国自主设计的分组对称密码算法,用于实现数据的加密/解密运算,以

保证数据和信息的机密性。

●

要保证一个对称密码算法的安全性的基本条件是其具备足够的密钥长度,SM4 算法与 AES 算法具

有相同的密钥长度分组长度128比特,因此在安全性上高于 3DES 算法。

在登录的接口参数里设置 CA 证书(Certificate)和账户分录(AccountEntry)。

通过certificate设置 Base64 编码后的证书字符串,通过accountEntry设置账户分录。

示例代码:

ArkTS

```
const loginParam: JRTCClientLoginParam = new JRTCClientLoginParam();
loginParam.certificate = "证书内容";
// 用户登录
client.login("juphoon", "123456", loginParam);
```

在加入会话房间时设置加密方式为 JRTCRoomSecurityType.SM4。

示例代码

ArkTS

```
let callJoinParam: JRTCCallJoinParam = new JRTCCallJoinParam();
callJoinParam.securityType = JRTCRoomSecurityType.SM4
mCall.join("10086", callJoinParam);
```

# 13.2 Token 校验

Token 认证服务,主要用于登录时 token 验证,由第三方服务获取 token,将 token 下发给集成的终

端,由 SDK 发起登录时带上 token ,进行认证。

详见token 流程介绍。

允许用户登录时,带入 token 。如果未使用,可以不带。

99

ArkTS

```
/**
```

* 登录 Juphoon RTC 平台,只有登录成功后才能进行平台上的各种业务

```
* <p>
* 登录结果通过 {@link JRTCClientCallback.onLogin onLogin} 回调通知
*
* @param { string } userId 用户ID
* @param { string } password 密码,不能为空
* @param { JRTCClientLoginParam? } clientLoginParam 登录参数,一般不需要设置,
```

如需设置请询问客服,传 undefined 则按默认值

```
* @return { boolean } 接口调用结果
```

*  - true:接口调用成功

*  - false:接口调用异常

* @warning 目前只支持免鉴权模式,服务器不校验账号密码,免鉴权模式下当账号不存在时会自动

去创建该账号

```
* @warning 用户名为英文数字和'+' '-' '_' '.',长度不要超过64字符,'-' '_' '.'不能
```

作为第一个字符

```
*/
public abstract login(userId: string, password: string, clientLoginPara
m?: JRTCClientLoginParam): boolean;
```

示例代码

ArkTS

```
let loginParam:JRTCClientLoginParam = new JRTCClientLoginParam();
loginParam.tokenType = "token校验类型";
loginParam.token = "token字符串";
client.login("userId", "密码", loginParam)
```

# 十四、视频多流

SDK 提供了可以自行创建/删除视频流通道的接口

使用场景举例:鉴于目前的房间模式只能由一人发起屏幕共享,当多个成员想在同个房间内发起屏幕共

享时,可以使用该接口实现。

100

ArkTS

```
/**
```

 * 创建额外视频流

```
 *
 * @param captureStreamId 本地视频流采集源流Id
```

 * @param screenShare     是否屏幕共享(包括窗口共享、区域共享)

```
 * @return 通话中的视频流ID  创建成功后,通话内其他成员将收到 {@link JRTCRoomCall
back#onParticipantUpdate} 回调
 */
public abstract createExtraStream(captureStreamId: string, screenShare: bo
olean): string | undefined;
/**
```

 * 删除额外视频流

```
 *
 * @param captureStreamId 本次视频流采集源流Id
 * @return 接口调用结果
 * - true: 接口调用成功,通话内其他成员将收到 {@link JRTCRoomCallback#onPartici
pantUpdate} 回调
 * - false: 接口调用异常
 */
public abstract deleteExtraStream(captureStreamId: string): boolean;
```

订阅/取消订阅额外视频流

101

ArkTS

```
/**
```

 * 订阅房间中其他用户的额外视频流

```
 *
 * @param participant  JRTCRoomParticipant 成员对象
 * @param streamId     视频流ID
 * @param videoSize    视频请求的尺寸
 * @return 接口调用结果
 * - true: 接口调用成功
 * - false: 接口调用异常
 */
public abstract requestExtraStreamVideo(participant: JRTCRoomParticipant,
streamId: string,
  videoSize: JRTCVideoSize): boolean;
/**
```

 * 取消订阅房间中其他用户的额外视频流

```
 *
 * @param participant  JRTCRoomParticipant 成员对象
 * @param streamId     视频流ID
 * @return 接口调用结果
 * - true: 接口调用成功
 * - false: 接口调用异常
 */
public abstract unRequestExtraStreamVideo(participant: JRTCRoomParticipan
t, streamId: string): boolean;
```

示例代码(以屏幕共享举例):

102

ArkTS

```
```

//发起端

//开启本地屏幕采集

```
mediaDevice.enableScreenCapture(true);
onScreenSharePermissionResult(result: boolean): void {
    if (result) {
      //创建视频额外流通道,将本地屏幕采集流id绑定到该通道
      let callStreamId:string = call.createExtraStream(mediaDevice.getScre
enCaptureId(), true);
      if (!TextUtils.isEmpty(callStreamId)) {
          //开启多流屏幕共享成功
      } else {
          //开启多流屏幕共享失败
      }
  }
}
//删除视频额外流通道
call.deleteExtraStream(mediaDevice.getScreenCaptureId());
//关闭本地屏幕采集
mediaDevice.enableScreenCapture(false);
onParticipantUpdate: (participant: JRTCRoomParticipant,changeParam: JRTCRo
omParticipantChangeParam) => {
 if (changeParam.extraStream) {
    //判断不是本端发起的多流
    if (participant.userId != JRTCManager.getInstance().client.getUserId
()) {
      //遍历新增的视频流
      for (const stream of changeParam.addedExtraStreams) {
        //订阅该视频流
        call.requestExtraStreamVideo(participant, stream, new JRTCVideoSiz
e(1280, 720));
      }
      this.updateVideoUi();
      //删除额外流不为空
      if (changeParam.removedExtraStreams.length > 0 ) {
        //遍历移除的视频流
        for (const stream of changeParam.removedExtraStreams) {
```

          //这里不需要去取消订阅

          //可有将该视频画面从到视图容器移除

```
        }
      }
    }
```

103

```
  }
}
```

104
