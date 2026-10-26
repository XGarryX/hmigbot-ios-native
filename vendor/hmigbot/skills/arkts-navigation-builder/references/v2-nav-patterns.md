# ArkTS V2 Navigation 完整模式参考

> 本文件为 **V2 主参考**（API 12+，`@ComponentV2 / @Local / @Param / @Event / @Provider / @Consumer / @ObservedV2 / AppStorageV2`），包含 ArkTS/HarmonyOS Navigation 组件的所有主要 V2 用法。**本项目锁 V2**。
>
> 每个示例均为完整可运行代码。所有示例基于 **API 12+** 推荐的 ArkTS V2 装饰器。
>
> V1 历史写法请见 [`nav-patterns.md`](./nav-patterns.md)（已加 legacy 标识）。
>
> **导航 API 在 V1/V2 中完全一致**：`Navigation / NavPathStack / NavDestination / pushPathByName / pop / popToName / clear / @Builder pageMap` 用法不变，**仅页面组件内的状态装饰器需要使用 V2**。

> **注意**：`@ohos.router` 在 API 12+ 已废弃。所有新代码必须使用本文件中的 Navigation + NavPathStack 方案。如需从 router 迁移到 Navigation，参阅 arkts-knowledge-verifier skill 的 `references/migration-patterns.md`。

> **⚠️ 传参写法（V2 严格模式必读）**：传参一律用 **`new XParam()` 类型化类实例**、取参一律用 **`as Object` widening + `instanceof`**。裸对象字面量 `pushPathByName('X', {...} as Record<string,string>)` 在 API 12+ 严格模式会编译失败（`arkts-no-untyped-obj-literals`）；裸 `const p = ctx.pathInfo.param` 会触发 `arkts-no-any-unknown`。完整规矩见 SKILL.md「⚠️ 编译硬规矩」。

---

## 1. 基础 Navigation + NavPathStack（V2）

最核心的导航模式：入口页面创建 NavPathStack，通过 `@Provider()` 注入，子页面用 `@Consumer()` 获取（V2 必须带括号 + Consumer 默认值）。

```typescript
// 路由参数类（V2 严格模式：传参/取参都基于类型化类，禁裸对象字面量）
class ProductDetailParam { productId: string = ''; productName: string = ''; }
class OrderConfirmParam { orderId: string = ''; from: string = ''; }
class PayResultParam { orderId: string = ''; status: string = ''; }

// 入口页面：包含 Navigation 容器和路由映射
@Entry
@ComponentV2
struct IndexPage {
  // V2：@Provider() 注入（必须带括号）
  @Provider('navPathStack') navPathStack: NavPathStack = new NavPathStack()

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
            // 跳转并传递参数（类型化 param 类实例，禁裸字面量）
            const detailParam = new ProductDetailParam()
            detailParam.productId = '10086'
            detailParam.productName = 'HarmonyOS 手机'
            this.navPathStack.pushPathByName('ProductDetail', detailParam)
          })

        Button('直接去订单确认')
          .width('80%')
          .onClick(() => {
            const orderParam = new OrderConfirmParam()
            orderParam.orderId = 'ORD-2024-001'
            this.navPathStack.pushPathByName('OrderConfirm', orderParam)
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
@ComponentV2
struct ProductDetailPage {
  // V2：@Consumer() 接收（必须带括号 + 默认值）
  @Consumer('navPathStack') navPathStack: NavPathStack = new NavPathStack()
  @Local productId: string = ''
  @Local productName: string = ''

  build() {
    NavDestination() {
      Column({ space: 16 }) {
        Text('商品ID: ' + this.productId)
          .fontSize(20)
        Text('商品名: ' + this.productName)
          .fontSize(20)

        Button('去下单')
          .onClick(() => {
            const nextParam = new OrderConfirmParam()
            nextParam.orderId = 'ORD-NEW'
            nextParam.from = 'detail'
            this.navPathStack.pushPathByName('OrderConfirm', nextParam)
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
      const obj = context.pathInfo.param as Object
      if (obj instanceof ProductDetailParam) {
        this.productId = obj.productId
        this.productName = obj.productName
      }
    })
  }
}

// 订单确认页
@ComponentV2
struct OrderConfirmPage {
  @Consumer('navPathStack') navPathStack: NavPathStack = new NavPathStack()
  @Local orderId: string = ''

  build() {
    NavDestination() {
      Column({ space: 16 }) {
        Text('订单号: ' + this.orderId)
          .fontSize(20)

        Button('确认支付')
          .onClick(() => {
            const payParam = new PayResultParam()
            payParam.orderId = this.orderId
            payParam.status = 'success'
            this.navPathStack.pushPathByName('PayResult', payParam)
          })

        Button('返回商品详情')
          .onClick(() => {
            this.navPathStack.popToName('ProductDetail')
          })
      }
      .width('100%')
      .padding(20)
    }
    .title('确认订单')
    .onReady((context: NavDestinationContext) => {
      const obj = context.pathInfo.param as Object
      if (obj instanceof OrderConfirmParam) {
        this.orderId = obj.orderId
      }
    })
  }
}

// 支付结果页
@ComponentV2
struct PayResultPage {
  @Consumer('navPathStack') navPathStack: NavPathStack = new NavPathStack()
  @Local status: string = ''

  build() {
    NavDestination() {
      Column({ space: 16 }) {
        Text(this.status === 'success' ? '支付成功' : '支付失败')
          .fontSize(24)
          .fontColor(this.status === 'success' ? '#00C853' : '#FF1744')

        Button('回到首页')
          .onClick(() => {
            this.navPathStack.clear()
          })
      }
      .width('100%')
      .height('100%')
      .justifyContent(FlexAlign.Center)
    }
    .title('支付结果')
    .onReady((context: NavDestinationContext) => {
      const obj = context.pathInfo.param as Object
      if (obj instanceof PayResultParam) {
        this.status = obj.status
      }
    })
  }
}
```

---

## 2. 动态路由注册（适合大型多模块项目，V2）

当页面超过 5 个时，if-else 路由映射不可维护。使用 `WrappedBuilder + Map` 实现动态注册。RouteMap 类本身与 V1 一致；只有页面组件用 V2 装饰器。

```typescript
// ============================================
// 文件: router/RouteMap.ets （注册表本身与 V1 相同）
// ============================================
export class RouteMap {
  private static builders: Map<string, WrappedBuilder<[object]>> = new Map()

  static register(name: string, builder: WrappedBuilder<[object]>): void {
    RouteMap.builders.set(name, builder)
  }

  static getBuilder(name: string): WrappedBuilder<[object]> | undefined {
    return RouteMap.builders.get(name)
  }

  static has(name: string): boolean {
    return RouteMap.builders.has(name)
  }

  static getAllRoutes(): string[] {
    return Array.from(RouteMap.builders.keys())
  }
}

// ============================================
// 文件: pages/ProfilePage.ets
// ============================================

@Builder
function ProfilePageBuilder(param: object) {
  ProfilePage()
}

const _registerProfile = (() => {
  RouteMap.register('ProfilePage', wrapBuilder(ProfilePageBuilder))
})()

@ComponentV2
struct ProfilePage {
  @Consumer('navPathStack') navPathStack: NavPathStack = new NavPathStack()
  @Local userName: string = ''

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

@ComponentV2
struct EditProfilePage {
  @Consumer('navPathStack') navPathStack: NavPathStack = new NavPathStack()
  @Local userName: string = ''

  build() {
    NavDestination() {
      Column({ space: 12 }) {
        TextInput({ text: this.userName, placeholder: '输入用户名' })
          .onChange((value: string) => {
            this.userName = value
          })

        Button('保存')
          .onClick(() => {
            // pop 可携带返回值给上一个页面
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

import './ProfilePage'
import './EditProfilePage'

@Entry
@ComponentV2
struct IndexPage {
  @Provider('navPathStack') navPathStack: NavPathStack = new NavPathStack()

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

### 2a. 多窗口（2in1）安全跳转：用 `pushDestinationByName` 而非 `pushPathByName`

自定义动态路由默认可用 `pushPathByName` 跳转。但**跨窗口场景（2in1 多窗口）必须改用 `pushDestinationByName`**：

```typescript
import { BusinessError } from '@kit.BasicServicesKit';

// ✅ 多窗口安全：pushDestinationByName 绑定并校验 UIContext 一致性
this.navPathStack.pushDestinationByName('ProfilePage', param)
  .catch((e: BusinessError) => { /* 路由不存在 / 上下文不匹配 → 兜底、重定向错误页 */ })
```
- 官方区别：`pushDestinationByName` **绑定上下文对象、调用时校验 UIContext 是否一致**；`pushPathByName` 不校验。
- 单窗口下两者**仅返回值不同**（pushDestinationByName 返回 `Promise`、可 `.catch` 路由失败）；**跨窗口**用 pushPathByName 可能把页面错配到别的窗口栈 → 必须用 pushDestinationByName。
- 与系统路由表用法一致，完整签名/防白屏见 `v2-system-routing.md`。

---

## 3. Navigation 模式（API 不变，V2 装饰器示例）

### 3a. Stack 模式（手机端，全屏页面切换）

```typescript
@Entry
@ComponentV2
struct StackModeExample {
  @Provider('navPathStack') navPathStack: NavPathStack = new NavPathStack()

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
    .mode(NavigationMode.Stack)
  }
}

@ComponentV2
struct StackSubPage {
  @Consumer('navPathStack') navPathStack: NavPathStack = new NavPathStack()

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
@ComponentV2
struct SplitModeExample {
  @Provider('navPathStack') navPathStack: NavPathStack = new NavPathStack()
  @Local mails: string[] = ['会议通知', '项目周报', '系统更新', '假期安排', '团建活动']

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
    .mode(NavigationMode.Split)
    .navBarWidth('35%')
    .navBarWidthRange([200, 400])
  }
}

@ComponentV2
struct MailDetailPage {
  @Consumer('navPathStack') navPathStack: NavPathStack = new NavPathStack()
  @Local mailTitle: string = ''
  @Local mailContent: string = ''

  build() {
    NavDestination() {
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
@ComponentV2
struct AutoModeExample {
  @Provider('navPathStack') navPathStack: NavPathStack = new NavPathStack()

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
    .mode(NavigationMode.Auto)
    .navBarWidth('40%')
  }
}

@ComponentV2
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

## 4. 页面生命周期（V2）

NavDestination 提供完整的页面生命周期回调。生命周期 API 本身与 V1 相同；只有状态装饰器是 V2。

```typescript
@ComponentV2
struct LifecycleDemoPage {
  @Consumer('navPathStack') navPathStack: NavPathStack = new NavPathStack()
  @Local pageId: string = ''
  @Local visitCount: number = 0

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
      let param = context.pathInfo.param as Record<string, string>
      this.pageId = param?.pageId ?? 'unknown'
      console.info(`[onReady] 页面创建, pageId=${this.pageId}`)
    })
    .onShown(() => {
      // 页面每次显示时触发
      this.visitCount++
      console.info(`[onShown] 页面显示, 第 ${this.visitCount} 次`)
    })
    .onHidden(() => {
      // 页面每次隐藏时触发
      console.info(`[onHidden] 页面隐藏`)
    })
    .onBackPressed(() => {
      // 用户按返回键时触发
      console.info(`[onBackPressed] 用户按返回`)
      return false
    })
  }
}
```

### 4a. 被页面级弹窗（DIALOG）覆盖时暂停/恢复：`onActive` / `onInactive`（API17+）

当一个 `NavDestinationMode.DIALOG` 页面盖到当前页上时，当前页**仍然可见**（DIALOG 默认透明）——所以 **`onHidden`/`onShown` 不会触发**，只会触发 `onInactive`（失去活跃）/ `onActive`（重新活跃）。要实现「被分享浮层/弹窗页覆盖时暂停播放、覆盖消失时恢复」，**必须用 onInactive/onActive**：

```typescript
NavDestination() {
  // 音频详情页 UI...
}
.onShown(() => { this.refreshProgress() })      // 本页进入路由栈可见：刷新进度
.onHidden(() => { this.reportDuration() })       // 本页离开路由栈：上报时长
.onInactive(() => { this.pausePlay() })          // 被 DIALOG 页覆盖、失去活跃 → 暂停（此时本页仍可见）
.onActive(() => { this.resumePlay() })           // DIALOG 页关闭、重新活跃 → 恢复

// 分享浮层是页面级 DIALOG（push 入栈的 NavDestination + mode DIALOG），不是组件级弹窗：
NavDestination() { /* 分享 UI */ }
  .mode(NavDestinationMode.DIALOG)
```
- 签名：`onActive(callback: Optional<Callback<NavDestinationActiveReason>>)` / `onInactive(...)`（回调参数可省，`.onActive(() => {})` 即可；需区分激活原因时再收 `(reason: NavDestinationActiveReason) => {}`）。
- ❌ **别用 `onHidden`/`onShown` 处理「被 DIALOG 覆盖暂停/恢复」**——DIALOG 覆盖时下层页仍可见、这俩根本不触发，暂停逻辑不会执行。`onShown`/`onHidden` 只管本页进出路由栈（进入刷新 / 离开上报），被覆盖态归 `onActive`/`onInactive`。

---

### 参数传递与接收的完整流程（V2）

```typescript
// ---- 发送方：传递参数 ----
@ComponentV2
struct SenderPage {
  @Consumer('navPathStack') navPathStack: NavPathStack = new NavPathStack()

  build() {
    NavDestination() {
      Button('打开带参数的页面')
        .onClick(() => {
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
@ComponentV2
struct ReceiverPage {
  @Consumer('navPathStack') navPathStack: NavPathStack = new NavPathStack()
  @Local userId: string = ''
  @Local action: string = ''

  build() {
    NavDestination() {
      Column({ space: 12 }) {
        Text('用户ID: ' + this.userId)
        Text('操作: ' + this.action)

        Button('完成并返回结果')
          .onClick(() => {
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
      let param = context.pathInfo.param as Record<string, string>
      this.userId = param?.userId ?? ''
      this.action = param?.action ?? ''
    })
  }
}
```

---

## 5. 嵌套导航（Tabs + Navigation 组合，V2）

真实应用常见模式：外层 Tabs 切换主功能区，每个 Tab 内嵌独立的 Navigation 实现页面跳转。

```typescript
@Entry
@ComponentV2
struct AppMainPage {
  @Local currentTabIndex: number = 0

  // 每个 Tab 使用独立的 NavPathStack，互不干扰
  @Provider('homeNavStack') homeNavStack: NavPathStack = new NavPathStack()
  @Provider('msgNavStack') msgNavStack: NavPathStack = new NavPathStack()

  @Builder
  homePageMap(name: string, param?: object) {
    if (name === 'HomeDetail') {
      HomeDetailPage()
    } else if (name === 'HomeSubDetail') {
      HomeSubDetailPage()
    }
  }

  @Builder
  msgPageMap(name: string, param?: object) {
    if (name === 'ChatPage') {
      ChatPage()
    }
  }

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
        .hideTitleBar(true)
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
    .scrollable(false)
    .onChange((index: number) => {
      this.currentTabIndex = index
    })
  }
}

// 首页详情
@ComponentV2
struct HomeDetailPage {
  @Consumer('homeNavStack') homeNavStack: NavPathStack = new NavPathStack()
  @Local itemId: string = ''

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
@ComponentV2
struct HomeSubDetailPage {
  @Consumer('homeNavStack') homeNavStack: NavPathStack = new NavPathStack()

  build() {
    NavDestination() {
      Column({ space: 12 }) {
        Text('二级详情页面')
          .fontSize(20)
        Button('回到首页列表')
          .onClick(() => {
            this.homeNavStack.clear()
          })
      }
      .padding(20)
    }
    .title('二级详情')
  }
}

// 聊天页面
@ComponentV2
struct ChatPage {
  @Consumer('msgNavStack') msgNavStack: NavPathStack = new NavPathStack()
  @Local chatWith: string = ''

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

### 5a. 详情页全屏覆盖底部标签栏（保留原生 Tabs）

上面每个 Tab 内嵌的 Navigation，其详情页默认只占 TabContent 区域、**盖不住底部标签栏**。要让详情**全屏覆盖标签栏**：不要为此放弃原生 Tabs 去手搓 Row 底栏，用一个 `AppStorageV2` 全局标志把 `Tabs` 的 `barHeight` 收成 0 即可。

```typescript
import { AppStorageV2 } from '@kit.ArkUI';   // 每个用到的文件各自 import

@ObservedV2
class TabBarFlag {
  @Trace detailFullscreen: boolean = false
}

// 外层入口：barHeight 随标志收起
@Local flag: TabBarFlag = AppStorageV2.connect(TabBarFlag, 'tabBarFlag', () => new TabBarFlag())!
// ...
Tabs({ barPosition: BarPosition.End, index: this.currentTabIndex }) {
  /* 内嵌 Navigation 的 TabContent（同 §5）... */
}
.barHeight(this.flag.detailFullscreen ? 0 : 56)   // 详情全屏时收起标签栏 → 覆盖

// 详情页 NavDestination：进入置 true、退出置 false
NavDestination() { /* ... */ }
  .onReady((ctx: NavDestinationContext) => {
    const obj = ctx.pathInfo.param as Object
    if (obj instanceof DetailParam) { this.itemId = obj.itemId }
    this.flag.detailFullscreen = true
  })
  .onDisAppear(() => { this.flag.detailFullscreen = false })
```
- ✅ 底栏是**原生 `Tabs` / `TabContent`**（不是手搓 `Row`）；详情靠内嵌 Navigation push、靠 `barHeight(0)` 覆盖标签栏；列表项跨组件共享同一 `@Provider/@Consumer('homeStack')` 实例。
- ❌ 别因为「要全屏覆盖」就整体改成自定义 `Row` 底栏 + `if/else` 切内容——那放弃了原生 Tabs 的手势/动画/角标能力（`v2-advanced-nav-patterns.md §3` 的手搓底栏是 MiniPlayer 沉浸场景的另一种取舍，不是标签导航的默认解）。

---

## 6. 自定义页面转场动画（V2）

Navigation 转场动画 API 与 V1 完全一致；只有页面组件用 V2 装饰器。

```typescript
@Entry
@ComponentV2
struct AnimatedNavExample {
  @Provider('navPathStack') navPathStack: NavPathStack = new NavPathStack()

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
      if (operation === NavigationOperation.PUSH) {
        return {
          timeout: 500,
          transition: (transitionProxy: NavigationTransitionProxy) => {
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
@ComponentV2
struct AnimatedPage {
  @Consumer('navPathStack') navPathStack: NavPathStack = new NavPathStack()

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

// 底部弹出页面
@ComponentV2
struct SlideUpPage {
  @Consumer('navPathStack') navPathStack: NavPathStack = new NavPathStack()

  build() {
    NavDestination() {
      Column({ space: 16 }) {
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
      .height('60%')
      .backgroundColor(Color.White)
      .borderRadius({ topLeft: 16, topRight: 16 })
    }
    .hideTitleBar(true)
    .mode(NavDestinationMode.DIALOG)
    .backgroundColor('rgba(0, 0, 0, 0.5)')
    .onBackPressed(() => {
      this.navPathStack.pop()
      return true
    })
  }
}
```

> DIALOG 模式是**页面级**弹窗（参与路由栈、被后续 push 覆盖、随 pop 销毁）；与之相对 `@CustomDialog`/`openCustomDialog` 默认全局级、恒盖路由页——Android Dialog 语义迁移的选型见 arkts-component-builder/references/v2-dialogs-and-sheets.md §2c。

---

## 速查：NavPathStack API 一览（V1/V2 完全一致）

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
stack.getParamByName('PageName')  // 获取指定页面的参数
stack.getIndexByName('PageName')  // 返回 Array<number>：所有同名页面的索引数组（非单个！）。判断存在用 .length>0，取首个用 [0]

// ---- 其他 ----
stack.moveToTop('PageName')       // 将栈中指定页面移到栈顶
stack.removeByName('PageName')    // 从栈中移除指定页面
```

---

## V2 vs V1 速查表（导航场景）

| 用途 | V2 | V1（不推荐） |
|---|---|---|
| 页面 struct | `@ComponentV2` | `@Component` |
| 页面内部状态（currentIndex / 参数缓存） | `@Local` | `@State` |
| 父→子单向传值（如 itemId） | `@Param @Once` 或 `@Param` | `@Prop` |
| 父↔子双向（如 selectedTab） | `@Param + @Event` 回调 | `@Link` |
| NavPathStack 跨层级共享 | `@Provider() / @Consumer()` | `@Provide / @Consume` |
| 跨组件状态（如 isFullPlayerVisible） | `@ObservedV2 + AppStorageV2.connect` | `@StorageLink` |
| 监听变化 | `@Monitor('prop') method(m: IMonitor)` | `@Watch('method')` |
| 路由参数类（推荐 V2 模式） | `@ObservedV2` 类 + `@Trace` 字段 | 普通 class（无装饰器） |

---

## 跨文档参考

- [`v2-tab-navigation.md`](./v2-tab-navigation.md) — V2 Tab 导航完整模式
- [`v2-advanced-nav-patterns.md`](./v2-advanced-nav-patterns.md) — V2 高级导航模式（路由参数类、FullPlayer 隐藏 Tab、路由常量管理）
- [`../SKILL.md`](../SKILL.md) — 决策树与陷阱总览
- `arkts-state-manager/references/v2-decorators.md` — V2 装饰器完整规则
