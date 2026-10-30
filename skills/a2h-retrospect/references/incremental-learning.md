<!-- when: a2h-execute 编译检查点后触发增量学习（§5），或需要 retrospect-counter.json schema 时加载 -->
<!-- topics: 增量学习, 编译修复 pattern 累计, retrospect-counter.json, 自动晋升 count≥3 -->

# 增量学习模式

`a2h-execute` 编译检查点后可选触发增量学习，无需等到完整 retrospect。

## 触发方式

`a2h-execute` 编译检查点后可选触发增量学习，无需等到完整 retrospect。

## 增量分析流程

```
编译修复完成
  │
  ├─ Step 1: 读取本次修复日志
  │   从 hmos-fix-build-errors 的修复记录中提取新 pattern
  │
  ├─ Step 2: 对比已有 references
  │   读取 known-patterns.md / api-corrections.md / verified-symbols.md
  │   │
  │   ├─ 已知模式 → 跳过（可选更新频次）
  │   ├─ 新模式 + 累计 ≥ 3 次 → 自动写入对应 reference
  │   └─ 新模式 + 累计 < 3 次 → 记录到计数器文件
  │
  └─ Step 3: 更新计数器
      写入 spec/retrospect-counter.json
```

## 临时计数文件

路径：`spec/retrospect-counter.json`

```json
{
  "last_updated": "2026-03-27T14:30:00Z",
  "pending_patterns": [
    {
      "id": "pattern-unique-id",
      "target_skill": "hmos-fix-build-errors",
      "target_file": "references/known-patterns.md",
      "error_signature": "错误特征描述",
      "fix_summary": "修复方案摘要",
      "count": 2,
      "first_seen": "2026-03-27",
      "last_seen": "2026-03-27",
      "examples": [
        { "file": "path/to/file.ets", "line": 42, "date": "2026-03-27" }
      ]
    }
  ]
}
```

## 自动晋升

当 `pending_patterns` 中某条记录的 `count` 达到 3：

1. 自动从 `pending_patterns` 中移除
2. 写入对应 skill 的 references 文件
3. 在回顾报告中记录 `AUTO_PROMOTED` 状态
