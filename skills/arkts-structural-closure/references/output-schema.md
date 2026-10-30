# structural-closure 输出 JSON schema 速查

> 从 SKILL.md §5 下沉。SKILL.md 通过 MUST-read 指针引用本文件。


### 5.1 audit_skeletons.py 输出

```json
{
  "scope": "stage|slice|all",
  "summary": { "L1": N, "L2": N, "L3": N, "L4": N, "FAIL": N, "WARN": N, "handoff_escape_hatches": N },
  "findings": [
    {
      "level": "L3",
      "subtype": "fake-content",
      "file": "pages/X.ets",
      "line": 42,
      "match": "<excerpt>",
      "suggested_action": "<action>",
      "severity_at_scope": "FAIL"
    }
  ],
  "handoff_escape_hatches": [ ... ]
}
```

### 5.2 verify_slice_wiring.py 输出

```json
{
  "slice_id": N,
  "categories": {
    "C1_orphan_check":      { "pass": N, "fail": N, "details": [...] },
    "C2_integration_point": { "pass": N, "fail": N, "details": [...] },
    "C3_cross_slice":       { "pass": N, "fail": N, "details": [...] },
    "C4_parent_replacement":{ "pass": N, "fail": N, "details": [...] }
  },
  "overall": "PASS|BLOCKED",
  "repair_actions": [
    {
      "id": "C2_ip_001",
      "category": "C2_integration_point",
      "failed_check": "C2_NO_EVIDENCE",
      "current_state": "<state>",
      "suggested_action": "<action>",
      "file": "<path>"
    }
  ]
}
```

### 5.2b orphans（pipeline 模式 `_run_pipeline_orphans` 输出）

```json
{
  "vm_candidates": N, "component_candidates": N,
  "orphan_count": N,                 // 保留的真孤儿数（进 fingerprint / 驱动循环）
  "orphans": [
    { "file": "...", "class_name": "X",
      "reason": "NO_IMPORTER|IMPORTED_BUT_NOT_INSTANTIATED|ONLY_INSTANTIATED_BY_NON_UI" }
  ],
  "exempted_count": N,               // 检测器盲区豁免数（不进 fingerprint / 不驱动循环）
  "exempted": [
    { "file": "...", "class_name": "X", "reason": "...",
      "exempt_evidence": "supertype|static-access|own-file-use|typed-ref:<file>" }
  ]
}
```

> `exempted` = 有"非 `new` 使用"正面证据的误报（`ref_graph_lib.usage_evidence()` 判定，逐条带证据、可审计回放）；**零证据者留在 `orphans` 仍为 FAIL**（fail-tight，真孤儿绝不豁免）。

### 5.3 structural_loop iterate 输出（含 dispatch_prompt）

```json
{
  "mode": "slice|pipeline",
  "target": "<N|final>",
  "iteration": N,
  "verdict": "CONVERGED|CONTINUE|STALLED|REGRESSED|EXHAUSTED",
  "escalation": "NONE|MANUAL|ROLLED_BACK",
  "reason": "<why>",
  "current_state": { "audit_fail": N, "wiring_repair_actions": N, "handoff_escape_hatches": N, "total_fail": N },
  "dispatch_prompt": "<追加给 repair worker 的整段 prompt>",
  "detector_json_paths": { "audit": "...", "wiring": "...", "orphans": "...", "immersive": "..." },
  "state_file": "<path>"
}
```

### 5.4 structural_loop finalize 输出（嵌入 brief loops.structural 段）

```json
{
  "iterations": N,
  "converged": true|false,
  "final_state": "PASS|ESCALATED|ROLLED_BACK",
  "final_audit_fail": N,
  "final_wiring_repair_actions": N,
  "verdict": "<last>",
  "escalation": "<mode>",
  "history": [...]
}
```

---
