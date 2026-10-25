# spec-evolver audit 模式（spec↔代码差距审计）

> 从 arkts-spec-evolver/SKILL.md 下沉。SKILL.md 通过 MUST-read 指针引用本文件。

## audit 模式

audit 模式用于审计 baseline spec 与实际代码的差距。**仅检测结构性地标**，不做语义级功能检测，避免过多误报。

### 检测范围

| 检测对象 | 扫描方式 |
|---------|---------|
| @Entry Page | `grep "@Entry" pages/*.ets` |
| @ComponentV2 / @Component（V2 优先 + V1 兼容） | `ls components/*.ets` + `grep -rEI '@ComponentV2\|@Component' components/` 与 ui-manifest.md 页面清单对比 |
| DAO 类 | `ls database/*Dao.ets` 与 feature-base.md 数据模型对比 |
| 数据表 | `grep "CREATE TABLE" database/*.ets` 与 feature-base.md 数据模型对比 |

**不检测**：工具函数、内部重构、UI 微调等非结构性变更。

### audit 流程

```
1. 读 baseline feature-index.md（功能清单）+ ui-manifest.md（页面清单）+ feature-base.md（数据模型）
2. 扫描 ArkTS 代码中的结构性地标:
   - @Entry Page（pages/*.ets）
   - @ComponentV2（V2，components/*.ets）/ @Component（V1 兼容）
   - DAO 类（database/*Dao.ets）
   - 数据表（grep CREATE TABLE）
3. 对比:
   - spec 有但代码无 → feature 增量（待实现）
   - 代码有但 spec 无（限结构性地标）→ feature 增量（补录）
   - spec 有 + 代码有但行为不一致 → bugfix 增量
4. 批量生成增量 spec
5. 更新 spec-index.md
6. 输出审计报告
```

#### audit 模式增强: 覆盖率驱动的 GAP 检测 [新增]

当 `spec/baseline/plans/coverage-matrix.md` 存在时，audit 模式额外执行：

1. 读取 coverage-matrix.md 的 Gaps 表和 Full Matrix
2. 对每个 GAP（未被任何 task 覆盖的 Feature ID）:
   - 读取 feature-index.md 中该功能的描述和子功能列表
   - 检查代码中是否有非计划内的实现（grep 关键词）
   - 如果代码中无实现 → 生成 increment spec (type: feature, status: pending)
   - 如果代码中有部分实现 → 生成 increment spec (type: optimization, status: pending)
3. 对每个 COVERED 但实际未实现的项（结合 CHECK-6 结果）:
   - 生成 increment spec (type: bugfix, status: pending)
4. 输出: 一组 increment spec 文件（spec/features/ 或 spec/optimizations/ 或 spec/bugfixes/）

这样 audit 模式不仅能检测"代码中有但 spec 中没有"的情况（当前能力），还能检测"spec 中有但代码中没有"的情况（新增能力）。

**前置条件**: 如果 coverage-matrix.md 不存在，跳过此增强部分，仅执行原有的结构扫描。

---
