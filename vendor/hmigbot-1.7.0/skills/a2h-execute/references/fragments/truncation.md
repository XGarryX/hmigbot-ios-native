# truncation — 截断/溢出定位与修复

## 心智模型
- `TextOverflow.Ellipsis` 必须配 `.maxLines(N)` 才生效；写对象形参 `.textOverflow({overflow: TextOverflow.Ellipsis})`；Clip 需父容器 `.clip(true)`；省略号一律 `'\u2026'`（单字符），禁拼 `'...'`。
- 自适应字号三件套：`.minFontSize/.maxFontSize/.heightAdaptivePolicy(MIN_FONT_SIZE_FIRST)` + maxLines + Ellipsis；禁运行时把 minFontSize 清 0。
- Flex/Row 子元素默认 `flexShrink=0`：空间不够直接被裁；长文本 Button 必须显式 `.flexShrink(1)`。
- 弹窗/浮层（Dialog/Menu/Popup/bindSheet）：外层 `Scroll` 包住 + `.constraintSize({maxHeight:'90%'})`；禁写死 `.height(N)`；自由窗口按当前窗口尺寸算位置；窄屏 bindSheet 切 `SheetType.BOTTOM`。
- 选区/光标：`setTextSelection` 索引按完整字符（grapheme cluster），禁落 Emoji 代理对中间；`SymbolSpan/ImageSpan` 视作断点。

## 定位口诀（现象 → 优先怀疑）
| 现象 | 怀疑 |
|---|---|
| 设 Ellipsis 无省略号 | 缺 maxLines／父容器宽度未收敛（Row 内缺 layoutWeight） |
| 省略号是三个句点 | 字符串拼接，改 `'\u2026'` |
| 图文混排省略号异常小 | ImageSpan 未继承字号，显式 .fontSize |
| Dialog 按钮文字被裁 | Button 缺 .flexShrink(1) |
| 标题栏自适应字号不生效 | 运行时动了 minFontSize／缺 heightAdaptivePolicy |
| 小屏/键盘弹起弹窗被切 | 缺 Scroll + constraintSize({maxHeight}) |
| 长 URL/英文单词撑破 | `wordBreak: WordBreak.BREAK_ALL`（AlertDialog 走 textStyle） |
| 大字体下挤爆 | 硬编码高度，去掉后由内容自撑 |

## 修法模式 B–F
- **B 硬编码尺寸**：`BreakpointType<T>(sm,md,lg,xl).getValue(bp)` 分档；宽度优先 `'100%'` + `constraintSize({maxWidth})`；图片用 `aspectRatio(16/9)` 替固定高。
- **C 可变内容无滚动**：`Scroll{...}.constraintSize({maxHeight})`；底部固定栏：中间 `List.layoutWeight(1)` 占满剩余。
- **D 折叠屏/悬停**：必须 `display.isFoldable()` + `display.on('foldStatusChange'/'foldDisplayModeChange')` 切布局；方向切换 setTimeout 防抖，禁 hover 分支提前 return。
- **E 文本溢出**：`Text.maxLines(N).textOverflow({overflow: TextOverflow.Ellipsis})`；Row 内文本 `.layoutWeight(1)`；消息气泡 `.constraintSize({maxWidth:'72%'})`。
- **F 断点缺失**（官方值）：xs<320／sm 320-600／md 600-840／lg 840-1440／xl≥1440 vp；用全局响应式 BreakpointModel，禁各页散落 mediaquery。

<!-- source: arkts-text-truncation/SKILL.md:L27-77,L172-192; arkts-truncation-fix/SKILL.md:L76-313 -->
