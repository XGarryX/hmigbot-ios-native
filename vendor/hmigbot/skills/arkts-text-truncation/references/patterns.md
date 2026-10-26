# 截断类缺陷 · 错误模式汇总

从 ArkTS 开发实践中归纳的 5 类错误模式。每个模式包含：典型症状、涉及组件、原理、排查提示、修复建议。各模式**覆盖的场景不重叠**：

1. **文本内容被截** — Ellipsis / Clip 本身不生效或样式异常
2. **弹窗浮层被屏幕/窗口裁切** — Dialog/Menu/Toast/bindSheet 超出可视区
3. **布局溢出撑破容器** — 固定尺寸 + 长文本/大字体
4. **文本选择手柄错位** — TextInput/RichEditor 在 Emoji/省略号/特殊 span 边界失准
5. **标题栏自适应字号异常** — `.minFontSize / .maxFontSize` 不生效

---

## 模式 1：文本截断属性不生效（省略号不显示 / 样式异常）

### 典型症状
- 设置了 `.textOverflow({ overflow: TextOverflow.Ellipsis })` 加 `.maxLines(1)`，文本溢出时**没有省略号**，直接硬截
- 显示的"省略号"是 3 个英文句点 `...` 而不是标准 `…`
- 图文混排（含 `ImageSpan`）场景下省略号**字号异常小**
- 跨平台（ArkUI-X iOS / Android）上省略号**垂直居中**而非底部对齐
- `TextOverflow.Clip` 也不裁剪，内容仍然溢出
- 文本宽度恰好等于容器宽度（临界值）时错误显示省略号

### 高发组件
`Text` / `Button`（`labelStyle`） / `Span` / `ImageSpan` / `TextArea`

### 原理
- `.textOverflow` 仅在**父容器宽度确定 + `.maxLines` 已设**时生效；两者缺一，Ellipsis 都不会出
- `TextOverflow.Clip` 要求容器启用裁剪（`.clip(true)` 或自带裁剪盒），否则子节点仍会越过边界绘制
- 跨平台下默认 `fontFamily` 不确定，底层排版基线会随系统默认字体变化，导致省略号垂直对齐偏
- `ImageSpan` 若没有继承父字号，会按默认字号参与排版，省略号字号跟着 `ImageSpan` 走
- `Button` 的 `labelStyle` 若不显式写 `overflow` 与 `maxLines`，按钮内长标签仍可能溢出

### 排查提示
1. 搜 `TextOverflow.` 使用点，逐处确认 `.maxLines` 配齐
2. 检查父容器是否给了确定宽度（放在 `Row` 里要么给 `.width`，要么给 `.layoutWeight(1)`）
3. ArkUI-X 场景显式打印 `fontFamily`；为空立即指定
4. 图文混排时给 `ImageSpan` 和外层 `Text` 都写明 `fontSize`

### 修复建议
```ts
// 纯文本
Text(this.longText)
  .maxLines(1)
  .textOverflow({ overflow: TextOverflow.Ellipsis })
  .width('100%')
  .fontFamily('sans-serif')   // 跨平台显式指定

// Button 长文本
Button('提交一份很长很长的审批单据')
  .labelStyle({
    overflow: TextOverflow.Ellipsis,
    maxLines: 1
  })
  .flexShrink(1)

// 图文混排：主字号显式下发
Text() {
  ImageSpan($r('app.media.icon')).width(16).height(16).fontSize(16)
  Span(this.longText)
}
.maxLines(1)
.fontSize(16)
.textOverflow({ overflow: TextOverflow.Ellipsis })
```
**禁忌**：不要用字符串 `'...'` 拼省略号，一律用 `'\u2026'`。

---

## 模式 2：弹窗/浮层超出可视区（小屏、键盘、自由窗口下被裁）

### 典型症状
- 设备高度不足或横屏时，`AlertDialog / CustomDialog` 底部按钮看不见
- 键盘弹出后，原本正常的弹窗被键盘遮住且没有上推
- 自由窗口（PC / 2in1 / 平板多窗）里 `Menu / Popup / Toast` 边缘被容器切掉
- 子菜单定位到窗口外
- `bindSheet` 在小宽度窗口仍显示为中央样式而非底部贴边

### 高发组件
`AlertDialog` / `CustomDialog` / `Menu` / `Popup` / `Toast` / `bindSheet` / 服务卡片

### 原理
- 浮层的高度上限是**当前窗口视口**的百分比（通常约 90%），不是物理屏幕
- 自由窗口下可绘制区 = 窗口 − 边框 − 标题栏；若应用把弹窗高度算到"整屏"就会溢出
- 键盘避让需监听 `avoidAreaChange`（type = `TYPE_KEYBOARD`），被动依赖系统默认避让在自由窗口下可能失败
- 子窗口位置要以**当前窗口内部坐标**为基准，不能叠加屏幕全局偏移
- `bindSheet` 响应式展示需要业务根据窗宽切 `SheetType`

### 排查提示
1. 把弹窗拖到小屏/横屏/键盘/自由窗口场景复现，看是否稳定截断
2. 自定义弹窗：检查是否有写死的 `.height(N)`；外层是否有 `Scroll`
3. 用 Inspector 看浮层 `frame` 与当前窗口 `windowRect` / `drawableRect` 对比
4. 打印 `window.getWindowProperties().windowRect` 与弹窗实测 rect 比对

### 修复建议
```ts
// 自定义弹窗模板：Scroll 外包 + maxHeight 上限
@CustomDialog
struct MyDialog {
  controller?: CustomDialogController;
  content: string = '';
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

// AlertDialog 长英文 URL 换行
AlertDialog.show({
  message: 'https://very-long-url-without-spaces...',
  textStyle: { wordBreak: WordBreak.BREAK_WORD }
})

// bindSheet 随窗宽自适应
.bindSheet(this.sheetOpen, this.buildSheet, {
  preferType: this.winWidth < 600 ? SheetType.BOTTOM : SheetType.CENTER,
  detents: [SheetSize.MEDIUM, SheetSize.LARGE]
})
```

应用侧主力是：**不用硬编码高度、外包 Scroll、以当前窗口为基准算位置**。

---

## 模式 3：固定尺寸容器 + 长文本 / 大字体 ⇒ 布局挤爆

### 典型症状
- `Dialog` 两个按钮并排，其中一个文字略长就被截
- 系统字体缩放（适老化 1.45× / 1.75×）打开后，弹窗内容按钮挤出
- `Slider` 拖动气泡里数字长一点就不出省略号（普通模式下）
- 自定义标题栏长文本换行或裁切异常
- 长英文 URL 在弹窗里撑破容器

### 高发组件
`Dialog` 内 `Button` / `Slider`（气泡） / `TitleBar` / 任意 `Row / Column` 内的固定宽高子元素

### 原理
- `Flex / Row / Column` 子元素默认 `flexShrink = 0`：空间不足时不收缩
- 常量硬编码的 `.height / .width` 在 `fontScale` 放大后必然溢出
- 长单词不换行由 `WordBreak` 控制；对 URL 默认 `BREAK_WORD` 不够狠
- 自适应字号三件套用错（尤其运行时清空 `.minFontSize`）会退化为"一步截断"

### 排查提示
1. 搜 `.height(数字)` / `.width(数字)` / 自定义常量高度，评估是否真的需要固定
2. 把系统字号调到最大（开发者选项）复现
3. 在 Flex 子元素上检查是否缺 `.flexShrink(1)`
4. 标题栏检查 `.minFontSize / .maxFontSize / .heightAdaptivePolicy` 三件套是否齐全

### 修复建议
```ts
// Flex 子元素允许收缩
Row() {
  Button('较长的按钮文字').flexShrink(1).layoutWeight(1)
  Button('确定').flexShrink(0)
}

// 外层 Scroll 兜底大字体
Scroll() {
  Column() { /* 标题 + 内容 + 按钮 */ }
}
.constraintSize({ maxHeight: '90%' })

// 自适应字号标题
Text(this.title)
  .minFontSize(14)
  .maxFontSize(20)
  .heightAdaptivePolicy(TextHeightAdaptivePolicy.MIN_FONT_SIZE_FIRST)
  .maxLines(1)
  .textOverflow({ overflow: TextOverflow.Ellipsis })

// 长 URL 在弹窗里
AlertDialog.show({
  message: url,
  textStyle: { wordBreak: WordBreak.BREAK_ALL }
})
```

**通用原则**：涉及用户可控字号的组件，宁可让内容自己撑高度、外套 `Scroll`，也不要写固定高度。

---

## 模式 4：TextInput / RichEditor 光标与选择手柄错位

### 典型症状
- 有 Emoji 的 `TextInput` / `TextArea` 调 `TextInputController.setTextSelection` 后，光标落在 Emoji 中间，表情残缺
- 长文本截断显示 `…` 时，拖动选择手柄反转，手柄跳到异常位置
- `Text` 里 AISpan 点击：点**省略号区域**仍然弹 AI 菜单
- `RichEditor` 里 AI 取词跨过 `SymbolSpan` / `ImageSpan`，把不可见文本一起抓进来
- `TextInput` 密码模式下输入超长密码，出现省略号

### 高发组件
`TextInput` / `TextArea` / `RichEditor` / `Text`（含 `AISpan` / `SymbolSpan` / `ImageSpan`）

### 原理
- Emoji / CJK 组合字符占多个 code unit；直接按 code unit 索引设选区会落在单字符中间
- 被 `…` 覆盖的原始字符在可视上不可见但仍有逻辑位置，点击热区/AI 取词不过滤就会穿越到"不可见区"
- 用户把第二手柄拖过第一手柄形成反转选区后，自绘选区菜单若不跟随反转会跳位
- `SymbolSpan` / `ImageSpan` 在遍历时应视作天然分隔符

### 排查提示
1. 文本含 Emoji → 通过 `TextInputController.setTextSelection(start, end)` → 观察光标
2. 反转选择：手动拖第二手柄越过第一手柄，看是否跳
3. `Text` + `AISpan` + 截断：点 `…` 所在位置，看是否弹菜单
4. `RichEditor` 含 `SymbolSpan`：触发 AI 取词，看抓取范围

### 修复建议
```ts
@ComponentV2
struct EmojiInput {
  controller: TextInputController = new TextInputController();
  @Local text: string = '';

  // 以完整字符数组为单位切分，避免落在代理对中间
  private safeRange(start: number, end: number): [number, number] {
    const chars = Array.from(this.text);
    const clamp = (i: number) => Math.max(0, Math.min(chars.length, i));
    const s = clamp(start);
    const e = clamp(end);
    // 将 code-unit 索引换算为字符索引后再反向映射
    const toCodeUnit = (n: number) => chars.slice(0, n).join('').length;
    return [toCodeUnit(s), toCodeUnit(e)];
  }

  build() {
    TextInput({ text: this.text, controller: this.controller })
      .onChange(v => this.text = v)
      .onSubmit(() => {
        const [s, e] = this.safeRange(0, 5);
        this.controller.setTextSelection(s, e);
      })
  }
}

// 密码超长：应用侧限制长度兜底
TextInput({ text: this.pwd })
  .type(InputType.Password)
  .maxLength(64)
  .onChange(v => this.pwd = v.slice(0, 64))

// AI 能力只挂在完整可见 span 上，不跨省略号
```

大多数根因需要框架侧修复，应用侧的主力是**以完整字符为单位操作 + 边界兜底 + 升级 SDK**。

---

## 模式 5：自适应字号与标题栏异常

### 典型症状
- 标题栏长文本没有先缩字号就直接截断
- 运行时更改标题后，`.minFontSize` 好像"失效"了
- 在含图标/图片的标题栏里，标题字号缩得过小
- 跨页面相同标题组件，在某些页面正常缩放，另一些页面不缩

### 高发组件
自定义 `TitleBar` / `Navigation` 标题区 / 列表项长标题 / 统计数字卡片

### 原理
- 自适应字号需要同时满足：`.minFontSize`、`.maxFontSize`、`.heightAdaptivePolicy`、`.maxLines` **四项齐全**
- 运行时动态更新 `.minFontSize`（尤其被设回 0 或与 `.maxFontSize` 相同）会让缩放区间消失
- 图标随标题放在同一 `Text` 里（通过 `ImageSpan`）会和标题竞争基线；标题字号应独立控制
- 标题外层放在 `Row` 里没有给 `.layoutWeight(1)`，宽度未收敛时不会触发缩放

### 排查提示
1. 检查这四项是否齐全：`.minFontSize / .maxFontSize / .heightAdaptivePolicy / .maxLines`
2. 搜索代码里动态修改 `.minFontSize` 的地方，评估能否移除
3. 标题外层 `Row`：`.layoutWeight(1)` 是否给了
4. 图标用独立 `Image` 组件而非 `ImageSpan`，与标题文本分开布局

### 修复建议
```ts
@ComponentV2
struct TitleBar {
  @Param @Once title: string = '';

  build() {
    Row() {
      Image($r('app.media.back')).width(24).height(24)
      Text(this.title)
        .layoutWeight(1)
        .minFontSize(14)
        .maxFontSize(20)
        .heightAdaptivePolicy(TextHeightAdaptivePolicy.MIN_FONT_SIZE_FIRST)
        .maxLines(1)
        .textOverflow({ overflow: TextOverflow.Ellipsis })
        .margin({ left: 8, right: 8 })
      Image($r('app.media.more')).width(24).height(24)
    }
    .width('100%')
    .height(56)
    .padding({ left: 16, right: 16 })
  }
}
```

**通用原则**：自适应字号的四个属性是原子组合，不要运行时分开改；图标与标题分别用独立组件控制尺寸。
