<!-- when: Phase 2.5a 框架 API 基础映射时加载（platform: android 必读）；为扫描出的标准框架栈标注 HarmonyOS Kit 等价物 -->
<!-- topics: framework mapping, Retrofit, OkHttp, WebSocket, SSE, javax.crypto, SharedPreferences, Kit 等价物, @kit.NetworkKit, rcp -->

# Android 框架 API → HarmonyOS Kit 等价物静态映射表

> **用途**：Phase 2.5a 的事实源。扫描结果里的**标准框架栈**（网络/序列化/加密/存储/设备标识）按本表直接写入「已命中」提示段，**不依赖** `hmos_references_file`、不依赖任何 MCP/在线查询 —— 本表内容已经 harmony-docs 离线官方快照（2026-05-24）逐条核验。
> **边界**：只收录**官方 Kit 有权威对应**的框架 API。三方 SDK（微信/支付宝/个推/友盟/Firebase…）官方 Kit 不覆盖 → 永远走 2.5b 用户预知文件，本表不猜。

## 1. 网络栈

| Android 侧（扫描特征） | HarmonyOS 等价物 | import | 备注 |
|---|---|---|---|
| Retrofit / OkHttp / HttpURLConnection | NetworkKit `http.createHttp().request()` | `import { http } from '@kit.NetworkKit'` | 命令式；响应须 `expectDataType: http.HttpDataType.STRING` 防自动 parse（见 arkts-network-troubleshoot I1）|
| OkHttp Interceptor 架构（拦截器≥1 个） | **rcp 会话+拦截器**：`rcp.createSession({ interceptors })` | `import { rcp } from '@kit.RemoteCommunicationKit'` | `rcp.Interceptor.intercept(context, next)` 与 OkHttp 同构；Session API 11+/拦截器 API 12+。选型详见 `arkts-network-troubleshoot/references/http-vs-rcp.md`；NetworkKit 自 API 22 也有内建 `HttpInterceptor` |
| Retrofit baseUrl 多环境 | `rcp.SessionConfiguration.baseAddress` 或自封装常量 | 同上 | — |
| WebSocket（OkHttp ws / Java-WebSocket） | NetworkKit `webSocket.createWebSocket()` | `import { webSocket } from '@kit.NetworkKit'` | connect/send/close + on('message'/'close'/'error') 事件订阅 |
| SSE（OkHttp EventSource） | **无独立 SSE API** —— NetworkKit `requestInStream` + `on('dataReceive')` 流式自拼 | `import { http } from '@kit.NetworkKit'` | 迁移难点，`migration_concerns` 必标；分帧/重连/`text/event-stream` 解析全部自实现 |
| GraphQL / gRPC 客户端 | **无官方 Kit** | — | 走 http/rcp 自封装或社区 ohpm 包；`migration_concerns` 标注 |
| DownloadManager / 大文件下载 | `request.agent`（后台下载任务） | `import { request } from '@kit.BasicServicesKit'` | 进度/断点/通知由系统代理；详见 arkts-download-manager skill |

## 2. 序列化 / JSON

| Android 侧 | HarmonyOS 等价物 | 备注 |
|---|---|---|
| Gson / Moshi `@SerializedName` | **无等价机制** —— ArkTS class 字段名默认即 JSON key | 字段名≠JSON key 的必须手写 FIELD_MAP 镜像（迁移高风险点，`migration_concerns` 必标；运行期细节归 arkts-network-troubleshoot Phase 4）|
| `JSON.parse` 泛型反序列化 | `JSON.parse(text) as T` 是**不安全 cast**（class 方法/setter 静默丢失） | Bean 用 interface 或手动 assign |

## 3. 加密 / 签名（auth_detail 相关）

| Android 侧 | HarmonyOS 等价物 | import |
|---|---|---|
| `javax.crypto.Mac`（HMAC 签名拦截器） | `cryptoFramework.createMac(algName)` | `import { cryptoFramework } from '@kit.CryptoArchitectureKit'` |
| `javax.crypto.Cipher`（AES/RSA） | `cryptoFramework.createCipher(transformation)` | 同上 |
| `MessageDigest`（MD5/SHA） | `cryptoFramework.createMd(algName)` | 同上 |
| — | ⚠️ 字节级怪癖（`Uint8Array.byteOffset` 防御拷贝、HMAC algName 无后缀、hex 大小写）| 实现细节归 `arkts-network-troubleshoot` Phase 3，本表只给编目标注 |

## 4. 本地存储（token / 公参持久化相关）

| Android 侧 | HarmonyOS 等价物 | import |
|---|---|---|
| SharedPreferences / MMKV | `preferences`（须 await init，注意启动 race） | `import { preferences } from '@kit.ArkData'` |
| Room / SQLite（接口缓存层） | `relationalStore`（RdbStore + RdbPredicates） | `import { relationalStore } from '@kit.ArkData'` |
| File 缓存 / 导入导出 | `fileIo`（沙箱路径） | `import { fileIo } from '@kit.CoreFileKit'` |

## 5. 设备标识 / 公参字段

| Android 侧 | HarmonyOS 等价物 | import | 备注 |
|---|---|---|---|
| `Settings.Secure.ANDROID_ID` | **无 1:1 等价** —— 首启 `util.generateRandomUUID()` 持久化复用 | `import { util } from '@kit.ArkTS'` | 后端 NOT NULL 约束场景的标准兜底 |
| OAID（`DeviceIdentifier.getOAID()`） | `identifier.getOAID(): Promise<string>` | `import { identifier } from '@kit.AdsKit'` | 需 `ohos.permission.APP_TRACKING_CONSENT`；**拒绝授权返全 0——实测常态（用户多不授权）**，不可假设 OAID 非空 |
| `Build.BRAND / MODEL / VERSION` | `deviceInfo.brand / .productModel / .osFullName` | `import { deviceInfo } from '@kit.BasicServicesKit'` | — |

> **设备指纹进后端（生成 deviceNo / NOT NULL 约束）时的可靠做法**：**OAID 非全 0 才用它、否则退持久化 UUID，二者取其一保证"永不空/全 0"**——持久化 UUID 才是可靠主路径，OAID 是"能用则用"；**禁送空串/全 0**（后端据指纹反查/生成时会 NPE 或 500）。
> **跨平台连续性盲区**：HMOS 的 OAID/UUID 与 Android 端不同 → 同一物理设备两端生成的 deviceNo 不同 → **老 Android 用户迁 HMOS 会被后端当成新设备**（丢原设备/游客态）。账号连续性须**后端配合**（接受 HMOS 身份映射 / 迁移）；客户端补非空指纹只保**新装**用户开箱可用。

## 使用规则（Phase 2.5a）

1. 逐条对照扫描结果：`services` 的网络栈特征、`interceptors`、`third_party_apis` 里实为框架能力的项（如 WebSocket 域名）、auth_detail 的签名算法 → 命中本表即写入「已命中」表，**来源列填 `framework-kit-mapping.md`**。
2. 表里「无等价 / 无官方 Kit」的条目**也要写进提示**（它们正是 `migration_concerns` 的素材），不要因为"没有对应物"就跳过。
3. 本表**只服务 markdown 提示段** —— 与 Phase 2.5b 相同约束：不给 `api-inventory.json` 新增任何字段。
4. 三方 SDK 一律不查本表（官方 Kit 不覆盖），归 2.5b / plan grill 补问。
