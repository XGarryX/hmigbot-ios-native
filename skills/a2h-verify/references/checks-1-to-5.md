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

先限定当前产品的实际 `.ets` 输入，复用本轮官方目标 SDK 编译诊断与已运行的结构检查。原始 grep 只定位候选，必须排除注释、字符串、示例和非产品文件，不得把文本命中当作 ERROR。

| 候选 | 后续核验 | 判定 |
|---|---|---|
| `: any`、`eval()`、SQL 拼接、生命周期取参线索 | 目标 SDK 实际诊断，或能绑定可执行结构、接收者与具体后果的结构证据 | 原始文字为 WARN；真实已定位缺陷才阻断对应代码 |
| 旧导入、`as` 断言 | 当前 SDK 支持范围及真实调用上下文 | 允许用法保留，记录迁移建议 |

CHECK-2 不为重复 SDK 错误另跑一次编译；引用 CHECK-1 的同签名原始诊断。没有可归因产品错误时可收口静态候选审阅，但不得据此声称编译或运行已验证。

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

以已确认的产品身份合同和当前模块配置为依据：

1. 若已确认 bundle、权限关联或品牌要求，比较当前配置与该具体合同；真实冲突绑定到相应模块和后果。
2. `com.example.*`、vendor 为 `example`、版本为 `1.0.0` 只作待确认提示；没有已确认要求时不凭样例名字判失败。
3. 从当前 ability/module/app 的真实资源引用解析图标、名称及适配配置，核验所引用资源存在、类型和目标 SDK 合法性。
4. 不要求固定 `foreground.png`、`background.png` 或 `layered_image.json` 名称；合法的其他文件名和图标形式可以通过。
5. 真实缺失的被引用资源、身份/权限冲突仍 FAIL；未知产品取舍记待确认，不能替开发者猜测。

SDK 编译与资源诊断是原生合法性依据；文件级解析仅做引用闭包、身份对账和证据绑定。已完成构建轴与尚未确认的展示要求分别报告。

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
