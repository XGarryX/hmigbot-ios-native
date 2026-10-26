# harmony-migration-toolkit

Deterministic **Android → HarmonyOS migration IR** pipeline. Stage 0 runs the **bundled** static analyzer under [`bundled_spec_tools/`](bundled_spec_tools/) (vendored from the former `spec-tools-for-opencode` tree), then emits one agent-consumable migration bundle plus reproducible intermediate artifacts.

## Project structure

```
harmony-migration-toolkit/
├── pipeline.py                  # entry point — orchestrates all stages
├── ARCHITECTURE.md              # bundled_spec_tools architecture reference (field details, algorithms, coverage data)
├── requirements.txt             # Python dependencies
├── stages/                      # stage implementations
│   ├── stage0_run_spec_tools.py # Stage 0 — invoke bundled static analyzer
│   ├── stage1_normalize.py      # Stage 1 — normalize facts into single JSON
│   ├── stage2_framework_map.py  # Stage 2 — Android API → HarmonyOS mapping
│   ├── stage3_architecture.py   # Stage 3 — projected HarmonyOS architecture
│   ├── stage4_emit_scaffold.py  # Stage 4 — scaffold plan emission
│   ├── build_android_facts.py   # facts model builder
│   ├── build_feature_tree.py    # feature tree construction
│   ├── build_framework_map.py   # framework mapping logic
│   ├── build_harmony_arch.py    # harmony architecture projection
│   ├── export_agent_bundle.py   # Stage 7 — final agent bundle export
│   ├── export_feature_tree_view.py  # Stage 6 — HTML viewer export
│   ├── feature_taxonomy_miner.py    # automatic feature taxonomy mining
│   ├── feature_tree_taxonomy.py     # taxonomy application
│   └── feature_tree_reports.py      # evidence & verification reports
├── bundled_spec_tools/          # vendored Stage 0 static analyzer
│   ├── main.py                  # standalone entry: python main.py <android_root>
│   ├── generate_specs.py        # per-screen spec generation
│   ├── extractors/              # all source/XML/AST extractors
│   │   ├── xml_extractor.py         # layout XML parsing
│   │   ├── source_extractor.py      # Kotlin/Java source scanning
│   │   ├── class_parser.py          # class/method symbol extraction
│   │   ├── navigation_extractor.py  # screen navigation detection
│   │   ├── fragment_detector.py     # Fragment host/attachment detection
│   │   ├── behavior_chain_extractor.py  # event→handler→effect chains
│   │   ├── dynamic_ui_extractor.py  # programmatic view detection
│   │   ├── function_graph_extractor.py  # call graph construction
│   │   ├── bytecode_navigation.py   # .class bytecode nav analysis
│   │   ├── ground_truth_builder.py  # XML ↔ behavior join
│   │   ├── non_ui_components.py     # services/receivers/widgets
│   │   ├── app_model_builder.py     # graph-shaped app model assembly
│   │   ├── ui_dag_assembler.py      # UI DAG from launcher screen
│   │   └── ...                      # additional extraction modules
│   └── verification/            # post-scan verification
│       ├── bytecode_verifier.py     # verify navigation via bytecode
│       ├── layout_verifier.py       # verify layout completeness
│       ├── manifest_verifier.py     # verify manifest coverage
│       └── report.py                # verification report assembly
├── schemas/                     # JSON Schema Draft 2020-12
│   ├── android_facts.v1.schema.json
│   ├── framework_map.v1.schema.json
│   ├── harmony_arch.v1.schema.json
│   ├── feature_tree.v1.schema.json
│   └── agent_bundle.v1.schema.json
├── data/
│   └── framework_map/rules.yaml # Android → HarmonyOS mapping rules
├── docs/
│   ├── PIPELINE_OUTPUTS.md      # directory-level output index
│   ├── FEATURE_TREE_AND_VIEWER_DESIGN.md  # feature tree IR design
│   └── 工具说明.md               # plain-language tool overview (Chinese)
├── tests/                       # pytest test suite
│   └── test_pipeline.py
└── fixtures/                    # test fixtures
    ├── minimal_android/         # minimal Android project for integration tests
    └── minimal_facts/           # pre-built facts for unit tests
```

## Requirements

- Python 3.10+
- `pip install -r requirements.txt`

> **tree-sitter (推荐但可选)**: 提供 AST 级源代码解析，用于精确的类继承链检测、Fragment 声明和调用图构建。如果未安装（或解析器加载失败），各提取器将自动降级到正则匹配模式——产出仍然可用，但 Fragment 挂载点、导航节点、调用图等指标会明显偏低。安装命令：`pip install tree-sitter tree-sitter-language-pack`。若确定不需要 AST 精度，可跳过。

## Usage

```bash
cd harmony-migration-toolkit
pip install -r requirements.txt

# Full run
python pipeline.py --android-root /path/to/android/project
```

The default full run executes all deterministic stages needed for agent handoff. The main file to inspect is:

```text
/path/to/android/project/harmony_migration_out/agent_bundle.v1.json
```

Stage 0 can also be run standalone (9 sub-steps: XML → source → ground truth → navigation → fragments → dynamic UI → behavior chains → UI DAG → per-screen specs):

```bash
python bundled_spec_tools/main.py /path/to/android/project --out /path/to/output
python bundled_spec_tools/main.py /path/to/android/project --out /path/to/output --validate  # with verification report
```

Detailed reproducible artifacts live under `/path/to/android/project/harmony_migration_out/intermediate/`.

To write output somewhere else, pass `--out`:

```bash
python pipeline.py --android-root /path/to/android/project --out /path/to/output
```

### Stages

| Stage | Output |
|-------|--------|
| 0 | `<output>/intermediate/0_android_facts/` — isolated full scan output mirror + normalized paths + `manifest.json` |
| 1 | `<output>/intermediate/1_android_facts/android_facts.v1.json` |
| 2 | `<output>/intermediate/2_framework_map/framework_map.v1.json` |
| 3 | `<output>/intermediate/3_harmony_arch/harmony_arch.v1.json` |
| 4 | Dry-run plan to stdout, or `<output>/intermediate/4_scaffold/` with `--emit-scaffold-files` |
| 5 | `<output>/intermediate/5_feature_tree/feature_tree.v1.json` + `feature_spec_evidence.json` + `verify_report.json` |
| 6 | Optional debug `<output>/viewer/` — static feature tree viewer and sidecar JSON |
| 7 | `<output>/agent_bundle.v1.json` — final agent-consumable migration bundle |

For a directory-level index of every file each stage writes, see [docs/PIPELINE_OUTPUTS.md](docs/PIPELINE_OUTPUTS.md).

The default output directory is `<android-root>/harmony_migration_out`. The default stage order is `0,1,2,3,5,4,7`: feature tree generation runs before scaffold emission and final bundle export. The root output is intentionally small: `agent_bundle.v1.json` is the deliverable, while deterministic debugging artifacts live under `intermediate/`.

### Advanced / Debug

Most users should use the full run above. These flags are mainly for tests, debugging, or rerunning part of an existing output:

```bash
# Debug/cache mode: reuse an existing bundled_spec_tools/output without rescanning
python pipeline.py --android-root /path/to/android/project --skip-spec-tools

# Run selected stages only
python pipeline.py --android-root /path/to/android/project --stages 5,7

# Generate the optional HTML debug viewer
python pipeline.py --android-root /path/to/android/project --stages 0,1,2,3,5,6
```

By default, Stage 0 writes the bundled scanner output to a per-run temporary directory under `<output>/intermediate/`, then mirrors it into `0_android_facts/`. The shared `bundled_spec_tools/output/` directory is only used when running `bundled_spec_tools/main.py` standalone or when explicitly passing `--skip-spec-tools`.

### Feature taxonomy

Stage 5 groups screens into logical `feature:*` nodes with deterministic automatic mining from screen names, layouts, packages, source paths, and navigation affinity. There is **no** bundled product taxonomy; pass `--taxonomy` (base YAML) and/or repeated `--taxonomy-overlay` only when you want explicit rules on top of the generated grouping.

Stage 5 writes `<output>/intermediate/5_feature_tree/taxonomy_report.json`, including generated feature counts, matched screen counts, and any remaining `unmatched_screens`.

## Documentation

| Document | Content |
|----------|---------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Technical reference for `bundled_spec_tools` — field definitions, algorithms, coverage data |
| [docs/工具说明.md](docs/工具说明.md) | Plain-language overview of the tool: what it does, how to use it, what it outputs (Chinese) |
| [docs/PIPELINE_OUTPUTS.md](docs/PIPELINE_OUTPUTS.md) | Directory-level index of all pipeline output files |
| [docs/FEATURE_TREE_AND_VIEWER_DESIGN.md](docs/FEATURE_TREE_AND_VIEWER_DESIGN.md) | Design for the feature tree IR, screen edges, Harmony projection, and HTML viewer |

## LLM boundary (contract)

**Deterministic tools own:** merging XML + source facts (via `bundled_spec_tools/`), Gradle/manifest parsing, framework **mapping tables** under [data/framework_map/rules.yaml](data/framework_map/rules.yaml), IR JSON and schema validation.

**LLM may assist:** filling `implementation_notes`, ArkTS/ArkUI drafts, Compose-heavy UI, JNI/NAPI ports — only via structured outputs with schemas defined in [schemas/](schemas/).

**LLM must not:** silently change navigation graphs, invent screens, or override `rules_version` mappings without a human-reviewed table change.

## Schemas

JSON Schema Draft 2020-12 under [schemas/](schemas/): `android_facts.v1.schema.json`, `framework_map.v1.schema.json`, `harmony_arch.v1.schema.json`, `feature_tree.v1.schema.json`, `agent_bundle.v1.schema.json`.

## Tests

```bash
pip install -r requirements.txt
pytest tests/ -q
```
