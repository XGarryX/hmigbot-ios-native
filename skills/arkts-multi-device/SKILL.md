---
name: arkts-multi-device
description: ArkTS 跨设备与断点适配的根因定位与修复（V2 优先，兼容 V1）：布局/尺寸/间距在不同设备（手机/平板/2in1/折叠屏展开折叠/车机/TV）或断点（sm/md/lg/xl）下错位；硬编码 .width/.margin 导致大屏空白或小屏挤爆；Grid/List/WaterFlow 列数不随容器变化；折叠屏铰链区被挡；主副屏/外接显示器切换后白屏；RTL 语言左右镜像错乱。代码示例使用 ArkTS V2 装饰器（`@ComponentV2 / @Local / @ObservedV2 / @Trace / AppStorageV2.connect`），V1（`@Component / @State / @StorageProp`）写法仅作历史对照。若主要是窗口形态切换（分屏/自由窗口/悬浮窗）引发，改用 arkts-multi-window。
metadata:
  type: domain
  domain: ui
  tags:
  - multi-device
  - breakpoint
  - foldable
  - responsive
  - rtl
---
# arkts-multi-device — ArkTS 多设备适配排查技能

> HarmonyOS "一多"（一次开发、多端部署）语境下的布局与渲染适配。

## 1. 何时启用
出现以下任一信号就应用本技能：
- 布局在某一种设备/窗口形态下错乱，切换到另一种形态又好
- 看到 issue 描述里出现 "平板/折叠屏/自由窗口/大屏/横屏/2in1/副屏/断点"
- 代码里写死 `.width(360)` `.margin(16)` 这类固定 vp 数值
- 使用 `Grid/List/WaterFlow` 但 `columnsTemplate/lanes` 是字符串常量
- RTL 语言（阿拉伯/希伯来）下左右颠倒

## 2. 心智模型（理解这些之后再看模式）

### 2.1 断点系统
HarmonyOS 以**容器宽度**为基准划分断点，而非屏幕宽度：

| 断点 | 宽度范围 | 典型形态 |
|---|---|---|
| `xs` | 0 – 320vp | 手表 |
| `sm` | 320 – 600vp | 手机竖屏、折叠屏折叠态 |
| `md` | 600 – 840vp | 折叠屏展开态、小平板、手机横屏 |
| `lg` | 840 – 1440vp | 平板、2in1、车机 |
| `xl` | 1440vp+ | 大屏/TV |

`GridRow/GridCol` 原生支持断点；`Grid/List/WaterFlow` 从 API Level 12+（HarmonyOS 5.0+） 起支持 `ItemFillPolicy` 断点对象。

### 2.2 窗口形态
ArkTS `window.WindowMode` 五种取值（`getWindowProperties().windowMode`）：
- `UNDEFINED = 1`
- `FULLSCREEN = 2` — 全屏
- `PRIMARY   = 3` — 分屏主窗（手机/平板）
- `SECONDARY = 4` — 分屏副窗
- `FLOATING  = 5` — 自由窗口 / 悬浮窗（2in1/平板带边框与标题栏，宽度 ≠ 屏幕宽度）

此外还有：画中画（PiP，独立状态而非 `WindowMode` 枚举值）、UIExtension 子窗口（系统组件宿主，独立 UIContext）。

> 窗口形态切换相关 bug 属 `arkts-multi-window` 范畴，本 skill 聚焦不同尺寸/设备下的断点与方向适配。

关键：应用的可绘制区域 = `windowSize − (边框 + safeArea + statusBar)`。写死 `.width('100%')` 在自由窗口里会挤变形。

### 2.3 折叠屏
折叠屏除普通 display 旋转外，还有**铰链区（fold crease）**——这是一块物理不可绘制或显示扭曲的区域，通常位于屏幕中间。展开态下需要：
- 获取 `display.getFoldCreaseRegion()` 得到折痕矩形
- 浮层（Dialog/Popup/Sheet）需避让，正式的 AlertDialog/CustomDialog 已内置规避
- 旋转角计算要在 `display.rotation` 基础上叠加设备物理偏移（字段名因 SDK 版本而异，从 `display.getDefaultDisplaySync()` 上取），不能只用屏幕旋转

### 2.4 多屏 / 主副屏切换
- 用 `@ohos.window.getLastWindow()`、`getWindowProperties().displayId` 获取当前窗口所在的**逻辑屏 id**
- 再用 `display.getDisplayByIdSync(displayId)` 拿该屏尺寸/DPI/旋转
- 监听 `display.on('change')` 感知副屏插拔 / 主屏切换

## 3. 排查流程

遇到"某设备/形态下布局异常"，按顺序走：

**Step 1：确定当前形态**
```ts
import display from '@ohos.display';
import window from '@ohos.window';

// 读窗口属性
const win = await window.getLastWindow(getContext());
const props = win.getWindowProperties();
console.log('windowRect', JSON.stringify(props.windowRect));
console.log('windowMode', props.windowMode);          // 1=UNDEFINED 2=FULLSCREEN 3=PRIMARY 4=SECONDARY 5=FLOATING
console.log('drawableRect', JSON.stringify(props.drawableRect));

// 读显示属性
const disp = display.getDefaultDisplaySync();
console.log('width/height', disp.width, disp.height, 'rot', disp.rotation);

// 折叠屏状态
console.log('foldStatus', display.getFoldStatus());   // EXPANDED / FOLDED / HALF_FOLDED
console.log('crease', JSON.stringify(display.getFoldCreaseRegion()));
```

**Step 2：对比断点判断**
用 `@ohos.mediaquery` 或 `BreakpointSystem` 确认当前断点，比对出问题的断点是否和预期一致。

**Step 3：查组件参数**
- 看 `Grid/List/WaterFlow` 的 `columnsTemplate/lanes` 是不是写死
- 看 `Row/Column/Flex` 的 `.width/.height/.margin/.padding` 是不是固定 vp
- 看 Image / 图片资源是否提供了 `resources/phone / resources/tablet` 多目录

**Step 4：看浮层**
如果是 Dialog/Menu/Popup 在折叠/横屏异常，用 ArkUI Inspector 抓布局树，重点看：
- 浮层容器的 `offset/size` 是否超出 `windowRect`
- 折叠屏下浮层 Y 是否撞到 `foldCreaseRegion`

**Step 5：看方向/主屏切换**
- RTL 问题：搜代码里的 `left/right/start/end`，用 `I18n.System.isRTL()` 对齐
- 主副屏：监听 `display.on('change')` 后，你的 `@Local`（V1：`@State`）是否有过期的屏幕尺寸快照

## 4. 典型问题定位口诀

| 现象 | 优先怀疑 |
|---|---|
| 某尺寸下内容被压扁或空白 | `.width` 固定；缺 GridRow 断点 |
| 折叠屏展开后顶部/中部留白 | 没避让 foldCreaseRegion |
| 平板上字号/间距和手机一样 | 缺 sys token / 没做断点切换 |
| 自由窗口里超出边缘 | 用了 screen 宽度而非 windowRect |
| 阿拉伯语下布局左右反了 | 用了 `left/right` 而非 `start/end` |
| 副屏扩展后触摸位置偏 | 缓存了主屏坐标 / 用了过期的 displayId |
| 主副屏切换后白屏 | 未监听 `display.on('change')` 重建 |

## 5. 端到端修复流程

> 前置：通过 §3 排查流程已定位到 `references/patterns.md` 中某个错误模式。

### Step 1 · 找到代码位置

在 ArkTS 工程里按以下顺序搜：

- 找硬编码尺寸：grep `\.width\(\d`、`\.height\(\d`、`\.margin\(\d`、`\.padding\(\d`——这些是断点适配的头号嫌疑
- 找网格 / 列表常量列数：grep `columnsTemplate\(`、`rowsTemplate\(`、`lanes\(`——看是否字符串常量而非断点对象
- 找断点系统：grep `BreakpointSystem`、`mediaquery`、`GridRow`、`GridCol`、`currentBreakpoint`
- 找尺寸基准：grep `display.getDefaultDisplaySync`、`getWindowProperties`、`windowRect`、`drawableRect`——看用的是屏幕还是窗口
- 找折叠屏：grep `getFoldStatus`、`getFoldCreaseRegion`、`foldStatusChange`、`foldDisplayModeChange`
- 找方向：grep `\.left\(`、`\.right\(`、`Alignment.End`、`I18n.System.isRTL`——RTL 风险点
- 找资源分目录：看 `resources/` 下是否有 `phone` / `tablet` / `2in1` 等限定词目录

### Step 2 · 对照错误模式的"错误写法"

翻到 `references/patterns.md`，典型错误特征：

- 写死 `.width(360)` / `.margin(16)` 的根容器，平板 / PC 上空间利用率极差
- `Grid` / `WaterFlow` 用 `columnsTemplate('1fr 1fr')` 字符串常量，跨断点不变
- 用 `display.getDefaultDisplaySync().width` 计算应用宽度（在自由窗口下错得最离谱）
- 折叠屏展开未读 `foldCreaseRegion`，关键内容 / 浮层正好压在折痕上
- 用 `left/right` 而非 `start/end`，阿拉伯/希伯来语下镜像错乱
- 主副屏切换缺 `display.on('change')`，缓存的 displayId / 尺寸过期

### Step 3 · 改写为正确写法

按 patterns.md 修复建议替换。关键动作：

- 根布局换成 `GridRow` + `GridCol`，按 `xs/sm/md/lg/xl` 给 `span` / `offset`
- `Grid / List / WaterFlow` 改用 `ItemFillPolicy` 断点对象（API Level 12+（HarmonyOS 5.0+））；旧版本用 `mediaquery` 切 `columnsTemplate`
- 尺寸基准统一改 `getWindowProperties().windowRect`（或 `drawableRect`），不要用 `display.getDefaultDisplaySync()`
- 折叠屏展开态读 `getFoldCreaseRegion()`，关键浮层位置避开；自定义浮层手动避让 crease Y 区间
- RTL：用 `Alignment.Start/End`、`.direction(Direction.Auto)`、padding/margin 的 `start/end` 写法
- 主副屏：在 `display.on('change')` 回调里失效本地尺寸缓存，重新读 `windowRect`
- 若根因是设备硬件偏移（如 Pura X 折叠态系统覆盖应用方向）：应用侧只能升级 SDK 或不强行 `setPreferredOrientation`

### Step 4 · 验证

- 手机竖屏 → 手机横屏 → 折叠屏折叠态 → 折叠屏展开态 → 折叠屏半折（Half-Folded）
- 平板竖屏 → 平板横屏 → 平板自由窗口拖大拖小
- 2in1 PC 全屏 → 自由窗口；外接副屏拖窗
- RTL：系统语言切阿拉伯语，跑一遍主路径
- 切换主副屏：插拔外接屏 / 切折叠屏主副屏

### Step 5 · 如果修完仍未解决

回到 §3 重新跑一遍；若问题更像窗口形态切换瞬间的浮层 / 拖拽 / 键盘避让，切换到 `arkts-multi-window`；若是字体缩放挤爆布局，叠加 `arkts-large-font`。

## 6. 参考
- `references/patterns.md`：从 OpenHarmony 历史缺陷中归纳的 5 大错误模式（症状→机制→排查→规避）
