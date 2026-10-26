"""Authoring and source gates share these source-evidence contracts."""
from .core import MigrationError, digest, safe_child


def validate_disposition(item, known):
    from .artifact_contract import validate_json
    subject = item.get('path') if isinstance(item, dict) and isinstance(item.get('path'), str) else None
    try:
        validate_json(item, 'source_disposition_entry')
    except MigrationError as exc:
        raise MigrationError(
            f'Invalid source disposition {subject or "<missing path>"}: '
            'requires path, disposition, reason, line, end_line and source_sha256'
            f' ({exc})') from exc
    if item['path'] not in known:
        raise MigrationError('Source disposition path is outside the current source index: ' + item['path'])
    return item


def validate_literal_exclusion(source, known, item):
    """One read-only proof for every entry the literal view consumes as an exclusion.

    Entry ``source_sha256`` is that file's current bytes; the whole-source snapshot
    digest belongs to the enclosing document and never substitutes for it.
    """
    validate_disposition(item, known)
    path = item['path']
    file = safe_child(source, path)
    if not file.is_file():
        raise MigrationError(f'Literal exclusion {path}: not a file in the current source')
    try:
        body = file.read_bytes()
    except OSError as exc:
        raise MigrationError(f'Literal exclusion {path}: source bytes are unreadable ({exc.__class__.__name__})') from exc
    if item['source_sha256'] != digest(body):
        raise MigrationError(
            f'Literal exclusion {path}: source_sha256 must be the sha256 of this file\'s current bytes')
    try:
        count = len(body.decode('utf-8-sig').splitlines())
    except UnicodeError as exc:
        raise MigrationError(f'Literal exclusion {path}: source is not a readable text file ({exc.__class__.__name__})') from exc
    if not item['line'] <= item['end_line'] <= count:
        raise MigrationError(
            f'Literal exclusion {path}: line/end_line must be an in-order span within the current {count} lines')
    return item


def source_truth(source, anchors, path, line):
    """Render only a real line in this feature's declared source files."""
    if not isinstance(path, str):
        raise MigrationError('Truth path must be a source-relative string')
    file = safe_child(source, path)
    if (path not in anchors or type(line) is not int
            or not file.is_file() or not 1 <= line <= len(file.read_text(encoding='utf-8-sig').splitlines())):
        raise MigrationError('Truth location is outside the feature anchors or line range')
    return f'真:src:{path}:{line}'
