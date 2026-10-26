# 网络栈选型：裸 `@ohos.net.http` vs RemoteCommunicationKit（rcp）

> 本 skill 的代码模板（[templates/code/http-client-unwrap.ets](templates/code/http-client-unwrap.ets)）基于裸 `@ohos.net.http`（NetworkKit）。它能跑通，但不是唯一选择 —— HarmonyOS 还提供更高层的 **RemoteCommunicationKit（命名空间 `rcp`）**，其内建拦截器/会话模型与 Android OkHttp 几乎 1:1，往往更省样板。本文给选型依据，**不强制改模板**。
>
> **经 harmony-docs（快照 2026-05-24）核验**：`import { rcp } from '@kit.RemoteCommunicationKit'`；`SessionConfiguration` / `Response.toJSON()` 自 **API 11**（4.1.0），`rcp.Interceptor.intercept(context, next): Promise<Response>` 自 **API 12**（5.0.0）。落地前确认工程 compatibleSdkVersion ≥ 12。

## 一句话差异

| | 裸 `http`（NetworkKit） | `rcp`（RemoteCommunicationKit） |
|---|---|---|
| 层级 | 低层：`http.createHttp().request(url, opts)`，逐请求手搓 | 高层：`rcp.createSession(config)` → `session.get/post/fetch` |
| 拦截器 | 长期无内建概念，自己在封装层串（**API 22 起新增 `HttpInterceptor.interceptorHandle`**，但基线 ≥22 才可用） | **内建 `rcp.Interceptor` 链**（`intercept(context, next)`，API 12+），与 OkHttp Interceptor 同构 |
| 会话级配置 | 每请求重复传 | `SessionConfiguration`：baseAddress / headers / 超时 / 证书 / 代理一处配 |
| JSON | 手动 `JSON.parse`（注意 I1 `expectDataType`）| `response.toJSON(): object \| null` 自动解析（**同样要防 I1 类自动 parse 误判**）|
| cookie / 重定向 / trace | 手动 | 内建 |

## Android → rcp 迁移映射（为什么常更顺）

- **OkHttp `Interceptor` 链** → `rcp.Interceptor[]`，`intercept(context: RequestContext, next: RequestHandler): Promise<Response>` 与 OkHttp 的 `intercept(chain)` 几乎一一对应：公参注入 / 签名 / 日志 / token 刷新都放拦截器，**比裸 http 在封装层手串更接近原架构**。
- **OkHttp `addInterceptor` 顺序** → `SessionConfiguration.interceptors` 数组顺序一致。
- **Retrofit baseUrl** → `SessionConfiguration.baseAddress`。
- **响应 unwrap（D1）** → 仍在拦截器里做（拿到 `rcp.Response` 后剥 BaseBean），但要注意 `toJSON()` 的解析行为（见下「坑」）。

## 选型建议

**选 rcp 当**：想 1:1 复刻 OkHttp 的拦截器架构 / 要会话级统一配置（baseAddress·headers·超时·证书）/ 要内建 cookie·重定向·trace / 新项目无历史 http 模板包袱，且基线 ≥ API 12。

**选裸 http 当**：要逐请求最大控制 / 团队已有大量 http 封装与本 skill 模板 / 字节级签名链路想完全自己掌控 read/write / 基线 < 12。（基线 ≥ 22 时裸 http 也有内建 `HttpInterceptor` 可用。）

## 迁移到 rcp 时仍要带过去的坑

- **I1 自动 parse**：rcp `toJSON()` 返回 `object | null`，与 http `expectDataType` 是同一类问题 —— 后端返非标准 JSON / 空 body 时拿到 `null`，业务码判定前必须判空（同 I3 空 body length 守卫思路）。
- **I4 权限**：rcp 一样要 `ohos.permission.INTERNET`，缺则请求未发出即拒（错误码 201 权限拒绝）。
- **签名字节级（A 类）**：rcp 不改变 cryptoFramework 的 `algName` / `utf8Bytes` 防御拷贝问题 —— 签名逻辑放拦截器，但 [sign-util.ets](templates/code/sign-util.ets) 的字节处理照搬。
- **D1 unwrap**：rcp 拦截器里 unwrap BaseBean 时，三方厂商响应不要被当自有信封剥（同 pitfalls D1 的 `unwrapBaseBean=false` 约定）。

## rcp 拦截器骨架（参考）

```typescript
import { rcp } from '@kit.RemoteCommunicationKit'

class SignInterceptor implements rcp.Interceptor {
  async intercept(context: rcp.RequestContext, next: rcp.RequestHandler): Promise<rcp.Response> {
    // 1. 注入公参 + 签名头（对应 OkHttp Interceptor）
    context.request.headers = { ...context.request.headers, 'sign': computeSign(context.request) }
    const resp = await next.handle(context)        // 放行
    // 2. 响应 unwrap（D1）：剥 BaseBean.data，三方响应保持不剥
    return resp
  }
}

const session = rcp.createSession({
  baseAddress: 'https://api.example.com',
  interceptors: [new SignInterceptor()],
  requestConfiguration: { transfer: { timeout: { connectMs: 10000, transferMs: 10000 } } }
})
// const r = await session.get('/user/info')
```

> Session / Request / Response / Interceptor 的全字段以官方 RemoteCommunicationKit 文档（`rcp.md`）为准；本骨架只保证结构正确，字段细节落地时对照官方文档或（如工程已配）`harmony-docs-cli` 查询。
