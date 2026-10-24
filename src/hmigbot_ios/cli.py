from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from . import __version__
from .core import MigrationError, json_bytes, load_config, read_json, write_json, write_new_tree
from .analyze import analyze, migration_plan, render_report
from .generate import generate, verify
from .environment import preflight, audit_baseline
from .evidence import pack, validate, KINDS
from .build import build_target
from .contracts import validate_facts
from .atoms import run_atom, OPERATIONS
from .workflow import initialize, pipeline_status, compare_behavior
from .tasks import create_task, check_task
from . import cloud
from .iphone import inspect_ipa
from .capture import capture
from . import hmigbot
from . import doctor
from .cli_output import configure_utf8, emit_json


def parser():
    cli = argparse.ArgumentParser(description="HMigBot native iOS adapter: inventory, plans and conservative ArkUI drafts")
    cli.add_argument("--version", action="version", version=__version__)
    sub = cli.add_subparsers(dest="command", required=True)
    binding = sub.add_parser('hmigbot-bind', help='Pin original standalone HMigBot target skills without changing them')
    binding.add_argument('--root', type=Path, required=True)
    binding.add_argument('--output', type=Path, required=True)
    binding_check = sub.add_parser('hmigbot-check', help='Check original skill and reference fingerprints')
    binding_check.add_argument('--binding', type=Path, required=True)
    draft = sub.add_parser('migration-contract', help='Discover iOS candidates for source-semantic contracts; generates no code')
    draft.add_argument('--source', type=Path, required=True)
    draft.add_argument('--output', type=Path, required=True)
    handoff_cmd = sub.add_parser('hmigbot-handoff', help='Route ready source contracts to real original HarmonyOS skills')
    for name in ('source', 'target', 'contract', 'binding', 'output'):
        handoff_cmd.add_argument('--' + name, type=Path, required=True)
    handoff_cmd.add_argument('--unit', action='append', help='Select units with all their dependencies; defaults to all')
    handoff_check = sub.add_parser('hmigbot-handoff-check', help='Reject changed source, skill references or prepared task artifacts')
    handoff_check.add_argument('--source', type=Path, required=True)
    handoff_check.add_argument('--handoff', type=Path, required=True)
    init = sub.add_parser("init", help="Write source-neutral configuration without changing the source")
    init.add_argument("--source", type=Path, required=True)
    init.add_argument("--target", type=Path, required=True)
    init.add_argument("--output", type=Path, required=True)
    check = sub.add_parser("preflight", help="Check prerequisites for one action")
    check.add_argument("--config", type=Path, required=True)
    check.add_argument("--action", choices=["scan", "source-build", "target-build", "target-device"], default="scan")
    scan = sub.add_parser("scan", help="Inventory native source and create a migration plan")
    scan.add_argument("--source", type=Path, required=True)
    scan.add_argument("--output", type=Path, required=True)
    gen = sub.add_parser("generate", help="Create a new HarmonyOS draft for completely recognized SwiftUI pages")
    gen.add_argument("--source", type=Path, required=True)
    gen.add_argument("--output", type=Path, required=True)
    gen.add_argument("--sdk", required=True)
    gen.add_argument("--min-sdk", required=True)
    gen.add_argument("--model-version", required=True)
    gen.add_argument("--bundle-name", required=True)
    gen.add_argument("--entry-view")
    gen.add_argument("--resource-bundle", action="append", type=Path, default=[])
    scaffold = sub.add_parser('scaffold', help='Create a native target project for any iOS source; migrates no application behavior')
    for name in ('source', 'output'):
        scaffold.add_argument('--' + name, type=Path, required=True)
    for name in ('sdk', 'min-sdk', 'model-version', 'bundle-name'):
        scaffold.add_argument('--' + name, required=True)
    ver = sub.add_parser("verify", help="Check source freshness and generated-file integrity, not behavioral equivalence")
    ver.add_argument("--source", type=Path, required=True)
    ver.add_argument("--target", type=Path, required=True)
    build = sub.add_parser("build-target", help="Run a configured Hvigor provider and retain build evidence")
    build.add_argument("--config", type=Path, required=True)
    build.add_argument("--output", type=Path, required=True)
    build.add_argument("--timeout", type=int, default=300)
    diag = sub.add_parser('diagnose-build', help='Diagnose captured Harmony build logs without modifying the project')
    diag.add_argument('--stdout', type=Path)
    diag.add_argument('--stderr', type=Path)
    diag.add_argument('--returncode', type=int, help='Actual process exit code; omit only when unknown or timed out')
    diag.add_argument('--output', type=Path, required=True)
    for identity in ('module', 'module-target', 'product'):
        diag.add_argument('--' + identity)
    evidence = sub.add_parser("evidence-pack", help="Package already captured source evidence")
    evidence.add_argument("--source", type=Path, required=True)
    evidence.add_argument("--artifacts", type=Path, required=True)
    evidence.add_argument("--output", type=Path, required=True)
    evidence.add_argument("--kind", choices=sorted(KINDS), required=True)
    evidence.add_argument("--provider", required=True)
    imp = sub.add_parser("evidence-check", help="Validate portable source evidence without trusting its claims")
    imp.add_argument("--source", type=Path, required=True)
    imp.add_argument("--bundle", type=Path, required=True)
    audit = sub.add_parser("audit-hmigbot", help="Record the standalone HMigBot 1.6.1 execution baseline")
    audit.add_argument("--root", type=Path, required=True)
    audit.add_argument("--output", type=Path, required=True)
    sub.add_parser("capabilities", help="Show implemented scopes and remaining atoms")
    contract = sub.add_parser("check-facts", help="Validate source-neutral fact IDs, provenance and anchor consistency")
    contract.add_argument("--input", type=Path, required=True)
    atom = sub.add_parser("atom", help="Run one independently testable native-source operation")
    atom.add_argument("operation", choices=sorted(OPERATIONS))
    atom.add_argument("--source", type=Path, required=True)
    atom.add_argument("--output", type=Path, required=True)
    atom.add_argument("--input", type=Path)
    atom.add_argument("--provider-config", type=Path)
    atom.add_argument("--default-locale")
    start = sub.add_parser('pipeline-init', help='Create a source-bound five-stage migration workspace')
    start.add_argument('--source', type=Path, required=True)
    start.add_argument('--run', type=Path, required=True)
    status = sub.add_parser('pipeline-status', help='Check current stages from artifacts; never fabricate done markers')
    status.add_argument('--run', type=Path, required=True)
    compare = sub.add_parser('compare-behavior', help='Compare independent source oracle cases with target observations')
    for name in ('source', 'target', 'oracle-bundle', 'observations', 'output'):
        compare.add_argument('--' + name, type=Path, required=True)
    task = sub.add_parser('task-create', help='Create a source-bound packet for one agent-executed atom')
    task.add_argument('--atom', required=True)
    task.add_argument('--source', type=Path, required=True)
    task.add_argument('--output', type=Path, required=True)
    check_task_cmd = sub.add_parser('task-check', help='Validate agent task artifact provenance and integrity')
    check_task_cmd.add_argument('--source', type=Path, required=True)
    check_task_cmd.add_argument('--task', type=Path, required=True)
    cp = sub.add_parser('cloud-prepare', help='Prepare a private-repository macOS build bundle without uploading')
    for name in ('source', 'config', 'output'):
        cp.add_argument('--' + name, type=Path, required=True)
    cd = sub.add_parser('cloud-dispatch', help='Run a prepared workflow in an explicit private GitHub repository')
    cd.add_argument('--gh', default='gh')
    cd.add_argument('--repository', required=True)
    cd.add_argument('--ref', required=True)
    cd.add_argument('--workflow', default='hmigbot-ios.yml')
    cf = sub.add_parser('cloud-fetch', help='Download a selected run and validate source/artifact hashes')
    cf.add_argument('--gh', default='gh')
    cf.add_argument('--repository', required=True)
    cf.add_argument('--run-id', required=True)
    cf.add_argument('--source', type=Path, required=True)
    cf.add_argument('--output', type=Path, required=True)
    ipa = sub.add_parser('ipa-inspect', help='Check IPA device architecture, bundle IDs and ZIP integrity before local signing')
    ipa.add_argument('--ipa', type=Path, required=True)
    cap = sub.add_parser('capture', help='Execute an explicit source evidence provider and preserve real logs')
    for name in ('source', 'provider-config', 'output'):
        cap.add_argument('--' + name, type=Path, required=True)
    cap.add_argument('--kind', choices=sorted(KINDS), required=True)
    doc = sub.add_parser('doctor', help='Read-only environment diagnostic: what works, what is missing, next actions')
    doc.add_argument('--project', type=Path, default=Path('.'), help='Project root to inspect (default: cwd)')
    doc.add_argument('--config', type=Path, help='Optional migration config to validate')
    doc.add_argument('--node', help='Explicit node path')
    doc.add_argument('--hvigor', help='Explicit hvigorw path')
    doc.add_argument('--ohpm', help='Explicit ohpm path')
    doc.add_argument('--java', help='Explicit java path')
    doc.add_argument('--sdk', help='Explicit HarmonyOS SDK path')
    doc.add_argument('--text', action='store_true', help='Also print human-readable report to stderr')
    return cli


def dispatch(args):
    command = args.command
    if command == 'hmigbot-bind':
        return hmigbot.bind(args.root, args.output)
    if command == 'hmigbot-check':
        binding = hmigbot.check_binding(args.binding)
        return {'status': 'binding_valid', 'root': binding['root'], 'skills': len(binding['skills']), 'execution': 'not_run'}
    if command == 'migration-contract':
        return hmigbot.contract_draft(args.source, args.output)
    if command == 'hmigbot-handoff':
        return hmigbot.handoff(args.source, args.target, args.contract, args.binding, args.output, args.unit)
    if command == 'hmigbot-handoff-check':
        return hmigbot.check_handoff(args.source, args.handoff)
    if command == 'capture':
        return capture(args.source, args.provider_config, args.output, args.kind)
    if command == 'ipa-inspect':
        return inspect_ipa(args.ipa)
    if command == 'cloud-prepare':
        return cloud.prepare(args.source, args.config, args.output)
    if command == 'cloud-dispatch':
        return cloud.dispatch(args.gh, args.repository, args.ref, args.workflow)
    if command == 'cloud-fetch':
        return cloud.fetch(args.gh, args.repository, args.run_id, args.source, args.output)
    if command == 'pipeline-init':
        return initialize(args.source, args.run)
    if command == 'pipeline-status':
        return pipeline_status(args.run)
    if command == 'compare-behavior':
        return compare_behavior(args.source, args.target, args.oracle_bundle, args.observations, args.output)
    if command == 'task-create':
        return create_task(args.atom, args.source, args.output)
    if command == 'task-check':
        return check_task(args.source, args.task)
    if command == "atom":
        result = run_atom(args.operation, args.source, args.output, provider_config=args.provider_config,
                          input_path=args.input, default_locale=args.default_locale)
        return {"operation": args.operation, "status": result["status"], "issues": len(result["issues"]),
                "output": str(args.output.resolve()), "application_migration": "not_verified"}
    if command == "init":
        output = args.output.resolve()
        if output.exists():
            raise MigrationError("Configuration already exists; edit it explicitly")
        if output.is_relative_to(args.source.resolve()):
            raise MigrationError("Keep migration config outside the source tree")
        config = {"schema_version": 2, "source": {"platform": "ios", "root": str(args.source.resolve())},
                  "target": {"platform": "harmonyos", "root": str(args.target.resolve())}, "tools": {}}
        # Validate before writing; no temporary invalid configuration is left behind.
        if args.source.resolve().is_relative_to(args.target.resolve()) or args.target.resolve().is_relative_to(args.source.resolve()):
            raise MigrationError("Source and target directories must not overlap")
        if not args.source.is_dir():
            raise MigrationError("Source directory does not exist")
        write_json(output, config)
        return {"config": str(output), "status": "created"}
    if command == "preflight":
        return preflight(load_config(args.config.resolve()), args.action)
    if command == "scan":
        source, output = args.source.resolve(), args.output.resolve()
        if source.is_relative_to(output) or output.is_relative_to(source):
            raise MigrationError("Scan output must not overlap source")
        report = analyze(source)
        plan = migration_plan(report)
        write_new_tree(output, {"facts.json": json_bytes(report), "plan.json": json_bytes(plan),
                                "report.md": render_report(report, plan).encode("utf-8")})
        return {"output": str(output), "inventory": report["inventory"], "tasks": len(plan["tasks"]),
                "convertible_pages": sum(p["status"] == "convertible_subset" for p in report["pages"]),
                "status": "analysis_complete", "migration_status": "not_verified"}
    if command in {"generate", "scaffold"}:
        manifest = generate(args.source, args.output, sdk=args.sdk, min_sdk=args.min_sdk,
                            model_version=args.model_version, bundle_name=args.bundle_name, entry_view=getattr(args, 'entry_view', None),
                            resource_bundles=getattr(args, 'resource_bundle', []), scaffold_only=command == 'scaffold')
        return {"output": str(args.output.resolve()), "pages": len(manifest["generated_pages"]),
                "status": manifest["status"], "app_migration": "incomplete", "target_build": "not_run"}
    if command == "verify":
        return verify(args.source.resolve(), args.target.resolve())
    if command == "build-target":
        if args.timeout < 1:
            raise MigrationError("Build timeout must be positive")
        return build_target(load_config(args.config.resolve()), args.output, args.timeout)
    if command == "evidence-pack":
        return pack(args.source, args.artifacts, args.output, args.kind, args.provider)
    if command == 'diagnose-build':
        from . import harmony_diagnostics as diagnostics
        target = {name: getattr(args, name) for name in ('module', 'module_target', 'product')
                  if getattr(args, name) is not None}
        report = diagnostics.analyze(args.stdout, args.stderr, args.returncode, target=target or None)
        path = diagnostics.save_report(report, args.output)
        from .core import digest as log_digest
        return {key: report[key] for key in ('status', 'build_command_passed', 'functional_verified', 'ui_verified', 'summary')} | {
            'report': str(path.resolve()), 'sha256': log_digest(path.read_bytes())}
    if command == "evidence-check":
        return validate(args.source.resolve(), args.bundle.resolve())
    if command == "audit-hmigbot":
        if args.output.exists():
            raise MigrationError("Baseline file already exists")
        result = audit_baseline(args.root.resolve())
        write_json(args.output, result)
        return result
    if command == "capabilities":
        from .core import safe_child
        result = read_json(Path(__file__).with_name("capabilities.json"))
        package = Path(__file__).resolve().parent
        canonical = read_json(safe_child(package, result['canonical_catalog']))
        entries = canonical['capabilities']
        unique = {entry['id'] for entry in entries if entry.get('independent') is True}
        if len(unique) != len(entries) or canonical['count'] != len(unique):
            raise MigrationError('Canonical semantic capability catalog is duplicated or inconsistent')
        return {**result, 'independent_capability_count': len(unique), 'canonical_capabilities': entries}
    if command == "check-facts":
        report = validate_facts(read_json(args.input))
        return {"contract_valid": True, "facts": len(report["facts"]), "behavior": "not_verified"}
    if command == "doctor":
        report = doctor.doctor(args.project, config=args.config, node_path=args.node,
                               hvigor_path=args.hvigor, ohpm_path=args.ohpm,
                               java_path=args.java, sdk_path=args.sdk)
        if args.text:
            print(doctor.render_text(report), file=sys.stderr)
        return report
    raise MigrationError("Unknown command")


def main(argv=None):
    configure_utf8(sys.stdout, sys.stderr)
    try:
        args = parser().parse_args(argv)
        result = dispatch(args)
        emit_json(result)
        if result.get("integrity_passed") is False or result.get("status") in {"unavailable", "build_failed", "capture_failed", "observations_differ", "stale_source", 'fail_with_errors', 'fail_unparsed', 'conflicting_build_evidence'}:
            return 3
        return 0
    except (MigrationError, OSError, UnicodeError, RecursionError) as exc:
        emit_json({"status": "error", "error": str(exc)}, stream=sys.stderr, indent=None)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
