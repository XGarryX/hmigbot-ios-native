<!-- when: a2h-retrospect 生成 §7 回顾报告时加载 -->
<!-- topics: 回顾报告模板, Skill 覆盖分析, 编译错误 Pattern, Confidence 准确度, 设计决策, 操作指引 -->

# 回顾报告模板

> 复制以下结构到 `docs/retrospect-report-YYYY-MM-DD.md` 并填充本轮数据。

---

# 回顾报告

- 回顾时间: YYYY-MM-DD HH:mm
- 迁移报告: spec/migration-report.md
- 验证报告: spec/verify-report.md

## Skill 覆盖分析

- Skill 覆盖率: X% (MATCH: A, OVERRIDE: B, DOWNGRADE: C, UNUSED: D)

| Task | Plan 建议 | 实际使用 | 状态 | 覆盖原因 |
|------|----------|---------|------|---------|
| ... | ... | ... | MATCH/OVERRIDE/... | ... |

## 编译错误 Pattern

| Pattern | 错误特征 | 修复方案 | 频次 |
|---------|---------|---------|------|
| ... | ... | ... | X |

## API 修正

| 原 API | 正确 API | 修正原因 |
|--------|---------|---------|
| ... | ... | ... |

## 确定性修正 Patch

| Patch 文件 | 目标 Skill | 修正数 | 状态 |
|-----------|-----------|--------|------|
| .agents/skills/.../xxx.patch | hmos-fix-build-errors | 3 | PENDING_REVIEW |
| .agents/skills/.../yyy.patch | arkts-knowledge-verifier | 2 | PENDING_REVIEW |

## UI Pipeline vs Feature Pipeline 对比

| 维度 | Stage 1 (UI Pipeline) | Stage 3 (Feature Slice) | 优势方 |
|------|----------------------|------------------------|-------|
| 转换页面数 | X | Y | — |
| 平均编译错误数 | A | B | Stage X |
| verify 通过率 | C% | D% | Stage X |
| UI 还原度 | 高/中/低 | 高/中/低 | Stage X |
| 平均修复耗时 | Xmin | Ymin | Stage X |

**结论**: ...（Stage 1 直接转换 vs Stage 3 Feature Slice 补充的优劣总结）

## Confidence 准确度

| Confidence 等级 | 页面数 | ACCURATE | OVER_ESTIMATED | UNDER_ESTIMATED | 实际通过率 |
|-----------------|--------|----------|----------------|-----------------|-----------|
| high | X | A | B | — | C% |
| medium | X | A | — | B | C% |
| low | X | A | — | B | C% |
| **总计** | X | A | B | C | D% |

**高估案例**（需改进 confidence 评估）:
- Page: ... → 原因: ...

**低估案例**（可升级 confidence）:
- Page: ... → 原因: ...

## 设计决策

| 决策 | 选择 | 原因 | 影响范围 | 状态 |
|------|------|------|---------|------|
| ... | ... | ... | ... | PENDING_APPROVAL |

## 操作指引

### 审核并应用 Patch

```bash
# 1. Review patch
cat <patch-file-path>

# 2. Apply (确认无误后)
git apply <patch-file-path>

# 3. Commit
git add -A && git commit -m "chore: apply retrospect patch <patch-name>"
```

### 审批设计决策

确认上述设计决策后，告诉我"审批通过"，我会将决策写入对应文档。
