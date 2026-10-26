"""Ownership-based applicability for page-only receipt evidence."""
import re


def delegates_page_safearea(task):
    """Only split domain cores with strictly non-page ownership may use []."""
    own = task.get("ownership") or []
    return (task.get("schema") == "domainImpl"
            and bool(re.fullmatch(r"impl:(?:r\d+:)?[^:]+", task.get("id", "")))
            and bool(own)
            and all(isinstance(p, str) and p.startswith((
                "entry/src/main/ets/features/", "entry/src/main/ets/components/"
            )) for p in own))
