---
name: app-relationship-tree
description: 在 `toolkit-fact-indexer` 已产出的 `spec/toolkit-fact-tree.json` 上做**多源补全**——把
  iOS 源码、a2h-spec 的 `spec/baseline/ui/page_*.md` / `feature-index.md`、ios-ui-graph-builder
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

> **原生输入边界**：本文件保留 Garry 的目标平台算法、私有 wire 字段和平台对照示例。
> 源输入只来自当前 git facts/semantics/page spec；历史源设备命令和旧语言扫描不适用于 iOS，
> 不得实际调用或用它们的缺省结果表示源端通过。源扫描缺少原生适配时保持 unresolved；
> 当前范围的屏幕采集/设备控制记 not_run。目标 hdc/hvigor 的适用部分也须遵守当前授权。



> **统一源合同**：源码只经 hmigbot_ios.execution_source.Source 消费 git 已校验的 facts/官方词项；本技能处理图的输出/查询合同，不重跑另一套源解析或选择不同构建配置。源语义、范围与审批回 git 上游。先读 [执行交界](../a2h-run/references/execution-boundary.md)。禁止当前范围的屏幕/界面/远控操作。历史 Android/Compose 源扫描命令不可用于 iOS，未知值不能填成已观测或通过。



> **iOS 源输入适配**：执行源分析/源设备操作前，读 [原生输入协议](../ios-source-analysis/SKILL.md)。它仅替换平台输入；原阶段、模板、规则、门禁、模式和 target 侧执行保持 1.5.2。

> **Codex subagent dispatch convention.** This skill dispatches subagents. In Codex, spawn them with the `spawn_agent` tool and pass `agent_type` = the role name **exactly as written in this skill** — the roles registered under `.codex/agents/*.toml` use the same hyphenated names, so no translation step is involved: `a2h-ios-converter`, `a2h-ios-analyzer`, `a2h-closer`, `a2h-fixer`, `a2h-migration-worker`, `ad-profile-builder`, `compose-fact-analyzer`, `hmos-builder`, `scenario-builder`, `visual-fixer`, `visual-fixer-reviewer`. The built-in `general-purpose` agent_type is unchanged. (Claude's `subagent_type` field is written `agent_type` for Codex; `Agent(...)` dispatch calls are `spawn_agent(...)`; there is no `Task` tool in Codex.)
>
> **Join 协议（收口五条款）。** Codex 子代理完成后**不会**唤醒主会话——结果必须由派发方主动收口，违者=静默卡死（实测事故）。
> ① **循环 wait**：每个 `spawn_agent` 句柄用循环调用 `wait_agent` 收口；单次超时只代表"还在跑"，继续再调；**禁止以"等待子代理"为由结束回合**。醒后必调 `list_agents` 确认是谁完成——**完成的唯一合法信号 = `agent_status` 为 `{"completed": …}`，绝不是产物文件的存在/条数**（文件会中途落盘，读半截=实测事故）；completed 态会在数轮后从 list 中消失，所以每次醒来都要及时查。正文所有"等待完成 / join / 到点即收"表述一律指此循环。
> ② **死句柄与验收**：连续 3 次超时后调 `list_agents` 核对，可配 `wait_for_artifact.py` 探产物活性；已 completed 且 summary 可读 → 直接消费；句柄消失且从未观测到 completed → 按断点重派（带原 prompt + 已落盘产物，上限 2 次），禁止继续等待。**completed ≠ 验收通过**：join 点跑 `python3 .agents/skills/a2h-join/scripts/join_gate.py --project .` 验产物完整性，FAIL 视同未取回、按本条重派。
> ③ **收口锚点**：本 skill 最终完成报告前必须收口全部句柄（join_gate exit 0）；正文写明的显式 join 点优先按正文执行。发用户门（Gate）时允许句柄跨 Gate 存活，但 Gate 摘要必须列明未收口句柄清单 + 各自的指定 join 点。
> ④ **放行 ≠ 遗弃**：正文"非阻塞放行/到点即收/降级继续"只推迟收口时机，不豁免收口义务。
> ⑤ **fire-and-forget**：仅正文显式声明"结果丢弃/不 gate"的派发（如 a2h-execute 的 env-prewarm）免收口；审计只认 join_gate 内静态 allowlist，正文声明只是文档层。
> **派发纪律**：`task_name` 必须唯一（带 page-id/slice-id/round-N 后缀）；并行派发前把预期产物清单写 `spec/a2h/_work/expected_<join点>.json`（join_gate 对账用，契约只认派发方、不认子代理自报）；**谁派谁收**——sub-agent 内部需要"等齐 N 片再合并"时禁止嵌套外派后自行退出，要么同步自做、要么把分片清单回报主会话代派（sub-agent 一停止，收口能力即丢）。**契约产物必须出自承担任务的子代理**：重派上限后仍产不出 → 如实报缺并停在未完成态；禁止派发方代写占位产物让 gate 转绿（声明过也不行——绿账必须对应真产物）。

> **路径约定**：下文 `$SKILLS_ROOT` = 本套 skills 的安装根目录。执行任何脚本前先设一次：`SKILLS_ROOT="$(cd "$(dirname 本SKILL.md)/.." && pwd)"`（用户级安装=`~/.agents/skills`；项目级=`<project>/.agents/skills` 或 `<project>/skills`）。

# app-relationship-tree — 原生事实树多源补全

## 1. 定位与原合同

沿用原五个主 phase 及 1.5/1.6、2.3/2.5/2.6/2.7 子步骤，原地补全 spec/toolkit-fact-tree.json，不新增另一棵关系树。补 purpose、触发链、前置态、导航合同和 dependency_graph；正确的 source_anchor、结构边和已有字段不能随意改写。

源输入统一遵守 [native-input](../ios-source-analysis/SKILL.md) 的 A1 入口/导航口径：App/Scene、实际 SwiftUI NavigationStack/Link、Tab、sheet/fullScreenCover、UIKit push/present/segue、URL 和 IB 关系。用 Source 选定的 target/当前配置源码、原四文件 UI 图、source-index 及 page/feature spec，不从类型后缀猜实际可达性。

原 fact-tree 的 pages/fragments/dialogs/components 是规范化分组槽位：分别承载顶层页面、嵌入子页、模态和普通组件，不代表原生框架类。保留原 JSON 键和 schema_version=1；fq_class/ios_file/source_anchor 必须为实际模块类型和源文件。静态分析节点明确 analysis role，不伪造 framework class。

## 2. 执行流程

### Phase 1: 探测 fact-tree

读取原 schema、实际 spec/toolkit-fact-tree.json 和 source-index。缺少时走 ios-fact-tree 的原生分析路径，按同一 schema 产出；UIKit/IB 与 SwiftUI 使用原生图/源码及语义补充。不能把仅支持其他源语法的 toolkit 编译扫描器用于 Swift，并把零扫描当成功。事实树未产出则如实缺少输入，不造空树；本技能是按原触发条件调用的专项能力，不新增到 SPEC 主线。

### Phase 1.5: 节点级校准

按真实声明、入口/导航/包含关系检查节点：仅合成 ID 没有实际源依据的节点需核实；fq_class 从模块与真实声明取值；漏识页面从源和规格补齐。删除/合并必须有等价真实节点证据并更新引用，不能把未在 plist 逐页登记的 SwiftUI 页面当假节点。保留正确事实，记录允许的 metadata/节点变动及理由。

### Phase 1.6: 源码 popup 正向扫描

不依赖已有 page spec，沿选定源码检查 sheet/fullScreenCover/alert/confirmationDialog/popover、UIKit present 与 child containment、UIAlertController/UIPresentationController 及真实自定义封装；追调用与条件，不只按文件名。记录候选、已存在、实际新增、未决与 source anchors。新增 source=app_relationship_tree_added_class_scan；construction_mode 继续用历史分析类别 layout_xml（真实 Storyboard/XIB）或 code_only（真实代码组合）。名称命中但无行为证据只能 uncertain=true，不能冒充真实模态。

### Phase 2: 补 purpose

逐 page/嵌入页/模态/component 读取源码与 spec，用自然语言说明用户目标、输入、结果和边界。purpose 不能只是类名、重复模板或源码复制；未知按原自检报缺。

### Phase 2.3: 多源 BFS reach_path

保留原 BFS 的 source entry、outbound 与 inverse-inbound 并集、contains/shows_dialogs 关系和交替 node/trigger token 形式；从实际 App/Scene/URL 入口开始，候选页面作为静态路径入口的情况必须与真实启动可达区分。所有路径节点引用闭合，不制造点击边。可复用只读通用图计算；若原 helper 仍要求不适用的源语法，则按同一算法顺序完成并记录证据，不运行该源扫描器。真正孤立或无法证明的路径明确披露，不能为满足非空检查伪造路径。

### Phase 2.5: 补 inbound_triggers

对每个实际调用方，沿 Button/action/gesture/selector/delegate/状态变化/scene 或 URL 处理，提取 from_page、trigger_type、trigger_label、trigger_view_id、evidence_file/evidence_line 和前置条件。控件 ID 使用真实身份并注明种类；无显式 ID 可用真实文本/结构定位，不能伪造资源 ID。自动显示与用户点击分开，动态目的地和触发文本保持不确定性。

### Phase 2.6: navigation_contract

保留原六种 relationship_kind：host_default、tab、sub_tab、wizard_step、lifecycle_modal、dialog_trigger。这里描述关系类别，不是框架 API。沿 A1 已有原生导航/状态口径核实宿主、默认选项、step 绑定、真实 present/sheet 条件与关闭路径。

合同保留 relationship_kind、wizard_index（仅多步）、from_state、trigger_actions[]、verify_signal、exit_action_to_next、contract_uncertain、generated_from。动作沿用 auto_default/tap_text/tap_resource_id/back/swipe；resource_id 必须是对应工具可观测的真实标识，缺设备观测不能当成已执行。verify_signal 必须能区分目的状态，不能用宿主存在冒充子页到达。多入口保留各自前置态；顺序 step 的 leads_to/index 闭合。没有源证据的合同标 uncertain 并写原 contracts_uncertain 报告，不能转成 fake-pass。

### Phase 2.7: 扩充 preconditions

校验并保留已有条目，按 kind+evidence 去重，新增 source 前缀 app_relationship_tree:。覆盖认证、权益、额度、权限、必填参数、缓存/集合内容与网络状态；保留实际检查顺序和失败副作用。

2.7b 的 state_required 对所有 record 做真实数据前置态推导，不因缺 page_md 跳过；从源条件与数据流定位哪些状态需要先准备。不得通过虚构账号、后台响应、服务成功或隐藏测试入口“准备”状态。

### Phase 3（可选）: reach_paths 孤儿补充

只给有真实依据的候选路径补充 heuristic 标志，不把启发式当设备到达结果，不删除已正确的 reach_paths。

### Phase 4: dependency_graph.layers

保留原六层和 feature 覆盖/互斥规则，按实际业务依赖而不是源目录或类型名称分层。输出遵守原 schema，不另加 UI 实现文件映射义务。

### Phase 5: 自检 + 写回

退出前必须确认：

| 项 | 验证 | 严重度 |
|---|---|---|
| JSON 合法 | `jq empty < spec/toolkit-fact-tree.json` | HARD |
| schema_version=1 不变 | 没被改坏 | HARD |
| 所有顶层页/嵌入页/模态 `purpose` 非 null | 自检 | HARD |
| 所有 component `purpose` 非 null | 自检 | HARD |
| navigation / source_anchor / parent_id / flow_graph / features / stats 与 LLM 跑前**逻辑等价**（允许 Phase 1.5 删假 record / 改 fq_class）| diff with allowed-mutations whitelist | HARD |
| **Phase 1.5 删除节点的 inbound/outbound 已 merge 到等价 real record**（v6.3）| 扫所有 navigation.inbound/outbound，from/to 必须存在于当前 records | HARD |
| **Phase 1.5 新增节点字段齐全**（v6.3）| id / type / fq_class / ios_file / source / purpose 不能 null（除了 source 字段标 added 的可接受首版 purpose=null）| HARD |
| reach_paths 字段保留（保留本次输入已有且正确的路径） | 长度 ≥ Phase 1 时长度 | HARD |
| **reach_path 字段非空**（v6.3 Phase 2.3）| 每条 record 都有 reach_path（App/Scene 根时为 `[id]`，其它至少 3 元素：root + token + self） | HARD |
| **reach_path 中所有 page-id token 都在 fact-tree 里**（v6.3）| BFS 中间步骤不能引用不存在的 record | HARD |
| **dependency_graph.layers 覆盖所有 features** | 每个 `fact.features[*].id` 必须在某 layer.features 里 | HARD |
| **dependency_graph.layers feature 互斥** | 同一 feature_id 不能出现在两层 | HARD |
| **inbound_triggers 字段存在**（v6.2 新增）| 每条 record 都有 inbound_triggers（≥1 条；launcher 可只有 boot） | HARD |
| **inbound_triggers.from_page 可达**（v6.2 新增）| 引用的 page id 必须是 fact-tree 中存在的 record，或是 null（仅 launcher boot） | HARD |
| **preconditions 扩充（v6.3）**| toolkit 已抽的基础 preconditions 必须保留；本 skill 扩充的条目 source 字段必须含 `app_relationship_tree:` 前缀 | HARD |
| **navigation_contract 字段存在**（v6.4）| 每条嵌入页/模态 都有 navigation_contract（host_default 类型可只填 relationship_kind + verify_signal） | HARD |
| **navigation_contract.relationship_kind 合法**（v6.4）| 必须是 6 类枚举之一（host_default / tab / sub_tab / wizard_step / lifecycle_modal / dialog_trigger）| HARD |
| **wizard chain 闭环**（v6.4）| 所有 relationship_kind=wizard_step 节点，按 wizard_index 排序应形成 0→1→2→...，相邻两节点 exit_action_to_next.leads_to 必须指向下一 index | HARD |
| **contract_uncertain 标记输出**（v6.4）| LLM 推断未通过确定性源码验证的，必须标 contract_uncertain=true + 写入 `spec/visual-verify/contracts_uncertain.md` | HARD |
| **新增 / 删除节点的 stats 字段对齐**（v6.3）| stats.total_pages/total_fragments/total_dialogs 必须 = 实际数组长度 | HARD |
| **inbound_triggers.evidence_file 真实存在**（v6.2 新增）| 抽样检查 5 条，evidence_file 路径必须在 ios_root 下存在 | HARD |
| **Phase 1.6 新增节点 source 前缀正确**（v6.5）| 类扫描新增的 dialog record `source` 必须 == `"app_relationship_tree_added_class_scan"`，便于追溯/统计 | HARD |
| **Phase 1.6 新增节点 construction_mode 合法**（v6.5）| 必须是 `"layout_xml"` 或 `"code_only"` 二选一 | HARD |

任一 ❌ → skill 失败，向用户报错。写回 `spec/toolkit-fact-tree.json` 覆盖。

---


## 3. 输入、输出与编排边界

输入是同一项目原生事实树、source-index、选定源、page spec、可选 feature-index；输出仍原地 toolkit-fact-tree.json。每个源码/脚本补充阶段及自检都要真实执行，不能拿文件存在替代完成。

原 run_all_phases/scan_popup_classes/calibrate_nodes/compute_navigation_contract 的源解析分支未证明支持 Swift 时，不用其源扫描分支；按上述相同阶段以 Source 与原四图产生同构材料。编排优先使用可用注册角色；不支持角色按同一协议顺序执行，不另开任务假装完成。下游通用结构自检与原严格度仍保留；真实缺口不能靠“适配”绕过。此专项不代表新增了 SPEC 全局门。
