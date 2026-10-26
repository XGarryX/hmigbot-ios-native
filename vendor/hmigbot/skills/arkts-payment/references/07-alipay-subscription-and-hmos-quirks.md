# 支付宝订阅签约 SCHEME 路径 + HarmonyOS 跨 App 跳转特殊问题

本文档解决在 HarmonyOS NEXT 上接**支付宝订阅类商品**（周期扣款 / "先签后付"）会同时遇到的两组特殊问题，以及一类支付宝 SDK 错误的深度诊断方法。任何接订阅扣款的项目都会踩。

适用情景：
- 支付宝商品类型为 **CYCLE_PAY_AUTH_P**（周期扣款授权）/ **GENERAL_WITHHOLDING**（通用代扣）/"先签后付"试用
- 用户日志里出现 `payDetail` 形如 `alipays://platformapi/startapp?...`
- 客户端日志显示轮询 `elapsed=180000+ms` 跑超时
- 弹"交易订单处理失败"且抓不到 SDK 错误码细节

---

## §1 支付宝订阅签约 SCHEME 路径

### 1.1 何时走 SCHEME（而非标准 SDK 路径）

支付宝同一个预下单接口对**不同商品类型**返回不同形态的支付串。如果客户端不识别就硬塞 `Pay().pay()` → 弹 **"交易订单处理失败"**（SDK 不识别 scheme，但只在内部日志里抛错）。

| 商品类型 | payDetail 形态 | 拉起方式 |
|---------|---------------|---------|
| 普通买断（exchange=1）| `app_id=xxx&biz_content=...&sign=...` 标准 orderInfo query 串 | `new Pay().pay(orderInfo, true)` |
| 订阅签约（exchange=2 + deduct=2 / 周期扣款 / 先签后付）| `alipays://platformapi/startapp?appId=60000157&...&sign_params=...` SCHEME URI | `bundleManager.canOpenLink + UIAbilityContext.openLink` |

> 这是支付宝**开放平台标准行为**，不是某个项目的特殊设计。任何用 cashiersdk 接周期扣款的项目都会遇到。

### 1.2 路径判定写法（兼容多形态字段名）

后端可能用任何字段名告诉客户端"这单走哪条路径"——`payAwakeningType` / `payType` / `awakeType` / `payChannel` 都见过；甚至完全不告诉客户端，让客户端自己判断。**最稳的写法是不依赖单一字段，组合判定**：

```typescript
function isAlipayScheme(payDetail: string, hintField?: string): boolean {
  // 1. 后端字段命中（兼容多种命名 / 大小写 / 数字与字符串）
  const t = (hintField ?? '').toLowerCase();
  if (t === 'appscheme' || t === 'scheme' || t === '2') return true;

  // 2. 兜底：payDetail 以 alipays:// 开头一定是 SCHEME
  if (payDetail.startsWith('alipays://')) return true;

  return false;
}
```

为什么兜底必加：
- 后端字段名经常变（迁移期 `payAwakeningType` 类型可能从 `number` 改成 `string` `"appScheme"`）
- 部分商品后端不下发 hint 字段，靠 `payDetail.startsWith('alipays://')` 才能识别

### 1.3 SCHEME 拉起完整模板

```typescript
import bundleManager from '@ohos.bundle.bundleManager';
import common from '@ohos.app.ability.common';
import { promptAction } from '@kit.ArkUI';

async function startAlipayAppScheme(
  payDetail: string,
  orderId: string,
  context: common.UIAbilityContext,
): Promise<{ ok: boolean; reason?: string }> {
  // 1. 检查支付宝是否安装
  //    实际是检查系统能否处理 alipays:// scheme。
  //    要求 module.json5 已声明 querySchemes: ["alipays"]。
  let installed = false;
  try {
    installed = bundleManager.canOpenLink('alipays://');
  } catch (e) {
    console.warn(`canOpenLink threw: ${e}`);
  }
  if (!installed) {
    promptAction.showToast({ message: '请先安装支付宝' });
    return { ok: false, reason: 'not_installed' };
  }

  // 2. context.openLink 拉起支付宝 App
  //    返回 Promise<void>，成功 ≠ 用户真完成了交互（仅代表 AMS 派发成功）
  try {
    await context.openLink(payDetail, undefined);
  } catch (e) {
    const m = e instanceof Error ? e.message : String(e);
    console.warn(`openLink failed: ${m}`);
    return { ok: false, reason: m };
  }

  // 3. 拉起后挂起等待用户回 App，再开始轮询订单状态（见 §2）
  return { ok: true };
}
```

### 1.4 反例：把 SCHEME URI 喂给 `Pay().pay`

```typescript
// ❌ 错：弹"交易订单处理失败"
const result = await new Pay().pay('alipays://platformapi/startapp?...', true);

// ✅ 对：fork 决策
if (isAlipayScheme(payDetail, hint)) {
  await startAlipayAppScheme(payDetail, orderId, ctx);
} else {
  const result = await new Pay().pay(payDetail, true);
}
```

错误根因：cashiersdk 内部按 query 串解析 `payDetail`，遇到 scheme 形态找不到 `app_id` / `sign` 等字段直接放弃，但只在内部日志抛错，对外只返"交易订单处理失败"——非常误导。

---

## §2 HarmonyOS 跨 App 跳转的特殊问题

### 2.1 现象：后台 setTimeout 被减速 ~4×

订单轮询日志典型表现：

```
[poll] start orderId=xxx maxTimes=30 (期望 45s 窗口)
[poll] #1/30 elapsed=1500ms
[poll] #5/30 elapsed=22500ms
[poll] #15/30 elapsed=70000ms    ← 后台被减速
...
[poll] timeout orderId=xxx after 180116ms (30 iterations)
```

**根因**：HarmonyOS NEXT 在 App 进入后台后会对 `setTimeout` 做节能处理，实测频率掉到大约 1/4。45s 设计窗口被拖到 ~180s。

**触发场景**：用户从本 App 拉起支付宝 App 完成签约——此期间本 App 整段都在后台。

> 这是 HMOS 平台行为，与微信/支付宝 SDK 无关。Android 上不存在。

### 2.2 解决思路：onForeground 唤醒 + 可中断 sleep

把"等待用户回 App"和"轮询订单状态"从单一 sleep 链路拆成两阶段：

1. **拉起后挂起**——不立刻轮询，让 App 待机
2. **回前台唤醒**——监听 `EntryAbility.onForeground`，前台时启动轮询；轮询过程中也能被前台事件中断 sleep（兼顾用户离开支付宝后再次回来的边界情况）

完整流程图：

```
ctx.openLink(alipays://...)        ← 拉起支付宝
  │
  ▼
waitForForeground(5min)            ← 挂起，监听 APP_FOREGROUND
  │  (用户在支付宝里 5-30s)
  ▼
EntryAbility.onForeground()        ← 用户跳回本 App
  └─ EventBus.post(APP_FOREGROUND) ← 广播事件
  │
  ▼
waitForForeground 收到 → resolve(true)
  │
  ▼
pollOrderStatus(orderId, isSubscribe=true)   ← 这时 App 在前台，setTimeout 正常
  │
  └─ 每轮 sleep 期间也监听 APP_FOREGROUND
       （兼顾用户中途又切去支付宝再回来的情况）
```

### 2.3 三段式实现模板

**Step 1 — `EntryAbility` 广播 APP_FOREGROUND 事件**：

```typescript
// EntryAbility.ets
import { EventBus } from '../events/EventBus';

interface AppForegroundPayload { from: string }
const APP_FOREGROUND = 'app:foreground';

onForeground(): void {
  // 用户从支付宝/微信/任意外部 App 跳回时触发
  EventBus.post<AppForegroundPayload>(APP_FOREGROUND, { from: 'foreground' });
  console.info('[EntryAbility] onForeground → post APP_FOREGROUND');
}
```

**Step 2 — `waitForForeground` 挂起等回前台**：

```typescript
function waitForForeground(maxWaitMs: number): Promise<boolean> {
  return new Promise<boolean>((resolve) => {
    let done = false;
    const cleanup = (woken: boolean): void => {
      if (done) return;
      done = true;
      EventBus.off<AppForegroundPayload>(APP_FOREGROUND, listener);
      resolve(woken);
    };
    const listener = (_data: AppForegroundPayload): void => cleanup(true);
    EventBus.on<AppForegroundPayload>(APP_FOREGROUND, listener);
    // 兜底超时（用户长时间在外部 App 的极端情况）
    setTimeout(() => cleanup(false), maxWaitMs);
  });
}
```

**Step 3 — `sleepInterruptible` 让轮询期间也能被唤醒**：

```typescript
/**
 * 可中断 sleep：要么自然超时，要么外部通过 register 拿到的 resolve 提前唤醒。
 *
 * @param register 把内部 resolve 函数交给调用方，调用方在外部事件触发时调它即可中断 sleep
 */
function sleepInterruptible(
  ms: number,
  register: (resolve: () => void) => void,
): Promise<void> {
  return new Promise<void>((resolve) => {
    let done = false;
    const onceResolve = (): void => {
      if (done) return;
      done = true;
      resolve();
    };
    register(onceResolve);             // 把 resolve 暴露给外部（监听 APP_FOREGROUND）
    setTimeout(onceResolve, ms);       // 自然超时兜底
  });
}
```

### 2.4 整合到轮询主循环

```typescript
async function pollOrderStatusForSubscribe(orderId: string): Promise<PayResult> {
  // 监听 APP_FOREGROUND 让 sleep 可中断
  let foregroundResolve: (() => void) | undefined;
  const onForegroundListener = (_d: AppForegroundPayload): void => {
    if (foregroundResolve) {
      const r = foregroundResolve;
      foregroundResolve = undefined;
      r();   // 立刻唤醒下一轮查询
    }
  };
  EventBus.on<AppForegroundPayload>(APP_FOREGROUND, onForegroundListener);

  try {
    for (let i = 0; i < POLL_MAX_TIMES_SUBSCRIBE; i++) {
      const st = await api.queryOrderStatus(orderId);
      if (isSuccess(st)) return { state: 'paid', orderId };
      if (isCanceled(st)) return { state: 'cancelled', orderId };

      // 关键：可中断 sleep
      await sleepInterruptible(POLL_INTERVAL_MS, (resolve) => {
        foregroundResolve = resolve;
      });
    }
    return { state: 'unknown', orderId, message: '轮询超时' };
  } finally {
    EventBus.off<AppForegroundPayload>(APP_FOREGROUND, onForegroundListener);
  }
}
```

### 2.5 主入口编排

```typescript
async function payWithAlipayScheme(
  payDetail: string,
  orderId: string,
  ctx: common.UIAbilityContext,
): Promise<PayResult> {
  const open = await startAlipayAppScheme(payDetail, orderId, ctx);   // §1.3
  if (!open.ok) {
    return { state: 'failed', orderId, message: open.reason ?? '拉起支付宝失败' };
  }

  // ★ 不立刻轮询：先挂起等回前台
  await waitForForeground(5 * 60 * 1000);       // 5 分钟兜底

  // 此刻 App 在前台，setTimeout 速度正常
  promptAction.showToast({ message: '正在校验订单，请稍后' });
  return await pollOrderStatusForSubscribe(orderId);
}
```

### 2.6 订阅类轮询窗口建议值

| 场景 | 间隔 | 次数 | 总窗口 |
|------|------|------|--------|
| 普通会员买断 / 积分订单 | 1.5s | 8 | 12s |
| **订阅签约 SCHEME** | **1.5s** | **30** | **45s** |

订阅类需要更长是因为：
- 用户在支付宝完成签约通常 5-30s（含登录、确认协议、生物识别）
- 后端 `payStatus: unsigned → signed` 落库可能延迟几秒
- 配合 `sleepInterruptible`，实际很多用户在 10-15s 内就能拿到结果

---

## §3 业务回跳 scheme（return_url）的"信号"语义

### 3.1 支付宝 biz_content 里的 return_url 是什么

支付宝周期扣款 SCHEME URI 的 `biz_content` 字段（解码后）会包含：

```json
{
  "external_logon_id": "xxx",
  "return_url": "iccapp://com.frx.trywellness/returnApp",   // ← 商户自定义回跳 scheme
  ...
}
```

支付宝完成签约/取消签约后，会拉起这个 `return_url`。这是支付宝**开放平台标准能力**，等价于 OAuth 的 redirect_uri。

> 具体 scheme 名（`iccapp` / `myapp` / `xyz`）由商户后端在生成 biz_content 时自选；客户端要做的是**注册**这个 scheme 让系统能把回跳分发到本 App。

### 3.2 module.json5 注册（**`skills` 而非 `querySchemes`**）

注意区分：
- `querySchemes` — 让本 App **能拉起**别的 App（出站）
- `skills.uris` — 让本 App **能被拉起**（入站）

回跳 scheme 是入站：

```json5
{
  "module": {
    "querySchemes": [
      "weixin", "wxopensdk",
      "alipay", "alipays"               // 让 canOpenLink('alipays://') 返 true
    ],
    "abilities": [{
      "name": "EntryAbility",
      "skills": [
        // 启动 entry
        { "actions": ["ohos.want.action.home"], "entities": ["entity.system.home"] },
        // 微信回跳（已有）
        { "actions": ["wxentity.action.open"] },
        // ★ 业务回跳 scheme（必须）
        {
          "actions": ["ohos.want.action.viewData"],
          "uris": [
            { "scheme": "iccapp", "host": "com.frx.trywellness" }
          ]
        }
      ]
    }]
  }
}
```

漏注册 → 支付宝完成签约后弹 **"暂无可用打开方式"**，且 ArkTS 端抓不到任何错误（这是支付宝 App 内部弹的）。

### 3.3 改完必须 clean rebuild（HMOS 编译行为）

`module.json5` 的 `skills` / `querySchemes` 在 **HAP 打包时被固化**，热加载读不到：

> ⚠️ 改完后必须：`Invalidate Caches → 重打包 → 重新签名 → 安装` —— 仅 Sync / Reload 不生效。

这是 HMOS 平台编译行为，不是 IDE 问题。新接支付的项目 80% 第一次会卡在"为什么我改了 module.json5 还是弹暂无可用打开方式"。

### 3.4 onNewWant 处理：识别为"我回来了"信号，**不要做路由跳转**

```typescript
// EntryAbility.ets
onNewWant(want: Want, launchParam: AbilityConstant.LaunchParam): void {
  // 微信支付回跳必转
  try { WXApi.handleWant(want, wxEventHandler); } catch (_) {}

  if (!want.uri || want.uri.length === 0) return;

  // ★ 业务回跳 scheme：仅作"我回来了"信号，不需要路由跳转
  // 原因：用户在签约前停留的页面（如 VIPCenterPage）本来就在栈顶；
  //       真正用来唤醒轮询的机制是 onForeground 广播 APP_FOREGROUND，
  //       这里强行做路由匹配反而会找不到对应路由打 warn 误导排查。
  if (want.uri.startsWith('iccapp://')) {
    console.info(`[EntryAbility] return via iccapp:// uri=${want.uri}`);
    return;       // 早返，不走 RouterUtil.navigateFromScheme
  }

  // 其它 deep link 走业务路由
  if (RouterUtil.isReady()) RouterUtil.navigateFromScheme(want.uri);
  else AppStorage.setOrCreate<string>('PENDING_DEEP_LINK', want.uri);
}
```

为什么不让通用 deep link 路由器处理回跳 scheme：
- `iccapp://com.frx.trywellness/returnApp` 没有对应业务页（不是用来导航的）
- 让 RouterUtil 处理 → 找不到路由打 `warn unknown route` → 排查时被误导以为路由配置错了
- 真正唤醒轮询的是 `onForeground` 通道，回跳 uri 只是顺带的"我回来了"信号

---

## §4 支付宝 sub_code 深度诊断

### 4.1 为什么需要解析子结构

`Pay().pay()` 返回的 `Map` 里 `result` 字段是支付宝服务端**完整 JSON 响应**，里面有真正的错误根因。只看 `resultStatus` + `memo` 看不到。

### 4.2 alipay_trade_app_pay_response 标准结构

支付宝**开放平台官方文档**定义（[文档地址](https://opendocs.alipay.com/open/204/105301)）：

```json
{
  "alipay_trade_app_pay_response": {
    "code": "10000",                  // 网关状态码
    "msg": "Success",
    "sub_code": "ACQ.SYSTEM_ERROR",   // ← 业务子状态码（关键诊断字段）
    "sub_msg": "系统繁忙",
    "app_id": "2021xxxxxxxxxxx",
    "out_trade_no": "20260507xxxx",
    "trade_no": "2026050722001xxxx",
    "total_amount": "0.01",
    "seller_id": "20880xxxxxxxxxx",
    "charset": "utf-8",
    "timestamp": "2026-05-07 12:00:00"
  },
  "sign": "..."
}
```

### 4.3 完整诊断模板

```typescript
async function payWithAlipay(orderInfo: string): Promise<PayResult> {
  // ★ 完整 dump payDetail 不截断（避免 substring 截断丢字段）
  console.info(`[alipay] payDetail FULL=${orderInfo}`);

  let result: Map<string, string>;
  try {
    result = await new Pay().pay(orderInfo, true);
  } catch (e) {
    // ★ 双形态返回：throw 路径
    //   Pay().pay 既可能 throw（参数解析失败 / SDK 初始化失败），
    //   也可能 return Map with error status（用户取消 / 网络异常）。两路都要处理。
    const errMsg = e instanceof Error ? e.message : String(e);
    let raw: string;
    try { raw = JSON.stringify(e); } catch (_) { raw = errMsg; }
    // JSON.stringify(error) 而非只看 Error.message —— 后端 reason 经常被吞掉
    console.warn(`[alipay] Pay().pay THROW msg=${errMsg} raw=${raw}`);
    return { state: 'failed', message: '支付宝调起失败' };
  }

  // ★ 完整 dump 所有 keys（拿 SDK 自定义 key）
  const allKeys: string[] = [];
  result.forEach((_v: string, k: string) => allKeys.push(k));
  const status = result.get('resultStatus') ?? '';
  const memo = result.get('memo') ?? '';
  const resultDetail = result.get('result') ?? '';
  console.info(
    `[alipay] resultStatus='${status}' memo='${memo}' ` +
    `result.len=${resultDetail.length} allKeys=[${allKeys.join(',')}]`
  );

  // ★ 解析 alipay_trade_app_pay_response 子结构（金矿）
  if (resultDetail.length > 0) {
    console.info(`[alipay] result FULL=${resultDetail}`);
    try {
      const parsed: Record<string, Object> = JSON.parse(resultDetail);
      const subResp = parsed['alipay_trade_app_pay_response'] as Record<string, Object> | undefined;
      if (subResp) {
        console.info(
          `[alipay] code=${subResp['code']} msg=${subResp['msg']} ` +
          `sub_code=${subResp['sub_code']} sub_msg=${subResp['sub_msg']} ` +
          `out_trade_no=${subResp['out_trade_no']} trade_no=${subResp['trade_no']} ` +
          `total_amount=${subResp['total_amount']} app_id=${subResp['app_id']}`
        );
      }
    } catch (parseErr) {
      console.warn(`[alipay] result JSON parse failed: ${parseErr}`);
    }
  }

  // ... 按 status 分发
}
```

### 4.4 高频 sub_code 速查（ACQ.* 码族）

| sub_code | 含义 | 客户端动作 |
|----------|------|-----------|
| `ACQ.TRADE_HAS_FINISHED` | 重复支付（订单已完成）| 直接当成功，调后端查订单状态 |
| `ACQ.SYSTEM_ERROR` | 支付宝侧故障 | 重试或提示用户稍后再试 |
| `ACQ.MERCHANT_AGREEMENT_NOT_EXIST` | **商户签约缺失**（最高频）| 后端配置问题，无法客户端修复 |
| `ACQ.INVALID_PARAMETER` | 参数错（金额格式 / 商户号 / 签名上下文）| 检查 saleAmount / partner ID / extJson 透传 |
| `ACQ.MERCHANT_AGREEMENT_INVALID` | 商户签约失效 | 后端联系支付宝运营 |
| `ACQ.PAYMENT_AUTH_NO_ERROR` | 授权号错误（订阅签约场景）| 检查 sign_params 完整性 |
| `ACQ.SELLER_BALANCE_NOT_ENOUGH` | 卖方余额不足（B2B）| 联系商户充值 |
| `ACQ.BUYER_BANKCARD_BALANCE_NOT_ENOUGH` | 买方余额不足 | 提示用户换卡 |
| `ACQ.RISK_CONTROL_BLOCK` | 风控拦截 | 提示用户使用其它支付方式 |

> 完整 ACQ.* 列表见支付宝开放平台官方接口文档"业务错误码"章节。

### 4.5 "商家参数错误" 高频根因（按概率）

定位"交易订单处理失败" / "商家参数错误"的标准排查顺序：

1. **`app_id` 错配**（最高频）—— `parseAlipayOrderInfo(payDetail)['app_id']` 是否与开放平台配的一致
2. **`sign` 缺失或为空** —— `(fields['sign'] ?? '').length > 0` 应为 true
3. **`biz_content` 解码异常** —— H5 表单提交时未 `decodeURIComponent` 二次编码会断
4. **`sub_code === 'ACQ.MERCHANT_AGREEMENT_NOT_EXIST'`** —— 商户没签某产品（如周期扣款）

### 4.6 orderInfo query 串拆字段诊断

支付宝 `orderInfo` 是 URL-encoded query 串，单字段对账可定位 80% 配置问题：

```typescript
function parseAlipayOrderInfo(orderInfo: string): Record<string, string> {
  const out: Record<string, string> = {};
  const pairs = orderInfo.split('&');
  for (const p of pairs) {
    const eq = p.indexOf('=');
    if (eq > 0) {
      out[p.substring(0, eq)] = decodeURIComponent(p.substring(eq + 1));
    }
  }
  return out;
}

// 在 requestAlipayPayOrder 拿到 payDetail 后立刻 dump
const fields = parseAlipayOrderInfo(payDetail);
console.info(
  `[alipay] payDetail parsed: ` +
  `app_id=${fields['app_id'] ?? ''} method=${fields['method'] ?? ''} ` +
  `sign_type=${fields['sign_type'] ?? ''} timestamp=${fields['timestamp'] ?? ''} ` +
  `version=${fields['version'] ?? ''} hasSign=${(fields['sign'] ?? '').length > 0} ` +
  `biz_content.len=${(fields['biz_content'] ?? '').length}`
);
const bizContent = fields['biz_content'] ?? '';
if (bizContent.length > 0) {
  console.info(`[alipay] biz_content=${bizContent}`);
}
```

---

## §5 诊断日志方法论（贯穿全章）

支付链路的报错经常被吞、被截断或者被多层封装压平。下面 4 条原则在前 4 章节里反复出现，单独列出：

### 5.1 完整 dump 不截断

```typescript
// ❌ 大字段被截断丢字段
console.info(`payDetail=${payDetail.substring(0, 400)}`);

// ✅ 完整 dump，便于对比抓包
console.info(`payDetail FULL=${payDetail}`);
```

### 5.2 `JSON.stringify(error)` 而非只看 `Error.message`

```typescript
// ❌ 后端 reason 被吞
console.warn(`pay failed: ${err.message}`);

// ✅ 完整 dump
let raw: string;
try { raw = JSON.stringify(e); } catch (_) { raw = String(e); }
console.warn(`pay failed: msg=${err.message} raw=${raw}`);
```

### 5.3 数组逐元素 + 关键字段一行 dump

```typescript
// ❌ 只打长度
console.info(`loadGoodsList ok len=${list.length}`);

// ✅ 每个 SKU 一行 + 关键字段（订阅签约场景靠这个判断 firstPrice/duration 是否对）
for (let i = 0; i < list.length; i++) {
  const g = list[i];
  console.info(
    `loadGoodsList[${i}] id=${g.id} name='${g.name}' ` +
    `price=${g.price} firstPrice=${g.firstPrice} ` +
    `duration=${g.duration} timeUnit=${g.timeUnit} ` +
    `exchange=${g.exchange} deduct=${g.deduct}`
  );
}
```

### 5.4 状态判定后立刻打"人话"日志

```typescript
// ❌ 让人反查代码才知道意义
console.info(`saleAmount=${realPrice}`);

// ✅ 直接说人话
console.info(
  `saleAmount=${realPrice} ` +
  `${exchange === 2 && deduct === 2 ? '(=firstPrice 先签后付/首期价)' : '(=price 标准价)'}`
);
```

---

## §6 后端字段类型以"实际抓包"为准

支付链路遇到"判定永远走默认分支"类 bug，常常是因为客户端的字段类型定义与后端实际下发不符。

**典型场景**：客户端按文档/Android 定义为 `number`（如 `1=SDK / 2=SCHEME`），但后端实际返字符串 `"appScheme"`。

**通用应对**：
- 字段类型尽量保守用 `string`（让数字也能通过）
- 判定写法兼容多形态：
  ```typescript
  const t = (raw ?? '').toString().toLowerCase();
  if (t === 'appscheme' || t === 'scheme' || t === '2') return true;
  ```
- 若有疑问，先抓包确认实际类型再定字段

> 这条原则不限于支付——任何后端响应字段在迁移期都建议先抓一次包再定型。

---

## §7 调试速查

| 症状 | 跳到 |
|------|------|
| 支付宝 SDK 弹"交易订单处理失败" | §1.4 反例 + §4 sub_code 诊断 |
| `payDetail` 是 `alipays://` 开头 | §1.1 路径判定 + §1.3 SCHEME 模板 |
| 轮询超时 `elapsed=180000+ms` 跑超时 | §2.1-2.5 onForeground 唤醒 |
| 支付宝完成签约弹"暂无可用打开方式" | §3.2 module.json5 skills + §3.3 clean rebuild |
| `RouterUtil` 报"未知路由 iccapp://..." | §3.4 onNewWant 早返 |
| `bundleManager.canOpenLink` 永远返 false | §1.3 + §3.2 querySchemes |
| 不知道支付宝具体错在哪 | §4.3 完整诊断模板 + §4.4 ACQ.* 速查 |
| 想知道 saleAmount 是否对 | §5.3 数组逐元素 dump |

---

## Changelog

- **2026-05-07 init**：从 Fitness 迁移项目支付宝订阅签约 SCHEME 全链路 + HMOS 后台 setTimeout 减速 + 业务回跳 scheme + sub_code 诊断沉淀
