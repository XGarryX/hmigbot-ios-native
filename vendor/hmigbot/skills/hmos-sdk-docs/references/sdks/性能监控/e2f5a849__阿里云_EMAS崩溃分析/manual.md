# **HarmonyOS SDK 接入** 

本章节介绍了 HarmonyOS SDK 的接入方法。 

## **前言** 

本 SDK 基于 HarmonyOS API 12 开发, compatibleSdkVersion 为 5.0.0(12) 。 

## **准备工作** 

1. 请参考 HarmonyOS 应用开发文档准备 HarmonyOS 应用开发环境。 

2. 请参考 Native 应用创建鸿蒙应用,在应用设置中查看 AppKey 和 AppSecret 。 

## **第一步:安装SDK** 

在 HarmonyOS 应用根目录执行以下命令来安装 SDK : 

ohpm install @aliyun/apm ohpm install @aliyun/apm_crash 

ohpm 工具及更多关于 OpenHarmony 安装第三方 SDK 的信息请参考 OpenHarmony 三方库中心仓说明。 

## **第二步:初始化SDK、启动崩溃分析** 

在 Ability onCreate 生命周期回调中执行以下代码初始化配置 SDK : 

### **说明** 

建议 SDK 初始化代码段,放在所有业务代码之前,确保 App 在启动时,优先加载崩溃分析服务,保障后续崩溃的信息,可 以即时获取并上传至控制台。 

```arkts
import { AbilityConstant, UIAbility, Want } from '@kit.AbilityKit'; import { window } from '@kit.ArkUI'; import { APM, APMConfig, Logger } from '@aliyun/apm'; import { hilog } from '@kit.PerformanceAnalysisKit'; import { crashAnalysisApi } from '@aliyun/apm_crash'; class MyCustomLog implements Logger { print(domain: number, tag: string, level: hilog.LogLevel, msg: string): void { switch (level) { case hilog.LogLevel.DEBUG: console.debug(` 自定义 log msg:${msg}`); break; case hilog.LogLevel.INFO: console.info(` 自定义 log msg:${msg}`); break; case hilog.LogLevel.WARN: console.warn(` 自定义 log msg:${msg}`); break; case hilog.LogLevel.ERROR: case hilog.LogLevel.FATAL: console.error(` 自定义 log msg:${msg}`); break; } } } export default class EntryAbility extends UIAbility { onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void { hilog.info(0x0000, 'testTag', '%{public}s', 'Ability onCreate'); const apm_perf_config: APMConfig = { context: this.context, appKey: 'appKey 参数 ', appSecret: 'appSecret 参数 ', nick: ' 用户昵称参数 ', userId: ' 用户 ID 参数 ', channel: ' 用户渠道参数 ', hiLog: true, // SDK 内的 hilog 开关 customLogger: new MyCustomLog(), // 自定义日志接口 } APM.init(apm_perf_config, [crashAnalysisApi]) APM.start(); } // 省略其它代码 } 
```

其中 appKey , appSecret 请配置为在准备工作中获取的 AppKey 和 AppSecret 。 

## **第三步:接入验证** 

SDK 接入完成后,需进行功能验证: 

### 1. 编写测试代码,模拟 / 触发移动端崩溃。例如: 

arkts 

// 数组越界 let tempList = ['a', 'b'] hilog.info(0x0000, 'apm', 'jsCrash %s', tempList[3].toString()) 

### 2. 重启移动端,大概 2 分钟后在控制台查看是否显示崩溃信息。 

### **说明** 

崩溃数据从采集到上传到控制台显示,存在大约 2~3 分钟延迟。 

## **1.0.0版本升级到1.0.1版本** 

1.0.1 版本相对于 1.0.0 版本,我们主要是优化了初始化接口,以支持更多的 APM 产品,比如性能分析。 需要调整的是 SDK 接入的第二步,参考第二步:初始化 SDK 、启动崩溃分析,修改为最新的接入代码即可。 同时接入性能、崩溃需要在 init 时引入两个 API ,核心代码参考如下: 

// 省略 import 代码 

```arkts
export default class EntryAbility extends UIAbility { onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void { hilog.info(0x0000, 'testTag', '%{public}s', 'Ability onCreate'); const apm_perf_config: APMConfig = { context: this.context, appKey: 'appKey 参数 ', appSecret: 'appSecret 参数 ', nick: ' 用户昵称参数 ', userId: ' 用户 ID 参数 ', channel: ' 用户渠道参数 ', hiLog: true, // SDK 内的 hilog 开关 customLogger: new MyCustomLog(), // 自定义日志接口 } // init 时要同时调用两个 api APM.init(apm_perf_config, [crashAnalysisApi , performanceApi]) APM.start(); } // 省略其它代码 }
```
