# fix-large-font（大字体修复）

适用 finding：症状仅在系统字体调大后出现（截断/溢出/图标放大/弹窗越界）。只改白名单内文件。

## 档位事实

fontSizeScale：1.0 / 1.15 / 1.45 / 1.75（普通上限）/ 2.0（适老化入口）/ 3.2（最严苛）。fp 随缩放、vp 不随；应用分档阈值取 1.75 与 2.0。

## 症状 → 根因 → 修法

| 症状 | 根因 | 修法 |
|---|---|---|
| 文本截断/溢出/撑爆布局 | 缺 maxFontScale | `.maxFontScale(2.0).minFontScale(1.0)`；TextInput/TextArea/Search 必锁 2.0 |
| 固定高度容器裁字 | `.height(56)` 写死 | 删固定高，改 `.constraintSize({ minHeight: ... })` 由内容撑 |
| 图标随文字放大 | SymbolGlyph/Image.fontSize 无单位按 fp 解析 | `.fontSize(24)`（裸数字=vp）+ `.minFontScale(1.0).maxFontScale(1.0)`；Chip 越界补 `.clip(true)` |
| 容器随字号长高 | `$r('sys.float.Caption_L')` 等 fp token 当容器尺寸 | 换 vp 基资源（如 ohos_id_card_height） |
| 切档后弹窗/Picker 不刷新 | 浮层独立节点树不重测 | EntryAbility.onConfigurationUpdate 写 AppStorageV2 模型 tick，驱动弹窗 dismiss+重建 |
| 初始不生效、点一下才变 | 分档逻辑写在 onClick/onAreaChange | 移到 aboutToAppear/build；fontSizeScale 存 @Local，@Computed 分档 |
| Popup/推荐框右侧或底部越界 | 位置只 clamp 单边 | 双边 clamp：`offset.x ∈ [edge, rect.width-w-edge]`；Y 再扣键盘 avoidArea |
| 子窗/UIExtension 字不放大 | fontScale 未同步到子窗 | 主窗 onConfigurationUpdate 里销毁重建子窗；或升级 SDK |
| 3.2 档光标乱跳/选区柄越界 | 框架测量 bug | `.maxFontScale(2.0)` 卡住不进 3.2 档；配置变更前主动收起选区与浮层 |
| 切字体后 Canvas 乱码 | 未感知系统字体变化 | onConfigurationUpdate 中主动重跑 fillText 重绘 |

## 硬规则

- 禁止用 Caption_* / Body_* / Subtitle_* 等 fp 资源做 height/width/size。
- 自定义 CustomDialog 内部 Text 必须透传 maxFontScale；内容可能超高时用 Scroll 包裹而非固定 height。
- 验证必跑五档 1.0/1.45/1.75/2.0/3.2，且切档时不关弹窗；横屏+大字体叠加测一次。

<!-- source: arkts-large-font/SKILL.md:L152-L216; references/patterns.md:L7-L351 -->
