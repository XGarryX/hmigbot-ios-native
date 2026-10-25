<!-- when: 双计划生成完成、向用户输出审批门控摘要时加载 -->
<!-- topics: 门控, 审批摘要, Placeholder Registry, briefs 落点 -->

# 双计划审批门控输出模板（§8）

双计划生成后向用户输出以下摘要，等待人工审批后才进入 a2h-execute。

```
## 双计划生成完成

### UI 转换计划 (ui-plan.md)
- 总页面: X 个
- 批次: Y 个 Batch
- ⚠️ Low confidence 页面: W 个（W=0 时省略本行）

### 功能执行计划 (feature-plan.md, plan_format: indexed-v1)
- Base 层任务: 7 个
- Feature Slices: N 个（slice 文件在 plans/slices/）
- 可并行组: M 组（size-1 组非 0 时附理由）

### 覆盖率
- P0 (V1) 功能: 100% ✓
- P1 (V1) 功能: XX%
- UI 页面: XX%

### Placeholder Registry
- 写入位置: spec/placeholder-registry.md（plan 期占位**直接写入**，无 coverage-matrix 中转）
- 总条目: N（全部 status=registered；执行期铸号遵守 _common.md §2.1c 发号协议，登记即占号）

### 骨架审计预演（仅 WARN）
- placeholder 密度 ≥ 5/file 的文件: K 个
- 建议: <列表 / 或 "无"，K=0 时显示无>

### Execute 阶段 brief 落点
- spec/execution/briefs/（由 a2h-execute 启动时自建，填充 batch_NN / base_NN / group_NN brief）

### grill #2 决策清单（追加至 spec/decision-ledger.md）
- 新增 D 编号决策: N 条（C6–C11 / C13–C14 / C17 类目）
- 三方 SDK 策略覆盖率: 100% ✓（所有 thirdparty-sdk placeholder 有对应 C8 决策）
- Gate A 级架构决策覆盖率: 100% ✓（所有 complex Slice 有对应 C7 决策）
- Plan 待修订项: K 条（execute 阶段将按 ledger 覆盖 plan 原文）
- escape 候选: J 条（待 retrospect 评审）

请审阅 spec/baseline/plans/、spec/placeholder-registry.md、**spec/decision-ledger.md**，确认后执行 a2h-execute。

可调整项:
- 调整 Batch 分组或页面排序
- 调整 Slice 执行顺序或并行组
- 修改 suggested_skills
- 增删 Slice 或 Base 任务
- 移动页面到不同 Batch
- **修订 ledger 中的 D 编号决策**（修订后 Plan 待修订项段需同步更新）
```

用户可以：
- 直接确认 → 进入 a2h-execute（execute 按 ledger 查表执行，不再交互式追问）
- 修改后确认 → 进入 a2h-execute
- 要求重新生成 → a2h-plan 重新执行
