---
name: a2h-build-zh
description: 触发：`$a2h-build-zh` 或自然语言。校验插件配置并在 HarmonyOS 仓上跑 hvigorw assembleHap
---

> **0.13.4 统一合同（优先于历史示例）**：先读 [执行交界合同](../a2h-run/references/execution-boundary.md)。源读取、选定构建配置、SwiftSyntax/facts、源 AC 和 indexed 计划由当前 git 上游唯一生产；从 execute 起使用本技能的 Garry 实施/收口方法。只使用宿主实际支持的派发字段，不照抄 `agent_type`。已有授权直接沿用；依赖失败输入的任务保持 blocked，不降低静态门禁。权限按交界合同区分：禁止桌面远控；指定测试应用/模拟器的截图、控件查询和固定回放可按已确认范围执行，Preview 不证明业务运行。录屏及未指定设备不在此授权内，未执行项如实记 not_run。未经授权不运行遥测上传。工具修复、工具验证、项目转换、HAP 构建和完整迁移验收分别报告，不能用局部 100% 代表全部完成。



> **iOS 源输入适配**：执行源分析/源设备操作前，读 [原生输入协议](../ios-source-analysis/SKILL.md)。它仅替换平台输入；原阶段、模板、规则、门禁、模式和 target 侧执行保持 1.5.2。

> Codex skill (converted from the `a2h-build-zh` slash command). Invoke with `$a2h-build-zh`, or pick it in `/skills` (the default_prompt below auto-runs). Codex has no custom slash commands, so the `$` prefix replaces `/`.


> **Windows：** 绝不走 `bash`。改用 `powershell -NoProfile -ExecutionPolicy Bypass -File .migbot\bin\a2h-tool.ps1 <validate|build>` 与 `.migbot\bin\a2h.exe <子命令>`（见 `$a2h-init` §0）。

1. 跑 `.migbot/bin/a2h-tool validate`。返回 `{ok:false}` → 把每条失败列给用户，建议跑 `$a2h-init` 修正路径，然后停下。
2. 否则跑 `.migbot/bin/a2h-tool build`。流式输出。报告最终退出码。
3. 上报本阶段 token 用量：跑 `Bash: .migbot/bin/a2h mark-stage a2h-build`。尽力而为、受授权门控——忽略其退出码（绝不影响构建结果）。
