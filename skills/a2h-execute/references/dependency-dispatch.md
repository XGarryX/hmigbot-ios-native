# Base 与 Slice 的真实依赖调度

## Plan 写作与冻结

保持原七字段 plan_items；parents 记录实际数据/接口/接线依赖，不为凑顺序添加虚假串行链。Base-1 公共模型先稳定；Database、Events、Preferences、公共组件只有真实互不依赖且 ownership 不相交才可并发。需要配置/数据库的 Network 保留真实父依赖。Base-7、FV-1、FV-2 都保留。已有冻结计划变更沿 reviewed replan；不能施工时重写计划或刷新旧摘要。

Slice 的 3a–3d 按同 F-ID 聚合一个 worker；组名作为共享收尾 checkpoint。需要比“父组已收尾”更细的目标输入时，在对应计划文件内添加并冻结以下独立 JSON 块，聚合 plan_items 原合同不变：

```json
{
  "dispatch_policy_version": 1,
  "items": [
    {"item_id": "SLICE:F002:3b", "checkpoint": "group-2", "reads": [
      {"path": "entry/src/main/ets/viewmodels/Model.ets", "producer": "SLICE:F001:3b"}
    ]}
  ]
}
```

示例 ID/路径须替换为当前已审真实项。producer 必须已在该项 parents 且拥有此精确路径；不能用 reads 删除父依赖。同一个 Slice 的所有部分 checkpoint 一致；同组各 Slice 也填同一 checkpoint。没有细化 reads 的父依赖保守等待原 closer/writeback。producer 的 `:3d` 接线文件属于 closer 后续写入范围，不能提前读。

编译安排在一处冻结计划（例如 feature-plan）声明；默认保留逐组编译。确有可独立施工任务、且完整集中构建消费者可用时可记录技术试点，不新增与现有授权重复的产品审批：

```json
{"dispatch_policy_version":1,"compile_policy":"stage3-pilot","items":[]}
```

## Execute Base 与 Slice

沿 [Stage 1 宿主调用规程](stage1-dispatch.md) 的 next → 真实 spawn → bind → observe 循环，phase 改为 `base` 或 `slice`。前置 UI Batch 仍先收口；Base 的每项保留原 closer 和 writeback，并以原 indexed receipt 关闭 checkpoint。公共接口只有当前产物哈希仍匹配才释放依赖。

Base-1..6 的相关任务/收尾停止写入后，派原 hmos-builder 执行真实 build，得到原 build.py 的 `build.json`、日志、诊断和 HAP，再执行：

```sh
python3 <runtime>/scripts/a2h_ios.py indexed-dispatch build-report --project <target> --gate base7 --evidence <实际外置build.json>
```

Base-7 的 build-report 只记真实构建返回；仍须原 Base-7 closer/writeback 并消费其 indexed receipt 关闭 checkpoint，才允许 Slice 派发。仅有构建报告不能跳过原收尾。Slice 依赖的 worker 接口已可信返回、输出非空且哈希固定、不在任何未结束作者的修改范围，并有冻结 reads 时，可提前处理独立部分。跨 checkpoint 提前启动还要求其 F02 scope 已登记 `resources:[]`：含新共享 element 资源的后续任务须等上一 closer 合并后再初始化/开工，避免旧资源原像过期。路由/公共导出继续等对应 closer。

closer 必须串行处理公共文件。默认每组保留真实编译；记录 `build-report --gate group:<checkpoint> --evidence <build.json>` 后才 checkpoint。构建时不得有 active/stopped 写者；当前 HAP、日志、诊断和源码身份都核验，不以旧 HAP 或退出 0 单独放行。`indexed-dispatch errors --input <原diagnostics.json>` 按实际文件 ownership 返回责任任务；未知/共享路径不自动授予任意 worker 修复权。

## Stage 3 集中编译试点

只有冻结 policy 为 `stage3-pilot` 才走此分支：每组仍做接线、F02 merge、原结构检查和非 loop 检查，group brief 用 `GENERATED_PENDING_COMPILE`，`build_status: deferred-to-stage3-gate`；`loops.compile.iterations: 0`、`converged: false`，不写 PASS。manifest 只写本组 brief/registry，不提前写 ui_manifest.verified 或 feature_index.implemented。

主线程仍调用原回写入口，额外给 `--generated-checkpoint <checkpoint>`（与 `--resource-scope` / `--resource-closer` 一起）。适配层核对已审 refs 和当前产物，原 vendor 只收到原 manifest；indexed receipt 记录 generated_checkpoint，控制器消费此收据关闭“生成收口”，编译保持 pending。

全部组收口且写者停止后，派原 hmos-builder 真实集中构建，再 `build-report --gate stage3 --evidence <实际build.json>`；`indexed-dispatch status` 必须返回 handoff_to_fv。历史 group brief 不补写成编译通过，独立当前构建证明由真实 FV structural_loop 入口消费：缺失/失败/过期返回 3，不触碰旧 loop state/result；通过后继续原全部检测器。末组/试点组延后的进度由 FV 原结构与真实编译条件满足后原 final writeback 补翻，不能把 pending_generation 当已验证。

Base-7、FV-1 全结构和 FV-2 最终真实构建始终执行。试点是否更快用 F14 相同输入/质量要求的总等待、并发、构建和返工记录判断，不预设必然提速。
