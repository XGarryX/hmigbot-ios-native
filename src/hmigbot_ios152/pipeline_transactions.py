"""Evidence-journalled pipeline commits with a state-last commit point.

Each replacement is atomic on one filesystem. The file set is not an OS atomic
transaction: failures are rolled back, and unfinished journals block new runs.
Recovery is explicit and must use the recorded preimages or verify every hash.
"""
from __future__ import annotations
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
from uuid import uuid4

CLEAR_STATUSES = frozenset(('committed', 'rolled_back'))
JOURNAL_GLOB = 'spec/execution/autofix-log/native-icon-input/*/pipeline-transactions/*/transaction.json'


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def _fsync_directory(path):
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _write(path, data):
    with path.open('wb') as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


def _journal(path, record):
    # Keep the previously durable journal if writing its next version fails.
    temporary = path.with_name('transaction.next.json')
    _write(temporary, (json.dumps(record, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))
    os.replace(temporary, path)
    _fsync_directory(path.parent)


def unfinished_transactions(project):
    """Read-only guard; a launcher can implement this exact glob without import."""
    unfinished = []
    for path in sorted(Path(project).glob(JOURNAL_GLOB)):
        try:
            record = json.loads(path.read_bytes())
            status = record.get('status') if isinstance(record, dict) else None
        except (OSError, ValueError, TypeError):
            status = None
        if status not in CLEAR_STATUSES:
            unfinished.append(path)
    return unfinished


@dataclass
class TransactionResult:
    journal: Path
    files: dict
    status: str


class TransactionError(OSError):
    def __init__(self, message, *, journal=None, record=None):
        super().__init__(message)
        self.journal = journal
        self.record = record


def _current_hash(path):
    return sha256(path.read_bytes()) if path.exists() else None


def _rollback(directory, record):
    errors = []
    for entry in reversed(record['files']):
        if entry['path'] not in record['applied']:
            continue
        target = Path(entry['path'])
        try:
            if entry['old_sha256'] is None:
                target.unlink(missing_ok=True)
                _fsync_directory(target.parent)
            else:
                restored = directory / 'staged' / ('rollback-' + str(entry['index']))
                backup = (directory / entry['backup']).read_bytes()
                if sha256(backup) != entry['old_sha256']:
                    raise OSError('backup preimage hash mismatch')
                _write(restored, backup)
                os.chmod(restored, entry['old_mode'])
                os.replace(restored, target)
                _fsync_directory(target.parent)
            if _current_hash(target) != entry['old_sha256']:
                raise OSError('restored preimage hash mismatch')
            record['restored'].append(entry['path'])
        except OSError as error:
            errors.append({'path': entry['path'], 'error': f'{type(error).__name__}: {error}'})
    for value in reversed(record.get('created_directories', [])):
        try:
            Path(value).rmdir()
        except OSError:
            pass
    record['rollback_errors'] = errors
    record['status'] = 'rollback_failed' if errors else 'rolled_back'
    return not errors


def commit_files(files, *, state_path, icon_evidence):
    """Commit a complete byte mapping; callers must finish all guards first."""
    state_path = Path(state_path).resolve()
    items = [(Path(path).resolve(), data) for path, data in files.items()]
    if len({path for path, _ in items}) != len(items) or state_path not in {path for path, _ in items}:
        raise ValueError('transaction needs unique destinations including state')
    if any(not isinstance(data, bytes) for _, data in items):
        raise TypeError('transaction targets must contain bytes')
    items = [(path, data) for path, data in items if path != state_path] + [(path, data) for path, data in items if path == state_path]
    directory = Path(icon_evidence).resolve() / 'pipeline-transactions' / uuid4().hex
    directory.mkdir(parents=True, exist_ok=False)
    (directory / 'staged').mkdir()
    (directory / 'backups').mkdir()
    journal = directory / 'transaction.json'
    record = {'schema': 'native-pipeline-transaction.v1', 'status': 'prepared',
              'state_file': str(state_path), 'files': [], 'applied': [], 'restored': [],
              'created_directories': []}
    # No canonical write occurs during staging and backup preparation.
    try:
        for index, (target, data) in enumerate(items):
            ancestor = target.parent
            while not ancestor.exists():
                ancestor = ancestor.parent
            if ancestor.stat().st_dev != directory.stat().st_dev:
                raise OSError('canonical and staging are on different filesystems')
            old = target.read_bytes() if target.exists() else None
            old_mode = (target.stat().st_mode & 0o7777) if old is not None else None
            stage = directory / 'staged' / str(index)
            _write(stage, data)
            if old_mode is not None:
                os.chmod(stage, old_mode)
            backup = 'backups/' + str(index) if old is not None else None
            if backup:
                _write(directory / backup, old)
            record['files'].append({'index': index, 'path': str(target), 'old_sha256': sha256(old) if old is not None else None,
                                    'new_sha256': sha256(data), 'old_mode': old_mode, 'backup': backup,
                                    'staged': 'staged/' + str(index)})
        _fsync_directory(directory / 'staged')
        _fsync_directory(directory / 'backups')
        _write(directory / 'preparedtransaction.json', (json.dumps(record, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))
        _fsync_directory(directory)
        _journal(journal, record)
    except Exception as error:
        # No replacement has happened. A prepared journal, if durable, remains
        # a conservative block; otherwise this directory has no entry journal.
        raise TransactionError(f'Cannot prepare pipeline transaction: {error}', journal=journal, record=record) from error
    try:
        for entry in record['files']:
            target = Path(entry['path'])
            pending = []
            parent = target.parent
            while not parent.exists():
                pending.append(parent)
                parent = parent.parent
            for parent in reversed(pending):
                parent.mkdir()
                record['created_directories'].append(str(parent))
            # Verify preimages again so a concurrent writer cannot be silently
            # overwritten after staging. This is a checked commit, not a lock.
            if _current_hash(target) != entry['old_sha256']:
                raise OSError(f'canonical preimage changed: {target}')
            os.replace(directory / entry['staged'], target)
            record['applied'].append(entry['path'])
            _fsync_directory(target.parent)
            _journal(journal, record)
    except Exception as error:
        record['error'] = f'{type(error).__name__}: {error}'
        _rollback(directory, record)
        try:
            _journal(journal, record)
        except OSError as journal_error:
            record['journal_error'] = str(journal_error)
        raise TransactionError(f'Pipeline commit failed ({record["status"]}): {error}', journal=journal, record=record) from error
    # A failure here leaves the durable status prepared. All new files may be
    # present, but the next entry must stop until explicit hash-based recovery.
    record['status'] = 'committed'
    try:
        _journal(journal, record)
    except Exception as error:
        record['status'] = 'prepared'
        record['error'] = f'committed journal failed: {type(error).__name__}: {error}'
        try:
            _journal(journal, record)
        except OSError as reset_error:
            record['journal_reset_error'] = str(reset_error)
        raise TransactionError(f'Cannot mark pipeline transaction committed: {error}', journal=journal, record=record) from error
    return TransactionResult(journal, {entry['path']: entry['new_sha256'] for entry in record['files']}, 'committed')


def recover_transaction(journal, *, rollback=False):
    """Explicit recovery: verify all-new/all-old, or restore recorded preimages."""
    journal = Path(journal).resolve()
    record = json.loads(journal.read_bytes())
    if record.get('schema') != 'native-pipeline-transaction.v1' or not isinstance(record.get('files'), list):
        raise TransactionError('Invalid transaction journal', journal=journal)
    if record.get('status') in CLEAR_STATUSES:
        return record['status']
    entries = record['files']
    if rollback:
        # A crash can happen between replace and applied-log write. Explicit
        # recovery considers each destination, not only the last durable list.
        record['applied'] = [entry['path'] for entry in entries if _current_hash(Path(entry['path'])) != entry['old_sha256']]
        record.setdefault('restored', [])
        _rollback(journal.parent, record)
    else:
        hashes = [_current_hash(Path(entry['path'])) for entry in entries]
        if all(value == entry['new_sha256'] for value, entry in zip(hashes, entries)):
            record['status'] = 'committed'
        elif all(value == entry['old_sha256'] for value, entry in zip(hashes, entries)):
            record['status'] = 'rolled_back'
        else:
            raise TransactionError('Mixed transaction files require explicit backup recovery', journal=journal, record=record)
    _journal(journal, record)
    if record['status'] == 'rollback_failed':
        raise TransactionError('Backup recovery failed', journal=journal, record=record)
    return record['status']
