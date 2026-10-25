# CHECK-1 ~ CHECK-5 执行细则

> 配合 SKILL.md §3 验证清单使用。本文件给出 CHECK-1 到 CHECK-5 的完整执行步骤、判定逻辑。CHECK-6~7（路由 + 视觉 委托）见 `check6-to-7.md`。

---

## CHECK-1：全量编译修复

委托 `hmos-fix-build-errors`，自动循环最多 20 轮（**不传 `--signed`/`--unsigned`，走 skill 的 auto 探测**：签名齐全即出 signed HAP；skill 任何模式都不改 `build-profile.json5` 的签名段。CHECK-1 报告须转录其 `Build Type + reason`——若为 unsigned，CHECK-7 装机会失败，原因要在这里就写清，别等设备段才报 DEFERRED）：

```
hmos-fix-build-errors（最多 20 轮）
  │
  ├─ 编译通过 → CHECK-1: PASS
  │
  └─ 20 轮仍失败 → 升级:
      ├─ 调用 arkts-knowledge-verifier 诊断
      │   ├─ 诊断后修复 → PASS
      │   └─ 仍然无法修复 → CHECK-1: FAIL（记录剩余错误列表）
```

**编译 FAIL 的短路行为**（见 SKILL.md §3.0）：
- CHECK-1 FAIL **不再"放任后续全部照跑"**。静态项（CHECK-2~6）+ CHECK-6 路由（纯静态读源码）可继续；但**设备段 CHECK-7 本轮跳过**（编译不过无法 build HAP，跑了只会空转撞错），本轮直接进 §5 老路径修编译后重跑。
- §5 回环耗尽仍编不过 → 设备段标 `DEFERRED（编译未过）`。
- **终态复检**：CHECK-6 改完源码后，门控判定的 CHECK-1 取 §3.0 终态编译复检结果，不沿用本轮开头那次。

---

## CHECK-2：静态分析

对所有 `.ets` 文件执行以下 grep 检查：

| 检查项 | 命令 | 严重级别 |
|--------|------|---------|
| `any` 类型 | `grep -rn ": any\b" --include="*.ets"` | ERROR |
| 废弃导入 | `grep -rn "from '@ohos\." --include="*.ets"` | WARN |
| SQL 拼接 | `grep -rn "'\s*+\s*" --include="*.ets"` 在 SQL 上下文中 | ERROR |
| `as` 类型断言 | `grep -rn " as " --include="*.ets"` | WARN |
| `eval()` | `grep -rn "eval(" --include="*.ets"` | ERROR |
| aboutToAppear 参数获取 | `grep -rn "aboutToAppear" --include="*.ets"` 中含 `pathInfo` | ERROR |

**结果判定**（与 SKILL.md §6 门控对齐——只有 ERROR 级阻塞）：

- ERROR = 0 → CHECK-2: PASS（WARN > 0 时附 warnings 清单，不改变判定、不触发 §5 回环）
- ERROR > 0 → CHECK-2: FAIL（仅 ERROR 项生成回环修复任务；WARN 项随报告记录）

> WARN 项（如 ` as ` 断言、`@ohos.*` 旧导入）在迁移代码中存在大量合法用法，计入 FAIL 会让本 CHECK 恒失败、空转 §5 回环预算，而门控本就规定 WARN 不阻塞——因此 WARN 只记录不判负。

---

## CHECK-3：占位符扫描（必选）

两步扫描：

### Step 1: 结构化扫描

读取 `spec/placeholder-registry.md`：

- 统计 pending 状态的占位符数量
- 对每个 pending 条目，检查目标页面/功能是否已在代码中实现
- 已实现但未回填 → 标记为"可回填未回填"

### Step 2: 兜底扫描

grep 未注册的占位符：

- `grep -rn "TODO:" --include="*.ets" entry/src/`
- `grep -rn "console.info('TODO:" --include="*.ets" entry/src/`
- 对比注册表，找出未注册的占位符并补录到注册表

### 结果判定

- pending = 0 且无未注册项 → CHECK-3: PASS
- pending > 0 但均为 deferred（V2 范围外）→ CHECK-3: PASS（附 warnings）
- 存在可回填但未回填的项 → CHECK-3: FAIL

---

## CHECK-4：App 身份校验（必选）

验证 App 配置文件中的身份信息不是模板默认值：

```
App 身份校验规则:
  │
  ├─ 1. app.json5 的 bundleName 不匹配 "com.example.*"
  │     → 匹配则 FAIL: "bundleName 仍是模板默认值"
  │
  ├─ 2. app.json5 的 vendor 不等于 "example"
  │     → 等于则 FAIL: "vendor 仍是模板默认值"
  │
  ├─ 3. app.json5 的 versionName 不等于 "1.0.0"
  │     → 等于则 WARN: "versionName 可能未从 iOS 同步"
  │
  ├─ 4. string.json 的 app_name 与 Spec 记录一致（如果 feature-index.md 中有 App 名称定义）
  │     → 不一致则 FAIL: "app_name 与 Spec 不匹配"
  │
  ├─ 5. foreground.png / background.png 文件大小 > 1KB
  │     → ≤ 1KB 则 WARN: "图标文件疑似默认图"
  │
  └─ 6. layered_image.json 存在且引用 $media:background + $media:foreground
       → 缺失或引用错误则 FAIL: "自适应图标配置异常"
```

### 结果判定

- 0 FAIL + 0 WARN → CHECK-4: PASS
- 0 FAIL + N WARN → CHECK-4: PASS (附 warnings)
- 任何 FAIL → CHECK-4: FAIL

---

## CHECK-5：页面状态审计（必选）

检查 `spec/baseline/ui-manifest.md` 中所有页面的 status 字段，按优先级分组审计。

> **本 CHECK 审计"转换完成态"，不要求 `verified`**。实测验证由 CHECK-6 完成，`verified` 由门控通过后的回写步骤（SKILL.md §6.1）统一置位。若把 verified 设为本 CHECK 的门槛，会出现"实测还没跑就要求已验证"的时序倒置：上游不敢标则恒 FAIL 空转回环，上游没实测就标则本 CHECK 形同虚设。

### Step 1: 读取页面清单

从 `ui-manifest.md` 的页面清单表格中提取每个页面的：

- 页面 ID
- 优先级（P0/P1/P2）
- 当前 status（pending / converted / verified / skipped）
- confidence（high / medium / low）

### Step 2: 按优先级分组统计

| 优先级 | 总数 | verified | converted | pending | skipped |
|--------|------|----------|-----------|---------|---------|
| P0 | 统计 | 统计 | 统计 | 统计 | 统计 |
| P1 | 统计 | 统计 | 统计 | 统计 | 统计 |
| P2 | 统计 | 统计 | 统计 | 统计 | 统计 |

### Step 3: 逐页检查 .ets 文件存在性

遍历 `spec/baseline/ui/page_NNNN.md`，读取每个页面 Spec 中记录的 ArkTS 目标文件路径，验证对应的 `.ets` 文件是否存在于 `entry/src/main/ets/` 下。**本步结果直接参与判定**：status 为 converted/verified 但目标文件缺失 = 状态与产物不符，按 FAIL 处理。

### 结果判定

- P0 页面 100% 处于 converted 或 verified，且 Step 3 文件存在性全部通过 → CHECK-5: PASS
- P0 页面有 pending → CHECK-5: FAIL（列出未转换的 P0 页面）
- P0 页面有 skipped → CHECK-5: FAIL（P0 不允许 skipped；确需放弃应先在 ui-manifest 降级该页优先级并记录原因）
- P0 页面 status=converted/verified 但目标 .ets 缺失 → CHECK-5: FAIL（列出"状态与产物不符"清单）
- P1 页面（converted+verified）占比 ≥ 80% → 附 info；< 80% → 附 warnings（P1 不阻塞）

---
