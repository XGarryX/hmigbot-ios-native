---
name: a2h-join
description: 子代理 join 协议工具库：由派发型 skill 的 join 点调用 join_gate、wait_for_artifact 和 audit_join_coverage，核验真实完成观察及产物。不要用于独立迁移阶段或业务行为验收。
metadata:
  type: tool
  domain: migration
  tags:
  - utility
  - migration
---

> **iOS 源输入适配**：执行源分析/源设备操作前，读 [原生输入协议](../a2h-spec/references/native-input.md)。它仅替换平台输入；原阶段、模板、规则、门禁、模式和 target 侧执行保持 1.5.2。

> **路径约定**：下文 `$SKILLS_ROOT` = 本套 skills 的安装根目录。执行任何脚本前先设一次：`SKILLS_ROOT="$(cd "$(dirname 本SKILL.md)/.." && pwd)"`（用户级安装=`~/.agents/skills`；项目级=`<project>/.agents/skills` 或 `<project>/skills`）。

# a2h-join — 子代理收口协议零件库

## 宿主任务范围

顶层及内部任务都通过实际 `CODEX_THREAD_ID` 唯一定位宿主 sessions 中自身完整原生文件，核对第一条 `session_meta` 的身份。顶层使用当前项目；内部子任务自己派发、自己收口时，必须传 `--project` 的真实绝对路径以及 `--rollout` 的自身原生文件。仅检查其直接孩子，孙任务由对应派发者收口。继承的 `metadata.cwd` 与目标不同必须披露，并检查旧目录未被误写。

分流前先根据实际 `CODEX_THREAD_ID` 定位宿主 sessions 中当前任务自身的元数据，子任务误传父会话日志也会拒绝，不得借顶层分流绕过身份核对。事后审计的哈希及字节数来自本次解析的同一批完整原始字节；文件后续增长不改写已观察记录的指纹。

此适配修复固定层级漏计及按同目录混计不同宿主的问题；原二进制保持不变。判定以原程序黑盒实测为准：曾在 `list_agents` 观察到 completed 即保留该事实；原程序也存在缺状态但契约齐全的 `via-contract` 兼容放行。技能执行仍必须先真实观察 completed、事前写 expected-set，不能用兼容放行替代完成观察。所有派发的任务名须在完整宿主历史内唯一，带尝试/轮次后缀；同名重用会拒绝。

已登记尝试的最后一次派发返回后，必须再次单独调用当前派发者子树的完整 `list_agents`；与派发并行的列表、窄范围或其他筛选结果不能代替。明确失败的派发仍要补派该请求并完成，无可识别请求名的失败须排查；不能以零句柄或不相关任务完成放行。瞬时列表错误保留诊断，错误返回后可用新的完整有效列表恢复。复用已完成代理执行 followup/resume 时，技能须重新 wait 并确认本轮 completed，不能借原程序的历史 completed 兼容行为提前结束。

事后 audit 使用同一作用域，只读取原生日志，记录真实路径、线程身份和 SHA-256，不写 join 账本，不代替实际 join。实际运行仅使用宿主 sessions 中未经修改的原始文件；对照夹具只用于回归。原入口支持的状态、契约检查、静态豁免和账本格式保持一致；未绑定 spawn 返回值不得以零句柄放行。日志更换物理文件时暂停排查，不拼接记录。

用户授权同会话从空工程重跑且旧尝试失败时，先读 [核验恢复与尝试登记](references/recovery.md)。只有完整归档、核验空备份、恢复并安装后才能登记新尝试。Gate 完整解析原日志并核对真实登记调用及成功输出、恢复证据和实现指纹；当前任务仍按原门禁验收，旧失败留在独立历史审计。重复 bootstrap 不移动边界。状态丢失或额外 begin 调用须停止排查，不能删除记录来放行。

## 背景（为什么需要它）

Codex 的子代理完成后**不会**唤醒主会话——结果必须由主会话主动循环 `wait_agent`
再经 `list_agents` 确认取回。协议全文（五条款）在各派发型 skill 顶部的
dispatch banner 里；本 skill 提供三个机械零件，把两类实测事故变成脚本可拦：

- **静默卡死**：模型"字面等待"结束回合（issue #23，AIPPT 断网后挂 4.5h）
- **假交接**：completed ≠ 验收——子代理报完成但产物缺失（实测：7 个分片
  agent 派完即停、functional_points 从未合并）

## 三个零件

### 1. join_gate.py — 收口硬闸（join 点必调）

```bash
python3 $SKILLS_ROOT/a2h-join/scripts/join_gate.py --project . --join-point <名字>
```

- 机械枚举本次实际宿主尝试的全部 `spawn_agent` 句柄（不信模型自报）
- 按最新 `list_agents` 出参判 completed / OUTSTANDING
- 对 completed 按 expected-set 契约或原子信封验产物完整性
- exit 0 → 追加 `spec/a2h/_work/join-ledger.jsonl`；exit 1 → 打印缺口清单，
  **禁止发完成报告/进下一阶段**；exit 3 → 按提示补信息（如先调一次 list_agents）
- 条款⑤ fire-and-forget 豁免 = 脚本内静态 allowlist（改表须过评审），
  正文 `[fire-and-forget]` 声明只是文档层

### 2. wait_for_artifact.py — 活性探针（条款②辅助）

```bash
python3 $SKILLS_ROOT/a2h-join/scripts/wait_for_artifact.py --path 'entry/**/*.ets' --window 120
```

⚠️ **不是 join oracle**——完成判定唯一权威 = `list_agents` 的
`{"completed": …}`；文件会中途落盘，存在/条数 ≠ 完成（两条实测事故铁律）。
本脚本只回答"产物还在长吗"：exit 0=活；exit 2=零增长（结合连续 wait 超时
按条款②判死活）。

### 3. audit_join_coverage.py — 事后审计（回归 oracle + ledger 防伪）

```bash
python3 $SKILLS_ROOT/a2h-join/scripts/audit_join_coverage.py <rollout.jsonl>... \
    [--project <项目绝对路径>] [--ledger spec/a2h/_work/join-ledger.jsonl] [--json out.json]
```

对每个句柄判 joined / fire-and-forget / ORPHAN，出句柄回收率；
`--ledger` 做防伪交叉验证（ledger 声称 joined 但 rollout 无 completed 观测
= 伪造/失配）。
实际宿主调用只接受自身一个原始文件；历史多文件对照仅用于离线回归。已登记尝试的账本必须匹配 attempt 身份及当时读取的原始字节快照，不能借用稍后才出现的完成观察。

## expected-set 契约（治"completed 但产物缺失"）

并行派发（T1 类 join 点）在 **spawn 前**由派发方落盘：

```json
// spec/a2h/_work/expected_<join点>.json
{"join_point": "stage1_batch2",
 "task_names": ["conv_page_*"],
 "artifacts": [{"path": "entry/src/main/ets/pages/*.ets",
                "min_count": 8, "min_bytes": 200, "json": false}]}
```

- 契约必须来自**派发方**——不认子代理自报 manifest（摸鱼者的 manifest
  会与其半截产物完全吻合）
- 无法预知产物集的点退回**原子信封**：子代理最后一步 temp+rename 写
  `spec/a2h/_work/done/<task_name>.done`
- `task_name` 必须唯一化（带 page-id/slice-id/round-N 后缀），这是
  task_name↔completed 机械配对不误配的前提

## 判定表（audit / gate 共用语义）

| 状态 | 判定 |
|---|---|
| completed + 契约/信封通过 | ✅ joined |
| 静态 allowlist 命中 | ⏭ fire-and-forget |
| Gate 摘要列明 + 指定 join 点的跨 Gate 存活 | ✅ alive-across-gate(declared) |
| 死句柄已按条款②断点重派 | ✅ dead-redispatched（原句柄免 FINAL） |
| completed 但契约 FAIL 且未重派 | ❌ completed-but-incomplete |
| 其余悬空 / 无 gate 记录即发完成报告 | ❌ 漏收 |

## 职责边界

- "做错了"（内容级）不归本套管——gate 验齐不齐/格式对不对；内容对错归
  verify / reviewer 轮（反摸鱼质检另有闭环）
- 沙箱读不到 `~/.codex/sessions/` 时 gate 退化：只验产物契约（--rollout
  显式传文件仍可全功能），句柄枚举交事后审计
