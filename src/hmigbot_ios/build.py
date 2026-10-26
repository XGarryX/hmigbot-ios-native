"""Explicit target build provider with a persisted log and artifact hashes."""
from datetime import datetime, timezone
import os
from pathlib import Path
import shutil
import subprocess

from .core import source_snapshot
from .core import SCHEMA, MigrationError, atomic_write, digest, json_bytes, snapshot, write_new_tree
from .generate import verify


def build_target(config, output: Path, timeout=300):
    if config["source"]["platform"] != "ios":
        raise MigrationError("Delegate Android builds to the existing HMigBot workflow")
    target = Path(config["target"]["root"])
    source = Path(config["source"]["root"])
    output = output.resolve()
    if any(output.is_relative_to(p) or p.is_relative_to(output) for p in (source, target)):
        raise MigrationError("Build evidence output must be separate from source and target")
    if output.exists() and any(output.iterdir()):
        raise MigrationError("Build evidence output already exists")
    if not (target / "build-profile.json5").is_file():
        raise MigrationError("Target has no build-profile.json5")
    generated_integrity = None
    if (target / "migration/generation.json").exists():
        try:
            generated_integrity = verify(source, target)
        except (MigrationError, OSError, ValueError, KeyError, TypeError) as exc:
            generated_integrity = {'status': 'unverified', 'error': str(exc)}
    tool = config.get("tools", {})
    hvigor = tool.get("hvigorw") or shutil.which("hvigorw")
    if not hvigor or not Path(hvigor).is_file():
        raise MigrationError("Configure tools.hvigorw with the actual executable/wrapper path")
    command = [hvigor]
    if Path(hvigor).suffix.lower() in {".bat", ".cmd", ".js"}:
        # Bypass cmd.exe quoting entirely; official bat wrappers delegate to this JS file.
        script = Path(hvigor).with_suffix(".js")
        node = tool.get("node") or shutil.which("node")
        if not script.is_file() or not node or not Path(node).is_file():
            raise MigrationError("Configure tools.node and use a wrapper with adjacent hvigorw.js")
        command = [node, str(script)]
    import re
    build = config.get('build', {})
    module, module_target, product = (build.get(k, d) for k, d in (('module', 'entry'), ('module_target', 'default'), ('product', 'default')))
    if not all(isinstance(v, str) and re.fullmatch(r'[A-Za-z0-9_-]+', v) for v in (module, module_target, product)):
        raise MigrationError('Build module, module_target and product must be identifiers')
    command += ["--mode", "module", "-p", f"module={module}@{module_target}", "-p", f"product={product}", "assembleHap", "--no-daemon"]
    env = os.environ.copy()
    if tool.get("deveco_sdk"):
        env["DEVECO_SDK_HOME"] = tool["deveco_sdk"]
    if tool.get("node"):
        env["NODE_HOME"] = str(Path(tool["node"]).parent)
    started = datetime.now(timezone.utc).isoformat()
    inputs = snapshot(target)
    from .quality_views import _summary_inputs, target_inputs
    product_hashes = target_inputs(target)
    contract_hashes, baseline = (_summary_inputs(target) if (target / '.migbot/config.json').exists()
                                 else ({}, {'status': 'not_established', 'missing_inputs': ['.migbot/config.json']}))
    contract_binding = {'status': 'input_bound' if baseline.get('status') == 'pending_review' and not baseline.get('input_error') else 'unbound',
                        'baseline': baseline, 'acceptance_verified': False,
                        'scope': 'Current SDK build diagnostics are independent of authored migration-contract acceptance.'}
    if generated_integrity and (generated_integrity.get('status') == 'unverified'
            or any(not row.get('passed') for row in generated_integrity.get('checks', []))):
        contract_binding.update(status='unbound', generation_error='Generated-source binding is missing or stale; reconcile before claiming migration acceptance.')
    source_error = None
    try:
        source_before = source_snapshot(source)['sha256']
    except (MigrationError, OSError) as exc:
        source_before, source_error = None, str(exc)
    try:
        result = subprocess.run(command, cwd=target, env=env, capture_output=True, timeout=timeout, shell=False)
        code, stdout, stderr = result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired as exc:
        code, stdout, stderr = None, exc.stdout or b"", exc.stderr or b""
    artifacts = []
    if code == 0:
        for path in sorted((target / module / "build").rglob("*.hap")):
            artifacts.append({"path": str(path.relative_to(target).as_posix()), "sha256": digest(path.read_bytes()),
                              "bytes": path.stat().st_size})
    try:
        source_after = source_snapshot(source)['sha256']
    except (MigrationError, OSError) as exc:
        source_after, source_error = None, str(exc)
    source_changed = source_before != source_after if source_before is not None and source_after is not None else None
    source_binding = {'status': 'unavailable' if source_changed is None else 'stale' if source_changed else 'bound',
                      'source_before_sha256': source_before, 'source_after_sha256': source_after,
                      'verification_scope': 'Source identity only; target build diagnostics do not prove migration equivalence.'}
    if source_error is not None:
        source_binding['error'] = source_error
    if source_binding['status'] != 'bound':
        contract_binding.update(status='unbound', source_binding=source_binding['status'])
    hvigor_success = b'BUILD SUCCESSFUL' in stdout + stderr
    report = {"schema_version": SCHEMA, "started_at": started, "command": command,
              "target_project": str(target.resolve()), "target_input_hashes": product_hashes,
              "spec_input_hashes": contract_hashes,
              "contract_binding": contract_binding,
              "target_input_sha256": inputs["sha256"], "target_after_sha256": snapshot(target)['sha256'],
              "source_sha256": source_before, "source_changed": source_changed,
              "source_binding": source_binding,
              "generation_integrity": generated_integrity,
              "exit_code": code, "artifacts": artifacts,
              "hvigor_success_marker": hvigor_success,
              "status": "build_passed" if code == 0 and artifacts and hvigor_success and source_changed is not True else "build_failed",
              "timeout": code is None, "behavior": "not_verified", "device_install": "not_run"}
    # Retain real logs first. The accepted build receipt is published only after
    # checking for contradictory compiler errors, even when a wrapper exits zero.
    write_new_tree(output, {"stdout.log": stdout, "stderr.log": stderr})
    from .harmony_diagnostics import analyze, save_report
    diagnostics = analyze(output / 'stdout.log', output / 'stderr.log', code,
                          target={'module': module, 'module_target': module_target, 'product': product})
    diagnostic_path = save_report(diagnostics, output / 'diagnostics.json')
    report['diagnostics'] = {'path': 'diagnostics.json', 'sha256': digest(diagnostic_path.read_bytes())}
    if not diagnostics['build_command_passed']:
        report['status'] = 'build_failed'
    atomic_write(output / 'build.json', json_bytes(report))
    return report
