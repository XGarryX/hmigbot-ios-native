<!-- when: a2h-spec 各 Phase 收尾输出审批摘要时加载（Step A4 输出报告 / Step B3 Gate B / Step C5 Gate C）-->
<!-- topics: Phase A 数据准备完成摘要, Phase B UI 清单完成摘要, Phase C 功能 Spec 完成摘要, grill #1 决策清单, 审批摘要格式 -->

# a2h-spec 各 Gate 输出摘要模板

> **提问格式铁律**：本文件所有 Gate 一律使用选项式提问，用户回复编号即可推进；
> 禁止填空式或开放式提问。格式与理由见 [decision-card.md](./decision-card.md)。

a2h-spec 三个 Phase 收尾各输出一份结构化摘要供人工审批。`<HARD-GATE>` 审批铁律保留在 SKILL.md body，本文只是摘要的**格式模板**。

## Phase A 完成（Step A4 输出准备报告）

```
## Phase A: 数据准备完成

### 页面清单（共 N 个页面）
| 序号 | Activity/Fragment | confidence | view.xml | meta.json | screenshot |
|------|------------------|-----------|----------|-----------|------------|
| 0001 | MainActivity     | high      | ✓ dump      | ✓ 已扩展  | ✓          |
| 0002 | HomeFragment     | medium    | ✓ 合成(脚本) | ✗→生成    | ✗          |
| 0003 | LoginActivity    | low       | ✗ 合成失败   | ✗→生成    | ✗          |

### 数据质量摘要
- high: X 页面（有 UIAutomator dump）
- medium: Y 页面（从源码合成）
- low: Z 页面（部分 layout 缺失）

### 建议
- Z 个 low confidence 页面建议在真机上运行 UIAutomator dump 提高数据质量

[1] 以当前数据质量继续，进入 Phase B　← 推荐（low 页面在 Phase B 标注 confidence 即可）
[2] 先对 Z 个 low confidence 页面补真机 dump 再继续
[3] 只对指定页面补 dump（请列编号）
[4] 中止本轮

回复编号即可。
```

## Phase B 完成（Step B3 审批摘要）

```
## Phase B: UI 清单生成完成

- 页面总数: N 个（P0 × a, P1 × b, P2 × c）
- 分批计划: M 个批次
- confidence 分布: high × X, medium × Y, low × Z
- 全局约定: 导航架构 = NavPathStack, 主色 = ...
- 共享组件: K 个

请审阅 spec/baseline/ui-manifest.md 和 spec/baseline/ui/ 目录。

[1] 通过，进入 Phase C（功能 Spec 生成）
[2] 通过，并把下列页面记为例外（请列编号）
[3] 先补下列页面再来（请列编号）
[4] 中止本轮

回复编号即可。
```

## Phase C 完成（Step C5 审批摘要）

```
## Phase C: 功能 Spec 生成完成 + grill #1 决策清单

### spec 产出
- 功能总数: N 个（P0 × a, P1 × b, P2 × c）
- 领域模型: X 个实体, Y 个关系
- 依赖图深度: Z 层
- 执行顺序: M 个并行组
- 基础设施: 数据库 X 表, 网络 Y 端点, 事件 Z 个

### 决策清单（spec/decision-ledger.md）
- D0 产出定位: <Demo / MVP / 上线 / 完整复刻>
- D 编号决策: N 条（C0–C5 / C12 / C15–C16 类目）
- **PD 待批决策（平台差异）**: P 条 —— 全部 approved/rejected，proposed 残留 = 0（lint_divergence --gate PASS）
  | PD-ID | 被替代 Android 行为 | 提议替代 | supersedes | emits（差异 AC） | 裁决 |
  |---|---|---|---|---|---|
- 运行期验证项: M 条（含差异 AC `[真机]` 项 → 路由 verify 设备三段）
- 技术必做项: K 条
- escape 候选: J 条（待 retrospect 评审）
- spec 卫生检查: PASS（或 FAIL 项已修复）

### 覆盖对账（scripts/lint_coverage.py → spec/.a2h/open-findings.json）
> 不再有 AC 预算表。数量没有下限/上限/偏差带，多写的 AC 永远不会导致失败。
> 充分性按证据判定：源码里检出什么行为信号，就要求覆盖对应的行为**种类**。

**可枚举事实对账表（lint_coverage.py 原样输出，逐行核对）**：

| feature | 枚举事实 | AC覆盖 | 组声明 | skip | 未交代 |
|---|---|---|---|---|---|

「未交代」列非零 = 🔴 阻断，[1] 不可选。组声明数异常偏高（如 90% 走 组:）说明在用合并
声明规避逐项写 AC——逐条抽查组成员是否真同构。

| feature | 证据要求的义务种类 | 已覆盖 | 🔴 阻断 | 🟡 建议 |
|---|---|---|---|---|

- 🔴 **阻断项 N 条**（必须清零才能选 [1]）
  | rule | subject | 位置 |
  |---|---|---|
  （`SPEC.UNCOVERED_ANCHOR_FILE` = 锚定文件有行为信号但无任何 AC 的 `源:` 指向它；
  `SPEC.INSTANCE_UNACCOUNTED` = 可枚举事实未被 AC/组声明/skip 交代；
  `SPEC.MANIFEST_ACTIVITY_UNACCOUNTED` = 某模块 manifest 声明的 Activity 无 page/anchor/skip——
  子模块 manifest 构建期合并，只扫 app/ 会漏；0 引用疑似死码登记 skip-list 并引用本项目死码处置决策即可关闭）

### 跳过登记披露（必列——跳过是决策，沉默是事故）
凡经 skip-list 关闭的 manifest Activity，逐条列出，死码也不例外：
| Activity | 模块 | 决策引用 | 理由摘要 |
|---|---|---|---|
| （示例）VideoPlayActivity | basic | D-xxx | 死码：Builder.start() 全仓 0 调用点 |
未引决策 ID 的行显示 ⚠ 并计入 🟡（`SPEC.MANIFEST_SKIP_NO_DECISION`）。本表数据来自
lint_coverage 输出的「已登记跳过的 manifest Activity」块与 context.manifest_accounting。
- 🟡 **建议项 M 条**（本 Gate 由用户裁决，可整体记为例外）
  - `SPEC.ORACLE_MISSING` / `SPEC.TRUTH_SOURCE_MISSING`：未写 `判:` / `真:` 的 AC 数
  - `SPEC.KIND_LIKELY_MISSING`：证据要求但 AC 文本未见对应表述的种类
  - `SPEC.ORACLE_TOO_WEAK`：声明的最强判定方式弱于证据要求
  - `SPEC.ADDENDUM_MISSING` / `SPEC.UNOWNED_FILE`

### 判定强度分布（判: 锚）
| 判定方式 | AC 数 | 说明 |
|---|---|---|
| static | | 仅代码形态断言——**这部分「通过」不等于行为正确**，占比过高需说明理由 |
| unit / contract / route | | |
| ui / visual / device | | |
- 未声明 `判:` 的 active AC: X / Y

### 诊断指标（不参与门禁）
- `spec/baseline/complexity-metrics.json`：decision_count / 密度 / split 建议
- lint_divergence: R1–R5 <PASS / FAIL 清单>
- lint_addenda_closure: <PASS / FAIL 清单>

请审阅 spec/baseline/feature-index.md、spec/baseline/features/ 目录、**spec/decision-ledger.md**。

[1] 通过，调用 a2h-plan 生成执行计划（plan 阶段会跑 grill #2 追加技术侧决策）
[2] 通过，并把下列建议项记为例外（请列编号；写入 decision-ledger 并附关闭条件）
[3] 先修下列问题再来（请列编号）
[4] 中止本轮

回复编号即可。存在 🔴 阻断项时 [1] 不可选——摘要须写明「本次不可选 [1]，因有 N 条阻断项」。
```
