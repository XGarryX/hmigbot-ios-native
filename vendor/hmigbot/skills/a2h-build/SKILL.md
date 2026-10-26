---
name: a2h-build
description: Trigger: `$a2h-build` or natural language. Validate plugin config and run hvigorw assembleHap on the HarmonyOS repo
---

> Codex skill (converted from the `a2h-build` slash command). Invoke with `$a2h-build`, or pick it in `/skills` (the default_prompt below auto-runs). Codex has no custom slash commands, so the `$` prefix replaces `/`.


> **Windows:** never go through `bash`. Use `powershell -NoProfile -ExecutionPolicy Bypass -File .migbot\bin\a2h-tool.ps1 <validate|build>` and `.migbot\bin\a2h.exe <subcommand>` (see `$a2h-init` §0).

1. Run `.migbot/bin/a2h-tool validate`. If it returns `{ok:false}`, list each failure to the user, suggest running `$a2h-init` to fix paths, and stop.
2. Otherwise run `.migbot/bin/a2h-tool build`. Stream output. Report final exit code.
3. Report this stage's token usage: run `Bash: .migbot/bin/a2h mark-stage a2h-build`. Best-effort and consent-gated — ignore its exit status (it never affects the build result).
