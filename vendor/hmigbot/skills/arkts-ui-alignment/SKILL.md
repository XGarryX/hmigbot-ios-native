---
name: arkts-ui-alignment
description: 将 Android UI 设计迁移到 ArkTS/HarmonyOS 的等价实现。当用户需要匹配 Android Material Design 视觉效果、把 Android 布局/控件映射到 ArkTS 等价物（含 SymbolGlyph 图标体系、颜色/间距/字号对齐）时触发。即使只说"还原这个安卓界面""图标怎么对应"也应触发。不适用于 ArkTS 原创组件设计（用 arkts-component-builder）。
metadata:
  type: domain
  domain: ui
  tags:
  - ui
  - android-migration
  - symbolglyph
  - material-design
---
# ArkTS UI Alignment — Android UI 迁移对齐

## API 版本

本 skill 基于 **API 12+**（HarmonyOS 5.0.0+）。UI 相关导入：

- ArkUI 组件：内置，无需额外导入
- SymbolGlyph：内置，资源引用 `$r('sys.symbol.xxx')`
- 弹窗：`import { promptAction } from '@kit.ArkUI'`

遇到版本兼容性或其他不确定的 ArkTS 知识点，参阅 arkts-knowledge-verifier skill。

---

## 生成约定：本项目锁 ArkUI V2

本 skill 的产物是**可运行的迁移页面**，一律用 **ArkUI V2** 声明式外壳（本 skill 讲的是视觉/控件对齐，不改这条）：

- 页面 struct = `@Entry @ComponentV2`（**不是** `@Component`）；状态用 `@Local`/`@Param`/`@Once`/`@Event`/`@Monitor`/`@Provider`/`@Consumer`（**绝不**用 V1 的 `@State`/`@Prop`/`@Link`/`@Watch`/`@Provide`/`@Consume`）。
- 本文档下方示例若出现 V1 装饰器，一律按 V2 改写；**映射/颜色/symbol/间距等对齐事实不变，只换装饰器外壳**。

```typescript
@Entry
@ComponentV2
struct Index {
  @Local selected: string = ''
  build() { /* 迁移后的 UI */ }
}
```

---

## Android → ArkTS 组件映射表

| Android 元素 | ArkTS 组件 | 备注 |
|-------------|-----------|------|
| `BottomNavigationView` | 自定义 `Row` + `@Builder tabBarItem` | 不用 `Tabs` 在 Navigation 内部 |
| `BottomSheetDialogFragment` | `NavDestination` (全屏) 或 `Sheet` | 视需求选择 |
| `DrawerLayout` | `SideBarContainer` | 侧边栏 |
| `RecyclerView` | `List` + `LazyForEach` | 虚拟列表 |
| `ViewPager2` | `Swiper` | 翻页 |
| `CoordinatorLayout` | `Stack` + 自定义手势 | 需手动实现 |
| `CardView` | `Column` + `borderRadius` + `shadow` | 卡片 |
| `FloatingActionButton` | `Button` + 绝对定位 | FAB |
| `ProgressBar` (Linear) | `Progress({ type: ProgressType.Linear })` | 进度条 |
| `ProgressBar` (Circular) | `Progress({ type: ProgressType.Ring })` | 进度环 |
| `Toolbar` / `ActionBar` | `NavDestination` 标题栏 | 自动 |
| `AlertDialog` | `getUIContext().getPromptAction().showDialog()` 或 CustomDialog | 弹窗（全局 `AlertDialog.show` 已废弃） |
| `PopupMenu` | `Menu` + `MenuItem` | 菜单 |
| `Snackbar` | `getUIContext().getPromptAction().showToast()` | 轻提示（全局 `promptAction.*` 已废弃） |
| `ImageView` + Glide | `Image(url)` 或 `@ohos/imageknife` | 图片加载 |
| `EditText` | `TextInput` / `TextArea`(多行) | 输入框 |
| `CheckBox` | `Checkbox` | 多选 |
| `RadioButton` + `RadioGroup` | `Radio`(同 group) | 单选 |
| `Switch` / `SwitchCompat` | `Toggle({ type: ToggleType.Switch })` | 开关 |
| `SeekBar` | `Slider` | 滑块 |
| `Spinner` | `Select` | 下拉选择 |
| `SwipeRefreshLayout` | `Refresh` | 下拉刷新 |

> 详细映射 + 代码示例见 `references/layout-mapping.md`

---

## SymbolGlyph 图标体系

### 已验证可用名称（编译验证通过，按类别速查）

以下名称经 DevEco Studio 真机编译验证**存在**，可直接 `$r('sys.symbol.<名>')` 使用：

- **导航/箭头**：`house` `chevron_left` `chevron_right` `chevron_up` `chevron_down` `arrow_left` `arrow_right` `arrow_up` `arrow_down` `arrow_2_circlepath`
- **列表/布局**：`list_bullet` `line_3_horizontal` `square_grid_2x2`
- **媒体控制**：`play_fill` `pause_fill` `playpause_fill` `backward_fill` `forward_end_fill` `backward_end_fill` `speaker_wave_2_fill` `mic` `mic_fill` `repeat` `repeat_1` `shuffle`
- **账户/隐私**：`person` `person_fill` `person_2` `lock` `eye` `eye_slash`（密码框显示/隐藏 = `eye` / `eye_slash`）
- **状态/标记**：`checkmark` `checkmark_circle` `checkmark_circle_fill` `xmark` `xmark_circle` `xmark_circle_fill` `plus` `plus_circle` `minus_circle` `info_circle` `exclamationmark_circle` `questionmark_circle`
- **常用操作**：`magnifyingglass` `trash` `gearshape` `envelope` `bell` `bell_fill` `heart` `heart_fill` `star` `star_fill` `bookmark` `bookmark_fill` `link` `paperplane` `paperplane_fill` `hand_thumbsup`
- **内容/时间**：`doc` `folder` `folder_fill` `calendar` `calendar_badge_plus` `clock` `camera` `camera_fill` `map` `flag` `bolt`
- **电商**：`cart` `cart_fill` `bag` `bag_fill` `gift` `gift_fill` `creditcard`
- **其它**：`wifi` `sun_max` `moon` `cloud`

### 已验证【不存在】+ 替代方案（编译报 `Unknown resource name`）

| 猜测名称（不存在） | 替代 |
|---|---|
| `forward_fill` | **`forward_end_fill`**（前进/下一首；`forward_fill` 本身不存在） |
| `ellipsis` / `dot_3_horizontal` | `line_3_horizontal` |
| `square_and_arrow_up`（分享） | `paperplane` / `paperplane_fill` |
| `tray_arrow_down` | `envelope` |
| `chart_bar` | `square_grid_2x2` |
| `eye_fill` / `eye_slash_fill` | `eye` / `eye_slash`（无 `_fill` 后缀） |
| `location` / `location_fill` | `map`（无 `location` 裸名） |
| `photo` | `doc` / `square_grid_2x2` |
| `music_note` | `speaker_wave_2_fill` |
| `tag` / `doc_fill` / `person_circle` / `slider_horizontal_3` | 改用上方已验证名 |

### 使用规范

```typescript
// 标准用法
SymbolGlyph($r('sys.symbol.house'))
  .fontSize(22)
  .fontColor([Color.Black])

// 条件颜色（选中/未选中）
SymbolGlyph($r('sys.symbol.play_fill'))
  .fontSize(20)
  .fontColor(this.isActive ? [Color.Black] : ['#99182431'])
```

**铁律**：
- 统一使用 `SymbolGlyph`；**绝不**把 Unicode emoji 或符号字（`♂` `♀` `✓` `★` 等）塞进 `Text` 当图标——那破坏视觉对齐、不是图标
- `fontColor` 参数是**数组**：`[Color.Black]` 不是 `Color.Black`
- **只用上方已验证清单里的名字**。图标不在清单时**按序回退**：① 清单里**语义最近的合法 symbol**（人物/性别→`person`/`person_fill`/`person_2`、搜索→`magnifyingglass`、分享→`paperplane`）→ ② 确需精确图形且工程自带矢量图才用 `Image` → ③ **绝不** emoji/Unicode 符号字，**绝不**凭猜发未验证 `sys.symbol.*`（编译必报 `Unknown resource name` 致整页失败；"先标 `[待验证]` 再发"挡不住）。
- ⚠️ 系统库**无**专用性别符号（`male`/`female`/`person_badge`/`figure_stand` probe 实证不存在）→ 性别男/女一律用通用 `person`/`person_2`（区分靠右侧文字标签），**别**回退 `Text('♂'/'♀')`。

### `ohos_` 前缀命名空间（HarmonyOS 原生图标）

除上面的裸名（源自 SF Symbols 命名体系）外，系统还预置一小撮 **`ohos_` 前缀**的鸿蒙原生图标。编译验证存在的有：`ohos_wifi` `ohos_lock` `ohos_trash` `ohos_star` `ohos_photo` `ohos_mic`。某些图标两种形并存（如 `wifi` 与 `ohos_wifi` 都可用）。**绝大多数常见动作没有 ohos_ 形**（`ohos_add`/`ohos_delete`/`ohos_settings`/`ohos_share`/`ohos_search`… 全部**不存在**，仍用裸名）。规则同上：**只用编译验证过的 `ohos_` 名**，不要凭猜造 `ohos_xxx`。遇到鸿蒙系统设置类页面的原生图标（WiFi/锁/相册等）可优先考虑对应 `ohos_` 名。

---

## 颜色系统映射

| Material 语义 | HarmonyOS 色值 | 用途 |
|-------------|---------------|------|
| primaryColor | `#007DFF` | 品牌蓝、主操作按钮 |
| surface | `#FAFAFA` | 卡片/面板背景 |
| background | `#FFFFFF` | 页面背景 |
| onSurface | `#182431` | 深色主文字 |
| onSurfaceVariant | `#99182431` | 次要文字（60% 不透明度） |
| divider | `#E0E0E0` | 分割线 |
| error | `#E84026` | 错误提示 |
| disabled | `#66182431` | 禁用态文字 |
| overlay | `#1A000000` | 蒙层/阴影（10% 黑） |
| pillBg | `#1F000000` | 药丸指示器背景（12% 黑） |

### 系统颜色资源

```typescript
// 推荐使用系统语义色（随深色模式自动切换）
$r('sys.color.ohos_id_color_text_primary')     // 主文字
$r('sys.color.ohos_id_color_text_secondary')   // 次要文字
$r('sys.color.ohos_id_color_background')       // 背景色
```

---

## 间距系统

采用 **4vp 基数**，保持视觉一致性：

| 级别 | 值 | 用途 |
|------|---|------|
| xs | 4vp | 紧凑间距 |
| sm | 8vp | 列表项内间距 |
| md | 12vp | 组件间距 |
| lg | 16vp | 区域间距、标准 padding |
| xl | 20vp | 大区域间距 |
| xxl | 24vp | 页面边距 |

```typescript
// 示例
Row() { ... }
  .padding({ left: 16, right: 16, top: 8, bottom: 8 })
  .margin({ top: 12 })
```

---

## Tab 栏方案

> **先分清两种 Tab，别一刀切**：下面"别把 `Tabs` 放进 `Navigation`"的告诫**只针对底部主导航 + Navigation 路由**这一种场景。**顶部分段切换（Android `TabLayout` + `ViewPager2`，不在 Navigation 内）应直接用原生 `Tabs`**，不要手搓 `Row` 页签 + `Swiper` 同步（那是回避、还原度差）：
>
> ```typescript
> Tabs({ barPosition: BarPosition.Start, index: this.idx }) {
>   TabContent() { FirstPage() }.tabBar('推荐')
>   TabContent() { SecondPage() }.tabBar('关注')
> }
> .onChange((i: number) => { this.idx = i })   // 点击/滑动双向同步由 Tabs 自带，无需自管手势
> ```
>
> 顶部三段式/中部分类 Tab = `Tabs({barPosition: BarPosition.Start}) + TabContent().tabBar(...)`；横向滚动多 Tab 加 `.barMode(BarMode.Scrollable)`。

### 问题：Tabs 在 Navigation 内部

`Tabs` 放在 `Navigation` 内部时，`NavDestination` 子页面会覆盖整个区域（包括 Tab 栏）。

### 解决方案：自定义 Tab 栏放在 Navigation 外部

```typescript
Column() {
  // 内容区（Navigation 占满剩余空间）
  Navigation(this.navPathStack) {
    // Tab 内容根据 currentTabIndex 切换
    if (this.currentTabIndex === 0) { HomeComponent() }
    else if (this.currentTabIndex === 1) { QueueComponent() }
    // ...
  }
  .navDestination(this.routerMap)
  .mode(NavigationMode.Stack)
  .layoutWeight(1)

  // MiniPlayer（Navigation 外部，不被覆盖）
  if (this.isPlayerVisible && !this.isFullPlayerVisible) {
    MiniPlayerArea()
  }

  // 自定义 Tab 栏（Navigation 外部，不被覆盖）
  if (!this.isFullPlayerVisible) {
    CustomTabBar()
  }
}
```

---

## 药丸指示器 Tab 样式

Material 3 风格的底部 Tab 栏（药丸形背景指示选中态）：

```typescript
@Builder
tabBarItem(index: number, title: Resource, icon: Resource) {
  Column() {
    // 药丸形背景
    Column() {
      SymbolGlyph(icon)
        .fontSize(22)
        .fontColor(this.currentTabIndex === index ?
          [Color.Black] : ['#99182431'])
    }
    .width(48)
    .height(28)
    .borderRadius(14)
    .backgroundColor(this.currentTabIndex === index ?
      '#1F000000' : '#00000000')
    .justifyContent(FlexAlign.Center)

    Text(title)
      .fontSize(10)
      .fontColor(this.currentTabIndex === index ?
        '#182431' : '#99182431')
      .margin({ top: 2 })
  }
  .layoutWeight(1)
  .justifyContent(FlexAlign.Center)
  .height('100%')
  .onClick(() => { this.currentTabIndex = index; })
}
```

> 完整代码见 `references/visual-patterns.md`

---

## 封面图 + Fallback 模式

网络图片 + 文字首字母占位符：

```typescript
if (this.coverUrl.length > 0) {
  Image(this.coverUrl)
    .width(40).height(40)
    .borderRadius(6)
    .objectFit(ImageFit.Cover)
} else {
  Column() {
    Text(this.title.length > 0 ?
      this.title.charAt(0).toUpperCase() : '?')
      .fontSize(18)
      .fontWeight(FontWeight.Bold)
      .fontColor(Color.White)
  }
  .width(40).height(40)
  .borderRadius(6)
  .backgroundColor('#BDBDBD')
  .justifyContent(FlexAlign.Center)
}
```

---

## 常见错误

### 1. Emoji vs SymbolGlyph 混用
```typescript
// ❌ emoji 大小不可控
Text('📋').fontSize(22)  // 实际渲染大小不确定

// ✓ SymbolGlyph 大小精确可控
SymbolGlyph($r('sys.symbol.list_bullet'))
  .fontSize(22)
  .fontColor([Color.Black])
```

### 2. 使用不存在的 symbol 名称
```typescript
// ❌ 编译报 Unknown resource name
SymbolGlyph($r('sys.symbol.tray_arrow_down'))

// ✓ 使用已验证的名称或查阅清单
SymbolGlyph($r('sys.symbol.envelope'))
```

### 3. Tabs 在 Navigation 内部
```typescript
// ❌ NavDestination 会覆盖 Tab 栏
Navigation() {
  Tabs() { ... }  // Tab 栏被子页面覆盖
}

// ✓ Tab 栏放在 Navigation 外部
Column() {
  Navigation() { ... }.layoutWeight(1)
  CustomTabBar()  // 始终可见
}
```

---

## 生成检查清单

- [ ] Android 组件已查对照表找到 ArkTS 等价物
- [ ] 图标统一使用 SymbolGlyph（不使用 emoji）
- [ ] Symbol 名称来自已验证清单
- [ ] 颜色使用 HarmonyOS 色值映射
- [ ] 间距使用 4vp 基数
- [ ] Tab 栏放在 Navigation 外部
- [ ] 封面图有 fallback 占位
- [ ] 没有使用 `any` 类型
- [ ] 导入使用 `@kit.*` 格式

---

## 跨 Skill 协作

| 需要什么 | 读取哪里 |
|---------|---------|
| UI 组件详细模板 | `arkts-component-builder/SKILL.md` |
| 导航方案 | `arkts-navigation-builder/SKILL.md` |
| 状态管理 | `arkts-state-manager/SKILL.md` |
| 动画效果 | `arkts-animation-builder/SKILL.md` |
| 业务功能模式 | `arkts-pattern-library/SKILL.md` |
| 验证 API | `arkts-knowledge-verifier/SKILL.md` |

> 完整路由矩阵见 `arkts-knowledge-verifier/references/skill-routing-guide.md`

---

## References

- `references/layout-mapping.md` — Android→ArkTS 组件映射详细版 + 代码示例 + 单位转换
- `references/visual-patterns.md` — 药丸 Tab 栏 + 封面 fallback + MiniPlayer + SymbolGlyph + 阴影卡片
- 遇到版本兼容性或其他不确定的 ArkTS 知识点，参阅 **arkts-knowledge-verifier** skill
