# 微信支付 SDK 深入细节

本文档聚焦 `@tencent/wechat_open_sdk` 的 **SDK 调起与回调** 细节。前置准备（Ability 集成、module.json5、签名）见 `01-ability-and-config.md`。

## 1. `PayReq` 字段完整规格

```typescript
const payReq = new wxopensdk.PayReq()
payReq.appId        = '<移动应用 AppID，来自开放平台>'
payReq.partnerId    = '<微信支付商户号>'
payReq.prepayId     = '<后端统一下单返回的预支付 ID>'
payReq.nonceStr     = '<随机字符串，后端生成>'
payReq.timeStamp    = '<秒级时间戳字符串>'
payReq.packageValue = 'Sign=WXPay'  // App 支付固定值
payReq.sign         = '<后端按签名规范生成>'
payReq.extData      = '<可选，pass-through 业务数据，通常传 orderId>'
```

**陷阱**：`extData` 会在 `PayResp` 里原样返回，是关联客户端订单和 SDK 回调的最佳途径。

### 字段类型严格要求
- 全部 `string` 类型。后端偶发返回 number 时必须 `.toString()` 强转。
- `packageValue` **不能为空字符串**，App 支付固定 `Sign=WXPay`（Web 支付是 `prepay_id=xxx`，别搞混）。
- `timeStamp` 是**秒级**时间戳（10 位）字符串，不是毫秒。

### 关键陷阱：`timeStamp` 大小写

```typescript
payReq.timeStamp = ...   // ✅ SDK 字段是 camelCase（注意大写 S）
payReq.timestamp = ...   // ❌ 编译报错或运行时被忽略
```

后端 JSON 字段通常小写 `timestamp`，**不要直接 `payReq.timestamp = json.timestamp`**，要 `payReq.timeStamp = json.timestamp`。漏这个映射是新手最高频的"七参没问题但调起失败"原因。

### `package` 字段三层错位（必双兼容）

这个字段从开放平台标准 → 后端响应 → SDK 字段，名字一路在变，必须搞清楚：

| 层 | 字段名 | 来源 |
|----|--------|------|
| 微信开放平台 JSON 标准 | `package` | 微信支付官方文档（[App 支付时序图](https://pay.weixin.qq.com/doc/v3/merchant/4012531349)） |
| **后端响应** | `package` 或 `packageVal` | 取决于商户后端封装；很多后端为了避开 `package` 关键字别名 alias 成 `packageVal` |
| **SDK 字段** | `packageValue` | wxopensdk 自己取的字段名（避免和 JS 关键字 `package` 冲突）|

客户端解析必须**双兼容**：

```typescript
const pkgFromBackend =
  (raw['package'] ?? raw['packageVal'] ?? '').toString();   // 双兼容
payReq.packageValue = pkgFromBackend.length > 0 ? pkgFromBackend : 'Sign=WXPay';
```

### App 支付 vs Web 支付字段大小写差异
- App 支付：小写 `appid / partnerid / prepayid / noncestr / timestamp / package`
- Web 支付（公众号/小程序）：驼峰 `appId / partnerId / prepayId / nonceStr / timeStamp / packageValue`

后端返回时可能混用，客户端必须双解析兼容（见 JSON fallback）。

## 2. 参数双源解析（JSON fallback）

部分后端不返回独立字段，把所有参数塞进一个 `payInfo` JSON 字符串。客户端必须兼容：

```typescript
function parseWechatPayParams(raw: Record<string, Object>): WxPayParams {
  let appid      = (raw.appid ?? '').toString()
  let partnerId  = (raw.partnerId ?? '').toString()
  let prepayId   = (raw.prepayId ?? '').toString()
  let nonceStr   = (raw.nonceStr ?? '').toString()
  let timestamp  = (raw.timestamp ?? '').toString()
  let sign       = (raw.sign ?? '').toString()
  let packageVal = (raw.packageVal ?? '').toString()

  const payInfoStr = (raw.payInfo ?? '').toString()
  if (prepayId.length === 0 && payInfoStr.length > 0) {
    try {
      const info = JSON.parse(payInfoStr) as Record<string, string>
      appid      = (info['appid']     ?? info['appId']                          ?? appid).toString()
      partnerId  = (info['partnerid'] ?? info['partnerId']                      ?? partnerId).toString()
      prepayId   = (info['prepayid']  ?? info['prepayId']  ?? info['prepay_id'] ?? prepayId).toString()
      nonceStr   = (info['noncestr']  ?? info['nonceStr']                       ?? nonceStr).toString()
      timestamp  = (info['timestamp'] ?? info['timeStamp']                      ?? timestamp).toString()
      packageVal = (info['package']   ?? info['packageVal'] ?? info['packageValue'] ?? packageVal).toString()
      sign       = (info['sign']      ?? info['paySign']                        ?? sign).toString()
    } catch (e) { /* log */ }
  }

  return { appid, partnerId, prepayId, nonceStr, timestamp, sign, packageVal }
}
```

**`.toString()` 强转必加**——防御服务端返回 `number` / `boolean` 导致 SDK 参数类型错误（"商家参数格式有误"的次常见原因）。

## 3. `sendReq` 返回类型版本兼容

`@tencent/wechat_open_sdk` 不同版本返回值不同：
- 旧版本（约 1.0.x 早期）：`Promise<boolean>` — true 表示调起成功
- 新版本：`Promise<SendReqResultWrap>` — 含 `result: boolean` / `errMsg` 等字段

兼容写法：

```typescript
async function safeSendReq(
  context: common.UIAbilityContext,
  payReq: wxopensdk.PayReq
): Promise<boolean> {
  const ret = await WXApi.sendReq(context, payReq) as unknown
  if (typeof ret === 'boolean') return ret
  if (ret && typeof ret === 'object' && 'result' in ret) {
    return (ret as { result: boolean }).result
  }
  return false
}
```

集成时先看本项目引入的 SDK 版本 d.ts 里 `sendReq` 签名，再选择合适的解包方式。**`sendReq` 返回成功仅代表"调起微信 App 成功"，不代表支付成功**——支付结果还要靠 `onResp`。

## 4. SDK 错误码速查表

### `sendReq` 失败常见错误

| 现象 | 错误码/日志 | 原因 | 排查 |
|---|---|---|---|
| 返回 false，log `openWechat fail by err:{"code":16000001}` | 16000001 | 设备未安装微信 | 真机调试；模拟器必炸 |
| 返回 false，无日志 | — | 参数格式错 | 检查七参完整、`packageValue` 非空、类型为 string |
| "应用未注册" | — | AppID/Bundle ID/Identifier 任一不对 | 见 `01-ability-and-config.md` §8 |
| "Bundle ID 信息校验不通过" | — | 自动签名 or 开放平台审核未过 | 改手动签名 + 等审核 |
| "商家参数格式有误" | — | prepayId 签名上下文不匹配 | 见本文 §5 |

### `onResp` 的 `errCode`

| errCode | 含义 | 业务动作 |
|---|---|---|
| 0 | 支付成功 | **调后端查询订单真实状态**（不可信 errCode=0）|
| -1 | 普通错误 | 提示失败 + cancel 订单 |
| -2 | 用户取消 | 提示取消 + cancel 订单 |
| -3 | 发送失败 | 检查参数 |
| -4 | 用户拒绝授权 | 登录场景出现，支付不常见 |
| -5 | 不支持错误 | 微信版本不支持 |

### "商家参数格式有误" 排查顺序（80% 问题在第 1 条）

1. **后端下单请求是否透传了商品的 `extJson` / `extStr`** — 后端签发 prepayId 时把该字段编码进签名上下文，客户端不传或传空 → 签名不匹配
2. **七参完整性** — `appId / partnerId / prepayId / nonceStr / timeStamp / packageValue / sign`
3. **类型** — 全部 string，`.toString()` 强转
4. **JSON fallback 大小写兼容** — `prepayid` vs `prepayId` vs `prepay_id` 全覆盖
5. **`packageValue` = `Sign=WXPay`**（App 支付固定值）
6. **`timeStamp` 是秒级**（10 位），不是毫秒
7. 如果使用了三方支付聚合 lib，检查内部路由有没有"路由错误"把微信参数送给了支付宝路径

## 5. 预检安装避免空报错

```typescript
import { bundleManager } from '@kit.AbilityKit'

async function checkWechatBeforePay(): Promise<boolean> {
  if (!bundleManager.canOpenLink('weixin://')) {
    promptAction.showToast({ message: '请先安装微信 App' })
    return false
  }
  return true
}
```

要求 `module.json5` 已声明 `querySchemes: ["weixin"]`。

## 6. 登录与支付回调共存

`SendAuthReq`（登录）和 `PayReq`（支付）共用同一个 `wxEventHandler.onResp`，必须在回调里区分：

```typescript
private onWxResp = (resp: wxopensdk.BaseResp): void => {
  if (resp instanceof wxopensdk.PayResp) {
    // 本页是支付页 → 处理
    // 本页是登录页 → 忽略（return）
  } else if (resp instanceof wxopensdk.SendAuthResp) {
    // 本页是登录页 → 处理
    // 本页是支付页 → 忽略
  }
}
```

如果全局 handler 被多个页面同时订阅，每个页面都应只处理自己关心的 resp 类型，否则事件串。

## 7. 完整调起模板（Page 层）

```typescript
// PayPage.ets（Page struct 内）
private async launchWechatPay(params: WxPayParams): Promise<void> {
  // 1. 预检
  if (!bundleManager.canOpenLink('weixin://')) {
    promptAction.showToast({ message: '请先安装微信' })
    return
  }

  // 2. 构造 PayReq
  const payReq = new wxopensdk.PayReq()
  payReq.appId        = params.appid
  payReq.partnerId    = params.partnerId
  payReq.prepayId     = params.prepayId
  payReq.nonceStr     = params.nonceStr
  payReq.timeStamp    = params.timestamp
  payReq.packageValue = params.packageVal.length > 0 ? params.packageVal : 'Sign=WXPay'
  payReq.sign         = params.sign
  payReq.extData      = params.orderId  // 用于回调关联

  // 3. 调起（必须 Page 层，ViewModel 拿不到 UIAbilityContext）
  try {
    const context = getContext(this) as common.UIAbilityContext
    const ok = await safeSendReq(context, payReq)
    if (!ok) {
      promptAction.showToast({ message: '微信支付调起失败' })
    }
  } catch (e) {
    Logger.error('sendReq error: ' + e.message)
  }
}
```

## 8. 回调到订单查询的衔接

`onResp` 里 `errCode === 0` **不代表支付真的成功**，必须查询后端订单状态确认：

```typescript
private onWxResp = async (resp: wxopensdk.BaseResp): Promise<void> => {
  if (!(resp instanceof wxopensdk.PayResp)) return
  const payResp = resp as wxopensdk.PayResp
  const orderId = payResp.extData  // 取回支付前 pass-through 的 orderId

  if (payResp.errCode === 0) {
    await this.queryPayResult(orderId)  // 见 05-order-lifecycle.md
  } else if (payResp.errCode === -2) {
    await this.cancelOrder(orderId)
    promptAction.showToast({ message: '支付已取消' })
  } else {
    await this.cancelOrder(orderId)
    promptAction.showToast({ message: '支付失败：' + payResp.errStr })
  }
}
```

`extData` 是回调关联业务订单的最佳途径，支付前必存。
