---
name: compose-fact-tree
description: 从 Jetpack Compose App 源码（纯 @Composable + Navigation-Compose / type-safe
  nav / Nav3 / Fragment-hosted）逆向生成与 harmony-migration-toolkit 完全一致的 `spec/toolkit-fact-tree.json`（schema_version=1），让下游
  a2h-spec / app-relationship-tree / arkts-visual-verify 零改动消费。专治 toolkit 啃不动 Compose（无
  XML layout、页面是 @Composable 函数、导航是 navigate 字符串数据流）的场景。当用户说"分析这个 Compose 项目产 fact-tree"、"Compose
  源码分析"、"给 Compose app 产关系树/导航图"、"toolkit 跑不了 Compose"时触发。方法论师承 A2H android-source-analysis
  的分阶段 agentic harness，但产物对齐 fact-tree 而非 feature_tree。
metadata:
  title: Compose 源码 → fact-tree（LLM 源码分析器）
  type: domain
---

> **Codex subagent dispatch convention.** This skill dispatches subagents. In Codex, spawn them with the `spawn_agent` tool and pass `agent_type` = the role name **exactly as written in this skill** — the roles registered under `.codex/agents/*.toml` use the same hyphenated names, so no translation step is involved: `a2h-activity-converter`, `a2h-android-analyzer`, `a2h-closer`, `a2h-fixer`, `a2h-migration-worker`, `ad-profile-builder`, `compose-fact-analyzer`, `hmos-builder`, `scenario-builder`, `visual-fixer`, `visual-fixer-reviewer`. The built-in `general-purpose` agent_type is unchanged. (Claude's `subagent_type` field is written `agent_type` for Codex; `Agent(...)` dispatch calls are `spawn_agent(...)`; there is no `Task` tool in Codex.)
>
> **Join 协议（收口五条款）。** Codex 子代理完成后**不会**唤醒主会话——结果必须由派发方主动收口，违者=静默卡死（实测事故）。
> ① **循环 wait**：每个 `spawn_agent` 句柄用循环调用 `wait_agent` 收口；单次超时只代表"还在跑"，继续再调；**禁止以"等待子代理"为由结束回合**。醒后必调 `list_agents` 确认是谁完成——**完成的唯一合法信号 = `agent_status` 为 `{"completed": …}`，绝不是产物文件的存在/条数**（文件会中途落盘，读半截=实测事故）；completed 态会在数轮后从 list 中消失，所以每次醒来都要及时查。正文所有"等待完成 / join / 到点即收"表述一律指此循环。
> ② **死句柄与验收**：连续 3 次超时后调 `list_agents` 核对，可配 `wait_for_artifact.py` 探产物活性；已 completed 且 summary 可读 → 直接消费；句柄消失且从未观测到 completed → 按断点重派（带原 prompt + 已落盘产物，上限 2 次），禁止继续等待。**completed ≠ 验收通过**：join 点跑 `python3 .agents/skills/a2h-join/scripts/join_gate.py --project .` 验产物完整性，FAIL 视同未取回、按本条重派。
> ③ **收口锚点**：本 skill 最终完成报告前必须收口全部句柄（join_gate exit 0）；正文写明的显式 join 点优先按正文执行。发用户门（Gate）时允许句柄跨 Gate 存活，但 Gate 摘要必须列明未收口句柄清单 + 各自的指定 join 点。
> ④ **放行 ≠ 遗弃**：正文"非阻塞放行/到点即收/降级继续"只推迟收口时机，不豁免收口义务。
> ⑤ **fire-and-forget**：仅正文显式声明"结果丢弃/不 gate"的派发（如 a2h-execute 的 env-prewarm）免收口；审计只认 join_gate 内静态 allowlist，正文声明只是文档层。
> **派发纪律**：`task_name` 必须唯一（带 page-id/slice-id/round-N 后缀）；并行派发前把预期产物清单写 `spec/a2h/_work/expected_<join点>.json`（join_gate 对账用，契约只认派发方、不认子代理自报）；**谁派谁收**——sub-agent 内部需要"等齐 N 片再合并"时禁止嵌套外派后自行退出，要么同步自做、要么把分片清单回报主会话代派（sub-agent 一停止，收口能力即丢）。**契约产物必须出自承担任务的子代理**：重派上限后仍产不出 → 如实报缺并停在未完成态；禁止派发方代写占位产物让 gate 转绿（声明过也不行——绿账必须对应真产物）。

## 0. 定位与边界

**你（LLM）是核心推理引擎，不是脚本执行器。** 你的任务：阅读 Kotlin/Compose 源码，做语义推理，产出**结构事实层** fact-tree。

- **输入**：一个 Jetpack Compose App 的源码根目录（含 settings.gradle(.kts)、build.gradle、Kotlin 源码）。
- **输出**：`<output_dir>/spec/toolkit-fact-tree.json`，**严格遵守** `references/fact-tree-schema.md`（SSOT，与 toolkit-fact-indexer 共用同一份；本 skill 在 `references/` 留了拷贝指针）。
- **责任范围**：只产**结构事实**（pages/fragments/dialogs/components/导航边/flow_graph/features 聚类骨架）。
  - `purpose` / `label` 兜底 / `dependency_graph` / `reach_paths` 语义补全**不在本 skill 范围**——保持 `null` / `[]`，由下游 `app-relationship-tree` 的 LLM 补（和 toolkit-fact-indexer 完全相同的契约）。
- **输出路径纪律（硬性）**：源码目录**只读**，禁止在源码目录内写任何文件；所有产出写到 `<output_dir>/`。中间产物写 `<output_dir>/spec/.cache/compose-fact/`。

> ⚠️ 与 A2H 的关键区别：A2H 产 **feature_tree**（L1-L6 能力层级树，给测试意图用）；本 skill 产 **fact-tree**（pages + 页面间导航**图** + 组件父子，给 visual-verify BFS 用）。能力层级 ≠ 导航边 ≠ 组件父子，**三者形状/高度不同**（详见 `references/why-not-feature-tree.md`），不要套用 L1-L6 推导。

## 1. 执行方式：分阶段 Sub-Agent 委派

师承 A2H android-source-analysis 的 agentic harness。主 Agent（或编排层）按下表顺序派发，**不自行执行各 Phase 推导**。独立调用时也可单 agent 串行跑完，但必须按 Phase 边界推进。

| Phase | 职责 | 产物 |
|-------|------|------|
| Phase 0 | 预扫 + Compose 探测 + 导航方言识别 | `.cache/compose-fact/source-index.json` |
| Phase 1 | 页面发现（哪些 @Composable 是 page/dialog/fragment） | pages/dialogs/fragments 骨架 |
| Phase 2 | **导航图**构建（最难，反虚边/反丢边/抓 fan-in） | navigation.{inbound,outbound} + flow_graph |
| Phase 3 | 组件抽取（flat list + parent_id + triggers + 组件级 navigation） | components[] |
| Phase 4 | features 聚类 + app 元信息 + stats 装配 | 完整 fact-tree |
| Phase 5 | **HARD 自检**（8 schema 闸 + 4 Compose 闸 + 3 parity 闸） | factcheck 报告 |
| Phase 6 |（可选）判页签名，给 visual-verify 用 | page_signature |
| **Phase 7** | **富化对齐**——补到与传统 toolkit 树**字段同构**（preconditions/navigation_contract/inbound_triggers/reach_path），使 arkts-visual-verify **零改**消费 | 富化后的 fact-tree |

---

## Phase 0 — 预扫与导航方言识别

### 0.1 Compose 探测（确认适用）
```bash
SRC=<source_dir>
echo "composable files:"; grep -rl --include='*.kt' "@Composable" "$SRC" | wc -l
echo "res/layout xml:";  find "$SRC" -path '*/res/layout/*.xml' | wc -l
```
若 `@Composable` 文件多、`res/layout` ≈ 0 → 适用本 skill。若两者都多（混合工程）→ 本 skill 产 Compose 侧，XML 侧交给 toolkit-fact-indexer，最后合并（见 0.4）。

### 0.2 识别导航方言（决定 Phase 1/2 用哪个 recognizer）
逐个 grep，一个工程可能并存多种。详细 recognizer 见 `references/nav-dialects.md`：

| 方言 | 探测特征 | 页面=？ 路由=？ |
|---|---|---|
| **D1 string-route** | `NavHost(` + `composable("route")` / `composable(CONST)` | composable lambda 里首个 @Composable 调用；路由=字符串/常量/枚举 .route |
| **D2 type-safe nav** | `composable<Route.X>` + `@Serializable data object/class` | sealed `Route` 子类型即页面 id；路由=类型 |
| **D3 state-object wrapper** | `composable(...)` + `appState::navigateToX` / `xxxState.navigate(...)` | 同 D1，但 nav wrapper 是某 state 类的方法 |
| **D4 Nav3** | `import androidx.navigation3.*` + `NavDisplay(` + `entry<T>` + `rememberNavBackStack` | `entry<T>` 的 T 即页面；导航=back-stack 操作（`backStack.add/removeLast`）|
| **D5 fragment-hosted** | `Fragment` + `ComposeView` / `setContent` + 单 `NavHostFragment` | Fragment→fragments[]；其 Compose 内容为组件 |
| **D6 custom/state** | 无 NavHost，靠 `when(screen){...}` + 状态枚举切换 | when 分支的 @Composable 即页面；导航=状态赋值 |

> **方言缺失 Fallback**：找不到任何 NavHost/NavDisplay → 按 D6（单 Activity setContent 直挂一个根 @Composable，按 `when`/状态切换枚举页面）；再不行退化为「每个 top-level @Composable 且被 setContent 或被路由引用的」当 page，并在 `notes` 标注「nav dialect=unknown，页面集合可能不全」。

### 0.3 建 source-index（机械预扫，可用 grep/Bash 助手）
写 `.cache/compose-fact/source-index.json`，给后续 Phase 定向读取：
- `composables`: 每个 `@Composable fun Name(` → {name, file, line, params, has_navhost}
- `route_consts`: 每个 `const val X = "..."` → {name, value}
- `enum_routes`: 每个 enum class 带 `route` 构造参 → {Enum.MEMBER: route_value}
- `nav_registrations`: 每个 `composable(...)` / `composable<T>` / `entry<T>` → {route_expr, file, line}
- `navigate_sites`: 每个 `.navigate(`/`navigateUp(`/`popBackStack(`/`backStack.add(` → {expr, enclosing_fn, file, line}
- `nav_wrappers`: 每个 fun 名以 navigate* 开头或体内含 `.navigate(` → {name, target_route_expr}
- `interactive_sites`: `clickable`/`combinedClickable`/`onClick =`/`toggleable`/`selectable`/`Slider`/`Switch`/`Checkbox`/`SwipeToDismiss` → {file, line, enclosing_composable}

### 0.4 混合工程合并约定
若 0.1 判定为混合：本 skill 只产 Compose 侧 pages/dialogs；最终与 toolkit-fact-indexer 产物按 `id` 去重 union（同名以 Compose 侧为准），`flow_graph` 取并集，`stats` 重算。

---

## Phase 1 — 页面发现

**核心判据：page = 被注册为导航目的地的 @Composable，*或* 页内 `when(stateVar)` 切换出的全屏内容 @Composable。** 不是所有 @Composable 都是页面（绝大多数是组件）。
> ⚠️ 别只认 NavHost destination！**NavHost destination 内部的 `when(state)` 状态切换同样产页**（最易漏）：引导/wizard pager（`when(currentPage){0->PageOne;1->PageTwo;2->PageThree}`）、页内 tab（`when(selectedTab)`）、多步表单——每个分支的全屏 @Composable 各拆一个 page 节点。判别「拆 vs 不拆（加载/错误态不拆）」+ 顺序取布局序，见 `references/nav-dialects.md` **D6**。Habicat 实测 OnboardScreen 就是 `when(currentPage)` 3 屏，漏拆会让 visual-verify 只截到第 1 屏。

1. 遍历 `nav_registrations`，对每条解析**路由**（见 `references/nav-dialects.md` 的解析规则）：
   - `const val` → 查 `route_consts` 取字面量
   - `Enum.MEMBER.route` → 查 `enum_routes`
   - 字符串模板 `"$PREFIX/$id?..."` → 解析常量前缀，`$var`/`${var}` 占位标记为 dynamic
   - type-safe `composable<Route.Inbox>` → 路由 = `Route.Inbox`（类型名即 id）
   - Nav3 `entry<DetailKey>` → 路由 = `DetailKey`
2. **screen composable** = 该注册 lambda 体内首个 @Composable 调用（跳过 `requireNotNull`/`remember*` 等非 UI 调用）。它就是这个 page 的实现。
3. 给每个 page 写骨架（字段定义严格按 schema §七）：
   ```jsonc
   {
     "id": "<screen composable 名>",          // 唯一；type-safe 用 Route 子类型名
     "type": "Composable",                     // host Activity 用 "Activity"
     "screen_kind": "page",                    // page | dialog | fragment
     "fq_class": "<package>.<Name>",
     "package": "<推断包名>",
     "label": null,                            // LLM 兜底可填，否则 null
     "purpose": null,                          // ⏭ 留给 app-relationship-tree
     "uncertain": false,
     "source": "compose_nav_registration",
     "android_file": "<相对源码根的 .kt 路径>",
     "layout_file": null,                      // Compose 无 XML layout
     "harmony_target": "pages/<name 小写>/Index",
     "logical_feature_id": null,               // Phase 4 回填
     "route": "<解析后的路由字面量>",          // Compose 扩展字段（schema 容忍附加字段）
     "is_start_destination": <是否 startDestination/起始 entry>,
     "contains": [], "shows_dialogs": [],
     "components": [],                          // Phase 3 填
     "navigation": {"inbound": [], "outbound": [], "unresolved_hints": []},
     "reach_paths": [], "notes": null
   }
   ```
4. **Dialog 识别** → `dialogs[]`（screen_kind="dialog"）：
   - 显式弹窗：条件渲染的 `AlertDialog(`/`BasicAlertDialog(`/`Dialog(`/`ModalBottomSheet(`/`Popup(`。
   - **条件 overlay（也算 dialog）**：用 `AnimatedVisibility`/`if(show)` 包裹的**全屏/居中 modal 覆盖层**——典型特征是带 scrim（半透明背景 `Modifier.background(...).clickable{关闭}`）+ 居中卡片/全屏面板 + 一个开关状态控制显隐（如 Jetsnack 的 FilterScreen）。这类语义上是对话框，归 `dialogs[]`，**不**当独立 page（它不是 NavHost destination，没有路由）。
   - 触发它的 page 在其 `shows_dialogs[]` 列出对话框 id；该 page 上对应的开关组件 `navigation.to_page` 指向这个 dialog id。
5. **Fragment 识别**（D5）→ `fragments[]`：每个 `class X : Fragment` 用 `ComposeView`/`setContent`。其内容 @Composable 作为该 fragment 的组件。host page 的 `contains[]` 列出 fragment id。
6. **host Activity**：单 LAUNCHER Activity（如 MainActivity）记一条 `type:"Activity"` 的 page，`contains` 指向它 setContent 的根 @Composable；它通常不是用户停留的「屏」，`label` 可标注为壳。
7. **页内 `when(stateVar)` 状态页**（D6，**务必扫，最易漏**）：对每个 destination 的 screen composable 体，找 `when(stateVar){...}` 形式且分支调用不同全屏 @Composable 的，按 D6 把每个分支拆成独立 page：
   - `id` = 分支 @Composable 名（PageContentOne/Two/Three、OverviewScreen…）；`screen_kind:"in_screen_state"`；`route:null`；`is_start_destination:false`。
   - 这些页**视觉各不相同**（与底栏 tab 壳不同），**不**打 `visual_alias_of`——visual-verify 要逐屏截。
   - 它们之间的推进（`currentPage=N` 赋值、tab 选中）在 Phase 2 建成边（via_component = 下一步按钮 / tab 项）；末屏的 `onComplete()`/外部回调 → 退出该流到下一 destination 的边。
   - 别过度拆：`when(uiState){Loading/Success/Error}` 这类加载/错误态不是页（D6 判别）。

---

## Phase 2 — 导航图（最难，三条铁律防坑）

构建页面间导航边。这是 Route A 两轮 review 反复栽的地方，**以下三条铁律必须执行**：

### 铁律 A：导航是「图」不是「树」——必须抓 fan-in
同一个 page 可被多个 page 跳入（如 Feed/Search/Cart 都 → SnackDetail）。**不要因为某个目的地"已经在某处出现过"就只建一条边**。每个真实触发点都建一条 inbound/outbound。

### 铁律 B：边归属「UI 触发页」，不是「wiring 注册点」——反虚边
回调常被层层透传（`onSnackClick → onSnackSelected → ::navigateToSnackDetail`）。`::navigateToSnackDetail` 的词法位置在 `JetsnackApp`（NavHost 容器），但**用户实际点击在 Feed 的 SnackItem**。
- **边的 `from` = 那个体内真正有 `clickable/onClick` 且该回调最终触发 navigate 的 page**，不是注册/透传点。
- 做法：从 `interactive_sites` 出发反向追——某 page 的某 clickable 调了回调 `cb`，沿 call-site 参数绑定（`Screen(cb = 上层cb / ::wrapper / {…wrapper…})`）做**定点传播（fixpoint）**，解析到最终 nav wrapper 的目标路由 → 目标 page。边记在**发起点 page** 上。
- 透传中间层（自己没有 UI 触发、只把回调往下传的 composable，如 MainContainer/addHomeGraph）**不单独成边**。

### 铁律 C：解不出的运行时路由「记录」不「丢弃」——反丢边
`navigateToBottomBarRoute(route)` / `navigate(someVar)` 这类 target 运行时才定：
- 若能枚举候选（如 bottom-bar 的 tabs = 某 enum 全体）→ 展开成多条边，`is_dynamic:true`。
- 完全解不出 → 写进该 page 的 `navigation.unresolved_hints[]`（`{kind, file, line, evidence, to_hint}`），**绝不静默丢**。
- 返回导航 `navigateUp()`/`popBackStack()`/`backStack.removeLast()` → 建一条 `trigger:"back"` 边到上一页（解不出具体上一页就标 `is_dynamic` + hint）。

### 双写：page 级 + 组件级
下游有两个消费者，**两处都要填**（review 教训：只填 page 级会让 4D 组件层拿不到 target）：
- **page 级**：`pages[i].navigation.outbound[]`（NavEntry：`{to, via_component, trigger, params, is_dynamic, source}`）与对应 page 的 `inbound[]`。
- **组件级**：发起跳转的那个 component 上 `navigation = {to_page, trigger, params, is_dynamic}`，并把 `via_component` 指向它。

### `is_dynamic` 的准确语义（别混淆，否则 B3/B4 失效）
`is_dynamic` 表示 **目标*页面*运行时才能确定**，**不是**"参数运行时才定"。
- `navigate("player/$episodeUri")` → 目标页 = PlayerScreen **确定**，只是 episodeUri 是参数 → **`is_dynamic:false`** + `params:{episodeUri:"runtime"}`。
- `navigate(someRuntimeRouteVar)` / `navigateToBottomBarRoute(route)`（目标页随运行时变量/枚举）→ **`is_dynamic:true`**。
- back（`navigateUp`/`popBackStack`，上一页由运行时栈决定）→ `trigger:"back"`，目标解不出时 `to:null`。
> ⚠️ 把"仅参数 runtime"误标 dynamic 会让该边逃过 factcheck B3/B4 双写校验（豁免按 `trigger==back || to==null`，不是按 is_dynamic）。`stats.dynamic_targets` 只数真·目标未知的边。

### flow_graph
聚合所有 `outbound` 成 `flow_graph.{nodes, edges}`。**`edges` 数量必须 == 所有 outbound 之和**（HARD 闸 6）。

---

## Phase 3 — 组件抽取（flat list + parent_id）

对每个 page/dialog/fragment，从其 screen composable 出发，**递归进子 @Composable**（同文件优先，限深 2-3，覆盖 Feed→FeedList→SnackItem 这种委托）收集**可交互元素 + 必要布局容器**。

- 收集对象：`Button/IconButton/TextButton/FilledTonalButton/FloatingActionButton/TextField/OutlinedTextField/Checkbox/Switch/Slider/FilterChip/RadioButton`，以及 `Modifier.clickable/combinedClickable/toggleable/selectable`、`SwipeToDismissBox`。布局容器 `Column/Row/Box/LazyColumn/LazyRow/Scaffold` 用于建 `parent_id` 邻接。
- 每个 component（字段严格按 schema §七 Component）：
  ```jsonc
  {
    "id": "<page小写>_<type小写>_<n>", "type": "<Compose 控件名>",
    "parent_id": "<同 page 内父容器 id 或 null>", "uncertain": false,
    "text": "<stringResource(R.string.x) 解析后的文案 或 字面量 或 null>",
    "hint": "<TextField placeholder 或 null>", "image_resource": null,
    "content_desc": "<contentDescription 或 null>", "on_click_attr": null,
    "is_interactive": <有 onClick/clickable/手势=true>,
    "visibility": "visible",                      // AnimatedVisibility/if 条件 → 见 visible_when
    "triggers": [<"click"|"long_press"|"swipe"|"toggle"|"value_change">],
    "purpose": null,                              // ⏭ 留给下游
    "action": null,
    "navigation": <若触发跳转: {to_page,trigger,params,is_dynamic}, 否则 null>,
    "visible_when": "<条件渲染的判据，否则 null>",
    "items": null,
    "behaviors": [{"event":"click","method":"clickable","file":"...kt","line":N,"enclosing_fn":"..."}],
    "source_anchor": {"file":"...kt","line":N}, "notes": null
  }
  ```
- **空实现 stub 检测（A2H 在 Compose 上发现的坑，务必做）**：`onClick = { }` / `onClick = { /* todo */ }` / 体为空 → `is_interactive:true` 但 `navigation:null`，`notes:"no-op stub（onClick 空实现，无视觉结果）"`。下游 visual-verify 不应期待它有跳转。
- **🔑 `text` / label `@string` 真值解析铁律（下游靠它点击 + 判到达，取错就点错/判错页）**：
  - `stringResource(R.string.X)` / `R.string.X` / `getString(R.string.X)` **必须解析到 strings.xml 里的实际值**，且要**跨所有模块**搜 `**/src/**/res/values[-<locale>]/strings.xml`——资源常不在 UI 模块，而在 `data`/`common`/`lib_*` 等模块（Habicat 实测 `R.string.skin_mode` 在 `data` 模块 values-zh = "外观显示"，UI 模块根本没有）。
  - locale 取**基线设备将运行的 locale = 应用默认 locale**（国产应用通常中文 → 优先 `values-zh`；无 locale 限定的 `values/` 是兜底）。见 Phase 7.4。
  - **严禁**用资源 **key 名**（`skin_mode`）、路由名、或 page-id 的 CamelCase 反推（`SkinModeScreen`→"皮肤模式"）当文案——这正是 Habicat label 取错的根因（树写"皮肤模式"，实屏"外观显示"）。
  - 解析不到 → **保留字面 `R.string.X` ref + `uncertain:true`**，**不要**编一个像模像样的译名。运行时拼接/格式化的动态文案 → `text` 置可辨识占位 + 标动态。
- `purpose` 一律 null。

---

## Phase 4 — features 聚类 + app 元信息 + 装配

1. **features[]**（schema §六，**结构骨架，不是业务功能**）：按**包/目录**聚类 pages（如 `ui/home/*`→一个 feature），或若同目录已有 A2H `feature_tree.json` 可借其 L1 域做种子。每条：
   ```jsonc
   {"id":"compose.<dir>", "label":"<目录名 Title>", "screens":[<page id...>],
    "top_tokens":[...], "strategy":"compose_package_cluster"}
   ```
   `logical_feature_id` 回填到各 page。
2. **app**：`package`（build.gradle `applicationId` / Manifest）、`launcher_short`（LAUNCHER Activity 或起始 page）、其余缺则 null。
3. **source** 段：`toolkit:"compose-fact-tree"`、`generator.skill/script_version`、`android_root`、`generated_at`、`resolution_notes`（route_consts/enum_routes/registrations/nav_wrappers 计数 + nav_dialects 命中）。
4. **dependency_graph**: `null`（⏭ app-relationship-tree 补）。
5. **reach_paths**: 每个 page `[]`（无 toolkit ui_paths）。可选：从 start destination 做一次轻量 BFS 填 `{display, depth, source:"compose_bfs", ref:null}`，但**默认 `[]`**保持与 toolkit 契约一致。
6. **stats**: 按 schema §十 逐字段算（total_pages/fragments/dialogs/components/navigation_edges/features、dynamic_targets、uncertain_items、components_with_parent…）。
7. 写 `<output_dir>/spec/toolkit-fact-tree.json`。**`$schema_version:1` 是权威键**（schema SSOT §三、下游 `assert fact["$schema_version"]==1`）；为与 toolkit-fact-indexer 产物外观一致也冗余写一个 `schema_version:1`。stats 的 `total_components`/`components_with_parent`/`total_navigation_edges` 必须与实际一致（闸7 现已校验，写错会红）。

---

## Phase 5 — HARD 自检（不可放宽）

跑 `scripts/factcheck.py <output_dir>/spec/toolkit-fact-tree.json`。它执行：

**A. schema §十二 的 8 项结构闸**（与 toolkit-fact-indexer 同款）：
1. `$schema_version==1`；2. 8 顶层字段齐；3. pages/fragments/dialogs id 唯一；4. 所有 `component.navigation.to_page` 可达或 `is_dynamic`；5. `parent_id` 闭合；6. `flow_graph.edges`==所有 outbound 之和；7. stats 一致；8. 所有 record `reach_paths` 是 list（非 null）。

**B. Compose 专项闸 4 项**（防本 skill 特有失真）：
- **B1 无孤儿页**：每个非 start page 必须有 ≥1 条 inbound，或在 `notes` 显式说明（否则 visual-verify BFS 到不了）。
- **B2 无丢边**：每个 `navigate_sites` 解不出 target 的，必须出现在某 page 的 `unresolved_hints` 或被展开成 dynamic 边——不允许凭空消失。
- **B3 无虚边**：`flow_graph.edges[].from` 不得是「纯透传 / 无 UI 触发」的 composable（每条边的 from 必须在某 component 上有对应 `navigation.to_page`）。
- **B4 page/组件级一致**：每条 page 级 outbound 必须能在该 page 的某 component 的 `navigation` 找到对应（双写一致）。

**C. parity 闸 3 项**（Phase 7 enrich_parity.py 必须已跑，否则薄树让 arkts 退化猜）：
- **C1 navigation_contract 齐备**：每个 record 有 `navigation_contract.trigger_actions[0].type` + `verify_signal.text_contains`。
- **C2 inbound_triggers 非空**：非 start/launcher 页必须有 inbound_triggers（含嵌套 NavHost 入口的 boot 兜底）。
- **C3 reach_path 是 list**。

任一 ❌ → 修正后重跑，直到全绿才算交付。注意 C 闸要求先跑 Phase 7。

---

## Phase 6 —（可选）判页签名，给 visual-verify 用

Compose 单 Activity 下 visual-verify「按 Activity 名判页」失效（所有页同一个 Activity）。本 skill 可额外产出**内容签名**让下游判页。详见 `references/page-identity.md`（已真机 6/6 验证 + 抗滚动）。

- **壳/容器 aliasing**（Phase 1 就该标）：视觉同屏的壳（Activity）/容器（底栏宿主，如 MainContainer）节点标 `visual_alias_of: <visual_start_page>`，**只作用于截图/判页层**，导航图里仍保留为真实 hub 节点（inbound 起点语义不能丢）。
- **签名生成**（首轮遍历各页存好 `<page_id>.xml` dump 后跑）：
  ```bash
  python3 scripts/gen_page_signatures.py --tree <tree>.json --dumps <dir of page dumps>
  ```
  给每页写 `page_signature = {positive[], negative[], selected_tab, kind}`：positive=跨页独占锚点（resolver any-of）；negative=别页强锚点本页无（排除法，专治 Feed 无独占锚点）；selected_tab=选中 tab 的 label（作 text 节点出现，**不是** `selected="true"`，那个 Compose 自绘底栏恒 false）；底栏共享 content-desc + 动态文本（数字/货币/超长）自动剔除。
- **运行时判页**：`python3 scripts/resolve_current_page.py --tree <tree>.json --serial <emu> --json` → `{page_id, confidence, selected_tab, reason}`，自带 scrollToTop 采集协议 + dialog/全屏/tab 三级优先。

## Phase 7 — 富化对齐（让 arkts-visual-verify 零改消费）

> **为什么必须做**：compose-fact-tree 默认产「薄树」（只有 navigation.{inbound,outbound} + 组件级 nav）。
> 而 arkts-visual-verify 是为**传统 toolkit 树**写的——它消费 `preconditions`（分 trip）、
> `navigation_contract`（点击导航 + 到达校验）、`inbound_triggers`（launcher walk 提示）、
> `reach_path`（真点遍历）。薄树缺这些 → arkts 退化成**现场猜** → 漏 onboarding 页、乱标 BLOCKED。
> 传统流水线是 toolkit 出基础树后由 **app-relationship-tree** 跑 Phase 2.3–2.7 富化补上的；
> **app-relationship-tree 不能直接用于 Compose**（它 grep `startActivity`+`findViewById`+layout xml +
> 用 AndroidManifest 删节点 → 对单 Activity Compose 会把 36/37 页当假节点删掉）。所以本 skill
> **自产**这些字段（数据它天生最准——正向解析 navController，不用反推）。详见
> `references/enrichment-parity-spec.md`（逐字段 schema + 消费点 file:line + 派生规则）。

**7.1 唯一需读源码的部分：login/VIP 门控扫描 → `preconditions`**（其余字段全可从树机械合成）。
扫 composable + NavHost 源码，识别：
- 路由被 `isLogin`/`requiresLogin` 守卫，或未登录时 `navigate(Login){popUpTo...}` 重定向
  → 该页加 `{"kind":"login_required","evidence":"<守卫表达式>","evidence_file","evidence_line","source":"compose_gating_scan"}`
- `isVip`/`subscription`/会员 守卫 → `{"kind":"vip_required",...}`
- 未登录条件重定向到 Login → `{"kind":"nav_redirect_target","evidence":"未登录 → LoginScreen",...}`（evidence 必含「未登录」，classify_trip 靠子串匹配）
- ⚠️ **onboarding/首启页（Privacy/Onboard/Login/Character…）不加任何 precondition**——
  arkts 默认 `pm clear` 冷启动 walk + dismiss_popups 关引导弹窗 + 命名 pattern 已把它们归 trip_1，
  天然走通并截图。只需 Phase 7.3 给它们 `from_state:cold_start` + boot inbound_trigger + verify 锚点。

**7.2（建议）补 `page_signature.positive` 作 verify 锚点**：Phase 6 若没跑，给每页补 1–2 个
跨页独占、会渲染在屏上的稳定文本（页标题优先）。enrich_parity 的 verify_signal 优先取它，
取不到才退化到「页内最长非交互 Text → page.label」，质量更高。

**7.3 跑机械合成脚本**（确定性，不读源码）：
```bash
python3 scripts/enrich_parity.py <output_dir>/spec/toolkit-fact-tree.json --in-place
```
它从树已有数据合成：`inbound_triggers`（反转 flow_graph.edges + 组件 text/label/source_anchor）、
`navigation_contract`（trigger_actions[0].label 取 inbound 边的组件 text；verify_signal 走兜底链；
contract_uncertain 派生）、`reach_path`(+companions，多源 BFS)、`construction_mode="code_only"`、
`truly_isolated`/`parent_in_nav` 等 stub。**不碰 preconditions**（7.1 LLM 已填）。

**7.4 locale 铁律**：`trigger_actions[].label` 与 `verify_signal.text_contains` 要匹配**设备上实际渲染的文案**。
国产应用源码串多为中文 → fact-tree 标签用**应用默认 locale（中文）原串**，且**基线安卓设备跑同一 locale**
（别在树里翻译成英文）。`stringResource(R.string.x)` 解析到默认 `values/strings.xml`；运行时动态文本
置 `label_dynamic:true` 靠 trigger_view_id(testTag) 兜底。

跑完重跑 Phase 5 factcheck，C 闸应转绿（15/15）。

## 交付物清单
- `<output_dir>/spec/toolkit-fact-tree.json` （主产物，**已过 Phase 7 富化**——与传统树字段同构）
- 每页带 `preconditions`(7.1) / `navigation_contract` / `inbound_triggers` / `reach_path`(7.3)，可选 `page_signature` / `visual_alias_of`（Phase 6）
- `<output_dir>/spec/.cache/compose-fact/source-index.json` （中间，可留痕）
- 终端打印：`pages=N dialogs=K fragments=M components=C edges=E features=F | gates: 15/15 PASS`

## 参考
- `references/fact-tree-schema.md` — schema SSOT（产物唯一事实来源）
- `references/nav-dialects.md` — 6 种 Compose 导航方言的 page/route/edge 解析规则
- `references/why-not-feature-tree.md` — 为何能力层级≠导航边≠组件父子（避免套用 A2H 的 L1-L6）
- `references/page-identity.md` — Compose 单 Activity 判页（替代失效的 Activity 名判页；内容签名 + 抗滚动/弹窗）
- `references/enrichment-parity-spec.md` — **Phase 7 富化字段逐条 schema + arkts 消费点 file:line + Compose 派生规则**（must-have vs cosmetic）
- `scripts/factcheck.py` — 15 项 HARD 闸校验器（A 结构8 + B Compose4 + C parity3）
- `scripts/enrich_parity.py` — **Phase 7 机械富化**（合成 navigation_contract/inbound_triggers/reach_path 等，对齐传统树字段）
- `scripts/gen_page_signatures.py` / `scripts/resolve_current_page.py` — 判页签名生成 + 运行时判页（Phase 6）
