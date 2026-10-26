---
name: arkts-payment
description: ArkTS/HarmonyOS 第三方支付通用集成技能（与生态无关）。专注于微信支付 SDK、支付宝 SDK、H5 支付 WebView 容器、跨 App 跳转、华为 IAP 选型等平台级能力与协议约束，不绑定任何特定后端字段/私有 lib。当用户需要从零集成第三方支付、接入 wxopensdk 或 cashiersdk、构建通用 H5 支付容器、适配 HarmonyOS WebView 支付白屏问题、设计保护窗口与订单查询重试策略、决策 IAP vs 三方 SDK 时使用此技能。也适用于新项目脚手架阶段、跨项目支付代码提炼、或当项目未使用 lib_payment/lib_common 等私有库时。**调试场景触发**：'商家参数格式有误'、'微信 H5 白屏'、'支付回调不触发'、'scheme 跳不过去'、'UIAbilityContext 找不到'、'Bundle ID 校验不通过'、'应用未注册'等。关键词：pay、payment、wxpay、alipay、third-party、cashier、sdk、webview、scheme、H5、IAP。本 skill 为通用平台方案（与生态无关）；如有项目专属生态版本另行集成。
metadata:
  type: domain
  domain: system
  tags:
  - payment
  - wechat-pay
  - alipay
  - webview
  - sdk
  - generic
  - third-party
  - iap
---
# ArkTS 第三方支付通用集成指南

**不绑定任何特定后端/私有 lib** 的第三方支付集成方案，专注于 HarmonyOS 平台约束与微信/支付宝/华为 IAP 的官方协议要求。

本文档是索引；细节模板在 `references/` 下。

## 适用范围

**覆盖**:
- `@tencent/wechat_open_sdk` 调起 + 回调 + 模块配置
- `@cashier_alipay/cashiersdk` 调起 + 状态码 + 安装陷阱
- **支付宝订阅签约 SCHEME 路径**（周期扣款 / "先签后付"，`alipays://...` URI 拉起）
- H5 支付 WebView 容器（UA / Referer / scheme / 回跳 / JS Bridge）
- 支付宝 H5 表单提交
- 华为 IAP 选型决策（何时必须用 IAP）
- 订单结果查询通用模式（重试 / 防并发 / 失败兜底）
- **HMOS 跨 App 跳转特殊问题**（后台 setTimeout 减速 / onForeground 唤醒 / 业务回跳 scheme 注册）
- **支付宝 sub_code 深度诊断**（ACQ.* 错误码族 / `alipay_trade_app_pay_response` 解析）
- 用户状态保护窗口原则

**不覆盖**:
- 具体业务后端的字段/路径 — 由项目和后端协商（见"后端契约检查清单"）
- 华为 IAP 完整集成代码 — 参考华为官方 Codelab
- VIP 分层/点数模型

## 架构约束（硬约束）

三层分离源于 HarmonyOS 平台特性：

```
Page 层     — 持有 UIAbilityContext，调 wxopensdk.sendReq
ViewModel 层 — 编排 + 存参 + 提供 onSuccess 回调给 Page
Service 层  — 网络调用 + 失败抛异常
```

**硬约束来源**：`wxopensdk.WXAPIFactory.createWXAPI(appid).sendReq(context, payReq)` 的 `context` 必须是 `common.UIAbilityContext`（`getContext(this) as common.UIAbilityContext`）。ViewModel 拿不到，**SDK 一定要在 Page 层调**。

## SDK 依赖

集成前查 [ohpm.openharmony.cn](https://ohpm.openharmony.cn/) 取最新版本：

```json5
{
  "dependencies": {
    "@tencent/wechat_open_sdk": "<check-latest>",
    "@cashier_alipay/cashiersdk": "<check-latest>"
  }
}
```

⚠️ 版本号用 `'<check-latest>'` 并在 ohpm.openharmony.cn 核实最新版，不写死（支付 SDK 跟随微信/支付宝后端升级）。

`build-profile.json5` 必须 `useNormalizedOHMUrl: true`，否则支付宝 SDK 报错。详见 [references/01-ability-and-config.md](references/01-ability-and-config.md) §2。

## 集成四步法

按顺序做。任意一步缺失 → 后续步骤必挂。

| 步 | 内容 | 详细文档 |
|---|---|---|
| 1️⃣ | Ability 集成 + module.json5 + WXApi 单例 + EventHandler | [01-ability-and-config.md](references/01-ability-and-config.md) §1-7 |
| 2️⃣ | 开放平台配置 + 手动签名 + appIdentifier | [01-ability-and-config.md](references/01-ability-and-config.md) §8-9 |
| 3️⃣ | 选型：三方 SDK vs 华为 IAP | [06-huawei-iap-selection.md](references/06-huawei-iap-selection.md) |
| 4️⃣ | 支付路径集成（见下表） | 路径对应文档 |

### 第 1 步关键检查清单

- [ ] `module.json5` 声明 `querySchemes: ["weixin", "wxopensdk", "alipay", "alipays"]`
- [ ] `module.json5` 含 `ohos.permission.INTERNET`
- [ ] EntryAbility `onCreate` + `onNewWant` **都调了 `WXApi.handleWant(want, handler)`**（漏此步 → `onResp` 永远不触发）
- [ ] `WXAPIFactory.createWXAPI(APP_ID)` 的 AppID 是**移动应用** AppID（非小程序 AppID）
- [ ] `WXApiEventHandler` 实现 `onReq` + `onResp` 双方法
- [ ] `build-profile.json5` 开启 `useNormalizedOHMUrl`

### 第 2 步关键检查清单

- [ ] 禁用 IDE 自动签名，改手动签名（固定证书）
- [ ] 微信开放平台 Bundle ID 与 `AppScope/app.json5` `bundleName` 严格一致（大小写敏感）
- [ ] 微信开放平台 Identifier = `bundleManager.getBundleInfoForSelf()` 的 `signatureInfo.appIdentifier`
- [ ] 审核通过后才能调 SDK（审核期必报 "Bundle ID 校验不通过"）

## 五条支付路径

| 路径 | 场景 | 核心约束 | 详细模板 |
|---|---|---|---|
| A | 微信原生 SDK | 7 参齐全、`packageValue='Sign=WXPay'`、`extData` 传 orderId | [02-wechat-sdk-details.md](references/02-wechat-sdk-details.md) |
| B | 微信 H5（WebView）| UA 伪装 + Referer + scheme 拦截 + 返回 pop | [04-h5-container.md](references/04-h5-container.md) |
| C | 支付宝 SDK（标准买断）| `resultStatus` 含 9000/8000/6001/6004/4000 全状态 | [03-alipay-sdk-details.md](references/03-alipay-sdk-details.md) |
| D | 支付宝 H5 表单 | orderInfo 必须 `decodeURIComponent` 再转义 | [04-h5-container.md](references/04-h5-container.md) §7 |
| **E** | **支付宝 SCHEME**（订阅签约 / 周期扣款 / "先签后付"）| `payDetail` 形如 `alipays://platformapi/startapp?...`，**必须**用 `bundleManager.canOpenLink + ctx.openLink`，**禁止**塞给 `Pay().pay`（弹"交易订单处理失败"）| [07-alipay-subscription-and-hmos-quirks.md](references/07-alipay-subscription-and-hmos-quirks.md) §1 |

> ⚠️ **路径 C vs E 的判定**：同一个支付宝预下单接口对**不同商品类型**返回不同形态的支付串。识别后再 fork：
> - `payDetail.startsWith('alipays://')` 或后端字段命中 `appScheme/scheme/2` → 路径 E
> - 其他（标准 query 串 `app_id=xxx&biz_content=...`）→ 路径 C
> 详见 [07 §1.2 路径判定写法](references/07-alipay-subscription-and-hmos-quirks.md)。

### 核心代码骨架（Page 层）

```typescript
// 调起前 ViewModel 已存好参数（wxSdkPayInfo 或 alipayOrderInfo）
private async onPaySuccess(): Promise<void> {
  if (this.vm.wxSdkPayInfo) {
    const p = this.vm.wxSdkPayInfo; this.vm.wxSdkPayInfo = null
    const payReq = new wxopensdk.PayReq()
    payReq.appId = p.appid
    payReq.partnerId = p.partnerId
    payReq.prepayId = p.prepayId
    payReq.nonceStr = p.nonceStr
    payReq.timeStamp = p.timestamp
    payReq.packageValue = p.packageVal.length > 0 ? p.packageVal : 'Sign=WXPay'
    payReq.sign = p.sign
    payReq.extData = p.orderId
    const context = getContext(this) as common.UIAbilityContext
    await WXApi.sendReq(context, payReq)
  } else if (this.vm.wxH5PayInfo) {
    // → 跳转 WebView 页
  } else if (this.vm.alipayOrderInfo) {
    const result = await new Pay().pay(this.vm.alipayOrderInfo, true)
    await this.handleAlipayResult(result, this.vm.orderId)
  }
}
```

## 选型：三方 SDK vs 华为 IAP

**上架华为应用市场 + 卖虚拟商品** → 必须用 IAP（政策）。其他场景可选。

| 场景 | 推荐 |
|---|---|
| 虚拟商品（VIP/点数/道具）+ 华为应用市场 | IAP |
| 订阅型自动续费 | IAP |
| 多端统一（iOS/Android/HarmonyOS）| 三方 SDK |
| 实物商品/线下服务 | 三方 SDK |

详细决策树见 [06-huawei-iap-selection.md](references/06-huawei-iap-selection.md)。

## H5 容器 4 要素

微信/支付宝 H5 网关对 WebView 有 4 项硬要求，任意一项缺失 → 白屏：

1. **UA 伪装**：`Web.userAgent(PAYMENT_USER_AGENT)`（标准 Android Chrome UA）
2. **Referer 注入**：`onControllerAttached` 里 `loadUrl(url, [{Referer: h5Domain}])`
3. **Scheme 拦截**：`onLoadIntercept` 捕获 `weixin://`/`alipays://`/`alipay://`
4. **返回后关闭**：`hasLaunchedExternalApp` flag + `onAppear` 检测

完整容器模板 + JS Bridge + 返回按钮劫持脚本 + Safe-area 三态 → [04-h5-container.md](references/04-h5-container.md)。

## 支付结果查询

**核心原则**：SDK 回调 / `errCode` / `resultStatus` **都不能单独判定支付成功**。唯一真相源是**后端订单查询**。

```typescript
// 基本骨架（细节见 references/05-order-lifecycle.md）
private isQueryingPayResult = false
async queryPayResult(orderId: string): Promise<void> {
  if (this.isQueryingPayResult) return  // ⚠️ 并发防护必加
  this.isQueryingPayResult = true
  try {
    await this.queryWithRetry(orderId, <retries>, <intervalMs>)
  } finally {
    this.isQueryingPayResult = false
  }
}
```

**关键陷阱**：`onPageShow` + SDK 回调并发触发 → 不加 flag 会产生双退栈 → 退出 App。

重试 + 失败兜底 + `cancelOrder` 调用时机 → [05-order-lifecycle.md](references/05-order-lifecycle.md)。

## 用户状态同步原则

**保护窗口必须下沉到 `applyUserInfo()`**，不是只在支付回调写时间戳。否则任意一次 `getUserInfo()` 都会把本地 VIP 状态刷回服务端"旧数据"。

```typescript
// 正确位置
async applyUserInfo(remote: UserInfo) {
  const protectActive = localVip > 0 && remoteVip === 0 &&
                        Date.now() - protectStartAt < PROTECTION_MS
  if (!protectActive) await setLocalVip(remoteVip)
}
```

集中化刷新器 + `onShown → refreshIfStale(true)` 感知跨端开通 → [05-order-lifecycle.md](references/05-order-lifecycle.md) §7-8。

## 前置校验

支付按钮 onClick 第一步必做：

```typescript
if (!await isLoggedIn()) { navigateToLogin(); return }
if (!this.agreementChecked) { this.showAgreementSheet = true; return }
if (isRenewProduct) { ensureRenewAgreement() }  // 周期扣款必须勾选自动续订协议（监管红线）
```

**渠道选择保留**：`updatePayChannels(product)` 会重置 `selectedPayChannel`，必须先存后恢复用户选择。

## 后端契约检查清单

本 skill 不绑定后端。集成前请向后端确认：

| 项 | 示例 | 必确认 |
|---|---|---|
| 预下单接口路径 | `/pay/order/preCreate` | 请求/响应结构 |
| 订单状态查询路径 | `/pay/order/queryStatus` | 返回码定义 |
| 取消订单路径 | `/pay/order/cancel` | 失败兜底 |
| 商品 `extJson` | — | 客户端是否需要回传到预下单 |
| 客户端能力码字段 | `pcu` / `clientPayType` | 字段名与位语义 |
| 渠道位掩码 | `paymentChannel` | 各 bit 对应渠道 |
| `extStr` 进签名上下文 | — | 强 YES（不传会导致"商家参数格式有误"）|
| 微信参数返回形态 | 独立字段 or `payInfo` JSON | 客户端必须双兼容 |
| 成功判定字段 | `status === 0` / `code === 'OK'` | 响应判断 |
| 订单状态码定义 | `payStatus: 0=待 1=成` | 值对应含义 |
| `notify_url` | — | 必填（缺则支付成功但后端不回调）|

## 通用陷阱清单（按严重度）

### 🔴 致命 — 不处理必炸

1. **SDK 调起成功 ≠ 支付真实成功** — 必须后端查询订单状态
2. **EntryAbility 未调 `WXApi.handleWant()`** — `onResp` 永远不触发 → 微信回来像没反应
3. **AppID 填小程序 AppID** — 必报"应用未注册"
4. **IDE 自动签名** — `appIdentifier` 每次变 → Bundle ID 校验失败
5. **微信开放平台审核未过** — 调用时必报"Bundle ID 校验不通过"（审核期间必现）
6. **ViewModel 试图调 `sendReq`** — 拿不到 `UIAbilityContext`
7. **WebView 默认 UA 含 `ArkWeb`** — 微信 H5 网关拒绝 → 白屏
8. **H5 支付未注入 Referer** — 微信网关强制校验
9. **`packageValue` 为空** — 微信 SDK 拒绝；App 支付固定 `Sign=WXPay`
10. **`useNormalizedOHMUrl: false`** — 支付宝 SDK 编译报错
11. **支付宝 SCHEME URI 喂给 `Pay().pay`** — 弹"交易订单处理失败"；订阅签约必须走 `bundleManager.canOpenLink + ctx.openLink`
12. **HMOS 后台 setTimeout 减速 ~4×** — 用户拉起支付宝期间 App 在后台，`setTimeout` 被减速，订阅签约 45s 窗口实测拖到 180s；必须用 `onForeground → APP_FOREGROUND` 唤醒模式
13. **业务回跳 scheme 漏注册** — 漏 `module.json5 skills.uris` → 支付宝完成签约弹"暂无可用打开方式"
14. **`module.json5` 改完没 clean rebuild** — `skills/querySchemes` 在 HAP 打包时固化，仅 Sync/Reload 不生效

### 🟡 高频 — 工程问题

11. **并发查询双退栈** — `onPageShow` + SDK 回调双触发，必须 `isQueryingPayResult` flag
12. **外部 App 调起失败未复位 `hasLaunchedExternalApp`** — `onAppear` 误 pop
13. **`updatePayChannels` 覆盖用户选择** — 先存后恢复
14. **保护窗口只在支付回调判断** — 必须下沉到 `applyUserInfo`
15. **Login + Pay 共用 `wxopensdk` 回调** — 必须 `instanceof` 区分 `PayResp`/`SendAuthResp`
16. **`aboutToAppear/Disappear` 配对缺失** — 野回调访问已销毁页面
17. **支付失败未调 cancel 接口** — 僵尸订单堆积
18. **支付宝只判 9000/6001/4000** — 漏掉 **8000/6004** 待确认状态 → 用户付了显示失败
19. **后端 `orderInfo` 缺 `notify_url`** — 付款成功但商户服务器不收到回调
20. **JSON 参数未 `.toString()` 强转** — 服务端偶发 number 类型导致 SDK 参数错误

### 🟢 次要

21. **支付宝 `orderInfo` 二次编码** — H5 表单前必须 `decodeURIComponent`
22. **SDK 版本写死** — 跟随微信/支付宝后端升级
23. **虚拟商品未用 IAP** — 华为市场拒审
24. **模拟器调试 `sendReq` 返回 16000001** — 模拟器没装微信；真机测试
25. **`querySchemes` 未声明** — `canOpenLink` 永远返回 false
26. **WebView `loadData` 加载含 `#` URL** — 空白 / 不显示

## 调试指引

| 症状 | 首查位置 |
|---|---|
| "商家参数格式有误" | [02-wechat-sdk-details.md](references/02-wechat-sdk-details.md) §4 排查顺序 |
| "应用未注册" / "Bundle ID 校验不通过" | [01-ability-and-config.md](references/01-ability-and-config.md) §8 |
| 微信 `onResp` 不触发 | [01-ability-and-config.md](references/01-ability-and-config.md) §4 (EntryAbility `handleWant`) |
| 微信 H5 白屏 | [04-h5-container.md](references/04-h5-container.md) §1 4 要素 |
| 支付宝 ohpm 安装失败 | [03-alipay-sdk-details.md](references/03-alipay-sdk-details.md) §1 |
| 支付宝 Release 模式不能拉起 | [03-alipay-sdk-details.md](references/03-alipay-sdk-details.md) §1 陷阱 3 |
| 从微信返回 WebView 不关闭 | [04-h5-container.md](references/04-h5-container.md) §1 要素 4 |
| 支付页退两次 / 退出 App | [05-order-lifecycle.md](references/05-order-lifecycle.md) §4 |
| 支付后 VIP 一会儿又没了 | [05-order-lifecycle.md](references/05-order-lifecycle.md) §6 |
| 华为市场拒审虚拟商品 | [06-huawei-iap-selection.md](references/06-huawei-iap-selection.md) §3 |
| "交易订单处理失败" / payDetail 是 `alipays://` 开头 | [07-alipay-subscription-and-hmos-quirks.md](references/07-alipay-subscription-and-hmos-quirks.md) §1 SCHEME 路径 |
| 订阅签约后轮询 `elapsed=180000+ms` 超时 | [07-alipay-subscription-and-hmos-quirks.md](references/07-alipay-subscription-and-hmos-quirks.md) §2 onForeground 唤醒 |
| 支付宝完成签约弹"暂无可用打开方式" | [07-alipay-subscription-and-hmos-quirks.md](references/07-alipay-subscription-and-hmos-quirks.md) §3 业务回跳 scheme |
| 想知道支付宝具体哪里错（sub_code / ACQ.* 码族） | [07-alipay-subscription-and-hmos-quirks.md](references/07-alipay-subscription-and-hmos-quirks.md) §4 sub_code 诊断 |
| 改了 `module.json5` 重启 App 没生效 | [07-alipay-subscription-and-hmos-quirks.md](references/07-alipay-subscription-and-hmos-quirks.md) §3.3 clean rebuild |

## Reference 索引

- [01-ability-and-config.md](references/01-ability-and-config.md) — 初始化、Ability 集成、module.json5、开放平台配置、签名陷阱
- [02-wechat-sdk-details.md](references/02-wechat-sdk-details.md) — `PayReq` 完整规格（含 `timeStamp` 大小写 + `package` 字段三层错位）、`sendReq` 版本兼容、错误码速查、JSON fallback
- [03-alipay-sdk-details.md](references/03-alipay-sdk-details.md) — cashiersdk 安装陷阱、`resultStatus` 全状态、`Pay.pay` 双形态返回（throw + Map error）、Map 完整 dump 模板
- [04-h5-container.md](references/04-h5-container.md) — WebView 4 要素、JS Bridge、劫持脚本、Safe-area 三态、支付宝 H5 表单
- [05-order-lifecycle.md](references/05-order-lifecycle.md) — 订单查询重试、并发防护、保护窗口、UserInfoRefresher、订阅类轮询窗口建议
- [06-huawei-iap-selection.md](references/06-huawei-iap-selection.md) — IAP 选型决策、PMS vs 非 PMS、合规要点
- **[07-alipay-subscription-and-hmos-quirks.md](references/07-alipay-subscription-and-hmos-quirks.md)** — 支付宝订阅签约 SCHEME 路径 + HMOS 跨 App 跳转特殊问题（后台 setTimeout 减速 / onForeground 唤醒 / 业务回跳 scheme）+ sub_code 深度诊断 + 诊断日志方法论


---

## See Also

- [arkts-login](../arkts-login/SKILL.md) — 同属第三方 SDK 系列（共享 wxopensdk EventHandler 过滤模式）
- [arkts-customer-service](../arkts-customer-service/SKILL.md) / [arkts-ad](../arkts-ad/SKILL.md) — 同系列
- 虚拟商品 + 上架华为市场 → 必须用 IAP（见本文档 §选型决策）
