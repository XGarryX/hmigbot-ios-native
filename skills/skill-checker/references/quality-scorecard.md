<!-- when: 单 skill 质量深审时加载（Step 3 LLM 环节 / 增量·指定粒度 / 批量 Top-K） -->
<!-- topics: 深审, scorecard, body 五分类, 路由, shadow-skill, 健康分 -->

# 单 skill 质量深审 — 流程 + scorecard 模板

跑 `quality_scan.py --skill <name>` 拿到确定性红旗后，本文件指导补**脚本判不了的 3 类语义判断**，并产出**两版**：**呈现版**（§B，总结式问题说明 + 建议，给人读）+ **报告版**（§C，问题项罗列 + 优先级可实操修改，给执行 / agent 用）。配套 [`quality-rubric.md`](./quality-rubric.md)。

---

## A. 深审三判（LLM）

### A1. B4 — body 五分类（最核心，决定 token 是否花在刀刃上）

逐 `##` 段落标类，估 Core Rule 行占比：

| 类 | 判据 | 去向 |
|---|---|---|
| Core Rule | 命令式动词 / 决策点 / 输出格式 / gotcha / HARD-GATE | 留 body |
| Background | 解释"为什么"、原理、历史变更 | → `references/`，body 留 1 句 |
| Example | 输入输出对 / 调用示例 | 留 1 个最佳，其余 → `references/` |
| Template | jsonc schema / 伪代码 / 配置样板 | → `references/` 或 `templates/` |
| Redundant | body 他处已说 | 删 |

**做法**：列出每个 `##`/`###` 段 → 标类 → `Core 行 / 总行`。< 40% → 🚩（目标 ≥ 60%）。

### A2. D6/D7 — 路由

- **D6 三要素**：主要能力 + 触发条件 + 唯一标识符（库名/API/文件名/术语）是否齐全。
- **D7 shadow-skill**：在**同 domain** 找一个**最易混的兄弟 skill**，问"description 这句话能否把两者分开？"。不能 → 必须补负向边界 `不要用于：<兄弟场景>（用 <兄弟 skill>）`。
  - 找法：上下游链路上的相邻 skill（生产者 vs 消费者）、同前缀同领域 skill、功能词重叠的 skill。

### A3. W2/W5 — 措辞（脚本只数频次，语义靠这里）

- **W2** 每个负向段（禁止/不要/❌）是否**紧跟正向替代**；纯负向 → 改"先给唯一合法路径，再一句兜底否定"。
- **W5** 单条规则是否只含 1 约束；`Do X but only Y unless Z and W` → 拆多条。

---

## B. 呈现版（总结式 · 给人读）

> 单 skill **不止给一个字母**——按 P1–P6 逐维出 verdict，再区分「必修 vs 可接受」。
> 脚本的「快速分级 A–F」只作粗筛表头（纯计数、严重度盲、不分维度，勿当结论）。
> 每维 verdict：✓ 合格 ｜ ⚠️ 改进 ｜ 🚩 必修 ｜ ℹ️ 提示。

```
## 质量审视: <skill>
快速分级: <A–F>（粗筛）  body≈<tok>  desc≈<tok>  架构: <mono/tier/flat>(<n> ref)

### 维度 profile（脚本信号 + LLM 判定 合判）
| 维度 | verdict | 脚本信号 | LLM 判定（必填，脚本判不了） |
|---|---|---|---|
| P1 路由 | <v> | F2/F8/D3/D5 命中情况 | D6 三要素齐全？D7 最易混 shadow-skill=<X>，能否区分？ |
| P2 Body | <v> | F3/F4/F6/B1/B2 | **B4 Core Rule ≈ <%>**（Core/Bg/Ex/Tmpl/Redun 各占比）|
| P3 References | <v> | R1（ℹ️）/R3 | R2 有无索引 / R4 body-ref 重叠 |
| P4 架构 | <v> | A1 | A2 Level-3（模板/长 schema）是否误置进 body |
| P6 措辞 | <v> | W1/W4/W6/W7/W8/W10 | W2 负向是否配正向 / W5 有无复合规则 |
| P7 代码规范 | <v> | （脚本无；含 ArkTS 代码才跑） | C1–C7 harmony-docs 核验：装饰器V1/V2·`as`转换·`@Type`·arkts-no-*·废弃API·组件存在性·权限（🔴 进 P0）；无 ArkTS 代码=N/A |

### 严重度细分（关键——避免"同分不同病"）
- 🚩 必修（路由/正确性/遵从）: <F8 无边界 / F2 desc / B4<40% / W2 纯负向 …，没有则写"无">
- 🟡 可接受（编排器固有 size，Core% 健康即不强压）: <F3 body 大 / F6 代码块多 …>
- 一句结论: <例 "路由✓措辞✓，仅 size 类红旗且 Core 58% → 维持现状" ｜ "B4 32%+无边界 → 必须重构">

### 优先级修复（对照 checklist 快速诊断流程 1–11）
1. <最高性价比，通常 description 负向边界>
2. <body 逐段分类抽 references>
3. …
```

> 快速分级算法（rubric）：R≥5→F｜R3–4→D｜R1–2→C｜R0&W>2→B｜R0&W≤2→A（R/W 不含 ℹ️）。
> **它只回答"要不要排进深审队列"，不回答"病在哪、要不要改"——后者看上面的维度 profile + 严重度细分。**

---

## C. 报告版（可实操 · 给执行/agent 用）

> 把呈现版诊断**摊平成可执行工单**，深度对标 `docs/skills_optimization_615/1_a2h-pipeline-refactoring.md`：含 **A 修改项** + **B 执行顺序** + **C 验收门** 三段。
> 优先级：**P0 必修**（路由/正确性/遵从：F8/F2/A1/B4<40%/W2 + **代码 🔴 C2/C3/C4/C6**）> **P1 建议**（⚠️ 改进：W1/W6/W10/B1/B2/D5 + **代码 🟡 C5/C7**）> **P2 可选**（ℹ️ 提示：R1/W4/W5/W7/W8 + Core% 健康时的 size 类红旗）。

```
## <skill> 修改报告（报告版）

### A. 修改项（按优先级 P0>P1>P2）
| # | 优先级 | 维度 | 问题项 | 证据（file:位置） | 可实操修改 |
|---|---|---|---|---|---|
| 1 | P0 | P1 | 缺负向边界 | SKILL.md `description` | 末尾加「不要用于：<相似场景>（用 <skill>）」 |
| 2 | P1 | P2 | Core 35% / body 9k | §A(模板段)/§B(背景段) | §A→`templates/x.md`、§B→`references/y.md`，body 留指针 |
| 3 | P2 | P3 | x.md 缺注解 | references/x.md:1 | 顶部加 `<!-- when:… --><!-- topics:… -->` |
| — | 不 action | P2 | F3/F6 size | — | Core 健康、编排器固有 size，**不动** |

### B. 执行顺序（含依赖）
1. P0 路由边界（零风险、最高收益）→ 2. P1 结构抽离 → 3. P1 措辞 → 4. P2 注解。
> 依赖：若含「Critical 前置」项，须排在结构抽离之后（body 瘦身后 Critical 才稳定落前 20%）。

### C. 验收门
**量化目标**：body ≤ <N> tok ｜ Core ≥ 60% ｜ P0 必修红旗清零 ｜ size 红旗已 B4 判为 accept/重构。
**验收脚本**（改完逐条复核；SK=skills 根）：
\```bash
grep -q '不要用于' $SK/<skill>/SKILL.md && echo '✓#1 边界'
python3 $SK/skill-checker/scripts/quality_scan.py --dir $SK --skill <skill>   # 复核维度 verdict 回绿
\```
**核心 checklist**：
| 验收项 | 判据 | 方式 |
|---|---|---|
| P0 必修红旗清零 | quality_scan 🚩 中无 P0 类（F8/F2/A1） | 脚本 |
| body Core 下限 | body ≤ N tok 且 B4 Core ≥ 60% | 脚本+LLM |
| 指针无悬空 | 抽出的 references 链接都 test -f 命中 | 脚本 |
| gotchas 保留 | 关键 HARD-GATE / evidence 规则仍在 body | 人工 |

无 P0/P1 时：「无必修/建议项，仅 P2 可选 N 项；维持现状」。
```

按 A 表自上而下执行；每改完一项跑 `quality_scan.py --skill <name>` 复核，C 验收门全绿才算闭环。

---

## D. Worked example — ios-project-inspector（F，两版并列）

快速分级: `F（🚩5/⚠️3）` body≈9.2k tok  架构: mono(0 ref)

| 维度 | verdict | 脚本信号 | LLM 判定 |
|---|---|---|---|
| P1 路由 | 🚩 | F8 无负向边界 | D7：与上游 `ios-ui-analyzer` 高度可混（"产 fact-tree/关系树"两者都命中）→ 必补边界 |
| P2 Body | 🚩 | F3 9.2k / F6 代码块24 / F4 自我介绍≥2 | **B4 Core≈30%**（Bg≈30% §1.1+§6+§4+§3.5；Tmpl≈25% jsonc/伪代码；Ex≈15%）|
| P3 References | ✓ | 无（但因 monolithic 无 ref 可拆） | — |
| P4 架构 | 🚩 | A1 monolithic 0 ref | A2：6 phase 的 jsonc schema/伪代码全堆 body |
| P6 措辞 | ⚠️ | W8 末尾无重述 / W10 `(v6.x` 版本标 | 可验证性强（Phase 5 自检带验证法，范例）；但 v6.x 版本标贯穿段标 = 噪音 |

**严重度细分**：
- 🚩 必修：F8 无边界（路由）、B4 30%（body 全是 Bg/Tmpl）、A1 monolithic
- 🟡 可接受：无——此处 F3/F6 **不是**可接受 size，而是 B4 30% 的症状（Core 太少），属必修
- 结论：**真 bloat + 路由风险，必须重构**（与 a2h-spec「size 大但 Core 58%、维持现状」恰好相反）

**呈现版结论**：真 bloat + 路由风险，必须重构（目标 9.2k → ~3–3.5k tok、Core ≥ 60%）。

**报告版**（同一诊断，摊成 A 修改项 / B 执行顺序 / C 验收门）：

#### A. 修改项（P0×2 / P1×1 / P2×1）
| # | 优先级 | 维度 | 问题项 | 证据 | 可实操修改 |
|---|---|---|---|---|---|
| 1 | P0 | P1 | 缺负向边界，与 ios-ui-analyzer 可混 | SKILL.md `description` | 末尾加「不要用于：首次从 toolkit 产物生成 fact-tree（用 ios-ui-analyzer）；改 HMOS 现状（不读 ArkTS）」 |
| 2 | P0 | P2/P4 | Core 30% + monolithic + 9.2k + 自我介绍(F4) | §1.1/§6/§4/§3.5(背景) + Phase 2.5–4(jsonc schema) + §1 自我介绍 | 建 `references/`：背景→references/、schema→references/templates/、删自我介绍；body 留 phase 骨架+铁律+Phase5自检 |
| 3 | P1 | P6 | v6.x 版本标(29 处, W10) | 各 `### Phase …（v6.x …）` + §6 | 段标删 `(v6.x …)`，版本史只留 §6 表 |
| 4 | P2 | P6 | 末尾无 Remember（W8 已降 ℹ️） | SKILL.md 末尾 | 可选：加 `> Remember:` 重述 top-3 铁律 |

#### B. 执行顺序
1. #1 边界（零风险）→ 2. #2 大重构（最大收益：建 references + 抽背景/schema + 删自我介绍）→ 3. #3 删版本标 → 4. #4 可选 Remember。
> 依赖：#4 Remember 须在 #2 body 瘦身之后做。

#### C. 验收门
**量化目标**：body 9.2k→≤3.5k tok ｜ Core≥60% ｜ tiered（有 references/）｜ 负向边界✓ ｜ P0 红旗(F8/A1/F4)清零。

```bash
SK=arkts-skills/skills; F=$SK/ios-project-inspector/SKILL.md
grep -q '不要用于' $F && echo '✓#1 边界'
[ -d $SK/ios-project-inspector/references ] && echo '✓#2 tiered'
grep -qE '（v[0-9]' $F && echo '✗#3 残留版本标' || echo '✓#3'
python3 $SK/skill-checker/scripts/quality_scan.py --dir $SK --skill ios-project-inspector  # 复核：🚩 必修应清零
```

| 验收项 | 判据 | 方式 |
|---|---|---|
| P0 清零 | quality_scan 必修红旗(F8/A1/F4)消失 | 脚本 |
| Core 下限 | body≤3.5k 且 Core≥60% | 脚本+LLM |
| gotchas 保留 | Phase 5 自检表 / 铁律仍在 body | 人工 |

---

## E. 脚本盲区提醒（深审必补）

`quality_scan.py` 的 W10 修订标记现抓 `Q\d 修复 / 域 \d / 翻转后 / vs lite / 原 Stage / （v\d.\d`（含括号内版本标）。但其它项目可能有别的修订惯例（如 `[r3]` / `# 改版2` / `迭代-N`）仍漏抓。深审时按目标 skill 实际惯例人工补判；通用噪音可在脚本 `REVISION_TAG` 增补 pattern。
