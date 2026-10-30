# CHECK-6 功能验收（摘除原件，2026-08-25）

> 摘除原因：用户指令（与 CHECK-9/10 同一处置模式）。恢复方式：把下列各块放回
> 原位并把现行 CHECK-6/7（原 7/8）编号退回，或整体作为新编号追加。
> 摘除时原编号：CHECK-6；摘除后 router=CHECK-6、visual=CHECK-7。

## 原件：SKILL.md 表行

| CHECK-6 功能验收 | 逐 F-xxx 读 `features/F-xxx.md` 验收标准 + 自动化检查 | V1 全 PASS → PASS |

---

## 原件：checks 执行细则节

## CHECK-6：功能验收

从 `spec/baseline/feature-index.md` 读取功能清单，逐项检查：

```
feature-index.md 功能列表
  │
  ├─ V1 项（必须通过）:
  │   ├─ 功能代码文件存在
  │   ├─ ViewModel 已创建
  │   ├─ 数据层已接入
  │   └─ ...（从 feature-index.md 读取各功能验收标准）
  │
  └─ V2 项（可选通过）:
      ├─ 动画流畅
      ├─ 性能达标
      └─ ...
```

### 验收方法

1. 读取 `spec/baseline/feature-index.md` 中的功能列表
2. 对每个 V1 功能 ID（F-xxx），读取 `spec/baseline/features/F-xxx.md` 中的验收标准
3. 自动化检查：
   - 文件是否存在：检查该功能 slice 文件（`plans/slices/slice-NN-<fid>.md`，经索引 `detail:` 指针定位）中对应的 output 文件
   - 关键方法：grep @Component / async 方法名 / $r 引用
4. 无法自动化的项标记为"需人工验收"

> **路由/导航正确性不在本 CHECK**：页面跳转、弹窗目的地、触发控件是否绑定路由等，统一交给 **CHECK-7 路由跳转验证**（`$arkts-router-verify`，控件级双端对账 + 自动修复），比这里的 `grep router 配置` 强得多。本 CHECK 只验功能的"代码/ViewModel/数据层"是否落地，不再 grep 路由注册。

每项通过自动化检查或标记为需要人工验收。

### 结果判定

- V1 所有自动化检查项 PASS → CHECK-6: PASS
- V1 有 FAIL → CHECK-6: FAIL
- V2 项不影响 CHECK-6 判定

### AC 质量与双端核对（v2.3+TY 新增）

a2h-spec 为每个 feature 按动态预算生成带锚点的 AC（验收标准），并过质量护栏。**锚点二型**：`源:<Swift/Objective-C 符号> → 标:`（parity AC，断言与 iOS 行为一致）| `决:<PD/D/G-ID> → 标:`（差异 AC，转写 decision-ledger 已批准的平台差异决策的替代行为）。CHECK-6 在功能验收时一并核对：

- **AC 质量**：抽查 AC 已按预算生成且过质量护栏——
  - 无「三无 AC」（无行为断言的空壳 AC）；
  - 无同 `源` 符号、同行为的重复 AC；
  - `depth: stub` 的 feature 其占位 AC（3–8 条）按 stub 计，**不计入实现率欠账**（不因 stub 缺实现而判 FAIL）。
- **AC 双端核对（按锚点二型分支）**：
  - `源:` parity AC：「源行为 ↔ ArkTS 实现」双端比对——源侧（Swift/Objective-C 符号）的行为标侧须有对应实现，标侧实现须能回溯到某条 AC。
  - `决:` 差异 AC：源侧 = **ledger 该决策条目的替代行为描述**（grep 决策 ID 取正文，不查 Swift 源——被替代的 iOS 行为已由决策记录），标侧实现须与该描述一致；`决:` 指向的 ledger 条目缺失或 status≠approved → CHECK-6: FAIL（未批决策不得进入验收）。
  - **`[真机]` 标记的差异 AC**：`标` 实现须存在（静态可查），但其**行为断言不计入本 CHECK 的静态实现率**——路由 CHECK-8 设备段实测；设备段 DEFERRED 时在报告「遗留未实测」清单中逐条列出（不静默吞掉）。

**判定并入 CHECK-6**：AC 命中质量护栏（三无 / 重复）、双端核对发现 V1 行为缺实现、或 `决:` 锚不可解析/未批准 → CHECK-6: FAIL；`depth: stub` 占位 AC 缺实现、`[真机]` AC 的行为断言（已路由设备段）不触发 FAIL。


---

## 原件：report 模板节

| 功能验收 | CHECK-6 | PASS/FAIL | V1 通过: X/Y, V2 通过: Z/W |

### CHECK-6: 功能验收
| 功能 ID | 功能名称 | V 级别 | 状态 | 备注 |
|---------|---------|--------|------|------|
| F-001 | ... | V1 | PASS/FAIL | ... |
| F-002 | ... | V2 | PASS/SKIP | ... |



---

## 原件：failure-loop 分支行

      │   ├─ CHECK-6  功能验收失败 → task: 补全缺失功能 (对应 skill)