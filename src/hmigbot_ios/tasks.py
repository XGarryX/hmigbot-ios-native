"""Evidence contracts for atomic operations performed by the coding agent."""
from pathlib import Path
from .core import source_snapshot
from .core import SCHEMA, MigrationError, digest, json_bytes, read_json, safe_child, snapshot, write_new_tree


def create_task(atom_id, source, output):
    catalog = read_json(Path(__file__).with_name('capabilities.json'))
    matches = [item for item in catalog['atoms'] if item['id'] == atom_id]
    if not matches:
        raise MigrationError('Unknown atom ID')
    source, output = source.resolve(), output.resolve()
    if output.is_relative_to(source) or source.is_relative_to(output):
        raise MigrationError('Task output must not overlap source')
    atom = matches[0]
    task = {'schema_version': SCHEMA, 'atom_id': atom_id, 'operation': atom['operation'],
            'source_sha256': source_snapshot(source)['sha256'], 'status': 'pending',
            'source_anchors_ref': [], 'decisions': [], 'outputs': [], 'verification': [], 'unresolved': []}
    write_new_tree(output, {'task.json': json_bytes(task)})
    return {'status': 'created', 'task': str(output / 'task.json'), 'atom_id': atom_id}


def check_task(source, task_path):
    task = read_json(task_path)
    if task.get('schema_version') != SCHEMA:
        raise MigrationError('Unsupported task contract')
    ids = {a['id'] for a in read_json(Path(__file__).with_name('capabilities.json'))['atoms']}
    if task.get('atom_id') not in ids:
        raise MigrationError('Unknown task atom')
    current = source_snapshot(source.resolve())
    if current['sha256'] != task.get('source_sha256'):
        raise MigrationError('Task source fingerprint is stale')
    source_files = {f['path']: f['sha256'] for f in current['files']}
    anchors = task.get('source_anchors_ref')
    if not isinstance(anchors, list) or not anchors:
        raise MigrationError('Task needs at least one real source anchor')
    for ref in anchors:
        if ref.get('path') not in source_files or ref.get('sha256') != source_files[ref['path']]:
            raise MigrationError('Missing or stale task source anchor')
    outputs = task.get('outputs')
    if not isinstance(outputs, list) or not outputs:
        raise MigrationError('Task needs reviewable outputs under its directory')
    for item in outputs + task.get('verification', []):
        file = safe_child(task_path.parent, item['path'])
        if not file.is_file() or digest(file.read_bytes()) != item.get('sha256'):
            raise MigrationError('Task output/evidence was modified: ' + item['path'])
    if not isinstance(task.get('decisions'), list) or not task['decisions']:
        raise MigrationError('Task must document its mapping/analysis decisions')
    return {'record_valid': True, 'atom_id': task['atom_id'], 'declared_status': task.get('status'),
            'verification_records': len(task.get('verification', [])), 'unresolved': task.get('unresolved', []),
            'scope': 'Artifact provenance and integrity; semantic acceptance depends on the atom-specific checks'}
