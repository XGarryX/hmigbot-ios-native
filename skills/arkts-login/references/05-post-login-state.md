# 登录后状态同步

登录成功后客户端要做的事远不止"存一个 token"。本文档聚焦 token 三处同步、通用数据写入模式、logout 正确流程、多页面感知登录态。

## 1. token 三处同步

典型项目里有三个地方需要同时持有 token：

| 位置 | 目的 | 生命周期 |
|---|---|---|
| `UserPreferences` / Preferences | 持久化跨应用重启 | App 卸载前 |
| `AppStorage` | 内存共享，供组件状态订阅 | App 进程存活期 |
| HTTP 拦截器（如项目 lib 的 `UserData`）| 请求头自动附加 Authorization | 进程存活期 |

**漏任何一处都会出问题**：

- 漏持久化 → 杀进程后登录态丢
- 漏 AppStorage → 组件层 `AppStorageV2.connect` 持有的实例不更新（V1 项目则是 `@StorageProp` 不更新），UI 看起来没登录
- 漏拦截器 → 网络请求仍用旧 token，接口 401

### 标准同步模板

```typescript
async saveToken(token: string): Promise<void> {
  // 1. 持久化
  await UserPreferences.setToken(token)

  // 2. 内存共享（组件状态订阅）
  AppStorage.setOrCreate('token', token)

  // 3. HTTP 拦截器（项目 lib 相关，按实际替换）
  <lib_network>.UserData.getInstance().token = token

  // 4. 版本号 bump 通知 UI 刷新
  AppStorage.setOrCreate('loginStateVersion', Date.now())
}
```

每条登录/登出/token 刷新路径都必须走这个统一入口。

## 2. `saveThirdPartyUserData` 通用数据写入模式

多个三方登录（微信 / 支付宝 / 其他）的后端响应结构高度相似。抽取公共方法避免重复：

```typescript
private async saveThirdPartyUserData(userData: ApiUserData): Promise<void> {
  // ⚠️ 关键原则：空值兜底，避免服务端空字段覆盖本地已有数据

  // token
  const existingToken = await UserPreferences.getToken()
  const token = (userData.token && userData.token.length > 0)
    ? userData.token
    : existingToken
  await this.saveToken(token)

  // userId
  const userId = (userData.userId && userData.userId > 0)
    ? userData.userId
    : await UserPreferences.getUserId()
  await UserPreferences.setUserId(userId)

  // VIP 等级（保护窗口应在 applyUserInfo 里而非这里；本地写入时用新值）
  const vipLevel = userData.vipLevel ?? await UserPreferences.getVipLevel()
  await UserPreferences.setVipLevel(vipLevel)

  // 昵称（空值不覆盖）
  if (userData.nickName && userData.nickName.length > 0) {
    await UserPreferences.setNickname(userData.nickName)
  }

  // 头像（空值不覆盖）
  if (userData.avatar && userData.avatar.length > 0) {
    await UserPreferences.setAvatar(userData.avatar)
  }

  // 其他可选字段：phoneAuth / userState / fromChannel 等
  await UserPreferences.setIsLogin(true)

  // 广播事件
  AppStorage.setOrCreate('loginStateVersion', Date.now())
  <emit LOGIN_OUT event with { isLogin: true }>
}
```

### 空值兜底的理由

服务端返回字段可能部分为空（数据库某字段为 null）。如果直接 `await setNickname(userData.nickName ?? '')`，本地的昵称会被覆盖成空字符串 → UI 显示空。

正确模式：**服务端返回空就不动本地**。

### 例外：token 必覆盖

token 不适用空值兜底——登录成功后必须用新 token。如果 userData.token 为空，说明后端接口有问题，应该视为登录失败。

## 3. 登录成功的完整处理链

```typescript
// VM 方法
async loginByWechat(code: string): Promise<boolean> {
  try {
    const userData: ApiUserData = await this.api.bindWx(code)
    if (!userData.token || userData.token.length === 0) {
      this.errorMessage = '登录失败（token 为空）'
      return false
    }
    await this.saveThirdPartyUserData(userData)
    return true
  } catch (e) {
    this.errorMessage = (e instanceof Error) ? e.message : '微信登录失败'
    return false
  }
}
```

## 4. 多页面感知登录态

### 方案 A：`loginStateVersion` 版本号

```typescript
// 1. 全局状态类（@ObservedV2 + @Trace）
@ObservedV2
class LoginStateModel {
  @Trace version: number = 0
}

// 2. 任意需要响应登录变化的 struct
@ComponentV2
struct SomePage {
  @Local loginState: LoginStateModel = AppStorageV2.connect(
    LoginStateModel, 'loginState', () => new LoginStateModel()
  )!

  // 用 @Monitor 监听变化触发动作
  @Monitor('loginState.version')
  onLoginStateChanged(): void {
    // 重新加载页面数据
    this.loadData()
  }
}
```

登录/登出 → 任意持有该 LoginStateModel 实例处直接 `this.loginState.version = Date.now()` → 所有 connect 同 key 的 struct 自动响应（V2 等价于 V1 的 `AppStorage.setOrCreate('loginStateVersion', ...)` + `@StorageLink`）。

### 方案 B：EventBus 广播

```typescript
// 登录成功时
<EventBus.emit>('LOGIN_STATE', { isLogin: true, userId })

// 订阅方
<EventBus.on>('LOGIN_STATE', (data) => {
  if (data.isLogin) this.refreshUserData()
  else this.clearUserUI()
})
```

### 选择建议

- **@ComponentV2 + @Provider/@Consumer + @Monitor** → 推荐方案，类型安全 + 响应式
- **EventBus**（老代码用）→ 适合解耦场景，但注意注销
- **方案 A 版本号 + AppStorageV2.connect**（V1 项目则用 `@StorageProp`）→ 简单场景可用

避免手动 `emitter.on` 回调写组件状态——@ComponentV2 里响应式更清晰。

## 5. logout 完整流程

```typescript
async logout(): Promise<void> {
  // 1. 调后端 logout（失败也继续清本地）
  try {
    await this.api.logout()
  } catch (e) {
    Logger.warn(TAG, 'logout api failed, continue local cleanup')
  }

  // 2. 清本地持久化数据
  await UserPreferences.clearUserSession()
  // clearUserSession 应清：token、userId、nickName、avatar、vipLevel、
  //                     vipManualUpdateTime、phone、userState、phoneAuth 等

  // 3. 清内存（AppStorage）
  AppStorage.setOrCreate('token', '')

  // 4. 清 HTTP 拦截器
  <lib_network>.UserData.getInstance().token = ''

  // 5. 通知 UI
  AppStorage.setOrCreate('loginStateVersion', Date.now())
  <emit LOGIN_OUT event with { isLogin: false }>
}
```

> **注**：注销后是否需要立即重建匿名/游客身份（如重新调 `initUserData` 拿新的会话 token），属于**业务侧设计决策**，不属于本 skill 范围。如果项目的部分接口（如发送验证码）要求请求头必须带 token，则在 logout 末尾按项目业务模型补充重建逻辑；否则可省略。

## 6. 保护窗口放哪里（关键设计）

支付/VIP 开通后本地 vipLevel 设为 1，但客户端下次调 getUserInfo 时服务端异步回调可能还没跑完 → 本地被覆盖回 0。**保护窗口防的是这个时序**。

### 错误：放支付/登录回调里

```typescript
// ❌ 只在这一处写保护时间戳
onPaySuccess() {
  await setVip(1)
  await setProtectStartAt(Date.now())
}

// 但任意一次 getUserInfo 仍会覆盖
onUserInfo(info) {
  await setVip(info.vipLevel)  // 会把 1 刷成 0
}
```

### 正确：下沉到 `applyUserInfo`

```typescript
// ✅ 保护判断放在"所有用户信息写回入口"
async applyUserInfo(remote: ApiUserData): Promise<void> {
  const localVip = await UserPreferences.getVipLevel()
  const remoteVip = remote.vipLevel ?? 0
  const protectStartAt = await UserPreferences.getVipManualUpdateTime()
  const PROTECTION_MS = <项目选定，建议 5 分钟>

  const withinProtection =
    localVip > 0 &&
    remoteVip === 0 &&
    Date.now() - protectStartAt < PROTECTION_MS

  if (!withinProtection) {
    await UserPreferences.setVipLevel(remoteVip)
  }
  // ... 其他字段照常写入
}
```

所有经过 applyUserInfo 的路径（登录、getUserInfo 刷新、支付成功等）都受保护。登录路径通常不触发保护（因为登录后 remoteVip 就是正确的），但走统一入口避免漏点。

## 7. 登录页的 UI 状态

```typescript
@ComponentV2
struct LoginPage {
  @Local isLoading: boolean = false
  @Local isPrivacyChecked: boolean = false
  // ...

  // 登录按钮
  Text('登录')
    .enabled(!this.isLoading)
    .opacity(this.isLoading ? 0.5 : 1.0)
    .onClick(() => this.onLoginClick())

  // 微信按钮
  Image($r('app.media.icon_wechat_login'))
    .onClick(() => {
      if (this.isLoading) return  // 防连点
      this.launchWechatAuth()
    })
}
```

**关键**：任何支付调起/登录调起必须在 `isLoading = true` 期间禁用所有可能触发登录的入口。

## 8. 自动登录（App 启动时）

```typescript
// App 启动 / SplashPage
async checkAutoLogin(): Promise<boolean> {
  const token = await UserPreferences.getToken()
  if (!token) return false  // 没 token → 游客态

  // 用 token 拉一次 getUserInfo 验证 token 有效性
  try {
    const info = await this.api.getUserInfo()
    await this.applyUserInfo(info)
    return true  // 自动登录成功
  } catch (e) {
    // token 过期或无效 → 清理 + 回到游客态
    if (<is 401>(e)) {
      await this.logout()
    }
    return false
  }
}
```

**重要**：App 启动时**不要**静默调用微信/支付宝 SDK 重新授权。那是"三方登录"，不是"自动登录"。自动登录只涉及本地 token + 后端验证。

## 9. 多端登录互踢（可选）

如果后端支持同一账号只能一端在线：

```typescript
// 监听后端推送（WebSocket / push）
on('KICK_OFF', async (data) => {
  if (data.userId === currentUserId) {
    promptAction.showToast({ message: '账号已在其他设备登录' })
    await this.logout()  // 本端强制登出
    <导航到登录页>
  }
})
```

## 10. 常见陷阱清单

| 现象 | 根因 | 解法 |
|---|---|---|
| 登录后 API 仍 401 | token 没同步到拦截器 | 三处同步模板（§1） |
| 登录后其他页面 UI 未刷新 | 没 bump loginStateVersion | `AppStorage.setOrCreate('loginStateVersion', Date.now())`（§4） |
| 服务端昵称返回空覆盖本地 | 未做空值兜底 | `if (xxx.length > 0) setXxx(...)`（§2） |
| 支付后 VIP 回退 | 保护窗口只在支付回调 | 下沉到 applyUserInfo（§6） |
| App 启动时重复跳登录页 | token 有效性未校验 | checkAutoLogin 里 getUserInfo（§8） |
| 多端互踢后本地未清 | 只提示未 logout | 监听到 KICK_OFF 必须 logout（§9） |
