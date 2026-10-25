# 支付宝登录 SDK 深入细节

支付宝登录在 HarmonyOS 上有两条可行路径。本文档先讲**主流路径**（`@cashier_alipay/cashiersdk` + 服务端签名 authInfo，AIImage / AIPPT 等生产项目实证），末尾附录讲**替代路径**（`@alipay/afservicesdk`，私有 ohpm 源可用时）。

## 1. SDK 选择

| 路径 | 包 | 核心 API | 可获取性 | 生产验证 |
|---|---|---|---|---|
| **主流（推荐）** | `@cashier_alipay/cashiersdk` | `new Pay().pay(authInfo, true)` | ✅ 公共 ohpm (`ohpm.openharmony.cn`) | AIImage、AIPPT |
| 替代 | `@alipay/afservicesdk` | `AFServiceCenter.call(AFServiceAuth, params)` | ⚠️ 公共 ohpm 404；仅私有源 / 支付宝侧渠道 | 文档上更干净，社区案例少 |

### 为什么 cashiersdk 也能做登录？

虽然 cashiersdk 的 README 写"不支持 auth"，但 SDK 底层通过 authInfo 里的 `apiname` 字段分流：

```
apiname=com.alipay.trade.app.pay     → 走支付流程  → 返回订单结果
apiname=com.alipay.account.auth      → 走授权流程  → 返回 auth_code
```

只要**服务端用 `app_private_key` 正确签名 `apiname=com.alipay.account.auth` 的 authInfo**，SDK 会调起授权页而非支付页。这是 AIImage `LoginPage.ets`、AIPPT `LoginPage.ets` 的生产用法——注释原话："HarmonyOS cashier SDK 的 Pay.pay() 底层同样走 Alipay 协议通道，传入 authInfo 时执行授权流程（而非支付）"。

### ⚠️ 常见误诊：跳到支付页 / "交易订单处理失败"

**错误归因**："cashiersdk 不能做登录，跳到支付页了，要换 afservicesdk"

**真实根因**（按概率从高到低）：
1. **authInfo 签名无效** — `sign` 字段是测试/mock 串、服务端签名算法错（必须 RSA2）、证书和开放平台注册的不匹配
2. **`app_id` 未在开放平台注册** 或 填错（小程序 AppID 混淆）
3. **authInfo 缺 `apiname=com.alipay.account.auth`** — 客户端拼 authInfo（不应这么做，必须后端签），漏了 apiname
4. **bundle id / 签名证书 / 开放平台 Identifier 三者未对齐** — 调起时底层校验失败，支付宝 App 显示通用错误

换成 afservicesdk 不会解决上述任何一条；问题根源在签名 & 配置，不是 SDK 选型。

## 2. 主流路径：cashiersdk + 服务端签名 authInfo

### 2.1 安装

```json5
// oh-package.json5
{
  "dependencies": {
    "@cashier_alipay/cashiersdk": "<check-latest>"  // 如 ^15.8.39
  }
}
```

`build-profile.json5` 必须：

```json5
{
  "app": {
    "products": [{
      "name": "default",
      "useNormalizedOHMUrl": true   // cashiersdk 强制要求，否则编译报错
    }]
  }
}
```

### 2.2 authInfo 格式（服务端生成，客户端原样送 SDK）

URL query string，关键字段：

```
apiname=com.alipay.account.auth
&method=alipay.open.auth.sdk.code.get
&app_id=<开放平台移动应用 AppID>
&pid=<合作伙伴 PID，16 位 2088 开头>
&product_id=APP_FAST_LOGIN
&scope=kuaijie
&target_id=<随机防重放>
&sign_type=RSA2
&sign=<服务端用 app_private_key 签名>
&timestamp=<时间戳>
```

**`apiname=com.alipay.account.auth` 是授权流与支付流的分水岭** —— 服务端生成时必须写这个值。

### 2.3 Page 层调起模板

```typescript
import { Pay } from '@cashier_alipay/cashiersdk'
import { promptAction } from '@kit.ArkUI'

private async launchAlipayAuth(): Promise<void> {
  if (!this.isPrivacyChecked) {
    promptAction.showToast({ message: '请先阅读并同意协议' })
    return
  }
  if (this.isLoading) return
  this.isLoading = true

  // Step 1: 从服务端获取已签名的 authInfo
  let authInfo: string = ''
  try {
    authInfo = await <api.getAliAuthUrl()>   // 后端接口，如 /system/aliAuthUrl
  } catch (e) {
    promptAction.showToast({ message: '支付宝登录失败' })
    this.isLoading = false
    return
  }
  if (authInfo.length === 0) {
    promptAction.showToast({ message: '支付宝登录失败' })
    this.isLoading = false
    return
  }

  // Step 2: 调起 SDK
  try {
    const result: Map<string, string> = await new Pay().pay(authInfo, true)
    await this.handleAlipayAuthResult(result)
  } catch (e) {
    promptAction.showToast({ message: '支付宝登录失败' })
  } finally {
    this.isLoading = false
  }
}
```

**注意**：`new Pay().pay()` 在 ArkTS 里**不需要 UIAbilityContext**（与微信 SDK 不同），理论上可放 ViewModel，但为架构一致性建议也在 Page 层调。

## 3. 返回值解析（关键细节）

`Pay().pay(authInfo, showLoading)` 返回 `Map<string, string>`。

### 3.1 第一层：resultStatus

和支付场景一致：

| resultStatus | 含义 | 处理 |
|---|---|---|
| `'9000'` | SDK 调起成功 | 继续解析 result 字段 |
| `'6001'` | 用户取消 | 提示"已取消"，不重试 |
| `'8000'` / `'6004'` | 处理中 | 登录场景一般当作失败处理；重试需用户再点击 |
| `'4000'` | 失败 | 提示失败 |
| 其他 | 其他错误 | 提示失败 |

**注意**：`resultStatus === '9000'` 只代表 **SDK 调起成功**，不代表授权成功。真正授权成功还要看 result 里的 `result_code`。

### 3.2 第二层：result 字段解析

```typescript
private async handleAlipayAuthResult(result: Map<string, string>): Promise<void> {
  const resultStatus = result.get('resultStatus') ?? ''
  const resultStr = result.get('result') ?? ''

  if (resultStatus === '6001') {
    promptAction.showToast({ message: '已取消支付宝登录' })
    return
  }
  if (resultStatus !== '9000') {
    promptAction.showToast({ message: '支付宝登录失败' })
    return
  }

  // resultStatus = 9000 → 继续解析 result 字段
  // result 格式: "auth_code=xxx&result_code=200&..."
  let authCode = ''
  let resultCode = ''
  for (const pair of resultStr.split('&')) {
    const eqIdx = pair.indexOf('=')
    if (eqIdx <= 0) continue
    const k = pair.substring(0, eqIdx)
    const v = pair.substring(eqIdx + 1)
    if (k === 'auth_code') authCode = v
    else if (k === 'result_code') resultCode = v
  }

  // ⚠️ 双校验：result_code='200' 且 auth_code 非空
  if (resultCode === '200' && authCode.length > 0) {
    await this.performAlipayLogin(authCode)
  } else {
    promptAction.showToast({ message: '支付宝授权失败' })
  }
}
```

### 3.3 result_code 对照

| result_code | 含义 |
|---|---|
| `200` | 授权成功 |
| `1005` | 账号被冻结 |
| `202` | 系统异常，可重试 |
| `11000` | 授权取消 |
| 其他 | 见支付宝文档 |

**硬约束**：`resultStatus === '9000'` **AND** `result_code === '200'` **AND** `auth_code` 非空 —— 三者同时满足才算成功。

### 3.4 常见错误对照

```typescript
// ❌ 只判 resultStatus
if (resultStatus === '9000') {
  sendToBackend(authCode)  // authCode 可能为空
}

// ❌ 没判 result_code
if (resultStatus === '9000' && authCode.length > 0) {
  sendToBackend(authCode)  // result_code 可能非 200，authCode 是脏数据
}

// ✅ 正确
if (resultStatus === '9000' && resultCode === '200' && authCode.length > 0) {
  sendToBackend(authCode)
}
```

## 4. 把 authCode 送后端

```typescript
private async performAlipayLogin(authCode: string): Promise<void> {
  this.isLoading = true
  try {
    const ok = await this.loginVm.loginByAlipay(authCode)
    if (ok) {
      promptAction.showToast({ message: '登录成功' })
      this.pathStack.pop()
    }
  } finally {
    this.isLoading = false
  }
}
```

ViewModel 里：

```typescript
async loginByAlipay(authCode: string): Promise<boolean> {
  try {
    const userData = await this.api.bindAli(authCode)
    await this.saveThirdPartyUserData(userData)  // 详见 05-post-login-state.md
    return true
  } catch (e) {
    this.errorMessage = (e instanceof Error) ? e.message : '支付宝登录失败'
    return false
  }
}
```

**关键**：客户端只送 `authCode`，**不换 access_token**。后端用 `app_private_key` 调 `alipay.system.oauth.token` 换 `access_token` + `user_id`，再签发业务 token 下发。详见 [01-login-flows.md](01-login-flows.md) §2-3。

## 5. 预检安装（可选）

```typescript
import { bundleManager } from '@kit.AbilityKit'

function isAlipayInstalled(): boolean {
  try {
    return bundleManager.canOpenLink('alipays://')
  } catch (e) {
    return false
  }
}
```

要求 `module.json5` 已声明 `querySchemes: ["alipay", "alipays"]`。SDK 内部对未安装支付宝 App 有兜底（走 H5 登录），所以预检非强制，但给用户明确提示"请先安装支付宝 App"则需要。

## 6. 共用 SDK 做支付 + 登录

项目同时做登录 + 支付时，两者都用 cashiersdk 的 `new Pay().pay(...)`；通过传入的 authInfo / orderInfo 的 `apiname` 字段分流。严格按场景区分方法名，不要混用：

```typescript
class LoginVM {
  async launchLogin(authInfo: string): Promise<Map<string, string>> {
    return await new Pay().pay(authInfo, true)  // authInfo 的 apiname=com.alipay.account.auth
  }
}

class PaymentVM {
  async launchPay(orderInfo: string): Promise<Map<string, string>> {
    return await new Pay().pay(orderInfo, true)  // orderInfo 的 apiname=com.alipay.trade.app.pay
  }
}
```

SDK 是无状态的 API，两个调用互不影响。

## 7. 后端职责（硬约束）

**客户端绝不能**：
- 用 `app_private_key` 自己签名 authInfo
- 调 `alipay.system.oauth.token` 换 access_token
- 存 access_token / user_id

**后端正确流程**：
1. 收到客户端的 `authCode`
2. 构造 `alipay.system.oauth.token` 请求（`grant_type=authorization_code&code=<authCode>`）
3. 用 `app_private_key` RSA2 签名，发 `https://openapi.alipay.com/gateway.do`
4. 拿 `access_token` + `user_id` + `refresh_token`
5. （可选）用 access_token 查 `alipay.user.info.share` 获取用户信息
6. 签发业务 token，和业务 userId 绑定
7. 业务 token + 用户信息下发客户端

详细原理见 [01-login-flows.md](01-login-flows.md) §2。

## 8. 安装陷阱排查

### 陷阱 1：`useNormalizedOHMUrl` 未开启

```
hvigor ERROR: Bytecode HARs: [@cashier_alipay/cashiersdk] not supported
when useNormalizedOHMUrl is not true
```

**解法**：项目级 `build-profile.json5` 加 `useNormalizedOHMUrl: true`。

### 陷阱 2：间接依赖下载失败

```
missing: @alipay/blueshieldsdk, required by @cashier_alipay/cashiersdk
ENOENT: ... utdid_sdk-*.har
```

**解法**（按成本从低到高）：
1. 删除 `oh-package-lock.json5`，重新 `ohpm install`
2. DevEco Studio `File → Invalidate caches` 全清后重启
3. 手动 `ohpm install @alipay/blueshieldsdk`

### 陷阱 3：Release 模式不能拉起

DevEco Studio 早期版本混淆对 cashiersdk 不友好 → 切 Release 后跳不过去。升级 DevEco 或加 keep 规则。

## 9. 模拟器调试限制

真机测试是唯一可靠方式。模拟器没装支付宝时 SDK 会走 H5 兜底，UI 表现和真机有差异。

## 10. "交易订单处理失败，请稍后再试" 深度排查

这是本 skill **最常被误诊**的症状。按下列顺序排查：

### 第一步：确认不是 SDK 选错

- ✅ 确认用的是 cashiersdk 的 `new Pay().pay(authInfo, true)`
- ❌ 如果先前因为这个错误换到 afservicesdk，**先换回 cashiersdk**，继续下一步

### 第二步：抓 authInfo 内容

打印 `authInfo` 字符串，逐字段核对：

| 字段 | 常见错误 |
|---|---|
| `apiname` | 应为 `com.alipay.account.auth`；任何其他值都会走到错误流程 |
| `app_id` | 必须是支付宝开放平台**"移动应用"**的 APPID；小程序 AppID / 网页应用 AppID 都不行 |
| `pid` | 16 位 2088 开头纯数字；0 或空值直接拒 |
| `sign` | 不能是 "MOCK_SIGN" / "TEST" / 空 / 占位值 |
| `sign_type` | 当前支付宝普遍要求 `RSA2`，`RSA` 部分 App 已拒 |
| `timestamp` | 与服务器时间相差超过 15 分钟会拒 |

**最常见**：demo/mock authInfo 带假 sign → 支付宝服务端验签失败 → App 显示"交易订单处理失败"。**必须接入后端真实签名接口**。

### 第三步：开放平台对齐

| 项 | 值 | 校对位置 |
|---|---|---|
| Bundle ID | `AppScope/app.json5` 的 `bundleName` | 支付宝开放平台"移动应用"页面 Bundle ID 字段 |
| 签名证书 | 项目 `build-profile.json5` 手动签名证书 | 开放平台的签名指纹 / appIdentifier 字段 |
| App ID | `getAliAuthInfo()` 返回的 authInfo 里的 `app_id` | 开放平台应用 ID |

任一项错配都可能导致服务端拒。改了包名或证书后必须**重新提交开放平台审核**。

### 第四步：网络抓包（仅开发环境）

服务端生成 authInfo 时，自己调 `alipay.system.oauth.token` 测试能否拿到 access_token。服务端都拿不到，客户端必然也拿不到。

### 第五步：同样 authInfo 换 Web 端测试

把 authInfo 放到浏览器访问 `https://authweb.alipay.com/auth?...`（需稍作改写）。如果 Web 端也拒，问题在后端签名；Web 端能通但 App 端不通，问题在 Bundle ID / 签名证书对齐。

## 11. 常见陷阱总表

| 现象 | 根因 | 解法 |
|---|---|---|
| **"交易订单处理失败，请稍后再试"** | authInfo sign 无效 / app_id 错 / bundle 不匹配 | §10 五步排查；**不要**换 SDK |
| 调起后进入支付页而非授权页 | authInfo 的 `apiname` 不是 `com.alipay.account.auth` | 后端生成时改 apiname |
| `authCode` 为空但 `resultStatus=9000` | 漏判 `result_code` | §3.4 双校验 |
| `resultStatus=6001` 被当失败处理 | 未单独分支"用户取消" | §3.1 分别处理 |
| `resultStatus=4000` | 授权系统异常 | 抓 memo 字段；服务端/后端排查 |
| `authCode` 送后端换不到 access_token | authCode 一次性已用 或 过期（10 分钟）| 拿到立即送，不缓存、不重放 |
| authInfo 里字段特殊字符传输失败 | 未 URL 编码 | 后端生成时统一 URL 编码 |
| release 模式不能拉起支付宝 | DevEco 混淆激进 | 升级或加 keep 规则 |

## 12. 安全性小结

- `authCode` 一次性、10 分钟有效 — 拿到立即送后端，不重试
- `app_private_key` 只在后端，客户端**绝不**接触
- 客户端持的是业务 token（后端签发），不是支付宝 access_token
- mock / demo authInfo 绝对不要留到生产版本（容易忘记替换）

---

## 附录 A：替代路径 — `@alipay/afservicesdk`

> ⚠️ **现状**：截至本文档更新时，`@alipay/afservicesdk` **不在公共 ohpm 仓库** —— `ohpm install` 会报 404：
> ```
> GET https://ohpm.openharmony.cn/ohpm/@alipay/afservicesdk → 404
> NOTFOUND package '@alipay/afservicesdk' not found from all the registries
> ```
> 仅部分私有源 / 支付宝直接分发渠道可用。如果你没有私有源访问权限，直接用主流路径（§2-7）。

### A.1 API 差异

afservicesdk 接口更语义化，不需要服务端签名：

```typescript
import {
  AFServiceParams, AFWantParams, AFServiceCenter,
  AFAuthServiceResponse, AFService
} from '@alipay/afservicesdk'

const ALIPAY_APP_ID = '<开放平台移动应用 AppID>'
const state = `login_${Date.now()}_${Math.random().toString(36).substring(2, 10)}`

// 客户端直接构造授权 URL（纯鉴权模式）
const authUrl = `https://authweb.alipay.com/auth?auth_type=PURE_OAUTH_SDK` +
  `&app_id=${ALIPAY_APP_ID}&scope=auth_user&state=${state}`

const bizParams = new Map<string, string>()
bizParams.set('url', encodeURIComponent(authUrl))

const backWant: AFWantParams = {
  bundleName: '<bundleName>',
  moduleName: 'entry',
  abilityName: 'EntryAbility'
}

const params = new AFServiceParams(
  bizParams,
  false,      // sandbox — HarmonyOS 版不支持，必须 false
  true,       // 使用 SDK 鉴权
  'AliPay',
  backWant,
  (response: AFAuthServiceResponse): void => {
    const parameters = response.result?.['parameters'] as Record<string, string> | undefined
    if (!parameters) return
    const authCode = (parameters['auth_code'] ?? '').toString()
    const respState = (parameters['state'] ?? '').toString()
    if (respState && respState !== state) return  // CSRF 校验
    if (authCode.length === 0) return
    sendToBackend(authCode)
  }
)

AFServiceCenter.call(AFService.AFServiceAuth, params)
```

### A.2 afservicesdk 使用约束

- `auth_type=PURE_OAUTH_SDK` 必填 — 缺失会回落到包含支付确认的流程
- `backWant` 三字段必须与 `module.json5` 中 Ability 声明一致
- `sandbox` 参数固定传 `false`（HarmonyOS 版不支持沙箱）
- 回调返回的字段必须 `.toString()` 强转 — 服务端偶发返回 number/boolean

### A.3 什么时候值得走这条路

- 你的企业有私有 ohpm 镜像或能直接从支付宝拿到包
- 不想引入服务端 authInfo 签名接口（把 URL 构造放客户端）
- 支付场景用不到 cashiersdk（不需要同时装两个包）

多数 HarmonyOS 项目不满足这些条件，用主流路径即可。
