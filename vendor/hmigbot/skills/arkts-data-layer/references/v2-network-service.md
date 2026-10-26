# ArkTS V2 网络服务模式参考

> 本文档基于 **ArkTS V2（API 12+）** 装饰器体系。本项目锁 V2，本文档为主参考。V1 历史写法见 [`network-service.md`](./network-service.md)（已加 legacy 标识）。
>
> 完整的 V2 网络请求封装模式，涵盖 HTTP 工具类、领域服务、网络状态监控、请求缓存、离线降级，以及配合 `AppStorageV2 / PersistenceV2` 实现的全局状态/持久化。
>
> **重要**：`HttpUtil / ApiService / NetworkMonitor / RequestCache` 等服务类**本身是纯静态工具，不依赖组件装饰器**，可直接复用 V1 实现。本文档区别在于：(1) Model 类用 `@ObservedV2 + @Trace`；(2) 消费 Service 的 UI 组件用 `@ComponentV2 + @Local`；(3) 全局状态用 `AppStorageV2.connect` 替代 V1 `@StorageLink`；(4) 持久化用 `PersistenceV2.globalConnect`。

---

## 1. HttpUtil —— 完整 HTTP 请求封装（V1/V2 通用）

基于 `@kit.NetworkKit` 的 `http` 模块封装，支持拦截器、错误处理、超时配置和统一 Token 管理。**与 V1 完全一致**。

```typescript
import { http } from '@kit.NetworkKit'

// ---- 类型定义 ----

export interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

export interface RequestConfig {
  baseUrl?: string
  timeout?: number
  headers?: Record<string, string>
}

export type RequestInterceptor = (options: http.HttpRequestOptions) => http.HttpRequestOptions
export type ResponseInterceptor = (response: http.HttpResponse) => http.HttpResponse

// ---- 错误类型 ----

export enum HttpErrorType {
  NETWORK = 'NETWORK',
  TIMEOUT = 'TIMEOUT',
  SERVER = 'SERVER',
  CLIENT = 'CLIENT',
  UNAUTHORIZED = 'UNAUTHORIZED',
  FORBIDDEN = 'FORBIDDEN',
  NOT_FOUND = 'NOT_FOUND',
  PARSE = 'PARSE',
  BUSINESS = 'BUSINESS',
  UNKNOWN = 'UNKNOWN'
}

// 自定义错误类必须 extends Error（并在构造器调 super(message)），否则 `throw new HttpError()`
// 触发 ArkTS arkts-limited-throw（throw 只接受 Error 及其子类）。message 由 Error 基类提供，不再重复声明。
export class HttpError extends Error {
  type: HttpErrorType
  code: number

  constructor(type: HttpErrorType, code: number, message: string) {
    super(message)
    this.type = type
    this.code = code
  }

  static fromStatusCode(statusCode: number, message: string = ''): HttpError {
    switch (statusCode) {
      case 401:
        return new HttpError(HttpErrorType.UNAUTHORIZED, 401, message || '登录已过期，请重新登录')
      case 403:
        return new HttpError(HttpErrorType.FORBIDDEN, 403, message || '没有访问权限')
      case 404:
        return new HttpError(HttpErrorType.NOT_FOUND, 404, message || '请求的资源不存在')
      default:
        if (statusCode >= 500) {
          return new HttpError(HttpErrorType.SERVER, statusCode, message || '服务器内部错误')
        } else if (statusCode >= 400) {
          return new HttpError(HttpErrorType.CLIENT, statusCode, message || '请求错误')
        }
        return new HttpError(HttpErrorType.UNKNOWN, statusCode, message || '未知错误')
    }
  }
}

// ---- HttpUtil 主类 ----

export class HttpUtil {
  private static baseUrl: string = ''
  private static defaultTimeout: number = 15000
  private static authToken: string = ''
  private static defaultHeaders: Record<string, string> = {
    'Content-Type': 'application/json'
  }

  private static requestInterceptors: RequestInterceptor[] = []
  private static responseInterceptors: ResponseInterceptor[] = []

  static init(config: RequestConfig): void {
    if (config.baseUrl !== undefined) {
      HttpUtil.baseUrl = config.baseUrl
    }
    if (config.timeout !== undefined) {
      HttpUtil.defaultTimeout = config.timeout
    }
    if (config.headers !== undefined) {
      let keys = Object.keys(config.headers)
      for (let key of keys) {
        HttpUtil.defaultHeaders[key] = config.headers[key]
      }
    }
  }

  static setToken(token: string): void {
    HttpUtil.authToken = token
  }

  static clearToken(): void {
    HttpUtil.authToken = ''
  }

  static getToken(): string {
    return HttpUtil.authToken
  }

  static addRequestInterceptor(interceptor: RequestInterceptor): void {
    HttpUtil.requestInterceptors.push(interceptor)
  }

  static addResponseInterceptor(interceptor: ResponseInterceptor): void {
    HttpUtil.responseInterceptors.push(interceptor)
  }

  static clearInterceptors(): void {
    HttpUtil.requestInterceptors = []
    HttpUtil.responseInterceptors = []
  }

  private static async request<T>(
    method: http.RequestMethod,
    url: string,
    data?: Object,
    customHeaders?: Record<string, string>,
    customTimeout?: number
  ): Promise<T> {
    let fullUrl = url.startsWith('http') ? url : `${HttpUtil.baseUrl}${url}`

    // ArkTS 禁对象字面量 spread（arkts-no-spread）——逐 key 拷贝
    let headers: Record<string, string> = {}
    for (let key of Object.keys(HttpUtil.defaultHeaders)) {
      headers[key] = HttpUtil.defaultHeaders[key]
    }
    if (HttpUtil.authToken.length > 0) {
      headers['Authorization'] = `Bearer ${HttpUtil.authToken}`
    }
    if (customHeaders !== undefined) {
      let keys = Object.keys(customHeaders)
      for (let key of keys) {
        headers[key] = customHeaders[key]
      }
    }

    let options: http.HttpRequestOptions = {
      method: method,
      header: headers,
      connectTimeout: customTimeout ?? HttpUtil.defaultTimeout,
      readTimeout: customTimeout ?? HttpUtil.defaultTimeout,
      expectDataType: http.HttpDataType.STRING
    }

    if (data !== undefined && (method === http.RequestMethod.POST || method === http.RequestMethod.PUT)) {
      options.extraData = JSON.stringify(data)
    }

    for (let interceptor of HttpUtil.requestInterceptors) {
      options = interceptor(options)
    }

    let httpRequest = http.createHttp()

    try {
      let response = await httpRequest.request(fullUrl, options)

      for (let interceptor of HttpUtil.responseInterceptors) {
        response = interceptor(response)
      }

      if (response.responseCode < 200 || response.responseCode >= 300) {
        throw HttpError.fromStatusCode(response.responseCode)
      }

      let responseBody = response.result as string
      if (responseBody === undefined || responseBody === null || responseBody.length === 0) {
        return {} as T
      }

      let jsonResult = JSON.parse(responseBody) as ApiResponse<T>

      if (jsonResult.code !== 0) {
        throw new HttpError(HttpErrorType.BUSINESS, jsonResult.code, jsonResult.message)
      }

      return jsonResult.data

    } catch (error) {
      if (error instanceof HttpError) {
        throw error
      }
      let errMsg = (error as Error).message ?? '网络请求失败'
      if (errMsg.includes('timeout') || errMsg.includes('Timeout')) {
        throw new HttpError(HttpErrorType.TIMEOUT, 0, '请求超时，请稍后重试')
      }
      throw new HttpError(HttpErrorType.NETWORK, 0, errMsg)
    } finally {
      httpRequest.destroy()
    }
  }

  static async get<T>(url: string, headers?: Record<string, string>, timeout?: number): Promise<T> {
    return HttpUtil.request<T>(http.RequestMethod.GET, url, undefined, headers, timeout)
  }

  static async post<T>(url: string, data?: Object, headers?: Record<string, string>, timeout?: number): Promise<T> {
    return HttpUtil.request<T>(http.RequestMethod.POST, url, data, headers, timeout)
  }

  static async put<T>(url: string, data?: Object, headers?: Record<string, string>, timeout?: number): Promise<T> {
    return HttpUtil.request<T>(http.RequestMethod.PUT, url, data, headers, timeout)
  }

  static async delete<T>(url: string, headers?: Record<string, string>, timeout?: number): Promise<T> {
    return HttpUtil.request<T>(http.RequestMethod.DELETE, url, undefined, headers, timeout)
  }
}
```

> **`data` 入参守卫**：`post/put` 的 `data` 若是 `@ObservedV2` 实例，先转 `data.toJson()` 再传——直接传会被 `JSON.stringify` 出 `__ob_` 前缀 key（后端不识别、接口可能仍 200）。见 v2-model-patterns §3。

**初始化和拦截器配置（V2 项目，在 EntryAbility 中）：**

```typescript
import { AppStorageV2 } from '@kit.ArkUI'

HttpUtil.init({
  baseUrl: 'https://api.example.com/v1',
  timeout: 20000
})

HttpUtil.addRequestInterceptor((options: http.HttpRequestOptions): http.HttpRequestOptions => {
  let headers = options.header as Record<string, string>
  headers['X-Device-Type'] = 'HarmonyOS'
  headers['X-App-Version'] = '1.0.0'
  options.header = headers
  return options
})

HttpUtil.addResponseInterceptor((response: http.HttpResponse): http.HttpResponse => {
  if (response.responseCode === 401) {
    HttpUtil.clearToken()
    // V2: 同步清除全局登录态
    const session = AppStorageV2.connect(UserSession, 'user_session', () => new UserSession())!
    session.isLoggedIn = false
    session.token = ''
    console.warn('Token 过期，需要重新登录')
  }
  return response
})

// 登录成功后写入 Token + 全局 session
HttpUtil.setToken('eyJhbGciOiJIUzI1NiIs...')
const session = AppStorageV2.connect(UserSession, 'user_session', () => new UserSession())!
session.isLoggedIn = true
session.token = 'eyJhbGciOiJIUzI1NiIs...'
```

---

## 1b. 文件上传（multipart/form-data）

Retrofit `@Multipart` + `@Part MultipartBody.Part`（承载 `file.asRequestBody` 的**文件字节**）→ HMOS `http.request` 的 `multiFormDataList`（API 11+）。

**陷阱（后端收空的头号真因）**：相册/文档选择器返回的 uri 或路径**不能直接当 `filePath`**。Android `File(pickedPath)` 总能读；HMOS 选择器给的是 media 库 uri / 应用沙箱外路径，http 协议栈**读不到** → multipart 里文件字节为空 → **后端收到空文件（接口仍 200、前端仍显示"成功"）**。

**修复**：先 `fileIo.copyFile` 把选中文件拷进应用沙箱（`context.cacheDir`/`filesDir`），再用沙箱路径作 `filePath`。

```typescript
import { http } from '@kit.NetworkKit'
import { fileIo } from '@kit.CoreFileKit'
import { common } from '@kit.AbilityKit'

// pickedPath = 选择器返回的 uri/外部路径（不保证可直接读）；BASE_URL/AvatarResult 按项目定义
static async uploadAvatar(
  context: common.UIAbilityContext,
  pickedPath: string,
  userId: string,
  token: string
): Promise<ApiResponse<AvatarResult>> {
  // 1) 关键：拷进沙箱得到 http 能读的路径。省这步 = 后端收空。
  const fileName: string = `avatar_${userId}.jpg`
  const sandboxPath: string = `${context.cacheDir}/${fileName}`
  await fileIo.copyFile(pickedPath, sandboxPath)   // src 传可读路径或 fd（string|number）；相册 media uri 读不到时先 open 取 fd 再 copy

  const req = http.createHttp()
  try {
    const resp = await req.request(`${BASE_URL}/user/uploadAvatar`, {
      method: http.RequestMethod.POST,
      header: {
        'Content-Type': 'multipart/form-data',   // boundary 由协议栈自动生成，别手写
        'token': token
      } as Record<string, string>,
      multiFormDataList: [
        {
          name: 'avatar',            // 对应 @Part avatar
          contentType: 'image/jpeg',
          filePath: sandboxPath,     // ← 文件部分给沙箱路径，协议栈读字节拼进 body
          remoteFileName: fileName   // 对应 createFormData(..., file.name, ...)
        },
        {
          name: 'userId',            // 对应 @Part("userId")
          contentType: 'text/plain',
          data: userId               // ← 文本部分给 data 值
        }
      ]
    })
    if (resp.responseCode !== 200) {
      throw HttpError.fromStatusCode(resp.responseCode)
    }
    const body = JSON.parse(resp.result as string) as ApiResponse<Record<string, Object>>
    return { code: body.code, message: body.message, data: AvatarResult.fromJson(body.data) }
  } finally {
    req.destroy()
  }
}
```

**WRONG（后端收空）**：
```typescript
// ✘ 把选择器路径/uri 直接当文本 data 传（传的是路径字符串、不是文件内容）
multiFormDataList: [{ name: 'avatar', contentType: 'image/jpeg', data: pickedPath }]
// ✘ 漏拷进沙箱，直接 filePath: pickedUri（http 读不到 → 空）
```

**自检**：
- 文件部分用 `filePath`（沙箱路径）或 `data`（内存内容 `ArrayBuffer`/`string`）——**绝不把路径/URI 字符串当文本 `data` 传**。
- 上传前**必有一步**把选中文件落到沙箱（`fileIo.copyFile`/读写），`filePath` 指向沙箱内路径。
- 大文件 / 需进度 / 后台续传 → `request.agent`（`Action.UPLOAD` + `FormItem`，见 arkts-download-manager），同样要求沙箱内文件路径。

---

## 2. ApiService —— 领域服务模式（V2 模型）

针对特定业务资源的 API 服务类。封装具体的接口路径和参数处理。Service 类本身是静态工具，与 V1 一致；Model 类用 V2 装饰器。

```typescript
// ==========================================
// 分页参数与响应（V1/V2 通用接口定义）
// ==========================================

export interface PageParams {
  page: number
  pageSize: number
}

export interface PageResult<T> {
  list: T[]
  total: number
  page: number
  pageSize: number
  hasMore: boolean
}

// ==========================================
// V2 文章模型（@ObservedV2 + @Trace）
// ==========================================

@ObservedV2
export class ArticleModel {
  @Trace id: number = 0
  @Trace title: string = ''
  @Trace content: string = ''
  @Trace author: string = ''
  @Trace coverImage: string = ''
  @Trace category: string = ''
  @Trace viewCount: number = 0
  @Trace likeCount: number = 0
  @Trace createdAt: number = 0

  constructor(
    id: number = 0,
    title: string = '',
    content: string = '',
    author: string = '',
    coverImage: string = '',
    category: string = '',
    viewCount: number = 0,
    likeCount: number = 0,
    createdAt: number = Date.now()
  ) {
    this.id = id
    this.title = title
    this.content = content
    this.author = author
    this.coverImage = coverImage
    this.category = category
    this.viewCount = viewCount
    this.likeCount = likeCount
    this.createdAt = createdAt
  }

  static fromJson(json: Record<string, Object>): ArticleModel {
    return new ArticleModel(
      json['id'] as number,
      json['title'] as string,
      (json['content'] as string) ?? '',
      (json['author'] as string) ?? '',
      (json['coverImage'] as string) ?? '',
      (json['category'] as string) ?? '',
      (json['viewCount'] as number) ?? 0,
      (json['likeCount'] as number) ?? 0,
      (json['createdAt'] as number) ?? Date.now()
    )
  }
}

// ==========================================
// ArticleService —— 文章 API 服务（与 V1 一致）
// ==========================================

export class ArticleService {
  private static readonly BASE_PATH = '/articles'

  static async getList(
    page: number = 1,
    pageSize: number = 20,
    category?: string
  ): Promise<PageResult<ArticleModel>> {
    let url = `${ArticleService.BASE_PATH}?page=${page}&pageSize=${pageSize}`
    if (category !== undefined && category.length > 0) {
      url += `&category=${category}`
    }

    try {
      let rawResult = await HttpUtil.get<Record<string, Object>>(url)

      let rawList = rawResult['list'] as Record<string, Object>[]
      let articles: ArticleModel[] = []
      for (let item of rawList) {
        articles.push(ArticleModel.fromJson(item))
      }

      return {
        list: articles,
        total: rawResult['total'] as number,
        page: page,
        pageSize: pageSize,
        hasMore: articles.length >= pageSize
      }
    } catch (error) {
      let httpError = error as HttpError
      throw ArticleService.mapError(httpError)
    }
  }

  static async getDetail(id: number): Promise<ArticleModel> {
    try {
      let rawResult = await HttpUtil.get<Record<string, Object>>(
        `${ArticleService.BASE_PATH}/${id}`
      )
      return ArticleModel.fromJson(rawResult)
    } catch (error) {
      let httpError = error as HttpError
      throw ArticleService.mapError(httpError)
    }
  }

  static async create(data: {
    title: string
    content: string
    category: string
    coverImage?: string
  }): Promise<ArticleModel> {
    try {
      let rawResult = await HttpUtil.post<Record<string, Object>>(
        ArticleService.BASE_PATH,
        data as Object
      )
      return ArticleModel.fromJson(rawResult)
    } catch (error) {
      let httpError = error as HttpError
      throw ArticleService.mapError(httpError)
    }
  }

  static async like(id: number): Promise<{ likeCount: number }> {
    try {
      return await HttpUtil.post<{ likeCount: number }>(
        `${ArticleService.BASE_PATH}/${id}/like`
      )
    } catch (error) {
      let httpError = error as HttpError
      throw ArticleService.mapError(httpError)
    }
  }

  private static mapError(error: HttpError): HttpError {
    switch (error.type) {
      case HttpErrorType.NOT_FOUND:
        return new HttpError(HttpErrorType.NOT_FOUND, 404, '文章不存在或已被删除')
      case HttpErrorType.UNAUTHORIZED:
        return new HttpError(HttpErrorType.UNAUTHORIZED, 401, '请先登录后再操作')
      case HttpErrorType.FORBIDDEN:
        return new HttpError(HttpErrorType.FORBIDDEN, 403, '您没有权限执行此操作')
      case HttpErrorType.NETWORK:
        return new HttpError(HttpErrorType.NETWORK, 0, '网络连接失败，请检查网络后重试')
      case HttpErrorType.TIMEOUT:
        return new HttpError(HttpErrorType.TIMEOUT, 0, '请求超时，请稍后重试')
      default:
        return error
    }
  }
}
```

**在 V2 页面中使用 ApiService：**

```typescript
@Entry
@ComponentV2
struct ArticleListPage {
  @Local articles: ArticleModel[] = []
  @Local isLoading: boolean = false
  @Local errorMsg: string = ''
  @Local currentPage: number = 1
  @Local hasMore: boolean = true

  aboutToAppear(): void {
    this.loadArticles()
  }

  async loadArticles(): Promise<void> {
    if (this.isLoading) return
    this.isLoading = true
    this.errorMsg = ''

    try {
      let result = await ArticleService.getList(this.currentPage, 20)
      if (this.currentPage === 1) {
        this.articles = result.list
      } else {
        this.articles = this.articles.concat(result.list)
      }
      this.hasMore = result.hasMore
    } catch (error) {
      let httpError = error as HttpError
      this.errorMsg = httpError.message
    } finally {
      this.isLoading = false
    }
  }

  build() {
    Column() {
      if (this.errorMsg.length > 0) {
        Column() {
          Text(this.errorMsg).fontColor(Color.Red)
          Button('重试').onClick(() => { this.loadArticles() })
        }
        .padding(20)
      }

      List() {
        ForEach(this.articles, (article: ArticleModel) => {
          ListItem() {
            Column() {
              Text(article.title).fontSize(16).fontWeight(FontWeight.Bold)
              Text(article.author).fontSize(12).fontColor('#999999')
            }
            .padding(12)
          }
        }, (article: ArticleModel) => article.id.toString())
      }
      .onReachEnd(() => {
        if (this.hasMore && !this.isLoading) {
          this.currentPage++
          this.loadArticles()
        }
      })
    }
  }
}
```

---

## 3. 网络状态检测（与 V1 一致）

`NetworkMonitor` 是纯静态工具类，不依赖装饰器。V2 中使用方式与 V1 完全一致。

```typescript
import { connection } from '@kit.NetworkKit'

export enum NetworkState {
  UNKNOWN = 'unknown',
  CONNECTED = 'connected',
  DISCONNECTED = 'disconnected'
}

export enum NetworkType {
  NONE = 'none',
  WIFI = 'wifi',
  CELLULAR = 'cellular',
  ETHERNET = 'ethernet',
  OTHER = 'other'
}

type NetworkStateCallback = (state: NetworkState, type: NetworkType) => void

export class NetworkMonitor {
  private static currentState: NetworkState = NetworkState.UNKNOWN
  private static currentType: NetworkType = NetworkType.NONE
  private static callbacks: NetworkStateCallback[] = []
  private static netConnection: connection.NetConnection | null = null

  static async hasNetwork(): Promise<boolean> {
    try {
      let hasNet = await connection.hasDefaultNet()
      return hasNet
    } catch (error) {
      console.error(`检查网络状态失败: ${JSON.stringify(error)}`)
      return false
    }
  }

  static async getNetworkType(): Promise<NetworkType> {
    try {
      let hasNet = await connection.hasDefaultNet()
      if (!hasNet) {
        return NetworkType.NONE
      }

      let netHandle = await connection.getDefaultNet()
      let netCapabilities = await connection.getNetCapabilities(netHandle)

      let bearerTypes = netCapabilities.bearerTypes
      if (bearerTypes.includes(connection.NetBearType.BEARER_WIFI)) {
        return NetworkType.WIFI
      } else if (bearerTypes.includes(connection.NetBearType.BEARER_CELLULAR)) {
        return NetworkType.CELLULAR
      } else if (bearerTypes.includes(connection.NetBearType.BEARER_ETHERNET)) {
        return NetworkType.ETHERNET
      }
      return NetworkType.OTHER
    } catch (error) {
      console.error(`获取网络类型失败: ${JSON.stringify(error)}`)
      return NetworkType.NONE
    }
  }

  static startMonitoring(): void {
    if (NetworkMonitor.netConnection !== null) {
      return
    }

    NetworkMonitor.netConnection = connection.createNetConnection()

    NetworkMonitor.netConnection.on('netAvailable', () => {
      NetworkMonitor.currentState = NetworkState.CONNECTED
      NetworkMonitor.updateType()
      NetworkMonitor.notifyCallbacks()
    })

    NetworkMonitor.netConnection.on('netLost', () => {
      NetworkMonitor.currentState = NetworkState.DISCONNECTED
      NetworkMonitor.currentType = NetworkType.NONE
      NetworkMonitor.notifyCallbacks()
    })

    NetworkMonitor.netConnection.on('netCapabilitiesChange', () => {
      NetworkMonitor.updateType()
      NetworkMonitor.notifyCallbacks()
    })

    NetworkMonitor.netConnection.register(() => {
      console.info('网络监听注册成功')
    })
  }

  static stopMonitoring(): void {
    if (NetworkMonitor.netConnection !== null) {
      NetworkMonitor.netConnection.unregister(() => {
        console.info('网络监听已注销')
      })
      NetworkMonitor.netConnection = null
    }
  }

  static onStateChange(callback: NetworkStateCallback): void {
    NetworkMonitor.callbacks.push(callback)
  }

  static removeCallback(callback: NetworkStateCallback): void {
    let index = NetworkMonitor.callbacks.indexOf(callback)
    if (index >= 0) {
      NetworkMonitor.callbacks.splice(index, 1)
    }
  }

  static getState(): NetworkState {
    return NetworkMonitor.currentState
  }

  static getType(): NetworkType {
    return NetworkMonitor.currentType
  }

  private static async updateType(): Promise<void> {
    NetworkMonitor.currentType = await NetworkMonitor.getNetworkType()
  }

  private static notifyCallbacks(): void {
    for (let callback of NetworkMonitor.callbacks) {
      callback(NetworkMonitor.currentState, NetworkMonitor.currentType)
    }
  }
}
```

> **V2 进阶**：可把网络状态封装成 `@ObservedV2` 类放入 `AppStorageV2`，让所有页面用 `@Local` 持有并自动响应网络变化。见下方第 6 节。

---

## 4. 离线降级策略（V2）

```typescript
import { preferences } from '@kit.ArkData'

export class OfflineFirstLoader {
  private context: Context
  private store: preferences.Preferences | null = null

  constructor(context: Context) {
    this.context = context
  }

  private async getStore(): Promise<preferences.Preferences> {
    if (this.store === null) {
      this.store = await preferences.getPreferences(this.context, 'offline_cache')
    }
    return this.store!
  }

  async loadData<T>(
    cacheKey: string,
    fetcher: () => Promise<T>,
    parser: (raw: string) => T
  ): Promise<{ data: T; fromCache: boolean }> {
    let hasNet = await NetworkMonitor.hasNetwork()

    if (hasNet) {
      try {
        let data = await fetcher()
        let store = await this.getStore()
        await store.put(cacheKey, JSON.stringify(data))
        await store.flush()
        return { data: data, fromCache: false }
      } catch (error) {
        console.warn(`网络请求失败，尝试读取缓存: ${JSON.stringify(error)}`)
        return await this.loadFromCache(cacheKey, parser)
      }
    } else {
      return await this.loadFromCache(cacheKey, parser)
    }
  }

  private async loadFromCache<T>(
    cacheKey: string,
    parser: (raw: string) => T
  ): Promise<{ data: T; fromCache: boolean }> {
    let store = await this.getStore()
    let cached = await store.get(cacheKey, '') as string
    if (cached.length > 0) {
      let data = parser(cached)
      return { data: data, fromCache: true }
    }
    throw new HttpError(HttpErrorType.NETWORK, 0, '无网络且无本地缓存')
  }
}
```

**在 V2 页面中使用：**

```typescript
@Entry
@ComponentV2
struct OfflineReadyPage {
  @Local articles: ArticleModel[] = []
  @Local fromCache: boolean = false
  @Local networkState: string = ''
  private loader: OfflineFirstLoader | null = null

  aboutToAppear(): void {
    // 组件内取 Context：用 this.getUIContext().getHostContext()（旧 getContext(this) 已不推荐，见 SKILL 常见错误 #10）。
    // 字段初始化期组件未挂载、拿不到 UIContext，故延后到 aboutToAppear 构造 loader；getHostContext() 返回 Context | undefined，判空后再用。
    const context = this.getUIContext().getHostContext()
    if (context !== undefined) {
      this.loader = new OfflineFirstLoader(context)
    }

    NetworkMonitor.onStateChange((state: NetworkState, type: NetworkType) => {
      this.networkState = `${state} (${type})`
      if (state === NetworkState.CONNECTED) {
        this.loadData()
      }
    })

    this.loadData()
  }

  async loadData(): Promise<void> {
    const loader = this.loader
    if (loader === null) {
      return
    }
    try {
      let result = await loader.loadData<ArticleModel[]>(
        'article_list',
        async (): Promise<ArticleModel[]> => {
          let pageResult = await ArticleService.getList(1, 50)
          return pageResult.list
        },
        (raw: string): ArticleModel[] => {
          let jsonArray = JSON.parse(raw) as Record<string, Object>[]
          let articles: ArticleModel[] = []
          for (let json of jsonArray) {
            articles.push(ArticleModel.fromJson(json))
          }
          return articles
        }
      )
      this.articles = result.data
      this.fromCache = result.fromCache
    } catch (error) {
      console.error(`加载数据失败: ${JSON.stringify(error)}`)
    }
  }

  build() {
    Column() {
      if (this.fromCache) {
        Row() {
          Text('当前显示离线缓存数据').fontColor(Color.Orange).fontSize(12)
        }
        .width('100%').padding(8).backgroundColor('#FFF3E0')
      }

      List() {
        ForEach(this.articles, (article: ArticleModel) => {
          ListItem() {
            Text(article.title).padding(12)
          }
        }, (article: ArticleModel) => article.id.toString())
      }
    }
  }
}
```

---

## 5. 请求缓存（与 V1 一致）

`RequestCache` 是纯静态工具，与装饰器无关。V2 中可直接使用 V1 的实现，详细代码见 [`network-service.md`](./network-service.md) 第 4 节。这里仅展示在 V2 项目中如何配合 V2 模型 + ComponentV2 调用：

```typescript
export class CachedArticleService {
  private static readonly BASE_PATH = '/articles'
  private static readonly CACHE_PREFIX = 'articles:'

  // 列表缓存 2 分钟
  static async getList(page: number = 1, pageSize: number = 20): Promise<PageResult<ArticleModel>> {
    let cacheKey = `${CachedArticleService.CACHE_PREFIX}list:${page}:${pageSize}`
    return RequestCache.cachedRequest<PageResult<ArticleModel>>(
      cacheKey,
      async (): Promise<PageResult<ArticleModel>> => {
        return await ArticleService.getList(page, pageSize)
      },
      2 * 60 * 1000
    )
  }

  static async getDetail(id: number): Promise<ArticleModel> {
    let cacheKey = `${CachedArticleService.CACHE_PREFIX}detail:${id}`
    return RequestCache.cachedRequest<ArticleModel>(
      cacheKey,
      async (): Promise<ArticleModel> => {
        return await ArticleService.getDetail(id)
      },
      5 * 60 * 1000
    )
  }

  static async create(data: {
    title: string
    content: string
    category: string
  }): Promise<ArticleModel> {
    let result = await ArticleService.create(data)
    RequestCache.invalidateByPrefix(`${CachedArticleService.CACHE_PREFIX}list:`)
    return result
  }

  static async forceRefreshList(page: number = 1, pageSize: number = 20): Promise<PageResult<ArticleModel>> {
    RequestCache.invalidateByPrefix(`${CachedArticleService.CACHE_PREFIX}list:`)
    return await CachedArticleService.getList(page, pageSize)
  }
}
```

---

## 6. V2 全局状态：AppStorageV2 / PersistenceV2

V2 的核心数据层升级：用 `AppStorageV2.connect / PersistenceV2.globalConnect`（页面子树范围共享用 `@Provider`/`@Consumer`）替代 V1 的 `@StorageLink / @StorageProp / @LocalStorageLink / PersistentStorage.persistProp` 双层模式。

### 6.1 AppStorageV2 — 全局运行时共享（不持久）

适合"登录态、购物车、当前播放项"等**不需要持久化的全局状态**。

```typescript
import { AppStorageV2 } from '@kit.ArkUI'   // 真实导出，必须 import

// 1. 定义全局 Model 类（@ObservedV2 + @Trace）
@ObservedV2
export class UserSession {
  @Trace isLoggedIn: boolean = false
  @Trace userId: string = ''
  @Trace userName: string = ''
  @Trace token: string = ''
  @Trace avatarUrl: string = ''

  reset(): void {
    this.isLoggedIn = false
    this.userId = ''
    this.userName = ''
    this.token = ''
    this.avatarUrl = ''
  }
}

// 2. 统一 key 常量
export class StorageKeys {
  static readonly USER_SESSION = 'user_session'
  static readonly CART = 'cart'
  static readonly NETWORK_STATUS = 'network_status'
}

// 3. 在 EntryAbility.onCreate 中预热（可选；首次 connect 时也会自动初始化）
// onCreate(want, launchParam) {
//   AppStorageV2.connect(UserSession, StorageKeys.USER_SESSION, () => new UserSession())
// }

// 4. 任意 @ComponentV2 中使用，自动响应变化
@Entry
@ComponentV2
struct ProfilePage {
  @Local session: UserSession = AppStorageV2.connect(
    UserSession,
    StorageKeys.USER_SESSION,
    () => new UserSession()
  )!

  build() {
    Column() {
      if (this.session.isLoggedIn) {
        Text('Welcome, ' + this.session.userName)
        Image(this.session.avatarUrl).width(64).height(64)
        Button('退出登录').onClick(() => {
          this.session.reset()
          HttpUtil.clearToken()
        })
      } else {
        Button('Login').onClick(() => {
          this.session.isLoggedIn = true
          this.session.userId = '12345'
          this.session.userName = 'Alice'
          this.session.token = 'jwt_token_xxx'
          HttpUtil.setToken(this.session.token)
        })
      }
    }
  }
}
```

### 6.2 PersistenceV2 — 持久化 + 响应式（推荐替代 V1 双层模式）

适合"主题、排序、视图类型、登录 token"等**需要持久化且 UI 响应**的场景。**自动落盘 + UI 自动刷新**，无需 V1 的"PersistentStorage.persistProp + @StorageLink"双层手动同步。

```typescript
import { PersistenceV2 } from '@kit.ArkUI'   // 真实导出，必须 import

// 1. 定义持久化 Model 类
@ObservedV2
export class AppSettings {
  @Trace theme: 'light' | 'dark' = 'light'
  @Trace pageSize: number = 20
  @Trace language: string = 'zh-CN'
  @Trace lastSyncTime: number = 0
  @Trace cachedToken: string = ''
}

// 2. 任意 @ComponentV2 中 connect
@Entry
@ComponentV2
struct SettingsPage {
  @Local settings: AppSettings = PersistenceV2.globalConnect({
    type: AppSettings,
    key: 'app_settings',
    defaultCreator: () => new AppSettings()
  })!

  build() {
    Column() {
      Text(`当前主题: ${this.settings.theme}`)
      Button('切换主题').onClick(() => {
        // 修改后自动落盘 + 所有引用该 key 的组件自动刷新
        this.settings.theme = this.settings.theme === 'light' ? 'dark' : 'light'
      })

      Text(`每页数量: ${this.settings.pageSize}`)
      Slider({ value: this.settings.pageSize, min: 10, max: 50, step: 5 })
        .onChange((v: number) => { this.settings.pageSize = v })

      Text(`上次同步: ${new Date(this.settings.lastSyncTime).toLocaleString()}`)
      Button('立即同步').onClick(async () => {
        await this.syncWithServer()
        this.settings.lastSyncTime = Date.now()
      })
    }
  }

  async syncWithServer(): Promise<void> {
    // 同步逻辑
  }
}
```

### 6.3 页面子树共享 — @Provider / @Consumer（无 LocalStorageV2）

⚠️ **不存在 `LocalStorageV2` 这个 API**（曾被误传，`import { LocalStorageV2 }` 即报 `Module '@kit.ArkUI' has no exported member 'LocalStorageV2'`）。"单个 UIAbility / 页面树范围内共享、不进全局"的正确做法：祖先用 `@Provider()` 提供 `@ObservedV2` 实例、后代用 `@Consumer()` 同名消费（查找不到时用本地默认值）；或页面根用 `@Local` 持实例、`@Param` 逐层下传。

```typescript
@ObservedV2
class TabState {
  @Trace selectedTab: number = 0
  @Trace badgeCount: Map<string, number> = new Map()
}

@ComponentV2
struct TabContainer {            // 祖先：提供实例
  @Provider() tabState: TabState = new TabState()

  build() {
    Tabs({ index: this.tabState.selectedTab }) {
      // ...
    }
    .onChange((index: number) => {
      this.tabState.selectedTab = index
    })
  }
}

@ComponentV2
struct TabBadge {                // 任意后代：同名消费
  @Consumer() tabState: TabState = new TabState()   // 查找不到 @Provider 时用此本地默认值
  build() { /* 读 this.tabState.badgeCount … */ }
}
```

### 6.4 V2 中网络状态全局响应（综合示例）

把 V1 的"NetworkMonitor 静态状态 + onStateChange 回调注册"模式升级为"全局 `@ObservedV2` 状态 + `AppStorageV2.connect` 自动响应"：

```typescript
@ObservedV2
export class NetworkStatusModel {
  @Trace state: NetworkState = NetworkState.UNKNOWN
  @Trace type: NetworkType = NetworkType.NONE
  @Trace lastChangeTime: number = 0

  @Computed
  get isOnline(): boolean {
    return this.state === NetworkState.CONNECTED
  }

  @Computed
  get displayText(): string {
    if (!this.isOnline) return '离线'
    switch (this.type) {
      case NetworkType.WIFI: return 'Wi-Fi'
      case NetworkType.CELLULAR: return '移动数据'
      case NetworkType.ETHERNET: return '以太网'
      default: return '在线'
    }
  }
}

// 在 EntryAbility.onCreate 启动监听并写入全局状态
export function bootstrapNetworkMonitor(): void {
  const status = AppStorageV2.connect(
    NetworkStatusModel,
    StorageKeys.NETWORK_STATUS,
    () => new NetworkStatusModel()
  )!

  NetworkMonitor.onStateChange((state: NetworkState, type: NetworkType) => {
    status.state = state
    status.type = type
    status.lastChangeTime = Date.now()
  })

  NetworkMonitor.startMonitoring()
}

// 任意页面顶部展示网络状态条
@ComponentV2
struct NetworkBanner {
  @Local status: NetworkStatusModel = AppStorageV2.connect(
    NetworkStatusModel,
    StorageKeys.NETWORK_STATUS,
    () => new NetworkStatusModel()
  )!

  build() {
    if (!this.status.isOnline) {
      Row() {
        Text(`当前${this.status.displayText}，部分功能不可用`)
          .fontColor(Color.White)
          .fontSize(12)
      }
      .width('100%')
      .padding(8)
      .backgroundColor('#F44336')
    }
  }
}
```

---

## V1 → V2 速查对照（网络/服务/全局状态场景）

| V1 写法 | V2 写法 | 备注 |
|---|---|---|
| `@Component struct Page` | `@ComponentV2 struct Page` | |
| `@State articles: ArticleModel[] = []` | `@Local articles: ArticleModel[] = []` | |
| `@Observed class ArticleModel { id: number = 0 }` | `@ObservedV2 class ArticleModel { @Trace id: number = 0 }` | |
| `@StorageLink('user') user: UserInfo = ...` | `@Local user: UserSession = AppStorageV2.connect(UserSession, 'user', () => new UserSession())!` | 需先定义 `@ObservedV2` 类 |
| `@StorageProp('theme') theme: string = 'light'` | 同上模式（读取 `.theme` 即可，写回 storage 也自动） | |
| `@LocalStorageLink('x') x: T = ...` | `@Provider()/@Consumer()` 或页面根 `@Local` 持 `@ObservedV2`（**无 `LocalStorageV2`**） | 页面子树范围共享 |
| `PersistentStorage.persistProp('theme', 'light')` + `@StorageLink('theme')` | `PersistenceV2.globalConnect({type, key, defaultCreator})` | 一站式持久化 |
| `@Watch('articles') onArticlesChange()` | `@Monitor('articles') onArticlesChange(m: IMonitor)` | |
| `Refresh({ refreshing: $$this.isRefreshing })` | `Refresh({ refreshing: this.isRefreshing })` | V2 不再用 `$$` |
| 子组件 `@ObjectLink article: ArticleModel` | `@Param article: ArticleModel = new ArticleModel()` | |

---

## V2 数据层架构最佳实践

```
┌────────────────────────────────────────────────────────────┐
│ UI Layer (@ComponentV2)                                    │
│   @Local: 组件内部状态                                      │
│   @Param: 接收 @ObservedV2 实例（替代 @ObjectLink）         │
│   @Local x = AppStorageV2.connect(...)!: 全局共享          │
│   @Local x = PersistenceV2.globalConnect(...)!: 持久化     │
└────────────────────────────────────────────────────────────┘
                          ↓ 调用
┌────────────────────────────────────────────────────────────┐
│ Service Layer (静态工具类)                                  │
│   ArticleService.getList()                                 │
│   HttpUtil.get/post（含拦截器、Token、错误处理）            │
│   NetworkMonitor.hasNetwork()                              │
│   RequestCache.cachedRequest()                             │
│   OfflineFirstLoader.loadData()                            │
└────────────────────────────────────────────────────────────┘
                          ↓ 返回
┌────────────────────────────────────────────────────────────┐
│ Model Layer (@ObservedV2 + @Trace)                         │
│   ArticleModel { @Trace id, @Trace title, ... }            │
│   UserSession { @Trace isLoggedIn, @Trace userName, ... }  │
│   AppSettings { @Trace theme, @Trace pageSize, ... }       │
│   @Computed get derived(): T { ... }                       │
└────────────────────────────────────────────────────────────┘
                          ↓ 持久化 / 网络
┌────────────────────────────────────────────────────────────┐
│ External (HTTP API / RdbStore / Preferences / 文件)         │
└────────────────────────────────────────────────────────────┘
```
