# fix-multi-device（多设备/断点修复）

适用 finding：症状随设备形态（手机/平板/2in1/折叠屏/副屏）或断点变化。窗口形态切换（分屏/悬浮窗）归 fix-multi-window 段。只改白名单内文件。

## 断点事实

按容器宽度分档（非屏宽）：xs<320 / sm 320–600 / md 600–840 / lg 840–1440 / xl ≥1440vp。

## 症状 → 根因 → 修法

| 症状 | 根因 | 修法 |
|---|---|---|
| 大屏贴边留白、小屏挤爆 | 硬编码 .width/.margin/.padding | 间距走 `$r('sys.float.margin_level*')` / `padding_level*` token；根布局 GridRow+GridCol 按 `span:{sm,md,lg}` |
| Grid/List/WaterFlow 列数不随断点 | columnsTemplate/lanes 是字符串常量 | API12+ 用 `{ fillType: PresetFillType.BREAKPOINT_SM1MD2LG3 }`；旧版本 mediaquery 驱动切换 |
| 自由窗口内容超边界 | 用 display.getDefaultDisplaySync() 当应用宽度 | 改 `getWindowProperties().windowRect / drawableRect`，订阅 windowSizeChange |
| 折叠屏浮层压折痕被遮 | 未避让 foldCreaseRegion | 系统弹窗优先（已内置避让）；自定义浮层避开 `getFoldCreaseRegion().creaseRects` 的 Y 区间 |
| 折叠开合后布局不更新 | 依赖 aboutToAppear 尺寸快照 | `display.on('foldStatusChange')` 重算，禁用旧快照 |
| XComponent 展开后旋转错 90°/180° | 只用 display.rotation | 最终角 = (rotation×90 + 设备物理偏移) % 360，偏移取 getDefaultDisplaySync() 非标字段 |
| RTL 语言左右镜像错 | left/right 硬编码 LTR | 改 start/end、LocalizedMargin、`.direction(Direction.Auto)` |
| 拖入副屏 DPI 错/白屏 | 缓存过期 displayId/尺寸 | 从 `getWindowProperties().displayId` + `display.getDisplayByIdSync()` 现取；`display.on('change')` 回调里失效缓存 |
| 多实例（PC 多开）互相污染 | 模块级静态变量存布局态 | 改组件 @Local（跨层级 @Provider/@Consumer）；跨实例用 AppStorageV2.connect |

## 硬规则

- 禁止 display 物理屏尺寸做应用布局基准。
- 断点状态用 @ObservedV2 BreakpointModel + AppStorageV2.connect 全局共享，禁止各页面自行计算。
- 验证矩阵：手机竖/横 → 折叠态/展开态/半折 → 平板自由窗口拖拉 → RTL 语言 → 插拔副屏。

<!-- source: arkts-multi-device/SKILL.md:L103-L164; references/patterns.md:L7-L229 -->
