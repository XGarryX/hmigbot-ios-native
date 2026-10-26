# Layer 3 Layout 陷阱大全

> **触发条件**：沉浸式架构铺好了（Layer 1+2 都对），但页面仍然出现"顶部小白边"、"Hero 不从 y=0 开始"、"BottomBar 飘到顶部"、"中间内容不可点击"等怪象。这些 99% 是 Layer 3 layout 写法触发了 ArkUI 的 layout 异常路径。

## 通用规律

ArkUI 在某些 layout 组合下会**自动启用** NavDestination 的 safeArea inset（让位状态栏），间接打破 Layer 2 的 expandSafeArea 效果。这种"自动让位"是 ArkUI 内部行为，无法直接关闭，只能通过避免触发的 layout 写法绕开。

定位时**强烈建议用 ArkUI Inspector 看 Image y 坐标**：
- y=0：穿透成功
- y ≈ windowTopPadding（28-44vp）：Layer 2 expandSafeArea 没生效或被自动让位
- y > 100vp：Stack 内多 child 100% 触发的严重 layout 偏移

---

## 陷阱 1：Scroll 同时设 `.height('100%')` + `.layoutWeight(1)`

### 现象
Hero 顶部出现 ≈windowTopPadding 高度的微小白边。

### 原因
ArkUI 看到 Scroll 显式有 height 后切换 layout 路径，间接触发 NavDestination 自动让位 safeArea。

### 修复
```ts
// ❌ 错
Scroll() { ... }
  .height('100%')      // ← 删掉这行
  .layoutWeight(1)

// ✅ 对
Scroll() { ... }
  .layoutWeight(1)     // 只用 layoutWeight，让 Scroll 完全靠 Flex 主轴分配剩余空间
```

---

## 陷阱 2：HeroSection 内容 height 不一致 / 混用 `'100%'`

### 现象
Hero 整体可见但顶部有微小白边，Image y 坐标 ≈30vp。

### 原因
Stack 内子组件 height 不一致（如 Stack=523、子 Column=276、子 Image=`'100%'`），Stack 内 layout 计算异常。

### 修复
**Stack height + 所有子组件 height 必须用同一个具体数值**（与 CourseSinglePage 500/500、CourseMultiPage 276/276 模式相同）：

```ts
// ❌ 错
Stack() {
  Column().width('100%').height(276).backgroundColor(...)   // 276
  Image(...).width('100%').height('100%').objectFit(...)    // ← '100%' 相对值
}
.width('100%')
.height(523)   // ← Stack 523 但子 Column 是 276 ←【height 三者不一致】

// ✅ 对
Stack() {
  Column().width('100%').height(523).backgroundColor(...)   // 523
  Image(...).width('100%').height(523).objectFit(...)       // 523
}
.width('100%')
.height(523)   // 三者都是 523
```

---

## 陷阱 3：Stack 内多个并列的 `.height('100%')` 兄弟 child

### 现象
Hero Image y 坐标 ≈ 130-400vp（不是 0），整个 Stack 起点被推下。

### 原因
ArkUI Stack 内多个 100% child 触发 layout 异常，整个 Stack 实际起点被推下 ≈130vp。典型出错组合：Scroll 100% + 浮层 BottomBar Column 100%。

### 修复
用经典"Column wrapper 上下分段"：Scroll 用 `layoutWeight(1)` + BottomBar 用固定 height，**Stack 只留一个 height 100% child**（Column wrapper）：

```ts
// ❌ 错（Stack 三个并列 child，两个 100%）
Stack({ alignContent: TopStart }) {
  Scroll() { ... }.width('100%').height('100%')           // ← 100% #1
  Column() { BottomBar() }.height('100%')                  // ← 100% #2  
                                                           //   .align(Bottom) 想让它沉底
  TopBar()
}

// ✅ 对（Stack 只有 1 个 100% child = Column wrapper）
Stack({ alignContent: TopStart }) {
  Column() {
    Scroll() { ... }.layoutWeight(1)                       // 占用剩余空间
    BottomBar()                                            // 固定 height（如 60vp）
  }.width('100%').height('100%')                           // ← 唯一 100% child
  TopBar()
}
```

---

## 陷阱 4：BottomBar 用 `.align(Alignment.Bottom)` / `.position` 浮层

### 现象
BottomBar 飘到顶部，或位置不可控随设备变化。

### 原因
在 ArkUI 某些版本下 Stack 子组件的 `.align(Bottom)` modifier 不可靠（陷阱 3 也是它的连锁反应）。

### 修复
老老实实用 Column wrapper 双段（CourseMultiPage 模式），不要用 Stack 浮层方式做 BottomBar。

---

## 陷阱 5：Hero 高度补偿 `windowTopPadding`

### 现象
状态栏区域显示一片纯色，没有 Hero 图穿透。

### 错误想法
"Hero 加 windowTopPadding 高度让位状态栏"。

### 原因
沉浸式架构下 Hero 应该**自然铺到屏幕物理顶 y=0**，状态栏区域**显示 Hero 顶部 ≈30vp 内容**（设计预期就是这样，状态栏文字浮在图片上）。

### 修复
用 Android 原始设计稿数值固定（如 276vp / 500vp），不加补偿：

```ts
// ❌ 错
Stack() { ... }
  .height(276 + this.windowModel.windowTopPadding)   // ← 不要补偿

// ✅ 对
Stack() { ... }
  .height(276)   // Android 原始设计稿值
```

---

## 陷阱 6：Stack 子组件用 `.layoutWeight(1)` 想铺满

### 现象
组件高度不确定，可能被父收缩到 0 或异常拉伸。

### 原因
`.layoutWeight()` 是 **Flex 容器（Row/Column）的主轴分配**，**Stack 子组件无效**。

### 修复
Stack 子组件铺满改用 `.width('100%').height('100%')`（注意陷阱 3：同一 Stack 内只允许 1 个 100% child）。

---

## 自检 Checklist

改完 Layer 3 layout 后对照检查：

- [ ] Scroll 没同时设置 `.height('100%')` + `.layoutWeight(1)`（**只用 layoutWeight**）
- [ ] HeroSection 内 Stack height + 子 Column height + 子 Image height **三个数值完全一致**（如 `276/276/276` 或 `500/500/500`），**没有用 `'100%'` 相对值**
- [ ] HeroSection 不补偿 windowTopPadding（按设计稿原值 276 / 500，让 Hero 自然铺到屏幕物理顶）
- [ ] Stack 内**没有多个并列的 `height('100%')` 兄弟 child**（典型坑：Scroll 100% + 浮层 BottomBar Column 100% → Image y=391px 而非 0）
- [ ] BottomBar 用 Column wrapper 双段模式（Column { Scroll layoutWeight(1) + BottomBar 固定 height }），**不要**把 BottomBar 当作 Stack 的并列 child 用 `align(Bottom)` 浮层
- [ ] Stack 子组件**没用** `.layoutWeight()`（Stack 是层叠容器不是 Flex，layoutWeight 无效；用 `width('100%').height('100%')` 铺满）

## 诊断 Inspector 用法

打开 ArkUI Inspector → 选中 Hero Image → 看 Component 详情面板的 `position` / `globalPosition` 字段：
- **y=0**：Layer 2 + Layer 3 都对了
- **y ≈ 28-44vp**：Layer 3 触发了自动让位（陷阱 1 或 2）
- **y > 100vp**：Stack 内多 100% child 异常（陷阱 3）
