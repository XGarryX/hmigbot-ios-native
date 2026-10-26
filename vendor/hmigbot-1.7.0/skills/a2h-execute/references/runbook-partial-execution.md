# a2h-execute · §6 部分执行触发语表（--retry-failed / --resume / --domain）

> 本文件由 `a2h-execute/SKILL.md` 原文**逐字搬出**（M1 token 减量：主会话 runbook 只留循环所需，细则集中于此）。读取时机：用户说「重跑失败的 / 只重跑某域 / 从断点继续 / 只跑基建 / 全部重新执行」，或 next_batch exit 1 契约违规后要重生成 plan。

## 6. 部分执行触发语表（--retry-failed / --resume / --domain 沿用 v2）

| 用户触发语（示例） | 命令映射（重生成 plan 后回 §2 循环） |
|---|---|
| 「重跑失败的任务」 | `python3 $EXE/scripts/generate_waves.py --blueprint spec/blueprint --out spec/waves --wave <当前波> --retry-failed --json` |
| 「只重跑 member-pay 域的审计修复」 | `generate_waves.py --wave auditfix --domain member-pay` |
| 「重做某个域的实现」 | 先按 ownership 回滚该域（recovery-playbook R3 局部分支）→ `generate_waves.py --wave domains --domain <key>` |
| 「从断点继续 / 接着上次跑」 | 直接拍①（state 指针续跑）；plan 文件丢失 → `generate_waves.py --wave <w> --resume` 重生成后拍① |
| 「只跑基建 / 只跑审计」 | `generate_waves.py --wave infra` / `--wave auditfix` |
| 「全部重新执行」 | `generate_waves.py --wave all`（旧 state 归档另起，禁覆盖续写） |

任务集裁剪依据统一为 state.json（`--retry-failed` 只取 failed，`--resume` 只取非终态，trim 逻辑在 generate_waves）；重生成后 `contract_hash` 由拍①复核，不一致即拒绝续跑。

E167（AIPPT_930 移植）：①`--domain` 对 infra 波按模块组 key 过滤（此前警告后忽略、派出全部）；②裁剪按逻辑任务 id 跨轮对账（`impl:r3:a` ↔ `impl:a`/`impl:r2:a`，取 state 最新一轮状态）——此前重入轮次先打 rN 再裁剪，`--resume` 把已 done 的全部重做、`--retry-failed` 裁成空集；③infra / domains / closeout 重入与 E68 同形：第二轮起 id 带 rN（`impl:r2:core`、`b4:r2:factchain`），回执与任务书文件名带 `infra-rN-`/`domains-rN-`/`closeout-rN-`，首轮产物不被覆盖（E81 只把旧回执判在途，文件仍会被新回执覆盖）。
