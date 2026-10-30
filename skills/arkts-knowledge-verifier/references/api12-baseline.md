# API 12 基线参考

> API 12（HarmonyOS 5.0.0）是所有 NEXT 项目的最低基线版本。
> 本文件详细记录 API 12 的所有关键规则，作为代码生成的基础参照。
>
> **⚠️ V2 项目说明**：本项目锁 ArkTS V2，下文 §2「状态装饰器规则」涉及的 `@State / @Prop / @Link / @Track` 是 **V1 历史装饰器**，仅用于阅读老代码或迁移老项目。**新代码请使用 V2 装饰器**（`@Local / @Param / @Param+@Once / @Param+@Event / @Trace`），完整规则见 [`v2-decorator-rules.md`](./v2-decorator-rules.md)，迁移规则见 [`v2-migration-patterns.md`](./v2-migration-patterns.md)。下文 §3「导航方案」中的 `@Component / @State` 同理（结构示例保留 V1 是为了与已有老项目对照；V2 实际写法是 `@ComponentV2 / @Local`，详见后文 V2 注解段）。

---

## 1. 导入规则

### 必须使用 @kit.* 导入

API 12+ 项目应统一使用 `@kit.*` 格式导入。`@ohos.*` 格式仍可编译通过但不推荐。

```typescript
// ✓ 推荐
import { AbilityConstant, UIAbility, Want } from '@kit.AbilityKit'
import { hilog } from '@kit.PerformanceAnalysisKit'
import { window } from '@kit.ArkUI'
import { http } from '@kit.NetworkKit'
import { connection } from '@kit.NetworkKit'
import { preferences } from '@kit.ArkData'
import { common } from '@kit.AbilityKit'
import { image } from '@kit.ImageKit'
import { fileIo } from '@kit.CoreFileKit'

// ✗ 不推荐（旧格式）
import router from '@ohos.router'
import { http } from '@ohos.net.http'
import dataPreferences from '@ohos.data.preferences'
```

### 常用 Kit 分类

| Kit 名称 | 包含模块 | 用途 |
|---|---|---|
| `@kit.ArkUI` | window, curves, matrix4, animator, measure, promptAction, font, mediaquery | UI 框架 |
| `@kit.AbilityKit` | UIAbility, Want, AbilityConstant, common, wantAgent | 应用能力 |
| `@kit.NetworkKit` | http, connection, socket, webSocket | 网络通信 |
| `@kit.ArkData` | preferences, relationalStore, distributedKVStore | 数据存储 |
| `@kit.PerformanceAnalysisKit` | hilog, hidebug | 性能分析 |
| `@kit.ImageKit` | image | 图片处理 |
| `@kit.MediaKit` | media | 媒体播放 |
| `@kit.CameraKit` | camera | 相机 |
| `@kit.AudioKit` | audio | 音频 |
| `@kit.CoreFileKit` | fileIo, picker | 文件操作 |
| `@kit.BasicServicesKit` | pasteboard, request | 基础服务 |
| `@kit.NotificationKit` | notification | 通知 |
| `@kit.LocationKit` | geoLocationManager | 定位 |
| `@kit.SensorServiceKit` | vibrator, sensor | 传感器 |
| `@kit.BackgroundTasksKit` | backgroundTaskManager | 后台任务 |

---

## 2. 状态装饰器规则（V1 历史 — Legacy）

> ⚠️ 下文为 **V1 装饰器** 在 API 12+ 的初始化与语法规则历史背景。**本项目锁 V2**，新代码请使用 V2 等价：
> - `@State` → `@Local`
> - `@Prop` → `@Param + @Once`（只读）/ `@Param`（可改）
> - `@Link` → `@Param + @Event` 回调
> - `@Track` → `@Trace`（用在 `@ObservedV2` 类的属性上）
> - `@Reusable` → `@ReusableV2`
>
> 完整 V2 装饰器规则见 [`v2-decorator-rules.md`](./v2-decorator-rules.md)。

### @Prop — 必须本地初始化（V1 legacy；V2 用 @Param）

```typescript
// API 11 及之前：可以不初始化
@Prop title: string

// API 12+：必须提供默认值
@Prop title: string = ''
@Prop count: number = 0
@Prop isActive: boolean = false
@Prop items: string[] = []
```

**为什么**：编译器在 API 12 加强了类型安全检查，@Prop 不再允许 undefined 状态。

### @Link — 传参语法变化（V1 legacy；V2 已无 @Link）

```typescript
// API 11 及之前：用 $ 前缀传引用
Parent:
  Child({ linkVar: $parentVar })

// API 12+（推荐）：直接传值
Parent:
  Child({ linkVar: this.parentVar })
```

两种写法在 API 12 都可以编译，但新项目统一使用直接传值方式。

### @Track — 新增装饰器（V1 legacy；V2 用 @Trace）

```typescript
@Observed
class DataModel {
  @Track name: string = ''      // 变化触发 UI 刷新
  @Track avatar: string = ''    // 变化触发 UI 刷新
  cacheData: string = ''        // 变化不触发 UI 刷新
  requestCount: number = 0      // 变化不触发 UI 刷新
}
```

**规则**：一旦类中有任何属性使用 @Track，则只有被 @Track 装饰的属性才触发 UI 刷新。

### @Reusable — 新增装饰器（V1 legacy；V2 用 @ReusableV2 + @ComponentV2）

```typescript
@Reusable
@Component
struct ListItemView {
  @State item: ItemModel = new ItemModel()

  aboutToReuse(params: Record<string, Object>): void {
    // 组件被复用时，更新数据
    this.item = params['item'] as ItemModel
  }

  build() {
    // ...
  }
}
```

配合 LazyForEach 使用，减少组件创建/销毁开销。

---

## 3. 导航方案

> **Navigation 容器 / NavPathStack / NavDestination / pageMap Builder 本身是 V1/V2 通用 API**，仅装饰器需要按 V1/V2 切换：父子组件用 `@ComponentV2 + @Local + @Provider() + @Consumer()`（V2）或 `@Component + @State + @Provide + @Consume`（V1）。

### Navigation 标准模板 — V2 写法（项目锁 V2，推荐）

```typescript
@Entry
@ComponentV2
struct MainPage {
  @Provider('navPathStack') navPathStack: NavPathStack = new NavPathStack()

  @Builder
  pageMap(name: string, param?: object) {
    if (name === 'DetailPage') {
      DetailPage()
    }
  }

  build() {
    Navigation(this.navPathStack) {
      // 首页内容
    }
    .navDestination(this.pageMap)
    .title('应用标题')
    .mode(NavigationMode.Stack)
  }
}

@ComponentV2
struct DetailPage {
  @Consumer('navPathStack') navPathStack: NavPathStack = new NavPathStack()
  @Local id: string = ''

  build() {
    NavDestination() {
      // 页面内容
    }
    .title('详情')
    .onReady((context: NavDestinationContext) => {
      let param = context.pathInfo.param as Record<string, string>
      this.id = param?.id ?? ''
    })
  }
}
```

### Navigation 标准模板 — V1 写法（legacy，仅参考）

```typescript
// ⚠️ V1 legacy — 老项目兼容查阅；新代码请用上方 V2 写法
@Entry
@Component
struct MainPage {
  @Provide('navPathStack') navPathStack: NavPathStack = new NavPathStack()

  @Builder
  pageMap(name: string, param?: object) {
    if (name === 'DetailPage') {
      DetailPage()
    }
  }

  build() {
    Navigation(this.navPathStack) {
      // 首页内容
    }
    .navDestination(this.pageMap)
    .title('应用标题')
    .mode(NavigationMode.Stack)
  }
}

@Component
struct DetailPage {
  @Consume('navPathStack') navPathStack: NavPathStack
  @State id: string = ''

  build() {
    NavDestination() {
      // 页面内容
    }
    .title('详情')
    .onReady((context: NavDestinationContext) => {
      let param = context.pathInfo.param as Record<string, string>
      this.id = param?.id ?? ''
    })
  }
}
```

### 关键区别

| 特性 | router（废弃） | Navigation（推荐） |
|---|---|---|
| 导入 | `@ohos.router` | 无需导入，ArkUI 内置 |
| 跳转 | `router.pushUrl()` | `navPathStack.pushPathByName()` |
| 返回 | `router.back()` | `navPathStack.pop()` |
| 传参 | `params` 对象 | `pushPathByName` 第二个参数 |
| 接收参数 | `router.getParams()` | `NavDestination.onReady()` |
| 页面注册 | `main_pages.json` 每页注册 | 只注册入口页，子页面通过 Builder 映射 |
| 多设备适配 | 不支持 | Stack/Split/Auto 模式 |
| 转场动画 | 有限 | `customNavContentTransition` 完全自定义 |

---

## 4. 动画新增

### keyframeAnimateTo（关键帧动画）

```typescript
// API 12+ 新增
keyframeAnimateTo({ iterations: 1 }, [
  {
    duration: 300,
    curve: Curve.EaseInOut,
    event: () => {
      this.scale = 1.2
      this.opacity = 0.8
    }
  },
  {
    duration: 200,
    curve: Curve.EaseOut,
    event: () => {
      this.scale = 1.0
      this.opacity = 1.0
    }
  }
])
```

### geometryTransition follow 参数

```typescript
// API 12+ 新增 follow 参数
.geometryTransition('shared_id', { follow: true })
// follow: true 时，目标位置组件跟随源位置组件的动画路径
```

---

## 5. build-profile.json5 版本字段

```json5
{
  "app": {
    "products": [
      {
        "name": "default",
        "compileSdkVersion": 12,          // 编译 SDK 版本（API 级别）
        "compatibleSdkVersion": 12,       // 最低兼容 SDK 版本
        "runtimeOS": "HarmonyOS"
      }
    ]
  }
}
```

**注意**：在部分 DevEco Studio 版本中，SDK 版本可能显示为字符串格式 `"5.0.0(12)"`，括号内的数字是 API 级别。代码生成时应根据 API 级别数字判断特性支持。
