<!-- when: 生成 feature-plan.md（L1 调度索引）+ plans/base-plan.md（Base 层正文）时加载 -->
<!-- topics: feature-plan 索引, plan_format, Base 层 stub, base-plan.md, Group 分节, group-closer 插入点, slice 头部, FV, indexed 布局 -->

# feature-plan.md（L1 调度索引）+ base-plan.md 完整模板

**indexed 布局唯一**：feature-plan.md 是纯调度索引——无状态列、无 spec 复述、无步骤契约样板、无依赖 ASCII 树；Base 层正文外置 `plans/base-plan.md`（仅 Stage 2 消费）；逐 slice 账本在 `plans/slices/slice-NN-<fid>.md`（模板见 [slice-plan-template.md](./slice-plan-template.md)）。

profile 2按[Plan交付合同](../references/plan-delivery-contract.md)为每个Base/FV正文任务生成一张局部责任表（字段/值、恰7行，值均JSON literal），记录完整item_id/ac_ids/ownership/parents/page_ids/scope/verification；各文件再输出与全部局部表7字段exact一致的唯一Plan items JSON。索引只投影自身FV，不能再次投影Base/Slice。精确输入章节另写，不凭关键词猜测依赖/范围/验证义务。

主控生成typed request时同步采用[决策上下文范围](../references/prompt-scope.md)与[request示例](plan-request-template.json)：只为显式审阅的局部决策添加prompt_scope；未标scope的全局/跨模块决策继续全部传播。此配置不写入7字段局部责任表、不改变写权/AC/验证义务，不能仅按无fact引用删除共享约束。

## 文件一：feature-plan.md（索引）

```markdown
# Feature Execution Plan

## Context
- spec_contract_version: 2
- plan_format: indexed-v1                  # 版本标记（消费脚本检测旧 monolith 的依据）
- Source: spec/baseline/feature-index.md, spec/baseline/feature-base.md
- Style: <style_set 值，none 或具体风格名>
- Total features (V1): <N>
- Total slices: <N>
- Base tasks: <Base 层任务数>
- 定位 / 工程锚点: <decision-ledger D0 摘要一行，不复述 ledger 正文>

## Base 层（<N> tasks；执行序 Phase 0；blocking: <由实际任务派生>）
detail: plans/base-plan.md

<Base 层到此为止——正文在 base-plan.md，索引不展开任何 Base 任务行>
```

## 文件二：plans/base-plan.md（Base 层正文，与索引同批生成）

**只读态**：与 slice 文件同律——无 checkbox、无 evidence 槽（完成性由 execute `base_NN_brief.md` HARD-GATE 记录，plan 不承载执行态）。

```markdown
# Base 层任务（执行时序 Phase 0，先于所有 Slice）

所有 Feature Slices 共用的基础设施，必须先完成。

- Base-0: 资源前置扫描与迁移
  - item_id: Base-0
  - suggested_skills: [ios-resources-convert]
  - input: 所有 spec 中引用的资源 ID 全集（扫描 spec/baseline/ui/page_*.md、spec/baseline/features/F-*.md、feature-base.md）
  - output: entry/src/main/resources/ 全量资源 + spec/baseline/plans/resource-mapping.md
  - acceptance: 缺失资源显式标 `$r('app.media.MISSING_xxx')`（编译期失败暴露而非静默 fallback）
  - blocking: true

- Base-1: Models — 所有 entity / DTO 定义
  - item_id: Base-1
  - suggested_skills: [arkts-data-layer]
  - input: feature-base.md Models 段
  - output: entry/src/main/ets/models/*.ets

- Base-2: Database — Schema + DAO
  - item_id: Base-2
  - suggested_skills: [arkts-data-layer]
  - input: feature-base.md Database 段
  - output: entry/src/main/ets/database/*.ets

- Base-3: Network — HttpClient + interceptors
  - item_id: Base-3
  - suggested_skills: [arkts-data-layer, arkts-network-troubleshoot]
  - input: feature-base.md Network 段
  - output: entry/src/main/ets/network/*.ets
  - data_chain_refs: chain-auth L2-L3    # 仅 chain-auth 项目填（Step 4.3 注入；字段名必须如此，§7 第 10 项按字段名校验）

- Base-4: Events — EventHub 常量 + pub/sub wrapper
  - item_id: Base-4
  - suggested_skills: [arkts-state-manager]
  - input: feature-base.md Events 段
  - output: entry/src/main/ets/events/*.ets

- Base-5: Preferences — 偏好设置与持久化行为迁移
  - item_id: Base-5
  - suggested_skills: [arkts-data-layer]
  - input: feature-base.md Preferences 段
  - output: entry/src/main/ets/preferences/*.ets

- Base-6: 公共组件库
  - item_id: Base-6
  - suggested_skills: [arkts-component-builder, arkts-pattern-library]
  - input: ui-manifest.md 共享组件表 + feature-base.md 公共组件段
  - output: entry/src/main/ets/components/common/*.ets

- Base-6.5: 组装根（能力表装配）——能力交付契约的收货点
  - item_id: Base-6.5
  - output: `entry/src/main/ets/AppAssembly.ets`——导出 `capabilityTable: CapabilityTable`
    **直接对象字面量**（每键 = 能力清单一项，值 = 规范实例；禁函数间接构造、禁 as）；
    使用plan-delivery-contract版本2结构化initialization声明真实宿主/阶段/调用/守卫/返回链；
    实际方法可以是open/installRoot/disposeRoot等，不按名字强制放在EntryAbility.onCreate
  - 能力清单 = 机械生成闭集（Base-1..6 单元 + 各 slice Step 3c scope + contracts seam 渠道符号；
    `gen_capability_manifest.py` 产出，闸每轮重新生成防篡改）
  - **消费方从组装根取依赖；组装根之外禁止 new 槽位类**（双实例=闸 FAIL）
  - 现代声明全局一个capability_schema:2围栏，runtime-slot/scoped/artifact-only按真实职责区分。
    absence/seams本轮仅none，批准缺席结构明确unsupported；禁止Unavailable*/Noop*空对象凑门。
    未来未物化项gen可列pending，最终ledger默认失败；不可删责任或创建空类抹平缺失
  - 验收：`capability_ledger_gate.py`（arkts-structural-closure，FV-1 pipeline 自动跑）
- Base-7: 编译验证 — Base 层全量编译
  - item_id: Base-7
  - suggested_agents: [hmos-builder]
  - blocking: true
```

> Base 任务的 input 一律写**指针**（feature-base.md 对应段），不复述能力清单内容。

每个Base/FV以`### BASE:Base-N`或`### FV:FV-N`独立标题定位；该标题用于冻结任务精确消费。标题下含输入/输出及恰一张责任表，示例值替换为实际责任，字段名/表头不变。

### BASE:Base-1

| 字段 | 值 |
|---|---|
| item_id | "BASE:Base-1" |
| ac_ids | [] |
| ownership | ["entry/src/main/ets/models/LibraryModel.ets"] |
| parents | ["BASE:Base-0"] |
| page_ids | [] |
| scope | "product" |
| verification | "generated" |

示例能力不等于固定任务总数：依据当前 Spec 选择任务，保留所需能力与阻断编译任务。每项补 `spec_refs`/`contract_refs` 精确节和相关 `ac_ids`；输出通配符在排期时展开成精确 owned files。base-plan.md 末节 `## Plan items` 的唯一 JSON 块逐项列 `BASE:Base-N` 全名（含非整数原编号），字段按交付合同，根任务 `parents: []`。

## 文件一（续）：Slice 索引（按 parallel_group 以 `## Group N` 分节；每组末尾一行 group-closer 插入点）

```markdown
## Slice 索引

## Group 1

## Slice 1: <功能名> (F001)
parallel_group: 1 | complexity: complex
depends_on: [Base]
pages_owned: 2 | placeholders: 1
detail: plans/slices/slice-01-f001.md

> group-closer @ G1：落地本组 cross_slice_edits + embed 槽位 → 编译 → 结构 fix-forward → 各 slice brief（契约见 a2h-execute §5e，plan 只标插入点、不复述五步）

## Group 2

## Slice 2: <功能名> (F002)
parallel_group: 2 | complexity: complex
depends_on: [Slice 1]
pages_owned: 1 | placeholders: 2
detail: plans/slices/slice-02-f002.md

> group-closer @ G2：同上（每 parallel_group 末尾恰一个 group-closer，size-1 组亦然）

<每 slice 头部固定 4 行字段，除此之外不写任何账本内容——账本在 slice 文件；
 Group 标题与 group-closer 行都是分节排列（parser 按 `## Slice` 头切段、二者天然容忍），slice 编号才是身份>

---

## Final Verification（Stage 3 全部 Slice 完成后顺序执行）

- FV-1: Final Structural Closure（a2h-execute §6）
  - item_id: FV-1
  - ac_ids: []（公共结构收口；不借此认领行为AC）
  - owned_files: []（profile 2独立FV只读；finding回原文件owner修复后重检）
  - suggested_skills: [arkts-structural-closure]
  - blocking: true
  - details: 调用结构闭包规程跑整工程兜底。profile 2独立FV只检查与回报finding，CONTINUE回原文件owner修复后重检；任务内部closer仅在冻结写权内收尾。禁止grep替代结构检查。
  - acceptance: `final_state == PASS`（完成性凭据由 execute §6 落 loops JSON + fv brief，plan 零回填）

- FV-2: 终态全量编译
  - item_id: FV-2
  - ac_ids: []（公共编译验证）
  - owned_files: []（profile 2独立编译验证；编译错回原文件owner修复后重检）
  - suggested_agents: [hmos-builder]
  - blocking: true
  - details: FV-1 通过后（其修复可能改码）跑终态全量编译（≤20 轮）；编译修复仅限编译级小改，**不回跑 FV-1**。
  - acceptance: BUILD_STATUS=PASS（真实构建，非 up-to-date 空转；凭据落 fv brief）

## Summary
- Base 层: <N> tasks（执行序 Phase 0）
- Feature Slices: <N>
- 并行组: <M> 组（size-1 组非 0 时附理由）
- Final Verification: 2 tasks
```

## 必填规则

1. 每 slice 头部字段齐全：`parallel_group / complexity / depends_on / pages_owned / placeholders / detail`（**无 priority**——优先级权威在 feature-index，调度只由 parallel_group + depends_on 驱动，快照即冗余）。`detail:` 必须指向实际生成的 slice 文件（§7 校验索引 ↔ 文件一一对应）。
1b. **Base 层 stub 恰 3 行**（`## Base 层` 标题含任务数与 blocking 标注 + `detail: plans/base-plan.md`，执行序 Phase 0 作括注）；指针指向同批实际生成的 base-plan.md；索引内**禁止展开任何 Base 任务行**（正文只在 base-plan.md 一处）。
1c. **Slice 索引按 parallel_group 以 `## Group N` 分节**（子组 2a/2b 各自分节）；Group 标题是排列不是身份——slice 编号才是引用键（P-S{N} / resolve_by / briefs），parser 按 `## Slice` 头切段、Group 行天然容忍。
1d. **每个 `## Group N` 末尾一行 `> group-closer @ GN`**（blockquote 插入点：落地本组 cross_slice_edits + embed → 编译 → 结构 fix-forward → brief）；对称 ui-plan 的「结算检查点」行——plan 只标插入点 + 指向 execute §5e，**不复述 closer 五步**（单一权威源）。
1e. **base-plan.md 只读**：Base 任务行无 `- [ ]` checkbox、无 `evidence:` 槽（对齐 slice 文件三铁律②；Base 完成性由 execute `base_NN_brief.md` 记录）。
2. `complexity` / `tier` 为一词级快照（spec 为权威，§7 校验一致性）。
3. `placeholders:` 为 registry 派生显示值（plan 期占位直接写 `spec/placeholder-registry.md`，索引不持有占位内容）。
4. **禁止**：依赖 ASCII 树（feature-index 已有，此处只留 depends_on/parallel_group 可执行编码）、步骤契约文本、integration_points / wires 等账本内容、任何状态列（执行状态在 feature-index / ui-manifest / briefs）。

5. feature-plan.md末节唯一Plan items JSON仅投影FV:FV-1/FV:FV-2；profile 2独立FV两项ownership均[]、verification均compile（第一项附结构检查义务），不得宣称行为或视觉通过。FV-2 parents含FV-1，二者在全部产品任务后。修复回原文件唯一owner；任务内部已获写权的closer仍按原Stage收尾。如另有真实行为/视觉任务明确保留相应义务，不虚构已执行结果。

6. FV每项以含完整ref的独立标题（如`### FV:FV-1`）定位，并有恰一张7行局部责任表；局部表与聚合JSON的parents/page_ids/scope/verification同样逐字段exact一致，不能仅核对ID/路径出现。所有parents填当前实际完整ref，根项[]，不以“所有任务之后”散文代替依赖数组。
