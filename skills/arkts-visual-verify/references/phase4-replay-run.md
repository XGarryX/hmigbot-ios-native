# Phase 4 鸿蒙一笔画回放 — 运行手册（2026-07-23）

> **状态:投产主路。** 一笔画回放是**鸿蒙侧覆盖的主方式**(与iOS Phase 2 边遍历对称),不是实验特性——
> 覆盖主链(Home→大纲→模板→PPTFile)一律走一笔画。**只有过程中撞阻塞时才按节点回退页粒度保底**:
> 触发条件 = replay_exec 级联升级(exit 32)/ 回位连败(`needs_pagegranular_fallback`)/ 异步时序·前置态
> 震荡够不到的节点(见 [`phase4-replay-judge.md`](phase4-replay-judge.md) J1.5 + [`phase2-edge-walk.md`](phase2-edge-walk.md))。
> **保底只兜"一笔画够不到的那几个节点",不是整趟降级页粒度。**

回放全链:**编译(compile_replay_plan) → [切段 slice_batches,可选] → 执行(replay_exec,纯机械) → 判定(judge 出单) → 修复(visual-fixer) → 回归**。
本手册讲**编译+切段+执行**(前半程);**判定+修复+回归闭环接线见 [`phase4-replay-judge.md`](phase4-replay-judge.md)(J1–J5,复用主线 Phase 5/6+visual-fixer+Phase 6.5 自持闭环,不另造)**。
capture_manifest 与页粒度 role=capture 契约同构,故下半程零改复用。
设计根由见 phase4-replay-compile.md / phase4-replay-executor.md;本文是**怎么实际跑**。

## 0. 铁律:先读全树字段,别在运行时重新发明(2026-07-23 用户纠正,最重要一条)
树里iOS侧已定性的账**必须尊重**,别把它已经处理过的当待办:
- `blackbox_behavior[].outcome` 以 `skipped_` 开头(skipped_homogeneous/skipped_in_plan/skipped_destructive)
  = node_sweep **已做过同构去重/已定性**,**不是待测功能点**,消费时直接跳过。
- 忽略此标记 → 把 18 张同构模板卡、9 条动态示例文案全拉进 reconcile → 侵入 + 拖时间 + 逼你在运行时
  重造同构去重(答案本就在树里)。**教训:消费树先读全字段,尤其 outcome/status 这类『已定性』标记。**
- reconcile 的元素**主来源 = `functional_checks`(该页干净功能点清单)**;blackbox_behavior 只补真实观察(非 skipped)。

## 1. 前置产物(缺一不可)
| 产物 | 谁产 | 内容 |
|---|---|---|
| `spec/toolkit-fact-tree.json` | iOS侧流水线(indexer+ART+反哺) | 含 runtime/functional_checks/blackbox_behavior;waited_s 需已反哺 |
| `spec/visual-verify/edgewalk-run2/walk_plan.json` | plan_edge_walk.py | 边粒度 DFS 步序(kind:push/dialog/tab_switch…) |
| iOS基线 dump ×2 轮 | 两轮遍历的 shots/*.xml | dump-diff 识别动态文案(哨兵去噪) |
| `spec/visual-verify/replay_annotations.json` | **编译期 LLM/人手写(每 app 一份)** | 见 §3 |

## 2. 编译:产 replay_plan_hmos.json（机械,零 app 常量在代码里）
> 下文 `$SCRIPTS` = `$SKILLS_ROOT/arkts-visual-verify/scripts`（全 py，三平台同一份；Windows `python3` 读作 `python`，见 windows-setup.md）。
```text
python3 $SCRIPTS/compile_replay_plan.py \
    --walk-plan <walk_plan.json> --tree <fact-tree.json> \
    --baseline-dir <轮2 shots目录> --baseline-dir2 <轮1 shots目录> \
    --annotations <replay_annotations.json> --out <replay_plan_hmos.json> [--default-wait 4]
```
机械 pass:①dump-diff 识别动态文案(剔哨兵/剔 reconcile)②`functional_checks`+`blackbox_behavior`(尊重 outcome)
产 reconcile 清单③node_sweep 四规则分边:**push 深下沉留 DFS 走序 / dialog 浅下沉移进 reconcile 当场测**
(dialog 的 DFS 步+配对 back 一起跳过)④哨兵**确定性排序**(按跨页稀有度,治抖动)⑤chrome/tab栏/子tab/破坏性剔除。

## 3. annotations schema(每 app 数据,不进代码——app 无关性靠这个)
```jsonc
{"app": {"bundle": "...", "ability": "..."},
 "input_edges": {"<from>--<trigger>": {"field_type":"TextInput","text_from_cli":true}},  // 需先输入的边(创作流填主题)
 "state_signatures": {"<trip>": ["ID:","VIP会员"]},        // 态检测(登录/VIP)——preflight 用
 "edge_overrides": {"<from>--<trigger>": {"locate_budget_s":70}},  // 异步门边:控件延迟渲染,轮询定位
 "reconcile_exclude": {"<node>": ["输入主题","导入文档"]},  // 页内子tab等非walk导航,reconcile不点
 "extra_blacklist": ["转人工","咨询客服"]}                   // 追加破坏性/危险词(默认词表见 plan_edge_walk)
```
★ **换 app 时代码不动,只重写这份 annotations + 换树 + 换基线**。这几项**原则上 LLM 编译期可从树推导**
(sub_tab 从 navigation_contract、异步预算从 waited_s、态签名从登录基线),现为手写——**LLM 自动生成是待做项(#9正式编译器)**。

## 3.5 切段(可选):slice_batches.py — 分段独立冷启跑
整条计划可切成"每段=冷启+一个 root-tab 子树"的 batch(分段冒烟/并行/单区域重跑)。边界从计划结构推导(root 的 tab_switch tap),零 app 常量。
```text
python3 $SCRIPTS/slice_batches.py --plan <replay_plan_hmos.json> --out-dir <目录> [--strip-login]
```
`--strip-login`:去 preflight.login_scenario(smoke 用,设备须已登录;避免撞未验证的自动登录)。产 `batch_<i>_<lead>.json`,各自 `replay_exec` 单跑。

## 3.9 ★机械为主 / LLM 为辅：退出码交接 + 断点续跑（2026-07-25 用户拍板）

**为什么改**：纯 0-LLM 回放在目标实现良好时最快（实测 125 步 43s），但目标一旦跑偏就**死磕**——
实测 25 个 tap 全撞同一个鸿蒙独有启动弹窗，1 节点采到、124 步空转，**1 个根因报成 11 张缺页单**。
iOS侧「分工轴铁律」早记同一教训（脚本编排 5 节点就断 / LLM 编排跑完 20）。
区别：鸿蒙侧**已有iOS GT 当路径**，LLM 不必"探"，只在墙前出场 → 代价远小于iOS侧。

```
┌─ replay_exec --resume-from N   （机械，全速）
│    exit 0  完成
│    exit 30 未知模态挡路（无白名单安全关闭键）
│    exit 31 位置失配（期望页 X，实际在 Y）
│    exit 32 级联根因（连撞同一障碍）
└─→ LLM 读 out-dir/checkpoint.json（含 modal_type / buttons / streak / evidence / diagnosis）
      ① 判性质 ② 处置或判定不可过 ③ **记 llm_intervention** → 回到顶部 --resume-from N
```

### 门禁确认键：**当场判，不用词表**（用户拍板，2026-07-25）
撞到"唯一按钮是确认类"的门（首启协议/隐私/声明/权限说明…）时，
**不加白名单第三档**——词表换个 app 就崩（文案不含"协议"二字的门禁遍地都是）。
改由 **LLM 看现场判**，判据是**语义不是字面**：

| 判据 | 可点 | 不可点 |
|---|---|---|
| 后果可逆性 | 仅确认知悉/授予展示权限 | 涉金额、订阅、注销、删除、权限授予后不可撤 |
| 是否消费资源 | 否 | 扣费/耗次数/发短信/发消息给真人 |
| iOS侧对照 | iOS有同类门且已过 | iOS没有 → 更要谨慎，先记差异 |

**拿不准一律不点**，记 `blocked` + checkpoint 交人工。

### 铁律：介入必留痕、必出单
> LLM 介入解决了障碍 ≠ 差异不存在。**机械回放走不下去，本身就是两端结构对不上的证据。**
> 每次介入必须写 `manifest.llm_intervention[]`（含**看到什么 / 为何判可点 / 做了什么 / 产生什么 finding**），
> `build_judge_input` 会把它们收进 `llm_interventions[]` 并标 `must_ticket`，**judge 不得只当"恢复成功"翻篇**。
> 不立这条，等于拿 LLM 的善意帮忙把迁移缺陷洗白——与覆盖完整性铁律（SKILL.md §1.1 第 4 条）直接冲突。

## 4. 执行:跑 replay_exec.py（机械段；撞墙按 §3.9 交接）
```text
python3 $SCRIPTS/replay_exec.py \
    --plan <replay_plan_hmos.json> --serial <hdc目标> \
    --bundle <bundle> --ability <ability> --out-dir <输出目录> [--input-text "测试主题"]
```
产物:`capture_manifest.json`(role=capture 契约:pages_status + per_page.{screenshot,dump,behavior_observations,
observation_notes} + **functional_coverage** + **reconcile_unsettled**)+ shots/ + dumps/ + run.jsonl。

### 4.1 ★落位 + 闸(2026-07-25 新增,**不做这两步不许进判定**)
`replay/<run>/` 是**工作区不是交付位**(output-layout 铁律)。跑完必须:
```text
python3 $SCRIPTS/replay_place_artifacts.py --capture-dir <out> --round N --trip <trip> \
    --project-root <根> --ios-baseline-dir spec/visual-verify/screenshots/ios/<trip>
python3 $SCRIPTS/assert_replay_artifacts.py <根> N <trip> <out>      # 红了=漏测,不许当通过
python3 $SCRIPTS/assert_gap_ticket_coverage.py <根> N <trip> <out>   # 缺页必须被合法认领+分类举证
# ★ 两条**都不是可选的**：它们的退出码现在由 Phase 6.4 assert_round_complete.py 汇总，
#   而 round_budget.py next 没有 spec/fix/round-N/_run_state.json 就直接 exit 2 —— 跳过=拿不到任何轮次结论。
#   （2026-08-16 前这两条只是"文档要求"，实测 round 4-6 报红但无人理会，照样输出 CLEAN_AT_EXIT）
```
闸的四条:①canonical 交付集 ≡ iOS baseline png 全集 ②每张图配对 `.hmos.json` ③sbs 齐套
④**功能点行为覆盖=1.0**(feat 单的素材供给率;页覆盖 100% 也可能行为覆盖 0%)。

### 4.1.5 ★破坏性收尾趟（trip-end pass）—— 完整接线（2026-07-25 补，此前只有散文没有步骤）
正常趟对破坏性元素**只定位不点**（记 `encountered_destructive`），所以：
`<页>#via=<破坏性触发>` 这类**iOS交付过基线**的确认窗页，鸿蒙侧**唯一可采时刻 = 确认窗弹出那一刻**。
它们不是豁免，是**必须跑收尾趟**（`coverage_pending_trip_end` 里逐页列名，闸 cond 1b 卡）。

```text
# ① 读 handler 产本轮 hprof（LLM 读 ArkTS 源码定性；只对正常趟**真遭遇过**的组件读，读码集塌到个位数）
#    输入 = <正常趟out>/encountered_destructive.json，产物 schema 见 phase4-replay-hmos-destructive-profile.md
# ② 裁最小走序（纯机械：只留"真渲染过 + hprof 判可安全验"的支路，无关支路整棵剪掉）
python3 $SCRIPTS/trip_end_slice.py --plan <replay_plan.json> \
    --encountered <正常趟out>/encountered_destructive.json --hprof <hprof.json> \
    --out <trip_end_plan.json>
# ③ 跑收尾趟——★必须换 out 目录（同目录跑会截断正常趟的 run.jsonl 与 manifest）
python3 $SCRIPTS/replay_exec.py --plan <trip_end_plan.json> --trip-end-pass \
    --hmos-profile <hprof.json> --out-dir <收尾out> --serial … --bundle … --ability …
# ④ 合并两趟——★必须给 --plan（用**完整**计划，不是裁过的），否则覆盖账不重算
python3 $SCRIPTS/merge_capture_dirs.py --out <merged> --plan <replay_plan.json> \
    <正常趟out> <收尾out>
# ⑤ 对 merged 目录落位 + 过闸（**不是**对任一单趟目录）
python3 $SCRIPTS/replay_place_artifacts.py --capture-dir <merged> --round N --trip <trip> \
    --project-root <根> --ios-baseline-dir spec/visual-verify/screenshots/ios/<trip>
python3 $SCRIPTS/assert_replay_artifacts.py <根> N <trip> <merged> <replay_plan.json>
```
**为什么必须这样串**（2026-07-25 审核实测的三方打架）：
- 对**收尾趟目录**单独过闸 → cond 1/4/5 全红（页太少 / 非破坏性元素全 `continue` 零观察 / `_full` 恒 false）；
- 对**正常趟目录**单独过闸 → cond 1b 永远红（它的 manifest 不会因为收尾趟跑过而更新）；
- 合并但**不给 `--plan`** → 字段来自"先到先得"的某个目录，两趟观察合不到一本账上 → **闸假红 + 假绿并存**。
⇒ 三本覆盖账（页 / 功能点 / reconcile 欠账）统一由 [`lib_coverage.py`](../scripts/lib_coverage.py) 算，
**是对 (计划, manifest) 的纯函数**，所以合并后能原样重算。执行器与合并侧共用同一实现（禁重实现）。

**诚实失败出口**：收尾趟跑过、且 hprof 如实判"鸿蒙没有确认弹窗"→ 执行器**正确地拒绝点** →
该页在鸿蒙侧根本不存在可采时刻。此时进 `justified_uncapturable`，闸不再计欠账
（否则就是"去跑你已经跑过的那趟"式假红——**假红比空过更危险，它教人绕闸**），
但 `unverified_destructive` 强制报缺桩仍在，judge 必出单。

### 4.2 每张截图必配 dump —— 唯一落盘口 `_shot()`
执行器**禁止直接调 `drv.screencap()`**,一律走 `_shot(name, txt)`(图 `X.jpeg` ↔ dump `X.hmos.json` 同名配对)。
实测教训:11 个截图点只有 `capture()` 一处写 dump → 60 张图对 20 份 dump,而裸奔的恰是两条承重线
(`__el*` = reconcile 逐元素现场 / `__weak` = 弱到达现场)→ judge 拿到 15 条 not_found + 5 条 noop
**一份现场 dump 都没有** → 三分归因无法执行 → 20 条疑点出单接近 0。

## 5. 血泪教训清单(去别处踩之前先读)
**A 通用原则(任何 app 适用)**:
- ★§0 那条:消费树读全字段,尊重 outcome/status 已定性标记,别运行时重造(同构去重/动态识别答案都在树里)。
- 每次 tap 前重新 dump,绝不缓存世界观(被测物"坏是常态",屏会自己变;缓存=拿过期世界观 mis-tap)。
- 到达门控:验证到达目标才截图入账,未到达绝不按目的地命名(否则截图账本说谎)。
- reconcile 对齐 node_sweep 四规则:walk(push)留走序 / ground+dialog 当场 tap→观察→BACK / destructive 不点 /
  同构 N≥3 抽验1;每元素保险丝(连续2个回不来中止本页)。
- ★**reconcile 判位靠页身份,不靠计划步序**(2026-07-25 实测):绑死步序 = 错过就永不重试。
  MemberCenter 的 reconcile 排在计划 idx46(从 AccountInfoActivity 过去),那条边 WRONG_LANDING,
  实际 step62 才从 MineFragment 到了页上——**站在页上却因为"那一步早翻篇了"16 个功能点一个没测**。
  改法:`_PEND` 欠账表 + 每次到页 `_arm_reconcile()` 就地插队;站在**别的已知页**上时
  发 `RECONCILE_DEFERRED` 但**不消费欠账**(绝不在错页上采,会产整片假 not_found)。
- ★**回位失败先重导航,连败 2 次才中止**(2026-07-25 实测):旧实现 `if not restored: break`
  一次失败即丢整页剩余元素,且让下方 `consec_fail>=2` 成为**永远执行不到的死代码**。
  实测 RecommendFragment 元素#7 一次失败吃掉剩余 8 个;全局 82 个计划元素只观察到 36 个(43%)。
  重导航策略全部取自计划(入边 tap / 受 ROOTS 守卫的 BACK),零 app 常量。
- ★**中途中止 ≠ 结账**:只有全部元素过完才 `RECONCILE`,否则 `RECONCILE_PARTIAL` 且**留在欠账表**,
  下次站上这页按 `(trigger_text, rid)` 去重续采。旧实现采 1 个也算翻篇。
- ★**未定位现场必须留证**:`not_found` 是 P0(控件不在 dump=`control_missing_in_hmos`)与
  自证工具 bug(控件在 dump=`locator_failed`)的**分水岭**,恰恰最需要证据。三条 not_found 出口
  原先零截图零 dump → judge 只能弃权。现在一律留 `__notfound` 图+dump,并机械落
  `label_in_page_texts` / `enumerated_screens` / `blame_hint` 供三分。
- ★**危险是方法约束不是覆盖豁免**(SKILL §1.1 第4条在回放侧的落法):首启单行道页原先整页
  `elements=[]`,把「进度条/轮播/加载进度/权限说明」这种**根本不用点**的功能点一起丢了
  (iOS有 7 条 ios_trusted 真值,鸿蒙一条没验)。改按 `needs_tap()` 三分——判据取
  **iOS基线 dump 的 clickable 属性**(零词表,换 app 照用):可点的跳过并记原因,
  不可点的走 `observe_only`**只验渲染不点击**。错向安全(误判只会少点一次,绝不会点穿向导)。
- 安全双保险:safety!=normal 整边跳 + 触发词硬黑名单(防计划标注洞)。
- 弃权≠缺陷:ABANDON 只说"没够着",判定层禁自动升级成 feat 单(定位数据坏时它对错什么都没说)。

**B 鸿蒙特有(因单 ability/无 id/键盘/异步)**:
- **pagePath 退化**(这个 app 整个跑在单 SplashPage)→ 判位不能靠 pagePath,靠**内容哨兵 + 页签名双引擎**
  (identify 加权哨兵管有名页 / page_signature_from_dump 注册表管无名页+精确同一性+环检测)。
- **app 组件无 rid**(ArkTS 不设 .id())→ 定位/同构判据不能用 rid,用文本(five_match)/结构(class+坐标带)。
- 哨兵**确定性排序**必须做(集合切片非确定→哨兵抖动→"时好时坏"的元凶)。
- input 后**先判键盘真开着再收**(误发 back=假BACK退页);中文可直填(免iOS ASCII 绕行)。
- 每轮开跑干净重启(别把上轮打断残留当 app 缺陷);冷启时长是变量→轮询根哨兵禁固定 sleep。
- 异步门边(生成完才渲染的控件)→ annotations 给 locate_budget 轮询定位。
- **屏外元素两级滚动**(2026-07-22,师承 blackbox enumerate/hmos_capture find-then-scroll):walk 边定位 miss→scroll_find 上滑≤3屏(到底=两屏签名同,miss 滚回复原);reconcile 进页**一次滚动全量枚举**(合并 page_texts+clicks,回顶)→枚举都没有=真 not_found(searched:full_page),有=滚到出现实时 tap;滚动消费后回位判据放宽(滚动位或页顶均算)+滚回顶。swipe 走 DeviceAdapter 中线坐标(避 4pt 边缘系统手势)。
- **dialog 边命名按因果不按"屏上有模态"**(2026-07-26 实测事故):原判据 `mt or changed` 两处松口——
  `changed` 单独成立就给一页命名(屏变了但根本没弹窗);`mt` 只证明**有**模态、不证明是**这次 tap 弹的**。
  实测鸿蒙独有的内容声明门(全屏 `Dialog [0,132][1272,2756]`)在 tap 前就盖着,点哪都落在它身上
  (同页两个不同控件算出同一个 tap 中心=点的本就是同一块遮罩),点完模态还在 → 声明门被存成
  `AppPermissionIntroDialog.jpeg` 并记 `captured`,页覆盖虚报 16/17。**同一条观察里 `outcome`
  已经写着 `overlay_or_state`(点到的是遮罩不是控件)——反证就在手边,判据没读它。**
  ⇒ 判据改成:必须有模态 **且**「tap 前无同类模态 或 点后签名变了」。
  **不要求哨兵命中**——变体页(`AppTipsDialog#via=*`)存在的意义就是两端文案不同,按文字验身份会误杀。
  拒采时写 `dialog_capture_refused` + `__dialog_capture_refused` 存证,`capture()` 返回值必须接。
- **顺路补采会抢先占位,把计划到达挡在门外**(2026-07-26 实测,同一个病的第三个变种):
  顺路补采是"站上了就采"的便宜货,但 `capture()` 见该页已 `captured` 就跳过 →
  **后来那次计划到达的干净图再也覆盖不进去**。实测 v9 的 HomeFragment:step10 在鸿蒙内容
  声明门(全屏 `Dialog`)盖着时被顺路采走,step15 `ARRIVED_strong` 时被跳过,于是
  **页级图永远是隔着遮罩那张,而逐元素证据(到达后采的)却是干净的** —— 同一页两套证据不同源,
  只看其中一套会得出相反结论。两处一起修才够:
  ① 屏上有**计划没声明**的模态时,顺路补采不许命名该页(记 `opportunistic_skipped`);
  ② `pages_status` 记 `provenance`(arrival/opportunistic),**计划到达有权改写顺路补采**。
- **`overlay_or_state` 是"没验到"不是"验过了"**(2026-07-26):tap 被遮罩吃掉,点到的不是那个控件。
  它此前不在 `lib_coverage.UNVERIFIED_OUTCOMES` 里 → 执行器如实记了遮挡、覆盖账却当有效观察,
  实测把 55/72 顶成了 59/72。凡"点了但没点着"的 outcome 一律留在分母里当欠账。

## 5.5 元素对齐与验证边界（规则）
- 鸿蒙侧 reconcile 用 `elem_signature`（标准化文本+rid+content_desc，**不含 type/bounds**）把 fact-tree 的 trigger spec 与 dump 抽出的元素**同签名对齐**，five_match 文本匹配只作兜底；`normalize_text_for_sig` 把动态文案归一。
- 边到达验证 = 哨兵命中 **且** page_signature 也变化才算到达（防"哨兵词点前屏上本就有"的假命中）；单 ability / degenerate pagePath 的 app **必需**落点身份识别（identify+签名注册表）+ 环检测，**不可退化成单 verify_text 判位**。
- **鸿蒙侧只验、不发现**：reconcile 严格只验树声明的 `functional_checks`，树没说的不测（树没说 = iOS没遍历过 = 无 oracle，鸿蒙扫到也判不了）。黑盒扫漏是**iOS侧建 ground truth**的机制，不在鸿蒙侧平移。

## 5.9 ★双侧审计结论 + 开跑 checklist(2026-07-23,两审计agent实测坐实)
**已修(本轮直接修掉,离线验过)**:①BLOCKER webview边压下沉栈(漏则H5卡死后续全废)②reconcile回位改NON_DESCENDING
(只page_change/overlay才BACK,toast/noop不BACK→防tab根BACK退app)③破坏性判据编译器+执行器都改**复用
blackbox_explore.DESTRUCTIVE_RE**(通用全词表,含退出登录/清缓存/退款/支付,全plan reconcile已验零危险词)
④input_field改rect(dict)优先(真机dump用rect,原只认attributes.bounds→创作主链断)⑤coldstart加preflight态校验
(state_signatures不命中→告警"未登录/态没就绪")⑥waited_s从run-2台账反哺(FileListPage 2.5→8.5s,异步边预算不误判)。

**开跑前必备 checklist(不备必返工)**:
1. **trip 首 batch 前由 dispatch 层建态一次**(dispatch 层建态,执行器零建态职责):`python3 run_scenario_with_verify.py login_harmonyos harmonyos --trip trip_2 --device-id <id> --package <bundle>`;验证步在 YAML 自身(切「我的」验 ID:)。exit 10→派 scenario-builder 自修/20→凭据找用户。后续 batch 不重跑。⚠️现 YAML 的 package/首启链是 630_tool 的,换靶 baseline_630 需先适配(从没在鸿蒙跑通,progress=0)。
2. **两轮基线dump齐**(--baseline-dir + --baseline-dir2);缺一轮→动态识别静默关→哨兵抖动。
3. 树 **waited_s 已反哺**(已做);异步门边在 annotations.edge_overrides 给 locate_budget_s。
4. annotations 补全:reconcile_exclude(带子tab的页)、input_edges(需输入的边)、state_signatures。
5. 设备**首启同意/隐私弹窗手动过掉**(执行器无排水drain_popups——HIGH-5未实装,换app/清数据必炸)。
6. 开跑后立即抽验:run.jsonl webview步后有无连片ABANDON(=webview栈没修干净);MineFragment reconcile后设备还在不在前台。

**剩余待修(按阻塞度;非本轮修)**:🟠webview landed_url未反哺→H5 URL对比缺oracle(采集侧补loadUrl);🟠收尾/resume/
阻塞传播(§5/§6/§8)未实装→出错带病硬跑不回补;🟡弱到达仍占正牌to命名(judge拿贴错标签基线);🟡is_walk模糊
子串可能漏测功能点(应改rid精确);🟡blackbox不按trip过滤(混入登出态元素噪声);🟢elem_signature因app无rid
基本空转(不有害,宣称的复用收益不存在,靠five_match兜底)。

## 5.95 ★冒烟实测发现(2026-07-22,Batch C+B 真机跑,见 aippt_vvCompare/spec/visual-verify/replay/SMOKE_REPORT.md)
切 3 段独立冷启 batch 跑了 C(推荐/作品 23步35s)+B(我的/会员 98步48s)。**架构骨架(切段/安全剪枝/弹窗/webview/tab导航)验证有效**;
blocker 全在前置态+上游数据+编译器健壮性,非骨架:
- ✅已修(2026-07-22)**T1[执行器·preflight] 登录检测查错页→根治=执行器删建态职责**:错不在查哪页,在**层**——
  建态+验证归 dispatch 层(next_batch 算 first_batch_in_trip→trip 首 batch 跑一次 scenario_chain;**验证步在 login YAML 自身**,
  login_harmonyos.yaml 结尾本就切「我的」tab 验 ui_gone:点击登录 + ID:)。执行器零建态职责:不查态不登录不硬停;
  态中途丢→到达门控+级联升级接住,按门禁铁律交 judge 判 P0(不归因环境)。preflight 自动登录块已整段删除。
- 🔴**T2[环境] 设备实为登出**(点击登录/剩余体验次数:0次,零 ID:/VIP;VIP有效期到7-31却登出=session没跨重启存活)→
  会员区 expect 全用登录真值→step43 我的tab WRONG_LANDING→9页 blocked。**印证"登录是被测前置不能假设已登好"**;需先把 login_harmonyos 在鸿蒙跑通(progress=0)。
- 🟠**T3[编译器] trigger_label_unknown 照 emit 空primary tap**(compile L192 fallback ""):C 的 3 条无trigger边→tried:[]→ABANDON+拖垮reconcile。
  修:见 trigger_label_unknown 且 prim=="" 且 rid空→emit skip(no_trigger_captured)(L85兄弟函数已跳,主emit循环漏)。
- 🟠**T4[上游·iOS侧] 3边 trigger_label_unknown**(Recommend→List/→Search、Works→Preview):iOS遍历没采到触发控件label(疑无文本图标入口)→鸿蒙无oracle。
- 🟡**T5[annotations] 引擎门边budget不足**:打开作品→PPTFile撞「PPT引擎启动中」(~15s)>默认4s→ABANDON;edge_overrides补 locate_budget_s。
- ✅**正向**:安全11条SKIP_DESTRUCTIVE_PRUNED(编译期静态剪,登出态识别乱套也零接触危险边)/tab导航稳/弹窗20条移reconcile/webview闭环/冷启15-18s非hang(受控复现推翻初判)。

## 5.97 precond(前置数据态)哲学:顺序对齐,绝不鸿蒙侧自建(2026-07-24,用户问"iOS侧有做接线吗"后定)
iOS侧**没有**功能点级自动建态机制——数据态靠**遍历顺序副产品**(创作流先生成PPT→作品区自然有数据)+grounding诚实记账(precondition字段,具体到源码行号)。鸿蒙侧同构:
- **态对齐=按 walk 顺序跑**(batch_4 的"列表非空"依赖 batch_1 副产品;单跑后区段撞 precond_unmet→先按序跑上游段);
- 编译器透传 `precond/precondition` → 执行器全页不见时定性 **precond_unmet**(非缺陷疑点)→ manifest.need_scenarios 结构化报缺(scenario-builder 可消费);
- **绝不自动建iOS没建过的态**(无 oracle 测了也判不了);涉支付/订阅/注销的态=可弃账号隔离 trip,红线。

## 6. 复用点名(禁重实现,审核铁律)
DeviceAdapter(设备层+page_signature) / extract_clickables_hmos / five_match(五级匹配,降级命中=text_mismatch P1) /
evidence_pack —— 均 import 现行实现。判定段复用 role=judge。建态委托 run_scenario_with_verify.py。

关联:phase4-replay-compile.md(编译设计) / phase4-replay-executor.md(执行设计) / node_sweep.py(四规则+同构去重源) /
memory [[vv-hmos-replay-landing]] [[design-precedent-protocol]]
