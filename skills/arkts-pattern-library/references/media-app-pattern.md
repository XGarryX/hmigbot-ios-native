# 媒体应用模式（**V1 历史文档 — Legacy**）

> ⚠️ **本项目锁 ArkTS V2**。本文档为 **V1 历史参考**（`@Component / @State / @StorageLink` 等），仅用于阅读老代码或迁移老项目时查阅。
>
> **新代码请使用 V2 装饰器**：参阅 [`v2-media-app-pattern.md`](./v2-media-app-pattern.md)（V2 主参考）和 [`../SKILL.md`](../SKILL.md)。

---

> 基于 AntennaPod ArkTS 播客应用实战总结的 3 种媒体应用 UI 模式：播放器双态、下载管理、Feed 导航链。
> 源码参考：`entry/src/main/ets/pages/Index.ets`、`entry/src/main/ets/network/DownloadManager.ets`、`entry/src/main/ets/playback/PlaybackController.ets`

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

### 状态驱动

```typescript
// 所有状态通过 AppStorage 传递，PlaybackController 写入，UI 组件读取
@StorageLink('isPlayerVisible') isPlayerVisible: boolean = false;     // 是否有播放内容
@StorageLink('isPlaying') isPlaying: boolean = false;                  // 是否正在播放
@StorageLink('isFullPlayerVisible') isFullPlayerVisible: boolean = false; // 全屏模式
@StorageLink('currentEpisodeTitle') currentEpisodeTitle: string = '';
@StorageLink('currentFeedTitle') currentFeedTitle: string = '';
@StorageLink('playbackPosition') playbackPosition: number = 0;
@StorageLink('playbackDuration') playbackDuration: number = 0;
@StorageLink('currentCoverUrl') currentCoverUrl: string = '';
```

### MiniPlayer 完整实现

```typescript
// 文件: pages/Index.ets (行 152-226)
if (this.isPlayerVisible && !this.isFullPlayerVisible) {
  Column() {
    // 顶部进度条
    Progress({ value: this.getProgressPercent(), total: 100, type: ProgressType.Linear })
      .height(2)
      .width('100%')
      .color('#007DFF')
      .backgroundColor('#E0E0E0')

    Row() {
      // 封面图 + fallback
      if (this.currentCoverUrl.length > 0) {
        Image(this.currentCoverUrl)
          .width(40).height(40).borderRadius(6).objectFit(ImageFit.Cover).margin({ right: 10 })
      } else {
        Column() {
          Text(this.currentFeedTitle.length > 0 ? this.currentFeedTitle.charAt(0).toUpperCase() : '?')
            .fontSize(18).fontWeight(FontWeight.Bold).fontColor(Color.White)
        }
        .width(40).height(40).borderRadius(6).backgroundColor('#BDBDBD')
        .justifyContent(FlexAlign.Center).alignItems(HorizontalAlign.Center).margin({ right: 10 })
      }

      // 标题 + 副标题
      Column() {
        Text(this.currentEpisodeTitle.length > 0 ? this.currentEpisodeTitle : 'No episode playing')
          .fontSize(14).maxLines(1).textOverflow({ overflow: TextOverflow.Ellipsis })
        if (this.currentFeedTitle.length > 0) {
          Text(this.currentFeedTitle)
            .fontSize(12).fontColor('#99000000').maxLines(1).textOverflow({ overflow: TextOverflow.Ellipsis })
        }
      }
      .layoutWeight(1).alignItems(HorizontalAlign.Start)

      // 播放/暂停按钮
      Column() {
        SymbolGlyph(this.isPlaying ? $r('sys.symbol.pause_fill') : $r('sys.symbol.play_fill'))
          .fontSize(20).fontColor(['#333333'])
      }
      .width(36).height(36).borderRadius(18).backgroundColor('#E8E8E8')
      .justifyContent(FlexAlign.Center).alignItems(HorizontalAlign.Center).margin({ left: 8 })
      .onClick(() => { PlaybackController.getInstance().playPause(); })
    }
    .padding({ left: 12, right: 16, top: 8, bottom: 8 }).width('100%')
  }
  .width('100%').backgroundColor('#FAFAFA')
  .shadow({ radius: 4, color: '#1A000000', offsetY: -2 })
  .onClick(() => {
    this.navPathStack.pushPathByName(RouteName.FULL_PLAYER, new Object());
  })
}
```

### FullPlayer 标志设置

```typescript
// FullPlayerComponent
NavDestination() { /* 全屏播放器 UI */ }
  .onReady(() => {
    this.isFullPlayerVisible = true;   // 进入 → 隐藏 MiniPlayer + Tab
  })
  .onDisAppear(() => {
    this.isFullPlayerVisible = false;  // 退出 → 恢复 MiniPlayer + Tab
  })
```

### FullPlayer 典型 UI 布局

```typescript
@Component
export struct FullPlayerComponent {
  @StorageLink('currentEpisodeTitle') title: string = '';
  @StorageLink('currentFeedTitle') feedTitle: string = '';
  @StorageLink('isPlaying') isPlaying: boolean = false;
  @StorageLink('playbackPosition') position: number = 0;
  @StorageLink('playbackDuration') duration: number = 0;
  @StorageLink('currentCoverUrl') coverUrl: string = '';
  @StorageLink('playbackSpeed') speed: number = 1.0;

  build() {
    NavDestination() {
      Column() {
        // 大封面图
        Image(this.coverUrl).width(280).height(280).borderRadius(12)

        // 标题 + 播客名
        Text(this.title).fontSize(20).fontWeight(FontWeight.Bold)
        Text(this.feedTitle).fontSize(14).fontColor('#99000000')

        // 进度滑块
        Slider({ value: this.position, max: this.duration })
          .onChange((value: number) => {
            PlaybackController.getInstance().seekTo(value);
          })

        // 控制按钮行
        Row() {
          SymbolGlyph($r('sys.symbol.gobackward_10'))
            .onClick(() => { PlaybackController.getInstance().rewind(); })
          SymbolGlyph(this.isPlaying ? $r('sys.symbol.pause_circle_fill') : $r('sys.symbol.play_circle_fill'))
            .onClick(() => { PlaybackController.getInstance().playPause(); })
          SymbolGlyph($r('sys.symbol.goforward_30'))
            .onClick(() => { PlaybackController.getInstance().fastForward(); })
        }
      }
    }
  }
}
```

---

## 2. 下载管理 UI — 三态按钮

### 三种状态

```
未下载 → [下载图标] 点击开始下载
下载中 → [进度环 + 百分比] 点击取消
已下载 → [已下载图标] 长按删除
```

### 状态驱动

```typescript
@State downloadProgress: number = -1;  // -1=非下载中, 0-100=进度
@State isDownloaded: boolean = false;

// EventBus 订阅
bus.subscribe(EVENT_DOWNLOAD_PROGRESS, (data: Object) => {
  if (data instanceof DownloadProgressData && data.episodeId === this.episodeId) {
    this.downloadProgress = data.percent;
  }
});

bus.subscribe(EVENT_EPISODE_DOWNLOADED, (data: Object) => {
  if (data instanceof DownloadLogData && data.episodeId === this.episodeId) {
    this.downloadProgress = -1;
    this.reloadEpisode();
  }
});

bus.subscribe(EVENT_DOWNLOAD_FAILED, (data: Object) => {
  if (data instanceof DownloadFailedData && data.episodeId === this.episodeId) {
    this.downloadProgress = -1;
    promptAction.showToast({ message: 'Download failed' });
  }
});
```

### UI 渲染

```typescript
if (this.downloadProgress >= 0) {
  // 下载中 — 进度环
  Stack() {
    Progress({ value: this.downloadProgress, total: 100, type: ProgressType.Ring })
      .width(32).height(32).color('#007DFF')
    Text(this.downloadProgress.toString() + '%').fontSize(10)
  }
  .onClick(() => {
    DownloadManager.getInstance().cancelDownload(this.episodeId);
    this.downloadProgress = -1;
  })
} else if (this.isDownloaded) {
  SymbolGlyph($r('sys.symbol.checkmark_circle_fill'))
    .fontSize(24).fontColor(['#4CAF50'])
} else {
  SymbolGlyph($r('sys.symbol.arrow_down_circle'))
    .fontSize(24).fontColor(['#666666'])
    .onClick(() => {
      DownloadManager.getInstance().downloadEpisode(this.episodeId, this.downloadUrl, this.mimeType);
    })
}
```

### DownloadManager 核心流程

```
downloadEpisode(itemId, url, mimeType)
  → ensureDirectory(downloadDir)
  → request.agent.create(config)  // 系统下载代理
  → task.on('progress', ...)      // 发布 EVENT_DOWNLOAD_PROGRESS
  → task.on('completed', ...)     // 移到 downloads 目录 → 更新 DB → 发布 EVENT_EPISODE_DOWNLOADED
  → task.on('failed', ...)        // 清理文件 → 发布 EVENT_DOWNLOAD_FAILED
  → task.start()
```

**下载完成后处理**：
1. 验证文件存在且非空
2. 从 cacheDir 移到 downloadDir
3. 更新 FeedMedia 数据库记录（localFileUrl, downloadDate, size）
4. 发布 `EVENT_EPISODE_DOWNLOADED` 通知 UI

---

## 3. Feed 列表 + 详情页 — 导航链

### 导航链

```
订阅网格 (SubscriptionComponent)
  → Feed 详情 (FeedDetailComponent)
    → 剧集详情 (EpisodeDetailComponent)
      → 播放 (PlaybackController)
```

### 订阅网格 → Feed 详情

```typescript
WaterFlow() {
  LazyForEach(this.vm.feeds, (feed: Feed) => {
    FlowItem() {
      FeedGridItem({ feed: feed })
    }
    .onClick(() => {
      const param = new FeedDetailParam();
      param.feedId = feed.id;
      this.navPathStack.pushPathByName(RouteName.FEED_DETAIL, param);
    })
  })
}
.columnsTemplate('1fr 1fr 1fr')
```

### Feed 详情 — Header + 剧集列表

```typescript
NavDestination() {
  Column() {
    // Feed 头部
    Row() {
      Image(this.imageUrl).width(100).height(100).borderRadius(12)
      Column() {
        Text(this.feedTitle).fontSize(20).fontWeight(FontWeight.Bold)
        Text(this.author).fontSize(14).fontColor('#99000000')
      }
    }
    // 剧集列表
    List() {
      LazyForEach(this.vm.episodes, (item: FeedItem) => {
        ListItem() { EpisodeListItem({ item: item }) }
          .onClick(() => {
            const param = new EpisodeDetailParam();
            param.episodeId = item.id;
            param.feedId = item.feedId;
            this.navPathStack.pushPathByName(RouteName.EPISODE_DETAIL, param);
          })
      })
    }
  }
}
.onReady((ctx: NavDestinationContext) => {
  const param = ctx.pathInfo.param;
  if (param instanceof FeedDetailParam) {
    this.feedId = param.feedId;
    this.loadData();
  }
})
```

### 剧集详情 — 操作按钮行

```typescript
Row() {
  // 播放按钮
  Button(this.currentEpisodeId === this.episodeId && this.isPlaying ? 'Pause' : 'Play')
    .onClick(() => {
      if (this.currentEpisodeId === this.episodeId) {
        PlaybackController.getInstance().playPause();
      } else {
        PlaybackController.getInstance().playEpisode(this.episodeId);
      }
    })

  // 下载按钮（三态，见上方）

  // 收藏按钮
  SymbolGlyph(this.isFavorite ? $r('sys.symbol.heart_fill') : $r('sys.symbol.heart'))
    .onClick(() => { this.vm.toggleFavorite(this.episodeId); })

  // 队列按钮
  SymbolGlyph(this.isInQueue ? $r('sys.symbol.text_badge_minus') : $r('sys.symbol.text_badge_plus'))
    .onClick(() => { this.vm.toggleQueue(this.episodeId); })
}
```

---

## 整体数据流总结

```
[用户操作]
    │
    ├─ 播放 → PlaybackController → AppStorage → @StorageLink UI
    │                            → EventBus → @State UI
    │
    ├─ 下载 → DownloadManager → EventBus → @State UI
    │                         → DB (FeedMedia)
    │
    ├─ 订阅 → FeedUpdateService → DB (Feed/FeedItem)
    │                           → EventBus → @State UI
    │
    └─ 设置 → UserPreferences → Preferences (磁盘)
                               → AppStorage → @StorageLink UI
```
