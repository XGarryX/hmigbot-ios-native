<!-- when: 派发 Stage 3 Step 3c 数据层接入（a2h-migration-worker）时加载本段 + _common.md -->
<!-- topics: Step 3c 数据层接入 prompt, Repository, Service, 数据流闭环 -->

# §6. Stage 3 Step 3c 数据层接入 prompt（a2h-migration-worker）

> 公共占位规则 §2.1 + 单写者纪律见 [`_common.md`](./_common.md)，派发时一并 Read。

派发 Codex 子代理 `a2h-migration-worker`（定义于 `.codex/agents/a2h-migration-worker.toml`），任务提示词：

```
你正在执行 Feature Slice [{slice_name}] 的 Step 3c: 数据层接入。

  功能 Spec: {feature_spec_path}
  已有 Base 层: entry/src/main/ets/network/, entry/src/main/ets/database/, entry/src/main/ets/models/
  已有 ViewModel: {viewmodel_path}
  Slice 复杂度: {complexity}
  源码理解摘要: {source_notes_path}      # complex 时必传：spec/baseline/source-understanding/{slice_name}-source-notes.md；simple 时可空

  使用 `$arkts-data-layer` skill
  可调用的辅助 Skills（worker frontmatter 保留的 17 个之一）:
    - arkts-library-migration: 三方库映射（OkHttp→NetworkKit 等）
    - android-view-to-arkui: 类→类的迁移翻译

  任务:
  1. 按需创建 Repository / Service（复用 Base 层已有的公共能力）
     （complex）拦截器 / header 注入 / 加密链必须对齐 source-notes 的 role=interceptor 总结
     （complex）功能 Spec 的 AC 组带 impl: 指针且目标 addendum consumed_at 匹配 step-3c
     （api / persistence 等，缺省按 slug 默认表）→ 先按 _common.md「impl: 指针语义」精读
     目标 §节（≤3 节 / ≤150 行，超出记 deferred_addenda）；禁止整目录扫读 addenda
  2. 接入网络层（API 调用）或本地存储（DB / Preferences）
     （complex）所有通路必须独立实现，参考 source-notes 的 role=service 总结
  3. ViewModel 调用 Repository 获取数据
  4. 完成完整数据流: UI ← ViewModel ← Repository ← API/DB
  5. 处理数据转换和缓存策略

  多子仓约束（项目存在 module-dep-graph.json 时）:
  - 调用其它子仓的 service / 数据模型 → 签名与语义契约以 cross-module-contracts.md
    （被依赖子仓为 owner 的权威规约）+ module-dep-graph.json 接口桩为准，按契约实现，
    禁止在 slice 内就地发明；契约缺失 → 报告记「决策缺口」（主线程按 §1.1 阻断），不臆造。

  输出: entry/src/main/ets/repositories/{SliceName}Repository.ets（如需）
  验收: 数据流完整闭环；语法自检通过（编译由 group-closer 统一跑）。
```

**特殊领域追加 Skill**：当功能涉及特殊领域时，在 `arkts-data-layer` 基础上追加对应 Skill：
- 媒体播放功能 → 追加 `$arkts-media-playback`
- 文件下载功能 → 追加 `$arkts-download-manager`
- 系统权限功能 → 追加 `$arkts-system-capabilities`
