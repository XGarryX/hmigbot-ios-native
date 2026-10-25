from __future__ import annotations

from pathlib import Path
from typing import Any

from stages._util import dump_json, load_json


def emit_scaffold_dry_run(harmony_arch_path: Path, out_dir: Path, write_files: bool) -> str:
    arch = load_json(harmony_arch_path)
    lines: list[str] = []
    lines.append("HarmonyOS scaffold plan (deterministic dry-run)")
    lines.append("=" * 50)
    lines.append(f"bundle_name: {arch.get('bundle_name')}")
    lines.append("")
    lines.append("modules:")
    for m in arch.get("modules") or []:
        lines.append(f"  - {m.get('name')} [{m.get('role')}] -> {m.get('oh_package_name')}")
    lines.append("")
    lines.append("abilities:")
    for a in arch.get("abilities") or []:
        lines.append(f"  - {a.get('name')} ({a.get('type')}) module={a.get('module')} screens={a.get('screens')}")
    lines.append("")
    lines.append("routes (placeholders):")
    for r in arch.get("routes") or []:
        lines.append(f"  - {r.get('name')}: {r.get('path_placeholder')}")
    text = "\n".join(lines) + "\n"

    if write_files:
        scaffold = out_dir / "4_scaffold"
        scaffold.mkdir(parents=True, exist_ok=True)
        (scaffold / "SCAFFOLD_PLAN.txt").write_text(text, encoding="utf-8", newline="\n")
        readme = (
            "# Generated scaffold (deterministic)\n\n"
            "This directory only records the planned Harmony module/route tree.\n"
            "Full `oh-package.json5` / ArkTS sources are intentionally not emitted in v1.\n"
            "Use `harmony_arch.v1.json` with LLM or DevEco templates for implementation.\n"
        )
        (scaffold / "README.md").write_text(readme, encoding="utf-8", newline="\n")
        dump_json(scaffold / "harmony_arch.snapshot.json", arch)

    return text
