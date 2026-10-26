"""Source-bound five-stage workspace; no telemetry or legacy .done sentinels."""
from pathlib import Path

from . import __version__
from .analyze import analyze, migration_plan, render_report
from .core import source_snapshot
from .core import SCHEMA, MigrationError, digest, json_bytes, read_json, safe_child, snapshot, write_new_tree
from .contracts import validate_facts


def initialize(source, run):
    source, run = source.resolve(), run.resolve()
    if run.is_relative_to(source) or source.is_relative_to(run):
        raise MigrationError('Run directory must not overlap source')
    facts = analyze(source)
    plan = migration_plan(facts)
    features = [{'id': 'FILE-' + digest(f['path'].encode())[:16], 'source_path': f['path'],
                 'source_sha256': f['sha256'], 'disposition': 'pending'} for f in facts['source_snapshot']['files']]
    metadata = {'schema_version': SCHEMA, 'tool_version': __version__, 'source_root': str(source),
                'source_sha256': facts['source_snapshot']['sha256'], 'stages': ['spec', 'plan', 'execute', 'verify', 'retrospect']}
    files = {'run.json': json_bytes(metadata), 'spec/facts.json': json_bytes(facts),
             'spec/report.md': render_report(facts, plan).encode('utf-8'), 'plan/operations.json': json_bytes(plan),
             'plan/features.json': json_bytes({'schema_version': SCHEMA, 'source_sha256': metadata['source_sha256'], 'features': features}),
             'execute/coverage.example.json': json_bytes({'source_sha256': metadata['source_sha256'], 'items': []}),
             'NEXT.md': ('# Migration run\n\nUse $a2h-ios-run and its references/run-protocol.md. '
                         'This is a new source baseline; no behavior has been migrated.\n\n'
                         'Next: read spec/report.md and the actual application entry; split plan/features.json '
                         'file candidates into observable features and prepare iOS semantic contracts. '
                         'Then map them to bound original HMigBot skills, implement and verify one feature slice.\n\n'
                         'On resume, inspect current source, target edits, latest slice brief, open findings and '
                         'running processes before repeating work. Record exact next action and evidence paths here. '
                         'Every source file needs a mapped or explicit not_applicable disposition.\n').encode()}
    write_new_tree(run, files)
    return {'status': 'initialized', 'run': str(run), 'features': len(features), 'migration_complete': False}


def check_coverage(source, target, features, coverage):
    expected = {f['id']: f for f in features}
    if len(expected) != len(features):
        raise MigrationError('Duplicate feature IDs')
    seen, gaps = set(), []
    if not isinstance(coverage.get('items'), list):
        raise MigrationError('Coverage items must be an array')
    for item in coverage['items']:
        key = item.get('feature_id')
        if key not in expected or key in seen:
            raise MigrationError('Unknown or duplicate coverage feature')
        seen.add(key)
        feature = expected[key]
        path = safe_child(source, feature['source_path'])
        if not path.is_file() or digest(path.read_bytes()) != feature['source_sha256']:
            raise MigrationError('Coverage source changed')
        status = item.get('status')
        if status == 'not_applicable':
            if not isinstance(item.get('reason'), str) or not item['reason'].strip():
                raise MigrationError('not_applicable requires a reviewable reason')
        elif status == 'implemented':
            outputs = item.get('outputs')
            if not isinstance(outputs, list) or not outputs:
                raise MigrationError('Implemented features require target file evidence')
            for output in outputs:
                dest = safe_child(target, output['path'])
                if not dest.is_file() or digest(dest.read_bytes()) != output.get('sha256'):
                    raise MigrationError('Missing or changed feature output')
        else:
            gaps.append(key)
    gaps += sorted(set(expected) - seen)
    return {'complete': not gaps, 'gaps': gaps, 'review_required': [i['feature_id'] for i in coverage['items'] if i.get('status') == 'not_applicable']}


def compare_behavior(source, target, oracle_bundle, observations, output):
    from .evidence import validate
    source, target = source.resolve(), target.resolve()
    proof = validate(source, oracle_bundle)
    if proof['kind'] not in {'source_tests', 'source_scenario'}:
        raise MigrationError('Oracle requires source test/scenario evidence')
    manifest = read_json(oracle_bundle / 'manifest.json')
    if 'artifacts/oracle.json' not in manifest['artifacts']:
        raise MigrationError('Bundle must contain hashed artifacts/oracle.json')
    expected = read_json(oracle_bundle / 'artifacts/oracle.json')
    actual = read_json(observations)
    target_hash = snapshot(target)['sha256']
    if actual.get('target_sha256') != target_hash:
        raise MigrationError('Target observations refer to another target snapshot')
    def cases(value):
        result = {}
        if not isinstance(value.get('cases'), list) or not value['cases']:
            raise MigrationError('Comparison needs nonempty cases')
        for case in value['cases']:
            if not isinstance(case.get('id'), str) or case['id'] in result:
                raise MigrationError('Invalid/duplicate case ID')
            result[case['id']] = case
        return result
    left, right = cases(expected), cases(actual)
    results = []
    for key in sorted(set(left) | set(right)):
        passed = key in left and key in right and 'expected' in left[key] and 'actual' in right[key]
        if passed:
            passed = json_bytes(left[key]['expected']) == json_bytes(right[key]['actual'])
        results.append({'id': key, 'passed': passed, 'feature_id': left.get(key, {}).get('feature_id')})
    report = {'schema_version': SCHEMA, 'source_sha256': proof['source_sha256'], 'target_sha256': target_hash,
              'oracle_manifest_sha256': digest((oracle_bundle / 'manifest.json').read_bytes()),
              'observations_sha256': digest(observations.read_bytes()), 'cases': results,
              'status': 'observations_equal' if all(r['passed'] for r in results) else 'observations_differ',
              'scope': 'Supplied cases only; capture authenticity and unobserved behavior are not proven'}
    if any(output.resolve().is_relative_to(p) or p.is_relative_to(output.resolve()) for p in (source, target)):
        raise MigrationError('Comparison output must be separate from source and target')
    write_new_tree(output, {'comparison.json': json_bytes(report)})
    return report


def pipeline_status(run):
    run = run.resolve()
    metadata = read_json(run / 'run.json')
    source, target = Path(metadata['source_root']), run / 'target'
    result = {'schema_version': SCHEMA, 'stages': {}, 'migration_complete': False, 'gaps': []}
    if source_snapshot(source)['sha256'] != metadata['source_sha256']:
        return {**result, 'status': 'stale_source', 'gaps': ['Reinitialize after source changes']}
    facts = validate_facts(read_json(run / 'spec/facts.json'))
    if facts['source_snapshot']['sha256'] != metadata['source_sha256']:
        raise MigrationError('Spec does not match run source')
    result['stages']['spec'] = 'facts_available'
    plan = read_json(run / 'plan/features.json')
    original = {f['path']: f['sha256'] for f in facts['source_snapshot']['files']}
    planned = {f['source_path']: f['source_sha256'] for f in plan['features']}
    if original != planned or plan.get('source_sha256') != metadata['source_sha256']:
        raise MigrationError('Plan must account for every original source file with current hashes')
    if len({f['id'] for f in plan['features']}) != len(plan['features']):
        raise MigrationError('Every functional feature needs a unique ID, even when several refer to one file')
    result['stages']['plan'] = 'coverage_plan_available'
    coverage_path = run / 'execute/coverage.json'
    if not coverage_path.exists():
        result['stages']['execute'] = 'pending'
        result['gaps'].append('execute/coverage.json is missing')
    else:
        coverage = read_json(coverage_path)
        if coverage.get('source_sha256') != metadata['source_sha256']:
            raise MigrationError('Coverage does not match run source')
        checked = check_coverage(source, target, plan['features'], coverage)
        result['stages']['execute'] = 'outputs_accounted' if checked['complete'] else 'partial'
        result['coverage'] = checked
        if checked['gaps']:
            result['gaps'].append('Source features still lack target implementation')
    build_path = run / 'verify/build/build.json'
    compare_path = run / 'verify/behavior/comparison.json'
    result['stages']['verify'] = 'pending'
    if build_path.exists() and compare_path.exists() and target.is_dir():
        build, behavior = read_json(build_path), read_json(compare_path)
        build_passed = (build.get('status') == 'build_passed' and build.get('exit_code') == 0 and
                        build.get('hvigor_success_marker') is True and
                        build.get('source_sha256') == metadata['source_sha256'] and
                        build.get('target_after_sha256') == snapshot(target)['sha256'])
        artifact_checks = []
        for item in build.get('artifacts', []):
            path = safe_child(target, item['path'])
            artifact_checks.append(path.is_file() and digest(path.read_bytes()) == item['sha256'])
        observed_ids = {c.get('feature_id') for c in behavior.get('cases', []) if c.get('passed')}
        implemented = {i['feature_id'] for i in read_json(coverage_path).get('items', []) if i.get('status') == 'implemented'} if coverage_path.exists() else set()
        cases = behavior.get('cases')
        behavior_passed = (isinstance(cases, list) and bool(cases) and all(c.get('passed') is True for c in cases)
            and len({c.get('id') for c in cases}) == len(cases) and behavior.get('status') == 'observations_equal'
            and behavior.get('source_sha256') == metadata['source_sha256'] and behavior.get('target_sha256') == snapshot(target)['sha256'])
        if build_passed and artifact_checks and all(artifact_checks) and behavior_passed and implemented.issubset(observed_ids):
            result['stages']['verify'] = 'recorded_checks_passed'
        else:
            result['gaps'].append('Build/behavior evidence is failed, stale or incomplete')
    else:
        result['gaps'].append('Build and source/target behavior evidence are required')
    # Code and evidence checks do not authenticate captures or waive platform/visual gaps.
    findings_path = run / 'verify/findings.json'
    if findings_path.exists():
        findings = read_json(findings_path)
        if not isinstance(findings, dict) or not isinstance(findings.get('findings'), list):
            raise MigrationError('Verification findings must contain an array')
        if any(not isinstance(f, dict) or not isinstance(f.get('id'), str) or f.get('status') not in {'open', 'blocked', 'closed'} for f in findings['findings']):
            raise MigrationError('Verification findings need IDs and open/blocked/closed status')
        unresolved = [f['id'] for f in findings['findings'] if f['status'] != 'closed']
        if unresolved:
            result['open_findings'] = unresolved
            result['gaps'].append('Verification findings are still open')
    report_path = run / 'retrospect/report.md'
    report_available = report_path.is_file() and bool(report_path.read_text(encoding='utf-8-sig').strip())
    result['stages']['retrospect'] = 'report_available' if report_available else 'pending'
    if not report_available:
        result['gaps'].append('retrospect/report.md is missing or empty')
    result['status'] = 'ready_for_acceptance_review' if not result['gaps'] else 'in_progress'
    result['acceptance_notes'] = ['Review not_applicable reasons', 'Review source observation provenance',
                                  'Complete required device, visual, accessibility and performance checks']
    return result
