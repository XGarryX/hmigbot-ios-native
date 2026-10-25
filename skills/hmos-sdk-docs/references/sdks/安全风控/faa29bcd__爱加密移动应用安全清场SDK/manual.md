# 北京智游网安科技有限公司 

北京智游网安科技有限公司 

爱加密移动应用安全清场 SDK 

集成手册(鸿蒙) 

V1.5.4 

文档密级:完全公开 

# ■ 版权声明 

本文档中出现的文字叙述、文档格式、插图、照片、方法、过程等内 容,除另有特别注明,版权均属智游网安所有,受到有关产权及版权 法保护。任何个人、机构未经智游网安的书面授权许可,不得以任何 方式复制或引用本文的任何片断。 

# ■ 免责条款 

本文档所含内容仅用于为平台最终用户提供信息,如内容有更改或撤 回,恕不另行通知。本公司已尽最大努力保证资料的准确可靠,但不 提供任何形式的担保。 

# 目 录 

1 文档定义 1 

1.1 编写目的 1 

1.2 适用范围 1 

1.3 术语与缩略语 1 

1.4 运行环境 1 

2 集成步骤 2 

2.1 SDK 文件结构 2 

2.2 使用 HAR 导入 SDK 2 

3 API 接口 3 

3.1 引入清场类 3 

3.2 授权 3 

3.2.1 Promise 接口 3 

3.2.2 参数说明 3 

3.2.3 返回值 3 

3.2.4 建议 4 

3.3 Root 状态检测 4 

3.3.1 Promise 接口 4 

3.3.2 同步接口 4 

3.3.3 参数说明 4 3.3.4 返回值 4 3.3.5 建议 5 

3.4 模拟器检测 5 

3.4.1 Promise 接口 5 

3.4.2 同步接口 5 

3.4.3 参数说明 5 

3.4.4 返回值 5 

3.5 调试注入攻击检测 5 

3.5.1 Promise 接口 5 

3.5.2 参数说明 6 

3.5.3 返回值 6 

3.6 反调试保护 6 

3.6.1 Promise 接口 6 

3.6.2 参数说明 6 

3.6.3 返回值 7 

3.6.4 说明 7 

3.7 VPN 代理检测 7 

3.7.1 Promise 接口 7 

3.7.2 参数说明 7 

3.7.3 返回值 7 

3.7.4 权限说明 7 

3.7.5 建议 8 

3.8 应用伪造签名检测 8 

3.8.1 Promise 接口 8 

3.8.2 同步接口 8 

3.8.3 参数说明 8 

3.8.4 返回值 8 

3.9 http 代理检测 8 

3.9.1 Promise 接口 8 

3.9.2 返回值 9 

3.9.3 说明 9 

3.10 禁止截屏 9 

3.10.1 Promise 接口 9 

3.10.2 参数说明 9 

3.10.3 返回值 9 

3.10.4 建议 10 

3.11 监听录屏 / 共享屏幕 / 投屏行为 10 

3.11.1 Promise 接口 10 

3.11.2 参数说明 10 

3.11.3 返回值 10 

3.11.4 说明 10 

3.12 取消录屏 / 共享屏幕 / 投屏监听 10 

3.12.1 Promise 接口 10 

3.12.2 参数说明 11 

3.12.3 返回值 11 

3.12.4 说明 11 

# 3.13 主动获取录屏 / 共享屏幕 / 投屏状态 11 

3.13.1 Promise 接口 11 

3.13.2 同步接口 11 

3.13.3 参数说明 11 

3.13.4 返回值 11 

3.14 OpenHarmony 系统检测 12 

3.14.1 Promise 接口 12 

3.14.2 返回值 12 

3.15 应用后台模糊化 12 

3.15.1 Promise 接口 12 

3.15.2 参数说明 12 

3.15.3 返回值 13 

3.15.4 page 页面内容 13 

3.15.5 说明 13 

3.16 移除应用后台模糊化 14 

3.16.1 参数说明 14 

3.16.2 返回值 14 

3.17 监听电话通信状态 14 

3.17.1 Promise 接口 14 

3.17.2 参数说明 14 

3.17.3 返回值 14 

3.17.4 说明 15 

# 3.18 取消电话通信状态监听 15 

3.18.1 Promise 接口 15 

3.18.2 参数说明 15 

3.18.3 返回值 15 

3.18.4 说明 15 

3.19 主动获取电话通信状态 15 

3.19.1 Promise 接口 15 

3.19.2 参数说明 15 

3.19.3 返回值 16 

3.20 Demo 实现演示代码 16 

3.21 注意 16 

4 公司介绍 17 

文档定义 

# 编写目的 

为了用户更好的使用爱加密移动应用安全清场 SDK (鸿蒙版)的相关 功能,特编写该文档。 

# 适用范围 

本文档适用于使用爱加密移动应用安全清场 SDK (鸿蒙版)的客户公 司内部开发人员、测试人员,爱加密安全技术人员、测试人员、售后 实施人员。 

# 术语与缩略语 

说明:本部分主要是对本文档所出现的重要缩略语进行解释 

编写、术语 

解释 

SDK 

安全清场 SDK (鸿蒙版) 

# 运行环境 

SDK 编译环境: DevEco Studio 5.0.3.900 Release SDK 运行环境:鸿蒙 api 12 以上版本系统 

DEMO 工程运行环境 : DevEco Studio 5.0.3.900 Release 

# 集成步骤 

SDK 文件结构 

使用 HAR 导入 SDK 

将 har 文件复制到项目 libs 目录。 

在需要使用 sdk 文件模块的 oh-package.json5 文件中加入如下配置。 

"dependencies": { 

"@ohos/ohosDriskLib": "file:../libs/ohosDriskLib.har" 

} 

# 安装依赖包 

DevEco 命令行运行 ohpm install 安装依赖包 

API 接口 

# 引入清场类 

```arkts
import { OhosDRiskTool } from '@ohos/ohosDriskLib'; 
```

授权 

Promise 接口 

static setLicenseKey(lic: string): Promise<OhosLicenseKeyResult>; 

参数说明 参数名称 类型 描述 可选 / 必选 

licensekey 

字符串 授权码 必选 

返回值 

获取授权状态返回码 

result.getStatus(); 

# 获取状态描述 

result.getStatusDescribe(); 

# 获取到期时间 

result.getExpiredDate(); 

# 授权状态码说明: 

状态码 

描述 

0 

授权码错误 

1 

授权成功 

-1 

授权码错误或者格式错误 

-2 

授权码或者格式错误 

-3 

授权到期 

-4 包名验证失败 

-5 

签名验证失败 

-6 

# 底层获取包名或签名失败 

建议 

授权接口放在应用入口 onCreate 调用即可。 Root 状态检测 

# Promise 接口 

static checkRootStatus(): Promise<boolean>; 

同步接口 

static checkRootStatusSync(): boolean; 

参数说明 

不涉及 

返回值 

返回值 

描述 

true 

设备已 root 

false 

设备未 Root 

建议 

调用之后直接返回当前设备 root 状态,已 root 设备可在 Ability 中调用 后提示当前设备存在风险。 

# 模拟器检测 

Promise 接口 

static checkIsSimulator(): Promise<boolean>; 

同步接口 

static checkIsSimulatorSync(): boolean; 

参数说明 

不涉及 

返回值 

返回值 

描述 

true 

当前设备为模拟器 

false 

当前为真实设备 

调试注入攻击检测 

Promise 接口 

static startAttackMonitorBackground(strategy:number, delay: number): Promise<boolean>; 

检测到攻击立即触发回调接口。 

参数说明 

参数名称 

类型 

描述 

可选 / 必选 

strategy 

int 

攻击响应策略。 

1 :只有回调。 

# 2 : dialog 弹窗,有确定和退出按钮。 

3 : dialog 弹窗,只有退出按钮。 

4 : Toast 提示,默认时间为 1500ms 。 

5 检测到攻击,应用默认退出。 

必选 

delay 

long 

循环检测间隔时间 ( 单位 ms) ,推荐值 (5000ms 大于 1000ms ) 必选 

返回值 

返回值 

描述 

true 

检测到攻击行为 

false 

检测失败 / 重复调用 / 循环检测结束 

反调试保护 

Promise 接口 

static antiDebugProtect(): boolean; 

参数说明 

无 

返回值 

# 返回值 

描述 

true 

# 反调试保护开启成功 

false 

已经开启,无需重复开启 / 非主进程开启失败 

# 说明 

以多进程方式保护应用主进程不被其他恶意进程所调试。 

VPN 代理检测 

Promise 接口 

static checkVpn(): Promise<boolean>; 

参数说明 

无 返回值 返回值 描述 

true 

使用了 vpn 代理 

false 

未使用 vpn 代理 权限说明 

使用该接口返回正常结果需要下面权限 ohos.permission.GET_NETWORK_INFO , sdk 已经默认添加该权限 

# 建议 

可用于数据分析,收集当前用户使用的设备环境信息或判断为使用 vpn 代理之后做 Toast 提示或退出处理。 

应用伪造签名检测 

Promise 接口 

static checkFakeSign(sign: string): Promise<boolean>; 

同步接口 

static checkFakeSignSync(sign: string): boolean; 

参数说明 

参数名称 

类型 

描述 

可选 / 必选 

sign 

string 

该应用签名证书指纹值 

必选 

返回值 

返回值 描述 

true 

应用签名被伪造 

false 

应用签名未被伪造,正版签名 

http 代理检测 

Promise 接口 

static checkNetProxy(): Promise<boolean>; 

返回值 

返回值 

描述 

true 

检测到 http 网络代理 

false 

未检测到 http 网络代理 

说明 

使用该接口前需要确认应用或者应用集成的第三方 sdk 没有使用 connection.setAppHttpProxy 接口设置网络代理,否则该接口会返回 true 。 

禁止截屏 

Promise 接口 

static disableCapture(context:common.UIAbilityContext, enable:boolean): Promise<boolean>; 

参数说明 

参数名称 

类型 

描述 

可选 / 必选 

context 

UIAbilityContext 

当前窗口的上下文 必选 

enable 

boolean 

是否开启禁止截屏(填入 false ,可以设置重新允许截屏) 必选 返回值 返回值 描述 

true 

功能开启成功 

false 

功能开启失败(未授权成功或调用接口异常) 建议 监听录屏 / 共享屏幕 / 投屏行为 

Promise 接口 

static startCheckIsCapture(paramCallback: Callback<boolean>, 

timeDelay:number): Promise<boolean>; 

参数说明 

参数名称 

类型 

描述 

可选 / 必选 

paramCallBack 

Callback<boolean> 

录屏 / 共享屏幕 / 投屏行为回调接口 

必选 

timeDelay 

number 

延时时间间隔,单位 :ms 

必选 

返回值 返回值 描述 

true 

功能开启成功 

false 

功能开启失败(未授权成功或调用接口异常) 说明 

内部会使用定时器循环进行检测,并通过回调接口将检测结果返回。 取消录屏 / 共享屏幕 / 投屏监听 

Promise 接口 

static clearCheckIsCaptureTimer(): Promise<boolean>; 

# 参数说明 

无 

返回值 

返回值 

描述 

true 

监听取消成功 

false 

监听取消失败(未授权成功或调用接口异常) 

说明 

移除监听录屏 / 共享屏幕 / 投屏行为的定时任务。 

主动获取录屏 / 共享屏幕 / 投屏状态 

Promise 接口 

static checkIsCapture(): Promise<boolean>; 

同步接口 

static checkIsCaptureSync(): boolean; 

参数说明 

无 

# 返回值 

返回值 

描述 

true 

检测到正在录屏 / 共享屏幕 / 投屏 

false 

未正在录屏 / 共享屏幕 / 投屏 

OpenHarmony 系统检测 

Promise 接口 

static checkIsOpenHarmony(): Promise<boolean>; 

返回值 返回值 描述 

true 

系统为 OpenHarmony 系统 

false 

系统为非 OpenHarmony 系统(系统为 Harmony next 官方系统) 应用后台模糊化 

Promise 接口 

static addIjmMaskLayer(page: string, windowStage: window.WindowStage): Promise<boolean>; 

参数说明 

# 参数名称 

类型 

描述 

可选 / 必选 

page 

string 

要加载到窗口中的页面内容的路径,该路径需添加到工程的 main_pages.json 文件中 

必选 

windowStage 

window.WindowStage 

窗口管理器 

必选 

返回值 

返回值 

描述 

true 

添加成功 

false 

添加失败(未授权成功或调用接口异常) 

page 页面内容 

import { window } from "@kit.ArkUI"; 

@Entry 

@Component 

export struct IjmMaskLayerWindowComponent { 

aboutToAppear(): void { 

} 

build() { 

Column() { 

Column() { 

} }.width('100%').height('100%') 

.foregroundBlurStyle(BlurStyle.Thin, { 

colorMode: ThemeColorMode.LIGHT, 

adaptiveColor: AdaptiveColor.DEFAULT 

}) 

} 

} 

# 说明 

参数一:传入的页面内容需要固定上面组件代码内容,不然没有模糊 效果。具体可以参考 demo 工程源码。 

参数二:如何在 Page 中获取 WindowStage 实例,可参考华为 FAQ : https://developer.huawei.com/consumer/cn/doc/harmonyos-faqs/ faqs-arkui-298 

# 该功能配置之后应用所有页面生效模糊化。 

移除应用后台模糊化 

static removeIjmMaskLayer(): Promise<boolean>; 

参数说明 

无 

返回值 

返回值 

描述 

true 

移除成功 

false 

移除失败(未授权成功或调用接口异常) 监听电话通信状态 

Promise 接口 

static startCheckCalling(paramCallback: Callback<boolean>, timeDelay:number): Promise<boolean>; 

参数说明 

参数名称 

类型 

描述 

可选 / 必选 

paramCallBack 

Callback<boolean> 

电话通信回调接口 

必选 

timeDelay 

number 

延时时间间隔,单位 :ms 必选 返回值 返回值 描述 

true 

功能开启成功 

false 

功能开启失败(未授权成功或调用接口异常) 

说明 

内部会使用定时器循环进行检测,并通过回调接口将检测结果返回。 取消电话通信状态监听 

Promise 接口 

static clearCheckCallingTimer(): Promise<boolean>; 

参数说明 

无 

返回值 

# 返回值 

描述 

true 

# 监听取消成功 

false 

监听取消失败(未授权成功或调用接口异常) 说明 

移除监听电话通信状态监听的定时任务。 

主动获取电话通信状态 

Promise 接口 

static checkIsCalling(): Promise<boolean>; 

同步接口 

static checkIsCallingSync(): boolean; 

参数说明 

无 

返回值 返回值 描述 

true 

检测到正在拨号 / 通话 

false 

未正在拨号 / 通话 

# Demo 实现演示代码 

在 App 的 OnCreate 方法中,添加 licenceKey 授权认证。如下图 

export default class App extends AbilityStage { 

onCreate() { 

console.info('Application onCreate') 

let key = " 请填写授权码 "; 

OhosDRiskTool.setLicenseKey(key).then(data => { 

console.info("lic result " + data.getStatus()); 

}); 

} 

} 

# 注意 

授权码:用户需提供应用包名和证书指纹给售后生成授权码。 

# 公司介绍 

北京智游网安科技有限公司(爱加密)成立于 2013 年,总部位于北 京,研发及运营中心位于深圳,同时在全国各地设立了 12 个分支机 构,拥有员工 400 多人。 

爱加密( www.ijiami.cn) 是专业的移动信息安全服务提供商,专注于 移动应用安全、大数据、物联网及工业互联网安全,坚持以用户需求 为导向、持续不断的创新,致力于为客户提供全方位、一站式的移动 安全全生命周期解决方案。爱加密的服务宗旨是通过革新性安全方案 和 7x24 小时全天候的专业服务,打造和谐、强大、高度安全的万物互 

# 联生态环境。 

爱加密拥有安全防护、安全检测、安全管理、业务运营、威胁感知、 安全监管、安全服务七大产品体系,贯穿了应用设计评估、安全开发 测试、应用优化、应用安全发布及应用上线运营阶段的整个生命周 期。目前行业用户遍及金融、运营商、政府、电商、能源、教育、游 戏等多个行业。至今共服务企业及开发者用户 50 万 + ,保护移动应用 100 万 + ,监测互联网应用 1500 万 + ,累计覆盖 10 亿移动终端。
