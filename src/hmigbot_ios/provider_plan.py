"""Read-only whole-plan preflight; provider execution remains explicit.

This checks request structure and referenced paths, not compiler availability,
configuration semantics, source bindings or the authenticity of imported data.
"""
from .core import MigrationError, io_path, read_json


def consumed_inputs(operation, config=None, input_path=None):
    """Normalize the inputs actually consumed by the authoritative atom."""
    if operation in {'swift-syntax', 'clang-ast'}:
        return config, None
    if operation == 'build-settings':
        return (config, None) if config else (None, input_path)
    return None, None


OPERATIONS = frozenset({'swift-syntax', 'clang-ast', 'build-settings',
                        'interface-builder', 'asset-inventory', 'localization-inventory'})


def preflight(path):
    """Validate every entry before any provider is started; keep argv cwd semantics.

    Paths retain the historical caller-working-directory interpretation. Repeated
    operations with different inputs are valid; exact duplicate requests are not.
    Provider-specific config contents are checked by the real provider so failed
    executions continue to retain their attempt diagnostics.
    """
    try:
        plan = read_json(path)
    except (OSError, ValueError) as exc:
        raise MigrationError('Provider plan cannot be read as JSON') from exc
    if (not isinstance(plan, dict) or type(plan.get('schema_version')) is not int
            or plan['schema_version'] != 2 or not isinstance(plan.get('providers'), list)):
        raise MigrationError('Provider plan requires v2 providers array')
    entries, seen = [], set()
    for index, provider in enumerate(plan['providers']):
        label = 'Provider plan entry ' + str(index)
        if not isinstance(provider, dict):
            raise MigrationError(label + ' must be an object')
        operation = provider.get('operation')
        if not isinstance(operation, str) or operation not in OPERATIONS:
            raise MigrationError(label + ' has unsupported operation')
        config, input_path = consumed_inputs(operation, provider.get('config'), provider.get('input'))
        consumed = {'config': config, 'input': input_path}
        paths = {}
        for field in ('config', 'input'):
            if consumed[field] is None:
                paths[field] = None
                continue
            value = consumed[field]
            if not isinstance(value, str) or not value.strip():
                raise MigrationError(label + ' ' + field + ' must be a nonempty path')
            target = io_path(value).resolve()
            if field == 'config' and not target.is_file():
                raise MigrationError(label + ' configuration file is missing')
            if field == 'input' and (not target.is_dir() or not (target / 'manifest.json').is_file()):
                raise MigrationError(label + ' input must be an evidence bundle with manifest.json')
            paths[field] = target
        if operation in {'swift-syntax', 'clang-ast'} and paths['config'] is None:
            raise MigrationError(label + ' requires explicit config')
        if operation == 'build-settings':
            bundle = paths['input']
            if paths['config'] is None and (bundle is None or not bundle.is_dir() or not (bundle / 'manifest.json').is_file()):
                raise MigrationError(label + ' requires an input evidence bundle with manifest.json')
        identity = (operation, paths['config'], paths['input'])
        if identity in seen:
            raise MigrationError(label + ' duplicates an earlier provider request')
        seen.add(identity)
        entries.append({'operation': operation, **{key: str(value) for key, value in paths.items() if value is not None}})
    return entries
