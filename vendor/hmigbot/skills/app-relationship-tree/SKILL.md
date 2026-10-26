---
name: app-relationship-tree
description: 在 `toolkit-fact-indexer` 已产出的 `spec/toolkit-fact-tree.json` 上做**多源补全**——把
  Android 源码、a2h-spec 的 `spec/baseline/ui/page_*.md` / `feature-index.md`、android-ui-graph-builder
  产物等作为 toolkit 产物的补充，把 toolkit 漏掉 / 不准 / 不全的字段都补上，包括：补 purpose、补 inbound_triggers
  触发链、补 preconditions 业务前置态、补 dependency_graph 架构分层、补 reach_paths 孤儿。**必要时甚至可以新增 node**（toolkit
  没识别但 spec / 源码明确描述的页面或弹窗）。**原地修改 fact-tree.json，不产新文件**。当用户说"补充 fact-tree"、"补 description"、"补
  purpose"、"完整化关系树"、"app-relationship-tree"、"丰富 toolkit 产物"、"产 dependency_graph"、"补导航链"、"补登录态"、"补前置条件"时触发。
metadata:
  tags:
  - analysis
  - enrichment
  - fact-tree
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

> **路径约定**：下文 `$SKILLS_ROOT` = 本套 skills 的安装根目录。执行任何脚本前先设一次：`SKILLS_ROOT="$(cd "$(dirname 本SKILL.md)/.." && pwd)"`（用户级安装=`~/.agents/skills`；项目级=`<project>/.agents/skills` 或 `<project>/skills`）。

# app-relationship-tree — toolkit-fact-tree 多源补全器（v6.3）

## 1. 定位（v6.3 重定位 — 2026-05）

**核心使命**：**完善 toolkit-fact-indexer 产出的 fact-tree**。toolkit 是确定性脚本，受限于"只能从 toolkit 的 12 个 JSON 抽事实"——任何 toolkit 没追到 / 没识别 / 没语义化的内容都是本 skill 的补全对象。

**补全的 4 种基本动作**：

| 动作 | 例子 | 用什么数据源 |
|---|---|---|
| **(a) 补字段** | toolkit 给的 record 有 `purpose=null` / `inbound=[]` / 缺 `preconditions[]` | 源码 + page_*.md + LLM 推断 |
| **(b) 校正字段** | toolkit 错误填值（fq_class 错包、自循环 inbound 等） | 源码反查正确值 + 启发式 |
| **(c) 新增节点** | toolkit 没识别的 page / dialog / fragment，但 spec / 源码明确描述 | 扫 a2h-spec `page_*.md` 找 toolkit 缺失的 record 名，按真实 source file 创建 record |
| **(d) 删除节点** | toolkit 误识别（`_promoted_page_*` 这种合成 ID 不对应真实 Activity） | grep AndroidManifest 验证；不在 manifest 的 promoted Activity 删 |

| 这个 skill | 做 | 不做 |
|---|---|---|
| 输入 | `spec/toolkit-fact-tree.json`（必须先跑 toolkit-fact-indexer）+ Android 源码根 + `spec/baseline/ui/page_*.md`（如有）| — |
| 输出 | **原地修改** `spec/toolkit-fact-tree.json` | 产新 JSON 文件 |
| LLM 补 `purpose` | ✅（page / fragment / dialog / component 全级别） | — |
| LLM 补 `inbound_triggers` 导航触发链 | ✅ 读源码反查 `startActivity(B)` 调用点 → 抽 onClick / button label / view id | — |
| LLM 补 `preconditions` 业务前置态 | ✅（toolkit-fact-indexer enhancer 已经补部分，本 skill 用 spec 校验 + 扩充：免费次数 / VIP 等级 / 必填参数等）| — |
| LLM 推 `dependency_graph.layers` | ✅（feature → 架构层级映射） | — |
| 启发式补 `reach_paths` 孤儿 | 🟡 可选 | — |
| **新增 node**（page/fragment/dialog） | ✅ 扫 a2h-spec page_*.md / 源码命名，发现 toolkit 漏识的 record | — |
| **删除假节点**（toolkit 误识别） | ✅ 用 AndroidManifest 校验 Activity 真实性，剔除 `_promoted_*` 等不对应真实类的 record | — |
| 校正 fq_class 错包路径 | ✅ 反查源码 `package xxx` 行确定真实包路径 | — |
| 改 toolkit 真正的事实字段（toolkit 已正确给出的，不能瞎改） | — | ❌ **铁律：toolkit 给的对的不能改** |
| 重新算 reach_paths 全图 / 重新建 nav graph | — | ❌ 已由 fact-indexer 完成；本 skill 只补漏不重算 |
| 产 `spec/app-relationship-tree.json` | — | ❌ **v6 删除该文件**，下游直接读 fact-tree |

> **核心原则（v6.3 落地）**：toolkit 产物是基础，本 skill 利用源码 + spec 把任何缺失 / 错误 / 不完整都补全。**fact-tree 的最终质量由本 skill 负责**——下游读到的版本是经过本 skill 校准的。

> **删除的旧 v6 误解**：早期 SKILL 把本 skill 限定为"只补 purpose"。这个限定 v6.3 已经撤销。

## 1.1 为什么要补 inbound_triggers（v6.2 关键变化）

toolkit 的 `navigation_graph.json` 在反射 / 间接 startActivity / FragmentTransaction 等场景下追不到边，导致 `inbound = []` 的 record 在 AIPPT 里高达 44 / 57。下游 visual-verify Phase Alpha 没办法做"点击优先、指令兜底"的 BFS——因为不知道**从哪个屏点哪个按钮**能到达本 record。

`am start` 直跳虽能拉起 Activity，但会**跳过 button 链路的验证**——HMOS 端那个按钮根本可能没接逻辑，visual-verify 却拿不出差异。

所以 app-relationship-tree 必须读源码反查触发链，填到一个新字段 `inbound_triggers[]`：

```jsonc
"AccountInfoActivity": {
  ...
  "inbound_triggers": [
    {
      "from_page": "MineFragment",
      "trigger_method": "onAccountClick",      // 调用栈源头方法
      "trigger_view_id": "tv_account_entry",   // 触发它的 View id（layout xml）
      "trigger_label": "账号信息",              // 该 View 的 text/content-desc
      "evidence_file": "MineFragment.kt",
      "evidence_line": 142,
      "source": "llm_source_read"
    }
  ]
}
```

下游 visual-verify 拿到 `inbound_triggers[0]` 就能在 host 屏上找"账号信息"clickable 节点点击。点不到再 fallback `am start`。

---

## 2. 执行流程（5 个 phase）

```
Phase 1:   探测 fact-tree                                       ~1s
    ↓
Phase 1.5: 节点级校准（v6.3 新增）                              ~30s
    ↓
Phase 2:   LLM 补 purpose                                       ~分钟级
    ↓
Phase 2.3: 多源 BFS reach_path（v6.3 复活 — 确定性脚本）         ~1s
            scripts/compute_reach_paths.py
            - 多源 BFS（launcher + 所有 page 当 entry）
            - outbound + inverse-inbound 取并集
            - 隐式 contains/shows_dialogs → 边
            - 名字启发式 + Tier 2 不动点迭代
            - 输出 reach_path = page-id + trigger token 交替序列
            - 标 truly_isolated（无源码调用方）
    ↓
Phase 2.5: LLM 补 inbound_triggers 导航触发链                   ~分钟级
    ↓
Phase 2.6: LLM 补 navigation_contract（v6.4 新增 — 根因解）     ~分钟级
            scripts/compute_navigation_contract.py
            - 给每个 Fragment / Dialog 输出精确 UI 导航合同
            - 字段：relationship_kind / trigger_action / verify_signal
                    / wizard_index / exit_action_to_next（仅 wizard）
            - 数据源：page_md + Android 源码（ViewPagerAdapter /
                     FragmentTransaction / DialogFragment.show）
            - 输出 + 确定性源码验证（不通过标 contract_uncertain）
            - 下游 visual-verify v3.9 按合同精确点击 + 强 verify_signal
            - 详见 §2.6
    ↓
Phase 2.7: LLM 扩充 preconditions 业务前置态（v6.3）            ~分钟级
    ↓
Phase 3 (可选): 启发式补 reach_paths 孤儿                        ~1s
    ↓
Phase 4:   LLM 推 dependency_graph.layers                       ~30s
    ↓
Phase 5:   自检 + 写回 fact-tree.json                            <1s
```

### Phase 1: 探测 fact-tree

```python
import json, sys
F = "spec/toolkit-fact-tree.json"
if not os.path.exists(F):
    print("❌ 缺 spec/toolkit-fact-tree.json，请先跑 toolkit-fact-indexer")
    sys.exit(2)
ft = json.load(open(F))
assert ft["$schema_version"] == 1
```

如果 fact-tree 不存在，**自动调起 toolkit-fact-indexer**（它内部处理"toolkit 产物是否存在"逻辑）。

### Phase 1.5: 节点级校准（v6.3 新增 — 重点）

**目的**：toolkit 产出有 3 类节点级别问题，必须先清洗才能保证后续 phase 工作的语义是干净的：

| 问题 | 怎么发现 | 怎么处置 |
|---|---|---|
| **假 Activity**（`_promoted_*` 等合成 ID 不对应真实 class） | grep AndroidManifest，看 record.id / record.fq_class 是否在 `<activity>` 节点里 | 删除该 record；同时清掉其它 record 中指向它的 inbound/outbound 边 |
| **fq_class 错包路径**（如 `cn.sanfate...page.X` 实际类在 `cn.sanfate...dialog.X`）| 在 source 里 grep `class XClassName` 得到真实文件路径，反推真实 package | 把 `fq_class` 改为正确 FQ；同时 `android_file` 也改 |
| **toolkit 漏识的节点** | 扫 `spec/baseline/ui/page_*.md` 的标题/章节，匹配 fact-tree 没有的 record id；或扫源码 `class .*Activity\|class .*Fragment\|class .*Dialog : ` 找 toolkit 漏的 | 新增 record：从源码 + page_*.md 抽 id / type / fq_class / android_file / purpose 模板字段；标 `source: "app_relationship_tree_added"` |

```pseudocode
# 1. 假 Activity 校验
manifest_activities = read_AndroidManifest("AndroidManifest.xml")
for r in fact_tree.pages[:]:
  if r.type == "Activity" and r.id.startswith("_promoted_"):
    # 用 fact-tree 里另一条同样 source-file 的真 record 兜底
    real = find_other_record_by_android_file(r.android_file)
    if real:
      merge_edges(real, r)  # 把 r 的 inbound/outbound 转给 real
      fact_tree.pages.remove(r)

# 2. fq_class 错包校正
for r in records:
  if r.fq_class and "." in r.fq_class:
    if not source_file_has_package(r.android_file, r.fq_class.rsplit(".",1)[0]):
      # 不匹配，反查真实 package
      real_pkg = grep_package_in_source(r.android_file)
      r.fq_class = real_pkg + "." + r.id

# 3. 漏识节点补充
spec_records = scan_page_md_titles("spec/baseline/ui/page_*.md")
for spec_id in spec_records:
  if spec_id not in [r.id for r in records]:
    # 扫源码找 class
    src = grep_class_definition(spec_id)
    if src:
      records.append({
        "id": spec_id,
        "type": classify_type(src),
        "fq_class": extract_fq(src),
        "android_file": src.file,
        "source": "app_relationship_tree_added",
        ...
      })
```

**重要约束**：只删 / 改 / 加节点本身的 metadata，不要改 toolkit 已正确填的字段（components / behaviors / source_anchor 等）。被删除的 record 如果有 inbound/outbound 引用，要 merge 到等价的真 record 上（按 android_file 同一性）。

### Phase 1.6: 源码 popup 类正向扫描（v6.5 新增）

**目的**：补 Phase 1.5 "page_*.md 反查" 的鸡生蛋盲区。Phase 1.5 line 154-168 的反向逻辑要求"spec 里已有 page_md → 才补 fact-tree"——如果 toolkit 没识别 → fact-tree 没记录 → a2h-spec 没生成 page_*.md → 永远触发不了。本 phase 改成**正向独立扫描**：源码有但 fact-tree 没有，**直接**补，不依赖 spec。

**实现**：脚本 `scripts/scan_popup_classes.py`，~1 秒跑完。

**扫描规则**：

1. `rg --files` 列所有 `(DialogFragment|BottomSheetDialogFragment|BottomSheetDialog|BottomDialog|Dialog|Popup|Window|Sheet).(kt|java)$` 候选文件
2. 路径过滤：排除 `src/test/`、`src/androidTest/`、`build/`、`generated/`、`xpopup/core/` 等
3. 文件名排除：XPopup 库自身（`BasePopupView` 等）+ 业务侧 Base 抽象基类（`BaseDialog`、`BaseDialogFragment`、`CenterBottomFragmentDialog`、`BaseBottomFragmentDialog` 等）
4. 对每个候选文件抽 `class Name [(...)] : Parent(...)` 子句（含 Kotlin 主构造器括号平衡处理）
5. **继承链传递闭包**：扫所有 .kt/.java（不止候选文件）建 `child→parent` 全图 → 闭包传递。`ColorPickerDialog → BubbleDialog → DialogBase` 能跨文件追到根
6. **白名单匹配**：祖先链中只要有以下任一即入选：
   - Dialog 系：`Dialog` / `AlertDialog` / `AppCompatDialog` / `DialogFragment` / `AppCompatDialogFragment` / `BottomSheetDialog` / `BottomSheetDialogFragment` / `DialogBase`
   - XPopup 系：`BasePopupView` / `AttachPopupView` / `CenterPopupView` / `BottomPopupView` / `FullScreenPopupView` / `DrawerPopupView` / `ConfirmPopupView` / `ImageViewerPopupView` / `PartShadowPopupView` / `PositionPopupView` / `HorizontalAttachPopupView` / `BubbleAttachPopupView`
   - 原生：`PopupWindow`
7. **命名兜底（uncertain=true）**：白名单未命中、但类名以 `Dialog/Popup/Window/Sheet/BottomDialog` 结尾 **且** 文件路径包含 `/dialog/`、`/popup/`、`/popwindow/`、`/bottomsheet/`、`/sheet/`、`/widget/`、`/view/` 之一 → 入选
8. **去重**：与已有 `pages + fragments + dialogs` 的 id 比对，已存在则跳过
9. **layout 检测**：`setContentView(R.layout.x)` / `LayoutInflater.inflate(R.layout.x)` / XPopup `getImplLayoutId()` 返回 `R.layout.x`
10. **construction_mode**：layout 命中 → `"layout_xml"`，否则 `"code_only"`

**新增字段**：
- `source: "app_relationship_tree_added_class_scan"`（区别于 Phase 1.5 的 `app_relationship_tree_added`）
- `construction_mode: "layout_xml" | "code_only"`（下游 a2h-spec Phase B 按此分支选页面结构模板）
- `uncertain: true`（仅命名兜底入选时）

**与 Phase 1.5 + fact-indexer 的互补关系**：

| 机制 | 覆盖场景 | 落地层 |
|---|---|---|
| fact-indexer 主链 | toolkit JSON 已识别的 page/fragment/dialog | fact-indexer |
| fact-indexer v1.3 popup-layout-prefix promotion | layout 文件名带 `dialog_/popup_/pop_` 前缀（与类名无关） | fact-indexer |
| Phase 1.5 反向 page_md 扫描 | spec 已写 page_md 但 fact-tree 漏的 | app-relationship-tree |
| **Phase 1.6 正向类名扫描（本 phase）** | **源码有 popup 类但 fact-tree 和 spec 都没有的** | **app-relationship-tree** |

三层互补，可同时命中同一 popup（按 id 去重），无重复。**Phase 1.6 是补漏的最后一道兜底，必须跑。**

**已知漏识**（留给后续 LLM phase 兜底）：
- XPopup 匿名子类：`new XPopup.Builder().asCustom(object : CenterPopupView{...})` —— 无独立类名
- factory 工厂构造：无独立 `*Dialog/*Popup` 类，靠运行时 `DialogFactory.create(type)`
- 命名不含 Dialog/Popup/Window/Sheet 后缀的（如 `ColorPicker`、`FontSettings`）

**自检（写入 stats.enhancers.app_relationship_tree_class_scan）**：
```json
{
  "candidates_total": 108,
  "added": 65,
  "skipped_existing": 43,
  "by_match": {"whitelist": 64, "naming_fallback": 1},
  "by_construction": {"layout_xml": 29, "code_only": 36}
}
```

### Phase 2: LLM 补 purpose（主任务）

> **铁律**：
> - LLM **只能填** `purpose` / `label`（兜底）/ `action` / `visible_when` / `items[].purpose` / `notes`
> - LLM **禁止改** navigation 边、source_anchor、id、type、parent_id、文件路径、flow_graph、features、stats、reach_paths
> - 改了 toolkit 事实字段 → 视为污染，重做

**遍历策略**：

```
读 spec/.cache/fact-tree/source-index.json (toolkit-fact-indexer 已产) 拿锚点

FOR EACH record IN pages + fragments + dialogs:
  IF record.purpose is null:
    优先级 1: 找 spec/baseline/ui/page_{record.id}.md 的 ## page structure 段，直接抄
    优先级 2: Read 源码片段（source_anchor.line ± 20 行）；缺锚点则 Read layout 前 60 行
    优先级 3: 启发式 fallback（从 id + label + type 推一句）
    立即落盘 fact-tree.json（断点续跑安全）

  FOR EACH component IN record.components:
    IF component.purpose is null:
      优先级 1: 同上，从 page_spec 找
      优先级 2: Read component.source_anchor 锚点 ±30 行源码
      优先级 3: 启发式 fallback（从 type + text + id 推一句）
      立即落盘
```

**LLM purpose 约束**：

```
12-30 字，动词开头；
不许写 ArkTS 实现细节（"应使用 Column 包裹"等）；
不许写假设性内容（"可能用于..." → 不确定就写"用途待确认"）；
不许翻译 type 名（不要写"按钮组件，名为 Button"）

例:
  Button text="登录"        → "触发登录流程，弹出登录页"
  RecyclerView id=rv_feed   → "Feed 信息流列表，垂直滚动"
  CustomShimmerWidget       → "骨架屏加载占位动画"
```

**LLM 还可以补 `notes` 字段**：toolkit 解不出的 trigger / 反射调用 / 业务怪点，写一句中文备注避免下次踩坑。

### Phase 2.3: 多源 BFS reach_path（v6.3 — 确定性脚本，复活自老版）

**为什么独立成 Phase**：toolkit-fact-indexer 给的 `reach_paths` 实际是 toolkit ui_paths.json 的 action segments（"在某屏调用了什么方法"），**不是"如何到达某屏"**。下游 visual-verify v3.8 要"点击优先"，需要真正的 root→leaf 可点击序列。本 phase 用一个 277 行的确定性 BFS 脚本计算干净 reach_path。

**怎么跑**：

```bash
python3 $SKILLS_ROOT/app-relationship-tree/scripts/compute_reach_paths.py \
    spec/toolkit-fact-tree.json
```

**算法摘要**（详见脚本顶部 docstring）：

```
1. 建有向图：
   - 显式 outbound + 反向 inbound 取并集（toolkit 数据不对称的容错）
   - 隐式 contains[] → fragment 边（"show_fragment_X"）
   - 隐式 shows_dialogs[] → dialog 边（"trigger_X"）
   - 名字启发式补漏识的 host：
     * FragmentGuide* / *GuideFragment → GuideActivity
     * FragmentHome / *RecommendFragment / *HomeFragment → HomeActivity
     * MineFragment / WorksFragment → HomeActivity（底部 Tab）
   - fuzzy match $\\d+ 后缀（HomeActivity$showCampaignDialog ≡ ...$1）

2. 多源 BFS：launcher 优先 + 其它 page 兜底当 entry，
   合并各源 reach 结果（节点只取第一次被发现的最短路径）

3. Tier 2 不动点迭代（最多 20 轮）：
   父被 reach 后子节点（含启发式 host）跟上

4. 输出 reach_path[i].e["reach_path"] = 节点 id 与 trigger token 交替的数组：
   ["SplashActivity","goto","HomeActivity","tap","MineFragment",
    "trigger_AccountInfoActivity","AccountInfoActivity"]
```

**AIPPT 实测**：57/57 = 100% 覆盖。仅 2 个 single-node 是数据缺陷（promoted 假节点 / 没走 companion helper 的直 Intent），靠 Phase 1.5 / Phase 2.5 修。

**铁律**：
- 本 phase 是**纯脚本**，不调 LLM
- 只**新增** `reach_path` 字段，不动 toolkit 已有字段
- reach_path 长度 1 的 record 标 unreached，下游知道是孤儿

### Phase 2.5: LLM 补 inbound_triggers 导航触发链（v6.2 关键）

> **铁律**：
> - LLM 读源码 grep `startActivity(<target>)` 反查谁调它，并把触发条件（onClick 函数 / View id / button text）抽出
> - **★间接跳转下钻（2026-07-16，AIPPT 实证漏边）**：grep 目标启动点（`startActivity(B)` /
>   `B.openXxx()` / `B.openWebPage()` 等）反查时，若调用点**不在**点击监听里、而在一个**普通函数/
>   扩展函数/ViewModel 方法**体内 → **不要停**，继续反查「谁调这个函数」，逐层上溯直到落到
>   `onClick`/`setOnClickListener`/`OnMenuItemClick` 等真实触发点，再抽 view id + label。
>   真实事故：`mineSettingCustomerService` 的 onClick 里写 `requireActivity().showService(false)`，
>   而 `showService`（SaleCenterViewModel.kt 扩展函数）内部才 `CustomerServiceWebActivity.openWebPage`。
>   只反查一层 → 反查到「showService 函数」就断链 → 这条 →CSWeb 边被漏建（同页 mineFeedback/
>   tvAfterSaleService 因直接调 openWebPage 就建对了，两两对照即此盲区）。**"点击→中转函数→
>   startActivity" 的两层间接是常见写法，必须下钻**；中转函数内有分支（如 showService 按
>   `contactUsUrl` 空否走 H5 或 拨号/弹窗）→ 每个分支的落点都要如实记（trigger 一个、落点多态）。
> - 对每个 fact-tree 里 `inbound = []` 或 `inbound[].trigger == "click"` 但 `via_component=null` 的 record，必须补全
> - 输出写到 record 顶层的新字段 `inbound_triggers[]`（不污染 toolkit 的 `navigation.inbound[]`）
> - **注释代码不是证据（2026-07-11）**：grep 命中行若处于注释中（行内 `//` 之后、`/* */` 块内、
>   `<!-- -->` 内），**禁止**作为 inbound_trigger / 导航边 / 前置条件的依据——引用 evidence_line 前
>   必须确认该行是活代码。真实事故（AIPPT WorksPage）：唯一入口 `fl_my_collect → WorksPage.openPage`
>   整段被 `//` 注释、layout 里控件也已删，仍被当活证据写进树 → 下游每轮真机白试导航 ~2min 后
>   BLOCKED，直到源码对质才翻案。同理：入口代码活着但引用的 view id 在 layout 里不存在，也要降级
>   （trigger_label 保留、加注 `layout_missing`），不得按可点击处理

**起点素材：`navigation.inbound[].nav_edge_seed`（toolkit 机械追到的候选边）**

toolkit 已把它机械追到的导航边写进 `record.navigation.inbound[]`，其中带 `nav_edge_seed: true`
的条目是**候选边**，字段：`from`（调用方 record id）+ `trigger_fn`（触发函数，如 `fn: onClick` /
`hosts fragment (FragmentTransaction.replace)`）+ `nav_edge_evidence_file` / `nav_edge_evidence_line`
（源码锚点）+ `nav_edge_extractor`（`regex` / `ast_index` / `bytecode*`）。

**这些是候选，不是成品** —— 它们给了「谁→谁、在哪行、哪个函数」，但缺 visual-verify 真正要的
`trigger_view_id` + `trigger_label`（真机上点的**文案**）。你的职责是把每条候选核实并解析成
完整 `inbound_triggers` 条目；同时补 toolkit 没追到的入口。

**遍历策略**：

```
FOR EACH record IN pages + fragments + dialogs:
  IF record.id == launcher_short:
    record.inbound_triggers = [{from_page: null, trigger: "boot", source: "launcher"}]
    continue

  candidates = [e for e in record.navigation.inbound if e.nav_edge_seed == true]

  # ── 先消费候选边（有锚点，定位快）──
  FOR EACH cand IN candidates:
    读 cand.nav_edge_evidence_file : cand.nav_edge_evidence_line 上下 30 行（AST/bytecode 来源
      注释安全可直接信；regex 来源已过 toolkit 注释校验，但你**仍须自查该行是活代码**）
    从 cand.trigger_fn 顺到真实触发控件：
      · fn: <onClick 名>          → 反查该函数体里的 view id（findViewById(R.id.X)/binding.X）
      · hosts fragment (Transaction.add/replace) → host 的 ViewPager/事务里该 fragment 的
        触发 tab/step（含 wizard_step 的 下一步/是/否 按钮）
      · menu <resId> / l2:localIntent → 按锚点定位
    从 layout xml / @string 抽 view 的真实 android:text/content-desc 当 trigger_label
    产出 inbound_trigger 条目（见下方 schema），source="llm_source_read"，
      并带 verified_from_seed: true（留痕：源自 toolkit 候选、经核实）
    ★ 候选核实为死码/注释/view 不存在 → **丢弃该候选**（不产条目），notes 记因由

  # ── 再补漏（候选没覆盖到的入口）──
  搜 Android 源码：grep -rn "startActivity.*${record.id}\|startActivityForResult.*${record.id}"
                 grep -rn "Intent.*${record.id}\.class\b"
  对每条**候选未覆盖**的命中：
    定位到所在 .kt / .java 文件 + 行号
    读上下 30 行：识别 onClick 函数 / view.setOnClickListener / lambda 触发点
    从同 file 反查 view id：findViewById(R.id.X) / databinding.X.setOnClickListener
    从同 module layout xml 找 R.id.X 的 view → 抽 android:text / content-desc
    LLM 推断 caller page (Activity/Fragment) 的 fact-tree id
  
  生成 inbound_trigger entry:
    {
      from_page:        <caller page id>,
      trigger_method:   <onClick 函数名>,
      trigger_view_id:  <R.id.X>,
      trigger_label:    <button text / content-desc / 推断>,
      evidence_file:    <相对路径>,
      evidence_line:    <行号>,
      source:           "llm_source_read"
    }

  Dialog / DialogFragment 特殊：
    搜 ${record.id}().show() / DialogFragment.show(...)
    同样反查到触发的 onClick / lifecycle hook
```

**约束**：

```
- trigger_label 必须从 layout xml / @string 资源真实抽出，不要 LLM 想象
- LLM 不确定时填 "trigger_label_unknown" + notes 说明，**不要瞎猜**
- 同一 record 可能有多个 inbound_triggers（多个屏都能跳到）——全列出，按调用频次 / 主流程优先排序
- launcher Activity 唯一 trigger 是 boot，特殊标 source: "launcher"
- `navigation.inbound[].nav_edge_seed` 是 toolkit 机械候选（带 from + trigger_fn + 锚点行），
  **必须逐条核实**再产出 inbound_trigger：注释/死码/view 不存在 → 丢弃；活代码 → 解析出
  trigger_view_id + trigger_label（真机文案），标 verified_from_seed: true。候选只是省你定位，
  不是免核实——直接原样抄会把 toolkit 的注释盲/无 label 缺陷带进最终真值
```

**输出例（AccountInfoActivity）**：

```jsonc
{
  "id": "AccountInfoActivity",
  ...
  "inbound_triggers": [
    {
      "from_page": "MineFragment",
      "trigger_method": "initView$1$1.onClick",
      "trigger_view_id": "rl_account_info",
      "trigger_label": "账号信息",
      "evidence_file": "app/src/main/java/cn/sanfate/pub/platform/page/MineFragment.kt",
      "evidence_line": 142,
      "source": "llm_source_read"
    }
  ]
}
```

下游 visual-verify Phase Alpha 拿到该字段后：
1. 把 inbound_triggers[0].from_page 当 host
2. am-start host → 在 host 屏 dump 里找含 "账号信息" 文本的 clickable → tap
3. 失败则用 trigger_view_id 找节点 tap
4. 仍失败 → 才回落 am-start AccountInfoActivity（cheat 路径）

### Phase 2.6: navigation_contract（v6.4 — 根因解，wizard / sub_tab / modal 精确导航）

**为什么需要**：下游 visual-verify 遍历器（旧版 walk_android_tree，现为 walk_exec.py 边遍历）的 Fragment 兜底逻辑是"找不到关键词就 fake-pass 截 host as-is"——结果 4 个 GuideXxxFragment 截到同一张 Step 1 图。根因是 **Fragment 的实际触发动作没结构化数据描述**。

本 phase 给每个 Fragment / Dialog 输出**精确 UI 导航合同**（`navigation_contract`），让 walk 脚本按合同精确点击 + 强验证，彻底消灭 fake-pass。

#### 合同结构（写到 record 顶层）

```jsonc
{
  "id": "GuideInitFragment",
  ...
  "navigation_contract": {
    "relationship_kind": "wizard_step",       // tab | sub_tab | wizard_step | lifecycle_modal | dialog_trigger | host_default
    "wizard_index": 0,                        // 仅 wizard_step 必填，从 0 开始
    "from_state": "GuideActivity_just_opened", // 前置态描述（人类可读，walk 用 reach_path 倒数第二节点判断匹配）
    "trigger_actions": [                      // 多入口数组（多数情况只 1 条）
      {
        "type": "auto_default" | "tap_text" | "tap_resource_id" | "back" | "swipe",
        "label": "下一步",                    // type=tap_text 时填
        "label_regex": null,                  // 运行时拼接文本用，如 "上传文档.*"
        "label_dynamic": false,               // true 表示文本来自运行时变量，walk 用 tap_first_clickable_button 兜底
        "resource_id": null,                  // type=tap_resource_id 时填
        "verify_after_tap": true              // 是否在 tap 后等 verify_signal
      }
    ],
    "verify_signal": {                        // 必填：到达本 Fragment 的标识
      "text_contains": "你常使用的PPT演示场景" // 单 primary（HMOS 一致铁律 §1.2，不需 fallback）
    },
    "exit_action_to_next": {                  // 仅 wizard_step：到下一 step 的动作
      "type": "tap_text", "label": "下一步",
      "leads_to": "GuideDifficulty1Fragment"
    },
    "contract_uncertain": false,              // LLM 推断未通过源码验证时标 true
    "generated_from": [                       // 锚点列表（追溯用）
      "spec/baseline/ui/page_0003_GuideActivity.md:38",
      "app/src/main/java/.../GuideActivity.kt:142"
    ]
  }
}
```

#### relationship_kind 6 类

| kind | 含义 | 例子 | trigger_action 模式 |
|---|---|---|---|
| `host_default` | host 启动后直接显示，无需 tap | HomeFragment 在 HomeActivity 默认 tab | `auto_default` |
| `tab` | 底部 / 顶部导航 tab | "我的" / "首页" 底部 tab | `tap_text` (tab label) |
| `sub_tab` | 容器内 ViewPager 子 tab | HomeDocFragment 是 HomeFragment 内的"导入文档"子 tab | `tap_text` (sub-tab label) |
| `wizard_step` | 顺序多步流程的某一步 | GuideInitFragment → Difficulty1 → Status → Details | 上一步的 `exit_action_to_next` |
| `lifecycle_modal` | 页面生命周期自动弹出 | LaunchAgreementDialog | `auto_default` |
| `dialog_trigger` | 特定业务按钮触发 | "联系客服" 按钮 → CustomerServiceDialog | `tap_text` |

#### 数据源 + LLM Prompt 模板

输入给 LLM 的上下文（每个 Fragment / Dialog 一次调用）：

```
context: {
  record_id: "GuideInitFragment",
  record_type: "Fragment",
  android_file: "app/src/main/java/.../GuideInitFragment.kt",  # 源码内容 ±30 行
  page_md_content: "..."  # spec/baseline/ui/page_*.md 匹配段
  host_record_id: "GuideActivity",   # parent_in_nav
  host_android_file: "...GuideActivity.kt",  # 源码 ±50 行
  host_layout_xml: "guide_activity.xml",  # 解析后的 button text
  sibling_fragment_ids: ["GuideDifficulty1Fragment", "GuideStatusFragment", ...]
}

task: 输出 navigation_contract，结构严格按 schema
```

#### 确定性源码验证（消除 LLM 错率）

LLM 输出后**必须**跑这些验证，不通过 → 标 `contract_uncertain: true`：

```python
case contract.relationship_kind:
  "wizard_step":
    # host 源码必须有 ViewPager.setCurrentItem 调用，或类似 step 切换逻辑
    assert grep("setCurrentItem|currentStep|step\s*\+\+", host_kt)
    
  "tab" | "sub_tab":
    # host layout xml 必须含 contract.trigger_action.label 文字
    assert label in extract_layout_strings(host_layout)
    
  "dialog_trigger":
    # host 源码必须有 `{record_id}.{...}.show(` 调用
    assert grep(f"{record_id}.*\\.show\\(", host_kt)
    
  "lifecycle_modal":
    # host 源码必须有 onCreate / onResume / onStart 里的 dialog.show()
    assert grep(f"override fun (onCreate|onResume|onStart)", host_kt)
    
  "host_default":
    # 无需验证
    pass
```

不通过的标 `contract_uncertain: true` + 输出到 `spec/visual-verify/contracts_uncertain.md` 供人工审。

#### 处理 4 个关键风险（建在 Phase 2.6 里）

| 风险 | 缓解 |
|---|---|
| **wizard 链失败传染**| Phase 5 自检：wizard_step 节点的 exit_action_to_next.leads_to 必须指向另一 wizard_step（同 host 内），形成有序闭环 |
| **LLM 推断错** | 上面的确定性源码验证 |
| **多入口同 Fragment** | trigger_actions[] 数组，walk 时按 reach_path 上文匹 from_state |
| **动态文本** | label_dynamic=true + label_regex 兜底 |

> **HMOS 端复用风险**：v6.4 起 SKILL.md §1.2（visual-verify）规定 contract 是双端唯一权威，HMOS 不一致 = 写 ALIGN findings，不在 contract 加 HMOS-side fallback。

### Phase 2.7: LLM 扩充 preconditions 业务前置态（v6.3 新增）

**为什么需要**：toolkit-fact-indexer 的 `enhance_with_preconditions` 已经用 regex 抽了基础模式（`UserData.isLogin()` / `interceptAuth==1` / `VipFunctionInterceptDialog` 等共 10 类）。但很多业务前置态藏在更复杂的语义里——toolkit 抓不到，spec/baseline/ui/page_*.md 已经写好。本 phase 让 LLM **校验和扩充**。

**输入**：
- fact-tree 每条 record 的现有 `preconditions[]`（toolkit 抽的）
- 对应 page_*.md（如 `spec/baseline/ui/page_0006_CreateOutLinePage.md`）
- 对应源码（用 `android_file` 锚点）

**遍历策略**：

```
FOR EACH record IN pages + fragments + dialogs:
  # 1. 找对应 page_*.md
  page_md = match_page_md(record.id, "spec/baseline/ui/page_*.md")
  if not page_md: continue

  # 2. 抽业务约束章节（"前置条件 / 拦截器 / 必填参数 / 数据依赖"）
  precondition_blocks = grep_sections(page_md,
    ["前置条件", "拦截器", "必填参数", "依赖", "数据约束", "用户状态"])

  # 3. LLM 把自然语言抽成结构化条目
  for block in precondition_blocks:
    new_pc = llm_extract_preconditions(block, source_anchor=record.android_file)
    # new_pc 形如 {kind: "param_required", evidence: "query 非空",
    #              source: "page_0006_CreateOutLinePage.md §参数依赖"}

    # 4. 合并到 record.preconditions[]（去重 by kind+evidence_fragment）
    record.preconditions = dedup_merge(record.preconditions or [], new_pc)
```

**Phase 2.7b: state_required 数据前置态推导（v6.8 新增，不依赖 page_md，全 record 必跑）**

> **为什么单列**：2.7 主循环 `if not page_md: continue` + 只抽入口拦截语义，会系统性漏掉
> **"入口不拦截、内容靠数据"** 的页面——典型如作品/收藏/历史列表页：列表空也能正常打开（空态占位），
> 源码无 `if (isEmpty()) return` 守卫可抓，但 (1) 空态截图对比价值低 (2) 下游"点条目进详情"的边
> 直接不可走（AIPPT 实测：PPTFilePage 依赖点击作品条目，账号无作品时该边永远走不通且会被误诊成
> nav_unreachable）。**数据前置是"测试可达性"属性，不是"入口拦截"属性——不要因为入口不拦截就跳过。**

对每条 record（不管有没有 page_md）按两个信号判：

```
信号 a（确定性，读树即可判，优先）:
  存在子页 child 满足: child.preconditions 含 param_required 且参数语义为"列表条目对象"
                     且 child.reach_path 途经本页的条目点击边
  → 本页补 state_required（evidence 写明 child 与边; unblocks=[child.id]）

信号 b（读源码，android_file 锚点）:
  布局含列表容器(RecyclerView/ListView/LazyColumn) 且 源码有空态分支
  （emptyView / list.isEmpty() 分支 / "暂无"占位文案）且 数据源来自 DB/接口（非静态写死）
  → 本页补 state_required（evidence 写空态分支出处）
```

产出条目**必须带 `data_hint`**（给下游 scenario-builder / visual-verify 预检器规划 fixture 的一句话数据需求）：

```jsonc
{"kind": "state_required",
 "evidence": "PPTFilePage(param_required: Intent 传入待预览作品) 经本页'我的创作'条目点击到达; 列表空则该边不可走",
 "data_hint": "账号内 ≥1 个已生成作品",
 "unblocks": ["PPTFilePage"],            // 仅信号 a 有; 预检器据此关联下游页面
 "source": "app_relationship_tree:state_required_rule_a"}   // rule_a / rule_b 标明推导来源
```

**★2.7b 收尾必须留痕（2026-07-10，机械闸依据）**：跑完后往树根写 marker——**找到 0 条也要写**：

```jsonc
"_phase_markers": {"state_required_rule": {"ran": true, "found": <N>, "at": "<ISO日期>"}}
```

出口闸（`dispatch.py::preconditions_gate`）凭"存在 `state_required_rule` source 的条目 **或** 此 marker"区分"跑了没发现"和"根本没跑"——缺痕迹直接 FAIL 不得交付。真实事故：本 phase 在一次 ART 崩溃抢救中被无声丢掉（手工补了 enrich patch 但没人对照 phase 清单核销），4 条数据前置态消失、下游 visual-verify 预检假绿放行，靠 trip_2 撞页才暴露。**崩溃抢救/断点续跑后必须重跑本 phase 或确认其痕迹仍在。**

**扩充的 kind 类别**（toolkit 抽不到的）：

| kind | 例子 | 通常出现在 |
|---|---|---|
| `param_required` | "需要 query 参数 + from 来源" / "intent extra 必传对象" | page_*.md §"传参"；源码 intent 读参 |
| `state_required` | "已上传文档" / "已选模板" / "作品列表非空" | page_*.md §"前置态" + **2.7b 树结构/源码信号（不依赖 page_md）** |
| `credits_required_amount` | "免费次数 ≥ 1" / "VIP 等级 ≥ 月会员" | page_*.md §"拦截器" |
| `nav_redirect_target` | "未登录 → 跳 LoginPage / 无余次 → 跳 MemberCenterPage" | page_*.md §"拦截器" |
| `feature_flag` | "interceptAuth=1 全局开关" / "服务端 userConfig/推送决定可见" | page_*.md §"全局配置"；服务端配置 |
| `permission_required` | "授予 MANAGE_EXTERNAL_STORAGE 后才可达" | 源码权限守卫（2026-07-10 收编） |
| `first_launch_onboarding` | "仅首启引导流程可达（MMKV 标记后不再出现）" | 源码首启守卫（2026-07-10 收编） |
| `business_state` | "productBean!=null 且 auditingStatus!=1 才弹" | dialog 变体节点可见性条件（2026-07-10 收编；**非 fixture 可造态，勿与 state_required 混用**） |
| `permission_not_granted` | "权限**未**授予时才弹提示 dialog" | dialog 变体节点（2026-07-10 收编） |

**★kind 白名单机械强制（2026-07-10）**：以上 kind + 基础层 `login_required`/`vip_required`/`login_conditional`/`intercept_dialog` 构成**封闭白名单**，由 `android-fact-tree/scripts/dispatch.py::preconditions_gate` 出口硬拦。真实事故：崩溃抢救的修复 agent 自造 `data_required`（还有 `server_config`/`intent_extra_required`）→ 2.7b rule_a 按 kind 字符串匹配链式失效 → state_required 全丢 → visual-verify 预检假绿。**语义已有近似 kind 的必须归并（intent 传参→param_required、服务端配置→feature_flag），确属新语义才扩表；扩表必须同时改本表和 gate 的 `PRECOND_KIND_WHITELIST`，只改一处 = 契约漂移。**

**输出例（CreateOutLinePage 扩充后）**：

```jsonc
"preconditions": [
  // toolkit-fact-indexer 抽的（基础）
  {"kind":"login_required","evidence":"UserData.isBinding() check",
   "evidence_file":"...CreateOutLinePage.kt","evidence_line":66,
   "source":"preconditions_enhancer"},
  // app-relationship-tree LLM 扩充的（业务）
  {"kind":"param_required","evidence":"query 非空",
   "source":"app_relationship_tree:page_0006_CreateOutLinePage.md"},
  {"kind":"credits_required_amount","evidence":"freeCount>=1 或 VIP",
   "source":"app_relationship_tree:page_0006_CreateOutLinePage.md §拦截器"},
  {"kind":"nav_redirect_target","evidence":"未登录→LoginPage / 无次数→MemberCenterPage",
   "source":"app_relationship_tree:page_0006_CreateOutLinePage.md §拦截器"}
]
```

**约束**：
- LLM 输出每条 precondition **必须**有 `evidence` 字段引述 spec 原文
- `source` 必须指明出处（页面 md / 源码行）
- 不要瞎猜——找不到证据就不写。toolkit 已有的不重复写
- preconditions 数组保持去重（kind+evidence_fragment 唯一）

### Phase 3 (可选): 启发式补 reach_paths 孤儿

> **触发条件**：用户显式要求"补完 reach_paths" 或 fact-tree 中 `reach_paths == []` 的 record > 0
>
> **承认现实**：toolkit-fact-indexer 已经从 toolkit 真实数据榨到 96% 覆盖（55/57 in AIPPT）。剩 4% 是 toolkit 的算法盲区——ViewPager 反射实例化的 Fragment / 自定义 widget 等。要拉到 100% 必须用命名启发式（不是 toolkit 事实，标 source 为 heuristic）。

启发式规则（来自旧 compute_reach_paths.py 的 Tier 2）：

```
FragmentXxx        → 同 package 找 XxxActivity 当 host
XxxFragment        → 找 XxxActivity 当 host
GuideDifficultyXFragment → host = GuideActivity（特殊模式）
RecommendFragment / RecommendListFragment → host = HomeActivity（tab 常见模式）
XxxFragment 嵌在 XxxParentFragment → 推 parent 当 host
```

匹配到 host 后：
```jsonc
record.reach_paths.append({
  "display": f"{host.reach_paths[0].display} > heuristic_host > {record.id}",
  "depth": host_depth + 1,
  "source": "heuristic_host_inference",   // 明确标 heuristic 不是 toolkit 事实
  "ref": null
})
```

### Phase 4: LLM 推 dependency_graph.layers

> **触发条件**：默认必跑（除非 fact-tree 已有 `dependency_graph` 字段表示之前跑过）。
>
> **背景**：toolkit-fact-indexer 给的 `features[]` 是 token 聚类（如 `generated.home.renew` / `generated.mine.about`），**没有架构语义**。下游 visual-verify 排序需要"先 Foundation 后 Shell"的层级提示，要 LLM 看每个 feature 的语义把 17 个聚类归到 6 个架构层。

#### 输入

```python
features = fact_tree["features"]          # toolkit 17 个聚类（id / label / screens / top_tokens）
records  = fact_tree["pages"] + fact_tree["fragments"] + fact_tree["dialogs"]
launcher = fact_tree["app"]["launcher_short"]    # 用于识别 Foundation
# 每个 feature 关联的 record 现在已经有 purpose（Phase 2 补好的）
```

#### 6 个架构层定义

| layer | 含义 | 典型 feature |
|---|---|---|
| 0 Foundation | App 启动 / 协议 / 引导 / 通用基础 | Splash / LaunchAgreement / Guide |
| 1 Auth | 登录 / 账号 / 三方认证 | Login / AccountInfo / AliAuth |
| 2 Monetize | 会员 / 支付 / 续费 / 退款 | MemberCenter / Pay / Renew / Refund |
| 3 Core AI | 主业务功能 | PPT 创作 / 大纲 / 模板 / 作品 |
| 4 Extended | 扩展功能 | 推荐 / 文件管理 / 视频播放 / WebView |
| 5 Shell | 聚合页 / 主导航 | Home / Mine / 主页 Tab 容器 |

#### LLM 任务

```
对每个 feature，根据：
  - representative_screens（toolkit 给的代表 screen 列表）
  - top_tokens（toolkit 聚类用的 token，如 ["login","auth","sms"]）
  - 关联 screen 的 purpose（Phase 2 已补的中文描述）
  - 关联 screen 的 android_file 包路径（如 .platform.page / .baseui.activity 可看出基础库）
  - 是否含 launcher

推断这个 feature 归属哪一层（0-5）。

特殊规则：
- 含 launcher_short 的 feature → 0 Foundation
- top_tokens 含 "login"/"auth"/"phone"/"account" → 1 Auth
- top_tokens 含 "pay"/"member"/"vip"/"refund"/"renew" → 2 Monetize
- screen 含 "Home"/"Mine"/"Main" 且其它 layer 都不匹配 → 5 Shell
- 其它业务功能 → 3 Core AI 或 4 Extended（看是否是主流程）
```

#### 输出

往 fact-tree 顶层加 `dependency_graph` 字段：

```jsonc
"dependency_graph": {
  "layers": [
    { "layer": 0, "name": "Foundation", "features": ["generated.splash.app", "generated.launch.agreement", "generated.guide.app", "generated.again.confirm"] },
    { "layer": 1, "name": "Auth",       "features": ["generated.app.src"] },   // app.src 含 LoginActivity / AccountInfoActivity
    { "layer": 2, "name": "Monetize",   "features": ["generated.member.center", "generated.home.renew"] },
    { "layer": 3, "name": "Core AI",    "features": ["generated.choice.ppttemplate", "generated.fill.pptquery", "generated.ppttemplate.preview", "generated.works.app"] },
    { "layer": 4, "name": "Extended",   "features": ["generated.customer.app", "generated.file.upload", "generated.landscape", "generated.video.play", "generated.web.app"] },
    { "layer": 5, "name": "Shell",      "features": ["generated.mine.about"] }
  ]
}
```

#### 约束

- 每个 `fact.features[*].id` **必须**出现在某层的 `features[]` 里（覆盖完整，不允许遗漏）
- 同一 feature 只能在一层（互斥）
- layer 编号 0-5 严格递增，name 字段与上面定义表一致
- 不可改 `fact.features` 数组本身（toolkit 事实）

#### 增量重跑

如果 fact-tree 已有 `dependency_graph` 且 feature 集没变（同 fact.features 列表），直接复用，不重新 LLM 推。

---

### Phase 5: 自检 + 写回

退出前必须确认：

| 项 | 验证 | 严重度 |
|---|---|---|
| JSON 合法 | `jq empty < spec/toolkit-fact-tree.json` | HARD |
| schema_version=1 不变 | 没被改坏 | HARD |
| 所有 page/fragment/dialog `purpose` 非 null | 自检 | HARD |
| 所有 component `purpose` 非 null | 自检 | HARD |
| navigation / source_anchor / parent_id / flow_graph / features / stats 与 LLM 跑前**逻辑等价**（允许 Phase 1.5 删假 record / 改 fq_class）| diff with allowed-mutations whitelist | HARD |
| **Phase 1.5 删除节点的 inbound/outbound 已 merge 到等价 real record**（v6.3）| 扫所有 navigation.inbound/outbound，from/to 必须存在于当前 records | HARD |
| **Phase 1.5 新增节点字段齐全**（v6.3）| id / type / fq_class / android_file / source / purpose 不能 null（除了 source 字段标 added 的可接受首版 purpose=null）| HARD |
| reach_paths 字段保留（toolkit 96% 的不能丢） | 长度 ≥ Phase 1 时长度 | HARD |
| **reach_path 字段非空**（v6.3 Phase 2.3）| 每条 record 都有 reach_path（launcher 时为 `[id]`，其它至少 3 元素：root + token + self） | HARD |
| **reach_path 中所有 page-id token 都在 fact-tree 里**（v6.3）| BFS 中间步骤不能引用不存在的 record | HARD |
| **dependency_graph.layers 覆盖所有 features** | 每个 `fact.features[*].id` 必须在某 layer.features 里 | HARD |
| **dependency_graph.layers feature 互斥** | 同一 feature_id 不能出现在两层 | HARD |
| **inbound_triggers 字段存在**（v6.2 新增）| 每条 record 都有 inbound_triggers（≥1 条；launcher 可只有 boot） | HARD |
| **inbound_triggers.from_page 可达**（v6.2 新增）| 引用的 page id 必须是 fact-tree 中存在的 record，或是 null（仅 launcher boot） | HARD |
| **preconditions 扩充（v6.3）**| toolkit 已抽的基础 preconditions 必须保留；本 skill 扩充的条目 source 字段必须含 `app_relationship_tree:` 前缀 | HARD |
| **navigation_contract 字段存在**（v6.4）| 每条 Fragment / Dialog 都有 navigation_contract（host_default 类型可只填 relationship_kind + verify_signal） | HARD |
| **navigation_contract.relationship_kind 合法**（v6.4）| 必须是 6 类枚举之一（host_default / tab / sub_tab / wizard_step / lifecycle_modal / dialog_trigger）| HARD |
| **wizard chain 闭环**（v6.4）| 所有 relationship_kind=wizard_step 节点，按 wizard_index 排序应形成 0→1→2→...，相邻两节点 exit_action_to_next.leads_to 必须指向下一 index | HARD |
| **contract_uncertain 标记输出**（v6.4）| LLM 推断未通过确定性源码验证的，必须标 contract_uncertain=true + 写入 `spec/visual-verify/contracts_uncertain.md` | HARD |
| **新增 / 删除节点的 stats 字段对齐**（v6.3）| stats.total_pages/total_fragments/total_dialogs 必须 = 实际数组长度 | HARD |
| **inbound_triggers.evidence_file 真实存在**（v6.2 新增）| 抽样检查 5 条，evidence_file 路径必须在 android_root 下存在 | HARD |
| **Phase 1.6 新增节点 source 前缀正确**（v6.5）| 类扫描新增的 dialog record `source` 必须 == `"app_relationship_tree_added_class_scan"`，便于追溯/统计 | HARD |
| **Phase 1.6 新增节点 construction_mode 合法**（v6.5）| 必须是 `"layout_xml"` 或 `"code_only"` 二选一 | HARD |

任一 ❌ → skill 失败，向用户报错。写回 `spec/toolkit-fact-tree.json` 覆盖。

---

## 3. 输入 / 输出

| 项 | 路径 | 说明 |
|---|---|---|
| **唯一必选输入** | `spec/toolkit-fact-tree.json` | toolkit-fact-indexer 产物，若不存在则自动调起 |
| 中间锚点（Phase 2 LLM 增量读用） | `spec/.cache/fact-tree/source-index.json` | toolkit-fact-indexer 已产 |
| **必选**（v6.3）| `spec/baseline/ui/page_*.md` | a2h-spec 产物，Phase 1.5 校验漏识节点 / Phase 2.7 扩充 preconditions 必读 |
| **必选**（v6.2）| Android 源码（`{android_root}/`） | LLM 看源码补 purpose **+ inbound_triggers + Phase 1.5 节点校准**；要 grep startActivity / Intent / class 定义，必须有源码 |
| 可选 | `spec/baseline/feature-index.md` | 校准 dependency_graph.layers 时优先用 |
| **唯一输出** | `spec/toolkit-fact-tree.json` | **原地覆盖**，不产新文件 |

---

## 3.5 如何完整跑这个 skill（v6.4 编排）

本 skill 5 个 phase 里 4 个是 LLM 任务、3 个是脚本任务。**正确执行流程是**：

### 推荐路径 A：一键 orchestrator + 派 sub-agent 补 LLM phase

```bash
# 第 1 步：跑所有确定性 phase（脚本）
bash $SKILLS_ROOT/app-relationship-tree/scripts/run_all_phases.sh \
    --android-root <ANDROID_ROOT> \
    --tree spec/toolkit-fact-tree.json

# orchestrator 跑完会输出 LLM phase 待办，如：
#   ❌ fact-tree 未完成 2 个 LLM phase:
#   📌 Phase 2 (purpose): 30 record purpose=null
#   📌 Phase 2.6 (contract.label): 42 contract_uncertain=true

# 第 2 步：对话里跟 模型说 → 模型派 sub-agent 跑 LLM phase
#   "跑 app-relationship-tree Phase 2.6 LLM 补 contract.label"
#   "跑 app-relationship-tree Phase 2 LLM 补 purpose"
#   或一次性：
#   "跑 app-relationship-tree 全 LLM phase"
```

### 推荐路径 B：让 模型当 orchestrator（最常用）

直接说：
> "跑 app-relationship-tree 完整流程，目标 fact-tree 是 X"

模型会：
1. 自动跑 run_all_phases.sh（脚本部分）
2. 看 preflight 报告，识别哪些 LLM phase 未完成
3. 按需派 sub-agent 跑 LLM phase（一次跑完所有 / 单 phase 跑）
4. 跑完后再跑 preflight 确认 ✅

### 不推荐做法

❌ 只跑 calibrate_nodes.py / compute_reach_paths.py / compute_navigation_contract.py 单脚本 — 会跳过所有 LLM phase
❌ 跳过 preflight 直接进 visual-verify — visual-verify 遍历器会卡住报错

### 检查当前状态

```bash
bash $SKILLS_ROOT/app-relationship-tree/scripts/preflight_check.sh \
    spec/toolkit-fact-tree.json
# exit 0 = 全完成，可下游消费
# exit 1 = 待 LLM phase，按提示派 sub-agent
```

下游 arkts-visual-verify Phase Alpha 启动时**自动**调这个 preflight，未完成会拒绝跑。

---

## 4. 与上下游协议

### 上游：toolkit-fact-indexer

- 必须先跑 toolkit-fact-indexer（产出 fact-tree.json + source-index.json）
- fact-tree 中所有 `purpose=null` 是预期的——本 skill 来补
- fact-tree 中 reach_paths 已有 96% 真实数据——本 skill 不动那 96%，只**新增** heuristic 条目给剩 4% 兜底

### 下游：直接读 fact-tree.json（统一入口）

- **a2h-spec** Phase 0.5：直接读 fact-tree.pages[].navigation 等结构事实 + 用 purpose 写 spec 描述
- **visual-verify** / **a2h-fixer**：直接读 fact-tree.pages[].reach_paths 当测试队列 + 检索地图
- 不再有 `spec/app-relationship-tree.json` 这个文件——v6 删除

---

## 5. 触发场景

```
用户: 补一下 fact-tree 的 description
用户: 补 purpose
用户: 完整化关系树
用户: 给 toolkit 产物加业务语义
用户: app-relationship-tree
用户: 我跑完 fact-indexer 了，把 description 都填上
用户: 给 fact-tree 产 dependency_graph
用户: 让 fact-tree 能被 visual-verify 按架构层级排序
用户: 补导航触发链 / 补 inbound_triggers / 让 visual-verify 知道按钮怎么跳
```

---

## 6. 历史变更

| 版本 | 时间 | 主要变化 |
|---|---|---|
| **v6.5**（current）| 2026-06 | **Phase 1.6 新增**：源码 popup 类正向扫描——补 Phase 1.5 反向 page_md 扫描的鸡生蛋盲区。脚本 `scan_popup_classes.py`，~1 秒跑完，rg-based + 继承链传递闭包 + 命名兜底。在 jq50w/project1 实测：fact-tree dialogs 180→245（+65），覆盖 65 个已知漏识 popup 中的 59 个（90.8%，剩 6 个为 Base 抽象基类，正确排除）。新增字段 `construction_mode` 区分 layout_xml/code_only。自检 +2 项 |
| v6.4 | 2026-05 | **Phase 2.6 新增**：navigation_contract — 给每个 Fragment / Dialog 输出精确 UI 导航合同（relationship_kind / trigger_actions / verify_signal / wizard_index）。下游 visual-verify v3.9 按合同精确点击 + 强 verify_signal，消灭 fake-pass。配合 4 项风险缓解（wizard 链闭环 / 源码确定性验证 / 多入口数组 / 动态文本 regex）。自检 +4 项 |
| v6.3 | 2026-05 | **职责扩展**：从"补 purpose"升级为"toolkit-fact-tree 多源补全器"——可补字段 / 校正字段 / 新增节点 / 删除节点。新增 Phase 1.5（节点校准：剔除假 Activity / 校正 fq_class / 补漏识 record）+ Phase 2.7（LLM 扩充 preconditions 业务前置态，配合 toolkit enhancer 的基础抽取）。page_*.md 从可选变必选。自检 +5 项 |
| v6.2 | 2026-05 | Phase 2.5 新增：**LLM 读源码补 `inbound_triggers` 导航触发链** — 每条 record 列出从哪些屏点哪些按钮可到达自己，含 view_id / button_label / source line。下游 visual-verify Phase Alpha 据此做"点击优先、指令兜底"导航。Android 源码从可选变必选。自检 +3 项 |
| v6.1 | 2026-05 | Phase 4 新增：LLM 推 `dependency_graph.layers`（feature → 架构层级映射），下游 visual-verify 排序得以按 Foundation → Shell 顺序工作。自检加 2 项（覆盖 + 互斥） |
| v6.0 | 2026-05 | **彻底简化**：仅做 fact-tree 语义补充；删除 spec/app-relationship-tree.json 产物；删除 Phase 4D 字段映射 / 独立 schema / Phase 5 Fragment / Phase 6.5 reach_path 脚本；下游直接读 fact-tree.json |
| ~~v5~~ | 2026-05 短暂 | Phase 4.5.A/B + 严格自检 + 仍产 app-relationship-tree.json |
| ~~v4~~ | 2026-04 | reach_path 单独脚本算 |
| ~~v3 及更早~~ | — | 复杂的多 phase 流程 |

---

## 7. 局限性

| 局限 | 说明 |
|------|------|
| 依赖 toolkit-fact-indexer 先跑过 | 必须有 spec/toolkit-fact-tree.json |
| 不读 ArkTS 源码 | tree 是预期状态参照系，不描述 HMOS 现状（旧 SKILL §0 设计原则保留） |
| heuristic reach_paths 不是 toolkit 事实 | 标 `source: "heuristic_host_inference"` 让下游自行判断 |
| 没有"多源融合扩 sub_components 列表" | v6 简化，如要从 graph_builder / android-source 扩列表，请走 toolkit 端补充（重跑 toolkit + fact-indexer） |
