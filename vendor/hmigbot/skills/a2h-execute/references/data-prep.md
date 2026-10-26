<!-- when: Stage 1 每页派发前做三源数据完整性预检查时加载 -->
<!-- topics: 数据预检, synthesize_view_xml, synthesize_meta_json, enrich 模式, scaffold 模式 -->

# 数据完整性预检查脚本调用（§3a-pre）

**3 模式判定表**（对 Batch 中每个待转换页面 page_NNNN，派发 converter 前检查三源数据）：

| meta.json 状态 | view.xml 状态 | 处理 |
|---------------|-------------|------|
| ✓ 含 layout_sources | ✓ 存在 | `synthesize_meta_json.py --mode enrich` 补充缺失字段 → 派发 |
| ✓ 含 layout_sources | ✗ 缺失 | `synthesize_view_xml.py` 合成 → enrich → 派发 |
| ✗ 缺失或无 layout_sources | — | `synthesize_meta_json.py --mode scaffold` → Phase A 按需 → `synthesize_view_xml.py` → enrich → 派发 |

Batch 级批量执行；同一 Batch 内多个页面缺 view.xml 时可并行调用脚本合成。enrich 模式确保 `menu_sources` / `fragment_tags` / `recycler_item_layouts` 等字段完整，避免 LLM 遗漏。

> **路径约定**：`$SKILLS_ROOT` = 本套 skills 安装根（与 app-relationship-tree 等 skill 同约定），常见为 `.agents/skills/`。

补充合成 view.xml 的调用方式：
```bash
python3 $SKILLS_ROOT/android-ui-graph-builder/scripts/synthesize_view_xml.py \
  $ANDROID_SRC \
  --layouts "{meta.json.layout_sources 逗号拼接}" \
  --output spec/baseline/ui-snapshots/page_NNNN_XxxActivity/view.xml \
  --package {package}
```

补充/修正 meta.json 确定性字段的调用方式：
```bash
python3 $SKILLS_ROOT/android-ui-graph-builder/scripts/synthesize_meta_json.py \
  $ANDROID_SRC \
  --activity {fully_qualified_class_name} \
  --page-id {page_id} \
  --output spec/baseline/ui-snapshots/page_NNNN_XxxActivity/meta.json \
  --mode enrich \
  --existing spec/baseline/ui-snapshots/page_NNNN_XxxActivity/meta.json \
  --view-xml spec/baseline/ui-snapshots/page_NNNN_XxxActivity/view.xml \
  --package {package}
```

## spec 补齐留痕（HARD-GATE）

本节脚本会向 `spec/baseline/ui-snapshots/` **写入/修改 spec 域产物**——execute 补齐 spec 数据必须留痕，禁止静默补写。每个 Batch 跑完合成后，向 `spec/migration-report.md` 的「spec 数据补齐记录」段 append 一条（无该段则创建）：

```yaml
- kind: snapshot_synthesized          # 或 snapshot_enriched
  affected_pages: [page_0043, page_0051]
  tool: synthesize_view_xml / synthesize_meta_json --mode <enrich|scaffold>
  reason: <缺 view.xml / meta 无 layout_sources 等一句话>
```

Batch 级一条即可（列全页面），不逐页开条。此记录是上游 `spec_change_request`（a2h-pipeline/v2 §12）的 legacy 等价物：将来 `contract_mode=v2` 时，本路径改为写 `spec/.a2h/change-requests/SCR-*.json` 并阻断受影响单元，等待新 Release；当前 legacy 模式下补写照常放行，仅强制留痕。
