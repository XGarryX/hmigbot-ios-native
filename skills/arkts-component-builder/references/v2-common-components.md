# ArkTS 常用组件速查手册（V2）

> 本文档为 LLM 提供常用 ArkTS UI 组件的 **V2** 用法快速参考（`@ComponentV2 / @Local / @Param / @Event`），包含基本用法、关键属性和常见坑点。**本项目锁 V2**，本文档为主参考。V1 历史用法查阅请见 [`common-components.md`](./common-components.md)。

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

**常见坑：**
- `textOverflow` 必须搭配 `maxLines` 才生效，单独设置无效
- `Text` 默认宽度是自适应内容的，在 `Row` 中需要用 `.layoutWeight(1)` 或 `.constraintSize({ maxWidth: '...' })` 限制宽度
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
  .alt($r('app.media.placeholder'))
  .onError(() => { console.error('图片加载失败') })
```

**关键属性：**

| 属性 | 类型 | 说明 |
|------|------|------|
| `objectFit` | `ImageFit` | `.Cover` / `.Contain` / `.Fill` / `.Auto` |
| `alt` | `Resource` | 加载中/失败时显示的占位图 |
| `fillColor` | `ResourceColor` | SVG/图标染色 |
| `autoResize` | `boolean` | 是否自动缩放，默认 `true` |
| `syncLoad` | `boolean` | 是否同步加载，默认 `false` |

**常见坑：**
- 网络图片需要在 `module.json5` 中声明 `ohos.permission.INTERNET`
- `Image` 必须设置宽高或者至少一个维度 + `aspectRatio`
- SVG 图标变色用 `.fillColor()`
- 圆形头像：`.borderRadius(宽度/2)` 并确保宽高相等
- **Image 不能渲染视频 URI**：视频项使用深色背景 + 播放图标占位
- **sourceSize 缩略图优化**：大量高分辨率图片设置 `sourceSize({ width: 256, height: 256 })`

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

**常见坑：**
- `Button` 自带内边距，自定义内容用 `Button() { ... }` 不带文字参数的形式
- `ButtonType.Capsule` 圆角自动计算，不能 `.borderRadius()` 覆盖；用 `ButtonType.Normal` 手动设
- 禁用态自动变灰，无需手动设颜色

---

## 4. TextInput — 文本输入（V2 推荐 @Param + @Event 双向）

```typescript
// V2 推荐：父组件持有 @Local，子组件 @Param + @Event 接收/通知
@ComponentV2
struct EditForm {
  @Local inputValue: string = ''

  build() {
    TextInput({ placeholder: '请输入内容', text: this.inputValue })
      .height(48)
      .width('100%')
      .fontSize(16)
      .maxLength(50)
      .type(InputType.Normal)
      .onChange((value: string) => {
        this.inputValue = value     // 直接更新 @Local
      })
      .onSubmit((enterKey: EnterKeyType) => {
        console.info('提交')
      })
  }
}
```

**封装为可复用子组件（@Param + @Event）：**

```typescript
@ComponentV2
struct LabeledInput {
  @Param @Once placeholder: string = ''
  @Param @Once labelText: string = ''         // 不用 label（避免与 Label 组件混淆）
  @Param inputValue: string = ''
  @Event onValueChange: (v: string) => void = () => {}

  build() {
    Column({ space: 4 }) {
      Text(this.labelText).fontSize(14).fontColor('#666')
      TextInput({ placeholder: this.placeholder, text: this.inputValue })
        .height(48)
        .onChange((v: string) => { this.onValueChange(v) })
    }
  }
}

// 父组件
@ComponentV2
struct LoginForm {
  @Local userName: string = ''

  build() {
    LabeledInput({
      placeholder: '请输入用户名',
      labelText: '用户名',
      inputValue: this.userName,
      onValueChange: (v: string) => { this.userName = v }
    })
  }
}
```

**关键属性：**

| 属性 | 类型 | 说明 |
|------|------|------|
| `type` | `InputType` | `.Normal` / `.Password` / `.Email` / `.Number` / `.PhoneNumber` |
| `placeholder` | `string` | 占位提示文字 |
| `placeholderColor` | `ResourceColor` | 占位文字颜色 |
| `maxLength` | `number` | 最大输入字符数 |
| `enterKeyType` | `EnterKeyType` | `.Search` / `.Send` / `.Done` / `.Go` |
| `caretColor` | `ResourceColor` | 光标颜色 |
| `showPasswordIcon` | `boolean` | 密码模式显示切换图标 |

**常见坑：**
- V2 推荐用 `@Param + @Event` 配合，不要试图用 V1 `$$` 双向绑定（V1 风格）
- 键盘弹起遮挡输入框，外层用 `Scroll` 容器或 `.expandSafeArea()` 避让
- `.onChange` 每次按键都触发，搜索场景需做防抖

---

## 5. Search — 搜索框

```typescript
@ComponentV2
struct SearchPage {
  @Local searchText: string = ''

  @Monitor('searchText')
  onSearchTextChange(monitor: IMonitor): void {
    // V2 用 @Monitor 替代 V1 @Watch，做防抖搜索
    this.debouncedSearch(this.searchText)
  }

  build() {
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
  }

  private doSearch(kw: string): void { /* ... */ }
  private debouncedSearch(kw: string): void { /* ... */ }
}
```

**常见坑：**
- `Search` 自带左侧搜索图标和圆角样式
- `.onSubmit` 在软键盘搜索按钮点击时触发，`.onChange` 是实时输入

---

## 6. Toggle — 开关/选择（V2 @Param + @Event 模式）

```typescript
// 子组件 — @Param + @Event 双向（替代 V1 @Link）
@ComponentV2
struct AppSwitch {
  @Param isEnabled: boolean = false
  @Event onIsEnabledChange: (v: boolean) => void = () => {}

  build() {
    Toggle({ type: ToggleType.Switch, isOn: this.isEnabled })
      .selectedColor('#007DFF')
      .onChange((v: boolean) => {
        this.onIsEnabledChange(v)
      })
  }
}

// 父组件
@ComponentV2
struct SettingsPage {
  @Local isPlayEnabled: boolean = true   // 不用 enabled

  build() {
    AppSwitch({
      isEnabled: this.isPlayEnabled,
      onIsEnabledChange: (v: boolean) => { this.isPlayEnabled = v }
    })
  }
}
```

**常见坑：**
- V2 不再用 `isOn: $$this.isEnabled` 这种 V1 双向绑定语法
- `ToggleType.Button` 必须有子组件作为按钮内容

---

## 7. Swiper — 轮播

```typescript
@ComponentV2
struct BannerSection {
  @Local banners: BannerItem[] = []

  build() {
    Swiper() {
      ForEach(this.banners, (item: BannerItem) => {
        Image(item.imageUrl)
          .width('100%')
          .height('100%')
          .objectFit(ImageFit.Cover)
          .borderRadius(12)
      }, (item: BannerItem) => item.id)
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
  }
}

class BannerItem {
  id: string = ''
  imageUrl: string = ''
}
```

**常见坑：**
- Swiper 子元素必须直接是组件，不能在中间嵌套 `if/else`
- 动态数据更新后 Swiper 可能不刷新，需要用 key 强制刷新
- `displayCount > 1` 时可实现卡片式轮播

---

## 8. Tabs — 选项卡（V2）

```typescript
@Entry
@ComponentV2
struct TabsPage {
  @Local currentTabIndex: number = 0
  private tabTitles: string[] = ['首页', '分类', '购物车', '我的']

  @Builder
  tabBuilder(title: string, index: number) {
    Column() {
      Text(title)
        .fontSize(this.currentTabIndex === index ? 16 : 14)
        .fontWeight(this.currentTabIndex === index ? FontWeight.Bold : FontWeight.Normal)
        .fontColor(this.currentTabIndex === index ? '#007DFF' : '#999')
    }
    .width('100%')
    .height('100%')
    .justifyContent(FlexAlign.Center)
  }

  build() {
    Tabs({ barPosition: BarPosition.End, index: this.currentTabIndex }) {
      ForEach(this.tabTitles, (title: string, index: number) => {
        TabContent() {
          Text(`${title}页面内容`)
            .fontSize(20)
        }
        .tabBar(this.tabBuilder(title, index))
      }, (title: string, index: number) => `${index}_${title}`)
    }
    .barMode(BarMode.Fixed)
    .onChange((index: number) => {
      this.currentTabIndex = index
    })
    .width('100%')
    .height('100%')
  }
}
```

**常见坑：**
- `TabContent` 必须用 `.tabBar()` 设置标签
- 顶部 Tab 用 `BarPosition.Start`，底部导航用 `BarPosition.End`
- `@Builder` 自定义 tabBar 时，`index` 参数用于实现选中态样式

---

## 9. LoadingProgress — 加载指示器

```typescript
@ComponentV2
struct LoadingState {
  @Param @Once isLoading: boolean = true

  build() {
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
  }
}
```

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

---

## 11. Badge — 角标

```typescript
@ComponentV2
struct MessageIcon {
  @Param @Once unreadCount: number = 0

  build() {
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
  }
}
```

**常见坑：**
- `count` 为 0 时角标自动隐藏
- Badge 是包裹型组件，子组件写在 `{ }` 中

---

## 12. Blank — 空白填充

```typescript
// 用在 Row 中推开左右元素
Row() {
  Text('标题').fontSize(16)
  Blank()
  Text('更多 >').fontSize(14).fontColor('#999')
}
.width('100%')
.padding(16)
```

**常见坑：**
- `Blank` 仅在 `Row` 或 `Column` 中有效
- 多个 Blank 等分剩余空间

---

## 13. Progress — 进度条

```typescript
@ComponentV2
struct ProgressDemo {
  @Param @Once progressValue: number = 0  // 不用 value

  build() {
    Column() {
      // 线性进度条
      Progress({ value: this.progressValue, total: 100, type: ProgressType.Linear })
        .width('100%')
        .height(8)
        .color('#007DFF')

      // 环形进度条
      Progress({ value: this.progressValue, total: 100, type: ProgressType.Ring })
        .width(80)
        .height(80)
        .color('#007DFF')
        .style({ strokeWidth: 8 })
    }
  }
}
```

---

## 14. Rating — 评分

```typescript
@ComponentV2
struct RatingForm {
  @Local score: number = 0   // 不用 value

  build() {
    Rating({ rating: this.score, indicator: false })
      .stars(5)
      .stepSize(0.5)
      .onChange((v: number) => {
        this.score = v
      })
  }
}
```

---

## 15. Slider — 滑块

```typescript
@ComponentV2
struct VolumeControl {
  @Local volumeLevel: number = 50   // 不用 value

  build() {
    Slider({
      value: this.volumeLevel,
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
      this.volumeLevel = value
      if (mode === SliderChangeMode.End) {
        console.info(`最终值: ${value}`)
      }
    })
  }
}
```

---

## 16. Select — 下拉选择

```typescript
@ComponentV2
struct CategorySelector {
  @Local selectedIndex: number = 0
  @Local selectedValue: string = '选项一'

  build() {
    Select([
      { value: '选项一' },
      { value: '选项二' },
      { value: '选项三' }
    ])
    .selected(this.selectedIndex)
    .value(this.selectedValue)
    .font({ size: 16 })
    .fontColor('#333')
    .onSelect((index: number, value: string) => {
      this.selectedIndex = index
      this.selectedValue = value
    })
  }
}
```

---

## 通用属性速查

```typescript
// 尺寸
.width('100%')
.height(48)
.aspectRatio(1.5)
.constraintSize({ minWidth: 100, maxWidth: 300, minHeight: 50, maxHeight: 200 })

// 边距
.margin(16)
.margin({ top: 8, bottom: 8 })
.padding({ left: 16, right: 16 })

// 背景与边框
.backgroundColor('#F5F5F5')
.borderRadius(12)
.border({ width: 1, color: '#E0E0E0', style: BorderStyle.Solid })

// 阴影
.shadow({ radius: 8, color: 'rgba(0,0,0,0.1)', offsetX: 0, offsetY: 2 })

// 透明度与可见性
.opacity(0.8)
.visibility(Visibility.Visible)

// 交互
.enabled(true)
.onClick(() => {})
.onTouch((event) => {})
```

---

## 跨文档参考

- [`v2-layout-patterns.md`](./v2-layout-patterns.md) — 6 种布局容器 V2 模板
- [`v2-prop-naming-rules.md`](./v2-prop-naming-rules.md) — V2 变量命名规则
- [`v2-responsive-design.md`](./v2-responsive-design.md) — V2 响应式设计
- [`v2-component-lifecycle-patterns.md`](./v2-component-lifecycle-patterns.md) — V2 生命周期与订阅
- `../SKILL.md` — V2 组件骨架
- `arkts-state-manager/references/v2-decorators.md` — V2 装饰器完整参考
