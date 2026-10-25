<!-- when: 需要某派发点 prompt 时，按下表路由到 agent-prompts/ 下对应单段文件（勿整份加载本索引求全） -->
<!-- topics: agent prompt 路由索引, 按段加载, 控制面瘦身 -->

# 子代理派发 prompt — 路由索引

> ⚠️ **本文件已按段拆分**（控制面瘦身：旧版单文件 413 行被每个 worker 整份吞，实测 122/206 agent 重复读全 8 段）。
> 现在**每个派发点只加载自己那一段 + 公共规则**，不再整份读。

## 加载规则（HARD-GATE）

派发某 worker 时，**Read 两个文件即构成完整派发规范**：

1. [`agent-prompts/_common.md`](./agent-prompts/_common.md) — 公共规则（§2.1 占位 5 类 kind + Stage 3 单写者纪律），**始终随读**
2. 下表对应的**单段文件** — 该 agent 的完整 prompt 模板

**不要为求全整份加载所有段**——各段相互独立，跨段引用已在各文件内以相对链接标注。

## 派发点 → 文件路由

| 派发点 | agent | 文件 |
|--------|-------|------|
| §1 Stage 1 converter | a2h-ios-converter | [`agent-prompts/1-converter.md`](./agent-prompts/1-converter.md) |
| §2 Stage 1 Batch 收尾 | **a2h-closer**（mode=batch，协议在 agent 定义） | [`agent-prompts/2-batch-closer.md`](./agent-prompts/2-batch-closer.md) |
| §3 Stage 2/3 通用 worker | a2h-migration-worker | [`agent-prompts/3-worker.md`](./agent-prompts/3-worker.md) |
| §4 Stage 3 Step 3a UI 补充 | a2h-migration-worker | [`agent-prompts/4-step3a-ui.md`](./agent-prompts/4-step3a-ui.md) |
| §5 Stage 3 Step 3b ViewModel 三段式 | a2h-migration-worker | [`agent-prompts/5-step3b-vm.md`](./agent-prompts/5-step3b-vm.md) |
| §6 Stage 3 Step 3c 数据层接入 | a2h-migration-worker | [`agent-prompts/6-step3c-data.md`](./agent-prompts/6-step3c-data.md) |
| §7 Stage 3 Step 3d 自身页内接线 | a2h-migration-worker | [`agent-prompts/7-step3d-wiring.md`](./agent-prompts/7-step3d-wiring.md) |
| §8 Stage 3 group-closer | **a2h-closer**（mode=group，协议在 agent 定义） | [`agent-prompts/8-group-closer.md`](./agent-prompts/8-group-closer.md) |

> 占位规则统一遵循 §2.1（见 `_common.md`）：合法占位 = 已登记的 5 类 kind 占位，未登记 / 自由文本一律 FAIL。
