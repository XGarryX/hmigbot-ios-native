# 音频应用脚手架

> 基于 AntennaPod ArkTS 播客应用实战总结的音频应用项目模板：module.json5 配置、GlobalState 初始化、层依赖规则、文件清单。
> 源码参考：`entry/src/main/module.json5`、`entry/src/main/ets/common/GlobalState.ets`
>
> **ArkTS V2 lock**：本文档代码示例使用 V2 装饰器（`@ComponentV2 / @Local / @ObservedV2 / @Trace / AppStorageV2 / PersistenceV2`）。`module.json5` 等配置文件 V1/V2 通用。V1 老项目（`@StorageLink + AppStorage.setOrCreate`）兼容写法见 `arkts-state-manager/references/state-decorators.md`。

---

## 1. module.json5 音频应用模板

音频应用需要 3 个权限 + 1 个 backgroundMode + workScheduler 扩展。

```json5
{
  "module": {
    "name": "entry",
    "type": "entry",
    "description": "$string:module_desc",
    "mainElement": "EntryAbility",
    "deviceTypes": ["phone", "tablet"],
    "deliveryWithInstall": true,
    "installationFree": false,
    "pages": "$profile:main_pages",

    // 3 个必要权限
    "requestPermissions": [
      {
        "name": "ohos.permission.INTERNET",
        "reason": "$string:permission_internet_reason",
        "usedScene": {
          "abilities": ["EntryAbility"],
          "when": "always"
        }
      },
      {
        "name": "ohos.permission.GET_NETWORK_INFO",
        "reason": "$string:permission_network_info_reason",
        "usedScene": {
          "abilities": ["EntryAbility"],
          "when": "always"
        }
      },
      {
        "name": "ohos.permission.KEEP_BACKGROUND_RUNNING",
        "reason": "$string:permission_background_running_reason",
        "usedScene": {
          "abilities": ["EntryAbility"],
          "when": "inuse"
        }
      }
    ],

    "abilities": [
      {
        "name": "EntryAbility",
        "srcEntry": "./ets/entryability/EntryAbility.ets",
        "description": "$string:EntryAbility_desc",
        "icon": "$media:layered_image",
        "label": "$string:EntryAbility_label",
        "startWindowIcon": "$media:startIcon",
        "startWindowBackground": "$color:start_window_background",
        "exported": true,
        // 后台播放 — 必须声明
        "backgroundModes": ["audioPlayback"],
        "skills": [
          {
            "entities": ["entity.system.home"],
            "actions": ["ohos.want.action.home"]
          }
        ]
      }
      // 多 ability 注意：abilities[] 里【每个】 ability 都必须带 startWindowIcon + startWindowBackground
      //   （schema 强制，缺任一则 PreBuild 报 "Schema validate failed: must have required property
      //   'startWindowIcon'"）。若拆出独立的后台播放 ability，照样给它补这两个字段 + 引用的 media/color 资源。
    ],

    "extensionAbilities": [
      {
        "name": "EntryBackupAbility",
        "srcEntry": "./ets/entrybackupability/EntryBackupAbility.ets",
        "type": "backup",
        "exported": false,
        "metadata": [
          {
            "name": "ohos.extension.backup",
            "resource": "$profile:backup_config"
          }
        ]
      },
      {
        // workScheduler 定时任务（如定时刷新 Feed）
        "name": "FeedUpdateWorkAbility",
        "srcEntry": "./ets/workers/FeedUpdateWorkAbility.ets",
        "type": "workScheduler",
        "exported": false
      }
    ]
  }
}
```

### 权限用途说明

| 权限 | 用途 | when |
|------|------|------|
| `INTERNET` | 网络请求（流式播放、下载、RSS 刷新） | always |
| `GET_NETWORK_INFO` | 检测网络状态（WiFi/蜂窝） | always |
| `KEEP_BACKGROUND_RUNNING` | 后台持续播放音频 | inuse |

### backgroundModes 类型

| 值 | 用途 |
|------|------|
| `audioPlayback` | 后台音频播放 |
| `dataTransfer` | 后台大文件下载 |
| `location` | 后台持续定位 |

---

## 2. GlobalState 初始化清单（V2 模式）

V2 不再用散落的 string key + `AppStorage.setOrCreate`，而是把相关字段聚合到 `@ObservedV2` 模型类中，通过 `AppStorageV2.connect(Cls, key, defaultCreator)` 暴露给所有页面/组件。一个 model = 一个 key = 一个共享实例。

```typescript
// 文件: common/PlaybackModel.ets — 播放器状态（V1 8 个 key 合并为 1 个类）
@ObservedV2
export class PlaybackModel {
  @Trace isPlaying: boolean = false;
  @Trace currentEpisodeTitle: string = '';
  @Trace currentFeedTitle: string = '';
  @Trace currentEpisodeId: number = -1;
  @Trace currentCoverUrl: string = '';
  @Trace playbackPosition: number = 0;
  @Trace playbackDuration: number = 0;
  @Trace currentEpisodePubDate: string = '';
}

// 文件: common/UiStateModel.ets — UI 状态（V1 3 个 key）
@ObservedV2
export class UiStateModel {
  @Trace currentTabIndex: number = 0;
  @Trace isPlayerVisible: boolean = false;
  @Trace isFullPlayerVisible: boolean = false;
}

// 文件: common/AppStateModel.ets — 应用运行时状态（V1 2 个 key）
@ObservedV2
export class AppStateModel {
  @Trace dbReady: boolean = false;
  @Trace isFeedUpdateRunning: boolean = false;
  @Trace themeMode: number = 0;
}

// 文件: common/UserPrefsModel.ets — 偏好设置（V1 9 个 key，PersistenceV2 自动落盘）
@ObservedV2
export class UserPrefsModel {
  @Trace enqueueDownloaded: boolean = true;
  @Trace enqueueLocation: number = 1;
  @Trace playbackSpeed: number = 1.0;
  @Trace fastForwardSecs: number = 30;
  @Trace rewindSecs: number = 10;
  @Trace skipSilence: boolean = false;
  @Trace showRemainTime: boolean = false;
  @Trace streamOverDownload: boolean = false;
  @Trace useEpisodeCover: boolean = true;
}

// 文件: common/StorageKeys.ets — 统一 key 常量
export class StorageKeys {
  static readonly PLAYBACK = 'playback';
  static readonly UI_STATE = 'uiState';
  static readonly APP_STATE = 'appState';
  static readonly USER_PREFS = 'userPrefs';
}
```

```typescript
// 文件: common/GlobalState.ets — V2 简化版
import { AppStorageV2, PersistenceV2 } from '@kit.ArkUI';

export class GlobalState {
  private static initialized: boolean = false;
  private static appContext: Context | undefined = undefined;
  static filesDir: string = '';
  static cacheDir: string = '';
  static downloadDir: string = '';

  static getContext(): Context {
    if (GlobalState.appContext === undefined) {
      throw new Error('GlobalState not initialized');
    }
    return GlobalState.appContext;
  }

  static async init(context: Context): Promise<void> {
    if (GlobalState.initialized) {
      return;
    }
    GlobalState.appContext = context;
    GlobalState.filesDir = context.filesDir;
    GlobalState.cacheDir = context.cacheDir;
    GlobalState.downloadDir = context.filesDir + '/downloads';

    // 1. 预热 V2 全局模型（首次 connect 即创建实例；后续任意页面 connect 共享）
    AppStorageV2.connect(PlaybackModel, StorageKeys.PLAYBACK, () => new PlaybackModel());
    AppStorageV2.connect(UiStateModel, StorageKeys.UI_STATE, () => new UiStateModel());
    const appState = AppStorageV2.connect(AppStateModel, StorageKeys.APP_STATE, () => new AppStateModel())!;

    // 2. 偏好设置走 PersistenceV2：磁盘持久化 + UI 响应一站式
    PersistenceV2.globalConnect({
      type: UserPrefsModel,
      key: StorageKeys.USER_PREFS,
      defaultCreator: () => new UserPrefsModel()
    });

    // 3. 初始化数据库
    await PodDatabase.getInstance().init(context);

    // 4. 标记就绪 — 直接写 @Trace 字段，所有 connect 该 key 的组件自动刷新
    appState.dbReady = true;
    GlobalState.initialized = true;
  }
}
```

**V1 → V2 迁移要点**：

| V1 散点写法 | V2 聚合写法 |
|---|---|
| 25 个 `AppStorage.setOrCreate('isPlaying', false)` | 4 个 `@ObservedV2` 模型类 + 4 次 `AppStorageV2.connect` |
| 组件用 `@StorageLink('isPlaying') isPlaying: boolean = false` | 组件用 `@Local playback: PlaybackModel = AppStorageV2.connect(...)!`，访问 `this.playback.isPlaying` |
| 持久化需手动 sync `Preferences ↔ AppStorage` | `PersistenceV2.globalConnect` 一站式（不用再写 `syncToAppStorage`） |

---

## 3. 层依赖规则

```
pages → components → viewmodels → database + network
                                      ↑
                                    models
                                      ↑
common ← 所有层都可以引用
```

**具体规则**：

| 层 | 可以依赖 | 不可以依赖 |
|------|---------|----------|
| `pages/` | components, common, playback, network | database (通过 viewmodel 间接) |
| `components/` | viewmodels, common, playback, network | pages, 其他 components (除 common/) |
| `viewmodels/` | database, network, models, common | pages, components |
| `database/` | models, common | 其他层 |
| `network/` | models, database, parser, common | pages, components |
| `parser/` | models, common | 其他层 |
| `playback/` | database, models, common, network | pages, components |
| `models/` | common (Constants) | 其他层 |
| `common/` | 无依赖 | 任何层 |
| `datasource/` | models | 其他层 |
| `helpers/` | common | pages, components |
| `workers/` | network, common | pages, components |

---

## 4. 96 文件清单

按目录分类的完整文件列表（基于 AntennaPod ArkTS 项目）。

### common/ (5 文件)
```
AppRouter.ets        — 路由常量 + 参数类 (19 路由, 8 参数类)
Constants.ets        — 全局常量 (表名, 状态码, 排序方式)
EventBus.ets         — 发布/订阅事件总线 + 30 个事件常量
EventData.ets        — 事件数据类 (每个事件一个类)
GlobalState.ets      — 全局状态初始化 (25+ AppStorage key)
```

### models/ (8 文件)
```
Feed.ets             — 播客源模型 (id, title, url, imageUrl...)
FeedItem.ets         — 剧集模型 (id, title, pubDate, description...)
FeedMedia.ets        — 媒体模型 (duration, position, downloadUrl...)
FeedPreferences.ets  — 播客偏好 (skipIntro, skipEnding, speed...)
Chapter.ets          — 章节模型 (start, title, href, imageUrl)
FeedFunding.ets      — 资助链接模型 (url, content)
DownloadResult.ets   — 下载日志模型
PodcastSearchResult.ets — 搜索结果模型
TranscriptEntry.ets  — 字幕条目模型
```

### database/ (8 文件)
```
PodDatabase.ets      — 数据库单例 (init, getStore, 建表 SQL)
FeedDao.ets          — Feed CRUD
FeedItemDao.ets      — FeedItem CRUD (含 JOIN 查询)
FeedMediaDao.ets     — FeedMedia CRUD
QueueDao.ets         — 队列操作 (add, remove, reorder)
FavoritesDao.ets     — 收藏操作
ChapterDao.ets       — 章节操作
DownloadLogDao.ets   — 下载日志
```

### network/ (6 文件)
```
HttpClient.ets       — HTTP 封装 (get, getConditional, post)
NetworkUtils.ets     — 网络工具 (isNetworkAvailable)
FeedUpdateService.ets — Feed 刷新服务 (subscribe, refresh)
DownloadManager.ets  — 下载管理 (download, cancel, delete)
PodcastSearcher.ets  — 播客搜索 (iTunes API)
DefaultFeedInitializer.ets — 首次安装默认订阅
```

### parser/ (7 文件)
```
FeedParser.ets       — RSS/Atom 解析主入口
DateParser.ets       — 日期格式解析
OpmlParser.ets       — OPML 导入/导出
TranscriptParser.ets — 字幕解析
namespace/ItunesNamespace.ets  — iTunes 命名空间
namespace/MediaNamespace.ets   — Media RSS 命名空间
namespace/DublinCoreNamespace.ets — Dublin Core 命名空间
namespace/ContentNamespace.ets — Content 命名空间
namespace/PodcastIndexNamespace.ets — Podcast Index 命名空间
```

### playback/ (3 文件)
```
PlaybackController.ets       — 播放控制 (play, pause, seek, speed)
BackgroundPlaybackManager.ets — 后台播放 (ContinuousTask + AVSession)
SleepTimer.ets               — 睡眠定时器
```

### viewmodels/ (13 文件)
```
HomeViewModel.ets            — 首页数据
FeedDetailViewModel.ets      — Feed 详情
EpisodeDetailViewModel.ets   — 剧集详情
QueueViewModel.ets           — 队列管理
InboxViewModel.ets           — 收件箱
AllEpisodesViewModel.ets     — 全部剧集
SubscriptionViewModel.ets    — 订阅管理
DownloadsViewModel.ets       — 下载管理
SearchViewModel.ets          — 搜索
PlaybackHistoryViewModel.ets — 播放历史
StatisticsViewModel.ets      — 统计
OnlineFeedViewModel.ets      — 在线 Feed 预览
VideoPlayerViewModel.ets     — 视频播放
```

### components/ (20+ 文件)
```
home/HomeComponent.ets
home/HomeConfigureDialog.ets
queue/QueueComponent.ets
episodes/InboxComponent.ets
episodes/AllEpisodesComponent.ets
episodes/EpisodeDetailComponent.ets
episodes/DownloadsComponent.ets
subscription/SubscriptionComponent.ets
feed/FeedDetailComponent.ets
feed/FeedInfoComponent.ets
feed/FeedSettingsComponent.ets
search/SearchComponent.ets
discovery/AddFeedComponent.ets
discovery/OnlineFeedViewComponent.ets
playback/FullPlayerComponent.ets
playback/PlaybackHistoryComponent.ets
playback/VideoPlayerComponent.ets
preferences/SettingsComponent.ets
statistics/StatisticsComponent.ets
statistics/HalfCircleChart.ets
common/EmptyStateView.ets
common/EpisodeListItem.ets
common/FeedGridItem.ets
common/MoreComponent.ets
common/OpmlImportComponent.ets
common/SectionHeader.ets
common/SortDialog.ets
common/CustomizeNavigationDialog.ets
```

### 其他目录
```
pages/Index.ets                    — 应用主页 (@Entry)
datasource/FeedDataSource.ets      — Feed IDataSource (LazyForEach)
datasource/FeedItemDataSource.ets  — FeedItem IDataSource (LazyForEach)
entryability/EntryAbility.ets      — 应用入口 (UIAbility)
entrybackupability/EntryBackupAbility.ets — 备份能力
helpers/FileUtils.ets              — 文件工具
helpers/StringUtils.ets            — 字符串工具
helpers/JsonUtils.ets              — JSON 工具
helpers/PermissionHelper.ets       — 权限工具
helpers/UserPreferences.ets        — 用户偏好 (Preferences)
helpers/PlaybackPreferences.ets    — 播放偏好
helpers/SleepTimerPreferences.ets  — 睡眠定时偏好
helpers/SyncCredentials.ets        — 同步凭据
workers/FeedUpdateWorkAbility.ets  — workScheduler 任务
workers/FeedUpdateWorker.ets       — 刷新执行器
```
