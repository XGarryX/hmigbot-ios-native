---
name: a2h-retrospect
description: 第五步：回顾本轮迁移，沉淀经验，优化 skill。分析 plan vs 实际差异，提取确定性修正和设计决策。双 Pipeline 经验对比。即使用户只说"回顾"或"优化"，也应触发。
metadata:
  type: pipeline
  domain: migration
  tags:
  - pipeline
  - migration
---
# a2h-retrospect

## 1. 定位

Pipeline 层第五步，**闭环自优化**。让 Domain Skill 越用越好。

```
a2h-spec → a2h-plan → a2h-execute → a2h-verify → a2h-retrospect（本 skill）
                                                       │
                                                       ├─ 分析差异
                                                       ├─ 提取经验
                                                       ├─ 分类沉淀
                                                       └─ 生成回顾报告
```

**核心原则**：满足自动写入条件（频次 ≥3、修复一致、确定性 100%）的模式自动写入 skill references；不满足条件的仍暂存为 staged patch。

---

## 2. 输入与前置检查

自动读取：

| 文件 | 用途 |
|------|------|
| `spec/plans/plan-*.md` | 计划：suggested_skills + task 列表 |
| `spec/migration-report.md` | 实际执行：skill 使用 + 覆盖记录 + 失败列表 |
| `spec/verify-report.md` | 验证结果：通过/失败项 |
| `spec/baseline/ui-manifest.md` | UI 页面清单与 confidence 评估 |
| `spec/baseline/source-coverage-report.md` | 源码侧覆盖审计（a2h-spec C4.6b 产出）；复盘漏判 domain / 欠锚包 / 跨子仓 seam（外部 auditor 存在时另读 `feature-coverage-report.md`，多子仓另读 `module-dep-graph.json`）|
| `git diff` / `git log`（本轮范围）| 代码变更全貌 |

> 若 git log 为 [`commit`](../commit/SKILL.md) skill 的 7 字段结构化格式，用 `git log --grep='Category:'` 提取 Category/Issue-Type/Skill/Tools/Spec-Ref/Fix-Approach 分布，替代部分 git diff 分析；否则跳过机器解析，仅用 git diff。

**前置检查（gate）**：
- `spec/verify-report.md` 不存在 → 提示"请先执行 a2h-verify"，**终止**
- `spec/migration-report.md` 不存在 → 提示"请先执行 a2h-execute"，**终止**
- `spec/plans/plan-*.md` 不存在 → WARN"无 plan，跳过 plan vs actual 对比"，继续

---

## 3. 分析流程（5 步）

> **MUST 加载** [references/analysis-flow.md](./references/analysis-flow.md) —— 每步详细决策流程图 / Stage 对比 / Confidence 评估逻辑在此；下方仅为概览，执行时以 reference 为准。

1. **Skill 使用差异 + Stage 对比** —— plan `suggested_skills` vs migration-report 实际 → 标 MATCH/OVERRIDE/DOWNGRADE/UNUSED，算覆盖率；对比 Stage 1 直接转换与 Stage 3 补充转换的编译错误率、保真度。
2. **编译错误 Pattern 提取** —— 从 `hmos-fix-build-errors` 修复记录按 5 类（类型/导入/API/语法/配置）提取 {错误特征, 修复方案, 频次}。
3. **API 修正提取** —— 从 `arkts-knowledge-verifier` 记录提取 {原签名 → 正确签名, 原因}（替换/升级/新增三类映射）。
4. **分类** —— Step 2-3 结果分为 **确定性修正**（100% 可自动应用）与 **设计决策**（需人工判断架构选择）。
5. **Confidence 准确度评估** —— a2h-spec 的 confidence 预测 vs 实际转换质量 → 标 ACCURATE/OVER_ESTIMATED/UNDER_ESTIMATED，输出总体准确率/高估率/低估率。
6. **spec 覆盖审计复盘** —— 读 `source-coverage-report.md`（及 `feature-coverage-report.md` / 多子仓 `module-dep-graph.json`），量化本轮「漏判 domain / 欠锚包 / 跨子仓 seam 不一致」，归因到 a2h-spec 的判定规则缺口，作为下条改进项的来源。

---

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
| 资源映射修正 | `android2hmos-resources-convert` | `references/` 对应文件 |
| 组件映射修正 | `arkts-component-builder` | `references/` 对应文件 |
| App 身份配置修正 | `arkts-app-identity` | `references/` 对应文件 |
| UI 模式修正 | `arkts-pattern-library` | `references/` 对应文件 |
| spec 欠规约 / 覆盖判定缺口 | `a2h-spec` | `score_complexity.py` 的 `D` 校准、tier 阈值、C4.6b skip-list 规则（仅确定性修正写入，否则降级 Staged Patch）|

**Staged Patch（降级路径）**：生成 `.patch` 到 `.agents/skills/<target>/references/`，命名 `<date>-<brief>.patch`，报告标 PENDING_REVIEW 等用户审核。

### 4b. 设计决策 → 变更摘要

列出 {决策内容, 选择原因, 影响范围} → 等人工审批 → 通过后才写入 `docs/development-experience.md` 或对应 skill reference。

### 4c. 关键经验 → 项目记忆文件

将本次迁移中值得跨会话复用的经验写入目标项目的 `spec/memory/` 目录（每条经验一个 markdown 文件）：

```
经验类型筛选:
  │
  ├─ 确定性修正中出现 3+ 次的 pattern → 写入 feedback memory
  │   示例: "ArkTS 中不能用 @ohos. 前缀，必须用 @kit."
  │
  ├─ 设计决策中被用户审批通过的选择 → 写入 project memory
  │   示例: "LazyForEach 性能优于 ForEach，大列表场景始终使用 LazyForEach"
  │
  ├─ Skill 覆盖率分析中的 OVERRIDE 原因 → 写入 feedback memory
  │   示例: "有 Android 源码时，dispatcher 比直接调 component-builder 质量更高"
  │
  ├─ 双 Pipeline 对比结论 → 写入 feedback memory
  │   示例: "Stage 1 direct conversion produces better UI than Stage 3 re-creation"
  │
  └─ Confidence 准确度发现 → 写入 project memory
      示例: "confidence:medium pages with complete layout XML converted well"
```

每个记忆文件遵循 frontmatter + 正文的结构（frontmatter 至少含 name / description / type）。

---

## 5. 增量学习模式（可选）

`a2h-execute` 编译检查点后可触发增量学习，无需等完整 retrospect。**完整流程 + `retrospect-counter.json` schema MUST 加载** [references/incremental-learning.md](./references/incremental-learning.md)。

要点：读本次修复日志 → 对比已有 references → 新模式累计 ≥3 自动写入、<3 记入 `spec/retrospect-counter.json`；count 达 3 自动晋升写入 references 并在报告记 `AUTO_PROMOTED`。

---

## 6. 安全边界

**自动写入范围（满足 3 个条件时允许）**：
- 写入 `.agents/skills/*/references/` 中的 `known-patterns.md`、`api-corrections.md`、`verified-symbols.md`
- 追加新条目或更新已有条目的频次/日期

**绝对不做的事**：
- 不删除 references 文件中的已有条目
- 不直接修改 `docs/development-experience.md`
- 不直接修改 `docs/dev-pitfalls.md`
- 不自动 `git apply` .patch 文件

**降级为 Staged Patch 时的操作**：
- 生成 .patch 文件（新建文件，不覆盖已有文件）
- 输出变更摘要（在报告中列出）
- 提供 review 指引（告诉用户如何操作）

用户审核 Staged Patch 的命令示例：

```bash
# Review patch
cat .agents/skills/hmos-fix-build-errors/references/YYYY-MM-DD-import-fix.patch

# Apply patch
cd .agents/skills/hmos-fix-build-errors/references/
git apply YYYY-MM-DD-import-fix.patch
```

---

## 7. 回顾报告

存储路径：`docs/retrospect-report-YYYY-MM-DD.md`。**完整报告模板 MUST 加载** [references/report-template.md](./references/report-template.md) —— 含 Skill 覆盖分析 / 编译错误 Pattern / API 修正 / 确定性修正 Patch / Pipeline 对比 / Confidence 准确度 / 设计决策 / 操作指引 共 8 段。

---

## 8. 与 Domain Skill 的关系

a2h-retrospect 是**经验沉淀层**，只读取产出做分析、**不调用** Domain Skill 改代码：分析 `hmos-fix-build-errors`（编译 pattern）/ `arkts-knowledge-verifier`（API 修正）/ `a2h-execute` Stage 1 派发记录（覆盖率）→ 沉淀到各目标 `references/` + `docs/retrospect-report-*.md`。

---

## 9. 触发 Prompt 示例

"回顾" / "优化 skill" / "总结这次迁移经验" / "沉淀一下踩坑" / "有哪些 pattern 可以复用" → 触发；先检查 `spec/verify-report.md`，不存在则提示先跑 a2h-verify。

---

## 10. 数据采集与上报

**本节是 a2h-retrospect 的必跑收尾步骤**：§7 回顾报告产出 ≠ skill 完成。报告写出来之后必须紧接着把下面两条命令跑完，skill 才算真正结束。

**【硬约束】严禁**用 Write / Edit / NotebookEdit 工具直接创建或修改 `.migbot/metrics/` 下任何文件——所有产物必须由下列 `.migbot/bin/a2h` 命令作为副产物生成。手工伪造文件等于把假数据上报给服务端。

> 全程由**主 agent** 在当前会话里直接调 Bash，**不要派发 subagent**。

原始 transcript 通道现在是自动的：Codex 生命周期 hook 会上传会话切片，服务端据此重新解析出用量数据。因此本步只剩两条命令（每条都是纯本地 Bash，不需要 LLM 推理）：

```bash
# 1. 代码行数对比（LOC 事实）→ code-lines.json
.migbot/bin/a2h count-lines

# 2. 收尾：标记 retrospect 阶段，写出 <project>/retrospect.done sentinel
.migbot/bin/a2h mark-stage a2h-retrospect
```

**步骤说明**

- **#1** `count-lines` 产出 Android / HarmonyOS 两侧按文件类型的行数，并记录 `android_app_name` / `harmonyos_app_name`。其中 `file_type:"total"` 为**核心代码行数**——仅累加源码与 UI/资源（`.java/.kt/.xml/.ets/.ts/.arkt/.proto`），已排除构建/依赖配置（`gradle/kts/properties/json/yaml/yml`）与文档（`.md/.txt` 本就不在统计列表内）；各配置类型仍保留独立的 per-type 记录，仅不计入 `total`。
- **#2** `mark-stage a2h-retrospect` 写出本阶段的 stage-marks fact，并落下 `.migbot/metrics/<project>/retrospect.done` sentinel（命令会剥掉 `a2h-` 前缀）——**这个 sentinel 就是 `$a2h-run` 用来判定 retrospect 阶段完成的 marker**。受授权门控、尽力而为，忽略退出码、绝不阻断。

---

## 11. Commit 提示（回顾完成后）

回顾报告生成后，建议调 [`commit`](../commit/SKILL.md) 提交本轮产出（references 自动写入 + staged patches）：报告 + 自动写入 → 大类=`verify`，Skill=`a2h-retrospect`，Fix-Approach="提取 N 个新 pattern 写入 references"；仅 staged patches → 不 commit（用户 review 后再提交）。

---

## References 索引

| 文件 | 何时加载 |
|---|---|
| [`references/analysis-flow.md`](./references/analysis-flow.md) | 执行 §3 分析 5 步，需每步详细决策图 / Stage 对比 / Confidence 评估 |
| [`references/report-template.md`](./references/report-template.md) | 生成 §7 回顾报告 |
| [`references/incremental-learning.md`](./references/incremental-learning.md) | §5 增量学习触发，需 `retrospect-counter.json` schema |

> **Remember**：自动写入仅限 3 条件全满足（频次≥3 / 修复一致 / 确定性 100%）；不删已有条目、不自动 git apply；跑分析 / 增量 / 出报告前，**先按 §3·§5·§7 的 MUST 加载指针 Read 整个 reference 文件**（不得仅凭 body 摘要执行）。
