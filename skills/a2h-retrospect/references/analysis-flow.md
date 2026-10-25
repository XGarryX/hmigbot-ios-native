<!-- when: a2h-retrospect 执行 §3 分析流程 5 步、需要每步详细决策逻辑时加载 -->
<!-- topics: Plan vs 实际 skill 差异, Stage 对比, 编译错误 pattern 提取, API 修正提取, Confidence 准确度评估 -->

# 分析流程 5 步：详细决策逻辑

> a2h-retrospect SKILL.md §3 的完整流程图。body 仅含 5 步概览，**执行时以本文件为准**。

## Step 1: Plan vs 实际 Skill 使用差异 + Stage 对比

从 plan 提取 `suggested_skills`，从 migration-report 提取实际使用的 skill，比对：

```
Plan suggested_skills  vs  Migration-report actual_skills
  │
  ├─ 完全一致 → 标记 MATCH
  ├─ 被覆盖（升级）→ 标记 OVERRIDE，记录原因
  ├─ 被覆盖（降级）→ 标记 DOWNGRADE，标红分析
  └─ 未使用 → 标记 UNUSED，分析是否多余
```

输出 Skill 覆盖率 = MATCH 数 / 总 task 数。

### Stage 对比分析

对比 Stage 1（UI Pipeline，a2h-ios-converter 直接转换）与 Stage 3 Step 3a（Feature Slice UI 补充转换）的转换质量：

```
Stage 1 (UI Pipeline) vs Stage 3 (Feature Slice UI supplement)
  │
  ├─ 页面范围对比:
  │   ├─ Stage 1 转换的页面列表（来自 ui-manifest.md confidence:high 页面）
  │   └─ Stage 3 Step 3a 转换的页面列表（来自 Feature Slice 中的 UI 任务）
  │
  ├─ 编译错误率对比:
  │   ├─ Stage 1 页面平均编译错误数
  │   ├─ Stage 3 页面平均编译错误数
  │   └─ 差异分析（哪种 Pipeline 产出更少编译错误）
  │
  └─ 保真度/准确度对比:
      ├─ Stage 1 页面 verify 通过率
      ├─ Stage 3 页面 verify 通过率
      └─ UI 还原度评估（布局、交互、样式的匹配程度）
```

## Step 2: 编译错误 Pattern 提取

从 `hmos-fix-build-errors` 的修复记录中提取可复用的编译错误模式：

```
编译错误日志
  │
  ├─ 分类:
  │   ├─ 类型错误（any / as / 类型不匹配）
  │   ├─ 导入错误（废弃模块 / 错误路径）
  │   ├─ API 错误（不存在 / 签名变更 / 废弃）
  │   ├─ 语法错误（ArkTS 特有限制）
  │   └─ 配置错误（module.json5 / build-profile.json5）
  │
  └─ 每个 pattern 提取:
      ├─ 错误特征（正则匹配）
      ├─ 修复方案
      └─ 出现频次
```

## Step 3: API 修正提取

从 `arkts-knowledge-verifier` 的验证记录中提取 API 修正：

```
Knowledge-verifier 日志
  │
  ├─ API 修正:
  │   ├─ 错误 API → 正确 API（替换映射）
  │   ├─ 废弃 API → 新 API（升级映射）
  │   └─ 不存在 API → 替代方案（新增映射）
  │
  └─ 每条修正提取:
      ├─ 原 API 签名
      ├─ 正确 API 签名
      └─ 修正原因
```

## Step 4: 分类

将 Step 2-3 的提取结果分为两类：

| 类型 | 定义 | 示例 |
|------|------|------|
| **确定性修正** | 100% 可自动应用的规则 | `@ohos.data.rdb` → `@kit.ArkData`; `file://` → `fd://` |
| **设计决策** | 需要人工判断的架构选择 | 选择 Repeat vs LazyForEach vs ForEach; 状态管理用 AppStorageV2.connect vs @Provider |

## Step 5: Confidence 准确度评估

对比 Phase A（a2h-spec）中对页面的 confidence 预测与实际转换质量，评估预测准确度：

```
ui-manifest.md confidence 预测  vs  实际转换结果
  │
  ├─ high confidence 页面:
  │   ├─ 转换顺利（符合预期）→ 标记 ACCURATE
  │   └─ 转换出现问题（编译错误多 / verify 失败）→ 标记 OVER_ESTIMATED
  │       → 标红，提取导致高估的原因，反馈改进 confidence 评估逻辑
  │
  ├─ medium confidence 页面:
  │   ├─ 转换顺利 → 标记 UNDER_ESTIMATED，可升级评估
  │   └─ 转换困难 → 标记 ACCURATE
  │
  ├─ low confidence 页面:
  │   ├─ 转换顺利 → 标记 UNDER_ESTIMATED，可升级评估
  │   └─ 转换困难 → 标记 ACCURATE
  │
  └─ 输出准确度指标:
      ├─ 总体准确率 = ACCURATE 数 / 总页面数
      ├─ 高估率 = OVER_ESTIMATED 数 / high confidence 页面数
      ├─ 低估率 = UNDER_ESTIMATED 数 / (medium + low) confidence 页面数
      └─ 各 confidence 等级的实际通过率分布
```
