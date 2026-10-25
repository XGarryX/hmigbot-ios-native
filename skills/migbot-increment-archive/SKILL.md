---
name: migbot-increment-archive
description: Trigger: `$migbot-increment-archive` or natural language. 归档 migbot-increment-workflow 完成的变更到 specs/archives/ 目录
---

> Codex skill (converted from the `migbot-increment-archive` slash command). Invoke with `$migbot-increment-archive`, or pick it in `/skills` (the default_prompt below auto-runs). Codex has no custom slash commands, so the `$` prefix replaces `/`.


归档变更，检查任务完成状态，将变更复制到归档目录。

---

## 输入

`$migbot-increment-archive` 后面为变更名称：

- `$migbot-increment-archive` — 未提供名称，列出所有未归档的变更供选择
- `$migbot-increment-archive 20260518-requirement-add-podcast-search` — 归档指定变更

---

## 步骤

### 步骤 1：识别变更

1. **解析输入**：
   - 如果提供名称 → 直接使用
   - 如果未提供 → 列出 `specs/changes/` 下所有未归档的变更目录

2. **验证变更目录存在**：
   - 存在 → 继续步骤 2
   - 不存在 → 提示用户变更目录不存在，结束

---

### 步骤 2：检查归档条件

读取 `specs/changes/{change_name}/todo.md`，检查：

| 检查项 | 说明 |
|--------|------|
| APPLYING 阶段 | 必须为 completed 状态 |
| apply-report.md | 必须存在 |
| 所有任务 | 必须为 completed 状态 |

**判断归档可行性**：

| 状态 | 处理方式 |
|------|----------|
| 任务全部完成 | 允许归档，继续步骤 3 |
| 任务未完成 | 提示用户哪些任务未完成，询问：1) 强制归档 2) 取消归档 |

---

### 步骤 3：加载 migbot-increment-archiving Skill

**强制要求**：必须使用 `migbot-increment-archiving` skill 加载并执行。

执行 `skill('migbot-increment-archiving')`，由 skill 负责：
1. 创建归档目标目录
2. 复制变更内容到归档目录
3. 验证复制完整性
4. 删除原始变更目录
5. 生成 archive-report.md

---

### 步骤 4：展示归档结果

```
## Migbot-Increment Archive 完成

**变更名称**: {change_name}
**归档路径**: specs/archives/{change_name}/
**包含文件**: proposal.md, delta-spec.md, delta-design.md, tasks.md, apply-report.md, archive-report.md
```

---

### 步骤 5：生成打点文档（必须执行）

**触发条件**：步骤 4 展示归档结果后立即执行，不可省略。

**文档路径与命名**：
- 路径：`docs/increment-report-phase-archive-{change_name}.md`
- 示例：`docs/increment-report-phase-archive-20260611-requirement-add-xxx.md`
- 其中 `{change_name}` 取自步骤 1 中识别的变更目录名

**强制要求**：
1. 必须放置在项目根目录 `docs/` 下；如目录不存在则先创建
2. 文件名严格按上述命名规范，不得改动
3. 模板章节顺序、字段名不可改动
4. 报错信息无内容时填"无"，不可省略章节
5. "一句话需求"、"用户消息"、"上下文概要" 字段必须去隐私（移除真实人名、手机号、邮箱、身份证号、IP 地址、token/key 及内部专有客户信息，保留技术性描述）

**文档模板**（以下内容写入到上述路径）：

````markdown
# 增量报告 - archive

## 1 项目简介
- 一句话需求：{去隐私后的一句话需求描述}
- 项目规模：{变更涉及的模块/文件数量}
- 执行耗时：{从 session 时间戳精确计算，如"32分15秒"；无法获取则填"N/A"}
- 消耗token：N/A（token消耗需要hook调接口抓取）
- 开发代码量：{新增/修改的代码行数估算}

## 2 用户中断
- 用户消息：{去隐私后的用户中断相关消息，无则填"无"}
- 上下文概要：{中断发生时的阶段和任务概要，无则填"无"}

## 3 报错信息
- 报错信息：{具体的报错信息}
- 上下文概要：{报错发生时的操作和阶段}
- 解决方案：{最终如何解决的}
- 出错次数：{该类错误的重复出现次数}
````

**字段记录规则**：
- 执行耗时：必须从 session 时间戳精确计算；无法获取时填 `N/A`，不可估算
- 消耗token：固定填 `N/A（token消耗需要hook调接口抓取）`
- 报错信息记录范围：包含系统级报错（编译失败、工具调用失败、测试失败等）和用户反馈报错（用户在对话中明确指出的"不对"、"功能没实现"、"行为异常"等）。如有多条，重复"3 报错信息"字段结构记录；如无任何报错，整段字段值填"无"
- 用户中断记录范围：用户在执行期间表达终止意图（"结束"、"完成"、"终止"、"不需要继续了"等）的相关消息及当时上下文

**完成后**：进入步骤 6 上报增量阶段用量与产物。

---

### 步骤 6：上报增量阶段用量与产物（必须执行）

**触发条件**：步骤 5 打点文档写入完成后立即执行，不可省略。

本命令（archive）作为**独立阶段**单独上报（不挂在 retrospect 的上报上；阶段位置由其真实起止时间决定，不强制排在 retrospect 之后）：

```bash
.migbot/bin/a2h mark-stage archive
```

该命令会：
1. 标记 `migbot-increment-archive` 阶段边界并写入 `archive.done` sentinel；本阶段的 Token / 耗时 / Skill / Sub-agent 用量由原始遥测通道上报、服务端解析后汇入性能看板 5002 的「按阶段」与「事件时间轴」视图（按真实时间渲染成独立 bar）；
2. 步骤 5 生成的 `docs/increment-report-phase-archive-*.md` 随原始遥测通道一并上报，服务端解析后归入同一 `migbot_session_id` 的导出包（无需单独上传）。

**【硬约束】**：
- 严禁用 Write / Edit 手工创建或伪造 `.migbot/metrics/` 下任何文件——所有上报产物必须由上述命令生成。
- 本步骤**不**重算迁移代码行数、**不**写入新的 HarmonyOS 总行，故不影响业务看板的翻译次数与覆盖率分母。
- 未授权（telemetry off）时命令自动静默跳过，失败也不阻断归档流程。

**完成后**：进入步骤 7 Git Merge 推荐。

---

### 步骤 7：Git Merge 推荐（可选）

归档完成后，如当前不在 main 分支且 `git_branch_adopted: true`：

向用户推荐：「归档已完成，建议将分支合并到 main。选择方式：1) 直接合并 2) 创建 PR 3) 跳过」

- 直接合并：
  ```bash
  git checkout main
  git pull origin main
  git merge feat/{YYYYMMDD}-{type}-{name} --no-ff
  git push origin main
  git branch -d feat/{YYYYMMDD}-{type}-{name}
  git push origin --delete feat/{YYYYMMDD}-{type}-{name}
  ```
- 创建 PR：
  ```bash
  gh pr create --title "feat({name}): {简要描述}" --body "变更目录: specs/archives/{change_name}"
  ```
- 跳过 → 告知用户分支已就绪，可随时合并

---

## 产出物

| 产出物 | 路径 |
|--------|------|
| 归档目录 | `specs/archives/{change_name}/` |
| 归档报告 | `specs/archives/{change_name}/archive-report.md` |

---

## 防护栏

### 强制执行要求
1. **必须使用 migbot-increment-archiving skill**：不得仅根据命令描述直接执行归档步骤
2. **必须使用 TodoWrite 工具跟踪进度**

### 禁止事项
1. **禁止删除未完成的变更**：除非用户明确要求强制归档
2. **禁止跳过完整性检查**：即使用户要求强制归档，也必须先执行检查
3. **禁止手动文件操作**：尽量使用命令行工具进行复制/删除

### 错误处理
| 错误场景 | 处理方式 |
|----------|----------|
| 变更目录不存在 | 提示用户检查输入的变更名称 |
| 复制失败 | 保留原目录，提示错误信息 |
| 删除原目录失败 | 保留原目录，报告归档不完整 |
| 归档目标已存在 | 提示用户归档已存在，询问是否覆盖 |

### 用户中断处理
当用户表达终止意图时：
1. 清除 TodoWrite 列表
2. 输出已完成/未完成的摘要
