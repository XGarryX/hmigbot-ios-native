# Migration Decisions — {项目名}

> 由 grill-with-docs 拷问会话产出（{YYYY-MM-DD}）。
> **唯一事实源**：a2h-execute / a2h-verify 执行时以本文件为准；与 baseline 报告冲突处以本文件覆盖。
> 决策类目映射：C0–C17，详见 a2h-spec skill 的 `references/migration-decision-categories.md`。

---

## 决策索引（速查 · 维护规则）

> **D-编号一行结论速查**：grep 命中某类目后在此快速定位，无需通读全文；上下游 agent 优先读本段建立决策感知，再按需 grep 对应 D-编号取完整正文（背景/候选/依据/影响）。
> **维护规则**：每**新增 / supersede** 一条 D-编号，**同步在此表追加 / 更新一行**（grill 产出决策时一并维护，与下方「D 编号决策」区一一对应）。索引只放结论，正文仍在下方——不复制正文，避免漂移。

| D-编号 | 类目 | 一行结论（= 该 D 的「选定」） | 状态 |
|--------|------|------------------------------|------|
| D-001 | C_ | {选定一行} | approved |
| ... | | | |

---

## 生命周期（单文件全周期累积）

**本文件在项目全生命周期内持续累积，不为 V1 / V2 / bugfix / 增量功能 创建新文件**。

| 阶段 | 行为 |
|------|------|
| 初次 grill（a2h-spec 首次 Step C4.8） | 以本模板生成 `spec/decision-ledger.md`，写入 D0 + 初始 D-编号 |
| 增量 grill（V2 / bugfix / 增量功能 / 重跑 a2h-spec） | **append** 新 D-编号到同一文件，**不**新建另一份 ledger |
| 决策被推翻 | 原条目状态改 `superseded`（保留历史，不删除），新决策递增 D 编号继续追加 |
| Plan 待修订项段 | 每轮 grill 追加新条目；execute 消费后可标 `applied` |
| escape 段 | 累积所有跨周期 escape 候选，retrospect 评审后标 `evaluated / promoted-to-C__ / dropped` |

**为何单文件**：execute / verify 永远 grep 一个文件；历史决策的可追溯性需要在同一文件看到 supersession 链；类目 C0–C17 跨 V1/V2 不变。

**状态枚举**（每条 D-编号 + PD-编号 + escape + Plan 待修订项 共用）：

```
proposed          → 生成期铸 ID（PD-*，spec C4 HARD-DIV 行/execute 决策缺口）→ grill 呈卡
pending-approval  → user 实时确认后 → approved
approved          → 新决策推翻后    → superseded
rejected          → 终态（连带其 HARD-DIV 行 + 差异 AC 重新生成）
superseded        → 终态（不再变化）
```

---

## 状态

- 本轮 grill 时间：{YYYY-MM-DD HH:mm}
- 状态：`pending-approval` / `approved` / `superseded`
- 审批人：{用户}
- 上游 spec 版本：{commit hash 或 spec 生成时间戳}

---

## D0 产出定位（决策树根 · C0）

> 本节是后续所有 D-编号决策的"真/桩/砍"切分基准。**必填**。

**定位**：______（真机 Demo / MVP / 可上线产品 / 完整复刻 之一）

**核心流程**（必须真实跑通的功能 ID 列表）：
- F___：______
- F___：______

**留桩范围**：______
**直接砍掉范围**：______

---

## 待批决策（PD-*）

> **平台无对等 → 行为差异**的提议决策（spec C4 §实现映射 HARD-DIV 行就地铸 ID；execute 期决策缺口亦可入此段）。
> grill 议程由机械 `grep -h "PD-[A-Z0-9-]*"` 汇集本段 + features/*.md——**散文式升级（"需记入 ledger"无 ID）禁止存在**（lint_divergence R1 FAIL）。
> 批准后 status→approved（可保留 PD-ID 或升格 D-编号并在此留 supersession 链）；驳回→rejected，连带 HARD-DIV 行 + 差异 AC 重新生成。

### PD-{类目C编号}-{F编号}-{序号} {提议简称}
- **类目**：C_  {类目名}
- **平台约束**：{为何无 1:1 等价（引 契约列证据）}
- **提议替代**：{替代行为 Y（用户可观察表述）}
- **影响 AC**：supersedes: [F00x-ACnn, ...]　emits: [F00x-ACmm（决: 锚差异 AC）, ...]
- **status**：proposed / approved / rejected

---

## D 编号决策

> 每条对应一个具体决策实例。类目列指向 C0–C17。
>
> ⚠️ **策略决策 ≠ 免除装配义务**（两次实录：D-022 "fail-closed 可重试"被 execute 读成
> 不装 ApiClient；D-012 "显式失败禁止伪成功"被读成网络运行时未 hydrate 即抛——四症状
> 成片失效）。错误处理类策略必须写**作用域限定**：它约束的是**失败路径语义**（失败时
> 不许假装成功），不得外延为"未配置就拒绝服务"；行为基线 = iOS 侧可观察行为
> （未登录 token 空串照样发请求）。缺 行为影响/作用域限定 字段的策略类决策，
> Step C5 审批呈现时按缺陷阻断。

### D-001 {决策简称}
- **类目**：C_  {类目名}
- **背景**：（一段话，说明本项目在该类目下的具体实例是什么）
- **候选项**：
  - A. ______
  - B. ______
  - C. ______
- **选定**：A / B / C
- **依据**：HarmonyOS 文档链接 / iOS 源码证据 / "用户确认"
- **影响范围**：Slice _ / page_NNNN / Base-N
- **行为影响**：`不改变iOS可观察行为` / `改变`（改变时必须列受影响 AC：F00x-ACnn, ...）
- **作用域限定**（**策略类必填**——错误处理/安全/合规/日志类决策）：本决策约束 ______；**不得外延为** ______
- **类型**：`具体决策`

### D-002 {决策简称}
（同上结构）

---

## 运行期验证项

> spec 阶段无法定、运行期才知道的（如"API 是否需要某 header 由响应码定"）。给默认假设 + 验证触发条件。

### R-001 {验证项简称}
- **默认假设**：______
- **验证触发条件**：______（如：调用返回 401/403 时）
- **触发后动作**：______（如：补注入签名头并重试）
- **关联类目**：C_

---

## 技术必做项（确定性修复，非决策）

> 不是决策，但 execute 必须执行的确定性技术修复。来源：自动探测 + 旁路②a。

- **T-001**：______（如：`dev-api.xxx.com` 为明文 HTTP，HarmonyOS 默认禁止明文流量，须在 `module.json5` 配置 cleartext 白名单）
- **T-002**：______

---

## Plan 待修订项

> 本文件落地后，**a2h-plan 产出的 `feature-plan.md` / `ui-plan.md` 中与本决策冲突的部分**，列出位置 + 调整目标。a2h-execute 执行时按本表覆盖 plan 原文。

| 位置 | 现状 | 应按决策调整为 | 关联决策 |
|------|------|----------------|---------|
| feature-plan.md Slice _ Step 3c | 写「______」 | D-___：改为「______」 | D-___ |
| ... | | | |

---

## spec 卫生检查结论

> grill 前置闸的确定性交叉比对结果。**全部 PASS 才能进入 grill 拷问**。

| 检查项 | 结果 |
|--------|------|
| 是否存在多套 spec 树并存 | PASS / FAIL（{说明}） |
| feature 编号体系全仓一致 | PASS / FAIL |
| 文档之间 / 文档内部无自相矛盾 | PASS / FAIL |
| 文档声称完成度与代码现状一致 | PASS / FAIL |
| 计数类指标跨文档无漂移 | PASS / FAIL |
| 无残留已被推翻的描述 | PASS / FAIL |
| verify / brief 报告非过时 | PASS / FAIL |

FAIL 项处理：______

---

## escape 记录（grill 期未匹配 C0–C17 的不清晰点）

> 这些点本项目走 ad-hoc grill 解决并记录在下方 D-编号区；同时上报 retrospect 评审是否升级为新 C 类目。

| 描述 | 关联现象 | 本项目处理（指向 D-编号） | retrospect 评审状态 |
|------|---------|--------------------------|---------------------|
| ... | | | pending / evaluated / promoted-to-C__ / dropped |

---

## 审批记录

| 日期 | 阶段 | 审批结果 | 备注 |
|------|------|---------|------|
| {YYYY-MM-DD} | spec grill #1 后 | approved | |
| {YYYY-MM-DD} | plan grill #2 后 | approved | |
