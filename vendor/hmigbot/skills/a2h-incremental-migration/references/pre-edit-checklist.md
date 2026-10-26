# §S2.5 Pre-Edit 机械核查关卡（references 详细版）

主 SKILL.md §S2.5 的详细执行手册。**动代码前必跑**。

## 1. 适用对象

§S2 用户（或 override 授权）确认差异清单后、任何 `Edit/Write` 动作前，对**每一条**要实施的差异跑以下四步。

**任一步失败** → 该条**不得**进入实施，降级为"待人工复核"回 §S2 清单末尾。

## 2. 四步机械核查

### S2.5.1 目标文件完整阅读（主代理亲自做）

- 主代理用 `Read` 打开本条差异 `expected_files` 每一个文件，读**完整内容**（>2000 行时分段读）
- 禁止仅用 `grep` 代替阅读
- 记录 `target_files_read: [{file, line_count}]` 到实施 log

### S2.5.2 Spec 反查（§3.5 Step B 的执行期复用）

```bash
HMOS={hmos_project}
for file in expected_files:
    grep -rn "$(basename $file .ets)" $HMOS/spec/
```

- 列出每个目标文件在 spec/ 下的被引用位置 → `existing_spec_refs: [{spec_file, line, snippet}]`
- 若 `existing_spec_refs` 非空，主代理必须读对应 spec 片段，判断本次改动是否会破坏已签收 spec 条目
- 判定会破坏 → 降级，回 §S2 补说明后让用户单独裁定

### S2.5.3 同义词扫描（§3.5.5 的执行期复用）

- 用本差异 §M2.2.x `hmos_synonyms` 已跑过的关键词**复跑一遍**（防止识别→实施之间 HMOS 有变更）
- 所有关键词仍为 0 命中才允许继续
- 出现 ≥1 命中 → 降级为"待人工复核"

### S2.5.4 改动完成后的 git diff 自审

每条差异实施完（每组 Edit/Write 闭合后）立即执行：

```bash
cd {hmos_project}
git diff --name-only
git diff --stat
```

- 实际改动文件集合必须是 `expected_files` 的**子集**
- 越界 → 立即停下来报告：

```
⚠ scope 越界：本条差异 expected_files={...}，但实际改动了 {extra_files}。
   请人工裁定：批准追加 / 回滚越界改动 / 终止本条。
```

- 未批准前不得进入下一条

## 3. 执行期日志要求

每条差异走完四步后，主代理必须产出一行实施记录到 `spec/incremental-migration-{date}/exec-log.md`：

```
[{timestamp}] diff #{n} "{title}"
  target_files_read: [...]
  existing_spec_refs: [...]
  reverse_scan_hits: 0
  scope_audit: PASS | EXTRA: [...]
  result: IMPLEMENTED | DEFERRED(reason) | ROLLED_BACK(reason)
```

§S4 完成摘要必须汇总本 log，让用户在最终报告里能逐条看到"每条差异的机械核查轨迹"。
