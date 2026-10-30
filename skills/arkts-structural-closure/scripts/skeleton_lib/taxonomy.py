"""Skeleton taxonomy: subtypes across 5 levels + severity rules.

Levels:
  L1 legitimate     — forward-ref / thirdparty-sdk / intentional-default /
                      resource-pending-translation / resource-pending-asset /
                      forward-ref-uncertain
  L2 probable       — empty-body (regex/AST detected; method_kind metadata)
  L3 definite       — fake-content / naked-TODO / throw-stub
  L4 architectural  — orphan-vm / dangling-fwd-ref / dead-route
  L5 resource       — resource-pending (unregistered [TODO: translate] / fallback marker)

Severity rule (hard-coded, no YAML):
  L1               → PASS always (legitimate placeholder, registry-backed)
  L2 + scope=slice → FAIL ; other scopes → WARN
  L3               → FAIL always
  L4               → FAIL always (dead-route → WARN only)
  L5               → FAIL always (resource layer unregistered placeholder)
"""
from __future__ import annotations
from dataclasses import dataclass, asdict, field
from enum import Enum
from typing import Optional, Literal


class Level(str, Enum):
    L1 = "L1"  # legitimate
    L2 = "L2"  # probable skeleton
    L3 = "L3"  # definite skeleton
    L4 = "L4"  # architectural skeleton
    L5 = "L5"  # resource-layer skeleton


class Severity(str, Enum):
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"


Scope = Literal["stage", "slice", "all"]


# Subtype catalogue. Keep these strings stable across phases — they get
# logged into handoffs and consumed by retrospect statistics.
SUBTYPES_L1 = {
    "forward-ref",
    "thirdparty-sdk",
    "intentional-default",
    # Registry-backed legitimate placeholders:
    "resource-pending-translation",
    "resource-pending-asset",
    "forward-ref-uncertain",
}
SUBTYPES_L2 = {"empty-body"}
SUBTYPES_L3 = {"fake-content", "naked-TODO", "throw-stub"}
SUBTYPES_L4 = {"orphan-vm", "dangling-fwd-ref", "dead-route",
               # toolchain guard: registry file has P-ID rows but parser loaded 0
               # (emitted by audit_skeletons instead of N dangling false positives)
               "registry-parse-degraded"}
SUBTYPES_L5 = {
    "resource-pending-unregistered",   # resource value has [TODO: translate] etc. but no registry entry
    "resource-fallback-unregistered",  # fallback asset used without registry P-RES-ASSET-*
}

ALL_SUBTYPES = SUBTYPES_L1 | SUBTYPES_L2 | SUBTYPES_L3 | SUBTYPES_L4 | SUBTYPES_L5


def level_of(subtype: str) -> Level:
    if subtype in SUBTYPES_L1:
        return Level.L1
    if subtype in SUBTYPES_L2:
        return Level.L2
    if subtype in SUBTYPES_L3:
        return Level.L3
    if subtype in SUBTYPES_L4:
        return Level.L4
    if subtype in SUBTYPES_L5:
        return Level.L5
    raise ValueError(f"unknown skeleton subtype: {subtype}")


def is_fail(level: Level, subtype: str, scope: Scope) -> bool:
    """Return True if this finding is FAIL-level under the given scope.
    Non-FAIL findings are WARN (recorded but not blocking).
    """
    if level == Level.L1:
        return False
    if level == Level.L4 and subtype == "dead-route":
        return False  # WARN only
    if level == Level.L2:
        return scope == "slice"
    # L3 + L4 (non-dead-route) + L5 always fail
    return True


def severity(level: Level, subtype: str, scope: Scope) -> Severity:
    if level == Level.L1:
        return Severity.PASS
    return Severity.FAIL if is_fail(level, subtype, scope) else Severity.WARN


@dataclass
class SkeletonFinding:
    """A single skeleton occurrence.

    `level` and `subtype` come from the patterns table; `legitimate` is computed
    by RegistryResolver after the initial regex match.
    """
    level: Level
    subtype: str
    file: str                              # repo-relative path
    line: int
    match: str                             # excerpt of the offending source
    suggested_action: str
    method_kind: Optional[str] = None      # for L2 empty-body: builder/lifecycle/handler/etc
    method_name: Optional[str] = None
    p_id: Optional[str] = None             # parsed from FWD-REF / PLACEHOLDER if present
    resolve_by: Optional[str] = None       # parsed from FWD-REF
    legitimate: bool = False               # True → finding is L1 (registry-backed)
    legitimacy_evidence: Optional[str] = None  # e.g. "registry P-S2-FWD-001 kind=forward-ref"
    severity_at_scope: Severity = Severity.WARN

    def to_dict(self) -> dict:
        d = asdict(self)
        d["level"] = self.level.value
        d["severity_at_scope"] = self.severity_at_scope.value
        return d
