> **当前发行 profile：设备/视觉后端延期。** `arkts-scenario-runner`、`arkts-visual-verify`、`arkts-ui-verifier`、`ios-screenshot-analyzer`（及历史 Android 截图别名）和 `scenario-builder` / `visual-fixer` / `visual-fixer-reviewer` 未作为本包可运行能力交付。不得调用、派发、要求安装或因其缺件阻断基本转换/构建/报告。相关本次实际调用记 deferred/not_run；可只读消费开发者提供的外部原始证据，核对源/目标版本、配置、范围和来源，保留外部实际结果，不能写成本工具已实测。没有证据不记 PASS，真实已归因产品失败继续保留。下文相关调用/目录仅为未来兼容标记。

> **iOS 源输入**：读取 Swift/Objective-C、SwiftUI/UIKit、Xcode 工程及原生资源；实际源构建与设备观测依赖可用的源平台环境。鸿蒙侧构建和验收保持原流程。源侧操作详见 `ios-source-analysis/SKILL.md`。

# CHECK-6 / 8：路由跳转验证 + 视觉对齐（两段委托）

> 配合 SKILL.md §3b 使用。本组四个 CHECK 都**委托给独立 verifier skill 自管循环**，a2h-verify 不持有循环。
> - **CHECK-6 路由（arkts-router-verify）= 纯静态**，自带抽取→对账→修复→复检闭环；**不依赖设备**，前置是"拿得到 iOS 源码仓"。先跑。
> - **CHECK-7（visual / ut / ui）= 设备相关**，必须严格串行 + 每段后 sleep 5（设备 IPC / uitest daemon）。在 CHECK-6 之后跑。

---

## §0 执行总序

```
CHECK-6  路由跳转验证（静态，先跑，自带 fix-loop）→ 改 HMOS 源码
   │  （routing 修复会改源码，放在设备验证之前，让 CHECK-7 跑在修过路由的代码上）
   ▼
CHECK-7  视觉对齐（设备）   ── sleep 5 ──▶
```

CHECK-6 与设备段之间**无 sleep / 串行约束**（routing 不碰设备）。设备段内部必须串行。

---

## §1 CHECK-6：路由跳转验证（arkts-router-verify，静态 + 自带 fix-loop）

### 1.1 这是什么

委托 `$arkts-router-verify`：在 iOS 源码仓与 HMOS 迁移仓**两端各抽一张控件级导航图**，以
`spec/baseline/ui-manifest.md` 做权威页面映射逐页对账，检出四维度路由问题并**自动改 HMOS 源码修复**，
修完复检出报告。**纯静态**（读源码，零设备零编译），因此可在设备不可用时照常运行。

检出/修复维度：① 目标页面缺（A1）② 目标弹窗缺（A2，弹窗是一等路由目的地）③ 跳转按钮/文字/菜单项缺（B）
④ 触发点未绑定路由/弹窗（C）。最高优是 `pushed_but_unregistered`（push 了没注册 = 运行时必崩 P0）。

### 1.2 前置条件检测

```
CHECK-6 前置:
  1. arkts-router-verify skill 已装在 <HMOS仓>/.agents/skills/
     —— 缺则 CHECK-6: DEFERRED（原因：verifier skill 未安装），计入门控 DEFERRED 标注
  2. iOS 源码仓路径可得（传给 router-verify 的 --ios-root）
     - 优先从 spec/migration-report.md / spec/baseline 里记录的 ios_root 读
     - 读不到则向用户索取；仍拿不到 → CHECK-6: DEFERRED
  3. spec/baseline/ui-manifest.md 存在最佳（无则 router-verify 退化为命名启发式，仍可跑）
```

本项源设备自动操作不可用于 iOS；当前所需观察记 not_run，读取已有独立源证据。
> 设备不可用不是 CHECK-6 标 DEFERRED 的理由。

### 1.3 执行

```pseudocode
if ios_root_available:
    $arkts-router-verify   # 进入其 7 步工作流：抽两端导航图 → LLM 补长尾 → 页面映射 →
                                 # 三视角对账 → triage + agent 分派修复 → 复检出报告（全程内部自管）
    读 spec/verify/route/ROUTE_VERIFY_SUMMARY.md + spec/verify/route/fix_plan.json → 提取状态
else:
    CHECK-6: DEFERRED
```

router-verify 内部已完成"抽取→对账→triage→agent 修复→复检收口"全链，a2h-verify **不干预其内部轮数、
不旁路派 fixer**——只读它退出后的报告。

### 1.4 结果读取与状态映射

| 产物 | 用途 |
|---|---|
| `spec/verify/route/ROUTE_VERIFY_SUMMARY.md` | 最终报告：verified / reopened / wontfix 明细 + 复检结果 |
| `spec/verify/route/fix_plan.json` | 修复清单收口态（每条 verified / reopened / wontfix）|
| `spec/verify/route/reachability_robust.json` | robust 可达性，含 `pushed_but_unregistered`（运行时必崩项）|

**状态映射**：

- 全部修复项闭环（`fix_plan.json` 无 `reopened`）**且** `pushed_but_unregistered == 0` → **PASS**
  （`wontfix` 项是合法遗留定性——死代码/架构等价/外部能力未迁移——不计失败，但写进报告遗留区）
- 存在 `reopened` 项 **或** `pushed_but_unregistered > 0` → **FAIL**（差距清单写入 verify-report.md）
- 拿不到 iOS 源码仓 / router-verify skill 未安装 → **DEFERRED**

### 1.5 状态合法集

| CHECK | 合法状态 | 备注 |
|---|---|---|
| CHECK-6 | PASS / FAIL / DEFERRED | DEFERRED 仅"拿不到 iOS 源码仓 / skill 未安装"；**与设备无关** |

---

## §2 CHECK-7：当前后端延期

当前不运行设备探针、不调用 visual/UI/scenario skills 或三个延期角色，也不因这些包未安装而要求开发者补装。CHECK-7 本工具实际调用为 deferred/not_run；基本转换、当前SDK构建、路由静态检查与报告继续。

开发者可提供外部已有报告及原始截图/日志/trace文件。仅核对其实际源/目标版本、配置、页面/场景范围、产生工具与结果，按外部证据如实引用；不冒称本工具完成采集或复测，输入已变的旧观察不得直接当作当前通过。没有外部证据保持未验证，真实已证产品缺陷保留。

以下历史产物路径只用于外部证据映射及未来兼容，不代表本profile已装可运行采集后端。

---

## §4 设备段结果读取与状态映射

### 4.1 CHECK-7（arkts-visual-verify）

| 产物 | 用途 |
|---|---|
| `spec/visual-verify/report.md` | 全局摘要：cache_stats + 各页 pass/fail |
| `spec/fix/round-N/ui/ALIGN_*.md` | 单条差异 markdown（一差异一文件，schema 见 visual-verify 自身 references）|
| `spec/fix/round-N/ui/{URL,CRASH}_*.md` | 不可达 / 崩溃记录 |

**状态映射**（CHECK-7 按失败性质分级——页面打不开/崩溃不是"视觉问题"）：

- 无 ALIGN/URL/CRASH 失败文件 → **PASS**
- 仅存在 ALIGN（纯视觉差异）→ **FAIL-visual**（不阻塞门控、不进回环；差异列表写入 verify-report.md，由用户或后续 a2h-fixer 离线处理）
- 存在 URL_* / CRASH_*（页面不可达/崩溃 = 功能性失败）→ **FAIL-functional**（阻塞门控，按 `failure-loop.md` 进 §5 老路径修复；ALIGN 部分仍只记录）
本项源设备自动操作不可用于 iOS；当前所需观察记 not_run，读取已有独立源证据。

> visual-verify 不带循环。产出 markdown 后即退出；a2h-verify **不在本 CHECK 内**派 fixer——
> CRASH/URL 的修复走 §5 回环（委托 a2h-execute），不是在本 CHECK 内重试。

---

## §5 设备段状态合法集

| CHECK | 合法状态 | 备注 |
|---|---|---|
本项源设备自动操作不可用于 iOS；当前所需观察记 not_run，读取已有独立源证据。

**禁止**：`NOT EXECUTED` / `SKIPPED for time` / `主线程自定义 SKIP` 不是合法状态；产出即视为流程未走完，必须补跑。

---

## §6 配置

- CHECK-6 路由：唯一必传参数是 `--ios-root`，其余路径 router-verify 自推导；换仓适配点（`FIRST_PARTY_PKGS` / ALIAS / ENTRY 等）见 `arkts-router-verify/references/config.md`。
