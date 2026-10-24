"""Consumer contract checks; synthetic review/build fixtures are not runtime proof."""
from copy import deepcopy
import os
from pathlib import Path
import plistlib
import sys

import pytest

ROOT = Path(os.environ.get('HMIGBOT_TEST_RUNTIME', Path(__file__).resolve().parents[1])).resolve()
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'tests'))

from hmigbot_ios.core import MigrationError, digest, json_bytes, read_json, write_json
from hmigbot_ios.ios_facts import RULES
from hmigbot_ios.ios_harness import ac_inventory, check, validate_native_claims
from hmigbot_ios.native_authoring import prepare, render
from hmigbot_ios.native_pipeline import check_source, configure, index_source
from hmigbot_ios.native_semantics import required_facts, validate_native_payload
from hmigbot_ios.source_responsibility import load_and_validate
from test_source_responsibility import case, replacement


def persist(c):
    """Use real graph/parser/projection with the shared synthetic compiler captures."""
    from hmigbot_ios.ios_harness import initialize
    configure(c['source'], c['project'])
    initialize(c['project'])
    index_source(c['project'])
    path = c['project'] / 'spec/baseline/features/F001-private.md'
    path.write_text(path.read_text().replace('---\nsource_anchors:', '---\nsource_platform: ios\nsource_anchors:')
                    .replace('判:device | 实际窗口', '判:unit | 公共窗口请求及应用赋值保留'))
    sem, _ = replacement(c)
    doc = sem['documents'][0]
    doc.update(languages=['objc'], frameworks=['nonvisual'])
    for dim in required_facts('feature', {'objc'}, {'nonvisual'}):
        if dim == 'state_transitions':
            continue
        facts = [f for f in c['graph']['facts'] if dim in RULES[f['kind']]['dimensions']]
        doc['facts'][dim] = ({'status': 'known', 'value': {'reviewed': 'Synthetic source token'},
            'fact_ids': [f['id'] for f in facts],
            'evidence': [{'path': f['anchor']['path'], 'line': f['anchor']['line']} for f in facts]}
            if facts else {'status': 'not_applicable', 'reason': 'Complete fixture source has no operation'})
    write_json(c['project'] / 'spec/baseline/ios-semantics.json', sem)
    write_json(c['project'] / 'spec/baseline/ios-responsibility.json', c['payload'])
    projection = load_and_validate(c['project'], c['source'], c['graph'], c['obs'])
    rows = []
    for obligation in c['obs']['obligations']:
        row = {'obligation_id': obligation['id'], 'ac_ids': ['F001-AC02'],
               'source_review': {'status': 'reviewed', 'input': 'open', 'processing': 'request',
                                 'observable': 'window', 'reviewer': 'fixture-reader'}}
        if obligation['id'] in projection.historical_obligation_ids:
            row.update(ac_ids=[], responsibility_ref='B-private')
        rows.append(row)
    write_json(c['project'] / 'spec/baseline/ios-coverage.json',
        {'schema_version': 2, 'graph_sha256': digest(json_bytes(c['graph'])), 'mappings': rows})
    return sem, projection


def bytes_of(project):
    return {p.relative_to(project).as_posix(): p.read_bytes() for p in project.rglob('*') if p.is_file()}


def candidate_request(c, sem):
    request = prepare(c['project'])['input_template']
    request.update(documents=deepcopy(sem['documents']), dispositions=[],
                   truth_anchors=[{'ac_id': 'F001-AC01', 'path': 'Private.m', 'line': 2}])
    return request


def test_valid_projection_is_consumed_without_claim_relabel_or_project_write(case):
    sem, projection = persist(case)
    before, source_before = bytes_of(case['project']), bytes_of(case['source'])
    result, _ = check_source(case['project'], report_only=True)
    assert result['findings'] == []
    report, _ = check(case['project'], report_only=True)
    for stage in ('source_contract', 'responsibility', 'coverage', 'native_claims'):
        assert report['checks'][stage]['status'] == 'PASS', report
    assert report['responsibility_counts'] == projection.counts
    assert report['obligation_treatments'] == projection.treatments
    assert report['historical_obligation_ids'] == list(projection.historical_obligation_ids)
    assert report['source_history_acceptance_ids'] == ['F001-AC01']
    assert report['acceptance_counts'] == {'all': 2, 'active_target': 1, 'source_history': 1}
    result = render(case['project'], candidate_request(case, sem))
    assert result['files']['spec/baseline/ios-semantics.json'] == sem
    assert result['status'] == 'candidate' and not result['spec_complete'] and not result['behavior_verified']
    assert projection.frozen_inputs().items() <= result['input_hashes'].items()
    assert sem['documents'][0]['facts']['state_transitions']['status'] == 'unknown'
    assert bytes_of(case['project']) == before and bytes_of(case['source']) == source_before


def test_absent_payload_preserves_legacy_unknown_fail_closed(case):
    sem, _ = persist(case)
    (case['project'] / 'spec/baseline/ios-responsibility.json').unlink()
    assert 'IOS.NATIVE_FACT_UNKNOWN' in {f['rule'] for f in check_source(case['project'], report_only=True)[0]['findings']}
    with pytest.raises(MigrationError, match='incomplete'):
        render(case['project'], candidate_request(case, sem))
    assert set(ac_inventory(case['project'])) == {'F001-AC01', 'F001-AC02'}


def test_explicit_responsibility_candidate_is_only_an_output_not_gate_authority(case):
    sem, _ = persist(case)
    (case['project'] / 'spec/baseline/ios-responsibility.json').unlink()
    request = candidate_request(case, sem)
    request['responsibility'] = case['payload']
    before = bytes_of(case['project'])
    result = render(case['project'], request)
    assert result['files']['spec/baseline/ios-responsibility.json'] == case['payload']
    assert result['responsibility_candidate'] is True
    assert result['candidate_hashes']['responsibility'] == digest(json_bytes(case['payload']))
    assert result['candidate_hashes']['native_semantics'] == digest(json_bytes(sem))
    assert bytes_of(case['project']) == before
    assert 'IOS.NATIVE_FACT_UNKNOWN' in {f['rule'] for f in check_source(case['project'], report_only=True)[0]['findings']}


@pytest.mark.parametrize('mutation', ['missing_value', 'missing_evidence', 'missing_fact_ids', 'private_as_known',
                                    'claim_drift', 'unapproved', 'stale_review', 'app_unknown'])
def test_invalid_or_incomplete_proof_never_suppresses_product_blockers(case, mutation):
    sem, _ = persist(case)
    claim = sem['documents'][0]['facts']['state_transitions']
    if mutation.startswith('missing_'):
        claim['parts'][1].pop(mutation.removeprefix('missing_'))
    elif mutation == 'private_as_known':
        claim['parts'][0].update(status='known', value={'pretend': 'complete'})
    elif mutation == 'claim_drift':
        claim['reason'] += ' changed'
    elif mutation == 'app_unknown':
        claim['parts'][1] = {'id': 'app', 'status': 'unknown', 'reason': 'Still unresolved',
                             'fact_ids': claim['parts'][1]['fact_ids']}
    elif mutation == 'unapproved':
        path = case['project'] / 'spec/decision-ledger.md'
        path.write_text(path.read_text().replace('approved', 'proposed'))
        case['payload']['replacements'][0]['decision_sha256'] = digest(path.read_bytes())
    else:
        path = case['project'] / case['payload']['review']['path']
        path.write_bytes(path.read_bytes() + b'\n ')
    if mutation != 'claim_drift':
        case['payload']['replacements'][0]['semantic_parts'][0]['claim_sha256'] = digest(json_bytes(claim))
    write_json(case['project'] / 'spec/baseline/ios-semantics.json', sem)
    write_json(case['project'] / 'spec/baseline/ios-responsibility.json', case['payload'])
    report, code = check(case['project'], report_only=True)
    assert code == 2
    assert report['checks']['responsibility']['status'] == 'FAIL'
    assert report['checks']['coverage']['status'] == report['checks']['native_claims']['status'] == 'not_run'
    with pytest.raises(MigrationError):
        ac_inventory(case['project'])
    with pytest.raises(MigrationError):
        prepare(case['project'])


@pytest.mark.parametrize('mutation', ['missing_history', 'wrong_history_ref', 'history_target_ac',
                                    'product_history_ref', 'product_old_ac', 'history_preview_forgery'])
def test_coverage_keeps_history_and_requires_current_product_acs(case, mutation):
    _, projection = persist(case)
    path = case['project'] / 'spec/baseline/ios-coverage.json'
    coverage = read_json(path)
    history = next(r for r in coverage['mappings'] if r['obligation_id'] in projection.historical_obligation_ids)
    product = next(r for r in coverage['mappings'] if r['obligation_id'] in projection.product_obligation_ids)
    if mutation == 'missing_history':
        coverage['mappings'].remove(history)
    elif mutation == 'wrong_history_ref':
        history['responsibility_ref'] = 'B-missing'
    elif mutation == 'history_target_ac':
        history['ac_ids'] = ['F001-AC02']
    elif mutation == 'product_history_ref':
        product.update(ac_ids=[], responsibility_ref='B-private')
    elif mutation == 'product_old_ac':
        product['ac_ids'] = ['F001-AC01']
    else:
        history['disposition'] = 'preview-only'
        (case['project'] / 'spec/baseline/skip-list.md').write_text('# Scope\n## Private boundary\nPrivate.m open\n')
    write_json(path, coverage)
    report, code = check(case['project'], report_only=True)
    assert code == 2 and report['checks']['coverage']['status'] == 'FAIL'


def test_hand_edited_requirements_index_cannot_reactivate_historical_ac(case):
    persist(case)
    write_json(case['project'] / 'spec/baseline/requirements-index.json',
               {'requirements': [{'requirement_id': 'F001-AC01', 'status': 'active'}]})
    assert set(ac_inventory(case['project'])) == {'F001-AC02'}


def test_real_source_state_cannot_be_replaced_by_empty_or_forged_typed_states(tmp_path):
    from test_ios_harness import fixture
    _, project, graph = fixture(tmp_path)
    sem = read_json(project / 'spec/baseline/ios-semantics.json')
    page = next(d for d in sem['documents'] if d['kind'] == 'page')
    assert any(f['kind'] == 'state' for f in graph['facts'])
    for value in ({'states': []}, {'states': [{'owner': 'Pretend'}]}):
        page['facts']['state_ownership']['value'] = value
        issues = []
        validate_native_claims(project, graph, sem, lambda *i: issues.append(i))
        assert 'IOS.STATE_VALUE_CONTRADICTION' in {i[0] for i in issues}


@pytest.mark.parametrize('fmt', [plistlib.FMT_BINARY, plistlib.FMT_XML])
def test_authoring_inventory_and_native_evidence_read_plist_in_real_format(tmp_path, fmt):
    from test_ios_harness import fixture
    source, project, _ = fixture(tmp_path, resources={'Info.plist': plistlib.dumps({'CFBundleName': '合法资源'}, fmt=fmt)})
    for path in (project / 'spec/baseline').rglob('*.md'):
        text = path.read_text()
        if '  - path: Counter.swift' in text:
            path.write_text(text.replace('  - path: Counter.swift', '  - path: Counter.swift\n  - path: Info.plist'))
    plan = prepare(project)
    info = next(a for a in plan['documents'][0]['source_anchors'] if a['path'] == 'Info.plist')
    assert info['content_validation'] == 'parsed' and info['format'] == 'plist'
    assert info['coordinate_kind'] == ('resource_document' if fmt == plistlib.FMT_BINARY else 'text_line')
    sem = read_json(project / 'spec/baseline/ios-semantics.json')
    # The shared fixture already records resource composition evidence on the
    # page. Give every such existing evidence item the same explicit format
    # coordinates as the new feature claim; binary resources have no text line.
    for doc in sem['documents']:
        for claim in doc['facts'].values():
            for evidence in claim.get('evidence', []):
                if evidence['path'] == 'Info.plist':
                    evidence['coordinate_kind'] = info['coordinate_kind']
                    evidence['source_sha256'] = digest((source / 'Info.plist').read_bytes())
    sem['documents'][0]['facts']['entrypoints'] = {'status': 'known', 'value': {'metadata': 'reviewed'},
        'evidence': [{'path': 'Info.plist', 'line': 1, 'coordinate_kind': info['coordinate_kind'],
                      'source_sha256': digest((source / 'Info.plist').read_bytes())}]}
    docs = {d['id']: (d['kind'], ['Counter.swift', 'Info.plist']) for d in sem['documents']}
    issues = []
    validate_native_payload(source, project, docs, {'Counter.swift', 'Info.plist'}, lambda *i: issues.append(i), sem)
    assert issues == []
    if fmt == plistlib.FMT_BINARY:
        for mutation in ('coordinate', 'hash', 'line', 'missing_coordinate', 'missing_hash'):
            altered = deepcopy(sem)
            evidence = altered['documents'][0]['facts']['entrypoints']['evidence'][0]
            if mutation == 'coordinate': evidence['coordinate_kind'] = 'text_line'
            elif mutation == 'hash': evidence['source_sha256'] = '0' * 64
            elif mutation == 'missing_coordinate': evidence.pop('coordinate_kind')
            elif mutation == 'missing_hash': evidence.pop('source_sha256')
            else: evidence['line'] = 2
            issues = []
            validate_native_payload(source, project, docs, {'Counter.swift', 'Info.plist'}, lambda *i: issues.append(i), altered)
            assert 'IOS.NATIVE_FACT_EVIDENCE' in {i[0] for i in issues}


def test_binary_resource_is_never_source_truth_or_corrupt_code_fallback(tmp_path):
    from test_ios_harness import fixture
    from hmigbot_ios.native_contract import source_truth
    source, project, _ = fixture(tmp_path, resources={'Info.plist': plistlib.dumps({'name': 'resource'}, fmt=plistlib.FMT_BINARY)})
    with pytest.raises((MigrationError, UnicodeError)):
        source_truth(source, ['Info.plist'], 'Info.plist', 1)
    (source / 'Counter.swift').write_bytes(b'\xff\xfeinvalid')
    sem = read_json(project / 'spec/baseline/ios-semantics.json')
    issues = []
    validate_native_payload(source, project, {d['id']: (d['kind'], ['Counter.swift']) for d in sem['documents']},
        {'Counter.swift'}, lambda *i: issues.append(i), sem)
    assert 'IOS.NATIVE_FACT_EVIDENCE' in {i[0] for i in issues}
