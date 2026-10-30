#!/bin/bash
# run_loop.sh — Drive ONE structural_loop iteration with auto-derived paths.
#
# Per a2h-execute design: the LLM main flow must dispatch repair workers itself
# (Python can't invoke 模型 agents). So this script runs ONE iteration and
# exits, letting the LLM branch on exit code.
#
# Usage:
#   bash scripts/run_loop.sh --mode slice    --target 3 --round 1 --project-root .
#   bash scripts/run_loop.sh --mode stage    --target 1 --round 1 --project-root . \
#       --diff-base abc123 --handoffs path/to/h1.md path/to/h2.md ...
#   bash scripts/run_loop.sh --mode pipeline --target final --round 1 --project-root .
#
# Auto-derived paths (under <project-root>/spec/execution/autofix-log/round-<R>/):
#   - state file: loop-state-<mode>-<target>.json
#   - latest result: loop-result-latest-<mode>-<target>.json (overwritten per iter)
#   - per-iter audit / wiring detail JSONs (named by structural_loop.py internally)
#
# Exit codes (mirror structural_loop.py iterate):
#   0 — CONVERGED: loop done, dispatch finalize and write handoff
#   1 — CONTINUE: LLM must dispatch repair worker per loop-result-latest.dispatch_prompt
#                 then re-invoke this script
#   2 — ESCALATED (STALLED / REGRESSED / EXHAUSTED): write handoff escalation
#   3 — argument / IO error

set -e

# ─── Windows / Git-Bash (MSYS/MINGW) path fix ────────────────────────────────
# Under MINGW/Git-Bash, `pwd` yields an MSYS path like `/d/Coding/...`. A native
# Windows python.exe CANNOT open it — it mis-resolves `/d/...` to `D:\d\...` and
# fails ("can't open file 'D:\\d\\...\\structural_loop.py'"). Convert any ABSOLUTE
# MSYS path that is handed to python.exe into a native path via `cygpath -m`
# (mixed mode = `D:/...`, forward slashes → safe to pass through the shell).
# Relative paths (`.`, `./x`) are left untouched so they keep resolving against the
# unchanged cwd. No-op on Linux/macOS (no `cygpath`; paths are already native).
winpath() { if command -v cygpath >/dev/null 2>&1; then cygpath -m "$1"; else printf '%s' "$1"; fi; }
maybe_native() { case "$1" in /*) winpath "$1" ;; *) printf '%s' "$1" ;; esac; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STRUCTURAL_LOOP="$(maybe_native "$SCRIPT_DIR/structural_loop.py")"

# Native input guard must run even when an original standalone binary is present.
PY=""
for _p in python3 python; do
    command -v "$_p" >/dev/null 2>&1 && { PY="$_p"; break; }
done
if [[ -z "$PY" ]]; then
    echo "error: Python is required for the native source-input guard" >&2
    exit 3
fi
ENTRY_BIN=""
run_structural_loop() {
    "$PY" "$STRUCTURAL_LOOP" "$@"
}

MODE=""
TARGET=""
ROUND=""
PROJECT_ROOT=""
DIFF_BASE=""
SLICES=""
HANDOFFS=()
ANDROID_RES=()
DENSITY=""
MAX_ITER=""

# ─── Parse args ──────────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
    case "$1" in
        --mode) MODE="$2"; shift 2 ;;
        --target) TARGET="$2"; shift 2 ;;
        --round) ROUND="$2"; shift 2 ;;
        --project-root) PROJECT_ROOT="$2"; shift 2 ;;
        --diff-base) DIFF_BASE="$2"; shift 2 ;;
        --slices) SLICES="$2"; shift 2 ;;
        --handoffs)
            shift
            while [[ $# -gt 0 && "$1" != --* ]]; do
                HANDOFFS+=("$1")
                shift
            done
            ;;
        --android-res)
            shift
            while [[ $# -gt 0 && "$1" != --* ]]; do
                ANDROID_RES+=("$1")
                shift
            done
            ;;
        --density) DENSITY="$2"; shift 2 ;;
        --max-iter) MAX_ITER="$2"; shift 2 ;;
        -h|--help)
            sed -n '2,30p' "$0"
            exit 0
            ;;
        *)
            echo "error: unknown arg $1" >&2
            exit 3
            ;;
    esac
done

# ─── Validate ────────────────────────────────────────────────────────────────
if [[ -z "$MODE" || -z "$TARGET" || -z "$ROUND" || -z "$PROJECT_ROOT" ]]; then
    echo "error: --mode, --target, --round, --project-root all required" >&2
    exit 3
fi
if [[ "$MODE" != "stage" && "$MODE" != "slice" && "$MODE" != "group" && "$MODE" != "pipeline" ]]; then
    echo "error: --mode must be 'stage' / 'slice' / 'group' / 'pipeline', got '$MODE'" >&2
    exit 3
fi
if [[ "$MODE" == "stage" && -z "$DIFF_BASE" ]]; then
    echo "error: --diff-base required for --mode=stage" >&2
    exit 3
fi
if [[ "$MODE" == "group" && -z "$SLICES" ]]; then
    echo "error: --slices N,M,... required for --mode=group" >&2
    exit 3
fi
if [[ ! -d "$PROJECT_ROOT" ]]; then
    echo "error: project root does not exist: $PROJECT_ROOT" >&2
    exit 3
fi

# ─── Derive paths ────────────────────────────────────────────────────────────
LOG_DIR="$PROJECT_ROOT/spec/execution/autofix-log/round-$ROUND"
mkdir -p "$LOG_DIR"
STATE_FILE="$LOG_DIR/loop-state-$MODE-$TARGET.json"
RESULT_FILE="$LOG_DIR/loop-result-latest-$MODE-$TARGET.json"

# ─── Build structural_loop iterate args ──────────────────────────────────────
LOOP_ARGS=(
    iterate
    --project-root "$(maybe_native "$PROJECT_ROOT")"
    --mode "$MODE"
    --target "$TARGET"
    --state-file "$(maybe_native "$STATE_FILE")"
    --output-json "$(maybe_native "$RESULT_FILE")"
)
if [[ -n "$DIFF_BASE" ]]; then
    LOOP_ARGS+=(--diff-base "$DIFF_BASE")   # git SHA, not a path → never converted
fi
if [[ -n "$SLICES" ]]; then
    LOOP_ARGS+=(--slices "$SLICES")         # mode=group: comma-separated slice numbers
fi
if [[ ${#HANDOFFS[@]} -gt 0 ]]; then
    LOOP_ARGS+=(--handoffs)
    for _h in "${HANDOFFS[@]}"; do LOOP_ARGS+=("$(maybe_native "$_h")"); done
fi
if [[ ${#ANDROID_RES[@]} -gt 0 ]]; then
    LOOP_ARGS+=(--android-res)
    for _r in "${ANDROID_RES[@]}"; do LOOP_ARGS+=("$(maybe_native "$_r")"); done
fi
if [[ -n "$DENSITY" ]]; then
    LOOP_ARGS+=(--density "$DENSITY")
fi
if [[ -n "$MAX_ITER" ]]; then
    LOOP_ARGS+=(--max-iter "$MAX_ITER")     # risk-conditional iteration cap (item6); structural_loop defaults to 8 when omitted
fi

# ─── Invoke ──────────────────────────────────────────────────────────────────
set +e
run_structural_loop "${LOOP_ARGS[@]}"
LOOP_EXIT=$?
set -e

# Input/IO failure is not the CONTINUE (1) or ESCALATED (2) protocol.
# In particular, never consume a prior CONVERGED result after a native guard stop.
if [[ "$LOOP_EXIT" -eq 3 ]]; then
    echo "[run_loop.sh] STOP_NATIVE_INPUT_OR_IO: no automatic retry, finalize, or stage advance. Inspect the current error/guard evidence; correct the input before explicitly invoking again." >&2
    exit 3
fi

# ─── Echo verdict line on stderr for LLM visibility ──────────────────────────
if [[ -f "$RESULT_FILE" ]]; then
    RESULT_NATIVE="$(maybe_native "$RESULT_FILE")"
    STATE_NATIVE="$(maybe_native "$STATE_FILE")"
    LOG_DIR_NATIVE="$(maybe_native "$LOG_DIR")"
    # 一次解析读三个字段（原为三次 `python3 -c`，各起一个进程读同一文件）。
    # 且此处已恢复 `set -e`：任一次解析非零退出都会直接终止脚本，把后面的
    # result_json / state_file / CONTINUE 指引全部吞掉 —— LLM 因此拿不到下一步。
    # 故显式 `|| true` 兜底，解析失败降级为 '?' 而不是中断输出。
    _SUMMARY=$(
        { [[ -n "$PY" ]] && "$PY" -c "
import json
d = json.load(open(r'''$RESULT_NATIVE''', encoding='utf-8'))
print(d.get('verdict', '?'))
print(d.get('iteration', '?'))
print(d.get('current_state', {}).get('total_fail', '?'))
"; } 2>/dev/null || true
    )
    VERDICT=$(sed -n '1p' <<<"$_SUMMARY"); VERDICT=${VERDICT:-?}
    ITER=$(sed -n '2p' <<<"$_SUMMARY");    ITER=${ITER:-?}
    FAIL=$(sed -n '3p' <<<"$_SUMMARY");    FAIL=${FAIL:-?}
    echo "[run_loop.sh] mode=$MODE target=$TARGET iter=$ITER verdict=$VERDICT total_fail=$FAIL" >&2
    echo "[run_loop.sh] result_json=$RESULT_NATIVE" >&2
    echo "[run_loop.sh] state_file=$STATE_NATIVE" >&2
    if [[ "$LOOP_EXIT" -eq 1 ]]; then
        echo "[run_loop.sh] CONTINUE → dispatch repair worker with result.dispatch_prompt, then re-invoke this script" >&2
    elif [[ "$LOOP_EXIT" -eq 0 ]]; then
        FINAL_JSON=$([[ "$MODE" == "pipeline" ]] && echo "loops-final-structural-closure" || echo "loops-$MODE-$TARGET")
        # 提示里给出本机实际可用的调用方式（编译态用 _entry.bin 子命令，否则系统解释器）
        if [[ -n "$ENTRY_BIN" ]]; then
            FINAL_CMD="$ENTRY_BIN structural_loop finalize"
        else
            FINAL_CMD="$PY $STRUCTURAL_LOOP finalize"
        fi
        echo "[run_loop.sh] CONVERGED → call: $FINAL_CMD --state-file $STATE_NATIVE --output-json $LOG_DIR_NATIVE/$FINAL_JSON.json" >&2
        echo "[run_loop.sh] NOTE: finalize 会跑 detector 完成度闸；缺项将判 INCOMPLETE 而非 PASS" >&2
    elif [[ "$LOOP_EXIT" -eq 2 ]]; then
        echo "[run_loop.sh] ESCALATED → finalize then write handoff escalation section" >&2
    fi
fi

exit $LOOP_EXIT
