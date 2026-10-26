<!-- when: 产出 Batch / Base / Slice brief 文档（§3b / §4e / §5e）时加载 -->
<!-- topics: brief schema, Batch brief, Base Task brief, Slice brief, loops 段, final_state -->

# a2h-execute brief 文档 schema

> 由 `a2h-execute/SKILL.md` 的 §3b / §4e / §5e 引用。本文件收三类 brief 的 markdown 模板 + 字段读取来源；HARD-GATE 规则（何时强制产出、缺失如何阻断、BLOCKED 判定）留在 SKILL.md 对应章节。

a2h-execute 三阶段各产一类 brief，统一落 `spec/execution/briefs/`：

| brief | 产出时机 | SKILL.md 章节 |
|---|---|---|
| Batch brief | Stage 1 每个 Batch 结算后（批内无编译，统一编译在 execute §3d 收口） | §3b |
| Base Task brief | Stage 2 每个 Base 任务（Base-1..7）完成后 | §4e |
| Group brief | Stage 3 每个 parallel_group 收尾（§5e）后——组粒度单文件，per-slice 小节 | §5e |

---

## 0. 跨 brief 通用：`loops` 段 + `final_state`（Phase 2 引入）

每个 brief 必含 `final_state` + `loops` 两个 top-level 字段，由 [`arkts-structural-closure`](../../arkts-structural-closure/SKILL.md) skill 的运行结果填入（含 compile_loop + structural_loop 两部分）。

**`final_state` 枚举**：

| 值 | 含义 | 下游影响 |
|---|---|---|
| `PASS` | compile + structural 两个 loop 都 CONVERGED | 正常进入下一单元 |
| `ESCALATED` | structural_loop 返回 STALLED / EXHAUSTED | 标记 + pipeline 继续；§5f 末尾若 ESCALATED 总数 > 10% → 阻断进 a2h-verify |
| `ROLLED_BACK` | structural_loop 返回 REGRESSED | git stash 本单元改动；阻断所有 `depends_on` 本单元的下游 |
| `BLOCKED` | placeholder / source-notes / deferred_items 校验 FAIL（不走 loop） | Slice 标 BLOCKED，要求人工补 plan |

**`loops` 段格式**（YAML，由 `structural_loop.py finalize` + 子代理 `hmos-builder` 收尾时输出）：

```yaml
loops:
  compile:
    iterations: 3
    converged: true
    final_errors: 0

  structural:                          # 由 structural_loop.py finalize 直接产出
    iterations: 4
    converged: true
    final_state: PASS                  # PASS | ESCALATED | ROLLED_BACK
    final_audit_fail: 0
    final_wiring_repair_actions: 0
    verdict: CONVERGED                 # CONVERGED | CONTINUE | STALLED | REGRESSED | EXHAUSTED
    escalation: NONE                   # NONE | MANUAL | ROLLED_BACK
    reason: "all checks pass at iteration 3"
    history:
      - { iter: 0, audit_fail: 0, wiring_repair_actions: 7,  brief_escape_hatches: 0 }
      - { iter: 1, audit_fail: 0, wiring_repair_actions: 3,  brief_escape_hatches: 0 }
      - { iter: 2, audit_fail: 1, wiring_repair_actions: 1,  brief_escape_hatches: 0 }
      - { iter: 3, audit_fail: 0, wiring_repair_actions: 0,  brief_escape_hatches: 0 }
```

**`escalation` 段**（仅 final_state ≠ PASS 时填）：

```yaml
escalation:
  category: structural_loop_stalled    # 或 _regressed / _exhausted
  unresolved_findings: <spec/execution/autofix-log/round-N/audit-X-iterY.json + wiring-X-iterY.json 路径>
  recommended_human_action: |
    上一轮 structural_loop 在第 N 轮停滞，verify_slice_wiring.py C2 仍报 3 个
    integration_point evidence 违规。建议检查 spec/baseline/features/F-xxx.md
    的「## 对接点」段是否描述格式正确（含 `<handler> ← <target>` 箭头）。
```

> 旧字段 `unresolved_placeholders` / `unregistered_skeletons` / `resource_dependencies_unresolved` 已废弃——loops.structural 段已含其所有信息（structural_loop 既扫骨架也校接线，state 文件持有完整 history）。如旧版 brief 仍含这些段，可读但不再要求新版 brief 写出。

---

## 1. Batch brief（§3b）

落点：`spec/execution/briefs/batch_NN_brief.md`

````markdown
# Batch NN Brief
- 完成时间: YYYY-MM-DD HH:mm
- final_state: PASS | BLOCKED          # PASS = 结算完成（资源 sweep + manifest）

## generated_pages
| 页面 | 状态 | 行数 |
|------|------|------|
| MainPage | converted | 245 |

## next_batch_prerequisites
- 前一 Batch manifest 已 apply
- 跨 Batch 间的 placeholder / resource 状态从 spec/placeholder-registry.md 与 resource-mapping.md 取
````

（批内无编译 → 无 loops / escalation 段；Stage 1 末的审计 + single-pass 由 execute §3d 主线程执行，结果入统计不入 batch brief）

读取来源：
- `generated_pages` 列：从 ui-manifest.md 本 Batch status: converted 的页面

---

## 2. Base Task brief（§4e）

落点：`spec/execution/briefs/base_NN_brief.md`

````markdown
# Base NN Brief: <任务名>
- 完成时间: YYYY-MM-DD HH:mm
- final_state: PASS | ESCALATED | ROLLED_BACK
- 编译状态: PASS / PARTIAL / FAILED / N/A（Base-1..6 通常 N/A，仅 Base-7 必含）

## generated_files
| 文件路径 | 类型 | 行数 |
|---------|------|------|
| entry/src/main/ets/models/UserBean.ets | model | 45 |

## modified_files
| 文件路径 | 改动摘要 |
|---------|---------|
| entry/src/main/resources/base/element/string.json | 追加 12 个字符串资源 |

## loops
（见 §0；Stage 2 末尾 Base-7 处含完整 compile + structural；Base-1..6 仅含本 Base 任务的 compile loop，structural 由 Stage 2 末尾跑）

## escalation
（仅 final_state ≠ PASS 时填，见 §0）

## evidence
- commit hash / file:line / spec anchor 列表（完成性凭据唯一落点——plan 产物零回填、无 evidence 槽）

## next_dependency
- 下一个 Base 任务名 / 或 "Stage 3 启动条件就绪"
````

读取来源：
- `generated_files` / `modified_files`：worker agent 报告 + git diff 自动汇总
- `loops`：本 Base 任务的 compile_loop + Stage 末尾 structural_loop（Base-7 处）
- `evidence`：worker 报告（commit / file:line；plan 无 evidence 槽）

---

## 3. Group brief（§5e，Stage 3 组粒度单文件）

落点：`spec/execution/briefs/group_NN_brief.md`——**任意组大小含 size-1 组**（串行降级 / 重试单 slice 同样按组文件写，slices 单元素）。由 **group-closer 唯一起草**（brief 全文进 writeback manifest `brief.content`，经 `apply_writeback.py` 落盘，见 §4——作者唯一 = closer，脚本只是落盘手）；ESCALATED 单 slice 重跑**只更新对应小节**（重跑 closer 读旧 brief 改该小节后给全文）。

**机器契约**：per-slice 小节头 = `## Slice N (F-xxx)`（deferral_policy / verify_closure_ledger 按小节切分归属 final_state 与 deferred_items；首个小节之前为组共享头部，不参与逐 slice 判定）；小节内延迟台账用 `### deferred_items`。

````markdown
# Group NN Brief
- group_id: N | slices: [Slice X, Slice Y] | 完成时间: YYYY-MM-DD HH:mm
- build_status: PASS | FAIL（+ iterations）           # 组共享，只写一次
- structural_verdict: CONVERGED | ESCALATED | deferred-to-FV（仅末组）  # 组共享
- wired_shared_files: [...]                           # 组级跨文件接线改动清单
- resolved_fwd_refs_group: [P-S{N}-..., ...]          # 本组解除的 forward-ref（收组清行对应）

## loops
（§0 格式；compile + structural 均为**组共享**结果，只写一次——各 slice 小节不复制）

## escalation
（仅 structural_verdict ≠ CONVERGED 时填，见 §0）

## Slice X (F-xxx)
- final_state: PASS | ESCALATED | ROLLED_BACK | BLOCKED
- step_3a_ui_supplement: generated_files / status_changes（page_NNNN pending → converted）
- step_3b_viewmodel: generated_files / source_notes_path（complex 必含，缺失 → BLOCKED）
- step_3c_data_layer: generated_files
- step_3d_wiring: wired_files / integration_points_done: n/n / resolved_fwd_refs（本 slice）
- cross_slice_edits: | file | handler | 原 owning_slice | 落地 evidence | 表（有则填）
- unresolved_placeholders: [...]（本 slice 前缀 grep registry 的残余）
- pages_verified: [...]（供 a2h-verify CHECK-5 核验）

### deferred_items
| 描述 | owner_skill | 闭环条件 | status |
|------|-------------|---------|--------|

## Slice Y (F-yyy)
（同上结构）
````

读取来源：头部 = group-closer 自身结果（build / structural / 共享文件改动 / 收组清行）；各小节 `step_3a/3b/3c` = 该 slice worker 报告；`step_3d` 跨文件部分 = group-closer 步骤 1；`loops` 组共享一份（各小节引用同一次，不复制）；per-slice 串行旧形态（`slice_NN_brief.md` 整文件）为 legacy 兜底，消费脚本双形态解析。

---

## 4. Writeback manifest（四模式通用，closer 唯一账本出口）

**原理**：closer 前四步改代码（落盘即持久），账本变更（registry 翻转/清行/retag、ui-manifest / feature-index 状态翻转、brief 落盘）100% 可从结果推导——不该在 20 分钟长 turn 尾巴上由 LLM 手写。closer **turn 内一律不 Edit 账本**，全部变更记入一份 manifest 一次 Write，由主线程跑 `a2h-execute/scripts/apply_writeback.py` 确定性落盘（幂等可重放；**崩溃恢复 = 重跑 apply，绝不重做接线/编译/结构**）。**唯一例外 = 新占位登记**（P-ID 发号 append-only，build-loop 即时消费，照旧直写）。

落点：`spec/execution/writeback/writeback-<mode>-<id>.json`（如 `writeback-group-03.json` / `writeback-batch-02.json` / `writeback-base-05.json` / `writeback-final.json`）。

```json
{
  "mode": "group",                        // group | batch | base | final
  "id": "03",
  "registry": {
    "resolve": ["P-S1-001", "P-S2-001"],  // kind=forward-ref → 删行（收组清行，历史留 brief）；其他 kind → status→resolved
    "retag": [{"pid": "P-S6-004", "column": "resolve_by", "value": "D-003（忠实占位·永久保留）"}]
  },
  "ui_manifest": {"converted": ["0040"], "verified": ["0001", "0002"]},   // 键 = 序号
  "feature_index": {"implemented": ["F001"]},                             // 键 = F-ID
  "impl_claims": {                        // AC 级认领（modes: group/final；batch 无 AC 归属不产）
    "claims": [{"requirement_id": "F001-AC01", "packet_id": "slice-03-F001",
                "files": ["entry/src/main/ets/pages/HomePage.ets"],
                "requirement_digest": "sha256:…", "attempt": 1}],          // symbols 可选
    "executed_packets": ["slice-03-F001"]
  },
  "brief": {"path": "spec/execution/briefs/group_03_brief.md", "content": "<brief 完整 markdown，schema 见 §1–§3>"}
}
```

各段可省（mode=base 通常仅 `brief`）；`ui_manifest.verified` / `feature_index.implemented` 只在双前置成立（编译 PASS ∧ 结构 CONVERGED）时记入；defer 末组（`structural_verdict: deferred-to-FV`）不记这两段，由 mode=final 的 manifest 补翻。`impl_claims` 同守双前置；`requirement_ids`/`requirement_digests` **抄自 plan-coverage.json 对应 packet，不由 LLM 手写**；落盘幂等键 = `(requirement_id, packet_id, attempt)`（apply_writeback.py §5，重跑 apply 不重复）。
