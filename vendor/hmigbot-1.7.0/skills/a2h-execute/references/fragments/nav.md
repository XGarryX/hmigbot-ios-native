# nav — 导航路由规则（V2）

## 方案选择
- 底部 Tab（3-5 平级入口）→ Tabs + TabContent
- 页面跳转 → Navigation + NavPathStack + NavDestination；手机 NavigationMode.Stack / 平板 Split / 自适应 Auto，必须显式设 mode
- 禁 @ohos.router（API12+ 已废弃）

## 编译硬规矩
1. import 纪律：用作值的类必须 import：`AppStorageV2/PersistenceV2/LengthMetrics/ComponentContent/window`（`import { AppStorageV2 } from '@kit.ArkUI'`，每个用到的文件各自 import）；禁 import ArkUI 组件/枚举（Navigation/NavDestination/NavPathStack/NavPathInfo/NavDestinationContext/WrappedBuilder/LaunchMode/NavigationMode 等 ambient）；禁 import 装饰器（@ComponentV2/@Local/@ObservedV2/@Trace 等）；例外：UIContext 作类型标注时 import 合法、勿删。
2. 路由参数必须是类型化类实例：声明 param 类 → new 后逐字段赋值 → 传实例；禁 `{...} as Record<string,string>`、`{} as object`、`{...} as XParam`（arkts-no-untyped-obj-literals）。无参路由声明 `class NoParam {}` 传 `new NoParam()`；单值可直传 string/number；@Builder pageMap 体内只能写 UI 组件语法，兜底须内联 `builder(param ?? new NoParam())`，禁 `const arg = ...`；`unknown[]` 赋 `Object[]` 用 `as Object[]`。
3. 取参：onReady 内 `const obj = ctx.pathInfo.param as Object` 再 `if (obj instanceof XParam)` 块内访问字段；禁裸 unknown 直接 instanceof（arkts-no-any-unknown）、禁 `const p: Object = ctx.pathInfo.param` 隐式赋值。
4. 页面 struct 的 @Local/@Param 字段禁用内置通用属性名（id/visibility/width/height/enabled/position/zIndex/opacity，撞 CustomComponent 基类）；换 itemId/coverVisible 等（param 类/数据类不受限）。
5. 进阶 API：getIndexByName 返回 `Array<number>`（判存在 `.length>0`、取首个 `[0]`）；customNavContentTransition 的 proxy.to/from 是 NavContentInfo，仅 name/index/mode/param/navDestinationId 五字段，无 opacity/translate（要动画则绑 @ObservedV2+@Trace state 后 animateTo）；disableAnimation(true) 是 NavPathStack 方法非组件属性；splitPlaceholder 传 ComponentContent（须 import）非裸 @Builder。

## 错误速记
| 症状 | 修法 |
|---|---|
| 用 @ohos.router 跳转 | Navigation + NavPathStack |
| NavDestination 收不到参数 | onReady(ctx) 取 ctx.pathInfo.param |
| Tabs onChange 不更新 index | 回调同步 @Local currentIndex |
| Navigation 未设 mode | 显式 Stack/Split/Auto |
| 混入 V1 装饰器 | 全 V2（@Local/@Param/@Event） |
| 父子双向用 @Link | @Param + @Event（V2 无 @Link） |

跨层级共享 NavPathStack 用 `@Provider('navPathStack')()` / `@Consumer('navPathStack')()`：必须带括号，Consumer 必须给默认值；Provider 只在宿主入口页（main_pages.json 首项，host_page.py 单写）——页面/组件内禁自建 `@Provider('navPathStack')`（遮蔽宿主的栈，子树导航全失效）。启动页 builder 首参须接受 `undefined`（宿主启动入栈由脚本生成，builder 首参非零参可构造类时传 undefined）。
页面发起导航只有一种写法：`this.navPathStack.pushPathByName('<路由名>', param)`（E77）；禁用 @Event/@Param 回调把导航"抛给父组件"——路由表实例化的页面没有父组件，回调即死端。

<!-- source: arkts-navigation-builder/SKILL.md:L46-67,L79-131,L150-164 -->
