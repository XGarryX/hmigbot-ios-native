# Pipeline Output Index

A directory-level map of everything the pipeline writes under `<output>/`. This is
an index ("what lives where"), not a field reference — for stage-0 field details
see [`bundled_spec_tools/ARCHITECTURE.md`](../bundled_spec_tools/ARCHITECTURE.md);
for the feature-tree / bundle schemas see `docs/FEATURE_TREE_AND_VIEWER_DESIGN.md`.

> The copy shipped into `<output>/` carries a live **数量统计 (Counts)** section at
> the end, computed from the artifacts of that run (this source template does not).

Default stage order is `0,1,2,3,5,4,7`. Each stage's products live under
`<output>/intermediate/<n>_<name>/`; the final deliverable sits at the output root.

```
<output>/
├── agent_bundle.v1.json        # Stage 7 — the single agent-consumable deliverable
├── PIPELINE_OUTPUTS.md         # this index, shipped into the output so consumers see it
├── viewer/                     # Stage 6 — interactive HTML viewer (optional stage)
└── intermediate/               # reproducible per-stage debugging artifacts
    ├── 0_android_facts/        # Stage 0 — static analysis of the Android app
    ├── 1_android_facts/        # Stage 1 — normalized single-file facts model
    ├── 2_framework_map/        # Stage 2 — Android API → HarmonyOS framework map
    ├── 3_harmony_arch/         # Stage 3 — projected HarmonyOS module/ability arch
    ├── 4_scaffold/             # Stage 4 — scaffold plan (only with --emit-scaffold-files)
    └── 5_feature_tree/         # Stage 5 — feature grouping + evidence + verification
```

(A transient `0_android_facts.__scan_tmp/` exists only while Stage 0 runs — the raw
scanner output before it is mirrored and normalized into `0_android_facts/`. It is
removed when the stage finishes, so it is not a product and not indexed below.)

## Stage 0 — `intermediate/0_android_facts/`

Full mirror of the bundled static analyzer (`bundled_spec_tools/`) output, with
paths normalized. The richest stage. Top-level JSON:

| File | Holds |
|------|-------|
| `static_xml.json` | Parsed XML layouts: elements, layout trees, string resources |
| `source_findings.json` | Raw source-scan hits: event registrations, id dispatchers, visibility controls, inflates |
| `function_symbols.json` | Every function/method symbol (id, class, file, line) |
| `call_graph.json` | Caller→callee edges + symbols + stats |
| `ground_truth.json` | XML elements joined with bound behaviors, conditional visibility, dynamic gaps, non-UI bindings, unmatched |
| `navigation_graph.json` | Screen nodes (activity/dialog) + navigation edges + class→layout map |
| `navigation_candidates.json` | Raw L1 navigation candidates before resolution |
| `fragments.json` | Detected fragments and host coverage |
| `dynamic_ui.json` | Programmatically created views + adapter→item-layout mappings |
| `behavior_chains.json` | Event → handler → effect chains + lifecycle hooks |
| `non_ui_components.json` | Orphan behaviors grouped by non-UI owning class (service / app-widget / receiver / listener…) with HarmonyOS ability hints, plus `used_by` (caller classes / screens that drive each component, from the call graph) |
| `screen_index.json` | Compact per-screen overview for LLM orientation |
| `manifest.json` | Stage-0 provenance: tool git commit + sha256/byte index of every artifact (not the AndroidManifest) |
| `ui_dag.json` | UI DAG assembled from the launcher screen |
| `ui_effect_paths.json` | Enumerated UI effect paths |
| `ui_paths*.json` | Path enumeration in flat / legacy / report / enumerated / coverage-report forms |

Sub-directories:

| Dir | Holds |
|-----|-------|
| `specs/` | One `<layout>_spec.json` per screen — the per-screen migration spec. Screens driven by a non-UI component also carry a `non_ui_dependencies` back-reference to it |
| `app_model/` | Graph-shaped app model: `index.json` (counts + file pointers), `features/` (one per feature node), `screens/` (one per screen), `paths/` (enumerated paths), `references/` (nav edges, UI-point index) |

## Stage 1 — `intermediate/1_android_facts/`

| File | Holds |
|------|-------|
| `android_facts.v1.json` | All Stage-0 facts normalized into one schema-validated model (the canonical input for later stages) |

## Stage 2 — `intermediate/2_framework_map/`

| File | Holds |
|------|-------|
| `framework_map.v1.json` | Android framework/API usages mapped to their HarmonyOS counterparts |

## Stage 3 — `intermediate/3_harmony_arch/`

| File | Holds |
|------|-------|
| `harmony_arch.v1.json` | Projected HarmonyOS architecture: modules, abilities, routes |

## Stage 4 — `intermediate/4_scaffold/`

Written only with `--emit-scaffold-files`; otherwise the plan is printed to stdout as a dry-run.

| File | Holds |
|------|-------|
| `SCAFFOLD_PLAN.txt` | Deterministic HarmonyOS scaffold plan (modules, abilities, route placeholders) |

## Stage 5 — `intermediate/5_feature_tree/`

| File | Holds |
|------|-------|
| `feature_tree.v1.json` | Screens grouped into logical `feature:*` nodes (UI / behavior / implementation anchors) |
| `feature_spec_evidence.json` | Evidence backing each feature grouping |
| `taxonomy_report.json` | Mined feature counts, matched screens, remaining unmatched screens |
| `verify_report.json` | Cross-checks of the feature tree against the facts |

## Stage 6 — `viewer/`

| Dir | Holds |
|-----|-------|
| `viewer/` | Self-contained interactive HTML view of the feature tree (optional stage, not in the default order) |

## Stage 7 — `agent_bundle.v1.json` (output root)

| File | Holds |
|------|-------|
| `agent_bundle.v1.json` | The one agent-consumable migration bundle assembled from the feature tree, framework map, harmony arch, and facts. This is the file to hand off. |
