> **iOS 源输入**：读取 Swift/Objective-C、SwiftUI/UIKit、Xcode 工程及原生资源；实际源构建与设备观测依赖可用的源平台环境。鸿蒙侧构建和验收保持原流程。源侧操作详见 `a2h-spec/references/native-input.md`。

# Phase 4 回放执行器设计（#11，v2 2026-07-22 审核修订版）

> ⚠️ **本文是设计规范(理想架构);实际怎么跑 + 脚本(replay_exec.py)用法 + 血泪教训看 [phase4-replay-run.md](phase4-replay-run.md)**。
> 实现经 2026-07-23 大量迭代(双引擎判位/同构去重/dialog当场测/签名判变化/尊重树outcome标记),以运行手册和脚本注释为准。

定位：**编译/执行/判定三段的第二段**——`replay_plan_hmos.json`（phase4-replay-compile.md **v2**，两文档互为契约，
字段增删必须同步改）的纯机械解释器。与iOS侧同宗：**LLM 坐庄，机械打工**。
**一笔画只是"到页方式"；到页后的行为对账仍是本执行器的第二职责（§4）——只换导航、不丢职责。**

## §0 三条铁律（验收标准）

1. **零 app 常量**：一切 app 数据来自 replay_plan / CLI。**验收闸覆盖 import 闭包**（不止执行器单文件——
   hardcode 搬进被 import 的模块同样算违规）：闭包内每处中文串命中必须属于 ①注释/日志 ②**通用语义词表
   数据文件**（关闭词/动词袋这类跨 app 语义常量，从代码剥离成数据文件，app 域词如"PPT/模板/会员"必须
   剔进 plan——现存反例：hmos_capture_page_e2e 的 VERB_BAG 混入了 app 域词，复用前先剥）。
   换树冒烟：Fitness 计划 dry-run 必须能跑、产诚实弃权账。
2. **判读制**：只产观察与证据包，永不判对错、永不写 fix 单。判定归双派 judge。
3. **弃权哲学**：只跑 happy path，偏离即带完整现场弃权；弃权必须廉价（秒级）且必须留痕（零静默跳过）。

## §1 复用点名（硬性规定，禁止重新实现）

| 层 | 复用物（实物路径） | 方式 |
|---|---|---|
| 设备层 | `blackbox_explore.DeviceAdapter`（adb/hdc 双端已封装：tap/swipe/back/screencap/page_signature） | **直接复用，禁新写设备层**；dumpLayout→cat 直读优化改在 DeviceAdapter 公共层，不在执行器私藏 |
| 元素提取 | `blackbox_explore.extract_clickables_hmos`（含子节点文字/rid 下钻） | 直接复用 |
| 匹配 | `hmos_capture_page_e2e.five_match`（B.0.5 五级降级的唯一实现） | **同一函数 import，禁重抄**（两部梯子=同一事实两种判决）；降级命中记 `matched_by`+`text_mismatches`（P1 素材，见 §5 表） |
| 证据/守卫 | `evidence_pack / guard_after_tap / foreground_state / dump_retry / tap_and_settle / wms_overlap_evidence`（均在 hmos_capture_page_e2e） | 抽成共享模块后 import（抽取时做 §0.1 的词表剥离） |
| 计划数学 | `walk_exec` 的 `precompute_positions / simulate_stack / subtree_end` + escalate/resume 状态机（~150 行纯计划运算） | **抽共享模块 import**（不是"移植合同"——重抄=漂移）。★2026-08-14 审计实核：`replay_exec.py` 现为**独立实现、未 import**——本合同尚未兑现。下次动这块时先抽共享模块再改，别把本行当既成事实引用 |
| 建态 | `run_scenario_with_verify.py` + `scenario_run.py`（凭据 `spec/scenarios/creds.local.json`，exit 词表见 §7） | preflight **只调它**，绝不自建登录执行 |
| 回位/判位语义 | walk_back_to 的 count 模型/下沉栈、walk_whereami 的双闸+weak 判定 | **语义平移、代码不搬**（无 activity 探针，判位信号换 pagePath，见 §3） |
| 收尾账 | walk_ledger / walk_finalize 的"机械收尾不许降级成自觉"语义 | 平移：执行器产出必须被机械闸对账（§8 验收） |

## §2 动作原语集（守卫内置，[Tn]=真机教训编号）

- `coldstart`：force-stop → start → **轮询根哨兵**（冷启时长是变量）[T6]
- `tap(step)`：重新 dump[T1] → 模态检查（§3）[T3] → `five_match(step.match)` 定位 → 点击 →
  按 `wait_budget_s` 轮询到达（§3 判位）→ **到达验证通过才截图入账**，否则存 `__<verdict>` 证据[T2]
- `input_text(step)`：按 `step.input.field_type`（TextInput/TextArea）定位[T4] → 聚焦 → inputText（中文直填）
  → **IME 确实开着才收**（§3 IME 判据；误发 keyEvent2=假 BACK 退页[T5]）
- `back`：**下沉栈守卫**（栈空不按）[T9] → 按后 dump-diff 验证，变则弹栈
- `close_dialog`：按 `step.return.recipe`（编译期从树 dialogs 目录+iOS真值产：取消键文本/关闭键 rid）→
  fallback BACK → BACK 无效（autoCancel=false 类）→ 弃权交 LLM。**绝不点语义确认键**（多态共享弹窗铁律）
- `reconcile(step)`：行为对账段，见 §4
- `verify / probe / skip`：计划步类型全集与编译器 action 枚举一一对应（对账闸依赖步数守恒）

安全双保险（每次 tap 前）[T8]：`safety != normal` → SKIP_SAFETY；trigger 命中 `plan.safety.blacklist`
→ SKIP_BLACKLIST（防计划标注洞）。

## §3 感知原语（语义字段优先，几何仅兜底——2026-07-22 审核修订）

鸿蒙 dumpLayout 自带强语义字段（实测确认），**禁用几何启发式主判**：

- **判位（到达判定）**：三级——①窗口根 `pagePath` / `abilityName` 命中 expect（mResumedActivity 的
  鸿蒙等价物，主信号）②`expect.sentinel[]` 文本命中（次级，多 NavDestination 同 pagePath 时消歧）
  ③dump 文本集显著变化（weak，降置信记录）。`plan.ignore_nodes[]`（splash 类永驻节点）全程排除。
- **模态检测**：`type=="Dialog"|"Popup"` + `hostWindowId` 分窗 + `zIndex`；层叠证据用
  `wms_overlap_evidence`（hidumper WMS，现成）。处置三分：计划内 dialog（当前步 expect.kind=dialog）
  → 正常业务；命中 `plan.dismissible_recipes[]`（首启同意类，编译期从树 dialogs 目录产）→ 机械关；
  计划外 → `unexpected_modal` 证据包弃权交 LLM（**不硬关**——弹窗语义只有 LLM/判定能读）。
- **IME 检测**：dump 窗口列表里**输入法窗口的 bundleName 存在**即开（结构语义），键盘皮肤特征仅兜底。
- **判活探针**（异步预算耗尽）：两次 dump 间隔比对，变=alive 延一次预算；静止=meltdown 语义弃权
  （静止前绝不按 BACK）。

## §4 行为对账段（FATAL-1 修订：一笔画的第二职责，契约与页粒度完全一致）

首达节点到达验证通过后，执行 `reconcile` 步（编译期按三源录制真值给出**本页元素清单**，
三源皆无记录的元素不进清单——`untested_skipped(no_recorded_oracle)` 既有铁律不变）：

- 逐元素：定位（five_match）→ tap → 观察记录（outcome/landed/toasts/evidence 截图）→ 回位（下沉栈/close_dialog）
- **只记观察不判定**（判读制）；oracle 对账归 judge
- 安全：清单元素同样过 §2 安全双保险；`plan.safety.blacklist` 词与 destructive 边在编译期已剔除
- 产出：`capture_manifest.per_page.<page>.behavior_observations[{trigger_text,rid,center,outcome,landed,toasts,evidence}]`
  + `observation_notes[]`（现场才知道的异常）——**与 sub-agent-batch-prompt.md 的 capture role 契约逐字段一致**，
  judge/B 审核员零改动消费

## §5 弃权=产出：verdict → 既有 finding kind 路由

| verdict | 证据包 | judge 出单 |
|---|---|---|
| ABANDON_no_match（五级全 miss） | 截图+dump+期望 vs 实际 clickables | trigger_missing_hmos P0 |
| **降级命中**（五级第 2-6 级中） | matched_by + text_mismatches | **trigger_text_mismatch P1**（exit 21 语义，照常继续走） |
| NO_NAV / CLICK_NO_EFFECT | pre dump + post dump + post 截图（★与实现对齐 2026-08-14：tap 时刻 pre **截图**不存在，judge 双图闸的"前图"用源页到达交付图，见 judge §排除项④）+ 带外数值 delta（`numeric_delta`） | nav_failed hint=button_dead |
| unexpected_modal | 模态截图+dump+WMS 证据 | 判定读图定 kind |
| escaped_app | 自动拉回（guard_after_tap）+记录 | SKIPPED / system_ui_expected→confirmed |
| app_crash | faultlog 采集 | CRASH P0 |
| 异步超时（判活后静止） | meltdown 证据包 | nav_failed/产品级卡死候选 |
| 建态失败（§7 映射） | scenario artifacts | P0 + blocks_subtree_propagation |

**阻塞传播与补采路由（MAJOR-6 修订）**：blocking 失败 → 计划 from/to 图算下游 → `blocked_by` 快跳留痕。
被快跳的 `settles_capture` 页**两条补采路**：①本轮 → 进**页粒度补采队列**（主会话在边界窗口用
`hmos_capture_page_e2e` 单页补——每页独立 reach_path 重放，不受断边连累，这正是页粒度兜底的存在意义）；
②跨轮 → 写入 `retry_edges`（phase4-dispatch 既有 carry-forward 契约），**编译器增量输入除 `_incr_plan.to_verify`
外必须并集 retry_edges**（compile 规范 v2 已同步）。快跳绝不等于放弃覆盖，两条路都有账。

## §6 LLM 兜底合同（共享 walk_exec 状态机，四种接手）

段内弃权 → exit 30 + `executor_state.json`。LLM 接手四支（目标是与 walk_exec 共享同一状态机模块——★现状为语义对齐、代码独立，见 §1 计划数学行的实核注记）：
`--resume` / `--resume --assume-at <node>` / `--skip-step N --skip-reason`（自动阻塞传播）/
`--mark-step-done N --assume-at <node>`（LLM 手工完成该步后续走——input 类边最常用）。

## §7 preflight（全机械，建态委托 scenario 管线——MAJOR-5 修订）

1. 干净重启[T6] → 根哨兵轮询 2. 网络探测：`plan.preflight.network_probe`
3. **态检测**：`plan.preflight.state_signatures` 命中 → `state_ok_existing` 跳建态
4. 未命中 → **调 `run_scenario_with_verify.py`**（trip scenario_chain），exit code 直接映射四态：
   0→`state_ok` / 20→`credentials_missing`(NEED_HUMAN，附 --save-creds 指引，**不算产品坏**) /
   10→配方坏派 scenario-builder（既有路由）/ 40|50→`state_broken`（**P0 + blocks_subtree_propagation
   登录墙后全部节点**，继续走登出态可达段）。
   **分工线**：建态=scenario 管线的事；"登录 UI 作为被测边"只存在于 trip_1（登出态）计划的普通边里，
   preflight 不重测登录 UI。
5. 计时插桩：t_locate/t_tap/t_wait/t_back 逐步落账[T10]。效率基线：干净边 2.25s/边（实测），
   BACK 验证 ~2.1s/次（dump-diff，无 0.04s 探针），146 步机械段目标 ≤15 分（异步边另计）。

## §8 验收清单（实现完成的定义）

- [ ] 零 hardcode：grep 闸过 **import 闭包** + Fitness 换树 dry-run 产诚实弃权账
- [ ] **行为对账契约**：per_page.behavior_observations 字段完整，judge/B 审核员零改动消费通过
- [ ] AIPPT trip_2 实跑：创作流主链全通、37 首达节点覆盖显著、零误标截图、耗时账落盘
- [ ] 安全：破坏性边零接触全留痕；共享 VIP 账号态前后校验一致
- [ ] 判读制：产物零判定字样；**机械收尾闸**对账（步数守恒:执行+跳过+阻塞=计划实数;每个 settles_capture
  有归宿:verified 截图/补采队列/retry_edges 三选一——防"收尾降级成自觉"复发）
- [ ] 复用核查：five_match/DeviceAdapter/scenario/计划数学模块均为 import 关系（diff 可证无重抄）

尾注[T1-T10]（v1-v3 真机教训）与资产复用判词详 memory vv-hmos-replay-landing 及 2026-07-22 审核报告。
