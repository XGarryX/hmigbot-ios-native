# 错误日志 → Phase 反向救火表

> 联调时收到具体错误，查这张表定位到 Phase，再到 [phases.md](phases.md) 对应章节排查。修复后回 Phase 6 重测。

## HTTP 状态码 / 业务码

| 错误特征 | 关键日志 | Phase | 核心检查项 |
|---------|---------|-------|----------|
| 404 路径错 | `No static resource xxx` | 1.1 | URL 漏前缀 / 接口名 ≠ 服务端路径（pitfalls D2）|
| -500 字段缺失 | `Missing request attribute 'xxx' of type Integer` | 1.2 | body 字段漏（pitfalls D3）|
| -500 后端 NPE | `Cannot invoke "...Enum.ordinal()" because xxx is null` | 1.5 / 1.6 | 公参字段缺 / packageName 不在白名单（pitfalls D4 / D5）|
| -500 DB 约束 | `Column 'XXX' cannot be null` | 1.5 | 公参字段必须非空 + 后端 NOT NULL（pitfalls D4）|
| -1001 用户未登录 | `用户未登录` 业务码 | 2 + 4 | 启动期 token 未写 + ResponseInterceptor unwrap 缺（pitfalls C1 / D1）|
| HTTP 401 | response.code == 401 | 1.4 + 3 | 签名错（pitfalls A 类）/ token 失效 |

## 拦截器 / 签名

| 错误特征 | 关键日志 | Phase | 核心检查项 |
|---------|---------|-------|----------|
| HMAC key 长度错 | `ConvertSymmKey: Invalid param: input key length is invalid!` | 3 | utf8Bytes 防御性拷贝 + HMAC algName 无后缀（pitfalls A1/A2）|
| signature 为空 | `signature=""` 或 `convert sym key failed` | 3 | 同上 |
| 签名长度对但 401 | response 401 + signature 长度正常 | 3.3 | hex 大小写错 / base64 vs hex 错（pitfalls A3）|
| MD5 中间值不一致 | 与 Android 同 input 算结果不同 | 3 + 1.4 | hex 大小写错 / 输入拼接顺序错 |

## 启动期 / AppStorage

| 错误特征 | 关键日志 | Phase | 核心检查项 |
|---------|---------|-------|----------|
| 协议每次冷启都弹 | 已同意但每次冷启重弹 | 2 | onWindowStageCreate 没 await PreferencesUtil.init（pitfalls C1）|
| prefs 未 ready | `prefs not init` (hilog) | 2 | 同上 |
| download 失败 | `download failed: No UIAbilityContext` | 2 | AppStorage('context') 未注入（pitfalls C2）|
| 拦截器静默 | HttpLog 不打请求/响应 body | 2 | AppStorage('isDebug') 未注入或 false |
| 拦截器公参全空 | platformInfo 内 markId/oaid/userId 都空 | 2 | PreferencesUtil.isReady=false 走默认值 |
| EventBus 报错 | `EventBus.post called before init` | 2 | EntryAbility.onCreate 未调 EventBus.init |
| 静态工具类 ctx 空 | `context is undefined` 在 SignUtil / Service | 2 | 用 AppStorage.get('context')（pitfalls C3 / H2）|

## ArkTS 语言陷阱

| 错误特征 | 现象 | Phase | 核心检查项 |
|---------|---------|-------|----------|
| 编译报对象字面值 | `arkts-no-untyped-obj-literals` | 编译期 | 行内 `{}` → interface / Record / new Object()（pitfalls B4）|
| 字段 undefined | `Cannot read property length of undefined` | 4 | JSON.parse as T 不安全 cast / @SerializedName 没镜像（pitfalls B1/B2）|
| AppStorage 拿不到 | `AppStorage.get('userData.token')` 永远 undefined | 5 | dot-notation 不展开，整对象读（pitfalls B3）|
| appName 显示资源 key | platformInfo.appName = `"$string:app_name"` | 1.5 | bundleInfo.label 是占位，需 resourceManager 解析（pitfalls B5）|

## 响应链路

| 错误特征 | 现象 | Phase | 核心检查项 |
|---------|---------|-------|----------|
| HTTP 200 但字段 undefined | userData.token / userId 都 undefined | 4 | unwrap 没启用 / data 字段没抽（pitfalls D1）|
| isResponseSuccess 永远 false | 业务码判定全走失败分支 | 4 | @SerializedName 字段没镜像（status → errorCode）（pitfalls B1）|
| 部分 Bean 字段读不到 | 某些 @SerializedName 映射字段 undefined | 4 + 1.3 | FIELD_MAP 没包含这些字段 |
| 三方接口数据被错误 unwrap | 三方厂商响应被当自有 BaseBean 处理 | 4 | vendorInstance 的 unwrapBaseBean 应保持 false |
| Token 失效不触发重登 | 服务端返 -1001 但 UI 没反应 | 4 | ResponseInterceptor 业务码检测字段名错 |

## UI 订阅

| 错误特征 | 现象 | Phase | 核心检查项 |
|---------|---------|-------|----------|
| 永远显示未登录 | 登录成功 + 抓包 token 拿到，但 MinePage 仍未登录 | 5 | @Prop 反模式，改 @StorageProp 自治订阅（pitfalls E1）|
| 跨页面切换数据延迟 | A 页面退出后 B 页面没刷新 | 5 | 双订阅模式（pitfalls E3）|
| 退出登录 UI 没刷新 | logout 成功但 UI 仍显示登录态 | 5 | clearLocalUser 没派发 USER_DATA_UPDATE |
| VIP 支付成功后入口仍显示 | 已开通 VIP 但首页仍显示「开通」 | 5 | 派生 isVip 逻辑错 / vipLevel 写入未触发刷新 |

## 三方 SDK

| 错误特征 | 关键日志 | Phase | 核心检查项 |
|---------|---------|-------|----------|
| `Cannot find module 'xxx'` | 编译期 | 0 / 编译 | ohpm install / oh-package.json5 / .ohpmrc 私仓源（pitfalls G5）|
| canOpenLink false | `bundleManager.canOpenLink('weixin://')` 返 false | 2.5 | module.json5 querySchemes 漏配 |
| onResp 永不触发 | 微信 / 支付宝授权回调不进入 | 2.4 | onCreate + onNewWant 都需调 handleSdkWant |

## 资源 / 国际化

| 错误特征 | 现象 | Phase | 核心检查项 |
|---------|---------|-------|----------|
| 主题色错 | 引入 lib 后变成 lib 默认色 | — | HAR 资源命名空间冲突（pitfalls H1）|
| string 显示资源 key | 切换语言不变化 | — | resources/<locale>/ 缺定义（pitfalls H3）|
| $r() 解析失败 | 编译过但运行时显示默认色 | — | 资源 key 拼写错 / HAR 资源未打进编译产物（pitfalls H4）|

## HMOS NetworkKit 平台陷阱（运行时全废型）

> 共同特征：**编译 PASS + HAP 正常生成 + 静态分析全过**，但 app 跑起来所有 API 都失败。出现这类症状**先按 I4 → I1 → I3 → I2 顺序排查**，再谈后端 / 签名 / 业务逻辑。

| 错误特征 | 关键日志 | Phase | 核心检查项 |
|---------|---------|-------|----------|
| 所有接口走 exception / 全部 JSON parse error | `JSON parse error: SyntaxError: Unexpected end of JSON input` 且后端正常返 JSON | 0 / 4 | `expectDataType: http.HttpDataType.STRING` 未指定 → response.result 被框架自动 parse 成 Object，typeof 判 string 走错分支（pitfalls I1）|
| 请求未发出 / 权限拒绝 | `request failed: 201` / 类似权限错误码 / hilog 报 permission denied | 0 | `module.json5` 缺 `ohos.permission.INTERNET` 声明（pitfalls I4）|
| 偶发空 body 误判 exception | HTTP 200 + `SyntaxError: Unexpected end of JSON input`，body 为空 | 4 | JSON.parse 前缺 `bodyStr.length === 0` 守卫（pitfalls I3）|
| GET 请求被代理 400 | 严格 WAF / CDN 环境下 GET 返 400 Bad Request | 1.1 / 6 | GET 误设 `Content-Type` 应改 `Accept`（pitfalls I2）|
| 全工程联调"网络异常" | 所有接口都走 onException / onFailure 分支 | 0 → I 类全查 | 按 I4 → I1 → I3 → I2 顺序排查；先确认权限 + 类型转换 + 空 body 防御 + header 规范 |

## 权威错误码速查（第二查找轴）

> 上面各表按「症状字符串」查；本表按**官方错误码数值**查 —— 日志里有裸错误码时从这里直接定位。码值经 harmony-docs（快照 2026-05-24）核验，全表见官方《Network Kit/错误码/HTTP错误码》与《crypto framework错误码》。

### 通用

| 码 | 官方含义 | Phase | 排查方向 |
|---|---|---|---|
| 201 | Permission denied 权限拒绝 | 0 | `module.json5` 缺 `ohos.permission.INTERNET`（pitfalls I4）|
| 401 | 参数检查失败（系统 API 入参错，**非 HTTP 401**）| — | 调用处入参类型/必填；勿与 HTTP 401 签名问题混淆 |

### NetworkKit HTTP（23000xx）

| 码 | 官方含义 | Phase | 排查方向 |
|---|---|---|---|
| 2300003 | URL 格式错误 | 1.1 | URL 拼接漏前缀 / 常量抽取错（pitfalls D2）|
| 2300006 | 域名解析失败 | 0 / 6 | base_url 环境配错 / 设备网络 / 私有域名仅内网可解析 |
| 2300007 | 无法连接到服务器 | 0 / 6 | 端口 / 防火墙 / 后端服务未起 |
| 2300008 | 服务器返回非法数据 | 4 | 响应非预期格式；先抓包看真实 body 再谈 unwrap |
| 2300009 | 拒绝对远程资源的访问 | 1.4 / 3 | 鉴权头缺失 / WAF 拦截 |
| 2300028 | 操作超时 | 2 / 6 | 超时配置 / 弱网；区分 connect 与 transfer 超时 |
| 2300052 | 服务器没有返回内容 | 4 | 空 body —— `JSON.parse('')` 前必须 length 守卫（pitfalls I3）|
| 2300094 | 身份校验失败 | 3 | SSL/SSH 层身份错，区别于业务签名 401 |
| **2300997** | **明文 HTTP 被拦截** | 1.6 | Android `usesCleartextTraffic` 的 HMOS 对应：测试环境 http:// 接口需配置网络安全策略放行明文，或改 https |
| **2300998** | **不允许访问域名** | 1.1 / 6 | 元服务/受管环境域名白名单未配；确认分发形态的域名管控 |
| 2300999 | 内部错误 | 6 | 升级 SDK / 收集 hilog 完整上下文再判 |

### cryptoFramework（Phase 3 签名链路）

| 码 | 官方含义 | 排查方向 |
|---|---|---|
| 17620001 | 内存操作失败 | 入参 buffer 异常 —— 优先查 `byteOffset` 防御拷贝（pitfalls A1）|
| 17620002 | ArkTS↔C 参数转换失败 | DataBlob 构造错：必须 `{ data: Uint8Array }` 整段拷贝后传 |
| 17620003 | 参数校验失败 | `algName` 不合法（如 HMAC 带了多余后缀，pitfalls A2）/ key 长度非法（`ConvertSymmKey invalid`）|
| 17630001 | 算法库操作错误 | init/update/doFinal 调用顺序错 / key 与算法不匹配 |

## 使用方法

1. 联调出错 → 复制关键日志关键词 grep 本表
2. 定位 Phase → 跳 [phases.md](phases.md) 对应小节排查
3. 修复后回 Phase 6 重测当前业务链路
4. 不要跨 Phase 跳过失败接口继续测后续链路

找不到对应错误时：可能是新坑（回写本表）/ 业务特定错误（找后端 / 看 spec/baseline/decisions.md）/ HMOS SDK 版本相关（升级 SDK）。
