"""Read existing findings, preserve each source, and group only evidenced causes.

This projection never closes findings or writes a producer's queue section.
"""
from pathlib import Path
import json

from .core import MigrationError, digest, json_bytes, read_json, safe_child
from .gate_policy import scope_to_tasks


def require(value, message):
    if not value:
        raise MigrationError(message)


def project_path(project, relative):
    target = safe_child(project, relative)
    cursor = Path(project)
    for part in Path(relative).parts:
        cursor = cursor / part
        require(not cursor.is_symlink(), 'Repair evidence cannot traverse symlinks: ' + relative)
    return target


def harvested(value):
    """Return stable local keys and raw findings from supported real reports."""
    require(isinstance(value, dict), 'Finding report must be an object')
    require(any(k in value for k in ('findings', 'failures', 'sections', 'pairs', 'unverified_ac_ids')),
            'Unsupported report shape; cannot treat missing findings as no failures')
    rows = []
    for field in ('findings', 'failures'):
        if field in value:
            require(isinstance(value[field], list), field + ' must be a list')
            for row in value[field]:
                require(isinstance(row, dict), 'Finding must be an object')
                key = row.get('finding_key') or row.get('id') or digest(json_bytes({
                    k: row.get(k) for k in ('rule', 'subject', 'case_id', 'ac_ids', 'source_fact')}))
                require(isinstance(key, str) and key, 'Finding identity is missing')
                rows.append((field + ':' + key, row))
    sections = value.get('sections', {})
    require(isinstance(sections, dict), 'Finding sections must be an object')
    for section, part in sorted(sections.items()):
        for key, row in harvested(part):
            rows.append(('section:' + section + ':' + key, row))
    pairs = value.get('pairs', [])
    require(isinstance(pairs, list), 'UI pairs must be a list')
    for pair in pairs:
        require(isinstance(pair, dict) and isinstance(pair.get('id'), str), 'Invalid paired checkpoint')
        assessment = pair.get('assessment', {})
        require(isinstance(assessment, dict), 'Invalid UI assessment')
        for row in assessment.get('differences', []):
            require(isinstance(row, dict), 'Invalid UI difference')
            if row.get('disposition') == 'excluded':
                continue
            require(isinstance(row.get('id'), str), 'UI difference needs an id')
            rows.append(('checkpoint:' + pair['id'] + ':' + row['id'],
                         {**row, 'checkpoint_id': pair['id'], 'owner_stage': 'execute'}))
        if pair.get('status') != 'compared':
            rows.append(('checkpoint:' + pair['id'] + ':incomplete', {
                'rule': 'UI.RECHECK_INCOMPLETE', 'subject': pair['id'], 'checkpoint_id': pair['id'],
                'owner_stage': 'execute', 'detail': pair.get('reason', 'Current paired evidence is incomplete')}))
    pending = value.get('unverified_ac_ids', [])
    require(isinstance(pending, list), 'Unverified AC ids must be a list')
    for ident in pending:
        require(isinstance(ident, str), 'Invalid unverified AC identity')
        rows.append(('unverified:' + ident, {'rule':'IOS.BEHAVIOR_UNVERIFIED', 'subject':ident,
                     'ac_ids':[ident], 'owner_stage':'execute', 'status':'unverified'}))
    effects = value.get('effect_review', {})
    require(isinstance(effects, dict), 'Effect review must be an object')
    for row in effects.get('findings', []):
        require(isinstance(row, dict) and isinstance(row.get('id'), str), 'Invalid effect finding identity')
        if row.get('status') != 'confirmed_failure':
            rows.append(('effect_review:' + row['id'], {**row, 'owner_stage': row.get('owner_stage', 'verify')}))
    if not rows and value.get('status') is not None and value['status'] not in {
            'PASS', 'passed', 'success', 'built', 'compared', 'equal_control_observations', 'not_selected'}:
        rows.append(('report_status', {'rule':'REPORT.RECHECK_INCOMPLETE',
                     'subject':'report', 'owner_stage':'verify', 'detail':value.get('status')}))
    require(len({key for key, _ in rows}) == len(rows), 'Duplicate finding identity in report')
    return rows


def load_reports(project, reports):
    require(isinstance(reports, list) and reports and all(isinstance(p, str) for p in reports)
            and len(reports) == len(set(reports)), 'Expected unique existing report paths')
    findings, hashes = [], {}
    for relative in reports:
        path = project_path(project, relative)
        require(path.is_file() and not path.is_symlink(), 'Existing report is unavailable: ' + relative)
        raw = path.read_bytes();value = read_json(path)
        require(path.read_bytes() == raw, 'Report changed while harvesting: ' + relative)
        hashes[relative] = digest(raw)
        for key, original in harvested(value):
            findings.append({'id': 'finding-' + digest(json_bytes([relative, key]))[:24],
                'local_key': key, 'report': relative, 'report_sha256': hashes[relative],
                'original': original, 'owner_stage': original.get('owner_stage', 'execute'),
                'checkpoint_id': original.get('checkpoint_id'), 'state': 'open'})
    return findings, hashes


def triage(project, request):
    project = Path(project).resolve(strict=True)
    require(isinstance(request, dict), 'Repair input must be an object')
    findings, reports = load_reports(project, request.get('reports'))
    contract_path = project_path(project, 'spec/execution/execution-contract.json')
    contract = read_json(contract_path) if contract_path.is_file() else {}
    tasks = [{'id': ident, **item} for ident, item in contract.get('plan_items', {}).items()]
    # Preserve originals. Causal projection is a consumer view, never new tasks.
    projected = scope_to_tasks([f['original'] for f in findings], tasks)
    by_id = {f['id']: f for f in findings}
    for finding, view in zip(findings, projected):
        finding['consumer_projection'] = view
        original = finding['original']
        refs = set()
        for field in ('ac_ids', 'page_ids', 'fact_ids'):
            values = original.get(field, [])
            if isinstance(values, list):refs.update(v for v in values if isinstance(v, str))
        if isinstance(original.get('source_fact'), str):refs.add(original['source_fact'])
        owner = original.get('owner')
        finding['associated_task_ids'] = sorted(t['id'] for t in tasks if t['id'] == owner or refs & (
            set(t.get('ac_ids', [])) | set(t.get('page_ids', [])) | set(t.get('fact_ids', []))))
    causes, grouped = [], set()
    for cause in request.get('root_causes', []):
        require(isinstance(cause, dict) and set(cause) == {
            'id', 'finding_ids', 'owner_stage', 'kind', 'evidence'}, 'Invalid root cause fields')
        require(isinstance(cause['id'], str) and cause['id'] and
                cause['id'] not in {c['id'] for c in causes}, 'Duplicate/missing root cause id')
        ids = cause['finding_ids']
        require(isinstance(ids, list) and ids and len(ids) == len(set(ids)) and
                set(ids) <= by_id.keys() and not set(ids) & grouped, 'Root cause finding selection is invalid')
        require(cause['kind'] in {'code', 'source', 'plan', 'tool', 'environment', 'unknown'},
                'Unknown root cause kind')
        require({by_id[i]['owner_stage'] for i in ids} == {cause['owner_stage']},
                'Root cause cannot merge different owner stages')
        owners = {json_bytes(by_id[i]['original'].get('owner')) for i in ids}
        require(len(owners) == 1, 'Root cause cannot merge different original repair owners')
        evidence = cause['evidence']
        require(isinstance(evidence, list) and evidence, 'Common cause requires actual evidence')
        pinned = []
        for ref in evidence:
            require(isinstance(ref, dict) and set(ref) == {'path', 'sha256'}, 'Root cause evidence needs exact path/hash')
            path = project_path(project, ref['path'])
            require(path.is_file() and not path.is_symlink() and digest(path.read_bytes()) == ref['sha256'],
                    'Root cause evidence changed: ' + str(ref.get('path')))
            pinned.append(ref)
        grouped.update(ids)
        causes.append({**cause, 'evidence': pinned, 'status': 'diagnosis_proposed',
                       'finding_states': {i: 'open' for i in ids}})
    for finding in findings:
        if finding['id'] not in grouped:
            causes.append({'id': 'independent-' + finding['id'], 'finding_ids': [finding['id']],
                'owner_stage': finding['owner_stage'], 'kind': 'unknown', 'evidence': [],
                'status': 'diagnosis_needed', 'finding_states': {finding['id']: 'open'}})
    # Blocking consumers first; do not infer a common cause from similar text.
    for cause in causes:
        blocked, associated = set(), set()
        for ident in cause['finding_ids']:
            blocked.update(by_id[ident]['consumer_projection'].get('impact', {}).get('blocked_tasks', []))
            associated.update(by_id[ident]['associated_task_ids'])
        downstream = blocked | associated
        while True:
            expanded = downstream | {t['id'] for t in tasks if
                set(t.get('parents', t.get('depends_on', t.get('dependencies', [])))) & downstream}
            if expanded == downstream:
                break
            downstream = expanded
        cause['blocked_tasks'] = sorted(blocked)
        cause['associated_task_ids'] = sorted(associated)
        cause['affected_downstream_tasks'] = sorted(downstream)
        cause['priority_consumers'] = len(downstream)
    causes.sort(key=lambda c: (-c['priority_consumers'], c['id']))
    return {'schema_version': 1, 'status': 'triaged', 'report_hashes': reports,
            'findings': findings, 'cause_groups': causes, 'original_queues_modified': False,
            'application_acceptance': 'not_established'}
