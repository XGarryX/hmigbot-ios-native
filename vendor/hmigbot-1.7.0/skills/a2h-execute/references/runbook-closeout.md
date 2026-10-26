# a2h-execute · §7 收尾（closeout 波）

> 本文件由 `a2h-execute/SKILL.md` 原文**逐字搬出**（M1 token 减量：主会话 runbook 只留循环所需，细则集中于此）。读取时机：auditfix 波 `done` 且 `next` 指向 `closeout`；closeout 波内 `gate:compile-4` / `gate:handoffs` / `gate:cold-start` / `gate:smoke-1page` / `gate:render-static` / `gate:handoff-check` 出现在 `next` 或升级材料里。

## 7. 收尾（closeout 波，全部由 plan 承载——V1，OPT-PLAN-V3 P1/P6）

v3 复盘原因 1：execute §7 曾是散文步骤（B4 三个 `Skill()`、一句「交棒 a2h-verify」），
散文交接全断——a2h-verify 调用 0 次、B4-2 静默降级、探针成常驻依赖、45 条跨域待办蒸发。
现在收尾是 **auditfix 之后的独立 `closeout` 波**，主会话对它和其它波一样只跑①④两条命令：

- auditfix 波 `done` 时 `next` 指向 `wiring`（有 backlog）或 `closeout`；照 §2 `done` 行走
  （`next.generate` → 回①）。**主会话不亲手跑任何收尾动作**。
- `closeout` 波节点链（`gates.device_smoke` 三档 off/hmos/dual 决定形状）：
  - `b4:factchain`（hmos/dual 档）= `a2h-factchain-runner` agent 任务，跑 fact 链三 Skill
    （device_smoke=off 时无此任务，reduce 链挂 `@start` 保留组照常收尾）；
  - `reduce:build-closeout --detach-probe`（按 `// A2H-PROBE` 标记摘探针）→ `gate:compile-4`
    （business_ratio 门，探针入图不算业务接线）**＝ 830 的 FV-2 终态全量编译**
    → `gate:handoffs`（verify_handoffs 三型断言）
    → hmos/dual 档再串 `gate:cold-start`（830 冷启探针：**不 crash + 首个网络请求出网**，
    二值机械判据、不看 UI 树；无设备 exit 3 记 `unverified-cold-start` 粘性债不阻断。
    E172（AIPPT_930 移植）：探针原始证据落盘 `spec/reports/smoke/cold-start-evidence/`（targets/hilog/ps/dump，
    报告带 `evidence_dir`）；hilog 远端报错（hdc shell 仍 exit 0）按 `EVIDENCE_LOST` 判 FAIL，不拿零日志当无崩溃；
    网络判据只数本应用进程（`hilog -P <pid>`）的网络栈日志，别的应用出网不能替本应用过闸；多设备按
    workflow-params `device.hdc_target` 选靶）
    → `gate:smoke-1page`（首屏可点；挂冷启闸之后——冷启不过就不必点）
    → **off 档**改串 `gate:render-static`（F4 静态回退：`static_runtime_lint` 模块级 new 运行期服务/避让区 px 当 vp +
    `sync_pagemap --check-only` 的 @Provider/@Consumer 对账、push 未注册、Navigation 根占位 + `host_page --check-only` 宿主三态/启动路由；
    报告 `spec/reports/smoke/render-static.json`，handoff-check 的 cold-start / smoke-1page 行读它——此前 off 档零渲染期检查，
    AIPPT_930_token2 冷启崩/导航失效全在人工实装才暴露）
    → `reduce:report --strict` → `gate:handoff-check`（交付面逐项对账）。
  - **FV-1 结构闭包不在本波**——它连同自动修复循环是上游的 `closure` 条件波，见 §7b。

- 交棒消息**唯一来源** `spec/reports/handoff-message.md`（handoff_check 产）：`closeout` 波
  `done` 时按 §2 `done` 行 `cat` 该文件转发。**BLOCKED 时该文件首行不含「完成」「failed=0」**——
  任一 blocked 项未清则本波不 `done`（escalate 呈用户，修后 `land_results.py --rerun-reduce gate:handoff-check`）。
