# H5 支付容器完整实现

本文档聚焦 WebView 承载微信 H5 支付、支付宝 H5 表单等场景的通用容器实现。

## 1. WebView 4 要素（缺一即白屏）

### 要素 1：UA 伪装

HarmonyOS WebView 默认 UA 含 `ArkWeb`，微信 / 支付宝 H5 网关 UA 检测失败 → 直接白屏。

```typescript
// UA 字符串本身不重要，关键特征：像 Android Chrome 移动端
export const PAYMENT_USER_AGENT =
  'Mozilla/5.0 (Linux; Android 14; Pixel 8 Build/UQ1A.240205.002) ' +
  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.64 Mobile Safari/537.36'

Web({ src, controller }).userAgent(PAYMENT_USER_AGENT)
```

UA 必须包含：`Android` + `AppleWebKit` + `Chrome` + `Mobile Safari` 这几个标识。

### 要素 2：Referer 注入

`Web({ src: url })` 直接加载**无法附加 header**。必须用 `onControllerAttached` + `loadUrl`：

```typescript
Web({
  src: referer.length > 0 ? '' : url,  // 有 referer 时先空 src
  controller: this.webController
})
  .onControllerAttached(() => {
    if (referer.length > 0 && url.length > 0) {
      this.webController.loadUrl(url, [
        { headerKey: 'Referer', headerValue: referer }
      ])
    }
  })
```

`referer` 值 = 后端返回的 `h5Domain`（商户在微信支付后台配置的授权域名）。

**常见坑**：后端返回的 `h5Domain` 可能是 `https://pay.merchant.com` 或 `pay.merchant.com`（有无协议头不一）。两种都要兼容，必要时加协议头前缀。

### 要素 3：Scheme 拦截

```typescript
.onLoadIntercept((event) => {
  const requestUrl = event.data.getRequestUrl()
  const schemes = ['weixin://', 'alipays://', 'alipay://']
  for (const s of schemes) {
    if (requestUrl.startsWith(s)) {
      this.openExternalApp(requestUrl)
      return true  // 阻止 WebView 自己加载（必然失败）
    }
  }
  return false
})
```

`module.json5` 的 `querySchemes` 必须同时声明 `weixin` / `alipay` / `alipays`，否则 `startAbility` 必失败。

### 要素 4：返回后自动关闭 WebView

从外部 App 回到本应用时 H5 收银台已失效，必须自动 pop。

```typescript
private hasLaunchedExternalApp: boolean = false

private openExternalApp(url: string): void {
  this.hasLaunchedExternalApp = true
  const context = getContext(this) as common.UIAbilityContext
  const want: Want = { action: 'ohos.want.action.viewData', uri: url }

  context.startAbility(want).catch((err: Error) => {
    // ⚠️ 失败必须复位 flag，否则下次 onAppear 误 pop
    this.hasLaunchedExternalApp = false
    if (url.startsWith('weixin://')) {
      promptAction.showToast({ message: '未安装微信或调起失败' })
    } else if (url.startsWith('alipay')) {
      promptAction.showToast({ message: '未安装支付宝或调起失败' })
    }
  })
}

.onAppear(() => {
  if (this.hasLaunchedExternalApp) {
    this.hasLaunchedExternalApp = false
    this.pathStack.pop()
  }
})
```

## 2. JS Bridge（H5 → Native 能力）

H5 常需要调原生"关闭页面"、"toast"。通用做法：

```typescript
interface WebJsBridge {
  closePage: () => void
  showToast: (msg: string) => void
  // 不要暴露敏感方法如 getToken / startPay
}

private jsBridge: WebJsBridge = {
  closePage: () => { this.pathStack.pop() },
  showToast: (msg: string) => { promptAction.showToast({ message: msg }) }
}

Web({ src, controller: this.webController })
  .javaScriptProxy({
    object: this.jsBridge,
    name: '<项目与 H5 约定的 bridge 名>',  // 如 nativeBridge
    methodList: ['closePage', 'showToast'],  // 白名单！
    controller: this.webController
  })
```

### 多 Bridge 名兼容

对接多个 H5 团队时，用**同一对象**绑多次不同 `name`：

```typescript
// 同一 jsBridge 对象以多个名字注册，兼容不同 H5 约定
.javaScriptProxy({ object: this.jsBridge, name: 'teamABridge', ... })
.javaScriptProxy({ object: this.jsBridge, name: 'teamBBridge', ... })
```

### 安全原则

- `methodList` 必须是白名单，不要暴露整个 `this` 或整个 VM
- Bridge 方法内不读 token、不发敏感请求
- 对外参数必须 sanitize（防 XSS 注入到 native 层）

## 3. H5 返回按钮劫持脚本

H5 自渲染的返回按钮可能通过 `window.close()` / `history.back()` / `onBackPressed` 触发，WebView 默认不会 pop 原生页。注入劫持脚本：

```typescript
.onPageEnd(() => {
  const BRIDGE_NAME = '<项目 bridge 名>'
  const hijack = `(function(){
    try {
      var callNative = function(){
        if (window.${BRIDGE_NAME} && window.${BRIDGE_NAME}.closePage) {
          window.${BRIDGE_NAME}.closePage();
          return true;
        }
        return false;
      };
      // 劫持 window.close
      var _close = window.close;
      window.close = function(){
        if(!callNative()){ try{_close.apply(window);}catch(e){} }
      };
      // 劫持 history.back（仅在无历史时回调原生）
      var _back = history.back.bind(history);
      history.back = function(){
        if (window.history.length <= 1 && callNative()) return;
        _back();
      };
      // onBackPressed 兜底
      if (typeof window.onBackPressed === "undefined") {
        window.onBackPressed = callNative;
      }
    } catch(e) {}
  })();`

  try {
    this.webController.runJavaScript(hijack)
  } catch (e) { /* log */ }
})

// 双保险：H5 调 window.close() 且劫持失败时
.onWindowExit(() => {
  this.pathStack.pop()
})
```

## 4. Safe-area 三态处理

同一 WebView 容器应适配三种场景：

| 场景 | `showTitle` | `fitWindow` | padding-top | 说明 |
|---|---|---|---|---|
| 协议/隐私等（原生 TitleBar）| `true` | - | TitleBar 自处理 | 左上角原生返回箭头 |
| H5 自带标题栏（客服/举报）| `false` | `false` | `0` | ArkTS 不加 padding，避免双空白 |
| 裸 H5（支付/活动）| `false` | `true` | `windowTopPadding + 6` | 避让系统状态栏 |

```typescript
.padding({
  top: (this.showTitle || !this.fitWindow) ? 0 : windowTopPadding + 6
})
```

## 5. 透明返回热区（兜底方案）

H5 自渲染返回按钮但 Bridge 注入失败时最后兜底：

```typescript
if (!this.showTitle && !this.fitWindow) {
  Row()
    .width(44)
    .height(44)
    .backgroundColor('rgba(0,0,0,0.001)')  // 近透明但可接收点击
    .position({ x: 0, y: <H5 返回按钮预估 y 位置> })
    .onClick(() => { this.pathStack.pop() })
}
```

**位置值**需根据 H5 实际渲染位置微调。这是兜底方案，主路径仍应走 Bridge + 劫持脚本。

## 6. 完整 WebView 容器模板

```typescript
@ComponentV2
struct PaymentWebView {
  pathStack: NavPathStack = new NavPathStack()
  @Local url: string = ''
  @Local title: string = ''
  @Local isLoading: boolean = false
  @Local showTitle: boolean = false
  @Local fitWindow: boolean = true
  private referer: string = ''
  private hasLaunchedExternalApp: boolean = false
  private webController: webview.WebviewController = new webview.WebviewController()

  private jsBridge: WebJsBridge = {
    closePage: (): void => { this.pathStack.pop() },
    showToast: (msg: string): void => { promptAction.showToast({ message: msg }) }
  }

  build() {
    NavDestination() {
      Column() {
        if (this.showTitle) { this.TitleBarBuilder() }
        Stack() {
          Web({
            src: this.referer.length > 0 ? '' : this.url,
            controller: this.webController
          })
            .width('100%').height('100%')
            .javaScriptAccess(true)
            .domStorageAccess(true)
            .mixedMode(MixedMode.All)
            .userAgent(PAYMENT_USER_AGENT)
            .javaScriptProxy({
              object: this.jsBridge,
              name: '<bridge name>',
              methodList: ['closePage', 'showToast'],
              controller: this.webController
            })
            .onControllerAttached(() => {
              if (this.referer.length > 0 && this.url.length > 0) {
                this.webController.loadUrl(this.url, [
                  { headerKey: 'Referer', headerValue: this.referer }
                ])
              }
            })
            .onPageEnd(() => {
              this.isLoading = false
              this.injectHijackScript()
            })
            .onLoadIntercept((event) => {
              const u = event.data.getRequestUrl()
              if (u.startsWith('weixin://') || u.startsWith('alipays://') || u.startsWith('alipay://')) {
                this.openExternalApp(u)
                return true
              }
              return false
            })
            .onWindowExit(() => { this.pathStack.pop() })

          if (this.isLoading) {
            LoadingProgress().width(40).height(40)
          }
        }
        .width('100%').layoutWeight(1)
        .padding({ top: (this.showTitle || !this.fitWindow) ? 0 : windowTopPadding + 6 })
      }
      .onAppear(() => {
        if (this.hasLaunchedExternalApp) {
          this.hasLaunchedExternalApp = false
          this.pathStack.pop()
        }
      })
    }
    .hideTitleBar(true)
  }
}
```

## 7. 支付宝 H5 表单提交

用于只有表单参数、没有 SDK 签名串的场景。

### 流程

1. `orderInfo` 是 URL query string 格式（已 URL 编码）
2. **必须 `decodeURIComponent(orderInfo)` 拆字段**（否则二次编码）
3. 每个字段 HTML 转义后构建 `<form>`
4. auto-submit JS
5. POST 到 `https://openapi.alipay.com/gateway.do`
6. H5 收银台 → 拦截 `alipays://` 同路径 B

### 最常见错误

忘记 `decodeURIComponent` → 二次编码 → 支付宝网关 4006 参数错误。

### 模板

```typescript
function buildAlipayFormHtml(orderInfo: string): string {
  // orderInfo 形如: method=alipay.trade.app.pay&app_id=xxx&biz_content=%7B...%7D&sign=xxx
  // 关键：每个字段的值可能已经被 URL 编码（如 biz_content 的 JSON）
  const params = parseQueryString(orderInfo)  // 拆成 { key: value }
  const fields = Object.keys(params).map(k => {
    const v = htmlEscape(decodeURIComponent(params[k]))  // ⚠️ decode!
    return `<input type="hidden" name="${k}" value="${v}" />`
  }).join('')

  return `<!DOCTYPE html>
<html><body>
  <form id="f" action="https://openapi.alipay.com/gateway.do" method="POST">
    ${fields}
  </form>
  <script>document.getElementById('f').submit();</script>
</body></html>`
}
```

把这段 HTML 存到沙箱文件或通过 `data:text/html;base64,...` 加载给 WebView。

## 8. 常见 H5 容器陷阱

| 现象 | 根因 | 解法 |
|---|---|---|
| 白屏 | UA 默认 ArkWeb | 替换 PAYMENT_USER_AGENT |
| 微信网关拒绝 | 缺 Referer 或不匹配商户域名 | `loadUrl` + header |
| `startAbility` 报 Ability 未找到 | `querySchemes` 未声明 | 在 module.json5 加 |
| 从微信回来 WebView 不关 | `hasLaunchedExternalApp` 未设 / 未检测 | 见 §1 要素 4 |
| H5 返回按钮点了没反应 | Bridge 名不匹配或未注入 | 同 name 双绑 + 劫持脚本 |
| 双页面 pop（退出 App）| 并发 query 未加 flag | 见 `05-order-lifecycle.md` |
| 支付宝 H5 报 4006 | orderInfo 二次编码 | `decodeURIComponent` 再构表单 |
| URL 含 `#` 空白 | 用了 `loadData` 加载 | 改用 `loadUrl` |
