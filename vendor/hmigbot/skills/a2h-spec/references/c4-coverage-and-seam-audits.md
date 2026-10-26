<!-- when: Phase C 跑 Step C4.6b/c/d/e（源码侧覆盖审计 / stub 深挖 / 跨模块 seam 审计 / addenda 收口）时加载 -->
<!-- topics: 源码侧功能覆盖审计, ownership, skip-list, feature-coverage-auditor, source-coverage-report, stub 深挖, 跨模块 seam 审计, cross-module-contracts, addenda 元数据, consumed_by, parent, slug -->

# Step C4.6b / C4.6c / C4.6d / C4.6e 细则：覆盖审计 · stub 深挖 · seam 审计 · addenda 收口

> 这四步在 a2h-spec Phase C 主体生成（C4）+ UI 覆盖审计（C4.6）之后、spec 卫生闸（C4.7）之前执行。

## Step C4.6b: 源码侧功能覆盖审计（强制）

> **优先路径（colleague v6.5，当 `arkts-feature-coverage-auditor` 技能存在时）**：UI 覆盖率审计通过后，自动调用 [arkts-feature-coverage-auditor](../../arkts-feature-coverage-auditor/SKILL.md) 做**四层 feature 覆盖率审计**（确定性脚本 `scripts/compute_feature_coverage.py`，~1 秒）：
> - 输入：`$ANDROID_SRC` + `spec/baseline/{feature-index.md, features/F*.md, ui-manifest.md, api-inventory/*, ref/*}`；输出：`spec/feature-coverage-report.md` + `spec/feature-coverage-tasks.md`。
> - 通过阈值（分档）：≤30 features (strict) L1≥90% / L2=100% / L3=100% / L4_main≥95% / L4_aux≥80%；>30 features (lenient) L1≥85% / L2=100% / L3=100% / L4_main≥90% / L4_aux≥70%。
> - FAIL → 读 `feature-coverage-tasks.md` 缺口（P0=strong / P1=medium / P2=weak）→ 回 Step C2/C4 补 feature → 重跑（最多 2 轮，3 轮转 warning + 人工 override）。
> - 为什么：feature 拆分纯靠 LLM 判断无确定性兜底——实证 project1 35 features 漏 7 个真业务 domain（layer/clock/outline/tag/bookmark/multi_window/notesfilter）；确定性 domain 扫描把漏判暴露在 spec 阶段。
>
> **兜底路径（本技能内置，`arkts-feature-coverage-auditor` 缺席时执行）**：以下 ownership 审计是无外部依赖的等价兜底，且与 tier 分档 + Phase 0 跨模块审计（C4.6d）兼容。两条路径择一即可——有外部 auditor 用其四层审计，否则跑本节 ownership 审计。

C4.6 审计的是 **UI 侧**覆盖（页面有没有漏）；C4.6b 与之对称，审计 **源码侧**功能覆盖（源码包有没有「无主」——即不被任何 feature 锚定）。UI 审计无法发现无对应页面的纯引擎/算法/库子系统，必须由本步骤兜底。

1. 输入：Step C1 的「源码包普查清单」 + 所有 `spec/baseline/features/F*.md` 的 `android_source_anchors`（取并集，按包归并到文件级）。
2. 对每个普查包计算 `anchored 覆盖率 = (该包内被任一 feature 锚定的文件数) / (该包文件总数)`。
0. **自动胶水预分类（减少 FAIL churn）**：包路径/类名命中纯胶水启发式（`*ViewPager` / `*Util` / `*Helper` / `*ShadowBuilder` 等纯工具类，或位于 `diagnostic/` `adhoc/` `widget/` `expand/` 等无业务语义目录）→ 自动写入 skip-list（reason=`platform-glue`），不计入 FAIL。人工在 Gate C 复核 skip-list 即可。
3. 判定规则（审计 **ownership**——是否被某 feature 认领，而非统一深度；深度由 tier 分档 + Step C4.6c 按需保证）：

   | 情况 | 判定 | 处理 |
   |------|------|------|
   | 重要包（`file_count ≥ 3` 或 `loc ≥ 500`）无任何 feature 认领 | **FAIL** | 新建 feature **或并入已有**；小型纯引擎包可建为 `tier: peripheral` / `depth: stub` 轻量认领；确无业务语义则 skip-list |
   | 含专属类（命名约定 `*View` / `*Renderer` / `*Controller` / `*Manager` / `*Session`，`loc ≥ 150`）的文件未被任一 feature anchor | **FAIL** | 须被某 feature anchor（ownership）；归入 stub feature 时其 AC 待 C4.6c 按需补，不阻断 |
   | 重要包已被认领但 core/standard 档覆盖率 `< 30%` | **WARN** | 写入 Gate C 审批摘要，由人工确认是否欠锚 |
   | 包已在 skip-list 中 | 跳过 | 需在 skip-list 注明理由分类 |

4. **skip-list 机制**（审计通过的唯一豁免途径）：纯平台胶水 / 测试 / 死代码 / 无业务语义的包写入 `spec/baseline/feature-coverage-skiplist.md`，每条记录 `package + 理由分类`。理由分类取值固定：`platform-glue`（平台桥接/控件壳）、`test-only`、`generated`、`dead-code`、`vendored-3p`（vendored 第三方库）、`merged-into-Fxxx`（语义已并入某 feature 但文件命名不匹配锚定 glob）。
5. 输出 `spec/baseline/source-coverage-report.md`：逐包列出 `file_count / loc / anchored% / 归宿（feature ID 或 skip 理由）`，并单列 FAIL / WARN 清单。
6. 通过条件：**每个重要包要么被某 feature 认领（含 peripheral stub），要么登记在 skip-list**——审计 ownership 而非统一深度（深度由 tier 分档 + C4.6c 按需保证）。FAIL → 回到 Step C2 补 feature/stub 或 skip-list；**至多自动重跑 1 次，仍 FAIL 则升级到 Gate C 摘要交人工决策，不无限循环**。

**为什么强制**：UI 审计只能发现「页面级」遗漏；UI 薄、引擎为主体的项目，最大的遗漏风险是「整个源码包没有任何 feature 认领」（无页面、无 API、可能也不在参考文档里），这类缺口只有源码侧普查 + 覆盖审计能在 spec 阶段暴露，否则会一路漏到实现/验证阶段。

## Step C4.6c: stub feature 按需深挖（execute 阶段触发，镜像 Phase A 按需模式）

`depth: stub`（peripheral）feature 在 spec 阶段只占位。当 a2h-execute / slice 执行真正触及它时，就地升级，无需回到 spec 全量重跑：

1. 把该 feature 从 `tier: peripheral` 视情升到 `standard`，`depth: stub → full`。
2. 补齐 standard 档 depth floor：覆盖率 ≥ 30%、AC ≥ max(20, anchored_LOC/250)、常量/分支/专属类穷举（含专属类 ≥1 AC）。
3. 增量更新 `feature-index.md` 状态与 `source-coverage-report.md`。
4. 继续切片，不中断 Pipeline。

触发条件：slice 目标 feature 的 `depth == stub`。这样「深度」被**延迟而非丢弃**——本轮把预算集中在 core/standard，peripheral 在被实际需要时才付深挖成本。

## Step C4.6d: 跨模块 seam 一致性审计（仅 `$MULTI_MODULE=true` 多子仓模式，强制）

C4.6 审 **UI 侧**覆盖、C4.6b 审 **源码侧 ownership**；本步与之对称，审 **跨模块边的两侧契约一致性**——分片生成最大的"错误逻辑"风险即在此。

1. 输入：`module-dep-graph.json` 的每条跨模块边 + 两侧子仓的 `features/F*.md`。
2. 对每条边 `A.caller → B.symbol`：
   - B 侧（owner）必须在某 feature 的 `## 服务层` 或 `## API 接口` 中规约该 symbol 的签名 + 语义契约；
   - A 侧（caller）的引用假设（参数 / 返回 / 可空性 / 副作用 / 线程）必须与 B 侧规约一致。
3. 判定规则：

   | 情况 | 判定 | 处理 |
   |------|------|------|
   | B 侧未规约被调 symbol | **FAIL** | B 侧补 feature/AC 认领该 seam 契约 |
   | 两侧契约不一致（签名 / 语义分叉） | **FAIL** | 以 owner（B）侧为准，修正 A 侧引用规约 |
   | 共享数据模型在两侧各自定义且分叉 | **FAIL** | 收敛到 `feature-base.md` / `cross-module-contracts.md` 单一权威，两侧引用 |
   | 边为 DI / 事件 / 反射（静态不可判，来自 P0.2） | **WARN** | 写 Gate C 摘要人工确认 |

4. 输出并入 `source-coverage-report.md` 的 `## 跨模块 seam 审计` 段（逐边列 owner / caller / 一致性判定）。
5. 通过条件：每条跨模块边两侧契约一致或登记 WARN；FAIL → 回到对应子仓补 / 改，**至多自动重跑 1 次**，仍 FAIL 升级 Gate C 摘要交人工决策。

**为什么强制**：分片生成的最大风险是跨子仓依赖被两侧各写一套 → 译成错误逻辑。本步在 spec 阶段（而非 verify 阶段）把 seam 不一致暴露出来。

## Step C4.6e: Addenda 元数据收口（仅 complexity=complex）

C4.5 / C4.6 / C4.6b 完成后（可能已通过自动追加触发新的 section overflow），对每个 `complexity=complex` 的 feature 执行 addenda 元数据收口与一致性校验。

1. 主文件 frontmatter YAML 块新增 `addenda` 字段，列出已生成的所有 addendum slug：

   ```yaml
   ---
   complexity: complex
   addenda: [api, state-machine, persistence]
   android_source_anchors:
     - role: service
       path: ...
   ---
   ```

2. 每个 addendum 文件 frontmatter：

   ```yaml
   ---
   parent: F001-playback                          # 主 feature 文件名（无 .md 后缀）
   slug: state-machine                            # 与主文件 addenda 数组中的条目一致
   consumed_by: [implementer]                     # 默认 [implementer]；仅当 addendum 对测试设计必需时加 verifier
   consumed_at: [step-3b]                         # 消费步骤（可多值）：step-3b | step-3c | closer | verifier；缺省按 slug 默认表（Step C4-pre 第 5 项）
   ---
   ```

3. `consumed_by` 语义：
   - `[implementer]`（默认） → 测试设计类 agent **不** load 此 addendum；修复类 agent 仅在 `kind=IMPL_MISSING` 时按需 lazy-load
   - `[implementer, verifier]` → 罕见。仅当 AC 拆分无法表达且测试设计确实依赖 addendum 时使用；优先考虑通过原子化 AC 消除此场景

   `consumed_at` 语义（步骤级过滤，供 a2h-execute 定向精读）：
   - `step-3b`（状态机 / 事件 / 生命周期 / 竞态类）| `step-3c`（API / 持久化 / 数据映射类）| `closer` | `verifier`；缺省时按 Step C4-pre 第 5 项 slug 默认表推断
   - a2h-execute 的 Step 3b / 3c worker 只精读「本 slice AC 组 `impl:` 指向 ∩ `consumed_at` 匹配本步骤」的 addendum §节（读取纪律与上限见 a2h-execute `agent-prompts/_common.md`「impl: 指针语义」）

4. 写入前交叉校验（不通过 → 报错并修正）：
   - 主文件 `addenda` 数组与 `spec/baseline/features/F00x-*.<slug>.md` 实际存在的文件**一一对应**
   - 每个 addendum 文件的 `parent` 字段指向存在的主文件
   - 每个 addendum 文件的 `slug` 字段与主文件 `addenda` 数组中的某条对应
   - 主文件 `## 验收标准` 不含 "(详见 xxx.md §y)" 或类似延迟描述（grep `\(详见.*\.md`、`see .*\.md`）；**AC 组标题 / AC 行尾的 `impl: <addendum>.md §<节>` 指针不属延迟描述**（指针只标注实现归宿，断言仍在 AC 本文）

5. **impl: 指针闭环（确定性 linter，~1 秒）**：

   ```bash
   python3 .agents/skills/a2h-spec/scripts/lint_addenda_closure.py --spec spec/baseline
   ```

   - **FAIL**：主文件 `addenda` 数组与实际 sibling 文件不一一对应 / `impl:` 指针悬挂（目标 addendum 文件不存在，或 `§<节>` 在目标文件中无匹配标题）/ AC 稳定 ID 缺失（`- [ ]` 后无 `F{编号}-AC{序号}`）、前缀与本文件 feature 编号不符、或全局重复
   - **WARN**：文件名偏离 `F\d{3}-{name}[.{slug}].md` 规范（存量字母前缀 corpus 仅提示）/ 孤儿 addendum（无任何 `impl:` 指向且 `consumed_by` 无 verifier——写了没人读的深度，补指针或删）/ AC 行有「详见」却无 `impl:`（应升级为指针）/ 单 addendum >400 行（拆分或收紧）
   - **单一权威 = 主文件前向 `impl:` 链**；反向索引由 linter 现算，**不落盘镜像字段**（避免双写漂移）
   - FAIL → 修指针 / 补节 / 同步数组后重跑，**至多自动重跑 1 次**，仍 FAIL 升级 Gate C（与 C4.6b / C4.6d 同款上限）

5. complexity=simple 的 feature 跳过本步骤（无 addenda）。
