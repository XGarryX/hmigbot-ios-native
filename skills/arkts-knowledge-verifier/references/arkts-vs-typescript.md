# ArkTS vs TypeScript 关键差异

> ArkTS 基于 TypeScript，但有大量语法和语义限制。
> LLM 最常见的错误就是把 TypeScript 习惯直接带入 ArkTS。
> 本文件列出所有关键差异，每条附带代码示例。
>
> **装饰器版本说明**：本项目锁 ArkTS V2（`@ComponentV2 / @Local / @Param / ...`）。下文示例中如出现 V1 装饰器（`@Component / @State / @Prop / ...`），均仅用于"ArkTS vs TS 对比"或"ArkTS 装饰器存在 / TS 没有"角度，**新代码请用 V2 等价**（详见本 skill `references/v2-decorator-rules.md`）。

---

## 1. struct vs class — 组件必须用 struct

ArkTS 的 UI 组件只能用 `struct` 声明，不能用 `class`。

```typescript
// ✗ TypeScript 习惯 — 用 class
@ComponentV2
class MyComponent {
  build() { ... }
}

// ✓ ArkTS 正确写法 — 用 struct（V2 项目）
@ComponentV2
struct MyComponent {
  build() { ... }
}

// V1 legacy 等价（仅老项目参考）
@Component
struct MyComponent {
  build() { ... }
}
```

**差异要点**：
- `struct` 是值类型，由框架管理生命周期
- `struct` 不能用 `new` 实例化（`new MyComponent()` 编译错误）
- `struct` 不能继承（`struct Child extends Parent` 不允许）
- `struct` 没有 `constructor`，初始化通过声明属性默认值完成

---

## 2. build() 内的特殊规则

`build()` 是 UI 描述函数，不是普通方法。框架会多次调用它来构建/更新 UI 树。

```typescript
// ✗ TypeScript 习惯 — 在 build() 里写逻辑
build() {
  let name = this.user.name        // 不允许声明局部变量
  console.log('rendering')          // 不允许 console.log
  const items = this.list.filter(x => x.active)  // 不允许
  Column() {
    Text(name)
  }
}

// ✓ ArkTS 正确写法 — build() 只描述 UI 树
build() {
  Column() {
    Text(this.getUserName())       // 逻辑封装成方法
    if (this.isLoggedIn) {         // if/else 用于条件渲染
      Text('Welcome')
    }
    ForEach(this.items, (item: ItemType) => {  // ForEach 用于循环渲染
      Text(item.name)
    }, (item: ItemType) => item.id)
  }
}
```

**build() 内允许的控制流**：
- `if / else if / else` — 条件渲染
- `ForEach()` / `LazyForEach()` — 循环渲染

**build() 内禁止的操作**：
- 声明变量（`let`/`const`/`var`）
- `console.log()` / `console.info()`
- 调用异步函数（`await`）
- `for` / `while` / `switch` 循环和分支
- 复杂表达式和计算

---

## 3. 类型系统限制

ArkTS 的类型系统比 TypeScript 严格得多。

```typescript
// ✗ TypeScript 习惯 — 使用 any
let data: any = fetchData()

// ✓ ArkTS — 禁止 any/unknown，必须明确类型
let data: ResponseData = fetchData()
```

```typescript
// ✗ TypeScript 习惯 — 联合类型自由使用
let value: string | number | boolean = getVal()

// ✓ ArkTS — 联合类型受限，简单联合可用，复杂联合需避免
// 推荐使用明确的接口或类替代复杂联合类型
```

```typescript
// ✗ TypeScript 习惯 — 动态属性访问
const key = 'name'
const val = obj[key]

// ✓ ArkTS — 使用类型安全的访问方式
const val = (obj as Record<string, string>)['name']
// 或直接使用 obj.name
```

---

## 4. UI 描述方式 — 不是 JSX

ArkTS 的 UI 不是 JSX/TSX，而是基于链式属性调用的声明式语法。

```typescript
// ✗ React/JSX 习惯
return (
  <div style={{ fontSize: 16, color: '#333' }}>
    <span>Hello</span>
  </div>
)

// ✓ ArkTS — 链式属性调用
Column() {
  Text('Hello')
    .fontSize(16)
    .fontColor('#333')
}
.width('100%')
.padding(16)
```

**关键差异**：
- 没有 `<Component />` 语法，直接调用 `Component() { ... }`
- 属性通过 `.method()` 链式调用设置，不是 `prop={value}`
- 子组件写在 `{ }` 闭包内，不是 `<Parent><Child/></Parent>`
- 事件处理写成 `.onClick(() => { ... })`，不是 `onClick={handler}`

---

## 5. 解构和展开运算符限制

```typescript
// ✗ TypeScript 习惯 — 对象解构
const { name, age } = user

// ✓ ArkTS — 限制使用解构，建议直接访问
const name = user.name
const age = user.age
```

```typescript
// ✗ TypeScript 习惯 — 对象展开
const newUser = { ...user, name: 'newName' }

// ✓ ArkTS — 数组展开可用，对象展开受限
// 对于 @ObservedV2（V2，推荐）/ @Observed（V1，legacy）类，创建新实例替代
const newUser = new UserModel()
newUser.name = 'newName'
newUser.age = user.age
```

**注意**：数组的展开运算符 `[...arr]` 通常可用，但对象展开 `{...obj}` 在某些场景下受限。

---

## 6. 模块导入差异

```typescript
// ✗ TypeScript/Node.js 习惯
import express from 'express'
import { readFile } from 'fs'
import * as path from 'path'

// ✓ ArkTS — 使用 @kit.* 系统模块
import { http } from '@kit.NetworkKit'
import { preferences } from '@kit.ArkData'
import { hilog } from '@kit.PerformanceAnalysisKit'
import { window } from '@kit.ArkUI'
```

ArkTS 没有 Node.js 生态，不能用 npm 包。系统 API 通过 `@kit.*` 导入。

---

## 7. 异步编程差异

```typescript
// ✗ TypeScript 习惯 — Promise.all 随意使用
const [a, b, c] = await Promise.all([fetchA(), fetchB(), fetchC()])

// ✓ ArkTS — async/await 基本可用，但注意：
// 1. build() 中不能使用 await
// 2. 异步操作放在 aboutToAppear() 或事件回调中
aboutToAppear(): void {
  this.loadData()  // 在生命周期中调用异步方法
}

async loadData(): Promise<void> {
  const data = await HttpUtil.get<ResponseType>('/api/data')
  this.items = data.list
}
```

---

## 8. 没有 DOM API

```typescript
// ✗ TypeScript/Web 习惯
document.getElementById('myDiv')
window.localStorage.setItem('key', 'value')
window.addEventListener('resize', handler)

// ✓ ArkTS — 没有 DOM，使用框架 API
// 存储用 Preferences
import { preferences } from '@kit.ArkData'
// 窗口操作用 window 模块
import { window } from '@kit.ArkUI'
// 无需手动操作 DOM，UI 由声明式状态驱动
```

---

## 9. 装饰器是 ArkTS 专有的

ArkTS 使用大量框架专有装饰器，TypeScript 中没有对应物。下表同时列出 V2（项目锁，推荐）与 V1（legacy）：

| 用途 | ArkTS V2（推荐） | ArkTS V1（legacy） | TypeScript 中无等价物 |
|---|---|---|---|
| 声明 UI 组件 | `@ComponentV2` | `@Component` | React 用 function/class |
| 标记入口页面 | `@Entry`（V1/V2 通用） | `@Entry` | 无 |
| 组件内响应式状态 | `@Local` | `@State` | React useState |
| 父→子单向只读 | `@Param + @Once` | `@Prop`（API 12+ 必须初始化） | React props |
| 父→子单向可改 | `@Param`（无 @Once） | `@Prop` | 无 |
| 父→子事件 / 父↔子双向 | `@Event` 回调（配合 `@Param`） | `@Link`（V2 已无） | 无直接等价 |
| 跨层级注入 | `@Provider() / @Consumer()`（必须带括号；`@Consumer` 必须给默认值） | `@Provide / @Consume` | React Context |
| 可观察类 | `@ObservedV2`（属性需加 `@Trace` 才观察） | `@Observed` / `@Track`（API 12+） | MobX observable |
| 引用可观察对象 | `@Param`（直接持有 `@ObservedV2` 实例） | `@ObjectLink`（V2 已无） | 无直接等价 |
| 可复用 UI 片段 | `@Builder` / `@LocalBuilder`（V1/V2 通用） | `@Builder` | React 组件 |
| 复用属性组合 | `@Styles`（V1/V2 通用） | `@Styles` | CSS class |
| 扩展组件属性 | `@Extend`（V1/V2 通用） | `@Extend` | 无 |
| 全局存储 | `AppStorageV2.connect(Cls, key, () => new Cls())` | `@StorageLink('key') / @StorageProp('key')` | 无 |
| LocalStorage | `@Provider()/@Consumer()`（无 LocalStorageV2） | `@LocalStorageLink / @LocalStorageProp` | 无 |
| 持久化 | `PersistenceV2.globalConnect({type, key, defaultCreator})` | `PersistentStorage.persistProp` + `@StorageLink` | 无 |
| 监听状态变化 | `@Monitor('prop') method(m: IMonitor): void` | `@Watch('method')` | React useEffect |
| 派生值缓存 | `@Computed get name(): T` | （V1 无） | React useMemo |
| 组件复用（长列表） | `@ReusableV2` | `@Reusable` | 无 |

---

## 10. 错误处理差异

```typescript
// ✗ TypeScript 习惯 — try/catch 捕获 any
try {
  await doSomething()
} catch (e: any) {
  console.error(e.message)
}

// ✓ ArkTS — 不能用 any
try {
  await doSomething()
} catch (err) {
  // err 类型为 Error 或需要显式转换
  hilog.error(0x0000, 'TAG', 'Error: %{public}s', (err as Error).message)
}
```

---

## 11. 不支持 structural typing（标称类型，对象须显式对应具名类型）

TypeScript 用 structural typing（"形状相同即兼容"），**ArkTS 不支持**——类型按名字（标称）匹配；对象字面量必须能对应到具名 `class`/`interface` 且字段完整，类实例必须 `new`。（官方："TypeScript支持structural typing，而ArkTS不支持"，出于运行时性能考虑。）

```typescript
// ✗ TS 习惯 — 把对象字面量当 class 实例（形状兼容即可）
class C { x: number = 0 }
let c: C = { x: 1 }              // ✗ ArkTS 报错：对象字面量不能充当 class 实例

// ✓ ArkTS — 类实例必须 new
let c: C = new C()
c.x = 1

// 数据对象用 interface + 字段完整的字面量
interface Point { x: number; y: number }
let p: Point = { x: 1, y: 2 }   // OK：能对应具名 interface 且字段完整
```
**要点**：不能靠"形状"隐式兼容；DTO 用 `interface` + 完整字面量，行为对象用 `class` + `new`。

---

## 12. 使用箭头函数而非函数表达式

**ArkTS 不支持函数表达式**（把 `function(){}` 当值），一律用箭头函数 `=>`。（官方："ArkTS不支持函数表达式，使用箭头函数（=>）。"）

```typescript
// ✗ TS 习惯 — 函数表达式当值
const add = function (a: number, b: number): number { return a + b }
list.forEach(function (item) { /* ... */ })

// ✓ ArkTS — 箭头函数
const add = (a: number, b: number): number => a + b
list.forEach((item: ItemType) => { /* ... */ })
```
> 具名函数声明 `function add() {}` 仍可用；受限的是把**函数表达式作为值**赋出/传参。组件事件回调也必须用箭头函数以正确绑定 `this`。

---

## 13. 不支持匿名类 / 匿名内部类

匿名类创建的对象类型未知，与"不支持 structural typing"冲突，**ArkTS 不支持**——用具名类或嵌套类替代。

```typescript
// ✗ TS/Java 习惯 — 匿名类实现接口
const handler = new (class implements Listener { onEvent(): void {} })()

// ✓ ArkTS — 具名类
class MyListener implements Listener { onEvent(): void {} }
const handler = new MyListener()
```

---

## 总结速查表

| 特性 | TypeScript | ArkTS |
|---|---|---|
| 组件声明 | `class` | `struct`（不能继承、不能 new） |
| 组件装饰器 | 无（React 用函数/类） | V2: `@ComponentV2` / V1 legacy: `@Component` |
| 状态装饰器 | 无（React useState） | V2: `@Local / @Param / @Event` / V1 legacy: `@State / @Prop / @Link` |
| UI 语法 | JSX/TSX | 链式属性调用 |
| build() 规则 | 无限制 | 只能放 UI 描述，禁止逻辑语句 |
| `any` 类型 | 允许 | 禁止 |
| 对象解构 | 自由使用 | 受限 |
| 对象展开 | 自由使用 | 受限 |
| DOM API | 可用 | 不存在 |
| npm 包 | 可用 | 不可用 |
| 模块导入 | `from 'package'` | `from '@kit.*'` |
| 异步 | 自由使用 | build() 内禁止 |
| structural typing | 支持（形状兼容） | 不支持（标称类型，须具名 + `new`） |
| 函数表达式 | 可用 | 不可用（改箭头函数 `=>`） |
| 匿名类 / 匿名内部类 | 可用 | 不可用（用具名 / 嵌套类） |
