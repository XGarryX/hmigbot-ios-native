---
name: arkts-webview-manager
description: >
  ArkTS/HarmonyOS WebView 开发技能（V2 优先，API 12+，兼容 V1）。覆盖 WebviewController API、CSS/JS 注入、多 WebView 分屏、页面模式（桌面/阅读/隐私）、字体样式控制、页内搜索、标签页管理、页面原地翻译、TTS 朗读等。状态管理使用 V2 装饰器（`@ComponentV2 / @Local / @Param / @Event / @Once / AppStorageV2 / PersistenceV2 / @ObservedV2 / @Trace`）；老项目 V1 装饰器（`@Component / @State / @Prop / @Link / @StorageLink / @Watch`）也可识别。当用户需要在 ArkTS 中使用 Web 组件加载网页、向页面注入脚本或样式、实现浏览器功能（前进后退、搜索、标签页、分屏）、控制 WebView 字体/颜色/阅读模式、实现页面翻译或内容朗读时，务必触发此 skill。即使用户只是说"加个深色模式"、"注入一段 CSS"、"实现页内搜索"、"翻译这个页面"、"朗读页面内容"，也应触发。
type: domain
domain: system
tags: [domain, system, webview, web, browser, css-injection, js-injection, tts, translate]
---

# ArkTS WebView 开发指南

本技能提供在 HarmonyOS ArkTS 中使用 `Web` 组件和 `WebviewController` 的通用模式。适用于任何需要嵌入 WebView 的应用，不限于浏览器。

> **API 版本与装饰器策略**：本 skill 代码示例基于 **API 12+** 推荐的 **ArkTS V2** 装饰器（`@ComponentV2 / @Local / @Param / @Event / @Once / @ObservedV2 / @Trace / @Monitor / AppStorageV2 / PersistenceV2`）。`Web()` 组件、`WebviewController` / `webview` 命名空间 API 在 V1/V2 完全通用 — V2 升级**只影响驱动 WebView 状态的装饰器**（如字体大小、模式开关、标签页状态等）。V1 老项目仍可参照本 skill，仅需把 `@Component → @ComponentV2`、`@State → @Local`、`@Prop → @Param + @Once`、`@StorageLink → AppStorageV2.connect`、`@Watch → @Monitor` 等装饰器替换；WebView API 调用部分原样保留。详见 `arkts-state-manager/SKILL.md`。

## 何时查阅哪个 Reference

| 你想做什么 | 去读 |
|-----------|------|
| 声明 Web 组件、调用导航 API、执行 JS、注入 CSS | `references/webview-controller.md` |
| 实现分屏/桌面模式/阅读模式/隐私模式 | `references/webview-page-modes.md` |
| 控制字体大小、粗体、颜色、反转、样式持久化 | `references/webview-font-settings.md` |
| 标签页管理、页内搜索、URL/Title 同步 | `references/webview-bookmark-history.md` |
| TTS 朗读（在线 TTS + AVPlayer）、页面翻译（原地翻译 / URL 重定向） | `references/webview-tts-translate.md` |

## 核心设计模式

### 1. CSS 注入

通过 `runJavaScript` 创建带唯一 ID 的 `<style>` 元素。ID 保证幂等 — 多次注入只更新不叠加。

```typescript
private injectCss(css: string, styleId: string): void {
  const safeCss = css.replace(/\\/g, '\\\\').replace(/`/g, '\\`').replace(/\$/g, '\\$');
  const js = `(function(){` +
    `var el=document.getElementById('${styleId}');` +
    `if(!el){el=document.createElement('style');el.id='${styleId}';document.head.appendChild(el);}` +
    `el.textContent=\`${safeCss}\`;` +
    `})()`;
  this.webController.runJavaScript(js).catch(() => {});
}

private removeCss(styleId: string): void {
  this.webController.runJavaScript(
    `(function(){var el=document.getElementById('${styleId}');if(el)el.remove();})()`
  ).catch(() => {});
}
```

### 2. JS 执行原则

1. **IIFE 包裹** — 所有注入的 JS 用 `(function(){ ... })()` 包裹，防止全局变量污染
2. **catch 兜底** — `runJavaScript()` 返回 Promise，必须 `.catch()` 防止页面异常导致崩溃
3. **大文件分块** — rawfile 加载的 JS/CSS 文件（如 Readability.js）需用分块 `uint8ArrayToString()`，否则 `String.fromCharCode(...spread)` 会栈溢出
4. **返回值反序列化** — `runJavaScript` 返回的是 JS 表达式结果的 **JSON 字符串化**形式，字符串会被外层引号包裹、内部换行/引号会被转义，需手动 strip + unescape

### 3. WebView 内 fetch 调用外部 API

当需要调用外部 HTTP API 处理页面内容时，优先在 **WebView JS 环境内用 `fetch()`** 完成，而非 ArkTS native HTTP 模块。

**优势**：
- 一次 `runJavaScript` 完成"采集 → 调 API → 回写 DOM"全流程，无需多轮 ArkTS ↔ JS 通信
- JS 中可直接操作 DOM 节点引用，不需要构建序列化映射

**适用场景**：页面原地翻译、内容摘要提取、文本标注等需要"读取 DOM → 调外部服务 → 修改 DOM"的功能。

**注意**：JS 中 `fetch()` 返回 Promise，`runJavaScript` 会自动等待异步结果。

### 4. 样式持久化

WebView 页面导航后，注入的 `<style>` 元素会丢失。解决方案：

```
onPageEnd 回调 → 检查所有样式开关状态 → 重新注入已开启的样式
```

在 `onPageEnd` 中调用 `reapplyStyles()` 函数统一处理，比在每个 toggle 函数中分别持久化更干净。

### 5. WebView 间通信（分屏场景）

两个 WebView 之间无法直接通信。已验证的方案：**借用 `document.title` 通道**。

- 发送方：通过 JS 设置 `document.title = '__MSG_TYPE__' + payload`
- 接收方：在 `onTitleReceive` 回调中检测前缀，拦截处理，不更新真实标题

## ArkTS 特有注意事项

| 问题 | 说明 |
|------|------|
| 无 `TextEncoder` / `TextDecoder` | 使用 `import { util } from '@kit.ArkTS'` → `new util.TextEncoder()` |
| 无全局 `URL` 类 | 手动解析字符串（`indexOf('://')` + `indexOf('/')`），不能 `new URL(str)` |
| 无 `{ ...obj }` 展开 | 逐字段构造新对象代替对象展开 |
| rawfile 返回 `Uint8Array` | 需用分块 `uint8ArrayToString()` 转换，每 8192 字节一块 |
| `runJavaScript` 返回值 | 字符串结果被 JSON 化（外层引号 + 转义），需 strip 引号 + `replace(/\\n/g, '\n')` 等反转义 |
| `runJavaScript` + 异步 JS | JS 中返回 Promise 时，`runJavaScript` 会等待 resolve 后返回结果字符串 |


## 其他官方参考文档

- [WebviewController API 文档](https://developer.huawei.com/consumer/cn/doc/harmonyos-references/js-apis-webview)
- [Web 组件开发指南](https://developer.huawei.com/consumer/cn/forum/topic/0201894660337260403)

