<!-- when: 派发 Stage 3 Step 3a UI 补充（a2h-migration-worker）时加载本段 + _common.md -->
<!-- topics: Step 3a UI 补充 prompt, forward-ref-uncertain 二次审视 -->

# §4. Stage 3 Step 3a UI 补充 prompt（a2h-migration-worker）

> 公共占位规则 §2.1 + 单写者纪律见 [`_common.md`](./_common.md)，派发时一并 Read。

派发 Codex 子代理 `a2h-migration-worker`（定义于 `.codex/agents/a2h-migration-worker.toml`），任务提示词：

```
你正在执行 Feature Slice [{slice_name}] 的 Step 3a: UI 补充。

  目标页面 + 嵌入子组件: {page_list}（含 ui-manifest 子组件表中的内嵌 Tab / Guide 子组件）
  页面 Spec: {page_spec_paths}

  检查页面状态:
  - 查询状态用 grep ui-manifest 对应页行（_common.md 校验性读取纪律），禁整读 manifest。
    例外：`## 全局约定` 节（设计令牌）允许并**要求**整节读，见下方「设计令牌」条。
  - 如果页面已在 Stage 1 转换完成（status: converted），确认 .ets 文件存在并报告——【不跳过 Slice】，页面接线由 Step 3d 处理。
  - 如果页面未转换，执行 UI 转换。

  派 `a2h-activity-converter` 子代理（`spawn_agent(agent_type="a2h-activity-converter")`；它是 agent 不是 skill，见 agents/a2h-activity-converter.toml）（如需转换新页面）
  公共组件库路径: entry/src/main/ets/components/common/

  设计令牌（机械注入，禁止转述/摘要）:
  - 派发本 prompt 前，**本 worker（不是主线程——你收到本模板时就是派发方）必须**运行
    `python3 <a2h-execute skill 根>/scripts/theme_brief.py --project <鸿蒙工程根> --activity {activity 名}`
    并把 stdout **原文**粘贴到下方占位块。输出自带
    `<<<THEME-BRIEF v2 BEGIN>>> ... <<<THEME-BRIEF v2 END>>>` 哨兵——
    粘贴后自检：prompt 里必须能看到成对哨兵，且不得残留 `{THEME_BRIEF_STDOUT` 字样：

    {THEME_BRIEF_STDOUT — 派发前用 theme_brief.py 输出原文替换本行，禁止留空或改写}

  - **二级派发透传义务（硬性）**：本步如再向下 spawn `a2h-activity-converter`，
    上方哨兵块必须**原文携带**进 converter 的提示词——转述、摘要、"它自己会去读"
    均视为违纪（实测教训：规格块只要经过一次模型转述就会丢失）。
  - 补充来源 = `spec/baseline/ui-manifest.md` 的 `## 全局约定` 节整节读取
    （`sed -n '/^## 全局约定/,/^## /p' spec/baseline/ui-manifest.md`；排版/图标等非主题令牌在此）
  - 若本步修正了主题绑定，写/更新**本页分片回执**
    `spec/execution/theme-receipts/<page_id>.json`（键=条目名，值=file:line；
    分片按页隔离，禁止写共享单文件）；收口时 theme_gate.py 按必填闭集机械对账，缺项 FAIL 打回
  - Android 侧靠主题隐式继承着色的控件（Material Button / Toolbar / TabLayout / FAB 等）
    必须在 ArkUI 侧**显式绑定**对应令牌资源 `$r('app.color.*')`，不得落回系统默认色
  - **禁止自创平行令牌体系**：转换期不得新建 `DesignTokens.ets` 之类裸数字/裸色值常量文件，
    不得硬编码色值与尺寸；一律走 `$r('app.color.*')` / `$r('app.float.*')`
    （边界：extractor 的 converter 内部挂钩在 a2h 管线内**停用**——其 DesignTokens.ets 产物与 $r 纪律互斥；仅限用户显式调用且走 float.json/color.json 路线）
  - 令牌节缺失或不匹配 → 报告 `design_tokens_missing`，禁止自行发明后静默继续

  forward-ref-uncertain 二次审视（本 Slice 的责任）:
  - 读 spec/placeholder-registry.md，过滤 kind=forward-ref-uncertain AND resolve_by=Slice {本} Step 3a
  - 对每个 P-ID:
    1. 定位 location 指向的代码区域（converter Stage 1 因 confidence=medium/low 留的 // TODO: 注释）
    2. 决策升级 OR 保留:
       - 升级为真实实现 → 删 TODO 注释 + 写真实代码 → 报告 uncertain_regions_resolved[<P-ID>]
       - 占位合理（动态值确实运行时才知）→ 保留 TODO + 报告 uncertain_regions_retained[<P-ID>, 原因]

  输出:
  - 确认所有目标页面存在对应 .ets 文件
  - uncertain_regions_resolved[]: 已升级实现的 P-ID 列表（execute 据此把 registry status → resolved）
  - uncertain_regions_retained[]: 保留占位的 P-ID + 原因（execute 写迁移报告）
```
