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

> **0.13.4 统一合同（优先于历史示例）**：先读 [执行交界合同](../a2h-run/references/execution-boundary.md)。源读取、选定构建配置、SwiftSyntax/facts、源 AC 和 indexed 计划由当前 git 上游唯一生产；从 execute 起使用本技能的 Garry 实施/收口方法。只使用宿主实际支持的派发字段，不照抄 `agent_type`。已有授权直接沿用；依赖失败输入的任务保持 blocked，不降低静态门禁。权限按交界合同区分：禁止桌面远控；指定测试应用/模拟器的截图、控件查询和固定回放可按已确认范围执行，Preview 不证明业务运行。录屏及未指定设备不在此授权内，未执行项如实记 not_run。未经授权不运行遥测上传。工具修复、工具验证、项目转换、HAP 构建和完整迁移验收分别报告，不能用局部 100% 代表全部完成。



> **iOS 源输入**：读取 Swift/Objective-C、SwiftUI/UIKit、Xcode 工程及原生资源；实际源构建与设备观测依赖可用的源平台环境。鸿蒙侧构建和验收保持原流程。源侧操作详见 `ios-source-analysis/SKILL.md`。

> **iOS 源输入适配**：执行源分析/源设备操作前，读 [原生输入协议](../ios-source-analysis/SKILL.md)。它仅替换平台输入；原阶段、模板、规则、门禁、模式和 target 侧执行保持 1.5.2。

> **当前验证范围**：统一采用七项语义，先读 [编号与范围合同](references/check-keys-and-scope.md)。默认只做基础与实际适用的文件检查；显式 `verify-report --scope <scope.json>` 可选择子集。高级 UI/视觉/设备检查不是转换、构建或生成报告的通用前置。已有当前有效真实失败仍须呈报，不能靠缩小范围隐藏。

> **当前发行边界：旧设备/视觉后端延期，官方应用测试单独取证。** `arkts-scenario-runner`、`arkts-visual-verify`、`arkts-ui-verifier`、`ios-screenshot-analyzer`（及历史 Android 截图别名）和 `scenario-builder` / `visual-fixer` / `visual-fixer-reviewer` 尚未恢复交付，不调用或要求补装这些旧后端，也不因其缺件阻断基本转换/构建/报告。指定应用/模拟器的官方截图、控件查询和固定回放按执行交界合同及实际适配入口运行，不因旧后端延期或缺少桌面屏幕权限一概记 not_run。许可、宿主可用、已实现、实际执行与验收结果分开；缺真实后端/输入仅限制对应检查。外部原始证据核对版本、配置、范围和来源，未执行不记 PASS，真实产品失败保留。下文旧调用/目录仅为兼容映射。


# a2h-verify

## 启动检查 — 待办 findings

读 `spec/.a2h/open-findings.json`（不存在 = 首轮，直接开工）：

| 情况 | 行动 |
|---|---|
| 有 `owner_stage: verify` 的条目 | 先处理这些，再做本轮正常工作；处理完重跑 `scripts/lint_verify_coverage.py` 确认消失 |
| 有上游当前有效的真实产品/源合同阻断 | 按 finding 的对象、消费者和任务依赖阻断受影响部分；独立诊断、构建和报告继续，不按整个队列拒绝开工 |
| 条目标记 `escalate: true`（同一路径多次无进展） | 停止该技术重试路径，读取原错误与恢复条件；可执行替代方案继续，不因次数生成产品决策卡 |
| 本阶段 section 标记 `halted` | 仅暂停该 section 的修复策略；修复真实缺陷或指定新的 `repair_strategy` 后重验。产品审批只用于真实的新产品取舍，预算/授权边界保留 |
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
                                        ├─ CHECK-6  路由跳转验证    → $arkts-router-verify（自动静态检查与报告消费）
                                        ├─ CHECK-7  视觉/运行外部证据 → deferred/not_run（后端延期）
                                        └─ 生成验证报告 + Retrospect 引导
```


---

## 1.1 适用检查与证据复用

按本次范围和实际依赖运行。没有设备、UI 权限或执行报告时，文件/SDK 诊断与报告继续；已选未执行项保留 DEFERRED，未选项标 not_selected，有当前证据和理由的适用性结论标 NOT_APPLICABLE。基础身份未确认时列待确认项，不猜测样例包名或图标并判失败。同签名完整证据跨阶段复用，修复后仅重验被变更破坏的检查。

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

不要求 `spec/migration-report.md` 作为启动凭证；直接诊断当前产物并生成 partial/DEFERRED 报告。真实验收仍核对其正式合同。

---

## 3. 验证清单

按所选检查的真实依赖执行，独立只读检查可并行；每项产出 PASS/FAIL/DEFERRED/NOT_APPLICABLE，并分别标记 selected/not_selected。

### 3.0 编译门禁（贯穿全流程，先于各 CHECK 的硬规则）

编译能不能过，是设备验证与门控的地基，因此有两条强制规则：

1. **编译短路**：CHECK-1 编译 FAIL 时，**本轮跳过设备段 CHECK-7**（它们要 build+install HAP，编译不过只会空转撞错），直接进 §5 老路径修编译后重跑。CHECK-6 路由是纯静态、读源码，**不受影响照常跑**。若 §5 回环耗尽仍编不过，设备段标 `DEFERRED（原因：编译未过）`。
2. **终态编译复检**：CHECK-6 自动检查只生成派生报告；若后续根据发现修复了源码，代码已不是 CHECK-1 当初校验的那份。**修改构建输入后，报告生成前必须重跑受影响的编译复检；输入签名未变时复用当前有效构建证据**，§6 门控的 "CHECK-1" 一律以**这次终态复检**为准，不沿用开头那次的旧结论（防"对账/测试闭环但最终语法不过"）。

### 3a. CHECK-1 ~ CHECK-5

| 检查项 | 简介 | 关键判定 |
|--------|------|---------|
| CHECK-1 全量编译修复 | 委托 `hmos-fix-build-errors` 最多 20 轮 → 失败升级到 `arkts-knowledge-verifier` | 编译通过 → PASS |
| CHECK-2 静态分析 | 当前产品的目标 SDK 诊断与结构证据；grep 仅为候选 | 真实产品错误阻断对应对象；文字/风格候选只提示 |
| CHECK-3 占位符扫描 | 结构化扫描 `placeholder-registry.md` + 兜底 grep TODO | pending=0 且无未注册项 → PASS |
| CHECK-4 App 身份校验 | bundleName/vendor/versionName/app_name/图标/layered_image.json | 0 FAIL → PASS（WARN 不阻塞）|
| CHECK-5 页面状态审计 | 按 P0/P1/P2 分组统计 status 字段 + .ets 文件存在性 | P0 100% converted/verified 且产物存在 → PASS（verified 由 §6.1 门控后回写）|

详见 `references/checks-1-to-5.md`。

### 3b. CHECK-6 ~ CHECK-7：两段委托验证（router 静态 + 设备段 visual）

> 暂停 ≠ 删除：仍以 DEFERRED 计入报告与门控标注（不阻塞），别把它写成 PASS/SKIPPED。

CHECK-6 使用仍交付的纯静态路由能力。CHECK-7 内置设备/视觉后端延期，当前不委托、不运行设备段；只读消费开发者外部证据，否则 deferred/not_run。

| 检查项 | 委托 | 内部循环 | 产物 | 关键判定 |
|--------|------|---------|------|---------|
| CHECK-6 路由跳转验证 | 随包 `arkts-router-verify` 目标抽取器 + iOS 源事实对账 | 主流程自动检查；修复按原任务写权执行后重跑 | `spec/verify/route/ios-route-check.json`、`ROUTE_VERIFY_SUMMARY.md` | 当前已审源边和注册静态对账无缺陷且无缺口 → 静态 PASS；缺绑定/未注册 → FAIL；源待审、过期或抽取失败 → DEFERRED |
旧 Android 设备脚本不能用于 iOS。指定 iOS 测试应用按当前官方适配器及已确认范围执行，或读取可核验独立源证据；未执行不写 PASS，只有一端不记双端通过。

**执行约束**：
旧 Android 设备脚本不能用于 iOS。指定 iOS 测试应用按当前官方适配器及已确认范围执行，或读取可核验独立源证据；未执行不写 PASS，只有一端不记双端通过。
- 仅为明确选中的应用/设备/场景，按实际适配器准备必要测试构建并运行；未选检查不触发 build/install。外部观察核对对应构建与当前输入；缺少 UI 证据不阻断独立基本转换、SDK构建或报告。
- CHECK-7 本工具实际调用记 deferred/not_run；未来设备段规则不能当作本发行版必经步骤。
- 拿不到 iOS 源码仓时 CHECK-6 记 DEFERRED；延期设备/视觉包缺件不提示补装、不扩大为全流程阻断。外部真实失败保留，外部证据未覆盖本次改动时不能沿用通过。

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

存储路径：`spec/verify-report.md`。完整模板见 `references/verify-report-template.md`（含 CHECK-1~7 总览表 + 门控判定 + 各 CHECK 详细结果表）。

---

## 5. 验证失败回环（适用于 CHECK-1~5 + CHECK-7 的 CRASH/URL 功能性子类）

0.13.5 的失败回流必须加载 [根因分诊与受影响复查](references/repair-and-recheck.md)。先消费本轮原报告的逐条失败并只读分诊，再由 `ui-repair run` 按原冻结任务写权执行真实修复、当前构建和受影响原检查；逐条收据保留，不把共因分组、评分或历史PASS当关闭。已确认的官方应用范围沿用，未选后端保持not_run/blocked。

- CHECK-6 自动入口不修改业务代码。缺边、未绑定或未注册的 findings 按原任务责任与写权进入修复；源清单/Spec 问题回原作者。修完重跑 `route-verify` 和受影响构建，原 finding 消失才关闭；不能宣称报告命令已自动修复。
- CHECK-7 拆两级：**ALIGN 纯视觉差异**只记报告等离线消化（不回环）；**CRASH/URL（页面打不开/崩溃）是功能性失败**，视同 CHECK-1~5 进老路径（visual-verify 自身无循环，这类失败若不回环就无人修复）。
- CHECK-1~5 任一失败，或 CHECK-7 存在 CRASH/URL → 走老路径：从失败项提取修复任务 → 生成 `spec/plans/plan-fix-<timestamp>.md` → 委托 a2h-execute 执行 → 重新执行 a2h-verify（重验范围见 `references/failure-loop.md`「回环轮重验范围」，**不是简单地"只查之前失败的项"**——修复可能引入回归）。
- 回环上限：最多 3 轮（硬上限）。

详见 `references/failure-loop.md`。

---

## 6. 门控

**V1 门控标准**：

```
门控判定:
  当前绑定的真实产品/源/产物 FAIL → FAIL，明确受影响对象与恢复条件
  已选且适用的基础项缺当前证据 → PARTIAL，可继续独立诊断/构建/报告
  已选项全部 PASS 或有证据 NOT_APPLICABLE → PASS_SELECTED_SCOPE
  七项真实 PASS → 当前检查范围 PASS；完整迁移等价仍按独立 AC/行为证据判定
  未选高级项 → not_selected，不因未执行阻断基础转换

```

CHECK-7 的 ALIGN 纯视觉差异不阻塞门控，记录在报告中作为后续优化方向。**CHECK-7 的 CRASH/URL 是功能性失败**（页面打不开/崩溃不是"视觉问题"），阻塞门控并进 §5 回环。

> **DEFERRED 不等于通过**：已选路由检查缺当前证据时报告保持 PARTIAL，并列明恢复条件；未选项独立标 not_selected。有缺口仍可继续独立诊断、构建和报告，不能宣称路由或完整迁移通过。

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
| `$arkts-router-verify` | 路由静态抽取与当前源事实对账（CHECK-6） | 正式报告自动调用；修复另按原写权执行 |
| `arkts-visual-verify`（延期） | CHECK-7 外部视觉证据范围 | 不内联/派发；读取开发者外部原始证据，否则 deferred/not_run |


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

自然语言触发时先核本次范围与当前输入；缺少执行报告时仍生成带准确缺口的诊断报告。

---

## 9. References 索引

| 文件 | 覆盖范围 |
|------|---------|
| `references/execution-discipline.md` | 执行铁律全文（自检清单、违规处置）|
| `references/checks-1-to-5.md` | CHECK-1 ~ CHECK-5 的完整执行步骤 |
| `references/check6-to-7.md` | CHECK-6（路由，静态）/ 7（设备段 visual）两段委托细则（前置检测、串行约束、产物读取、状态映射）|
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


## 冷启证据范围

`a2h-execute/scripts/cold_start_probe.sh` 只读取已有 CLI 文件证据，不自动操作设备或读取界面。提供明确应用、PID、启动窗口、进程观察文件和日志；命令缺少输入时输出 not_run 与恢复条件，不主动采集。

普通 `AppRecovery` 文字、其他进程崩溃或旧时间窗日志不是本应用失败。启动观察与首启网络分轴报告；仅已确认的联网场景检查对应请求，离线应用不要求网络。没有请求日志保留 unverified，不能把全局网络日志冒充本应用联网成功。

缺少授权、设备或运行证据时允许继续静态/构建和 partial 报告；实际归因崩溃、错误路由或请求失败保留为对应业务缺陷。未观察不等于通过，也不等于产品已失败。

## 统一报告消费合同

本执行模型使用七项 CHECK 编号，不复用旧四项编号的语义。将实际检查结果写入
`spec/verification/verify-results.json`：schema_version=2、execution_model=indexed-stages-v1、
source_sha256、execution_contract_sha256、当前 spec_input_hashes/target_input_hashes，
checks 每项含 id/status(PASS|FAIL|DEFERRED)/detail/exit_code/evidence(path,sha256)。
输入摘要从 quality_views 的同名只读函数取得，不能手编通过值。CHECK-1 还需当前终态真实构建证据。
随后运行 `python3 <runtime>/scripts/a2h_ios.py verify-report --project <target> [--build-evidence <实际报告>]`，
由命令单写七项 `spec/verify-report.md`；旧 schema 1 四项结果不能误作本轮七项通过。
DEFERRED 逐项保留；允许继续的阶段门记 PASS_WITH_DEFERRED，不能称完整迁移验收已通过。


0.13.6：存在页面/导航输入时，正式verify-report/gate-artifacts会实际调用arkts-router-verify目标抽取及当前iOS源事实对账，自动消费CHECK-6。显式未选项不调用；--check只读验证现有证据。缺源清单/检查失败/输入过期不能用旧PASS放行；自动入口只生成派生结果，不擅改业务代码。实际入口及边界见arkts-router-verify开头0.13.6协议。
