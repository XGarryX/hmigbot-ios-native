---
name: a2h-run
description: Trigger: `$a2h-run` or natural language. Run the full a2h migration pipeline (spec → plan → execute → verify → retrospect) with per-stage confirmation and auto-resume.
---

> Codex skill (converted from the `a2h-run` slash command). Invoke with `$a2h-run`, or pick it in `/skills` (the default_prompt below auto-runs). Codex has no custom slash commands, so the `$` prefix replaces `/`.


the user's input (the command argument) is ignored. `$a2h-run` does not forward arguments. For feature-scoped specs, invoke the `a2h-spec` skill directly with a feature name.

## Goal

Sequence the five pipeline-stage skills end-to-end, pausing for user confirmation between stages and auto-resuming where a previous run left off. Stop on any failure.

## 1. Detect mode

Read `.migbot/config.json` from the current working directory.

- If the file does not exist, stop and tell the user: `"migbot is not installed in this project. Run install.sh first."`
- Read the `confirmed` key.
  - `confirmed != true` (false, missing, or any other value) → stop and tell the user: `"Config not confirmed yet. Run $a2h-init first to confirm the android / harmonyos / hvigorw paths, then re-run $a2h-run."`. Do not proceed.
## 2. Probe completion markers

Check each stage's marker files in order to determine the resume point. A stage counts as complete only when **all** of its markers exist.

| # | Stage              | Markers                                                                                |
|---|--------------------|----------------------------------------------------------------------------------------|
| 1 | `a2h-spec`         | `spec/baseline/ui-manifest.md` AND `spec/baseline/feature-index.md`                    |
| 2 | `a2h-plan`         | `spec/baseline/plans/ui-plan.md` AND `spec/baseline/plans/feature-plan.md`             |
| 3 | `a2h-execute`      | `spec/migration-report.md`                                                             |
| 4 | `a2h-verify`       | `spec/verify-report.md`                                                                |
| 5 | `a2h-retrospect`   | At least one file matching `docs/retrospect-report-*.md` **AND** at least one file matching `.migbot/metrics/*/retrospect.done` |

> **Important: both marker files must be produced by the a2h-retrospect skill's closing step.** In particular, `retrospect.done` must be a side effect of running `.migbot/bin/a2h mark-stage a2h-retrospect`; that call writes the stage-marks fact and drops the sentinel (it strips the `a2h-` prefix, so the file is `retrospect.done`) — consent `granted` uploads the fact, otherwise it silently no-ops, **both satisfy the marker**. Per-stage token usage is not collected here: the lifecycle hooks upload the session transcript and the server parses usage out of it. **Never use Write/Edit to create files under `.migbot/metrics/` (including `retrospect.done`) just to "satisfy" the marker** — that bypasses the real collection and writes fake data. If a marker is missing, go back to the a2h-retrospect skill and re-run `mark-stage`; do not fabricate the file by hand.

The resume target is the first stage whose markers are missing.

- **All markers missing** → start at stage 1; no prompt.
- **Some markers present** → list completed stages and prompt: `"Detected completed stages: <list>. Resume from <next stage>? (yes / restart from spec / stop)"`. On bare `yes` proceed from the resume target; on `restart from spec` start at stage 1; on anything else halt with `"Stopped before any stage ran."`.
- **All five stages have markers** → prompt: `"All five stages have completion markers. Re-run from spec, or stop? (restart / stop)"`. On `restart` start at stage 1; otherwise halt.

## 3. Run each stage

For each stage from the resume target through stage 5, in this fixed order: `a2h-spec`, `a2h-plan`, `a2h-execute`, `a2h-verify`, `a2h-retrospect`.

1. Announce: `"Starting stage <N>/5: <id>."`
3. After the stage's own steps finish, summarize in 2-3 lines: list new/changed files under that stage's expected output paths and a one-line outcome.
4. **Join outstanding subagents (HARD-GATE — issue #23).** If the stage skill dispatched any background subagents (`spawn_agent`) whose results have not been collected yet, collect every outstanding handle NOW by calling `wait_agent` in a loop — a timeout means "still running", call it again. Never end the turn while a handle is outstanding: in Codex nothing re-invokes this session when a subagent finishes, so an ended turn stalls the whole pipeline silently with no prompt (the multi-module hang in issue #23). Only after every handle is joined, proceed to the marker check.
5. Verify the stage's completion markers (from §2) now exist. If any required marker is missing, treat the stage as failed and apply the failure handling below.
   > Token-usage reporting is no longer done here — each pipeline skill reports its own stage as its final step (`a2h mark-stage <id>`). So a skill run standalone (not via `$a2h-run`) still reports. Nothing to do at this step beyond the marker check.
6. Prompt: `"Continue to next stage? (yes / stop)"`
   - `yes` → next stage.
   - anything else → halt with: `"Stopped at <id>. Resume with $a2h-run."`
7. **Failure handling.** If the stage skill raises an error, prints `STOP`, or fails to produce its required completion markers, halt with: `"Stopped at <id> due to error: <one-line summary>. Resume with $a2h-run after addressing the issue."`. No auto-retry.

## 4. After stage 5

Print a final summary listing the five stages and their outputs (paths only, one per line).

Then check telemetry delivery: run `Bash: .migbot/bin/a2h status --json` (ignore a non-zero exit or unknown subcommand — older runtimes don't have it). If the output reports pending or dead outbox entries, append this advisory note (informational only — uploads are hook-driven and retry automatically; never block or retry here):

> Note: <N> telemetry upload(s) are still queued locally and will be retried automatically. You can flush them now with `.migbot/bin/a2h flush`.

Then remind the user:

> All five stages complete. Run `$a2h-build` to compile the migrated code.
