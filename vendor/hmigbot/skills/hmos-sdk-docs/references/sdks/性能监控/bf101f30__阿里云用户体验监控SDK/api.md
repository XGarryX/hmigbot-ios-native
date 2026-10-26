# HarmonyOS NEXT 用户体验监控 SDK

# 接口说明

### 一、启动配置接口

| AlibabaCloudRum.withAppID("<your app id>").s |  |
|---|---|

|  | tart(this.context.getApplicationContext()) |
|---|---|

withAppID 之后进行相关配置, 可同时配置多项, start函数后配置无效。

### 设置自定义APP版本

通过此方法设置了自定义设备App版本号,那么SDK将会上报此版本号,不再使用默认获

取的版本号.

接口说明

●

| 参数 | 说明 | 参数限制 | 失败结果 |
|---|---|---|---|
| version | 自定义的版本号 | 字符串长度大于0, 小于等于64,否则接 口调用失败 | 当次设置无效 |

```
withAppVersion(version: string):AlibabaCloudRum
```

●

代码示例:

```
AlibabaCloudRum.withAppID("<#AppID#>")
      .withConfigAddress("<#ConfigAddr#>")
      .withAppVersion("custom app version")
      .start(this.context.getApplicationContext());
```

### 设置自定义应用环境

通过此方法设置应用环境字段

接口说明

●

| 参数 | 说明 | 参数限制 | 失败结果 |
|---|---|---|---|
| environment | 应用环境枚举 | 仅可使用预置枚举 单位,否则接口调 用失败,枚举类型 「0:NONE无环境配 置,1:PROD线上环 境,2:GRAY灰度环 境,3:PRE预发环 境,4:DAILY日常环 境,5:LOCAL本地环 境」 | 当次设置无效 |

```
withAppEnvironment(environment: AppEnvironment):AlibabaCloudRum
```

●

代码示例:

```
import {AppEnvironment} from'@alibabacloud_rum/harmony_sdk'
AlibabaCloudRum.withAppID("<#AppID#>")
  .withConfigAddress("<#ConfigAddr#>")
  .withAppEnvironment(AppEnvironment.NONE)
// .withAppEnvironment(AppEnvironment.PROD)
// .withAppEnvironment(AppEnvironment.GRAY)
// .withAppEnvironment(AppEnvironment.PRE)
// .withAppEnvironment(AppEnvironment.DAILY)
// .withAppEnvironment(AppEnvironment.LOCAL)
  .start(this.context.getApplicationContext());
```

注意:SDK内部预置了应用环境枚举单位,预置单位类型见AppEnvironment枚举类

### 使用自定义冷启动结束时间

是否使用自定义冷启动结束时间

接口说明:

●

```
withUseCustomLaunch(used: boolean):AlibabaCloudRum
```

| 参数 | 说明 |
|---|---|
| used | boolean 类型,true:使用自定义冷启动结 束,false:不使用自定义冷启动结束时间 |

●

代码示例:

```
AlibabaCloudRum.withAppID("<#AppID#>")
  .withConfigAddress("<#ConfigAddr#>")
  .withUseCustomLaunch(true)
  .start(this.context.getApplicationContext());
```

### 设置SDK自身请求Header

本接口用于设置对于SDK自身发起的网络请求中添加自定义请求头

接口说明:

●

| 参数 | 说明 | 失败结果 |
|---|---|---|
| headers | 要设置的请求头键值对(最 多设置64个,key长度限制 256个字符,value长度限制 512个字符) | key,value长度限制则单条数 据无效 |

```
withSDKRequestHeaders(headers: Map<string, string>): AliababCloudRum
```

●

代码示例:

```
constheaders:Map<string,string> = new Map();
headers.set("headerKey1","headerValue1");
headers.set("headerKey2","headerValue2");
headers.set("headerKey3","headerValue3");
AlibabaCloudRum.withAppID("<#AppID#>")
  .withConfigAddress("<#ConfigAddr#>")
  .withSDKRequestHeaders(headers)
  .start(this.context.getApplicationContext());
```

### 设置用户渠道ID

区分应用发布的渠道

接口说明:

●

| 参数 | 说明 | 参数限制 | 失败结果 |
|---|---|---|---|
| channelID | 自定义的渠道号 | 符串长度大于0,小 于等于256,否则接 口调用失败 | 当次设置无效 |

```
withChannelID(channelID: string): AlibabaCloudRum
```

●

代码示例:

```
AlibabaCloudRum.withAppID("<#AppID#>")
  .withConfigAddress("<#ConfigAddr#>")
  .withChannelID("custom channelID")
  .start(this.context.getApplicationContext());
```

### 设置设备ID

自定义设备 ID

接口说明:

●

| 参数 | 说明 | 参数限制 | 失败结果 |
|---|---|---|---|
| deviceID | 自定义的设备ID | 符串长度大于0,小 于等于256,否则接 口调用失败 | 当次设置无效 |

```
withDeviceID(deviceID: string): AlibabaCloudRum
```

●

代码示例:

```
AlibabaCloudRum.withAppID("<#AppID#>")
  .withConfigAddress("<#ConfigAddr#>")
  .withDeviceID("custom channelID")
  .start(this.context.getApplicationContext());
```

### 二、数据获取接口

### 获取设备 ID

如果在 SDK 启动时设置了 withDeviceID 接口,那么会返回自定义的 ID

接口说明:

●

```
static getDeviceID(): string
```

●

代码示例:

```
constdeviceID = AlibabaCloudRum.getDeviceID();
console.log("ORSDK: "+deviceID);
```

### 获取SDK当前版本

获取当前 SDK 的版本

接口说明:

●

```
static getSdkVersion(): string
```

●

代码示例:

```
constsdkVersion = AlibabaCloudRum.getSdkVersion();
console.log("ORSDK: "+sdkVersion);
```

### 三、自定义信息设置接口

### 自定义用户名称

SDK支持设置与用户相关的信息,从而完成性能数据与实际用户相关联的需求场景。

接口说明

●

| 参数 | 说明 | 参数限制 | 失败结果 |
|---|---|---|---|
| userName | 用户名称标识 | 字符串可为空或空 串 。 字符串小于等于 256,且不包含特殊 字符(只允许数字 、 字母 中文 冒号 、 、 、 空格 斜杠 下划 、 、 线 连字符 英文句 、 、 号 星号 叹号 、 、 、 @ #,空或空串无 、 效),否则接口调用 失败 | 当次设置无效 |

```
setUserName(userName: string);
```

代码示例:

```
AlibabaCloudRum.setUserID("testName");
```

### 自定义异常

调用接口并传入相应参数,可完成自定义异常数据的统计功能。

接口说明

●

```
static setCustomException(error: Error); //推荐使用,直接将 Exception 或
Throwable 对象传入即可
```

| 参数 | 说明 | 参数限制 | 失败结果 |
|---|---|---|---|
| throwable | 异常对象 | 系统抛出的异常对 象,非null | 当次设置无效 |

代码示例:

●

```
try {
thrownew Error("Test");
} catch (err) {
   AlibabaCloudRum.setCustomException(err);
}
```

更为灵活的重载配置如下,可用于业务型异常上报,有关参数可填充符合参数限制的任意内

容,平台直接展示。

接口说明

●

| 参数 | 说明 | 参数限制 | 失败结果 |
|---|---|---|---|
| exceptionType | 异常类型(必要) | 字符串长度大于0, 小于等于256,否则 接口调用失败 。 | 当次设置无效 |
| causeBy | 异常原因 | 字符串可为空或空 串。 字符串小于等于 512,超长截取。 | - |
| errorDump | 异常信息 | 超出10000字符时 会被切割 | 字符串可为空或空 串。 字符串小于等于 10000,超长截 取。 |

```
static setCustomException(errorType: string, causeBy?: string,
errorDump?: string);
```

代码示例:

●

```
try {
thrownew Error("Test");
} catch (err) {
if (err instanceof Error) {
       AlibabaCloudRum.setCustomException(err.name, err.message,
err.stack);
    }
}
```

### 自定义事件

调用接口并传入相应参数,可完成自定义事件数据统计功能。

接口说明

●

| 参数 | 说明 | 参数限制 | 失败结果 |
|---|---|---|---|
| eventName | 事件名称(必要) | 字符串长度小于等 于256,超长会截取 | 接口调用失败,当 次设置无效 |
| group | 事件分组 | 字符串可为空或空 串。 字符串小于等于 256,超长截取。 | - |
| value | 事件值 | Double 类型 | - |
| snapshots | 事件快照 | 字符串可为空或空 串。 字符串小于等于 7000,超长截取。 | - |
| attributes | kv存储信息 | 可为空,转JSON后 长度在7000字符以 | - |

```
static setCustomEvent(eventName: string, group?: string, value?:
number, snapshots?: string, attributes?: Map<string, string>)
```

|  |  | 内 |  |
|---|---|---|---|

代码示例:

```
AlibabaCloudRum.setCustomEvent("注册");
constinfo = new Map<string, string>();
info.set("eventNumber","10001");
info.set("eventName", "alibaba");
info.set("eventXX", "xxx");
AlibabaCloudRum.setCustomEvent("登录失败", "事件分组", undefined, "事件快
照", info);
```

### 自定义日志

调用接口并传入相应参数,可完成自定义事件数据统计功能。

接口说明

●

| 参数 | 说明 | 参数限制 | 失败结果 |
|---|---|---|---|
| content | 日志信息(必要) | 字符串长度大于0小 于等于10000,超 长截取。 | 接口调用失败,当 次设置无效 |
| name | 日志名称 | 字符串长度大于0且 小于等于256 。 | - |
| snapshots | 日志快照 | 字符串可为空或空 串。 字符串小于等于 7000,超长截取。 | - |
| level | 日志等级 | 字符串长度大于0且 小于等于 256,默 认为 INFO。 | - |

```
static setCustomLog(content: string, name?: string, snapshots?: string,
level?: string, attributes?: Map<string, Object>);
```

| attributes | 日志附加信息 | Map可为空或空集 。 转JSON后,字符串 长度与content共 享,否则接口调用失 败 。 | - |
|---|---|---|---|

代码示例:

```
AlibabaCloudRum.setCustomLog("日志内容1");
constlogInfo = new Map<string, string>();
logInfo.set("logXX","xxx");
AlibabaCloudRum.setCustomEvent("日志内容2", "日志名称", "日志快照",
"ERROR", logInfo);
```
