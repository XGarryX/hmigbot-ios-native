# Bundled static analysis (legacy: spec-tools-for-opencode)

This directory is **vendored** into `harmony-migration-toolkit` so Stage 0 does not depend on a sibling checkout.

- **Entry**: `main.py`
  - Standalone: `python main.py <android_project_root>` writes to `./output/`.
  - Explicit output: `python main.py <android_project_root> --out /tmp/static_scan`.
- **Output isolation**: when run through `pipeline.py`, Stage 0 passes a per-run temporary `--out` directory under `<output>/intermediate/`, mirrors that tree into `intermediate/0_android_facts/`, then removes the temporary directory. This prevents stale files from `./output/` leaking across projects.
- **Cache mode**: `pipeline.py --skip-spec-tools` still reuses `./output/` (or `--spec-tools-root .../output`) for debugging.

Upstream logic originated from `spec-tools-for-opencode`; prefer editing here so releases stay self-contained. Optional override: `python pipeline.py ... --spec-tools-root /other/copy`.
