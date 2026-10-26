# 实战状态管理模式（**V1 历史文档 — Legacy**）

> ⚠️ **本项目锁 ArkTS V2**。本文档为 **V1 历史参考**（基于 V1 `@StorageLink / @Provide/@Consume / PersistentStorage` 等装饰器组合的实战模式），仅用于阅读老代码或迁移老项目时查阅。
>
> **新代码请使用 V2 实战模式**：参阅 [`v2-real-world.md`](./v2-real-world.md)（主参考，含 `AppStorageV2 + @ObservedV2 + @Trace` 等 V2 模式）。

> 基于 AntennaPod ArkTS 播客应用实战总结的 5 种 V1 状态管理模式：GlobalState 注册表、双层持久化、PlaybackController 绑定、EventBus 联动、@Provide/@Consume。
> 源码参考：`entry/src/main/ets/common/GlobalState.ets`、`entry/src/main/ets/helpers/UserPreferences.ets`、`entry/src/main/ets/playback/PlaybackController.ets`

---

## 1. GlobalState 25+ key 注册表

所有 `@StorageLink` 使用的 key 必须在任何组件的 `@StorageLink` 声明之前通过 `AppStorage.setOrCreate` 初始化。`GlobalState.init()` 在应用启动时（`Index.aboutToAppear`）调用一次。

### 完整 key 分类表

| 类别 | key | 类型 | 默认值 | 用途 |
|------|-----|------|--------|------|
| **播放器状态** | | | | |
| | `isPlaying` | boolean | false | 是否正在播放 |
| | `currentEpisodeTitle` | string | '' | 当前剧集标题 |
| | `currentFeedTitle` | string | '' | 当前播客名 |
| | `currentEpisodeId` | number | -1 | 当前剧集 ID |
| | `currentCoverUrl` | string | '' | 当前封面 URL |
| | `playbackPosition` | number | 0 | 播放位置（ms） |
| | `playbackDuration` | number | 0 | 总时长（ms） |
| | `currentEpisodePubDate` | string | '' | 当前剧集发布日期 |
| **UI 状态** | | | | |
| | `currentTabIndex` | number | 0 | 当前选中 Tab |
| | `isPlayerVisible` | boolean | false | MiniPlayer 是否可见 |
| | `isFullPlayerVisible` | boolean | false | 全屏播放器是否可见 |
| **应用状态** | | | | |
| | `dbReady` | boolean | false | 数据库是否就绪 |
| | `isFeedUpdateRunning` | boolean | false | 是否正在刷新 Feed |
| | `themeMode` | number | 0 | 主题模式 |
| **偏好设置** | | | | |
| | `enqueueDownloaded` | boolean | true | 下载后自动入队 |
| | `enqueueLocation` | number | 1 | 入队位置 |
| | `playbackSpeed` | number | 1.0 | 播放速度 |
| | `fastForwardSecs` | number | 30 | 快进秒数 |
| | `rewindSecs` | number | 10 | 后退秒数 |
| | `skipSilence` | boolean | false | 跳过静音 |
| | `showRemainTime` | boolean | false | 显示剩余时间 |
| | `streamOverDownload` | boolean | false | 优先流式播放 |
| | `useEpisodeCover` | boolean | true | 使用剧集封面 |

### 初始化代码

```typescript
// 文件: common/GlobalState.ets
private static initAppStorage(): void {
  // Database readiness flag
  AppStorage.setOrCreate<boolean>('dbReady', false);

  // Player state
  AppStorage.setOrCreate<boolean>('isPlaying', false);
  AppStorage.setOrCreate<string>('currentEpisodeTitle', '');
  AppStorage.setOrCreate<string>('currentFeedTitle', '');
  AppStorage.setOrCreate<number>('currentEpisodeId', -1);
  AppStorage.setOrCreate<string>('currentCoverUrl', '');
  AppStorage.setOrCreate<number>('playbackPosition', 0);
  AppStorage.setOrCreate<number>('playbackDuration', 0);

  // UI state
  AppStorage.setOrCreate<number>('currentTabIndex', 0);
  AppStorage.setOrCreate<boolean>('isPlayerVisible', false);
  AppStorage.setOrCreate<boolean>('isFullPlayerVisible', false);

  // App state
  AppStorage.setOrCreate<boolean>('isFeedUpdateRunning', false);
  AppStorage.setOrCreate<number>('themeMode', 0);

  // Preferences-driven UI state (defaults, overwritten by syncToAppStorage)
  AppStorage.setOrCreate<boolean>('enqueueDownloaded', true);
  AppStorage.setOrCreate<number>('enqueueLocation', 1);
  AppStorage.setOrCreate<number>('playbackSpeed', 1.0);
  AppStorage.setOrCreate<number>('fastForwardSecs', 30);
  AppStorage.setOrCreate<number>('rewindSecs', 10);
  AppStorage.setOrCreate<boolean>('skipSilence', false);
  AppStorage.setOrCreate<boolean>('showRemainTime', false);
  AppStorage.setOrCreate<boolean>('streamOverDownload', false);
  AppStorage.setOrCreate<boolean>('useEpisodeCover', true);

  // Episode pub date for FullPlayer display
  AppStorage.setOrCreate<string>('currentEpisodePubDate', '');
}
```

### 初始化时序

```
EntryAbility.onCreate()
  → Index.aboutToAppear()
    → GlobalState.init(context)
      → initAppStorage()           // 1. 先注册所有 key
      → PodDatabase.init()          // 2. 初始化数据库
      → UserPreferences.init()      // 3. 初始化偏好
      → syncToAppStorage()          // 4. 用持久化值覆盖默认值
      → dbReady = true              // 5. 通知 UI 可以渲染
    → PlaybackController.restoreLastPlayedEpisode()  // 6. 恢复上次播放
    → DefaultFeedInitializer.initDefaultFeedsIfEmpty() // 7. 首次安装初始化
```

---

## 2. 双层持久化 — Preferences + AppStorage

**架构**：`Preferences`（磁盘持久化）+ `AppStorage`（内存 UI 驱动）。

- `Preferences` 是持久化存储（重启后保留）
- `AppStorage` 是内存级存储（重启后丢失，需要从 Preferences 恢复）
- `@StorageLink` 只绑定 `AppStorage`

```
[Preferences 磁盘]  ←→  [AppStorage 内存]  ←→  [@StorageLink UI]
     持久化                 UI 驱动                组件绑定
```

### syncToAppStorage — Preferences → AppStorage

```typescript
// 文件: helpers/UserPreferences.ets
syncToAppStorage(): void {
  AppStorage.setOrCreate<number>('themeMode', this.getThemeMode());
  AppStorage.setOrCreate<boolean>('enqueueDownloaded', this.isEnqueueDownloaded());
  AppStorage.setOrCreate<number>('enqueueLocation', this.getEnqueueLocation());
  AppStorage.setOrCreate<number>('playbackSpeed', this.getPlaybackSpeed());
  AppStorage.setOrCreate<number>('fastForwardSecs', this.getFastForwardSecs());
  AppStorage.setOrCreate<number>('rewindSecs', this.getRewindSecs());
  AppStorage.setOrCreate<boolean>('skipSilence', this.isSkipSilence());
  AppStorage.setOrCreate<boolean>('showRemainTime', this.isShowRemainTime());
  AppStorage.setOrCreate<boolean>('streamOverDownload', this.isStreamOverDownload());
  AppStorage.setOrCreate<boolean>('useEpisodeCover', this.isUseEpisodeCover());
}
```

### 设置变更 — UI → AppStorage → Preferences

```typescript
// 设置页面修改播放速度
async onSpeedChanged(newSpeed: number): Promise<void> {
  // 1. 更新 AppStorage（立即驱动 UI）
  AppStorage.setOrCreate<number>('playbackSpeed', newSpeed);
  // 2. 持久化到 Preferences（下次启动恢复）
  await UserPreferences.getInstance().setPlaybackSpeed(newSpeed);
}
```

### Preferences 安全读取（typeof 检查）

```typescript
// ArkTS 禁止 as，用 typeof 检查
private getInt(key: string, def: number): number {
  if (this.prefs === undefined) {
    return def;
  }
  const val = this.prefs.getSync(key, def);
  if (typeof val === 'number') {
    return val;
  }
  return def;
}

private getBoolean(key: string, def: boolean): boolean {
  if (this.prefs === undefined) {
    return def;
  }
  const val = this.prefs.getSync(key, def);
  if (typeof val === 'boolean') {
    return val;
  }
  return def;
}
```

---

## 3. PlaybackController → AppStorage 绑定

PlaybackController 是非组件类（单例），不能用 `@StorageLink`，直接调用 `AppStorage.setOrCreate`。

### 播放开始 — 写入完整状态

```typescript
// PlaybackController.playEpisode() 中
AppStorage.setOrCreate<string>('currentEpisodeTitle', item.title);
AppStorage.setOrCreate<string>('currentFeedTitle',
  this.currentFeed !== undefined ? this.currentFeed.getDisplayTitle() : '');
AppStorage.setOrCreate<number>('currentEpisodeId', item.id);
AppStorage.setOrCreate<string>('currentCoverUrl', item.getImageLocation());
AppStorage.setOrCreate<boolean>('isPlayerVisible', true);
AppStorage.setOrCreate<number>('playbackPosition', feedMedia.position);
AppStorage.setOrCreate<number>('playbackDuration', feedMedia.duration);
AppStorage.setOrCreate<string>('currentEpisodePubDate', item.getPubDateStr());
```

### 实时位置更新 — AVPlayer timeUpdate 回调

```typescript
// setupAVPlayerCallbacks() 中
player.on('timeUpdate', (time: number) => {
  AppStorage.setOrCreate<number>('playbackPosition', time);
  EventBus.getInstance().publish(EVENT_PLAYBACK_POSITION,
    new PlaybackPositionData(time, AppStorage.get<number>('playbackDuration') ?? 0));
});
```

### 播放/暂停状态切换

```typescript
private onPlaying(): void {
  this.setStatus(PLAYER_STATUS_PLAYING);
  AppStorage.setOrCreate<boolean>('isPlaying', true);
  this.startPositionSaveTimer();
}

private onPaused(): void {
  this.setStatus(PLAYER_STATUS_PAUSED);
  AppStorage.setOrCreate<boolean>('isPlaying', false);
  this.stopPositionSaveTimer();
  this.savePosition();
}
```

### 停止 — 清理所有状态

```typescript
private async stopInternal(clearUI: boolean): Promise<void> {
  // ...
  AppStorage.setOrCreate<boolean>('isPlaying', false);

  if (clearUI) {
    AppStorage.setOrCreate<boolean>('isPlayerVisible', false);
    AppStorage.setOrCreate<string>('currentEpisodeTitle', '');
    AppStorage.setOrCreate<string>('currentFeedTitle', '');
    AppStorage.setOrCreate<number>('currentEpisodeId', -1);
    AppStorage.setOrCreate<string>('currentCoverUrl', '');
    AppStorage.setOrCreate<number>('playbackPosition', 0);
    AppStorage.setOrCreate<number>('playbackDuration', 0);
    AppStorage.setOrCreate<string>('currentEpisodePubDate', '');
  }
}
```

### 从 AppStorage 读取（非组件代码）

```typescript
// PlaybackController 从 AppStorage 读取当前位置
const pos = AppStorage.get<number>('playbackPosition');
const currentPos = pos !== undefined ? pos : 0;

// 读取用户设置
const rewindSecs = AppStorage.get<number>('rewindSecs');
const secs = rewindSecs !== undefined ? rewindSecs : 10;
```

---

## 4. EventBus + @State 联动

EventBus 用于非状态绑定的跨组件通知（如数据变更），收到事件后触发 `@State` 变量更新。

```
[PlaybackController]                [EpisodeDetailComponent]
     │                                    │
     │ 标记播放完成                         │
     │ EventBus.publish(                   │
     │   EVENT_EPISODE_PLAY_STATE_CHANGED) │
     │                                    │
     └───────── EventBus ────────────────→ │
                                          │ bus.subscribe(EVENT_..., () => {
                                          │   this.reloadEpisode()  // 重新加载
                                          │   // 更新 @State 变量
                                          │   this.episodeState = PLAY_STATE_PLAYED
                                          │ })
```

**与 @StorageLink 的分工**：

| 机制 | 适用场景 | 示例 |
|------|---------|------|
| `@StorageLink` | 持续性全局状态（播放位置、主题） | `playbackPosition`, `isPlaying` |
| `EventBus` | 一次性通知（数据变更、操作完成） | `EVENT_FEED_UPDATED`, `EVENT_QUEUE_CHANGED` |
| `@State` | 组件内部 UI 状态 | `isLoading`, `title`, `isFavorite` |
| `@Prop` | 父→子单向传递 | `icon`, `message`, `actionLabel` |

---

## 5. @Provide/@Consume NavPathStack

`NavPathStack` 使用 `@Provide/@Consume` 在组件树中共享，让任何子组件都能导航。

```typescript
// Index.ets — 根组件提供
@Entry
@Component
struct Index {
  @Provide('navPathStack') navPathStack: NavPathStack = new NavPathStack();
  // ...
}

// 任意子组件消费
@Component
export struct FeedDetailComponent {
  @Consume('navPathStack') navPathStack: NavPathStack;

  build() {
    NavDestination() {
      // ...
      Button('View Episode')
        .onClick(() => {
          const param = new EpisodeDetailParam();
          param.episodeId = item.id;
          param.feedId = item.feedId;
          this.navPathStack.pushPathByName(RouteName.EPISODE_DETAIL, param);
        })
    }
  }
}
```

**@Provide/@Consume vs @StorageLink**：

| 特性 | @Provide/@Consume | @StorageLink |
|------|-------------------|-------------|
| 作用域 | 组件树内（父→后代） | 全局（任何组件） |
| 存储位置 | 组件树上下文 | AppStorage |
| 适用类型 | 对象引用（NavPathStack） | 基础类型（string, number, boolean） |
| 典型用途 | NavPathStack 共享 | 播放状态、偏好设置 |
