> **iOS .33 执行分支**：先读 [Xcode 原生源流程](native-xcode-source.md)，源端派发同时附 [native-source-batch-prompt](native-source-batch-prompt.md)。本文件的业务/账目/预算语义保留；旧 adb/Activity/uiautomator/pm clear 示例只属 Android 历史源分支。iOS 用本工程独占的 XCUITest session，原目标 HDC 与全部门禁不变。

> **iOS 源输入**：读取 Swift/Objective-C、SwiftUI/UIKit、Xcode 工程及原生资源；实际源构建与设备观测依赖可用的源平台环境。鸿蒙侧构建和验收保持原流程。源侧操作详见 `a2h-spec/references/native-input.md`。

# Sub-agent Batch Prompt

> 图遍历 + 真实点击的 sub-agent prompt 模板。主会话 Phase 4 派发 batch 时按本文件渲染 prompt。

---

## Prompt 模板（主会话渲染填入）

```text
[历史源平台示例：不适用于 iOS，不可执行。iOS 源设备/构建按本文件适配及 native-input 协议；目标 hdc/hvigor 检查仍须实际执行。]
你是 arkts-visual-verify sub-agent。

## 你的任务
跑一个 batch（8 个 page），对每个 page:
  1. 真实点击导航到该 page（不用 am-start 直跳）
  2. 截图 + 多模态对比 iOS vs HMOS
  3. 测试该 page 的每条出边（edges_to_test）在 HMOS 是否可点（iOS可行性查录制证据，见 B.5.a）
  4. 测试该 page 的 back 按钮行为
  5. 写差异 markdown + manifest.json

## 角色模式（双派并行，2026-07-20；见 phase4-dispatch.md §Step 4.A.2）

role: {role}   # "capture" | "judge" | "full"（缺省 full = 上述任务全做，旧串行兼容）
# ★若上行显示的是未替换的花括号占位（旧串行路径没注入 role）→ 按 full 处理

**role=capture（占设备，判读制铁律：只记「发生了什么」，不写「对不对」）**：
- 做：Phase A 准备、Phase B 的导航/截图/dump、行为对账的**实点与观察记录**
  （逐元素 tap → 记 outcome/landed/toasts[]/evidence，**不对 oracle、不下判定**）、
  失败出口证据包（exit 20-27 的包原样落盘）、Phase C 仅落 capture_manifest
- 不做：多模态对比、oracle 对账判定、render_finding_skeleton/写任何 spec/fix md、聚类
- 产物：`batches/{batch_id}/capture_manifest.json`：
  `{pages_status:{...同 B.7 词表}, per_page:{<page_id>:{screenshot, dump,
    behavior_observations:[{trigger_text, rid, center, outcome, landed, toasts, evidence}],
    nav_evidence_package?}}, started_at, finished_at}`
- 观测异常（截图与 outcome 矛盾/动态文案轮换等现场才知道的事）写进 per_page 的
  `observation_notes[]`——判定 agent 只看文件，看不到你的现场

**role=judge（零设备，禁一切 adb/hdc 命令）**：
- 输入：capture_manifest + 截图/dump 文件 + 树（oracle 三源）+ iOS 基线
- 做：多模态对比、行为对账**判定**（behavior_observations × 三源录制真值）、写单
  （骨架脚本+灵魂照旧）、类内 systemic 聚类、落 `batches/{batch_id}/manifest.json`（原 schema）
- 不做：任何设备命令；某页观察缺失 → manifest 记 `judge_blocked(missing_capture)`，**禁猜禁补采**
  （补采归主会话 capture 补漏队列）

## 输入（主会话注入）

nav_mode: {nav_mode}          # "xml" | "compose"，由主会话从 tree.source.toolkit 判定后注入（见下方 §导航方式）

batch_json: {batch_id, starting_page, scenario_chain, pages: [...]}
具体结构看 spec/visual-verify/batches.json (本 batch 对应那段)

iOS .48 目标代码定位：读取本 batch 行的 `file_resolved`；寄生页读取 `parent_file_resolved` 与 `parent_used`。`file_candidates` 只表示歧义候选，须结合实际代码核实；没有定位则保留未定位。`android_file` 保持原源字段，不当作 HMOS 路径。上述字段仅帮助定位代码，不能作为导航、到达或 PASS 证据；判定实现缺失仍按原 `resolve_hmos_impl.py` 核验。

device_config:
  ios_serial: {ios_serial}
  hmos_target:    {hmos_target}
  ios_pkg:    {ios_pkg}
  hmos_bundle:    {hmos_bundle}
  hmos_ability:   {hmos_ability}

output_paths:
  manifest:  spec/visual-verify/batches/{batch_id}/manifest.json
  findings:  spec/fix/round-{N}/ui/
  screenshots:
    # {trip_id} 取本 batch 所属 trip 的 trip_id（trip_1_logged_out 或 trip_2_logged_in_vip）
    ios: spec/visual-verify/screenshots/ios/{trip_id}/{page_id}.png   # iOS 永不变，baseline 已存在即跨轮复用；缺失才截
    hmos:    spec/visual-verify/screenshots/harmony/round-{N}/{trip_id}/{page_id}.jpeg
    sbs:     spec/visual-verify/screenshots/sbs/round-{N}/{trip_id}/{page_id}.jpeg

prior_findings:
  # 主会话拿前序 batch 已 CRASH_NAV_FAILED 的 edge 注入
  # sub-agent 见到本 batch 中某个 page 在 blocked_pages 列表里时 → 直接产 BLOCKED_*.md placeholder
  blocked_pages: [{page_id, blocked_by_md_path}, ...]
  retry_edges: [{from_page, to_page, prior_failed_round}, ...]   # 上一轮失败本轮重测

# 仅"B 审核员重派"路径才有此字段（首次派发时为空）
b_gaps: [
  {page, contract_source, delivery_evidence_missing, action}
]
retry_reason: "B 审核发现以下契约-交付漏对齐项，必须补齐"

# 若 b_gaps 非空：本次 sub-agent 任务**收窄为仅补 gaps**——按 gaps[*].action 逐条补漏，
# 不重跑已通过的 page，不增加新维度；补完更新 manifest 同 page 的相应字段即可退出。

## 导航方式（按 nav_mode 分，**进 Phase A 前先认这个**）

本文件下面所有"导航/到达某页"的步骤（`walk_to.py` 到 starting_page、Phase B.2 `walk_to(page)` 校验、B.5 `click_and_verify_edge`、am-start 兜底、严格 text 匹配）**默认是 `nav_mode == "xml"` 的走法**。

**IF nav_mode == "xml"（传统 XML/Activity 应用）**：照本文件原样执行，不变。

**IF nav_mode == "compose"（Jetpack Compose 应用，tree.source.toolkit=="swiftui-fact-tree"）**：
确定性 `walk_to`/`click_and_verify_edge`/`am-start` 对 Compose **不可靠**（单 Activity → Activity 名判页失效 + am-start 拉不起路由；底部 tab 无文字 → 文字匹配 trigger_not_found；同屏重复文字 → 点错）。因此 **Compose 模式下你（sub-agent，本身是带视觉的多模态 agent）自己导航**，用 fact-tree 的 `reach_path` + trigger `label` 当**语义提示**，按下列规则现场判断点哪：

```
Compose 导航规则（替代 walk_to / am-start / 严格 text 匹配）：
1. 判页：不看 activity 名（恒为单一 .MainActivity）。改用屏幕内容判断——
   dump 文字 / 截图,匹配该页 fact-tree 的 page_signature.positive 或语义。
2. 点元素：
   a. 有唯一可见文字的（按钮/设置行/"查看全部"）→ dump 找该文字节点,点其 bounds 中心。
      注意 Compose 节点常 clickable=false,**别按 clickable 过滤**,按文字 bounds 直接点。
   b. 无文字图标(底部 tab / 纯图标按钮)→ 按位置点:底部导航栏在屏幕最底,
      n 个 tab 等分屏宽,reach_path 里 tab 的语义序(或 fact-tree role/order)决定点第几格中心。
   c. 同屏重复文字(如多个"查看全部")→ 读截图/ dump 上下文,
      按它所属 section 标题(成就墙/数据统计…)选对应那个,点它附近(同行/紧邻)的那个。
3. 不走 am-start 直跳内部页(Compose 路由不是 Activity,必失败)。
4. 每跳后 sleep 2-3s(recomposition + 转场),再 dump/截图确认到没到目标页。
5. reach_path 是"语义意图链"不是确定性选择器——照它的顺序一跳跳走,每跳用上面 1-2 现场落点。
```

**Compose 模式下不调** `walk_to.py` / `click_and_verify_edge.py`（它们对 Compose 会 trigger_not_found/am_start_failed）；改由你按上面规则自走。其余流程（截图、多模态对比、写 markdown、manifest）**完全不变**。

### 双端真值语义（两 nav_mode 都适用，Compose 尤其重要）

★单侧化注（2026-07-12）：表中"iOS 基准"一列指 **Phase 2 录制产物**（baseline 截图在不在），
不是实时驱动iOS——本表语义本就是录制真值对账，原样有效。HMOS 到不了时按"iOS录制侧到没到过"
区分含义,**不要笼统当导航失败**：

| iOS 基准 | HMOS 被测 | 含义 | 产出 |
|---|---|---|---|
| 该页有 baseline 截图(到得了) | 你在 HMOS **到不了/找不到入口** | 鸿蒙漏了/挪了该入口 | 写 finding `CRASH_P<page>_page_missing_hmos`(P0,kind=CRASH)——**不是导航失败,是迁移缺陷** |
| iOS 也没 baseline(Phase 2 就到不了) | — | 树/scenario 错或本就不可达 | 按既有 BLOCKED/scenario_required 处理,**不赖 HMOS** |

> 即:**iOS基准能到、你在鸿蒙到不了 = 一条 P0 finding,不是"截不到图跳过"**。这正是双端对比要抓的"鸿蒙实现不完备"。

---

## 执行流程

### Phase A: 准备

**Step A.-1（HARD-GATE，v3.10 新增；2026-07-12 per-page 化）** — 进 HMOS 操作前必跑 iOS baseline gate：

```text
python3 $SKILLS_ROOT/arkts-visual-verify/scripts/check_ios_screenshot.py spec/toolkit-fact-tree.json
# Exit 0 + stdout "PASS"           = 基线全量到位，继续
# Exit 0 + stdout "PASS_WITH_DEBT" = 覆盖率在漂移带（fact-tree 演进快于基线的常态）：**继续跑**，
#     但读 spec/visual-verify/_baseline_debt.json——本 batch 页若在欠账清单里（missing_pages /
#     tech_blocked_pages），该页不做多模态对比，按 2.1-a 记 SKIPPED(no_ios_baseline)（显式
#     占位，禁静默跳过）；其余有基线的页照常全流程
# Exit 2 = NEED:ios-baseline:xxx（覆盖率低于地板 = Phase 2 整体没跑级事故）→
#     **立即停止本 batch**，写 fatal_error 到 manifest 后退出
```

理由：门防的是"静默跳过遍历"，不是"树比基线新"。多模态对比依赖基线，但基线是跨轮录制资产而
fact-tree 持续演进，两者周期性失同步是常态——per-page 放行 + 显式欠账保住对比基准，地板挡住
"Phase 2 压根没跑"的真事故。trip_2 欠账偏高仍是 login scenario 退化信号（gate stderr 会提示），
sub-agent 不私自修 scenario，交主会话。

0. **HMOS 前置自检**（★单侧化 2026-07-12：Phase 4 常规流程**不驱动iOS设备**——iOS侧
   动画/adb 自检整段删除；iOS真值全部来自 Phase 2 录制产物。唯一例外见 B.4.5 步骤 6 对照实验）:
   - uitest 探针：`hdc -t {hmos_target} shell uitest dumpLayout -p /data/local/tmp/_probe.json` 一次成功
   - （dialog_id_catalog.json 是iOS resource-id 目录，HMOS 弹窗排水不用它——见 B.-1）

1. reset_app（★2026-07-12 修正——旧"双端 pm clear + bm clean -d"是双侧时代残留，且是真 bug：
   **bm clean -d 会抹掉主会话在 trip 边界建好的登录态/门链态**（Phase 2 侧同型教训：trip_2 禁
   pm clear）。sub-agent 的 reset 只许 kill 进程，**清数据归主会话 trip 边界管**）:
   hdc -t {hmos_target} shell aa force-stop {hmos_bundle}
   sleep 2
   # iOS设备不碰（单侧化）；trip 态若发现不对 → 按下方步骤 2 写 SKIPPED 交主会话，别自己清数据重建

2. **不要**自己跑 scenario_chain！**trip 级 scenario（login/门链）全禁**——那是全局共享态，
   由主代理在 trip 起点统一调度（见 `phase4-dispatch.md` 主循环 `reset_app_and_run_scenarios`）。
   本 sub-agent 假设进入时 app 已在 `batch.starting_page` 应到达的态（如 trip_2 已登录）。
   若 walk_to 发现**登录态**不对 → 写 SKIPPED 占位让主代理重派或人工介入，不要私自跑 scenario。
   ★唯一例外（2026-07-10 ③）：**数据态** check/create 配方可就地重放（见 B.1 自愈梯）——
   局部态、check 可验证、限额 1 次/state/batch、必入 manifest。仅此一类，别扩大解释。

3. walk_to starting_page（**仅 nav_mode=="xml"**；nav_mode=="compose" 时跳过本步,改按上方 §导航方式 的 Compose 规则自己走到 starting_page）:
   python3 $SKILLS_ROOT/arkts-visual-verify/scripts/walk_to.py \
       --device harmonyos --target {hmos_target} \
       --page-id {batch_json.starting_page} \
       --fact-tree spec/toolkit-fact-tree.json \
       --bundle {hmos_bundle} --ability {hmos_ability}
   若 walk_to 失败：
     batch 整体 status=batch_blocked，写 SKIPPED 占位。

### Phase B: 主循环（每页）

**写单铁律（骨架机械化，2026-07-12——写单占墙钟 ~45% 的治理）**：所有问题单（ALIGN/CRASH/
URL/IMPL_MISSING/SYSTEMIC/SKIPPED_*）一律先调骨架生成器，**禁止手打 frontmatter/§0/§6/§7**：
```text
python3 $SKILLS_ROOT/arkts-visual-verify/scripts/render_finding_skeleton.py \
    --project-root . --round {N} --layer {ui|feat} --id <按 fix-file-schema §二派生> \
    --title "<按 §二 title 公式>" --kind <kind> --severity <P0|P1|P2> \
    --category-pattern <diff_kind> --page <page_id> --trip {trip_id} \
    --suggested-files <f1,f2|unknown> --similarity <x> --multimodal-severity <high|medium|low> \
    [--anchor "<源码锚点/账本行>"] [--feature-path "<feat单>"] [--evidence <额外证据,逗号分隔>] \
    [--extra-json '{"blocks_subtree":[...],"reverify":{...},"v4_edge":{...},"subsumes_ui":[...]}']
```
脚本包办：命名/同轮冲突-2/§0 必读块（视觉类自动）/§1 来源行+ios_source_refs 注入/
§2 spec_oracle 注入（feat）/§6 空块/§7 reach_path 注入/**carry-forward**（上轮同 id 的
disposition 三元组+§6 历史自动继承——你不用再手工翻上轮文件）。你只做两件事：
①把判定结论填进 CLI 参数 ②Edit 生成文件，把每个 `<<LLM:...>>` 占位替换成判定内容
（§2 期望/§3 实际/§4 源码缺口/§5 修复建议——单子的灵魂仍是你写的，壳子归脚本）。
写完自检：文件里不残留任何 `<<LLM:` 字样（残留=半成品，审计判违规）。

**行为对账铁律**（★单侧化重写 2026-07-12；原"双端同一动作"废止——Phase 4 不驱动iOS）：
每个 page 截图后，对其上每个可见交互元素（button / link / checkbox / toggle / input / list item /
系统返回键 / NavHeader < 按钮）做 **HMOS 单侧实测 × 录制真值对账**：HMOS 上实点一次观察落地态，
预期从**三源录制真值**取（按优先级，命中即用，manifest 记 oracle_source）：
  1. `functional_checks[].expected_ios`（Phase 2.5 grounding 实测真值）——该元素若已被
     B.4.5 覆盖，**不重复实点**，直接以 B.4.5 结果为准；
  2. `pages[].blackbox_behavior.{trip}[]`（Phase 2 黑盒行为账本：trigger_text/rid → outcome ∈
     noop/page_change/overlay_or_state/escaped_app/**toast_only**——本页清单外元素的主真值源）；
     ★ `toast_only` 附 `toasts[]` 原文：页面没下沉但弹了 toast（toast 不进 a11y 树，dump 抓不到，
       靠 logcat 统一 tag 抓）。**别把它当 noop 对待**——noop 是「点了没反应」，toast_only 是
       「该弹这句话」，鸿蒙侧要拿 `toasts[]` 当预期去对。
  3. iOS 源码声明（该 page 的 §1 ios_source_refs，grep 下列关键字——第三源，仅前两源
     无记录时用，据此出的单标 confidence=declared_only）。
**三源皆无记录的元素 → `untested_skipped(reason=no_recorded_oracle)`，不实测不猜**（无判据的
实测结果不可解释；例外：任何操作导致 app crash 照写 CRASH 单——crash 无需 oracle）。
任何差异（HMOS noop vs 账本 page_change / 落错页 / 默认值不符 / toast 缺失）即立**独立** finding，
category_pattern 用原词表。第三源的 grep 关键字：
- 默认状态: `setChecked(true|false)` / `ios:checked` / `cbAgreed = true|false` 等字段默认值赋值
- 点击响应: `setOnClickListener` / `onClick` 内 `startActivity` / `Intent` 目标 / `finish()` / `popBackStack()`
- toast 反馈: `Toast.makeText(...).show()` / `Snackbar.make(...)` + msg 文本字面值
- 震动 / 音效: `Vibrator.vibrate` / `SoundPool.play`
- 后端调用: `apiService.xxx` / `retrofit` interface 方法 / URL 字面值

iOS 源声明 X 而 HMOS 实测无 X / 行为不符 → 立 finding，category_pattern 写 `behavior_mismatch_ios_baseline`。iOS 源缺乏证据 → finding §1 标 "iOS 源参考缺失"，提示 fixer 后续确认。

**瞬时反馈覆盖**：行为对账的"落地态"含所有可观察反馈通道——不仅是稳定 UI，还包括 toast /
loading / 转场动画 / promptAction 弹窗 / 音效 / 震动 / 后端 API 调用。**HMOS 侧捕获手段不限截图**，
预期值来自录制真值（expected_ios 的 toast 文本 / iOS源码里的 Toast.makeText 字面值）：
- toast / 瞬时弹窗 → `hdc hilog` grep `promptAction.showToast` + msg 文本 对 expected_ios 比
- 后端 API 调用 → `hilog` grep `axios` / `RequestUtil` / 请求 URL + payload（对iOS源码声明的 URL）
- 音效 / 震动 → 不强求自动测，但 iOS 源含 `SoundPool` / `Vibrator` 而 HMOS 无对应 → 立 finding
- 动画 → 触发后 200-500ms 内连截 2-3 帧捕获过渡态

与录制真值任一通道有差异即立独立 finding。

「点击无响应」≠「跳转失败」≠「跳转到错页」 —— 三种都是 bug，必须明确归类到不同 category_pattern（`dead_handler` / `nav_failed` / `wrong_target`），不准合并到"导航失败"一个 finding 里。「checkbox 默认 true vs false」是默认状态差异，不是视觉差异，必须**验默认值**而非看勾选样式。

**完备性自检**（写本页 manifest 前问 3 遍）："本 page 每个**有录制真值**的元素都对账了吗？
无真值元素都进 untested_skipped(no_recorded_oracle) 了吗？表单默认值都和 expected_ios /
源码默认值比过了吗？" 任一答否 → 补做再退出。**禁止**写 "本轮未深入测试交互" / "留待后续
visual-verify"，**禁止**为补真值驱动iOS设备。

FOR EACH page IN batch_json.pages:

  # B.-1 关弹窗：已内置于 B.2 的 hmos_capture_page_e2e.py（保守词表+BACK 排水，2026-07-12）。
  # 仅当你手工接管导航时才需要人肉排水（同款规则：只点 关闭/取消/我知道了/跳过 类明确关闭词，
  # 禁点"确定/同意/立即开通"前进钮；关不掉的弹层本身可能就是 finding，交对比段别死磕；
  # 词表+BACK 都关不掉的形态 → 写 BLOCKED 单上报，**由主会话派 ad-profile-builder** 学
  # ad_profile.hmos.json——你没有子代理派发权（`spawn_agent` 归主会话），禁自派/禁在本 chunk 内死磕）

  # B.0 是否被上游阻塞？
  IF page.page_id IN prior_findings.blocked_pages:
      write BLOCKED_P{page_id}.md (引用 blocked_by_md_path)
      pages_status[{page_id}] = {status: blocked}
      CONTINUE

  # B.0.5 反哺节点特殊导航（仅当 page.id 含 "#via=" 才走）
  # 这类节点是 iOS Phase 2 黑盒发现物，page_id 形如 "MoreActivity#via=证件扫描"
  # 反哺到 fact-tree 时已经写好了 parent_page / via_trigger.text，HMOS 端需按 trigger text 找控件
  IF "#via=" IN page.page_id:
      parent_id = page.parent_page                              # fact-tree 反哺字段
      expected_trigger = page.via_trigger.text                  # iOS 源端发现的原文案
      cached_ios_shot = page.blackbox_screenshot            # iOS 落地截图缓存路径

      # 1) 先把 HMOS 走到 parent 页
      walk_to(parent_id) or {
          write SKIPPED_P{page_id}_parent_unreachable.md (reason=parent_walk_failed,parent=parent_id)
          CONTINUE OUTER LOOP
      }

      # 2) HMOS dumpLayout 看 trigger 在不在
      hdc shell uitest dumpLayout -p /data/local/tmp/_via_dump.json
      hdc file recv /data/local/tmp/_via_dump.json <TEMP>/_via_dump.json    # <TEMP>=/tmp 或 %TEMP%
      hmos_dump = load(<TEMP>/_via_dump.json)

      # 3) 严格 text 匹配 — 完全等于 expected_trigger
      target = find_clickable_by_strict_text(hmos_dump, expected_trigger)

      IF target:
          # 严格命中 → tap center → 继续走 B.3+ 标准 capture/多模态/markdown 管道
          tap_center(target.bounds)
          sleep 2
          # iOS 源端不重测：cached_ios_shot 直接当 baseline
          # → 跳到 B.3，by-pass B.1/B.2 (parent precondition 已满足 + 在 trigger 落地态)

      ELSE:
          # 4) 严格不命中，按顺序降级匹配（依次尝试，首个命中即采用）
          # 实测教训（2026-05-23）：iOS "拍照识物" ↔ HMOS "万物识别" 业务等价但
          # 文案完全无字符前缀/子串重叠，需要词法 + 业务语义两级降级才能避免误判 P0。
          
          BUSINESS_VERB_BAG = {
              "拍照", "识别", "扫描", "转换", "翻译", "计数", "识物",
              "OCR", "PDF", "Word", "Excel", "PPT", "图片", "文档", "证件", "导入", "保存"
          }
          
          fuzzy = None
          strategy = None
          
          # 4.a 词法层（前缀/子串）
          for cand in clickable_candidates(hmos_dump):
              if cand.text.startswith(expected_trigger) or expected_trigger.startswith(cand.text):
                  fuzzy, strategy = cand, "prefix"; break
              if expected_trigger in cand.text or cand.text in expected_trigger:
                  fuzzy, strategy = cand, "substring"; break
          
          # 4.b content_desc / resource_id token
          IF NOT fuzzy:
              for cand in clickable_candidates(hmos_dump):
                  if cand.content_desc == expected_trigger:
                      fuzzy, strategy = cand, "content_desc"; break
                  if expected_trigger_slug in cand.resource_id:
                      fuzzy, strategy = cand, "rid_token"; break
          
          # 4.c 字符集重叠 + 业务动词语义兜底（新加，修 P0 误判风险）
          # 触发条件：candidate 与 expected 共享 ≥2 个字符，且共享字符里
          # 至少 1 个落在 BUSINESS_VERB_BAG 任一词内（防止靠常见字"的/一/中"误匹配）
          IF NOT fuzzy:
              best = None; best_score = 0
              expected_chars = set(expected_trigger)
              for cand in clickable_candidates(hmos_dump):
                  overlap = expected_chars & set(cand.text)
                  if len(overlap) < 2:
                      continue
                  # 必须命中业务动词词袋
                  hits_verb = any(
                      any(c in verb for c in overlap)
                      for verb in BUSINESS_VERB_BAG
                  )
                  if not hits_verb:
                      continue
                  # tie-break: 更高 overlap + 同 parent.section 分组优先
                  score = len(overlap) + (1 if same_section_as(cand, parent_id) else 0)
                  if score > best_score:
                      best, best_score = cand, score
              if best:
                  fuzzy, strategy = best, f"char_overlap+verb (score={best_score})"

          IF fuzzy:
              # 文案不一致但似乎是同一功能入口
              write ALIGN_P{page_id_slug}_trigger_text_mismatch.md WITH
                    kind=ALIGNMENT_DIFF, severity=P1, fixer_layer=ui,
                    category_pattern=trigger_text_mismatch,
                    evidence={ expected: expected_trigger,
                               actual:   fuzzy.text,
                               match_strategy: strategy }
              tap_center(fuzzy.bounds)
              sleep 2
              # 继续走 B.3+ 标准管道（截图 + 多模态 + ALIGN）

          ELSE:
              # 5) 词法 + 语义都 miss → HMOS 真缺该入口（功能缺失）
              top_texts = extract_top_n_texts(hmos_dump, 15)
              write ALIGN_P{page_id_slug}_trigger_missing_hmos.md WITH
                    kind=ALIGNMENT_DIFF, severity=P0, fixer_layer=feat,
                    category_pattern=trigger_missing_hmos,
                    evidence={ expected_trigger: expected_trigger,
                               parent_page: parent_id,
                               hmos_top_texts: top_texts,
                               ios_baseline_screenshot: cached_ios_shot,
                               tried_strategies: ["strict","prefix","substring","content_desc","rid_token","char_overlap+verb"] }
              pages_status[{page_id}] = {status: fail, kind: trigger_missing_hmos}
              CONTINUE OUTER LOOP   # 该 variant 不走后续，下一个 page

  # B.0.6 dialog 对比特殊路径（2026-07-11 接线——Phase 2 已给可采 dialog 独立成图iOS基线）
  # 判定：PAGE_ID 在 tree.dialogs[]（python 一行式查树，与 Phase 2 1.1.4 同判据）。是 → 走本段，跳过 B.1-B.5：
  IF PAGE_ID 在 tree.dialogs[]:
      # 0) 基线门：spec/visual-verify/screenshots/ios/{trip}/{PAGE_ID}.png 不存在 →
      #    iOS侧也没触发出来（声明式排除 / 合法 BLOCKED——page_queue 是全量 dialog 入队，此门自筛）。
      #    pages_status 记 {status: skipped, reason: no_ios_baseline}，不出单不硬凑；CONTINUE
      # 触发数据从单一事实源取（与 Phase 2 同判据，禁自行解析）：
      #   python3 $SKILLS_ROOT/arkts-visual-verify/scripts/phase2_scope.py spec/toolkit-fact-tree.json --json
      #   → 该 dialog 的 from_page(FROM) / trigger_label(TRIG)
      # 1) walk_to(FROM) 到父页；不可达 → 按 B.2 同款写 CRASH_P{FROM}_navigation_unreachable
      #    （单出在父页头上，别赖 dialog）；本 dialog 记 status=blocked，CONTINUE
      # 2) HMOS dumpLayout 找 TRIG：严格 text → B.0.5 同款五级降级（含 BUSINESS_VERB_BAG 语义兜底）
      #    · 全 miss → write ALIGN_P{PAGE_ID}_trigger_missing_hmos.md（P0, fixer_layer=feat,
      #      category_pattern=trigger_missing_hmos；**iOS基线在场=iOS可触发，鸿蒙找不到=真迁移缺陷**；
      #      evidence 带 ios baseline png + hmos_top_texts + tried_strategies——B.0.5 同 schema）
      #      pages_status 记 fail，CONTINUE
      #    · 降级命中 → 照 B.0.5 写 trigger_text_mismatch P1，继续
      # 3) tap TRIG → 判"弹出了"：从iOS基线 dump（{PAGE_ID}.ios.xml）抽 2-3 条稳定文本当
      #    verify 信号，tap 后 HMOS dumpLayout 含任一 = 弹出
      #    · tap 后 layout 无变化 → CRASH_P{PAGE_ID}_nav_failed_….md, hint=click_no_effect（失败分级表原词）
      #    · 变了但 verify 信号全无 → 可能弹错/内容全缺——**别在此武断**，照走 4) 让结构+多模态出单
      # 4) HMOS 截图 + resize + dumpLayout（{PAGE_ID}.hmos.json）→ sbs 拼图 → B.3.5 结构 oracle
      #    → B.4 多模态（page_id=dialog id；ALIGN 单与普通页同格式同管道，schema 零新增）
      # 5) dialog 带 functional_checks → 在弹出态上走 B.4.5 dual-oracle（expected_ios 已由
      #    Phase 2 grounding 填；feat 单格式照旧）
      #    ★破坏性 dialog（退款/取消订阅/注销确认）：截图对比可以，**绝不点确定**（同 B.4.5 步骤 4 铁律）
      # 6) 关 dialog（BACK/取消/关闭钮）回父页；关不掉 → walk_to --restart-first 恢复 + manifest 记 note
      # 7) pages_status[{PAGE_ID}] 照常四桶计时 + capture_mode: dialog；edges/黑盒不跑（叶子，与 Phase 2 一致）
      CONTINUE OUTER LOOP

  # B.1 注入数据态（如有 precondition）——自愈梯（2026-07-10 ③，替代旧"造不出就 SKIPPED"）
  FOR pc IN page.preconditions:
      IF pc.kind == "state_required" AND NOT _state_satisfied(pc):
          # 态蒸发 ≠ 配方坏——主会话 checkpoint（dispatch 0.b）造过态，配方是活的，先重放再认输：
          # 1) 复验：重跑 check 配方（廉价非消耗；配方名读 progress.json.states_provisioned，
          #    checkpoint 已记；查无此 state → 不自愈，直接 3)——学习归主会话派 builder）
          # 2) check 红 → 就地重放 create 配方（包装脚本，device=harmonyos）→ 重回本页
          #    → _state_satisfied 复验过 → 继续 B.2+。★限额：同 state 同 batch 最多 1 次
          #    （create 多为消耗型）。★自愈必入账：manifest 本页记 state_repaired: {state, elapsed}
          # 3) create 重放失败 / 二次蒸发 / 无配方 →
          #    write SKIPPED_DATA_REQUIRED_P{page_id}.md（按 fix-file-schema 4.1.5：
          #    v4_data_state.reason=creation_flow_failed|db_empty，attempted_creation=true +
          #    attempted_creation_error=自愈梯已试记录，disposition=pending_data_seed）
          #    CONTINUE OUTER LOOP（主会话按路由派 scenario-builder 播种数据——配方级问题）
      IF pc.kind == "vip_required" AND NOT user_is_vip():
          # 不该到这里：trip_2 假设是 vip 账号
          log error, CONTINUE
      # login_required / nav_redirect_target / credits_required_amount 等
      # 由 scenario_chain 已经满足

  # B.2 到页+采集打包（★2026-07-12 机械化——旧 B.-1排水/B.2 walk_to/B.3 HMOS截图段整体
  #   由一次脚本调用包办：reset(仅force-stop)→排水→导航(iOSreach_path重放→链走,五级降级
  #   匹配+滚动/瞬态/BACK救场梯,动作锚定位置模型)→入口锚定到达→截图+dumpLayout。
  #   **失败即证据**：每个失败出口自动带证据包(现场截图+dump+步序+期望vs实际对照),你拿包
  #   直接写单,禁重导航重dump、禁"更努力到达"）
  python3 $SKILLS_ROOT/arkts-visual-verify/scripts/hmos_capture_page_e2e.py \
      spec/toolkit-fact-tree.json --page "$PAGE_ID" --trip "$TRIP_ID" \
      --target {hmos_target} --bundle {hmos_bundle} --ability {hmos_ability} \
      --shots-dir spec/visual-verify/screenshots/harmony/round-{N}/$TRIP_ID
  # H2E_JSON = 上面 stdout；H2E_EXIT = 其 exit code（bash `$?` / PowerShell `$LASTEXITCODE`）
  # 退出码路由（机械，无判断空间；单格式全走 fix-file-schema 既有 kind）：
  #  0  ok → JSON 直抄 manifest（nav_by/verify_confidence/hop_n/reach_path/elapsed 禁重计时），
  #          verify_confidence=low **不是失败**（入口锚定：页烂照采），继续 B.3 拼图
  #  21 ok+素材 → 同 0 继续采集对比（导航已成功、下游判定不受影响），**另**出素材单：
  #     · JSON.text_mismatches[] → 逐条 ALIGN trigger_text_mismatch P1（带 matched_by/expected/actual）
  #     · JSON.layout_drifts[] → **单出在父页头上**（page_id=parent_page，不赖目标页）：
  #       ios_first_screen=true → ALIGN_P{parent}_layout_drift_{trigger-slug}.md
  #       （category_pattern=layout_drift, fixer_layer=ui, P2；§2 期望=iOS首屏含'{trigger}'
  #        （{parent}.ios.xml 实证），§3 实际=鸿蒙滚动 {scrolls_needed} 屏才出现）
  #       ios_first_screen=false/null → 只记 manifest note 不出单（iOS也在折叠区/无档，非漂移）
  #       去重：B.4 多模态若已对同 parent 页报了同元素的位置/折叠差异 → 并进一张（同 page_id 内 LLM 拍板）
  #  20 trigger_missing → **负向判决，过复核门再写单**（见下方铁律 R9）：evidence.search_exhausted
  #          =true 且视觉复核通过 → ALIGN_P{page}_trigger_missing_hmos.md P0 fixer_layer=feat
  #          （evidence 齐全：parent_page/parent_anchor/expected_trigger/tried_strategies/
  #           search_exhausted/hmos_clickables/现场截图/ios_baseline——B.0.5 同 schema）；
  #          search_exhausted=false / 复核存疑 → 手工补扫完再判，仍缺才 P0，否则降 low_confidence 提示单
  #  22 click_no_effect → CRASH_P{page}_nav_failed_….md hint=button_dead（evidence.edge 指明哪条边）
  #  23 parent_unreachable/hop_limit → 单出在链上最早不可达的父页 + 阻塞子树（Step 4.B），
  #          本页 pages_status=blocked 引用之；若断点页本 batch 已出过单则只做引用不重复出
  #  24 escaped_app → SKIPPED（不算 bug；脚本已自动拉回 app）；若该 trigger 树上声明为应用内
  #          跳转 → 改写 wrong_target 素材
  #  25 app_crash → CRASH_P{page}_app_crash.md
  #  26 empty_state → B.1 数据态自愈梯（配方 device=harmonyos；重放后重调本脚本；无配方 →
  #          SKIPPED_DATA_REQUIRED 按 fix-file-schema 4.1.5）
  #  27 dump_unavailable / 14 screenshot_failed → 运维路径：重试一次，仍败写 partial manifest 上报
  #  2  边界拒跑 → dialog 走 B.0.6 / trip_1 链页归主会话——检查你走错了分支
  # 手工接管（例外，如 nav 数据缺口 unstable）：按 §导航方式 Compose 规则自走，到页后
  #   重调本脚本 --capture-only 收尾（就地截图+dump，nav_by 覆写 "llm"）

  # B.3 sbs 拼图（iOS baseline=Phase 2 录制产物直接复用，HMOS 侧图/dump 已由 B.2 脚本落盘）
  按 references/phase4-capture.md：拼 sbs（baseline 缺失场景见 2.1-a——SKIPPED 路由回 Phase 2）

  # B.3.5 结构 oracle（确定性，多模态之前先跑）—— P0-B
  按 references/phase4-multimodal.md 的 2.2-pre：
  跑 structural_diff.py（iOS dump = Phase 2 存的 .ios.xml + HMOS dump = B.3 取的 .hmos.json）
  → 硬差异(缺/多/序)入合并集；component_checklist + position_hints 注入 B.4 的多模态 prompt。
  两端 dump 任一缺失 → 跳过本步，仅多模态（不阻断）。

  # B.4 多模态对比（iOS vs HMOS）
  按 references/phase4-multimodal.md 流程（prompt 带上 B.3.5 的核对表划重点）
  产 ALIGN/CRASH/URL findings（按 references/fix-file-schema.md）
  # 合并去重：多模态 differences[] ∪ 结构 oracle differences[]，按 phase4-classify-write.md 2.3-0 规则

  # B.4.5 功能点双 oracle 判定（dual-oracle）—— 仅当该 page record 有 functional_checks[] 时跑
  #   ★0.5) 先调零点击普查器（2026-07-12 ②收缩版——机械化边界=只做"被操作对象可预期"的事；
  #     交互执行不机械化：鸿蒙是未完备被测物，脚本在坏页面上做 tap→观察→回来的闭环必然
  #     hardcode 到这个 app 的具体烂法，换 app 即崩）：
  #       python3 $SKILLS_ROOT/arkts-visual-verify/scripts/check_replay.py spec/toolkit-fact-tree.json \
  #           --page "$PAGE_ID" --trip "$TRIP_ID" --target {hmos_target} --bundle {hmos_bundle} \
  #           --ability {hmos_ability} --evidence-dir spec/visual-verify/hmos_evidence \
  #           --ledger-json spec/visual-verify/blackbox_discoveries/round-0/$PAGE_ID/${PAGE_ID}__manifest.json
  #     脚本零 tap（唯一设备动作=全页滚动普查），产 9 桶分流 JSON，**总数守恒==checks 数**（缺=双漏）：
  #       presence_executed     → view/custom_view 字面量已渲染（机械判）；语义等价你复核一眼即可
  #       enum_pass_mechanical  → enum 成员全在（机械 PASS，记 manifest 统计）
  #       locate_failed         → **阳性素材非跳过**：控件/字面量穷尽不存在（带 census_sample+共享截图+
  #                               search_exhausted）→ 按 R9 复核（改名?折叠?图标无文本?真缺）→ 真缺写
  #                               feat 缺失单（expected_ios 真值现成，不用点就出单）。
  #                               page_collapse=true 时大概率同根 → 按页级/SYSTEMIC 聚合别吐碎单
  #       interaction_pending   → 控件在场，**你按下方原 1)-5) 步逐个实测**（单点观察/破坏即停铁律照旧）
  #       deferred_outcome → 下方 1) verify_by=outcome 事务流程；deferred_webview → 下方 WebView H5 特化；
  #       deferred_destructive → 下方 4) 破坏性弹窗即停不点确定；precond_mismatch → 下方 2) 登录态校验
  #       （均附 found_in_census 提示）。★守恒自检：9 桶（presence_executed/enum_pass_mechanical/
  #       locate_failed/interaction_pending/deferred_outcome/deferred_webview/deferred_destructive/
  #       precond_mismatch/aborted）计数和必 == checks 总数（conservation_ok），不等=有桶漏处理
  #       aborted               → fail-open 残留，按原流程手工补，禁当 pass/skip
  #     你的判定工作从"逐 check 编排设备"收敛为"复核 presence/locate_failed + 实测 interaction_pending"。
  # 上游 Phase 2.5 grounding 已给每条 check 填好 expected_ios(iOS实测,主判据) /
  # ios_trusted(指纹判落点可信度) / expected_llm(LLM种子,保底) / precondition。
  # 读 fact-tree 该 page 的 functional_checks[];为空跳过。每条:
  #   0) ★check_kind 分流(枚举收敛产物,2026-07-10 fold_enum_groups)★:
  #      · check_kind=="enum_group_presence" → **零点击判定**:uitest dumpLayout 一次,对 check.members[].name
  #        逐一做文本匹配(滚动区先滚到底展开)。全部存在→PASS;缺任一/文案不符→FAIL 写 feat 单
  #        (§evidence 列出缺失成员名单;expected_ios 若为"全部存在"即iOS真值)。**不走 1)-4) 的点击流程**。
  #      · check_kind=="enum_group_behavior" → 走正常 1)-5),tap 目标= check.representative
  #        (代表值轮换可选:members_ref 指向的 presence.members[(current_round-1) mod n],跳过"全部/其他";
  #         判据/锚点/precondition 已随代表成员携带在本 check 上)。组内其余值不逐个测——
  #         同构组同一代码路径,presence 兜渲染层 + behavior 兜行为层。
  #      · 其它/无 check_kind → 正常 1)-5)。
  #   1) 鸿蒙侧操作该功能点,观察落地 H —— **先按 check.verify_by 分流(Q2 事务型 oracle;与 phase2.5 2a iOS侧对称)**:
  #      ★ verify_by=="outcome"(事务型:登录/支付/提交等)→ **绝不单点 tap(单点只碰门禁=Q2 病根),调 verify_outcome 走完事务**:
  #          python3 $SKILLS_ROOT/arkts-visual-verify/scripts/verify_outcome.py \
  #              --scenario <check.outcome_scenario> --device harmonyos --device-id <hmos_target> \
  #              --package <hmos_bundle> --project-root .
  #        · reached_outcome=true → H = 到达成功态(与 expected_ios 成功态比,一致=PASS)。
  #        · reached_outcome=false → H = 未到达成功态(事务真退化)。输出**自动带 failure_trace.signatures**
  #          (逐请求 path→status/toast,分级抓)→ 按 5c 归因首个失败步 + 同根 fold,再走 6) 对照实验判 P0。
  #        · scenario_not_found(无 outcome_scenario 配方)→ 记 scenario_not_found 上报,**由主会话反应式派
  #          scenario-builder** 学一份(你无子代理派发权,禁自派),**别退化成单点 tap**。
  #        (iOS grounding 与鸿蒙判定**调同一个 verify_outcome**——正是 Q2 病根"两侧各写散文、跑偏成门禁"的解药)
  #      ★ verify_by=="landing"(默认,绝大多数控件)→ 单点看落地,**定位方式按 check.tap_by 分流(2026-06,支持 Compose)**:
  #        · tap_by=="text"(Compose 注入,无 resource-id)→ 按 check.tap_text **文案定位**点击
  #          (uitest dumpLayout 找含该文本的可点击节点 bounds→tap center;Compose 本就靠文案/语义导航)。
  #        · 否则(XML 默认)→ 按 name / ios_anchor.raw_identifier(真 resource-id)定位 tap。
  #      (expected_ios/llm 含 toast 的项,点完 <1s 即时截图,否则 toast 抓不到)
  #      ★★ 落地是 WebView 容器页的特化(2026-07-11,与 phase2.5 2c 对称;H5=功能项非 UI 项)★★
  #        · expected_ios 是 {url, h5_signature} 形态(新粒度)→ 判定=①URL:按 phase4-webview 2.1.4-a
  #          抓鸿蒙端运行态 URL,compare_webview_urls.py 归一化比对(剔 ts/token/channel 等白名单参数);
  #          ②签名:落地 dump 含 h5_signature 静态文本。URL 对+签名对=PASS;URL 错=FAIL(接线错,真迁移缺陷);
  #          **URL 对但签名失配=low_confidence 提示复核**(大概率 H5 改版,非迁移缺陷,勿直接 FAIL)。
  #        · expected_ios 还是旧 activity 名粒度→ 判定退化为容器级(如实标 low_confidence:
  #          "真值粒度不足,容器恒真"),提示重新 grounding,勿装高置信 PASS。
  #        · 桥接类 check(anchor=@JavascriptInterface/onShowFileChooser 等)→ **进 H5 定向一跳**:
  #          H5 内找触发控件 tap,oracle=原生侧反应(原生确认弹窗/相册/拨号盘,与 H5 DOM 质量无关);
  #          H5 内定位不到控件 → 记 untriggered(**绝不 FAIL**,H5 改版≠迁移缺陷);
  #          破坏性桥(退款/取消订阅)点到原生确认弹窗即停,不点确定。
  #   2) precondition 校验:鸿蒙端当前登录态须 == 该 check 的 precondition,否则跳过 + 标 precond_mismatch
  #      (iOS真值在某登录态测的,鸿蒙必须同态比,否则 trusted 真值错配)
  #   3) 按 ios_trusted 分流判(语义匹配,非字面;方向/形态一致即可):
  #        ios_trusted=true → H 匹配 expected_ios → PASS;不匹配 → FAIL
  #            (expected_ios 是iOS实测可信真值,鸿蒙不符=真退化;形态退化如 弹窗↔toast↔整页 算不匹配→FAIL)
  #        ios_trusted=false → 退回 expected_llm 弱判 + 标 low_confidence(无论结果)
  #            (鸿蒙端实际可达且与源码预测一致时,feat 单补记"H与源码预测一致"供人工升级置信)
  #   4) 破坏性确认(退款/取消订阅/删除)点到弹确认弹窗即停,不点确定
  #   5) FAIL / low_confidence → 写 feat 单 spec/fix/round-{N}/feat/(fixer_layer=feat, kind=IMPL_MISSING,
  #      §evidence 带:expected_ios(主判据) + expected_llm(种子) + ios_anchor(iOS源码锚点,供 fixer 对照修)
  #      + 鸿蒙实测 H + confidence(high/low_confidence)。schema 见 fix-file-schema.md feat 层)
  #      ★(Q2 透传,若 check 带则一并写入 feat 单,供 fixer 提速):
  #        · source_section → 控件类型 = 修复模式直给(dialog→CustomDialogV2 / context_menu→bindContextMenu 长按 /
  #          enum_options→Picker/Select 选项 / bottom_sheet→Sheet / seekbar→Slider 拖动);fixer 不必再从截图猜控件类型。
  #        · precondition_required → 该功能点要在此前置态下才成立(写进 feat 单,fixer 复现/验证时照此造态)。
  #        · expected_source → 判据可信度(spec_acceptance>spec_nav>inferred);inferred 时 fixer 对 expected 留余地。
  #      ★★ spec 验收契约注入(2026-06,只 feat 单;与 §1 ios_source_refs 注入对称)★★
  #        写 feat 单前调:python3 $SKILLS_ROOT/arkts-visual-verify/scripts/inject_spec_oracle.py <page_id> "<check.feature_path>"
  #        解析 stdout JSON 的 spec_lines,原样写进 feat 单 §2 期望(行已带 "> " 块引用前缀)。
  #        作用:把 spec/baseline/features/F*.md 的「## 验收标准」行为契约喂给 fixer(expected_ios 只是一句话实测态,
  #              验收标准才有几档/默认/持久化/边界——feat 修复要的"怎么算对"。ui 单不注入,截图自足)。
  #        ★非静默铁律:resolved=false 时 spec_lines 是 "> spec_oracle: UNRESOLVED(...)" 行,**也原样写进单子**,
  #              绝不省略(让 fixer 知道去手读 spec,不静默遗漏)。旁路缺失则提示先跑 Step 1.0.6 build_spec_oracle.py。
  #      ★ feat 单 frontmatter 必带 page_id = 本 check grounding 时所在页(dual-oracle 当场就站在这页,白拿)。
  #        这是下面 5b 对账的 join 键——没有它,ui 单(按 page_id 命名)和 feat 单永远对不上。
  #   PASS 不写单,记进 manifest.functional_checks 统计。
  #
  #   5b) ★同页 feat↔ui 对账(fold,产出侧去重,2026-06-18)★
  #       目的:同一元素既功能退化(feat)又视觉不一致(B.4 已写 ui 单)= 一个根因,只许留一端,且不许矛盾。
  #       触发:本 check 判 FAIL/low_confidence 且要写 feat 单时,先扫 B.4 本页(同 page_id)刚写的 ui findings,
  #            按元素/anchor 模糊匹配(ui 单的 context_slug / 元素描述 ↔ 本 check 的 name / ios_anchor.raw_identifier)。
  #       命中后按 H 的失败模式定 primary,fold 另一端(外观细节不丢——折进留下的那张单正文;真有残留下轮重截再冒):
  #         • H = 缺失 / 空操作 / 跳错目标 / 形态退化(弹窗↔toast↔整页) → feat primary:
  #             - 删掉(rm)匹配的 ui 单文件;把它的视觉细节(文案/样式 expected)并入 feat 单正文"§3 实际"作实装验收点;
  #             - feat 单 frontmatter 加 subsumes_ui: [被删 ui 单的 id];manifest 该 ui finding 标 folded_into=feat_id。
  #             - 理由:元素都不存在/行为不对,谈何对齐外观;visual-fixer 按 expected_ios 端到端实装时本就会产出正确外观。
  #         • H = 元素在、但被 UI 挡死(遮挡 / 滚出屏 / 看着 disabled 点不到,功能失败只是症状) → ui primary:
  #             - 不写 feat 单;在保留的 ui 单正文补一句"该 UI 缺陷同时阻断功能 {check.name}(expected_ios: …)";
  #             - ui 单 frontmatter 加 subsumes_feat: [check_id];manifest 记 feat check folded_into=ui_id。
  #         • 无命中(真·独立:同页但不同元素/纯视觉差) → 各写各的,不 fold(不同根因,不冲突)。
  #       默认偏向:命中但 H 失败模式判不准时,默认 feat primary(实装即对齐;错选顶多多一轮,不丢数据)。
  #   5c) ★事务型(verify_by=outcome)失败:首个失败步归因 + 同根 fold(2026-07-09,治"终端症状单→fixer修一层剥一层拖长")★
  #       事务链(如 登录 = initUser 建会话 → 勾协议 → 发码 → 提交)失败时,verify_outcome 已把设备日志
  #       failure_trace.signatures(逐请求 path→status/toast/后端异常)抓进输出。据此写单:
  #       (a) **归因到首个失败步当根,别停在终端症状**:如 initUser status=-500「mediaNo null」是根,其后
  #           sendSms/bind 的 status=-1001「用户未登录」是**连带**。feat 单 §3 实际带全 trace、§5 根因指首个失败步。
  #       (b) **同根 fold(feat↔feat,补 5b 的 feat↔ui 之外的空白)**:同一事务链上多个 outcome 点(获取验证码+登录)
  #           若 failure_trace 同错误签名(同 status 码/同后端错误)→ **只写一张单**(归因首个失败步),别每点各一张。
  #           frontmatter subsumes:[其它 outcome check_id];manifest 其它点 folded_into=该单。
  #           实测教训:登录链曾出 2 张 -1001 单 = 1 个根因,分头修=拖长。
  #       (c) **隐藏后端步**(如 initUser,非 UI 控件、不在 functional_checks)只由事务 trace 暴露——若 app 日志未逐请求
  #           归因(failure_trace.tier=generic_fallback 全是系统噪音)→ 加**一次网络插桩**(HttpClient 打 path→status)
  #           确诊首个失败步后再出单,别拿终端 -1001 当根因糊过去(会让 fixer 修错层、多剥几轮)。
  #       (d) **写 reverify 块**(供 fixer C.5 round 内紧循环):本单是事务型失败、你刚跑过 verify_outcome 知道
  #           scenario/device_id/package → 写进 feat 单 frontmatter `reverify:`(schema 见 fix-file-schema.md)。
  #           fixer 据此重编重验、**在一个 round 内剥完 masked 分层**(登录=路径→mediaNo→…);不写=fixer 退回
  #           "待下轮验",masked 分层会拖成 K 个 round。走不完的事务(支付/OAuth)本就无 outcome 配方、不写 reverify。
  #   6) 门禁功能(登录/上传/授权/跳转到态)判定铁律:失败时默认假设=功能退化,不是"环境/网络"。
  #      升级/标 blocked 前必须对照实验:①另一端(iOS)相同输入能否成功——★单侧化 2026-07-12:
  #        对照证据**优先用录制**(该 check 的 expected_ios 即 Phase 2 iOS实测成功记录 /
  #        scenario artifacts 最近成功 run.log / builder 四证里的iOS对照),有录制证据即视为
  #        "另一端成功"成立,**不实跑iOS**;全无录制证据才 gate_experiment.py 实跑对照(唯一例外口)
  #      ②失败端平台是否健康(ping通/UI完整)
  #      ③即时失败(<1s关页/无loading/无报错=处理没真执行,强指向未实现)还是等待超时(才考虑网络)。
  #      另一端成功+平台健康+即时失败 → 写 P0 FAIL(kind=IMPL_MISSING,severity=P0;事务型按 5c 带 failure_trace +
  #      归因首个失败步 + 同根 fold)+ §6 blocks_subtree 列被阻塞下游,
  #      绝不降级 blocked/skip。真实漏测:鸿蒙登录不真正发起登录、即时关页,差点被当"模拟器网络问题"放过。
  # 注:这是 A2H 功能维度(有 oracle),与 B.5 测出边(纯导航)互补;详上游接口见 references/phase2.5-grounding.md。

  # B.5 测出边
  FOR edge IN page.edges_to_test:
      IF edge.contract_uncertain OR (NOT edge.trigger.label AND NOT edge.trigger.resource_id):
          # fact-tree 数据不全，跳过本 edge 测试
          NOTE in manifest.unstable_edges
          CONTINUE
      
      # B.5.a iOS可行性 = 查录制证据（★单侧化 2026-07-12：禁实时驱动iOS验证边）
      # 证据三级（任一命中即"iOS端该 edge 可行"，manifest 记 oracle_source）：
      #   1) tree.pages[edge.to_page].screenshots.{trip}.reach_path 含"从本 page 经该 trigger"
      #      的一跳（Phase 2 实走过——最强证据）
      #   2) 本 page 的 blackbox_behavior.{trip}[] 有该 trigger 且 outcome=page_change（账本实测）
      #   3) edge.to_page 的 inbound_triggers 有源码锚点 evidence_file:line（编译期声明——最弱，
      #      据此出的失败单标 confidence=declared_only，提示 fixer 先核iOS真机行为再动手）
      # 三级全无 → NOTE manifest.unstable_edges(reason=no_recorded_oracle)，跳过本 edge
      # （旧 FACT_TREE_INVALID_EDGE 的"iOS实点失败"判据随实点一起废止；树数据弱走 unstable_edges）

      # B.5.b HMOS 端点击 + verify
      hmos_result = python3 click_and_verify_edge.py \
          --device harmonyos --target {hmos_target} \
          --trigger-text {edge.trigger.label} \
          [--trigger-resource-id {edge.trigger.resource_id}] \
          --verify-text {edge.verify_signal} \
          --verify-timeout-ms 5000
      
      IF hmos_result.status != "ok":
          # 真 HMOS bug
          # 计算 blocks_subtree (该 edge 的 target + 该 target 的所有 reachable downstream)
          blocked = compute_subtree(edge.to_page, fact_tree)
          write CRASH_P{page_id}_nav_failed_{page_id}_to_{edge.to_page}.md
                with v4_edge + blocks_subtree=blocked
          NOTE in manifest.findings + manifest.blocks_subtree_propagation
          # 不要中断本 batch；这个 edge 失败只影响子树，本 batch 内其它 page 继续测

      ELSE:
          # HMOS ok → 在 edge.to_page 上
          # B.5.c 顺手测 back 是否能回 page（back 预期=树导航契约：child 返回应落 parent；
          #   无 parent 关系记录时 back 失败单标 low_confidence，不武断 P0）
          back_result = test_back_to_parent(expected={page.page_id}, device=harmonyos)
          IF back_result.failed:
              severity = back_critical(edge) ? "P0" : "P1"
              write CRASH_P{edge.to_page}_back_failed_{edge.to_page}_to_{page.page_id}.md
                    with severity={severity} + actual_landed
              am-start page or walk_to(page) 强拉回，保 BFS 不漂

  # B.6 黑盒兜底：已下沉到 Phase 2
  # ──────────────────────────────────────────────────────────────
  # 设计变更（v3.11 / 2026-05-25 重构）：黑盒探索不再在 HMOS sub-agent 里跑。
  # 改为 Phase 2 dispatcher + sub-agent chunk 模式（主会话编排）：
  #   1. scripts/dispatch_phase2_batches.py 切 chunk + 输出计划 JSON
  #   2. 主会话按 references/native-source-batch-prompt.md 派 sub-agent 跑每 chunk
  #   3. sub-agent 内 LLM-driven 真实点击导航 + 截图 + 黑盒发现写 manifest
  #   4. 主会话跑完所有 chunk 后再调 dispatch_phase2_batches.py（不加 --plan-only）
  #      聚合 manifest 反哺 fact-tree.pages[].screenshots.{trip}.reach_path
  #   5. scripts/materialize_blackbox_to_factree.py 仍用于反哺 extras_variants
  #
  # 反哺后的 variant page_id 形如 "MoreActivity#via=证件扫描"，会自然
  # 通过 build_page_queue → batches.json 进入 sub-agent 的 batch_json.pages，
  # 由 B.0.5 段统一走「parent + 严格 text match + 模糊降级」管道处理。
  #
  # 所以本 sub-agent 不再需要 extract_clickables / click_and_verify
  # 这套额外探测——遇到 #via= page 走 B.0.5，其它走 B.1+。
  
  # B.7 写本页 manifest 条目
  pages_status[{page_id}] = {
      status: pass | fail | crash,
      similarity: ...,
      high_count: ..., medium_count: ..., low_count: ...,
      edges_tested: N, edges_failed_hmos: M, edges_failed_factree: K,
      back_tested: true/false, back_failed: true/false,
      fix_files: [...],
      # ★计时账单(2026-07-10 插桩,必填;validate_batch_output 会警告缺失)★
      # 采集铁律:计时命令**搭在本来就要跑的 Bash 调用里**(步骤首条命令前记 epoch 秒 S、
      # 末条命令后打印 T_<桶>=now-S；bash 用 `date +%s`，PowerShell 用 `[int](Get-Date -UFormat %s)`),**禁止为计时单独发工具调用**——
      # 否则插桩本身制造 LLM 回合开销。桶边界:scenario=B.-1/2.-1造态 nav=B.0-B.2导航+确认
      # capture=B.3截图/dump/sbs compare=B.3.5+B.4 functional=B.4.5 edges=B.5 write=B.7+写单
      elapsed: {scenario: <s>, nav: <s>, capture: <s>, compare: <s>,
                functional: <s>, edges: <s>, write: <s>},
      # 行为对账铁律证据（必填，B 审核员规则 5 据此判定；详 Phase B 开头铁律段。单侧化 2026-07-12）
      interaction_test_summary: {
          tested_count: <int>,        # 本 page HMOS 实测且有录制真值可对账的元素数
          diff_count: <int>,          # 与录制真值有差异的数量（每条立独立 finding）
          untested_skipped: [         # 跳过的交互 + 原因（no_recorded_oracle / 长按 / 需特定数据态）
              {element: "<selector>", reason: "<具体原因>", oracle_source: "<functional_checks|ledger|source|none>"}
          ],
      },
  }

### Phase C: 收尾

写 manifest.json:
{
  batch_id, current_round,
  started_at, finished_at, duration_seconds,   # ★必填(2026-07-10)——进 Phase A 第一条命令记 date -u,
                                               #   写 manifest 时算差;历史上 13 个 batch 只有 4 个填了,
                                               #   耗时分析只能靠文件 mtime 验尸。validate_batch_output 警告缺失
  scenario_chain, scenario_results,
  pages_status: {...},
  findings: [...条 ALIGN/CRASH 高层摘要],
  systemic_candidates: ,
  blocks_subtree_propagation: [
      {root_cause: "CRASH_P0001_nav_failed_HomeActivity_to_MineFragment",
       blocked_pages: [AccountInfoActivity, AboutUsActivity, ...]}
  ],
  unstable_edges: [...contract_uncertain 跳过的],
  // 黑盒兜底产出
  blackbox_stats: {
      total_unknowns_explored: 12,
      missing_page_findings: 3,
      missing_edge_findings: 5,
      decoration_filtered: 2,
      escaped_app_count: 2
  },
  page_signature_map: {                         // 给主会话用：本 batch 期间观察到的 page sig
      "HomeActivity":   "...|s1f0c|tabcd",      // 用于 lookup_page_signature
      "AccountInfoActivity": "...|s27510|t...."
  }
}

并在 batch 结束时更新全局缓存:
  spec/visual-verify/batches/_global_explored_clickables.json
    schema: {signature: {first_explored_at: ISO, from_page: str, outcome: str}}

完成后 sub-agent 退出。主会话读 manifest，做跨 batch 阻塞传递 + systemic 聚类。

## 重要约束（铁律）

R1: 永远不用 am-start 直跳非 launcher 内部页（HMOS 单 ability 架构，跳不到）
R2: 失败 edge 先查**录制真值**（B.5.a 三级证据）再判 HMOS bug（避免冤枉）；仅声明级证据的单
    标 confidence=declared_only。★Phase 4 全程禁驱动iOS设备（唯一例外：B.4.5 步骤 6 门禁对照
    实验且录制对照证据全无时走 gate_experiment.py）
R3: HMOS 端测 edge 失败时不要重试 > 3 次（避免假阳性 + 浪费时间）
R4: 跨 page 的 back 预期 = 树导航契约（inbound/parent 关系：从 child 返回应落 parent）；
    无 parent 记录的 back 失败标 low_confidence（★不再实时驱动iOS当 back 基准）
R5: 多模态对比图严格 resize ≤1800px（不然 API 报错整轮报废）
R6: manifest 必须落盘，即使中途 batch 中止也要写 partial manifest
R7: 不读 spec/toolkit-fact-tree.json 全文，需要时读 spec/visual-verify/batches.json (本 batch 段)
R8: 黑盒探索已下沉 Phase 2（iOS 源端一次性勘察 + 反哺 fact-tree）。
    sub-agent 不主动跑黑盒；遇到 page_id 含 "#via=" 的反哺节点统一走 §B.0.5
    流程：parent walk_to → 严格 text 匹配 → 失败降级模糊匹配 → 全无降级写
    ALIGN(trigger_missing_hmos, P0)，文案近似命中写 ALIGN(trigger_text_mismatch, P1)
R9: **负向判决复核门（2026-07-12）**：机械判定分两类且风险不对称——正向观察（点了没反应/
    落错页/outcome 与账本不符）是直接观测，可径直出单；**负向判决（"入口不存在""元素缺失"，
    含 exit 20 与 B.3.5 结构 oracle 的 missing 类）本质是证明不存在**，dump 只含已渲染节点，
    折叠区/懒加载虚拟列表/折叠面板/页内横向 tab/图内文字都会造假阳性（实测：'关于我们'在
    鸿蒙折叠区，无滚动救场就是一张假 P0）。写 P0 前必须：①evidence.search_exhausted=true
    （脚本已滚到真底）②你亲眼读一次证据截图复核（你是多模态 agent，这一眼很便宜）。
    任一不满足 → 手工补扫/降 low_confidence，绝不直出 P0。

## 增强工具（2026-05-22 借鉴 HomeTrans）

### page_signature 双重确认（自动）

`click_and_verify_edge.py` 默认输出 `pre_click_signature` + `post_click_signature` + `page_changed`。

**用法**：
- `page_changed=True` + `verify_found=True` → 正常成功
- `page_changed=False` + `verify_found=True` → status="verify_text_but_page_unchanged"
  含义：verify text 在 click 前后都存在，**click 可能根本没生效**（button dead）。
  应当报 NAV_FAILED 而不是 OK——这是 HMOS button 接错 handler 的典型现象，
  scan 项目 "退出登录失败" 就是这种 case
- `page_changed=True` + `verify_found=False` + `verify_timeout` → 跳了别处但没到预期页
  含义：可能跳到错误页，或动画太慢——按 NAV_FAILED 处理但 hint=jumped_to_wrong_page

### escaped_app 检测（需 sub-agent 显式打开）

调用 `click_and_verify_edge.py` 时传 `--expected-bundle com.example.demoapp.hm`。
返回 `status=escaped_app` + `escaped_to_bundle=<外部 app bundle>` 时，**不要当 HMOS bug 报**：
- 这是真实业务行为（如点击"联系我们"跳浏览器、点支付跳微信）
- 写 SKIPPED placeholder（或不写，看主代理决策），不要写 CRASH_NAV_FAILED
- 之后 force-stop 主 app + restart 回到当前测试态

```text
# 推荐调用模式
python3 click_and_verify_edge.py \
    --device harmonyos --target {hmos_target} \
    --trigger-text "{label}" --verify-text "{verify_signal}" \
    --expected-bundle {hmos_bundle} \
    --verify-timeout-ms 5000
# exit 6 → escaped_app；不算 HMOS bug
```

### restart_first 兜底（back 失败后用）

当 back 测试连续失败 ≥ 2 次或 app 漂到未知态时，用 `walk_to.py --restart-first` 强制恢复：

```text
python3 walk_to.py \
    --device harmonyos --target {hmos_target} \
    --page-id {当前应该在的 page_id} \
    --fact-tree spec/toolkit-fact-tree.json \
    --bundle {hmos_bundle} --ability {hmos_ability} \
    --restart-first   # ← 加这个 flag
# 内部: force-stop + aa start + 5s 等冷启动 + walk
```

适用场景：
- back 让 app 漂到非预期页 → restart_first 干净恢复
- escaped_app 后回主 app → restart_first
- 测了 10-15 个 page 后定期 hygiene → restart_first 清积累状态

### 失败分级表

| click_and_verify_edge 输出 | 写什么 markdown |
|---|---|
| `ok` + `page_changed=true` | (无 finding，正常通过) |
| `verify_text_but_page_unchanged` | CRASH_*_nav_failed_*.md，hint=button_dead |
| `verify_timeout` + `page_changed=true` | CRASH_*_nav_failed_*.md，hint=jumped_to_wrong_page |
| `verify_timeout` + `page_changed=false` | CRASH_*_nav_failed_*.md，hint=click_no_effect |
| `trigger_not_found` | 有录制证据（B.5.a 1/2 级）→ CRASH_*_button_missing（iOS有、鸿蒙无，真迁移缺陷）；仅声明级/无证据 → NOTE unstable_edges（树数据弱，不冤枉鸿蒙）|
| `escaped_app` | （不当 HMOS bug；可写 SKIPPED 或忽略） |
| `click_failed` | CRASH_*_nav_failed_*.md，hint=hdc_input_failed |
```

---

## 错误恢复策略

| 场景 | sub-agent 行为 |
|---|---|
| scenario 失败 | 整 batch status=batch_blocked，所有 page 写 SKIPPED，退出 |
| walk_to(starting_page) 失败 | 同上 |
| 当前 page 截图失败（app crash 等）| 写 CRASH_P{page_id}_app_crash.md，跳过该 page 继续下一个 |
| edge 测试触发 app crash | 同上 + 标该 edge 为 trigger_crash |
| back 测试导致 app 漂到未知页 | am-start launcher → walk_to 当前 page，重试一次；仍失败标 navigation_unreachable |
| hdc 设备掉线 | 整 batch 中止，写 partial manifest 退出，让主会话决定是否换设备（★iOS设备不在环内，其状态与本 batch 无关）|

---

## 调用契约（主会话注入）

主会话调用 sub-agent 时 prompt 渲染参数：

```python
prompt = render_template("sub-agent-batch-prompt.md", {
    "batch_id":         batch.batch_id,
    "batch_json_ref":   f"spec/visual-verify/batches.json (trip={trip.trip_id}, batch={batch.batch_id})",
    "current_round":    N,
    "ios_serial":   "emulator-5554",   # ★单侧化后仅 B.4.5 步骤6 gate_experiment 兜底路径可能用；常规流程不驱动
    "hmos_target":      "127.0.0.1:5555",
    "ios_pkg":      "com.example.demoapp",
    "hmos_bundle":      "com.example.demoapp.hm",
    "hmos_ability":     "PhoneAbility",
    "blocked_pages":    [...],   # 主会话从前序 batch 的 blocks_subtree 累积
    "retry_edges":      [...],   # 上一轮失败本轮要重测的
})
```
