<!-- when: Phase A 调用确定性脚本生成 meta.json 骨架 / 合成 view.xml 时加载 -->
<!-- topics: synthesize_meta_json, synthesize_view_xml, scaffold 模式, enrich 模式, 合成 view.xml 特征 -->

# Phase A 确定性脚本调用

Phase A 用 android-ui-graph-builder 的两个脚本做确定性提取：`synthesize_meta_json.py`（scaffold 生骨架 / enrich 补字段）与 `synthesize_view_xml.py`（无 UIAutomator dump 时从 layout XML 合成 view.xml）。

## Step A2a 确定性骨架生成（scaffold 模式）

对每个 Activity/Fragment，先运行确定性脚本生成 meta.json 骨架：

```bash
python3 .agents/skills/android-ui-graph-builder/scripts/synthesize_meta_json.py \
  $ANDROID_SRC \
  --activity {fully_qualified_class_name} \
  --page-id {page_id} \
  --output spec/baseline/ui-snapshots/{page_dir}/meta.json \
  --mode scaffold \
  --package {package}
```

脚本自动提取：`layout_sources`、`menu_sources`、`fragment_tags`、`style_sources`、`recycler_item_layouts`、`navigation_targets`。LLM 需补充的字段以默认占位值标记（`label=""`、`confidence="medium"`、`dynamic_menus={}`、`navigation_mode="UNKNOWN"` 等）。

## Step A3 合成 view.xml（无 UIAutomator dump 时）

1. 确认 meta.json 中 `layout_sources` 已填充（来自 Step A2 分析结果）
2. 调用合成脚本：
   ```bash
   python3 .agents/skills/android-ui-graph-builder/scripts/synthesize_view_xml.py \
     $ANDROID_SRC \
     --layouts "{meta.json.layout_sources 逗号拼接}" \
     --menus "{meta.json.menu_sources 逗号拼接}" \
     --resolve-strings \
     --resolve-styles \
     --output spec/baseline/ui-snapshots/page_NNNN_XxxActivity/view.xml \
     --package {AndroidManifest 中的 package 属性}
   ```
3. 脚本输出结果处理：
   - 成功 → 在 meta.json 中标记 `"view_xml_synthesized": true`，confidence 维持 `medium`
   - 失败 → confidence 降为 `low`，meta.json 标记 `"view_xml_synthesized": false`，记录失败原因，不阻塞后续 Phase
4. view.xml 合成后，运行 enrich 模式补充 `clickable_elements`（从 view.xml 提取）：
   ```bash
   python3 .agents/skills/android-ui-graph-builder/scripts/synthesize_meta_json.py \
     $ANDROID_SRC \
     --activity {fully_qualified_class_name} \
     --page-id {page_id} \
     --output spec/baseline/ui-snapshots/{page_dir}/meta.json \
     --mode enrich \
     --existing spec/baseline/ui-snapshots/{page_dir}/meta.json \
     --view-xml spec/baseline/ui-snapshots/{page_dir}/view.xml \
     --package {package}
   ```

合成版 view.xml 特征：
- 根元素 `<hierarchy synthesized="true">` 标识为合成版
- `bounds` 属性始终为空（无运行时坐标数据）
- `class` 为全限定类名，`resource-id` 为 `{package}:id/{name}` 格式
- `clickable`/`enabled`/`scrollable` 等从 XML 属性取值，无则用 Android 默认值
- 递归处理 `<include>` 和 `<merge>` 标签


## extract_visibility_bindings.py（显隐绑定真值账，Phase A 收尾必跑）

```bash
python3 <a2h-spec>/scripts/extract_visibility_bindings.py \
    --android-root <ANDROID_ROOT> \
    --output spec/baseline/ui/visibility-bindings.json
```

从安卓源抽取全部条件显隐绑定（Kotlin/Java `.visibility/.isVisible =` 赋值 + XML
初始 gone），产出闭集真值账供 execute worker 逐条核销、structural-closure
binding_gate 机械对账。治「绑定链断裂」类缺陷（实录：「我的」页 showServiceCenter
零赋值 × fail-closed 默认 → 服务中心四按钮整块蒸发；CC 版同病但默认极性侥幸忠实）。