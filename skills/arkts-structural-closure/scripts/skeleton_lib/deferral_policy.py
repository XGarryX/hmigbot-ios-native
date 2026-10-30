"""deferral_policy — single source of truth for deciding whether an unresolved
forward-ref is a *legitimate external deferral* (survives the pipeline) or an
*in-pipeline wiring gap* (must be paid before the pipeline ends).

Two consumers share this policy so they can never drift apart:
  - skeleton_lib.classifier.scan_dangling_fwd_refs   (P3: stale in-code marker)
  - scripts/verify_closure_ledger.py                 (P2: pipeline-end ledger gate)

────────────────────────────────────────────────────────────────────────────
WHY THIS EXISTS  (root-cause: AIPPT migration, 2026-06-13)
────────────────────────────────────────────────────────────────────────────
FV-1 (pipeline structural closure) declared PASS while ~39 in-app wiring
forward-refs sat unresolved — among them P-S4-HOM-* (HomePage onResume needs
HomeViewModel, never built) and P-S4-MIN-* (MineTab needs SaleCenterViewModel,
never built). They slipped because the dangling-fwd-ref detector only flagged a
lingering marker when its owning slice handoff was `final_state: PASS`. Slices
4/7/9 finished as `ESCALATED` (for *unrelated* benign false-positives), so every
unresolved marker they owned was silently amnestied as "slice not done yet,
marker legitimate". But ESCALATED is TERMINAL in this pipeline — the slice is
never re-opened — so those debts were permanently unpaid, not "in progress".

POLICY (calibrated against placeholder-registry.md `resolve_by` convention):
  - `resolve_by = "Slice N Step 3d"`  → debt OWNED by an in-pipeline slice.
       If slice N is TERMINAL (handoff final_state ∈ TERMINAL_STATES) and the
       ref is still unresolved → GAP (its scheduled owner has finished; nobody
       will pay it). ESCALATED / ROLLED_BACK count as terminal, not just PASS.
  - `resolve_by = "集成期 …"` / non-slice / empty → integration-phase / external
       trigger (D-007 SDK 入仓 / D-008 凭据注入 / R-005 后端上线). Legitimately
       survives the pipeline → EXTERNAL.
"""
from __future__ import annotations
import re
from pathlib import Path
from typing import Optional

# A slice in any of these states will NOT be re-opened by the pipeline, so an
# unresolved debt it owns is permanently unpaid (not "still in progress").
TERMINAL_STATES = ("PASS", "ESCALATED", "ROLLED_BACK")

# resolve_by names an in-pipeline slice, e.g. "Slice 4 Step 3d". The leading 0*
# tolerates "Slice 04". Anything without this shape (e.g. "集成期 D-008") is read
# as an external / integration-phase trigger.
_SLICE_IN_RESOLVE_BY = re.compile(r"Slice\s+0*(\d+)", re.IGNORECASE)

# handoff final_state, both frontmatter (`- final_state: ESCALATED`) and the
# loops yaml form (`final_state: ESCALATED`).
_FINAL_STATE = re.compile(r"final_state\s*[:=]\s*([A-Za-z_]+)", re.IGNORECASE)
_HANDOFF_FNAME = re.compile(r"^slice_0*(\d+)_(?:brief|handoff)\.md$")

# Stage-summary (brief) 落点：新路径优先，旧 handoffs 路径兜底（升级期兼容）
_SUMMARY_DIRS = (
    ("spec", "execution", "briefs"),
    ("spec", "baseline", "plans", "handoffs"),
)


def iter_slice_summary_paths(project_root: Path):
    """Yield slice_NN_brief.md / slice_NN_handoff.md across new + legacy dirs."""
    for parts in _SUMMARY_DIRS:
        d = project_root.joinpath(*parts)
        if not d.exists():
            continue
        for pattern in ("slice_*_brief.md", "slice_*_handoff.md"):
            yield from sorted(d.glob(pattern))


_SLICE_SECTION_HDR = re.compile(r"^##\s+Slice\s+0*(\d+)\b", re.MULTILINE)


def iter_slice_brief_sections(project_root: Path):
    """Yield (slice_num, section_text, source_path, line_offset).

    P2-1 group-file form: `spec/execution/briefs/group_NN_brief.md` holds one
    `## Slice N (F-xxx)` section per slice — the header block before the first
    section is group-shared (build/loops) and is never yielded, so its
    `final_state:` lines cannot be misattributed to a slice. Legacy per-slice
    files (slice_NN_brief.md / _handoff.md) yield as whole-file sections
    (offset 0) — dual-path fallback, both forms may coexist mid-migration.
    """
    for parts in _SUMMARY_DIRS:
        d = project_root.joinpath(*parts)
        if not d.exists():
            continue
        for p in sorted(d.glob("group_*_brief.md")):
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            heads = list(_SLICE_SECTION_HDR.finditer(text))
            for i, m in enumerate(heads):
                end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
                yield (int(m.group(1)), text[m.start():end], p,
                       text[:m.start()].count("\n"))
    for p in iter_slice_summary_paths(project_root):
        fm = _HANDOFF_FNAME.match(p.name)
        if not fm:
            continue
        try:
            yield int(fm.group(1)), p.read_text(encoding="utf-8", errors="replace"), p, 0
        except Exception:
            continue


def parse_owning_slice(resolve_by: str) -> Optional[int]:
    """Extract the owning Slice number from a `resolve_by` field. None if it does
    not name a slice — i.e. it is an integration-phase / external trigger.

    The `resolve_by` field is authoritative (not the P-ID prefix): group-closers
    *correct* resolve_by during their step 1d (e.g. P-S4-MIN-005's P-ID says
    slice 4 but resolve_by was re-pointed to "Slice 9"; P-S4-AGC-001's P-ID says
    slice 4 but resolve_by is "集成期 D-008" → external). Reading the P-ID prefix
    instead would misclassify these.
    """
    if not resolve_by:
        return None
    m = _SLICE_IN_RESOLVE_BY.search(resolve_by)
    return int(m.group(1)) if m else None


def is_external_deferral(resolve_by: str) -> bool:
    """True iff resolve_by does NOT name an in-pipeline slice — an integration-
    phase / external trigger that legitimately survives the pipeline."""
    return parse_owning_slice(resolve_by) is None


def load_terminal_slices(project_root: Path) -> dict[int, str]:
    """Scan slice stage-summaries（`spec/execution/briefs/slice_NN_brief.md`，
    旧 `spec/baseline/plans/handoffs/slice_NN_handoff.md` 兜底）; return
    {slice_num: final_state} for every slice whose brief declares a terminal
    final_state (PASS / ESCALATED / ROLLED_BACK).

    Empty dict on missing dir / parse failure (graceful degradation — the caller
    falls back to registry-only reasoning).
    """
    out: dict[int, str] = {}
    for num, text, _p, _off in iter_slice_brief_sections(project_root):
        sm = _FINAL_STATE.search(text)
        if not sm:
            continue
        state = sm.group(1).upper()
        if state in TERMINAL_STATES:
            out[num] = state
    return out


def classify_unresolved_fwd_ref(
    p_id: str,
    entry: dict,
    terminal_slices: dict[int, str],
) -> dict:
    """Classify ONE unresolved forward-ref registry entry.

    Returns a finding dict:
      verdict  ∈ {GAP, EXTERNAL, PENDING}
      severity ∈ {FAIL, PASS, WARN}
    GAP/FAIL is the high-precision signal: owning slice is terminal yet the debt
    is unpaid. EXTERNAL/PASS is a documented integration-phase deferral. PENDING/
    WARN is "slice named but not terminal yet" (should not occur at pipeline end;
    kept non-blocking so the gate is safe to run mid-pipeline too).
    """
    resolve_by = (entry.get("resolve_by") or "").strip()
    status = (entry.get("status") or "").strip()
    location = (entry.get("location") or "").strip()
    trigger = (entry.get("trigger_condition") or "").strip()
    owning = parse_owning_slice(resolve_by)

    base = {
        "p_id": p_id,
        "location": location,
        "resolve_by": resolve_by,
        "status": status,
        "trigger_condition": trigger[:240],
        "owning_slice": owning,
    }

    if owning is None:
        base.update({
            "verdict": "EXTERNAL",
            "severity": "PASS",
            "slice_state": None,
            "reason": (
                f"resolve_by={resolve_by!r} is an integration-phase / external trigger "
                f"(not an in-pipeline slice) → legitimately survives the pipeline "
                f"(D-007 SDK / D-008 凭据 / R-005 后端)."
            ),
        })
        return base

    state = terminal_slices.get(owning)
    if state is not None:
        base.update({
            "verdict": "GAP",
            "severity": "FAIL",
            "slice_state": state,
            "reason": (
                f"owning Slice {owning} is TERMINAL (final_state={state}) but forward-ref "
                f"{p_id} is still status={status!r} — its scheduled owner has finished and "
                f"will not re-open, so this in-app wiring debt is permanently unpaid. "
                f"Either implement the wiring + set registry status→resolved, or, if the "
                f"dependency (e.g. a ViewModel) was never created, schedule a slice/anchor "
                f"to build it (see a2h-plan anchor-coverage gate)."
            ),
        })
        return base

    base.update({
        "verdict": "PENDING",
        "severity": "WARN",
        "slice_state": None,
        "reason": (
            f"resolve_by names Slice {owning} which has no terminal handoff yet — legitimately "
            f"pending if the pipeline is still running; at pipeline end this means the slice "
            f"never ran (phantom owner) and should be investigated."
        ),
    })
    return base
