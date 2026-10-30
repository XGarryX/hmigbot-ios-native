<!-- when: 派发 Stage 3 group-closer（a2h-closer, mode=group，每 parallel_group 末尾一次）时加载本段 + _common.md -->
<!-- topics: group 收尾派发参数, mode=group, a2h-closer, 五步协议指针 -->

# §8. Stage 3 group-closer 派发（a2h-closer, mode=group）

> **收尾协议单源 = `a2h-closer` agent 定义**（mode=group 五步：跨文件接线 → 资源增量合并及引用校验 → 编译 → 结构 fix-forward（max_iter 查表）→ 组单文件 group brief；含读取聚焦契约与 HARD-GATE）；本文件只是派发参数模板。公共占位规则 §2.1 + 单写者纪律见 [`_common.md`](./_common.md)，派发时一并 Read。
> 组粒度通用（**含 size-1 组**：串行降级 / 重试单 slice / 只执行 Slice N——同一派发，slices 单元素）。

派发 Codex 子代理 `a2h-closer`（定义于 `.codex/agents/a2h-closer.toml`），任务提示词：

```
mode=group。你是 Stage 3 parallel_group [{group_id}] 的 group-closer，本组 slice {slice_ids} 的 worker 已完成（各自只写自身page/VM/repo和独占资源增量），均已提交资源增量或显式空提交。按你的 agent 定义 mode=group 五步协议执行。

  本组各 slice 文件（plans/slices/，只读调度账本）: {per_slice_files}
    每份含 cross_slice_edits / wires(含 embed) / integration_points（纯结构化对）
  本组产出文件: {group_ets_files}
  资源作用域: {resource_scope}                           # init声明计划项集合与本组相同
  唯一资源收尾者: {resource_closer}
  收尾资源任务: {closer_resource_task_or_none}            # sweep新资源也需预登记再submit
  组内 slice 复杂度事实（max_iter 查表输入）: {slices_complexity}   # 各 slice 的 complexity
  defer_structural_to_fv: {true|false}                    # 仅末组 true（execute 按索引判定；结构验证交 FV-1）
  compile_policy: {per-group|stage3-pilot}                # 从冻结 dispatch policy 读取，默认 per-group
  dispatch_checkpoint: {当前已审checkpoint}
  iOS 源根: {ios_source_dir}
  HarmonyOS 工程根: {harmony_project_dir}
```

**集中编译试点分支**：仅冻结 `stage3-pilot` 时按 [依赖调度](../dependency-dispatch.md) 执行生成收口：brief 明示 `GENERATED_PENDING_COMPILE` 和 `deferred-to-stage3-gate`，compile 迭代为 0、converged=false，不伪报 PASS；原结构/资源/占位门照做。manifest 不含 ui_manifest / feature_index 进度翻转，信封返回 `dispatch_checkpoint`；主线程原 apply 加 `--generated-checkpoint <dispatch_checkpoint>` 及资源参数，之后以原 indexed receipt 调 `indexed-dispatch checkpoint`。全部组关闭后仍须集中真实构建和原 FV；当前资源/构建证明过期则阻止 FV。默认 per-group 沿下面原编译条件。

**HARD-GATE**（主线程侧）：当前资源增量全部齐备、merge成功且收据后像有效 → writeback manifest 必产（brief_content含全部slice小节）→ 主线程跑 `apply_writeback.py ... --resource-scope <resource_scope> --resource-closer <resource_closer>` 成功，加原有编译/结构条件后才算本组PASS。信封必须返回 `resource_scope`、`resource_closer`、`resource_merge_receipt`。编译/结构修复又改变资源会使旧收据失效：收停写者，沿已审责任建立新资源作用域并重新提交/合并/核验，不能刷新旧hash或合并后再直写。只有尚未过期的manifest和资源收据可重放；存在pending先recover。原结构异常按 `structural_escalation.state_file` 交主线程处理，不因此自行执行Git回滚。
