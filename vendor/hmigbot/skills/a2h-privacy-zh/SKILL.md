---
name: a2h-privacy-zh
description: 触发：`$a2h-privacy-zh` 或自然语言。查询或变更 migbot 数据档位。子命令：status / accept / deny / off。
---

> Codex skill (converted from the `a2h-privacy-zh` slash command). Invoke with `$a2h-privacy-zh`, or pick it in `/skills` (the default_prompt below auto-runs). Codex has no custom slash commands, so the `$` prefix replaces `/`.

> **Windows：** 下文所有 `.migbot/bin/a2h …` / `bash .migbot/bin/a2h-agreement …` 调用对应为 `.migbot\bin\a2h.exe …` / `powershell -NoProfile -ExecutionPolicy Bypass -File .migbot\bin\a2h-agreement.ps1 …`——绝不走 `bash`（见 `$a2h-init` §0）。


按 用户本次输入（作为命令参数） 分派：

| 用户本次输入（作为命令参数） | 行为 |
|---|---|
| 空 / `status` | §A — 显示当前状态 |
| `accept` / `agree` / `yes`（任意大小写） | §B — 展示协议并参与，启用 migbot |
| `deny` / `disagree` / `no`（任意大小写） | §C — 拒绝（禁用 migbot） |
| `off` / `stop` / `disable`（任意大小写） | §D — 关闭全部上报 |
| 其他任何输入 | 打印下面的用法块并退出，不修改任何内容 |

用法：

```
$a2h-privacy            # 显示当前数据档位
$a2h-privacy status     # 同上
$a2h-privacy accept     # 先展示协议，再加入 FULL 档
$a2h-privacy deny       # 拒绝计划——禁用 migbot（不上报任何数据）
$a2h-privacy off        # 关闭全部上报（任何数据都不离开本机）
```

> **参与是二元的**（协议全文：`.migbot/policies/user-experience-improvement-plan.<language>.md`）。参与本计划是使用 migbot 的前提：
> - **已参与**（`telemetry_consent: "granted"`）——migbot **已启用**；上报全部工作过程产物类别。
> - **已拒绝**（其他任意值：`"denied"` / `"off"` / 未设，或一次性环境变量 `A2H_TELEMETRY_OFF=1`）——migbot **已禁用**（从 `$a2h-spec` 起的迁移流水线拒绝运行），且**不上报任何数据**。

---

## §A. status

1. 读 `.migbot/config.json`。
   - 文件缺失 → 告诉用户 `"本工程未安装 migbot。请先运行 install.sh。"`，然后停下。
2. 解析 `telemetry_consent`、`telemetry_consent_at`、`migbot_session_id`、`language`（缺失则回退 `en`）。
3. 把 `telemetry_consent` 映射为状态：`granted` → **已参与（migbot 已启用）**；其他任意值 → **已拒绝（migbot 已禁用）**。
   - 可选：跑 `Bash: .migbot/bin/a2h status --json`（非零退出则忽略）查看本地 outbox 状态；若显示有排队上传，回显其条数。
4. 打印（只要存在 `migbot_session_id` 就回显——它是日后申请删除数据的凭据，提醒用户保存）：

   > ```
   > ── migbot 参与状态 ──
   > 状态：<已参与——migbot 已启用 / 已拒绝——migbot 已禁用>
   >   已参与 → migbot 可运行；上报 代码行数 + 应用名 + Token 用量 + 构建日志 + 回顾报告
   >   已拒绝 → migbot 被禁用（迁移流水线拒绝运行），且不上报任何数据
   > 上次变更：<telemetry_consent_at，或 "(从未设置)">
   > 删除凭据（请保存）：
   >   migbot_session_id: <migbot_session_id，或 "(尚无——在 $a2h-init 时生成)">
   >   install_id:        <取自 `a2h status --json` 的 install_id，或 "(无)">   ← 同意按机器计，一台机器覆盖其全部工程
   >   （要删除数据，把 install_id（或 migbot_session_id）发送至协议第八条所列隐私邮箱。）
   > 协议全文：.migbot/policies/user-experience-improvement-plan.<language>.md
   >
   > 管理命令：
   >   $a2h-privacy accept   参与计划并启用 migbot（会先展示协议全文）
   >   $a2h-privacy deny     拒绝——禁用 migbot
   >   $a2h-privacy status   查看当前状态
   > 你也可以手动编辑 .migbot/config.json 的 telemetry_consent 字段。
   > ```

---

## §B. accept

1. 读 `.migbot/config.json`：
   - 文件缺失 → 告诉用户 `"本工程未安装 migbot。请先运行 install.sh。"`，停下。
   - 解析 `language`（缺失则回退 `en`）、`telemetry_consent`、`agreement_version`、`migbot_session_id`。
   - **安装级门控——每台机器只同意一次。** 先跑 `Bash: .migbot/bin/a2h init-run`（不带参数）：它把本机 `install_id` 写进 config；若用户在本机已做过决定（`~/.migbot/install.json`），会把该决定复制进本工程（stderr 出现 `inherited from install`）。之后重新读取 `telemetry_consent` / `agreement_version`，让下面的幂等门控看到继承后的状态；因此停下时，说 `"本机已同意过，本工程已自动继承"`，不要再展示协议。
   - **幂等门控——已参与则不做任何事。** 静默探测当前协议版本：跑 `Bash: bash .migbot/bin/a2h-agreement --lang <language> --check`，从其 JSON 读 `version`（不弹窗）。若 `telemetry_consent == "granted"` **且** 存储的 `agreement_version` 等于该版本（或探测到的版本为空），说明用户已在当前版本下参与：按 §A 格式打印状态（回显**现有**的 `migbot_session_id`），并追加一行 `"您已参与本计划，未做任何更改。输入 $a2h-privacy deny 可退出。"`，然后**就此停止**。**不**重新展示协议、**不**生成新句柄、**不**改动 config。只有 `unset` / `denied` / 协议版本变更才继续到第 2 步。
2. **以带外方式展示协议（绝不贴进对话）。** 跑 `Bash: bash .migbot/bin/a2h-agreement --lang <language>`，解析其单行 JSON 结论——`{"shown":..,"method":..,"path":..,"version":..,"reason":..}`。**绝不**把协议正文读进/回显到本对话；用户在弹窗/文件里读。按 `shown` 分支：
   - `"popup"` → 告诉用户：`"用户体验改善计划已在单独窗口中打开。若没弹出，请自行打开：<path>。读完后在下方作答。"`
   - `"path"` → 告诉用户：`"请在决定前打开并阅读用户体验改善计划：<path>。（当前环境无法弹窗，请手动打开文件。）"`
   - `"error"`，或 `a2h-agreement` 不可用 / 不在 PATH → 定位不到协议。告诉用户 `"协议文件缺失。请重装 migbot 或联系运营方。同意状态未做任何修改。"`，然后停下——**不要**改 config。
   - 保留 JSON 里的 `version` 作为第 6 步的 `agreement_version`。
3. 指引用户去看协议后，另起一块，输出二选一提示：

   > ```
   > 您是否同意以上协议？请选择：
   >   1) 我接受
   >   2) 我拒绝
   > 请输入 1 或 2：
   > ```

4. **【硬约束】解析用户的下一条输入**——仅当它（忽略大小写、去首尾空白）匹配以下之一才视为**同意**：`1`、`accept`、`agree`、`yes`、`y`、`i accept`、`我接受`、`同意`。**其他任何**输入（`2`、`拒绝`、`deny`、`no`、空、`cancel`、转移话题）一律视为**拒绝**。绝不从上下文推断同意。

   > **确定安装句柄——绝不轮换已有句柄。** 若 `.migbot/config.json` 已有非空的 `migbot_session_id`，**原样沿用**它作为 `<句柄>`（它是删除已上传数据的凭据，此前所有上报都挂在它下面）。只有该字段缺失或为空时才生成：跑 `Bash: uuidgen | tr 'A-Z' 'a-z'`，取其 stdout（不透明令牌——原样记录，不要解析或描述）。句柄用于删除句柄与活跃用户计数，本身**不**等于同意授权。

5. **拒绝** → 拒绝（这会禁用 migbot）：Edit `.migbot/config.json`：`"telemetry_consent": "denied"`、`"telemetry_consent_at": "<当前 ISO-8601 UTC>"`、`"migbot_session_id": "<句柄>"`、`"agreement_version": "<第 2 步的版本>"`；其余字段不动。跳到第 8 步。

6. **接受** → 写 config：
   - 用第 2 步里 `a2h-agreement` 返回的 `agreement_version`（协议文末 `Version: vX.Y`）。若为空则不写该字段。
   - Edit `.migbot/config.json`，写入/更新：`"telemetry_consent": "granted"`、`"telemetry_consent_at": "<当前 ISO-8601 UTC>"`、`"migbot_session_id": "<句柄>"`（已有则保持不变）、`"agreement_version": "<版本>"`；其余字段不动。

7. **接受时**再跑 `Bash: .migbot/bin/a2h init-run --consent granted --migbot-session-id <句柄>`，把同意状态写回 `.migbot/config.json`（失败只是告警——首次 `$a2h-run` 上报时服务端会自动补登）。

8. 复用 §A 的输出格式显示最终状态（回显 `migbot_session_id` 并提醒用户保存）。

---

## §C. deny（拒绝——禁用 migbot）

1. 读 `.migbot/config.json`：
   - 文件缺失 → 告诉用户 `"本工程未安装 migbot。请先运行 install.sh。"`，停下。
2. Edit `.migbot/config.json`：
   - `telemetry_consent` 设为 `"denied"`；
   - `telemetry_consent_at` 设为当前 ISO-8601 UTC；
   - 其余字段不动（保留已有的 `migbot_session_id`，以便日后删除请求仍有句柄）。
3. 打印：

   > ```
   > ✔ 已拒绝用户体验改善计划（telemetry_consent="denied"）。
   >
   > migbot 现已禁用：从 $a2h-spec 起的迁移流水线将拒绝运行，且不上报任何数据。
   > 参与本计划是使用本工具的前提。本地 .migbot/metrics/ 下可能仍有残留产物；
   > 它们绝不会被发送。要清理本地缓存：  rm -rf .migbot/metrics/
   >
   > 随时可重新启用：  $a2h-privacy accept
   > 要删除已上传到服务端的历史数据，按协议第八条联系我们（提供 migbot_session_id，
   > 可用 $a2h-privacy status 查看）。
   > ```

---

## §D. off（deny 的同义词——同样禁用 migbot）

二元模型下 `off` 是 `deny` 的同义词（都拒绝并禁用 migbot）。

1. 读 `.migbot/config.json`：
   - 文件缺失 → 告诉用户 `"本工程未安装 migbot。请先运行 install.sh。"`，停下。
2. 跑 `Bash: .migbot/bin/a2h init-run --consent denied`，把拒绝状态写回 `.migbot/config.json`（会把 `telemetry_consent` 设为 `"denied"`；已有的 `migbot_session_id` 会保留，以便日后删除请求仍有句柄）。
3. 打印与 §C 相同的"已禁用"提示，提醒用户 `$a2h-privacy accept` 可重新启用 migbot，并说明一次性环境变量关闭开关 `A2H_TELEMETRY_OFF=1`——导出它后，本次会话无论授权状态如何，运行时都不上报任何数据。

---

## 注意

- 所有时间戳必须是 ISO-8601 UTC（如 `2026-05-26T10:30:00Z`）。
- `$a2h-privacy accept` **必须**在询问前先把协议展示给用户——经 `a2h-agreement` 带外展示（弹窗，或无 GUI 环境下给出文件路径）。**绝不**在未展示协议的情况下写 `granted`；那构成"披露不足"，违反协议本身。协议**绝不**贴进对话：弹窗/路径把全文带外展示，避免占用 agent 上下文。若无法弹窗（WSL / Git Bash / 无头 / macOS 沙盒），脚本降级为打印路径——它**不**回退到打印正文，你也不应。
- 参与是**二元**的：拒绝本计划（`deny`/`off`，或 `A2H_TELEMETRY_OFF=1`）会完全禁用 migbot 且不上报任何数据——没有"最小档"的中间状态。只有 `granted` 才启用本工具。与用户沟通时务必讲清这一点。
- §A–§D 中，若**任何**步骤失败（文件缺失、Edit 出错、用户取消），**不要**写 `granted`；安全默认是保持 config 不动。
- 绝不从本命令编辑 `.agents/skills/` 或 `.claude/agents/`。只动 `.migbot/config.json`。
