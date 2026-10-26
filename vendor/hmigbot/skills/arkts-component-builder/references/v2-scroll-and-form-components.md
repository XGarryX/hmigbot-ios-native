# V2 高频组件：滚动容器 + 表单控件

> 补 `v2-layout-patterns.md`（Column/Row/Stack/Flex/Grid/List）与 V1-Legacy `common-components.md` 之外的高频组件。**经 harmony-docs（快照 2026-05-24）核验**，全部用 @ComponentV2 + @Local 状态。

---

## 一、滚动 / 容器族

### 1. Scroll —— 单子组件可滚动容器

```typescript
@ComponentV2
struct ScrollDemo {
  scroller: Scroller = new Scroller()
  build() {
    Scroll(this.scroller) {
      Column() { /* 唯一子组件；内容超出即可滚动 */ }
    }
    .scrollable(ScrollDirection.Vertical)   // Vertical / Horizontal
    .scrollBar(BarState.Auto)
    .onScroll((xOff: number, yOff: number) => { /* 滚动监听 */ })
    // 控制：this.scroller.scrollEdge(Edge.Top) / scrollTo({ xOffset: 0, yOffset: 200 })
  }
}
```
> Scroll **只能有一个直接子组件**（通常 Column/Row）。长列表用 `List`+`LazyForEach`，不要用 Scroll 套 ForEach。

### 2. WaterFlow —— 瀑布流（不等高卡片，如图片/笔记流）

```typescript
@ObservedV2
class NoteItem {
  id: string = ''
  @Trace title: string = ''
  @Trace cover: string = ''
  @Trace ratio: number = 1   // 图片宽高比，驱动 aspectRatio 确定高度
}

WaterFlow() {
  LazyForEach(this.dataSource, (item: NoteItem) => {
    FlowItem() {
      Column() {
        // 图片必须有可确定的高度：用 aspectRatio 绑比例字段
        Image(item.cover).width('100%').aspectRatio(item.ratio)
        Text(item.title)
      }
    }.width('100%')
  }, (item: NoteItem) => item.id)
}
.columnsTemplate('1fr 1fr')      // 两列
.columnsGap(8).rowsGap(8)
.cachedCount(5)
```
> 子项必须是 `FlowItem`；数据源用 `LazyForEach`/`Repeat` + `IDataSource`（见 arkts-data-layer）。
> **WaterFlow 的 FlowItem 子项（尤其图片）必须有可确定的高度**（`.aspectRatio` 绑比例字段，或 `.height()` 绑 `@Local` + `onComplete` 动态算）；靠 Image 自动撑开会让 WaterFlow 感知不到高度→重叠错位。仅有 URL、比例未知时：`@Local imgH: number = 0` + `Image(url).height(this.imgH || 120).onComplete((e) => { if (e) this.imgH = /* 按 e.width/e.height 与列宽算高 */ })`。

### 3. Refresh —— 下拉刷新容器

```typescript
@ComponentV2
struct RefreshDemo {
  @Local isRefreshing: boolean = false
  build() {
    Refresh({ refreshing: $$this.isRefreshing }) {   // $$ 双向绑定 refreshing
      List() { /* ... */ }
    }
    .onRefreshing(() => {
      this.loadData().then(() => { this.isRefreshing = false })  // 完成后必须回写 false
    })
  }
  loadData(): Promise<void> { return Promise.resolve() }
}
```
> 支持 `promptText` 自定义文案、`builder` 自定义刷新头。上拉加载更多用 `List.onReachEnd`。

### 3.5 嵌套滚动 nestedScroll —— 内层可滚动嵌在外层滚/滑容器里（手势优先级）

**何时必须配**：当一个可滚动组件（List / Scroll / Grid / WaterFlow）**嵌在另一个会滚动或翻页的容器里**（Swiper / Tabs / 外层 Scroll / 父 List），且希望**内层先响应手势**时，内层必须显式设 `.nestedScroll(...)`。Android 会自动分发触摸手势，HarmonyOS 不会——不配则**外层容器直接吃掉内层滚动手势**（例：Swiper 内嵌横向 List，横滑会翻页而不是滚 List）。

```typescript
// 内层横向 List 嵌在外层 Swiper 里：让 List 先横滑，滑到边缘再交给 Swiper 翻页
@ComponentV2
struct CategoryStrip {
  @Param categories: CategoryItem[] = []
  @Event onTap: (id: string) => void = () => {}
  build() {
    List({ space: 8 }) {
      ForEach(this.categories, (item: CategoryItem) => {
        ListItem() { /* 分类项 */ }
      }, (item: CategoryItem) => item.id)
    }
    .listDirection(Axis.Horizontal)          // 横向滚动
    .nestedScroll({                          // 关键：内层先滚，边缘再让父组件动
      scrollForward:  NestedScrollMode.SELF_FIRST,
      scrollBackward: NestedScrollMode.SELF_FIRST
    })
    .width('100%').height(84)
    .scrollBar(BarState.Off)
    .edgeEffect(EdgeEffect.Spring)
  }
}

// 外层 Swiper 直接放各页子组件（第一页内嵌上面的横向 List）
Swiper() {
  FirstBanner({ categories: this.categories })   // 内含 CategoryStrip
  PlainBanner()
}
.loop(true).width('100%').height(200)
```

**NestedScrollMode 四值**（`SystemCapability.ArkUI.ArkUI.Full`，API 10+）：

| 值 | 含义 |
|---|---|
| `SELF_FIRST` (1) | 自身先滚动，自身滚到边缘后父组件才滚（**内层优先，最常用**） |
| `SELF_ONLY` (0) | 只自身滚，不与父联动（默认值） |
| `PARENT_FIRST` (2) | 父组件先滚，父滚到边缘后自身才滚 |
| `PARALLEL` (3) | 自身与父组件同时滚 |

> `scrollForward` / `scrollBackward` 是 `NestedScrollOptions` 的两个方向字段（向前 / 向后），通常同设 `SELF_FIRST`。同理适用「竖向 List 嵌在外层 Scroll 里」「List 嵌 Tabs 内容页」等场景——内层想先滚就配 `SELF_FIRST`。⚠️ 内层内容比自身还小、且 `edgeEffect` 未开 `alwaysEnabled` 时内层不产生滑动手势，`nestedScroll` 不生效、手势归父组件。

### 4. RelativeContainer —— 约束布局（锚点对齐，替代深层嵌套）

```typescript
RelativeContainer() {
  Text('标题').id('title')
    .alignRules({
      top:  { anchor: '__container__', align: VerticalAlign.Top },
      start:{ anchor: '__container__', align: HorizontalAlign.Start }
    })
  Text('副标题')
    .alignRules({ top: { anchor: 'title', align: VerticalAlign.Bottom } })  // 锚到 title 下方
}.width('100%').height(120)
```
> `__container__` 指父容器；其余用兄弟组件的 `.id()`。适合复杂相对定位，避免 Stack/Column 多层套。

---

## 二、表单控件族

### 5. TextArea —— 多行输入

```typescript
@ComponentV2
struct TextAreaDemo {
  @Local content: string = ''
  build() {
    TextArea({ text: this.content, placeholder: '请输入内容…' })
      .onChange((v: string) => { this.content = v })
      .maxLength(200)
      .height(120)
  }
}
```
> 单行输入用 `TextInput`（见 common-components.md）；TextArea 自动换行、可设高度。

### 6. Checkbox / CheckboxGroup —— 多选

```typescript
@ComponentV2
struct CheckDemo {
  @Local a: boolean = false
  @Local b: boolean = false
  build() {
    Column() {
      // 全选控制器（可选）
      CheckboxGroup({ group: 'g1' })
        .onChange((r: CheckboxGroupResult) => { /* r.status / r.name */ })
      Checkbox({ name: 'a', group: 'g1' }).select(this.a)
        .onChange((on: boolean) => { this.a = on })
      Checkbox({ name: 'b', group: 'g1' }).select(this.b)
        .onChange((on: boolean) => { this.b = on })
    }
  }
}
```
> 同 `group` 的 Checkbox 由同名 CheckboxGroup 统一管理（全选/反选）；回调签名 `(value: boolean)`。

### 7. Radio —— 单选

```typescript
@ComponentV2
struct RadioDemo {
  @Local selected: string = 'opt1'
  build() {
    Row() {
      Radio({ value: 'opt1', group: 'r1' }).checked(this.selected === 'opt1')
        .onChange((on: boolean) => { if (on) this.selected = 'opt1' })
      Radio({ value: 'opt2', group: 'r1' }).checked(this.selected === 'opt2')
        .onChange((on: boolean) => { if (on) this.selected = 'opt2' })
    }
  }
}
```
> 同 `group` 的 Radio 互斥；用一个 `@Local selected` 记录当前值，`checked` 绑定比较结果。

## 关键规则

- **Scroll 单子组件**；长列表/瀑布流用 `List`/`WaterFlow` + `LazyForEach`，不要 Scroll 套大 ForEach。
- **嵌套滚动**：可滚动组件（List/Scroll/Grid/WaterFlow）嵌在外层滚/滑容器（Swiper/Tabs/Scroll/父 List）里、想内层先响应时，内层**必须**配 `.nestedScroll({ scrollForward: NestedScrollMode.SELF_FIRST, scrollBackward: NestedScrollMode.SELF_FIRST })`；不配则外层吃掉内层手势（如 Swiper 内嵌横向 List 会翻页而非滚 List）。
- **List 横向滚动用链式 `.listDirection(Axis.Horizontal)`**，`listDirection` 不是构造器参数（`List({...})` 只接 `space/initialIndex/scroller`）。
- **WaterFlow FlowItem 子项（尤其图片）必须有可确定高度**（`.aspectRatio` 绑比例，或 `.height()` 绑 `@Local`+`onComplete`）；靠 Image 自动撑开会重叠错位。
- **Refresh `refreshing` 用 `$$` 双向绑定**，`onRefreshing` 完成后必须把状态回写 `false`。
- **表单控件状态用 `@Local`**；同组用相同 `group` 名；Radio 用单一 `selected` 值驱动 `checked`。
- 选择类组件（Toggle/Slider/Select/Rating）见 `common-components.md`；这里只补它缺的 TextArea/Checkbox/Radio。
