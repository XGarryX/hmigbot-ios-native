# 集成文档(HarmonyOS Analytics SDK) 

在使用前,请先阅读数据模型 

## 1. 集成神策分析 SDK 

方式一:在 IDE 控制台按照以下命令行完成 SDK 的安装 

(请先咨询技术顾问同学,获取 HarmoyOS SDK 最新安装包 SensorsAnalyticsSDK.har) ,将 SensorsAnalyticsSDK.har 拷贝到鸿蒙项目工程目录下,运 行以下命令: 

ohpm install SensorsAnalyticsSDK.har 

方式二:参考如下配置,在 oh-package.json5 文件中添加依赖指向 SensorsAnalyticsSDK.har 文件放置的位置,然后点击同步。 

(请先咨询技术顾问同学,获取 HarmoyOS SDK 最新安装包 SensorsAnalyticsSDK.har) 

{ "license": "", "devDependencies": {}, "author": "", "name": "sdkdemo", "description": "Please describe the basic information.", "main": "", "version": "1.0.0", "dependencies": { "@sensorsdata/analytics": "file:./src/main/SensorsAnalyticsSDK.har" }, "dynamicDependencies": {} } 

鸿蒙 API 9 配置
对于 API 9 版本的,需要手动配置下  oh_modules/@sensorsdata/analytics/src/main/module.json  的 module.json 文件

## 2. 初始化神策分析 SDK 

### 2.1. 获取项目数据接收地址 

每个项目都有单独的数据接收地址
请使用 管理员 账户获取相应项目的数据接收地址

### 2.2. 初始化 SDK 

在项目 Ability 入口文件 onCreate 方法中参考如下代码初始化 SDK: 

import sensors from '@sensorsdata/analytics'; sensors.init({ // 服务器接收地址 server_url: '你的数据接收地址', // Ability 上下文 context: this.context, // 是否显示日志 show_log: true, // 开启 App 打通 H5 app_js_bridge: true }); 

SDK 只会在调用了 init 后才会上报数据,请确保 init 在合适的时机进行调用。 

#### 2.2.1. 权限配置说明 

SDK 共需要三个权限,需要应用进行配置: 

|权限|用途|
|---|---|
|`ohos.permission.INTERNET`|必须权限,允许应用发送统计数据,SDK 发送埋点数据需要此权限|
|`ohos.permission.GET_NETWORK_INFO`|必须权限,允许应用检测网络状态|
|`ohos.permission.GET_WIFI_INFO`|可选权限,允许应用获取 WIFI 信息|

## 3. SDK 基本配置 

### 3.1. 用户关联 

用户关联是为了对用户进行唯一标识,提高用户行为分析的准确性。目前神策提供了简易用户关联和全域用户关联分为用于支撑不同的业务场景。 

简易用户关联(IDM 2.0) 全域用户关联(IDM 3.0) 

### 3.2. 设置事件公共属性 

对于所有事件都需要添加的属性,初始化 SDK 后,可以通过 registerSuperProperties() 将属性注册为公共属性。详细使用文档参见基础 API 功能介绍。 

### 3.3. 记录激活事件 

可以调用 trackAppInstall() 方法记录激活事件,多次调用此方法只会在第一次调用时触发激活事件。 

### 3.4. 代码埋点追踪事件 

SDK 初始化后,可以通过 track() 方法追踪用户行为事件,并为事件添加自定义属性。详细使用文档参见基础 API 功能介绍。 

## 4. 调试查看事件信息 

初始化 SDK 时,进行以下配置,即可打开 SDK 的日志输出功能: 

// 打开 SDK 的日志输出功能 show_log: true 

在 IDE 日志面板 中筛选 sensorsdatasdk 关键词展示 SDK 日志。 

## 5. SDK 可选配置 

### 5.1. 打通 App 与 H5 

初始化 SDK 时,进行如下配置,即可开启 App 打通 H5 功能 

// 开启 App 打通 H5 app_js_bridge: true 

注意:App 端需要在 Web 控件中参考如下代码注入打通对象到 Web 控件,在 onControllerAttached 回调里调用  createH5BridgeProxy 方
法:
import sensors from '@sensorsdata/analytics';
...
url = 'https:// .... ';
controller = new web_webview.WebviewController()
...
Web({ src: this.url, controller: this.controller })
.javaScriptAccess(true)
// 在 onControllerAttached 回调里调用 createH5BridgeProxy 方法
.onControllerAttached(() => {
    console.log('onControllerAttached');
    sensors.createH5BridgeProxy(this.controller)
})
打通原理:通过  Web 控件 的 registerJavaScriptProxy 方法注入 SDK 桥接对象实现,打通功能需要 App 和 H5 同时开启才可以生效,H5 开启 ()
方法请参考 App 打通 H5。
