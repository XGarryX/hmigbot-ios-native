---
name: ios-fact-tree
description: 从 SwiftUI、UIKit/Interface Builder 或混合 iOS 工程生成原格式 fact-tree，先读取选定 target/Release 上下文，再组织页面、导航、组件与系统接缝分析。
---

> **iOS 源输入适配**：执行源分析/源设备操作前，读 [原生输入协议](../a2h-spec/references/native-input.md)。它仅替换平台输入；原阶段、模板、规则、门禁、模式和 target 侧执行保持 1.5.2。

> **Codex subagent dispatch convention.** This skill dispatches subagents. In Codex, spawn them with the `spawn_agent` tool and pass `agent_type` = the role name **exactly as written in this skill** — the roles registered under `.codex/agents/*.toml` use the same hyphenated names, so no translation step is involved: `a2h-ios-converter`, `a2h-ios-analyzer`, `a2h-closer`, `a2h-fixer`, `a2h-migration-worker`, `ad-profile-builder`, `compose-fact-analyzer`, `hmos-builder`, `scenario-builder`, `visual-fixer`, `visual-fixer-reviewer`. The built-in `general-purpose` agent_type is unchanged. (Claude's `subagent_type` field is written `agent_type` for Codex; `Agent(...)` dispatch calls are `spawn_agent(...)`; there is no `Task` tool in Codex.)
>
> **Join 协议（收口五条款）。** Codex 子代理完成后**不会**唤醒主会话——结果必须由派发方主动收口，违者=静默卡死（实测事故）。
> ① **循环 wait**：每个 `spawn_agent` 句柄用循环调用 `wait_agent` 收口；单次超时只代表"还在跑"，继续再调；**禁止以"等待子代理"为由结束回合**。醒后必调 `list_agents` 确认是谁完成——**完成的唯一合法信号 = `agent_status` 为 `{"completed": …}`，绝不是产物文件的存在/条数**（文件会中途落盘，读半截=实测事故）；completed 态会在数轮后从 list 中消失，所以每次醒来都要及时查。正文所有"等待完成 / join / 到点即收"表述一律指此循环。
> ② **死句柄与验收**：连续 3 次超时后调 `list_agents` 核对，可配 `wait_for_artifact.py` 探产物活性；已 completed 且 summary 可读 → 直接消费；句柄消失且从未观测到 completed → 按断点重派（带原 prompt + 已落盘产物，上限 2 次），禁止继续等待。**completed ≠ 验收通过**：join 点跑 `python3 .agents/skills/a2h-join/scripts/join_gate.py --project .` 验产物完整性，FAIL 视同未取回、按本条重派。
> ③ **收口锚点**：本 skill 最终完成报告前必须收口全部句柄（join_gate exit 0）；正文写明的显式 join 点优先按正文执行。发用户门（Gate）时允许句柄跨 Gate 存活，但 Gate 摘要必须列明未收口句柄清单 + 各自的指定 join 点。
> ④ **放行 ≠ 遗弃**：正文"非阻塞放行/到点即收/降级继续"只推迟收口时机，不豁免收口义务。
> ⑤ **fire-and-forget**：仅正文显式声明"结果丢弃/不 gate"的派发（如 a2h-execute 的 env-prewarm）免收口；审计只认 join_gate 内静态 allowlist，正文声明只是文档层。
> **派发纪律**：`task_name` 必须唯一（带 page-id/slice-id/round-N 后缀）；并行派发前把预期产物清单写 `spec/a2h/_work/expected_<join点>.json`（join_gate 对账用，契约只认派发方、不认子代理自报）；**谁派谁收**——sub-agent 内部需要"等齐 N 片再合并"时禁止嵌套外派后自行退出，要么同步自做、要么把分片清单回报主会话代派（sub-agent 一停止，收口能力即丢）。**契约产物必须出自承担任务的子代理**：重派上限后仍产不出 → 如实报缺并停在未完成态；禁止派发方代写占位产物让 gate 转绿（声明过也不行——绿账必须对应真产物）。

> **路径约定**：下文 `$SKILLS_ROOT` = 本套 skills 的安装根目录。执行任何脚本前先设一次：`SKILLS_ROOT="$(cd "$(dirname 本SKILL.md)/.." && pwd)"`（用户级安装=`~/.agents/skills`；项目级=`<project>/.agents/skills` 或 `<project>/skills`）。

# ios-fact-tree — 原前置树编排入口

先读 [原生输入协议](../a2h-spec/references/native-input.md)。本 skill 保留 1.5.2 的“判架构 → 分派生成器 → 汇合 → 原数据闸 → 功能合并”流程，输入识别换成 SwiftUI/UIKit/IB。

1. `python scripts/detect_arch.py <源根>` 判架构。pure_compose/pure_traditional/hybrid 是旧 wire 标签，对应 SwiftUI/UIKit/混合，不表示应用使用 Compose。
2. SwiftUI 侧使用 $swiftui-fact-tree；UIKit/IB 侧按 $ios-ui-graph-builder 的真实页面、组件、导航与 containment 生成同构树，再调用 $app-relationship-tree 补语义。不能调用 iOS APK/toolkit 解析器处理 Swift。
3. 混合侧合并已有节点，补 UIHostingController/UIViewRepresentable/UIViewControllerRepresentable 的承载边，不造虚节点。保持原 activities/fragments/components/flow_graph 和导航/前置条件/reach_paths 格式；这些是通用树的历史字段。
4. 按原 $a2h-functional-registry → $a2h-functional-merge 注入 functional_checks；并行时维持原快照、单写者与 join 协议。没有并行能力时顺序完成，不伪造子任务完成标记。
5. 对最终树运行原 `dispatch.py gate` 及它调用的 output_contract/connectivity/functional 检查。图的可达性、字段与功能关联规则不因 iOS 豁免。

实际页面集合和导航语义仍由分析者完成；静态扫描只提供有出处的线索，不把每次赋值转成一条验收标准。
