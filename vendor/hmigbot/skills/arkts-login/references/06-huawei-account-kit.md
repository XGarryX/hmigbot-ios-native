# 华为账号一键登录（Account Kit）

HarmonyOS NEXT **系统原生**一键登录方案。基于 OAuth 2.0 + OpenID Connect，鸿蒙生态唯一不依赖第三方厂商、不依赖运营商网关、不依赖 SIM 卡的一键登录路径。

> 与微信/支付宝登录复用同一套 OAuth 2.0 职责边界（见 [01-login-flows.md](01-login-flows.md)），但客户端调用形态完全不同 — 不走 SDK SendReq + WXEventHandler 异步回调，而是 `AuthenticationController.executeRequest()` 直接 await Promise。

## 1. 为什么单独一份文档

Account Kit 与微信/支付宝/SMS 三条路径的关键差异：

| 维度 | 微信 / 支付宝 | Account Kit |
|---|---|---|
| 调用形态 | `sendReq()` + 异步 onResp 回调 | `executeRequest()` → Promise |
| 凭证 | `code` / `auth_code` | `authorizationCode` + 可选 `unionID` / `openID` |
| 用户号码 | 客户端拿不到，全靠服务端反查 | **匿名手机号客户端可显示**，明文需服务端换 |
| 安装依赖 | 必须装微信/支付宝 App | **零外部依赖**，鸿蒙系统自带 |
| SIM 卡要求 | 无 | 无（这是相对运营商一键登录的核心优势） |
| 权益申请 | 开放平台审核 | AGC 实时审批（2025 升级后秒过） |
| 上架要求 | 可选 | **若已接第三方账号登录则必选**（华为应用市场强制规则） |

## 2. 适用判断

**适用**：
- 鸿蒙原生应用（`HarmonyOS` API 12+）
- 主用户群在中国大陆境内
- 需要满足华为应用市场上架强制规则

**不适用 / 限制**：
- 中国港澳台、海外华为账号 — 拿不到匿名手机号
- 邮箱账号 / 未绑定手机号的华为账号 — 匿名手机号为空
- 应用服务端必须部署在中国境内（涉及境内号码字段不允许出境）
- 需要支持非华为账号用户的"一键登录" — Account Kit 仅覆盖华为账号场景，非华为账号用户必须降级 SMS

**典型组合策略**：Account Kit 优先 + SMS 兜底（覆盖无华为账号、邮箱账号、海外账号场景）。

## 3. 权益申请（前置条件）

2025 年升级后流程简化：

1. AGC（AppGallery Connect）控制台 → 我的应用 → 选择应用
2. "API 管理" → "Account Kit" → 申请 `quickLoginAnonymousPhone` 权益
3. **2025-2026 升级后实时审批**：符合条件的应用秒过；不符合的会立即说明原因
4. 审批通过后 **24 小时生效**（调试可临时把设备时间向后调 24 小时绕过）

无权益就调匿名手机号接口 → 返回空字符串，必须空值降级。

## 4. 配置准备

### 4.1 oh-package.json5

无需新增 ohpm 依赖，Account Kit 是系统 Kit：

```typescript
import { authentication } from '@kit.AccountKit'
import { hilog } from '@kit.PerformanceAnalysisKit'
```

### 4.2 module.json5 权限

```json5
{
  "module": {
    "requestPermissions": [
      { "name": "ohos.permission.INTERNET" }
    ]
  }
}
```

`Account Kit` 不要求额外的危险权限，无需运行时申请。

### 4.3 混淆白名单（关键，漏配必坑）

如果项目开启代码混淆（`obfuscation-rules.txt`），`quickLoginAnonymousPhone` 属性会被混淆 → 取号永远为空。必须保留：

```
# obfuscation-rules.txt
-keep-property-name
quickLoginAnonymousPhone
unionID
openID
authorizationCode
```

### 4.4 client_id

AGC 应用控制台 "应用信息" → "Client ID"。**不是** AppGallery 的 App ID。建议放进 `BuildProfile` 或资源字符串，不要硬编码：

```typescript
import { BuildProfile } from '../BuildProfile'
const HW_CLIENT_ID = BuildProfile.HW_CLIENT_ID
```

## 5. 客户端调用（最小可用代码）

### 5.1 标准调用模板

```typescript
import { authentication } from '@kit.AccountKit'
import { common } from '@kit.AbilityKit'
import { BusinessError } from '@kit.BasicServicesKit'

class HuaweiLoginHelper {
  /**
   * 触发华为账号一键登录授权。
   * @returns authorizationCode 临时凭证（5 分钟有效）+ 匿名手机号
   * @throws BusinessError 用户取消 / 未登录华为账号 / 系统错误
   */
  static async login(context: common.UIAbilityContext): Promise<HuaweiLoginResult> {
    // 1. 构建授权请求
    const provider = new authentication.HuaweiIDProvider()
    const request = provider.createLoginWithHuaweiIDRequest()
    request.scopes = ['quickLoginAnonymousPhone']  // 匿名手机号 scope
    request.permissions = ['quickLoginAnonymousPhone']
    request.forceLogin = true   // false=华为账号未登录直接报错；true=拉起华为账号登录页
    request.state = `hw_login_${Date.now()}`  // CSRF 防护，回调原样返回

    // 2. 执行请求
    const controller = new authentication.AuthenticationController(context)
    const response = await controller.executeRequest(request)

    // 3. 解析结果（注意类型断言）
    const data = response.data as authentication.LoginWithHuaweiIDResponse
    return {
      authorizationCode: data?.authorizationCode ?? '',
      anonymousPhone: data?.unionID ?? '',  // 匿名手机号位于 unionID 字段（鸿蒙 SDK 命名约定）
      openID: data?.openID ?? '',
      unionID: data?.unionID ?? '',
      state: data?.state ?? '',
    }
  }
}

interface HuaweiLoginResult {
  authorizationCode: string
  anonymousPhone: string  // 形如 138****8888，可直接展示
  openID: string
  unionID: string
  state: string
}
```

> **注意**：HarmonyOS API 不同小版本字段位置略有调整，写代码前务必查 [arkts-knowledge-verifier](#) 验证 `LoginWithHuaweiIDResponse` 的实际字段。本模板按 API 12+ 通行结构。

### 5.2 Page 层调起（推荐 forceLogin=false 走静默优先）

```typescript
@Entry
@ComponentV2
struct HuaweiLoginButton {
  @Local isLoading: boolean = false
  @Local anonymousPhone: string = ''  // 预取号结果，用于按钮文案展示

  // 进入页面时静默预取号（用户已登录华为账号场景下零交互拿到号码）
  aboutToAppear(): void {
    this.preFetchPhone()
  }

  private async preFetchPhone(): Promise<void> {
    try {
      const ctx = getContext(this) as common.UIAbilityContext
      const result = await HuaweiLoginHelper.login(ctx /* forceLogin=false 在 Helper 内传入 */)
      this.anonymousPhone = result.anonymousPhone
    } catch (e) {
      // 静默失败，UI 显示"使用华为账号登录"通用文案
      console.info(`[HwLogin] preFetch silent fail: ${(e as BusinessError).code}`)
    }
  }

  private async onClickLogin(): Promise<void> {
    if (this.isLoading) return
    if (!this.isPrivacyChecked) {
      promptAction.showToast({ message: '请先阅读并同意服务条款和隐私协议' })
      return
    }

    this.isLoading = true
    try {
      const ctx = getContext(this) as common.UIAbilityContext
      const result = await HuaweiLoginHelper.login(ctx)

      if (result.authorizationCode.length === 0) {
        promptAction.showToast({ message: '华为登录异常，请重试或选择其他方式' })
        return
      }

      // 把 authorizationCode 送后端，后端调
      // POST https://oauth-login.cloud.huawei.com/oauth2/v6/quickLogin/getPhoneNumber
      // 拿明文手机号 + UnionID → 关联/创建用户 → 返回业务 token
      await this.loginVm.loginByHuaweiCode(result.authorizationCode)
    } catch (e) {
      this.handleLoginError(e as BusinessError)
    } finally {
      this.isLoading = false
    }
  }

  build() {
    Button(this.anonymousPhone.length > 0
      ? `华为账号 ${this.anonymousPhone} 一键登录`
      : '使用华为账号登录')
      .onClick(() => this.onClickLogin())
      .enabled(!this.isLoading)
  }
}
```

### 5.3 静默登录 vs 显式登录的选择

| 模式 | `forceLogin` | 适用场景 |
|---|---|---|
| 静默登录 | `false` | 用户已绑定过应用 + 已登录系统华为账号 → 进入 App 自动恢复登录态。失败默认无 UI |
| 显式登录 | `true` | 登录页用户主动点击 → 即使系统未登录华为账号也拉起登录引导 |

**典型策略**：App 启动 / Mine Tab 进入时跑一次静默登录 → 失败再展示显式登录按钮。

## 6. 服务端契约（必读）

⚠️ **客户端只拿 authorizationCode，绝不直接调华为开放平台换 token** — 同样的 OAuth 2.0 边界（[01-login-flows.md](01-login-flows.md) §2-3）。

### 6.1 服务端接口

服务端使用 `client_id + client_secret + authorizationCode` 调华为云：

```
POST https://oauth-login.cloud.huawei.com/oauth2/v6/quickLogin/getPhoneNumber
{
  "client_id": "<AGC client_id>",
  "client_secret": "<AGC client_secret>",
  "authorization_code": "<客户端送来的 authorizationCode>"
}

→ 返回:
{
  "phoneNumber": "+8613812345678",  // 完整明文手机号
  "countryCode": "86",
  "unionID": "...",                 // 华为账号在该开发者下的稳定唯一标识
  "openID": "..."                   // 当前应用下的标识
}
```

**unionID 是关联用户的稳定 key**：华为账号在同一开发者下的所有应用共享 unionID（用于跨应用串联），openID 仅当前应用唯一。**绑用户表用 unionID**。

### 6.2 后端契约检查清单

| 项 | 示例 | 必确认 |
|---|---|---|
| 华为登录接口路径 | `/user/loginByHuawei` | 入参：`authorizationCode`；响应：业务 token + 用户信息 |
| 服务端 client_id / client_secret 来源 | AGC 控制台 | **secret 绝不下发客户端** |
| 服务端部署位置 | 必须中国境内 | 海外服务器调华为云接口拿不到 phoneNumber |
| 华为返回的 phoneNumber 处理 | 入库前去 `+86` 前缀 | 与 SMS 登录入库一致 |
| 90 天免短信验证 | 后端实现 | 同手机号 90 天内有 Account Kit 登录记录可免短信 |

## 7. 与 SMS / 微信 共存的登录页设计

```
┌─────────────────────────────────┐
│  Logo                           │
│                                 │
│  [华为账号 138****8888 一键登录] │ ← Account Kit（首选）
│                                 │
│  ─────── 其他登录方式 ───────    │
│                                 │
│  [手机号 + SMS 登录]             │ ← SMS 兜底
│  [微信登录]                      │ ← 可选
│                                 │
│  ☐ 已阅读并同意《服务协议》/《隐私政策》│
└─────────────────────────────────┘
```

**展示逻辑**：
1. 进页面 → 静默预取号
2. 拿到匿名手机号 → 主按钮显示号码 + "一键登录"
3. 拿不到 → 主按钮文案"使用华为账号登录"
4. 主按钮失败 → 提示用户改用 SMS

## 8. 错误码与降级策略

```typescript
import { BusinessError } from '@kit.BasicServicesKit'

private handleLoginError(err: BusinessError): void {
  const code = err.code
  switch (code) {
    case 1001502001:  // 网络异常
      promptAction.showToast({ message: '网络异常，请重试' })
      break
    case 1001500001:  // 用户取消
      // 静默处理，不弹提示（按苹果 / 谷歌人机交互规范）
      break
    case 1001502005:  // 用户未登录华为账号
      // 提示用户先登录华为账号，或建议改用 SMS
      promptAction.showToast({ message: '请先登录华为账号或使用其他登录方式' })
      this.fallbackToSms()  // 自动切到 SMS UI
      break
    case 1001500003:  // 权益未生效（24h 内 / 未申请）
    case 1001500004:  // 权益申请未通过
      // 不向用户暴露技术细节，直接降级
      console.warn('[HwLogin] entitlement not ready')
      this.fallbackToSms()
      break
    default:
      promptAction.showToast({ message: '登录失败，请稍后重试' })
      console.error(`[HwLogin] code=${code} msg=${err.message}`)
  }
}
```

> **错误码以华为开发者官网最新文档为准**。本表为常见代表值，实际数值随系统版本可能微调，写代码前用 [arkts-knowledge-verifier](#) 校核 `@kit.AccountKit` 的最新 errcode。

## 9. 上架华为应用市场强制规则（决策依据）

华为应用市场规则原文（提交审核前必读）：

> 提交至华为应用市场的 HarmonyOS 应用和元服务，登录场景全部满足以下三点时，**华为账号登录为必选**：
> 1. 接入了第三方登录方式（如微信登录、QQ 登录）
> 2. 应用和三方账号 CP 非同一关联主体（如 QQ 音乐接入微信登录就属于同一关联主体，可豁免）
> 3. 不涉及使用公民真实身份信息来鉴定用户身份（涉及实名认证的金融/政务类除外）

**对 Fitness 类应用的含义**：如果你的应用接了微信登录 / SMS 登录，那么 Account Kit **必须接** — 否则上架被拒。

## 10. 与项目 D-4 决策的对接

> 此节为 Fitness 项目特定语境（来自 spec/baseline/migration-decisions.md D-4），其他项目可忽略。

Android 闪验 SHANYAN → HarmonyOS 替换三档：

| 候选 | 工作量 | 体验 | 上架风险 |
|---|---|---|---|
| **A. Account Kit 单点** | 低 | 鸿蒙最佳 | 无华为账号用户无法登录（需保留 SMS 才合规） |
| **B. 仅 SMS 兜底** | 极低 | 中 | 上架可能被拒（若有微信登录） |
| **C. Account Kit + SMS 兜底** ✅ | 低 | 高 | 满足强制规则 |

**推荐 C**：
- 已有 SMS 链路完整复用
- 新增 `services/sdk/HuaweiAccountAdapter.ets` 包装 §5 模板
- 后端新增 `/user/loginByHuawei` 端点（参考 §6.1 套用现有 OneClick 后端）
- LoginPage 顶部加 Account Kit 按钮 + 现有 SMS 表单不动

## 11. 常见陷阱

| 现象 | 根因 | 解法 |
|---|---|---|
| 匿名手机号永远为空 | 混淆未保留 `quickLoginAnonymousPhone` 属性 | 加 `-keep-property-name` §4.3 |
| 匿名手机号永远为空（混淆已保留）| 权益审批刚通过 < 24h | 等 24h 或调试机系统时间往后调 |
| 匿名手机号永远为空（权益已生效）| 邮箱账号 / 海外华为账号 / 未绑手机号 | 空值降级 SMS |
| 服务端拿不到 phoneNumber 字段 | 服务端部署在海外站点 | 服务端必须中国境内部署 |
| `executeRequest` throws "User cancel" | 用户主动关闭授权页 | 静默处理，不打 toast |
| 静默预取号成功但显式登录失败 | `forceLogin` 设错 / scope 漏配 | 严格按 §5.1 模板 scopes/permissions 都填 |
| 登录后业务 token 仍 401 | 漏掉 token 三处同步 | 见 [05-post-login-state.md §1](05-post-login-state.md) |
| 上架审核被拒"未接华为账号登录" | 接了微信但没接 Account Kit | 按 §9 强制规则补接 |
| `getContext(this)` 返回 null | 在非 @Entry 组件 / aboutToAppear 之前调 | 必须 Page 层 + 生命周期内调 |

## 12. 调试技巧

1. **日志过滤**：`hilog tag=AccountKit` 或 `tag=HuaweiID` 抓 SDK 内部日志
2. **权益生效校验**：调一次 `executeRequest`（forceLogin=true）→ 若返回的 `unionID` 全空 → 权益未生效
3. **多设备测试**：模拟器无法测真实华为账号，必须真机；平板 / 折叠屏 / 手表上 UI 表现可能不同，按设备类型 capability 兜底
4. **服务端联调**：用 Postman / curl 直接调华为开放平台接口验证 `client_id + client_secret` 正确性，再串入业务后端

## 13. 进一步阅读

- 华为账号官方文档：[Account Kit 一键登录开发指南](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/account-quick-login)
- AGC 权益申请入口：AGC 控制台 → 我的应用 → API 管理 → Account Kit
- 鸿蒙系统 API：`@kit.AccountKit` → `authentication` namespace
- 一键登录场景分支：[一键登录，打造华为账号便捷新体验](https://blog.csdn.net/HUAWEI_HMSCore/article/details/140927909)

---

**与本 skill 其他文档的协同**：
- OAuth 2.0 职责边界 → [01-login-flows.md](01-login-flows.md)
- 登录后 token 同步 → [05-post-login-state.md](05-post-login-state.md)
- SMS 兜底（必备）→ [04-sms-login-generic.md](04-sms-login-generic.md)
