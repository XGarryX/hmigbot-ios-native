# VPN 隧道 HormonyOS 版本接口手册 

版本: V1.0.0 

目 录 

1 概述 3 

- 2 使用说明 4 

- 2.1 项目配置 4 

2.2 VPN 进程( MyVpnExtAbility.ets )中使用的接口 4 

2.2.1 调用流程 5 

# 2.2.2 接口相关 5 

# 2.3 UI 进程 (Index.ets)IPC 方式通讯 VPN 进程 6 

2.3.1 VPN 进程作为 IPC 服务端进行绑定 6 

2.3.2 UI 进程作为 IPC 客户端绑定和主动发起请求 6 

# 2.4 UI 进程调用备注 6 

2.4.1 说明 6 

# 概述 

本文为 vpn 隧道接口在 hormonyOS(5.0.0.123 系统版本 ) 下的使用指 导, dev 开发工具版本是 5.0.1Release, 其中 vpn_client.har 是依赖库, VpnExtensionAbility 的三方 VPN 进程去使用依赖库,调用鸿蒙隧道相 关接口建立 vpn 服务的启动和隧道绑定, UI 进程通过现有的鸿蒙 IPC 机 制和 VPN 进程进行数据的传递和状态交互。因为鸿蒙 SDK13 不支持 extension 打包进 hsp 等集成包,本文档会部分篇幅介绍 VpnExtensionAbility 及现有的 IPC 机制。华为后期可能会更换其他机 制,但目前仅能使用 IPC 机制去做 VPN 应用。 

使用说明 

# 项目配置 

# 图 1-1 module.json5 的配置 

上图配置代表 VPN 进程的配置,其中 type:vpn 中的类型 vpn 目前官方 提供的编译工具暂不支持 vpn 类型需要点击 “type” ,增加新类型,具 体操作如下: 

# 在 X:\DevEco 

Studio\sdk\default\hms\toolchains\modulecheck\module.json 中的 type 添加 ”vpn” 类型,参考鸿蒙社区问答如何支持 VPN 的使用,链接 为: https://developer.huawei.com/consumer/cn/forum/ topic/0201170363350906639?fid=0109140870620153026 

图 1-2 oh-package.json5 依赖模块的配置 

上图是告知 libs 库的依赖方便 VPN 进程可以使用 vpn_client 模块中的各 种接口配置 

VPN 进程( MyVpnExtAbility.ets )中使用的接口 

依赖导入: import {Slink,loginResult,closedCallback} from 'vpn_client'; 

Slink 是 ts 单例类使用 Slink.getInstance 获取类实例 

loginResult 结构 

名称 

类型 

注释 

fd 

number 

需要被隧道保护的 socketfd 

resource 

string 

隧道的资源信息 

msg 

string 

隧道成功失败标志 

调用流程 

调用流程 : 

slink.InitVpn 初始化 sdk 

slink.setParams 设置 vpn 参数 

slink.login 登录 vpn 

系统 api VpnConnection.protect(loginResult.fd) 保护隧道 fd 

系统 api VpnConnection.create(config) 设置虚拟网络信息(路由、 ip 等) 

slink.startVpn 开启 vpn 实际业务,注册断开回调函数 closedNotify 

接口相关 

接口说明 : 

初始化 SDK, 传入 context , VPN 进程内部上下文,该接口是异步接口同 步调用 await 时需要外部函数增加 async 关键字 

InitVpn(context: Context): Promise<boolean>; 

设置 VPN 参数,传入服务器 ip , tcp 端口, udp 端口,服务器资源配置 是否是 ipv6 。 

setParams(serverIp: string, tcpPort: number, udpPort: number, isIpv6: boolean): boolean; 

登录 vpn ,传入用户名及密码 

login(name: string, pwd: string): loginResult; 

开启 vpn 数据业务,传入鸿蒙 vpn 虚卡 fd 和断开的回调通知 js 函数 

startVpn(fd: number, func: closedCallback): void; 

关闭 vpn 数据业务 

stopVpn(): void; 

UI 进程 (Index.ets)IPC 方式通讯 VPN 进程 

注意: sdk13 手机系统为 5.0.0.123 版本以后可以通过 ipc 方式交互。 5.0.0.115 系统版本的手机不支持 Ipc 需要华为推送系统更新。华为后 期可能会更新 UI 进程和 VPN 进程间的通信方式,现阶段只能以 IPC 的 

# 方式实现两进程通信。 

VPN 进程作为 IPC 服务端进行绑定 

在 onConnect 回调中建立 rpc.RemoteObject 的示例创建方便和客户端 进程绑定 

具体参考 demo 中的代码写法 

UI 进程作为 IPC 客户端绑定和主动发起请求 

context.connectServiceExtensionAbility 和指定的 want 建立 connect 。 

利用 1 里连接好的 proxy 发起请求,得到结果目前内置请求 VPN 进程开 启 vpn 数据业务和查询 VPN 进程实际业务状态两个 IPC 进程通讯 

UI 进程调用备注 

说明 

步骤一: UI 进程通过开启 VPN 进程并建立连接 

步骤二: UI 进程获取步骤一的结果,根据结果做出反馈 

步骤三: UI 进程停止 VPN 进程 

备注:因为华为 IPC 进程目前是一问一答的设计机制,因此 IPC 进程都 需要自己去轮询处理,这部分需要客户端集成应用自己去参考华为实 现,本文档仅提供开启关闭查询状态三个接口,后续华为升级或开放 更灵活的进程间通讯接口,文档会以追加的方式,更新新的使用方 式。 

示例程序中用 IPC 方式开启、关闭 vpn , vpn 的状态使用订阅公共事 件, ext 进程通过公共事件发送 vpn 状态的方式通知 ui 进程。在实际对 接中可以考虑其他方式实现。
