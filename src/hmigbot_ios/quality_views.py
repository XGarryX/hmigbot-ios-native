"""Read-only product and evidence projections; raw ledgers remain authoritative.

These views describe reviewed source spans and bound execution records. Neither
literal classification nor historical progress proves runtime equivalence.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from .core import MigrationError, digest, json_bytes, read_json, safe_child, snapshot

LITERAL_GROUPS = ('texts', 'colors', 'dims', 'durations_ms', 'dynamic_texts',
                  'numeric_constants', 'symbolic_colors')


def spec_inputs(project):
    from .ios_scheduler import baseline_inputs
    from .plan_contract import contract_revision
    return {**baseline_inputs(Path(project), 'domains'), '@tool-contract': contract_revision(Path(project))}


def target_inputs(project):
    """Bind the complete non-generated product tree, separate from tool reports."""
    from .ios_scheduler import _execution_evidence
    return {f['path']: f['sha256'] for f in snapshot(Path(project))['files']
            if not f['path'].startswith(('spec/', 'migration/'))
            and (not f['path'].startswith('.migbot/') or f['path'] == '.migbot/config.json')
            and not _execution_evidence(f['path'])}


def product_literals(project):
    from .native_pipeline import context
    from .ios_facts import validate_graph
    from .ios_harness import ac_inventory
    from .ios_literals import extract
    from .native_contract import validate_literal_exclusion
    from .source_scope import preview_source_lines
    source, project = context(Path(project))
    base = project / 'spec/baseline'
    raw = read_json(base / 'literal-ledger.json')
    if raw != extract(source):
        raise MigrationError('Raw literal ledger is stale or edited; extract it again')
    graph, obs = validate_graph(source, project)
    from .ios_harness import responsibility
    projection = responsibility(project, source=source, graph=graph, obligations=obs)
    coverage = read_json(base / 'ios-coverage.json')
    if coverage.get('graph_sha256') != digest(json_bytes(graph)):
        raise MigrationError('Product literal view requires current reviewed coverage')
    acs = ac_inventory(project)
    facts = {f['id']: f for f in graph['facts']}
    reviewed = []
    historical = [facts[projection.treatments[o]['source_fact_id']]['anchor']
                  for o in projection.historical_obligation_ids] if projection is not None else []
    for mapping in coverage.get('mappings', []):
        review = mapping.get('source_review', {})
        fact = facts.get('IF-' + str(mapping.get('obligation_id', ''))[3:])
        if (fact and mapping.get('ac_ids') and set(mapping['ac_ids']) <= set(acs)
                and review.get('status') == 'reviewed'
                and all(isinstance(review.get(k), str) and review[k].strip()
                        for k in ('input', 'processing', 'observable', 'reviewer'))):
            reviewed.append(fact['anchor'])
    dispositions = []
    scope_path = base / 'ios-source-disposition.json'
    if scope_path.exists():
        scope = read_json(scope_path)
        if scope.get('source_sha256') != graph['source_sha256']:
            raise MigrationError('Source disposition is stale; re-review the scope')
        indexed = {f['path'] for f in snapshot(source)['files']}
        for item in scope.get('files', []):
            validate_literal_exclusion(source, indexed, item)
            dispositions.append(item)
    preview_cache, entries = {}, []
    for group in LITERAL_GROUPS:
        for index, item in enumerate(raw.get(group, [])):
            for anchor in item.get('sources', []):
                path, sep, raw_line = anchor.rpartition(':')
                if not sep or not raw_line.isdigit():
                    raise MigrationError('Literal source must identify an exact source line')
                line = int(raw_line)
                if path not in preview_cache:
                    preview_cache[path] = preview_source_lines(safe_child(source, path))
                classification, reason = 'unknown', 'No reviewed active source fact at this line'
                if any(a['path'] == path and a['line'] <= line <= a['end_line'] for a in historical):
                    classification, reason = 'source_history', 'Exact validated historical source responsibility; retained in raw ledger'
                if any(a['path'] == path and a['line'] <= line <= a['end_line'] for a in reviewed):
                    classification, reason = 'product', 'Intersects reviewed active source fact; usage still needs source analysis'
                if line in preview_cache[path]:
                    classification, reason = 'preview', 'Exact Preview span; exclusion approval is checked separately by the source gate'
                for scope in dispositions:
                    if scope['path'] == path and scope['line'] <= line <= scope['end_line']:
                        classification = {'not_applicable': 'excluded'}.get(scope['disposition'], scope['disposition'])
                        reason = scope['reason']
                if projection is not None:
                    # Old file ownership notes do not override precise reviewed
                    # obligations. Shared source lines keep product priority.
                    if line not in preview_cache[path] and any(a['path'] == path and a['line'] <= line <= a['end_line'] for a in reviewed):
                        classification, reason = 'product', 'Intersects reviewed active source fact; usage still needs source analysis'
                    elif any(a['path'] == path and a['line'] <= line <= a['end_line'] for a in historical):
                        classification, reason = 'source_history', 'Exact validated historical source responsibility; retained in raw ledger'
                entries.append({**item, 'sources': [anchor], 'raw_ref': {'collection': group, 'index': index},
                                'classification': classification, 'reason': reason, 'usage': 'unresolved'})
    inputs = {'literal-ledger.json': digest(json_bytes(raw)), 'ios-facts.json': digest(json_bytes(graph)),
              'ios-coverage.json': digest(json_bytes(coverage))}
    if scope_path.exists():
        inputs[scope_path.name] = digest(scope_path.read_bytes())
    inputs['acceptance'] = digest(json_bytes(acs))
    if projection is not None:
        inputs['responsibility'] = digest(json_bytes(projection.frozen_inputs()))
    return {'schema_version': 1, 'source_sha256': graph['source_sha256'], 'inputs': inputs,
            'entries': entries, 'behavior_verified': False,
            'scope': 'Derived source-consumption candidates; not localization completeness or pixel conversion'}


def validate_product_view(project, view):
    if view != product_literals(project):
        raise MigrationError('Product literal view changed or its inputs are stale; recompute it')
    return True


def _legacy_counts(path):
    from .artifact_contract import markdown_tables
    counts = {}
    if path.exists():
        for table in markdown_tables(path.read_text(encoding='utf-8-sig')):
            headers = table['headers']
            if '状态' in headers or 'status' in headers:
                pos = headers.index('状态' if '状态' in headers else 'status')
                for row in table['rows']:
                    if len(row) > pos:
                        counts[row[pos]] = counts.get(row[pos], 0) + 1
    return counts


def _placeholders(project):
    from .artifact_contract import markdown_sections, markdown_tables
    path = project / 'spec/placeholder-registry.md'
    statuses = {'registered', 'pending', 'due', 'fired', 'resolved', 'deferred'}
    result = {'status': 'not_present', **dict.fromkeys(sorted(statuses), 0)}
    if not path.exists():
        return result
    text, seen = path.read_text(encoding='utf-8-sig'), set()
    sections = [s for s in markdown_sections(text) if s['title'] == '注册表']
    if len(sections) > 1:
        result['status'] = 'parse_error'; return result
    if sections:
        text = sections[0]['body']
    result['status'] = 'parsed'
    for table in markdown_tables(text):
        for row in table['rows']:
            row = [cell.strip('` ') for cell in row]
            ids = [cell for cell in row if re.fullmatch(r'P-[A-Za-z0-9-]+', cell)]
            if not ids:
                continue
            header = [cell.strip('` ') for cell in table['headers']]
            status_columns = [i for i, name in enumerate(header) if name.lower() in {'status', '状态'}]
            if len(ids) != 1 or ids[0] in seen or len(status_columns) != 1 or status_columns[0] >= len(row):
                result['status'] = 'parse_error'; continue
            seen.add(ids[0])
            status = row[status_columns[0]].lower()
            if status not in statuses:
                result['status'] = 'parse_error'; continue
            result[status] += 1
    if (set(re.findall(r'\bP-[A-Za-z0-9-]+\b', text)) - {'P-ID'}) - seen:
        result['status'] = 'parse_error'
    return result


def _compilation(project, source_sha, evidence):
    if evidence is None:
        return {'status': 'not_run'}
    path = Path(evidence)
    report = read_json(path)
    result = {'status': 'legacy_unclassified', 'evidence': str(path.resolve())}
    required = {'target_project', 'source_sha256', 'target_input_hashes', 'spec_input_hashes', 'artifacts'}
    if not required <= set(report):
        return result
    try:
        current = (Path(report['target_project']).resolve() == project.resolve()
                   and report['source_sha256'] == source_sha
                   and report['target_input_hashes'] == target_inputs(project)
                   and report['spec_input_hashes'] == spec_inputs(project))
        artifacts = report['artifacts']
        current = current and isinstance(artifacts, list) and bool(artifacts) and all(
            digest(safe_child(project, a['path']).read_bytes()) == a['sha256'] for a in artifacts)
    except (OSError, KeyError, TypeError, MigrationError):
        current = False
    result['status'] = ('stale' if not current else 'passed' if report.get('status') == 'build_passed'
                        and report.get('exit_code') == 0 and report.get('hvigor_success_marker') is True
                        and report.get('source_changed') is False else 'failed')
    return result


def _behavior(project, source_sha, acs):
    path = project / 'spec/reports/ios-behavior-check.json'
    if not path.exists():
        return {'status': 'not_run'}
    result = {'status': 'legacy_unclassified', 'evidence': path.relative_to(project).as_posix()}
    report = read_json(path)
    required = {'spec_input_hashes', 'verification_sha256', 'target_input_hashes'}
    if not required <= set(report):
        return result
    verification = project / 'spec/verification/ios-behavior.json'
    current = (report.get('source_sha256') == source_sha and verification.exists()
               and report['verification_sha256'] == digest(verification.read_bytes())
               and report['spec_input_hashes'] == spec_inputs(project)
               and report['target_input_hashes'] == target_inputs(project))
    if not current:
        result['status'] = 'stale'; return result
    covered, ac_statuses, invalid_acs = set(), {}, set()
    cases = {c['id']: c for c in read_json(verification).get('cases', [])}
    logs_current = True
    observed_ids = set()
    semantic_failures = [f for f in report.get('failures', []) if f.get('rule') != 'IOS.BEHAVIOR_OBSERVATION']
    for item in report.get('observations', []):
        case = cases.get(item.get('id'), {})
        valid = (item.get('id') not in observed_ids and item.get('ac_ids') == case.get('ac_ids')
                 and item.get('runner') == case.get('runner') and item.get('command') == case.get('command'))
        observed_ids.add(item.get('id'))
        if item.get('status') in {'observed_pass', 'observed_fail'}:
            for stream in ('stdout', 'stderr'):
                log = safe_child(project, 'spec/reports/behavior/' + item['id'] + '/' + stream + '.log')
                valid = valid and log.exists() and digest(log.read_bytes()) == item.get(stream + '_sha256')
            logs_current = logs_current and valid
            try:
                stdout = safe_child(project, 'spec/reports/behavior/' + item['id'] + '/stdout.log')
                actual = json.loads(stdout.read_bytes())
                valid = valid and actual == item.get('actual')
                passed = item.get('exit_code') == 0 and actual == case.get('oracle', {}).get('expected')
                valid = valid and (item['status'] == 'observed_pass') == passed
            except (OSError, ValueError, UnicodeError):
                valid = False
            logs_current = logs_current and valid
        if not valid or semantic_failures:
            invalid_acs.update(case.get('ac_ids', []))
            continue
        if item.get('status') == 'observed_pass' and item.get('exit_code') == 0 and item.get('actual') == case.get('oracle', {}).get('expected'):
            covered.update(item.get('ac_ids', []))
            for ident in item.get('ac_ids', []):
                if ac_statuses.get(ident) != 'failed': ac_statuses[ident] = 'passed'
        elif item.get('status') == 'observed_fail':
            for ident in item.get('ac_ids', []): ac_statuses[ident] = 'failed'
    for ident, case in cases.items():
        if ident not in observed_ids: invalid_acs.update(case.get('ac_ids', []))
    covered -= invalid_acs
    for ident in invalid_acs: ac_statuses[ident] = 'unverified'
    result['status'] = ('passed' if report.get('behavior_verified') is True and report.get('status') == 'PASS'
                        and not report.get('failures') and covered == set(acs) and logs_current
                        else 'failed' if report.get('failures') else 'unverified')
    result['scope'] = report.get('scope')
    result['ac_statuses'] = {a: ac_statuses.get(a, 'unverified') for a in sorted(acs)}
    return result


def summary(project, *, build_evidence=None, include_behavior=True):
    from .artifact_contract import _primary_feature
    from .native_pipeline import context
    from .ios_harness import ac_inventory, responsibility
    source, project = context(Path(project))
    projection = responsibility(project, source=source)
    try:
        acs = ac_inventory(project, projection=projection)
    except MigrationError as exc:
        # Reports must describe the pre-authoring boundary, too. Malformed
        # acceptance contracts remain errors; no ACs means no behavior proof.
        if str(exc) != 'No stable acceptance criteria exist':
            raise
        acs = {}
    source_sha = snapshot(source)['sha256']
    base = project / 'spec/baseline'
    from .page_evidence import generation, pages
    generated, tasks, records = generation(project, source_sha)
    axes = {'generation': generated,
            'compilation': _compilation(project, source_sha, build_evidence),
            'behavior': _behavior(project, source_sha, acs) if include_behavior else {'status': 'not_run', 'scope': 'behavior not selected in this verification scope'}, 'visual': {'status': 'not_run'}}
    if not acs and include_behavior:
        axes['behavior'] = {'status': 'unverified', 'reason': 'No stable acceptance criteria exist'}
    visual = project / 'spec/reports/visual-verify-report.md'
    if visual.exists():
        axes['visual'] = {'status': 'legacy_unclassified', 'evidence': visual.relative_to(project).as_posix()}
    evidence_files = [p for folder in ('spec/state', 'spec/waves', 'spec/blueprint', 'spec/verification', 'spec/reports/behavior')
                      for p in (project / folder).rglob('*') if p.is_file()
                      and (include_behavior or not p.relative_to(project).as_posix().startswith('spec/reports/behavior/') and p.name != 'ios-behavior.json')]
    for name in ('ios-behavior-check.json', 'visual-verify-report.md'):
        path = project / 'spec/reports' / name
        if path.exists() and (include_behavior or name != 'ios-behavior-check.json'): evidence_files.append(path)
    inputs = {'spec': spec_inputs(project), 'target': target_inputs(project),
              'evidence': {p.relative_to(project).as_posix(): digest(p.read_bytes()) for p in sorted(evidence_files)}}
    if build_evidence is not None: inputs['build_evidence_sha256'] = digest(Path(build_evidence).read_bytes())
    result = {'schema_version': 2, 'source_sha256': source_sha, 'axes': axes, 'inputs': inputs,
            'pages': pages(project, acs, axes, tasks, records),
            'behavior_verified': axes['behavior']['status'] == 'passed',
            'counts': {'acceptance': len(acs), 'features': sum(_primary_feature(p) for p in (base / 'features').glob('F*.md')),
                       'pages': len(list((base / 'ui').glob('page_*.md')))},
            'legacy_progress': {'features': _legacy_counts(base / 'feature-index.md'),
                                'pages': _legacy_counts(base / 'ui-manifest.md')},
            'placeholders': _placeholders(project),
            'scope': 'Read-only evidence axes; historical verified cells are compatibility progress only'}
    if projection is not None:
        result['source_responsibility'] = {'enabled': True, 'counts': projection.counts,
                                           'behavior_verified': False}
        result['counts'].update(acceptance_all=len(projection.acceptance['all']),
                                acceptance_source_history=len(projection.acceptance['source_history']))
    from .harness_schema import validate
    return validate(result, 'specSummary')


def render_report(report):
    """Deterministic generated report. Narrative stage details belong in linked reports."""
    from .harness_schema import validate
    validate(report, 'specSummary')
    lines = ['# 迁移证据报告', '', '<!-- hmigbot-derived-report:2 -->', '',
             '- source_sha256: `' + report['source_sha256'] + '`',
             '- summary_sha256: `' + digest(json_bytes(report)) + '`', '',
             '| 范围 | 数量 |', '|---|---|']
    lines += ['| ' + k + ' | ' + str(v) + ' |' for k, v in report['counts'].items()]
    lines += ['', '| 证据轴 | 当前状态 |', '|---|---|']
    lines += ['| ' + k + ' | ' + v['status'] + ' |' for k, v in report['axes'].items()]
    lines += ['', '| 页面 | 计划项 | 任务 | AC | 生成 | 编译 | 行为 | 视觉 |', '|---|---|---|---|---|---|---|---|']
    for page in report['pages']:
        cells = [page['page_id'], ', '.join(page['plan_item_refs']) or '-',
                 ', '.join(page['task_ids']) or '-', ', '.join(page['ac_ids']) or '-']
        cells += [page['axes'][axis]['status'] for axis in ('generation', 'compilation', 'behavior', 'visual')]
        lines.append('| ' + ' | '.join(cells) + ' |')
    lines += ['', '生成依据原内核落账和当前文件哈希；编译依据绑定当前输入的构建证据。',
              '行为仅覆盖已执行的独立 AC 观测；宿主逻辑测试不证明设备 UI。视觉与结构检查需各自证据。',
              'not_run、unverified、unmapped、unlanded、stale 均不等于通过。完整明细见同轮 spec-summary JSON。', '']
    return '\n'.join(lines)


def validate_report(project, text, *, build_evidence=None):
    if text != render_report(summary(project, build_evidence=build_evidence)):
        raise MigrationError('Migration report is edited or stale; regenerate it from current evidence')
    return True
