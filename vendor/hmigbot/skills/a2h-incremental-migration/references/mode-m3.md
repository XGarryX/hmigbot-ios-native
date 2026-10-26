# §M3 Targeted 模式 — 详细执行手册

主 SKILL.md §M3 卡片的详细执行手册。**当用户给出具体功能锚点（功能名 / 类名 / id / "只迁移 XX"）时使用本模式。**

## 核心方法论

锚点 → A_CLOSURE → H_TARGETS → scope-locked 实施。

## 主流程图

```
§M3.1 grep 关键词
   ↓
A_CLOSURE 是否为空？
   │
   ├─ 非空 → §M3.2 H_TARGETS 映射（正常迁移路径）
   │           ↓
   │        （回归范围派生由通用 §SR 处理）
   │           ↓
   │        §M3.3 scope-lock 实施
   │           ↓
   │        §M3.4 改动审计
   │           ↓
   │        §S2 用户对齐 → §S3 委托 evolver 走 create+plan+execute+verify
   │
   └─ 空 → §M3.1.1 硬闸门，向用户三选一：
            ├─ (a) 换关键词重试 §M3.1（≤3 轮，超限强制走 (c)）
            ├─ (b) Android 无实现 → 委托 arkts-spec-evolver 走 V2 新功能
            │        ↑ 委托时 android_behavior_trace=null
            │          spec context 标注"无 Android 参考实现，纯 HMOS 新增"
            │          evolver Gate 1 摘要顶部显示该标签供审批
            └─ (c) 取消同步（流程结束，无任何代码改动）
```

**关键原则**：
- A_CLOSURE 空 = 没有 Android 行为轨迹可同步 → **绝对不得**让 LLM 凭用户描述脑补 Android 实现
- (b) 路径不退回到 §M2 / §M1（它们也需要 Android 有实现），而是主动跨 skill 委托给 spec-evolver
- 整个分流对用户无感：选 (b) 后用户在 evolver Gate 1 看到的是熟悉的 spec 摘要审批界面，仅多一行"无 Android 参考"标签

## M3.1 功能定位（keyword closure，不做全量扫描）

> ⚠ 死代码过滤（必跑）：`grep` 命中后必须用 Python 剥离注释再判，**只命中注释**视为 0 命中，走 §M3.1.1 硬闸门。详见 references/dead-code-filter.md

```bash
KW="上传作品"    # 或 "tv_upload_item" / "UserItemsStore"
grep -rlE "$KW|uploadItem|UserItemsStore" {android_dir}/app/src/main/ > /tmp/a_files.txt
cat /tmp/a_files.txt
```

读每个命中文件，做 1-2 层依赖递归，得 **A_CLOSURE**：

```
本轮 Targeted scope — A_CLOSURE（12 文件）：
  UI       fragment_items.xml（FAB + 相关 id）
  Logic    ItemsFragment.kt（openImagePicker / mergeItems / upload）
  Store    UserItemsStore.kt
  String   strings.xml 新增 key: upload_work / upload_success / upload_failed
  Drawable icon_upload_work.png / icon_local_doc.png
请确认闭包是否完整？
```

用户确认 A_CLOSURE 前**不得开始写代码**。

### M3.1.1 Android 端无对应实现的硬闸门（必跑）

`grep` 0 命中 / A_CLOSURE 实际为空时，**绝对不得**让 LLM 凭用户描述脑补一个 Android 实现。必须停下来向用户确认：

```
⚠ Android 侧未找到对应实现
  搜索关键词：{KW + 派生别名}
  扫描结果：0 命中
  扫描范围：{android_dir}/app/src/main/

  可能原因，请用户确认（回复 a/b/c）：

  (a) 关键词错了 / 命名不一致
      → 请补充候选关键词重试 §M3.1（如 "WorksFragment / tv_upload / btnUpload" 等）

  (b) Android 也没做 → 你想直接在 HMOS 新建该功能
      → 本 skill 终止当前流程，改委托给 arkts-spec-evolver 的 create+plan+execute+verify
        作为 V2 新功能处理（spec source: 用户主动新增，非 Android 同步）

  (c) 取消本次同步（功能记错了 / 不在本项目范围）
      → 流程结束，无任何代码改动
```

**硬性约束**：
- 用户回复 (a/b/c) 前禁止进入 §M3.2 H_TARGETS 映射
- 选 (b) → 本 skill 显式调用 arkts-spec-evolver，传 payload 时 `android_behavior_trace` 字段必须填 `null`，并在 spec context 里标注"无 Android 参考实现，纯 HMOS 新增"，让 evolver Gate 1 审批时用户能看到这个标记
- 选 (a) 重试时如果 3 轮后 A_CLOSURE 仍为空 → 强制按 (c) 处理，避免无限重试

**必须补一步**：A_CLOSURE 非空时，跑 §3.5 HMOS Spec 双重验证——若 `spec/baseline/features/` 或 `spec/features/F-*.md` 已描述该功能，向用户复核"是否为已实现功能的扩展/修改"，避免重复新建 spec。把 H_TARGETS 每个文件在 spec 里承载的既有功能列出来，供 §M3.3 scope-lock 边界校验。

## M3.2 目标映射（H_TARGETS，scope lock）

| A_CLOSURE | H_TARGETS |
|---|---|
| Fragment/Activity | `.ets` 页面（改或新建）|
| Store/Service/Dialog | `services/*.ets` / `components/dialog/*.ets` |
| layout XML | `.ets` 的 UI 段 |
| strings.xml key | `resources/base/element/string.json` |
| drawable/mipmap | `resources/base/media/` |
| 权限 | `module.json5`（查 §4.3） |

显式输出 H_TARGETS 清单，**这就是 scope lock**。

## M3.3 Scope lock 实施规则

- **允许**：改/建 H_TARGETS 内文件
- **禁止**：改 H_TARGETS 之外文件；"顺便"修 bug / 重命名 / 重构 / 格式化；触碰无关 import/装饰器声明（@State/@Local/@Param/@Provider 等任一）/注释
- **越界处理**：发现必须改 H_TARGETS 之外文件时，**立即停下来**问用户：
  ```
  ⚠ scope 越界请示：需修改 {file}（原因：...），批准后追加到 H_TARGETS。
  ```
- 每个改动必须说明对应 A_CLOSURE 哪一项。

## M3.4 改动审计

```bash
cd {hmos_project}
git diff --name-only > /tmp/actual.txt
comm -23 /tmp/actual.txt /tmp/h_targets.txt   # 越界清单
```

越界清单非空 → 逐条说明；未批准的 `git checkout` 回滚。

→ 进 §S2 用户对齐（Targeted 模式下 §S2 更轻，主要确认 A_CLOSURE / H_TARGETS）。
