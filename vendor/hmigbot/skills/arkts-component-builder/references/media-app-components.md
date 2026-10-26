# 媒体应用组件模式（**V1 历史文档 — Legacy**）

> ⚠️ **本项目锁 ArkTS V2**。本文档示例采用 **V1 装饰器写法**（`@Component / @StorageLink / @Prop`），仅用于阅读老代码或迁移老项目时查阅。
>
> **新代码请使用 V2 装饰器**：参阅 [`v2-media-app-components.md`](./v2-media-app-components.md)（V2 主参考，使用 `@ComponentV2 / @ObservedV2 + @Trace + AppStorageV2.connect / @Param`）。

> 基于 AntennaPod ArkTS 播客应用实战总结的 4 种组件模式：MiniPlayer、自定义 Tab 栏、封面图 + fallback、空状态组件。
> 源码参考：`entry/src/main/ets/pages/Index.ets`、`entry/src/main/ets/components/common/EmptyStateView.ets`

---

## 1. MiniPlayer 模式 — 底部浮动播放条

MiniPlayer 放置在 `Navigation` 外部、Tab 栏上方，通过 `@StorageLink` 驱动显隐和内容。
FullPlayer 打开时 MiniPlayer 自动隐藏（`isFullPlayerVisible` 控制）。

**关键设计点**：
- 进度条使用 `Progress(Linear)` 贴顶，视觉上无缝连接内容区
- 封面图有无两态（Image / Text 首字母 fallback）
- 播放/暂停按钮使用 `SymbolGlyph` 动态切换图标
- 点击整个 MiniPlayer 跳转到 FullPlayer
- 播放/暂停按钮单独响应点击（`onClick` 阻止冒泡）

```typescript
// 文件: pages/Index.ets (行 152-226)
// MiniPlayer — always above tab bar, hidden when FullPlayer is open
if (this.isPlayerVisible && !this.isFullPlayerVisible) {
  Column() {
    Progress({ value: this.getProgressPercent(), total: 100, type: ProgressType.Linear })
      .height(2)
      .width('100%')
      .color('#007DFF')
      .backgroundColor('#E0E0E0')

    Row() {
      if (this.currentCoverUrl.length > 0) {
        Image(this.currentCoverUrl)
          .width(40)
          .height(40)
          .borderRadius(6)
          .objectFit(ImageFit.Cover)
          .margin({ right: 10 })
      } else {
        Column() {
          Text(this.currentFeedTitle.length > 0 ? this.currentFeedTitle.charAt(0).toUpperCase() : '?')
            .fontSize(18)
            .fontWeight(FontWeight.Bold)
            .fontColor(Color.White)
        }
        .width(40)
        .height(40)
        .borderRadius(6)
        .backgroundColor('#BDBDBD')
        .justifyContent(FlexAlign.Center)
        .alignItems(HorizontalAlign.Center)
        .margin({ right: 10 })
      }

      Column() {
        Text(this.currentEpisodeTitle.length > 0 ? this.currentEpisodeTitle : 'No episode playing')
          .fontSize(14)
          .maxLines(1)
          .textOverflow({ overflow: TextOverflow.Ellipsis })
        if (this.currentFeedTitle.length > 0) {
          Text(this.currentFeedTitle)
            .fontSize(12)
            .fontColor('#99000000')
            .maxLines(1)
            .textOverflow({ overflow: TextOverflow.Ellipsis })
        }
      }
      .layoutWeight(1)
      .alignItems(HorizontalAlign.Start)

      Column() {
        SymbolGlyph(this.isPlaying ? $r('sys.symbol.pause_fill') : $r('sys.symbol.play_fill'))
          .fontSize(20)
          .fontColor(['#333333'])
      }
      .width(36)
      .height(36)
      .borderRadius(18)
      .backgroundColor('#E8E8E8')
      .justifyContent(FlexAlign.Center)
      .alignItems(HorizontalAlign.Center)
      .margin({ left: 8 })
      .onClick(() => {
        PlaybackController.getInstance().playPause();
      })
    }
    .padding({ left: 12, right: 16, top: 8, bottom: 8 })
    .width('100%')
  }
  .width('100%')
  .backgroundColor('#FAFAFA')
  .shadow({ radius: 4, color: '#1A000000', offsetY: -2 })
  .onClick(() => {
    this.navPathStack.pushPathByName(RouteName.FULL_PLAYER, new Object());
  })
}
```

**@StorageLink 驱动的状态**（在 GlobalState 中初始化）：

```typescript
@StorageLink('isPlayerVisible') isPlayerVisible: boolean = false;
@StorageLink('isPlaying') isPlaying: boolean = false;
@StorageLink('currentEpisodeTitle') currentEpisodeTitle: string = '';
@StorageLink('currentFeedTitle') currentFeedTitle: string = '';
@StorageLink('playbackPosition') playbackPosition: number = 0;
@StorageLink('playbackDuration') playbackDuration: number = 0;
@StorageLink('currentCoverUrl') currentCoverUrl: string = '';
@StorageLink('isFullPlayerVisible') isFullPlayerVisible: boolean = false;
```

**进度百分比计算**：

```typescript
private getProgressPercent(): number {
  if (this.playbackDuration > 0 && this.playbackPosition > 0) {
    return Math.round(this.playbackPosition * 100 / this.playbackDuration);
  }
  return 0;
}
```

---

## 2. 自定义 Tab 栏 — @Builder tabBarItem

使用 `@Builder` 构建自定义 Tab 项，支持 Material 3 风格药丸指示器。
不使用系统 `Tabs` 组件，而是 `Row` + `if/else` 手动切换 Tab 内容。

**为什么不用系统 Tabs**：
- 系统 Tabs 的 tabBar 定制灵活度不够（无法做药丸指示器）
- Navigation + 自定义 Tab Row 可以让 MiniPlayer 浮在 Tab 栏上方

```typescript
// 文件: pages/Index.ets (行 83-111)
@Builder
tabBarItem(index: number, title: Resource, icon: Resource) {
  Column() {
    // Pill-shaped gray background for selected tab icon (Material 3 style)
    Column() {
      SymbolGlyph(icon)
        .fontSize(22)
        .fontColor(this.currentTabIndex === index ?
          [Color.Black] : ['#99182431'])
    }
    .width(48)
    .height(28)
    .borderRadius(14)
    .backgroundColor(this.currentTabIndex === index ? '#1F000000' : '#00000000')
    .justifyContent(FlexAlign.Center)
    .alignItems(HorizontalAlign.Center)

    Text(title)
      .fontSize(10)
      .fontColor(this.currentTabIndex === index ? '#182431' : '#99182431')
      .margin({ top: 2 })
  }
  .layoutWeight(1)
  .justifyContent(FlexAlign.Center)
  .height('100%')
  .onClick(() => {
    this.currentTabIndex = index;
  })
}
```

**药丸指示器关键属性**：

| 属性 | 值 | 说明 |
|------|------|------|
| `width` | 48 | 固定药丸宽度 |
| `height` | 28 | 固定药丸高度 |
| `borderRadius` | 14 | 高度的一半，形成圆角药丸 |
| `backgroundColor` | `'#1F000000'` / `'#00000000'` | 选中半透明黑 / 未选中全透明 |

**Tab 栏使用**：

```typescript
// 5 个 Tab 等分
Row() {
  this.tabBarItem(0, $r('app.string.tab_home'), $r('sys.symbol.house'))
  this.tabBarItem(1, $r('app.string.tab_queue'), $r('sys.symbol.list_bullet'))
  this.tabBarItem(2, $r('app.string.tab_inbox'), $r('sys.symbol.envelope'))
  this.tabBarItem(3, $r('app.string.tab_subscriptions'), $r('sys.symbol.square_grid_2x2'))
  this.tabBarItem(4, $r('app.string.tab_more'), $r('sys.symbol.line_3_horizontal'))
}
.width('100%')
.height(56)
.backgroundColor(Color.White)
.border({ width: { top: 0.5 }, color: '#E0E0E0' })
```

**Tab 内容切换**（if/else 而非 Tabs 组件）：

```typescript
Navigation(this.navPathStack) {
  if (this.dbReady) {
    if (this.currentTabIndex === 0) {
      HomeComponent()
    } else if (this.currentTabIndex === 1) {
      QueueComponent()
    } else if (this.currentTabIndex === 2) {
      InboxComponent()
    } else if (this.currentTabIndex === 3) {
      SubscriptionComponent()
    } else {
      MoreComponent()
    }
  }
}
```

---

## 3. 封面图 + fallback 模式

当图片 URL 存在时显示 `Image`，不存在时显示 `Text` 首字母 + 灰色背景。
此模式在 MiniPlayer、剧集列表项、Feed 网格项中反复使用。

```typescript
// 文件: pages/Index.ets (行 162-183)
if (this.currentCoverUrl.length > 0) {
  Image(this.currentCoverUrl)
    .width(40)
    .height(40)
    .borderRadius(6)
    .objectFit(ImageFit.Cover)
    .margin({ right: 10 })
} else {
  Column() {
    Text(this.currentFeedTitle.length > 0 ? this.currentFeedTitle.charAt(0).toUpperCase() : '?')
      .fontSize(18)
      .fontWeight(FontWeight.Bold)
      .fontColor(Color.White)
  }
  .width(40)
  .height(40)
  .borderRadius(6)
  .backgroundColor('#BDBDBD')
  .justifyContent(FlexAlign.Center)
  .alignItems(HorizontalAlign.Center)
  .margin({ right: 10 })
}
```

**通用化提取建议**：

```typescript
@Builder
function CoverImage(url: string, fallbackText: string, size: number) {
  if (url.length > 0) {
    Image(url)
      .width(size)
      .height(size)
      .borderRadius(size * 0.15)
      .objectFit(ImageFit.Cover)
  } else {
    Column() {
      Text(fallbackText.length > 0 ? fallbackText.charAt(0).toUpperCase() : '?')
        .fontSize(size * 0.45)
        .fontWeight(FontWeight.Bold)
        .fontColor(Color.White)
    }
    .width(size)
    .height(size)
    .borderRadius(size * 0.15)
    .backgroundColor('#BDBDBD')
    .justifyContent(FlexAlign.Center)
    .alignItems(HorizontalAlign.Center)
  }
}
```

---

## 4. 空状态组件

通用占位组件，用于列表/页面无数据时的提示。支持图标、提示文字、可选操作按钮。

```typescript
// 文件: components/common/EmptyStateView.ets
@Component
export struct EmptyStateView {
  @Prop icon: string = '';
  @Prop message: string = '';
  @Prop actionLabel: string = '';
  onAction: () => void = () => {};

  build() {
    Column() {
      if (this.icon.length > 0) {
        Text(this.icon)
          .fontSize(48)
          .margin({ bottom: 16 })
      }

      Text(this.message)
        .fontSize(16)
        .fontColor('#99000000')
        .textAlign(TextAlign.Center)
        .padding({ left: 32, right: 32 })

      if (this.actionLabel.length > 0) {
        Button(this.actionLabel)
          .fontSize(14)
          .margin({ top: 16 })
          .onClick(() => {
            this.onAction();
          })
      }
    }
    .width('100%')
    .layoutWeight(1)
    .justifyContent(FlexAlign.Center)
    .alignItems(HorizontalAlign.Center)
  }
}
```

**使用示例**：

```typescript
// 队列为空
EmptyStateView({
  icon: '📋',
  message: 'Your queue is empty.\nAdd episodes to start listening.',
  actionLabel: 'Browse Podcasts',
  onAction: () => {
    this.navPathStack.pushPathByName(RouteName.ADD_FEED, new Object());
  }
})

// 搜索无结果
EmptyStateView({
  icon: '🔍',
  message: 'No results found for your search.',
  actionLabel: '',
  onAction: () => {}
})
```

**设计要点**：
- 使用 `@Prop` 接收父组件传入的配置（单向绑定）
- `layoutWeight(1)` 让空状态组件填满剩余空间
- `justifyContent(FlexAlign.Center)` 垂直居中
- `onAction` 回调使用默认空函数，避免使用可选类型

---

## 整体页面结构

Index.ets 的整体布局层次：

```
Column (root)
├── Navigation (layoutWeight=1, 占满剩余空间)
│   ├── Tab 内容 (if/else 切换)
│   └── navDestination → routerMap
├── MiniPlayer (if isPlayerVisible && !isFullPlayerVisible)
│   ├── Progress (Linear, 顶部进度条)
│   └── Row (封面 + 标题 + 播放按钮)
└── Tab Bar (if !isFullPlayerVisible)
    └── Row (5 个 tabBarItem, layoutWeight 等分)
```

**关键布局技巧**：
- `Navigation` 设置 `layoutWeight(1)` 占满内容区
- MiniPlayer 和 Tab Bar 用 `if` 条件渲染（FullPlayer 时隐藏）
- Tab Bar 使用 `height(56)` 固定高度
- 整体 Column 用 `width('100%').height('100%')` 撑满屏幕
