# fix-accessibility（无障碍修复）

适用 finding：症状涉及读屏播报、焦点、触达热区、状态同步。只改白名单内文件。

## 症状 → 根因 → 修法

| 症状 | 根因 | 修法 |
|---|---|---|
| 读屏只念"按钮/图片" | 图标按钮缺 accessibilityText | 补 `.accessibilityText($r('app.string.xxx')).accessibilityLevel('yes')`，文案必须走 i18n 资源 |
| 选中/勾选态播报错 | 自绘控件状态未入无障碍树 | 补 `.accessibilitySelected(b)` / `.accessibilityChecked(b)`，绑定必须是 @Local（V1 @State） |
| 装饰图/分隔线/Loading 被念出 | 未屏蔽子树 | `.accessibilityLevel('no-hide-descendants')`；**纯装饰层**（不拦点击）加 `.hitTestBehavior(HitTestMode.Transparent)` 穿透。**模态遮罩不适用本行**：要吞点击用 `.onClick(() => {})`，禁 Block/Transparent（语义见 arkui-enums 四值表——v3 F-001 实证） |
| XComponent/Web 读屏沉默 | 三方渲染未桥接 | 外层容器补整体 `.accessibilityText(...)` + `.accessibilityGroup(true)` 兜底；真桥接须 NDK AccessibilityProvider 或升级 SDK |
| 按钮看得到点不中 | 热区 <48vp 或 responseRegion 写小 | 删小 responseRegion；加 padding 或 `.constraintSize({ minWidth: 48, minHeight: 48 })` |
| 弹窗弹出焦点停在下层 | 缺焦点入口 | 弹窗首选项 `.defaultFocus(true)`，容器 `.groupDefaultFocus(true)` |
| Tab 顺序乱/列表项无法聚焦 | focusable/tabIndex 缺失 | `.focusable(true).focusOnTouch(true)`；表单按语义序 `.tabIndex(n)` |
| 长按/拖拽读屏下失效 | duration <300ms 与读屏手势冲突 | `LongPressGesture({ duration: 500 })`；自绘按钮走 gestureModifier |
| 数据刷新读屏不更新 | 绑了普通变量 | 改绑 @Local/@Param（V1 @State/@Prop）；伪 Toast 改 promptAction.showToast |

## 硬规则

- 必须：交互元素视觉尺寸与热区均 ≥48vp×48vp（WCAG 2.5.5）。
- 禁止：onAccessibilityHover/onAccessibilityFocus 内放业务逻辑（仅读屏开启才触发）。
- accessibilityLevel 四档 auto/yes/no/no-hide-descendants：图标按钮用 yes，装饰层用 no-hide-descendants。
- 验证：`hidumper -s AccessibilityMS` dump 无障碍树，比对 text/checked/selected/componentType。

<!-- source: arkts-accessibility/SKILL.md:L145-L214; references/patterns.md:L7-L293 -->
