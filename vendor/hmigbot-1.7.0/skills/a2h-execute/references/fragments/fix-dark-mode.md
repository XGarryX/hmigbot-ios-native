# fix-dark-mode（深色模式修复）

适用 finding：症状涉及深浅色切换、颜色/图标/状态栏主题。只改白名单内文件。

## 症状 → 根因 → 修法

| 症状 | 根因 | 修法 |
|---|---|---|
| 两种模式颜色一样/黑上加黑 | 硬编码 Color.xxx / '#RRGGBB' / 0x / rgba | 改 `$r('sys.color.*')` 语义 token（font_primary / comp_background_primary / icon_primary / interactive_*）；品牌色进 base+dark 两份 color.json |
| 深色回退浅色值 | dark/ 缺同名资源或限定词错 | 补 `dark/element/color.json` 同名项；2in1 深色放 `2in1-dark/` 而非 `2in1/` |
| 资源名带 _dark/_night 后缀 | 绕过限定词匹配 | 迁到 `dark/media/icon.svg`，代码统一 `$r('app.media.icon')` |
| 首次正确、切换后不变 | 透传链丢 Resource 引用（RichEditor/渐变/foregroundColor） | onColorModeChange 里重赋 @Local 颜色变量触发刷新；升级 SDK |
| 图标深色下消失/发糊 | SVG 无 fillColor 或用 stroke | `.fillColor($r('sys.color.icon_primary'))`；SVG 改闭合 path+fill |
| HSP 深色失效、主包正常 | HSP 模块缺自己的 dark/ | 该模块内补 `src/main/resources/dark/`（主包 dark/ 覆盖不到） |
| 应用固定深色被系统切走 | 未走官方 API | `getApplicationContext().setColorMode(COLOR_MODE_DARK)` |
| 状态栏文字看不见 | 系统栏不随主题自动变 | 主题切换时重调 `setWindowSystemBarProperties({ statusBarContentColor, navigationBarContentColor })` |
| Canvas/Web/XComponent 不刷 | 自绘像素框架不管 | `mediaquery.matchMediaSync('(dark-mode: true)').on('change', ...)` 或 onColorModeChange 重绘；Web 注入 prefers-color-scheme CSS |
| Menu/Popup 与宿主主题不一致 | MenuOptions.colorMode 未设 | bindMenu 显式传 colorMode |

## 硬规则

- 禁止随主题变化的属性上出现字面颜色；一律资源引用。
- 资源匹配优先级：设备-dark → dark → 设备 → base，缺同名项回退 base。
- 透传链路必须保留 Resource 类型，禁止中途解析成 Color 数值。
- ColorMode：NOT_SET=-1（跟随系统）/ DARK=0 / LIGHT=1；多窗口下各 UI 实例独立读 `getContext(this).config.colorMode`。

<!-- source: arkts-dark-mode/SKILL.md:L153-L221; references/patterns.md:L7-L349 -->
