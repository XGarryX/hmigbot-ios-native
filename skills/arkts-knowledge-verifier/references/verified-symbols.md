# Verified SymbolGlyph Symbols

> **This file is auto-maintained by `a2h-retrospect`.**
> Manual edits are allowed but may be overwritten when retrospect detects updated symbols.
> Last updated: 2026-03-27

---

## Confirmed Working

The following 29 symbol names have been verified to work with `SymbolGlyph($r('sys.symbol.<name>'))` on API 12+:

| # | Symbol Name | Typical Usage |
|---|-------------|---------------|
| 1 | `house_fill` | Home tab icon |
| 2 | `list_bullet` | List / subscription tab |
| 3 | `play_fill` | Play button |
| 4 | `pause_fill` | Pause button |
| 5 | `magnifyingglass` | Search |
| 6 | `gearshape` | Settings |
| 7 | `star_fill` | Favorited / starred |
| 8 | `star` | Not favorited |
| 9 | `trash` | Delete |
| 10 | `plus` | Add / create |
| 11 | `goforward_30` | Skip forward 30s |
| 12 | `gobackward_10` | Skip backward 10s |
| 13 | `forward_end_fill` | Next track |
| 14 | `moon_fill` | Sleep timer |
| 15 | `music` | Audio / podcast generic |
| 16 | `envelope` | Inbox |
| 17 | `dot_grid_2x2` | Grid view / category |
| 18 | `share` | Share action |
| 19 | `arrow_left` | Back navigation |
| 20 | `clock` | History / recent |
| 21 | `xmark` | Close / dismiss |
| 22 | `checkmark` | Confirm / done |
| 23 | `chevron_right` | Drill-down / detail |
| 24 | `arrow_down_to_line` | Download |
| 25 | `line_3_horizontal` | Menu / hamburger |
| 26 | `play_square_stack_fill` | Queue / playlist |
| 27 | `backward_end_fill` | Previous track（上一曲，与 #13 `forward_end_fill` 成对） |
| 28 | `wifi` | WiFi / 连接状态（无线网络已连接） |
| 29 | `bell` | 通知 / 提醒（消息铃铛） |

> **媒体播控成对图标**：下一曲 = `forward_end_fill`（#13）；上一曲 = `backward_end_fill`（#27）。
> 两者在官方音乐服务卡片 worked-example 中作为「下一首 / 上一首」按钮成对出现。
> 不要虚构 `previous_fill` / `backward_fill` / `skip_previous` 等名 —— 上一曲就是 `backward_end_fill`。

> **本清单非穷举**：官方符号库远大于此表，连接/状态、通知/提醒类图标官方均有收录（如 `wifi`、`bell`）。遇到表外的 symbol 名，不要一律标 `[待验证]`，应先按官方 docs 的 worked-example 核实其确切拼写（用 `sys.symbol.<name>` 全文检索命中即为已验证），核实到确切名就据实给出，仅在官方 docs 也查无实证时才回退 `[待验证]`。

---

## Known Invalid

The following symbol names do **NOT** exist in the HarmonyOS symbol library. Use the replacement instead.

| # | Invalid Name | Replacement | Notes |
|---|-------------|-------------|-------|
| 1 | `music_note` | `music` | Simplified name |
| 2 | `doc_on_doc` | `list_bullet` | No direct equivalent; list icon is closest |
| 3 | `copy` | `checkmark` | No copy icon; use checkmark for "copied" feedback |
| 4 | `tray_fill` | `envelope` | Inbox concept mapped to envelope |
| 5 | `tray` | `envelope` | Same as tray_fill |
| 6 | `square_and_arrow_up` | `share` | iOS-style share icon mapped to HarmonyOS share |
| 7 | `ohos_share` | `share` | Incorrect prefix; just use `share` |
| 8 | `rectangle_grid_2x2` | `dot_grid_2x2` | Different naming convention |
| 9 | `square_grid_2x2_fill` | `dot_grid_2x2` | Different naming convention |
| 10 | `play_square_stack` | `play_square_stack_fill` | Only filled variant exists |
| 11 | `arrow_up_arrow_down` | `chevron_right` | No sort icon; chevron as fallback |
| 12 | `antenna_radiowaves_left_and_right` | `music` | No antenna icon; music as podcast fallback |
