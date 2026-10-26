"""Stage 1 entry: path normalization is applied in stage0; this module builds android_facts IR."""

from __future__ import annotations

# Re-export builder for pipeline clarity
from stages.build_android_facts import build_android_facts

__all__ = ["build_android_facts"]
