# **HarmonyOS** 用户运营 **SDK API** 接口文档 

## 接口类说明 

### 本文档所有接口所涉及的相关类及说明如下: 

|接口|说明|
|---|---|
|Ido|SDK功能接口类,用于调用SDK相关功能|
|IdoConfg|SDK配置接口类,用于设SDK相关参数(**注意:**IdoConfg配置需要在 SDK初始化之前配置。)|
|预初始化 类名|**Ido**|
|接口|preInit(context: Context): void|

#### 说明: 

预初始化 SDK ,读取配置参数,此时用户运营服务未启动, gtcid 并未生成,用户运营功能未启 动。 

#### 参数: 

context : Context 提供了 ability 或 application 的上下文的能力,包括访问特定应用程序的资源等。 

## 初始化 

|类名|**Ido**|
|---|---|
|接口|init(context: Context): Promise<string>|

#### 说明: 

初始化成功后 SDK 将自动生成应用活跃时长事件。 

#### 参数: 

context : Context 提供了 ability 或 application 的上下文的能力,包括访问特定应用程序的资源等。 

#### 返回值: 

返回一个含有 gtcId 的 Promise 

获取版本号

类名 Ido
接口 getVersion(): string
说明:
获取 SDK 版本号。
自定义事件
计数事件
类名 Ido
接口 onEvent(eventId: string, attrs: EventAttributes, ext?: string): void

#### 说明: 

每次在事件触发时调用 onEvent 方法,应用统计平台根据 eventId ,统计该事件触发的次数。 

#### 参数: 

eventId :自定义事件 Id ,用于标识事件的唯一 

attrs: 自定义属性,用于扩展统计需求 

#### 代码示范: 

// 计数统计事件 const map1 = new Map<string, string | number | Date | boolean>() map1.set('test1', 1) map1.set('test2', '2') map1.set('test3', true) map1.set('test4', new Date()) Ido.onEvent('event1', map1) 

### 用户属性 

|类名|**Ido**|
|---|---|
|接口|onProfle(attrs: EventAttributes, ext?: string): void|

#### 说明: 

设置用户属性,用于记录用户基本固定不变的属性,例如性别、年龄、注册时间、注册地域、注 册渠道等。 

#### 参数: 

attrs: 自定义用户属性,用于扩展统计需求 

#### 代码示范: 

// 用户属性事件 const map3 = new Map<string, string | number | Date | boolean>() map3.set('test1', 1) map3.set('test2', '2') map3.set('test3', true) map4.set('test4', new Date()) Ido.onProfile(map3) 

## 设置开发者模式 

类名 **IdoConfig** 接口 setDebugEnable(enable: boolean): void 

说明 

开启 / 关闭开启开发者模式,开发者模式下,将在 logcat 输出 SDK 相关日志。 

请在调试的时候使用该接口,切勿发布到线上版本。 

#### 参数: 

enable :开启 / 关闭开启开发者模式

设置 AppId

类名 IdoConfig
接口 setAppId(appId: string): void
说明

设置 appid ,这里设置的 appid 优先级比 module.json5 文件中配置的 appid 优先级更高。 

请在 Ido 初始化之前调用。

参数:

appId :从个推开发者平台申请的 appid 

设置计数事件上传频率
类名 IdoConfig
接口 setEventUploadInterval(timeMillis: number): void

#### 说明 

设置计数事件的上传频率 eventUploadInterval ,默认值为 10000 ,即 10 秒; 

- 上传计数事件前会先检测上次上传操作的时间,如果距离上次上传操作已经过去了 eventUploadInterval 这么多时间,则会触发事件上传操作,否则将等待下次符合要求再上 传。 

#### 参数 

timeMillis :设置的 eventUploadInterval 值,单位毫秒。 

## 设置计数事件事件强制上传条数 

|类名|**IdoConfg**|
|---|---|
|接口|setEventForceUploadSize(size: number): void|

#### 说明 

- 设置计数事件的强制上传条数 eventForceUploadSize ,默认数量为 30 条; 

如果距离上次上传计数事件的时间不满足 eventUploadInterval 频率限制, SDK 还会去检测现有的 离线计数事件条数,如果超过 eventForceUploadSize 这个条数,则会强制触发上传。 

#### 参数 

size :设置的 eventForceUploadSize 值。 

## 设置用户属性事件上传频率 

|类名|**IdoConfg**|
|---|---|
|接口|setProfleUploadInterval(timeMillis: number): void|

#### 说明 

- 设置用户属性事件传频率 profileUploadInterval ,默认值为 5000 ,即 5 秒; 

- 上传用户属性事件前会先检测上次上传操作的时间,如果距离上次上传操作已经过去了 profileUploadInterval 这么多时间,则会触发事件上传操作,否则将等待下次符合要求再上 传。 

#### 参数 

timeMillis :设置的 profileUploadInterval 值,单位毫秒。 

## 设置用户属性事件强制上传条数 

|类名|**IdoConfg**|
|---|---|
|接口|setProfleForceUploadSize(size: number): void|

#### 说明 

- 设置用户属性事件的强制上传条数 profileForceUploadSize ,默认数量为 5 条 ; 

如果距离上次上传用户属性事件的时间不满足 profileUploadInterval 频率限制, SDK 还会去检测现 有的离线用户属性事件条数,如果超过 profileForceUploadSize 这个条数,则会强制触发上传。 

#### 参数 

size :设置的 profileForceUploadSize 值。 

## 设置会话超时时长 

#### 类名 

#### **IdoConfig** 

接口 setSessionTimeoutMillis(sessionTimeoutMillis: number): void 

#### 说明 

- 应用从前台退至后台,在后台运行时间超过 sessionTimeout 后,此时再回到前台, SDK 将 一 

- 认为是 次全新的启动。 

sessionTimeout 的默认值为 30 秒。 

#### 参数 

timeoutMillis : sessionTimeout 值,单位毫秒 

## 设置最小有效活跃时长 

类名 

#### **IdoConfig** 

接口 setMinAppActiveDuration(minAppActiveDuration: number): void 

#### 说明 

- SDK 统计应用前台活跃时长时,会对时长做判定,如果该时长小于 minAppActiveDuration , SDK 将认为无效,不予上传。 

minAppActiveDuration 的默认值为 0 ; 

#### 参数 

minAppActiveDuration :最小有效活跃时长,单位毫秒 

## 设置最大有效活跃时长 

|类名|**IdoConfg**|
|---|---|
|接口|setMaxAppActiveDuration(maxAppActiveDuration: number): void|

#### 说明 

- SDK 统计应用前台活跃时长时,会对时长做判定,如果该时长大于 maxAppActiveDuration , SDK 将认为无效,不予上传。 

maxAppActiveDuration 的默认值为 12 小时。 

#### 参数 

maxAppActiveDuration :最大有效活跃,单位毫秒
