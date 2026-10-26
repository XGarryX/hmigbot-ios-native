# Stage A 产物质量检查清单（sub-agent prompt）

> 给 sub-agent 用的**只读检查清单**。sub-agent 不应修复，只产报告。
> 主代理收到报告后自行决定是否修 / 重跑哪一步。

---

## 你的任务

读取 `{project_root}/intermediate/` + `{project_root}/agent_bundle.v1.json`，逐项核对下表，给每条标 `PASS` / `FAIL` / `UNKNOWN`，最后输出**结构化 JSON 报告**。

**不要修文件、不要重跑命令、不要给修复建议之外的判断**。你的唯一任务是检查 + 报告。

---

## 检查项（逐条核对）

### [FILE-EXISTS] 14 个核心文件存在

```
intermediate/0_android_facts/
├── manifest.json
├── navigation_graph.json
├── navigation_candidates.json
├── ground_truth.json
├── static_xml.json
├── source_findings.json
├── function_symbols.json
├── call_graph.json
├── ui_dag.json
├── ui_paths.json
├── ui_paths_legacy.json
├── ui_paths_enumerated.json
├── ui_paths_coverage_report.json
└── ui_effect_paths.json
intermediate/1_android_facts/android_facts.v1.json
intermediate/2_framework_map/framework_map.v1.json
intermediate/3_harmony_arch/harmony_arch.v1.json
intermediate/5_feature_tree/feature_tree.v1.json
agent_bundle.v1.json
```

任一缺失 → FAIL。

### [FILE-SIZE] 关键文件最小尺寸

| 文件 | 最小字节 | 失败含义 |
|---|---|---|
| `ui_paths.json` | > 100 | 空 `[]` 意味着 UI path 枚举塌了 |
| `ui_paths_legacy.json` | > 100 | 同上 |
| `ui_dag.json` | > 500 | 空桩通常 < 500B |
| `ui_paths_enumerated.json` paths 数组长度 | > 5 | 只有 2-3 条通常意味着 BFS 第二跳就死 |
| `navigation_graph.json` | > 5000 | 异常小通常没解到 source files |
| `agent_bundle.v1.json` | > 10000 | bundle 输出残缺 |

任一不达标 → FAIL。

### [FIELD] 关键字段非空

| 文件 | 字段路径 | 失败含义 |
|---|---|---|
| `1_android_facts/android_facts.v1.json` | `manifest.launcher_activity_qualified` 非空 | launcher 解析失败 → 下游全 cascade |
| `1_android_facts/android_facts.v1.json` | `manifest.package` 非空 | manifest 没读到（AGP 7+ namespace 未兜底）|
| `0_android_facts/ui_dag.json` | `screen_class` 非空 | UI DAG 起点没匹配上类名 |
| `0_android_facts/ui_paths_coverage_report.json` | `launcher_class` 非空 | 同上 |
| `0_android_facts/ui_paths_coverage_report.json` | `screen_total > 0` | screens 列表空 |

任一为空 / 0 / null → FAIL。

### [CONSISTENCY] 数据一致性

| 检查 | 阈值 | 失败含义 |
|---|---|---|
| `navigation_graph.json` 的 `edges` 自循环比例（`from == to`）| < 50% | 大量自循环意味着 toolkit 解不出 Class 参数，认输打 marker |
| `navigation_graph.json` 的 `type=activity` 边里跨 Activity 真边数 | ≥ 5 | 一个非空项目至少 5 条真跳转 |
| `ui_paths_enumerated.json` 的 leaf_class 是否含 ≥ 3 个真实 Activity（非 *Dialog / 非 $内部类） | ≥ 3 | 全停在弹窗说明只走了第一跳 |

任一阈值不过 → FAIL。

### [SCHEMA-AGREEMENT] toolkit_to_fact_tree_draft.py 入参契约

| 检查 | 失败含义 |
|---|---|
| `agent_bundle.v1.json` 含 `intermediate_manifest.artifacts` | bundle 没正确打包 |
| `agent_bundle.v1.json` 含 `outline.app` 且 `app.application_id` 或 `app.namespace` 非空 | 应用元信息全空 |

---

## 输出格式

**必须**返回这个 JSON 结构（不要写散文，不要写 markdown）：

```json
{
  "verdict": "PASS" | "FAIL",
  "checks": [
    {
      "id": "FILE-EXISTS",
      "status": "PASS" | "FAIL" | "UNKNOWN",
      "detail": "string，可省略"
    },
    {
      "id": "FILE-SIZE",
      "status": "FAIL",
      "detail": "ui_paths.json = 3 bytes (expected > 100)；ui_paths_legacy.json = 3 bytes"
    }
    // ...
  ],
  "failed_files": ["intermediate/0_android_facts/ui_paths.json", "..."],
  "root_cause_hint": "string — 你的最佳归因猜测，例如：launcher_class 空，怀疑 main.py 拿到的 android_root 是错的相对路径。如果不确定写 'unknown'。"
}
```

字段说明：
- `verdict`: 任一 FAIL → 整体 FAIL
- `checks`: 每条检查的状态
- `failed_files`: 涉及的产物文件路径
- `root_cause_hint`: **只是猜测**，不是结论。主代理可以采纳或推翻。

---

## 禁止做的事

- ❌ 修文件
- ❌ 跑任何命令（除了 `wc -c` / `head` / `jq` 等读取命令）
- ❌ 假定通过（"看起来 OK" 不是 PASS，必须实测）
- ❌ 跳过检查项（每条都要给 status）
- ❌ 写无关分析（路径推荐、修复方案、未来优化都不要）
