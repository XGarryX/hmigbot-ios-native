"""Portable source evidence bundles. Integrity is not authenticity or a test pass."""
from pathlib import Path

from .core import SCHEMA, MigrationError, digest, json_bytes, read_json, safe_child, snapshot, source_files, write_new_tree

KINDS = {"source_build", "source_build_settings", "source_tests", "source_scenario", "source_screenshot", "source_snapshot",
         "source_trace", "source_network", "source_data", "source_debug", "source_performance"}


def pack(source: Path, artifacts: Path, output: Path, kind: str, provider: str):
    source, artifacts, output = source.resolve(), artifacts.resolve(), output.resolve()
    if kind not in KINDS or not provider.strip():
        raise MigrationError("Specify a source evidence kind and the capturing provider/version")
    for input_root in (source, artifacts):
        if output.is_relative_to(input_root) or input_root.is_relative_to(output):
            raise MigrationError("Evidence output must not overlap an input directory")
    files = source_files(artifacts)
    if not files:
        raise MigrationError("No evidence artifacts supplied")
    payload = {"artifacts/" + p.relative_to(artifacts).as_posix(): p.read_bytes() for p in files}
    manifest = {"schema_version": SCHEMA, "source_sha256": snapshot(source)["sha256"],
                "kind": kind, "provider": provider, "origin": "user_supplied_source_evidence",
                "claim_validation": "not_performed", "artifacts": {n: digest(b) for n, b in payload.items()}}
    payload["manifest.json"] = json_bytes(manifest)
    write_new_tree(output, payload)
    return manifest


def validate(source: Path, bundle: Path):
    from .contracts import validate_file_map
    manifest = read_json(bundle / "manifest.json")
    if not isinstance(manifest, dict) or manifest.get("schema_version") != SCHEMA or manifest.get("kind") not in tuple(KINDS):
        raise MigrationError("Unsupported evidence contract")
    if (not isinstance(manifest.get("provider"), str) or not manifest["provider"].strip()
            or manifest.get("origin") != "user_supplied_source_evidence"
            or manifest.get("claim_validation") != "not_performed"):
        raise MigrationError("Evidence requires provider, source origin and unvalidated-claim metadata")
    if manifest.get("source_sha256") != snapshot(source)["sha256"]:
        raise MigrationError("Evidence source fingerprint does not match current source")
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, dict) or not artifacts:
        raise MigrationError("Evidence has no artifacts")
    validate_file_map(artifacts)
    for name, expected in artifacts.items():
        if not name.startswith("artifacts/"):
            raise MigrationError("Evidence file must be under artifacts/")
        path = safe_child(bundle, name)
        if not path.is_file() or digest(path.read_bytes()) != expected:
            raise MigrationError(f"Missing or modified evidence: {name}")
    return {"schema_version": SCHEMA, "integrity_passed": True, "source_sha256": manifest["source_sha256"],
            "kind": manifest["kind"], "artifact_count": len(artifacts),
            "claim_validation": "not_performed", "behavior_equivalence": "not_verified"}
