#!/usr/bin/env python3
"""Shared open-findings queue for the a2h pipeline.

One file — `spec/.a2h/open-findings.json` — holds every open finding across the
four stages. Each linter owns exactly one *section* (keyed by its own id) and
rewrites only that section, so stages never clobber one another.

Routing is a set difference, not a registry. A linter compares two artifacts;
whichever side is missing an entry names the owner stage. A finding is closed
only when the linter that raised it re-runs and stops reporting it — never by
anyone declaring it fixed.

Loop control counts REPAIR ROUNDS, not linter runs. A run only advances the
counters when the caller passes `after_repair=True`; status checks are free.
Progress is measured on the whole blocking set of a section, not per finding —
a repair loop that keeps *mutating* its failures (fix AC01, AC02 appears; fix
AC02, AC03 appears) never repeats a finding key, so per-key counters are blind
to it. Section rules:

    strictly fewer blocking findings than last round  -> progress, counter resets
    same blocking set, or different-but-not-smaller   -> no_progress_rounds += 1
    no_progress_rounds >= HALT_LIMIT (or repair_rounds >= MAX_REPAIR_ROUNDS)
        -> only that section/repair strategy is paused; LOOP.NOT_CONVERGING is
           advisory. Actual product findings retain their own impact and scope.
           A changed strategy or resolved defects releases technical backoff;
           retry counts never create a product-approval requirement.

Per-finding `occurrences`/`escalate` stay (they answer "is THIS item stuck"),
but they too advance only on repair rounds.

This module is copied verbatim into each stage's `scripts/` directory; it has no
dependencies outside the standard library so every stage can import it locally.
"""
from __future__ import annotations

import json
import hashlib
import os
from typing import Any

FINDINGS_REL = "spec/.a2h/open-findings.json"
LOOP_LIMIT = 3          # per-finding: repair rounds before `escalate`
HALT_LIMIT = 3          # per-section: consecutive no-progress repair rounds before halt
MAX_REPAIR_ROUNDS = 10  # per-section: absolute cap even with slow progress
STAGES = ("spec", "plan", "execute", "verify")
SEVERITIES = ("blocking", "warn")


def finding_key(rule: str, subject: str) -> str:
    """Stable identity: same rule + same subject → same key across runs."""
    digest = hashlib.sha256(f"{rule}\x00{subject}".encode("utf-8")).hexdigest()
    return f"FK-{digest[:16]}"


# This fragment is inserted verbatim into the standalone stage queue copies.
_IMPACT_RULES = {
    'source_binding': set('AC_TRUTH_INVALID AC_TRUTH_MISSING INVALID_SOURCE_ANCHOR SOURCE_ANCHOR_MISSING SOURCE_INDEX_MISSING STALE_SOURCE STALE_DISPOSITION INVALID_DISPOSITION LEGACY_SOURCE_FIELD PREVIEW_REVIEW_REQUIRED'.split()),
    'product_behavior': set('AC_DUPLICATE AC_JUDGMENT_MISSING AC_MISSING DOCUMENT_DUPLICATE FEATURES_MISSING CLAIM_FACT_LINK CLAIM_SIGNAL_MISSING CLAIM_TYPED_VALUE CLAIM_UNRELATED_LINE NATIVE_DIMENSION_MISSING NATIVE_DOCUMENT_MISSING NATIVE_FACTS_FRAMEWORK NATIVE_FACTS_ID NATIVE_FACTS_KIND NATIVE_FACTS_LANGUAGE NATIVE_FACTS_MISSING NATIVE_FACTS_SCHEMA NATIVE_FACT_EVIDENCE NATIVE_FACT_REASON NATIVE_FACT_STATUS NATIVE_FACT_UNKNOWN NATIVE_FACT_VALUE NA_CONTRADICTION OBLIGATION_AC_MISSING OBLIGATION_FEATURE_MISMATCH OBLIGATION_ID OBLIGATION_UNCOVERED ORACLE_TOO_WEAK RESPONSIBILITY_INVALID RESPONSIBILITY_MAPPING SOURCE_REVIEW_MISSING SOURCE_UNACCOUNTED STATE_UNRESOLVED STATE_VALUE_CONTRADICTION OBJC_STATE_UNRESOLVED'.split()),
    'source_interpretation': set('EXTRACTION_UNRESOLVED CONDITIONAL_BUILD TOKEN_BALANCE TOKEN_IDENTIFIER_UNRESOLVED IB_PARSE RESOURCE_PARSE PROVIDER_UNRESOLVED HARNESS_CONTRACT'.split()),
    'behavior_evidence': set('BEHAVIOR_CASE_AC BEHAVIOR_CASE_ID BEHAVIOR_CHAIN_ID BEHAVIOR_CHAIN_MISSING BEHAVIOR_COMMAND BEHAVIOR_INPUT_CHANGED BEHAVIOR_NODE BEHAVIOR_OBSERVATION BEHAVIOR_REVIEW BEHAVIOR_RUNNER BEHAVIOR_SOURCE_CHANGED BEHAVIOR_TARGET_CHANGED BEHAVIOR_TARGET_STALE BEHAVIOR_TARGET_UNBOUND INDEPENDENT_ORACLE_MISSING'.split()),
}
_SPEC_PRODUCT_RULES = set('AC_DEFERRED AC_DUPLICATE AC_EXPECTED AC_MISSING ARTIFACT_PROFILE DOCUMENT_MISSING REFERENCE_INVALID TARGET_UNDEFINED TRUTH_IMPORT TRUTH_INVALID TRUTH_PREVIEW UI_TARGET_STATE UNRESOLVED ACTION_AC ACTION_APPLICABILITY ACTION_CONFLICT ACTION_DUPLICATE ACTION_HISTORY ACTION_JSON ACTION_NA_EVIDENCE ACTION_OWNER ACTION_REFERENCE ACTION_REQUIRED ACTION_SKIPPED ACTION_SKIPPED_SCOPE ACTION_SOURCE ACTION_TARGET ACTION_UNRESOLVED ARTIFACT_JSON ARTIFACT_META_EVIDENCE ARTIFACT_MISSING ARTIFACT_NA_EVIDENCE ARTIFACT_SOURCE ARTIFACT_UNRESOLVED RESPONSIBILITY_INVALID'.split())
_IMPACT_CONSEQUENCES = {
    'source_binding': 'The affected conversion/acceptance claim would be bound to absent, changed, or unrelated source evidence.',
    'product_behavior': 'The affected source behavior, state/event contract, or acceptance obligation cannot be retained by dependent implementation.',
    'source_interpretation': 'The affected source/configuration cannot be interpreted reliably for source-bound implementation; independent build diagnostics remain available.',
    'behavior_evidence': 'The affected acceptance observation cannot establish behavior for the current source/target inputs.',
    'consumer_contract': 'The affected implementation contract has missing/conflicting behavior, ownership, source evidence, or a required executable data field.',
}


def _valid_impact(impact):
    return (isinstance(impact, dict)
            and isinstance(impact.get('affected_objects'), list) and bool(impact['affected_objects'])
            and all(isinstance(v, str) and v.strip() for v in impact['affected_objects'])
            and impact.get('impact_kind') in set(_IMPACT_CONSEQUENCES) | {'build', 'resource', 'write_conflict'}
            and all(isinstance(impact.get(k), str) and impact[k].strip()
                    for k in ('consequence', 'consumer', 'recovery')))


def causal_impact(rule, owner_stage, subject, detail, *, subject_ref=None, fix_hint=None):
    kind = None
    if rule.startswith('IOS.SPEC_') and rule[9:] in _SPEC_PRODUCT_RULES:
        kind = 'consumer_contract'
    elif rule.startswith('IOS.'):
        suffix = rule[4:]
        kind = next((kind for kind, rules in _IMPACT_RULES.items() if suffix in rules), None)
    if kind is None:
        return None
    return {'affected_objects': [subject], 'impact_kind': kind,
            'consequence': detail + ' ' + _IMPACT_CONSEQUENCES[kind],
            'consumer': 'source-bound implementation and acceptance' if kind != 'behavior_evidence' else 'affected acceptance verification',
            'blocked_tasks': [], 'evidence_refs': [subject_ref or subject],
            'recovery': fix_hint or 'Repair the identified object/input and rerun its owning check; no new product approval is implied.',
            'consumer_stages': ['plan', 'execute', 'verify'] if owner_stage == 'spec' else ['execute', 'verify'] if owner_stage == 'plan' else ['verify'],
            'scope': 'source' if rule in {'IOS.STALE_SOURCE', 'IOS.SOURCE_INDEX_MISSING'} else 'affected_objects'}


def recovery_options(item, *, capabilities=None, unblocked_tasks=None):
    """Available choices are not measurements; every proposed action is not_run."""
    capabilities = capabilities or {}
    def option(ident, label, scope, limitation, next_step, recovery):
        return {'id': ident, 'label': label, 'capability_status': 'available',
                'verification_status': 'not_run', 'actual_call': None, 'result': None,
                'evidence_paths': [], 'capability_scope': scope,
                'verification_limit': limitation, 'next_step': next_step, 'recovery': recovery}
    choices = [
        option('inspect_reported_evidence', 'Inspect the reported object and evidence',
               'Read the current diagnostic and its referenced local inputs.',
               'Inspection alone does not resolve missing compiler/runtime/behavior evidence.',
               'Inspect the affected_objects/evidence_refs and the original diagnostic before selecting a repair path.',
               'Correct the identified input or collect the missing evidence, then rerun its owning check.'),
        option('report_partial_progress', 'Record accurate partial progress',
               'Render the current findings, completed checks and unresolved scope.',
               'A partial report is not a passing migration or an executed native verification.',
               'Report needs_review/blocked/not_run with the original error and the remaining recovery condition.',
               'Resume the affected check after its documented prerequisite is available.'),
    ]
    if capabilities.get('native_source_cli') is True:
        choices.append(option('collect_native_cli_evidence', 'Use the available native CLI path',
            'Read source/build configuration through the configured native CLI and compiler providers.',
            'CLI availability does not mean this action has run or that runtime behavior was verified.',
            'Run the configured CLI evidence provider for the selected source/build scope and retain its command, raw result and evidence path.',
            'If the selected compiler/context is unsupported, retain that scope as unknown and continue independent file diagnostics.'))
    if capabilities.get('xcode_mcp_read') is True:
        choices.append(option('collect_xcode_read_evidence', 'Use the available read-only Xcode MCP path',
            'Query only the permitted Xcode tools and current authorized engineering context.',
            'A successful read does not replace compiler branches, target builds or runtime observations.',
            'Invoke a discovered applicable read tool and retain its exact request, response and source/configuration binding.',
            'If the instance or folder authorization is unavailable, keep the original error and use the CLI option when available.'))
    if capabilities.get('target_sdk_build') is True:
        choices.append(option('run_independent_target_build', 'Run the configured target SDK build',
            'Execute the actual configured build and retain current logs, selected inputs and artifact hashes.',
            'Compilation does not establish source behavior equivalence or complete Spec acceptance.',
            'Run the configured target build without fabricating missing contract data, and report contract binding separately.',
            'Use the real SDK diagnostic to repair affected code/configuration; retain missing behavior evidence.'))
    if unblocked_tasks:
        choices.append({**option('continue_unaffected_tasks', 'Continue the identified unaffected tasks',
            'Only the listed tasks have no dependency on this blocker.',
            'The affected object and final acceptance remain unresolved.',
            'Continue only these already authorized task ids, preserving the affected task recovery point.',
            'Resume affected tasks after their owning check confirms the repair.'), 'task_ids': sorted(set(unblocked_tasks))})
    return choices


def effective_finding(item):
    """Read old queues without rewriting another linter's owned section."""
    value = dict(item)
    impact = value.get('impact')
    if not _valid_impact(impact):
        impact = causal_impact(value.get('rule', ''), value.get('owner_stage', 'spec'),
                               str(value.get('subject', '')), str(value.get('detail', '')),
                               subject_ref=value.get('subject_ref'), fix_hint=value.get('fix_hint'))
    if impact is not None:
        value['impact'] = impact
    if value.get('severity') == 'blocking' and not _valid_impact(impact):
        value.update(reported_severity='blocking', severity='warn', impact_status='needs_review')
    else:
        value['impact_status'] = ('established' if _valid_impact(impact) else 'advisory'
                                  if value.get('rule', '').startswith(('AUDIT.', 'REPORT.', 'LOOP.'))
                                  or value.get('rule') == 'IOS.PROVIDER_RETRY' else 'needs_review')
    value.pop('action_options', None)
    value['action_option_refs'] = ['inspect_reported_evidence', 'report_partial_progress']
    return value


def make(
    rule: str,
    owner_stage: str,
    subject: str,
    detail: str,
    *,
    severity: str | None = None,
    subject_ref: str | None = None,
    fix_hint: str | None = None,
    options: list[str] | None = None,
    impact: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a finding; hard gates require an established product/consumer impact.

    Known protections receive machine-derived impact. New rules without a causal
    contract remain visible for review rather than silently blocking all stages.
    """
    if owner_stage not in STAGES:
        raise ValueError(f"unknown owner_stage: {owner_stage}")
    if severity is not None and severity not in SEVERITIES:
        raise ValueError(f"unknown severity: {severity}")
    impact = impact if _valid_impact(impact) else causal_impact(
        rule, owner_stage, subject, detail, subject_ref=subject_ref, fix_hint=fix_hint)
    requested = severity if severity is not None else ('blocking' if _valid_impact(impact) else 'warn')
    value = {"finding_key": finding_key(rule, subject), "rule": rule,
        "owner_stage": owner_stage, "severity": requested, "subject": subject,
        "subject_ref": subject_ref, "detail": detail, "fix_hint": fix_hint,
        "options": options, "occurrences": 1, "escalate": False, "decision_ref": None}
    if impact is not None:
        value['impact'] = impact
    return effective_finding(value)


def path_for(project_root: str) -> str:
    return os.path.join(project_root, FINDINGS_REL)


def load(project_root: str) -> dict[str, Any]:
    path = path_for(project_root)
    if not os.path.isfile(path):
        return {"version": 1, "sections": {}}
    try:
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, json.JSONDecodeError):
        # A corrupt queue must not silently look empty — that would read as
        # "nothing to fix". Surface it as a tooling finding instead.
        return {
            "version": 1,
            "sections": {
                "_tooling": {
                    "findings": [
                        make(
                            "TOOLING.FINDINGS_UNREADABLE",
                            "spec",
                            FINDINGS_REL,
                            "open-findings.json exists but could not be parsed",
                            fix_hint="Preserve unreadable bytes, then rebuild linter-owned sections from current checks; do not delete review history.",
                        )
                    ]
                }
            },
        }
    data.setdefault("version", 1)
    data.setdefault("sections", {})
    return data


def _blocking_digest(items: list[dict[str, Any]]) -> tuple[str, int]:
    keys = sorted(
        item["finding_key"] for item in items
        if effective_finding(item).get("severity") == "blocking" and item.get("finding_key")
    )
    digest = hashlib.sha256("\n".join(keys).encode("utf-8")).hexdigest()[:16]
    return digest, len(keys)


def _stage_of_section(section: str) -> str:
    prefix = section.split("/", 1)[0]
    return prefix if prefix in STAGES else "spec"


def replace_section(
    project_root: str,
    section: str,
    findings: list[dict[str, Any]],
    *,
    context: dict[str, Any] | None = None,
    after_repair: bool = False,
) -> dict[str, Any]:
    """Rewrite one section; advance loop counters only when `after_repair`.

    A plain status run (after_repair=False) refreshes the finding list but
    counts nothing — re-checking must never look like a failed repair.
    """
    data = load(project_root)
    prior_section = data["sections"].get(section, {})
    prior = {
        item["finding_key"]: item
        for item in prior_section.get("findings", [])
        if isinstance(item, dict) and item.get("finding_key")
    }
    carried = []
    for raw_item in findings:
        item = effective_finding(raw_item)
        was = prior.get(item["finding_key"])
        if was:
            base = int(was.get("occurrences", 1))
            item["occurrences"] = base + 1 if after_repair else base
            item["decision_ref"] = was.get("decision_ref")
        item["escalate"] = item["occurrences"] >= LOOP_LIMIT
        carried.append(item)

    digest, blocking_count = _blocking_digest(carried)
    prior_progress = prior_section.get("progress", {}) if isinstance(prior_section.get("progress"), dict) else {}
    repair_rounds = int(prior_progress.get("repair_rounds", 0))
    no_progress = int(prior_progress.get("no_progress_rounds", 0))
    halted = bool(prior_progress.get("halted", False))
    decision_ref = prior_progress.get("decision_ref")
    current_context = prior_section.get("context", {}) if context is None else context
    strategy = current_context.get("repair_strategy", current_context.get("strategy_id"))
    prior_strategy = prior_section.get("context", {}).get("repair_strategy", prior_section.get("context", {}).get("strategy_id"))
    changed_strategy = strategy != prior_strategy
    if changed_strategy:
        # Only an actual technical-path change resets this strategy's budget.
        # Merely rotating finding keys must not enable an unbounded repair loop.
        no_progress, repair_rounds, halted = 0, 0, False

    if blocking_count == 0:
        # clean section: the loop converged; all brakes release automatically
        no_progress, repair_rounds, halted = 0, 0, False
    elif after_repair and "blocking_count" in prior_progress and not changed_strategy:
        repair_rounds += 1
        if blocking_count < int(prior_progress.get("blocking_count", 0)):
            no_progress = 0
        else:
            # same set, or mutated without shrinking — both count as stuck
            no_progress += 1
        halted = halted or no_progress >= HALT_LIMIT or repair_rounds >= MAX_REPAIR_ROUNDS

    if halted and blocking_count:
        stage = _stage_of_section(section)
        stall = make(
            "LOOP.NOT_CONVERGING", stage, section,
            f"This repair strategy made no progress for {no_progress} rounds ({repair_rounds} attempts). "
            "Pause this strategy; independent diagnostics and unrelated work may continue.",
            severity="warn",
            fix_hint="Choose a technical recovery path or repair the actual defect, then rerun its owning check. A product decision is needed only for a real scope tradeoff.",
        )
        stall["occurrences"] = no_progress
        stall["retry_paused"] = True
        stall["retry_scope"] = section
        carried = [stall] + carried

    data["sections"][section] = {
        "context": current_context,
        "progress": {
            "blocking_digest": digest,
            "blocking_count": blocking_count,
            "repair_rounds": repair_rounds,
            "no_progress_rounds": no_progress,
            "halted": halted,
            "decision_ref": decision_ref,
            "retry_scope": section,
            "recovery": "Repair current defects or select a different technical repair_strategy; unrelated tasks are not halted.",
        },
        "findings": sorted(carried, key=lambda f: (f["severity"], f["rule"], f["subject"])),
    }
    path = path_for(project_root)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    return data


def clear_halt(project_root: str, section: str, decision_ref: str | None = None, *, strategy_ref: str | None = None) -> None:
    """Resume this strategy with a technical recovery reference or existing decision.

    The queue never invents a product approval simply because retries ran out.
    Resolved findings release the brake automatically in replace_section().
    """
    recovery_ref = strategy_ref or decision_ref
    if not recovery_ref:
        raise ValueError("clear_halt requires a technical recovery reference or an existing product decision")
    data = load(project_root)
    body = data["sections"].get(section)
    if not body:
        return
    progress = body.get("progress", {})
    progress.update(
        {"halted": False, "no_progress_rounds": 0, "repair_rounds": 0, "decision_ref": decision_ref, "strategy_ref": strategy_ref}
    )
    body["progress"] = progress
    body["findings"] = [
        item for item in body.get("findings", [])
        if item.get("rule") != "LOOP.NOT_CONVERGING"
    ]
    path = path_for(project_root)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")


def section_exit_code(project_root: str, section: str, findings: list[dict[str, Any]]) -> int:
    """3 pauses this repair strategy; 2 identifies actual product blockers; 0 is no hard gate."""
    data = load(project_root)
    progress = data["sections"].get(section, {}).get("progress", {})
    if progress.get("halted") and any(effective_finding(f).get("severity") == "blocking" for f in findings):
        return 3
    return exit_code(findings)


def for_stage(project_root: str, stage: str) -> list[dict[str, Any]]:
    """Every open finding addressed to `stage`, across all sections."""
    data = load(project_root)
    out = []
    for section in data.get("sections", {}).values():
        for item in section.get("findings", []):
            if isinstance(item, dict) and item.get("owner_stage") == stage:
                out.append(effective_finding(item))
    return sorted(out, key=lambda f: (f["severity"], f["rule"], f["subject"]))


def upstream_of(project_root: str, stage: str, *, affected_objects: list[str] | None = None, task_ids: list[str] | None = None) -> list[dict[str, Any]]:
    """Blocking findings owned by a stage earlier in the pipeline than `stage`.

    Optional task/object filters restrict refusal to actual consumers. A
    stopped repair strategy or advisory does not block unrelated diagnostics.
    """
    order = {name: index for index, name in enumerate(STAGES)}
    here = order[stage]
    data = load(project_root)
    out = []
    for section in data.get("sections", {}).values():
        for item in section.get("findings", []):
            if not isinstance(item, dict):
                continue
            item = effective_finding(item)
            owner = item.get("owner_stage")
            impact = item.get("impact", {})
            if owner not in order or order[owner] >= here or item.get("severity") != "blocking":
                continue
            if impact.get('consumer_stages') and stage not in impact['consumer_stages']:
                continue
            if impact.get('scope') != 'source':
                if task_ids is not None and impact.get('blocked_tasks') and not set(task_ids).intersection(impact['blocked_tasks']):
                    continue
                if affected_objects is not None and not set(affected_objects).intersection(impact.get('affected_objects', [])):
                    continue
            out.append(item)
    return sorted(out, key=lambda f: (f["owner_stage"], f["rule"], f["subject"]))


def render(findings: list[dict[str, Any]], title: str) -> str:
    """Human-readable block for gate summaries and linter stdout."""
    if not findings:
        return f"{title}: 无\n"
    lines = [f"{title}: {len(findings)} 条"]
    for raw_item in findings:
        item = effective_finding(raw_item)
        mark = "🔴" if item["severity"] == "blocking" else "🟡"
        lines.append(f"  {mark} [{item['rule']}] {item['subject']}")
        lines.append(f"       {item['detail']}")
        if item.get("subject_ref"):
            lines.append(f"       位置: {item['subject_ref']}")
        if item.get("fix_hint"):
            lines.append(f"       建议: {item['fix_hint']}")
        if item.get("escalate"):
            lines.append(
                f"       ⚠ 已连续出现 {item['occurrences']} 轮；复核该技术路径。"
                f"真实产品取舍才需要决策，独立任务和诊断可继续。"
            )
    lines.append("  可继续路径（选项可用不等于已经执行）：")
    for choice in recovery_options({}):
        lines.append("    - " + choice['label'] + " [not_run]")
        lines.append("      范围: " + choice['capability_scope'])
        lines.append("      限制: " + choice['verification_limit'])
        lines.append("      下一步: " + choice['next_step'])
    return "\n".join(lines) + "\n"


def exit_code(findings: list[dict[str, Any]]) -> int:
    """2 for established product/consumer blockers; warnings remain visible without a product veto."""
    return 2 if any(effective_finding(item)["severity"] == "blocking" for item in findings) else 0
