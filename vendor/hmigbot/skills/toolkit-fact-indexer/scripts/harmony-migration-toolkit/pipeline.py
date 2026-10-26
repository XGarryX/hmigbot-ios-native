#!/usr/bin/env python3
"""
Deterministic Android → Harmony migration IR pipeline.

Usage:
  python pipeline.py --android-root PATH [--out DIR] [--stages 0,1,2,3,5,4,7]
  python pipeline.py --android-root PATH --facts-source PATH  # skip Stage 0 scanner (tests)
  python pipeline.py ... --stages 5,7  # refresh feature tree + agent bundle when facts exist
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from jsonschema import validators

# Allow `python pipeline.py` from toolkit root without installing as package
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Force UTF-8 on stdout/stderr so progress prints (arrows, Chinese text) survive a
# piped/redirected stream on a non-UTF-8 locale (e.g. Windows cp936) instead of
# crashing with UnicodeEncodeError.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

# Support TREE_SITTER_CACHE_DIR env var for offline machines (parser DLLs)
_cache_dir = __import__("os").environ.get("TREE_SITTER_CACHE_DIR")
if _cache_dir:
    try:
        from tree_sitter_language_pack import configure, PackConfig
        configure(PackConfig(cache_dir=_cache_dir))
    except Exception:
        pass

from stages.build_android_facts import build_android_facts
from stages.build_feature_tree import build_feature_tree
from stages.build_framework_map import build_framework_map
from stages.build_harmony_arch import build_harmony_arch
from stages.export_agent_bundle import export_agent_bundle
from stages.export_feature_tree_view import export_feature_tree_view
from stages.stage0_run_spec_tools import run_stage0
from stages.stage4_emit_scaffold import emit_scaffold_dry_run
from stages._util import toolkit_root


def _load_schema(name: str) -> dict:
    p = toolkit_root() / "schemas" / name
    return json.loads(p.read_text(encoding="utf-8"))


def _validate(instance: dict, schema_name: str) -> None:
    schema = _load_schema(schema_name)
    cls = validators.validator_for(schema)
    cls.check_schema(schema)
    validator = cls(schema, format_checker=None)
    errors = sorted(validator.iter_errors(instance), key=lambda e: e.path)
    if errors:
        msg = "\n".join(f"  {'/'.join(str(x) for x in e.path)}: {e.message}" for e in errors[:12])
        raise ValueError(f"Schema {schema_name} validation failed:\n{msg}")


def _validate_file(path: Path, schema_name: str) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    _validate(data, schema_name)
    return data


def _require_file(path: Path, stage: int, producer: str) -> bool:
    if path.is_file():
        return True
    print(f"Stage {stage} requires {path} ({producer}).", file=sys.stderr)
    return False


def _require_dir(path: Path, stage: int, producer: str) -> bool:
    if path.is_dir():
        return True
    print(f"Stage {stage} requires {path} ({producer}).", file=sys.stderr)
    return False


def _parse_stages(raw: str) -> set[int]:
    try:
        stages = {int(x.strip()) for x in raw.split(",") if x.strip()}
    except ValueError as exc:
        raise ValueError(f"--stages must be comma-separated integers, got: {raw}") from exc
    unknown = sorted(s for s in stages if s not in {0, 1, 2, 3, 4, 5, 6, 7})
    if unknown:
        raise ValueError(f"Unknown stage(s): {unknown}. Valid stages are 0,1,2,3,4,5,6,7.")
    return stages


def _build_counts_section(facts_dir: Path, framework_map_path: Path,
                          harmony_arch_path: Path, feature_tree_path: Path) -> str:
    """Render a counts summary of the produced artifacts as a markdown section.

    Reads only schema-stable count fields from the canonical artifacts, so it is
    app-agnostic (no WordPress/AntennaPod assumptions). Every read is guarded —
    a partial run (some stages skipped, some files missing) still yields the rows
    it can fill, and absent artifacts are simply omitted rather than erroring.
    Cost is a handful of small-JSON reads plus one glob; negligible next to the
    scan that produced them.
    """
    from collections import Counter

    def _load(path: Path):
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None

    def _table(title: str, rows: list[tuple[str, str]]) -> list[str]:
        if not rows:
            return []
        out = [f"### {title}\n", "| 指标 metric | 数量 count |", "|------|------|"]
        out += [f"| {k} | {v} |" for k, v in rows]
        out.append("")
        return out

    lines: list[str] = []

    # ── Stage 0: static facts ──
    s0: list[tuple[str, str]] = []
    nav = _load(facts_dir / "navigation_graph.json")
    if nav:
        nodes = nav.get("nodes", {}) or {}
        by_type = Counter(n.get("type", "?") for n in nodes.values())
        type_str = " / ".join(f"{t} {c}" for t, c in sorted(by_type.items(), key=lambda kv: -kv[1]))
        s0.append(("屏幕节点 navigation_graph.nodes", f"{len(nodes)}（{type_str}）" if type_str else str(len(nodes))))
        s0.append(("导航边 navigation_graph.edges", str(len(nav.get("edges", []) or []))))
    fr = _load(facts_dir / "fragments.json")
    if fr:
        cov = (fr.get("stats", {}) or {}).get("coverage", {}) or {}
        if cov.get("declared_fragment_count") is not None:
            s0.append(("Fragment 声明/已挂载/孤儿 declared/attached/orphan",
                       f"{cov.get('declared_fragment_count')} / "
                       f"{cov.get('attached_fragment_count')} / "
                       f"{len(cov.get('orphan_classes', []) or [])}"))
    bc = _load(facts_dir / "behavior_chains.json")
    if bc:
        s0.append(("行为链 behavior_chains", str(len(bc.get("behavior_chains", []) or []))))
    specs = list((facts_dir / "specs").glob("*_spec.json"))
    if specs:
        s0.append(("屏幕说明书 specs/*.json", str(len(specs))))
    dag = _load(facts_dir / "ui_dag.json")
    if dag and "screens" in (dag.get("aggregate_stats", {}) or {}):
        s0.append(("启动页可达屏幕 ui_dag.reachable", str(dag["aggregate_stats"]["screens"])))
    lines += _table("Stage 0 — 静态事实 `intermediate/0_android_facts/`", s0)

    # ── App model (already a counts dict) ──
    am = _load(facts_dir / "app_model" / "index.json")
    if am and isinstance(am.get("counts"), dict):
        lines += _table("App 模型 `intermediate/0_android_facts/app_model/`",
                        [(k, str(v)) for k, v in am["counts"].items()])

    # ── Later stages ──
    later: list[tuple[str, str]] = []
    fm = _load(framework_map_path)
    if fm:
        later.append(("Stage 2 framework_map.mappings", str(len(fm.get("mappings", []) or []))))
        later.append(("Stage 2 framework_map.gap_items", str(len(fm.get("gap_items", []) or []))))
    ha = _load(harmony_arch_path)
    if ha:
        later.append(("Stage 3 harmony_arch.modules", str(len(ha.get("modules", []) or []))))
        later.append(("Stage 3 harmony_arch.abilities", str(len(ha.get("abilities", []) or []))))
        later.append(("Stage 3 harmony_arch.routes", str(len(ha.get("routes", []) or []))))
    ft = _load(feature_tree_path)
    if ft:
        later.append(("Stage 5 feature_tree.nodes", str(len(ft.get("nodes", []) or []))))
        later.append(("Stage 5 feature_tree.edges", str(len(ft.get("edges", []) or []))))
    lines += _table("后续阶段 framework map / harmony arch / feature tree", later)

    if not lines:
        return ""
    return ("\n## 数量统计 (Counts)\n\n"
            "> 由 pipeline 在产物生成后从各阶段产物自动统计，随每次运行刷新；"
            "未运行的阶段或缺失的产物自动省略。\n\n" + "\n".join(lines))


def main() -> int:
    root = toolkit_root()
    parser = argparse.ArgumentParser(description="Harmony migration deterministic IR pipeline")
    parser.add_argument("--android-root", type=Path, required=True, help="Android project root")
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Output directory (default: ANDROID_ROOT/harmony_migration_out)",
    )
    parser.add_argument(
        "--spec-tools-root",
        type=Path,
        default=None,
        help="Override bundled static analyzer root (default: toolkit bundled_spec_tools/)",
    )
    parser.add_argument(
        "--stages",
        type=str,
        default="0,1,2,3,5,4,7",
        help="Comma-separated stage numbers (default 0,1,2,3,5,4,7)",
    )
    parser.add_argument(
        "--skip-spec-tools",
        action="store_true",
        help="Debug/cache mode: reuse SPEC_TOOLS_ROOT/output without re-running the bundled scanner",
    )
    parser.add_argument(
        "--facts-source",
        type=Path,
        default=None,
        help="Copy pre-built facts tree to 0_android_facts (skips bundled static analyzer run)",
    )
    parser.add_argument(
        "--taxonomy",
        type=Path,
        default=None,
        help="Optional feature taxonomy YAML for stage 5 (no bundled defaults; use with --taxonomy-overlay as needed)",
    )
    parser.add_argument(
        "--taxonomy-overlay",
        type=Path,
        action="append",
        default=[],
        help="Feature taxonomy YAML overlay for stage 5; may be repeated",
    )
    parser.add_argument(
        "--emit-scaffold-files",
        action="store_true",
        help="Stage 4 writes 4_scaffold/ files; default is dry-run text only to stdout",
    )
    args = parser.parse_args()

    android_root = args.android_root.resolve()
    out_dir = args.out.resolve() if args.out else android_root / "harmony_migration_out"
    out_dir.mkdir(parents=True, exist_ok=True)
    try:
        stages = _parse_stages(args.stages)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    intermediate_dir = out_dir / "intermediate"
    intermediate_dir.mkdir(parents=True, exist_ok=True)
    facts_dir = intermediate_dir / "0_android_facts"
    android_facts_path = intermediate_dir / "1_android_facts" / "android_facts.v1.json"
    framework_map_path = intermediate_dir / "2_framework_map" / "framework_map.v1.json"
    harmony_arch_path = intermediate_dir / "3_harmony_arch" / "harmony_arch.v1.json"
    feature_tree_path = intermediate_dir / "5_feature_tree" / "feature_tree.v1.json"
    agent_bundle_path = out_dir / "agent_bundle.v1.json"

    if 0 in stages:
        run_stage0(
            android_root,
            intermediate_dir,
            args.spec_tools_root,
            skip_spec_tools=args.skip_spec_tools,
            facts_source=args.facts_source,
        )

    if 1 in stages:
        if not _require_dir(facts_dir, 1, "run stage 0 or provide existing 0_android_facts"):
            return 1
        build_android_facts(
            android_root,
            facts_dir,
            android_facts_path,
        )
        _validate_file(android_facts_path, "android_facts.v1.schema.json")

    if 2 in stages:
        if 1 not in stages and not _require_file(android_facts_path, 2, "run stage 1 first"):
            return 1
        build_framework_map(
            android_facts_path,
            framework_map_path,
        )
        _validate_file(framework_map_path, "framework_map.v1.schema.json")

    if 3 in stages:
        if 1 not in stages and not _require_file(android_facts_path, 3, "run stage 1 first"):
            return 1
        if 2 not in stages and not _require_file(framework_map_path, 3, "run stage 2 first"):
            return 1
        build_harmony_arch(
            android_facts_path,
            framework_map_path,
            harmony_arch_path,
        )
        _validate_file(harmony_arch_path, "harmony_arch.v1.schema.json")

    if 5 in stages:
        if 1 not in stages and not _require_file(android_facts_path, 5, "run stage 1 first"):
            return 1
        if not _require_dir(facts_dir, 5, "run stage 0 first"):
            return 1
        build_feature_tree(
            android_facts_path,
            facts_dir,
            feature_tree_path,
            taxonomy_path=args.taxonomy.resolve() if args.taxonomy else None,
            taxonomy_overlay_paths=[p.resolve() for p in args.taxonomy_overlay],
            harmony_arch_path=harmony_arch_path if harmony_arch_path.is_file() else None,
        )
        _validate_file(feature_tree_path, "feature_tree.v1.schema.json")

    if 4 in stages:
        if 3 not in stages and not _require_file(harmony_arch_path, 4, "run stage 3 first"):
            return 1
        text = emit_scaffold_dry_run(
            harmony_arch_path,
            intermediate_dir,
            write_files=args.emit_scaffold_files,
        )
        if not args.emit_scaffold_files:
            print(text)

    if 6 in stages:
        if 5 not in stages and not _require_file(feature_tree_path, 6, "run stage 5 first"):
            return 1
        export_feature_tree_view(
            feature_tree_path,
            out_dir / "viewer",
            framework_map_path=framework_map_path if framework_map_path.is_file() else None,
            harmony_arch_path=harmony_arch_path if harmony_arch_path.is_file() else None,
        )

    if 7 in stages:
        if 5 not in stages and not _require_file(feature_tree_path, 7, "run stage 5 first"):
            return 1
        export_agent_bundle(
            feature_tree_path=feature_tree_path,
            evidence_path=feature_tree_path.parent / "feature_spec_evidence.json",
            verify_report_path=feature_tree_path.parent / "verify_report.json",
            taxonomy_report_path=feature_tree_path.parent / "taxonomy_report.json",
            framework_map_path=framework_map_path,
            harmony_arch_path=harmony_arch_path,
            android_facts_path=android_facts_path,
            facts_dir=facts_dir,
            intermediate_dir=intermediate_dir,
            out_path=agent_bundle_path,
        )
        _validate_file(agent_bundle_path, "agent_bundle.v1.schema.json")

    # Ship the directory-level product index with the output, so an agent that
    # only sees <output>/ (not the toolkit source tree) can still orient itself.
    # The shipped copy also carries a live "数量统计" section computed from the
    # artifacts just produced, so the root index reflects this run's counts.
    index_src = toolkit_root() / "docs" / "PIPELINE_OUTPUTS.md"
    if index_src.is_file():
        index_text = index_src.read_text(encoding="utf-8")
        counts_section = _build_counts_section(
            facts_dir, framework_map_path, harmony_arch_path, feature_tree_path)
        (out_dir / "PIPELINE_OUTPUTS.md").write_text(
            index_text + counts_section, encoding="utf-8")

    print("Pipeline completed.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
