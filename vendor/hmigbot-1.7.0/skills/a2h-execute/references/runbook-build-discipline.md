# a2h-execute · 构建修复循环操作纪律

> 本文件由 `a2h-execute/SKILL.md` 原文**逐字搬出**（M1 token 减量：主会话 runbook 只留循环所需，细则集中于此）。读取时机：派 hmos-builder / auditfix 修复 worker、`action=repair`、编译门 `quick_fix`，或 CLI 构建出现 daemon 僵死 / `00303208` / `00303217` / `00305008`。

## 构建修复循环操作纪律

本阶段执行期间，`hmos-fix-build-errors` 或任何构建修复类 subagent（hmos-builder / auditfix 修复 worker）必须遵守以下构建纪律：

### Cache Cleanliness

- `hvigorw clean` 最多执行 **1 次**。禁止 `rm -rf entry/build`（会破坏 hvigor daemon 增量状态）。
- `ohpm install` 只在构建循环开始前执行一次，不在循环内部重复执行。

### Checkpoint 提交

- 每次 `BUILD SUCCESSFUL` 之后必须立刻 `git commit`，提交消息格式：`checkpoint(<wave>): build pass after K fixes`。
- 若 linter 回改导致文件变更，用 `git checkout -- <file>` 恢复而非重新编辑。

### CLI 构建降级策略

出现以下情况时禁止继续 CLI 构建，必须**升级到 IDE 构建**：
- `hvigorw` 在 <1 秒内退出且无编译错误行 → Daemon 僵死，重试 1 次后仍失败则升级
- SDK 路径错误 `00303208`/`00303217` 连续出现 2 次 → 升级
- `module.json5` 语法损坏（`00305008`）连续出现 2 次 → 升级且禁止手动修改 module.json5
- 单个文件被 linter 回改超过 3 次 → 升级，由 IDE 环境验证最终状态

### 降级时输出

```
构建环境已不稳定，无法继续 CLI 构建验证。
请在 DevEco Studio IDE 中 Build → Build HAP(s) 验证项目完整性。
```
