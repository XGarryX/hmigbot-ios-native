---
name: a2h-init
description: Trigger: `$a2h-init` or natural language. Confirm auto-detected ios / harmonyos / hvigorw / deveco / hdc paths in plain language. Run on first install or whenever the paths change.
---

> **iOS 源输入**：读取 Swift/Objective-C、SwiftUI/UIKit、Xcode 工程及原生资源；实际源构建与设备观测依赖可用的源平台环境。鸿蒙侧构建和验收保持原流程。源侧操作详见 `a2h-spec/references/native-input.md`。

# a2h-init — native iOS input

## 0. 环境先行

先读 [原生输入协议](../a2h-spec/references/native-input.md)，运行 `python3 .agents/hmigbot-runtime/scripts/ios_input.py environment`。本发行版面向 Mac：通过 Xcode / xcrun 核实开发者目录、Swift 编译器与 iOS SDK；需要时命令级设置 DEVELOPER_DIR，不推定全局 xcode-select 已选择完整 Xcode。技术发现、配置查询、源 App 编译与运行分别记录。路径已由用户指定或确认时直接复用。

## 1. Provision runtime and read current config

运行安装包的 a2h-bootstrap（Windows 使用 .ps1，其他系统使用脚本），本地创建缺失配置，保留已有配置和自定义字段，不安装遥测 hooks。配置读取 `source_platform`、`ios.source_root`、`harmonyos`、`deveco`、`hvigorw`、`hdc`、`language`、`confirmed`。

## 2. 数据设置

默认本地执行、不上传。参与上游计划不是本地迁移前提；不自动调用 privacy accept 或 flush，不更改用户已有同意记录。

## 3. Path confirmation + iOS Release context

尚未确认时展示检测到的 iOS 源路径，校验目录并允许用户修改；已确认时询问是否重确认，已有授权直接复用。检查真实 Xcode/SwiftPM 工程标志，列出产品 target 是技术发现。记录已有 Release 配置导出路径，校验其内容类别；不要在 INIT 决定迁移哪些产品或能力。

Mac 上使用真实 Xcode 捕获：`python3 .agents/hmigbot-runtime/scripts/ios_input.py capture-release --src <源根> --project <工程.xcodeproj> --scheme <实际scheme> --build --out <新的包外捕获目录>`。保存实际 Release 构建与 SwiftDriver 参数。SPEC 确认 target 后，用该捕获执行 `prepare-source --src <源根> --project-root <目标根> --bundle <捕获目录> --variant <variant.json> --out <新的source-view目录>`，自动构建当前 Xcode provider，不传 `--provider`。已有捕获可在原完整性校验通过且源码未变时复用；不要补写缺省 flags 或构建通过记录。

## 4. Confirm `harmonyos`

Show: `HarmonyOS root: <harmonyos>` (almost always `.`).

Run `test -d "<harmonyos>"` and `test -f "<harmonyos>/oh-package.json5"`. Report:

- both exist → `✔ HarmonyOS project detected`
- dir exists, no `oh-package.json5` → `⚠ directory exists but no oh-package.json5 found`
- missing → `✘ path missing`

Ask: `"Use this path, or enter a different one? (keep / <new path>)"`. Same handling as step 3.

## 5. Confirm DevEco install path

Read the `deveco` field. `install.sh` auto-detects DevEco by scanning `$PATH`, then platform-appropriate locations (Windows: C/D/E/F drives; macOS: `/Applications`; Linux: `/opt`, `/usr/local`).

**If `deveco` is non-empty**, show: `DevEco install: <deveco>` and run `Bash: test -d "<deveco>"`.

- exists → `✔ DevEco directory found`
- missing → `✘ path no longer exists`

Then ask: `"Use this DevEco path, keep it, or override? (keep / <new path> / clear)"`.
- `keep` → retain.
- `<new path>` → replace; re-test with `test -d`.
- `clear` → set to empty string; treat as "skip".

**If `deveco` is empty** (auto-detection failed at install time), tell the user:

> `DevEco install path was not auto-detected on this machine. Please tell me where DevEco Studio is installed (e.g. "D:\\codetool\\DevEco Studio" or "/Applications/DevEco-Studio.app"), or type "skip" to leave it empty.`

- Plain path → run `test -d`; if missing, warn and ask again.
- `skip` → leave empty. Step 6 will then have to fall through to asking the user for hvigorw directly.

`deveco` is recorded so step 6 below (and any future tooling) can locate DevEco's bundled hvigor without re-scanning.

## 6. Confirm `hvigorw` (resolution chain)

`hvigorw` is the build wrapper. Standard HarmonyOS projects ship one at the project root, but some templates ship only `hvigorw.bat`, and others rely on DevEco's bundled hvigor. Walk this chain — **try silently in order, stop at the first hit**:

| # | Candidate                                            | Notes                                  |
|---|------------------------------------------------------|----------------------------------------|
| 1 | `hvigorw` field value (if non-empty)                 | Explicit user override; relative paths resolve against install dir |
| 2 | `<harmonyos>/hvigorw`                                | Project-local POSIX wrapper            |
| 3 | `<harmonyos>/hvigorw.bat`                            | Project-local Windows batch            |
| 4 | `<deveco>/tools/hvigor/bin/hvigorw`                  | DevEco-bundled POSIX wrapper (on macOS, deveco already includes `/Contents`) |
| 5 | `<deveco>/tools/hvigor/bin/hvigorw.bat`              | DevEco-bundled Windows batch           |

Test rules:
- For non-`.bat` candidates, use `Bash: test -x "<path>"`.
- For `.bat` candidates, use `Bash: test -f "<path>"` (the `-x` bit is unreliable for batch files on Windows / Git Bash).
- On Windows both collapse to `Test-Path -LiteralPath "<path>" -PathType Leaf` (§0). Never probe a `C:\` path through `bash`.

When a candidate hits, that becomes the **resolved hvigorw**.

### 6.1 If a candidate hit

Report: `✔ hvigorw resolved: <path> (candidate #N)`.

Ask: `"Use this hvigorw, or override? (keep / <new path>)"`.
- `keep` → write the resolved path into the `hvigorw` field. Use absolute path when the candidate is outside `<harmonyos>` (i.e. candidates 4-5); use relative form (`hvigorw` or `hvigorw.bat`) for candidates 2-3; preserve the original value for candidate 1.
- `<new path>` → validate with the same `test -x` / `test -f` rule. If valid, store as override.

### 6.2 If no candidate hit

Report:
> `✘ hvigorw not found in any of the standard locations:
>   - <harmonyos>/hvigorw
>   - <harmonyos>/hvigorw.bat
>   - <deveco>/tools/hvigor/bin/hvigorw[.bat]   (deveco = "<deveco-or-empty>")`

If `deveco` is empty (or `clear`-ed in step 5), tell the user: `"DevEco install path is not set, so I couldn't check candidates 4-5. If you want me to use DevEco's bundled hvigor, give me the DevEco install dir; otherwise give me the full path to a working hvigorw[.bat]."`

Then ask: `"Path? (or 'skip' to leave hvigorw empty — build will fail until you fix this)"`.

- Path looks like a DevEco install dir (contains `tools/hvigor`) → set `deveco` field, then re-run candidates 4-5 from the chain above.
- Path looks like a direct hvigorw[.bat] → validate with `test -x` / `test -f`, store as override.
- `skip` → leave `hvigorw` empty. Continue to step 7.

## 7. Source observation and hdc

若有 Simulator/iPhone/Xcode 观测材料，记录位置；没有则记录不可用，源端运行验证稍后记 DEFERRED，不伪造。鸿蒙 hdc 沿用原解析链：

### 7.2 `hdc`

Try to auto-detect — **stop at the first hit**:

| # | Candidate | Notes |
|---|-----------|-------|
| 1 | `hdc` field value (if non-empty and executable) | Explicit user override in config.json |
| 2 | `command -v hdc` | Already on PATH |
| 3 | `<deveco>/Contents/sdk/default/openharmony/toolchains/hdc` | DevEco-bundled hdc (macOS) |
| 4 | `$HOME/Library/Huawei/Sdk/openharmony/toolchains/hdc` | Standalone HarmonyOS SDK |

If a candidate hits, report: `✔ hdc resolved: <path> (candidate #N)`.

Ask: `"Use this hdc, or override? (keep / <new path> / skip)"`.
- `keep` → write resolved path into `hdc` field (leave empty for candidate 2).
- `<new path>` → validate with `test -x`; if missing, warn and re-ask.
- `skip` → leave `hdc` empty.

If no candidate hits and `deveco` is empty, hint: `"DevEco install path is not set, so I couldn't check DevEco-bundled hdc. Provide the full path to hdc, a DevEco install dir, or type 'skip'."`.

If user gives a DevEco install dir → set `deveco` field, re-run candidate 3.

## 8. Write config + mark confirmed

只修改已确认字段，保留其余键。`source_platform="ios"`；`ios.source_root` 保存用户路径，`ios.configuration="Release"`；尚未确认迁移范围时不写 variant.targets。`harmonyos/hvigorw/deveco/hdc/language` 沿用原约定，最后 `confirmed=true`。

## 9. Final validation

运行 a2h-tool validate（Windows 使用 .ps1）检查路径；鸿蒙可构建性由 $a2h-build 的真实构建验证。原 `a2h init-run`、`a2h count-lines`、`a2h mark-stage a2h-init` 是最佳努力的本地阶段记录，保留原顺序，忽略非关键统计失败；默认拒绝上传。不得手工编造完成哨兵。

## 10. Final report

报告路径、环境、Swift、Xcode 配置输入状态和真正执行过的检查。下一步可运行 $a2h-build 或 $a2h-spec；规格范围由 SPEC 确认。本轮只初始化时正常结束，不额外要求范围选择。
