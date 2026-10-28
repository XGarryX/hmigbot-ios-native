"""Source-independent target input around the original route stage commands.

The historical ``*.native-input.json`` filenames remain compatible, while the
target producer identity describes only HarmonyOS inputs. Source adapters check
their own source facts before consuming the target graph.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

from hmigbot_ios.core import MigrationError, atomic_write, read_json, write_json
from .route_engine import compiled
from .target_routes import digest, supplement_target, validate_receipt, validate_target_snapshot


TARGET_CONSUMERS = frozenset({'build_page_mapping', 'build_report', 'diff_routes',
                             'hmos_reachability', 'thin_shell_probe', 'build_fix_plan'})


def _begin(out, stage):
    out.mkdir(parents=True, exist_ok=True)
    write_json(out / (stage + '.native-input.json'), {'stage': stage, 'scope': 'harmonyos-target',
               'source_platform': 'harmonyos', 'status': 'incomplete', 'outputs_usable': False})


def _finish(out, stage, receipt, inputs, outputs, extra=None):
    paths = [out / name for name in outputs]
    missing = [str(path) for path in paths if not path.is_file()]
    if missing:
        raise MigrationError('Original route engine did not produce: ' + ', '.join(missing))
    identity = receipt['snapshot_sha256']
    write_json(out / (stage + '.native-input.json'), {'stage': stage, 'scope': 'harmonyos-target',
        'source_platform': 'harmonyos', 'status': 'complete', 'target_identity': identity,
        'input_identity': identity,
        'inputs': {str(out / name): digest((out / name).read_bytes()) for name in inputs if (out / name).is_file()},
        'outputs': {str(path): digest(path.read_bytes()) for path in paths}, **(extra or {})})
    failure = out / (stage + '.native-failure.json')
    if failure.is_file():
        failure.rename(out / (stage + '.native-failure.' + digest(failure.read_bytes())[:12] + '.json'))


def target_current(root, out):
    metadata = read_json(out / 'hmos_extract.native-input.json')
    if metadata.get('status') != 'complete' or metadata.get('scope') != 'harmonyos-target':
        raise MigrationError('HarmonyOS target extraction is missing/stale; rerun hmos_extract')
    for name in ('actual_nav.json', 'actual_nav.original.json', 'hmos_extract.ets-input.json'):
        path = out / name
        if not path.is_file() or metadata.get('outputs', {}).get(str(path)) != digest(path.read_bytes()):
            raise MigrationError('HarmonyOS target output changed; rerun hmos_extract: ' + name)
    receipt = read_json(out / 'hmos_extract.ets-input.json')
    if metadata.get('target_identity') != receipt.get('snapshot_sha256'):
        raise MigrationError('HarmonyOS target identity changed; rerun hmos_extract')
    validate_receipt(root, receipt)
    return receipt


def _run(scripts, stage, root, out, argv):
    process = compiled(scripts, stage, argv, {'ROUTE_VERIFY_ROOT': str(root), 'ROUTE_VERIFY_OUT': str(out)})
    print(process.stdout, end='')
    if process.stderr:
        print(process.stderr, file=sys.stderr, end='')
    return process.returncode


def target_extract(scripts, root, out, argv):
    _begin(out, 'hmos_extract')
    code = _run(scripts, 'hmos_extract', root, out, argv)
    if code:
        return code
    original_bytes = (out / 'actual_nav.json').read_bytes()
    original = json.loads(original_bytes)
    derived, receipt = supplement_target(root, original, scripts=scripts, original_bytes=original_bytes, engine_argv=argv)
    validate_target_snapshot(root, receipt, actual=derived)
    atomic_write(out / 'actual_nav.original.json', original_bytes)
    write_json(out / 'hmos_extract.ets-input.json', receipt)
    if derived != original:
        write_json(out / 'actual_nav.json', derived)
    _finish(out, 'hmos_extract', receipt, [],
            ['actual_nav.json', 'actual_nav.original.json', 'hmos_extract.ets-input.json'],
            {'target_input_mode': 'original compiled extraction plus official ETS static supplements; source-independent'})
    print('HarmonyOS target supplements: scope=%s, %d added/resolved rows, %d unknowns, %d merge conflicts; inspect %s' % (
        receipt.get('scope_status'), len(receipt.get('added_edges', [])), len(receipt.get('unknowns', [])),
        len(receipt.get('merge_unknowns', [])), out / 'hmos_extract.ets-input.json'))
    return 0


def target_consumer(stage, scripts, root, out, argv):
    receipt = target_current(root, out)
    _begin(out, stage)
    code = _run(scripts, stage, root, out, argv)
    if code:
        return code
    if stage == 'hmos_reachability':
        path = out / 'reachability_robust.json'
        report = read_json(path)
        edges = read_json(out / 'actual_nav.json').get('edges', [])
        receipt_path = out / 'hmos_extract.ets-input.json'
        changed = False
        for page in report.get('pages', []):
            related = [edge for edge in edges if edge.get('target') == page.get('hmos_page') and edge.get('supplement') == 'ets_ast']
            if related:
                page['ets_ast_supplement'] = {'scope': 'static syntax evidence; original layer unchanged; no device validation',
                    'receipt': str(receipt_path), 'receipt_sha256': digest(receipt_path.read_bytes()), 'edges': related}
                changed = True
        if changed:
            write_json(path, report)
    target_current(root, out)
    names = {'build_page_mapping': ['page_mapping.json'], 'build_report': ['migration_nav_report.json'],
             'diff_routes': ['diff_routes_report.json', 'diff_routes_report.md'],
             'hmos_reachability': ['reachability_robust.json'],
             'thin_shell_probe': ['thin_shell_report.json', 'thin_shell_report.md'], 'build_fix_plan': ['fix_plan.json']}[stage]
    _finish(out, stage, receipt, ['actual_nav.json', 'hmos_extract.ets-input.json', 'nav_edges.json', 'page_mapping.json'], names,
            {'target_input_mode': 'original compiled consumer; original independent classifications retained'})
    return 0
