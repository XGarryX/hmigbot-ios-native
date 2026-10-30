> 来源: ohpm 中央仓 README(T1 信源) | 包: `@sensorsdata/analytics` | ohpm 最新版: 0.0.2 | 抓取: 2026-07-16
> 注意: 版本可能比市场快照新,以此为准时核对 CHANGELOG

# SensorsData HarmonyOS Analytics SDK

## 神策简介

[**神策数据**](https://www.sensorsdata.cn/)
(Sensors Data),隶属于神策网络科技(北京)有限公司,是一家专业的大数据分析服务公司,大数据分析行业开拓者,为客户提供深度用户行为分析平台、以及专业的咨询服务和行业解决方案,致力于帮助客户实现数据驱动。神策数据立足大数据及用户行为分析的技术与实践前沿,业务现已覆盖以互联网、金融、零售快消、高科技、制造等为代表的十多个主要行业、并可支持企业多个职能部门。公司总部在北京,并在上海、深圳、合肥、武汉等地拥有本地化的服务团队,覆盖东区及南区市场;公司拥有专业的服务团队,为客户提供一对一的客户服务。公司在大数据领域积累的核心关键技术,包括在海量数据采集、存储、清洗、分析挖掘、可视化、智能应用、安全与隐私保护等领域。 [**More**](https://www.sensorsdata.cn/about/aboutus.html)

## SDK 简介

神策 HarmonyOS Analytics SDK 支持手动调用相应埋点 APIs 采集埋点事件。
- 支持 OpenHarmony API Level 9、API Level 10

## 集成文档

###  通过 ohpm 集成

```yaml
ohpm install @sensorsdata/analytics
```

OpenHarmony ohpm 环境配置等更多内容,请参考[如何安装 OpenHarmony ohpm 包](https://gitee.com/openharmony-tpc/docs/blob/master/OpenHarmony_har_usage.md)

### 通过本地 har 集成
首先将下载的 SensorsAnalyticsSDK.har 放入项目根目录,再执行以下命令:

```yaml
ohpm install ./SensorsAnalyticsSDK.har
```

## 初始化 SDK
在项目 Ability 入口文件 onCreate 方法中参考如下代码初始化 SDK:

```javascript
import sensors from '@sensorsdata/analytics';
sensors.init({
    // 服务器接收地址
    server_url: '数据接收地址',
    // Ability 上下文
    context: this.context,
    // 是否显示日志
    show_log: true,
    // 是否开启采集位置信息,需要 app 授权,默认 false
    enable_track_location: true,
    // 是否开启批量发送,默认 false  
    batch_send: true,
    // 数据发送超时时间
    datasend_timeout: 10000,
    // 开启 App 打通 H5
    app_js_bridge: true
});
```

> SDK 只会在调用了 init 后才会上报数据,请确保 init 在合适的时机进行调用。

###  权限配置说明
| 权限 | 用途                              |
|----|---------------------------------|   
| ohos.permission.INTERNET | 必须权限,允许应用发送统计数据,SDK 发送埋点数据需要此权限 |
| ohos.permission.GET_NETWORK_INFO| 必须权限,允许应用检测网络状态                 |
| ohos.permission.GET_WIFI_INFO| 可选权限,允许应用获取 WIFI 信息             |、 ## SDK 基本使用 ### 设置事件公共属性 对于所有事件都需要添加的属性,初始化 SDK 后,可以通过 `registerSuperProperties` 将属性注册为公共属性。详细使用文档参见基础 API 功能介绍。 ### 记录激活事件 可以调用 `trackAppInstall` 方法记录激活事件,多次调用此方法只会在第一次调用时触发激活事件。 ### 代码埋点追踪事件 SDK 初始化后,可以通过 `track` 方法追踪用户行为事件,并为事件添加自定义属性。详细使用文档参见基础 API 功能介绍。 ### 调试查看事件信息 初始化 SDK 时,进行以下配置,即可打开 SDK 的日志输出功能```javascript
// 打开 SDK 的日志输出功能  
show_log: true
```

### App 与 H5 打通
初始化 SDK 时,进行如下配置,即可开启 App 打通 H5 功能:

```javascript
// 开启 App 打通 H5
app_js_bridge: true
```

App 端需要在 Web 控件中参考如下代码注入打通对象到 Web 控件:

```java
import sensors from '@sensorsdata/analytics';
...
url = 'https:// .... ';
controller = new web_webview.WebviewController()
...

Web({ src: this.url, controller: this.controller })
.javaScriptAccess(true)
.javaScriptProxy(sensors.createH5BridgeProxy(this.controller))

```

打通原理:通过 Web 控件的 `javaScriptProxy` 方法注入 SDK 桥接对象实现,打通功能需要 App 和 H5 同时开启才可以生效,H5 开启方法请参考 App 打通 H5。

## License

Copyright 2015-2024 Sensors Data Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
