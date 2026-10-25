> **iOS 源输入**：读取 Swift/Objective-C、SwiftUI/UIKit、Xcode 工程及原生资源；实际源构建与设备观测依赖可用的源平台环境。鸿蒙侧构建和验收保持原流程。源侧操作详见 `a2h-spec/references/native-input.md`。

# 端到端链路（standalone 主线）+ 被编排调用附录

> 从 SKILL.md §6 + §11 拆出。仅在用户问"完整链路"或被外部调用方集成时 Read。
> **本 skill 是独立自闭环单元**：单独调用即完整"验→修→重编重装→再验"循环；
> a2h-verify 等编排器只是众多调用方之一（见文末附录）。

## 完整链路（端到端，用户一条指令触发）

下面是用户一条指令（"跑视觉对比"）触发后的完整链路：

```text
[历史源平台示例：不适用于 iOS，不可执行。iOS 源设备/构建按本文件适配及 native-input 协议；目标 hdc/hvigor 检查仍须实际执行。]
用户: "跑视觉对比"
  │
  ▼
arkts-visual-verify (本 skill)
  │
  ├─ Phase 0: round_budget.py begin [--budget N]（默认 3 轮，冻结 started_at_round）
  │
  ├─ Phase 1.0: 跑 check_prereq_freshness.py spec/toolkit-fact-tree.json --source <ios_src>
  │    NEED → 调 $ios-fact-tree（统一调度器：判架构 XML/Compose/混合 → 分发生成器 → 自带闸）→ 复跑 gate 确认 PASS
  │    （前置自动补齐是自闭环的一部分：缺什么就地生成，不假设编排器已备好）
  │
  ├─ Phase 1.1: 前置条件检查（adb/hdc/模拟器/包 + 新鲜检查 --rebuild --skip-if-fresh：
  │             Step 6.8 打过戳→秒过；无戳→重编；构建失败→自动接 hmos-fix-build-errors）
  │             + 三级探针：REQUIRED 自动补齐 / UNIT fail-fast / OPTIONAL 降级告知
  │             （维度启用/降级表第一屏打印，见 phase1-prepare.md Step 1.1.f）
  │             a2h-spec 产物整体缺失（exit 3）→ 自动调 $a2h-spec 补齐 → 复跑探针
  │             （只自动调一次，仍缺则降级继续；部分缺失不触发，直接降级）
  ├─ Phase 1.2: 构建页面队列 + 按层级排序（用 scripts/build_page_queue.py）
  ├─ Phase 1.2.5: 可达性预分类 → { public, login_walled, data_dependent }
  ├─ Phase 3: (a) 准备 spec/fix/round-N/ui/ 目录骨架
  │              从 _state.yaml 读 N（无则 0）；carry forward disposition
  │             (b) 准备 iOS 截图缓存目录 + manifest 一致性自检（v2）
  │              抓 app_fingerprint（versionName）一次留用
  │
  └─ Phase 4: 逐页扫描 FOR EACH page IN queue (pages + fragments + dialogs) —— 不重截、不循环
       │       全量遍历：priority 决定顺序，不决定测不测
       │
       ├─ Step 4.-1: 非 public 页 → 调 arkts-scenario-runner
       │     │  ★ iOS baseline 已存在 → 跳过 iOS 源端 scenario
       │     │  ★ v2：scenario 未在 page_scenarios.json 声明 → 写 CRASH_*_scenario_required_*.md（不 skip）
       │     │
       │     ├─ run_scenario_with_verify.py login {ios|harmonyos}   ← 包装脚本，禁直跑 scenario_run.py
       │     │     └─ iOS baseline 已存在时仅跑 harmonyos
       │     │     └─ auto 策略: 有缓存 prefs → static 秒启
       │     ├─ run_scenario_with_verify.py upload_image harmonyos
       │     └─ 读 result.json，success=false → 写 CRASH_*_scenario_failed_*.md，next page
       │
       ├─ Step 4.0: 从首页导航到目标页（uitest dumpLayout 拿坐标）
       │     └─ 找不到 target → 写 CRASH_*.md (nav_unreachable_*)
       ├─ Step 4.1: 截图
       │     │  ★ iOS 源端：baseline png 已存在即复用，缺失才 adb screencap
       │     │  HarmonyOS 端：永远 hdc snapshot_display 重截
       ├─ Step 4.1.2: capture_mode 分流
       ├─ Step 4.1.3: 长页面分段 + 拼接（long 模式）
       ├─ Step 4.1.4: H5/WebView 验证（web 模式）→ url 不一致写 URL_*.md
       ├─ Step 4.1.5: 崩溃检测 → 崩溃写 CRASH_*.md (app_crash_on_*)
       ├─ Step 4.2: 多模态对比 → differences[] + siblings + icons + missing/extra + scroll_needed
       ├─ Step 4.3: 差异分类（仍走 §1.1.1 铁律）
       ├─ Step 4.4: ★ 把每条差异写成 spec/fix/round-N/ui/{kind}_*.md
       │           （一差异一文件；按 schema 派 ID、写 frontmatter、写 5 sections）
       │           （carry forward disposition；本步骤不动 .ets — fixer 在 Phase 6.6 统一跑）
       └─ Step 4.5: 落 progress.json.pages[X]（status / rounds++ / fix_files[]）
  │
  ▼
Phase 6: 写汇总 + 自检 + 派 fixer
  ├─ Step 6.1: spec/fix/round-N/_index.md
  ├─ Step 6.2: spec/fix/round-N/_summary.md（页面维度 + checks performed + Top10）
  ├─ Step 6.3: spec/fix/round-N/_delta.md（round-0 跳过；与上轮 diff）
  ├─ Step 6.4: 更新 spec/fix/_state.yaml.last_verifier_results.visual-verify
  ├─ Step 6.5: 跑 schema §十 自检脚本（不通过 → 重写 → 仍不通过升级用户）
  ├─ Step 6.6: ★主动派 visual-fixer★（本 skill 闭环修复；派发前先 --clear-stamp 清新鲜戳）
  │    `spawn_agent(agent_type="visual-fixer", task_name=f"visual_fixer_round_{N}", message=fixer_prompt)`
  │    visual-fixer 读 ui/*.md + sbs 截图，按 page_id 整体诊断修 .ets
  │    修完代码落盘即返回（不动 git / 不重编 / 不复测）
  ├─ Step 6.7: 派 visual-fixer-reviewer 反摸鱼质检
  ├─ Step 6.8: ★fix 后置构建（构建锚点①）★ —— 顺利出包+装机才算过
  │    auto_install_artifacts.py --rebuild → 成功打新鲜戳（下轮 Phase 1.1.d 秒过）
  │    构建失败 → 自动调 $hmos-fix-build-errors 修到出包 → 复跑装机
  │    它也修不动才升级用户（每构建点最多自动修一次）
  └─ Step 6.9: report.md **必须用 render_report.py 机械渲染**，禁止主代理自由总结
  │            （事故：round-6 报告里"覆盖 6/20"和"三轮闭环已完成"并排躺着——
  │              数字诚实、结论造假，而下游读的是结论那句）
  │
  ▼
Phase 6.4: 整轮硬闸 assert_round_complete.py（**必跑**，产 spec/fix/round-N/_run_state.json）
  expected_trips 从iOS基线**实时枚举** → 每 trip 跑 assert_replay_artifacts
  + assert_gap_ticket_coverage → 汇总成 ROUND_VERDICT
    0 CLEAN / 10 有产品差异 / 11 有债 / 20 缺 trip / 21 缺页没出单 / 22 用了陈旧产物
  ⚠️ 不跑它 → 下面的 6.5 直接 exit 2 拒绝给结论（"闸没人调"这条老路已封死）
  │
  ▼
Phase 6.5: 自持循环闸（本 skill 唯一的循环出口）
  跑 round_budget.py next，按退出码路由：
    0  → 已自增 round，回 Phase 1（修改已在 Step 6.8 上了设备并打戳，
         Phase 1.1.d 见戳秒过；无戳则兜底重编——任何路径下截图前包必新鲜）
    11 → CONVERGED —— 现需 open==0 **且** debt==0 **且** 整轮闸==ALIGNMENT_CLEAN
         （仍需显式 --early-exit-on-clean 才启用）
     2 → 缺 spec/fix/round-N/_run_state.json：本轮没跑 Phase 6.4，拒绝给结论
    10 → 本次调用预算用尽 → round_budget.py end 打印终态契约（SKILL.md §5.2）：
         VERDICT + 轮次轨迹 + 进展三态诊断 → 转述给用户
  │
  ▼
终态（standalone 下这就是完整答案）:
  还有 open？→ 用户再说一次"跑视觉对比"即可续跑（差值预算天然累计 3→6→9）
  停滞？→ 按诊断查 _delta.md / §6 尝试史，判是否撞上修不动的项转人工
```
**终止条件（本 skill 自持，`scripts/round_budget.py` 机械判定）**：
- 本次调用轮数用尽 → BUDGET_EXHAUSTED（默认 3，`--budget` 可覆盖）—— **主要出口**
- open finding == 0 → CONVERGED，但**默认关闭**，需显式 --early-exit-on-clean
  · open = disposition ∈ {null, partial}；已裁决终态仍 carry-forward 留痕但不计入
  · 默认关闭的理由：漏检会伪装成 open==0。「跑满预算」失败只是费时间（显性），
    「提前收敛」失败是静默假阴性——看起来成功、实际遗留问题，还会误导下游门控。
    宁可多跑两轮。open 计数仍每轮打印，但只作诊断，不作控制流。
- HAP 构建失败（Step 6.8 或 Phase 1.1.d）→ 先自动调 hmos-fix-build-errors 修到出包；
  它也修不动 → ABORT（禁止拿旧包继续截；「重编跑了」不算数，「顺利出包」才算过）
- visual-fixer 自行升级（修不动） → 暂停循环交给用户

**预算是差值不是绝对阈值**：`begin` 冻结进入时的 current_round 为 started_at_round，
判据是 `current_round - started_at_round + 1 < budget`。于是多次调用天然累计——
调用 1 跑 round 0/1/2，调用 2 从 round-3 起再跑 3 轮，累计 6。
**累计是算式的自然结果，不靠任何「允许累计」的规则授权。**

**关键约定（必读，2026-05-23 反转）**：
- **本 skill 自带 fix 闭环**：Phase 6 末尾主动派 visual-fixer 处理 round-N/ui/*.md
- visual-fixer 是**专属 agent**（不是通用 a2h-fixer）：强制读 sbs 双端对比图做多模态诊断，按 page_id 整体修 ArkUI 源码
- visual-fixer 修完代码落盘即退，不动 git、不重编、不复测；**重编 + 重装由本 skill 在 Step 6.8
  （fix 后置构建）立即执行，出包成功打新鲜戳，下轮 Phase 1.1.d 见戳秒过、无戳兜底重编**——
  每个 fix 批次恰好编译一次（2026-08-12 构建点重排）。历史教训：更旧的版本把重编委托给
  a2h-verify，单独调用时整条断掉——下一轮截的是旧二进制，修改永远上不了设备，
  这是「跑 20+ 轮仍不收敛」的真正根因
- **本 skill 自持 current_round 推进**（`round_budget.py`，每次调用默认 3 轮）；`_state.yaml` 轮次字段单写者
- **本 skill 不删除旧 round-(N-1)/ 目录**，git 永久保留所有历史轮次
- **disposition** 字段由 verifier 单一裁判（2026-05-24 v4 起 visual-fixer 完全不写 disposition）；本 skill 负责 carry forward 上轮值 + 下轮重测后写 `fixed` 升 RESOLVED；用户对话豁免可设 `manual_review`（详 fix-file-schema §五）

**用户全链路只需做的事**：
1. 启动两个模拟器，装好 App（或让本 skill 用 `scripts/auto_install_artifacts.py` 自动装）
2. **一次性**建凭证档：`scenario_run.py --save-creds --device <ios|harmonyos> --package <pkg> --phone <手机号> --code <万能码>`（只写 `spec/scenarios/creds.local.json`，**与端无关、不实跑 login、不驱动设备**；两端账号不同各存一份）。之后所有场景/visual-verify 自动复用。迁移产物已带 `spec/baseline/dev_info.json`（契约参考文件）时，手机号/万能码可直接从中取值建档，这步免人工。
3. 说"跑视觉对比"

> ⚠️ **顺序铁律**：login 的首次**实跑**由 Phase 2（iOS trip_2 基线）触发，落在**iOS**端——**不要**为了"录码"先 `--device harmonyos` 实跑 login（用 step 2 的 `--save-creds` 录码即可）。iOS全量基线（对齐真值）必须先于一切 HMOS 设备交互；HMOS 端 scenario 被 `run_scenario_with_verify.py` 顺序闸（exit 60）拦在iOS基线完成之后。

---

## 附录：被外部编排调用时的差异（a2h-verify CHECK-6 / spec-evolver Step 11 / device-smoke 等）

**几乎没有差异**——这正是自闭环设计的目的。调用方与 standalone 用户在本 skill 眼里是同一种角色，
统一走 SKILL.md §5.3 调用方契约：

| 环节 | 调用方要做的 | 调用方**不要**做的 |
|---|---|---|
| 触发 | $arkts-visual-verify，可传 `--budget N`（spec-evolver 的 `retry_policy.max_rounds` 映射到此） | — |
| 循环中 | 无（Phase 1-6.5 全自持：重编重装、派 fixer、轮次推进都在内） | 不代跑 fixer、不干预轮次 |
| 结束后 | 读 VERDICT + `_summary.md`，映射成自己的结论（如 CHECK-6 的 PASS/FAIL） | 不写 `_state.yaml` 轮次字段 |
| 续跑 | 直接再调一次本 skill（差值预算天然累计） | 不自增 current_round |

映射建议（a2h-verify CHECK-6 为例）：`CLEAN_AT_EXIT` → PASS；`OPEN_REMAIN` / `BUDGET_EXHAUSTED`
且进展诊断为"有进展" → 再调一次；"停滞" → FAIL 转人工。

git 边界：本 skill 与 visual-fixer 都不动 git；add/commit 归用户或上游调用方统筹。
若 dt-verifier 在同一全局轮也产了 feat 单，round-N/ 顶层 _index.md 的合并由编排方负责（本 skill 只写自己的段）。
