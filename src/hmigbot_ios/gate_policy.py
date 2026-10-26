"""Causal finding projections shared by gate consumers.

The standalone queue owns rule classification. These helpers preserve the raw
finding and expose severity/scope without changing product or control ledgers.
"""
import re


def normalize_findings(findings, *, queue=None):
    if queue is None:
        from .native_pipeline import findings_module
        queue = findings_module()
    return [queue.effective_finding(item) for item in findings]


def blocking_findings(findings, *, queue=None, task_ids=None, affected_objects=None):
    result = []
    for item in normalize_findings(findings, queue=queue):
        if item.get('severity') != 'blocking':
            continue
        impact = item['impact']
        if impact.get('scope') != 'source':
            if task_ids is not None and impact.get('blocked_tasks') and not set(task_ids).intersection(impact['blocked_tasks']):
                continue
            if affected_objects is not None and not set(affected_objects).intersection(impact.get('affected_objects', [])):
                continue
        result.append(item)
    return result


def summary_status(findings, *, queue=None):
    normalized = normalize_findings(findings, queue=queue)
    return 'FAIL' if blocking_findings(normalized, queue=queue) else 'needs_review' if normalized else 'PASS'


def with_action_options(findings, *, capabilities=None, unblocked_tasks=None, queue=None):
    """Propose available recovery paths without claiming any has been executed.

    Native/MCP/build choices appear only for explicit capability observations
    supplied by the caller. Unknown/false availability never becomes a choice.
    """
    if queue is None:
        from .native_pipeline import findings_module
        queue = findings_module()
    return [{**item, 'action_options': queue.recovery_options(
                item, capabilities=capabilities, unblocked_tasks=unblocked_tasks)}
            for item in normalize_findings(findings, queue=queue)]


def action_options(*, capabilities=None, unblocked_tasks=None, queue=None):
    """One shared catalog avoids repeating every recipe in every finding."""
    if queue is None:
        from .native_pipeline import findings_module
        queue = findings_module()
    return queue.recovery_options({}, capabilities=capabilities, unblocked_tasks=unblocked_tasks)


def scope_to_tasks(findings, tasks, *, graph=None, task_inputs=None, queue=None):
    """Derive actual task associations; never invent missing product tasks.

    Unmapped blockers remain visible for source/final acceptance review. They
    do not become a fabricated task id or a blocker of independent diagnostics.
    """
    by_fact = {f['id']: f.get('anchor', {}).get('path') for f in (graph or {}).get('facts', [])}
    task_inputs = task_inputs or {}
    result = []
    for item in normalize_findings(findings, queue=queue):
        if item.get('severity') != 'blocking':
            result.append(item); continue
        impact = {**item['impact']}
        objects = set(impact.get('affected_objects', []))
        refs = objects | {str(v) for v in impact.get('evidence_refs', [])}
        identifiers = set().union(*(set(re.findall(r'F\d+(?:-AC\d+)?|page_\d+|I[FO]-[A-Za-z0-9]+', value)) for value in refs))
        identifiers |= {'IF-' + value[3:] for value in identifiers if value.startswith('IO-')}
        blocked = set(impact.get('blocked_tasks', []))
        for task in tasks:
            facts = set(task.get('fact_ids', []))
            actual = set(task.get('ac_ids', [])) | set(task.get('fact_ids', [])) | set(task.get('page_ids', []))
            actual |= {value.split('-AC', 1)[0] for value in task.get('ac_ids', [])}
            actual |= {by_fact[value] for value in facts if value in by_fact and by_fact[value]}
            actual |= {ref['path'] for ref in task_inputs.get(task['id'], [])}
            if impact.get('scope') == 'source' or actual & (refs | identifiers):
                blocked.add(task['id'])
        impact['blocked_tasks'] = sorted(blocked)
        impact['association'] = 'source_scope' if impact.get('scope') == 'source' else 'matched_consumers' if blocked else 'unmapped_acceptance_blocker'
        result.append({**item, 'impact': impact})
    return result
