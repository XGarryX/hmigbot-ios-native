---
name: arkts-login
description: ArkTS/HarmonyOS 第三方**登录**通用集成技能（页面/组件示例采用 V2：@ComponentV2/@Local/AppStorageV2.connect/@Monitor，兼顾 V1：@Component/@State/@StorageProp 老项目对照）。覆盖微信、支付宝、华为 Account Kit 一键登录、手机号+SMS 四条路径的客户端职责与 OAuth 2.0 / OpenID Connect 协议约束，不绑定特定后端字段。**用户提到登录、授权、一键登录、账号绑定、登录 SDK 集成时务必立即触发**——含接入微信 SendAuthReq、调起支付宝授权、接华为 Account Kit、SMS 验证码倒计时、一键登录 SDK 选型（闪验/极光/阿里 PNVS/个推/华为）、Android 登录模块迁移鸿蒙等。**即使只说'加个登录'、'接微信'、'闪验怎么换鸿蒙版本'，也应触发**。**调试场景必触**：登录无回调、支付宝登录跳到支付页、华为匿名手机号为空、Account Kit 权益未生效、上架被拒未接华为账号登录、验证码发不出去、Bundle ID 校验不通过、scope 错误等。关键词：login、auth、登录、授权、一键登录、wechat-login、alipay-login、huawei-login、account-kit、闪验、极光认证、SendAuthReq、authorizationCode、cashiersdk、quickLoginAnonymousPhone、OAuth、SMS、验证码。**不适用**：纯 UI 走 arkts-component-builder；**支付/订单/IAP 走 arkts-payment**；后端接口设计本 skill 不约束。
metadata:
  type: domain
  domain: system
  tags:
  - login
  - auth
  - wechat-login
  - alipay-login
  - huawei-login
  - account-kit
  - sms
  - oauth
  - openid-connect
  - sdk
  - generic
  - third-party
---
# ArkTS 第三方登录通用集成指南

**不绑定任何特定后端/私有 lib** 的第三方**登录**集成方案，专注于 OAuth 2.0 / OpenID Connect 客户端职责边界与微信/支付宝/华为官方协议要求。

> ⚠️ **本 skill 只覆盖登录（用户身份识别 + token 签发）**，不涉及任何支付/订单/资金流场景。即使支付宝登录与支付宝支付复用同一 SDK 包（`@cashier_alipay/cashiersdk`），本文档也只描述其登录用法（`apiname=com.alipay.account.auth`）。

本文档是索引；细节模板在 `references/` 下。

## 你在登录链路里的位置（L4–L6）

本 skill 负责登录链路的 **L4 方式凭证 / L5 登录接口 / L6 存 token + 头注入**。其下的 **L0–L3（基础设施 / 隐私门控 / 请求可信化签名 / 设备身份）由 Stage 2 `arkts-network-troubleshoot` 建**，并已被 spec 期 probe 证明可打通——你坐在这个地基上，别重复实现签名/设备层。

落地前**对照本项目 `spec/baseline/api-inventory/data-chains/chain-auth.md`（数据链路契约）逐层自检**：确认 L2 签名拦截器已挂、L3 设备头有真实来源、尤其**登录成功后 token 已同步到拦截器**（本文件致命陷阱 #11：token 没同步三处 → 后续 API 401）+ 冷启后 token 能水合回来。契约的 L4–L6 行点名的 owner 就是你。

## 支付宝登录的 SDK 选择

⚠️ 支付宝登录涉及 SDK 选型，需特别说明：

- **主流路径（推荐）**：`@cashier_alipay/cashiersdk` 的 `Pay().pay(authInfo, true)`。AIImage / AIPPT 等生产项目实际用法。虽然 cashiersdk 的 README 写"不支持 auth"，但 SDK 底层通过 authInfo 里 `apiname` 字段分流：传 `apiname=com.alipay.account.auth` 会走授权通道并返回 `auth_code`。这是目前公共 ohpm 仓库唯一可用于登录的路径。
- **替代路径（私有源）**：`@alipay/afservicesdk` 的 `AFServiceCenter.call(AFServiceAuth, ...)`。接口更干净，但该包**不在公共 ohpm 仓库**（`ohpm.openharmony.cn` 查询 404），仅部分私有镜像或支付宝侧渠道可获取。详见 [03-alipay-login.md](references/03-alipay-login.md) §附录。
- **"登录拉起后显示支付 UI / 交易订单处理失败"的真实根因**：authInfo 的 `apiname` 字段错（不是 `com.alipay.account.auth` 而是支付的 `com.alipay.trade.app.pay`）或签名无效被服务端拒签，**和 SDK 选择无关**。mock 签名串（`sign=MOCK_SIGN`）必复现此错误；真机测试必须接入后端真实登录授权签名接口。

## 适用范围

**覆盖**:
- 微信登录（`SendAuthReq` + code 流程）
- 支付宝登录（`@cashier_alipay/cashiersdk` + 服务端签名 authInfo 走 `apiname=com.alipay.account.auth`；附录含 `@alipay/afservicesdk` 替代路径）
- **华为账号一键登录**（`@kit.AccountKit` + `quickLoginAnonymousPhone` scope + `AuthenticationController.executeRequest` + 服务端 `getPhoneNumber` 换明文）
- 手机号+SMS 登录的**通用骨架**（60s 验证码倒计时、防重复点击与并发）
- OAuth 2.0 authorization_code 客户端职责边界（含华为 OpenID Connect 扩展）
- 登录后的 token 三处同步、`saveThirdPartyUserData` 通用写入
- 一键登录 SDK **替换决策**（华为 Account Kit 系统原生 / 极光 JVerification / 阿里云 PNVS / 个推 GYSDK 横向比较 — 详见 [06-huawei-account-kit.md §10](references/06-huawei-account-kit.md)）

**不覆盖**:
- 具体后端 API 字段/路径 — 由项目和后端协商（见"后端契约检查清单"）
- 三大运营商官方一键登录 SDK 的直接接入（移动认证 / 联通沃认证 / 天翼认证）— 通常用聚合 SDK 包装，不直连
- 闪验 SHANYAN HarmonyOS NEXT 原生 SDK — 公开渠道未见鸿蒙版本，需联系厂商获取
- 手机号+SMS 的具体业务接口实现 — 仅覆盖通用流程

## 架构约束（硬约束）

OAuth 三层分离：

```
Page 层      — 持有 UIAbilityContext，调 wxopensdk.sendReq / new Pay().pay(authInfo)
              / new authentication.AuthenticationController(ctx).executeRequest(req)
              管理倒计时、UI 状态、前置校验
ViewModel 层 — 业务编排 + 调后端 bindWx/bindAli/bindMobile/bindHuawei + 状态写回
              singleton 实例，不持有 UI 引用
Service 层   — 纯网络调用 + 数据转换（含调 /getAliAuthUrl 拿服务端签名串）
              失败抛异常
```

**硬约束来源**：所有 SDK 入口（`wxopensdk.WXAPIFactory.createWXAPI(appid).sendReq(context, authReq)` / `new Pay().pay(...)` / `authentication.AuthenticationController(context)`）的 `context` 都必须是 `common.UIAbilityContext`。ViewModel 拿不到 → **SDK 必须在 Page 层调**。Account Kit 是 `await Promise` 形态而非异步回调，但 context 来源约束相同。

## 初始化前置（自包含）

新项目集成时必做。已做过则跳过。

### 1. `module.json5` 必备配置

```json5
{
  "module": {
    "requestPermissions": [
      { "name": "ohos.permission.INTERNET" },
      { "name": "ohos.permission.GET_NETWORK_INFO" }
    ],
    "querySchemes": [
      "weixin", "wxopensdk",      // 微信
      "alipay", "alipays"         // 支付宝
    ],
    "abilities": [{
      "name": "EntryAbility",
      "skills": [
        { "actions": ["ohos.want.action.home"], "entities": ["entity.system.home"] },
        { "actions": ["wxentity.action.open"] }   // 微信回调必需
      ]
    }]
  }
}
```

### 2. SDK 依赖

```json5
// oh-package.json5
{
  "dependencies": {
    "@tencent/wechat_open_sdk": "<check-latest>",      // 微信登录 SendAuthReq
    "@cashier_alipay/cashiersdk": "<check-latest>"     // 支付宝登录授权流
    // 本 skill 只描述登录用法：传 apiname=com.alipay.account.auth 的服务端签名串
    // 走授权通道返回 auth_code。其他 apiname 用法不属本 skill 范围。
    //
    // 替代包 @alipay/afservicesdk 不在公共 ohpm 仓库（ohpm.openharmony.cn 404），
    // 仅部分私有源 / 支付宝直接分发渠道可获取。接口更干净但可用性差，
    // 详见 references/03-alipay-login.md §附录。
  }
}
```

`build-profile.json5` 必须 `useNormalizedOHMUrl: true`（cashiersdk 强制要求）。

### 3. WXApi 单例

```typescript
// utils/WxApiHelper.ets
import * as wxopensdk from '@tencent/wechat_open_sdk'

const APP_ID = '<微信开放平台 - 移动应用 AppID>'
// ⚠️ 不是小程序 AppID
export const WXApi = wxopensdk.WXAPIFactory.createWXAPI(APP_ID)
```

### 4. EntryAbility 集成（关键）

**漏此步 → 登录回调永远不触发**。

```typescript
import { WXApi } from '../utils/WxApiHelper'
import { wxEventHandler } from '../utils/WxEventHandler'

export default class EntryAbility extends UIAbility {
  onCreate(want: Want, launchParam): void {
    // HarmonyOS 版 SDK 在 createWXAPI() 内部已完成 App 注册，
    // WXApi 接口上没有 registerApp（那是 Android SDK 的遗留方法），
    // 只需 handleWant 处理"从微信冷启动回来"的场景
    WXApi.handleWant(want, wxEventHandler)
  }
  onNewWant(want: Want, launchParam): void {
    WXApi.handleWant(want, wxEventHandler)  // 从微信跳回必走
  }
}
```

### 5. WXApiEventHandler（多订阅点）

登录可能从多个入口触发（登录页 / Mine 头部"登录"浮窗 / 拦截器触发的弹窗等），多个订阅点同时存在时必须用 Map 支持多订阅，避免后注册的覆盖前一个：

```typescript
class WxEventHandlerImpl implements wxopensdk.WXApiEventHandler {
  private respCallbacks: Map<string, (resp: wxopensdk.BaseResp) => void> = new Map()

  registerOnWXRespCallback(cb): void { this.respCallbacks.set(cb.toString(), cb) }
  unregisterOnWXRespCallback(cb): void { this.respCallbacks.delete(cb.toString()) }
  onReq(req): void { /* ... */ }
  onResp(resp): void { this.respCallbacks.forEach(cb => cb(resp)) }
}
export const wxEventHandler = new WxEventHandlerImpl()
```

> ⚠️ 若项目同时使用了微信支付 SDK，由于 SDK 共用同一个 `WXApiEventHandler` 接口分发回调，登录订阅者必须按 `resp.type === Command.kCommandSendAuth` 或 `instanceof SendAuthResp` 过滤，否则支付回调会被误当作登录响应。具体过滤代码见 [02-wechat-login.md §3](references/02-wechat-login.md)。

### 6. 开放平台与签名

- **禁用 IDE 自动签名**，用手动签名（固定证书）
- 微信开放平台：填 Bundle ID + Identifier（`bundleManager.getBundleInfoForSelf()` 的 `signatureInfo.appIdentifier`），**提交审核通过**后才能调用
- AppID 必须是**移动应用** AppID，不是小程序 AppID

审核未过期间调 `sendReq` 必报"Bundle ID 校验不通过" / "应用未注册"。

### 7. 华为 Account Kit 专属配置（仅接华为登录时）

Account Kit 是 **系统 Kit**，无需 ohpm 依赖，但必须配置以下三项：

```typescript
// 仅 import，无需注册
import { authentication } from '@kit.AccountKit'
```

1. **AGC 权益申请** — 控制台 "API 管理 → Account Kit"，申请 `quickLoginAnonymousPhone`，2025 升级后**实时审批 + 24 小时生效**
2. **混淆白名单**（项目开混淆必加）：
   ```
   # obfuscation-rules.txt
   -keep-property-name
   quickLoginAnonymousPhone
   unionID
   openID
   authorizationCode
   ```
3. **服务端 client_id / client_secret** — 来自 AGC，**绝不下发客户端**，与微信 AppSecret / 支付宝 app_private_key 同等敏感

完整接入与示例代码见 [06-huawei-account-kit.md](references/06-huawei-account-kit.md)。

## 致命陷阱清单（🔴 不处理必炸）

本章只列跨登录方式通用的致命级问题。每种登录方式的域内陷阱（scope 错、倒计时位置、saveUserData 覆盖、canOpenLink 预检、SDK 版本漂移等）见对应 reference 末尾的 "常见陷阱"：

- 微信：[02-wechat-login.md §10](references/02-wechat-login.md)
- 支付宝：[03-alipay-login.md §11](references/03-alipay-login.md)
- SMS：[04-sms-login-generic.md §8](references/04-sms-login-generic.md)
- 华为 Account Kit：[06-huawei-account-kit.md §11](references/06-huawei-account-kit.md)
- 登录后状态同步：[05-post-login-state.md §10](references/05-post-login-state.md)

### 🔴 跨登录方式致命问题

1. **客户端换 access_token / phoneNumber** — AppSecret / app_private_key / client_secret 泄漏 = 黑产可冒用任意用户。必须后端换。参见 [01-login-flows.md](references/01-login-flows.md) §2-3
2. **微信登录回调未按 `resp.type` 过滤** — 同一个 `WXApiEventHandler` 会分发所有微信 SDK 响应；项目若同时接入了其他 wxopensdk 能力（典型为微信支付的 PayResp），登录订阅者必须用 `resp.type === Command.kCommandSendAuth` 或 `instanceof SendAuthResp` 过滤，否则非授权类型的响应会被错误当作登录结果
3. **`state` 参数不设随机值**（含华为 Account Kit）— CSRF 攻击；授权链接可被中间人劫持
4. **支付宝登录只看 `resultStatus='9000'` 未看 `result_code='200'`** — 9000 只代表 SDK 调起成功，用户真正授权成功还需 result_code=200 + authCode 非空
5. **支付宝登录拉起后显示"交易订单处理失败，请稍后再试" / 显示支付 UI** — 根因是登录授权 authInfo 的 `apiname` 字段错（不是 `com.alipay.account.auth`，可能误填了支付的 `com.alipay.trade.app.pay`）或签名无效被服务端拒签，**与 SDK 选择无关**。Mock 签名串、`app_id` 未注册、证书不匹配都会触发。真机调试前必须接入后端真实**登录授权**签名接口（不是支付下单接口）；不要相信"换个 SDK 就好"的误诊。详见 [03-alipay-login.md §10-11](references/03-alipay-login.md)
6. **EntryAbility 未调 `WXApi.handleWant()`** — onResp 永远不触发，用户点登录像没反应。**登录回调不工作首查这条**
7. **AppID / Client ID 配置错** — 微信用小程序 AppID → "应用未注册"；华为用 AGC App ID 而不是 Client ID → 取号必失败
8. **IDE 自动签名** — appIdentifier 每次构建可能变 → 开放平台校验失败。必须手动签名
9. **华为账号匿名手机号永远为空** — 三大致命前提条件未满足之一：(a) 混淆未保留 `quickLoginAnonymousPhone` 属性 (b) AGC 权益申请未生效（< 24h） (c) 服务端部署在海外站点拿不到完整号码。详见 [06-huawei-account-kit.md §11](references/06-huawei-account-kit.md)
10. **上架华为应用市场被拒"未接华为账号登录"** — 应用接了第三方账号登录（微信/QQ）但没接 Account Kit。华为应用市场强制规则。详见 [06-huawei-account-kit.md §9](references/06-huawei-account-kit.md)
11. **登录后 token 没同步到 HTTP 拦截器**（不只是 Preferences）— 后续 API 仍用旧 token，接口 401。必须三处同步，详见 [05-post-login-state.md §1](references/05-post-login-state.md)
12. **登录页 sendSms / login 按钮未做并发锁与按钮 disabled** — 用户连点导致重复提交 / 倒计时未启动就发第二次。每个网络请求前都要检查 `isLoading` 标志位与按钮 enabled 态，详见 [04-sms-login-generic.md §2](references/04-sms-login-generic.md)

## 四条登录路径

| 路径 | 场景 | 核心约束 | 详细文档 |
|---|---|---|---|
| A | 微信登录 | SendAuthReq + `scope='snsapi_userinfo'` + `state` 防 CSRF + code 送后端 | [02-wechat-login.md](references/02-wechat-login.md) |
| B | 支付宝登录 | 服务端签名 authInfo（含 `apiname=com.alipay.account.auth`）→ `new Pay().pay(authInfo, true)` → 双校验 `resultStatus=9000` + `result_code=200` + `auth_code` 非空 → 送后端换业务 token | [03-alipay-login.md](references/03-alipay-login.md) |
| C | SMS 登录（通用骨架）| 60s 验证码倒计时由 Page 管理 + 发送成功才启动 + 防重复点击与并发 | [04-sms-login-generic.md](references/04-sms-login-generic.md) |
| D | 华为账号一键登录 | `@kit.AccountKit` + `quickLoginAnonymousPhone` scope + AGC 权益生效 + 混淆白名单 + `authorizationCode` 送后端 → 服务端 `getPhoneNumber` 换明文手机号 + UnionID | [06-huawei-account-kit.md](references/06-huawei-account-kit.md) |

**路径选型规则（以用户选择为准）**：

本 skill **不替用户做选型决策**。当需要确定接哪条/哪几条路径时，按以下优先级获取：

1. **用户直接说明** — 用户明确指定"接微信 + SMS"、"只用华为一键登录"、"按 Android 端原方案 1:1 复刻"等指令，**严格按用户指令执行**
2. **用户给定的参考源码仓** — 用户提供 Android / iOS / 其他平台已有项目作为参考时，**按源码仓现有方案对应迁移**：
   - Android 用了闪验 SHANYAN → 鸿蒙端按 D-4 决策（华为 Account Kit / 三方鸿蒙版 SDK 替换，见 [06 §10](references/06-huawei-account-kit.md)）
   - Android 用了微信开放平台 SDK → 鸿蒙端用 `@tencent/wechat_open_sdk`（路径 A）
   - Android 用了支付宝授权 → 鸿蒙端用 `@cashier_alipay/cashiersdk`（路径 B）
   - Android 用了短信验证码登录 → 鸿蒙端用路径 C
3. **用户未指明** — **主动询问用户**，列出 A/B/C/D 四条路径与上架强制规则等约束，让用户拍板，**不替用户预设选择**

> ⚠️ 即使有华为应用市场上架强制规则、无华为账号兜底等"行业最佳实践"，也仅作为**询问时的提示信息**展示给用户，**不能作为默认选型理由直接落地**。

## OAuth 2.0 客户端职责边界（核心原则）

> 客户端只拿 code / authCode / authorizationCode，**绝不能在客户端换 access_token / phoneNumber**

OAuth 2.0 `authorization_code` 模式的职责分离（华为 Account Kit 走 OpenID Connect，但边界完全相同）：

| 步骤 | 客户端 | 后端 |
|---|---|---|
| 1. 发起授权 | ✅ SDK 调起（sendReq / Pay().pay() / executeRequest） | — |
| 2. 拿临时凭证 | ✅ 回调或 await 拿 code / authCode / authorizationCode | — |
| 3. 换 access_token / phoneNumber | ❌ **绝对不能** | ✅ 用 AppSecret / app_private_key / client_secret 换 |
| 4. 拿用户信息 | ❌ | ✅ 用 access_token 查 |
| 5. 签发业务 token | ❌ | ✅ 生成自家登录态 token |
| 6. 持久化登录态 | ✅ 存 token | — |

AppSecret / client_secret 泄漏 = 黑产可冒用任意用户。详细原理见 [01-login-flows.md](references/01-login-flows.md)。

> **Account Kit 特例说明**：客户端可以拿到**匿名手机号**（如 `138****8888`，仅用于授权页 UI 展示），但**完整明文手机号**仍只能由服务端调华为云 `getPhoneNumber` 接口换取，与上述边界一致。

## 登录后状态同步

**token 三处同步**（项目侧通用模式）：

```typescript
// 一次登录成功，token 同步三处
await UserPreferences.setToken(token)            // 持久化
AppStorage.setOrCreate('token', token)           // 内存共享（给拦截器）
<lib_network>.UserData.getInstance().token = token  // 给 lib 内拦截器（如项目有）
AppStorage.setOrCreate('loginStateVersion', Date.now())  // 版本号驱动 UI 刷新
```

**三方登录数据通用写入**：`saveThirdPartyUserData(userData)` 集中处理多个三方登录的响应——空值兜底，避免覆盖本地已有数据。详见 [05-post-login-state.md](references/05-post-login-state.md)。

**logout 正确流程**：
```typescript
await api.logout()
await UserPreferences.clearUserSession()
AppStorage.setOrCreate('loginStateVersion', Date.now())
// 注：注销后是否需要重新初始化匿名/游客身份属于业务设计，
//    本 skill 不约束，由项目自身决定。
```

## 前置校验

登录按钮 onClick 第一步：

```typescript
if (!this.isPrivacyChecked) {
  promptAction.showToast({ message: '请先阅读并同意服务条款和隐私协议' })
  return
}
if (this.isLoading) return  // 防连点
```

协议勾选是监管要求（个人信息保护法）。

## 后端契约检查清单

本 skill 不绑定后端。集成前请向后端确认：

| 项 | 示例 | 必确认 |
|---|---|---|
| 微信登录接口路径 | `/user/bindWx` | 入参：`code`；响应：业务 token + 用户信息 |
| 支付宝登录接口路径 | `/user/bindAli` | 入参：`authCode`；响应：同上 |
| **华为账号登录接口路径** | `/user/loginByHuawei` | 入参：`authorizationCode`；后端调华为云 `getPhoneNumber` 拿明文手机号 + UnionID；响应：业务 token + 用户信息 |
| **华为云 client_id / client_secret** | AGC 控制台获取 | **绝不下发客户端**；服务端必须中国境内部署 |
| SMS 发送接口 | `/sms/send` | 入参：手机号；响应：成功/失败 |
| SMS 登录接口 | `/user/bindMobileBySmsCode` | 入参：`mobile` + `smsCode` |
| 支付宝 authInfo 预签名接口 | `/user/getAliAuthUrl` 或 `/system/aliAuthUrl` | 响应：已由后端 `app_private_key` RSA2 签名的 authInfo 字符串（含 `apiname=com.alipay.account.auth`），客户端原样送 `Pay().pay()` |
| logout 接口 | `/user/logout` | 仅后端 session 清理；本地清除/重建身份的策略由项目自行决定 |
| 响应用户信息字段 | `token / userId / vipLevel / nickName / avatar / phoneAuth / userState / unionID（华为）` | 字段名对齐 |
| 成功判定 | `status === 0` / `code === 'OK'` | 响应判断 |

## 调试指引

| 症状 | 首查位置 |
|---|---|
| 微信登录 `onResp` 不触发 | §初始化前置 §4 (EntryAbility `handleWant`) |
| "Bundle ID 校验不通过" / "应用未注册" | §初始化前置 §6 (手动签名 + 审核) |
| 微信登录 scope 错误 | [02-wechat-login.md](references/02-wechat-login.md) §3 |
| **支付宝登录拉起后显示"交易订单处理失败，请稍后再试"** | [03-alipay-login.md](references/03-alipay-login.md) §10 (登录授权 authInfo 的 apiname/签名校验) — 不是 SDK 选错，是登录授权签名串无效 |
| 支付宝登录 `auth_code` 为空 | [03-alipay-login.md](references/03-alipay-login.md) §5 (result 解析) |
| 验证码倒计时未启动 / 重复发送 | [04-sms-login-generic.md](references/04-sms-login-generic.md) §2 (倒计时只在发送成功回调里启动 + 防并发) |
| 登录成功但后续 API 401 | [05-post-login-state.md](references/05-post-login-state.md) §1 (token 三处同步) |
| 登录后其他页面 UI 未刷新 | [05-post-login-state.md](references/05-post-login-state.md) §4 (loginStateVersion) |
| 微信登录回调收到非授权响应（项目同时接了其他 wxopensdk 能力时）| [02-wechat-login.md](references/02-wechat-login.md) §4 (按 resp.type 过滤 SendAuthResp) |
| **华为一键登录匿名手机号永远为空** | [06-huawei-account-kit.md](references/06-huawei-account-kit.md) §11（混淆白名单 / 24h 权益生效 / 海外账号） |
| `executeRequest` 报"权益未生效" | [06-huawei-account-kit.md](references/06-huawei-account-kit.md) §3（AGC 权益申请） |
| 华为账号登录后服务端拿不到 phoneNumber | [06-huawei-account-kit.md](references/06-huawei-account-kit.md) §6（服务端必须中国境内部署） |
| 上架华为应用市场被拒"未接华为账号登录" | [06-huawei-account-kit.md](references/06-huawei-account-kit.md) §9（强制规则三条件判定） |
| 一键登录 SDK 横向选型困惑 | [06-huawei-account-kit.md](references/06-huawei-account-kit.md) §10（决策矩阵）|

## Reference 索引

- [01-login-flows.md](references/01-login-flows.md) — OAuth 2.0 通用登录流程、客户端职责边界、authorization_code 时序图
- [02-wechat-login.md](references/02-wechat-login.md) — `SendAuthReq` 完整规格、按 `resp.type` 过滤非登录类响应、错误码速查
- [03-alipay-login.md](references/03-alipay-login.md) — `@cashier_alipay/cashiersdk` 登录用法（`apiname=com.alipay.account.auth`）+ 服务端签名 authInfo 主流路径、登录拉起异常根因分析、附录：afservicesdk 替代路径（私有源）
- [04-sms-login-generic.md](references/04-sms-login-generic.md) — 60s 验证码倒计时模式、防重复点击与并发锁
- [05-post-login-state.md](references/05-post-login-state.md) — token 三处同步、通用数据写入、logout 正确流程
- [06-huawei-account-kit.md](references/06-huawei-account-kit.md) — 华为账号一键登录（@kit.AccountKit + quickLoginAnonymousPhone）、AGC 权益审批、客户端代码模板、服务端 getPhoneNumber、错误码、上架强制规则、与三方 SDK 选型对比


---

## See Also

- [arkts-payment](../arkts-payment/SKILL.md) — 同属第三方 SDK 系列（共享 wxopensdk EventHandler 过滤模式）
- [arkts-customer-service](../arkts-customer-service/SKILL.md) / [arkts-ad](../arkts-ad/SKILL.md) — 同系列
