# 公共约定（common）   ← 分层形态下的公共约定骨架

> 多端点复用的「信封 / 签名 / 公参 / 共享 Bean / 业务码」**在此写一次**，各 `apis/*.md` 用链接引用。
> 这是分层的核心收益：合并一类，避免在每个 endpoint 重复展开。

---

## 通道与 BaseURL

示例项目网络层有 4 个通道，分别对应 4 个 `HttpClient` 实例：

| 通道 | BaseURL | 用途 | 实例 |
|------|---------|------|------|
| 自有业务 | `AppConfig.baseUrl`（动态） | 用户 / 支付 / 业务接口 | `HttpClient.defaultInstance()`（启用 unwrap）|
| AI 图像 vendor-A | `https://image-api.vendor-a.com` | 图像生成 | `HttpClient.vendorAInstance()`（不 unwrap）|
| LLM vendor-B | `https://llm-api.vendor-b.com` | 聊天 / Bot | `HttpClient.vendorBInstance()`（SSE 流式）|
| TTS vendor-C | `https://tts-api.vendor-c.com` | 文字转语音 | `HttpClient.vendorCInstance()`（不 unwrap）|

切换原则：拦截器 `isOwnBusinessRequest` 判定走自有 / 三方分支；三方域**不要** unwrap data。

---

## 签名头 / 鉴权头

### 自有业务签名

- **算法**：`SHA1(body + ts + token + MD5(minute + token) + key)`
- **hex 大小写**：MD5 / SHA1 中间值与最终值 **全部大写**
- **必需 Header**：`ss`（签名值，32 字符 hex 大写）/ `tt`（毫秒时间戳）/ `token`（会话 token，登录前为空串）
- **HMOS 入口**：`SignUtil.md5()` + `SignUtil.sha1()`
- **Android 源文件**：`network/.../RequestInterceptor.kt`

### AI 图像 vendor-A 签名（AWS-style）

- **算法**：HMAC-SHA256 标准 AWS V4 流程（CanonicalRequest → StringToSign → SigningKey → Signature）
- **hex 大小写**：MD5 / 中间值**小写**
- **必需 Header**：`X-Date`（ISO 8601）/ `Authorization`（含 `Credential=AK/.../request` + `SignedHeaders` + `Signature`）/ `X-Content-Sha256` / `Host`
- **HMOS 入口**：`SignUtil.computeVendorASignature()` + `SignUtil.md5Lower()`
- **关键差异**：与自有业务 hex 大小写相反 —— SignUtil 必须分两个入口（`md5` / `md5Lower`），不要试图统一

### LLM vendor-B

- **认证**：Bearer Token（API Key 直接放 Header `Authorization: Bearer <key>`）
- **关键风险**：API Key 不能写死客户端，应走后端代理或服务端配置下发

> 详细签名字节级对账与 HMOS SignUtil 实现细节见 `arkts-network-troubleshoot` 的 Phase 1.4 + Phase 3。

---

## 公共请求参数（platformInfo）

所有自有业务接口的 body 都嵌套一个 `platformInfo` 对象（公参），多端点复用。字段表：

| 字段 | 类型 | 必需 | 说明 |
|------|------|:--:|------|
| baseType | string | 是 | 渠道大类，后端按此反查 enum |
| channel | string | 是 | 子渠道号（如 `20240101`）|
| packageName | string | 是 | Android applicationId（HMOS 侧硬覆盖到 Android 值，否则后端 enum 查不到）|
| versionName / versionCode | string / int | 是 | 应用版本 |
| androidId | string | 是 | 设备 ANDROID_ID（HMOS 无等价 API，首启 UUID 持久化）|
| oaid | string | 否 | 广告 ID |
| imei | string | 否 | HMOS 无等价，填空串 |
| brand / model / osVersion | string | 是 | 设备品牌 / 型号 / 系统版本 |
| screenW / screenH | int | 是 | 屏幕分辨率 |
| operatorName | string | 否 | 运营商，HMOS 取 SIM operator |

> 各 `apis/*.md` 的 endpoint 请求参数表里用一行 `_(公共)_ → platformInfo（见 common.md）` 引用，不重复展开。
> HMOS 实现模板见 `arkts-network-troubleshoot` 的 `references/pitfalls.md`（platformInfo 公共参数）。

---

## 响应信封

自有业务后端响应为 **双层信封**：

```json
{
  "code": 0,
  "msg": "ok",
  "data": {
    "status": 0,
    "toastMsg": "",
    "...业务字段..."
  }
}
```

- **外层** `{code, msg, data}`：HTTP 网关层（很少出现 `code != 0`）
- **内层** `{status, toastMsg, ...}`：业务层（业务码在此判定）
- **HMOS unwrap**：自有业务实例 `unwrapBaseBean=true`，抽 `data` 字段后再镜像 `status → errorCode`、`toastMsg → errorMsg`（对齐 Android `@SerializedName`）
- **三方域**：响应结构各自不同，**不要** unwrap

> 字段镜像表 `FIELD_MAP` 见 `arkts-network-troubleshoot` 的 `references/pitfalls.md` §I1（expectDataType + coerceToString）。

---

## 业务状态码

| status | 含义 | UI 处置 |
|--------|------|---------|
| 0 | 成功 | 正常处理 |
| -1001 | Token 失效 | 抛 `TokenExpiredException`，清登录态，跳登录页 |
| -2001 | 用户被封禁 | toast + 退登 |
| -500 | 服务端内部错（含字段缺失 / DB NOT NULL / enum NPE）| toast + 不重试 |
| 其他 | 业务错误 | toast `toastMsg` |

> 服务端 enum 字段映射（如 `baseType` / `channel`）需找后端要 enum 列表；本项目对应文档归档在 `spec/baseline/backend-contracts.md`。

---

## 共享响应体

### UserData（被多端点复用）

`/user/initUser`、`/user/bindMobileBySmsCode`、`/user/bindWx`、`/user/bindAli`、`/user/getInfo` 等都返回此 Bean：

| 字段 | JSON 名 | 类型 | 说明 |
|------|---------|------|------|
| errorCode | status | int | 业务码（`@SerializedName("status")`）|
| errorMsg | toastMsg | string | 错误提示（`@SerializedName("toastMsg")`）|
| token | token | string | 会话 token，未登录为空串 |
| userId | userId | long | 用户 ID（**注意**：抓包实测可能是 string，见 runtime） |
| nickName | nickName | string | 昵称 |
| avatar | avatar | string | 头像 URL |
| vipLevel | vipLevel | int | VIP 等级，0 表示未开通 |
| vipExpireTime | vipExpireTime | long | VIP 到期毫秒时间戳 |
| *（其余字段略）* | | | |

> 各 `apis/*.md` 中需要返回 `UserData` 的 endpoint 写「响应：`UserData` → 见 [common.md](common.md)」即可，不重复字段表。

### BaseBean<T>（外层信封）

| 字段 | JSON 名 | 类型 | 说明 |
|------|---------|------|------|
| errorCode | status | int | 业务码（外层 `code` 不展开到 Bean，由 HttpClient unwrap 阶段消化） |
| errorMsg | toastMsg | string | 提示 |
| data | data | `T` | 业务数据，HMOS 显式 unwrap 后即业务体 |

---

## 抓包状态标记说明

`apis/*.md` 每个 endpoint 标注 runtime 状态：

| 标记 | 含义 | 来源 |
|------|------|------|
| ⬜ static-only | `runtime` 段仍为 `null`，源码静态推断 | `android-api-inventory` 初版产出默认 |
| ✅ verified | `runtime` 已抓且与 `static` 一致 | `arkts-network-troubleshoot` Phase 0.3 抓包 + Phase 1.7 DIFF |
| ⚠️ mismatch | `runtime` 已抓且与 `static` 有差异 | 同上；差异详情就近列出 + 链到 `spec/baseline/api-contract-diff.md` |

> `api-inventory.json` 是机器可读唯一事实源，md 集是 JSON 的投影；JSON 的 `runtime`/`reconciled` 段更新后，md 标记同步刷新。
