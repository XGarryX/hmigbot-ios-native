# Prompt Templates

Use these templates to keep the migration batch size small and the acceptance criteria explicit.

## 1. Audit Template

```text
Use $ios-ui-to-arkui.

Audit this iOS View/XML project and generate a source UI manifest.

Source root:
- D:\path\to\ios-project

Requirements:
1. Run the scanner and produce `<target>/spec/reports/derived/ui-migration/manifest.json` in the HarmonyOS target project.
2. Summarize page candidates, layouts, menus, dialogs, adapters, and unresolved references.
3. Call out risky patterns that should not be migrated mechanically.
4. Do not write target UI code yet.
```

## 2. Feature Migration Template

```text
Use $ios-ui-to-arkui.

Migrate one iOS feature batch into ArkUI.

Inputs:
- Source manifest: <target>/spec/reports/derived/ui-migration/manifest.json
- Batch file: <target>/spec/reports/derived/ui-migration/batches/home-page.md
- Target project: D:\path\to\target-project

Requirements:
1. Read the batch and list direct dependencies before editing target files.
2. Migrate only this batch. Do not touch unrelated pages.
3. Create missing child components, dialogs, and list items in the same batch.
4. Preserve unsupported behavior as TODOs instead of inventing parity.
5. Update `migration-index.json` with covered source files and pages.
6. Run the build verification step and fix syntax/build errors.
```

## 3. Verify And Repair Template

```text
Use $ios-ui-to-arkui.

Verify a partially migrated ArkUI target and repair missing or broken pieces.

Inputs:
- Batch JSON: <target>/spec/reports/derived/ui-migration/batches/home-page.json
- Migration index: <target>/spec/reports/derived/ui-migration/migration-index.json
- Target project: D:\path\to\target-project

Requirements:
1. Run the coverage checker.
2. Identify missing source dependencies and wrong target mappings.
3. Repair only the missing or broken pieces for this batch.
4. Re-run the target build and stop only when the batch is syntactically clean.
```
