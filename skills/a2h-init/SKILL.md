---
name: a2h-init
description: "iOS→HarmonyOS 迁移第 0 步（初始化）：核对 iOS 源根与鸿蒙目标根、探测 macOS+Xcode 与目标工具能力，用 init 写入身份并经 harness-init 检查源分析配置，validate 单独报告目标构建准入。当用户说“初始化”“开始迁移”“init”或首次运行 a2h-run/spec 时使用；路径变化、源工程更换或 Xcode 环境变化时可重跑。不要用于：源理解与规格生成（用 a2h-spec）、计划（用 a2h-plan）、执行迁移（用 a2h-execute）。"
metadata:
  type: pipeline
  domain: migration
  tags:
  - ios
  - pipeline
  - migration
  layer: pipeline
---

本统一版本先读 [单一流程、环境前置与兼容范围](../a2h-run/references/unified-workflow.md)；其中明确的写入、准备时机和行为范围规则优先于下文的旧调用示例。


> **派发约定**：本 skill **不派发 subagent**，全部步骤在主会话执行。它只做只读探测、按已有授权确认输入、调用 init/harness-init/doctor/validate 本包命令——不写产品文件、不建 spec 业务产物。
>
> 路径约定：`$IOS_SRC` = iOS 源码根；`<target>` = 鸿蒙目标工程根；`<runtime>` = 本包 runtime（`scripts/a2h_ios.py` 所在根）。本 skill 写入 `<target>/.migbot/config.json`、`spec/reports/init-environment.json` 及清单内受控工具元数据：身份字段由 init 写，harness 标记由 harness-init 写；不手改配置、不动源/目标代码。历史v1迁移需单独的显式导入，不能在初始化中自动代做。

# a2h-init — 迁移初始化与环境确认

## 0. 定位与纪律

- 输入：用户提供的 iOS 源路径、鸿蒙目标路径；已有 `<target>/.migbot/config.json`（若有）。
- 输出：`<target>/.migbot/config.json`（init写身份，harness-init写harness标记）+ init 最终报告。收尾跑 `mark-stage a2h-init`。
- **顺序固定**：遥测状态（§3）→ 源根确认（§4）→ 目标根确认（§5）→ hvigor/DevEco/hdc 环境事实（§6）→ **macOS+Xcode 能力探测（§7）** → 写 config（§8）→ 最终校验（§9）→ 最终报告（§10）。任何一步不许跳过。
- 唯一交互点 = 路径确认各步的 `(keep / <new path>)` 提问；其余禁交互追问。
- **第一条可见输出必须是**一行初始化计划（§3→§4→§5→§6→§7→§8→§9），然后才开始 §1。
- 硬约束：**不写账号密码、证书私钥到配置**；**不因初始化覆盖源/目标代码**；**缺工具写 unavailable，不生成虚假路径**；**重复运行幂等**（§Notes）。

## 1. 宿主 shell 选择（读此节后再跑任何命令）

命令统一写成 **Python runtime 调用**，bash 与 PowerShell 形式等价（macOS 的 `python` 指 python3）：

| bash 形式（macOS / Linux） | PowerShell 形式（Windows） |
|---|---|
| `python <runtime>/scripts/a2h_ios.py <cmd> …` | `python <runtime>\scripts\a2h_ios.py <cmd> …` |
| `test -d "<p>"` | `Test-Path -LiteralPath "<p>" -PathType Container` |
| `test -f "<p>"` | `Test-Path -LiteralPath "<p>" -PathType Leaf` |
| `command -v xcodebuild` | `(Get-Command xcodebuild -ErrorAction SilentlyContinue).Source` |

**Windows 上不要通过 bash 探测任何路径**（bash 可能解析到 WSL，看不到 `C:\`；issue #41 同源事故）。

## 2. 本包 runtime 与读取现有配置

1. 定位 `<runtime>`：工作区安装在 `.hmigbot-ios/plugin` 时取该目录；插件原目录本身就是 runtime。两个都查不到 → 停止并提示重新安装本包，**禁止**用别的 `a2h_ios.py` 凑数（runtime 版本必须一致）。
2. 读 `<target>/.migbot/config.json`（存在时），解析：`source_platform`、`ios`、`harmonyos`、`language`、`confirmed`、`telemetry_consent`。
   - **现有 `source_platform` 非 `ios`，或 `ios` 与本次用户给的源路径不同 → 先报告具体冲突，得到用户明确答复才继续**。禁止静默改写（已有 baseline 的 success 状态不能沿用到换源后的工程）——此约束与 init 命令内置检查一致（`Source changed: review the existing baseline`）。
   - 已有确认路径与授权时直接复用，不重复询问；身份冲突才确定恢复范围。

## 3. 遥测状态检查（先于一切路径提问，不阻断）

已明确要求完整用量/时间目标且目标根已知时，先执行 `usage-start --project <target> --run-id <run-id>`，再做任何环境盘点与准备；复用当前已启动 run，不重置计时。若缺少目标根，先取得必要定位，并将未覆盖的前置时间如实标为 UNKNOWN，不从首次派发倒推起点。

本包遥测**默认 `denied` 且不阻断流水线**（与原 HMigBot 的"不同意就不能用"模型不同）：

- 读 `telemetry_consent`：`denied`/缺失 → 一行说明 `"遥测默认关闭（telemetry_consent: denied）。usage-* 账本为本地记录，不上传。"` 并继续。
- `granted` → 一行说明 `"遥测已授权（consented at <telemetry_consent_at>）。"` 并继续。
- **本 skill 不询问、不修改 consent**（变更由用户在包文档规定的位置自办）。

## 4. 确认 `ios` 源根

显示：`Detected iOS source: <ios>`（无值或路径不存在则 `iOS source not detected.`）。

跑 `test -d "<ios>"` 并做 iOS 工程 marker 探测（**任一命中即算工程证据；marker 只是线索，不推导必能编译**）：

| # | Marker | 含义 |
|---|---|---|
| 1 | `<ios>/*.xcodeproj` 或 `*.xcworkspace` | Xcode 工程 |
| 2 | `<ios>/Package.swift` | SwiftPM 清单 |
| 3 | `<ios>/Podfile` | CocoaPods 依赖 |

报告：`✔ path exists（Xcode project / SwiftPM / Podfile 证据：…）` / `✘ path missing`。然后问：

> `"Use this path, or enter a different one? (keep / <new path>)"`

`keep` → 保留；其他输入 → 视为新路径并重跑 `test -d`；仍缺失 → 警告 `"该路径不存在。仍使用？(yes / no)"`，`no` 重问、`yes` 接受。

**iOS 源不必在本机可编译**（iOS 与 Android 的实质差异）：源在 Mac/Xcode 编译属正常；init 只确认路径与工程 marker。识别 Xcode project/scheme/target 的入口语义留给 `source-index`（a2h-spec 阶段）。

## 5. 确认 `harmonyos` 目标根

显示：`HarmonyOS root: <harmonyos>`（几乎总是 `.`）。跑 `test -d` 与 `test -f "<harmonyos>/oh-package.json5"`：

- 两者存在 → `✔ HarmonyOS project detected`
- 目录存在但无 oh-package.json5 → `⚠ directory exists but no oh-package.json5 found`
- 缺失 → `✘ path missing`

问法同 §4。**目标根与源根必须互不包含**（§0 硬约束）：违反时报告并拒绝写入，由用户改路径。

## 6. hvigor / DevEco / hdc 环境事实（记录，不写 config）

初始化命令负责config.json中的源/目标身份字段（§8），harness-init另写其既有控制标记；hvigorw、node、SDK、hdc 属环境事实，由 `doctor` 每次显式探测或经 `--hvigor/--sdk/--node/--ohpm` 显式传入，不在此步骤伪造或覆盖配置。init 的职责是**如实记录并报告**：

1. 探测链（静默依序，首个命中即停）：

| 项 | 候选（依序） |
|---|---|
| hvigorw | `<harmonyos>/hvigorw` → `<harmonyos>/hvigorw.bat` → `<deveco>/tools/hvigor/bin/hvigorw[.bat]` |
| DevEco | 用户此前提供/常见安装位（`D:\codetool\DevEco Studio`、`/Applications/DevEco-Studio.app` 等） |
| node/ohpm | `command -v node` / `command -v ohpm` |
| hdc | `command -v hdc` → `<deveco>/Contents/sdk/default/openharmony/toolchains/hdc`（macOS）→ `$HOME/Library/Huawei/Sdk/openharmony/toolchains/hdc` |

   `.bat` 用 `test -f`，其余 `test -x`（Windows 统一 `Test-Path -PathType Leaf`，§1）。
2. 每个探测结果给用户一行结论（`✔ hvigorw: <path>` / `✘ hvigorw not found (candidates: …)`），追问只对"是否使用此路径"做确认（`keep / <new path> / skip`）；**skip 只影响后续 build/设备验证，不影响源分析起步**。
3. 缺失结论全部并入最终报告的能力清单（§10），不落 config、不伪造。

## 7. macOS+Xcode 能力探测（iOS 特有，必做）

按「真实 iOS 开发 = macOS + Xcode」场景，init **必须**区分并记录四类能力的三态：`available`（本机探测到）/ `configured`（用户已配置）/ `executed`（本轮实际执行过）。

1. **宿主能力协商（权威来源）**：跑 `python <runtime>/scripts/a2h_ios.py doctor --project <target>`（只读），读其 `host_profile`：
   - macOS + `xcodebuild` + `xcrun` 可用 → **native 候选能力 available**；后续仍须真实执行provider并验证其结果，不能仅据探测声称已有工程成员/符号绑定证据；
   - Windows / macOS 无 Xcode → 源解析走 **static 回退**（`ios.swift_compiler_context: unavailable`）。
2. 显式探测（仅 macOS；Windows 直接记 unavailable）：

```bash
command -v xcodebuild; command -v xcrun; command -v swift
```

   - Apple 官方 skills（Xcode 27）：`available` = `xcrun agent skills export` 可执行；未导出 → `apple_skills.status=not_loaded`（不阻断）。实际加载在 a2h-spec 阶段按 `ios-source-analysis` 的接入规程做。
   - Xcode MCP：仅当用户在宿主已配置（如 `codex mcp add xcode -- xcrun mcpbridge`）才记 `configured`；能探测到 xcrun ≠ 已连通 MCP，未连通记 `xcode_mcp.status=unavailable`。
3. **云构建日志不能代替 iPhone 安装/功能验证**（`cloud.macos_build` 与真机验证分开记录）——这是 iOS 迁移的固定红线，最终报告必须单列。
4. 探测结果随 §9 校验一并写入最终报告；本包 provenance（`ios-analysis-provenance.json`）由 spec 阶段正式落盘。

## 8. 写 config（唯一写者 = init 命令）

```bash
python <runtime>/scripts/a2h_ios.py init --source "<ios>" --project "<target>"
```

- 命令写：`source_platform=ios`、`ios`、`harmonyos`、`language`（缺省 zh）、`telemetry_consent`（缺省 denied）、`confirmed`。**`confirmed` 由命令保持现状**；本包不设 confirmed=true 门槛。源分析起步检查用 §9 的 `harness-init`，目标构建准入单独由 `validate` 判断。
- **禁止手 Edit 该文件**（init 是唯一写者）。路径含空格时整体加引号。
- 命令报错（典型：Android 旧配置、源根改变）→ 读错误原文按 §4/§5 修正后重跑，最多 2 轮；仍失败 → 记欠账并如实呈报，不硬闯。

## 9. 最终校验

在 harness/任何原生载荷之前，执行 `python <runtime>/scripts/a2h_ios.py init-environment --project <target>` 盘点，说明动作后在已有授权内加 `--prepare` 准备。显式用量目标的 usage-start 必须先于这次必要准备。清单外/外部 runtime 不修复；报告各能力缺口。

1. **源分析配置门**：`python <runtime>/scripts/a2h_ios.py harness-init --project <target>`。exit 0 仅说明源/配置可进入 a2h-spec，不证明源理解完整或可编译；非0则保留错误，修配置或按现有显式导入协议处理，不能越过。已有v2配置可幂等重跑；仍由spec阶段执行source-index与后续源合同门。
2. **目标构建准入**：`python <runtime>/scripts/a2h_ios.py validate --project <target>`。exit 0 仅说明构建工具路径与配置检查通过；非0列出真实失败项及恢复条件。缺 hvigor/build-profile **不阻断源分析**；保持目标构建 blocked，执行构建前必须修复并重跑到 exit 0，不伪造路径或削弱 validate。
3. `python <runtime>/scripts/a2h_ios.py doctor --project <target>`：读 `overall` 与 `host_profile`，把可用/缺失/下一步分源分析、目标构建、设备验证写进最终报告。doctor 只统计，**绝不递归扫盘、绝不运行 Swift**。
4. 本轮要求用量目标时，在必要 init 准备之前按主控计量规程启动 `usage-start --project <target> --run-id <本轮run-id>`；若账本不可用，源检查结果仍可报告，但用量完整性为UNKNOWN，不能声明满足Token目标。账本不会自动证明全部宿主调用均已采集。

## 10. 最终报告（必带三块）

- **能力清单**：ios/harmonyos 路径与工程 marker、hvigor/DevEco/hdc 环境事实、Xcode/Apple skills/MCP 三态、native候选能力与实际执行证据、static回退及可执行阶段（缺 hvigor 时标注"目标编译暂缺工具"）。
- **遥测状态块**：`Current state: <denied (default — nothing uploaded) / granted>`。本包遥测默认关闭、不阻断任何阶段。
- **下一步**：`a2h-run` 或单独 `a2h-spec`。

## Notes

- 路径输入原样保留（相对路径按安装目录解析，为用户可移植性保留；不自动转绝对）。
- 配置由 init/harness-init 各自按既有责任写入；不手改 `.agents/`、源/目标代码或控制账本。
- 重复运行幂等：confirmed 已 true 时按 §2 的 yes/no 分支走；源更换先重审旧 baseline（§2/§8 双保险）。
- 无待迁移源工程时仍可完成环境自检；不创建虚构应用 baseline。
- Xcode project/scheme/target、`CFBundleDisplayName` 等源内事实由 `source-index`/spec 阶段提取，init 不预先解析。

---

## 收尾：上报本阶段用量

本 skill 的最后一步（无论单独触发还是经 a2h-run）：

```bash
.migbot/bin/a2h mark-stage a2h-init
```

标记 `a2h-init` 阶段水位（写 stage-marks fact，受授权门控、尽力而为）。token 用量由宿主生命周期采集，本步不采集。**忽略其退出码，绝不阻断流水线。**
