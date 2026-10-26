---
name: android-view-to-arkui
description: Audit, plan, and migrate Android View/XML UI projects into HarmonyOS ArkUI/ETS in controlled feature batches. Use when you need to port an Android XML-based UI to ArkUI, especially for Activity/Fragment/layout/RecyclerView/Dialog/menu codebases where one-shot migrations miss subpages or components, produce wrong screens, or leave syntax and build errors.
metadata:
  type: domain
  domain: migration
  tags:
  - migration
  - android
  - view-xml
  - arkui
---
# Android View To Arkui

## Overview

Use this skill to turn Android View/XML UI migration into a controlled pipeline instead of a one-shot rewrite. First scan the source UI graph, then generate a per-feature batch, migrate only that batch into ArkUI, and verify both dependency coverage and target build health before moving on.

## Supported Scope

Apply this skill when the source UI is primarily built from:

- Android `Activity` and `Fragment`
- XML layouts, menus, drawables, strings, and dimens
- `RecyclerView` with `Adapter` and `ViewHolder`
- Dialogs, bottom sheets, navigation drawers, toolbars, and tab shells

Do not assume direct support for:

- Jetpack Compose
- custom `View.onDraw` or gesture-heavy custom views
- MotionLayout or Coordinator behaviors that rely on nested Android behaviors
- Media3, ExoPlayer, or video surface behavior
- business logic, background jobs, or persistence migration

For those cases, read [references/unsupported-patterns.md](references/unsupported-patterns.md) and leave explicit TODOs instead of inventing behavior.

## Project Artifacts

Keep project-specific state under `.codex/ui-migration/` in the repo being migrated:

- `manifest.json`: source UI inventory created by `scripts/scan_android_ui.ps1`
- `migration-index.json`: source files and pages already covered by migrated target code
- `batches/*.md`: human-readable migration task packs
- `batches/*.json`: machine-readable batch metadata used by the coverage checker

Do not hardcode project-specific page names or target paths into this skill.

## Workflow

### 1. Audit The Source UI

Run the scanner before planning or coding:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/scan_android_ui.ps1 `
  -SourceRoot D:\path\to\android-project `
  -OutputPath D:\path\to\repo\.codex\ui-migration\manifest.json
```

The scanner inventories:

- page candidates (`Activity`, `Fragment`)
- layout and menu references
- likely dialog, adapter, view holder, section, and custom-view dependencies
- unresolved resource references that need manual review

Use the manifest as the source of truth for what exists. Do not start migration from memory or from a single XML file.

### 1.5. MANDATORY: Deep Verify The Manifest

After the scanner produces `manifest.json`, you MUST run the deep verification script. Do NOT skip this step.

```powershell
powershell -ExecutionPolicy Bypass -File scripts/deep_verify.ps1 `
  -SourceRoot D:\path\to\android-project `
  -ManifestPath D:\path\to\repo\.codex\ui-migration\manifest.json
```

The script performs inheritance-based scanning (not just filename patterns) across ALL modules to find Activities, Fragments, Dialogs, Adapters, and Custom Views that the filename-based scanner missed. It cross-checks every found class against the manifest and outputs a report to `.codex/ui-migration/manifest-verify-report.json`.

If the script exits with code 1 (missing items found):
1. Review the missing items in the report
2. Update `manifest.json` to include the missing pages and dependencies
3. Re-run the script until it reports `COMPLETE`

Do NOT proceed to step 2 until the deep verification passes.

### 2. Build One Feature Batch

Generate a task pack for one or more related entry pages:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build_feature_pack.ps1 `
  -ManifestPath D:\path\to\repo\.codex\ui-migration\manifest.json `
  -PageNames HomeFragment,SubscriptionsFragment
```

This creates both a Markdown batch file and a JSON batch file. Use the Markdown file for migration work and keep the JSON file for coverage checking.

Choose the smallest batch that still makes sense:

- app shell first
- one feature page plus its direct children
- one dialog family
- one list screen plus its item component

Never ask Codex to migrate the entire repo in one pass.

### 3. Read Only The Needed References

Before writing code:

- read [references/android-to-arkui-mapping.md](references/android-to-arkui-mapping.md) for control and structure mapping
- read [references/prompt-templates.md](references/prompt-templates.md) for task prompts
- read [references/unsupported-patterns.md](references/unsupported-patterns.md) when the batch includes dynamic fragments, custom views, player UI, or Android-specific shell behavior

Do not load every reference file unless it is needed for the current batch.

### 4. Migrate One Batch At A Time

When migrating a batch, follow these rules:

- list direct dependencies from the batch before editing target files
- translate static structure first, then add state and interaction wiring
- do NOT translate Android layout parameters (`layout_width` / `match_parent` / `layout_margin`) literally — ArkUI counts margin as part of a component's own size, so `width('100%')` + horizontal margin overflows the parent (the compiler will not catch it). See the **Layout Parameter Mapping** table in `references/android-to-arkui-mapping.md`: sink horizontal margin into the parent's `padding` (or `calc(100% - Nvp)`), keep vertical margin as-is.
- create missing subcomponents in the same batch if the source page depends on them
- split app shell, page, list item, dialog, and section components instead of building one giant target file
- keep unsupported or platform-specific behavior as explicit TODOs
- do not silently drop menus, dialogs, or list item types

If the source page uses dynamic composition, such as programmatically injecting child fragments or sections, mirror that as a parent ArkUI component plus extracted child components rather than flattening everything into one page.

### 5. Record Coverage

Keep `migration-index.json` updated after each batch. At minimum, record:

- covered source pages
- covered source files
- target files created for that batch

Then run the coverage checker:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/check_coverage.ps1 `
  -BatchJsonPath D:\path\to\repo\.codex\ui-migration\batches\home-fragment.json `
  -MigrationIndexPath D:\path\to\repo\.codex\ui-migration\migration-index.json
```

Treat missing coverage as a blocker. Fix the batch or update the migration index before moving on.

### 5.5. MANDATORY: Post-Batch Deep Verification

After coverage check passes, you MUST run this verification before proceeding to the build step. Do NOT skip this.

#### 5.5a — Completeness check: sub-dependencies

For each page in the batch, re-read the Android source class and verify every dependency was handled:

1. **Included layouts**: Search the layout XML for `<include layout=` — was each included layout translated into a sub-component or inlined in the target?
2. **Adapters**: Does the source use RecyclerView/ListView? Was the Adapter's item layout migrated as a separate `@ComponentV2` (or legacy `@Component`) sub-component?
3. **ViewHolders**: If the Adapter has a ViewHolder with complex layout, was it captured in the target?
4. **Dialogs launched**: Search the source class for `Dialog`, `.show()`, `AlertDialog`, `BottomSheet` — was each dialog migrated or noted as TODO?
5. **Menu items**: Does the source inflate a menu XML? Were all menu actions translated to ArkUI header actions or buttons?
6. **Navigation targets**: Were all `Intent`/`NavController.navigate` targets accounted for in the migration index or manifest?
7. **Child Fragments**: Does the source add child fragments via `FragmentTransaction` or `childFragmentManager`? Were they migrated as child components?

For each missing dependency found:
- Create the missing component immediately in this batch, OR
- Add it to the manifest as a new uncovered page/dependency and document it in the batch report

#### 5.5b — Write batch verification report

Append verification results to the batch Markdown file:

```markdown
## Post-Batch Verification

### Sub-dependency check
- Included layouts checked: N, all handled: ✅/❌
- Adapters checked: N, all handled: ✅/❌
- Dialogs checked: N, all handled: ✅/❌
- Menus checked: N, all handled: ✅/❌
- Child fragments checked: N, all handled: ✅/❌
- Items added during verification: N

### Verdict: ✅ PASS / ⚠️ FIXED / ❌ BLOCKED
```

Only proceed to step 6 (build verification) if the verdict is ✅ PASS or ⚠️ FIXED.

### 6. Verify The Target Build

After each batch, verify the target project. This is the ONLY syntax check — the build compiler catches all type errors, missing imports, decorator issues, and ArkTS-specific constraints.

```powershell
powershell -ExecutionPolicy Bypass -File scripts/verify_target_build.ps1 `
  -TargetRoot D:\path\to\target-project `
  -BuildCommand ".\hvigorw.bat --mode project assembleHap"
```

If the build fails:
1. Read the error output carefully
2. Fix each error in the generated `.ets` files
3. Re-run the build
4. Repeat until the build passes or the only remaining errors are from files NOT created in this batch

Do NOT close the task while syntax or build errors remain in files created by this batch.

## Migration Guardrails

- Treat the migration as UI-first. Only port behavior needed to render or navigate the batch.
- Assume source dependencies are hidden in Java/Kotlin, XML, adapters, dialogs, menus, and dynamic child components.
- Prefer reusable ArkUI components over mechanical layout conversion.
- Convert one page family at a time. Large multi-page prompts cause omissions.
- Keep source and target terminology separate. Translate structure, not class names.

## Quick Triage

Use this skill when the user asks for things like:

- “Scan this Android app and tell me what UI needs to move”
- “Convert this Android View/XML page into ArkUI”
- “Find what the previous migration missed”
- “Generate a migration checklist before writing target UI”
- “Fix the target build after a partial UI migration”

Do not use this skill for generic Android refactors or for non-UI business logic ports.
