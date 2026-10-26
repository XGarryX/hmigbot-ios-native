"""Exclusive multi-file creation with rollback limited to our unchanged writes."""
from __future__ import annotations
import os
from pathlib import Path
from .core import MigrationError, safe_child


def create_missing(project, files, *, before_commit=None, strict_existing=False):
    project = Path(project).resolve()
    plan, skipped = [], []
    for relative, text in files.items():
        target = safe_child(project, relative)
        content = text.encode('utf-8') if isinstance(text, str) else text
        if target.exists():
            if strict_existing and target.read_bytes() != content:
                raise MigrationError('Existing document conflicts with candidate (would overwrite): ' + relative)
            skipped.append(relative)
        else:
            plan.append((relative, target, content))
    created = []
    try:
        if before_commit:
            before_commit()
        for relative, target, content in plan:
            target.parent.mkdir(parents=True, exist_ok=True)
            if safe_child(project, relative) != target:
                raise MigrationError('Destination changed during creation: ' + relative)
            with target.open('xb', buffering=0) as stream:
                info = os.fstat(stream.fileno())
                item = {'path': relative, 'target': target, 'identity': (info.st_dev, info.st_ino), 'content': b''}
                created.append(item)
                while len(item['content']) < len(content):
                    count = stream.write(content[len(item['content']):])
                    if not count:
                        raise OSError('Creation made no progress: ' + relative)
                    item['content'] = content[:len(item['content']) + count]
        if before_commit:
            before_commit()
    except BaseException as exc:
        retained = []
        for item in reversed(created):
            target = item['target']
            try:
                if not target.exists() and not target.is_symlink():
                    continue
                info = target.stat()
                if (target.is_symlink() or safe_child(project, item['path']) != target
                        or (info.st_dev, info.st_ino) != item['identity'] or target.read_bytes() != item['content']):
                    retained.append(item['path'])
                else:
                    target.unlink()
            except (OSError, MigrationError):
                retained.append(item['path'])
        detail = '; retained changed/unremovable files: ' + ', '.join(sorted(retained)) if retained else ''
        if not isinstance(exc, (MigrationError, OSError, ValueError)):
            if detail:
                exc.add_note(detail)
            raise
        raise MigrationError('Scaffold apply failed; unchanged new files rolled back: ' + str(exc) + detail) from exc
    return {'created': sorted(item['path'] for item in created), 'skipped': sorted(skipped), 'refused': [],
            'spec_complete': False, 'behavior_verified': False}
