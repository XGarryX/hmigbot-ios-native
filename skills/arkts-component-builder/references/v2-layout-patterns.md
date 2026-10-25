# ArkTS 布局容器完整模板（V2）

> 本文档为 LLM 提供 6 种核心布局容器的 V2 完整代码模板（`@ComponentV2 / @Local / @Param / @Event`），可直接复制使用。**本项目锁 V2**，本文档为主参考。V1 历史模板查阅请见 [`layout-patterns.md`](./layout-patterns.md)。

---

## 1. Column — 垂直表单布局

<!-- 适用场景：需要从上到下排列元素时使用，最常见于登录/注册表单、设置页面、信息展示列表。 -->

```typescript
// 垂直表单布局：登录页面（V2）
@Entry
@ComponentV2
struct LoginForm {
  @Local userName: string = ''
  @Local userPassword: string = ''
  @Local isLoading: boolean = false

  @Event onLoginSuccess: () => void = () => {}

  build() {
    Column() {
      // 顶部 Logo
      Image($r('app.media.logo'))
        .width(80)
        .height(80)
        .margin({ top: 60, bottom: 40 })

      // 标题
      Text('欢迎登录')
        .fontSize(24)
        .fontWeight(FontWeight.Bold)
        .margin({ bottom: 32 })

      // 用户名输入框
      TextInput({ placeholder: '请输入用户名', text: this.userName })
        .type(InputType.Normal)
        .height(48)
        .width('100%')
        .margin({ bottom: 16 })
        .onChange((value: string) => { this.userName = value })

      // 密码输入框
      TextInput({ placeholder: '请输入密码', text: this.userPassword })
        .type(InputType.Password)
        .height(48)
        .width('100%')
        .margin({ bottom: 24 })
        .onChange((value: string) => { this.userPassword = value })

      // 登录按钮
      Button('登录', { type: ButtonType.Capsule })
        .width('100%')
        .height(48)
        .backgroundColor('#007DFF')
        .onClick(() => { this.isLoading = true })

      // 底部辅助链接
      Row() {
        Text('忘记密码？')
          .fontSize(14)
          .fontColor('#999')
        Blank()
        Text('注册账号')
          .fontSize(14)
          .fontColor('#007DFF')
      }
      .width('100%')
      .margin({ top: 16 })
    }
    .width('100%')
    .height('100%')
    .padding({ left: 24, right: 24 })
    .backgroundColor('#F5F5F5')
    .alignItems(HorizontalAlign.Center)
    .justifyContent(FlexAlign.Start)
  }
}
```

**Column 关键属性：**

| 属性 | 类型 | 说明 |
|------|------|------|
| `alignItems` | `HorizontalAlign` | 水平对齐：`.Start` / `.Center` / `.End` |
| `justifyContent` | `FlexAlign` | 垂直分布方式 |
| `space` | `number \| string` | 子元素间距 |

---

## 2. Row — 水平卡片布局

<!-- 适用场景：横向排列元素，如卡片内的图片+文字信息、工具栏按钮组、底部导航。 -->

```typescript
// 水平卡片：用户信息卡（V2）
@ComponentV2
struct UserCard {
  @Param @Once userName: string = ''       // 不用 name（无碰撞但保持业务命名）
  @Param @Once userDesc: string = ''
  @Param @Once avatarUrl: string = ''
  @Param @Once tags: string[] = []

  build() {
    Row() {
      // 左侧头像
      Image(this.avatarUrl)
        .width(56)
        .height(56)
        .borderRadius(28)
        .objectFit(ImageFit.Cover)

      // 中间文字信息区域
      Column() {
        Text(this.userName)
          .fontSize(16)
          .fontWeight(FontWeight.Medium)
          .fontColor('#333')
          .maxLines(1)
          .textOverflow({ overflow: TextOverflow.Ellipsis })

        Text(this.userDesc)
          .fontSize(13)
          .fontColor('#999')
          .margin({ top: 4 })
          .maxLines(2)
          .textOverflow({ overflow: TextOverflow.Ellipsis })

        // 标签行
        Row({ space: 6 }) {
          ForEach(this.tags, (tag: string) => {
            Text(tag)
              .fontSize(11)
              .fontColor('#007DFF')
              .backgroundColor('#E8F0FE')
              .borderRadius(4)
              .padding({ left: 6, right: 6, top: 2, bottom: 2 })
          }, (tag: string, index: number) => `${index}_${tag}`)
        }
        .margin({ top: 6 })
      }
      .layoutWeight(1)
      .alignItems(HorizontalAlign.Start)
      .margin({ left: 12 })

      // 右侧箭头
      Image($r('sys.media.ohos_ic_public_arrow_right'))
        .width(20)
        .height(20)
        .fillColor('#CCC')
    }
    .width('100%')
    .padding(16)
    .backgroundColor(Color.White)
    .borderRadius(12)
    .shadow({ radius: 8, color: 'rgba(0,0,0,0.08)', offsetX: 0, offsetY: 2 })
    .alignItems(VerticalAlign.Center)
    .justifyContent(FlexAlign.Start)
  }
}
```

**Row 关键属性：**

| 属性 | 类型 | 说明 |
|------|------|------|
| `alignItems` | `VerticalAlign` | 垂直对齐：`.Top` / `.Center` / `.Bottom` |
| `justifyContent` | `FlexAlign` | 水平分布方式 |
| `space` | `number \| string` | 子元素间距 |

> **注意：** `layoutWeight(1)` 是 Row 中最常用的技巧，让某个子元素占满剩余空间。

---

## 3. Stack — 图片叠加层布局

<!-- 适用场景：元素重叠显示，如图片上叠加文字/角标、头像在线状态标记、浮动按钮。 -->

```typescript
// 堆叠布局：商品图片 + 折扣角标 + 底部渐变文字（V2）
@ComponentV2
struct ProductImageCard {
  @Param @Once imageUrl: string = ''
  @Param @Once cardTitle: string = ''      // 不用 title（避免与系统 title 概念混淆）
  @Param @Once discountLabel: string = ''  // 不用 discount
  @Param @Once isNew: boolean = false

  build() {
    Stack() {
      // 底层：商品图片
      Image(this.imageUrl)
        .width('100%')
        .height(200)
        .objectFit(ImageFit.Cover)
        .borderRadius(12)

      // 中层：底部渐变遮罩 + 标题
      Column() {
        Blank()
        Column() {
          Text(this.cardTitle)
            .fontSize(16)
            .fontColor(Color.White)
            .fontWeight(FontWeight.Medium)
            .maxLines(1)
            .textOverflow({ overflow: TextOverflow.Ellipsis })
        }
        .width('100%')
        .padding({ left: 12, right: 12, bottom: 12, top: 24 })
        .linearGradient({
          direction: GradientDirection.Bottom,
          colors: [['rgba(0,0,0,0)', 0], ['rgba(0,0,0,0.6)', 1]]
        })
      }
      .width('100%')
      .height('100%')
      .borderRadius(12)

      // 顶层：折扣角标（左上角）
      if (this.discountLabel.length > 0) {
        Text(this.discountLabel)
          .fontSize(12)
          .fontColor(Color.White)
          .backgroundColor('#FF4D4F')
          .borderRadius({ topLeft: 12, bottomRight: 8 })
          .padding({ left: 8, right: 8, top: 4, bottom: 4 })
      }

      // 顶层："新品" 标记（右上角）
      if (this.isNew) {
        Text('NEW')
          .fontSize(10)
          .fontWeight(FontWeight.Bold)
          .fontColor(Color.White)
          .backgroundColor('#52C41A')
          .borderRadius(4)
          .padding({ left: 6, right: 6, top: 2, bottom: 2 })
          .position({ x: '85%', y: 8 })
      }
    }
    .width('100%')
    .height(200)
    .alignContent(Alignment.TopStart)
  }
}
```

**Stack 关键属性：**

| 属性 | 类型 | 说明 |
|------|------|------|
| `alignContent` | `Alignment` | 子元素默认对齐位置（9 宫格方位） |

> Stack 中后声明的元素在上层（z-index 更高）。可对单个子元素使用 `.position()` 做绝对定位。

---

## 4. Flex — 标签自动换行布局

<!-- 适用场景：灵活的换行/排列，如标签/芯片云、自适应按钮组、不等宽元素自动排列。 -->

```typescript
// 弹性布局：标签/芯片自动换行（V2）
@Entry
import { LengthMetrics } from '@kit.ArkUI'  // Flex 的 space 用 LengthMetrics.vp(n)（值）必须 import，否则报 'LengthMetrics only refers to a type, but is being used as a value'

@ComponentV2
struct TagCloudPage {
  @Local selectedTags: string[] = []
  private allTags: string[] = [
    '科技', '教育', '医疗健康', '金融理财', '游戏',
    '社交', '音乐', '旅行', '美食', '运动健身',
    '摄影', '阅读', '编程', 'AI', '设计'
  ]

  build() {
    Column({ space: 16 }) {
      Text('选择你感兴趣的标签')
        .fontSize(20)
        .fontWeight(FontWeight.Bold)

      Text(`已选择 ${this.selectedTags.length} 个`)
        .fontSize(14)
        .fontColor('#999')

      // Flex 自动换行容器
      Flex({
        direction: FlexDirection.Row,
        wrap: FlexWrap.Wrap,
        justifyContent: FlexAlign.Start,
        alignItems: ItemAlign.Center,
        space: { main: LengthMetrics.vp(8), cross: LengthMetrics.vp(10) }
      }) {
        ForEach(this.allTags, (tag: string) => {
          Text(tag)
            .fontSize(14)
            .fontColor(this.selectedTags.includes(tag) ? Color.White : '#333')
            .backgroundColor(this.selectedTags.includes(tag) ? '#007DFF' : '#F0F0F0')
            .borderRadius(20)
            .padding({ left: 16, right: 16, top: 8, bottom: 8 })
            .border({
              width: 1,
              color: this.selectedTags.includes(tag) ? '#007DFF' : '#E0E0E0'
            })
            .onClick(() => {
              if (this.selectedTags.includes(tag)) {
                this.selectedTags = this.selectedTags.filter(t => t !== tag)
              } else {
                this.selectedTags = [...this.selectedTags, tag]
              }
            })
            .animation({ duration: 200 })
        }, (tag: string) => tag)
      }
      .width('100%')

      Button('确认选择', { type: ButtonType.Capsule })
        .width('100%')
        .height(44)
        .margin({ top: 24 })
        .enabled(this.selectedTags.length > 0)
    }
    .width('100%')
    .height('100%')
    .padding(20)
  }
}
```

> **Flex vs Row/Column：** 仅当需要 `wrap` 换行或复杂弹性布局时才用 Flex。简单横/竖排优先用 Row/Column，性能更好。

---

## 5. Grid + GridItem — 商品网格布局

<!-- 适用场景：固定列数的网格排列，如商品列表、照片墙、功能菜单九宫格。 -->

```typescript
// 网格布局：2 列商品展示（V2 + @ObservedV2）
interface Product {
  id: number
  productName: string
  productPrice: number
  imageUrl: string
  salesCount: number
}

@Entry
@ComponentV2
struct ProductGrid {
  @Local products: Product[] = [
    { id: 1, productName: '无线蓝牙耳机', productPrice: 299, imageUrl: '/common/img/p1.png', salesCount: 1234 },
    { id: 2, productName: '智能手表', productPrice: 599, imageUrl: '/common/img/p2.png', salesCount: 856 },
    { id: 3, productName: '便携充电宝', productPrice: 129, imageUrl: '/common/img/p3.png', salesCount: 3421 },
    { id: 4, productName: '机械键盘', productPrice: 459, imageUrl: '/common/img/p4.png', salesCount: 672 }
  ]

  build() {
    Column() {
      Text('热门商品')
        .fontSize(20)
        .fontWeight(FontWeight.Bold)
        .width('100%')
        .padding({ left: 16, top: 16, bottom: 12 })

      Grid() {
        ForEach(this.products, (product: Product) => {
          GridItem() {
            Column() {
              Image(product.imageUrl)
                .width('100%')
                .height(160)
                .objectFit(ImageFit.Cover)
                .borderRadius({ topLeft: 8, topRight: 8 })

              Column() {
                Text(product.productName)
                  .fontSize(14)
                  .fontColor('#333')
                  .maxLines(2)
                  .textOverflow({ overflow: TextOverflow.Ellipsis })
                  .lineHeight(20)

                Row() {
                  Text(`¥${product.productPrice}`)
                    .fontSize(18)
                    .fontWeight(FontWeight.Bold)
                    .fontColor('#FF4D4F')
                  Blank()
                  Text(`${product.salesCount}人付款`)
                    .fontSize(11)
                    .fontColor('#999')
                }
                .width('100%')
                .alignItems(VerticalAlign.Bottom)
                .margin({ top: 8 })
              }
              .width('100%')
              .padding(10)
              .alignItems(HorizontalAlign.Start)
            }
            .backgroundColor(Color.White)
            .borderRadius(8)
            .shadow({ radius: 4, color: 'rgba(0,0,0,0.06)', offsetX: 0, offsetY: 1 })
          }
        }, (product: Product) => product.id.toString())
      }
      .columnsTemplate('1fr 1fr')
      .rowsGap(12)
      .columnsGap(12)
      .padding({ left: 12, right: 12 })
      .width('100%')
      .layoutWeight(1)
    }
    .width('100%')
    .height('100%')
    .backgroundColor('#F5F5F5')
  }
}
```

**Grid 关键属性：**

| 属性 | 类型 | 说明 |
|------|------|------|
| `columnsTemplate` | `string` | 列定义：`'1fr 1fr'` / `'100px 1fr 1fr'` |
| `rowsTemplate` | `string` | 行定义，不设则按内容自动增长 |
| `columnsGap` | `Length` | 列间距 |
| `rowsGap` | `Length` | 行间距 |
| `cachedCount` | `number` | 预加载缓存行数 |

> 不设 `rowsTemplate` 时 Grid 可滚动；同时设了两者则为固定网格不可滚动。

---

## 6. List + ListItem — 消息列表布局

<!-- 适用场景：可滚动的长列表，最常用的列表容器。支持懒加载、分组、滑动操作。 -->

```typescript
// 可滚动消息列表：聊天列表页（V2，@ObservedV2 类）
@ObservedV2
class Message {
  id: string = ''
  @Trace senderName: string = ''
  @Trace senderAvatar: string = ''
  @Trace content: string = ''
  @Trace timeText: string = ''       // 不用 time（保持业务命名清晰）
  @Trace unreadCount: number = 0
  @Trace isOnline: boolean = false

  // 用构造器逐字段赋值。⚠️ ArkTS 不支持 `Object.assign(new X(), {...})`（arkts-limited-stdlib 报错），
  // 也不要用对象字面量 `{...}` 构造 @ObservedV2 实例（@Trace 观测性需经构造器/new 初始化）。
  constructor(id: string, senderName: string, senderAvatar: string,
              content: string, timeText: string, unreadCount: number, isOnline: boolean) {
    this.id = id
    this.senderName = senderName
    this.senderAvatar = senderAvatar
    this.content = content
    this.timeText = timeText
    this.unreadCount = unreadCount
    this.isOnline = isOnline
  }
}

@Entry
@ComponentV2
struct MessageList {
  @Local messages: Message[] = []

  aboutToAppear(): void {
    // V2 直接构建 @ObservedV2 实例数组——用构造器 new Message(...)，不要用 Object.assign
    this.messages = [
      new Message('1', '张三', '/avatars/a1.png', '明天下午3点开会', '10:30', 2, true),
      new Message('2', '项目组', '/avatars/a2.png', 'review', '09:45', 5, false),
      new Message('3', '王五', '/avatars/a3.png', '吃饭吗？', '昨天', 0, true)
    ]
  }

  build() {
    Column() {
      // 顶部搜索栏
      Search({ placeholder: '搜索' })
        .height(40)
        .margin({ left: 16, right: 16, top: 8, bottom: 8 })

      // 消息列表
      List({ space: 0 }) {
        ForEach(this.messages, (msg: Message) => {
          ListItem() {
            Row() {
              // 头像 + 在线状态
              Stack({ alignContent: Alignment.BottomEnd }) {
                Image(msg.senderAvatar)
                  .width(48)
                  .height(48)
                  .borderRadius(24)
                  .objectFit(ImageFit.Cover)

                if (msg.isOnline) {
                  Circle()
                    .width(12)
                    .height(12)
                    .fill('#52C41A')
                    .stroke(Color.White)
                    .strokeWidth(2)
                }
              }

              // 消息内容
              Column() {
                Row() {
                  Text(msg.senderName)
                    .fontSize(16)
                    .fontWeight(FontWeight.Medium)
                    .fontColor('#333')
                    .layoutWeight(1)

                  Text(msg.timeText)
                    .fontSize(12)
                    .fontColor('#BBB')
                }
                .width('100%')

                Row() {
                  Text(msg.content)
                    .fontSize(14)
                    .fontColor('#999')
                    .maxLines(1)
                    .textOverflow({ overflow: TextOverflow.Ellipsis })
                    .layoutWeight(1)

                  if (msg.unreadCount > 0) {
                    Text(`${msg.unreadCount}`)
                      .fontSize(11)
                      .fontColor(Color.White)
                      .backgroundColor('#FF4D4F')
                      .borderRadius(10)
                      .width(20)
                      .height(20)
                      .textAlign(TextAlign.Center)
                  }
                }
                .width('100%')
                .margin({ top: 6 })
              }
              .layoutWeight(1)
              .margin({ left: 12 })
            }
            .width('100%')
            .padding({ left: 16, right: 16, top: 12, bottom: 12 })
          }
          .swipeAction({
            end: {
              builder: () => {
                this.swipeActionEnd(msg.id)
              }
            }
          })
        }, (msg: Message) => msg.id)  // key 只用稳定业务 id；严禁拼可变字段（unreadCount/online/选中态）——可变字段入 key 会使该项每次变化被【重建】而非更新，致复用错乱/闪烁
      }
      .width('100%')
      .layoutWeight(1)
      .divider({
        strokeWidth: 0.5,
        color: '#F0F0F0',
        startMargin: 76,
        endMargin: 16
      })
      .scrollBar(BarState.Off)
      .edgeEffect(EdgeEffect.Spring)
      .cachedCount(5)
    }
    .width('100%')
    .height('100%')
    .backgroundColor(Color.White)
  }

  @Builder
  swipeActionEnd(itemId: string) {
    Row() {
      Button('删除')
        .fontSize(14)
        .fontColor(Color.White)
        .backgroundColor('#FF4D4F')
        .height('100%')
        .width(80)
        .onClick(() => {
          this.messages = this.messages.filter(m => m.id !== itemId)
        })
    }
    .height('100%')
  }
}
```

**List 关键属性：**

| 属性 | 类型 | 说明 |
|------|------|------|
| `space` | `number` | 列表项间距 |
| `divider` | `object` | 分割线配置 |
| `scrollBar` | `BarState` | 滚动条显示 |
| `edgeEffect` | `EdgeEffect` | 边缘效果：`.Spring` / `.Fade` / `.None` |
| `cachedCount` | `number` | 屏幕外预渲染条数 |
| `listDirection` | `Axis` | 滚动方向 |

> **性能提示：** 大数据列表使用 `LazyForEach` 或 V2 推荐的 `Repeat` 替代 `ForEach`。

---

## V2 大列表新选择：Repeat

```typescript
@ObservedV2
class FeedItem {
  id: string = ''
  @Trace itemTitle: string = ''
  @Trace itemDesc: string = ''
}

@ComponentV2
struct LongFeedList {
  @Local feeds: FeedItem[] = []

  build() {
    List() {
      Repeat<FeedItem>(this.feeds)
        .each((rep: RepeatItem<FeedItem>) => {
          ListItem() {
            Column() {
              Text(rep.item.itemTitle).fontSize(16)
              Text(rep.item.itemDesc).fontSize(13).fontColor('#999')
            }
          }
        })
        .key((item: FeedItem) => item.id)
        .virtualScroll({ totalCount: this.feeds.length })
    }
    .width('100%')
    .layoutWeight(1)
  }
}
```

---

## 7. 自定义布局（onMeasureSize / onPlaceChildren）

当内置容器（Column/Row/Flex/Grid）表达不了你要的测量/摆放逻辑（如「按列各自累计高度」「排满隐藏超出项」「精确接管子元素尺寸」）时，用 `@ComponentV2` 的**自定义布局**回调接管。**onMeasureSize（测量）与 onPlaceChildren（摆放）须成对实现**；子内容经 `@BuilderParam` 传入，组件 `build()` **只放 `this.content()`/`this.builder()`**。

```typescript
@ObservedV2
class CardData {
  @Trace title: string = ''
  @Trace boxHeight: number = 80
  constructor(title: string, boxHeight: number) {
    this.title = title
    this.boxHeight = boxHeight
  }
}

@ComponentV2
struct TwoColumnLayout {
  @Builder emptyContent() {}
  @BuilderParam content: () => void = this.emptyContent
  @Param @Once gap: number = 12

  // 测量：遍历 children 调 child.measure(...) 量尺寸，算容器自身尺寸（SizeResult{width,height}，单位 vp）
  onMeasureSize(selfLayoutInfo: GeometryInfo, children: Array<Measurable>, constraint: ConstraintSizeOptions): SizeResult {
    const avail: number = constraint.maxWidth as number          // ⚠️ 见下「约束是 Length」
    const colWidth: number = (avail - this.gap) / 2
    let leftH: number = 0
    let rightH: number = 0
    children.forEach((child: Measurable, i: number) => {
      const m: MeasureResult = child.measure({
        minWidth: colWidth, maxWidth: colWidth, minHeight: 0, maxHeight: constraint.maxHeight
      })
      if (i % 2 === 0) { leftH += m.height } else { rightH += m.height }
    })
    return { width: avail, height: Math.max(leftH, rightH) }
  }

  // 摆放：逐子 child.layout({x,y}) 定位；child.measureResult 拿测量结果
  onPlaceChildren(selfLayoutInfo: GeometryInfo, children: Array<Layoutable>, constraint: ConstraintSizeOptions): void {
    const avail: number = constraint.maxWidth as number
    const colWidth: number = (avail - this.gap) / 2
    let leftY: number = 0
    let rightY: number = 0
    children.forEach((child: Layoutable, i: number) => {
      const h: number = child.measureResult.height
      if (i % 2 === 0) { child.layout({ x: 0, y: leftY }); leftY += h }
      else { child.layout({ x: colWidth + this.gap, y: rightY }); rightY += h }
    })
  }

  build() {
    this.content()   // 自定义布局组件 build() 内只放 this.content()/this.builder()
  }
}

@Entry
@ComponentV2
struct Index {
  @Local cards: CardData[] = [
    new CardData('A', 70), new CardData('B', 110), new CardData('C', 90), new CardData('D', 60)
  ]
  @Builder
  cardView(c: CardData) {
    Column() { Text(c.title).fontSize(16) }
      .width('100%').height(c.boxHeight).backgroundColor('#E8F0FE').borderRadius(8)
  }
  build() {
    Column() {
      // 给自定义容器加边框 → 外层套内置容器再链式（自定义组件尾随闭包后不能直接链 .border/.width）
      Column() {
        TwoColumnLayout({ gap: 12 }) {
          ForEach(this.cards, (c: CardData) => {
            this.cardView(c)
          }, (c: CardData) => c.title)   // 自定义布局内只能 ForEach，禁 Repeat/LazyForEach
        }
      }
      .width('100%').padding(12).border({ width: 1, color: '#CCCCCC' })
    }
    .width('100%').height('100%').padding(16)
  }
}
```

**自定义布局四条硬规则**（`onMeasureSize`/`onPlaceChildren`/`Measurable`/`Layoutable`/`SizeResult`/`GeometryInfo`/`ConstraintSizeOptions`/`MeasureResult` 都是 ArkUI ambient 类型，**不 import**）：

1. **约束字段是 `Length`、不是 number**：`constraint.maxWidth / minWidth / maxHeight / minHeight` 类型是 `Length`（`string | number | Resource`）。**要参与算术/比较时用 `as number` 收窄**——`const avail: number = constraint.maxWidth as number`（官方范式 `Math.min(200, constraint.maxWidth as number)`）。**不要**自写形参为 `string | number` 的 `toPx()` 辅助去转它（`Resource` 不在 `string|number` 里 → 报 `Type 'Resource' is not assignable to type 'string | number'`）。把 `constraint.maxHeight` 原样回传给 `child.measure({...})` 则无需转（同是 `ConstraintSizeOptions` 字段）。
2. **build() 只放 `this.content()`**（或 `this.builder()`）——子项一律经 `@BuilderParam` 传入，不在 build() 里堆别的容器。
3. **自定义布局内禁懒加载**：子项渲染只能用 `ForEach`，**不能** `Repeat` / `LazyForEach`（框架不支持）。
4. **加通用属性套容器**：给自定义容器加 `.border/.width/.backgroundColor` 时，外层套一层内置容器（`Column(){ MyLayout(){...} }.border(...)`）——自定义组件尾随闭包后直接链式会报 `Cannot find name 'width'`（详见 `v2-codegen-patterns.md` §@BuilderParam 链式坑）。

> 旧 API `onMeasure`/`onLayout`（API 9）已废弃，统一用 `onMeasureSize`/`onPlaceChildren`（API 10+）。

---

## 布局选择速查表

| 场景 | 推荐容器 | 原因 |
|------|----------|------|
| 简单纵向排列 | `Column` | 最简单，性能最好 |
| 简单横向排列 | `Row` | 最简单，性能最好 |
| 元素重叠/叠加 | `Stack` | 专为重叠设计 |
| 自动换行标签 | `Flex({ wrap: FlexWrap.Wrap })` | 唯一支持自动换行的容器 |
| 固定列数网格 | `Grid` | 自动处理行列排列 |
| 长列表/滚动 | `List` | 支持懒加载、滑动操作 |
| 大列表 V2 推荐 | `List + Repeat` | V2 友好的虚拟列表 |
| 瀑布流 | `WaterFlow` | 不等高网格 |

---

## 跨文档参考

- [`v2-common-components.md`](./v2-common-components.md) — V2 常用组件用法
- [`v2-prop-naming-rules.md`](./v2-prop-naming-rules.md) — V2 变量命名规则
- [`v2-responsive-design.md`](./v2-responsive-design.md) — V2 响应式断点
- `../SKILL.md` — V2 组件骨架
