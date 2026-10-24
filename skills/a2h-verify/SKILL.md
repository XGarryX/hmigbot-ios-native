---
name: a2h-verify
description: "iOS→HarmonyOS 迁移第四步（Verify）：验证迁移产出，执行静态分析与 App 身份校验（源身份取自 Info.plist/Xcode 构建变量/Asset Catalog，Swift/ObjC、SwiftUI/UIKit），并由用户选择视觉对齐、单元测试和行为验证，汇总所选范围内的真实结果。当用户说“验证迁移结果”“跑一下验证”或在迁移上下文中说“验证”“测试”时触发。不要用于：生成迁移规格（用 a2h-spec）、执行迁移代码（用 a2h-execute）、已有规格的增量修改。"
metadata:
  type: pipeline
  domain: migration
  tags:
  - ios
  - verify
  - pipeline
  - migration
  layer: pipeline
---

本统一版本先读 [单一流程、环境前置与兼容范围](../a2h-run/references/unified-workflow.md)；其中明确的写入、准备时机和行为范围规则优先于下文的旧调用示例。


> **调用关系**：本 skill 主会话执行，**不派发三写 worker 子代理**。用户选中的视觉/UT 验证委托对应 verifier skill（CHECK-3 → `arkts-visual-verify`、CHECK-4 → `arkts-ut-verifier`），其内部测试设计、构建、设备执行与修复由各 skill 契约调度，a2h-verify 只编排与汇总、不另派同类 fixer。行为验证由本包 `behavior-check` 命令执行，**只报告、不参与整体判定**。
>
> **路径约定**：`$IOS_SRC` 读 `<target>/.migbot/config.json` 的 `ios` 字段；`<runtime>` = 本包 runtime（`scripts/a2h_ios.py` 所在根）。源端无 Mac/设备不妨碍可执行的目标检查；缺失的已选检查记 DEFERRED/PARTIAL，**不能**自动改成 SKIP。本 skill 不写产品代码；唯一主会话写的文件是 `spec/verify-report.md`（汇总结论），派生产物由 `spec-summary`/`migration-report` 命令单写。

# a2h-verify

Pipeline 第四步，负责基础检查与可选检查的编排和结果汇总。静态分析与 App 身份校验在主对话执行；用户选中的视觉、UT、行为验证按各自契约完成。

## 0. 定位与纪律

- **前置**：`<target>/.migbot/config.json` 存在且 `source_platform=ios`；验证默认作用于当前迁移产出（模块/页面/功能范围由本次选择定）。
- **输入**：鸿蒙工程根、待验证模块、用户指定范围；仅为本次执行项定位 iOS 源码根、页面清单、UI Spec 与功能 Spec，**不要求额外执行报告作为启动凭证**。
- **输出**：`spec/verify-report.md`（五项结果与证据汇总）+ 派生产物 `spec/reports/spec-summary.json`、`spec/migration-report.md`。
- **唯一交互点 = 开始前的可选检查选择**（CHECK-3/4/5 选哪些，见 §1）；其余禁交互追问，机械检查由 exit code 判定（behavior-check：0=PASS，2=FAIL，3=UNVERIFIED）。
- **第一条可见输出必须是一行执行计划**（固定 CHECK-1/2 → 已选 CHECK 的相对顺序），然后才开始 §1。
- **硬约束**：**不手改派生报告**（`spec/migration-report.md` 由命令单写，`verify-report.md` 由 verify-report 命令单写，当前 verifier 结果与范围写入其受校验输入）；**不把未选 CHECK 改判为已执行**；**不把结构 PASS 或安装成功升格为行为一致**；**源截图仅用真实 iPhone/Xcode/云运行材料，无源截图不生成虚假视觉一致率**；CHECK-5 不参与整体判定。

## 0.1 分步命令表（实际执行的命令，每条带 exit code）

| 阶段 | 命令 | 产物 | exit 语义 | 失败处置 |
|---|---|---|---|---|
| CHECK-5 行为验证(可选) | `python <runtime>/scripts/a2h_ios.py behavior-check --project <target>`；只有已授权实际用例才加 `--run` | `spec/reports/ios-behavior-check.json` | 0=PASS；2=FAIL；3=UNVERIFIED | 只报告，不触发修复回环、不参与整体判定 |
| 派生汇总 | `python <runtime>/scripts/a2h_ios.py spec-summary --project <target> --output <target>/spec/reports/spec-summary.json` | `spec/reports/spec-summary.json` | 0=生成；非0=FAIL | 修复输入后重跑，最多 2 轮 |
| 迁移报告生成 | `python <runtime>/scripts/a2h_ios.py migration-report --project <target> --output <target>/spec/migration-report.md` | `spec/migration-report.md` | 0=生成；非0=FAIL | 同上 |
| 迁移报告一致性 | `python <runtime>/scripts/a2h_ios.py migration-report --project <target> --check <target>/spec/migration-report.md` | 校验回执 | 0=current；非0=不一致 | 重新生成并重检，**禁止**手填状态消除差异 |

- 有当前真实构建 JSON 报告时，后三条追加 `--build-evidence <build-report.json>`；缺少则不传，**不从 verifier 的文字 PASS 或旧 verified 推定构建已验证**。
- CHECK-1/2 与 CHECK-3/4 无对应本包命令：CHECK-1/2 按 `references/static-and-identity.md` 静态扫描执行；CHECK-3/4 委托 verifier，结果读各自报告（见 §3）。

## 0.2 无人值守处置阶梯（E266，适用于 CHECK-1/2/3 的修复回环）

> 失败 → 按失败来源归属（`references/failure-loop.md`）生成修复任务并回到对应处理；外层回环**最多 3 轮**。3 轮、无可执行修复、缺外部条件或需产品决策 → 结束自动回环，保留准确的失败与未验证范围。**任何分支不得停机呈报人工**；CHECK-5 的 FAIL/UNVERIFIED 只报告、不进入该回环。

- CHECK-1 静态 ERROR / CHECK-2 身份 FAIL：任务允许修复时生成执行阶段修复任务，否则记失败结束。
- CHECK-3 功能性失败 → 读 visual verifier 修复与复测结果，仍需执行阶段处理的进外层回环；纯 ALIGN 差异记建议项。
- CHECK-4 由 UT verifier 按选定模式处理，a2h-verify 不包一层同类 fix-loop。
- 输入缺失/设备不可用/执行环境失败 → 写明恢复条件，**不把基础设施故障转成补业务代码任务**。

## 0.6.0 控制面入口

先读取 [iOS Harness v2](../ios-source-analysis/references/harness-v2.md)，以该协议决定输入、机器门禁和状态写者。以下原领域规程继续用于规格内容、indexed 计划、接线和真实验证；不得再手工调度或写入三份控制账本。

原真实验证继续执行。行为范围已明确选中时运行 `behavior-check` 校验事件/持久化效果链（CHECK-5）；只有已有授权的实际用例才用 `--run`，保留独立源 oracle。未运行、未覆盖和环境不足仍为 UNVERIFIED，不受旧 PASS 或 task done 影响。

## 1. 开始前：选择可选检查项

开始任何 CHECK 前，先确定本次执行范围。CHECK-1/2 固定执行；CHECK-3/4/5 可任选、组合或全部不选。

若用户已明确指定（如“只跑 UT”“跑 3、4、5”“全部执行”），直接采用该可选检查选择。否则先用多选交互询问，选项仅显示检查编号和名称，不追加括号说明：

> 本次要执行哪些可选检查？可多选：CHECK-3 视觉对齐、CHECK-4 单元测试、CHECK-5 行为验证。也可以回复“全部”或“都不选，仅做 CHECK-1/2”。

无多选工具时用普通文本提问，接受编号或名称组合。收到有效选择后再开始执行；未回复不默认全选。选择只决定执行哪些 CHECK，各 verifier 的修复模式仍按当前任务意图确定。

未选项记为 SKIP（用户未选择），不检查其前置条件、不启动其 verifier、不复用其旧报告。未选 CHECK-5 也不跑 `behavior-check`、不读 `spec/verification/ios-behavior.json`、不读历史行为报告。选择在本次修复和复检中保持不变；用户明确调整时再更新。

“只跑 UT”选 4，“行为验证 / Behavior Verify / 跑效果检查”选 5，“全部执行”选 3/4/5，固定 1/2 始终执行。全选不授权 CHECK-5 第二轮。只验证、不改产品代码的任务选中 CHECK-5 时，`--run` 仅限已有授权且具备独立源 oracle 的用例；其余保持 not_run（当前能力与只读约束不兼容），不调用默认修复流程或虚构 verify_only。

用户明确要求页面导航或 UI 功能验证时，独立调用 `arkts-ui-verifier`，遵循其模式和授权范围；该结果单独报告，不自动增加本流程的 CHECK 项。

## 2. 输入与范围

- 确认鸿蒙工程根目录、待验证模块和用户指定范围；默认验证当前迁移产出。
- 仅为本次执行项从当前任务、工程记录或 `spec/baseline/` 定位所需的 iOS 源码根目录、页面清单、UI Spec 与功能 Spec，不要求额外的执行报告作为启动凭证。
- 某项输入、设备或 verifier 缺失时，记录该项受影响范围和恢复条件，继续其他可执行项。CHECK-3/4 的输入和设备要求见 [设备验证](references/device-verification.md)；CHECK-5 见 §3 与 `behavior-check` 语义，源端无 Mac/设备不妨碍可行的目标检查，缺失记 DEFERRED/PARTIAL。

## 3. 五项检查

执行 CHECK-1/2，再按 CHECK-3 → CHECK-4 → CHECK-5 的相对顺序执行已选项；每项结束后立即读取实际产物并记录结论。

| 编号 | 检查项 | 执行方式 | 通过条件 |
|---|---|---|---|
| CHECK-1 | 静态分析 | 扫描并复核迁移代码中的类型、导入、SQL、动态执行和生命周期用法 | ERROR 为 0；WARN 附报告 |
| CHECK-2 | App 身份校验 | 检查应用配置、名称和图标资源；源身份从 Info.plist/Xcode 构建变量/Asset Catalog 取得 | FAIL 为 0；WARN 附报告 |
| CHECK-3 | 视觉对齐 | `arkts-visual-verify` | 完成范围内实测且无未解决差异；纯 ALIGN 差异记建议项 |
| CHECK-4 | 单元测试 | `arkts-ut-verifier` | 全范围实际 GREEN，无未验证设计点 |
| CHECK-5 | 行为验证（可选） | `behavior-check` 一次调用（`--run` 仅限已授权实际用例） | 只报告设置/点击稳定终态与链校验；不判全域 PASS，不参与整体判定 |

CHECK-1/2 的具体规则见 [静态分析与 App 身份](references/static-and-identity.md)。CHECK-3/4 的模式、产物和状态映射见 [设备验证](references/device-verification.md)。

**CHECK-5 行为验证语义（iOS）**：

- 命令 `python <runtime>/scripts/a2h_ios.py behavior-check --project <target>` 读 `spec/verification/ios-behavior.json`（`schema_version=2`、`source_sha256` 钉当前独立源快照），校验事件/持久化效果链与用例、写 `spec/reports/ios-behavior-check.json`。
- 默认不加 `--run`：只做结构校验并报告 `not_run`；加 `--run` 时仅对已获授权的实际用例执行进程观察，保留独立源 oracle（`oracle.source_fact` + `reviewer`），执行后复核源/目标未被进程副作用改动。
- exit 语义：`0=PASS`（无失败且无待覆盖 AC）、`2=FAIL`（有失败规则）、`3=UNVERIFIED`（存在未覆盖 AC）。未运行、未覆盖、环境不足仍为 UNVERIFIED，**不受旧 PASS 或 task done 影响**。
- **行为验证只报告、不参与整体判定**：CHECK-5 状态单列“行为验证结果（非门控）”，安装成功或局部点击通过仍为 WARN，设置正确性未验证；其 FAIL/UNVERIFIED 不触发 §0.2 外层回环。

## 4. 执行与修复

1. 执行 CHECK-1/2，记录文件位置、复核依据与问题级别。
2. 将工程路径、验证范围和当前任务的修复约束传给已选 verifier。UT 默认 `verify_fix`，仅验证时使用 `verify_only`。
3. 按 visual → UT → behavior-check 的相对顺序串行执行已选项；设备交接前确认前一 verifier 真实退出并释放设备，静默 5 秒。CHECK-5 一次调用、默认不加 `--run`（single-round）；未选项保持 SKIP，全部不选则汇总基础检查。
4. 每段结束后读取本次报告、当前轮摘要和必要证据，保留原始状态。verifier 的内部修复由其自身调度，a2h-verify 不另派同类 fixer，也不重置内部轮数。
5. 仍需由执行阶段处理的失败按 [失败处理](references/failure-loop.md) 回到 `a2h-execute`；CHECK-5 状态不触发该回环。包括 CHECK-5 在内的源码修复结束后，复检 CHECK-1、受影响的 CHECK-2 及已选 CHECK-3/4；未复测的受影响设备项记 PARTIAL，已确认失败保留。
6. 汇总到 `spec/verify-report.md`，使用 [报告模板](references/verify-report-template.md)。结束前实际执行 §0.6.0 之后的派生汇总、迁移报告生成与一致性检查，读取产物并在验证报告中链接；本轮未选或未跑范围保持原状态。

构建、签名和安装由所选 verifier 按自身契约处理；构建或运行失败按实际结果记录，不新增独立编译检查。后续修复改变已测代码或配置时，复检受影响项；未复检的旧结果注明未覆盖当前改动。

## 5. 结果判定

| 单项状态 | 含义 |
|---|---|
| PASS | 约定范围内验证完成且通过；非阻塞 WARN 可随附 |
| FAIL | 已确认检查失败或验证执行失败，注明产品、测试或环境原因 |
| PARTIAL | 已执行一部分，但仍有未验证、待复核或未覆盖当前改动的范围 |
| DEFERRED | 因输入、设备或 skill 等前置缺失而未执行，注明恢复条件 |
| SKIP | 用户未选择的 CHECK-3/4/5，不参与本次结论计算 |
| FAIL-visual | CHECK-3 仅有 ALIGN 纯视觉差异，作为建议项 |
| FAIL-functional | CHECK-3 存在崩溃、目的页不匹配或功能缺失等已确认问题 |
| WARN / ERROR | CHECK-5 的未验证修复 / 流程或结果错误；仅报告，其 SKIP/DEFERRED 同样不参与整体判定 |

基础及已选视觉/UT 范围结论仅根据 CHECK-1/2 和已选 CHECK-3/4 计算；排除 CHECK-5 的全部状态：

- 存在 FAIL 或 FAIL-functional → **FAIL**。
- 没有上述失败，但存在 PARTIAL 或 DEFERRED → **PARTIAL**，明确尚未验证的范围。
- 其余情况 → **PASS**；存在 WARN 或 FAIL-visual 时标注“通过，附建议项”。

已选项未生成报告、修复文件已写入或问题文件目录为空，都不能据此判 PASS。报告明确写出执行项与未选项；PASS 仅表示本次范围通过，存在未选项时不能描述为所有五项均已验证。CHECK-5 单列“行为验证结果（非门控）”；安装成功或局部点击通过仍为 WARN，设置正确性未验证。

**完整迁移验收边界**：上述局部verify语义保持不变；局部PASS、ALIGN建议、未选CHECK或CHECK-5非门控结果都不能推出UI准确率/功能完备度100%。完整结论须以独立源审定的全部必验页面/状态/条件和业务AC为分母，绑定当前源、目标产物、构建与真实视觉/行为证据；not_run、未知、缺端、陈旧、失败及尚未解决差异都保留。当前逐页visual仍为not_run，没有已实现的自动完整验收profile可以冒称通过。后续实现严格终局生产者/消费者前，只能报告真实已验范围与完整验收缺口；两个100%的全部必验验证须计入同一2小时挑战。

## 阶段证据

CHECK 汇总与修复复检结束后，主线程依次实际运行以下命令；`<target>` 为绝对目标路径。有当前真实构建 JSON 报告时，三条均追加相同 `--build-evidence <build-report.json>`；缺少则不传，不从 verifier 的文字 PASS 或旧 verified 推定构建已验证。

```text
python <runtime>/scripts/a2h_ios.py spec-summary --project <target> --output <target>/spec/reports/spec-summary.json
python <runtime>/scripts/a2h_ios.py migration-report --project <target> --output <target>/spec/migration-report.md
python <runtime>/scripts/a2h_ios.py migration-report --project <target> --check <target>/spec/migration-report.md
```

读取命令退出码、summary 的逐页 `page_id/plan_item_refs/task_ids/target_paths/ac_ids` 及独立生成/编译/行为/视觉轴，将两份派生产物路径与实际检查结果写进 `spec/verify-report.md`。`--check` 从当前证据重算；过期或手改时修复证据、重新生成并重检，不能手填状态消除差异。工具汇总不能代替 CHECK-1/2 或各 verifier；结构仍独立引用真实结构检查。

生成须有冻结计划、当前回执/产物摘要和原内核成功落账。编译为全工程构建输入覆盖声明页面文件，不证明页面可达或交互有效。行为按本页真实 AC 观测分配，不从全局 PASS 推给未测页面；host 逻辑测试不充作设备 UI。当前逐页视觉轴为 not_run，真实视觉结果继续引用选中 verifier 的本轮报告，不能回填派生状态。未知、未执行、未落账与过期结论均保留；用户未选择的 CHECK 不据此改成已执行。

## 读取时机（references）

| 触发时机 | 必读文件 |
|---|---|
| CHECK-1/2 执行规则、级别与判定 | references/static-and-identity.md |
| CHECK-3/4 调用准备、产物与状态映射 | references/device-verification.md + references/ios-source-protocol.md |
| 失败归属、外层回环与复检范围 | references/failure-loop.md |
| 汇总五项结果与证据 | references/verify-report-template.md |
| harness v2 协议（机器门禁与状态写者） | ../ios-source-analysis/references/harness-v2.md |

## 交接

- **闸门**：`spec/verify-report.md` 已产出且 §0.6.0/阶段证据 的派生汇总与一致性检查实际执行过，才完成本阶段。验证结论不因 mark-stage 或迁移报告而改判；未选/未跑范围在报告中明确为 SKIP/PARTIAL/DEFERRED。
- **移交产物**：`spec/verify-report.md`、`spec/reports/spec-summary.json`、`spec/migration-report.md`、`spec/reports/ios-behavior-check.json`（选中 CHECK-5 时）。
- **下一步**：下游按报告结论决定是否回 `a2h-execute` 修复（§0.2 外层回环），或进入 `a2h-retrospect` 复盘（同会话可直接续跑）。

---

## 收尾：上报本阶段用量

本 skill 的最后一步（无论经 a2h-run 还是单独触发）：

```bash
.migbot/bin/a2h mark-stage a2h-verify
```

标记 `a2h-verify` 阶段水位（写 stage-marks fact，受授权门控、尽力而为）。阶段水位用于识别本阶段已结束，**不将 FAIL、PARTIAL 或未选项改判为 PASS**；通过范围仍以本次报告为准。token 用量由宿主生命周期采集，本步不采集。**忽略其退出码，绝不阻断流水线。**
