---
name: a2h-privacy
description: Trigger: `$a2h-privacy` or natural language. "Query or change the migbot data tier. Subcommands: status / accept / deny / off."
---

> Codex skill (converted from the `a2h-privacy` slash command). Invoke with `$a2h-privacy`, or pick it in `/skills` (the default_prompt below auto-runs). Codex has no custom slash commands, so the `$` prefix replaces `/`.

> **Windows:** every `.migbot/bin/a2h …` / `bash .migbot/bin/a2h-agreement …` call below is `.migbot\bin\a2h.exe …` / `powershell -NoProfile -ExecutionPolicy Bypass -File .migbot\bin\a2h-agreement.ps1 …` — never through `bash` (see `$a2h-init` §0).


Dispatch on the user's input (the command argument):

| the user's input (the command argument) | Action |
|---|---|
| empty / `status` | §A — show current state |
| `accept` / `agree` / `yes` (any case) | §B — display policy and enrol (full tier) |
| `deny` / `disagree` / `no` (any case) | §C — decline (disables migbot) |
| `off` / `stop` / `disable` (any case) | §D — turn off ALL uploads |
| anything else | print the usage block below and exit without modifying anything |

Usage:

```
$a2h-privacy            # show current data tier
$a2h-privacy status     # same as above
$a2h-privacy accept     # show the policy, then enrol in the FULL tier
$a2h-privacy deny       # decline the Plan — DISABLES migbot (nothing uploaded)
$a2h-privacy off        # turn OFF all uploads (nothing leaves the machine)
```

> **Participation is binary** (full agreement: `.migbot/policies/user-experience-improvement-plan.<language>.md`). Joining the Plan is a precondition for using migbot:
> - **enrolled** (`telemetry_consent: "granted"`) — migbot is **enabled**; every work-process category is shared.
> - **declined** (anything else: `"denied"` / `"off"` / unset, or the one-shot env `A2H_TELEMETRY_OFF=1`) — migbot is **disabled** (the migration pipeline from `$a2h-spec` refuses to run) and **nothing** is uploaded.

---

## §A. status

1. Read `.migbot/config.json`.
   - File missing → tell the user `"migbot is not installed in this project. Run install.sh first."`, then stop.
2. Parse `telemetry_consent`, `telemetry_consent_at`, `migbot_session_id`, `language` (fallback to `en` if `language` is absent).
3. Map `telemetry_consent` to a state: `granted` → **enrolled (migbot enabled)**; anything else → **declined (migbot disabled)**.
   - Optionally run `Bash: .migbot/bin/a2h status --json` (ignore a non-zero exit) to surface local outbox state; if it reports queued uploads, mention the count.
4. Print (echo `migbot_session_id` whenever it is present — it is the credential for requesting data deletion later, so remind the user to keep it):

   > ```
   > ── migbot Participation ──
   > Status: <enrolled — migbot enabled / declined — migbot DISABLED>
   >   enrolled → migbot runs; code-lines + app names + token usage + build logs + retrospect report are shared
   >   declined → migbot is disabled (the migration pipeline won't run) and nothing is uploaded
   > Last changed:  <telemetry_consent_at, or "(never set)">
   > Deletion credential (keep this):
   >   migbot_session_id: <migbot_session_id, or "(none yet — set at $a2h-init)">
   >   install_id:        <install_id from `a2h status --json`, or "(none)">   ← consent is per machine; one install covers all its projects
   >   (To delete your data, email your install_id (or migbot_session_id) to the privacy mailbox in the policy's §8.)
   > Full policy:   .migbot/policies/user-experience-improvement-plan.<language>.md
   >
   > Management commands:
   >   $a2h-privacy accept   enrol and enable migbot (the policy is shown in full first)
   >   $a2h-privacy deny     decline — disables migbot
   >   $a2h-privacy status   show the current status
   > You may also manually edit .migbot/config.json's telemetry_consent field.
   > ```

---

## §B. accept

1. Read `.migbot/config.json`:
   - File missing → tell the user `"migbot is not installed in this project. Run install.sh first."`, stop.
   - Parse `language` (fallback `en` if absent), `telemetry_consent`, `agreement_version`, `migbot_session_id`.
   - **Install-level gate — agree once per machine.** Run `Bash: .migbot/bin/a2h init-run` (no flags) first: it copies this machine's `install_id` into config and, when the user already decided on this machine (`~/.migbot/install.json`), copies that decision into this project (stderr shows `inherited from install`). Re-read `telemetry_consent` / `agreement_version` afterwards so the idempotency gate below sees the inherited state; when it stops there, say `"already accepted on this machine — inherited by this project"` instead of re-showing the agreement.
   - **Idempotency gate — already enrolled means no-op.** Silently probe the current policy version: run `Bash: bash .migbot/bin/a2h-agreement --lang <language> --check` and read `version` from its JSON (raises no window). If `telemetry_consent == "granted"` **and** the stored `agreement_version` equals that version (or the probed version is empty), the user is already enrolled under the current plan: print the §A status block (echoing the **existing** `migbot_session_id`) plus the line `"You are already enrolled — nothing changed. Run $a2h-privacy deny to withdraw."`, and **stop here**. Do **not** re-show the agreement, do **not** mint a new handle, do **not** touch config. Only `unset` / `denied` / a changed policy version proceeds to step 2.
2. **Display the agreement out of band (do NOT paste it into the conversation).** Run `Bash: bash .migbot/bin/a2h-agreement --lang <language>` and parse its single-line JSON verdict — `{"shown":..,"method":..,"path":..,"version":..,"reason":..}`. **Never** read or echo the policy body into this chat; the user reads it in the popup / file. Branch on `shown`:
   - `"popup"` → tell the user: `"The User Experience Improvement Plan has opened in a separate window. If no window appeared, open it yourself: <path>. Read it, then answer below."`
   - `"path"` → tell the user: `"Please open and read the User Experience Improvement Plan before deciding: <path>. (Your environment can't pop a window — open the file manually.)"`
   - `"error"`, or `a2h-agreement` is unavailable / not on PATH → the policy could not be located. Tell the user `"Policy file is missing. Reinstall migbot or contact the operator. Consent state was NOT modified."`, then stop — **do not** edit config.
   - Keep the `version` value from the JSON as `agreement_version` for step 6 below.
3. After pointing the user at the agreement, on a separate block, output a multiple-choice prompt so the user picks from two unambiguous options:

   > ```
   > Do you agree to the policy above? Please choose:
   >   1) I accept
   >   2) I refuse
   > Enter 1 or 2:
   > ```

4. **[HARD CONSTRAINT] Parse the user's next input** — treat the input as **consent** if and only if it matches one of the following (case-insensitive, leading/trailing whitespace stripped):
   - `1`
   - `accept` / `agree` / `yes` / `y`
   - `i accept`

   **Any** other input (including `2`, `i refuse`, `deny` / `no` / `n` / `refuse`, empty reply, `cancel`, or the user changing the subject) **must** be treated as refusal. **Never** infer consent from context — only the exact strings above qualify.

   > **Resolve the install handle — never rotate an existing one.** If `.migbot/config.json` already holds a non-empty `migbot_session_id`, **reuse it verbatim** as `<handle>` (it is the credential for deleting data already uploaded under it, and every prior upload is keyed to it). Only if the field is missing or empty, mint one: run `Bash: uuidgen | tr 'A-Z' 'a-z'` and take its stdout (an opaque token — record verbatim, do not parse or describe). The handle identifies this install for the deletion handle and active-user counting, and is **not** itself a consent grant.

5. **Refuse** → decline (this disables migbot): Edit `.migbot/config.json`: `"telemetry_consent": "denied"`, `"telemetry_consent_at": "<current ISO-8601 UTC>"`, `"migbot_session_id": "<handle>"`, `"agreement_version": "<version from step 2>"`; leave everything else untouched. Skip to step 8.

6. **Accept** → write config:
   - Use the `agreement_version` returned by `a2h-agreement` in step 2 (the policy's bottom `Version: vX.Y`). If it was empty, leave the field out.
   - Edit `.migbot/config.json`, writing/updating: `"telemetry_consent": "granted"`, `"telemetry_consent_at": "<current ISO-8601 UTC>"`, `"migbot_session_id": "<handle>"` (unchanged if it already existed), `"agreement_version": "<version>"`; leave everything else untouched.

7. **On accept**, run `Bash: .migbot/bin/a2h init-run --consent granted --migbot-session-id <handle>` to record the consent in `.migbot/config.json` (failure is only a warning — the first `$a2h-run` upload registers it server-side anyway).

8. Show the final state by reusing the §A output format (echo `migbot_session_id` and remind the user to keep it).

---

## §C. deny  (decline — disables migbot)

1. Read `.migbot/config.json`:
   - File missing → tell the user `"migbot is not installed in this project. Run install.sh first."`, stop.
2. Edit `.migbot/config.json`:
   - Set `telemetry_consent` to `"denied"`;
   - Set `telemetry_consent_at` to the current ISO-8601 UTC time;
   - Leave all other fields untouched (keep any `migbot_session_id` so a later deletion request still has the handle).
3. Print:

   > ```
   > ✔ Declined the User Experience Improvement Plan (telemetry_consent="denied").
   >
   > migbot is now DISABLED: the migration pipeline (from $a2h-spec onward) will
   > refuse to run, and nothing is uploaded. Participation is required to use the
   > tool. Stale artefacts may still sit under .migbot/metrics/; they are never
   > sent. To purge the local cache:  rm -rf .migbot/metrics/
   >
   > Re-enable any time with:  $a2h-privacy accept
   > To request deletion of already-uploaded server-side data, contact us per the
   > policy's §8 (quote your migbot_session_id, shown by $a2h-privacy status).
   > ```

---

## §D. off  (synonym for deny — also disables migbot)

`off` is a synonym for `deny` under the binary model (both decline and disable migbot).

1. Read `.migbot/config.json`:
   - File missing → tell the user `"migbot is not installed in this project. Run install.sh first."`, stop.
2. Run `Bash: .migbot/bin/a2h init-run --consent denied` to record the decline in `.migbot/config.json` (this sets `telemetry_consent` to `"denied"`; the existing `migbot_session_id` is preserved so a later deletion request still has the handle).
3. Print the same disabled notice as §C, remind the user that `$a2h-privacy accept` re-enables migbot, and note the one-shot env kill switch `A2H_TELEMETRY_OFF=1` — exporting it makes the runtime upload nothing for that session regardless of consent.

---

## Notes

- All timestamps must be ISO-8601 UTC (e.g. `2026-05-26T10:30:00Z`).
- `$a2h-privacy accept` **must** present the policy to the user before asking — out of band via `a2h-agreement` (a popup window, or the file path on a GUI-less environment). **Never** write `granted` without having shown the agreement; doing so would constitute "insufficient disclosure" and violates the policy itself. The agreement is **never** pasted into the conversation: the popup/path shows the full file out of band so it does not consume the agent's context window. If no window can be raised (WSL / Git Bash / headless / macOS sandbox), the script degrades to printing the path — it does **not** fall back to dumping the text, and neither should you.
- Participation is **binary**: declining the Plan (`deny`/`off`, or `A2H_TELEMETRY_OFF=1`) disables migbot entirely and uploads nothing — there is no partial "minimal" tier. Only `granted` enables the tool. Be precise about this when talking to the user.
- In §A–§D, if **any** step fails (missing file, Edit error, user cancellation), do **not** write `granted`; the safe default is to leave the config untouched.
- Never edit `.agents/skills/` or `.claude/agents/` from this command. Only `.migbot/config.json` is in scope.
