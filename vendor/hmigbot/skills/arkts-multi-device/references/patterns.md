# 多设备适配 · 错误模式汇总

从 OpenHarmony 历史修复中归纳的 5 类错误模式。每个模式包含：典型症状、涉及组件、底层机制、排查提示、修复建议。

---

## 模式 1：硬编码尺寸 / 边距，无法跨设备放大

### 典型症状
- 标题栏在平板/大屏上仍然只有 16vp 左右边距，视觉"贴边"
- 卡片/内容区在折叠屏展开后没有变宽的层次感
- 按钮组在大屏上间距偏小，点击热区堆在一起
- 同一页面在手机上合适，在平板上显得"信息太稀"或"太挤"

### 高发组件
`Navigation` / `TitleBar` / `EditableTitleBar` / `Toolbar` / 自定义卡片容器 / `Row/Column` 根容器。

### 底层机制
早期 ArkUI 组件主题（theme）里很多尺寸写死为手机基线（如 `title_margin_left = 16vp`、`list_item_padding = 12vp`）。跨设备后这些数值不再合适，但组件没有"按容器宽度分档"的能力。系统后来补了 `margin_level1 / level2 / level3` 资源 token 和 S/M/L 三档断点主题，组件内部根据容器宽度选档。

### 排查提示
1. 在可疑布局里全局搜 `.margin(`、`.padding(`、`.width(`、`.height(` 后跟字面数字的位置
2. 确认是否用了 `$r('sys.float.margin_level*')` 或自定义资源
3. 切到不同设备 / 修改窗口大小，用 ArkUI Inspector 看边距是否变化

### 修复建议
- 所有尺寸/间距走系统 token：
  - 间距：`$r('sys.float.margin_level1|2|3')`、`$r('sys.float.padding_level*')`
  - 圆角：`$r('sys.float.corner_radius_level*')`
  - 元素尺寸：`$r('sys.float.ohos_id_button_small_height')` 等
- 自定义主题需要 S/M/L 档时，用断点切换（V2 推荐：把当前断点封装到 `@ObservedV2` 类，通过 `AppStorageV2.connect` 全局共享）：
  ```ts
  @ObservedV2
  export class BreakpointModel {
    @Trace currentBp: string = 'sm';
  }

  @ComponentV2
  struct ThemedRoot {
    @Local bp: BreakpointModel = AppStorageV2.connect(BreakpointModel, 'breakpoint', () => new BreakpointModel())!;

    @Computed
    get horizPadding(): number {
      return this.bp.currentBp === 'lg' ? 32 : this.bp.currentBp === 'md' ? 24 : 16;
    }
  }
  ```
  > V1 等价：`@StorageProp('currentBreakpoint') currentBp: string = 'sm'` 加普通 getter。
- 组件级：优先用系统高级组件（`Navigation`、`TabContent`、`ComposeListItem` 等），它们已内置分档

---

## 模式 2：列表/网格组件列数固定，不随断点变化

### 典型症状
- `Grid/WaterFlow` 在平板上仍是 2 列，空间浪费
- `List.lanes(2)` 在手机竖屏下两列挤到内容溢出
- 同一页内容密度在所有设备上一样

### 高发组件
`Grid` / `WaterFlow` / `List`（双列/多列模式）

### 底层机制
早期 API：
- `columnsTemplate: string`（"1fr 1fr 1fr"）
- `lanes: number | LengthConstrain`
两者都是静态值，无法响应容器宽度。新 API 引入 `ItemFillPolicy` / `PresetFillType` 断点策略对象，在底层按当前断点自动切换列数。

### 排查提示
1. 搜代码里的 `columnsTemplate(` 和 `lanes(` 调用点
2. 如果参数是字符串/数字常量 → 就是这个模式
3. 检查 API Level 是否 ≥ 12（断点对象才可用）

### 修复建议
- 用断点策略代替字符串：
  ```
  Grid().columnsTemplate({ fillType: PresetFillType.BREAKPOINT_SM1MD2LG3 })
  WaterFlow().columnsTemplate({ fillType: PresetFillType.BREAKPOINT_SM2MD3LG5 })
  List().lanes({ fillType: PresetFillType.BREAKPOINT_SM1MD2LG3 }, gutter)
  ```
- API Level < 12 回退方案（V2 写法，复用上面的 `BreakpointModel`）：
  ```ts
  @ComponentV2
  struct GridPage {
    @Local bp: BreakpointModel = AppStorageV2.connect(BreakpointModel, 'breakpoint', () => new BreakpointModel())!;

    @Computed
    get cols(): string {
      return this.bp.currentBp === 'lg' ? '1fr 1fr 1fr' : this.bp.currentBp === 'md' ? '1fr 1fr' : '1fr';
    }

    build() {
      Grid().columnsTemplate(this.cols)
    }
  }
  ```
  > V1 等价：`@StorageProp('currentBreakpoint') bp: string = 'sm'` 加普通 getter，`@Component struct GridPage`。
- 页面级布局分档优先用 `GridRow + GridCol`：
  ```
  GridRow({ breakpoints: { value: ['320vp','600vp','840vp','1440vp'] } }) {
    GridCol({ span: { sm: 12, md: 6, lg: 4 } }) { /* item */ }
  }
  ```

---

## 模式 3：折叠屏硬件特殊性未处理（铰链区、物理旋转）

### 典型症状
- 浮层（Dialog、Popup、自定义弹窗）正好落在屏幕中间的折痕上，被物理遮挡或显示变形
- 折叠屏从折叠切到展开后，XComponent / Canvas 绘制内容旋转异常（错 90°/180°）
- 内容虽能显示但避开折痕后可用区"凭空"变小

### 高发组件
`Dialog / CustomDialog / AlertDialog` / `Popup / Sheet` / `XComponent` / 自定义浮层。

### 底层机制
- **折痕**：折叠屏设备在展开态下有一块物理铰链区域（通常屏幕纵向中部），应用若把内容/浮层正好放这里会被遮挡。系统通过 `display.getFoldCreaseRegion()` 暴露矩形。
- **旋转**：折叠屏外屏/内屏物理摆放方向不同，展开态对 `XComponent` 等直接渲染表面需要在 `display.rotation`（屏幕逻辑旋转 0/1/2/3）基础上叠加**设备物理偏移**——该偏移字段因设备/SDK 版本而异，优先查 `display.getDefaultDisplaySync()` 返回的非标字段（可能叫 `defaultDeviceRotationOffset` 或类似），没有则走设备适配表。最终渲染旋转角 = 屏幕逻辑旋转 × 90° + 设备偏移，再对 360 取余。

### 排查提示
1. 折叠屏上打开问题页面 → ArkUI Inspector 看浮层 Y 坐标
2. 打印 `display.getFoldCreaseRegion().creaseRects` 与浮层 rect 对比
3. 如果是旋转问题，打印 `display.rotation` 和 `display.getDefaultDisplaySync()` 的其他字段，确认是不是只用了一个

### 修复建议
- 浮层优先用系统 API：`AlertDialog.show`、`promptAction.showDialog`、`Menu`、`Popup`——系统已做折痕避让
- 自定义浮层：
  ```ts
  const crease = display.getFoldCreaseRegion();
  const rects = crease?.creaseRects ?? [];
  // 在 onWillShow 里计算目标 Y，避开 crease.top..crease.bottom
  ```
- XComponent 旋转：
  ```ts
  const disp = display.getDefaultDisplaySync();
  const base = disp.rotation;                        // 0 / 1 / 2 / 3
  const offset = (disp as any).defaultDeviceRotationOffset ?? 0;
  const final = (base * 90 + offset) % 360;
  // 把 final 传给 XComponent 的渲染 surface 或做自身 transform
  ```
- 监听折叠状态切换：
  ```ts
  display.on('foldStatusChange', (status) => {
    // EXPANDED → FOLDED 时重算布局；不要依赖 aboutToAppear 的尺寸快照
  });
  ```

---

## 模式 4：窗口形态感知错误（用屏幕尺寸替代窗口尺寸 / 不监听窗口变化）

### 典型症状
- 应用在自由窗口（FLOATING）模式下超出边界，绘制到窗口外
- 分屏下布局仍按全屏宽度计算，内容被裁剪
- 窗口缩放时页面不刷新，保持初始尺寸
- 2in1 上从触屏切到外接屏，UI 不响应

### 高发组件
根容器（`Stack / Column / Row` 根节点）/ 固定宽度卡片 / 自定义悬浮元素 / `Toast`（系统已修）。

### 底层机制
- 屏幕尺寸 `display.width/height` 是**物理屏幕**的，与应用可绘制区域无关
- 自由窗口下有边框（~4vp）+ 标题栏（~37vp）+ 边距，**窗口矩形 ≠ 屏幕矩形**
- 多实例（同一应用多开）时各实例窗口尺寸独立，不能用全局变量缓存

### 排查提示
1. 搜 `display.getDefaultDisplaySync()` 的调用点，看是否该换成窗口 API
2. 是否订阅了 `window.on('windowSizeChange')`
3. 是否把第一次拿到的宽高存成 `@Local`（V1：`@State`）之后不再更新

### 修复建议
- 取尺寸用窗口：
  ```ts
  const win = await window.getLastWindow(getContext());
  const rect = win.getWindowProperties().windowRect;  // 这才是可绘区
  ```
- 订阅变化：
  ```ts
  win.on('windowSizeChange', (size) => {
    this.appWidth = px2vp(size.width);
    this.appHeight = px2vp(size.height);
  });
  ```
- 避免 `.width('100vp固定值')`，用百分比或 Flex：
  ```
  Column().width('100%')          // 跟随窗口
  Column().constraintSize({ maxWidth: 840 })   // 大屏有上限
  ```
- 不要全局变量缓存尺寸；宽高应存在组件 `@Local`（V1：`@State`）或 `AppStorageV2`（V1：`AppStorage`）并监听更新

---

## 模式 5：方向/多屏/多实例导致的状态污染

### 典型症状
- 阿拉伯语/希伯来语下按钮在错的一侧、图标左右反
- 应用拖到副屏（外接显示器）上，仍按主屏 DPI 绘制
- 同一应用多实例（PC 多开）下，其中一个实例的布局影响了另一个
- 主副屏切换后白屏或布局错乱

### 高发组件
任何用 `{ left, right }` 的布局；自定义组件含全局/静态变量；跨屏浮窗。

### 底层机制
- **方向**：ArkTS 推荐 `LocalizedMargin/LocalizedPadding/LocalizedEdges`，系统按 locale 自动映射 `start↔left`、`end↔right`。用 `left/right` 等于硬编码 LTR。
- **多屏**：每块屏幕有自己的 `displayId`、`densityDpi`、`rotation`。应用要通过 `getWindowProperties().displayId` 取当前窗口所在屏幕的 `Display`。
- **多实例**：应用静态变量（模块级 `let x = ...` / `static` 类字段）在同一进程多窗口下共享，会互相污染。布局相关状态必须是组件实例的 `@Local`（V1：`@State`）。

### 排查提示
1. 语言方向：全局搜 `Edges({ left`、`.margin({ left`、`Alignment.Start`、`FlexDirection.Row` + RTL 场景
2. 多屏：搜 `display.getDefaultDisplaySync`；应改为从 window 取 displayId
3. 多实例：检查模块顶层的 `let/const` 是否存储了"当前屏幕宽度、当前断点"等可变量

### 修复建议
- 方向：
  ```
  .margin({ start: LengthMetrics.vp(16), end: LengthMetrics.vp(8) })
  .padding({ start: 16, end: 8 })            // v12+ 支持 Localized
  ```
- 取当前屏幕：
  ```ts
  const win = await window.getLastWindow(getContext());
  const displayId = win.getWindowProperties().displayId;
  const disp = display.getDisplayByIdSync(displayId);
  ```
- 多实例：所有可变 UI 状态放组件 `@Local`（跨层级共享用 `@Provider`/`@Consumer`；V1：`@State` 或 `LocalStorage`）；跨实例共享用 `AppStorageV2.connect(Cls, key, ...)` 并订阅更新事件（V1：`AppStorage`），不要用模块静态变量
- 主副屏：监听 `display.on('change')` 和 `window.on('windowVisibilityChange')`，重新读取 displayId 并刷新布局
