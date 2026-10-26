# 无障碍 · 错误模式汇总

从历史修复中归纳的 6 类错误模式。每个模式包含：典型症状、高发组件、机制、排查提示、修复建议。

---

## 模式 1：图标按钮 / 自定义控件缺无障碍语义标签

### 典型症状
- 屏幕朗读只念 "按钮"、"图片"，不念功能（关闭、服务面板、收藏…）
- 自定义 AppBar、Toolbar、悬浮操作键的关闭键、菜单键完全无播报
- 视障用户只能靠记忆位置操作

### 高发组件
`Image` / 纯图标 `Button` / 自定义 AppBar / 自定义浮层按钮 / 带 `onClick` 的 `Stack` / `Row` 容器。

### 机制
无障碍树里每个节点有 `text` 字段。纯图标元素没有 `Text` 子节点，默认 `text = ""`，屏幕朗读退化到只念组件类型。必须通过 `accessibilityText`（主播报）+ `accessibilityDescription`（补充说明）显式注入。

### 排查提示
1. 对每个 `onClick` 的元素检查有没有可见文字
2. 无可见文字却可点击 → 必须有 `accessibilityText`
3. 文本要来自 i18n 资源而非硬编码中文，避免多语言读屏错音

### 修复建议
```ts
@ComponentV2
struct ServiceBar {
  @Local menuRead: string = getContext(this)
    .resourceManager.getStringByNameSync('arkui_app_bar_service_panel');

  build() {
    Row() {
      Image($r('app.media.ic_service'))
        .width(24).height(24)
        .onClick(() => this.openPanel())
        .accessibilityText(this.menuRead)              // 必填：读屏主文本
        .accessibilityDescription('双击打开服务面板')   // 选填：操作提示
        .accessibilityLevel('yes')                     // 图标按钮建议强制 yes

      // 纯装饰性图片要显式屏蔽
      Image($r('app.media.decoration'))
        .accessibilityLevel('no-hide-descendants')
    }
  }

  private openPanel(): void { /* ... */ }
}
```

> V1 等价：`@Component` → `@ComponentV2`、`@State` → `@Local`。

---

## 模式 2：选中 / 勾选 / 展开状态未同步到无障碍树

### 典型症状
- 自定义 Tab 切换后读屏仍播报 "未选中"
- 自绘 Checkbox/RadioGroup 被读成 "复选框"，但不念 "已勾选 / 未勾选"
- 折叠面板展开了，朗读内容不变

### 高发组件
自定义 `Tab / Segment`、`Chip`（选中态）、自绘 `Checkbox / Radio`、`Accordion / Expander`、Option 列表项。

### 机制
原生 `Checkbox / Radio / Toggle` 自带状态，无障碍树的 `checked / selected` 会自动填充。但用 `Text / Row / Stack` 自行绘制的 "伪控件" 没有这条通路，需通过 `accessibilityChecked(boolean)` / `accessibilitySelected(boolean)` 主动把状态推入无障碍树。

### 排查提示
1. 用 `hidumper -s AccessibilityMS` 抓节点，查 `checked / selected` 字段
2. 若字段始终为 false 且组件是自绘 → 缺属性绑定
3. 确认属性绑定的是 `@Local` 变量（V1：`@State`）—— 会自动触发刷新，不是普通成员

### 修复建议
```ts
// 自定义单选项
Text(this.label)
  .onClick(() => this.onSelect())
  .accessibilitySelected(this.selected)
  .accessibilityText(this.label)
  .accessibilityDescription(this.selected ? '已选中' : '未选中')

// 自绘勾选
Row() { /* 自绘方框 + 勾 */ }
  .onClick(() => this.checked = !this.checked)
  .accessibilityChecked(this.checked)
```
`@Local`（V1：`@State`）变化时 ArkUI 会自动刷新无障碍属性，不需要手动触发事件。

---

## 模式 3：XComponent / Web / 自绘控件无法被读屏识别

### 典型症状
- `XComponent` 里的按钮、`Web` 里的 DOM 元素完全读不到
- `Web` 页面滑动后无障碍焦点（绿框）停留在老位置，不跟手
- 自绘画布区域读屏扫过无任何反馈

### 高发组件
`XComponent`（NDK 渲染、游戏、图形 SDK）、`Web`（H5 内容）、Canvas 自绘控件。

### 机制
ArkTS 声明式无障碍树只覆盖声明式节点；`XComponent` / `Web` 的内容由自身渲染模块管理，必须由底层桥接后才能被读屏识别：

- `Web`：升级到内置无障碍桥接的 SDK 版本即可，应用侧通常无需改代码
- `XComponent`：需由 NDK 侧实现 AccessibilityProvider；ArkTS 侧做不到

应用侧能做的兜底：对整个三方渲染容器提供整体语义标注，至少告诉用户这是什么区域。

### 排查提示
1. 打开读屏，手指在 `XComponent` / `Web` 区域滑动，若无任何反馈 → 底层未桥接
2. 焦点能落上但滑动后不跟手 → `Web` SDK 版本过旧
3. 焦点绿框出现在组件外 → 底层返回的 rect 不准，升级 SDK

### 修复建议
```ts
// 整体语义兜底：给容器一个 accessibilityText，至少能被读到
Stack() {
  XComponent({ id: 'mapView', type: 'surface', libraryname: 'map' })
}
  .accessibilityText('地图画面')
  .accessibilityDescription('双击进入地图交互模式')
  .accessibilityGroup(true)   // 子节点合并为一个播报单元

// Web 只需升级 SDK；若自定义 WebController 需确保滚动/页面切换事件正常回传
Web({ src: 'https://example.com', controller: this.webController })
```

如果 `XComponent` 里有明确的交互热点（如游戏中的按钮），在 ArkTS 侧叠加一层透明可点击 `Button` 做无障碍代理，是目前最常用的做法。

---

## 模式 4：触达热区过小 / 手势与读屏冲突

### 典型症状
- 按钮看得到但点不中，需要反复点
- 长按拖拽在开启读屏时无法触发（读屏抢占手势）
- 老年用户反馈 "按不准"

### 高发组件
紧凑布局中的小图标按钮、文本选择菜单中的 "复制 / 全选"、自定义长按菜单、可拖拽列表项。

### 机制
- `.responseRegion()` 会**完全覆盖**默认热区；若写死比组件 rect 更小的范围，会直接裁掉可点击区
- `.hitTestBehavior()` 决定命中测试行为；装饰性遮罩若为默认 `Default`，会拦截下层点击
- 读屏开启后会接管单击/双击/长按，自绘短长按（< 300ms）或复合手势会与读屏冲突

### 排查提示
1. 搜 `.responseRegion(` 所有调用点，确认没有把区域写小
2. 检查交互元素最小视觉尺寸 × 最小热区均应 ≥ `48vp`
3. 读屏下测试长按、拖拽、双击——若要求 `< 300ms` 的快速手势序列，必然冲突
4. 浮层遮罩检查 `.hitTestBehavior(HitTestMode.Transparent)`

### 修复建议
```ts
// 小图标按钮：用 constraintSize 保证最小热区，比 responseRegion 稳
Image($r('app.media.ic_close'))
  .width(24).height(24)
  .constraintSize({ minWidth: 48, minHeight: 48 })
  .onClick(() => this.close())
  .accessibilityText('关闭')
  .accessibilityLevel('yes')

// 拖拽手势给读屏留出时间（不要用默认 ~150ms）
LongPressGesture({ repeat: false, duration: 500 })
  .onAction(() => this.startDrag())

// 装饰层允许点击穿透
Stack()
  .hitTestBehavior(HitTestMode.Transparent)
  .accessibilityLevel('no-hide-descendants')

// 自绘/定制按钮推荐走 gestureModifier（与读屏事件派发兼容）
// 如使用系统高级组件的 ButtonGestureModifier：先确认 import 路径；否则自行实现 GestureModifier 接口
import { ButtonGestureModifier } from '@ohos.arkui.advanced.Dialog';  // 参考 import，以实际 SDK 版本为准
Button('确定')
  .gestureModifier(new ButtonGestureModifier(/* 按 API 要求传参 */))
```

---

## 模式 5：焦点入口与焦点遍历顺序错误

### 典型症状
- 弹窗/浮层弹出后，读屏焦点仍停留在下层页面
- 键盘 Tab 切焦点时顺序混乱，跳到视觉上很远的控件
- 自定义列表项无法用键盘/遥控器选中
- 焦点在嵌套容器里 "逃" 出去，或根本进不去

### 高发组件
自定义 Dialog / Popup / Sheet、自定义列表项、嵌套 `Scroll` / `List`、tabIndex 未设置的表单。

### 机制
ArkUI 的 UI 焦点系统依赖 `.focusable(true)` / `.tabIndex(n)` / `.defaultFocus(true)` / `.groupDefaultFocus(true)` 这组属性：

- 默认 `focusable` 取决于组件类型：`Button` / `TextInput` 默认可聚焦，`Text` / `Row` 默认不可
- `tabIndex` 控制 Tab 键顺序；未设置时按节点树顺序
- 弹窗类容器需显式 `.defaultFocus(true)` 指定焦点入口，否则焦点停在原位置
- `.focusOnTouch(true)` 让触摸也能触发焦点，适配键鼠混用场景

无障碍焦点（读屏绿框）与 UI 焦点是两套，但 `.defaultFocus` 同时影响两者的初始位置。

### 排查提示
1. 自定义 Dialog 里找一个应该首焦的元素（如 "确定" 按钮），看是否设 `.defaultFocus(true)`
2. 搜 `.tabIndex(` 看表单是否按语义顺序声明
3. 嵌套列表是否用 `.groupDefaultFocus(true)` 把组级默认焦点指向首项
4. 用 Inspector 查 "focusable" 属性是否为预期

### 修复建议
```ts
// 自定义 Dialog 明确焦点入口
Column() {
  Text('是否删除？')
  Row() {
    Button('取消').onClick(() => this.cancel())
    Button('确定')
      .onClick(() => this.confirm())
      .defaultFocus(true)      // 首焦：确定
  }
}
  .groupDefaultFocus(true)     // 作为焦点组

// 表单按语义顺序设 tabIndex
TextInput({ placeholder: '姓名' }).tabIndex(1)
TextInput({ placeholder: '电话' }).tabIndex(2)
Button('提交').tabIndex(3)

// 自定义列表项可聚焦 + 触摸触焦
Row() { /* ... */ }
  .focusable(true)
  .focusOnTouch(true)
  .onClick(() => this.onTap())
```

---

## 模式 6：装饰性元素被误读 / 动态内容读屏未刷新

### 典型症状
- 读屏念出 "图片、图片、图片"（循环背景图、分隔线）
- 下拉刷新时 Loading 图被反复播报
- 数据刷新后，读屏仍停留在旧的文本上
- Toast / Snackbar 出现但读屏不播报

### 高发组件
背景装饰图、分隔线 `Divider`、Loading 动画、Badge 数字、轮询刷新的数据卡片。

### 机制
- 装饰性元素若不显式屏蔽，会和内容节点混在无障碍树中，读屏按顺序扫过全部念出
- `accessibilityLevel('no-hide-descendants')` 能屏蔽整棵子树
- 动态文本绑定 `@Local` / `@Param`（V1：`@State` / `@Prop`）时 ArkUI 会自动刷新无障碍属性；若绑了普通变量，节点不会更新
- Toast 等一次性 UI 需要系统层支持读屏通知；应用侧应避免用自定义 `Stack` 模拟 Toast（因为不会触发读屏通知）

### 排查提示
1. 所有纯装饰元素（背景图、分隔线、Loading）是否设 `accessibilityLevel('no-hide-descendants')`
2. 动态文本是否绑定 `@Local` / `@Param` 等响应式变量（V1：`@State` / `@Link` / `@Prop`）
3. 是否用了自定义 "伪 Toast"，应改用系统 `promptAction.showToast`
4. Badge 数字若只是视觉红点（无数字意义）应屏蔽

### 修复建议
```ts
// 装饰元素：屏蔽整棵子树
Image($r('app.media.bg_decoration'))
  .accessibilityLevel('no-hide-descendants')

Divider()
  .accessibilityLevel('no-hide-descendants')

// Loading 动画：不参与播报
LoadingProgress()
  .accessibilityLevel('no-hide-descendants')

// 动态文本必须用 @Local（V1：@State）才会触发无障碍刷新
@ComponentV2
struct PriceTag {
  @Local price: string = '¥0';

  build() {
    Text(this.price)                       // 数据变化时读屏会重新播报
      .accessibilityText(`价格 ${this.price}`)
  }
}

// 小红点 Badge（无数字）屏蔽
Badge({ count: 0, style: { badgeSize: 6 } }) {
  Image($r('app.media.ic_msg'))
}
  .accessibilityText('消息')
  .accessibilityLevel('yes')
```

对于必须主动播报的动态变化（如异步加载完成），目前 ArkTS 没有直接 API，实践上有两种兜底：
1. 让焦点移到新出现的节点（`.defaultFocus(true)` 配合条件渲染），读屏自然会播报
2. 用系统 `promptAction.showToast`，让系统层走读屏通知
