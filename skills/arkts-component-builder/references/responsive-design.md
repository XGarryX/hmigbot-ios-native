# ArkTS 响应式设计参考（**V1 历史文档 — Legacy**）

> ⚠️ **本项目锁 ArkTS V2**。本文档示例采用 **V1 装饰器写法**（`@Component / @State / @StorageProp`），仅用于阅读老代码或迁移老项目时查阅。
>
> **新代码请使用 V2 装饰器**：参阅 [`v2-responsive-design.md`](./v2-responsive-design.md)（V2 主参考，使用 `@ComponentV2 / @Local / AppStorageV2.connect`）。

> 本文档为 LLM 提供 HarmonyOS ArkTS 响应式设计的完整模板和最佳实践。

---

## 1. 断点系统概述

HarmonyOS 定义了三个标准断点：

| 断点 | 宽度范围 | 典型设备 |
|------|----------|----------|
| `sm` | [0, 320vp) ~ [0, 600vp) | 手机竖屏 |
| `md` | [600vp, 840vp) | 折叠屏展开、平板竖屏 |
| `lg` | >= 840vp | 平板横屏、2in1 设备 |

> 注意：具体断点阈值可根据应用场景自行定义，上表为推荐值。

---

## 2. 使用 MediaQuery 监听断点

```typescript
// 断点常量定义
// 建议放在公共文件中复用，如 common/constants/Breakpoints.ets
export class BreakpointConstants {
  static readonly SM: string = 'sm'
  static readonly MD: string = 'md'
  static readonly LG: string = 'lg'

  // 断点阈值
  static readonly BREAKPOINT_SM: number = 320
  static readonly BREAKPOINT_MD: number = 600
  static readonly BREAKPOINT_LG: number = 840
}
```

### 方式一：在 AbilityStage / EntryAbility 中统一监听

```typescript
// EntryAbility.ets — 在 Ability 生命周期中注册断点监听
import { AbilityConstant, UIAbility, Want } from '@kit.AbilityKit'
import { mediaquery, window } from '@kit.ArkUI'

export default class EntryAbility extends UIAbility {
  private smListener?: mediaquery.MediaQueryListener
  private mdListener?: mediaquery.MediaQueryListener
  private lgListener?: mediaquery.MediaQueryListener

  onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void {
    // 初始化断点监听
    this.smListener = mediaquery.matchMediaSync('(width < 600vp)')
    this.mdListener = mediaquery.matchMediaSync('(600vp <= width < 840vp)')
    this.lgListener = mediaquery.matchMediaSync('(840vp <= width)')

    this.smListener.on('change', (result: mediaquery.MediaQueryResult) => {
      if (result.matches) {
        AppStorage.setOrCreate('currentBreakpoint', 'sm')
      }
    })
    this.mdListener.on('change', (result: mediaquery.MediaQueryResult) => {
      if (result.matches) {
        AppStorage.setOrCreate('currentBreakpoint', 'md')
      }
    })
    this.lgListener.on('change', (result: mediaquery.MediaQueryResult) => {
      if (result.matches) {
        AppStorage.setOrCreate('currentBreakpoint', 'lg')
      }
    })
  }

  onWindowStageCreate(windowStage: window.WindowStage): void {
    // 设置默认断点
    AppStorage.setOrCreate('currentBreakpoint', 'sm')
    windowStage.loadContent('pages/Index')
  }
}
```

### 方式二：封装 BreakpointSystem 工具类

```typescript
// common/utils/BreakpointSystem.ets
// 可复用的断点管理类，在页面 aboutToAppear 中注册
import { mediaquery } from '@kit.ArkUI'

export class BreakpointType<T> {
  sm: T
  md: T
  lg: T

  constructor(sm: T, md: T, lg: T) {
    this.sm = sm
    this.md = md
    this.lg = lg
  }

  // 根据当前断点返回对应值
  getValue(breakpoint: string): T {
    if (breakpoint === 'md') {
      return this.md
    } else if (breakpoint === 'lg') {
      return this.lg
    } else {
      return this.sm
    }
  }
}

export class BreakpointSystem {
  private smListener?: mediaquery.MediaQueryListener
  private mdListener?: mediaquery.MediaQueryListener
  private lgListener?: mediaquery.MediaQueryListener

  // 注册断点监听，写入 AppStorage
  register(): void {
    this.smListener = mediaquery.matchMediaSync('(width < 600vp)')
    this.mdListener = mediaquery.matchMediaSync('(600vp <= width < 840vp)')
    this.lgListener = mediaquery.matchMediaSync('(840vp <= width)')

    this.smListener.on('change', (result: mediaquery.MediaQueryResult) => {
      if (result.matches) {
        AppStorage.setOrCreate('currentBreakpoint', 'sm')
      }
    })
    this.mdListener.on('change', (result: mediaquery.MediaQueryResult) => {
      if (result.matches) {
        AppStorage.setOrCreate('currentBreakpoint', 'md')
      }
    })
    this.lgListener.on('change', (result: mediaquery.MediaQueryResult) => {
      if (result.matches) {
        AppStorage.setOrCreate('currentBreakpoint', 'lg')
      }
    })
  }

  // 取消注册
  unregister(): void {
    this.smListener?.off('change')
    this.mdListener?.off('change')
    this.lgListener?.off('change')
  }
}
```

---

## 3. 使用 @StorageProp 读取断点状态

```typescript
// 在任意组件中通过 @StorageProp 获取当前断点
@Entry
@Component
struct ResponsivePage {
  // 从 AppStorage 读取断点值，默认 'sm'
  @StorageProp('currentBreakpoint') currentBreakpoint: string = 'sm'

  build() {
    Column() {
      Text(`当前断点: ${this.currentBreakpoint}`)
        .fontSize(16)
        .fontColor('#999')

      // 根据断点动态调整布局
      if (this.currentBreakpoint === 'sm') {
        // 手机：单列布局
        this.phoneLayout()
      } else if (this.currentBreakpoint === 'md') {
        // 平板竖屏：双列布局
        this.tabletLayout()
      } else {
        // 大屏：三列布局
        this.desktopLayout()
      }
    }
    .width('100%')
    .height('100%')
  }

  @Builder
  phoneLayout() {
    Column({ space: 12 }) {
      ForEach(this.getItems(), (item: string) => {
        Text(item)
          .width('100%')
          .height(80)
          .backgroundColor('#F0F0F0')
          .borderRadius(8)
          .textAlign(TextAlign.Center)
      })
    }
    .padding(16)
  }

  @Builder
  tabletLayout() {
    Grid() {
      ForEach(this.getItems(), (item: string) => {
        GridItem() {
          Text(item)
            .width('100%')
            .height(80)
            .backgroundColor('#F0F0F0')
            .borderRadius(8)
            .textAlign(TextAlign.Center)
        }
      })
    }
    .columnsTemplate('1fr 1fr')
    .columnsGap(12)
    .rowsGap(12)
    .padding(16)
  }

  @Builder
  desktopLayout() {
    Grid() {
      ForEach(this.getItems(), (item: string) => {
        GridItem() {
          Text(item)
            .width('100%')
            .height(80)
            .backgroundColor('#F0F0F0')
            .borderRadius(8)
            .textAlign(TextAlign.Center)
        }
      })
    }
    .columnsTemplate('1fr 1fr 1fr')
    .columnsGap(12)
    .rowsGap(12)
    .padding(24)
  }

  private getItems(): string[] {
    return ['卡片 1', '卡片 2', '卡片 3', '卡片 4', '卡片 5', '卡片 6']
  }
}
```

---

## 4. Grid 响应式列数

通过 `columnsTemplate` 直接绑定断点实现自适应列数，这是最常用的响应式模式。

```typescript
// 响应式商品网格：sm=1列, md=2列, lg=3列
@Entry
@Component
struct ResponsiveGrid {
  @StorageProp('currentBreakpoint') currentBreakpoint: string = 'sm'

  // 根据断点计算列模板
  getColumnsTemplate(): string {
    switch (this.currentBreakpoint) {
      case 'lg':
        return '1fr 1fr 1fr'   // 3 列
      case 'md':
        return '1fr 1fr'       // 2 列
      default:
        return '1fr'           // 1 列
    }
  }

  // 根据断点计算边距
  getPadding(): number {
    switch (this.currentBreakpoint) {
      case 'lg':
        return 32
      case 'md':
        return 24
      default:
        return 16
    }
  }

  build() {
    Column() {
      // 标题栏（响应式字号）
      Text('商品列表')
        .fontSize(this.currentBreakpoint === 'sm' ? 20 : 24)
        .fontWeight(FontWeight.Bold)
        .width('100%')
        .padding({ left: this.getPadding(), top: 16, bottom: 12 })

      // 响应式网格
      Grid() {
        ForEach(this.getProducts(), (product: ProductItem) => {
          GridItem() {
            this.productCard(product)
          }
        }, (product: ProductItem) => product.id.toString())
      }
      .columnsTemplate(this.getColumnsTemplate())
      .columnsGap(12)
      .rowsGap(12)
      .padding({ left: this.getPadding(), right: this.getPadding() })
      .width('100%')
      .layoutWeight(1)
    }
    .width('100%')
    .height('100%')
    .backgroundColor('#F5F5F5')
  }

  @Builder
  productCard(product: ProductItem) {
    Column() {
      Image(product.imageUrl)
        .width('100%')
        .aspectRatio(this.currentBreakpoint === 'sm' ? 2.5 : 1.2)
        .objectFit(ImageFit.Cover)
        .borderRadius({ topLeft: 8, topRight: 8 })

      Column() {
        Text(product.name)
          .fontSize(14)
          .maxLines(2)
          .textOverflow({ overflow: TextOverflow.Ellipsis })

        Text(`¥${product.price}`)
          .fontSize(18)
          .fontWeight(FontWeight.Bold)
          .fontColor('#FF4D4F')
          .margin({ top: 8 })
      }
      .padding(12)
      .alignItems(HorizontalAlign.Start)
      .width('100%')
    }
    .backgroundColor(Color.White)
    .borderRadius(8)
  }

  private getProducts(): ProductItem[] {
    return [
      { id: 1, name: '无线耳机', price: 299, imageUrl: '/common/p1.png' },
      { id: 2, name: '智能手表', price: 599, imageUrl: '/common/p2.png' },
      { id: 3, name: '充电宝', price: 129, imageUrl: '/common/p3.png' },
      { id: 4, name: '键盘', price: 459, imageUrl: '/common/p4.png' },
      { id: 5, name: '鼠标', price: 199, imageUrl: '/common/p5.png' },
      { id: 6, name: '扩展坞', price: 259, imageUrl: '/common/p6.png' }
    ]
  }
}

interface ProductItem {
  id: number
  name: string
  price: number
  imageUrl: string
}
```

---

## 5. GridRow/GridCol 栅格系统

ArkTS 还提供了类似 Bootstrap 的 12 栏栅格系统：

```typescript
// 使用 GridRow/GridCol 实现响应式表单布局
@Entry
@Component
struct ResponsiveForm {
  @State username: string = ''
  @State email: string = ''
  @State phone: string = ''
  @State address: string = ''

  build() {
    Scroll() {
      GridRow({
        columns: 12,                           // 总栏数
        gutter: { x: 12, y: 16 },              // 列间距、行间距
        breakpoints: {
          value: ['600vp', '840vp'],            // 断点阈值
          reference: BreakpointsReference.WindowSize
        }
      }) {
        // 标题：始终占满整行
        GridCol({ span: 12 }) {
          Text('用户注册')
            .fontSize(24)
            .fontWeight(FontWeight.Bold)
            .margin({ bottom: 8 })
        }

        // 用户名：sm 占 12 栏（满行），md 占 6 栏（半行），lg 占 4 栏（1/3 行）
        GridCol({ span: { sm: 12, md: 6, lg: 4 } }) {
          Column({ space: 4 }) {
            Text('用户名').fontSize(14).fontColor('#666')
            TextInput({ placeholder: '请输入用户名' })
              .height(44)
              .onChange((v: string) => { this.username = v })
          }
          .alignItems(HorizontalAlign.Start)
          .width('100%')
        }

        // 邮箱
        GridCol({ span: { sm: 12, md: 6, lg: 4 } }) {
          Column({ space: 4 }) {
            Text('邮箱').fontSize(14).fontColor('#666')
            TextInput({ placeholder: '请输入邮箱' })
              .type(InputType.Email)
              .height(44)
              .onChange((v: string) => { this.email = v })
          }
          .alignItems(HorizontalAlign.Start)
          .width('100%')
        }

        // 手机
        GridCol({ span: { sm: 12, md: 6, lg: 4 } }) {
          Column({ space: 4 }) {
            Text('手机号').fontSize(14).fontColor('#666')
            TextInput({ placeholder: '请输入手机号' })
              .type(InputType.PhoneNumber)
              .height(44)
              .onChange((v: string) => { this.phone = v })
          }
          .alignItems(HorizontalAlign.Start)
          .width('100%')
        }

        // 地址：始终占满整行
        GridCol({ span: 12 }) {
          Column({ space: 4 }) {
            Text('详细地址').fontSize(14).fontColor('#666')
            TextInput({ placeholder: '请输入详细地址' })
              .height(44)
              .onChange((v: string) => { this.address = v })
          }
          .alignItems(HorizontalAlign.Start)
          .width('100%')
        }

        // 提交按钮：sm 占满，md/lg 右对齐占部分
        GridCol({
          span: { sm: 12, md: 6, lg: 4 },
          offset: { sm: 0, md: 6, lg: 8 }   // offset 让按钮靠右
        }) {
          Button('提交注册', { type: ButtonType.Capsule })
            .width('100%')
            .height(44)
            .backgroundColor('#007DFF')
        }
      }
      .padding(16)
    }
    .width('100%')
    .height('100%')
    .backgroundColor('#F5F5F5')
  }
}
```

**GridRow/GridCol 关键属性：**

| 组件 | 属性 | 说明 |
|------|------|------|
| `GridRow` | `columns` | 总栏数（默认 12） |
| `GridRow` | `gutter` | 间距 `{ x: 列间距, y: 行间距 }` |
| `GridRow` | `breakpoints` | 断点阈值和参考 |
| `GridCol` | `span` | 跨栏数，可按断点设：`{ sm: 12, md: 6, lg: 4 }` |
| `GridCol` | `offset` | 左侧偏移栏数，可按断点设 |
| `GridCol` | `order` | 排列顺序，可按断点设（改变元素显示顺序） |

---

## 6. 折叠屏适配

折叠屏设备在展开/折叠时会触发屏幕尺寸变化，可通过断点系统自动适配，也可使用 `display` 接口获取折叠状态。

```typescript
// 折叠屏感知组件
import { display } from '@kit.ArkUI'

@Entry
@Component
struct FoldableAdaptive {
  @StorageProp('currentBreakpoint') currentBreakpoint: string = 'sm'
  @State isFolded: boolean = true
  @State foldStatus: display.FoldStatus = display.FoldStatus.FOLD_STATUS_UNKNOWN

  aboutToAppear(): void {
    // 监听折叠状态变化
    display.on('foldStatusChange', (status: display.FoldStatus) => {
      this.foldStatus = status
      this.isFolded = (status === display.FoldStatus.FOLD_STATUS_FOLDED)
    })

    // 获取初始折叠状态
    if (display.isFoldable()) {
      this.foldStatus = display.getFoldStatus()
      this.isFolded = (this.foldStatus === display.FoldStatus.FOLD_STATUS_FOLDED)
    }
  }

  aboutToDisappear(): void {
    display.off('foldStatusChange')
  }

  build() {
    Column() {
      // 根据折叠状态选择布局
      if (this.isFolded) {
        // 折叠态：单列紧凑布局
        this.compactLayout()
      } else {
        // 展开态：左右分栏布局
        this.expandedLayout()
      }
    }
    .width('100%')
    .height('100%')
  }

  // 折叠态：类似手机的紧凑布局
  @Builder
  compactLayout() {
    Column() {
      // 顶部导航
      Row() {
        Text('我的应用')
          .fontSize(20)
          .fontWeight(FontWeight.Bold)
        Blank()
        Image($r('sys.media.ohos_ic_public_settings'))
          .width(24).height(24)
      }
      .width('100%')
      .padding({ left: 16, right: 16, top: 12, bottom: 12 })

      // 内容列表
      List({ space: 8 }) {
        ForEach(this.getMenuItems(), (item: MenuItem) => {
          ListItem() {
            Row() {
              Image(item.icon)
                .width(40).height(40).borderRadius(8)
              Column() {
                Text(item.title).fontSize(16).fontColor('#333')
                Text(item.subtitle).fontSize(12).fontColor('#999').margin({ top: 2 })
              }
              .alignItems(HorizontalAlign.Start)
              .margin({ left: 12 })
              .layoutWeight(1)
              Image($r('sys.media.ohos_ic_public_arrow_right'))
                .width(20).height(20).fillColor('#CCC')
            }
            .padding(12)
          }
        })
      }
      .width('100%')
      .layoutWeight(1)
      .padding({ left: 16, right: 16 })
    }
  }

  // 展开态：左侧导航 + 右侧详情的分栏布局
  @Builder
  expandedLayout() {
    Row() {
      // 左侧导航面板
      Column() {
        Text('我的应用')
          .fontSize(20)
          .fontWeight(FontWeight.Bold)
          .padding({ left: 16, top: 16, bottom: 16 })
          .width('100%')

        List({ space: 4 }) {
          ForEach(this.getMenuItems(), (item: MenuItem) => {
            ListItem() {
              Row() {
                Image(item.icon)
                  .width(32).height(32).borderRadius(6)
                Text(item.title)
                  .fontSize(15)
                  .margin({ left: 10 })
                  .layoutWeight(1)
              }
              .padding({ left: 16, right: 16, top: 10, bottom: 10 })
              .width('100%')
              .borderRadius(8)
              .backgroundColor(item.selected ? '#E8F0FE' : Color.Transparent)
            }
            .onClick(() => {
              // 处理导航点击
            })
          })
        }
        .width('100%')
        .layoutWeight(1)
      }
      .width(280) // 固定宽度侧边栏
      .height('100%')
      .backgroundColor('#FAFAFA')
      .border({ width: { right: 0.5 }, color: { right: '#E8E8E8' } })

      // 右侧详情面板
      Column() {
        Text('选择一个菜单项查看详情')
          .fontSize(16)
          .fontColor('#999')
      }
      .layoutWeight(1) // 占满剩余空间
      .height('100%')
      .justifyContent(FlexAlign.Center)
      .backgroundColor(Color.White)
    }
    .width('100%')
    .height('100%')
  }

  private getMenuItems(): MenuItem[] {
    return [
      { icon: $r('app.media.ic_home'), title: '首页', subtitle: '查看最新动态', selected: true },
      { icon: $r('app.media.ic_msg'), title: '消息', subtitle: '3 条未读消息', selected: false },
      { icon: $r('app.media.ic_contacts'), title: '通讯录', subtitle: '管理联系人', selected: false },
      { icon: $r('app.media.ic_profile'), title: '我的', subtitle: '个人中心', selected: false }
    ]
  }
}

interface MenuItem {
  icon: Resource
  title: string
  subtitle: string
  selected: boolean
}
```

**FoldStatus 枚举值：**

| 值 | 说明 |
|------|------|
| `FOLD_STATUS_UNKNOWN` | 未知状态 |
| `FOLD_STATUS_EXPANDED` | 完全展开 |
| `FOLD_STATUS_FOLDED` | 完全折叠 |
| `FOLD_STATUS_HALF_FOLDED` | 半折叠（悬停态） |

---

## 7. 完整示例：响应式卡片网格组件

将以上所有模式整合为一个完整的、可直接复用的响应式卡片网格页面。

```typescript
// pages/ResponsiveCardGrid.ets
// 完整的响应式卡片网格页面，支持 sm/md/lg 三种布局

import { mediaquery } from '@kit.ArkUI'

// ==================== 数据模型 ====================

interface CardData {
  id: number
  title: string
  description: string
  imageUrl: string
  tag: string
  tagColor: string
  date: string
}

// ==================== 断点工具 ====================

class BreakpointHelper {
  // 根据断点获取对应值
  static getValue<T>(bp: string, sm: T, md: T, lg: T): T {
    if (bp === 'lg') return lg
    if (bp === 'md') return md
    return sm
  }
}

// ==================== 主页面 ====================

@Entry
@Component
struct ResponsiveCardGrid {
  @StorageProp('currentBreakpoint') currentBreakpoint: string = 'sm'
  @State cards: CardData[] = []
  @State isLoading: boolean = true

  // 断点监听器
  private smListener?: mediaquery.MediaQueryListener
  private mdListener?: mediaquery.MediaQueryListener
  private lgListener?: mediaquery.MediaQueryListener

  aboutToAppear(): void {
    // 如果在 Ability 层未注册断点监听，在此注册
    this.registerBreakpoints()
    // 模拟加载数据
    this.loadData()
  }

  aboutToDisappear(): void {
    this.smListener?.off('change')
    this.mdListener?.off('change')
    this.lgListener?.off('change')
  }

  private registerBreakpoints(): void {
    this.smListener = mediaquery.matchMediaSync('(width < 600vp)')
    this.mdListener = mediaquery.matchMediaSync('(600vp <= width < 840vp)')
    this.lgListener = mediaquery.matchMediaSync('(840vp <= width)')

    this.smListener.on('change', (r: mediaquery.MediaQueryResult) => {
      if (r.matches) AppStorage.setOrCreate('currentBreakpoint', 'sm')
    })
    this.mdListener.on('change', (r: mediaquery.MediaQueryResult) => {
      if (r.matches) AppStorage.setOrCreate('currentBreakpoint', 'md')
    })
    this.lgListener.on('change', (r: mediaquery.MediaQueryResult) => {
      if (r.matches) AppStorage.setOrCreate('currentBreakpoint', 'lg')
    })
  }

  private loadData(): void {
    // 模拟异步数据加载
    setTimeout(() => {
      this.cards = [
        { id: 1, title: 'ArkTS 入门指南', description: '从零开始学习 ArkTS 开发，掌握声明式 UI 编程范式。',
          imageUrl: '/common/img/card1.png', tag: '教程', tagColor: '#007DFF', date: '2024-01-15' },
        { id: 2, title: '组件化开发实践', description: '深入理解 @Component 和 @Builder，构建可复用的 UI 组件。',
          imageUrl: '/common/img/card2.png', tag: '进阶', tagColor: '#FF9800', date: '2024-01-14' },
        { id: 3, title: '状态管理全解析', description: '@State、@Prop、@Link、@Provide 各装饰器的使用场景。',
          imageUrl: '/common/img/card3.png', tag: '核心', tagColor: '#FF4D4F', date: '2024-01-13' },
        { id: 4, title: '列表性能优化', description: 'LazyForEach、cachedCount 和虚拟滚动的最佳实践。',
          imageUrl: '/common/img/card4.png', tag: '性能', tagColor: '#52C41A', date: '2024-01-12' },
        { id: 5, title: '动画效果大全', description: '属性动画、显式动画、路径动画和共享元素转场。',
          imageUrl: '/common/img/card5.png', tag: '动画', tagColor: '#722ED1', date: '2024-01-11' },
        { id: 6, title: '网络请求与数据持久化', description: 'HTTP 请求封装、数据缓存和 Preferences 存储。',
          imageUrl: '/common/img/card6.png', tag: '数据', tagColor: '#13C2C2', date: '2024-01-10' },
        { id: 7, title: '多设备适配策略', description: '一次开发多端部署，响应式布局和折叠屏适配方案。',
          imageUrl: '/common/img/card7.png', tag: '适配', tagColor: '#FA8C16', date: '2024-01-09' },
        { id: 8, title: '安全与权限管理', description: '权限申请流程、数据加密和安全存储最佳实践。',
          imageUrl: '/common/img/card8.png', tag: '安全', tagColor: '#EB2F96', date: '2024-01-08' },
        { id: 9, title: '测试与调试技巧', description: '单元测试、UI 测试和 DevEco Studio 调试工具使用。',
          imageUrl: '/common/img/card9.png', tag: '工具', tagColor: '#2F54EB', date: '2024-01-07' }
      ]
      this.isLoading = false
    }, 500)
  }

  build() {
    Column() {
      // ===== 顶部区域 =====
      this.headerSection()

      if (this.isLoading) {
        // 加载状态
        Column() {
          LoadingProgress()
            .width(48)
            .height(48)
            .color('#007DFF')
          Text('加载中...')
            .fontSize(14)
            .fontColor('#999')
            .margin({ top: 12 })
        }
        .width('100%')
        .layoutWeight(1)
        .justifyContent(FlexAlign.Center)
      } else {
        // ===== 卡片网格 =====
        this.cardGrid()
      }
    }
    .width('100%')
    .height('100%')
    .backgroundColor('#F5F5F5')
  }

  // ==================== 顶部区域 ====================
  @Builder
  headerSection() {
    Column() {
      // 标题行
      Row() {
        Column() {
          Text('学习中心')
            .fontSize(BreakpointHelper.getValue(this.currentBreakpoint, 22, 26, 28))
            .fontWeight(FontWeight.Bold)
            .fontColor('#333')
          Text('发现优质 ArkTS 学习资源')
            .fontSize(14)
            .fontColor('#999')
            .margin({ top: 4 })
        }
        .alignItems(HorizontalAlign.Start)

        Blank()

        // 大屏时显示搜索框
        if (this.currentBreakpoint !== 'sm') {
          Search({ placeholder: '搜索文章' })
            .width(BreakpointHelper.getValue(this.currentBreakpoint, 0, 200, 320))
            .height(36)
        }
      }
      .width('100%')

      // 手机端搜索框换行显示
      if (this.currentBreakpoint === 'sm') {
        Search({ placeholder: '搜索文章' })
          .width('100%')
          .height(36)
          .margin({ top: 12 })
      }
    }
    .width('100%')
    .padding({
      left: BreakpointHelper.getValue(this.currentBreakpoint, 16, 24, 32),
      right: BreakpointHelper.getValue(this.currentBreakpoint, 16, 24, 32),
      top: 16,
      bottom: 16
    })
    .backgroundColor(Color.White)
  }

  // ==================== 卡片网格 ====================
  @Builder
  cardGrid() {
    Grid() {
      ForEach(this.cards, (card: CardData) => {
        GridItem() {
          this.cardItem(card)
        }
      }, (card: CardData) => card.id.toString())
    }
    // 核心：根据断点切换列数
    .columnsTemplate(
      BreakpointHelper.getValue(this.currentBreakpoint, '1fr', '1fr 1fr', '1fr 1fr 1fr')
    )
    .columnsGap(BreakpointHelper.getValue(this.currentBreakpoint, 0, 16, 20))
    .rowsGap(BreakpointHelper.getValue(this.currentBreakpoint, 12, 16, 20))
    .padding({
      left: BreakpointHelper.getValue(this.currentBreakpoint, 16, 24, 32),
      right: BreakpointHelper.getValue(this.currentBreakpoint, 16, 24, 32),
      top: 12,
      bottom: 16
    })
    .width('100%')
    .layoutWeight(1)
    .edgeEffect(EdgeEffect.Spring)
  }

  // ==================== 单个卡片 ====================
  @Builder
  cardItem(card: CardData) {
    Column() {
      // 卡片图片区域
      Stack({ alignContent: Alignment.TopStart }) {
        Image(card.imageUrl)
          .width('100%')
          .height(BreakpointHelper.getValue(this.currentBreakpoint, 140, 160, 180))
          .objectFit(ImageFit.Cover)
          .borderRadius({ topLeft: 12, topRight: 12 })

        // 标签角标
        Text(card.tag)
          .fontSize(11)
          .fontColor(Color.White)
          .backgroundColor(card.tagColor)
          .borderRadius({ topLeft: 12, bottomRight: 8 })
          .padding({ left: 10, right: 10, top: 4, bottom: 4 })
      }

      // 卡片内容区域
      Column() {
        Text(card.title)
          .fontSize(BreakpointHelper.getValue(this.currentBreakpoint, 15, 16, 17))
          .fontWeight(FontWeight.Medium)
          .fontColor('#333')
          .maxLines(1)
          .textOverflow({ overflow: TextOverflow.Ellipsis })
          .width('100%')

        Text(card.description)
          .fontSize(13)
          .fontColor('#666')
          .maxLines(2)
          .textOverflow({ overflow: TextOverflow.Ellipsis })
          .lineHeight(20)
          .margin({ top: 6 })
          .width('100%')

        // 底部日期
        Row() {
          Text(card.date)
            .fontSize(12)
            .fontColor('#BBB')
          Blank()
          Text('阅读更多')
            .fontSize(12)
            .fontColor('#007DFF')
        }
        .width('100%')
        .margin({ top: 10 })
      }
      .padding({ left: 14, right: 14, top: 12, bottom: 14 })
      .alignItems(HorizontalAlign.Start)
      .width('100%')
    }
    .backgroundColor(Color.White)
    .borderRadius(12)
    .shadow({
      radius: 6,
      color: 'rgba(0,0,0,0.06)',
      offsetX: 0,
      offsetY: 2
    })
    .clip(true) // 确保圆角裁剪图片
  }
}
```

---

## 响应式设计检查清单

在构建响应式页面时，逐项检查：

| 检查项 | 说明 |
|--------|------|
| 断点注册 | 确保 `mediaquery` 监听器已在 Ability 或页面中注册 |
| 列数适配 | Grid 的 `columnsTemplate` 是否根据断点变化 |
| 间距适配 | padding/margin/gap 是否随屏幕变大而增大 |
| 字号适配 | 标题等关键文字是否在大屏上适当放大 |
| 图片比例 | 图片 `aspectRatio` 或 `height` 是否适配不同宽度 |
| 导航形态 | sm 用底部 Tab，md/lg 考虑侧边导航 |
| 内容密度 | 大屏幕可以展示更多信息，不要浪费空间 |
| 折叠屏 | 是否监听了 `foldStatusChange` 并适配半折叠态 |
| 安全区域 | 是否使用 `.expandSafeArea()` 处理刘海/挖孔屏 |
| 横竖屏 | 是否处理了设备旋转引起的断点变化 |
