# ArkTS V2 全局状态管理完整模板

> 本文档覆盖 V2 的 `AppStorageV2` / `PersistenceV2` 完整用法与模板代码（**V2 没有 LocalStorageV2**；页面子树共享见 §3）。**本项目锁 V2**。V1 模式（`AppStorage / @StorageLink / PersistentStorage`）查阅请见 [`global-state.md`](./global-state.md)。

---

## 目录

1. [AppStorageV2 完整用法](#1-appstoragev2-完整用法)
2. [PersistenceV2 持久化存储](#2-persistencev2-持久化存储)
3. [页面子树共享：@Provider/@Consumer（V2 无 LocalStorageV2）](#3-页面子树共享providerconsumer)
4. [V1 → V2 迁移模式](#4-v1--v2-迁移模式)
5. [常见陷阱](#5-常见陷阱)

---

## 1. AppStorageV2 完整用法

### 核心 API

```typescript
AppStorageV2.connect<T>(
  type: TypeConstructorWithArgs<T>,    // @ObservedV2 类
  key: string,                          // 全局唯一 key
  defaultCreator: () => T               // 实例工厂（首次 connect 时调用）
): T | undefined  // 实际可用 ! 断言（保证不为 undefined）
```

### 基础模板

```typescript
// 1. 定义状态类（必须 @ObservedV2 + @Trace 属性）
@ObservedV2
export class UserModel {
  @Trace isLoggedIn: boolean = false
  @Trace userId: string = ''
  @Trace userName: string = ''
  @Trace avatar: string = ''
}

// 2. 定义全局 key 常量（推荐，避免拼写错误）
export class StorageKeys {
  static readonly USER = 'user'
  static readonly THEME = 'theme'
  static readonly SETTINGS = 'app_settings'
}

// 3. 任意组件中 connect
@ComponentV2
struct ProfilePage {
  @Local user: UserModel = AppStorageV2.connect(
    UserModel,
    StorageKeys.USER,
    () => new UserModel()
  )!

  build() {
    Column() {
      if (this.user.isLoggedIn) {
        Text(`欢迎，${this.user.userName}`)
        Button('退出').onClick(() => {
          this.user.isLoggedIn = false  // 自动同步到所有 connect 同一 key 的组件
          this.user.userId = ''
          this.user.userName = ''
        })
      } else {
        Button('登录').onClick(() => {
          this.user.isLoggedIn = true
          this.user.userId = '12345'
          this.user.userName = '张三'
        })
      }
    }
  }
}
```

### 多组件共享同一实例

```typescript
@ComponentV2
struct PageA {
  @Local user: UserModel = AppStorageV2.connect(UserModel, 'user', () => new UserModel())!
  // 修改 this.user.userName ...
}

@ComponentV2
struct PageB {
  @Local user: UserModel = AppStorageV2.connect(UserModel, 'user', () => new UserModel())!
  // 自动看到 PageA 的修改
}
```

> 第一次 `connect` 时 `defaultCreator` 被调用创建实例；后续 `connect` 同一 key 直接返回已存在的实例（`defaultCreator` 不再调用）。

### 提前预热（可选）

如果希望在 `EntryAbility.onCreate()` 阶段就把数据准备好（例如从持久层加载）：

```typescript
import { AppStorageV2 } from '@kit.ArkUI'

export default class EntryAbility extends UIAbility {
  onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void {
    // 提前 connect，触发 defaultCreator 调用
    const user = AppStorageV2.connect(UserModel, 'user', () => {
      const u = new UserModel()
      // 从 Preferences 加载
      // u.userId = preferences.getStringSync('userId', '')
      return u
    })!
    // 后续可写入字段：
    // user.userName = await loadUserNameFromDB()
  }
}
```

### 移除 connection

```typescript
AppStorageV2.remove<T>(key: string): void
```

> 移除后再 `connect` 同一 key 会重新创建实例（`defaultCreator` 再次调用）。

---

## 2. PersistenceV2 持久化存储

### 核心 API

```typescript
PersistenceV2.globalConnect<T>({
  type: TypeConstructorWithArgs<T>,    // @ObservedV2 类
  key?: string,                         // 持久化 key（不传时用类名）
  defaultCreator: () => T               // 实例工厂
}): T | undefined
```

- **替代 V1 `PersistentStorage.persistProp`**
- **一站式：磁盘持久化 + UI 响应式**（V1 需要 Preferences + AppStorage 双层模式手动同步）
- 修改 `@Trace` 属性时**自动落盘**
- 应用重启后自动从磁盘恢复

### 基础模板

```typescript
// 1. 定义持久化类
@ObservedV2
export class AppConfig {
  @Trace theme: string = 'light'
  @Trace fontSize: number = 14
  @Trace viewType: string = 'list'
  @Trace sortOrder: string = 'asc'
  @Trace showHidden: boolean = false
}

// 2. 全局单例（推荐：在专门的 GlobalState 模块导出）
export const appConfig = PersistenceV2.globalConnect({
  type: AppConfig,
  key: 'app_config',
  defaultCreator: () => new AppConfig()
})!

// 3. 任意组件中使用（不用每次都 globalConnect）
import { appConfig } from '../common/GlobalState'

@ComponentV2
struct SettingsPage {
  @Local config: AppConfig = appConfig  // 直接拿全局实例

  build() {
    Column() {
      Toggle({ type: ToggleType.Switch, isOn: this.config.theme === 'dark' })
        .onChange((isDark) => {
          this.config.theme = isDark ? 'dark' : 'light'  // ✓ 自动落盘 + UI 响应
        })

      Slider({ value: this.config.fontSize, min: 12, max: 24 })
        .onChange((v) => { this.config.fontSize = v })  // ✓ 自动落盘 + UI 响应
    }
  }
}
```

### 错误处理（持久化失败）

```typescript
PersistenceV2.notifyOnError((key: string, reason: string, message: string) => {
  console.error(`Persistence error: key=${key}, reason=${reason}, message=${message}`)
  // 上报埋点 / 提示用户 / 重试逻辑
})
```

### 移除持久化项

```typescript
PersistenceV2.remove(key: string): void
PersistenceV2.keys(): Array<string>  // 列出所有已持久化的 key
```

---

## 3. 页面子树共享：@Provider/@Consumer

> ⚠️ **没有 `LocalStorageV2` 这个 API。** V2 的存储类只有 `AppStorageV2`（全局）和 `PersistenceV2`（持久化全局）；`import { LocalStorageV2 } from '@kit.ArkUI'` 会编译报错 `has no exported member 'LocalStorageV2'`。V1 的 `@LocalStorageLink/@LocalStorageProp`（LocalStorage 页面树作用域）在 V2 **没有同名等价物**。

**页面子树范围共享**（页面 A → 子组件 B → 孙组件 C，都能读写，但不进全局、别的页面看不到）用 **`@Provider` / `@Consumer`**（跨组件层级双向同步）：祖先组件 `@Provider` 提供，任意后代 `@Consumer` 取用，无需逐层 `@Param` 转发，作用域 = 该组件子树。

```typescript
// 祖先（页面根）提供
@Entry
@ComponentV2
struct PageRoot {
  @Provider('pageState') count: number = 0   // 提供给整棵子树
  build() { Column() { MiddleArea() } }
}

@ComponentV2
struct MiddleArea {
  build() { Column() { LeafEditor() } }       // 中间层无需转发
}

// 任意后代消费（可读可写，写回自动同步整棵子树）
@ComponentV2
struct LeafEditor {
  @Consumer('pageState') count: number = 0    // @Consumer 必须给默认值
  build() {
    Button(`+1 (${this.count})`).onClick(() => { this.count++ })
  }
}
```

- 共享复杂对象时，让被共享对象是 `@ObservedV2` 类（字段加 `@Trace`），`@Provider`/`@Consumer` 持同一实例。
- 也可不用 @Provider/@Consumer，直接由页面根 `@Local` 持一个 `@ObservedV2` 实例、用 `@Param` 显式下传给子组件——适合层级浅、依赖明确的场景。

### 何时用哪种作用域

| 场景 | 选 |
|---|---|
| 单页面树范围共享（页面 A → 子组件 B → 子组件 C） | `@Provider`/`@Consumer`（或 `@Param` 下传 `@ObservedV2`） |
| 跨页面共享（任意 Page 都能拿到） | `AppStorageV2` |
| 需要持久化（重启保留） | `PersistenceV2` |
| 严格单组件内部 | `@Local`（无需 storage） |

---

## 4. V1 → V2 迁移模式

### 模式 A：`@StorageLink` → `AppStorageV2.connect`

```typescript
// V1 写法
@Component
struct V1Page {
  @StorageLink('isLoggedIn') isLoggedIn: boolean = false
  @StorageLink('userName') userName: string = ''
  build() {
    Text(this.isLoggedIn ? this.userName : '未登录')
  }
}

// V2 写法
@ObservedV2
class UserModel {
  @Trace isLoggedIn: boolean = false
  @Trace userName: string = ''
}

@ComponentV2
struct V2Page {
  @Local user: UserModel = AppStorageV2.connect(UserModel, 'user', () => new UserModel())!
  build() {
    Text(this.user.isLoggedIn ? this.user.userName : '未登录')
  }
}
```

> V2 把 V1 散落的 key（`isLoggedIn / userName`）封装到一个类，避免 key 拼写不一致。

### 模式 B：`PersistentStorage.persistProp` → `PersistenceV2.globalConnect`

```typescript
// V1 写法
PersistentStorage.persistProp('theme', 'light')
PersistentStorage.persistProp('fontSize', 14)

@Component
struct V1Settings {
  @StorageLink('theme') theme: string = 'light'
  @StorageLink('fontSize') fontSize: number = 14
}

// V2 写法
@ObservedV2
class AppConfig {
  @Trace theme: string = 'light'
  @Trace fontSize: number = 14
}

const appConfig = PersistenceV2.globalConnect({
  type: AppConfig,
  key: 'app_config',
  defaultCreator: () => new AppConfig()
})!

@ComponentV2
struct V2Settings {
  @Local config: AppConfig = appConfig
}
```

### 模式 C：V1 双层模式 → V2 单层 PersistenceV2

V1 经常写"Preferences + AppStorage 双层"以同时实现持久化与 UI 响应：

```typescript
// V1 双层（复杂）
async setViewType(v: string): Promise<void> {
  AppStorage.setOrCreate('viewType', v)         // UI 响应
  await preferences.put('viewType', v)          // 磁盘持久化
  await preferences.flush()
}
```

V2 一行解决：

```typescript
// V2 单层
this.config.viewType = v   // ✓ 自动同时完成 UI 响应 + 磁盘持久化
```

---

## 5. 常见陷阱

### 陷阱 1：connect 时 type 与 key 不匹配

```typescript
@ObservedV2
class UserModel { @Trace name: string = '' }

@ObservedV2
class GuestModel { @Trace anonymousId: string = '' }

// 错误 — 同一 key 两次 connect 用了不同类型
AppStorageV2.connect(UserModel, 'user', () => new UserModel())
AppStorageV2.connect(GuestModel, 'user', () => new GuestModel())  // ❌ 类型冲突
```

**修正**：同一 key 永远对应同一类型；不同概念用不同 key。

### 陷阱 2：用 PersistenceV2 持久化非 @ObservedV2 类

```typescript
class PlainConfig {  // ❌ 缺 @ObservedV2
  theme: string = ''
}

PersistenceV2.globalConnect({
  type: PlainConfig,  // ❌ 运行时报错
  key: 'config',
  defaultCreator: () => new PlainConfig()
})
```

**修正**：所有传入 `connect` 的类必须是 `@ObservedV2 + @Trace` 属性。

### 陷阱 3：持久化复杂结构（嵌套 / 数组 / 集合）

V2 `PersistenceV2` 支持嵌套 `@ObservedV2` 类与数组，但**不支持函数 / Class 方法 / 循环引用**。两条易踩的硬规则（不满足会**静默失败**——仅日志报错、不抛异常）：

- **复杂/嵌套类型属性必须加 `@Type`**：属性是 `@ObservedV2` 类、`Array`、`Date`、`Map`、`Set` 时必须用 `@Type(...)` 标注其构造器，否则报错码 **14108 "Miss @Type"** 且不持久化。
- **裸集合类型须用 `UIUtils.makeObserved`**：`defaultCreator` 返回 `Array/Map/Set/Date` 时要包一层 `UIUtils.makeObserved(...)`，否则持久化失败。

```typescript
import { PersistenceV2, Type, UIUtils } from '@kit.ArkUI'

@ObservedV2
class Item {
  @Trace title: string = ''
  // ❌ 不要在持久化类里放 () => void 这类成员
}

@ObservedV2
class Cart {
  @Type(Item)                  // ✓ 嵌套类/数组元素类型必须标 @Type，否则 14108 静默失败
  @Trace items: Item[] = []
}

// 持久化集合：defaultCreator 用 makeObserved 包裹
const cart = PersistenceV2.globalConnect({
  type: Cart, key: 'cart',
  defaultCreator: () => UIUtils.makeObserved(new Cart())
})!
```

### 陷阱 4：`connect` 后忘记 `!` 断言

```typescript
const user = AppStorageV2.connect(UserModel, 'user', () => new UserModel())  // 类型: UserModel | undefined
user.userName = 'X'  // ❌ 编译错误：可能为 undefined
```

**修正**：

```typescript
const user = AppStorageV2.connect(UserModel, 'user', () => new UserModel())!  // 加 ! 断言
```

实际上首次 `connect` 必返回实例，`undefined` 仅在异常场景出现，加 `!` 是惯用法。

### 陷阱 5：在循环中重复 connect

```typescript
// ❌ 反模式
for (let i = 0; i < 100; i++) {
  AppStorageV2.connect(...)  // 性能开销
}

// ✓ 一次 connect，引用复用
const user = AppStorageV2.connect(UserModel, 'user', () => new UserModel())!
for (let i = 0; i < 100; i++) {
  // use user
}
```

---

## 跨文档参考

- [`v2-decorators.md`](./v2-decorators.md) — 装饰器完整语法
- [`v2-update-patterns.md`](./v2-update-patterns.md) — 数据更新模式
- [`v2-real-world.md`](./v2-real-world.md) — 实战业务场景（GlobalState 类、PlaybackController 等）
