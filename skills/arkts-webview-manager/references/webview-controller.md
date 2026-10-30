# WebviewController 核心 API 与 Web 组件配置

## 1. 控制器声明

```typescript
import webview from '@ohos.web.webview';

private webController: webview.WebviewController = new webview.WebviewController();
```

每个独立的 WebView 实例需要自己的 controller。分屏等多 WebView 场景需声明多个。

## 2. Web 组件声明式配置

```typescript
Web({ src: this.url, controller: this.webController })
  .id('my_web')
  .width('100%')
  .layoutWeight(1)
  // ── 功能开关 ──
  .javaScriptAccess(true)        // JS 执行权限
  .domStorageAccess(true)         // DOM 存储（localStorage/sessionStorage）
  .fileAccess(true)               // 本地文件访问
  .imageAccess(true)              // 图片加载
  .geolocationAccess(true)        // 地理位置
  .mediaPlayGestureAccess(true)   // 媒体播放手势
  // ── 字体缩放 ──
  .textZoomRatio(this.fontSize)   // 100 = 100%, 150 = 150%
  // ── 生命周期回调 ──
  .onPageBegin((event) => { /* 页面开始加载 */ })
  .onPageEnd(() => { /* 页面加载完成 — 适合注入样式/脚本 */ })
  .onProgressChange((event) => { /* event.newProgress: 0-100 */ })
  .onTitleReceive((event) => { /* event.title: 页面标题 */ })
  .onErrorReceive(() => { /* 加载错误 */ })
```

### 关键回调时机

| 回调 | 触发时机 | 典型用途 |
|------|---------|---------|
| `onPageBegin` | URL 开始加载 | 更新地址栏、设置 loading 状态 |
| `onPageEnd` | 页面加载完成 | 注入 CSS/JS、同步标签页状态、恢复样式 |
| `onProgressChange` | 加载进度变化 | 进度条显示 |
| `onTitleReceive` | 页面标题变化 | 更新标题栏、WebView 间通信通道 |

## 3. 导航 API

```typescript
// 加载 URL
this.webController.loadUrl(url);

// 加载 HTML 字符串（适用于 EPUB、本地内容等）
this.webController.loadData(
  htmlContent,      // HTML 字符串
  'text/html',      // MIME 类型
  'utf-8',          // 编码
  basePath           // 基础路径（file://...），用于解析相对资源路径
);

// 前进/后退/刷新/停止
this.webController.backward();
this.webController.forward();
this.webController.refresh();
this.webController.stop();

// 检查能否前进/后退（用于更新按钮状态）
const canBack: boolean = this.webController.accessBackward();
const canFwd: boolean = this.webController.accessForward();
```

## 4. JavaScript 执行

### 4.1 统一封装（推荐）

```typescript
private runJs(script: string): void {
  this.webController.runJavaScript(script).catch((_err: Error) => {});
}
```

`runJavaScript()` 返回 `Promise<string>`，结果是 JS 表达式返回值的字符串形式。**必须 `.catch()`**，否则页面 JS 异常会导致应用崩溃。

### 4.2 获取返回值

```typescript
this.webController.runJavaScript("window.getSelection().toString()")
  .then((result: string) => {
    // result 是 JS 返回值的字符串化
  });
```

### 4.3 从 rawfile 加载并执行大型 JS 文件

rawfile 返回 `Uint8Array`，必须分块转换为字符串（见第 7 节），否则大文件会栈溢出。

```typescript
private async loadAndRunRawfile(fileName: string): Promise<void> {
  try {
    const context = getContext(this) as common.UIAbilityContext;
    const rawfileContent = context.resourceManager.getRawFileContentSync(fileName);
    const jsString = this.uint8ArrayToString(rawfileContent);
    await this.webController.runJavaScript(jsString);
  } catch (e) {
    console.error(`loadAndRunRawfile(${fileName}) failed: ${String(e)}`);
  }
}
```

### 4.4 链式执行（先加载库，再调用库 API）

```typescript
this.loadAndRunRawfile('SomeLibrary.js').then(() => {
  this.webController.runJavaScript(`(function(){
    // 此处可使用 SomeLibrary 暴露的全局 API
  })()`);
});
```

### 4.5 IIFE 模式（所有注入 JS 必须使用）

```typescript
// 正确 ✓ — IIFE 包裹，防止全局变量污染
const js = `(function(){
  var el = document.getElementById('myStyle');
  if (!el) { el = document.createElement('style'); el.id = 'myStyle'; document.head.appendChild(el); }
  el.textContent = '* { color: red !important }';
})()`;

// 错误 ✗ — 全局作用域可能冲突
const js = `var el = document.getElementById('myStyle'); ...`;
```

## 5. CSS 注入系统

### 5.1 核心注入函数

通过 `runJavaScript` 创建带唯一 ID 的 `<style>` 元素。ID 保证幂等 — 多次注入只更新不叠加。

```typescript
private injectCssString(css: string, styleId: string): void {
  const safeCss = css.replace(/\\/g, '\\\\').replace(/`/g, '\\`').replace(/\$/g, '\\$');
  const js = `(function(){` +
    `var el=document.getElementById('${styleId}');` +
    `if(!el){el=document.createElement('style');el.id='${styleId}';document.head.appendChild(el);}` +
    `el.textContent=\`${safeCss}\`;` +
    `})()`;
  this.runJs(js);
}
```

### 5.2 从 rawfile 加载 CSS

```typescript
private injectCssFromRawfile(fileName: string, styleId: string): void {
  try {
    const context = getContext(this) as common.UIAbilityContext;
    const rawfileContent = context.resourceManager.getRawFileContentSync(fileName);
    const cssString = this.uint8ArrayToString(rawfileContent);
    this.injectCssString(cssString, styleId);
  } catch (e) {
    console.error(`injectCssFromRawfile(${fileName}) failed: ${String(e)}`);
  }
}
```

### 5.3 移除已注入的样式

```typescript
this.runJs(`(function(){var el=document.getElementById('${styleId}');if(el)el.remove();})()`);
```

### 5.4 Style ID 命名约定

建议使用统一前缀（如 `myapp_`），新增样式时沿用命名约定。示例：

| Style ID | 用途 |
|----------|------|
| `myapp_font_style` | 自定义字体族 |
| `myapp_bold_style` | 粗体 |
| `myapp_theme_style` | 主题/颜色 |

## 6. 页内搜索 API

```typescript
this.webController.searchAllAsync(query);  // 高亮所有匹配
this.webController.searchNext(true);       // 下一个匹配
this.webController.searchNext(false);      // 上一个匹配
this.webController.searchAllAsync('');      // 清除高亮
```

典型模式：跟踪 `lastQuery`，新关键词用 `searchAllAsync`，相同关键词用 `searchNext`。

## 7. uint8ArrayToString 工具函数

rawfile 内容为 `Uint8Array`，大文件必须分块转换：

```typescript
private uint8ArrayToString(data: Uint8Array): string {
  const CHUNK = 8192;
  let result = '';
  for (let i = 0; i < data.length; i += CHUNK) {
    const end = Math.min(i + CHUNK, data.length);
    const chunk: number[] = [];
    for (let j = i; j < end; j++) {
      chunk.push(data[j]);
    }
    result += String.fromCharCode(...chunk);
  }
  return result;
}
```

> 直接 `String.fromCharCode(...largeArray)` 会因参数过多导致栈溢出。

## 8. 其他 API

```typescript
// User Agent 切换（切换后需 refresh 生效）
this.webController.setCustomUserAgent(uaString);
this.webController.refresh();

// PDF 打印
const adapter = this.webController.createWebPrintDocumentAdapter('savePdf');

// 调试模式（在 aboutToAppear 中启用）
webview.WebviewController.setWebDebuggingAccess(true);
```
