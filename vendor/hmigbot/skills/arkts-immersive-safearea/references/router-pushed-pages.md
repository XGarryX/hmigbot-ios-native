# 场景 E：router.pushUrl 跳转的独立 @Entry 页

> **触发条件**：page 不是 MainPage Tab 内容、不是 NavPathStack 子页，而是 `router.pushUrl({ url: 'pages/Xxx' })` 直跳转的独立 page（典型：课程详情、设置、编辑器、详情页）。

## 与 MainPage 子页的根本区别

| | MainPage Tab 子页 | router.pushUrl 独立页 |
|---|---|---|
| 父级容器 | NavPathStack（基座） | 无（独立 @Entry） |
| Layer 2 谁负责 | 基座 Navigation | **本页根容器自己** |
| 需要在 page 写 `expandSafeArea` | 否 | **是（必须四向）** |
| 需要 `hideTitleBar(true)` | 是 | 是 |

## 两条铁律

1. **Layer 2 责任搬到 page 自己根容器上**：page 的根 Stack/Column 必须自己声明四向 `expandSafeArea([SYSTEM, CUTOUT], [START, END, TOP, BOTTOM])`，否则 NavDestination 默认让位 safeArea，Hero 不能穿透到 y=0。
2. **NavDestination 仍然要保留 + `hideTitleBar(true)`**：项目里这种 page 通常 build 第一层是 `NavDestination()` 包装（即使不在 NavPathStack 体系里，ArkUI 也接受这种用法）。`hideTitleBar(true)` 必须，否则视觉上会有顶部空白 title bar。

---

## 完整模板（带 Hero + 滚动 + BottomBar）

```ts
@Entry
@ComponentV2
struct DetailPage {
  @Local windowModel: WindowModel = AppStorageV2.connect(WindowModel, () => new WindowModel())!

  build() {
    NavDestination() {
      Stack({ alignContent: Alignment.TopStart }) {
        Column() {
          Scroll() {
            Column() {
              this.HeroSection()
              this.InfoCard()
            }.width('100%')
          }
          .layoutWeight(1)              // ← 只用 layoutWeight，不要再加 .height('100%')！
          .scrollBar(BarState.Off)

          this.BottomBar()              // 固定 height（如 60vp），不用 layoutWeight
        }
        .width('100%')
        .height('100%')

        this.TopBar()                   // 浮顶层
      }
      .width('100%').height('100%')
      .backgroundColor(Color.White)
      // 🔑 关键：四向 expandSafeArea 必须加在最外层 Stack 上
      .expandSafeArea(
        [SafeAreaType.SYSTEM, SafeAreaType.CUTOUT],
        [SafeAreaEdge.START, SafeAreaEdge.END, SafeAreaEdge.TOP, SafeAreaEdge.BOTTOM]
      )
    }
    .hideTitleBar(true)
  }
}
```

---

## 容易踩坑的 layout 细节（强相关，详见 layout-traps.md）

router.pushUrl 跳转 + Hero + 滚动 + BottomBar 的组合，是 layout 陷阱的高发场景：

- **Scroll 不要同时设 `.height('100%')` + `.layoutWeight(1)`** — 删掉 `.height('100%')`，否则 ArkUI 切换 layout 路径，间接触发 NavDestination 自动让位 safeArea → 顶部出现 ≈windowTopPadding 高的微小白边。
- **HeroSection 内 Stack height + 子 Column height + 子 Image height 三者必须用同一个具体数值**（如 `276/276/276` 或 `500/500/500`），**不能混用 `'100%'` 相对值**。
- **Hero 不补偿 windowTopPadding**：用 Android 原始设计稿数值固定（如 276vp / 500vp），让 Hero 自然铺到屏幕物理顶 y=0，状态栏文字浮在图片上。
- **不要把 BottomBar 当作 Stack 的并列 child + `.align(Bottom)` 浮层**：用经典 Column wrapper 上下分段（Scroll layoutWeight(1) + BottomBar 固定 height），Stack 只留一个 height 100% child。

---

## 自检 Checklist

- [ ] page 根容器加了**四向** `expandSafeArea([SYSTEM, CUTOUT], [START, END, TOP, BOTTOM])`
- [ ] `NavDestination` 外层加了 `.hideTitleBar(true)`
- [ ] 没在外层 Stack 之外（如 NavDestination 自己）写第二次 `expandSafeArea`
- [ ] Scroll 只用 `.layoutWeight(1)`，**没有**同时 `.height('100%')`
- [ ] Hero 内 Stack/Column/Image height **数值一致**，不混用 `'100%'`
- [ ] Hero 高度按设计稿原值（不加 `+ windowTopPadding`）
- [ ] BottomBar 走 Column wrapper 双段（不是 Stack 浮层）
- [ ] TitleBar/TopBar 浮层 padding-top 用了 `windowTopPadding + N`
- [ ] BottomBar margin-bottom 用了 `N + windowBottomPadding`
