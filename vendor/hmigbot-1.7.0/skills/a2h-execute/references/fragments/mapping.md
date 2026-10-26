<!-- GAP: SymbolGlyph 已验证清单转校验数据（5 册 §5.3），但数据文件路径/契约名未在 IMPL-CONTRACT 定义，本片段暂以"已验证清单数据"指代 -->
# mapping — Android→ArkTS UI 映射

产物一律 V2 外壳：`@ComponentV2` + `@Local/@Param/@Event`，禁 V1 装饰器。页面外壳 = `NavDestination`（`.hideTitleBar(true)`）+ 同文件导出 `@Builder export function <页名>Builder()`；页名 = page-names.json 鸿蒙页名（已含 Page 后缀：页 `AppTipsDialogPage` → `AppTipsDialogPageBuilder`），路由名就是页名 `'AppTipsDialogPage'`；K9 对旧写法 `<页名>PageBuilder` 也登记别名，新写只用前者（spec/CONTRACT.md §1/§2；K9 `sync_pagemap` 只认此签名生成路由表，零 builder 整波 FAIL）。`<页名>Builder` 与任何 `@Builder` 体内禁 `return`（「Only UI component syntax」编译必败；K9 逐 builder 静态扫，命中整波 FAIL 派 repair）：条件渲染用 `if (…) { 组件 } else { 组件 }`，提前退出逻辑挪到方法。页面禁 `@Entry`：唯一 @Entry 是 Navigation 宿主入口页（main_pages.json 首项，`host_page.py` 单写，代理禁改）（页面写 @Entry → 零 PageBuilder，NO_BUILDERS 停机）。

页内导航硬规（E77）：`startActivity/show(DialogFragment)/navigate` 一律 `this.navPathStack.pushPathByName('<契约路由名>', <类型化参数实例>)`；stack 用 `@Consumer('navPathStack') navPathStack: NavPathStack = new NavPathStack()`（宿主入口页（main_pages.json 首项，host_page.py 单写）已 `@Provider('navPathStack')`，无需 onReady 再取；页面内禁再写 `@Provider('navPathStack')`）；返回 `this.navPathStack.pop()`。禁把契约导航边改写成 `@Event onOpenXxx` / `@Param onXxx` 交给"父组件"：NavDestination 页由路由表实例化、无父组件接回调，编译绿、点击无响应。@Event 只用于同文件真实父子（页 → 自己的 Body/Item 子组件）。

## 组件映射
| Android | ArkTS |
|---|---|
| BottomNavigationView | 自定义 Row + @Builder tabBarItem |
| Dialog / DialogFragment / BottomSheetDialogFragment | DIALOG 模式弹窗页：`NavDestination().mode(NavDestinationMode.DIALOG)`，push 打开、pop 关闭（E259，底部弹层内容贴底） |
| DrawerLayout | SideBarContainer |
| RecyclerView | List + LazyForEach |
| ViewPager2 | Swiper |
| CoordinatorLayout | Stack + 自定义手势 |
| CardView | Column + borderRadius + shadow |
| FloatingActionButton | Button + 绝对定位 |
| ProgressBar 线/环 | Progress({type: Linear / Ring}) |
| Toolbar/ActionBar | NavDestination 标题栏 |
| AlertDialog | getUIContext().getPromptAction().showDialog()（全局 AlertDialog.show 已废弃） |
| Snackbar | getUIContext().getPromptAction().showToast()（全局 promptAction.* 已废弃） |
| PopupMenu | Menu + MenuItem |
| ImageView+Glide | Image(url) 或 @ohos/imageknife |
| EditText | TextInput / TextArea(多行) |
| CheckBox / RadioButton / Switch | Checkbox / Radio / Toggle({type: Switch}) |
| SeekBar / Spinner / SwipeRefreshLayout | Slider / Select / Refresh |

## 颜色（Material→HarmonyOS）
primary `#007DFF`｜surface `#FAFAFA`｜background `#FFFFFF`｜onSurface `#182431`｜次要 `#99182431`｜divider `#E0E0E0`｜error `#E84026`｜disabled `#66182431`｜overlay `#1A000000`｜pillBg `#1F000000`。优先系统语义色 `$r('sys.color.ohos_id_color_text_primary')` 等（随深色模式）。

## 间距：4vp 基数
xs=4／sm=8／md=12／lg=16(标准 padding)／xl=20／xxl=24(页面边距)

## Tab 两分法
- 顶部分段切换（TabLayout+ViewPager2，不在 Navigation 内）→ 原生 `Tabs({barPosition: BarPosition.Start})` + `TabContent().tabBar()`；禁手搓 Row+Swiper 同步；多 Tab 加 `.barMode(BarMode.Scrollable)`。
- 底部主导航+Navigation 路由 → Tab 栏必须外置（NavDestination 会覆盖内部 Tab 栏）：
```ts
Column() {
  Navigation(this.navPathStack) {/* 按 currentTabIndex 切内容 */}
    .navDestination(this.routerMap).mode(NavigationMode.Stack).layoutWeight(1)
  CustomTabBar() // 外部，永不被覆盖
}
```

## 3 类常见错误
1. emoji/Unicode 符号字当图标 → 必须 SymbolGlyph，fontColor 是数组 `[Color.Black]`；
2. 凭猜用未验证 `sys.symbol.*` 名 → Unknown resource name；只用已验证清单数据里的名；
3. Tabs 放 Navigation 内部 → 子页覆盖 Tab 栏；按上方外置方案。

## 资源合并优先级（E1-1）
同名资源按 app 模块 > library > 自定义 sourceSets 生效。取 drawable/@color/@dimen 字面值先查 `spec/ref/resource-override-map.json` 的 effective，禁直读库模块 values（错色）。

<!-- source: arkts-ui-alignment/SKILL.md:L42-72,L130-174,L178-224,L291-325 -->

## 边距/内距：start/end 是陷阱（E272）

| 安卓 | ArkUI | 禁写 |
|---|---|---|
| `marginStart` / `marginEnd` | `.margin({ left: … })` / `.margin({ right: … })` | `.margin({ start/end: … })` |
| `paddingStart` / `paddingEnd` | `.padding({ left: … })` / `.padding({ right: … })` | `.padding({ start/end: … })` |
| `layout_weight=n` | `.layoutWeight(n)` | — |

`{ start/end }` 命中 ArkUI 的 **LocalizedEdges 重载**，该重载的字段类型是 `LengthMetrics`（`{unit, value}`），
`$r('app.float.*')` 是 `Resource`，**类型不兼容** → `Type 'Resource' is missing the following properties
from type 'LengthMetrics': unit, value`。ds2 首轮此类 34 条，占首轮编译错误 15%。
本工程无 RTL 需求；真需要 RTL 时用 `LengthMetrics.resource($r(…))` 配 `{ start/end }`。
`gravity` 不在此表——Text 用 `.textAlign()`、容器用 `.justifyContent()/.alignItems()`，按语境定，不机械翻。
