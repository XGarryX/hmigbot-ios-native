---
name: a2h-build-zh
description: 触发：`$a2h-build-zh` 或自然语言。校验插件配置并在 HarmonyOS 仓上跑 hvigorw assembleHap
---

> Codex skill (converted from the `a2h-build-zh` slash command). Invoke with `$a2h-build-zh`, or pick it in `/skills` (the default_prompt below auto-runs). Codex has no custom slash commands, so the `$` prefix replaces `/`.


> **Windows：** 绝不走 `bash`。改用 `powershell -NoProfile -ExecutionPolicy Bypass -File .migbot\bin\a2h-tool.ps1 <validate|build>` 与 `.migbot\bin\a2h.exe <子命令>`（见 `$a2h-init` §0）。

1. 跑 `.migbot/bin/a2h-tool validate`。返回 `{ok:false}` → 把每条失败列给用户，建议跑 `$a2h-init` 修正路径，然后停下。
2. 否则跑 `.migbot/bin/a2h-tool build`。流式输出。报告最终退出码。
3. 上报本阶段 token 用量：跑 `Bash: .migbot/bin/a2h mark-stage a2h-build`。尽力而为、受授权门控——忽略其退出码（绝不影响构建结果）。
