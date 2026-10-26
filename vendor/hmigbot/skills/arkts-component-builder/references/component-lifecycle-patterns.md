# 组件生命周期模式（**V1 历史文档 — Legacy**）

> ⚠️ **本项目锁 ArkTS V2**。本文档示例采用 **V1 装饰器写法**（`@Component / @State / @StorageLink`），仅用于阅读老代码或迁移老项目时查阅。
>
> **新代码请使用 V2 装饰器**：参阅 [`v2-component-lifecycle-patterns.md`](./v2-component-lifecycle-patterns.md)（V2 主参考，使用 `@ComponentV2 / @Local / AppStorageV2.connect / @Monitor`）。

> 基于 AntennaPod ArkTS 播客应用实战总结的 3 种组件生命周期模式：EventBus 订阅管理、ViewModel 数据加载、ForEach key 生成器。
> 源码参考：`entry/src/main/ets/components/episodes/EpisodeDetailComponent.ets`、`entry/src/main/ets/viewmodels/HomeViewModel.ets`

---

## 1. EventBus 订阅生命周期管理

**核心原则**：`aboutToAppear` 订阅，`aboutToDisappear` 取消订阅。不取消会导致内存泄漏和幽灵更新。

**模式**：使用 `unsubscribers: (() => void)[]` 数组收集所有取消函数，在 `aboutToDisappear` 统一调用。

```typescript
// 文件: components/episodes/EpisodeDetailComponent.ets
@Component
export struct EpisodeDetailComponent {
  private vm: EpisodeDetailViewModel = new EpisodeDetailViewModel();
  @State episodeId: number = 0;
  @State title: string = '';
  @State isDownloaded: boolean = false;
  @State downloadProgress: number = -1;
  // ... 其他 @State
  private unsubscribers: (() => void)[] = [];

  private setupEventSubscriptions(): void {
    const bus = EventBus.getInstance();

    // 收藏状态变化 → 重新加载
    this.unsubscribers.push(bus.subscribe(EVENT_FAVORITES_CHANGED, () => {
      this.reloadEpisode();
    }));

    // 队列变化 → 重新加载
    this.unsubscribers.push(bus.subscribe(EVENT_QUEUE_CHANGED, () => {
      this.reloadEpisode();
    }));

    // 下载完成 → 检查是否是当前剧集
    this.unsubscribers.push(bus.subscribe(EVENT_EPISODE_DOWNLOADED, (data: Object) => {
      if (data instanceof DownloadLogData && data.episodeId === this.episodeId) {
        this.downloadProgress = -1;
        this.reloadEpisode();
      }
    }));

    // 播放状态变化
    this.unsubscribers.push(bus.subscribe(EVENT_EPISODE_PLAY_STATE_CHANGED, () => {
      this.reloadEpisode();
    }));

    // 下载进度 → 过滤当前剧集
    this.unsubscribers.push(bus.subscribe(EVENT_DOWNLOAD_PROGRESS, (data: Object) => {
      if (data instanceof DownloadProgressData) {
        const progressData: DownloadProgressData = data;
        if (progressData.episodeId === this.episodeId) {
          this.downloadProgress = progressData.percent;
        }
      }
    }));

    // 下载失败
    this.unsubscribers.push(bus.subscribe(EVENT_DOWNLOAD_FAILED, (data: Object) => {
      if (data instanceof DownloadFailedData) {
        const failedData: DownloadFailedData = data;
        if (failedData.episodeId === this.episodeId) {
          this.downloadProgress = -1;
          promptAction.showToast({ message: 'Download failed' });
        }
      }
    }));
  }

  aboutToDisappear(): void {
    // 统一取消所有订阅
    for (let i = 0; i < this.unsubscribers.length; i++) {
      this.unsubscribers[i]();
    }
  }
}
```

**EventBus.subscribe 返回取消函数的设计**：

```typescript
// EventBus 实现
subscribe(event: string, callback: (data: Object) => void): () => void {
  let list = this.listeners.get(event);
  if (list === undefined) {
    list = [];
    this.listeners.set(event, list);
  }
  list.push(callback);
  // 返回取消订阅的闭包
  return (): void => {
    this.unsubscribe(event, callback);
  };
}
```

**事件数据类型检查**（不用 `as`，用 `instanceof`）：

```typescript
// ArkTS 严格模式禁止 as 断言，必须用 instanceof
this.unsubscribers.push(bus.subscribe(EVENT_DOWNLOAD_PROGRESS, (data: Object) => {
  if (data instanceof DownloadProgressData) {
    // 此处 data 已经被类型缩窄为 DownloadProgressData
    const progressData: DownloadProgressData = data;
    if (progressData.episodeId === this.episodeId) {
      this.downloadProgress = progressData.percent;
    }
  }
}));
```

---

## 2. ViewModel 数据加载模式

**模式**：ViewModel 作为普通 class，组件通过 `@State` 绑定数据，在 `aboutToAppear` 或 `onReady` 中调用 `vm.loadData()`。EventBus 事件触发重新加载。

```typescript
// ViewModel 层 — 文件: viewmodels/HomeViewModel.ets
export class HomeViewModel {
  private feedDao: FeedDao = new FeedDao();
  private feedItemDao: FeedItemDao = new FeedItemDao();
  recentEpisodes: FeedItemDataSource = new FeedItemDataSource();
  continueListening: FeedItemDataSource = new FeedItemDataSource();
  newEpisodes: FeedItemDataSource = new FeedItemDataSource();
  surpriseEpisodes: FeedItemDataSource = new FeedItemDataSource();
  classicFeeds: FeedDataSource = new FeedDataSource();
  subscriptionCount: number = 0;

  async loadData(): Promise<void> {
    const items = await this.feedItemDao.getRecentlyPublished(0, 50);
    this.recentEpisodes.reloadAll(items);

    const feeds = await this.feedDao.getAllFeeds();
    this.subscriptionCount = feeds.length;
    this.classicFeeds.reloadAll(feeds);

    // 分类处理
    const continueItems: FeedItem[] = [];
    const newItems: FeedItem[] = [];
    for (let i = 0; i < items.length; i++) {
      const item = items[i];
      if (item.media !== null && item.media.position > 0 && !item.isPlayed()) {
        continueItems.push(item);
      }
      if (item.state === PLAY_STATE_NEW) {
        newItems.push(item);
      }
    }
    this.continueListening.reloadAll(continueItems);
    this.newEpisodes.reloadAll(newItems);

    const randomItems = await this.feedItemDao.getRandomEpisodes(5);
    this.surpriseEpisodes.reloadAll(randomItems);
  }
}
```

```typescript
// 组件层 — 使用 ViewModel
@Component
export struct HomeComponent {
  private vm: HomeViewModel = new HomeViewModel();
  @State isLoading: boolean = true;
  private unsubscribers: (() => void)[] = [];

  aboutToAppear(): void {
    this.loadData();
    this.setupEventSubscriptions();
  }

  private async loadData(): Promise<void> {
    this.isLoading = true;
    await this.vm.loadData();
    this.isLoading = false;
  }

  private setupEventSubscriptions(): void {
    const bus = EventBus.getInstance();
    this.unsubscribers.push(bus.subscribe(EVENT_FEED_UPDATED, () => {
      this.loadData();
    }));
    this.unsubscribers.push(bus.subscribe(EVENT_SUBSCRIPTION_ADDED, () => {
      this.loadData();
    }));
    this.unsubscribers.push(bus.subscribe(EVENT_QUEUE_CHANGED, () => {
      this.loadData();
    }));
  }

  aboutToDisappear(): void {
    for (let i = 0; i < this.unsubscribers.length; i++) {
      this.unsubscribers[i]();
    }
  }

  build() {
    Column() {
      if (this.isLoading) {
        LoadingProgress().width(48).height(48)
      } else {
        // 渲染内容...
      }
    }
  }
}
```

**ViewModel vs @State 职责分离**：

| 层 | 职责 | 示例 |
|------|------|------|
| ViewModel | 数据加载、业务逻辑、DAO 调用 | `loadData()`, `toggleFavorite()` |
| @State | UI 驱动状态 | `isLoading`, `title`, `isFavorite` |
| EventBus | 跨组件通知 | `EVENT_FEED_UPDATED` → 重新加载 |
| @StorageLink | 全局持久化状态 | `isPlaying`, `currentEpisodeTitle` |

---

## 3. ForEach key 生成器

**核心原则**：key 必须包含会变化的字段，否则 UI 不会刷新。

**错误做法**（key 只有 id）：

```typescript
// 错误：item 的播放状态变化后，UI 不会刷新
ForEach(this.items, (item: FeedItem) => {
  EpisodeListItem({ item: item })
}, (item: FeedItem) => item.id.toString())
```

**正确做法**（key 包含变化字段）：

```typescript
// 正确：播放状态、下载进度变化都会触发 UI 刷新
ForEach(this.items, (item: FeedItem) => {
  EpisodeListItem({ item: item })
}, (item: FeedItem) => {
  let key = item.id.toString();
  key += '_' + item.state.toString();  // 播放状态
  if (item.media !== null) {
    key += '_' + item.media.position.toString();  // 播放进度
    key += '_' + (item.media.isDownloaded() ? '1' : '0');  // 下载状态
  }
  return key;
})
```

**LazyForEach 的 key 规则一样**：

```typescript
// FeedItemDataSource 实现 IDataSource 接口
LazyForEach(this.vm.recentEpisodes, (item: FeedItem) => {
  EpisodeListItem({ item: item })
}, (item: FeedItem) => {
  return item.id.toString() + '_' + item.state.toString();
})
```

**key 变化字段选择指南**：

| 数据类型 | 推荐 key 组成 |
|---------|-------------|
| FeedItem | `id + state + media.position + media.isDownloaded` |
| Feed | `id + feedTitle + imageUrl + unreadCount` |
| Queue item | `id + queuePosition + state` |
| Download item | `id + downloadProgress + isDownloaded` |

**常见坑**：
- `ForEach` 和 `LazyForEach` 都需要 key 生成器
- 如果 key 不变，即使底层数据变了，UI 也不会重建子组件
- 不要在 key 中包含太多字段（会导致不必要的重建），只包含影响 UI 呈现的字段
