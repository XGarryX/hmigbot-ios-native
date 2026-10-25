# 订单查询与用户状态同步

本文档聚焦**支付完成后**的工程模式：订单结果查询、失败兜底、用户状态写回的保护窗口、跨端同步。

## 1. 核心原则

> **SDK 回调 / errCode / resultStatus ≠ 支付真实成功**

唯一可信的真相源是**后端订单查询**。客户端 SDK 回调只是"用户行为反馈"——用户可能已经付了但客户端没收到回调（App 被杀、网络中断），也可能客户端收到 `errCode=0` 但后端订单因为签名校验问题其实未成功。

流程：
```
SDK 回调 → 客户端查询后端订单 → 后端返回真实状态 → 更新 UI/用户数据
                ↓（多次重试）
          失败兜底：调后端 cancelOrder 避免僵尸订单
```

## 2. 订单查询完整模板

```typescript
class OrderQueryHelper {
  private isQueryingPayResult: boolean = false
  private currentOrderId: string = ''

  /** 发起查询（入口方法，支持多次触发） */
  async queryPayResult(): Promise<void> {
    // 1. 并发防护
    if (this.isQueryingPayResult) {
      Logger.info(TAG, 'queryPayResult: already in flight')
      return
    }
    if (this.currentOrderId.length === 0) {
      Logger.info(TAG, 'queryPayResult: no orderId')
      return
    }

    this.isQueryingPayResult = true
    const orderId = this.currentOrderId
    this.currentOrderId = ''  // 清除，防止 onPageShow 二次触发

    try {
      await this.queryWithRetry(orderId, <MAX_RETRY>, <INTERVAL_MS>)
    } finally {
      this.isQueryingPayResult = false
    }
  }

  /** 重试查询 */
  private async queryWithRetry(
    orderId: string,
    retries: number,
    intervalMs: number
  ): Promise<void> {
    for (let i = 0; i <= retries; i++) {
      try {
        const status = await this.api.queryOrderStatus(orderId)
        if (this.isSuccess(status)) {
          await this.handleSuccess(orderId)
          return
        }
      } catch (e) {
        Logger.warn(TAG, `queryOrderStatus attempt ${i} failed`)
      }
      if (i < retries) {
        await this.sleep(intervalMs)
      }
    }
    // 最终仍未成功 → 兜底取消订单
    Logger.warn(TAG, `query exhausted after ${retries + 1} attempts`)
    await this.cancelOrder(orderId)
    promptAction.showToast({ message: '支付状态未确认' })
  }

  private isSuccess(status): boolean {
    // 后端约定的成功条件
    return status.payStatus === <后端成功码>
  }

  private async handleSuccess(orderId: string): Promise<void> {
    // 1. 更新本地 VIP / 点数（立即更新，不等服务端异步）
    // 2. 设置保护窗口时间戳
    // 3. 通知 UI 刷新
    // 4. pop 支付页
  }

  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms))
  }
}
```

## 3. 参数选择建议

| 场景 | 间隔 | 重试次数 | 总窗口 |
|------|------|---------|--------|
| 普通买断 / 积分订单 | 1500~3000ms | 2~4 | ~12s |
| **支付宝订阅签约 SCHEME**（`alipays://...`）| 1500ms | **20~30** | **30~45s** |
| 微信 H5 / 支付宝 8000 态 | 1500~3000ms | 2~4 | ~12s |

订阅签约场景需要更长是因为：用户在支付宝完成签约通常 5-30s（含登录、确认协议、生物识别），后端 `payStatus: unsigned → signed/paid` 落库可能延迟几秒。配合可中断 sleep（监听 `APP_FOREGROUND` 事件唤醒），实际很多用户在 10-15s 内就能拿到结果——具体见 [07-alipay-subscription-and-hmos-quirks.md](./07-alipay-subscription-and-hmos-quirks.md) §2。

> ⚠️ **总超时不要超过用户耐受**：普通订单建议 ≤15 秒；订阅类极限 60 秒。超过用户会以为 App 卡死。

## 4. 并发双退栈陷阱（通用！）

```
时间线：
T0  用户在微信完成支付
T1  微信回调本 App → aboutToAppear 触发 query (链 A)
T2  onPageShow 触发 → 再触发一次 query (链 B)
T3  链 A 查询成功 → pop()  ← 支付页退出
T4  链 B 查询成功 → pop()  ← 但此时栈顶已经是支付页的上一页，再 pop 多退一级
T5  很可能直接退出 App
```

**必加 `isQueryingPayResult` flag + 清除 orderId 防并发**（见 §2 模板）。这是真实出现过的线上 bug。

### 4.1 HMOS 后台 setTimeout 减速（订阅签约场景特别注意）

普通微信/支付宝 SDK 调起场景，调起 → 用户支付 → 回跳本 App 全过程通常不超过 5 秒，App 在后台时间短，`setTimeout` 减速几乎不影响。

但 **支付宝订阅签约 SCHEME** 场景下（用 `bundleManager.canOpenLink + ctx.openLink` 拉起支付宝 App）用户在外部 App 停留 5-30s，期间本 App 在后台 → `setTimeout` 被减速到约 1/4。如果在 `openLink` 后立刻开始普通轮询，45s 设计窗口实测会拖到 ~180s。

正确模式：`openLink` 后**先挂起等回前台再轮询**，且轮询循环中 sleep 也支持被前台事件中断。完整模板见 [07-alipay-subscription-and-hmos-quirks.md](./07-alipay-subscription-and-hmos-quirks.md) §2。

## 5. 失败自动取消订单

所有失败路径都应调后端 `cancelOrder(orderId)`：
- `onResp` 返回 `errCode != 0`
- `resultStatus` 明确失败（4000）
- 查询重试全部失败
- 用户主动取消

**目的**：
- 避免后端僵尸订单堆积
- 同一商品短时间内可重新下单（订单占用解除）

## 6. 保护窗口：放在写回入口而非支付回调

### 错误做法（常见）

```typescript
// 只在支付成功时写保护时间戳
async onPaySuccess() {
  await setVip(N)
  await setProtectionStartAt(Date.now())
}
```

**问题**：支付后任意页面调 `getUserInfo()` → `setVip(serverValue)` → 本地 VIP 立即被服务端"旧数据"覆盖。

### 正确做法：下沉到 `applyUserInfo`

```typescript
async applyUserInfo(remote: UserInfo): Promise<void> {
  const localVip = await <getLocalVip>()
  const remoteVip = remote.<vipField> ?? 0
  const protectStartAt = await <getProtectStartAt>()
  const PROTECTION_MS = <项目选定，建议 5 分钟>

  // 保护窗口判断
  const withinProtection =
    localVip > 0 &&
    remoteVip === 0 &&
    Date.now() - protectStartAt < PROTECTION_MS

  if (!withinProtection) {
    await <setLocalVip>(remoteVip)
  } else {
    Logger.info(TAG, 'VIP protection: skip downgrade')
  }

  // 其他字段不受保护窗口影响，正常写入
  if (remote.avatar) await <setAvatar>(remote.avatar)
  // ...
}
```

### 为什么下沉

保护窗口的目的是对抗"服务端异步回调晚于客户端下次 getUserInfo"的时序问题。这个风险出现在**所有**触发 `getUserInfo` 的路径，不只是支付回调。下沉到 `applyUserInfo` → 任意路径都受保护。

## 7. 集中化用户信息刷新器

避免每个页面散落 `getUserInfo + applyUserInfo`。

```typescript
export class UserInfoRefresher {
  private static instance: UserInfoRefresher | null = null
  private inFlight: boolean = false
  private lastAt: number = 0
  private readonly throttleMs: number = <项目选定，建议 30_000>

  static getInstance(): UserInfoRefresher {
    if (UserInfoRefresher.instance === null) {
      UserInfoRefresher.instance = new UserInfoRefresher()
    }
    return UserInfoRefresher.instance
  }

  async refreshIfStale(force: boolean = false): Promise<void> {
    // 1. 未登录跳过（getInfo 需要 token）
    if (!await <isLoggedIn>()) return

    // 2. 防并发
    if (this.inFlight) {
      Logger.info(TAG, 'refresh: in flight, skip')
      return
    }

    // 3. 节流（force=true 旁路）
    const now = Date.now()
    if (!force && now - this.lastAt < this.throttleMs) {
      Logger.info(TAG, 'refresh: throttled')
      return
    }

    this.inFlight = true
    try {
      const info = await <api.getUserInfo>()
      await <applyUserInfo>(info)  // 含保护窗口判断
      this.lastAt = Date.now()
      // 可选：广播刷新事件
      <emit USER_INFO_REFRESHED>
    } catch (e) {
      Logger.error(TAG, 'refresh failed: ' + e)
      // 失败不更新 lastAt，允许下次重试
    } finally {
      this.inFlight = false
    }
  }

  /** 支付 / 登录完成后调，让下次刷新立即真发 */
  resetThrottle(): void {
    this.lastAt = 0
  }
}
```

## 8. 关键页的 `onShown` 刷新策略

**问题场景**：用户在设备 A 开通 VIP，本机（设备 B）如何感知？

**解法**：在 VIP / 充值 / 订阅管理等关键页的 `onShown` 强制刷新：

```typescript
// MemberCenterPage.ets
.onShown(() => {
  UserInfoRefresher.getInstance().refreshIfStale(true)  // force=true
})
```

**force=true 原因**：节流是为了防止频繁刷新浪费请求，但用户进入 VIP 相关页说明他此刻关心 VIP 状态——值得发一次真请求。

### 应用清单

建议启用 `onShown → refreshIfStale(true)` 的页面：
- 会员中心 / 开通 VIP 页
- 点数充值页
- 订阅管理 / 退订页
- 账户信息页
- 设置页（显示 VIP 状态的入口）

## 9. 支付完成全链路模板

```typescript
async handlePaySuccess(orderId: string): Promise<void> {
  // 1. 立即写本地状态（不等服务端异步）
  await <setLocalVip>(<新 VIP 等级>)
  await <setProtectionStartAt>(Date.now())

  // 2. 允许刷新器下次立即真发
  UserInfoRefresher.getInstance().resetThrottle()

  // 3. 拉一次服务端最新信息（会经过保护窗口判断）
  await UserInfoRefresher.getInstance().refreshIfStale(true)

  // 4. 广播刷新事件（其他页面监听）
  <emit PAY_SUCCESS>

  // 5. UI 层
  promptAction.showToast({ message: '支付成功' })
  this.pathStack.pop()
}
```

## 10. 常见陷阱清单

| 现象 | 根因 | 解法 |
|---|---|---|
| 支付成功后很快 VIP 变回非 VIP | 服务端异步回调晚于客户端 getUserInfo | 保护窗口下沉到 applyUserInfo |
| 支付页退两次 / 退出 App | 并发 query 未加 flag | isQueryingPayResult flag |
| 僵尸订单堆积 | 失败时未 cancel | 所有失败路径都 cancelOrder |
| 跨设备状态不同步 | 关键页 onShown 未刷新 | refreshIfStale(true) |
| 查询请求过密 | 节流阈值太短 | 建议 30s 节流 + force 旁路 |
| 登出后 refresh 401 | 未登录时仍发请求 | refreshIfStale 开头 isLoggedIn 预检 |
