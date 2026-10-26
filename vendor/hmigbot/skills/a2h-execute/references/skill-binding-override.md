<!-- when: 派发任一 subagent 前做 runtime 上下文检查 / 处理 skill 缺失降级 / 注入风格 skills 时加载 -->
<!-- topics: runtime 覆盖表, 风格 skills 注入, 只升级不降级, skill 不存在降级 -->
<!-- 分工: 本文件只管 runtime 行为(覆盖/注入/降级), 零映射条目; task→skill 映射数据的唯一权威 = a2h-plan references/skill-binding-rules.md -->

# Skill 绑定：runtime 覆盖 + 风格注入 + 降级

> 主路径（三层承载：Base/FV stanza → 4 步默认映射 → slice 文件 `suggested_skills+:` 增量）见 SKILL.md §8a；本文件是其覆盖 / 注入 / 降级细则。

## 1. 覆盖路径：runtime 上下文检查

在 subagent 启动前，a2h-execute 检查当前上下文，可能覆盖 plan 的建议：

| 检查条件 | 覆盖规则 | 原因 |
|---------|---------|------|
| Stage 1 页面转换 | 使用 `a2h-activity-converter` agent | converter agent 专门为页面级 UI 转换设计 |
| Stage 3 Step 3a 页面未转换且有 Android 源码 | 先触发 Phase A 按需数据准备，再调 converter | 必须有数据才能转换 |
| 上一个编译检查点 FAILED | 暂停执行，报告错误列表 | 阻断性检查点不继续后续 task |
| task 使用了不确定的 API | 追加 `arkts-knowledge-verifier` | 防止使用错误/废弃的 API |
| task 内容命中 a2h-plan `references/skill-binding-rules.md` 映射表关键词（动画/视频/媒体/下载/权限等）但 plan 未标 | 按该表追加对应 Domain Skill——**plan 漏标兜底，非第二映射源**（具体映射零复制，查表为准）；兜底触发即在迁移报告覆盖记录表标「plan 漏标：该 slice 文件 `suggested_skills+:` 应补」 | 主路径 = plan 期落字段；runtime 只兜漏网 |
| task 联调报错出现 `401` / `-500` / 签名错 / `Missing request attribute` / 响应 unwrap 失败 / 后端调不通 | 追加 `arkts-network-troubleshoot` | 网络层反向救火（error-lookup 反查 Phase + 修复模板） |
| task 跨多个领域 | 组合多个 skill 按顺序执行 | 单个 skill 无法覆盖所有需求 |
| plan 中 style_set != none | 追加对应风格集的全部 style skills | 风格 skills 提供团队规范约束，subagent 自动遵循 |

## 2. 风格 Skills 注入

读取 plan Context 中的 `Style` 字段（即 `style_set` 值）：

- `style_set = none` 或字段缺失 → 不注入任何风格 skills，subagent 仅使用 domain/codebase/tool skills
- `style_set != none`（例如 `wfhc-standard`）→ 执行以下逻辑：
  1. 扫描 skills 目录中 frontmatter `style-set` 值匹配的所有 SKILL.md
  2. 找到匹配的风格 skills → 追加到 subagent 的 skills 列表
  3. style_set 值在 skills 目录中找不到对应 skills → 发出 WARN 日志，回退到 `none`（不阻断执行）

风格 skills 对 `a2h-activity-converter`（Stage 1）和 `a2h-migration-worker`（Stage 2/3）均生效。注入时追加在 suggested_skills 之后。

## 3. 覆盖原则

**只升级不降级**：可从单 skill 升级为多 skill 组合、可追加验证类 skill（knowledge-verifier）；不能移除 plan 已建议的 skill（除非 skill 不存在需降级）。覆盖发生时记录原因到迁移报告的覆盖记录表。

## 4. Skill 不存在降级

plan 建议的 skill 不存在（用户可能未安装）时：
1. 将 task 描述与所有可用 skill 的 `description` 字段做语义匹配
2. 优先选择带 `tags: [migration]` 的 skill
3. 无匹配 → subagent 仅基于 prompt 中的上下文执行（无 skill 增强）
