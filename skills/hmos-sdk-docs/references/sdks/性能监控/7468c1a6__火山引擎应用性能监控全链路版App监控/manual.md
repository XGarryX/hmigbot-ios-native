# 应用性能监控全链路版 

## Harmony SDK接入 

版权所有:北京火山引擎科技有限公司 

产品版本:1.0.0 文档版本:20240606 

应用性能监控全链路版 

法律声明 

### 法律声明 

本《 Harmony SDK 接入》的所有内容,包括但不限于文字、商标、架构、图示、图 片、页面布局等 , 其知识产权(著作权、商标权、专利权、商业秘密等)归属于北京火山 引擎科技有限公司及其关联公司(火山引擎),非经火山引擎书面同意,任何个人和组织 不得复制、使用、修改、转发或以任何违反本《 Harmony SDK 接入》所承载的目的进 行传播。 

本《 Harmony SDK 接入》陈述内容仅作为产品的通用性介绍和参考性指引,火山引擎 保留按 “ 现状 ” 和 “ 当前可用 ” 的形式提供产品和服务的权利。火山引擎不对本《 Harmony SDK 接入》中所载的产品功能、性质、质量、标准等内容进行明示或默示的保证和承 诺,最终以您与火山引擎实际签署的协议为准。 

如您发现本《 Harmony SDK 接入》有任何错误或歧义,或发现有对本《 Harmony SDK 接入》、产品本身的侵权行为,请与火山引擎取得联系。 

联系方式: service@volcengine.com , 400-850-0030 (周一至周五 10:00-18:00 ) 

文档版本:20240606 

版权所有 © 北京火山引擎科技有限公司 

1 

应用性能监控全链路版 

目录 

### 目录 

|法律声明|1|
|---|---|
|目录|1|
|1. 应用接入Harmony SDK|1|
|2. 验证数据上报|4|

文档版本:20240606 

版权所有 © 北京火山引擎科技有限公司 

1 

应用性能监控全链路版 

1. 应用接入Harmony SDK 

### 1. 应用接入Harmony SDK 

本文介绍Harmony SDK的详细接入步骤。接入SDK后,即可在应用性能监控全链路版平台上使用相关分析 功能。 

#### 注意事项 

   - Harmony SDK目前仅限在中国大陆应用使用(不包括港澳台地区)。 

- 

- 调用SDK初始化接口不会采集用户信息,调用SDK启动接口会开始采集用户信息,请确保采集用户信息 之前已经获得用户授权SDK隐私政策 。 

   - 目前仅支持离线包接入,请单击此处 提交工单获取har包。 

- 

#### 步骤一:获取SDK包,引入依赖 

1. 把har包拷贝到工程中, 如 entry/libs 目 录下。 2. 在主入口module 的 oh-package.json5 文 件中,添加离线har包依赖。 

"dependencies": { "@hpem/apmplus_crash": "file:libs/apmplus_crash_x.x.x.har" } 

#### 步骤二:初始化SDK并开启监控 

注意 

初始化SDK阶段,不获取用户个人信息。 

1. 在AbilityStage的onCreate中,添加以下代码,初始化崩溃相关功能。 

import {MonitorCrash, Config } from '@hpem/apmplus_crash'; _/** * 入口module的module.json5中配置的srcEntry */_ 

export default class EntryAbilityStage extends AbilityStage { 

```arkts
let mMonitor:MonitorCrash|undefined = undefined; _// 应用的HAP在首次加载时,为该Module初始化_ onCreate(): void { this.initCrashMonitor(this.context); } 
```

文档版本:20240606 

版权所有 © 北京火山引擎科技有限公司 

应用性能监控全链路版 

1. 应用接入Harmony SDK 

onAcceptWant(want: Want) { return "EntryAbilityStage"; } 

```arkts
onMemoryLevel(level: AbilityConstant.MemoryLevel): void { } initCrashMonitor(context: Context) { let config:Config.Config = Config.app({{AppId}}, {{AppToken}}) _// AppId为string类型和鉴权 token,可从平台应用信息处获取,token错误无法上报数据_ .channel(CHANNEL) _// 应用渠道,string类型_ .versionCode(100) _// 可选,number类型_ .versionName('1.0.0') _// 可选,string类型_ .dynamicParams({ _// 可选_ getDeviceId() { return DID; _// string类型,不设置默认生成本地id_ }, getUserId() { return UID; _// string类型,不设置默认为空_ } }) _// .debug(true) // 控制是否输出日志_ .autoStart(false) _// 控制是否在初始化时自动开启监控,默认为true_ .build(); this.mMonitor = MonitorCrash.init(context, config); _// 在用户同意隐私协议后开启监控,未设置autoStart或者autoStart传true时不需要调用 // this.mMonitor.start();_ } 
```

##### 说明 

- Context建议传递ApplicationContext。 

- versionCode为数字版本号,例如100;versionName为字符版本号,例如"1.0.0"。 

- 初始化返回的MonitorCrash实例为后续配置的入口。 

- 避免重复调用初始化方法。 

   - AppID和AppToken获取方法,请参见如何查询AppID和AppToken? 。 

2. 启动崩溃监控,开始收集数据。 

##### 注意 

请在用户同意隐私政策后,再调用方法收集数据。 

文档版本:20240606 

版权所有 © 北京火山引擎科技有限公司 

应用性能监控全链路版 

1. 应用接入Harmony SDK 

_// 启动监控_ 

- _// 当初始化时autoStart传入false设置为初始化时不自动开启监控,需要在合适的位置调用start方 法开启监控;_ 

_// 如果初始化时未设置autoStart参数或者设置为true,将自动开启监控,不需要调用start方法。_ 

this.mMonitor?.start(); 

文档版本:20240606 

版权所有 © 北京火山引擎科技有限公司 

应用性能监控全链路版 

2. 验证数据上报 

### 2. 验证数据上报 

您可以根据业务需求,按照以下模块说明,检查对应模块是否接入成功。 

#### **JS** 崩溃 

1. 添加以下代码,等待App发生崩溃。 

_// 建议测试时关闭appRecovery // appRecovery.enableAppRecovery(appRecovery.RestartFlag.NO_RESTART)_ throw new Error("Monitor Exception"); 

2. 重新启动App,SDK会立即上报上次启动期间发生的崩溃,然后在控制台查看上报成功的日志。 

#### **Native** 崩溃 

1. 添加以下代码,等待App发生崩溃。 

```arkts
_// import { process } from '@kit.ArkTS';_ process.kill(11, process.pid) 
```

2. 重新启动App,SDK会立即上报上次启动期间发生的崩溃,然后在控制台查看上报成功的日志。 

#### **AppFreeze** 

1. 添加以下代码,等待App发生闪退,可适当触摸屏幕。 

```arkts
_// import { systemDateTime } from '@kit.BasicServicesKit';_ let start = systemDateTime.getTime(); while (start + 10000 > systemDateTime.getTime()) {} 
```

2. 重新启动App,SDK会上报上次启动期间发生的崩溃,然后在控制台查看上报成功的日志。 3. 如果发现没有上报,适当等待后再次重新启动App。 

文档版本:20240606 

版权所有 © 北京火山引擎科技有限公司
