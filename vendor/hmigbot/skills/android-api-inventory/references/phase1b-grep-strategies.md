# Phase 1b 补扫 grep 策略与极端情况降级

> SKILL.md Phase 1b 的展开。**判定何时补扫**在主文件（规则 A / B / C），**具体跑哪些 grep + 极端情况怎么降级**在本文件。

---

## 按技术栈选 grep 策略

按项目 `build.gradle` 声明的依赖识别技术栈，**不要全部跑**，只跑该项目实际用到的：

| 技术栈 | grep 关键字 | 说明 |
|--------|-------------|------|
| **裸 OkHttp** | `OkHttpClient\|\.newCall\(\|Request\.Builder` | 从上下文推断 URL 和用途 |
| **Ktor** | `HttpClient\s*\{\|\.get\(\|\.post\(\|\.submitForm\(` | Kotlin Multiplatform 项目常见 |
| **WebSocket** | `newWebSocket\|wss?://\|WebSocketListener` | OkHttp / 标准 WS |
| **SSE** | `EventSource\|text/event-stream\|okhttp-sse` | 服务端推送 |
| **GraphQL** | `apollo\|GraphQLRequest\|@Query\s*\(\s*"""` | Apollo 客户端 |
| **gRPC** | `ManagedChannel\|StreamObserver\|\.newBlockingStub` | Protocol Buffers + gRPC |
| **SDK 黑盒** | 先在 `build.gradle(.kts)` 找依赖清单识别 SDK（如 `twitch4j`、`com.aallam.openai`），然后 Grep 项目中调用该 SDK 的方法 | 注意：grep 的是**调用点**，不是 SDK 内部 HTTP |

### HMOS（`platform: harmony`）侧的对应物

HMOS 侧 Phase 1b 补扫目标换成：

| 技术栈 | grep 关键字 |
|--------|-------------|
| `@kit.NetworkKit` HTTP | `http\.createHttp\(\)` + 调用点拼 URL |
| `@kit.NetworkKit` WebSocket | `webSocket\.createWebSocket\(\)` |
| 三方 SDK 黑盒 | 在 `oh-package.json5` 找依赖，grep 调用点 |

「按技术栈选 grep 策略」**框架**两平台通用，只是 grep 关键字换。

---

## auth 链专项 grep 字典（Phase 2.75 auth_model 素材 · 补捕获盲区）

> 端点级扫描抓不到"请求可信化 / 设备身份"这些藏在拦截器和基类里的机制——fitness 复盘实证"19 header 抽 0 签名"整层漏抓。Phase 2.75 建 `auth_model`（及下游 Phase 2.8 的 `chain-auth`）前，**主动**用下表按层 grep，逐层要么抓到机制、要么显式判"无"（无签名层本身是红旗，触发复查）。

| 层 | grep 起手式 | 落点 |
|---|---|---|
| **L2 签名/加密** | `sign` `nonce` `authSign` `signature` `safe-env` `private-key`(私钥) `encrypt` `getEncList` `decodeType` `HmacUtil\|AesGcm\|RsaUtil` | `auth_model.token_injection`（signing/body_rewrite evidence）；密钥/盐**记 file:line**（禁掩码，值在源码） |
| **L3 设备身份** | `oaid` `OAID` `deviceId` `getDeviceId` `AndroidID\|ANDROID_ID` `uuid\|UUID` `MediaDrm\|Widevine` `initUser` `deviceLogin` `vistorToken\|visitorToken` `guest\|tourist` `device/register` | `auth_model.token_acquisition` / `identity_model` / 轴A、轴B |
| **L0 身份常量** | `tenantCode` `productId` `applicationId` `appId` `BASE_URL` `buildConfigField` | `base_urls` / `api_related_constants`；**身份常量沉在资源子模块（`lib-res*/AppConstant.kt` 等）时，grep 范围要下探到子模块**，别只扫主 module（fitness 租户三元组坑） |

**边界（重要）**：**L1 隐私关键词（`isAgree` / `privacy` / `AGREE_PRIVACY` / `initThirdSdk`）不进本 skill** —— 隐私门控不是网络 API，归 feature-spec / source-understanding；本 skill 只到"L0 身份常量、L2 可信化、L3 设备身份"。

**grep 注意（通用，避免漏抓/误判）**：
- **大小写/下划线/驼峰变体都搜**：如 `private-key` 亦搜 `PRIVATE_KEY` / `privateKey`；关键词是"起手式"不是精确串。
- **加密可能自研或封在二进制 AAR**：标准 `encrypt` / `AesGcm` / `RsaUtil` 搜不到 ≠ 无加密——追 `*.encode` / `*.decrypt` / `*Encrypt` 的**定义处**拿算法/密钥/IV；`decodeType` 之类是**解密标记位 ≠ 算法实现**，别把标记当加密本身。算法/密钥封在不可读 AAR → 标 `MISSING-TRUTH`（需后端/厂商）。
- **命中设备标识后回验用途**（定轴B）：看它是否出现在**签名串 / 登录请求体 / 换 token 的请求**里——是 → 轴B `identity-basis`/`request-trust-component`；否（仅埋点/业务）→ 轴B `irrelevant`，别误当登录前置。
- **多模块可能有并行子栈**：子模块可能自带同名 `Interceptor`/`ApiService`/网络 Loader——按**主 applicationId / 主 Loader 归属**分主副，别把子栈当主栈。
- **排除生成物降噪**：grep 加 `--glob '!build/**'`（或跳过 kapt stubs），否则命中翻倍。
- **公参/身份值抓"来源"、别用 gradle 默认占位**：进签名的公参对象（platformInfo/公共请求参数）的身份字段（`versionCode`/`versionName`/`baseType`/`applicationId`）在**多 flavor/渠道包**应用里常来自 **flavor 配置 XML**（`product.xml` 等被 build.gradle 解析的文件），真实**渠道值**在 **walle 渠道清单** `channel/*.txt`——从这些取真值，**别用 gradle 里的默认占位**（如 `versionName "1.0"`/code 1，那是 fallback，后端不认）。这些值**既进签名、又是后端身份门**（错了→ -401/权限门 / mediaNo 类映射 NPE）。捕获记**字段的值来源**即可，精确值交 probe 循环实测（见 arkts-network-troubleshoot probe-runbook 候选来源约定）。

---

## 补扫产物的处置

按以下两种方式之一落地：

- **方式 A（推荐）**：以同样的 JSON 结构**追加**到 `raw_apis.json` 对应字段（如新增 `websockets` / `sse_streams` / `sdk_providers` 数组）
- **方式 B**：单独存 `raw_apis_supplemental.json`，Phase 3 汇总时一并读

两种方式 Phase 2-4 都能消费；选哪个看项目偏好与脚本能否扩展。

---

## 极端情况降级（规则 C）

### React Native / Flutter 壳

判定：源码根有 `package.json` + `node_modules/`（RN）或有 `pubspec.yaml`（Flutter）。

此时 Kotlin / Swift 层只是 RN/Flutter 的 bootstrap，无法用本 skill 分析业务接口。处置：

1. **不要勉强扫 Kotlin** —— 业务 HTTP 全在 JS/Dart 层
2. Phase 3 产出一份简短说明文档（`api-inventory.md`），声明本 skill 不适用 + 建议用户在 JS/Dart 层重跑 API 梳理
3. `coverage` 字段标 `_mode: degraded`，`gaps` 为空

### 离线 / 无网络项目

判定：`raw_apis.json` 的 `services` 与 `hardcoded_urls` 都为 0，build.gradle 也无网络相关依赖。

处置：

1. 跳过 Phase 1b 全量补扫
2. 直接 Phase 3 输出"本项目无外部 API"文档
3. 可列系统级 API 依赖（ContentResolver / 文件系统 / MediaStore 等），用 `local_system_apis` 字段
