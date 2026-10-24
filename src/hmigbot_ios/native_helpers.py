"""Narrow native frontends for bundled HMigBot consumers, not a migration engine."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import os

from .runtime_timeouts import timeout_for
from .scheduler_windows_runtime import run as run_owned_process

ROOT = Path(__file__).resolve().parents[2]


def original(skill, helper, arguments, *, cwd=None):
    path = ROOT / 'vendor/hmigbot/skills' / skill / 'scripts' / helper
    if not path.is_file():
        raise ValueError('Complete bundled helper is missing: ' + helper)
    stage = {'structural_loop.py': 'structural', 'assembly_gate.py': 'assembly',
             'literal_gate.py': 'literal'}.get(helper, 'helper')
    # Preserve historically unbounded helpers unless an explicit cap/deadline is supplied.
    limit = timeout_for(stage, default=None)
    command = [sys.executable, str(path), *map(str, arguments)]
    if os.name == 'nt':
        result = run_owned_process(command, cwd=cwd, env=os.environ.copy(), timeout=limit)
        return subprocess.CompletedProcess(result.args, result.returncode,
            result.stdout.decode('utf-8', errors='replace'), result.stderr.decode('utf-8', errors='replace'))
    from .portable_helper import run
    return run(path, arguments, cwd=cwd, timeout=limit, capture_output=True, encoding='utf-8', errors='replace')


def feature_inputs(arguments):
    # Keep upstream ID/addendum parsing; only the emitted oracle destination changes.
    parser = argparse.ArgumentParser(description='Resolve native feature, AC and source-oracle output paths')
    parser.add_argument('--project-root', type=Path, required=True)
    parser.add_argument('--scope')
    args = parser.parse_args(arguments)
    call = ['--project-root', args.project_root]
    if args.scope:
        call += ['--scope', args.scope]
    result = original('arkts-ut-verifier', 'feature_inputs.py', call)
    if result.returncode:
        sys.stderr.write(result.stderr or result.stdout)
        return result.returncode
    data = json.loads(result.stdout)
    for feature in data['features']:
        filename = Path(feature['oracle_file']).name
        feature['oracle_file'] = str(args.project_root.resolve() / 'spec/verify/ut/source-oracle' / filename)
    print(json.dumps(data, ensure_ascii=False, indent=2))
    return 0


def icon_audit(project, output):
    """Read-only original detector; never infer iOS scale from a default density."""
    from .native_icon_scope import audit
    return audit(project, output, original)


def structural_loop(arguments):
    parser = argparse.ArgumentParser(description='Original structural loop with native image constraints preflight')
    sub = parser.add_subparsers(dest='operation', required=True)
    iterate = sub.add_parser('iterate')
    iterate.add_argument('--project-root', type=Path, required=True)
    iterate.add_argument('--mode', choices=['stage', 'slice', 'group', 'pipeline'], required=True)
    iterate.add_argument('--target', required=True)
    iterate.add_argument('--state-file', type=Path, required=True)
    iterate.add_argument('--slices')
    iterate.add_argument('--max-iter', type=int)
    iterate.add_argument('--diff-base')
    iterate.add_argument('--handoffs', nargs='*')
    iterate.add_argument('--output-json', type=Path)
    finalize = sub.add_parser('finalize')
    finalize.add_argument('--state-file', type=Path, required=True)
    finalize.add_argument('--output-json', type=Path)
    args = parser.parse_args(arguments)
    if args.operation == 'iterate' and args.mode in {'slice', 'group'}:
        from .native_structural import enabled, iterate as native_iterate
        if enabled(args.project_root):
            try:
                return native_iterate(args, original)
            except (ValueError, KeyError, OSError) as exc:
                if args.output_json:
                    from .core import write_json
                    write_json(args.output_json, {'status': 'failed', 'passed': False, 'error': str(exc)})
                raise
    if args.operation == 'iterate' and args.mode == 'pipeline':
        report = args.state_file.resolve().with_name(args.state_file.stem + '-native-images.json')
        audit = icon_audit(args.project_root, report)
        if audit['status'] != 'passed':
            data = {'verdict': 'NATIVE_INPUT_REQUIRED', 'passed': False, 'mutated': False,
                    'report': str(report), 'findings': audit['report']['flagged'],
                    'action': 'Use actual source layout and asset scale; fix owned ArkUI dimensions, then retry'}
            if args.output_json:
                args.output_json.parent.mkdir(parents=True, exist_ok=True)
                args.output_json.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
            print(json.dumps(data, ensure_ascii=False, indent=2))
            return 3
    native_pipeline = args.operation == 'iterate' and args.mode == 'pipeline'
    if args.operation == 'finalize' and args.state_file.is_file():
        from .core import read_json
        native_pipeline = read_json(args.state_file).get('mode') == 'pipeline'
    if native_pipeline:
        from .native_pipeline_runtime import invoke as invoke_pipeline
        result = invoke_pipeline(arguments, original=original)
    else:
        result = original('arkts-structural-closure', 'structural_loop.py', arguments)
    sys.stdout.write(result.stdout)
    sys.stderr.write(result.stderr)
    return result.returncode


def verify_slice_wiring(arguments):
    from .native_structural import enabled, wiring
    # Let the bundled parser own the complete legacy CLI, including help and
    # validation errors. Only a positively identified native project adapts.
    probe = argparse.ArgumentParser(add_help=False)
    probe.add_argument('--project-root', type=Path)
    identity, _ = probe.parse_known_args(arguments)
    if identity.project_root is None or not enabled(identity.project_root):
        result = original('arkts-structural-closure', 'verify_slice_wiring.py', arguments)
        sys.stdout.write(result.stdout)
        sys.stderr.write(result.stderr)
        return result.returncode
    parser = argparse.ArgumentParser(description='Native indexed wiring with original C1/C3/C4 detectors')
    parser.add_argument('--project-root', type=Path, required=True)
    parser.add_argument('--slice', dest='slice_number', type=int, required=True)
    parser.add_argument('--feature-plan', type=Path)
    parser.add_argument('--output-json', type=Path)
    args = parser.parse_args(arguments)
    import tempfile
    try:
        with tempfile.TemporaryDirectory(prefix='native-wiring-') as directory:
            report = wiring(args.project_root.resolve(), args.slice_number,
                            args.output_json or Path(directory) / 'wiring.json', original,
                            feature_plan=args.feature_plan)
    except (ValueError, KeyError, OSError) as exc:
        if args.output_json:
            from .core import write_json
            write_json(args.output_json, {'status': 'failed', 'overall': 'BLOCKED', 'error': str(exc)})
        raise
    if not args.output_json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report['overall'] == 'PASS' else 1


def main(arguments=None):
    arguments = list(sys.argv[1:] if arguments is None else arguments)
    try:
        if not arguments:
            raise ValueError('Expected feature-inputs, structural-loop or icon-audit')
        operation = arguments.pop(0)
        if operation == 'feature-inputs':
            return feature_inputs(arguments)
        if operation == 'structural-loop':
            return structural_loop(arguments)
        if operation == 'verify-slice-wiring':
            return verify_slice_wiring(arguments)
        if operation == 'icon-audit':
            parser = argparse.ArgumentParser(description='Read-only native image constraints check')
            parser.add_argument('--project-root', type=Path, required=True)
            parser.add_argument('--output-json', type=Path, required=True)
            args = parser.parse_args(arguments)
            report = icon_audit(args.project_root, args.output_json)
            print(json.dumps(report, ensure_ascii=False, indent=2))
            return 0 if report['status'] == 'passed' else 2
        raise ValueError('Unknown helper operation')
    except (ValueError, KeyError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({'status': 'failed', 'error': str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 3


if __name__ == '__main__':
    raise SystemExit(main())
