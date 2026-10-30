# 媒体应用组件模式（V2）

> 基于 ArkTS V2（`@ComponentV2 / @ObservedV2 + @Trace + AppStorageV2 / @Param + @Event`）的 4 种媒体应用组件模式：MiniPlayer、自定义 Tab 栏、封面图 + fallback、空状态组件。**本项目锁 V2**，本文档为主参考。V1 历史模式查阅请见 [`media-app-components.md`](./media-app-components.md)。

> 源码风格参考：`entry/src/main/ets/pages/Index.ets`、`entry/src/main/ets/components/common/EmptyStateView.ets`

---

## 1. MiniPlayer 模式 — 底部浮动播放条（V2 + AppStorageV2）

V2 用 `@ObservedV2` 类封装播放状态，组件用 `@Local` 持有 `AppStorageV2.connect()` 的实例。
MiniPlayer 放置在 `Navigation` 外部、Tab 栏上方，FullPlayer 打开时 MiniPlayer 自动隐藏。

### 1.1 定义播放状态类（@ObservedV2）

```typescript
// 文件: viewmodels/PlaybackModel.ets
@ObservedV2
export class PlaybackModel {
  @Trace isPlayerVisible: boolean = false
  @Trace isPlaying: boolean = false
  @Trace currentEpisodeTitle: string = ''
  @Trace currentFeedTitle: string = ''
  @Trace playbackPosition: number = 0
  @Trace playbackDuration: number = 0
  @Trace currentCoverUrl: string = ''
  @Trace isFullPlayerVisible: boolean = false
}
```

### 1.2 MiniPlayer 组件

```typescript
// 文件: pages/Index.ets（V2）
import { PlaybackModel } from '../viewmodels/PlaybackModel'

@Entry
@ComponentV2
struct IndexPage {
  // V2 全局共享状态：AppStorageV2.connect 替代 V1 @StorageLink
  @Local playback: PlaybackModel = AppStorageV2.connect(
    PlaybackModel,
    'playback',
    () => new PlaybackModel()
  )!

  @Local currentTabIndex: number = 0
  @Local navPathStack: NavPathStack = new NavPathStack()
  @Local dbReady: boolean = false

  build() {
    Column() {
      Navigation(this.navPathStack) {
        if (this.dbReady) {
          this.tabContent()
        }
      }
      .layoutWeight(1)

      // MiniPlayer — always above tab bar, hidden when FullPlayer is open
      if (this.playback.isPlayerVisible && !this.playback.isFullPlayerVisible) {
        this.miniPlayer()
      }

      // Tab Bar
      if (!this.playback.isFullPlayerVisible) {
        this.tabBar()
      }
    }
    .width('100%')
    .height('100%')
  }

  @Builder
  miniPlayer() {
    Column() {
      Progress({ value: this.getProgressPercent(), total: 100, type: ProgressType.Linear })
        .height(2)
        .width('100%')
        .color('#007DFF')
        .backgroundColor('#E0E0E0')

      Row() {
        if (this.playback.currentCoverUrl.length > 0) {
          Image(this.playback.currentCoverUrl)
            .width(40).height(40).borderRadius(6)
            .objectFit(ImageFit.Cover)
            .margin({ right: 10 })
        } else {
          // Fallback：首字母色块
          Column() {
            Text(this.playback.currentFeedTitle.length > 0
              ? this.playback.currentFeedTitle.charAt(0).toUpperCase()
              : '?')
              .fontSize(18)
              .fontWeight(FontWeight.Bold)
              .fontColor(Color.White)
          }
          .width(40).height(40).borderRadius(6)
          .backgroundColor('#BDBDBD')
          .justifyContent(FlexAlign.Center)
          .alignItems(HorizontalAlign.Center)
          .margin({ right: 10 })
        }

        Column() {
          Text(this.playback.currentEpisodeTitle.length > 0
            ? this.playback.currentEpisodeTitle
            : 'No episode playing')
            .fontSize(14)
            .maxLines(1)
            .textOverflow({ overflow: TextOverflow.Ellipsis })
          if (this.playback.currentFeedTitle.length > 0) {
            Text(this.playback.currentFeedTitle)
              .fontSize(12)
              .fontColor('#99000000')
              .maxLines(1)
              .textOverflow({ overflow: TextOverflow.Ellipsis })
          }
        }
        .layoutWeight(1)
        .alignItems(HorizontalAlign.Start)

        Column() {
          SymbolGlyph(this.playback.isPlaying
            ? $r('sys.symbol.pause_fill')
            : $r('sys.symbol.play_fill'))
            .fontSize(20)
            .fontColor(['#333333'])
        }
        .width(36).height(36).borderRadius(18)
        .backgroundColor('#E8E8E8')
        .justifyContent(FlexAlign.Center)
        .alignItems(HorizontalAlign.Center)
        .margin({ left: 8 })
        .onClick(() => {
          PlaybackController.getInstance().playPause()
        })
      }
      .padding({ left: 12, right: 16, top: 8, bottom: 8 })
      .width('100%')
    }
    .width('100%')
    .backgroundColor('#FAFAFA')
    .shadow({ radius: 4, color: '#1A000000', offsetY: -2 })
    .onClick(() => {
      this.navPathStack.pushPathByName(RouteName.FULL_PLAYER, new Object())
    })
  }

  private getProgressPercent(): number {
    if (this.playback.playbackDuration > 0 && this.playback.playbackPosition > 0) {
      return Math.round(this.playback.playbackPosition * 100 / this.playback.playbackDuration)
    }
    return 0
  }

  @Builder
  tabContent() { /* ... 略 ... */ }

  @Builder
  tabBar() { /* ... 略 ... */ }
}
```

### 1.3 V1 → V2 状态对比

| V1 写法 | V2 写法 |
|---------|---------|
| `@StorageLink('isPlaying') isPlaying: boolean = false` | `this.playback.isPlaying`（来自 `PlaybackModel` 实例） |
| 8 个独立 `@StorageLink` | 1 个 `@ObservedV2 PlaybackModel` 类，含 8 个 `@Trace` 字段 |
| 每个字段单独同步 | 整个对象通过 `AppStorageV2.connect` 全局共享 |
| `AppStorage.set('isPlaying', true)` | `this.playback.isPlaying = true`（直接修改 `@Trace` 属性） |

**优势**：
- 状态聚合到一个类，避免散落多处
- `@Trace` 属性级精确观察，避免不必要的全局刷新
- key 拼写错误风险降低（只一处 `'playback'`）

---

## 2. 自定义 Tab 栏 — @Builder tabBarItem（V2）

使用 `@Builder` 构建自定义 Tab 项，支持 Material 3 风格药丸指示器。
不使用系统 `Tabs` 组件，而是 `Row` + `if/else` 手动切换 Tab 内容。

```typescript
// V2 风格自定义 Tab 栏
@Entry
@ComponentV2
struct IndexPage {
  @Local currentTabIndex: number = 0

  @Builder
  tabBarItem(tabIdx: number, tabTitle: Resource, tabIcon: Resource) {
    Column() {
      // Pill-shaped gray background for selected tab icon (Material 3 style)
      Column() {
        SymbolGlyph(tabIcon)
          .fontSize(22)
          .fontColor(this.currentTabIndex === tabIdx
            ? [Color.Black]
            : ['#99182431'])
      }
      .width(48).height(28).borderRadius(14)
      .backgroundColor(this.currentTabIndex === tabIdx
        ? '#1F000000'
        : '#00000000')
      .justifyContent(FlexAlign.Center)
      .alignItems(HorizontalAlign.Center)

      Text(tabTitle)
        .fontSize(10)
        .fontColor(this.currentTabIndex === tabIdx
          ? '#182431'
          : '#99182431')
        .margin({ top: 2 })
    }
    .layoutWeight(1)
    .justifyContent(FlexAlign.Center)
    .height('100%')
    .onClick(() => {
      this.currentTabIndex = tabIdx
    })
  }

  build() {
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
  }
}
```

**药丸指示器关键属性**：

| 属性 | 值 | 说明 |
|------|------|------|
| `width` | 48 | 固定药丸宽度 |
| `height` | 28 | 固定药丸高度 |
| `borderRadius` | 14 | 高度的一半，形成圆角药丸 |
| `backgroundColor` | `'#1F000000'` / `'#00000000'` | 选中半透明黑 / 未选中全透明 |

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

## 3. 封面图 + fallback 模式（V2 @Builder 提取通用）

当图片 URL 存在时显示 `Image`，不存在时显示 `Text` 首字母 + 灰色背景。
此模式在 MiniPlayer、剧集列表项、Feed 网格项中反复使用。

```typescript
// V2 通用化提取（组件外部 @Builder）
@Builder
function CoverImage(coverUrl: string, fallbackText: string, coverSize: number) {
  if (coverUrl.length > 0) {
    Image(coverUrl)
      .width(coverSize)
      .height(coverSize)
      .borderRadius(coverSize * 0.15)
      .objectFit(ImageFit.Cover)
  } else {
    Column() {
      Text(fallbackText.length > 0
        ? fallbackText.charAt(0).toUpperCase()
        : '?')
        .fontSize(coverSize * 0.45)
        .fontWeight(FontWeight.Bold)
        .fontColor(Color.White)
    }
    .width(coverSize)
    .height(coverSize)
    .borderRadius(coverSize * 0.15)
    .backgroundColor('#BDBDBD')
    .justifyContent(FlexAlign.Center)
    .alignItems(HorizontalAlign.Center)
  }
}

// 使用：在 V2 组件内部直接调用全局 @Builder
@ComponentV2
struct EpisodeListItem {
  @Param @Once coverUrl: string = ''
  @Param @Once feedTitle: string = ''

  build() {
    Row() {
      CoverImage(this.coverUrl, this.feedTitle, 40)
      Text(this.feedTitle).margin({ left: 12 })
    }
  }
}
```

> **V2 迁移要点**：原 V1 的全局 `@Builder` 函数在 V2 完全兼容（`@Builder` 不属于状态装饰器）。

---

## 4. 空状态组件（V2）

通用占位组件，用于列表/页面无数据时的提示。支持图标、提示文字、可选操作按钮。

```typescript
// 文件: components/common/EmptyStateView.ets（V2）
@ComponentV2
export struct EmptyStateView {
  @Param @Once iconText: string = ''         // 不用 icon（emoji 字符串）
  @Param @Once messageText: string = ''      // 不用 message
  @Param @Once actionLabelText: string = ''  // 不用 actionLabel
  @Event onActionClick: () => void = () => {}

  build() {
    Column() {
      if (this.iconText.length > 0) {
        Text(this.iconText)
          .fontSize(48)
          .margin({ bottom: 16 })
      }

      Text(this.messageText)
        .fontSize(16)
        .fontColor('#99000000')
        .textAlign(TextAlign.Center)
        .padding({ left: 32, right: 32 })

      if (this.actionLabelText.length > 0) {
        Button(this.actionLabelText)
          .fontSize(14)
          .margin({ top: 16 })
          .onClick(() => {
            this.onActionClick()
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
@ComponentV2
struct QueuePage {
  @Local navPathStack: NavPathStack = new NavPathStack()

  build() {
    Column() {
      // 队列为空
      EmptyStateView({
        iconText: '📋',
        messageText: 'Your queue is empty.\nAdd episodes to start listening.',
        actionLabelText: 'Browse Podcasts',
        onActionClick: () => {
          this.navPathStack.pushPathByName(RouteName.ADD_FEED, new Object())
        }
      })
    }
  }
}
```

**设计要点（V2）**：
- 使用 `@Param @Once` 接收父组件传入的配置（V2 单向只读）
- `@Event` 替代 V1 直接传函数的写法（V2 事件命名约定）
- `layoutWeight(1)` 让空状态组件填满剩余空间
- `justifyContent(FlexAlign.Center)` 垂直居中

---

## 整体页面结构（V2）

Index.ets 的整体布局层次：

```
Column (root)
├── Navigation (layoutWeight=1, 占满剩余空间)
│   ├── Tab 内容 (if/else 切换)
│   └── navDestination → routerMap
├── MiniPlayer (if playback.isPlayerVisible && !playback.isFullPlayerVisible)
│   ├── Progress (Linear, 顶部进度条)
│   └── Row (封面 + 标题 + 播放按钮)
└── Tab Bar (if !playback.isFullPlayerVisible)
    └── Row (5 个 tabBarItem, layoutWeight 等分)
```

**关键布局技巧**：
- `Navigation` 设置 `layoutWeight(1)` 占满内容区
- MiniPlayer 和 Tab Bar 用 `if` 条件渲染（FullPlayer 时隐藏）
- Tab Bar 使用 `height(56)` 固定高度
- 整体 Column 用 `width('100%').height('100%')` 撑满屏幕
- **V2 优势**：`@Local playback: PlaybackModel = AppStorageV2.connect(...)` 一行替代 V1 8 个 `@StorageLink`

---

## V1 → V2 媒体状态迁移完整步骤

1. **抽出 V1 `@StorageLink` 字段为 `@ObservedV2` 类**：
   - 例如 V1 8 个 `@StorageLink('isPlaying' / 'currentEpisodeTitle' / ...)` → 1 个 `PlaybackModel` 类，每个字段加 `@Trace`
2. **首次入口 `EntryAbility.onCreate` 预热**（可选）：
   ```typescript
   onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void {
     AppStorageV2.connect(PlaybackModel, 'playback', () => new PlaybackModel())
   }
   ```
3. **每个使用方组件**：
   ```typescript
   @Local playback: PlaybackModel = AppStorageV2.connect(PlaybackModel, 'playback', () => new PlaybackModel())!
   ```
4. **读写**：原 `this.isPlaying` → `this.playback.isPlaying`；写法相同（`= true` / `= false`）。
5. **PlaybackController** 不变（业务类）。

---

## 跨文档参考

- [`v2-common-components.md`](./v2-common-components.md) — V2 常用组件用法
- [`v2-layout-patterns.md`](./v2-layout-patterns.md) — V2 布局模板
- [`v2-component-lifecycle-patterns.md`](./v2-component-lifecycle-patterns.md) — V2 生命周期与 EventBus
- [`v2-prop-naming-rules.md`](./v2-prop-naming-rules.md) — V2 变量命名规则
- `arkts-state-manager/references/v2-global-state.md` — V2 全局状态完整模板
- `arkts-state-manager/references/v2-real-world.md` — V2 PlaybackController 绑定 / EventBus 联动
