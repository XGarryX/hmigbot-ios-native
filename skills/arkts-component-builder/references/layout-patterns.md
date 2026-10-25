# ArkTS 布局容器完整模板（**V1 历史文档 — Legacy**）

> ⚠️ **本项目锁 ArkTS V2**。本文档示例采用 **V1 装饰器写法**（`@Component / @State / @Prop`），仅用于阅读老代码或迁移老项目时查阅。
>
> **新代码请使用 V2 装饰器**：参阅 [`v2-layout-patterns.md`](./v2-layout-patterns.md)（V2 主参考，使用 `@ComponentV2 / @Local / @Param`）。

> 本文档为 LLM 提供 6 种核心布局容器的完整代码模板，可直接复制使用。

---

## 1. Column — 垂直表单布局

<!-- 适用场景：需要从上到下排列元素时使用，最常见于登录/注册表单、设置页面、信息展示列表。 -->

```typescript
// 垂直表单布局：登录页面
@Entry
@Component
struct LoginForm {
  @State username: string = ''
  @State password: string = ''
  @State isLoading: boolean = false

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
      TextInput({ placeholder: '请输入用户名' })
        .type(InputType.Normal)
        .height(48)
        .width('100%')
        .margin({ bottom: 16 })
        .onChange((value: string) => {
          this.username = value
        })

      // 密码输入框
      TextInput({ placeholder: '请输入密码' })
        .type(InputType.Password)
        .height(48)
        .width('100%')
        .margin({ bottom: 24 })
        .onChange((value: string) => {
          this.password = value
        })

      // 登录按钮
      Button('登录', { type: ButtonType.Capsule })
        .width('100%')
        .height(48)
        .backgroundColor('#007DFF')
        .onClick(() => {
          this.isLoading = true
        })

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
    // Column 关键属性
    .alignItems(HorizontalAlign.Center) // 水平对齐：Start | Center | End
    .justifyContent(FlexAlign.Start)    // 垂直分布：Start | Center | End | SpaceBetween | SpaceAround | SpaceEvenly
  }
}
```

**Column 关键属性：**

| 属性 | 类型 | 说明 |
|------|------|------|
| `alignItems` | `HorizontalAlign` | 子元素水平对齐：`.Start` / `.Center` / `.End` |
| `justifyContent` | `FlexAlign` | 子元素垂直分布方式 |
| `space` | `number \| string` | 子元素间距（统一间距，替代逐个设 margin） |

---

## 2. Row — 水平卡片布局

<!-- 适用场景：需要横向排列元素时使用，如卡片内的图片+文字信息、工具栏按钮组、底部导航。 -->

```typescript
// 水平卡片：用户信息卡
@Component
struct UserCard {
  @Prop userName: string = ''
  @Prop userDesc: string = ''
  @Prop avatarUrl: string = ''
  @Prop tags: string[] = []

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
          })
        }
        .margin({ top: 6 })
      }
      .layoutWeight(1) // 关键：占满剩余空间
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
    .shadow({
      radius: 8,
      color: 'rgba(0,0,0,0.08)',
      offsetX: 0,
      offsetY: 2
    })
    // Row 关键属性
    .alignItems(VerticalAlign.Center)  // 垂直对齐：Top | Center | Bottom
    .justifyContent(FlexAlign.Start)   // 水平分布方式
  }
}
```

**Row 关键属性：**

| 属性 | 类型 | 说明 |
|------|------|------|
| `alignItems` | `VerticalAlign` | 子元素垂直对齐：`.Top` / `.Center` / `.Bottom` |
| `justifyContent` | `FlexAlign` | 子元素水平分布方式 |
| `space` | `number \| string` | 子元素间距 |

> **注意：** `layoutWeight(1)` 是 Row 中最常用的技巧，让某个子元素占满剩余空间。

---

## 3. Stack — 图片叠加层布局

<!-- 适用场景：需要元素重叠显示时使用，如图片上叠加文字/角标、头像上的在线状态标记、浮动按钮。 -->

```typescript
// 堆叠布局：商品图片 + 折扣角标 + 底部渐变文字
@Component
struct ProductImageCard {
  @Prop imageUrl: string = ''
  @Prop title: string = ''
  @Prop discount: string = ''
  @Prop isNew: boolean = false

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
        Blank() // 占据上方空间，把内容推到底部
        // 底部渐变区域
        Column() {
          Text(this.title)
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
      if (this.discount) {
        Text(this.discount)
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
          .position({ x: '85%', y: 8 }) // 绝对定位到右上角
      }
    }
    .width('100%')
    .height(200)
    // Stack 关键属性
    .alignContent(Alignment.TopStart) // 默认对齐方式，适用于所有子元素
    // Alignment 枚举值：
    // TopStart | Top | TopEnd
    // Start    | Center | End
    // BottomStart | Bottom | BottomEnd
  }
}
```

**Stack 关键属性：**

| 属性 | 类型 | 说明 |
|------|------|------|
| `alignContent` | `Alignment` | 子元素默认对齐位置（9 宫格方位） |

> **注意：** Stack 中后声明的元素在上层（z-index 更高）。可对单个子元素使用 `.position()` 做绝对定位。

---

## 4. Flex — 标签自动换行布局

<!-- 适用场景：需要灵活的换行/排列时使用，如标签/芯片云、自适应按钮组、不等宽元素的自动排列。 -->

```typescript
// 弹性布局：标签/芯片自动换行
@Entry
@Component
struct TagCloudPage {
  @State selectedTags: string[] = []
  private allTags: string[] = [
    '科技', '教育', '医疗健康', '金融理财', '游戏',
    '社交', '音乐', '旅行', '美食', '运动健身',
    '摄影', '阅读', '编程', 'AI', '设计',
    '电影', '动漫', '户外探险'
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
        direction: FlexDirection.Row,  // 主轴方向
        wrap: FlexWrap.Wrap,           // 关键：允许换行
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
        })
      }
      .width('100%')

      // 底部确认按钮
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

**Flex 关键属性（构造参数）：**

| 属性 | 类型 | 说明 |
|------|------|------|
| `direction` | `FlexDirection` | `.Row` / `.RowReverse` / `.Column` / `.ColumnReverse` |
| `wrap` | `FlexWrap` | `.NoWrap`（默认不换行）/ `.Wrap` / `.WrapReverse` |
| `justifyContent` | `FlexAlign` | 主轴分布 |
| `alignItems` | `ItemAlign` | 交叉轴对齐 |
| `alignContent` | `FlexAlign` | 多行时行间分布（仅 Wrap 时生效） |
| `space` | `FlexSpaceOptions` | 主轴和交叉轴间距 |

> **Flex vs Row/Column：** 仅当需要 `wrap` 换行或复杂弹性布局时才用 Flex。简单横/竖排优先用 Row/Column，性能更好。

---

## 5. Grid + GridItem — 商品网格布局

<!-- 适用场景：需要固定列数的网格排列时使用，如商品列表、照片墙、功能菜单九宫格。 -->

```typescript
// 网格布局：2 列商品展示
interface Product {
  id: number
  name: string
  price: number
  imageUrl: string
  sales: number
}

@Entry
@Component
struct ProductGrid {
  @State products: Product[] = [
    { id: 1, name: '无线蓝牙耳机', price: 299, imageUrl: '/common/img/p1.png', sales: 1234 },
    { id: 2, name: '智能手表', price: 599, imageUrl: '/common/img/p2.png', sales: 856 },
    { id: 3, name: '便携充电宝', price: 129, imageUrl: '/common/img/p3.png', sales: 3421 },
    { id: 4, name: '机械键盘', price: 459, imageUrl: '/common/img/p4.png', sales: 672 },
    { id: 5, name: '显示器支架', price: 189, imageUrl: '/common/img/p5.png', sales: 445 },
    { id: 6, name: 'Type-C 扩展坞', price: 259, imageUrl: '/common/img/p6.png', sales: 998 }
  ]

  build() {
    Column() {
      // 顶部标题栏
      Text('热门商品')
        .fontSize(20)
        .fontWeight(FontWeight.Bold)
        .width('100%')
        .padding({ left: 16, top: 16, bottom: 12 })

      // 2 列商品网格
      Grid() {
        ForEach(this.products, (product: Product) => {
          GridItem() {
            Column() {
              // 商品图片
              Image(product.imageUrl)
                .width('100%')
                .height(160)
                .objectFit(ImageFit.Cover)
                .borderRadius({ topLeft: 8, topRight: 8 })

              // 商品信息
              Column() {
                Text(product.name)
                  .fontSize(14)
                  .fontColor('#333')
                  .maxLines(2)
                  .textOverflow({ overflow: TextOverflow.Ellipsis })
                  .lineHeight(20)

                Row() {
                  Text(`¥${product.price}`)
                    .fontSize(18)
                    .fontWeight(FontWeight.Bold)
                    .fontColor('#FF4D4F')
                  Blank()
                  Text(`${product.sales}人付款`)
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
            .shadow({
              radius: 4,
              color: 'rgba(0,0,0,0.06)',
              offsetX: 0,
              offsetY: 1
            })
          }
        }, (product: Product) => product.id.toString())
      }
      // Grid 关键属性
      .columnsTemplate('1fr 1fr')      // 2 列等宽；3 列用 '1fr 1fr 1fr'
      .rowsGap(12)                       // 行间距
      .columnsGap(12)                    // 列间距
      .padding({ left: 12, right: 12 })
      .width('100%')
      .layoutWeight(1)
      // 可选：固定行高
      // .rowsTemplate('1fr 1fr 1fr')   // 指定行数和比例
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
| `columnsTemplate` | `string` | 列定义：`'1fr 1fr'`（2等列）、`'100px 1fr 1fr'`（首列固定）|
| `rowsTemplate` | `string` | 行定义，不设则按内容自动增长 |
| `columnsGap` | `Length` | 列间距 |
| `rowsGap` | `Length` | 行间距 |
| `scrollBar` | `BarState` | 滚动条：`.Off` / `.Auto` / `.On` |
| `cachedCount` | `number` | 预加载缓存行数 |

> **注意：** 不设 `rowsTemplate` 时 Grid 可滚动；同时设了 `columnsTemplate` 和 `rowsTemplate` 则为固定网格不可滚动。

---

## 6. List + ListItem — 消息列表布局

<!-- 适用场景：需要可滚动的长列表时使用，是最常用的列表容器。支持懒加载、分组、滑动操作等。 -->

```typescript
// 可滚动消息列表：聊天列表页
interface Message {
  id: string
  senderName: string
  senderAvatar: string
  content: string
  time: string
  unreadCount: number
  isOnline: boolean
}

@Entry
@Component
struct MessageList {
  @State messages: Message[] = [
    { id: '1', senderName: '张三', senderAvatar: '/avatars/a1.png',
      content: '明天下午3点开会，记得准时参加', time: '10:30', unreadCount: 2, isOnline: true },
    { id: '2', senderName: '项目组', senderAvatar: '/avatars/a2.png',
      content: '李四：代码已经提交了，请帮忙 review', time: '09:45', unreadCount: 5, isOnline: false },
    { id: '3', senderName: '王五', senderAvatar: '/avatars/a3.png',
      content: '周末一起吃饭吗？', time: '昨天', unreadCount: 0, isOnline: true },
    { id: '4', senderName: '系统通知', senderAvatar: '/avatars/sys.png',
      content: '您的订单已发货，预计明天送达', time: '昨天', unreadCount: 1, isOnline: false }
  ]

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

                  Text(msg.time)
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
          // ListItem 滑动操作
          .swipeAction({
            end: {
              builder: () => {
                this.swipeActionEnd(msg.id)
              }
            }
          })
        }, (msg: Message) => msg.id)
      }
      // List 关键属性
      .width('100%')
      .layoutWeight(1)
      .divider({
        strokeWidth: 0.5,
        color: '#F0F0F0',
        startMargin: 76, // 头像宽度 + 间距，让分割线不覆盖头像
        endMargin: 16
      })
      .scrollBar(BarState.Off)
      .edgeEffect(EdgeEffect.Spring) // 弹性回弹效果
      .cachedCount(5)                // 预加载 5 条
    }
    .width('100%')
    .height('100%')
    .backgroundColor(Color.White)
  }

  // 滑动删除按钮
  @Builder
  swipeActionEnd(id: string) {
    Row() {
      Button('删除')
        .fontSize(14)
        .fontColor(Color.White)
        .backgroundColor('#FF4D4F')
        .height('100%')
        .width(80)
        .onClick(() => {
          this.messages = this.messages.filter(m => m.id !== id)
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
| `divider` | `object` | 分割线配置：`strokeWidth`、`color`、`startMargin`、`endMargin` |
| `scrollBar` | `BarState` | 滚动条显示：`.Off` / `.Auto` / `.On` |
| `edgeEffect` | `EdgeEffect` | 边缘效果：`.Spring`（回弹）/ `.Fade`（渐隐）/ `.None` |
| `cachedCount` | `number` | 屏幕外预渲染条数，提升滚动流畅度 |
| `listDirection` | `Axis` | 滚动方向：`.Vertical`（默认）/ `.Horizontal` |

> **性能提示：** 大数据列表使用 `LazyForEach` 替代 `ForEach` 实现按需渲染，需搭配 `IDataSource` 接口。

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
| 瀑布流 | `WaterFlow` | 不等高网格 |
