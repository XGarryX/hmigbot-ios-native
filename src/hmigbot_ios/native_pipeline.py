"""iOS source checks for the original a2h spec tree; no model or pipeline scheduler."""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import re
import sys
import shutil
import uuid

from .analyze import analyze
from .core import source_snapshot
from .core import MigrationError, read_json, safe_child, snapshot, write_json, digest, json_bytes, atomic_write, SOURCE_SUFFIXES, SOURCE_NAMES
from .native_semantics import validate_native_facts
from . import doctor as doctor_module
from .native_contract import source_truth, validate_literal_exclusion
from .cli_output import configure_utf8, emit_json

ROOT = Path(__file__).resolve().parents[2]
CODE = {'.swift', '.m', '.mm', '.h', '.c', '.cpp', '.storyboard', '.xib'}


def _emit_capability_choices(cards):
    from .xcode_mcp import render_choice as mcp_choice
    from .source_ui_capture import render_choice as ui_choice
    for card in cards:
        message=ui_choice(card) if card.get('id')=='source_ui_capture' else mcp_choice(card)
        if message:
            print(message,file=sys.stderr)


def _derived_output(project, path, name, *, migration=False):
    """Derived output must not replace execution evidence or become its own input."""
    root, path = (Path(project) / 'spec/reports').resolve(), Path(path).resolve()
    allowed = path == root / name or (path.is_relative_to(root / 'derived')
              and path != root / 'derived' and path.suffix == Path(name).suffix)
    if migration:
        allowed = allowed or path == (Path(project) / 'spec/migration-report.md').resolve()
    if not allowed:
        raise MigrationError('Use the canonical derived report path or spec/reports/derived; execution evidence cannot be overwritten')
    return path


def configure(source: Path, project: Path):
    source, project = source.resolve(), project.resolve()
    if not source.is_dir() or not project.is_dir():
        raise MigrationError('Source and Harmony project directories must exist')
    if source == project or project.is_relative_to(source) or source.is_relative_to(project):
        raise MigrationError('Harmony project must be separate from the iOS source')
    path = project / '.migbot/config.json'
    data = read_json(path) if path.exists() else {}
    if not isinstance(data, dict):
        raise MigrationError('Configuration must be a JSON object')
    if data.get('source_platform') not in (None, 'ios') or (data.get('android') and not data.get('ios')):
        raise MigrationError('Existing Android configuration is not an iOS project; choose another target')
    if data.get('ios') and Path(data['ios']).resolve() != source:
        raise MigrationError('Source changed: review the existing baseline before updating config')
    data.update(source_platform='ios', ios=str(source), harmonyos=str(project))
    data.setdefault('language', 'zh')
    data.setdefault('confirmed', False)
    data.setdefault('telemetry_consent', 'denied')
    write_json(path, data)
    return {'status': 'configured', 'config': str(path), 'confirmed': data['confirmed']}


def context(project: Path):
    project = project.resolve()
    cfg = read_json(project / '.migbot/config.json')
    if not isinstance(cfg, dict):
        raise MigrationError('Configuration must be a JSON object')
    if cfg.get('source_platform') != 'ios' or not cfg.get('ios'):
        raise MigrationError('Expected source_platform=ios and ios source path in .migbot/config.json')
    source = Path(cfg['ios'])
    if not source.is_absolute():
        source = project / source
    if not source.is_dir():
        raise MigrationError('Configured iOS source is unavailable')
    return source.resolve(), project


def index_source(project: Path):
    source, project = context(project)
    path = project / 'spec/baseline/ios-source-index.json'
    if path.exists():
        raise MigrationError('Source index exists: review changes and preserve it before refreshing')
    current = source_snapshot(source)
    if source_snapshot(source) != current:
        raise MigrationError('Source changed while indexing; no source index was published')
    data = {'version': 1, 'source_platform': 'ios', 'source_sha256': current['sha256'],
            'files': current['files'], 'excluded_directories': current['excluded_directories'],
            'facts': [], 'scope': 'Repository content snapshot only; source facts belong to the facts command'}
    write_json(path, data)
    return {'status': 'indexed', 'path': str(path), 'files': len(current['files']), 'spec_complete': False}


def refresh_source_index(project: Path, review_path: Path):
    source, project = context(project)
    review = read_json(review_path)
    path = project / 'spec/baseline/ios-source-index.json'
    prior = read_json(path)
    current = source_snapshot(source)
    if not isinstance(review, dict) or review.get('previous_source_sha256') != prior['source_sha256'] or review.get('source_sha256') != current['sha256'] or not all(isinstance(review.get(k), str) and review[k].strip() for k in ('reviewer', 'reason')):
        raise MigrationError('Source refresh needs reviewed old/new snapshot digests and a concrete reason')
    from .ios_facts import validate_graph
    validate_graph(source, project)
    archive = project / 'spec/.a2h/history' / digest(json_bytes(prior))
    write_json(archive / 'ios-source-index.json', prior)
    if source_snapshot(source) != current:
        raise MigrationError('Source changed while indexing; previous source index stays published')
    data = {**prior, 'files': current['files'], 'source_sha256': current['sha256'], 'facts': [],
            'scope': 'Repository content snapshot only; source facts belong to the facts command', 'refresh_review': review}
    write_json(path, data)
    return {'status': 'refreshed_requires_harness_recheck', 'archive': str(archive), 'spec_complete': False}


def source_paths(text: str):
    """Read file anchors from the original YAML list/map conventions, without YAML execution."""
    paths = []
    in_block = False
    for line in text.splitlines():
        if re.match(r'^\s*source_anchors:\s*(?:#.*)?$', line):
            in_block = True
            continue
        if in_block and (line.startswith('```') or (line and not line[0].isspace())):
            in_block = False
        if in_block:
            match = re.match(r'\s+(?:-\s+)?[\w.-]+:\s*(?:"([^"]+)"|\'([^\']+)\'|([^#]+))', line)
            if match:
                value = next(v for v in match.groups() if v is not None).strip()
                if Path(value).suffix.lower() in SOURCE_SUFFIXES or Path(value).name in SOURCE_NAMES:
                    paths.append(value)
    return list(dict.fromkeys(paths))


def findings_module():
    path = ROOT / 'skills/a2h-spec/scripts/_a2h_findings.py'
    spec = importlib.util.spec_from_file_location('ios_a2h_findings', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_source(project: Path, *, after_repair=False, report_only=False):
    """Check source provenance/ownership and AC evidence, updating the original shared queue."""
    source, project = context(project)
    queue = findings_module()
    issues = []
    def fail(rule, subject, detail):
        issues.append(queue.make(rule, 'spec', subject, detail))
    index_path = project / 'spec/baseline/ios-source-index.json'
    if not index_path.is_file():
        fail('IOS.SOURCE_INDEX_MISSING', str(index_path), 'Run source-index before writing the baseline')
        baseline = {'files': []}
    else:
        baseline = read_json(index_path)
        if not isinstance(baseline, dict) or not isinstance(baseline.get('files'), list) or any(
            not isinstance(f, dict) or not isinstance(f.get('path'), str) for f in baseline['files']
        ):
            raise MigrationError('Malformed iOS source index; preserve it and re-review the source baseline')
        current = source_snapshot(source)
        if baseline.get('source_sha256') != current['sha256']:
            fail('IOS.STALE_SOURCE', str(source), 'Source changed; re-review affected spec and evidence before refreshing the baseline')
    known = {f['path'] for f in baseline['files']}
    ownership = set()
    features = list((project / 'spec/baseline/features').glob('F*.md'))
    pages = list((project / 'spec/baseline/ui').glob('page_*.md'))
    seen_ids = set()
    documents = {}
    for doc in [*features, *pages]:
        text = doc.read_text(encoding='utf-8-sig')
        # Addenda share their parent's anchors; their closure is checked by the original linter.
        if doc in features and re.match(r'F\d+[-_].+\..+\.md$', doc.name):
            continue
        anchors = source_paths(text)
        stable = re.match(r'^(page_\d+|F\d+)', doc.stem)
        if stable:
            if stable[1] in documents:
                fail('IOS.DOCUMENT_DUPLICATE', stable[1], 'Multiple main specs use the same stable ID')
            documents[stable[1]] = ('feature' if doc in features else 'page', anchors)
        if not anchors:
            fail('IOS.SOURCE_ANCHOR_MISSING', doc.name, 'source_anchors must reference real iOS files')
        if re.search(r'android_source_anchors', text):
            fail('IOS.LEGACY_SOURCE_FIELD', doc.name, 'Review the old baseline and migrate to native source_anchors')
        for relative in anchors:
            try:
                file = safe_child(source, relative)
                if relative not in known or not file.is_file():
                    raise MigrationError('Not a file in the indexed iOS source')
                ownership.add(relative)
            except MigrationError as exc:
                fail('IOS.INVALID_SOURCE_ANCHOR', doc.name + ':' + relative, str(exc))
        if 'source_platform: ios' not in text:
            fail('IOS.PLATFORM_UNDECLARED', doc.name, 'Declare source_platform: ios alongside source_anchors')
        if doc in features:
            from .spec_contract import acceptance
            acs = acceptance(text)
            if not acs:
                fail('IOS.AC_MISSING', doc.name, 'Use the original stable AC IDs and source/judgment/truth syntax')
            for ac_id, body in acs:
                if ac_id in seen_ids:
                    fail('IOS.AC_DUPLICATE', ac_id, 'Stable acceptance IDs must be unique')
                seen_ids.add(ac_id)
                if not re.search(r'判:(static|unit|contract|route|ui|visual|device)\s*\|', body):
                    fail('IOS.AC_JUDGMENT_MISSING', ac_id, 'Missing original judgment anchor')
                truth = re.search(r'真:src:(.+?):(\d+)(?:`|\s|$)', body)
                if truth:
                    try:
                        source_truth(source, anchors, truth[1], int(truth[2]))
                    except (MigrationError, OSError, UnicodeError) as exc:
                        fail('IOS.AC_TRUTH_INVALID', ac_id, str(exc))
                elif not re.search(r'真:(test|trace|device|decision):[^`\s]+', body):
                    fail('IOS.AC_TRUTH_MISSING', ac_id, 'Expected independent source/test/trace/device/decision evidence')
    disposition_path = project / 'spec/baseline/ios-source-disposition.json'
    disposition = read_json(disposition_path) if disposition_path.exists() else {'files': []}
    if not isinstance(disposition, dict) or not isinstance(disposition.get('files'), list):
        raise MigrationError('Source dispositions must be an object containing a files list')
    if disposition_path.exists():
        # Reuse the walk above when the index exists; the scope binds the live whole-source digest.
        whole = current['sha256'] if index_path.is_file() else source_snapshot(source)['sha256']
        if disposition.get('source_sha256') != whole:
            fail('IOS.STALE_DISPOSITION', disposition_path.relative_to(project).as_posix(),
                 'Disposition scope requires the current whole-source source_sha256 at the top level; '
                 'each entry keeps its own file byte hash')
    dispositions = disposition['files']
    for item in dispositions:
        if not isinstance(item, dict):
            fail('IOS.INVALID_DISPOSITION', str(item), 'Disposition entry must be an object')
            continue
        try:
            validate_literal_exclusion(source, known, item)
            ownership.add(item['path'])
        except MigrationError as exc:
            fail('IOS.INVALID_DISPOSITION', str(item.get('path')), str(exc))
    for path in sorted(known):
        if Path(path).suffix.lower() in CODE and path not in ownership:
            fail('IOS.SOURCE_UNACCOUNTED', path, 'Map to a page/feature source anchor or record a reviewed disposition')
    if not features:
        fail('IOS.FEATURES_MISSING', 'features', 'No original-format feature specs exist')
    from .ios_harness import responsibility
    projection = None
    try:
        projection = responsibility(project, source=source)
    except (MigrationError, OSError, ValueError, TypeError, KeyError) as exc:
        fail('IOS.RESPONSIBILITY_INVALID', 'ios-responsibility.json', str(exc))
    validate_native_facts(source, project, documents, known, fail, projection=projection)
    from .gate_policy import summary_status
    result = {'status': summary_status(issues, queue=queue), 'checks': 'source provenance, AC format, file ownership and native semantic contract; not semantic equivalence',
              'findings': issues, 'source_platform': 'ios', 'behavior_verified': False}
    if not report_only:
        queue.replace_section(str(project), 'spec.ios-source', issues, after_repair=after_repair)
        write_json(project / 'spec/baseline/ios-source-check.json', result)
    return result, queue.section_exit_code(str(project), 'spec.ios-source', issues)


def resolve(source: Path, anchor: str):
    source = source.resolve()
    safe_child(source, anchor)  # refuse path traversal even when falling back to suffix matching
    candidates = [source / f['path'] for f in source_snapshot(source)['files'] if f['path'] == anchor or f['path'].endswith('/' + anchor)]
    if len(candidates) == 1:
        return {'status': 'OK', 'path': str(candidates[0])}, 0
    return {'status': 'AMBIGUOUS' if candidates else 'MISS', 'candidates': [str(p) for p in candidates]}, 3 if candidates else 2


def tool_config(project: Path):
    source, project = context(project)
    cfg = read_json(project / '.migbot/config.json')
    tool = dict(cfg.get('tools') or {})
    for name in ('hvigorw', 'node', 'deveco_sdk', 'hdc'):
        value = cfg.get(name) or tool.get(name)
        if value:
            path = Path(value)
            tool[name] = str((project / path).resolve() if not path.is_absolute() else path)
    if not tool.get('hvigorw'):
        tool['hvigorw'] = next((str(project / p) for p in ('hvigorw', 'hvigorw.bat') if (project / p).is_file()), None)
    tool.setdefault('node', shutil.which('node'))
    return {'source': {'platform': 'ios', 'root': str(source)}, 'target': {'root': str(project)},
            'tools': tool, 'build': cfg.get('build', {})}


def validate_tools(project: Path):
    cfg = tool_config(project)
    failures = []
    hvigor = cfg['tools'].get('hvigorw')
    if not hvigor or not Path(hvigor).is_file():
        failures.append('Configure a real hvigorw path')
    elif Path(hvigor).suffix.lower() in {'.js', '.bat', '.cmd'}:
        if not Path(hvigor).with_suffix('.js').is_file():
            failures.append('JavaScript hvigor entry missing beside wrapper')
        node = cfg['tools'].get('node')
        if not node or not Path(node).is_file():
            failures.append('Configure a real Node executable')
    if not (Path(cfg['target']['root']) / 'build-profile.json5').is_file():
        failures.append('HarmonyOS build-profile.json5 missing; run the original scaffolder first')
    return {'ok': not failures, 'failures': failures, 'source_platform': 'ios',
            'scope': 'source/config/build tool paths only', 'devices_checked': False, 'compiled': False}, 1 if failures else 0


def build_project(project: Path):
    from .build import build_target
    config = tool_config(project)
    # Evidence remains separate from both roots, as required by the build recorder.
    output = project.resolve().parent / '.a2h-build-evidence' / uuid.uuid4().hex
    result = build_target(config, output)
    result['evidence'] = str(output)
    return result, 0 if result['status'] == 'build_passed' else 1


def _maybe_spec_gates(project: Path):
    """Refresh generated spec gates when facts already exist.

    Gate generation is additive and intentionally does not turn an incomplete
    source review into a passing result.  A malformed/partial workspace keeps
    the original command's diagnostics while exposing the generation error in
    the command receipt.
    """
    try:
        from .gate_artifacts import generate_spec_gates, generate_plan_gates
        result = generate_spec_gates(project)
        result['next_stage'] = generate_plan_gates(project)
        return result
    except (MigrationError, OSError, ValueError, KeyError, TypeError) as exc:
        return {'status': 'not_generated', 'stage': 'spec', 'error': str(exc)}


def main(argv=None):
    configure_utf8(sys.stdout, sys.stderr)
    arguments = list(sys.argv[1:] if argv is None else argv)
    if arguments[:1] == ['resource-delta']:
        from .resource_merge import main as resource_main
        return resource_main(arguments[1:])
    adapters = {'pipeline-metrics': 'execution_measurements', 'indexed-dispatch': 'indexed_dispatch',
                'route-verify': 'routing_verify',
                'ui-delivery': 'ios_ui_delivery', 'behavior-review': 'behavior_review',
                'ui-repair': 'ui_repair_dispatch'}
    if arguments and arguments[0] in adapters:
        from importlib import import_module
        return import_module('.' + adapters[arguments[0]], __package__).main(arguments[1:])
    from . import __version__
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--version', action='version', version=__version__)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('resource-delta', help='Submit and merge task-owned resource changes; use resource-delta --help')
    for adapter in adapters:
        commands.add_parser(adapter, help='Use ' + adapter + ' --help for the project-bound protocol')
    init = commands.add_parser('init')
    init.add_argument('--source', required=True, type=Path)
    init.add_argument('--project', required=True, type=Path)
    commands.add_parser('expertise-audit')
    for name in ('execution-contract', 'verify-scope', 'init-environment', 'repair-permissions', 'source-index', 'source-refresh', 'source-check', 'spec-check', 'spec-authoring', 'spec-summary', 'migration-report', 'verify-report', 'gate-artifacts', 'spec-upgrade', 'validate', 'build', 'literals', 'product-literals', 'harness-init', 'import-legacy', 'facts', 'facts-view', 'harness-check', 'behavior-check', 'plan-check', 'plan-ir', 'replan', 'recover-blocked', 'next-batch', 'land-results', 'expertise-plan', 'expertise-review', 'mcp-query', 'manifest-evaluate', 'conditional-capture', 'source-analysis', 'spec-scaffold', 'usage-start', 'usage-record', 'usage-reserve', 'usage-release', 'usage-summary', 'usage-check', 'usage-finish'):
        p = commands.add_parser(name)
        p.add_argument('--project', required=True, type=Path)
        if name in {'init-environment','source-analysis'}:
            p.add_argument('--source-ui',choices=['ask','capture','replay','skip'],
                           help='Explicit source UI strategy; scope/request/bindings come from ui_capture in analysis config')
        if name == 'execution-contract':
            p.add_argument('--apply', action='store_true')
            p.add_argument('--usage-ledger',type=Path)
            p.add_argument('--usage-run-id')
        if name == 'verify-scope':
            p.add_argument('--input', type=Path, required=True)
        if name == 'init-environment':
            p.add_argument('--prepare', action='store_true')
            p.add_argument('--entrypoint', action='append', default=[],
                           help='Explicit runtime entrypoint to prepare; repeat for several paths')
            p.add_argument('--mcp', choices=['ask', 'enable', 'skip'], default='ask',
                           help='Developer choice for Xcode MCP; CLI remains available')
        if name == 'repair-permissions':
            p.add_argument('--path', type=Path, help='Exact in-project directory/file; defaults to this project root')
        if name.startswith('usage-'):
            p.add_argument('--ledger', type=Path, help='Project spec/reports/derived/.../usage-budget.json')
            if name in {'usage-start', 'usage-finish'}:
                p.add_argument('--run-id', required=True)
            if name == 'usage-start':
                p.add_argument('--token-limit', type=int, default=19_900_000)
                p.add_argument('--walltime-limit-seconds', type=int, default=7200)
            if name in {'usage-record', 'usage-reserve', 'usage-release'}:
                p.add_argument('--input', type=Path, required=True, help='Exact usage, reservation or uncalled-release request JSON')
        if name == 'recover-blocked':
            p.add_argument('--review', type=Path, required=True)
        if name == 'source-check':
            p.add_argument('--after-repair', action='store_true')
            p.add_argument('--report-only', action='store_true')
            p.add_argument('--harness', action='store_true')
        if name in {'facts', 'source-analysis'}:
            p.add_argument('--variant', type=Path)
            p.add_argument('--providers', type=Path)
            p.add_argument('--manifest-evidence', type=Path)
            p.add_argument('--brief', action='store_true')
        if name == 'verify-report':
            p.add_argument('--scope', type=Path, help='Explicit normalized verification scope request')
        if name == 'gate-artifacts':
            p.add_argument('--stage', choices=['spec', 'plan', 'execute', 'verify', 'all'], default='all')
            p.add_argument('--input', type=Path)
        if name == 'source-analysis':
            p.add_argument('--apply-scaffold', action='store_true', help='Create only missing canonical, unreviewed scaffold files')
            p.add_argument('--analysis-config', type=Path, help='Explicit analysis scope and evidence; default auto')
            p.add_argument('--plan-only', action='store_true', help='Read-only context decisions without executing stages')
            p.add_argument('--mcp', choices=['ask', 'enable', 'skip'],
                           help='Use the existing developer choice, or explicitly select read-only MCP/CLI for this run')
        if name == 'spec-scaffold':
            p.add_argument('--apply', type=Path, help='Apply a previously derived candidate; never approves it')
            p.add_argument('--brief', action='store_true', help='With --output, print only the artifact receipt')
        if name == 'manifest-evaluate':
            p.add_argument('--config', required=True, type=Path)
            p.add_argument('--output', required=True, type=Path)
        if name == 'conditional-capture':
            p.add_argument('--config', required=True, type=Path)
            p.add_argument('--output', required=True, type=Path)
        if name == 'facts-view':
            p.add_argument('--scope', choices=['project', 'ui', 'feature', 'api'], required=True)
        if name == 'behavior-check':
            p.add_argument('--run', action='store_true')
        if name in {'plan-check', 'plan-ir', 'replan'}:
            p.add_argument('--input', type=Path, required=True)
        if name == 'expertise-review':
            p.add_argument('--input', type=Path, required=True)
        if name == 'spec-authoring':
            p.add_argument('--input', type=Path)
        if name == 'mcp-query':
            p.add_argument('--server', type=Path, required=True)
            p.add_argument('--request', type=Path, required=True)
        if name == 'source-refresh':
            p.add_argument('--review', type=Path, required=True)
        if name in {'literals', 'product-literals', 'spec-summary', 'migration-report', 'spec-upgrade', 'spec-authoring', 'spec-scaffold'}:
            p.add_argument('--output', type=Path)
        if name in {'spec-summary', 'migration-report', 'verify-report', 'gate-artifacts'}:
            p.add_argument('--build-evidence', type=Path)
        if name in {'spec-summary', 'migration-report'}:
            p.add_argument('--brief', action='store_true',
                           help='With --output, write the same full file but print only a small receipt (status/path/sha256/counts).')
        if name in {'migration-report', 'verify-report'}:
            p.add_argument('--check', type=Path)
        if name == 'spec-upgrade':
            p.add_argument('--apply', type=Path)
            selection = p.add_mutually_exclusive_group()
            selection.add_argument('--patch', action='append')
            selection.add_argument('--all-candidates', action='store_true')
        if name in {'next-batch', 'land-results'}:
            p.add_argument('--wave', default='domains')
        if name == 'next-batch':
            p.add_argument('--usage-ledger', type=Path, help='Check supplied usage before dispatch; requires --usage-run-id')
            p.add_argument('--usage-run-id', help='Expected run identity for --usage-ledger')
    resolver = commands.add_parser('resolve')
    resolver.add_argument('--source', required=True, type=Path)
    resolver.add_argument('--anchor', required=True)
    doc = commands.add_parser('doctor', help='Read-only environment diagnostic: what works, what is missing, next actions')
    doc.add_argument('--project', type=Path, default=Path('.'), help='Project root to inspect (default: cwd)')
    doc.add_argument('--config', type=Path, help='Optional migration config to validate')
    doc.add_argument('--node', help='Explicit node path')
    doc.add_argument('--hvigor', help='Explicit hvigorw path')
    doc.add_argument('--ohpm', help='Explicit ohpm path')
    doc.add_argument('--java', help='Explicit java path')
    doc.add_argument('--sdk', help='Explicit HarmonyOS SDK path')
    doc.add_argument('--text', action='store_true', help='Also print human-readable report to stderr')
    args = parser.parse_args(argv)
    from .project_progress import ProjectProgress
    progress_note = ProjectProgress(args)

    def analysis_progress(event):
        _emit_capability_choices(event.get('capability_choices',[]))
        print(json.dumps(event, ensure_ascii=True), file=sys.stderr)
        progress_note.record(event.get('status', 'running'), event)

    progress_note.record('running')
    try:
        code = 0
        if args.command == 'verify-scope':
            # Scope numbering is a public protocol, not a directory-marker mode.
            from .indexed_verify import scope as resolve_scope
            result = resolve_scope(read_json(args.input))
        elif args.command == 'init-environment':
            from .init_environment import run
            result = run(args.project, ROOT, prepare=args.prepare,
                         entrypoints=args.entrypoint, mcp=args.mcp,source_ui=args.source_ui)
            _emit_capability_choices(result.get('capability_choices',[]))
            code = 0 if result['status'] == 'ready' else 2
        elif args.command == 'repair-permissions':
            from .macos_permissions import ensure_runtime_permissions
            project = args.project.resolve()
            install_path = project / '.hmigbot-ios/install.json'
            config_path = project / '.migbot/config.json'
            installed = install_path.is_file() and read_json(install_path).get('owner') == 'hmigbot-ios'
            configured = config_path.is_file() and read_json(config_path).get('source_platform') == 'ios'
            if not installed and not configured:
                raise MigrationError('Permission repair requires the current configured or installed migration project')
            target = args.path if args.path is not None else project
            if not target.is_absolute():
                target = project / target
            result = ensure_runtime_permissions(project, target)
        elif args.command.startswith('usage-'):
            from . import usage_budget
            project = args.project.resolve()
            ledger = _derived_output(project, args.ledger or project / 'spec/reports/derived/usage-budget.json', 'usage-budget.json')
            if ledger.name != 'usage-budget.json':
                raise MigrationError('Usage ledger must be named usage-budget.json within spec/reports/derived')
            if args.command == 'usage-start':
                result = usage_budget.start(ledger, args.run_id, project_root=project,
                                            token_limit=args.token_limit, walltime_limit_seconds=args.walltime_limit_seconds)
            elif args.command == 'usage-record':
                request = read_json(args.input)
                required = {'call_id', 'raw_usage', 'run_id', 'normalization_mode', 'stage', 'agent', 'provider'}
                if not isinstance(request, dict) or not required <= request.keys() or request.keys() - required - {'attempt'}:
                    raise MigrationError('Usage record needs exact call identity, raw_usage and normalization_mode fields')
                result = usage_budget.record(ledger, **request)
                if not result['can_continue']:
                    code = 2 if result['status'] == 'FAIL' else 3
            elif args.command in {'usage-reserve', 'usage-release'}:
                request = read_json(args.input)
                required = ({'call_id', 'token_upper_bound', 'run_id', 'stage', 'agent', 'provider'}
                            if args.command == 'usage-reserve' else {'call_id', 'run_id', 'reason'})
                optional = {'attempt'} if args.command == 'usage-reserve' else set()
                if not isinstance(request, dict) or not required <= request.keys() or request.keys() - required - optional:
                    raise MigrationError('Reservation/release request needs exact identity and bound or audit reason fields')
                result = (usage_budget.reserve(ledger, project_root=project, **request)
                          if args.command == 'usage-reserve' else usage_budget.release(ledger, **request))
                # Reserve creates or replays this unique call's hold. A replay
                # is bookkeeping, never permission to invoke the same call twice.
                # No remaining capacity for additional calls is not an error.
                code = 0
            else:
                result = (usage_budget.finish(ledger, run_id=args.run_id) if args.command == 'usage-finish'
                          else usage_budget.check(ledger))
                if args.command != 'usage-summary':
                    code = {'PASS': 0, 'FAIL': 2, 'UNKNOWN': 3}[result['status']]
            result['ledger'] = str(ledger)
        elif args.command == 'expertise-audit':
            from .expertise import audit
            manifest, files = audit()
            result = {'status': 'passed', 'packs': len(manifest['packs']), 'files': len(files)}
        elif args.command == 'expertise-plan':
            from .expertise import prepare
            result = prepare(args.project)
        elif args.command == 'expertise-review':
            from .expertise import record
            result = record(args.project, args.input)
        elif args.command == 'mcp-query':
            from .source_mcp import capture
            result = capture(args.project, args.server, args.request)
        elif args.command == 'init': result = configure(args.source, args.project)
        elif args.command == 'execution-contract':
            from .execution_bridge import prepare
            result = prepare(args.project, apply=args.apply,usage_ledger=args.usage_ledger,
                             usage_run_id=args.usage_run_id)
        elif args.command == 'source-index': result = index_source(args.project)
        elif args.command == 'source-analysis':
            from .source_analysis import run
            result = run(args.project, variant=read_json(args.variant) if args.variant else None,
                         providers=args.providers, manifest_evidence=args.manifest_evidence,
                         apply_scaffold=args.apply_scaffold, analysis_config=args.analysis_config,
                         plan_only=args.plan_only,
                         progress=analysis_progress, mcp=args.mcp,source_ui=args.source_ui)
            if args.plan_only:
                _emit_capability_choices(result.get('capability_choices',[]))
            code = 2 if result.get('status') in {'needs_input', 'failed','needs_ui_evidence'} else 0
        elif args.command == 'spec-scaffold':
            from .native_scaffold import scaffold, apply_scaffold
            if args.apply:
                if args.output or args.brief:
                    raise MigrationError('Choose scaffold apply or candidate output')
                result = apply_scaffold(args.project, read_json(args.apply))
                result['status'] = 'refused' if result.get('refused') else 'applied_candidate'
                code = 2 if result.get('refused') else 0
            else:
                if args.brief and not args.output:
                    raise MigrationError('--brief requires --output; keep the full scaffold candidate')
                result = scaffold(args.project)
                if args.output:
                    output = _derived_output(args.project, args.output, 'spec-scaffold.json')
                    write_json(output, result)
                    if args.brief:
                        body = output.read_bytes()
                        result = {'status': 'candidate', 'output': str(output), 'sha256': digest(body),
                                  'bytes': len(body), 'counts': result['summary'],
                                  'spec_complete': False, 'behavior_verified': False}
        elif args.command == 'source-refresh': result = refresh_source_index(args.project, args.review)
        elif args.command == 'literals':
            from .ios_literals import run
            result = run(args.project, args.output)
        elif args.command == 'spec-authoring':
            from .native_authoring import prepare, render
            result = render(args.project, read_json(args.input)) if args.input else prepare(args.project)
            if args.output:
                write_json(_derived_output(args.project, args.output, 'spec-authoring.json'), result)
        elif args.command == 'spec-upgrade':
            from .spec_upgrade import inspect, apply
            if args.apply:
                if args.output or not (args.patch or args.all_candidates):
                    raise MigrationError('Apply needs explicit --patch or --all-candidates and cannot use --output')
                report = read_json(args.apply)
                ids = [p['patch_id'] for p in report['patches']] if args.all_candidates else args.patch
                result = apply(args.project, report, patch_ids=ids)
            else:
                if args.patch or args.all_candidates:
                    raise MigrationError('Patch selection requires --apply REPORT')
                result = inspect(args.project)
                if args.output:
                    write_json(_derived_output(args.project, args.output, 'spec-upgrade.json'), result)
        elif args.command == 'migration-report':
            from .quality_views import summary, render_report, validate_report
            if args.check and args.output:
                raise MigrationError('Choose report output or report check')
            if args.brief:
                if args.check:
                    raise MigrationError('--brief is not supported with --check; keep the check receipt unchanged')
                if not args.output:
                    raise MigrationError('--brief requires --output; refusing to discard the report body')
            if args.check:
                contents = args.check.read_text(encoding='utf-8')
                from .gate_artifacts import MARKER, generate_execution_gates
                if MARKER in contents and 'gate_status: BLOCKED' in contents:
                    expected = generate_execution_gates(args.project, build_evidence=args.build_evidence, write=False)
                    if contents != expected['markdown']:
                        raise MigrationError('Blocked migration report is edited or stale; regenerate it')
                else:
                    validate_report(args.project, contents, build_evidence=args.build_evidence)
                result = {'status': 'current', 'report': str(args.check)}
            else:
                report = summary(args.project, build_evidence=args.build_evidence)
                text = render_report(report)
                if args.output:
                    path = _derived_output(args.project, args.output, 'migration-report.md', migration=True)
                    atomic_write(path, text.encode('utf-8'))
                    if args.brief:
                        body = path.read_bytes()
                        counts = report.get('counts', {}) if isinstance(report, dict) else {}
                        result = {'status': 'generated', 'mode': 'brief',
                                  'output': str(path), 'sha256': digest(body), 'bytes': len(body),
                                  'counts': {'acceptance': counts.get('acceptance'),
                                             'features': counts.get('features'),
                                             'pages': counts.get('pages')}}
                    else:
                        result = {'status': 'generated', 'report': str(args.output), 'markdown': text}
                else:
                    result = {'status': 'generated', 'report': None, 'markdown': text}
        elif args.command == 'verify-report':
            from .gate_artifacts import generate_verify_report
            result = generate_verify_report(args.project, build_evidence=args.build_evidence, write=not args.check, scope=read_json(args.scope) if args.scope else None)
            if args.check:
                if args.check.read_text(encoding='utf-8') != result.pop('markdown'):
                    raise MigrationError('Verification report is stale or edited; regenerate from current evidence')
                result['status'] = 'current'
        elif args.command == 'gate-artifacts':
            from .gate_artifacts import generate_spec_gates, generate_plan_gates, generate_execution_gates, generate_verify_report
            if args.input:
                from .ios_scheduler import generate
                generate(args.project, args.input, validate_only=True)
            generated = []
            if args.stage in {'spec', 'all'}:
                generated.append(generate_spec_gates(args.project))
            if args.stage in {'plan', 'all'}:
                generated.append(generate_plan_gates(args.project, args.input))
            if args.stage in {'execute', 'all'}:
                generated.append(generate_execution_gates(args.project, build_evidence=args.build_evidence))
            if args.stage in {'verify', 'all'}:
                generated.append(generate_verify_report(args.project, build_evidence=args.build_evidence))
            result = {'status': 'generated', 'stages': generated, 'behavior_verified': False}
        elif args.command in {'product-literals', 'spec-summary'}:
            from .quality_views import product_literals, summary
            if args.command == 'spec-summary' and args.brief and not args.output:
                raise MigrationError('--brief requires --output; refusing to discard the summary')
            result = (product_literals(args.project) if args.command == 'product-literals'
                      else summary(args.project, build_evidence=args.build_evidence))
            if args.output:
                output = _derived_output(args.project, args.output, args.command + '.json')
                write_json(output, result)
                if args.command == 'spec-summary' and args.brief:
                    body = output.read_bytes()
                    counts = result.get('counts', {}) if isinstance(result, dict) else {}
                    result = {'status': 'generated', 'mode': 'brief',
                              'output': str(output), 'sha256': digest(body), 'bytes': len(body),
                              'counts': {'acceptance': counts.get('acceptance'),
                                         'features': counts.get('features'),
                                         'pages': counts.get('pages')}}
        elif args.command == 'conditional-capture':
            from .conditional_evidence import capture
            result = capture(args.project.resolve(), args.config, args.output)
        elif args.command == 'spec-check':
            from .spec_contract import check as check_contract
            result, code = check_contract(args.project)
        elif args.command == 'source-check':
            if args.harness:
                from .ios_harness import check
                result, code = check(args.project, report_only=args.report_only)
            else:
                result, code = check_source(args.project, after_repair=args.after_repair, report_only=args.report_only)
                result['harness_ready'] = False
                result['compatibility_only'] = True
            if not args.report_only:
                from .gate_artifacts import refresh_spec_reports
                try:
                    result['gate_artifacts'] = refresh_spec_reports(args.project, result if args.harness else None)
                except (MigrationError, OSError, ValueError) as exc:
                    result['gate_artifacts'] = {'status': 'not_generated', 'error': str(exc)}
        elif args.command in {'harness-init', 'import-legacy'}:
            from .ios_harness import initialize
            result = initialize(args.project, import_legacy=args.command == 'import-legacy')
            if args.command == 'import-legacy':
                result['gate_artifacts'] = _maybe_spec_gates(args.project)
        elif args.command == 'facts':
            from .ios_facts import refresh
            source, project = context(args.project)
            result = refresh(project, source, read_json(args.variant) if args.variant else None, args.providers,
                             args.manifest_evidence)
            gate = _maybe_spec_gates(project)
            if gate['status'] != 'generated':
                code = 2
            result = ({'status': 'extracted', 'source_sha256': result['source_sha256'],
                       'facts': len(result['facts'])} if args.brief else dict(result))
            result['gate_artifacts'] = gate
        elif args.command == 'manifest-evaluate':
            from .manifest_evidence import capture
            source, project = context(args.project)
            output = args.output.resolve()
            if not output.is_relative_to((project / 'spec/ref/ios-manifest-evidence').resolve()):
                raise MigrationError('Capture manifest evidence under project/spec/ref/ios-manifest-evidence')
            result = capture(source, args.config, output)
            if result.get('status') == 'capture_failed':
                code = 2
        elif args.command == 'facts-view':
            from .ios_facts import view
            source, project = context(args.project)
            result = view(project, source, args.scope)
        elif args.command == 'harness-check':
            from .ios_harness import check
            result, code = check(args.project)
            from .gate_artifacts import generate_verify_report
            result['gate_artifacts'] = generate_verify_report(args.project)
        elif args.command == 'behavior-check':
            from .ios_facts import validate_graph
            from .ios_harness import ac_inventory
            from .behavior import verify
            source, project = context(args.project)
            graph, _ = validate_graph(source, project)
            result, code = verify(project, source, graph, ac_inventory(project), run=args.run)
            from .gate_artifacts import generate_verify_report
            result['gate_artifacts'] = generate_verify_report(project)
        elif args.command in {'plan-check', 'plan-ir'}:
            from .ios_scheduler import generate
            result = generate(args.project, args.input, validate_only=args.command == 'plan-check')
            if args.command == 'plan-ir':
                from .gate_artifacts import generate_plan_gates
                result['gate_artifacts'] = generate_plan_gates(args.project, args.input)
        elif args.command == 'recover-blocked':
            from .replan_recovery import recover_blocked
            result = recover_blocked(args.project, args.review)
        elif args.command == 'replan':
            from .ios_scheduler import replan
            result = replan(args.project, args.input)
            from .gate_artifacts import generate_plan_gates
            result['gate_artifacts'] = generate_plan_gates(args.project, args.input)
        elif args.command in {'next-batch', 'land-results'}:
            from .ios_scheduler import step
            options = ({'usage_ledger': args.usage_ledger, 'usage_run_id': args.usage_run_id}
                       if args.command == 'next-batch' else {})
            result, code = step(args.project, args.wave, landing=args.command == 'land-results', **options)
            if args.command == 'land-results':
                from .gate_artifacts import generate_execution_gates
                result['gate_artifacts'] = generate_execution_gates(args.project)
        elif args.command == 'validate': result, code = validate_tools(args.project)
        elif args.command == 'build': result, code = build_project(args.project)
        elif args.command == 'doctor':
            result = doctor_module.doctor(args.project, config=args.config, node_path=args.node,
                                          hvigor_path=args.hvigor, ohpm_path=args.ohpm,
                                          java_path=args.java, sdk_path=args.sdk)
            if args.text:
                print(doctor_module.render_text(result), file=sys.stderr)
            code = 0 if result.get('status') == 'diagnostic_complete' else 2
        else: result, code = resolve(args.source, args.anchor)
        progress_note.record(result.get('status', 'returned'), result, exit_code=code)
        emit_json(result)
        return code
    except (MigrationError, OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        error = {'status': 'FAIL', 'error': str(exc)}
        if isinstance(getattr(exc, 'receipt', None), dict):
            error['permission_repair'] = exc.receipt
        progress_note.record('FAIL', error, exit_code=2)
        emit_json(error, indent=None)
        return 2
