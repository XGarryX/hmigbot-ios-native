# design-tokens — 主题令牌绑定与回执

> 来源：830 `agent-prompts/4-step3a-ui.md`「设计令牌」段。规格块（`<<<THEME-BRIEF v2 …>>>` 哨兵对）由组装器机械注入，禁转述/摘要（转述即丢失）。

## 不变量：Android 靠主题隐式着色的控件（Material Button/Toolbar/TabLayout/FAB），ArkUI 必须显式绑定，否则落系统默认色
| 场景 | 必须写 | 禁止 |
|---|---|---|
| 颜色 | `$r('app.color.<令牌名>')` | 裸 `#RRGGBB`、`Color.Blue` |
| 尺寸/圆角/间距 | `$r('app.float.<令牌名>')` | 裸数字 |
| 按钮形状 | 按令牌显式设 `.type()` / `.borderRadius()` | 落回胶囊默认形状 |

## 禁止自创平行令牌体系
不得新建 `DesignTokens.ets` 之类裸数字/裸色值常量文件，不得在组件里硬编码色值与尺寸；令牌一律 `$r('app.color.*')` / `$r('app.float.*')`（`color.json` / `float.json` 路线）。
> 边界：`arkts-design-tokens-extractor` 的 converter 内部挂钩在本管线内停用（其 `DesignTokens.ets` 产物与 `$r` 纪律互斥）；仅用户显式调用时走 float/color.json 路线。

## 回执：改了主题绑定就必须写分片回执
写/更新 `spec/execution/theme-receipts/<page_id>.json`：
```json
{ "<令牌条目名>": "<file:line>", "...": "..." }
```
- 按页一个文件，禁多页共写（并发 worker 互相覆盖）。
- closure 波 `gate:closure-scan` / `gate:closure-rescan`（FV-1）的 theme detector 按 `spec/baseline/resolved-theme.json` 推导的必填闭集机械对账：条目缺失、色值未绑定、硬编码 hex、Button 落回胶囊，任一即 FAIL。
- 无 `resolved-theme.json` = 该闸放行，但属流程缺陷（A0.6b 没跑）不是豁免。

## 令牌缺失时不许自行发明
规格块无对应令牌或与页面不匹配 → 结构化摘要报 `design_tokens_missing`（走 `decision_gaps` 或 `deferred_items`），禁自编色值静默继续。
