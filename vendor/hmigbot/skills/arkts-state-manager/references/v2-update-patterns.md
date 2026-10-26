# ArkTS V2 数据更新与 UI 刷新模式

> 本文档详细说明 V2 装饰器下如何正确更新各类数据以触发 UI 刷新。**本项目锁 V2**。V1 模式查阅请见 [`update-patterns.md`](./update-patterns.md)。

---

## 目录

1. [简单类型（number / string / boolean）](#1-简单类型)
2. [@ObservedV2 类与 @Trace 属性](#2-observedv2-类与-trace-属性)
3. [数组更新（V2 ArrayProxy）](#3-数组更新)
4. [Map / Set 更新](#4-map--set-更新)
5. [嵌套对象更新](#5-嵌套对象更新)
6. [Date 更新](#6-date-更新)
7. [反模式速查](#7-反模式速查)

---

## 1. 简单类型

`number / string / boolean / enum` 的 `@Local`：**直接赋值即触发**。

```typescript
@ComponentV2
struct Counter {
  @Local count: number = 0
  @Local isActive: boolean = false

  build() {
    Column() {
      Button('+1').onClick(() => { this.count++ })           // ✓ 触发
      Button('toggle').onClick(() => { this.isActive = !this.isActive })  // ✓ 触发
    }
  }
}
```

---

## 2. @ObservedV2 类与 @Trace 属性

### 关键规则

- **只有 `@Trace` 属性变化触发刷新**
- 嵌套属性的类也必须是 `@ObservedV2`，且嵌套属性也加 `@Trace`
- 替换整个实例（重新赋值）也触发刷新

### 示例

```typescript
@ObservedV2
class User {
  id: string = ''                  // ❌ 不加 @Trace，UI 不响应
  @Trace name: string = ''         // ✓
  @Trace age: number = 0           // ✓
}

@ComponentV2
struct UserCard {
  @Local user: User = new User()

  build() {
    Column() {
      Text(this.user.name)
      Button('改名').onClick(() => {
        this.user.name = '李四'  // ✓ @Trace 触发刷新
      })
      Button('改 id').onClick(() => {
        this.user.id = 'new-id'  // ❌ 不刷新（id 无 @Trace）
      })
      Button('换实例').onClick(() => {
        this.user = new User()    // ✓ 替换实例，整体刷新
      })
    }
  }
}
```

### 选择性观察

故意不加 `@Trace` 可以避免无关属性变化触发不必要的刷新（性能优化）：

```typescript
@ObservedV2
class LogEntry {
  id: string = ''             // 稳定，不需观察
  timestamp: number = 0       // 稳定，不需观察
  @Trace message: string = '' // 用户编辑，需观察
}
```

---

## 3. 数组更新

V2 数组在 `@Local / @Param` 下默认包装为 ArrayProxy，**`push / pop / splice / shift / unshift / 下标赋值` 都触发刷新**。

### 推荐写法

```typescript
@ComponentV2
struct TodoList {
  @Local items: string[] = []

  // 方式 1：push（V2 推荐，简洁）
  add(item: string): void {
    this.items.push(item)  // ✓ 触发
  }

  // 方式 2：splice
  removeAt(idx: number): void {
    this.items.splice(idx, 1)  // ✓ 触发
  }

  // 方式 3：下标赋值
  updateAt(idx: number, newVal: string): void {
    this.items[idx] = newVal  // ✓ 触发
  }

  // 方式 4：整体重新赋值（最稳，跨场景兼容性好）
  reset(newList: string[]): void {
    this.items = newList  // ✓ 触发
  }

  // 方式 5：扩展运算符
  addAll(more: string[]): void {
    this.items = [...this.items, ...more]  // ✓ 触发
  }
}
```

### 数组中的对象需要 @ObservedV2

如果数组元素是对象，且要观察对象属性变化，元素类必须是 `@ObservedV2 + @Trace`：

```typescript
@ObservedV2
class TodoItem {
  @Trace title: string = ''
  @Trace done: boolean = false
}

@ComponentV2
struct List {
  @Local todos: TodoItem[] = []

  toggleDone(idx: number): void {
    this.todos[idx].done = !this.todos[idx].done  // ✓ @Trace 属性变化，触发对应 item 刷新
  }
}
```

---

## 4. Map / Set 更新

`Map / Set` 在 V2 下也是 Proxy，使用其方法触发刷新。

```typescript
@ComponentV2
struct Tags {
  @Local tagMap: Map<string, number> = new Map([['arkts', 1], ['hmos', 2]])
  @Local tagSet: Set<string> = new Set(['featured', 'hot'])

  build() {
    Column() {
      Button('add map').onClick(() => {
        this.tagMap.set('new', 3)  // ✓ 触发
      })
      Button('delete map').onClick(() => {
        this.tagMap.delete('arkts')  // ✓ 触发
      })
      Button('clear map').onClick(() => {
        this.tagMap.clear()  // ✓ 触发
      })

      Button('add set').onClick(() => {
        this.tagSet.add('new')  // ✓ 触发
      })
    }
  }
}
```

> ⚠️ 通过 `for...of` 遍历后修改 Map/Set 内对象的属性，**对象本身需是 `@ObservedV2 + @Trace`** 才能触发对应位置刷新。

---

## 5. 嵌套对象更新

V2 通过嵌套 `@ObservedV2` 类实现深层观察。**不需要 V1 的 `@ObjectLink`**。

```typescript
@ObservedV2
class Address {
  @Trace city: string = ''
  @Trace street: string = ''
  @Trace postcode: string = ''
}

@ObservedV2
class Profile {
  @Trace name: string = ''
  @Trace address: Address = new Address()  // 嵌套必须也是 @ObservedV2
}

@ObservedV2
class User {
  @Trace id: string = ''
  @Trace profile: Profile = new Profile()
}

@ComponentV2
struct UserView {
  @Local user: User = new User()

  build() {
    Column() {
      Text(this.user.profile.name)
      Text(this.user.profile.address.city)

      // 三层嵌套都能响应：
      Button('改 city').onClick(() => {
        this.user.profile.address.city = 'Beijing'  // ✓ 触发刷新
      })
      Button('换整个 address').onClick(() => {
        this.user.profile.address = new Address()  // ✓ 触发刷新
      })
    }
  }
}
```

### V1 → V2 嵌套观察对照

| 场景 | V1 | V2 |
|---|---|---|
| 父持有类实例 | `@State user: User`（@Observed 类） | `@Local user: User`（@ObservedV2 类） |
| 子接收类实例 | `@ObjectLink user: User`（必须） | `@Param user: User`（直接传） |
| 嵌套属性观察 | 嵌套也得 `@Observed`，但子需 `@ObjectLink` 才能拿到嵌套对象 | 嵌套也得 `@ObservedV2 + @Trace`，路径上每层都响应 |

---

## 6. Date 更新

```typescript
@ComponentV2
struct Picker {
  @Local selectedDate: Date = new Date()

  build() {
    Column() {
      Text(this.selectedDate.toLocaleString())
      Button('明天').onClick(() => {
        this.selectedDate.setDate(this.selectedDate.getDate() + 1)  // ✓ 触发
      })
      Button('换日期').onClick(() => {
        this.selectedDate = new Date('2026-01-01')  // ✓ 触发
      })
    }
  }
}
```

---

## 7. 反模式速查

### ❌ 反模式 1：忘记 @Trace

```typescript
@ObservedV2
class User {
  name: string = ''  // ❌ 没 @Trace
}

@ComponentV2
struct View {
  @Local user: User = new User()
  build() {
    Text(this.user.name)
    Button('改名').onClick(() => {
      this.user.name = '李四'  // ❌ 不刷新！
    })
  }
}
```

**修正**：给 `name` 加 `@Trace`。

### ❌ 反模式 2：嵌套类未声明 @ObservedV2

```typescript
class Address {  // ❌ 缺 @ObservedV2
  city: string = ''
}

@ObservedV2
class User {
  @Trace address: Address = new Address()  // 整体替换可触发，但属性变化不触发
}

// View.user.address.city = 'X'  → ❌ 不刷新
```

**修正**：`Address` 也加 `@ObservedV2`，且 `city` 加 `@Trace`。

### ❌ 反模式 3：试图用 V1 装饰器

```typescript
@ComponentV2
struct Page {
  @State count: number = 0  // ❌ 编译错误
  @ObjectLink user: User    // ❌ V2 无此装饰器
}
```

**修正**：V2 用 `@Local count` / `@Param user`。

### ❌ 反模式 4：父子双向用 @Link 思路

```typescript
// 错误尝试 — V2 没有 @Link
@ComponentV2
struct Child {
  @Link value: number  // ❌ 编译错误
}
```

**修正**：用 `@Param + @Event` 回调（见 [`v2-decorators.md` §4](./v2-decorators.md#4-event)）。

### ❌ 反模式 5：在 @Builder 中声明状态

```typescript
@Builder
function MyBuilder() {
  @Local count: number = 0  // ❌ @Builder 不能持有状态
}
```

**修正**：把状态放到 `@ComponentV2 struct`，`@Builder` 仅作 UI 拼装。

### ❌ 反模式 6：直接读取 AppStorageV2 内部 Map（不通过 connect）

```typescript
// ❌ V2 不应该直接 get/set 全局存储
const v = AppStorageV2.connect(UserModel, 'user', () => new UserModel())  // 拿到引用就好
v.userName = 'X'  // ✓ 直接改实例属性触发响应
```

**修正**：所有访问通过 `connect()` 返回的实例引用 + `@Trace` 属性。

---

## 跨文档参考

- [`v2-decorators.md`](./v2-decorators.md) — 装饰器完整语法
- [`v2-global-state.md`](./v2-global-state.md) — 全局/持久化状态模板
- [`v2-real-world.md`](./v2-real-world.md) — 实战业务场景模式
