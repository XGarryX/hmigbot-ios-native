---
name: skill-checker
description: "检查 Skills / Agents / Commands / Rules 的「合规性」（frontmatter、taxonomy、references、计数，决定能否过 CI） 与「质量」（description 路由力、body 五分类、tiered 架构、措辞遵从度 + ArkTS 代码规范 harmony-docs 核验，依据 v2 审视 checklist）。 当用户说\"检查新增的 skill / 是否合规 / 跑一下检查 / 看看有没有问题\"，或\"skill 体检 / 质量审视 / 瘦身分析 / 哪些 skill 该重构 / 批量检查所有 skill / token 太大\"，或刚创建或修改了 SKILL.md / Agent / Command / Rule 时触发。 不要用于：从零生成新 skill（用 skill-creator）、跑业务迁移流程（用 a2h-* skills）、纯应用代码审查。"
metadata:
  type: tool
  domain: engineering
  tags:
  - governance
  - compliance
  - validation
  - checker
---
# Skill Checker — 能力合规 + 代码规范 + 质量检查器

对新增/修改的 Skills、Agents、Commands、Rules，**默认跑三个并列类目并合并出一份报告**：

| 类目 | 查什么 | 结果 | 性质 |
|---|---|---|---|
| **合规**（Step 2） | frontmatter / taxonomy / references / 计数能否过 CI + 跨 skill 引用一致性 + domain skill 消费方注册 | ERROR / WARN | **硬门**（ERROR 挡 CI；引用/消费方为 WARN） |
| **代码规范**（Step 3，仅含 ArkTS 代码的 skill） | skill 教的 ArkTS 代码/API/装饰器是否符合规范 + 当前官方文档（harmony-docs 核验） | 🔴正确性 / 🟡过时 / ℹ️风格 | **硬门**（🔴 教坏代码 = 必挡，等同 ERROR） |
| **质量**（Step 4） | 路由力 / token 效率 / body 五分类 / 措辞遵从度 / 可移植性（跨项目+跨平台） | 🚩红旗 / ⚠️改进 + 健康分 | 建议，不挡 CI |

三类目并行，Step 5 统一报告，Step 6 分类目引导修复。**硬门 = 合规 ERROR + 代码规范 🔴**（两者清零才能合并/过 CI）；质量是软建议。代码规范仅对含 ArkTS 代码的 skill 跑，且 **harmony-docs MCP 未配置时静默跳过**（见 Step 3）。

## 检查依据

开始前先读取权威规范（随项目演进，勿凭记忆）：

**合规**：① [`references/development-and-release-guide.md`](references/development-and-release-guide.md)（开发规范 + CI 五项） ② [`references/skill-hub-guide.md`](references/skill-hub-guide.md)（分类/标签/manifest） ③ [`references/skill-taxonomy.yaml`](references/skill-taxonomy.yaml)（type/domain/style-set 合法枚举）
**代码规范**：④ [`references/arkts-code-spec-check.md`](references/arkts-code-spec-check.md)（ArkTS 7 类检查 + harmony-docs MCP 协议）+ harmony-docs 离线官方文档（MCP `mcp__harmony-docs__*` / subagent `harmony-docs-cli`；未配置见 [`references/harmony-docs-setup.md`](references/harmony-docs-setup.md)）
**质量**：⑤ [`references/quality-rubric.md`](references/quality-rubric.md)（v2 审视 checklist 的可执行蒸馏）

> ①②③⑤ 为 skill 自带副本（self-contained）；项目有更新版规范以根源文件为准并同步回这里。④ 依赖的 harmony-docs 是外部 MCP——**未配置则代码规范类目静默跳过，不报错**。

## 工作流程

### Step 1: 识别范围与粒度

确定查哪些目标、用哪种粒度：

| 粒度 | 触发 | targets | 质量维度做法 |
|---|---|---|---|
| **增量**（默认） | `git diff --name-only HEAD` + `--cached` 找改动文件 | 改动的能力文件 | `quality_scan.py --skill <每个>` + LLM 深审 |
| **批量体检** | 用户说"检查所有 skill / 全仓体检 / 哪些该重构" | 全部 skill | `quality_scan.py --all` 出热力图，LLM 只审 Top-K |
| **指定** | 用户点名某 skill | 该 skill | 同增量 |

无法判断时问用户："你新增或修改了哪些文件？"。目标文件类型：

| 文件模式 | 能力类型 |
|----------|----------|
| `*/SKILL.md`（任意 skill 目录） | Skill |
| `**/agents/*.md` | Agent |
| `**/commands/*.md` | Command |
| `**/rules/*.md` | Rule |

### Step 2: 合规维度检查（ERROR / WARN）

对每个目标文件，按能力类型执行对应清单。

#### Skill 检查清单

| # | 检查项 | 严重度 | 规则 |
|---|--------|--------|------|
| 1 | SKILL.md 存在 | ERROR | 目录下必须有 SKILL.md |
| 2 | frontmatter 格式 | ERROR | 首行为 `---`，有完整的 YAML frontmatter |
| 3 | name 字段 | ERROR | 非空，全局唯一 |
| 4 | description 字段 | ERROR | 非空 |
| 5 | type 字段 | ERROR | 非空，值在 `references/skill-taxonomy.yaml` 的 types 中 |
| 6 | domain 字段 | ERROR | 非空，值在 `references/skill-taxonomy.yaml` 的 domains 中 |
| 7 | style-set 字段 | ERROR | 当 type=style 时必填，值须在 taxonomy 中 |
| 8 | tags 字段 | WARN | 建议添加 tags 提升可搜索性 |
| 9 | references/ 完整性 | ERROR | SKILL.md 中引用的 `references/` 文件必须实际存在 |
| 10 | name 一致性 | ERROR | 如果同名 Skill 存在于其他平台集合中，name 必须完全一致 |
| 11 | 跨 skill 引用一致性 | WARN | 改了契约级事实（§号/步数/字段/计数）须联动改引用处；捞出出站强引用待人核（见 `references/checklist-quick-ref.md`「跨 skill 引用一致性」） |
| 12 | domain skill 消费方注册 | WARN | type=domain 须在 `a2h-plan/SKILL.md` §4「suggested_skills 标注规则」注册或被 agent 引用，否则主流水线不派发；pipeline/tool/Hub 豁免（见 `references/checklist-quick-ref.md`「domain skill 消费方注册」） |

#### Agent 检查清单

| # | 检查项 | 严重度 | 规则 |
|---|--------|--------|------|
| 1 | frontmatter 存在 | ERROR | 首行为 `---`，有完整 YAML frontmatter |
| 2 | name 字段 | ERROR | 非空 |
| 3 | description 字段 | ERROR | 非空 |
| 4 | skills 引用有效 | ERROR | frontmatter 中 skills 列表里的每个 Skill 目录必须存在于 skills 根目录下 |

#### Command / Rule 检查清单

| # | 检查项 | 严重度 | 规则 |
|---|--------|--------|------|
| 1 | 文件格式 | WARN | 应有清晰的标题和结构 |
| 2 | 内容完整 | WARN | 不应有 TODO/TBD 占位符 |

### Step 3: 代码规范检查（ArkTS · harmony-docs；硬门，仅含 ArkTS 代码的 skill）

**前置探测（必做，决定是否静默跳过）**：先确认 harmony-docs 可用——主线程 ToolSearch 能找到 `mcp__harmony-docs__*`，或 subagent 有 `harmony-docs-cli` skill。
- **未配置 / 不可用** → **静默跳过本步**：报告「代码规范」段标 `SKIPPED：harmony-docs 未配置`，**不阻断、不报错、不计入硬门**。（配置见 [`references/harmony-docs-setup.md`](references/harmony-docs-setup.md)，可让 模型照着自动配好）
- 可用 → 继续。

**适用性**：仅当 skill 含 ArkTS 代码（ts/ets 代码块、装饰器、`@ohos.*`、ArkUI 组件、`ohos.permission.*`）时跑；纯编排（a2h-*）/ 工具 skill → 标 `N/A：无 ArkTS 代码`。

**核验**：用 harmony-docs MCP（`mcp__harmony-docs__*`；subagent 用 `harmony-docs-cli`）按 [`references/arkts-code-spec-check.md`](references/arkts-code-spec-check.md) 核验 C1–C7（装饰器 V1/V2 · `as` 转换 · `@Type`/makeObserved · arkts-no-* · 废弃 API · 组件存在性 · 权限）。每条 finding **必带 harmony-docs 出处**，doc 与 skill 冲突 **以 doc 为准**（skill 可能在传播幻觉）。

**严重度（硬门）**：🔴 正确性（教坏代码 = 编译失败/静默失效）→ **必修，等同 ERROR 挡 CI**；🟡 过时/缺口 → 应修；ℹ️ 风格 → 建议。

### Step 4: 质量维度检查（🚩红旗 / ⚠️改进 + 健康分；软建议）

**必跑**。依据 [`references/quality-rubric.md`](references/quality-rubric.md)。

1. **确定性扫描**（零 LLM，秒级）：
   ```bash
   # scripts/quality_scan.py 在本 skill 目录下；--dir 指向被检 skills 根（含各 skill 子目录，默认当前目录、一级扫描、不递归）
   python3 scripts/quality_scan.py --dir <skills-root> --skill <name>   # 增量/指定
   python3 scripts/quality_scan.py --dir <skills-root> --all            # 批量体检 → 热力图
   python3 scripts/quality_scan.py --dir <skills-root> --all --filter 'a2h-*'  # 子集批量（如 a2h 流水线）
   ```
   得到脚本可判的红旗/改进 + 健康分（A–F）+ **P8 可移植性**（M1 项目特定候选 / M2 脚本跨平台）。`--json <path>` 可另存指标。
2. **LLM 深审**（仅增量/指定，或批量的 Top-K）：按 [`references/quality-scorecard.md`](references/quality-scorecard.md) 的「深审三判」补脚本未覆盖的语义项（规则定义见 quality-rubric.md）：
   - **B4** Core Rule 占比 —— 逐段标 Core / Background / Example / Template / Redundant，非 Core 应移 references。
   - **D6·D7** 路由三要素 + 与相邻 skill 区分 —— 构造一个高迷惑性 shadow-skill 验证不误触发。
   - **W2·W5** 负向是否配正向 / 单约束 —— 复合规则拆单约束。
   - **M1** 项目特定候选 —— 脚本捞出的业务域名/私有包名，确认是否该占位化（占位名 `com.example`/`*.example.*` 与基础设施域名已白名单排除，剩下的人工判）。
   - 产出 quality-scorecard.md 的两版：**呈现版**（§B 总结式·给人读）+ **报告版**（§C 问题罗列 + 优先级可实操清单·给执行/agent 用）；脚本盲区（如 `v6.x` 等项目特有版本噪音）人工补判。

> 批量体检时合规/代码规范由 CI / 单审兜底，报告以质量热力图为主；增量/指定时三类目等量呈现。

### Step 5: 合并报告（合规 + 代码规范 + 质量一起出）★

一份报告给三类目，**硬门在前、软建议在后**。**增量/指定**用 per-target 卡片，**批量**用热力图：

```
## 检查报告：<skill-name>（或 N 个文件）
合规：✗ 2 ERROR / 1 WARN  ｜  代码规范：🔴 1（含 ArkTS 代码）  ｜  质量：健康分 C（🚩2/⚠️3）
硬门（合规 ERROR + 代码规范 🔴）：✗ 未通过 —— 需修 3 项

### 合规（硬门 · 挡 CI）
ERROR  1. [skill-xxx] type 字段缺失 — frontmatter 未找到 type
WARN   1. [skill-xxx] tags 缺失 — 建议添加提升可搜索性

### 代码规范（硬门 · ArkTS · harmony-docs 核验；🔴 等同 ERROR）
适用性：✅ 含 ArkTS 代码 ｜ N/A 无 ArkTS 代码 ｜ SKIPPED harmony-docs 未配置
🔴 正确性（必修）
1. [C2] references/x.md:88 教 `<Type>x` → 改 `as T`（依据：从TypeScript到ArkTS的适配规则.md）
🟡 过时  1. [C5] 用已废弃 request2 → requestInStream（依据：lookup_symbol request2 = deprecated）

### 质量（软建议 · 不挡 CI；依据 quality-rubric）
🚩 红旗
1. [P4/F3] body 9.4k token 且大量内联模板 → 迁移 tiered
2. [P1/F8] 缺负向边界 → 易与 skill-yyy 误触发
⚠️ 改进  1. [P6/W1] 弱化词 12 处 → 收紧为祈使
⚠️ 改进  2. [P8/M2] scripts/foo.sh:12 用 `grep …\b` → `grep -w`（跨平台）
ℹ️       [P8/M1] 业务域名 dev-api.xxx.cn 候选 → LLM 确认是否占位化
↓ 优先级修复清单（对照 checklist「快速诊断流程 1–11」）

### 结论
- **硬门**（合规 ERROR + 代码规范 🔴）：✗ 未通过 → 先修 2 ERROR + 1 🔴 才能合并/过 CI
- 质量健康分：C —— 建议重构 body（可选，不挡 CI）
```

**批量体检**给 `quality_scan.py --all` 的热力图 + 聚合 + Top-K（质量），附一行合规摘要；**代码规范在批量阶段标「待单审核验」**（脚本判不了，需 MCP）。无任何问题则报告"合规全过 + 代码规范 ✓/N/A + 质量 A/B，无需动作"。

### Step 5.5: 报告留存（输出报告后必问）

报告在对话里输出后，**主动询问用户是否保存到本地，并要求其提供路径**：

> "报告已输出。是否保存到本地？如需保存，请提供目标路径（如 `docs/skill-quality/<skill>-report.md`）。"

- 用户**给出路径** → 用 Write 把**完整报告**落盘（增量/指定：呈现版 + 报告版；批量：热力图 + 聚合 + Top-K + 各 skill 报告版）；目标目录不存在则先建，写完回显最终路径。
- 用户**拒绝 / 不提供路径** → 不写盘，直接进 Step 6。
- **路径必须由用户显式提供**——不得自选默认路径直接写盘，也不得在用户未回应前预先落盘。

### Step 6: 引导修复（按类目分流）

| 类目 | 修复性质 | 默认方式 |
|---|---|---|
| 合规 ERROR/WARN | 补 frontmatter / 改枚举 / 创建缺失 ref（**低风险**） | 可**自动修复**：逐项改 + 展示 diff 确认；需判断的字段（type/domain）给推荐值待确认；修完重跑 |
| 代码规范 🔴/🟡 | 按 harmony-docs 出处改 skill 里的错代码/废弃 API（**硬门，必修**） | 逐条照 doc 修正 + diff 确认；🔴 未清不得视为通过 |
| 质量 🚩/⚠️ | 重构 body / 抽 references / 改措辞（**高风险**） | 默认**手动 + 逐条 diff 确认**；**不默认自动改**、**不挡 CI**，不为"过检查"做无谓重构（Better Prompts Hurt） |

**硬门优先**：合规 ERROR + 代码规范 🔴 必须清零，质量可延后。手动模式对每条给明确指令（改哪个文件、哪一行、改成什么），用户改完可再次触发检查。

### Step 7: 计数更新 + CI 验证

1. **计数**：核对 skills 根目录 README.md 数量声明与实际目录数；不符则报告差异（"声明 29，实际 30"），自动修复模式下更新。
2. **CI**：所有硬门（合规 ERROR + 代码规范 🔴）修复完成后建议运行——
   ```bash
   npm run ci                                          # 全量
   cd scripts/skill-hub && python hub.py --validate-only   # 仅 Skill Hub
   ```

## 常见修复示例

**缺少 type/domain 标签（合规）：**
```yaml
# 修复前
---
name: arkts-new-skill
description: 一句话描述
---

# 修复后
---
name: arkts-new-skill
description: 一句话描述
type: domain        # ← 根据 skill 内容推断
domain: ui          # ← 根据 skill 内容推断
---
```

**Agent 引用不存在的 Skill（合规）：**
```
ERROR: Agent a2h-worker 引用了 skill "arkts-nonexistent"，但该目录不存在。
修复: 确认 skill 名称是否拼写正确，或先创建该 Skill。
```

**缺负向边界（质量 P1/F8，最常见红旗）：**
```yaml
# 描述末尾补一句，切分相邻 skill，降误触发
description: >
  …（原能力 + 触发）…
  不要用于：<相似但不同的场景>（用 <正确 skill>）。
```

## 注意事项

- 推断 type/domain 时读 SKILL.md 完整内容，不要仅凭名称猜测；无法确定则列候选让用户选。
- 检查 name 唯一性需扫描 skills 根目录下所有同名目录；taxonomy 以 `references/skill-taxonomy.yaml` 为准，不硬编码枚举。
- 质量维度的 `quality_scan.py` 是确定性初筛，红旗末尾标注的 LLM 项（B4/D6/D7/W5）必须人工深审补全，勿只报脚本结果。
- 三类目结论分开陈述：**硬门 = 合规 ERROR + 代码规范 🔴（决定能否合并/过 CI）**，质量红旗/改进只是软建议，勿混淆强制力。
- 代码规范类目依赖 harmony-docs MCP：**未配置时静默跳过**（报告标 `SKIPPED`，不阻断、不报错、不计入硬门），不得因缺 MCP 而让整个检查失败。
