# Fuxi ArkTS 开发与上线指南

新增 Skill、Agent 及其他能力类型的开发规范、自检流程和上线步骤。

---

## 1. 开发 Skill

### 1.1 创建目录

```bash
mkdir -p arkts-skills/skills/<skill-name>/references
```

命名规范：
- Domain Skill 以 `arkts-` 前缀命名，例如 `arkts-xxx-manager`
- Pipeline Skill 以 `a2h-` 前缀命名
- 分析工具以 `android-` 前缀命名
- 全小写，单词间用 `-` 连接

### 1.2 编写 SKILL.md

```markdown
---
name: <skill-name>
description: >
  一句话描述该 Skill 的用途和覆盖范围。
---

## 定位

描述该 Skill 在整体架构中的位置、与其他 Skill 的关系。

## 核心能力

列出该 Skill 能做什么，包含具体的技术细节和模式。

## 使用方式

说明如何调用该 Skill，输入/输出约定。

## 参考文档

- [xxx 参考](references/xxx.md)
```

**必需项**：
- frontmatter 必须包含 `name` 和 `description` 字段
- frontmatter 以 `---` 开头和结尾
- 如果 SKILL.md 中引用了 `references/` 下的文件，该文件必须存在

### 1.3 添加 references/

将该 Skill 需要的参考材料放入 `references/` 目录：

```
arkts-skills/skills/<skill-name>/
├── SKILL.md
└── references/
    ├── api-reference.md
    ├── patterns.md
    └── examples.md
```

SKILL.md 中通过 Markdown 链接引用：`[API 参考](references/api-reference.md)`

### 1.4 添加评测（可选）

```json
// evals.json
{
  "skill_name": "<skill-name>",
  "evals": [
    {
      "id": 1,
      "prompt": "用户提示词",
      "expected_output": "期望的输出行为描述",
      "files": []
    }
  ]
}
```

---

## 2. 开发 Agent

### 2.1 创建文件

```bash
touch arkts-agents/agents/<agent-name>.md
```

命名规范：以 `a2h-` 前缀命名，例如 `a2h-xxx-worker`。

### 2.2 编写 Agent 定义

```markdown
---
name: <agent-name>
description: 一句话描述该 Agent 的职责。
tools: Read, Glob, Grep, Bash, Edit, Write
skills: skill-a, skill-b, skill-c
model: opus
color: green
---

You are a **[Role Name]** — 描述该 Agent 的角色定位。

## How You Work

1. 读取 prompt 指定的任务
2. 调用指定的 skill(s)
3. 执行并返回结果

## Rules

- 必须使用 prompt 中指定的 skill
- ...（其他约束）
```

**frontmatter 字段说明**：

| 字段 | 必需 | 说明 |
|------|------|------|
| name | 是 | Agent 名称 |
| description | 是 | 一句话描述 |
| tools | 是 | 可用的工具列表 |
| skills | 否 | 依赖的 Skill 列表（逗号分隔），每个必须是 arkts-skills/skills/ 下的有效目录 |
| model | 否 | 推荐模型（opus / sonnet） |
| color | 否 | 在 UI 中的标识颜色 |

---

## 3. 开发其他能力类型

### 3.1 Command（Slash Command）

在 `commands/` 下创建 `.md` 文件：

```markdown
# /<command-name>

Slash Command — 一句话描述。

## 行为

触发哪些 Skill/Agent，执行什么流程。

## 使用方式

/<command-name> <参数说明>
```

### 3.2 Rule（Project Rule）

在 `rules/` 下创建 `.md` 文件：

```markdown
# 规则标题

## 适用范围

哪些场景下该规则生效。

## 规则内容

具体的编码约束、命名规范、使用限制等。
```

Rule 文件会自动注入到会话上下文，内容应精炼、可执行、无歧义。

### 3.3 Template

在 `templates/` 对应子目录下创建模板文件：

```
templates/
├── project-init/<template-name>/    # 包含完整项目结构
└── pages/<page-name>.ets            # 单页模板
```

### 3.4 Knowledge Base

在 `knowledge/` 对应子目录下添加结构化数据：

```
knowledge/
├── api-mapping/<category>.json      # API 映射表（JSON 格式）
└── patterns/<pattern-name>.md       # 迁移 Pattern 文档
```

### 3.5 MCP Server

在 `mcp-servers/<server-name>/` 下实现：

```
mcp-servers/<server-name>/
├── server.py          # MCP Server 实现
├── requirements.txt   # Python 依赖
└── README.md          # 使用说明
```

### 3.6 Hook

在 `.claude-plugin/hooks/` 下添加 shell 脚本，并在 `plugin.json` 的 `hooks` 字段中注册：

```json
{
  "hooks": {
    "session-start": ".claude-plugin/hooks/session-start.sh",
    "<event-name>": ".claude-plugin/hooks/<script>.sh"
  }
}
```

---

## 4. CI 五项验证详解

开发完成后运行 `npm run ci`，依次执行以下 5 项检查：

### 4.1 lint:skills — Skill 格式校验

**脚本**: `scripts/ci/lint-skills.sh`

逐个扫描 `arkts-skills/skills/` 下的所有目录，对每个 Skill 检查：

| # | 检查项 | 通过条件 | 失败示例 |
|---|--------|----------|----------|
| 1 | SKILL.md 存在 | 目录下有 SKILL.md 文件 | `ERROR: [xxx] Missing SKILL.md` |
| 2 | frontmatter 格式 | 文件首行是 `---` | `ERROR: [xxx] SKILL.md does not start with frontmatter (---)` |
| 3 | name 字段 | frontmatter 中包含 `name:` | `ERROR: [xxx] SKILL.md frontmatter missing 'name' field` |
| 4 | description 字段 | frontmatter 中包含 `description:` | `ERROR: [xxx] SKILL.md frontmatter missing 'description' field` |
| 5 | references/ 目录 | 如果 SKILL.md 引用了 `references/`，该目录必须存在 | `ERROR: [xxx] SKILL.md references 'references/' but directory does not exist` |

### 4.2 check:refs — 引用完整性校验

**脚本**: `scripts/ci/check-refs.sh`

扫描每个 SKILL.md 中对 `references/` 下具体文件的引用，验证文件实际存在。

识别三种引用格式：

| 格式 | 示例 | 说明 |
|------|------|------|
| Markdown 链接 | `[参考](references/api.md)` | 最常见的引用方式 |
| 反引号列表项 | `` - `references/api.md` `` | 文件列表中的引用 |
| HTML 注释 | `<!-- references/api.md -->` | 隐式引用 |

跨 Skill 引用（如 `other-skill/references/xxx.md`）会自动排除，不检查。

**失败示例**: `ERROR: [xxx] Referenced path does not exist: references/nonexistent.md`

### 4.3 check:agents — Agent 绑定校验

**脚本**: `scripts/ci/check-agents.sh`

解析 `arkts-agents/agents/` 下每个 `.md` 文件的 frontmatter，提取 `skills:` 字段（逗号分隔的 Skill 列表），验证每个 Skill 名对应的目录存在于 `arkts-skills/skills/` 下。

| 情况 | 输出 | 说明 |
|------|------|------|
| 正常 | `INFO: [a2h-migration-worker] 28 skills checked` | 所有引用的 Skill 目录都存在 |
| 无 skills 字段 | `INFO: [a2h-android-analyzer] No skills field in frontmatter, skipping` | 该 Agent 不依赖任何 Skill，跳过 |
| 无 frontmatter | `WARN: [xxx] No frontmatter found, skipping` | 文件格式不标准，跳过 |
| 引用不存在 | `ERROR: [xxx] References non-existent skill: bad-skill` | Skill 目录不存在，必须修复 |

### 4.4 check:counts — 计数一致性校验

**脚本**: `scripts/ci/check-counts.sh`

对比**实际目录数量**与 `arkts-skills/skills/README.md` 中的**声明数量**，检查是否一致。

**实际计数逻辑**：

```
总目录数（arkts-skills/skills/ 下所有子目录）
  - Pipeline Skills（a2h-spec, a2h-plan, a2h-execute, a2h-verify, a2h-retrospect）
  - 工具（drawio）
  = Domain Skills
```

**从 README.md 提取声明**（grep 匹配模式）：

| 模式 | 示例匹配 |
|------|----------|
| `N 个 Pipeline Skills` | "5 个 Pipeline Skills" → 5 |
| `N 个 Domain Skills` | "29 个 Domain Skills" → 29 |
| `N 个 Agent` | "3 个 Agent" → 3 |

三组数字分别对比，任一不匹配即报错。

**典型场景**：新增一个 Skill 后忘记更新 README 中的数量 → `ERROR: Domain Skills count mismatch: README says 29, actual is 30`

### 4.5 check:plugin — 插件元数据校验

**脚本**: `scripts/ci/validate-plugin.sh`

校验 `.claude-plugin/plugin.json` 的格式和内容：

| # | 检查项 | 通过条件 | 失败示例 |
|---|--------|----------|----------|
| 1 | JSON 合法 | python3 能解析 | `ERROR: plugin.json is not valid JSON` |
| 2 | 必需字段 | name, version, description, author, skills, agents 都存在且非空 | `ERROR: Missing or empty required field: author` |
| 3 | 版本号格式 | 符合 semver（x.y.z） | `ERROR: Version 'v1' does not match semver format` |
| 4 | 路径有效 | skills 和 agents 指向的目录存在 | `ERROR: Skills path does not exist: arkts-skills/skills/` |
| 5 | 版本一致 | plugin.json 的 version 与 package.json 的 version 相同 | `ERROR: plugin.json version (1.0.0) does not match package.json version (1.1.0)` |

---

### 自检清单汇总

开发完成后，按以下清单逐项确认：

**Skill 相关**：
- [ ] SKILL.md frontmatter 包含 `name` 和 `description`
- [ ] SKILL.md 引用的 references/ 文件都存在
- [ ] `npm run lint:skills` 通过
- [ ] `npm run check:refs` 通过

**Agent 相关**：
- [ ] frontmatter 的 `skills` 列表中每个 Skill 目录都存在
- [ ] `npm run check:agents` 通过

**计数相关**：
- [ ] 更新 `arkts-skills/skills/README.md` 中的数量声明和分类表
- [ ] `npm run check:counts` 通过

**版本相关**：
- [ ] `plugin.json` 和 `package.json` 版本号一致
- [ ] `npm run check:plugin` 通过

**全量验证**：

```bash
npm run ci    # 一键跑全部 5 项，所有 PASSED 即可提 PR
```

---

## 5. 上线流程

### 5.1 开发阶段

```
1. 从 staging 分支拉取 feature 分支
   git checkout staging && git pull
   git checkout -b feat/<feature-name>

2. 开发 Skill/Agent/其他能力

3. 本地自检
   npm run ci  →  全部 PASSED

4. 提交
   git add <files>
   git commit -m "feat: add <skill-name> for <purpose>"
```

### 5.2 PR 阶段

```
5. 提交 PR 到 staging
   git push -u origin feat/<feature-name>
   gh pr create --base staging

6. GitHub Actions 自动运行 PR Check（5 项校验）
   - skill-lint       ✅
   - ref-check        ✅
   - agent-binding    ✅
   - count-consistency ✅
   - plugin-validate  ✅

7. Code Review + PR Check 全绿 → 合入 staging
```

### 5.3 验证阶段

```
8. staging 分支定期运行全链路 E2E（Phase 2 后生效）
   - 自动执行迁移场景
   - 评分对比基准线
   - 劣化 → 创建 Issue 标记
   - 通过 → 自动创建 staging → main 的 PR

9. 人工确认 → 合入 main
```

### 5.4 发布阶段

```
10. 更新版本号
    package.json + plugin.json 同步更新
    更新 CHANGELOG.md

11. 打 tag
    git tag v1.x.x
    git push origin v1.x.x

12. GitHub Actions 自动触发 release.yml（Phase 4 后生效）
    - 完整 E2E 验证
    - 生成质量报告
    - 发布到插件市场
```

### 5.5 流程总览

```
feat 分支 ──→ PR ──→ staging ──→ E2E 验证 ──→ main ──→ tag ──→ release
               │                    │                    │
          PR Check（自动）     定期全链路（自动）     发布门禁（自动）
          Code Review（人工）   劣化检测（自动）      质量报告（自动）
```

---

## 6. 常见问题

### Q: 新增 Skill 后 check:counts 报错怎么办？

更新 `arkts-skills/skills/README.md` 中的数量声明，将 Domain Skills 数量 +1，并在架构图和分类表中添加新 Skill。

### Q: Agent 引用了一个还不存在的 Skill 怎么办？

先创建 Skill 目录和 SKILL.md，再提交 Agent。check:agents 会校验所有引用的 Skill 目录必须存在。

### Q: 如何判断新功能属于哪个能力类型？

| 你要做的事 | 应该用 |
|-----------|--------|
| 封装一个领域的专业知识和流程 | Skill |
| 编排多个 Skill 完成复杂任务 | Agent |
| 提供用户一键触发的快捷入口 | Command |
| 定义所有会话都应遵守的编码约束 | Rule |
| 沉淀可复用的结构化知识数据 | Knowledge Base |
| 提供项目/页面的起始结构 | Template |
| 封装外部工具为标准化 API | MCP Server |
| 在会话生命周期事件时自动执行 | Hook |

### Q: OpenCode 平台有什么不同？

当前 Skill/Agent 内容是平台无关的。如果 OpenCode 的工具名或格式与 Codex 不兼容，需要在 `.opencode/` 适配层中处理差异，或在 `arkts-skills-opencode/` 中维护平台专用版本。
