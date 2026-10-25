# Phase 4 回放 — 判定 + 修复接线(编译/执行之后的下半程)

> 补齐 [`phase4-replay-run.md`](phase4-replay-run.md) 只讲的"前两段(编译+执行)"。回放产的 `capture_manifest.json`
> 与页粒度 batch sub-agent 的 role=capture 契约**同构**,所以判定/修复**复用页粒度主线(Phase 5/6 + visual-fixer +
> Phase 6.5 round_budget 自持闭环),不另造**。本文只给"回放采集 → 那套下半程"的接线步骤。主会话**永远不 Read 截图**(§0.4)。

链路全貌:`compile_replay_plan → slice_batches(可选) → replay_exec` **(前两段,见 run.md)** → **本文 J1–J5**。

## J0 ★产物落位(机械,**先落位再组装**——2026-07-25 新增)
> `$SCRIPTS` = `$SKILLS_ROOT/arkts-visual-verify/scripts`（同 run.md）。
回放产物住在 `replay/<run>/` 是**工作区**,不是交付位。先摆进 canonical 布局,下游(judge/visual-fixer/
Phase 6 自检/外部调用方)才认得。**跳过这步 = 整条下游拿不到图,只能各自绕路**(实测:judge 曾在单里
把 evidence 路径改指回放目录绕过去,缺陷因此静默存活一整轮)。
```text
python3 $SCRIPTS/replay_place_artifacts.py --capture-dir <replay 输出目录> \
    --round N --trip <trip_id> --project-root <项目根> \
    --ios-baseline-dir spec/visual-verify/screenshots/ios/<trip_id>
```
产 `screenshots/harmony/round-N/{trip}/{page}.{jpeg,hmos.json}` + `_evidence/`(过程证据) + `_placement.json`(含覆盖对账)。

## J1 组装判定输入(机械,零判定)
```text
python3 $SCRIPTS/build_judge_input.py --root <项目根> --capture-dir <replay 输出目录> \
    --ios-baseline-dir <iOS基线 shots> --tree <fact-tree.json> --round N --trip <trip_id>
```
⚠️ `--trip` **必填**(2026-07-25 改):它参与 canonical sbs 路径构造,默认值会让整轮拼图静默落进错误 trip 目录。
对 capture_manifest 里 captured 的每页:拼 sbs(iOS左|鸿蒙右,落
`screenshots/sbs/round-N/{trip}/`)+ 装 functional_checks(带 grounded
`expected_ios`)+ behavior_observations + 上一轮同页单,产 `<capture-dir>/judge_input_roundN.json` + 建 `round-N/{ui,feat}`。

## J1.5 ★产物闸(不过不许进判定)
```text
python3 $SCRIPTS/assert_replay_artifacts.py <项目根> N <trip_id> <capture 目录> <replay_plan.json>
```
⚠️ 第 5 参 `<replay_plan.json>` **必给**(2026-07-25 复审 B-1/B-2):闸此前**从不读计划**,
断言的量全取自 manifest/_placement —— 全是**被审对象自己产的东西**。实测 0 张鸿蒙截图 +
一份手写 aliases 的 `_placement.json` 就能全绿。计划是编译期从iOS真值算出的**独立信源**。

八条断言:
| cond | 断言 | 红了怎么办 |
|---|---|---|
| 0 | 新鲜度:`_placement.placed_at ≥ manifest.started_at`(防陈货顶包) | 重跑落位 |
| 1 | canonical 交付集 ≡ iOS baseline png 全集(0字节不算交付;别名须在计划的 `same_screen_aliases` 里且宿主图真在) | 逐页归因/补采 |
| 1b | 收尾趟欠账(`#via=` 确认窗页) | 跑 §4.1.5 收尾趟五步 |
| 2 | 每张图配对 `.hmos.json` 且是**合法 JSON** | 重跑(dump 写失败) |
| 3 | sbs 齐套(分母=靶单 ∩ 交付集,不是全交付集——无iOS GT 的页拼不出 sbs) | 重跑 J1 |
| 4 | 功能点行为覆盖:分母取**计划的** `functional_denominator` − 编译期有据延后 | 补跑/逐条说明 |
| 5 | reconcile 无未结清页 | 补跑欠账页 |
| 6/7 | 执行器自报无截图/dump 缺口;本轮真采过东西 | 查设备/重跑 |

**红了就是漏测,不许当"通过"往下走**——没有这道闸,43% 的行为覆盖会以"全绿"面目混过整轮(实测)。
**但假红同样危险(它教人绕闸)**:所以 1b 有诚实失败出口、3 的分母收窄、0 的时间戳格式不合即拒判而非误判。
⚠️ 分段跑 / 收尾趟一律先 `merge_capture_dirs.py --plan <完整计划>` 合并再落位过闸,**不对单趟目录过闸**(见 run.md §4.1.5)。
- **分段跑过(slice_batches)** = 多个 out 目录、各自 manifest → 每个 out 目录跑一次 J1,或先并 manifest 再跑。
- `is_webview` 以 dump 无 `Web` 节点为准(命名兜底)。

## J1.5 级联升级项:页粒度兜底 + 导航问题 vs 真bug 判读
执行器机械导航撞异常(WRONG_LANDING / NO_NAV / nav 边 ABANDON)时不硬走:**记升级包 + phantom 跳掉"没进去的子树"(防级联,绝不发新tap=安全),到 verify/coldstart 锚点再对齐**。产 `capture_manifest.escalations[]`(status=escalated 的节点)。处理两步:
1. **页粒度兜底(恢复 + 机械判别器)**:升级节点交**既有页粒度主线**(walk_to 从根重导航该页 + 截图)——鸿蒙侧本就保留页粒度路径当兜底(边链路未全量测,不能只靠一笔画)。冷启重导航的结果**本身就是"导航问题 vs 真bug"的机械判据**:
   - 重导航**到达** → 一笔画那次是位置/异步故障,**已恢复**,该页转 captured(`via:pagegranular_fallback`);
   - 重导航**也到不了** → 该边/页**真异常**(真bug 候选),留证据交离线 judge 定。
   build_judge_input 已把 `pagegranular_reached` 回填进 `escalations[]`。
2. **残余含糊交 LLM**(judge 段):兜底后仍说不清的(到了但内容诡异/重定向像bug),judge 从证据判。**安全**:兜底只重放 plan 步(编译期已破坏性剪枝),不即兴导航,共享账号零新增风险。

## J1.8 ★判定并行:按 batch 分派 judge(判定段提速 3-4x,零竞态)
判定全程零设备、零共享写(各 judge 写各自页的单),**天然可并行**——与被否的"采集∥判定"无关(那个是采集单进程占设备拆不开)。串行判 10 页 ~50 分钟 → 按 batch 并派 ~15 分钟。
```
主会话:
① 各 batch 出目录各组一个判定包(build_judge_input 吃单 capture-dir),
   跨 batch 共有页(冷启落地 HomeActivity 等)用 --skip-pages 只留一个 batch 判,去重防重复单;
② 4 个 judge sub-agent 并发派(一 batch 一个,contract 同 J2);
③ 收齐 → 主会话跨 batch systemic 聚类 + _summary/_delta(J3),judge 从不跨 batch。
```
去重规则:先扫各 batch 判定包的 captured 页,重复页保留在"最该判它的 batch"(该页首次 captured 的 batch,或功能点最多的),其余 batch 组包时 `--skip-pages` 排除。

## J2 派 judge sub-agent(role=judge,独立上下文读图)
派发通用 Codex 子代理（`agent_type="default"`），传入 `judge_input_roundN.json`，并要求它**先读 `fix-file-schema.md`(唯一 schema)+ `phase2-classify-write.md`
(ui 分类) + `sub-agent-batch-prompt.md` §B.4.5(feat 双 oracle)**,然后**逐页**(这就是页粒度模式的出单时机):
1. **UI**:读该页 `sbs` 多模态 diff → 一差异一文件 `round-N/ui/ALIGN_P<page>_<kind>_<slug>.md`;§3 原样贴 description+root_cause_hint;分类默认 bug。
2. **feat 双 oracle**:每个 functional_check 用 `expected_ios`(ios_trusted)否则 `expected_llm` 作真值,**从 hmos 截图+dump 复核**。
   ⚠️**绝不盲信 `behavior_observations.outcome=="not_found"`**——机械 reconcile 把展示型功能点当可点找会误报;从证据判在不在,真缺失才出 `feat/*.md`(kind=IMPL_MISSING)。
3. **webview 页**:只做原生外壳 diff + 注明有无 landed-URL oracle(无则不臆造 URL 差异);不逐元素 diff 网页内容。
4. **carry-forward**:prev_round_tickets 每条若 disposition 已设 → 带进 round-N 同 id 单。
5. `inject_factree_refs.py <page_id> <trip>` 取 §1/§7;报错则用 baseline_md + ios_anchor.decl_file 填 §4,真不知写 "unknown"。
5.5 **★长链路断点定位(用户核心需求:只说结果影响修复效率)**:判定包每页/每升级项带 `trace`(该batch关键步序:step/边/verdict/t_wait/retap/reenter)。链路型 feat 单(创作流等)正文**必含「断点定位」**:走到第几步、断点边与verdict、等待时长、断点现场证据、上游各步状态——修复者直接跳到断点,禁止只写"生成失败"。walk继承类 check 用 `walk_evidence`(挂接的walk步verdict)作证据。
5.7 **★破坏性功能点判读(安全跳过≠通过,用户抓的真漏洞)**:观察 outcome 为 `skipped_destructive_unverified` 或带 `capture_status=pruned_unverified` 的 check——**绝不算 PASS**,必须出「未验证/需人工或隔离trip」报缺单(iOS侧 evidence=None=进页即真操作,鸿蒙也不能碰)。`safe_dialog_probe` 类(iOS「到弹窗即止」对齐)有 `dialog_evidence` 弹窗截图+`dialog_texts`:judge 比对弹窗标题/正文/按钮与 expected_ios,「确定后行为」两端都未验证=正常报缺不算缺陷。**铁律:确定/确认/是 键两端永不点。**
6. **升级项 adjudication ★判据 = 「按iOS的边能不能走通」,不是「最终到没到」**(2026-07-25 用户拍板修订):

   旧判据 `pagegranular_reached=true → 已恢复,不出单` **在一笔画回放语境下是反的**。一笔画回放的
   全部意义就是**照iOS的走法再走一遍**;「按计划边点过去到不了、要人工绕路才到」**本身就是接线错误**,
   正是迁移要验的东西。用"后来到了"把它判成 recovered = 把接线 bug 当成功吞掉。
   （旧判据只在**页粒度兜底**语境成立:那里脚本导航失败常是脚本尺子不准,LLM 接管走到=路本来就通。）

   ```
   按计划边直接到达                      → 不出单
   按计划边到不了（任何原因）             → 先看三分归因，再决定出不出**产品单**
      ├ LLM/页粒度绕路后到了 → 仍出单，标 recovered_by_detour（路存在但接线错，P1）
      └ 绕路也到不了         → 升级 page_missing_hmos（P0）
   ```

   **★三分归因（2026-07-25 用户拍板）——「没采到」必须分清是谁的错**，执行器已机械判好
   （`escalations[].blame`，判据 = verdict + **失败现场 dump** 里控件在不在）：

   | blame | 现场证据 | 判定 | 出单 |
   |---|---|---|---|
   | `handler_not_implemented` | 控件已渲染、tap 成功，但屏无变化 | **onClick 空实现** | ✅ `IMPL_MISSING` P0 |
   | `control_missing_in_hmos` | **第一层双端 dump 对账**认定iOS有该文本、鸿蒙没有 | **鸿蒙未实装该控件** | ✅ `IMPL_MISSING` P0 |
   | `routing_target_wrong` | 点后落到非预期页 | **路由目标错** | ✅ `nav_chain_broken_hmos` |
   | `locator_failed` | **控件就在 dump 里**，只是没命中 | **我们的定位逻辑问题** | ❌ **绝不出产品单**，记工具缺陷 |
   | `existence_undecidable_no_text_anchor` | 该 check 的iOS锚点**无任何文本**（纯图标 / rid=None） | **判不了**——双端文本对账对它不可见 | ❌ **绝不出产品单**，记工具缺口（需结构定位） |

   > **★`control_missing_in_hmos` 的裁决权已收归第一层（2026-07-28 用户提出并拍板）**。
   > 此前它由**第二层**（reconcile 点击）盖章：点不着 → 盖 P0。而点不着的主因是**我们拿错了名字**——
   > `functional_checks[].name` 是人写的功能描述（「客服中心」「检查更新」「版本号」），
   > 屏上的字是『联系我们』『版本更新』『V1.0.6』。**实测 trip_2 的 18 条 `control_missing_in_hmos`，
   > 接上第一层后只剩 1 条**（8 条改判 `locator_failed`、13 条改判 `existence_undecidable`），
   > 而剩的那 1 条还是动态推荐文案误判。
   >
   > **分层铁律**：
   > | 层 | 判什么 | 靠什么 | 抓得到 / 抓不到 |
   > |---|---|---|---|
   > | 第一层 `dump_reconciliation` | 控件在不在、文案对不对 | 双端 dump 文本集对差，**零定位零点击** | 抓不到空实现 |
   > | 第二层 reconcile 点击 | 点了有没有反应、跳对页没 | 定位 + tap | 唯一能抓 `handler_not_implemented` |
   >
   > **第二层不再有权回答第一层的问题**：定位失败一律 `locator_failed`。
   > 两层缺一不可——只有第一层会漏掉空实现（实测 `MineTab.ets:564` 的 `onCustomerServiceClick()`）；
   > 只有第二层会把定位缺陷冤枉成产品缺陷。
   >
   > **`existence_undecidable` 不是"没事"，是"欠一件工具"**：13 条全是纯图标元素，
   > 文本这条路结构上救不了，得补结构定位。judge 不出产品单，但**必须在 `_summary` 记为覆盖欠账**，
   > 否则"判不了"会伪装成"没问题"。

   **★第一层的页级结论 `dump_reconciliation.verdict`（judge 逐页先读它再判元素）**：

   | verdict | 含义 | judge 怎么做 |
   |---|---|---|
   | `elements_all_present` | iOS有的文本鸿蒙**全都有** | 本页任何 `control_missing_in_hmos` 归因**一律不成立** |
   | `elements_missing` | 确有iOS有、鸿蒙没有的文本 | 出单前复核三种非缺陷成因：①需滚动才可见 ②服务端驱动内容差异（分类/推荐列表）③H5 正文（鸿蒙 WebView 内容不进 dump） |
   | `hmos_page_blank` | 鸿蒙 app 文本=0 且渲染轮询超时 | **整页空白是单一根因**：出 1 张「页面空白」单，**绝不逐条出 N 张缺页单**（血泪：1 个根因曾报成 11 张） |
   | `hmos_render_unsettled` | dump 采于渲染未稳定时 | missing 列表**证据可疑，不得据此判缺失**，须重采 |
   | `available:false` | 任一端 dump 缺失 | **无证据 ≠ 反证**，不得推断鸿蒙没实装；退回多模态 sbs |

   **★假 P0 的两条主要来源（2026-07-25 实测：执行器判 4 条 P0，复核只 1 条成立）**——
   `NO_NAV` 与 `WRONG_LANDING` 是仅有的**不经位置闸直接判产品缺陷**的路径，必须自带排除项：

   | verdict | 判产品缺陷前必须排除 | 排除后的 blame |
   |---|---|---|
   | `NO_NAV` | ①屏上有模态遮罩(tap 被吃) ②输入边的文本没真落进输入框 ③当前已在目标页(再点同一 tab 本就 noop) ④**双图硬闸（见下）** | `blocked_by_modal` / `input_not_applied` / `noop_already_there` / `content_changed_text_filtered`（**均非缺陷**） |
   | `WRONG_LANDING` | ①落点是登录门(登出趟被拦是**正确行为**) ②该边树载 `runtime.device_state` 只在别趟确认过 | `blocked_by_login_gate` / `edge_confirmed_only_in_other_trip`（**均非缺陷**） |

   **★排除项④·双图硬闸（2026-08-14 假 NO_NAV 事故修——两轮 judge 只看单张 no_nav 图、采信"屏幕
   没变"，实际页面已推进两页）**：落 `handler_not_implemented` 前必须并排 view「源页交付图」与
   「`{to}__no_nav.jpeg`」两张截图。图上**任何 app 内容区差异**（文案/图片/滑块/进度，不含状态栏
   时间电量）→ 不得判 handler 未实装，改判 `nav_advanced_but_text_blind`（工具侧签名盲区），
   转位置重建。两图 app 区确认等同 → 才许落 handler_not_implemented。注意前图时差：tap 时刻的
   pre 截图不存在（实现只存 post 截图+pre dump），"前图"=源页到达时的交付图，可能有滚动/态漂移
   ——无法确认时标 `needs_human`，**绝不缺省判缺陷**。执行器带 `numeric_delta` 字段的升级包
   （blame=`content_changed_text_filtered`）已在机械层排除，judge 复核双图即可，不必重判。

   judge 看到这些 blame 一律**不出产品单**；看到 `exclusions_checked` 字段才说明排除项真跑过。

   最隐蔽的是 `handler_not_implemented`：控件画出来了、也点得到，UI 截图看起来一模一样，
   **只有点了没反应才暴露**（本轮实测 `MineTab.ets:564` 的 `onCustomerServiceClick()` 就是空实现）。
   纯 UI 对比永远抓不到它——这正是行为对账（reconcile / 一笔画）存在的意义。
   反过来 `locator_failed` 若误判成产品缺陷，就是**拿我们的 bug 去冤枉被测物**，同样严重。

   合法态差异（前置未满足/非 VIP/一次性资源已消费）仍记 `blocked_precond` 不出单——
   但**必须有证据**（precond_unmet / one_shot_consumed 标记），不能因为"后来到了"就免判。
   escalation 的 verdict 直接映射 kind：`trigger_missing`→缺元素或接线错(最常见)、
   `WRONG_LANDING`→路由目标错、`NO_NAV`→点击无响应。含糊则标 needs_human。
**铁律**:严格照 schema;一差异一文件;**绝不改 .ets**;零真差异+零 feat 失败的页不出单。返回紧凑 JSON(每页 ui/feat 单名 + status + totals + escalations_adjudicated)。

## J3 主会话收尾(不读图)
核盘 round-N/{ui,feat} 文件存在 + schema(段数/frontmatter)→ 跨页 **systemic 聚类**(同根差异回填 `systemic_root`,见 Phase 5)→
写 `_index.md`/`_summary.md`/`_delta.md`(vs 上一轮)。

## J4 接修复(复用主线 Phase 6,零改)
按 SKILL.md **Phase 6**:主会话调用 `spawn_agent`（`agent_type="visual-fixer"`）处理 `round-N/{ui,feat}/*.md` 并改 .ets（按 `fixer_layer` 分 ui/feat/resource）；
fixer FINAL_ANSWER 返回后，**主会话接着调用** `spawn_agent`（`agent_type="visual-fixer-reviewer"`）反摸鱼质检（Step 6.7，带硬闸；
2026-08-04 前写的是 fixer 自派,但 fixer 无 子代理派发、结构上派不出)。**回放侧不动这段,直接复用。**

## J5 回归 + 轮次(闭环)
- **轮次**:`_state.yaml.current_round` 由**本 skill 自持**(`scripts/round_budget.py`,Phase 6.5 按退出码路由);任何调用方(含 a2h-verify)只读不写。
- **回归重跑 = 再走一遍链**:visual-fixer 改完 → `replay_exec`(必要时 `slice_batches` 单区域)重采 → J1→J3 出 round-(N+1) → carry-forward disposition 判"修好没"。**这就是回放侧的收敛闭环**(等价页粒度的重截图,但机械回放更省)。

## 接线前必检(踩过的坑)
1. **采集态必须对齐基线 trip**:登出态采图对登录态基线 = 伪差异(实测教训)。judge_input 的 trip 要与 `--ios-baseline-dir` 同态。
2. **behavior_observations 假 not_found**:见 J2-2,判定从证据出,别当缺陷。
3. **覆盖前提**:回放只走iOS walk_plan 已发现的边;树没说的无 oracle 不判(非缺漏,是设计)。创作流/非VIP/登出 trip 需各自 trip 的 walk_plan + 采集。

关联:[[phase4-replay-run]](compile+execute) · `sub-agent-batch-prompt.md`(role=judge/B.4.5) · `fix-file-schema.md` · SKILL.md Phase 5/6
