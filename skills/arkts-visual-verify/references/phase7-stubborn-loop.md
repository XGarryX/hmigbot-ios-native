# Phase 7 — 顽固 finding 集中冲刺循环

> 在 Phase 6 visual-fixer 派发完成、本 skill 退出前执行。
> 触发：当本轮 ui/ 下存在"顽固 finding"。否则跳过本 phase 直接退出。

## Step 0 触发判定（机械化）

**主代理必跑**（替代 LLM grep + mv + sed 3 步操作）：

```text
python3 $SKILLS_ROOT/arkts-visual-verify/scripts/detect_stubborn.py --round ${N}
# exit 0 = 无顽固 finding，跳过 Phase 7 直接退出
# exit 1 = 已搬 N 个到 spec/fix/stubborn/<finding_id>/，继续下方 mini-round
# exit 2 = schema 异常（升级用户）
```

扫描域：`round-N/ui/` **+ `round-N/feat/`**（2026-08-29 修：原只扫 ui/，功能类顽固单永不入选）。

脚本内部判定：**①必须成立**，且 ②③④ **任一**成立即顽固——
1. frontmatter `disposition` ∉ {`fixed`, `skipped`, `manual_review`}
2. 正文 §6 段已有 ≥ 3 个 attempt 子项，严格按 regex `^### round-\d+ attempt by visual-fixer$` 匹配（schema §6.1 硬约束）
3. **跨轮次 ≥ 3 且仍 open**——同 finding_id（含 CARRYOVER_/RESOLVED_ 前缀归一后）在 ≥3 个不同
   `round-N` 目录出现过。★不看 attempt 数：blocked 类单**不产生 attempt**，用 attempt 当唯一
   判据会让"卡得最死的单永远够不着升级门槛"（实录：模板单跨 round-4/5/6，attempt 仅 2）。
4. **连续 2 轮标 `blocked_by_*`**（frontmatter `disposition` 或 §3 正文含该标记）→ 直接写
   `disposition: manual_review` + `manual_review_reason: blocked_upstream:<阻断源>`，
   **不搬 stubborn/、不进 mini-round**：这类单要的是解除上游阻断，在本页反复修永远无解
   （实录：模板单连续两轮 `blocked_by_startup_gate`，真因在启动门而非模板页）。

命中的 finding **mv** 到 `spec/fix/stubborn/<finding_id>/`，frontmatter 写/改 `stubborn_origin: round-N/ui/<filename>`（脚本处理 CARRYOVER 文件名前缀 + 已存在字段替换不追加 2 个坑）。

**唯一入口**：stubborn 搬移逻辑仅在 Phase 7 Step 0 持有（detect_stubborn.py）。Phase 3 carry-forward 只负责复制未收口 finding，不做 attempt 计数（避免双入口互相绕的反模式）。

## mini-round 流程（单 finding 最多 5 次）

对每个顽固 finding **串行**跑（不并行，防设备冲突）：

```
for attempt in 1..5:
  1. 单页截图：
     - HMOS: hdc 启动 + 按 finding.page_id 导航 + screencap → screenshots/harmony/round-N/stubborn/<finding_id>_attempt{attempt}.jpeg
     - iOS: 同上（baseline 已存在即跳过）
     - sbs: 合成
  2. 派 visual-fixer（focused 模式，prompt 模板见下）
  3. visual-fixer 改完代码 → 追加 §6 `### round-{N} attempt by visual-fixer` 子段
     <!-- attempt 标题用 N=主轮号；mini-round 子序号 1..5 写入"未做的事"段开头如 "[mini-round 2/5]"。
          5 次 attempt = 5 个相同标题段（不是共享 1 个段），grep -c 准确数到 attempt 总数。 -->
  4. 重复 1（重测）：
     - sbs similarity ≥ 0.95 且无 CRASH → Phase 7 framework（verifier 角色）标 `disposition: partial` + 移回原 ui/ 目录 → break
     - 否则继续下一 attempt
  5. attempt == 5 仍未通过：
     - Phase 7 framework 写 `disposition: manual_review` + `disposition_reason: "stubborn 5 focused attempts exhausted, see §6"`
     - 移回原 ui/ 目录 + _summary.md 顶部追加 ⚠️ 段提示用户介入

> **disposition 写入主体**：Phase 7 第 4/5 步的 disposition 由 Phase 7 framework 主流程（verifier 角色）写，**不是 fixer mini-round**——与 schema §五 "disposition 由 verifier 单一裁判" 一致。
```

## 主流程暂停

Phase 7 期间主 Phase 暂停，不并发跑其他 finding 的处理。Phase 7 全部 stubborn finding 处理完后才退出 skill。

## focused 模式 visual-fixer prompt 模板

```
你正在处理顽固 finding（已失败 N 轮，本轮第 X/5 次集中冲刺）。

[路径] spec/fix/stubborn/<finding_id>/<finding>.md
[要求]
1. 先 Read 上述 markdown，特别是 §6 全部历史尝试
2. **禁止**重复历史 §6 中任一条"假设根因 + 改动摘要"组合
3. 必须显式在新 attempt 的"未做的事 / 已排除的可能"列出本次为何选择新方向
4. 改完代码后追加 §6 子段（标题严格 `### round-{N} attempt by visual-fixer`，N=主轮号；mini-round 子序号写"未做的事"段开头）
5. 改动落盘即可，不动 git、不重编、不重测（Phase 7 主流程会重截）
```

## 单 finding 处理时间预算

~5 min/attempt × 5 = ~25 min。3 个并发顽固 = ~75 min。超过 90 min 主流程要在 _summary.md 显式记录。

## _state.yaml 增量字段

```yaml
stubborn_loops:
  <finding_id>:
    started_at_round: <N>
    attempts: <1..5>
    last_attempt_at: <timestamp>
    resolved: <true|false>
```
