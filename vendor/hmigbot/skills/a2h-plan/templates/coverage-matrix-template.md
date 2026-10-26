<!-- when: 覆盖率校验（§7）输出 coverage-matrix.md 时加载 -->
<!-- topics: coverage-matrix, Feature Gaps, UI Page Gaps, Wiring Ownership Map, 分层校验 -->

# coverage-matrix.md 完整模板

§7 覆盖率校验通过后输出 `spec/baseline/plans/coverage-matrix.md`。各失败表（Placeholder / Complex Slice anchor / 对接点归属）只在对应校验不通过时填行，通过则留空表头。

```markdown
# Coverage Matrix

## Summary
- Feature 覆盖率:
  - P0 (V1): X/Y (Z%) — 必须 100%
  - P1 (V1): X/Y (Z%) — 建议 >= 80%
  - P2 / V2 / Skip: X 个 GAP（允许）
- UI 页面覆盖率: X/Y (Z%)
- Placeholder trigger 白名单率: 100% ✓（直接对 spec/placeholder-registry.md 校验——plan 期占位直写 registry，无中转副本）
- Complex Slice anchor 完整率: 100% ✓（直接读 feature spec 顶部 anchors 校验路径存在性）
- 对接点归属率: 100% ✓
- 分层校验 5 项（索引对应 / spec_refs 存在 / 快照一致 / 零复述 / 状态交叉）: PASS ✓

## Feature Gaps
| F-ID | 功能名 | 优先级 | 版本 | 状态 |
|------|--------|--------|------|------|
| F-xxx | ... | P1 | V1 | MISSING |

## UI Page Gaps
| 序号 | 页面 | 优先级 | 状态 |
|------|------|--------|------|
| 00XX | XxxPage | P1 | MISSING |

## Placeholder 校验失败
| P-ID | 所属 Slice | 失败原因 |
|------|-----------|---------|
| P-S3-002 | Slice 3 | trigger_condition 含黑名单关键词"等真机" |

## Complex Slice anchor 校验失败
| Slice | feature | 失败原因 |
|-------|---------|---------|
| Slice 5 | F-007 vip | complexity=complex 但 android_source_anchors 为空 |

## Deferred
| F-ID | 功能名 | 优先级 | 版本 | 原因 |
|------|--------|--------|------|------|
| F-xxx | ... | P2 | V2 | 延期到 V2 |

## Full Feature Matrix
| F-ID | 功能名 | 优先级 | 版本 | 覆盖 Slice | 状态 |
|------|--------|--------|------|-----------|------|
| F-xxx | ... | P0 | V1 | Slice 1 | COVERED |

## Full UI Page Matrix
| 序号 | 页面 | 优先级 | 覆盖 Batch | 状态 |
|------|------|--------|-----------|------|
| 0001 | MainPage | P0 | Batch 1 | COVERED |

## Wiring Ownership Map
> 由 §7 第 8 项跨切片接线归属检测产出。供 a2h-execute §3a converter 计算 forward-ref `resolve_by`。

| 文件 | handler | slot | owning_slice | 类型 |
|------|---------|------|--------------|------|
| pages/CreateOutLinePage.ets | onGenerateClick | | Slice 1 | owned（首切片） |
| components/TemplateTabComponent.ets | onSearchClick | | Slice 10 | cross_slice（文件由 Slice 6 创建） |

> slot 可选：仅同 `(文件,handler)` 落在不同槽位（Tab 槽位 / builder 名）时填，作 P2 撞键区分；留空时退化为二元键，行为不变。

## Skill Routing Map（各 slice Step 行 `suggested_skills+` 增量汇总）
> 派生视图：从 `slices/*.md` 的 Step 行 `suggested_skills+:` 汇总，供一处审阅 skill 分布（L1 索引不承载 skill 路由）。默认映射（a2h-plan §4 表：3a=converter/3b=state-manager/3c=data-layer/3d=closer 链）**不列**，只列差异化增量；无增量的 slice 省略。

| Slice | Step | suggested_skills+（增量） |
|-------|------|--------------------------|
| Slice 1 (F004) | 3b | arkts-login |
| Slice 3 (F005) | 3b / 3c | arkts-payment / arkts-payment, arkts-webview |

## 对接点归属校验失败
| feature spec | 对接点 | 失败原因 |
|--------------|--------|---------|
| F-005.md | TemplateTabComponent.onSearchClick | 无任何 Slice 的 integration_points / cross_slice_edits 认领 |

## 分层校验失败（§7 分层校验 5 项，通过则留空表头）
| 检查项 | 对象 | 失败原因 |
|--------|------|---------|
| 索引↔文件对应 | Slice 12 | detail 指针指向的 slices/slice-12-f012.md 不存在 |
| spec_refs 存在 | Slice 10 | spec_refs 指向的 features/F008-exam-flow.api.md 不存在 |
| 快照一致性 | Slice 4 | 索引 complexity=simple 与 spec 顶部 complex 不一致 |
| 零复述 | Slice 6 | 条目超行数上限（疑似复制 spec 正文） |
| 状态交叉 | F007 | feature-index status=implemented 但 owned 页 0034 仍 pending |
```
