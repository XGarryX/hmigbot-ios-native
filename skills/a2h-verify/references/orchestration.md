> **当前发行 profile：设备/视觉后端延期。** `arkts-scenario-runner`、`arkts-visual-verify`、`arkts-ui-verifier`、`ios-screenshot-analyzer`（及历史 Android 截图别名）和 `scenario-builder` / `visual-fixer` / `visual-fixer-reviewer` 未作为本包可运行能力交付。不得调用、派发、要求安装或因其缺件阻断基本转换/构建/报告。相关本次实际调用记 deferred/not_run；可只读消费开发者提供的外部原始证据，核对源/目标版本、配置、范围和来源，保留外部实际结果，不能写成本工具已实测。没有证据不记 PASS，真实已归因产品失败继续保留。下文相关调用/目录仅为未来兼容标记。

> **iOS 源输入**：读取 Swift/Objective-C、SwiftUI/UIKit、Xcode 工程及原生资源；实际源构建与设备观测依赖可用的源平台环境。鸿蒙侧构建和验收保持原流程。源侧操作详见 `ios-source-analysis/SKILL.md`。

# 与 Domain Skill 的关系

> 配合 SKILL.md §7 使用。a2h-verify 是**验证编排层**，不实现修复逻辑、不持有循环；本文件描述 a2h-verify 编排的所有 Domain Skill。

---

## 编排关系图

```
a2h-verify（编排层）
  │
  ├─ $hmos-fix-build-errors   — 全量编译修复（CHECK-1，主对话内联）
  ├─ $arkts-knowledge-verifier — 编译升级诊断 + 静态分析辅助（CHECK-1/2，主对话内联）
  ├─ $arkts-app-identity       — App 身份校验（CHECK-4，主对话内联）
  ├─ $arkts-router-verify      — 路由跳转验证 + 内置修复闭环（CHECK-6，纯静态，主对话内联）
  ├─ 外部视觉证据             — CHECK-7 deferred/not_run（内置后端延期）
```

> 原 `$arkts-spec-evolver`（旧编号下的 Spec 覆盖率审计）已随该 CHECK 删除而移除编排——覆盖率由 CHECK-5 覆盖（CHECK-6 功能验收已摘除，见 _dormant/check6-functional/）。

a2h-verify **不再直接派 `Agent(a2h-fixer)` 或 `Agent(a2h-diagnoser)`**。修复执行者实际是各 verifier 自带的 agent（router 的工作包修复 agent），由各自内部循环调度；`a2h-fixer` 仅保留"visual ALIGN 差异离线消费者"一个角色（用户按需触发，不在本流程编排内）；`a2h-diagnoser` 在 v13 编排中无调用方。

---

## 调用模型规则

- **Skill(...)**：domain 知识封装，主对话进入 skill 上下文执行；产出留在主对话，可被后续步骤直接读取
- **CHECK-6 路由（router-verify）纯静态，不碰设备**：先于设备段跑（修复会改源码，让设备验证跑在修过路由的代码上），与设备段之间无串行/sleep 约束
- 设备段 skill（visual / ut / ui）**严格串行**调用，每段后 sleep 5（设备静默 + uitest daemon 排空）；不得同一条消息派发

**Domain Skill 缺失时没有 SKIP**（CHECK-1~7 均无 SKIP 状态，见 `execution-discipline.md` §1.1），按下表处置：

| 缺失的 Skill | 受影响 CHECK | 处置 |
|---|---|---|
| hmos-fix-build-errors | CHECK-1 | **编译验证照跑**（主线程直接跑 hvigor 编译）；缺的只是自动修复能力，编译失败如实标 FAIL |
| arkts-knowledge-verifier | CHECK-1/2 | CHECK-1 失去升级诊断（仍可 FAIL 收口）；CHECK-2 的 grep 规则在 `checks-1-to-5.md` 内自含，照跑 |
| arkts-app-identity | CHECK-4 | 校验规则在 `checks-1-to-5.md` 内自含，主线程直接执行，照跑 |
| arkts-router-verify | CHECK-6 | DEFERRED（原因：verifier skill 未安装）|
| arkts-visual-verify（延期） | CHECK-7 | deferred/not_run，不要求补装；可消费开发者外部原始证据 |

本项源设备自动操作不可用于 iOS；当前所需观察记 not_run，读取已有独立源证据。

---

## 产物目录约定

**两个 verifier 产物目录互相独立，无共写、无共享状态文件**（route 收口在 `spec/verify/` 下，visual 独占 `spec/fix/`）：

| Skill | 写入目录（独占根） | 产物 |
|---|---|---|
| arkts-router-verify | `spec/verify/route/` | `ROUTE_VERIFY_SUMMARY.md` / `fix_plan.json` / `reachability_robust.json` 等 |
| arkts-visual-verify | `spec/fix/round-N/ui/` | `ALIGN_*.md` / `URL_*.md` / `CRASH_*.md`（自有 `spec/fix/_state.yaml` 管轮次）|

> **schema 注意**：各 skill 自带 `references/fix-file-schema.md`，读文件时以产出方 skill 的 schema 为准
> （visual 的 `kind` 含 `ALIGNMENT_DIFF / URL_MISMATCH / CRASH / SYSTEMIC` 等）。router 与 visual 目录彻底分离，
> a2h-verify 读取时无需做 `source:` 过滤。

---

## 职责分工

- **a2h-verify**：编排顺序、编译短路与终态编译复检（§3.0）、读各 verifier 产物、聚合报告、门控判定、门控后 verified 回写（§6.1）、失败回环（CHECK-1~5 + CHECK-7 的 CRASH/URL 功能性子类）
- **arkts-router-verify**：双端控件级导航图抽取 + 三视角对账 + triage + agent 分派修复 + 复检收口（纯静态，自管闭环）
- **视觉后端（延期）**：本profile不采集、不派发fixer；只读消费外部证据并保留真实差异与功能性失败，不冒称本工具复测。
