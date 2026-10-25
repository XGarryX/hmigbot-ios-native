# Phase 4 回放计划编译器（鸿蒙一笔画·编译期规范，v2 2026-07-22）

> ⚠️ **本文是设计规范(理想架构);实际怎么跑 + 脚本用法 + 血泪教训看 [phase4-replay-run.md](phase4-replay-run.md)**。
> 实现(compile_replay_plan.py)经 2026-07-23 大量迭代,具体做法(确定性哨兵/尊重outcome标记/dialog移进reconcile/
> 同构去重/chrome剔除)以运行手册和脚本注释为准,本设计稿可能滞后。

> **契约互引**：本规范与 phase4-replay-executor.md **v2** 互为契约——执行器消费的每个字段必须在本
> schema 里有定义，任何一侧增删字段必须同步改另一侧（2026-07-22 审核抓出 9 处脱节后立此规矩）。

定位：**编译/执行/判定三段分离**的第一段。LLM 当编译器——散文真值（死因/toast/动态性注记）的唯一
合法消费者在这里（用户裁决：散文不结构化、机器不读散文；机器只吃本规范产出的计划）。
执行期（纯机械）与判定期（双派并行，§4.A.2）只消费 `replay_plan_hmos.json`，永不回头读树的散文。

## 输入（全部实物，禁引用不存在的字段）
- **树**（唯一权威源）：`spec/toolkit-fact-tree.json`——runtime 结构化字段（status/control/landed/
  waited_s）+ 散文（not_reproduced_in[].reason / deferred_in / note）
- **走序**：`$EW/walk_plan.json`——数字规格**只准引用它的实数**（当前 146 步/73 边/70 tap；
  禁手抄禁记忆,历史教训:曾误传 108 步）
- **增量集**（round-2+）：`spec/visual-verify/_incr_plan.json` 的 `to_verify`（Step 4.A.0 产出）
- **鸿蒙源码**（破坏性闸用）：工程 `entry/src/main/ets/`
- spike 既定事实（scratchpad 会话产物,结论已固化于此）：中文可直接 inputText（免 ASCII 绕行）；
  toast 进 dumpLayout 树（tap 后快 dump 可验）；splash 节点 `PPT引擎启动中` 永驻 dump 须入忽略集；
  冷启时长变量 → coldstart 步必须轮询哨兵。

## 输出 schema：`$EW/replay_plan_hmos.json`（v2——计划级字段 + 步级字段）
```jsonc
{"compiled_from_tree_hash": "<树文件 sha256>", "pipeline_version": "<SKILL.md 顶部常量>",
 "verify_scope": "full|incremental",
 // ── 计划级(执行器 §1/§3/§7 消费,v2 补齐——此前 9 处脱节) ──
 "app": {"bundle": "...", "ability": "..."},          // derived_config 来
 "safety": {"blacklist": ["取消订阅","一键退款","..."]}, // plan_edge_walk 词表+项目规则,防标注洞双保险
 "roots": [{"node": "HomeActivity", "sentinel": ["..."], "pagePath": "pages/..."}],
 "preflight": {"network_probe": ["<须后端加载才出现的文本类别>"],
               "state_signatures": {"trip_2_logged_in_vip": ["<账号行模式>","<VIP标识>"]},
               "scenario_chain": ["login"]},          // 建态委托 scenario 管线(执行器 §7),编译器不产 login_segment
 "dismissible_recipes": [{"mark": ["<弹窗识别文本>"], "close": {"text": "同意并继续"}}],  // 树 dialogs 目录来,首启同意类
 "ignore_nodes": ["<splash 类永驻节点文本>"],          // 基线 dump 差集发现,计划级(步级 expect.ignore 废止并入此)
 "steps": [
  {"step": 12, "from": "MineFragment", "to": "AboutUsActivity",
   "action": "tap|back|input_text|close_dialog|coldstart|reconcile|verify|probe|skip",
   //          ↑ v2:补 reconcile/verify/probe/skip——walk_plan 实有步型全集,步数对账闸依赖守恒
   "input": {"field_type": "TextInput|TextArea", "text": "人工智能与教育"},   // v2:补 field_type(按类型定位,禁文本标签)
   "match": {"primary": "关于我们", "source": "runtime|static",
             "skip_text_level": false, "disambiguate": "bounds|type|none"},
   "wait_budget_s": 5,                             // runtime.waited_s×1.5 向上取整;无实测默认 8
   "expect": {"kind": "page|dialog|toast|system_ui_expected|none",
              "pagePath": "pages/AboutUs",          // v2:判位主信号(窗口根自带,mResumedActivity 等价物)
              "sentinel": ["稳定文本1","稳定文本2"]},
   "on_ios": "confirmed|no_truth",
   "return": {"kind": "back|close_dialog|tab_retap", "steps": 1,
              "recipe": {"text": "取消"}},          // v2:close_dialog 关闭配方(树 dialogs+iOS真值来;无则 BACK)
   "safety": "normal",
   // reconcile 步专用(v2,行为对账段——每首达节点一步,元素清单按三源录制真值,三源皆无的元素不进清单):
   "elements": [{"trigger_text": "检查更新", "rid": "...", "oracle_source": "functional_checks|blackbox_behavior|declared"}]
  }]}
```

## 编译规则（审核修正后定稿，逐条有出处）
1. **破坏性闸（FATAL-1）**：`safety ∈ {stop_at_dialog, skip_unless_verified, confirm_risk}` 的边，
   编译期必须**读鸿蒙 ArkTS 源码**确认该 handler 只弹窗不执行（两侧连同一真后端 dev-api.whiap.cn，
   赌错=唯一 VIP 账号不可逆损毁）。源码确认不了 → 该边 `deferred_destructive` **不进机械计划**，
   积单交人。`skip_destructive` 边永不编译（作品删除类,无确认门）。
2. **死因分流（FATAL-3 修正）**：树散文死因由编译 LLM 现读现分——**平台门**（SDK/appops/厂商服务，
   鸿蒙无同态）→ 不排步，记 `untested_skipped(platform_gate)`；**app 状态门**（登录/VIP/数据空）→
   编成"鸿蒙同态下也不应出现"对账步；**树缺陷/脏锚点** → 零预期，不排步。
3. **disproven 边不进计划**（树内 `disproven` 标记；与 plan_edge_walk 过滤同语义，代码独立）。
4. **动态文案**：编译期读判读注记（grounding 散文）识别动态边 → `skip_text_level: true`。
   静态边保持严格文本匹配——**鸿蒙真把文案写错要能被抓到**，匹配失败本身可能是 finding。
5. **toast 边**：iOS真值为 toast 语义的边 → `expect.kind=toast`，sentinel=toast 原文
   （spike 已证 dumpLayout 可验）。防 click_no_effect 假 P0。
6. **D-005 类平台转译边**（文件选择/系统分享）→ `expect.kind=system_ui_expected`：
   进系统 UI = confirmed 证据，不判 escaped_app。
7. **无真值步**：静态 label 排步，`on_ios=no_truth`，判定降置信；match.primary 为空
   （icon 无文本无 rid）→ `no_matchable_trigger` 弃权类，不带空配方上场。

## 两道闸（防漂移，回应"每轮重读散文=换马甲"的审核批评）
- **冻结复用**：计划带 `compiled_from_tree_hash` + `pipeline_version`。两者都没变 → **原计划复用，
  禁重编译**。任一变了 → 重编译并 **diff 审**：只人审新旧计划的差异行（死因分类翻转/边增删/预算变化），
  不整轮重审。
- **增量裁剪（2026-07-21 提速②；v2 补 retry_edges 输入）**：round-2+ 编译时裁剪范围 =
  `_incr_plan.json.to_verify` **∪ `retry_edges`**（上轮执行器弃权/阻塞快跳写入的 carry-forward，
  phase4-dispatch 既有契约——快跳绝不等于放弃覆盖，跨轮必须回来）——只保留"途经这些页"所需的
  最短段（含到达链），其余步剔除并记 `pruned_by_incremental: N 步`（留痕非静默）。
  哨兵页(sampling 触发)照编不裁且标加严。`degraded_full=true` 时禁裁剪。round-1 恒全量。
- **reconcile 步编译（v2，行为对账）**：每个 `settles_capture` 首达节点在其到达步后编一条
  `action=reconcile` 步，元素清单按三源录制真值（functional_checks / blackbox_behavior / 源码声明）
  生成；**三源皆无记录的元素不进清单**（untested_skipped 铁律）；破坏性词元素在编译期剔除
  （与 safety.blacklist 同源）。清单为空的节点省略 reconcile 步并留痕。

## 编译产物自检（编译 LLM 出计划前必过）
- steps 里每个 `match.primary` 非空或已标 `no_matchable_trigger`
- 每条 destructive 边有源码确认记录（文件:行号）或已 deferred
- 数字对账（v2 修订）：steps 数 = walk_plan 对应范围实数 − 剔除数（平台门/disproven/deferred/pruned）
  + reconcile 新增步数；三项分别列明，等式机械可验
- `{{`/`<<` 类占位符零残留
