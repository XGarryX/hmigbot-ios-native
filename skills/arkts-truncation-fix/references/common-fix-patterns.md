# 常见截断问题修复模式速查表

## 目录

1. [安全区遮挡](#1-安全区遮挡)
2. [硬编码尺寸](#2-硬编码尺寸)
3. [内容溢出无滚动](#3-内容溢出无滚动)
4. [折叠屏悬停失败](#4-折叠屏悬停失败)
5. [文本截断](#5-文本截断)
6. [断点系统缺失](#6-断点系统缺失)
7. [布局容器选择](#7-布局容器选择)
8. [AlphabetIndexer 溢出](#8-alphabetindexer-溢出)
9. [Tabs 双栏问题](#9-tabs-双栏问题)
10. [底部安全区导航栏](#10-底部安全区导航栏)

---

## 1. 安全区遮挡

### 症状
- 状态栏遮住顶部标题
- 底部导航指示条遮住操作按钮
- 刘海/挖孔区域覆盖内容

### 错误写法

```typescript
// 错误 1：魔术数字手动避让
Column() {
  Text("标题").margin({ top: 44 })  // 44 在某些设备上不够
}

// 错误 2：padding 放错容器
Column() {
  Column() { this.HeaderArea() }  // 头部没有 padding
  Column() { this.ContentArea() }
    .padding({ top: statusBarHeight })  // 应该加在头部上
}

// 错误 3：topAvoidHeight 声明了没赋值
@Local topAvoidHeight: number = 0       // V2；V1 等价 @State topAvoidHeight: number = 0
// aboutToAppear() 为空
```

### 正确写法

```typescript
// V2（项目锁 V2，推荐）；V1 等价见下方对照
@Local safeTopVp: number = 0;
@Local safeBottomVp: number = 0;

aboutToAppear(): void {
  window.getLastWindow(this.getUIContext().getHostContext()).then((win) => {
    this.updateSafeInsets(win);
    win.on('avoidAreaChange', () => this.updateSafeInsets(win));
  });
}

private updateSafeInsets(win: window.Window): void {
  const systemArea = win.getWindowAvoidArea(window.AvoidAreaType.TYPE_SYSTEM);
  const cutoutArea = win.getWindowAvoidArea(window.AvoidAreaType.TYPE_CUTOUT);
  const navArea = win.getWindowAvoidArea(window.AvoidAreaType.TYPE_NAVIGATION_INDICATOR);
  this.safeTopVp = px2vp(Math.max(
    systemArea.topRect.top + systemArea.topRect.height,
    cutoutArea.topRect.top + cutoutArea.topRect.height, 0));
  this.safeBottomVp = px2vp(Math.max(navArea.bottomRect.height, 0));
}

// 根容器上应用
Column() { /* ... */ }
  .padding({ top: this.safeTopVp, bottom: this.safeBottomVp })
```

---

## 2. 硬编码尺寸

### 症状
- 手机正常，平板或折叠屏上留白过多或内容太小
- 窄屏上文字/图片超出边界

### 错误写法

```typescript
Text("标题").fontSize(30)          // 小屏太大，大屏太小
Image(src).width(120).height(160)  // 固定比例不适配
Row().width(360).height(100)       // 超出窄屏
```

### 正确写法

```typescript
// 用 BreakpointType 按设备选值
private titleFont = new BreakpointType(18, 22, 26, 30);
Text("标题").fontSize(this.titleFont.getValue(bp))

// 图片用 aspectRatio
Image(src).width('100%').aspectRatio(3/4).objectFit(ImageFit.Cover)

// 宽度用百分比 + 最大宽度
Row().width('90%').constraintSize({ maxWidth: 600 })

// 间距也响应式
private sidePadding = new BreakpointType(12, 16, 24, 32);
```

---

## 3. 内容溢出无滚动

### 症状
- 聊天引用预览撑破底部栏
- 长文本超出可见区域，底部看不到
- 列表项过多，底部内容被遮挡

### 错误写法

```typescript
// 引用预览无约束
Column() {
  if (this.referenceMessage) {
    Row() { /* 引用内容 */ }  // 可能无限增长
  }
  Row() { /* 输入框 */ }
}
```

### 正确写法

```typescript
Column() {
  if (this.referenceMessage) {
    Scroll() {
      Column() {
        Row() { /* 引用内容 */ }
      }.width('100%')
    }
    .scrollBar(BarState.Off)
    .constraintSize({ maxHeight: this.getRefMaxHeight(bp) })
  }
  Row() { /* 输入框，保证可见 */ }
}

private getRefMaxHeight(bp: string): number {
  return bp === 'xs' ? 60 : 120;
}
```

对于列表 + 固定底栏的布局：

```typescript
Column() {
  TitleBar().height(56)                    // 固定顶部
  List().layoutWeight(1)                   // 自适应中间
  BottomBar().height(52)                   // 固定底部
}
```

---

## 4. 折叠屏悬停失败

### 症状
- 折叠屏展开后布局不变化
- 悬停模式（hover mode）不生效
- 内容横跨折痕区域

### 错误写法

```typescript
// 遇到旋转就放弃
if (needQuarterTurn) {
  this.resetHoverLayoutState();
  return;  // 直接退出，悬停模式完全不工作
}
```

### 正确写法

```typescript
// 监听折叠状态
display.on('foldStatusChange', (status) => {
  this.foldStatus = status;
  this.isHoverMode = (status === 0);  // EXPANDED
});

// 方向切换加防抖
private scheduleOrientation(target: number, delayMs: number): void {
  clearTimeout(this.orientTimer);
  this.orientTimer = setTimeout(() => {
    window.getLastWindow(this.context).then(w => w.setPreferredOrientation(target));
  }, delayMs);
}

// 悬停布局 — 按折痕分两屏
if (this.isHoverMode) {
  if (this.isVerticalCrease) {
    this.VerticalHoverLayout();
  } else {
    this.HorizontalHoverLayout();
  }
}
```

---

## 5. 文本截断

### 症状
- 长文字被直接裁切，看不到省略号
- 文字撑破容器，破坏其他元素布局
- 横向列表中文字溢出

### 错误写法

```typescript
Text(longTitle)  // 无 maxLines，无 textOverflow
```

### 正确写法

```typescript
// 单行
Text(longTitle)
  .maxLines(1)
  .textOverflow({ overflow: TextOverflow.Ellipsis })

// 多行
Text(description)
  .maxLines(2)
  .textOverflow({ overflow: TextOverflow.Ellipsis })

// Row 中的文本需要 layoutWeight 或 maxWidth
Row() {
  Image(avatar).width(40)
  Text(name)
    .layoutWeight(1)
    .maxLines(1)
    .textOverflow({ overflow: TextOverflow.Ellipsis })
  Text(time)
}

// 消息气泡
Text(msg)
  .constraintSize({ maxWidth: '72%' })
```

---

## 6. 断点系统缺失

### 症状
- 所有设备显示完全相同的布局
- 平板上大量空白，手机上过于拥挤

### 快速接入方案

```typescript
// 1. 定义断点常量
static readonly BP_SM = 600;
static readonly BP_MD = 840;
static readonly BP_LG = 1440;

// 2. 监听窗口大小
win.on('windowSizeChange', (size) => {
  const w = px2vp(size.width);
  if (w < BP_SM) this.breakpoint = 'sm';
  else if (w < BP_MD) this.breakpoint = 'md';
  else if (w < BP_LG) this.breakpoint = 'lg';
  else this.breakpoint = 'xl';
});

// 3. 按断点切换布局
build() {
  if (this.isLargeScreen()) {
    this.DualPaneLayout();
  } else {
    this.SinglePaneLayout();
  }
}
```

---

## 7. 布局容器选择

### 何时用什么

| 场景 | 推荐容器 | 原因 |
|------|---------|------|
| 顶部固定 + 中间滚动 + 底部固定 | `Column` + `layoutWeight(1)` | 中间自动填满 |
| 侧边索引 + 主内容 | `RelativeContainer` 或 `Stack` | 绝对定位侧边栏 |
| 双栏/多栏布局 | `Row` + `layoutWeight` 或百分比 | 按比例分配空间 |
| 内容自适应居中 + 限宽 | `Column` + `constraintSize({ maxWidth })` | 大屏不会过宽 |
| 卡片网格 | `Grid` + `columnsTemplate` 按断点变列数 | 响应式网格 |
| 消息气泡（左右对齐） | `Row` + `justifyContent` | 按发送方向对齐 |

---

## 8. AlphabetIndexer 溢出

### 典型问题

AlphabetIndexer 组件在 RelativeContainer 中定位时，如果主内容 List 没有给索引器留出右侧空间，会导致：
- 索引字母覆盖在列表文字上方
- 索引器在窄屏上超出屏幕右边缘

### 修复

```typescript
RelativeContainer() {
  List() {
    // ...
  }
  .id('mainList')
  .alignRules({
    top: { anchor: '__container__', align: VerticalAlign.Top },
    bottom: { anchor: '__container__', align: VerticalAlign.Bottom },
    left: { anchor: '__container__', align: HorizontalAlign.Start },
    right: { anchor: '__container__', align: HorizontalAlign.End }
  })

  AlphabetIndexer({ arrayValue: this.alphabets, selected: this.selectedIndex })
    .alignRules({
      top: { anchor: '__container__', align: VerticalAlign.Top },
      bottom: { anchor: '__container__', align: VerticalAlign.Bottom },
      right: { anchor: '__container__', align: HorizontalAlign.End }
    })
}
```

如果索引器遮挡内容，给 List 的列表项加右侧 padding：

```typescript
ListItem() {
  Row() {
    Text(contact).margin({ left: 20 })
  }
  .padding({ right: 40 })  // 给 AlphabetIndexer 留空间
}
```

---

## 9. Tabs 双栏问题

### 典型问题

使用自定义 TabBar 时，系统默认 TabBar 仍然显示，浪费垂直空间（56px）。

### 修复

```typescript
Tabs({ barPosition: BarPosition.End }) {
  // ...
}
.barHeight(0)  // 隐藏系统 tab bar，使用自定义 tab bar
```

---

## 10. 底部安全区导航栏

### 典型问题

底部 padding 放在根容器上导致所有子元素都被推上去，而不是只让底栏避让。

### 修复

```typescript
// 错误：padding 放在根容器
Stack() {
  Tabs()
  CustomTabBar()
}.padding({ bottom: safeBottom })  // 所有内容都受影响

// 正确：padding 放在自定义 TabBar 上
Stack() {
  Tabs()
  CustomTabBar()
    .padding({ bottom: this.safeBottomVp })  // 只有 TabBar 避让
}
```
