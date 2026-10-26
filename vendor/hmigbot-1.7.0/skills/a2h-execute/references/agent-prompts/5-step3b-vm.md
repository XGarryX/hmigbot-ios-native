<!-- when: 派发 Stage 3 Step 3b ViewModel C7 三段式（a2h-migration-worker）时加载本段 + _common.md -->
<!-- topics: Step 3b ViewModel 三段式 prompt, 源码理解, 差异清单, source-notes -->

# §5. Stage 3 Step 3b ViewModel C7 三段式 prompt（a2h-migration-worker）

> 公共占位规则 §2.1 + 单写者纪律见 [`_common.md`](./_common.md)，派发时一并 Read。

派发 Codex 子代理 `a2h-migration-worker`（定义于 `.codex/agents/a2h-migration-worker.toml`），任务提示词：

```
你正在执行 Feature Slice [{slice_name}] 的 Step 3b: ViewModel + 状态管理。

  功能 Spec: {feature_spec_path}
  UI Spec: {ui_spec_paths}
  已有 UI 文件: {existing_ets_files}
  Slice 复杂度: {complexity}            # simple 或 complex
  Slice 文件: {slice_file_path}          # plans/slices/slice-NN-<fid>.md（只读调度账本）
  Android 源码 anchors:                  # complex 必传：spec 顶部全部 anchors（经 slice 文件 anchors_ref.source 取）
    {anchors_yaml}
  Android 源码根目录: {android_source_dir}

  使用 `$arkts-state-manager` skill
  可调用的辅助 Skills（worker frontmatter 保留的 17 个之一）:
    - android-ui-graph-query: 查 page/component 上下文
    - android-view-to-arkui: Android XML → ArkTS 组件翻译
    - arkts-knowledge-verifier: API 验证

  任务（complex feature 强制走完三段；simple 可跳过第一、第二段）:

  【第一段：源码理解】（complexity=complex 时强制）
  在生成任何 ArkTS 代码前，必须 Read 上方 anchors 列出的文件（grep-first 定点读，
  不整读源文件）。**spec 已含「## 源码 5-role 摘要」时先核对
  该摘要**（不重写），差异随第二段输出；spec 无摘要时按 5 个 role 输出摘要（缺一不可）：

    ### Source Understanding Summary
    - role=presenter/viewmodel: 总结 ① 状态机（列出所有状态枚举） ② 事件流 ③ 异常分支
    - role=service/repository:  总结 ① 接口列表 ② fromJson 兜底 ③ 缓存策略
    - role=interceptor:         总结 ① 拦截链顺序 ② header/参数注入 ③ 加密路径
    - role=base_class:          总结 ① 基类 lifecycle hook ② opt-in 机制 ③ 共享状态
    - role=util:                总结 ① 静态方法清单 ② 命中场景 ③ 副作用

    每个 role 摘要**必须含具体的 Kotlin 类名或方法名**（grep 反查依据）——缺类名/方法名 → WORKER FAIL。
    无 anchor 的 role → 输出 \"该 role 无 anchor\"，但其他必须填齐。

    功能 Spec 的 AC 组带 impl: 指针（目标 addendum consumed_at 匹配 step-3b，缺省按 slug
    默认表）→ 按 _common.md「impl: 指针语义」精读目标 §节（≤3 节 / ≤150 行，超出记
    deferred_addenda），与 anchors 源码一并纳入本段理解；禁止整目录扫读 addenda。

    AC 锚点二型：`源:<Kotlin 符号> → 标:`（parity，行为契约 = anchors 源码）与
    `决:<PD/D/G-ID> → 标:`（平台差异 AC）。遇 `决:` 锚 AC：**行为契约 = grep
    spec/decision-ledger.md 该决策 ID 的正文**（替代行为描述 + §数据流 `替代路径` 行），
    不要去找不存在的 Kotlin 符号；实现落点仍是 `标`。`[真机]` 标记不豁免实现，
    仅表示行为断言由 verify 设备实测。

  【第二段：差异清单】（complexity=complex 时强制）
  对比源码摘要与 feature spec，列出 spec 没写的隐式逻辑:

    ### Spec Gap List
    - <差异 1>: spec 没写但源码里有的逻辑（含触发条件 + 代码引用）
    - <差异 2>: ...

    差异清单为空 → 输出 \"无差异\"。

  【第三段：ViewModel 实现】（必选）
  1. 创建 ViewModel class
     （complex）状态机分支必须对齐【第一段】的「状态机」总结
  2. 定义 @Local / @Param / @Event 回调 状态变量
  3. 实现 UI 事件处理方法
     （complex）事件处理必须覆盖【第一段】列出的全部异常分支
  4. 将 UI 组件事件绑定到 ViewModel 方法

  输出（除代码外）:
  - 主响应: 上述三段（complex）或仅第三段（simple）
  - 主代码: entry/src/main/ets/viewmodels/{SliceName}ViewModel.ets
  - 副产物（complex 强制）: 写 spec/execution/source-understanding/{slice_name}-source-notes.md
    内容 = 第二段差异清单（spec 已有 5-role 摘要时不复制摘要——单一权威源；spec 无摘要时才含第一段）

  验收（HARD-GATE）:
  - complex: 响应必须含完整三段 + source-notes.md 必须存在 + ViewModel 语法自检通过（编译由 group-closer 统一跑）
  - simple: ViewModel 语法自检通过（编译由 group-closer 统一跑）+ UI 事件绑定完整
  - 任何 role 摘要中无具体 Kotlin 类名 / 方法名 → WORKER FAIL（脚本反查校验）
```

**响应模板约束**：worker 在 prompt 中受三段式格式强约束，独立 Step 3.0 派发 agent 被合并入此 prompt，节省 ~30-50 min 启动开销。

**反向回灌机制**：source-notes.md 中「差异清单」非空时，由 a2h-retrospect（不在本方案范围）或人工**反向追加到 feature spec 的 § 隐式契约章节**。下一轮迁移同类 feature 时 spec 已含这些隐式逻辑。本方案**不强制自动回灌**，差异清单的可信度由 worker grep 反查保证，最终决定仍需人工 review。
