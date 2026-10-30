> **当前发行边界：旧设备/视觉后端延期，官方应用测试单独取证。** `arkts-scenario-runner`、`arkts-visual-verify`、`arkts-ui-verifier`、`ios-screenshot-analyzer`（及历史 Android 截图别名）和 `scenario-builder` / `visual-fixer` / `visual-fixer-reviewer` 尚未恢复交付，不调用或要求补装这些旧后端，也不因其缺件阻断基本转换/构建/报告。指定应用/模拟器的官方截图、控件查询和固定回放按执行交界合同及实际适配入口运行，不因旧后端延期或缺少桌面屏幕权限一概记 not_run。许可、宿主可用、已实现、实际执行与验收结果分开；缺真实后端/输入仅限制对应检查。外部原始证据核对版本、配置、范围和来源，未执行不记 PASS，真实产品失败保留。下文旧调用/目录仅为兼容映射。

> **iOS 源输入**：读取 Swift/Objective-C、SwiftUI/UIKit、Xcode 工程及原生资源；实际源构建与设备观测依赖可用的源平台环境。鸿蒙侧构建和验收保持原流程。源侧操作详见 `ios-source-analysis/SKILL.md`。

# CHECK-6 / 7：路由静态检查与应用证据

配合 SKILL.md §3b 使用。以下是 0.13.6 实际执行协议；旧七步模型在环修复示例不代表报告命令已执行修复。

## §0 执行总序

主流程按当前页面/导航事实选择 CHECK-6，实际调用随包 `hmos_extract.py` 及 `hmos_reachability.py` 目标注册扫描，对照当前 iOS 源事实和已审 Spec 映射，消费结果到正式报告。检查只写派生产物，不改业务代码。若后续修复源码，先重跑本检查与受影响构建，再消费相应应用证据。

## §1 CHECK-6：当前静态执行协议

### 1.1 输入及来源

使用项目当前配置中的 iOS 源路径、有效 `ios-facts.json`、当前页面 Spec 和执行合同。Spec 作者在 Plan 冻结前形成 `spec/verification/ios-routing.json`，逐条绑定所有 navigation fact；具体字段及来源规则见 [路由技能](../../arkts-router-verify/SKILL.md) 开头 0.13.6 协议。Plan 冻结其摘要。源事实未覆盖、映射未审或输入已变时保留 DEFERRED，禁止用目标代码倒推期望源边。旧 Android 源抽取器不用于 iOS。

### 1.2 实际调用

存在页面或导航输入的正常 `verify-report` / `gate-artifacts` 默认执行 CHECK-6 并消费当前结果。独立复验命令：

```sh
python3 <runtime>/scripts/a2h_ios.py route-verify --project <target>
```

`route-verify --check` 及报告只读检查不启动抽取器，只核对当前证据及输入摘要；显式范围未选 CHECK-6 不调用。无需设备或编译成功即可检查静态源码。检查崩溃、超时或缺源证据不会复用旧 PASS。

### 1.3 产物与状态

| 产物 | 用途 |
|---|---|
| `spec/verify/route/ios-route-check.json` | 当前输入绑定、实际命令、退出码、findings、gaps、证据摘要；CHECK-6 正式消费入口 |
| `spec/verify/route/runs/<id>/` | 本轮实际目标导航图、目标注册扫描、stdout/stderr、源导航待对账清单 |
| `spec/verify/route/ROUTE_VERIFY_SUMMARY.md` | 管理标记内追加本轮状态；保留已有人工修复历史 |

- PASS：已审当前源边全部覆盖、静态目标绑定及注册通过，且无证据缺口。仅证明本轮静态范围。
- FAIL：源期望路由缺失、按钮未绑定/死 Builder、已解析页面未注册等当前真实缺陷，阻断对应门控。
- DEFERRED：源未审、覆盖不完整、输入过期、抽取器失败、动态目标未解析，或参数/返回/模态语义缺独立证据。已选项报告保持 PARTIAL，并给出恢复条件。

静态 PASS 不证明设备可达、参数传递、返回状态恢复或完整导航语义。设备不可用本身不阻止静态检查。

### 1.4 修复与关闭

按本轮 findings 的原任务责任和冻结写权执行必要修复；源/Spec 问题回原作者，不在目标侧掩盖。修复后重跑同一 `route-verify` 和受影响构建，逐条原缺陷消失才关闭。`fix_plan.json`、旧 `reachability_robust.json` 或人工声明不能替代当前正式结果。报告命令本身不自动派修复 agent，也不写业务代码。

---

## §2 CHECK-7：应用运行与视觉证据

旧 visual/UI/scenario 后端和三个延期角色不调用、不要求补装。新的官方应用截图、控件查询和固定回放按明确的应用/模拟器/场景、实际入口和当前构建执行；未选不调用，已选但缺真实后端/输入的子项保留具体 deferred/not_run，不能因旧后端延期或没有桌面屏幕权限一概跳过。基本转换、当前SDK构建、路由静态检查与报告继续。

开发者可提供外部已有报告及原始截图/日志/trace文件。仅核对其实际源/目标版本、配置、页面/场景范围、产生工具与结果，按外部证据如实引用；不冒称本工具完成采集或复测，输入已变的旧观察不得直接当作当前通过。没有外部证据保持未验证，真实已证产品缺陷保留。

以下历史产物路径只用于外部证据映射及未来兼容，不代表本profile已装可运行采集后端。

---

## §4 设备段结果读取与状态映射

### 4.1 CHECK-7（当前配对证据与旧后端兼容映射）

| 产物 | 用途 |
|---|---|
| `spec/visual-verify/report.md` | 全局摘要：cache_stats + 各页 pass/fail |
| `spec/fix/round-N/ui/ALIGN_*.md` | 单条差异 markdown（一差异一文件，schema 见 visual-verify 自身 references）|
| `spec/fix/round-N/ui/{URL,CRASH}_*.md` | 不可达 / 崩溃记录 |

**状态映射**（CHECK-7 按失败性质分级——页面打不开/崩溃不是"视觉问题"）：

- 已明确范围的检查点均有当前源/目标构建绑定、真实执行及配对通过证据，且没有未解决的已确认差异 → **PASS**；缺少失败文件本身不能证明通过
- 仅存在 ALIGN（纯视觉差异）→ **FAIL-visual**（不阻塞门控、不进回环；差异列表写入 verify-report.md，由用户或后续 a2h-fixer 离线处理）
- 存在 URL_* / CRASH_*（页面不可达/崩溃 = 功能性失败）→ **FAIL-functional**（阻塞门控，按 `failure-loop.md` 进 §5 老路径修复；ALIGN 部分仍只记录）
旧 Android 设备脚本不能直接用于 iOS；指定 iOS 测试应用使用官方测试适配器，或读取可核验的独立源证据。未实际执行不记 PASS，只有源端证据不能记双端视觉通过。

> visual-verify 不带循环。产出 markdown 后即退出；a2h-verify **不在本 CHECK 内**派 fixer——
> CRASH/URL 的修复走 §5 回环（委托 a2h-execute），不是在本 CHECK 内重试。

---

## §5 设备段状态合法集

| CHECK | 合法状态 | 备注 |
|---|---|---|
旧 Android 设备脚本不能直接用于 iOS；指定 iOS 测试应用使用官方测试适配器，或读取可核验的独立源证据。未实际执行不记 PASS，只有源端证据不能记双端视觉通过。

当前公开状态沿用 `PASS` / `FAIL` / `DEFERRED` / `NOT_APPLICABLE` 及选择范围合同，未选与已选未执行分开。`NOT_APPLICABLE` 需要当前检查证据和真实理由；时间不足、缺设备或缺证据不能伪装成通过，也不由本文件增加全局补跑门。真实已绑定失败保留。

---

## §6 配置

- CHECK-6 独立入口必传 `--project <target>`；源与目标从当前配置读取。`--check` 为只读验证。不存在当前入口可用的 `--ios-root` 参数，不沿用旧 Android 扫描配置。
