> **当前发行边界：旧设备/视觉后端延期，官方应用测试单独取证。** `arkts-scenario-runner`、`arkts-visual-verify`、`arkts-ui-verifier`、`ios-screenshot-analyzer`（及历史 Android 截图别名）和 `scenario-builder` / `visual-fixer` / `visual-fixer-reviewer` 尚未恢复交付，不调用或要求补装这些旧后端，也不因其缺件阻断基本转换/构建/报告。指定应用/模拟器的官方截图、控件查询和固定回放按执行交界合同及实际适配入口运行，不因旧后端延期或缺少桌面屏幕权限一概记 not_run。许可、宿主可用、已实现、实际执行与验收结果分开；缺真实后端/输入仅限制对应检查。外部原始证据核对版本、配置、范围和来源，未执行不记 PASS，真实产品失败保留。下文旧调用/目录仅为兼容映射。

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
  ├─ $arkts-router-verify      — 路由静态检查与报告消费（CHECK-6，主流程实际调用）
  ├─ 官方应用测试/配对证据      — CHECK-7 按实际范围/结果；旧视觉后端延期
```

> 原 `$arkts-spec-evolver`（旧编号下的 Spec 覆盖率审计）已随该 CHECK 删除而移除编排——覆盖率由 CHECK-5 覆盖（CHECK-6 功能验收已摘除，见 _dormant/check6-functional/）。

a2h-verify **不再直接派 `Agent(a2h-fixer)` 或 `Agent(a2h-diagnoser)`**。CHECK-6 报告入口不派修复 agent，真实缺陷按原任务责任、写权和受影响复查规程处理；`a2h-fixer` 仅保留"visual ALIGN 差异离线消费者"一个角色（用户按需触发，不在本流程编排内）；`a2h-diagnoser` 在 v13 编排中无调用方。

---

## 调用模型规则

- **Skill(...)**：domain 知识封装，主对话进入 skill 上下文执行；产出留在主对话，可被后续步骤直接读取
- **CHECK-6 路由（router-verify）纯静态，不碰设备**：先做当前静态检查；若后续修复源码，重验路由和受影响构建后再消费设备证据，与设备段之间无串行/sleep 约束
- 设备段 skill（visual / ut / ui）**严格串行**调用，每段后 sleep 5（设备静默 + uitest daemon 排空）；不得同一条消息派发

**Domain Skill 缺失时没有 SKIP**（CHECK-1~7 均无 SKIP 状态，见 `execution-discipline.md` §1.1），按下表处置：

| 缺失的 Skill | 受影响 CHECK | 处置 |
|---|---|---|
| hmos-fix-build-errors | CHECK-1 | **编译验证照跑**（主线程直接跑 hvigor 编译）；缺的只是自动修复能力，编译失败如实标 FAIL |
| arkts-knowledge-verifier | CHECK-1/2 | CHECK-1 失去升级诊断（仍可 FAIL 收口）；CHECK-2 的 grep 规则在 `checks-1-to-5.md` 内自含，照跑 |
| arkts-app-identity | CHECK-4 | 校验规则在 `checks-1-to-5.md` 内自含，主线程直接执行，照跑 |
| arkts-router-verify | CHECK-6 | DEFERRED（原因：verifier skill 未安装）|
| arkts-visual-verify（延期） | CHECK-7 | deferred/not_run，不要求补装；可消费开发者外部原始证据 |

旧 Android 设备脚本不能用于 iOS。指定 iOS 测试应用按当前官方适配器及已确认范围执行，或读取可核验独立源证据；未执行不写 PASS，只有一端不记双端通过。

---

## 产物目录约定

**两个 verifier 产物目录互相独立，无共写、无共享状态文件**（route 收口在 `spec/verify/` 下，visual 独占 `spec/fix/`）：

| Skill | 写入目录（独占根） | 产物 |
|---|---|---|
| arkts-router-verify | `spec/verify/route/` | `ios-route-check.json` / `ROUTE_VERIFY_SUMMARY.md` / `runs/<id>/` |
| arkts-visual-verify | `spec/fix/round-N/ui/` | `ALIGN_*.md` / `URL_*.md` / `CRASH_*.md`（自有 `spec/fix/_state.yaml` 管轮次）|

> **schema 注意**：各 skill 自带 `references/fix-file-schema.md`，读文件时以产出方 skill 的 schema 为准
> （visual 的 `kind` 含 `ALIGNMENT_DIFF / URL_MISMATCH / CRASH / SYSTEMIC` 等）。router 与 visual 目录彻底分离，
> a2h-verify 读取时无需做 `source:` 过滤。

---

## 职责分工

- **a2h-verify**：编排顺序、编译短路与终态编译复检（§3.0）、读各 verifier 产物、聚合报告、门控判定、门控后 verified 回写（§6.1）、失败回环（CHECK-1~5 + CHECK-7 的 CRASH/URL 功能性子类）
- **arkts-router-verify**：随包目标导航图抽取 + 当前已审 iOS 源事实对账 + 输入/证据绑定；正式报告自动消费，修复按原写权另行执行
- **应用视觉证据**：指定测试应用的官方适配器按真实入口、当前构建和检查点取证；配对必须有对应两端证据。旧视觉后端和 fixer 角色仍延期，不据此禁止新适配器；外部证据标明来源，不冒称本工具采集/复测。
