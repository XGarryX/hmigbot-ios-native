"""Opt-in, content-preserving repair of orphan registry Markdown row groups."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import tempfile


SCHEMA = ['P-ID', 'location', 'trigger_condition', 'status', 'kind', 'resolve_by']


def cells(line: bytes):
    text = line.decode('utf-8').strip()
    if not text.startswith('|') or not text.endswith('|'):
        return None
    # A pipe is a delimiter only when preceded by an even number of backslashes.
    parts = []
    start = 1
    for i in range(1, len(text)):
        if text[i] != '|':
            continue
        backslashes = 0
        j = i - 1
        while j >= 0 and text[j] == '\\':
            backslashes += 1
            j -= 1
        if backslashes % 2 == 0:
            parts.append(text[start:i].strip())
            start = i + 1
    return parts


def format_registry(raw: bytes):
    lines = raw.splitlines(keepends=True)
    eligible = []
    fence = None
    for line in lines:
        text = line.decode('utf-8').rstrip('\r\n')
        mark = re.match(r'^ {0,3}(`{3,}|~{3,})(.*)$', text)
        eligible.append(fence is None and mark is None)
        if mark:
            token, tail = mark.groups()
            if fence is None:
                fence = (token[0], len(token))
            elif token[0] == fence[0] and len(token) >= fence[1] and not tail.strip():
                fence = None
    headers = {}
    for i in range(len(lines) - 1):
        if not (eligible[i] and eligible[i + 1]):
            continue
        row, separator = cells(lines[i]), cells(lines[i + 1])
        if row and separator and len(row) == len(separator) and all(re.fullmatch(r':?-{3,}:?', x) for x in separator):
            headers[i] = row
    candidates = [i for i, row in headers.items() if len(row) == 6 and row[0] == 'P-ID']
    if not candidates or any(headers[i] != SCHEMA for i in candidates):
        raise ValueError('registry formatting requires one unambiguous existing six-column header/separator pair')
    first = candidates[0]
    header, separator = lines[first], lines[first + 1]
    newline = b'\r\n' if header.endswith(b'\r\n') else b'\n'
    out, inserted, active, i = [], [], False, 0
    while i < len(lines):
        if i in headers:
            active = headers[i] == SCHEMA
            out.extend(lines[i:i + 2])
            i += 2
            continue
        row = cells(lines[i]) if eligible[i] else None
        data = row is not None and len(row) == 6 and re.fullmatch(r'P-[A-Za-z0-9._-]+', row[0]) and row[0] != 'P-ID'
        if data:
            if not active:
                if out and out[-1].strip():
                    out.append(newline)
                out.extend((header, separator))
                inserted.append(i + 1)
            active = True
        elif not row or len(row) != 6:
            active = False
        out.append(lines[i])
        i += 1
    return b''.join(out), inserted


def replace_bytes(path: Path, data: bytes):
    fd, temporary = tempfile.mkstemp(prefix='.' + path.name + '.', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, path.stat().st_mode & 0o777)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def apply_if_requested(argv, run_engine):
    """Return None for the exact legacy path; otherwise return the engine exit code."""
    if '-h' in argv or '--help' in argv:
        return None
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('manifest', nargs='?')
    parser.add_argument('--project-root', default='.')
    parser.add_argument('--dry-run', action='store_true')
    args, unknown = parser.parse_known_args(argv)
    if unknown or not args.manifest:
        return None
    try:
        manifest = json.loads(Path(args.manifest).read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return None  # Preserve original malformed-input diagnostics.
    registry = manifest.get('registry', {}) if isinstance(manifest, dict) else {}
    if not isinstance(registry, dict) or not registry.get('ensure_table_headers', False):
        return None
    if registry['ensure_table_headers'] is not True:
        raise ValueError('registry.ensure_table_headers must be a boolean')
    project = Path(args.project_root).resolve()
    path = project / 'spec/placeholder-registry.md'
    before = path.read_bytes()
    formatted, positions = format_registry(before)
    print('registry.ensure_table_headers: insert before original lines ' + json.dumps(positions), flush=True)
    if args.dry_run:
        # The original engine reads a private spec copy, so even dry-run observers
        # never see temporary changes in the real project.
        with tempfile.TemporaryDirectory(prefix='hmigbot-writeback-dry-') as temporary:
            overlay = Path(temporary)
            shutil.copytree(project / 'spec', overlay / 'spec', symlinks=True)
            (overlay / 'spec/placeholder-registry.md').write_bytes(formatted)
            return run_engine([str(Path(args.manifest).resolve()), '--project-root', str(overlay), '--dry-run'])
    committed = False
    try:
        if formatted != before:
            replace_bytes(path, formatted)
        code = run_engine(argv)
        committed = code == 0
        return code
    finally:
        if not committed:
            replace_bytes(path, before)
