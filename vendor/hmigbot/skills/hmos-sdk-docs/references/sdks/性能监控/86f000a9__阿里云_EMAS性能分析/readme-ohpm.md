> 来源: ohpm 中央仓 README(T1 信源) | 包: `@aliyun/apm_perf` | ohpm 最新版: 2.0.2 | 抓取: 2026-07-16
> 注意: 版本可能比市场快照新,以此为准时核对 CHANGELOG

# EMAS APM 性能分析

线上App性能问题,自动采集,包括启动、页面加载、帧率等性能指标,多维度自动聚合分析,网络请求自定义上报,保障线上App质量,进而提升客户留存和活跃。

## 下载安装

需要同时安装apm和apm_perf两个包。

```shell
ohpm install @aliyun/apm
ohpm install @aliyun/apm_perf
```

## 使用

### 配置

需要在UIAbility实例创建完成时的onCreate()回调中,初始化SDK。

```typescript
import { APM, APMConfig, Logger } from '@aliyun/apm';
import { performanceApi } from '@aliyun/apm_perf';

class MyCustomLog implements Logger {
  print(domain: number, tag: string, level: hilog.LogLevel, msg: string): void {
    switch (level) {
      case hilog.LogLevel.DEBUG:
        console.debug(`自定义log msg:${msg}`);
        break;
      case hilog.LogLevel.INFO:
        console.info(`自定义log msg:${msg}`);
        break;
      case hilog.LogLevel.WARN:
        console.warn(`自定义log msg:${msg}`);
        break;
      case hilog.LogLevel.ERROR:
      case hilog.LogLevel.FATAL:
        console.error(`自定义log msg:${msg}`);
        break;
    }
  }
}

export default class EntryAbility extends UIAbility {
  onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void {
    
    // APM 初始化参数
    const apm_config: APMConfig = {
      context: this.context,
      appKey: 'appKey参数',
      appSecret: 'appSecret参数',
      nick: '用户昵称参数',
      userId: '用户ID参数',
      channel: '用户渠道参数',
      hiLog: true, // SDK内的hilog开关
      customLogger: new MyCustomLog(), // 自定义日志接口
    }
    APM.init(apm_config, [performanceApi])
    APM.start();
  }
}
```
