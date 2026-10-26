# 北京智游网安科技有限公司 

北京智游网安科技有限公司 

爱加密移动威胁态势感知平台 

鸿蒙 SDK 接入文档 

版本号: 3.6.0 

文档密级:公开使用 

# ■ 版权声明 

本文档中出现的文字叙述、文档格式、插图、照片、方法、过程等内 容,除另有特别注明,版权均属智游网安所有,受到有关产权及版权 法保护。任何个人、机构未经智游网安的书面授权许可,不得以任何 方式复制或引用本文的任何片断。 

# ■ 免责条款 

本文档所含内容仅用于为平台最终用户提供信息,如内容有更改或撤 回,恕不另行通知。本公司已尽最大努力保证资料的准确可靠,但不 提供任何形式的担保。 

目 录 

目录 

1 简介 v 

2 合规指引 v 

# 2.1 鸿蒙 SDK 申请系统权限说明 v 

2.2 鸿蒙 SDK 隐私声明 vi 

3 运行环境 vii 

4 集成步骤 vii 

4.1 SDK 文件结构 vii 

4.2 使用 HAR 导入 SDK vii 

5 API 接口 viii 

5.1 初始化接口 viii 

5.1.1 引入初始化类 viii 

5.1.2 接口 viii 

5.1.3 参数说明 viii 

5.1.4 返回值 ix 

5.1.5 建议 ix 

5.2 启动接口 x 

5.2.1 接口 x 

5.2.2 说明 x 

5.3 监听录屏 / 共享屏幕 / 投屏行为 x 

5.3.1 Promise 接口 x 

5.3.2 参数说明 x 

5.3.3 返回值 x 

5.3.4 说明 xi 

5.4 取消录屏 / 共享屏幕 / 投屏监听 xi 

5.4.1 Promise 接口 xi 

5.4.2 参数说明 xi 

5.4.3 返回值 xi 

5.4.4 说明 xi 

5.5 主动获取录屏 / 共享屏幕 / 投屏状态 xi 

5.5.1 Promise 接口 xi 

5.5.2 同步接口 xi 

5.5.3 参数说明 xii 

5.5.4 返回值 xii 

5.6 监听电话通信状态 xii 

5.6.1 Promise 接口 xii 

5.6.2 参数说明 xii 

5.6.3 返回值 xii 

5.6.4 说明 xii 

5.7 取消电话通信状态监听 xiii 

5.7.1 Promise 接口 xiii 

5.7.2 参数说明 xiii 

5.7.3 返回值 xiii 

5.7.4 说明 xiii 

5.8 主动获取电话通信状态 xiii 

5.8.1 Promise 接口 xiii 

5.8.2 同步接口 xiii 

5.8.3 参数说明 xiii 

5.8.4 返回值 xiv 

5.9 设置定制版弹窗接口 xiv 

5.9.1 接口 xiv 

5.9.2 参数说明 xiv 

5.9.3 返回值 xiv 

5.10 屏幕录制设置 sdk 是否响应后台策略开关接口 xiv 

5.10.1 接口 xiv 

5.10.2 参数说明 xiv 

5.10.3 返回值 xv 

5.11 隐私合规字段收集配置 xv 

5.11.1 引入初始化类 xv 

5.11.2 接口 xv 

5.11.3 接口说明 xv 

5.12 禁止截屏 xvi 

5.12.1 Promise 接口 xvi 

5.12.2 参数说明 xvi 

5.12.3 返回值 xvii 

- 5.13 应用后台模糊化 xvii 

5.13.1 Promise 接口 xvii 

5.13.2 参数说明 xvii 

5.13.3 返回值 xvii 

5.13.4 page 页面内容 xvii 

5.13.5 说明 xviii 

5.14 移除应用后台模糊化 xviii 

5.14.1 参数说明 xviii 

5.14.2 返回值 xix 

5.15 模拟器检测 xix 

5.15.1 参数说明 xix 

5.15.2 返回值 xix 

5.16 设置定位获取频率 xix 

5.16.1 参数说明 xix 

5.16.2 返回值 xx 

5.16.3 说明 xx 

5.17 监听麦克风占用行为 xx 

5.17.1 Promise 接口 xx 

5.17.2 参数说明 xx 

5.17.3 返回值 xx 

5.17.4 说明 xx 

5.18 取消麦克风占用监听 xxi 

5.18.1 Promise 接口 xxi 

5.18.2 参数说明 xxi 

5.18.3 返回值 xxi 

5.18.4 说明 xxi 

5.19 主动获取麦克风占用状态 xxi 

5.19.1 Promise 接口 xxi 

5.19.2 参数说明 xxi 

5.19.3 返回值 xxi 

5.20 Demo 实现演示代码 xxii 

6 公司介绍 24 

# 简介 

威胁感知鸿蒙 SDK 是将设备遭受到的安全信息进行采集并且能够接收 服务端策略等功能的开放平台,此文档是为了提供给开发者简便,易 用的 API 接口,方便快速接入。 

合规指引 

# 鸿蒙 SDK 申请系统权限说明 

接入说明:对于爱加密威胁感知 SDK 可选申请的系统权限,您可以参 考相关如下表格的内容,详细了解相关权限与各业务功能的关系及其 申请时机,因相关权限的不申请将会对其对应的功能造成影响,您可 以结合业务实际需要进行合理配置。 

# 鸿蒙操作系统应用权限列表 

# 权限 

是否可选 

用途 

# 申请时机 

ohos.permission.INTERNET 

必选 

网络权限。用于实现和服务器通信,以便提供态势感知服务 启用业务功能读取 

ohos.permission.GET_NETWORK_INFO 

必选 

查看网络连接状态的权限。用于实现网络断开后 sdk 重新连接 启用业务功能读取 

ohos.permission.GYROSCOPE 

必选 

允许应用读取陀螺仪传感器的数据 

启用业务功能读取 

ohos.permission.MICROPHONE 

必选 

允许应用读取麦克风使用状态 

启用业务功能读取 

鸿蒙 SDK 隐私声明 

在 APP 隐私声明中增加威胁感知隐私内容,可将如下内容复制粘贴到 APP 的隐私条款中: 

SDK 名称:爱加密威胁感知 SDK 

第三方主体:北京智游网安科技有限公司 

SDK 用途:保障 APP 运行安全和业务安全,避免用户受到黑灰产攻击 

处理个人信息类型:应用信息(应用名称、应用版本号、包名、安装 时间、卸载时间、应用运行模式、证书 MD5 ),硬件信息 ( 设备型 号、设备厂商、屏幕分辨率、剩余电量、 CPU 使用率、 CPU 型号、 CPU 架构、设备名称、指令集 1 、主板信息、陀螺仪信息 ) ,系统信息 ( 系统名称、系统版本 ) ,位置信息 ( 经度、维度、时区信息 ) ,网络信 息 ( 运营商、网络代码、联网方式、外网 IP 、 Wi-Fi BSSID 、 Wi-Fi 信号 强度、蓝牙 MAC 、 WiFi_MAC 、 WiFi 名称、局域网 IP 、 MAC 地址、麦 克风状态 ) 

数据处理方式:去标识化、数据加密 

隐私权政策链接: https://www.ijiami.cn/privacypolicy/infoBeatharmony-privacy.html 

官网链接: https://www.ijiami.cn 

运行环境 

SDK 编译环境: DevEco Studio 5.0.3 900 Release 

SDK 运行环境:鸿蒙 api 12 以上版本系统 

集成步骤 

SDK 文件结构 

使用 HAR 导入 SDK 

将 har 文件复制到项目 libs 目录。 

在需要使用 sdk 文件模块的 oh-package.json5 文件中加入如下配置。 

"dependencies": { 

"ohoswxgzlibrary": "file:../libs/ohosWxgzLibrary.har" 

} 

# 安装依赖包 

DevEco 命令行运行 ohpm install 安装依赖包 

API 接口 

# 初始化接口 

引入初始化类 

import { OhosWxgzSdk } from 'ohoswxgzlibrary'; 

import { OhosWxgzSdkConfig } from 'ohoswxgzlibrary'; 

# 接口 

static initialize(config:OhosWxgzSdkConfig, ctx:Context, appKey: string, url:string): void; 

参数说明 

参数名称 

类型 

描述 

可选 / 必选 

config 

OhosWxgzSdkConfig 

sdk 字段收集配置 

必选 

ctx 

common.UIAbilityContext 

应用上下文 

必选 

appKey 

字符串 

应用 key ,由平台生成,如何生成咨询售后人员 

必选 

Url 

字符串 

服务端上报地址 

必选 返回值 

无 

建议 

初始化接口放在应用入口 onCreate 调用即可。 

注意: 

请在 WxgzSdk.initialize 初始化执行前设置自定义设备 ID ,初始化后调 用则设置无法生效; 

应用破解分析(选配): 

OhosWxgzSdk .setSign(sign:string); 

参数: 

sign :输入发布应用签名(签名证书 sha256 格式,可以使用下面命令 获取 java -jar hap-sign-tool.jar verify-app -inFile test.hap - outCertChain auto.cer -outProfile auto.p7b) 

检测项轮询间隔(选配): 

OhosWxgzSdk .setInterval(interval:number); 

参数: 

interval :设置高频地理检测项轮询间隔时间,单位毫秒。默认 180 秒 高频切换账号设置(选配): 

OhosWxgzSdk.setAccount(account:string); 

参数: 

acount :输入当前账号 

启动接口 

接口 

static start(): void; 

说明 

放在同意隐私政策之后调用,不调用该接口威胁感知 sdk 功能将不生 效。 

监听录屏 / 共享屏幕 / 投屏行为 

Promise 接口 

static OhosWxgzSdk.startCheckIsCapture(paramCallback: Callback<boolean>, timeDelay:number): Promise<boolean>; 

参数说明 

参数名称 

类型 

描述 

可选 / 必选 

paramCallBack 

Callback<boolean> 

# 录屏 / 共享屏幕 / 投屏行为回调接口 

必选 

timeDelay 

number 

延时时间间隔,单位 :ms 

必选 

返回值 返回值 描述 

true 

功能开启成功 

false 

功能开启失败(未授权成功或调用接口异常) 

说明 

内部会使用定时器循环进行检测,并通过回调接口将检测结果返回。 取消录屏 / 共享屏幕 / 投屏监听 

Promise 接口 

static OhosWxgzSdk.clearCheckIsCaptureTimer(): Promise<boolean>; 

参数说明 

无 

返回值 

返回值 

描述 

true 

监听取消成功 

false 

监听取消失败(未授权成功或调用接口异常) 说明 

移除监听录屏 / 共享屏幕 / 投屏行为的定时任务。 主动获取录屏 / 共享屏幕 / 投屏状态 

Promise 接口 

static OhosWxgzSdk.checkIsCapture(): Promise<boolean>; 同步接口 

static OhosWxgzSdk.checkIsCaptureSync(): boolean; 

参数说明 

无 

返回值 

返回值 描述 

true 

检测到正在录屏 / 共享屏幕 / 投屏 

# false 

未正在录屏 / 共享屏幕 / 投屏 

监听电话通信状态 

Promise 接口 

static OhosWxgzSdk.startCheckCalling(paramCallback: Callback<boolean>, timeDelay:number): Promise<boolean>; 

参数说明 参数名称 

类型 

描述 

可选 / 必选 

paramCallBack 

Callback<boolean> 

电话通信回调接口 

必选 

timeDelay 

number 

延时时间间隔,单位 :ms 

必选 

返回值 返回值 描述 

true 

# 功能开启成功 

false 

功能开启失败(未授权成功或调用接口异常) 

# 说明 

内部会使用定时器循环进行检测,并通过回调接口将检测结果返回。 取消电话通信状态监听 

Promise 接口 

static OhosWxgzSdk.clearCheckCallingTimer(): Promise<boolean>; 

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

移除监听电话通信状态监听的定时任务。 

主动获取电话通信状态 

# Promise 接口 

static OhosWxgzSdk.checkIsCalling(): Promise<boolean>; 

同步接口 

static OhosWxgzSdk.checkIsCallingSync(): boolean; 

# 参数说明 

无 

返回值 

返回值 

描述 

true 

检测到正在拨号 / 通话 

false 

未正在拨号 / 通话 

设置定制版弹窗接口 

接口 

static OhosWxgzSdk.setOemTShanVersion(enable:boolean, uiContext:UIContext):void 

参数说明 

参数名称 

类型 描述 

可选 / 必选 

enable 

boolean 

是否使用该功能, true 使用, false 不使用 ( 默认值 ) 

必选 

uiContext 

UIContext 

UI 组件上下文 

必选 返回值 

无 

屏幕录制设置 sdk 是否响应后台策略开关接口 接口 

static OhosWxgzSdk.setCaptureResponseSwitch(enable:boolean):void 

参数说明 

参数名称 

类型 描述 

可选 / 必选 

enable 

boolean 

是否响应后台策略开关, true 响应 ( 默认值 ) , false 不响应 

必选 

返回值 

无 

# 隐私合规字段收集配置 

引入初始化类 

import { OhosWxgzSdkConfig } from 'ohoswxgzlibrary'; import { OhosWxgzSdkBuilder } from 'ohoswxgzlibrary'; 

# 接口 

static OhosWxgzSdkBuilder().build(): OhosWxgzSdkConfig; 接口说明 接口名称 描述 

值说明 默认值 

可选 / 必选 

deviceInfo 

设备基本信息相关开关 

false 不收集, true 收集。 

true 

可选 

location 

# 定位经纬度相关开关 

false 不收集, true 收集。 

true 

可选 

netType 网络类型相关开关 false 不收集, true 收集。 true 可选 cpu cpu 信息相关开关 false 不收集, true 收集。 true 可选 battery 电池电量相关开关 false 不收集, true 收集。 true 可选 bundleInfo 应用基本信息相关开关 false 不收集, true 收集。 

true 

可选 

timeZone 

时区信息相关开关 false 不收集, true 收集。 true 

可选 

dp 分辨率相关开关 false 不收集, true 收集。 true 

可选 

simOpCode Sim 卡相关开关 false 不收集, true 收集。 true 可选 

operator 运营商相关开关 false 不收集, true 收集 true 

可选 

# bluetooth 

蓝牙信息相关开关 

false 不收集, true 收集。 

true 

可选 

localip 

内网 ip 相关开关 

false 不收集, true 收集。 

true 

可选 

ip 

外网 ip 相关开关 

false 不收集, true 收集。 

true 

可选 

sensor 

传感器相关开关 

false 不收集, true 收集。 

true 

可选 

wifi wifi 、 mac 相关开关 

# false 不收集, true 收集。 

true 

可选 

aaid 

aaid 标识符相关开关 

false 不收集, true 收集。 

true 

可选 

microphone 

麦克风相关开关 

false 不收集, true 收集。 

true 

可选 

禁止截屏 

Promise 接口 

static 

OhosWxgzSdk.disableCapture(context:common.UIAbilityContext, enable:boolean): Promise<boolean>; 

参数说明 

参数名称 

类型 

描述 

可选 / 必选 

# context 

UIAbilityContext 

当前窗口的上下文 

必选 

enable 

boolean 

是否开启禁止截屏(填入 false ,可以设置重新允许截屏) 必选 返回值 返回值 描述 

true 

功能开启成功 

false 

功能开启失败(调用接口异常) 应用后台模糊化 

Promise 接口 

static OhosWxgzSdk.addIjmMaskLayer(page: string, windowStage: window.WindowStage): Promise<boolean>; 

参数说明 

参数名称 

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

必选 返回值 返回值 描述 

true 

添加成功 

false 

添加失败(调用接口异常) 

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

该功能配置之后应用所有页面生效模糊化。 

移除应用后台模糊化 

static OhosWxgzSdk.removeIjmMaskLayer(): Promise<boolean>; 

# 参数说明 

无 

返回值 

返回值 

描述 

true 

# 移除成功 

false 

移除失败(调用接口异常) 模拟器检测 

static OhosWxgzSdk.checkIsSimulator(): Promise<boolean>; 

static OhosWxgzSdk.checkIsSimulatorSync(): boolean; 

参数说明 

无 

返回值 

返回值 

描述 

true 

检测为模拟器 

false 

检测为非模拟器 

# 设置定位获取频率 

static OhosWxgzSdk.setLocationInterval(interval: number): void; 

参数说明 

参数名称 

类型 

描述 

可选 / 必选 

Interval 

number 

设置 sdk 定位获取频率,单位 ms 

必选 

返回值 

无 

# 说明 

如果无合规问题,无需调用该接口,目前定位大于 3 秒才会调用定位 相关 api ,基本满足合规检测; 监听麦克风占用行为 

Promise 接口 

static 

OhosWxgzSdk.startCheckIsMicrophoneOccupy(paramCallback: Callback<boolean>, timeDelay:number): Promise<boolean>; 

# 参数说明 

参数名称 

类型 

描述 

可选 / 必选 

paramCallBack 

Callback<boolean> 

麦克风占用行为回调接口 必选 

timeDelay 

number 

延时时间间隔,单位 :ms 必选 返回值 返回值 

描述 

true 

功能开启成功 

false 

功能开启失败(未授权成功或调用接口异常) 

说明 

内部会使用定时器循环进行检测,并通过回调接口将检测结果返回。 取消麦克风占用监听 

Promise 接口 

static OhosWxgzSdk.clearCheckIsMicrophoneOccupyTimer(): Promise<boolean>; 

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

移除监听麦克风占用行为的定时任务。 

主动获取麦克风占用状态 

Promise 接口 

static OhosWxgzSdk.checkIsMicrophoneOccupy(): Promise<boolean>; 

# 参数说明 

无 

返回值 

返回值 

描述 

true 

检测到麦克风在被使用 

false 

检测到麦克风未被使用 

# Demo 实现演示代码 

在 EntryAbility 的 onCreate 方法中,添加初始化。如下图 

onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void { 

hilog.info(0x0000, 'testTag', '%{public}s', 'Ability onCreate'); 

let config:OhosWxgzSdkConfig = new OhosWxgzSdkBuilder() 

.sensor(false) 

.wifi(false) 

.build(); 

OhosWxgzSdk.initialize(config, this.context, " 填写 appKey", " 填写 url"); 

} 

} 

# 公司介绍 

北京智游网安科技有限公司(爱加密)成立于 2013 年,总部位于北 京,研发及运营中心位于深圳,同时在全国各地设立了 6 个分支机 构,拥有员工近 300 人。 

爱加密( www.ijiami.cn) 是专业的移动信息安全服务提供商,专注于 应用安全、大数据、业务合规、开发安全、数据安全、安全运营等领 域,坚持以用户需求为导向、持续不断的创新,致力于为客户提供全 方位、一站式的安全全生命周期解决方案。爱加密的服务宗旨是通过 革新性安全方案和 7x24 小时全天候的专业服务,打造和谐、强大、高 度安全的万物互联生态环境。 

爱加密产品体系和服务能力,贯穿了应用设计评估、安全开发测试、 应用优化、应用安全发布及应用上线运营阶段的整个生命周期。目前 行业用户遍及金融、运营商、政府、电商、能源、教育、游戏等多个 行业。至今共服务企业及开发者用户 50 万 + ,保护移动应用 100 万 + ,监测互联网应用 2000 万 + ,累计覆盖 10 亿移动终端。
