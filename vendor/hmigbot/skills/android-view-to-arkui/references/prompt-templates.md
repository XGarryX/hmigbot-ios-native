# Prompt Templates

Use these templates to keep the migration batch size small and the acceptance criteria explicit.

## 1. Audit Template

```text
Use $android-view-to-arkui.

Audit this Android View/XML project and generate a source UI manifest.

Source root:
- D:\path\to\android-project

Requirements:
1. Run the scanner and produce `.codex/ui-migration/manifest.json`.
2. Summarize page candidates, layouts, menus, dialogs, adapters, and unresolved references.
3. Call out risky patterns that should not be migrated mechanically.
4. Do not write target UI code yet.
```

## 2. Feature Migration Template

```text
Use $android-view-to-arkui.

Migrate one Android feature batch into ArkUI.

Inputs:
- Source manifest: D:\path\to\repo\.codex\ui-migration\manifest.json
- Batch file: D:\path\to\repo\.codex\ui-migration\batches\home-fragment.md
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
Use $android-view-to-arkui.

Verify a partially migrated ArkUI target and repair missing or broken pieces.

Inputs:
- Batch JSON: D:\path\to\repo\.codex\ui-migration\batches\home-fragment.json
- Migration index: D:\path\to\repo\.codex\ui-migration\migration-index.json
- Target project: D:\path\to\target-project

Requirements:
1. Run the coverage checker.
2. Identify missing source dependencies and wrong target mappings.
3. Repair only the missing or broken pieces for this batch.
4. Re-run the target build and stop only when the batch is syntactically clean.
```
