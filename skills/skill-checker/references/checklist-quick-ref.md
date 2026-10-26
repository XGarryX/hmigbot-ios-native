<!-- when: 跑「合规线」检查时加载（frontmatter / taxonomy / references / 计数 / CI） -->
<!-- topics: 合规, frontmatter, taxonomy, CI 校验, 命名规范, README 计数 -->

# 合规检查速查表

本文件是检查规则的精简版，完整规范见项目根目录下的指南文件。

## Skill 必需 frontmatter 字段

```yaml
---
name: <skill-name>           # 必填，全局唯一，全小写 + 连字符
description: <一句话描述>      # 必填，非空
type: <type>                  # 必填，值来自 skill-taxonomy.yaml
domain: <domain>              # 必填，值来自 skill-taxonomy.yaml
style-set: <style-set>       # 条件必填：type=style 时
tags: [tag1, tag2]            # 可选，建议填写
---
```

## Agent 必需 frontmatter 字段

```yaml
---
name: <agent-name>            # 必填
description: <一句话描述>      # 必填
tools: Read, Glob, ...        # 必填，可用工具列表
skills: skill-a, skill-b      # 可选，逗号分隔，每个须对应 arkts-skills/skills/ 下的有效目录
model: opus                   # 可选
---
```

## Skill 命名规范

| 类型 | 前缀 | 示例 |
|------|------|------|
| Domain Skill | `arkts-` | arkts-data-layer |
| Pipeline Skill | `a2h-` | a2h-spec |
| 分析工具 | `iOS-` | ios-ui-analyzer |
| 风格 Skill | `arkts-` | arkts-ui-component |

## 目录结构要求

```
arkts-skills/skills/<skill-name>/
├── SKILL.md            # 必须存在
└── references/         # 如 SKILL.md 中引用了 references/ 则必须存在
    └── *.md            # SKILL.md 中引用的每个文件都必须存在
```

## CI 五项校验

| 脚本 | 检查内容 |
|------|----------|
| lint:skills | SKILL.md 格式、frontmatter 完整性 |
| check:refs | references/ 引用完整性 |
| check:agents | Agent 的 skills 字段引用有效性 |
| check:counts | README.md 数量声明与实际一致 |
| check:plugin | plugin.json 格式和版本一致性 |

## README 计数位置

文件: `arkts-skills/skills/README.md`

需要更新的声明模式：
- `N 个 Pipeline Skills`
- `N 个 Domain Skills`
- `N 个 Agent`

## 跨 skill 引用一致性（WARN）

改了契约级"事实"（章节号/步数/字段名/收尾名/数量），引用它的别处必须联动改——**跨 skill 强引用最危险**。检查时捞出本 skill 的所有出站强引用，标"待人工核对目标方是否同步"（脚本无法自动判定两侧是否一致）：

```bash
# 捞出本 skill 对外部 skill 章节/契约的强引用
grep -nE '§[0-9]+|[A-Za-z0-9-]+ +§|[0-9]+ ?个?步骤?' <skill>/SKILL.md <skill>/references/*.md
```

判定：列出的每条 `… §N` / 「N 步」若指向**别的 skill**，须人工确认目标方该编号/契约仍存在且语义一致；不一致 → WARN「引用漂移，需联动」。典型：a2h-plan 硬引用 a2h-execute §5e/§6/Slice 步数（execute 改了，plan 没跟 = 指向旧结构）。

## domain skill 消费方注册（WARN）

`type: domain` 的 skill 必须有消费方，否则主流水线（a2h-plan → a2h-execute）永不派发，成"孤儿 skill"：

```bash
# 该 domain skill 是否在 a2h-plan 的 suggested_skills 映射注册（§4「suggested_skills 标注规则」），或被任何 agent 引用
grep -n "<skill-name>" arkts-skills/skills/a2h-plan/SKILL.md
grep -rn "<skill-name>" arkts-skills/skills/*/agents/*.md
```

判定：两处都查不到 → WARN「未注册消费方，a2h-plan §4 不会标 suggested_skills，主流水线不派发」。豁免：`type` 为 pipeline / tool，或 Hub 类（被其它 skill 内部 `Skill()` 调用）——这些不进 §4 映射。
