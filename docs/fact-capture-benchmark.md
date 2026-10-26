# Repeatable synthetic fact-capture benchmark

This benchmark measures `ios_facts.extract`, obligation construction and a final
source snapshot in a fresh worker process. It makes no provider or model calls;
tokens are `not_applicable`. It does not convert an application and does not
establish functional, visual, end-to-end migration, two-hour or 20M-token acceptance.
There is no overall migration PASS. Do not extrapolate its timings to migration
throughput.

## Run

Use an existing Python 3.11+ runtime. No installation is required. On Windows,
`--runtime` and `--output` must resolve to absolute D: directories. The runtime
argument is the **src** directory containing `hmigbot_ios/ios_facts.py`.
The output's parent must exist; the output itself must not exist, even if empty.
Every invocation needs a new output directory. Source files, logs and reports all
stay in that directory. Windows worker TEMP/TMP are set to `D:/Temp`, and bytecode
cache writes are disabled. On other platforms absolute paths are accepted.

```powershell
$env:TEMP = 'D:/Temp'
$env:TMP = 'D:/Temp'
$env:PYTHONDONTWRITEBYTECODE = '1'
$python = 'D:/DevTools/hmigbot-test-20261020/Scripts/python.exe'
$runtime = 'D:/IOS2Harmony/hmigbot-implementation-20261020/integration/src'
& $python scripts/benchmark_fact_capture.py --runtime $runtime --lines 100000 --files 100 --output D:/Temp/fact-capture-100k-run1 --timeout 300
& $python scripts/benchmark_fact_capture.py --runtime $runtime --lines 200000 --files 200 --output D:/Temp/fact-capture-200k-run1 --timeout 600
# Optional extension probe, not an acceptance requirement:
& $python scripts/benchmark_fact_capture.py --runtime $runtime --lines 500000 --files 500 --output D:/Temp/fact-capture-500k-run1 --timeout 1200
```

Use the same LOC, file count, runtime and machine for comparisons; retain separate
output directories and record the runtime revision alongside the reports. Do not
run a large probe against a version known to reread and split a full source file
for every fact. Start with a small probe or a short timeout. Each size is a
separate invocation and process. Exit 0 means the fact capture completed; exit 1
means a retained failed result; exit 2 means invalid arguments or an output
directory that was refused.

## Dataset and measurements

`--lines` and `--files` are required integers. Lines are exact physical,
newline-terminated source lines, including imports and padding comments. Files are
balanced to within one line. Each file must have 12 through 10,000 lines. Choose
roughly 1,000 lines per file for scale probes, rather than one very large file.
The generated Swift has shallow independent View structs, uniquely named owners
and state variables, two state declarations, three string literals and two events
per 11-line block. At most ten deterministic comment lines pad a file to its exact
size. Identical arguments yield identical relative filenames, source bytes and
source fingerprint across independent output paths. These are synthetic lexical
inputs; compilation and behavior are not tested.

`report.json` includes exact `source.loc`, `source.files`, `source.source_bytes`,
fact/obligation counts, counts by fact kind, capture wall seconds and the final
source SHA-256. The generated fingerprint uses the runtime snapshot's canonical
ordered file entries (relative path, byte count, per-file SHA-256). A completed
capture must match both its initial runtime fingerprint and this generated
fingerprint. Source generation, imports and report serialization are excluded
from `capture_wall_seconds`; `subprocess_wall_seconds` includes worker startup and
report writing. Fact and obligation graph serialization to disk is not measured.

`peak_memory` gives the worker's lifetime peak, including imports, using Windows
`GetProcessMemoryInfo.PeakWorkingSetSize`, or `resource.ru_maxrss` on supported
Unix platforms. Its platform and method are explicit. Unavailable measurements
are null, not zero. The metric is not a resettable capture-only allocation peak.

`read_bytes` instruments successful `pathlib.Path.read_bytes` calls **inside the
generated source tree only**. It reports calls and logical bytes by phase:

- `extraction_snapshot`: snapshot reads made during extraction.
- `capture_other`: other reads during extraction and obligation construction,
  including per-fact rereads in older implementations.
- `final_snapshot`: the independent final fingerprint check.

Two full snapshot passes are expected. Compare `capture_other`, maximum calls per
file and `logical_bytes_per_source_byte` to detect amplification beyond those
passes. These are API-level logical bytes returned to Python, **not physical disk
I/O** or OS cache misses. `read_text`, direct `open` and `mmap` are outside this
counter; `disk_io_bytes` is deliberately null. Instrumentation adds overhead, so
compare instrumented runs consistently. Runtime imports and report/log reads do
not contribute to source read counters.

Failed workers and timeouts retain `source/`, `worker.stdout.log`,
`worker.stderr.log` and a `status: failed` report. A completed worker also retains
`worker-result.json`. Missing counts and unfinished final hashes remain null;
timeout duration is not presented as successful capture time.

## Small regression tests

```powershell
$env:TEMP = 'D:/Temp'
$env:TMP = 'D:/Temp'
$env:PYTHONDONTWRITEBYTECODE = '1'
& D:/DevTools/hmigbot-test-20261020/Scripts/python.exe -m pytest tests/test_scale_benchmark.py -q -p no:cacheprovider --basetemp D:/Temp/fact-capture-small-tests
```

The tests check exact LOC/bytes/facts/obligations, reproducibility, source-only
read attribution, directory refusal, failure logs and timeouts using tiny inputs.
They do not run any 100k, 200k or 500k probes.
