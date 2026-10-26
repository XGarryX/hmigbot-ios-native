# a2h-execute · 禁写面 / 围栏三档 / 产物写权硬规则（E24）

> 本文件由 `a2h-execute/SKILL.md` 原文**逐字搬出**（M1 token 减量：主会话 runbook 只留循环所需，细则集中于此）。读取时机：升级材料含 `gate:fence-audit` / `fence-snapshot` / `reduce:product-write-audit` / `quick_fix`，或任何想亲手改产物的念头出现时。

- **禁写面与围栏三档**（第十四批）：落账按 ownership 对账 `files_touched`，三档——`forbidden`（spec/ 契约与台账、`*/src/main/resources/**`、EntryAbility、WiringRoot、装机面；自身围栏内除外，回执文件免检）→ 该回执**判 FAIL 并按拍①快照还原**（`next_batch` 零在途时拍 `spec/state/fence-snapshot/`）；`cross_owner`（写进同波另一任务围栏）→ 记账，波尾 `gate:fence-audit` 未经 `spec/state/fence-ack.json` 确认不放行编译（升级呈报，人看一眼再放）；`unowned` 记债。资源 JSON 唯一写者是 `seed_resources.py`：understand 波尾 `reduce:seed-resources` 把收割字面量播进 element JSON 并产 `spec/baseline/resource-index.json`（任务书内联「原值 → 资源名」）；各实现波尾 `reduce:resource-sweep` 把回执 `resources_needed[]` 统一补写后再编译。主会话处置：fence-audit 升级材料到手 → 复核 `spec/reports/fence-audit-<wave>.json` 的 blocking，确认无害则把 {task, file} 追加进 fence-ack.json 的 acked[]，`--rerun-reduce gate:fence-audit`。

## 产物写权硬规则（E24，DR_0903 冒烟实证）

主会话**不写产物**（`entry/src/main/ets/**`、`resources/**`）。产物只有三类合法写者，波尾 `reduce:product-write-audit` 按时间窗机械核对，窗口外的改动记 `mainloop_edit` 进 `spec/reports/product-write-audit-<wave>.json` 并计入交接欠账：

| 写者 | 窗口 | 说明 |
|---|---|---|
| 代理 | 派发 → 落账 | 计划内 agent 任务；产物改动必须出现在回执 `files[]` |
| 脚本 | reduce 开始 → 结束 | `sync_pagemap` / `mount_wiring` / `seed_resources --sweep` / `write_probe`（E37 K4 探针，波尾 build 前 `reduce:probe`，留痕 `spec/state/probe-writes.json`；编译门 graph-mismatch 的处置也是跑它 `--gate <门>` 再 `--rerun-reduce`，不再手写探针）等 land_results 执行的 reduce |
| quick_fix | 编译门判 `quick_fix` → 该门下次重跑 | 915 唯一例外：错误数 ≤ `gates.quick_fix_threshold` 时主循环亲手快修（`references/conservative-mode.md` §3）；超阈值派 hmos-builder |

**禁止**（DR_0903 三次实证，全部是「凑闸」）：
- 深度闸 / 契约门 / 围栏门 / 任何非编译门 FAIL 后亲手改产物——走 depthfix 回派、fence-ack、修复代理；
- 亲手改完产物后手动重跑门禁脚本覆盖报告——门禁只经 `land_results.py --rerun-reduce <gate>` 重跑；
- 亲手跑 `state_update.py` 补页/域状态——账由 land_results 自动落（E25），账不对是脚本 bug，报缺不补账。
