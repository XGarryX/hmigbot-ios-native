# Android-to-HarmonyOS UI Interaction Mapping Reference

<!-- TODO: Fill in the actual UI interaction mapping content -->
<!-- This reference maps Android UI interaction patterns to HarmonyOS ArkUI equivalents -->
<!-- Covers: onClick→.onClick(), onLongClick→LongPressGesture, swipe→SwipeGesture, TextWatcher→onChange, onScroll, Drag&Drop, animations, etc. -->




## 一、触摸事件映射

### 1.1 基础触摸事件

| Android 事件 | HarmonyOS 事件 | 映射说明 | 代码示例对比 |
|-------------|---------------|----------|-------------|
| `onTouchEvent(MotionEvent)` | `onTouch(event: TouchEvent)` | 直接映射 | Android: `view.onTouchEvent(event)`<br/>HarmonyOS: `Component().onTouch((event) => {})` |
| `onInterceptTouchEvent(MotionEvent)` | `onTouchIntercept(event: TouchEvent)` | 直接映射 | Android: `viewGroup.onInterceptTouchEvent(event)`<br/>HarmonyOS: `Container().onTouchIntercept((event) => {})` |
| `dispatchTouchEvent(MotionEvent)` | 事件分发机制 | 架构差异 | Android: 手动分发<br/>HarmonyOS: 自动分发 + 手势系统 |

### 1.2 MotionEvent 动作映射

| Android Action | HarmonyOS 触摸类型 | 映射说明 |
|---------------|-------------------|----------|
| `ACTION_DOWN` | `TouchType.Down` | 手指按下 |
| `ACTION_UP` | `TouchType.Up` | 手指抬起 |
| `ACTION_MOVE` | `TouchType.Move` | 手指移动 |
| `ACTION_CANCEL` | `TouchType.Cancel` | 事件取消 |
| `ACTION_POINTER_DOWN` | 多点触摸开始 | 新手指按下 |
| `ACTION_POINTER_UP` | 多点触摸结束 | 手指抬起 |
| `ACTION_OUTSIDE` | 触摸区域外 | 触摸在组件外 |

### 1.3 触摸事件属性映射（API 20/21）

| Android 属性 | HarmonyOS 属性 | 映射说明 |
|-------------|---------------|----------|
| `event.getX()` / `event.getY()` | `event.touches[0].x` / `event.touches[0].y` | 获取坐标 |
| `event.getRawX()` / `event.getRawY()` | `event.touches[0].screenX` / `event.touches[0].screenY` | 获取屏幕坐标 |
| `event.getPointerCount()` | `event.touches.length` | 触摸点数量 |
| `event.getPointerId(index)` | `event.touches[index].id` | 触摸点 ID |
| `event.getPressure()` | `event.touches[0].pressure` | 压力值 |
| `event.getSize()` | `event.touches[0].toolType` | 触摸工具类型 |
| `event.getEventTime()` | `event.timestamp` | 事件时间戳 |
| `event.getSource()` | 无直接对应 | 输入源判断需自定义 |

### 1.4 响应热区设置（API 20/21 新增）

| Android 功能 | HarmonyOS 功能 | 映射说明 | 代码示例 |
|-------------|---------------|----------|---------|
| `setTouchDelegate()` | `responseRegion` | 扩展响应热区 | `Component().responseRegion({ x: '10%', y: '10%', width: '80%', height: '80%' })` |
| 无直接对应 | `responseRegion` | 热区可配置多个区域 | 支持设置一个或多个热区范围 |
| 无直接对应 | `responseRegion` | 百分比偏移 | x/y 可设置正负值百分比 |

### 1.5 触摸测试控制（API 20/21 新增）

| Android 功能 | HarmonyOS 功能 | 映射说明 | 代码示例 |
|-------------|---------------|----------|---------|
| `requestDisallowInterceptTouchEvent()` | `hitTestBehavior` | 阻止拦截（静态配置） | `Component().hitTestBehavior(HitTestMode.None)` |
| `onInterceptTouchEvent()` | `onTouchIntercept()` | 事件拦截（动态回调） | `Container().onTouchIntercept((event) => { /* 返回 HitTestMode */ })` |
| 无直接对应 | `HitTestMode.Default` | 默认：自身命中会阻塞兄弟组件 | API 7+ |
| 无直接对应 | `HitTestMode.None` | 自身不接收事件，不阻塞 | API 7+ |
| 无直接对应 | `HitTestMode.Block` | 阻塞子组件的触摸测试 | API 7+ |
| 无直接对应 | `HitTestMode.Transparent` | 自身触摸测试，不阻塞 | API 7+ |
| 无直接对应 | `HitTestMode.BLOCK_HIERARCHY`（API 20 新增）| 自身和子节点响应，阻止祖先 | API 20+ |
| 无直接对应 | `HitTestMode.BLOCK_DESCENDANTS`（API 20 新增）| 自身不响应，后代也不响应 | API 20+ |

### 1.6 事件冒泡与阻止（API 20/21 增强）

| Android 机制 | HarmonyOS 机制 | 映射说明 | 代码示例对比 |
|-------------|---------------|----------|-------------|
| 无直接 API | `stopPropagation()` | 停止事件冒泡 | HarmonyOS: `event.stopPropagation()`（API 21+） |
| 无直接 API | 事件冒泡机制 | 默认冒泡到父组件 | 遵循右子树优先的后序遍历 |
| 手势和事件独立 | 手势事件冒泡不影响基础事件 | stopPropagation 只停止 Touch 事件，不影响手势 | 需要注意 |

---

## 二、点击事件映射

### 2.1 基础点击事件

| Android 事件 | HarmonyOS 事件 | 映射说明 | 代码示例对比 |
|-------------|---------------|----------|-------------|
| `OnClickListener.onClick(View)` | `onClick(() => {})` | 直接映射 | Android: `button.setOnClickListener { }`<br/>HarmonyOS: `Button().onClick(() => {})` |
| `OnLongClickListener.onLongClick(View)` | `onLongPress()` 手势 | 手势识别 | Android: `button.setOnLongClickListener { }`<br/>HarmonyOS: `Button().gesture(LongPressGesture().onAction(() => {}))` |
| `OnDoubleClickListener` | `TapGesture({count: 2})` | 手势识别 | Android: 自定义实现<br/>HarmonyOS: `Component().gesture(TapGesture({count: 2}).onAction(() => {}))` |
| `OnContextClickListener` | `BindContextMenu` | 上下文菜单 | Android: `view.setOnContextClickListener { }`<br/>HarmonyOS: `Component().bindContextMenu(this.menuBuilder)` |

---

## 三、手势识别映射

### 3.1 点击手势

| Android 手势 | HarmonyOS 手势 | 映射说明 | 参数映射 |
|-------------|---------------|----------|---------|
| `GestureDetector.OnSingleTapUpListener` | `TapGesture({count: 1})` | 单击 | count: 1 |
| `GestureDetector.OnDoubleTapListener` | `TapGesture({count: 2})` | 双击 | count: 2 |
| `GestureDetector.OnShowPressListener` | `TapGesture` + 延时 | 长按触发 | 需自定义延时 |
| 手指按下 | `TapGesture` onAction | 动作回调 | `onAction(() => {})` |

### 3.2 长按手势

| Android 手势 | HarmonyOS 手势 | 映射说明 | 代码示例 |
|-------------|---------------|----------|---------|
| `GestureDetector.OnLongPressListener` | `LongPressGesture` | 长按 | `Component().gesture(LongPressGesture().onAction(() => {}))` |
| `onLongPress(MotionEvent)` | `LongPressGesture` onAction | 长按动作 | `onAction(() => { /* 长按触发 */ })` |

### 3.3 拖动手势

| Android 手势 | HarmonyOS 手势 | 映射说明 | 参数映射 |
|-------------|---------------|----------|---------|
| `GestureDetector.OnScrollListener` | `PanGesture` | 滑动/拖动 | direction: PanDirection |
| `onScroll(MotionEvent e1, MotionEvent e2, float distanceX, float distanceY)` | `PanGesture` onAction | 滑动动作 | `onAction((event: GestureEvent) => { /* 处理滑动 */ })` |
| `onFling(MotionEvent e1, MotionEvent e2, float velocityX, float velocityY)` | `SwipeGesture` | 快速滑动 | 需要速度阈值判断 |

### 3.4 缩放手势

| Android 手势 | HarmonyOS 手势 | 映射说明 | 参数映射 |
|-------------|---------------|----------|---------|
| `ScaleGestureDetector.OnScaleGestureListener` | `PinchGesture` | 双指缩放 | 需配合手势系统 |
| `onScale(ScaleGestureDetector detector)` | `PinchGesture` onAction | 缩放动作 | `onAction((event: GestureEvent) => { /* 处理缩放 */ })` |
| `onScaleBegin(ScaleGestureDetector detector)` | `PinchGesture` onActionStart | 缩放开始 | `onActionStart(() => {})` |
| `onScaleEnd(ScaleGestureDetector detector)` | `PinchGesture` onActionEnd | 缩放结束 | `onActionEnd(() => {})` |

### 3.5 旋转手势

| Android 手势 | HarmonyOS 手势 | 映射说明 | 代码示例 |
|-------------|---------------|----------|---------|
| 无直接对应（需自定义） | `RotationGesture` | 双指旋转 | `Component().gesture(RotationGesture().onAction(() => {}))` |

### 3.6 手势组合与冲突处理

| Android 机制 | HarmonyOS 机制 | 映射说明 |
|-------------|---------------|----------|
| GestureDetector 组合 | `GestureGroup` | 手势组合识别 |
| 手势冲突处理 | `GestureMask` | 手势响应模式控制 |
| 事件拦截 onInterceptTouchEvent | `onTouchIntercept` | 触摸事件拦截 |

---

## 四、滑动与拖拽映射

### 4.1 滑动手势

| Android 事件 | HarmonyOS 手势 | 映射说明 | 代码示例 |
|-------------|---------------|----------|---------|
| `OnPageChangeListener` | `SwiperController` + onChange | 页面滑动 | `Swiper().onChange((index) => {})` |
| `OnScrollChangeListener` | `Scroll` onScroll | 滚动监听 | `Scroll().onScroll((xOffset, yOffset) => {})` |
| `RecyclerView.OnScrollListener` | `List` onScroll | 列表滚动 | `List().onScroll((scrollOffset, scrollState) => {})` |

### 4.2 拖拽功能

| Android 功能 | HarmonyOS 功能 | 映射说明 | 代码示例 |
|-------------|---------------|----------|---------|
| View.OnDragListener | `Drag` 装饰器 | 拖拽功能 | `Component().gesture(Drag())` |
| `onDrag(View v, DragEvent event)` | `Drag` onActionStart/onAction/onActionEnd | 拖拽事件 | `onActionStart(() => {})`<br/>`onAction((event) => {})`<br/>`onActionEnd(() => {})` |
| `startDragAndDrop()` | 无直接对应 | 系统拖拽 | 需自定义实现 |

### 4.3 滑动删除

| Android 功能 | HarmonyOS 功能 | 映射说明 | 代码示例 |
|-------------|---------------|----------|---------|
| ItemTouchHelper Swipe | `SwipeGesture` + 状态 | 滑动删除 | `ListItem().gesture(SwipeGesture().onAction(() => { /* 删除逻辑 */ }))` |

---

## 五、焦点事件映射

### 5.1 焦点获取与失去

| Android 事件 | HarmonyOS 事件 | 映射说明 | 代码示例对比 |
|-------------|---------------|----------|-------------|
| `OnFocusChangeListener.onFocusChange(View v, boolean hasFocus)` | `onFocus()` / `onBlur()` | 分离为两个事件 | Android: `view.onFocusChange { _, hasFocus -> }`<br/>HarmonyOS: `Component().onFocus(() => {}).onBlur(() => {})` |
| `setOnFocusChangeListener()` | `onFocus()` / `onBlur()` | 焦点变化监听 | `Component().onFocus(() => { /* 获得焦点 */ }).onBlur(() => { /* 失去焦点 */ })` |

### 5.2 焦点请求与管理

| Android 功能 | HarmonyOS 功能 | 映射说明 | 代码示例对比 |
|-------------|---------------|----------|-------------|
| `requestFocus()` | `focusControl.requestFocus()` | 请求焦点 | Android: `editText.requestFocus()`<br/>HarmonyOS: `focusControl.requestFocus(this.input)` |
| `clearFocus()` | `focusControl.requestFocus(null)` | 清除焦点 | Android: `editText.clearFocus()`<br/>HarmonyOS: `focusControl.requestFocus(null)` |
| `isFocused()` | 组件属性 `focused` | 检查焦点状态 | Android: `view.isFocused()`<br/>HarmonyOS: 组件内部状态判断 |
| `findFocus()` | `focusControl.requestFocus()` | 查找焦点组件 | 功能相似，API不同 |

### 5.3 焦点遍历

| Android 功能 | HarmonyOS 功能 | 映射说明 |
|-------------|---------------|----------|
| `FOCUS_DOWN` / `FOCUS_UP` / `FOCUS_LEFT` / `FOCUS_RIGHT` | 键盘方向键 | 方向键移动焦点 |
| `nextFocusDown` 等 XML 属性 | `focusable` 属性 | 焦点可获取性 |
| `FocusFinder.findNextFocus()` | 系统自动处理 | 下一个焦点查找 |

### 5.4 焦点触发方式

| Android 特性 | HarmonyOS 特性 | 映射说明 |
|-------------|---------------|----------|
| 触摸自动获取焦点 | 默认不自动 | HarmonyOS 需设置 `focusOnTouch` 属性 |
| Tab 键切换焦点 | Tab 键切换焦点 | 默认行为一致 |
| 方向键移动焦点 | 方向键移动焦点 | 默认行为一致 |

---

## 六、键盘事件映射

### 6.1 键盘输入事件

| Android 事件 | HarmonyOS 事件 | 映射说明 | 代码示例对比 |
|-------------|---------------|----------|-------------|
| `OnKeyListener.onKey(View v, int keyCode, KeyEvent event)` | `onKeyEvent(event: KeyEvent)` | 键盘事件 | Android: `view.setOnKeyListener { _, keyCode, _ -> }`<br/>HarmonyOS: `Component().onKeyEvent((event) => { /* 处理按键 */ })` |
| `dispatchKeyEvent(KeyEvent event)` | `onKeyEvent()` | 按键分发 | 功能类似 |

### 6.2 键盘操作映射

| Android 键值 | HarmonyOS 键值 | 映射说明 |
|-------------|---------------|----------|
| `KeyEvent.KEYCODE_ENTER` | `KeyCode.ENTER` | 回车键 |
| `KeyEvent.KEYCODE_BACK` | `KeyCode.ESCAPE` | 返回键 |
| `KeyEvent.KEYCODE_DEL` | `KeyCode.DELETE` | 删除键 |
| `KeyEvent.KEYCODE_TAB` | `KeyCode.TAB` | Tab 键 |
| `KeyEvent.KEYCODE_DPAD_UP/DOWN/LEFT/RIGHT` | 方向键 | 方向键 |

### 6.3 输入法相关

| Android 功能 | HarmonyOS 功能 | 映射说明 |
|-------------|---------------|----------|
| `InputMethodManager` | `InputMethod` | 输入法管理 |
| `showSoftInput()` / `hideSoftInput()` | `focusControl.requestFocus()` | 显示/隐藏键盘 |
| `IME_ACTION` 配置 | `enterKeyType` 属性 | 输入法操作类型 |

---

## 七、事件分发与拦截映射

### 7.1 事件分发机制（API 20/21）

| Android 机制 | HarmonyOS 机制 | 映射说明 | 架构差异 |
|-------------|---------------|----------|---------|
| `dispatchTouchEvent()` | 自动分发系统 | Android 手动分发 | HarmonyOS 自动处理 |
| `onInterceptTouchEvent()` | `onTouchIntercept()` | 事件拦截 | 功能类似，API不同 |
| 事件响应链机制 | 事件响应链机制 | 事件传播 | HarmonyOS 基于触摸测试构建响应链（API 20/21） |

### 7.2 事件冒泡与阻止（API 20/21）

| Android 机制 | HarmonyOS 机制 | 映射说明 | 代码示例对比 |
|-------------|---------------|----------|-------------|
| `requestDisallowInterceptTouchEvent(true)` | `onTouchIntercept` 返回 false | 阻止拦截 | Android: `parent.requestDisallowInterceptTouchEvent(true)`<br/>HarmonyOS: `Container().onTouchIntercept(() => false)` |
| `stopPropagation()` | `event.stopPropagation()` | 停止事件冒泡 | HarmonyOS: `event.stopPropagation()`（API 21+） |
| `return true` / `return false` | 事件消费 | 事件消费控制 | Android: `return true` 消费事件<br/>HarmonyOS: 绑定事件即消费 |

### 7.3 手势拦截增强（API 20 新增）

| Android 功能 | HarmonyOS 功能 | 映射说明 | 代码示例 |
|-------------|---------------|----------|---------|
| 无直接对应 | `onGestureRecognizerJudgeBegin()` | 手势判断拦截 | `Component().onGestureRecognizerJudgeBegin(() => { /* 拦截手势判断 */ })` |
| 无直接对应 | `parallelGesture()` | 并行手势绑定 | 支持系统手势和自定义手势并行处理 |
| 无直接对应 | `手势拦截` | 动态控制手势触发 | 从 API 20 开始支持手势拦截能力 |

### 7.4 事件响应链（API 20/21 核心特性）

| 概念 | Android | HarmonyOS | 说明 |
|-----|---------|-----------|------|
| 触摸测试 | 手动实现 | 自动基于坐标测试 | API 20/21 自动进行 |
| 响应链收集 | 递归遍历 | 右子树优先后序遍历 | 更高效的事件分发 |
| 事件分发 | dispatchTouchEvent | 自动分发系统 | 减少开发复杂度 |

### 7.3 触摸冲突处理

| Android 问题 | HarmonyOS 解决方案 | 映射说明 | 参考文档 |
|-------------|-------------------|----------|---------|
| 父子组件触摸事件冲突 | `onTouch` + `onClick` 冲突解决 | 多层级事件处理 | [多层级手势事件官方文档](https://developer.huawei.com/consumer/cn/doc/HarmonyOS-Guides/arkts-gesture-events-multi-level-gesture) |
| Button onClick 父组件 onTouch 冲突 | `stopPropagation()` 或配置 | 事件优先级处理 | [onTouch与onClick事件冲突 FAQ](https://developer.huawei.com/consumer/cn/doc/harmonyos-faqs/faqs-arkui-174) |

---

## 八、生命周期事件映射

### 8.1 组件生命周期

| Android 生命周期 | HarmonyOS 生命周期 | 映射说明 | 调用时机 |
|----------------|-------------------|----------|---------|
| `View.onAttachedToWindow()` | `aboutToAppear()` | 组件即将出现 | 组件挂载到 DOM 时 |
| `View.onDetachedFromWindow()` | `aboutToDisappear()` | 组件即将消失 | 组件从 DOM 卸载时 |
| `View.onVisibilityChanged()` | `visibility` 属性变化 | 可见性变化 | 组件显示/隐藏时 |

### 8.2 页面生命周期

| Android 生命周期 | HarmonyOS 生命周期 | 映射说明 | 调用时机 |
|----------------|-------------------|----------|---------|
| `Activity.onCreate()` | `UIAbility.onCreate()` | 创建 | 页面创建时 |
| `Activity.onStart()` | `UIAbility.onForeground()` | 前台 | 页面进入前台时 |
| `Activity.onResume()` | `UIAbility.onForeground()` 内部处理 | 可交互 | 页面可交互时 |
| `Activity.onPause()` | `UIAbility.onBackground()` | 后台 | 页面进入后台时 |
| `Activity.onStop()` | `UIAbility.onBackground()` | 停止 | 页面停止时 |
| `Activity.onDestroy()` | `UIAbility.onDestroy()` | 销毁 | 页面销毁时 |

### 8.3 页面显示与隐藏

| Android 事件 | HarmonyOS 事件 | 映射说明 | 代码示例 |
|-------------|---------------|----------|---------|
| `onWindowFocusChanged(boolean hasFocus)` | `onPageShow()` / `onPageHide()` | 窗口焦点变化 | `@Entry struct Page { onPageShow() { /* 页面显示 */ } onPageHide() { /* 页面隐藏 */ } }` |
| `onConfigurationChanged(Configuration newConfig)` | `onConfigurationUpdated(newConfig)` | 配置变化 | 配置（如屏幕方向）变化时调用 |

---

## 九、动画交互映射

### 9.1 属性动画

| Android 动画 | HarmonyOS 动画 | 映射说明 | 代码示例对比 |
|-------------|---------------|----------|-------------|
| `ObjectAnimator.ofFloat(view, "translationX", 0, 100)` | `animateTo({ duration: 1000 }, () => { this.x = 100 })` | 属性动画 | Android: `ObjectAnimator.ofFloat(view, "translationX", 0, 100).start()`<br/>HarmonyOS: `animateTo({ duration: 1000 }, () => { this.x = 100 })` |
| `ValueAnimator.ofFloat(0, 100)` | `animateTo()` | 值动画 | Android: `ValueAnimator.ofFloat(0, 100)`<br/>HarmonyOS: `animateTo({ duration: 1000 }, () => { this.value = 100 })` |
| `AnimatorSet` | 组合 `animateTo` 调用 | 动画集合 | Android: `AnimatorSet.playTogether(animator1, animator2)`<br/>HarmonyOS: `animateTo({ duration: 1000 }, () => { this.x = 100; this.y = 200; })` |

### 9.2 补间动画

| Android 动画 | HarmonyOS 动画 | 映射说明 | 代码示例对比 |
|-------------|---------------|----------|-------------|
| `TranslateAnimation` | `animateTo` + `translate` | 平移动画 | Android: `TranslateAnimation(0, 100, 0, 0)`<br/>HarmonyOS: `Component().translate({ x: this.x }).animation({ duration: 1000 })` |
| `ScaleAnimation` | `animateTo` + `scale` | 缩放动画 | Android: `ScaleAnimation(1, 1.5f, 1, 1.5f)`<br/>HarmonyOS: `Component().scale({ x: this.scale }).animation({ duration: 1000 })` |
| `RotateAnimation` | `animateTo` + `rotate` | 旋转动画 | Android: `RotateAnimation(0, 360)`<br/>HarmonyOS: `Component().rotate({ angle: this.angle }).animation({ duration: 1000 })` |
| `AlphaAnimation` | `animateTo` + `opacity` | 透明度动画 | Android: `AlphaAnimation(1, 0)`<br/>HarmonyOS: `Component().opacity(this.opacity).animation({ duration: 1000 })` |

### 9.3 转场动画

| Android 转场 | HarmonyOS 转场 | 映射说明 | 代码示例对比 |
|-------------|---------------|----------|-------------|
| `ActivityOptions.makeCustomAnimation()` | `pageTransition()` | 页面转场 | Android: `startActivity(intent, options.toBundle())`<br/>HarmonyOS（V2 推荐）: `@Entry @ComponentV2 struct Page { pageTransition() { PageTransitionEnter({ type: RouteType.None, duration: 1000 }).slide({ type: SlideEffect.Right }) } }`（V1 老项目把 `@ComponentV2` 改为 `@Component`） |
| `SharedElementCallback` | `sharedTransition()` | 共享元素转场 | Android: `ActivityOptions.makeSceneTransitionAnimation()`<br/>HarmonyOS: `Component().sharedTransition('id', { duration: 1000 })` |
| `Transition` | `transition` | 组件转场 | Android: `TransitionSet`<br/>HarmonyOS: `if (this.show) { Component().transition({ type: TransitionType.All, opacity: 0 }) }` |

### 9.4 动画监听器

| Android 监听器 | HarmonyOS 监听器 | 映射说明 | 代码示例对比 |
|-------------|---------------|----------|-------------|
| `Animator.AnimatorListener` | `AnimatorResult` 回调 | 动画生命周期 | Android: `animator.addListener(object: Animator.AnimatorListener { override fun onAnimationStart(animation: Animator) {} override fun onAnimationEnd(animation: Animator) {} })`<br/>HarmonyOS: `animateTo({ duration: 1000, onFinish: () => { /* 动画结束 */ } }, () => { /* 动画内容 */ })` |
| `ValueAnimator.AnimatorUpdateListener` | `AnimatorResult` 回调 | 动画更新 | Android: `valueAnimator.addUpdateListener { animation -> val value = animation.animatedValue as Float }`<br/>HarmonyOS: 状态自动更新，无需回调 |

### 9.5 动画控制

| Android 功能 | HarmonyOS 功能 | 映射说明 | 代码示例对比 |
|-------------|---------------|----------|-------------|
| `animator.start()` | `animateTo()` 自动执行 | 启动动画 | Android: `animator.start()`<br/>HarmonyOS: `animateTo({}, () => { /* 状态变化即启动 */ })` |
| `animator.cancel()` | `AnimatorResult.cancel()` | 取消动画 | Android: `animator.cancel()`<br/>HarmonyOS: `animatorResult.cancel()` |
| `animator.pause()` | 无直接对应 | 暂停动画 | HarmonyOS 需自定义实现 |
| `animator.resume()` | 无直接对应 | 恢复动画 | HarmonyOS 需自定义实现 |

---

## 十、拖放功能映射

### 10.1 拖拽系统

| Android 功能 | HarmonyOS 功能 | 映射说明 | 代码示例对比 |
|-------------|---------------|----------|-------------|
| `View.startDragAndDrop()` | `Drag` 装饰器 | 拖拽启动 | Android: `view.startDragAndDrop(clipData, myShadow, null, 0)`<br/>HarmonyOS: `Component().gesture(Drag())` |
| `OnDragListener` | `Drag` 回调 | 拖拽监听 | Android: `view.setOnDragListener { _, event -> when (event.action) { DragEvent.ACTION_DROP -> } }`<br/>HarmonyOS: `Component().gesture(Drag().onActionStart(() => {}).onAction((event) => {}).onActionEnd(() => {}))` |
| `DragEvent.ACTION_DRAG_STARTED` | `Drag` onActionStart | 拖拽开始 | `onActionStart(() => { /* 拖拽开始 */ })` |
| `DragEvent.ACTION_DRAG_LOCATION` | `Drag` onAction | 拖拽进行中 | `onAction((event: GestureEvent) => { /* 拖拽位置 */ })` |
| `DragEvent.ACTION_DROP` | `Drop` 装饰器 | 放置 | `Component().gesture(Drop().onDrop((event) => { /* 处理放置 */ }))` |

### 10.2 放置目标

| Android 功能 | HarmonyOS 功能 | 映射说明 | 代码示例 |
|-------------|---------------|----------|---------|
| `DragEvent.ACTION_DROP` | `Drop` onDrop | 放置目标 | `DropContainer().gesture(Drop().onDrop((event) => { /* 处理数据放置 */ }))` |
| `ClipData` 传递 | `Drop` event 参数 | 数据传递 | 通过 gesture event 传递数据 |

---

## 十一、无障碍功能映射

### 11.1 无障碍属性

| Android 属性 | HarmonyOS 属性 | 映射说明 | 代码示例对比 |
|-------------|---------------|----------|-------------|
| `setContentDescription(CharSequence)` | `accessibilityText` | 无障碍文本 | Android: `view.setContentDescription("描述文本")`<br/>HarmonyOS: `Component().accessibilityText("描述文本")` |
| `setImportantForAccessibility(int)` | `accessibilityLevel` | 无障碍重要性 | Android: `view.setImportantForAccessibility(View.IMPORTANT_FOR_ACCESSIBILITY_YES)`<br/>HarmonyOS: `Component().accessibilityLevel(AccessibilityLevel.AUTO)` |
| `setAccessibilityDelegate()` | 无直接对应 | 无障碍代理 | 需自定义实现 |
| `announceForAccessibility(CharSequence)` | 无直接对应 | 公告通知 | 需使用系统 API |

---

## 十二、未找到直接对应方案的 UI 交互功能（API 20/21 更新）

以下 Android UI 交互功能在 HarmonyOS ArkUI 中暂无直接对应功能：

| Android 功能 | HarmonyOS 替代方案 | 难度等级 | 说明 |
|-------------|-------------------|---------|------|
| **拖放系统** |  |  |  |
| `ClipData` 系统拖放 | 自定义拖拽 | 困难 | HarmonyOS 没有 ClipData 系统，需自定义数据传递 |
| `DragEvent.ACTION_DRAG_ENTERED/EXITED` | 自定义边界检测 | 中等 | 需手动判断拖拽进入/离开区域 |
| **高级焦点功能** |  |  |  |
| `FocusFinder` 查找算法 | `focusControl` API | 中等 | 系统自动处理，无手动查找需求 |
| `setOnFocusChangeListener` 的精确时机 | `onFocus` / `onBlur` | 简单 | 时机略有差异，需调整逻辑 |
| **触摸事件细节** |  |  |  |
| `MotionEvent.getToolType()` | `toolType` 属性 | 简单 | 部分支持，工具类型有限 |
| `MotionEvent.getAxisValue()` | 无直接对应 | 中等 | 手柄、滚轮等高级输入暂不支持 |
| `MotionEvent.getSource()` | 无直接对应 | 中等 | 输入源判断需自定义 |
| **手势冲突高级处理** |  |  |  |
| `onInterceptTouchEvent()` 嵌套拦截 | `onTouchIntercept` 级联 | 简单 | API 20/21 提供了更强大的拦截机制 |
| **动画高级功能** |  |  |  |
| `Animator.pause()` / `resume()` | 自定义状态管理 | 中等 | 需要手动控制动画状态 |
| `AnimatorListener.onAnimationRepeat()` | 自定义重复逻辑 | 中等 | HarmonyOS 无重复回调，需手动实现 |
| `LayoutTransition` | 自定义布局动画 | 困难 | 需要监听组件添加/删除 |
| `ViewPropertyAnimator` 组合 | 链式 `animateTo` | 简单 | 语法不同，功能类似 |
| **键盘事件细节** |  |  |  |
| `KeyEvent` 完整事件体系 | `KeyEvent` 简化版 | 中等 | HarmonyOS 键盘事件较为简化 |
| `dispatchKeyShortcutEvent()` | 无直接对应 | 中等 | 快捷键处理需自定义 |
| `onKeyLongPress()` | 自定义延时判断 | 简单 | 需要计时逻辑 |
| **多窗口交互** |  |  |  |
| `onMultiWindowModeChanged()` | 无直接对应 | 不可行 | HarmonyOS 无多窗口模式 |
| `onPictureInPictureModeChanged()` | 无直接对应 | 不可行 | HarmonyOS 无画中画模式 |

**注意**：API 20/21 已显著改进了事件处理能力，包括：
- 增强的 HitTestMode（BLOCK_HIERARCHY、BLOCK_DESCENDANTS）
- 手势拦截增强（onGestureRecognizerJudgeBegin）
- 事件响应链机制优化
- 响应热区 responseRegion 支持

---

## 十三、映射方案总结

### 13.1 完全直接映射的交互功能（40+）

可以直接一对一替换的交互功能：
- 基础触摸事件（onTouch）
- 点击事件（onClick）
- 焦点事件（onFocus/onBlur）
- 键盘事件（onKeyEvent）
- 基础手势（点击、长按）
- 动画 API（animateTo）

### 13.2 需要调整的交互功能（30+）

需要调整实现方式的交互功能：
- 手势识别（需使用手势系统而非监听器）
- 动画系统（声明式动画，状态驱动）
- 事件分发（自动分发 vs 手动分发）
- 生命周期（分离为多个回调）

### 13.3 需要自定义实现的交互功能（15+）

需要编写自定义逻辑或组件的交互功能：
- 系统拖放（需自定义数据传递）
- 高级焦点功能（系统自动处理）
- 动画暂停/恢复（需状态管理）
- 多窗口交互（架构不支持）

### 13.4 API 20/21 新增改进

API 20/21 带来了以下重要改进：
- **响应热区支持**：`responseRegion` 属性，可扩展组件响应范围
- **增强的触摸测试控制**：`HitTestMode.BLOCK_HIERARCHY`、`HitTestMode.BLOCK_DESCENDANTS`
- **手势拦截增强**：`onGestureRecognizerJudgeBegin()`、`parallelGesture()`
- **事件响应链优化**：更高效的事件分发机制
- **stopPropagation()**：更灵活的事件冒泡控制

---

## 十四、迁移建议

### 14.1 交互功能迁移优先级

1. **高优先级**（完全支持）：
   - 点击事件、长按事件
   - 基础手势（点击、长按、拖动）
   - 焦点事件、键盘事件
   - 基础动画

2. **中优先级**（部分支持）：
   - 复杂手势（缩放、旋转）
   - 事件分发与拦截
   - 转场动画
   - 无障碍功能

3. **低优先级**（暂不支持或困难）：
   - 系统拖放
   - 多窗口交互
   - 高级键盘事件
   - 动画暂停/恢复

### 14.2 交互功能迁移策略

1. **声明式思维转换**：
   - Android：命令式，监听器 + 回调
   - HarmonyOS：声明式，状态 + 绑定
   - 需要改变编程范式

2. **手势系统优先**：
   - 优先使用 HarmonyOS 手势系统（TapGesture、PanGesture 等）
   - 避免在 onTouch 中手动解析手势

3. **状态驱动动画**：
   - 动画通过状态变化触发
   - 使用 `@Local`（V2 推荐，API 12+）/ `@State`（V1 老项目）装饰器管理动画状态

4. **事件冒泡处理**：
   - 理解 HarmonyOS 事件冒泡机制
   - 合理使用 stopPropagation()

### 14.3 注意事项

1. **事件模型差异**：
   - Android：事件分发机制复杂
   - HarmonyOS：手势系统更简洁

2. **焦点处理方式**：
   - Android：复杂的焦点查找和管理
   - HarmonyOS：focusControl API 简化

3. **动画架构差异**：
   - Android：基于对象的动画系统
   - HarmonyOS：基于状态的声明式动画

4. **手势识别方式**：
   - Android：GestureDetector + 监听器
   - HarmonyOS：手势装饰器 + 回调

5. **测试重点**：
   - 多点触控场景
   - 手势冲突处理
   - 性能优化（避免过度重绘）

---

## 参考链接

### Android 官方文档
1. **[处理多点触控手势 | Android Developers](https://developer.android.com/develop/ui/views/touch-and-input/gestures/multi?hl=zh-cn)**
2. **[检测常用手势 | Android Developers](https://developer.android.com/develop/ui/views/touch-and-input/gestures/detector?hl=zh-cn)**
3. **[了解手势 | Jetpack Compose](https://android-docs.cn/develop/ui/compose/touch-input/pointer-input/understand-gestures)**
4. **[ViewGroup中管理触摸事件 | Android Developers](https://developer.android.com/develop/ui/views/touch-and-input/gestures/viewgroup?hl=zh-cn)**
5. **[属性动画概览 | Android Developers](https://developer.android.com/develop/ui/views/animations/prop-animation?hl=zh-cn)**
6. **[Android 触摸手势基础官方文档概览](https://www.cnblogs.com/mengdd/p/3335508.html)**
7. **[Android 手势识别类 GestureDetector 基本介绍](https://developer.aliyun.com/article/569712)**

### HarmonyOS 官方文档
1. **[多层级手势事件官方文档](https://developer.huawei.com/consumer/cn/doc/HarmonyOS-Guides/arkts-gesture-events-multi-level-gesture)**
2. **[焦点事件](https://developer.huawei.com/consumer/cn/doc/harmonyos-references/ts-universal-focus-event)**
3. **[焦点处理指南](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-common-events-focus-event)**
4. **[转场动画](https://developer.huawei.com/consumer/cn/doc/HarmonyOS-Guides/arkts-animation-transition)**
5. **[显式动画(animateTo)](https://developer.huawei.com/consumer/cn/doc/harmonyos-references/ts-explicit-animation)**
6. **[焦点事件onBlur/onFocus回调无法触发](https://developer.huawei.com/consumer/cn/doc/harmonyos-faqs/faqs-arkui-165)**
7. **[onTouch与onClick事件冲突 FAQ](https://developer.huawei.com/consumer/cn/doc/harmonyos-faqs/faqs-arkui-174)**

### 技术博客与实战文章
1. **[ArkUI交互事件与手势处理全解析](https://blog.csdn.net/2301_79624024/article/details/147620496)** - HarmonyOS 手势处理
2. **[触摸事件机制深入解析](https://segmentfault.com/a/1190000047072887)** - Android 触摸事件详解
3. **[Android触摸事件分发、手势识别与输入优化实战](https://juejin.cn/post/7611830146089615406)** - 事件分发机制
4. **[探秘Android手势事件机制与优化技巧](https://juejin.cn/post/7238869983621611576)** - 手势事件机制

---

*本文档基于 Android 14 和 HarmonyOS NEXT API 20/21 (6.0.0/6.0.1) 整理，具体 API 以官方最新文档为准。UI 交互功能的映射涉及复杂的编程范式转换和 API 20/21 新增的事件响应链机制，建议在实际迁移中结合具体场景灵活应用。*
