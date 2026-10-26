# gesture-refresh-traps — 手势与刷新静默陷阱（编译全绿、真机才死）

1. 嵌套滚动被父吞：内层 List/Scroll/Grid/WaterFlow 放进 Swiper/Tabs/外层 Scroll，默认 `NestedScrollMode.SELF_ONLY`（不联动），同向手势被外层抢走。修法：内层显式 `.nestedScroll({scrollForward: NestedScrollMode.SELF_FIRST, scrollBackward: NestedScrollMode.SELF_FIRST})` + 有界外尺寸（layout-sizing-traps #2）。四值：SELF_FIRST 内层先滚（最常用）/ SELF_ONLY 默认不联动 / PARENT_FIRST 父先滚（下拉刷新头、折叠工具栏）/ PARALLEL 同滚。负向守卫：仅同向滚动冲突需要，不同向嵌套（横滑 Swiper 内竖滑 List）默认不冲突别硬配；内层内容比自身小且 edgeEffect 未开 alwaysEnabled 时不产生滑动手势，nestedScroll 不生效。
2. @Builder 值参 = 调用时刻快照：动态值（`this.balance.toString()`、`item.value`）当值参传 @Builder → 定格首帧；数据源即使 @ObservedV2+@Trace，取出属性值传参仍是快照。修法从轻到重：① 首选 @Builder 内直读 `this.` 被订阅状态（静态标签仍可走值参）；② 确有共享结构才抽 @ComponentV2 子组件用 @Param；③ ForEach 各块数据源不同时传整个 @ObservedV2 对象（@Builder 单参且传对象字面量才按引用；≥2 参不刷新）。
3. keyGenerator 必须含所有影响显示的可变字段：key 只含 `item.id` 而 VM 用同 id 新对象重建（`new Line({item, count})`）→ 框架判同项、复用旧子组件、不重派 @Param（count/选中态/playState 停旧值）。修法：`item.id + '_' + item.count`，或引用稳定用 @ObservedV2+@Trace 原地改字段。
4. 子元素点击被父手势抢：祖先绑 PanGesture/SwipeGesture/priorityGesture、或元素在 Swiper/嵌套滚动容器内 → 子 onClick 不响应。修法：先排除 Z-order 遮挡（arkui-enums/runtime-patterns 蒙层规则）；确属手势竞争：父子都响应 → `parallelGesture`；仅子响应 → `priorityGesture`/`monopolizeEvents(true)`；命中区不准 → 校正 `responseRegion`。与 #1 区分：#4 点击被抢、#1 滚动被吞，可同页并存。
5. Swiper/ForEach 全量创建 × 多实例 Lottie 全量同播：无回收语义，`autoplay:true` 直译后所有分页动画同播（单帧截图正常）→ GPU/内存陡增。修法：Lottie 留 `playing` 控制口，由当前页索引/可见性回调驱动 play/pause。负向守卫：单个/全屏常驻 Lottie、自带回收的 LazyForEach 不硬塞。

<!-- provenance: runtime（真机迁移复盘 P-05/18/24/25/26）
     source: android-ui-graph-query/references/ui-migration-pitfalls.md; arkts-component-builder/references/v2-scroll-and-form-components.md §3.5 -->
