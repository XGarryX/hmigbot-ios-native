---
name: arkts-large-font
description: ArkTS 大字体场景下的根因定位与修复（V2 优先，兼容 V1）：系统字体缩放（fontSizeScale 1.15 / 1.45 / 1.75 / 2.0 / 3.2x）下文本/布局/图标出现截断、溢出、重叠、位置错乱、SymbolGlyph 异常放大、浮层/菜单变小或越界、切换档位后不刷新等。若文本被 Ellipsis 截断但与字体档位无关，改用 arkts-text-truncation；若主要是读屏/焦点/热区等无障碍功能，改用 arkts-accessibility。
metadata:
  type: domain
  domain: ui
  tags:
  - large-font
  - font-scale
  - aging
  - accessibility
  - layout
---
# arkts-large-font — ArkTS 大字体/适老化排查技能

> HarmonyOS 设置 → 显示与亮度 → 字体大小/显示大小 被用户调大（尤其"适老化"档位）后，ArkUI 页面出现的截断、溢出、错位、图标失真、菜单变形等一系列缺陷的根因定位。

## 1. 何时启用

出现以下任一信号就应用本技能：

- 默认字体下一切正常，**把系统字体调到"大/超大/最大"档**就出 bug
- 描述中出现 "大字体 / 适老化 / fontScale / 字号放大 / 截断 / 溢出"
- 文本控件（Text / Button / Search / TextInput / Tabs）在放大后被裁切、挤压或换行异常
- 图标（SymbolGlyph / Chip 内 Icon / Swiper 数字指示器）异常变大
- 弹窗 / 浮层（Dialog / Picker / SelectOverlay / Popup / AutoFill）位置偏移、宽度越界、菜单变小
- 子窗口 / UIExtensionComponent / IsolatedComponent 中字体不跟随系统缩放
- 超大字体下输入框光标/选区柄跳跃异常

## 2. 心智模型

### 2.1 字体缩放档位

系统字体通过 `fontSizeScale`（= 显示层"字体大小"滑块 × "显示大小"）作用到所有 `fp` 单位文本。常见档位：

| 档位 | fontSizeScale | 说明 |
|---|---|---|
| 标准 | 1.0 | 默认 |
| 大 | 1.15 | 常用 |
| 更大 | 1.45 | 常用 |
| 最大 | 1.75 | 普通设置上限 |
| 适老化-大 | 2.0 | 进入"适老化模式"才可选 |
| 适老化-超大 | 3.2 | 设计约束最严苛档位 |

通常以 `1.75` 为"非适老化上限"，以 `2.0` 为"适老化入口阈值"。应用层分档计算 padding/height 时建议也用这两个阈值。

### 2.2 fp vs vp

- **fp**（font pixel）：文本专用，**会**跟随 `fontSizeScale` 放大
- **vp**（virtual pixel）：布局专用，**不**跟随字体缩放
- 坑 1：`SymbolGlyph` / `Image.fontSize(...)` 若不显式写单位，默认按 **fp** 解析，图标会跟着字号放大
- 坑 2：把系统资源 `$r('sys.float.Caption_L')`（fp 基）拿去做容器高度，容器跟着变高
- 坑 3：`$r` 资源若不显式指定单位，测量阶段可能被当作 fp，引起文字闪烁/测量异常

### 2.3 maxFontScale / minFontScale

ArkUI 文本类组件（`Text / Button / Search / TextInput / TextArea / Badge / SymbolGlyph / SubHeader` 等）提供：

```ts
.maxFontScale(2.0)   // 限制最大放大倍数
.minFontScale(1.0)   // 限制最小缩放（防止异常缩小）
```

没显式设置时，多数组件等于"无上限"，适老化 2.0~3.2 档会把布局撑爆。`Button` / `SegmentButton` / `Refresh` / Swiper 指示器 / `AlphabetIndexer` 等早期 API 版本未提供该属性，需升级 SDK 或自行用 `Text` 包裹并转发交互。

### 2.4 系统字体变更事件

系统字体档位变化时，UIAbility 会收到 `onConfigurationUpdate(config)` 回调，`config.fontSizeScale` 反映新档位。

**非**自动销毁重建的浮层（`CustomDialog` / `AlertDialog` / `Picker` / `CalendarPicker` / `DatePicker` / `SelectOverlay` / 自定义弹窗）在档位切换时框架不一定会刷新其内部测量 —— 需要应用层在 `onConfigurationUpdate` 里主动 `dismiss` 并重新打开。

### 2.5 初始化 vs 事件回调

适老化下的"页签变高、Padding 扩大、Margin 调整"必须在组件构建 / 首次布局阶段读取 `fontSizeScale` 后决定。放在 `onClick / onAreaChange` 事件里会导致**首次加载不生效、点一下才刷新**。典型写法：`aboutToAppear` 里读取 fontScale 存到 `@Local`（V1：`@State`），`build()` 用其分档。

### 2.6 浮层位置计算

`Popup / Menu / AutoFill 推荐框 / SelectOverlay / Dialog` 在大字体下内部文本变大 → 弹窗整体变大。自定义位置算法必须同时限制**左边界**和`offset.x + popupWidth ≤ windowRect.width - edge`。只 clamp 单边会在放大后越界。

### 2.7 SymbolGlyph 与图标

`SymbolGlyph` 本质是字体 glyph，天然按 fp 缩放。若图标不应跟随字体放大：

```ts
SymbolGlyph($r('sys.symbol.xxx'))
  .fontSize(24)                 // 纯数字 = vp，不随字号缩放
  .minFontScale(1.0).maxFontScale(1.0)
```

`ComposeListItem` 等高级组件内置图标尺寸也可能需要透传同样的 `minFontScale/maxFontScale` 限制。

### 2.8 子窗 / UIExtensionComponent / IsolatedComponent

子窗（`window.createSubWindow`）、`UIExtensionComponent`、`IsolatedComponent` 的容器和主窗独立，其 fontScale 不一定自动同步：

- 旧版本子窗创建后 `fontSizeScale` 停留在 1.0
- `IsolatedComponent` 历史上被误判为卡片，字号被限制 ≤ 1.3
- `UIExtensionComponent` 在主窗字体档位变更时可能不同步刷新

对策：应用层在主窗 `onConfigurationUpdate` 里主动销毁 + 重建子窗；或升级到已修复的 SDK 版本。

## 3. 排查流程

### Step 1 · 确认是不是字体缩放问题

```ts
import { UIContext } from '@kit.ArkUI';
import { common } from '@kit.AbilityKit';

// 页面 aboutToAppear 里读
const ctx: UIContext = this.getUIContext();
const abilityCtx = ctx.getHostContext() as common.UIAbilityContext;
const scale = abilityCtx?.config?.fontSizeScale ?? 1.0;
console.log('current fontSizeScale =', scale);
// 1.0 下正常、>= 1.45 就坏 → 基本可判定
```

并在 UIAbility 监听变更：

```ts
// EntryAbility
onConfigurationUpdate(newCfg: Configuration): void {
  console.log('fontSizeScale', newCfg.fontSizeScale);
}
```

### Step 2 · 用 Inspector 抓节点矩形

开启大字体后用 ArkUI Inspector 选中异常节点：

- 看节点 `rect` 是否超过父容器或 `windowRect`
- 看兄弟节点之间是否重叠
- 如果是浮层，看锚点坐标 vs 弹窗实际宽高

### Step 3 · 核对组件字体属性

在出问题的组件上，依次检查：

1. 有没有 `.maxFontScale(...)`？没有就是第一嫌疑
2. 有没有固定 `.height(xxx)`？大字体下文字撑不开就被截
3. 有没有用 fp 资源（如 `$r('sys.float.Caption_L')` / `Body_*` / `Subtitle_*`）做容器尺寸？
4. 是 `SymbolGlyph` / 图标吗？`fontSize` 有没有显式写单位？
5. 是自定义弹窗吗？`maxFontScale` 是否漏传到内部 `Text`？

### Step 4 · 针对浮层，手动触发字体档位切换

- 打开页面 → 弹出 Dialog / Picker → 不关弹窗切系统字体档位 → 看是否刷新
- 不刷新 → 应用层在 `onConfigurationUpdate` 里主动 `dismiss()` 并重新 `show()`（或通过 `AppStorageV2.connect(FontScaleModel, key, ...)` + `@Local` 实例驱动销毁重建；V1 等价：`AppStorage` + `@StorageLink` key）

### Step 5 · 针对自定义组件 / 子窗

- 自定义测量逻辑：打印读到的 `fontSizeScale`，确认尺寸按它分档
- 子窗 / `UIExtensionComponent`：在子窗页面里再打印一次 `fontSizeScale`，若与主窗不一致 → 命中同步缺失
- 横屏 + 大字体叠加：确认你的横屏分支没有"吞掉"适老化分支

## 4. 典型问题定位口诀

| 现象 | 优先怀疑 |
|---|---|
| 文本被放大到截断 / 溢出 | 缺 `.maxFontScale(...)`；或设了固定 `.height(...)` |
| 图标跟着文字变大（SymbolGlyph/Chip/ListItem） | `SymbolGlyph.fontSize` 无单位按 fp 解析；容器未 `.clip(true)` |
| 切字体档位后弹窗没变化 | 浮层未响应档位变化；需在 `onConfigurationUpdate` 主动重建 |
| 大字体下 Popup/Menu 右侧越界 | 位置算法只限左边界，未算 `offset.x + width ≤ windowRect.width` |
| 页面初始化没大字体效果、点一下才变 | 适老化分档逻辑错写在事件回调而非 `aboutToAppear`/`build` |
| 子窗 / UIExtensionComponent 字体不跟随 | 主窗档位未同步到子窗；监听 `onConfigurationUpdate` 重建子窗 |
| 菜单 / 安全控件点开反而变小 | 内部测量约束漏传 `maxFontScale` |
| 超大字体下光标乱跳、选区柄越界 | 框架测量 bug，限制 `.maxFontScale(2.0)` 规避进入 3.2 档 |
| 系统字体切换后 Canvas 显示乱码 | 未监听 `onConfigurationUpdate` 主动 `invalidate()` 重绘 |
| 大字体 + 横屏叠加才复现 | 横屏分支跳过了适老化分档；自定义 Dialog 未走适老化逻辑 |

## 5. 端到端修复流程

> 前置：通过 §3 排查流程已定位到 `references/patterns.md` 中某个错误模式。

### Step 1 · 找到代码位置

在 ArkTS 工程里按以下顺序搜：

- 全工程 grep `fontSize(`、`$r('sys.float.`（尤其 `Caption_*` / `Body_*` / `Subtitle_*`）、`fp` / `vp` 单位混用
- grep `.maxFontScale(`、`.minFontScale(`——看哪些文本组件**没**设
- grep `.height(` / `.constraintSize(`——看是否对文本/按钮/Tab 容器写死高度
- 找自定义弹窗：`@CustomDialog` / `CustomDialogController` / `bindSheet` / `bindMenu` / `bindContextMenu` / `Picker` / `AlertDialog`
- 找图标类：`SymbolGlyph(`、`Image(...).fontSize(`、`Chip(`、`SubHeader(`
- 找子窗 / 扩展：`createSubWindow`、`UIExtensionComponent`、`IsolatedComponent`
- 找配置回调：`onConfigurationUpdate(`——确认是否已存在并响应 `fontSizeScale`

### Step 2 · 对照错误模式的"错误写法"

翻到 `references/patterns.md` 里你匹配的模式，最常命中的错误特征：

- 文本/按钮缺 `.maxFontScale(...)`，适老化档位下被撑爆
- `SymbolGlyph` / `Image.fontSize` 不带单位，按 fp 解析跟着字号放大
- 用 `$r('sys.float.Caption_L')` 这类 fp 资源做容器 `.height(...)`，容器随字号长高
- `.height(56)` 写死的页签 / 标题栏，大字体下文字被裁
- 自定义弹窗在 `onConfigurationUpdate` 中未销毁重建，切档不刷新
- 适老化分档逻辑写在 `onClick` 而不是 `aboutToAppear`/`build`

### Step 3 · 改写为正确写法

按 patterns.md 修复建议替换。关键动作：

- 给所有受影响文本类组件加 `.maxFontScale(2.0).minFontScale(1.0)`（适老化以 2.0 为上限是常见取舍）
- 输入类组件 `TextInput / TextArea / Search` 务必锁 `.maxFontScale(2.0)`，避免超大档下光标/选区算错
- 把 `SymbolGlyph(...).fontSize(24)`（裸数字 = vp）+ `.minFontScale(1.0).maxFontScale(1.0)` 锁死图标
- 删掉文本容器的固定 `.height(...)`，改 `.constraintSize({ minHeight: ... })` 让内容撑
- 自定义浮层位置算法要**同时 clamp 左右 / 上下两边**：`offset.x ∈ [edge, windowRect.width - popupWidth - edge]`；只 clamp 单边在大字体放大后会越界
- 在 `EntryAbility.onConfigurationUpdate` 里把当前 `fontSizeScale` 写进 `AppStorageV2`（V1：`AppStorage`），弹窗 / 子窗用 `AppStorageV2.connect(FontScaleModel, ...)` 持有的 `@Local` 实例驱动重建（V1 等价：`@StorageLink`）
- 若根因是框架旧版本 bug（patterns.md 会标注，如超大档光标乱跳、`IsolatedComponent` 字号锁 1.3）：应用侧只能升级 SDK，或用 `.maxFontScale(2.0)` 把档位卡在 3.2 之前

### Step 4 · 验证

- 系统设置 → 显示与亮度 → 字体大小 / 显示大小，依次切到 1.0 / 1.45 / 1.75 / 2.0 / 3.2 五档，每档复跑出问题路径
- 进入"适老化模式"专门验 2.0 与 3.2 档
- 切档时**不关弹窗**，验自定义 Dialog / Picker / Menu 是否随档位刷新
- 横屏 + 大字体叠加测一次，确认横屏分支没吞掉适老化分支
- 子窗 / `UIExtensionComponent`：在子窗内打印 `fontSizeScale`，确认与主窗一致

### Step 5 · 如果修完仍未解决

回到 §3 排查流程从 Step 1 重新跑一遍；若现象更像是窗口尺寸 / 折叠 / 横竖屏导致，切换到 `arkts-multi-window` 或 `arkts-multi-device`；若是文本"装不下"被截断，切到 `arkts-text-truncation`。

## 6. 参考

- `references/patterns.md`：从大字体历史缺陷归纳的 7 类错误模式（症状 → 机制 → 排查 → 修复）
