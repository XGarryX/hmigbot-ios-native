<!-- when: a2h-spec 派发 subagent 时加载（§3.0 选项 A 派发 a2h-android-analyzer / Step B0 派发 android-api-inventory）-->
<!-- topics: a2h-android-analyzer 派发 prompt, android-api-inventory 派发 prompt, 后台并行子 agent, summary 字段, 分支 C 输入源模式 -->

# a2h-spec 派发的 subagent prompt

a2h-spec 主线程在两处派发 subagent，完整派发 prompt 在此。

## a2h-android-analyzer（§3.0 选项 A：自动生成参考文档）

用户在 3.0 前置选「自动生成参考文档」时派发：

```
Agent(
  子代理 `a2h-android-analyzer`
  prompt: "分析 Android 项目并生成参考文档。
    android_source_dir: $ANDROID_SRC
    output_dir: spec/ref/
    project_name: {从 AndroidManifest 提取的 package 短名}"
)
```

等待完成后，记录 `$REF_SPEC` 和 `$REF_DESIGN` 路径，继续 Phase A。

## android-api-inventory（Step 3.0c3 预派发；Step B0 兜底）

**3.0c2 一结束（Step 3.0c3）即派发**后台子 agent——它只需 `$ANDROID_SRC`（+ 此刻已定的两个可选
文件参数），不依赖 Phase 0/A/B 任何产物，是全管线最长单体子任务，提前起跑可把墙钟完全藏进
Phase 0/A + B-UI。若 3.0c3 被跳过，Step B0 兜底补派发（prompt 相同）：

```
Agent(
  子代理 `a2h-migration-worker`
  run_in_background: true,
  model: "sonnet",            # 机械 API 枚举（endpoints / services / base_urls 结构化抽取，低创造性），无需强模型；抽取完整性由下游 feature-coverage L3 覆盖脚本反查兜底。不用 haiku：API 漏抽对漏迁影响大，sonnet 完整性/成本最佳。语义判定（a2h-android-analyzer / grill D-decision / ring contract）仍保留强模型。
  prompt: "执行 android-api-inventory skill，对 Android 源码做外部 API 清单提取。
    platform: android           # 显式固定为 android（a2h-spec 永远以此模式调用本 skill，详见 android-api-inventory 契约段）
    android_source_dir: $ANDROID_SRC
    输出目录: spec/baseline/api-inventory/
    hmos_references_file: $HMOS_REFS_FILE  # 仅当 Step 3.0c 产出 spec/ref/hmos-references.md 时传入；为 null 则忽略（此时 Phase 2.5 整段跳过）
    backend_facts_file: $BACKEND_FACTS_FILE  # v1.3：仅当 Step 3.0c2 产出 spec/ref/backend-facts.md 时传入；为 null 则忽略（uncertainties 全部以 open 状态产出，不预销账）
    当前 spec/baseline/features/ 与 feature-index.md 均未生成 → Phase 4 走【分支 C — 输入源模式】。
    完成后返回 summary（5 个字段）：
      - services_count: number
      - endpoints_count: number
      - feature_candidates_count: number
      - coverage_mode: 'audit' | 'incremental' | 'candidate' | 'degraded'
      - hmos_hint_section_present: boolean  # Phase 2.5 等价物提示段是否落到 api-inventory.md（hmos_references_file 为空或文件不存在时为 false）"
)
```

记录子 agent 句柄为 `$API_INVENTORY_JOB`，主线继续 B-UI 轨（Step B1）。

> **降级**：若环境不支持后台子 agent，退化为「B-UI 轨全部完成后、Step B-join 处前台串行调用一次 android-api-inventory」——丢失并行收益但功能等价。

## auth-chain-probe（Step B-probe：登录链路活性探针并行轨）

B-join 确认 `data-chains/chain-auth.md` 落盘 + `spec/baseline/dev_info.json` 就位后即派发，与 Gate B 审批 + Phase C 的 C1–C4 并行；**前置齐即跑，不询问用户是否要跑**（前置缺才建 `U-ENV`/`U-ACCOUNT` 留给 grill，见 `grill-1-decision-gates.md` §C4.7b）：

```
Agent(
  子代理 `a2h-migration-worker`
  run_in_background: true,
  prompt: "执行 arkts-network-troubleshoot 场景 E（auth-chain 活性探针），验证登录链路能否真打通。
    MUST 读: references/probe-runbook.md（循环骨架 + 错误三分类 + 候选来源约定 + 上限 N=10 跳过）
           + references/probe-error-remediation.md（错误→修法知识库）
    只读输入: spec/baseline/api-inventory/data-chains/chain-auth.md（靶点 + 公参字段的值来源）
             spec/baseline/dev_info.json（测试 base_url + 业务成功码 + 测试账号）
             scripts/verify-sign.js（复用项目已复现的签名实现）

    【并行安全约束 —— 你与 Phase C 的 spec 生成并行运行，违反即产生读写竞态】
    1. 循环期全程只读：禁写任何 spec 产物（chain-auth / uncertainties / golden 一律不落盘）。
    2. 发现缓冲在返回值：结论、试出的真值、golden 请求响应、待补 KB 条目，全部作为返回值带回。
    3. 落盘由主线程在 C4.7b join 后统一执行；你不执行任何写操作。

    完成后返回 summary：
      - verdict: 'PASS' | 'BLOCKED' | 'EXHAUSTED' | 'UNKNOWN'
      - endpoint: 命中的靶点
      - resolved_values: 循环试出的能通值（版本 / baseType / 渠道 / 指纹等）
      - golden: 成功那次的 请求/响应/签名输入串（PASS 时必填，供主线程落 chain-auth.golden.json）
      - blockers: 后端侧 / 人输(MISSING-TRUTH) 类断点（供冒泡 grill）
      - tried_candidates: 试过的候选（EXHAUSTED 时必填）
      - new_kb_entries: 本轮撞到的新『错误→修法』模式（供追加知识库）"
)
```

记录句柄为 `$AUTH_PROBE_JOB`，主线继续 Gate B → Phase C；Step C4.7b `join` 后由**主线程**一次性落盘（存 golden + 回填真值 + `uncertainties[]` append + RED→GREEN 重投影）。

> **降级**：不支持后台子 agent → 不在此派发，由 Step C4.7b 前台串行跑同一循环（串行路径无并发写，上述只读约束不适用）。**非登录项目**（无 auth 链 / 无 chain-auth）不派发。
