"""Project explicit prompt scopes without dropping unscoped shared decisions.

The complete decision ledger stays in the pinned blueprint. Optional
``prompt_scope`` only controls which decisions are inlined into each prompt;
it never grants ownership or changes acceptance requirements.
"""
from .core import MigrationError


def project_inputs(facts, tasks, decisions):
    fact_by_id = {fact['id']: fact for fact in facts}
    order = {fact['id']: index for index, fact in enumerate(facts)}
    by_task = {task['id']: task for task in tasks}
    ac_consumers, fact_consumers = {}, {}
    result = {}
    for task in tasks:
        ident = task['id']
        for ac in task.get('ac_ids', []):
            ac_consumers.setdefault(ac, set()).add(ident)
        for fact in task['fact_ids']:
            if fact not in fact_by_id:
                raise MigrationError('Prompt references unknown fact: ' + str(fact))
            fact_consumers.setdefault(fact, set()).add(ident)
        result[ident] = {
            'facts': [fact_by_id[key] for key in sorted(set(task['fact_ids']), key=order.__getitem__)],
            'decisions': [],
            'omitted_decisions': 0,
        }
    allowed = {'task_ids': set(by_task), 'ac_ids': set(ac_consumers), 'fact_ids': set(fact_by_id)}
    for decision in decisions:
        if not isinstance(decision, dict):
            raise MigrationError('Prompt decisions must be objects')
        scope = decision.get('prompt_scope')
        if 'prompt_scope' not in decision:
            consumers = set(by_task)  # Legacy and shared decisions remain visible.
        else:
            if not isinstance(scope, dict) or not scope or set(scope) - set(allowed):
                raise MigrationError('Decision prompt_scope needs explicit task_ids, ac_ids or fact_ids')
            consumers = set()
            selected = 0
            for field, ids in scope.items():
                if not isinstance(ids, list) or any(not isinstance(key, str) for key in ids):
                    raise MigrationError('Decision prompt_scope IDs must be string arrays')
                unknown = set(ids) - allowed[field]
                if unknown:
                    raise MigrationError('Decision prompt_scope references unknown ' + field + ': ' + ','.join(sorted(unknown)))
                selected += len(ids)
                for key in ids:
                    consumers.update({key} if field == 'task_ids' else
                                     ac_consumers[key] if field == 'ac_ids' else fact_consumers.get(key, set()))
            if not selected or not consumers:
                raise MigrationError('Decision prompt_scope must select an actual task consumer')
        for ident in consumers:
            result[ident]['decisions'].append(decision)
    for value in result.values():
        value['omitted_decisions'] = len(decisions) - len(value['decisions'])
    return result
