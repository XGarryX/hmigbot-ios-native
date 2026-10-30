# ArkTS V2 组件代码生成模板

> 从 `arkts-component-builder/SKILL.md` 下沉：标准骨架 / @Builder·@Styles·@Extend 复用 / 常见错误完整代码。SKILL.md 通过 MUST-read 指针引用本文件。

## 标准组件骨架（V2）

生成任何 UI 组件时，使用此骨架：

```typescript
@ComponentV2
struct ComponentName {
  // 1. 输入参数（来自父组件）
  @Param @Once title: string = '默认标题'   // 只读
  @Param items: ItemType[] = []             // 可改本地副本
  @Event onItemClick: (id: string) => void = () => {}

  // 2. 内部状态
  @Local private count: number = 0
  @Local private isLoading: boolean = true

  // 3. 派生状态（可选）
  @Computed
  get itemCount(): number {
    return this.items.length
  }

  // 4. 生命周期 — 数据加载（禁止使用 loadMockData）
  async aboutToAppear(): Promise<void> {
    try {
      this.items = await DBReader.getXxxList()
    } catch (e) {
      this.items = []
    } finally {
      this.isLoading = false
    }
  }

  // 5. @Builder 抽取复杂子 UI
  @Builder
  itemBuilder(item: ItemType) {
    Row() {
      Text(item.title).fontSize(16)
    }
    .padding(12)
    .onClick(() => { this.onItemClick(item.id) })
  }

  // 6. build() — 只有 UI 描述
  build() {
    Column() {
      Text(this.title)
      if (this.isLoading) {
        LoadingProgress().width(48).height(48)
      } else {
        ForEach(this.items, (item: ItemType) => {
          this.itemBuilder(item)
        }, (item: ItemType) => item.id)
      }
    }
    .width('100%')
    .height('100%')
  }
}
```

**入口页面**额外加 `@Entry`：

```typescript
@Entry
@ComponentV2
struct IndexPage {
  build() {
    Column() { /* ... */ }
  }
}
```

---


## @Builder / @Styles / @Extend 复用（V1/V2 通用）

`@Builder / @Styles / @Extend / @BuilderParam` 在 V1/V2 通用，无需迁移。

### @Builder — 抽取可复用 UI 片段

当一个 UI 片段在 build() 中出现 2+ 次，或超过 10 行时，抽取为 @Builder：

```typescript
@ComponentV2
struct CardList {
  @Local items: { title: string; desc: string }[] = []

  // 组件内 @Builder
  @Builder
  cardItem(title: string, desc: string) {
    Column() {
      Text(title).fontSize(18).fontWeight(FontWeight.Bold)
      Text(desc).fontSize(14).fontColor('#666')
    }
    .padding(16)
    .borderRadius(12)
    .backgroundColor(Color.White)
  }

  build() {
    Column() {
      // 这里传的是【静态】字面量，永不随状态变化 → 值参完全正常
      this.cardItem('标题1', '描述1')
      this.cardItem('标题2', '描述2')
    }
  }
}
```

#### ⚠️ 动态状态不能作 @Builder 的「值参」传入（否则定格首帧、永不刷新）

> **仅针对随状态变化的动态数据**。上例那种永不变的静态字面量走值参没有任何问题；本规则只约束「值会随 @Local/@Trace 改变、期望 UI 跟着刷新」的数据。

**硬事实**（`@Builder装饰器：自定义构建函数.md`，docs VERIFIED）：`@Builder` 默认**按值传递**——当传入的参数是状态变量时，**状态变量的改变不会引起 @Builder 函数内的 UI 刷新**。把动态值（尤其 `number`/`string`/`boolean` 这类简单类型）当值参传进 @Builder，builder 内渲染的就是**调用时刻的快照**，之后状态再变，这一行/这个磁贴会**定格在首帧**不再更新。

**最隐蔽的错因 —— 传「@Trace 对象的属性值」≠ 传「@Trace 对象」**：即使数据源是 `@ObservedV2 + @Trace` 的响应式对象，一旦你取出它的某个属性值（如 `item.currentPrice` 这个 `number`）作为值参传入，传的是**这个 number 的快照、不是那个可观测对象**，照样不刷新。@Trace 值传能刷新，**只在传入整个对象、且 builder 内读它的 @Trace 属性**时成立（见下方合格实现④）。

**四条合格实现（择一）**：

1. **@Builder 内直读 `this.` 上被订阅的状态**（@Local/@Trace），动态值不走参数；只有**静态**的标签/标题才走值参。← 最简单、首选。
2. **抽 @ComponentV2 子组件，动态值用 `@Param` 接**（`@Param` 变化会刷新其关联组件），在子组件内部渲染。
3. **单一对象字面量**参数按引用传递：**仅当** @Builder 只有**一个**参数、且调用时**直接传对象字面量**（`this.row({ label, value: this.count })`）才生效；**≥2 个参数一律不刷新**（哪怕都用对象字面量）。
4. **在 @ComponentV2 内，把整个 `@ObservedV2 + @Trace` 类对象**（不是它的某个 number 属性值）作值参传入，builder 内读该对象的 @Trace 属性 → 可刷新。

**Worked example —— WRONG（值参传 @Trace 属性值）vs CORRECT（直读 this）**

```typescript
@ObservedV2
class SeckillItem {
  @Trace currentPrice: number = 0
  constructor(p: number) { this.currentPrice = p }
}

// ❌ 错误：把 @Trace 对象的【属性值】(number) 当值参传入 @Builder
@ComponentV2
struct WrongCard {
  @Local item: SeckillItem = new SeckillItem(199)

  @Builder
  priceRow(label: string, price: number) {   // price 是 number 值参 = 快照
    Row() {
      Text(label)
      Text('¥' + price.toFixed(2))            // 定格首帧，item.currentPrice 再变这里也不刷新
    }
  }

  build() {
    Column() {
      // 传的是 item.currentPrice 这个 number（快照），不是 item 对象 → 不刷新
      this.priceRow('现价', this.item.currentPrice)
    }
  }
}

// ✅ 正确（合格实现①）：静态标签走值参，动态价格在 @Builder 内直读 this.item.currentPrice
@ComponentV2
struct RightCard {
  @Local item: SeckillItem = new SeckillItem(199)

  @Builder
  priceRow(label: string) {                   // 只有静态 label 走值参
    Row() {
      Text(label)
      Text('¥' + this.item.currentPrice.toFixed(2))  // 直读被订阅状态 → 价格变化自动刷新
    }
  }

  build() {
    Column() {
      this.priceRow('现价')
    }
  }
}
```

> 若被复用行确实需要**每次传入不同的动态数据源**（如 ForEach 里各不相同的 item），走合格实现④：把整个 `@ObservedV2+@Trace` 对象作值参传（`this.cardBody(item)`），builder 内读 `item.currentPrice`；或走②抽子组件用 `@Param item: SeckillItem` 接。**切记传对象本身、不要传它的 number 属性值。**

### @BuilderParam — 把 UI 片段当参数传给子组件

```typescript
@ComponentV2
struct Card {
  @Builder defaultContent() {}                              // @BuilderParam 的默认值必须是 @Builder 方法
  @BuilderParam content: () => void = this.defaultContent   // ❌ 不能写 = () => {}（报 ''@BuilderParam' property can only initialized by '@Builder' function'）

  build() {
    Column() {
      this.content()  // 由父组件提供具体 UI
    }
    .borderRadius(12)
    .padding(16)
  }
}

// 父组件
@ComponentV2
struct Parent {
  build() {
    Card() {
      Text('父组件传入的内容').fontSize(16)
    }
  }
}
```

> **⚠️ 自定义组件 + 尾随闭包后，不能链式通用属性**（高频踩坑，编译期硬错）：自定义组件用尾随闭包形 `Card() { ... }` 注入 @BuilderParam 内容后，**闭包 `}` 已结束该组件表达式**，紧跟的 `.width()/.border()/.backgroundColor()` 会被当成新语句解析 → 报 `Cannot find name 'width'/'border'` 或 `Declaration or statement expected`。**内置容器**（Column/Row/Stack…）尾随闭包后链式属性是合法的，**自定义组件不行**。修法：外层套一层内置容器，把通用属性加在容器上。
>
> ```typescript
> // ❌ 错误：自定义组件尾随闭包后直接链式属性
> MyContainer() {
>   ForEach(this.items, (it: ItemType) => { this.itemView(it) }, (it: ItemType) => it.id)
> }
> .width('100%')          // 报 Cannot find name 'width'
> .border({ width: 1 })   // 报 Declaration or statement expected
>
> // ✅ 正确：外层套内置容器，属性加在容器上
> Column() {
>   MyContainer() {
>     ForEach(this.items, (it: ItemType) => { this.itemView(it) }, (it: ItemType) => it.id)
>   }
> }
> .width('100%')
> .border({ width: 1, color: '#CCCCCC' })
> ```

### wrapBuilder — 把全局 @Builder 当值/集合，运行时动态选取

需要"按数据字段在多个排版/卡片样式之间运行时切换"时，用 `wrapBuilder()` 把**全局** @Builder 包成可存进数组/Map、可传递的句柄。

- 函数名是 `wrapBuilder()`（**小写**开头）；句柄类型是 **`WrappedBuilder<[参数类型...]>`**——注意是 `Wrapped`，**不是** `WrapBuilder`。
- `wrapBuilder()` **只能包全局 @Builder 函数**（不能包 struct 成员方法）。
- 句柄的 `.builder(...)` 只能写在 struct 内部的 UI 位置。

```typescript
@Builder
function compactRow(row: FeedRow) { Text(row.title).fontSize(16) }
@Builder
function richRow(row: FeedRow) { Text(row.title).fontSize(20).fontColor(Color.Blue) }

const FALLBACK: WrappedBuilder<[FeedRow]> = wrapBuilder(compactRow)

@ObservedV2
class FeedRow {
  id: string = ''
  title: string = ''
  // 把"这一行该用哪个排版"的 WrappedBuilder 预存在数据上
  wb: WrappedBuilder<[FeedRow]> = FALLBACK
  constructor(id: string, title: string, wb: WrappedBuilder<[FeedRow]>) {
    this.id = id; this.title = title; this.wb = wb
  }
}

@Entry
@ComponentV2
struct Index {
  // builder 表：值类型是 WrappedBuilder<[FeedRow]>，不是 WrapBuilder
  private table: Map<string, WrappedBuilder<[FeedRow]>> = new Map([
    ['compact', wrapBuilder(compactRow)],
    ['rich', wrapBuilder(richRow)]
  ])
  @Local rows: FeedRow[] = []

  aboutToAppear(): void {
    // 关键：选取（.get()/?? 等方法调用、表达式）放在 @Builder **外面**——这里数据装配时算好
    this.rows = [
      new FeedRow('a', '紧凑卡片', this.table.get('compact') ?? FALLBACK),
      new FeedRow('b', '富信息卡片', this.table.get('rich') ?? FALLBACK)
    ]
  }

  build() {
    Column() {
      // ✅ 调用头是 ForEach 循环变量的成员：row.wb.builder(row)
      ForEach(this.rows, (row: FeedRow) => {
        row.wb.builder(row)
      }, (row: FeedRow) => row.id)
    }
  }
}
```

> **`.builder()` 调用的两条铁律**（违反报 `Only UI component syntax can be written here` / `'...' does not meet UI component syntax`）：
> 1. **不能**在 @Builder 体内写 `const wb = ...; wb.builder()`——@Builder 体内只允许 UI 语法，禁止声明局部变量。
> 2. 调用头**不能是方法/函数调用的返回值**：`this.pickBuilder(k).builder(row)` ❌、`this.table.get(k)!.builder(row)` ❌。先把选取结果落到**数据字段或 `this` 成员**（在 @Builder 外算好），再用**成员访问/循环变量**调用：`row.wb.builder(row)` ✅、`this.headerWb.builder(arg)` ✅。

### @Styles — 复用属性组合

```typescript
// 定义（组件外部全局或组件内部）
@Styles function cardStyle() {
  .padding(16)
  .borderRadius(12)
  .backgroundColor(Color.White)
  .shadow({ radius: 4, color: '#1A000000' })
}

// 使用
Column() { /* ... */ }
  .cardStyle()
```

### @Extend — 扩展特定组件

```typescript
// 只能扩展指定组件类型
@Extend(Text)
function titleText() {
  .fontSize(20)
  .fontWeight(FontWeight.Bold)
  .fontColor('#222')
}

// 使用
Text('Hello').titleText()
```

---


## 常见错误 vs 正确写法（V2 视角）

### 错误 1：在 build() 中调用异步函数

```typescript
// 错误
build() {
  Column() {
    await this.loadData()  // build() 不能 async
  }
}

// 正确 — 在生命周期中加载
aboutToAppear(): void {
  this.loadData()
}
```

### 错误 2：组件属性顺序错误

```typescript
// 推荐顺序：尺寸 → 布局 → 外观 → 交互
Text('Hello')
  .width('100%')                    // 尺寸
  .padding(16)                      // 布局
  .fontSize(16)                     // 外观
  .fontColor('#333')
  .backgroundColor(Color.White)
  .borderRadius(8)
  .onClick(() => { /* ... */ })     // 交互
```

### 错误 3：忘记 ListItem 包裹

```typescript
// 错误 — List 的直接子组件必须是 ListItem
List() {
  ForEach(this.items, (item) => {
    Text(item.name)  // 直接放 Text 会报错
  })
}

// 正确
List() {
  ForEach(this.items, (item) => {
    ListItem() {
      Text(item.name)
    }
  }, (item) => item.id)
}
```

### 错误 4：Grid 没有 GridItem

```typescript
// 错误
Grid() {
  ForEach(this.items, (item) => {
    Column() { /* ... */ }  // 必须用 GridItem 包裹
  })
}

// 正确
Grid() {
  ForEach(this.items, (item) => {
    GridItem() {
      Column() { /* ... */ }
    }
  }, (item) => item.id)
}
```

### 错误 5：@Builder 中直接修改子组件入参

```typescript
// 错误 — @Builder 中直接修改入参（不会触发 UI 更新）
@Builder
itemView(item: ItemType) {
  Text(item.name)
    .onClick(() => {
      item.selected = true  // 不会触发 UI 更新（除非 ItemType 是 @ObservedV2 且 selected 加 @Trace）
    })
}

// 正确 — 通过 @Event 回调通知父组件，或把 ItemType 标为 @ObservedV2
@Builder
itemView(item: ItemType, onSelect: () => void) {
  Text(item.name)
    .onClick(() => onSelect())
}

// 或：
@ObservedV2
class ItemType {
  id: string = ''
  @Trace selected: boolean = false   // V2 加 @Trace 后修改自动刷新
}
```

### 错误 6：父子双向同步用 V1 @Link 写法

```typescript
// 错误 — V2 没有 @Link
@ComponentV2
struct Child {
  @Link value: string = ''   // ❌ 编译错误
}

// 正确 — V2 用 @Param + @Event 回调
@ComponentV2
struct Child {
  @Param value: string = ''
  @Event onValueChange: (v: string) => void = () => {}

  build() {
    TextInput({ text: this.value })
      .onChange((v: string) => { this.onValueChange(v) })
  }
}

// 父组件
@ComponentV2
struct Parent {
  @Local text: string = ''

  build() {
    Child({
      value: this.text,
      onValueChange: (v: string) => { this.text = v }
    })
  }
}
```

---
