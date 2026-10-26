# 场景 F：H5 容器（Web 组件壳页）的沉浸式

> **触发条件**：会员中心、活动页等"H5 渲染主体内容、native 仅做容器"的页面。代码特征：根组件是 `Web({...})`，与 jsBridge 通信（`handleClosePage` / `getToken` 等），有 Webview controller。

## 与原生 page 沉浸式的根本差异

H5 容器的状态栏让位**由 H5 自己处理**（CSS `env(safe-area-inset-top)`）。native 仅负责让 Web 物理铺满屏幕。

| | 普通原生 page | H5 容器 page |
|---|---|---|
| 谁负责让位状态栏 | native（padding-top: windowTopPadding）| **H5**（`env(safe-area-inset-top)`）|
| native 是否加 padding-top | 是 | **绝对不加** |
| TitleBar | 通常自绘 | 通常完全移除（H5 内自渲染）|
| 关闭按钮 | 原生 X 按钮 | H5 内 X 按钮 + jsBridge |

---

## 四条核心规则

### 1. native 端不要给 Web 加 padding-top

加了反而让 H5 顶部出现空白条，状态栏区域既不显示 H5 渐变也不显示原生背景。**H5 自己用 CSS 处理 safe-area-inset 避让**。

### 2. TitleBar 通常完全移除

先看 Android 同款页面 XML（如 `cs_vip_webview_activity.xml`）。如果 Android 也无原生 TitleBar、X 关闭按钮由 H5 自己渲染，那 HOS 端**也不要**加任何 native TitleBar 或浮层 X。

### 3. 关闭路径有 3 条，必须语义一致

| 路径 | 触发方式 |
|---|---|
| 物理返回键 | `onBackPress()` |
| H5 内 X 关闭按钮 | jsBridge `handleClosePage` 通知 native |
| H5 挽留弹窗后用户确认关闭 | 同 `handleClosePage`（通常带 retention 参数）|

如果有 `closeToHome` 这类语义（Gather/Scheme 入口避免回到死栈），**三条路径都要判断**，否则会出现"X 按钮回死栈、物理返回键回 MainPage"的不一致。

### 4. 加载进度条用浮层，不参与 layout 流

进度条若作为 Column/Stack 的 layout child，会挤占 Web 高度（哪怕只 2vp）→ Web 不再铺满屏幕。改用 `.position({y: windowTopPadding})` 让进度条浮在状态栏底，不影响 Web 尺寸。

---

## 完整模板

```ts
@Entry
@ComponentV2
struct VipH5Page {
  @Local windowModel: WindowModel = AppStorageV2.connect(WindowModel, () => new WindowModel())!
  @Local progress: number = 0
  @Local closeToHome: boolean = false
  private controller: webview.WebviewController = new webview.WebviewController()

  // jsBridge handler 路径 1：H5 内 X 关闭按钮
  private handleBridgeMessage(msg: BridgeMessage): void {
    switch (msg.handlerName) {
      case 'handleClosePage':
        // ✅ 与 onBackPress 同样判断 closeToHome
        if (this.closeToHome) {
          router.replaceUrl({ url: 'pages/MainPage' })
        } else {
          router.back()
        }
        break
      // ... 其他 handler
    }
  }

  // 路径 2：物理返回键
  onBackPress(): boolean {
    // ... WebView backward 优先
    if (this.closeToHome) {
      router.replaceUrl({ url: 'pages/MainPage' })
      return true
    }
    return false
  }

  build() {
    NavDestination() {
      Stack({ alignContent: Alignment.TopStart }) {
        // ① Web 铺满整个 Stack（含状态栏区域）
        Web({ src: '', controller: this.controller })
          .javaScriptAccess(true)
          .domStorageAccess(true)
          // ... 其他配置
          .width('100%')
          .height('100%')          // ✅ 不能用 layoutWeight（Stack 子组件无效）

        // ② 加载进度条用 position 浮层，不挤占 Web 高度
        if (this.progress > 0 && this.progress < 100) {
          Progress({ value: this.progress, total: 100, type: ProgressType.Linear })
            .width('100%').height(2)
            .position({ x: 0, y: this.windowModel.windowTopPadding })
        }
      }
      .width('100%').height('100%')
      // ③ 场景 F = 场景 E 的子集：router.pushUrl 跳转 → 自己加四向 expandSafeArea
      .expandSafeArea(
        [SafeAreaType.SYSTEM, SafeAreaType.CUTOUT],
        [SafeAreaEdge.START, SafeAreaEdge.END, SafeAreaEdge.TOP, SafeAreaEdge.BOTTOM]
      )
    }
    .hideTitleBar(true)
    .onBackPressed(() => this.onBackPress())
  }
}
```

---

## 改造前必做：用 ArkUI Inspector 确认入口

> ⚠️ 项目里"会员中心"可能有多个候选 page（VIPCenterPage / VipH5Page / VIPCenterExPage），看文件名容易猜错。

**操作步骤**：让用户实际打开页面 → ArkUI Inspector 截图 → 看 Component Tree 根节点是哪个 page 文件 → 再下手改。

否则可能改了一个不被路由触发的兜底页，用户测试发现"完全没生效"。

---

## 自检 Checklist

- [ ] 改造前已用 ArkUI Inspector 确认实际入口 page
- [ ] 已查 Android 同款 page XML，确认是否需要原生 TitleBar；如果不需要则**完全移除** TitleBarComponent
- [ ] native 端**不**给 Web 加 `padding-top: windowTopPadding`
- [ ] Web 用 `width('100%').height('100%')`（不用 layoutWeight，因 Stack 容器无效）
- [ ] 加载进度条用 `.position({y: windowTopPadding})` 浮层，不参与 layout 流
- [ ] 关闭路径三处对齐 `closeToHome` 语义：`onBackPress` / `handleClosePage` jsBridge / `handleRetention` 后的 close（建议抽取统一 close 函数）
- [ ] 根 Stack 加了四向 `expandSafeArea`（与场景 E 一致）
- [ ] `NavDestination` 外层加了 `.hideTitleBar(true)`
