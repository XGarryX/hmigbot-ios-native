from __future__ import annotations

import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from stages._util import dump_json, normalize_android_paths, sha256_text, toolkit_root


def _load_json_if_present(path: Path) -> Any:
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _spec_tools_trace(spec_tools: Path) -> dict[str, Any]:
    trace: dict[str, Any] = {
        "root": str(spec_tools).replace("\\", "/"),
    }
    main_py = spec_tools / "main.py"
    if main_py.is_file():
        body = main_py.read_text(encoding="utf-8", errors="ignore")
        trace["main_py_sha256"] = sha256_text(body)
        trace["main_py_bytes"] = len(body.encode("utf-8"))
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(spec_tools),
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        if commit:
            trace["git_commit"] = commit
    except (OSError, subprocess.CalledProcessError):
        trace["git_commit"] = None
    return trace


def _validate_core_artifacts(facts_dir: Path) -> dict[str, Any]:
    checks: dict[str, Any] = {"warnings": []}
    call_graph = _load_json_if_present(facts_dir / "call_graph.json")
    function_symbols = _load_json_if_present(facts_dir / "function_symbols.json")

    if call_graph is None:
        checks["warnings"].append("missing_call_graph_json")
    elif not isinstance(call_graph, dict):
        checks["warnings"].append("call_graph_json_not_object")
    else:
        for key in ("calls", "symbols", "stats"):
            if key not in call_graph:
                checks["warnings"].append(f"call_graph_missing_{key}")
        calls = call_graph.get("calls") if isinstance(call_graph.get("calls"), list) else []
        symbols = call_graph.get("symbols") if isinstance(call_graph.get("symbols"), list) else []
        stats = call_graph.get("stats") if isinstance(call_graph.get("stats"), dict) else {}
        checks["call_graph"] = {
            "call_count": len(calls),
            "symbol_count": len(symbols),
            "stats_symbol_count": stats.get("symbol_count"),
        }

    if function_symbols is None:
        checks["warnings"].append("missing_function_symbols_json")
    elif not isinstance(function_symbols, dict):
        checks["warnings"].append("function_symbols_json_not_object")
    else:
        symbols = function_symbols.get("symbols") if isinstance(function_symbols.get("symbols"), list) else []
        stats = function_symbols.get("stats") if isinstance(function_symbols.get("stats"), dict) else {}
        checks["function_symbols"] = {
            "symbol_count": len(symbols),
            "stats_symbol_count": stats.get("symbol_count"),
        }
        cg_stats = (checks.get("call_graph") or {}).get("stats_symbol_count")
        if cg_stats is not None and cg_stats != len(symbols):
            checks["warnings"].append("function_symbols_count_differs_from_call_graph_stats")
        if stats.get("symbol_count") is not None and stats.get("symbol_count") != len(symbols):
            checks["warnings"].append("function_symbols_stats_count_differs_from_symbols")

    return checks


def _normalize_dir_facts_dir(facts_dir: Path, android_root: Path) -> dict[str, dict[str, Any]]:
    # Path normalization must preserve each file's authored key order — specs are
    # built in progressive-disclosure order (brief first) and sorting keys here
    # would alphabetize them (behavior before brief), defeating that intent.
    #
    # Returns each artifact's sha256/byte index, computed from the text we just
    # wrote, so the caller can build the manifest without a second full read of the
    # tree (the call graph alone is ~13MB).
    android_root = android_root.resolve()
    hashes: dict[str, dict[str, Any]] = {}
    for p in facts_dir.rglob("*.json"):
        data = json.loads(p.read_text(encoding="utf-8"))
        fixed = normalize_android_paths(data, android_root)
        text = json.dumps(fixed, indent=2, ensure_ascii=False) + "\n"
        p.write_text(text, encoding="utf-8", newline="\n")
        hashes[p.relative_to(facts_dir).as_posix()] = {
            "sha256": sha256_text(text),
            "bytes": len(text.encode("utf-8")),
        }
    return hashes


def default_spec_tools_root() -> Path:
    """Directory containing bundled `main.py` + `extractors/` (toolkit-internal)."""
    return toolkit_root() / "bundled_spec_tools"


def _copy_from_spec_output(spec_output: Path, facts_dir: Path) -> None:
    """Mirror bundled spec-tools ``output/`` into ``facts_dir`` (full tree, no filename whitelist).

    Static scan may add new JSON or subdirectories; copying everything avoids silently dropping files.
    """
    if not spec_output.is_dir():
        raise FileNotFoundError(
            f"Spec-tools output directory missing or not a directory: {spec_output}"
        )
    if facts_dir.exists():
        shutil.rmtree(facts_dir)
    shutil.copytree(spec_output, facts_dir, symlinks=False)


def run_stage0(
    android_root: Path,
    out_dir: Path,
    spec_tools_root: Path | None,
    skip_spec_tools: bool = False,
    facts_source: Path | None = None,
) -> dict[str, Any]:
    """
    Populate out_dir/0_android_facts from bundled_spec_tools or from --facts-source.

    If facts_source is set, copy that directory tree (for tests) and skip running main.py.
    """
    android_root = android_root.resolve()
    spec_tools = (spec_tools_root or default_spec_tools_root()).resolve()
    spec_main = spec_tools / "main.py"
    spec_output = spec_tools / "output"
    facts_dir = out_dir / "0_android_facts"
    scan_tmp = out_dir / "0_android_facts.__scan_tmp"

    if facts_source is not None:
        src = facts_source.resolve()
        if not src.is_dir():
            raise FileNotFoundError(f"--facts-source not a directory: {src}")
        if facts_dir.exists():
            shutil.rmtree(facts_dir)
        shutil.copytree(src, facts_dir)
    elif not skip_spec_tools:
        if not spec_main.is_file():
            raise FileNotFoundError(
                f"Bundled spec-tools main.py not found: {spec_main}. "
                "Restore harmony-migration-toolkit/bundled_spec_tools or pass --spec-tools-root."
            )
        if scan_tmp.exists():
            shutil.rmtree(scan_tmp)
        cmd = [sys.executable, str(spec_main), str(android_root), "--out", str(scan_tmp)]
        try:
            subprocess.run(cmd, cwd=str(spec_tools), check=True)
            if not scan_tmp.is_dir():
                raise FileNotFoundError(
                    f"Spec-tools scan produced no output directory: {scan_tmp}"
                )
            # Move (rename on the same filesystem — scan_tmp and facts_dir are
            # siblings under out_dir) rather than copytree+rmtree, avoiding a full
            # copy of the multi-MB scan tree. On success scan_tmp is gone, so the
            # finally cleanup is a no-op; it only fires if the scan or move failed.
            if facts_dir.exists():
                shutil.rmtree(facts_dir)
            shutil.move(str(scan_tmp), str(facts_dir))
        finally:
            # A killed process (Ctrl-C, OOM) can skip this; the rmtree at the top of
            # the next run sweeps any stale scan_tmp, so it never lingers as an artifact.
            if scan_tmp.exists():
                shutil.rmtree(scan_tmp)
    else:
        if not spec_output.is_dir():
            raise FileNotFoundError(
                f"--skip-spec-tools requires existing {spec_output} "
                f"(run Stage 0 without --skip-spec-tools once, or populate output/ under {spec_tools})."
            )
        _copy_from_spec_output(spec_output, facts_dir)

    artifact_hashes = _normalize_dir_facts_dir(facts_dir, android_root)

    manifest: dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "android_root": str(android_root).replace("\\", "/"),
        "spec_tools_root": str(spec_tools).replace("\\", "/"),
        "spec_tools": _spec_tools_trace(spec_tools),
        "facts_source": str(facts_source).replace("\\", "/") if facts_source else None,
        "artifact_checks": _validate_core_artifacts(facts_dir),
        "artifacts": {},
    }
    # Reuse the sha256/byte index produced during normalization instead of reading
    # every artifact a second time (the call graph alone is ~13MB).
    for rel in sorted(artifact_hashes):
        manifest["artifacts"][rel] = artifact_hashes[rel]

    dump_json(facts_dir / "manifest.json", manifest)
    return manifest
