<!-- when: 生成 plans/slices/slice-NN-<fid>.md（L2 slice 文件）时加载 -->
<!-- topics: slice 文件, 只读调度账本, 结构化接线对, anchors_ref -->

# slice-NN-<fid>.md（L2 slice 文件）完整模板

**三条铁律（写进每份生成物的自我约束，违反 = plan FAIL）**：

1. **调度表而非详案**：work_scope只允许名字级引用（页面序号/VM名/service名）；机器scope只取product/excluded。业务内容用spec_refs精确指针，复制spec正文仍FAIL。
2. **生成后只读**：不含 checkbox、evidence 槽、状态字段——完成性由 verify_slice_wiring 机械校验（读代码）+ 组 brief 小节记录；worker 与 closer 均不回写本文件。
3. **不持有占位**：plan 期占位直接写 `spec/placeholder-registry.md`（P-ID 发号协议见 execute `_common.md` §2.1c）。

profile 2每步生成一张局部责任表（字段/值、恰7行，值为JSON literal），完整item_id使用SLICE:F-ID:3a/3b/3c/3d。每步输入引用active AC、精确Spec章节与contract_refs闭包。人读的名字级任务范围命名为work_scope，与机器scope="product"/"excluded"区分。按[Plan交付合同](../references/plan-delivery-contract.md)生成与全部局部表7字段exact一致的唯一Plan items JSON。

## 模板

```markdown
## Slice 7: 首页与院校浏览 (F006)
parallel_group: 4 | complexity: simple
depends_on: [Slice 5]
# （chain-auth 项目）本 slice 为某层 owner 时必加：data_chain_refs: chain-auth L4-L6 —— 字段名必须如此，写进 input 指针不算（§7 第 10 项按字段名校验）

source_anchors_ref: {count: 0, source: spec/baseline/features/F006-home-college.md}

integration_points:                     # 纯结构化对（无 checkbox / evidence），从 spec「## 对接点」lift
  - HomePage.@Local collegeList ← CollegeViewModel.collegeList
  - HomePage.onCollegeClick → CollegeViewModel.openDetail()

wires:                                  # 统一接线账本（同现行：VM 入边 + embed 入边）
  - page: entry/src/main/ets/pages/HomePage.ets
    viewmodel: entry/src/main/ets/viewmodels/CollegeViewModel.ets
  - page: entry/src/main/ets/pages/IndexPage.ets      # 组件嵌入入边 → C4
    slot: tab1Home
    embed: HomePage()
    resolve_by: Slice 7 Step 3a

modifies_files:                         # 只列他切片所建文件（自建文件禁列）；本例 IndexPage 由别的切片创建
  - entry/src/main/ets/pages/IndexPage.ets
  cross_slice_edits:                    # 只收非 embed 的 handler 回改；tab1Home 槽位填充已由上方 wires embed 条（含 resolve_by）承载，禁止在此双登
    - file: entry/src/main/ets/pages/IndexPage.ets
      handler: onCollegeShare           # 示例：真 handler 回改（非槽位填充）
      resolve_by: Slice 7 Step 3d

- Step 3a: UI 补充 — work_scope: 0072, F001(HomePage)（名字级）| input: ui-manifest对应行 + ui-manifest.md#全局约定 + ui/page_0072.md#组件层级
- Step 3b: ViewModel — work_scope: CollegeViewModel | suggested_skills+: arkts-login | input: features/F006-home-college.md#状态管理 + <实际合同路径#精确节>
- Step 3c: 数据层 — work_scope: CollegeService | input: features/F006-home-college.md#API接口 + <实际合同路径#精确节>
- Step 3d/3e: 接线 + 验证 — input: integration_points/wires + <动作完成事件的精确引用> | 契约见 a2h-execute §5e（本文件零复述）
```

## 字段规则

| 字段 | 规则 |
|---|---|
| 头部 3 行 | 与索引条目一致（§7 校验快照一致性） |
| `source_anchors_ref` | `{count, source}` 结构化残端；**不复制 anchors 列表**（权威在 feature spec 顶部，worker 按 grep-first 纪律定点消费） |
| `integration_points` | 单行结构化对 `<Page>.<handler|@Local 状态> ←/→ <Target>.<member>`；零 checkbox、零 evidence、零散文 |
| `wires` / `cross_slice_edits` | 同现行 YAML 形态（parser 兼容）；embed 条目含 slot/embed/resolve_by。**去双登**：跨切片槽位填充只登 wires embed 条（resolve_by 即归属声明），cross_slice_edits 只收非 embed 的 handler 回改——closer 步骤 1-0/1a/1b 按 embed ∪ cross_slice_edits 并集消费，双登即噪音 |
| `modifies_files` | 只列**他切片所建**的已存在文件；**本切片自建文件禁列**（自建是 generates 事实）；无他建回改时整段省略 |
| Step 行 | 每步一行：work_scope + 可选suggested_skills+ + input指针；机器责任放本步固定表，验收契约零复述（权威在execute §5b–5e） |
| `suggested_skills+` | **差异化增量**（delta-only；字段名含 `suggested_skills` 词根便于检索、`+` 表增量）：只写超出步骤默认映射（a2h-plan §4 表）的追加 skill（如登录→arkts-login / 支付→arkts-payment / H5→arkts-webview），plan 期语义判断的确定性产出；默认映射零复述、无追加不写字段 |
| `item_id` / `ac_ids` / `contract_refs` | 责任表为完整稳定ID与实际实施AC；合同精确节进入传递闭包。纯名字work_scope不能替代这些输入 |

## Plan items（生成文件的必备末节）

四步分别以含完整ref的独立标题（如`### SLICE:F006:3b`）定位，标题下恰一张局部责任表；该标题用于冻结任务精确消费。示例为3b，其余步同样填写，不用步骤关键词代替机器字段。

### SLICE:F006:3b

| 字段 | 值 |
|---|---|
| item_id | "SLICE:F006:3b" |
| ac_ids | ["F006-AC01"] |
| ownership | ["entry/src/main/ets/viewmodels/CollegeViewModel.ets"] |
| parents | ["BASE:Base-1"] |
| page_ids | ["page_0072"] |
| scope | "product" |
| verification | "generated" |

末节唯一plan_items_version:2 JSON块投影全部局部表，7字段exact一致。Step 3d结构/编译不冒充behavior；行为/视觉若在后续承担，映射保留每项义务。typed task拆合填写mapping_reason，原Slice只读。
