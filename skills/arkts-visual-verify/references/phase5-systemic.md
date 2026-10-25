# Phase 5 — 跨 batch systemic 聚类

> 从 SKILL.md §4 Phase 5 抽出。所有 batch sub-agent 完成、Phase 6 之前 Read。
>
> **目的**：sub-agent 在自己的 batch 内做了"类内 systemic"聚类（≥3 页同模式），但**跨 batch** 的全局模式（例如「9 个 batch 共 12 页都缺 NavHeaderBar」）只有主会话能看全。这一步在 Phase 6 之前跑，纯文本不读图。

---

## Step 4.5.a 收集所有 manifest 的 findings

```python
import json, glob
findings = []        # 跨 batch 所有 ALIGN/CRASH 的细粒度记录
for mf in glob.glob("spec/visual-verify/batches/*/manifest.json"):
    m = json.load(open(mf))
    for f in m["findings"]:
        # f 包含 page_id, kind, category_pattern, severity, fix_file
        findings.append(f | {"batch_id": m["batch_id"]})
```

每条 finding 必含 `category_pattern` 字段（由 sub-agent 在写 ALIGN 时同步写入 manifest），用于聚类。常见 pattern：
- `missing_navheader` / `nav_titlebar_layout_drift`
- `padding_top_hardcoded` / `padding_left_hardcoded`
- `font_weight_bold_misuse`
- `tab_order_drift`
- `image_resource_missing` / `image_fallback_white_bg`
- `lazyforeach_used` / `componentv1_decorator_used`
- `webview_url_mismatch`

---

## Step 4.5.b 聚类规则

```python
from collections import defaultdict
buckets = defaultdict(list)
for f in findings:
    if f["kind"] != "ALIGNMENT_DIFF": continue
    if f.get("folded_into"): continue   # B.4.5 同页对账已把它 fold 进 feat 单（文件已 rm），不重复计/聚类
    buckets[f["category_pattern"]].append(f)

cross_batch_systemic = []
for pattern, items in buckets.items():
    batches_hit = set(i["batch_id"] for i in items)
    pages_hit   = set(i["page_id"] for i in items)
    if len(batches_hit) >= 2 and len(pages_hit) >= 3:
        cross_batch_systemic.append({
            "pattern": pattern,
            "pages": sorted(pages_hit),
            "batches": sorted(batches_hit),
            "evidence_fix_files": [i["fix_file"] for i in items],
        })
```


### 4.5.b-2 blocked 根因必跑 wiring-gap 判据（**强制**）

上面的聚类只看 `ALIGNMENT_DIFF`。**blocked 页同样要聚类**——按"根因文案"分桶：

```python
blocked_buckets = defaultdict(list)
for f in findings:
    if f.get("status") != "blocked": continue
    key = f.get("disposition_reason") or f.get("not_migration_evidence") or ""
    blocked_buckets[normalize(key)].append(f)   # 归一化：去页名/数字，留根因骨架
```

任一桶 **≥2 页** 且根因形如「XX 未配置 / 未就绪 / 暂不可用 / 等后端 / provider 不可用」
→ **必须先跑 [`wiring-gap-detection.md`](wiring-gap-detection.md) §2 的三步判据**，再决定定性：

- 装配入口调用点 = 0 → **实现缺口**，出一张 SYSTEMIC 根因单（`kind=IMPL_MISSING`、
  `severity=P0`、`is_migration_bug=true`），受影响页挂 `affects[]`；**不得整桶标 noop**
- 调用点存在但运行期条件不满足 → 维持 blocked，但 `not_migration_evidence` 必须写明调用点行号

> **禁止**：把一整桶 blocked 直接归成"上游未就绪"而不跑判据。真实事故里
> 一个未接线的 `installApiClient()` 曾让 6 个 service、十余个页面集体假 blocked，
> 且骗过编译/占位符/页面状态/功能验收全部既有闸。

---

## Step 4.5.c 写 cross-batch SYSTEMIC markdown

每条 `cross_batch_systemic` 写一份 `spec/fix/round-N/ui/_systemic/SYSTEMIC_{pattern}.md`，schema 按 [`fix-file-schema.md`](fix-file-schema.md) `kind: SYSTEMIC`：

```yaml
---
id: SYSTEMIC_{pattern}
kind: SYSTEMIC
severity: P0          # 跨 ≥2 batch 默认 P0
affects: ["P0001", "P0007", "P0011", ...]   # 全部命中 page_id
fixer_layer: ui
suggested_files: [...]   # 取所有命中 ALIGN 的 suggested_files 并集
related: [...]           # 所有命中 ALIGN 的相对路径
...
---
```

并在每条命中的 ALIGN markdown 里**回填 systemic_root** 字段：
```python
for ali in items["evidence_fix_files"]:
    patch_frontmatter(ali, {"systemic_root": f"spec/fix/round-{N}/ui/_systemic/SYSTEMIC_{pattern}.md"})
```

---

## Step 4.5.d 不要重复写类内 SYSTEMIC

sub-agent 在 batch 内已经写过 `SYSTEMIC_{batch_id}_{pattern}.md`（局部）。如果同 pattern 在 Phase 5 升级为跨 batch SYSTEMIC：
- 局部 SYSTEMIC 改名加 `_local` 后缀，或者直接合并到跨 batch SYSTEMIC（合并时把 affects 取并集）
- 避免一个 pattern 出现两份 SYSTEMIC 干扰 fixer
