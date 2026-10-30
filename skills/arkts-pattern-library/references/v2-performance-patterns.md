# 性能优化模式完整参考（V2）

> 本项目锁 ArkTS V2，本文档为 V2 主参考。V1 历史写法（`@Component / @State / @Reusable / @Observed + @Track`）见 [`performance-patterns.md`](./performance-patterns.md)。

V2 在性能层面的关键变化：

| 主题 | V1 | V2 |
|---|---|---|
| 列表项复用 | `@Reusable` | `@ReusableV2` + `@ComponentV2` |
| 类属性精确观察 | `@Observed` + `@Track` | `@ObservedV2` + `@Trace`（默认就是属性级，不再"整对象观察") |
| 派生值缓存 | 无（要手算 + 缓存） | `@Computed` |
| 数组下标改对象属性能否触发刷新 | 否（除非用 @Observed/@Track） | 是（@ObservedV2 + @Trace 属性变化即刷新；ArrayProxy 触发 push/splice 等也刷新） |

## 1. LazyForEach 最佳实践（V2）

### ForEach vs LazyForEach 选择

```typescript
// ===== 反面示例：大列表使用 ForEach，一次性创建所有节点 =====
@ComponentV2
struct BadListPerf {
  @Local items: string[] = Array.from({ length: 1000 }, (_, i) => `Item ${i}`)

  build() {
    // ForEach 会一次性渲染全部 1000 条，首屏卡顿严重
    List() {
      ForEach(this.items, (item: string) => {
        ListItem() {
          Text(item).fontSize(16).height(48)
        }
      }, (item: string) => item)
    }
    .width('100%')
    .height('100%')
  }
}

// ===== 正确做法：大列表使用 LazyForEach，按需创建节点 =====

// IDataSource 实现与 V1 相同（与装饰器无关）
class ListDataSource implements IDataSource {
  private data: string[] = []
  private listeners: DataChangeListener[] = []

  constructor(items: string[]) {
    this.data = items
  }

  totalCount(): number {
    return this.data.length
  }

  getData(index: number): string {
    return this.data[index]
  }

  registerDataChangeListener(listener: DataChangeListener): void {
    if (this.listeners.indexOf(listener) < 0) {
      this.listeners.push(listener)
    }
  }

  unregisterDataChangeListener(listener: DataChangeListener): void {
    const idx = this.listeners.indexOf(listener)
    if (idx >= 0) {
      this.listeners.splice(idx, 1)
    }
  }
}

@ComponentV2
struct GoodListPerf {
  private dataSource: ListDataSource = new ListDataSource(
    Array.from({ length: 1000 }, (_, i) => `Item ${i}`)
  )

  build() {
    // LazyForEach 只创建可视区域 + cachedCount 数量的节点
    List() {
      LazyForEach(this.dataSource, (item: string) => {
        ListItem() {
          Text(item).fontSize(16).height(48)
        }
      }, (item: string) => item)
    }
    .width('100%')
    .height('100%')
    .cachedCount(5) // 预加载前后各 5 条
  }
}
```

### cachedCount 调优建议

```typescript
// cachedCount 设置策略：
// - 简单列表项（纯文本）：cachedCount(3~5)
// - 复杂列表项（图文卡片）：cachedCount(2~3)，避免内存过高
// - 高速滑动场景：cachedCount(8~10)，减少白屏
List() {
  LazyForEach(this.dataSource, (item: string) => {
    ListItem() {
      // 列表项内容
    }
  }, (item: string) => item)
}
.cachedCount(5)
```

## 2. @ReusableV2 组件复用（V2）

```typescript
// ===== 反面示例：列表滑动时频繁创建/销毁组件 =====
@ComponentV2
struct NonReusableCard {
  @Param @Once title: string = ''
  @Param @Once description: string = ''

  // 每次滑出视窗就销毁，滑入时重新创建，造成性能抖动
  build() {
    Column({ space: 6 }) {
      Text(this.title).fontSize(16).fontWeight(FontWeight.Bold)
      Text(this.description).fontSize(13).fontColor('#999999')
    }
    .padding(12)
    .backgroundColor(Color.White)
    .borderRadius(8)
  }
}

// ===== 正确做法：使用 @ReusableV2 复用组件实例 =====
@ReusableV2
@ComponentV2
struct ReusableCard {
  @Param @Once title: string = ''
  @Param @Once description: string = ''

  // V2 复用回调【无入参】——@ReusableV2 复用时框架会自动用父组件传入值重置 @Param、用初始值重置 @Local，
  // 不要手动从 params 还原（@Param 只读，赋值即编译报错 Cannot assign to read-only property）。
  // 通常可整体省略本方法；仅当复用时需执行纯副作用（埋点 / 重置纯内部 @Local 派生态）才实现它。
  aboutToReuse(): void {}

  build() {
    Column({ space: 6 }) {
      Text(this.title).fontSize(16).fontWeight(FontWeight.Bold)
      Text(this.description).fontSize(13).fontColor('#999999')
    }
    .padding(12)
    .backgroundColor(Color.White)
    .borderRadius(8)
  }
}

// 在列表中使用 @ReusableV2 组件
@ComponentV2
struct ReusableListExample {
  private dataSource: ListDataSource = new ListDataSource(
    Array.from({ length: 500 }, (_, i) => `Item_${i}`)
  )

  build() {
    List({ space: 8 }) {
      LazyForEach(this.dataSource, (item: string, index: number) => {
        ListItem() {
          // 框架自动复用 ReusableCard 实例，通过 aboutToReuse 更新数据
          ReusableCard({
            title: `标题 ${index}`,
            description: `描述内容 ${index}`
          })
        }
      }, (item: string) => item)
    }
    .width('100%')
    .height('100%')
    .cachedCount(5)
  }
}
```

## 3. 避免不必要的重新渲染（V2 精准观察）

V1 用大对象 `@State pageData = {...}` 时，修改任一字段都会触发整个对象 UI 刷新；V2 用 `@ObservedV2 + @Trace` 后，只有变化属性绑定的 UI 才刷新。

```typescript
// ===== V2 推荐做法 1：拆分为独立 @Local =====
@ComponentV2
struct GoodStateUpdate {
  @Local title: string = '首页'
  @Local count: number = 0
  @Local items: string[] = ['a', 'b', 'c']

  build() {
    Column() {
      Text(this.title).fontSize(20)        // count 变化时不刷新
      Text(`${this.count}`).fontSize(16)
      ForEach(this.items, (item: string) => {
        Text(item)
      }, (item: string) => item)

      Button('+1').onClick(() => {
        this.count++  // 只触发 count 相关 UI
      })
    }
  }
}

// ===== V2 推荐做法 2：用 @ObservedV2 + @Trace 类，仍能精准刷新 =====
@ObservedV2
class PageData {
  @Trace title: string = '首页'
  @Trace count: number = 0
  @Trace items: string[] = ['a', 'b', 'c']
  @Trace lastUpdate: string = ''
}

@ComponentV2
struct GoodStateUpdateClass {
  @Local data: PageData = new PageData()

  build() {
    Column() {
      Text(this.data.title).fontSize(20)
      Text(`${this.data.count}`).fontSize(16)
      ForEach(this.data.items, (item: string) => {
        Text(item)
      }, (item: string) => item)

      Button('+1').onClick(() => {
        this.data.count++  // V2 精准刷新：只刷新绑定 count 的 Text
      })
    }
  }
}
```

### V2：@Trace 替代 V1 @Track（同时去掉了 @Observed → @ObservedV2）

```typescript
// V2：标记需要观察的属性，未标记的属性变化不触发 UI 刷新
@ObservedV2
class UserProfile {
  @Trace name: string = ''       // UI 关心的字段
  @Trace avatar: string = ''     // UI 关心的字段
  lastLoginTime: string = ''     // 不标记 @Trace，变化不触发 UI 刷新
  internalId: string = ''        // 内部字段，不需要触发 UI
  requestCount: number = 0       // 内部记账计数器：只做记账/控制流，即使每次操作都自增也用普通字段、不加 @Trace（自增不触发刷新）
}

@ComponentV2
struct TraceExample {
  @Local user: UserProfile = new UserProfile()

  aboutToAppear(): void {
    this.user.name = '张三'
  }

  build() {
    Column({ space: 12 }) {
      // 只在 name 或 avatar 变化时刷新
      Text(this.user.name).fontSize(18)

      Button('更新登录时间（不触发UI刷新）')
        .onClick(() => {
          // lastLoginTime 没有 @Trace，这里赋值不会导致 UI 重新渲染
          this.user.lastLoginTime = new Date().toISOString()
        })

      Button('更新名称（触发UI刷新）')
        .onClick(() => {
          // name 有 @Trace，会触发 UI 刷新
          this.user.name = '李四'
        })
    }
  }
}
```

> **@Trace 判定看"是否驱动 UI 渲染"、不看"是否会变"**：VM/model 里只做记账或控制流的内部字段（请求计数器、重试次数、非渲染标志等）即使每次操作都自增也用**普通字段、不加 @Trace**（自增只更新记账、不触发任何刷新）。只有当需求**明确要展示**该值时，才给它加 @Trace 并渲染到 UI；否则不要为一个内部计数器引入多余的反应式开销。

## 4. @Computed 派生值缓存（V2 新增）

V1 没有 @Computed，要么每次 build 重算，要么手动缓存（容易脏）。V2 直接用 `@Computed` getter：

```typescript
@ObservedV2
class CartItem {
  @Trace price: number = 0
  @Trace quantity: number = 0
}

@ComponentV2
struct Cart {
  @Local items: CartItem[] = []

  @Computed
  get totalPrice(): number {
    console.info('计算 totalPrice')  // 只在 items 或子项 price/quantity 变化时打印
    return this.items.reduce((sum, i) => sum + i.price * i.quantity, 0)
  }

  @Computed
  get itemCount(): number {
    return this.items.length
  }

  build() {
    Column() {
      Text(`商品数: ${this.itemCount}`)
      Text(`总价: ${this.totalPrice}`)        // 多次读取只计算一次
      Text(`总价（再读）: ${this.totalPrice}`)  // 命中缓存
    }
  }
}
```

## 5. 图片加载优化（V2，与 V1 一致）

图片优化与装饰器无关，V2 写法仅 struct 装饰器变化：

```typescript
// ===== 反面示例：直接加载原图 =====
@ComponentV2
struct BadImageLoading {
  build() {
    List() {
      ForEach([1, 2, 3, 4, 5], (item: number) => {
        ListItem() {
          Image('https://example.com/photo_full.jpg')
            .width('100%')
            .height(200)
        }
      }, (item: number) => item.toString())
    }
  }
}

// ===== 正确做法：缩略图 + 占位图 =====
@ComponentV2
struct GoodImageLoading {
  build() {
    List({ space: 8 }) {
      ForEach([1, 2, 3, 4, 5], (item: number) => {
        ListItem() {
          Column() {
            Image(`https://example.com/photo_thumb_${item}.jpg`)
              .width('100%')
              .height(200)
              .objectFit(ImageFit.Cover)
              .alt($r('app.media.placeholder'))
              .borderRadius(8)
          }
        }
      }, (item: number) => item.toString())
    }
    .width('100%')
    .height('100%')
    .cachedCount(3)
  }
}

// 网络图片组件封装（V2）
@ComponentV2
struct OptimizedNetworkImage {
  @Param @Once src: string = ''
  @Param @Once thumbnailSrc: string = ''
  @Local isLoaded: boolean = false
  @Local hasError: boolean = false

  build() {
    Stack() {
      if (this.hasError) {
        Column() {
          Text('图片加载失败')
            .fontSize(12)
            .fontColor('#CCCCCC')
        }
        .width('100%')
        .height('100%')
        .backgroundColor('#F5F5F5')
        .justifyContent(FlexAlign.Center)
      } else {
        Image(this.src)
          .width('100%')
          .height('100%')
          .objectFit(ImageFit.Cover)
          .onComplete(() => {
            this.isLoaded = true
          })
          .onError(() => {
            this.hasError = true
          })
      }

      if (!this.isLoaded && !this.hasError) {
        LoadingProgress()
          .width(24)
          .height(24)
      }
    }
  }
}
```

## 6. List 列表性能优化（V2）

```typescript
@ComponentV2
struct OptimizedList {
  private dataSource: ListDataSource = new ListDataSource(
    Array.from({ length: 2000 }, (_, i) => `Item_${i}`)
  )

  build() {
    List({ space: 0 }) {
      LazyForEach(this.dataSource, (item: string, index: number) => {
        ListItem() {
          Row() {
            Text(item).fontSize(16)
          }
          .width('100%')
          .height(56)
          .padding({ left: 16 })
        }
      }, (item: string) => item)
    }
    .width('100%')
    .height('100%')
    .cachedCount(5)
    .divider({ strokeWidth: 0.5, color: '#F0F0F0' })
  }
}

// 多列瀑布流列表
@ComponentV2
struct MultiColumnList {
  private dataSource: ListDataSource = new ListDataSource(
    Array.from({ length: 500 }, (_, i) => `Product_${i}`)
  )

  build() {
    List({ space: 8 }) {
      LazyForEach(this.dataSource, (item: string, index: number) => {
        ListItem() {
          Column({ space: 8 }) {
            Column()
              .width('100%')
              .height(120)
              .backgroundColor('#F0F0F0')
              .borderRadius({ topLeft: 8, topRight: 8 })
            Text(item)
              .fontSize(14)
              .padding({ left: 8, right: 8, bottom: 8 })
          }
          .backgroundColor(Color.White)
          .borderRadius(8)
          .shadow({ radius: 2, color: '#0A000000', offsetY: 1 })
        }
      }, (item: string) => item)
    }
    .width('100%')
    .height('100%')
    .lanes(2, 8)  // 2 列，列间距 8vp
    .padding({ left: 8, right: 8 })
    .cachedCount(4)
  }
}
```

## 7. 状态管理性能优化（V2 父子拆分 + @Param/@Event）

V1 把频繁变化的状态放在父组件，整个父 build 重新执行，所有子组件被迫刷新；V2 同样需要拆分，且子→父用 `@Param + @Event` 而非 `@Link`：

```typescript
// ===== V2 推荐做法：将频繁变化的部分抽离为独立组件 =====

// 计数器独立组件（双向：用 @Param + @Event）
@ComponentV2
struct CounterSection {
  @Param counter: number = 0
  @Event onCounterChange: (v: number) => void = () => {}

  build() {
    Row({ space: 12 }) {
      Text(`计数: ${this.counter}`).fontSize(18)
      Button('+1').onClick(() => { this.onCounterChange(this.counter + 1) })
    }
  }
}

// 列表独立组件（只读：@Param @Once）
@ComponentV2
struct ListSection {
  @Param @Once items: string[] = []

  build() {
    Column() {
      ForEach(this.items, (item: string) => {
        ExpensiveChild({ data: item })
      }, (item: string) => item)
    }
  }
}

@ComponentV2
struct GoodParent {
  @Local counter: number = 0
  @Local listItems: string[] = ['A', 'B', 'C']

  build() {
    Column() {
      // counter 变化只触发 CounterSection 刷新
      CounterSection({
        counter: this.counter,
        onCounterChange: (v: number) => { this.counter = v }
      })
      // listItems 不变，ListSection 不会重新渲染
      ListSection({ items: this.listItems })
    }
  }
}

@ComponentV2
struct ExpensiveChild {
  @Param @Once data: string = ''

  build() {
    Row() {
      Text(this.data).fontSize(16)
    }
    .width('100%')
    .height(60)
    .padding(16)
    .backgroundColor(Color.White)
    .margin({ bottom: 4 })
  }
}
```

## 8. build 函数优化（V2，与 V1 一致 — 与装饰器无关）

```typescript
// ===== 反面示例：过深的组件嵌套 =====
@ComponentV2
struct DeepNesting {
  @Local title: string = '标题'

  build() {
    Column() {
      Row() {
        Column() {
          Row() {
            Column() {
              Text(this.title).fontSize(16)  // 5 层嵌套只为居中
            }
          }
        }
      }
    }
    .width('100%')
    .height('100%')
    .justifyContent(FlexAlign.Center)
  }
}

// ===== 正确做法：扁平化布局 =====
@ComponentV2
struct FlatLayout {
  @Local title: string = '标题'

  build() {
    Column() {
      Text(this.title).fontSize(16)
    }
    .width('100%')
    .height('100%')
    .justifyContent(FlexAlign.Center)
  }
}

// ===== 反面示例：在 build 中做条件分支产生大量冗余节点 =====
@ComponentV2
struct BadConditional {
  @Local type: number = 0

  build() {
    Column() {
      if (this.type === 0) {
        Column() { Text('类型A').fontSize(20) }.width('100%').height(200).backgroundColor('#FF6B6B')
      }
      if (this.type === 1) {
        Column() { Text('类型B').fontSize(20) }.width('100%').height(200).backgroundColor('#4ECDC4')
      }
      if (this.type === 2) {
        Column() { Text('类型C').fontSize(20) }.width('100%').height(200).backgroundColor('#667EEA')
      }
    }
  }
}

// ===== 正确做法：使用 @Builder 复用结构，仅变化数据 =====
interface TypeConfig {
  label: string
  color: ResourceColor
}

@ComponentV2
struct GoodConditional {
  @Local type: number = 0
  private configs: TypeConfig[] = [
    { label: '类型A', color: '#FF6B6B' },
    { label: '类型B', color: '#4ECDC4' },
    { label: '类型C', color: '#667EEA' }
  ]

  @Builder
  TypeCard(config: TypeConfig) {
    Column() {
      Text(config.label).fontSize(20).fontColor(Color.White)
    }
    .width('100%')
    .height(200)
    .backgroundColor(config.color)
    .justifyContent(FlexAlign.Center)
    .borderRadius(12)
  }

  build() {
    Column({ space: 16 }) {
      this.TypeCard(this.configs[this.type])

      Row({ space: 8 }) {
        ForEach([0, 1, 2], (idx: number) => {
          Button(`切换${idx}`)
            .fontSize(14)
            .backgroundColor(this.type === idx ? '#667EEA' : '#CCCCCC')
            .onClick(() => { this.type = idx })
        }, (idx: number) => idx.toString())
      }
    }
    .width('100%')
    .padding(16)
  }
}
```

## V2 性能优化检查清单

- [ ] 大列表用 `LazyForEach + cachedCount`（不要用 ForEach 渲染上千项）
- [ ] 列表项考虑 `@ReusableV2 + @ComponentV2`（替代 V1 `@Reusable`）；`aboutToReuse()` **无入参**、绝不给 @Param 赋值（复用时框架自动重置）
- [ ] 数据模型用 `@ObservedV2 + @Trace`（替代 V1 `@Observed + @Track`）
- [ ] 派生值用 `@Computed` 缓存（替代手算）
- [ ] 频繁变化的状态拆分到独立子组件，避免整个父 build 重跑
- [ ] 子→父双向用 `@Param + @Event`（替代 V1 `@Link`）
- [ ] 列表预缓存用 `cachedCount(n)`（**绝不写 `estimatedItemSize`——List 无此属性、纯属虚构，会编译报错 `Property 'estimatedItemSize' does not exist`**）
- [ ] 图片用缩略图 URL + `alt` 占位图
- [ ] 避免过深嵌套（5 层以上 Column/Row）
