<!-- when: 所有 Stage 执行完毕后生成 spec/migration-report.md（§10）时加载 -->
<!-- topics: 迁移报告, migration-report, Stage 详情, Skill 使用统计, 页面状态汇总 -->

# a2h-execute 迁移报告模板

> 由 `a2h-execute/SKILL.md` §10 引用。所有 Stage 执行完毕后，按本模板生成 `spec/migration-report.md`。

```markdown
# 迁移报告

- 执行时间: YYYY-MM-DD
- 三阶段执行: Stage 1 → Stage 2 → Stage 3

## 总览

| 阶段 | 任务数 | 成功 | 失败 | 编译状态 |
|------|--------|------|------|---------|
| Stage 1: UI Pipeline | X pages | a | a' | PASS/PARTIAL |
| Stage 2: Feature Base | 7 tasks | b | b' | PASS/FAIL |
| Stage 3: Feature Slices | N slices × 4 steps | c | c' | PASS/PARTIAL |
| **总计** | **M** | **S** | **F** | |

## Stage 1 详情: UI Pipeline

| Batch | 页面数 | 成功 | 失败 | 编译修复轮数 |
|-------|--------|------|------|------------|
| Batch 1 | 3 | 3 | 0 | 2 |
| Batch 2 | 4 | 3 | 1 | 5 |

### 页面转换清单
| 页面 | Android 来源 | 状态 | 输出文件 |
|------|-------------|------|---------|
| MainPage | MainActivity | converted | pages/MainPage.ets |
| HomePage | HomeFragment | converted | pages/HomePage.ets |

## Stage 2 详情: Feature Base

| 任务 | Skill | 状态 | 产出文件数 |
|------|-------|------|-----------|
| Base-1: Models | arkts-data-layer | SUCCESS | 5 |
| Base-2: Database | arkts-data-layer | SUCCESS | 3 |
| Base-6: 公共组件库 | component-builder | SUCCESS | 8 |

## Stage 3 详情: Feature Slices

| Slice | 功能 | Step 3a | Step 3b | Step 3c | Step 3d/3e | 状态 |
|-------|------|---------|---------|---------|------------|------|
| Slice 1 | 播放功能 | SUCCESS | SUCCESS | SUCCESS | WIRED+VERIFIED | PASS |
| Slice 2 | 订阅功能 | SUCCESS | SUCCESS | SUCCESS | WIRED | VERIFIED | PASS |
| Slice 3 | 搜索功能 | SUCCESS | SUCCESS | FAILED | - | - | FAIL |

## Skill 使用统计

| Skill | 调用次数 | 被覆盖次数 |
|-------|---------|-----------|
| a2h-activity-converter | 12 | 0 |
| arkts-data-layer | 8 | 0 |
| arkts-state-manager | 6 | 0 |
| hmos-builder (agent) | 15 | 0 |
| arkts-knowledge-verifier | 2 | 0 (追加) |

## 覆盖记录

| Task | 阶段 | 原建议 | 实际使用 | 覆盖原因 |
|------|------|--------|---------|---------|
| Slice 3 Step 3c | Stage 3 | data-layer | data-layer + media-playback | 功能涉及音频播放 |

## 产出文件清单

| 文件路径 | 来源阶段 | 状态 |
|---------|---------|------|
| entry/src/main/ets/pages/MainPage.ets | Stage 1 | NEW |
| entry/src/main/ets/models/Episode.ets | Stage 2 | NEW |
| entry/src/main/ets/viewmodels/PlaybackViewModel.ets | Stage 3 | NEW |

## FAILED 列表

| 阶段 | Task | 失败原因 | 建议处理 |
|------|------|---------|---------|
| Stage 3 | Slice 3 Step 3c | API 不存在 | 手动排查 API 兼容性 |

## 页面状态汇总

| 状态 | 数量 |
|------|------|
| verified | X |
| converted | Y |
| pending | Z |
| FAILED | W |

## 最终编译

- 状态: SUCCESS | FAILED
- 剩余错误: (如果 FAILED)

## Final Structural Closure

| 项 | 值 |
|----|----|
| final_state | PASS / ESCALATED / ROLLED_BACK |
| verdict | CONVERGED / STALLED / REGRESSED / EXHAUSTED |
| 迭代轮数 | N |
| evidence | spec/execution/autofix-log/round-<R>/loops-final-structural-closure.json + spec/execution/briefs/final_structural_closure_brief.md |
```
