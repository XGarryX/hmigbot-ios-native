"""Read-only settings/click effect review over actual declared case observations.

No keyword hit or reviewer checkbox proves business behavior. Selected effects
need independent source oracles and actual current process outputs; device
authenticity remains the existing backend's separately reported responsibility.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core import MigrationError, digest, json_bytes, read_json, source_snapshot
from .receipt_outputs import regular_path

STAGES = {'setting': ('default', 'save', 'reload', 'business_effect'),
          'click': ('input', 'processing', 'side_effect', 'feedback')}


def _at(value, path):
    if not isinstance(path, list) or not path or any(not isinstance(k, str) or not k for k in path):
        raise MigrationError('Effect stage needs a nonempty object-key path')
    for key in path:
        if not isinstance(value, dict) or key not in value:
            raise MigrationError('Effect value missing at ' + '.'.join(path))
        value = value[key]
    return value


def review(project, source, graph, spec, observations):
    """Consume the original behavior command's in-memory observations."""
    project, source = Path(project), Path(source)
    selected = spec.get('effect_review', {})
    if not isinstance(selected, dict):
        raise MigrationError('effect_review must be an object')
    if not selected or selected.get('selected') is not True:
        return {'status': 'not_selected', 'findings': [], 'behavior_verified': False,
                'scope': 'settings/click effects not selected; ordinary behavior cases retain original scope'}
    if (not isinstance(selected, dict) or set(selected) - {'selected', 'chains'}
            or not isinstance(selected.get('chains'), list)):
        raise MigrationError('Invalid selected effect_review')
    if graph.get('source_sha256') != source_snapshot(source)['sha256'] or spec.get('source_sha256') != graph['source_sha256']:
        raise MigrationError('Effect review requires the current independent iOS source')
    facts = {f['id']: f for f in graph['facts']}
    cases = {c['id']: c for c in spec.get('cases', [])}
    observed = {o['id']: o for o in observations}
    findings, results, seen = [], [], set()

    def issue(chain, stage, rule, detail, confirmed=False):
        ident = str(chain.get('id', 'unknown'))
        findings.append({'id': 'effect-' + digest((rule + ':' + ident + ':' + stage).encode())[:20],
            'rule': rule, 'subject': ident, 'stage': stage, 'detail': detail,
            'source_fact': chain.get('source_fact'), 'case_id': chain.get('case_id'),
            'ac_ids': chain.get('ac_ids', []), 'owner': chain.get('owner'),
            'status': 'confirmed_failure' if confirmed else 'unverified'})

    for chain in selected['chains']:
        if not isinstance(chain, dict):
            raise MigrationError('Effect chains must be objects')
        ident, kind = chain.get('id'), chain.get('kind')
        if not isinstance(ident, str) or not ident or ident in seen or kind not in STAGES:
            raise MigrationError('Effect chain ID/kind is missing, duplicate or invalid')
        seen.add(ident)
        fact, case = facts.get(chain.get('source_fact')), cases.get(chain.get('case_id'))
        expected_kind = 'persistence' if kind == 'setting' else 'event'
        if fact is None or fact.get('kind') != expected_kind or case is None:
            issue(chain, 'source', 'IOS.EFFECT_SOURCE', 'No current independent source fact and declared behavior case'); continue
        ids = chain.get('ac_ids')
        if (not isinstance(ids, list) or not ids or len(set(ids)) != len(ids) or
                not set(ids) <= set(case.get('ac_ids', [])) or not isinstance(chain.get('owner'), str) or not chain['owner']):
            issue(chain, 'ownership', 'IOS.EFFECT_OWNERSHIP', 'Effect requires owned ACs from this case and a repair owner'); continue
        oracle = case.get('oracle', {})
        if oracle.get('source_fact') != chain['source_fact'] or not oracle.get('reviewer') or 'expected' not in oracle:
            issue(chain, 'oracle', 'IOS.EFFECT_ORACLE', 'Missing independent reviewed source expectation'); continue
        stages = chain.get('stages')
        if not isinstance(stages, dict) or set(stages) != set(STAGES[kind]):
            issue(chain, 'chain', 'IOS.EFFECT_CHAIN', 'Required stages: ' + ', '.join(STAGES[kind])); continue
        if any(not isinstance(p, list) or not p or any(not isinstance(k, str) or not k for k in p) for p in stages.values()) or len({tuple(p) for p in stages.values()}) != len(stages):
            issue(chain, 'chain', 'IOS.EFFECT_CHAIN', 'Each stage needs its own concrete observed value path; one saved field cannot prove all effects'); continue
        targets = case.get('target_hashes')
        if (not isinstance(targets, dict) or not targets or any(
                digest(regular_path(project, p).read_bytes()) != sha for p, sha in targets.items())):
            issue(chain, 'target', 'IOS.EFFECT_TARGET', 'Current target inputs for the actual behavior process are missing or stale'); continue
        result = {'id': ident, 'kind': kind, 'case_id': case['id'], 'owner': chain['owner'], 'stages': {}}
        observation = observed.get(case['id'])
        output = None
        if observation and observation.get('status') in {'observed_pass', 'observed_fail'}:
            log = regular_path(project, 'spec/reports/behavior/' + case['id'] + '/stdout.log')
            if (not log.is_file() or digest(log.read_bytes()) != observation.get('stdout_sha256')
                    or observation.get('command') != case.get('command')):
                issue(chain, 'observation', 'IOS.EFFECT_EVIDENCE', 'Original process output/command is missing or changed'); continue
            try:
                output = read_json(log)
            except MigrationError:
                output = None
            if output != observation.get('actual') or observation.get('exit_code') != 0:
                issue(chain, 'observation', 'IOS.EFFECT_PROCESS', 'Effect process did not return a valid successful observation', True); continue
        for stage in STAGES[kind]:
            try:
                expected = _at(oracle['expected'], stages[stage])
            except MigrationError as exc:
                issue(chain, stage, 'IOS.EFFECT_ORACLE', str(exc)); result['stages'][stage] = 'unverified'; continue
            if output is None:
                issue(chain, stage, 'IOS.EFFECT_NOT_RUN', 'No actual current execution for this effect stage')
                result['stages'][stage] = 'not_run'; continue
            try:
                actual = _at(output, stages[stage])
            except MigrationError as exc:
                issue(chain, stage, 'IOS.EFFECT_MISSING', str(exc), True); result['stages'][stage] = 'failed'; continue
            if json_bytes(actual) != json_bytes(expected):
                issue(chain, stage, 'IOS.EFFECT_MISMATCH', 'Observed value differs from independent iOS expectation', True)
                result['stages'][stage] = {'status': 'failed', 'expected': expected, 'actual': actual}
            else:
                result['stages'][stage] = {'status': 'observed_match', 'value': actual}
        results.append(result)
    if not selected['chains']:
        findings.append({'id': 'effect-empty', 'rule': 'IOS.EFFECT_SCOPE_EMPTY', 'subject': 'effect_review',
                         'stage': 'scope', 'status': 'unverified', 'detail': 'Selected effect review has no cases'})
    confirmed = any(f['status'] == 'confirmed_failure' for f in findings)
    return {'schema_version': 1, 'status': 'FAIL' if confirmed else 'UNVERIFIED' if findings else 'PASS',
            'findings': findings, 'chains': results, 'behavior_verified': not findings and bool(results),
            'source_sha256': graph['source_sha256'],
            'scope': 'selected effect-stage values from original process outputs and independent source oracles; not full device or call-graph validation'}


def replay(project):
    """Recheck a saved current behavior report without invoking any command."""
    from .quality_views import spec_inputs, target_inputs
    project = Path(project).resolve()
    cfg = read_json(regular_path(project, '.migbot/config.json'))
    source = Path(cfg['ios']); source = source if source.is_absolute() else project / source
    report = read_json(regular_path(project, 'spec/reports/ios-behavior-check.json'))
    spec_path = regular_path(project, 'spec/verification/ios-behavior.json')
    if (report.get('verification_sha256') != digest(spec_path.read_bytes()) or
            report.get('spec_input_hashes') != spec_inputs(project) or report.get('target_input_hashes') != target_inputs(project)
            or report.get('source_sha256') != source_snapshot(source)['sha256']):
        raise MigrationError('Saved behavior report is stale; rerun the original behavior-check')
    # Replay the original authoritative graph validator; a source_fact spelling
    # copied into a case cannot create an independent fact or its semantic kind.
    spec = read_json(spec_path)
    from .ios_facts import validate_graph
    graph, _ = validate_graph(source, project)
    return review(project, source, graph, spec, report.get('observations', []))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        value = replay(args.project)
        print(json.dumps(value, ensure_ascii=False, indent=2))
        return 2 if value['status'] == 'FAIL' else 3 if value['status'] == 'UNVERIFIED' else 0
    except (MigrationError, OSError, KeyError, TypeError, ValueError) as exc:
        print(json.dumps({'status': 'blocked', 'error': str(exc), 'recovery': 'rerun original behavior-check with current independent effect cases'}, ensure_ascii=False))
        return 2
