# a2h-execute · 三宿主派发差异与降级兜底

> 本文件由 `a2h-execute/SKILL.md` 原文**逐字搬出**（M1 token 减量：主会话 runbook 只留循环所需，细则集中于此）。读取时机：换宿主续跑，或宿主无 subagent 能力需进入逐个亲自执行的兜底。

## 4. 三宿主派发差异（唯一的宿主适配面）

| 宿主 | 拍②派发方式 | 并行 | 状态 |
|---|---|---|---|
| Claude Code | Task 工具，subagent 类型字段填注册 agent 名，单消息多 Task | ✅ | 已验证 |
| Codex | 会话内线程指定 agent（max_concurrent_threads_per_session 配额） | 机制确认 | 细节 Step 3.5 实测 |
| OpenCode | task / @agent 指定注册 agent | 待实测 | 并行语义 Step 3.5 实测 |

**降级兜底（免费自带）**：宿主无 subagent 能力 → 主会话按批**逐个亲自执行**任务 prompt，结果同样写 `result_path`、同样一行回执语义、同样拍④落账——判断都在脚本里，正确性不损，只损墙钟。进入兜底前须呈报用户一句，禁静默降级。
