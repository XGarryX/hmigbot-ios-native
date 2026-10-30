# migbot-increment-reviewing 文档审阅

面向 `spec`、`arch`、`design`、需求提案及需求分析产物的 Markdown 文档审阅技能。

## 支持的文档类型

| 类型 | 说明 |
|------|------|
| spec | 需求规格文档 |
| arch | 架构设计文档 |
| design | 详细设计文档 |
| proposal | 需求提案 |
| rq-parse | 需求解析产物 |
| rq-clarify | 需求澄清产物 |
| rq-codebase | 代码仓理解产物 |

## 两种模式

### 轻量审阅（默认）

适合日常文档优化，输出简短摘要 + 关键问题 + 优化稿。

### 详细审计（audit mode）

用户明确要求时进入，输出完整审计报告 + 证据 + 修复建议，可选评分/Critic。

## 流程图

### 总览

```mermaid
flowchart TD
  A["用户提交文档<br/>spec/arch/design/proposal/需求分析产物"] --> B["识别文档类型"]
  B --> C["判断作者意图"]
  C --> D{"用户是否要求<br/>完整审计、评分、追溯或 Critic？"}

  D -- "没有明确要求" --> E["轻量审阅"]
  D -- "明确要求" --> F["详细审计"]

  E --> G["输出<br/>简短摘要 + 关键问题 + 优化稿"]
  F --> H["输出<br/>审计报告 + 证据 + 修复建议<br/>可选评分 / Critic"]
```

### 轻量审阅流程

```mermaid
flowchart TD
  A["进入轻量审阅"] --> B["快速确认文档类型和作者意图"]
  B --> C["按 8 类常见问题扫描"]
  C --> D["挑出最影响质量的 3-5 个问题"]
  D --> E["给出位置、严重程度和原因"]
  E --> F["生成同类型优化稿"]
  F --> G["保留原文事实<br/>修复明显缺陷<br/>不补造业务事实"]
  G --> H["交付结果<br/>摘要 + 问题列表 + 优化稿"]
```

### 详细审计流程

```mermaid
flowchart TD
  A["进入详细审计"] --> B{"审计哪类文档？"}

  B -- "需求规格" --> C["按需求规格检查<br/>范围、角色、FR/NFR、验收标准、约束"]
  B -- "架构设计" --> D["按架构设计检查<br/>组件、依赖、技术决策、NFR 承接、风险"]
  B -- "详细设计" --> E["按详细设计检查<br/>接口契约、数据模型、状态流程、错误处理"]
  B -- "需求提案" --> P["按需求提案检查<br/>概述、解析、澄清、需求、影响范围、复杂度"]
  B -- "需求分析产物" --> R["按需求分析产物检查<br/>需求解析、需求澄清、代码仓理解"]

  C --> G["形成发现项"]
  D --> G
  E --> G
  P --> G
  R --> G

  G --> H["每条发现包含<br/>证据、位置、严重程度、修复建议"]
  H --> I{"是否要求评分？"}
  I -- "是" --> J["补充评分表和加权分"]
  I -- "否" --> K["跳过评分"]
  J --> L{"是否要求 Critic？"}
  K --> L
  L -- "是" --> M["检查发现项是否有证据支撑"]
  L -- "否" --> N["输出审计报告"]
  M --> N
```

### 资料加载规则

```mermaid
flowchart TD
  A["收到请求"] --> B{"运行模式"}

  B -- "轻量审阅" --> C["只加载轻量模板<br/>和 8 类问题指南"]
  C --> D{"文档类型不清楚？"}
  D -- "是" --> E["补充加载文档类型说明"]
  D -- "否" --> F["直接审阅"]

  B -- "详细审计" --> G["加载审计指南"]
  G --> H{"文档类型"}
  H -- "需求规格" --> I["加载需求规格检查项"]
  H -- "架构设计" --> J["加载架构设计检查项"]
  H -- "详细设计" --> K["加载详细设计检查项"]
  H -- "需求提案" --> P["加载需求提案检查项"]
  H -- "需求解析" --> Q["加载需求解析检查项"]
  H -- "需求澄清" --> R["加载需求澄清检查项"]
  H -- "代码仓理解" --> S["加载代码仓理解检查项"]

  G --> L{"用户要求评分或 Critic？"}
  L -- "评分" --> M["加载评分规则"]
  L -- "Critic" --> N["加载证据审计规则"]
  L -- "都没有" --> O["不加载额外资料"]
```

### 8 类问题检查顺序

```mermaid
flowchart TD
  A["开始检查"] --> B["D1 清晰性<br/>是否有模糊词或歧义"]
  B --> C["D2 完整性<br/>是否缺关键章节或要素"]
  C --> D["D5 追溯性<br/>编号和上下游引用是否断裂"]
  D --> E["D7 可验证性<br/>是否能写成测试或验收条件"]
  E --> F["D4 准确性<br/>是否有虚假标准、API 或组件"]
  F --> G["D3 一致性<br/>术语、状态和约束是否漂移"]
  G --> H["D6 可行性<br/>资源、性能和技术方案是否冲突"]
  H --> I["D8 可维护性<br/>是否存在硬编码、强耦合或缺扩展点"]
  I --> J["汇总主要问题"]
```

## 参考文件索引

### 目录结构

```
references/
├── audit-mode-guide.md         # 详细审计入口指南
├── audit-profiles/             # 审计配置（按文档类型）
│   ├── spec.md
│   ├── arch.md
│   ├── design.md
│   ├── proposal.md
│   ├── rq-parse.md
│   ├── rq-clarify.md
│   └── rq-codebase.md
├── audit-rules/                # 检查项（按文档类型）
│   ├── check-items-spec.md
│   ├── check-items-arch.md
│   ├── check-items-design.md
│   ├── check-items-proposal.md
│   ├── check-items-rq-parse.md
│   ├── check-items-rq-clarify.md
│   └── check-items-rq-codebase.md
├── audit-scoring/              # 评分规则
│   └── score.md
├── audit-critic/               # Critic 自查规则
│   └── critic.md
├── concise-review-template.md  # 轻量审阅输出模板
├── concise-dimensions-guide.md # D1-D8 缺陷检测清单
├── doc-type-profiles.md        # 文档类型说明
└── skill-improvement-guide.md  # Skill 优化建议
```

### 轻量审阅模式

| 加载时机 | 文件 | 用途 |
|----------|------|------|
| 必选 | `references/concise-review-template.md` | 输出模板 |
| 必选 | `references/concise-dimensions-guide.md` | D1-D8 缺陷检测清单 |
| 条件 | `references/doc-type-profiles.md` | 仅当文档类型不明确时加载 |

**禁止加载（轻量模式）：**
- `audit-rules/check-items-*.md`
- `audit-scoring/score.md`
- `audit-critic/critic.md`

### 详细审计模式

| 步骤 | 文件 | 用途 |
|------|------|------|
| 必选（入口） | `references/audit-mode-guide.md` | 路由表、解析规则、输出顺序 |
| 条件（按类型） | `references/audit-profiles/spec.md` | 需求规格审计配置 |
| 条件（按类型） | `references/audit-profiles/arch.md` | 架构设计审计配置 |
| 条件（按类型） | `references/audit-profiles/design.md` | 详细设计审计配置 |
| 条件（按类型） | `references/audit-profiles/proposal.md` | 需求提案审计配置 |
| 条件（按类型） | `references/audit-profiles/rq-parse.md` | 需求解析审计配置 |
| 条件（按类型） | `references/audit-profiles/rq-clarify.md` | 需求澄清审计配置 |
| 条件（按类型） | `references/audit-profiles/rq-codebase.md` | 代码仓理解审计配置 |
| 条件（按类型） | `references/audit-rules/check-items-spec.md` | 需求规格详细检查项 |
| 条件（按类型） | `references/audit-rules/check-items-arch.md` | 架构设计详细检查项 |
| 条件（按类型） | `references/audit-rules/check-items-design.md` | 详细设计详细检查项 |
| 条件（按类型） | `references/audit-rules/check-items-proposal.md` | 需求提案详细检查项 |
| 条件（按类型） | `references/audit-rules/check-items-rq-parse.md` | 需求解析详细检查项 |
| 条件（按类型） | `references/audit-rules/check-items-rq-clarify.md` | 需求澄清详细检查项 |
| 条件（按类型） | `references/audit-rules/check-items-rq-codebase.md` | 代码仓理解详细检查项 |
| 可选 | `references/audit-scoring/score.md` | 加权评分规则 |
| 可选 | `references/audit-critic/critic.md` | Critic 自查规则 |
| 可选 | `references/skill-improvement-guide.md` | Skill 优化建议（面向生成文档的 skill） |

## 缺陷维度（D1-D8）

| 维度 | 名称 | 说明 |
|------|------|------|
| D1 | 清晰性 | 模糊词、歧义表达 |
| D2 | 完整性 | 缺失关键章节或要素 |
| D3 | 一致性 | 术语、状态、约束漂移 |
| D4 | 准确性 | 虚假标准、API、组件引用 |
| D5 | 追溯性 | 编号和上下游引用断裂 |
| D6 | 可行性 | 资源、性能、技术方案冲突 |
| D7 | 可验证性 | 无法写成测试或验收条件 |
| D8 | 可维护性 | 硬编码、强耦合、缺扩展点 |

## 输出原则

- 保留原文已成立的事实
- 修复检测到的所有缺陷
- 合理补全必须标注 `Assumption:` 或 `Reviewer suggestion:`
- 不得捏造业务事实

## 触发方式

当用户提到以下关键词时触发：
- "审阅文档"、"review"、"文档评审"
- "审计"、"audit"
- "优化文档"、"优化提案"