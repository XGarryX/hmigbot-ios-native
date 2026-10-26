# spec/baseline 对账表模板（6 张通用 + 1 张鉴权专项）

> Phase 1 用。复制每一节到工程 `spec/baseline/<对应文件>.md` 填表。
> **与 API contract 的关系**：工程内有 `spec/baseline/api-inventory/api-inventory.json` 时，这 6 张表是该 endpoint-keyed contract 的「按维度投影」（派生视图）—— contract 是主存储，以它的 `static`（来自 android-api-inventory）/ `runtime`（Phase 0.3 抓包回填）/ `reconciled`（Phase 1.7 DIFF）为准，6 表从中派生即可，不要与 contract 各填一遍。无 `api-inventory.json` 时，6 表即对账主产物，照常按下文 grep 自抽。
> v1.3 增设第 7 张专项表 `auth-chain.md`（Phase 1.8）：投影 `api-inventory.json` 的 `auth_model` + `data_flows[chain=auth]`。

## 目录

1. [url-mapping.md — URL 全表对账](#1-url-mappingmd--url-全表对账)
2. [request-bodies.md — Request body 字段对账](#2-request-bodiesmd--request-body-字段对账)
3. [json-field-mapping.md — JSON 字段映射对账](#3-json-field-mappingmd--json-字段映射对账)
4. [sign-algorithms.md — 签名算法对账](#4-sign-algorithmsmd--签名算法对账)
5. [platform-info.md — 公参字段对账](#5-platform-infomd--公参字段对账)
6. [product-config.md — 构建期注入字段](#6-product-configmd--构建期注入字段)
7. [auth-chain.md — 鉴权/登录链路对账（v1.3）](#7-auth-chainmd--鉴权登录链路对账v13)

---

## 1. url-mapping.md — URL 全表对账

抽取命令：

```bash
grep -rn 'const val\s\+\w\+\s*=\s*"/' android_src --include='*.kt' | grep -v '/build/'
grep -rn '@POST("/\|@GET("/' android_src --include='*.kt' | grep -v '/build/'
grep -rn "const URL_" hmos_src/network/services --include='*.ets'
```

每个 Service 一张表（下表为**格式示例**，值替换为你项目的实际内容）：

| HMOS Service.method | Android 等价 | Android URL 来源 | Android URL 字面值 | HMOS URL 常量名 | HMOS URL 字面值 | 对账 |
|---|---|---|---|---|---|---|
| `<Service>.<methodA>` | `<Service>.<methodA>` | `<UrlObject>.<methodA>` | `/<domain>/<pathA>` | `URL_<METHOD_A>` | `/<domain>/<pathA>` | ✅ |
| `<Service>.<methodB>` | `<Service>.<methodB>` | `<UrlObject>.<methodB>` | `/<domain>/<实际服务端路径>` | `URL_<METHOD_B>` | ? | ? |

对账状态：✅ 对齐 / ⚠️ 部分对齐（注明差异）/ ❌ 未对齐 / 🟡 待 SDK/后端。

陷阱：HMOS URL 漏命名空间前缀（`/user/` `/system/` 等）/ 用客户端方法名而非服务端路径 / 接口名 ≠ URL 名（Android 接口名常与服务端实际 path 不一致，必须填服务端实际 path）。

---

## 2. request-bodies.md — Request body 字段对账

抽取命令：

```bash
grep -rn 'mutableMapOf("' android_src --include='*.kt' -A 5 | grep -v '/build/'
grep -rn 'fun\s\+\w*[Bb]ody\b' android_src --include='*.kt' -A 3 | grep -v '/build/'
```

下表为**格式示例**，值替换为你项目的实际内容：

| HMOS Service.method | Android body 字段（完整） | HMOS body 实际传 | 字段对账 | 类型对账 | 风险点 |
|---|---|---|---|---|---|
| `<Service>.<methodA>` | `{<fieldA>: String, <constField>: Int=1}` | `{<fieldA>, <constField>: 1}` | ✅ | ✅ | 别漏 `<constField>` 这种看似默认值的常量 |
| `<Service>.<methodB>` | `{<fieldA>, <fieldB>}` | `{<fieldA>, <fieldB>}` | ✅ | ✅ | — |

陷阱：漏看似无意义的常量字段（Android 工具函数里 `"source" to 1` 这种）；公参误以为拦截器自动注入；字段类型 / 拼写错；嵌套对象漏抽。

---

## 3. json-field-mapping.md — JSON 字段映射对账

抽取命令：

```bash
grep -rn '@SerializedName(' android_src --include='*.java' --include='*.kt' | grep -v '/build/'
```

下表 BaseBean 两行（`status→errorCode` / `toastMsg→errorMsg`）是绝大多数 Android 工程的通用映射；其余按你项目实际 `@SerializedName` 填：

| Bean 类 | Java/Kotlin 字段 | JSON 字段名 | ArkTS 字段名 | 镜像策略 | 镜像已实施 |
|---|---|---|---|---|---|
| BaseBean | errorCode | `status` | errorCode | HttpClient unwrap 后镜像 | ✅ |
| BaseBean | errorMsg | `toastMsg` | errorMsg | 同上 | ✅ |
| `<Bean>` | `<arktsFieldA>` | `<jsonFieldA>` | `<arktsFieldA>` | 同上 | ⏳ |
| `<Bean>` | `<arktsFieldB>` | `<jsonFieldB>` | `<arktsFieldB>` | 同上 | ⏳ |

HMOS HttpClient FIELD_MAP：

```typescript
private static FIELD_MAP: Map<string, string> = new Map([
  ['status', 'errorCode'],
  ['toastMsg', 'errorMsg'],
  ['<jsonFieldA>', '<arktsFieldA>'],
  ['<jsonFieldB>', '<arktsFieldB>'],
  // ... 每条 @SerializedName 加一行
]);
```

---

## 4. sign-algorithms.md — 签名算法对账

抽取命令：

```bash
grep -rln 'MD5_TABLE\|b2hStr\|byteToHex\|toHex' android_src --include='*.java' --include='*.kt'
grep -A 3 -B 1 "'[a-fA-F]'" $(grep -rln 'MD5_TABLE\|toHex\|b2hStr' android_src --include='*.kt' --include='*.java')
```

下表为**格式示例**（算法步骤 / hex 大小写 / 文件路径都按你项目实际填）：

| 签名链路 | 算法步骤 | 中间值 hex 大小写 | 最终编码 | Android 文件 | HMOS 入口 |
|---|---|---|---|---|---|
| 自有业务签名 | `SHA1(body+ts+token+MD5(...)+key)`（示例）| MD5/SHA1 **大写**（示例）| hex | `<自有签名实现.kt>` | `SignUtil.md5()` + `sha1()` |
| 三方厂商签名 | `base64(HmacSHA1(MD5(appId+ts), secret))`（示例）| MD5 **小写**（示例）| base64 | `<三方签名实现>` | `SignUtil.md5Lower()` + `computeVendorSignature()` |

> ⚠️ hex 大小写**必须**逐个核对 Android 实际代码的 hex 字符表（`'A'..'F'` 大写 / `'a'..'f'` 小写）。同一工程不同链路可能不同。

SignUtil 必备入口：`md5` / `md5Lower` / `sha1` / `sha1Lower` / `hmacSha1Bytes` / `computeVendorSignature` / `utf8Bytes` / `bytesToHex` / `bytesToBase64`。

约束：HMAC 用 `createSymKeyGenerator('HMAC')` 无后缀；utf8Bytes 防御性拷贝；hex 大小写不可一刀切。

---

## 5. platform-info.md — 公参字段对账

抽取命令：

```bash
grep -rln 'AppFormInfo\|PlatformInfo\|CommonParams' android_src --include='*.kt' --include='*.java' | grep -v '/build/'
```

完整字段对照表见 [phases.md Phase 1.5](../phases.md#15-公参platforminfo字段对账)。

本项目实际取值表（值替换为你项目实际）：

| 字段 | Android 取值 | HMOS 取值 | 来源/决策 |
|---|---|---|---|
| baseType | `<your_brand_type>` | 同（硬编码） | spec/baseline/product-config.md |
| channel | `<your_default_channel>` | 同（硬编码） | 同上 |
| packageName | `<com.your.android.applicationId>` | 同（硬覆盖） | spec/baseline/decisions.md |
| `<后端 enum 派生字段>` | （后端派生） | 兜底字段（如缺失后端 NPE） | 后端反查 enum |

fallback 决策记录（每个无等价 API 的字段写一段）：

```markdown
## androidId
- Android: Settings.Secure.ANDROID_ID（16 hex 字符）
- HMOS: 首启 util.generateRandomUUID(false).replace(/-/g,'') 生成 32 字符，PreferencesUtil 持久化
- 行为差异：应用清数据 / 卸载重装时变（类似 Android 8+）

## packageName
- Android applicationId: com.brand.product
- HMOS bundleName: com.example.harmony-default
- 决策：platformInfo.packageName 硬覆盖 Android applicationId
- 长期方案：（D5 三方案选一）
```

完整 PlatformInfo class 模板见 [templates/code/platform-info.ets](code/platform-info.ets)。

---

## 6. product-config.md — 构建期注入字段

抽取命令：

```bash
grep -n 'productFlavors\|manifestPlaceholders\|buildConfigField' android_src/app/build.gradle*
cat android_src/channel/product.xml
grep -A 1 '<meta-data' android_src/app/src/main/AndroidManifest.xml
```

| Android 字段 | brandA 取值 | ... | HMOS 等价位置 | HMOS 取值 | 决策 |
|---|---|---|---|---|---|
| applicationId | `com.brand.a` | ... | AppScope/app.json5 bundleName 或硬覆盖 | ? | 见 D5 |
| baseType | `brand_a` | ... | HttpInterceptor.APP_BASE_TYPE 常量 | ? | 硬编码 |
| defaultChannel | `20240101` | ... | HttpInterceptor.DEFAULT_CHANNEL 常量 | ? | 硬编码 |
| appName | "品牌 A" | ... | string.json `app_name` | ? | resources |
| weixinAppId | `wx_a` | ... | WxApiHelper.WECHAT_APP_ID 常量 | ? | — |
| weixinSecret | `secret_a` | ... | **不应在客户端** OAuth 不持 SECRET | — | 见 G2 |
| huaweiAppId | `1000xxx` | ... | AGConnect-Services.json | ? | — |

多 product 决策：单 product → 全硬编码；2-3 → build-profile.json5 buildProfileFields；多 brand → 独立 HSP 模块。

---

## 7. auth-chain.md — 鉴权/登录链路对账（v1.3）

> 事实源优先级：`api-inventory.json` 的 `auth_model` 段 > phases.md §1.8 grep 自抽。填表纪律见 [phases.md §1.8](../phases.md#18-鉴权登录链路对账v13--auth-chainmd)。

下表为**格式示例**，Android 列的值来自 `auth_model` 对应字段（或自抽证据 文件:行号）：

| # | 要素 | Android 事实 | HMOS 实现 | 对账 | 备注 / uncertainty |
|---|------|-------------|-----------|:--:|------|
| 1 | token 获取 | `POST /user/initUser`（guest）+ `POST /user/loginBySmsCode`（bound） | SplashService.initUser / LoginService.login | ✅ | 游客登录语义 = 拿回设备身份 |
| 2 | token 存储 | MMKV key `token` + `userData` | PreferencesUtil + AppStorage('userData')（V2 单一源） | ⏳ | — |
| 3 | token 注入 | HeaderInterceptor：header `token` / `ss` / `tt` | HttpInterceptor.addHeader | ⏳ | header 大小写 → U-00x（②）|
| 4 | token 失效 | `-1001`，仅 bound 态清 token 跳登录 | ResponseInterceptor 失效判定 | ⏳ | guest 态不清（D4c）|
| 5 | token 清除 | 退出登录清 `token`，**保留** `deviceNo` | UserRepository.logout | ⏳ | 别清设备级字段 |
| 6 | 身份模型 | device-bound；首绑手机号后不可回游客态 | 登录页 + 「我的」Tab 状态机 | ⏳ | 不可逆边逐条列 |

对账状态：✅ 对齐 / ⚠️ 差异（注明） / ⏳ 未实现 / 🟡 待抓包（needs_capture）/ ❌ 未对齐。

**不可逆边清单**（来自 `auth_model.irreversibles`，逐条列，防止 HMOS 侧实现出"看似合理但违反业务约束"的版本）：

- （示例）设备首次绑定手机号后，任何本端操作不回游客态
- （示例）注销后 deviceNo 标记不可用，重登可能撞「用户已注销」
