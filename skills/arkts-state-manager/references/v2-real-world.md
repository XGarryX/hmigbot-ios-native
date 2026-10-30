# V2 实战状态管理模式

> 基于真实应用（如 AntennaPod ArkTS）实战总结的 5 种 V2 状态管理模式：GlobalState 类、PersistenceV2 持久化、PlaybackController 绑定、EventBus 联动、@Provider/@Consumer 跨页。**本项目锁 V2**。V1 版本查阅请见 [`real-world-state-patterns.md`](./real-world-state-patterns.md)。

---

## 模式 1：GlobalState 作为 @ObservedV2 类（替代 V1 散 key）

V1 时代 `GlobalState.init()` 通过 `AppStorage.setOrCreate('key', val)` 注册 25+ 个 key，组件用 `@StorageLink('key')` 绑定。问题：key 散落、拼写易错、无类型保护。

V2 推荐**单一 `@ObservedV2` 类封装所有全局状态**：

```typescript
// common/GlobalState.ets
@ObservedV2
export class GlobalState {
  // 用户态
  @Trace isLoggedIn: boolean = false
  @Trace userId: string = ''
  @Trace userName: string = ''

  // 播放态
  @Trace isPlaying: boolean = false
  @Trace currentEpisodeId: string = ''
  @Trace playbackPosition: number = 0

  // UI 偏好
  @Trace viewType: string = 'list'
  @Trace sortOrder: string = 'asc'
  @Trace showHidden: boolean = false

  // 网络/系统
  @Trace isOnline: boolean = true
  @Trace networkType: string = 'wifi'

  // ... 其他 15+ 个字段
}

// 全局单例（应用启动时 connect 一次）
export const globalState = AppStorageV2.connect(
  GlobalState,
  'global_state',
  () => new GlobalState()
)!
```

### 在组件中使用

```typescript
import { globalState, GlobalState } from '../common/GlobalState'

@ComponentV2
struct PlayerBar {
  @Local g: GlobalState = globalState  // 直接引用全局实例

  build() {
    Row() {
      Text(this.g.isPlaying ? '⏸' : '▶')
        .onClick(() => { this.g.isPlaying = !this.g.isPlaying })  // 自动同步所有引用
      Text(this.g.userName)
    }
  }
}
```

### 与 V1 GlobalState.init() 的对比

| 维度 | V1 | V2 |
|---|---|---|
| 注册时机 | `Index.aboutToAppear` 里 25+ 行 `setOrCreate` | 直接定义类，第一次 `connect` 时自动初始化 |
| 类型安全 | 无（key 是字符串、value 是 Object） | 有（类属性强类型） |
| key 拼写错误 | 易（`@StorageLink('isLoggdIn')` 静默失效） | 不可能（属性是字段，编译期检查） |
| 字段加减 | 同时改 init() 和组件多处 | 改类定义即可 |
| 跨组件刷新 | `@StorageLink` 单字段 | `@Local g: GlobalState` 引用整个实例，按需读字段 |

---

## 模式 2：PersistenceV2 一站式持久化（替代 V1 双层模式）

V1 双层模式：`AppStorage`（UI 响应）+ `Preferences`（磁盘）+ 手动同步代码。

V2 一站式：`PersistenceV2.globalConnect` 同时承担两者。

```typescript
// helpers/UserPreferences.ets
@ObservedV2
export class UserPreferences {
  @Trace theme: string = 'light'
  @Trace fontSize: number = 14
  @Trace autoPlayNext: boolean = true
  @Trace downloadOverWifi: boolean = true
  @Trace skipIntroSeconds: number = 30
  @Trace skipOutroSeconds: number = 15
  @Trace playbackSpeed: number = 1.0
}

// 全局单例
export const userPrefs = PersistenceV2.globalConnect({
  type: UserPreferences,
  key: 'user_prefs',
  defaultCreator: () => new UserPreferences()
})!
```

### 设置页直接绑定，无需手动同步

```typescript
import { userPrefs, UserPreferences } from '../helpers/UserPreferences'

@ComponentV2
struct SettingsPage {
  @Local prefs: UserPreferences = userPrefs

  build() {
    Column() {
      // 主题切换
      Row() {
        Text('深色模式')
        Toggle({ type: ToggleType.Switch, isOn: this.prefs.theme === 'dark' })
          .onChange((isDark) => {
            this.prefs.theme = isDark ? 'dark' : 'light'  // ✓ 自动落盘
          })
      }

      // 字号
      Row() {
        Text(`字号: ${this.prefs.fontSize}`)
        Slider({ value: this.prefs.fontSize, min: 12, max: 24 })
          .onChange((v) => { this.prefs.fontSize = v })  // ✓ 自动落盘
      }

      // 播放速度
      Row() {
        Text(`速度: ${this.prefs.playbackSpeed}x`)
        Button('+').onClick(() => {
          this.prefs.playbackSpeed = Math.min(2.0, this.prefs.playbackSpeed + 0.25)
        })
      }
    }
  }
}
```

### 错误监听

```typescript
// 应用启动时注册一次
PersistenceV2.notifyOnError((key, reason, message) => {
  console.error(`Persistence error key=${key}: ${reason} - ${message}`)
  // 可选：上报埋点
})
```

---

## 模式 3：PlaybackController 绑定到 GlobalState

播放控制器是单例，状态需要在多个 UI 位置（迷你播放栏、全屏播放页、通知栏控件）同步显示。

```typescript
// playback/PlaybackController.ets
import { globalState, GlobalState } from '../common/GlobalState'

@ObservedV2
export class PlaybackController {
  @Trace isPlaying: boolean = false
  @Trace currentEpisodeId: string = ''
  @Trace position: number = 0
  @Trace duration: number = 0

  private g: GlobalState = globalState  // 持有 GlobalState 引用

  // 播放/暂停
  togglePlay(): void {
    this.isPlaying = !this.isPlaying
    this.g.isPlaying = this.isPlaying  // 同步到 GlobalState
    // 调用底层 AVPlayer ...
  }

  // 加载新 episode
  loadEpisode(episodeId: string): void {
    this.currentEpisodeId = episodeId
    this.g.currentEpisodeId = episodeId
    this.position = 0
    this.g.playbackPosition = 0
    // 调用底层 AVPlayer ...
  }

  // 进度更新（由 AVPlayer 回调驱动）
  onProgress(positionMs: number): void {
    this.position = positionMs
    this.g.playbackPosition = positionMs  // 同步到 GlobalState
  }
}

// 全局单例
export const playbackController = AppStorageV2.connect(
  PlaybackController,
  'playback_controller',
  () => new PlaybackController()
)!
```

### UI 中绑定

```typescript
@ComponentV2
struct MiniPlayerBar {
  @Local pc: PlaybackController = playbackController

  build() {
    Row() {
      Text(this.pc.isPlaying ? '⏸' : '▶')
        .onClick(() => { this.pc.togglePlay() })
      Progress({ value: this.pc.position, total: this.pc.duration })
      Text(this.pc.currentEpisodeId)
    }
  }
}

@ComponentV2
struct FullScreenPlayer {
  @Local pc: PlaybackController = playbackController  // 同一实例

  build() {
    // 自动与 MiniPlayerBar 保持同步
  }
}
```

---

## 模式 4：EventBus 联动（与状态管理正交）

业务事件（如"刷新订阅列表"、"网络恢复"）适合用 EventBus 模式而非 GlobalState。

EventBus 与状态装饰器解耦——它**不持有数据**，只发事件，监听者自己更新本地 `@Local`：

```typescript
// common/EventBus.ets
type Listener<T> = (data: T) => void

class EventBus {
  private listeners: Map<string, Set<Function>> = new Map()

  on<T>(event: string, listener: Listener<T>): void {
    if (!this.listeners.has(event)) this.listeners.set(event, new Set())
    this.listeners.get(event)!.add(listener)
  }

  off<T>(event: string, listener: Listener<T>): void {
    this.listeners.get(event)?.delete(listener)
  }

  emit<T>(event: string, data: T): void {
    this.listeners.get(event)?.forEach(l => (l as Listener<T>)(data))
  }
}

export const eventBus = new EventBus()

export const Events = {
  SUBSCRIPTION_REFRESHED: 'subscription_refreshed',
  NETWORK_RESTORED: 'network_restored',
  EPISODE_DOWNLOADED: 'episode_downloaded',
} as const
```

### 在组件中订阅

```typescript
import { eventBus, Events } from '../common/EventBus'

@ComponentV2
struct SubscriptionList {
  @Local items: Subscription[] = []

  private onRefreshed = (newList: Subscription[]) => {
    this.items = newList  // 触发 UI 刷新
  }

  aboutToAppear() {
    eventBus.on(Events.SUBSCRIPTION_REFRESHED, this.onRefreshed)
  }

  aboutToDisappear() {
    eventBus.off(Events.SUBSCRIPTION_REFRESHED, this.onRefreshed)
  }

  build() {
    List() {
      ForEach(this.items, (item: Subscription) => {
        ListItem() { Text(item.title) }
      })
    }
  }
}
```

### 何时用 EventBus vs GlobalState

| 性质 | 用 |
|---|---|
| 持续状态（"当前是否登录"） | GlobalState（@ObservedV2 类） |
| 一次性事件（"刚刚下载完成"） | EventBus |
| 需要历史（最近 N 次事件） | 自建 ring buffer + GlobalState |
| 跨进程（前后台） | EmitterAPI / commonEventManager |

---

## 模式 5：@Provider / @Consumer 跨页主题/语言注入

主题、语言、用户角色等需要"应用所有页面都能感知"的全局设定，可用 `@Provider / @Consumer` 替代 GlobalState：

```typescript
// 应用根
@Entry
@ComponentV2
struct App {
  @Provider() theme: string = 'light'
  @Provider() locale: string = 'zh-CN'

  build() {
    Navigator() {
      // 任意深度的子页面都能 @Consumer 拿到
    }
  }
}

// 任意子页面/组件
@ComponentV2
struct AnyDeepComponent {
  @Consumer() theme: string = 'light'    // 必须给默认值
  @Consumer() locale: string = 'zh-CN'

  build() {
    Text(this.locale === 'zh-CN' ? '你好' : 'Hello')
      .fontColor(this.theme === 'dark' ? '#FFF' : '#000')
  }
}
```

### Provider/Consumer vs GlobalState 抉择

| 场景 | 选 |
|---|---|
| 静态注入（主题、语言、用户角色） | `@Provider/@Consumer` |
| 高频读写、需要类型安全的全局态 | GlobalState (`@ObservedV2` + `AppStorageV2`) |
| 跨 UIAbility / 跨进程 | 持久化 + IPC，再灌到 GlobalState |

---

## 实战案例：完整启动链

```typescript
// EntryAbility.ets
import { AppStorageV2, PersistenceV2 } from '@kit.ArkUI'
import { GlobalState, globalState } from './common/GlobalState'
import { UserPreferences, userPrefs } from './helpers/UserPreferences'
import { PlaybackController, playbackController } from './playback/PlaybackController'

export default class EntryAbility extends UIAbility {
  onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void {
    // 1. 注册持久化错误监听
    PersistenceV2.notifyOnError((key, reason, message) => {
      console.error(`Persistence error: ${key}: ${reason} - ${message}`)
    })

    // 2. 触发全局单例的 connect（实例已在模块顶层创建，此处仅确认初始化时机）
    console.info('GlobalState ready, isLoggedIn=', globalState.isLoggedIn)
    console.info('UserPrefs ready, theme=', userPrefs.theme)
    console.info('PlaybackController ready')

    // 3. 应用网络/电量监听并写入 GlobalState
    this.observeNetwork(globalState)
  }

  private observeNetwork(g: GlobalState): void {
    // ConnectivityManager 监听 ...
    // 状态变化时直接写 g.isOnline = ...
  }
}
```

---

## 跨文档参考

- [`v2-decorators.md`](./v2-decorators.md) — 装饰器完整语法
- [`v2-update-patterns.md`](./v2-update-patterns.md) — 数据更新模式
- [`v2-global-state.md`](./v2-global-state.md) — `AppStorageV2 / PersistenceV2` API 完整说明（V2 无 LocalStorageV2）
- [`SKILL.md`](../SKILL.md) — 决策树与陷阱总览
