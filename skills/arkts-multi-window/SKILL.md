---
name: arkts-multi-window
description: ArkTS 窗口形态切换场景下的根因定位与修复（V2 优先，兼容 V1）：分屏（PRIMARY/SECONDARY）、自由窗口（FLOATING）、悬浮窗、画中画（PiP）、UIExtension 子窗口、系统子窗、窗口缩放/拖拽、模式切换（FULLSCREEN ↔ FLOATING ↔ SPLIT）下出现布局错位、Dialog/Menu/Toast/Sheet 位置漂移、键盘避让失败、拖拽/调整大小白屏、沉浸式/safeArea 异常、状态残留（选中高亮/菜单）等。代码示例使用 ArkTS V2 装饰器（`@ComponentV2 / @Local / @Param`），V1（`@Component / @State / @Prop`）写法仅作历史对照。跨设备/断点/折叠屏铰链改用 arkts-multi-device。
metadata:
  type: domain
  domain: ui
  tags:
  - multi-window
  - split-screen
  - floating
  - safe-area
  - pip
---
# arkts-multi-window — ArkTS 多窗口形态排查技能

> 同一台设备内部不同窗口形态（全屏 / 分屏 / 自由窗口 / 悬浮窗 / 画中画 / UIExtension 子窗口）下的布局、浮层、避让、拖拽问题。
> 关注的是「窗口形态切换」而非「屏幕尺寸分档」。

## 1. 何时启用

出现以下任一信号就应用本技能：

- 应用在**全屏正常**，进入**分屏 / 自由窗口 / 悬浮窗**后布局错位、被裁剪、Toast/Menu/Dialog 位置漂到屏幕外
- 拖拽窗口边缘**调整尺寸**时白屏、内容卡在动画中间、弹窗不跟随
- 自由窗口下出现**鼠标 hover 热区错位**、二级菜单进不去、点击位置偏移一段距离
- **键盘弹起**时弹窗或输入框上移过多/不足，自由窗口拖到屏幕底部以下后键盘高度异常
- **UIExtension 子窗口 / 系统子窗口 / 子模态**里的 Toast、Dialog 显示位置和主窗对不上
- 分屏下半屏（SPLIT_SECONDARY）顶部/底部被状态栏、导航栏、Web 内容遮挡
- 窗口模式切换（FULLSCREEN ↔ FLOATING ↔ SPLIT）后状态残留：选中高亮不消失、复制粘贴菜单不消失、光标不闪
- 多窗或自由窗口下 `visibleAreaChange` 等回调不触发

如果只是手机/平板/折叠屏的尺寸分档/断点/铰链问题——切换到 `arkts-multi-device`。

## 2. 心智模型

### 2.1 WindowMode / WindowStatusType 与"窗口矩形 ≠ 屏幕矩形"

**两套枚举要分清**（读日志/源码时不要混用）：

ArkTS 侧 `window.WindowMode`（`getWindowProperties().windowMode` 返回值）：
```
UNDEFINED = 1
FULLSCREEN = 2
PRIMARY   = 3   // 分屏主窗
SECONDARY = 4   // 分屏副窗
FLOATING  = 5   // 自由窗口 / 悬浮窗
```

ArkTS 侧 `window.WindowStatusType`（`getWindowStatus()` 返回、`windowStatusChange` 回调入参——运行态更细）：
```
UNDEFINED = 0
FULL_SCREEN = 1
MAXIMIZE   = 2
MINIMIZE   = 3
FLOATING   = 4
SPLIT_SCREEN = 5
```

可绘制区域分层（自由窗口最复杂）：

```
┌─ 物理 Display ────────────────────────┐
│ ┌─ Window (windowRect) ────────────┐ │
│ │ ┌─ 窗口边框 ───────────────────┐ │ │   约 2vp
│ │ │ ┌─ 标题栏 ─────────────────┐ │ │ │   约 37vp
│ │ │ ├─ 内容 padding ───────────┤ │ │ │
│ │ │ │ ┌─ drawableRect ───────┐ │ │ │ │   ← 你的 ArkTS 页面只能画这里
│ │ │ │ │   根组件 100%         │ │ │ │ │
│ │ │ │ └──────────────────────┘ │ │ │ │
│ │ │ └──────────────────────────┘ │ │ │
│ │ └──────────────────────────────┘ │ │
│ └──────────────────────────────────┘ │
└──────────────────────────────────────┘
```

- **`display.getDefaultDisplaySync()` 返回的是物理屏**——别用它做应用布局
- **`window.getWindowProperties().windowRect`** 是窗口在屏幕上的矩形（含边框/标题栏）
- **`drawableRect`** 才是真正可绘制内容区域；自由窗口下它比 `windowRect` 小一圈
- 子窗口（subWindow / systemTopMost / UIExtension）有自己的 `windowRect`，**不等于主窗 `windowRect`**

### 2.2 关键判定 API

| 判断 | 接口 | 用途 |
|---|---|---|
| 当前窗口模式 | `getWindowProperties().windowMode` | 判 FLOATING / FULLSCREEN / PRIMARY / SECONDARY |
| 当前运行形态 | `getWindowStatus()` → `WindowStatusType` | 进一步区分 MAXIMIZE / MINIMIZE / SPLIT_SCREEN / FLOATING |
| 是否系统级置顶子窗 | `ToastShowMode.SYSTEM_TOP_MOST`；子窗 `isTopmost` 属性 | Toast/Dialog 跨窗显示时要区分 |
| 当前组件所在 UIContext | `this.getUIContext()` / `this.getUIContext().getHostContext()` | 子窗 ≠ 主窗，闭包里不要捕获主窗 context |
| 是否自由窗口 | `getWindowProperties().windowMode === window.WindowMode.FLOATING` | 自由窗口要补偿边框、标题栏 |
| 窗口可绘制矩形 | `getWindowProperties().drawableRect` | 真正可画区域，比 `windowRect` 小（自由窗口下） |

### 2.3 浮层（Toast/Menu/Dialog/Popup/Sheet）的常见坑

浮层位置 = **目标节点屏幕坐标 − 当前窗口偏移**。错的写法基本是两类：

1. 用全屏宽高 `display.getDefaultDisplaySync().width` 来算 → 自由窗口里冲出窗口
2. 用主窗的 UIContext 去弹子窗里的 Menu / Dialog / Sheet → 坐标算到主窗去了

正确做法：浮层的 builder 或点击回调里，使用 `this.getUIContext()` 拿**当前组件所在窗口**的 UIContext，不要在子窗口里用 `AppStorage` / 闭包里缓存的主窗 UIContext。

### 2.4 避让（safeArea / avoidArea / 键盘）

速查：
- 状态栏/导航栏/挖孔/手势区/底部小白条/键盘——共 5 种类型，详见 §2.9
- 推荐用 `.expandSafeArea([SafeAreaType.SYSTEM, SafeAreaType.KEYBOARD], ...)` 声明式处理；只有自定义避让时才手动读 `getWindowAvoidArea`
- 自由窗口下键盘高度算法旧版本有 bug：窗口拖到屏幕底部以下时可能出现"虚假键盘高度"，自定义避让前先判 `keyboardHeight > 0`

### 2.5 窗口尺寸 / 形态变化的事件流

```
window.on('windowSizeChange', (size) => { /* 宽高变了 */ })
windowStage.on('windowStageEvent', (state) => { /* SHOWN/HIDDEN/ACTIVE/INACTIVE，注：此事件在 WindowStage 上，不在 Window 上 */ })
window.on('avoidAreaChange', (data) => { /* safeArea 变了 */ })
window.on('windowVisibilityChange', (visible) => {})
display.on('foldStatusChange', ...)  // 多设备技能负责
```

只要支持自由窗口/分屏，**必须**监听 `windowSizeChange`，否则页面会卡在初始尺寸。动画类组件（Swiper / 转场）在尺寸变化时要主动 `stopAnimation()`，不然会停在中间帧。

### 2.6 窗口模式 × 设备支持矩阵（华为官方）

| 设备 | 全屏 | 分屏 | 自由多窗 | 悬浮窗 |
|---|---|---|---|---|
| 手机 | 支持（默认） | 支持（上下 1:1/1:2/2:1、左右 1:1） | 不支持 | 支持 |
| 折叠屏 | 支持（默认） | 支持（折叠态同手机；双折展开/三折M 仅 1:1；三折G 按横竖判定） | 不支持 | 支持 |
| 平板 | 支持（默认） | 支持 | 支持（进入后强制横屏、DPI 调至最小） | 支持 |
| 2in1 PC | 支持 | 支持 | 支持（默认，`floating` = 自由多窗） | 支持 |

注：平板/PC 中 `supportWindowMode` 的 `floating` 语义依自由多窗开关：开启时为自由多窗，关闭时为悬浮窗。手机/折叠屏中 `floating` 仅代表悬浮窗。

### 2.7 关键 API 一览

| 主题 | 接口 / 字段 | 说明 |
|---|---|---|
| 声明支持模式 | `module.json5` → `abilities[].supportWindowMode: ["fullscreen","split","floating"]` | 静态声明；默认三种全开 |
| 动态修改支持模式 | `win.setSupportedWindowModes(modes)`（Window 实例方法，`win` 来自 `window.getLastWindow`） | 仅 2in1/tablet 自由多窗下生效 |
| 自由窗口尺寸限制 | `minWindowWidth/Height`、`maxWindowWidth/Height`、`minWindowRatio`、`maxWindowRatio`；`setWindowLimits()` | 超界系统强制调整 |
| 窗口类型 | `WindowType` | 区分系统窗口 / 应用主窗 / 应用子窗 |
| 窗口模式状态 | `WindowStatusType`：`FULL_SCREEN` / `SPLIT_SCREEN` / `FLOATING` / `MAXIMIZE` / `MINIMIZE` | 运行期窗口"当前形态" |
| 形态监听 | `window.on('windowStatusChange', cb)` | 模式切换瞬间窗口尺寸尚未刷新，需要尺寸用下一条 |
| 尺寸监听 | `window.on('windowSizeChange', cb)` | 窗口尺寸变化；180° 旋转不触发（用 `display.on('change')` 兜底） |
| 矩形变化 | `window.on('windowRectChange')` | 位置/宽高变化（折叠开合场景推荐） |
| 显示屏变化 | `window.on('displayIdChange')` | 窗口跨屏移动 |
| 避让区 | `window.getWindowAvoidArea(AvoidAreaType.X)` + `on('avoidAreaChange')` | 见 §2.8 |
| 折叠状态 | `display.on('foldStatusChange')` / `foldDisplayModeChange` | 物理折叠 / 显示模式变化 |
| 应用内分屏 | `startAbility(want, { windowMode: window.WindowMode.PRIMARY \| window.WindowMode.SECONDARY })` | 仅左右分屏；折叠/直板只能上下分屏不生效 |
| 窗口拖动 | `startMoving()` / `startMoving(offsetX, offsetY)` / `stopMoving()` / `moveWindowTo()` | 自定义标题栏用 `startMoving`（高性能、支持跨屏）；`moveWindowTo` 不跟手 |
| 拖拽缩放 | `setResizeByDragEnabled(enable)` | 不带标题栏子窗和悬浮窗不可热区拖拽 |
| 尺寸记忆 | `setWindowRectAutoSave(enabled, isSaveBySpecifiedFlag?)` | 仅 PC；`specified` 启动模式 + flag=true 才分实例记忆 |
| 最大化启动 | `module.json5` metadata `ohos.ability.window.isMaximize=true` | 需同时声明 `fullscreen+floating` |
| 横向悬浮窗 | `preferMultiWindowOrientation: "landscape"/"landscape_auto"` + `enableLandscapeMultiWindow()` / `disableLandscapeMultiWindow()` | 配置 + API 必须同时使用 |
| 子窗跟随主窗 | `setFollowParentWindowLayoutEnabled(true)` | 子窗旋转时无需自行 `resize+moveWindowTo` |

> 提示：官方强调"每种监听只处理该回调返回的数据"——不要在 `windowRectChange` 回调里再主动 `getWindowAvoidArea`，改用 `avoidAreaChange`。布局回调里也不要做 IO 等耗时逻辑。

### 2.8 旋转策略（window.Orientation 18 值）

**三大类 + 一种跟随桌面**：

| 分类 | 枚举 | 行为 |
|---|---|---|
| **固定**（初始方向，不可旋转） | `PORTRAIT` / `LANDSCAPE` / `PORTRAIT_INVERTED` / `LANDSCAPE_INVERTED` / `LOCKED` | `LOCKED` 跟屏幕当前方向锁定 |
| **自动-不受控制中心** | `AUTO_ROTATION` / `AUTO_ROTATION_PORTRAIT` / `AUTO_ROTATION_LANDSCAPE` | 传感器自由/仅竖/仅横 |
| **自动-受控制中心** | `AUTO_ROTATION_RESTRICTED` / `AUTO_ROTATION_PORTRAIT_RESTRICTED` / `AUTO_ROTATION_LANDSCAPE_RESTRICTED` / `AUTO_ROTATION_UNSPECIFIED`（4 向受系统判定） | 旋转锁定开关生效 |
| **带首选方向** | `USER_ROTATION_PORTRAIT` / `_LANDSCAPE` / `_PORTRAIT_INVERTED` / `_LANDSCAPE_INVERTED` | 调用瞬间临时转到指定方向，之后自动旋转 |
| **跟随桌面** | `FOLLOW_DESKTOP` | 推荐多设备统一方案 |

**三级配置 + 优先级**（数值大者覆盖小者）：

| 级别 | 配置处 | 作用域 | 版本 | 典型使用 |
|---|---|---|---|---|
| 应用级 | `module.json5` → `abilities[].orientation` | 应用启动方向、全应用默认 | 全版本 | 启动初始方向 |
| 窗口级 | `window.setPreferredOrientation(o)` | 整个 WindowStage（Router / Navigation 均生效） | API 9+ | 跨页面统一 |
| 页面级 | `NavDestination.preferredOrientation(o)` | 单页面（仅 Navigation） | API 19+ | 每页不同（推荐新版本） |

**互斥规则**：三级之间**后设置者覆盖前者**。窗口级设置后，页面跳转默认沿用上一页面策略；页面级仅在 Navigation 路由下生效，Router 路由不响应。页面级设置需要在 `aboutToAppear` 设、`aboutToDisappear` 恢复为上一页策略（用 `getPreferredOrientation()` 缓存）。

**子窗口 / 悬浮窗旋转特殊规则**：

- **子窗**：主窗尺寸由系统控制，子窗尺寸/位置由应用控制。主窗旋转后子窗不会自动适配，导致显示截断。对策：监听主窗 `windowSizeChange` → 对子窗 `resize(newW, newH)` + `moveWindowTo(newX, newY)`；或用 `setFollowParentWindowLayoutEnabled(true)` 交给系统。
- **悬浮窗**：系统默认竖向。横屏应用需 `preferMultiWindowOrientation: "landscape"/"landscape_auto"`（声明）+ `enableLandscapeMultiWindow()` / `disableLandscapeMultiWindow()`（动态启用），**两者缺一回退竖屏**。
- **系统优先级高于应用**：Pura X 折叠态等特定设备场景，系统会覆盖应用自定义策略。
- **180° 旋转**：窗口尺寸未变 → `windowSizeChange` 不触发，需 `display.on('change')` 兜底。

### 2.9 沉浸式与 avoidArea

**四套沉浸方案对比**：

| 方案 | 级别 | 效果 | 适用 | 坑 |
|---|---|---|---|---|
| 组件 `.background(color)` | 组件级 | 背景延伸至避让区、内容留在安全区 | 仅背景沉浸；滚动容器无效 | 内容无法延伸 |
| 组件 `.ignoreLayoutSafeArea() + .height(LayoutPolicy.matchParent)` | 组件级 | 背景 + 内容都延伸 | 需完全覆盖屏幕 | 内容易冲突避让区，需手动避让 |
| 组件 `.expandSafeArea([SafeAreaType], [SafeAreaEdge])` | 组件级 | 背景延伸、子组件仍布局在安全区 | 需指定延伸区域类型 | **必须紧贴安全区边界**；**不能设固定宽高**（百分比可）；**父为滚动容器时失效** |
| `setWindowLayoutFullScreen(true)` | 窗口级 | 所有页面全屏、不自动避让 | 全应用统一沉浸 | 所有页面都得自己算避让；通常配合 `setWindowSystemBarEnable` / `setWindowSystemBarProperties` |

**三个窗口级 API 职责划分**：

- `setWindowLayoutFullScreen(true/false)` — 布局能否越过状态栏/导航条（**布局权限**）
- `setWindowSystemBarEnable(['status','navigation'])` / `setSpecificSystemBarEnabled('status', bool)` — 系统栏**显隐**
- `setWindowSystemBarProperties({ statusBarColor, statusBarContentColor, navigationBarColor, ... })` — 系统栏**颜色/前景色**

**AvoidArea 5 种类型**：

| 类型 | 含义 | 典型用途 |
|---|---|---|
| `TYPE_SYSTEM` | 状态栏 + 底部导航条 | 顶/底 padding 避让 |
| `TYPE_CUTOUT` | 挖孔/刘海 | 旋转/折叠/悬浮窗下挖孔可能在上/下/左/右，均需动态响应 |
| `TYPE_SYSTEM_GESTURE` | 侧边返回手势区 | 避让手势冲突区域 |
| `TYPE_KEYBOARD` | 软键盘 | 键盘弹起后底部避让；自由窗口需额外扣边框+标题栏 |
| `TYPE_NAVIGATION_INDICATOR` | 底部小白条 | 与 `TYPE_SYSTEM` 分离处理 |

统一用 `window.on('avoidAreaChange', data => switch(data.type))` 分类型响应，不要在 `windowRectChange` 里主动查 avoidArea。

**自由窗口标题栏沉浸（PC、平板自由多窗、Mate XTs）**：

- `setWindowDecorVisible(false)` — 隐藏标题栏文字/图标，保留右上角三键
- `setWindowDecorHeight(h)` — 控制三键区显示高度
- `setDecorButtonStyle({colorMode, buttonSize, spacingBetweenButtons, closeButtonRightMargin, ...})` — 三键样式
- `getTitleButtonRect()` — 三键区位置/大小，供页面布局避让
- `on('windowTitleButtonRectChange', cb)` — 三键区尺寸变化监听（窗口三键在不同模式/DPI 下大小会变）
- 组件级沉浸方案（`background`/`ignoreLayoutSafeArea`/`expandSafeArea`）对自由窗口标题栏**不生效**，必须用上面这套窗口 API。

### 2.10 子窗 vs 主窗 context

- 子窗（`window.createSubWindow` / `ContextMenu` / `bindSheet` / `bindContextMenu` 等）有独立的 UIContext
- 把主窗的 UIContext 传给子窗用 → 弹窗位置算到主窗里去了
- 解决：组件回调里始终用 `this.getUIContext()`；不要在模块顶层或闭包里缓存 UIContext
- 系统级子窗（`ToastShowMode.SYSTEM_TOP_MOST` 或子窗 `isTopmost=true`）跨进程显示，偏移基准是屏幕而非宿主窗

## 3. 排查流程

### Step 1 · 复现并打印当前窗口形态

```ts
import window from '@ohos.window';
import display from '@ohos.display';

const win = await window.getLastWindow(getContext(this));
const p = win.getWindowProperties();
console.log('windowMode',  p.windowMode);          // 1=UNDEFINED 2=FULLSCREEN 3=PRIMARY 4=SECONDARY 5=FLOATING
console.log('windowRect',  JSON.stringify(p.windowRect));     // 含边框
console.log('drawableRect',JSON.stringify(p.drawableRect));   // 真实可画区
console.log('isLayoutFullScreen', p.isLayoutFullScreen);
console.log('displayId',   p.displayId);
const sysAvoid = win.getWindowAvoidArea(window.AvoidAreaType.TYPE_SYSTEM);
const kbdAvoid = win.getWindowAvoidArea(window.AvoidAreaType.TYPE_KEYBOARD);
console.log('safeArea sys', JSON.stringify(sysAvoid));
console.log('safeArea kbd', JSON.stringify(kbdAvoid));
```

把这些值贴在出问题的窗口里和正常窗口里各打一份，直接能看出"错的尺寸基准是谁"。

### Step 2 · 监听变化，确认是否响应

```ts
win.on('windowSizeChange', (size) => {
  console.log('size change', size.width, size.height);
});
win.on('avoidAreaChange', (data) => {
  console.log('avoid change', data.type, JSON.stringify(data.area));
});
```

如果出问题的现象是「拖大窗口后内容没跟上」「键盘弹起没反应」——首先确认这两个回调是否进入。没进入就是**根本没订阅**或订阅在错的 window 实例上。

### Step 3 · 浮层错位，用 Inspector 看坐标基准

ArkUI Inspector 抓出弹窗节点，记下它的 `frame`，与上面打印的 `windowRect` / `drawableRect` 对比：

- 浮层 `frame.x` 接近 `windowRect.left` 而非 0 → 用了屏幕绝对坐标
- 浮层 `frame.y` 比预期多了约 37vp → 没扣自由窗口标题栏
- 浮层 `frame.width` 等于屏宽而非窗宽 → 算的是屏幕尺寸不是窗口尺寸

### Step 4 · 判断是不是子窗 context 拿错

```ts
// 错：在 bindContextMenu / bindSheet 的 builder 里，
// 用了组件类外面闭包捕获的主窗 UIContext。
// 对：用当前组件的
const ctx = this.getUIContext();
const win = ctx.getHostContext();   // 子窗对应自己的 ability context
```

如果是自定义弹窗，确认你 `componentUtils.getRectangleById()` 拿到的 rect 来自子窗，而不是主窗的 root id。

### Step 5 · 状态残留问题：在 sizeChange 回调里清

窗口移动 / 模式切换时易残留：选中高亮、复制菜单、光标手柄、悬浮预览。
对策：在 `windowSizeChange` 里主动清理：

```ts
win.on('windowSizeChange', () => {
  this.controller?.closeSelectionMenu();   // TextInput/TextArea
  this.swiperController?.finishAnimation();
  PromptAction.closeToast?.();             // 若适用
  this.popupVisible = false;
});
```

## 4. 典型问题定位口诀

| 现象 | 优先怀疑 |
|---|---|
| 自由窗口里弹窗位置整体右下偏一段 | 没扣窗口边框（约 2vp）+ 标题栏（约 37vp） |
| 自由窗口里二级菜单 hover 进不去 | 鼠标坐标基于窗口外框，菜单热区基于内容区，差了标题栏高度 |
| Toast 在分屏/子窗里位置不对 | 用了主窗 UIContext；应在子窗组件里 `this.getUIContext()` |
| 分屏副窗（SECONDARY）顶部被状态栏盖住 | 没显式避让；加 `.expandSafeArea([SafeAreaType.SYSTEM], [SafeAreaEdge.TOP])` |
| 拖拽窗口尺寸后页面卡住、Swiper 停在中间 | 没监听 `windowSizeChange` / 未 `finishAnimation()` |
| 自由窗口拖到屏幕外，键盘高度变正数 | 框架旧 bug；自定义避让时先判 `keyboardHeight > 0` |
| 自由窗口移动后文本选中高亮/菜单不消失 | 窗口尺寸/位置变化时未清理选中态（`closeSelectionMenu()` 等） |
| 自由窗口下 GridRow 断点判断为大屏 | `Breakpoints.reference` 用 `WindowSize` 但未扣边框，改 `ComponentSize` 或升级 |
| 拖拽预览图飞到屏幕外/另一半屏 | 用了相对坐标当全局；要 `getPaintRectCenterToScreen − currentWindowOffset` |
| 多窗下 `visibleAreaChange` 不回调 | 旧版本框架 bug；升级 SDK，或用 `windowVisibilityChange` 兜底 |
| 半模态 `bindSheet` 在小窗口仍是中央样式 | 监听窗宽，宽度小于断点时切到 `SheetType.BOTTOM` |
| 子窗口里 Dialog 的遮罩没盖满 | 子窗浮层栈未刷新；窗口变化时主动 close 再 open |

## 5. 端到端修复流程

> 前置：通过 §3 排查流程已定位到 `references/patterns.md` 中某个错误模式。

### Step 1 · 找到代码位置

在 ArkTS 工程里按以下顺序搜：

- 找窗口监听：grep `windowSizeChange`、`windowStatusChange`、`windowRectChange`、`avoidAreaChange`、`displayIdChange`——确认订阅是否齐全
- 找浮层 builder：grep `bindContextMenu`、`bindMenu`、`bindSheet`、`bindPopup`、`CustomDialogController`、`promptAction.showToast`
- 找尺寸 / 坐标基准：grep `display.getDefaultDisplaySync`、`getDefaultDisplaySync().width`、`vp2px`、`px2vp`——这些常被错当作窗口尺寸
- 找窗口能力：grep `setWindowLayoutFullScreen`、`setWindowSystemBarEnable`、`setPreferredOrientation`、`setSupportedWindowModes`
- 找子窗 / 扩展：grep `createSubWindow`、`UIExtensionComponent`、`isTopmost`、`SYSTEM_TOP_MOST`
- 看 `module.json5` 的 `supportWindowMode` / `orientation` / `preferMultiWindowOrientation`
- 找闭包缓存的 UIContext：grep `getUIContext()` 是否被存在模块顶层 / 单例 / `AppStorage` 里

### Step 2 · 对照错误模式的"错误写法"

翻到 `references/patterns.md`，典型错误特征：

- 用 `display.getDefaultDisplaySync().width/height` 做应用布局或浮层定位（应用 `windowRect` / `drawableRect`）
- 自由窗口下浮层位置未扣窗口边框（约 2vp）+ 标题栏（约 37vp）
- 子窗 builder 里复用了主窗 UIContext，弹窗坐标算到主窗
- 缺少 `windowSizeChange` 订阅，拖拽尺寸后页面卡在初始尺寸 / Swiper 停在中间帧
- 自由窗口下键盘高度未判 `keyboardHeight > 0` 就避让，被旧版本"虚假键盘高度" bug 命中
- 窗口模式切换后未 `closeSelectionMenu()`、未关弹窗，状态残留

### Step 3 · 改写为正确写法

按 patterns.md 修复建议替换。关键动作：

- 应用布局/浮层一律基于 `getWindowProperties().windowRect`（外框）或 `drawableRect`（可绘制区）；自由窗口下用 `drawableRect`
- 浮层 builder 里始终 `this.getUIContext()`，禁止闭包缓存；子窗 Toast 显式 `ToastShowMode.SYSTEM_TOP_MOST` 或保持非系统级且在子窗 UIContext 内调用
- 在主窗 / 子窗各自的 `windowSizeChange` 回调里：`finishAnimation()`、`closeSelectionMenu()`、关闭遗留 Popup / Menu，必要时主动 `dismiss + show` 重建弹窗
- 沉浸 / 避让用 `.expandSafeArea([SafeAreaType.SYSTEM, SafeAreaType.KEYBOARD], [...])`；自由窗口标题栏沉浸只能走 `setWindowDecorVisible / setWindowDecorHeight / setDecorButtonStyle`
- 子窗旋转 / 主窗尺寸变化：`setFollowParentWindowLayoutEnabled(true)` 或 `resize + moveWindowTo`
- 若根因是框架旧版本 bug（如 `visibleAreaChange` 不回调、自由窗口虚假键盘高度）：升级 SDK，或加判空 / 用 `windowVisibilityChange` 兜底

### Step 4 · 验证

- 全屏 → 进入分屏（PRIMARY / SECONDARY 各测）→ 退回全屏
- 平板 / PC：拖拽到自由窗口，**沿四边各拉一次** + 拖到屏幕四角，期间弹出 Menu / Dialog / Sheet 看是否跟随
- 自由窗口下弹起软键盘，再把窗口拖到屏幕底部以下，看是否出现虚假键盘高度
- 窗口跨屏移动（外接显示器 / 折叠屏主副屏）
- 切窗口模式时不关弹窗，验状态残留
- 子窗 / `UIExtensionComponent` 里弹 Toast / Menu，确认坐标在子窗内

### Step 5 · 如果修完仍未解决

回到 §3 重新跑一遍；若问题更像跨设备断点 / 折叠屏铰链 / RTL，切换到 `arkts-multi-device`；若是大字体导致浮层撑破，叠加 `arkts-large-font`。

## 6. 参考

- `references/patterns.md`：从历史缺陷与华为官方 FAQ 归纳的多窗口错误模式（症状 → 机制 → 排查 → 修复）。
