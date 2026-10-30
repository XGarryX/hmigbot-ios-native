# 组件生命周期模式（V2）

> 基于 ArkTS V2（`@ComponentV2 / @Local / @Monitor / AppStorageV2`）的 4 种组件生命周期模式：EventBus 订阅管理、ViewModel 数据加载、ForEach key 生成器、`@Monitor` 响应状态变化。**本项目锁 V2**，本文档为主参考。V1 历史模式查阅请见 [`component-lifecycle-patterns.md`](./component-lifecycle-patterns.md)。

> 源码风格参考：`entry/src/main/ets/components/episodes/EpisodeDetailComponent.ets`、`entry/src/main/ets/viewmodels/HomeViewModel.ets`

---

## 1. EventBus 订阅生命周期管理（V2）

**核心原则**：`aboutToAppear` 订阅，`aboutToDisappear` 取消订阅。不取消会导致内存泄漏和幽灵更新。

**模式**：使用 `unsubscribers: (() => void)[]` 数组收集所有取消函数，在 `aboutToDisappear` 统一调用。

```typescript
// 文件: components/episodes/EpisodeDetailComponent.ets（V2）
@ComponentV2
export struct EpisodeDetailComponent {
  @Param @Once episodeId: number = 0

  // V2 用 @Local 管理组件内部状态
  @Local private episodeTitle: string = ''
  @Local private isDownloaded: boolean = false
  @Local private downloadProgress: number = -1
  @Local private isPlayed: boolean = false

  private vm: EpisodeDetailViewModel = new EpisodeDetailViewModel()
  private unsubscribers: (() => void)[] = []

  aboutToAppear(): void {
    this.reloadEpisode()
    this.setupEventSubscriptions()
  }

  aboutToDisappear(): void {
    // 统一取消所有订阅
    for (let i = 0; i < this.unsubscribers.length; i++) {
      this.unsubscribers[i]()
    }
  }

  private async reloadEpisode(): Promise<void> {
    const ep = await this.vm.loadEpisode(this.episodeId)
    if (ep !== null) {
      this.episodeTitle = ep.title
      this.isDownloaded = ep.isDownloaded
      this.isPlayed = ep.isPlayed
    }
  }

  private setupEventSubscriptions(): void {
    const bus = EventBus.getInstance()

    // 收藏状态变化 → 重新加载
    this.unsubscribers.push(bus.subscribe(EVENT_FAVORITES_CHANGED, () => {
      this.reloadEpisode()
    }))

    // 队列变化 → 重新加载
    this.unsubscribers.push(bus.subscribe(EVENT_QUEUE_CHANGED, () => {
      this.reloadEpisode()
    }))

    // 下载完成 → 检查是否是当前剧集
    this.unsubscribers.push(bus.subscribe(EVENT_EPISODE_DOWNLOADED, (data: Object) => {
      if (data instanceof DownloadLogData && data.episodeId === this.episodeId) {
        this.downloadProgress = -1
        this.reloadEpisode()
      }
    }))

    // 下载进度 → 过滤当前剧集
    this.unsubscribers.push(bus.subscribe(EVENT_DOWNLOAD_PROGRESS, (data: Object) => {
      if (data instanceof DownloadProgressData) {
        const progressData: DownloadProgressData = data
        if (progressData.episodeId === this.episodeId) {
          this.downloadProgress = progressData.percent
        }
      }
    }))
  }

  build() {
    Column() {
      Text(this.episodeTitle)
      if (this.downloadProgress >= 0) {
        Progress({ value: this.downloadProgress, total: 100, type: ProgressType.Linear })
      }
    }
  }
}
```

**EventBus.subscribe 返回取消函数的设计**（V1/V2 通用，EventBus 本身与装饰器无关）：

```typescript
// EventBus 实现
subscribe(event: string, callback: (data: Object) => void): () => void {
  let list = this.listeners.get(event)
  if (list === undefined) {
    list = []
    this.listeners.set(event, list)
  }
  list.push(callback)
  return (): void => {
    this.unsubscribe(event, callback)
  }
}
```

**事件数据类型检查**（不用 `as`，用 `instanceof`，V1/V2 通用）：

```typescript
this.unsubscribers.push(bus.subscribe(EVENT_DOWNLOAD_PROGRESS, (data: Object) => {
  if (data instanceof DownloadProgressData) {
    const progressData: DownloadProgressData = data
    if (progressData.episodeId === this.episodeId) {
      this.downloadProgress = progressData.percent
    }
  }
}))
```

---

## 2. ViewModel 数据加载模式（V2）

**模式**：ViewModel 标为 `@ObservedV2` 类，`@Trace` 暴露需要观察的字段；组件通过 `@Local` 持有 ViewModel 实例，在 `aboutToAppear` 中调用 `vm.loadData()`，EventBus 事件触发重新加载。

```typescript
// ViewModel 层 — 文件: viewmodels/HomeViewModel.ets（V2）
@ObservedV2
export class HomeViewModel {
  private feedDao: FeedDao = new FeedDao()
  private feedItemDao: FeedItemDao = new FeedItemDao()

  // V2：需要 UI 观察的字段加 @Trace
  @Trace recentEpisodes: FeedItem[] = []
  @Trace continueListening: FeedItem[] = []
  @Trace newEpisodes: FeedItem[] = []
  @Trace surpriseEpisodes: FeedItem[] = []
  @Trace classicFeeds: Feed[] = []
  @Trace subscriptionCount: number = 0

  async loadData(): Promise<void> {
    const items = await this.feedItemDao.getRecentlyPublished(0, 50)
    this.recentEpisodes = items

    const feeds = await this.feedDao.getAllFeeds()
    this.subscriptionCount = feeds.length
    this.classicFeeds = feeds

    // 分类处理
    const continueItems: FeedItem[] = []
    const newItems: FeedItem[] = []
    for (let i = 0; i < items.length; i++) {
      const item = items[i]
      if (item.media !== null && item.media.position > 0 && !item.isPlayed()) {
        continueItems.push(item)
      }
      if (item.state === PLAY_STATE_NEW) {
        newItems.push(item)
      }
    }
    this.continueListening = continueItems
    this.newEpisodes = newItems

    const randomItems = await this.feedItemDao.getRandomEpisodes(5)
    this.surpriseEpisodes = randomItems
  }
}
```

```typescript
// 组件层 — 使用 ViewModel（V2）
@ComponentV2
export struct HomeComponent {
  @Local private vm: HomeViewModel = new HomeViewModel()
  @Local private isLoading: boolean = true

  private unsubscribers: (() => void)[] = []

  aboutToAppear(): void {
    this.loadData()
    this.setupEventSubscriptions()
  }

  private async loadData(): Promise<void> {
    this.isLoading = true
    await this.vm.loadData()
    this.isLoading = false
  }

  private setupEventSubscriptions(): void {
    const bus = EventBus.getInstance()
    this.unsubscribers.push(bus.subscribe(EVENT_FEED_UPDATED, () => {
      this.loadData()
    }))
    this.unsubscribers.push(bus.subscribe(EVENT_SUBSCRIPTION_ADDED, () => {
      this.loadData()
    }))
    this.unsubscribers.push(bus.subscribe(EVENT_QUEUE_CHANGED, () => {
      this.loadData()
    }))
  }

  aboutToDisappear(): void {
    for (let i = 0; i < this.unsubscribers.length; i++) {
      this.unsubscribers[i]()
    }
  }

  build() {
    Column() {
      if (this.isLoading) {
        LoadingProgress().width(48).height(48)
      } else {
        // 渲染 vm.recentEpisodes 等（@Trace 字段变化时自动刷新）
        Text(`订阅数: ${this.vm.subscriptionCount}`)
      }
    }
  }
}
```

**ViewModel vs @Local 职责分离（V2）**：

| 层 | 职责 | 示例 |
|------|------|------|
| `@ObservedV2` ViewModel | 数据加载、业务逻辑、DAO 调用 | `loadData()`, `toggleFavorite()` |
| `@Local` | UI 驱动状态（组件本地） | `isLoading`, `currentTab` |
| `@Param + @Event` | 组件间数据流（替代 V1 `@Prop / @Link`） | 父子传值 + 双向同步 |
| EventBus | 跨组件通知 | `EVENT_FEED_UPDATED` → 重新加载 |
| `AppStorageV2.connect` | 全局共享状态（替代 V1 `@StorageLink`） | `PlaybackModel` 全局播放状态 |

---

## 3. ForEach / Repeat key 生成器（V2 通用）

**核心原则**：key 必须包含会变化的字段，否则 UI 不会刷新。V1/V2 同样适用。

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
  let key = item.id.toString()
  key += '_' + item.state.toString()                                    // 播放状态
  if (item.media !== null) {
    key += '_' + item.media.position.toString()                         // 播放进度
    key += '_' + (item.media.isDownloaded() ? '1' : '0')                // 下载状态
  }
  return key
})
```

**V2 推荐 Repeat 的 key 写法**：

```typescript
@ObservedV2
class FeedItem {
  id: string = ''
  @Trace state: number = 0
  @Trace position: number = 0
}

@ComponentV2
struct EpisodeRepeatList {
  @Local items: FeedItem[] = []

  build() {
    List() {
      Repeat<FeedItem>(this.items)
        .each((rep: RepeatItem<FeedItem>) => {
          ListItem() {
            EpisodeListItem({ item: rep.item })
          }
        })
        .key((item: FeedItem) => `${item.id}_${item.state}_${item.position}`)
        .virtualScroll({ totalCount: this.items.length })
    }
  }
}
```

> **V2 优势**：当 `FeedItem` 是 `@ObservedV2` 类时，`@Trace` 属性变化会让组件内的 `Text(this.item.state)` 等绑定自动刷新，**部分场景下 key 可以只用稳定 id**，依靠 `@Trace` 而非 key 重建。但若整个 `EpisodeListItem` 内部状态需要重建（如 `aboutToAppear` 副作用），仍需把变化字段放入 key。

**LazyForEach 的 key 规则一样**（V1/V2 通用）：

```typescript
// FeedItemDataSource 实现 IDataSource 接口
LazyForEach(this.dataSource, (item: FeedItem) => {
  EpisodeListItem({ item: item })
}, (item: FeedItem) => {
  return item.id.toString() + '_' + item.state.toString()
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
- `ForEach / LazyForEach / Repeat` 都需要 key 生成器
- 如果 key 不变，即使底层数据变了，UI 也不会重建子组件（除非 V2 `@Trace` 属性级触发）
- 不要在 key 中包含太多字段（会导致不必要的重建），只包含影响 UI 呈现的字段

---

## 4. 用 @Monitor 响应状态变化（V2 替代 V1 @Watch）

V2 用 `@Monitor` 方法装饰器替代 V1 的 `@Watch`，签名带 `IMonitor`：

```typescript
@ComponentV2
struct SearchPage {
  @Local keyword: string = ''
  @Local sortBy: string = 'date'
  @Local results: SearchResult[] = []

  @Monitor('keyword')
  onKeywordChange(monitor: IMonitor): void {
    // 防抖搜索：keyword 变化时触发
    this.debouncedSearch(this.keyword)
  }

  @Monitor('keyword', 'sortBy')
  onAnyFilterChange(monitor: IMonitor): void {
    // monitor.dirty 返回变化的属性名集合
    monitor.dirty.forEach(name => {
      console.info(`${name} changed`)
    })
  }

  private searchTimer: number = -1
  private debouncedSearch(kw: string): void {
    if (this.searchTimer !== -1) {
      clearTimeout(this.searchTimer)
    }
    this.searchTimer = setTimeout(() => {
      this.performSearch(kw)
    }, 300)
  }

  private async performSearch(kw: string): Promise<void> {
    if (kw.length === 0) {
      this.results = []
      return
    }
    this.results = await SearchService.search(kw, this.sortBy)
  }

  build() {
    Column() {
      TextInput({ placeholder: '搜索...', text: this.keyword })
        .onChange((v: string) => { this.keyword = v })
      Text(`找到 ${this.results.length} 条结果`)
    }
  }
}
```

**陷阱**：`@Monitor` 回调中**不要修改被监听的属性**，否则可能死循环：

```typescript
// 危险 — 可能无限循环
@Monitor('count')
onCountChange(monitor: IMonitor): void {
  this.count = this.count + 1   // 又触发 onCountChange！
}

// 正确 — 修改其他变量
@Monitor('count')
onCountChange(monitor: IMonitor): void {
  this.displayText = `Count is ${this.count}`
}
```

---

## V2 完整生命周期顺序

| 时机 | 钩子 | 用途 |
|------|------|------|
| 组件构造后、首次 build 前 | `aboutToAppear()` | 数据加载、订阅事件、初始化 ViewModel |
| 每次 build 后 | (无显式钩子) | — |
| 状态变化触发刷新前 | `@Monitor` 方法 | 响应状态变化 |
| 路由进入页面后 | `onPageShow()` | 仅 `@Entry` 页面，恢复刷新 |
| 路由离开页面前 | `onPageHide()` | 仅 `@Entry` 页面，暂停刷新 |
| 组件销毁前 | `aboutToDisappear()` | 取消订阅、释放资源 |
| 复用前（@ReusableV2） | `aboutToReuse()` ⚠️**无入参** | 复用时框架自动按父传入值刷新 @Param、按初始值重置 @Local；可在此重置纯 @Local 派生态，**勿手动给 @Param 赋值**（@Param 只读，赋值报 `Cannot assign to read-only property`）。V1 才是 `aboutToReuse(params)` |

> **@ReusableV2 复用 id**：可选——省略则默认用组件名作 reuseId；如需指定，用 `.reuse({ reuseId: () => 'xxx' })`（`reuseId` 是 `ReuseIdCallback` 回调形），**不要**写成 `.reuse('xxx')`（字符串 → 报 `Type 'string' is not assignable to type 'ReuseIdCallback'`）或 V1 的 `.reuseId('xxx')`（V2 上不存在该属性）。

---

## 跨文档参考

- [`v2-common-components.md`](./v2-common-components.md) — V2 常用组件用法
- [`v2-layout-patterns.md`](./v2-layout-patterns.md) — V2 布局模板
- [`v2-prop-naming-rules.md`](./v2-prop-naming-rules.md) — V2 变量命名规则
- [`v2-media-app-components.md`](./v2-media-app-components.md) — V2 媒体应用模式
- `arkts-state-manager/references/v2-decorators.md` — V2 装饰器完整参考
- `arkts-state-manager/references/v2-global-state.md` — V2 全局状态模板
