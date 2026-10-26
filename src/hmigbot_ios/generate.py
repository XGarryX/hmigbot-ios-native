"""Build draft projects only from the closed, fully consumed page grammar."""
from __future__ import annotations

from pathlib import Path
import re

from . import __version__
from .core import source_snapshot
from .core import SCHEMA, MigrationError, digest, json_bytes, read_json, safe_child, snapshot, write_new_tree
from .analyze import analyze, migration_plan, render_report
from .swiftui import emit_view


def sdk_api(value):
    match = re.fullmatch(r"\d+\.\d+\.\d+\((\d+)\)", value)
    if match:
        return int(match.group(1))
    if re.fullmatch(r"\d+\.\d+\.\d+", value) and int(value.split(".")[0]) >= 26:
        return int(value.split(".")[0])
    raise MigrationError("HarmonyOS SDK requires product notation through API 25 (6.0.2(22)), or x.y.z from API 26 (26.0.0)")


def generate(root: Path, output: Path, *, sdk: str, min_sdk: str, model_version: str,
             bundle_name: str, entry_view: str | None = None, resource_bundles=None, scaffold_only=False):
    root, output = root.resolve(), output.resolve()
    if root.is_relative_to(output) or output.is_relative_to(root):
        raise MigrationError("Generated output and source must not overlap")
    if sdk_api(sdk) < sdk_api(min_sdk) or sdk_api(min_sdk) < 12:
        raise MigrationError("Require target SDK >= compatible SDK >= API 12")
    if not re.fullmatch(r"\d+\.\d+\.\d+", model_version):
        raise MigrationError("model_version must be an explicit x.y.z version")
    if not re.fullmatch(r"[a-zA-Z][a-zA-Z0-9_]*(?:\.[a-zA-Z][a-zA-Z0-9_]*)+", bundle_name):
        raise MigrationError("Invalid HarmonyOS bundle name")
    report = analyze(root)
    if report['parsing']['status'] == 'failed' and not scaffold_only:
        failed = [p for p in report['parsing']['files'] if p['status'] == 'failed']
        raise MigrationError('Official and weak parsing failed: ' +
            '; '.join(p['path'] + ': ' + ' | '.join(a.get('error', a['status']) for a in p['attempts']) for p in failed))
    pages = [p for p in report["pages"] if p["status"] in {"convertible_subset", 'weak_draft_subset'}]
    if not pages and not scaffold_only:
        raise MigrationError("No page is completely covered by an implemented rule; run scan for gaps")
    if scaffold_only:
        pages = []
        entry_view = 'Index'
    names = [p["view"]["name"] for p in pages] if not scaffold_only else ['Index']
    if len({n.casefold() for n in names}) != len(names):
        raise MigrationError("Duplicate/case-colliding view names need module-aware naming")
    if entry_view is None:
        if len(pages) != 1:
            raise MigrationError("Multiple convertible views: select --entry-view explicitly")
        entry_view = names[0]
    if entry_view not in names:
        raise MigrationError("entry-view is not a convertible source view")
    files = {}
    resources = []
    for bundle in resource_bundles or []:
        artifact = read_json(bundle / 'artifact.json')
        if artifact.get('schema_version') != SCHEMA or artifact.get('operation') not in {'asset-convert', 'localization-convert'}:
            raise MigrationError('Unsupported resource bundle')
        if artifact.get('source_sha256') != report['source_snapshot']['sha256']:
            raise MigrationError('Resource bundle is stale or belongs to another source')
        from .contracts import validate_file_map
        validate_file_map(artifact.get('outputs'))
        for name, checksum in artifact['outputs'].items():
            if not name.startswith('entry/src/main/resources/'):
                raise MigrationError('Resource bundle attempts to modify a non-resource file')
            data = safe_child(bundle, name).read_bytes()
            if digest(data) != checksum or name in files:
                raise MigrationError('Modified or conflicting resource output')
            files[name] = data
        resources.append(artifact)
    image_mappings = [m for a in resources if a['operation'] == 'asset-convert' for m in a['data']['mappings']]
    string_mappings = [m for a in resources if a['operation'] == 'localization-convert' for m in a['data']['mappings']]
    def bind_resources(node):
        if node['kind'] == 'Image':
            matches = [m for m in image_mappings if m['source_name'] == node['asset_name']]
            if len(matches) != 1:
                raise MigrationError('Image needs one unambiguous converted asset: ' + node['asset_name'])
            match = matches[0]
            node['resource'] = match['resource']
            for axis in ('width', 'height'):
                if not any(m['name'] == axis for m in node['modifiers']):
                    node['modifiers'].append({'name': axis, 'value': match['logical_' + axis]})
        elif node.get('text') and not node.get('verbatim') and all('literal' in p for p in node['text']):
            text = ''.join(p['literal'] for p in node['text'])
            matches = [m for m in string_mappings if m['key'] == text]
            if len(matches) > 1:
                raise MigrationError('Text key needs an explicit localization namespace: ' + text)
            if matches:
                node['resource'] = matches[0]['resource']
        for child in node['children']:
            bind_resources(child)
    def put(name, value):
        if name in files:
            raise MigrationError('Generated template conflicts with resource output: ' + name)
        files[name] = value.encode("utf-8") if isinstance(value, str) else json_bytes(value)
    if scaffold_only:
        put('entry/src/main/ets/pages/Index.ets',
            '// Project scaffold only. No source application behavior has been migrated.\n'
            '@Entry\n@Component\nstruct Index {\n  build() {\n    Column() {\n'
            '      Text("Migration scaffold")\n    }\n  }\n}\n')
    for page in pages:
        # Do not mutate extracted source facts when lowering target-only resource bindings.
        import copy
        target_view = copy.deepcopy(page['view'])
        bind_resources(target_view['root'])
        name = page["view"]["name"]
        # Every registered page is an independent preview, not reconstructed navigation.
        put(f"entry/src/main/ets/pages/{name}.ets", emit_view(target_view, entry=True))
    put("AppScope/app.json5", {"app": {"bundleName": bundle_name, "vendor": "migration-draft",
        "versionCode": 1000000, "versionName": "1.0.0", "icon": "$media:app_icon", "label": "$string:app_name"}})
    put("AppScope/resources/base/element/string.json", {"string": [{"name": "app_name", "value": entry_view}]})
    icon = '<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128" viewBox="0 0 128 128"><rect width="128" height="128" rx="24" fill="#255EDC"/><path d="M32 64h64M64 32v64" stroke="white" stroke-width="12"/></svg>'
    put("AppScope/resources/base/media/app_icon.svg", icon)
    put("entry/src/main/resources/base/media/app_icon.svg", icon)
    put("entry/src/main/resources/base/element/string.json", {"string": [{"name": "entry_label", "value": entry_view}]})
    put("entry/src/main/resources/base/element/color.json", {"color": [{"name": "start_background", "value": "#FFFFFF"}]})
    put("entry/src/main/resources/base/profile/main_pages.json", {"src": [f"pages/{entry_view}"] +
        [f"pages/{name}" for name in names if name != entry_view]})
    put("entry/src/main/module.json5", {"module": {"name": "entry", "type": "entry", "mainElement": "EntryAbility",
        "deviceTypes": ["phone", "tablet"], "deliveryWithInstall": True, "installationFree": False,
        "pages": "$profile:main_pages", "abilities": [{"name": "EntryAbility", "srcEntry": "./ets/entryability/EntryAbility.ets",
            "icon": "$media:app_icon", "label": "$string:entry_label", "startWindowIcon": "$media:app_icon",
            "startWindowBackground": "$color:start_background", "exported": True,
            "skills": [{"entities": ["entity.system.home"], "actions": ["ohos.want.action.home"]}]}]}})
    put("entry/src/main/ets/entryability/EntryAbility.ets",
        "import { UIAbility } from '@kit.AbilityKit';\nimport { window } from '@kit.ArkUI';\n\n"
        "export default class EntryAbility extends UIAbility {\n"
        "  onWindowStageCreate(stage: window.WindowStage): void {\n"
        f"    stage.loadContent('pages/{entry_view}', (error) => {{\n"
        "      if (error.code) { console.error('Page load failed: ' + error.message); }\n"
        "    });\n  }\n}\n")
    put("build-profile.json5", {"app": {"products": [{"name": "default", "runtimeOS": "HarmonyOS",
        "compileSdkVersion": sdk, "targetSdkVersion": sdk, "compatibleSdkVersion": min_sdk}], "buildModeSet": [{"name": "debug"}, {"name": "release"}]},
        "modules": [{"name": "entry", "srcPath": "./entry", "targets": [{"name": "default", "applyToProducts": ["default"]}]}]})
    put("entry/build-profile.json5", {"apiType": "stageMode", "buildOption": {}, "targets": [{"name": "default"}]})
    put("oh-package.json5", {"modelVersion": model_version, "name": "migration-draft", "version": "1.0.0", "dependencies": {}})
    put("entry/oh-package.json5", {"name": "entry", "version": "1.0.0", "dependencies": {}})
    put("hvigor/hvigor-config.json5", {"modelVersion": model_version, "dependencies": {}})
    put("hvigorfile.ts", "import { appTasks } from '@ohos/hvigor-ohos-plugin';\nexport default { system: appTasks, plugins: [] };\n")
    put("entry/hvigorfile.ts", "import { hapTasks } from '@ohos/hvigor-ohos-plugin';\nexport default { system: hapTasks, plugins: [] };\n")
    plan = migration_plan(report)
    put("migration/facts.json", report)
    put("migration/plan.json", plan)
    if resources:
        put('migration/resources.json', resources)
    put("migration/report.md", render_report(report, plan))
    manifest = {"schema_version": SCHEMA, "tool_version": __version__, "source_sha256": report["source_snapshot"]["sha256"],
                "source_root": str(root), "profile": {"sdk": sdk, "min_sdk": min_sdk, "model_version": model_version},
                "generated_pages": [{"source": p["path"], "target": f"entry/src/main/ets/pages/{p['view']['name']}.ets",
                                     "rule": p["view"]["rule"], 'parsing': p['parsing']} for p in pages],
                'parsing': report['parsing'],
                "files": {name: digest(data) for name, data in sorted(files.items())},
                "status": "scaffold_created" if scaffold_only else "draft_generated", "target_build": "not_run", "source_build": "not_run",
                "behavior": "not_verified", "visual": "not_verified", "app_migration": "incomplete"}
    put("migration/generation.json", manifest)
    if source_snapshot(root)['sha256'] != report['source_snapshot']['sha256']:
        raise MigrationError('Source changed before draft publication')
    write_new_tree(output, files)
    return manifest


def verify(root: Path, output: Path):
    from .contracts import validate_generation
    manifest = read_json(output / "migration/generation.json")
    validate_generation(manifest)
    checks = [{"name": "source_snapshot", "passed": source_snapshot(root)["sha256"] == manifest["source_sha256"]}]
    for name, expected in manifest["files"].items():
        path = safe_child(output, name)
        checks.append({"name": name, "passed": path.is_file() and digest(path.read_bytes()) == expected})
    return {"schema_version": SCHEMA, "integrity_passed": all(c["passed"] for c in checks), "checks": checks,
            "scope": "source freshness and generated-file integrity only",
            "target_build": "not_run", "behavior": "not_verified", "app_migration": "incomplete"}
