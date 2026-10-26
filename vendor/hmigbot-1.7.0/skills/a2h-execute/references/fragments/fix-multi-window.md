# fix-multi-window（多窗口形态修复）

适用 finding：症状仅在分屏/自由窗口/悬浮窗/PiP/子窗形态下出现。跨设备断点/铰链归 fix-multi-device 段。只改白名单内文件。
<!-- GAP: 源 skill 无 PiP 专属错误模式，PiP 布局漂移暂按 FLOATING 行处理 -->

## 坐标事实

windowMode：2=FULLSCREEN / 3=PRIMARY（分屏主）/ 4=SECONDARY（分屏副）/ 5=FLOATING。自由窗口 = 边框≈2vp + 标题栏≈37vp + drawableRect；页面只能画 drawableRect。

## 症状 → 根因 → 修法（分屏/悬浮窗布局漂移）

| 症状 | 根因 | 修法 |
|---|---|---|
| 自由窗口浮层整体偏 ~37vp | 未扣边框+标题栏 | FLOATING 判定后补偿 vp2px(37+2)；定位用 `componentUtils.getRectangleById().windowOffset` |
| Toast/Menu 弹到主窗或屏幕角 | 子窗用了主窗 UIContext / 用屏幕尺寸 | 浮层 builder 一律 `this.getUIContext()`，禁闭包缓存；子窗 Toast 用 ToastShowMode.TOP_MOST |
| 拖窗后布局卡初始尺寸/Swiper 停中间帧 | 未订阅 windowSizeChange | 订阅并写 @Local 宽高；回调里 finishAnimation()、closeSelectionMenu()、关遗留浮层 |
| 分屏副窗顶部被状态栏盖 | 副窗避让漏判 | 显式 `.expandSafeArea([SafeAreaType.SYSTEM],[SafeAreaEdge.TOP])` |
| 窗口拖到屏下键盘高度为正 | 虚假 keyboardHeight 旧 bug | 自定义避让先判 `kbd > 0`；FLOATING 再扣 37+2vp |
| 分屏内容截断且滚不动 | 固定高度+非滚动容器 | 根容器包 Scroll；弹窗 `constraintSize({maxHeight:'80%'})` + 内容 `layoutWeight(1)` |
| 分屏视频拉伸/裁切 | surface 无比例约束 | XComponent `.aspectRatio(9/16)`；Video `.objectFit(ImageFit.Contain)`；禁 display 手算 |
| 横屏应用进悬浮窗被竖向 | 配置与 API 缺一 | module.json5 `preferMultiWindowOrientation:"landscape_auto"` + enable/disableLandscapeMultiWindow() 成对调用 |
| 悬浮窗顶部系统条盖住按钮 | 沉浸页未响应形态切换 | windowStatusChange 里 FLOATING 时取 TYPE_SYSTEM topRect.height 做顶部 padding，全屏时归 0 |
| GridRow 自由窗口断点偏大 | WindowSize 参照未扣边框 | 改 `reference: BreakpointsReference.ComponentSize` |
| 180° 旋转/折叠开合不刷新 | windowSizeChange 不触发 | `display.on('change')` 兜底；avoidArea 各类型只在 avoidAreaChange 里处理 |
| 主窗旋转后子窗错位截断 | 子窗尺寸应用自管 | `setFollowParentWindowLayoutEnabled(true)`；否则主窗 sizeChange 里 resize+moveWindowTo |

## 硬规则

- 禁止 display.getDefaultDisplaySync() 做布局/浮层定位。
- 禁止在 windowRectChange 回调里主动查 avoidArea；每种监听只处理自身回调数据。

<!-- source: arkts-multi-window/SKILL.md:L295-L361; references/patterns.md:L7-L704 -->
