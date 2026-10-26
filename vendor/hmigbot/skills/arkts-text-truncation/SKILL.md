---
name: arkts-text-truncation
description: ArkTS 文本/布局截断场景下的根因定位与修复：文本被 Ellipsis 截断或省略号位置异常、maxLines 不生效、Flex/Row 内 Text 被挤没（缺 layoutWeight/flexShrink）、弹窗/CustomDialog/bindSheet 超出屏幕高度被裁切、布局撑破容器、文本选择手柄或光标在截断边界错位、标题栏/NavBar 长文本异常、RichEditor/TextInput 截断等。若主要是系统字体缩放导致的截断，优先用 arkts-large-font。**边界**：本 skill 仅限文本字符级截断（Text/RichEditor/TextInput）+ 弹窗超屏裁切；图片裁切 / 列表显示不全 / AlphabetIndexer 溢出 / 多设备适配 / 折叠屏布局切换 / 响应式断点 → [arkts-truncation-fix](../arkts-truncation-fix/SKILL.md)。
metadata:
  type: domain
  domain: ui
  tags:
  - text-truncation
  - ellipsis
  - overflow
  - dialog
  - layout
---
# arkts-text-truncation — ArkTS 截断类缺陷排查技能

> 覆盖「文本内容被截」「容器浮层被裁」「布局溢出撑破」「文本选择边界错位」「标题栏/自适应字号异常」五类"装不下"的 UI 缺陷。

## 1. 何时启用

出现以下任一信号就应用本技能：

- 长文本没有出现省略号，或省略号位置/样式异常（过小、居中、变成三个句点 `...`）
- 文本"正好装满"时反而被加了省略号；或文本没超出却被裁掉了底部
- `Dialog` / `AlertDialog` / `CustomDialog` / `Menu` / `Popup` / `Toast` / `bindSheet` 在小屏、横屏、键盘弹起、自由窗口下**显示不全**
- `Button`、标题栏、`Slider` 气泡等**固定尺寸容器**里的长文本被裁掉
- 大字体 / 适老化模式下布局挤爆、弹窗按钮文字被切
- `TextInput` / `TextArea` / `RichEditor` 中的**光标或选择手柄位置**在省略号边界、Emoji、`SymbolSpan` 附近错乱
- `TextOverflow.Ellipsis` / `.maxLines` / `.flexShrink` / 自适应字号等属性看似设置了却"不生效"
- 自定义标题栏长文本没有按 `.minFontSize / .maxFontSize` 缩放

## 2. 心智模型（看懂这些再看模式）

### 2.1 `TextOverflow` 四档

| 枚举值 | 行为 |
|---|---|
| `TextOverflow.None` | 不做任何处理，内容溢出容器 |
| `TextOverflow.Clip` | 在容器边界硬裁剪；需要父容器 `.clip(true)` 才会真切掉 |
| `TextOverflow.Ellipsis` | 最后一行尾部替换为 `…`（U+2026，单字符，不是三个 `.`），**必须配合 `.maxLines` 才有意义** |
| `TextOverflow.MARQUEE` | 跑马灯滚动，不截断 |

常见盲区：属性需要写成对象 `.textOverflow({ overflow: TextOverflow.Ellipsis })`；`.maxLines(1)` 不给，Ellipsis 永远不出。

### 2.2 自适应字号三件套

`Text` 上的 `.minFontSize / .maxFontSize / .heightAdaptivePolicy` 实现「先缩字号再截断」。典型用法：

```ts
Text(this.title)
  .minFontSize(14)
  .maxFontSize(20)
  .heightAdaptivePolicy(TextHeightAdaptivePolicy.MIN_FONT_SIZE_FIRST)
  .maxLines(1)
  .textOverflow({ overflow: TextOverflow.Ellipsis })
```

**陷阱**：业务中途把 `.minFontSize` 清成 0 或不一致地动态改，会导致「设了 `minFontSize` 却依然一步截断」的现象——不要在运行时重置。

### 2.3 Flex 伸缩语义

放在 `Flex / Row / Column` 里的子元素默认 `flexShrink = 0`（典型如 Dialog 内部并排 `Button`）：空间不够也不收缩，直接被裁。长文本 `Button` 要能压缩必须显式 `.flexShrink(1)`；`.layoutWeight(n)` 按比例分配剩余空间，`.flexGrow(n)` 扩张剩余空间。

### 2.4 弹窗/浮层自适应

`Dialog / Menu / Popup / Toast / bindSheet` 都是子窗口或浮层，高度上限由系统夹到视口的一定百分比。应用侧兜底要点：

- 自定义弹窗外层用 `Scroll` 包住「标题 + 内容 + 按钮」
- 通过 `.constraintSize({ maxHeight: '90%' })` 留安全余量
- **不要**写死 `.height(固定数值)`；让内容撑，外层限制上限
- 自由窗口/小窗下，以**当前窗口尺寸**为基准算弹窗位置，不要用屏幕全屏尺寸（详见 `arkts-multi-window` 技能）

`bindSheet` 在小屏或横屏可用 `SheetType.BOTTOM`，并配合 `detents` 指定多档高度。

### 2.5 文本选择边界（TextInput / TextArea / RichEditor）

几个敏感点：
- **Emoji / 组合字符**：通过 `TextInputController.setTextSelection(start, end)` / `RichEditorController.setSelection(start, end)` 设置选区或 `caretPosition(pos)` 移动光标时，若 index 落在代理对中间，光标会显示在半个 Emoji 里。务必以完整字符（grapheme cluster）为单位计算索引。
- **省略号区域**：被 `…` 覆盖的原始字符在可视上不可见但仍占位，点击热区、AI 取词范围不要穿越到这段。
- **选区反转**（用户把第二手柄拖过第一手柄）：自绘选区/自定义菜单要跟着反转更新锚点，否则手柄会在省略号边界"跳一行"。
- **`SymbolSpan` / `ImageSpan`**：AI 取词、文本遍历应把这些视作天然断点，不要穿透。

## 3. 排查流程

### Step 1 · 先确定截断类别

问一句：「是**文本内容**被截，还是**容器/浮层**被裁？」

- 文本内容被截 → Step 2
- 容器/浮层被裁 → Step 3
- 大字体/适老化下整体挤爆 → Step 4
- 文本选择/光标位置错乱 → Step 5

### Step 2 · 文本截断自检

```ts
Text(this.longText)
  .maxLines(1)                                       // 必不可少，否则 Ellipsis 无效
  .textOverflow({ overflow: TextOverflow.Ellipsis }) // 对象形参
  .width('100%')                                     // 或 .constraintSize({ maxWidth: ... })
  .fontFamily('sans-serif')                          // ArkUI-X 跨平台显式指定
```

检查点：
- 父容器宽度是否收敛？`Text` 放在 `Row` 里没给宽度/权重，会被当作无限宽永远不截断 → 加 `.layoutWeight(1)` 或显式宽度
- 图文混排（含 `ImageSpan`）时省略号字号异常小 → 给 `ImageSpan` 显式 `.fontSize`，或给外层 `Text` 设置统一字号
- 英文长单词/URL 不换行 → 默认 `WordBreak.BREAK_WORD`；想让无空格 URL 也强断用 `WordBreak.BREAK_ALL`；`AlertDialog` 用 `textStyle: { wordBreak: WordBreak.BREAK_WORD }`
- 大小写强制 → `.textCase(TextCase.UpperCase)` 等在测量后再变换，不要用字符串自己拼
- 别手动用 `"..."` 拼省略号，应使用 `"\u2026"`（`…`）

### Step 3 · 浮层/弹窗截断自检

```ts
@CustomDialog
struct MyDialog {
  controller?: CustomDialogController;
  build() {
    Scroll() {
      Column() {
        Text('标题').fontSize(20)
        Text(this.content)
          .maxLines(10)
          .textOverflow({ overflow: TextOverflow.Ellipsis })
        Row() {
          Button('取消').flexShrink(1).layoutWeight(1)
          Button('确定').flexShrink(1).layoutWeight(1)
        }
      }
      .padding(24)
    }
    .constraintSize({ maxHeight: '90%' })
  }
}
```

检查点：
- Dialog 按钮文字被切 → `Button` 加 `.flexShrink(1)`，必要时 `.labelStyle({ overflow: TextOverflow.Ellipsis, maxLines: 1 })`
- `AlertDialog` 长英文 URL 撑破 → `textStyle: { wordBreak: WordBreak.BREAK_ALL }`
- Menu / Popup 在自由窗口下被裁 → 位置应以当前窗口为基准，详见 `arkts-multi-window`
- 小屏或键盘弹起时弹窗底部看不见 → 去掉硬编码 `.height(N)`，改 `constraintSize + Scroll`
- `bindSheet` 在小宽度窗口下仍居中展示 → 监听窗宽并在窄屏切为 `SheetType.BOTTOM`

### Step 4 · 大字体 / 适老化专项

系统字号缩放 `fontScale` 可到 1.75× 或更高，任何硬编码像素高度都会被撑爆。

- 搜代码里的 `.height(常量)` / `.width(常量)`——能去就去
- 高度交给内容自撑；外层加 `Scroll` + `constraintSize({ maxHeight: ... })`
- `Slider` 气泡、`Toast` 这类小浮层按 `fontScale` 分档切宽度
- 标题栏使用自适应字号三件套（`.minFontSize / .maxFontSize / .heightAdaptivePolicy`），**不要**在运行时清掉 `minFontSize`

### Step 5 · TextInput / RichEditor 选择边界

```ts
@ComponentV2
struct Editor {
  controller: TextInputController = new TextInputController();
  @Local text: string = '';

  build() {
    TextInput({ text: this.text, controller: this.controller })
      .maxLength(64)
      .onChange(v => this.text = v)
      .onSubmit(() => {
        // 以完整字符为单位设置选区，避免落在 Emoji 代理对中间
        this.controller.setTextSelection(0, this.text.length);
      })
  }
}
```

- 含 Emoji 的输入框光标异常 → 设选区时以完整字符串切片为单位；升级 SDK
- 密码模式 `TextInput` 显示出了省略号 → 应用侧用 `.maxLength` + `onChange` 截断兜底
- 点击省略号区域仍触发 AI 菜单 → 业务只给完整可见的 span 挂 AI 能力；或规避 AI 菜单
- `RichEditor` 取词跨越 `SymbolSpan` / `ImageSpan` → 应用侧将特殊 span 视作分隔，分段调用

## 4. 典型问题定位口诀

| 现象 | 优先怀疑 |
|---|---|
| 设了 `TextOverflow.Ellipsis` 却没省略号 | `.maxLines` 未设 / 父容器宽度未收敛（无 `layoutWeight` 或宽度） |
| 省略号是 `"..."` 三个点 | 代码里用字符串拼接；应改 `"\u2026"`（`…`） |
| 图文混排省略号字号异常小 | `ImageSpan` 未继承父字号，显式 `.fontSize` |
| 跨平台（iOS/Android）省略号垂直居中 | `fontFamily` 未指定，显式设 `sans-serif` |
| `Text` 没超宽却被截断 | 父容器宽度计算在临界值；或外部加了额外 padding/margin |
| Dialog 按钮文字被裁 | `Button` 缺 `.flexShrink(1)` |
| 标题栏自适应字号不生效 | 运行时误动 `.minFontSize`，或未设 `.heightAdaptivePolicy` |
| 小屏/横屏/键盘弹起弹窗被切 | 未用 `Scroll` 包裹 + `.constraintSize({ maxHeight })` |
| 自由窗口下 `Menu` / `Popup` 被裁 | 位置算到全屏尺寸；改用当前窗口基准（见 arkts-multi-window） |
| `Slider` 气泡文字不省略 | 气泡宽度硬编码；按 `fontScale` 分档 |
| 大字体下 `AlertDialog` 按钮挤出 | 内部硬编码高度；外层 `Scroll` + 按钮 `.flexShrink(1)` |
| `TextInput` 光标跳到 Emoji 中间 | 设选区未按完整字符；升级 SDK |
| 省略号处选择手柄位置错乱 | 选区反转时锚点未跟随互换 |
| 点击省略号仍弹 AI 菜单 | AI 热区穿越了被省略号覆盖的不可见文字 |
| 密码模式 `TextInput` 出现省略号 | 应用侧 `.maxLength` + `onChange` 截断兜底 |
| 连续旋转后卡片内容被切 | 回调里做了硬尺寸覆盖；让系统布局接管 |

## 5. 端到端修复流程

> 前置：通过 §3 排查流程已定位到 `references/patterns.md` 中某个错误模式。

### Step 1 · 找到代码位置

在 ArkTS 工程里按以下顺序搜：

- 找截断属性：grep `maxLines\(`、`textOverflow\(`、`TextOverflow\.`、`heightAdaptivePolicy\(`、`minFontSize\(`、`maxFontSize\(`
- 找布局硬约束：grep `\.height\(\d`、`\.width\(\d`、`constraintSize\(`、`\.flexShrink\(`、`\.layoutWeight\(`
- 找弹窗：grep `@CustomDialog`、`CustomDialogController`、`AlertDialog\.show`、`bindSheet\(`、`bindMenu\(`、`bindPopup\(`、`promptAction\.showToast`
- 找输入：grep `TextInput\(`、`TextArea\(`、`RichEditor\(`、`TextInputController`、`setTextSelection\(`、`setSelection\(`、`caretPosition\(`
- 找跑马灯 / 自适应：grep `MARQUEE`、`fontFamily\(`
- 找省略号字面量：grep `'\.\.\.'`、`"\.\.\."`——典型反模式（应改 `'\u2026'`）
- 找标题栏 / Slider 气泡 / Tab：自定义 Header / `Slider` / `Tabs` / `Chip` 内部文本是否给了截断属性

### Step 2 · 对照错误模式的"错误写法"

翻到 `references/patterns.md`，典型错误特征：

- 设了 `TextOverflow.Ellipsis` 但缺 `.maxLines(1)`，或父容器宽度未收敛（`Row` 里没 `layoutWeight`）
- 用字符串 `'...'` 拼省略号而非单字符 `'\u2026'`
- `Dialog` 按钮 `Button` 缺 `.flexShrink(1)`，长文本被裁
- 弹窗写死 `.height(N)` 而非 `Scroll + constraintSize({ maxHeight: '90%' })`
- `AlertDialog` 长 URL 未配 `textStyle: { wordBreak: WordBreak.BREAK_ALL }`
- 自适应字号场景动态把 `.minFontSize` 清成 0，或缺 `.heightAdaptivePolicy`
- `TextInputController.setTextSelection` 索引落在 Emoji 代理对中间

### Step 3 · 改写为正确写法

按 patterns.md 修复建议替换。关键动作：

- 文本截断：`.maxLines(N).textOverflow({ overflow: TextOverflow.Ellipsis })` + 父容器收敛宽度（`.layoutWeight(1)` 或显式宽度）
- 省略号一律用 `'\u2026'`；图文混排给 `ImageSpan` 显式 `.fontSize`
- 弹窗骨架：`Scroll() { Column() { ... Row() { Button().flexShrink(1).layoutWeight(1) } } }.constraintSize({ maxHeight: '90%' })`
- `AlertDialog` 长 URL：`textStyle: { wordBreak: WordBreak.BREAK_ALL }`；中文段落用 `BREAK_WORD`
- 标题栏 / Slider 气泡：`.minFontSize / .maxFontSize / .heightAdaptivePolicy(TextHeightAdaptivePolicy.MIN_FONT_SIZE_FIRST) + .maxLines(1) + Ellipsis`，且不要在运行时清掉 `minFontSize`
- 小屏 `bindSheet`：监听窗宽，窄屏切 `SheetType.BOTTOM` + `detents`
- `TextInputController.setTextSelection`：以完整字符切片为单位计算索引；含 Emoji / `SymbolSpan` 时按 grapheme cluster 处理
- 若根因是框架旧版本 bug（如 Emoji 光标乱跳、密码模式出现省略号）：升级 SDK，或用 `.maxLength` + `onChange` 截断兜底

### Step 4 · 验证

- 准备**最长文案** × **最小窗口** × **最大字体档（1.75 / 2.0 / 3.2）** 三维组合表，逐组复测
- 弹窗在小屏 + 横屏 + 键盘弹起场景各跑一次
- 含 URL / 邮箱 / 全英文长单词的文案专测一次
- Emoji / 组合字符 / `SymbolSpan` / `ImageSpan` 输入框光标移动 + 选择 + 复制粘贴
- RTL 语言下省略号位置（应在尾部对应方向）
- 自由窗口下浮层位置 / 截断行为（与 `arkts-multi-window` 验证项叠加）

### Step 5 · 如果修完仍未解决

回到 §3 重新跑一遍；若浮层位置 / 自由窗口裁切是主因，切到 `arkts-multi-window`；若大字体撑爆是主因，切到 `arkts-large-font`；若跨设备断点导致宽度不一，切到 `arkts-multi-device`。

## 6. 参考

- `references/patterns.md`：5 类错误模式的详细拆解（症状 → 机制 → 排查 → 修复）
- 窗口形态相关截断（自由窗口、分屏、子窗坐标）见 `arkts-multi-window` 技能

---

## See Also

- [arkts-truncation-fix](../arkts-truncation-fix/SKILL.md) — 容器/列表/图片溢出 + 多设备/折叠屏/响应式断点（本 skill 不覆盖）
- [arkts-large-font](../arkts-large-font/SKILL.md) — 系统字体缩放档位下的截断（已明示让位关系）
- [arkts-multi-window](../arkts-multi-window/SKILL.md) — 窗口形态切换场景下的浮层裁切
