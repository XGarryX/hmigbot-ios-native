安全网关 SDK 接口设计文档 

修改记录 版本 日期 更改原因 编写人 V1.0.0 2025-04-18 创建 李洋 V1.0.0 2025-04-18 支持离线策略测试 李洋 

V6.4.0 

2025-05-07 

增加创建隧道结果回调、接口更新、版本号更新 

李洋 

说明介绍 

能力: 

为集成 SDK 的鸿蒙应用提供外网访问内网业务的能力,通过加密隧道 保护传输数据 

当前版本仅提供代理隧道能力,需要主动配置代理转发给隧道 

组成: 

SDK 模块以 HAR 静态库形式提供,全称为 SDPTunnelLibrary.har ,当 前使用的鸿蒙 SDK 版本为 5.0.4 ( 16 ),已不再支持 32 位,仅支持 64 位的 arm 、 amd 架构 

文件列表: 

SDPTunnelLibrary.har : SDK 库 

开发语言: C/C++ 、 go 、 arkts 、 ts 

导出规范: HAR 

架构: arm ,仅支持 64 位 

运行环境:鸿蒙 

SDK : 5.0.4 ( 16 ),具体兼容版本范围待测试 

模型:仅支持 Stage 

集成流程 

# 创建工程 

打开 DevEco Studio ,菜单栏点击 “ 文件 -> 新建 -> 新建项目 ->Empty Ability” , SDK 建议用最新的 5.0.4 ( 16 ): 

# SDK 文件拷贝 

拷贝 sdk 及其依赖库到 src 根目录,可基于实际情况调整: 

# SDK 导入流程 

添加依赖:修改 oh-package.json5 

导入库,在 arkts 代码文件如 Index.ets 中通过以下代码导入 sdk ,如 图: 

调用:按以下顺序直接调用导入的函数即可 

SDPSDK_Init 

SDPSDK_BindUser 

离线模式:在工程目录放置 tunnelPly.json 并重新编译打包即可,无需 修改代码,已附上参考文件,注意离线模式仅针对策略流程上与在线 相同,发布前需要确认已删除离线策略 

# 初始化接口 

接口描述 

# 接口声明 

export declare function SDPSDK_Init(serverAddr: string, trustApp: 

string[], udid: string): boolean; 

接口描述 

【同步】用于初始化参数 

调用时机 

应用启动后,访问业务前的任一时间调用即可 

输入参数 

参数名称 

类型 

描述 

可选 / 必选 

serverAddr 

string 

管理平台地址 :https://ip:port 

必选 

trustApp 

string[] 

应用白名单,仅过滤名单应用流量,默认过滤当前应用 可选 

udid 

string 

设备 ID 

必选 

# 返回值 

返回值 

描述 

boolean 

成功: true ,失败: false 

# 示例: 

SDPSDK_Init(this.serverUrl, ["com.huawei.hmos.browser", "com.huawei.browser"], this.udid) 

绑定用户接口 

接口描述 

# 接口声明 

export declare function SDPSDK_BindUser(userCode: string, bundleName?: string): Promise<void>; 

# 接口描述 

【异步】用于到管理平台绑定用户设备、获取策略以及开启隧道 调用时机 

在初始化接口之后 

输入参数 

参数名称 

类型 

描述 

可选 / 必选 

userCode 

string 

用户标识 

必选 

BundleName 

String 

包名,当测试包名与发布包名不同时,通过指定包名确保用户绑定以 及策略获取接口调用正常 

可选 

返回值 

返回值 

描述 

Promise<void> 

成功: - ,失败: BusinessError 

# 示例: 

SDPSDK_BindUser(this.userCode, this.bundleName).then(() => { hilog.info(DOMAIN, TAG, " 绑定用户成功 ") }).catch((err: BusinessError) => { hilog.error(DOMAIN, TAG, " 绑定用户失败 : %{public}s", err) }) 

# 创建隧道结果回调接口 

接口描述 

# 接口声明 

export declare function SDPSDK_WaitForTunnelCreate(): 

Promise<void>; 

接口描述 

【异步】用于等待隧道创建完成 

调用时机 

在绑定用户接口之后 输入参数 参数名称 类型 描述 

可选 / 必选 

无 

返回值 返回值 

描述 

Promise<void> 

成功: - ,失败: BusinessError 

# 示例: 

SDPSDK_WaitForTunnelCreate().then(() => { hilog.error(DOMAIN, TAG, `vpn 创建成功 `) }).catch((err: BusinessError) => { hilog.error(DOMAIN, TAG, `vpn 创建失败 : ${err}`) }) 

# 查看隧道状态接口 

接口描述 

# 接口声明 

export declare function SDPSDK_GetTunnelInfo(): Promise<string>; 

# 接口描述 

- 【异步,待完善】用于查看隧道信息,目前仅支持返回速率、流量 调用时机 

在绑定用户接口后 

输入参数 参数名称 类型 描述 

可选 / 必选 

无 

返回值 返回值 描述 

Promise<string> 

成功: json 字符串,失败: BusinessError 

# 示例: 

import {SDPSDK_GetTunnelInfo} from 'sdptunnellibrary' 

```arkts
SDPSDK_GetTunnelInfo().then((result: string) => { const info: TunnelInfo = JSON.parse(result); this.tunnelInfo = JSON.stringify(info, null, 2); // 缩进 2 空格 hilog.debug(DOMAIN, TAG, `${this.tunnelInfo}`) }) 
```

# 结果参考: 

{"status_gateway": 0,"status_proxy": 0,"status_vpn": 0,"status_dns": 0,"flow": "2.2 kB","rate": "163 B/s","errinfo_gw": "","errinfo_proxy": ""}
