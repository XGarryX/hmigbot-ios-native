---
name: migbot-increment-reviewing
description: 审阅 SDD / Spec 类 Markdown 文档（spec、arch、design）及需求提案、需求解析、需求澄清、代码仓理解产物，先判断作者意图与文档类型，再输出更贴近原意的优化稿。默认走轻量模式；只有在用户明确要求完整审计时，才进入 audit mode。
---

# SDD / Spec 文档审阅

面向 `spec`、`arch`、`design` 及 OpenSpec 中可映射到这三类的 Markdown 文档；同时支持需求提案、需求解析、需求澄清、代码仓理解四类需求分析产物。非支持类型的输入内容只能作为背景上下文辅助判断，不进入主输出文档集合。

核心目标：
- 判断文档是否用合适形式表达作者意图
- 直接产出更清晰、结构更稳、但不捏造事实的优化版本

## 模式选择

默认使用 `default concise`。只有用户明确要求以下内容时才进入 `audit mode`：
- 完整审阅报告
- 评分表或加权分
- 完整问题清单
- 追溯矩阵或全链路追溯
- Critic 审查
- 跨需求规格、架构设计、详细设计的全链路审计
- 面向生成这些文档的 skill 给出优化建议

## 默认轻量模式（default concise）

默认模式加载：
- `references/concise-review-template.md`（输出模板）
- `references/concise-dimensions-guide.md`（D1-D8 缺陷检测清单）
- `references/doc-type-profiles.md`（仅当文档类型不明确）

默认模式禁止加载：
- `references/audit-rules/check-items-*.md`（详细检查项，audit mode 专用）
- `references/audit-scoring/score.md`（评分，需用户明确要求）
- `references/audit-critic/critic.md`（Critic 自查，需用户明确要求）

### 默认轻量模式检测流程

1. 加载 `concise-dimensions-guide.md`，了解 8 个缺陷维度的定义
2. 按指南中的「快速检测流程」顺序扫描文档：
   D1 模糊词 → D2 完整性 → D5 追溯性 → D7 可验证性 → D4 准确性 → D3 一致性 → D6 可行性 → D8 可维护性
3. 将发现的缺陷按模板要求格式输出：`- **D{编号}**，{严重程度}：{位置}`
4. 生成优化稿时，**必须修复检测到的缺陷**：
   - D1 模糊词 → 替换为定量标准
   - D7 不可验证 → 补充二元判定条件
   - D2 缺失类别 → 以 `Assumption:` 或 `Reviewer suggestion:` 标注补全
   - D5 断裂 ID → 修复编号和引用
   - D4 虚假引用 → 删除或标注为需核实
   - 不得捏造原文没有的业务事实

输出必须严格使用 `references/concise-review-template.md`，包含：
1. 简短审阅摘要
2. 带 D 维度标签的关键问题（3-5 条）
3. 修复了已检测缺陷的优化稿

## 详细审计模式（audit mode）

进入 audit mode 后先加载：
- `references/audit-mode-guide.md`（已包含路由表、解析规则、输出顺序）

再根据文档类型只加载一个审计配置及对应的检查项：
- `references/audit-profiles/spec.md` + `references/audit-rules/check-items-spec.md`
- `references/audit-profiles/arch.md` + `references/audit-rules/check-items-arch.md`
- `references/audit-profiles/design.md` + `references/audit-rules/check-items-design.md`
- `references/audit-profiles/proposal.md` + `references/audit-rules/check-items-proposal.md`
- `references/audit-profiles/rq-parse.md` + `references/audit-rules/check-items-rq-parse.md`
- `references/audit-profiles/rq-clarify.md` + `references/audit-rules/check-items-rq-clarify.md`
- `references/audit-profiles/rq-codebase.md` + `references/audit-rules/check-items-rq-codebase.md`

只有当需要评分或 Critic 时才按需打开：
- `references/audit-scoring/score.md` — 加权评分
- `references/audit-critic/critic.md` — Critic 自查

当用户要求评估或优化生成文档的 skill 时，额外打开：
- `references/skill-improvement-guide.md` — 将文档缺陷反推为 skill 优化建议

## 输出原则

优化稿必须：
- 保留原文中已经成立的事实
- 改善结构、层次和抽象粒度
- 更贴近推断出的作者意图
- 删除无关或干扰性内容
- 不补造业务事实
- **修复检测到的所有缺陷**（D1-D8）

缺陷修复规则：
- D1 模糊词 → 替换为合理的定量标准（参考原文上下文中已有的数值）
- D7 不可验证 → 补充具体错误码或二元判定条件
- D2 缺失 → 以 `> Assumption:` 或 `> Reviewer suggestion:` 标注补全内容
- D5 断裂 → 修复编号一致性和交叉引用
- D4 虚假 → 删除无法核实的引用

如果为了让文档可用而必须做合理补全，只能明确标注：
- `Assumption:`
- `Reviewer suggestion:`

## 作者意图画像

审阅前先做轻量画像：
- 可能目标
- 目标读者
- 重点内容
- 非重点内容
- 抽象层级
- 偏好的表达形式

核心判断：这份文档是否在“用对的形式表达对的内容”。
