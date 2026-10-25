# Phase 3 — 准备 spec/fix/round-N/ 目录骨架 + iOS 截图缓存

> 从 SKILL.md §4 Phase 3 抽出。Phase 3 进入时 Read。

在进入逐页截图前，做两件事。

---

## (a) 准备 fix-markdown 目录

```
1. 读 spec/fix/_state.yaml.current_round → 取 N（不存在视为 N=0，并初始化 _state.yaml schema_version=2）
2. 建目录 spec/fix/round-N/ui/_systemic（bash `mkdir -p` / PowerShell `New-Item -ItemType Directory -Force` / python `os.makedirs(...,exist_ok=True)`）
3. 若 spec/fix/round-(N-1)/ui/ 存在 → 缓存所有文件的 frontmatter（id, disposition, disposition_reason, disposition_set_at_round），后续 Step 4.4 写入新 markdown 时按 schema §五 carry forward
4. 若 spec/fix/round-N/ui/ 已有残留（异常退出导致）→ 全部清空（防止遗留旧轮次的 markdown 污染本轮）
5. **物理 carry-forward 未收口 finding**（防"漏检即蒸发"）—— 在第 4 步清空后立即跑：

   逻辑（跨平台 python 实现在下方，语义逐条对应）：
   - PREV = N-1；PREV_DIR = spec/fix/round-{PREV}/ui；CURR_DIR = spec/fix/round-{N}/ui；N>0 且 PREV_DIR 存在才跑
   - 遍历 PREV_DIR/*.md：跳过文件名以 `RESOLVED_` / `CARRYOVER_` / `_` 开头的（已收口 / 已 carry / 系统文件）
   - 读 frontmatter `disposition:`（去空格与引号）；`fixed|skipped|manual_review` → 跳过
   - 其余 carry 到 CURR_DIR/CARRYOVER_{原名去.md}_from_r{PREV}.md：
     · **partial 原样复制**（含 disposition/reason/set_at_round——§五约定 partial 是"fixer 改了等下轮重测"信号，
       重置成 null 会让 visual-verify 把它当普通新 finding 处理，丢失"重测"语义）
     · 其它 → 复制并把 `disposition:` / `disposition_reason:` / `disposition_set_at_round:` 三行值重置为 `null`
   - 末尾打印 `[phase3] carry-forward: <条数> findings from round-{PREV}`

   ```text
   python3 $SKILLS_ROOT/arkts-visual-verify/scripts/carry_forward_findings.py <N>
   # （原内联 python -c 已落成脚本，逻辑不变；PowerShell/bash 通用）
   ```

   **设计意图**：
   - **finding 不蒸发**：disposition ≠ fixed/skipped/manual_review 全部带到本轮
   - **partial 信号保留**：唯一例外，原样复制不重置 disposition，让 visual-verify 知道"上轮改过，本轮务必重测同 reach_path"
   - **不阻断流程**：纯文件复制，失败可容忍
   - **不在 Phase 3 判定 stubborn**：顽固 finding 搬移逻辑统一由 Phase 7 持有（详 phase7-stubborn-loop.md），避免双入口
```

---

## (b) iOS baseline 完整性速览

```
1. 统计 screenshots/ios/{trip_id}/ 各 trip 的 baseline png 数（正式 gate 在
   build_batches.py 入口的 check_ios_screenshot.py，这里只输出速览不拦截）：
   "iOS baseline: trip_1={N} 张, trip_2={M} 张"
```

> **注意**：本 skill **不再做"跑 grep 批量预修复"**——批量修复是 visual-fixer 的职责。预修复机会被 visual-fixer 的 systemic 聚合（同根因 ≥3 页 → SYSTEMIC_*.md）覆盖，本 skill 只负责把症状写出来，不主动 grep 改代码。
