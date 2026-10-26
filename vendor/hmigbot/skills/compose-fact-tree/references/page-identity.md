# Compose 判页（page identity）—— 替代失效的「按 Activity 名判页」

## 问题
Compose 单 Activity App，所有 NavHost destination 都停在**同一个 Activity**（如
`com.example.jetsnack/.ui.MainActivity`）。`dumpsys activity | grep mResumedActivity`
对每一页返回相同值 → **按 Activity 名判页彻底失效**。route 字符串活在 NavController
进程内存，`dumpsys`（含 `dumpsys activity top`）不导出（实测视图树到 `AndroidComposeView`
就是单个不透明节点，无 route/子 Composable）。

## 判页主键分层（visual-verify android-navigation-playbook 应按此短路）
| 层 | 主键 | 适用 | 侵入 |
|---|---|---|---|
| T0 | `mResumedActivity` Activity 名 | 传统多 Activity App | 零 |
| **T0 短路** | 检测到单 Activity + 高 @Composable → **跳过 T0**（恒退化，别做无效比对） | Compose SPA | — |
| T1（默认）| **内容签名**（本文档） | 任何 App，零侵入，对装好的 APK 直接判 | 零 |
| T2（可选高保真）| NavController route → logcat | 有源码且**愿重编**时 | 改源码+重编 |

> T2 仅当你能重编时用，**不进默认链**——基线 App 的定位是"不可改的真值参照"，重编了就不是基线。
> 且嵌套 NavHost（如 Jetsnack 外层 `home` + MainContainer 内层 `home/feed`）要给**内外两个**
> NavController 都挂 `addOnDestinationChangedListener` 才能拿到精确页；type-safe nav 的 `dest.route`
> 是类全限定名不是可读串。所以 T2 没有提案吹的"一个 listener 零歧义"那么轻。
>
> `testTagsAsResourceId` 同样要改源码重编（实测 Jetsnack 64 个 Compose 节点 resource-id 全空），
> 不是"轻量 opt-in"，并入 T2 类。

## T1 内容签名（默认方案，已真机验证 6/6 + 抗滚动）

### 复合签名（每页 `page_signature`，由 `scripts/gen_page_signatures.py` 生成）
单一"独占锚点集"不够（**Feed 硬伤**：其独占锚点是会滚出视口的合集标题 + 动态零食名）。改用复合：
- `positive[]`：本页跨页**独占**锚点（resolver 用 **any-of** 而非 all，容忍动态项变化）
- `negative[]`：**别页**的强锚点而本页没有的 → **排除法**（专治无稳定独占锚点的页）
- `selected_tab`：底部导航**选中 tab**。⚠️ Jetsnack 自绘底栏 **`selected="true"` 恒为 false 不可用**；
  真正信号是 **「选中 tab 的 label 会作为 `text` 节点出现」**（Feed→`text="HOME"`，Cart→`text="MY CART"`），
  未选中 tab 只有 `content-desc` 图标。tab 标签**自动识别** = 在多数页作 content-desc 出现的串。
- `kind`：`dialog` 浮层签名**优先**于其遮住的页。

### 采集协议（resolver `scripts/resolve_current_page.py`）
1. 判页前**强制 scrollToTop**（向下滑几次露顶部），消"锚点滚出视口"。`--no-scroll` 可关。
2. uiautomator dump → 取所有 `text` / `content-desc`。
3. `selected_tab_live` = 哪个 tab 标签作为 **text 节点**出现（底栏恒可见 → **抗滚动**）。
4. 判定优先级：
   - **① dialog 浮层**：某 dialog 的 positive 命中 → 判它（即便底栏 tab 穿透）。
   - **② 非 tab 全屏页**（`selected_tab=None`，如详情页）：positive 命中且无底栏 tab text。
   - **③ tab 页**：`selected_tab` 锁定候选 → `negative` 命中则否决 → `positive` any-of 提分。
     Feed 这种弱页靠 **(selected_tab=HOME) + (negative 全不命中)** 判出，即便 positive 因滚动/动态变了。
5. 底栏共享 content-desc（HOME/SEARCH/CART/…）一律**拉黑**不进 positive（否则 5 页互相污染）。
6. 动态文本降噪：含数字/货币/超长段落的 token 不当 positive（价格/件数/零食名随数据变）。

### 真机验证（Jetsnack, emulator-5554）
- 离线盲判 6/6 对；live 6/6 对。
- **Feed 抗滚动压测**：滑到底（"Android's picks" 等顶部锚点全滚出）后，`--no-scroll` 仍判对 Feed
  （靠 selected_tab=HOME + negative 全不命中）；默认模式 scrollToTop 还原后照判对。
- Feed vs FilterScreen（都 tab=HOME）：dialog 优先 + Sort/Category 锚点 → FilterScreen；Feed 靠排除法。

## 正交修复：壳/容器节点 aliasing
MainActivity（壳）/ MainContainer（底栏容器）/ Feed 三节点**视觉同屏**（都是 Feed 首屏）。
`gen_page_signatures.py` 给无独立 dump 的壳/容器页标 `visual_alias_of: <visual_start>`（Jetsnack→Feed）。
**只作用于截图/判页层**——导航图里 MainContainer 仍是真实 hub 节点（底栏宿主，inbound 起点语义不能丢）。
双端对比时两端 page_id 要按 alias 对齐；底栏在 4 个 tab 页都在，diff 时底栏选中态差异需单列不算 bug。

## 调用方式（visual-verify 集成）
```bash
# 一次性：首轮遍历各页时存 dump，生成签名
python3 gen_page_signatures.py --tree spec/toolkit-fact-tree.json --dumps spec/visual-verify/page_dumps
# 导航中任意时刻判当前页
python3 resolve_current_page.py --tree spec/toolkit-fact-tree.json --serial emulator-5554 --json
# -> {"page_id":"Feed","confidence":0.92,"selected_tab":"HOME","reason":"..."}
```
