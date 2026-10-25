# `spec/fix/round-N/<layer>/<id>.md` 文件模板

> 用法：verifier 写每个失败问题文件时，照此骨架填空。`{...}` 是占位符。
> Schema 完整定义见 `fix-file-schema.md`。

> **⚠️ v2 重要变更（已应用）**：
> - 移除 `kind: SYSTEMIC` 枚举值 + `_systemic/SYSTEMIC_*.md` 子目录约定
> - 移除 frontmatter 字段 `systemic_root` 和 `affects`
> - 移除 `disposition: problematic`（原回滚标记）
>
> 下方模板示例可能仍含旧语法，**新生成的文件**应严格按 §3 §4 §5 表格里 v2 简化后的字段写。**示例 D（systemic 跨 Feature 根因）已废除**，不要再产生此类文件。

---

## 模板（复制粘贴用）

```markdown
---
id: {id}
title: {一句话标题，≤ 60 字符}

source: {dt-verifier | visual-verify | manual}
layer: {feat | ui}
kind: {RED | ERROR | IMPL_MISSING | UNREACHABLE | ALIGNMENT_DIFF | SYSTEMIC}
severity: {P0 | P1 | P2}
fixer_layer: {feat | ui}

suggested_files:
  - {仓内相对路径 1}
  - {仓内相对路径 2}

related: []
systemic_root: {null | spec/fix/round-N/feat/_systemic/SYSTEMIC_xxx.md}
affects: []

evidence:
  - {日志/截图/dump 路径，带行号}

disposition: null
disposition_reason: null
disposition_set_at_round: null
---

# {title}

## 1. Spec 引用
> {原文直引，≤ 5 行}

来源: {spec/baseline/...路径}

## 2. 期望
{期望行为/视觉}

## 3. 实际
{实际行为/视觉/日志首行}

## 4. 源码缺口
- {file}:{line} — {缺口描述}

## 5. 修复建议
1. {步骤 1，动词开头}
2. {步骤 2}

```

---

## 三种典型来源的填法示例

### 示例 A：dt-verifier 单元测试 RED

`spec/fix/round-0/feat/F010_AC03_deleteFiles_useRecycleBin.md`

```markdown
---
id: F010_AC03_deleteFiles_useRecycleBin
title: deleteFiles 必须支持 useRecycleBin 分支

source: dt-verifier
layer: feat
kind: RED
severity: P0
fixer_layer: feat

suggested_files:
  - entry/src/main/ets/viewmodels/FileOperationsViewModel.ets
  - entry/src/main/ets/services/FileSystemService.ets

related: []
systemic_root: null
affects: []

evidence:
  - docs/autofix-log/round-0/raw-log.txt:1245

disposition: null
disposition_reason: null
disposition_set_at_round: null
---

# deleteFiles 必须支持 useRecycleBin 分支

## 1. Spec 引用
> 当 useRecycleBin = true 时，删除文件改为移动到 ~/.recycle/，被回收的文件可被恢复。

来源: spec/baseline/features/F010_FileOps.md §3.2

## 2. 期望
expect(result.deletedCount).assertEqual(1) && expect(result.recycled).assertTrue()

## 3. 实际
result.deletedCount = 0; result.recycled = undefined

## 4. 源码缺口
- entry/src/main/ets/viewmodels/FileOperationsViewModel.ets:30-48 — deleteFiles 永远走 fs.unlink，没 useRecycleBin 分支
- entry/src/main/ets/services/FileSystemService.ets — 缺 moveToRecycleBin(path) 方法

## 5. 修复建议
1. 在 FileSystemService 新增 moveToRecycleBin(path)，调用 photoAccessHelper.deleteAssets API
2. 在 FileOperationsViewModel.deleteFiles 加 useRecycleBin 分支：true → moveToRecycleBin；false → fs.unlink
3. 返回值补 recycled: boolean 字段

```

### 示例 B：dt-verifier UI 测试 ERROR

`spec/fix/round-0/ui/P0010_UI_INTERACT_row_open_dialog.md`

```markdown
---
id: P0010_UI_INTERACT_row_open_dialog
title: SettingsPage 行点击应弹出 Dialog

source: dt-verifier
layer: ui
kind: ERROR
severity: P0
fixer_layer: ui

suggested_files:
  - entry/src/main/ets/pages/SettingsPage.ets

related: []
systemic_root: null
affects: []

evidence:
  - docs/autofix-log/round-0/raw-log.txt:3422

disposition: null
disposition_reason: null
disposition_set_at_round: null
---

# SettingsPage 行点击应弹出 Dialog

## 1. Spec 引用
> 设置项点击后弹出对应 Dialog（FontDialog / TtsSettingDialog 等）

来源: spec/baseline/ui/page_0010_SettingsPage.md §交互行为

## 2. 期望
.click('settings_font_row') → Dialog 出现 → driver.findComponent(...) 命中

## 3. 实际
ERROR: timeout 5000ms; CustomDialogController 未触发

## 4. 源码缺口
- entry/src/main/ets/pages/SettingsPage.ets:88 — Row 缺 onClick handler
- entry/src/main/ets/pages/SettingsPage.ets:120 — fontDialogController 未在 build() 内初始化

## 5. 修复建议
1. 在 SettingsPage 顶部初始化 `fontDialogController = new CustomDialogController({builder: FontDialog(...)})`
2. Row 加 `.onClick(() => fontDialogController.open())`
3. 同步给 Row 加 `.id('settings_font_row')`，更新 testable-id-manifest.md

```

### 示例 C：visual-verify 视觉对齐

`spec/fix/round-0/ui/ALIGN_P0002_color_drift.md`

```markdown
---
id: ALIGN_P0002_color_drift
title: 主页深色模式背景色偏亮

source: visual-verify
layer: ui
kind: ALIGNMENT_DIFF
severity: P1
fixer_layer: ui

suggested_files:
  - entry/src/main/ets/utils/ThemeColors.ets
  - entry/src/main/ets/pages/MainPage.ets

related: []
systemic_root: null
affects: []

evidence:
  - spec/baseline/ui/page_0002/screenshot_dark.png
  - docs/visual-verify/round-0/P0002_actual.png

disposition: null
disposition_reason: null
disposition_set_at_round: null
---

# 主页深色模式背景色偏亮

## 1. Spec 引用
> 主页深色模式背景应为 #1A1A1A，主文字 #E0E0E0

来源: spec/baseline/ui/page_0002.md §视觉规格

## 2. 期望
- 背景: #1A1A1A
- 主文字: #E0E0E0
- 截图: spec/baseline/ui/page_0002/screenshot_dark.png

## 3. 实际
- 背景: #2A2A2A（偏亮 16 单位）
- 主文字: #FFFFFF（对比度过高）
- 截图: docs/visual-verify/round-0/P0002_actual.png

## 4. 源码缺口
- entry/src/main/ets/utils/ThemeColors.ets:14 — DARK_BG 错写为 #2A2A2A
- entry/src/main/ets/pages/MainPage.ets:88 — Text color 硬编码 #FFFFFF，未走主题资源

## 5. 修复建议
1. 修正 ThemeColors.DARK_BG = #1A1A1A
2. MainPage Text 颜色换成 $r('app.color.text_primary')
3. 在 resources/dark/element/color.json 补 text_primary = #E0E0E0

```

### 示例 D：systemic 跨 Feature 根因

`spec/fix/round-0/feat/_systemic/SYSTEMIC_db-init-context-failure.md`

```markdown
---
id: SYSTEMIC_db-init-context-failure
title: 数据库初始化时 Context 缺失，连环遮蔽 12 条 RED

source: dt-verifier
layer: feat
kind: SYSTEMIC
severity: P0
fixer_layer: feat

suggested_files:
  - entry/src/main/ets/database/GalleryDatabase.ets

related: []
systemic_root: null
affects:
  - feat/F005_AC01_db_init.md
  - feat/F012_AC01_savedPage_create.md
  - feat/F010_AC01_listFiles_returns_array.md
  - feat/F010_AC02_listFiles_with_filter.md
  - feat/F010_AC03_deleteFiles_useRecycleBin.md
  - feat/F010_AC05_deleteFiles_dirPath.md
  - feat/F018_AC01_domainConfig_load.md
  - feat/F018_AC02_domainConfig_persist.md
  - feat/F019_AC01_translationCache_set.md
  - feat/F019_AC02_translationCache_get.md
  - feat/F020_AC01_chatGptQuery_save.md
  - feat/F020_AC02_chatGptQuery_list.md

evidence:
  - docs/autofix-log/round-0/raw-log.txt:88
  - docs/autofix-log/round-0/raw-log.txt:120

disposition: null
disposition_reason: null
disposition_set_at_round: null
---

# 数据库初始化时 Context 缺失，连环遮蔽 12 条 RED

## 1. Spec 引用
> 所有 Repository / Service 需通过 RDB 持久化数据；测试环境应能注入 abilityContext。

来源: spec/baseline/feature-base.md §数据模型

## 2. 期望
GalleryDatabase.init() 在测试环境下成功初始化，使 Repository 方法的 mock 期望可触达。

## 3. 实际
12 条 unit AC 全部 ERROR：`TypeError: Cannot read property 'getContext' of undefined`，
栈首均指向 `GalleryDatabase.init(GalleryDatabase.ets:82)`。

## 4. 源码缺口
- entry/src/main/ets/database/GalleryDatabase.ets:82-97 — init 依赖 AppStorage.get('abilityContext')，测试环境未预置
- entry/src/main/ets/database/GalleryDatabase.ets — 无 abilityContext fallback

## 5. 修复建议
1. GalleryDatabase.init 添加 fallback：当 AppStorage.get('abilityContext') 为 undefined 时，
   尝试 getContext(this) 兜底（生产 + 测试通用）
2. 修完后 12 条 affected AC 应在下轮 verifier 重跑后批量转 GREEN

```

---

## 写文件时的注意点

1. **YAML 严格**：缩进用空格（不用 tab）；列表项 `  - xxx` 顶格 2 空格 + 短横线 + 空格
2. **null vs []**：单值字段用 `null`；列表字段用 `[]`（即使 `affects: []` 也要显式写）
3. **路径格式**：仓内相对路径，开头**不加** `./` 或 `/`
4. **行号**：`<file>:<line>` 或 `<file>:<start>-<end>`；区段长度 ≤ 30 行
5. **section 标题严格**：`## 1. Spec 引用` 等数字编号 + 中文标题，**不可省略数字**
6. **不写历史尝试 section**：跨轮历史靠 round 目录序列承载（git diff round-N round-N+1 + `docs/autofix-log/round-N/{batch,fixer-summary,rollback}.md`）
