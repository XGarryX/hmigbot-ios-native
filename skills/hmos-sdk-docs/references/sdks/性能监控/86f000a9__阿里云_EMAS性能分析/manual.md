# **HarmonyOS SDK接入** 

本章节介绍了 HarmonyOS SDK 的接入方法。 

## **前言** 

本 SDK 基于 HarmonyOS API 12 开发, compatibleSdkVersion 为 5.0.0(12) 。 

## **准备工作** 

1. 请参考 HarmonyOS 应用开发文档准备 HarmonyOS 应用开发环境。 

2. 请参考 Native 应用创建鸿蒙应用,在应用设置中查看 AppKey 和 AppSecret 。 

## **第一步:安装SDK** 

在 HarmonyOS 应用根目录执行以下命令来安装 SDK : 

ohpm install @aliyun/apm ohpm install @aliyun/apm_perf 

ohpm 工具及更多关于 OpenHarmony 安装第三方 SDK 的信息请参考 OpenHarmony 三方库中心仓说明。 

## **第二步:初始化SDK、启动性能分析** 

在 Ability onCreate 生命周期回调中执行以下代码初始化配置 SDK : 

```arkts
import { AbilityConstant, UIAbility, Want } from '@kit.AbilityKit'; import { window } from '@kit.ArkUI'; import { APM, APMConfig, Logger } from '@aliyun/apm'; import { hilog } from '@kit.PerformanceAnalysisKit'; import { performanceApi } from '@aliyun/apm_perf'; class MyCustomLog implements Logger { print(domain: number, tag: string, level: hilog.LogLevel, msg: string): void { switch (level) { case hilog.LogLevel.DEBUG: console.debug(` 自定义 log msg:${msg}`); break; case hilog.LogLevel.INFO: console.info(` 自定义 log msg:${msg}`); break; case hilog.LogLevel.WARN: console.warn(` 自定义 log msg:${msg}`); break; case hilog.LogLevel.ERROR: case hilog.LogLevel.FATAL: console.error(` 自定义 log msg:${msg}`); break; } } } export default class EntryAbility extends UIAbility { onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void { hilog.info(0x0000, 'testTag', '%{public}s', 'Ability onCreate'); const apm_perf_config: APMConfig = { context: this.context, appKey: 'appKey 参数 ', appSecret: 'appSecret 参数 ', nick: ' 用户昵称参数 ', userId: ' 用户 ID 参数 ', channel: ' 用户渠道参数 ', hiLog: true, // SDK 内的 hilog 开关 customLogger: new MyCustomLog(), // 自定义日志接口 } APM.init(apm_perf_config, [performanceApi]) APM.start(); } // 省略其它代码 } 
```

其中 appKey , appSecret 请配置为在准备工作中获取的 AppKey 和 AppSecret 。 

## **第三步:接入验证** 

SDK 接入完成后,可以正常启动应用,进行一些页面跳转操作,然后将应用退到后台,等待 3 分钟后在控制台查看是否有应用 数据。
