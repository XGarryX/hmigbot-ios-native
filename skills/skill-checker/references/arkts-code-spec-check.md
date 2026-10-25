<!-- when: 质量线检查含 ArkTS 代码的 skill 时跑（arkts-* domain/style、含 .ets/装饰器/@ohos API 示例） -->
<!-- topics: ArkTS 代码规范, harmony-docs 核验, V1/V2 装饰器, arkts-no-* 规则, 废弃 API, 代码质量 -->

# ArkTS 代码规范核验（P7 · harmony-docs MCP 驱动）

与**合规 / 质量并列的独立硬门类目**（不归入质量软建议）：核验 skill 里**教的 ArkTS 代码 / API / 装饰器是否符合 ArkTS 规范 + 当前 HarmonyOS 官方文档**。教错代码的 skill 最危险——会把幻觉 / 废弃 / 坏写法批量传播到下游产物，故 🔴 正确性 **等同 ERROR 挡 CI**。产出独立「代码规范」报告段。

## 何时跑

- **跑**：SKILL.md / references 含 ArkTS 代码块（` ```ts ` / ` ```ets ` / ` ```arkts `）、装饰器（`@Component*` / `@Local` …）、`@ohos.*` / `@kit.*` import、ArkUI 组件、`ohos.permission.*`。
- **N/A**：纯编排（pipeline，如 a2h-*）/ 纯工具 skill 无 ArkTS 代码 → 段标 `N/A：无 ArkTS 代码`。
- **SKIPPED（前置探测必做）**：harmony-docs 不可用（主线程 ToolSearch 无 `mcp__harmony-docs__*` **且** subagent 无 `harmony-docs-cli` skill）→ **静默跳过**，段标 `SKIPPED：harmony-docs 未配置`，**不阻断、不报错、不计入硬门**。配置方法见 [`harmony-docs-setup.md`](./harmony-docs-setup.md)（可让 模型照着自动配好）。

## 核验工具与协议（harmony-docs）

- 主线程：`mcp__harmony-docs__*`（`lookup_symbol` / `search_docs` / `read_doc` / `find_by_syscap` / `list_module_*`）。
- subagent：`harmony-docs-cli` skill（Bash 跑 query.py）。
- 协议：**3 漏斗 gate → 深查（lookup + read 全 md + ≥1 出处）→ 冲突以 doc 为准**。
- **出处铁律**：每条 finding 必带 harmony-docs 出处（doc 文件名 / symbol / since / syscap）；无出处不得判 🔴。skill 与 doc 冲突时**以 doc 为准**（skill 可能在传播幻觉——见 `docs/skills_optimization_615/3_core-skills-correction.md`：knowledge-verifier 曾杜撰规则 `arkts-no-ts-like-as`）。

## 检查项（逐类，对照 harmony-docs）

| # | 类别 | 查什么 | harmony-docs 入口 | 典型 🔴 |
|---|---|---|---|---|
| C1 | 装饰器 V1/V2 | 项目要求 V2 时出现废弃/混用 `@Component/@State/@Prop/@Link/@Observed/LazyForEach` | search_docs「状态管理」「装饰器」 | 教 V1 写法 / V1V2 混用编译错 |
| C2 | 类型转换 | `as T` 是唯一合法；禁 `<Type>x`、`as const` | search_docs「从TypeScript到ArkTS的适配规则」 | 教 `<Type>x` / 杜撰 rule id |
| C3 | 持久化观测 | 嵌套/集合 `@ObservedV2` 持久化必标 `@Type`；裸集合 `UIUtils.makeObserved` | search_docs「@Type」「14108」「makeObserved」 | 漏 `@Type` → 14108 静默失效 |
| C4 | ArkTS 限制规则 | `arkts-no-structural-typing` / `-no-untyped-obj-literals` / `-no-definite-assignment`(`!`) / `-no-utility-types`(Partial/Record) / `-no-func-expressions`(bind/apply/call) / `-limited-stdlib` / `-no-spread` / `-no-for-in` / `-no-enum-mixed-types` | search_docs 对应 rule 名 /「ArkTS语法约束」 | 示例用 `!` 断言 / `Partial<T>` / 无类型 obj literal |
| C5 | 废弃 API | 示例 API 是否 deprecated / since 不符（`request2` / Stepper / `@ohos.router` 若称当前） | lookup_symbol（看 since/deprecated 字段） | 教已删/废弃 API |
| C6 | 组件/API 存在性 | ArkUI 组件 / `@ohos.*` 方法/属性是否真实存在 + syscap + since | lookup_symbol / find_by_syscap | 杜撰组件/方法/属性 |
| C7 | 权限字符串 | `ohos.permission.*` 是否真实 + 是否需 ACL | search_docs「权限」 | 杜撰权限名 |

## 严重度 → 报告版优先级

- 🔴 **正确性**（教错/坏代码：编译失败或静默失效）→ **P0 必修**
- 🟡 **过时/缺口**（废弃 API / 漏必要 API，如持久化未提 `@Type`）→ **P1**
- ℹ️ **风格**（可用但非最佳/版本可更新）→ **P2**

## 「代码质量」报告段格式（融入总报告）

```
### 代码质量（ArkTS 规范 · harmony-docs 核验）
适用性：✅ 含 ArkTS 代码（扫描 X 块） ｜ 或 N/A 无 ArkTS 代码
🔴 a / 🟡 b / ℹ️ c

🔴 正确性（→ P0；会生成坏代码）
| 问题 | 证据(skill 位置) | harmony-docs 依据 | 修正 |
|---|---|---|---|
| 教 `<Type>x` 转换 | references/x.md:88 | 「as 是类型转换唯一语法，不支持 <type>」(从TypeScript到ArkTS的适配规则.md) | 改 `as T` |
🟡 过时/缺口 …（同表）
ℹ️ 风格 …（同表）

小结：🔴 任一非 0 → 该 skill 会生成坏代码，P0 必修；全 0 → 代码规范 ✓
```

## 衔接 skill-checker 主线

- **独立硬门类目**：与合规 / 质量并列（SKILL.md Step 3）；🔴 = 必修（等同 ERROR 挡 CI），🟡 应修，ℹ️ 建议。报告里「代码规范」段排在合规之后、质量之前。
- **单 skill 深审**：出一行 verdict + 🔴/🟡/ℹ️ 清单；🔴 进报告版 P0、🟡 进 P1、ℹ️ 进 P2。
- **批量体检**：脚本（quality_scan.py）判不了本类目（需 MCP）→ 批量阶段标「待单审核验」，仅在单审（增量/指定/Top-K）且 skill 含 ArkTS 代码时跑。
- **范围**：核验 skill 自身教的代码，不核业务代码（那是 arkts-knowledge-verifier 的职责）。
