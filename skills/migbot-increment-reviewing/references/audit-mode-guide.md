# Audit Mode Guide

Enter audit mode only if the user explicitly asks for: full audit report, scoring or weighted score, complete findings list, traceability matrix, Critic review, or cross-document `spec + arch + design` audit. Otherwise stay in `default concise`.

## Minimal Audit Path

```
classify document type
→ load one audit profile (spec/arch/design)
→ extract only required fields
→ run checks from that profile
→ summarize findings# 详细审计模式指南

只有用户明确要求完整审计报告、评分或加权分、完整问题清单、追溯矩阵、Critic 审查，或跨需求规格、架构设计、详细设计的全链路审计时，才进入 audit mode。其他情况保持 `default concise`。

如果用户要求评估或优化生成这些文档的 skill，也进入 audit mode，并额外输出 skill 优化映射。

## 最小审计路径

```
识别文档类型
→ 加载一个审计配置（需求规格 / 架构设计 / 详细设计 / 需求提案 / 需求解析 / 需求澄清 / 代码仓理解）
→ 只提取必要字段
→ 运行该审计配置的检查项
→ 汇总发现项
→ 按需评分或执行 Critic
```

## 审计配置路由

| 文档类型 | 加载内容 |
|---------------|------|
| `spec` | `audit-profiles/spec.md` |
| `arch` | `audit-profiles/arch.md` |
| `design` | `audit-profiles/design.md` |
| 需求提案 | `audit-profiles/proposal.md` |
| 需求解析 | `audit-profiles/rq-parse.md` |
| 需求澄清 | `audit-profiles/rq-clarify.md` |
| 代码仓理解 | `audit-profiles/rq-codebase.md` |
| 不明确 | 先加载 `doc-type-profiles.md`，再选择一个审计配置 |

## 文档类型解析

不要只依赖文件名。必须结合文件名、目录和正文内容判断。如果文件名与正文不一致，优先相信正文，但降低置信度。

### 需求类文档（spec-like）提取目标
- 范围（包含 / 排除）
- 参与者 / 角色
- 功能需求（包含 ID、描述、验收标准）
- 非功能需求（类别、指标；如有）
- 约束（技术 / 合规 / 资源）
- 术语表 / 术语定义

功能需求通常包含“必须 / 应当 / shall / should / must”等表达。NFR 通常包含定量指标或质量属性关键词。

### 架构类文档（arch-like）提取目标
- 组件（名称、职责、暴露接口）
- 依赖关系（来源、目标、类型、协议）
- 技术栈（类别、选型、理由）
- NFR 策略（质量属性、方案、目标指标）
- 带理由的设计决策

组件列表优先来自架构图图例或独立组件章节。技术选型通常出现在“技术栈”或“设计决策”章节。

### 详细设计类文档（design-like）提取目标
- 接口（输入、输出、错误、前置/后置条件、副作用、并发语义）
- 数据模型（字段、约束、关系、索引）
- 算法 / 关键流程（伪代码或分步说明、边界情况）
- 状态机（状态、转换、初始/终止状态、非法转换处理）
- 错误处理策略（范围、重试/降级、错误类别）

接口定义可能分散在多个章节，需要按接口合并。数据模型可能以表格、伪 SQL 或 ER 图形式出现。

### 需求提案提取目标
- 需求概述（功能名称、需求类型、关联特性、需求描述、使用场景、预期效果）
- 需求解析报告
- 需求澄清结果
- 功能需求和可靠性需求
- 影响范围分析
- 复杂度评估和跳过策略
- 待解决问题

重点判断：需求提案是否把前置分析、用户决策、需求条目、影响范围和后续制品策略串成一条可执行链路。

### 需求解析产物提取目标
- 原始需求
- 意图分类（类型、一句话概括）
- 领域映射
- 影响层次
- 关键实体
- 模糊点及严重程度
- 复杂度评估

重点判断：解析是否覆盖了需求分析所需的结构化信息，是否把不确定内容标为模糊点，而不是直接当成事实。

### 需求澄清产物提取目标
- 待澄清模糊点
- 提问批次和问题列表
- 用户回答或默认决策
- 已澄清的关键决策
- 待定假设
- 功能边界（包含 / 不包含）

重点判断：是否优先处理 blocker 模糊点，问题是否少而准，澄清结果是否能直接支撑后续需求规格生成。

### 代码仓理解产物提取目标
- 需求类别
- 重点分析类别
- 架构分析
- 接口 / 契约识别
- 公共组件或函数识别
- 影响范围分析
- 现有代码分析
- 风险识别
- 测试验证策略
- 监控运维支持

重点判断：是否基于真实代码证据、是否按需聚焦相关模块、是否输出可被后续需求分析直接使用的 `info.md`。

## 重型参考资料

不要一次性加载全部重型资料。只有审计配置指向具体检查项，或用户明确要求时才打开：
- `check-items-spec.md` / `check-items-arch.md` / `check-items-design.md`：详细检查规则
- `check-items-proposal.md`：需求提案详细检查规则
- `check-items-rq-parse.md` / `check-items-rq-clarify.md` / `check-items-rq-codebase.md`：需求分析产物详细检查规则
- `scoring/overview.md`：加权评分规则，仅在用户要求数字评分时使用
- `critic/quick-protocol.md`：Critic 自查协议
- `skill-improvement-guide.md`：skill 优化映射，仅在用户要求评估或优化 skill 时使用

## 输出顺序

1. 一句话结论
2. 文档类型和审计范围
3. 关键发现项（证据 + 修复建议）
4. 可选评分摘要（仅在用户要求时输出）
5. 可选 Critic 结果（仅在用户要求时输出）
6. 可选 skill 优化建议（仅在用户要求评估或优化 skill 时输出）

→ optionally score or run Critic
```

## Profile Routing

| Document type | Load |
|---------------|------|
| `spec` | `audit-profiles/spec.md` |
| `arch` | `audit-profiles/arch.md` |
| `design` | `audit-profiles/design.md` |
| unclear | `doc-type-profiles.md`, then one profile |

## Document Type Parsing

Do not rely on exact filenames. Classify by filename + directory + content together. If filename and content differ, prefer content but lower confidence.

### spec-like extraction target
- scope (included / excluded)
- actors / roles
- functional requirements (with IDs, descriptions, acceptance criteria)
- non-functional requirements (category, metric if available)
- constraints (technology / compliance / resource)
- glossary / term definitions

Functional requirements typically start with "shall / should / must". NFRs have quantitative metrics or quality-attribute keywords.

### arch-like extraction target
- components (name, responsibility, exposed interfaces)
- dependencies (source, target, type, protocol)
- tech stack (category, choice, rationale)
- NFR strategies (quality attribute, approach, target metric)
- design decisions with rationale

Component lists preferably come from architecture diagram legend or standalone sections. Tech choices appear in "tech stack" or "design decisions" sections.

### design-like extraction target
- interfaces (input, output, errors, pre/postconditions, side effects, concurrency)
- data models (fields, constraints, relationships, indexes)
- algorithms / key flows (pseudocode or step-by-step, edge cases)
- state machines (states, transitions, initial/terminal, illegal handling)
- error handling strategy (scope, retry/fallback, categories)

Interface definitions may be scattered; consolidate per interface. Data models may appear as tables, pseudo-SQL, or ER diagrams.

## Heavy References

Do not load these wholesale. Open only when a profile points to a specific section:
- `check-items-spec.md` / `check-items-arch.md` / `check-items-design.md` — detailed check rules
- `scoring-criteria.md` — weighted scoring details (only if user asks for numeric scores)
- `critic/quick-protocol.md` — Critic self-review

## Output Order

1. One-sentence conclusion
2. Document type and audit scope
3. Key findings (evidence + remediation)
4. Optional score summary (only if asked)
5. Optional Critic result (only if asked)
