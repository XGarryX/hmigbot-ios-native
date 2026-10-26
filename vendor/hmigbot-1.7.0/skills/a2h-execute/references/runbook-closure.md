# a2h-execute · §7b closure 波（830 Final Structural Closure 自动修复循环）

> 本文件由 `a2h-execute/SKILL.md` 原文**逐字搬出**（M1 token 减量：主会话 runbook 只留循环所需，细则集中于此）。读取时机：`done.next` 出 closure 波、`gate:closure-scan` / `gate:closure-rescan` 升级、closure 判 STALLED（`next.kind=escalate`）。

## 7b. closure 波（830 Final Structural Closure 自动修复循环）

830 的 FV-1 是个有界循环：`structural_loop iterate --mode pipeline` 扫一轮 → CONTINUE 就把
`dispatch_prompt` 交给 repair worker → 修完重扫，`MAX_ITER=8` 封顶，STALLED / REGRESSED /
EXHAUSTED 一律浮出复核**不静默放行**。静态 DAG 表达不了「扫完再决定扇出多少」，故照 wiring
条件波的成法拆开，主会话对它和其它波一样只跑①④两条命令：

| 环节 | 承载 |
|---|---|
| 首轮扫描 | auditfix 链尾 `gate:closure-scan`（保底入口，wiring 是条件波）；wiring 跑过则其链尾再扫一次刷新账 |
| 汇账 | `closure_backlog.py`：iterate 的 detector findings → 按 ownership glob 归属 owner → `spec/blueprint/closure-backlog.json`（`open` / `round` / `items[]` / `unowned[]`） |
| 出波 | `next_batch` 见 `open>0` 且未 defer / 未到顶 → `done.next` 出 closure 波 |
| 扇出 | `generate_waves --wave closure`：**按 owner 一个修复任务**（id 带 `r<round>` 后缀防跨轮撞 dispatch 账），任务书只列本 owner 名下条目 + 完整简报指针，白名单按 owner 收窄。E176（AIPPT_930 移植）：域 owner 的白名单附带本域各页的 E39 主题回执分片 `spec/execution/theme-receipts/<page>.json`（处方常要求校正漂移的 file:line，此前只投产物写权、worker 只能依法 skipped）；不给共享目录、别域分片、infra owner 的 UI 回执，plan 与任务书共用 `_closure_owner_files` |
| 分轨 | 830 §3.5：owner 名下**全为 ui 类** → `a2h-activity-converter`；含 feat 或混合 → `a2h-migration-worker`。**粒度是 owner 不是单条 finding**——lint R3 禁同 map 组内 ownership 相交，单写者纪律也禁两个 agent 并发改同一 owner |
| 收敛判定 | 波尾 `gate:closure-rescan` 重跑 iterate 并改写 backlog（round+1）——**worker 不自证**；仍 open 且 round<max_iter → `next_batch` 再出一轮 closure；到顶（exhausted）→ 跳过并把未收敛记入交付欠账，不当通过 |

`unowned[]`（扫出问题但 ownership 无人认领）不参与扇出，但计入 `open`——「扫不出归属」不等于
「没问题」，这是 v3 那 45 条 skipped 蒸发的同型陷阱。
