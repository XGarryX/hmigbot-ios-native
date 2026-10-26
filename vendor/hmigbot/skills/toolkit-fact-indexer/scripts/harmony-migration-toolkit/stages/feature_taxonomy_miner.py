from __future__ import annotations

import re
from collections import Counter
from typing import Any


_NOISE_TOKENS = {
    "activity",
    "fragment",
    "dialog",
    "bottom",
    "sheet",
    "view",
    "viewmodel",
    "model",
    "screen",
    "adapter",
    "holder",
    "item",
    "list",
    "detail",
    "details",
    "page",
    "pages",
    "layout",
    "binding",
    "manager",
    "helper",
    "handler",
    "navigator",
    "utils",
    "util",
    "factory",
    "provider",
    "repository",
    "service",
    "worker",
    "receiver",
    "controller",
    "presenter",
    "component",
    "content",
    "main",
    "base",
    "abstract",
    "impl",
    "ui",
    # build-tree / source-root path words — never a meaningful feature name
    "java",
    "kotlin",
    "src",
}

_ACTION_TOKENS = {
    "add",
    "create",
    "delete",
    "edit",
    "fetch",
    "get",
    "handle",
    "init",
    "load",
    "new",
    "open",
    "remove",
    "request",
    "save",
    "set",
    "setup",
    "show",
    "start",
    "update",
}


def _split_words(value: str) -> list[str]:
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", value or "")
    value = re.sub(r"[^A-Za-z0-9]+", " ", value)
    out: list[str] = []
    for raw in value.lower().split():
        if len(raw) < 3:
            continue
        if raw.isdigit():
            continue
        out.append(raw)
    return out


def _domain_tokens(meta: dict[str, Any]) -> list[str]:
    # Cluster on the developer-chosen semantic names only — the class name and the
    # layout id. The `package` and `source_path` fields carry the reverse-domain and
    # build-tree path (de/danoeh/antennapod, java/src/main/app …), which are pure
    # location, identical across every screen, and would otherwise dominate the token
    # counts and turn every feature label into "<X> Java Src". They are excluded.
    tokens: list[str] = []
    for key in ("class_name", "layout"):
        tokens.extend(_split_words(str(meta.get(key) or "")))
    return [t for t in tokens if t not in _NOISE_TOKENS]


def _primary_token(tokens: list[str]) -> str:
    meaningful = [t for t in tokens if t not in _ACTION_TOKENS]
    if meaningful:
        return Counter(meaningful).most_common(1)[0][0]
    if tokens:
        return Counter(tokens).most_common(1)[0][0]
    return ""


def _label_from_tokens(tokens: list[str]) -> str:
    if not tokens:
        return "Generated feature"
    words = []
    for token in tokens:
        if token not in words:
            words.append(token)
        if len(words) >= 3:
            break
    return " ".join(w.capitalize() for w in words)


def _feature_id(tokens: list[str]) -> str:
    chosen = []
    for token in tokens:
        if token not in chosen and token not in _ACTION_TOKENS:
            chosen.append(token)
        if len(chosen) >= 2:
            break
    if not chosen:
        chosen = tokens[:1] or ["misc"]
    return "generated." + ".".join(chosen)


def mine_generated_taxonomy(
    screen_hosts: dict[str, dict[str, Any]],
    nav_edges: list[dict[str, Any]],
    preassigned: dict[str, str],
) -> tuple[dict[str, str], dict[str, str], dict[str, Any]]:
    """Deterministically group screens that were not assigned by explicit taxonomy rules."""
    token_by_screen: dict[str, list[str]] = {}
    buckets: dict[str, list[str]] = {}
    for screen, meta in sorted(screen_hosts.items()):
        if screen in preassigned:
            continue
        enriched = dict(meta)
        enriched.setdefault("class_name", screen)
        tokens = _domain_tokens(enriched)
        if not tokens:
            # Deterministic last resort: a name whose every word is structural noise
            # (e.g. MainActivity → main/activity) would otherwise be stranded as
            # unmatched once location tokens are dropped. Cluster it by its own
            # class/layout words instead — still developer-chosen names, never the
            # package/path noise we deliberately excluded.
            tokens = _split_words(str(enriched.get("class_name") or "")) + _split_words(
                str(enriched.get("layout") or "")
            )
        primary = _primary_token(tokens)
        if not primary:
            continue
        token_by_screen[screen] = tokens
        buckets.setdefault(primary, []).append(screen)

    # Navigation affinity: if a screen is still alone, attach it to an adjacent bucket
    # when that bucket has a stable primary token. This remains deterministic by sorting.
    screen_bucket = {screen: bucket for bucket, screens in buckets.items() for screen in screens}
    for edge in sorted(nav_edges, key=lambda e: (str(e.get("from")), str(e.get("to")), int(e.get("line") or 0))):
        a = str(edge.get("from") or "")
        b = str(edge.get("to") or "")
        if a not in screen_bucket or b not in screen_bucket:
            continue
        ba = screen_bucket[a]
        bb = screen_bucket[b]
        if ba == bb:
            continue
        if len(buckets.get(ba, [])) == 1 and len(buckets.get(bb, [])) > 1:
            buckets[bb].append(a)
            buckets[ba].remove(a)
            screen_bucket[a] = bb
        elif len(buckets.get(bb, [])) == 1 and len(buckets.get(ba, [])) > 1:
            buckets[ba].append(b)
            buckets[bb].remove(b)
            screen_bucket[b] = ba

    screen_to_feature: dict[str, str] = {}
    screen_to_rule: dict[str, str] = {}
    generated_features: list[dict[str, Any]] = []
    used_ids: set[str] = set()

    for bucket, screens in sorted((k, sorted(set(v))) for k, v in buckets.items() if v):
        token_counter: Counter[str] = Counter()
        for screen in screens:
            token_counter.update(token_by_screen.get(screen) or [bucket])
        top_tokens = [t for t, _count in token_counter.most_common(6) if t not in _NOISE_TOKENS]
        fid = _feature_id(top_tokens or [bucket])
        if fid in used_ids:
            fid = f"{fid}.{len(used_ids) + 1}"
        used_ids.add(fid)
        label = _label_from_tokens(top_tokens or [bucket])
        for screen in screens:
            screen_to_feature[screen] = fid
            screen_to_rule[screen] = f"generated:{bucket}"
        generated_features.append(
            {
                "feature_id": fid,
                "label": label,
                "screen_count": len(screens),
                "top_tokens": top_tokens[:6],
                "representative_screens": screens[:8],
                "rule_id": f"generated:{bucket}",
            }
        )

    report = {
        "strategy": "deterministic_token_graph_clustering",
        "generated_feature_count": len(generated_features),
        "assigned_screen_count": len(screen_to_feature),
        "generated_features": generated_features,
    }
    return screen_to_feature, screen_to_rule, report
