# Compose 导航方言 recognizer（page / route / edge 解析规则）

Compose 的导航不是单一写法。下面 6 种方言各给：**怎么找页面、怎么解析路由、怎么建导航边**。一个工程可并存多种（如 Jetcaster mobile=D1、tv=D1、wear 不同）。

---

## D1 — string-route（最常见，Navigation-Compose 经典）
**探测**：`NavHost(` + `composable("route")` / `composable(CONST)` / `addXxxGraph` 扩展函数里的 `composable(...)`。

**page**：`composable(<route>) { backStackEntry -> ScreenX(...) }` 中 lambda 体首个 @Composable 调用 `ScreenX` 即页面（跳过 `requireNotNull`/`remember*`/作用域包装）。`addXxxGraph(builder)` 扩展函数内部的 `composable(...)` 同样算注册。

**route 解析**：
- 字面量 `"home"` → 直接取。
- 常量 `MainDestinations.HOME_ROUTE` → 查 `const val HOME_ROUTE="home"`。
- 枚举 `HomeSections.FEED.route` → 查 `enum class HomeSections(... val route)` 的 FEED 构造实参。
- 模板 `"${SNACK_DETAIL_ROUTE}/{id}?origin={o}"` → 解析常量前缀，`{id}`/`$var` 为参数占位，`is_dynamic` 视情况。

**edge**：`navController.navigate("snack/$id")` 或 nav wrapper `navigateToSnackDetail(...)` → 解析目标 route → route_page 反查目标页面。**按 SKILL Phase2 铁律 B 把边归到 UI 触发页**（追回调链）。

> Jetsnack 实例：外层 NavHost 注册 HOME→MainContainer、SNACK_DETAIL→SnackDetail；内层 addHomeGraph 注册 FEED/SEARCH/CART/PROFILE→Feed/Search/Cart/Profile。真实导航边 Feed/Search/Cart→SnackDetail（onSnackClick→onSnackSelected→::navigateToSnackDetail）+ bottom-bar MainContainer→各 tab（navigateToBottomBarRoute(route)，运行时路由，按铁律 C 展开成 dynamic）。

---

## D2 — type-safe nav（现代默认，AndroidX 2.8+）
**探测**：`composable<Route.Inbox> { }` + `sealed interface Route { @Serializable data object Inbox : Route; @Serializable data class Detail(val id:String):Route }`。

**page**：`composable<T>` 的类型参 `T`（sealed 子类型）即页面，**id = 子类型名**（`Inbox`/`Detail`）。
**route 解析**：无字符串路由，**类型即路由**。`data class` 的构造参 = 导航参数。
**edge**：`navController.navigate(Route.Detail(id))` → 目标 = `Detail`。参数从构造实参取。
**注意**：起始页 `startDestination = Route.Inbox`（类型，非字符串）。

> Reply 实例：`ReplyApp.kt` `composable<Route.Inbox>/<Articles>/<DirectMessages>/<Groups>`。

---

## D3 — state-object wrapper（导航逻辑封装在 state 类）
**探测**：D1 的注册形态 + nav 是某 holder 类的方法：`appState.navigateToPlayer(...)` / `appState::navigateBack` / `rememberXxxAppState()`。

**page / route**：同 D1。
**edge 关键差异**：nav wrapper 不是 top-level fun，而是 `class XxxAppState { fun navigateToPlayer(...) { navController.navigate(...) } }` 的**方法**。
- 把这些方法也纳入 `nav_wrappers`（识别 `class .*State` / `*NavController` 内含 `.navigate(` 的方法）。
- 回调追踪同铁律 B：`Screen(onPlay = appState::navigateToPlayer)` → 该 screen 的播放按钮 → Player 页。

> Jetcaster mobile 实例：`JetcasterApp.kt` `appState.navigateToPlayer(episode.uri, backStackEntry)`、`appState::navigateBack`。

---

## D4 — Navigation3（最新，back-stack 操作式）
**探测**：`import androidx.navigation3.*` + `NavDisplay(backStack = ...)` + `entry<KeyType> { }` + `rememberNavBackStack(...)`。

**page**：`entry<DetailKey> { key -> DetailScreen(key) }` 的类型参 `DetailKey` 即页面，id = Key 类型名。
**route 解析**：**Key 类型即路由**（同 D2 思路，但是 Nav3 的 NavKey）。
**edge**：导航 = **back-stack 直接操作**，没有 `navigate()`：
- 入栈 `backStack.add(DetailKey(id))` → edge 到 Detail。
- 出栈 `backStack.removeLastOrNull()` / `removeAt` → back 边。
- 把 `backStack.add/remove*` 纳入 `navigate_sites`（而非只找 `.navigate(`）。

> JetNews 实例：`JetnewsNavDisplay.kt` 用 `NavDisplay` + `entry<>`。**这是 Route A 第一轮误诊成"custom builder"的方言，单独 recognizer。**

---

## D5 — fragment-hosted Compose（混合）
**探测**：`class X : Fragment` 内 `ComposeView` / `setContent { }` + 单个 `NavHostFragment`（传统 nav_graph.xml）。

**page/fragment**：Fragment → `fragments[]`（screen_kind="fragment"）。其 `setContent` 的根 @Composable 是它的 UI，内部控件归该 fragment 的 components。
**导航**：Fragment 间用传统 `findNavController().navigate(R.id.xxx)` 或 nav_graph.xml `<action>`。
- 有 nav_graph.xml → 读 `<action app:destination>` 建边（退化为类 toolkit 的 XML 解析）。
- host page 的 `contains[]` 列 fragment id。

> Jetchat 实例：`NavActivity` + `ConversationFragment`/`ProfileFragment`（Fragment + Compose 内容）。

---

## D6 — 页内 `when(stateVar)` 状态切换（状态机导航 / wizard / pager / 页内 tab）
**探测**：`when(stateVar) { 0 -> ScreenA(); 1 -> ScreenB() }` 或 `when(currentScreen) { Screen.A -> AScreen() }`，
分支调用**不同的全屏内容 @Composable**，由用户动作（按钮/tab/滑动）改 `stateVar` 推进。
**⚠️ 不限于「无 NavHost 的整 app」——NavHost destination *内部* 的 `when(state)` 同样适用**（最常见的漏判）：
- 引导/wizard pager：`when(currentPage){0->PageOne{currentPage=1};1->PageTwo{currentPage=2};2->PageThree{onComplete()}}`
- 页内 tab：`when(selectedTab){Overview->..;Task->..}`（底栏宿主页内部）
- 多步表单/分步流

**page**：`when` 每个分支调用的全屏 @Composable **各拆成一个独立 page 节点**，id = 分支 @Composable 名（如 PageContentOne/Two/Three、OverviewScreen…）。
**route**：`stateVar` 的分支值即"路由"（页内态，`route` 可为 null，`screen_kind: in_screen_state`）。
**edge**：改 `stateVar` 的赋值即导航边。`currentPage = 1` / `selectedTab = Task` / `currentScreen = Screen.B` 都纳入 `navigate_sites`，触发它的按钮/tab 即 via_component（下一步、tab 项）。最后一分支若调 `onComplete()`/外部回调 → 退出该流的边（到下一 destination）。

**🔑 拆 vs 不拆（关键判别，别过度拆）**：
- **拆**（视为页）：`stateVar` 是「选哪个屏」选择器——名字像 `currentPage/selectedTab/currentScreen/step/pageIndex/wizardStep`，分支是**不同的全屏内容**，由用户动作推进，有导航语义（wizard 步 / tab / pager 屏）。
- **不拆**（同一页的状态，不建页）：`stateVar` 是**加载/异步/空错态**——名字像 `uiState/loadingState/result`，分支是 `Loading/Success/Error/Empty` 的同一逻辑屏渲染态；或纯可见性开关。这些是**一个 page 的内部状态**，不拆。

**🔑 顺序/位置取「布局序」不取「声明序」**：page 之间的先后（wizard 步顺序）和底栏 tab 的左→右视觉顺序，**必须取实际布局/渲染顺序**——
- wizard 步顺序 = `when` 分支的 `stateVar` 值递增顺序（0→1→2）。
- 底栏 tab 左→右顺序 = 底栏 composable（Row/自绘 bar）里**子项的布局排列顺序**，或驱动它的 `items`/enum **在 UI 渲染处的遍历顺序**——**不是** route/composable 声明在文件里的先后。（Habicat 实测底栏视觉序是 Task/Boss/Store/Overview，与源码 enum 声明序不同；取错会让下游按位置点错 tab。）

> 单 Activity 极简 app / JetLagged 类单屏（可能只有 1 page，0 边，正常）。

---

## 嵌套 NavHost（D1/D3 常见，Jetsnack 即是）
某个外层 destination 的 screen composable 内部**又开一个 NavHost**（如外层 home/snack，MainContainer 内部再开 feed/search/cart/profile）。归属规则：
- **每层 NavHost 各有自己的 startDestination**，但 `is_start_destination:true` **只给最外层 NavHost 的起点**（如 MainContainer）。内层起点（如 Feed）`is_start_destination:false`，否则 Phase5 B1 闸会误判其它内层页为孤儿、且 BFS 起点歧义。
- 内层各页之间/到外层页的边照常建。内层容器页（MainContainer）若只是承载内层 NavHost + bottom-bar，本身是「壳/容器」，到内层 tab 的切换边由它发出（铁律 C 的 dynamic 边），但它**不**作为 SnackDetail 等的 from（铁律 B）。
- host Activity（壳）→ 外层起点 → 内层起点，用 `contains[]` 串层级，不用导航边表达「壳包含容器」。

## 通用 Fallback（方言识别失败）
1. 找不到任何上述特征 → 把 `setContent { RootComposable() }` 的 `RootComposable` 当唯一 page，标 `notes:"nav dialect=unknown"`。
2. 仍要尽量从 `interactive_sites` 找出状态切换/回调，建尽量多的边并标 `uncertain:true`。
3. **宁可标 unresolved_hints / uncertain，也不要凭空造边或静默丢边**（铁律 B/C）。
