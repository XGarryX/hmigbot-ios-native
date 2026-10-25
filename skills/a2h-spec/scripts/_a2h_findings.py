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
        -> section `halted`: a LOOP.NOT_CONVERGING blocking finding is injected,
           `section_exit_code` returns 3 (distinct from 2 = converging), and the
           only way forward is a human decision recorded via `clear_halt`.

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


def make(
    rule: str,
    owner_stage: str,
    subject: str,
    detail: str,
    *,
    severity: str = "blocking",
    subject_ref: str | None = None,
    fix_hint: str | None = None,
    options: list[str] | None = None,
) -> dict[str, Any]:
    """Build one finding. `owner_stage` is the stage that must act on it."""
    if owner_stage not in STAGES:
        raise ValueError(f"unknown owner_stage: {owner_stage}")
    if severity not in SEVERITIES:
        raise ValueError(f"unknown severity: {severity}")
    return {
        "finding_key": finding_key(rule, subject),
        "rule": rule,
        "owner_stage": owner_stage,
        "severity": severity,
        "subject": subject,
        "subject_ref": subject_ref,
        "detail": detail,
        "fix_hint": fix_hint,
        # options is non-null only for findings whose owner cannot be determined
        # mechanically; the stage renders them as a decision card.
        "options": options,
        "occurrences": 1,
        "escalate": False,
        "decision_ref": None,
    }


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
                            fix_hint="delete the file and re-run the stage linters",
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
        if item.get("severity") == "blocking" and item.get("finding_key")
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
    for item in findings:
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

    if blocking_count == 0:
        # clean section: the loop converged; all brakes release automatically
        no_progress, halted = 0, False
    elif after_repair and "blocking_count" in prior_progress:
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
            f"连续 {no_progress} 轮修复未使阻断集合缩小（累计 {repair_rounds} 轮）。"
            f"继续叠补丁只会增加实现路径——按决策卡裁决后用 --clear-halt <决策ID> 解除。",
            fix_hint="出决策卡：换实现路径 / 判为平台差异走 HARD-DIV / 记 deferred 并写关闭条件 / 中止转人工",
            options=[
                "换实现路径（说明拟采用的新路径）",
                "判定为平台差异，走 HARD-DIV 决策改写要求",
                "记为 deferred，写明关闭条件",
                "中止该范围，转人工处理",
            ],
        )
        stall["occurrences"] = no_progress
        stall["escalate"] = True
        carried = [stall] + carried

    data["sections"][section] = {
        "context": context or {},
        "progress": {
            "blocking_digest": digest,
            "blocking_count": blocking_count,
            "repair_rounds": repair_rounds,
            "no_progress_rounds": no_progress,
            "halted": halted,
            "decision_ref": decision_ref,
        },
        "findings": sorted(carried, key=lambda f: (f["severity"], f["rule"], f["subject"])),
    }
    path = path_for(project_root)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    return data


def clear_halt(project_root: str, section: str, decision_ref: str) -> None:
    """Release a halted section. Only a recorded human decision may do this —
    the mirror image of 'only the linter closes a finding'."""
    if not decision_ref:
        raise ValueError("clear_halt requires a decision id (e.g. D-021 / B-007)")
    data = load(project_root)
    body = data["sections"].get(section)
    if not body:
        return
    progress = body.get("progress", {})
    progress.update(
        {"halted": False, "no_progress_rounds": 0, "repair_rounds": 0, "decision_ref": decision_ref}
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
    """3 = halted (stop repairing, decide); 2 = blocking but converging; 0 = clean."""
    data = load(project_root)
    progress = data["sections"].get(section, {}).get("progress", {})
    if progress.get("halted") and any(f.get("severity") == "blocking" for f in findings):
        return 3
    return exit_code(findings)


def for_stage(project_root: str, stage: str) -> list[dict[str, Any]]:
    """Every open finding addressed to `stage`, across all sections."""
    data = load(project_root)
    out = []
    for section in data.get("sections", {}).values():
        for item in section.get("findings", []):
            if isinstance(item, dict) and item.get("owner_stage") == stage:
                out.append(item)
    return sorted(out, key=lambda f: (f["severity"], f["rule"], f["subject"]))


def upstream_of(project_root: str, stage: str) -> list[dict[str, Any]]:
    """Blocking findings owned by a stage earlier in the pipeline than `stage`.

    A stage must refuse to start while these exist — that is the whole
    back-routing mechanism.
    """
    order = {name: index for index, name in enumerate(STAGES)}
    here = order[stage]
    data = load(project_root)
    out = []
    for section in data.get("sections", {}).values():
        for item in section.get("findings", []):
            if not isinstance(item, dict):
                continue
            owner = item.get("owner_stage")
            if owner in order and order[owner] < here and item.get("severity") == "blocking":
                out.append(item)
    return sorted(out, key=lambda f: (f["owner_stage"], f["rule"], f["subject"]))


def render(findings: list[dict[str, Any]], title: str) -> str:
    """Human-readable block for gate summaries and linter stdout."""
    if not findings:
        return f"{title}: 无\n"
    lines = [f"{title}: {len(findings)} 条"]
    for item in findings:
        mark = "🔴" if item["severity"] == "blocking" else "🟡"
        lines.append(f"  {mark} [{item['rule']}] {item['subject']}")
        lines.append(f"       {item['detail']}")
        if item.get("subject_ref"):
            lines.append(f"       位置: {item['subject_ref']}")
        if item.get("fix_hint"):
            lines.append(f"       建议: {item['fix_hint']}")
        if item.get("escalate"):
            lines.append(
                f"       ⚠ 已连续出现 {item['occurrences']} 轮 —— 停止补丁式修复，"
                f"改用决策卡在 修复 / 记为例外 / 撤回该要求 之间选择"
            )
    return "\n".join(lines) + "\n"


def exit_code(findings: list[dict[str, Any]]) -> int:
    """2 when anything blocking is open, else 0. Warnings gate at the human Gate."""
    return 2 if any(item["severity"] == "blocking" for item in findings) else 0
