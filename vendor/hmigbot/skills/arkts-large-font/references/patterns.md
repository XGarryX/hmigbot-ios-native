# 大字体适配 · 错误模式汇总

从历史缺陷归纳的 7 类典型错误模式。每个模式包含：典型症状、高发组件、底层机制、排查提示、修复建议。

---

## 模式 1：文本组件未限制 `maxFontScale`，适老化档位下撑爆布局

### 典型症状
- 同一页面 1.0 倍正常，切到 1.75 / 2.0 / 3.2 档文字被截断、省略号、换行挤压
- `Button` 内文字高度异常、超出按钮边界
- `Badge` 小红点数字异常大
- `Swiper` 数字指示器、`AlphabetIndexer` 侧边字母异常放大
- `TextInput` 的错误提示、字符计数器（`showCounter`）未随字号同步或反而越界
- `SegmentButton` 分段按钮文字不响应缩放（个别版本需显式 `maxFontScale` 才能正常缩放）

### 高发组件
`Button` / `Search` / `TextInput` / `TextArea` / `Badge` / `Swiper` / Swiper 指示器 / `AlphabetIndexer` / `Refresh`（loadingText）/ `SegmentButton` / `SubHeader` / 自定义容器里的 `Text`

### 底层机制
- 文本类组件的 `fontSize` 使用 fp 单位时会无上限跟随系统 `fontSizeScale` 放大，未设置 `maxFontScale` 就等于无封顶
- 早期 API 版本的 `Button` / `SymbolGlyph` 未暴露 `minFontScale / maxFontScale`
- `Badge` / Swiper 指示器 / `AlphabetIndexer` / `Refresh` 等在内部自建文本时，应用层无法直接设置 `maxFontScale`
- 若同时设定了固定 `.height(...)`，文本放大但容器不变高，直接截

### 排查提示
1. 全局搜 `.maxFontScale(` 的使用 —— 大字体相关组件里没出现基本都是候选
2. 搜代码里的 `.height(` + 数字常量，和 `Text` 类组件配合时要重点关注
3. 模拟器里打开 **设置 → 显示与亮度 → 字体大小 = 最大**，再开 **辅助功能 → 适老化模式** 复现

### 修复建议
```ts
// 通用：给所有应放大但有上限的文本加 maxFontScale
Text(this.title)
  .fontSize($r('sys.float.Title_S'))
  .maxFontScale(2.0)           // 通用上限
  .minFontScale(0.85)          // 防异常缩小

// Button 文本
Button('确认')
  .fontSize(16)
  .maxFontScale(2.0)

// 不希望跟随字体放大的"数字/字母标签"
Text(index.toString())
  .maxFontScale(1.0).minFontScale(1.0)
```

对没有 `maxFontScale` 属性的早期组件（低版本 `Button` / `AlphabetIndexer` 等），用 `Text` 外包并转发交互；或升级 SDK。

---

## 模式 2：弹窗 / Picker 类组件未响应字体档位变化，切档位后显示不刷新

### 典型症状
- 弹窗已弹出时改变系统字体档位，弹窗内字号/间距**不变**
- 关闭再打开才正常
- `CalendarPicker` / `DatePicker` / `TimePicker` 选项字体在适老化下超出上限未生效
- 自定义 `CustomDialog` 切横屏 + 改字体后宽度不自适应

### 高发组件
`CalendarPicker` / `DatePicker` / `TimePicker` / `AlertDialog` / `CustomDialog` / `SelectOverlay` / `Menu`（长按菜单）/ 半模态 `bindSheet`

### 底层机制
- 浮层是独立的节点树，不会随主页面一起重新测量
- 历史上部分系统弹窗（`CalendarPicker`、`DatePicker` 早期版本）字体档位变化后框架未重新测量其内容
- 自定义 `CustomDialog` 如果内部没有把 `maxFontScale` 传给子 `Text`，适老化档位下会直接越界

### 排查提示
1. 保持弹窗不关 → 改系统字体 → 若无任何视觉变化 = 命中本模式
2. 在 UIAbility 的 `onConfigurationUpdate` 打日志，确认回调确实触发但弹窗未响应
3. 检查 `CustomDialog` 的 builder 内是否对内部文本设置了 `maxFontScale`

### 修复建议
应用层兜底 —— 在 UIAbility 中监听字体变更，主动关闭并重开弹窗：

```ts
// FontScaleModel.ets — 全局响应式模型
@ObservedV2
export class FontScaleModel {
  @Trace tick: number = 0;
  @Trace scale: number = 1.0;
}

// EntryAbility.ets
export default class EntryAbility extends UIAbility {
  private lastScale: number = 1.0;

  onConfigurationUpdate(newCfg: Configuration): void {
    if (newCfg.fontSizeScale !== undefined && newCfg.fontSizeScale !== this.lastScale) {
      this.lastScale = newCfg.fontSizeScale;
      const model = AppStorageV2.connect(FontScaleModel, 'fontScale', () => new FontScaleModel())!;
      model.scale = newCfg.fontSizeScale;
      model.tick = Date.now();           // 驱动弹窗销毁重建
    }
  }
}

// 页面侧：用 AppStorageV2.connect 取实例，作为 if 条件或 key 销毁重建弹窗
@ComponentV2
struct DialogHost {
  @Local fs: FontScaleModel = AppStorageV2.connect(FontScaleModel, 'fontScale', () => new FontScaleModel())!;
  // 例：把 this.fs.tick 当 key 强制重建弹窗
}
```

> V1 等价：`AppStorage.setOrCreate` → `AppStorageV2.connect(FontScaleModel, ...)` 上的属性赋值；`@StorageLink('fontScaleTick') tick: number = 0` → `@Local fs: FontScaleModel = AppStorageV2.connect(...)!` 后访问 `this.fs.tick`。

自定义 `CustomDialog` 内部文本务必透传 `maxFontScale`；若内容可能超高，用 `Scroll` 包裹而非固定 `height`。

---

## 模式 3：自适应逻辑错写在事件回调 / 尺寸硬编码，初始化不生效

### 典型症状
- 页面刚进入大字体模式时样式仍是默认，**点击一下**才变成适老化样式
- `Tabs` 子页签内边距首次加载错乱
- 自定义 `Tabs` 写死 `.height(64)`，大字体下仍是 64，不按档位变
- `Dialog` 在悬浮窗 / 横屏下"跳过"了适老化重算

### 高发组件
`Tabs` / `TabBar` / `SubTabBarStyle` / 自定义菜单 / `CustomDialog` / `bindSheet`

### 底层机制
- 适老化分档必须在组件构建阶段（`aboutToAppear` / `build()`）就根据 `fontSizeScale` 决定尺寸
- 放在 `onClick / onTouch / onAreaChange` 里 → 首帧未触发，需要一次用户交互
- 写死的 padding / margin / height 常量在大字体下不会自动变大

### 排查提示
1. 页面进入后立即观察布局 → 点任意位置 → 样式突变 = 命中本模式
2. 自定义布局逻辑里全局搜硬编码数字 margin / padding / height
3. 横屏 / 悬浮窗下是否走了不同分支跳过适老化分档

### 修复建议
```ts
import { UIContext } from '@kit.ArkUI';
import { common } from '@kit.AbilityKit';

@ComponentV2
struct MyHeader {
  @Local fontScale: number = 1.0;

  aboutToAppear() {
    const ctx = this.getUIContext().getHostContext() as common.UIAbilityContext;
    this.fontScale = ctx?.config?.fontSizeScale ?? 1.0;
  }

  // 按档位取尺寸（V2 推荐用 @Computed 缓存）
  @Computed
  get bottomMargin(): number {
    return this.fontScale >= 1.75 ? 32 : this.fontScale >= 1.45 ? 24 : 16;
  }

  build() {
    Column() {
      // ...
    }
    .margin({ bottom: this.bottomMargin })
  }
}
```

> V1 等价：`@Component` → `@ComponentV2`、`@State` → `@Local`；V1 没有 `@Computed`，需手写 `private get` 而无缓存。

并在 UIAbility 的 `onConfigurationUpdate` 里同步 `fontSizeScale`（推荐通过 `AppStorageV2.connect(FontScaleModel, ...)`，V1 等价 `AppStorage`），触发页面重建。

---

## 模式 4：fp 单位或 `SymbolGlyph` 图标意外跟随字体缩放

### 典型症状
- `SymbolGlyph` / `Image($r('sys.symbol.*'))` 图标在大字体下随文字一起变大，撑破卡片
- `Chip` 内部图标溢出 Chip 边界（clip 未开）
- `ComposeListItem` 图标行在适老化档位变形
- `Tabs` 底部文本引用 `$r('sys.float.Caption_L')` → fp 基资源，跟随放大

### 高发组件
`SymbolGlyph` / `Chip` / `ComposeListItem` / `TabBar`（底部页签）/ 使用 `$r('sys.float.*')` 作为尺寸

### 底层机制
- `SymbolGlyph.fontSize` 若不指定单位，**默认按 fp** 解析 → 跟系统字体缩放
- `Chip` 早期版本根容器 `.clip(false)`，容器尺寸固定但内部图标变大，越界可见
- `$r('sys.float.Caption_L')` / `Body_*` / `Subtitle_*` 等文字 token 是 fp 单位，不适合用在容器 `height / width / size`

### 排查提示
1. 搜 `SymbolGlyph(` 所有点，看 `.fontSize(...)` 是否显式数字且无单位（即 vp）
2. 搜 `.clip(false)` + `Chip` / 自定义容器
3. 搜 `$r('sys.float.` 用在 `.height / .width / .size / SymbolGlyph.fontSize` 的地方

### 修复建议
```ts
// 图标不应随字号变化
SymbolGlyph($r('sys.symbol.message'))
  .fontSize(24)                 // 纯数字 = vp
  .minFontScale(1.0)
  .maxFontScale(1.0)

// Chip 内图标越界兜底
Chip({ /* ... */ }).clip(true)

// 容器尺寸用 vp 基资源（非 Caption / Body 类）
.height($r('sys.float.ohos_id_card_height'))
```

低版本如果系统组件没暴露 `clip` / `maxFontScale`，用 `Stack` 外包一层并自行 `.clip(true)`。

---

## 模式 5：浮层 / Popup 位置计算只 clamp 单边，大字体下右/下侧越界

### 典型症状
- 自动填充推荐弹窗在大字体下**右侧**超出应用 / 屏幕
- 自动填充 Popup 被键盘遮挡（大字体下弹窗高度增加）
- `SelectOverlay` 菜单错位、"更多"按钮阴影错位
- `SelectOverlay` 点击热区变小
- 安全控件（`PasteButton`）点开菜单反而变小

### 高发组件
`Popup` / `bindPopup` / `SelectOverlay` / `Menu` / `PasteButton` / `SaveButton` / `Web` 内弹层

### 底层机制
- 弹窗 X 偏移常见错误：只限制 `offset.x >= edge`，**漏掉** `offset.x + popupWidth ≤ windowRect.width - edge`。字号变大后 `popupWidth` 增长 → 右侧越界
- 键盘弹起后可用区域变小，未重新夹取 Y 偏移 → 弹窗被键盘盖住
- 安全控件内部测量顺序错误，导致大字体下内部 padding 没更新就开始排版

### 排查提示
1. 大字体档位打开弹窗 → 用 Inspector 看弹窗 `rect.right` 是否超出 `windowRect.width`
2. 同时观察键盘弹起后 `rect.bottom` 是否超过 `windowRect.height - keyboardHeight`
3. 若是系统组件（`SelectOverlay` / `PasteButton`），升级 SDK 是最直接的修复

### 修复建议
自定义浮层位置算法必须双边 clamp：

```ts
import window from '@ohos.window';

// 假设已拿到当前窗口
const win = await window.getLastWindow(getContext(this));
const rect = win.getWindowProperties().drawableRect;   // 真实可绘区
const kbd = win.getWindowAvoidArea(window.AvoidAreaType.TYPE_KEYBOARD);
const edge = 8;

const maxX = rect.width - popupWidth - edge;
offset.x = Math.min(Math.max(offset.x, edge), maxX);

const maxY = rect.height - popupHeight - kbd.bottomRect.height - edge;
offset.y = Math.min(Math.max(offset.y, edge), maxY);
```

系统 `SelectOverlay / Popup / Menu` 的历史 bug 只能通过升级 SDK 修复；临时规避可将触发位置尽量远离屏幕右 / 下边缘，或在业务中主动 `dismiss` 后重新 `show`。

---

## 模式 6：子窗 / UIExtensionComponent / IsolatedComponent 未继承宿主 fontScale

### 典型症状
- 主窗文字正常放大，**子窗 / 弹窗 / UIExtensionComponent 内文字不放大**
- AI 菜单（`UIExtensionComponent`）在大字体下异常、甚至崩溃
- `IsolatedComponent` 内字体被"卡住"最大 1.3 倍
- 自定义子窗（`window.createSubWindow`）创建后字号停留在 1.0

### 高发组件
`window.createSubWindow` 创建的子窗 / `UIExtensionComponent` / `IsolatedComponent` / 依赖子窗显示的 AI 菜单 / 文本识别浮层

### 底层机制
- 子窗容器独立，历史版本未自动同步主窗 `fontSizeScale`
- `IsolatedComponent` 曾被框架按"卡片"归类，字号被限制 ≤ 1.3 倍
- `UIExtensionComponent` 的宿主节点若被当作局部变量持有，重绘时可能被释放

### 排查提示
1. 在子窗 / `UIExtensionComponent` 页面内打印当前 `fontSizeScale`，若为 1.0 而主窗是 2.0 → 命中
2. 自定义 `UIExtensionComponent` 节点务必提升为 `class` 成员字段持有强引用
3. 老版本（API 9 / 10）多数需要升级 SDK 才有根本修复

### 修复建议
应用临时规避 —— 在主窗 `onConfigurationUpdate` 中主动销毁并重建子窗：

```ts
// EntryAbility
onConfigurationUpdate(newCfg: Configuration): void {
  if (newCfg.fontSizeScale !== this.lastScale) {
    this.lastScale = newCfg.fontSizeScale ?? 1.0;
    this.destroySubWindow();
    this.createSubWindow();
  }
}
```

自定义 `UIExtensionComponent` 节点务必提升为类成员字段持有强引用，避免重绘时被 GC。

---

## 模式 7：超大字体下文本测量 / 光标 / 选区边界计算错误

### 典型症状
- `TextInput` / `TextArea` 在 2.0~3.2 倍字号下用方向键 / PageUp / PageDown / Home / End，光标跳到错误位置
- 选区柄越界、超出内容区
- `TextInput` 改 `fontSize` 后选框不跟随
- `RichEditor` 拖拽场景偶现崩溃
- `Tabs` 长按 + 旋转屏幕触发异常选中
- `Picker` 抛滑 + 改字体概率性字号不正确
- `Canvas` `fillText` 切系统字体后乱码

### 高发组件
`TextInput` / `TextArea` / `RichEditor` / `Picker` / `Tabs`（长按菜单）/ `Canvas`

### 底层机制
这类问题大多属于框架测量层 bug：
- 行高大于输入框高时，换行判定失效
- 选区柄高度大于内容区高度时没有特殊处理
- `fontSize` 变更未触发选区重新测量
- `Picker` 抛滑阶段继续使用旧布局约束
- `Canvas` 未感知系统默认字体变化

### 排查提示
1. 专门在 `fontSizeScale = 3.2` 下跑输入 / 光标用例
2. 关注大字体 + 横竖屏切换 / 旋转 / 抛滑组合场景
3. `RichEditor` 拖拽崩溃通常是时序问题，拖拽结束回调里不要直接触发重绘

### 修复建议
应用侧主要靠**规避 + 升级**：

- 重度依赖文本编辑的页面，给关键输入限制 `.maxFontScale(2.0)`，防止进入 3.2 档

```ts
TextInput({ placeholder: '请输入' })
  .maxFontScale(2.0)
```

- 在旋转 / 配置变更前主动收起选区、关闭长按弹窗：

```ts
@ObservedV2
class OverlayDismissModel {
  @Trace tick: number = 0;
}

// EntryAbility
onConfigurationUpdate(newCfg: Configuration): void {
  const m = AppStorageV2.connect(OverlayDismissModel, 'overlayDismiss', () => new OverlayDismissModel())!;
  m.tick = Date.now();
}

// 页面侧：@Local m = AppStorageV2.connect(OverlayDismissModel, 'overlayDismiss', () => new OverlayDismissModel())!;
// 用 @Monitor('m.tick') 监听变化触发 blur / dismiss 活跃浮层
```

> V1 等价：`AppStorage.setOrCreate('overlayDismissTick', Date.now())` + 页面侧 `@StorageLink('overlayDismissTick') tick: number = 0` + `@Watch('onTickChange')`。

- `Canvas` 文字渲染：在 `onConfigurationUpdate` 中若 `fontSizeScale` 变化，主动调用 `CanvasRenderingContext2D` 的重绘逻辑重新 `fillText`。
