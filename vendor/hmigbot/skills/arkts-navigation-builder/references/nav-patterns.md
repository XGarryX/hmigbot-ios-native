# ArkTS Navigation 完整模式参考（**V1 历史文档 — Legacy**）

> ⚠️ **本项目锁 ArkTS V2**。本文档为 **V1 历史参考**（`@Component / @State / @Provide / @Consume / @StorageLink` 等），仅用于阅读老代码或迁移老项目时查阅。
>
> **新代码请使用 V2 装饰器**：参阅 [`v2-nav-patterns.md`](./v2-nav-patterns.md)（主参考）和 [`SKILL.md`](../SKILL.md)。
>
> 注：`Navigation / NavPathStack / NavDestination` API 本身在 V1/V2 中完全一致，仅页面组件内的状态装饰器需要从 V1 迁移到 V2。

> 本文件为 LLM 教学参考，包含 ArkTS/HarmonyOS Navigation 组件的所有主要用法。
> 每个示例均为完整可运行代码。
> 所有示例基于 **API 12+**。

> **注意**：`@ohos.router` 在 API 12+ 已废弃。所有新代码必须使用本文件中的 Navigation + NavPathStack 方案。如需从 router 迁移到 Navigation，参阅 arkts-knowledge-verifier skill 的 `references/migration-patterns.md`。

---

## 1. 基础 Navigation + NavPathStack

最核心的导航模式：入口页面创建 NavPathStack，通过 @Provide 注入，子页面用 @Consume 获取。

```typescript
// 入口页面：包含 Navigation 容器和路由映射
@Entry
@Component
struct IndexPage {
  // 创建导航栈并通过 @Provide 向下注入
  @Provide('navPathStack') navPathStack: NavPathStack = new NavPathStack()

  // 路由映射：将页面名称映射到对应的 Builder 组件
  @Builder
  pageMap(name: string, param?: object) {
    if (name === 'ProductDetail') {
      ProductDetailPage()
    } else if (name === 'OrderConfirm') {
      OrderConfirmPage()
    } else if (name === 'PayResult') {
      PayResultPage()
    }
  }

  build() {
    Navigation(this.navPathStack) {
      // 首页内容
      Column({ space: 16 }) {
        Text('商品列表')
          .fontSize(28)
          .fontWeight(FontWeight.Bold)

        Button('查看商品详情')
          .width('80%')
          .onClick(() => {
            // 跳转并传递参数
            this.navPathStack.pushPathByName('ProductDetail', {
              productId: '10086',
              productName: 'HarmonyOS 手机'
            } as Record<string, string>)
          })

        Button('直接去订单确认')
          .width('80%')
          .onClick(() => {
            this.navPathStack.pushPathByName('OrderConfirm', {
              orderId: 'ORD-2024-001'
            } as Record<string, string>)
          })
      }
      .width('100%')
      .height('100%')
      .justifyContent(FlexAlign.Center)
    }
    .navDestination(this.pageMap)   // 绑定路由映射
    .title('首页')                   // 导航栏标题
    .mode(NavigationMode.Stack)      // 手机端用 Stack 模式
  }
}

// 商品详情页 —— 接收参数、可继续前进或返回
@Component
struct ProductDetailPage {
  @Consume('navPathStack') navPathStack: NavPathStack
  @State productId: string = ''
  @State productName: string = ''

  build() {
    NavDestination() {
      Column({ space: 16 }) {
        Text('商品ID: ' + this.productId)
          .fontSize(20)
        Text('商品名: ' + this.productName)
          .fontSize(20)

        Button('去下单')
          .onClick(() => {
            // 继续前进到下一个页面
            this.navPathStack.pushPathByName('OrderConfirm', {
              orderId: 'ORD-NEW',
              from: 'detail'
            } as Record<string, string>)
          })

        Button('返回首页')
          .onClick(() => {
            this.navPathStack.pop()
          })
      }
      .width('100%')
      .padding(20)
    }
    .title('商品详情')
    .onReady((context: NavDestinationContext) => {
      // 在 onReady 中接收跳转传递的参数
      let param = context.pathInfo.param as Record<string, string>
      this.productId = param?.productId ?? ''
      this.productName = param?.productName ?? ''
    })
  }
}

// 订单确认页
@Component
struct OrderConfirmPage {
  @Consume('navPathStack') navPathStack: NavPathStack
  @State orderId: string = ''

  build() {
    NavDestination() {
      Column({ space: 16 }) {
        Text('订单号: ' + this.orderId)
          .fontSize(20)

        Button('确认支付')
          .onClick(() => {
            this.navPathStack.pushPathByName('PayResult', {
              orderId: this.orderId,
              status: 'success'
            } as Record<string, string>)
          })

        Button('返回商品详情')
          .onClick(() => {
            // popToName 可以回退到栈中指定名称的页面
            this.navPathStack.popToName('ProductDetail')
          })
      }
      .width('100%')
      .padding(20)
    }
    .title('确认订单')
    .onReady((context: NavDestinationContext) => {
      let param = context.pathInfo.param as Record<string, string>
      this.orderId = param?.orderId ?? ''
    })
  }
}

// 支付结果页
@Component
struct PayResultPage {
  @Consume('navPathStack') navPathStack: NavPathStack
  @State status: string = ''

  build() {
    NavDestination() {
      Column({ space: 16 }) {
        Text(this.status === 'success' ? '支付成功' : '支付失败')
          .fontSize(24)
          .fontColor(this.status === 'success' ? '#00C853' : '#FF1744')

        Button('回到首页')
          .onClick(() => {
            // clear() 清空整个导航栈，直接回到根页面
            this.navPathStack.clear()
          })
      }
      .width('100%')
      .height('100%')
      .justifyContent(FlexAlign.Center)
    }
    .title('支付结果')
    .onReady((context: NavDestinationContext) => {
      let param = context.pathInfo.param as Record<string, string>
      this.status = param?.status ?? ''
    })
  }
}
```

---

## 2. 动态路由注册（适合大型多模块项目）

当页面超过 5 个时，if-else 路由映射不可维护。使用 WrappedBuilder + Map 实现动态注册。

```typescript
// ============================================
// 文件: router/RouteMap.ets
// 路由注册表单例 —— 全局唯一，管理所有页面 Builder
// ============================================
export class RouteMap {
  // 存储所有已注册的页面 Builder
  private static builders: Map<string, WrappedBuilder<[object]>> = new Map()

  // 注册页面：页面文件加载时调用
  static register(name: string, builder: WrappedBuilder<[object]>): void {
    RouteMap.builders.set(name, builder)
  }

  // 获取页面 Builder：导航时调用
  static getBuilder(name: string): WrappedBuilder<[object]> | undefined {
    return RouteMap.builders.get(name)
  }

  // 检查页面是否已注册
  static has(name: string): boolean {
    return RouteMap.builders.has(name)
  }

  // 获取所有已注册的页面名称（调试用）
  static getAllRoutes(): string[] {
    return Array.from(RouteMap.builders.keys())
  }
}

// ============================================
// 文件: pages/ProfilePage.ets
// 每个页面文件自行注册到 RouteMap
// ============================================

// 1. 定义模块级 @Builder（必须是全局函数，不能是 struct 方法）
@Builder
function ProfilePageBuilder(param: object) {
  ProfilePage()
}

// 2. 利用 IIFE 在模块加载时自动注册
const _registerProfile = (() => {
  RouteMap.register('ProfilePage', wrapBuilder(ProfilePageBuilder))
})()

@Component
struct ProfilePage {
  @Consume('navPathStack') navPathStack: NavPathStack
  @State userName: string = ''

  build() {
    NavDestination() {
      Column({ space: 12 }) {
        Text('用户: ' + this.userName)
          .fontSize(22)

        Button('编辑资料')
          .onClick(() => {
            this.navPathStack.pushPathByName('EditProfilePage', {
              userName: this.userName
            } as Record<string, string>)
          })
      }
      .width('100%')
      .padding(20)
    }
    .title('个人主页')
    .onReady((context: NavDestinationContext) => {
      let param = context.pathInfo.param as Record<string, string>
      this.userName = param?.userName ?? '未知用户'
    })
  }
}

// ============================================
// 文件: pages/EditProfilePage.ets
// ============================================
@Builder
function EditProfilePageBuilder(param: object) {
  EditProfilePage()
}

const _registerEditProfile = (() => {
  RouteMap.register('EditProfilePage', wrapBuilder(EditProfilePageBuilder))
})()

@Component
struct EditProfilePage {
  @Consume('navPathStack') navPathStack: NavPathStack
  @State userName: string = ''

  build() {
    NavDestination() {
      Column({ space: 12 }) {
        TextInput({ text: this.userName, placeholder: '输入用户名' })
          .onChange((value: string) => {
            this.userName = value
          })

        Button('保存')
          .onClick(() => {
            // pop 可以携带返回值给上一个页面
            this.navPathStack.pop({ updatedName: this.userName } as Record<string, string>)
          })
      }
      .width('100%')
      .padding(20)
    }
    .title('编辑资料')
    .onReady((context: NavDestinationContext) => {
      let param = context.pathInfo.param as Record<string, string>
      this.userName = param?.userName ?? ''
    })
  }
}

// ============================================
// 文件: pages/Index.ets
// 入口页面 —— 使用动态路由
// ============================================

// 重要：必须 import 所有页面文件，确保自注册代码执行
import './ProfilePage'
import './EditProfilePage'

@Entry
@Component
struct IndexPage {
  @Provide('navPathStack') navPathStack: NavPathStack = new NavPathStack()

  // 动态路由映射 —— 无需 if-else，新增页面零修改
  @Builder
  pageMap(name: string, param?: object) {
    if (RouteMap.has(name)) {
      RouteMap.getBuilder(name)!.builder(param ?? ({} as object))
    }
  }

  build() {
    Navigation(this.navPathStack) {
      Column({ space: 16 }) {
        Text('动态路由示例')
          .fontSize(24)
          .fontWeight(FontWeight.Bold)

        Button('进入个人主页')
          .width('80%')
          .onClick(() => {
            this.navPathStack.pushPathByName('ProfilePage', {
              userName: '张三'
            } as Record<string, string>)
          })
      }
      .width('100%')
      .height('100%')
      .justifyContent(FlexAlign.Center)
    }
    .navDestination(this.pageMap)
    .title('首页')
    .mode(NavigationMode.Stack)
  }
}
```

---

## 3. Navigation 模式

### 3a. Stack 模式（手机端，全屏页面切换）

```typescript
@Entry
@Component
struct StackModeExample {
  @Provide('navPathStack') navPathStack: NavPathStack = new NavPathStack()

  @Builder
  pageMap(name: string, param?: object) {
    if (name === 'SubPage') {
      StackSubPage()
    }
  }

  build() {
    Navigation(this.navPathStack) {
      Column() {
        Text('Stack 模式')
          .fontSize(24)
        Text('页面全屏切换，适合手机')
          .fontSize(14)
          .fontColor('#666')
          .margin({ top: 8 })

        Button('进入子页面')
          .margin({ top: 20 })
          .onClick(() => {
            this.navPathStack.pushPathByName('SubPage', {} as object)
          })
      }
      .width('100%')
      .height('100%')
      .justifyContent(FlexAlign.Center)
    }
    .navDestination(this.pageMap)
    .title('Stack 模式演示')
    // Stack: 每次只显示一个页面，新页面覆盖旧页面
    .mode(NavigationMode.Stack)
  }
}

@Component
struct StackSubPage {
  @Consume('navPathStack') navPathStack: NavPathStack

  build() {
    NavDestination() {
      Text('这是子页面，全屏显示')
        .fontSize(20)
    }
    .title('子页面')
  }
}
```

### 3b. Split 模式（平板端，左右分栏）

```typescript
@Entry
@Component
struct SplitModeExample {
  @Provide('navPathStack') navPathStack: NavPathStack = new NavPathStack()

  // 模拟邮件列表数据
  @State mails: string[] = ['会议通知', '项目周报', '系统更新', '假期安排', '团建活动']

  @Builder
  pageMap(name: string, param?: object) {
    if (name === 'MailDetail') {
      MailDetailPage()
    }
  }

  build() {
    Navigation(this.navPathStack) {
      // 左侧：邮件列表（始终可见）
      List({ space: 1 }) {
        ForEach(this.mails, (mail: string, index: number) => {
          ListItem() {
            Text(mail)
              .fontSize(16)
              .width('100%')
              .padding(16)
              .backgroundColor(Color.White)
          }
          .onClick(() => {
            this.navPathStack.pushPathByName('MailDetail', {
              title: mail,
              content: `这是 "${mail}" 的详细内容...`
            } as Record<string, string>)
          })
        })
      }
      .width('100%')
      .height('100%')
      .backgroundColor('#F5F5F5')
    }
    .navDestination(this.pageMap)
    .title('收件箱')
    // Split: 左侧显示 Navigation 内容，右侧显示 NavDestination
    .mode(NavigationMode.Split)
    .navBarWidth('35%')         // 左侧导航栏占 35%
    .navBarWidthRange([200, 400]) // 左侧宽度可拖拽范围（vp）
  }
}

@Component
struct MailDetailPage {
  @Consume('navPathStack') navPathStack: NavPathStack
  @State mailTitle: string = ''
  @State mailContent: string = ''

  build() {
    NavDestination() {
      // 右侧：邮件详情
      Column({ space: 12 }) {
        Text(this.mailTitle)
          .fontSize(22)
          .fontWeight(FontWeight.Bold)
        Divider()
        Text(this.mailContent)
          .fontSize(16)
          .lineHeight(26)
      }
      .width('100%')
      .padding(24)
      .alignItems(HorizontalAlign.Start)
    }
    .title(this.mailTitle)
    .onReady((context: NavDestinationContext) => {
      let param = context.pathInfo.param as Record<string, string>
      this.mailTitle = param?.title ?? ''
      this.mailContent = param?.content ?? ''
    })
  }
}
```

### 3c. Auto 模式（自动适配手机/平板）

```typescript
@Entry
@Component
struct AutoModeExample {
  @Provide('navPathStack') navPathStack: NavPathStack = new NavPathStack()

  @Builder
  pageMap(name: string, param?: object) {
    if (name === 'AutoSubPage') {
      AutoSubPage()
    }
  }

  build() {
    Navigation(this.navPathStack) {
      Column({ space: 12 }) {
        Text('Auto 模式')
          .fontSize(24)
        Text('屏幕宽度 >= 600vp 时自动切换为 Split')
          .fontSize(14)
          .fontColor('#666')

        Button('打开子页面')
          .margin({ top: 20 })
          .onClick(() => {
            this.navPathStack.pushPathByName('AutoSubPage', {} as object)
          })
      }
      .width('100%')
      .height('100%')
      .justifyContent(FlexAlign.Center)
    }
    .navDestination(this.pageMap)
    .title('自适应导航')
    // Auto: 窄屏(< 600vp)用 Stack，宽屏(>= 600vp)用 Split
    .mode(NavigationMode.Auto)
    .navBarWidth('40%')  // Split 时左侧宽度
  }
}

@Component
struct AutoSubPage {
  build() {
    NavDestination() {
      Text('子页面内容')
        .fontSize(20)
    }
    .title('子页面')
  }
}
```

---

## 4. 页面生命周期

NavDestination 提供完整的页面生命周期回调，用于参数接收、数据加载、资源管理等。

```typescript
@Component
struct LifecycleDemoPage {
  @Consume('navPathStack') navPathStack: NavPathStack
  @State pageId: string = ''
  @State visitCount: number = 0

  build() {
    NavDestination() {
      Column({ space: 16 }) {
        Text('页面ID: ' + this.pageId)
          .fontSize(20)
        Text('显示次数: ' + this.visitCount)
          .fontSize(16)

        Button('进入下一页')
          .onClick(() => {
            this.navPathStack.pushPathByName('LifecycleDemoPage', {
              pageId: 'nested-' + Date.now()
            } as Record<string, string>)
          })

        Button('返回')
          .onClick(() => {
            this.navPathStack.pop()
          })
      }
      .width('100%')
      .padding(20)
    }
    .title('生命周期演示')
    // ---- 生命周期回调 ----
    .onReady((context: NavDestinationContext) => {
      // 页面首次创建时触发（仅一次）
      // 用途：接收跳转参数、初始化数据
      let param = context.pathInfo.param as Record<string, string>
      this.pageId = param?.pageId ?? 'unknown'
      console.info(`[onReady] 页面创建, pageId=${this.pageId}`)
    })
    .onShown(() => {
      // 页面每次显示时触发（包括从其他页面返回时）
      // 用途：刷新数据、恢复定时器、开始动画
      this.visitCount++
      console.info(`[onShown] 页面显示, 第 ${this.visitCount} 次`)
    })
    .onHidden(() => {
      // 页面每次隐藏时触发（被新页面覆盖、或切换到其他 Tab 时）
      // 用途：暂停动画、停止定时器、保存草稿
      console.info(`[onHidden] 页面隐藏`)
    })
    .onBackPressed(() => {
      // 用户按返回键时触发
      // 返回 true 表示拦截默认返回行为（自行处理）
      // 返回 false 表示不拦截，执行默认返回
      console.info(`[onBackPressed] 用户按返回`)

      // 示例：弹出确认对话框
      // 这里简单演示直接放行
      return false
    })
  }
}
```

### 参数传递与接收的完整流程

```typescript
// ---- 发送方：传递参数 ----
@Component
struct SenderPage {
  @Consume('navPathStack') navPathStack: NavPathStack

  build() {
    NavDestination() {
      Button('打开带参数的页面')
        .onClick(() => {
          // pushPathByName 的第二个参数即为传递的数据
          this.navPathStack.pushPathByName('ReceiverPage', {
            userId: '12345',
            action: 'edit',
            timestamp: Date.now().toString()
          } as Record<string, string>)
        })
    }
    .title('发送方')
  }
}

// ---- 接收方：获取参数 ----
@Component
struct ReceiverPage {
  @Consume('navPathStack') navPathStack: NavPathStack
  @State userId: string = ''
  @State action: string = ''

  build() {
    NavDestination() {
      Column({ space: 12 }) {
        Text('用户ID: ' + this.userId)
        Text('操作: ' + this.action)

        Button('完成并返回结果')
          .onClick(() => {
            // pop 可携带返回值
            this.navPathStack.pop({
              result: 'saved',
              modifiedUserId: this.userId
            } as Record<string, string>)
          })
      }
      .padding(20)
    }
    .title('接收方')
    .onReady((context: NavDestinationContext) => {
      // context.pathInfo.param 包含跳转时传递的所有参数
      let param = context.pathInfo.param as Record<string, string>
      this.userId = param?.userId ?? ''
      this.action = param?.action ?? ''
    })
  }
}
```

---

## 5. 嵌套导航（Tabs + Navigation 组合）

真实应用常见模式：外层 Tabs 切换主功能区，每个 Tab 内嵌独立的 Navigation 实现页面跳转。

```typescript
@Entry
@Component
struct AppMainPage {
  @State currentTabIndex: number = 0

  // 每个 Tab 使用独立的 NavPathStack，互不干扰
  @Provide('homeNavStack') homeNavStack: NavPathStack = new NavPathStack()
  @Provide('msgNavStack') msgNavStack: NavPathStack = new NavPathStack()

  // ---- 首页 Tab 的路由映射 ----
  @Builder
  homePageMap(name: string, param?: object) {
    if (name === 'HomeDetail') {
      HomeDetailPage()
    } else if (name === 'HomeSubDetail') {
      HomeSubDetailPage()
    }
  }

  // ---- 消息 Tab 的路由映射 ----
  @Builder
  msgPageMap(name: string, param?: object) {
    if (name === 'ChatPage') {
      ChatPage()
    }
  }

  // ---- 自定义 TabBar ----
  @Builder
  tabBarBuilder(title: string, index: number) {
    Column() {
      Text(title)
        .fontSize(14)
        .fontColor(this.currentTabIndex === index ? '#007DFF' : '#999')
    }
    .width('100%')
    .height('100%')
    .justifyContent(FlexAlign.Center)
  }

  build() {
    Tabs({ barPosition: BarPosition.End, index: this.currentTabIndex }) {
      // ---- Tab 1：首页（内嵌 Navigation） ----
      TabContent() {
        Navigation(this.homeNavStack) {
          Column({ space: 12 }) {
            Text('首页内容')
              .fontSize(24)
            Button('查看详情')
              .onClick(() => {
                this.homeNavStack.pushPathByName('HomeDetail', {
                  itemId: '001'
                } as Record<string, string>)
              })
          }
          .width('100%')
          .height('100%')
          .justifyContent(FlexAlign.Center)
        }
        .navDestination(this.homePageMap)
        .mode(NavigationMode.Stack)
        .hideTitleBar(true)  // Tab 内的 Navigation 通常隐藏标题栏
      }
      .tabBar(this.tabBarBuilder('首页', 0))

      // ---- Tab 2：消息（内嵌 Navigation） ----
      TabContent() {
        Navigation(this.msgNavStack) {
          Column({ space: 12 }) {
            Text('消息列表')
              .fontSize(24)
            Button('打开聊天')
              .onClick(() => {
                this.msgNavStack.pushPathByName('ChatPage', {
                  chatWith: '李四'
                } as Record<string, string>)
              })
          }
          .width('100%')
          .height('100%')
          .justifyContent(FlexAlign.Center)
        }
        .navDestination(this.msgPageMap)
        .mode(NavigationMode.Stack)
        .hideTitleBar(true)
      }
      .tabBar(this.tabBarBuilder('消息', 1))

      // ---- Tab 3：我的（无需内部导航） ----
      TabContent() {
        Column() {
          Text('个人中心')
            .fontSize(24)
        }
        .width('100%')
        .height('100%')
        .justifyContent(FlexAlign.Center)
      }
      .tabBar(this.tabBarBuilder('我的', 2))
    }
    .barHeight(56)
    .scrollable(false)   // 禁止滑动切换 Tab
    .onChange((index: number) => {
      this.currentTabIndex = index
    })
  }
}

// 首页详情
@Component
struct HomeDetailPage {
  @Consume('homeNavStack') homeNavStack: NavPathStack
  @State itemId: string = ''

  build() {
    NavDestination() {
      Column({ space: 12 }) {
        Text('首页详情: ' + this.itemId)
          .fontSize(20)
        Button('继续深入')
          .onClick(() => {
            this.homeNavStack.pushPathByName('HomeSubDetail', {} as object)
          })
      }
      .padding(20)
    }
    .title('详情')
    .onReady((context: NavDestinationContext) => {
      let param = context.pathInfo.param as Record<string, string>
      this.itemId = param?.itemId ?? ''
    })
  }
}

// 首页二级详情
@Component
struct HomeSubDetailPage {
  @Consume('homeNavStack') homeNavStack: NavPathStack

  build() {
    NavDestination() {
      Column({ space: 12 }) {
        Text('二级详情页面')
          .fontSize(20)
        Button('回到首页列表')
          .onClick(() => {
            // 清空首页 Tab 的导航栈
            this.homeNavStack.clear()
          })
      }
      .padding(20)
    }
    .title('二级详情')
  }
}

// 聊天页面
@Component
struct ChatPage {
  @Consume('msgNavStack') msgNavStack: NavPathStack
  @State chatWith: string = ''

  build() {
    NavDestination() {
      Column() {
        Text('与 ' + this.chatWith + ' 的聊天')
          .fontSize(20)
      }
      .padding(20)
    }
    .title(this.chatWith)
    .onReady((context: NavDestinationContext) => {
      let param = context.pathInfo.param as Record<string, string>
      this.chatWith = param?.chatWith ?? ''
    })
  }
}
```

---

## 6. 自定义页面转场动画

Navigation 支持自定义 NavDestination 的进场/退场动画效果。

```typescript
@Entry
@Component
struct AnimatedNavExample {
  @Provide('navPathStack') navPathStack: NavPathStack = new NavPathStack()

  @Builder
  pageMap(name: string, param?: object) {
    if (name === 'AnimatedPage') {
      AnimatedPage()
    } else if (name === 'SlideUpPage') {
      SlideUpPage()
    }
  }

  build() {
    Navigation(this.navPathStack) {
      Column({ space: 20 }) {
        Text('转场动画演示')
          .fontSize(24)

        Button('水平滑入页面')
          .onClick(() => {
            this.navPathStack.pushPathByName('AnimatedPage', {} as object)
          })

        Button('底部弹出页面')
          .onClick(() => {
            this.navPathStack.pushPathByName('SlideUpPage', {} as object)
          })
      }
      .width('100%')
      .height('100%')
      .justifyContent(FlexAlign.Center)
    }
    .navDestination(this.pageMap)
    .title('动画导航')
    .mode(NavigationMode.Stack)
    // 自定义全局转场动画
    .customNavContentTransition((from: NavContentInfo, to: NavContentInfo, operation: NavigationOperation) => {
      // 判断是 push 还是 pop 操作，返回不同动画
      if (operation === NavigationOperation.PUSH) {
        // push 时：新页面从右侧滑入
        return {
          timeout: 500,      // 动画超时时间（ms）
          transition: (transitionProxy: NavigationTransitionProxy) => {
            // 使用 animateTo 执行动画
            animateTo({
              duration: 350,
              curve: Curve.EaseInOut,
              onFinish: () => {
                transitionProxy.finishTransition()
              }
            }, () => {
              transitionProxy.to.translate = { x: 0 }
            })
          },
          onTransitionEnd: () => {
            console.info('Push 动画完成')
          }
        } as NavigationAnimatedTransition
      } else {
        // pop 时：当前页面向右滑出
        return {
          timeout: 500,
          transition: (transitionProxy: NavigationTransitionProxy) => {
            animateTo({
              duration: 300,
              curve: Curve.EaseIn,
              onFinish: () => {
                transitionProxy.finishTransition()
              }
            }, () => {
              transitionProxy.from.translate = { x: '100%' }
            })
          }
        } as NavigationAnimatedTransition
      }
    })
  }
}

// 水平滑入页面
@Component
struct AnimatedPage {
  @Consume('navPathStack') navPathStack: NavPathStack

  build() {
    NavDestination() {
      Column({ space: 16 }) {
        Text('水平滑入的页面')
          .fontSize(22)

        Button('返回')
          .onClick(() => {
            this.navPathStack.pop()
          })
      }
      .width('100%')
      .height('100%')
      .justifyContent(FlexAlign.Center)
      .backgroundColor('#E3F2FD')
    }
    .title('滑入页面')
    .hideTitleBar(true)
  }
}

// 底部弹出页面 —— 使用 NavDestination 的 mode 实现弹窗式页面
@Component
struct SlideUpPage {
  @Consume('navPathStack') navPathStack: NavPathStack

  build() {
    NavDestination() {
      Column({ space: 16 }) {
        // 顶部拖拽条
        Row()
          .width(40)
          .height(4)
          .borderRadius(2)
          .backgroundColor('#CCC')
          .margin({ top: 12 })

        Text('底部弹出的页面')
          .fontSize(22)
          .margin({ top: 20 })

        Blank()

        Button('关闭')
          .width('80%')
          .margin({ bottom: 34 })
          .onClick(() => {
            this.navPathStack.pop()
          })
      }
      .width('100%')
      .height('60%')          // 只占屏幕 60% 高度
      .backgroundColor(Color.White)
      .borderRadius({ topLeft: 16, topRight: 16 })
    }
    .hideTitleBar(true)
    // DIALOG 模式：页面以弹窗形式展示，背景半透明
    .mode(NavDestinationMode.DIALOG)
    .backgroundColor('rgba(0, 0, 0, 0.5)')  // 半透明遮罩
    .onBackPressed(() => {
      this.navPathStack.pop()
      return true
    })
  }
}
```

> DIALOG 模式是**页面级**弹窗（参与路由栈、被后续 push 覆盖、随 pop 销毁）；与之相对 `@CustomDialog`/`openCustomDialog` 默认全局级、恒盖路由页——Android Dialog 语义迁移的选型见 arkts-component-builder/references/v2-dialogs-and-sheets.md §2c。

---

## 速查：NavPathStack API 一览

```typescript
const stack = new NavPathStack()

// ---- 前进操作 ----
stack.pushPathByName('PageName', paramObject)         // 跳转到指定页面
stack.pushPathByName('PageName', param, onPop)        // 跳转，并监听目标页面返回
stack.pushPath({ name: 'PageName', param: obj })      // 等价写法
stack.replacePath({ name: 'NewPage', param: obj })    // 替换当前页面（不入栈）

// ---- 后退操作 ----
stack.pop()                       // 返回上一页
stack.pop(resultObject)           // 返回上一页并携带返回值
stack.popToName('PageName')       // 回退到栈中指定名称的页面
stack.popToIndex(0)               // 回退到栈中指定索引的页面
stack.clear()                     // 清空栈，回到根页面

// ---- 栈信息查询 ----
stack.size()                      // 当前栈深度
stack.getAllPathName()            // 获取所有页面名称数组
stack.getParamByName('PageName') // 获取指定页面的参数
stack.getIndexByName('PageName') // 获取指定页面在栈中的索引

// ---- 其他 ----
stack.moveToTop('PageName')      // 将栈中指定页面移到栈顶
stack.removeByName('PageName')   // 从栈中移除指定页面
```
