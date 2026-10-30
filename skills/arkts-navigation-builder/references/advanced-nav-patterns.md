# 高级导航模式（**V1 历史文档 — Legacy**）

> ⚠️ **本项目锁 ArkTS V2**。本文档为 **V1 历史参考**（`@Component / @State / @Provide / @Consume / @StorageLink` 等），仅用于阅读老代码或迁移老项目时查阅。
>
> **新代码请使用 V2 装饰器**：参阅 [`v2-advanced-nav-patterns.md`](./v2-advanced-nav-patterns.md)（主参考）和 [`SKILL.md`](../SKILL.md)。
>
> 注：路由参数类、routerMap @Builder、onReady 参数接收、路由常量管理等模式本身在 V1/V2 中思路一致，但 V2 推荐用 `@ObservedV2` 类作为参数类，并用 `AppStorageV2.connect` 替代 `@StorageLink` 实现 FullPlayer 隐藏 Tab 等跨组件状态共享。

> 基于 AntennaPod ArkTS 播客应用实战总结的 5 种导航模式：路由参数类、routerMap、FullPlayer 隐藏 Tab、onReady 参数接收、路由常量管理。
> 源码参考：`entry/src/main/ets/common/AppRouter.ets`、`entry/src/main/ets/pages/Index.ets`

---

## 1. 路由参数类定义

每个需要参数的 NavDestination 都有一个对应的参数类。使用 `class`（不是 interface），字段必须有默认值（ArkTS 严格模式要求）。

```typescript
// 文件: common/AppRouter.ets (行 29-60)
export class FeedDetailParam {
  feedId: number = 0;
}

export class EpisodeDetailParam {
  episodeId: number = 0;
  feedId: number = 0;
}

export class FeedSettingsParam {
  feedId: number = 0;
}

export class FeedInfoParam {
  feedId: number = 0;
}

export class OnlineFeedViewParam {
  feedUrl: string = '';
}

export class VideoPlayerParam {
  episodeId: number = 0;
}

export class OpmlImportParam {
  filePath: string = '';
}

export class FullPlayerParam {
  // No params needed — reads from AppStorage
}
```

**设计要点**：
- 每个参数类对应一个 NavDestination 页面
- 所有字段必须有默认值（ArkTS 不允许未初始化的字段）
- `FullPlayerParam` 不需要参数（数据来自 AppStorage），但仍定义空类用于类型一致性
- 传递参数时使用 `instanceof` 检查类型，而不是 `as` 断言

---

## 2. routerMap @Builder — 路由映射

在 `Index.ets` 中定义 `@Builder routerMap`，将路由名映射到对应的组件。
使用 `if/else` 链（ArkTS 不支持 `switch` 在 @Builder 中直接用）。

```typescript
// 文件: pages/Index.ets (行 49-81)
@Builder
routerMap(name: string) {
  if (name === RouteName.FEED_DETAIL) {
    FeedDetailComponent()
  } else if (name === RouteName.EPISODE_DETAIL) {
    EpisodeDetailComponent()
  } else if (name === RouteName.FEED_SETTINGS) {
    FeedSettingsComponent()
  } else if (name === RouteName.FEED_INFO) {
    FeedInfoComponent()
  } else if (name === RouteName.ONLINE_FEED_VIEW) {
    OnlineFeedViewComponent()
  } else if (name === RouteName.ADD_FEED) {
    AddFeedComponent()
  } else if (name === RouteName.PLAYBACK_HISTORY) {
    PlaybackHistoryComponent()
  } else if (name === RouteName.DOWNLOADS) {
    DownloadsComponent()
  } else if (name === RouteName.STATISTICS) {
    StatisticsComponent()
  } else if (name === RouteName.SETTINGS) {
    SettingsComponent()
  } else if (name === RouteName.VIDEO_PLAYER) {
    VideoPlayerComponent()
  } else if (name === RouteName.OPML_IMPORT) {
    OpmlImportComponent()
  } else if (name === RouteName.FULL_PLAYER) {
    FullPlayerComponent()
  } else if (name === RouteName.EPISODES) {
    AllEpisodesComponent()
  } else if (name === RouteName.SEARCH) {
    SearchComponent()
  }
}
```

**绑定到 Navigation**：

```typescript
Navigation(this.navPathStack) {
  // Tab 内容...
}
.navDestination(this.routerMap)  // 注册路由映射
.hideTitleBar(true)              // 隐藏 Navigation 自带的标题栏
.mode(NavigationMode.Stack)      // 使用栈模式
```

---

## 3. FullPlayer 隐藏 Tab

当 FullPlayer 打开时，MiniPlayer 和 Tab 栏都需要隐藏，实现全屏沉浸式播放体验。

**实现方式**：`@StorageLink('isFullPlayerVisible')` 控制 `if` 条件渲染。

```typescript
// Index.ets 整体结构
build() {
  Column() {
    // Navigation — 始终存在
    Navigation(this.navPathStack) { /* Tab 内容 */ }
      .layoutWeight(1)

    // MiniPlayer — 仅在播放中且非全屏时显示
    if (this.isPlayerVisible && !this.isFullPlayerVisible) {
      // MiniPlayer 组件...
    }

    // Tab 栏 — 仅在非全屏时显示
    if (!this.isFullPlayerVisible) {
      Row() {
        // 5 个 tab...
      }
      .height(56)
    }
  }
}
```

**FullPlayerComponent 中设置标志**：

```typescript
@Component
export struct FullPlayerComponent {
  @StorageLink('isFullPlayerVisible') isFullPlayerVisible: boolean = false;

  build() {
    NavDestination() {
      // 全屏播放器 UI...
    }
    .onReady(() => {
      this.isFullPlayerVisible = true;  // 进入时隐藏 Tab
    })
    .onDisAppear(() => {
      this.isFullPlayerVisible = false; // 退出时恢复 Tab
    })
  }
}
```

**为什么用 @StorageLink 而不是 @State/事件**：
- `isFullPlayerVisible` 需要跨组件通信（FullPlayer 组件 → Index 页面）
- 它们不在同一组件树层级中（FullPlayer 在 NavDestination 内）
- @StorageLink 通过 AppStorage 实现双向绑定，任意组件修改都能立即反映

---

## 4. onReady 参数接收

**关键规则**：NavDestination 参数必须在 `onReady` 回调中获取，不能在 `aboutToAppear` 中获取（此时参数尚未就绪）。

```typescript
@Component
export struct EpisodeDetailComponent {
  @State episodeId: number = 0;
  @State feedId: number = 0;
  private vm: EpisodeDetailViewModel = new EpisodeDetailViewModel();

  build() {
    NavDestination() {
      // UI 内容...
    }
    .onReady((ctx: NavDestinationContext) => {
      // 在 onReady 中获取参数
      const param = ctx.pathInfo.param;
      if (param instanceof EpisodeDetailParam) {
        this.episodeId = param.episodeId;
        this.feedId = param.feedId;
        this.loadData();
      }
    })
  }
}
```

**发送参数**：

```typescript
// 跳转到剧集详情
const param = new EpisodeDetailParam();
param.episodeId = item.id;
param.feedId = item.feedId;
this.navPathStack.pushPathByName(RouteName.EPISODE_DETAIL, param);
```

**类型检查必须用 instanceof**（ArkTS 禁止 `as`）：

```typescript
// 正确 — 使用 instanceof
const param = ctx.pathInfo.param;
if (param instanceof FeedDetailParam) {
  this.feedId = param.feedId;
}

// 错误 — ArkTS 严格模式禁止 as
// const param = ctx.pathInfo.param as FeedDetailParam;
```

**常见错误**：

```typescript
// 错误：aboutToAppear 中参数尚未就绪
aboutToAppear(): void {
  // ctx.pathInfo.param 此时是 undefined！
  // 导致页面空白或崩溃
}

// 正确：使用 onReady
.onReady((ctx: NavDestinationContext) => {
  // 参数已就绪，可以安全读取
})
```

---

## 5. 路由常量集中管理

所有路由名使用 `RouteName` 静态类集中定义，避免字符串硬编码。

```typescript
// 文件: common/AppRouter.ets (行 1-24)
export class RouteName {
  static readonly HOME: string = 'home';
  static readonly SUBSCRIPTIONS: string = 'subscriptions';
  static readonly QUEUE: string = 'queue';
  static readonly EPISODES: string = 'episodes';
  static readonly SEARCH: string = 'search';
  static readonly FEED_DETAIL: string = 'feedDetail';
  static readonly EPISODE_DETAIL: string = 'episodeDetail';
  static readonly FEED_SETTINGS: string = 'feedSettings';
  static readonly FEED_INFO: string = 'feedInfo';
  static readonly ONLINE_FEED_VIEW: string = 'onlineFeedView';
  static readonly ADD_FEED: string = 'addFeed';
  static readonly PLAYBACK_HISTORY: string = 'playbackHistory';
  static readonly DOWNLOADS: string = 'downloads';
  static readonly STATISTICS: string = 'statistics';
  static readonly SETTINGS: string = 'settings';
  static readonly VIDEO_PLAYER: string = 'videoPlayer';
  static readonly OPML_IMPORT: string = 'opmlImport';
  static readonly FULL_PLAYER: string = 'fullPlayer';
  static readonly INBOX: string = 'inbox';
}
```

**总计 19 个路由**，可分为 4 类：

| 类别 | 路由 |
|------|------|
| Tab 页 (5) | HOME, QUEUE, INBOX, SUBSCRIPTIONS, EPISODES |
| 详情页 (4) | FEED_DETAIL, EPISODE_DETAIL, FEED_SETTINGS, FEED_INFO |
| 功能页 (6) | SEARCH, ADD_FEED, ONLINE_FEED_VIEW, DOWNLOADS, PLAYBACK_HISTORY, STATISTICS |
| 全屏页 (4) | FULL_PLAYER, VIDEO_PLAYER, SETTINGS, OPML_IMPORT |

**NavPathStack 操作速查**：

```typescript
// NavPathStack 由 @Provide 共享给所有子组件
@Provide('navPathStack') navPathStack: NavPathStack = new NavPathStack();

// 子组件通过 @Consume 获取
@Consume('navPathStack') navPathStack: NavPathStack;

// 推入页面
this.navPathStack.pushPathByName(RouteName.FEED_DETAIL, param);

// 返回上一页
this.navPathStack.pop();

// 清除栈（回到根页面）
this.navPathStack.clear();

// 替换当前页面
this.navPathStack.replacePath({ name: RouteName.HOME });
```
