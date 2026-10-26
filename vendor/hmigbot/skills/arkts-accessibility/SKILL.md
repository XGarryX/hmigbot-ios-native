---
name: arkts-accessibility
description: ArkTS 无障碍/适老化场景下的根因定位与修复（V2 优先，兼容 V1）：焦点丢失或 tabIndex 顺序错乱、触达热区过小（< 48vp）、屏幕朗读标签缺失、对比度不足、选中/勾选状态未播报、装饰性元素被误读、XComponent/Web 内容读不到等。代码示例使用 ArkTS V2 装饰器（`@ComponentV2 / @Local / @Param + @Once / @Event`），V1（`@Component / @State / @Prop`）写法仅作历史对照。若主要是字体缩放撑破布局，改用 arkts-large-font。
metadata:
  type: domain
  domain: ui
  tags:
  - accessibility
  - a11y
  - screen-reader
  - focus
  - hit-area
---
# arkts-accessibility — ArkTS 无障碍排查技能

> 屏幕朗读 / 焦点管理 / 触达热区 / 语义标注 场景下的 UX 根因定位。
> 大字体导致的布局破坏请用 `arkts-large-font`，本技能聚焦语义、焦点、热区、读屏、状态同步。

## 1. 何时启用

出现以下任一信号就应用本技能：
- 开启屏幕朗读 / ScreenReader 后某控件不读、读错内容、只念出 "未标记按钮"
- 自定义组件（尤其 `XComponent`、`Web`、Canvas 自绘控件）读屏无法识别
- 无障碍焦点绿框丢失、不跟手、滑动后停留在旧位置，或超出组件边界
- 手指点得到文本却触发不了点击（触达热区过小）
- 组件选中/勾选状态（Tab、Chip、自定义 Option）读屏无法播报 "已选中 / 已勾选"
- 装饰性遮罩、占位图被读屏误读
- 用户反馈出现 "读屏"、"无障碍"、"盲人模式"、"焦点框" 等关键词

## 2. 心智模型

### 2.1 无障碍树与播报链路

ArkUI 渲染树之外还有一棵**无障碍树**，屏幕朗读等辅助服务从这棵树取节点信息。每个节点暴露以下可读字段：`text / checked / selected / componentType / focusable / hint / error`。

应用侧通过 ArkTS 属性**主动覆写**这些字段：

| 属性 | 作用 |
|---|---|
| `accessibilityText` | 读屏主文本，覆盖默认的文字聚合 |
| `accessibilityDescription` | 补充说明/操作提示 |
| `accessibilityLevel` | 是否参与播报 |
| `accessibilityChecked` | 勾选态（true/false） |
| `accessibilitySelected` | 选中态（true/false） |
| `accessibilityGroup` | 把子节点合并为一个播报单元 |
| `accessibilityRole` | 覆盖组件语义类型 |

没有显式设置时，框架会从 `Text` 子节点聚合文字；图标按钮、纯绘制组件、`XComponent` 默认读不到有用内容。

### 2.2 accessibilityLevel 的四档

- `"auto"`（默认）：有 text 就参与播报，无 text 跳过
- `"yes"`：强制参与，哪怕没有文字也会念出 "按钮"
- `"no"`：本节点不参与，但子节点仍参与
- `"no-hide-descendants"`：本节点和后代都不参与（装饰性元素、覆盖层遮罩必用）

### 2.3 三方渲染内容的无障碍桥接

`XComponent`（NDK 渲染）、`Web` 组件有自己的内部树，ArkUI 的声明式无障碍树覆盖不到它们：

- **`Web` 组件**：升级到内置无障碍桥接的 SDK 版本即可，应用侧通常无需改代码；若自定义 `WebController` 行为，需保证滚动/页面切换事件正常回传，以便读屏焦点框能跟随滚动
- **`XComponent`**：需通过 NDK 侧的 AccessibilityProvider 接口注册自绘节点；ArkTS 侧做不到，必须由底层渲染模块配合

应用侧能做的：包一层可访问容器，用 `accessibilityText` / `accessibilityDescription` 至少暴露出 "这里是地图" / "这里是游戏画面" 的整体语义。

### 2.4 UI 焦点 vs 无障碍焦点

**UI 焦点**（键盘/遥控器）与**无障碍焦点**（读屏绿框）是两套：

- UI 焦点：`.focusable(true)` / `.tabIndex(n)` / `.defaultFocus(true)` / `.groupDefaultFocus(true)` / `.focusOnTouch(true)`
- 无障碍焦点：由辅助服务推进，根据节点在无障碍树中的顺序自动遍历；应用侧无法直接控制绿框位置，只能保证节点被正确加入树、rect 准确

两者都依赖组件被正确地加入节点树且 `visibility != Hidden`。自定义容器需要屏蔽子节点时，用 `accessibilityLevel('no-hide-descendants')` 而不是仅靠 `visibility`。

### 2.5 热区（responseRegion / hitTestBehavior）

- 默认热区 = 组件自身 rect
- `.responseRegion(...)` 会**完全覆盖**默认热区；写死过小数值会造成 "看得到按钮但点不到"
- `.hitTestBehavior(HitTestMode.Block / Transparent / None / Default)` 决定点击穿透规则，浮层遮罩常需要 `Transparent` 让下层可点
- 交互元素最小视觉尺寸与最小热区均建议 ≥ `48vp × 48vp`（WCAG 2.5.5）

对于自定义的小图标按钮，加一层 padding 或 `constraintSize({ minWidth: 48, minHeight: 48 })` 比直接设 `responseRegion` 更稳。

### 2.6 无障碍事件回调

- `onAccessibilityHover((isHover, event) => {...})`：读屏手指悬停进入/离开某节点时触发，可用于自绘控件更新高亮
- `onAccessibilityFocus((isFocus) => {...})`：节点获得/失去无障碍焦点时触发

这些回调仅在读屏开启时才触发，不要把普通业务逻辑放进去。

### 2.7 手势与读屏共存

读屏开启后，系统会接管单击/双击/滑动手势，直接使用 `.onClick` 的按钮一般正常；但自绘长按、拖拽、自定义 `GestureGroup` 会与读屏冲突。推荐：

- 按钮统一实现 `GestureModifier` 接口（或使用高级组件库 `@ohos.arkui.advanced.*` 提供的 `ButtonGestureModifier`），通过 `.gestureModifier(...)` 挂载；它会在内部按无障碍事件路由重新派发，避免与读屏冲突。注：`ButtonGestureModifier` 不是 `@ohos.window` 里的公开 API，使用前先确认 import 路径
- 长按手势 `duration` 不要小于 500ms，避免与读屏双击/长按冲突
- 可拖拽列表项的长按阈值同样建议 ≥ 500ms

## 3. 排查流程

### Step 1 · 确认读屏是否开启

```ts
import accessibility from '@ohos.accessibility';

accessibility.isOpenAccessibility().then(v => console.log('a11y enabled', v));
```

若读屏未开但用户仍反馈问题，多半是 UI 焦点 / 触达热区问题，而非语义标注问题。

### Step 2 · dump 无障碍树

命令行：`hidumper -s AccessibilityMS` 可输出当前窗口无障碍元素。重点看可疑节点：
- `text` 是否为空，是否是内部变量名而非用户可读文案
- `componentType` 是否和真实语义一致（明明是按钮却是 "Image"）
- `checked / selected` 是否正确反映当前状态
- `accessibilityLevel` 是否误设为 `"no"`

### Step 3 · 检查 ArkTS 侧语义标注

```ts
// 图标按钮必须显式标注，否则只会念 "按钮" 或 "图片"
Image($r('app.media.ic_close'))
  .onClick(() => this.close())
  .accessibilityText(getContext(this).resourceManager.getStringByNameSync('close_button'))
  .accessibilityDescription('双击关闭服务面板')
  .accessibilityLevel('yes')

// 选中/勾选态
Text('深色').accessibilitySelected(this.isDark)
Row() { /* 自绘勾选框 */ }.accessibilityChecked(this.agree)

// 装饰性覆盖遮罩
Stack().accessibilityLevel('no-hide-descendants')
```

### Step 4 · 检查焦点与热区

- 搜代码里 `.responseRegion(`，确认没有把可点击区域写小
- 确认交互元素最小热区 ≥ `48vp × 48vp`
- 自定义弹窗/浮层是否用 `.defaultFocus(true)` 明确了焦点入口
- 自定义列表是否设置了 `.focusable(true)` 与合理的 `.tabIndex`

### Step 5 · 检查自定义手势

- 长按/拖拽手势 `duration` 是否过短（< 300ms）
- 自绘按钮是否用了 `ButtonGestureModifier` 或等价的复合手势封装
- 是否在 `onAccessibilityHover` / `onAccessibilityFocus` 里放了会阻塞的业务逻辑

## 4. 典型问题定位口诀

| 现象 | 优先怀疑 |
|---|---|
| 读屏只念 "按钮" 不念功能 | 缺 `accessibilityText`（图标类元素） |
| 读屏念出内部变量名 | `accessibilityText` 拼到了错误字段/未走 i18n 资源 |
| 自定义 Tab / Option 选中态播报错 | 缺 `accessibilitySelected` 或 `accessibilityChecked` |
| `XComponent / Web` 不响应读屏 | 三方渲染内容未桥接；用外层容器补整体 `accessibilityText` |
| 焦点绿框越过组件边界 | 组件自身 rect 不准（动画未结束时读取） |
| 装饰性遮罩被读屏念出来 | 缺 `accessibilityLevel('no-hide-descendants')` |
| 手指点不到按钮 | 热区过小；加 padding 或 `constraintSize({ minWidth: 48, minHeight: 48 })` |
| 浮层遮罩挡住下层点击 | `hitTestBehavior` 设置错误；装饰层应为 `Transparent` |
| 拖拽与读屏双指手势冲突 | 长按 `duration` 过短；用 `ButtonGestureModifier` |
| 自定义 Dialog 弹出后读屏仍停在下面 | 弹窗节点未设 `.defaultFocus(true)` |
| 动态刷新后读屏内容不变 | 绑定的是普通变量而非 `@Local`（V1：`@State`）；属性未随状态变化更新 |

## 5. 端到端修复流程

> 前置：通过 §3 排查流程已定位到 `references/patterns.md` 中某个错误模式。

### Step 1 · 找到代码位置

在 ArkTS 工程里按以下顺序搜：

- 找语义属性：grep `accessibilityText`、`accessibilityDescription`、`accessibilityLevel`、`accessibilityChecked`、`accessibilitySelected`、`accessibilityGroup`、`accessibilityRole`——看哪些组件**没有**
- 找仅图标按钮：grep `Image\(`、`SymbolGlyph\(` 后紧跟 `\.onClick\(` 的，往往缺 `accessibilityText`
- 找焦点：grep `\.focusable\(`、`\.tabIndex\(`、`\.defaultFocus\(`、`\.groupDefaultFocus\(`
- 找热区：grep `\.responseRegion\(`、`\.hitTestBehavior\(`；以及尺寸 `< 48vp` 的可点击区域
- 找自定义手势：grep `LongPressGesture`、`PanGesture`、`GestureGroup`、`gestureModifier`，看 `duration` 是否过短
- 找三方渲染：grep `XComponent\(`、`Web\(`——确认外层有可访问容器包裹
- 找事件回调：grep `onAccessibilityHover`、`onAccessibilityFocus`——确认未塞业务逻辑

### Step 2 · 对照错误模式的"错误写法"

翻到 `references/patterns.md`，典型错误特征：

- 仅图标按钮（`Image` / `SymbolGlyph` + `onClick`）无 `accessibilityText`，读屏只念 "按钮" / "图片"
- 自定义 Tab / Chip / Option 切换状态时未更新 `accessibilitySelected` / `accessibilityChecked`
- 装饰性遮罩 / 占位图未设 `accessibilityLevel('no-hide-descendants')`，读屏读出脏内容
- 小图标按钮直接 `.responseRegion(...)` 写小，或自身 rect < 48vp 未补 padding
- `XComponent` / `Web` 无外层语义包裹，整块区域读屏沉默
- 自定义长按 `duration < 300ms`，与读屏双击 / 长按手势冲突
- 弹窗弹出后未设 `.defaultFocus(true)`，读屏焦点仍停在底层

### Step 3 · 改写为正确写法

按 patterns.md 修复建议替换。关键动作：

- 仅图标按钮：补 `.accessibilityText($r('app.string.xxx')).accessibilityDescription(...).accessibilityLevel('yes')`
- 状态类组件：在 `@Local`（V1：`@State`）变化的同时同步 `accessibilitySelected(this.selected)` / `accessibilityChecked(this.checked)`
- 装饰层：`.accessibilityLevel('no-hide-descendants')`；浮层遮罩同时配 `.hitTestBehavior(HitTestMode.Transparent)` 让点击穿透到下层
- 小热区：加 padding 或 `.constraintSize({ minWidth: 48, minHeight: 48 })`，优于 `responseRegion`
- `XComponent` / `Web` 外层包一层容器并补整体 `accessibilityText`；`XComponent` 真正自绘内容需 NDK 侧 `AccessibilityProvider` 桥接（应用 ArkTS 侧无法绕过）
- 自定义手势 `duration` ≥ 500ms；用 `ButtonGestureModifier` 替换裸 `GestureGroup`
- 弹窗内首项加 `.defaultFocus(true)`；动态内容更新走 `@Local`（V1：`@State`）驱动以触发无障碍树刷新
- 若根因是框架旧版本 bug（如 `Web` 无障碍桥接缺失）：升级 SDK，或外层补整体语义作为兜底

### Step 4 · 验证

- 系统设置 → 辅助功能 → 屏幕朗读（华为读屏）开启
- 沿主路径单指上滑 / 下滑遍历每个焦点，确认顺序合理、没有读出装饰性内容
- 每个仅图标按钮：读屏念出的内容是否表达功能，而非"按钮 / 图片"
- 状态类组件切换后立即听是否播报 "已选中 / 已勾选"
- 关闭读屏，遥控器 / 外接键盘 Tab 遍历，确认 UI 焦点链路
- 用细手指 / 触控笔点 48vp 边缘控件，确认热区
- `hidumper -s AccessibilityMS` dump 一次树，对比修改前后

### Step 5 · 如果修完仍未解决

回到 §3 重新跑一遍；若问题源自字体缩放破坏布局，切换到 `arkts-large-font`；若是深色模式下对比度 / 焦点框不可见，叠加 `arkts-dark-mode`。

## 6. 参考

- `references/patterns.md`：6 大无障碍错误模式（症状 → 机制 → 排查 → 修复）
