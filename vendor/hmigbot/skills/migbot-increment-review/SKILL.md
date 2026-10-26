---
name: migbot-increment-review
description: Trigger: `$migbot-increment-review` or natural language. 审阅 SDD / Spec 类 Markdown 文档，输出优化稿
---

> Codex skill (converted from the `migbot-increment-review` slash command). Invoke with `$migbot-increment-review`, or pick it in `/skills` (the default_prompt below auto-runs). Codex has no custom slash commands, so the `$` prefix replaces `/`.


审阅 Markdown 文档（spec、arch、design、proposal 等），先判断文档类型，再输出更贴近原意的优化稿。

---

## 输入

`$migbot-increment-review` 后面为文档路径或审阅描述：

- `$migbot-increment-review specs/changes/xxx/delta-spec.md` — 审阅指定文件
- `$migbot-increment-review specs/specs/feat-xxx/` — 审阅目录下所有文档
- `$migbot-increment-review 审阅 xxx 项目的架构设计` — 描述性审阅

---

## 步骤

### 步骤 1：识别审阅对象

1. **解析输入**：
   - 如果是文件路径，读取文件内容
   - 如果是描述，在当前项目中查找匹配文档供用户选择

2. **识别文档类型**（按以下优先级）：
   - `delta-spec.md` / `spec.md` → spec 类型
   - `new-arch.md` / `arch.md` → arch 类型
   - `delta-design.md` / `design.md` → design 类型
   - `proposal.md` → proposal 类型
   - `rq-parse` 产物 → rq-parse 类型
   - `rq-clarify` 产物 → rq-clarify 类型
   - `rq-codebase` 产物 → rq-codebase 类型
   - 其他 → 根据内容判断

3. **输出识别结果**：
   ```
   ## Migbot-Increment Review: {文档路径}

   **文档类型**: {spec / arch / design / proposal / ...}
   **文档路径**: {path}

   正在加载审阅流程...
   ```

---

### 步骤 2：加载 migbot-increment-reviewing Skill

**强制要求**：必须使用 `migbot-increment-reviewing` skill 加载并执行。

执行 `skill('migbot-increment-reviewing')`，由 skill 负责：
1. 加载对应类型的审阅模板和检查清单
2. 执行默认轻量模式或 audit mode
3. 生成优化稿

---

### 步骤 3：输出审阅结果

1. **输出审阅摘要**：
   ```
   ## 审阅摘要

   **文档类型**: {type}
   **检测缺陷**: {N} 个（D1-D8 维度）
   **优化稿已生成**: {path}
   ```

2. **文件处理决策**：
   - 如果目标文件已存在，询问用户：
     ```
     目标文件已存在：
     - 覆盖原文件
     - 保存为 `{原文件名}.reviewed.md`
     - 取消审阅
     ```
   - 如果目标文件不存在，直接写入优化稿

3. **用户确认后写入文件**

---

### 步骤 4：生成打点文档（必须执行）

**触发条件**：步骤 3 写入优化稿后立即执行，不可省略。

**文档路径与命名**：
- 路径：`docs/increment-report-phase-review-{被审阅文档名或描述短名}.md`
- 示例：`docs/increment-report-phase-review-delta-spec.md`
- `{...}` 取被审阅文档的去路径文件名（或描述性审阅时的简短英文/拼音短名）

**强制要求**：
1. 必须放置在项目根目录 `docs/` 下；如目录不存在则先创建
2. 文件名严格按上述命名规范，不得改动
3. 模板章节顺序、字段名不可改动
4. 报错信息无内容时填"无"，不可省略章节
5. "一句话需求"、"用户消息"、"上下文概要" 字段必须去隐私（移除真实人名、手机号、邮箱、身份证号、IP 地址、token/key 及内部专有客户信息，保留技术性描述）
6. **本打点文档是本阶段唯一上传的产物——绝不上传被审阅/改写的源文档本身**（其可能含源码或隐私）

**文档模板**（以下内容写入到上述路径）：

````markdown
# 增量报告 - review

## 1 项目简介
- 一句话需求：{去隐私后的一句话需求/审阅目标描述}
- 项目规模：{被审阅文档数量/类型}
- 执行耗时：{从 session 时间戳精确计算，如"32分15秒"；无法获取则填"N/A"}
- 消耗token：N/A（token消耗需要hook调接口抓取）
- 开发代码量：N/A（review 不产生代码）

## 2 用户中断
- 用户消息：{去隐私后的用户中断相关消息，无则填"无"}
- 上下文概要：{中断发生时的阶段和任务概要，无则填"无"}

## 3 报错信息
- 报错信息：{具体的报错信息，无则填"无"}
- 上下文概要：{报错发生时的操作和阶段}
- 解决方案：{最终如何解决的}
- 出错次数：{该类错误的重复出现次数}
````

**字段记录规则**：与 workflow/archive 打点文档一致（执行耗时必须从 session 时间戳精确计算或填 N/A；消耗token 固定填 N/A；报错/中断按结构记录，无则填"无"）。

**完成后**：进入步骤 5 上报增量阶段用量与产物。

---

### 步骤 5：上报增量阶段用量与产物（必须执行）

**触发条件**：步骤 4 打点文档写入完成后立即执行，不可省略。

本命令（review）作为**独立阶段**单独上报（阶段位置由其真实起止时间决定，不强制排在 retrospect 之后）：

```bash
.migbot/bin/a2h mark-stage review
```

该命令会：
1. 标记 `migbot-increment-review` 阶段边界并写入 `review.done` sentinel；本阶段的 Token / 耗时 / Skill / Sub-agent 用量由原始遥测通道上报、服务端解析后汇入性能看板 5002 的「按阶段」与「事件时间轴」视图（按真实时间渲染成独立 bar）；
2. 步骤 4 生成的 `docs/increment-report-phase-review-*.md` 随原始遥测通道一并上报（**不**上传被审阅/改写的源文档）。

**【硬约束】**：
- 严禁用 Write / Edit 手工创建或伪造 `.migbot/metrics/` 下任何文件——所有上报产物必须由上述命令生成。
- 本步骤**不**重算迁移代码行数、**不**写入新的 HarmonyOS 总行，故不影响业务看板的翻译次数与覆盖率分母。
- 未授权（telemetry off）时命令自动静默跳过，失败也不阻断审阅流程。

**完成后**：按 `## 输出` 章节展示完成状态。

---

## 输出

### 产出物

| 产出物 | 说明 |
|--------|------|
| 优化稿 | 默认覆盖原文件，或按用户选择保存 |

### 完成输出模板

```
## Migbot-Increment Review 完成

**文档类型**: {spec / arch / design / ...}
**检测缺陷**: {N} 个
**优化稿**: {path}

审阅完成！
```

---

## 模式选择说明

### 默认轻量模式（default concise）

- 加载 `references/concise-review-template.md`
- 加载 `references/concise-dimensions-guide.md`（D1-D8 缺陷检测）
- 加载 `references/doc-type-profiles.md`（仅当文档类型不明确）

输出包含：
1. 简短审阅摘要
2. 带 D 维度标签的关键问题（3-5 条）
3. 修复了已检测缺陷的优化稿

### 详细审计模式（audit mode）

只有用户明确要求以下内容时才进入：
- 完整审阅报告
- 评分表或加权分
- 完整问题清单
- 追溯矩阵或全链路追溯
- Critic 审查
- 跨需求规格、架构设计、详细设计的全链路审计

进入 audit mode 后加载：
- `references/audit-mode-guide.md`
- 对应类型的审计配置和检查清单

---

## 防护栏

### 强制执行要求
1. **必须使用 migbot-increment-reviewing skill**：不得仅根据命令描述直接执行审阅步骤
2. **必须使用 TodoWrite 工具跟踪进度**
3. **不得覆盖未备份的文件**：文件写入前必须确认用户选择

### 禁止事项
1. **不得捏造业务事实**：优化稿中只保留原文已有事实，补充内容必须标注来源
2. **不得删除核心内容**：除非原文明确冗余

### 用户中断处理
当用户表达终止意图时：
1. 清除 TodoWrite 列表
2. 输出已完成/未完成的摘要
