---
id: {{ id }}
type: {{ type }}                    # feature | bugfix | optimization
title: {{ title }}
priority: {{ priority }}            # P0/P1/P2
status: pending                     # pending | planned | in_progress | verifying | done | failed | deprecated
created: {{ date }}
source: {{ source }}                # issue #N / 用户反馈 / 测试发现 / 审计发现
affects:
  - L1: {{ sections }}
  - L2: {{ sections }}
  - L3: {{ sections }}
# deprecated_by:                   # 被哪个增量替代（废弃时填写）
# deprecated_reason:               # 废弃原因（废弃时填写）
---

## 背景

<!-- 为什么需要这个变更 -->

## 复现步骤

<!-- bugfix 类型专用，其他类型删除此节 -->
1. ...

## 根因分析

<!-- bugfix 类型专用，其他类型删除此节 -->

## 变更描述

### 对 L1 的影响
<!-- 如不影响 L1，删除此节 -->

### 对 L2 的影响
<!-- 如不影响 L2，删除此节 -->

### 对 L3 的影响
<!-- 如不影响 L3，删除此节 -->

## 实现指引

<!-- 具体实现方案、注意事项、参考踩坑 -->

## 回归范围

<!--
本节由 a2h-incremental-migration §M3.2.5 自动派生（增量迁移场景），
或由 evolver create 阶段从 affects + grep 反查派生（独立 spec 场景）。
verify Step 11 必须消费此节决定回归测试范围。
若为纯新增功能（不触碰任何已有页面/组件/共享方法），可保留空表 + 标注 "纯新增，无回归项"。
-->

派生时间：YYYY-MM-DD HH:mm
派生命中：feature_acs={N}, page_acs={M}, total={N+M}, 阈值=10
explosion: false                       # true 表示 total>10，需 opt_out
opt_out_reason: null                   # explosion=true 时必填
opt_out_approved_by: null              # explosion=true 时必填（由用户审批确认）

### feature_acs（受改动影响的 baseline 功能 AC）
- F00x-ACy：描述（来源：触碰的共享文件/方法）

### page_acs（受改动影响的 baseline 页面级 AC）
- P000x-UI-SMOKE_xxx
- P000x-UI-INTERACT_xxx

### shared_files / shared_symbols（派生根因）
- entry/src/main/ets/pages/XxxPage.ets (struct: XxxView)
- entry/src/main/ets/viewmodels/XxxViewModel.ets (method: loadXxx)

### affected_visual_pages（视觉对照清单，affects 含 ui 时必填）
<!--
视觉验证以同期 Android 应用为视觉真值，不做"改代码前 baseline 截图"。
清单 = 本次新增功能涉及的页面状态 + page_acs 涉及的所有状态。
-->
- page_id: page_xxxx
  state_label: descriptive_state_name
  hmos_entry_path: 冷启 → ...
  android_reference: ActivityName / FragmentName, state=...
  android_entry_path: 冷启 → ...

### 合并记录（Step 9.5 回写）
<!--
execute 完成后，Step 9.5 基于实际 git diff 重扫产出清单 B，
与 Step 3.5 预测的清单 A 取并集，回写上述各节。
-->
- 清单 A（Step 3.5 预测）：feature_acs={N}, page_acs={M}
- 清单 B（Step 9.5 实扫）：feature_acs={P}, page_acs={Q}
- 新增项（B - A）：{列出清单 B 中有但清单 A 中没有的条目}
- 最终：feature_acs={X}, page_acs={Y}, total={X+Y}

### rationale（派生理由）
<!-- 为什么这些 AC 会受影响 -->

## 验收标准

- [ ] 验收条件 1
- [ ] 验收条件 2

## 实现计划

<!-- spec-evolver plan 阶段自动生成 -->
- plan 文件:
- task 数量:
- 复杂度: 完整流程 / 简化流程

## 执行记录

<!-- spec-evolver execute 阶段自动填充 -->
- 执行时间:
- 触发 skill:
- 修改文件:
- commit:

## 验证记录

<!-- spec-evolver verify 阶段自动填充 -->

### Step 10 静态验证
- 编译验证: ✅/❌（hmos-fix-build-errors 自动闭环）
- 验收验证: X/Y 项通过（grep / 代码结构）
- 验证时间:

### Step 11a 自动化回归（消费 ## 回归范围 的 feature_acs + page_acs）
<!-- 仅当 ## 回归范围 非空时填充；纯新增功能跳过 -->
- 调用 skill: arkts-dt-verifier --filter <feature_acs + page_acs>
- baseline AC 索引: entry/src/ohosTest/ets/test/tdd-ac-index.md
- 跑测设备: hdc {device_id} / adb {device_id}
- 结果: feature_acs X/N GREEN, page_acs Y/M GREEN
- 退化条目: <空> | <列出 RED/ERROR 的 AC + 原因>
- 报告: docs/dt-verification-report.md
- 结论: ✅ 无退化 / ❌ 有退化（进回退处理）

### Step 11b 视觉验证（消费 ## 回归范围 的 affected_visual_pages）
<!-- 仅当 affects 含 ui: 时填充 -->
- 视觉真值：同期 Android 应用（不做 HMOS 改前 baseline 截图）
- 对 affected_visual_pages 每条状态：
  - HMOS 走 hmos_entry_path → 截图（after）
  - Android 走 android_entry_path → 截图（reference）
  - 多模态对比，判定标准（叠加语义）：
    - baseline（Android）有的 UI 元素在 HMOS 必须存在 + 位置/样式不变（允许像素级微差）
    - HMOS 新增元素允许（属于本次新增功能）
    - 已有元素消失 / 位移 / 变形 → 失败
- 结果汇总:
  - {state_label_1}: ✅ / ❌（差异描述）
  - {state_label_2}: ✅ / ❌
  - 总体: K/K 张状态对照通过

### 设备探测（Step 11 前置，必跑）
- hdc list targets: <stdout 原文>
- adb devices: <stdout 原文>

### 总结
- status: verifying → done / verifying(visual-pending) / failed

## 回退记录

<!-- 仅在验证失败回退时填充 -->
