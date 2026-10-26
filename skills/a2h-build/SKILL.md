---
name: a2h-build
description: Trigger: `$a2h-build` or natural language. Validate plugin config and run hvigorw assembleHap on the HarmonyOS repo
---

> **0.13.4 统一合同（优先于历史示例）**：先读 [执行交界合同](../a2h-run/references/execution-boundary.md)。源读取、选定构建配置、SwiftSyntax/facts、源 AC 和 indexed 计划由当前 git 上游唯一生产；从 execute 起使用本技能的 Garry 实施/收口方法。只使用宿主实际支持的派发字段，不照抄 `agent_type`。已有授权直接沿用；依赖失败输入的任务保持 blocked，不降低静态门禁。当前范围禁止屏幕读取/截图/录屏及设备远控；依赖这些观察的检查记 not_run。未经授权不运行遥测上传。工具修复、工具验证、项目转换、HAP 构建和完整迁移验收分别报告，不能用局部 100% 代表全部完成。



> **iOS 源输入适配**：执行源分析/源设备操作前，读 [原生输入协议](../ios-source-analysis/SKILL.md)。它仅替换平台输入；原阶段、模板、规则、门禁、模式和 target 侧执行保持 1.5.2。

> Codex skill (converted from the `a2h-build` slash command). Invoke with `$a2h-build`, or pick it in `/skills` (the default_prompt below auto-runs). Codex has no custom slash commands, so the `$` prefix replaces `/`.


> **Windows:** never go through `bash`. Use `powershell -NoProfile -ExecutionPolicy Bypass -File .migbot\bin\a2h-tool.ps1 <validate|build>` and `.migbot\bin\a2h.exe <subcommand>` (see `$a2h-init` §0).

1. Run `.migbot/bin/a2h-tool validate`. If it returns `{ok:false}`, list each failure to the user, suggest running `$a2h-init` to fix paths, and stop.
2. Otherwise run `.migbot/bin/a2h-tool build`. Stream output. Report final exit code.
3. Report this stage's token usage: run `Bash: .migbot/bin/a2h mark-stage a2h-build`. Best-effort and consent-gated — ignore its exit status (it never affects the build result).
