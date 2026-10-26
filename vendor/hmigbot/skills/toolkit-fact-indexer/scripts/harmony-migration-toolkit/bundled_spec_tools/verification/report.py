from __future__ import annotations

import json
from pathlib import Path


def build_verification_report(
    manifest_result: dict,
    layout_result: dict,
    bytecode_result: dict,
) -> dict:
    report = {
        "schema_version": "1.0",
        "summary": {},
        "sections": {
            "manifest_activity_check": manifest_result,
            "layout_fragment_check": layout_result,
            "bytecode_hierarchy_check": bytecode_result,
        },
    }

    manifest = manifest_result
    layout = layout_result
    bytecode = bytecode_result

    total = 0
    matched = 0
    missed = 0
    issues: list[str] = []

    m_total = manifest.get("manifest_activity_count", 0)
    m_matched = manifest.get("ast_activity_count", 0)
    m_missed = len(manifest.get("ast_activity_missed", []))
    m_only = len(manifest.get("manifest_only", []))
    total += m_total
    matched += m_matched
    missed += m_missed + m_only
    if m_missed:
        issues.append(
            f"{m_missed} manifest activities have wrong AST type"
        )
    if m_only:
        issues.append(
            f"{m_only} manifest activities missing from AST hierarchy entirely"
        )

    l_total = layout.get("layout_fragment_ref_count", 0)
    l_matched = layout.get("ast_fragment_count", 0)
    l_missed = len(layout.get("ast_fragment_missed", []))
    l_only = len(layout.get("layout_only", []))
    total += l_total
    matched += l_matched
    missed += l_missed + l_only
    if l_missed:
        issues.append(
            f"{l_missed} layout <fragment> refs have wrong AST type"
        )
    if l_only:
        issues.append(
            f"{l_only} layout <fragment> refs missing from AST hierarchy"
        )

    if bytecode.get("bytecode_available"):
        b_frag_diff = bytecode.get("ast_vs_bytecode_fragment_diff", {})
        b_act_diff = bytecode.get("ast_vs_bytecode_activity_diff", {})

        frag_bc_only = len(b_frag_diff.get("bytecode_only", []))
        frag_ast_only = len(b_frag_diff.get("ast_only", []))
        act_bc_only = len(b_act_diff.get("bytecode_only", []))
        act_ast_only = len(b_act_diff.get("ast_only", []))

        if frag_bc_only:
            issues.append(f"{frag_bc_only} fragments in bytecode but not in AST")
        if frag_ast_only:
            issues.append(f"{frag_ast_only} fragments in AST but not in bytecode")
        if act_bc_only:
            issues.append(f"{act_bc_only} activities in bytecode but not in AST")
        if act_ast_only:
            issues.append(f"{act_ast_only} activities in AST but not in bytecode")

    report["summary"] = {
        "total_checks": total,
        "matched": matched,
        "issues": len(issues),
        "issue_details": issues,
    }

    return report


def print_verification_report(report: dict) -> None:
    summary = report["summary"]
    print("=" * 70)
    print("VERIFICATION REPORT")
    print("=" * 70)
    print(f"  Total checks : {summary['total_checks']}")
    print(f"  Matched      : {summary['matched']}")
    print(f"  Issues       : {summary['issues']}")

    for section_name, section_data in report["sections"].items():
        print(f"\n  ── {section_name} ──")
        if "manifest_activity_count" in section_data:
            m = section_data
            print(f"    Manifest activities: {m['manifest_activity_count']}")
            print(f"      AST matched as activity: {m['ast_activity_count']}")
            for item in m.get("ast_activity_missed", []):
                print(f"      ⚠  {item['class']} → AST says {item['ast_kind']}")
            for item in m.get("manifest_only", []):
                print(f"      ⚠  {item['class']} → not in AST hierarchy")
        elif "layout_fragment_ref_count" in section_data:
            l = section_data
            print(f"    Layout <fragment> refs: {l['layout_fragment_ref_count']}")
            print(f"      AST matched as fragment: {l['ast_fragment_count']}")
            for item in l.get("ast_fragment_missed", []):
                print(f"      ⚠  {item['class']} → AST says {item['ast_kind']}")
            for item in l.get("layout_only", []):
                print(f"      ⚠  {item['class']} → not in AST hierarchy")
        elif "bytecode_class_count" in section_data:
            b = section_data
            print(f"    Bytecode classes: {b['bytecode_class_count']}")
            if not b.get("bytecode_available"):
                print("      ⚠  No bytecode data — build project first or check find_class_dir()")
                continue
            print(f"      Fragments: {b['bytecode_fragment_count']}  "
                  f"Activities: {b['bytecode_activity_count']}")
            for diff_key, diff_label in [
                ("ast_vs_bytecode_fragment_diff", "Fragment"),
                ("ast_vs_bytecode_activity_diff", "Activity"),
            ]:
                diff = b.get(diff_key, {})
                bc_only = diff.get("bytecode_only", [])
                ast_only = diff.get("ast_only", [])
                matched = diff.get("matched", [])
                synthetic = diff.get("synthetic_excluded_count", 0)
                print(f"      {diff_label} AST vs Bytecode:")
                print(f"        matched: {len(matched)}")
                if ast_only:
                    print(f"        AST only ({len(ast_only)}): {', '.join(ast_only[:10])}")
                if bc_only:
                    print(f"        Bytecode only ({len(bc_only)}): {', '.join(bc_only[:10])}")
                if synthetic:
                    print(f"        excluded (Hilt synthetic bases): {synthetic}")

    if summary["issues"]:
        print("\n  ── Issues ──")
        for iss in summary["issue_details"]:
            print(f"    • {iss}")
    print("=" * 70)
