"""plan_lib — Parsers for feature-plan.md slice headers and integration_points.

Provides structured access to:
  - Slice header YAML (complexity, depends_on, android_source_anchors, ...)
  - placeholders_planned
  - integration_points (handler ← target + evidence)
  - wires (VM 实例化 + 组件@Builder嵌入)
  - cross_slice_edits
  - modifies_files
"""
from .feature_plan_parser import (
    FeaturePlan,
    SliceSpec,
    IntegrationPoint,
    WireEntry,
    CrossSliceEdit,
    ParentReplacement,
)

__all__ = [
    "FeaturePlan",
    "SliceSpec",
    "IntegrationPoint",
    "WireEntry",
    "CrossSliceEdit",
    "ParentReplacement",
]
