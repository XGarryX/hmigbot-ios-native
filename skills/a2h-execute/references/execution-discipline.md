# §1.1 执行铁律 — 决策来源与禁止交互

> 本文件是 a2h-execute SKILL.md §1.1 + §2 启动必读 的**完整执行规范**。SKILL.md 仅保留摘要 + 指针；执行到该步时 **MUST Read 本文件全文**。
> 三道闸协同：闸 1（本 HARD-GATE）+ 闸 2（`spec/decision-ledger.md`）+ 闸 3（项目指令文件决策段，由 a2h-spec Step C4.8b 同步）。
> 宿主别名 **`PROJECT_INSTRUCTIONS_FILE`**：Codex → 项目根 `AGENTS.md`；Codex → 项目根 `AGENTS.md`。下文统一用此别名；正确性不依赖宿主对该文件的自动注入，必须显式 Read。

## 启动必读

> 把 ledger 与项目指令文件强制拉进当前 skill 执行 context，

1. **`Read PROJECT_INSTRUCTIONS_FILE`**（按上述宿主别名解析，若存在）
   - 拉入闸 3 内容：决策段（C0–C17 类目 + "查表 / fail-fast 不追问" 规则）+ 通用行为准则
   - 验证含 marker `<!-- a2h-decision-snippet:start -->` / `<!-- a2h-decision-snippet:end -->`
   - 文件缺失 / marker 缺失 → WARN 写入 `spec/migration-report.md`「启动检查」段（提示 a2h-spec Step C4.8b 未跑或被删），**不阻断**

2. **`Read spec/decision-ledger.md` 顶部「决策索引」段 + D0**（若存在；**按需读，不整份吞**）
   - 默认只读：文件头 → `## D 编号决策` 之前（含「决策索引」速查表 + 状态 + D0 产出定位，约 30–50 行）。索引表已含每条 D-编号的**一行结论 + 类目**，足以建立全局决策感知。
   - **正文按需 grep**：执行某 Slice/页触及某类目时，再 `grep -A 12 "### D-0NN" spec/decision-ledger.md` 取该条完整正文（背景/候选/依据/影响）。**禁止无差别 Read 整份 234 行 ledger** —— 实测旧流程 26 个 agent 整份吞全文 × cache_read 是控制面膨胀主因之一；索引 + 按需 grep 降 ~80% 注入量、零决策内容丢失。
   - 若 ledger **无「决策索引」段**（旧产物 / a2h-spec 未重跑 C4.8）→ 回退整份 Read（兼容），并 WARN 提示重跑 a2h-spec 生成索引。
   - 验证 status 字段：必须为 `approved`（spec Gate C 与 plan Gate 均已审批）—— status 在文件头部，按需读已覆盖。
   - 文件缺失 → **阻断**：写 migration-report 提示 grill #1/#2 未跑，要求先回到 a2h-spec / a2h-plan
   - status ≠ `approved` → **阻断**：提示用户先完成审批

启动必读完成后，再自动读取 `spec/baseline/plans/` 下已审批的双计划文件（见 SKILL.md §2 表）。

## 执行铁律（HARD-GATE）

execute 阶段的歧义应在 a2h-spec / a2h-plan 的 grill 嵌入点已经清零。本阶段只负责**按决策推进**，不再交互式追问。

唯一事实源：**`spec/decision-ledger.md`**（D0 决策树根 + D-编号决策 + 运行期验证项 + 技术必做项 + Plan 待修订项 + spec 卫生检查结论）。

凡 execute 期遇到以下任一情形，**必先 grep `spec/decision-ledger.md` 对应类目**：
- 范围取舍 / 技术替代 / UX 行为差异 / 工程配置 / 数据策略 类判断
- 与 plan / spec 现有描述冲突
- 触发条件超出 plan 既定 task 范围
- 任何 SKILL.md 既有段落中写有「提示用户三选一」「除非用户指定 blocking」「要求人工补 plan」等交互动作

执行规则：
- ledger 命中 → 按之执行，**严禁询问用户**
- ledger 未命中 → fail-fast，把缺口写入 `spec/migration-report.md` 的「决策缺口」段（schema 见下），**严禁交互式追问**；阻断当前 Stage / Slice / Batch，由下一轮 grill 补齐
- ledger 与其他文档冲突 → **ledger 优先**
- Plan 待修订项段落 → 直接按本表覆盖 plan 原文，不再核对 plan 当前措辞

## 决策缺口段 schema（写入 spec/migration-report.md）

```markdown
## 决策缺口（execute 期未命中 ledger）

| 缺口 ID | 触发位置 | 类目候选(C0–C17 或 escape) | 现象 | 阻断范围 | 上报时间 |
|---------|---------|---------------------------|------|---------|---------|
| G-001 | Stage 3 Slice 5 Step 3c | C8 SDK 策略 | F005 涉及 X SDK，ledger 未定占位/降级策略 | Slice 5 后续步骤 | YYYY-MM-DD HH:mm |
```

每条缺口由回流到 spec/plan grill 的下一轮拷问，或经评审升级为 checklist 新类目。
