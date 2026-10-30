# 性能优化模式完整参考（**V1 历史文档 — Legacy**）

> ⚠️ **本项目锁 ArkTS V2**。本文档为 **V1 历史参考**（`@Component / @State / @Prop / @Observed / @Track / @Reusable` 等），仅用于阅读老代码或迁移老项目时查阅。
>
> **新代码请使用 V2 装饰器**：参阅 [`v2-performance-patterns.md`](./v2-performance-patterns.md)（V2 主参考）和 [`../SKILL.md`](../SKILL.md)。

---

## 1. LazyForEach 最佳实践

### ForEach vs LazyForEach 选择

```typescript
// ===== 反面示例：大列表使用 ForEach，一次性创建所有节点 =====
@Component
struct BadListPerf {
  @State items: string[] = Array.from({ length: 1000 }, (_, i) => `Item ${i}`)

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

// 必须实现 IDataSource 接口
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

@Component
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
    .cachedCount(5) // 预加载前后各 5 条，平衡内存和滑动流畅度
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
.cachedCount(5) // 根据场景调整
```

## 2. @Reusable 组件复用

```typescript
// ===== 反面示例：列表滑动时频繁创建/销毁组件 =====
@Component
struct NonReusableCard {
  @Prop title: string = ''
  @Prop description: string = ''

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

// ===== 正确做法：使用 @Reusable 复用组件实例 =====
@Reusable
@Component
struct ReusableCard {
  @State title: string = ''
  @State description: string = ''

  // 当组件被复用时调用，更新数据而不重新创建
  aboutToReuse(params: Record<string, Object>): void {
    this.title = params.title as string
    this.description = params.description as string
  }

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

// 在列表中使用 @Reusable 组件
@Component
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

## 3. 避免不必要的重新渲染（精准状态更新）

```typescript
// ===== 反面示例：一个大对象状态导致整体刷新 =====
interface PageData {
  title: string
  count: number
  items: string[]
  lastUpdate: string
}

@Component
struct BadStateUpdate {
  // 修改 count 时，整个 pageData 标记为变化，所有绑定该状态的 UI 都会刷新
  @State pageData: PageData = {
    title: '首页',
    count: 0,
    items: ['a', 'b', 'c'],
    lastUpdate: ''
  }

  build() {
    Column() {
      Text(this.pageData.title).fontSize(20)    // count 变了，这里也被迫刷新
      Text(`${this.pageData.count}`).fontSize(16)
      // items 列表也会被迫刷新
      ForEach(this.pageData.items, (item: string) => {
        Text(item)
      }, (item: string) => item)

      Button('+1').onClick(() => {
        // 触发整个对象更新
        this.pageData = {
          title: this.pageData.title,
          count: this.pageData.count + 1,
          items: this.pageData.items,
          lastUpdate: new Date().toISOString()
        }
      })
    }
  }
}

// ===== 正确做法：拆分为独立的 @State 变量 =====
@Component
struct GoodStateUpdate {
  // 各状态独立，修改 count 不影响 title 和 items 相关的 UI
  @State title: string = '首页'
  @State count: number = 0
  @State items: string[] = ['a', 'b', 'c']

  build() {
    Column() {
      Text(this.title).fontSize(20)        // 不会因 count 变化而刷新
      Text(`${this.count}`).fontSize(16)   // 只有 count 变化时刷新
      ForEach(this.items, (item: string) => {
        Text(item)                         // 不会因 count 变化而刷新
      }, (item: string) => item)

      Button('+1').onClick(() => {
        this.count++ // 只触发 count 相关的 UI 更新
      })
    }
  }
}
```

### 使用 @Track 装饰器精准追踪属性

```typescript
// @Track 装饰器标记需要追踪的属性，未标记的属性变化不触发 UI 刷新
@Observed
class UserProfile {
  @Track name: string       // UI 关心的字段
  @Track avatar: string     // UI 关心的字段
  lastLoginTime: string     // 不标记 @Track，变化不触发 UI 刷新
  internalId: string        // 内部字段，不需要触发 UI

  constructor(name: string, avatar: string) {
    this.name = name
    this.avatar = avatar
    this.lastLoginTime = ''
    this.internalId = ''
  }
}

@Component
struct TrackExample {
  @State user: UserProfile = new UserProfile('张三', '')

  build() {
    Column({ space: 12 }) {
      // 只在 name 或 avatar 变化时刷新
      Text(this.user.name).fontSize(18)

      Button('更新登录时间（不触发UI刷新）')
        .onClick(() => {
          // lastLoginTime 没有 @Track，这里赋值不会导致 UI 重新渲染
          this.user.lastLoginTime = new Date().toISOString()
        })

      Button('更新名称（触发UI刷新）')
        .onClick(() => {
          // name 有 @Track，会触发 UI 刷新
          this.user.name = '李四'
        })
    }
  }
}
```

## 4. 图片加载优化

```typescript
// ===== 反面示例：直接加载原图 =====
@Component
struct BadImageLoading {
  build() {
    List() {
      ForEach([1, 2, 3, 4, 5], (item: number) => {
        ListItem() {
          // 直接加载原图，可能是几 MB 的大图
          Image('https://example.com/photo_full.jpg')
            .width('100%')
            .height(200)
        }
      }, (item: number) => item.toString())
    }
  }
}

// ===== 正确做法：多策略图片优化 =====
@Component
struct GoodImageLoading {
  build() {
    List({ space: 8 }) {
      ForEach([1, 2, 3, 4, 5], (item: number) => {
        ListItem() {
          Column() {
            Image(`https://example.com/photo_thumb_${item}.jpg`) // 使用缩略图 URL
              .width('100%')
              .height(200)
              .objectFit(ImageFit.Cover)
              // 设置图片解码尺寸，避免解码超大图片
              .alt($r('app.media.placeholder')) // 占位图，避免加载时白屏
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

// 网络图片组件封装：统一加载状态 + 错误处理
@Component
struct OptimizedNetworkImage {
  @Prop src: string = ''
  @Prop thumbnailSrc: string = ''
  @State isLoaded: boolean = false
  @State hasError: boolean = false

  build() {
    Stack() {
      if (this.hasError) {
        // 加载失败占位
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

      // 加载中指示器
      if (!this.isLoaded && !this.hasError) {
        LoadingProgress()
          .width(24)
          .height(24)
      }
    }
  }
}
```

## 5. List 列表性能优化

```typescript
// ===== 列表性能关键参数 =====
@Component
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

// ===== 多列瀑布流列表 =====
@Component
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
    .lanes(2, 8) // 2 列，列间距 8vp
    .padding({ left: 8, right: 8 })
    .cachedCount(4)
  }
}
```

## 6. 状态管理性能优化

```typescript
// ===== 反面示例：父组件状态变化导致所有子组件刷新 =====
@Component
struct BadParent {
  @State counter: number = 0
  @State listItems: string[] = ['A', 'B', 'C']

  build() {
    Column() {
      Text(`计数: ${this.counter}`)
      Button('+1').onClick(() => { this.counter++ })

      // counter 变化时，父组件 build() 重新执行
      // 下面的子组件虽然数据没变，但因为在同一个 build() 中也会被刷新
      ForEach(this.listItems, (item: string) => {
        ExpensiveChild({ data: item }) // 每次 counter++ 都重新渲染
      }, (item: string) => item)
    }
  }
}

// ===== 正确做法：将频繁变化的部分抽离为独立组件 =====
// 计数器独立组件
@Component
struct CounterSection {
  @Link counter: number

  build() {
    Row({ space: 12 }) {
      Text(`计数: ${this.counter}`).fontSize(18)
      Button('+1').onClick(() => { this.counter++ })
    }
  }
}

// 列表独立组件
@Component
struct ListSection {
  @Prop items: string[] = []

  build() {
    // items 没变化就不会重新渲染
    ForEach(this.items, (item: string) => {
      ExpensiveChild({ data: item })
    }, (item: string) => item)
  }
}

@Component
struct GoodParent {
  @State counter: number = 0
  @State listItems: string[] = ['A', 'B', 'C']

  build() {
    Column() {
      // counter 变化只触发 CounterSection 刷新
      CounterSection({ counter: $counter })
      // listItems 不变，ListSection 不会重新渲染
      ListSection({ items: this.listItems })
    }
  }
}

@Component
struct ExpensiveChild {
  @Prop data: string = ''

  build() {
    // 模拟复杂子组件
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

## 7. build 函数优化（最小化组件树深度）

```typescript
// ===== 反面示例：过深的组件嵌套 =====
@Component
struct DeepNesting {
  @State title: string = '标题'

  build() {
    Column() {
      Row() {
        Column() {
          Row() {
            Column() {
              // 5 层嵌套只为了居中一个 Text，布局计算开销大
              Text(this.title).fontSize(16)
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
@Component
struct FlatLayout {
  @State title: string = '标题'

  build() {
    // 一层 Column 即可实现居中
    Column() {
      Text(this.title).fontSize(16)
    }
    .width('100%')
    .height('100%')
    .justifyContent(FlexAlign.Center)
  }
}

// ===== 反面示例：在 build 中做条件分支产生大量冗余节点 =====
@Component
struct BadConditional {
  @State type: number = 0

  build() {
    Column() {
      // 三种类型用三个完整的布局，切换时频繁创建/销毁
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
@Component
struct GoodConditional {
  @State type: number = 0
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
      // 复用同一个 Builder，只传不同数据
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

interface TypeConfig {
  label: string
  color: ResourceColor
}
```
