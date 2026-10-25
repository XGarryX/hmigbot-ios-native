---
name: arkts-state-manager
description: 生成 ArkTS/HarmonyOS 状态管理代码（V2 优先，API 12+）。当用户需要解决组件间数据通信、全局状态共享、数据持久化、UI 刷新不触发等问题，或使用 V2/V1 状态装饰器（@Local/@Param/@Event/@Provider/@Consumer/@ObservedV2/AppStorageV2/PersistenceV2 等）时，务必触发此 skill。即使只说"父子组件传值""全局变量"也应触发。页面路由/导航跳转用 arkts-navigation-builder。
metadata:
  type: domain
  domain: state
  tags:
  - state
  - decorator
  - arkts-v2
  - appstorage
---
# ArkTS State Manager — 状态管理生成器（V2 优先）

## API 版本与项目策略

本 skill 的代码模板基于 **API 12+（HarmonyOS 5.0.0+）和 ArkTS V2 装饰器体系**。

> **项目锁 V2**：本项目所有新生成代码使用 V2 装饰器（`@ComponentV2 / @Local / @Param / @Event / @Once / @Provider / @Consumer / @ObservedV2 / @Trace / @Monitor / @Computed / AppStorageV2 / PersistenceV2`）。如需 V1 兼容写法查阅，参阅 `references/state-decorators.md` 等 V1 历史文档（已加 legacy 标识）。

V2 vs V1 关键差异：

| V1 装饰器 | V2 等价 | 备注 |
|---|---|---|
| `@Component` | `@ComponentV2` | struct 装饰器 |
| `@State` | `@Local` | 组件内部状态 |
| `@Prop`（单向只读） | `@Param + @Once` | V2 显式标记不可改 |
| `@Prop`（单向可改） | `@Param`（不带 `@Once`） | 子组件可改本地副本 |
| `@Link`（双向） | **没有直接等价** — `@Param + @Event` 回调 | V2 强调单向数据流 + 事件 |
| `@Provide / @Consume` | `@Provider() / @Consumer()` | 必须带括号，`@Consumer` 必须给默认值 |
| `@Observed` | `@ObservedV2` | 类装饰器 |
| `@ObjectLink` | **取消** — `@ObservedV2` 实例直接通过 `@Param` 传 | V2 简化对象引用 |
| `@StorageLink / @StorageProp` | `AppStorageV2.connect(Cls, key, () => new Cls())` | 配合 `@ObservedV2` 类 |
| `@LocalStorageLink / @LocalStorageProp` | `@Provider()/@Consumer()`（子树共享）/ `@Param` 下传 `@ObservedV2` | **V2 无 LocalStorageV2** |
| `PersistentStorage.persistProp` | `PersistenceV2.globalConnect({type, key, defaultCreator})` | V2 一站式持久化 |
| `@Watch` | `@Monitor('propName')` | V2 是方法装饰器，签名带 `IMonitor` |
| — | `@Computed`（V2 新增） | 缓存派生状态 |
| — | `@Trace`（V2 新增） | 类属性级精确观察 |

生成代码前，先确认目标 API 版本 ≥ 12。检查方法：读取 `build-profile.json5` 的 `compatibleSdkVersion` 字段。遇到版本兼容性或其他不确定的 ArkTS 知识点（如属性、语法、权限等），参阅 arkts-knowledge-verifier skill。

---

## 核心原理

ArkTS V2 的状态管理基于**装饰器驱动的响应式系统 + 单向数据流**。框架通过装饰器标记需要观察的变量，当变量变化时自动触发 UI 重渲染。V2 相比 V1 的核心改进：

- **明确单向数据流**：父→子 `@Param`，子→父 `@Event` 回调（不再有 V1 `@Link` 隐式双向）
- **属性级观察**：V2 用 `@Trace` 精确标记可观察属性（V1 默认观察整个对象第一层）
- **派生状态缓存**：V2 新增 `@Computed`，避免重复计算
- **类与组件关注点分离**：V2 鼓励把状态封装到 `@ObservedV2` 类，组件用 `@Local` 持有实例

---

## 状态装饰器选择决策树（V2）

```
数据在哪些组件间共享？
│
├─ 只在当前组件内使用
│   └─ @Local
│       值类型直接观察；@ObservedV2 类的 @Trace 属性变化触发刷新
│
├─ 父 → 子 单向只读
│   └─ @Param + @Once
│       子组件不可修改，父组件更新时同步
│
├─ 父 → 子 单向可改（在子组件内可读可写，但不回传父）
│   └─ @Param
│       子组件可读写本地副本，父更新时覆盖
│
├─ 父 ↔ 子 双向同步（V1 @Link 替代方案）
│   └─ 子: @Param value + @Event $value（事件名 = $ + 属性名）；父: Child({ value: this.value!! }) 语法糖
│       或手工 @Event onValueChange（名任意，但父就不能用 !!）。详见 v2-decorators.md «!! 双向绑定»
│
├─ 跨层级（祖先 → 后代）
│   └─ @Provider（祖先）+ @Consumer（后代）
│       无需逐层传递，自动向下查找匹配
│
├─ 引用 @ObservedV2 类实例
│   └─ @Param + 类属性加 @Trace
│       直接用 @Param 持有实例（V2 不再用 @ObjectLink）
│
├─ 全局共享（所有页面）
│   └─ AppStorageV2.connect(Cls, key, () => new Cls())
│       配合 @ObservedV2 类，自动同步内存与所有引用
│
├─ 页面子树范围共享（页面 A → 子组件 B → 孙组件 C，不进全局）
│   └─ @Provider（祖先）+ @Consumer（后代）  ⚠️ 没有 LocalStorageV2 这个 API
│       或页面根 @Local 持 @ObservedV2 实例、用 @Param 下传
│
└─ 持久化（应用重启保留）
    └─ PersistenceV2.globalConnect({type: Cls, key, defaultCreator: ...})
        一站式：磁盘持久化 + UI 响应式
```

> ⚠️ **V2 真实存储类只有 `AppStorageV2`（全局）与 `PersistenceV2`（持久化全局）；没有 `LocalStorageV2`**（曾被误传，实际不存在，`import` 即编译报错 `has no exported member 'LocalStorageV2'`）。"页面子树范围、不进全局"的共享用 `@Provider`/`@Consumer`，或页面根 `@Local` 持 `@ObservedV2` 实例并 `@Param` 下传。

---

## V2 装饰器用法与刷新模式

> **MUST**：编写任何 V2 状态代码前，先读 `references/v2-decorators.md` —— @ComponentV2 / @Local / @Param+@Once / @Event / @Provider+@Consumer / @ObservedV2+@Trace / @Monitor / @Computed / @ReusableV2 的完整语法、示例与 V2/V1 速查表。
>
> **MUST**：数组 / Map/Set / 嵌套对象 / Date 更新后 UI 不刷新时，先读 `references/v2-update-patterns.md`（含反模式速查）。

### 框架能观察什么（速记）

| 数据类型 | 能观察 | 不能观察 |
|---|---|---|
| 简单类型（@Local） | 重新赋值 | — |
| @ObservedV2 类 | @Trace 属性赋值 | 未加 @Trace 的属性 |
| 数组 | 整体重新赋值；V2 ArrayProxy 的 push/splice | 下标改对象属性（除非对象是 @ObservedV2 且属性带 @Trace） |
| Map/Set | set / delete / clear | — |

---

## AppStorageV2 初始化时机

**关键规则**：使用 `AppStorageV2.connect()` 时，第一次调用会自动用 `defaultCreator` 创建实例。无需在 `EntryAbility.onCreate()` 提前 `setOrCreate`（V1 模式）。

```typescript
// V2 简化模式：组件直接 connect，框架处理初始化
@ComponentV2
struct MainPage {
  @Local user: UserModel = AppStorageV2.connect(UserModel, 'user', () => new UserModel())!
  // 第一次访问时自动用 () => new UserModel() 创建实例
  // 后续 connect 同一 key 共享同一实例
}
```

如需在 `EntryAbility` 提前从持久层加载数据，仍可在 `onCreate` 中调用 `AppStorageV2.connect()` 预热并写入字段。

---

## 常见陷阱对照（V2）

### 陷阱 1：忘记给类属性加 @Trace

```typescript
// 错误 — 没加 @Trace，UI 不会刷新
@ObservedV2
class User {
  name: string = ''  // ❌ 缺少 @Trace
}

// 正确
@ObservedV2
class User {
  @Trace name: string = ''  // ✓
}
```

### 陷阱 2：AppStorageV2 key 拼写不一致

```typescript
// 错误 — 两次 connect 用了不同 key
AppStorageV2.connect(UserModel, 'user', () => new UserModel())  // 一处
AppStorageV2.connect(UserModel, 'usr', () => new UserModel())   // 另一处 — 不同实例！

// 正确 — 统一 key 常量
export class StorageKeys {
  static readonly USER = 'user'
}
AppStorageV2.connect(UserModel, StorageKeys.USER, () => new UserModel())
```

### 持久化决策树（V2 简化）

```
数据需要怎样存储和响应？
│
├─ 只在运行时使用，不需持久化
│   └─ AppStorageV2.connect(Cls, key, () => new Cls())
│       应用退出后数据丢失
│
├─ 需要持久化，但不需要驱动 UI 实时刷新
│   └─ Preferences（通过 PreferencesUtil）
│       直接读写磁盘，UI 在下次读取时获取新值
│
└─ 需要持久化 + UI 实时刷新（最常见）
    └─ PersistenceV2.globalConnect({type, key, defaultCreator})
        一站式：磁盘持久化 + UI 响应式（V2 推荐，无需 V1 的"双层模式"）
```

**PersistenceV2 模板**：

```typescript
@ObservedV2
class Config {
  @Trace viewType: string = 'list'
  @Trace sortOrder: string = 'asc'
}

@ComponentV2
struct SettingsPage {
  @Local config: Config = PersistenceV2.globalConnect({
    type: Config,
    key: 'app_config',
    defaultCreator: () => new Config()
  })!

  build() {
    // 修改自动落盘 + UI 响应（无需手动同步两套存储）
    Button('切换视图').onClick(() => {
      this.config.viewType = this.config.viewType === 'list' ? 'grid' : 'list'
    })
  }
}
```

**何时用哪种**：

| 场景 | 方案 | 示例 |
|------|------|------|
| 临时 UI 状态 | `@Local` | 加载中状态、弹窗显示 |
| 运行时全局状态 | `AppStorageV2` | 当前登录用户信息 |
| 用户设置/偏好 | `PersistenceV2` | 主题、排序方式、视图类型 |
| 简单 token 持久化 | `PersistenceV2`（含 string 字段的类） | 登录 token |
| 结构化数据持久化 | RdbStore | 用户收藏、历史记录 |

### 陷阱 3：在 @Builder 中使用状态装饰器

```typescript
// 错误 — @Builder 是函数，不能持有状态
@Builder
function myBuilder() {
  @Local count: number = 0  // 编译错误
}

// 正确 — 状态放在 @ComponentV2 struct 中，@Builder 只接收参数
```

### 陷阱 4：V2 不允许 V1 装饰器混用

```typescript
// 错误 — V2 项目中混入 V1 装饰器
@ComponentV2
struct Page {
  @State count: number = 0  // ❌ V1 @State 不能用在 @ComponentV2 中
}

// 正确 — V2 全套
@ComponentV2
struct Page {
  @Local count: number = 0  // ✓
}
```

### 陷阱 5：@Monitor 回调中修改被监听的属性

```typescript
// 危险 — 可能导致无限循环
@Local count: number = 0

@Monitor('count')
onCountChange(monitor: IMonitor): void {
  this.count = this.count + 1  // 又触发 onCountChange！
}

// 正确 — @Monitor 中只修改其他变量
@Monitor('count')
onCountChange(monitor: IMonitor): void {
  this.displayText = `Count is ${this.count}`
}
```

---

## 生成检查清单

- [ ] 根据数据共享范围选择了正确的 V2 装饰器
- [ ] 所有 struct 用 `@ComponentV2`，所有可观察类用 `@ObservedV2`
- [ ] `@Local` 变量已初始化
- [ ] `@Param` 必须有默认值（V2 强制）
- [ ] 父子双向场景用 `@Param + @Event`，不要试图用 V1 `@Link`
- [ ] 类的可观察属性已加 `@Trace`
- [ ] AppStorageV2.connect 的 key 拼写完全一致
- [ ] 持久化场景用 `PersistenceV2.globalConnect`，不再用 V1 双层模式
- [ ] `@Monitor` 回调不会修改被监听的属性
- [ ] 同一文件不混用 V1/V2 装饰器（如 `@Component` + `@ComponentV2`）

---

## 跨 Skill 协作

| 需要什么 | 读取哪里 |
|---------|---------|
| 完整业务功能 | `arkts-pattern-library/SKILL.md` |
| UI 组件配合状态 | `arkts-component-builder/SKILL.md` |
| 数据层（Model + Service） | `arkts-data-layer/SKILL.md` |
| 全局状态 + 导航守卫 | `arkts-navigation-builder/SKILL.md` |

> 完整路由矩阵见 `arkts-knowledge-verifier/references/skill-routing-guide.md`

---

## References

### V2 主参考（推荐，本项目实际使用）

- `references/v2-decorators.md` — 所有 V2 装饰器的完整语法和边界情况
- `references/v2-update-patterns.md` — 各种数据结构的正确更新模式（数组、Map、嵌套对象，V2 视角）
- `references/v2-global-state.md` — AppStorageV2 / PersistenceV2 完整模板（+ 页面子树共享 @Provider/@Consumer；**无 LocalStorageV2**）
- `references/v2-real-world.md` — V2 GlobalState 注册表、PersistenceV2 持久化、PlaybackController 绑定、EventBus 联动

### V1 历史参考（仅老项目兼容查阅）

- `references/state-decorators.md` — V1 装饰器全集（@State / @Prop / @Link 等）
- `references/update-patterns.md` — V1 数据更新模式
- `references/global-state.md` — V1 AppStorage / @StorageLink / PersistentStorage 模板
- `references/real-world-state-patterns.md` — V1 真实场景模式

> 遇到版本兼容性或其他不确定的 ArkTS 知识点（如属性、语法、权限等），参阅 **arkts-knowledge-verifier** skill
