from __future__ import annotations

from pathlib import Path
from typing import Any

from stages._util import dump_json, load_json


def build_harmony_arch(
    android_facts_path: Path,
    framework_map_path: Path,
    out_path: Path,
) -> dict[str, Any]:
    af = load_json(android_facts_path)
    fm = load_json(framework_map_path)

    app_id = (af.get("manifest") or {}).get("application_id") or "com.example.placeholder"
    bundle_name = app_id  # Harmony bundleName often mirrors applicationId strategy

    gradle_modules = af.get("gradle_modules") or []
    modules: list[dict[str, Any]] = []
    if gradle_modules:
        for i, gm in enumerate(gradle_modules):
            name = gm.get("name", f"module_{i}")
            role = "entry" if name == "app" or i == 0 else "feature"
            modules.append(
                {
                    "name": f"harmony_{name}",
                    "role": role,
                    "oh_package_name": "entry" if role == "entry" else f"feature_{name}",
                    "source_android_modules": [name],
                }
            )
    else:
        modules.append(
            {
                "name": "harmony_entry",
                "role": "entry",
                "oh_package_name": "entry",
                "source_android_modules": ["app"],
            }
        )

    launcher = (af.get("manifest") or {}).get("launcher_activity_class") or "MainActivity"
    abilities: list[dict[str, Any]] = [
        {
            "name": "EntryAbility",
            "type": "UIAbility",
            "module": modules[0]["name"],
            "screens": [launcher],
        }
    ]
    if len(modules) > 1:
        abilities.append(
            {
                "name": "FeatureAbility",
                "type": "UIAbility",
                "module": modules[1]["name"],
                "screens": [],
            }
        )

    routes: list[dict[str, Any]] = []
    for sc in af.get("screens") or []:
        if sc.get("noise") != "clean":
            continue
        cn = sc.get("class_name") or ""
        layout = sc.get("layout") or ""
        if not cn:
            continue
        safe = cn.replace("$", "_").replace(".", "_").lower()[:64]
        routes.append(
            {
                "name": safe,
                "path_placeholder": f"pages/{safe}/Index",
                "android_screen_class": cn,
                "android_layout": layout,
            }
        )
        if len(routes) >= 64:
            break

    ir: dict[str, Any] = {
        "schema_version": "1.0",
        "bundle_name": bundle_name,
        "modules": modules,
        "abilities": abilities,
        "routes": routes,
        "resource_conventions": {
            "string_catalog": "src/main/resources/base/element/string.json",
            "media_migration": "Migrate drawable/mipmap to Harmony media scale buckets per HDS guidelines.",
        },
        "framework_rules_version": fm.get("rules_version"),
        "gap_item_count": len(fm.get("gap_items") or []),
    }
    dump_json(out_path, ir)
    return ir
