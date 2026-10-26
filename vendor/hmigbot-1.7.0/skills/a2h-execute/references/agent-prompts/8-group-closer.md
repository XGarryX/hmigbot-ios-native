<!-- when: 派发 Stage 3 group-closer（a2h-closer, mode=group，每 parallel_group 末尾一次）时加载本段 + _common.md -->
<!-- topics: group 收尾派发参数, mode=group, a2h-closer, 五步协议指针 -->

# §8. Stage 3 group-closer 派发（a2h-closer, mode=group）

> **收尾协议单源 = `a2h-closer` agent 定义**（mode=group 五步：跨文件接线 → 资源校验 → 编译 → 结构 fix-forward（max_iter 查表）→ 组单文件 group brief；含读取聚焦契约与 HARD-GATE）；本文件只是派发参数模板。公共占位规则 §2.1 + 单写者纪律见 [`_common.md`](./_common.md)，派发时一并 Read。
> 组粒度通用（**含 size-1 组**：串行降级 / 重试单 slice / 只执行 Slice N——同一派发，slices 单元素）。

派发 Codex 子代理 `a2h-closer`（定义于 `.codex/agents/a2h-closer.toml`），任务提示词：

```
mode=group。你是 Stage 3 parallel_group [{group_id}] 的 group-closer，本组 slice {slice_ids} 的 worker 已完成（各自只写了自身 page/VM/repo）。按你的 agent 定义 mode=group 五步协议执行。

  本组各 slice 文件（plans/slices/，只读调度账本）: {per_slice_files}
    每份含 cross_slice_edits / wires(含 embed) / integration_points（纯结构化对）
  本组产出文件: {group_ets_files}
  组内 slice 复杂度事实（max_iter 查表输入）: {slices_complexity}   # 各 slice 的 complexity
  defer_structural_to_fv: {true|false}                    # 仅末组 true（execute 按索引判定；结构验证交 FV-1）
  Android 源根: {android_source_dir}
  HarmonyOS 工程根: {harmony_project_dir}
```

**HARD-GATE**（主线程侧）：writeback manifest 必产（brief_content 含全部 slice 小节）→ 主线程跑 `apply_writeback.py` 成功（brief 落盘 + 账本翻转）+ `build_status=PASS` + `structural_verdict=CONVERGED` 才算本组 PASS；崩溃恢复 = manifest 在则重跑 apply、绝不重做接线/编译/结构；仅 STALLED/REGRESSED/EXHAUSTED 时按信封 `structural_escalation.state_file` 处置（派专家 repair worker / git rollback / 标 BLOCKED）。
