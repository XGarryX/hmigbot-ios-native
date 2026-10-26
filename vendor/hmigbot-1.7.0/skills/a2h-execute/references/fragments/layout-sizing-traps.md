# layout-sizing-traps — ArkUI 尺寸解析硬事实（与 Android 语义相反，编译不拦）

1. `width/height('100%')` 向上解析：解析到最近一个有确定尺寸的祖先（不是父内容大小）。父级 wrap-content / List 行无定高时该子层撑满整片可用空间（列表行撑成整屏、chip/徽标"背景层"撑成大色块）。修法：背景/描边画在容器自身（`.backgroundColor()`/`.border()`/`.linearGradient()`），由内容定大小；禁 `100%` 子层填父。自检 `grep -rnE "width\('100%'\)|height\('100%'\)"` 后核父级是否 wrap-content。
2. 滚动容器不 wrap 内容：横向 List/Scroll/Grid 缺显式 `.height()` → 有剩余空间撑满父级、被挤则塌成 0（纵向缺 `.width()` 同理）。修法：显式定轴尺寸（= 最高子项 + margin）。同根性能坑：Scroll 嵌 List 内层不定高 → 子项一次性全建，LazyForEach 失效；嵌套必须给内层定高 / `layoutWeight`。
3. Text 默认自动折行（溢出默认 Clip，省略号须显式设）。"只显示一行"的真因是横向无界约束（Row 未限宽 / 横向 Scroll / Flex 不换行）。修法：先给宽度约束（父定宽 / `layoutWeight(1)`），确需截断才 `.maxLines(N).textOverflow({overflow: TextOverflow.Ellipsis})`；别误信"默认单行"乱加 maxLines。
4. Tabs 底栏不可见 = 没拿到确定高度：放进 wrap-content/滚动父级或被同级挤压，TabBar 顶出可视区。安全形态 `Column(){ Tabs(...).layoutWeight(1) }`；Tabs 别嵌无定高滚动容器。Tabs 放 Navigation 内部时 NavDestination 盖住整个区域（含 Tab 栏）：Tabs 放外部或自定义 Row 做 Tab 栏。
5. SideBarContainer 子组件顺序与 DrawerLayout 相反：第一个子组件 = 侧边栏，第二个 = 主内容。转换时交换顺序，否则侧边栏占满全屏。
6. RelativeContainer：子组件声明顺序决定 z-order（RelativeLayout 不受顺序影响），按底→顶排列或 `.zIndex()`；无 chain/ratio/bias/barrier/guideline，复杂约束改 Row/Column 嵌套 + Flex 模拟。CoordinatorLayout 折叠联动无等价物：Scroll `onScroll` 回调手动算 AppBar 高度/透明度。
7. Image 默认 `ObjectFit.Cover`（裁切），ImageView 默认 FIT_CENTER：需 `.objectFit(ImageFit.Contain)` 对齐。
9. 无尺寸约束的 `Image` 撑满可用空间（Android `wrap_content` = 图片固有尺寸；ArkUI 无 width/height 的 Image = 撑满父级），语义正好相反（角标撑爆顶栏、整屏塌版，编译/静态全过）。规则：每个 `Image()` 必须带 `.width()+.height()`，或一边 + `.aspectRatio()`，或 `.size()`；尺寸按 Android 资源固有尺寸（drawable 像素 ÷ 密度倍数，xxhdpi ÷3）或布局里的 dp 值填。自检：`arkts-structural-closure/scripts/icon/icon_audit.py`（audit 波 round-0 预检已挂）。
8. 默认 padding=0、对齐不继承：Text/容器类默认无内边距、不继承父 gravity；自拼"按钮"须显式 `.padding()` + `.textAlign()`（Button 等主题组件有预设内边距，按实测为准）。
10. ConstraintLayout 约束链换算（E1-3）：`top→X.top`/`bottom→Y.top` 这类相对锚点必须先换算到容器原点再写 Stack 子项 offset/margin（直接抄相对值会整体偏移、元素重叠）。优先同 Stack 同高同原点靠 z-order 覆盖，不用 offset。

<!-- provenance: runtime（真机迁移复盘 P-01/02/03/07/11/12/13/14/15/20/22）
     source: android-ui-graph-query/references/ui-migration-pitfalls.md -->
