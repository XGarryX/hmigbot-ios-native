---
name: arkts-truncation-fix
description: 修复 ArkTS/HarmonyOS 应用中 UI 内容截断、布局溢出、多设备适配不良等问题（V2 优先，API 12+）。当用户提到"内容显示不全""布局溢出""折叠屏布局异常""图片被裁切""AlphabetIndexer 溢出""列表显示不全""多设备/响应式/断点适配""hover 模式失败"等，或只说"界面显示有问题""这个页面有 bug"（截断/响应式/折叠屏方向）时触发。**沉浸式 / 安全区 / 状态栏遮挡 / setWindowLayoutFullScreen → [arkts-immersive-safearea](../arkts-immersive-safearea/SKILL.md)。** **纯文本字符级截断（Ellipsis 位置 / maxLines 不生效 / Flex 内 Text 被挤没 / 弹窗超屏 / RichEditor / TextInput）→ [arkts-text-truncation](../arkts-text-truncation/SKILL.md)。**
metadata:
  type: domain
  domain: ui
  tags:
  - ui
  - truncation
  - responsive
  - foldable
---
# ArkTS UI Truncation / Display Fix — 界面展示截断修复

本 skill 用于诊断和修复 ArkTS 应用中的 UI 截断、布局溢出、文本溢出、折叠屏布局切换和多设备适配问题。这些问题在手机、平板、折叠屏等不同设备上表现各异，需要系统性排查。

> **沉浸式 / 安全区适配 / 状态栏遮挡请走 [arkts-immersive-safearea](../arkts-immersive-safearea/SKILL.md)**（已从本 skill 迁移）

## API 版本

基于 **API 12+**（HarmonyOS 5.0.0+）。涉及的关键 API：

- 折叠屏：`display.on('foldStatusChange')`、`display.on('foldDisplayModeChange')`、`display.getCurrentFoldCreaseRegion()`
- 断点系统：`mediaquery.matchMediaSync()` 或自定义 `BreakpointObserver`
- 窗口管理：`window.getLastWindow()` 取窗口属性 / 监听 `windowSizeChange`（不再涉及 `setWindowLayoutFullScreen` 与 `AvoidArea`，那些走 immersive-safearea）

---

## 诊断流程

收到截断/显示问题后，按以下步骤排查：

### Step 1：定位问题类别

先阅读涉及的 .ets 文件，判断属于哪个类别（可多选）：

| 类别 | 典型症状 | 排查重点 |
|------|---------|---------|
| ~~**A. 安全区遮挡**（已迁移）~~ | 状态栏/导航栏遮住内容、全屏背景没延伸、刘海区域覆盖文字 | **→ 走 [arkts-immersive-safearea](../arkts-immersive-safearea/SKILL.md)**（四层架构 + WindowModel 响应式，本 skill 不再覆盖） |
| **B. 硬编码尺寸** | 某设备正常、另一设备截断或留白过多 | 搜索 `height(N)` `width(N)` `fontSize(N)` 等固定值 |
| **C. 内容溢出无滚动** | 列表/文本/卡片超出容器，底部内容看不到 | 变量高度内容是否缺少 `Scroll` 或 `constraintSize` |
| **D. 折叠屏/悬停失败** | 折叠展开后布局不变化、悬停模式无效 | 是否有 fold 事件监听、hover 布局分支 |
| **E. 文本截断** | 长文字撑破容器或被直接裁切 | 是否有 `maxLines` + `textOverflow` |
| **F. 断点系统缺失** | 所有设备显示相同布局，平板/折叠屏体验差 | 是否有 breakpoint 逻辑和布局模式切换 |

### Step 2：阅读代码，提取具体问题点

对每个 .ets 文件逐项检查：

1. **根容器**：是否有顶部/底部安全区 padding？
2. **固定尺寸**：哪些 `width(N)` / `height(N)` 在不同屏幕上会出问题？
3. **滚动容器**：可变高度的内容是否被 `Scroll` 或 `List` 包裹？
4. **文本组件**：所有 `Text()` 是否有溢出处理？
5. **断点响应**：是否有 breakpoint 工具类和响应式值切换？

### Step 3：生成修复方案

按下面的修复模式生成代码。每个修复都说明原因和适用场景。

---

## 修复模式详解

### 模式 A：安全区域适配 → 已迁移到 arkts-immersive-safearea

本 skill 不再覆盖安全区适配 / 沉浸式背景延伸 / 状态栏遮挡等场景。完整方案请走：

**[arkts-immersive-safearea](../arkts-immersive-safearea/SKILL.md)** — 提供：

- 四层架构（EntryAbility 一次性测量 → 根 Navigation `expandSafeArea` → 业务页 WindowModel 响应式 padding → 滚动场景特化）
- `WindowModel` 全局共享（`windowTopPadding` / `windowBottomPadding` / 4 字段响应式，折叠屏/分屏/悬浮窗自动重算）
- Layer 1-3 自检 Checklist
- 6 大场景模板（默认 V2 / router.pushUrl 独立页 / H5 容器 / Hero+Scroll / V1 混栈 / layout 陷阱）

> 该 skill 替代了原本各页自取 `window.AvoidAreaType` + 手动加 padding 的简化方案，避免双源同步、折叠屏不重算等问题。

---

### 模式 B：固定尺寸改为响应式

**问题根因**：`height(56)`、`fontSize(20)`、`width(150)` 等硬编码值在某个屏幕上恰好合适，但在其他设备上溢出或太小。

**诊断信号**：
- 大量纯数字的 `width()`、`height()`、`fontSize()`、`margin()`、`padding()`
- 标题栏 `height(56)` 没有用百分比
- 图片固定尺寸 `width(120).height(160)`

**修复方案**：

用断点工具类提供不同值：

```typescript
class BreakpointType<T> {
  sm: T;
  md?: T;
  lg?: T;
  xl?: T;

  getValue(breakpoint: string): T {
    switch (breakpoint) {
      case 'xl': return this.xl ?? this.lg ?? this.md ?? this.sm;
      case 'lg': return this.lg ?? this.md ?? this.sm;
      case 'md': return this.md ?? this.sm;
      default: return this.sm;
    }
  }
}

// 使用示例
private titleFont = new BreakpointType(18, 20, 24, 28);
private headerHeight = new BreakpointType(48, 52, 56, 56);

Text("标题")
  .fontSize(this.titleFont.getValue(this.currentBreakpoint))
```

对于宽度，优先使用百分比或 `layoutWeight`：

```typescript
// 固定宽度 — 在窄屏上会溢出
Row().width(360)

// 改为百分比 + 最大宽度
Row()
  .width('100%')
  .constraintSize({ maxWidth: 600 })
```

对于图片，用 `aspectRatio` 代替固定高度：

```typescript
Image(src)
  .width('100%')
  .aspectRatio(16 / 9)
  .objectFit(ImageFit.Cover)
```

---

### 模式 C：可变内容添加滚动约束

**问题根因**：聊天引用预览、长文本、动态列表等可变高度内容没有 `Scroll` 包裹和最大高度约束，导致撑破父容器。

**诊断信号**：
- 变量内容直接放在 `Column` 里，没有 `Scroll` 包裹
- 底部操作栏被可变内容推出屏幕
- 列表内容没有 `.padding({ bottom: N })` 给底部栏留空间

**修复方案**：

```typescript
// 可变高度内容必须限制最大高度 + 提供滚动
Scroll() {
  Column() {
    // 动态内容...
  }.width('100%')
}
.scrollBar(BarState.Auto)
.constraintSize({ maxHeight: this.getMaxContentHeight() })

// maxHeight 应根据断点调整
private getMaxContentHeight(): number | string {
  switch (this.currentBreakpoint) {
    case 'xs': return 80;   // 小屏限制更严
    case 'sm': return 120;
    default: return 'auto'; // 大屏不限制
  }
}
```

对于底部有固定操作栏的布局，使用 `RelativeContainer` 或 `Flex` 让列表自适应剩余空间：

```typescript
Column() {
  // 标题栏 — 固定高度
  Row() { Text("标题") }.height(56)

  // 内容区 — 自动填满剩余空间
  List({ scroller: this.scroller }) {
    // ...
  }.layoutWeight(1)  // 关键：占满剩余空间

  // 底部栏 — 固定高度
  Row() { /* 输入框等 */ }.height(52)
}
```

---

### 模式 D：折叠屏悬停模式

**问题根因**：未监听折叠状态变化，或在需要旋转时放弃悬停适配。

**诊断信号**：
- 无 `display.on('foldStatusChange')` 监听
- hover 逻辑中有 `if (needQuarterTurn) { return; }` 之类的提前退出
- 无折叠屏设备检测 `display.isFoldable()`

**修复方案**：

```typescript
import display from '@ohos.display';

// 判断折叠屏
private checkFoldable(): void {
  try {
    this.isFoldable = display.isFoldable();
    if (this.isFoldable) {
      this.foldStatus = display.getFoldStatus() as number;
      this.foldDisplayMode = display.getFoldDisplayMode() as number;
      display.on('foldStatusChange', (status: number) => {
        this.foldStatus = status;
        this.updateHoverMode();
      });
      display.on('foldDisplayModeChange', (mode: number) => {
        this.foldDisplayMode = mode;
        this.updateHoverMode();
      });
    }
  } catch (e) {
    console.error('foldable check failed', e);
  }
}

// 根据折叠状态切换布局
private updateHoverMode(): void {
  // FOLD_STATUS_EXPANDED = 0, 折叠屏完全展开
  // FOLD_STATUS_FOLDED = 2
  const expanded = 0;
  this.isHoverMode = this.isFoldable && this.foldStatus === expanded;
}
```

**方向锁定防抖**（避免折叠瞬间方向反复切换）：

```typescript
private orientationTimerId: number = -1;

private schedulePreferredOrientation(target: number, delayMs: number): void {
  clearTimeout(this.orientationTimerId);
  this.orientationTimerId = setTimeout(() => {
    window.getLastWindow(this.getUIContext().getHostContext()).then((win) => {
      win.setPreferredOrientation(target);
    });
  }, delayMs);
}
```

---

### 模式 E：文本溢出处理

**问题根因**：`Text` 组件没有设置 `maxLines` 和 `textOverflow`，长文字直接撑破容器或被裁切。

**诊断信号**：
- `Text(name)` 或 `Text(description)` 没有 `maxLines` 和 `textOverflow`
- 在 `Row` 中的文本没有 `.layoutWeight(1)` 或 `constraintSize({ maxWidth: ... })`
- 列表项的标题/副标题无截断处理

**修复方案**：

```typescript
// 单行截断
Text(longTitle)
  .maxLines(1)
  .textOverflow({ overflow: TextOverflow.Ellipsis })

// 两行截断
Text(description)
  .maxLines(2)
  .textOverflow({ overflow: TextOverflow.Ellipsis })

// 在 Row 中，文本需要约束最大宽度
Row() {
  Image(avatar).width(40).height(40)
  Text(name)
    .layoutWeight(1)           // 占满剩余空间
    .maxLines(1)
    .textOverflow({ overflow: TextOverflow.Ellipsis })
  Text(time).fontSize(12)
}
```

对于消息气泡等场景，使用 `constraintSize`：

```typescript
Text(messageContent)
  .constraintSize({ maxWidth: '72%' })
  .fontSize(14)
```

---

### 模式 F：断点系统

**问题根因**：没有响应式断点机制，所有设备使用完全相同的布局。

**断点值**（华为官方规范，必须遵循）：

| 断点 | 宽度范围 | 典型设备 |
|------|---------|---------|
| xs | < 320vp | 小屏设备 |
| sm | 320-600vp | 手机竖屏 |
| md | 600-840vp | 手机横屏/小平板 |
| lg | 840-1440vp | 平板 |
| xl | >= 1440vp | 大平板/折叠屏展开 |

**完整断点工具类实现见 `references/breakpoint-toolkit.ets`**（V2 风格），包含：
- `BreakpointConstants` — 断点阈值与字符串标识常量
- `BreakpointType<T>` — 按断点返回不同值的泛型工具
- `getBreakpointByWidth / getVerticalBreakpoint / isLargeBreakpoint / getMaxContentWidth` — 断点计算函数
- `@ObservedV2 BreakpointModel` + `getBreakpointModel()` — 全局响应式模型（替代 V1 散落 `AppStorage.setOrCreate / @StorageProp` 模式）
- `AdaptiveWindowObserver` — 综合断点 + 折叠屏观察者（写入 BreakpointModel；安全区适配请改用 arkts-immersive-safearea 的 WindowModel）

---

## 输出格式

修复截断问题时，输出格式：

```markdown
## 诊断结果

- 问题类别：[A/B/C/D/E/F 中的哪几项]
- 影响设备：[xs/sm/md/lg/xl 中的哪些]
- 严重程度：[高/中/低]

## 问题分析

[对每个问题点，说明为什么会导致截断]

## 修复方案

[给出修复后的代码，标注修改点和原因]
```

---

## 与其他 Skill 的关系

- **arkts-immersive-safearea**：⭐ 沉浸式 / 安全区 / 状态栏遮挡 / setWindowLayoutFullScreen / 全屏背景延伸（**本 skill 不再覆盖此领域**，完整方案在该 skill）
- **arkts-text-truncation**：⭐ 纯文本字符级截断（Ellipsis / maxLines / Flex 内 Text 挤没 / 弹窗超屏裁切 / RichEditor / TextInput）（**本 skill 收容器/列表/图片溢出 + 多设备/折叠屏/响应式断点**）
- **arkts-component-builder**：如果修复需要创建新的自定义组件
- **arkts-knowledge-verifier**：不确定某个 API 是否存在或版本兼容性时
- **arkts-codebase-debug**：如果是运行时行为异常而非布局截断问题
- **arkts-ui-alignment**：如果涉及 Android UI 迁移到 ArkTS 的对齐

---

## 参考文档

- `references/breakpoint-toolkit.ets` — 完整的断点 + 折叠屏工具类代码（V2 风格：`@ObservedV2 BreakpointModel` + `AppStorageV2.connect`；安全区已迁移到 arkts-immersive-safearea）
- `references/common-fix-patterns.md` — 各类截断问题的修复模式速查表
