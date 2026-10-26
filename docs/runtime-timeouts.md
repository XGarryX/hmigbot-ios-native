# Subprocess timeouts and a shared deadline

Large source trees can spend more than 60 seconds inside scheduler validation or
more than 180 seconds in the structural pipeline. Those wrapper limits are now
configurable through inherited environment variables. No vendor archive or
scheduler algorithm is changed. These controls do not add adaptive parallelism.

| Environment variable | Default seconds | Actual consumer |
|---|---:|---|
| `HMIGBOT_SCHEDULER_TIMEOUT_SECONDS` | 60 | `ios_scheduler.invoke` and installed `windows_scheduler_runtime.invoke`; plan validation, next-batch, landing and state operations |
| `HMIGBOT_STRUCTURAL_TIMEOUT_SECONDS` | 180 | `native_pipeline_runtime._invoke_raw`; raw original structural loop |
| `HMIGBOT_LITERAL_TIMEOUT_SECONDS` | 60 | `native_literal_scope._original`; each raw/page-projection original literal detector |
| `HMIGBOT_ASSEMBLY_TIMEOUT_SECONDS` | 60 | `native_pipeline_semantics.assembly_main`; staged nested assembly detector |
| `HMIGBOT_JOIN_TIMEOUT_SECONDS` | 60 | `join_rollout.main`; original join gate, excluding its existing Git provenance probes |
| `HMIGBOT_HELPER_TIMEOUT_SECONDS` | unbounded | `native_helpers.original`; other original helper subprocesses |

Direct `native_helpers.original` calls historically had no timeout. That default
is preserved, including the legacy non-Windows structural callback. Explicit
structural/literal/assembly overrides are selected for those named helpers;
other helpers use the helper setting. A supplied deadline also bounds these
historically unbounded helper waits.

Values are finite positive numeric seconds, including fractions, at most 604800
seconds (one week) per subprocess. Zero, negatives, NaN, infinity, empty strings,
non-numbers and larger stage values raise an explicit configuration error. The
default values remain 60/180 seconds where those limits already existed. Staging
the disposable runtime is outside a per-process cap.

`HMIGBOT_DEADLINE_EPOCH_SECONDS` optionally supplies one **absolute UTC Unix epoch
timestamp** for all covered subprocesses. Every launch uses the smaller of its
stage cap and the remaining deadline. The timestamp is inherited unchanged by
children, so a nested literal or assembly check does not reset it. The deadline is
checked both before expensive scheduler/pipeline staging and at child launch.
The timestamp must be finite, positive and at most one week in the future.
An already expired deadline starts no child and reports failure. This optional
wall-clock deadline includes elapsed staging time, but it does not preempt Python
code while it is running; it is checked at the covered subprocess boundaries.

For example, in the same PowerShell session as the existing migration commands:

```powershell
$env:HMIGBOT_SCHEDULER_TIMEOUT_SECONDS = '900'
$env:HMIGBOT_STRUCTURAL_TIMEOUT_SECONDS = '1800'
$env:HMIGBOT_LITERAL_TIMEOUT_SECONDS = '600'
$env:HMIGBOT_ASSEMBLY_TIMEOUT_SECONDS = '600'
# One shared deadline, computed once before the desired workflow:
$deadlineEpochSeconds = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds() + 7200
$env:HMIGBOT_DEADLINE_EPOCH_SECONDS = [string]$deadlineEpochSeconds
python scripts/a2h_ios.py next-batch --project D:/Example/Harmony --wave domains
```

The same inherited settings reach `plan-ir`, `next-batch` and `land-results`
through `scripts/a2h_ios.py`, and the structural/literal skill frontends through
their native runtime bridges. They are consumed by the wrapper execution path;
they do not change a project plan, receipt, ownership rule or acceptance result.
Preparation and conversion **can use these larger wrapper allowances when they
reach those consumers**. Pure in-process source preparation has no new timer.

Windows launches in these bridges use the existing owned Job process runner.
Timeout terminates its owned descendants and retains real partial output.
Scheduler timeouts replace stale stdout/stderr logs and write a failure record;
structural timeout returns 124; literal/assembly timeout replaces any requested
old success JSON with a failing result containing partial process evidence.
Join timeout returns an unverified result containing partial process evidence.
Unix launches preserve their existing subprocess mechanism; equivalent process
tree ownership is not introduced on Unix by this change.

Raising a timeout does not establish that 100k lines convert within two hours,
or that any token, functional or visual acceptance target passed. The usage
ledger remains separate and must record actual work. These execution guards do
not reserve tokens, measure throughput or automatically choose worker counts.
Build commands, provider-specific configured timeouts, Git provenance probes,
cloud calls and limits internal to immutable vendor engines retain their own
contracts. This is not a universal hard deadline over every activity.

Focused tests use injected execution limits and one 0.6-second owned Windows
process-tree timeout; they do not wait 60 seconds or execute an application
conversion or scale benchmark.
