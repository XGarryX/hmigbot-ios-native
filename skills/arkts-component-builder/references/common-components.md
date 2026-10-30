# ArkTS 常用组件速查手册（**V1 历史文档 — Legacy**）

> ⚠️ **本项目锁 ArkTS V2**。本文档示例采用 **V1 装饰器写法**（`@Component / @State / @Prop / @Link`），仅用于阅读老代码或迁移老项目时查阅。
>
> **新代码请使用 V2 装饰器**：参阅 [`v2-common-components.md`](./v2-common-components.md)（V2 主参考，使用 `@ComponentV2 / @Local / @Param / @Event`）。

> 本文档为 LLM 提供常用 ArkTS UI 组件的快速参考，包含基本用法、关键属性和常见坑点。

---

## 1. Text — 文本显示

```typescript
// 基本用法
Text('Hello, HarmonyOS')
  .fontSize(16)
  .fontColor('#333333')
  .fontWeight(FontWeight.Medium)
  .maxLines(2)
  .textOverflow({ overflow: TextOverflow.Ellipsis })
```

**关键属性：**

| 属性 | 类型 | 说明 |
|------|------|------|
| `fontSize` | `number \| string \| Resource` | 字号，单位 vp |
| `fontColor` | `ResourceColor` | 文字颜色 |
| `fontWeight` | `FontWeight \| number` | 字重：`100`-`900` 或枚举 |
| `maxLines` | `number` | 最大行数 |
| `textOverflow` | `{ overflow: TextOverflow }` | 溢出处理：`.Ellipsis` / `.Clip` / `.None` |
| `textAlign` | `TextAlign` | 对齐：`.Start` / `.Center` / `.End` |
| `decoration` | `{ type, color? }` | 装饰线：`TextDecorationType.Underline` / `.LineThrough` |
| `lineHeight` | `number \| string` | 行高 |
| `letterSpacing` | `number \| string` | 字间距 |
| `fontStyle` | `FontStyle` | `.Normal` / `.Italic` |
| `copyOption` | `CopyOptions` | 长按复制：`.None` / `.InApp` / `.LocalDevice` |

**常见坑：**
- `textOverflow` 必须搭配 `maxLines` 才生效，单独设置无效
- `Text` 默认宽度是自适应内容的，在 `Row` 中需要用 `.layoutWeight(1)` 或 `.constraintSize({ maxWidth: '...' })` 限制宽度，否则省略号不生效
- 富文本用 `Span` 子组件实现：`Text() { Span('粗体').fontWeight(700); Span('普通') }`

---

## 2. Image — 图片显示

```typescript
// 本地资源图片
Image($r('app.media.photo'))
  .width(120)
  .height(120)
  .objectFit(ImageFit.Cover)
  .borderRadius(8)

// 网络图片
Image('https://example.com/image.png')
  .width('100%')
  .aspectRatio(1.5)
  .alt($r('app.media.placeholder'))  // 加载中占位图
  .onError(() => { console.error('图片加载失败') })
```

**关键属性：**

| 属性 | 类型 | 说明 |
|------|------|------|
| `objectFit` | `ImageFit` | `.Cover`（裁切填充）/ `.Contain`（完整显示）/ `.Fill`（拉伸）/ `.Auto` |
| `alt` | `Resource` | 加载中/失败时显示的占位图 |
| `interpolation` | `ImageInterpolation` | 图片插值：`.High` / `.Medium` / `.Low` / `.None` |
| `fillColor` | `ResourceColor` | SVG/图标染色 |
| `autoResize` | `boolean` | 是否自动缩放到组件大小，默认 `true` |
| `syncLoad` | `boolean` | 是否同步加载，默认 `false` |
| `copyOption` | `CopyOptions` | 长按复制图片 |

**常见坑：**
- 网络图片需要在 `module.json5` 中声明网络权限：`ohos.permission.INTERNET`
- `Image` 必须设置宽高或者至少一个维度 + `aspectRatio`，否则可能显示为 0
- SVG 图标变色用 `.fillColor()`，不要用 `.colorFilter()`
- 圆形头像：`.borderRadius(宽度/2)` 并确保宽高相等
- **Image 不能渲染视频 URI**：`Image` 组件不支持视频类型的 `photoAccessHelper` URI，视频文件的缩略图会显示为灰色空白。视频项应使用深色背景 + 播放图标占位：
  ```typescript
  if (medium.isVideo()) {
    Column() {
      Image($r('sys.media.ohos_ic_public_play'))
        .width(32).height(32).fillColor('#CCFFFFFF')
    }.backgroundColor('#1A1A1A').aspectRatio(1)
  } else {
    Image(medium.path).sourceSize({ width: 256, height: 256 })
  }
  ```
- **sourceSize 缩略图优化**：大量高分辨率图片缩略图会导致卡顿和内存飙升。为缩略图设置 `sourceSize` 限制解码尺寸：
  ```typescript
  Image(medium.path)
    .sourceSize({ width: 256, height: 256 }) // 缩略图只需 256px
    .objectFit(ImageFit.Cover)
  ```

---

## 3. Button — 按钮

```typescript
// 文字按钮
Button('确认', { type: ButtonType.Capsule, stateEffect: true })
  .width('100%')
  .height(44)
  .fontSize(16)
  .backgroundColor('#007DFF')
  .onClick(() => {
    console.info('按钮点击')
  })

// 图标+文字按钮
Button() {
  Row({ space: 6 }) {
    Image($r('sys.media.ohos_ic_public_add'))
      .width(20).height(20).fillColor(Color.White)
    Text('新建').fontSize(14).fontColor(Color.White)
  }
}
.height(36)
.padding({ left: 16, right: 16 })
```

**关键属性：**

| 属性 | 类型 | 说明 |
|------|------|------|
| `type` | `ButtonType` | `.Capsule`（圆角胶囊）/ `.Circle`（圆形）/ `.Normal`（方角） |
| `stateEffect` | `boolean` | 按下时是否有视觉反馈效果 |
| `fontSize` | `number` | 文字字号 |
| `fontColor` | `ResourceColor` | 文字颜色 |
| `backgroundColor` | `ResourceColor` | 背景色 |
| `enabled` | `boolean` | 是否可点击 |

**常见坑：**
- `Button` 自带内边距，自定义内容时用不带文字参数的 `Button() { ... }` 形式
- `ButtonType.Capsule` 的圆角是自动计算的，不能通过 `.borderRadius()` 覆盖；用 `ButtonType.Normal` 再手动设圆角
- 禁用态自动变灰，无需手动设颜色

---

## 4. TextInput — 文本输入

```typescript
// 基本输入框
TextInput({ placeholder: '请输入内容', text: this.inputValue })
  .height(48)
  .width('100%')
  .fontSize(16)
  .maxLength(50)
  .type(InputType.Normal)
  .onChange((value: string) => {
    this.inputValue = value
  })
  .onSubmit((enterKey: EnterKeyType) => {
    console.info('提交')
  })
```

**关键属性：**

| 属性 | 类型 | 说明 |
|------|------|------|
| `type` | `InputType` | `.Normal` / `.Password` / `.Email` / `.Number` / `.PhoneNumber` |
| `placeholder` | `string` | 占位提示文字 |
| `placeholderColor` | `ResourceColor` | 占位文字颜色 |
| `maxLength` | `number` | 最大输入字符数 |
| `enterKeyType` | `EnterKeyType` | 回车键类型：`.Search` / `.Send` / `.Done` / `.Go` |
| `caretColor` | `ResourceColor` | 光标颜色 |
| `showPasswordIcon` | `boolean` | 密码模式时是否显示切换图标 |
| `copyOption` | `CopyOptions` | 是否允许复制 |

**常见坑：**
- `TextInput` 是非受控组件。`.text($$this.value)` 双向绑定时用 `$$`，不用 `onChange`
- 键盘弹起可能遮挡输入框，外层需要 `Scroll` 容器或使用 `.expandSafeArea()` 避让
- `.onChange` 每次按键都触发，搜索场景需做防抖

---

## 5. Search — 搜索框

```typescript
// 搜索框
Search({ value: this.searchText, placeholder: '搜索商品' })
  .height(40)
  .width('100%')
  .searchButton('搜索')
  .onSubmit((value: string) => {
    this.doSearch(value)
  })
  .onChange((value: string) => {
    this.searchText = value
  })
```

**关键属性：**

| 属性 | 类型 | 说明 |
|------|------|------|
| `searchButton` | `string` | 右侧搜索按钮文字，不设则无按钮 |
| `placeholderColor` | `ResourceColor` | 占位文字颜色 |
| `placeholderFont` | `Font` | 占位文字字体 |
| `searchIcon` | `IconOptions` | 自定义搜索图标 |
| `cancelButton` | `object` | 取消按钮样式 |
| `textFont` | `Font` | 输入文字字体 |

**常见坑：**
- `Search` 自带左侧搜索图标和圆角样式，不需要额外包装
- `.onSubmit` 在软键盘搜索按钮点击时触发，`.onChange` 是实时输入变化

---

## 6. Toggle — 开关/选择

```typescript
// 开关
Toggle({ type: ToggleType.Switch, isOn: this.isEnabled })
  .selectedColor('#007DFF')
  .onChange((isOn: boolean) => {
    this.isEnabled = isOn
  })

// 复选按钮
Toggle({ type: ToggleType.Checkbox, isOn: false })
  .selectedColor('#007DFF')
  .size({ width: 20, height: 20 })

// 状态按钮（可切换样式的按钮）
Toggle({ type: ToggleType.Button, isOn: this.isActive }) {
  Text('关注')
    .fontSize(14)
    .fontColor(this.isActive ? Color.White : '#333')
}
.selectedColor('#007DFF')
```

**关键属性：**

| 属性 | 类型 | 说明 |
|------|------|------|
| `type` | `ToggleType` | `.Switch`（开关）/ `.Checkbox`（勾选）/ `.Button`（按钮） |
| `isOn` | `boolean` | 初始状态 |
| `selectedColor` | `ResourceColor` | 选中时颜色 |
| `switchPointColor` | `ResourceColor` | Switch 类型的滑块颜色 |

**常见坑：**
- `isOn` 只是初始值，不会响应式更新。需要双向绑定用 `isOn: $$this.isEnabled`
- `ToggleType.Button` 必须有子组件作为按钮内容

---

## 7. Swiper — 轮播

```typescript
// 图片轮播
Swiper() {
  ForEach(this.bannerList, (item: BannerItem) => {
    Image(item.imageUrl)
      .width('100%')
      .height('100%')
      .objectFit(ImageFit.Cover)
      .borderRadius(12)
  })
}
.autoPlay(true)
.interval(3000)
.indicator(
  new DotIndicator()
    .selectedColor(Color.White)
    .color('rgba(255,255,255,0.5)')
)
.loop(true)
.height(180)
.width('100%')
```

**关键属性：**

| 属性 | 类型 | 说明 |
|------|------|------|
| `autoPlay` | `boolean` | 是否自动播放 |
| `interval` | `number` | 自动播放间隔（ms） |
| `loop` | `boolean` | 是否循环 |
| `indicator` | `DotIndicator \| DigitIndicator \| boolean` | 指示器样式 |
| `vertical` | `boolean` | 是否纵向滑动 |
| `duration` | `number` | 切换动画时长（ms） |
| `cachedCount` | `number` | 预加载页数 |
| `displayCount` | `number` | 一屏显示几个 |

**常见坑：**
- Swiper 子元素必须直接是组件，不能在中间嵌套 `if/else`
- 动态数据更新后 Swiper 可能不刷新，需要用 key 强制刷新
- `displayCount > 1` 时可实现卡片式轮播

---

## 8. Tabs — 选项卡

```typescript
// 选项卡页面
@Entry
@Component
struct TabsPage {
  @State currentIndex: number = 0
  private tabTitles: string[] = ['首页', '分类', '购物车', '我的']

  @Builder
  tabBuilder(title: string, index: number) {
    Column() {
      Text(title)
        .fontSize(this.currentIndex === index ? 16 : 14)
        .fontWeight(this.currentIndex === index ? FontWeight.Bold : FontWeight.Normal)
        .fontColor(this.currentIndex === index ? '#007DFF' : '#999')
    }
    .width('100%')
    .height('100%')
    .justifyContent(FlexAlign.Center)
  }

  build() {
    Tabs({ barPosition: BarPosition.End, index: this.currentIndex }) {
      ForEach(this.tabTitles, (title: string, index: number) => {
        TabContent() {
          // 每个 Tab 页的内容
          Text(`${title}页面内容`)
            .fontSize(20)
        }
        .tabBar(this.tabBuilder(title, index))
      })
    }
    .barMode(BarMode.Fixed)
    .onChange((index: number) => {
      this.currentIndex = index
    })
    .width('100%')
    .height('100%')
  }
}
```

**关键属性：**

| 属性 | 类型 | 说明 |
|------|------|------|
| `barPosition` | `BarPosition` | `.Start`（顶部）/ `.End`（底部） |
| `barMode` | `BarMode` | `.Fixed`（等分）/ `.Scrollable`（可滚动） |
| `vertical` | `boolean` | 是否竖向 Tab |
| `scrollable` | `boolean` | 内容是否可滑动切换 |
| `animationDuration` | `number` | 切换动画时长 |
| `barWidth` | `Length` | Tab 栏宽度 |
| `barHeight` | `Length` | Tab 栏高度 |

**常见坑：**
- `TabContent` 必须用 `.tabBar()` 设置标签，不设会报错
- 顶部 Tab 用 `BarPosition.Start`，底部导航用 `BarPosition.End`
- `@Builder` 自定义 tabBar 时，`index` 参数用于实现选中态样式

---

## 9. LoadingProgress — 加载指示器

```typescript
// 页面加载中
if (this.isLoading) {
  Column() {
    LoadingProgress()
      .width(48)
      .height(48)
      .color('#007DFF')
    Text('加载中...')
      .fontSize(14)
      .fontColor('#999')
      .margin({ top: 12 })
  }
  .width('100%')
  .layoutWeight(1)
  .justifyContent(FlexAlign.Center)
}
```

**关键属性：**

| 属性 | 类型 | 说明 |
|------|------|------|
| `color` | `ResourceColor` | 加载动画颜色 |
| `width` / `height` | `Length` | 组件大小 |

**常见坑：**
- `LoadingProgress` 是系统自带转圈动画，无法自定义动画形式
- 大小建议 32-64vp，太小看不清，太大不美观

---

## 10. Divider — 分割线

```typescript
// 水平分割线
Divider()
  .strokeWidth(0.5)
  .color('#F0F0F0')
  .margin({ left: 16, right: 16 })

// 垂直分割线（在 Row 中使用）
Row() {
  Text('左').layoutWeight(1).textAlign(TextAlign.Center)
  Divider().vertical(true).height(20).strokeWidth(1).color('#E0E0E0')
  Text('右').layoutWeight(1).textAlign(TextAlign.Center)
}
```

**关键属性：**

| 属性 | 类型 | 说明 |
|------|------|------|
| `strokeWidth` | `number` | 线宽 |
| `color` | `ResourceColor` | 颜色 |
| `vertical` | `boolean` | 是否垂直，默认 `false`（水平线） |
| `lineCap` | `LineCapStyle` | 端点样式 |

**常见坑：**
- 默认是水平全宽分割线，用 `margin` 控制缩进
- 垂直分割线需要在 `Row` 中使用，且必须设置 `height`

---

## 11. Badge — 角标

```typescript
// 数字角标
Badge({
  count: this.unreadCount,
  maxCount: 99,
  position: BadgePosition.RightTop,
  style: {
    badgeSize: 16,
    badgeColor: '#FF4D4F',
    fontSize: 10
  }
}) {
  Image($r('app.media.message_icon'))
    .width(28)
    .height(28)
}

// 红点标记（不显示数字）
Badge({
  value: '',
  position: BadgePosition.RightTop,
  style: { badgeSize: 8, badgeColor: '#FF4D4F' }
}) {
  Text('消息')
    .fontSize(16)
}
```

**关键属性（构造参数）：**

| 属性 | 类型 | 说明 |
|------|------|------|
| `count` | `number` | 显示数字 |
| `maxCount` | `number` | 最大数字，超过显示 `maxCount+` |
| `value` | `string` | 显示文本（与 count 二选一），空字符串 `''` 显示纯红点 |
| `position` | `BadgePosition` | `.RightTop` / `.Right` / `.Left` |
| `style` | `BadgeStyle` | 角标尺寸、颜色、字号 |

**常见坑：**
- `count` 为 0 时角标自动隐藏
- Badge 是包裹型组件，子组件写在 `{ }` 中

---

## 12. Blank — 空白填充

```typescript
// 用在 Row 中推开左右元素
Row() {
  Text('标题').fontSize(16)
  Blank()  // 占满中间所有空间
  Text('更多 >').fontSize(14).fontColor('#999')
}
.width('100%')
.padding(16)

// 设置最小宽度
Row() {
  Text('A')
  Blank().min(20)  // 最少 20vp 空白
  Text('B')
}
```

**关键属性：**

| 属性 | 类型 | 说明 |
|------|------|------|
| `min` | `number` | 最小尺寸 |
| `color` | `ResourceColor` | 填充颜色（调试时可用） |

**常见坑：**
- `Blank` 仅在 `Row` 或 `Column` 中有效，在其他容器中无效果
- 等价于 CSS 的 `flex: 1` + `margin: auto` 效果
- 多个 Blank 等分剩余空间

---

## 13. Progress — 进度条

```typescript
// 线性进度条
Progress({ value: 70, total: 100, type: ProgressType.Linear })
  .width('100%')
  .height(8)
  .color('#007DFF')
  .backgroundColor('#E8E8E8')
  .style({ strokeWidth: 8, strokeRadius: 4 })

// 环形进度条
Progress({ value: 75, total: 100, type: ProgressType.Ring })
  .width(80)
  .height(80)
  .color('#007DFF')
  .style({ strokeWidth: 8 })

// 胶囊进度条（带文字）
Progress({ value: 45, total: 100, type: ProgressType.Capsule })
  .width(200)
  .height(40)
  .color('#007DFF')
```

**关键属性：**

| 属性 | 类型 | 说明 |
|------|------|------|
| `value` | `number` | 当前进度值 |
| `total` | `number` | 总进度值，默认 100 |
| `type` | `ProgressType` | `.Linear` / `.Ring` / `.Eclipse` / `.ScaleRing` / `.Capsule` |
| `color` | `ResourceColor` | 进度颜色 |
| `backgroundColor` | `ResourceColor` | 背景色 |
| `style` | `ProgressStyleOptions` | 详细样式：`strokeWidth`、`strokeRadius` 等 |

**常见坑：**
- `value` 动态更新时会自动有动画过渡
- `ProgressType.Ring` 需要设等宽等高才是正圆

---

## 14. Rating — 评分

```typescript
// 星级评分
Rating({ rating: this.score, indicator: false })
  .stars(5)
  .stepSize(0.5)
  .starStyle({
    backgroundUri: '/common/star_empty.svg',
    foregroundUri: '/common/star_full.svg',
    secondaryUri: '/common/star_half.svg'
  })
  .onChange((value: number) => {
    this.score = value
  })

// 只读评分展示
Rating({ rating: 4.5, indicator: true })
  .stars(5)
  .width(100)
```

**关键属性：**

| 属性 | 类型 | 说明 |
|------|------|------|
| `rating` | `number` | 当前评分值 |
| `indicator` | `boolean` | `true` 只读，`false` 可交互 |
| `stars` | `number` | 星星总数，默认 5 |
| `stepSize` | `number` | 步长：`0.5`（半星）/ `1`（整星） |
| `starStyle` | `StarStyleOptions` | 自定义图标：`backgroundUri`、`foregroundUri`、`secondaryUri` |

**常见坑：**
- 自定义星星图标需要同时提供 3 个状态（空/半/满）的资源
- `indicator: true` 时用户不可操作，仅展示

---

## 15. Slider — 滑块

```typescript
// 水平滑块
Slider({
  value: this.volume,
  min: 0,
  max: 100,
  step: 1,
  style: SliderStyle.OutSet
})
.width('100%')
.blockColor(Color.White)
.trackColor('#E8E8E8')
.selectedColor('#007DFF')
.showTips(true)
.onChange((value: number, mode: SliderChangeMode) => {
  this.volume = value
  if (mode === SliderChangeMode.End) {
    console.info(`最终值: ${value}`)
  }
})
```

**关键属性：**

| 属性 | 类型 | 说明 |
|------|------|------|
| `value` | `number` | 当前值 |
| `min` / `max` | `number` | 范围 |
| `step` | `number` | 步长 |
| `style` | `SliderStyle` | `.OutSet`（滑块在轨道外）/ `.InSet`（滑块在轨道内）|
| `direction` | `Axis` | `.Horizontal` / `.Vertical` |
| `blockColor` | `ResourceColor` | 滑块颜色 |
| `trackColor` | `ResourceColor` | 未选中轨道颜色 |
| `selectedColor` | `ResourceColor` | 已选中轨道颜色 |
| `showTips` | `boolean` | 拖动时是否显示提示值 |

**常见坑：**
- `onChange` 的 `mode` 参数区分拖动过程（`Moving`）和结束（`End`），避免在拖动中做重计算
- 垂直滑块需要显式设 `height`

---

## 16. Select — 下拉选择

```typescript
// 下拉选择器
Select([
  { value: '选项一' },
  { value: '选项二' },
  { value: '选项三' },
  { value: '选项四' }
])
.selected(this.selectedIndex)
.value(this.selectedValue)
.font({ size: 16 })
.fontColor('#333')
.selectedOptionFont({ size: 16, weight: FontWeight.Medium })
.selectedOptionFontColor('#007DFF')
.optionFont({ size: 16 })
.optionFontColor('#333')
.onSelect((index: number, value: string) => {
  this.selectedIndex = index
  this.selectedValue = value
})
```

**关键属性：**

| 属性 | 类型 | 说明 |
|------|------|------|
| `selected` | `number` | 当前选中索引 |
| `value` | `string` | 当前显示文本 |
| `font` | `Font` | 显示区字体 |
| `fontColor` | `ResourceColor` | 显示区文字颜色 |
| `optionFont` | `Font` | 下拉列表项字体 |
| `optionFontColor` | `ResourceColor` | 下拉列表项颜色 |
| `selectedOptionFont` | `Font` | 选中项字体 |
| `selectedOptionFontColor` | `ResourceColor` | 选中项颜色 |
| `selectedOptionBgColor` | `ResourceColor` | 选中项背景色 |

**常见坑：**
- `Select` 的构造参数是 `SelectOption[]` 数组，每项至少有 `value` 字段，可选 `icon`
- 初始状态如果不设 `selected` 和 `value`，显示为空
- 选项较多时下拉列表自动可滚动，无需额外处理

---

## 通用属性速查

以下属性可用于所有组件：

```typescript
// 尺寸
.width('100%')          // 宽度：数字(vp)、百分比字符串、Resource
.height(48)             // 高度
.aspectRatio(1.5)       // 宽高比
.constraintSize({       // 约束尺寸
  minWidth: 100, maxWidth: 300,
  minHeight: 50, maxHeight: 200
})

// 边距
.margin(16)             // 全方向
.margin({ top: 8, bottom: 8 })  // 分方向
.padding({ left: 16, right: 16 })

// 背景与边框
.backgroundColor('#F5F5F5')
.borderRadius(12)       // 统一圆角
.borderRadius({ topLeft: 12, topRight: 12 })  // 分角
.border({ width: 1, color: '#E0E0E0', style: BorderStyle.Solid })

// 阴影
.shadow({
  radius: 8,
  color: 'rgba(0,0,0,0.1)',
  offsetX: 0,
  offsetY: 2
})

// 透明度与可见性
.opacity(0.8)           // 0-1
.visibility(Visibility.Visible)  // Visible | Hidden | None

// 交互
.enabled(true)          // 是否可交互
.onClick(() => {})      // 点击事件
.onTouch((event) => {}) // 触摸事件

// 动画
.animation({
  duration: 300,
  curve: Curve.EaseInOut
})
```
