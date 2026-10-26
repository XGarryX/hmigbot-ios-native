<!-- when: 派发 Stage 2/3 通用 worker（a2h-migration-worker，Base 层任务）时加载本段 + _common.md -->
<!-- topics: Stage 2/3 通用 worker prompt, Base 层任务, 占位规则 -->

# §3. Stage 2/3 通用 worker prompt（a2h-migration-worker）

> 公共占位规则 §2.1 见 [`_common.md`](./_common.md)，派发时一并 Read。

派发 Codex 子代理 `a2h-migration-worker`（定义于 `.codex/agents/a2h-migration-worker.toml`），任务提示词：

```
你正在执行 Android→HarmonyOS 迁移 Base 层任务（执行时序 Phase 0）。

  任务: {task_name}
  描述: {task_description}
  详细信息: {task_details}

  使用 Skill: {suggested_skills}   ← 每个 skill 以 `$<name>` 形式显式调用（领域 skill 未开隐式路由，裸名不会自动加载）
  输入来源: {task_input_source}
  输出位置: {task_output_path}

  Android 源码路径: {android_source_dir}
  HarmonyOS 项目路径: {harmony_project_dir}

  验收标准:
  {task_acceptance_criteria}

  占位规则：合法占位的 marker 形态与 kind 枚举权威定义在
  `a2h-plan/templates/placeholder-registry-template.md`。Base worker 阶段常用 kind:
  - `forward-ref`：Base signature 桩（如 `throw ApiException(...)`），登记 `resolve_by=Slice {N} Step 3c`
  - `thirdparty-sdk`：三方 SDK 占位 + 白名单 trigger_condition
  - `resource-pending-asset`：fallback 资产 + `trigger=<resource-id> 就绪`
  所有占位 6 字段齐全；其余写法（自由 TODO 注释 / console.info('TODO:...') / 空回调 / 资源 value 含未登记 [TODO:...]）一律禁止。
```
