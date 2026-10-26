<!-- when: 生成 ui-plan.md 时加载 -->
<!-- topics: ui-plan, Batch 分批, owning_slice -->

# ui-plan.md 完整模板

body 只留分批规则（批内页数无上限，批 = 优先级的自然分组）；Batch 表格形态与下列生成规则在此模板。

profile 2同时遵循[Plan交付合同](../references/plan-delivery-contract.md)。概要页面表含稳定item_id、精确目标路径与AC；每页另外生成一张固定局部责任表（字段/值，恰7行，值为JSON literal），聚合Plan items JSON逐字段等于这些表，不复制业务正文。依赖、scope、verification不能凭概要文字推测。

## 生成规则

**页面依赖不参与分批**——导航 / 嵌入目标未建一律由 FWD-REF 机制兜底，批内无编译（统一编译在 execute §3d 收口），跨批依赖零编译代价。**批内不标逐页并行关系**——批内默认全并行派发（单写者纪律各写各文件，导航目标未建由 FWD-REF 兜）。

**单页范围**：真实迁移范围仅 1 页，或只有首批孤页且无前一批时，允许 size-1 Batch，并记录 total_pages 与原因；不造页面凑批。其他孤页可并入前一批末尾，保留原优先级。每批仍须结算与最终编译。


**结算检查点**：每 Batch 末尾注入一个（批收尾结算：资源 sweep + brief，**无编译**；统一编译在 a2h-execute §3d 收口）。

```markdown
# UI Conversion Plan

## Context
- spec_contract_version: 2
- Source: spec/baseline/ui-manifest.md
- Style: <style_set 值，none 或具体风格名>
- Total pages: <总页面数>
- Batches: <批次数>

## Batch 1: P0 Core Pages

| item_id | 序号 | 页面 | iOS 来源 | 目标文件 | owning_slice | ac_ids |
|---------|------|------|----------|----------|--------------|--------|
| PAGE-0001 | 0001 | MainPage | MainScreen | entry/src/main/ets/pages/MainPage.ets | F001 | ["F001-AC01"] |
| PAGE-0002 | 0002 | HomePage | HomeScreen | entry/src/main/ets/pages/HomePage.ets | F002 | ["F002-AC01"] |
| PAGE-0003 | 0003 | QueuePage | QueueScreen | entry/src/main/ets/pages/QueuePage.ets | F003 | ["F003-AC01"] |

结算检查点: Batch 1 完成后（batch closer 结算 → brief，见 a2h-execute §3b）

## Batch 2: P0 Player + Subscription

| item_id | 序号 | 页面 | iOS 来源 | 目标文件 | owning_slice | ac_ids |
|---------|------|------|----------|----------|--------------|--------|
| PAGE-0004 | 0004 | PlayerPage | PlayerScreen | entry/src/main/ets/pages/PlayerPage.ets | F004 | ["F004-AC01"] |
| PAGE-0005 | 0005 | SubscriptionPage | SubscriptionScreen | entry/src/main/ets/pages/SubscriptionPage.ets | F005 | ["F005-AC01"] |
| PAGE-0006 | 0006 | SearchPage | SearchScreen | entry/src/main/ets/pages/SearchPage.ets | F006 | ["F006-AC01"] |

结算检查点: Batch 2 完成后（同上）

## Batch 3: P1 Secondary
...

## Batch N: P2 Low Priority
| item_id | 序号 | 页面 | iOS 来源 | 目标文件 | owning_slice | ac_ids |
|---------|------|------|----------|----------|--------------|--------|
| PAGE-00XX | 00XX | AboutPage ⚠️low | AboutScreen | entry/src/main/ets/pages/AboutPage.ets | F0NN | ["<实际active AC>"] |

`owning_slice`列填裸F-ID（如`F001`，`^F\d+$`），必须等于feature-index“创建页面”列对该page的唯一creator。关联页面用于消费范围，不能替代创建归属。converter据此及接线映射给forward-ref钩子算resolve_by。

**归属核对**：每个活动页面恰有一个创建feature；零个或多个都回Spec修正，不按拓扑最早、涉及页、hub/壳容器或临时猜测兜底。共页可被多个feature关联消费，但文件全生命周期写权仍唯一；同文件后续接线归入同一typed owner任务内部实施。

> 执行者：本链由主线程编排 P0（kernel）判定，ui-plan writer 只抄结果表（SKILL §3.0）；单线程降级时由生成者自判，规则同此。

结算检查点: Batch N 完成后 + Stage 1 统一收口（入口装配 → 骨架审计 → single-pass 编译，a2h-execute §3d）

## Summary
- P0 pages: X (Batch 1-2)
- P1 pages: Y (Batch 3-4)
- P2 pages: Z (Batch 5+)
- ⚠️ Low confidence: W pages（W=0 时省略本行）
```

## Plan items（生成文件的必备末节）

每页在概要之后以`### UI:PAGE-NNNN`独立标题定位，标题下恰一张局部责任表；该标题用于冻结任务的精确章节消费。示例值须替换，表头/7字段固定，字符串及数组用JSON字面量。

### UI:PAGE-0001

| 字段 | 值 |
|---|---|
| item_id | "UI:PAGE-0001" |
| ac_ids | ["F001-AC01"] |
| ownership | ["entry/src/main/ets/pages/MainPage.ets"] |
| parents | [] |
| page_ids | ["page_0001"] |
| scope | "product" |
| verification | "generated" |

末节唯一plan_items_version:2 JSON块投影全部局部责任表，7字段exact一致。ownership/ac_ids还须与概要页面表同页行一致；导航依赖由FWD-REF承担时不臆造串行边。不把示例值复制进实际交付。
