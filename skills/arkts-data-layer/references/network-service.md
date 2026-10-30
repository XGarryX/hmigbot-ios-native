# ArkTS 网络服务模式参考（**V1 历史文档 — Legacy**）

> ⚠️ **本项目锁 ArkTS V2**。本文档为 **V1 历史参考**（`@Observed / @State / @Component / @Entry` 等），仅用于阅读老代码或迁移老项目时查阅。
>
> **新代码请使用 V2 装饰器**：参阅 [`v2-network-service.md`](./v2-network-service.md)（V2 主参考）和 [`SKILL.md`](../SKILL.md)。
>
> 注意：`HttpUtil / ApiService / NetworkMonitor / RequestCache / OfflineFirstLoader` 等服务类**本身不依赖组件装饰器**（纯静态工具），V1/V2 通用。本文档中需要 V1→V2 替换的地方主要是 Model 类与消费 Service 的 UI 组件部分：
> - 模型类 `@Observed` → `@ObservedV2`，可观察属性加 `@Trace`
> - UI 组件 `@Component` → `@ComponentV2`
> - 组件状态 `@State` → `@Local`
> - 子组件接收模型 `@ObjectLink x: Cls` → `@Param x: Cls = new Cls()`
> - 全局状态 `@StorageLink('key') x: T = ...` → 先用 `@ObservedV2` 类包裹，再 `@Local x: Cls = AppStorageV2.connect(Cls, 'key', () => new Cls())!`

---

> 完整的网络请求封装模式，涵盖 HTTP 工具类、领域服务、网络状态检测和请求缓存。

---

## 1. HttpUtil —— 完整 HTTP 请求封装

基于 `@kit.NetworkKit` 的 `http` 模块封装，支持拦截器、错误处理、超时配置和统一 Token 管理。

```typescript
// ==========================================
// HttpUtil —— 网络请求工具类
// ==========================================

import { http } from '@kit.NetworkKit'

// ---- 类型定义 ----

// 统一响应结构（与后端约定的 JSON 格式）
export interface ApiResponse<T> {
  code: number        // 业务状态码
  message: string     // 提示信息
  data: T             // 响应数据
}

// 请求配置
export interface RequestConfig {
  baseUrl?: string
  timeout?: number
  headers?: Record<string, string>
}

// 请求拦截器：在发送前修改请求配置
export type RequestInterceptor = (options: http.HttpRequestOptions) => http.HttpRequestOptions

// 响应拦截器：在返回前处理响应
export type ResponseInterceptor = (response: http.HttpResponse) => http.HttpResponse

// ---- 错误类型 ----

export enum HttpErrorType {
  NETWORK = 'NETWORK',         // 网络不可用
  TIMEOUT = 'TIMEOUT',         // 请求超时
  SERVER = 'SERVER',           // 服务端错误 (5xx)
  CLIENT = 'CLIENT',           // 客户端错误 (4xx)
  UNAUTHORIZED = 'UNAUTHORIZED', // 未授权 (401)
  FORBIDDEN = 'FORBIDDEN',     // 无权限 (403)
  NOT_FOUND = 'NOT_FOUND',     // 资源不存在 (404)
  PARSE = 'PARSE',             // 解析错误
  BUSINESS = 'BUSINESS',       // 业务逻辑错误
  UNKNOWN = 'UNKNOWN'          // 未知错误
}

export class HttpError {
  type: HttpErrorType
  code: number
  message: string

  constructor(type: HttpErrorType, code: number, message: string) {
    this.type = type
    this.code = code
    this.message = message
  }

  // 根据 HTTP 状态码创建对应错误
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
  // 基础配置
  private static baseUrl: string = ''
  private static defaultTimeout: number = 15000  // 默认超时 15 秒
  private static authToken: string = ''
  private static defaultHeaders: Record<string, string> = {
    'Content-Type': 'application/json'
  }

  // 拦截器列表
  private static requestInterceptors: RequestInterceptor[] = []
  private static responseInterceptors: ResponseInterceptor[] = []

  // ---- 初始化配置 ----

  // 设置基础 URL（在应用启动时调用一次）
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

  // ---- Token 管理 ----

  // 设置认证 Token（登录成功后调用）
  static setToken(token: string): void {
    HttpUtil.authToken = token
  }

  // 清除 Token（退出登录时调用）
  static clearToken(): void {
    HttpUtil.authToken = ''
  }

  // 获取当前 Token
  static getToken(): string {
    return HttpUtil.authToken
  }

  // ---- 拦截器管理 ----

  // 添加请求拦截器
  static addRequestInterceptor(interceptor: RequestInterceptor): void {
    HttpUtil.requestInterceptors.push(interceptor)
  }

  // 添加响应拦截器
  static addResponseInterceptor(interceptor: ResponseInterceptor): void {
    HttpUtil.responseInterceptors.push(interceptor)
  }

  // 清除所有拦截器
  static clearInterceptors(): void {
    HttpUtil.requestInterceptors = []
    HttpUtil.responseInterceptors = []
  }

  // ---- 核心请求方法 ----

  // 通用请求方法（所有 HTTP 方法的底层实现）
  private static async request<T>(
    method: http.RequestMethod,
    url: string,
    data?: Object,
    customHeaders?: Record<string, string>,
    customTimeout?: number
  ): Promise<T> {
    // 拼接完整 URL
    let fullUrl = url.startsWith('http') ? url : `${HttpUtil.baseUrl}${url}`

    // 构建请求头（ArkTS 禁对象字面量 spread arkts-no-spread——逐 key 拷贝）
    let headers: Record<string, string> = {}
    for (let key of Object.keys(HttpUtil.defaultHeaders)) {
      headers[key] = HttpUtil.defaultHeaders[key]
    }
    // 添加 Token
    if (HttpUtil.authToken.length > 0) {
      headers['Authorization'] = `Bearer ${HttpUtil.authToken}`
    }
    // 合并自定义请求头
    if (customHeaders !== undefined) {
      let keys = Object.keys(customHeaders)
      for (let key of keys) {
        headers[key] = customHeaders[key]
      }
    }

    // 构建请求选项
    let options: http.HttpRequestOptions = {
      method: method,
      header: headers,
      connectTimeout: customTimeout ?? HttpUtil.defaultTimeout,
      readTimeout: customTimeout ?? HttpUtil.defaultTimeout,
      expectDataType: http.HttpDataType.STRING
    }

    // 设置请求体（POST/PUT）
    if (data !== undefined && (method === http.RequestMethod.POST || method === http.RequestMethod.PUT)) {
      options.extraData = JSON.stringify(data)
    }

    // 应用请求拦截器
    for (let interceptor of HttpUtil.requestInterceptors) {
      options = interceptor(options)
    }

    // 创建请求实例
    let httpRequest = http.createHttp()

    try {
      let response = await httpRequest.request(fullUrl, options)

      // 应用响应拦截器
      for (let interceptor of HttpUtil.responseInterceptors) {
        response = interceptor(response)
      }

      // 处理 HTTP 状态码
      if (response.responseCode < 200 || response.responseCode >= 300) {
        throw HttpError.fromStatusCode(response.responseCode)
      }

      // 解析响应体
      let responseBody = response.result as string
      if (responseBody === undefined || responseBody === null || responseBody.length === 0) {
        // 无响应体（如 204 No Content），返回空对象
        return {} as T
      }

      let jsonResult = JSON.parse(responseBody) as ApiResponse<T>

      // 检查业务状态码（与后端约定 code === 0 表示成功）
      if (jsonResult.code !== 0) {
        throw new HttpError(HttpErrorType.BUSINESS, jsonResult.code, jsonResult.message)
      }

      return jsonResult.data

    } catch (error) {
      // 如果已经是 HttpError，直接抛出
      if (error instanceof HttpError) {
        throw error
      }
      // 网络错误或其他异常
      let errMsg = (error as Error).message ?? '网络请求失败'
      if (errMsg.includes('timeout') || errMsg.includes('Timeout')) {
        throw new HttpError(HttpErrorType.TIMEOUT, 0, '请求超时，请稍后重试')
      }
      throw new HttpError(HttpErrorType.NETWORK, 0, errMsg)
    } finally {
      httpRequest.destroy()
    }
  }

  // ---- 便捷方法 ----

  // GET 请求
  static async get<T>(url: string, headers?: Record<string, string>, timeout?: number): Promise<T> {
    return HttpUtil.request<T>(http.RequestMethod.GET, url, undefined, headers, timeout)
  }

  // POST 请求
  static async post<T>(url: string, data?: Object, headers?: Record<string, string>, timeout?: number): Promise<T> {
    return HttpUtil.request<T>(http.RequestMethod.POST, url, data, headers, timeout)
  }

  // PUT 请求
  static async put<T>(url: string, data?: Object, headers?: Record<string, string>, timeout?: number): Promise<T> {
    return HttpUtil.request<T>(http.RequestMethod.PUT, url, data, headers, timeout)
  }

  // DELETE 请求
  static async delete<T>(url: string, headers?: Record<string, string>, timeout?: number): Promise<T> {
    return HttpUtil.request<T>(http.RequestMethod.DELETE, url, undefined, headers, timeout)
  }
}
```

**初始化和拦截器配置示例：**

```typescript
// ==========================================
// 在 EntryAbility 的 onCreate 中初始化
// ==========================================

// 初始化基本配置
HttpUtil.init({
  baseUrl: 'https://api.example.com/v1',
  timeout: 20000
})

// 添加请求拦截器：在每个请求中加入设备信息
HttpUtil.addRequestInterceptor((options: http.HttpRequestOptions): http.HttpRequestOptions => {
  let headers = options.header as Record<string, string>
  headers['X-Device-Type'] = 'HarmonyOS'
  headers['X-App-Version'] = '1.0.0'
  options.header = headers
  return options
})

// 添加响应拦截器：统一处理 401 跳转登录
HttpUtil.addResponseInterceptor((response: http.HttpResponse): http.HttpResponse => {
  if (response.responseCode === 401) {
    // Token 过期，清除本地 Token 并跳转登录页
    HttpUtil.clearToken()
    // 此处可发送事件通知跳转（通过 emitter 等）
    console.warn('Token 过期，需要重新登录')
  }
  return response
})

// 登录成功后设置 Token
HttpUtil.setToken('eyJhbGciOiJIUzI1NiIs...')
```

**发送请求示例：**

```typescript
// GET 请求
try {
  let userInfo = await HttpUtil.get<UserModel>('/user/profile')
  console.info(`用户名: ${userInfo.name}`)
} catch (error) {
  let httpError = error as HttpError
  console.error(`请求失败 [${httpError.type}]: ${httpError.message}`)
}

// POST 请求
try {
  let result = await HttpUtil.post<{ id: number }>('/order/create', {
    productId: 123,
    quantity: 2
  })
  console.info(`订单创建成功，ID: ${result.id}`)
} catch (error) {
  let httpError = error as HttpError
  if (httpError.type === HttpErrorType.BUSINESS) {
    // 业务错误，显示后端返回的提示
    console.warn(httpError.message)
  } else if (httpError.type === HttpErrorType.NETWORK) {
    // 网络错误
    console.error('网络不可用，请检查网络设置')
  }
}
```

---

## 2. ApiService —— 领域服务模式

针对特定业务资源的 API 服务类。封装具体的接口路径和参数处理。

```typescript
// ==========================================
// ApiService 基础模式 —— 文章服务示例
// ==========================================

// 分页请求参数
export interface PageParams {
  page: number
  pageSize: number
}

// 分页响应结构
export interface PageResult<T> {
  list: T[]
  total: number
  page: number
  pageSize: number
  hasMore: boolean
}

// 文章模型
@Observed
export class ArticleModel {
  id: number
  title: string
  content: string
  author: string
  coverImage: string
  category: string
  viewCount: number
  likeCount: number
  createdAt: number

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
// ArticleService —— 文章 API 服务
// ==========================================

export class ArticleService {
  private static readonly BASE_PATH = '/articles'

  // 获取文章列表（分页）
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

      // 解析分页数据
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

  // 获取文章详情
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

  // 创建文章
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

  // 更新文章
  static async update(id: number, data: {
    title?: string
    content?: string
    category?: string
    coverImage?: string
  }): Promise<ArticleModel> {
    try {
      let rawResult = await HttpUtil.put<Record<string, Object>>(
        `${ArticleService.BASE_PATH}/${id}`,
        data as Object
      )
      return ArticleModel.fromJson(rawResult)
    } catch (error) {
      let httpError = error as HttpError
      throw ArticleService.mapError(httpError)
    }
  }

  // 删除文章
  static async remove(id: number): Promise<void> {
    try {
      await HttpUtil.delete<Object>(`${ArticleService.BASE_PATH}/${id}`)
    } catch (error) {
      let httpError = error as HttpError
      throw ArticleService.mapError(httpError)
    }
  }

  // 点赞文章
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

  // ---- 错误映射：将通用 HttpError 转换为业务友好的提示 ----
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

**在页面中使用 ApiService：**

```typescript
@Entry
@Component
struct ArticleListPage {
  @State articles: ArticleModel[] = []
  @State isLoading: boolean = false
  @State errorMsg: string = ''
  @State currentPage: number = 1
  @State hasMore: boolean = true

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
        // 错误提示 + 重试按钮
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

## 3. 网络状态检测

检测网络可用性和类型，实现离线降级策略。

```typescript
// ==========================================
// NetworkMonitor —— 网络状态监控
// ==========================================

import { connection } from '@kit.NetworkKit'

// 网络状态枚举
export enum NetworkState {
  UNKNOWN = 'unknown',
  CONNECTED = 'connected',
  DISCONNECTED = 'disconnected'
}

// 网络类型枚举
export enum NetworkType {
  NONE = 'none',
  WIFI = 'wifi',
  CELLULAR = 'cellular',
  ETHERNET = 'ethernet',
  OTHER = 'other'
}

// 网络状态变化回调
type NetworkStateCallback = (state: NetworkState, type: NetworkType) => void

export class NetworkMonitor {
  private static currentState: NetworkState = NetworkState.UNKNOWN
  private static currentType: NetworkType = NetworkType.NONE
  private static callbacks: NetworkStateCallback[] = []
  private static netConnection: connection.NetConnection | null = null

  // ---- 查询当前网络状态 ----

  // 检查是否有可用网络（快速同步检查）
  static async hasNetwork(): Promise<boolean> {
    try {
      let hasNet = await connection.hasDefaultNet()
      return hasNet
    } catch (error) {
      console.error(`检查网络状态失败: ${JSON.stringify(error)}`)
      return false
    }
  }

  // 获取当前网络类型
  static async getNetworkType(): Promise<NetworkType> {
    try {
      let hasNet = await connection.hasDefaultNet()
      if (!hasNet) {
        return NetworkType.NONE
      }

      let netHandle = await connection.getDefaultNet()
      let netCapabilities = await connection.getNetCapabilities(netHandle)

      // 判断网络类型
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

  // ---- 网络状态监听 ----

  // 开始监听网络变化（在 EntryAbility 中调用）
  static startMonitoring(): void {
    if (NetworkMonitor.netConnection !== null) {
      return  // 已在监听
    }

    NetworkMonitor.netConnection = connection.createNetConnection()

    // 监听网络可用
    NetworkMonitor.netConnection.on('netAvailable', () => {
      NetworkMonitor.currentState = NetworkState.CONNECTED
      NetworkMonitor.updateType()
      NetworkMonitor.notifyCallbacks()
    })

    // 监听网络断开
    NetworkMonitor.netConnection.on('netLost', () => {
      NetworkMonitor.currentState = NetworkState.DISCONNECTED
      NetworkMonitor.currentType = NetworkType.NONE
      NetworkMonitor.notifyCallbacks()
    })

    // 监听网络能力变化（例如 WiFi 切换到蜂窝）
    NetworkMonitor.netConnection.on('netCapabilitiesChange', () => {
      NetworkMonitor.updateType()
      NetworkMonitor.notifyCallbacks()
    })

    // 注册监听
    NetworkMonitor.netConnection.register(() => {
      console.info('网络监听注册成功')
    })
  }

  // 停止监听
  static stopMonitoring(): void {
    if (NetworkMonitor.netConnection !== null) {
      NetworkMonitor.netConnection.unregister(() => {
        console.info('网络监听已注销')
      })
      NetworkMonitor.netConnection = null
    }
  }

  // 注册状态变化回调
  static onStateChange(callback: NetworkStateCallback): void {
    NetworkMonitor.callbacks.push(callback)
  }

  // 移除回调
  static removeCallback(callback: NetworkStateCallback): void {
    let index = NetworkMonitor.callbacks.indexOf(callback)
    if (index >= 0) {
      NetworkMonitor.callbacks.splice(index, 1)
    }
  }

  // 获取当前状态
  static getState(): NetworkState {
    return NetworkMonitor.currentState
  }

  // 获取当前类型
  static getType(): NetworkType {
    return NetworkMonitor.currentType
  }

  // 内部：更新网络类型
  private static async updateType(): Promise<void> {
    NetworkMonitor.currentType = await NetworkMonitor.getNetworkType()
  }

  // 内部：通知所有回调
  private static notifyCallbacks(): void {
    for (let callback of NetworkMonitor.callbacks) {
      callback(NetworkMonitor.currentState, NetworkMonitor.currentType)
    }
  }
}
```

**离线降级模式：**

```typescript
// ==========================================
// 离线降级策略 —— 网络不可用时使用本地缓存
// ==========================================

import { preferences } from '@kit.ArkData'

// 带离线降级的数据加载器
export class OfflineFirstLoader {
  private context: Context
  private store: preferences.Preferences | null = null

  constructor(context: Context) {
    this.context = context
  }

  // 初始化本地存储
  private async getStore(): Promise<preferences.Preferences> {
    if (this.store === null) {
      this.store = await preferences.getPreferences(this.context, 'offline_cache')
    }
    return this.store!
  }

  // 带离线降级的数据加载
  // 优先网络请求，失败时读取本地缓存
  async loadData<T>(
    cacheKey: string,
    fetcher: () => Promise<T>,
    parser: (raw: string) => T
  ): Promise<{ data: T; fromCache: boolean }> {
    // 先检查网络
    let hasNet = await NetworkMonitor.hasNetwork()

    if (hasNet) {
      try {
        // 有网络：从服务端获取
        let data = await fetcher()
        // 成功后缓存到本地
        let store = await this.getStore()
        await store.put(cacheKey, JSON.stringify(data))
        await store.flush()
        return { data: data, fromCache: false }
      } catch (error) {
        console.warn(`网络请求失败，尝试读取缓存: ${JSON.stringify(error)}`)
        // 网络请求失败，降级到缓存
        return await this.loadFromCache(cacheKey, parser)
      }
    } else {
      // 无网络：直接读缓存
      return await this.loadFromCache(cacheKey, parser)
    }
  }

  // 从缓存加载
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

**在页面中使用离线降级：**

```typescript
@Entry
@Component
struct OfflineReadyPage {
  @State articles: ArticleModel[] = []
  @State fromCache: boolean = false
  @State networkState: string = ''
  private loader: OfflineFirstLoader | null = null

  aboutToAppear(): void {
    // 组件内取 Context：用 this.getUIContext().getHostContext()（旧 getContext(this) 已不推荐，见 SKILL 常见错误 #10）。
    // 字段初始化期组件未挂载，延后到 aboutToAppear 构造 loader；getHostContext() 返回 Context | undefined，判空后再用。
    const context = this.getUIContext().getHostContext()
    if (context !== undefined) {
      this.loader = new OfflineFirstLoader(context)
    }

    // 监听网络变化
    NetworkMonitor.onStateChange((state: NetworkState, type: NetworkType) => {
      this.networkState = `${state} (${type})`
      if (state === NetworkState.CONNECTED) {
        // 网络恢复时自动刷新
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
        // 网络请求函数
        async (): Promise<ArticleModel[]> => {
          let pageResult = await ArticleService.getList(1, 50)
          return pageResult.list
        },
        // 缓存解析函数
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
      // 网络状态提示
      if (this.fromCache) {
        Row() {
          Text('当前显示离线缓存数据')
            .fontColor(Color.Orange)
            .fontSize(12)
        }
        .width('100%')
        .padding(8)
        .backgroundColor('#FFF3E0')
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

## 4. 请求缓存模式

内存级缓存，避免短时间内重复请求同一接口。支持过期自动失效。

```typescript
// ==========================================
// RequestCache —— 内存请求缓存
// ==========================================

// 缓存条目
class CacheEntry<T> {
  data: T
  timestamp: number    // 缓存写入时间
  ttl: number          // 生存时间（毫秒）

  constructor(data: T, ttl: number) {
    this.data = data
    this.timestamp = Date.now()
    this.ttl = ttl
  }

  // 是否已过期
  get isExpired(): boolean {
    return Date.now() - this.timestamp > this.ttl
  }

  // 剩余存活时间
  get remainingTtl(): number {
    let remaining = this.ttl - (Date.now() - this.timestamp)
    return remaining > 0 ? remaining : 0
  }
}

export class RequestCache {
  // 缓存存储
  private static cache: Map<string, CacheEntry<Object>> = new Map()
  // 默认缓存时间：5 分钟
  private static defaultTtl: number = 5 * 60 * 1000
  // 最大缓存条目数（防止内存泄漏）
  private static maxEntries: number = 100
  // 进行中的请求（防止并发重复请求）
  private static pendingRequests: Map<string, Promise<Object>> = new Map()

  // ---- 配置 ----

  // 设置默认缓存时间
  static setDefaultTtl(ttl: number): void {
    RequestCache.defaultTtl = ttl
  }

  // 设置最大缓存条目数
  static setMaxEntries(max: number): void {
    RequestCache.maxEntries = max
  }

  // ---- 核心方法 ----

  // 带缓存的请求
  // 流程：检查缓存 -> 有效则返回 -> 无效则发请求 -> 缓存结果 -> 返回
  static async cachedRequest<T>(
    cacheKey: string,
    fetcher: () => Promise<T>,
    ttl?: number
  ): Promise<T> {
    // 第一步：检查缓存
    let cached = RequestCache.cache.get(cacheKey)
    if (cached !== undefined && !cached.isExpired) {
      console.info(`命中缓存: ${cacheKey}，剩余 ${cached.remainingTtl}ms`)
      return cached.data as T
    }

    // 第二步：检查是否有相同请求正在进行（防止并发重复请求）
    let pending = RequestCache.pendingRequests.get(cacheKey)
    if (pending !== undefined) {
      console.info(`复用进行中的请求: ${cacheKey}`)
      return pending as Promise<T>
    }

    // 第三步：发起新请求
    let requestPromise = fetcher()
    RequestCache.pendingRequests.set(cacheKey, requestPromise as Promise<Object>)

    try {
      let data = await requestPromise

      // 缓存结果
      let cacheTtl = ttl ?? RequestCache.defaultTtl
      RequestCache.cache.set(cacheKey, new CacheEntry<Object>(data as Object, cacheTtl))

      // 检查缓存条目数，超出则清理最旧的
      RequestCache.evictIfNeeded()

      return data
    } finally {
      // 无论成功失败都移除进行中状态
      RequestCache.pendingRequests.delete(cacheKey)
    }
  }

  // ---- 缓存管理 ----

  // 使指定缓存失效
  static invalidate(cacheKey: string): void {
    RequestCache.cache.delete(cacheKey)
  }

  // 使匹配前缀的所有缓存失效（例如清除某个资源的所有缓存）
  static invalidateByPrefix(prefix: string): void {
    let keysToDelete: string[] = []
    RequestCache.cache.forEach((_value: CacheEntry<Object>, key: string) => {
      if (key.startsWith(prefix)) {
        keysToDelete.push(key)
      }
    })
    for (let key of keysToDelete) {
      RequestCache.cache.delete(key)
    }
  }

  // 清除所有缓存
  static clearAll(): void {
    RequestCache.cache.clear()
    RequestCache.pendingRequests.clear()
  }

  // 清除所有过期缓存
  static clearExpired(): void {
    let keysToDelete: string[] = []
    RequestCache.cache.forEach((entry: CacheEntry<Object>, key: string) => {
      if (entry.isExpired) {
        keysToDelete.push(key)
      }
    })
    for (let key of keysToDelete) {
      RequestCache.cache.delete(key)
    }
  }

  // 获取缓存统计信息
  static getStats(): { total: number; expired: number; active: number } {
    let total = RequestCache.cache.size
    let expired = 0
    RequestCache.cache.forEach((entry: CacheEntry<Object>) => {
      if (entry.isExpired) {
        expired++
      }
    })
    return {
      total: total,
      expired: expired,
      active: total - expired
    }
  }

  // 内部：超出上限时清理最旧的条目
  private static evictIfNeeded(): void {
    if (RequestCache.cache.size <= RequestCache.maxEntries) {
      return
    }

    // 先清过期的
    RequestCache.clearExpired()

    // 如果还超限，按写入时间删最旧的
    if (RequestCache.cache.size > RequestCache.maxEntries) {
      let oldestKey: string = ''
      let oldestTime: number = Number.MAX_VALUE
      RequestCache.cache.forEach((entry: CacheEntry<Object>, key: string) => {
        if (entry.timestamp < oldestTime) {
          oldestTime = entry.timestamp
          oldestKey = key
        }
      })
      if (oldestKey.length > 0) {
        RequestCache.cache.delete(oldestKey)
      }
    }
  }
}
```

**在 ApiService 中集成缓存：**

```typescript
// ==========================================
// 带缓存的 ApiService 示例
// ==========================================

export class CachedArticleService {
  private static readonly BASE_PATH = '/articles'
  // 缓存 key 前缀
  private static readonly CACHE_PREFIX = 'articles:'

  // 获取文章列表（带缓存，缓存 2 分钟）
  static async getList(page: number = 1, pageSize: number = 20): Promise<PageResult<ArticleModel>> {
    let cacheKey = `${CachedArticleService.CACHE_PREFIX}list:${page}:${pageSize}`

    return RequestCache.cachedRequest<PageResult<ArticleModel>>(
      cacheKey,
      async (): Promise<PageResult<ArticleModel>> => {
        // 实际网络请求
        return await ArticleService.getList(page, pageSize)
      },
      2 * 60 * 1000  // 缓存 2 分钟
    )
  }

  // 获取文章详情（带缓存，缓存 5 分钟）
  static async getDetail(id: number): Promise<ArticleModel> {
    let cacheKey = `${CachedArticleService.CACHE_PREFIX}detail:${id}`

    return RequestCache.cachedRequest<ArticleModel>(
      cacheKey,
      async (): Promise<ArticleModel> => {
        return await ArticleService.getDetail(id)
      },
      5 * 60 * 1000  // 缓存 5 分钟
    )
  }

  // 创建文章（创建后清除列表缓存）
  static async create(data: {
    title: string
    content: string
    category: string
  }): Promise<ArticleModel> {
    let result = await ArticleService.create(data)
    // 创建成功后，使列表缓存失效（下次请求会重新获取）
    RequestCache.invalidateByPrefix(`${CachedArticleService.CACHE_PREFIX}list:`)
    return result
  }

  // 更新文章（更新后清除相关缓存）
  static async update(id: number, data: {
    title?: string
    content?: string
  }): Promise<ArticleModel> {
    let result = await ArticleService.update(id, data)
    // 清除该文章的详情缓存和列表缓存
    RequestCache.invalidate(`${CachedArticleService.CACHE_PREFIX}detail:${id}`)
    RequestCache.invalidateByPrefix(`${CachedArticleService.CACHE_PREFIX}list:`)
    return result
  }

  // 删除文章（删除后清除相关缓存）
  static async remove(id: number): Promise<void> {
    await ArticleService.remove(id)
    RequestCache.invalidate(`${CachedArticleService.CACHE_PREFIX}detail:${id}`)
    RequestCache.invalidateByPrefix(`${CachedArticleService.CACHE_PREFIX}list:`)
  }

  // 强制刷新（清除所有文章缓存后重新请求）
  static async forceRefreshList(page: number = 1, pageSize: number = 20): Promise<PageResult<ArticleModel>> {
    RequestCache.invalidateByPrefix(`${CachedArticleService.CACHE_PREFIX}list:`)
    return await CachedArticleService.getList(page, pageSize)
  }
}
```

**完整使用示例（页面中整合缓存服务）：**

```typescript
@Entry
@Component
struct CachedArticlePage {
  @State articles: ArticleModel[] = []
  @State isLoading: boolean = false
  @State cacheInfo: string = ''

  aboutToAppear(): void {
    this.loadData()
  }

  async loadData(): Promise<void> {
    this.isLoading = true
    try {
      let result = await CachedArticleService.getList(1, 20)
      this.articles = result.list
      // 显示缓存统计
      let stats = RequestCache.getStats()
      this.cacheInfo = `缓存: ${stats.active}条有效 / ${stats.total}条总计`
    } catch (error) {
      console.error(`加载失败: ${JSON.stringify(error)}`)
    } finally {
      this.isLoading = false
    }
  }

  build() {
    Column() {
      // 缓存信息
      Text(this.cacheInfo)
        .fontSize(12)
        .fontColor('#999999')
        .padding(8)

      Row({ space: 8 }) {
        // 普通加载（可能命中缓存）
        Button('加载')
          .onClick(() => { this.loadData() })

        // 强制刷新（跳过缓存）
        Button('强制刷新')
          .onClick(async () => {
            this.isLoading = true
            try {
              let result = await CachedArticleService.forceRefreshList(1, 20)
              this.articles = result.list
            } finally {
              this.isLoading = false
            }
          })

        // 清除所有缓存
        Button('清除缓存')
          .onClick(() => {
            RequestCache.clearAll()
            this.cacheInfo = '缓存已清除'
          })
      }
      .padding(8)

      if (this.isLoading) {
        LoadingProgress().width(40).height(40)
      }

      List() {
        ForEach(this.articles, (article: ArticleModel) => {
          ListItem() {
            Column() {
              Text(article.title).fontSize(16)
              Text(`浏览: ${article.viewCount}  点赞: ${article.likeCount}`)
                .fontSize(12)
                .fontColor('#999999')
            }
            .padding(12)
            .width('100%')
            .alignItems(HorizontalAlign.Start)
          }
        }, (article: ArticleModel) => article.id.toString())
      }
      .layoutWeight(1)
    }
  }
}
```
