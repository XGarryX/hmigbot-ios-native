# `spec/fix/round-N/ui/<id>.md` 文件模板

`arkts-ui-verifier` 的 execute 步骤写每个失败 UI 测试问题文件时，照此骨架填空。`{...}` 是占位符。Schema 完整定义见 `fix-file-schema.md`。

## 模板（复制粘贴用）

```markdown
---
id: {id}
title: {一句话标题，≤ 60 字}

source: arkts-ui-verifier
layer: ui
kind: {RED | ERROR | IMPL_MISSING | UNREACHABLE}
severity: {P0 | P1 | P2}

suggested_files:
  - {仓内相对路径 1}
  - {仓内相对路径 2}

related: []

evidence:
  - {日志/dump 路径，带行号}

disposition: null
disposition_reason: null
disposition_set_at_round: null
---

# {title}

## 1. Spec 引用
> {原文直引，≤ 5 行}

来源: {spec/baseline/ui/page_00xx.md §节标题} 或 {spec/baseline/features/F00x.md §AC{n}}

## 2. 期望
- **意图层**：{`assertComponentExist(ON.id(...))` / `getText()==...` / `isChecked()==...`}
- **状态层**：{`AppStorage.get<T>('key')==value` 或 `@State` 绑定值}

## 3. 实际
- 意图层：{定位失败 / 控件特征实测值 / 日志原文首行}
- 状态层：{`AppStorage.get('key')` 实测值；含 `undefined` 表示 key 未建}

## 4. 源码缺口
- {file}:{line} — {缺口描述；含缺 onClick / AppStorage 状态键 / `.id()` 锚点等}

## 5. 修复建议
1. {步骤 1，动词开头}
2. {步骤 2}
```

## 填法示例：UI 测试 ERROR（含双重断言）

`spec/fix/round-0/ui/P0010_UI_INTERACT_row_open_dialog.md`

```markdown
---
id: P0010_UI_INTERACT_row_open_dialog
title: SettingsPage 行点击应弹出 Dialog 且 dialogVisible 状态翻转

source: arkts-ui-verifier
layer: ui
kind: ERROR
severity: P0

suggested_files:
  - entry/src/main/ets/pages/SettingsPage.ets

related: []

evidence:
  - /tmp/ui-run.log:3422

disposition: null
disposition_reason: null
disposition_set_at_round: null
---

# SettingsPage 行点击应弹出 Dialog 且 dialogVisible 状态翻转

## 1. Spec 引用
> 设置项点击后弹出对应 Dialog（FontDialog / TtsSettingDialog 等）

来源: spec/baseline/ui/page_0010_SettingsPage.md §交互行为

## 2. 期望
- **意图层**：.click('settings_font_row') → `assertComponentExist(ON.id('font_dialog'))`
- **状态层**：`AppStorage.get<boolean>('fontDialogVisible') == true`

## 3. 实际
- 意图层 ERROR: timeout 5000ms; CustomDialogController 未触发
- 状态层: `AppStorage.get('fontDialogVisible') == undefined`（key 都没建）

## 4. 源码缺口
- entry/src/main/ets/pages/SettingsPage.ets:88 — Row 缺 onClick handler
- entry/src/main/ets/pages/SettingsPage.ets:120 — fontDialogController 未在 build() 内初始化
- entry/src/main/ets/pages/SettingsPage.ets — `fontDialogVisible` AppStorage key 未声明

## 5. 修复建议
1. 在 SettingsPage 顶部初始化 `fontDialogController = new CustomDialogController({builder: FontDialog(...)})`
2. Row 加 `.onClick(() => { fontDialogController.open(); AppStorage.setOrCreate('fontDialogVisible', true) })`
3. 同步给 Row 加 `.id('settings_font_row')`，更新 testable-id-manifest.md
```

## 写文件时的注意点

1. **YAML 严格**：缩进用空格（不用 tab）；列表项 `  - xxx` 顶格 2 空格 + 短横线 + 空格
2. **null vs []**：单值字段用 `null`；列表字段用 `[]`（即使 `related: []` 也要显式写）
3. **路径格式**：仓内相对路径，开头**不加** `./` 或 `/`
4. **行号**：`<file>:<line>` 或 `<file>:<start>-<end>`；区段长度 ≤ 30 行
5. **section 标题严格**：`## 1. Spec 引用` 等数字编号 + 中文标题，**不可省略数字**
6. **不写"历史尝试" section**：跨轮历史靠 round 目录序列 + `fixer-summary-ui.md` 承载
7. **双重断言**：「期望」「实际」分别写出意图层 + 状态层（与 test-design-template.md 标准 3 一致）；纯渲染 SMOKE 无对应状态键时，「期望」「实际」备注"仅意图层 + 原因"
