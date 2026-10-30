<!-- when: 派发 Stage 1 Batch 收尾（a2h-closer, mode=batch，每 Batch 末尾一次）时加载本段 + _common.md -->
<!-- topics: Batch 收尾派发参数, mode=batch, a2h-closer -->

# §2. Stage 1 Batch 收尾派发（a2h-closer, mode=batch）

> **收尾协议单源 = `a2h-closer` agent 定义**（mode=batch 两步：任务资源增量合并及引用核对 → writeback manifest；批内无编译，统一编译在 execute §3d 收口）；本文件只是派发参数模板。公共占位规则 §2.1 + 单写者纪律见 [`_common.md`](./_common.md)，派发时一并 Read。

派发 Codex 子代理 `a2h-closer`（定义于 `.codex/agents/a2h-closer.toml`），任务提示词：

```
mode=batch。你是 Stage 1 Batch [{batch_n}] 的收尾者，本批所有并发 converter 已完成并提交各自的资源增量（无新增也有空提交）。按你的 agent 定义 mode=batch 两步协议执行；统一 merge 后核对引用，不再直写共享资源。

  本批页面: {batch_pages}                    # 序号 + ArkTS 文件路径清单
  本批生成/改动的 .ets: {batch_ets_files}
  资源作用域: {resource_scope}                 # 派发前主线程init，计划项集合与本批相同
  唯一资源收尾者: {resource_closer}             # 与scope.json的closer_id一致
  收尾资源任务: {closer_resource_task_or_none}  # sweep需补资源时，init已将该任务预登记
  iOS 源根: {ios_source_dir}
  HarmonyOS 工程根: {harmony_project_dir}
```

**HARD-GATE**（主线程侧）：全部预期资源提交齐备并合并成功，回读当前 `merge-receipt.json` → writeback manifest 必产 → 主线程跑 `apply_writeback.py ... --resource-scope <resource_scope> --resource-closer <resource_closer>` 成功（brief 落盘 + 账本翻转）才进下一 Batch。当前task-deltas-v1合同不能漏传作用域；资源作用域计划项必须与本批精确对应。信封保留 `resource_scope`、`resource_closer`、`resource_merge_receipt` 和 `writeback_manifest`。有pending先recover；已完成合并但资源/输入改变时回责任者处理，不能凭旧收据重放。
