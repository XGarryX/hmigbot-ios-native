# HarmonyOS Build Log Diagnostics

Reusable, read-only diagnostics for HarmonyOS build output: parse real captured
stdout/stderr logs plus the real process returncode and produce a structured,
re-verifiable report. Implementation: `src/hmigbot_ios/harmony_diagnostics.py`.
Tests: `tests/test_harmony_diagnostics.py`.

## Status semantics (core contract)

| Condition | `status` | `build_command_passed` |
|---|---|---|
| returncode != 0 or None, errors parsed | `fail_with_errors` | false |
| returncode != 0 or None, nothing parseable | `fail_unparsed` (never PASS) | false |
| returncode == 0, no error findings | `build_command_passed` | true |
| returncode == 0, ERROR/FATAL or BUILD FAILED evidence present | `conflicting_build_evidence` | false |

`returncode=0` only means the build command exited 0: `functional_verified` and
`ui_verified` are always `false`. `process_exit_zero` preserves that process
fact; `overall_status` is `unknown` for an otherwise clean zero exit, `conflict`
for contradictory logs, and `fail` for nonzero/missing exit codes.
`error_code`, `file`, `line`, `column` and
`target` are only reported when literally present in the log; every finding
pins the exact original log line via `log_ref` and states its `basis` (local
DevEco skill data or an explicit heuristic marker). Unmatched errors stay
`category: "unknown"` with low confidence.

## API

`build-target` now saves `diagnostics.json` beside its original logs and pins its
hash in `build.json`. Compiler errors or a failure marker contradicting exit zero
prevent a `build_passed` result. A successful build still needs its HAP, success
marker and current source fingerprint; diagnostics alone do not prove compilation.

For logs captured separately, run from the distribution root:

```powershell
python scripts/ios2harmony.py diagnose-build --stdout 'D:/Build/stdout.log' --stderr 'D:/Build/stderr.log' --returncode 1 --module entry --output 'D:/Build/diagnostics.json'
```

Use the real return code; omit it only when unknown (for example, a timeout).
The CLI prints a small receipt; findings remain in the output report. Failed or
conflicting build evidence exits 3, invalid input exits 2, and a completed
diagnosis with a clean zero exit returns 0 without verifying UI or functionality.

```python
import json
from pathlib import Path
from hmigbot_ios.harmony_diagnostics import analyze, save_report, verify

report = analyze(
    Path("build-logs/stdout.log"),          # required: captured stdout log
    Path("build-logs/stderr.log"),          # optional: captured stderr log
    proc.returncode,                        # real exit code (int or None)
    target={"module": "entry", "module_target": "default"},  # optional identity
)
print(report["status"], report["summary"]["errors"])
for f in report["findings"]:
    print(f["log_ref"], f["error_code"], f["category"], f["suggestion"])

save_report(report, Path("build-logs/diagnostics.json"))
loaded = json.loads(Path("build-logs/diagnostics.json").read_text(encoding="utf-8"))
assert verify(loaded)   # False once any source log changed/moved/deleted
```

`verify(report) -> bool` re-hashes every recorded log (SHA-256 kept in
`report["logs"][stream]["sha256"]`) and detects drift. It raises
`MigrationError` for non-diagnostics payloads.

`target` accepts only `module`, `module_target`, and `product` identity fields
with bounded string identifiers; unknown fields, scalar metadata and recognized
credential patterns are rejected without echoing their values. This is not a
general metadata transport.

## Coverage

Classifications derive from the installed skills `arkts-error-fixes`
(ArkTS type/syntax: object literals, standalone `this`, catch clause,
possibly-null, unused vars, duplicate `@Entry`, etc.) and
`deveco-studio-hvigor` (hvigorw invocation, modelVersion compatibility,
signing/keystore, environment), plus explicit heuristics for module/resource
dependencies, `@ohos`/`@kit` SDK imports and device cases. Categories:
`arkts_type`, `arkts_syntax`, `arkts_lint`, `module_dependency`, `resource`,
`sdk_api`, `hvigor`, `signing`, `device`, `unknown`.

## Safety

- Logs are read once, hashed, never modified (originals kept read-only, hashes
  auditable via `verify`). `save_report` refuses output paths resolving to either
  input log or sharing its file identity, including hard-link aliases. A separate
  existing report can be replaced.
- Credential-like lines (passwords, tokens, private keys, Bearer values) are
  never copied into reports; they are replaced with `[REDACTED:...]` markers and
  counted in `redacted_lines`.
- Sensitive assignments, including quoted keys and values containing spaces,
  redact the entire diagnostic line. Masking uses recognizable credential
  patterns and cannot detect every arbitrary secret embedded in free text.
- Signing suggestions only guide read-only inspection and authorized valid
  configuration; existing signingConfigs and credentials must be preserved.
- The API never edits source code, signing configuration or devices, never
  accesses the network and never calls model APIs (see `report["api_contract"]`).

## Limitations

- Rules were validated against synthetic logs modeled on DevEco/hvigor output
  only; no real-device or real-project HarmonyOS build capture was used. Real
  target compilation logs remain to be verified by the coordinator.
- Not every log format is parsed; unparsed non-zero builds are reported as
  `fail_unparsed` rather than guessed.

## Running the tests

```powershell
$env:PYTHONDONTWRITEBYTECODE="1"
$env:PYTHONPATH="<repo>\src"
$env:TEMP="D:\Temp"; $env:TMP="D:\Temp"
& "<configured-python.exe>" -m pytest tests/test_harmony_diagnostics.py -q -p no:cacheprovider
```

The initial module, fixtures and guide were drafted by DevEco. Codex independently
reviewed the draft and added the input/output collision guard, bounded target
identity contract, stronger redaction, conflicting-evidence status and signing
preservation advice with focused counterexample tests.
