# 支付宝 SDK 深入细节

本文档聚焦 `@cashier_alipay/cashiersdk` 的安装陷阱、完整状态码处理与调起模板。

> **订阅签约 / 周期扣款**（payDetail 形如 `alipays://platformapi/startapp?...`）走的是 **SCHEME 路径**，不是本文这条 SDK 路径。把 SCHEME URI 喂给 `Pay().pay` 会弹"交易订单处理失败"。详见 [07-alipay-subscription-and-hmos-quirks.md](./07-alipay-subscription-and-hmos-quirks.md) §1。

## 1. 安装陷阱（按发生频率排序）

### 陷阱 1：`useNormalizedOHMUrl` 未开启

```
hvigor ERROR: Bytecode HARs: [@cashier_alipay/cashiersdk] not supported
when useNormalizedOHMUrl is not true
```

**解法**：项目级 `build-profile.json5` 每个 product 节点下添加：

```json5
{
  "app": {
    "products": [{
      "name": "default",
      "useNormalizedOHMUrl": true
    }]
  }
}
```

### 陷阱 2：间接依赖下载失败

常见报错：

```
missing: @alipay/blueshieldsdk, required by @cashier_alipay/cashiersdk
ENOENT: no such file or directory ... blueshieldsdk-*.har
ENOENT: no such file or directory ... utdid_sdk-*.har
```

**解法**（按成本从低到高）：
1. 删除所有 `oh-package-lock.json5`，重新 `ohpm install`
2. DevEco Studio：`File → Invalidate caches`，勾选全部三项，清理后重启
3. 手动 `ohpm install @alipay/blueshieldsdk` 单独装
4. 换 ohpm 源（如果走代理/镜像）

### 陷阱 3：Release 模式不能拉起

现象：Debug 模式能拉起支付宝 App，切到 Release（混淆 + 签名）后跳不过去。

**原因**：DevEco Studio 早期版本的混淆规则对支付宝 SDK 不友好。

**解法**：升级 DevEco Studio 到较新版本；或在 `obfuscation-rules.txt` 里为支付宝 SDK 加 keep 规则：

```
-keep-property-name
# 保留 cashiersdk 相关类名
-keep @cashier_alipay/cashiersdk/**
-keep @alipay/blueshieldsdk/**
```

实际 keep 规则写法随 DevEco 版本变化，参考官方最新文档。

## 2. `Pay.pay()` 完整签名

```typescript
import { Pay } from '@cashier_alipay/cashiersdk'

const result: Map<string, string> = await new Pay().pay(orderInfo, showLoading)
//                                              ^                ^
//                                              |                第二参数：true=显示SDK内置Loading
//                                              后端返回的已签名 orderInfo 串
```

**返回值是 `Map<string, string>`**，通过 `result.get(key)` 读值。常用 key：
- `'resultStatus'`: 主结果码
- `'memo'`: 备注信息
- `'result'`: 原始结果字符串（含支付宝服务端 JSON，可用于深度诊断；见 §5）

### 双形态返回：throw + Map with error 都要处理

`Pay().pay(...)` 的 reject 路径**两条都可能命中**——参数解析失败 / SDK 初始化失败会 **throw**；用户取消、网络异常会 **return Map** 但 `resultStatus` 是失败码。两条都得 catch：

```typescript
let result: Map<string, string>;
try {
  result = await new Pay().pay(orderInfo, true);
} catch (e) {
  // 路径 A：SDK 直接 throw（SDK 内部初始化或参数严重错误）
  // 用 JSON.stringify 完整 dump，因为 Error.message 经常吞 backend reason
  const m = e instanceof Error ? e.message : String(e);
  let raw: string;
  try { raw = JSON.stringify(e); } catch (_) { raw = m; }
  console.warn(`[alipay] Pay().pay THROW msg=${m} raw=${raw}`);
  return { state: 'failed', message: '支付宝调起失败' };
}
// 路径 B：拿到 Map，但 resultStatus 可能是 4000 / 6001 / ... → 按 §3 表分发
```

### 完整 dump Map 内容（诊断必备）

`result.get('resultStatus')` / `'memo'` 不够——出疑难杂症时要看 SDK 是否塞了自定义 key，以及 `result` 字段里的支付宝服务端 JSON：

```typescript
const status = result.get('resultStatus') ?? '';
const memo = result.get('memo') ?? '';
const resultDetail = result.get('result') ?? '';

// 列出所有 key（包含 SDK 自定义 key）
const allKeys: string[] = [];
result.forEach((_v: string, k: string) => allKeys.push(k));
console.info(
  `[alipay] resultStatus='${status}' memo='${memo}' ` +
  `result.len=${resultDetail.length} allKeys=[${allKeys.join(',')}]`
);

// 完整 dump result 字段不截断（含 alipay_trade_app_pay_response 子结构，定位 sub_code/sub_msg 必备）
if (resultDetail.length > 0) {
  console.info(`[alipay] result FULL=${resultDetail}`);
}
```

详见 [07-alipay-subscription-and-hmos-quirks.md](./07-alipay-subscription-and-hmos-quirks.md) §4 的 `alipay_trade_app_pay_response` 解析模板和 ACQ.* sub_code 速查。

## 3. `resultStatus` 完整对照表

| 状态码 | 含义 | 客户端动作 |
|---|---|---|
| `'9000'` | 订单支付成功 | 查后端订单确认 + handlePaySuccess |
| `'8000'` | 正在处理中，支付结果未知 | **⚠️ 必须主动查询订单状态**，不能当失败 |
| `'6001'` | 用户取消 | cancel 订单 + toast "已取消" |
| `'6002'` | 网络连接出错 | 重试或提示 |
| `'6004'` | 支付结果未知，需查询 | **⚠️ 和 8000 同等对待，查询订单** |
| `'4000'` | 订单支付失败 | cancel 订单 + toast 失败 |
| `'5000'` | 重复请求 | 提示用户 |
| 其他 | 其他失败 | 归为失败 |

**关键错误**：很多项目只判断 9000/6001/4000 三态，忽略 8000/6004 → 明明付了钱显示失败 → 投诉。

## 4. 标准处理模板

```typescript
async function handleAlipayResult(
  result: Map<string, string>,
  orderId: string
): Promise<void> {
  const status = result.get('resultStatus') ?? ''
  const memo = result.get('memo') ?? ''
  Logger.info(TAG, `alipay result: status=${status}, memo=${memo}`)

  switch (status) {
    case '9000':
      // 支付成功：仍需后端查询确认（不能单独相信 SDK 返回）
      await queryOrderWithRetry(orderId)
      break

    case '8000':
    case '6004':
      // 处理中状态：必须主动查询
      promptAction.showToast({ message: '正在确认支付结果...' })
      await queryOrderWithRetry(orderId)
      break

    case '6001':
      await cancelOrder(orderId)
      promptAction.showToast({ message: '支付已取消' })
      break

    case '4000':
    default:
      await cancelOrder(orderId)
      promptAction.showToast({ message: '支付失败' })
      break
  }
}
```

## 5. 输入选择：`orderInfo` vs `zftUrl`

后端通常同时返回：
- `orderInfo`: SDK 标准签名串（推荐用这个）
- `zftUrl`: 直付通 H5 URL（兜底）

优先级：

```typescript
const payString = (orderResult.orderInfo?.length ?? 0) > 0
  ? orderResult.orderInfo
  : (orderResult.zftUrl ?? '')

if (payString.length === 0) {
  onFail('支付参数为空')
  return
}

const result = await new Pay().pay(payString, true)
```

## 6. 调起前预检（可选）

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

要求 `module.json5` 已声明 `querySchemes: ["alipay", "alipays"]`。

SDK 内部对未安装场景有兜底——会走 H5 收银台——所以预检非强制，但如果要给用户明确提示"请先安装支付宝"则需要。

## 7. 安全边界

> **SDK 调起成功 ≠ 支付真实成功**

`resultStatus === '9000'` 也不能单独作为 VIP/点数到账依据，仍需：
1. 后端验签：`result.get('result')` 里含服务端签名，本地不要自己验，送后端
2. 后端查询订单：以服务端订单状态为最终真相源

客户端行为对付了但没到账的投诉敏感，**永远不要跳过后端确认**。

## 8. `notifyUrl` 必填

后端生成 `orderInfo` 时**必须包含 `notify_url` 参数**（放在 method 之后，因为签名需要按 key 排序）。

缺 `notify_url` → 支付成功后支付宝不会回调商户服务器异步通知 → 订单永远悬挂"已付未到账"状态。

这是后端责任，但前端调试时如果发现"支付显示成功但点数/VIP 没到账"，第一反应应该是查后端 notify_url 配置。

## 9. 完整调起模板（Page 层）

```typescript
// PayPage.ets 内
private async launchAlipay(orderInfo: string, orderId: string): Promise<void> {
  if (orderInfo.length === 0) {
    promptAction.showToast({ message: '支付参数为空' })
    return
  }

  try {
    const result = await new Pay().pay(orderInfo, true)
    await this.handleAlipayResult(result, orderId)
  } catch (e) {
    const msg = (e instanceof Error) ? e.message : String(e)
    Logger.error(TAG, 'alipay threw: ' + msg)
    await this.cancelOrder(orderId)
    promptAction.showToast({ message: '支付宝调起失败' })
  }
}
```

注意：`new Pay().pay(...)` 在 ArkTS 中**不需要 `UIAbilityContext`**（和微信 SDK 不同），所以理论上可以在 ViewModel 调——但为了架构一致性建议也放 Page 层。
