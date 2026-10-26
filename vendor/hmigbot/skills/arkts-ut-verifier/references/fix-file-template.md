# `spec/verify/ut/round-N/ut/<id>.md` 文件模板

`arkts-ut-verifier` 的 execute 步骤写每个失败问题文件时，照此骨架填空。`{...}` 是占位符。Schema 完整定义见 `fix-file-schema.md`。

## 模板（复制粘贴用）

```markdown
---
id: {id}
title: {一句话标题，≤ 60 字}

source: arkts-ut-verifier
layer: ut
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

来源: {spec/baseline/features/F00x.md §AC{n}}

## 2. 期望
{期望断言文本，如 `expect(result.deletedCount).assertEqual(1)`}

## 3. 实际
{运行返回值 / 错误首行}

## 4. 源码缺口
- {file}:{line} — {缺口描述}

## 5. 修复建议
1. {步骤 1，动词开头}
2. {步骤 2}
```

## 填法示例：单元测试 RED

`spec/verify/ut/round-0/ut/F010_AC03_deleteFiles_useRecycleBin.md`

```markdown
---
id: F010_AC03_deleteFiles_useRecycleBin
title: deleteFiles 必须支持 useRecycleBin 分支

source: arkts-ut-verifier
layer: ut
kind: RED
severity: P0

suggested_files:
  - entry/src/main/ets/viewmodels/FileOperationsViewModel.ets
  - entry/src/main/ets/services/FileSystemService.ets

related: []

evidence:
  - /tmp/ut-run.log:1245

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
- entry/src/main/ets/viewmodels/FileOperationsViewModel.ets:30-48 — deleteFiles 永远走 fs.unlink，无 useRecycleBin 分支
- entry/src/main/ets/services/FileSystemService.ets — 缺 moveToRecycleBin(path) 方法

## 5. 修复建议
1. 在 FileSystemService 新增 moveToRecycleBin(path)，调用 photoAccessHelper.deleteAssets API
2. 在 FileOperationsViewModel.deleteFiles 加 useRecycleBin 分支：true → moveToRecycleBin；false → fs.unlink
3. 返回值补 recycled: boolean 字段
```

## 写文件时的注意点

1. **YAML 严格**：缩进用空格（不用 tab）；列表项 `  - xxx` 顶格 2 空格 + 短横线 + 空格
2. **null vs []**：单值字段用 `null`；列表字段用 `[]`（即使 `related: []` 也要显式写）
3. **路径格式**：仓内相对路径，开头**不加** `./` 或 `/`
4. **行号**：`<file>:<line>` 或 `<file>:<start>-<end>`；区段长度 ≤ 30 行
5. **section 标题严格**：`## 1. Spec 引用` 等数字编号 + 中文标题，**不可省略数字**
6. **不写"历史尝试" section**：跨轮历史靠 round 目录序列 + `fixer-summary-ut.md` 承载
