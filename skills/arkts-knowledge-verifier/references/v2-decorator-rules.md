# ArkTS V2 装饰器规则速查

> 本文档是 **V2 装饰器规则速查**（项目锁 V2 主参考）。要求 **API 12+（HarmonyOS 5.0.0+）**。
>
> - 完整 V2 语法/边界 → [`arkts-state-manager/references/v2-decorators.md`](../../arkts-state-manager/references/v2-decorators.md)
> - V1 → V2 迁移规则 → [`v2-migration-patterns.md`](./v2-migration-patterns.md)
> - V1 装饰器历史参考（legacy） → [`arkts-state-manager/references/state-decorators.md`](../../arkts-state-manager/references/state-decorators.md)

---

## 1. V2 装饰器全集

### 组件层

| 装饰器 | 用途 | 必须配合 | 禁止混用 |
|---|---|---|---|
| `@ComponentV2` | 标记 V2 组件 struct | `struct ...` | 任何 V1 装饰器（`@State / @Prop / @Link / @Watch / @Provide / @Consume / @Observed / @ObjectLink / @StorageLink ...`） |
| `@Entry` | 标记入口页（V1/V2 通用） | `@ComponentV2` 或 `@Component` | — |
| `@ReusableV2` | 标记可复用组件（API 12+） | `@ComponentV2` | `@Reusable`（V1） |

### 状态层

| 装饰器 | 数据流方向 | 默认值 | 替代的 V1 |
|---|---|---|---|
| `@Local` | 组件内部 | 必须初始化 | `@State` |
| `@Param` | 父→子（可改本地副本，不回传） | 必须初始化 | `@Prop`（可改语义） |
| `@Param + @Once` | 父→子单向只读（子不可改） | 必须初始化 | `@Prop`（只读语义） |
| `@Event` | 子→父事件回调（替代双向） | 必须给默认实现 | （V1 用 `@Link` 实现双向） |
| `@Provider()` | 祖先→后代（必须带括号） | 初始化 | `@Provide` |
| `@Consumer()` | 后代消费祖先（必须带括号 + 默认值） | **必须给默认值** | `@Consume`（不要求默认值） |

### 类层（可观察类）

| 装饰器 | 用途 | 替代的 V1 |
|---|---|---|
| `@ObservedV2` | 类装饰器，标记可观察类 | `@Observed` |
| `@Trace` | 类属性装饰器，标记需观察的属性（精确属性级） | `@Track`（V1 API 12+） |

### 响应/计算层

| 装饰器 | 用途 | 签名要求 | 替代的 V1 |
|---|---|---|---|
| `@Monitor('prop')` | 方法装饰器，监听 1 个或多个属性变化 | `method(monitor: IMonitor): void` | `@Watch('method')`（V1 是属性装饰器） |
| `@Computed` | getter 装饰器，缓存派生值（依赖追踪） | `get name(): T { return ... }` | （V1 无对应物） |

### 全局/持久化存储 API

| API | 用途 | 替代的 V1 |
|---|---|---|
| `AppStorageV2.connect(Cls, key, () => new Cls())` | 全局共享 | `@StorageLink('key') / @StorageProp('key')` |
| `@Provider()/@Consumer()` 或页面根 `@Local`+`@Param`（无 LocalStorageV2） | 单 LocalStorage 共享 | `@LocalStorageLink / @LocalStorageProp` |
| `PersistenceV2.globalConnect({type, key, defaultCreator})` | 持久化 + 响应式 | `PersistentStorage.persistProp` |

> V2 全局/持久化必须先定义 `@ObservedV2` 类（属性加 `@Trace`）。

### 通用（V1/V2 都可用）

`@Builder / @BuilderParam / @Styles / @Extend / @LocalBuilder` —— 这些装饰器在 V1/V2 都可用，无需迁移。
注意：`@LocalBuilder` 在 V2 中常用于在 `@ComponentV2` 内部定义 builder 段。

---

## 2. 关键规则

### 2.1 `@ComponentV2` 内禁止 V1 装饰器

```typescript
// ❌ 编译错误：V1/V2 mixed usage
@ComponentV2
struct Page {
  @State count: number = 0      // V1 @State 不能用在 @ComponentV2
  @Prop title: string = ''       // V1 @Prop 同理
  @Link active: boolean          // V1 @Link 同理
  @Watch('onCountChange')         // V1 @Watch 同理
  count2: number = 0
}

// ✅ V2 全套
@ComponentV2
struct Page {
  @Local count: number = 0
  @Param @Once title: string = ''
  @Param active: boolean = false
  @Event onActiveChange: (v: boolean) => void = () => {}

  @Monitor('count')
  onCountChange(monitor: IMonitor): void { /* ... */ }
}
```

### 2.2 `@Param` 必须初始化（V2 强制）

```typescript
// ❌ 编译错误
@Param title: string

// ✅
@Param title: string = ''
@Param @Once count: number = 0
@Param items: Item[] = []
@Param user: UserModel = new UserModel()
```

### 2.3 `@Provider() / @Consumer()` 必须带括号 + `@Consumer` 必须给默认值

```typescript
// ❌
@Provider theme: string = 'light'        // 缺括号
@Consumer() theme: string                 // 缺默认值

// ✅
@Provider() theme: string = 'light'
@Consumer() theme: string = 'light'       // 找不到匹配 Provider 时使用此默认值
```

### 2.4 `@Monitor` 是方法装饰器（与 V1 `@Watch` 不同）

```typescript
// V1（不在 V2 项目中使用）
@State count: number = 0
@Watch('onCountChange')

// V2
@Local count: number = 0

@Monitor('count')
onCountChange(monitor: IMonitor): void {
  console.info('changed:', monitor.value<number>('count')?.now)
  // ⚠️ 不要在此修改被监听的属性，避免无限循环
}

// 多属性监听
@Monitor('a', 'b', 'c')
onAnyChange(monitor: IMonitor): void {
  monitor.dirty.forEach(name => { /* ... */ })
}
```

### 2.5 `@ObservedV2` 类的属性必须加 `@Trace` 才会触发 UI 刷新

```typescript
@ObservedV2
class User {
  id: string = ''                 // 不加 @Trace，变化不刷新（适合稳定 id）
  @Trace name: string = ''        // ✅ 加 @Trace，变化刷新
  @Trace address: Address = new Address()  // 嵌套 @ObservedV2 类
}

@ObservedV2
class Address {
  @Trace city: string = ''
}
```

### 2.6 V2 取消 `@ObjectLink`：直接用 `@Param` 持有 `@ObservedV2` 实例

```typescript
// V1（不在 V2 项目中使用）
@Observed class Item { name: string = '' }
@Component struct ItemView { @ObjectLink item: Item }

// V2
@ObservedV2 class Item { @Trace name: string = '' }
@ComponentV2 struct ItemView {
  @Param item: Item = new Item()    // V2 直接 @Param 持有，不再用 @ObjectLink
}
```

### 2.7 V2 `@Param + @Event` 替代 V1 `@Link`

```typescript
// V1（不在 V2 项目中使用）
@Component struct Switch { @Link isOn: boolean }
// 父：Switch({ isOn: $isOn })

// V2
@ComponentV2 struct Switch {
  @Param isOn: boolean = false
  @Event onIsOnChange: (v: boolean) => void = () => {}

  build() {
    Toggle({ type: ToggleType.Switch, isOn: this.isOn })
      .onChange((v) => { this.onIsOnChange(v) })
  }
}

// 父
@ComponentV2 struct Parent {
  @Local isOn: boolean = false
  build() {
    Switch({
      isOn: this.isOn,
      onIsOnChange: (v) => { this.isOn = v }
    })
  }
}
```

### 2.8 V2 全局状态：`AppStorageV2.connect` + `@ObservedV2` 类

```typescript
// 1. 定义可观察类
@ObservedV2
class UserModel {
  @Trace isLoggedIn: boolean = false
  @Trace userName: string = ''
}

// 2. 任意组件中获取（首次 connect 自动用 defaultCreator 初始化）
@ComponentV2
struct ProfilePage {
  @Local user: UserModel = AppStorageV2.connect(
    UserModel,
    'user',
    () => new UserModel()
  )!

  build() {
    Text('Welcome, ' + this.user.userName)
  }
}
```

### 2.9 V2 持久化：`PersistenceV2.globalConnect`（一站式）

```typescript
@ObservedV2
class AppConfig {
  @Trace theme: string = 'light'
  @Trace fontSize: number = 14
}

@ComponentV2
struct SettingsPage {
  @Local config: AppConfig = PersistenceV2.globalConnect({
    type: AppConfig,
    key: 'app_config',
    defaultCreator: () => new AppConfig()
  })!

  build() {
    Text(`Theme: ${this.config.theme}`)
    Button('Toggle')
      .onClick(() => {
        this.config.theme = this.config.theme === 'light' ? 'dark' : 'light'
        // 自动落盘 + UI 响应（无需 V1 双层模式）
      })
  }
}
```

### 2.10 V2 派生值缓存：`@Computed`（V1 无）

```typescript
@ComponentV2
struct Cart {
  @Local items: Item[] = []

  @Computed
  get totalPrice(): number {
    return this.items.reduce((s, i) => s + i.price * i.count, 0)
    // 仅 items / item.price / item.count 变化时重新计算，否则返回缓存值
  }

  build() {
    Text(`总价: ${this.totalPrice}`)
    Text(`总价（再读）: ${this.totalPrice}`)  // 多次读取只计算一次
  }
}
```

---

## 3. V2 vs V1 速查表（一行版）

| 用途 | V2（推荐） | V1（legacy） |
|---|---|---|
| 组件 struct | `@ComponentV2` | `@Component` |
| 组件内部状态 | `@Local` | `@State` |
| 父→子单向只读 | `@Param + @Once` | `@Prop` |
| 父→子单向可改 | `@Param`（无 @Once） | `@Prop` |
| 父↔子双向 | `@Param + @Event` 回调 | `@Link`（V2 已无） |
| 跨层级 | `@Provider() / @Consumer()` | `@Provide / @Consume` |
| 可观察类 | `@ObservedV2` + 属性加 `@Trace` | `@Observed`（默认观察整体或配合 `@Track` 过滤） |
| 持有类实例 | `@Param`（V2 取消 `@ObjectLink`） | `@ObjectLink` |
| 全局状态 | `AppStorageV2.connect(Cls, k, () => new Cls())` | `@StorageLink('k') / @StorageProp('k')` |
| LocalStorage | `@Provider()/@Consumer()` 或页面根 `@Local`+`@Param`（无 LocalStorageV2） | `@LocalStorageLink / @LocalStorageProp` |
| 持久化 | `PersistenceV2.globalConnect({type, key, defaultCreator})` | `PersistentStorage.persistProp` |
| 监听变化 | `@Monitor('p') method(m: IMonitor): void` | `@Watch('method') @State p` |
| 派生值缓存 | `@Computed get name(): T` | （V1 无） |
| 组件复用 | `@ReusableV2` | `@Reusable` |

---

## 4. V2 装饰器存在性 / 合法性判定（FAQ）

> **Q**：`@State` 在 V2 项目中合法吗？
> **A**：不合法。`@State` 是 V1 装饰器。`@ComponentV2` 内不允许任何 V1 装饰器。请用 `@Local`。

> **Q**：`@Param` 不带 `@Once` 子组件能改吗？
> **A**：能改本地副本，但不会回传父组件；父组件更新时会覆盖子组件的本地修改。要双向同步用 `@Param + @Event`。

> **Q**：`@Computed` 可以是普通方法吗？
> **A**：不可以。`@Computed` 必须装饰 getter（`get name(): T { return ... }`），普通方法没有缓存语义。

> **Q**：`@Trace` 可以装饰非 `@ObservedV2` 类的属性吗？
> **A**：不可以。`@Trace` 只在 `@ObservedV2` 类内有效。

> **Q**：V2 还能用 `@Builder / @Styles / @Extend` 吗？
> **A**：能。这些装饰器在 V1/V2 都可用，无需迁移。`@LocalBuilder` 推荐在 `@ComponentV2` 内使用。

> **Q**：`AppStorageV2.connect` 第一次调用没拿到值怎么办？
> **A**：第一次 connect 时框架会自动用 `defaultCreator` 创建实例。无需在 `EntryAbility.onCreate()` 提前 `setOrCreate`（V1 模式）。

> **Q**：V1 项目能逐步迁移到 V2 吗？
> **A**：可以。同一项目内不同文件可以分别使用 V1 / V2，但**单个文件 / 单个 `@ComponentV2` 内**不能混用。建议按文件粒度分批迁移，参阅 `v2-migration-patterns.md`。

---

## 5. 跨文档参考

- [`v2-migration-patterns.md`](./v2-migration-patterns.md) — V1→V2 装饰器迁移完整规则
- [`api12-baseline.md`](./api12-baseline.md) — API 12 基线（导入、装饰器规则历史背景、导航）
- [`arkts-vs-typescript.md`](./arkts-vs-typescript.md) — ArkTS 与 TypeScript 差异（含 V2 装饰器示例）
- [`arkts-state-manager/references/v2-decorators.md`](../../arkts-state-manager/references/v2-decorators.md) — V2 装饰器完整语法与边界（主参考）
- [`arkts-state-manager/references/v2-global-state.md`](../../arkts-state-manager/references/v2-global-state.md) — `AppStorageV2 / PersistenceV2` 完整模板
- [`arkts-state-manager/references/state-decorators.md`](../../arkts-state-manager/references/state-decorators.md) — V1 装饰器历史参考（legacy）
