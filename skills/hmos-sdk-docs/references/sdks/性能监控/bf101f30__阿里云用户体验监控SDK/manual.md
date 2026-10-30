# HarmonyOS NEXT 使用指南

ARMS 用户体验监控提供了鸿蒙(HarmonyOS)SDK 用于监控鸿蒙应用。本文介绍如何集

成 HarmonyOS SDK 并将应用接入用户体验监控。

# 版本要求

●

手机的@ohos.deviceInfo.sdkApiVersion值需为12-13。

●

Stage应用的compatibleSdkVersion不低于5.0.0(12)。

# 接入指南

### 步骤一:创建应用

1.登录ARMS控制台。

2.在左侧导航栏选择用户体验监控 > 应用列表,并在顶部菜单栏选择目标地域。

3.在应用列表页面单击添加应用。

4.在创建应用面板单击HarmonyOS。

5.在HarmonyOS面板输入应用名称和描述,然后单击创建。

说明:应用名称唯一,不能与已创建的应用名称重复。

创建成功后,当前应用将会自动生成对应的 ConfigAddress(上报地址)和 AppID。

### 步骤二:集成 SDK

第一步:鸿蒙 RUM SDK 已发布到第三方仓库中,可以通过如下两种方式集成 SDK:

●

方式一:在 Terminal 窗口中,切换到模块级目录,执行如下命令安装三方包,DevEco

Studio 会自动在该模块的 oh-package.json5 中自动添加三方包依赖。

```
cd path/to/your/project
ohpm config set registry https://ohpm.openharmony.cn/ohpm/
ohpm install @alibabacloud_rum/harmony_sdk
```

●

方式二:在工程的 oh-package.json5 中 dependencies 增加 sdk har 包依赖,配置如

下:

```
"dependencies": {
"@alibabacloud_rum/harmony_sdk": "^0.1.1"
}
```

依赖设置完成后,需要执行 ohpm install 命令安装依赖包,依赖包会安装到工程的

oh_modules 目录下。

```
ohpm install
```

第二步:Rebuild 项目,确保配置生效

### 步骤三:接入 SDK

### 1.配置授权信息

检查应用程序 module.json5 配置文件,确保已引入如下授权:

```
ohos.permission.INTERNET            发送网络数据
ohos.permission.GET_NETWORK_INFO    获取网络状态信息
```

### 2.配置 ohmurl 规则

将工程级或模块级 build-profile.json5 中的 useNormalizedOHMUrl 修改为 true, 若没有

该配置项请手动添加。

```
{
"app" : {
"products": [{
"buildOption": {
"strictMode": {
"useNormalizedOHMUrl": true
          }
        }
    }]
  }
}
```

### 3.初始化 SDK

在入口 entry moudle 自定义 AbilityStage 中的 onCreate 函数中,添加如下代码

```
AlibabaCloudRum.withAppID("<your appid>") // AppID 在创建 RUM 应用时获取
      .withConfigAddress("<your config address") // ConfigAddress 在创建
RUM 应用时获取
      .start(this.context.getApplicationContext());
```

代码示例

```
onCreate(): void {
this.initAlibabaCloudRumSdk();
}
private initAlibabaCloudRumSdk() {
  AlibabaCloudRum.withAppID("<your appid>")
    .withConfigAddress("<your config address")
    .start(this.context.getApplicationContext());
}
```

### 4.网络采集

```
目前支持采集框架hms.collaboration.rcp,ohos.net.http,ohos.net.webSocke
t,ohos.net.socket.TCPSocket,ohos.net.socket.UDPSocket,当采集对应网络框
```

架时,需要使用 AlibabaCloudRumTrace 引用这些框架类,各网络框架 API 使用同官网文

档,如下是每个网络采集示例。

●

'hms.collaboration.rcp'

```
需要在rcp.createSessionAPI 前添加AlibabaCloudRumTrace开头引用
import { rcp } from'@kit.RemoteCommunicationKit';
import { AlibabaCloudRumTrace } from'@alibabacloud_rum/harmony_sdk';
// 示例1: 无参数传递
letsession1 = AlibabaCloudRumTrace.rcp.createSession(); // 这里要添加
AlibabaCloudRumTrace 开头引用
// 示例2: 有参数传递
letsession2 = AlibabaCloudRumTrace.rcp.createSession({}); // 这里要添加
AlibabaCloudRumTrace 开头引用
```

| ohos.net.webSocke |  |
|---|---|

|  | t |
|---|---|

●

'ohos.net.http'

```
需要在http.createHttpAPI 前添加AlibabaCloudRumTrace开头引用。
import { http } from'@kit.NetworkKit';
import { BusinessError } from'@kit.BasicServicesKit';
import { AlibabaCloudRumTrace } from'@alibabacloud_rum/harmony_sdk';
lethttpRequest = AlibabaCloudRumTrace.http.createHttp(); // 这里要添加
AlibabaCloudRumTrace 开头引用
letoptions: http.HttpRequestOptions = {};
letpromise = httpRequest.request(
'request url', options
);
promise.then((responseData: http.HttpResponse) => {
}).catch((err: BusinessError) => {
})
```

●

'ohos.net.webSocket'

```
需要在webSocket.createWebSocket API 前添加AlibabaCloudRumTrace开头引用。
import { webSocket } from'@kit.NetworkKit';
import { AlibabaCloudRumTrace } from'@alibabacloud_rum/harmony_sdk';
letwebSocketInstance: webSocket.WebSocket =
AlibabaCloudRumTrace.webSocket.createWebSocket(); // 这里要添加
AlibabaCloudRumTrace 开头引用
```

●

'ohos.net.socket.TCPSocket'

```
需要在调用socket.constructTCPSocketInstance API 前添加AlibabaCloudRumTrace
```

开头引用。

```
import { socket } from'@kit.NetworkKit';
import { AlibabaCloudRumTrace } from'@alibabacloud_rum/harmony_sdk';
lettcpSocketInstance: AlibabaCloudRumTrace.socket.TCPSocket =
AlibabaCloudRumTrace.socket.constructTCPSocketInstance(); // 这里要添加
@alibabacloud_rum/agent 开头引用
```

'ohos.net.socket.UDPSocket'

●

```
需要在socket.constructUDPSocketInstance API 前添加AlibabaCloudRumTrace开头
```

引用。

```
import { socket } from'@kit.NetworkKit';
import { AlibabaCloudRumTrace } from'@alibabacloud_rum/harmony_sdk';
letudpSocketInstance: AlibabaCloudRumTrace.socket.UDPSocket =
AlibabaCloudRumTrace.socket.constructUDPSocketInstance(); // 这里要添加
AlibabaCloudRumTrace 开头引用
```

### 5.视图/启动数据采集

●

Ability 数据采集

在 UIAbility 的子类声明上添加@AlibabaCloudRumTrace.InjectAbility 装饰器

```
import { AlibabaCloudRumTrace } from'@alibabacloud_rum/harmony_sdk';
@AlibabaCloudRumTrace.InjectAbility
export defaultclassEntryAbilityextends UIAbility {
onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void {
  }
onWindowStageCreate(windowStage: window.WindowStage): void {
  }
onForeground(): void {
  }
onBackground(): void {
  }
onWindowStageDestroy(): void {
  }
onDestroy() {
  }
}
```

●

AbilityStage 数据采集

在 AbilityStage 的子类声明上添加@AlibabaCloudRumTrace.InjectStage 装饰器

```
import { AlibabaCloudRumTrace } from'@alibabacloud_rum/harmony_sdk';
@AlibabaCloudRumTrace.InjectStage
export defaultclassEntryAbilityStageextends AbilityStage {
onCreate() {
  }
onMemoryLevel(level: AbilityConstant.MemoryLevel): void {
  }
}
```

●

Page 数据采集

在 Page 结构下面添加AlibabaCloudRumTrace.InjectPage(Index) 接口调用并传入当

前结构, Page 生命周期 (

aboutToAppear,onPageShow,onPageHide,aboutToDisappear) 函数尽量复写,否则影响

快照数据采集和性能准确性。

```
import { AlibabaCloudRumTrace } from'@alibabacloud_rum/harmony_sdk';
@Entry
@Component
struct Index {
  build() {
  }
  aboutToAppear(): void {
  }
  onPageShow(): void {
  }
  onPageHide(): void {
  }
  aboutToDisappear(): void {
  }
}
AlibabaCloudRumTrace.InjectPage(Index)
```

### 6.Web 数据采集

●

采集 Web 性能数据

设置采集接口共有两种方案:

第一种: (*推荐)

在 javaScriptOnDocumentStart、onControllerAttached 中分別添加

AlibabaCloudRumTrace.Web.getScriptItem()、

AlibabaCloudRumTrace.Web.onControllerAttachedHilt(this.controller)

```
import { AlibabaCloudRumTrace } from'@alibabacloud_rum/harmony_sdk';
Web()
  .javaScriptOnDocumentStart([AlibabaCloudRumTrace.Web.getScriptItem()])
  .onControllerAttached(() => {
    AlibabaCloudRumTrace.Web.onControllerAttachedHilt(this.controller);
// this.controller:必须是当前Web绑定的WebviewController
  })
```

第二种:

在 onPageEnd 中添加 AlibabaCloudRumTrace.Web.onPageEndHilt(this.controller)

```
import { AlibabaCloudRumTrace } from'@alibabacloud_rum/harmony_sdk';
Web()
  .onPageEnd((event) => {
    AlibabaCloudRumTrace.Web.onPageEndHilt(this.controller);
// this.controller:必须是当前Web绑定的WebviewController
  })
```

●

采集 Web 异常数据

在 onErrorReceive、onHttpErrorReceive、onSslErrorEventReceive 中添加对应

AlibabaCloudRumTrace.Web 的方法

```
import { AlibabaCloudRumTrace } from'@alibabacloud_rum/harmony_sdk';
Web()
  .onErrorReceive((event) => {
if (!event) {
return;
    }
    AlibabaCloudRumTrace.Web.onErrorReceive(event.request, event.error,
this.controller.getWebId()); // this.controller:必须是当前Web绑定的
WebviewController
  })
  .onHttpErrorReceive((event) => {
if (!event) {
return;
    }
    AlibabaCloudRumTrace.Web.onHttpErrorReceive(event.request,
event.response, this.controller.getWebId()); // this.controller:必须是当
前Web绑定的WebviewController
  })
  .onSslErrorEventReceive((event) => {
    AlibabaCloudRumTrace.Web.onSslErrorEventReceive(event.error,
this.controller.getWebId()); // this.controller:必须是当前Web绑定的
WebviewController
  })
```

### 7.接入验证

a.如何验证 SDK 是否已经接入成功

| AlibabaCloudRum.withAppID(<your app id>).start(this.c |  |
|---|---|

```
ontext.getApplicationContext()一同配置.withOpenHilog(),开启日志打印开关,需
```

要在调用 start 函数之前 withAppID 之后进行相关配置。

```
AlibabaCloudRum.withAppID("<your appid>") // AppID 在创建 RUM 应用时获取
      .withConfigAddress("<your config address") // ConfigAddress 在创建
RUM 应用时获取
      .withOpenHilog()
      .start(this.context.getApplicationContext());
```

|  | ontext.getApplicationContext() |
|---|---|

启动应用后,查看 DevEco-studio Hilog 日志,搜索 ORSDK

```
ORSDK-Agent   I   starting...         (注:Agent 集成成功)
ORSDK-Agent   I   OpenRum token*****   (注:Agent 启动成功)
```

# 接口说明

### 一、启动配置接口

| AlibabaCloudRum.withAppID("<your app id>").s |  |
|---|---|

|  | tart(this.context.getApplicationContext()) |
|---|---|

withAppID 之后进行相关配置, 可同时配置多项, start 函数后配置无效。

### 设置自定义APP版本

通过此方法设置了自定义设备 App 版本号,那么 SDK 将会上报此版本号,不再使用默认

获取的版本号.

接口说明

●

| 参数 | 说明 | 参数限制 | 失败结果 |
|---|---|---|---|
| version | 自定义的版本号 | 字符串长度大于 0, 小于等于 64,否则 接口调用失败 | 当次设置无效 |

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
| environment | 应用环境枚举 | 仅可使用预置枚举 单位,否则接口调 用失败,枚举类型 「0:NONE 无环境 配置,1:PROD 线上 环境,2:GRAY 灰度 环境,3:PRE 预发环 境,4:DAILY 日常环 境,5:LOCAL 本地环 境」 | 当次设置无效 |

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

注意:SDK 内部预置了应用环境枚举单位,预置单位类型见 AppEnvironment 枚举类

### 使用自定义冷启动结束时间

是否使用自定义冷启动结束时间

接口说明:

●

| 参数 | 说明 |
|---|---|
| used | boolean 类型,true:使用自定义冷启动结 束,false:不使用自定义冷启动结束时间 |

```
withUseCustomLaunch(used: boolean):AlibabaCloudRum
```

●

代码示例:

```
AlibabaCloudRum.withAppID("<#AppID#>")
  .withConfigAddress("<#ConfigAddr#>")
  .withUseCustomLaunch(true)
  .start(this.context.getApplicationContext());
```

### 设置SDK自身请求Header

本接口用于设置对于 SDK 自身发起的网络请求中添加自定义请求头

接口说明:

●

| 参数 | 说明 | 失败结果 |
|---|---|---|
| headers | 要设置的请求头键值对(最 多设置 64 个,key 长度限 制 256 个字符,value 长度 限制 512 个字符) | key,value 长度限制则单条数 据无效 |

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
| channelID | 自定义的渠道号 | 符串长度大于 0,小 于等于 256,否则接 口调用失败 | 当次设置无效 |

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
| deviceID | 自定义的设备 ID | 符串长度大于 0,小 于等于 256,否则接 口调用失败 | 当次设置无效 |

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

SDK 支持设置与用户相关的信息,从而完成性能数据与实际用户相关联的需求场景。

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

| 参数 | 说明 | 参数限制 | 失败结果 |
|---|---|---|---|
| throwable | 异常对象 | 系统抛出的异常对 象,非 null | 当次设置无效 |

```
static setCustomException(error: Error); //推荐使用,直接将 Exception 或
Throwable 对象传入即可
```

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
| exceptionType | 异常类型(必要) | 字符串长度大于 0, 小于等于 256,否则 接口调用失败 。 | 当次设置无效 |
| causeBy | 异常原因 | 字符串可为空或空 串。 | - |

```
static setCustomException(errorType: string, causeBy?: string,
errorDump?: string);
```

|  |  | 字符串小于等于 512,超长截取。 |  |
|---|---|---|---|
| errorDump | 异常信息 | 超出 10000 字符时 会被切割 | 字符串可为空或空 串。 字符串小于等于 10000,超长截 取。 |

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
| eventName | 事件名称(必要) | 字符串长度小于等 于 256,超长会截 取 | 接口调用失败,当 次设置无效 |
| group | 事件分组 | 字符串可为空或空 串。 字符串小于等于 256,超长截取。 | - |

```
static setCustomEvent(eventName: string, group?: string, value?:
number, snapshots?: string, attributes?: Map<string, string>)
```

| value | 事件值 | Double 类型 | - |
|---|---|---|---|
| snapshots | 事件快照 | 字符串可为空或空 串。 字符串小于等于 7000,超长截取。 | - |
| attributes | kv 存储信息 | 可为空,转 JSON 后 长度在 7000 字符 以内 | - |

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
| content | 日志信息(必要) | 字符串长度大于 0 小于等于 10000, 超长截取。 | 接口调用失败,当 次设置无效 |
| name | 日志名称 | 字符串长度大于 0 且 小于等于 256 。 | - |

```
static setCustomLog(content: string, name?: string, snapshots?: string,
level?: string, attributes?: Map<string, Object>);
```

| snapshots | 日志快照 | 字符串可为空或空 串。 字符串小于等于 7000,超长截取。 | - |
|---|---|---|---|
| level | 日志等级 | 字符串长度大于 0 且小于等于 256, 默认为 INFO。 | - |
| attributes | 日志附加信息 | Map 可为空或空 集 。 转 JSON 后,字符 串长度与 content 共 享,否则接口调用失 败 。 | - |

代码示例:

```
AlibabaCloudRum.setCustomLog("日志内容1");
constlogInfo = new Map<string, string>();
logInfo.set("logXX","xxx");
AlibabaCloudRum.setCustomEvent("日志内容2", "日志名称", "日志快照",
"ERROR", logInfo);
```

# SDK 版本说明

| 版本 | 发布时间 | 发布说明 |
|---|---|---|
| v0.1.1 | 2024 年 11 月 21 日 | 修复已知问题 支持自定义事件 支持自定义日志 |
| v0.1.0 | 2024 年 11 月 14 日 | 发布 Harmony NEXT SDK 的初始版本 0.1.0 。 |
