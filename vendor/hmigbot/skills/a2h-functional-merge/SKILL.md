---
name: a2h-functional-merge
description: 在 app-relationship-tree 跑完之后运行,把 A2H 安卓测试工具 Stage1 的三样独特产物——功能点枚举(尤其 enum 驱动的动态工具)、预期结果(可视觉验证的判据)、功能点→安卓源码锚点——注入 fact-tree(spec/toolkit-fact-tree.json),让下游 arkts-visual-verify 能在单趟页面遍历里顺手做功能检查、产 feat 问题单。当用户说"把 A2H 的功能点/预期合进 fact-tree""让 visual-verify 能测功能不只是 UI""注入功能检查""A2H 产物融合 fact-tree""functional-merge""把功能清单挂到页面上"时触发。即使用户只说"把 A2H 的功能点接进来"或"让 fact-tree 带上功能维度",只要上下文是 A2H↔visual-verify 融合,也应触发。**只消费 A2H Stage1(functional_registry + test_intents),绝不跑 A2H 的执行阶段;只新增字段,绝不改 toolkit/art 已填的导航与结构。**
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

# a2h-functional-merge — 把 A2H 功能维度注入 fact-tree

## 1. 定位

`toolkit-fact-indexer`(结构)+ `app-relationship-tree`(导航/语义)把 fact-tree 补成了一张**页面+导航**地图。但它**缺功能维度**——visual-verify 拿它只能做 UI 对比,不知道"这页该测哪些功能、什么算对"。

**谁触发本 skill(接线,v6.7)**:除用户显式调用外,**`android-fact-tree` 出口契约 §3.5 会自动接续本 skill**——它产完树跑过 gate 后,检测到 A2H Stage1 产物(`functional_registry.json`)存在就自动调本 skill 注入功能维度。所以 A2H 项目走 `android-fact-tree → (自动)本 skill → visual-verify` 全自动,无需人工记得手动跑;纯 UI 项目无 registry,android-fact-tree 不接续,本 skill 不跑。

本 skill 补这块,且**只从 A2H Stage1 拿三样 fact-tree 自己产不出的东西**:

| A2H 独特产物 | 来源文件·字段 | fact-tree 为何缺 |
|---|---|---|
| ① **功能点枚举** | `functional_registry.json` · `name` | 41 个 enum 驱动工具(AI抠图/换发型…)运行时拼出,不在任何 layout,fact-tree 无 record |
| ② **预期结果(判据)** | `test_intents.json` · `steps` 切出"预期" | fact-tree 只有 `purpose`(描述),没有"什么算对"的 oracle |
| ③ **功能点→源码锚点** | `functional_registry.json` · `source_file`/`raw_identifier` | fact-tree 页面级文件路径稀疏、enum 工具无位置 |

**为什么独立成 skill(不并进 app-relationship-tree)**:art 的契约是"只读安卓源码即可补全",自给自足、不依赖任何流水线。本 skill 的契约是"消费 A2H 流水线产物"。**把对 A2H 的依赖隔离在这一个 skill 里**,art 保持独立(A2H 怎么更新都不碰 art)。

```
toolkit-fact-indexer → app-relationship-tree → 【本 skill】 → arkts-visual-verify
   (结构骨架)          (导航/purpose/孤儿)      (注入功能维度)    (单趟:UI + 功能)
                                                    ↑
                                          A2H Stage1(只跑源码分析)
```

## 2. 输入 / 输出

| | 路径 | 说明 |
|---|---|---|
| 输入1 | `spec/toolkit-fact-tree.json` | **art 跑完的版本**(已有 navigation/reach_path/purpose) |
| 输入2 | **`spec/a2h/functional_registry.json`**(契约路径) | 功能点 + source_file + raw_identifier + feature_path。**只从此契约路径读**——上游须把 A2H Stage1 产物拷到这里;不再"任意位置"搜(workspace 多份 registry 会摸错弱版/过期版) |
| 输入3 | **`spec/a2h/test_intents.json`**(契约路径) | 4 组意图,`steps` 内嵌"预期结果" |
| 输出 | **原地改写** `toolkit-fact-tree.json` | 给 page record 加 `functional_checks[]`;顶层加 `unmapped_functional_points[]`;`stats.a2h_functional_merge` 记账 |

**不消费**:A2H 的 `summary_results.json`(Stage4 意图改写)、`android_execution/`(Stage3)、`harmony_execution/`(Stage5)。这些要么无意义(步骤改写,安卓↔鸿蒙导航本就相同),要么是执行结果(执行交给 visual-verify)。

**镜像功能点默认跳过(2026-06)**:`merge_functional_into_facttree.py` 默认**跳过 `is_mirror=true` 的条目**(A2H 跨引用副本,同一 `raw_identifier`、在主页面已有 check)。理由:镜像是"同一功能的第二个入口",重挂 = 冗余重测 + 2 倍成本,且位置错(功能不在枢纽页屏上,要测得先导航走、那一刻与主页面 check 重合);**入口可达性由 visual-verify 图遍历(点首页区块那条边)覆盖,不需复制叶子 check**。实测 AntennaPod:挂上 1188(含镜像)→ 604(唯一真功能),省 695 冗余。确需在每个入口逐控件重测可加 `--keep-mirrors`。`stats.a2h_functional_merge.mirror_skipped` 记账。

## 3. 注入的 schema(只增不改)

挂到 page record 顶层:

```jsonc
"functional_checks": [{
  "fp_id": "FP_售后中心",
  "name": "售后中心",
  "feature_path": "我的>设置>售后中心",          // join 溯源
  // —— 双 oracle:LLM 种子(保底) + 安卓实测(主) ——
  "expected_llm": "跳转至售后中心页面",            // ← test_intents 切出(LLM静态分析种子);A 不可信时保底
  "expected_llm_missing": false,                  // 没 join 到则 true
  "expected_android": null,                       // ← grounding 安卓实测填(主 oracle);未跑为 null
  "android_trusted": null,                        // ← grounding 用独立结构指纹判 A 落点是否可信(true/false);未跑 null
  "android_anchor": {
     "decl_file": "app/.../activity_mine_setting.xml",  // ← functional_registry.source_file (声明处)
     "impl_file": null,                          // ← Phase 3 枚举精修补的入口宿主页(非枚举为 null)
     "raw_identifier": "..."                      // ← 精确符号锚 / type 判别
  },
  "type_discriminator": null,    // 通用宿主页(如 HSVFXPreviewActivity 承载 7 工具)时填枚举值
  "confidence": "high",          // 映射置信(high/medium/low)
  "mapping_method": "layout字段",
  "source": "a2h_functional_merge",
  // —— Q2 透传(源码侧额外信息,供 visual-verify 修复流程用;上游缺则为 null,向后兼容) ——
  "source_section": "context_menu",        // ← registry.source_section 控件类型 → fixer 选修复模式(grounding 选 tap/longtap/drag)
  "precondition_required": "队列非空且未锁定", // ← intents.precondition(源码推导前置态)→ grounding step0 据此造态 + 种子 precondition
  "expected_source": "spec_acceptance"     // ← intents.expected_source 判据溯源 → trust 信号(spec_acceptance>spec_nav>inferred)
}]
```
> **Q2 透传三字段(2026-06 增)**:`source_section` / `precondition_required` / `expected_source` 由 merge 从 registry+intents 直接搬运到每条 check。消费侧:grounding phase0.5 step0 读 `precondition_required` 造态、step1 据 `source_section` 选交互方式;visual-fixer 读 `source_section`(修复模式)+ `expected_source`(可信度)。上游 registry/intents 无这些字段时填 `null`,不影响 A2H 老产物。

挂不上页面的(参数原子如"比例2:3"、fact-tree 无对应 record):进顶层 `unmapped_functional_points[]`,带 `unmapped_reason`,**绝不静默丢弃**。

## 4. 执行流程(确定性优先 + LLM 只兜枚举)

> ⚠️ **下面 Phase 0-6 是 XML/View 架构专用**（`map_registry_to_facttree.py` 靠 R.menu/R.xml grep + resource-id 模糊 join）。**纯 Compose 走旁路** `scripts/compose_merge_into_facttree.py`：读 `compose_host_map.json`（由 `a2h-functional-registry` 的 `compose_registry_from_tree.py` 产）做**精确映射**，无 grep、无模糊 join；注入 check 带 `tap_by=text`/`tap_text`/`code_anchor` 供 visual-verify 按文案点。由 android-fact-tree §3.5 按架构调，混合架构两条都跑（按 fp_id 去重叠加）。

### Phase 0 — 前置探测
- `spec/toolkit-fact-tree.json` 存在,且 **art 已跑过**(抽查 reach_path 不是几乎全孤儿;若是,先回去跑 `$app-relationship-tree`)。
- **契约路径** `spec/a2h/functional_registry.json` + `spec/a2h/test_intents.json` 存在。**只认这两条契约路径**——不在别处搜 registry(workspace 可能有多份新旧/强弱 registry,搜到弱版/过期版会系统性吃错;固定契约路径后,放哪份是上游的显式责任)。缺则不是本 skill 兜底找,而是回上游"把 Stage1 产物拷到 `spec/a2h/`"。

### Phase 1+2+4+5+6 — 确定性主链(一个脚本跑完)
先产/复用功能点→页面映射,再合并注入(`--registry`/`--intents` 写死契约路径,不用占位符/脚本默认):

```bash
# (a) 功能点 → fact-tree page 的确定性映射(三路:类名直命中/layout文件名/枚举分发/kt文件名)
python3 $SKILLS_ROOT/a2h-functional-merge/scripts/map_registry_to_facttree.py \
    --registry spec/a2h/functional_registry.json \
    --facttree spec/toolkit-fact-tree.json \
    --src-root <ANDROID_SRC> \
    --out      registry_facttree_map.json

# (b) join 预期 + 注入 fact-tree + 自检
python3 $SKILLS_ROOT/a2h-functional-merge/scripts/merge_functional_into_facttree.py \
    --facttree spec/toolkit-fact-tree.json \
    --registry spec/a2h/functional_registry.json \
    --intents  spec/a2h/test_intents.json \
    --map      registry_facttree_map.json
```

脚本内部:
- **Phase 1** 按 `feature_path` join functional_registry ↔ test_intents(归一化 `>` 分隔+去空格,叶名兜底)。
- **Phase 2** 用 (a) 的映射把功能点落到 page(确定性覆盖 ~82%)。
- **Phase 4** 从 `steps` 切"预期结果"当 oracle;切不到标 `expected_missing`。
- **Phase 5** mapped 挂 page.functional_checks;unmapped 进顶层数组。
- **Phase 6** 自检:不丢功能点、android_anchor 非空、计数一致;失败即退出。

### Phase 3 — 枚举入口精修(LLM,只补 low 置信枚举)
确定性映射对 41 个 enum 工具只能给 low 置信(分发在 `when(type){...}` 中枢,grep 取众数有噪声)。**只对这批派 sub-agent 精修**(不是全量 LLM,避免厚重):

派一个 sub-agent,prompt 要点(详见 [`references/enum-refine-prompt.md`](references/enum-refine-prompt.md)):
- 输入:low 置信枚举功能点(name + raw_identifier 枚举值)+ fact-tree record id 清单 + 安卓源码根。
- 方法:grep 枚举值定位分发中枢的 `when(type)` 分支 → 顺分支体追到真正 `startActivity(Xxx)` 的**入口宿主页**(常是通用承载页 HSVFXPreviewActivity / PictureVideoActivity,用 type 区分);区分"入口页"vs"结果/详情/预览/成功页/弹窗"(后者是噪声)。
- 输出:`{raw_identifier: {mapped_record, impl_file, confidence:"high", evidence}}` 写到 `enum_refine_overrides.json`。

然后用 `--enum-refine enum_refine_overrides.json` 重跑上面的 (b),把精修结果覆盖进 functional_checks(host 升 high、补 impl_file)。

> 为什么 LLM 只碰这批:enum 工具是 fact-tree 与 registry 唯一**本体粒度错位**的地方(运行时 enum vs 静态页面),只有它需要语义读源码;其余 toggle/dialog/navigation 确定性映射已 100%。

### Phase 5b — behavior_chains 静态互验(确定性, warn-only, 2026-07 增)

新版 harmony-migration-toolkit 产 `intermediate/0_android_facts/behavior_chains.json`(AST 事件链)时,
与 registry 做三桶互验——两条**独立推导链**(census+LLM 读源码 vs AST 事件链)互相挑错。
AIPPT 实测战果:暴露 census 的 platform-res 目录级盲区(+127 控件)、救回 2 条 LLM 漏项
(模板搜索入口)、28 条功能点升"静态确认"级置信。

```bash
python3 .../scripts/reconcile_behavior_chains.py \
  --registry <spec/a2h/functional_registry.json> \
  --chains   <toolkit_out>/intermediate/0_android_facts/behavior_chains.json \
  --out      <spec/a2h/_work/chains_reconcile_report.json> \
  [--apply-facttree <spec/toolkit-fact-tree.json>]   # Phase 5 注入完成后再跑,给 checks 加 verification
```

四桶语义(报告 `stats` + 明细):
- `confirmed_by_static` — 元素+事件对上、效果不矛盾 → 下游 visual-verify 可自动判
- `conflict` — 元素对上但链侧 effect 与 expected 矛盾 → **必须人/LLM 看**
- `chain_only_candidate` — 链有 registry 无 → 候选漏项,**LLM 回源码裁决**(真漏→改 functional_points 走 registry 的 S4 重投影;噪声/锚点差异→记录后忽略)
- `chain_noise` — 动画/基础设施监听,词表机械滤除,不参与对账

铁律:**warn-only 永不阻塞**(chains 缺失时跳过,非致命);脚本**只产报告 + 只增 `verification` 字段**,
绝不自动增删功能点(实测 chain_only 里 60%+ 是噪声/锚点口径差,自动回写会灌脏);裁决者=运行 skill 的
LLM,以源码为真值。expected 判据从同目录 test_intents.json 的 steps 切"预期结果:"获得(registry 按契约不带)。

### Phase 7 — 枚举同构收敛(确定性,注入后必跑,2026-07-10 增)

registry 的 `enum_options` 提取对同一交互机制的每个枚举值各产一条功能点(判据模板同型,只有枚举值不同——
源码里是同一条 `it.style==选中值` 代码路径)。逐条测 = N 倍设备往返换零增量信号
(aippt_vvSpeed 实测:TemplateFilterDialog 24 条里 20 条是风格×10+颜色×10 同构组;全树 189→165)。

```bash
python3 $SKILLS_ROOT/a2h-functional-merge/scripts/fold_enum_groups.py <spec/toolkit-fact-tree.json>          # dry-run 看报告
python3 $SKILLS_ROOT/a2h-functional-merge/scripts/fold_enum_groups.py <spec/toolkit-fact-tree.json> --write  # 落盘
```

- **折叠规则(确定性,无 LLM)**:分组键=(宿主页, source_section==enum_options, decl_file, name 的'-'前缀),
  组员≥3 → 折叠为 2 条:`enum_group_presence`(组存在性,B.4.5 走 dump 文本匹配零点击) +
  `enum_group_behavior`(代表值深测全链;代表优先取已 grounding 成员,否则跳过"全部/其他"取首个具体值,
  expected_android/android_trusted/precondition 随代表携带)。members[] 保留全部原成员关键信息。
- **静态标题剔除**(保守双谓词:name 以"标题"结尾 AND expected 以"显示"开头)——纯静态文本断言归 UI 截图对比,
  不该占 functional check(`--no-drop-titles` 可关)。
- **可逆**:被折叠/剔除的原始完整对象存 `spec/a2h/_work/fold_enum_report.json`。**幂等**:enum_group_* 不再参与折叠,重复跑零副作用。
- **消费端已接**:visual-verify B.4.5 第 0 步按 check_kind 分流(presence→dump 匹配/behavior→代表值走原流程,
  见 sub-agent-batch-prompt.md);Phase 0.5 grounding 同步(presence 零点击 grounding,见 phase2.5-grounding.md)。
- **三架构通用**:折叠作用在树上,XML/Compose/混合注入完之后都跑这一步。

## 5. 铁律(防污染,同 app-relationship-tree)

- **只新增** `functional_checks` / `unmapped_functional_points` / `android_anchor` / `stats.a2h_functional_merge`。
- **禁改** toolkit + art 已填字段:navigation / reach_path / inbound_triggers / navigation_contract / purpose / id / type / parent_id / components / flow_graph。改了=污染,重做。
- **只消费 A2H Stage1**,不跑 Stage3/4/5。
- **不丢功能点**:每条要么挂 page,要么进 unmapped(带 reason)。
- **确定性优先**:LLM 只精修 low 置信枚举,不全量 LLM。
- **★归属以 `android_anchor.decl_file` 为准(源码真值),不是名字匹配**(2026-07-16 AIPPT 实证:196 个
  check 约 30 个挂错节点)。decl_file 直说了控件住在哪个文件,它才是归属的唯一真值:
  - decl=类文件 `Xxx.kt` → 归属节点 `Xxx`;decl=布局 `activity_xx.xml` → 归属该布局的**宿主页**
    (用源码 `R.layout` 绑定反查,**不用命名约定**——`WorksFragment→fragment_work` 会猜错,
    同 arkts-visual-verify/plan_edge_walk.py:161 的教训)
  - **白名单例外**(不然会误伤,这两类 decl≠节点是对的):`item_*.xml` 列表项布局 → 归**宿主页**;
    桥/工具类(`WebAppInterface.kt` 等非页面类)→ 归**注册该桥的容器页**(同 a2h-functional-registry §131)
  - feature_path / 裸名匹配**只配当 decl_file 定位不到时的兜底,且必须告警、不许静默**——
    `merge_functional_into_facttree.py:resolve_host_via_fp` 的「第二趟裸名兜底」就是串台之源:
    **6 个弹窗都有「关闭」,裸名一撞就全倒进同一节点**。实测 AppTipsDialog 收了 5 个别人的「关闭」
    (来自 MemberCenter/Campaign/LimitedGift/VipFunctionIntercept/VipBindAccount),而
    CampaignDialog、VipFunctionInterceptDialog 的 checks 被搬空成 **0**。同款:GuideDifficulty3
    收了 Difficulty1/2 的「是/否」(tv_goon/tv_skip 三个 fragment 同名),Difficulty1/2 归零。
  - **挂错的代价是双向的**:挂错那边**永久 not_found**(换任何 trip/状态都救不了,且会被误判成
    「该态不渲染」——实测 MineFragment 5 个 not_found 里 2 个其实是挂错);正主那边**静默缺 check**,
    账面看不出来。

## 6. 自检(写入 stats,透明缺口)

退出前确认(脚本已内建,任一失败即 fail):
- 功能点总数 == mapped + unmapped(无丢失)。
- 每条 functional_check 的 `android_anchor.decl_file` 非空。
- **★归属正确性(2026-07-16 新增,治「只验完备不验正确」)**:每条 check 的 `decl_file` 必须**解析得回它
  所在的节点**(类文件名==节点id / 布局==该节点的 `R.layout` 绑定 / `item_*.xml`、桥类走上面的白名单)。
  对不上 → **列出并 fail,不许静默落盘**。
  ⚠ 只验「decl_file 非空」是**不够**的:真值一直在手却从不拿来对账,正是 ~30 个 check 挂错却全程绿灯的
  根因。这条闸是确定性的、零成本,能一次挡住整类缺陷。
- **★反面信号(串台警报)**:某节点有 layout/类却 `checks=0`,同时另一节点堆着 N 个**同名** check
  → 极可能是裸名兜底把它们全倒过去了(实测 CampaignDialog/VipFunctionIntercept/GuideDifficulty1/2
  被搬空)。列出「checks=0 但有 UI 的节点」+「同名 check ≥3 的节点」两张表供核。
- 没有改动 toolkit/art 字段(只多了 functional_checks / unmapped 数组)。

输出账单(stats.a2h_functional_merge):`功能点总数 / mapped(按置信分档) / unmapped 及原因 / 挂上但缺预期数 / 承接页面数 / 枚举精修数`。缺口明明白白标出,不假装 100%。

## 7. 下游契约(双 oracle,visual-verify 怎么用)

本 skill 注入的是**双 oracle 的种子**:`expected_llm`(LLM 静态分析,保底)+ `expected_android:null` / `android_trusted:null`(占位,待 grounding 填)。完整链路:

**上游 grounding(visual-verify Phase 0.5,安卓趟)**:导航到页后逐 check 在**安卓**实操功能 + 观察 + **结构指纹自验**,填:
- `expected_android` = 安卓实测真值(主判据);`android_trusted` = 指纹判落点是否可信;`precondition` = 测试登录态。
- 指纹独立于 `expected_llm`(对照 fact-tree 该功能点该去的 record 结构),挡误触/没点中——没真到达就标 `android_trusted=false`,不瞎写。

**下游判定(visual-verify Phase 2,鸿蒙趟)**:遍历到页时逐 check 鸿蒙实测 H,按 `android_trusted` 分流(语义匹配,非字面):

| android_trusted | 判定 |
|---|---|
| **true** | H 匹配 `expected_android` → PASS;不匹配 → **FAIL**(安卓可信真值,鸿蒙不符=真退化;形态退化 弹窗↔toast↔整页 算不匹配)|
| **false** | 退回 `expected_llm` 弱判 + 标 `low_confidence`(安卓无可信真值,保守;鸿蒙实际可达且与源码预测一致时补记供人工升级)|

- precondition:鸿蒙登录态须 == check 的 precondition,否则跳过+标 precond_mismatch。
- FAIL/low_confidence → 写 feat 单:`fixer_layer=feat`、`kind=IMPL_MISSING`、evidence 带 `expected_android`(主)+`expected_llm`(种子)+`android_anchor`(安卓锚点供 fixer 对照)+鸿蒙实测 H。
- 通用宿主页(`type_discriminator` 非空且多条)→ 循环测各 type。

**为什么双 oracle**:`expected_android`(安卓实测)和 `expected_llm`(LLM 猜)是"修正者 vs 被修正者",不是两个投票者——所以**不用"两者一致"当置信**(那是范畴错误,会把 grounding 成功纠错误降级);而是用**独立结构指纹**判 `expected_android` 自身可信度。切片实测:真退化 4/4 抓 FAIL、untrusted 3/3 落 low_confidence 不误报、grounding 同时提 precision(少误报)和 recall(抓到单 oracle 漏的门禁退化)。

这样**一趟遍历同时出 UI 单(原有)+ feat 单(功能维度)**,无需 A2H 跑执行、无需事后映射。详见 arkts-visual-verify `references/phase2.5-grounding.md`。

## 8. 局限

| 局限 | 说明 |
|---|---|
| 覆盖上限 ~82%+精修 | 确定性映射 82.7%;参数原子(比例/媒体筛选)无 page record → 进 unmapped |
| feature_path 归一是 join 命门 | registry 与 intents 的 feature_path 格式/粒度有差异,靠归一+叶名兜底,极端不一致会 join 不到预期(标 expected_missing) |
| 预期是安卓派生 | 多数 OK(规则9 限可视觉验证);少数引用安卓专属文案的,下游判定看语义不看字面 |
| 依赖 art 先跑 | fact-tree 必须先经 art 补好导航,否则页面够不着,功能检查无从执行 |
