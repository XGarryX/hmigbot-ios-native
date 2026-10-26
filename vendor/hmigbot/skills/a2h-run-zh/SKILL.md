---
name: a2h-run-zh
description: 触发：`$a2h-run-zh` 或自然语言。跑完整 a2h 迁移流水线（spec → plan → execute → verify → retrospect），逐阶段确认并自动续跑。
---

> Codex skill (converted from the `a2h-run-zh` slash command). Invoke with `$a2h-run-zh`, or pick it in `/skills` (the default_prompt below auto-runs). Codex has no custom slash commands, so the `$` prefix replaces `/`.


用户本次输入（作为命令参数） 忽略。`$a2h-run` 不转发参数。要做特性级 spec，直接调用 `a2h-spec` skill 并传特性名。

## 目标

按序串接五个 pipeline 阶段 skill，每阶段间暂停让用户确认，再次进入时从上次停下的位置自动续跑。任何阶段失败立即停下。

## 1. 检测模式

读 cwd 下的 `.migbot/config.json`。

- 文件不存在 → 停下并告诉用户：`"migbot 还没装到这个工程里。先跑 install.sh。"`
- 读 `confirmed` 键。
  - `confirmed != true`（false、缺失或其他值）→ 停下并告诉用户：`"配置还没确认。先跑 $a2h-init 确认 android / harmonyos / hvigorw 路径，再回来跑 $a2h-run。"`。不要继续。
## 2. 探测完成标记

按序检查每个阶段的标记文件来决定续跑起点。**所有**标记都在的阶段才算完成。

| # | 阶段                | 标记                                                                                  |
|---|--------------------|----------------------------------------------------------------------------------------|
| 1 | `a2h-spec`         | `spec/baseline/ui-manifest.md` 和 `spec/baseline/feature-index.md`                     |
| 2 | `a2h-plan`         | `spec/baseline/plans/ui-plan.md` 和 `spec/baseline/plans/feature-plan.md`              |
| 3 | `a2h-execute`      | `spec/migration-report.md`                                                             |
| 4 | `a2h-verify`       | `spec/verify-report.md`                                                                |
| 5 | `a2h-retrospect`   | 至少一个匹配 `docs/retrospect-report-*.md` 的文件 **和** 至少一个匹配 `.migbot/metrics/*/retrospect.done` 的文件 |

> **重要：两个 marker 文件都必须由 a2h-retrospect skill 的收尾步骤产出。** 特别是 `retrospect.done` 必须由 `.migbot/bin/a2h mark-stage a2h-retrospect` 作为副产物生成；该调用会写出 stage-marks fact 并落下 sentinel（它会剥掉 `a2h-` 前缀，所以文件名是 `retrospect.done`）——`granted` 时上传该 fact、否则静默跳过，**两种情况都满足 marker**。阶段 token 用量不在这里采集：生命周期 hook 会上传会话记录，由服务端解析出用量。**绝不要用 Write/Edit 工具直接创建 `.migbot/metrics/` 下任何文件（含 `retrospect.done`）来"满足"这个 marker**——那会绕开真实采集，写出来的是假数据。如果 marker 缺失，应当回到 a2h-retrospect skill 重跑 `mark-stage`，而不是手工伪造文件。

续跑目标是第一个标记不全的阶段。

- **所有标记都缺** → 从阶段 1 起跑；不提示。
- **部分标记在** → 列已完成阶段并提示：`"已完成阶段：<列表>。从 <下一阶段> 续跑吗？(yes / restart from spec / stop)"`。`yes` → 从续跑目标继续；`restart from spec` → 从阶段 1 重跑；其他 → 停下并提示 `"还没跑任何阶段就停了。"`。
- **五个阶段标记都在** → 提示：`"五个阶段都有完成标记。从 spec 重跑还是停？(restart / stop)"`。`restart` → 从阶段 1 重跑；其他 → 停。

## 3. 跑每个阶段

从续跑目标跑到阶段 5，固定顺序：`a2h-spec`、`a2h-plan`、`a2h-execute`、`a2h-verify`、`a2h-retrospect`。

1. 宣告：`"开始阶段 <N>/5：<id>。"`
3. 阶段步骤完成后，2-3 行总结：列该阶段预期输出路径下新增/修改的文件，一句话产出小结。
4. **收口未回收的子代理（HARD-GATE —— issue #23）。** 若该阶段 skill 派发过后台子代理（`spawn_agent`）且结果尚未取回，**现在**就对每个未回收句柄循环调用 `wait_agent` 收口——超时只代表"还在跑"，继续再调。**句柄未收口时绝不能结束回合**：Codex 里子代理完成不会唤醒本会话，回合一结束整条流水线就静默卡死、没有任何提示（issue #23 的多模块卡死正是这个）。全部收口后再做标记检查。
5. 验证该阶段的完成标记（见 §2）现在都在。任何必需标记缺失 → 视为该阶段失败，按下方失败处理。
   > token 用量上报不再在这里做——每个流水线 skill 在自己的最后一步上报本阶段（`a2h mark-stage <id>`）。这样即便单独触发某个 skill（不经 `$a2h-run`）也会上报。本步除标记检查外无需额外动作。
6. 提示：`"继续下一阶段？(yes / stop)"`
   - `yes` → 下一阶段。
   - 其他 → 停下并提示：`"在 <id> 停下。再跑 $a2h-run 续跑。"`
7. **失败处理。** 若 skill 抛错、打印 `STOP`、或必需标记没生成，停下并提示：`"在 <id> 因错误停下：<一句话总结>。处理完再跑 $a2h-run 续跑。"`。不自动重试。

## 4. 阶段 5 之后

打印最终总结：列五个阶段和它们的产出（仅路径，一行一个）。

然后检查遥测送达情况：跑 `Bash: .migbot/bin/a2h status --json`（非零退出或子命令不存在则忽略——旧版运行时没有它）。若输出显示 outbox 有 pending 或 dead 条目，追加以下提示（仅告知性质——上传由 hook 驱动会自动重试，这里绝不阻塞、绝不代为重试）：

> 提示：还有 <N> 条遥测数据在本地排队，稍后会自动重传。也可以现在手动执行 `.migbot/bin/a2h flush` 立即补传。

然后提示：

> 五个阶段都完成。跑 `$a2h-build` 编译迁出来的代码。
