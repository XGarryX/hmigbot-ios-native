"""Skeleton classifier: scan files, produce SkeletonFinding list, mark
legitimacy via RegistryResolver and adjacent FWD-REF / PLACEHOLDER markers.
"""
from __future__ import annotations
from pathlib import Path
from typing import Iterable, Optional

from .patterns import (
    SKELETON_PATTERNS,
    EMPTY_BUILDER_HEURISTIC,
    ESCAPE_HATCH_PHRASES,
    FWD_REF_MARKER,
    PLACEHOLDER_MARKER,
    RESOURCE_PENDING_PATTERNS,
)
from .taxonomy import (
    Level,
    Scope,
    Severity,
    SkeletonFinding,
    level_of,
    severity,
)
from .registry_resolver import RegistryResolver
from .deferral_policy import load_terminal_slices


# ─── How many adjacent lines count as "next to" a legitimacy marker ──────────
ADJACENT_LINES = 3


def _read_text(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def _find_adjacent_marker(
    lines: list[str],
    target_line_idx: int,
    marker_re,
) -> Optional[dict]:
    """Search ADJACENT_LINES above and below for a marker match. Return regex
    groupdict on hit, else None.
    """
    lo = max(0, target_line_idx - ADJACENT_LINES)
    hi = min(len(lines), target_line_idx + ADJACENT_LINES + 1)
    for i in range(lo, hi):
        m = marker_re.search(lines[i])
        if m:
            return m.groupdict()
    return None


def _classify_finding(
    finding: SkeletonFinding,
    lines: list[str],
    line_idx: int,
    resolver: RegistryResolver,
    scope: Scope,
) -> SkeletonFinding:
    """Determine legitimacy + severity for a raw finding."""
    # 1. Check for adjacent FWD-REF marker
    fwd_groups = _find_adjacent_marker(lines, line_idx, FWD_REF_MARKER)
    if fwd_groups:
        p_id = fwd_groups["p_id"]
        finding.p_id = p_id
        finding.resolve_by = f"Slice {fwd_groups['slice']} Step {fwd_groups['step']}"
        if resolver.is_fwd_ref_known(p_id):
            finding.legitimate = True
            finding.legitimacy_evidence = f"adjacent FWD-REF marker {p_id} registered"
            finding.level = Level.L1
            finding.subtype = "forward-ref"
            finding.severity_at_scope = Severity.PASS
            return finding
        else:
            # marker present but not in registry → unregistered FWD-REF (still illegitimate)
            finding.legitimacy_evidence = (
                f"FWD-REF marker {p_id} present but NOT in placeholder-registry.md"
            )

    # 2. Check for adjacent PLACEHOLDER marker (thirdparty-sdk)
    ph_groups = _find_adjacent_marker(lines, line_idx, PLACEHOLDER_MARKER)
    if ph_groups:
        p_id = ph_groups["p_id"]
        finding.p_id = p_id
        if resolver.is_sdk_placeholder_registered(p_id):
            finding.legitimate = True
            finding.legitimacy_evidence = f"adjacent PLACEHOLDER marker {p_id} registered as thirdparty-sdk"
            finding.level = Level.L1
            finding.subtype = "thirdparty-sdk"
            finding.severity_at_scope = Severity.PASS
            return finding

    # 3. registry location reverse-lookup（for TODO/console.info etc. that auto-register
    #    to registry without adjacent marker — e.g. component-builder L3 auto-registration,
    #    dt-verifier // TODO[text-lookup-failed], converter Phase 4 自由 TODO）
    if hasattr(resolver, "get_entry_by_location"):
        # Try file:line first, then file path alone
        location_with_line = f"{finding.file}:{finding.line}"
        entry = resolver.get_entry_by_location(location_with_line)
        if entry is None:
            entry = resolver.get_entry_by_location(finding.file)
        if entry and entry.get("status") not in ("resolved",):
            kind = entry.get("kind", "unknown")
            # Only allow legitimate-TODO kinds to take the location-lookup shortcut
            if kind in {
                "forward-ref",
                "forward-ref-uncertain",
                "resource-pending-translation",
                "resource-pending-asset",
                "thirdparty-sdk",
            }:
                finding.p_id = entry.get("p_id")
                finding.legitimate = True
                finding.legitimacy_evidence = (
                    f"registry location-lookup hit P-ID {entry.get('p_id')} kind={kind}"
                )
                finding.level = Level.L1
                finding.subtype = kind
                finding.severity_at_scope = Severity.PASS
                return finding

    # 4. Compute severity at scope
    finding.severity_at_scope = severity(finding.level, finding.subtype, scope)
    return finding


def scan_ets_files(
    files: Iterable[Path],
    resolver: RegistryResolver,
    scope: Scope,
    project_root: Path,
) -> list[SkeletonFinding]:
    """Scan a set of .ets files; return all skeleton findings (post-classification)."""
    out: list[SkeletonFinding] = []
    for f in files:
        if not f.exists() or f.suffix != ".ets":
            continue
        text = _read_text(f)
        if not text:
            continue
        lines = text.splitlines()
        rel_path = str(f.relative_to(project_root)) if project_root in f.parents or f.is_relative_to(project_root) else str(f)

        # Iterate patterns
        for subtype, regex, action, method_kind in SKELETON_PATTERNS:
            for m in regex.finditer(text):
                # find line number
                line_idx = text.count("\n", 0, m.start())
                line_no = line_idx + 1
                excerpt = lines[line_idx].strip() if line_idx < len(lines) else m.group(0)

                # method_name attempt: extract from match if pattern captured one
                method_name = None
                if subtype == "empty-body" and method_kind == "builder":
                    name_m = _BUILDER_NAME.search(m.group(0))
                    if name_m:
                        method_name = name_m.group(1)

                level = level_of(subtype)
                finding = SkeletonFinding(
                    level=level,
                    subtype=subtype,
                    file=rel_path,
                    line=line_no,
                    match=excerpt[:200],
                    suggested_action=action,
                    method_kind=method_kind,
                    method_name=method_name,
                )
                finding = _classify_finding(finding, lines, line_idx, resolver, scope)
                out.append(finding)

        # Empty-builder heuristic (separate; produces L2 with method_kind=builder-with-placeholder)
        for m in EMPTY_BUILDER_HEURISTIC.finditer(text):
            line_idx = text.count("\n", 0, m.start())
            line_no = line_idx + 1
            excerpt = lines[line_idx].strip() if line_idx < len(lines) else m.group(0)
            finding = SkeletonFinding(
                level=Level.L2,
                subtype="empty-body",
                file=rel_path,
                line=line_no,
                match=excerpt[:200],
                suggested_action=(
                    "@Builder body wraps prose placeholder. Replace with real call "
                    "(e.g. from a wires embed entry) or add // FWD-REF marker."
                ),
                method_kind="builder-with-placeholder",
                method_name=m.group(1),
            )
            finding = _classify_finding(finding, lines, line_idx, resolver, scope)
            out.append(finding)

    return out


def scan_resource_jsons(
    files: Iterable[Path],
    resolver: RegistryResolver,
    scope: Scope,
    project_root: Path,
) -> list[SkeletonFinding]:
    """Scan resource JSON files (resources/<locale>/element/*.json)
    for L5 resource-pending findings.

    For each `"value": "[TODO: translate] ..."` match, check whether registry has
    an entry with kind=resource-pending-translation and matching location
    `<json-path>:<key-name>`. If yes → legitimate (L1). If no → L5 FAIL.
    """
    out: list[SkeletonFinding] = []
    # Cheap pre-compiled key extractor: tries to find `"name": "<key>"` on the same
    # JSON line or the line above, so we can derive registry `location` format
    # `<path>:<key>` to look up.
    import re as _re_local
    KEY_RE = _re_local.compile(r'"name"\s*:\s*"([^"]+)"')

    for f in files:
        if not f.exists() or f.suffix != ".json":
            continue
        # Only scan files under resources/<locale>/element/
        parts = f.parts
        if "resources" not in parts or "element" not in parts:
            continue
        text = _read_text(f)
        if not text:
            continue
        lines = text.splitlines()
        try:
            rel_path = str(f.relative_to(project_root))
        except ValueError:
            rel_path = str(f)

        for subtype, regex, action in RESOURCE_PENDING_PATTERNS:
            for m in regex.finditer(text):
                line_idx = text.count("\n", 0, m.start())
                line_no = line_idx + 1
                excerpt = lines[line_idx].strip() if line_idx < len(lines) else m.group(0)

                # Find key name: same line or up to 3 lines above
                key_name = None
                for back in range(0, 4):
                    probe = line_idx - back
                    if probe < 0:
                        break
                    key_m = KEY_RE.search(lines[probe])
                    if key_m:
                        key_name = key_m.group(1)
                        break

                # Registry lookup: location format `<rel_path>:<key_name>`
                location_lookup = f"{rel_path}:{key_name}" if key_name else rel_path
                entry = resolver.get_entry_by_location(location_lookup) if hasattr(resolver, "get_entry_by_location") else None

                if entry and entry.get("kind") in {"resource-pending-translation", "resource-pending-asset"}:
                    # Legitimate L1
                    finding = SkeletonFinding(
                        level=Level.L1,
                        subtype=entry.get("kind"),
                        file=rel_path,
                        line=line_no,
                        match=excerpt[:200],
                        suggested_action=f"Registered resource-pending placeholder ({entry.get('kind')}); "
                                        f"trigger: {entry.get('trigger_condition','?')}.",
                        p_id=entry.get("p_id"),
                        legitimate=True,
                        legitimacy_evidence=f"registry entry {entry.get('p_id')} kind={entry.get('kind')}",
                    )
                    finding.severity_at_scope = Severity.PASS
                else:
                    # L5 FAIL: unregistered resource placeholder
                    finding = SkeletonFinding(
                        level=Level.L5,
                        subtype=subtype,
                        file=rel_path,
                        line=line_no,
                        match=excerpt[:200],
                        suggested_action=action + (
                            f" Expected registry location format: `{location_lookup}`."
                            if key_name else ""
                        ),
                    )
                    finding.severity_at_scope = Severity.FAIL
                out.append(finding)

    return out


def scan_handoff_files(files: Iterable[Path]) -> list[dict]:
    """Scan handoff prose for escape-hatch phrases. Returns list of dicts
    {file, line, phrase} (not SkeletonFinding — different domain).
    """
    out: list[dict] = []
    for f in files:
        if not f.exists():
            continue
        text = _read_text(f)
        if not text:
            continue
        for i, line in enumerate(text.splitlines(), start=1):
            for phrase in ESCAPE_HATCH_PHRASES:
                if phrase in line:
                    out.append({
                        "file": str(f),
                        "line": i,
                        "phrase": phrase,
                        "excerpt": line.strip()[:200],
                    })
    return out


def scan_dangling_fwd_refs(
    files: Iterable[Path],
    resolver: RegistryResolver,
    project_root: Path,
    scope: Scope = "all",
) -> list[SkeletonFinding]:
    """L4 detection: surface `// FWD-REF:` markers that should have been removed.

    Three classes (all → L4.dangling-fwd-ref, all FAIL):
      1. **unregistered**: marker exists but P-ID not in placeholder-registry.md
      2. **registry-resolved**: marker exists, registry status=resolved
      3. **slice-terminal (stale)**: marker exists, registry status≠resolved,
         BUT the resolve_by Slice's handoff has a TERMINAL final_state
         (PASS / ESCALATED / ROLLED_BACK) → the owning slice has finished and
         will not be re-opened, so the unpaid debt is stale and must be removed
         or implemented. (Previously this only fired for PASS, which amnestied
         every unresolved marker owned by an ESCALATED slice — see
         deferral_policy.py for the AIPPT root-cause.)

    NOTE: only `// FWD-REF: P-… resolve_by=Slice N Step 3x` markers match
    FWD_REF_MARKER; integration-phase markers (`resolve_by=集成期 …`, e.g. AGC /
    backend / SDK留桩) do NOT match the regex and are therefore never scanned
    here — so Class 3 broadening to terminal slices cannot false-positive on
    legitimate external deferrals.
    """
    terminal_slices = load_terminal_slices(project_root)
    out: list[SkeletonFinding] = []
    for f in files:
        if not f.exists() or f.suffix != ".ets":
            continue
        text = _read_text(f)
        if not text:
            continue
        lines = text.splitlines()
        try:
            rel_path = str(f.relative_to(project_root))
        except ValueError:
            rel_path = str(f)

        for m in FWD_REF_MARKER.finditer(text):
            line_idx = text.count("\n", 0, m.start())
            line_no = line_idx + 1
            excerpt = lines[line_idx].strip() if line_idx < len(lines) else m.group(0)
            p_id = m.group("p_id")
            slice_n = m.group("slice")
            step = m.group("step")

            entry = resolver.get_entry(p_id)
            slice_n_int = int(slice_n)

            if entry is None:
                # Class 1: unregistered
                finding = SkeletonFinding(
                    level=Level.L4,
                    subtype="dangling-fwd-ref",
                    file=rel_path,
                    line=line_no,
                    match=excerpt[:200],
                    suggested_action=(
                        f"FWD-REF P-ID `{p_id}` is NOT in placeholder-registry.md. "
                        f"Either register it (kind=forward-ref + resolve_by=Slice {slice_n} Step {step}) "
                        f"or remove the marker if implementation is now in place."
                    ),
                    p_id=p_id,
                    resolve_by=f"Slice {slice_n} Step {step}",
                )
                finding.severity_at_scope = Severity.FAIL
                out.append(finding)
            elif entry.get("status") == "resolved":
                # Class 2: registry says resolved
                finding = SkeletonFinding(
                    level=Level.L4,
                    subtype="dangling-fwd-ref",
                    file=rel_path,
                    line=line_no,
                    match=excerpt[:200],
                    suggested_action=(
                        f"placeholder-registry.md marks `{p_id}` as `resolved` but the "
                        f"`// FWD-REF:` marker is still present at {rel_path}:{line_no}. "
                        f"Remove the marker (the wiring is complete according to registry)."
                    ),
                    p_id=p_id,
                    resolve_by=f"Slice {slice_n} Step {step}",
                )
                finding.severity_at_scope = Severity.FAIL
                out.append(finding)
            elif slice_n_int in terminal_slices:
                # Class 3: stale — owning slice TERMINAL (PASS/ESCALATED/ROLLED_BACK)
                # but the debt is still unpaid. ESCALATED is terminal: the slice is
                # never re-opened, so a lingering marker is a real gap, not "pending".
                slice_state = terminal_slices[slice_n_int]
                finding = SkeletonFinding(
                    level=Level.L4,
                    subtype="dangling-fwd-ref",
                    file=rel_path,
                    line=line_no,
                    match=excerpt[:200],
                    suggested_action=(
                        f"STALE marker: `{p_id}` registry status={entry.get('status','?')}, "
                        f"but Slice {slice_n} handoff is already final_state={slice_state} (terminal). "
                        f"The owning Slice has finished and will not be re-opened. Either implement "
                        f"the wiring AND set registry status → resolved + remove this marker, or, if "
                        f"the dependency (e.g. a ViewModel) was never created, schedule a slice/anchor "
                        f"to build it (a2h-plan anchor-coverage gate) — do NOT leave it amnestied."
                    ),
                    p_id=p_id,
                    resolve_by=f"Slice {slice_n} Step {step}",
                )
                finding.severity_at_scope = Severity.FAIL
                out.append(finding)
            # else: owning slice has no terminal handoff yet → genuinely in progress,
            #       marker legitimate (loop will re-check once the slice finalizes).
    return out


# ─── helpers ──────────────────────────────────────────────────────────────────
import re as _re
_BUILDER_NAME = _re.compile(r"@Builder\s+(\w+)\s*\(")
