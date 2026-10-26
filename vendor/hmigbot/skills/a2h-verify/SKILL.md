---
name: a2h-verify
description: 第四步：验证 Android→HarmonyOS 迁移产出，执行静态分析与 App 身份校验，并由用户选择视觉对齐和单元测试，汇总所选范围内的真实结果。当用户说“验证迁移结果”“跑一下验证”或在迁移上下文中说“验证”“测试”时触发。
metadata:
  type: pipeline
  domain: migration
  tags:
  - pipeline
  - migration
---
# a2h-verify

Pipeline 第四步，负责基础检查与可选设备验证的编排和结果汇总。静态分析与 App 身份校验在主对话执行；用户选中的视觉、UT 委托对应 verifier，具体测试设计、构建、设备执行和内部修复按各 skill 的契约完成。

## 开始前：选择设备验证项

开始任何 CHECK 前，先确定本次执行范围。CHECK-1/2 固定执行；CHECK-3/4 可任选、组合或全部不选。

若用户已明确指定（如“只跑 UT”“跑 3、4”“全部执行”），直接采用该设备验证选择。否则先用多选交互询问：

> 本次要执行哪些设备验证？可多选：CHECK-3 视觉对齐、CHECK-4 单元测试。也可以回复“全部”或“都不选，仅做 CHECK-1/2”。

无多选工具时用普通文本提问，接受编号或名称组合。收到有效选择后再开始执行；未回复不默认全选。选择只决定执行哪些 CHECK，各 verifier 的修复模式仍按当前任务意图确定。

未选项记为 SKIP（用户未选择），不检查其前置条件、不启动其 verifier、不复用其旧报告。选择在本次修复和复检中保持不变；用户明确调整时再更新。

用户明确要求页面导航或 UI 功能验证时，独立调用 `$arkts-ui-verifier`，遵循其模式和授权范围；该结果单独报告，不自动增加本流程的 CHECK 项。

## 输入与范围

- 确认鸿蒙工程根目录、待验证模块和用户指定范围；默认验证当前迁移产出。
- 仅为本次执行项从当前任务、工程记录或 `spec/baseline/` 定位所需的 Android 源码根目录、页面清单、UI Spec 与功能 Spec，不要求额外的执行报告作为启动凭证。
- 某项输入、设备或 verifier 缺失时，记录该项受影响范围和恢复条件，继续其他可执行项。各 verifier 的输入和设备要求见 [设备验证](references/device-verification.md)。

## 四项检查

执行 CHECK-1/2，再按 CHECK-3 → CHECK-4 的相对顺序执行已选项；每项结束后立即读取实际产物并记录结论。

| 编号 | 检查项 | 执行方式 | 通过条件 |
|---|---|---|---|
| CHECK-1 | 静态分析 | 扫描并复核迁移代码中的类型、导入、SQL、动态执行和生命周期用法 | ERROR 为 0；WARN 附报告 |
| CHECK-2 | App 身份校验 | 检查应用配置、名称和图标资源 | FAIL 为 0；WARN 附报告 |
| CHECK-3 | 视觉对齐 | `arkts-visual-verify` | 完成范围内实测且无未解决差异；纯 ALIGN 差异记建议项 |
| CHECK-4 | 单元测试 | `arkts-ut-verifier` | 全范围实际 GREEN，无未验证设计点 |

CHECK-1/2 的具体规则见 [静态分析与 App 身份](references/static-and-identity.md)。CHECK-3/4 的模式、产物和状态映射见 [设备验证](references/device-verification.md)。

## 执行与修复

1. 执行 CHECK-1/2，记录文件位置、复核依据与问题级别。
2. 将工程路径、验证范围和当前任务的修复约束传给已选 verifier。UT 默认 `verify_fix`，仅验证时使用 `verify_only`。
3. 按 visual → UT 的相对顺序串行执行已选设备项；两项均选时，visual 退出并释放设备后静默 5 秒，再启动 UT。只选一项时直接执行该项，全部不选时直接汇总基础检查。
4. 每段结束后读取本次报告、当前轮摘要和必要证据，保留原始状态。verifier 的内部修复由其自身调度，a2h-verify 不另派同类 fixer，也不重置内部轮数。
5. 仍需由执行阶段处理的失败按 [失败处理](references/failure-loop.md) 回到 `a2h-execute`；修复后复检受影响项。
6. 汇总到 `spec/verify-report.md`，使用 [报告模板](references/verify-report-template.md)。

构建、签名和安装由设备 verifier 在执行测试时处理；构建或运行失败按实际结果记录，不新增独立编译检查。后续修复改变已测代码或配置时，复检受影响项；未复检的旧结果注明未覆盖当前改动。

## 结果判定

| 单项状态 | 含义 |
|---|---|
| PASS | 约定范围内验证完成且通过；非阻塞 WARN 可随附 |
| FAIL | 已确认检查失败或验证执行失败，注明产品、测试或环境原因 |
| PARTIAL | 已执行一部分，但仍有未验证、待复核或未覆盖当前改动的范围 |
| DEFERRED | 因输入、设备或 skill 等前置缺失而未执行，注明恢复条件 |
| SKIP | 用户未选择的 CHECK-3/4，不参与本次结论计算 |
| FAIL-visual | CHECK-3 仅有 ALIGN 纯视觉差异，作为建议项 |
| FAIL-functional | CHECK-3 存在崩溃、目的页不匹配或功能缺失等已确认问题 |

整体结论仅根据 CHECK-1/2 和已选设备项计算：

- 存在 FAIL 或 FAIL-functional → **FAIL**。
- 没有上述失败，但存在 PARTIAL 或 DEFERRED → **PARTIAL**，明确尚未验证的范围。
- 其余情况 → **PASS**；存在 WARN 或 FAIL-visual 时标注“通过，附建议项”。

已选项未生成报告、修复文件已写入或问题文件目录为空，都不能据此判 PASS。报告明确写出执行项与未选项；PASS 仅表示本次范围通过，存在未选项时不能描述为所有四项均已验证。

## 收尾：盘库与阶段水位

成功产出 `spec/verify-report.md` 后，作为本 skill 的最后一步依次执行以下命令。每条命令均忽略退出码，不阻断交付，也不改变报告中的验证结论。

```bash
# 1. 统计 Android 与 HarmonyOS 两侧代码行
.migbot/bin/a2h count-lines

# 2. 标记本阶段水位
.migbot/bin/a2h mark-stage a2h-verify
```

`count-lines` 写入两侧代码行数，必须先于 `mark-stage a2h-verify`，确保阶段水位落库时行数已就位。阶段水位用于服务端识别本阶段已经结束，不将 FAIL、PARTIAL 或未选项改判为 PASS；通过范围仍以本次报告为准。token、subagent 和 skill 维度用量由生命周期 hook 上传的会话记录在服务端解析，本步骤不运行 CC 的 metrics 上传命令。

## 参考文件

| 文件 | 用途 |
|---|---|
| [静态分析与 App 身份](references/static-and-identity.md) | CHECK-1/2 执行规则 |
| [设备验证](references/device-verification.md) | CHECK-3/4 调用与结果读取 |
| [失败处理](references/failure-loop.md) | 外层修复范围、退出条件和复检 |
| [报告模板](references/verify-report-template.md) | 四项结果与证据汇总 |
