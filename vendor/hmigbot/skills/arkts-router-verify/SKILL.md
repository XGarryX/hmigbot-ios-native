---
name: arkts-router-verify
description: 静态验证并自动修复 Android→HarmonyOS 迁移的"页面路由跳转"。脚本各抽一张控件级导航图 (Android 的 startActivity/companion/Jetpack-Navigation/XPopup 弹窗，HMOS 的 router/ Navigation pushPathByName/CustomDialog)， 以 spec 的 ui-manifest 做权威页面映射，逐页对账，检出四维度路由问题并改 HMOS 源码： ① 目标页面是否存在 ② 目标弹窗是否存在（弹窗是一等路由目的地，按 dialog_specs 抽取规格重建） ③ 跳转按钮/文字/菜单项是否存在 ④ 触发点是否绑定了路由跳转/弹窗打开。修完再复检出报告。 只要用户想"验证路由跳转/导航迁移对不对"、"检查跳转按钮有没有/绑没绑路由"、"页面跳转漏没漏"、 "route verify"、"迁移后导航验证"，即使只说"检查跳转"、"验证导航"、"路由对账"，都应触发本 skill。 纯 UI 视觉/控件属性验证不归本 skill（那是 arkts-visual-verify）。
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

# ArkTS-Router-Verify — 迁移路由跳转 静态验证 + 自动修复

验证 Android 原版的"点击控件→页面跳转"在 HMOS(ArkTS)迁移版里是否被正确实现，并自动修复。
**纯静态**(读源码，零设备零编译)，因此可进 CI、可复现。

核心思路:把 `(源页 → 触发控件 → 导航调用 → 目标页/弹窗)` 这条链在**两端源码各抽一张控件级导航图**，
再以 spec 的页面映射对账。检两个维度、修四维度问题(A1 页面缺/A2 弹窗缺/B 控件缺/C 未绑定):

- **维度1 跳转是否正常**: Android 有 `源→目标`(页面或弹窗)，HMOS 是否也有、目标对不对
- **维度2 控件存在 + 事件绑定**: 触发按钮/文字/菜单项在不在、点击绑没绑到路由/弹窗

## 何时用

用户要验证/修复迁移后的**导航路由**正确性时。不要用于:纯视觉对比(arkts-visual-verify)、
控件属性/UI 层测试、功能逻辑验证（由其它 verifier 负责）。

## 前置

- 两个仓:Android 源码 + HMOS(ArkTS)迁移仓
- **产物落点 = 整个工程目录(不是 skill 目录)**:所有脚本/模型产物统一写到
  `<HMOS工程根>/spec/verify/route/`。工程根 = 含 `.agents/` 的那一级(安放约定:skill 装在
  `<HMOS工程根>/.agents/skills/arkts-router-verify/`),由 `nav_common` 从脚本 `__file__` 位置
  向上找 `.agents/` 自推导——**锚定工程根,即便 `cd scripts` 也不会落进 skill 目录**。
  唯一必传参数是 `--android-root`(Android 仓根,extract 后写进产物供下游自动读);要改落点用
  环境变量 `ROUTE_VERIFY_ROOT`(工程根)/`ROUTE_VERIFY_OUT`(直接指定产物目录)或各脚本
  `--out-dir/--hmos-root` 覆盖,**不在代码里写死路径**
- **自包含,无跨 skill 依赖**:确定性抽取原语(Android 源码枚举/控件文案反查/intent-extras
  gating)已全部就地实现于 `scripts/reuse.py`(仅依赖标准库,不再 importlib 加载兄弟 skill)
- HMOS 仓有 `spec/baseline/ui-manifest.md`(迁移期产出的页面映射表)最佳;没有则退化为命名启发式
- 换仓适配点(**必配 `FIRST_PARTY_PKGS`**、ALIAS/ENTRY 等)见 `references/config.md`

## 工作流(7 步，按序)

所有脚本在 `scripts/` 下，互相同目录 import。**全部产出统一写到 `<HMOS工程根>/spec/verify/route/`**
（工程根 = 含 `.agents/` 的那一级，不是 skill 目录）——脚本产物、模型在环写的 `llm_verdicts.json`、
最终报告 `ROUTE_VERIFY_SUMMARY.md` 都在这一个目录，不散落别处（脚本侧由 `nav_common.out_dir()`
= `<工程根>/spec/verify/route` 保证，自推导锚定 `.agents/` 不随 `cd` 漂移；模型侧把文件写到
**同一个目录**——脚本每步都会打印该目录的绝对路径，按它写即可）。

### Phase 1 — 抽两端控件级导航图

```bash
cd scripts          # 仅为简写脚本调用；产物落点自推导到 <工程根>/spec/verify/route，不在 scripts 下
# （skill 未装在工程的 .agents/ 下、或要改落点时：export ROUTE_VERIFY_ROOT=<工程根>）
# ① Android：穷举 nav 点 + 触发归属到点击点 + tab 组
#    覆盖: Intent::class / companion / dialog.show / XPopup asCustom / Jetpack Navigation
#    (res/navigation/*.xml 的 action→destination 自动解析) / startActivity(ForResult)
#    注释内的示例代码已剥离不计
python3 extract_nav_graph.py --platform android        # → expected_nav.json
```

**② LLM 补长尾(模型在环)** — 脚本只解确定性目标(解析率看 stats.clickable_resolved_rate，
因仓而异)，剩下的程序化/外部 intent/navigate(变量) 要模型裁决:

```bash
python3 llm_worklist.py                                 # → llm_worklist.json(flag 方法清单)
```

读 `llm_worklist.json`，对每个唯一方法体裁决(只读被 flag 的方法，不读全仓)，写
**`spec/verify/route/llm_verdicts.json`**(模型在环产物，与脚本产物同目录；格式见
`references/llm_verdicts.example.json`)。裁决要点:
- 剔除非路由:`ACTION_DIAL/VIEW` 外部 intent(拨号/浏览器)、`AppLoadDialog` 等 loading 框、注释死代码、
  companion 自跳定义(launcher_def)
- 救回真边:程序化桶里的真实跳转(如某 `onClick→Login`)、span 文本链接、守卫式跳转(支付前鉴权)

```bash
python3 apply_llm.py                                    # → nav_edges.json(清洗后的 Android 路由集)
# ⚠️ 带裁决覆盖率门禁：worklist 里 <85% 的 flag 方法有裁决时拒绝出集(防拿半裁决产物出报告)，
#    明知故犯需显式 --allow-stale-verdicts；同时打印输入产物 mtime 时间线，旧于上游会告警
```

**③ HMOS：控件级 + 全链绑定 + tab 组**

```bash
python3 hmos_extract.py                                 # → actual_nav.json
```

每个 `.onClick` 控件记录 `{类型/文字/图标, 是否绑定, 全链追到的目标(含 onClick→this.方法()→router), guard}`。
覆盖四族弹出/跳转形态：router、Navigation(pushPathByName/pushPath 对象式)、CustomDialog
(controller.open + `openCustomDialog`，含 wrapBuilder)、**popup/sheet 族**(`bindSheet`/
`bindContentCover`/`bindPopup` 属性式弹层——状态翻转显示，静态归不到点击点，记页面级 dialog 边；
`bindMenu` action 回调按点击触发源)。**路由名 = 字面量 + 常量符号表**(RouteConstants.X
自动解析成真名)，纯变量解析不出 → target=null 计入 `stats.nav_target_unresolved`(不再错把变量名
当路由名)。TabContent 首子是 Stack/Column 等内建容器时继续向内找自定义组件。
**死 Builder 检测**：零引用的非 export `@Builder`(声明了但没挂渲染树)体内抽出的
边/控件打 `dead_builder` 标记——`grep 命中 ≠ 渲染可达`，visual-fixer 把工具栏 Builder 从 build()
摘除后五个入口静默消失、静态照常全绿就是此盲点。报告侧(build_report/diff_routes/reachability)
自动排除死边；`stats.dead_builders` 清单必须逐条 triage：恢复挂载 or 确认有意移除记遗留。
**返回/关闭键审计**(`back_audit`)：按 media 资源名认"返回意图"图标(启发式见 config.md §3)，
验证其属性链或父容器(≤2 层回溯，Row{图标+文字}.onClick 惯用法)绑定了返回效果——pop\w*(必须
覆盖 popSafely 等封装变体)/back/close/dismiss/@Event 委托/状态翻转关浮层。`missing_onclick`/
`unbound`(handler 实质为空)是缺陷；**`bound_event` 项需补一步宿主链核验**：pageMap 裸实例化
`X()` 进入的页面级组件无法接收 @Event/回调对象，默认空操作=死键——确认有 pages/ 包装层接真
回调，或组件内自兜底 pop。

### Phase 2 — 页面映射(spec 权威 + 实际核对)

```bash
python3 build_page_mapping.py                           # → page_mapping.json
```

以 `ui-manifest.md` 的 Android→ArkTS 映射为权威基底，叠加 Fragment→子组件 View 启发式、实际抽取核对。
**输出里的 `divergence` = spec 意图 vs 实际实现的偏差**(就是迁移问题，如"spec 计划合并但实际另造独立页"、
"spec 转换但实际孤儿无导航到达")。

### Phase 3 — 对账(四视角，互为印证)

```bash
python3 build_report.py                                 # → migration_nav_report.json (per-page 控件级)
python3 diff_routes.py                                  # → diff_routes_report.json/.md (目的地+边级)
python3 hmos_reachability.py                            # → reachability_robust.json (robust 口径)
python3 thin_shell_probe.py                             # → thin_shell_report.json/.md (薄壳占位口径)
```

- **build_report** 每页: `{android_page, hmos_page, page_aligned, jumps[], missing_jumps[], extra_jumps[]}`。
  `jumps` 含 `match_by`(text 精确 / target 图标按目标 / tab 底部栏兄弟)；tab 互切不误报。
  ⚠️ 只看得到 onClick 链发起的导航——程序化 push(启动 manager/三元/变量)在此口径下显示
  missing，**必须以 robust 口径复核后再定性**。
- **diff_routes** 目的地覆盖 + 边级 diff(Android dialog/auto_dialog 与 HMOS page+dialog 对称口径)。
- **hmos_reachability**(robust，与触发方式无关): 对每个 Android 目的地查
  `struct 存在 / 全文件 push 证据(字面量+常量) / pageMap 注册 / embed 引用(bindSheet/builder/内联)`，
  分层 wired / reachable_via_embed / struct_only_no_push / pagelevel_missing / inline_overlay；
  **附查 pushed_but_unregistered(push 了但没注册进任何 pageMap → 运行时必崩，最高优)**。
  这是 onClick 盲点的兜底口径，三视角里最稳。
  **附查 no_back_affordance(页面级返回缺失)**：被 push 的注册页若 `hideTitleBar(true)`(系统
  返回箭头被藏)且全文件无 pop/back/close/onBackPress、也无返回意图图标 → 用户进去只剩系统
  手势可退，对照 Android 工具栏返回即"返回缺失"——典型成因是设了 `.title()` 又 hideTitleBar
  却没补自绘返回。
  **附查 embedded_pop_only_back(双形态 pop 失效，第三层盲点)**：页面既注册可 push、又被别处
  内嵌实例化(主区内容/Pad 双栏)，返回键效果仅 pop 系且无内嵌退出路径(`embedded_exit`：事件
  发布/状态翻转/@Event 委托)——push 形态正常、内嵌形态栈上没有自己 → pop 空栈 no-op 点击无
  反应。**绑定存在 ≠ 绑定在当前渲染形态下有效**。修法：栈深>0 走 pop，栈空走宿主内容切换
  事件。命中项需人工确认(内嵌于"自身已被 push 的宿主"时 pop 外层是正确语义,如登录子栈根页)。
- **thin_shell_probe(薄壳占位，第五层盲点)**：对 reachability 的每对 android↔hmos 页做
  **字段集对账**——ViewBinding 泛型反推安卓布局(`FragmentXxxBinding`→`fragment_xxx.xml`,
  类名≠布局名时 a2h-spec 与 android_dialog_probe 都会漏)、安卓 `@string/x` vs HMOS
  `$r('app.string.x')` 键迁移率、控件类缺口表(SeekBar→Slider/RadioGroup→Radio/
  RecyclerView→List/ForEach…)、交互控件数比。**"存在性"三视角全绿的对应物可能只迁了
  零头**(复盘案例:PadCreateSketchDialog 安卓 57 交互控件、HMOS 11 个,且薄壳占住"存在"
  这个坑反而把 A2 缺失重建路径挡死——半成品比空缺更难被发现)。坑:HMOS 同名文件有
  re-export 壳(dialogs/X.ets 数行转发 pages/X.ets),探针已优先取真声明 `struct X` 的文件
  并跟随 `export{X}from`,人工核对时同样别拿转发壳当实现。阈值/控件对账表见
  `references/config.md`。在 Phase1① 与 hmos_reachability 之后跑。

### Phase 4 — 分析 + 自动修复(改 HMOS 源码)

**修复对象 = 页面 + 弹窗，一视同仁。** 弹窗是本 skill 的一等路由目的地(`dialog.ctor`/`dialog.show`
边)——"目标弹窗不存在"与"目标页面不存在"同属维度 A，**禁止以"弹窗属功能层"为由把整类划出修复
范围**(复盘教训:曾有一轮把 21 个弹窗目的地整体记遗留，被对账清单打回重修)。确实修不了的
(目标依赖未迁移的外部能力，如系统分享面板/三方 SDK 页)逐条定性进遗留项，不按类划走。

按 ①→⑥ 顺序执行（④⑤⑥ 是"清单 → triage → agent 分派"的修复管线，所有修复经由
`fix_plan.json` 流转，不允许绕过清单直接改码——清单即审计轨迹）：

**① 定位**：读四视角产物——`reachability_robust.json` 优先(其 `pushed_but_unregistered` 最高优:
push 了没注册，运行时必崩)，再 `migration_nav_report.json`(控件级 missing_jumps) +
`diff_routes_report.json`(边级；弹窗看 `dest_missing_inline_overlay` / `edge_missing_inline_overlay`
两个清单，这就是弹窗修复的工作列表) + `page_mapping.json`(spec 偏差) +
`thin_shell_report.json`(thin_shell=true 项 = 薄壳补全工作列表，A2-THIN)。

**② 调查定性**(硬规矩，否则会错改)：对每条 missing/divergence 先读 HMOS 源码：
- 跳转其实存在但抽取盲点(协议链接 / auto-nav / @Builder 参数 lambda / bindMenu action)→ **不改，
  回头扩抽取器再复跑**(否则修复清单本身就是错的)
- 死代码/被系统能力替代(如 FileUpload→DocumentViewPicker、Android R+ 权限提示框)→ **不改，报告标注**
- spec 计划的合并/重构(根页用 `pop()` 返回 = push 的架构等价；Android adapter 里的弹窗宿主迁进页面)
  → **核对承接方真实可达后记"等价"，不记缺失**
- **grep 命中 ≠ 渲染可达**：作"已存在/等价"判定引用的证据行,必须核实不在死 Builder
  (`stats.dead_builders`)、注释、未挂载组件内——绑定代码躺在仓里但渲染树不调用,运行时照样没有
- **孤儿页出边不得作 wired 证据(第四层盲点)**：判 already_wired/等价时引用的 push 语句,
  必须回查其宿主页在 `reachability_robust` 的 layer——宿主是 `struct_only_no_push`(注册了
  但零入边)时该边是 **orphan_edge**,等于没接(复盘案例:九个笔弹窗的 re-tap 修复全落在
  孤儿 Hub 页上,边级对账永远自洽绿,live 组件没人修)。裁决证据必须含一条**从入口可达的
  完整触发链**,不接受"目标存在+有 push 语句"单证
- **存在 ≠ 完整(第五层盲点)**：对应物存在时,判 already_wired/architecture_equivalent 前
  必须过 `thin_shell_report` 口径——thin_shell=true 的不是等价是 A2-THIN 待补全,
  禁止以"已合并/已迁移"叙事一笔带过
- **单宿主兼任 Android 多形态**(同一 HMOS 页既当主区又当推入列表页)时,对照取**形态并集**;
  与 visual-verify 的单 baseline 修复(extra_element 砍件)交叉核对,防互相误伤——visual-verify 修复轮按"主页"
  基线砍掉顶栏五图标,连带"文件夹列表"形态的入口全静默丢失即此例

**③ 弹窗信息采集**(修任何弹窗前必跑；弹窗"长什么样"是抽取出来的事实，不是模型记忆)：

```bash
python3 android_dialog_probe.py            # → dialog_specs.json
```

对每个第一方弹窗产出：构造参数(→ HMOS props)、回调签名(→ onConfirm 形状)、布局文件、控件清单
(单选/勾选/输入框/按钮，文案经 strings.xml 解析)。修弹窗时 props/回调/内容控件**以此为准**；
注意 RadioGroup 的选项可能在 Kotlin 类体里动态 add(布局里只有空组)——specs 里控件数明显偏少时，
回读 `file` 字段指向的类体核对选项清单。

**④ 产修复清单**(脚本机械聚合，零判断)：

```bash
python3 build_fix_plan.py               # → fix_plan.json(候选项,全部 pending_triage)
```

把三视角问题聚成逐条修复项：维度初判(A1-REG/A1/A2/C-dlg/B、C)、证据指针(哪份报告哪个字段)、
dialog 规格摘要、宿主初判、files_expected、**work package 分包建议**(按宿主文件聚类 = agent
并行的最小冲突单元)。复检轮用 `--round N` 另起文件保留历史；已含进度的清单防误覆盖。

**⑤ 清单 triage**(模型在环，写回 `fix_plan.json`)：把 ② 的调查结论逐条落到清单——
- `status: approved`(真问题,待修) 或 `wontfix`(不修)；**wontfix 必填 `verdict_basis`**
  (死代码/架构等价/外部能力未迁移/宿主重构归因差异/抽取盲点——盲点类要先扩抽取器重跑①-④)
- 补全 `host_page`(脚本映射不出的源,如 adapter/extension 边的真实 HMOS 宿主)、调整 `package`
  (A2 组件归首用宿主包;**pageMap/路由表热点文件所在包标 serial**)、修正 `files_expected`

**⑥ agent 分派修复**(approved 项按 package 并行发 Agent，协议细则见 fix-guide §8)：
- **冲突规则**：一个文件只属于一个包;含 pageMap/main_pages 的注册热点包串行跑(或排最前);
  跨包共享的新弹窗组件归首用包建,其余包只 import(depends_on 标依赖,被依赖包先跑)
- **每个 agent 的输入**：自己包的 items(含 evidence/fix_hint/spec_ref) + `dialog_specs.json` +
  `references/fix-guide.md`;**边界**:只改自己包 files_expected 内的文件,缺信息回报不擅自扩界
- **每个 agent 的回写**：**写独立结果文件 `fix_packages/result_<包名>.json`**(并行 agent 直接
  竞写 fix_plan.json 会互相覆盖——实践教训)，格式 `{item_id: {status: fixed|blocked,
  files_changed, notes}}`;主会话用合并脚本统一灌回 `fix_plan.json`。修不了的标 blocked+原因
- **新建路由名必须上报**：agent 在波内新建/push 了规划期未知的 NavDestination 路由名时,结果文件
  加 `new_routes: [名字]`——注册热点(MainPage/pageMap)归 serial 包,其它 agent 不许自己注册;
  主会话收齐后统一补注册,否则复检 `pushed_but_unregistered` 必抓到运行时必崩项(实战已出过此类必崩)
- 主会话合并全部 result 后进 Phase 5 复检

修法速查(triage 定性与修复 agent 共同依据，代码模板见 `references/fix-guide.md`)：

| 维度 | 现象(报告字段) | 修法 |
|---|---|---|
| **A1-REG 注册缺失** | `pushed_but_unregistered`(P0,运行时必崩) | pageMap/`main_pages.json`/`route_map.json` 补注册 |
| **A1 页面不存在** | `page_mapping.divergence` 孤儿/缺 struct | 建 `pages/X.ets` + 注册 + 来源页绑定 |
| **A2 弹窗不存在** | `dest_missing_inline_overlay` 弹窗目的地 | 按 `dialog_specs.json` 建 `dialogs/X.ets`(@CustomDialog) + 宿主 controller + 触发 `.open()` + 回调接 ViewModel/Config |
| **A2-THIN 薄壳占位** | `thin_shell_report` 的 thin_shell=true(存在但字段集对账不达标) | **原文件内补全**(不重建):按 `layouts` 指向的安卓布局补控件类缺口+未迁移文案键;dialog 类对照 `dialog_specs.json`(specs 里 layout=None 时按探针 ViewBinding 反推结果回读布局) |
| **B 触发控件缺失** | `missing_jumps` 控件在 HMOS 该页无对应(含菜单/CAB 项) | 该页 `build()` / 菜单数组 / CAB 菜单加项 |
| **C 触发存在未绑定** | 控件 `bound=false` / TODO 空壳 / 间接链断 | onClick / menu action 里补 push 或 `controller.open()` |
| **C-back 返回键死/缺** | `back_audit` 的 missing_onclick/unbound、`no_back_affordance` | 补 popSafely/close 绑定；pageMap 裸实例化组件加自兜底 pop 或 pages/ 包装层；hideTitleBar 页无自绘返回时还原系统标题栏 |

**A2 硬约束**(保证抽取器能识别、复检能闭环)：
- controller 用**声明初始化**形状：`xxxCtrl: CustomDialogController = new CustomDialogController({
  builder: AndroidDialogName({...}) })`——不要写 `| null`，否则 `hmos_extract` 的 RE_DIALOG_CTRL
  认不出，复检会假阴
- **组件名 = Android 弹窗类名**(ChangeSortingDialog ↔ ChangeSortingDialog)，canon 剥后缀自动对账，
  不用进 ALIAS
- 动态内容(消息文案/列表数据)走 `@Link` + 宿主 `@State`(controller 构造时普通 prop 只捕获一次)；
  回调签名照 specs 的 callback 定义，能接现成 ViewModel/Config 后端就接真的，没有后端的回调体留
  TODO——**路由链必须真实可达，业务深度可以分期**
- Android 弹窗里再开弹窗的(specs 可见,如 PickMedium→PickDirectory)，在子弹窗组件内声明嵌套
  controller，保持链路

### Phase 5 — 复检出报告

修完重跑 Phase 1③ + Phase 2 + Phase 3 全链(page_mapping 的 reached/divergence 会随修复变化，
不重跑会拿陈旧映射出报告——mtime 告警也会拦):

```bash
python3 hmos_extract.py && python3 build_page_mapping.py && \
python3 build_report.py && python3 diff_routes.py && python3 hmos_reachability.py && \
python3 thin_shell_probe.py
```

闭环断言(按维度)：
- A1-REG/A1：`reachability_robust` 该页转 wired，`pushed_but_unregistered` 保持 0
- A2：`actual_nav` 出现对应 `dialog.open` 边；`diff_routes` 的弹窗目的地从
  `dest_missing_inline_overlay` 移入 `dest_matched`
- A2-THIN：`thin_shell_report` 该对 thin_shell 转 false(overlap/缺口/ratio 达标)，
  且全局 thin_shells 数不增(防补全 A 页时把共享组件改薄殃及 B 页)
- B/C：该控件出现在 `actual_nav` 且 `bound=true`，对应 `missing_jump` 移入 `jumps`
- 全局：编译过一次(有构建环境时；DevEco hvigorw assembleHap)，防止"对账闭环但语法不过"
- 全局：`stats.dead_builders` 无新增项(修复把绑定写进没人调用的 Builder = 白修——复检必查)；
  `pushed_but_unregistered` 保持 0(波内 agent 新建路由名最容易在这里漏注册)

**回写 `fix_plan.json` 收口**：每条 `fixed` 项按上述断言核对——闭环 → `status: verified`；
未闭环 → `status: reopened`(附 notes 说明断在哪)，打回对应包重修或重新 triage。清单里不允许
留 `fixed` 终态(要么 verified 要么 reopened)。

**最终报告写 `spec/verify/route/ROUTE_VERIFY_SUMMARY.md`**(会话里同步给摘要)，修复明细直接
从 `fix_plan.json` 生成：verified 项(改了什么/在哪/谁修的) + reopened 项(断在哪) +
wontfix 项(verdict_basis 即遗留定性)。

## 命名对齐(每仓适配点)

`build_page_mapping.py` / `diff_routes.py` 里的 `ALIAS`(不规则改名映射，如
`NewDirDialog→AddDirPage` 这类)、`RESTRUCTURED`(合并成 tab/子视图)、`ENTRY`(入口页不计)
是 repo-specific，换仓按该仓 ui-manifest 调——库版本默认为空/最小集,填法见 `references/config.md`。

## 产物清单(`spec/verify/route/`)

```
expected_nav.json                    Android 全量 nav 点(脚本原始抽取,含 android_root)
llm_worklist.json                    待 LLM 裁决的 flag 方法清单(脚本产)
llm_verdicts.json                    ★模型在环写入:逐方法裁决(非脚本产,也写本目录)
nav_edges.json / nav_edges_full.json Android 最终路由集 / 全量含被剔除点(nav_kind 标注)
actual_nav.json                      HMOS 控件级 + 全链绑定 + tab 组
dialog_specs.json                    Android 弹窗规格(构造参数/回调签名/布局控件,Phase4 修弹窗依据)
fix_plan.json                        修复清单(脚本产候选→★模型 triage→★agent 回写→复检收口,审计轨迹)
page_mapping.json                    Android↔HMOS 页面映射 + 偏差
migration_nav_report.json            per-page 报告(维度1+2,onClick 口径)
diff_routes_report.json/.md          目的地覆盖 + 边级对账
reachability_robust.json             robust 可达性(注册+push+embed,onClick 盲点兜底)
thin_shell_report.json/.md           薄壳占位口径(字段集对账:键迁移率/控件类缺口/交互数比)
ROUTE_VERIFY_SUMMARY.md              ★模型写入:最终报告(修复明细+复检结果+遗留项)
```

## 重要原则

- **只读被 flag 的方法做 LLM 裁决**，不读全仓——省 token、可复现；方法多时(>100)按批切片
  并行发裁决 agent(批文件落 `llm_batches/`)，主会话合并成 `llm_verdicts.json` 后过门禁
- **修复前先调查**——区分真 bug、死代码、spec 偏差、抽取盲点，避免错改(血泪教训)
- **弹窗与页面同等修**——弹窗目的地不许按类划成"功能层遗留"；弹窗内容以 `dialog_specs.json`
  的抽取事实为准，不靠模型对原 App 的记忆(知名开源项目尤其容易"想当然")
- **源码存在 ≠ 渲染可达**——绑定/push 必须挂在 build() 可达的渲染路径上才算数,死 Builder
  清单(`stats.dead_builders`)是一等公民问题源(复盘案例:五入口静默消失、对账全绿)
- **存在 ≠ 完整**——对应物"在"不等于"迁全了"。已存在的页/弹窗必须过 thin_shell 字段集对账,
  薄壳占位(白板弹窗:57 控件迁 11)比纯缺失更危险:它把存在性检查全部喂绿,还挡住重建路径
- **静态只证"源码里接对了"**，不证"运行时跑通"(运行时需设备，本 skill 不做)
