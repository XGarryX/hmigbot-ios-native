# Android-to-HarmonyOS UI Layout Mapping Reference

<!-- TODO: Fill in the actual UI layout mapping content -->
<!-- This reference maps Android layout containers to HarmonyOS ArkUI layout equivalents -->
<!-- Covers: LinearLayout→Column/Row, FrameLayout→Stack, ConstraintLayout→RelativeContainer, RecyclerView→List+LazyForEach, ScrollView→Scroll, etc. -->


## 布局容器映射

| 安卓部分UI | 对应鸿蒙部分UI | 其他说明 |
|-----------|---------------|---------|
| `LinearLayout` (vertical) | `Column` 组件 | 纵向线性布局，支持 `.justifyContent()`、`.alignItems()` |
| `LinearLayout` (horizontal) | `Row` 组件 | 横向线性布局 |
| `FrameLayout` | `Stack` 组件 | 层叠布局，支持 `.alignContent()` |
| `RelativeLayout` | `RelativeContainer` 组件 | 相对布局，通过 `.alignRules()` 设置定位规则 |
| `ConstraintLayout` | `RelativeContainer` / 自定义布局 | 约束布局，复杂场景可用自定义 `onMeasureSize`/`onPlaceChildren` |
| `FlexboxLayout` | `Flex` 组件 | 弹性布局，支持 `FlexDirection`/`FlexWrap`/`FlexAlign` 标准 Flexbox |
| `GridLayout` | `Grid` 组件 | 网格布局，通过 `.columnsTemplate('1fr 1fr 1fr')` 定义列 |
| `TableLayout` | `Grid` 组件 | 表格布局，使用 `Grid` 组件模拟表格结构 |
| `CoordinatorLayout` | 组合 `Scroll` + `Column` + 动画 | 无直接对应，需组合模拟 AppBar 折叠效果 |
| `AppBarLayout` / `CollapsingToolbarLayout` | `Navigation` 标题栏 + `titleMode` | 折叠工具栏，`NavigationTitleMode.Full`→`.Mini` 自动切换 |
| `ScrollView` | `Scroll` 组件 | 滚动容器，通过 `Scroller` 控制器编程式滚动 |
| `HorizontalScrollView` | `Scroll` + `ScrollDirection.Horizontal` | 横向滚动 |
| `NestedScrollView` | `Scroll` + `.nestedScroll()` | 嵌套滚动策略配置 |
| `ViewPager` / `ViewPager2` | `Swiper` 组件 | 页面滑动切换，支持 `.autoPlay()`、`.indicator()`、`.loop()` |
| `SwipeRefreshLayout` | `Refresh` 组件 | 下拉刷新，通过 `.onRefreshing()` 回调处理刷新 |
| `RecyclerView` | `List` 组件 | 高性能列表，使用 `List` + `ForEach`/`LazyForEach` 渲染子组件 |
| `RecyclerView` (GridLayoutManager) | `Grid` 组件 | 网格布局，通过 `.columnsTemplate()` 设置列数 |
| `RecyclerView` (StaggeredGridLayoutManager) | `WaterFlow` 组件 | 瀑布流布局 |
| `ListView` | `List` 组件 | 传统列表，使用 `List` 组件实现 |
| `GridView` | `Grid` 组件 | 网格视图，使用 `Grid` 组件实现 |
| `DrawerLayout` / `NavigationView` | `SideBarContainer` 组件 | 侧边栏/抽屉 |
| `TabLayout` + `ViewPager` | `Tabs` 组件 | 标签页，`Tabs` 整合标签栏和内容页切换 |
| `BottomNavigationView` | `Tabs` + `BarPosition.End` | 底部导航栏 |
| `CardView` | `Card` 组件 / `Container` + 样式 | 卡片视图，使用 `Card` 组件或自定义样式实现 |
| `Space` | `Blank` 组件 | 空白间隔，使用 `Blank` 组件实现 |
| `FragmentContainerView` | `NavDestination` / `@ComponentV2`（V2）/ `@Component`（V1） | 片段容器视图，映射到 `NavDestination` 或自定义组件 |
| `RecyclerViewFastScroller` | 自定义组件 | 列表快速滚动条，需自定义实现 |
| `MySearchMenu` (自定义) | `Search` 组件 + 自定义菜单 | 自定义搜索菜单，使用 `Search` 组件并添加自定义菜单 |
| `MyViewPager` (自定义) | `Swiper` 组件 | 自定义视图分页器，使用 `Swiper` 组件实现 |
| `MyRecyclerView` (自定义) | `List` 组件 | 自定义 RecyclerView，使用 `List` 组件实现 |
| `MyTextView` (自定义) | `Text` 组件 | 自定义 TextView，使用 `Text` 组件实现 |
| `MyAppCompatCheckbox` (自定义) | `Checkbox` 组件 | 自定义 Checkbox，使用 `Checkbox` 组件实现 |

## 布局属性映射

| 安卓部分UI | 对应鸿蒙部分UI | 其他说明 |
|-----------|---------------|---------|
| `layout_weight` | `.layoutWeight()` / `.flexGrow()` | 权重分配 |
| `padding` / `margin` | `.padding()` / `.margin()` | 支持统一或分别指定 `{ top, right, bottom, left }` |
| `View.GONE` / `View.INVISIBLE` | `Visibility.None` / `Visibility.Hidden` | `None`=不占位（GONE）；`Hidden`=占位不显示（INVISIBLE） |
| `android:id` | `.id('xxx')` / 组件引用变量 | 组件标识 |
| `android:background` | `.backgroundColor()` / `.backgroundImage()` | 背景 |
| `android:alpha` | `.opacity()` | 透明度 0~1 |
| `android:elevation` | `.shadow({ radius, color, offsetX, offsetY })` | 阴影 |
| `android:rotation` | `.rotate({ angle: xxx })` | 旋转 |
| `android:scaleX/Y` | `.scale({ x: xxx, y: xxx })` | 缩放 |
| `android:translationX/Y` | `.translate({ x: xxx, y: xxx })` | 平移 |
| `android:clipToOutline` | `.clip(true)` / `.clipShape()` | 裁剪 |
| `setEnabled(false)` | `.enabled(false)` | 禁用状态 |
| `android:focusable` | `.focusable(true)` | 可聚焦 |
| `android:focusableInTouchMode` | `.focusable(true)` + `.focusOnTouch(true)` | 触摸模式下可聚焦 |
| `android:clickable` | `.enabled(true)` + `.onClick()` | 可点击 |
| `android:longClickable` | `.gesture(LongPressGesture())` | 可长按 |
| `android:scrollbars` | `.scrollBar()` | 滚动条 |
| `android:fadeScrollbars` | `.scrollBar().fade(true)` | 滚动条自动隐藏 |
| `android:overScrollMode` | `.overScrollMode()` | 过度滚动模式 |
| `GradientDrawable` | `.linearGradient()` / `.radialGradient()` | 渐变背景 |
| `CardView` radius | `.borderRadius()` | 圆角 |
| `GradientDrawable.setStroke()` | `.border({ width, color, radius })` | 边框 |
| `android:layout_width` / `android:layout_height` | `.width()` / `.height()` | 宽高设置，支持具体数值、百分比、`'match_parent'`/`'wrap_content'` |
| `android:gravity` | `.alignItems()` / `.justifyContent()` | 内容对齐方式 |
| `android:layout_gravity` | `.alignSelf()` | 子组件在父容器中的对齐方式 |
| `android:orientation` (LinearLayout) | `Column` / `Row` | 布局方向 |
| `android:divider` (LinearLayout) | `Divider` 组件 | 分隔线 |
| `android:showDividers` (LinearLayout) | `Divider` 组件位置 | 分隔线显示位置 |

## 页面结构映射

| 安卓部分UI | 对应鸿蒙部分UI | 其他说明 |
|-----------|---------------|---------|
| `Activity` | `PageAbility` | 主UI容器 |
| `Fragment` | `NavDestination` / `@ComponentV2`（V2）/ `@Component`（V1） | 通过 Navigation + NavDestination 实现子页面路由 |
| `Service` | `ServiceAbility` | 后台服务 |
| `BroadcastReceiver` | `EventHub` + `@Event` | 广播接收器，使用事件订阅机制 |
| `ContentProvider` | `DataAbility` | 内容提供者 |
| `Toolbar` / `ActionBar` | `Navigation` 标题栏 | 通过 `.title()` 和 `.menus()` 配置 |
| `Intent` | `router` 模块 | 页面导航，使用 `router.push()`、`router.replace()` 等 |
| `Bundle` | `router.push({ params: {} })` | 页面间传递数据 |
| `onActivityResult` | `router.push()` + 回调 | 页面返回结果 |
| `startActivityForResult` | `router.push()` + 回调 | 启动页面并获取结果 |

## 列表与可滚动组件映射

| 安卓部分UI | 对应鸿蒙部分UI | 其他说明 |
|-----------|---------------|---------|
| `RecyclerView.Adapter` | `LazyForEach` + `IDataSource` | 数据适配器，实现 `IDataSource` 接口配合 `LazyForEach` 懒加载 |
| `RecyclerView.ViewHolder` | `@Builder` / `@ComponentV2`（V2）/ `@Component`（V1） | 声明式 UI 无需 ViewHolder 模式 |
| `LinearLayoutManager` | `List` 默认布局 | 纵向列表，`.listDirection(Axis.Horizontal)` 切换横向 |
| `GridLayoutManager` | `Grid` 组件 | 网格布局管理器 |
| `StaggeredGridLayoutManager` | `WaterFlow` 组件 | 瀑布流布局管理器 |
| `ItemTouchHelper` (swipe) | `ListItem.swipeAction()` | 列表项滑动操作菜单 |
| `ItemTouchHelper` (drag) | `ListItem.dragable()` | 列表项拖拽排序 |
| `DiffUtil` | `IDataSource` 的 `DataChangeListener` | 差异通知，`onDataAdd`/`onDataDelete`/`onDataChange` |
| `PagerAdapter` / `FragmentStateAdapter` | `Swiper` + `ForEach`/`LazyForEach` | 无需 Adapter 模式，直接循环渲染子页面 |
| `ListAdapter` | `LazyForEach` + `IDataSource` | 带 DiffUtil 的适配器 |
| `ArrayAdapter` | `ForEach` + 数组 | 数组适配器 |
| `BaseAdapter` | `ForEach` / `LazyForEach` | 基础适配器 |

## 迁移注意事项

1. **范式转换**：Android 使用命令式 UI（XML 布局 + Java/Kotlin 操作）；ArkUI 使用声明式 UI（ArkTS 组件树 + 状态驱动渲染）
2. **Adapter 模式消除**：`RecyclerView.Adapter`、`PagerAdapter` 等被 `ForEach`/`LazyForEach` + `IDataSource` 替代
3. **Fragment → NavDestination**：Fragment 模块化 UI 能力映射到 `Navigation` + `NavDestination` 路由
4. **布局属性调整**：Android 的布局属性需要转换为 ArkUI 的链式调用语法
5. **性能优化**：使用 `LazyForEach` 进行懒加载，避免一次性渲染大量数据
6. **响应式布局**：使用 `Flex` 和 `Grid` 组件实现响应式布局，适应不同屏幕尺寸
