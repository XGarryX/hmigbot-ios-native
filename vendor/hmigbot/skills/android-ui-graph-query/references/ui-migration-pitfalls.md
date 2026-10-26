# UI Migration Pitfalls — 静默映射陷阱

编译通过但运行时异常的 Android → ArkUI 映射陷阱。
a2h-activity-converter 在 Phase 2 加载此文件，转换时必须逐条检查。

## CRITICAL — 必须处理，否则页面不可用

### P-01: SideBarContainer 子组件顺序反转
- **Android**: DrawerLayout 第一个子组件 = 主内容，第二个 = 侧边栏（通过 layout_gravity 标识）
- **ArkUI**: SideBarContainer 第一个子组件 = 侧边栏，第二个 = 主内容
- **错误表现**: 侧边栏和主内容位置互换，侧边栏占据全屏，主内容被挤到侧边
- **修复**: 转换时交换子组件顺序

### P-02: Tabs + Navigation 全屏遮盖
- **Android**: TabLayout + ViewPager 可嵌套在任意布局中
- **ArkUI**: Tabs 放在 Navigation 内部时，NavDestination 会覆盖整个 Navigation 区域（含 Tabs）
- **错误表现**: 切换到子页面后 Tab 栏消失
- **修复**: Tabs 放在 Navigation 外部，或使用自定义 Row 实现 Tab 栏

### P-03: CoordinatorLayout 滚动协调丢失
- **Android**: CoordinatorLayout + AppBarLayout + CollapsingToolbarLayout = 联动折叠
- **ArkUI**: 无直接等价物，Scroll + Column 不会自动联动
- **错误表现**: AppBar 不随滚动折叠，嵌套滚动可能冲突
- **修复**: 使用 Scroll 的 onScroll 回调手动计算 AppBar 高度和透明度

### P-17: 几何 ≠ 命中测试（层叠/浮层：尺寸位置 与 是否挡触摸 解耦，各用专属 API）
- **不变量**: ArkUI 中「尺寸/位置/层叠顺序」与「是否接收·拦截触摸」正交且各有专属属性。源端（Compose Box.align / FrameLayout layout_gravity）二者常被"盒子大小"耦合，迁移时**必须拆开**，否则一改俱错。
- **两条独立决策**:
  - **几何 = 源布局里它视觉覆盖的区域**：占满→`'100%'`，占半幅→`'50%'`/对应 weight，贴边小块→真实 wxh。**不得为"别挡触摸"而缩小，也不得为"贴边"而放大到全屏。**
  - **触摸 = hitTestBehavior（或 onClick 落位）**：纯展示、点击交底层→上层 `.hitTestBehavior(HitTestMode.Transparent)`；上层自身响应→给上层 onClick。
  - **⚠️ HitTestMode.Block 语义 = 自身参与命中、但阻塞其【子节点】的触摸测试**（不是"挡住下层"）。因此不变量：**凡 subtree 含 onClick/交互控件的容器（弹窗卡片、控制条等）一律禁止无条件 Block**——写了按钮就全死（实锤：AIPPT 18 弹窗 32 处全灭）。Block 只有**三种**合法形态：① subtree 无任何交互子节点的纯遮罩（loading 蒙层）；② **隐藏**时 Block（`visible ? None : Block`——防透明控件吃点击）；③ 叶子组件自身（无后代可挡）。★**「显示时 Block」（`visible ? Block : None`）永远是缺陷**：它和形态② 只差三元分支位置、语义完全相反，一挂就把整棵子树的按钮全掐死。2026-08-29 AIPPT 实锤——闸此前把**所有**条件表达式一律豁免（只 FAIL 无条件字面 Block），于是一处写反、6 个弹窗的按钮全死而闸全绿，fixer 连修 5 轮全落空。现 `hit_test_gate.py` 按三元分支位置判别；排查用 `arkts-visual-verify/scripts/hit_chain_probe.py` 直接打印祖先命中链。**铁证形态：点击无效但系统 Back 有效**（按键不走命中测试，触摸走）。"独占蒙层挡下层"靠遮罩自身全屏 + 自己接收点击（Default 即可），不靠 Block。
- **双向错误表现**: 盒子太大且缺 hitTestBehavior→下层点不动/滚不动（"内容缺失/点不动"）；盒子太小→盖不住对应区域、底层透出（"选中态错位/两态混叠/背景缺一截"）。
- **修复**: 先按源布局把几何设成它该覆盖的区域，再按意图设 hitTestBehavior——二者分别表达，互不迁就。
- **自检**: 任一 Stack 上层子节点（背景/选中态/贴边浮层），核对两点：① 其 w/h 是否等于源布局该层覆盖区域（不是 wrap_content 也不是误铺全屏）；② 是否按"该不该挡触摸"显式设了 hitTestBehavior。grep 起点 `width\('100%'\).*height\('100%'\)` 仅查"过大"一类，"过小"一类需对源布局核对。

### P-20: 百分比尺寸子节点（width/height('100%')）在 wrap-content / 无定高父级里向上解析 → 撑满
- **Android/Compose**: 背景层 `fillMaxSize()` 靠父约束定尺寸，与内容同大
- **ArkUI**: 子节点的 `width/height('100%')` 解析到**最近一个有确定尺寸的祖先**，不是"父内容大小"。父级若是 wrap-content（由内容定大小）或在 List 里无定高，该子层就撑满整片可用空间。常见两类：① **列表行**背景层铺满视口、行被撑成整屏高；② **chip/徽标/卡片**等本应由文字定大小的组件，被一个当"背景/描边"的 `100%` 子层撑成大色块（该层被状态门控移除后又恢复 → "默认态大、操作后变正常"）
- **错误表现**: 列表每行异常高/背景铺满；或标签、徽标在默认态是大色块、交互后恢复
- **修复**: 不要用 `100%` 子层去填父高/宽。背景/描边**画在容器自身**（`.linearGradient()`/`.backgroundColor()`/`.border()`），由内容定大小，露描边环用 `.padding(1)`；确需测量再定高的用 `onAreaChange`
- **grep 自检**: `grep -rnE "width\('100%'\)|height\('100%'\)" src/components`，命中后核查父级是否 wrap-content / 无定高

### P-22: 横向滚动容器（List/Scroll/Grid, Axis.Horizontal）缺显式定轴尺寸
- **Android/Compose**: LazyRow / 横向滚动高度由子项固有高度决定，自动 wrap 成内容高
- **ArkUI**: 滚动容器**不 wrap 内容**。横向时不显式 `.height()` → 有剩余空间就**撑满父级**（连带里面 `width('100%')` 的背景/渐变一起拉伸成大色块）、被同级抢空间就**塌成 0**。纵向滚动容器缺 `.width()` 同理
- **错误表现**: 横向卡片行/标签条变成大色块顶掉其它内容，或整条不可见
- **修复**: 显式 `.height(= 最高子项高 + 上下 margin)`；纵向同理显式 `.width()`
- **同根性能坑**: Scroll 嵌套 List 时内层 List 不设宽高 → **子项全部一次性加载，LazyForEach 懒加载失效**（官方最佳实践明文）——同样是"滚动容器尺寸不由内容定"的另一面；嵌套场景必须给内层 List 定高 / `layoutWeight`
- **grep 自检**: `grep -rnE "Axis.Horizontal|Scroll\(|Grid\(" src/`，逐处确认链式属性含 `.height(<数字>)`（非 `'100%'`、非缺失）

## HIGH — 功能缺失或数据不更新

### P-04: NavDestination 参数时序
- **Android**: Intent extras 在 onCreate/onResume 中可用
- **ArkUI**: NavDestination 的 pathInfo.param 仅在 onReady() 中可用，aboutToAppear() 中为 undefined
- **错误表现**: 页面参数始终为空，页面显示默认状态
- **修复**: 参数读取放在 onReady() 回调中，不放在 aboutToAppear()

### P-05: ForEach / LazyForEach key 不完整导致 UI 不刷新
- **Android**: RecyclerView.Adapter notifyItemChanged(position) 精准更新
- **ArkUI（ForEach）**: keyGenerator 只含 id 时，属性变更（如 playState）不触发刷新
- **ArkUI（LazyForEach + V2 @Param）**: keyGenerator 返回 `item.id`，但 VM 用「同 id、新值」重建对象（如 `new Line({ item, count: n })`，`item.id` 不变）→ 框架按 key 判定为同一项、**复用旧子组件、不重派 `@Param`** → 子组件停在旧值（如数量加减后 count 不变）
- **错误表现**: 数据变了但 UI 不更新；列表项的 count / 选中态 / playState 停在旧值
- **修复**: ① key 必须含所有影响显示的可变字段：`item.id + '_' + item.count`（ForEach 与 LazyForEach 同理）；② 或保持对象引用稳定、用 `@ObservedV2` + `@Trace` 原地改字段（而非整体 `new`），让 `@Param` 沿响应链派发

### P-24: 抽可复用渲染时，把**动态**值当 @Builder【值参】传 → 定格首帧不刷新
- **适用范围**: 只约束「值会随 `@Local`/`@Trace` 变化、且**期望 UI 跟着刷新**」的**动态**数据。**静态/不变的值（含静态标签文字、写死的常量）走 @Builder 值参完全正常、不受本条约束**——不要为静态内容改写或拆组件。典型触发 = 同一布局里**内联重复**几个「标签 + 实时数值」块（各绑 ViewModel 实时字段、非 `<include>`/非 RecyclerView item），转换器为去重抽可复用渲染方式时。
- **陷阱**: 抽 `@Builder` 时把**动态数值当值参**传（`@Builder statRow(label, value: number)` + `this.statRow('余额', this.balance.toString())`）→ `@Builder` **默认按值传递**、传入是**调用时刻的快照**；`@Local`/`@Trace` 之后再变，builder 内那段 UI **不刷新**、定格首帧。**最隐蔽**：数据源即使是 `@ObservedV2 + @Trace`，一旦取出它的**属性值**（`item.value` 这个 number）作值参传，传的仍是 number 快照、不是可观测对象，照样不刷新。
- **错误表现**: 编译通过、首帧数值正确，但运行时数值**永不变**（定时器/网络/推送更新了状态、界面纹丝不动）。
- **修复（从轻到重，别过度拆组件）**:
  - ① **首选、最轻**：`@Builder` **内直读** `this.` 上被订阅的状态（`this.balance`），动态值不走参数、静态标签仍可走值参。**@Builder 本身没问题**，改的只是「动态值别当参数」。
  - ② **仅当各块确有共享结构、值得独立组件时**：抽 `@ComponentV2` 子组件，动态值用 `@Param value` 接入（`@Param` 变化刷新其 UI）。**别为响应式硬拆组件**——单页少量块用 ① 即可。
  - ③ **ForEach / 各块数据源不同时**：传**整个** `@ObservedV2 + @Trace` 对象（**非**它的属性值），builder/子组件内读其 `@Trace` 属性。（`@Builder` 单参且直接传对象字面量才按引用生效，≥2 参不刷新。）
- **grep 自检**: `grep -rnE "@Builder" src/` 逐个核对——参数是否承载**会随状态变化的动态值**、调用处是否传 `xxx.toString()`/某属性值快照。**只有动态值中招才改**（走 ①/②/③）；**静态值参一律不动**。

### P-06: AppStorage 绑定时序
- **Android**: SharedPreferences 首次访问自动创建
- **ArkUI（V1）**: `@StorageLink('key')` 在组件实例化时绑定，如果 key 未预注册则绑定失败
- **ArkUI（V2，API 12+ 推荐）**: 用 `AppStorageV2.connect(Cls, key, () => new Cls())` 配合 `@ObservedV2` 类，**首次 connect 时自动用 `defaultCreator` 初始化**，无需在 EntryAbility 预注册即可工作；如需提前从持久层加载，仍可在 `EntryAbility.onCreate` 调用 `AppStorageV2.connect` 预热
- **错误表现**: V1 组件始终显示默认值，后续更新也无响应（V2 不会出现此问题，因为有 `defaultCreator` 兜底）
- **修复（V1）**: 在 `EntryAbility.onCreate` 中预注册所有 AppStorage key（如 `AppStorage.setOrCreate('key', initValue)`）
- **修复（V2）**: 升级到 V2 `AppStorageV2.connect` 模式，从根本上消除此类时序错误
- **grep 兼容检索**: `grep -E '@StorageLink|AppStorageV2' src/`（同时覆盖 V1 / V2 写法）

### P-07: ConstraintLayout 表达力缺口
- **Android**: ConstraintLayout 支持 chain、ratio、bias、barrier、guideline
- **ArkUI**: RelativeContainer 仅支持基本 alignRules
- **错误表现**: 复杂约束布局塌陷或错位
- **修复**: 复杂约束改用 Row/Column 嵌套 + Flex 布局模拟，或 onMeasureSize 自定义

### P-08: RecyclerView Adapter 模式丢失
- **Android**: Adapter 有粒度通知：notifyItemChanged/Inserted/Removed + DiffUtil
- **ArkUI**: 简单 ForEach(array) 丢失通知粒度，全量重渲染，动画消失
- **错误表现**: 列表无插入/删除动画，性能下降
- **修复**: 使用 LazyForEach + IDataSource 接口，实现 DataChangeListener

### P-09: NavigationView 语义丢失
- **Android**: NavigationView 集成抽屉头部、菜单项、选中状态管理
- **ArkUI**: 无等价物，需自定义 Column + List
- **错误表现**: 抽屉动画、选中高亮、头部滚动行为丢失
- **修复**: 自行实现选中状态管理和动画同步

### P-18: Scroll 内可点击元素的点击被父级手势抢占
- **Android/Compose**: `Modifier.clickable{}` 嵌在 `verticalScroll` 内，tap（无位移）与滚动（有位移）天然区分，点击正常触发
- **ArkUI**: 默认**子组件手势优先**，Scroll 内 Button/可点元素的 tap 通常能触发；但当祖先额外绑了竞争性自定义手势（`PanGesture` / `SwipeGesture` / `priorityGesture`）、或元素处于 Swiper / 嵌套滚动容器、或 `responseRegion` 不准时，父级 Pan 抢走手势 → 子 `onClick` / `TapGesture` 不响应
- **错误表现**: 列表/详情页里「SEE MORE」「展开更多」「行内按钮」点不动，但页面能滚
- **修复**: 先排除 Z-order 遮挡（见 P-17：贴底/全屏 overlay 盖住点击区）；确属手势竞争再按场景选——父子都要响应→子元素 `parallelGesture`（或父级 Pan 改 `parallelGesture`）；仅子响应→子元素 `priorityGesture` / `monopolizeEvents(true)`；嵌套【滚动】手势冲突见 P-25；命中区不准→校正 `responseRegion`

### P-25: 嵌套【滚动】手势被父容器吞——同向可滚子组件放进 Swiper/Scroll/Tabs 内层滑不动
- **Android**: `ViewPager` / `HorizontalScrollView` / `NestedScrollView` 内嵌同向 `RecyclerView` / `ScrollView`，嵌套滚动由框架自动分发，内外都能滑
- **ArkUI**: 内层 `List` / `Scroll` / `Grid` 直接放进 `Swiper` / `Scroll` / `Tabs` 后，**默认 `NestedScrollMode.SELF_ONLY`（不联动）**——同向手势被外层抢走：外层翻页 / 滚动、内层滑不动。编译不报错、纯运行时（典型：Swiper banner 内嵌横向分类 List，手指横滑触发的是 Swiper 翻页、分类条滚不动）
- **错误表现**: 内嵌的横向条 / 二级列表拖不动；或内层滚一点就带着外层一起动、方向错乱
- **修复方向**: 内层可滚组件显式配 `.nestedScroll(…SELF_FIRST)`（内层先滚、到边缘再交父级）+ 有界外尺寸（见 P-22）。**各容器 nestedScroll API / 枚举值 / worked example 见 arkts-component-builder/references/v2-scroll-and-form-components.md §3.5（规则正文以它为准，此处不复写）**
- **负向守卫**: 仅**同向【滚动】**冲突需要——**不同向**嵌套（横滑 Swiper 内竖滑 List 等）默认不冲突、别硬配；**点击 / tap** 被抢是 **P-18** 非本条；外层需先滚（下拉刷新头 / 折叠工具栏）用 `PARENT_FIRST` 非 `SELF_FIRST`
- **区别 P-18**: P-18 是内层元素**点击**被抢（页面能滚、按钮点不动）；P-25 是内层容器**滚动**被父吞（内层根本滑不动）。机制不同、可同页并存

### P-26: 多页/列表内多个 Lottie 全量同播——回收语义丢失
- **Android**: `RecyclerView` / `ViewPager` 有视图回收，屏幕外 item **不渲染、不播动画**；`lottie_autoPlay="true"` 写在 item 布局上，实际只有可见项在播
- **ArkUI**: `Swiper` / 普通 `ForEach` **全量创建所有子项**，把 `LottieAnimationView` 逐格直译成 `autoplay:true` 后**所有分页的动画同时播放**——编译不报错、单帧截图也正常；多页多格时 GPU/内存陡增 → 卡顿、耗电，密集场景有闪退风险
- **修复**: 只播当前可见项——Lottie 组件留 `playing` 控制口，由当前页索引或可见性回调驱动 play/pause；方案选择与组件模板见 **arkts-animation-migrate/references/lottie.md §6.1**（规则正文以它为准，此处不复写）
- **负向守卫**: 仅「全量创建容器 × 多实例 Lottie」需要；**单个/全屏常驻 Lottie（欢迎页、签到弹层）**、以及本身有回收语义的 **`LazyForEach` 列表**，不要硬塞可见性机关
- **区别 P-25**: P-25 是滚动**手势**被父吞（交互层）；P-26 是动画**播放生命周期**没有回收语义（渲染/性能层）。可同页并存

### P-27: Android 页面级 Dialog 直译成全局弹窗——路由跳转后弹窗盖住新页
- **Android**: `Dialog` / `DialogFragment` 是页面级——弹窗开着 `startActivity`，新页天然盖住弹窗、弹窗随宿主销毁，返回后仍在
- **ArkUI**: `@CustomDialog` / `openCustomDialog` / `showDialog` 默认**全局级**（弹窗节点挂页面根节点下，层级高于所有路由/导航页）：路由跳转不自动关闭，弹窗**恒盖在新页之上**。编译不报错、纯运行时
- **错误表现**: 弹窗里点「查看详情/规则」push 新页后，弹窗仍浮在最上层挡住新页；被迫把弹窗改写成页面级组件
- **修复方向**: `openCustomDialog` options 设 `levelMode: LevelMode.EMBEDDED`（API 15+、仅非子窗模式）；或透明弹窗页 `NavDestinationMode.DIALOG`。**规则正文见 arkts-component-builder/references/v2-dialogs-and-sheets.md §2c（以它为准，此处不复写）**
- **负向守卫**: 用完即关、不跨路由跳转的普通确认框 / Toast / Sheet 不需要页面级——别硬套

### P-23: @ObservedV2 / @Trace / @Observed 实例不能 JSON.stringify
- **Android**: Gson（或同类反射序列化库）`toJson(obj)` / `fromJson` 基于反射，序列化全部字段，与字段声明方式无关
- **ArkUI**: `@ObservedV2` / `@Trace` / `@Observed` 把字段转为访问器属性，`JSON.stringify(实例)` 枚举不到这些字段 → 产出空或残缺 JSON；再 `JSON.parse` + `fromJson` 还原即得空对象
- **错误表现**: 经序列化的对象字段全空——跨页传参（NavPathStack param）/ 持久化（Preferences）/ 跨线程（emitter）后，接收端拿到空值、必填校验失败、页面无数据
- **修复**: 不要对观察类实例直接 `JSON.stringify`。给模型显式写 `toJson()` 逐字段构造 plain object / Record，与 `fromJson()` 配对；序列化用 `obj.toJson()`，反序列化用 `Cls.fromJson(JSON.parse(s))`
- **grep 自检**: `grep -rnE "JSON.stringify\(" src/`，逐处确认实参不是 @ObservedV2/@Trace 类实例（应为 `.toJson()` 结果或 plain 对象）

## MEDIUM — 视觉偏差

### P-10: ViewPager → Swiper 生命周期差异
- **Android**: OnPageChangeCallback 在页面可见时触发
- **ArkUI**: Swiper onChange 触发时机与动画阶段关系不同
- **错误表现**: 页面初始化代码在错误时机执行
- **修复**: 关键初始化逻辑放在页面组件的 aboutToAppear 中，不依赖 onChange 回调

### P-11: BottomNavigationView → Tabs 底栏不可见（高度约束问题，非容器约束）
- **Android**: BottomNavigationView 可放在任意位置
- **ArkUI**: `Tabs({ barPosition: BarPosition.End })` 官方**没有**"必须放 Column"之类容器约束；底栏不可见的实际根因通常是 **Tabs 没拿到确定高度**——被放进 wrap-content / 滚动父级，或被同级组件挤压，TabBar 被顶出可视区
- **错误表现**: Tab 栏位置错误、不可见，或整个 Tabs 区域高度异常
- **修复**: 让 Tabs 获得确定高度并占满剩余空间——典型安全形态 `Column(){ Tabs(...).layoutWeight(1) }`，或对 Tabs 显式定高；不要把 Tabs 嵌进无定高的滚动容器

### P-12: 默认 padding/margin 差异
- **Android**: Button 等组件有默认 padding（约 12dp），gravity 从父容器继承
- **ArkUI**: Text / 容器类组件默认 padding 为 0，对齐也不从父容器继承，需显式设置（Button 等带主题预设样式的组件有自带内边距，以官方样式/实测为准，勿一概按 0 处理）
- **错误表现**: 自定义容器拼的"按钮"文字紧贴边框，文本左对齐而非居中
- **修复**: 显式设置 .padding() 和 .textAlign()

### P-13: RelativeLayout z-order 反转
- **Android**: RelativeLayout 子组件顺序不影响布局（由规则决定），但影响绘制顺序
- **ArkUI**: RelativeContainer 的子组件声明顺序决定 z-order
- **错误表现**: 需要在上层的组件被遮挡
- **修复**: 按 z-order 从底到顶排列子组件，或使用 .zIndex()

### P-14: Text 不折行的真因是横向无界约束（默认并非单行截断）
- **Android**: TextView 默认多行显示
- **ArkUI**: Text **默认同样自动折行**（官方 Text.maxLines：「默认情况下，文本是自动折行的」；溢出默认 `TextOverflow.Clip` 裁切，省略号**必须显式设置**）。真正的坑在**约束**：Text 处于横向无界容器（Row 未限宽、横向 Scroll、Flex 不换行）时拿到无限宽 → 单行延伸出屏，看起来像"只显示一行"
- **错误表现**: 文本不折行、单行被裁出屏幕右侧；或误信"默认单行"给正常多行文本加 `.maxLines(N)`，反而把内容截断了
- **修复**: 先给 Text 可达的宽度约束（父级定宽 / `layoutWeight(1)` / 视场景 `.width('100%')`），它即自动折行；确需截断时才显式 `.maxLines(N).textOverflow({ overflow: TextOverflow.Ellipsis })`

### P-15: Image 缩放默认值
- **Android**: ImageView 默认 ScaleType.FIT_CENTER（适应边界，保持比例，居中）
- **ArkUI**: Image 默认 ObjectFit.Cover（填满裁切）
- **错误表现**: 图片裁切方式不同
- **修复**: 设置 .objectFit(ImageFit.Contain)

## 入口配置

### P-16: 入口页面未注册
- **问题**: 迁移后 main_pages.json 仍指向 pages/Index（Hello World）
- **错误表现**: 启动应用显示 Hello World 而非迁移后的主页
- **修复**: a2h-execute Stage 1 全部 Batch 完成后（§3d 收口入口装配），更新 main_pages.json 的 src 数组
