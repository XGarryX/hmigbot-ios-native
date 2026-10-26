---
name: arkts-component-builder
description: 生成 ArkTS/HarmonyOS 声明式 UI 组件代码（V2 优先，API 12+）。当用户需要创建页面、编写组件、设计布局（Column/Row/Stack/Grid/List/Flex）、创建自定义组件、编写 ForEach/LazyForEach/Repeat 列表、处理响应式断点适配、实现卡片/列表/表单/弹窗等 UI 元素、或生成任何 .ets UI 代码时，务必触发此 skill。即使只说"帮我写个页面""做个界面"也应触发。完整业务功能（搜索/登录/列表详情页）优先 arkts-pattern-library；页面导航/路由用 arkts-navigation-builder。
metadata:
  type: domain
  domain: ui
  tags:
  - ui
  - component
  - arkts-v2
  - declarative
---
# ArkTS Component Builder — UI 组件生成器（V2 优先）

## API 版本与项目策略

本 skill 的代码模板基于 **API 12+（HarmonyOS 5.0.0+）和 ArkTS V2 装饰器体系**。

> **项目锁 V2**：本项目所有新生成的 UI 组件代码使用 V2 装饰器（`@ComponentV2 / @Local / @Param / @Event / @Once / @Provider / @Consumer / @ObservedV2 / @Trace / @ReusableV2 / AppStorageV2 / PersistenceV2`）。`@Builder / @BuilderParam / @Styles / @Extend / @Entry` 在 V1/V2 通用，仍可使用。如需 V1 兼容写法查阅，参阅 `references/common-components.md / layout-patterns.md / responsive-design.md / media-app-components.md / component-lifecycle-patterns.md / prop-naming-rules.md` 等 V1 历史文档（已加 legacy 标识）。

V2 vs V1 关键差异（UI 视角）：

| V1 装饰器 | V2 等价 | 备注 |
|---|---|---|
| `@Component` | `@ComponentV2` | struct 装饰器，UI 组件必须用 V2 |
| `@State` | `@Local` | 组件内部状态 |
| `@Prop`（单向只读） | `@Param + @Once` | V2 显式标记不可改 |
| `@Prop`（单向可改） | `@Param`（不带 `@Once`） | 子组件可改本地副本 |
| `@Link`（双向） | **没有直接等价** — `@Param + @Event` 回调 | V2 强调单向数据流 + 事件 |
| `@Provide / @Consume` | `@Provider() / @Consumer()` | 必须带括号，`@Consumer` 必须给默认值 |
| `@Observed + @ObjectLink` | `@ObservedV2 + @Trace` 属性，传递时直接 `@Param` | V2 简化对象引用 |
| `@StorageLink / @StorageProp` | `AppStorageV2.connect(Cls, key, () => new Cls())` | 配合 `@ObservedV2` 类 |
| `@Watch` | `@Monitor('propName')` | V2 是方法装饰器 |
| `@Reusable` | `@ReusableV2` | 长列表组件复用 |
| `@Builder / @BuilderParam / @Styles / @Extend / @Entry` | 不变 | V1/V2 通用 |

- 使用 `@kit.*` 导入（不要用 `@ohos.*`）
- 使用 Navigation 导航（不要用 `@ohos.router`）
- `@Param` 必须有默认值（V2 强制）
- 遇到版本兼容性或其他不确定的 ArkTS 知识点（如属性、语法、权限等），参阅 arkts-knowledge-verifier skill

---

## 输入模式

### 模式 A: 描述驱动（默认）

输入: 文字描述 + 可选 design tokens
输出: ArkTS 组件代码（V2）
适用: 新建轨、无 Android 参考的组件

### 模式 B: Android 源码参照（精细迁移）

输入:
  - android_layout: XML 布局文件路径（必须）— Agent 必须先 Read 此文件
  - android_class: Java/Kotlin 类文件路径（必须）— Agent 必须先 Read 此文件
  - design_tokens: 共享样式常量路径（可选）— 来自 ui-framework Task 的产出

执行规则:
  1. **先读后写**: 必须先 Read android_layout 和 android_class 的完整内容，禁止跳过
  2. **提取属性**: 从 XML 中提取所有 View 及其属性（尺寸、间距、颜色、字号、圆角、阴影、可见性）
  3. **组件映射**: 按以下对照表逐组件转写:
     - FrameLayout → Stack
     - LinearLayout (vertical) → Column
     - LinearLayout (horizontal) → Row
     - RelativeLayout / ConstraintLayout → RelativeContainer 或 Column+Row 组合
     - RecyclerView (horizontal) → List(){...}.listDirection(Axis.Horizontal)（`listDirection` 是链式属性，不是构造器参数）
     - RecyclerView (vertical) → List + LazyForEach（V2 推荐 `Repeat`）
     - CardView → Column + .borderRadius() + .shadow()
     - ImageView → Image
     - TextView → Text
     - ProgressBar (linear) → Progress({ type: ProgressType.Linear })
     - ProgressBar (circular) → Progress({ type: ProgressType.Ring })
     - SwipeRefreshLayout → Refresh
  4. **属性转换**: dp → vp (1:1), sp → fp (1:1), 颜色值直接复制, match_parent → '100%', wrap_content → 默认
  5. **共享 tokens**: 如提供 design_tokens 路径，必须使用其中定义的常量而非硬编码
  6. **交互保持**: onClick → .onClick(), onLongClick → LongPressGesture, SwipeAction 保留

### SymbolGlyph 图标预验证

生成 UI 代码前，如果需要使用系统图标：
1. 读取 arkts-knowledge-verifier/references/verified-symbols.md 获取已验证名称列表
2. 只使用列表中的名称，不要猜测或创造新名称
3. 如果 Android 对应图标在验证列表中找不到等价物，使用最接近的替代或使用自定义图片资源

已知不存在的常见名称: music_note (用 music), doc_on_doc (用 list_bullet), copy (用 checkmark), tray_fill (用 envelope), square_and_arrow_up (用 share)

适用: 精细迁移轨（轨道 0）的页面框架和组件生成

触发判断: 当 task 包含 android_layout 或 android_source 字段时，自动使用模式 B

---

## 核心约束

ArkTS 的声明式 UI 与 React/Flutter 表面相似，但有本质差异。以下约束是 LLM 最容易忽略的：

### 1. struct 不是 class

```typescript
// 错误 — LLM 常犯：把 @ComponentV2 写成 class
@ComponentV2
class MyComponent { ... }

// 正确 — 必须用 struct
@ComponentV2
struct MyComponent {
  build() { ... }
}
```

**为什么**：ArkTS 的 `@ComponentV2`（V1 是 `@Component`）只能装饰 struct。struct 是值类型，由框架管理生命周期，不能用 new 实例化。

### 2. build() 内只放 UI 描述，不放逻辑语句

```typescript
// 错误 — build() 里写了 let、变量声明、console.log
build() {
  let name = this.user.name  // 不允许
  console.log('rendering')    // 不允许
  Column() {
    Text(name)
  }
}

// 正确 — 逻辑写成方法或 @Computed 属性，build() 只描述 UI 树
build() {
  Column() {
    Text(this.getUserName())
    if (this.isLoggedIn) {  // if 可以用于条件渲染
      Text('Welcome')
    }
  }
}
```

**为什么**：build() 是 UI 描述函数，框架会多次调用它来重建 UI 树。只有条件渲染（if/else）和循环渲染（ForEach / LazyForEach / Repeat）是允许的控制流。

### 3. 单根节点规则

```typescript
// 错误 — 多个根节点
build() {
  Text('Hello')
  Text('World')
}

// 正确 — 单个根容器
build() {
  Column() {
    Text('Hello')
    Text('World')
  }
}
```

### 4. 链式属性调用

```typescript
// ArkTS 属性是在组件后面链式调用的
Text('Hello')
  .fontSize(16)
  .fontColor('#333')
  .fontWeight(FontWeight.Bold)
  .margin({ top: 8 })
```

### 5. V2 不可与 V1 装饰器混用

```typescript
// 错误 — V2 项目中混入 V1 装饰器
@ComponentV2
struct Page {
  @State count: number = 0   // ❌ V1 @State 不能用在 @ComponentV2 中
  @Prop title: string = ''   // ❌ V1 @Prop 不能用
}

// 正确 — V2 全套
@ComponentV2
struct Page {
  @Local count: number = 0   // ✓
  @Param @Once title: string = ''  // ✓
}
```

---

## 标准组件骨架（V2）

> **MUST**：生成页面/组件骨架前，先读 `references/v2-codegen-patterns.md` §标准组件骨架 —— @Entry/@ComponentV2 页面、自定义组件、容器骨架模板。

---

## 布局选型决策树

根据 UI 需求选择容器：

```
需要什么布局？
│
├─ 垂直排列子元素 → Column
├─ 水平排列子元素 → Row
├─ 子元素重叠/覆盖 → Stack
├─ 等间距均分空间 → Flex（配合 justifyContent）
├─ 固定行列的网格 → Grid + GridItem
│   └─ columnsTemplate: '1fr 1fr 1fr'（3列等宽）
├─ 滚动长列表 → List + ListItem
│   ├─ <20 项 → ForEach
│   ├─ ≥20 项 → LazyForEach + IDataSource
│   └─ V2 大列表新选择 → Repeat（配合 .virtualScroll）
└─ 轮播/翻页 → Swiper
```

### 常用布局属性速查

```typescript
// Column/Row 主轴与交叉轴
Column() { /* ... */ }
  .justifyContent(FlexAlign.Center)    // 主轴居中
  .alignItems(HorizontalAlign.Start)   // 交叉轴左对齐

Row() { /* ... */ }
  .justifyContent(FlexAlign.SpaceBetween) // 两端对齐
  .alignItems(VerticalAlign.Center)       // 垂直居中

// 通用尺寸
.width('100%')
.height(200)
.padding({ left: 16, right: 16 })
.margin({ top: 12 })

// Stack 对齐
Stack({ alignContent: Alignment.BottomEnd }) { /* ... */ }

// Grid 模板
Grid() { /* ... */ }
  .columnsTemplate('1fr 1fr')        // 2列等宽
  .rowsGap(12)
  .columnsGap(12)
```

---

## @Builder / @Styles / @Extend 复用

> **MUST**：复用 UI 片段前，先读 `references/v2-codegen-patterns.md` §@Builder —— @Builder / @BuilderParam / @Styles / @Extend / **wrapBuilder（运行时按数据选排版）** 完整模板，含「自定义组件尾随闭包后不能链式通用属性」「`.builder()` 调用头不能是方法调用结果」两个编译期硬坑。
>
> **⚠️ 响应式硬规矩**：动态状态（会随 @Local/@Trace 变化、期望 UI 跟着刷新的值）**绝不能作 @Builder 的「值参」传入**——@Builder 默认按值传递，值参是调用时刻的快照，状态再变也定格首帧不刷新（尤其把 `@Trace` 对象的 number/string **属性值**当值参传，同样是快照、不刷新）。改法：@Builder 内直读 `this.` 上的状态（静态标签才走值参）／抽 @ComponentV2 子组件用 `@Param` 接动态值／单一对象字面量引用传递（仅单参有效）。完整 WRONG-vs-CORRECT 对照见 `references/v2-codegen-patterns.md` §@Builder「动态状态不能作值参」。静态字面量走值参不受此限。

---

## ForEach / LazyForEach / Repeat 选型

| 场景 | 选用 |
|---|---|
| 静态/少量数据（<20 项） | ForEach |
| 大量数据（≥20 项） | LazyForEach（按需渲染） |
| API 12+ 新项目 | Repeat（V2 推荐，复用更优） |

> **MUST**：完整列表模板见 `references/v2-layout-patterns.md`（含 Repeat、List+ListItem、Grid+GridItem）。
>
> **MUST（内置容器表达不了的测量/摆放）**：需自定义测量/摆放（按列累计高、排满隐藏、精确接管子尺寸等）时，先读 `references/v2-layout-patterns.md` §7 自定义布局 —— `onMeasureSize`/`onPlaceChildren` 成对实现完整模板 + 四条硬规则（**约束字段是 `Length` 须 `as number` 收窄**、build() 仅 `this.content()`、布局内禁 Repeat/LazyForEach 用 ForEach、加属性套内置容器）。
>
> **MUST**：滚动容器（Scroll / WaterFlow / Refresh / RelativeContainer）与表单控件（TextArea / Checkbox / Radio）见 `references/v2-scroll-and-form-components.md`。

---

## 资源引用规范

```typescript
// 引用 resources/ 下的资源，不要硬编码字符串
Text($r('app.string.title'))           // 字符串
Image($r('app.media.icon_home'))       // 图片
.backgroundColor($r('app.color.bg'))   // 颜色

// rawfile 资源
Image($rawfile('images/banner.png'))
```

---

## 弹窗 / Sheet / 模态

> **MUST**：写弹窗 / 底部面板 / 全屏模态前，先读 `references/v2-dialogs-and-sheets.md` —— Toast/确认框/操作菜单（`getUIContext().getPromptAction()`）、`@CustomDialog`+`CustomDialogController`、`bindSheet`（半模态）、`bindContentCover`（全屏）。⚠️ 全局 `AlertDialog.show` / `promptAction.*` 已废弃，V2 用 UIContext 形式。

---

## 常见错误速记（V2）

| # | 错误 | 正确做法 |
|---|---|---|
| 1 | build() 内调用异步函数 | 数据请求放 aboutToAppear / 事件回调 |
| 2 | 组件属性顺序错误 | 通用属性在前、事件回调在后 |
| 3 | List 直接放内容 | 列表项用 ListItem 包裹 |
| 4 | Grid 直接放内容 | 网格项用 GridItem 包裹 |
| 5 | @Builder 内直接改子组件入参 | 用 @Event 回调上抛 |
| 6 | 父子双向用 V1 @Link | 用 @Param + @Event（见 arkts-state-manager/references/v2-decorators.md） |
| 7 | 用 `Object.assign(new X(), {...})` 造对象 | ArkTS 限制 stdlib（报 `arkts-limited-stdlib`）；给类加**构造器** `new X(a, b, ...)` 或逐字段赋值；`@ObservedV2` 实例尤其用构造器（保 @Trace 观测性） |
| 8 | 自定义组件尾随闭包后直接链式 `.width()/.border()`（`Comp(){...}.width()`） | 报 `Cannot find name 'width'` / `Declaration or statement expected`；**外层套内置容器** `Column(){ Comp(){...} }.width()`，属性加在容器上（内置容器可链、自定义组件不可） |
| 9 | 运行时按数据选排版：写成 `WrapBuilder` / 在 @Builder 里 `const wb=...` / 对方法调用结果 `.builder()` | 类型是 **`WrappedBuilder<[T]>`**（非 `WrapBuilder`）；选取放 @Builder **外**（数据装配时算好）落到数据字段或 `this` 成员，再用成员/循环变量调用 `row.wb.builder(row)`；禁 `this.pick(k).builder(...)`、禁 @Builder 内 `const` |
| 10 | 自定义布局里把 `constraint.maxWidth` 当 number 直接算术 / 自写 `toPx(x:string\|number)` 转它 | 约束字段是 `Length`(含 `Resource`)；算术前 **`as number` 收窄**（`constraint.maxWidth as number`），别自写排除 Resource 的 toPx（报 `Type 'Resource' is not assignable to 'string \| number'`）；详见 `references/v2-layout-patterns.md` §7 |
| 11 | 可滚动组件（List/Scroll/Grid/WaterFlow）嵌在外层滚/滑容器（Swiper/Tabs/父 Scroll/父 List）里，内层滚不动、手势被外层吃掉 | 内层想先响应就配 `.nestedScroll({ scrollForward: NestedScrollMode.SELF_FIRST, scrollBackward: NestedScrollMode.SELF_FIRST })`（HarmonyOS 不像 Android 自动分发嵌套手势）；如 Swiper 内嵌横向 List 不配会翻页而非滚 List；四值/写法见 `references/v2-scroll-and-form-components.md` §3.5 |

> **MUST**：每条「错误 vs 正确」完整代码见 `references/v2-codegen-patterns.md` §常见错误 / §wrapBuilder。

---

## Linter 共存规则

本项目的项目级 linter 会自动重写 `.ets` 文件，包括：
- 将 Android SVG 素材引用 (`$r('app.media.ic_xxx_vector')`) 替换为 `SymbolGlyph($r('sys.symbol.xxx'))`
- 重新格式化 import 块
- 删除或重新生成文件头注释

Agent 在与 linter 交互时必须遵守以下规则：

### 两次即停原则

同一个 `.ets` 文件被 linter 回改超过 **2 次** → 放弃手写覆盖。改为：
- 接受 linter 的版本作为基线
- 只修复**编译器级错误**（类型不匹配、属性不存在、导入缺失）
- 不纠结风格差异（SymbolGlyph vs Image、inline color hex vs DesignTokens 常量、注释格式）

### CustomComponent 命名冲突不可妥协

若 `@Param` / `@Event` / getter 名称与 `CustomComponent` 基类方法冲突（`onClick`, `borderRadius`, `aspectRatio`, `translate`, `scale` 等），**必须改名**。这是编译错误，linter 无法自动修复。相反，linter 可能会让冲突变得更严重（例如将 `computedBorderRadius` 改回 `borderRadius`）。

**处理方式**：修复命名冲突后立即 `git commit` 创建检查点。若 linter 后续又更改了该文件，使用 `git checkout -- <file>` 恢复到检查点版本，而不是重新编辑。

### 生成检查清单追加项

生成新 `.ets` 文件时，额外检查以下不与 linter 冲突的规则：
- [ ] getter 名不与 `CustomComponent` 基类方法冲突（特别是 `borderRadius`、`onClick`、`aspectRatio`、`translate`、`scale`）
- [ ] `@Builder` 和 `build()` 方法有显式返回类型标注 `: void` 以避免 `arkts-no-implicit-return-types`

---

## 共享组件资格判定

在决定创建一个共享 UI 组件之前，必须通过以下三项判定：

1. **多调用方**：Android 源项目中这个 View/布局是否被 **3 个以上**调用方使用？
2. **纯数据配置**：各调用方对它的差异是否**仅限数据**（text、visibility、count），而非行为或状态？
3. **无动态图标切换**：是否存在调用方特有的动态图标切换逻辑（例如 ViewPagerActivity 的方向图标在 portrait/landscape/auto 间切换，而 PhotoVideoActivity 没有方向图标）？

**任意一条不满足 → 不抽取共享组件**。改为各页面独立内联实现，在页面注释中标明源布局引用。

**缘由**：内联优于一个需要 5+ 个 `@Param` flag（如 `isCurrentHidden`、`orientationMode`、`isOrientationLocked`）来控制行为差异的臃肿抽象。Android 源项目中 `bottom_actions.xml` 并非一个已封装的可复用 widget — 每个 Activity 独立引用它，Kotlin 代码中的图标切换逻辑各不相同。

---

## 生成检查清单（V2）

生成 UI 代码后，逐项检查：

- [ ] 使用 `@ComponentV2 struct`（不是 class，不是 V1 `@Component`）
- [ ] `build()` 内只有 UI 描述，无变量声明和 console.log
- [ ] 单根节点
- [ ] ForEach / LazyForEach / Repeat 提供了 keyGenerator
- [ ] List 内用 ListItem 包裹，Grid 内用 GridItem 包裹
- [ ] 字符串和图片使用 $r() 资源引用（如适用）
- [ ] 属性使用链式调用语法
- [ ] 数据加载在 aboutToAppear() 中而非 build() 中
- [ ] @Builder 方法在 build() 中通过 `this.xxx()` 调用
- [ ] 事件回调按三级策略生成（L1/L2/L3），无空注释回调
- [ ] `@Local / @Param / @Event` 变量名不在禁用列表中（参考 references/v2-prop-naming-rules.md）
- [ ] 所有用户可见文本使用 $r('app.string.xxx')，禁止硬编码中文/英文（纯数字、标点、格式占位符除外）
- [ ] aboutToAppear() 中使用 DBReader/Service 真实调用 + try-catch 空数组兜底，不使用 loadMockData()
- [ ] 所有 $r('sys.symbol.xxx') 图标名称已在 arkts-knowledge-verifier/references/verified-symbols.md 中确认存在
- [ ] **V2 强制**：`@Param` 必须有默认值；`@Event` 必须有默认实现 `() => {}`
- [ ] **V2 强制**：同一 struct 不混用 V1/V2 装饰器（如 `@ComponentV2` + `@State`）
- [ ] **V2 强制**：父子双向用 `@Param + @Event` 回调，不试图用 V1 `@Link`
- [ ] **V2 强制**：可观察类用 `@ObservedV2` 装饰，需观察的属性加 `@Trace`，不再用 `@ObjectLink`

---

## 回调生成规则（三级策略）

生成 UI 组件中的事件回调（onClick、onPlayClick、onAddToQueue 等）时，**必须按以下三级策略生成**，禁止留空注释：

### 判断流程

```
生成回调代码前:
  │
  ├─ Step 1: Grep 项目中是否存在对应 Controller/Manager/DAO
  │   例: grep -rn "class PlaybackController" entry/src/
  │
  ├─ 存在 → L1 完整接线
  ├─ 不存在但项目有 EventBus/emitter → L2 事件桥接
  └─ 都不满足 → L3 签名占位符
```

### 三级策略

| 级别 | 条件 | 生成内容 | 示例 |
|------|------|---------|------|
| **L1 完整接线** | Controller/Manager/DAO 已存在于项目中 | 直接调用真实方法 | `PlaybackController.getInstance().play(item.getMedia())` |
| **L2 事件桥接** | Controller 未就绪但 EventBus/emitter 已配置 | 发射事件 + 留接收端 TODO | `emitter.emit('PLAY_MEDIA', { itemId: item.id })` |
| **L3 签名占位符** | 以上都不满足 | console.info 占位符 + 自动注册到 placeholder-registry | `console.info('TODO:PLAY_MEDIA:FeedDetailComponent')` |

### 关键约束

1. **禁止空注释回调**: `onClick: () => { /* Start playback */ }` 是被禁止的。这种回调用户无法发现问题（不报错、不可 grep），是 BF-001 类缺陷的根源。
2. **L3 格式强制**: 占位符必须用 `console.info('TODO:<ACTION>:<COMPONENT>')` 格式，以便 grep 扫描发现。
3. **自动注册**: 每个 L3 占位符必须追加到 `spec/placeholder-registry.md`（P-ID + location + trigger_condition + status + kind + resolve_by 6 字段齐全），格式见 [a2h-plan/templates/placeholder-registry-template.md](../a2h-plan/templates/placeholder-registry-template.md)。
4. **扫描先行**: 生成回调前 MUST grep 项目，不能假设 Controller 不存在。

### 示例对比

```typescript
// 被禁止 — 空注释回调（BF-001 根源）
Button('Play')
  .onClick(() => {
    // Start playback
  })

// L1 — Controller 存在时
Button('Play')
  .onClick(() => {
    PlaybackController.getInstance().playMedia(this.item.getMedia())
  })

// L2 — 有 EventBus 但无 Controller
Button('Play')
  .onClick(() => {
    emitter.emit({ eventId: EventIds.PLAY_MEDIA }, { data: { itemId: this.item.id } })
  })

// L3 — 占位符（同时注册到 placeholder-registry）
Button('Play')
  .onClick(() => {
    console.info('TODO:PLAY_MEDIA:EpisodeItemBuilder')
  })
```

---

## 跨 Skill 协作

当用户需求超出纯 UI 范围时，读取以下 skill 的内容来补充：

| 需要什么 | 读取哪里 |
|---------|---------|
| 完整业务功能（列表详情、搜索、登录等） | `arkts-pattern-library/SKILL.md` |
| 列表数据源（LazyForEach + IDataSource） | `arkts-data-layer/references/datasource-patterns.md` |
| 页面导航（Navigation + NavDestination） | `arkts-navigation-builder/SKILL.md` |
| 状态管理（V2 `@Local / @Param / @Provider` 选择） | `arkts-state-manager/SKILL.md` 决策树 |
| 动画效果（animateTo/transition） | `arkts-animation-builder/SKILL.md` |
| 媒体播放 | `arkts-media-playback/SKILL.md` |
| 文件下载 | `arkts-download-manager/SKILL.md` |
| Android UI 对齐 | `arkts-ui-alignment/SKILL.md` |

> 完整路由矩阵见 `arkts-knowledge-verifier/references/skill-routing-guide.md`

---

## References

### V2 主参考（推荐，本项目实际使用）

- `references/v2-layout-patterns.md` — 6 种布局容器的 V2 完整模板与适用场景
- `references/v2-common-components.md` — Text/Image/Button/TextInput/Swiper/Tabs/Search 等常用组件 V2 用法
- `references/v2-scroll-and-form-components.md` — 滚动容器(Scroll/WaterFlow/Refresh/RelativeContainer) + 表单控件(TextArea/Checkbox/CheckboxGroup/Radio) V2 模板
- `references/v2-responsive-design.md` — V2 响应式断点设计（AppStorageV2 + @Local）
- `references/v2-media-app-components.md` — 媒体应用组件 V2 模式（@ObservedV2 PlaybackModel + AppStorageV2）
- `references/v2-component-lifecycle-patterns.md` — V2 组件生命周期（aboutToAppear / @Monitor / EventBus 订阅）
- `references/v2-prop-naming-rules.md` — V2 `@Param / @Local / @Event` 命名规则（避免 CustomComponent 基类冲突）

### V1 历史参考（仅老项目兼容查阅）

- `references/layout-patterns.md` — V1 布局模板（@Component / @State / @Prop）
- `references/common-components.md` — V1 常用组件用法
- `references/responsive-design.md` — V1 响应式设计（AppStorage.setOrCreate + @StorageProp）
- `references/media-app-components.md` — V1 媒体应用模式（@StorageLink）
- `references/component-lifecycle-patterns.md` — V1 组件生命周期（@StorageLink 全局状态）
- `references/prop-naming-rules.md` — V1 `@Prop / @State / @Link` 命名规则

> 遇到版本兼容性或其他不确定的 ArkTS 知识点（如属性、语法、权限等），参阅 **arkts-knowledge-verifier** skill
