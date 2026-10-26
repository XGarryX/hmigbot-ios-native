<!-- when: a2h-plan §3.0 编排派发（P1 三写 A∥B∥C）时加载 -->
<!-- topics: plan 派发参数, kernel 内联, ui-plan writer, base-plan writer, slice writer, 信封契约 -->

# a2h-plan 派发参数模板（编排 P1 三写并行）

> 编排协议与阶段划分单源 = SKILL.md §3.0；本文件只收三个派发的参数模板 + 公共纪律。规则权威在各模板 / SKILL 正文——派发 prompt 不复述规则，只带 MUST-Read 清单与 kernel 数据。

## 公共纪律（三派发通用）

- **MUST-Read**：各派发列出的模板 / references 必须整文件 Read（SKILL Critical 强制加载条款适用于 subagent，跳过 = PROCESS_VIOLATION）。
- **单写者分配**：A→ui-plan.md；B→plans/base-plan.md；C→plans/slices/* + spec/placeholder-registry.md（P1 窗口唯一 registry 写者——B 的 P-B 行信封带回，无并发）；索引 / coverage-matrix 主线程写，agent 禁碰。
- **kernel 只抄不判**：归属消歧 / hub / 横切 / 定号已由主线程 P0 裁决并随 prompt 内联下发；agent 发现 kernel 与 spec 冲突 → 信封报告，禁自行改判。
- **返回 = 信封 ≤30 行**：状态 + 计数 + 路径；禁贴产物正文。
- **派发 prompt 禁复述**模板 / SKILL 已载规则——一行 MUST-Read 指针即可；但任务专属参数（kernel 表 / 清单）不得省略。

## P1-A：ui-plan writer

派发一个通用子代理，任务提示词：

```
生成 spec/baseline/plans/ui-plan.md。MUST 先 Read: a2h-plan/templates/ui-plan-template.md（整文件，分批规则与表格形态以其为准）。
  页面归属表（kernel，只抄不判，含 hub 裁决结果）: {page_owning_map}    # 页 id → 裸 F-ID
  分批输入: spec/baseline/ui-manifest.md（优先级 / confidence / 依赖三源见模板生成规则）
  写权: 仅 ui-plan.md。
```

信封：`batches_count / pages_total / low_confidence_pages[] / kernel_conflicts[]（应空）`。

## P1-B：base-plan writer

派发一个通用子代理，任务提示词：

```
生成 spec/baseline/plans/base-plan.md。MUST 先 Read: a2h-plan/templates/feature-plan-template.md（整文件，「文件二」段为生成规范）+ a2h-plan/references/skill-binding-rules.md。
  输入: spec/baseline/feature-base.md + feature-index.md 共享组件/服务；chain-auth 存在时按 SKILL Step 4.3 表注入 Base 侧 data_chain_refs（L0 / L2-L3 行）
  写权: 仅 base-plan.md；如产生 P-B 占位 → 行全文写入信封带回，禁直写 registry。
```

信封：`base_tasks_count / registry_rows_pending[]（P-B 行全文，主线程 append）/ chain_auth_injected: L0,L2-L3 | N/A`。

## P1-C：slice writer（全量；参数 `{slice_list}` 天然支持将来分片为 K=ceil(N/4) 个同构 writer，协议不变）

派发一个通用子代理，任务提示词：

```
按 a2h-plan SKILL §3b Step 4.0–4.3 生成全部 slice 文件。MUST 先 Read: a2h-plan/SKILL.md（Step 4.0–4.3 为执行规范）+ templates/slice-plan-template.md + templates/placeholder-registry-template.md + references/skill-binding-rules.md。
  slice 清单（kernel 定号，只抄）: {slice_list}       # Slice N ↔ F-ID ↔ spec 路径 ↔ depends_on ↔ tier/depth
  页面归属表: {page_owning_map}
  对接点归属映射: {wiring_owner_map}                  # cross_slice_edits 的 owner 与 resolve_by 依据
  写权: plans/slices/slice-NN-<fid>.md（每文件恰写一次）+ placeholder-registry.md 直写（Step 4.1 原文执行）。
```

信封：`slices_written / per_slice: {N: {placeholders, fwd_refs}} / kernel_conflicts[]（应空）`。
