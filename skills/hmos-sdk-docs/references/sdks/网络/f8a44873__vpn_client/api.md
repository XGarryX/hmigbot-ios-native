# VPN 隧道 HormonyOS 版本接口文档 

版本: V1.0.0 

目 录 

1 概述 3 

- 2 使用说明 3 

- 2.1 Slink 的接口 3 

2.1.1 loginResult 结构 3 

2.1.2 InitVpn(context: Context): Promise<boolean> 3 

2.1.3 setParams(serverIp: string, tcpPort: number, udpPort: number, isIpv6: boolean): boolean ; 3 

2.1.4 login(name: string, pwd: string): loginResult ; 3 

2.1.5 startVpn(fd: number, func: closedCallback): void ; 4 

2.1.6 stopVpn(): void ; 4 

概述 

本文为 vpn 隧道接口在 hormonyOS(5.0.0.123 系统版本 ) 下的接口文 档。 使用说明 

Slink 的接口 

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

# 隧道成功失败标志 

InitVpn(context: Context): Promise<boolean> 

名称 

类型 

注释 

context 

Context 

上下文对象 

接口说明 : 

初始化 SDK, 传入 context , VPN 进程内部上下文,该接口是异步接口同 步调用 await 时需要外部函数增加 async 关键字。 

setParams(serverIp: string, tcpPort: number, udpPort: number, isIpv6: boolean): boolean ; 

名称 

类型 

注释 

context 

Context 

上下文对象 

接口说明 : 

设置 VPN 参数,传入服务器 ip , tcp 端口, udp 端口,服务器资源配置 是否是 ipv6 。 

2.1.4 login(name: string, pwd: string): loginResult ; 

名称 类型 注释 

name string 用户名 Pwd string 密码 2.1.5 startVpn(fd: number, func: closedCallback): void ; 名称 类型 注释 

Fd number Vpn 虚卡 fd func closedCallback 回调函数 接口说明 : 开启 vpn 数据业务。 

2.1.6 stopVpn(): void ; 

接口说明 : 

关闭 VPN 业务。
