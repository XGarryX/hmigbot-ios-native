# ArkTS V1 → V2 装饰器迁移规则

> 本文档是 **V1 → V2 装饰器迁移的完整规则与代码对照**，作为本项目锁 V2 后将老代码升级或验证升级正确性的参考。
>
> - V2 装饰器规则速查 → [`v2-decorator-rules.md`](./v2-decorator-rules.md)
> - V2 装饰器完整语法 → [`arkts-state-manager/references/v2-decorators.md`](../../arkts-state-manager/references/v2-decorators.md)
> - V1 装饰器历史参考 → [`arkts-state-manager/references/state-decorators.md`](../../arkts-state-manager/references/state-decorators.md)
> - 老 V1 项目升 API 12 的废弃 API 迁移 → [`migration-patterns.md`](./migration-patterns.md)

---

## 1. 13 类装饰器映射规则

| # | V1 装饰器 | V2 等价 | 迁移操作 | 是否结构性变化 |
|---|---|---|---|---|
| 1 | `@Component` | `@ComponentV2` | 改装饰器名 | 否（Edit 全替换） |
| 2 | `@State` | `@Local` | 改装饰器名 | 否（Edit 全替换） |
| 3 | `@Prop`（只读） | `@Param + @Once` | 改装饰器名 + 加 `@Once` | 否 |
| 3' | `@Prop`（可改） | `@Param`（不带 `@Once`） | 改装饰器名 | 否 |
| 4 | `@Link` | **没有直接等价** — `@Param + @Event` 回调 | 父子两端结构性改写 | **是** |
| 5 | `@Provide` | `@Provider()` | 改装饰器名 + 加括号 | 否 |
| 6 | `@Consume` | `@Consumer()` | 改装饰器名 + 加括号 + **必须给默认值** | 否 |
| 7 | `@Observed` | `@ObservedV2` | 改装饰器名 + 属性加 `@Trace` | 部分 |
| 8 | `@ObjectLink` | **取消** — `@Param` 直接持有 `@ObservedV2` 实例 | 删 `@ObjectLink` 改 `@Param` | 部分 |
| 9 | `@StorageLink('k')` | `@Local x = AppStorageV2.connect(Cls, 'k', () => new Cls())!` | 先抽 `@ObservedV2` 类 | **是** |
| 9' | `@StorageProp('k')` | 同上（只读：不写回 storage） | 同上 | **是** |
| 10 | `@LocalStorageLink / @LocalStorageProp` | `@Provider()/@Consumer()` 或页面根 `@Local`+`@Param`（无 LocalStorageV2） | 同上 | **是** |
| 11 | `PersistentStorage.persistProp` | `PersistenceV2.globalConnect({type, key, defaultCreator})` | 先抽 `@ObservedV2` 类 + 删 `AppStorage.set` 双层模式 | **是** |
| 12 | `@Watch('method')` | `@Monitor('prop') method(monitor: IMonitor): void` | 移装饰器到方法 + 改签名 | 部分 |
| 13 | `@Reusable` | `@ReusableV2` | 改装饰器名 | 否 |

> **通用不变**：`@Entry / @Builder / @BuilderParam / @Styles / @Extend` 在 V1/V2 都可用，无需迁移。

---

## 2. 简单装饰器（可 `replace_all` 批量替换）

以下装饰器的 V1→V2 是**纯字符串替换**，不需要结构性改动：

| 替换 | 命令示例（DevEco Studio 全局搜索替换） |
|---|---|
| `@Component` → `@ComponentV2` | 注意排除 `@ComponentV2` 自身（regex：`@Component\b`） |
| `@State ` → `@Local ` | （含尾随空格避免误匹配） |
| `@Observed\b` → `@ObservedV2` |  |
| `@Provide(` → `@Provider(`，`@Provide ` → `@Provider() ` | 注意带括号 |
| `@Consume(` → `@Consumer(`，`@Consume ` → `@Consumer() ` | 加默认值 |
| `@Watch` → `@Monitor`（仅装饰器名；签名仍需手改） |  |
| `@Reusable\b` → `@ReusableV2` |  |

> **不能简单替换**的装饰器：`@Link / @StorageLink / @StorageProp / @LocalStorageLink / @LocalStorageProp / @Prop / PersistentStorage.persistProp` — 见下文结构性改写。

---

## 3. 结构性改写示例

### 3.1 `@Link` → `@Param + @Event`

**V1 写法**：

```typescript
// 父
@Component
struct Parent {
  @State count: number = 0
  build() {
    Child({ count: $count })  // V1：$ 前缀传引用
  }
}

// 子
@Component
struct Child {
  @Link count: number
  build() {
    Button(`+1`).onClick(() => { this.count++ })
  }
}
```

**V2 写法**：

```typescript
// 父
@ComponentV2
struct Parent {
  @Local count: number = 0
  build() {
    Child({
      count: this.count,
      onCountChange: (v: number) => { this.count = v }
    })
  }
}

// 子
@ComponentV2
struct Child {
  @Param count: number = 0
  @Event onCountChange: (v: number) => void = () => {}

  build() {
    Button(`+1`).onClick(() => {
      this.onCountChange(this.count + 1)
    })
  }
}
```

**改写要点**：
- 子组件的 `@Link` → `@Param`（必须给默认值）+ 新增 `@Event onXxxChange`
- 子组件改值 → 通过 `this.onXxxChange(newValue)` 通知父
- 父组件 `$xxx` → `xxx: this.xxx`，新增 `onXxxChange: (v) => { this.xxx = v }`
- 命名约定：`on<PropertyName>Change`（驼峰 + 后缀 `Change`）

---

### 3.2 `@Prop`（只读 vs 可改）→ `@Param`

**V1**：

```typescript
@Component
struct ProgressBar {
  @Prop progress: number = 0   // V1：单向传递（API 12+ 必须初始化）
  @Prop label: string = '进度'
  build() {
    Text(`${this.label}: ${this.progress}%`)
  }
}
```

**V2 — 只读（推荐显式 `@Once`）**：

```typescript
@ComponentV2
struct ProgressBar {
  @Param @Once progress: number = 0   // 子组件不可改（编译期检查）
  @Param @Once label: string = '进度'
  build() {
    Text(`${this.label}: ${this.progress}%`)
  }
}
```

**V2 — 子组件需要本地编辑（不带 `@Once`）**：

```typescript
@ComponentV2
struct EditableInput {
  @Param value: string = ''   // 子可改本地副本，不回传父
  build() {
    TextInput({ text: this.value })
      .onChange((v) => { this.value = v })  // 仅修改本地
  }
}
```

**判定规则**：
- 默认 `@Once`（V2 推荐显式声明子组件不可改）
- 子组件需要绑定到 `TextInput / TextArea / Slider` 等可编辑控件 → 不带 `@Once`
- 需要双向同步父子 → 不用 `@Param`，改用 `@Param + @Event`（见 §3.1）

---

### 3.3 `@Observed + @ObjectLink` → `@ObservedV2 + @Trace + @Param`

**V1**：

```typescript
@Observed
class TaskItem {
  id: string = ''
  title: string = ''   // V1 默认观察整个对象第一层
  done: boolean = false
}

@Component
struct TaskList {
  @State tasks: TaskItem[] = []
  build() {
    ForEach(this.tasks, (item: TaskItem) => {
      TaskItemView({ task: item })
    }, (item: TaskItem) => item.id)
  }
}

@Component
struct TaskItemView {
  @ObjectLink task: TaskItem
  build() {
    Toggle({ type: ToggleType.Checkbox, isOn: this.task.done })
      .onChange((v: boolean) => { this.task.done = v })
  }
}
```

**V2**：

```typescript
@ObservedV2
class TaskItem {
  id: string = ''                // 不加 @Trace，变化不刷新（适合稳定 id）
  @Trace title: string = ''      // 加 @Trace，变化刷新
  @Trace done: boolean = false
}

@ComponentV2
struct TaskList {
  @Local tasks: TaskItem[] = []
  build() {
    Repeat<TaskItem>(this.tasks)
      .each((item: RepeatItem<TaskItem>) => {
        TaskItemView({ task: item.item })
      })
      .key((task) => task.id)
  }
}

@ComponentV2
struct TaskItemView {
  @Param task: TaskItem = new TaskItem()   // V2 直接 @Param 持有，无需 @ObjectLink
  build() {
    Toggle({ type: ToggleType.Checkbox, isOn: this.task.done })
      .onChange((v: boolean) => { this.task.done = v })   // @Trace 属性变化自动刷新
  }
}
```

**改写要点**：
- `@Observed` → `@ObservedV2`
- 类的可观察属性加 `@Trace`（不加 `@Trace` 的属性变化不刷新；适合稳定 id 字段）
- `@ObjectLink` → 删除，改用 `@Param`（必须给默认值，通常用 `new Cls()`）
- `ForEach` 可选改用 `Repeat`（V2 推荐，性能更好）

---

### 3.4 `@StorageLink / @StorageProp` → `AppStorageV2.connect`

**V1**（分散 key 模式）：

```typescript
@Component
struct PlaybackPage {
  @StorageLink('isPlaying') isPlaying: boolean = false
  @StorageLink('currentSpeed') speed: number = 1.0
  @StorageProp('trackTitle') title: string = ''   // 只读
}

// 必须在 EntryAbility.onCreate() 提前 setOrCreate
AppStorage.setOrCreate('isPlaying', false)
AppStorage.setOrCreate('currentSpeed', 1.0)
AppStorage.setOrCreate('trackTitle', '')
```

**V2**（合并 `@ObservedV2` 类 + connect）：

```typescript
// 1. 抽出可观察类
@ObservedV2
class PlaybackModel {
  @Trace isPlaying: boolean = false
  @Trace speed: number = 1.0
  @Trace title: string = ''
}

// 2. 任意组件中获取（首次 connect 自动用 defaultCreator 初始化，无需提前 setOrCreate）
@ComponentV2
struct PlaybackPage {
  @Local model: PlaybackModel = AppStorageV2.connect(
    PlaybackModel,
    'playback',
    () => new PlaybackModel()
  )!

  build() {
    Text(this.model.title)
    Button(this.model.isPlaying ? '暂停' : '播放')
      .onClick(() => {
        this.model.isPlaying = !this.model.isPlaying   // 自动同步到所有 connect 该 key 的组件
      })
  }
}
```

**改写要点**：
- 多个相关 `@StorageLink` key 合并为一个 `@ObservedV2` 类（每个 key 一个 `@Trace` 属性）
- `@StorageLink` → `@Local x = AppStorageV2.connect(Cls, 'k', () => new Cls())!`（注意末尾 `!`）
- `@StorageProp` 同上（V2 不区分读写：通过类属性的 `@Trace` 决定可观察，类似 V1 的"只读"语义需自行约定）
- 删除 `EntryAbility.onCreate()` 中的 `AppStorage.setOrCreate` 预热（V2 connect 自动初始化）
- 多组件 connect 同一 key 共享同一实例

---

### 3.5 `@LocalStorageLink / @LocalStorageProp` → `@Provider` / `@Consumer`（无 LocalStorageV2）

**不存在 `LocalStorageV2` 这个 API**（`import` 即报 `has no exported member 'LocalStorageV2'`）。页面树/子树范围共享改用 `@Provider`（祖先）/ `@Consumer`（后代，查找不到时用本地默认值），或页面根 `@Local` 持 `@ObservedV2` 实例并用 `@Param` 逐层下传。

```typescript
@ObservedV2
class PageState {
  @Trace counter: number = 0
}

@ComponentV2
struct MyPage {                       // 祖先：提供实例
  @Provider() state: PageState = new PageState()
}

@ComponentV2
struct ChildView {                    // 后代：同名消费
  @Consumer() state: PageState = new PageState()   // 查找不到 @Provider 时用此本地默认值
}
```

---

### 3.6 `PersistentStorage.persistProp` → `PersistenceV2.globalConnect`

**V1**（双层模式：PersistentStorage + AppStorage + @StorageLink）：

```typescript
// 启动时
PersistentStorage.persistProp('userToken', '')
PersistentStorage.persistProp('themeMode', 'light')

// 组件
@Component
struct AppRoot {
  @StorageLink('userToken') token: string = ''
  @StorageLink('themeMode') theme: string = 'light'
}
```

**V2**（一站式 globalConnect）：

```typescript
@ObservedV2
class AppGlobal {
  @Trace userToken: string = ''
  @Trace themeMode: string = 'light'
}

@ComponentV2
struct AppRoot {
  @Local global: AppGlobal = PersistenceV2.globalConnect({
    type: AppGlobal,
    key: 'app_global',
    defaultCreator: () => new AppGlobal()
  })!

  build() {
    Text(`Theme: ${this.global.themeMode}`)
    Button('Toggle Theme').onClick(() => {
      this.global.themeMode = this.global.themeMode === 'light' ? 'dark' : 'light'
      // 自动落盘 + UI 响应
    })
  }
}
```

**改写要点**：
- 删除 `PersistentStorage.persistProp` 启动调用
- 多个相关 persistProp key 合并为一个 `@ObservedV2` 类（属性加 `@Trace`）
- 改值自动落盘 + UI 响应，无需 `AppStorage.set` 同步两套存储

---

### 3.7 `@Watch('method')` → `@Monitor('prop')`

**V1**：

```typescript
@Component
struct SearchPage {
  @State @Watch('onKeywordChange') keyword: string = ''

  onKeywordChange(propName: string): void {
    this.performSearch(this.keyword)
  }
}
```

**V2**：

```typescript
@ComponentV2
struct SearchPage {
  @Local keyword: string = ''

  @Monitor('keyword')
  onKeywordChange(monitor: IMonitor): void {
    console.info('changed:', monitor.value<string>('keyword')?.now)
    this.performSearch(this.keyword)
  }

  // 多属性监听：@Monitor('a', 'b', 'c')
  // monitor.dirty 返回变化的属性名数组
}
```

**改写要点**：
- V1 是属性装饰器写在 `@State` 旁；V2 是**方法装饰器**写在方法上
- V1 回调签名 `(propName: string) => void`；V2 是 `(monitor: IMonitor) => void`
- V2 一个方法可监听多个属性：`@Monitor('a', 'b', 'c')`
- ⚠️ 不要在 `@Monitor` 回调中修改被监听的属性（会无限循环）

---

## 4. 完整迁移 Checklist

升级一个文件 / 一个 skill 时，逐项检查：

### 4.1 装饰器名替换

- [ ] 所有 `@Component` 改为 `@ComponentV2`（注意不要误改 `@ComponentV2`）
- [ ] 所有 `@State` 改为 `@Local`
- [ ] 所有 `@Observed` 改为 `@ObservedV2`，并给可观察属性加 `@Trace`
- [ ] 所有 `@Provide` 改为 `@Provider()`（带括号）
- [ ] 所有 `@Consume` 改为 `@Consumer()`（带括号 + **加默认值**）
- [ ] 所有 `@Watch` 改为 `@Monitor`（且移到方法上 + 改签名）
- [ ] 所有 `@Reusable` 改为 `@ReusableV2`

### 4.2 结构性改写

- [ ] 所有 `@Link` 改为 `@Param + @Event` 回调（父子两端配对改写）
- [ ] 所有 `@Prop` 改为 `@Param`（默认加 `@Once`，仅可编辑控件场景去掉 `@Once`）
- [ ] 所有 `@ObjectLink` 改为 `@Param`，并删除 `@ObjectLink`
- [ ] 所有 `@StorageLink / @StorageProp` 抽合并 `@ObservedV2` 类 + 改 `AppStorageV2.connect`
- [ ] 所有 `@LocalStorageLink / @LocalStorageProp` 改 `@Provider`/`@Consumer` 或页面根 `@Local`+`@Param`（无 LocalStorageV2）
- [ ] 所有 `PersistentStorage.persistProp` 改 `PersistenceV2.globalConnect`，并删除 V1 双层模式

### 4.3 V2 强制约束

- [ ] `@ComponentV2` 内不混入任何 V1 装饰器
- [ ] `@Param` 必须给默认值（V2 强制）
- [ ] `@Consumer()` 必须给默认值
- [ ] `@Provider() / @Consumer()` 必须带括号
- [ ] `@ObservedV2` 类的可观察属性加 `@Trace`
- [ ] `@Monitor` 回调签名带 `IMonitor` 参数

### 4.4 验证 grep

```bash
# V1 残留（应仅剩 references/v1-compat.md / references/state-decorators.md 等历史文档）
grep -rEI '@Component|@State|@Prop|@Link|@Provide|@Consume|@Observed|@ObjectLink|@StorageLink|@StorageProp|@LocalStorageLink|@LocalStorageProp|@Watch' <path> | \
  grep -vE '@ComponentV2|@ObservedV2|@Provider|@Consumer|StorageV2'

# V2 命中
grep -rEI '@ComponentV2|@ObservedV2|@Local|@Param|@Once|@Provider|@Consumer|@Monitor|@Computed|AppStorageV2|PersistenceV2|@Trace' <path>
```

---

## 5. 与 [`migration-patterns.md`](./migration-patterns.md) 的关系

| 文档 | 内容 | 适用场景 |
|---|---|---|
| `migration-patterns.md` | `@ohos→@kit` 导入迁移、router→Navigation、V1 `@Prop` 初始化、V1 `@Link` `$` 前缀去除 | 老 V1 项目升 API 12（仍是 V1） |
| `v2-migration-patterns.md`（本文档） | V1 装饰器→V2 装饰器映射 + 结构性改写 | V1 项目升 V2（本项目锁 V2 后必读） |

升级路径建议：
1. 先用 `migration-patterns.md` 升导入和导航到 API 12 基线
2. 再用本文档升装饰器到 V2

---

## 6. 跨文档参考

- [`v2-decorator-rules.md`](./v2-decorator-rules.md) — V2 装饰器规则速查
- [`api12-baseline.md`](./api12-baseline.md) — API 12 基线
- [`arkts-state-manager/references/v2-decorators.md`](../../arkts-state-manager/references/v2-decorators.md) — V2 装饰器完整语法
- [`arkts-state-manager/references/v2-global-state.md`](../../arkts-state-manager/references/v2-global-state.md) — V2 存储 API 模板
- [`arkts-state-manager/references/state-decorators.md`](../../arkts-state-manager/references/state-decorators.md) — V1 装饰器历史参考（legacy）
- [`arkts-architecture-refactor/references/v2-migration-playbook.md`](../../arkts-architecture-refactor/references/v2-migration-playbook.md) — 重构层面的 V1→V2 迁移手册
