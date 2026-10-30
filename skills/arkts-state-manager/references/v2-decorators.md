# ArkTS V2 状态管理装饰器完整参考

> 本文档覆盖 ArkTS V2（API 12+ 推荐）全部状态相关装饰器的语法、规则与完整示例。**本项目锁 V2**，本文档为主参考。V1 装饰器查阅请见 [`state-decorators.md`](./state-decorators.md)。

---

## 目录

1. [@ComponentV2](#1-componentv2)
2. [@Local](#2-local)
3. [@Param + @Once](#3-param--once)
4. [@Event](#4-event)
5. [@Provider / @Consumer](#5-provider--consumer)
6. [@ObservedV2 + @Trace](#6-observedv2--trace)
7. [@Monitor](#7-monitor)
8. [@Computed](#8-computed)
9. [@ReusableV2](#9-reusablev2-api-12)
10. [V2 vs V1 速查表](#10-v2-vs-v1-速查表)

---

## 1. @ComponentV2

### 语法规则

```typescript
@ComponentV2
struct MyComponent {
  build() { ... }
}
```

- **替代 V1 `@Component`**：所有使用 V2 状态装饰器（`@Local / @Param / @Event / ...`）的 struct 必须用 `@ComponentV2`
- **不可与 V1 装饰器混用**：`@ComponentV2` 内禁止出现 `@State / @Prop / @Link / @Provide / @Consume / @Watch`
- 仍可与 `@Entry / @Builder / @BuilderParam / @Styles / @Extend` 配合使用

### 完整示例

```typescript
@Entry
@ComponentV2
struct HomePage {
  @Local title: string = 'Home'

  build() {
    Column() {
      Text(this.title)
    }
  }
}
```

---

## 2. @Local

### 语法规则

```
@Local 变量名: 类型 = 初始值;
```

- **必须初始化**：声明时必须赋初始值
- **私有性**：仅组件内部可访问
- **替代 V1 `@State`**：语义和触发条件相同
- **支持的类型**：`number / string / boolean / enum / Array / Map / Set / Date / @ObservedV2 类实例`
- **触发刷新**：
  - 简单类型：值变化即刷新
  - `@ObservedV2` 实例：实例引用替换 OR 实例的 `@Trace` 属性变化
  - 数组（V2 内置 Proxy）：`push / pop / splice / shift / unshift / 下标赋值` 都触发刷新；整体重新赋值也可
  - Map/Set：`set / delete / clear` 触发刷新
  - Date：`setFullYear / setMonth / ...` 触发刷新

### 完整示例

```typescript
@ObservedV2
class TaskItem {
  @Trace title: string = ''
  @Trace done: boolean = false
}

@ComponentV2
struct TodoPage {
  // 简单类型
  @Local count: number = 0
  // @ObservedV2 类实例
  @Local task: TaskItem = new TaskItem()
  // 数组
  @Local tags: string[] = ['ArkTS', 'HarmonyOS']

  build() {
    Column({ space: 12 }) {
      Text(`Count: ${this.count}`)
      Button('+1').onClick(() => { this.count++ })

      Text(`Task: ${this.task.title}`)
      Button('改名').onClick(() => { this.task.title = '新任务' })

      Text(`Tags: ${this.tags.join(', ')}`)
      Button('加标签').onClick(() => { this.tags.push('OpenHarmony') })
    }
  }
}
```

---

## 3. @Param + @Once

### 语法规则

```typescript
// 单向只读（推荐）
@Param @Once 变量名: 类型 = 默认值

// 单向可改（子可改本地副本，不回传父）
@Param 变量名: 类型 = 默认值
```

- **必须有默认值**（V2 强制，与 V1 `@Prop` API 12+ 行为一致）
- **替代 V1 `@Prop`**：单向数据流的父→子传值
- **`@Once` 标记**：声明子组件不可修改该值（编译期检查）
- **不带 `@Once`**：子组件可读写本地副本（不回传父，父更新时覆盖）

### 完整示例

```typescript
// 子组件：只读 Param
@ComponentV2
struct ProgressBar {
  @Param @Once progress: number = 0  // 子不可改
  @Param @Once label: string = '进度'

  build() {
    Column() {
      Text(`${this.label}: ${this.progress}%`)
      Progress({ value: this.progress, total: 100 })
    }
  }
}

// 父组件
@ComponentV2
struct Parent {
  @Local progress: number = 50

  build() {
    Column() {
      ProgressBar({ progress: this.progress, label: '加载' })
      Button('+10').onClick(() => { this.progress += 10 })
    }
  }
}
```

### 何时用 @Once vs 不用

| 场景 | 推荐写法 |
|---|---|
| 配置项 / 显示值（子不应修改） | `@Param @Once value: T = default` |
| 子组件需要本地编辑（如 TextInput 的 text） | `@Param value: T = default`（无 @Once） |
| 双向同步（子改要回传父） | `@Param + @Event onValueChange`（见下节） |

---

## 4. @Event

### 语法规则

```typescript
@Event eventName: (param: T) => ReturnType = () => default
```

- **必须给默认实现**：通常是 no-op `() => {}` 或 `() => default`
- **替代 V1 `@Link` 双向同步**：父子单向 + 事件回调，组合实现双向语义
- 命名约定：`on<Property>Change` / `onClick` / `onConfirm` 等

### !! 双向绑定语法糖（V2 最简双向写法，API 12+）

父子双向同步可用 `!!` 语法糖一行搞定，但**对 @Event 命名有强制契约**：

- 子组件：`@Param value: T = default` + `@Event $value: (v: T) => void = () => {}`——**事件名必须是 `$` + 受控属性名**（属性 `value` → 事件 `$value`）。子组件回写调用 `this.$value(newVal)`。
- 父组件：`Child({ value: this.value!! })`——`this.value!!` 是语法糖，等价于 `Child({ value: this.value, $value: (v: T) => { this.value = v } })`。
- ⚠️ 用了 `!!` 就**不要再显式传 `$value`**（API 18+ 会编译报错）；`!!` **不支持多层父子传递**；`!!!`（3 个及以上感叹号）无双向效果。
- 若事件名用 `onValueChange` 这类任意名（手工回写），父组件就**不能**用 `this.value!!`，只能 `Child({ value: this.value, onValueChange: v => this.value = v })`。

```typescript
@Entry
@ComponentV2
struct Parent {
  @Local count: number = 0
  build() {
    Column() {
      Text(`${this.count}`)
      Stepper({ value: this.count!! })   // 语法糖：自动展开为 value + $value
    }
  }
}

@ComponentV2
struct Stepper {
  @Param value: number = 0
  @Event $value: (v: number) => void = () => {}   // 事件名必须是 $value
  build() {
    Row() {
      Button('-').onClick(() => this.$value(this.value - 1))
      Text(`${this.value}`)
      Button('+').onClick(() => this.$value(this.value + 1))
    }
  }
}
```

### 完整示例（替代 V1 @Link）

```typescript
// V1 @Link 写法（不在 V2 项目中使用）
// @Link isOn: boolean

// V2 @Param + @Event 写法
@ComponentV2
struct Switch {
  @Param isOn: boolean = false
  @Event onIsOnChange: (v: boolean) => void = () => {}

  build() {
    Toggle({ type: ToggleType.Switch, isOn: this.isOn })
      .onChange((v: boolean) => {
        this.onIsOnChange(v)  // 通知父组件
      })
  }
}

// 父组件用 @Local 持有真值
@ComponentV2
struct Parent {
  @Local isOn: boolean = false

  build() {
    Switch({
      isOn: this.isOn,
      onIsOnChange: (v: boolean) => { this.isOn = v }
    })
  }
}
```

---

## 5. @Provider / @Consumer

### 语法规则

```typescript
// 提供方
@Provider() 变量名: 类型 = 初始值
@Provider('alias') 变量名: 类型 = 初始值  // 带别名

// 消费方
@Consumer() 变量名: 类型 = 默认值  // 必须给默认值（V1 @Consume 不要求）
@Consumer('alias') 变量名: 类型 = 默认值
```

- **必须带括号**（V1 `@Provide / @Consume` 不带括号）
- **替代 V1 `@Provide / @Consume`**：跨层级共享，自动向上查找匹配
- `@Consumer` 在找不到匹配 `@Provider` 时使用默认值

### 完整示例

```typescript
@ComponentV2
struct App {
  @Provider() theme: string = 'light'

  build() {
    Column() {
      Header()
      Content()  // 内部任意层级的 @Consumer 都能拿到 theme
    }
  }
}

@ComponentV2
struct Content {
  @Consumer() theme: string = 'light'  // 必须给默认值

  build() {
    Text('Current theme: ' + this.theme)
      .fontColor(this.theme === 'dark' ? '#FFF' : '#000')
  }
}
```

---

## 6. @ObservedV2 + @Trace

### 语法规则

```typescript
@ObservedV2
class MyClass {
  // 需要观察的属性加 @Trace
  @Trace property1: T = default

  // 不加 @Trace 的属性变化不触发 UI 刷新
  property2: T = default
}
```

- **替代 V1 `@Observed + @ObjectLink`**：V2 的可观察类
- **属性级精确观察**：只有 `@Trace` 标记的属性变化才刷新（V1 `@Observed` 默认观察整个对象第一层）
- **嵌套类**：嵌套的属性所属类也必须是 `@ObservedV2`，且嵌套属性也加 `@Trace`
- **不需要 `@ObjectLink`**：V2 直接用 `@Param` 或 `@Local` 持有 `@ObservedV2` 实例即可

### 完整示例

```typescript
@ObservedV2
class Address {
  @Trace city: string = ''
  @Trace street: string = ''
}

@ObservedV2
class User {
  id: string = ''                    // 不加 @Trace，变化不刷新（场景：稳定 id）
  @Trace name: string = ''
  @Trace address: Address = new Address()  // 嵌套 @ObservedV2 类
}

@ComponentV2
struct UserCard {
  @Param user: User = new User()  // V2 直接 @Param 持有，无需 @ObjectLink

  build() {
    Column() {
      Text(this.user.name)         // user.name 变化刷新
      Text(this.user.address.city) // user.address.city 变化也刷新（嵌套 Trace）
    }
  }
}
```

---

## 7. @Monitor

### 语法规则

```typescript
@Monitor('propName')
methodName(monitor: IMonitor): void {
  // 当 propName 变化时调用
}

@Monitor('a', 'b', 'c')  // 多属性
methodName(monitor: IMonitor): void {
  // a / b / c 中任一变化时调用
  // monitor.dirty 返回变化的属性名数组
}
```

- **替代 V1 `@Watch`**：V2 是**方法装饰器**，V1 是属性装饰器
- 方法签名必须接受 `IMonitor` 参数（即使不用）
- 监听字符串显式声明属性名
- `IMonitor.dirty: string[]` — 本次触发变化的属性名集合
- `IMonitor.value<T>(propName?)` — 读取属性变化前后值

### 完整示例

```typescript
@ComponentV2
struct SearchPage {
  @Local keyword: string = ''
  @Local sortBy: string = 'date'

  @Monitor('keyword')
  onKeywordChange(monitor: IMonitor): void {
    console.info('keyword changed:', monitor.value<string>('keyword')?.now)
    this.performSearch(this.keyword)
  }

  @Monitor('keyword', 'sortBy')
  onAnyFilterChange(monitor: IMonitor): void {
    // monitor.dirty 返回变化的属性名
    monitor.dirty.forEach(name => {
      console.info(`${name} changed`)
    })
  }

  performSearch(kw: string): void { /* ... */ }

  build() {
    TextInput({ placeholder: '搜索...' })
      .onChange((v: string) => { this.keyword = v })
  }
}
```

---

## 8. @Computed

### 语法规则

```typescript
@Computed
get derivedValue(): T {
  return this.deps.someCalculation()
}
```

- **V1 没有等价物**（V2 新增）
- 标记 getter，自动追踪依赖（读取的 `@Local / @Param / @ObservedV2` 属性）
- 缓存结果，依赖未变时返回缓存
- 必须是 getter，不能是普通方法

### 完整示例

```typescript
@ObservedV2
class Item {
  @Trace price: number = 0
  @Trace count: number = 0
}

@ComponentV2
struct Cart {
  @Local items: Item[] = []

  @Computed
  get totalPrice(): number {
    console.info('计算 totalPrice')  // 仅在 items / item.price / item.count 变化时打印
    return this.items.reduce((sum, i) => sum + i.price * i.count, 0)
  }

  @Computed
  get itemCount(): number {
    return this.items.length
  }

  build() {
    Column() {
      Text(`商品数: ${this.itemCount}`)
      Text(`总价: ${this.totalPrice}`)  // 多次读取只计算一次
      Text(`总价（再读）: ${this.totalPrice}`)
    }
  }
}
```

### 何时用 @Computed vs @Monitor

| 需求 | 用 |
|---|---|
| 派生一个只读值给 UI 显示 | `@Computed` |
| 依赖变化时执行副作用（API 调用、修改其他状态） | `@Monitor` |
| 依赖变化时既要显示又要副作用 | `@Computed`（显示）+ `@Monitor`（副作用），各司其职 |

---

## 9. @ReusableV2 (API 12+)

### 语法规则

```typescript
@ReusableV2          // 装饰器无参数；自 API 18 起，仅能装饰 @ComponentV2 组件
@ComponentV2
struct ContactRow {
  @Param @Once title: string = ''
  @Local expanded: boolean = false   // 复用时框架自动重置为初始值

  // V2 复用回调【无入参】aboutToReuse()——不是 V1 的 aboutToReuse(params)
  aboutToReuse(): void {
    // @Local / @Param / @Computed / @Monitor 已自动重置，通常无需手动还原
  }
  aboutToRecycle(): void { /* 可选：回收时释放资源 */ }

  build() { /* ... */ }
}
```

- **替代 V1 `@Reusable`**：配合 `LazyForEach / Repeat` 的组件复用优化。
- **`aboutToReuse()` 无入参**。V1 才是 `aboutToReuse(params: Record<string, Object>)`；V2 复用时**自动重置**组件内 `@Local`/`@Param`/`@Computed`/`@Monitor` 到初始/传入值，不需要手动从 params 取值还原。
- **只能作为 `@ComponentV2` 的子组件**使用；用在 V1（`@Component`）父组件下会**编译报错**。
- **指定复用 id 用 `.reuse({ reuseId: () => 'xxx' })`（ReuseOptions），不要用 V1 的 `.reuseId(...)` 属性**——在 `@ComponentV2 + @ReusableV2` 上写 `.reuseId(...)` 会编译报错（`The reuseId attribute is not applicable ...`）。省略则默认用组件名作 reuseId。
- 不要和 V1 `@Reusable` 同时装饰同一组件（编译校验异常）。
- 长列表场景下显著降低 GC 压力与渲染延迟。

### 完整示例

```typescript
@ReusableV2
@ComponentV2
struct ContactItem {
  @Param @Once name: string = ''
  @Param @Once phone: string = ''

  build() {
    Row() {
      Text(this.name)
      Text(this.phone)
    }
  }
}

@ComponentV2
struct ContactList {
  @Local contacts: Contact[] = []

  build() {
    List() {
      LazyForEach(contacts, (item: Contact) => {
        ListItem() {
          ContactItem({ name: item.name, phone: item.phone })
        }
      }, (item: Contact) => item.id)
    }
  }
}
```

---

## 10. V2 vs V1 速查表

| 用途 | V2 | V1（不推荐） |
|---|---|---|
| 组件 struct | `@ComponentV2` | `@Component` |
| 组件内部状态 | `@Local` | `@State` |
| 父→子单向只读 | `@Param + @Once` | `@Prop`（API 12+ 必须初始化） |
| 父→子单向可改 | `@Param`（不带 @Once） | `@Prop` |
| 父↔子双向 | `@Param + @Event` 回调 | `@Link`（V2 已无） |
| 跨层级 | `@Provider() / @Consumer()` | `@Provide / @Consume` |
| 可观察类 | `@ObservedV2 + @Trace 属性` | `@Observed`（默认观察整体） |
| 持有类实例 | `@Param` / `@Local` | `@ObjectLink`（V2 已无） |
| 全局状态 | `AppStorageV2.connect(...)` | `@StorageLink / @StorageProp` |
| 页面子树共享 | `@Provider() / @Consumer()`（或 `@Param` 下传 `@ObservedV2`） | `@LocalStorageLink / @LocalStorageProp`（**V2 无 LocalStorageV2**） |
| 持久化 | `PersistenceV2.globalConnect(...)` | `PersistentStorage.persistProp` |
| 监听变化 | `@Monitor('prop') method(m: IMonitor)` | `@Watch('method')` |
| 派生值缓存 | `@Computed` | （V1 无） |
| 组件复用 | `@ReusableV2` | `@Reusable` |

---

## 跨文档参考

- [`v2-update-patterns.md`](./v2-update-patterns.md) — 数据更新模式（数组 / Map / 嵌套对象）
- [`v2-global-state.md`](./v2-global-state.md) — `AppStorageV2 / PersistenceV2` 完整模板（无 LocalStorageV2）
- [`v2-real-world.md`](./v2-real-world.md) — V2 实战模式（GlobalState 类、PlaybackController 等）
- [`SKILL.md`](../SKILL.md) — 决策树与陷阱总览
