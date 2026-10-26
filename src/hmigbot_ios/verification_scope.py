"""One explicit verification scope, independent of caller/package provenance."""
from .core import MigrationError


def resolve(request):
    if not isinstance(request, dict):
        raise MigrationError('Verification scope must be an object')
    selected = request.get('checks', [])
    if not isinstance(selected, list) or any(item not in ['CHECK-1','CHECK-2','CHECK-3','CHECK-4','CHECK-5'] for item in selected):
        raise MigrationError('Unknown verification check selection')
    behavior = request.get('behavior', 'selected' if 'CHECK-5' in selected else 'pending')
    if behavior not in {'selected', 'not_selected', 'pending'}:
        raise MigrationError('Behavior scope must be selected, not_selected or pending')
    if 'CHECK-5' in selected and behavior != 'selected':
        raise MigrationError('Conflicting behavior scope and CHECK-5 selection')
    run = request.get('run_behavior', False)
    if type(run) is not bool or run and (behavior != 'selected' or request.get('authorized_cases') is not True):
        raise MigrationError('Real behavior execution needs selected scope and authorized cases with independent oracles')
    checks = ['CHECK-1', 'CHECK-2'] + [item for item in ('CHECK-3','CHECK-4') if item in selected]
    return {'schema_version': 1, 'checks': checks, 'behavior': behavior, 'run_behavior': run,
            'pending': ['behavior'] if behavior == 'pending' else [],
            'execution_order': checks + (['behavior-check'] if behavior == 'selected' else []),
            'overall_checks': checks, 'behavior_affects_overall': False}
