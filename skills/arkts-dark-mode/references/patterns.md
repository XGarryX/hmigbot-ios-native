# 深色模式 · 错误模式汇总

ArkTS 深色适配 7 类错误模式。每个模式：典型症状 / 高发组件 / 机制 / 排查 / 修复。

---

## 模式 1：硬编码颜色值，无法跟随主题

### 典型症状

- 按压 / 悬浮 / 获焦态背板颜色在深浅色下表现一致，或深色下出现"黑上加黑"看不清
- `TextInput` 取消按钮、`Toggle` / `Button` 背板在深色下明显不对
- 深色下出现纯黑 `#000000` 或纯白 `#FFFFFF` 的刺眼区域

### 高发组件

`TextInput` / `Search` / `Toggle` / `Button` / `Select` / `Radio`、自定义 `stateStyles`、自定义 `Dialog` 遮罩。

### 机制

代码里直接写 `Color.Black`、`'#66000000'`、`'rgba(0,0,0,0.1)'`、`0x99000000` 等字面颜色——这类值不经过资源系统，`ColorMode` 切换时没有任何替换链路可以生效。

### 排查

1. 代码全局搜：`Color.Black`、`Color.White`、`'#`、`0xFF`、`rgba(`
2. 搜 `.stateStyles({`、`.pressedColor`、`.focusColor` 后是否跟字面值
3. 用 Inspector 对比两种模式下节点实际颜色：两模式相同即硬编码

### 修复

优先使用系统语义 token；次选自有 `$r('app.color.xxx')` 并在 `dark/element/color.json` 提供覆写。

```ts
// 反模式：字面色 + 内联对象写 stateStyles（ArkTS 不支持对象字面量里直接写 .xxx 修饰符）
Button()
  .backgroundColor('#F0F0F0')
  // .stateStyles({ pressed: { ... } })  // 不合法语法

// 正模式：用 @Styles 函数 + sys.color 语义 token
@Styles function pressedDark() { .backgroundColor($r('sys.color.ohos_id_color_click_effect')) }

Button()
  .backgroundColor($r('sys.color.comp_background_tertiary'))
  .stateStyles({ pressed: pressedDark })
```

若必须用自定义品牌色，在 `resources/base/element/color.json` 与 `resources/dark/element/color.json` 同名各给一份。

---

## 模式 2：资源目录 / 限定词放错或缺失

### 典型症状

- 深色下某颜色或图标回退到了浅色值
- 2in1 深色下灰阶不对，手机深色正常
- 项目里有 `icon_dark.svg` / `bg_night.png` 这类后缀区分主题的资源，深色下不生效
- 弹窗遮罩在深色下透明度不对或完全没有

### 高发组件

`Image`、自定义 `Dialog` / `Menu` / `Radio` / `Toggle`，以及任何使用 `$r('sys.color.*')` 的组件。

### 机制

资源系统按**限定词目录**优先级匹配：`设备-dark → dark → 设备 → base`。找不到就 fallback 到 base。因此：

- `dark/element/color.json` 缺某 `name` → 深色下回退浅色值
- 把深色资源放到 `2in1/element` 而非 `2in1-dark/element` → 2in1 深色时命中浅色目录
- 用 `_dark` 文件名后缀区分 → 完全不走限定词机制
- 组件交互态（hover / focus / pressed）资源漏配 → 切到该状态时回退

### 排查

1. 查 `resources/dark/element/` 和 `resources/dark/media/` 是否存在
2. 在 `resources/` 下搜问题资源名，看 `dark/` 是否同名覆盖
3. 搜项目中 `_dark.svg` / `_night.` / `_light.` 后缀文件，全部是反模式
4. 多设备：`dark/`、`phone-dark/`、`tablet-dark/`、`2in1-dark/` 按需备齐

### 修复

标准结构：

```
resources/
  base/element/color.json       { "ohos_id_color_brand": "#317AF7" }
  base/media/icon.svg
  dark/element/color.json       { "ohos_id_color_brand": "#4F93F8" }
  dark/media/icon.svg
```

迁移 `icon_dark.svg` → `dark/media/icon.svg`，代码统一 `$r('app.media.icon')`。若系统 token 颜色不理想，可在 `dark/element/color.json` 中用相同 key 覆写。

---

## 模式 3：资源引用丢失，切换主题不刷新

### 典型症状

- 首次进入页面颜色正确，切换深浅色后颜色**不变**，杀进程重进才对
- `RichEditor.fontColor` / `.foregroundColor` / `.colorBlend` / 渐变色等属性上明明写的是 `$r('app.color.primary')`，却不跟主题走

### 高发组件

`RichEditor`、复杂属性路径的 `Text`、`linearGradient` / `sweepGradient` 渐变背景、`foregroundColor` / `colorBlend`、NDK 自定义节点。

### 机制

`$r('app.color.xx')` 解析时，框架保留 resource 引用；切换主题时靠该引用重新解析得到新色值。问题出在**属性透传链路**：若中间某层只把 resource 解析成 Color 数值而不再保留引用，切换时就没有刷新入口。旧版本框架在若干属性上有过此类 bug，新版本已陆续修复。

### 排查

1. 用 `setColorMode` 强制切换，观察问题属性是否刷新
2. 若不刷新，确认属性属不属于上述"高风险属性"
3. NDK 自绘：确认有无订阅 `OH_ArkUI_NodeEvent_ON_COLOR_CONFIGURATION_UPDATE` 并在回调里重建颜色

### 修复

- 升级系统 / SDK 基线（框架已在多版本修复）
- 应用侧绕行：在 `onColorModeChange` 或 `mediaquery` 回调里把 `@Local`（V1：`@State`）的颜色变量重新赋值，触发声明式刷新；不要指望 `.key()` 能强制重建（它仅用于测试标识）

```ts
@ComponentV2
struct ThemedText {
  @Local bgColor: ResourceColor = $r('sys.color.background_primary');
  @Local textColor: ResourceColor = $r('sys.color.font_primary');

  onColorModeChange(mode: number) {
    // 重新赋值触发刷新；Resource 对象切换主题时自身会解析为新值，
    // 但高风险属性（渐变、阴影、自绘 Canvas）需要手动"换一次值"才会刷
    this.bgColor = $r('sys.color.background_primary');
    this.textColor = $r('sys.color.font_primary');
  }

  build() {
    Text('hello')
      .backgroundColor(this.bgColor)
      .fontColor(this.textColor)
  }
}
```

> V1 等价：`@Component` → `@ComponentV2`、`@State` → `@Local`。
> 主题切换偏好若需全局/持久化共享，定义 `@ObservedV2 class ThemeModel { @Trace isDark: boolean = false }` 并通过 `AppStorageV2.connect(ThemeModel, 'theme', () => new ThemeModel())!` 替代 V1 `@StorageLink('theme')`。

如果仍不刷新，改用 `if (this.revision >= 0) { ... }` 条件渲染，或把该节点抽成子组件并在主题切换时用 `@Reusable` 重挂载。

NDK 场景：切换时重建相关颜色属性，不要缓存上次解析出的 ARGB 值。

---

## 模式 4：SVG / 图标未正确变色

### 典型症状

- 深色下菜单项、返回按钮、最大化按钮等图标"消失"或与背景糊在一起
- SVG 图标在深色下线条模糊、粗细不均
- 用了 `$r('sys.media.xxx')` 系统图标，浅色下正常，深色下还是黑的

### 高发组件

`Image`、`MenuItem` 的 icon、`Navigation` 返回按钮、自定义 TitleBar 图标。

### 机制

- SVG 变色依赖 `Image.fillColor()`。没设 `fillColor` 的自定义 SVG 在主题切换时不会自动变。
- 只有系统前缀的 SVG 才被框架默认允许变色；应用自定义 SVG 默认不变，必须显式 `.fillColor()`。
- SVG 若用 `stroke` 做轮廓，在变色或高 DPI 缩放下易粗细不均、粘连——规范是**用闭合 path + fill**。
- 自定义 `Navigation` 返回按钮若不是标准 `Image` 节点，框架的主题刷新逻辑可能识别不到。

### 排查

1. 深色下 Inspector 查 Image 节点，`fillColor` 是否为空
2. 打开 SVG 源文件，看是否用 `stroke=`；是则改为 `fill`
3. 自定义返回按钮是否用了标准 `Image`
4. 资源名是否含 `_dark` / `_light` 后缀

### 修复

```ts
// SVG 图标显式 fillColor 适配
Image($r('app.media.ic_home'))
  .fillColor($r('sys.color.icon_primary'))   // token 会随主题自动切
  .width(24).height(24)

// Navigation 返回按钮：用系统图标或标准 Image
Navigation()
  .title('Title')
  .titleMode(NavigationTitleMode.Mini)
  .backButtonIcon($r('sys.media.ohos_ic_back'))
```

SVG 设计规范：所有图形用 `<path fill="...">`，不要 `stroke`；若必须 stroke，设具体色而非继承。

---

## 模式 5：HSP / HAR 深色资源失效

### 典型症状

- 主包深色正常，HSP 动态共享包里的组件深色失效
- 多模块工程中，某个模块的深色图标 / 颜色始终命中浅色

### 高发组件

跨模块引用资源的所有组件；使用三方 HSP 的业务页面。

### 机制

每个 HSP / HAR 模块需独立提供 `src/main/resources/dark/` 目录，主包的 `dark/` 不会下沉覆盖 HSP 内部资源。旧系统基线在 HSP 资源查找上有已知 bug，新基线已修复。

### 排查

1. 确认问题只在 HSP 引用上出现
2. 打开该 HSP 模块源码，确认 `src/main/resources/dark/element/color.json` 和 `dark/media/` 真的存在、命名正确
3. 问题依旧：记录系统版本号，对照基线修复单

### 修复

- 在 HSP 模块**内部**补齐 `dark/` 限定词目录
- 升级系统基线到包含 HSP 深色资源修复的版本
- 低基线临时规避：在 `onColorModeChange` 里手动 `.backgroundColor(isDark ? colorA : colorB)` 显式分流，不依赖资源自动切换

---

## 模式 6：ColorMode 状态管理与切换时序

### 典型症状

- 应用想固定深色 / 浅色，但系统主题一变就被拽走
- 多窗口中一个窗口切了主题，另一个没同步
- `Menu` / `ContextMenu` / `Popup` / `Sheet` 颜色与宿主页面不一致，或该独立却被宿主拖着走

### 高发组件

`UIAbility` 级别的 ColorMode 设置、`Menu` / `ContextMenu` / `Popup` / `bindSheet`。

### 机制

- **应用级固定**：只有走 `ApplicationContext.setColorMode(...)` 才会让框架记住"应用主动设过"，后续系统配置变更不覆盖本应用。绕过此 API 自己切 state，会被系统 configuration 更新重置。
- **多窗口**：每个窗口 / UI 实例独立感知主题，取当前 `getContext(this).config.colorMode`，不要跨窗口共享主题状态。
- **Menu 独立 colorMode**：默认跟随宿主；若需要独立主题，显式在 `MenuOptions` 上传 `colorMode`。

### 排查

1. 应用级固定失效 → 打印 `ctx.config.colorMode`，并确认 `setColorMode` 确实有被调用
2. Menu / Popup 主题不对 → 看 `MenuOptions` 是否传了 `colorMode`
3. 多窗口状态不同步 → 用每个窗口自己的 UIContext / config 取值

### 修复

```ts
import { common, ConfigurationConstant } from '@kit.AbilityKit';

// 应用固定深色
const appCtx = getContext(this).getApplicationContext();
appCtx.setColorMode(ConfigurationConstant.ColorMode.COLOR_MODE_DARK);

// Menu 独立主题
Button('more')
  .bindMenu(this.MenuBuilder, {
    colorMode: ConfigurationConstant.ColorMode.COLOR_MODE_DARK
  })

// 每个窗口单独感知主题
@Entry @ComponentV2 struct Page {
  onColorModeChange(mode: ColorMode): void {
    this.refreshCanvas(mode === ColorMode.DARK);
  }

  refreshCanvas(isDark: boolean): void { /* ... */ }
}

// V1 等价：@Component → @ComponentV2
```

---

## 模式 7：自绘 / Canvas / Web / 状态栏不响应主题切换

### 典型症状

- `Canvas` 绘制的图表、`XComponent` 渲染画面切换主题后颜色不变
- `Web` 内部内容跟系统主题脱节
- 状态栏图标深色下看不见（白底白字）或浅色下看不见（黑底黑字）
- 自定义 Dialog 背景模糊色切换主题后不变

### 高发组件

`Canvas` / `XComponent` / `Web`、状态栏 / 导航栏、自定义 drawable。

### 机制

框架只会自动刷新声明式组件属性（`backgroundColor` / `fontColor` 等）的主题。**自绘 API 画出的像素**框架管不到，必须应用订阅主题变更事件并重绘。状态栏也是一次性设置：`setWindowSystemBarProperties` 不会随 ColorMode 自动更新，需要切换时重调。

### 排查

1. 问题组件是不是 `Canvas` / `XComponent` / `Web` 这类自绘
2. 全局搜 `mediaquery.matchMediaSync`、`onColorModeChange` —— 有无订阅
3. 状态栏问题：搜 `setWindowSystemBarProperties` 调用点，确认在主题切换时有重复调

### 修复

```ts
import mediaquery from '@ohos.mediaquery';
import window from '@ohos.window';

@ComponentV2
struct ChartPage {
  private listener?: mediaquery.MediaQueryListener;
  @Local isDark: boolean = false;

  aboutToAppear(): void {
    this.listener = mediaquery.matchMediaSync('(dark-mode: true)');
    this.listener.on('change', (r: mediaquery.MediaQueryResult) => {
      this.isDark = r.matches;
      this.repaintCanvas();
      this.syncSystemBar();
    });
  }

  aboutToDisappear(): void {
    this.listener?.off('change');
  }

  async syncSystemBar(): Promise<void> {
    const win = await window.getLastWindow(getContext(this));
    await win.setWindowSystemBarProperties({
      statusBarContentColor:     this.isDark ? '#FFFFFF' : '#000000',
      navigationBarContentColor: this.isDark ? '#FFFFFF' : '#000000',
    });
  }

  // 或使用组件回调
  onColorModeChange(mode: ColorMode): void {
    this.isDark = (mode === ColorMode.DARK);
    this.repaintCanvas();
  }

  repaintCanvas(): void { /* ... */ }
  build() { /* ... */ }
}
```

> V1 等价：`@Component` → `@ComponentV2`、`@State` → `@Local`。
> 若需要在多页面/多组件共享 `isDark`（避免每个页面各自订阅）：定义 `@ObservedV2 class ThemeModel { @Trace isDark: boolean = false }`，并用 `AppStorageV2.connect(ThemeModel, 'theme', () => new ThemeModel())!` 全局取实例（V1 等价于 `@StorageLink('isDark')`）。

`Web` 场景：注入 CSS `@media (prefers-color-scheme: dark)`，或在主题切换时 `runJavaScript` 把主题值传给页面。
