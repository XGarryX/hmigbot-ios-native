<!-- when: 跑「质量审视」线时加载（用户说体检/质量审视/瘦身/哪些 skill 该重构/批量检查） -->
<!-- topics: skill 质量, 路由, body 五分类, tiered 架构, 措辞遵从度, 红旗 -->

# Skill 质量审视 Rubric（v2 checklist 可执行蒸馏）

**用法**：质量线（≠ 合规线）。合规看 [`checklist-quick-ref.md`](./checklist-quick-ref.md)；质量看本文件。
- 批量体检：跑 `scripts/quality_scan.py --all`，只覆盖「检测=脚本」项 → 红旗热力图。
- 单 skill 深审：脚本指标 + 本文件「检测=LLM」项逐条判 → scorecard。

严重度：🚩 红旗（强烈建议重构）｜⚠️ 改进（应优化）｜ℹ️ 提示。
检测：`脚本`（确定性，可批量）｜`LLM`（需读懂语义）｜`半`（脚本初筛 + LLM 确认）。

---

## P1 Description（路由层）

| ID | 检查 | 阈值 / 判据 | 严重度 | 检测 |
|---|---|---|---|---|
| D1 | description 存在 | frontmatter 有非空 description | 🚩 缺失 | 脚本 |
| D2 | 长度下限 | ≥ 20 token（约 32 CJK 字） | 🚩 过短 | 脚本 |
| D3 | 长度上限 | ≤ 1024 字符（约 250 token） | ⚠️ 超长 | 脚本 |
| D4 | 负向边界 | 含 `不要用于 / 不适用 / Do NOT use` 子句 | 🚩 缺失 | 脚本 |
| D5 | 功能清单堆砌 | 顿号/逗号分隔项 ≤ 6；无"支持 A、B、C、D…"长列举 | ⚠️ 命中 | 脚本 |
| D6 | 路由三要素 | 主要能力 + 触发条件 + 唯一标识符（库名/API/格式/术语）齐全 | ⚠️ 缺项 | LLM |
| D7 | shadow-skill 区分 | 能与同 domain 相邻 skill 清晰区分（不靠泛词） | ⚠️ 不可分 | LLM |

修复指向：D4→补"不要用于…（用 X）"；D5→功能清单移 body；D6→补缺失要素。

---

## P2 Body 五分类（Core / Background / Example / Template / Redundant）

| ID | 检查 | 阈值 / 判据 | 严重度 | 检测 |
|---|---|---|---|---|
| B1 | body 体量 | > 5000 token 🚩；2000–5000 ⚠️ | 🚩/⚠️ | 脚本 |
| B2 | 完整代码块数 | > 3 ⚠️；> 6 🚩（Example/Template 过多） | ⚠️/🚩 | 脚本 |
| B3 | 自我介绍段 | `本 skill 是/用于/旨在` 或 `What this skill does` ≥ 2 段 | ⚠️ | 脚本 |
| B4 | Core Rule 占比 | 目标 ≥ 60%（实证基线 38.5%） | 🚩 < 40% | LLM |
| B5 | Background 误置 | "为什么/原理/背景"段是否该移 references | ⚠️ | LLM |
| B6 | Redundant | 同一规则在 body 多处重复 | ⚠️ | 半 |

修复指向：逐段标 Core/Background/Example/Template/Redundant → 非 Core 移 references，留指针。

---

## P3 References & Files

| ID | 检查 | 阈值 / 判据 | 严重度 | 检测 |
|---|---|---|---|---|
| R1 | 按需注解 | 每个 `references/*.md` 含 `when` + `topics`（或 frontmatter/HTML 注释等价） | ℹ️ 缺失（提示级，不计入健康分） | 脚本 |
| R2 | reference 索引 | SKILL.md 列出有哪些子文件 + 何时读 | ⚠️ 无索引 | 半 |
| R3 | 文件过小 | 单文件 ≥ 30 token（过小不值得拆） | ℹ️ | 脚本 |
| R4 | body-ref 重叠 | 同份内容同时在 body 和 reference | ⚠️ | 半 |
| R5 | 无差别加载 | reference 是否被无条件全量读入 | ℹ️ | LLM |

---

## P4 架构形态

| ID | 检查 | 阈值 / 判据 | 严重度 | 检测 |
|---|---|---|---|---|
| A1 | monolithic | 无 `references/` 子目录 且 body > 2000 token | 🚩 | 脚本 |
| A2 | 三级披露 | Level-3 内容（模板/示例/长 schema）是否塞在 Level-2 body | 🚩 | LLM |
| A3 | 子目录告知 | body 是否告诉 agent 子文件存在及何时读 | ⚠️ | 半 |

---

## P5 质量门（改造后验证，非静态检查）

| ID | 检查 | 判据 | 检测 |
|---|---|---|---|
| G1 | Faithfulness | core 规则完整无歧义；移出内容可被找到；不丢 gotchas | LLM/人工 |
| G2 | Task 实测 | 3–5 真实任务通过率 ≥ 改造前 | 人工/eval |

> P5 仅在**改造后**跑；静态体检不评分。

---

## P6 措辞质量（Core Rule 遵从度）

| ID | 检查 | 阈值 / 判据 | 严重度 | 检测 |
|---|---|---|---|---|
| W1 | 弱化词 | `建议/可以/尽量/最好/酌情/应该/you should/might/perhaps` 频次 > body 行数 × 5% | ⚠️ | 脚本 |
| W2 | 整段负向 | `禁止/不要/不得/don't` 段落无正向替代配对 | ⚠️ | 半 |
| W3 | 软偏好用负向 | 非硬边界却用 "Do NOT" 表达 | ⚠️ | LLM |
| W4 | 自证约束 | `确保…正确 / 保证…无误 / make sure…correct / ensure…runs` | ℹ️（提示级·不计入健康分） | 脚本 |
| W5 | 单约束 | 单条规则无 3+ 嵌套条件（"Do X but only Y unless Z and W"） | ℹ️（提示级） | LLM |
| W6 | 通用最佳实践 | `最佳实践 / 规范实现 / best practices / clean code / 写干净` | ⚠️ | 脚本 |
| W7 | 关键规则前置 | 前 20% 含 `<HARD-GATE>/关键约束/Critical/MUST` 区块 | ℹ️（提示级·短/工具 skill 常不适用） | 脚本 |
| W8 | 末尾重述 | body 长（> 2000 token）时末段含 `Remember/重申/再次` | ℹ️（提示级·短/工具 skill 常不适用） | 脚本 |
| W9 | 反默认 | 规则是否"模型默认做不到"的（删模型已会的） | ℹ️ | LLM |
| W10 | 修订标记噪音 | 正文/prompt 含 `Q\d 修复 / 域 \d / 翻转后 / vs lite / 原 Stage` | ⚠️ | 脚本 |

修复指向：W1→收紧祈使；W2/W3→先正后负；W4→删自证；W6→换项目特定规则；W7→加 Critical 区块；W10→移 commit/CHANGELOG。

---

## P7 ArkTS 代码规范（harmony-docs 核验 · 仅含 ArkTS 代码的 skill）

核验 skill 教的 ArkTS 代码/API/装饰器是否符合规范 + 当前官方文档。**这是与合规/质量并列的独立硬门类目（非质量软建议）：🔴 等同 ERROR 挡 CI；harmony-docs MCP 未配置则静默跳过**。检测 = **LLM + harmony-docs MCP**（脚本判不了）。完整 7 类检查项 + MCP 协议 + 报告格式见 [`arkts-code-spec-check.md`](./arkts-code-spec-check.md)。

| ID | 类别 | 严重度 |
|---|---|---|
| C1 | 装饰器 V1/V2（废弃/混用） | 🔴/⚠️ |
| C2 | 类型转换（`as T` 唯一合法，禁 `<Type>x`/`as const`） | 🔴 |
| C3 | 持久化 `@Type` / `makeObserved`（漏→14108 静默失效） | 🔴/🟡 |
| C4 | arkts-no-* 限制规则（`!` / Partial / 无类型 literal / spread / for-in …） | 🔴 |
| C5 | 废弃 API（request2 / Stepper / @ohos.router …） | 🟡 |
| C6 | 组件/API 存在性 + syscap + since | 🔴 |
| C7 | 权限字符串真实性 + ACL | 🟡 |

每条 finding **必带 harmony-docs 出处**；doc 与 skill 冲突以 doc 为准。🔴=正确性(→P0)｜🟡=过时/缺口(→P1)｜ℹ️=风格(→P2)。纯编排/工具 skill 无 ArkTS 代码 → N/A。

---

## P8 可移植性（跨项目 + 跨平台 · 质量软建议）

> 与 P1–P6 同属质量软建议（⚠️/🚩，不挡 CI）；列在 P7 后仅因编号顺延，**P7 才是独立的代码规范硬门**。判据是「超出写它的那个上下文仍可用」：M1 跨项目、M2 跨平台。

| ID | 检查 | 阈值 / 判据 | 严重度 | 检测 |
|---|---|---|---|---|
| M1 | 项目特定硬绑定 | desc/body/refs 含真实业务域名（非 `example.*`）、私有反向域名包名（非 `com.example`/`ohos.*`/`iOS.*` 白名单）、厂商/客户专名、私有签名方案（XXTEA 等） | ⚠️ | 半（脚本捞候选 + LLM 确认） |
| M2 | 脚本跨平台 | `scripts/*.{sh,py,ps1}` 含 GNU-only 写法（`grep…\b`/`sed -i`/`readlink -f`/`stat -c`/`date -d`）、平台专属命令（pbcopy/xclip）、写死绝对用户路径（`/Users/`·`/home/`·`C:\`） | 🚩 绝对路径 / ⚠️ 其余 | 脚本 |

修复指向：M1→例子用占位名（`com.example` / `vendor-A` / `dev-api.example.com`）、只留结构、加 `_note` 说明已抽象；M2→词边界用 `grep -w`、路径相对/参数化、避开 BSD/GNU 分歧命令。完整踩坑例见作者指南 §3.2 桶 2 / 桶 5。

> 脚本只**标候选**（M1 有误报）：占位名 `com.example` / `*.example.*` 与基础设施域名（huawei/github/gitee…）已白名单排除，其余由 LLM 深审确认是否真需占位化。M2 跳过注释行与 `re.compile(` 模式定义行以减误报。

---

## 红旗清单（16 条 → 触发即建议重构）

**结构**：F1 desc>200token｜F2 desc 缺失/<20token｜F3 body>5000token 且 monolithic｜F4 大量"What this skill does"自我介绍｜F5 同规则反复｜F6 >3 完整代码块｜F7 reference 总和>10000token 无差别加载｜F8 无负向边界｜F9 误触发率>20%（需 eval）

**措辞**：F10 大量弱化词｜F11 整段负向无正向｜F12 规则不可验证｜F13 单规则 3+ 嵌套条件｜F14 关键规则埋中部｜F15 自证约束｜F16 大量通用最佳实践

脚本可判：F1 F2 F3 F4 F6 F8 F10 F12(部分) F14 F15 F16｜需 LLM/eval：F5 F7 F9 F11 F13。

---

## 健康分（建议算法）

```
红旗(🚩) = R 个；改进(⚠️) = W 个
A: R=0 且 W≤2     B: R=0 且 W>2     C: R=1~2
D: R=3~4          F: R≥5
```

批量体检按「红旗数 降序、body token 降序」排名，Top-K（默认 5）推单 skill 深审。

---

## 与合规线的边界（勿混）

- 合规线（[`checklist-quick-ref.md`](./checklist-quick-ref.md)）：ERROR/WARN，挡 CI，改 frontmatter/refs/计数，低风险自动修。
- 质量线（本文件）：🚩/⚠️，不挡 CI，多为重构 body，**默认手动 + diff 确认，不默认自动改**。
