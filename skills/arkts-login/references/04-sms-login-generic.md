# 手机号 + SMS 验证码登录（通用骨架）

不涉及具体后端接口，**只讲通用客户端骨架**：60s 验证码倒计时、防重复点击与并发。

> 注：注销后是否需要重建匿名/游客身份、登录页是否需要带初始 token 等**业务侧设计决策不属于本 skill 范围**，由项目自行决定。

## 1. 流程骨架

```
1. 用户输入手机号
2. 点击"获取验证码" → 发送 SMS 接口
3. 发送成功 → 启动 60s 倒计时
4. 用户收到短信输入验证码（6 位可选自动登录）
5. 点击"登录" → 登录接口（手机号 + 验证码）
6. 登录成功 → 持久化业务 token + pop 页面
```

## 2. 验证码发送失败不启动倒计时

**踩过的坑**：

```typescript
// ❌ 错误：不 await，立即启动倒计时
private onGetVerifyCode() {
  this.loginVm.sendSmsCode(phone)  // 异步发起，但不等
  this.startCountdown()             // 立即启动
  // 实际 sendSmsCode 失败了，但倒计时已走 → 用户等 60s 才能重试
}
```

**正确**：

```typescript
// ✅ await + try/catch
private async onGetVerifyCode() {
  try {
    await this.loginVm.sendSmsCode(phone)
  } catch (e) {
    promptAction.showToast({ message: '发送失败' })
    return  // 失败直接 return，不启动倒计时
  }
  this.startCountdown()
}
```

## 3. 60s 倒计时由 Page 管理（不是 ViewModel）

**错误做法**（新手常犯）：

```typescript
// ❌ 把倒计时放 ViewModel
class LoginVM {
  countdown: number = 0
  private timer: number = -1

  sendSmsCode() {
    this.timer = setInterval(() => { this.countdown-- }, 1000)
  }
}
```

**为什么错**：ViewModel 一般是 singleton。多个登录页（如绑定手机号弹窗 + 登录页）共享同一个 VM，倒计时会互相干扰。Page 销毁后 VM 还在，timer 泄漏。

**正确做法**：Page 持有 timer，VM 只负责调接口：

```typescript
@ComponentV2
struct LoginPage {
  @Local countDown: number = 0
  @Local isGetCodeEnabled: boolean = true
  @Local getCodeText: string = '获取验证码'
  private countDownTimer: number = -1

  aboutToDisappear(): void {
    // 页面销毁必须清 timer，否则 timer 泄漏
    if (this.countDownTimer !== -1) {
      clearInterval(this.countDownTimer)
      this.countDownTimer = -1
    }
  }

  private startCountdown(): void {
    this.isGetCodeEnabled = false
    this.countDown = 60
    this.getCodeText = `${this.countDown}s`
    this.countDownTimer = setInterval(() => {
      this.countDown--
      if (this.countDown <= 0) {
        this.resetCountdown()
      } else {
        this.getCodeText = `${this.countDown}s`
      }
    }, 1000)
  }

  private resetCountdown(): void {
    if (this.countDownTimer !== -1) {
      clearInterval(this.countDownTimer)
      this.countDownTimer = -1
    }
    this.countDown = 0
    this.isGetCodeEnabled = true
    this.getCodeText = '获取验证码'
  }
}
```

## 4. 防连点"获取验证码"

两种机制叠加：

**UI 层**：`isGetCodeEnabled` 状态变量 + `.enabled(this.isGetCodeEnabled)`。

**逻辑层**：函数入口 `if (!this.isGetCodeEnabled) return`。

两者都要有，因为：
- UI 层 `.enabled(false)` 只能让按钮变灰，不能阻止代码层面的重复调用
- 逻辑层 return 兜底防御

```typescript
private async onGetVerifyCode(): Promise<void> {
  if (!this.isGetCodeEnabled) return  // 防并发
  // ...
}
```

## 5. 验证码输入自动触发登录（可选）

部分 App 验证码输入满 6 位自动登录：

```typescript
TextInput({ text: this.verifyCode })
  .onChange(async (value: string) => {
    this.verifyCode = value
    if (value.length === 6) {
      // 自动触发登录（前提：其他校验通过）
      if (this.isPrivacyChecked) {
        await this.onLoginClick()
      }
    }
  })
```

**注意**：不要同时保留"登录"按钮的点击路径和自动登录路径竞态——自动触发后一定要置 `isLoading = true` 防止按钮再点。

## 6. 登录成功的处理

```typescript
private async onLoginClick() {
  if (this.isLoading) return  // 防并发
  if (!this.isPrivacyChecked) {
    promptAction.showToast({ message: '请先同意协议' })
    return
  }
  if (this.verifyCode.length === 0) {
    promptAction.showToast({ message: '请输入验证码' })
    return
  }

  this.isLoading = true
  try {
    const success = await this.loginVm.loginWithSms(this.phoneNumber, this.verifyCode)
    if (success) {
      // 登录成功 → 清倒计时 → pop 页面
      this.resetCountdown()
      this.pathStack.pop()
    } else {
      promptAction.showToast({ message: this.loginVm.errorMessage || '登录失败' })
      // 失败时不清倒计时（让用户看到 "验证码输错了，还能再等 20s 重发"）
    }
  } finally {
    this.isLoading = false
  }
}
```

## 7. ViewModel 层通用模式

```typescript
@ObservedV2
class LoginViewModel extends BaseViewModel {
  @Trace errorMessage: string = ''

  /** 发送验证码 — 失败时 throw，不返回 false（让 Page 用 try/catch 更清晰）*/
  async sendSmsCode(phone: string): Promise<void> {
    try {
      await <api.sendSms>(phone)
    } catch (e) {
      // ArkTS：throw 只接受 Error 及其派生类（arkts-limited-throw）。catch 到的 e 是非
      // Error 静态类型，直接 `throw e` 编译不过——先收敛成 Error 局部变量再抛。
      const err: Error = (e instanceof Error) ? e : new Error('发送失败')
      this.errorMessage = err.message
      throw err
    }
  }

  /** 登录 — 返回 boolean，失败时 errorMessage 已设置 */
  async loginWithSms(phone: string, code: string): Promise<boolean> {
    try {
      const userData = await <api.bindMobileBySmsCode>(phone, code)
      await this.saveUserData(userData)  // 见 05-post-login-state.md
      return true
    } catch (e) {
      this.errorMessage = (e instanceof Error) ? e.message : '登录失败'
      return false
    }
  }
}
```

**设计决策**：
- `sendSmsCode` 失败抛异常 — Page 用 `try { await } catch {}` 决定是否启动倒计时
- `loginWithSms` 失败返回 false + 设 errorMessage — Page 直接判 boolean，toast 读 errorMessage

两种模式各有场景，根据上下游消费方式选。

### 7.1 错误链路的两个 ArkTS 编译点（TS 能过、ArkTS 拦）

1. **重抛异常**：`throw` 只接受 `Error` 及其派生类（`arkts-limited-throw`，错误码 10605087）；直接
   `throw e`（`e` 是 catch 的非 Error 静态类型）编译不过——先收敛成 `Error` 局部再抛，
   见上方 `sendSmsCode`。自定义错误类须 `extends Error`。
   **负向守卫（多类分发）**：把 `throw e` 裹进 `instanceof` 守卫也**仍报同错**——
   `if (e instanceof BizError || e instanceof NetworkError) { throw e }` 编译不过：`throw`
   只按 catch 变量的声明类型判定、不吃守卫的 `instanceof` 流窄化（仅 `throw` 如此；读 `e.message`
   等成员照常窄化）。多类分发同样先收敛成 typed 局部再抛：
   `const err: Error = (e instanceof BizError || e instanceof NetworkError || e instanceof TimeoutError) ? e : classify(e as Object); throw err`。
2. **无参端点的空请求体**：游客/设备登录、拉取用户信息等无入参端点，请求体为空对象。ArkTS
   禁止用裸 `{}` 初始化 `object` / `Object` 类型（`arkts-no-untyped-obj-literals`），
   `send(url, {})` 这类会编译失败。空 body 改用 `const body: object = new Object()`
   （`new Object()` 不是字面量、豁免此规则），或声明一个空 `interface` 再 `{}` 初始化它。

## 8. 常见陷阱清单

| 现象 | 根因 | 解法 |
|---|---|---|
| 验证码发送失败但倒计时已启动 | `sendSmsCode` 未 await | 改 await + try/catch，详见 §2 |
| 多个登录入口共享 VM 倒计时打架 | 倒计时放 VM | 挪到 Page，详见 §3 |
| Page 销毁后 timer 泄漏 | `aboutToDisappear` 未 clearInterval | 加清理，详见 §3 |
| 验证码按钮连点发多条短信 | 无 `isGetCodeEnabled` 防护 | UI + 逻辑双锁，详见 §4 |
| 用户未同意协议就能登 | 登录方法内无校验 | `onLoginClick` 头部加，详见 §6 |
| 验证码填错后还要等 60s | 登录失败时误清倒计时 | 失败不清，详见 §6 |
| 重抛异常报 `arkts-limited-throw` | 直接 `throw e`（e 非 Error 静态类型）| 收敛成 Error 局部再抛，详见 §7.1 |
| 空 body 报 `arkts-no-untyped-obj-literals` | 无参端点用裸 `{}` 初始化 object | `new Object()` 或空 interface，详见 §7.1 |
