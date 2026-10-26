---
name: migbot-increment-implementing
description: |
  Migbot-Increment IMPLEMENTING 阶段 skill，用于代码开发任务分解与规划。
  当用户说"执行 migbot-increment-implementing"、"开始开发xxx"、"任务分解"或类似表述时触发。
  本 skill 负责 IMPLEMENTING 阶段的所有工作：任务分解、任务排序、产出 tasks.md。
---

# migbot-increment-implementing Skill

## 概述

本 skill 实现 Migbot-Increment IMPLEMENTING 阶段，负责将设计文档分解为可执行的开发任务。

```
IMPLEMENTING 阶段流程：
step2-1（任务分解）→ step2-2（任务排序）→ step2-3（产出 tasks.md）
```

## 使用方法

```
执行 migbot-increment-implementing {类型}-{名称}
开始开发 {功能名称}
进行 {功能} 的任务分解
```

---

## 前置条件

进入 IMPLEMENTING 阶段前，确认以下条件已满足：
1. PLANNING 阶段已完成
2. `{CHANGES_ROOT}/{YYYYMMDD}-{类型}-{名称}/` 目录下存在设计制品（proposal.md、delta-design.md 等）

---

## 全局约束

### 1. TodoWrite 管理

**注意**：TodoWrite 由编排层 migbot-increment-workflow 统一管理，本 skill 不使用 TodoWrite 工具。

### 2. todo.md 文件同步

在每个 step 完成后，同步更新 `{CHANGES_ROOT}/{YYYYMMDD}-{类型}-{名称}/todo.md` 文件，记录当前进度。

### 3. 任务颗粒度

每个任务应该是最小可开发单元，确保：
- 任务可以在 1-2 小时内完成
- 任务有明确的验收标准
- 任务有明确的输入和输出

---

## step2-1：任务分解

### step2-1-1：阅读设计文档

1. 阅读 `{CHANGES_ROOT}/{YYYYMMDD}-{类型}-{名称}/delta-design.md`
2. 阅读 `{CHANGES_ROOT}/{YYYYMMDD}-{类型}-{名称}/proposal.md`
3. 理解需要开发的代码组件和模块

### step2-1-2：识别代码组件

根据 delta-design.md 中的模块设计，识别需要开发的代码组件：

1. **数据访问层组件**
   - DAO 类（FeedDao、FeedItemDao、QueueDao 等）
   - 数据库表结构变更

2. **业务逻辑层组件**
   - Service 类（PlaybackController、DownloadManager、FeedUpdateService 等）
   - ViewModel 类

3. **表现层组件**
   - Component 结构体
   - 页面组件

4. **基础设施组件**
   - EventBus 事件定义
   - 常量定义
   - 工具类

### step2-1-3：拆分为最小可开发任务

每个任务应该包含：
- **任务名称**：清晰描述要做什么
- **任务描述**：详细说明实现方式
- **涉及文件**：需要创建或修改的文件路径
- **依赖任务**：前置任务（无则为"无"）
- **验收标准**：如何验证任务完成

---

## step2-2：任务排序

### step2-2-1：确定任务依赖关系

分析任务之间的依赖关系：
- 哪些任务必须在前置任务完成后才能开始
- 哪些任务可以并行执行
- 哪些任务是关键路径上的任务

### step2-2-2：制定开发顺序

根据依赖关系制定开发顺序：
1. 基础设施任务优先（DAO、常量、工具类）
2. 核心业务逻辑次之（Service、ViewModel）
3. UI 表现层最后（Component、页面）

---

## step2-3：产出 tasks.md

在 `{CHANGES_ROOT}/{YYYYMMDD}-{类型}-{名称}/tasks.md` 中输出。

**参考模板**：`migbot-increment-implementing/templates/tasks-template.md`

### tasks.md 结构

```markdown
# {功能名称} 开发任务

## 任务概述

- 功能名称：{功能名称}
- 变更类型：{类型}
- 关联特性：feat-{特性}
- 开发阶段：{阶段描述}
- 预计任务数：{数量}

## 任务列表

### 阶段 1：基础设施

#### Task 1.1: {任务名称}
**描述**：{任务描述}
**涉及文件**：
- `{文件路径}`
**依赖任务**：无
**验收标准**：
- {标准 1}
- {标准 2}

#### Task 1.2: {任务名称}
...

### 阶段 2：核心功能

#### Task 2.1: {任务名称}
...

## 开发顺序

```
Task 1.1 → Task 1.2 → Task 2.1 → Task 2.2 → ... → 完成
```

## 验收计划

| 任务 | 验收方式 | 验收时间 |
|------|---------|----------|
| Task 1.1 | 代码审查 | {日期} |
| Task 2.1 | 单元测试 | {日期} |
```

---

## IMPLEMENTING 阶段完成

**完成条件**：tasks.md 中所有任务已分解完成

**完成动作**：
1. 更新 `{CHANGES_ROOT}/{YYYYMMDD}-{类型}-{名称}/todo.md` 中的任务状态（标记 IMPLEMENTING 完成）

**用户确认**：

```
## IMPLEMENTING 阶段完成

**产出物位置**：`{CHANGES_ROOT}/{YYYYMMDD}-{类型}-{名称}/tasks.md`

**任务列表**：
- Task 1.1: {任务名称}
- Task 1.2: {任务名称}
- Task 2.1: {任务名称}
...

**开发顺序**：
Task 1.1 → Task 1.2 → Task 2.1 → Task 2.2 → ... → 完成

**请确认**：
- 任务分解是否符合您的预期？
- 是否需要调整？

选项：
1. 接受，继续下一阶段
2. 调整（请说明需要调整的内容）
```

### 处理用户修改请求

如果用户在确认时要求调整：
1. 暂停继续执行
2. 听取并记录用户的调整需求
3. 重新分解或排序任务
4. 更新 tasks.md
5. 重新展示更新后的内容
6. 再次等待用户确认
7. 用户接受后继续执行下一阶段

**提示用户**：任务分解完成，可以进入applying阶段，进行代码开发


---

## 附录

### Skill 模板文件

模板文件位于 `migbot-increment-implementing/templates/` 目录：

| 模板文件 | 用途 |
|----------|------|
| `tasks-template.md` | 开发任务模板 |
| `todo-template.md` | 任务进度模板 |

