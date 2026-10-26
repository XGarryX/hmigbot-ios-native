---
name: a2h-init
description: Trigger: `$a2h-init` or natural language. Confirm auto-detected android / harmonyos / hvigorw / deveco / adb / hdc paths in plain language. Run on first install or whenever the paths change.
---

> Codex skill (converted from the `a2h-init` slash command). Invoke with `$a2h-init`, or pick it in `/skills` (the default_prompt below auto-runs). Codex has no custom slash commands, so the `$` prefix replaces `/`.


the user's input (the command argument) is ignored.

## Goal

Walk the user through confirming the paths in `.migbot/config.json` (`android`, `harmonyos`, `deveco`, `hvigorw`, `adb`, `hdc`) using plain conversational prompts. On success, set `confirmed: true` so `$a2h-run` stops redirecting here.

**Order matters: the User Experience Improvement Plan consent (§2) runs FIRST**, right after the silent runtime provisioning, before any path questions. The agreement is shown to the user *out of band* (a popup window, or a file path) — never pasted into this conversation — so it does not consume the agent's context window.

## 0. Pick the shell for this host (read before running anything)

Every command below is written in its **macOS / Linux (bash)** form. On **Windows**, do **not** run `bash` at all — `bash` may resolve to WSL (`C:\Windows\system32\bash.exe`), which cannot see `C:\` paths and looks for an extension-less `a2h`, so every path check and the "a2h not staged" check misreport (issue #41). Git Bash and WSL are indistinguishable by name, so the rule is unconditional. Detect the host first: the working directory looks like `C:\…` / `D:\…`, or `$env:OS` is `Windows_NT`, or the project's `AGENTS.md` carries a `migbot-platform: windows` block. Then translate with this table (`PS` = `powershell -NoProfile -ExecutionPolicy Bypass`):

| bash form (macOS / Linux)                          | Windows form                                                                 |
|----------------------------------------------------|------------------------------------------------------------------------------|
| `bash .migbot/bin/a2h-bootstrap --lang X`          | `PS -File .migbot\bin\a2h-bootstrap.ps1 -Lang X`                            |
| `bash .migbot/bin/a2h-agreement --lang X [--check]`| `PS -File .migbot\bin\a2h-agreement.ps1 -Lang X [-Check]`                   |
| `.migbot/bin/a2h <subcommand> …`                   | `.migbot\bin\a2h.exe <subcommand> …`                                        |
| `.migbot/bin/a2h-tool validate`                    | `PS -File .migbot\bin\a2h-tool.ps1 validate`                                |
| `test -d "<p>"`                                    | `PS -Command "Test-Path -LiteralPath '<p>' -PathType Container"`            |
| `test -f "<p>"` / `test -x "<p>"`                  | `PS -Command "Test-Path -LiteralPath '<p>' -PathType Leaf"`                 |
| `command -v adb` / `command -v hdc`                | `PS -Command "(Get-Command adb -ErrorAction SilentlyContinue).Source"`      |
| `uuidgen \| tr 'A-Z' 'a-z'`                        | `PS -Command "[guid]::NewGuid().ToString()"`                                 |

Relative paths in `config.json` (`../android-app`, `.`) are resolved against the install dir on both platforms. The JSON contracts (`{"ok":..}`, `{"shown":..}`, `{"status":..}`) are identical between the bash and `.ps1` twins, so the rest of this skill needs no other change.

## 1. Provision runtime and read current config

First run `Bash: bash .migbot/bin/a2h-bootstrap --lang <zh|en>` — on Windows `powershell -NoProfile -ExecutionPolicy Bypass -File .migbot\bin\a2h-bootstrap.ps1 -Lang <zh|en>` (§0) — (`.migbot/bin` is staged by `install.sh`/`install.ps1`). This is **idempotent** and plays the role install.sh does: it stages the runtime into `.migbot/bin` (a2h-tool plus the `a2h` telemetry binary, invoked as `a2h <subcommand>`) and the policy docs into `.migbot/policies`, and creates a `.migbot/config.json` skeleton (with `telemetry_consent: "unset"`) if one does not exist yet. It never overwrites an existing config.

Then read `.migbot/config.json` from the current working directory.

- If `a2h-bootstrap` is unavailable (install was not run) **and** the file does not exist, stop and tell the user: `"migbot runtime not found. Run migbot's install.sh / install.ps1 against this project, then re-run $a2h-init."`
- Parse these fields: `language`, `android`, `harmonyos`, `deveco`, `hvigorw`, `adb`, `hdc`, `confirmed`.

**Hook trust self-check (Codex-only, never blocks).** Run `Bash: .migbot/bin/a2h hook-trust` (Windows: `.migbot\bin\a2h.exe hook-trust`). Codex ≥ 0.129 silently skips any lifecycle hook the user has not trusted in `/hooks` (and does not load the project `.codex` layer at all until the project is trusted), so a migration can run end-to-end with **zero telemetry and no error**. If the command exits non-zero, relay its `RESULT:` line to the user verbatim and add: *"Until you run `/hooks` in Codex and trust the migbot hooks, nothing from this migration is uploaded. You can re-check with `.migbot/bin/a2h hook-trust`."* Then continue — do not wait for them to fix it.

Do **not** ask about the paths yet — go straight to §2.

## 2. User Experience Improvement Plan — consent (runs first, unconditionally)

MigBot (迁移精灵) has an **optional** User Experience Improvement Plan (full agreement: `.migbot/policies/user-experience-improvement-plan.<lang>.md`). Upon participation, the tool uploads work-process artifacts (no personal data involved) at the end of the `$a2h-run` pipeline. Until the user **explicitly consents**, nothing is ever uploaded.

> **There is one consent flow, defined by `$a2h-privacy accept`.** `install.sh` / `install.ps1` try to collect the decision **at install time** — that runs in the user's real terminal, where the agreement popup CAN be raised. If they did, `.migbot/config.json` already shows `granted`/`denied` and §2.1 just notes it. Otherwise (unattended install, `--no-consent`, or a decision not yet made) a2h-init runs that exact flow inline (§2.2) on a **first run** — it shows the full agreement and asks for the decision before anything else. ⚠ Inside Codex's sandbox `a2h-agreement` **cannot pop a window** (LaunchServices/Explorer mach-lookups are denied), so the inline flow degrades to `shown:"path"` and the user must open the file manually — which is why install-time collection is preferred. For an already-decided state it just notes the state and moves on. The steps in §2.2 **MUST stay identical to `$a2h-privacy` §B** — keep them in sync.

This section runs on **every** invocation (so users upgrading from an older client that had no consent field still get prompted). It is unconditional and comes before the path steps.

### 2.1 Branch on the current participation state

> **Install-level consent (agree once per machine).** Before reading the state below, run `Bash: .migbot/bin/a2h init-run` (no flags). It mints or reuses this machine's `install_id` (`~/.migbot/install.json`), copies it into `.migbot/config.json`, and — if the user already accepted or declined on this machine — copies that decision (`telemetry_consent`, `telemetry_consent_at`, `agreement_version`) into this project (stderr shows `inherited from install`). A project that inherits `granted` is enrolled without seeing the agreement again; the `migbot_session_id` is still minted per project.

First, **silently** probe the current policy version: run `Bash: bash .migbot/bin/a2h-agreement --lang <language> --check` and read `version` from its single-line JSON (this raises **no** window and shows **no** text). Call it `<current_version>`.

Read the `telemetry_consent` and `agreement_version` fields from `.migbot/config.json`:

| Current value | Action |
|---|---|
| `"granted"` and stored `agreement_version` == `<current_version>` (or `<current_version>` is empty) | Note `"You are enrolled in the User Experience Improvement Plan (consented at <telemetry_consent_at>). Run $a2h-privacy deny to withdraw, or $a2h-privacy status to see your migbot_session_id."`, then continue to §3. |
| `"denied"` and stored `agreement_version` == `<current_version>` (or empty) | Note `"⚠ You have declined the User Experience Improvement Plan, so the migration pipeline is DISABLED. Agreeing to the Plan is required to use migbot — declining means the tool cannot be used. Run $a2h-privacy accept to enable it."`, then **terminate the current initialization flow immediately — do not execute any subsequent steps (§3–§10)**. |
| `"granted"` or `"denied"` **but** stored `agreement_version` != `<current_version>` | The plan **materially changed** — your prior choice no longer applies (per the agreement's "material change ⇒ re-consent" clause). Tell the user `"The User Experience Improvement Plan was updated (<stored> → <current_version>); please review and choose again."` and **run the consent flow in §2.2 now**, then continue to §3. |
| `"unset"` / missing / any other value | **First run — run the consent flow in §2.2 now**, then continue to §3. |

> Operators: bump the policy `Version:` line **only** for material changes (new data category, changed purpose/storage/operator). Typo/wording fixes must keep the version so they don't needlessly re-prompt every user (agreement §7.4).

### 2.2 First-run consent flow — run the `$a2h-privacy accept` flow inline

This is the **same** flow as `$a2h-privacy accept` (§B of that command). **Perform it now** — do not merely tell the user to run it. These steps must stay in sync with `$a2h-privacy` §B.

1. **Display the agreement out of band (do NOT paste it into the conversation).** Run `Bash: bash .migbot/bin/a2h-agreement --lang <language>` and parse its single-line JSON verdict — `{"shown":..,"method":..,"path":..,"version":..,"reason":..}`. **Never** read or echo the policy body into this chat; the user reads it in the popup / file. Branch on `shown`:
   - `"popup"` → tell the user: `"The User Experience Improvement Plan has opened in a separate window. If no window appeared, open it yourself: <path>. Read it, then answer below."`
   - `"path"` → tell the user: `"Please open and read the User Experience Improvement Plan before deciding: <path>. (Your environment can't pop a window — open the file manually.)"`
   - `"error"`, or `a2h-agreement` is unavailable / not on PATH → the policy could not be located. Tell the user `"Policy file is missing. Re-run migbot's install.sh / install.ps1, or contact the operator. Consent state was NOT modified."`, do **not** edit config, and continue to §3. (If you have the path `.migbot/policies/user-experience-improvement-plan.<language>.md` and it exists, you may instead give the user that path and proceed — but still never paste its contents.)
   - Keep the `version` value from the JSON as `agreement_version` for step 4 below.
2. After pointing the user at the agreement, on a separate block output exactly:

   > ```
   > Do you agree to the policy above? Please choose:
   >   1) I accept
   >   2) I refuse
   > Enter 1 or 2:
   > ```

3. **[HARD CONSTRAINT] Parse the user's next input** — treat it as **consent** if and only if it matches (case-insensitive, trimmed): `1`, `accept`, `agree`, `yes`, `y`, or `i accept`. **Any** other input (`2`, `refuse`, `deny`, `no`, empty, `cancel`, or changing the subject) is a **refusal**. Never infer consent from context.
4. **Refuse** → Edit `.migbot/config.json`: `"telemetry_consent": "denied"`, `"telemetry_consent_at": "null"`, `"agreement_version": "null"`; leave everything else untouched (**do not** mint the install handle, **do not** write `migbot_session_id`). Then **explicitly warn the user**: `"⚠ You have declined the User Experience Improvement Plan. Participation in the Plan is required to use migbot — declining means the tool cannot be used. The migration pipeline (from $a2h-spec onward) is DISABLED, and nothing is uploaded while declined. You can enable it any time with $a2h-privacy accept."`. **Terminate the current initialization flow immediately — do not execute any subsequent steps (§3–§10).**

   > **Refusing disables migbot AND blocks the flow.** Participation in the Plan is required to use migbot: the migration pipeline will refuse to run, and nothing is uploaded while declined. On refusal, no scripts are executed (no install handle is minted, no `migbot_session_id` is written) — the flow terminates immediately, strictly blocking all subsequent skill execution.
5. **Accept** → write config:
   - First, resolve the install handle: if `.migbot/config.json` already holds a non-empty `migbot_session_id`, **reuse it verbatim** (never rotate an existing handle — prior uploads are keyed to it). Only if it is missing/empty, mint one: run `Bash: uuidgen | tr 'A-Z' 'a-z'` and take its stdout (an opaque token — record it verbatim). It identifies this install for the deletion handle and for active-user counting; it is **not** a consent grant by itself.
   - Use the `agreement_version` returned by `a2h-agreement` in step 1 (the policy's bottom `Version: vX.Y`). If it was empty, leave the field out.
   - Edit `.migbot/config.json`, writing/updating: `"telemetry_consent_at": "<current ISO-8601 UTC>"` and `"agreement_version": "<version>"`; leave everything else untouched.
   - Run `Bash: .migbot/bin/a2h init-run --consent granted --migbot-session-id <handle>`. This writes `telemetry_consent: "granted"` and `migbot_session_id` into `.migbot/config.json` and pins the run identity. (`--migbot-session-id` only backfills an empty field, so a re-run never rewrites an existing handle.) Server-side registration of the consent happens automatically on the first upload.
   - Continue to §3.

## 3. Path confirmation gate + confirm `android`

**Gate:** If `confirmed == true` already, ask the user: `"Config already confirmed. Re-confirm paths? (yes / no)"`.

- `no` → skip §3-§9 path confirmation and **jump straight to §10** (the final report). Consent (§2) has already run, so upgraders are still covered. Exit after §10.
- `yes` (or `confirmed` was not already true) → run the full §3-§9 flow below.

Now confirm `android`. Show the current value to the user:

> `Detected Android source: <android>` (or `Android source not detected.` if value is the placeholder `../android-app` or the path doesn't exist)

Run `Bash: test -d "<android>"` (resolved relative to the install dir) to check whether the path exists. Report the result inline:

- exists → `✔ path exists`
- missing → `✘ path missing`

Then ask: `"Use this path, or enter a different one? (keep / <new path>)"`.

- `keep` → retain current value.
- Any other input → treat as the new path. Re-run `test -d` on the new value; if missing, warn `"That path doesn't exist. Use it anyway? (yes / no)"`. On `no`, ask again. On `yes`, accept.

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

## 7. Confirm `adb` and `hdc` paths

These two fields let `a2h-tool validate` locate adb / hdc when they are not on `$PATH`.

### 7.1 `adb`

Try to auto-detect — **stop at the first hit**:

| # | Candidate | Notes |
|---|-----------|-------|
| 1 | `adb` field value (if non-empty and executable) | Explicit user override in config.json |
| 2 | `command -v adb` | Already on PATH |
| 3 | `$HOME/Library/Android/sdk/platform-tools/adb` | macOS default Android SDK location |
| 4 | `/usr/local/bin/adb` | Common symlink location |

If a candidate hits, report: `✔ adb resolved: <path> (candidate #N)`.

Ask: `"Use this adb, or override? (keep / <new path> / skip)"`.
- `keep` → write resolved path into `adb` field (leave empty for candidate 2 — it's already on PATH, no need to hardcode).
- `<new path>` → validate with `test -x`; if missing, warn and re-ask.
- `skip` → leave `adb` empty. validate will still pass if adb is on PATH at runtime.

If no candidate hits, tell the user:

> `adb not found. Android emulator checks will fail. Please provide the full path to adb, or type "skip" to leave it empty.`

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

Use the Edit tool to update `.migbot/config.json`. The final shape:

```json
{
  "android": "<confirmed>",
  "harmonyos": "<confirmed>",
  "hvigorw": "<resolved-or-empty>",
  "deveco": "<confirmed-or-empty>",
  "adb": "<resolved-or-empty>",
  "hdc": "<resolved-or-empty>",
  "language": "<preserved>",
  "confirmed": true
}
```

Preserve `language` and any extra keys the user may have added; only overwrite `android`, `harmonyos`, `hvigorw`, `deveco`, `adb`, `hdc`, and `confirmed`. **Preserve** `telemetry_consent`, `telemetry_consent_at`, `migbot_session_id`, `agreement_version` — those are managed by §2 above; do not touch them here.

## 9. Final validation

After the path work is done, capture and report the init-stage signals (both best-effort and tier-gated — ignore their exit status; neither blocks init):

1. **Pin the run identity.** Run `Bash: .migbot/bin/a2h init-run` (Windows: `.migbot\bin\a2h.exe init-run`, likewise for the two calls below). This pins `run_id` / `project` / `app_version` into `.migbot/config.json` — the identity every telemetry upload of this migration hangs off. It is **idempotent**: an existing run_id is reused as-is (re-running init is harmless), and if the config was lost but `.migbot/metrics/` still holds a run directory the original run_id is recovered. A deliberate restart requires the explicit `--fresh` flag (never pass it unless the user asked to start the migration over).
2. **Android baseline.** Run `Bash: .migbot/bin/a2h count-lines`. This counts the Android-side code lines and reads the Android app name, recording them as a fact (HarmonyOS doesn't exist yet at init). It is the top-of-funnel signal the dashboard uses for active-user / active-project stats.
3. **Init-stage boundary.** Run `Bash: .migbot/bin/a2h mark-stage a2h-init`. This marks the `a2h-init` stage boundary; the session transcript that the lifecycle hooks upload is attributed to it server-side.

Run `.migbot/bin/a2h-tool validate` (Windows: `powershell -NoProfile -ExecutionPolicy Bypass -File .migbot\bin\a2h-tool.ps1 validate`). If it returns `{"ok":true}`, tell the user:

> `Config confirmed. You can now run $a2h-build to verify HarmonyOS compiles, or $a2h-run to start the migration pipeline.`

**If `telemetry_consent` is `granted`**, append on its own line (substituting the actual value from `.migbot/config.json`): `Please keep a record of your migbot_session_id: <migbot_session_id> — it is the credential you'll need to request deletion of your uploaded data later.` (Echo only the stored value; never explain how it is generated.)

If it returns failures, list them and tell the user:

> `Config saved with confirmed: true, but a2h-tool reports: <failures>. Re-run $a2h-init or fix the paths manually.`

## 10. Final report

After the §9 validation result (or directly here if the §3 gate chose `no`), **append** this block — it is **mandatory**, so the user always knows how to join/withdraw:

> ```
> ── User Experience Improvement Plan ──
> Current state: <granted (enrolled — migbot enabled) / denied (declined — migbot DISABLED)> (last changed: <telemetry_consent_at>)
> Participation in the Plan is REQUIRED to use migbot; declining disables the migration pipeline.
> Full agreement: .migbot/policies/user-experience-improvement-plan.<language>.md
> Change participation:
>   $a2h-privacy accept   enrol in the Plan and enable migbot (the Plan is shown in full first)
>   $a2h-privacy deny     decline — disables migbot
>   $a2h-privacy status   show the current state
> You may also manually edit .migbot/config.json's telemetry_consent field.
> ```

---

## Notes

- Path inputs are taken verbatim — do not auto-resolve relative paths to absolute. The user may prefer relative paths (e.g. `../android-app`) for portability. **Exception**: candidates 4-5 of the hvigorw chain ARE stored as absolute paths because they live outside `<harmonyos>`.
- Never edit `.agents/skills/` or `.claude/agents/` from this command. Only `.migbot/config.json` is in scope.
- §2 captures consent **only on a first run** (`telemetry_consent` unset), by running the exact `$a2h-privacy accept` flow inline (§2.2). For `granted`/`denied` states it is read-only. There is still a single consent flow — §2.2 mirrors `$a2h-privacy` §B and must not diverge; never invent a different consent path here.
- The agreement is **never** pasted into this conversation. `a2h-agreement` shows it out of band (popup window, else a file path) to keep it out of the agent's context window. If the popup cannot be raised (WSL / Git Bash / headless / macOS sandbox), the script degrades to printing the path — it does **not** fall back to dumping the text, and neither should you.
