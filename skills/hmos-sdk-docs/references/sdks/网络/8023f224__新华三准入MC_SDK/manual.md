H3C iES Harmony SDK 应用开发指导 

资料版本: 5W100-20251211 

Copyright © 2026 新华三技术有限公司 版权所有,保留一切权利。 

非经本公司书面许可,任何单位和个人不得擅自摘抄、复制本文档内 容的部分或全部,并不得以任何形式传播。 

除新华三技术有限公司的商标外,本手册中出现的其它公司的商标、 产品标识及商品名称,由各自权利人拥有。 

本文档中的信息可能变动,恕不另行通知。 

目 录 

1 内容导航 1 

2 功能概述 2 

2.1 分类及特点 2 

2.2 接口及功能 2 

3 环境配置 3 

3.1 工具包说明 3 

3.2 开发环境准备 3 

3.2.1 将 har 包添加到工程中 3 

3.2.2 权限 3 

3.3 相关配置 4 

3.3.1 VPN 引入配置 4 

3.3.2 SDK 初始化配置 7 

4 功能开发指导 9 

4.1 SSL VPN 一键式认证接口使用说明 9 

# 4.2 SSL VPN 分步认证接口使用说明 10 

4.2.1 连接 VPN 设备 10 

4.2.2 VPN 登录 11 

4.2.3 建立 IP 层 SSL VPN 隧道 12 

4.3 SSL VPN 下线操作 13 

5 附录 14 

5.1 Emitter 消息注册 14 

5.2 错误码参考 15 

# 内容导航 

本文档主要用于指导鸿蒙应用开发人员,如何调用 H3C iES Harmony SDK( 以下简称 iES SDK 或 SDK) 提供的软件开发工具包。主要内容如 下: 

功能概述:说明 iES SDK 的分类特性。简要介绍 iES SDK 提供的接口及 功能,可单击链接跳转至相应的功能开发说明章节。 

环境配置:说明 iES SDK 工具中所包含的文件,以及如何配置。 

相关配置:展示 iES SDK 的快速入门开发流程,介绍 VPN 引入配置和 SDK 初始化配置的具体方法。 

功能开发指导:分章节详细介绍各接口可实现的功能描述及开发、调 试方法。 

# 功能概述 

# 分类及特点 

iES SDK :可单独完成 SSL VPN 接入认证,无需预先安装 iNode MC 客 户端。用户可根据自身需要加载不同的静态库文件及头文件。 

应用根据自身的需求,可以调用一键式 VPN 建立,或者分布式 VPN 建 立。 

# 接口及功能 

iES SDK 提供的接口和功能如表 2-1 所示,单击功能名称链接可跳转至 相应的典型功能开发说明。 

iES SDK 接口功能表 

功能 

类或接口名 

类或接口描述 

SSL VPN 一键式认证接口使用说明 

linkAndLoginVPN 

一键式建立 VPN 隧道 

SSL VPN 分步认证接口使用说明 

vpnConnect 

VPN 连接 

loginForV7 

VPN 登录 

startVpn 

建立 IP 层 SSL VPN 隧道 

stopVpn 

VPN 下线 

# 环境配置 

# 工具包说明 

iES SDK 软件包名称: iES_SDK_HMY_x.xx.zip(x.xx 是 SDK 的版本号 ) 软件包解压后如下: 

Har 文件夹: iES_SDK_x.xx_Harmony.har 文件 

Sample 文件夹:包含 SDK 开发的示例工程代码。 

《 H3C iES Harmony SDK 应用开发指导 .docx 》 

开发环境准备 

# 将 har 包添加到工程中 

将 Har 文件夹的 har 文件复制到工程中 entry\libs\ 目录下,如下图所 示。 

# 复制文件 

# 权限 

需要在应用 entry\src\main\module.json5 文件中添加三个权限: ohos.permission.INTERNET 、 ohos.permission.GET_WIFI_INFO 、 ohos.permission.GET_NETWORK_INFO ,如下图所示: 

# 添加权限 

# 相关配置 

# VPN 引入配置 

该小节介绍如何在应用工程中引入 SDK 中有关 SSL VPN 功能,以及如 何进行配置。 

# 引入 SDK 的 har 包 

在工程的 entry\oh-package.json5 文件中,添加 SDK 的依赖,如下图, Demo 中引入了 file:.\libs\iessdk.har ,并命名为 inodevpnsdk ,那后续 所有对 SDK 中接口的引用,都要从 “inodevpnsdk” 这个包中引入,比 如 import { VpnHarAbility } from 'inodevpnsdk'; 

添加 SDK 依赖 

# 配置 module 文件 

在工程的 entry\src\main\ets 目录下添加 AppVpnAbility 文件,并在 entry\src\main\module.json5 文件的 extensionAbilities 中添加对应的 引用,如图所示: 

# 添加 AppVpnAbility 文件 

# 添加对应的引用 

Module 配置中, AppVpnAbility 的 type 类型设置为 “vpn” ,但鸿蒙原 配置中无该类型,需要在 module.json 文件中手动添加(注意不是 module.json5 文件),添加方式如下: 

Windows 用户使用 Ctrl+ 鼠标左键单击 “type” 字段, Mac 用户可按住 Command+ 鼠标轻击,在 IDE 打开 module.json 文件,在 module.json 文件标题处右键,选择 [ 打开范围 >Explorer] ,打开 module.json 所在 文件夹 

# 打开 module.json 所在文件夹 

进入文件夹 

打开 module.json 文件, Windows 用户可按住 Ctrl+F 搜索, Mac 用户 按住 Command+F 搜索,通过关键字 Indicates the type of the extension. 找到图中所示位置,将 “vpn” 字段填入即可。 

Indicates the type of the extension. 

# SDK 初始化配置 

每次应用程序启动时,都需要对 SDK 进行初始化操作,只有初始化操 作完成之后才能使用 SDK 的功能接口。使用示例如下: 

在 entryAbility 的 onCreate() 方法中,调用 SDK 的初始化接口: 

调用 SDK 的初始化接口 

# 接口描述 

SDK 进行初始化,方便后续所有接口的使用 

方法定义 

static initSDK(context: Context, logDirPath: string, logLevel: number) 

参数描述 

参数描述 

参数 

类型 

描述 

context 

Context ,必填项 

上下文。 

logDirPath 

string ,必填项 

SDK 日志路径。 

可为空串,空串情况下,由 SDK 指定位置 

建议应用层使用写成 this.context.filesDir+‘/XXX’ 的方式 

logLevel 

number ,必填项 

日志级别( 0-5 )。 

功能开发指导 

该章节介绍有关 SSL VPN 的相关接口使用。其中, SSL VPN 接口分为 两种调用方式: 

SSL VPN 一键式认证接口使用说明:只调用一个接口完成整个 SSL VPN 认证。多域情况下,要使用 SDK 提供的域选择页面。 

SSL VPN 分步认证接口使用说明:按照 H3C SSL VPN 认证流程,依次 完成连接、认证、启动 VPN 服务的接口调用。 

所有方式都需要应用层通过 Emitter 消息注册回调,接收 SSL VPN SDK 中返回的一些状态。 

SSL VPN 一键式认证接口使用说明 

接口描述 

SSL VPN 认证一键式接口,通过该接口, SDK 与 VPN 网关进行连接、 认证并开启 VPN 隧道服务。 

# 方法定义 

public static async linkAndLoginVPN(sslVpnInfo: SslVpnInfo) 参数描述 

SslVpnInfo 类属性参数描述 

参数描述 参数属性 类型 描述 

username string (必填) 用户名 password string (必填) 用户密码 vpnAddr string (必填) VPN 网关地址 domainName string (必填) VPN 网关域名(无域名可填 ‘’ 空值) 

certFilePath 

String (选填) 

证书路径 

certpwd 

string (选填) 

证书密码 

返回值 

无,通过 emitter 接收结果 

异常情况 

所有异常情况,都由 SDK 进行弹框提醒,具体问题请查询错误码参 考。 接收 emitter 的失败消息,参照附录 Emitter 消息注册。 

使用示例 

使用示例 

注意事项 

在调用 linkAndLoginVPN 接口页面的 aboutToAppear ()中,赋值 SDK 中的上下文。 赋值 SDK 中的上下文 

在调用 linkAndLoginVPN 接口前,先注册 VPN 认证成功信息回调,登 录成功后自行完成 APP 层业务逻辑 

SSL VPN 分步认证接口使用说明 

本章节对 SSL VPN 认证过程中的每个阶段进行接口的使用进行说明, 为了完成 SSL VPN 的认证,请按顺序调用。 

# 连接 VPN 设备 

接口描述 

通过该接口, SDK 与 VPN 网关设备进行连接,并将获取到的域列表信 息返回给应用 

方法定义 

public static async vpnConnect(vpnAddr: string, domainName: string, 

certFile?: string, certpwd?: string): Promise<string[]> 

参数描述 

参数描述 

参数名 

类型 

描述 

vpnAddr 

string (必填) 

VPN 网关地址 

domainName 

string (必填) 

域名,可填空字符串 

certFile 

string? (选填) 

证书文件(暂不支持) 

certpwd 

string? (选填) 

证书密码(暂不支持) 

返回值 

返回值 

类型 

描述 

string[] 

域列表信息,如果网关上存在域信息且传入的 domainName 不存在 时,返回当前域列表 

异常情况 

所有异常情况,都由 SDK 进行弹框提醒,具体问题请查询错误码参 考。 

使用示例 

使用示例 

VPN 登录 

接口描述 

通过该方法, SDK 发起 VPN 登录认证。只有在连接 VPN 设备接口返回 值非 null 、 undefined 时,才能进行该接口调用。 

方法定义 

public static async loginForV7(userName: string, password: string, dynPassword: 

string|null,vldCode: string|null, certFile?: string, certpwd?: string): Promise<boolean> 

参数描述 

参数描述 参数名 类型 描述 userName string (必填) 用户名 password string (必填) 密码 dynPassword string|null (选填) 动态密码,如果不需要动态密码,可以输入空值 暂不支持 vldCode string|null (选填) 验证码,如果不需要验证码,可以输入空值 暂不支持 

certFile 

# string (选填) 

证书文件,暂不支持 

certpwd 

string (选填) 

证书密码,暂不支持 

返回值 返回值 类型 描述 

boolean 

SSL VPN 登录认证是否成功 

异常情况 

所有异常情况,都由 SDK 进行弹框提醒,具体问题请查询错误码参 考。 接收 emitter 的失败消息,请参见 Emitter 消息注册。 

使用示例 

使用示例 

建立 IP 层 SSL VPN 隧道 

在认证成功后,启动 VPN 隧道服务。只有在 VPN 登录接口返回 true 时,调用该接口。 

接口描述 

通过该方法, SDK 启动鸿蒙移动设备上的 VPN 隧道服务。 

方法定义 

public static async startVpn(): Promise<void> 

参数描述 

无 

返回值 

无,使用 emitter 接收结果。 

异常情况 

所有异常情况,都由 SDK 进行弹框提醒,具体问题请查询错误码列 表。 接收 emitter 的失败消息,请参见 Emitter 消息注册。 

使用示例 

在 VPN 登录成功后才能启动 VPN 隧道: 

使用示例 

SSL VPN 下线操作 

接口描述 

该接口为 SSL VPN 下线操作,同时关闭 SSL VPN 隧道 

方法定义 

public static stopVpn(): void 

参数描述 

无 

# 返回值 

无,通过 emitter 获取当前的结果。 

异常情况 

所有异常情况,都由 SDK 进行弹框提醒,具体问题请查询错误码参 考。 

使用示例 

使用示例 

附录 

Emitter 消息注册 

在需要的页面或者 Ability 中,注册 emitter 消息,消息接收 key 是 EventHuber.VPN_EMITTER_KEY ,根据 key 对应的内容区分是什么消 息: 

emitter 消息 

消息内容码 

描述 

EventHuber.VPN_LOGIN_SUCCESS 

SSL VPN 启动成功 

EventHuber.VPN_LOGOUT 

SSL VPN 登出成功 

EventHuber.VPN_LOGIN_FAILED 

SSL VPN 启动失败 

EventHuber.VPN_TUNNEL_PREPARE_CANCEL 

SSL VPN 取消授权 

使用示例: 

错误码参考 错误码参考 错误码 SDK 常量值 描述 1 NETWORK_ERROR 网络连接失败 2 CONNECT_TIMEOUT 连接超时 5 USER_NAME_IS_NULL 认证时,用户名为空 6 PASSWORD_IS_NULL 认证时,密码为空 

7 

# AUTH_ADDR_IS_NULL 

# 认证地址为空 

12 

VPN_HANDSHAKE_INVALIDUSER 

VPN 登录后握手报文,提示 536 错误 51 

SDK_NOT_INIT 

SDK 授权错误码 -SDK 没有初始化。 5101 

SDK_NOT_INIT_FILEERROR 初始化时,创建各种内存文件出错 5103 

SDK_NOT_INIT_LOGERROR 

初始化时,加载日志路径出错 

101 

PKG_CONTENT_ERROR 

报文中回应了异常信息 

102 

PKG_PARSE_DATA_ERROR 

报文解析失败 

103 

PKG_LOGIN_SMSNEED_ERROR 

VPN 登录认证需要 SMS 

4003 

VPN_VERSION_ERROR 

VPN 版本错误 

4004 

VPN_ADDR_CONN_WRONG 

VPN 连接了错误的网关地址 4006 

VPN_LOGIN_FAILED 

VPN 网关认证时发生错误 4008 VPN_NOT_CONNECT 

VPN 没有连接,无法获取具体信息 4009 VPN_VLD_CODE_IS_NULL 

VPN 验证码为空 

4010 

VPN_DYN_PWD_IS_NULL 

VPN 动态密码为空 

4011 

VPN_NOT_REQ_VLD_IMG 

没有请求校验码 

4012 

VPN_HANDSHAKE_ERR 

VPN 握手错误 

15001 

LOGIN_FAILED 

登录报文 result 标签返回 Failed
