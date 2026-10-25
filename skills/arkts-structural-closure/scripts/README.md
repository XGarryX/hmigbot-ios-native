# arkts-structural-closure / scripts

Deterministic detection scripts implementing the structural verification
protocol defined in [`../SKILL.md`](../SKILL.md). All scripts produce
structured JSON and use exit code conventions (0 = pass, 1 = fail / findings).

> **鍗忚鏂囨。**锛氭墍鏈?loop 鐩稿叧鑴氭湰锛坄run_loop.sh` / `structural_loop.py` / `loop_runner.py`锛?> 瀹炵幇鐨勬槸 [`../SKILL.md`](../SKILL.md) 搂3 瀹氫箟鐨勫崗璁紙verdict 5 绫?+ 鏀舵暃甯搁噺 + repair worker 娲惧彂锛夈€?> 璋冭剼鏈箣鍓?LLM 蹇呴』鍏堝姞杞?SKILL.md锛屽惁鍒?verdict 澶勭疆閿欒銆?
## CLI entries

| Script | Purpose | When called |
|---|---|---|
| `run_loop.sh` | **loop 鍏ュ彛**锛堜粎 slice / pipeline 涓ょ mode锛夛細鍖呰 structural_loop iterate锛岃矾寰勫叏鑷姩娲剧敓 | 搂5e (slice) / 搂6 (pipeline) 涓ゅ锛汼tage 1/2 鏈熬 搂3c 鏀圭敤涓€娆℃€?`audit_skeletons` 涓嶈蛋 loop |
| `structural_loop.py` | Loop 鍗曟杩唬 + finalize锛氭娴?鈫?verdict 鈫?dispatch_prompt | 琚?run_loop.sh 璋冪敤锛沠inalize 鏀跺熬鏃剁嫭绔嬭皟鐢?|
| `audit_skeletons.py` | Skeleton detection (10 瀛愮被) + escape-hatch + dangling FWD-REF | 琚?structural_loop 鍐呴儴璋冪敤锛坰tage / slice / all 涓夌 scope锛?|
| `verify_slice_wiring.py` | Slice-level wiring closure C1-C4 | 琚?structural_loop slice 妯″紡鍐呴儴璋冪敤 |
| `check-fullscreen-immersive-safearea.sh` | 娌夋蹈寮?+ 瀹夊叏鍖哄洓浠跺 lint | 琚?structural_loop pipeline 妯″紡鍐呴儴璋冪敤 |
| `loop_runner.py` | 鏀舵暃 verdict 鍒ゅ畾锛圕ONVERGED/CONTINUE/STALLED/REGRESSED/EXHAUSTED锛?| structural_loop 鍐呴儴搴擄紱浜﹀彲鐙珛 CLI 璋冭瘯 |

## Subpackages (library code)

Imported by CLI scripts; not meant to be invoked directly.

| Package | Responsibility |
|---|---|
| `skeleton_lib/` | 10-subtype taxonomy + regex patterns + RegistryResolver + classifier |
| `ref_graph_lib/` | .ets parser 鈫?project-wide import + instantiation graph 鈫?orphan detection |
| `plan_lib/` | feature-plan.md slice header YAML parser (wires[VM + embed], integration_points, cross_slice_edits) |

## Calling convention

Each CLI script:

```bash
python3 .agents/skills/arkts-structural-closure/scripts/<name>.py \
    --project-root <abs> \
    [--output-json <path>] \
    [script-specific args...]
```

Exit codes:
- `0` 鈥?no FAIL-level findings (PASS / WARN only); safe to proceed
- `1` 鈥?at least one FAIL finding; structural_loop should dispatch repair
- `2` 鈥?argument / IO error

All scripts emit UTF-8 JSON to `--output-json` or stdout.

## Cross-skill access

Skills outside a2h-execute (e.g. a2h-verify CHECK-2/3 sanity in Phase 3)
**invoke the CLI directly** via the path above; they do **not** import
the sub-packages. This keeps the lib boundary internal to a2h-execute.

If a second skill ever needs the same library, refactor at that time
into a shared location 鈥?not preemptively.

## Adding a pattern

Edit one place: `skeleton_lib/patterns.py`. The pattern is automatically
picked up by `audit_skeletons.py` and (transitively) by `verify_slice_wiring.py`
C4's residual-skeleton check.

Severity rules (L1/L2/L3/L4 鈫?PASS/WARN/FAIL) live in
`skeleton_lib/taxonomy.py` and are hard-coded (no YAML config).
