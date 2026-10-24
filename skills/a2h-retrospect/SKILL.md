---
name: a2h-retrospect
description: "iOS→HarmonyOS 迁移第五步（Retrospect，闭环自优化）：读 spec 计划 / brief / 回执 / 验证记录与派生报告，分析 plan vs 实际 skill 差异、编译错误 pattern、API 修正与 Confidence 准确度，把满足三条件（频次≥3 / 修复一致 / 确定性 100%）的确定性修正自动写入目标 skill references，其余降级 Staged Patch 等用户审核；设计决策与关键经验另行沉淀，产出回顾报告。当用户说“回顾”“优化 skill”“总结这次迁移经验”“沉淀一下踩坑”时触发。不要用于：生成 Spec（用 a2h-spec）、计划（用 a2h-plan）、执行（用 a2h-execute）、验证（用 a2h-verify）——无验证痕迹时先跑 a2h-verify，无迁移报告时先跑 a2h-execute。"
metadata:
  type: pipeline
  domain: migration
  tags:
  - ios
  - retrospect
  - migration
  layer: pipeline
---

本统一版本先读 [单一流程、环境前置与兼容范围](../a2h-run/references/unified-workflow.md)；其中明确的写入、准备时机和行为范围规则优先于下文的旧调用示例。


> **调用关系**：本 skill **不派发 subagent**，全部步骤在主会话执行。只读取上游产物做分析、按三条件把沉淀写进各目标 skill 的 `references/`——不调用 Domain Skill 改代码、不亲自 alter 迁移产物。分析即记录：`hmos-fix-build-errors`（编译 pattern）/ `arkts-knowledge-verifier`（API 修正）/ `a2h-execute` 派发记录（skill 覆盖）→ 沉淀到目标 `references/` + 回顾报告。
>
> **路径约定**：`<target>` = 鸿蒙目标工程根；`<runtime>` = 本包 runtime（`scripts/a2h_ios.py` 所在根）。输入读 `<target>/spec/` 下 plan / brief / 回执 / 派生报告；输出回顾报告落 `<target>/docs/retrospect-report-YYYY-MM-DD.md`，临时计数落 `<target>/spec/retrospect-counter.json`，Staged Patch 落 `.agents/skills/<target>/references/`。禁落会话临时目录。

# a2h-retrospect — 经验沉淀与闭环自优化

## 0. 定位与纪律

Pipeline 层第五步，**闭环自优化**，让 Domain Skill 越用越好：

```
a2h-spec → a2h-plan → a2h-execute → a2h-verify → a2h-retrospect（本 skill）
                                                       │
                                                       ├─ 分析差异
                                                       ├─ 提取经验
                                                       ├─ 分类沉淀
                                                       └─ 生成回顾报告
```

- **前置（gate）**：有验证痕迹即可跑——`spec/reports/smoke/round-*/findings.json`（v2 真机通道）/ `spec/fix/_state.yaml` 含 `last_verifier_results` / `spec/verify-report.md`（v1）任一存在即通过；全缺 → 提示「请先执行 a2h-verify」并**终止**。`spec/migration-report.md` 不存在 → 提示「请先执行 a2h-execute」并**终止**。plan（`spec/baseline/plans/` 或兼容 `spec/plans/plan-*.md`）不存在 → WARN「无 plan，跳过 plan vs actual 对比」继续。
- **输入**：优先读 `spec/baseline/plans/{ui-plan,base-plan,feature-plan}.md` 与 slices（兼容旧 `spec/plans/plan-*` 仅在实际存在时使用）；`spec/migration-report.md`；`spec/verify-report.md`；`spec/baseline/ui-manifest.md` / `source-coverage-report.md`；`spec/ref/ios-expertise-plan.json`、reviews、`ios-analysis-provenance.json` 及实际 MCP 捕获；`git diff`/`git log`（本轮范围）。
- **输出**：回顾报告、自动写入的 target skill references 条目、Staged Patch、`spec/retrospect-counter.json`。
- **唯一交互点 = 无（全自动分析）**；但设计决策与 Staged Patch **需用户审核后**才落盘（等审核响应，不是交互式追问）。**自动写入仅限三条件全满足**（§4a），任一不满足 → 降级。
- **第一条可见输出必须是**一行回顾计划（前置检查 → 原生源理解复盘 → 5 步分析 → 两类沉淀 → 报告 → 用量收尾）。

## 1. 原生源理解复盘输入（0.7.0，必做）

计划优先读取 `spec/baseline/plans/{ui-plan,base-plan,feature-plan}.md` 与 slices，兼容旧 `spec/plans/plan-*` 仅在实际存在时使用。读取 `spec/ref/ios-expertise-plan.json`、reviews、`ios-analysis-provenance.json` 及实际 MCP 捕获，**区分四类事实**：加载资料 / 声明审阅 / 真实工具调用 / 行为验证——复盘源码误解、规范建议误当源事实、漏路由及证据失效；**未知不能计入已验证准确率**。上游固定快照不自动改写，改进放自有 references 或 staged patch，审阅升级后再回归。

## 2. 输入与前置检查

自动读取：

| 文件 | 用途 |
|------|------|
| `spec/baseline/plans/{ui-plan,base-plan,feature-plan}.md` + slices | 计划：suggested_skills + task 列表；兼容旧 `spec/plans/plan-*.md` |
| `spec/migration-report.md` | 实际执行：skill 使用 + 覆盖记录 + 失败列表 |
| `spec/verify-report.md` | 验证结果：通过/失败项 |
| `spec/baseline/ui-manifest.md` | UI 页面清单与 confidence 评估 |
| `spec/baseline/source-coverage-report.md` | 源码侧覆盖审计（a2h-spec 产出）；复盘漏判 domain / 欠锚包 / 跨子仓 seam |
| `git diff` / `git log`（本轮范围） | 代码变更全貌 |

> 若 git log 为 [`commit`](../commit/SKILL.md) skill 的 7 字段结构化格式，用 `git log --grep='Category:'` 提取 Category/Issue-Type/Skill/Tools/Spec-Ref/Fix-Approach 分布替代部分 git diff 分析；否则跳过机器解析，仅用 git diff。

前置检查（gate，见 §0 前置三条件）。

## 3. 分析流程（5 步）

> **MUST 加载** [references/analysis-flow.md](./references/analysis-flow.md) —— 每步详细决策流程图 / Stage 对比 / Confidence 评估逻辑在此；下方仅为概览，执行时以 reference 为准。

1. **Skill 使用差异 + Stage 对比** —— plan `suggested_skills` vs migration-report 实际 → 标 MATCH/OVERRIDE/DOWNGRADE/UNUSED，算覆盖率；对比 Stage 1 直接转换与 Stage 3 Step 3a 补充转换的编译错误率、保真度。
2. **编译错误 Pattern 提取** —— 从 `hmos-fix-build-errors` 修复记录按 5 类（类型/导入/API/语法/配置）提取 {错误特征, 修复方案, 频次}。
3. **API 修正提取** —— 从 `arkts-knowledge-verifier` 记录提取 {原签名 → 正确签名, 原因}（替换/升级/新增三类）。
4. **分类** —— Step 2-3 结果分为 **确定性修正**（100% 可自动应用）与 **设计决策**（需人工判断架构选择）。
5. **Confidence 准确度评估** —— a2h-spec 的 confidence 预测 vs 实际转换质量 → 标 ACCURATE/OVER_ESTIMATED/UNDER_ESTIMATED，输出总体准确率/高估率/低估率。
6. **spec 覆盖审计复盘** —— 读 `source-coverage-report.md`（及 `feature-coverage-report.md` / 多子仓 `module-dep-graph.json`，外部 auditor 存在时），量化本轮「漏判 domain / 欠锚包 / 跨子仓 seam 不一致」，归因到 a2h-spec 的判定规则缺口，作为下条改进项来源。

## 4. 两类沉淀

### 4a. 确定性修正 → 自动写入目标 skill references

**自动写入条件（3 个全满足才写）**：① 频次 ≥3（本轮或历史累计）② 修复方式一致（非一事一议）③ 确定性 100%（无需人工判断）。

流程：读目标 references → 已有相同 pattern 则更新频次/日期，否则追加新条目 → 在回顾报告记录写入日志。**任一条件不满足 → 降级 Staged Patch**。

**References 目标映射**：

| 修正内容 | 目标 Skill | 写入文件 |
|---------|-----------|---------|
| 编译错误 pattern | `hmos-fix-build-errors` | `references/known-patterns.md` |
| API 映射 / 导入路径修正 | `arkts-knowledge-verifier` | `references/api-corrections.md` |
| Symbol 验证 | `arkts-knowledge-verifier` | `references/verified-symbols.md` |
| 资源映射修正 | `ios-resources-convert` | `references/` 对应文件 |
| 组件映射修正 | `arkts-component-builder` | `references/` 对应文件 |
| App 身份配置修正 | `arkts-app-identity` | `references/` 对应文件 |
| UI 模式修正 | `arkts-pattern-library` | `references/` 对应文件 |
| spec 欠规约 / 覆盖判定缺口 | `a2h-spec` | 原生语义维度、源文件处置、独立 AC 真值及有证据的 skip-list 规则（仅确定性修正写入，否则降级 Staged Patch） |

**Staged Patch（降级路径）**：生成 `.patch` 到 `.agents/skills/<target>/references/`，命名 `<date>-<brief>.patch`，报告标 PENDING_REVIEW 等用户审核。

### 4b. 设计决策 → 变更摘要

列出 {决策内容, 选择原因, 影响范围} → 等人工审批 → 通过后才写入 `docs/development-experience.md` 或对应 skill reference。

### 4c. 关键经验 → 项目记忆文件

将本次迁移中值得跨会话复用的经验写入目标项目的 `spec/memory/` 目录（每条经验一个 markdown 文件，frontmatter 至少含 name / description / type）：

```
经验类型筛选:
  ├─ 确定性修正中出现 3+ 次的 pattern → 写入 feedback memory
  ├─ 设计决策中被用户审批通过的选择 → 写入 project memory
  ├─ Skill 覆盖率分析中的 OVERRIDE 原因 → 写入 feedback memory
  ├─ 双 Pipeline 对比结论 → 写入 feedback memory
  └─ Confidence 准确度发现 → 写入 project memory
```

## 5. 增量学习模式（可选）

`a2h-execute` 编译检查点后可触发增量学习，无需等完整 retrospect。**完整流程 + `retrospect-counter.json` schema MUST 加载** [references/incremental-learning.md](./references/incremental-learning.md)。

要点：读本次修复日志 → 对比已有 references → 新模式累计 ≥3 自动写入、<3 记入 `spec/retrospect-counter.json`；count 达 3 自动晋升写入 references 并在报告记 `AUTO_PROMOTED`。

## 6. 安全边界

**自动写入范围（满足 3 个条件时允许）**：写入 `.agents/skills/*/references/` 中的 `known-patterns.md`、`api-corrections.md`、`verified-symbols.md`；只追加或更新频次/日期。

**绝对不做**：不删除 references 已有条目；不直接修改 `docs/development-experience.md` / `docs/dev-pitfalls.md`；不自动 `git apply` .patch 文件。

**降级操作**：生成 .patch 文件（新建，不覆盖已有）；报告列变更摘要；给 review 指引。用户审核命令示例：

```bash
cat .agents/skills/hmos-fix-build-errors/references/YYYY-MM-DD-import-fix.patch
cd .agents/skills/hmos-fix-build-errors/references/
git apply YYYY-MM-DD-import-fix.patch
```

## 7. 数据采集与回顾报告

**本节的命令由主 agent 在当前会话直接调用，不派发 subagent；严禁用 Write/Edit 手建派生产物。**先核验输入的派生产物是当前的：

```text
python <runtime>/scripts/a2h_ios.py spec-summary --project <target> --output <target>/spec/reports/spec-summary.json
python <runtime>/scripts/a2h_ios.py migration-report --project <target> --check <target>/spec/migration-report.md
python <runtime>/scripts/a2h_ios.py usage-summary --project <target> [--ledger <target>/spec/reports/derived/usage-budget.json]
```

| 命令 | 用途 | 关键 flags | exit code 语义 |
|---|---|---|---|
| `spec-summary` | 派生 spec 摘要（逐页关联/生成/编译/行为轴） | `--project`、`--output`（可选）、`--build-evidence`（可选）、`--brief` | 0=生成，2=FAIL |
| `migration-report` | 生成或校验迁移报告 | `--project`、`--output` 或 `--check`、`--build-evidence`、`--brief` | 0=生成/current，2=FAIL |
| `usage-summary` | 读本轮 skill 用量账本（自动化凭证） | `--project`、`--ledger`（可选） | 0=读取成功 |
| `resolve` | 复盘漏路由时复核源锚点 | `--source <source>`、`--anchor <anchor>` | 0=OK，3=AMBIGUOUS，2=MISS |

`migration-report --check` 从当前证据重算，过期或手改时修复证据、重新生成再重检，**不能手填状态消除差异**。

回顾报告存储路径：`docs/retrospect-report-YYYY-MM-DD.md`。**完整报告模板 MUST 加载** [references/report-template.md](./references/report-template.md) —— 含 Skill 覆盖分析 / 编译错误 Pattern / API 修正 / 确定性修正 Patch / Pipeline 对比 / Confidence 准确度 / 设计决策 / 操作指引共 8 段。

## 8. 触发 Prompt 示例

"回顾" / "优化 skill" / "总结这次迁移经验" / "沉淀一下踩坑" / "有哪些 pattern 可以复用" → 触发；先按 §0 前置检查，缺验证痕迹/迁移报告则提示先跑对应上游。

## 9. Commit 提示（回顾完成后，可选）

回顾报告生成后，建议调 [`commit`](../commit/SKILL.md) 提交本轮产出（references 自动写入 + staged patches）：报告 + 自动写入 → 大类=`verify`，Skill=`a2h-retrospect`，Fix-Approach="提取 N 个新 pattern 写入 references"；仅 staged patches → 不 commit（用户 review 后再提交）。

## 10. 读取时机（references）

| 触发时机 | 必读文件 |
|---|---|
| 执行 §3 分析 5 步，需每步详细决策图 / Stage 对比 / Confidence 评估 | references/analysis-flow.md |
| §5 增量学习触发，需 `retrospect-counter.json` schema | references/incremental-learning.md |
| 生成 §7 回顾报告 | references/report-template.md |

## 11. 交接

- 前置门闸：回顾报告生成 + 自动写入 done / 待审核清单列明，才能收尾。
- 移交产物清单：`docs/retrospect-report-YYYY-MM-DD.md`、自动写入的 references 条目清单、`spec/retrospect-counter.json`（若有）、Staged Patch 清单（PENDING_REVIEW）。
- 下一步：沉淀闭环结束，本轮迁移收口；同会话无后续 skill。待审核的 Staged Patch / 设计决策由用户 review 后分别 apply / 批准。

---

## 收尾：上报本阶段用量

本 skill 的最后一步（无论经 a2h-run 还是单独触发）：

```bash
.migbot/bin/a2h mark-stage a2h-retrospect
```

标记 `a2h-retrospect` 阶段水位（写 stage-marks fact，受授权门控、尽力而为）。token 用量由宿主生命周期采集，本步不采集。**忽略其退出码，绝不阻断流水线。**

> **Remember**：自动写入仅限 3 条件全满足（频次≥3 / 修复一致 / 确定性 100%）；不删已有条目、不自动 git apply；跑分析 / 增量 / 出报告前，**先按 §3·§5·§7 的 MUST 加载指针 Read 整个 reference 文件**（不得仅凭 body 摘要执行）。