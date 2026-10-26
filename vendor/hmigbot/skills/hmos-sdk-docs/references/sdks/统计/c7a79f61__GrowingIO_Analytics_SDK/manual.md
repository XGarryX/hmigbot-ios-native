多平台 SDK

HarmonyOS SDK

无埋点

# 无埋点

SDK 自2.3.0起,正式支持无埋点上报和圈选

# 如何集成

## 开启无埋点监听

若您的应用需要使用无埋点功能,在主窗口对应的 Ability的onWindowStageCreate方法中开启无埋点监听:

```
onWindowStageCreate(windowStage: window.WindowStage) {
try {
    windowStage.loadContent('pages/Index',  (err: BusinessError) => {
const errCode: number = err.code
if (errCode) {
        console.error(`Failed to load the content. Cause code: ${err.code}, message: ${err.message}`)
return;
      }
      console.info('Succeeded in loading the content.')
// 在 windowStage.loadContent 完成时,开启无埋点监听
      GrowingAnalytics.onWindowStageCreate(this, windowStage)
    });
  } catch (exception) {
    console.error(`Failed to load the content. Cause code: ${exception.code}, message:
${exception.message}`)
  }
}
```

注意:该监听在未初始化 SDK 之前不会获取任何设备信息,以及产生事件数据

## 开启无埋点采集

在 SDK 初始化时,设置配置项autotrackEnabled为true(2.1.0版本默认为true ,2.2.0版本起,默认为false ,后续版本可能会有所

改动)来开启采集无埋点数据:

```
startAnalytics() {
let config = new GrowingConfig().NewSaaS(
'Your AccountId',
'Your DataSourceId',
'Your UrlScheme',
'Your DataCollectionServerHost<Optional>'
  )
  config.autotrackEnabled = true
  GrowingAnalytics.start(this.context, config)
}
```

## 开启页面浏览事件自动埋点

在 SDK 初始化时,设置配置项autotrackAllPages为true(默认为false )来开启页面浏览事件自动埋点,适配组件导航(Navigation)和

页面路由(@ohos.router):

```
startAnalytics() {
let config = new GrowingConfig().NewSaaS(
'Your AccountId',
'Your DataSourceId',
'Your UrlScheme',
'Your DataCollectionServerHost<Optional>'
  )
  config.autotrackAllPages = true
  GrowingAnalytics.start(this.context, config)
}
```

# 设置页面别名

您也可以通过手动设置页面别名,设置后:

页面路径为对应的别名

无论是否开启页面浏览事件自动埋点,该页面的页面浏览事件都将生成

## 基于组件导航(Navigation)

```
let destination = new NavPathInfo(name, {
"growing_alias": "homePage"
} as Record<string, Object>)
this.pageStack.pushDestination(destination)
```

## 基于页面路由(@ohos.router)

```
router.pushUrl({
  url: path,
  params: {
"growing_alias": "homePage"
  }
})
```

# 设置页面属性

通过手动设置页面属性为该页面添加事件发生时所伴随的属性信息

## 基于组件导航(Navigation)

```
let destination = new NavPathInfo(name, {
"growing_attributes": {
"key1": "value1",
"key2": 100
  } as Record<string, Object>
} as Record<string, Object>)
this.pageStack.pushDestination(destination)
```

## 基于页面路由(@ohos.router)

```
router.pushUrl({
  url: path,
  params: {
"growing_attributes": {
"key1": "value1",
"key2": 100
    }
  }
})
```

# 最佳实践

## 设置组件标识

为了确保点击事件中组件路径的准确性,在必要时,可以对自定义组件添加组件唯一标识符。这是由于自定义组件在其有渲染内容时,其类型为

```
__Common__
```

相关文档:

获取节点的类型:

https://developer.huawei.com/consumer/cn/doc/harmonyos-references/js-apis-arkui-framenode#getnodetype12

组件标识:

https://developer.huawei.com/consumer/cn/doc/harmonyos-references/ts-universal-attributes-component-id

另外,当无法圈选某个可以触发点击事件的组件时,请对该组件添加组件唯一标识符,且添加 GrowingAutotrackElementID 标记,使得 SDK 认

定该组件可以圈选:

```
Button('Not focusable').id('uniqueID-xxx-' + GrowingAutotrackElementID)
```

## 设置页面别名

如果您的应用中有 NavDestination页面名称相同,或 Router目标命名路由页面名称相同的情况,请通过设置页面别名来避免数据分析异常

多平台 SDK

HarmonyOS SDK

初始化配置

# 初始化配置

在初始化过程中,SDK 会接收一个由用户传入的默认配置Config ,配置相关说明如下表:

## 配置表格

| 配置项 | 参数类 型 | 默认 值 | 说明 |
|---|---|---|---|
| accountId | string | - | 项目 ID (AccountID),每个应用对应唯一值 |
| dataSourceId | string | - | 应用的 DataSourceId,唯一值 |
| urlScheme | string | - | 自定义 URL Scheme |
| dataCollectionServerHost | string | - | 服务端部署后的 ServerHost,默认值为 https://napi.growingio.com |
| debugEnabled | boolean | false | 调试模式,开启后会输出 SDK 日志,在线上环境请关闭 |
| sessionInterval | number | 30 | 设置会话后台留存时长,指当前会话在应用进入后台后的最大留存时间,默认为 30 秒。另外,其他情况下也会重新生成一个新的会话,如设置用户 ID 等核心信 息,重新打开数据收集等 |
| dataUploadInterval | number | 15 | 数据发送的间隔,默认为 15 秒。SDK 会先将事件存入数据库中,然后以每隔默认 时间 15 秒向服务器发送事件包 |
| dataCollectionEnabled | boolean | true | 数据收集,当数据收集关闭时,SDK 将不会再产生事件和上报事件 |
| idMappingEnabled | boolean | false | 是否开启多用户身份上报 |
| requestOptions.connectTimeout | number | 30 | 事件请求尝试建立连接的最大等待时间,默认为 30 秒 |
| requestOptions.transferTimeout | number | 30 | 事件请求允许传输数据的最大等待时间,默认为 30 秒 |
| dataValidityPeriod | number | 7 | 本地未上报的事件数据有效时长,默认为 7 天 |
| useProtobuf | boolean | true | 事件请求是否采用 Protobuf 数据格式 |
| encryptEnabled | boolean | true | 事件请求是否开启加密传输,加密上报时,不会明文显示 |
| compressEnabled | boolean | true | 事件请求是否开启压缩传输 (snappy) |

多平台 SDK

HarmonyOS SDK

数据采集API

# 数据采集API

## 初始化是否成功

```
static isInitializedSuccessfully(): boolean
```

返回是否初始化成功

```
let success = GrowingAnalytics.isInitializedSuccessfully()
```

## 数据采集开关

```
static setDataCollectionEnabled(enabled: boolean)
```

打开或关闭数据采集

```
GrowingAnalytics.setDataCollectionEnabled(true)
```

## 设置登录用户 ID

```
static setLoginUserId(userId: string, userKey?: string)
```

当用户登录之后调用,设置登录用户 ID 和用户 Key

INFO

如果您的App每次用户升级版本时无需重新登录的话,为防止用户本地缓存被清除导致的无法被识别为登录用户,建议在用户每次升级

App版本后初次访问时重新调用setLoginUserId方法

当需要标记用户ID类型时,请先进行规划,并在平台的数据中心,添加新的用户身份类型,再设置userkey,误设会影响数据质量。设

置用户 Key需在初始化 SDK 时设置config.idMappingEnabled = true

参数说明

| 参数 | 参数类型 | 说明 |
|---|---|---|
| userId | string | 长度限制大于 0 且小于等于 1000 |
| userkey | string | 长度限制大于 0 且小于等于 1000,默认为 '' |

示例

```
GrowingAnalytics.setLoginUserId('user')
GrowingAnalytics.setLoginUserId('user', 'harmony')
```

## 清除登录用户 ID

```
static cleanLoginUserId()
```

当用户登出之后调用,清除已经设置的登录用户ID

```
GrowingAnalytics.cleanLoginUserId()
```

## 设置用户的地理位置

```
static setLocation(latitude: number, longitude: number)
```

设置用户当前的地理位置,基于WGS-84坐标

参数说明

| 参数 | 参数类型 | 说明 |
|---|---|---|
| latitude | number | 地理坐标点纬度 |
| longitude | number | 地理坐标点经度 |

示例

```
const latitude: number = 30.0
const longitude: number = 120.0
GrowingAnalytics.setLocation(latitude, longitude)
```

## 清除用户的地理位置

```
static cleanLocation()
```

清除用户当前的地理位置

```
GrowingAnalytics.cleanLocation()
```

## 设置埋点事件

```
static track(eventName: string, attributes: GrowingAttrType = {})
```

发送一个埋点事件;注意:在添加发送的埋点事件代码之前,需在分析云平台事件管理界面创建埋点事件以及关联事件属性

INFO

GrowingAttrType为 SDK 限定的事件属性类型,实际为:

```
{ [key: string]: string | number | boolean | string[] | number[] | boolean[] }
```

参数说明

| 参数 | 参数类型 | 说明 |
|---|---|---|
| eventName | string | 事件名,事件标识符 |
| attributes | GrowingAttrType | 事件发生时所伴随的属性信息;当事件属性关联有维度表时,属性值为对应的维度表模型 ID(记录 ID)(可选) |

示例

```
GrowingAnalytics.track('buyProduct1')
GrowingAnalytics.track('buyProduct2', {
'name': 'apple',
'money': 1000,
'num': 100,
'from': ['sichuan', 'guizhou', 'hunan']
})
let attributes: GrowingAttrType = {}
attributes['a'] = 'b'
GrowingAnalytics.track('buyProduct3', attributes)
```

详细使用示例:埋点事件示例

## 事件计时器

```
static trackTimerStart(eventName: string): string
```

初始化一个事件计时器,参数为计时事件的事件名称,返回值为该事件计时器唯一标识

```
static trackTimerPause(timerId: string)
```

暂停事件计时器,参数为trackTimer返回的唯一标识

```
static trackTimerResume(timerId: string)
```

恢复事件计时器,参数为trackTimer返回的唯一标识

```
static trackTimerEnd(timerId: string, attributes: GrowingAttrType = {})
```

停止事件计时器,参数为trackTimer返回的唯一标识。调用该接口会自动触发删除定时器。

```
static removeTimer(timerId: string)
```

删除事件计时器,参数为trackTimer返回的唯一标识。该接口会将标识为timerId的计时器置为空。调用停止计时器接口,会自动触发该接口。

注意移除时不论计时器处于什么状态,都不会发送事件。

```
static clearTrackTimer()
```

清除所有已经注册的事件计时器。存在所有计时器需要清除时调用。注意移除时不论计时器处于什么状态,都不会发送事件。

参数说明

| 参数 | 参数类型 | 说明 |
|---|---|---|
| eventName | string | 事件名,事件标识符 |
| attributes | GrowingAttrType | 事件发生时所伴随的属性信息;当事件属性关联有维度表时,属性值为对应的维度表模型 ID(记录 ID)(可选) |
| timerId | string | 计时器唯一标识符,由trackTimerStart 返回 |

示例

```
let timerId = GrowingAnalytics.trackTimerStart('eventName')
GrowingAnalytics.trackTimerPause(timerId)
GrowingAnalytics.trackTimerResume(timerId)
GrowingAnalytics.trackTimerEnd(timerId)
GrowingAnalytics.trackTimerEnd(timerId, {
'property': 'value',
'property2': 100
})
GrowingAnalytics.removeTimer(timerId)
GrowingAnalytics.clearTrackTimer()
```

注意:

endTimer时发送 CUSTOM 事件上报数据:

eventName埋点事件标识符(trackTimerStart传入)

attributes用户自定义事件属性(trackTimerEnd传入)

event_duration事件时长(SDK 内部根据timerId自动计算获取)

event_duration按照秒上报,小数点精度保证到毫秒

event_duration变量及其值会自动添加在attributes中

event_duration时间统计不会计算后台时间

eventName对应的埋点事件需要在平台中绑定标识符为event_duration,且类型为小数的事件属性

## 设置登录用户属性

```
static setLoginUserAttributes(attributes: GrowingAttrType)
```

以登录用户的身份定义登录用户属性,用于用户信息相关分析

参数说明

| 参数 | 参数类型 | 说明 |
|---|---|---|
| attributes | GrowingAttrType | 用户属性信息 |

示例

```
GrowingAnalytics.setLoginUserAttributes({
'name': 'ben',
'age': 30
})
```

详细使用示例:用户属性事件示例

## 获取设备 ID

```
static getDeviceId(): string
```

获取设备id,又称为匿名用户id,SDK 自动生成用来定义唯一设备

```
let deviceId = GrowingAnalytics.getDeviceId()
```

## 事件通用属性

```
static setGeneralProps(props: GrowingAttrType)
```

为所有自定义埋点事件设置通用属性,多次调用,相同字段的新值将覆盖旧值

```
static removeGeneralProps(keys: string[])
```

移除指定字段的埋点事件通用属性

```
static clearGeneralProps()
```

移除所有埋点事件通用属性

```
static setDynamicGeneralProps(generator: () => GrowingAttrType)
```

设置动态通用属性

参数说明

| 参数 | 参数类型 | 说明 |
|---|---|---|
| props | GrowingAttrType | 事件发生时所伴随的属性信息;当事件属性关联有维度表时,属性值为对应的维度表模型 ID(记录 ID) |

示例

// 设置通用属性

```
GrowingAnalytics.setGeneralProps({
'prop1': 10,
'prop2': 'name',
'prop3': [1, 2, 3],
'prop4': ['a', 'b', 'c'],
'name': 'banana'
})
// 清除指定字段的通用属性
GrowingAnalytics.removeGeneralProps(['prop1', 'prop2', 'prop3'])
// 清除通用属性
GrowingAnalytics.clearGeneralProps()
// 设置动态通用属性
GrowingAnalytics.setDynamicGeneralProps(() => {
return {'dynamicProp' : Util.formatDate(new Date()) }
})
// 清除动态通用属性
GrowingAnalytics.setDynamicGeneralProps(() => ({}))
```

## Hybrid打通

```
static createHybridProxy(controller: webview.WebviewController): {
object: object;
name: string;
methodList: Array<string>;
controller: WebviewController;
} | undefined
```

在webView控件中注入hybrid实现打通(javaScriptAccess和domStorageAccess需同时设置为true):

```
let url = 'https://www.example.com'
Web({ src: url, controller: this.controller})
  .javaScriptAccess(true)
  .domStorageAccess(true)
  .javaScriptProxy(GrowingAnalytics.createHybridProxy(this.controller))
```

对应的 H5页面需要集成Web JS SDK 以及 App内嵌页打通插件才能生效

如果您需要注入多个 JavaScript对象或者通过permission配置权限管控,请在onControllerAttached回调中使用

```
registerJavaScriptProxy进行注入hybrid:
let url = 'https://www.example.com'
// 通过permission配置权限管控
let permission = 'Your Permission'
Web({ src: url, controller: this.controller})
  .javaScriptAccess(true)
  .domStorageAccess(true)
  .onControllerAttached(() => {
let proxy = GrowingAnalytics.createHybridProxy(this.controller)
if (proxy) {
this.controller.registerJavaScriptProxy(proxy.object, proxy.name, proxy.methodList, [],
permission)
    }
// 如果需要注入多个JavaScript对象
let yourProxy = new YourProxy()
if (yourProxy) {
this.controller.registerJavaScriptProxy(yourProxy.object, yourProxy.name, yourProxy.methodList,
yourProxy.async MethodList, permission)
    }
  })
```

## 多实例采集

初始化多实例

| 配置项 | 子实例是否能单独配置 |
|---|---|
| accountId | 是 |
| dataSourceId | 是 |
| urlScheme | 是 |
| dataCollectionServerHost | 是 |
| debugEnabled | 否,以主实例为准 |
| sessionInterval | 是 |
| dataUploadInterval | 是 |
| dataCollectionEnabled | 是 |
| idMappingEnabled | 是 |
| requestOptions.connectTimeout | 是 |

```
let config = new GrowingConfig().NewSaaS(
'SubTracker AccountId',
'SubTracker DataSourceId',
'SubTracker UrlScheme',
'SubTracker DataCollectionServerHost<Optional>'
)
GrowingAnalytics.startSubTracker(trackerId, config)
初始化配置中,accountId/dataSourceId/dataCollectionServerHost都可与主实例不同,具体如下表格:
```

| 配置项 | 子实例是否能单独配置 |
|---|---|
| requestOptions.transferTimeout | 是 |
| dataValidityPeriod | 否,以主实例为准 |
| useProtobuf | 是 |
| encryptEnabled | 是 |
| compressEnabled | 是 |

注意:初始化子实例前必须先初始化主实例

兼容 APIs

子实例可单独调用以下接口,其逻辑与其他实例相互隔离

```
export interface GrowingAnalyticsInterface {
isInitializedSuccessfully(): boolean
setDataCollectionEnabled(enabled: boolean): void
setLoginUserId(userId: string, userKey?: string): void
cleanLoginUserId(): void
setLoginUserAttributes(attributes: GrowingAttrType): void
track(eventName: string, attributes: GrowingAttrType, sendTo?: string[]): void
trackTimerStart(eventName: string): string
trackTimerPause(timerId: string): void
trackTimerResume(timerId: string): void
trackTimerEnd(timerId: string, attributes: GrowingAttrType, sendTo?: string[]): void
removeTimer(timerId: string): void
clearTrackTimer(): void
}
```

假设子实例的trackerId为subTrackerId_01 ,调用方式如下:

// 获取子实例,需要先初始化该子实例,否则下述接口将无法生效

```
let subTracker = GrowingAnalytics.tracker('subTrackerId_01')
// 返回是否初始化成功
let success = subTracker.isInitializedSuccessfully()
if (!success) {
return
}
// 数据采集开关
subTracker.setDataCollectionEnabled(true)
// 登录用户ID
subTracker.setLoginUserId('user')
subTracker.setLoginUserId('user', 'harmony')
subTracker.cleanLoginUserId()
// 设置埋点事件
subTracker.track('buyProduct1')
subTracker.track('buyProduct2', {
'name': 'apple',
'money': 1000,
'num': 100,
'from': ['sichuan', 'guizhou', 'hunan']
})
// 事件计时器
let timerId = subTracker.trackTimerStart('eventName')
subTracker.trackTimerPause(timerId)
subTracker.trackTimerResume(timerId)
subTracker.trackTimerEnd(timerId)
let timerId2 = subTracker.trackTimerStart('eventName2')
subTracker.trackTimerEnd(timerId2, {
'property': 'value',
'property2': 100
})
subTracker.removeTimer(timerId)
subTracker.clearTrackTimer()
// 设置登录用户属性
subTracker.setLoginUserAttributes({
'name': 'ben',
'age': 30
})
// Hybrid 打通
subTracker.createHybridProxy(this.controller)
```

SendTo

可使用sendTo功能将主实例或子实例的自定义事件转发到其他子实例:

```
// 主实例track转发
GrowingAnalytics.track('buyProduct1', {}, ['subTrackerId_01', 'subTrackerId_02'])
GrowingAnalytics.track('buyProduct2', {
'name': 'apple',
'money': 1000,
'num': 100,
'from': ['sichuan', 'guizhou', 'hunan']
}, ['subTrackerId_01', 'subTrackerId_02'])
// 主实例事件计时器转发
let timerId = GrowingAnalytics.trackTimerStart('eventName')
GrowingAnalytics.trackTimerEnd(timerId, {}, ['subTrackerId_01', 'subTrackerId_02'])
let timerId2 = GrowingAnalytics.trackTimerStart('eventName2')
GrowingAnalytics.trackTimerEnd(timerId2, {
'property': 'value',
'property2': 100
}, ['subTrackerId_01', 'subTrackerId_02'])
// 子实例track转发
let subTracker = GrowingAnalytics.tracker('subTrackerId_01')
subTracker.track('buyProduct1', {}, ['subTrackerId_02'])
subTracker.track('buyProduct2', {
'name': 'apple',
'money': 1000,
'num': 100,
'from': ['sichuan', 'guizhou', 'hunan']
}, ['subTrackerId_02'])
// 子实例事件计时器转发
let timerId = subTracker.trackTimerStart('eventName')
subTracker.trackTimerEnd(timerId, {}, ['subTrackerId_02'])
let timerId2 = subTracker.trackTimerStart('eventName2')
subTracker.trackTimerEnd(timerId2, {
'property': 'value',
'property2': 100
}, ['subTrackerId_02'])
```

当前仅track和trackTimerEnd接口支持sendTo转发

多平台 SDK

HarmonyOS SDK

版本记录

# 版本记录

# 2.4.1(2025-08-28)

## Bug Fixes修复

fix:compatibleSdkVersion降低为 API 12

fix:添加UseTsHar标记,以适配 Sendable的使用

# 2.4.0(2025-08-26)

## Features功能

feat:添加事件大小限制,避免sqlite数据库操作异常

## Performance性能优化

perf:并发处理事件发送前的序列化、压缩等逻辑

perf:并发处理事件生命周期期间的数据库操作

# 2.3.0(2025-06-05)

## Features功能

feat:支持原生无埋点圈选(仅 New SaaS,需要开启无埋点采集)

## Bug Fixes修复

fix:优化圈选/Mobile Debugger截图功能的性能,增加防抖机制,减小截图大小

fix:内部emit机制中,eventId使用string类型替代原先的number类型,避免误触发

# 2.2.0(2025-04-08)

## Features功能

feat:支持 Mobile Debugger

chore:buildOption.arkOptions.byteCodeHar改为false,不再作为字节码har发布

feat:支持配置页面属性growing_attributes

## Bug Fixes修复

fix: Debug调试模式下,dataUploadInterval默认为1000ms

fix: SaaS 模式下,移除部分不必要的日志输出

fix:修复首次VISIT事件偶现多发

fix(CDP):修复 Flutter侧传递点击事件到鸿蒙时,丢失pageShowTimestamp字段

fix:修复当返回 NavPathStack首页时,未发送 Page事件

fix:修复当应用从后台返回前台时,未发送基于 Navigation的 Page事件(基于 Router会发)

# 2.1.0(2024-11-14)

## Features功能

feat:支持protobuf数据格式传输

# 2.0.1(2024-10-25)

## Bug Fixes修复

fix:start、track、trackTimerEnd方法签名修正

# 2.0.0(2024-09-10)

从2.0.0开始,本 SDK 基于将于2024年第四季度发布的 HarmonyOS NEXT(5.0.0, API 12)商业稳定版本进行开发,废弃1.x版本对

OpenHarmony和 HarmonyOS(4.x, API 10-11)的兼容(对应 API 版本可以通过集成 Android SDK 进行采集):

从集成体验上,部分对外接口改为同步接口,避免async-await污染

从编译上,发布的 HAR 升级为字节码格式,有效提升应用模块的编译构建效率

从性能上,SDK 初始化耗时从100+ms降低至不到10ms

从稳定性上,修复了更多业务场景下的已知问题

另外,发布 GrowingToolsKit插件1.0.0,旨在帮助用户提高集成 GrowingIO SDK 效率,在使用 SDK 的开发过程中,便于排查问题,为用户提供

最好的埋点服务。

以下是具体改动:

## Refactor(BREAKING CHANGE)破坏性更改

发布的 HAR 升级为字节码格式,需要在工程级build-profile.json5中配置useNormalizedOHMUrl为true

compatibleSdkVersion从4.0.0(10)改为5.0.0(12)

SDK 初始化接口从异步调用方式改为同步,需要更换集成方式(在数据库创建或连接成功之前产生的事件将先在内存中缓存)

事件计时器相关外部接口从异步调用方式改为同步,需要更换集成方式(内部接口更换已废弃的 API systemDatetime.getRealTime为

```
systemDatetime.getUptime )
```

事件数据库开启加密,与1.x版本的事件数据库不兼容,集成2.0.0之后1.x版本未发送的事件将丢弃

INFO

当用非加密方式打开一个已有的加密数据库时,会返回错误码14800011,表示数据库损坏。此时用加密方式可以正常打开该数据库。

https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/js-apis-data-relationalstore-V5#storeconfig

使用推荐的rcp(Remote Communication Kit远场通信服务)替换@ohos.net.http进行事件网络请求

```
初始化配置项requestOptions.readTimeout重命名为requestOptions.transferTimeout ,以符合
rcp.Configuration.transfer对应的配置项名称
```

## Features功能

feat:添加 APP_CLOSED 事件,在应用进入后台时触发,多实例情况下,各个实例都会发送

## Bug Fixes修复

fix:使用applicationStateChange监听应用前后台变化,兼容子窗口存在的场景

fix:修复多实例下 EventSender不会同时发送各实例产生的事件数据(1.x版本主实例在发送事件请求过程中,子实例不会发送事件)

fix:修复采集开关关闭时的逻辑,在 Flutter/Hybrid混合场景下,也能正确判断是否转发事件

fix:dataCollectionEnabled仅控制是否进行采集,不再控制是否发送数据,与iOS/Android SDK 保持一致

fix:修复多实例下,事件的eventSequenceId字段未进行区分,现在各个实例单独计数

fix:修复多实例下,错误使用trackerId作为本地存储key的一部分,现在使用accountId+dataSourceId以兼容更多用户场景

## 其他

fix: SDK 项目名从library改为 GrowingAnalytics

docs:更新、优化所有文档描述

feat:添加 GioKit插件,包括 SDK 信息、事件库、网络记录等功能,支持多实例下展示

# 附:HarmonyOS SDK 2.0.0升级说明

最低适配 HarmonyOS NEXT(5.0.0, API 12)商业稳定版本,compatibleSdkVersion:5.0.0(12)

2.0.0与1.x版本的事件数据库不兼容,集成2.0.0之后1.x版本未发送的事件将丢弃

该说明适用于从1.x版本升级,全新集成2.0.0按照集成文档上的步骤集成即可

## 通过ohpm中心仓更新

```
ohpm update @growingio/analytics
```

## 配置标准化 OHMUrl

在工程级build-profile.json5中配置useNormalizedOHMUrl为true

```
{
"app": {
"products": [
      {
"buildOption": {
"strictMode": {
"useNormalizedOHMUrl": true
          }
        }
      }
    ]
  }
}
```

## 初始化

调整 SDK 初始化代码从异步改为同步:

```
startAnalytics() {
let config = new GrowingConfig().NewSaaS(
'Your AccountId',
'Your DataSourceId',
'Your UrlScheme',
'Your DataCollectionServerHost<Optional>'
  )
  GrowingAnalytics.start(this.context, config)
}
```

## 集成 GioKit(推荐)

```
ohpm install @growingio/tools
```

并在 SDK 初始化时,添加 Giokitplugin:

```
import { GrowingToolsKit } from'@growingio/tools'
let config = new GrowingConfig().NewSaaS(
'Your AccountId',
'Your DataSourceId',
'Your UrlScheme',
'Your DataCollectionServerHost<Optional>'
)
config.plugins = [new GrowingToolsKit()]
GrowingAnalytics.start(this.context, config)
```

注意:请仅在 DEBUG 环境下使用 GrowingToolsKit,RELEASE 环境下 GrowingToolsKit将不会显示

## 初始化配置

```
若您的应用中使用了初始化配置项requestOptions.readTimeout ,请将其替换为requestOptions.transferTimeout
```

## 事件计时器

若您的应用中使用了事件计时器相关接口,将调用方式从异步修改为同步:

```
let timerId = GrowingAnalytics.trackTimerStart('eventName')
GrowingAnalytics.trackTimerPause(timerId)
GrowingAnalytics.trackTimerResume(timerId)
GrowingAnalytics.trackTimerEnd(timerId)
GrowingAnalytics.trackTimerEnd(timerId, {
'property': 'value',
'property2': 100
})
GrowingAnalytics.removeTimer(timerId)
GrowingAnalytics.clearTrackTimer()
```

# 1.2.0(2024-07-26)

## Features

适配 Flutteron HarmonyOS (3.7.12-ohos)

# 1.1.0(2024-06-21)

## Features

适配 HarmonyOS NEXT

支持从 OpenHarmony API 10到 API 12

支持 New SaaS/SaaS/CDP 平台集成

支持多实例采集

支持通用属性

支持hybrid打通

支持事件数据加密压缩上报

新增初始化配置项,如:网络请求超时时长、数据有效时长、加密、压缩等等

## Bug Fixes

优化 SDK 初始化方式,见 README

其他稳定性优化

# 1.0.0(2023-12-14)

## Features

适配 ArkTS 语法

支持 OpenHarmony API 10

# 0.0.1(2023-12-08)

## Features

支持埋点事件上报

支持访问事件自动上报

支持用户属性上报

支持事件计时器

支持用户 ID 配置,包括 ID Mapping

支持数据采集开关配置

支持静态公共属性配置

支持 HarmonyOS 3.1.0(OpenHarmony API 9)
