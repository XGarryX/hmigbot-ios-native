# 多窗口形态 · 错误模式汇总

从历史缺陷与华为官方 BPTA 最佳实践归纳的错误模式。每个模式包含：典型症状、高发组件、触发场景、底层机制、排查提示、修复建议。

---

## 模式 1：浮层用屏幕坐标而非"节点所在窗口"坐标

### 典型症状
- Toast 在自由窗口/悬浮窗里飘到屏幕角落，跟应用窗口完全脱节
- ContextMenu / Menu / SubMenu 弹出位置远离触发点
- 自由多窗下菜单被截断（高度计算超过窗口实际可用区）
- bindContextMenu 在子窗里偏移到主窗位置

### 高发组件
`Toast` / `Menu` / `ContextMenu` / `SubMenu` / `Popup` / `CustomDialog` / `bindSheet` / `Picker` / 自定义浮层。

### 底层机制
浮层位置的正确公式：

```
浮层屏幕坐标 = 触发节点屏幕坐标 + 偏移
            ≠ 触发节点 layoutRect + 主窗 windowRect.left
```

错误的实现往往：
- 用 `display.getDefaultDisplaySync().width` 当应用宽度（屏幕而非窗口）
- 在 `bindContextMenu` / `bindSheet` / `promptAction` / 自定义弹窗的 builder 闭包里捕获了**主窗**的 UIContext，子窗里弹起后位置算到主窗去了
- 没区分系统置顶子窗（`ToastShowMode.SYSTEM_TOP_MOST` 或子窗 `isTopmost=true`）——它们跨窗显示，偏移应基于屏幕而非宿主窗
- 自由窗口下没扣窗口边框（约 2vp）+ 标题栏（约 37vp）

### 排查提示
1. 在出问题的浮层 builder 里立刻打印 `this.getUIContext().getWindowName?.()` 与主窗对比
2. 用 ArkUI Inspector 看浮层节点 `frame.x` / `frame.y` 是否落在 `windowRect` 内部
3. 系统 Toast 异常优先尝试切换 `ToastShowMode`：`DEFAULT` vs `TOP_MOST` vs `SYSTEM_TOP_MOST`，可定位是不是层级判断错
4. 自由窗口里如果浮层位置整体偏移了 ~37vp，怀疑标题栏未扣

### 修复建议
- ArkTS 侧获取窗口尺寸用窗口 API，不用 display：

```ts
const ctx: UIContext = this.getUIContext();
const win = window.findWindow(ctx.getWindowName());
const rect = win.getWindowProperties().drawableRect;   // 真实可绘
```

- 自定义浮层的 X/Y 用 `componentUtils.getRectangleById(id)` 读取触发组件的 windowOffset：

```ts
import componentUtils from '@ohos.arkui.componentUtils';
const r = componentUtils.getRectangleById('triggerBtn');
// r.windowOffset 是相对当前窗口左上角的位置
```

- 系统 Toast/Dialog 在子窗口下显式声明层级：

```ts
promptAction.showToast({
  message: 'hi',
  showMode: promptAction.ToastShowMode.TOP_MOST,   // 或 SYSTEM_TOP_MOST
});
```

- 自定义弹窗在窗口尺寸变化时主动重算位置（见模式 3）

---

## 模式 2：自由窗口下未补偿边框 / 标题栏 / 内边距

### 典型症状
- 自由窗口（带边框和标题栏）下点击/hover 位置整体偏一段距离
- 二级菜单 hover 热区错位，鼠标从一级菜单移过去就触发关闭
- 弹窗位置整体下移 ~37vp（标题栏高度）
- GridRow 在自由窗口里断点判定偏大（被算成 lg，实际只有 md 宽度）
- Stack 里的 MenuItem `originOffset.y` 多出标题栏高度

### 高发组件
`Menu` / `SubMenu` / `MenuItem` / `Popup` / 自定义浮层 / `GridRow` (`BreakpointsReference.WindowSize`)

### 底层机制
自由窗口（`window.WindowMode.FLOATING`）的窗口实际包含：

- 约 **2vp** 的边框（左右上下）
- 约 **37vp** 的顶部标题栏
- 内容区与边框之间还有一层 padding

坐标系基准因参照物不同而错位：
- **鼠标事件**坐标：相对**窗口左上角**（含边框和标题栏）
- **菜单/浮层内容节点**：相对**内容区左上角**（已扣边框 + 标题栏）

两者直接相减就会差出"边框 + 标题栏"那一段。

`GridRow` 的 `BreakpointsReference.WindowSize` 也踩过同样坑：直接用 `windowRect.width` 当判定值，没扣边框，自由窗口里被误判为更大档位。

### 排查提示
1. 自由窗口下偏移大约等于 37vp 的，几乎都是标题栏未补偿
2. 看代码里有没有混用：UI 事件坐标 vs 节点 layout 坐标，前者基于窗口外框，后者基于内容区
3. GridRow 排查时切 `BreakpointsReference.ComponentSize`，能正常断点说明就是这个模式

### 修复建议
- 自由窗口判定与高度补偿：

```ts
const win = await window.getLastWindow(getContext(this));
const props = win.getWindowProperties();
if (props.windowMode === window.WindowMode.FLOATING) {
  // 自定义热区 / 浮层位置时补偿
  const titleBar = vp2px(37);   // 标题栏
  const border   = vp2px(2);    // 边框
  hotspotY -= titleBar + border;
}
```

- GridRow 在自由窗口下推荐用 `ComponentSize` 参照系：

```ts
GridRow({
  breakpoints: {
    value: ['320vp','600vp','840vp','1440vp'],
    reference: BreakpointsReference.ComponentSize,   // 不依赖 windowRect
  },
}) { /* ... */ }
```

- 系统资源里 Picker / SubWindow 弹窗高度限制：

```ts
.constraintSize({ maxHeight: 640 })
// 或：$r('sys.float.picker_device_height_limit')
```

---

## 模式 3：未监听 windowSizeChange，状态卡在初始尺寸

### 典型症状
- 把窗口从全屏拖到自由窗口或调小后，页面布局保持原样、内容溢出
- Swiper 切换动画途中改变窗口形态，最终卡在两页之间
- 多窗下 `visibleAreaChange` 不回调（旧版本框架 bug）
- 半模态 `bindSheet` 进入小窗后还是中央样式而不是底部样式
- 拖拽窗口边缘时 XComponent / 自定义画布未刷新

### 高发组件
根容器 / `Swiper` / `XComponent` / `Canvas` / `bindSheet` / 任何依赖固定宽高计算的组件

### 底层机制
- 应用窗口尺寸变化由 `window.on('windowSizeChange')` 上抛
- ArkTS 的 `@Local`（V1：`@State`）不会自动跟随窗口尺寸——必须在回调里赋值
- 进行中的动画（Swiper / 转场 / Animator）在 surface 改变时不会被框架自动中断，需要主动 `finishAnimation()`，否则停在动画中间帧
- 某些组件回调（如 `visibleAreaChange`）依赖底层 Vsync 中转，在多窗特定路径上有过事件丢失，应用层无法完全规避

### 排查提示
1. 在根组件 `aboutToAppear` 里订阅一次 `windowSizeChange`，看回调是否进入
2. 如果回调进入但 UI 没变，看是不是把宽高存到了**模块顶层 let** 而不是 `@Local`（V1：`@State`）
3. Swiper 卡中间帧问题：在尺寸变化日志的同一时刻打印 `this.swiperController` 状态

### 修复建议
- 标准订阅模板：

```ts
@ComponentV2
struct WindowAwareRoot {
  @Local winW: number = 0;
  @Local winH: number = 0;
  private win?: window.Window;

  async aboutToAppear() {
    this.win = await window.getLastWindow(getContext(this));
    const r = this.win.getWindowProperties().drawableRect;
    this.winW = px2vp(r.width);
    this.winH = px2vp(r.height);

    this.win.on('windowSizeChange', this.onSize);
    this.win.on('avoidAreaChange', this.onAvoid);
  }
  aboutToDisappear() {
    this.win?.off('windowSizeChange', this.onSize);
    this.win?.off('avoidAreaChange', this.onAvoid);
  }
  private onSize = (size: window.Size) => {
    this.winW = px2vp(size.width);
    this.winH = px2vp(size.height);
    // 主动收尾任何进行中的动画
    this.swiperController?.finishAnimation();
  };
  private onAvoid = (data: window.AvoidAreaOptions) => { /* … */ };
}
```

> V1 等价：`@Component` → `@ComponentV2`、`@State` → `@Local`。

- 半模态根据窗宽切换样式：

```ts
.bindSheet($$this.show, this.builder, {
  preferType: this.winW < 600
    ? SheetType.BOTTOM
    : SheetType.CENTER,
  onWidthDidChange: (w) => { /* 5.0+ */ },
  onTypeDidChange:  (t) => {},
})
```

- 多窗下 `visibleAreaChange` 不可靠时的兜底：

```ts
this.win?.on('windowVisibilityChange', (visible) => {
  // 用窗口可见性补充组件可见性
});
```

---

## 模式 4：分屏 / 自由窗口下安全区与键盘避让算错

### 典型症状
- 分屏**下半屏**（SPLIT_SECONDARY）顶部被状态栏遮住，或 Web 内容超出可视区
- 自由窗口里弹窗被键盘部分遮挡
- 自由窗口里弹窗避让键盘时**上移过多**，整个挪到屏幕外
- 自由窗口被拖到屏幕底部以下时，键盘明明没弹也算出虚假 `keyboardHeight`，导致页面莫名上移
- Web 在分屏左/右窗下避让计算错位（用了窗口绝对坐标）

### 高发组件
`Web` / `Popup` / `CustomDialog` / `bindSheet` / `TextInput` / `TextArea` / 任何根容器需要避状态栏

### 底层机制
- `getWindowAvoidArea(TYPE_SYSTEM)` 给出系统栏避让矩形；分屏副窗（`WindowMode.SECONDARY`）曾在旧版本框架里漏判，需显式 `.expandSafeArea`
- 键盘避让 `TYPE_KEYBOARD` 给的是相对窗口的高度。自由窗口若窗口底边已在屏幕外，框架旧实现可能用 `deviceHeight − windowRect.bottom` 做差值，**未先判 `keyboardHeight > 0`** → 负负得正算出虚假高度
- 自由窗口下根 Stage 节点不是全屏，自定义键盘避让需再减去窗口边框（约 2vp）和标题栏（约 37vp），否则避让过头
- Web 等使用绝对坐标 (`windowRect.Left()` 等) 计算 padding，分屏窗口起点非 (0,0) 时会偏出一截

### 排查提示
1. 打印 `getWindowAvoidArea(TYPE_SYSTEM)` 与 `TYPE_KEYBOARD`，看 top/bottom 是否合理
2. 自由窗口键盘问题：把窗口拖到屏幕底部以下复现，看 `keyboardHeight` 是否非零
3. 分屏问题用 Inspector 抓根节点 `padding`，对比 safeArea 是否真的应用上

### 修复建议
- 系统/键盘避让用声明式 API，框架已分窗口模式处理：

```ts
Stack() { /* … */ }
.expandSafeArea(
  [SafeAreaType.SYSTEM, SafeAreaType.KEYBOARD],
  [SafeAreaEdge.TOP, SafeAreaEdge.BOTTOM]
)
```

- 自定义键盘避让必须先判存在：

```ts
win.on('avoidAreaChange', (data) => {
  if (data.type !== window.AvoidAreaType.TYPE_KEYBOARD) return;
  const kbd = data.area.bottomRect.height;
  if (kbd <= 0) {                  // ← 关键：键盘没弹起就别算
    this.keyboardOffset = 0;
    return;
  }
  // 自由窗口要扣窗口边框 + 标题栏
  let offset = kbd;
  const props = win.getWindowProperties();
  if (props.windowMode === window.WindowMode.FLOATING) {
    offset -= vp2px(37) + vp2px(2);
  }
  this.keyboardOffset = Math.max(offset, 0);
});
```

- 分屏下半屏务必显式避让：

```ts
Column() { /* … */ }
.width('100%').height('100%')
.expandSafeArea([SafeAreaType.SYSTEM])  // 即便上半屏正常，也加这一行
```

---

## 模式 5：子窗 / UIExtension / SystemTopMost 上下文混淆

### 典型症状
- 子窗口（subWindow / systemTopMost）里的 Dialog 遮罩没盖住正确区域，或位置偏到主窗
- UIExtension 子窗里弹 Toast 显示在宿主窗中央而非自己窗内
- 主窗调 `bindContextMenu` 一切正常，子窗里调位置就乱
- 窗口尺寸改变后子窗里的浮层未重新布局
- 跨窗 Toast / 系统级 Dialog 显示位置与宿主对不上

### 高发组件
`Toast` / `Dialog` / `Menu` / `ContextMenu` / `bindSheet` / 任何通过 `createSubWindow` / `SYSTEM_TOP_MOST` / UIExtension 显示的浮层

### 底层机制
每个窗口（主窗 / 子窗 / UIExtension 子窗）有**独立的 UIContext**。浮层位置的计算基于当前 UIContext 中的窗口信息；若拿错就会错位。

典型踩坑：
- 在外部闭包中捕获了主窗的 `UIContext` / `getContext()`，传到子窗 builder 中使用
- `Toast.showMode` 取 `DEFAULT` / `TOP_MOST` / `SYSTEM_TOP_MOST` 偏移基准不同——`SYSTEM_TOP_MOST` 是跨窗显示，应基于**显示屏**坐标而不是宿主窗坐标
- UIExtension 子窗与宿主进程不同，共享 AppStorage 但 UIContext 不同
- 主窗 `windowSizeChange` 后没通知子窗，子窗里的浮层用了过期尺寸

### 排查提示
1. 弹窗 builder 第一行打印 `this.getUIContext().getHostContext()` 看是不是子窗 ability
2. Toast 异常时切换 `showMode` 三种值各试一次，正常那个的逻辑就是当前问题路径
3. UIExtension 排查：用 `@ohos.app.ability.UIExtensionContentSession` 提供的 `loadContent` 选项确认 context 链
4. 子窗弹窗在窗口缩放后未刷新——监听 `windowSizeChange`，主动 `close + open` 重建

### 修复建议
- 为子窗弹窗显式指定层级：

```ts
promptAction.showToast({
  message: msg,
  showMode: promptAction.ToastShowMode.TOP_MOST,    // 在子窗里正常显示
});

// CustomDialog
this.dialogController = new CustomDialogController({
  builder: MyDialog(),
  isModal: true,
  showInSubWindow: true,    // 在独立子窗里显示，不受主窗裁剪
});
```

- UIExtension 内部用 session 提供的 context，不要依赖宿主 context：

```ts
// UIExtensionAbility 里
onSessionCreate(want, session: UIExtensionContentSession) {
  session.loadContent('pages/Index', new LocalStorage());
  // 此后该页面 this.getUIContext() 拿到的是子窗自己的
}
```

- 子窗在尺寸变化时主动重建浮层：

```ts
subWin.on('windowSizeChange', () => {
  this.dialogController?.close();
  // 等下一帧再 open，避免位置用旧尺寸
  setTimeout(() => this.dialogController?.open(), 0);
});
```

---

## 模式 6：窗口拖动 / 模式切换后状态残留（选中、菜单、光标、拖拽预览）

### 典型症状
- 自由窗口移动后，文本选中高亮不消失
- 自由窗口拖动后，复制粘贴菜单/SelectionMenu 一直挂在原位置
- 输入框获焦态显示为多个手柄，或光标不闪烁
- 全屏 ↔ 自由窗口切换后第一次拖拽，预览图从屏幕外飞入
- 分屏后选择手柄拖动卡顿、不跟手

### 高发组件
`TextInput` / `TextArea` / `RichEditor` / 选中菜单（SelectionMenu） / 选择手柄 / 拖拽预览（Drag / DragDrop）

### 底层机制
窗口尺寸/位置变化时，框架内部需要清理一批"瞬时状态"——光标、选中区间、选择手柄、复制菜单、ContextMenu、拖拽预览节点——旧版本不少路径只清理了一部分，导致残留。

- 拖拽场景下，预览节点位置 = `节点屏幕中心 − 当前窗口偏移`；窗口移动后未重新读取窗口偏移就会算错
- 长按拉起菜单 + 后续 Tap 之间没有状态机区分时，Tap 会被错误识别为"普通点击"再拉起键盘

### 排查提示
1. 复现路径：选中文字 → 拖动窗口 / 切换模式，看哪些 UI 还在
2. Inspector 看选择手柄节点是否仍存在；存在说明选择菜单 / 手柄没关闭
3. 拖拽预览偏移：拖拽前后各打一次 `getWindowProperties().windowRect`，看是不是用了缓存值
4. 输入框光标不闪：检查 `focusable` 是否为 true、当前节点是否真的 focused

### 修复建议
- 在 `windowSizeChange` 中主动清理：

```ts
this.win.on('windowSizeChange', () => {
  // 文本组件
  this.textController?.closeSelectionMenu();
  this.textController?.stopEditing();
  // 自定义浮层 / 菜单
  this.popupVisible = false;
  this.menuVisible = false;
  // 拖拽预览（如果是自定义实现）
  this.dragPreviewVisible = false;
});
```

- 拖拽预览定位用屏幕坐标 − 当前窗口偏移：

```ts
import componentUtils from '@ohos.arkui.componentUtils';
const node = componentUtils.getRectangleById('dragSrc');
const winRect = win.getWindowProperties().windowRect;
const screenX = node.screenOffset.x;     // 屏幕绝对
const screenY = node.screenOffset.y;
this.previewX = screenX - winRect.left;  // 转回当前窗口
this.previewY = screenY - winRect.top;
```

- 长按 + 后续点击的状态区分：

```ts
@ComponentV2
struct LongPressItem {
  @Local private isLongPress: boolean = false;

  build() {
    Row() { /* ... */ }
      .gesture(LongPressGesture()
        .onAction(() => { this.isLongPress = true; this.openMenu(); }))
      .onClick(() => {
        if (this.isLongPress) { this.isLongPress = false; return; }
        // 真正的点击行为
      })
  }

  private openMenu(): void { /* ... */ }
}
```

> V1 等价：`@State` → `@Local`。

- 鼠标 hover 自动消失菜单（避免标题栏分屏菜单不消失）：

```ts
private hoverTimer = -1;
Menu() { /* … */ }
.onHover((isHover) => {
  if (isHover) {
    clearTimeout(this.hoverTimer);
  } else {
    this.hoverTimer = setTimeout(() => { this.menuVisible = false; }, 1000);
  }
})
```

---

## 模式 7：分屏/悬浮窗后窗口高度缩小，固定高度内容被截断且无法滚动

### 典型症状
- 应用全屏正常，进入分屏（上下分屏，窗高变成 1/2 或 1/3）或竖向悬浮窗（3:4.575 比例）后，垂直方向内容被截断
- 页面无法上下滑动查看剩下的内容
- `CustomDialog` 分屏后底部按钮盖住中间内容（按钮用 `position({bottom:0})` 定位）
- 子组件 `.height(500)` 在分屏后大于父容器，父容器被撑溢出

### 高发组件
`NavDestination` 根容器 / `Column` / `CustomDialog` / 任何用固定 vp 值作为高度的页面

### 底层机制
- 分屏比例由产品定义（手机上下分屏常见 1:1 / 1:2 / 2:1），应用无法控制
- 竖向悬浮窗宽高比 ≈ 3:4.575，与全屏 16:9 / 4:3 差异大
- 内容若是固定高度 + 非滚动容器，窗口一缩内容就溢出且无兜底

### 排查提示
1. 把窗口从全屏切到分屏，若"看不见 + 滚不动"几乎必是此模式
2. 检查根容器是否被 `Scroll` 包裹；`CustomDialog` 是否配了 `constraintSize({maxHeight: '...%'})`
3. 检查子组件高度：绝对 vp 值可疑，百分比/`layoutWeight` 安全

### 修复建议
- 根容器包 `Scroll`，允许超出时滚动查看：

```ts
NavDestination() {
  Scroll() {
    Column({ space: 12 }) { /* ... */ }
  }
}
```

- 弹窗设 maxHeight 百分比 + 内容区占剩余：

```ts
@CustomDialog struct MyDialog {
  build() {
    Column() {
      Text('标题')
      Column() { Scroll() { /* 内容 */ } }.layoutWeight(1)  // 占剩余
      Row() { Button('取消'); Button('确定') }.height(56)   // 自然贴底
    }
    .constraintSize({ maxHeight: '80%' })
  }
}
```

- 次要元素用 `.displayPriority(n)`，窗口太小时优先折叠低优先级（一多隐藏能力）

---

## 模式 8：XComponent / Video 在分屏下宽高比错乱或被截断

### 典型症状
- 分屏后视频画面被拉伸/形变（XComponent）
- 分屏后视频超出窗口底部被裁（Video，高度 100% + 100% 宽度）
- 用 `display.getDefaultDisplaySync().width * aspect` 手算尺寸，窗口变化后尺寸不跟

### 高发组件
`XComponent`（SURFACE 类型）/ `Video` / 任何依赖 surface 宽高比的播放器

### 底层机制
- XComponent 的 SURFACE 需要应用侧显式控制宽高比；默认并不自动 aspectRatio
- Video 默认 `objectFit` 为填充模式，保持比例放大到铺满，若宽度已等于窗宽、高度又写 100%，画面会超过窗口高度
- 很多应用在 `aboutToAppear` 里基于 `display` 算出固定值存到 `@Local`（V1：`@State`），不监听 `windowSizeChange` 导致尺寸不更新

### 排查提示
1. 把窗口从全屏切成分屏，画面是否形变——形变 = aspectRatio 没设
2. 画面是否被底部裁切——通常是 `objectFit` 不对或高度用了 100% + 父无 Scroll
3. 搜代码里的 `display.getDefaultDisplaySync()`，这是分屏 bug 高发接口

### 修复建议
- XComponent 交给框架按宽高比布局：

```ts
XComponent({ id: 'video', type: XComponentType.SURFACE, controller: this.ctl })
  .aspectRatio(9 / 16)    // 框架自动按父容器宽度算高度
```

- Video 显式 `Contain`：

```ts
Video({ src: $rawfile('v.mp4') })
  .width('100%').height('100%')
  .objectFit(ImageFit.Contain)
```

- 必须用数值尺寸时，订阅 `windowSizeChange` 同步 `@Local`（V1：`@State`），不用 `display.getDefaultDisplaySync()`

---

## 模式 9：横屏应用进入悬浮窗未声明适配，被强制竖向显示

### 典型症状
- 视频、游戏类应用从横屏进入悬浮窗后，画面被塞进竖向窗口显示不全
- 悬浮窗里页面方向与全屏方向不一致，旋转/比例不对
- 仅开了 `preferMultiWindowOrientation` 但没调 API，或仅调了 API 没改配置，效果不稳定

### 高发组件
播放页（`Video` / `XComponent`）、游戏画面、任何期望维持横向比例的沉浸式页面

### 底层机制
- 系统悬浮窗默认竖向。要支持横向悬浮窗，必须**配置 + API 双管齐下**：
  - `module.json5` 的 `abilities[].preferMultiWindowOrientation` = `"landscape"` 或 `"landscape_auto"`（声明能力）
  - 页面 `aboutToAppear` 调 `enableLandscapeMultiWindow()`；退出 `aboutToDisappear` 调 `disableLandscapeMultiWindow()`（动态启用）
- 两者缺一，系统可能回退到竖向悬浮窗

### 排查提示
1. 打开 `module.json5` 搜 `preferMultiWindowOrientation`，没有 → 就是此模式
2. 调了 `enableLandscapeMultiWindow()` 但效果仍不对，检查配置文件是否也改了
3. 页面退出没调 `disableLandscapeMultiWindow()` 会影响后续页面，记得成对

### 修复建议

`module.json5`：

```json
{
  "module": {
    "abilities": [{
      "name": "EntryAbility",
      "preferMultiWindowOrientation": "landscape_auto"
    }]
  }
}
```

页面：

```ts
@ComponentV2
export struct VideoPage {
  private win = (this.getUIContext().getHostContext() as common.UIAbilityContext)
    .windowStage.getMainWindowSync();

  aboutToAppear(): void {
    this.win.enableLandscapeMultiWindow();
  }
  aboutToDisappear(): void {
    this.win.disableLandscapeMultiWindow();
  }
}
```

> V1 等价：`@Component` → `@ComponentV2`。

配合模式 10（沉浸模式悬浮窗顶 bar 避让）一起处理，悬浮窗下顶部才不会挡住可点击区域。

---

## 模式 10：沉浸式应用在悬浮窗/分屏下，顶部系统控制条与应用内容区重合、按钮无法点击

### 典型症状
- 沉浸式视频/游戏应用进入悬浮窗后，悬浮窗顶部系统控制条（返回/最大化/关闭）盖住应用右上角按钮，点击事件被系统条吃掉
- 分屏后应用顶部按钮与分屏顶部控制条重叠

### 触发场景
- 应用 `setSpecificSystemBarEnabled('status', false)` 隐藏状态栏 + 窗口设为沉浸式
- 悬浮窗模式 (`WindowStatusType.FLOATING`) 或分屏模式下出现

### 底层机制
- 系统在悬浮窗/分屏下会注入自己的"顶 bar"，与 `TYPE_SYSTEM` 避让区以新的 `topRect.height` 上报
- 应用若在全屏下本来不需要避让，切到悬浮窗后没有响应 `windowStatusChange` / `avoidAreaChange`，内容就覆盖在系统条下

### 修复建议

```ts
@ComponentV2
struct ImmersivePage {
  @Local topSafeHeight: number = 0;

  aboutToAppear(): void {
    const win = (this.getUIContext().getHostContext() as common.UIAbilityContext)
      .windowStage.getMainWindowSync();
    const applyAvoid = (status: window.WindowStatusType) => {
      if (status === window.WindowStatusType.FLOATING) {
        this.topSafeHeight = this.getUIContext().px2vp(
          win.getWindowAvoidArea(window.AvoidAreaType.TYPE_SYSTEM).topRect.height);
      } else {
        this.topSafeHeight = 0;
      }
    };
    applyAvoid(win.getWindowStatus());
    win.on('windowStatusChange', applyAvoid);
  }

  build() { /* 顶部按钮区 .padding({ top: this.topSafeHeight }) */ }
}
```

> V1 等价：`@Component` → `@ComponentV2`、`@State` → `@Local`。

应用顶部操作区用 `.padding({ top: this.topSafeHeight })` 避让。**切忌只看全屏就写死 0**。

---

## 模式 11：应用子窗在主窗旋转后尺寸/位置错乱或被截断

### 典型症状
- 主窗从竖屏旋转到横屏，子窗还是原来的宽高和位置，超出屏幕被截断或位置诡异
- 悬浮框、引导气泡、自定义浮层（基于 `window.createSubWindow`）旋转后错位

### 触发场景
- 应用使用 `AUTO_ROTATION` / `AUTO_ROTATION_RESTRICTED` 等可旋转策略
- 子窗尺寸由应用显式 `resize()` 指定（非跟随主窗）

### 底层机制
- 主窗尺寸由系统控制、子窗尺寸由应用控制。主窗 `windowSizeChange` 不会自动推到子窗
- 旋转后若不手动交换子窗宽高并换算新坐标，子窗仍是旧矩形

### 修复建议

优先交给系统跟随：

```ts
subWindow.setFollowParentWindowLayoutEnabled(true);   // 一劳永逸
```

若必须自行控制，在主窗尺寸变化时重算：

```ts
mainWindow.on('windowSizeChange', () => {
  const r = subWindow.getWindowProperties().windowRect;
  // 旋转后宽高对调、位置按比例换算
  subWindow.resize(r.height, r.width);
  subWindow.moveWindowTo(r.top, r.left);
});
```

---

## 模式 12：180° 旋转 / 折叠开合后布局未更新（监听接口选错）

### 典型症状
- 设备从竖屏直接转到反向竖屏（180°），页面内挖孔位置没更新、状态栏避让没重算
- 折叠屏展开/折叠后，某些依赖 `avoidArea` 的组件不跟随刷新

### 触发场景
- 仅监听 `windowSizeChange`，但 180° 旋转窗口宽高不变——回调不触发
- 在 `windowRectChange` 回调里主动调 `getWindowAvoidArea()`——此时避让区可能尚未更新

### 底层机制
- `windowSizeChange` 仅在宽高数值变化时触发
- `display.on('change')` 能感知方向变化（即使尺寸不变）
- 避让区变化有独立事件 `avoidAreaChange`，挖孔 `TYPE_CUTOUT` 在旋转后位置会跑到左/右/下，必须单独订阅
- 华为官方规范："每种监听只处理该回调返回的数据"，不要跨回调主动查

### 修复建议

```ts
// 尺寸变化
win.on('windowSizeChange', onSize);
// 180° / 方向变化兜底
display.on('change', (id) => { /* 重新读方向 */ });
// 折叠状态
display.on('foldStatusChange', (fs) => {});
// 避让区（含挖孔）—— 每一类单独处理，不要在 windowRectChange 里查
win.on('avoidAreaChange', (data) => {
  switch (data.type) {
    case window.AvoidAreaType.TYPE_SYSTEM:               /* 顶/底系统栏 */ break;
    case window.AvoidAreaType.TYPE_CUTOUT:               /* 挖孔，旋转后位置会变 */ break;
    case window.AvoidAreaType.TYPE_NAVIGATION_INDICATOR: /* 底部小白条 */ break;
    case window.AvoidAreaType.TYPE_KEYBOARD:             /* 键盘，注意 height>0 判空 */ break;
    case window.AvoidAreaType.TYPE_SYSTEM_GESTURE:       /* 侧边手势区 */ break;
  }
});
```

对挖孔避让：页面要设计成"挖孔可能在上/下/左/右任一边"，用 `leftRect/topRect/rightRect/bottomRect.height/width` 全部读取再施加 padding。
