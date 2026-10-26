<!-- when: 派发 Stage 1 Batch 收尾（a2h-closer, mode=batch，每 Batch 末尾一次）时加载本段 + _common.md -->
<!-- topics: Batch 收尾派发参数, mode=batch, a2h-closer -->

# §2. Stage 1 Batch 收尾派发（a2h-closer, mode=batch）

> **收尾协议单源 = `a2h-closer` agent 定义**（mode=batch 两步：资源残量兜底 → writeback manifest；批内无编译，统一编译在 execute §3d 收口）；本文件只是派发参数模板。公共占位规则 §2.1 + 单写者纪律见 [`_common.md`](./_common.md)，派发时一并 Read。

派发 Codex 子代理 `a2h-closer`（定义于 `.codex/agents/a2h-closer.toml`），任务提示词：

```
mode=batch。你是 Stage 1 Batch [{batch_n}] 的收尾者，本批所有并发 converter 已完成（已按直写纪律 append 资源键，你只补漏不重写）。按你的 agent 定义 mode=batch 两步协议执行。

  本批页面: {batch_pages}                    # 序号 + ArkTS 文件路径清单
  本批生成/改动的 .ets: {batch_ets_files}
  Android 源根: {android_source_dir}
  HarmonyOS 工程根: {harmony_project_dir}
```

**HARD-GATE**（主线程侧）：writeback manifest 必产 → 主线程跑 `apply_writeback.py` 成功（brief 落盘 + 账本翻转）才进下一 Batch（批间无编译门）；崩溃恢复 = manifest 在则重跑 apply。
