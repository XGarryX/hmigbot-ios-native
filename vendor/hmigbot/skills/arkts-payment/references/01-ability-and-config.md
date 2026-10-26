# 初始化、Ability 集成与开放平台配置

第三方支付集成在 HarmonyOS 上的"第一公里"。绝大部分"回调不触发"、"Bundle ID 校验失败"、"应用未注册"根因都在这里。

## 1. `module.json5` 必备配置

```json5
{
  "module": {
    "requestPermissions": [
      { "name": "ohos.permission.INTERNET" },
      // 若需要获取安装列表（判断微信是否装）
      { "name": "ohos.permission.GET_BUNDLE_INFO_PRIVILEGED" }
    ],
    "querySchemes": [
      "weixin",     // 用于 bundleManager.canOpenLink('weixin://')
      "wxopensdk",  // 用于 wxopensdk 内部跳转微信
      "alipay",     // 支付宝
      "alipays"
    ],
    "abilities": [
      {
        "name": "EntryAbility",
        "skills": [
          {
            "actions": ["ohos.want.action.home"],
            "entities": ["entity.system.home"]
          },
          {
            // 接收微信回调（必须）
            "actions": ["wxentity.action.open"]
          },
          {
            // ★ 业务回跳 scheme（接支付宝订阅签约 / 任何 OAuth 回跳必须）
            // 支付宝周期扣款的 biz_content 含 `return_url=iccapp://...`，签约完成后
            // 拉起此 scheme 跳回本 App。具体 scheme 名（iccapp / myapp / xyz）由
            // 商户后端在生成 biz_content 时自选；客户端要做的就是把它注册给系统。
            // 详见 references/07-alipay-subscription-and-hmos-quirks.md §3
            "actions": ["ohos.want.action.viewData"],
            "uris": [
              { "scheme": "<your-business-scheme>", "host": "<your-bundle-name>" }
            ]
          }
        ]
      }
    ]
  }
}
```

缺 `querySchemes` → `canOpenLink` 永远返回 false；缺 `wxentity.action.open` action → 从微信返回时系统找不到 Ability 分发；缺业务回跳 `skills.uris` → 支付宝完成签约后弹**"暂无可用打开方式"**（且 ArkTS 端抓不到任何错误，是支付宝 App 内部弹的）。

> ⚠️ **改完 module.json5 必须 clean rebuild**：`Invalidate Caches → 重打包 → 重新签名 → 安装` —— `skills` / `querySchemes` 在 HAP 打包时被固化，仅 Sync / Reload 不生效。新接支付的项目 80% 第一次卡在这里。这是 HMOS 平台编译行为，不是 IDE 问题。

## 2. 项目构建配置

`build-profile.json5`（项目级）必须开启 normalized URL，否则支付宝 SDK 报错：

```json5
{
  "app": {
    "products": [{
      "name": "default",
      "compatibleSdkVersion": "5.0.0(12)",
      "useNormalizedOHMUrl": true   // ⚠️ 支付宝 cashiersdk 强制要求
    }]
  }
}
```

不开会看到：`Bytecode HARs: [@cashier_alipay/cashiersdk] not supported when useNormalizedOHMUrl is not true`。

## 3. WXApi 单例初始化

```typescript
// utils/WxApiHelper.ets
import * as wxopensdk from '@tencent/wechat_open_sdk'

const APP_ID = '<微信开放平台-移动应用 AppID>'
// ⚠️ 不是小程序 AppID、不是公众号 AppID、不是其他 App 的 AppID
// 高频踩坑：误填小程序 AppID → "应用未注册"

export const WXApi = wxopensdk.WXAPIFactory.createWXAPI(APP_ID)
```

## 4. EntryAbility 集成（关键）

微信从外部返回时，系统通过 Ability 的 `onNewWant` 派发。**不调 `WXApi.handleWant()` → `onResp` 永远不触发**。

```typescript
import UIAbility from '@ohos.app.ability.UIAbility'
import * as wxopensdk from '@tencent/wechat_open_sdk'
import { Want } from '@kit.AbilityKit'
import { WXApi } from '../utils/WxApiHelper'
import { wxEventHandler } from '../utils/WxEventHandler'

export default class EntryAbility extends UIAbility {
  onCreate(want: Want, launchParam): void {
    // 冷启动时：如果 want 来自微信，也要 handleWant
    WXApi.handleWant(want, wxEventHandler)
    // 注：HarmonyOS 版 SDK 的 WXApi 接口（1.0.x）只有 4 个方法：
    //   sendReq / openWechat / handleWant / isWXAppInstalled
    // 没有 registerApp —— 那是 Android SDK 的遗留。createWXAPI() 内部已完成 App 注册，
    // 不需要（也无法）额外调用 registerApp。
  }

  onNewWant(want: Want, launchParam): void {
    // 热启动回到前台时：从微信跳回必走这里
    WXApi.handleWant(want, wxEventHandler)
  }
}
```

## 5. `WXApiEventHandler` 完整实现（Map-based 多订阅）

支持多个页面同时注册不同的 callback，典型用于 LoginPage 和 MemberCenterPage 共存的场景。

```typescript
// utils/WxEventHandler.ets
import * as wxopensdk from '@tencent/wechat_open_sdk'

export type WxReqCallback = (req: wxopensdk.BaseReq) => void
export type WxRespCallback = (resp: wxopensdk.BaseResp) => void

class WxEventHandlerImpl implements wxopensdk.WXApiEventHandler {
  private reqCallbacks: Map<string, WxReqCallback> = new Map()
  private respCallbacks: Map<string, WxRespCallback> = new Map()

  registerOnWXReqCallback(cb: WxReqCallback): void {
    this.reqCallbacks.set(cb.toString(), cb)
  }
  unregisterOnWXReqCallback(cb: WxReqCallback): void {
    this.reqCallbacks.delete(cb.toString())
  }
  registerOnWXRespCallback(cb: WxRespCallback): void {
    this.respCallbacks.set(cb.toString(), cb)
  }
  unregisterOnWXRespCallback(cb: WxRespCallback): void {
    this.respCallbacks.delete(cb.toString())
  }

  onReq(req: wxopensdk.BaseReq): void {
    this.reqCallbacks.forEach(cb => cb(req))
  }
  onResp(resp: wxopensdk.BaseResp): void {
    this.respCallbacks.forEach(cb => cb(resp))
  }
}

export const wxEventHandler = new WxEventHandlerImpl()
```

## 6. 页面消费模板

```typescript
// PayPage.ets
aboutToAppear(): void {
  wxEventHandler.registerOnWXRespCallback(this.onWxResp)
}
aboutToDisappear(): void {
  wxEventHandler.unregisterOnWXRespCallback(this.onWxResp)
}

private onWxResp = (resp: wxopensdk.BaseResp): void => {
  // 多页面共享 handler 时必须区分子类
  if (resp instanceof wxopensdk.PayResp) {
    if (resp.errCode === 0) { /* 查订单 */ }
    else if (resp.errCode === -2) { /* 用户取消 */ }
    else { /* 失败 */ }
  }
  // SendAuthResp 属于登录页，本页忽略
}
```

生命周期强制配对：**`aboutToAppear` 注册 / `aboutToDisappear` 注销**。用 `onAppear` / `onDisAppear` 会错过真正的回调时机。

## 7. 安装预检（避免模拟器空报错）

```typescript
import { bundleManager } from '@kit.AbilityKit'

function isWeChatInstalled(): boolean {
  try {
    return bundleManager.canOpenLink('weixin://')
  } catch (e) {
    return false
  }
}
```

`bundleManager.canOpenLink` 要求 `querySchemes` 已声明 `weixin`，否则永远返回 false。

## 8. 开放平台配置与签名陷阱

### 签名：禁用自动签名

| 签名方式 | `appIdentifier` | 开放平台校验 |
|---|---|---|
| 自动签名（IDE 默认）| 每次构建可能变 | ❌ 必挂 |
| 手动签名（固定证书）| 稳定 | ✅ 正确 |

**必须用手动签名**，且调试 / 发布使用同一套证书；否则开发期能用、上架版炸。

### 获取 `appIdentifier`

```typescript
import { bundleManager } from '@kit.AbilityKit'

async function getAppIdentifier(): Promise<string> {
  const info = await bundleManager.getBundleInfoForSelf(
    bundleManager.BundleFlag.GET_BUNDLE_INFO_WITH_SIGNATURE_INFO
  )
  return info.signatureInfo.appIdentifier
}
```

该值填入微信开放平台 "管理中心 - 移动应用 - 平台信息 - Identifier" 字段。

### QQ 互联 fingerprint（可选）

QQ 要的是 MD5(fingerprint)，不是 appIdentifier：

```typescript
const info = bundleManager.getBundleInfoForSelfSync(<flags>)
const fp = info.signatureInfo.fingerprint.toLowerCase()
const md5 = <md5-lib>(fp)  // 32 位 MD5
```

### 审核流程时序

1. 微信开放平台创建/编辑"移动应用" → 填 Bundle ID + Identifier → 提交审核
2. **审核期间调 SDK 会报 "Bundle ID 校验不通过" / "应用未注册"** — 正常现象
3. 审核通过后才能正常调起
4. 改包名 / 换签名证书必须重新提交审核

### 三者严格对齐清单

| 项 | 位置 | 值 |
|---|---|---|
| Bundle ID | `AppScope/app.json5` → `bundleName` | `com.xxx.yyy` |
| Bundle ID | 微信开放平台 | 必须完全一致（大小写敏感）|
| Identifier | 开放平台 Identifier 字段 | 来自 `signatureInfo.appIdentifier` |
| AppID | 代码里 `createWXAPI(appId)` | 开放平台 AppID（**移动应用**，非小程序）|

任意一项对不上 → SDK 调起失败，且错误提示不一定准确。

## 9. 初始化次序（支付场景最佳实践）

在 `EntryAbility.onCreate`：

1. 基础 context / 工具初始化
2. `WXApi.handleWant(want, handler)`（处理冷启动时来自微信的 want）
3. 其他 SDK 初始化

**`handleWant` 必须**在 `onCreate` 和 `onNewWant` 两处都调，对应冷启动 / 热启动两种回微信的场景。

### ⚠️ 不要调用 `registerApp`

某些外部资料（特别是沿袭 Android SDK 写法的教程）会建议调用 `WXApi.registerApp(appId, handler)`。
**在 HarmonyOS 版 `@tencent/wechat_open_sdk` (1.0.x) 中这个方法不存在**，写上去会编译报错：

```
ERROR: 10505001  Property 'registerApp' does not exist on type 'WXApi'
```

SDK 接口（`WXAPIFactory.d.ets`）只有 4 个方法：
`sendReq` / `openWechat` / `handleWant` / `isWXAppInstalled`。
`createWXAPI(APP_ID)` 内部已完成 App 注册。
