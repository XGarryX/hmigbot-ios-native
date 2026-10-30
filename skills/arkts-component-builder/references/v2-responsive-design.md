# ArkTS 响应式设计参考（V2）

> 本文档为 LLM 提供 HarmonyOS ArkTS V2（`@ComponentV2 / @Local / AppStorageV2.connect`）响应式设计的完整模板和最佳实践。**本项目锁 V2**，本文档为主参考。V1 历史模式查阅请见 [`responsive-design.md`](./responsive-design.md)。

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

## 2. 使用 MediaQuery 监听断点（V2 + AppStorageV2）

V2 用 `@ObservedV2` 类封装断点状态，组件通过 `AppStorageV2.connect` 读取。

### 2.1 定义断点状态类

```typescript
// 文件: common/utils/BreakpointModel.ets
@ObservedV2
export class BreakpointModel {
  @Trace currentBreakpoint: string = 'sm'
}

export class BreakpointConstants {
  static readonly SM: string = 'sm'
  static readonly MD: string = 'md'
  static readonly LG: string = 'lg'
  static readonly STORAGE_KEY: string = 'app_breakpoint'

  // 断点阈值
  static readonly BREAKPOINT_SM: number = 320
  static readonly BREAKPOINT_MD: number = 600
  static readonly BREAKPOINT_LG: number = 840
}
```

### 2.2 在 EntryAbility 中统一监听

```typescript
// EntryAbility.ets — 在 Ability 生命周期中注册断点监听
import { AbilityConstant, UIAbility, Want } from '@kit.AbilityKit'
import { mediaquery, window } from '@kit.ArkUI'
import { BreakpointModel, BreakpointConstants } from '../common/utils/BreakpointModel'

export default class EntryAbility extends UIAbility {
  private smListener?: mediaquery.MediaQueryListener
  private mdListener?: mediaquery.MediaQueryListener
  private lgListener?: mediaquery.MediaQueryListener
  private bpModel?: BreakpointModel

  onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void {
    // V2：通过 AppStorageV2 注册全局断点状态
    this.bpModel = AppStorageV2.connect(
      BreakpointModel,
      BreakpointConstants.STORAGE_KEY,
      () => new BreakpointModel()
    )!

    // 初始化断点监听
    this.smListener = mediaquery.matchMediaSync('(width < 600vp)')
    this.mdListener = mediaquery.matchMediaSync('(600vp <= width < 840vp)')
    this.lgListener = mediaquery.matchMediaSync('(840vp <= width)')

    this.smListener.on('change', (result: mediaquery.MediaQueryResult) => {
      if (result.matches && this.bpModel !== undefined) {
        this.bpModel.currentBreakpoint = BreakpointConstants.SM
      }
    })
    this.mdListener.on('change', (result: mediaquery.MediaQueryResult) => {
      if (result.matches && this.bpModel !== undefined) {
        this.bpModel.currentBreakpoint = BreakpointConstants.MD
      }
    })
    this.lgListener.on('change', (result: mediaquery.MediaQueryResult) => {
      if (result.matches && this.bpModel !== undefined) {
        this.bpModel.currentBreakpoint = BreakpointConstants.LG
      }
    })
  }

  onWindowStageCreate(windowStage: window.WindowStage): void {
    windowStage.loadContent('pages/Index')
  }
}
```

### 2.3 封装 BreakpointSystem 工具类（可选）

```typescript
// common/utils/BreakpointSystem.ets — 可在页面 aboutToAppear 中注册
import { mediaquery } from '@kit.ArkUI'
import { BreakpointModel, BreakpointConstants } from './BreakpointModel'

export class BreakpointType<T> {
  sm: T
  md: T
  lg: T

  constructor(sm: T, md: T, lg: T) {
    this.sm = sm
    this.md = md
    this.lg = lg
  }

  getValue(currentBp: string): T {
    if (currentBp === BreakpointConstants.MD) return this.md
    if (currentBp === BreakpointConstants.LG) return this.lg
    return this.sm
  }
}

export class BreakpointSystem {
  private smListener?: mediaquery.MediaQueryListener
  private mdListener?: mediaquery.MediaQueryListener
  private lgListener?: mediaquery.MediaQueryListener
  private bpModel: BreakpointModel = AppStorageV2.connect(
    BreakpointModel,
    BreakpointConstants.STORAGE_KEY,
    () => new BreakpointModel()
  )!

  register(): void {
    this.smListener = mediaquery.matchMediaSync('(width < 600vp)')
    this.mdListener = mediaquery.matchMediaSync('(600vp <= width < 840vp)')
    this.lgListener = mediaquery.matchMediaSync('(840vp <= width)')

    this.smListener.on('change', (result: mediaquery.MediaQueryResult) => {
      if (result.matches) this.bpModel.currentBreakpoint = BreakpointConstants.SM
    })
    this.mdListener.on('change', (result: mediaquery.MediaQueryResult) => {
      if (result.matches) this.bpModel.currentBreakpoint = BreakpointConstants.MD
    })
    this.lgListener.on('change', (result: mediaquery.MediaQueryResult) => {
      if (result.matches) this.bpModel.currentBreakpoint = BreakpointConstants.LG
    })
  }

  unregister(): void {
    this.smListener?.off('change')
    this.mdListener?.off('change')
    this.lgListener?.off('change')
  }
}
```

---

## 3. 在组件中读取断点（V2 @Local + AppStorageV2.connect）

```typescript
// V2 替代 V1 @StorageProp
@Entry
@ComponentV2
struct ResponsivePage {
  @Local bpModel: BreakpointModel = AppStorageV2.connect(
    BreakpointModel,
    BreakpointConstants.STORAGE_KEY,
    () => new BreakpointModel()
  )!

  build() {
    Column() {
      Text(`当前断点: ${this.bpModel.currentBreakpoint}`)
        .fontSize(16)
        .fontColor('#999')

      // 根据断点动态调整布局
      if (this.bpModel.currentBreakpoint === 'sm') {
        this.phoneLayout()
      } else if (this.bpModel.currentBreakpoint === 'md') {
        this.tabletLayout()
      } else {
        this.desktopLayout()
      }
    }
    .width('100%')
    .height('100%')
  }

  @Builder
  phoneLayout() {
    Column({ space: 12 }) {
      ForEach(this.getItems(), (item: string, index: number) => {
        Text(item)
          .width('100%')
          .height(80)
          .backgroundColor('#F0F0F0')
          .borderRadius(8)
          .textAlign(TextAlign.Center)
      }, (item: string, index: number) => `${index}_${item}`)
    }
    .padding(16)
  }

  @Builder
  tabletLayout() {
    Grid() {
      ForEach(this.getItems(), (item: string, index: number) => {
        GridItem() {
          Text(item)
            .width('100%')
            .height(80)
            .backgroundColor('#F0F0F0')
            .borderRadius(8)
            .textAlign(TextAlign.Center)
        }
      }, (item: string, index: number) => `${index}_${item}`)
    }
    .columnsTemplate('1fr 1fr')
    .columnsGap(12)
    .rowsGap(12)
    .padding(16)
  }

  @Builder
  desktopLayout() {
    Grid() {
      ForEach(this.getItems(), (item: string, index: number) => {
        GridItem() {
          Text(item)
            .width('100%')
            .height(80)
            .backgroundColor('#F0F0F0')
            .borderRadius(8)
            .textAlign(TextAlign.Center)
        }
      }, (item: string, index: number) => `${index}_${item}`)
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

### V1 → V2 对照

| V1 | V2 |
|----|----|
| `@StorageProp('currentBreakpoint') currentBreakpoint: string = 'sm'` | `@Local bpModel: BreakpointModel = AppStorageV2.connect(BreakpointModel, key, () => new BreakpointModel())!` + 访问 `this.bpModel.currentBreakpoint` |
| `AppStorage.setOrCreate('currentBreakpoint', 'sm')` | `this.bpModel.currentBreakpoint = 'sm'`（直接修改 `@Trace` 字段） |

---

## 4. Grid 响应式列数（V2）

通过 `columnsTemplate` 直接绑定断点实现自适应列数，这是最常用的响应式模式。

```typescript
// 响应式商品网格：sm=1列, md=2列, lg=3列（V2）
interface ProductItem {
  id: number
  productName: string
  productPrice: number
  imageUrl: string
}

@Entry
@ComponentV2
struct ResponsiveGrid {
  @Local bpModel: BreakpointModel = AppStorageV2.connect(
    BreakpointModel,
    BreakpointConstants.STORAGE_KEY,
    () => new BreakpointModel()
  )!

  // 根据断点计算列模板
  getColumnsTemplate(): string {
    switch (this.bpModel.currentBreakpoint) {
      case 'lg': return '1fr 1fr 1fr'
      case 'md': return '1fr 1fr'
      default: return '1fr'
    }
  }

  getPadding(): number {
    switch (this.bpModel.currentBreakpoint) {
      case 'lg': return 32
      case 'md': return 24
      default: return 16
    }
  }

  build() {
    Column() {
      Text('商品列表')
        .fontSize(this.bpModel.currentBreakpoint === 'sm' ? 20 : 24)
        .fontWeight(FontWeight.Bold)
        .width('100%')
        .padding({ left: this.getPadding(), top: 16, bottom: 12 })

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
        .aspectRatio(this.bpModel.currentBreakpoint === 'sm' ? 2.5 : 1.2)
        .objectFit(ImageFit.Cover)
        .borderRadius({ topLeft: 8, topRight: 8 })

      Column() {
        Text(product.productName)
          .fontSize(14)
          .maxLines(2)
          .textOverflow({ overflow: TextOverflow.Ellipsis })

        Text(`¥${product.productPrice}`)
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
      { id: 1, productName: '无线耳机', productPrice: 299, imageUrl: '/common/p1.png' },
      { id: 2, productName: '智能手表', productPrice: 599, imageUrl: '/common/p2.png' },
      { id: 3, productName: '充电宝', productPrice: 129, imageUrl: '/common/p3.png' },
      { id: 4, productName: '键盘', productPrice: 459, imageUrl: '/common/p4.png' }
    ]
  }
}
```

---

## 5. GridRow/GridCol 栅格系统（V2）

ArkTS 提供了类似 Bootstrap 的 12 栏栅格系统，V1/V2 通用，仅装饰器不同：

```typescript
@Entry
@ComponentV2
struct ResponsiveForm {
  @Local userName: string = ''
  @Local userEmail: string = ''
  @Local userPhone: string = ''
  @Local userAddress: string = ''

  build() {
    Scroll() {
      GridRow({
        columns: 12,
        gutter: { x: 12, y: 16 },
        breakpoints: {
          value: ['600vp', '840vp'],
          reference: BreakpointsReference.WindowSize
        }
      }) {
        GridCol({ span: 12 }) {
          Text('用户注册')
            .fontSize(24)
            .fontWeight(FontWeight.Bold)
            .margin({ bottom: 8 })
        }

        GridCol({ span: { sm: 12, md: 6, lg: 4 } }) {
          Column({ space: 4 }) {
            Text('用户名').fontSize(14).fontColor('#666')
            TextInput({ placeholder: '请输入用户名' })
              .height(44)
              .onChange((v: string) => { this.userName = v })
          }
          .alignItems(HorizontalAlign.Start)
          .width('100%')
        }

        GridCol({ span: { sm: 12, md: 6, lg: 4 } }) {
          Column({ space: 4 }) {
            Text('邮箱').fontSize(14).fontColor('#666')
            TextInput({ placeholder: '请输入邮箱' })
              .type(InputType.Email)
              .height(44)
              .onChange((v: string) => { this.userEmail = v })
          }
          .alignItems(HorizontalAlign.Start)
          .width('100%')
        }

        GridCol({ span: { sm: 12, md: 6, lg: 4 } }) {
          Column({ space: 4 }) {
            Text('手机号').fontSize(14).fontColor('#666')
            TextInput({ placeholder: '请输入手机号' })
              .type(InputType.PhoneNumber)
              .height(44)
              .onChange((v: string) => { this.userPhone = v })
          }
          .alignItems(HorizontalAlign.Start)
          .width('100%')
        }

        GridCol({ span: 12 }) {
          Column({ space: 4 }) {
            Text('详细地址').fontSize(14).fontColor('#666')
            TextInput({ placeholder: '请输入详细地址' })
              .height(44)
              .onChange((v: string) => { this.userAddress = v })
          }
          .alignItems(HorizontalAlign.Start)
          .width('100%')
        }

        GridCol({
          span: { sm: 12, md: 6, lg: 4 },
          offset: { sm: 0, md: 6, lg: 8 }
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

---

## 6. 折叠屏适配（V2）

折叠屏设备在展开/折叠时会触发屏幕尺寸变化，可通过断点系统自动适配，也可使用 `display` 接口获取折叠状态。

```typescript
// 折叠屏感知组件（V2）
import { display } from '@kit.ArkUI'

@Entry
@ComponentV2
struct FoldableAdaptive {
  @Local bpModel: BreakpointModel = AppStorageV2.connect(
    BreakpointModel,
    BreakpointConstants.STORAGE_KEY,
    () => new BreakpointModel()
  )!
  @Local isFolded: boolean = true
  @Local foldStatus: display.FoldStatus = display.FoldStatus.FOLD_STATUS_UNKNOWN

  aboutToAppear(): void {
    display.on('foldStatusChange', (status: display.FoldStatus) => {
      this.foldStatus = status
      this.isFolded = (status === display.FoldStatus.FOLD_STATUS_FOLDED)
    })

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
      if (this.isFolded) {
        this.compactLayout()
      } else {
        this.expandedLayout()
      }
    }
    .width('100%')
    .height('100%')
  }

  @Builder
  compactLayout() {
    Column() {
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

      List({ space: 8 }) {
        ForEach(this.getMenuItems(), (item: MenuItem, index: number) => {
          ListItem() {
            Row() {
              Image(item.itemIcon).width(40).height(40).borderRadius(8)
              Column() {
                Text(item.itemTitle).fontSize(16).fontColor('#333')
                Text(item.itemSubtitle).fontSize(12).fontColor('#999').margin({ top: 2 })
              }
              .alignItems(HorizontalAlign.Start)
              .margin({ left: 12 })
              .layoutWeight(1)
              Image($r('sys.media.ohos_ic_public_arrow_right'))
                .width(20).height(20).fillColor('#CCC')
            }
            .padding(12)
          }
        }, (item: MenuItem, index: number) => `${index}_${item.itemTitle}`)
      }
      .width('100%')
      .layoutWeight(1)
      .padding({ left: 16, right: 16 })
    }
  }

  @Builder
  expandedLayout() {
    Row() {
      Column() {
        Text('我的应用')
          .fontSize(20)
          .fontWeight(FontWeight.Bold)
          .padding({ left: 16, top: 16, bottom: 16 })
          .width('100%')

        List({ space: 4 }) {
          ForEach(this.getMenuItems(), (item: MenuItem, index: number) => {
            ListItem() {
              Row() {
                Image(item.itemIcon).width(32).height(32).borderRadius(6)
                Text(item.itemTitle)
                  .fontSize(15)
                  .margin({ left: 10 })
                  .layoutWeight(1)
              }
              .padding({ left: 16, right: 16, top: 10, bottom: 10 })
              .width('100%')
              .borderRadius(8)
              .backgroundColor(item.isSelected ? '#E8F0FE' : Color.Transparent)
            }
          }, (item: MenuItem, index: number) => `${index}_${item.itemTitle}`)
        }
        .width('100%')
        .layoutWeight(1)
      }
      .width(280)
      .height('100%')
      .backgroundColor('#FAFAFA')
      .border({ width: { right: 0.5 }, color: { right: '#E8E8E8' } })

      Column() {
        Text('选择一个菜单项查看详情')
          .fontSize(16)
          .fontColor('#999')
      }
      .layoutWeight(1)
      .height('100%')
      .justifyContent(FlexAlign.Center)
      .backgroundColor(Color.White)
    }
    .width('100%')
    .height('100%')
  }

  private getMenuItems(): MenuItem[] {
    return [
      { itemIcon: $r('app.media.ic_home'), itemTitle: '首页', itemSubtitle: '查看最新动态', isSelected: true },
      { itemIcon: $r('app.media.ic_msg'), itemTitle: '消息', itemSubtitle: '3 条未读消息', isSelected: false },
      { itemIcon: $r('app.media.ic_contacts'), itemTitle: '通讯录', itemSubtitle: '管理联系人', isSelected: false },
      { itemIcon: $r('app.media.ic_profile'), itemTitle: '我的', itemSubtitle: '个人中心', isSelected: false }
    ]
  }
}

interface MenuItem {
  itemIcon: Resource
  itemTitle: string
  itemSubtitle: string
  isSelected: boolean
}
```

---

## 7. 完整示例：响应式卡片网格组件（V2）

将以上所有模式整合为一个完整的、可直接复用的响应式卡片网格页面。

```typescript
// pages/ResponsiveCardGrid.ets — V2 完整响应式卡片网格

import { mediaquery } from '@kit.ArkUI'
import { BreakpointModel, BreakpointConstants } from '../common/utils/BreakpointModel'

interface CardData {
  id: number
  cardTitle: string         // 不用 title
  cardDescription: string   // 不用 description
  imageUrl: string
  tagText: string           // 不用 tag
  tagColor: string
  publishDate: string       // 不用 date
}

class BreakpointHelper {
  static getValue<T>(bp: string, sm: T, md: T, lg: T): T {
    if (bp === 'lg') return lg
    if (bp === 'md') return md
    return sm
  }
}

@Entry
@ComponentV2
struct ResponsiveCardGrid {
  @Local bpModel: BreakpointModel = AppStorageV2.connect(
    BreakpointModel,
    BreakpointConstants.STORAGE_KEY,
    () => new BreakpointModel()
  )!

  @Local cards: CardData[] = []
  @Local isLoading: boolean = true

  private smListener?: mediaquery.MediaQueryListener
  private mdListener?: mediaquery.MediaQueryListener
  private lgListener?: mediaquery.MediaQueryListener

  aboutToAppear(): void {
    this.registerBreakpoints()
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
      if (r.matches) this.bpModel.currentBreakpoint = 'sm'
    })
    this.mdListener.on('change', (r: mediaquery.MediaQueryResult) => {
      if (r.matches) this.bpModel.currentBreakpoint = 'md'
    })
    this.lgListener.on('change', (r: mediaquery.MediaQueryResult) => {
      if (r.matches) this.bpModel.currentBreakpoint = 'lg'
    })
  }

  private loadData(): void {
    setTimeout(() => {
      this.cards = [
        { id: 1, cardTitle: 'ArkTS V2 入门指南',
          cardDescription: '从零开始学习 ArkTS V2 装饰器（@ComponentV2 / @Local / @Param）。',
          imageUrl: '/common/img/card1.png', tagText: '教程', tagColor: '#007DFF', publishDate: '2024-01-15' },
        { id: 2, cardTitle: '组件化开发实践',
          cardDescription: '深入理解 @ComponentV2 和 @Builder，构建可复用的 UI 组件。',
          imageUrl: '/common/img/card2.png', tagText: '进阶', tagColor: '#FF9800', publishDate: '2024-01-14' },
        { id: 3, cardTitle: 'V2 状态管理全解析',
          cardDescription: '@Local、@Param、@Event、@Provider/@Consumer 的使用场景。',
          imageUrl: '/common/img/card3.png', tagText: '核心', tagColor: '#FF4D4F', publishDate: '2024-01-13' },
        { id: 4, cardTitle: '列表性能优化',
          cardDescription: 'LazyForEach、Repeat、virtualScroll 的最佳实践。',
          imageUrl: '/common/img/card4.png', tagText: '性能', tagColor: '#52C41A', publishDate: '2024-01-12' },
        { id: 5, cardTitle: '动画效果大全',
          cardDescription: '属性动画、显式动画、路径动画和共享元素转场。',
          imageUrl: '/common/img/card5.png', tagText: '动画', tagColor: '#722ED1', publishDate: '2024-01-11' },
        { id: 6, cardTitle: 'PersistenceV2 持久化',
          cardDescription: 'V2 一站式持久化：磁盘存储 + UI 响应式。',
          imageUrl: '/common/img/card6.png', tagText: '数据', tagColor: '#13C2C2', publishDate: '2024-01-10' }
      ]
      this.isLoading = false
    }, 500)
  }

  build() {
    Column() {
      this.headerSection()

      if (this.isLoading) {
        Column() {
          LoadingProgress()
            .width(48).height(48).color('#007DFF')
          Text('加载中...').fontSize(14).fontColor('#999').margin({ top: 12 })
        }
        .width('100%')
        .layoutWeight(1)
        .justifyContent(FlexAlign.Center)
      } else {
        this.cardGrid()
      }
    }
    .width('100%')
    .height('100%')
    .backgroundColor('#F5F5F5')
  }

  @Builder
  headerSection() {
    Column() {
      Row() {
        Column() {
          Text('学习中心')
            .fontSize(BreakpointHelper.getValue(this.bpModel.currentBreakpoint, 22, 26, 28))
            .fontWeight(FontWeight.Bold)
            .fontColor('#333')
          Text('发现优质 ArkTS V2 学习资源')
            .fontSize(14)
            .fontColor('#999')
            .margin({ top: 4 })
        }
        .alignItems(HorizontalAlign.Start)

        Blank()

        if (this.bpModel.currentBreakpoint !== 'sm') {
          Search({ placeholder: '搜索文章' })
            .width(BreakpointHelper.getValue(this.bpModel.currentBreakpoint, 0, 200, 320))
            .height(36)
        }
      }
      .width('100%')

      if (this.bpModel.currentBreakpoint === 'sm') {
        Search({ placeholder: '搜索文章' })
          .width('100%').height(36)
          .margin({ top: 12 })
      }
    }
    .width('100%')
    .padding({
      left: BreakpointHelper.getValue(this.bpModel.currentBreakpoint, 16, 24, 32),
      right: BreakpointHelper.getValue(this.bpModel.currentBreakpoint, 16, 24, 32),
      top: 16,
      bottom: 16
    })
    .backgroundColor(Color.White)
  }

  @Builder
  cardGrid() {
    Grid() {
      ForEach(this.cards, (card: CardData) => {
        GridItem() {
          this.cardItem(card)
        }
      }, (card: CardData) => card.id.toString())
    }
    .columnsTemplate(
      BreakpointHelper.getValue(this.bpModel.currentBreakpoint, '1fr', '1fr 1fr', '1fr 1fr 1fr')
    )
    .columnsGap(BreakpointHelper.getValue(this.bpModel.currentBreakpoint, 0, 16, 20))
    .rowsGap(BreakpointHelper.getValue(this.bpModel.currentBreakpoint, 12, 16, 20))
    .padding({
      left: BreakpointHelper.getValue(this.bpModel.currentBreakpoint, 16, 24, 32),
      right: BreakpointHelper.getValue(this.bpModel.currentBreakpoint, 16, 24, 32),
      top: 12,
      bottom: 16
    })
    .width('100%')
    .layoutWeight(1)
    .edgeEffect(EdgeEffect.Spring)
  }

  @Builder
  cardItem(card: CardData) {
    Column() {
      Stack({ alignContent: Alignment.TopStart }) {
        Image(card.imageUrl)
          .width('100%')
          .height(BreakpointHelper.getValue(this.bpModel.currentBreakpoint, 140, 160, 180))
          .objectFit(ImageFit.Cover)
          .borderRadius({ topLeft: 12, topRight: 12 })

        Text(card.tagText)
          .fontSize(11)
          .fontColor(Color.White)
          .backgroundColor(card.tagColor)
          .borderRadius({ topLeft: 12, bottomRight: 8 })
          .padding({ left: 10, right: 10, top: 4, bottom: 4 })
      }

      Column() {
        Text(card.cardTitle)
          .fontSize(BreakpointHelper.getValue(this.bpModel.currentBreakpoint, 15, 16, 17))
          .fontWeight(FontWeight.Medium)
          .fontColor('#333')
          .maxLines(1)
          .textOverflow({ overflow: TextOverflow.Ellipsis })
          .width('100%')

        Text(card.cardDescription)
          .fontSize(13)
          .fontColor('#666')
          .maxLines(2)
          .textOverflow({ overflow: TextOverflow.Ellipsis })
          .lineHeight(20)
          .margin({ top: 6 })
          .width('100%')

        Row() {
          Text(card.publishDate)
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
    .shadow({ radius: 6, color: 'rgba(0,0,0,0.06)', offsetX: 0, offsetY: 2 })
    .clip(true)
  }
}
```

---

## 响应式设计检查清单（V2）

在构建响应式页面时，逐项检查：

| 检查项 | 说明 |
|--------|------|
| 断点注册 | 确保 `mediaquery` 监听器已在 Ability 或页面中注册 |
| AppStorageV2 注册 | `BreakpointModel` 已通过 `AppStorageV2.connect` 全局注册 |
| @Local 持有 BreakpointModel | 组件用 `@Local` 持有实例，不要每次手写 `AppStorageV2.connect` |
| 列数适配 | Grid 的 `columnsTemplate` 是否根据断点变化 |
| 间距适配 | padding/margin/gap 是否随屏幕变大而增大 |
| 字号适配 | 标题等关键文字是否在大屏上适当放大 |
| 图片比例 | 图片 `aspectRatio` 或 `height` 是否适配不同宽度 |
| 导航形态 | sm 用底部 Tab，md/lg 考虑侧边导航 |
| 内容密度 | 大屏幕展示更多信息，不浪费空间 |
| 折叠屏 | 是否监听了 `foldStatusChange` 并适配半折叠态 |
| 安全区域 | 是否使用 `.expandSafeArea()` 处理刘海/挖孔屏 |
| 横竖屏 | 是否处理了设备旋转引起的断点变化 |

---

## 跨文档参考

- [`v2-common-components.md`](./v2-common-components.md) — V2 常用组件用法
- [`v2-layout-patterns.md`](./v2-layout-patterns.md) — V2 布局模板
- [`v2-prop-naming-rules.md`](./v2-prop-naming-rules.md) — V2 变量命名规则
- [`v2-component-lifecycle-patterns.md`](./v2-component-lifecycle-patterns.md) — V2 生命周期
- `arkts-state-manager/references/v2-global-state.md` — V2 AppStorageV2 完整模板
