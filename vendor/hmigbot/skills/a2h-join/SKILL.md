---
name: a2h-join
description: 子代理 join 协议的机械零件库（收口硬闸 join_gate / 活性探针 wait_for_artifact / 事后审计 audit_join_coverage）。不是可独立触发的流水线阶段——由各派发型 skill 的 join 点显式调用其脚本；用户一般不直接调用本 skill。
metadata:
  type: utility
  domain: migration
  tags:
  - utility
  - migration
---

> **路径约定**：下文 `$SKILLS_ROOT` = 本套 skills 的安装根目录。执行任何脚本前先设一次：`SKILLS_ROOT="$(cd "$(dirname 本SKILL.md)/.." && pwd)"`（用户级安装=`~/.agents/skills`；项目级=`<project>/.agents/skills` 或 `<project>/skills`）。

# a2h-join — 子代理收口协议零件库

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

- 机械枚举本会话 rollout 的全部 `spawn_agent` 句柄（不信模型自报）
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
    [--ledger spec/a2h/_work/join-ledger.jsonl] [--json out.json]
```

对每个句柄判 joined / fire-and-forget / ORPHAN，出句柄回收率；
`--ledger` 做防伪交叉验证（ledger 声称 joined 但 rollout 无 completed 观测
= 伪造/失配）。

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
