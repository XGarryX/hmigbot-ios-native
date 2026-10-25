# Harmony接入文档_2026.5.27 

## 基本信息 

SDK 名称:热力引擎 Harmony SDK 

开发者名称:汇量云(北京)科技有限公司 

SDK 版本号: 1.8.0 

SDK 包名: @solarengine/core 

MD5 值: 8c1767222786552a73376c73f859422c 

主要功能:热力引擎是一站式增长分析与发行决策平台,致力于帮助开发者搭建便捷、高效 的数据管理中台,洞察业务运营全链路数据,制定更优增长决策。热力引擎支持全球全渠道 数据管理,帮助开发者实现归因分析、用户粒度 ROI 分析,能有效衡量渠道价值,为投放和 变现策略调优提供全方位数据支持。同时,提供应用内埋点及参数管理,配合多种分析模型 与 AB 测试功能,全面还原用户全生命周期旅程,挖掘用户需求及业务增长点,快速验证并 推行产品迭代优化,为开发者提升业务运营效率,实现规模化增长赋能。 

适用范围:适用于 Harmony APILevel 20 及以上版本,且仅支持 Stage 应用模型。 

隐私政策链接: https://www.solar-engine.com/privacyPolicy.html 

合规指南: https://help.solar-engine.com/cn/docs/he-gui-zhi-nan-roat 

## 一 : 第 步 获取 **Appkey** 

Appkey 查询路径:资产管理 - 应用管理 -16 位 Appkey (即应用 ID )。 

## 第二步:导入 **SDK** 

##### 两种方式导入 SDK 

##### 方式一:通过鸿蒙仓库导入 SDK 

##### 进入工程 entry 目录,执行以下命令: 

```
ohpm install @solarengine/core
```

方式二:通过本地 har 包导入 SDK

1. 下载 SDK : SolarEngine-Harmony-v1.8.0 

2. 将下载的 SolarEngineCorex.x.x.har 放入工程 libs 目录,执行以下命令: 

```
//your_project_path/entry/libs/SolarEngineCorex.x.x.har是har包路径
ohpminstall your_project_path/entry/libs/SolarEngineCorex.x.x.har
```

## 第三步:配置权限 

##### 在项目中找到项目配置文件 module.json5 ,加入如下权限: 

```
ohos.permission.INTERNET//必须权限,允许应用发送网络请求。
ohos.permission.GET_NETWORK_INFO//必须权限,允许应用检测网络状态。
ohos.permission.APP_TRACKING_CONSENT//必须权限,允许应用获取oaid。注:须在
获得此权限后再初始化sdk,如果缺少此权限,会影响设备归因
ohos.permission.STORE_PERSISTENT_DATA//必须权限,允许应用卸载时保留
distinctid,用于设备归因。
```

## : 第四步 配置混淆 

如果打包时需要开启混淆配置,请将下方代码增加到混淆配置文件中 

```
-keep
./oh_modules/@solarengine/core
```

## 第五步:预初始化 **SDK** 

在应用安装后首次冷启动时,需要先预初始化 SDK ,预初始化时 SDK 不采集任何个人信息 也不会向热力引擎上报数据 , 

请请确保用户同意《隐私政策》并且 SDK 预初始化成功后,再调用初始化函数正式初始化 SDK 

##### 方法示例 

```
public staticpreInit(context: Context, appKey: string)
```

##### 参数说明 

|参数名称|参数含义|参数类型|是否必传|
|---|---|---|---|
|context|应用程序上下文对象|Context|是|
|appKey|第一步获取的 Appkey|string|是|

##### 调用示例 

```
import {SolarEngineManager} from '@solarengine/core'
SolarEngineManager.preInit(getContext(), appkey)
```

看到 solar engine sdk preInit success! 代表预初始化成功了 

## : 第六步 初始化配置(可选) 

##### **SolarEngineConfig** 参数说明 

本配置类用于初始化 SDK 时,对服务能力与数据采集行为进行精细化控制,分为核心功能开 关、辅助功能开关、数据采集开关三类参数。 

此方法返回的 **config** 配置作为可选参数,如未设置则为默认值 

```
letconfig = newSolarEngineConfig();
config.enable2GReporting = true;
config.isDebugMode = true;
```

#### 一 、核心功能开关配置 

##### 控制 SDK 核心业务能力的启用 / 停用,直接决定归因、分析等核心服务是否生效。 

|方法名|参 数 类 型 是 否 必 填|说明 示例|
|---|---|---|
|enableAtt ribution|boo lean 否|是否开启归因服务,默认开启。关闭后将 停用全部归因相关能力,无法获取归因结 果、延迟deeplink、deeplink等相关服 务;若同时关闭分析服务,SDK将停止上 报所有数据。 confg.enableAttri bution=true;|
|二、辅助功 控制SDK的 非核心业务的 enableAn alytics|能开关 运行模式、 运行行为。 boo lean 否|调试日志、网络策略、授权等待、辅助功能(如延迟Deeplink)等 是否开启分析服务,默认开启。关闭后 A/B测试、在线参数等所有分析类功能均 无法使用;若同时关闭归因服务,SDK将 不再上报任何数据。 confg.enableAnal ytics=true;|
|方法名|参 数 类 型|是 否 必 填 说明 示例|
|logEnabled|void|否 是否开启本地调试日志,默认为 false,不开启 confg.logEnabled=true ;|
|enable2GR orting|ep boo lean|否 是否在2G网络时上报事件,默 认为false,不上报 confg.enable2GReport ing=true;|

|isDebugMode|boo lean|否|是否开启Debug模式,默认为 false,不开启,使用前请查看功 能说明|confg.isDebugMode=t rue;|
|---|---|---|---|---|
|enableDeferre|boo|否|否是启用延迟deeplink功能,默|confg.enableDeferred|
|dDeeplink|lean||认为false,不开启|Deeplink=true;|
|authorizationTi|nu|否|等待用户授权结果的最大时长,|confg.authorizationTim|
|meout|mb||单位为毫秒,默认使用SDK内部|eout=120;|
||er||等待时长||

#### 三、数据采集开关 

控制 SDK 的运行模式、调试日志、网络策略、授权等待、辅助功能(如延迟 Deeplink )等 非核心业务的运行行为。 

|方法名|参 数 类 型|是 否 必 填|说明|示例|
|---|---|---|---|---|
|enableIPV6|boo lean|否|是否采集ipv6地址,不采集设置为false, 默认true(采集)|confg.enableIPV6= true;|
|enableLang uage|boo lean|否|是否采集设备语言,不采集设置为false, 默认true(采集)|confg.enableLangu age=true;|
|enableLoca le|boo lean|否|是否采集设备所在地区,不采集设置为 false,默认true(采集)|confg.enableLocal e=true;|
|enableTime Zone|boo lean|否|是否采集设备所在时区,不采集设置为 false,默认true(采集)|confg.enableTimeZ one=true;|
|enableScre enWH|boo lean|否|是否采集屏幕宽度/屏幕高度,不采集设 置为false,默认true(采集)|confg.enableScree nWH=true;|
|enableDen sity|boo lean|否|是否采集屏幕密度,不采集设置为false, 默认true(采集)|confg.enableDensit y=true;|
|enableNet workType|boo lean|否|是否采集网络状态,不采集设置为false, 默认true(采集)|confg.enableNetwo rkType=true;|
|enableUA|boo lean|否|是否采集UA,不采集设置为false,默认 true(采集)|confg.enableUA=tr ue;|

|enableOAI|boo|否|是否采集OAID,不采集设置为false,默|confg.enableOAID|
|---|---|---|---|---|
|D|lean||认true(采集)|=true;|
|enableODI|boo|否|是否采集ODID,不采集设置为false,默|confg.enableODID|
|D|lean||认true(采集)|=true;|
|enableAAID|boo|否|是否采集AAID,不采集设置为false,默|confg.enableAAID=|
||lean||认true(采集)|true;|

## 第七步:初始化 **SDK** 

必须保证热力引擎 **SDK** 初始化成功后再调用其他方法,如初始化成功之前调用其他方法会 不生效(设置公共事件属性、设置 **channel** 、设置预置事件自定义属性方法除外)。 

##### 方法示例 

|参数说明 `public s` `config: `|`tatic async initialize(context: Con` `SolarEngineConfig)`|
`text, appKey: string, `|
|---|---|---|
|参数名称|参数含义|参数类型 是否必传|
|context|应用程序上下文对象|Context 是|
|appKey|第一步获取的Appkey|string 是|
|confg|配置项可以为空,如果为空则为默认值|SolarEngineConfg 否|

##### 调用示例 

```
import {SolarEngineManager,SolarEngineConfig, InitSDKListener } from
'@solarengine/core'
letonInitListener: InitSDKListener = {
onInitComplete: (code: number) => {
  console.error(TAG, `初始化完成,返回码: ${code}`);
}
};
//设置SDK初始化回调
SolarEngineManager.setInitSDKListener(onInitListener);
//SDK初始化
SolarEngineManagerinitialize(getContext()"yourappkey");
```

如果开启了本地调试日志开关,看到 solar engine SDK init success 代表初始化成功了 

##### 初始化回调 **code** 码: 

|0|初始化成功|
|---|---|
|101|SDK未预初始化|
|102|appkey非法|
|103|context为空|
|104|数据库初始化失败|
|105|distinct_id生成失败|

## : 第八步 获取归因回调信息 

### **8.1 SDK** 提供两种方式获取归因结果信息 

#### 方式一:设置归因结果回调获取归因结果 

注:请在 SDK 初始化前设置归因结果回调,因为 SDK 初始化时可能会立即给归因结果回调, 在 SDK 初始化后设置可能会导致接收不到归因结果回调。 

##### 方法示例 

public static setAttributionListener(attributionListener:
AttributionListener)
调用示例

```
import { SolarEngineManager, AttributionListener} from
'@solarengine/core'
let attributionListener: AttributionListener = {
  onAttributionSuccess(attribution:Record<string, Object>) {
//获取归因结果成功
  },
  onAttributionFailed(errorCode: number) {
//获取归因结果失败
  }
};
//设置归因回调监听
SolarEngineManager.setAttributionListener(attributionListener);
//初始化SDK
SolarEngineManager.initialize(getContext(),"开发者申请的appkey");
```

#### 方式二:直接获取归因结果 

直接获取归因结果的方法返回的是本地缓存,如果本地缓存还未生成,那么归因结果将会为 {} 

##### 方法示例 

public static getAttribution(): Record<string, Object>
返回值 : 返回归因结果信息,如无则返回默认值 :   {}
调用示例

```
import { SolarEngineManager} from '@solarengine/core'
```

`let attribution = SolarEngineManager.getAttribution();` 归因 errorCode 描述及 归因结果详情见: 归因结果详情
