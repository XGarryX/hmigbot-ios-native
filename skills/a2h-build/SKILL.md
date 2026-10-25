---
name: a2h-build
description: Trigger: `$a2h-build` or natural language. Validate plugin config and run hvigorw assembleHap on the HarmonyOS repo
---

> **iOS 源输入适配**：执行源分析/源设备操作前，读 [原生输入协议](../a2h-spec/references/native-input.md)。它仅替换平台输入；原阶段、模板、规则、门禁、模式和 target 侧执行保持 1.5.2。

> Codex skill (converted from the `a2h-build` slash command). Invoke with `$a2h-build`, or pick it in `/skills` (the default_prompt below auto-runs). Codex has no custom slash commands, so the `$` prefix replaces `/`.


> **Windows:** never go through `bash`. Use `powershell -NoProfile -ExecutionPolicy Bypass -File .migbot\bin\a2h-tool.ps1 <validate|build>` and `.migbot\bin\a2h.exe <subcommand>` (see `$a2h-init` §0).

1. Run `.migbot/bin/a2h-tool validate`. If it returns `{ok:false}`, list each failure to the user, suggest running `$a2h-init` to fix paths, and stop.
2. Otherwise run `.migbot/bin/a2h-tool build`. Stream output. Report final exit code.
3. Report this stage's token usage: run `Bash: .migbot/bin/a2h mark-stage a2h-build`. Best-effort and consent-gated — ignore its exit status (it never affects the build result).
