# user 接口（UserApiService）   ← 分层形态下的模块文件骨架

> 模块：network / 文件：`network/src/main/java/com/example/app/network/api/UserApiService.kt` / 端点数：12 / 通道：自有业务
> 公共约定（信封 / 签名 / 公参 / 业务码 / 共享 Bean）见 [../common.md](../common.md)
>
> 本文件展示**单个模块文件该长什么样**：保留端点速览表 + 1 个 endpoint 完整展开 + 第 2 个 endpoint 含 mismatch 演示。
> 真实产出会把 12 个 endpoint 全部按统一模板展开。

---

## 端点速览

| # | 方法名 | HTTP | 路径 | 接口名 | runtime |
|:-:|--------|:-:|------|------|:-:|
| 1 | initUser | POST | `/user/initUser` | 初始化用户会话 | ⚠️ mismatch |
| 2 | bindMobile | POST | `/user/bindMobileBySmsCode` | 手机号 + 短信验证码绑定 / 登录 | ⬜ static-only |
| 3 | bindWx | POST | `/user/bindWx` | 微信 OAuth 绑定 / 登录 | ⬜ static-only |
| 4 | bindAli | POST | `/user/bindAli` | 支付宝绑定 / 登录 | ⬜ static-only |
| 5 | bindHonor | POST | `/user/bindHonor` | 荣耀账号绑定 / 登录 | ⬜ static-only |
| 6 | bindHuawei | POST | `/user/bindHuawei` | 华为账号绑定 / 登录 | ⬜ static-only |
| 7 | bindMobileByToken | POST | `/user/bindMobileByToken` | Token 直绑手机号 | ⬜ static-only |
| 8 | getInfo | POST | `/user/getInfo` | 拉取当前用户信息 | ⬜ static-only |
| 9 | closeAccount | POST | `/user/closeAccount` | 注销账号 | ⬜ static-only |
| 10 | logout | POST | `/user/logout` | 退出登录 | ⬜ static-only |
| 11 | getPackageList | POST | `/user/getPackageList` | 拉取已安装包列表上报 | ⬜ static-only |
| 12 | uploadAppList | POST | `/user/uploadAppList` | 安装包列表批量上报 | ⬜ static-only |

> **认证统一为**：Token 注入 + 自定义签名 (ss / tt Header) via `RequestInterceptor`（见 [common.md §签名头/鉴权头 §自有业务签名](../common.md#自有业务签名)）。下面 endpoint 详情不再重复。

---

## 1. initUser — 初始化用户会话（设备信息 + token 获取）

- **方法**：`POST /user/initUser`（REST）
- **Service**：`UserApiService.initUser`（`network/.../UserApiService.kt`:16）
- **认证**：自有业务签名 + Token → 见 [common.md](../common.md#自有业务签名)
- **runtime**：⚠️ **mismatch** — 抓包发现外层信封与字段类型与源码 Bean 不一致，详见下方「runtime 差异」
- **特殊标注**：无

### 请求参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|:--:|------|
| body | `RequestBody`（JSON） | 是 | 由 `UserRepository.initUser()` 构造，含 `deviceId` / `channel` / `androidId` / `oaid` / `platformInfo` |
| _(公共)_ | — | — | + `platformInfo` 公参对象 → 见 [common.md](../common.md#公共请求参数platforminfo) |

### 响应参数：`UserData`

完整字段表见 [common.md §UserData](../common.md#userdata被多端点复用)。本接口实际返回的关键字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| errorCode（← `status`） | int | 业务码，0 成功 |
| token | string | 会话 token，本接口产出，后续所有自有业务请求带它 |
| userId | long ⚠️ | **抓包实测为 string**，详见 runtime 差异 |
| nickName / avatar / vipLevel / vipExpireTime | — | → 见 [common.md §UserData](../common.md#userdata被多端点复用)|

### runtime 差异（reconciled.status: mismatch）

抓包时间：2026-04-16 09:20:11（方法 C 代理抓包）

| 维度 | static（源码推断） | runtime（实测） | 对 HMOS 实现的影响 |
|------|-------------------|----------------|---------------------|
| response-wrapper | 源码 Bean 按扁平结构反序列化 | 实测有 `{code, msg, data}` 外壳，业务体在 `data` | HMOS HttpClient 必须显式 unwrap data，源码推不出这一层（见 [common.md §响应信封](../common.md#响应信封)）|
| field-type (`userId`) | 声明为 `long` | 真实 JSON `userId` 是 string（`"1000000123"`）| HMOS Bean `userId` 用 string，勿用 number；判定登录态时按字符串非空判 |

> 完整 mismatch 清单（含其他 endpoint）见 `spec/baseline/api-contract-diff.md`。

---

## 2. bindMobile — 手机号 + 短信验证码绑定 / 登录

- **方法**：`POST /user/bindMobileBySmsCode`（REST）
- **Service**：`UserApiService.bindMobile`（`network/.../UserApiService.kt`:28）
- **认证**：自有业务签名 + Token → 见 [common.md](../common.md#自有业务签名)
- **runtime**：⬜ **static-only**（未抓真包，源码推断）
- **特殊标注**：⚠️ **方法名 ≠ 服务端路径** —— Android 方法名简写为 `bindMobile`，服务端实际 path 为 `/user/bindMobileBySmsCode`。HMOS URL 常量必须填服务端实际 path，不能用方法名（见 [common.md 网络层架构摘要 / pitfalls D2](../api-inventory.md#网络层架构摘要)）

### 请求参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|:--:|------|
| body | `RequestBody`（JSON） | 是 | `{ mobile: string, smsCode: string }` + `platformInfo` |
| _(公共)_ | — | — | + `platformInfo` 公参对象 → 见 [common.md](../common.md#公共请求参数platforminfo) |

### 响应参数：`UserData`

→ 见 [common.md §UserData](../common.md#userdata被多端点复用)（与 initUser 同 Bean）。

---

*（其余 10 个 endpoint：bindWx / bindAli / bindHonor / bindHuawei / bindMobileByToken / getInfo / closeAccount / logout / getPackageList / uploadAppList —— 真实产出按相同统一模板展开。请求体字段不同，但响应大多为 `UserData` 或 `BaseBean<Void>`，仅个别接口有差异字段需在此单独展开。）*

---

## 这个模块文件展示了什么

1. **端点速览表** — 一眼看全模块多少 endpoint、各自 runtime 状态
2. **统一展开模板** — 方法 / Service / 认证（链 common）/ runtime 标记 / 特殊标注 / 请求表 / 响应表
3. **响应强制表格化** — 即使是共享 Bean，也要在 endpoint 里列出关键字段 + 链 common.md（不省略响应段）
4. **runtime mismatch 就近披露** —  `initUser` 演示了 ⚠️ 标记 + 差异表 + 链向 `api-contract-diff.md` 的写法
5. **「合并一类」** — 认证、公参、共享 Bean、业务码 都在 [common.md](../common.md) 写一次，本文件用链接引用，不重复展开
