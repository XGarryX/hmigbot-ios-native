---
name: a2h-verify
description: 第四步：验证迁移产出。编译检查 + 静态分析 + 占位符扫描 + App 身份校验 + 页面状态审计 + 功能验收 + 路由跳转验证 + 视觉对齐。即使用户只说"验证"或"测试"，也应触发。
metadata:
  type: pipeline
  domain: migration
  tags:
  - pipeline
  - migration
---

> **.33 iOS 适配**：CHECK-6 使用 [原生路由输入](../arkts-router-verify/references/native-route-source.md)；CHECK-7 使用 [Xcode 源端流程](../arkts-visual-verify/references/native-xcode-source.md)。当前 source provider 使用工具独占的新 Simulator，不占用其他工程设备。适配器不可用是工具错误，不能谎报设备不存在或把缺产物视为 PASS；原回环、编译复检及合法状态不变。


> **iOS 源输入**：读取 Swift/Objective-C、SwiftUI/UIKit、Xcode 工程及原生资源；实际源构建与设备观测依赖可用的源平台环境。鸿蒙侧构建和验收保持原流程。源侧操作详见 `a2h-spec/references/native-input.md`。

> **iOS 源输入适配**：执行源分析/源设备操作前，读 [原生输入协议](../a2h-spec/references/native-input.md)。它仅替换平台输入；原阶段、模板、规则、门禁、模式和 target 侧执行保持 1.5.2。

> **⚠️ 用户契约（最高优先级）**：本 skill 每个 CHECK 必须严格顺序执行；不允许以"省时 / 省 token / 上下文长 / 预估收效低"等理由跳过或合并任一项。**CHECK-6/7 各自委托给独立的 verifier skill**（router / visual）；router-verify 的修复闭环、ut 和 ui 的修复循环都在它们自身的 SKILL 内部完成，a2h-verify 不再持有循环。

# a2h-verify

## 启动检查 — 待办 findings

读 `spec/.a2h/open-findings.json`（不存在 = 首轮，直接开工）：

| 情况 | 行动 |
|---|---|
| 有 `owner_stage: verify` 的条目 | 先处理这些，再做本轮正常工作；处理完重跑 `scripts/lint_verify_coverage.py` 确认消失 |
| 有 `owner_stage` 属**上游阶段**且 `severity: blocking` 的条目 | 🔴 **拒绝开工**，列出条目并提示用户回到该阶段（a2h-spec / a2h-plan / a2h-execute） |
| 条目标记 `escalate: true`（同一问题连续 3 轮） | 🔴 停止自动重试，按 a2h-spec `templates/decision-card.md` §连续未收敛 出决策卡 |
| 本阶段 section 标记 `halted`（进度停滞 3 轮 / 累计 10 轮） | 🔴 **停止修复尝试**，按 decision-card §连续未收敛 出决策卡；用户裁决后 `--clear-halt <决策ID>` 解除，再继续 |
| 无条目 | ✅ 正常开工 |

路由不靠猜：每个 linter 比对两份产物，**哪一侧缺条目就由哪一侧负责**。责任无法机械判定时
（典型：AC 按当前描述实现不了），用决策卡上报，由用户指定 owner——选项与 owner 的对应关系
写死在卡里，避免推诿。

**findings 只能由「原 linter 重跑后不再报」来关闭**，不能由任何一方声明「已修复」而关闭。

> **存量/legacy spec 首轮提示**：报 `VERIFY.SPEC_INDEX_MISSING` 不是要求改写 spec——在 a2h-spec
> 侧跑 `python3 <a2h-spec>/scripts/build_traceability_index.py --project-root <ROOT>` 即从现有
> Markdown 秒级派生 index（零内容改动），重跑本 linter 即关闭。

## 1. 定位

Pipeline 层第四步，**统一验证编排**。聚合多种验证手段，给出一份结构化的通过/失败报告。

```
a2h-spec → a2h-plan → a2h-execute → a2h-verify（本 skill）
                                        │
                                        ├─ CHECK-1  全量编译修复
                                        ├─ CHECK-2  静态分析
                                        ├─ CHECK-3  占位符扫描
                                        ├─ CHECK-4  App 身份校验
                                        ├─ CHECK-5  页面状态审计
                                        ├─ CHECK-6  路由跳转验证    → $arkts-router-verify（纯静态，内置修复闭环）
                                        ├─ CHECK-7  视觉对齐         → $arkts-visual-verify
                                        └─ 生成验证报告 + Retrospect 引导
```


---

## 1.1 执行铁律（无跳过原则）

主对话执行 a2h-verify 时**禁止以"省时 / 省 token / 上下文长 / 预估收效低"等任何理由**跳过任一 CHECK 项。

核心禁止项：
1. **CHECK-1~8 任一项标 SKIP**——CHECK-1~8 全部没有 SKIP 条件；不可执行只能标 DEFERRED 并写明原因
2. **CHECK-6/7 委托后不读结果**——主线程必须读各 verifier 产出，把 PASS/FAIL 落到本 skill 报告
3. **失败回环老路径提前 break**——"最多 3 轮"是硬上限不是建议


**详见 `references/execution-discipline.md`**。

---

## 2. 输入

| 文件 | 用途 |
|------|------|
| `spec/baseline/ui-manifest.md` | 页面清单、优先级、confidence、页面状态 |
| `spec/baseline/feature-index.md` | 功能总索引、V1/V2 分配、依赖图 |
| `spec/baseline/plans/feature-plan.md` | 已执行的功能执行计划（L1 索引；逐 slice 账本在 `plans/slices/slice-NN-<fid>.md`） |
| `spec/baseline/plans/ui-plan.md` | 已执行的 UI 转换计划 |
| `spec/baseline/ui/page_NNNN.md` | 各页面详细 UI Spec |
| `spec/baseline/features/F-xxx.md` | 各功能详细 Spec |
| `spec/migration-report.md` | a2h-execute 执行报告 |
| `spec/placeholder-registry.md` | 占位符注册表（如果存在） |
| `entry/src/main/ets/**/*.ets` | 迁移产出代码 |

如果 `spec/migration-report.md` 不存在，提示用户先执行 `a2h-execute`。

---

## 3. 验证清单

按顺序执行，每项产出独立的 PASS/FAIL/DEFERRED 状态（CHECK-1~8 均无 SKIP）。

### 3.0 编译门禁（贯穿全流程，先于各 CHECK 的硬规则）

编译能不能过，是设备验证与门控的地基，因此有两条强制规则：

1. **编译短路**：CHECK-1 编译 FAIL 时，**本轮跳过设备段 CHECK-7**（它们要 build+install HAP，编译不过只会空转撞错），直接进 §5 老路径修编译后重跑。CHECK-6 路由是纯静态、读源码，**不受影响照常跑**。若 §5 回环耗尽仍编不过，设备段标 `DEFERRED（原因：编译未过）`。
2. **终态编译复检**：CHECK-6 自带修复闭环会改源码，跑完后代码已不是 CHECK-1 当初校验的那份。**报告生成前必须重跑一次编译复检**，§6 门控的 "CHECK-1" 一律以**这次终态复检**为准，不沿用开头那次的旧结论（防"对账/测试闭环但最终语法不过"）。

### 3a. CHECK-1 ~ CHECK-5

| 检查项 | 简介 | 关键判定 |
|--------|------|---------|
| CHECK-1 全量编译修复 | 委托 `hmos-fix-build-errors` 最多 20 轮 → 失败升级到 `arkts-knowledge-verifier` | 编译通过 → PASS |
| CHECK-2 静态分析 | grep 检查：`any`、废弃导入、SQL 拼接、`as`、`eval()`、aboutToAppear 参数 | ERROR 0 → PASS（WARN 不阻塞，附清单）|
| CHECK-3 占位符扫描 | 结构化扫描 `placeholder-registry.md` + 兜底 grep TODO | pending=0 且无未注册项 → PASS |
| CHECK-4 App 身份校验 | bundleName/vendor/versionName/app_name/图标/layered_image.json | 0 FAIL → PASS（WARN 不阻塞）|
| CHECK-5 页面状态审计 | 按 P0/P1/P2 分组统计 status 字段 + .ets 文件存在性 | P0 100% converted/verified 且产物存在 → PASS（verified 由 §6.1 门控后回写）|

详见 `references/checks-1-to-5.md`。

### 3b. CHECK-6 ~ CHECK-6：两段委托验证（router 静态 + 设备段 visual）

> 暂停 ≠ 删除：仍以 DEFERRED 计入报告与门控标注（不阻塞），别把它写成 PASS/SKIPPED。

两个 verifier 都委托独立 skill 自管循环。**CHECK-6 路由纯静态先跑**（修复会改源码，让设备验证跑在修过路由的代码上）；**CHECK-7 设备段严格串行**，每个跑完 sleep 5（设备静默）。

| 检查项 | 委托 | 内部循环 | 产物 | 关键判定 |
|--------|------|---------|------|---------|
| CHECK-6 路由跳转验证 | `$arkts-router-verify` | **自带修复闭环**（抽取→对账→agent 修复→复检收口） | `spec/verify/route/ROUTE_VERIFY_SUMMARY.md`、`fix_plan.json` | 无 reopened 且 `pushed_but_unregistered`=0 → PASS；拿不到 iOS 源码仓 → DEFERRED |
| CHECK-7 视觉对齐 | `$arkts-visual-verify` | 无（一次性截图对比） | `spec/fix/round-N/ui/{ALIGN,URL,CRASH}_*.md` | CRASH/URL=0 且 ALIGN=0 → PASS；仅 ALIGN → FAIL-visual（不门控）；CRASH/URL>0 → FAIL-functional（阻塞门控，进 §5 回环）；adb/hdc 任一不可用 → DEFERRED |

**执行约束**：
- **CHECK-6 路由纯静态、不碰设备**：不依赖 hdc/adb，先于设备段跑；它与设备段之间无串行/sleep 约束
- **设备段的前置是"编译能过"**：CHECK-7 要 build+install HAP，因此 CHECK-1 终态编译 FAIL 时本轮不跑它们（见 §3.0 编译短路）；回环耗尽仍编不过则标 `DEFERRED（编译未过）`
- **CHECK-7 设备段**：visual 跑完 sleep 5（设备静默 + uitest daemon 排空）再进后续步骤
- 拿不到 iOS 源码仓 → CHECK-6 标 DEFERRED；**源 iPhone/Simulator 观测工具或 hdc 任一不可用 → CHECK-7 标 DEFERRED**（visual 需双端模拟器截图）；**对应 verifier skill 未安装 → 该 CHECK 标 DEFERRED（原因：skill 未安装）**，没有任何"主线程 SKIP"（见 `references/orchestration.md` 处置表）

详见 `references/check6-to-7.md`。

> 已删除的三项：**Spec 覆盖率**（UI 覆盖率与 CHECK-5、功能 V1 VERIFIED 率与 CHECK-6 重复）、**confidence 降级审查**（与 CHECK-5 页面状态审计 + CHECK-3 占位符扫描重叠）、**风格合规**（原 CHECK-9，依赖的风格 orchestrator skill 不在本包内，恒为 SKIP/DEFERRED，见 `references/_dormant/check9-style/`）。三者均为非门控的建议性检查，删除以收敛流程。

### 3c. Retrospect 引导（必选）

验证报告生成后，自动输出引导信息：

```
全部通过 → "验证全部通过。建议执行 a2h-retrospect 提取本次迁移经验。"
门控通过但有建议项失败（FAIL-visual）→ "门控通过；存在 N 项建议性问题（视觉差异），
    可离线处理，不阻塞。建议执行 a2h-retrospect。"
门控失败 → "存在门控失败项，请先处理（回环已跑满/或需人工介入）。处理完毕后建议执行 a2h-retrospect。"
```

### 3e. 生成统一验证报告

汇总所有检查结果，写入 `spec/verify-report.md`。模板见 `references/verify-report-template.md`。

---

## 4. 验证报告

存储路径：`spec/verify-report.md`。完整模板见 `references/verify-report-template.md`（含 CHECK-1~8 总览表 + 门控判定 + 各 CHECK 详细结果表）。

---

## 5. 验证失败回环（适用于 CHECK-1~5 + CHECK-7 的 CRASH/URL 功能性子类）

- CHECK-6 失败由 router-verify 内部处理（自带修复闭环）。a2h-verify **不为它做老路径回环**。
- CHECK-7 拆两级：**ALIGN 纯视觉差异**只记报告等离线消化（不回环）；**CRASH/URL（页面打不开/崩溃）是功能性失败**，视同 CHECK-1~5 进老路径（visual-verify 自身无循环，这类失败若不回环就无人修复）。
- CHECK-1~5 任一失败，或 CHECK-7 存在 CRASH/URL → 走老路径：从失败项提取修复任务 → 生成 `spec/plans/plan-fix-<timestamp>.md` → 委托 a2h-execute 执行 → 重新执行 a2h-verify（重验范围见 `references/failure-loop.md`「回环轮重验范围」，**不是简单地"只查之前失败的项"**——修复可能引入回归）。
- 回环上限：最多 3 轮（硬上限）。

详见 `references/failure-loop.md`。

---

## 6. 门控

**V1 门控标准**：

```
门控判定:
  ├─ CHECK-1 全量编译: MUST PASS（取 §3.0 终态编译复检结果，非开头那次）
  ├─ CHECK-2 静态分析: ERROR 级 0 MUST PASS（WARN 不阻塞）
  ├─ CHECK-3 占位符扫描: MUST PASS（无可回填未回填项；deferred V2 占位符不算失败）
  ├─ CHECK-4 App 身份校验: MUST PASS（0 FAIL；WARN 不阻塞）
  ├─ CHECK-5 页面状态审计: P0 页面 100% converted/verified 且产物存在 MUST PASS
  ├─ CHECK-6 路由跳转验证: MUST PASS（DEFERRED 时不阻塞；含运行时必崩项 pushed_but_unregistered=0）
  ├─ CHECK-7 功能性子项: CRASH/URL_MISMATCH = 0 MUST PASS（仅 ALIGN 视觉差异不阻塞；DEFERRED 时不阻塞）
  │
  以上全部通过？
  ├─ 是 → 门控通过 → 执行 §6.1 状态回写 → 可进入 a2h-retrospect
  └─ 否 → 触发回环（§5），或提示用户手动介入
```

CHECK-7 的 ALIGN 纯视觉差异不阻塞门控，记录在报告中作为后续优化方向。**CHECK-7 的 CRASH/URL 是功能性失败**（页面打不开/崩溃不是"视觉问题"），阻塞门控并进 §5 回环。

> **DEFERRED 不阻塞 ≠ 强通过**：CHECK-6/7 在前置缺失时 DEFERRED 不卡门，但若门控是在若干 DEFERRED 下达成的（如无设备 + 无 iOS 源码仓时门控实际只剩 CHECK-1~5 纯静态项），报告**必须在门控判定区显著标注**"本次门控通过是在 N 项 DEFERRED 下达成，路由/视觉未实测"，避免被误读为强通过。

### 6.1 验证状态回写（门控通过后必跑）

CHECK-5 审计的是"转换完成态"（converted），`verified` 在此处统一置位——这是全流程唯一把实测结论写回 `spec/baseline/ui-manifest.md` 的环节，缺了它 verified 状态就没有产生机制：

```
门控通过后:
  ├─ CHECK-7 实测（非 DEFERRED）且无 CRASH/URL → 把 P0 页面中 status=converted 的批量置 verified
  │     例外: 某页在 spec/fix/round-N/ui/ 仍有 CRASH_/URL_ 单未消
  │           → 该页不回写，列入报告"遗留未回写"清单
  ├─ CHECK-7 DEFERRED → 不回写（status 维持 converted），
  │     报告标注"未实测，verified 未置位"
  └─ 回写时在 ui-manifest 该页备注记录来源（a2h-verify 日期 + 本轮实际非 DEFERRED 的实测项，如 "CHECK-7"；CHECK-6 DEFERRED 时不得写入 CHECK-6）
```

P1/P2 页面不在门控与实测保证范围内，不回写。下次运行 CHECK-5 时，verified 即是上一轮实测的真实痕迹，而不是未经验证的自我声明。

---

## 7. 与 Domain Skill 的关系

| Skill / Agent | 角色 | 调用方式 |
|---|---|---|
| `$hmos-fix-build-errors` | 全量编译修复（CHECK-1） | 主对话内联 |
| `$arkts-knowledge-verifier` | 编译升级诊断 + 静态分析辅助（CHECK-1/2） | 主对话内联 |
| `$arkts-app-identity` | App 身份校验（CHECK-4） | 主对话内联 |
| `$arkts-router-verify` | 路由跳转验证 + 内置修复闭环（CHECK-6，纯静态） | 主对话内联 |
| `$arkts-visual-verify` | 视觉对齐（CHECK-7） | 主对话内联 |


详见 `references/orchestration.md`。

---

## 8. 触发 Prompt 示例

```
验证
测试一下
检查下迁移结果
跑一下验证
编译通过吗
检查代码质量
P0 页面都验证了吗
```

自然语言触发时，a2h-verify 先检查 `spec/migration-report.md` 是否存在。如果不存在，提示用户先执行 a2h-execute。

---

## 9. References 索引

| 文件 | 覆盖范围 |
|------|---------|
| `references/execution-discipline.md` | 执行铁律全文（自检清单、违规处置）|
| `references/checks-1-to-5.md` | CHECK-1 ~ CHECK-5 的完整执行步骤 |
| `references/check6-to-7.md` | CHECK-6（路由，静态）/ 8（设备段 visual）两段委托细则（前置检测、串行约束、产物读取、状态映射）|
| `references/verify-report-template.md` | `spec/verify-report.md` 的完整模板 |
| `references/failure-loop.md` | 失败回环算法（CHECK-1~5 + CHECK-7 CRASH/URL；含编译短路 Step 0、回环轮重验范围表）|
| `references/orchestration.md` | 编排关系完整图、调用模型规则 |

---

## 收尾 — 验证对账（强制）

把每条 requirement 的结论写入 `spec/.a2h/verification.json`：

```json
{"verdicts": [{"requirement_id": "F001-AC01", "verdict": "pass",
               "oracle_used": "ui", "evidence": "spec/fix/round-1/ui/…md",
               "requirement_digest": "sha256:…", "reason": ""}]}
```

`verdict` ∈ `pass | fail | blocked | deferred`。**设备不可用时结论是 `blocked`，不是 `pass`**。

然后跑：

```bash
python3 scripts/lint_verify_coverage.py --project-root $PROJECT_ROOT
```

- 🔴 `VERIFY.NO_VERDICT`：active 需求没有任何结论——**这就是「verify 漏判了 AC」的检出点**。
- 🔴 `VERIFY.REQUIREMENT_FAILED`：结论为 fail → `owner_stage=execute`，走既有回环
  （见 [references/failure-loop.md](./references/failure-loop.md)），修复任务须带上
  `requirement_id`，这样复检能按需求逐条确认关闭，而不是只看 CHECK 级别的红绿。
- 🔴 `VERIFY.VERDICT_STALE`：AC 已变更，结论基于旧断言。
- 🟡 `VERIFY.DEFERRAL_UNEXPLAINED`：blocked/deferred 未写原因与关闭条件。

> **判定强度门禁尚未启用**：本对账只回答「有没有被判过」，不回答「判得够不够强」。
> Spec 侧已在每条 AC 的 `判:` 锚声明了应有的判定方式，Gate 摘要会把 `判:` 与实际
> `oracle_used` 并列如实呈报，但暂不自动阻断。「编译通过 ≠ 行为正确」的强度门禁是后续
> 单独一项。

---

## 10. 收尾：盘库 + 上报本阶段用量

verify 成功产出 `spec/verify-report.md` 后，作为本 skill 的最后一步执行（纯本地 Bash，**忽略退出码、绝不阻断**）。**两条命令的先后顺序有意义，不要调换**：

```bash
# 1. 代码行数盘库（LOC 事实）→ code-lines.json
.migbot/bin/a2h count-lines

# 2. 标记本阶段水位
.migbot/bin/a2h mark-stage a2h-verify
```

- **`count-lines`** 统计 iOS / HarmonyOS 两侧的代码行数。verify 通过即迁移完成，此刻两侧代码都已就位，是行数盘库的第一个有效时点——而 `$a2h-init` 那次盘库跑在迁移之前，HarmonyOS 侧尚不存在（记为 `null`）。缺了这一次，一个只跑到 verify、不跑 retrospect 的迁移会永远停在"已完成、HarmonyOS 0 行"。a2h-retrospect 结尾还会再盘一次（覆盖同一 run 的 fact），两次都跑不会重复计数。
- **`mark-stage a2h-verify`** 写出本阶段的 stage-marks fact 与 sentinel。这个水位就是**服务端判定"迁移已完成"的唯一依据**（Codex 没有 CC 的 finalize 上传）——所以它必须排在 `count-lines` 之后：完成状态一旦落库，看板就会开始展示这个 app 的行数，行数得先就位。token / subagent / skill 维度的用量由生命周期 hook 上传的会话记录在服务端解析归因，供性能看板（5002）的事件时间轴使用；本步不自行采集用量。

---


## 冷启冒烟与粘性债（能力交付契约配套，2026-08-24 起）

设备在线时，CHECK-7 前先跑 60 秒冷启冒烟（`a2h-execute/scripts/cold_start_probe.sh`）：
**主判据 = 首个网络请求出网 + 冷启不 crash**（二值、机械、不可被文案措辞游戏）；
dump 中「未配置/尚未就绪/unavailable」类文案仅作附加证据。
设备不在线 → **不是 DEFERRED 后消失**：verify 报告固定记 `unverified-cold-start`
粘性债，**该状态令整体验收门控保持 FAIL/BLOCKED**（与 CHECK-4 bundleName 模板值同级），
直到设备段真跑过冒烟为止。禁止以任何汇总口径把此债从报告首屏挪走。