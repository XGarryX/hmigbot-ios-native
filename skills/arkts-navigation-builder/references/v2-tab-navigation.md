# ArkTS V2 Tab 导航完整模式参考

> 本文件为 **V2 主参考**（API 12+，`@ComponentV2 / @Local / @Param / @Once / @ObservedV2 / @Trace / AppStorageV2 / PersistenceV2`），包含 ArkTS/HarmonyOS Tabs 组件的所有主要 V2 用法。**本项目锁 V2**。
>
> 每个示例均为完整可运行代码。
>
> V1 历史写法请见 [`tab-navigation.md`](./tab-navigation.md)（已加 legacy 标识）。
>
> **Tabs API 在 V1/V2 中完全一致**：`Tabs / TabContent / TabsController / BarPosition / BarMode / .barHeight / .scrollable / .onChange` 用法不变，**仅状态装饰器需要使用 V2**。Tab 状态持久化（V1 的 `@StorageLink + PersistentStorage`）在 V2 中改用 `AppStorageV2.connect / PersistenceV2.globalConnect`。

---

## 1. 基础 Tabs（最小示例，V2）

最简单的 Tabs 用法，使用内置文字 TabBar。

```typescript
@Entry
@ComponentV2
struct BasicTabsExample {
  @Local currentIndex: number = 0   // V2：@Local 替代 @State

  build() {
    Tabs({ barPosition: BarPosition.End, index: this.currentIndex }) {

      TabContent() {
        Column() {
          Text('首页内容')
            .fontSize(24)
        }
        .width('100%')
        .height('100%')
        .justifyContent(FlexAlign.Center)
      }
      .tabBar('首页')

      TabContent() {
        Column() {
          Text('分类内容')
            .fontSize(24)
        }
        .width('100%')
        .height('100%')
        .justifyContent(FlexAlign.Center)
      }
      .tabBar('分类')

      TabContent() {
        Column() {
          Text('我的内容')
            .fontSize(24)
        }
        .width('100%')
        .height('100%')
        .justifyContent(FlexAlign.Center)
      }
      .tabBar('我的')
    }
    .barHeight(56)
    .scrollable(false)
    .animationDuration(300)
    .onChange((index: number) => {
      this.currentIndex = index
    })
  }
}
```

---

## 2. 自定义 TabBar（图标 + 文字 + 角标，V2）

真实应用必备：自定义图标、选中/未选中颜色切换、消息角标。

```typescript
// Tab 项的数据结构
interface TabItemInfo {
  title: string
  icon: Resource
  selectedIcon: Resource
  badgeCount: number
}

@Entry
@ComponentV2
struct CustomTabBarExample {
  @Local currentIndex: number = 0

  // V2：tabItems 是 plain array，没有 reactive 需求时不需要 @Local
  // 如果需要响应式（如清除角标），把 badgeCount 抽出到 @ObservedV2 类
  private tabItems: TabItemInfo[] = [
    { title: '首页', icon: $r('app.media.ic_home'), selectedIcon: $r('app.media.ic_home_filled'), badgeCount: 0 },
    { title: '发现', icon: $r('app.media.ic_discover'), selectedIcon: $r('app.media.ic_discover_filled'), badgeCount: 0 },
    { title: '消息', icon: $r('app.media.ic_message'), selectedIcon: $r('app.media.ic_message_filled'), badgeCount: 5 },
    { title: '我的', icon: $r('app.media.ic_mine'), selectedIcon: $r('app.media.ic_mine_filled'), badgeCount: 0 }
  ]

  @Builder
  tabItemBuilder(item: TabItemInfo, index: number) {
    Column() {
      Badge({
        count: item.badgeCount,
        position: BadgePosition.RightTop,
        style: {
          fontSize: 10,
          badgeSize: 16,
          badgeColor: '#FF3B30'
        }
      }) {
        Image(this.currentIndex === index ? item.selectedIcon : item.icon)
          .width(24)
          .height(24)
          .fillColor(this.currentIndex === index ? '#007DFF' : '#8E8E93')
      }

      Text(item.title)
        .fontSize(10)
        .fontWeight(this.currentIndex === index ? FontWeight.Medium : FontWeight.Normal)
        .fontColor(this.currentIndex === index ? '#007DFF' : '#8E8E93')
        .margin({ top: 4 })
    }
    .width('100%')
    .height('100%')
    .justifyContent(FlexAlign.Center)
    .padding({ top: 6, bottom: 2 })
  }

  build() {
    Tabs({ barPosition: BarPosition.End, index: this.currentIndex }) {

      TabContent() {
        HomeTabContent()
      }
      .tabBar(this.tabItemBuilder(this.tabItems[0], 0))

      TabContent() {
        DiscoverTabContent()
      }
      .tabBar(this.tabItemBuilder(this.tabItems[1], 1))

      TabContent() {
        MessageTabContent({ badgeCount: this.tabItems[2].badgeCount })
      }
      .tabBar(this.tabItemBuilder(this.tabItems[2], 2))

      TabContent() {
        MineTabContent()
      }
      .tabBar(this.tabItemBuilder(this.tabItems[3], 3))
    }
    .barHeight(56)
    .scrollable(false)
    .onChange((index: number) => {
      this.currentIndex = index
      // 切换到消息 Tab 时清除角标
      if (index === 2) {
        this.tabItems[2].badgeCount = 0
      }
    })
  }
}

// ---- 各 Tab 页面内容组件 ----

@ComponentV2
struct HomeTabContent {
  build() {
    Column({ space: 16 }) {
      Text('首页')
        .fontSize(28)
        .fontWeight(FontWeight.Bold)
      Text('欢迎使用 HarmonyOS')
        .fontSize(16)
        .fontColor('#666')
    }
    .width('100%')
    .height('100%')
    .justifyContent(FlexAlign.Center)
  }
}

@ComponentV2
struct DiscoverTabContent {
  build() {
    Column() {
      Text('发现页面')
        .fontSize(28)
        .fontWeight(FontWeight.Bold)
    }
    .width('100%')
    .height('100%')
    .justifyContent(FlexAlign.Center)
  }
}

@ComponentV2
struct MessageTabContent {
  // V2：父传只读用 @Param + @Once
  @Param @Once badgeCount: number = 0

  // 模拟消息数据
  @Local messages: string[] = ['张三: 明天开会', '李四: 收到', '系统通知: 版本更新', '王五: 周末聚餐', '赵六: OK']

  build() {
    Column() {
      List({ space: 1 }) {
        ForEach(this.messages, (msg: string) => {
          ListItem() {
            Row() {
              Column()
                .width(44)
                .height(44)
                .borderRadius(22)
                .backgroundColor('#E0E0E0')
                .margin({ right: 12 })

              Text(msg)
                .fontSize(15)
                .layoutWeight(1)
            }
            .width('100%')
            .padding({ left: 16, right: 16, top: 12, bottom: 12 })
            .backgroundColor(Color.White)
          }
        })
      }
      .width('100%')
      .layoutWeight(1)
      .backgroundColor('#F5F5F5')
    }
  }
}

@ComponentV2
struct MineTabContent {
  build() {
    Column({ space: 12 }) {
      Column()
        .width(80)
        .height(80)
        .borderRadius(40)
        .backgroundColor('#E0E0E0')

      Text('用户名')
        .fontSize(20)
        .fontWeight(FontWeight.Medium)
      Text('个人简介...')
        .fontSize(14)
        .fontColor('#999')
    }
    .width('100%')
    .height('100%')
    .justifyContent(FlexAlign.Center)
  }
}
```

---

## 3. 可滚动 Tabs（多分类场景，V2）

当 Tab 数量较多时（如新闻分类、商品类目），使用可滚动 Tabs。

```typescript
@Entry
@ComponentV2
struct ScrollableTabsExample {
  @Local currentIndex: number = 0

  private categories: string[] = [
    '推荐', '热点', '科技', '体育', '娱乐',
    '财经', '教育', '健康', '旅游', '美食',
    '汽车', '时尚', '游戏', '音乐', '影视'
  ]

  @Builder
  categoryTabBuilder(category: string, index: number) {
    Column() {
      Text(category)
        .fontSize(this.currentIndex === index ? 16 : 14)
        .fontWeight(this.currentIndex === index ? FontWeight.Bold : FontWeight.Normal)
        .fontColor(this.currentIndex === index ? '#333' : '#999')
        .padding({ left: 12, right: 12 })

      Divider()
        .width(this.currentIndex === index ? 20 : 0)
        .strokeWidth(3)
        .color('#007DFF')
        .lineCap(LineCapStyle.Round)
        .margin({ top: 6 })
        .animation({ duration: 200, curve: Curve.EaseOut })
    }
    .height('100%')
    .justifyContent(FlexAlign.Center)
  }

  build() {
    Column() {
      Tabs({ barPosition: BarPosition.Start, index: this.currentIndex }) {
        ForEach(this.categories, (category: string, index: number) => {
          TabContent() {
            Column() {
              Text(category + ' 频道内容')
                .fontSize(20)
            }
            .width('100%')
            .height('100%')
            .justifyContent(FlexAlign.Center)
          }
          .tabBar(this.categoryTabBuilder(category, index))
        })
      }
      .barMode(BarMode.Scrollable)
      .barHeight(48)
      .scrollable(true)
      .animationDuration(250)
      .onChange((index: number) => {
        this.currentIndex = index
      })
    }
    .width('100%')
    .height('100%')
  }
}
```

---

## 4. Tabs + Swiper 联动（V2）

某些场景需要 Tab 切换和手势滑动内容联动。

```typescript
@Entry
@ComponentV2
struct TabSwiperExample {
  @Local currentIndex: number = 0

  // SwiperController / TabsController 不是状态变量，可作为 private 字段
  private swiperController: SwiperController = new SwiperController()

  private tabTitles: string[] = ['关注', '推荐', '热榜']

  @Builder
  topTabBuilder(title: string, index: number) {
    Text(title)
      .fontSize(this.currentIndex === index ? 18 : 15)
      .fontWeight(this.currentIndex === index ? FontWeight.Bold : FontWeight.Normal)
      .fontColor(this.currentIndex === index ? '#333' : '#999')
      .padding({ left: 16, right: 16 })
      .animation({ duration: 150 })
  }

  build() {
    Column() {
      Row() {
        ForEach(this.tabTitles, (title: string, index: number) => {
          Column() {
            this.topTabBuilder(title, index)
          }
          .onClick(() => {
            this.currentIndex = index
            this.swiperController.changeIndex(index)
          })
        })
      }
      .width('100%')
      .height(48)
      .justifyContent(FlexAlign.Center)
      .backgroundColor(Color.White)

      Divider().color('#F0F0F0')

      Swiper(this.swiperController) {
        FollowFeedContent()
        RecommendFeedContent()
        HotFeedContent()
      }
      .index(this.currentIndex)
      .loop(false)
      .indicator(false)
      .cachedCount(1)
      .onChange((index: number) => {
        this.currentIndex = index
      })
      .layoutWeight(1)
    }
    .width('100%')
    .height('100%')
  }
}

@ComponentV2
struct FollowFeedContent {
  @Local items: string[] = ['关注作者1的新文章', '关注作者2的视频', '关注话题更新']

  build() {
    List({ space: 8 }) {
      ForEach(this.items, (item: string) => {
        ListItem() {
          Text(item)
            .fontSize(16)
            .width('100%')
            .padding(16)
            .backgroundColor(Color.White)
            .borderRadius(8)
        }
      })
    }
    .width('100%')
    .height('100%')
    .padding(12)
    .backgroundColor('#F5F5F5')
  }
}

@ComponentV2
struct RecommendFeedContent {
  @Local items: string[] = ['推荐内容1: HarmonyOS 开发入门', '推荐内容2: ArkTS 最佳实践', '推荐内容3: 组件化架构']

  build() {
    List({ space: 8 }) {
      ForEach(this.items, (item: string) => {
        ListItem() {
          Text(item)
            .fontSize(16)
            .width('100%')
            .padding(16)
            .backgroundColor(Color.White)
            .borderRadius(8)
        }
      })
    }
    .width('100%')
    .height('100%')
    .padding(12)
    .backgroundColor('#F5F5F5')
  }
}

@ComponentV2
struct HotFeedContent {
  @Local hotItems: string[] = ['#1 热搜话题A', '#2 热搜话题B', '#3 热搜话题C', '#4 热搜话题D']

  build() {
    List({ space: 8 }) {
      ForEach(this.hotItems, (item: string, index: number) => {
        ListItem() {
          Row({ space: 12 }) {
            Text((index + 1).toString())
              .fontSize(18)
              .fontWeight(FontWeight.Bold)
              .fontColor(index < 3 ? '#FF3B30' : '#999')
              .width(30)
              .textAlign(TextAlign.Center)

            Text(item)
              .fontSize(16)
              .layoutWeight(1)
          }
          .width('100%')
          .padding(16)
          .backgroundColor(Color.White)
          .borderRadius(8)
        }
      })
    }
    .width('100%')
    .height('100%')
    .padding(12)
    .backgroundColor('#F5F5F5')
  }
}
```

---

## 5. Tab 状态持久化（V2 — 用 AppStorageV2 / PersistenceV2 替代 V1 @StorageLink）

V2 移除了 `@StorageLink / @StorageProp / PersistentStorage.persistProp`。改用 `@ObservedV2` 类 + `AppStorageV2.connect()`（运行时共享）或 `PersistenceV2.globalConnect()`（重启后保留）。

### 方案 A：AppStorageV2（仅应用内生命周期保持）

```typescript
// 1. 定义 Tab 状态类
@ObservedV2
class TabState {
  @Trace lastTabIndex: number = 0
}

// 2. 在 EntryAbility.onCreate 中预热（可选）
// AppStorageV2.connect(TabState, 'tabState', () => new TabState())

@Entry
@ComponentV2
struct AppStorageTabExample {
  // V2 替代 V1 @StorageLink('lastTabIndex')
  // 任意页面修改 tabState.lastTabIndex 都会同步到所有 connect 的位置
  @Local tabState: TabState = AppStorageV2.connect(
    TabState, 'tabState', () => new TabState()
  )!

  build() {
    Tabs({ barPosition: BarPosition.End, index: this.tabState.lastTabIndex }) {
      TabContent() {
        Column() {
          Text('首页')
            .fontSize(24)
        }
        .width('100%')
        .height('100%')
        .justifyContent(FlexAlign.Center)
      }
      .tabBar('首页')

      TabContent() {
        Column() {
          Text('发现')
            .fontSize(24)
        }
        .width('100%')
        .height('100%')
        .justifyContent(FlexAlign.Center)
      }
      .tabBar('发现')

      TabContent() {
        Column() {
          Text('我的')
            .fontSize(24)
        }
        .width('100%')
        .height('100%')
        .justifyContent(FlexAlign.Center)
      }
      .tabBar('我的')
    }
    .barHeight(56)
    .scrollable(false)
    .onChange((index: number) => {
      // 修改 @Trace 字段自动同步到所有引用
      this.tabState.lastTabIndex = index
    })
  }
}
```

### 方案 B：PersistenceV2（应用重启后仍保持）

```typescript
@ObservedV2
class PersistedTabState {
  @Trace savedTabIndex: number = 0
}

@Entry
@ComponentV2
struct PersistentTabExample {
  // V2 替代 V1 PersistentStorage.persistProp + @StorageLink
  // PersistenceV2 一站式：磁盘持久化 + UI 响应式
  @Local tabState: PersistedTabState = PersistenceV2.globalConnect({
    type: PersistedTabState,
    key: 'persistedTabState',
    defaultCreator: () => new PersistedTabState()
  })!

  build() {
    Tabs({ barPosition: BarPosition.End, index: this.tabState.savedTabIndex }) {
      TabContent() {
        Column() {
          Text('首页')
            .fontSize(24)
          Text('关闭应用再打开，会恢复到这个 Tab')
            .fontSize(12)
            .fontColor('#999')
        }
        .width('100%')
        .height('100%')
        .justifyContent(FlexAlign.Center)
      }
      .tabBar('首页')

      TabContent() {
        Column() {
          Text('消息')
            .fontSize(24)
        }
        .width('100%')
        .height('100%')
        .justifyContent(FlexAlign.Center)
      }
      .tabBar('消息')

      TabContent() {
        Column() {
          Text('我的')
            .fontSize(24)
        }
        .width('100%')
        .height('100%')
        .justifyContent(FlexAlign.Center)
      }
      .tabBar('我的')
    }
    .barHeight(56)
    .scrollable(false)
    .onChange((index: number) => {
      // 修改自动落盘 + UI 响应（无需手动同步两套存储）
      this.tabState.savedTabIndex = index
    })
  }
}
```

### 方案 C：TabsController 编程式切换

```typescript
@Entry
@ComponentV2
struct ControllerTabExample {
  @Local currentIndex: number = 0
  private tabsController: TabsController = new TabsController()

  build() {
    Column() {
      Row({ space: 8 }) {
        Button('跳到首页')
          .fontSize(12)
          .onClick(() => {
            this.tabsController.changeIndex(0)
          })
        Button('跳到消息')
          .fontSize(12)
          .onClick(() => {
            this.tabsController.changeIndex(1)
          })
        Button('跳到我的')
          .fontSize(12)
          .onClick(() => {
            this.tabsController.changeIndex(2)
          })
      }
      .width('100%')
      .padding(12)
      .justifyContent(FlexAlign.Center)
      .backgroundColor('#F0F0F0')

      Tabs({
        barPosition: BarPosition.End,
        index: this.currentIndex,
        controller: this.tabsController
      }) {
        TabContent() {
          Column() {
            Text('首页')
              .fontSize(24)
          }
          .width('100%')
          .height('100%')
          .justifyContent(FlexAlign.Center)
        }
        .tabBar('首页')

        TabContent() {
          Column() {
            Text('消息')
              .fontSize(24)
          }
          .width('100%')
          .height('100%')
          .justifyContent(FlexAlign.Center)
        }
        .tabBar('消息')

        TabContent() {
          Column() {
            Text('我的')
              .fontSize(24)
          }
          .width('100%')
          .height('100%')
          .justifyContent(FlexAlign.Center)
        }
        .tabBar('我的')
      }
      .barHeight(56)
      .scrollable(false)
      .layoutWeight(1)
      .onChange((index: number) => {
        this.currentIndex = index
      })
    }
    .width('100%')
    .height('100%')
  }
}
```

---

## 速查：Tabs API 一览（V1/V2 完全一致）

```typescript
// ---- Tabs 组件属性 ----
Tabs({
  barPosition: BarPosition.End,      // TabBar 位置：End（底部）| Start（顶部）
  index: this.currentIndex,          // 当前选中 Tab 的索引
  controller: tabsController         // 可选：编程式控制器
})
  .barHeight(56)                     // TabBar 高度
  .barWidth('100%')                  // TabBar 宽度
  .barMode(BarMode.Fixed)            // Fixed（等分）| Scrollable（可滚动）
  .scrollable(false)                 // 是否允许手势滑动切换内容
  .animationDuration(300)            // 切换动画时长(ms)
  .vertical(false)                   // 是否垂直排列（用于侧边 Tab）
  .barBackgroundColor(Color.White)   // TabBar 背景色
  .onChange((index: number) => {})   // Tab 切换回调（必须更新 currentIndex）

// ---- TabContent 属性 ----
TabContent() { /* 页面内容 */ }
  .tabBar('标题文字')                // 简单文字 TabBar
  .tabBar(this.customBuilder(i))     // 自定义 @Builder TabBar

// ---- TabsController ----
const ctrl = new TabsController()
ctrl.changeIndex(2)                  // 编程式切换到第 3 个 Tab

// ---- Badge 角标（配合自定义 TabBar 使用） ----
Badge({
  count: 5,
  maxCount: 99,
  position: BadgePosition.RightTop,
  style: {
    fontSize: 10,
    badgeSize: 16,
    badgeColor: '#FF3B30'
  }
}) {
  Image($r('app.media.ic_tab'))
    .width(24)
    .height(24)
}

// ---- 常见搭配 ----
// 底部导航：barPosition.End + barMode.Fixed + scrollable(false)
// 顶部分类：barPosition.Start + barMode.Scrollable + scrollable(true)
// 侧边标签：vertical(true) + barPosition.Start
```

---

## V2 vs V1 速查表（Tabs 场景）

| 用途 | V2 | V1（不推荐） |
|---|---|---|
| 页面 struct | `@ComponentV2` | `@Component` |
| currentIndex 状态 | `@Local currentIndex: number = 0` | `@State currentIndex: number = 0` |
| Tab 内容子组件接收只读参数（如 badgeCount） | `@Param @Once badgeCount: number = 0` | `@Prop badgeCount: number = 0` |
| 子组件内部状态（如 messages 数组） | `@Local messages: string[] = []` | `@State messages: string[] = []` |
| Tab 状态运行时持久化 | `AppStorageV2.connect(Cls, key, factory)` | `@StorageLink('key')` |
| Tab 状态磁盘持久化 | `PersistenceV2.globalConnect({ type, key, defaultCreator })` | `PersistentStorage.persistProp + @StorageLink` |

---

## 跨文档参考

- [`v2-nav-patterns.md`](./v2-nav-patterns.md) — V2 Navigation 完整模式
- [`v2-advanced-nav-patterns.md`](./v2-advanced-nav-patterns.md) — V2 高级导航模式
- [`../SKILL.md`](../SKILL.md) — 决策树与陷阱总览
- `arkts-state-manager/references/v2-global-state.md` — `AppStorageV2 / PersistenceV2` 完整模板
