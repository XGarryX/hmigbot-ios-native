"""iOS contract gates shared by skills, dispatch and receipt landing."""
from __future__ import annotations

import json
import re
from pathlib import Path

from .core import MigrationError, digest, json_bytes, read_json, safe_child, write_json
from .ios_facts import RULES, validate_graph


def initialize(project: Path, *, import_legacy=False):
    from .native_pipeline import context
    source, project = context(project)
    cfg_path = project / '.migbot/config.json'
    cfg = read_json(cfg_path)
    marker = cfg.get('ios_harness')
    contract_version = marker.get('spec_contract_version', 1) if isinstance(marker, dict) else 2
    if type(contract_version) is not int or contract_version not in (1, 2):
        raise MigrationError('Unsupported spec contract version; preserve the current baseline')
    if marker and marker.get('version') != 2:
        raise MigrationError('Unsupported harness version; do not overwrite state')
    if (project / 'spec/state/state.json').exists() and not marker:
        raise MigrationError('Existing state writer must be retired before adopting the iOS harness')
    legacy = project / 'spec/baseline/ios-semantics.json'
    if legacy.exists() and read_json(legacy).get('schema_version') != 2:
        if not import_legacy:
            raise MigrationError('Existing v1 baseline needs explicit import-legacy; preserve stable IDs')
        original = read_json(legacy)
        archive = project / 'spec/.a2h/legacy-0.5.0'
        for name in ('ios-semantics.json', 'ios-source-check.json', 'verification.json', 'impl-claims.json'):
            path = project / 'spec/baseline' / name
            if path.exists() and not (archive / name).exists():
                write_json(archive / name, read_json(path))
        migrated = {**original, 'schema_version': 2, 'imported_from': '0.5.0'}
        for doc in migrated.get('documents', []):
            for field, value in doc.get('facts', {}).items():
                doc['facts'][field] = {'status': 'unknown', 'reason': 'Imported v1 claim requires typed facts and independent review', 'legacy_claim': value}
        write_json(legacy, migrated)
    cfg['ios_harness'] = {'version': 2, 'spec_contract_version': contract_version,
                          'scheduler': 'hmigbot-codex-1.7.0',
                          'state_writer': 'state_update.py', 'journal_writer': 'land_results.py',
                          'dispatch_writer': 'next_batch.py', 'legacy_pass_inherited': False}
    cfg['ios_expertise'] = {'version': 1, 'required': False}
    write_json(cfg_path, cfg)
    return {'status': 'initialized', 'harness_version': 2, 'legacy_pass_inherited': False, 'source': str(source)}


def responsibility(project, *, source=None, graph=None, obligations=None, semantics=None, candidate=None):
    """The sole optional source/target authority; absence retains legacy strictness."""
    project = Path(project)
    if candidate is None and not (project / 'spec/baseline/ios-responsibility.json').is_file():
        return None
    if source is None:
        from .native_pipeline import context
        source, project = context(project)
    if graph is None or obligations is None:
        graph, obligations = validate_graph(source, project)
    from .source_responsibility import load_and_validate
    return load_and_validate(project, source, graph, obligations, semantics=semantics, candidate=candidate)


def ac_inventory(project, *, projection=None):
    from .spec_contract import acceptance
    from .native_pipeline import source_paths
    from .artifact_contract import _primary_feature
    acs = {}
    documents = sorted((project / 'spec/baseline/features').glob('F*.md'))
    owners = {}
    for doc in documents:
        if _primary_feature(doc):
            feature = re.match(r'F\d+', doc.name)[0]
            if feature in owners:
                raise MigrationError('Duplicate feature owner: ' + feature)
            owners[feature] = doc
    for doc in documents:
        text = doc.read_text(encoding='utf-8-sig')
        feature = re.match(r'F\d+', doc.name)[0]
        for ident, body in acceptance(text):
            if ident in acs:
                raise MigrationError('Duplicate acceptance ID: ' + ident)
            if ident.split('-AC', 1)[0] != feature or feature not in owners:
                raise MigrationError('Acceptance ID must belong to its main feature: ' + ident)
            judgment = re.search(r'判:(static|unit|contract|route|ui|visual|device)\s*\|', body)
            if not judgment:
                raise MigrationError('Missing judgment: ' + ident)
            owner = owners[feature]
            acs[ident] = {'judgment': judgment[1], 'body': body, 'feature_id': feature,
                         'document': doc.relative_to(project).as_posix(),
                         'owner_document': owner.relative_to(project).as_posix(),
                         'source_paths': source_paths(owner.read_text(encoding='utf-8-sig'))}
    if not acs:
        raise MigrationError('No stable acceptance criteria exist')
    projection = projection if projection is not None else responsibility(project)
    if projection is not None:
        projection.validate_frozen_inputs(project)
        acs = {ident: row for ident, row in acs.items() if ident in projection.target_acceptance_ids}
        if set(acs) != set(projection.target_acceptance_ids):
            raise MigrationError('Active acceptance criteria differ from the original freshly compiled inventory')
    return acs


def _coverage_source_paths(project, source, ident, ac):
    """Declared ownership and exact shared contracts, never inferred prose meaning.

    Referencing one shared section does not grant all anchors of its document.
    Only real source evidence in that section (or an active action explicitly
    bound to this AC) extends the feature's own file boundary. Existing contract
    checks remain responsible for the rest of the shared contract's validity.
    """
    from .artifact_contract import SOURCE_REF, _anchor, _visible_lines, json_blocks, validate_json
    from .spec_contract import references
    paths = set(ac['source_paths'])
    pending = [safe_child(project, path) for path in {ac['document'], ac['owner_document']}]
    visited = set()
    while pending:
        document = pending.pop()
        if document in visited:
            continue
        visited.add(document)
        for target, _, body in references(project, document, document.read_text(encoding='utf-8-sig')):
            # A precise contract_ref is the explicit consumer relationship.
            # Ignore code examples; typed action fences have a separate reader.
            for _, line in _visible_lines(body):
                for match in SOURCE_REF.finditer(line):
                    anchor = {'path': match['path'].strip(), 'line': int(match['line'])}
                    _anchor(source, anchor)
                    if match['end']:
                        end = int(match['end'])
                        if end < anchor['line']:
                            raise MigrationError('Shared source range ends before it starts')
                        _anchor(source, {**anchor, 'line': end})
                    paths.add(anchor['path'])
            for block in json_blocks(body):
                if block['kind'] != 'action-contract':
                    continue
                value = json.loads(block['body'])
                validate_json(value, 'action_contract')
                if (value['scope'] == 'active' and value['owner'] == ac['feature_id']
                        and ident in value['ac_ids']):
                    for anchor in value['source_anchors']:
                        _anchor(source, anchor)
                        paths.add(anchor['path'])
            pending.append(target)
    return paths


def validate_native_claims(project, graph, semantics, fail, *, projection=None):
    """Shared v2 claim checks for the formal gate and authoring candidates."""
    from .native_pipeline import source_paths
    if projection is not None:
        projection.validate_frozen_inputs(project)
    facts = {f['id']: f for f in graph['facts']}
    for doc in semantics.get('documents', []):
        anchors = set()
        folder = 'ui' if doc.get('kind') == 'page' else 'features'
        for path in (project / 'spec/baseline' / folder).glob(doc.get('id', '') + '*.md'):
            anchors.update(source_paths(path.read_text(encoding='utf-8-sig')))
        for dimension, claim in doc.get('facts', {}).items():
            relevant = [f for f in facts.values() if f['anchor']['path'] in anchors and dimension in RULES[f['kind']]['dimensions']]
            subject = str(doc.get('id')) + ':' + dimension
            if claim.get('status') == 'unknown' and projection is not None:
                _validate_claim(project, graph, facts, anchors, dimension, subject, claim, [], fail)
                treatment = projection.semantic_requirement(doc.get('id'), dimension, claim)
                if not treatment['target_required']:
                    private_ids = {f for p in treatment['private_parts'] for f in p['fact_ids']}
                    app_relevant = [f for f in relevant if f['id'] not in private_ids]
                    retained = treatment['retained_parts']
                    combined = {f for p in retained for f in p['fact_ids']}
                    if not {f['id'] for f in app_relevant} <= combined:
                        fail('IOS.CLAIM_SIGNAL_MISSING', subject, 'Retained app dimensions omitted a source signal')
                    for part in retained:
                        part_relevant = [f for f in app_relevant if f['id'] in part['fact_ids']]
                        _validate_claim(project, graph, facts, anchors, dimension, subject + ':' + part['id'], part, part_relevant, fail)
                    continue
            _validate_claim(project, graph, facts, anchors, dimension, subject, claim, relevant, fail)


def _validate_claim(project, graph, facts, anchors, dimension, subject, claim, relevant, fail):
    tool_ids = claim.get('tool_evidence_ids', [])
    if not isinstance(tool_ids, list):
        raise MigrationError('tool_evidence_ids must be a list')
    if tool_ids:
        from .source_mcp import validate_captures
        validate_captures(project, graph, tool_ids, claim.get('fact_ids', []))
    if claim.get('status') == 'not_applicable' and relevant:
        fail('IOS.NA_CONTRADICTION', subject, 'Source signals require treatment: ' + ','.join(f['id'] for f in relevant))
    if claim.get('status') == 'known':
        if not isinstance(claim.get('value'), dict) or not claim['value']:
            fail('IOS.CLAIM_TYPED_VALUE', subject, 'v2 known values must be structured objects')
        refs = claim.get('fact_ids')
        if (not isinstance(refs, list) or not refs or any(not isinstance(r, str) for r in refs)
                or len(set(refs)) != len(refs)
                or any(r not in facts or facts[r]['anchor']['path'] not in anchors for r in refs)):
            fail('IOS.CLAIM_FACT_LINK', subject, 'Known claims need machine fact IDs within document source anchors')
        elif relevant and not {f['id'] for f in relevant} <= set(refs):
            fail('IOS.CLAIM_SIGNAL_MISSING', subject, 'Known dimension omitted a detected source signal')
        else:
            evidence = claim.get('evidence')
            if (not isinstance(evidence, list) or not evidence or any(not isinstance(e, dict)
                    or not isinstance(e.get('path'), str) or type(e.get('line')) is not int for e in evidence)):
                fail('IOS.CLAIM_UNRELATED_LINE', subject, 'Known claims require source evidence with path and integer line')
            elif any(not any(e['path'] == facts[r]['anchor']['path'] and facts[r]['anchor']['line'] <= e['line'] <= facts[r]['anchor']['end_line'] for r in refs) for e in evidence):
                fail('IOS.CLAIM_UNRELATED_LINE', subject, 'Evidence must intersect the linked fact spans')
        if dimension == 'state_ownership' and relevant:
            expected = [{'fact_id': f['id'], 'owner': f['owner'], **f['value']} for f in relevant if f['kind'] == 'state']
            if claim.get('value') != {'states': expected}:
                fail('IOS.STATE_VALUE_CONTRADICTION', subject, 'State owner/storage/type/initializer must match extracted declarations')


def check(project: Path, *, report_only=False):
    from .native_pipeline import context, check_source, source_paths, findings_module
    source, project = context(project)
    queue = findings_module()
    from .gate_policy import action_options, blocking_findings, normalize_findings, summary_status
    issues = []
    excluded_obligations = set()
    preview_cache = {}
    coverage_paths = {}
    extraction_dispositions = []

    def fail(rule, subject, detail):
        issues.append(queue.make(rule, 'spec', subject, detail))

    checks = {}
    values = {}

    def stage(name, action, *, dependencies=(), subject=None):
        """Independent diagnostics run even when a preceding contract failed.

        A skipped consumer is explicitly blocked, never counted as a passing
        validation. Only the original queue writer below persists the result.
        """
        blocked = [dep for dep in dependencies if checks[dep]['status'] not in {'PASS', 'needs_review', 'advisory'}]
        if blocked:
            checks[name] = {'status': 'not_run', 'blocked_dependencies': blocked,
                            'actual_call': None, 'result': 'not_run', 'evidence_paths': [],
                            'recovery': 'Restore the listed consumed prerequisites; independent checks remain available.'}
            return
        before = len(issues)
        try:
            values[name] = action()
        except (MigrationError, OSError, ValueError, TypeError, AttributeError,
                KeyError, IndexError) as exc:
            fail('IOS.HARNESS_CONTRACT', subject or name, str(exc))
        added = issues[before:]
        checks[name] = {'status': summary_status(added, queue=queue),
                        'finding_count': len(added),
                        'blocking_count': len(blocking_findings(added, queue=queue)),
                        'actual_call': {'kind': 'tool_gate_check', 'name': name},
                        'result': summary_status(added, queue=queue),
                        'evidence_paths': [] if report_only else ['spec/reports/ios-harness-check.json'],
                        'recovery': 'Repair only identified affected inputs and rerun this owning check; report options do not establish native verification.'}
        if name == 'expertise' and isinstance(values.get(name), dict) and values[name].get('blocking') is False:
            checks[name].update(status='advisory', result='advisory', detail=values[name])

    def configuration():
        cfg = read_json(project / '.migbot/config.json')
        if cfg.get('ios_harness', {}).get('version') != 2:
            raise MigrationError('Initialize v2 harness; legacy check results are not harness acceptance')

    def source_contract():
        # Retain original ownership/AC/native semantics checks, without writes.
        result, _ = check_source(project, report_only=True)
        issues.extend(result['findings'])

    def extraction():
        nonlocal extraction_dispositions
        from .manifest_scope import issue_dispositions
        extraction_dispositions = issue_dispositions(values['graph'][0])
        for disposition in extraction_dispositions:
            if disposition['blocking']:
                issue = disposition['issue']
                from .finding_identity import extraction_finding
                issues.append(extraction_finding(queue, issue))

    def expertise():
        from .expertise import check as check_expertise
        return check_expertise(project, source, values['graph'][0])

    def literals():
        from .ios_literals import extract_for_project
        if read_json(project / 'spec/baseline/literal-ledger.json') != extract_for_project(source, project):
            raise MigrationError('Literal ledger must be extracted from current iOS source; spec-only empty scans are insufficient')

    def semantics_input():
        semantics = read_json(project / 'spec/baseline/ios-semantics.json')
        if (not isinstance(semantics, dict) or semantics.get('schema_version') != 2
                or semantics.get('source_platform') != 'ios'
                or not isinstance(semantics.get('documents'), list)):
            raise MigrationError('Native claims require v2 semantics with source_platform=ios and a documents list')
        # Validate consumer input shape before any graph-linked claim comparison.
        # Full source ownership, required dimensions and evidence remain checked
        # by source_contract; malformed objects must not abort other stages.
        for doc in semantics['documents']:
            if (not isinstance(doc, dict) or not isinstance(doc.get('id'), str)
                    or doc.get('kind') not in ('page', 'feature')
                    or not isinstance(doc.get('facts'), dict)):
                raise MigrationError('Semantic documents require id, kind and facts object')
            for claim in doc['facts'].values():
                if not isinstance(claim, dict) or claim.get('status') not in ('known', 'unknown', 'not_applicable'):
                    raise MigrationError('Semantic claims require known, unknown or not_applicable status')
                for field in ('fact_ids', 'tool_evidence_ids'):
                    if field in claim and (not isinstance(claim[field], list)
                            or any(not isinstance(v, str) for v in claim[field])):
                        raise MigrationError(field + ' must be a list of strings')
                if 'evidence' in claim and (not isinstance(claim['evidence'], list)
                        or any(not isinstance(e, dict) or not isinstance(e.get('path'), str)
                               or type(e.get('line')) is not int for e in claim['evidence'])):
                    raise MigrationError('Semantic evidence requires path and integer line objects')
        return semantics

    def coverage_input():
        coverage = read_json(project / 'spec/baseline/ios-coverage.json')
        if (not isinstance(coverage, dict) or coverage.get('schema_version') != 2
                or not isinstance(coverage.get('graph_sha256'), str)
                or not isinstance(coverage.get('mappings'), list)):
            raise MigrationError('Coverage requires v2 mappings and current graph_sha256')
        for mapping in coverage['mappings']:
            if not isinstance(mapping, dict) or not isinstance(mapping.get('obligation_id'), str):
                raise MigrationError('Coverage mappings require an obligation_id string')
            if ('ac_ids' in mapping and (not isinstance(mapping['ac_ids'], list)
                    or any(not isinstance(ident, str) for ident in mapping['ac_ids']))):
                raise MigrationError('Coverage ac_ids must be a list of strings')
            if 'skip_ref' in mapping and not isinstance(mapping['skip_ref'], str):
                raise MigrationError('Coverage skip_ref must be a string')
            if 'responsibility_ref' in mapping and not isinstance(mapping['responsibility_ref'], str):
                raise MigrationError('Coverage responsibility_ref must be an exact boundary ID string')
        return coverage

    def coverage_check():
        graph, obs = values['graph']
        coverage = values['coverage_input']
        if coverage['graph_sha256'] != digest(json_bytes(graph)):
            raise MigrationError('Coverage requires v2 mappings and current graph_sha256')
        facts = {f['id']: f for f in graph['facts']}
        acs, seen = values['acceptance'], set()
        projection = values['responsibility']
        expected = {o['id']: o for o in obs['obligations']}
        for mapping in coverage['mappings']:
            if not isinstance(mapping, dict):
                raise MigrationError('Coverage mapping must be an object')
            ident = mapping.get('obligation_id')
            if ident not in expected or ident in seen:
                fail('IOS.OBLIGATION_ID', str(ident), 'Unknown or duplicate obligation mapping'); continue
            seen.add(ident)
            ids = mapping.get('ac_ids', [])
            treatment = projection.treatments.get(ident) if projection is not None else None
            if treatment is not None:
                if ids or mapping.get('responsibility_ref') != treatment['boundary_ref']:
                    fail('IOS.RESPONSIBILITY_MAPPING', ident, 'Historical obligation needs its exact validated boundary ID and no target ACs')
            elif 'responsibility_ref' in mapping:
                fail('IOS.RESPONSIBILITY_MAPPING', ident, 'Product obligation cannot claim a historical boundary')
            from .source_scope import preview_source_lines
            source_fact = facts[expected[ident]['fact_id']]
            anchor = source_fact['anchor']
            if anchor['path'] not in preview_cache:
                preview_cache[anchor['path']] = preview_source_lines(safe_child(source, anchor['path']), project=project, source=source)
            preview = preview_cache[anchor['path']]
            is_preview = set(range(anchor['line'], anchor['end_line'] + 1)) <= preview
            if is_preview or mapping.get('disposition') == 'preview-only':
                from .spec_contract import sections
                review = mapping.get('source_review', {})
                skip_ref = mapping.get('skip_ref', '')
                skip_path, _, heading = skip_ref.partition('#')
                skip_text = (project / 'spec/baseline/skip-list.md').read_text(encoding='utf-8-sig')
                reviewed = (is_preview and not ids and mapping.get('disposition') == 'preview-only'
                    and mapping.get('source_sha256') == anchor['file_sha256']
                    and skip_path == 'spec/baseline/skip-list.md' and heading in sections(skip_text)
                    and anchor['path'] in sections(skip_text).get(heading, '')
                    and isinstance(review, dict) and review.get('status') == 'reviewed'
                    and all(isinstance(review.get(k), str) and review[k].strip() for k in ('input', 'processing', 'observable', 'reviewer')))
                if reviewed:
                    excluded_obligations.add(ident)
                else:
                    fail('IOS.PREVIEW_REVIEW_REQUIRED', ident, 'Keep the original obligation; exclude only exact Preview spans with current file hash, source review and skip-list heading, without product ACs')
                continue
            if treatment is not None:
                continue
            if not isinstance(ids, list) or not ids or any(not isinstance(a, str) or a not in acs for a in ids):
                fail('IOS.OBLIGATION_AC_MISSING', ident, 'Bind obligation to real stable acceptance criteria'); continue
            for ac_id in ids:
                if ac_id not in coverage_paths:
                    coverage_paths[ac_id] = _coverage_source_paths(project, source, ac_id, acs[ac_id])
                if anchor['path'] not in coverage_paths[ac_id]:
                    fail('IOS.OBLIGATION_FEATURE_MISMATCH', ident + ':' + ac_id,
                         anchor['path'] + ' is outside ' + acs[ac_id]['feature_id']
                         + ' source anchors and its explicitly referenced shared source contracts')
            if not any(acs[a]['judgment'] in expected[ident]['judgments'] for a in ids):
                fail('IOS.ORACLE_TOO_WEAK', ident, 'Required judgment: ' + '/'.join(expected[ident]['judgments']))
            # A signal is a review obligation, not a claim that token analysis bound its calls.
            review = mapping.get('source_review')
            if not isinstance(review, dict) or review.get('status') != 'reviewed' or not all(isinstance(review.get(k), str) and review[k].strip() for k in ('input', 'processing', 'observable', 'reviewer')):
                fail('IOS.SOURCE_REVIEW_MISSING', ident, 'Review input -> processing -> observable outcome against source')
        for ident in sorted(expected.keys() - seen):
            fail('IOS.OBLIGATION_UNCOVERED', ident, expected[ident]['obligation'])

    def spec_contract():
        from .spec_contract import check as check_contract
        content, _ = check_contract(project)
        issues.extend(content['findings'])

    stage('configuration', configuration, subject='.migbot/config.json')
    stage('source_contract', source_contract)
    stage('graph', lambda: validate_graph(source, project),
          subject='spec/baseline/ios-facts.json + ios-obligations.json')
    stage('extraction', extraction, dependencies=('graph',))
    stage('expertise', expertise, dependencies=('graph',),
          subject='spec/ref/ios-expertise-plan.json + ios-expertise-reviews.json')
    stage('literals', literals, subject='spec/baseline/literal-ledger.json')
    stage('semantics_input', semantics_input, subject='spec/baseline/ios-semantics.json')
    stage('coverage_input', coverage_input, subject='spec/baseline/ios-coverage.json')
    stage('responsibility', lambda: responsibility(project, source=source, graph=values.get('graph', (None, None))[0],
          obligations=values.get('graph', (None, None))[1], semantics=values.get('semantics_input')),
          dependencies=('graph', 'semantics_input') if (project / 'spec/baseline/ios-responsibility.json').exists() else (),
          subject='spec/baseline/ios-responsibility.json')
    stage('acceptance', lambda: ac_inventory(project, projection=values.get('responsibility')), subject='spec/baseline/features')
    stage('native_claims', lambda: validate_native_claims(
        project, values['graph'][0], values['semantics_input'], fail, projection=values['responsibility']),
        dependencies=('configuration', 'source_contract', 'graph', 'semantics_input') +
        (('responsibility',) if (project / 'spec/baseline/ios-responsibility.json').exists() else ()))
    stage('coverage', coverage_check,
          dependencies=('configuration', 'graph', 'coverage_input', 'acceptance') +
          (('responsibility',) if (project / 'spec/baseline/ios-responsibility.json').exists() else ()))
    # This independent stage is attempted even when source or graph checks fail;
    # its own input error is reported rather than hiding the remaining contract.
    stage('spec_contract', spec_contract)
    issues = normalize_findings(issues, queue=queue)
    if not report_only:
        queue.replace_section(str(project), 'spec.ios-harness', issues)
    report = {'schema_version': 2, 'status': summary_status(issues, queue=queue), 'findings': issues,
              'blocking_count': len(blocking_findings(issues, queue=queue)),
              'advisory_count': len(issues) - len(blocking_findings(issues, queue=queue)),
              'action_options': action_options(queue=queue) if issues else [],
              'scope': 'source contract and obligation coverage', 'behavior_verified': False,
              'excluded_obligation_ids': sorted(excluded_obligations),
              'extraction_issue_dispositions': extraction_dispositions, 'checks': checks}
    projection = values.get('responsibility')
    if projection is not None:
        report.update(responsibility_counts=projection.counts,
                      acceptance_counts={scope: len(rows) for scope, rows in projection.acceptance.items()},
                      historical_obligation_ids=list(projection.historical_obligation_ids),
                      product_obligation_ids=list(projection.product_obligation_ids),
                      obligation_treatments=projection.treatments,
                      source_history_acceptance_ids=list(projection.acceptance['source_history']),
                      target_acceptance_ids=list(projection.target_acceptance_ids))
    if not report_only:
        write_json(project / 'spec/reports/ios-harness-check.json', report)
    return report, queue.exit_code(issues)


def acceptance_binding(project, source, graph):
    """Exact consumed inputs for optional reuse, never a replacement native check.

    Raw authored bytes intentionally make this stricter than progress-tolerant
    plan identity. A cache miss runs the full gate and introduces no new gate.
    """
    try:
        from .consumed_inputs import baseline_inputs
        from .plan_contract import contract_revision
        from .expertise import check as check_expertise, PLAN, REVIEWS
        from .apple_capabilities import GUIDANCE
        inputs = baseline_inputs(project, 'domains')
        for name in ('.migbot/config.json', PLAN, REVIEWS, GUIDANCE):
            path = safe_child(project, name)
            inputs[name] = digest(path.read_bytes()) if path.is_file() else None
        # Revalidate selected guidance/resources now: their source files may be
        # outside the project. Never cache resource freshness behind its label.
        expertise = check_expertise(project, source, graph)
        return {'rules_sha256': contract_revision(project),
                'source_sha256': graph['source_sha256'],
                'graph_sha256': digest(json_bytes(graph)),
                'consumed_inputs': inputs,
                'expertise_sha256': digest(json_bytes(expertise))}
    except (MigrationError, OSError, ValueError, KeyError, TypeError):
        return None


def retain_acceptance(project, source, graph, report, code, before):
    """Retain only an actual successful check with unchanged input boundaries."""
    after = acceptance_binding(project, source, graph)
    if code or before is None or before != after:
        return None
    value = {'schema_version': 1, 'kind': 'actual_harness_acceptance',
             'actually_invoked': True, 'exit_code': 0, 'binding': after, 'report': report}
    raw = json_bytes(value)
    name = 'spec/reports/ios-harness-receipts/' + digest(raw) + '.json'
    write_json(safe_child(project, name), value)
    return {'path': name, 'sha256': digest(raw), 'binding_sha256': digest(json_bytes(after))}


def reuse_acceptance(project, source, graph, contract):
    """Reuse a frozen success only after live native/source validation by caller.

    Missing/old/changed receipts fall back to the full gate. This does not cache
    validate_graph: condition/compiler evidence remains validated every call.
    """
    try:
        from .plan_contract import assert_pinned
        from .ios_scheduler import kernel
        assert_pinned(project, contract)
        plan = read_json(safe_child(project, 'spec/waves/plan-domains.json'))
        identity = digest(json_bytes({k: v for k, v in plan.items() if k != 'contract_hash'}))
        if (identity != contract.get('plan_identity_sha256')
                or kernel().compute_contract_hash(Path(project) / 'spec/blueprint', []) != plan.get('contract_hash')):
            return None
        ref = contract.get('harness_acceptance')
        if not isinstance(ref, dict) or set(ref) != {'path', 'sha256', 'binding_sha256'}:
            return None
        if not re.fullmatch(r'spec/reports/ios-harness-receipts/[0-9a-f]{64}\.json', ref['path']):
            return None
        path = safe_child(project, ref['path'])
        if digest(path.read_bytes()) != ref['sha256']:
            return None
        value = read_json(path)
        current = acceptance_binding(project, source, graph)
        if (value.get('schema_version') != 1 or value.get('kind') != 'actual_harness_acceptance'
                or value.get('actually_invoked') is not True or value.get('exit_code') != 0
                or current is None or value.get('binding') != current
                or digest(json_bytes(current)) != ref['binding_sha256']):
            return None
        report = value['report']
        from .gate_policy import blocking_findings
        if not isinstance(report, dict) or blocking_findings(report.get('findings', [])):
            return None
        return report, {'mode': 'reused', 'not_actual_call_now': True,
                        'original_result': ref, 'native_evidence_validated_now': True}
    except (MigrationError, OSError, ValueError, KeyError, TypeError):
        return None


def behavior_check(project: Path):
    """Validate source/target chains and run explicit independent executable oracles.

    Static checks deliberately cannot establish runtime equivalence.
    """
    from .native_pipeline import context
    from .ios_facts import validate_graph
    from .behavior import verify
    source, project = context(project)
    graph, _ = validate_graph(source, project)
    return verify(project, source, graph, ac_inventory(project))
