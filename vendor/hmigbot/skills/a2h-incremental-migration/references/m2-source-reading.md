# §M2.2 LLM 源码并排阅读（references 详细版）

主 SKILL.md §M2.2 的详细执行手册。Source-compare 模式的主扫描路径。

## 1. 并排阅读流程

对每对配对页面，LLM 按以下顺序阅读并生成"行为轨迹清单"：

**1. Android 侧**：读 layout XML + 对应 Fragment/Activity.kt
- 提取用户可触及的交互入口：按钮 / FAB / 菜单项 / Tab / 列表项点击 / 下拉刷新 / 滑动删除 / 长按
- 对每个入口追 `setOnClickListener` / `onMenuItemClick` → handler 方法 → 调用到的 store/service
- 形成行为轨迹：`{控件} → {触发} → {数据调用} → {UI 反馈}`

**2. HMOS 侧**：读对应 `.ets` 的 `build()` + `aboutToAppear` + `onClick` handler
- 同样提取交互入口和行为轨迹

**3. 对齐**：两份轨迹清单逐条对比
- Android 有、HMOS 无此入口 → 🔴
- 入口都在但 handler 缺步骤（例：Android 弹对话框 + 埋点 + 接口，HMOS 只弹对话框）→ 🟠
- 完全对齐 → ✅（列为透明度证据）

**严禁**仅比对 layout id 集合或 onClick 字面量集合（§1.1 已禁的符号差集方法）。**必须**阅读实际行为。

**必须补一步**：HMOS 行为轨迹得出后，跑 §3.5 的 HMOS Spec 双重验证——用 `spec/baseline/` 和 `spec/features/` 校准"HMOS 端这条行为是否已签收"，避免把 spec 已定义但源码恰好未命中关键词的功能误判为 🔴。

## 2. 每条差异必带的 5 个证据字段（硬性）

子代理/主代理产出每条 🔴/🟠 时，**必须**同时提交以下 5 字段。缺任一 → 该条自动降级 `confidence: low`，进 §S2"待验证桶"而非直接进 🔴/🟠：

| 字段 | 要求 | 作用 |
|------|------|------|
| `android_trace` | `{file}:{line-range}` + 3 句行为描述 | 证明 Android 行为读过 |
| `hmos_read` | `{file}:{line-range}` + 目标页面 `build()` / `onClick` 前 20 行片段摘要 | 证明 HMOS 目标页面**真读过**，不是仅 grep |
| `hmos_synonyms` | ≥3 个同义关键词 + 每个 grep stdout。来源：**中文文案**（按钮文字/Toast/对话框标题） / **同义动词**（save/export/download、upload/publish、refresh/reload、delete/remove） / **图标或资源 id**（icon_save / ic_download）/ **路由 url 片段**（pages/XxxPage）。**禁止**用 Android 方法名/类名作关键词 | 防命名差异假阳性 |
| `hmos_spec_status` | ❌未提及 / ✅已签收 / ⚠部分定义 / ⚠spec与代码不一致（§3.5 Step A 产出）| spec 层校准 |
| `confidence` | `high` / `medium` / `low`。默认 `low`，只有上面 4 项齐全且 `hmos_synonyms` 全部空命中才可升 `high` | 分层置信度 |

## 3. 子代理返回格式样例（进入 🔴 的最小完备单元）

```yaml
- title: 作品页批量上传
  android_trace:
    file: app/src/main/java/com/.../ItemsFragment.kt
    lines: 120-180
    behavior: "FAB tv_upload_item.click → PhotoViewPicker → POST /api/items/batch-upload → 列表刷新"
  hmos_read:
    file: entry/src/main/ets/pages/MainPage.ets
    lines: 785-1050   # ItemsView 的 build() + 所有 onClick 已逐行读完
    summary: "ItemsView 仅有单条 FAB（本地 DocumentViewPicker），无 batch 上传分支；toolbar 仅 delete。"
  hmos_synonyms:
    - keyword: "批量上传"
      grep_result: "(no matches)"
    - keyword: "batch-upload"
      grep_result: "(no matches)"
    - keyword: "icon_upload_batch"
      grep_result: "(no matches)"
    - keyword: "多选上传"
      grep_result: "(no matches)"
  hmos_spec_status: "❌未提及"
  confidence: high
  bucket: 🔴
```

## 4. 主代理验收规则

收到子代理报告后，对每条 `confidence: high` 的 🔴 **抽样 20%** 做主代理亲自复核：
- Read 对应 `hmos_read.file` 的指定行范围
- 重跑 `hmos_synonyms` 里的 grep

复核不通过 → **全部 🔴 回炉重做**。

## 5. 完整输出示例

```
配对：ItemsFragment.kt + fragment_items.xml  ↔  MainPage.ets (Items Tab)

Android 行为轨迹：
  1. FAB tv_upload_item.click → openImagePicker() → 相册多选 → POST /api/items/batch-upload → 刷新列表
  2. list item 长按 → 进入 isManageMode → 底部 Toolbar 显示"删除"
  3. Toolbar 删除 → 确认对话框 → POST /api/items/batch-delete → 移除项

HMOS 行为轨迹（从 MainPage.ets 的 Items Tab 段 + UserItemsStore.ets 提取）：
  1. [缺] 无上传 FAB 入口
  2. 长按 → isManageMode → Toolbar ✅
  3. Toolbar 删除 → AlertDialog → UserItemsStore.batchDelete ✅

差异：
  🔴 1 条：上传 FAB + 批量上传接口
```
