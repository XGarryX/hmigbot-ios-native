---
name: hmos-fix-build-errors
description: Build a HarmonyOS project via CLI and automatically fix compile errors in a loop until the build succeeds. Handles ArkTS V2 errors (@ComponentV2/@Local/@Param/@Event/@Once/@Provider/@Consumer/@Monitor/@Computed/@ObservedV2/@Trace/AppStorageV2/PersistenceV2) as well as legacy V1 (@Component/@State/@Prop/@Link/@Provide/@Consume/@Observed/@ObjectLink/@StorageLink/@StorageProp/@Watch). Default unsigned HAP; pass --signed to build a signed HAP (signing config must already exist in the project's build-profile.json5).
metadata:
  type: tool
  domain: engineering
---

> **Codex subagent dispatch convention.** This skill dispatches subagents. In Codex, spawn them with the `spawn_agent` tool and pass `agent_type` = the role name **exactly as written in this skill** — the roles registered under `.codex/agents/*.toml` use the same hyphenated names, so no translation step is involved: `a2h-activity-converter`, `a2h-android-analyzer`, `a2h-closer`, `a2h-fixer`, `a2h-migration-worker`, `ad-profile-builder`, `compose-fact-analyzer`, `hmos-builder`, `scenario-builder`, `visual-fixer`, `visual-fixer-reviewer`. The built-in `general-purpose` agent_type is unchanged. (Claude's `subagent_type` field is written `agent_type` for Codex; `Agent(...)` dispatch calls are `spawn_agent(...)`; there is no `Task` tool in Codex.)
>
> **Join 协议（收口五条款）。** Codex 子代理完成后**不会**唤醒主会话——结果必须由派发方主动收口，违者=静默卡死（实测事故）。
> ① **循环 wait**：每个 `spawn_agent` 句柄用循环调用 `wait_agent` 收口；单次超时只代表"还在跑"，继续再调；**禁止以"等待子代理"为由结束回合**。醒后必调 `list_agents` 确认是谁完成——**完成的唯一合法信号 = `agent_status` 为 `{"completed": …}`，绝不是产物文件的存在/条数**（文件会中途落盘，读半截=实测事故）；completed 态会在数轮后从 list 中消失，所以每次醒来都要及时查。正文所有"等待完成 / join / 到点即收"表述一律指此循环。
> ② **死句柄与验收**：连续 3 次超时后调 `list_agents` 核对，可配 `wait_for_artifact.py` 探产物活性；已 completed 且 summary 可读 → 直接消费；句柄消失且从未观测到 completed → 按断点重派（带原 prompt + 已落盘产物，上限 2 次），禁止继续等待。**completed ≠ 验收通过**：join 点跑 `python3 .agents/skills/a2h-join/scripts/join_gate.py --project .` 验产物完整性，FAIL 视同未取回、按本条重派。
> ③ **收口锚点**：本 skill 最终完成报告前必须收口全部句柄（join_gate exit 0）；正文写明的显式 join 点优先按正文执行。发用户门（Gate）时允许句柄跨 Gate 存活，但 Gate 摘要必须列明未收口句柄清单 + 各自的指定 join 点。
> ④ **放行 ≠ 遗弃**：正文"非阻塞放行/到点即收/降级继续"只推迟收口时机，不豁免收口义务。
> ⑤ **fire-and-forget**：仅正文显式声明"结果丢弃/不 gate"的派发（如 a2h-execute 的 env-prewarm）免收口；审计只认 join_gate 内静态 allowlist，正文声明只是文档层。
> **派发纪律**：`task_name` 必须唯一（带 page-id/slice-id/round-N 后缀）；并行派发前把预期产物清单写 `spec/a2h/_work/expected_<join点>.json`（join_gate 对账用，契约只认派发方、不认子代理自报）；**谁派谁收**——sub-agent 内部需要"等齐 N 片再合并"时禁止嵌套外派后自行退出，要么同步自做、要么把分片清单回报主会话代派（sub-agent 一停止，收口能力即丢）。**契约产物必须出自承担任务的子代理**：重派上限后仍产不出 → 如实报缺并停在未完成态；禁止派发方代写占位产物让 gate 转绿（声明过也不行——绿账必须对应真产物）。

# HarmonyOS Auto Build & Fix

## 调用参数与工具边界（原 Claude Code frontmatter 迁移）

> 下列参数格式与操作边界由已移除的 frontmatter 字段迁移而来，在此以 body 指引形式保留、作为行为约束遵守。

- **参数格式**：`<harmonyos-project-path> <deveco-studio-path> [--signed|--unsigned]`
  - 参数按位置从调用方提示词中获取（Codex 无 slash-command 参数注入，调用时在提示词中依序给出）
- **允许的操作类型**（作为行为约束遵守、非硬性权限）：子代理派发、读取文件、写文件、编辑文件、通配搜索、内容检索、执行 shell。

Automatically build a HarmonyOS NEXT project from the command line, parse compile errors, fix them, and retry — repeating until the build succeeds.

- **HarmonyOS Project**: `$ARGUMENTS[0]` (the HarmonyOS project root, e.g. `D:/MyHmosApp`)
- **DevEco Studio Path**: `$ARGUMENTS[1]` (DevEco Studio installation root, e.g. Windows `D:/DevEco Studio`; macOS `/Applications/DevEco-Studio.app/Contents`)
- **--signed | --unsigned** (optional): `$ARGUMENTS[2]`.
  - omitted → **auto**（默认）：`build-profile.json5` 里签名配置齐全且三份材料文件在本机存在 → 出 **signed HAP**；否则出 unsigned HAP。
  - `--signed` → 强制 signed；签名不齐直接 STOP 报告（Step 0.5）。
  - `--unsigned` → 强制 unsigned（例如只想验证能否编译）。
  - **任何模式下本 skill 都不得修改 `build-profile.json5` 的 `signingConfigs` / `signingConfig`**（见 Step 0 §5 与 Checkpoint Commit）。

---

## Step 0: Validate Inputs & Setup Environment

1. **Verify project exists** — Check that `$ARGUMENTS[0]` contains a valid HarmonyOS project (look for `build-profile.json5`, `entry/src` directory, `oh-package.json5`).

2. **Determine platform & verify DevEco installation** — Decide the platform branch ONCE here and reuse it everywhere below (Step 1.1 Plan A/B, safeguards):
   - **Windows** → check `$ARGUMENTS[1]` contains:
     - `tools/node/node.exe` → this is `<node-path>`
     - `tools/hvigor/bin/hvigorw.js`
     - `tools/ohpm/bin/ohpm.bat` → this is `<ohpm-path>`
     - `sdk/` directory
   - **macOS / Linux** → check `$ARGUMENTS[1]` (macOS DevEco root is typically `/Applications/DevEco-Studio.app/Contents`) contains:
     - `tools/node/bin/node` → this is `<node-path>`
     - `tools/hvigor/bin/hvigorw.js`
     - `tools/ohpm/bin/ohpm` → this is `<ohpm-path>`
     - `sdk/` directory
   - If a binary is not at the listed path, Glob for it under the DevEco root (e.g. `**/node`, `**/hvigorw.js`) before failing. Record the resolved `<node-path>` / `<ohpm-path>` for reuse.

3. **Set up `local.properties`** — Ensure the project root has `local.properties` with:
   ```properties
   hwsdk.dir=<deveco-path>/sdk
   ```
   Create it if missing. Use forward slashes in the path.

4. **Run `ohpm install`** — Install dependencies before first build. Use the platform branch decided in item 2:

   **Windows (PowerShell)**:
   ```powershell
   & "<deveco-path>\tools\ohpm\bin\ohpm.bat" install
   ```
   (run with the project dir as working directory; do NOT append `2>&1` — PowerShell 5.1 wraps native stderr into error records)

   **macOS / Linux (bash)**:
   ```bash
   cd "<project-dir>"
   export PATH="<deveco-path>/tools/ohpm/bin:$PATH"
   "<ohpm-path>" install
   ```

5. **Determine Build Mode**（**只读探测，绝不改 `build-profile.json5`**——2026-08-18 前的版本在这里"若有 signingConfigs 则删除"，实测会把用户 DevEco 配好的真实签名连同密码整段删掉并随 checkpoint 入库，下游装机全废；已废止）：
   1. **跑脚本**（别手工看，`.cer` 里通常是 3 张证书的链，`openssl x509 -enddate` 只显示第一张根证书 2049 会误判）：
      `python3 <本 skill 目录>/scripts/check_signing.py <project-dir>` → 一行 JSON：`configured` / `product_ref` / `files{}` / `cert_not_after`（链中最早到期=叶证书）/ `profile_not_after`（.p7b 载荷 validity）/ `expired` / `verdict` / `reason`。脚本只读，不改任何文件；Windows 下同一份（不依赖 openssl 命令）。**脚本跑不起来**（无 python / 报错）→ 不阻塞：按 Unsigned build mode 继续，报告 `unsigned(fallback: signing probe unavailable: <错误首行>)`——编译永远照跑，签名探测失败只影响出不出 signed 包。
   2. 按 `$ARGUMENTS[2]` 决定：
      - **omitted（auto）**：直接采用脚本 `verdict`：`signed` → **Signed build mode**（Step 0.5 只做校验，不会 STOP）；`unsigned` → **Unsigned build mode**，报告原样转录脚本 `reason`（`no signing configured` / `material missing: …` / `certificate expired NotAfter=…` / `no product references it`）。
      - **auto 命中 signed 但 SignHap 阶段仍失败**（hvigor 报 `Failed :entry:default@SignHap` / `11013xxx` 证书或 profile 错误，且 ArkTS 编译 0 error）：这不是源码错误，**不进 build-fix 循环**；改按下面 §5.3 的临时剥离流程用 unsigned 重跑一次，报告 `unsigned(fallback: SignHap failed: <hvigor 原话首行>)`，并在报告里提示用户到 DevEco 重新生成签名。
      - **`--signed`** → Signed build mode，进 Step 0.5，不齐则 STOP 报告。
      - **`--unsigned`** → Unsigned build mode。
   3. **Unsigned build mode 的实现约束**：若 `build-profile.json5` 里存在 `signingConfigs` / product `signingConfig` 引用（材料缺失或用户强制 unsigned），hvigor 会在签名步骤报错。此时**只允许临时剥离**：先 `cp build-profile.json5 build-profile.json5.a2h-signing-bak`（不入库，加进 `.gitignore`），在工作副本里去掉签名段，构建；**无论成败，构建结束后立即用备份原样还原并删除备份**，还原后核对与备份 md5 一致。绝不把剥离后的文件留在工作区、更不允许进入任何 commit。没有签名段的工程无需此步。
   4. 进入 Step 1。

---

## Step 0.5: Validate Signing Config (Signed build mode)

This step is executed whenever the build mode resolved to **signed**（`--signed` 显式指定，或 auto 探测命中）。auto 命中时 §5 已确认三项齐全，本步只是复核；`--signed` 时不齐则 STOP。

Signing information is read directly from the project's own `build-profile.json5`. The user must have already configured signing in DevEco Studio before running this skill.

### Steps:

1. **Read `build-profile.json5`** in the project root.

2. **Check for `signingConfigs`** — Look for `app.signingConfigs` array in the file.
   - If `signingConfigs` exists and has at least one entry with valid `material` fields (`certpath`, `storeFile`, `profile`), proceed to step 3.
   - If `signingConfigs` is missing or empty, **STOP and report to the user**:
     > Signing configuration not found in `build-profile.json5`.
     > Please open the project in DevEco Studio, go to **File → Project Structure → Signing Configs**, enable **Automatically generate signature**, then re-run this skill with `--signed`.

3. **Validate signing material files exist** — For the first entry in `signingConfigs`, check that the files referenced by `material.certpath`, `material.storeFile`, and `material.profile` actually exist on disk.
   - If any file is missing, **STOP and report** which files are missing. Suggest the user re-open DevEco Studio and re-generate the signing config.

4. **Ensure product references signing** — Check that the product entry in `products` array has `"signingConfig": "default"` (or matching the signing config name). **Missing → do NOT add it**（那是改用户工程配置）：`--signed` 时 STOP 并告诉用户去 DevEco Signing Configs 勾上；auto 时脚本已判 unsigned-fallback。

5. Proceed to Step 1.

---

## Step 1: Build-Fix Loop

Execute the following loop. **Maximum 20 iterations** to prevent infinite loops.

### 1.1 Run CLI Build

Use the platform branch decided in Step 0.2. **Both plans share two hard rules**:

- **The build's output MUST be redirected to `<project-dir>/build_out.log` from INSIDE the script/command itself**, ending with a `BUILD_EXIT_CODE=<n>` sentinel line. Never rely on capturing the build's stdout: a timeout loses all piped output, and large logs exceed tool output truncation limits. The log file survives timeouts and background runs, and is inspected with Grep.
- **Keep the hvigor daemon** — do NOT pass `--no-daemon`. The daemon holds incremental compile state; killing it every iteration turns each of up to 20 fix loops into a cold build. Only stop the daemon explicitly via the safeguards below when a build hangs or SDK-path errors appear.

**Housekeeping (once, before the first build)**: if the project is a git repo, ensure `.gitignore` contains `build_temp.bat` and `build_out.log` (append if missing) so aborted runs don't pollute git status.

#### Plan A — Windows (batch file + PowerShell `cmd /c`)

Env vars must be set inside a `.bat` so they reach the native `node.exe`/`java` child processes with correct Windows path format.

1. **Write `<project-dir>/build_temp.bat`** (backslashes in paths):

   **For unsigned builds** (no `--signed`):
   ```bat
   @echo off
   set "DEVECO_SDK_HOME=<deveco-path>\sdk"
   cd /d "<project-dir>"
   "<node-path>" "<deveco-path>\tools\hvigor\bin\hvigorw.js" assembleHap --mode module -p module=entry > "<project-dir>\build_out.log" 2>&1
   set "RC=%ERRORLEVEL%"
   echo BUILD_EXIT_CODE=%RC%>> "<project-dir>\build_out.log"
   exit /b %RC%
   ```

   **For signed builds** (`--signed`): same, but add these two lines before `set "DEVECO_SDK_HOME=..."`:
   ```bat
   set "PATH=<deveco-path>\jbr\bin;%PATH%"
   set "JAVA_HOME=<deveco-path>\jbr"
   ```
   (the `SignHap` step spawns `java` as a child process)

2. **Run the batch file via the PowerShell tool** (foreground or `run_in_background` per the timeout policy below):
   ```powershell
   cmd /c '"<project-dir>\build_temp.bat"'
   ```
   - The single-quote-wrapping-double-quote form keeps paths with spaces intact.
   - Do NOT append `2>&1` (PowerShell 5.1 wraps native stderr into error records); the bat already redirects everything to the log.
   - **NEVER use `cmd.exe //c`** — the `//c` form is Git-Bash-only path-mangling. From PowerShell/cmd it is not recognized as `/c`, so cmd opens an *interactive* shell that reads EOF and exits instantly, leaving a banner-only log and no build.

3. The bat file is reused across iterations; delete `build_temp.bat` and `build_out.log` only after the loop ends (Step 2).

#### Plan B — macOS / Linux (direct bash, no script file)

`export` propagates to child processes normally on POSIX — no wrapper script needed:

```bash
cd "<project-dir>"
export DEVECO_SDK_HOME="<deveco-path>/sdk"
"<node-path>" "<deveco-path>/tools/hvigor/bin/hvigorw.js" assembleHap --mode module -p module=entry > build_out.log 2>&1
echo "BUILD_EXIT_CODE=$?" >> build_out.log
```

**For signed builds** (`--signed`), additionally export before the build line:
```bash
export JAVA_HOME="<deveco-path>/jbr/Contents/Home"   # macOS; verify $JAVA_HOME/bin/java exists, Glob under <deveco-path>/jbr if not
export PATH="$JAVA_HOME/bin:$PATH"
```

#### Timeout policy

- **First build (cold)**: run in the background (`run_in_background`). Cold start (hvigor init, SDK component load, dependency scan, antivirus scanning on Windows) routinely exceeds 5 minutes. You are notified automatically on completion — do NOT poll in a sleep loop; you may Grep `build_out.log` occasionally for progress.
- **Subsequent builds (incremental, daemon warm)**: foreground with a 600000ms (10 min) timeout.

#### Recovery protocol on timeout / lost result

1. **Check whether the build process is still alive**:
   - Windows (PowerShell): `Get-CimInstance Win32_Process -Filter "Name='node.exe'" | Where-Object { $_.CommandLine -match 'hvigor' }`
   - macOS/Linux (bash): `pgrep -f hvigorw.js`
2. **If alive** → wait and watch `build_out.log` grow. **NEVER launch a second build concurrently** — two hvigor processes corrupt each other's build dir and clobber the shared log.
3. **If dead** and the log has no `BUILD_EXIT_CODE=` sentinel → the build crashed or was killed mid-run; inspect the log tail for the last activity, then rebuild (this counts as an iteration).

### 1.2 Check Build Result

Judge the result from `build_out.log` **using Grep** (never load the whole file into context):

- Log contains `BUILD SUCCESSFUL` AND `BUILD_EXIT_CODE=0` → verify the output HAP file exists (paths in Step 2). If it exists → **Build succeeded!** Exit the loop, go to Step 2.
- Log contains `ERROR` or `BUILD FAILED` → Parse errors (Grep with `-B/-A` context) and continue to 1.3.
- Log contains only a shell banner (a few lines of `Microsoft Windows [...]` + prompt, no hvigor output) → the invocation itself was broken (see Plan A step 2). Fix the invocation and re-run; do NOT count this as a build-fix iteration.

### 1.3 Parse Errors

Extract error information from `build_out.log` (Grep for `ERROR` with context lines). Errors typically appear in these formats:

```
ERROR: <file-path>:<line>:<col> - <error-code>: <message>
```

or

```
ArkTS:ERROR File: <file-path>:<line>:<col>
  <error message>
```

Group errors by file. Focus on **actual errors**, not warnings.

### 1.4 Fix Errors

Read each file that has errors and apply fixes. Use the error reference table below to identify and fix common issues:

| Error Code / Pattern | Message | Fix |
|---|---|---|
| `arkts-limited-throw` | "throw statements cannot accept values of arbitrary types" | Change `throw err` to `throw (err instanceof Error) ? err : new Error(String(err))` |
| `arkts-no-obj-literals-as-types` | "Object literals cannot be used as type declarations" | Define a named `interface` instead of inline `{ key: Type }` |
| `arkts-no-untyped-obj-literals` | "Object literal must correspond to some explicitly declared class or interface" | Assign to typed variable: `const r: MyInterface = {...}; return r;` |
| `arkts-no-any-type` / `any` type usage | "Use explicit types instead of any" | Replace `any` with the correct concrete type or `object` |
| `arkts-no-var` | "Use 'let' or 'const' instead of 'var'" | Replace `var` with `let` or `const` |
| `10903329` | "Unknown resource name 'xxx'" | Verify resource exists in `resources/base/media/` or `element/*.json`. Use `layered_image` as fallback for missing images. **Special case**: `$r('sys.media.ohos_ic_public_xxx')` references system icons by SDK-specific names that may not exist in the build SDK — replace with `$r('app.media.ic_public_xxx')` and add the icon file to `resources/base/media/` |
| `10505001` | "Resource[] is not assignable to ResourceColor" | Remove array brackets: `.fontColor($r('app.color.x'))` not `.fontColor([$r('app.color.x')])` |
| `00303221` | "permission must be a value that is predefined within the SDK" | Remove invalid permission from `module.json5`. See valid permissions list below |
| Missing import | "Cannot find name 'xxx'" | Add the correct import (see import reference below) |
| Missing `async` | "await expression requires async function" | Add `async` to the enclosing function |
| Missing `build()` | "@ComponentV2 / @Component must have build() method" | Add a `build() {}` method to the `@ComponentV2` (V2) or `@Component` (V1) struct |
| Type mismatch | Various type errors | Fix the type annotation or cast appropriately |
| Duplicate identifier | "Duplicate identifier 'xxx'" | Remove or rename the duplicate declaration |

**For errors NOT in the table above**: Read the error message carefully, read the relevant source file, understand the context, and apply an appropriate fix. Use your knowledge of ArkTS/HarmonyOS to determine the correct solution.

### 1.5 Log Progress

After each fix iteration, briefly report:
- Iteration number
- Number of errors found
- Summary of fixes applied
- Whether re-building

Then go back to **1.1** and rebuild.

---

## Step 2: Build Success Report

When the build succeeds, present a summary:

1. **Build Status**: SUCCESS
2. **Build Type + reason**: `signed(--signed)` / `signed(auto: signing material present)` / `unsigned(--unsigned)` / `unsigned(no signing configured)` / `unsigned(fallback: material missing: <paths>)`
3. **Signing**: signed 时确认用了 `build-profile.json5` 的签名配置；unsigned-fallback 时确认 `build-profile.json5` 已原样还原（md5 与备份一致）——**任何情况下 `signingConfigs` 都不应出现在本次 diff 里**
4. **Iterations**: How many build-fix cycles were needed
5. **Total Errors Fixed**: Count of errors fixed across all iterations
6. **Summary of Changes**: List of files modified and what was fixed in each
7. **Output HAP Path**:
   - Signed: `<project>/entry/build/default/outputs/default/entry-default-signed.hap`
   - Unsigned: `<project>/entry/build/default/outputs/default/entry-default-unsigned.hap`

8. **Cleanup**: Delete `<project-dir>/build_temp.bat` (Windows) and `<project-dir>/build_out.log` now that the loop is over. (Also perform this cleanup when giving up after max iterations.)

---

## Reference: Common HarmonyOS Imports

```typescript
// Network
import { http } from '@kit.NetworkKit';

// Data persistence
import { preferences } from '@kit.ArkData';
import { relationalStore } from '@kit.ArkData';

// UI utilities
import { router } from '@kit.ArkUI';
import { promptAction } from '@kit.ArkUI';

// Ability & Context
import { UIAbility, AbilityConstant, Want } from '@kit.AbilityKit';
import { common } from '@kit.AbilityKit';

// File I/O
import { fileIo } from '@kit.CoreFileKit';

// Logging
import { hilog } from '@kit.PerformanceAnalysisKit';

// JSON parsing — built-in, no import needed
// ArkUI built-in components (Text, Column, Row, List, Button, Image, etc.) — NO import needed
```

## Reference: Valid Permission Names

Commonly used SDK-validated permissions for `module.json5`:

- `ohos.permission.INTERNET`
- `ohos.permission.GET_NETWORK_INFO`
- `ohos.permission.GET_WIFI_INFO`
- `ohos.permission.KEEP_BACKGROUND_RUNNING`
- `ohos.permission.PUBLISH_AGENT_REMINDER`
- `ohos.permission.CAMERA`
- `ohos.permission.MICROPHONE`
- `ohos.permission.APPROXIMATELY_LOCATION`
- `ohos.permission.LOCATION`
- `ohos.permission.READ_MEDIA`
- `ohos.permission.WRITE_MEDIA`
- `ohos.permission.USE_BLUETOOTH`
- `ohos.permission.VIBRATE`

**Note**: `ohos.permission.NOTIFICATION` does NOT exist. When in doubt, omit the permission.

---

## Build-Fix Loop: Environmental Safeguards

### Cache Cleanliness

- **Single `ohpm install`**: Run `ohpm install` exactly once at the start of the build-fix loop. Do NOT re-run it inside the loop unless a new dependency was explicitly added.
- **Cache cleanup limit**: `clean` may be run at most **1 time** per entire build-fix session. Invoke it through the same platform wrapper as Step 1.1 (replace `assembleHap --mode module -p module=entry` with `clean`) — there is no `hvigorw` executable on PATH, especially on Windows. If errors increase after a clean, stop CLI build immediately and escalate to IDE-based verification.
- **Never `rm -rf entry/build`**: This destroys the hvigor daemon's incremental state and can cause unrecoverable cache corruption. The only safe cache reset is the `clean` task run through the Step 1.1 wrapper.

### SDK Path Poisoning

- **Environment variable pinning**: `DEVECO_SDK_HOME` is set explicitly *inside the Step 1.1 build script/command* to `<deveco-path>/sdk` — that value is authoritative and must match `hwsdk.dir` in `local.properties`. Never rely on a value inherited from the outer shell. If the *outer* shell carries a different stale `DEVECO_SDK_HOME`, clear it there so tools launched outside the wrapper don't pick it up:
  - Windows (PowerShell): `Remove-Item Env:DEVECO_SDK_HOME -ErrorAction SilentlyContinue`
  - macOS/Linux (bash): `unset DEVECO_SDK_HOME`
- **If `00303208` or `00303217` appears**: First verify the value set in the build script matches `hwsdk.dir` in `local.properties`. If it matches but the error persists, the hvigor daemon has cached a bad value — stop the daemon via the Step 1.1 wrapper with `--stop-daemon` as the sole argument (i.e. `"<node-path>" ".../hvigorw.js" --stop-daemon`), wait 2 seconds, then retry. After 2 consecutive SDK-path failures, **escalate to IDE build**.

### Hanged Daemon

- **If build exits <1s with no compile errors**: The hvigor daemon is likely dead or unresponsive. Stop it via the Step 1.1 wrapper: `"<node-path>" "<deveco-path>/tools/hvigor/bin/hvigorw.js" --stop-daemon` (Windows: run inside the bat / a `cmd /c` one-liner with the same env; macOS: plain bash). Wait 2 seconds, retry once. If still failing after 2 attempts, escalate to IDE build.

### Checkpoint Commit

- **After every `BUILD SUCCESSFUL`**: Immediately `git commit` all changed files with a checkpoint message: `checkpoint(base-N): build pass after K fixes`.
- **签名段守卫**：commit 前 `git diff -- build-profile.json5`，若含 `signingConfigs` / `signingConfig` 行的删除或改动 → 先按 Step 0 §5.3 还原再 commit。本 skill 的 checkpoint **永远不得包含签名配置变更**（2026-08-18 实测：删除曾随 checkpoint 静默入库，`git status` 干净、只有翻历史才看得见）。
- **On linter revert**: If a file is reverted after the checkpoint, use `git checkout -- <file>` to restore the build-pass state rather than re-editing.

---

## Reference: ArkTS Strict Mode Rules

All code must comply with ArkTS strict mode:

1. **No `any` type** — Use explicit types or `object`
2. **No `var`** — Only `let` and `const`
3. **No dynamic property access** — Use typed interfaces instead of `obj['key']` on typed objects
4. **`throw` must throw Error instances** — Never `throw 'string'` or `throw unknownVar`
5. **All object literals must match declared interfaces** — No anonymous `{ key: val }` returns without a matching interface
6. **No inline object literal types** — `function(): { a: string }` is forbidden; define a named `interface`
7. **All `@ComponentV2` (V2) / `@Component` (V1) structs must have `build()`** — Missing build method is a compile error
8. **`$r()` resource references validated at compile time** — All referenced resources must exist
9. **`fontColor()` expects `ResourceColor`**, not `Resource[]` — Don't wrap in array brackets (exception: `SymbolGlyph`)
10. **Permission names in `module.json5`** — Must be SDK-predefined values

## Important Notes

- **Timeout**: First (cold) build → run in background, no foreground timeout applies. Incremental builds → 600000ms (10 min) foreground timeout. On timeout, follow the recovery protocol in 1.1 — never start a second concurrent build.
- **Max iterations**: Stop after 20 iterations to prevent infinite loops. If build still fails after 20 attempts, report the remaining errors to the user.
- **Don't over-fix**: Only fix errors reported by the compiler. Don't proactively refactor unrelated code.
- **Read before edit**: Always read a file before modifying it. Understand the surrounding context.
- **One error can cause many**: A single root-cause fix (like adding a missing interface) may resolve multiple reported errors. After fixing root causes, rebuild to see remaining issues.
- **ohpm errors**: If the build fails because of missing packages, run `ohpm install` again.

---

## References

- `references/arkts-strict-patterns.md` — ArkTS 严格模式编译错误的确定性修复 Pattern（throw/any/var/interface 等）
- `references/known-patterns.md` — 已知常见编译错误 Pattern 及修复方案
- `references/rdb-entity-pattern.md` — RDB 实体类编译错误 Pattern（数据库实体相关）
