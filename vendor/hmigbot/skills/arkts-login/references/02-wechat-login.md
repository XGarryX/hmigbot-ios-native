# 微信登录 SDK 深入细节

聚焦 `wxopensdk.SendAuthReq` 的调起、回调、与支付回调共存处理。前置（Ability 集成、module.json5、签名）见 SKILL.md §初始化前置。

## 1. `SendAuthReq` 字段规格

```typescript
import * as wxopensdk from '@tencent/wechat_open_sdk'

const authReq = new wxopensdk.SendAuthReq()
authReq.scope = 'snsapi_userinfo'  // 移动应用唯一值
authReq.state = 'login_' + Date.now() + '_' + Math.random().toString(36).substring(2, 10)
// 可选
authReq.transaction = '<业务侧追踪 ID，回调原样返回>'
```

### scope 限制

**移动应用 scope 只能填 `snsapi_userinfo`**。
- 小程序的 `snsapi_base` / `snsapi_login` 不适用
- 填错会报"scope 参数错误"或直接返回失败

### state 必填

防 CSRF 必备。详细原理见 [01-login-flows.md](01-login-flows.md) §4。

### transaction（可选）

业务侧追踪 ID，微信回调会原样返回。多个并发请求时用于区分。

## 2. 调起模板（Page 层）

```typescript
// LoginPage 内
private launchWechatAuth(): void {
  // 前置校验
  if (!this.isPrivacyChecked) {
    promptAction.showToast({ message: '请先阅读并同意服务条款和隐私协议' })
    return
  }
  if (this.isLoading) return

  const APP_ID = '<移动应用 AppID>'
  if (APP_ID.length === 0) {
    Logger.error(TAG, 'WX_APPID is empty')
    return
  }

  const authReq = new wxopensdk.SendAuthReq()
  authReq.scope = 'snsapi_userinfo'
  authReq.state = 'login_' + Date.now()
  this.pendingWxState = authReq.state  // 存本地用于 CSRF 校验

  try {
    const context = getContext(this) as common.UIAbilityContext
    const wxApi = wxopensdk.WXAPIFactory.createWXAPI(APP_ID)
    wxApi.sendReq(context, authReq)
    Logger.info(TAG, 'wechat auth sent')
  } catch (e) {
    Logger.error(TAG, 'launchWechatAuth error: ' + e)
    promptAction.showToast({ message: '无法打开微信' })
  }
}
```

## 3. 回调注册与过滤

```typescript
// Page struct
private wxRespCallback = (resp: wxopensdk.BaseResp): void => {
  this.handleWxAuthResp(resp)
}

aboutToAppear(): void {
  wxEventHandler.registerOnWXRespCallback(this.wxRespCallback)
}
aboutToDisappear(): void {
  wxEventHandler.unregisterOnWXRespCallback(this.wxRespCallback)
}

private handleWxAuthResp(resp: wxopensdk.BaseResp): void {
  // ⚠️ 关键：必须过滤出授权类型的回调
  // Command.kCommandSendAuth = 1 表示是授权回调
  if (resp.type !== wxopensdk.Command.kCommandSendAuth) {
    return  // 支付回调、分享回调等，本页忽略
  }

  if (resp.errCode === wxopensdk.ErrCode.ERR_OK) {
    const authResp = resp as wxopensdk.SendAuthResp
    // state 校验（防 CSRF）
    if (authResp.state !== this.pendingWxState) {
      Logger.error(TAG, 'state mismatch')
      return
    }
    this.pendingWxState = ''

    const code = authResp.code ?? ''
    if (code.length === 0) {
      promptAction.showToast({ message: '微信授权异常' })
      return
    }
    this.performWechatLogin(code)  // 送到后端
  } else if (resp.errCode === wxopensdk.ErrCode.ERR_USER_CANCEL) {
    promptAction.showToast({ message: '已取消微信登录' })
  } else if (resp.errCode === wxopensdk.ErrCode.ERR_AUTH_DENIED) {
    promptAction.showToast({ message: '微信授权被拒绝' })
  } else {
    promptAction.showToast({ message: '微信授权失败' })
  }
}
```

### 为什么必须过滤 resp.type

`wxEventHandler` 是全局单例，Login 页和 Payment 页都会订阅。如果不过滤：

- 用户在 Payment 页支付 → PayResp 回调 → Login 页的 callback 也收到 → 误判登录成功
- 用户在 Login 页授权 → SendAuthResp 回调 → Payment 页的 callback 也收到 → 去查根本不存在的订单

**必须用 `resp.type` 或 `resp instanceof` 区分**。

## 4. 与 Payment 共存的双回调模式

```typescript
// 登录页
private onWxResp = (resp: wxopensdk.BaseResp): void => {
  if (resp.type !== wxopensdk.Command.kCommandSendAuth) return  // 只处理授权
  // ...
}

// 支付页
private onWxResp = (resp: wxopensdk.BaseResp): void => {
  if (resp.type !== wxopensdk.Command.kCommandPayByWX) return  // 只处理支付
  // ...
}
```

或者用 `instanceof`：

```typescript
if (resp instanceof wxopensdk.SendAuthResp) { /* 登录 */ }
if (resp instanceof wxopensdk.PayResp) { /* 支付 */ }
```

两种写法都行，**必选其一**。

## 5. 错误码对照表

| errCode | 常量 | 含义 | 业务动作 |
|---|---|---|---|
| 0 | `ERR_OK` | 授权成功 | 取 code → 送后端 |
| -1 | `ERR_COMM` | 普通错误 | 提示失败，不重试 |
| -2 | `ERR_USER_CANCEL` | 用户取消 | 提示"已取消"，不重试 |
| -3 | `ERR_SENT_FAILED` | 发送失败 | 检查 APP_ID / 签名 / 审核状态 |
| -4 | `ERR_AUTH_DENIED` | 授权拒绝 | 提示"授权被拒"，引导其他登录方式 |
| -5 | `ERR_UNSUPPORT` | 不支持 | 微信版本太低 |
| -6 | `ERR_BAN` | 应用被禁 | 开放平台账号被封 |

## 6. 回调拿到 code 后的处理

```typescript
private async performWechatLogin(code: string): Promise<void> {
  this.isLoading = true
  try {
    // 把 code 送后端，后端换 access_token + 查用户信息 + 签发业务 token
    const userData = await this.loginVm.loginByWechat(code)
    if (userData) {
      promptAction.showToast({ message: '登录成功' })
      this.pathStack.pop()
    } else {
      promptAction.showToast({ message: '微信登录失败' })
    }
  } catch (e) {
    promptAction.showToast({ message: '微信登录失败' })
  } finally {
    this.isLoading = false
  }
}
```

**关键**：客户端只送 code，**不换 token**。详见 [01-login-flows.md](01-login-flows.md) §2-3。

## 7. 双回调路径兼容

HarmonyOS 上微信回调有两种传递路径：

### 路径 A：通过 WXEventHandler（推荐）

Ability 的 `onCreate` / `onNewWant` 调 `WXApi.handleWant()` → SDK 内部分发到 `WXApiEventHandler.onResp` → Page 注册的 callback 被调用。

本文档主推这种方式，适合有 UI 交互的登录场景。

### 路径 B：通过 `onNewWant` 直取 want 参数

```typescript
// EntryAbility
onNewWant(want: Want): void {
  if (want?.parameters?.code) {
    const code = want.parameters.code as string
    // 通过 AppStorage 或 EventBus 通知 Page
    AppStorage.setOrCreate('wxLoginCode', code)
  }
  WXApi.handleWant(want, wxEventHandler)  // 同时也走 Event Handler
}
```

适合无 UI 场景（如后台刷新 token）。一般项目用路径 A 足够，不需要双路径。

## 8. 未安装微信的预检

```typescript
import { bundleManager } from '@kit.AbilityKit'

function isWeChatInstalled(): boolean {
  try {
    return bundleManager.canOpenLink('weixin://')
  } catch (e) {
    return false
  }
}

// 登录按钮 onClick
if (!isWeChatInstalled()) {
  promptAction.showToast({ message: '请先安装微信 App' })
  return
}
```

`module.json5` 的 `querySchemes` 必须声明 `weixin`，否则 `canOpenLink` 永远返回 false。

## 9. 模拟器调试限制

模拟器上 `sendReq` 必失败（错误码 16000001 类），因为模拟器没装微信。

- **真机测试**是唯一可靠方式
- 日志里搜 `wxopensdk::WXApi` 标签定位问题

## 10. 微信登录常见陷阱

| 现象 | 根因 | 解法 |
|---|---|---|
| `onResp` 不触发 | EntryAbility 没调 `handleWant` | 加上 |
| "应用未注册" | APP_ID 填成小程序 AppID | 改用移动应用 AppID |
| "Bundle ID 校验不通过" | 自动签名 / 开放平台未审核通过 | 手动签名 + 等审核 |
| 支付结果被登录页接收 | 未过滤 resp.type | 加 `Command.kCommandSendAuth` 过滤 |
| state 校验失败 | 没存 pendingState / 存完忘记清 | 按 §2-3 模板存取 |
| 模拟器永远失败 | 没装微信 | 真机测试 |
| code 每次都是空 | 开放平台 `snsapi_userinfo` scope 未申请 | 开放平台配置里申请 |

## 11. 登录/支付回调的注销时机

Page 销毁时必须注销 callback：

```typescript
aboutToDisappear(): void {
  wxEventHandler.unregisterOnWXRespCallback(this.wxRespCallback)
}
```

**不要用 `onDisAppear`** — `onDisAppear` 可能在 Page 还存活时触发（如 push 新页），导致提前注销错过回调。`aboutToDisappear` 才是真正的"页面销毁"生命周期。
