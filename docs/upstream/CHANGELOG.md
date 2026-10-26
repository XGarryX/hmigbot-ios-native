# Changelog

本文件记录 hmigbot-CodeX（原 migbot-CodeX，2026-08 改名）（Codex 版 Android → ArkTS / HarmonyOS 迁移插件包）各迭代的关键改动。

## [version v1.6.1] - 2026-09-16

本次两趟 skills 同步（ArkTs-Core `version_915_codex`@d60f288 → @3f67862，PR #64 / #65）只做一件事：**把 v1.6.0 打包态（Nuitka 二进制）在真实工程里实跑暴露的路径与调用问题修干净**。23 个 skill 的 windows-x64 / macos-arm64 二进制重编，文本改动限于 4 个测试文件、`android-fact-tree/scripts/dispatch.py`、`phase1-prepare.md` 与 skill 级 CHANGELOG；`a2h` 运行时、`agents-codex/`、安装脚本未变。

### 🐛 修复 (Fixed)

* **视觉验证前置探针在 Codex 安装布局下误报（v1.6.0 升级提示里记的已知问题）**：`check_dimension_prereqs.py` 查兄弟 skill 时把 `~/.claude/skills/` 写死在代码里，查 agent 只认 `<agent>.md`，codex-adapter 改得了文档改不了拼法，标准的 `<project>/.agents/skills/` + `.codex/agents/*.toml` 布局恒报 UNIT 缺失 → 整条视觉验证 ABORT。现在 skill 根 / agent 注册 / 模板定位收进 `sibling_exec` 一处：`.claude` 与 `.agents` 两种布局都查、`.md` 与 `.toml` 都认、判「文件在不在」不判「我在哪」；11 个业务脚本改调它。本仓实测：Codex 布局不设 `SKILLS_ROOT` 四项全 ✅，**v1.6.0 的 `SKILLS_ROOT` 绕行不再需要**。
* **打包态兄弟脚本静默不被调用**：8 处 `os.path.isfile(<兄弟>.py)` 守卫在 `_entry.dist/` 里恒 False（那里没有 `.py`），feat 单 §2 永远 UNRESOLVED、截鸿蒙前的 baseline 安全闸消失、Phase 2 出口验收 / 黑盒证据检查跳过、事务复验一律 degraded——源码态跑不出来。守卫统一改 `sibling_exec.sibling_available`（冻结态按 `find_spec` 判编没编进去）。
* **6 个模块级脚本没有 `main()`**：`build_judge_input` / `build_spec_oracle` / `inject_spec_oracle` / `merge_capture_dirs` / `slice_batches` / `trip_end_slice` 逻辑写在模块级，打包态 `_entry <stem>` 取 `.main` 报 AttributeError、退出码 1（round-1 judge 组装实锤）。全部包进 `main(argv=None)`，CLI 参数、stdout、产物路径零改动。
* **`android-fact-tree/scripts/dispatch.py`**（唯一以源码发运的脚本）：`_resolve_skill` 只认 Claude 线目录 → 两种布局都查；调 `check_dimension_prereqs` 的 `[sys.executable, …]` 改借 vv 的 `sibling_cmd`（打包态 `sys.executable` 是不可执行的 libpython）。`arkts-scenario-runner/scenario_run.py` 与 `sibling_exec.py` 副本整文件同步为源侧。

### 🔧 优化 (Improved)

* **树覆盖闸不许模型自行放宽**（`app-relationship-tree` Step 1.0.7）：0915 实跑事故——两次 FAIL 后模型自写 `_phase_markers.coverage_gate_override` 以 0.84 / 0.95 过闸。现在 E1 / E3 分母剔除非 walkable 节点（abstract / external_entry / dead_code 等，另报 `nonwalkable_excluded`），E3 默认 100% → 92%；任一 `--min-*` 低于默认必须由用户在 `spec/tree_hints.json` 写 `coverage_gate_approved`，否则 `GATE: REFUSED`（exit 3）；实际阈值与批准人写进 `tree_coverage.json`。
* **打包契约变成 pytest 静态闸**：业务脚本不得再拼 `.claude` / `.codex` / `.agents` 路径或 `<agent>.md`、不得用 isfile 守 `.py`、不得 `[sys.executable, …]` spawn，`sibling_exec.py` 副本必须与 vv 这份逐字节相同；以后新脚本过这道 pytest 就天然兼容打包态，不用装成插件实跑才发现。

### ✅ 校验 (Validated)

* `arkts-visual-verify/_tests` 638 → 683 例（新增 `test_env_neutral_0916` / `test_sibling_available_0915` / `test_entry_main_wrappers_0915` / `test_plugin_form_0915`）；`app-relationship-tree` 30 → 36；`android-fact-tree` 新增 `test_resolve_skill_0916`（6 布局矩阵）；`arkts-scenario-runner` 新增 `test_ad_dismiss_spawn_0915`。
* 影子根 Nuitka 真二进制：Codex 形状工程（显式根 / 无 env 自动发现）探针全 ✅、打包器 verify PASS=110 FAIL=0；每笔改动经独立子代理（Opus）验收后合入。本仓 `validate.sh` PASS。

### ⚠️ 升级提示

* v1.6.0 升级提示中「前置探针路径」的 `SKILLS_ROOT` 绕行可以撤掉；已设的不影响（显式指定时语义与输出一字不变）。
* 树覆盖闸变严：此前靠低阈值过闸的工程会转为 `GATE: REFUSED`，请把缺口清单与理由写进 `spec/tree_hints.json` 的 `coverage_gate_approved` 后重跑，不要改树里的 `walkability.status`。

> **二进制说明**：本版重编 23 个 skill 的 `scripts/bin/{windows-x64,macos-arm64}/_entry.dist/`（源提交 3f67862）；`bin/a2h-*` 运行时未重编，与 v1.5.2 一致。

## [version v1.6.0] - 2026-09-15

本次 skills 同步（来自 ArkTs-Core `version_915_codex`@1b3088d，经 PR #60 skills-sync/codex-53 合入，CI 修正 4ea40f5）有两条主线。**DT Verify**：`a2h-verify` 验证编排从 11 项收敛为 4 项、结论只覆盖本次实际验证的范围；`arkts-ut-verifier` 引入 Android 行为依据、oracle / 设计 / 生成三段 8 路并发，并封死测试「假绿」与统计失真。**Visual Verify**：让视觉验证「跑得更快、更少熔断、账目更真」——判定从「一趟一个 judge 扛 3.5 小时」改为按负载切包并行，工单跨轮结转 / 判定包合并 / 页账回写三处断点接通，鸿蒙回放与安卓边遍历经 0909→0913 十余趟真机回归逐条修通，源侧 23 个 shell 脚本全部 Python 化并修通打包线（Nuitka 二进制）校验。配套 `agents-codex/` 新增 9 个具名 agent（`arkts-ut-*` 5 个、`arkts-ui-*` 4 个，`.codex/agents` 由 22 → 31），`visual-fixer` / `visual-fixer-reviewer` 与 `app-relationship-tree` / `toolkit-fact-indexer` / `arkts-scenario-runner` 同步更新；`a2h` 运行时二进制与 `install.sh` / `install.ps1` 未变。

### ✨ 新增 (Added)

#### Visual Verify（arkts-visual-verify）

* **判定按负载切包并行（`slice_judge_input.py`）**：判定输入不再绑在采集切段上，而是按「页级产物必读 + 证据抽看 + 归属 escalations」的字节负载装箱，切成 K 个判定包、一包一个 judge 并行；关联组不拆、同屏别名原子、DFS 连续切，`--max-parallel`（默认 8）分波、`--max-packets` 硬上限，不写死页数。实测同一工程 round-0：trip_1 15 页 → 5 包、trip_2 20 页 → 7 包，判定段 33+20.5 分钟 → 约 10 分钟（对照此前单 judge 每趟 3.5 小时）。
* **判定包合并器（`merge_judge_packets.py`，J2.5 ①）**：K 份 `notes_partNN.json` 机械合并为 `batch_notes.json`。包齐闸（缺包 exit 21 不落盘）；list 拼接去重、dict 逐层递归并集、只有叶子标量冲突才记 `_merge.conflicts[]`（保 owner 包）；确定性。替代此前主会话手写合并（真实数据上当场崩过）。
* **工单跨轮结转脚本（`carry_forward.py`）**：文件名 = 工单 id 跨轮恒定，结转信息落 `carried_from_round` / `carried_rounds`；fixed / skipped / manual_review / problematic 不结转，其余原样带走不重置；幂等。根治此前 shell 片段结转的五处同根缺陷（改名破坏「文件名 = id」、pending 占位被清空、占位不被认、二次结转被自己前缀过滤、delta 按 id 差集虚高）。真实三轮数据：自检 FAIL 67 → 0、占位认出 0 → 4、丢过的 7 张单找回。
* **回放模式下游接线**：`build_batches.py` 新增 `android_edgewalk_partition`（无 chunk manifest 时按 `_trip_assignment.json` + 安卓基线 png 全集分批）；`mark_batch_done.py` 真写 `progress.pages` 页账；规范新增 J2.5 步骤。治干跑实爆的三处断点（Phase 3.5 从树重推 45/49 页、Phase 5/6 读不到回放 manifest 聚类为 0、`assert_run_success` 62 页假红）。
* **鸿蒙回放：计划外门放行 + 哨兵静态键**：目标未到 ∧ 认不出任何计划页 ∧ 不在登录门页 → 机械尝试一次门控件（首启隐私门只点「同意并继续」）；哨兵选词优先树里的静态文案并补「必要条件」，治「大纲页被认成 PPT 页」类误判。
* **鸿蒙回放：翻译对等性 + 门放行移植**：`--android-edges` 救回安卓已确认的边（安卓验证过的边鸿蒙一条不许静默放过，安卓被门拦住的边鸿蒙要去验门还在不在）；索引按 `(from, to[, trigger])` 分级避免取到兄弟边；`gate_pass` 从安卓侧移植到鸿蒙执行器，UI 词表单一真源。
* **安卓边遍历：熔断包自带诊断与决策菜单（`escalate`）**：熔断时给出有序 `options[]`（第一项为执行器推荐，每项带可执行 `cmd` / 适用条件 / 后果 / 覆盖损失），能机械收的不再熔断；哨兵消费 LLM 的 `verify_signal`、首启门边进 walk_0、尾部回栈剪枝、输入守卫出 `type` 步、分派表新鲜度闸。
* **判读债链路与跨趟隔离**：`walk_ledger.binding_debt` 三态为唯一定义（闸 / 驱动 / 收尾账共用）；`walk_finalize` 新增 §2.6 真拦；新动作 `settle_binding_debt`；BLOCKED 单默认 `binding_pending`；债池读不出来也判红。
* **树侧反哺与体检**：`tree_feedback.py` 只报不删（重复节点交树侧根治，`app-relationship-tree` Phase 1.7 折叠调用点节点）；边体检与契约闸（`guard_flags`）；auto 转场边编成 `wait` 步而非跳过。
* **调试截图三层治理**：`adhoc_capture` 通道 + fixer 看 / 判分离 + 收口自动归档；设备截图落点纪律与收口卫生检查（`check_scratch_pollution.py`），治客户实报的工程根目录截图污染。

### 🔧 优化 (Improved)

#### DT Verify（a2h-verify / arkts-ut-verifier）

* **a2h-verify 验证编排精简**：原 11 项检查收敛为 4 项——静态分析（CHECK-1）与 App 身份校验（CHECK-2）固定执行，视觉对齐（CHECK-3）、单元测试（CHECK-4）由用户按需选择；构建、安装及内部修复交由对应 verifier 完成。统一报告明确区分 PASS / FAIL / PARTIAL / DEFERRED / SKIP，结论仅覆盖本次选择和实际验证的范围，保留迁移完成信号与阶段用量上报。
* **arkts-ut-verifier 引入 Android 行为依据**：新增可选的 Android oracle 采集，提取可溯源的行为、分支与预期值；Spec 限定验证范围，Android 源码及已批准的平台差异决定功能行为与测试预期。补充未实现功能诊断和逐用例生成记录，缺入口、缺证据的条目显式列出。
* **测试生成与修复流程提效**：oracle、设计、生成各支持最多 8 路并发，单个 Feature 设计完成即可进入生成队列；增加公共设施预检、首批编译试跑和分批编译检查点。修复按文件所有权并行，覆盖生产实现、必要业务接线及测试更新，经独立质量复核、完整构建和设备复测后确认结果。

#### Visual Verify（arkts-visual-verify）

* **源侧 23 个 `.sh` 全部退役为同名 `.py`，与 Codex 产物合流**：行为等价，116 例 parity 全过后冻成 golden 接班；三平台同一套脚本，Windows 原生无需 bash / awk / grep / sed / jq / yq / sips。此前只在 Codex 产物里单独移植的 `render_report.py` / `assert_round_complete.py` / `check_reviewer_report.py` / `assert_gap_ticket_coverage.py` / `resolve_hmos_impl.py` / `smoke_one_page.py` / `device_triage.py` 回流为源侧正式工具并在 `cli-cheatsheet.md` 登记调用点，Codex 版不再与源侧分叉；文档里 153 行 shell 一行式改为 python 一行式或跨平台写法，`TRIP_ID=x bash …` 改为 `--trip` 参数。顺带消灭 `.sh` 里 7 处真 bug（4 处变量紧贴全角标点让闸「形同虚设」或静默吞退出码；2 处 `sort -u` 缺 `LC_ALL=C` 在中文页名上分母塌缩、覆盖率虚高；1 处债数拼接错）。
* **鸿蒙回放判位改「路径先验 + 同平台参考」**：`PAGE_REF` / `texts_pos` / `on_page_by_ref`，跨 resume 恢复 `PAGE_REF_RESTORED`；模糊匹配落错页不再判路由错；back 已在目标页不按（栈顶判据）。严格 A/B 验收通过，t2a 起 11/11 恢复生效。
* **回放 A/B 档 7 项**：rid-only 身份兜底按安卓屏上文案定位（`no_screen_identity` 归因）、数值形文案不当哨兵、探测步 kind 按目标类型推、续跑重建 DFS 栈、dumpsys 叠层弹窗识别（`overlay_dialogs`）进采集硬闸。全部零应用常量，每条先在 101 份真实 dump 上离线回放再落。
* **按趟真值**：安卓真值按趟隔离（别趟确认不救回、`confirmed_other_trip`）；`android_edge_lookup_how` 区分 label / pair / none 命中 + `label_gate`；遭遇账聚合；排除表子串匹配。
* **安卓瞬态页采集根治**：到达判定尺子从「uiautomator 等 idle」换成 `dumpsys activity top`（0.05 秒一次、不看动画），治「交付基线是首页图却账本 verified」；弹窗叠层采集并入。
* **关单口径统一**：四处「sbs similarity ≥ 0.95」统一为「页级 similarity ≥ 0.95 且无 CRASH → 页关闭、页内单随页关闭」；rubric 只豁免顶部状态栏与底部系统导航条，`overall_similarity` 必须由 `differences[]` 按 high 0.05 / medium 0.02 / low 0.01 扣分算出（清单空 = 1.0）。
* **工单账本**：fixed 单不再改名（`RESOLVED_` 前缀取消，改写三字段），`is_closed_ticket()` 按 disposition 判闭；`render_round_summary` 的 delta 改按 disposition 迁移并新增 `still_open`；BLOCKED 占位原名结转、不计 open、到达后出正常单并删占位；`render_finding_skeleton` 拒绝同轮同 id 重复出单。
* **`run_fix_self_check` 并入第 10 项**（原 Codex 侧 `check_fix_schema` 三条硬约束：`nav_failed` 必须 `android_verified` / BLOCKED 的 `blocked_by` 必须指向存在文件 / `FACT_TREE_INVALID_EDGE` 归属 `app-relationship-tree`），补 9 例正向测试并做突变自证。
* **golden / parity 路径无关化**：占位符 `<SKILLS>` / `<REAL_PROJECT>`，新闸「golden 里不许出现绝对路径」；真实工程用例恒在矩阵、夹具缺席显式 skip 并打出环境变量名，治「换台机器少跑 8 例、报告照写全绿」。

### 🐛 修复 (Fixed)

#### DT Verify（arkts-ut-verifier）

* **防止测试「假绿」与统计失真**：禁止弱化断言、删除用例或扩大 mock 来凑通过；按真实 Hypium 日志逐用例解析，分别报告原始通过率、设计验证比例和 AC 完成比例，未生成、忽略及未执行项保留在未验证范围中。
* **修正收敛与通过判定**：可处理问题清空但仍有真实验证缺口时标为 CONVERGED，仅全范围实际验证通过才判 PASS；修复新增入口后同步补测并更新旧分类，避免沿用 `no_entry` 等状态漏验。
* **隔离验证产物与状态**：UT 设计、报告、诊断和修复轮次统一归入 `spec/verify/ut/`，避免与 UI、视觉验证共享目录和状态造成干扰。

#### Visual Verify（arkts-visual-verify）

* **打包线（Nuitka 二进制）校验 24 例失败**：调度壳按 `main()` 必填参数个数分派，移植脚本写成 `main(argv)` 接列表 → 打包态收到单个字符串被逐字符迭代；兄弟脚本用 `sys.executable` spawn 在打包态指向不可执行的 libpython（Errno 13）；`arkts-ut-verifier/android_source.py` 的错误收口写在 `__main__` 里被调度壳绕过。修法：28 个脚本 `main(argv=None)` 缺省自读参数；兄弟 spawn 全部改 `sibling_exec.sibling_cmd`（开发态直跑 `.py`，冻结态自调 `_entry` 二进制）；`python_exe()` 冻结态判据改用 Nuitka `__compiled__` 标记；`run_scenario_with_verify` 的 skills 根改走 `ARKTS_SKILL_DIR`。同一打包线：visual-verify PASS=87 FAIL=23 → **PASS=110 FAIL=0**，ut-verifier PASS=5 FAIL=0。
* **鸿蒙回放假单归因四轮修复**（t1d → t1i 六趟真机验证）：`not_found + control_missing` 假账 17 → 0、rendered 3 → 14；wait 步开始前先判位，已站在别页立即 `AUTO_LANDED_ELSEWHERE` 不空等；熔断前把游标推到下一步、位置 = 本步落点。
* **安卓边遍历第三、四轮通用修复**（0910 真机 41 次熔断归因 10 条工具缺陷）：宿主上子 activity 的 `back_then_resume` / `renav_then_resume` 回位；node_sweep 链模式合并写回 `run_meta`、chain-mode 不再第二份破坏性词表；链趟 `walk_6_chain_sweep` 按 walk_0 步序重走首启链补欠账页。
* **路径反哺与账本收口**：dialogs 漏遍历、失败静默吞、运行时 rid 不许回填三处断点；命中链探针 + 三闸接线 + 整轮账本路径收口；顽固单判据扩域、跨轮次、阻断升级。
* **fixer**：行为类缺陷必须读到「行为承载体」的安卓源；回补丢失的安卓真值表 + 登录经验入册；工单加「必用参考」段（诊断命令直接摆进单里）。

### ✅ 校验 (Validated)

* `arkts-visual-verify/scripts/_tests`：490 → 638 例（设 `VV_PARITY_REAL_PROJECT` 时；不设 630 passed / 8 skipped），跑时 38.9 秒 → 24.4 秒；`app-relationship-tree` 30、`toolkit-fact-indexer` 23 不变。
* 真机 / 真实产物验收：t1f→t1i、t2a→t2c 共九趟鸿蒙回放严格 A/B；0913 全流程干跑 5h18m；0913–14 三轮修复闭环 open 73 → 31 → 14 作为归因与回归数据源；每笔改动由独立子代理验收后合入。
* 本仓 `validate.sh`：`VALIDATE: PASS`（skills checked: 99，agents checked: 31）；上游 publish-skills CI（windows-x64 + macos-arm64 build + verify / publish）在 `version_915_codex` 1b3088d 全绿。

### ⚠️ 升级提示

* **新增 agent 需重装**：`arkts-ut-*`（5）/ `arkts-ui-*`（4）九个具名 agent 随本版进入 `agents-codex/`，已有工程请重跑 `install.sh` / `install.ps1` 把它们装进 `.codex/agents/`（幂等）；`arkts-ut-verifier` 派发时角色缺失会明确报配置缺口而不是静默降级。
* **a2h-verify 交互变化**：进入验证前会先问「本次要执行哪些设备验证」（CHECK-3 视觉对齐 / CHECK-4 单元测试，可多选或都不选）；未选项记 SKIP、不参与结论计算，结论只对本次选择的范围负责。
* **UT 产物落点**：`arkts-ut-verifier` 的设计 / 报告 / 诊断 / 修复轮次改落 `spec/verify/ut/`，不再与 UI、视觉验证共用目录；旧工程续跑请以新路径为准。
* **脚本调用方式**：Codex 版本就以 `python3 …/x.py` 调用，本版不需要改；文档里 `TRIP_ID=<trip> bash run_scenario_with_verify.sh` 写法统一为 `python3 run_scenario_with_verify.py … --trip <trip>`（PowerShell 无 env 前缀语法）。`scripts/*.py` 是自动生成的 launcher，实际执行 `scripts/bin/<平台>/_entry.dist/` 下的二进制。
* **工单文件名规则**：fixed 单不再改名为 `RESOLVED_*`，闭合状态以 frontmatter `disposition` 为准；跨轮结转不再生成 `CARRYOVER_*` 文件，同一 id 跨轮恒定。旧前缀仍兼容读取。
* **关单判据**：页级 similarity ≥ 0.95（rubric 只豁免系统栏）且无 CRASH 才关页，页内单随页关闭；此前四处口径不一的 0.95 已统一。
* **前置探针路径（已知问题）**：视觉验证 1.1.f 三级探针 `check_dimension_prereqs.py` 查 agent 时已按 `~/.codex/agents/` / `<project>/.codex/agents/` 找，但查兄弟 skill（`arkts-scenario-runner` 的 `scenario_run.py`、`hmos-fix-build-errors`）时未设 `SKILLS_ROOT` 就退回 `~/.claude/skills/`——`install.sh` 装到 `<project>/.agents/skills/` 的标准布局会被误报 ❌ UNIT 缺失（2026-09-15 本仓实测复现，提示语也仍写 `.claude/skills`，已记为待修）。绕行：跑视觉验证前按 SKILL.md「路径约定」先设 `SKILLS_ROOT` 指向 `.agents/skills/`，探针即正常 ✅。

### 📝 文档 (Docs)

* `arkts-visual-verify/references/` 新增 `windows-setup.md`（源侧全 py 化后的 Windows 说明）、`layout-troubleshooting.md`、`wiring-gap-detection.md`；`phase4-replay-judge.md` 新增 J1.8 ②③ / J2.5、`phase2-edge-walk.md` §4.ab、`phase4-replay-run.md` §2；`fix-file-schema.md` §五 / §4.3-4 / §十 口径更新；`cli-cheatsheet.md` 工具箱表补齐回流脚本调用点。
* `a2h-verify/references/` 随编排精简重写：新增 `static-and-identity.md`（CHECK-1/2 规则）与 `device-verification.md`（CHECK-3/4 模式、产物、状态映射），退役 `checks-1-to-5.md` / `check6-to-7.md` / `execution-discipline.md` / `orchestration.md` 及整个 `_dormant/`。
* `arkts-ut-verifier/references/` 新增 `android-oracle-protocol.md` / `android-oracle-template.md`（Android oracle 采集）、`execution-checkpoints.md`（预检 / 试跑 / 分批编译检查点）、`fixer-dispatch.md` / `fixer-test-policy.md` / `fixer-wiring-policy.md`（修复分派与接线边界）、`mock-policy.md` / `import-mock.md`、`result-statistics.md`（三口径通过率）、`unimplemented-schema.md`；原 `agent-prompts/` 四份内联提示词退役，改由 `arkts-ut-*` 具名 agent 承接。
* 视觉验证变更细账以 `skills/arkts-visual-verify/CHANGELOG.md`（skill 根）为准，本文件为面向插件用户的摘要。

> **二进制说明**：本版 `skills/*/scripts/bin/` 为 windows-x64 + macos-arm64 双平台 Nuitka 二进制，由上游 CI 自源提交 1b3088d 重编，visual-verify 与 ut-verifier 的入口契约修复已编入；`bin/a2h-*` 六平台运行时二进制未重编，与 v1.5.2 一致。

## [version v1.5.2] - 2026-08-31

本次 skills 同步（来自 ArkTs-Core `version_830_codex_v`）修掉三类静默失效：领域 agent 装了从不被派发、打点调用指向不存在的二进制、装机脚本重跑会叠加内容。

### 🐛 修复 (Fixed)

* **领域 agent 装了却从不被派发**：22 个 `arkts-*` 领域 agent 随 `agents-codex/` 正常装进 `.codex/agents/`，但「主会话何时派发、派给谁、怎么校验回复末尾的 `loaded_skills:` 行」这条规则只写在上游的 `AGENTS.dispatch.md` 里，`install.sh` / `install.ps1` 从不读它 —— 契约只送到一半（agent 侧的自律条款随 `*.toml` 同步了，调度端的规则没有）。**失败是静默的**：22 个 `.toml` 全部正常，看不出异常，只是永远没被 `spawn_agent`。现在 `install.sh` 新增 §5b、`install.ps1` 新增 §5c，把 `AGENTS.dispatch.md` 以「替换或追加」方式写入 `AGENTS.md` 的 `arkts-domain-agents` 标记块，沿用同文件 `migbot-platform` 块的既有惯用法；`install.sh` 用纯 awk 实现，不引入 python3 依赖。原 §5 的 `migbot` 空标记块逻辑一字未动，两个块共存互不干扰。
* **装机脚本重跑会叠加内容**：上游 `AGENTS.dispatch.md` 的 `arkts-domain-agents:end` 标记原在文件中段，其后的「设备截图落点纪律」一段落在标记块**外面**，而注入是「用整个文件替换标记块」⇒ 每装一次块外内容追加一份（实测 17 → 23 → 29 行）。上游已把结束标记移到文件末尾，整个文件成为一个受管块；三连装稳定 25 行、每块各 1 个。
* **打点调用指向不存在的二进制**：五个流水线 skill（`a2h-spec` / `plan` / `execute` / `verify` / `retrospect`）收尾调的是 `.migbot/bin/a2h-codex mark-stage`，而 v1.0.1 起运行时只装 `a2h`（`a2h-codex` 是已退役的发行别名，`install.sh` 还会主动删除它）。这些调用旁标注「忽略退出码、绝不阻断流水线」，于是 8 处全部 `no such file or directory` 且被静默吞掉 —— 流水线表面全绿，**看板永远收不到阶段水位**。上游已改用 `a2h`，并修掉转换器里把二进制名连同子命令一起替换的改写规则。
* **`validate.sh` 三条硬失败清零**：skill 目录 `android2hmos_resources_convert` 改名为 `android2hmos-resources-convert`（对齐 `NAME_RE`，与既有的 `hmos_fix_build_errors` → `hmos-fix-build-errors` 同款处理）；`a2h-execute` 参考文档里两处 `.claude/skills` 残留改为单平台陈述；6 个 `agents-codex/*.toml` 里的下划线 skill 名一并更正。

### ⚠️ 升级提示

* 已有工程重装后，`AGENTS.md` 会新增 `arkts-domain-agents` 标记块（幂等，重复安装不叠加）；块内内容由上游生成，请勿手改。
* 若此前手工建过 `.migbot/bin/a2h-codex` 软链作为绕行，`install.sh` 会自动清除，不再需要。

## [version v1.5.1] - 2026-08-30

统一版本线 1.5.1：配套运行时 migbot-runtime-src v1.4.7、服务端 migbot-server v1.2.32。本版把**同意改为安装级**（一台机器同意一次，新工程自动继承），`migbot_session_id` 改为每工程一个，用户数按 `install_id` 去重。

- **Install-level consent (agree once per machine)** (with migbot-runtime-src ≥ v1.4.7, migbot-server ≥ v1.2.32): `a2h init-run` mints/reuses this machine's `install_id` (`~/.migbot/install.json`) and inherits the machine's consent decision into new projects; `a2h-init` §2.1 and `a2h-privacy` §B run `init-run` before showing the agreement, so a project that inherits `granted` no longer prompts. `migbot_session_id` is now **per project** (one dashboard row = one project); users are de-duplicated by `install_id`. `/a2h-privacy status` also shows `install_id` — one deletion request clears every project on the machine.
- Runtime binaries synced to migbot-runtime-src **v1.4.7**.

## [version v1.5.0] - 2026-08-27

版本线统一：自本版起与 hmigbot（Claude Code 线）同号发布（1.5.0），配套运行时 migbot-runtime-src v1.4.3。功能内容承接 v1.0.1（见下），另含 publish 版本门禁与 publish-lite secret 名修正。

## [version v1.0.1] - 2026-08-27

本次迭代主线是「打点能力与 hmigbot 一致」：二进制统一命名 a2h（a2h-codex 别名退役）、a2h-init / a2h-privacy 改为从 hmigbot commands 机械生成、同意流程幂等化、hook 信任自检。配套运行时 migbot-runtime-src v1.4.1+。

### 🔧 变更 (Changed)

- **a2h-init / a2h-privacy（中英四份）改为从 hmigbot 的 `commands/*.md` 机械生成**，脚本 `scripts/sync-commands.py`（取代一次性的 `.convert/commands.py`）。宿主差异全部收敛在脚本里：`/`→`$`、`a2h-bootstrap`/`a2h-agreement` 路径、plugin 与 install.sh 措辞、剥离 Claude Code 专属 OTel 清理、注入 Codex 专属 hook-trust 自检。**不要再手改这四个 SKILL.md**——改 hmigbot 的 command 后重跑 `python3 scripts/sync-commands.py --src <hmigbot>/commands`；`--check` 可做漂移检查。
- 生成结果与此前手改版对比：a2h-privacy 逐字节相同；a2h-init 仅措辞级差异（以源为准）。


### 🔧 优化 (Improved)

* **遥测二进制统一命名 `a2h-codex` → `a2h`**：运行时二进制与 hmigbot（Claude Code 版）的 `a2h` 本就是同一个程序，`a2h-codex` 只是发行别名。现在两个插件统一使用 `a2h` 这一个名字：`bin/a2h-<os>-<arch>[.exe]` 六个平台产物、`install.sh` / `install.ps1` / `a2h-bootstrap(.ps1)` 就位路径（`.migbot/bin/a2h`、`.migbot\bin\a2h.exe`）、`.codex/config.toml` 的 `[hooks.*]` 命令（`./.migbot/bin/a2h hook`）、全部 skill 中的 `init-run` / `mark-stage` / `hook-trust` / `count-lines` 调用、`validate.sh` 与发布 workflow 的断言、README / PORTING 文档一并改名。子命令集合不变。
* **旧安装自动迁移（幂等）**：`install.sh` / `install.ps1` 若检测到 `.codex/config.toml` 中仍是 `a2h-codex hook` / `a2h-codex.exe hook`，会原地改写为 `a2h`（只替换该 token，其余内容不动，可反复执行）；就位 `a2h` 后同时删除磁盘上残留的 `.migbot/bin/a2h-codex[.exe]`，`a2h-bootstrap(.ps1)` 的清扫列表亦同步加入该旧名。注意：改写 hook 命令行后 Codex 的 hook 信任 hash 会变化，需在 Codex 里重新 `/hooks` 信任一次（安装尾声的 `hook-trust` 自检会提示）。


本次迭代的主线是「让计划变轻、让执行可追责」：plan 产物从 127KB 单体文件重构为「索引 + 逐切片账本」的分层形态并由多个 subagent 并行生成；execute 的收尾链路统一到单一收尾者与脚本化回写，崩溃后秒级恢复；spec 侧引入证据驱动的覆盖门禁与 AC 级追溯，让「被静默漏掉的需求」在每个阶段都会被机械点名。全部改动均由 aippt / jetsnack 多轮端到端验证驱动。

改动同步自源仓库 ArkTs-Core：[#77 a2h-plan/execute 分层优化]、[#79 Spec 证据驱动覆盖门禁]，及 version_815_planFix 分支的后续调度修正。

### ✨ 新增 (Added)

* **证据驱动覆盖门禁（a2h-spec）**：从 Android 源码机械检出行为信号与具名实例（埋点事件、桥方法、枚举、阈值等），逐实例记账——每一条要么被 AC 认领、要么显式跳过并披露，漏账即阻断。取代旧的「AC 数量预算」，数量不再参与判定。
* **AC 级跨阶段追溯**：spec → plan → execute → verify 每阶段一份账本、一个 linter，漏认领 / 绑旧断言 / 双实现自动检出并定责到具体阶段；同一问题多轮不收敛自动熔断，转为决策卡交用户裁决。
* **plan 三写并行编排**：ui-plan、base-plan、全部切片账本由三个 subagent 并行生成，主线程只负责全局裁决（拓扑、归属、分组）与收拢审批。
* **统一收尾者 + 回写脚本**：execute 各阶段收尾统一为一个四模式 agent；状态账本与 brief 的落盘交给幂等脚本执行——收尾崩溃后重跑脚本即恢复，不再重做接线与编译。

### 🔧 优化 (Improved)

* **计划体量与读取开销大幅下降**：plan 产物 127KB → 约 33KB（-74%），执行期 plan 相关上下文读取约 -95%；subagent 返回一律压缩为 30 行内信封。
* **编译链路精简**：删除 Stage 1 逐批编译门（页面互不依赖，统一在阶段末一次容忍性编译收口）；全程增量构建 + 环境预热；发布门强制真实构建防「空转假通过」。
* **调度规则收敛**：UI 分批改为纯优先级分组；单任务的组/批一律消除（并组、附挂或并批）；组容量改为直接按切片数计数，不再加权。
* **spec 生成提速**：最长的 api-inventory 子任务前置隐藏约 15–18 分钟；切片生成即自检，覆盖修复不再拖串行尾巴；DataBinding 与自定义资源目录的布局解析一次通过。

### 🐛 修复 (Fixed)

* **切片被按步骤拆成多个 subagent**：废除单元化波次派发（实测有害无益），改为每切片恒一个 worker，确实过大时按依赖断面拆分。
* **444 条「需求未认领」**：根因是记账缺口而非实现缺口——实现认领现由收尾者从计划账本自动抄录、随回写脚本落盘。
* **结构验证产物写错目录**：Windows 下手动驱动脚本时误写 docs/，现脚本层硬拒旧路径并指引正确落点。
* **旧术语泄漏**：生成产物中残留的 handoff 旧称全量清理为 brief。

### ⚠️ 兼容性：

* 旧版单体 feature-plan 会被明确报错并提示重新生成计划（执行进度存于状态账本，重排零损失）；旧产物中的已废弃字段可被解析器容忍，无需迁移。

## [version v0.2.0] - 2026-07-30

本次以**登录能力落地**与**多项 skill 自优化**为主线：新增登录功能，并对 skill 自优化、visual verify、spec 分层分级三条能力线做了一轮打磨。

### ✨ 新增 (Added)

- **登录功能实现**：接入登录能力，迁移插件包在使用前具备账号登录入口。

### 🔧 优化 (Improved)

- **Skill 自优化**：对 skill 自优化闭环做一轮打磨，提升迭代优化的稳定性与效果。
- **Visual verify 优化**：优化视觉校验（visual verify）流程，提升 UI 验证的准确性与可用性。
- **Spec 分层分级优化**：优化 spec 的分层、分级机制，改善规格内容的组织与消费。


## [version v0.1.4] - 2026-07-24

本次以**补齐编排型 skill 的前置配置**为主线：`config-seed.toml` 开箱写入 Codex 多线程编排所需的三项配置，安装器对已有 `config.toml` 的老用户做幂等补写，并新增三键守护校验。本版仅配置与安装器变更，`a2h-codex` 六平台二进制未重编，与 v0.1.2 完全一致。

### ✨ 新增 (Added)

- **`config-seed.toml` 补齐编排三项前置配置**（#2，Closes #1）：编排型 skill（`a2h-execute` / `a2h-verify` / `arkts-visual-verify` / `arkts-ut-verifier`）依赖 Codex 的多线程编排能力，seed 现在开箱写入 `[features] multi_agent = true`、`[agents] max_threads = 6`，并为原有的 `max_depth = 2` 补上默认值说明。
- **安装器对老用户幂等补写**：老用户已有 `config.toml` 时 seed 不会拷贝，此前这三项前置配置只能手工补。`install.sh` / `install.ps1` 镜像 `hooks=true` 的模式新增：
  - **4a'**：幂等补写 `multi_agent = true`——表内插入、不写重复表头；用户显式配置了 `false` 时只告警不覆盖，尊重用户选择。
  - **4a''**：检测到 `max_depth < 2` 时告警不改值。

### ✅ 校验 (Validated)

- `validate.sh` 新增三键守护检查（`multi_agent` / `max_threads` / `max_depth`），本地跑通：`VALIDATE: PASS`（skills checked: 89，agents checked: 7）。

### 📝 文档 (Docs)

- README / `docs/PORTING.md` 同步，顺带修正 `docs/PORTING.md` 过期的 `max_depth = 1` 表述。

### 🔗 配套服务端版本 (Server)

- 无服务端配套要求，本版不涉及打点链路。

> **二进制说明**：本版仅配置与安装器变更，`bin/a2h-codex-*` 六平台二进制未改动，与 v0.1.2 完全一致（未重编）。