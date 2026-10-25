---
name: arkts-navigation-builder
description: 生成 ArkTS/HarmonyOS 页面导航和路由代码（V2 优先，API 12+）。当用户需要实现页面跳转、Navigation 容器、NavPathStack 导航栈、NavDestination 页面注册、Tab/底部/侧边栏导航、@Builder 路由映射、pushPathByName 传参跳转、页面返回传值、路由拦截等功能时，务必触发此 skill。即使只说"做个多页面应用""页面怎么跳转"也应触发。仅组件内状态管理（@Local/@Param/@Provider 等）用 arkts-state-manager。
metadata:
  type: domain
  domain: navigation
  tags:
  - navigation
  - routing
  - tabs
  - arkts-v2
---
# ArkTS Navigation Builder — 导航路由生成器（V2 优先）

## API 版本与项目策略

本 skill 的代码模板基于 **API 12+（HarmonyOS 5.0.0+）和 ArkTS V2 装饰器体系**。

> **项目锁 V2**：本项目所有新生成代码使用 V2 装饰器（`@ComponentV2 / @Local / @Param / @Event / @Once / @Provider / @Consumer / @ObservedV2 / @Trace / AppStorageV2 / PersistenceV2`）。导航 API 本身（`Navigation / NavPathStack / NavDestination / Tabs / TabContent`）在 V1/V2 中**完全一致**，仅页面组件内的状态装饰器需要使用 V2。
>
> 如需 V1 兼容写法查阅，参阅 `references/nav-patterns.md`、`references/tab-navigation.md`、`references/advanced-nav-patterns.md`（已加 legacy 标识）。

> **重要**：`@ohos.router` 在 API 12+ 已废弃。所有新项目必须使用 `Navigation` + `NavPathStack` 进行页面导航。如果用户的现有代码使用 router，应引导其迁移到 Navigation 方案。迁移详细步骤参阅 arkts-knowledge-verifier skill。

- 使用 `Navigation` + `NavPathStack`（不要用 `@ohos.router`）
- 使用 `@kit.*` 导入
- 页面组件用 `@ComponentV2`，跨层级共享 NavPathStack 用 `@Provider() / @Consumer()`
- 生成代码前，先确认用户的目标 API 版本（读 `build-profile.json5` 的 `compatibleSdkVersion`）

### V1 → V2 装饰器映射（导航上下文）

| V1 装饰器 | V2 等价 | 备注 |
|---|---|---|
| `@Component` | `@ComponentV2` | 页面 struct 装饰器 |
| `@State` | `@Local` | 页面内部状态（如 `currentIndex`、参数缓存） |
| `@Prop` | `@Param`（只读加 `@Once`） | 父→子单向传值 |
| `@Link` | `@Param + @Event` 回调 | V2 强调单向数据流 + 事件 |
| `@Provide('navPathStack')` | `@Provider('navPathStack')()` | 必须带括号 |
| `@Consume('navPathStack')` | `@Consumer('navPathStack')()` | 必须带括号 + 默认值 |
| `@StorageLink('isFullPlayerVisible')` | `AppStorageV2.connect(Cls, key, () => new Cls())` | 配合 `@ObservedV2` 类 |
| `@Watch` | `@Monitor('prop') method(m: IMonitor)` | 方法装饰器 |

> **导航 API 本身完全一致**：`Navigation / NavPathStack / NavDestination / pushPathByName / pop / popToName / clear / NavigationMode.Stack/Split/Auto / @Builder pageMap` 在 V1/V2 中无任何差异，**仅状态装饰器需要改**。

详细 V2 装饰器规则参阅 `arkts-state-manager/references/v2-decorators.md`。

---

## 导航方案选择

ArkTS 有两种主要导航模式，根据应用类型选择：

```
你的应用需要什么导航？
│
├─ 底部 Tab 切换（如微信/淘宝主页）
│   └─ Tabs + TabContent
│       适合：3-5 个平级主要功能入口
│
└─ 页面跳转（列表→详情、登录→首页）
    └─ Navigation + NavPathStack + NavDestination
        适合：层级式页面导航
        │
        ├─ 手机端 → mode: NavigationMode.Stack（栈模式）
        ├─ 平板端 → mode: NavigationMode.Split（分栏模式）
        └─ 自适应 → mode: NavigationMode.Auto
```

---

## 导航实现模板（详见 references）

> **MUST**：写导航代码前，按场景先读对应 reference——

> - **系统路由表（route_map.json + module.json5 `routerMap`）/ 跨模块(HAP/HSP/HAR)导航 / `pushDestinationByName`（防白屏）—— 官方推荐** → `references/v2-system-routing.md`
> - 页面跳转（Navigation + NavPathStack）/ 动态路由注册 / 页面生命周期（含 **被 DIALOG 页覆盖暂停·恢复 onActive/onInactive §4a**）/ 嵌套导航(Tabs+Navigation) / **详情全屏覆盖标签栏(§5a)** / **多窗口 pushDestinationByName(§2a)** / 自定义转场 → `references/v2-nav-patterns.md`
> - 底部 Tab 导航（Tabs + TabContent）/ 自定义 TabBar / 可滚动 Tabs / Tab 状态持久化 → `references/v2-tab-navigation.md`
> - 路由参数类型化 / routerMap @Builder / 全屏隐藏 Tab / 路由常量集中管理 / **路由拦截·登录守卫（setInterception）** / **导航栈持久化·进程回收后恢复多级页面(§7 recoverable / getPathStack / setPathStack)** / **单例页复用(§8a onNewParam+LaunchMode) · 精确删栈(§8b removeByIndexes/removeByNavDestinationId) · 嵌套导航取父栈(§8c getParent) · 返回传值(§8d onResult, 比 onPop 新)** → `references/v2-advanced-nav-patterns.md`

---

## ⚠️ 编译硬规矩（V2 严格模式 —— 不照做必编译失败）

> 以下三条是 skill-only 生成最高频的真实编译错误来源。**注意：部分下方 reference 示例仍用过时写法（`{...} as Record<string,string>` 传参、`const p = ctx.pathInfo.param` 裸 unknown 取参）——在当前 API 12+ 严格模式会编译失败，请一律按本节改写。**

### 规矩 1 · import 纪律：真实导出 vs ambient 环境名
- ✅ **必须 import**（`@kit.ArkUI` 真实导出、用作值——**每个用到的文件各自 import**）：`AppStorageV2`、`PersistenceV2`、`LengthMetrics`、`ComponentContent`、`window`
  ```typescript
  import { AppStorageV2, PersistenceV2 } from '@kit.ArkUI';   // BusinessError 从 @kit.BasicServicesKit
  ```
  最易漏：写了 `AppStorageV2.connect(...)` 却忘 import → `Cannot find name 'AppStorageV2'`。
- ❌ **绝不 import**（ArkUI 组件/容器/枚举一律 ambient、裸用即可）：`Navigation`/`NavDestination`/`NavPathStack`/`NavPathInfo`/`NavDestinationContext`/`WrappedBuilder`，及枚举 `LaunchMode`/`NavigationMode`/`NavDestinationMode`/`BarPosition` 等。一旦 `import { Navigation } from '@kit.ArkUI'` 即报 `Module '@kit.ArkUI' has no exported member 'Navigation'`、整文件编不过。
- ⚠️ **`UIContext` 是例外、别误删**：值通常由 `this.getUIContext()` 取得、**无需 import**；但 `UIContext` 本身是 `@kit.ArkUI` 真实导出，作**类型标注**（`let ctx: UIContext = this.getUIContext()`）时 **import 合法、不报错**——不要把它当 ambient 名而删掉类型 import。
- ❌ **装饰器一律 ambient、绝不 import**：`@ComponentV2`/`@Local`/`@Param`/`@Event`/`@Once`/`@ObservedV2`/`@Trace`/`@Monitor`/`@Provider`/`@Consumer`/`@Builder` 等是语言内置，裸用即可。`import { ObservedV2, Trace } from '@kit.ArkUI'` 会报 `Module '@kit.ArkUI' has no exported member 'ObservedV2'`。**只有用作「值」的类**（`AppStorageV2`/`PersistenceV2`/`LengthMetrics`/`ComponentContent`）才 import（见上）；装饰器永不 import。

### 规矩 2 · 路由参数必须是「类型化类实例」，禁裸对象字面量
```typescript
// ✅ 正确：声明 param 类，new 后逐字段赋值，传实例
class DetailParam { id: number = 0; origin: string = ''; }
const p = new DetailParam();
p.id = 10086; p.origin = 'feed';
this.navPathStack.pushPathByName('Detail', p);
```
❌ 禁 `pushPathByName('Detail', { id: 1 } as Record<string, string>)`、`{} as object`、`{ ... } as XParam`
→ `Object literal must correspond to some explicitly declared class or interface (arkts-no-untyped-obj-literals)`。
（单值参数可直接传基元：`pushPathByName('Detail', productId)`，productId 为 string/number。）
- **无参路由**：声明空类 `class NoParam {}` 传 `new NoParam()`，**禁 `{} as object`**（同样触发 `arkts-no-untyped-obj-literals`）。动态路由 `WrappedBuilder.builder(...)` 的兜底**直接内联** `builder(param ?? new NoParam())`——⚠️ `@Builder pageMap(name){...}` 体内**只能写 UI 组件语法**，禁 `const arg = ...` 等普通语句（否则 `Only UI component syntax can be written here`），别把兜底拆成 `const arg = param ?? new NoParam(); builder(arg)`。
- **数组参数/取值**：`unknown[]`（如 `NavPathStack.getParamByName()` 的返回）赋给 `Object[]` 会报 `Type 'unknown[]' is not assignable to type 'Object[]'`——用 `as Object[]` widening（标量 `as Object` 的数组版）。

### 规矩 3 · 取路由参数：先 `as Object` widening，再 instanceof
`pathInfo.param` 静态类型是 `unknown`（`pushPathByName(name, param: unknown, ...)`）。
```typescript
.onReady((ctx: NavDestinationContext) => {
  const obj = ctx.pathInfo.param as Object;   // ✅ 用 `as Object` 强转 widening（不是注解赋值）
  if (obj instanceof DetailParam) {
    this.id = obj.id;            // 字段只在 instanceof 块内访问
    this.origin = obj.origin;
  }
})
```
- ❌ `const p = ctx.pathInfo.param`（裸 unknown）直接 instanceof → `Use explicit types instead of "unknown" (arkts-no-any-unknown)`。
- ❌ `const p: Object = ctx.pathInfo.param`（隐式赋值）→ `Type 'unknown' is not assignable to type 'Object'`。
- `as Object` 是合法且必需的 widening；只是不推荐 `as DetailParam` 直接下行断言（instanceof 更安全、且与构造侧一致）。

### 规矩 4 · 页面组件字段别用「内置通用属性名」（`id`/`visibility`/`width`…）
页面 struct（`@ComponentV2` NavDestination/页面）的 `@Local`/`@Param` 字段**不要用组件内置通用属性的名字**——`id`、`visibility`、`width`、`height`、`enabled`、`position`、`zIndex`、`opacity` 等都是基类 `CustomComponent` 的成员，同名字段报 `Property 'xxx' in type 'YourPage' is not assignable to the same property in base type 'CustomComponent'`。加前缀/换名：`itemId`、`coverVisible`、`boxWidth` 等。（**param 类 / 数据 model 类**不是组件，字段叫 `id`/`visibility` 没问题。）

### 规矩 5 · 进阶栈/转场 API 易错点
- `NavPathStack.getIndexByName(name)` 返回 **`Array<number>`**（所有同名页面的索引数组，**不是单个 number**）：判断存在用 `.length > 0`、取首个用 `[0]`。直接 `getIndexByName(n) >= 0` 报 `Operator '>=' cannot be applied to types 'number[]' and 'number'`。
- 自定义转场 `customNavContentTransition` 里 `proxy.to`/`proxy.from` 是 `NavContentInfo`——**只含 `name`/`index`/`mode`/`param`/`navDestinationId` 五个字段，`opacity` 与 `translate` 都不存在**（写 `proxy.to.opacity`/`.translate` 报 `Property '...' does not exist on type 'NavContentInfo'`）。要淡入淡出/位移：把页面 `.opacity()`/`.translate()` 绑到共享 `@ObservedV2 + @Trace` state、`animateTo` 改那个 state。
- 关闭某流程转场动画：`this.navPathStack.disableAnimation(true)`——是 **`NavPathStack` 的方法**、不是组件属性（写成 `NavDestination(){...}.disableAnimation(true)` 报 `Property 'disableAnimation' does not exist on type 'NavDestinationAttribute'`）。
- 分栏右侧默认占位页 `splitPlaceholder(placeholder: ComponentContent)`（API20+）：传 **`ComponentContent`**、不是裸 `@Builder`——`new ComponentContent(this.getUIContext(), wrapBuilder(PlaceholderBuilder))`（裸传 `()=>void` 报 `Argument of type '() => void' is not assignable to parameter of type 'ComponentContent<Object>'`）；`ComponentContent` 须 `import { ComponentContent } from '@kit.ArkUI'`。

---

## Navigation 模式选择（API 不变）

```typescript
// Stack 模式 — 手机端，全屏切换
.mode(NavigationMode.Stack)

// Split 模式 — 平板端，左侧列表 + 右侧详情
.mode(NavigationMode.Split)
.navBarWidth('40%')  // 左侧宽度

// Auto 模式 — 根据屏幕宽度自动切换
.mode(NavigationMode.Auto)
// 宽度 >= 600vp 时用 Split，否则用 Stack
```

---

## 常见错误速记（V2）

| # | 错误 | 正确做法 |
|---|---|---|
| 1 | 用 @ohos.router 跳转 | 用 Navigation + NavPathStack（router 已废弃） |
| 2 | NavDestination 不接收参数 | onReady(context) 里取 context.pathInfo.param |
| 3 | Tabs onChange 不更新 index | onChange 回调同步 @Local currentIndex |
| 4 | Navigation 不设 mode | 显式设 NavigationMode（Stack/Split/Auto） |
| 5 | V2 项目混入 V1 装饰器 | 全用 V2（@Local/@Param/@Event…） |
| 6 | 父子双向用 @Link | 用 @Param + @Event（V2 无 @Link） |

> **MUST**：每条「错误 vs 正确」完整代码见对应 reference（v2-nav-patterns / v2-tab-navigation / v2-advanced-nav-patterns）。

---

## 生成检查清单（V2）

- [ ] 选择了合适的导航方案（Tabs / Navigation / 组合）
- [ ] Navigation 有明确的 mode 设置
- [ ] NavPathStack 通过 `@Provider() / @Consumer()` 注入（V2 必须带括号 + Consumer 默认值）
- [ ] NavDestination 在 onReady 中接收参数
- [ ] 页面 Builder 在 navDestination 中正确映射
- [ ] Tabs 设置了 onChange 回调更新 currentIndex
- [ ] 返回操作使用 navPathStack.pop()
- [ ] 所有页面 struct 使用 `@ComponentV2`，所有页面内部状态用 `@Local`
- [ ] 父子双向场景用 `@Param + @Event`，不要试图用 V1 `@Link`
- [ ] 全屏隐藏 Tab 等跨组件状态用 `@ObservedV2 + AppStorageV2.connect`，不再用 `@StorageLink`
- [ ] 同一文件不混用 V1/V2 装饰器（如 `@Component` + `@ComponentV2`）

---

## 跨 Skill 协作

当用户需求超出纯导航范围时，读取以下 skill 的内容来补充：

| 需要什么 | 读取哪里 |
|---------|---------|
| 完整业务功能（列表详情页需要导航+数据+UI） | `arkts-pattern-library/SKILL.md` — 它有编排协议引导完整流程 |
| 列表页 UI 组件（List + ForEach + 卡片） | `arkts-component-builder/SKILL.md` |
| 数据模型和网络请求 | `arkts-data-layer/SKILL.md` |
| 状态管理（V2 装饰器、AppStorageV2、PersistenceV2） | `arkts-state-manager/SKILL.md` 与 `arkts-state-manager/references/v2-decorators.md` |
| 全局状态（登录状态驱动导航守卫） | `arkts-state-manager/references/v2-global-state.md` |
| 页面转场动画 | `arkts-animation-builder/SKILL.md` "transition" 节 |

> 完整路由矩阵见 `arkts-knowledge-verifier/references/skill-routing-guide.md`

---

## References

### V2 主参考（推荐，本项目实际使用）

- `references/v2-nav-patterns.md` — V2 完整导航模板（基础 / 动态路由 + 多窗口 pushDestinationByName / Stack/Split/Auto / 生命周期 / Tabs+Navigation 嵌套 + 详情全屏覆盖标签栏 / 转场动画）
- `references/v2-tab-navigation.md` — V2 Tabs 完整模式（基础 / 自定义 TabBar / 可滚动 Tabs / Tabs+Swiper / 状态持久化 with AppStorageV2）
- `references/v2-advanced-nav-patterns.md` — V2 高级导航模式（@ObservedV2 路由参数类、routerMap @Builder、FullPlayer 隐藏 Tab via AppStorageV2、onReady 参数、路由常量、setInterception 守卫、栈持久化/进程恢复 recoverable+getPathStack/setPathStack、进阶栈 onNewParam/LaunchMode 单例·removeByIndexes/removeByNavDestinationId·getParent）
- `references/v2-system-routing.md` — 系统路由表 route_map + 跨模块导航 + pushDestinationByName（防白屏）

### V1 历史参考（仅老项目兼容查阅）

- `references/nav-patterns.md` — V1 导航完整模板（@Component / @State / @Provide / @Consume）
- `references/tab-navigation.md` — V1 Tabs 完整模式（含 @StorageLink 持久化）
- `references/advanced-nav-patterns.md` — V1 高级导航模式（含 @StorageLink 全屏隐藏 Tab）

> 遇到版本兼容性或其他不确定的 ArkTS 知识点（如属性、语法、权限等），参阅 **arkts-knowledge-verifier** skill
