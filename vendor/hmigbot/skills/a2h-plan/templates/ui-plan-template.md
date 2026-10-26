<!-- when: 生成 ui-plan.md 时加载 -->
<!-- topics: ui-plan, Batch 分批, owning_slice -->

# ui-plan.md 完整模板

body 只留分批规则（批内页数无上限，批 = 优先级的自然分组）；Batch 表格形态与下列生成规则在此模板。

## 生成规则

**页面依赖不参与分批**——导航 / 嵌入目标未建一律由 FWD-REF 机制兜底，批内无编译（统一编译在 execute §3d 收口），跨批依赖零编译代价。**批内不标逐页并行关系**——批内默认全并行派发（单写者纪律各写各文件，导航目标未建由 FWD-REF 兜）。

**size-1 Batch 禁止**：孤页批并入**前一批**末尾，行内保留其原优先级标注（此并批不视为违反优先级单调性；§7 校验 size-1 批 = 0）。

**confidence 同为分批输入**（读 ui-manifest，high 在前）：**不输出 confidence 列**；仅 `low` 页在行内标 `⚠️low`（需人工补充 UIAutomator dump 数据，异常才显性）。

**结算检查点**：每 Batch 末尾注入一个（批收尾结算：资源 sweep + brief，**无编译**；统一编译在 a2h-execute §3d 收口）。

```markdown
# UI Conversion Plan

## Context
- Source: spec/baseline/ui-manifest.md
- Style: <style_set 值，none 或具体风格名>
- Total pages: <总页面数>
- Batches: <批次数>

## Batch 1: P0 Core Pages

| 序号 | 页面 | Android 来源 | owning_slice |
|------|------|-------------|--------------|
| 0001 | MainPage | MainActivity | F001 |
| 0002 | HomePage | HomeFragment | F002 |
| 0003 | QueuePage | QueueFragment | F003 |

结算检查点: Batch 1 完成后（batch closer 结算 → brief，见 a2h-execute §3b）

## Batch 2: P0 Player + Subscription

| 序号 | 页面 | Android 来源 | owning_slice |
|------|------|-------------|--------------|
| 0004 | PlayerPage | PlayerActivity | F004 |
| 0005 | SubscriptionPage | SubscriptionFragment | F005 |
| 0006 | SearchPage | SearchFragment | F006 |

结算检查点: Batch 2 完成后（同上）

## Batch 3: P1 Secondary
...

## Batch N: P2 Low Priority
| 序号 | 页面 | Android 来源 | owning_slice |
|------|------|-------------|--------------|
| 00XX | AboutPage ⚠️low | AboutActivity | F0NN |

`owning_slice` 列填**裸 F-ID**（如 `F001`），从 `feature-index.md` 的 feature→涉及页面 映射推导。**必须是裸 F-ID 而非「Slice N」**（`^F\d{3}$` 契约；Slice↔F-ID 1:1，编号见 feature-plan 索引）。converter 据此 + §7 接线归属映射，为 forward-ref 钩子算 `resolve_by`。

**归属消歧**（按序机械判定，禁 LLM 自由裁量）：
1. 恰一 feature 声明 → 归它（常态）
2. 零声明 → 取 `page_NNNN.md` 关联功能；再无 → 归拓扑最早在 `integration_points`/`wires` 引用它的 feature；**仍无主 → 阻断**（spec 缺口，回补 feature-index，禁止硬猜掩盖）
3. 多 claim → 归**拓扑最早者**（= 文件创建者 = 单写者），其余 feature 对自己的 handler 走 cross_slice_edit
4. hub/壳容器页 → 覆盖优先，按 SKILL Step 5「隐式关系兜底」（归最早承载任一 Tab 的切片）

> 执行者：本链由主线程编排 P0（kernel）判定，ui-plan writer 只抄结果表（SKILL §3.0）；单线程降级时由生成者自判，规则同此。

结算检查点: Batch N 完成后 + Stage 1 统一收口（入口装配 → 骨架审计 → single-pass 编译，a2h-execute §3d）

## Summary
- P0 pages: X (Batch 1-2)
- P1 pages: Y (Batch 3-4)
- P2 pages: Z (Batch 5+)
- ⚠️ Low confidence: W pages（W=0 时省略本行）
```
