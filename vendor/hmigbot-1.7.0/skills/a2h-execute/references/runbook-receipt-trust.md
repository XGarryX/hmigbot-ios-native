# a2h-execute · 回执可信与 findings 销账（DevEco-830 A8 / A3 / A2 / C1 / C2）

> 本文件由 `a2h-execute/SKILL.md` 原文**逐字搬出**（M1 token 减量：主会话 runbook 只留循环所需，细则集中于此）。读取时机：落账出现 `FILES_MISSING` / `DEFERRED_LOCATION_MISSING` / `rejected[]` / `resolved_rejected`；`gate:round0-clear` / `findings-gate.json` / `safearea-layers` / `escalated-ratio` 出现在升级或 handoff 材料里。

## 回执可信与 findings 销账（DevEco-830 A8 / A3 / A2 / C1 / C2）

「主会话零开放决策」的前提是 worker 回执可信；830 复盘实证该前提会被打破（回执 OK 而产物不存在 6 次、`return;` 空实现标 resolved）。以下核验全部由脚本在落账链内完成，主会话不读结果正文：

- **A8 声明文件实存**：`land_results` 落账前核 `files[]` / `files_touched[]` 每条相对路径实存（目录算实存，含通配符的条目不判）；缺失 → `FILES_MISSING`，按结构化不合格走重试配额（RETRY_NEEDED / RETRY_EXHAUSTED）。
- **A3 deferred 兑现真伪**：`resolved_refs[]` 翻 resolved 必须过两关——条目 `trigger` 可机械求值且成立（symbol-implemented / grep / api-online 查源码，其余跑 `check_cmd`），且目标函数体非 no-op（去注释后为空或只 `return`）。不成立或无判据 → `rejected[]` 留原状态（`contract_sync --merge-deferred` 报告 `summary.resolved_rejected`）。合法空 override 在函数体内或签名上一行写 `// A2H-NOOP: <理由>` 豁免。
- **E250 handoff 断言**：handoff 的完成是「交接对象做了某事」（改动常在别人的文件里），不走桩位判据——必写断言型 trigger（grep / artifact / slice / symbol-implemented）；登记时 grep 正则自检（能编译、能命中自身字面形态，双重转义自动去一层，纠不了拒登），resolve_by 缺省 wiring；gate:handoffs 的 trigger 对账与到期欠账覆盖 handoff。
- **E244 桩位判据**：forward-ref / forward-ref-uncertain 不再由代理写判据——登记时脚本在 `location` 锚点上方插 `// FWD-REF(<ID>)`、记锚点代码指纹（锚点找不到退整文件指纹），判据 `stub-cleared`，并从桩位代码抽出还没落盘的跨文件引用（`pending_refs`，取自代码不是预测）。求值（去标记后的文本）：桩位引用全部可解析且非空实现是前提；登记时有未落盘引用的（桩位已按契约名调用）→ 提供方落盘即成立，gate:handoffs 对账时自动置 resolved 并删标记；登记时是空实现 / 本地占位的 → 还须申报兑现且代码与登记时不同（去注释比较）。只删标记、只改注释、换一种空实现、改成调用未落盘符号 → `rejected[]`。location 文件不存在 → 落账期 `DEFERRED_LOCATION_MISSING`，走重试配额（代理在上下文里改正路径）。外部条件类判据（sdk-available / decision-chosen / api-online / resource-ready）照旧。
- **A2 findings 销账门**：auditfix 波 fix 批后 `gate:round0-clear`（`findings_gate.py --rerun`）重跑 round0 取残余 findings；P0/P1 必须清零或带豁免，P2 逐条落 `spec/reports/findings-backlog.json`。豁免两种写法：`spec/blueprint/findings-waivers.json`（check + file 通配 + waived_by + reason）或源码行 `// A2H-WAIVE: <check> <理由>`。**缺省 report-only**（exit 0，`handoff_check` 记 warn）；`workflow-params.gates.findings_blocking=true` 或 `--blocking` 才阻断——B1/C1 新检查器先观察一轮再切。
- **C1 UI 静态 lint**（round0 内置四条，零设备）：`ui-web-src-timing`（Web 首帧无条件创建 + 事后赋值 + 无 loadUrl，P1）/ `ui-image-src-binding`（Image 绑非状态字段且事后赋值，P2）/ `ui-statusbar-double-inset`（根 padding statusBar 之上子元素 margin top>40，P1）/ `ui-listitem-fullwidth`（ListItem 撑满使 List 对齐失效，P2）。销账走 A2。
- **B3 链③ 沉浸式四层反查**（round0 `safearea-layers`，仅当 meta.json 有 `needs_immersive_safearea=true` 的页）：L1 全工程须有 `setWindowLayoutFullScreen(true)`；L2 根 Navigation 须有 `expandSafeArea`（根无而每个沉浸式页自 expand 视为「L2 搬到本页」也成立）；L3 每个沉浸式页须有前景避让（`windowTopPadding` 等）；根有 L2 时子页再 expand 记 P2 双重穿透。逐页 grep expandSafeArea 是 830 撤回的错误候选，此处不用。E168（AIPPT_930 移植，模块 `_task_scope.py`）：domains 波 `safearea_layers` 机器收紧只对写页面的任务生效——拆分域核心任务（`impl:<域>` / `impl:rN:<域>`，写权全在 `features/`、`components/` 下、不写任何页）四层申报由页面块承担，核心回执允许显式 `[]`（字段缺失仍拒绝；页面块、写权含 pages/ 或宽泛写权仍必填非空）。
- **C2 收尾口径**：`handoff_check` 把 `state.gates["escalated-ratio"]` 最新判决与 `findings-gate.json` 纳入检查项（`escalated-ratio` 未过 → blocked；findings 未销账 → report-only warn / blocking blocked），两道门不得互相矛盾。
