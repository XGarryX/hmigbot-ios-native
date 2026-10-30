# ArkTS Tab 导航完整模式参考（**V1 历史文档 — Legacy**）

> ⚠️ **本项目锁 ArkTS V2**。本文档为 **V1 历史参考**（`@Component / @State / @Prop / @StorageLink` 等），仅用于阅读老代码或迁移老项目时查阅。
>
> **新代码请使用 V2 装饰器**：参阅 [`v2-tab-navigation.md`](./v2-tab-navigation.md)（主参考）和 [`SKILL.md`](../SKILL.md)。
>
> 注：`Tabs / TabContent / TabsController` API 本身在 V1/V2 中完全一致，仅状态装饰器需要从 V1 迁移到 V2。Tab 状态持久化（V1 用 `@StorageLink + PersistentStorage`）在 V2 中改用 `AppStorageV2.connect / PersistenceV2.globalConnect`。

> 本文件为 LLM 教学参考，包含 ArkTS/HarmonyOS Tabs 组件的所有主要用法。
> 每个示例均为完整可运行代码。

---

## 1. 基础 Tabs（最小示例）

最简单的 Tabs 用法，使用内置文字 TabBar。

```typescript
@Entry
@Component
struct BasicTabsExample {
  @State currentIndex: number = 0

  build() {
    // barPosition: 控制 TabBar 位置
    // BarPosition.End = 底部, BarPosition.Start = 顶部
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
      .tabBar('首页')   // 最简写法：直接传字符串

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
    .scrollable(false)         // 禁止左右滑动切换
    .animationDuration(300)    // Tab 切换动画时长（ms）
    .onChange((index: number) => {
      // 必须更新 currentIndex，否则选中状态不同步
      this.currentIndex = index
    })
  }
}
```

---

## 2. 自定义 TabBar（图标 + 文字 + 角标）

真实应用必备：自定义图标、选中/未选中颜色切换、消息角标。

```typescript
// Tab 项的数据结构
interface TabItemInfo {
  title: string
  icon: Resource          // 未选中图标
  selectedIcon: Resource  // 选中图标
  badgeCount: number      // 角标数量，0 表示不显示
}

@Entry
@Component
struct CustomTabBarExample {
  @State currentIndex: number = 0

  // Tab 配置数据
  private tabItems: TabItemInfo[] = [
    {
      title: '首页',
      icon: $r('app.media.ic_home'),
      selectedIcon: $r('app.media.ic_home_filled'),
      badgeCount: 0
    },
    {
      title: '发现',
      icon: $r('app.media.ic_discover'),
      selectedIcon: $r('app.media.ic_discover_filled'),
      badgeCount: 0
    },
    {
      title: '消息',
      icon: $r('app.media.ic_message'),
      selectedIcon: $r('app.media.ic_message_filled'),
      badgeCount: 5  // 有 5 条未读消息
    },
    {
      title: '我的',
      icon: $r('app.media.ic_mine'),
      selectedIcon: $r('app.media.ic_mine_filled'),
      badgeCount: 0
    }
  ]

  // 自定义 TabBar 构建器
  // 注意：@Builder 方法中使用 this 引用组件状态
  @Builder
  tabItemBuilder(item: TabItemInfo, index: number) {
    Column() {
      // ---- 图标区域（含角标） ----
      Badge({
        count: item.badgeCount,          // 角标数字
        position: BadgePosition.RightTop,
        style: {
          fontSize: 10,
          badgeSize: 16,
          badgeColor: '#FF3B30'          // 角标背景色（红色）
        }
      }) {
        Image(this.currentIndex === index ? item.selectedIcon : item.icon)
          .width(24)
          .height(24)
          .fillColor(this.currentIndex === index ? '#007DFF' : '#8E8E93')
      }

      // ---- 标题文字 ----
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

      // ---- 首页 Tab ----
      TabContent() {
        HomeTabContent()
      }
      .tabBar(this.tabItemBuilder(this.tabItems[0], 0))

      // ---- 发现 Tab ----
      TabContent() {
        DiscoverTabContent()
      }
      .tabBar(this.tabItemBuilder(this.tabItems[1], 1))

      // ---- 消息 Tab ----
      TabContent() {
        MessageTabContent({ badgeCount: this.tabItems[2].badgeCount })
      }
      .tabBar(this.tabItemBuilder(this.tabItems[2], 2))

      // ---- 我的 Tab ----
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

@Component
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

@Component
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

@Component
struct MessageTabContent {
  @Prop badgeCount: number = 0

  // 模拟消息数据
  @State messages: string[] = ['张三: 明天开会', '李四: 收到', '系统通知: 版本更新', '王五: 周末聚餐', '赵六: OK']

  build() {
    Column() {
      // 消息列表
      List({ space: 1 }) {
        ForEach(this.messages, (msg: string) => {
          ListItem() {
            Row() {
              // 头像占位
              Column()
                .width(44)
                .height(44)
                .borderRadius(22)
                .backgroundColor('#E0E0E0')
                .margin({ right: 12 })

              // 消息内容
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

@Component
struct MineTabContent {
  build() {
    Column({ space: 12 }) {
      // 头像
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

## 3. 可滚动 Tabs（多分类场景）

当 Tab 数量较多时（如新闻分类、商品类目），使用可滚动 Tabs。

```typescript
@Entry
@Component
struct ScrollableTabsExample {
  @State currentIndex: number = 0

  // 大量分类数据
  private categories: string[] = [
    '推荐', '热点', '科技', '体育', '娱乐',
    '财经', '教育', '健康', '旅游', '美食',
    '汽车', '时尚', '游戏', '音乐', '影视'
  ]

  // 自定义顶部 Tab 样式（胶囊/下划线风格）
  @Builder
  categoryTabBuilder(category: string, index: number) {
    Column() {
      Text(category)
        .fontSize(this.currentIndex === index ? 16 : 14)
        .fontWeight(this.currentIndex === index ? FontWeight.Bold : FontWeight.Normal)
        .fontColor(this.currentIndex === index ? '#333' : '#999')
        .padding({ left: 12, right: 12 })

      // 选中指示器（底部短线）
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
            // 每个分类的内容
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
      .barMode(BarMode.Scrollable)     // 关键：启用可滚动模式
      .barHeight(48)
      .scrollable(true)                 // 允许左右滑动切换内容
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

## 4. Tabs + Swiper 联动（可滑动切换内容）

某些场景需要 Tab 切换和手势滑动内容联动（如图片浏览、内容推荐卡片）。

```typescript
@Entry
@Component
struct TabSwiperExample {
  @State currentIndex: number = 0

  // Swiper 控制器，用于从 Tab 点击驱动 Swiper 切换
  private swiperController: SwiperController = new SwiperController()

  private tabTitles: string[] = ['关注', '推荐', '热榜']

  // Tab 样式
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
      // ---- 顶部 Tab 栏 ----
      Row() {
        ForEach(this.tabTitles, (title: string, index: number) => {
          Column() {
            this.topTabBuilder(title, index)
          }
          .onClick(() => {
            this.currentIndex = index
            // 点击 Tab 时驱动 Swiper 切换
            this.swiperController.changeIndex(index)
          })
        })
      }
      .width('100%')
      .height(48)
      .justifyContent(FlexAlign.Center)
      .backgroundColor(Color.White)

      Divider().color('#F0F0F0')

      // ---- 可滑动内容区域（Swiper） ----
      Swiper(this.swiperController) {
        // 关注频道
        FollowFeedContent()

        // 推荐频道
        RecommendFeedContent()

        // 热榜频道
        HotFeedContent()
      }
      .index(this.currentIndex)
      .loop(false)                   // 不循环
      .indicator(false)              // 隐藏指示器点
      .cachedCount(1)                // 预加载相邻 1 个页面
      .onChange((index: number) => {
        // Swiper 滑动时同步更新 Tab 选中状态
        this.currentIndex = index
      })
      .layoutWeight(1)
    }
    .width('100%')
    .height('100%')
  }
}

// ---- 各频道内容组件 ----

@Component
struct FollowFeedContent {
  @State items: string[] = ['关注作者1的新文章', '关注作者2的视频', '关注话题更新']

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

@Component
struct RecommendFeedContent {
  @State items: string[] = ['推荐内容1: HarmonyOS 开发入门', '推荐内容2: ArkTS 最佳实践', '推荐内容3: 组件化架构']

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

@Component
struct HotFeedContent {
  @State hotItems: string[] = ['#1 热搜话题A', '#2 热搜话题B', '#3 热搜话题C', '#4 热搜话题D']

  build() {
    List({ space: 8 }) {
      ForEach(this.hotItems, (item: string, index: number) => {
        ListItem() {
          Row({ space: 12 }) {
            // 排名序号
            Text((index + 1).toString())
              .fontSize(18)
              .fontWeight(FontWeight.Bold)
              .fontColor(index < 3 ? '#FF3B30' : '#999')  // 前三名红色
              .width(30)
              .textAlign(TextAlign.Center)

            // 话题标题
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

## 5. Tab 状态持久化（记住上次选中的 Tab）

使用 AppStorage 或 PersistentStorage 在应用重启后恢复上次的 Tab 位置。

```typescript
// ==============================
// 方案 A：AppStorage（仅应用内生命周期保持）
// 适合场景：从子页面返回时恢复 Tab
// ==============================

// 在 EntryAbility 的 onCreate 中初始化
// AppStorage.setOrCreate('lastTabIndex', 0)

@Entry
@Component
struct AppStorageTabExample {
  // @StorageLink 双向绑定 AppStorage 中的值
  // 切换 Tab 时自动保存，返回页面时自动恢复
  @StorageLink('lastTabIndex') currentIndex: number = 0

  build() {
    Tabs({ barPosition: BarPosition.End, index: this.currentIndex }) {
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
      // @StorageLink 自动将值写回 AppStorage
      this.currentIndex = index
    })
  }
}

// ==============================
// 方案 B：PersistentStorage（应用重启后仍保持）
// 适合场景：用户习惯记忆
// ==============================

// 在 EntryAbility 的 onCreate 中初始化持久化存储
// PersistentStorage.persistProp('savedTabIndex', 0)

@Entry
@Component
struct PersistentTabExample {
  // PersistentStorage 的值也通过 @StorageLink 访问
  // 区别在于 PersistentStorage 会将值持久化到磁盘
  @StorageLink('savedTabIndex') currentIndex: number = 0

  build() {
    Tabs({ barPosition: BarPosition.End, index: this.currentIndex }) {
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
      this.currentIndex = index
    })
  }
}

// ==============================
// 方案 C：TabsController 编程式切换
// 适合场景：从通知跳转到指定 Tab、深度链接
// ==============================

@Entry
@Component
struct ControllerTabExample {
  @State currentIndex: number = 0

  // TabsController 用于编程式切换 Tab
  private tabsController: TabsController = new TabsController()

  build() {
    Column() {
      // 顶部操作区 —— 模拟从外部跳转到指定 Tab
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

      // Tab 内容区
      Tabs({
        barPosition: BarPosition.End,
        index: this.currentIndex,
        controller: this.tabsController  // 绑定控制器
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

## 速查：Tabs API 一览

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
  count: 5,                          // 角标数字，0 时不显示
  maxCount: 99,                      // 超过显示 "99+"
  position: BadgePosition.RightTop,  // 角标位置
  style: {
    fontSize: 10,
    badgeSize: 16,
    badgeColor: '#FF3B30'            // 红色角标
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
