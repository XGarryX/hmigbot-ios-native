# **API** 

## **SDK配置选项** 

```
import common from '@ohos.app.ability.common'
export enum LogLevel {
  DEBUG,
  INFO,
  WARN,
  ERROR,
  NONE
}
export type RecordRule = {
  // 需要采集此参数的域名/URL配置。目标URL包含于这项配置才会采集,如果不配置本条规则会对所有URL
生效
  url?: string
  // 获取全部请求头, 默认空
  reqHeaders?: string[]
  // 请求体配置, 默认空
  reqBody?: string[]
  // 获取全部返回头, 默认空
  resHeaders?: string[]
  // 返回体配置, 默认空
  resBody?: string[]
}
export type NetworkConfig = {
  // 网络请求采集开关, 默认false
  enabled?: boolean
  // 跨应用追踪开关, 默认false
  trackingEnabled?: boolean
  // 采集header body开关, 默认false
  recordEnabled?: boolean
  // 采集数据白名单
  recordConfig?: RecordRule[]
  // 采集数据黑名单
  recordBlockConfig?: RecordRule[]
  // 采集的body截断长度, 单位KB
  bodyMaxSize?: number
  // 第三方apm请求头支持
  apms?: string[]
  // trace propagators
  propagators?: string[]
}
export type CrashConfig = {
  // 崩溃采集总开关, 默认true
  enabled?: boolean
  // js崩溃采集开关, 默认true
  jsCrashEnabled?: boolean
  // cpp崩溃采集开关, 默认true
  cppCrashEnabled?: boolean
}
export type FreezeConfig = {
  // 卡死监控开关, 默认false
  enabled?: boolean
}
export type LaunchWaitingPolicy = {
  cold?: {
    // 启动耗时事件等待时间, 默认30000ms
    launchEvent?: number
    // ability生命周期等待时间, 默认10000ms
    ability?: number
    // page生命周期等待时间, 默认15000ms
    page?: number
  },
  hot?: {
    // 启动耗时事件等待时间, 默认15000ms
    launchEvent?: number
    // 启动耗时事件等待时间, 默认10000ms
    ability?: number
  }
}
export type UserExperienceConfig = {
  // 总开关, 默认false
  enabled?: boolean
  // 启动监控开关, 默认true
  launchEnabled?: boolean
  // 页面监控开关, 默认true
  pageEnabled?: boolean
  // 操作监控开关, 默认true
  userActionEnabled?: boolean
  // 自定义启动时间结束点开关, 默认false
  customLaunchEnd?: boolean
  // 全量trace采集开关, 默认false
  traceEnabled?: boolean
  // 慢操作阈值, 默认3000ms
  slowUserActionThreshold?: number
  // 慢启动阈值, 默认3000ms
  slowLaunchThreshold?: number
  // 热启动阈值, 默认30s
  hotStartThreshold?: number
  // 慢可交互阈值, 默认1000ms
  slowPageLoadThreshold?: number
  // 慢首屏阈值, 默认3000ms
  slowPageDurationThreshold?: number
  // 启动耗时计算等待策略
  launchWaitingPolicy?: LaunchWaitingPolicy
  // 判断为操作错误的错误请求占比, 默认100
  actionFailureThreshold?: number
}
export type UserActionConfig = {
  // 总开关, 默认false
  enabled?: boolean
}
export type WebviewConfig = {
  // 总开关, 默认false
  enabled?: boolean
  // web sdk注入开关, 默认true
  webSdkEnabled?: boolean
  // 注入jsProxy开关, 默认true
  jsProxyEnabled?: boolean
  // JS片段注入开关, 默认true
  jsSnippetEnabled?: boolean
  // web sdk数据压缩开关, 默认false
  // 当平台支持压缩功能时,后端可以通过下发的配置开关控制是否启用压缩,如需手动配置压缩开关,必须
确保后端平台实际支持该功能
  webSdkCompressEnabled?: boolean
}
/**
 * 应用配置
 */
export type InitConfig = {
  // redirect服务器地址
  redirectHost: string
  // 应用appKey
  appKey: string
  // 上下文
  context: common.Context
  // 日志级别, 默认LogLevel.INFO
  logLevel?: LogLevel
  // 数据是否使用http发送数据, 默认false, 使用https发送
  httpEnabled?: boolean
  // axios对象, 需要拦截axios时需要传入
  axios?: any
  // 最大获取的栈深度, 默认20
  stackDepth?: number
  // 是否使用历史数据协议上报(平台3.8.0.0和以下版本平台需要设置为true),默认false
  legacyDataProtocol?: boolean
  // 构建ID
  buildId?: string
  // init内部部分逻辑是否采用异步初始化, 默认false
  async Init?: boolean
  // 是否启用国密加密方式上传数据, 默认false
  encEnabled?: boolean
  // 是否开启数据压缩上传, 默认true
  compressEnabled?: boolean
  // SDK请求超时时间, 单位ms, 默认15000ms, 最小设置3000ms, 设置低于最小值将回退为默认值
  timeout?: number
  // 网络请求采集配置
  network?: NetworkConfig
  // Crash监控配置
  crash?: CrashConfig
  // AppFreeze监控配置
  freeze?: FreezeConfig
  // 用户体验配置
  ue?: UserExperienceConfig
  // 用户行为分析配置
  ua?: UserActionConfig
  // webview配置
  webview?: WebviewConfig
}
```

##### 说明: 

1. init传入的配置为SDK初始配置,在SDK与服务端通信后会优先以服务端下发的配置为准 

## **网络请求** 

### **Axios** 

SDK支持 `@ohos/axios` 库网络请求采集, 可以使用下面2种方式监控axios: 

1. `tingyun.init` 时传入axios实例 

```
import tingyun from '@tingyun/sdk-core'
import axios from '@ohos/axios'
tingyun.init({
   // 传入axios实例对象
   axios: axios
})
```

2. 使用 `tingyun.registerAxiosInstance` 注册axios实例, 可以注册多个实例API定义: 

```
export type Tingyun = {
  registerAxiosInstance: (axiosInstance: AxiosInstance) => void
}
```

##### 示例: 

```
import tingyun from '@tingyun/sdk-core'
import { axiosInstance1, axiosInstance2 } from './utils/axios'
tingyun.registerAxiosInstance(axiosInstance1)
tingyun.registerAxiosInstance(axiosInstance2)
// ...
```

##### 说明: 

1. 两种方式可以同时使用, 相同axios实例只会被注册一次 

2. 首次启动时, SDK默认关闭网络请求开关, 如果需要监控首次启动时的网络请求, 需要在 `tingyun.init` 时配置网络请求开关默认为true 

```
tingyun.init({
  network: {
    enabled: true
  }
})
```

### **RCP** 

SDK通过提供拦截器的方式支持对RCP(remote communication platform)的监控。用户需要在调用 `createSession` 时加入SDK提供的拦截器 

```
import tingyun from '@tingyun/sdk-core'
const session = rcp.createSession({
  // ...
  // 加入拦截器
  interceptors: [new tingyun.RCPInterceptor()]
})
```

### **SDK网络请求接口** 

SDK对系统 `@ohos.net.http` 包 `HttpRequest.request` 接口进行了封装,对外暴露了 `request` 接口。 调用这个接口发送的网络请求会被SDK采集 

API定义: 

```
import http from '@ohos.net.http';
export type HttpRequestWrapperOptions = {
  url: string
  options?: http.HttpRequestOptions
  // http.createHttp() 返回的request对象,如果不传SDK内部会创建。不传httpRequest时,SDK
内部只会在用户传入callback时在用户callback执行完后同步调用httpRequest.destroy。传入
httpRequest时, SDK除了调用httpRequest.request之外不会调用其他方法。如果需要调用
httpRequest其他方法、自行控制destroy时机以及使用promise方式时,需要传入httpRequest
  httpRequest?: http.HttpRequest
}
export interface HttpRequestWrapper {
  (options: HttpRequestWrapperOptions, callback:
AsyncCallback<http.HttpResponse>): void
  (options: HttpRequestWrapperOptions): Promise<http.HttpResponse>
}
export type Tingyun = {
  // ...
  // http request封装
  request: HttpRequestWrapper
}
使用示例: 示例1: 传递URL (promise) 
tingyun.request({url: 'xxx'})
  .then((res) => {
    // ...
  })
  .catch((err) => {
    // ...
  })
```

##### 示例2: 传递URL (callback) 

```
tingyun.request({url: 'xxx'}, (err, res) => {
  // ...
})
```

##### 示例3: 传递URL和options (promise) 

```
tingyun.request({url: 'xxx', options: {
  method: http.RequestMethod.POST,
  header: {
    'Content-Type': 'application/json'
  },
  extraData: {
    // ...
  }
}})
.then((res) => {
  // ...
})
.catch((err) => {
  // ...
})
```

##### 示例4: 传递URL和options (callback) 

```
tingyun.request({url: 'xxx', options: {
  method: http.RequestMethod.POST,
  header: {
    'Content-Type': 'application/json'
  },
  extraData: {
    // ...
  }
}}, (err, res) => {
  // ...
})
```

##### 示例5: 使用自定义请求对象 

```
const httpRequest = http.createHttp()
tingyun.request({
  url: 'xxx',
  httpRequest: httpRequest
}, (err, res) => {
  // ...
})
```

### **自定义请求** 

为了支持用户使用的一些自定义网络请求库,SDK对外提供一套可以收集用户自身采集的网络库信息的 ArkTS层API。为了满足多种使用场景,  提供两种使用模式: 

1. 模式1:请求发起时和请求结束后分别调用SDK API,SDK在请求结束API被调用时,收集这条网络 请求 第一种模式又分为2种使用方式: 

   - 请求开始前调用 `tingyun.startRequest` ,结束后调用 `tingyun.endRequest` , 两次调用都传 递一个自行维护的请求ID关联同一个请求。这种方式调用比较灵活,但需要自行维护一个请求 ID标识一个请求,如果现有的请求库本身提供了请求ID,或者请求开始和结束的代码结构比较 分散时,适合用这种方式 

   - 请求开始前调用 `tingyun.startRequest` 获取到SDK返回的请求实例,请求结束后调用请求实 例的end方法结束请求。这种方式不需要自行维护请求ID,但代码结构较为复杂时,可能需要 自行传递请求实例对象, 如果发送请求代码逻辑比较简单,在单一函数内完成时,适合用这种 方式 

2. 模式2:请求结束后或任意时刻, 一次性调用 `tingyun.createRequest` , 上报一条完整的网络请求数 据 

#### **模式1: startRequest / endRequest** 

##### API定义: 

```
export type Tingyun = {
  // 开始自定义请求
  startRequest: (options: RequestStartOptions) => IRequestInstance
  // 结束自定义请求
  endRequest: (options: RequestEndOptions) => void
}
export interface IRequestInstance {
  end: (options?: RequestEndOptions) => void
  clear: () => void
  readonly id: string
}
export type RequestMethod = 'OPTIONS' | 'GET' | 'HEAD' | 'POST' | 'PUT' |
'DELETE' | 'TRACE' | 'CONNECT'
export type KeyValueStore<T> = Record<string, T> | Map<string, T>
export const LibNames = {
  Flutter: 10,
  OhosHttp: 13,
  OhosAxios: 14,
  OhosRCP: 15
} as const
export type LibName = typeof LibNames[keyof typeof LibNames]
export type RequestStartOptions = {
  // 请求URL
  url: string
  // 请求ID: 请求唯一标识, 不传SDK将自动生成一个UUID格式字符串
  id?: string
  // 请求开始时间: 13位毫秒时间戳, 如果不传SDK将接口调用时间点作为开始点
  startTime?: number
  // method: 默认为GET
  method?: RequestMethod
  // 网络库名称
  libName?: LibName
  // 请求头
  reqHeaders?: KeyValueStore<string>
  // 请求体: 仅支持传文本类型, 如果是JSON格式需要序列化为字符串传入
  reqBody?: string
  // 发送字节数
  bytesSent?: number
  // 请求对象超时清理时间, 单位毫秒: 开始请求一段时间后如果不调用endRequest, SDK内会自动清理
当前请求释放资源, 默认为90000ms
  timeout?: number
}
export type RequestEndOptions = {
  // 请求ID: 请求唯一标识, 当使用Tingyun.endRequest时必传,当使用请求实例对象结束时不传
  id?: string
  // http状态码
  statusCode?: number
  // 错误码: 网络错误或其他错误的错误码, 请求成功或发生http错误(4xx, 5xx), 不需要传
  errorCode?: number
  // 请求结束时间: 13位毫秒时间戳, 如果不传SDK将接口调用的时间点作为结束点
  endTime?: number
  // 请求总耗时, 单位毫秒: 如果不传使用endTime - startTime计算
  duration?: number
  // dns耗时, 单位毫秒: dns结束时间 - dns开始时间
  dns?: number
  // 建立连接时间, 单位毫秒: 建立连接结束时间 - 建立连接开始时间
  connect?: number
  // ssl握手时间, 单位毫秒: ssl握手结束时间 - ssl握手开始时间
  ssl?: number
  // 首包, 单位毫秒: 首包结束时间 - 首包开始时间
  firstPacket?: number
  // 剩余包, 单位毫秒: 剩余包结束时间 - 剩余包开始时间
  remainPacket?: number
  // 本地排队时间, 单位毫秒
  localQueue?: number
  // 发送字节数: 会覆盖startRequest时传递的bytesSent
  bytesSent?: number
  // 接收字节数
  bytesReceived?: number
  // 请求目标地址服务端IP
  ip?: string
  // 请求头: 会覆盖startRequest时传递的reqHeaders
  reqHeaders?: KeyValueStore<string>
  // 请求体: 仅支持传文本类型, 如果是JSON格式需要序列化为字符串传入. 会覆盖startRequest时传
递的reqBody
  reqBody?: string
  // 返回头
  resHeaders?: KeyValueStore<string>
  // 返回体: 仅支持传文本类型的返回体, 如果是JSON格式需要序列化为字符串传入
  resBody?: string
  // 错误信息
  errorMessage?: string
  // 错误堆栈
  errorStack?: string
  // 链路追踪第三方apm请求头
  apms?: KeyValueStore<string>
  // 包含Tingyun APM的原始返回头和值
  tyApm?: KeyValueStore<string>
}
```

示例1: 使用startRequest/endRequest,自定义请求ID 

```
import tingyun from '@tingyun/sdk-core'
async function testRequest1() {
  // 自定义请求ID
  const reqId = genRequestId()
  const url = 'https://example.com'
  const method = 'POST'
  const reqBody = {
    key1: 1
  }
  const reqHeaders = {
    'Content-Type': 'application/json;charset=UTF-8'
  }
  // 请求开始前, 调用startRequest开始请求
  tingyun.startRequest({
    id: reqId,
    url: url,
    method: method,
    reqHeaders: reqHeaders,
    reqBody: JSON.stringify(reqBody)
  })
  try {
    // 调用自己的请求库
    const response = await callCustomHttpLib(url, {
      method: method,
      reqBody: reqBody,
      reqHeaders: reqHeaders
    })
    // 请求成功, 调用endRequest结束请求, 传递标识请求的请求ID
    tingyun.endRequest({
      id: reqId,
      statusCode: response.statusCode,
      resHeaders: response.headers,
      resBody: response.body
    })
  } catch(e) {
    // 请求失败, 调用endRequest结束请求, 传递标识请求的请求ID
    tingyun.endRequest({
      id: reqId,
      errorCode: e.code
    })
  }
}
```

##### 示例2: 使用startRequest返回的请求实例结束请求 

```
import tingyun from '@tingyun/sdk-core'
async function testRequest2() {
  const url = 'https://example.com'
  const method = 'POST'
  const reqBody = {
    key1: 1
  }
  const reqHeaders = {
    'Content-Type': 'application/json;charset=UTF-8'
  }
  // 请求开始前, 调用startRequest开始请求, 并获取请求实例
  const requestInstance = tingyun.startRequest({
    url: url,
    method: method,
    reqHeaders: reqHeaders,
    reqBody: JSON.stringify(reqBody)
  })
  try {
    // 调用自己的请求库
    const response = await callCustomHttpLib(url, {
      method: method,
      reqBody: reqBody,
      reqHeaders: reqHeaders
    })
    // 请求成功, 使用请求实例的end方法结束请求
    requestInstance.end({
      statusCode: response.statusCode,
      resHeaders: response.headers,
      resBody: response.body
    })
  } catch(e) {
    // 请求失败, 使用请求实例的end方法结束请求
    requestInstance.end({
      errorCode: e.code
    })
  }
}
```

**模式2: createRequest** 

API定义: 

```
export type Tingyun = {
  createRequest: (options: RequestOptions) => void
}
// RequestStartOptions RequestEndOptions 见上方
export type RequestOptions = Omit<RequestStartOptions & RequestEndOptions, 'id' |
'timeout'>
```

##### 示例: 

```
async function testRequest3() {
  const url = 'https://example.com'
  const method = 'POST'
  const reqBody = {
    key1: 1
  }
  const reqHeaders = {
    'Content-Type': 'application/json;charset=UTF-8'
  }
  // 设置开始时间
  const startTime = Date.now()
  let endTime
  try {
    // 调用自己的请求库
    const response = await callCustomHttpLib(url, {
      method: method,
      reqBody: reqBody,
      reqHeaders: reqHeaders
    })
    // 设置结束时间
    endTime = Date.now()
    // 请求成功, 调用createRequest创建自定义请求
    tingyun.createRequest({
      url: url,
      startTime: startTime,
      endTime: endTime,
      statusCode: response.statusCode,
      reqHeaders: reqHeaders,
      resHeaders: response.headers,
      resBody: response.body
    })
  } catch(e) {
    // 设置结束时间
    endTime = Date.now()
    // 请求失败, 调用createRequest创建自定义请求
    tingyun.createRequest({
      url: url,
      startTime: startTime,
      endTime: endTime,
      errorCode: e.code
    })
  }
}
```

## **用户体验监控** 

### **注册UIContext** 

##### 页面和操作监控需要注册UIContext 

##### API定义: 

```
export Tingyun = {
  registerUIContext(uiContext: UIContext)
}
```

##### 使用方式: 

```
import tingyun from '@tingyun/sdk-core'
export default class EntryAbility extends UIAbility {
  onWindowStageCreate(windowStage: window.WindowStage): void {
    windowStage.loadContent('pages/Index', (err, data) => {
      // 获取当前UIAbility的主窗口
      windowStage.getMainWindow((err: BusinessError, data) => {
        const uiContext = data.getUIContext()
        // 注册当前窗口的UIContext
        tingyun.registerUIContext(uiContext)
      })
    });
  }
}
```

### **操作监控** 

##### SDK支持采集用户点击事件 

##### 使用方式: 

1. 注册UIContext 

2. 在需要采集的组件上设置 `id` 属性或添加自定义属性 `_ty_name` 来设置操作名称, 自定义属性的优先 级高于 `id` 示例: 

```
Button('clickTest')
  // 设置组件ID
  .id('<自定义操作名称>')
  // 自定义属性
  .customProperty('_ty_name', '<自定义操作名称>')
  .onClick(() => {
  })
```

### **自定义操作** 

API定义: 

```
export type ActionStartOptions = {
  // 父级操作的key, 不传视为顶级操作
  parent?: string
  // 事件唯一标识, 不传则使用name作为唯一标识
  key?: string
  // 操作开始时间, 毫秒时间戳, 不传取调用时间
  startTime?: number
}
export type ActionEndOptions = {
  // 操作名称
  name?: string
  // 事件唯一标识, 不传则使用name作为唯一标识
  key?: string
  // 操作结束时间, 毫秒时间戳, 不传取调用时间
  endTime?: number
  // 自定义tag
  tag?: string
  // 自定义信息
  metaData?: KeyValueStore<ValueType>
}
export interface IActionInstance {
  end: (options?: ActionEndOptions) => void
  readonly key: string
  readonly name: string
}
export type Tingyun = {
  // 开始用户操作
  startAction: (name: string, options?: ActionStartOptions) => IActionInstance
  // 结束用户操作
  endAction: (options: ActionEndOptions) => void
}
```

##### 使用方式: 

##### 示例1: 基本使用 

```
// 开始操作
const action = tingyun.startAction('action1')
// ...
// 结束操作
action.end()
```

##### 示例2: 传递自定义tag和附加信息 

```
// 开始操作
const action = tingyun.startAction('action1')
// ...
// 结束操作
action.end({
  // tag
  tag: 'tag1',
  // 附加信息
  metaData: {
    prop1: ''
  }
})
```

##### 示例3: 自定义开始时间和结束时间 

```
// 开始操作
const action = tingyun.startAction('action1', {
  startTime: <13位毫秒时间戳>
})
// ...
// 结束操作
action.end({
  endTime: <13位毫秒时间戳>
})
```

### **自定义冷启动耗时结束点** 

##### API定义: 

```
export type CustomLaunchOptions = {
  className?: string
}
export type Tingyun = {
  // 自定义启动结束时间
  setCustomLaunchTime: (options?: CustomLaunchOptions) => void
}
```

##### 使用方式: 

1. SDK启动时设置 `customLaunchEnd` 为true 

```
import tingyun from '@tingyun/sdk-core'
tingyun.init({
  // ...
  ue: {
     customLaunchEnd: true
  }
})
```

2. 在冷启动结束时调用 `tingyun.setCustomLaunchTime` 

```
import tingyun from '@tingyun/sdk-core'
tingyun.setCustomLaunchTime()
```

## **Webview数据采集** 

API定义: 

```
export type Tingyun = {
  // 注册webController
  registerWebviewController: (controller: webview.WebviewController) => void
  // 获取需要注入的JS代码
  getWebScriptItem: (scriptRules?: string[]) => any
}
```

使用方式: 

```
import tingyun from '@tingyun/sdk-core'
Web({ src: 'xxxx', controller: this.controller })
  // 确保javaScriptAccess和domStorageAccess都是开启状态
  .javaScriptAccess(true)
  .domStorageAccess(true)
  .onControllerAttached(() => {
    // onControllerAttached回调中调用tingyun.registerWebviewController
    tingyun.registerWebviewController(this.controller)
  })
  // 注入webview监控所需的JS代码
  .javaScriptOnDocumentStart([tingyun.getWebScriptItem()])
```

## **自定义错误** 

API: 

```
export const ErrorTypes = {
  // 自定义错误
  CUSTOM: 1,
  // SDK捕获的错误
  CAPTURED: 2
} as const
export type ErrorType = typeof ErrorTypes[keyof typeof ErrorTypes]
export type ErrorInfo = {
  // 堆栈
  stack?: string
  // 线程id
  threadId?: number
  // 线程名称
  threadName?: string
}
export type KeyValueStore<T> = Record<string, T> | Map<string, T>
export type ValueType = string | number | boolean | object
export type ErrorOptions = {
  // 错误类型, 默认为自定义错误
  type?: ErrorType
  // 错误补充信息
  error?: ErrorInfo
  // 附加信息
  metaData?: KeyValueStore<ValueType>
}
export type Tingyun = {
  // 自定义错误
  reportError: (message: string, options?: ErrorOptions) => void
}
```

##### 使用方式: 

```
import tingyun from '@tingyun/sdk-core'
tingyun.reportError('<customError>')
```

## **自定义用户附加信息** 

API: 

```
export type Tingyun = {
  setCustomData: (key: string, message: string) => void
}
```

##### 使用方式: 

```
import tingyun from '@tingyun/sdk-core'
tingyun.setCustomData('<key>', '<value>')
```

## **自定义面包屑** 

##### API: 

```
export type Tingyun = {
  leaveBreadcrumb: (breadcrumb: string) => void
}
```

##### 使用方式: 

```
import tingyun from '@tingyun/sdk-core'
tingyun.leaveBreadcrumb('<message>')
```

## **用户ID** 

API: 

```
export type Tingyun = {
  setUserId: (userId: string) => void
}
```

##### 使用方式: 

```
import tingyun from '@tingyun/sdk-core'
tingyun.setUserId('<userId>')
```

##### 说明: 

1. SDK初始化结束之前如果多次设置用户ID,只会取最后一次设置的值 

## **切换会话** 

##### API: 

```
export type Tingyun = {
  startNextSession: (sessionId?: string) => void
}
```

##### 使用方式: 

```
import tingyun from '@tingyun/sdk-core'
tingyun.startNextSession()
```

## **经纬度** 

##### API: 

```
export type Tingyun = {
  setLatLon: (latitude: number, longitude: number) => void
}
```

##### 使用方式: 

```
import tingyun from '@tingyun/sdk-core'
tingyun.setLatLon(<纬度>, <经度>)
```

##### 说明: 

1. 纬度有效值为 [-90, 90] 

2. 经度有效值为 [-180, 180] 

3. 经纬度其中之一传无效值,API调用无效 

**协议扩展** 

API: 

```
export type Tingyun = {
  /**
   * 创建执行单元
   * @param name 名称,不能为空,长度限制为1024字符,超过截取前1024字符
   * @param operation 数据类型,不能为空,长度限制为128字符,超过截取前128字符
   * @return s
   */
  startSpan: (name: string, operation: string) => ISpan
}
export interface ISpan {
  /**
   * 完成执行单元
   * @param status 执行状态, 默认为SpanStatuses.OK
   */
  finish: (status?: SpanStatus) => void
  /**
   * 创建子执行单元
   * @param name 名称,不能为空,长度限制为1024字符,超过截取前1024字符
   * @param operation 数据类型,不能为空,长度限制为128字符,超过截取前128字符
   * @param description 描述信息,长度限制为1024字符,超过截取前1024字符
   * @return s
   */
  startChild: (name: string, operation: string, description?: string) => ISpan
  /**
   * 设置Data数据
   * @param key data的key
   * @param value data的value
   */
  setData: (key: string, value: Object) => void
  /**
   * 根据key移除Data
   * @param key data的key
   */
  removeData: (key: string) => void
  /**
   * 设置Tag数据
   * @param key tag的key
   * @param value tag的value
   */
  setTag: (key: string, value: string) => void
  /**
   * 根据key移除Tag
   * @param key tag的key
   */
  removeTag: (key: string) => void
  /**
   * 设置Metric数据
   * @param key metric的key
   * @param value metric的value
   * @param unit metric的单位
   */
  setMetric: (key: string, value: number, unit?: string) => void
  /**
   * 根据key移除Metric
   * @param key Metric的key
   */
  removeMetric: (key: string) => void
  /**
   * 设置执行状态
   * @param status
   */
  setStatus: (status: SpanStatus) => void
  /**
   * 设置执行单元耗时, 单位ms
   * @param duration
   */
  setDuration: (duration: number) => void
  /**
   * 设置状态码
   * @param code 状态码,默认为"0"
   */
  setStatusCode: (code: string) => void
}
export const SpanStatuses = {
  UNKNOWN: 0,
  OK: 1,
  ERROR: -1
} as const
export type SpanStatus = typeof SpanStatuses[keyof typeof SpanStatuses]
// 预定义单位
export const SpanMetricUnits = {
  Bit: "b",
  Byte: "B",
  Kilobytes: "KB",
  Megabytes: "MB",
  Millisecond: "ms",
  Second: "s",
  Minute: "m",
  Hour: "h",
  Day: "d",
  Bitps: "b/s",
  Byteps: "B/s",
  KBps: "KB/s",
  MBps: "MB/s",
} as const
```

使用方式: 

```
import tingyun, {SpanStatuses} from '@tingyun/sdk-core'
const span = tingyun.startSpan('span_name', 'span_operation')
span.setData('dataKey', 'dataValue')
span.setTag('tagKey', 'tagValue')
span.setMetric('time', 50, SpanMetricUnits.Millisecond)
span.setDuration(100)
span.setStatus(SpanStatuses.OK)
span.setStatusCode('200')
const childSpan = span.startChild('child_span_name', 'child_span_operation')
childSpan.finish()
span.finish()
```
