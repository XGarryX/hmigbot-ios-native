<!-- when: 派发 Stage 3 Step 3d 自身页内接线（a2h-migration-worker）时加载本段 + _common.md -->
<!-- topics: Step 3d 自身页内接线 prompt, 单写者纪律, forward-ref 解除, evidence 规则 -->

# §7. Stage 3 Step 3d 自身页内接线 prompt（a2h-migration-worker）

> 公共占位规则 §2.1 + 单写者纪律见 [`_common.md`](./_common.md)，派发时一并 Read。
> 跨文件接线 / 编译 / 结构验证 / brief 由本组 group-closer 统一完成，见 [`8-group-closer.md`](./8-group-closer.md)（§8）。

派发 Codex 子代理 `a2h-migration-worker`（定义于 `.codex/agents/a2h-migration-worker.toml`），任务提示词：

```
你正在执行 Feature Slice [{slice_name}] 的 Step 3d 自身页内接线（跨文件接线 / 编译 / 结构验证 / brief 由本组 group-closer 统一完成，见 §8）。

  接线清单（来自 plans/slices/slice-NN-<fid>.md——只读调度账本）:
  - integration_points: {integration_points}     # 纯结构化对（page.handler ← Target.member），无 checkbox/evidence
  - wires: {wires}                                # page → viewmodel 映射
  - modifies_files: {modifies_files}              # 本 Slice 需修改的【已存在】文件
  - cross_slice_edits: {cross_slice_edits}        # 跨切片回改子集（仅作上下文，本 step 不执行——closer 落地）

  已有 ViewModel: {viewmodel_path}
  已有 Repository: {repository_path}

  使用 `$arkts-state-manager` skill

  写盘边界（单写者纪律，无条件）:
  - 只编辑【本 slice 自身】的 page / component / VM / repository 文件。
  - 禁碰共享文件与他切片文件：HomePage 等父页、feature-plan.md/plans 产物、
    cross_slice_edits 列出的文件——全部移交 group-closer（§8 步骤 1）。
    两项 append-only 例外照 _common.md：registry 登记行 append、资源 JSON append 缺失键。

  任务:
  1. 编辑 modifies_files 中属于自身页面/组件的【已存在】.ets 文件（不新建）。
  2. 补 import：自身页面 / 子组件 import 并实例化对应 ViewModel（`new XxxViewModel()`）。
  3. 替换 forward-ref 钩子：grep 自身文件内 `// FWD-REF:` marker，逐个换成真实调用：
     - handler 绑定到 ViewModel 方法
     - aboutToAppear 调用 ViewModel / Repository 加载数据
  4. 接线完成性**不回填任何 plan 文件**（slice 文件只读）——由 verify_slice_wiring C2 按
     结构化对从代码机械判定；自身完成的对接点计数随报告返回（明细 closer 写入 brief）。

  占位规则:
  - 接线工作禁止留任何 placeholder / TODO / prose defer。
  - resolve_by=本 Slice 的 forward-ref：【自身文件内的】必须在本 Step 全部解除（marker 消失 + 真实实现存在）；
    位于共享 / 他切片文件中的由 group-closer 解除（§8 步骤 1c）。

  返回报告必须含（信封，_common.md 信封契约）:
  - wired_files: []          # 实际改动的自身文件清单（仅路径）
  - resolved_fwd_refs: []    # 本 Step 解除的 forward-ref P-ID 清单（closer 据此记入 writeback manifest `registry.resolve`）
  - integration_points_done_count: N  # 自身页内已接对接点计数（明细 closer 写入 brief；机械判定归 verify_slice_wiring）
```

**evidence 规则**：接线 evidence 必须指向**调用方**（如 `pages/CreateOutLinePage.ets:48 import` + `:81 new AIPptViewModel()`），**不得用 ViewModel 文件自身行号充数**——VM 文件存在不等于被接上。

> **scope 说明**：§7 的 scope **永远是自身文件**（任意组大小，含 size-1 组）。跨文件部分（cross_slice_edits / HomePage embed wires / registry 状态集合）整体由 §8 group-closer 收口（账本经 writeback manifest 落盘；plan 产物零回填）——不存在"§7 做全部接线"的模式。
