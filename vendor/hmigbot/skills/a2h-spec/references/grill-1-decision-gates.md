# grill #1：spec 卫生闸 + 需求侧决策清零 + AGENTS.md 同步

> 本文件是 a2h-spec SKILL.md Step C4.7 / C4.8 / C4.8b 的**完整执行规范**。SKILL.md 仅保留摘要 + 指针；执行到对应步骤时 **MUST Read 本文件全文**。
> 三道闸定位：本流程承载**闸 1（grill #1 需求侧）**与**闸 3（AGENTS.md 同步）**；闸 2（grill #2 技术侧）在 a2h-plan。

## §C4.7: spec 卫生前置闸（HARD-GATE · grill #1 前置）

grill #1 之前必须先确保 spec 自身不矛盾，否则拷问基础就是错的。本步骤是**确定性交叉比对**，非 grill 题目：

| 检查项 | 检测手段 |
|--------|---------|
| 是否存在多套 spec 树并存、权威源不明 | 扫 `spec/` 下是否有 `optimized/` / `optimized_spec/` / `baseline/` 多树 |
| feature 编号体系是否全仓一致（同一 F-ID 同一含义） | 交叉比对 feature-index.md ↔ features/F-*.md ↔ 各报告中的 F-ID 含义 |
| 文档之间 / 文档内部是否自相矛盾（决策表 vs 正文） | 比对各阶段产出报告中重复表述的状态字段 |
| 文档声称完成度是否与代码现状一致 | 抽样核查 spec 声称 "已完成" 的功能对应 .ets 文件是否存在 + 非空壳 |
| 计数类指标（页面数 / 实体数 / 占位符数 / 完成度）跨文档是否漂移 | 跨文档比对同一指标的数值 |
| 是否残留已被推翻的描述（如废弃 API / 旧装饰器） | grep 全仓废弃符号清单 |
| verify / brief 报告是否过时 | 比对最新代码 commit 时间 vs 报告时间戳 |
| **（若 `data-chains/chain-auth.md` 存在）数据链路每层是否都有真实 owner** | 对 chain-auth §5.1 完备性总表**逐层**交叉核 `feature-index.md` / Base 任务集：把每层 owner（L0=feature-base/身份·L1=启动/隐私 feature·L2/L3=Base-3·L4–L6=auth feature·L7=下游 feature）解析到**真实存在**的 feature/Base；任一层解析不到（尤 **L1 隐私/启动**、L7 下游——横切链路最易漏主）= **FAIL**（RC1"横向链路散落纵向 feature 无人 own"的兜底闸；chain-auth 不存在的纯 UI 项目跳过本项）|

执行：
1. 逐项跑确定性检测
2. 全部 PASS → 进入 Step C4.8
3. 任一 FAIL → 阻断本 Phase，输出修复建议清单，要求先修文档/spec 再重跑本步骤

结论写入 `spec/decision-ledger.md` 的「spec 卫生检查结论」段。模板：`templates/decision-ledger-template.md`。

## §C4.7b: auth-chain 活性探针（probe · grill 前 · 前置就绪即无条件执行）

Step C4.7 卫生闸 PASS 后、grill #1 之前：`join` Phase C 开头已派发的 `$AUTH_PROBE_JOB`（派发点见 a2h-spec Step B-join 尾），把 auth 链路的推测**变实测**：PASS→uncertainties `resolved`；FAIL→收窄成带证据的问题（FAIL-设备=后端需放开鸿蒙设备识别口径 / FAIL-签名=密钥参数不对）。结果回写共享 `uncertainties[]`，供下游 grill #2 C17 **带 probe 实测证据**拷问（execute 因此保持无阻断）。

**严禁**在跑 probe 前产生任何对话式征询语（"要不要跑探针"、"是否现在验证"等）：前置（`chain-auth.md` + `dev_info.json`）齐备 → **直接跑**；缺失才分流建 `U-ENV`/`U-ACCOUNT` + 走 C15 后端环境问（产 grill 问题，而非征询）。

**运行形态（隔离子 agent · 循环并行 · 写在 join 串行）**：循环骨架见 `arkts-network-troubleshoot/references/probe-runbook.md`；轮数多、墙钟长，故在 Phase C 开头即派发隔离子 agent 与 C1–C4 **并行跑**（派发 prompt 含并行安全三约束，见 [subagent-prompts.md](../references/subagent-prompts.md) § auth-chain-probe），本步只 `join`。
- **join 后由主线程一次性落盘**：存 `chain-auth.golden.json` + 回填真值 + `uncertainties[]` append + RED→GREEN 重投影。子 agent 循环期只读、发现缓冲在返回值——**写全部串行于此，故并行无竞态**。
- **回填不产生 stale**：plan 扇给各 owner 的是 `data_chain_refs` 指针（不复制值），join 的回填自动传播给已生成的 spec。
- **降级**：不支持后台子 agent → 本步前台串行跑（功能等价，无并行 / context 隔离收益；串行无并发写）。

## §C4.8: grill #1 — 需求侧决策清零（HARD-GATE）

> 配套：`references/migration-decision-categories.md` C0–C17；`templates/decision-ledger-template.md`。

### 调用模式（严格）

Step C4.7 卫生闸 PASS 后，**立即直接调用 `grill-with-docs`**（或显式 invoke `/grill-with-docs`），传入需求侧类目（C0–C5、C12、C15–C16）。

**严禁**在调用前产生任何对话式征询语（"准备好了吗"、"是否需要 grill"等）。grill 自身就是交互式拷问流程，自己承担与用户的对话，PASS 后直接 invoke。

### 必问 vs 自答 分流（grill 内部规则）

grill 不允许模型对 🔴 类目自行填充，必须分流：

| 分流 | 适用类目 | 处理 |
|------|---------|------|
| **实时交互拷问**（grill 必须逐条问用户，模型不得自行猜测填充） | 🔴 类目：**C0 产出定位** / **C2 迁移范围** / **C5 dead code 取舍** / **C12 忠实复刻** / **C15 后端环境**（多 base_url 时）/ **C16 持久化迁移范围**；以及任何 escape 候选 / Step C4.7 卫生闸 FAIL 项 | 逐条问 → 用户答 → 写一条 ledger D 编号 → 下一条。**单条流式确认，不允许"批量填好再让用户审批"** |
| **PD-* 待批决策卡**（实时交互拷问类；议程 = 机械 grep，防散文式升级漏收） | 全部 `PD-*`（spec C4 §实现映射 HARD-DIV 行铸 ID + ledger「待批决策」段；`grep -h "PD-[A-Z0-9-]*" spec/baseline/features/*.md spec/decision-ledger.md` 汇集去重） | 每张卡呈现：被替代 Android 行为 / 平台约束（契约列证据）/ 提议替代 / supersedes 与 emits 的 AC 清单——**决策 + 其差异 AC 作为一个单元批复**。approve → status=approved；modify/reject → 该 HARD-DIV 行 + 差异 AC 重新生成后重呈。**grill 结束时 PD-* 不得残留 proposed**（Gate C 出口 `lint_divergence --gate` 强制） |
| **模型自答 + Step C5 摘要呈现**（user 整体 veto 权） | 🟢🔵🟡 类目：C1 增量路由（项目状态自动判）/ C3 设备形态（资源限定符探测）/ C4 横切能力（资源目录探测）/ C5 探测部分（dead code 识别）/ C15 base_url 单环境（自动取） | 模型自答 + 写 ledger 「事实」/「运行期验证」段 → Step C5 摘要列出"已自动决策"清单 → 用户审批时整体 veto |

**策略类决策的两个必填字段**（错误处理/安全/合规/日志，写 ledger D 编号时强制）：
`行为影响`（是否改变安卓可观察行为，改变必列受影响 AC）+ `作用域限定`（"本决策约束 X，
不得外延为 Y"句式）。这是防「策略被 execute 外延成架构级 fail-closed」的源头闸
（实录：D-012 "显式失败"→ 网络运行时未 hydrate 即抛，模板/登录/H5/点击四症状同源）。

**判断原则**：纯代码仓自动可得的事项（资源、组件、形态、变体目录等）模型自决；**涉及整体（产出/范围）、三方库与外部 API、UX 偏好、密钥/签名/工程配置、自相矛盾或完全不清晰的项 — 必须问用户**。

### grill 流程

```
加载 references/migration-decision-categories.md C0–C17 类目 + 必问/自答分组
  + 当前 spec 产物（ui-manifest.md / feature-index.md / features/）
  + 自动提取事实（api-inventory.json / AndroidManifest 已抽取项）
  ↓
正向：逐类目在本项目 spec 找实例
  - 实例不存在（如 Android 无 values-night） → 自动消解，跳过
  - 实例存在 + 🔴 类目 → 实时拷问
  - 实例存在 + 🟢🔵🟡 类目 → 模型自答，写「已自动决策」段
  ↓
反向：扫 spec 不清晰信号（TODO / [待对齐] / 待确认 / 占位 / 矛盾 / 低 confidence）
  - 能归 🔴 类目 → 实时拷问
  - 能归 🟢🔵🟡 类目 → 模型自答
  - 归不到任何类目 → escape，**必须实时拷问** + 标「新类目候选」记入 ledger escape 段
  ↓
全部结论写入 spec/decision-ledger.md：
  - D 编号决策（🔴 类目，用户答案）
  - 已自动决策段（🟢🔵🟡 类目，模型自答 + 来源依据）
  - 运行期验证项 / 技术必做项 / escape 段
```

### HARD-GATE 约束

- 本步骤产出的 ledger 必须含 **D0 产出定位**（C0 类目）—— D0 是后续所有决策的真桩切分基准，**缺失即阻断 Step C5**
- 所有 🔴 类目实例和 escape 项必须有 user 答复的 evidence，**严禁模型代答**
- **PD-* 待批决策清零**：grill 结束时全部 PD-* 须为 approved / rejected（无 proposed 残留）；Gate C 出口跑 `scripts/lint_divergence.py --gate` 强制（决: 锚指向 proposed 即 FAIL）
- Step C5 摘要必须分别列出"用户实时确认"和"已自动决策"两块，用户可对后者整体 veto

### Ledger 生命周期处理

- **首次跑（项目无 `spec/decision-ledger.md`）**：以 `templates/decision-ledger-template.md` 为骨架生成 ledger，写入 D0 + 初始 D-编号
- **后续跑（ledger 已存在，单文件全生命周期累积）**：
  - 仅 append 新 D-编号，不覆盖既有决策
  - 既有决策与当前 spec 冲突 → 原条目状态改 `superseded`，新决策递增编号
  - escape 段、已自动决策段、运行期验证项段 同样 append
  - V1 / V2 / bugfix / 增量功能 **共用同一个 ledger 文件**，不按版本拆分
  - 详细规则见 `templates/decision-ledger-template.md` 「生命周期」段

## §C4.8b: 同步项目 AGENTS.md（决策段 + HarmonyOS 知识查询优先级 + 通用基线，三道闸·闸 3 落地）

> 算法权威定义：[`templates/agents-md-decision-snippet.md`](../templates/agents-md-decision-snippet.md)「Idempotent 同步算法」节。

Step C4.8 ledger 产出后**必须**自动跑此子步骤，把**最多三段独立 marker 块**落到项目根 `AGENTS.md`：

1. **决策触发段**（`a2h-decision-snippet`，**始终同步**）— 迁移特定规则，HARD-GATE 级
2. **HarmonyOS 知识查询优先级段**（`a2h-harmonyos-dev-skill`，**条件同步**）— 当 `harmonyos-development` skill 在当前配置中可用时才写入；skill 不可用时**不写入**，已存在时**移除**
3. **通用行为准则**（`a2h-karpathy-baseline`，**始终同步**）— 迁移友好版 Karpathy（删 #1 Think Before Coding + #4 Goal-Driven Execution，保留 #2 Simplicity / #3 Surgical 并加迁移化 caveat）

各段独立 marker、独立同步、互不干扰。顺序：决策段 → harmonyos-dev-skill 段（如有） → Karpathy 段。

**同步算法**（权威定义 + 各段实体内容见 [`../templates/agents-md-decision-snippet.md`](../templates/agents-md-decision-snippet.md)「Idempotent 同步算法」节）：

- PRE-CHECK：`HMOS_DEV_SKILL_AVAILABLE` = Glob `**/harmonyos-development/SKILL.md` 命中非空
- 三段独立幂等同步：无 AGENTS.md → 创建骨架（created）；含 marker 且内容有差 → 替换（updated）；无 marker 且应同步 → 按顺序插入（appended）；条件段已存在但 skill 不可用 → 移除（updated）；全部最新 → 不写（unchanged）

**关键设计点**：
- **显式读取指令**：AGENTS.md 中写明「会话开始必须先读取 `spec/decision-ledger.md` 顶部『决策索引』段」（Codex 无 `@` import 自动加载，纯路径文本不保证被读取）
- **决策段在前 + 职责正交**：决策段管 C0–C17（"不问，按 ledger 走"），通用基线管代码量 / 修改边界 / 风格，互不重叠
- **intro 全中文**：自动创建的骨架 intro（项目名 / 源路径 / 技术栈 / baseline 路径 / ledger 引用）必须全中文，仅路径与文件名保留原文
- **删 Karpathy #1 与 #4**：#1 "unclear → ask" 与「禁止追问」冲突；#4 成功标准已内置于 execute / verify HARD-GATE

**不变式**（违反即视为 bug）：
- marker 范围**之外**的既有内容永远不动
- 各段 marker 互相独立，更新互不污染
- 反复跑结果一致（第二次同步走 updated / unchanged）
- 决策**内容**只在 ledger，AGENTS.md 只装**规则**

**输出**：在 Step C5 摘要中追加同步状态：

```
### AGENTS.md 同步（闸 3）
- 项目 AGENTS.md 路径: <PROJECT_ROOT>/AGENTS.md
- 决策段同步结果: created / appended / updated / unchanged
- harmonyos-dev-skill 段同步结果: created / appended / updated / unchanged / removed / not-applicable（skill 不可用）
- 通用基线段同步结果: created / appended / updated / unchanged
- harmonyos-development skill 检测: ✓ 可用（路径: ...） / ✗ 不可用
- ledger 引用方式: @spec/decision-ledger.md（按需加载）
```

> AGENTS.md 各段都是规则不是决策，按模板机械同步即可，**不触发用户审批**；规则演进时改 snippet 模板 + 重跑 Step C4.8。
