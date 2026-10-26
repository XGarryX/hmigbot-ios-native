# arkui-enums — ArkUI 枚举合法值速查（防枚举幻觉）

成员名只准抄下表；表外枚举先查 SDK `ets/component/enums.d.ts` 再用。幻觉多为 Compose/Flutter/iOS 同名 API 串台。

## 实证错误（写前对照）
| 幻觉写法 | 正确 | 串台来源 |
|---|---|---|
| `TextOverflow.MiddleEllipsis` | `TextOverflow.Ellipsis`（ArkUI 无中间省略） | Compose 1.8 TextOverflow.MiddleEllipsis |
| `HitTestMode.Opaque` | `HitTestMode.Default`（Flutter opaque=自身+子孙可命中并阻断其后兄弟）；禁写 Block：Block 连子孙一起排除，遮罩里放按钮必死（首屏死区） | Flutter HitTestBehavior.opaque |
| `Alignment.CenterEnd` | `Alignment.End`（End 已是垂直居中+尾部） | Compose Alignment.CenterEnd |

## 合法值全集（HarmonyOS 6.0.2 / API 22 enums.d.ts 实测；@since 成员低版本工程不可用）
| 枚举 | 全部成员 |
|---|---|
| TextOverflow | None, Clip, Ellipsis, MARQUEE(@since11) |
| HitTestMode | Default, Block, Transparent, None, BLOCK_HIERARCHY(@since20), BLOCK_DESCENDANTS(@since20) |
| Alignment | TopStart, Top, TopEnd, Start, Center, End, BottomStart, Bottom, BottomEnd（9 宫格，无 CenterStart/CenterEnd） |
| TextAlign | Center, Start, End, JUSTIFY(@since11) |
| FlexAlign | Start, Center, End, SpaceBetween, SpaceAround, SpaceEvenly |
| FontWeight | Lighter, Normal, Regular, Medium, Bold, Bolder（`.fontWeight()` 另接受 number 与 '400' 型字符串） |
| ImageFit | Contain, Cover, Auto, Fill, ScaleDown, None; TOP_START/TOP/TOP_END/START/CENTER/END/BOTTOM_START/BOTTOM/BOTTOM_END(@since12), MATRIX(@since15) |
| BarState | Off, Auto, On |
| FontStyle | Normal, Italic |
| TextDecorationType | None, Underline, Overline, LineThrough |
| ItemAlign | Auto, Start, Center, End, Baseline, Stretch |
| VerticalAlign | Top, Center, Bottom |
| HorizontalAlign | Start, Center, End |
| FlexDirection | Row, Column, RowReverse, ColumnReverse |
| FlexWrap | NoWrap, Wrap, WrapReverse |
| Visibility | Visible, Hidden, None |
| WordBreak | NORMAL, BREAK_ALL, BREAK_WORD, HYPHENATION |
| TextHeightAdaptivePolicy | MAX_LINES_FIRST, MIN_FONT_SIZE_FIRST, LAYOUT_CONSTRAINT_FIRST |
| TextCase | Normal, LowerCase, UpperCase |
| LineBreakStrategy | GREEDY, HIGH_QUALITY, BALANCED |

## HitTestMode 四值语义（按语义选值，禁按名猜）
| 值 | 自身 | 子孙 | 其后兄弟节点 | 典型场景 |
|---|---|---|---|---|
| Default | 可命中 | 可命中 | 自身命中时阻断 | 绝大多数场景；Flutter opaque 的对应值 |
| Block | 可命中 | **全部排除** | 阻断 | 仅"整块只响应自己、内部无任何交互"的叶子；**容器内有按钮/输入必死** |
| Transparent | 可命中 | 可命中 | **不阻断（穿透）** | 装饰层/读屏屏蔽层 |
| None | 排除 | 可命中 | 不阻断 | 自身让路、子组件照常交互 |

遮罩要吞点击：用 `.onClick(() => {})` 吃事件，不用 Block（见 runtime-patterns 第 5 条）。

## 硬规矩
1. 表内枚举 = 该 SDK 版本下成员穷举；其它枚举本表未穷举，用前必查声明，禁类推。
2. 大小写照抄：新老成员风格混杂（Ellipsis vs MARQUEE），不许"统一风格"改写。
3. @since 成员先对照工程 compileSdkVersion，低于该 API 不可用。
4. 编译报 `Property 'X' does not exist on type 'typeof Y'` = 枚举幻觉：回本表按语义选值（HitTestMode 用四值表；其它枚举先读 enums.d.ts 该成员注释），禁按名称相似度猜（Opaque 猜成 Block：编译全绿、首屏全死）。

<!-- source: aippt_new_0818/spec/reports/execute-adjudications.md ADJ-10（4 处枚举编译错实证）+ HarmonyOS 6.0.2(API22) sdk/default/openharmony/ets/component/enums.d.ts 逐枚举实测 -->
