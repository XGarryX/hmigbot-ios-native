> 来源: ohpm 中央仓 README(T1 信源) | 包: `@volcengine/apmplus` | ohpm 最新版: 2.1.0 | 抓取: 2026-07-16
> 注意: 版本可能比市场快照新,以此为准时核对 CHANGELOG

# APMPlus Harmony 性能稳定性监控

## 一、简介
火山引擎是字节跳动旗下的云服务平台,火山引擎 APMPlus Harmony SDK,支持对Harmony OS Next平台的APP进行监控,可以查看线上真实用户的稳定性、性能、自定义埋点数据,帮助研发及时发现线上异常、定位排障,助力企业通过监控数据有效优化用户体验。
【APMPlus平台】https://www.volcengine.com/product/apmplus

核心优势
* 接入成本低,非侵入式SDK,初始化即可监控JS崩溃、AppFreeze、Native崩溃,也支持启动监控、自主事件打点、网络监控、自定义打点回捞。
* 丰富的异常现场还原能力。提供了丰富的现场还原能力,包括且不限于堆栈回溯、日志抓取、用户交互还原等。
* 更灵活的采样方式,提供了多种采样配置,支持按功能模块设置采样、按用户设置采样,以帮助您节省事件量。

## 二、APMPlus SDK 接入

### 2.1 创建产品
需要在火山引擎平台注册账号,然后在应用性能监控全链路版控制台创建应用。创建完成后可以在平台看到AppID、AppToken。具体的接入应用文档:https://www.volcengine.com/docs/6431/70797
产品创建后需要购买事件可以在平台查看上报数据,试用可以在火山平台联系在线客服,提供AppID申请免费试用额度。具体开通服务文档:https://www.volcengine.com/docs/6431/75599

### 2.2 集成SDK
通过 ohpm 安装APMPlus SDK。

```shell
ohpm i @volcengine/apmplus@2.0.7
```

### 2.3 初始化SDK
SDK初始化需要尽早完成,建议在 AbilityStage 或者 Ability 的 onCreate 生命周期中。初始化代码参考如下:

```
    APMPlus.init(this.context);
    
    APMPlus.setDeviceId("device_id");//可选,设备device_id,不返回会使用内部内置默认device_id
    APMPlus.setUserId("user_id");//可选,用户标识,没有默认值。
    let builder = new APMPlusBuilder("AppID", "AppToken");//必填
    builder.debug = true;//可选,测试阶段配置有输出日志
    builder.channel = "volcengine";//可选,渠道
    builder.startMonitor = true;//可选,是否开启启动监控
    builder.netMonitor = true;//可选,是否开启网络监控 后续需要使用HttpMonitor进行监控
    builder.logRecovery = true;//可选,是否开启自定义Vlog打点回捞能力
    builder.versionCode = BuildProfile.VERSION_CODE;//可选,应用versionCode
    builder.versionName = BuildProfile.VERSION_NAME;//可选,应用versionName
    APMPlus.start(builder);
```

详细接入文档:https://www.volcengine.com/docs/6431/1256322

## 三、更多信息
更详细的接入文档、功能介绍、最佳实践请参考【应用性能监控全链路版】 https://www.volcengine.com/docs/6431/69088 也可以在官网咨询在线客服获取更多支持。
