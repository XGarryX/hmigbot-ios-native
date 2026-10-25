---
name: arkts-dark-mode
description: ArkTS 深色模式场景下的根因定位与修复（V2 优先，兼容 V1）：硬编码颜色（#RRGGBB / 0x / Color.xxx）、主题资源未切换、resources/dark 目录缺失或路径错、状态栏/导航栏颜色错、图标/SVG/图片未变色、HSP/HAR 模块深色资源失效、ColorMode 切换后不刷新、Canvas/Web 未响应主题等。代码示例使用 ArkTS V2 装饰器（`@ComponentV2 / @Local / @ObservedV2 / @Trace / AppStorageV2.connect`），V1（`@Component / @State / @StorageLink`）写法仅作历史对照。
metadata:
  type: domain
  domain: ui
  tags:
  - dark-mode
  - theme
  - color-mode
  - resources
  - token
---
# arkts-dark-mode — ArkTS 深色模式排查技能

> HarmonyOS / ArkUI 语境下深色浅色主题切换的资源匹配与渲染刷新问题定位。

## 1. 何时启用

出现以下任一信号就应用本技能：

- 深色模式下某组件仍显示浅色底、黑字、发白图标或"看不见"
- 切换深浅色主题后页面颜色不变，杀进程重进才生效
- 图标 / SVG 在深色下不变色、描边发虚、对比度异常
- HSP / HAR 里的资源深色失效，主包正常
- 状态栏 / 导航栏前景色与内容主题不匹配
- 代码里写了 `Color.Black`、`'#000000'`、`'rgba(0,0,0,0.1)'` 这类字面颜色
- 应用想独立固定深色 / 浅色但被系统切换覆盖
- Canvas / XComponent / Web 自绘内容在主题切换后不刷新

## 2. 心智模型（先理解这些再看模式）

### 2.1 三种 ColorMode

```ts
import { ConfigurationConstant } from '@kit.AbilityKit';
// ConfigurationConstant.ColorMode
//   COLOR_MODE_NOT_SET = -1   // 跟随系统（默认）
//   COLOR_MODE_DARK    =  0
//   COLOR_MODE_LIGHT   =  1
```

- `NOT_SET` 含义是"跟随系统"。应用级可用 `getApplicationContext().setColorMode(...)` 固定一种；一旦应用主动设过，系统主题变更不再覆盖本应用。
- 组件级用 `@Entry` / `@ComponentV2`（V1：`@Component`）的 `onColorModeChange()` 回调感知切换。
- 读当前模式：`getContext(this).config.colorMode`。避免依赖全局单例状态，多窗口 / 多实例下每个 UI 实例各自感知。

### 2.2 语义色体系（token）

ArkUI 暗色适配的第一原则是**不写具体颜色值**，改引用系统 token：

- 文字：`$r('sys.color.font_primary' | 'font_secondary' | 'font_tertiary' | 'font_emphasize')`
- 图标：`$r('sys.color.icon_primary' | 'icon_secondary' | 'icon_on_primary')`
- 背景 / 组件：`$r('sys.color.comp_background_primary' | 'comp_background_secondary' | 'comp_foreground_primary' | 'comp_divider')`
- 交互态：`$r('sys.color.interactive_hover' | 'interactive_click' | 'interactive_focus')`、`$r('sys.color.ohos_id_color_click_effect')`
- 组件激活：`$r('sys.color.ohos_id_color_component_activated')`

系统会在 light / dark / 2in1-dark 等限定词目录下分别提供值，切换时自动刷新。

### 2.3 资源限定词目录

正确：

```
resources/
  base/element/color.json          # 浅色基线
  base/media/icon.svg
  dark/element/color.json          # 深色覆写（同 name 覆盖）
  dark/media/icon.svg              # 深色图标覆写
  2in1-dark/element/color.json     # 2in1 设备深色
```

错误：`base/media/icon_dark.svg`、`icon_night.png`（用文件名后缀区分主题）——这绕过限定词匹配，深色下不会命中。

### 2.4 HSP / HAR 的深色资源

每个 HSP / HAR 模块需独立提供 `src/main/resources/dark/` 目录，主包的 `dark/` 覆盖不到 HSP 内部资源。若出现"HSP 包深色失效、主包正常"，先查 HSP 模块自身是否有 `dark/` 目录，再考虑系统基线版本。

### 2.5 onColorModeChange 与 $r 的刷新机制

`$r('app.color.xx')` 在属性赋值时，框架保留 resource 引用，主题切换时根据该引用重新解析并刷新。若属性传参途中只保留了 `Color` 值而丢掉了 resource 引用（历史上 RichEditor、部分渐变/foregroundColor 在旧版本出现过），切换主题就不会刷新。典型表现：**首次进入页面颜色正确，切换后不变**。

### 2.6 窗口栏目主题

状态栏 / 导航栏**不跟随页面 ColorMode 自动变**，必须显式设置：

```ts
import window from '@ohos.window';
const win = await window.getLastWindow(getContext(this));
await win.setWindowSystemBarProperties({
  statusBarContentColor:     isDark ? '#FFFFFF' : '#000000',
  navigationBarContentColor: isDark ? '#FFFFFF' : '#000000',
});
```

主题切换时需要重新调一次。

### 2.7 mediaquery 订阅

纯 ArkTS 层可用 `mediaquery.matchMediaSync('(dark-mode: true)')` 订阅切换事件，用于驱动 Canvas、Web、XComponent 等**自绘内容重绘**——这些场景框架不会自动刷新。

## 3. 排查流程

### Step 1 · 读当前 ColorMode

```ts
import { common, ConfigurationConstant } from '@kit.AbilityKit';
const ctx = getContext(this) as common.UIAbilityContext;
console.log('colorMode', ctx.config.colorMode);   // 0 DARK / 1 LIGHT / -1 NOT_SET
```

### Step 2 · 切主题快速验证

系统设置里手动切；或调试时：

```ts
ctx.getApplicationContext().setColorMode(ConfigurationConstant.ColorMode.COLOR_MODE_DARK);
```

观察问题组件：

- **完全不刷新** → 资源引用在属性透传中丢失（模式 3），或自绘未订阅（模式 7）
- **刷新但色不对** → 资源目录缺 dark 副本 / 限定词错 / 硬编码（模式 1、2）

### Step 3 · 用 Inspector 看实际颜色

DevEco ArkUI Inspector 抓节点的 `color` / `backgroundColor` / `fillColor`：

- 值是具体 `#RRGGBB` 且两种模式下相同 → 代码里硬编码了
- 值是 `$r(...)` 但深色下拿到的仍是浅色色号 → 资源目录缺 dark 副本或限定词命名错

### Step 4 · 检查资源目录

```
resources/dark/element/color.json       # 深色覆写存在？
resources/dark/media/                   # 深色图标存在？
```

若用了 HSP：每个 HSP 模块都要独立提供 `dark/` 目录。

### Step 5 · 监听切换事件驱动自绘

Canvas / XComponent / Web / 自定义 drawable：

```ts
import mediaquery from '@ohos.mediaquery';

aboutToAppear() {
  this.listener = mediaquery.matchMediaSync('(dark-mode: true)');
  this.listener.on('change', (r) => this.repaint(r.matches));
}

// 或在 @ComponentV2（V1：@Component）中：
onColorModeChange(mode: ColorMode): void {
  this.repaint(mode === ColorMode.DARK);
}
```

## 4. 典型问题定位口诀

| 现象 | 优先怀疑 |
|---|---|
| 按压 / 悬浮态颜色两种模式下都一样 | 硬编码了 `'rgba(0,0,0,0.1)'` 之类字面值 |
| 整个页面深色下仍是浅色底 | 根布局 `.backgroundColor(Color.White)` 或 `'#FFFFFF'` |
| 图标深色下看不见或颜色错 | `Image` 没设 `.fillColor($r(...))`；或 SVG 用了 stroke 而非 fill |
| 切换主题后颜色不变、重进才对 | 属性透传中丢了 resource 引用（模式 3）/ 自绘未订阅切换 |
| HSP 组件深色失效、主包正常 | HSP 模块缺 `dark/` 目录，或系统基线版本偏旧 |
| 应用想固定深色却被系统切走 | 没走 `ApplicationContext.setColorMode` |
| 2in1 深色灰阶不对 | 深色资源放到 `2in1/element` 而非 `2in1-dark/element` |
| 资源名是 `icon_dark.svg` | 用文件名后缀区分主题，应迁移到 `dark/media/icon.svg` |
| 状态栏文字深色下看不见 | 没调 `setWindowSystemBarProperties` |
| Menu / Popup 颜色跟宿主不一致 | `MenuOptions.colorMode` 未显式设置 |
| Canvas / Web 切主题不刷 | 未订阅 `mediaquery('(dark-mode: true)')` 或 `onColorModeChange` |

## 5. 端到端修复流程

> 前置：通过 §3 排查流程已定位到 `references/patterns.md` 中某个错误模式。

### Step 1 · 找到代码位置

在 ArkTS 工程里按以下顺序搜：

- 找硬编码颜色：grep `Color\.`（如 `Color.White` / `Color.Black`）、`'#[0-9A-Fa-f]{3,8}'`、`0x[0-9A-Fa-f]{6,8}`、`'rgba?\(`
- 找属性键：grep `\.backgroundColor\(`、`\.fontColor\(`、`\.fillColor\(`、`\.borderColor\(`、`linearGradient`、`foregroundColor`
- 找资源目录：看 `resources/` 下是否存在 `dark/element/color.json` 与 `dark/media/`；按 `2in1-dark/`、`tablet-dark/` 等设备限定词目录
- 找命名误区：grep 文件名形如 `*_dark.*`、`*_night.*`、`icon_black.*`——这些是绕过限定词匹配的反模式
- 找切换感知：grep `onColorModeChange`、`mediaquery.matchMediaSync`、`getApplicationContext().setColorMode`、`config.colorMode`
- 找窗口栏：grep `setWindowSystemBarProperties`、`statusBarContentColor`、`navigationBarContentColor`
- HSP / HAR：在每个模块的 `src/main/resources/` 下确认 `dark/` 目录存在

### Step 2 · 对照错误模式的"错误写法"

翻到 `references/patterns.md`，典型错误特征：

- `.backgroundColor(Color.White)` / `.fontColor('#222222')` 等字面量直接写死
- 用 `'rgba(0,0,0,0.1)'` 表达按压 / 分割线，深浅色都一样
- `Image` / SVG 图标按 `_dark.svg` 后缀切换，绕开 `dark/media/` 限定词
- 自定义属性 / 渐变中途把 `Resource` 解析成 `Color` 数值再传，主题切换不刷新
- `Canvas` / `Web` / `XComponent` 自绘内容未订阅 `mediaquery('(dark-mode: true)')`
- 状态栏 / 导航栏前景色没有跟随 `colorMode` 调用 `setWindowSystemBarProperties`
- HSP 模块缺 `dark/` 目录，深色下回落到 base

### Step 3 · 改写为正确写法

按 patterns.md 修复建议替换。关键动作：

- 颜色统一改 `$r('sys.color.font_primary' | 'comp_background_primary' | 'icon_primary' | ...)` 等 token；按压 / 悬浮态用 `interactive_*` 系列
- 业务自定义颜色放进 `base/element/color.json` + `dark/element/color.json`，引用方写 `$r('app.color.xxx')`
- 图标走 `Image($r('app.media.xxx')).fillColor($r('sys.color.icon_primary'))`；SVG 用 fill 而非 stroke
- 在属性透传链路保留 `Resource` 类型，**不要**中途 `getColor()` 解出数值
- `Canvas` / `Web` / `XComponent`：`aboutToAppear` 里 `mediaquery.matchMediaSync('(dark-mode: true)').on('change', ...)` 触发重绘；或在 `@ComponentV2`（V1：`@Component`）内重写 `onColorModeChange`
- 状态栏：监听 `onColorModeChange` 后调 `setWindowSystemBarProperties`
- HSP / HAR：每个模块独立补 `src/main/resources/dark/`
- 若根因是框架旧版本 bug（如 RichEditor / 渐变属性丢 Resource 引用）：升级 SDK，或临时通过 `onColorModeChange` 强制重建组件

### Step 4 · 验证

- 控制中心切深色 → 浅色 → 跟随系统，每档复测
- 设置 → 显示 → 深色模式定时切换，覆盖到时间点切换路径
- 应用前后台切换时切系统主题，回前台看是否刷新
- HSP 涉及页面专门跑一遍
- 状态栏 / 导航栏前景色在两种模式下都清晰可读
- Canvas / Web / 自绘组件切主题后立即重绘

### Step 5 · 如果修完仍未解决

回到 §3 重新跑一遍；若仅在某些设备形态（2in1 / 折叠屏）下深色异常，叠加 `arkts-multi-device`；若深色下文本对比度 / 焦点框看不清，叠加 `arkts-accessibility`。

## 6. 参考

- `references/patterns.md`：ArkTS 深色模式 7 大错误模式（症状 → 机制 → 排查 → 修复）。
