# 媒体应用模式（V2）

> 本项目锁 ArkTS V2，本文档为 V2 主参考。V1 历史写法（`@Component / @State / @StorageLink('isPlaying')` 散点式）见 [`media-app-pattern.md`](./media-app-pattern.md)。

> 基于 AntennaPod ArkTS 播客应用实战总结的 3 种媒体应用 UI 模式：播放器双态、下载管理、Feed 导航链。
> 源码参考：`entry/src/main/ets/pages/Index.ets`、`entry/src/main/ets/network/DownloadManager.ets`、`entry/src/main/ets/playback/PlaybackController.ets`

---

## V2 升级要点

V1 用 8 个 `@StorageLink('xxx')` 散点共享播放器状态：

```typescript
// V1 散点式
@StorageLink('isPlayerVisible') isPlayerVisible: boolean = false
@StorageLink('isPlaying') isPlaying: boolean = false
@StorageLink('isFullPlayerVisible') isFullPlayerVisible: boolean = false
@StorageLink('currentEpisodeTitle') currentEpisodeTitle: string = ''
// ... 还有 4 个
```

V2 改为：**定义 `PlaybackState` `@ObservedV2` 类**，所有播放相关字段加 `@Trace`，组件通过 `AppStorageV2.connect(PlaybackState, 'playback', () => new PlaybackState())!` 获得共享实例。优势：

- 类型集中，IDE 自动补全好
- 无需 8 次 connect，一次拿全部
- 修改任意 `@Trace` 字段自动同步所有引用方

---

## 1. 播放器 UI — MiniPlayer + FullPlayer 双态

### 架构

```
┌─────────────────────────────────┐
│  Navigation                     │
│  ┌───────────────────────────┐  │
│  │  Tab 内容 / NavDestination │  │
│  │  (含 FullPlayer)          │  │
│  └───────────────────────────┘  │
│                                 │
├─ MiniPlayer (Navigation 外部)  ─┤  ← if isPlayerVisible && !isFullPlayerVisible
│  [进度条][封面][标题][播放按钮]  │
├─────────────────────────────────┤
│  Tab 栏 (5 个 Tab)              │  ← if !isFullPlayerVisible
└─────────────────────────────────┘
```

### 双态切换机制

| 状态 | 触发方式 | 显示组件 | 隐藏组件 |
|------|---------|---------|---------|
| 非播放 | 初始状态 | Tab 内容 + Tab 栏 | MiniPlayer, FullPlayer |
| MiniPlayer | 开始播放后 | Tab 内容 + MiniPlayer + Tab 栏 | FullPlayer |
| FullPlayer | 点击 MiniPlayer | FullPlayer | MiniPlayer + Tab 栏 |
| 回到 MiniPlayer | NavPathStack.pop() | MiniPlayer + Tab 栏 | FullPlayer |

### V2 状态驱动 — 用 @ObservedV2 类集中管理

```typescript
// 全局播放状态类
@ObservedV2
class PlaybackState {
  @Trace isPlayerVisible: boolean = false        // 是否有播放内容
  @Trace isPlaying: boolean = false              // 是否正在播放
  @Trace isFullPlayerVisible: boolean = false    // 全屏模式
  @Trace currentEpisodeTitle: string = ''
  @Trace currentFeedTitle: string = ''
  @Trace currentCoverUrl: string = ''
  @Trace playbackPosition: number = 0
  @Trace playbackDuration: number = 0
  @Trace playbackSpeed: number = 1.0
  @Trace currentEpisodeId: string = ''
}

// Storage Key 常量
class PlaybackStorageKeys {
  static readonly PLAYBACK = 'playback'
}
```

### MiniPlayer 完整实现（V2）

```typescript
// 文件: pages/Index.ets
@ComponentV2
struct MiniPlayer {
  @Local playback: PlaybackState = AppStorageV2.connect(
    PlaybackState, PlaybackStorageKeys.PLAYBACK, () => new PlaybackState()
  )!
  @Param navPathStack: NavPathStack = new NavPathStack()

  @Computed
  get progressPercent(): number {
    if (this.playback.playbackDuration <= 0) return 0
    return (this.playback.playbackPosition / this.playback.playbackDuration) * 100
  }

  build() {
    if (this.playback.isPlayerVisible && !this.playback.isFullPlayerVisible) {
      Column() {
        // 顶部进度条
        Progress({ value: this.progressPercent, total: 100, type: ProgressType.Linear })
          .height(2)
          .width('100%')
          .color('#007DFF')
          .backgroundColor('#E0E0E0')

        Row() {
          // 封面图 + fallback
          if (this.playback.currentCoverUrl.length > 0) {
            Image(this.playback.currentCoverUrl)
              .width(40).height(40).borderRadius(6).objectFit(ImageFit.Cover).margin({ right: 10 })
          } else {
            Column() {
              Text(this.playback.currentFeedTitle.length > 0
                ? this.playback.currentFeedTitle.charAt(0).toUpperCase() : '?')
                .fontSize(18).fontWeight(FontWeight.Bold).fontColor(Color.White)
            }
            .width(40).height(40).borderRadius(6).backgroundColor('#BDBDBD')
            .justifyContent(FlexAlign.Center).alignItems(HorizontalAlign.Center).margin({ right: 10 })
          }

          // 标题 + 副标题
          Column() {
            Text(this.playback.currentEpisodeTitle.length > 0
              ? this.playback.currentEpisodeTitle : 'No episode playing')
              .fontSize(14).maxLines(1).textOverflow({ overflow: TextOverflow.Ellipsis })
            if (this.playback.currentFeedTitle.length > 0) {
              Text(this.playback.currentFeedTitle)
                .fontSize(12).fontColor('#99000000').maxLines(1).textOverflow({ overflow: TextOverflow.Ellipsis })
            }
          }
          .layoutWeight(1).alignItems(HorizontalAlign.Start)

          // 播放/暂停按钮
          Column() {
            SymbolGlyph(this.playback.isPlaying ? $r('sys.symbol.pause_fill') : $r('sys.symbol.play_fill'))
              .fontSize(20).fontColor(['#333333'])
          }
          .width(36).height(36).borderRadius(18).backgroundColor('#E8E8E8')
          .justifyContent(FlexAlign.Center).alignItems(HorizontalAlign.Center).margin({ left: 8 })
          .onClick(() => { PlaybackController.getInstance().playPause() })
        }
        .padding({ left: 12, right: 16, top: 8, bottom: 8 }).width('100%')
      }
      .width('100%').backgroundColor('#FAFAFA')
      .shadow({ radius: 4, color: '#1A000000', offsetY: -2 })
      .onClick(() => {
        this.navPathStack.pushPathByName('FullPlayer', new Object())
      })
    }
  }
}
```

### FullPlayer 标志设置（V2）

```typescript
@ComponentV2
struct FullPlayerComponent {
  @Local playback: PlaybackState = AppStorageV2.connect(
    PlaybackState, PlaybackStorageKeys.PLAYBACK, () => new PlaybackState()
  )!

  build() {
    NavDestination() { /* 全屏播放器 UI */ }
      .onReady(() => {
        this.playback.isFullPlayerVisible = true   // 进入 → 隐藏 MiniPlayer + Tab
      })
      .onDisAppear(() => {
        this.playback.isFullPlayerVisible = false  // 退出 → 恢复 MiniPlayer + Tab
      })
  }
}
```

### FullPlayer 典型 UI 布局（V2）

```typescript
@ComponentV2
export struct FullPlayerUI {
  @Local playback: PlaybackState = AppStorageV2.connect(
    PlaybackState, PlaybackStorageKeys.PLAYBACK, () => new PlaybackState()
  )!

  build() {
    NavDestination() {
      Column() {
        // 大封面图
        Image(this.playback.currentCoverUrl).width(280).height(280).borderRadius(12)

        // 标题 + 播客名
        Text(this.playback.currentEpisodeTitle).fontSize(20).fontWeight(FontWeight.Bold)
        Text(this.playback.currentFeedTitle).fontSize(14).fontColor('#99000000')

        // 进度滑块
        Slider({ value: this.playback.playbackPosition, max: this.playback.playbackDuration })
          .onChange((value: number) => {
            PlaybackController.getInstance().seekTo(value)
          })

        // 控制按钮行
        Row() {
          SymbolGlyph($r('sys.symbol.gobackward_10'))
            .onClick(() => { PlaybackController.getInstance().rewind() })
          SymbolGlyph(this.playback.isPlaying
            ? $r('sys.symbol.pause_circle_fill') : $r('sys.symbol.play_circle_fill'))
            .onClick(() => { PlaybackController.getInstance().playPause() })
          SymbolGlyph($r('sys.symbol.goforward_30'))
            .onClick(() => { PlaybackController.getInstance().fastForward() })
        }
      }
    }
  }
}
```

### PlaybackController 写入 V2 状态

```typescript
class PlaybackController {
  private static instance: PlaybackController

  static getInstance(): PlaybackController {
    if (!PlaybackController.instance) {
      PlaybackController.instance = new PlaybackController()
    }
    return PlaybackController.instance
  }

  // 播放控制器持有共享 PlaybackState 实例
  private state: PlaybackState = AppStorageV2.connect(
    PlaybackState, PlaybackStorageKeys.PLAYBACK, () => new PlaybackState()
  )!

  playEpisode(episodeId: string): void {
    this.state.currentEpisodeId = episodeId
    this.state.isPlayerVisible = true
    this.state.isPlaying = true
    // ... AVPlayer 启动 ...
  }

  playPause(): void {
    this.state.isPlaying = !this.state.isPlaying
  }

  seekTo(position: number): void {
    this.state.playbackPosition = position
  }

  rewind(): void {
    this.state.playbackPosition = Math.max(0, this.state.playbackPosition - 10000)
  }

  fastForward(): void {
    this.state.playbackPosition = Math.min(this.state.playbackDuration, this.state.playbackPosition + 30000)
  }
}
```

---

## 2. 下载管理 UI — 三态按钮（V2）

### 三种状态

```
未下载 → [下载图标] 点击开始下载
下载中 → [进度环 + 百分比] 点击取消
已下载 → [已下载图标] 长按删除
```

### V2 状态驱动

下载是局部组件状态（每个剧集独立），用 `@Local` + EventBus 订阅；不需要全局 AppStorageV2：

```typescript
@ComponentV2
struct DownloadButton {
  @Param @Once episodeId: string = ''
  @Param @Once downloadUrl: string = ''
  @Param @Once mimeType: string = ''
  @Local downloadProgress: number = -1   // -1=非下载中, 0-100=进度
  @Local isDownloaded: boolean = false

  aboutToAppear(): void {
    const bus = EventBus.getInstance()

    bus.subscribe(EVENT_DOWNLOAD_PROGRESS, (data: Object) => {
      if (data instanceof DownloadProgressData && data.episodeId === this.episodeId) {
        this.downloadProgress = data.percent
      }
    })

    bus.subscribe(EVENT_EPISODE_DOWNLOADED, (data: Object) => {
      if (data instanceof DownloadLogData && data.episodeId === this.episodeId) {
        this.downloadProgress = -1
        this.reloadEpisode()
      }
    })

    bus.subscribe(EVENT_DOWNLOAD_FAILED, (data: Object) => {
      if (data instanceof DownloadFailedData && data.episodeId === this.episodeId) {
        this.downloadProgress = -1
        // 现行实例形 Toast：全局 promptAction.showToast 自 API18 已 deprecated，用 UIContext 实例形
        this.getUIContext().getPromptAction().showToast({ message: 'Download failed' })
      }
    })
  }

  reloadEpisode(): void {
    // 重新查询 DB，更新 isDownloaded
  }

  build() {
    if (this.downloadProgress >= 0) {
      // 下载中 — 进度环
      Stack() {
        Progress({ value: this.downloadProgress, total: 100, type: ProgressType.Ring })
          .width(32).height(32).color('#007DFF')
        Text(this.downloadProgress.toString() + '%').fontSize(10)
      }
      .onClick(() => {
        DownloadManager.getInstance().cancelDownload(this.episodeId)
        this.downloadProgress = -1
      })
    } else if (this.isDownloaded) {
      SymbolGlyph($r('sys.symbol.checkmark_circle_fill'))
        .fontSize(24).fontColor(['#4CAF50'])
    } else {
      SymbolGlyph($r('sys.symbol.arrow_down_circle'))
        .fontSize(24).fontColor(['#666666'])
        .onClick(() => {
          DownloadManager.getInstance().downloadEpisode(this.episodeId, this.downloadUrl, this.mimeType)
        })
    }
  }
}
```

### DownloadManager 核心流程（不变，业务无关）

```
downloadEpisode(itemId, url, mimeType)
  → ensureDirectory(downloadDir)
  → request.agent.create(config)
  → task.on('progress', ...)      // 发布 EVENT_DOWNLOAD_PROGRESS
  → task.on('completed', ...)     // 移到 downloads 目录 → 更新 DB → 发布 EVENT_EPISODE_DOWNLOADED
  → task.on('failed', ...)        // 清理文件 → 发布 EVENT_DOWNLOAD_FAILED
  → task.start()
```

---

## 3. Feed 列表 + 详情页 — 导航链（V2）

### 导航链

```
订阅网格 (SubscriptionComponent)
  → Feed 详情 (FeedDetailComponent)
    → 剧集详情 (EpisodeDetailComponent)
      → 播放 (PlaybackController)
```

### 订阅网格 → Feed 详情（V2）

```typescript
@ObservedV2
class Feed {
  id: string = ''
  @Trace title: string = ''
  @Trace imageUrl: string = ''
  @Trace author: string = ''
}

class FeedDetailParam {
  feedId: string = ''
}

@ComponentV2
struct SubscriptionComponent {
  @Local feeds: Feed[] = []
  @Consumer() navPathStack: NavPathStack = new NavPathStack()

  build() {
    WaterFlow() {
      LazyForEach(this.feeds, (feed: Feed) => {
        FlowItem() {
          FeedGridItem({ feed: feed })
        }
        .onClick(() => {
          const param = new FeedDetailParam()
          param.feedId = feed.id
          this.navPathStack.pushPathByName('FeedDetail', param)
        })
      })
    }
    .columnsTemplate('1fr 1fr 1fr')
  }
}

@ComponentV2
struct FeedGridItem {
  @Param @Once feed: Feed = new Feed()
  build() {
    Column() {
      Image(this.feed.imageUrl).width(100).height(100).borderRadius(8)
      Text(this.feed.title).fontSize(12).maxLines(2)
    }
  }
}
```

### Feed 详情 — Header + 剧集列表（V2）

```typescript
@ObservedV2
class FeedItem {
  id: string = ''
  feedId: string = ''
  @Trace title: string = ''
}

class EpisodeDetailParam {
  episodeId: string = ''
  feedId: string = ''
}

@ObservedV2
class FeedDetailVM {
  @Trace feedTitle: string = ''
  @Trace imageUrl: string = ''
  @Trace author: string = ''
  @Trace episodes: FeedItem[] = []
}

@ComponentV2
struct FeedDetailComponent {
  @Local feedId: string = ''
  @Local vm: FeedDetailVM = new FeedDetailVM()
  @Consumer() navPathStack: NavPathStack = new NavPathStack()

  loadData(): void {
    // 加载 feed 详情和剧集列表
  }

  build() {
    NavDestination() {
      Column() {
        // Feed 头部
        Row() {
          Image(this.vm.imageUrl).width(100).height(100).borderRadius(12)
          Column() {
            Text(this.vm.feedTitle).fontSize(20).fontWeight(FontWeight.Bold)
            Text(this.vm.author).fontSize(14).fontColor('#99000000')
          }
        }
        // 剧集列表
        List() {
          LazyForEach(this.vm.episodes, (item: FeedItem) => {
            ListItem() { EpisodeListItem({ item: item }) }
              .onClick(() => {
                const param = new EpisodeDetailParam()
                param.episodeId = item.id
                param.feedId = item.feedId
                this.navPathStack.pushPathByName('EpisodeDetail', param)
              })
          })
        }
      }
    }
    .onReady((ctx: NavDestinationContext) => {
      const param = ctx.pathInfo.param
      if (param instanceof FeedDetailParam) {
        this.feedId = param.feedId
        this.loadData()
      }
    })
  }
}

@ComponentV2
struct EpisodeListItem {
  @Param @Once item: FeedItem = new FeedItem()
  build() {
    Row() { Text(this.item.title).fontSize(16) }
  }
}
```

### 剧集详情 — 操作按钮行（V2）

```typescript
@ComponentV2
struct EpisodeDetailComponent {
  @Param @Once episodeId: string = ''
  @Local isFavorite: boolean = false
  @Local isInQueue: boolean = false
  @Local playback: PlaybackState = AppStorageV2.connect(
    PlaybackState, PlaybackStorageKeys.PLAYBACK, () => new PlaybackState()
  )!
  private vm = new EpisodeDetailVM()

  build() {
    Row() {
      // 播放按钮：使用 @Computed 派生显示文本
      Button(this.playButtonText)
        .onClick(() => {
          if (this.playback.currentEpisodeId === this.episodeId) {
            PlaybackController.getInstance().playPause()
          } else {
            PlaybackController.getInstance().playEpisode(this.episodeId)
          }
        })

      // 下载按钮（三态，见上方 DownloadButton）

      // 收藏按钮
      SymbolGlyph(this.isFavorite ? $r('sys.symbol.heart_fill') : $r('sys.symbol.heart'))
        .onClick(() => { this.vm.toggleFavorite(this.episodeId) })

      // 队列按钮
      SymbolGlyph(this.isInQueue ? $r('sys.symbol.text_badge_minus') : $r('sys.symbol.text_badge_plus'))
        .onClick(() => { this.vm.toggleQueue(this.episodeId) })
    }
  }

  @Computed
  get playButtonText(): string {
    return this.playback.currentEpisodeId === this.episodeId && this.playback.isPlaying ? 'Pause' : 'Play'
  }
}

class EpisodeDetailVM {
  toggleFavorite(id: string): void { /* ... */ }
  toggleQueue(id: string): void { /* ... */ }
}
```

---

## 整体数据流总结（V2）

```
[用户操作]
    │
    ├─ 播放 → PlaybackController → PlaybackState (@ObservedV2 类，AppStorageV2 共享) → 所有 connect 的组件自动刷新
    │                            → EventBus → @Local UI（仅本地反应）
    │
    ├─ 下载 → DownloadManager → EventBus → @Local UI
    │                         → DB (FeedMedia)
    │
    ├─ 订阅 → FeedUpdateService → DB (Feed/FeedItem)
    │                           → EventBus → @Local UI
    │
    └─ 设置 → UserSettings (@ObservedV2) → PersistenceV2.globalConnect → 自动落盘 + 所有 connect 组件刷新
```

## V2 关键变更对照（vs V1）

| 位置 | V1 | V2 |
|---|---|---|
| 组件 struct | `@Component struct MiniPlayer` | `@ComponentV2 struct MiniPlayer` |
| 8 个共享状态 | 8 个 `@StorageLink('xxx')` 散点 | 1 个 `PlaybackState` 类 + 1 次 `AppStorageV2.connect` |
| 局部状态 | `@State downloadProgress: number` | `@Local downloadProgress: number` |
| 子组件 props | `@Prop episodeId: string` | `@Param @Once episodeId: string` |
| 进度百分比计算 | 每次 build 重算 | `@Computed get progressPercent()` 缓存 |
| 跨层级（NavPathStack） | `@Provide('navPathStack') / @Consume('navPathStack')` | `@Provider() / @Consumer()` |
