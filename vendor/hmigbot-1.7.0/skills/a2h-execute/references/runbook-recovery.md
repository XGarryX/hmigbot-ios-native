# a2h-execute · §5 恢复（编排状态全在文件，会话可弃）

> 本文件由 `a2h-execute/SKILL.md` 原文**逐字搬出**（M1 token 减量：主会话 runbook 只留循环所需，细则集中于此）。读取时机：会话中断 / compaction / 崩溃后重入、换会话或换宿主续跑、`escalate`。与 `recovery-playbook.md` 八条剧本配套。

## 5. 恢复（编排状态全在文件，会话可弃）

编排事实全部落盘（plan + state + results + journal + dispatch），主会话上下文不承载任何编排状态，因此：

- **state 指针续跑**：会话中断 / compaction / 崩溃 → 新会话（同一工程目录）跑一遍拍①即接上，无需人工盘点。
- **换会话 / 换宿主续跑成立**：在 OpenCode 里继续 Codex 跑到一半的 wave，同样只是跑拍①。
- 派发过但未落账的任务：拍①输出 `wait` + `missing[]`，按 §2 表处置；journal 的 `resume_key` 保证幂等不重做。

八条故障剧本（零产出 / 半产出 / 编译门降档 / 重入防重 / deferred 汇账 / **R7 门禁 REDUCE_FAIL 复位重跑** / **R8 平台侧集群故障 529 潮**）→ **MUST READ** [references/recovery-playbook.md](./references/recovery-playbook.md)。

- **脚本报错 = 停机呈报**：主会话不得修改产品文件（`entry/**`）与 `.agents/skills/**`，也不得热改数据/脚本绕过报错；呈现报错原文与上下文等用户裁决。若人工裁定热改（用户明确指示改哪个文件），记录于 `python3 $EXE/scripts/hotfix_ledger.py --add --file <path> --error "<原文首行>" --note "<改了什么>" [--diff-file <path>]` → `spec/state/hotfix-ledger.json`（按 (file, error) 幂等；`--list` 查看；handoff_check 以「热改记录 N 条」呈报，不阻断）。

## 手动起无人值守外壳（a2h_run.py 之外的排障用法，E208）
`DEVECO_SDK_HOME=<sdk> python3 $EXE/scripts/unattended_runner.py --project <root> --prompt CODEX_PROMPT.md --log spec/state/runner.jsonl [--max-restarts 3 --backoff 300]`；`--dry-run` 只打印命令与在途任务。
