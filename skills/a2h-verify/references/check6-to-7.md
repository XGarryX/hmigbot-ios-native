> **可执行设备探针**：`probe_devices.py --project-root <本工程> --json [--serial <目标>]` 已有 iOS 分支。原0/10/20枚举保留，source_setup=pending表示须进入Phase1实际build/create/start；exit2工具错误不能当DEFERRED。旧CHECK-8 wire在本iOS契约对应CHECK-7 visual，当前输出明确映射。

> **.33 可执行分支**：CHECK-6 的 iOS 源 producer/裁决/弹窗/薄壳入口见 [native-route-source](../../arkts-router-verify/references/native-route-source.md)。CHECK-7 的 Xcode 构建、独占 source Simulator、真实观察与 canonical 桥接见 [native-xcode-source](../../arkts-visual-verify/references/native-xcode-source.md)。本文件下方 adb 条件仅属历史 Android 分支；iOS 以真实 Xcode provider/source session 与目标 HDC 状态判前置，provider 错误不当作 DEFERRED。

> **iOS 源输入**：读取 Swift/Objective-C、SwiftUI/UIKit、Xcode 工程及原生资源；实际源构建与设备观测依赖可用的源平台环境。鸿蒙侧构建和验收保持原流程。源侧操作详见 `a2h-spec/references/native-input.md`。

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

> **DEFERRED 仅在"拿不到 iOS 源码仓"或"skill 未安装"时合法**。注意 CHECK-6 **不依赖 hdc/adb**——
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

## §2 CHECK-7 前置条件检测（设备段）

**前置 0（编译门禁，最先查）**：设备段要 build+install HAP，因此 **CHECK-1 终态编译必须可过**才跑它们。
- CHECK-1 编译 FAIL → 本轮**跳过设备段**，进 SKILL.md §5 老路径先修编译再重跑（CHECK-6 路由静态，不受影响照常跑）
- §5 回环耗尽仍编不过 → 设备段标 `DEFERRED（编译未过）`，不空转
- CHECK-6 改完源码后，按 §3.0 重跑一次终态编译复检，门控以复检结果为准

**前置 0.5（skill 安装检测 + 显式禁用）**：由下方 `probe_devices.py` **一并机械判定**，读 JSON `checks` 即可，
不要自己 `ls` 兄弟目录：
- 对应 verifier skill（visual / ut / ui）未安装 → 该 CHECK 标 `DEFERRED（verifier skill 未安装：<name>）`；

编译可过后，**跑机械探针，按退出码路由**——不要自己 `which` / 搜路径 / 数 "device" 行：

```text
[历史源平台示例：不适用于 iOS，不可执行。iOS 源设备/构建按本文件适配及 native-input 协议；目标 hdc/hvigor 检查仍须实际执行。]
python3 $SKILLS_ROOT/a2h-verify/scripts/probe_devices.py          # 默认每条探针 10s 硬超时
#   0  ALL_READY         hdc+adb 都可用且各有在线设备 → CHECK-7 全部跑
#  10  HMOS_ONLY         只有鸿蒙端在线            → CHECK-7 DEFERRED（visual 需双端）
#  20  HMOS_UNAVAILABLE  hdc 缺 / 超时 / 无设备     → CHECK-7 全部 DEFERRED
# stdout 一行 JSON：hdc/adb 路径、resolved、在线设备列表、*_timed_out、checks{CHECK-7: RUN|DEFERRED(原因)}
```
> **为什么改成脚本**（2026-08-17 用户实报"设备前置检查跑了 20+ 分钟没结果"）：
> 此前这里是一段让模型自主执行的伪代码，三个结构性的慢——
> ① 只列了 macOS/Linux 路径，**Windows 上模型只能自己搜盘**（`dir /s /b hdc.exe`，10-20 分钟起步）；
> ② `hdc list targets` / `adb devices` **无超时**，hdc 服务端陈旧/挂死时无限期阻塞，模型就干等；
> ③ 每条命令一次模型往返。脚本三平台候选表定位（含 Windows）+ 每条 10s 硬超时 + 一次出结论，秒级。
> **DEFERRED 的原因字符串直接抄 JSON 里 `checks` 的值**（区分"hdc 没找到 / 超时 / 有工具无设备"，
> 三者处置不同：设 env HDC / `hdc kill` 重试 / 起模拟器）。

探针内部等价逻辑（供排障，**不要手动执行**）：hdc 按 env `HDC` → PATH → DevEco 安装根下的固定相对位置
（macOS `/Applications/DevEco-Studio.app/Contents/sdk/default/openharmony/toolchains/`、
Windows `%ProgramFiles%\Huawei\DevEco Studio\sdk\...`、Linux `~/command-line-tools/sdk/...`）；
# 原源平台历史命令（iOS 按本文件适配说明执行）: adb 按 env `ADB` → PATH → `$IOS_HOME/platform-tools` → 平台默认位。在线判定：
`hdc list targets` 非空且不含 Empty；`adb devices` 状态列为 `device`（排除 offline/unauthorized）。

> DEFERRED 仅在对应前置不满足时合法（工具不可用 / 编译未过 / skill 未安装，完整集见 `execution-discipline.md` §1.3）。其他情况必须出 PASS 或 FAIL；不允许"省时 SKIPPED"。

---

## §3 设备段串行执行编排

设备 verifier 严格串行，主线程内联调用：

```pseudocode
probe = json(python3 $SKILLS_ROOT/a2h-verify/scripts/probe_devices.py)   # §2 的探针结果，checks 里已含 设备/skill/暂停/禁用 四类判定
# CHECK-7：视觉对齐（一次性，无循环）
if probe.checks["CHECK-7"] == "RUN":   # 由 probe_devices.py 判：双端在线 + skill 已装 + 未暂停/禁用
    $arkts-visual-verify        # 写 spec/fix/round-N/ui/{ALIGN,URL,CRASH}_*.md
    sleep 5                            # 设备静默
    读 spec/visual-verify/report.md → 立即落状态:
        无失败文件 → PASS
        仅 ALIGN → FAIL-visual（不门控）
        存在 CRASH/URL → FAIL-functional（门控阻塞，进 §5 回环）
else:
    CHECK-7: DEFERRED

```

**铁律**（违反即流程作废）：

1. **设备段 visual 跑完 sleep 5** 再进后续步骤（设备静默 / uitest daemon 排空）；今后若增设备类 verifier，一律串行、不得同一条消息派发

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
- adb 或 hdc 任一不可用 → **DEFERRED**（visual 需双端截图）

> visual-verify 不带循环。产出 markdown 后即退出；a2h-verify **不在本 CHECK 内**派 fixer——
> CRASH/URL 的修复走 §5 回环（委托 a2h-execute），不是在本 CHECK 内重试。

---

## §5 设备段状态合法集

| CHECK | 合法状态 | 备注 |
|---|---|---|
| CHECK-7 | PASS / FAIL-visual / FAIL-functional / DEFERRED | DEFERRED 仅 adb 或 hdc 任一不可用 / 编译未过 / skill 未安装；FAIL-functional（CRASH/URL）阻塞门控 |

**禁止**：`NOT EXECUTED` / `SKIPPED for time` / `主线程自定义 SKIP` 不是合法状态；产出即视为流程未走完，必须补跑。

---

## §6 配置

- CHECK-6 路由：唯一必传参数是 `--ios-root`，其余路径 router-verify 自推导；换仓适配点（`FIRST_PARTY_PKGS` / ALIAS / ENTRY 等）见 `arkts-router-verify/references/config.md`。
