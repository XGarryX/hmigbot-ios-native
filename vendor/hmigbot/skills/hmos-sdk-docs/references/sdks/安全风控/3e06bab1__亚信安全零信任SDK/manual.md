零信任 SDP 移动终端( SDK )安全隧道接入方案 V1.5 

# 1. 项目背景 

# 1.1 项目背景 

移动办公是指办公人员可在任何时间、任何地点处理与业务相关的任 何事情,例如家庭办公、出差员工远程办公。这种全新的办公模式, 可以让办公人员摆脱时间和空间的束缚,单位信息可以随时随地通畅 地进行交互流动,工作将更加轻松有效,整体运作更加协调。随着国 内网络发展的日益成熟,移动办公越来越受到企业的亲睐。 

由于移动办公要经过开放的 Internet 接入企业的内部网,由此移动办 公使用的首要问题就是移动办公的安全问题。在网络安全威胁日益严 重的今天,移动办公系统的安全更是一个不容忽视的重要问题。如何 保证企业网络和信息的安全,也是用户最关心的一个问题。 

手机安全隧道建设主要完成部署移动终端实现移动办公环境下安全隧 道接入企业内网;实现系统架构整体优化,提高系统的兼容性、安全 性,以满足企业日常移动办公需要。 

“ ” 实现 移动办公 移动应用安全隧道安全接入,保障移动应用的安全接 入和数据的安全传输。 

# 1.2 需求说明 

# 1.2.1 传输安全 

业务系统不暴露在互联网上直接访问,需要访问的人员需要通过安全 认证后才能接入,访问指定的业务系统,且访问过程中全程加密,防 止数据被窃取。 

# 1.2.2 权限隔离 

能提供权限梳理工具来帮助梳理静态权限,提供信任引擎来基于身份 实现细粒度的动态权限管控; 

权限梳理工具梳理后,能多种方式分配应用系统权限(智能分配或手 动分配) 

# 1.2.3 移动端终端访问 

支持 Android/iOS/ 鸿蒙移动终端接入,访问公司业务系统。 

# 1.2.4 认证安全 

使用用户名 + 密码认证,保障接入终端身份可靠。 

1.2.5 审计安全 

日志要求记录并保存不少于六个月。 

# 1.3 设计目标 

使用移动设备来完成工作已成为一种新常态,远程工作者经常连接到 未知的、共享的或公共的网络来完成这些任务,这使得能随时随地安 全访问公司资源成为必要,也给终端安全带来了新的挑战。这种转变 使管理员需要在努力确保最大的数据安全性的同时,保持员工的工作 效率。 

# 1.3.1 移动终端的接入 

使用员工在访问其移动设备上的公司数据时都使用安全隧道连接,不 可避免的网络故障会导致与服务端的连接失败,并且无法确保在网络 连接恢复后可以重新建立 VPN 连接。员工不会察觉自己的服务端已经 断开,这可能会威胁到传输中敏感信息的安全性,其中需要解决以下 可能存在的安全性问题。 

安全隧道:代理网关架设在用户与业务系统之间,将 B/S 业务系统从 HTTP 转换成 HTTPS ;对于 C/S 会建立 SSL 加密隧道,防止局域网利用 嗅探技术窃取他人会话信息,利用他人的会话身份窃取信息和篡改数 据的风险。 

未经授权地访问:提供基于应用授权的细粒度访问权限控制,让用户 只能访问同一台 Web 服务器上的有限页面,防止非法接入用户找到 SQL 注入漏洞页面;同时支持按组织、标签、角色、用户等分配访问 权限,给客户多种权限分配,让用户按需配置各种应用的访问权限, 提高安全性。 

加密算法有效性:根据不同业务的安全级别,提供 AES 、 SHA 、 RSA 、 RC4 、 GCM 、 ECDSA 、 MD5 进行选择,保障数据的安全性。 

隧道维持:在用户通过安全隧道下载上传文件时,保持安全隧道连 接,不被移动 

系统回收。 

# 2. 系统架构 

# 2.1 网络拓扑 

# 2.2 主要数据说明 

敲门标识: SPA 敲门成功后由控制中心返回给 SDK 的标识,用于通过 认证端口继续认证 

会话标识:登录流程完全结束后,由控制中心返回给 SDK 的标识,用 于标识本次登录会话,后续用于校验访问隧道资源的合法性。 

# 3. 接入流程 

# 3.1 登录认证 

用户使用账号 + 静态密码的方式进行认证登录,账号和密码保存在 SDP 本地或者第三方认证中心, SDP 控制中心和第三方认证中心进行 对接,实现用户登录认证流程。 

# 3.1.1 流程图 

# 3.1.2 流程说明 

用户在移动端 APP 上打开登录界面,输入用户名和密码以及认证模式 移动端 APP 调用 SDP-SDK ,提供认证模式 

SDK 携带账号密码调用 SDP 控制中心进行敲门认证 

SDP 控制中心识别控制模式,不在本地认证,而是转至第三方认证中 心进行密码认证 

第三方认证中心校验账号和密码 

“ ” 第三方认证中心返回认证结果,此处以 成功 说明流程 

SDP 控制中心生成敲门标识,返回给 SDK 

SDK 携带敲门标识进行上线登录 

SDP 控制中心校验敲门标识的正确性, 

# 3.2 隧道创建 

登录认证成功后, SDP 需要在移动端系统内创建安全隧道,安全隧道 创建根据系统的差别耗时时间不定,所以需要有通知机制。 

# 3.2.1 流程图 

前置条件:已经登录认证成功 

# 3.2.2 流程说明 

前置条件:已经登录认证成功 

SDP-SDK 根据控制中心返回结果设置路由表、设置 DNS 

SDP-SDK 设置虚拟网卡、启动虚拟网卡 

因为虚拟网卡启动需要几秒钟, APP 可先展示界面,等待 SDP-SDK 创 建成功后通知,触发 APP 连接网络查询具体数据。 

# 3.3 隧道维持 

安全隧道成功创建后,由于性能的需要,需要维持 TCP 长连接, SDK 通过定时心跳包和 SDP 控制中心保持连接。 

# 3.3.1 流程图 

前提条件:移动端 APP 已顺利登录认证成功,且正确创建安全隧道。 

# 3.3.2 流程说明 

SDP-SDK 定时 30 秒发送心跳包,维持安全隧道。 

# 3.4 隧道重连 

在移动手机实际使用过程中,可能出现以下情况: 

网络切换 

网络波动 

APP 进程被杀 

会导致安全隧道断开,当用户恢复网络后,可以通过自动或由移动 APP 主动调用,无需再次认证,重新连接安全隧道。 

# 3.4.1 流程图 

# 3.4.2 流程说明 

场景 1 : SDK 主动连接 

当由于网络切换导致隧道断开。 

SDP-SDK 会定时监测安全隧道状态 

当 SDP-SDK 监测到安全隧道断开,则会主动使用会话标识发起重新连 接 

场景 2 :移动端 APP 主动连接 

当由于 APP 进程被杀导致连接断开,再次打开 APP 时,可无需让用户 再次登录,移动端 APP 调用 SDK 主动发起连接 

用户打开移动端 APP 

APP 调用 SDK 进行重连 

SDK 检测到状态为断开 

SDK 主动使用会话标识发起重新连接 

如果重连失败,则反馈给移动端 APP ,让用户重新登录。 

# 3.5 隧道被动销毁 

为了安全保护, SDP 规定用户在安全隧道建立一定时间后,必须主动 下线,防止长时间在线被黑客利用。 

# 3.5.1 流程图 

# 3.5.2 流程说明 

会话到期后,控制中心通知 SDK 主动销毁会话 

SDK 主动销毁安全隧道 

SDK 通知移动端 APP 销毁的消息,移动端 APP 提醒用户,转至登录界 面 

# 3.6 隧道主动销毁 

用户主动退出时,需要销毁安全隧道。 

# 3.6.1 流程图 

# 3.6.2 流程说明 

用户主动退出 

SDK 通知控制中心销毁会话 

SDK 销毁安全隧道 

6. 鸿蒙 -SDK 接入 

sdk 版本: 1.0.17 

[SDP 鸿蒙 sdk-1.0.17.zip] 

6.1 开发环境 

名称 

# 版本 

# 开发工具 

DevEco Studio 

DevEco Studio 5.0.0 Release 

# 开发语言 

TS 

ArkTS 

Napi c/c++ 

API 12 Release 

支持系统 

HarmonyOS 5.0.1 及以上 

6.2 组件说明见下表 组件名称 

描述 

是否必须 

YXSDP.har 

连接 SDP ,断开 SDP ,重新连接 SDP ,代理请求,网络切换自动重连 等 是 

6.3 组件接入和工程设置 

# 6.3.1 导入组件到工程主路径 

# 6.3.2 配置组件引用,完成后同步刷新项目 

# 6.3.3 组件权限 

权限 

描述 

是否必须 ohos.permission.INTERNET 网络访问权限 是 

ohos.permission.STORE_PERSISTENT_DATA 数据存储权限 是 

ohos.permission.GET_NETWORK_INFO 网络信息查看权限 是 

ohos.permission.KEEP_BACKGROUND_RUNNING 后台运行权限 

是 

ohos.permission.LOCATION 

访问位置信息 

是 

ohos.permission.APPROXIMATELY_LOCATION 

访问位置信息,精准定位 

是 

ohos.permission.ACCESS_BIOMETRIC 生物特征,指纹, faceid 

是 

后台权限设置 

key 值 描述 

是否必须 value 值 

backgroundModes 后台访问模式 是 

["audioPlayback"] 

6.3.4 VPN 扩展 Abilities 设置 

在主工程新建 YXSDPDemoVpnExtAbility.ets 文件,内容如下 module.json5 中设置如下: 

# 如何查找 vpn 扩展 

在工程模块 module.json5 中编辑 vpn 扩展,点击 type 进入 module.json 编辑内容,在 enum 中手动添加 vpn 类型并保存 

# 6.4 相关方法调用 

6.4.1 初始化 

初始化方法只调用一次,请在启动 app 后, onWindowStageCreate 中 调用初始化方法 

调用组件库 import { YXSDPMangage } from "yxsdp" ,调用代码如下 

C++ import { YXSDPMangage } from "yxsdp" 

```arkts
onWindowStageCreate(windowStage: window.WindowStage): void { // Main window is created, set main page for this ability hilog.info(0x0000, 'testTag', '%{public}s', 'Ability 
```

onWindowStageCreate'); windowStage.loadContent('pages/Index', (err) => { if (err.code) { hilog.error(0x0000, 'testTag', 'Failed to load the content. Cause: %{public}s', JSON.stringify(err) ?? ''); return; } hilog.info(0x0000, 'testTag', 'Succeeded in loading the content.'); // 初始化 SDK 

YXSDPMangage.init(this.context,windowStage); }); } 

# 初始化接口 

C++ YXSDPMangage.init(context: common.UIAbilityContext, windowStage: window.WindowStage, abilityName?: string) 

init 入参 

# 参数名 

类型 

描述 

是否必须 

context 

common.UIAbilityContext 

主 Ability 的对应的 context 

是 

windowStage 

window.WindowStage 

主窗口 WindowStage 

是 

abilityName 

string 

主 Ability 名称,默认 EntryAbility 

否 

# 6.4.2 查询 SDK 版本号 

调用组件库 import { YXSDPMangage } from "yxsdp" ,调用代码如下 

```arkts
C++ import { YXSDPMangage } from "yxsdp" let version: string = YXSDPMangage.sdkVersion(); 
```

查询版本号接口 

C++ YXSDPMangage.sdkVersion(): string 

# 6.4.3 连接 SDP 

调用组件库 import { YXSDPMangage } from "yxsdp" ,调用代码如下 

```arkts
C++ import { YXSDPMangage } from "yxsdp"; let sdp = 
YXSDPMangage.YXSDP.manage(); sdp.sdpConnectStatusDidChange = (connectStatus: YXSDPMangage.YXSDPConnectState) => { if (connectStatus == YXSDPMangage.YXSDPConnectState.Connected) { console.log("sdp 创建成功 "); } if (connectStatus == YXSDPMangage.YXSDPConnectState.DisConnected) { console.log("sdp 断开连接 ") } } let config: YXSDPMangage.YXSDPConfig = new YXSDPMangage.YXSDPConfig() config.knockHost = "10.21.x.x"; config.knockPort = 12345; config.userName = "admin"; config.passWord = "pass"; config.vpnAbilityName = "YXSDPDemoVpnExtAbility"; sdp.startConnect(config,() => { console.log(` 连接成功 `) 
```

sdp.reciveSDPRespData = (resp: YXSDPMangage.YXSDPResponseData) => { console.log(JSON.stringify(resp)) }; },(err: BusinessError) => { sdp.reciveSDPRespData = (resp: YXSDPMangage.YXSDPResponseData) => { console.log(JSON.stringify(resp)) }; console.log(` 连接失败 ${err.code}=======${err.message}`) }) 

# 连接 SDP 接口 

C++ 

() => { // 成功会调 },(err:BusinessError) => { // 失败回调 }) YXSDPConfig 连接配置类说明 

类型 

属性 

类型 

描述 

是否必须 

YXSDPConfig 

knockHost 

string 

敲门 host IP 是 

knockPort number 敲门 端口 是 userName string 用户名 是 

passWord string 密码, sm2 加密后的密文 是 

vpnAbilityName 

string 

扩展 VPN Ability 名,如: YXSDPDemoVpnExtAbility 

是 

reqData 

string 

现场自定义认证参数 

否 

qcf 

QCFInfo 

国盾量子配置信息,详见 4.3.1 QCFInfo 类说明 

否 

thirdauthData 

YXSDPProxyConfig 

第三方透传认证数据,详见 4.6YXSDPProxyConfig 说明 

否 

# 6.4.4 断开 SDP 连接 

调用组件库 import { YXSDPMangage } from "yxsdp" ,调用代码如下 

```arkts
C++ import { YXSDPMangage } from "yxsdp" let sdp = YXSDPMangage.YXSDP.manage(); sdp.stop(); 
```

# 断开 SDP 连接接口 

C++ YXSDPMangage.YXSDP.manage().stop() 

# 6.4.5 重连 SDP 接口 

调用组件库 import { YXSDPMangage } from "yxsdp" ,调用代码如下 

```arkts
C++ import { YXSDPMangage } from "yxsdp"; let sdp = YXSDPMangage.YXSDP.manage(); //--- 如需要长时重连,请保存首 
```

次认证连接 SDP 后返回的 reOnlineUserInfo 信息 //--- 注意 ⚠ 这种模 式下不支持 qcf 国盾量子加密 let host: string = " 敲门 host"; let port: number = 敲门端口 ; let userName: string = 用户名 ; if (!sdp.config) { sdp.config = new YXSDPMangage.YXSDPConfig(); 

sdp.config.knockHost = host; sdp.config.knockPort = port; sdp.config.userName = userName; sdp.config.vpnAbilityName = "YSXSDPVpnExtAbility"; } sdp.reOnlineUserInfo = new YXSDPMangage.YXSDPReOnLineUserData(host,port,userid,userName,refreshkey); //--- sdp.reOnline(() => { console.log(` 重新连接成功 `) },(err: BusinessError) => { console.log(` 重新连接失败 ${err.code} =======${err.message}`) }) 

# YXSDPReOnLineUserData 重连信息类说明 

类型 

属性 

类型 

描述 

是否必须 

YXSDPReOnLineUserData 

host 

string 

重连 敲门 host 

是 

port 

number 

重连 敲门 端口 

是 

userid string 

用户 id 是 

nickname 

string 用户名 

是 

refreshkey 

string 

刷新 key 值 

是 

# 6.4.6 代理请求接口 

调用组件库 import { YXSDPMangage } from "yxsdp" ,调用代码如下 C++ import { YXSDPMangage } from "yxsdp" let sdp = YXSDPMangage.YXSDP.manage(); 

```arkts
let config: YXSDPMangage.YXSDPProxyConfig = { requrl: "http:// xxx", method: "POST", header: "", data: "", serverHost: "10.28.x.x", port:12345 }; sdp.proxyapiV2(config).then((resp) => { console.log(` 请求成功 =====${resp}`); 
```

}).catch((err:BusinessError) => { console.log(`${err.code} =======${err.message}`) }) 

# YXSDPProxyConfig 说明 

约束 

参数名 

类型 

描述 

是否必须 

YXSDPProxyConfig 

requrl 

string 

第三方请求 url 地址 

是 

method 

string 

第三方请求方式,大写,如: POST 是 

header 

string 

第三方请求头 

是 

data 

string 

# 第三方请求体 

是 

serverHost 

string 

敲门 host IP 

是 

port 

number 

敲门端口 

是 

proxyapiV2 是 UDP 代理请求,不支持透传大包;如需大包代理请求 (如人脸认证)请联系管理员! 

# 6.4.7 App 销毁时,关闭 SDP 

调用组件库 import { YXSDPMangage } from "yxsdp" ,调用代码如下 

C++ import { YXSDPMangage } from "yxsdp" 

```arkts
onWindowStageWillDestroy(): void { // Main window is destroyed, release UI related resources hilog.info(0x0000, 'testTag', '%{public} s', 'Ability onWindowStageWillDestroy'); YXSDPMangage.YXSDP.manage().stop(); } 
```

# 6.4.8 日志管理 

调用组件库 import { YXSDPMangage } from "yxsdp" ,调用代码如下 C++ import { YXSDPMangage } from "yxsdp" // 控制台打印 

```arkts
YXSDPMangage.consoleOutput(true); // 开启日志记录到文件 YXSDPMangage.recordLog(true); // 获取日志文件路径 Å let paths: string[] = YXSDPMangage.logPath(); 
```

consoleOutput 入参 

参数名 

类型 

描述 

是否必须 

consoleOutput 

boolean 

控制台日志是否打印 

true: 控制台打印日志 false: 控制台不打印日志 

# 7. 附录 

SDP Android/iOS SDK 错误码 

iOS-app 集成 sdk 优化处理(隧道)
