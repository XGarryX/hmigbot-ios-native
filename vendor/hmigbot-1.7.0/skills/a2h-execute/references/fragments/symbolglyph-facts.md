# symbolglyph-facts — SymbolGlyph 实证事实表（防幻觉）

图标只准用下方「已验证存在」清单里的名字；清单外按回退序，绝不凭猜发 `sys.symbol.*`（编译必报 `Unknown resource name`，整页失败；"先标待验证再发"也挡不住）。

## 已验证存在（`$r('sys.symbol.<名>')` 直接可用）
- 导航/箭头：house chevron_left chevron_right chevron_up chevron_down arrow_left arrow_right arrow_up arrow_down arrow_2_circlepath
- 列表/布局：list_bullet line_3_horizontal square_grid_2x2
- 媒体：play_fill pause_fill playpause_fill backward_fill forward_end_fill backward_end_fill speaker_wave_2_fill mic mic_fill repeat repeat_1 shuffle
- 账户/隐私：person person_fill person_2 lock eye eye_slash（密码显隐 = eye / eye_slash）
- 状态：checkmark checkmark_circle checkmark_circle_fill xmark xmark_circle xmark_circle_fill plus plus_circle minus_circle info_circle exclamationmark_circle questionmark_circle
- 操作：magnifyingglass trash gearshape envelope bell bell_fill heart heart_fill star star_fill bookmark bookmark_fill link paperplane paperplane_fill hand_thumbsup
- 内容/时间：doc folder folder_fill calendar calendar_badge_plus clock camera camera_fill map flag bolt
- 电商：cart cart_fill bag bag_fill gift gift_fill creditcard
- 其它：wifi sun_max moon cloud
- `ohos_` 前缀（仅这些验证存在）：ohos_wifi ohos_lock ohos_trash ohos_star ohos_photo ohos_mic；`ohos_add`/`ohos_delete`/`ohos_settings`/`ohos_share`/`ohos_search` 等全不存在，用裸名。

## 已验证不存在 → 替代
| 幻觉名 | 用 |
|---|---|
| forward_fill | forward_end_fill（backward_fill 存在，forward_fill 不存在） |
| ellipsis / dot_3_horizontal | line_3_horizontal |
| square_and_arrow_up（分享） | paperplane / paperplane_fill |
| tray_arrow_down | envelope |
| chart_bar | square_grid_2x2 |
| eye_fill / eye_slash_fill | eye / eye_slash（无 _fill 形） |
| location / location_fill | map（无 location 裸名） |
| photo | doc / square_grid_2x2 |
| music_note | speaker_wave_2_fill |
| male / female / person_badge / figure_stand | person / person_2（性别靠文字标签，禁 Text('♂'/'♀')） |
| tag / doc_fill / person_circle / slider_horizontal_3 | 上方已验证名 |

## 硬规矩
1. `fontColor` 参数是数组：`[Color.Black]` 不是 `Color.Black`；条件色 `this.isActive ? [Color.Black] : ['#99182431']`。
2. 清单外图标按序回退：① 清单内语义最近名（人物/性别→person 系、搜索→magnifyingglass、分享→paperplane）→ ② 确需精确图形且工程自带矢量图才用 Image → ③ 绝不 emoji/Unicode 符号字（♂ ♀ ✓ ★）塞 Text 当图标。

## Tabs-in-Navigation 覆盖陷阱（两分法）
- 底部主导航 + Navigation 路由：`Tabs` 放 `Navigation` 内部会被 `NavDestination` 子页覆盖整个区域（含 Tab 栏）→ Tab 栏必须外置：`Column { Navigation(this.navPathStack){按 currentTabIndex 切内容}.navDestination(this.routerMap).mode(NavigationMode.Stack).layoutWeight(1); CustomTabBar() }`。
- 顶部分段切换（TabLayout+ViewPager2，不在 Navigation 内）→ 原生 `Tabs({barPosition: BarPosition.Start})` + `TabContent().tabBar()`（点击/滑动双向同步自带），禁手搓 Row 页签 + Swiper 同步；多 Tab 加 `.barMode(BarMode.Scrollable)`。

<!-- source: arkts-ui-alignment/SKILL.md:L73-133,L178-224 -->
