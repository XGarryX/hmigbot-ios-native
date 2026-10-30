"""Native write/deletion evidence; original scheduler remains the only state writer.

This is a migration protocol adapter, not an Apple source analyzer. Deletions
require a frozen exact path/hash and the same pre-dispatch bytes. No sentinel
file or hash is ever used for a file that no longer exists.
"""
from contextlib import contextmanager
from pathlib import Path
import re

from .core import MigrationError, atomic_write, digest, json_bytes, read_json, safe_child


def require(ok, detail):
    if not ok:
        raise MigrationError('Receipt outputs: ' + detail)


def regular_path(project, relative):
    actual = safe_child(project, relative)
    cursor = Path(project)
    for part in Path(relative).parts:
        cursor /= part
        require(not cursor.is_symlink() and not getattr(cursor, 'is_junction', lambda: False)(),
                'linked output path: ' + relative)
    return actual


def hashes(value):
    return (isinstance(value, dict) and all(isinstance(p, str) and isinstance(h, str)
            and re.fullmatch('[0-9a-f]{64}', h) for p, h in value.items()))


def deletion_intent(project, task, *, check_current=False):
    planned = task.get('deletions', {})
    require(hashes(planned) and set(planned) <= set(task['ownership']), 'deletion intent exceeds frozen ownership')
    for path, expected in planned.items():
        actual = regular_path(project, path)
        if check_current:
            require(actual.is_file() and digest(actual.read_bytes()) == expected,
                    'planned deletion preimage missing/changed: ' + path)
    return planned


def validate_outputs(project, receipt, task, *, before=None, readonly=False):
    written, deleted = receipt.get('file_hashes'), receipt.get('deleted_files', {})
    planned = deletion_intent(project, task)
    require(hashes(written) and hashes(deleted), 'invalid written/deleted hash maps')
    require(not set(written) & set(deleted), 'path cannot be both written and deleted')
    touched = set(written) | set(deleted)
    require(touched <= set(task['ownership']), 'receipt exceeds frozen ownership')
    require(set(deleted) <= set(planned), 'undeclared deletion')
    for path, expected in written.items():
        actual = regular_path(project, path)
        require(actual.is_file() and digest(actual.read_bytes()) == expected, 'written output missing/changed: ' + path)
    for path, expected in deleted.items():
        require(planned[path] == expected and before is not None and before.get(path) == expected,
                'deletion differs from frozen/pre-dispatch bytes: ' + path)
        require(not regular_path(project, path).exists(), 'deleted output still exists: ' + path)
    require(isinstance(receipt.get('files_touched'), list) and len(receipt['files_touched']) == len(touched)
            and set(receipt['files_touched']) == touched, 'touched files differ from written/deleted outputs')
    if 'files' in receipt:
        require(isinstance(receipt['files'], list) and len(receipt['files']) == len(touched)
                and set(receipt['files']) == touched, 'original files list differs from native outputs')
    if receipt.get('status') == 'generated':
        require(touched or readonly, 'generated receipt must pin actual outputs')
        require(touched == set(task['ownership']) and set(deleted) == set(planned),
                'generated receipt omitted planned outputs/deletions')
    return written, deleted


def _projection(raw):
    import json
    receipt = json.loads(raw)
    paths = list(receipt['file_hashes'])
    return json_bytes(dict(receipt, files=paths, files_touched=paths))


def recover_bridges(project, wave, plan_path, tasks, source_sha, before):
    """Recover only an exact bridge left by interrupted original landing."""
    plan_sha = digest(plan_path.read_bytes())
    for task in tasks:
        directory = project / f'spec/reports/ios-deletion-receipts/{wave}/{task["id"]}'
        for marker in sorted(directory.glob('*.bridge.json')):
            record = read_json(marker)
            if record.get('plan_sha256') != plan_sha:
                continue
            original = marker.with_name(marker.name.removesuffix('.bridge.json') + '.json')
            raw = original.read_bytes()
            require(record == {'schema_version': 1, 'plan_sha256': plan_sha, 'source_sha256': source_sha,
                    'task_id': task['id'], 'result_path': task['result_path'],
                    'receipt_sha256': digest(raw), 'projection_sha256': digest(_projection(raw))}, 'invalid deletion bridge marker')
            require(original.stem == digest(raw), 'deletion archive identity changed')
            result = regular_path(project, task['result_path'])
            if result.read_bytes() == _projection(raw) and raw != _projection(raw):
                import json
                receipt = json.loads(raw)
                require(receipt.get('status') == 'generated' and receipt.get('source_sha256') == source_sha
                        and receipt.get('plan_sha256') == plan_sha and receipt.get('task_id') == task['id'],
                        'stale deletion bridge receipt')
                validate_outputs(project, receipt, task, before=before)
                atomic_write(result, raw)


@contextmanager
def legacy_projection(project, wave, plan_path, receipts):
    """Project existing-file lists for the legacy reader, then restore native bytes.

    Source/plan/ownership/preimage/absence were validated before entering. The
    native receipt and an exact recovery marker precede any temporary write.
    Product files and original state/dispatch/journal are never edited here.
    """
    import json
    restored, evidence = [], []
    try:
        for ident, path in receipts:
            raw = path.read_bytes(); receipt = json.loads(raw); projected = _projection(raw)
            relative = f'spec/reports/ios-deletion-receipts/{wave}/{ident}/{digest(raw)}.json'
            archive = regular_path(project, relative)
            if archive.exists():
                require(archive.read_bytes() == raw, 'deletion archive collision')
            else:
                atomic_write(archive, raw)
            marker = archive.with_name(archive.stem + '.bridge.json')
            record = {'schema_version': 1, 'plan_sha256': digest(plan_path.read_bytes()),
                      'source_sha256': receipt['source_sha256'], 'task_id': ident,
                      'result_path': path.relative_to(project).as_posix(), 'receipt_sha256': digest(raw),
                      'projection_sha256': digest(projected)}
            if marker.exists():
                require(read_json(marker) == record, 'deletion bridge marker changed')
            else:
                atomic_write(marker, json_bytes(record))
            restored.append((path, raw, projected))
            atomic_write(path, projected)
            evidence.append({'id': ident, 'archive': relative, 'sha256': digest(raw),
                             'deleted_files': receipt['deleted_files'], 'original_disposition': 'existing-file-list-projection'})
        yield evidence
    finally:
        failures = []
        for path, raw, projected in restored:
            try:
                current = path.read_bytes()
                require(current in (raw, projected), 'native receipt changed during deletion landing: ' + str(path))
                if current != raw:
                    atomic_write(path, raw)
            except (OSError, MigrationError) as exc:
                failures.append(str(exc))
        if failures:
            raise MigrationError('Could not restore all deletion receipts; originals retained in archive: ' + '; '.join(failures))
