# iOS→ArkTS 布局映射参考

> 组件映射详细版 + 代码示例 + 布局对照 + 单位转换。

---

## 布局容器映射

### VStack / HStack / UIStackView → Column / Row

```swift
VStack {
  Text("标题")
  Button("操作", action: submit)
}
```

```typescript
// ArkTS 等价
Column() {
  Text('标题')
  Button('操作')
}
```

```swift
HStack {
  Image("icon")
  Text("标题")
}
```

```typescript
// ArkTS 等价
Row() {
  Image($r('app.media.icon'))
  Text('标题')
}
```

### ZStack / UIView 层叠 → Stack

> ⚠️ **陷阱（57 处实锤事故，2026-08-24）**：`.align()` 修饰符只对齐**组件自身内容**，
> **不能定位 Stack 子项**——未区分源 alignment 与目标定位语义就写 `Image(...).align(Alignment.End)`
> 会让子项按 Stack 的 alignContent 叠放（图标叠标题正中、按钮浮顶遮内容）。
> 子项定位只有三条路：全子统一 `Stack({alignContent})`、逐子 `RelativeContainer+alignRules`、
> 标题栏左中右 `Row+对称占位块`。`.align()` 唯一合法场景 = 子项已撑满
> （`layoutWeight(1)`/`height('100%')`）后钉自身内容。

```swift
ZStack(alignment: .bottom) {
  Image("cover")
  Text("叠加文字")
}
```

```typescript
// ArkTS 等价
Stack({ alignContent: Alignment.Bottom }) {
  Image($r('app.media.cover'))
  Text('叠加文字')
}
```

### 原生约束 → RelativeContainer 或组合布局（需逐项验证）

`RelativeContainer`（API 12+）可承接部分 NSLayoutConstraint / alignmentGuide 布局；优先保留实际约束、优先级和尺寸提案，不能视为完整直接等价：给子组件设 `id`，用 `alignRules` 相对锚定父容器（`'__container__'`）或兄弟组件。简单线性布局也可用 Column/Row 嵌套。

```typescript
RelativeContainer() {
  Image($r('app.media.cover')).width(60).height(60)
    .id('cover')
    .alignRules({
      top: { anchor: '__container__', align: VerticalAlign.Top },
      left: { anchor: '__container__', align: HorizontalAlign.Start }
    })
  Text(this.title).fontSize(16)
    .id('title')
    .alignRules({
      top: { anchor: 'cover', align: VerticalAlign.Top },
      left: { anchor: 'cover', align: HorizontalAlign.End }
    })
}

// 简单线性布局：Column + Row 嵌套即可
Column() {
  Row() {
    Image(this.coverUrl).width(60).height(60)
    Column() {
      Text(this.title).fontSize(16)
      Text(this.subtitle).fontSize(12).fontColor('#99000000')
    }.layoutWeight(1)
    Button('操作')
  }
}
```

### 实际原生左右/剩余空间约束 → Row / Column + layoutWeight

```typescript
// 左-中-右 布局
Row() {
  Image(icon).width(40)            // 左侧固定宽度
  Column() {                       // 中间填充剩余空间
    Text(title)
  }.layoutWeight(1)
  Text(time)                       // 右侧固定
}
```

---

## 列表组件映射

### SwiftUI List / UITableView / UICollectionView → List + LazyForEach

```swift
List(items) { item in
  ItemView(item: item)
}
```

```typescript
// ArkTS — 使用 LazyForEach 虚拟化
List() {
  LazyForEach(this.dataSource, (item: ItemModel) => {
    ListItem() {
      ItemComponent({ item: item })
    }
  }, (item: ItemModel) => item.id.toString())
}
```

### SwiftUI Grid / UICollectionView 网格 → Grid

```typescript
Grid() {
  ForEach(this.items, (item: ItemModel) => {
    GridItem() {
      ItemComponent({ item: item })
    }
  })
}
.columnsTemplate('1fr 1fr 1fr')  // 3 列等分
.rowsGap(8)
.columnsGap(8)
```

---

## 交互组件映射

### TabView / UITabBarController → Tabs 或已批准的自定义 Row

```typescript
// 不要用 Tabs 在 Navigation 内部！
Row() {
  this.tabBarItem(0, $r('app.string.home'), $r('sys.symbol.house'))
  this.tabBarItem(1, $r('app.string.queue'), $r('sys.symbol.list_bullet'))
  this.tabBarItem(2, $r('app.string.inbox'), $r('sys.symbol.envelope'))
}
.width('100%')
.height(56)
.backgroundColor(Color.White)
.border({ width: { top: 0.5 }, color: '#E0E0E0' })
```

### 实际原生侧栏 → SideBarContainer

```typescript
SideBarContainer(SideBarContainerType.Embed) {
  // 侧边栏内容
  Column() { ... }
  // 主内容
  Column() { ... }
}
.showSideBar(this.showSidebar)
.sideBarWidth(280)
```

### 分页 TabView / UIPageViewController → Swiper

```typescript
Swiper() {
  ForEach(this.pages, (page: PageModel) => {
    PageComponent({ data: page })
  })
}
.index(this.currentPage)
.indicator(true)
```

### 实际原生卡片组合 → Column + 圆角 + 阴影

```typescript
Column() {
  // 卡片内容
}
.borderRadius(12)
.backgroundColor(Color.White)
.shadow({ radius: 4, color: '#1A000000', offsetY: 2 })
.padding(16)
```

### 实际 SwiftUI alert / UIAlertController → getUIContext().getPromptAction().showDialog

```typescript
// ⚠️ 全局 AlertDialog.show() 已废弃，V2 用 UIContext 形式
const res = await this.getUIContext().getPromptAction().showDialog({
  title: '确认删除',
  message: '删除后不可恢复',
  buttons: [
    { text: '取消', color: '#666666' },
    { text: '删除', color: '#E84026' }
  ]
});
if (res.index === 1) { this.doDelete(); }
```
> 自定义内容弹窗见 `arkts-component-builder/references/v2-dialogs-and-sheets.md`。

### 实际源 Toast 语义（含操作按钮时不能只替换文本）→ getUIContext().getPromptAction().showToast

```typescript
// ⚠️ 全局 promptAction.showToast 已废弃，V2 用 UIContext 形式
this.getUIContext().getPromptAction().showToast({
  message: '操作成功',
  duration: 2000
});
```

---

## 文本与表单控件映射

| iOS | ArkUI | 说明 |
|---|---|---|
| `Text / UILabel` | `Text` | 实际本地化文本 → `Text('...')`；`textColor/textSize` → `.fontColor()/.fontSize()` |
| `TextField / UITextField` | `TextInput` | 实际 placeholder、输入类型、编辑与提交回调 |
| `TextEditor / UITextView` | `TextArea` | 保留多行、选择和编辑行为 |
| 原生勾选/单选组合 | `Checkbox / Radio` | SwiftUI Binding 或 UIKit 事件驱动；实际状态语义逐项保留 |
| `Toggle / UISwitch` | `Toggle({ type: ToggleType.Switch })` | 实际选中状态与变更回调 |
| `Slider / UISlider` | `Slider` | 实际范围、步长、拖动阶段与值 |
| `Picker / UIPickerView` | `Select` 或已批准的自定义选择器 | 核对选项、选择与展开方式，不假定视觉等价 |
| `refreshable / UIRefreshControl` | `Refresh` | 保留刷新完成、错误和取消 |
| `Image / UIImageView` | `Image` | 实际资源/网络来源、内容模式、尺寸和真实 scale |

> 控件完整 V2 模板：`arkts-component-builder/references/v2-scroll-and-form-components.md`（TextArea/Checkbox/Radio）、`v2-common-components.md`（TextInput/Toggle/Slider/Select）。

### refreshable / UIRefreshControl → Refresh

```typescript
Refresh({ refreshing: $$this.isRefreshing }) {   // $$ 双向绑定
  List() { /* 列表内容 */ }
}.onRefreshing(() => { this.reload().then(() => { this.isRefreshing = false; }); })
```

---

## 进度指示器映射

### 确定进度 ProgressView / UIProgressView

```typescript
Progress({ value: this.percent, total: 100, type: ProgressType.Linear })
  .height(2)
  .width('100%')
  .color('#007DFF')
  .backgroundColor('#E0E0E0')
```

### 原生环形/不确定进度

```typescript
Progress({ value: this.percent, total: 100, type: ProgressType.Ring })
  .width(32)
  .height(32)
  .color('#007DFF')
  .style({ strokeWidth: 3 })
```

---

## 单位转换

| iOS | ArkTS | 说明 |
|---------|-------|------|
| 源布局 points / NSLayoutConstraint | vp | 按真实规格和设备尺度核对，不从图片倍率换算布局 |
| UIFont/SwiftUI 字体尺寸与动态字体 | fp / 实际字体策略 | 保留字体资源、行高、字重与动态缩放决策 |
| 图片或截图 pixels | 实际资源/显示尺寸 | 结合逐图 scale 和观测 units，不按统一密度猜测 |

以下仅为目标布局示例，数值必须从本轮源规格取得：

```typescript
// ArkTS：数字就是 vp
Text('标题')
  .fontSize(16)   // 示例值，取真实字体规格
  .margin({ top: 8 })  // 示例值，取真实间距规格
```

原生单位口径：源码 frame/约束的 point 数值以 1 point → 1 vp 作为布局基准，视口适配按本轮规格处理；字体 point 数值按目标 fp/动态字体策略核对。不得把 points 当 pixels 后再除设备密度。仅原始图片/截图 pixels 按真实逐图 scale 或观测坐标单位换算，不使用默认倍率。目标引擎常量不改，图片守卫仍拒收无源证据的尺寸自愈。
