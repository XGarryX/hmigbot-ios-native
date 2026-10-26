# component — V2 UI 组件规则

## 五条核心约束
1. struct 不是 class：@ComponentV2 只能装饰 struct（禁 `@ComponentV2 class`）；框架管生命周期，禁 new。
2. build() 只放 UI：禁变量声明/console.log/异步调用；仅允许 if/else 与 ForEach/LazyForEach/Repeat；逻辑抽方法或 @Computed。
3. 单根节点：build() 顶层唯一根容器。
4. 属性链式调用：`Text('x').fontSize(16).fontColor('#333')`。
5. 禁 V1/V2 混用：@ComponentV2 内禁 @State/@Prop/@Link；@Param 必须有默认值，@Event 必须有默认实现 `() => {}`；@Builder/@BuilderParam/@Styles/@Extend/@Entry 为 V1/V2 通用。

## 列表选型
- <20 项 → ForEach；≥20 项 → LazyForEach + IDataSource；API12+ 新项目 → Repeat（配 .virtualScroll）。
- 必须提供 keyGenerator；List 内必须 ListItem，Grid 内必须 GridItem。

## 回调三级策略（禁空注释回调）
先 grep 项目确认 Controller/Manager/DAO 是否存在：
- L1 已存在 → 直接调真实方法：`PlaybackController.getInstance().play(...)`
- L2 无 Controller 但有 EventBus/emitter → `emitter.emit(...)` + 接收端 TODO
- L3 都无 → `console.info('TODO:<ACTION>:<COMPONENT>')` 占位，并登记 placeholder-registry（6 字段齐全）
禁 `onClick(() => { /* 注释 */ })`（不可 grep、不报错）。

## 资源引用
用户可见文本/图片/颜色必须 $r()：`$r('app.string.title')`、`$r('app.media.icon')`、`.backgroundColor($r('app.color.bg'))`；rawfile 用 `$rawfile('x.png')`；禁硬编码中英文文案（纯数字/标点/格式占位符除外）。`$r('sys.symbol.xxx')` 名先在 verified-symbols 清单确认存在。

## prop 命名冲突规则
@Param/@Local/@Event/@Provider()/@Consumer() 变量名禁用 CustomComponent 基类冲突名：size/position/value/width/height/type/enabled/opacity/visibility/direction/offset/border/padding/margin/shadow/translate/scale/rotate/zIndex/aspectRatio/flexBasis/flexGrow/flexShrink/alignSelf/layoutWeight/clip/mask/id/key/hitTestBehavior/responseRegion/touchable/monopolizeEvents/onClick；并避开基类方法名 build/aboutToAppear/aboutToDisappear/onPageShow/onPageHide/onBackPress/pageTransition/getUIContext/getHostContext 等。
修法：加业务前缀（width→cardWidth、id→itemId、value→sliderValue、offset→scrollOffset）；@Event 用 `on<Action>` 或 `on<Property>Change`（禁 onClick）。param 类/数据 model 类字段不受限。

## Linter 共存（工程配了自动重写 .ets 的项目级 linter 时）
- 两次即停：同一 .ets 被 linter 回改 >2 次 → 接受 linter 版为基线，只修编译器级错误（类型/属性/导入缺失），不纠结风格（SymbolGlyph vs Image、色值 vs 常量、注释格式）。
- 命名冲突不可妥协：@Param/@Event/getter 撞基类名是编译错，linter 修不了还可能改回——改名后立即 git commit 检查点；linter 再改用 `git checkout -- <file>` 恢复，不重新手编。
- @Builder 与 build() 显式标注 `: void`（防 arkts-no-implicit-return-types）。

## 共享组件资格（抽公共组件前三问，任一不满足 → 各页内联 + 注释标源布局）
1. 源 View/布局被 ≥3 个调用方使用？2. 调用方差异仅限数据（text/visibility/count），非行为/状态？3. 无调用方特有动态逻辑（如方向图标随 portrait/landscape 切换）？
内联优于需 5+ 个 @Param flag 的臃肿抽象；Android include 布局常不是真组件。

## 容器默认对齐反模式（E1-2/E1-4）
1. `ListItem(){…}.width('100%')` 使 `List.alignListItem`（默认 Start）失效、落到内容居中（Android 纵向 LinearLayoutManager+wrap_content 左对齐项）：不给 ListItem 写 width，由内容定宽。
2. Column 默认 `alignItems: Center`、Stack 默认 `Center`，Android 默认左上：须显式 `.alignItems(HorizontalAlign.Start)` / `Stack({alignContent: Alignment.TopStart})`。
3. TextView `drawableStart/End` 复合图标按固有尺寸渲染，不随容器高：翻成 `Row(Image().width(w).height(h), Text)`，尺寸 = drawable 像素÷密度，禁撑到行高。

<!-- source: arkts-component-builder/SKILL.md:L91-183,L249-264,L265-275,L305-355,L330-388; arkts-component-builder/references/v2-prop-naming-rules.md -->
