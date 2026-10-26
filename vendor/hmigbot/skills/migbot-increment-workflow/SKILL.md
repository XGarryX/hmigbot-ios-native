---
name: migbot-increment-workflow
description: Trigger: `$migbot-increment-workflow` or natural language. 管理 Migbot-Increment(AI native workflow) 工作流，执行 PLANNING → IMPLEMENTING → APPLYING
---

> Codex skill (converted from the `migbot-increment-workflow` slash command). Invoke with `$migbot-increment-workflow`, or pick it in `/skills` (the default_prompt below auto-runs). Codex has no custom slash commands, so the `$` prefix replaces `/`.


按照 Migbot-Increment 工作流程提出changes：根据工作流程步骤创建变更并生成所有产物。

按照 migbot-increment 工作流程创建变更，并生成产物：
- **PLANNING**：需求分析（不考虑现有解决方案和代码实现）和系统设计（软件设计）。
- **IMPLEMENTING**：任务分解。
- **APPLYING**：代码生成。

当所有阶段完成后，即可对变更进行归档。

---

## 输入

`$migbot-increment-workflow` 后面的参数是一个动作和变更名称，或者是用户想要构建的描述。

## 步骤

### 步骤 0：初始化检查（首次使用必须）

**触发条件**：首次使用或 `specs/initialized.flag` 不存在

检查 `specs/initialized.flag` 是否存在：

**如果不存在：**
```
## ⚠️ 初始化检查

检测到未初始化。在开始工作流之前，需要先进行环境检查和目录配置。

请先执行：$migbot-increment-init

$migbot-increment-init 将检查：
- 项目路径和编译环境
- 测试框架可用性
- 目录结构配置
- TEST_ROOT 路径
```

用户执行 `$migbot-increment-init` 完成初始化后，再继续。

**如果存在：** 继续步骤 1。

### 步骤 1：意图识别

收到用户输入后，首先将其意图分类为三种类型之一。

#### 意图 1：设计开发（Design/Development）

设计开发包括五个子意图：

| 子意图  | 类别 | 触发词举例 | 目录管理 |
|------|------|------------|----------|
| 新增功能 | New Requirement | `add`, `new`, `新增`, `增加`, `开发`, `我要`, `我想`, `需要`, `希望` | `./specs/changes/<YYYYMMDD>-requirement-add-<name>` |
| 功能变更 | Change Requirement | `change`, `变更`, `修改`, `改动`, `调整`, `优化` | `./specs/changes/<YYYYMMDD>-requirement-change-<name>` |
| 缺陷修复 | Bugfix | `fix`, `bugfix`, `修复`, `解决`, `bug`, `问题`, `错误` | `./specs/changes/<YYYYMMDD>-bugfix-<name>` |
| 架构优化 | Architecture Refactor | `重构`, `refactor`, `优化架构`, `架构调整`, `重写` | `./specs/changes/<YYYYMMDD>-arch-refactor-<name>` |
| 平台迁移 | Platform Migration | `migration`, `迁移`, `移植`, `跨平台`, `安卓转鸿蒙` | `./specs/changes/<YYYYMMDD>-platform-migration-<name>` |

如果识别为意图 1，则按照以下模板输出识别结果：

```
## Migbot-Increment Workflow: {type}-{name}

**Intent**: Design/Development - {New Requirement / Change Requirement / Bugfix / Architecture Refactor / Platform Migration}
**Category**: {需求类别}
**Directory**: specs/changes/{date}-{type}-{name}/

正在创建新变更目录...
正在启动 PLANNING 阶段...
```

**核心原则**：设计开发类任务必须按标准流程执行，对 changes 中已有内容不要改动。
1. **始终创建新的变更目录**
   - 不得检查或修改现有变更
   - 路径：根据步骤 1-0 中意图识别结果确定路径
   - 使用当日日期，不检查是否存在同名目录
2. **按照步骤 2：工作流程阶段 执行标准流程**
3. **每个阶段后询问用户确认**

#### 意图 2：继续任务（Continue Task）

**触发条件**：用户明确使用 `continue` 关键词：
- `$migbot-increment-workflow continue`
- `$migbot-increment-workflow continue <name>`
- 继续、继续执行、继续未完成的任务

如果识别为意图 2，则按照以下模板输出识别结果：
```
## Migbot-Increment Workflow: Continue - {name}

发现未完成的任务：
1. {date}-{type}-{name}: {phase}

请指定要继续的任务，或使用：
$migbot-increment-workflow continue <name>
```

**继续任务核心原则**：
**步骤**：
1. 检查 `specs/changes/` 子目录
2. 查找未完成的任务（没有 `archive-report.md` 的目录）
3. 如果提供名称，直接恢复该任务
4. 如果未提供名称，列出未完成任务供用户选择
5. 如果有多个未完成任务，询问用户选择哪个
6. 根据 `todo.md` 从最后一个未完成阶段恢复

#### 意图 3：其他（Other）

**触发条件**：无法明确分类为设计开发或继续任务。
**其他意图核心原则**：
- 直接跟随用户的指示执行。

---

### 步骤 2：工作流程阶段

#### 强制要求

**强制要求**：
1. **每个阶段必须使用对应的 skill** - 不得仅根据命令描述直接执行阶段步骤
2. **每个阶段后必须获得用户确认** - 在进入下一阶段前询问用户是否同意继续
3. **任何阶段都不允许给出默认假设** - 模糊或不确定的问题必须使用问答工具与人工进行交互

---

### 步骤 2-1 PLANNING 阶段（必须使用 migbot-increment-planning skill）

**强制要求**：
- 使用 `migbot-increment-planning` skill 加载并执行

**前置说明**：
- 意图分类已识别需求类别（新增功能/功能变更/缺陷修复/架构优化/平台迁移）

**步骤**：严格按照使用的 skill 中的步骤要求执行。

**完成后**：
1. 列出产出物：
   - `specs/changes/{date}-{type}-{name}/**.md`
   -
2. **使用以下问题询问用户审查产出物**：
   ```
   ## PLANNING 阶段产出物审查

   请审查以下产出物：
   - **.md（skill中要求的所有产出物）
   - proposal.md（需求提案）
   - delta-spec.md（需求规格说明）
   - ...

   是否同意继续到 IMPLEMENTING 阶段？
   - 同意：进入任务分解阶段
   - 不同意：请提出修改意见，我将等待您的指示
   ```
3. 如果用户同意：进入 IMPLEMENTING 阶段
4. 如果用户不同意：等待用户的修改指示

---

### 步骤 2-2 IMPLEMENTING 阶段（必须使用 migbot-increment-implementing skill）

**强制要求**：
- 使用 `migbot-increment-implementing` skill 加载并执行

**步骤**：严格按照使用的 skill 中的步骤顺序制定任务和执行任务。

**完成后**：
1. 列出产出物：
   - `specs/changes/{date}-{type}-{name}/todo.md`（已更新）
   - `specs/changes/{date}-{type}-{name}/tasks.md`
2. **使用以下问题询问用户审查产出物**：
   ```
   ## IMPLEMENTING 阶段产出物审查

   请审查以下产出物：
   - tasks.md（任务分解与排序）

   是否同意继续到 APPLYING 阶段？

   在进入 APPLYING 前，请确认：
   - [ ] 编译环境已就绪（hvigorw 可用）
   - [ ] 测试框架已配置（hvigorw test@entry 可用）
   - [ ] 项目可成功编译

   如环境未就绪，请在进入 APPLYING 前处理，或说明原因。

   选项：
   - 同意：进入代码应用与测试阶段
   - 不同意：请提出修改意见，我将等待您的指示
   ```
   3. 如果用户同意：进入 APPLYING 阶段
   4. 如果用户不同意：等待用户的修改指示

---

### 步骤 2-3 APPLYING 阶段（必须使用 migbot-increment-applying skill）

**强制要求**：
- 使用 `migbot-increment-applying` skill 加载并执行

**步骤**：严格按照使用的 skill 中的步骤顺序制定任务和执行任务。

**完成后**：
1. 列出产出物：
   - `specs/changes/{date}-{type}-{name}/todo.md`（已更新）
   - `specs/changes/{date}-{type}-{name}/apply-report.md`
2. **使用以下问题询问用户审查产出物**：
   ```
   ## APPLYING 阶段产出物审查

   请审查以下产出物：
   - apply-report.md（应用测试报告）

   是否同意完成任务？
   - 同意：进入步骤 3 生成打点文档
   - 不同意：请提出修改意见，我将等待您的指示
   ```

---

### 步骤 3：生成打点文档（必须执行）

**触发条件**：APPLYING 阶段产出物审查通过后立即执行，不可省略。

**文档路径与命名**：
- 路径：`docs/increment-report-phase-workflow-{date}-{type}-{name}.md`
- 示例：`docs/increment-report-phase-workflow-20260611-requirement-add-xxx.md`
- 其中 `{date}-{type}-{name}` 取自步骤 1 中识别出的变更目录名

**强制要求**：
1. 必须放置在项目根目录 `docs/` 下；如目录不存在则先创建
2. 文件名严格按上述命名规范，不得改动
3. 模板章节顺序、字段名不可改动
4. 报错信息无内容时填"无"，不可省略章节
5. "一句话需求"、"用户消息"、"上下文概要" 字段必须去隐私（移除真实人名、手机号、邮箱、身份证号、IP 地址、token/key 及内部专有客户信息，保留技术性描述）

**文档模板**（以下内容写入到上述路径）：

````markdown
# 增量报告 - workflow

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

**完成后**：进入步骤 4 上报增量阶段用量与产物。

---

### 步骤 4：上报增量阶段用量与产物（必须执行）

**触发条件**：步骤 3 打点文档写入完成后立即执行，不可省略。

本命令（workflow）作为**独立阶段**单独上报（不挂在 retrospect 的上报上；阶段位置由其真实起止时间决定，不强制排在 retrospect 之后）：

```bash
.migbot/bin/a2h mark-stage workflow
```

该命令会：
1. 标记 `migbot-increment-workflow` 阶段边界并写入 `workflow.done` sentinel；本阶段的 Token / 耗时 / Skill / Sub-agent 用量由原始遥测通道上报、服务端解析后汇入性能看板 5002 的「按阶段」与「事件时间轴」视图（按真实时间渲染成独立 bar）；
2. 步骤 3 生成的 `docs/increment-report-phase-workflow-*.md` 随原始遥测通道一并上报，服务端解析后归入同一 `migbot_session_id` 的导出包（无需单独上传）。

**【硬约束】**：
- 严禁用 Write / Edit 手工创建或伪造 `.migbot/metrics/` 下任何文件——所有上报产物必须由上述命令生成。
- 本步骤**不**重算迁移代码行数、**不**写入新的 HarmonyOS 总行，故不影响业务看板的翻译次数与覆盖率分母。
- 未授权（telemetry off）时命令自动静默跳过，失败也不阻断工作流。

**完成后**：本工作流结束，按 `## 输出` 章节展示完成状态。

---

## 输出

### 产出物路径格式
所有产出物必须创建在 `specs/changes/{YYYYMMDD}-{type}-{name}/` 目录下。各阶段产出物详情已在对应步骤章节的 **完成后** 中描述。

#### 状态输出：
```
## Migbot-Increment Workflow 状态

已完成：
- 20260419-requirement-change-playback-speed: COMPLETED

使用 `$migbot-increment-workflow continue <name>` 恢复任务。
```

#### 完成：
```
## Migbot-Increment Workflow 完成

**变更：** {date}-{type}-{name}
**Intent**: Design/Development - {New Requirement / Change Requirement / Bugfix / Architecture Refactor / Platform Migration}
**Category**: {需求类别}
**Location:** specs/changes/{date}-{type}-{name}/

所有阶段已成功完成！
```

---

## 产出物创建指南

### 目录结构检测
在执行 change 前，必须检测目录结构：
```
1. SPECS_FEATURE_ROOT: 按顺序检查
   - specs/specs/feat-{特性}/ *

2. CHANGES_ROOT: specs/changes/ *

3. Feat 目录: 列出 SPECS_FEATURE_ROOT 下所有 feat-{特性}
```

在 todo.md 中记录路径配置：
```markdown
## 路径配置
SPECS_FEATURE_ROOT: specs/specs
CHANGES_ROOT: specs/changes
```

### 产出物创建原则
1.  每个阶段完成后必须更新 `todo.md` 记录当前状态
2. 产出物内容必须与阶段要求一致，不可缺失关键章节
3. 产出物路径一旦确定，不得修改
4. 必须维护 `specs/changes/{date}-{type}-{name}/todo.md` 用于会话恢复


---

## 防护栏

### 强制执行要求
1. **必须使用对应 skill**：每个阶段必须加载并执行对应的 skill，不得仅根据命令描述直接执行步骤
2. **必须用户确认**：每个阶段结束后必须询问用户确认，用户同意后方可进入下一阶段
3. **不得修改已有内容**：设计开发类任务不得修改 `changes` 目录中已有内容
4. **必须使用 TodoWrite 工具跟踪进度**：首先必须把PLANNING-IMPLEMENTING-APPLYING三个基本步骤列出来，然后随着加载不同的skill，再补充其他具体的任务。

TodoWrite 示例：

```javascript
{
  todos: [
    { content: "Migbot-Increment Workflow 开始 - ***", status: "in_progress", priority: "high" },
    { content: "PLANNING - step1: ***", status: "pending", priority: "high" },
    { content: "PLANNING - step*: ***", status: "pending", priority: "high" },
    { content: "IMPLEMENTING - step1: ***", status: "pending", priority: "high" },
    { content: "IMPLEMENTING - step*: ***", status: "pending", priority: "high" },
    { content: "APPLYING - step1: ***", status: "pending", priority: "high" },
    { content: "APPLYING - step*: ***", status: "pending", priority: "high" },
  ]
}
```

### 禁止事项
1. **禁止提交密钥**：`build-profile.json5` 包含签名证书路径和密码，不得提交到版本库
2. **ResultSet 必须关闭**：使用 ResultSet 后必须在 `finally` 块中关闭

### 用户中断处理
当用户表达以下意思时，应立即停止并结束任务：
- "结束"、"完成"、"终止"
- "就这样吧"、"不需要继续了"
- 其他明确表示不再继续的表述

中断后必须：
1. **立即清除 TodoWrite 列表**：将 todos 设为空数组 `[]`
2. 更新 todo.md 标记当前阶段为 `cancelled` 或 `completed (partial)`
3. 输出清晰的完成/未完成摘要，让用户清楚知道任务终止时的工作状态
