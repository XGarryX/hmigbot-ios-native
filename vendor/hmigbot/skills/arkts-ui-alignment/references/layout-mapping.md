# Android→ArkTS 布局映射参考

> 组件映射详细版 + 代码示例 + 布局对照 + 单位转换。

---

## 布局容器映射

### LinearLayout → Column / Row

```xml
<!-- Android 垂直布局 -->
<LinearLayout android:orientation="vertical">
  <TextView ... />
  <Button ... />
</LinearLayout>
```

```typescript
// ArkTS 等价
Column() {
  Text('标题')
  Button('操作')
}
```

```xml
<!-- Android 水平布局 -->
<LinearLayout android:orientation="horizontal">
  <ImageView ... />
  <TextView ... />
</LinearLayout>
```

```typescript
// ArkTS 等价
Row() {
  Image($r('app.media.icon'))
  Text('标题')
}
```

### FrameLayout → Stack

> ⚠️ **陷阱（57 处实锤事故，2026-08-24）**：`.align()` 修饰符只对齐**组件自身内容**，
> **不能定位 Stack 子项**——按安卓 gravity 直觉写 `Image(...).align(Alignment.End)`
> 会让子项按 Stack 的 alignContent 叠放（图标叠标题正中、按钮浮顶遮内容）。
> 子项定位只有三条路：全子统一 `Stack({alignContent})`、逐子 `RelativeContainer+alignRules`、
> 标题栏左中右 `Row+对称占位块`。`.align()` 唯一合法场景 = 子项已撑满
> （`layoutWeight(1)`/`height('100%')`）后钉自身内容。

```xml
<!-- Android 帧布局（层叠） -->
<FrameLayout>
  <ImageView ... />
  <TextView android:gravity="bottom|center" ... />
</FrameLayout>
```

```typescript
// ArkTS 等价
Stack({ alignContent: Alignment.Bottom }) {
  Image($r('app.media.cover'))
  Text('叠加文字')
}
```

### ConstraintLayout / RelativeLayout → RelativeContainer（直接等价）

`RelativeContainer`（API 12+）是 ConstraintLayout 的直接等价物：给子组件设 `id`，用 `alignRules` 相对锚定父容器（`'__container__'`）或兄弟组件。简单线性布局也可用 Column/Row 嵌套。

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

### RelativeLayout → Row / Column + layoutWeight

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

### RecyclerView → List + LazyForEach

```java
// Android
RecyclerView recyclerView = findViewById(R.id.list);
recyclerView.setAdapter(new MyAdapter(items));
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

### GridView → Grid

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

### BottomNavigationView → 自定义 Row

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

### DrawerLayout → SideBarContainer

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

### ViewPager2 → Swiper

```typescript
Swiper() {
  ForEach(this.pages, (page: PageModel) => {
    PageComponent({ data: page })
  })
}
.index(this.currentPage)
.indicator(true)
```

### CardView → Column + 圆角 + 阴影

```typescript
Column() {
  // 卡片内容
}
.borderRadius(12)
.backgroundColor(Color.White)
.shadow({ radius: 4, color: '#1A000000', offsetY: 2 })
.padding(16)
```

### AlertDialog → getUIContext().getPromptAction().showDialog

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

### Snackbar → getUIContext().getPromptAction().showToast

```typescript
// ⚠️ 全局 promptAction.showToast 已废弃，V2 用 UIContext 形式
this.getUIContext().getPromptAction().showToast({
  message: '操作成功',
  duration: 2000
});
```

---

## 文本与表单控件映射

| Android | ArkUI | 说明 |
|---|---|---|
| `TextView` | `Text` | `android:text` → `Text('...')`；`textColor/textSize` → `.fontColor()/.fontSize()` |
| `EditText`（单行） | `TextInput` | `hint`→`placeholder`；`inputType`→`.type(InputType.*)`；`onTextChanged`→`.onChange()` |
| `EditText`（`textMultiLine`） | `TextArea` | 自动换行、可设高度 |
| `CheckBox` | `Checkbox` | `isChecked`→`.select()`；`OnCheckedChange`→`.onChange((on:boolean)=>{})` |
| `RadioButton` + `RadioGroup` | `Radio`（同 `group`） | 用一个 `selected` 值驱动各 `.checked()` |
| `Switch` / `SwitchCompat` | `Toggle({ type: ToggleType.Switch })` | `.onChange((on:boolean)=>{})` |
| `SeekBar` | `Slider` | `progress`→`value`；`max`→`max`；`.onChange((v,mode)=>{})` |
| `Spinner` | `Select` | 选项数组 → `Select([{ value: '...' }])`；`.onSelect((i,v)=>{})` |
| `SwipeRefreshLayout` | `Refresh` | 见下 |
| `ImageView` | `Image` | `src`→`Image($r('app.media.x'))`；`scaleType`→`.objectFit(ImageFit.*)` |

> 控件完整 V2 模板：`arkts-component-builder/references/v2-scroll-and-form-components.md`（TextArea/Checkbox/Radio）、`v2-common-components.md`（TextInput/Toggle/Slider/Select）。

### SwipeRefreshLayout → Refresh

```typescript
Refresh({ refreshing: $$this.isRefreshing }) {   // $$ 双向绑定
  List() { /* 列表内容 */ }
}.onRefreshing(() => { this.reload().then(() => { this.isRefreshing = false; }); })
```

---

## 进度指示器映射

### ProgressBar (Linear)

```typescript
Progress({ value: this.percent, total: 100, type: ProgressType.Linear })
  .height(2)
  .width('100%')
  .color('#007DFF')
  .backgroundColor('#E0E0E0')
```

### ProgressBar (Circular / Ring)

```typescript
Progress({ value: this.percent, total: 100, type: ProgressType.Ring })
  .width(32)
  .height(32)
  .color('#007DFF')
  .style({ strokeWidth: 3 })
```

---

## 单位转换

| Android | ArkTS | 说明 |
|---------|-------|------|
| dp | vp | 1:1 对应，density-independent pixels |
| sp | fp | 字体大小，但 ArkTS 中通常直接用 vp |
| px | px | 物理像素（不推荐） |

ArkTS 中数值默认单位为 vp，直接使用数字即可：

```typescript
// ArkTS：数字就是 vp
Text('标题')
  .fontSize(16)   // 16vp，等同于 Android 16sp
  .margin({ top: 8 })  // 8vp，等同于 Android 8dp
```
